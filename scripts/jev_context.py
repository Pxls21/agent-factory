#!/usr/bin/env python3
"""jev_context: the shared library of the Jev bug locator (scripts/jev_locate.py) and the Jev-assisted bug-echo
(scripts/jev_echo.py); tasks #227 and #229, D-072 item 4, brief tasks/briefs/jev-laya/JT2-brief.md.

Advisory only (KC-J1, KC-J1b; docs/research/findings/JEV-LEVERAGE-AUDIT-2026-09-24.md section 3): Jev FINDS and SORTS,
the model and deterministic code DECIDE. No Jev score reaches a gate. No gate file may import or run this module
(scripts/no_laya_in_gates.py). Standard library only, plus the instruments' command lines.

The pipeline (the brief's pinned decisions D-1 to D-4):
  collect()  runs the code-intel instruments in parallel threads. Each is optional and fail-open (D-1): an absent or
             failing one yields an `unmapped — <tool> unavailable` line, never a silent blank. Each instrument has ONE
             30 s budget shared by its calls. A timed-out tool is killed with its whole process group.
  merge()    makes every hit a chunk {id, instruments, path, line, text<=400}. Code hits on the same path within 5
             lines merge and keep every instrument that found them (D-2). Record rows (registry rows, CLAUDE.md quirk
             segments, commits) stay separate rows and are not files to read (the lane report, DD-8).
  jev_rank() scores at most 48 chunks through scripts/jev.py, one noul per chunk, after a lexical pre-filter (D-3).
             Only the local endpoint is asked (venue "local", or a pinned loopback url): never the bridge. The query
             is the question's last 1,000 characters, because the model's window is 1,024 tokens and the server puts
             the query BEFORE the chunk and cuts from the right: a longer query would cut every chunk off. 1,000 is
             also jev.rank's own query cut (D-076 (b)), which keeps a query's HEAD: sending more would lose the tail.
  render()   the pack, markdown or JSON, under the character budget (default 6,000, hard cap 9,000: AF-AP-183) (D-4).
             Deterministic for fixed inputs and fixed instrument outputs: every order has a total tie-break, and the
             pack holds no timing.
Displayed text passes transcript_export.scrub first; without the scrubber, snippets are withheld.
"""
import concurrent.futures
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
try:
    from transcript_export import scrub as _scrub
except Exception:          # without the scrubber, no repo text is displayed (render() withholds the snippets)
    _scrub = None

CODE_DIRS = ("proofs", "spikes", "scripts", "src", "harness-ports", "tests")
VENDORED = ("sandbox-kit/", "graft/", ".gitnexus/", ".code-review-graph/", "node_modules/", ".claude/skills/",
            ".agents/")
INSTRUMENTS = ("graft", "gitnexus", "cbm", "crg", "rg", "registry", "quirks", "git-log")
RECORDS = ("registry", "quirks", "git-log")
INSTRUMENT_TIMEOUT = 30.0
TEXT_CAP = 400
MERGE_LINES = 5
MAX_JEV_CHUNKS = 48
JEV_BATCH = 8               # chunks per call (at most 48 in all, D-3); see jev_rank
JEV_QUERY_CHARS = 1000      # = jev.RANK_QUERY_CHARS (D-076 (b)); the tail is kept here, so nothing is cut there
JEV_TIMEOUT = 240.0
TOP_DEFAULT = 12
BUDGET_DEFAULT = 6000
BUDGET_CAP = 9000
BUDGET_MIN = 1000
RECORD_TOP = 8
FILES_SHOWN = 10
SEARCH_CHARS = 300
NOTE_CHARS = 160
QUESTION_SHOWN = 300
RG_MAX_HITS = 400
RG_TOKEN_HITS = 100
RG_TOKENS = 8
MARK = "bit 2026-"
# The pack's orders. A Jev score may only reorder the base order's selection, never replace it (KC-J5).
ORDERS = ("unranked", "lexical", "jev")
# D-077 (the coordinator, 2026-09-24): the default is `lexical`; Jev is opt-in behind `--order jev`. A3's pre-registered
# rule picked jev>lexical (mean recall@5 0.300 against 0.250, docs/research/findings/jev-locate-bench/results.md), but
# that lead is ONE case of 20 crossing the rank-5 line, MRR@10 reverses it (0.122 against 0.210), and a Jev pack costs
# 36-165 s against 5-28 s. Under D-074 a model becomes the default only when it beats the plain order; this run does
# not show that. The bench reruns when a better model exists.
DEFAULT_ORDER = "lexical"
JEV_BASE = "lexical"            # the base whose selection `--order jev` reorders, and the order when Jev is down

_STOP = frozenset((
    "the and for that with this from not are was but its has have had into when then than they them their there what "
    "which while where who why how all any can could should would will one two per via out off own our you your use "
    "used using only also just more most less such each every other some same none true false self def return import "
    "class null new old get set run runs ran file files line lines code test tests does did done make made").split())
_KEYWORDS = frozenset((
    "if elif else for while in not and or is return assert try except finally with as def class lambda yield pass "
    "break continue raise import from global nonlocal del await async None True False then fi do done case esac "
    "function local export echo exit len open print str int float bool list dict set tuple isinstance range type "
    "super repr sorted min max sum any all").split())


class Context:
    """Where and how the instruments run; resolved ONCE by the caller and threaded explicitly (never re-read from the
    environment later: CLAUDE.md, "os.environ is NOT a config channel")."""

    def __init__(self, root, tools, scope=None, timeout=INSTRUMENT_TIMEOUT):
        self.root = os.path.abspath(root)
        self.tools = tools
        self.scope = scope
        self.timeout = timeout
        self.slug = self.root.strip("/").replace("/", "-")      # codebase-memory's project name (the code-intel skill)


def default_tools(home):
    """The instruments' argv prefixes. Bare names resolve through the inherited PATH when a call runs; codebase-memory
    and code-review-graph live under the caller's home (the sandbox's /root, the PC's $HOME: scripts/lane_context.sh:41
    and .claude/skills/code-intel-trio/SKILL.md name them)."""
    return {"graft": ["graft"], "node": ["node"], "rg": ["rg"], "git": ["git"],
            "cbm": [os.path.join(home, ".local", "bin", "codebase-memory-mcp")],
            "crg": [os.path.join(home, "venv-crg", "bin", "code-review-graph")]}


# ---------- text ----------

def clean(text):
    """One line: control characters and runs of whitespace become one space."""
    return " ".join("".join(c if c.isprintable() or c in "\t\n" else " " for c in str(text)).split())


def show(text, n):
    """Display text from the repo or the question: scrubbed FIRST, then cleaned and cut to n characters ("..." marks
    a cut). Without the scrubber it is withheld, never shown raw."""
    if _scrub is None:
        return "[withheld: the scrubber did not import]"
    return _cut(clean(_scrub(str(text))), n)


def show_note(text, n):
    """A line this tool wrote (a ranking line, an unmapped reason): scrubbed when the scrubber is there, else cleaned."""
    return _cut(clean(_scrub(str(text)) if _scrub is not None else text), n)


def _cut(t, n):
    return t if len(t) <= n else t[:max(0, n - 3)] + "..."


def lines_of(text):
    """A tool's output as lines, split on "\n" ONLY (AF-AP-132): str.splitlines() also breaks on a form feed, \x0b,
    \x1c-\x1e, U+0085, U+2028 and U+2029, so a matched source line holding one was cut in two (JT3's finding in
    parse_rg, 2026-09-24): its snippet lost its tail, and a tail shaped `path:NN:` became a hit of its own."""
    return text.split("\n")


def words(text):
    """The lexical words of a text: letters split on punctuation, underscores and camelCase; lower case; 3+ letters;
    no stop words."""
    out = set()
    for tok in re.findall(r"[A-Za-z][A-Za-z0-9]*", str(text)):
        for part in re.findall(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|[0-9]+", tok):
            p = part.lower()
            if len(p) >= 3 and not p.isdigit() and p not in _STOP:
                out.add(p)
    return out


_QUOTED = re.compile(r"`([^`\n]{3,160})`|\"([^\"\n]{3,160})\"|'([^'\n]{3,160})'")
_ERRCLS = re.compile(r"(?<![\w.])([A-Z][A-Za-z0-9]*(?:Error|Exception|Warning|Interrupt|Exit))(?!\w)")
_FLAG = re.compile(r"(?<![\w-])(--[a-z][a-z0-9-]{2,40})(?![\w-])")
_FILEREF = re.compile(r"(?<![\w./-])((?:/?[\w.-]+/)*[\w-][\w.-]*\.(?:py|sh|js|cjs|mjs|ts|rs|md|yaml|yml|json|toml|txt))"
                      r"(?::L?(\d+))?(?![\w/])")
_TRACE = re.compile(r'File "([^"\n]+)", line (\d+)')      # a Python traceback frame
_IDENT = re.compile(r"(?<![\w.$-])([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)(?!\w)")
_KIND_RANK = {"quoted": 0, "ident": 1, "error": 2, "flag": 3, "fileref": 4, "word": 5}


def _code_like(ident):
    body = ident.strip("_")
    return len(ident) >= 4 and ("_" in body or "." in ident or re.search(r"[a-z][A-Z]", ident) is not None)


def tokens(text):
    """The question's distinctive tokens, most distinctive first: [(kind, token, line or None)]. Kinds: quoted strings,
    code-like identifiers (snake_case, camelCase, dotted), error class names, --flags, file refs (`x.py:NN`). With no
    code-like token, the longest prose words (7+ letters) stand in (kind "word")."""
    text = str(text)
    found, refs = {}, set()
    for m in _TRACE.finditer(text):
        refs.add(m.group(1))
        found.setdefault(m.group(1), ("fileref", int(m.group(2))))
    for m in _FILEREF.finditer(text):
        refs.add(m.group(1))
        found.setdefault(m.group(1), ("fileref", int(m.group(2)) if m.group(2) else None))
    for m in _QUOTED.finditer(text):
        q = next(g for g in m.groups() if g is not None).strip()
        if (len(q) >= 6 or not q.isalpha()) and len(q) >= 3 and q not in refs:   # not a bare short word ("rank")
            found.setdefault(q, ("quoted", None))
    for m in _ERRCLS.finditer(text):
        found.setdefault(m.group(1), ("error", None))
    for m in _FLAG.finditer(text):
        found.setdefault(m.group(1), ("flag", None))
    for m in _IDENT.finditer(text):
        t = m.group(1)
        if _code_like(t) and t not in refs and not any(t in r for r in refs):
            found.setdefault(t, ("ident", None))
    out = [(k, t, ln) for t, (k, ln) in found.items()]
    if not out:
        out = [("word", w, None) for w in words(text) if len(w) >= 7]
    out.sort(key=lambda x: (_KIND_RANK[x[0]], -len(x[1]), x[1]))
    return out


def identifiers(toks, n=2):
    """At most n symbol names for the per-symbol instruments: plain names first (a project's own functions), then
    the last part of a dotted name (often a library call such as os.path.exists)."""
    out = []
    for kind, t, _ in sorted((x for x in toks if x[0] == "ident"), key=lambda x: "." in x[1]):
        name = t.rsplit(".", 1)[-1]
        if len(name) >= 3 and name not in out:
            out.append(name)
    return out[:n]


def search_text(question, toks):
    """The query the search instruments get: the question when short, else its distinctive tokens."""
    q = clean(question)
    if len(q) <= SEARCH_CHARS:
        return q
    joined = " ".join(t for _, t, _ in toks[:12])
    return joined[:SEARCH_CHARS] if joined.strip() else q[-SEARCH_CHARS:]


# ---------- running a tool ----------

def run_tool(argv, cwd, timeout, ok=(0,)):
    """(rc, stdout, reason); reason is None when the tool ran and its exit code is in `ok`. Never raises. The tool
    runs in its own process group, and a timeout kills the whole group."""
    if timeout <= 0.5:
        return None, "", "skipped: the instrument's %gs budget is spent" % INSTRUMENT_TIMEOUT
    try:
        p = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             start_new_session=True)
    except FileNotFoundError:
        return None, "", "not found: %s" % os.path.basename(argv[0])
    except OSError as e:
        return None, "", "%s: %s" % (type(e).__name__, clean(e.strerror or e))
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except OSError:
            pass
        try:
            p.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            pass
        return None, "", "timeout after %.0fs" % timeout
    out = out.decode("utf-8", "replace")
    if p.returncode not in ok:
        lines = [ln.strip() for ln in lines_of(err.decode("utf-8", "replace") + "\n" + out) if ln.strip()]
        # the line that STARTS with the error (node prints the throwing source line first, then `Error: ...`)
        why = [ln for ln in lines if re.match(r"(?:[A-Za-z]*Error\b|error\b|fatal\b)", ln, re.I)] or \
            [ln for ln in lines if re.search(r"error|unavailable|not found|no such|fatal", ln, re.I)] or lines[-1:]
        return p.returncode, out, "rc %d: %s" % (p.returncode, clean(why[0] if why else "")[:120])
    return p.returncode, out, None


def norm_path(p, root):
    """A repo-relative path, or None: outside the root, empty, or under a vendored tree."""
    if not p or not isinstance(p, str):
        return None
    p = p.strip()
    if os.path.isabs(p):
        p = os.path.relpath(os.path.normpath(p), root)
    p = p.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    if not p or p == "." or p.startswith("../") or p.startswith(VENDORED):
        return None
    return p


def hit(instrument, path, line, text):
    try:
        ln = max(0, int(line or 0))
    except (TypeError, ValueError):
        ln = 0
    return {"instrument": instrument, "path": path, "line": ln, "text": clean(text)[:TEXT_CAP]}


class _Budget:
    """One instrument's 30 s budget, shared by its calls (the brief's D-1)."""

    def __init__(self, seconds):
        self.end = time.monotonic() + seconds

    def left(self):
        return self.end - time.monotonic()


# ---------- the parsers (each reads the exact shape the lane measured live; tests pin them on captured output) ----------

_ENTRY = re.compile(r"^(?:\d+\.|-)\s+\S")


def parse_graft(out, root):
    """graft ask: an entry is a line starting `N.` (lexical) or `-` (structural) plus its indented lines; its site is
    the first token that names an existing file (`path` or `path:Lnn[-Lmm]`). A vendored site drops the entry."""
    hits, block = [], []

    def flush():
        if not block:
            return
        text = clean(" ".join(block))
        for tok in text.split():
            m = re.match(r"^\[?(.+?)\]?(?::L(\d+)(?:-L\d+)?)?[,;)]*$", tok)
            cand = m.group(1) if m else tok
            full = cand if os.path.isabs(cand) else os.path.join(root, cand)
            if ("/" in cand or "." in cand) and os.path.isfile(full):
                path = norm_path(cand, root)
                if path:
                    hits.append(hit("graft", path, m.group(2) if m else 0, text))
                return
    for ln in lines_of(out):
        if _ENTRY.match(ln):
            flush()
            block[:] = [ln]
        elif block and ln[:1].isspace() and ln.strip():
            block.append(ln)
        else:
            flush()
            block[:] = []
    flush()
    return hits


def _json(out):
    try:
        d = json.loads(out)
    except ValueError:
        start = out.find("{")
        try:
            d = json.loads(out[start:]) if start >= 0 else None
        except ValueError:
            d = None
    return d if isinstance(d, dict) else None


def parse_gitnexus_query(out, root):
    """`gitnexus query` JSON: every process symbol and definition with a filePath is a hit."""
    d = _json(out)
    if d is None:
        return None
    summaries = {p.get("id"): p.get("summary") for p in d.get("processes") or [] if isinstance(p, dict)}
    hits = []
    for key in ("process_symbols", "definitions"):
        for s in d.get(key) or []:
            if not isinstance(s, dict):
                continue
            path = norm_path(s.get("filePath"), root)
            if path:
                kind = str(s.get("id") or "").split(":", 1)[0] or "symbol"
                proc = summaries.get(s.get("process_id"))
                text = "%s %s%s" % (kind, s.get("name"), " (flow: %s)" % proc if proc else "")
                hits.append(hit("gitnexus", path, s.get("startLine"), text))
    return hits


def parse_gitnexus_context(out, root, sym):
    """`gitnexus context <sym>` JSON (local-backend.js _contextImpl): the definition and every incoming reference
    (file-level: GitNexus gives them no line), or the candidates of an ambiguous name; `{error}` = no hit."""
    d = _json(out)
    if d is None:
        return None
    hits = []
    if d.get("status") == "found" and isinstance(d.get("symbol"), dict):
        s = d["symbol"]
        path = norm_path(s.get("filePath"), root)
        if path:
            hits.append(hit("gitnexus", path, s.get("startLine"), "%s %s: the definition" % (s.get("kind"), sym)))
        for rel, entries in sorted((d.get("incoming") or {}).items()):
            for e in (entries or [])[:20]:
                if isinstance(e, dict):
                    path = norm_path(e.get("filePath"), root)
                    if path:     # a live caller entry has uid, name and filePath, no kind (measured 2026-09-24)
                        kind = e.get("kind") or str(e.get("uid") or "").split(":", 1)[0] or "symbol"
                        hits.append(hit("gitnexus", path, 0, "%s %s %s %s" % (kind, e.get("name"), rel, sym)))
    elif d.get("status") == "ambiguous":
        for c in d.get("candidates") or []:
            if isinstance(c, dict):
                path = norm_path(c.get("filePath"), root)
                if path:
                    hits.append(hit("gitnexus", path, c.get("line"), "%s %s: a candidate" % (c.get("kind"), c.get("name"))))
    return hits


_CBM_ROW = re.compile(r"^\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+)-(\d+)\s+(-?\d+(?:\.\d+)?)\s*$")


def parse_cbm(out, root, slug):
    """`codebase-memory-mcp cli search_graph` rows: `qn label file start-end rank`."""
    hits = []
    for ln in lines_of(out):
        m = _CBM_ROW.match(ln)
        if m:
            path = norm_path(m.group(3), root)
            if path:
                qn = m.group(1)
                qn = qn[len(slug) + 1:] if qn.startswith(slug + ".") else qn
                hits.append(hit("cbm", path, m.group(4), "%s %s" % (m.group(2), qn)))
    return hits


def parse_crg(out, root, sym):
    """`code-review-graph query callers_of` JSON -> (hits, qualified names to re-ask) or None when it is not JSON.
    `ok`: every caller is a hit. `ambiguous`: the candidates whose name IS the symbol are its definitions (hits), and
    their qualified names are re-asked (at most 2). `not_found`: nothing."""
    d = _json(out)
    if d is None:
        return None
    hits, again = [], []
    if d.get("status") == "ok":
        for r in d.get("results") or []:
            if isinstance(r, dict):
                path = norm_path(r.get("file_path"), root)
                if path:
                    hits.append(hit("crg", path, r.get("line_start"), "%s %s calls %s" % (r.get("kind"), r.get("name"), sym)))
    elif d.get("status") == "ambiguous":
        for c in d.get("candidates") or []:
            if isinstance(c, dict) and c.get("name") == sym:
                path = norm_path(c.get("file_path"), root)
                if path:
                    hits.append(hit("crg", path, c.get("line_start"), "%s %s: the definition" % (c.get("kind"), sym)))
                    if c.get("qualified_name") and len(again) < 2:
                        again.append(c["qualified_name"])
    return hits, again


def parse_rg(out, root, instrument="rg"):
    """`rg -n --no-heading --with-filename` lines: path:line:text."""
    hits = []
    for ln in lines_of(out):
        parts = ln.split(":", 2)
        if len(parts) == 3 and parts[1].isdigit():
            path = norm_path(parts[0], root)
            if path:
                hits.append(hit(instrument, path, parts[1], parts[2]))
        if len(hits) >= RG_MAX_HITS:
            break
    return hits


# ---------- the instruments ----------

def _unmapped(name, reason):
    return "unmapped — %s unavailable (%s)" % (name, clean(reason)[:NOTE_CHARS])


def inst_graft(question, toks, ctx):
    if not os.path.isfile(os.path.join(ctx.root, "graft", "INDEX.md")):
        return [], [_unmapped("graft", "graft/INDEX.md absent")], False
    argv = ctx.tools["graft"] + ["ask", search_text(question, toks)]
    if ctx.scope:
        argv += ["--in", ctx.scope]
    rc, out, reason = run_tool(argv, ctx.root, ctx.timeout)
    if reason:
        return [], [_unmapped("graft", reason)], False
    return parse_graft(out, ctx.root), [], True


def inst_gitnexus(question, toks, ctx):
    if not os.path.isfile(os.path.join(ctx.root, ".gitnexus", "run.cjs")):
        return [], [_unmapped("gitnexus", ".gitnexus/run.cjs absent")], False
    budget, hits, notes, answered = _Budget(ctx.timeout), [], [], False
    rc, out, reason = run_tool(ctx.tools["node"] + [".gitnexus/run.cjs", "query", search_text(question, toks),
                                                    "--repo", "."], ctx.root, budget.left())
    got = None if reason else parse_gitnexus_query(out, ctx.root)
    if got is None:
        notes.append(_unmapped("gitnexus query", reason or "non-JSON output"))
    else:
        hits += got
        answered = True
    for sym in identifiers(toks):
        rc, out, reason = run_tool(ctx.tools["node"] + [".gitnexus/run.cjs", "context", sym, "--repo", "."],
                                   ctx.root, budget.left())
        d = _json(out) if rc == 1 else None
        if d is not None and "error" in d and "status" not in d:
            answered = True      # rc 1 with `{"error": "Symbol ... not found"}`: an answer (no such symbol), not an outage
            continue
        got = None if reason else parse_gitnexus_context(out, ctx.root, sym)
        if got is None:
            notes.append(_unmapped("gitnexus context %s" % sym, reason or "non-JSON output"))
        else:
            hits += got
            answered = True
    return hits, notes, answered


def inst_cbm(question, toks, ctx):
    argv = ctx.tools["cbm"] + ["cli", "search_graph", "--project", ctx.slug, "--query", search_text(question, toks)]
    rc, out, reason = run_tool(argv, ctx.root, ctx.timeout)
    if reason:
        return [], [_unmapped("codebase-memory", reason)], False
    if not re.search(r"^results:", out, re.M):
        return [], [_unmapped("codebase-memory", "no result table: " + clean(out)[:80])], False
    return parse_cbm(out, ctx.root, ctx.slug), [], True


def inst_crg(question, toks, ctx):
    if not os.path.isfile(os.path.join(ctx.root, ".code-review-graph", "graph.db")):
        return [], [_unmapped("code-review-graph", ".code-review-graph/graph.db absent")], False
    syms = identifiers(toks)
    if not syms:
        return [], ["not run — code-review-graph: no identifier in the question"], False
    budget, hits, notes, answered = _Budget(ctx.timeout), [], [], False
    for sym in syms:
        queue = [sym]
        while queue:
            name = queue.pop(0)
            rc, out, reason = run_tool(ctx.tools["crg"] + ["query", "callers_of", name], ctx.root, budget.left())
            got = None if reason else parse_crg(out, ctx.root, sym)
            if got is None:
                notes.append(_unmapped("code-review-graph callers_of %s" % sym, reason or "non-JSON output"))
                continue
            answered = True
            hits += got[0]
            if name == sym:
                queue += got[1]
    return hits, notes, answered


def _dirs(ctx):
    if ctx.scope:
        return [ctx.scope] if os.path.exists(os.path.join(ctx.root, ctx.scope)) else []
    return [d for d in CODE_DIRS if os.path.isdir(os.path.join(ctx.root, d))]


def rg_search(ctx, pattern, dirs, timeout, flags=(), instrument="rg", cap=RG_TOKEN_HITS):
    """One rg call for one pattern -> (hits, reason). At most 3 lines per file, `cap` hits, sorted by path."""
    argv = ctx.tools["rg"] + ["-n", "--no-heading", "--with-filename", "--sort", "path", "-m", "3",
                              "--max-columns", "400", "--max-columns-preview"] + list(flags) + ["-e", pattern, "--"]
    rc, out, reason = run_tool(argv + list(dirs), ctx.root, timeout, ok=(0, 1))
    if reason:
        return [], reason
    return parse_rg(out, ctx.root, instrument)[:cap], None


def rg_fixed(ctx, token, dirs, timeout, flags=(), instrument="rg"):
    return rg_search(ctx, token, dirs, timeout, ["-F"] + list(flags), instrument)


def inst_rg(question, toks, ctx):
    dirs = _dirs(ctx)
    if not dirs:
        return [], [_unmapped("rg", "no code directory under the root")], False
    budget, hits, notes, answered = _Budget(ctx.timeout), [], [], False
    pats = [t for k, t, _ in toks if k in ("quoted", "ident", "error", "flag", "word")][:RG_TOKENS]
    refs = [(t, ln) for k, t, ln in toks if k == "fileref"]
    fold = ["-i"] if all(k == "word" for k, _, _ in toks) else []
    for p in pats:          # one call per token, each capped: a common token cannot crowd a rare one out
        h, reason = rg_fixed(ctx, p, dirs, budget.left(), fold)
        if reason:
            notes.append(_unmapped("rg -F %s" % p[:40], reason))
        else:
            hits += h
            answered = True
    if refs:
        rc, out, reason = run_tool(ctx.tools["rg"] + ["--files", "--sort", "path", "--"] + dirs, ctx.root,
                                   budget.left(), ok=(0, 1))
        if reason:
            notes.append(_unmapped("rg --files", reason))
        else:
            answered = True
            files = [f for f in lines_of(out) if f]
            for ref, ln in refs:
                if os.path.isabs(ref):   # a traceback's absolute path: inside the root, else its last two parts
                    ref = norm_path(ref, ctx.root) or "/".join(ref.split("/")[-2:])
                match = [f for f in files if f == ref or f.endswith("/" + ref)][:5]
                hits += [hit("rg", f, ln or 0, "named in the question: %s%s" % (ref, ":%d" % ln if ln else ""))
                         for f in match if norm_path(f, ctx.root)]
    if not pats and not refs:
        notes.append("not run — rg: no distinctive token in the question")
    return hits, notes, answered


def _read_lines(root, rel):
    try:
        with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as fh:
            return fh.read().split("\n")
    except OSError:
        return None


def _top_records(question, rows, instrument, path):
    """rows = [(line, text, bonus)]: the RECORD_TOP best by lexical overlap (+ bonus), ties by line."""
    qw = words(question)
    scored = [(len(qw & words(t)) + bonus, ln, t) for ln, t, bonus in rows]
    scored = [s for s in scored if s[0] > 0]
    scored.sort(key=lambda s: (-s[0], s[1]))
    return [hit(instrument, path, ln, t) for _, ln, t in scored[:RECORD_TOP]]


def inst_registry(question, toks, ctx):
    lines = _read_lines(ctx.root, "docs/INCIDENT-LOG.md")
    if lines is None:
        return [], [_unmapped("registry", "docs/INCIDENT-LOG.md absent")], False
    ids = set(re.findall(r"AF-AP-\d+", question))
    rows = []
    for i, ln in enumerate(lines, 1):
        m = re.match(r"^\| (AF-AP-\d+) \|", ln)
        if m:
            rows.append((i, ln, 100 if m.group(1) in ids else 0))
    return _top_records(question, rows, "registry", "docs/INCIDENT-LOG.md"), [], True


def quirk_segments(lines):
    """[(line, segment)]: one window per `bit 2026-` marker in CLAUDE.md, starting at the clause that holds it."""
    out = []
    for i, ln in enumerate(lines, 1):
        for m in re.finditer(re.escape(MARK), ln):
            lo = max(0, m.start() - 280)
            cut = max(ln.rfind("**", lo, m.start() - 40), ln.rfind(". ", lo, m.start() - 40))
            if cut >= lo:
                lo = cut + 2
            out.append((i, ln[lo:lo + TEXT_CAP]))
    return out


def inst_quirks(question, toks, ctx):
    lines = _read_lines(ctx.root, "CLAUDE.md")
    if lines is None:
        return [], [_unmapped("quirks", "CLAUDE.md absent")], False
    rows = [(ln, seg, 0) for ln, seg in quirk_segments(lines)]
    return _top_records(question, rows, "quirks", "CLAUDE.md"), [], True


def inst_gitlog(question, toks, ctx):
    picks = [t for _, t, _ in toks][:2]
    if not picks:
        return [], ["not run — git-log: no distinctive token in the question"], False
    budget, hits, notes, answered = _Budget(ctx.timeout), [], [], False
    for tok in picks:
        rc, out, reason = run_tool(ctx.tools["git"] + ["log", "-S" + tok, "--oneline", "-5"], ctx.root, budget.left())
        if reason:
            notes.append(_unmapped("git-log -S%s" % tok[:40], reason))
            continue
        answered = True
        for ln in lines_of(out):
            if ln.strip():
                sha = ln.split()[0]
                hits.append(hit("git-log", "git:" + sha, 0, "%s  (git log -S%s)" % (ln, tok[:60])))
    return hits, notes, answered


INSTRUMENT_FNS = {"graft": inst_graft, "gitnexus": inst_gitnexus, "cbm": inst_cbm, "crg": inst_crg, "rg": inst_rg,
                  "registry": inst_registry, "quirks": inst_quirks, "git-log": inst_gitlog}


def _safe(fn, name, question, toks, ctx):
    try:
        return fn(question, toks, ctx)
    except Exception as e:           # fail open: one line naming the instrument, never a traceback
        return [], [_unmapped(name, "internal error: %s" % type(e).__name__)], False


def collect(question, ctx, instruments=INSTRUMENTS, fns=None):
    """Run the selected instruments in parallel -> (hits, notes, answered). `fns` overrides the instrument functions
    (tests). Every instrument NOT selected gets a `not run` note: nothing is silently absent."""
    fns = fns or INSTRUMENT_FNS
    toks = tokens(question)
    chosen = [n for n in INSTRUMENTS if n in instruments]
    hits, notes, answered = [], [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, len(chosen))) as ex:
        futs = {n: ex.submit(_safe, fns[n], n, question, toks, ctx) for n in chosen}
    for n in chosen:
        h, nt, ok = futs[n].result()
        hits += h
        notes += nt
        if ok:
            answered.append(n)
    notes += ["not run — %s: not selected (--instruments)" % n for n in INSTRUMENTS if n not in chosen]
    return hits, notes, answered


# ---------- chunks, order, Jev ----------

def merge(hits, query_words):
    """D-2: code hits on the same path within MERGE_LINES of the cluster's first line merge into one chunk that keeps
    every instrument that found it; record rows stay one chunk each (DD-8). Ids follow a canonical order."""
    code = sorted((h for h in hits if h["instrument"] not in RECORDS),
                  key=lambda h: (h["path"], h["line"], h["instrument"], h["text"]))
    groups, cur = [], None
    for h in code:
        if cur is not None and h["path"] == cur["path"] and h["line"] - cur["line"] <= MERGE_LINES:
            cur["instruments"].add(h["instrument"])
            if h["text"] not in cur["texts"]:
                cur["texts"].append(h["text"])
        else:
            cur = {"path": h["path"], "line": h["line"], "instruments": {h["instrument"]}, "texts": [h["text"]]}
            groups.append(cur)
    seen = set()
    for h in sorted((h for h in hits if h["instrument"] in RECORDS),
                    key=lambda h: (h["instrument"], h["path"], h["line"], h["text"])):
        key = (h["instrument"], h["path"], h["line"], h["text"])
        if key not in seen:
            seen.add(key)
            groups.append({"path": h["path"], "line": h["line"], "instruments": {h["instrument"]}, "texts": [h["text"]]})
    chunks = []
    for g in sorted(groups, key=lambda g: (g["path"], g["line"], sorted(g["instruments"]), g["texts"])):
        text = " | ".join(g["texts"])[:TEXT_CAP]
        insts = sorted(g["instruments"])
        chunks.append({"id": "k%d" % len(chunks), "path": g["path"], "line": g["line"], "instruments": insts,
                       "agreement": len(insts), "record": insts[0] in RECORDS, "text": text,
                       "lexical": len(query_words & words(text + " " + g["path"]))})
    return chunks


def unranked_key(c):
    return (-c["agreement"], -c["lexical"], c["path"], c["line"], c["id"])


def lexical_key(c):
    return (-c["lexical"], c["path"], c["line"], c["id"])


def order_base(chunks, mode):
    """A base (non-Jev) order. `unranked` = D-3's fallback: instrument agreement, then lexical score. `lexical` =
    lexical score alone (the coordinator's third A3 column). Ties by path, line and id."""
    return sorted(chunks, key=lexical_key if mode == "lexical" else unranked_key)


def order_unranked(chunks):
    return order_base(chunks, "unranked")


def prefilter(chunks, n=MAX_JEV_CHUNKS, protect=()):
    """D-3: at most n chunks go to Jev. The `protect` chunks first (the base order's top K, so every item the pack
    can show is scored), then the best by token overlap with the question."""
    first = list(protect)[:n]
    ids = {c["id"] for c in first}
    rest = sorted((c for c in chunks if c["id"] not in ids),
                  key=lambda c: (-c["lexical"], -c["agreement"], c["path"], c["line"], c["id"]))
    return first + rest[:max(0, n - len(first))]


def order_ranked(chunks, scores):
    """The PURE Jev order (D-3 as pinned, measured in A3's `jev` column; never a pack order, KC-J5): scored chunks by
    score, then the unscored ones; ties by the unranked order."""
    return sorted(chunks, key=lambda c: (0 if c["id"] in scores else 1, -scores.get(c["id"], 0.0)) + unranked_key(c))


def reorder(items, score_of):
    """KC-J5 (the coordinator's rule 3): Jev may REORDER the items the base order keeps, never replace them. The set
    is the input's; the order is by score (an unscored item after the scored ones), ties by base position."""
    pos = {id(x): i for i, x in enumerate(items)}
    return sorted(items, key=lambda x: (score_of(x) is None, -(score_of(x) or 0.0), pos[id(x)]))


def jev_text(c):
    where = ("commit %s" % c["path"][4:]) if c["path"].startswith("git:") else (
        "%s:%d" % (c["path"], c["line"]) if c["line"] else c["path"])
    return "%s (%s)\n%s" % (where, "+".join(c["instruments"]), c["text"])


def jev_query(text):
    """The question's last JEV_QUERY_CHARS characters (the model's window; see the module docstring)."""
    t = str(text).strip()
    return t[-JEV_QUERY_CHARS:]


_JEV_LOCK = threading.Lock()


def jev_rank(query, chunks, instructions=None, url=None, timeout=JEV_TIMEOUT, log=True, protect=()):
    """-> (scores {chunk id: noul} or None, reason or None, the chunks sent). Local endpoint only (DD-1)."""
    sent = prefilter(chunks, protect=protect)
    if not sent:
        return None, "no chunk to rank", []
    try:
        import jev
    except Exception as e:
        return None, "scripts/jev.py did not import (%s)" % type(e).__name__, []
    opts = {"timeout": timeout, "log": log}
    if url:
        opts["url"] = url
    else:
        opts["venue"] = "local"
    items = [{"id": c["id"], "text": jev_text(c)} for c in sent]
    scores, n = {}, (len(items) + JEV_BATCH - 1) // JEV_BATCH
    for b in range(n):
        # small calls: the server answers under ONE lock (laya_systemone_server.py do_POST), and the endpoint is shared
        # with other lanes; each chunk is its own model call either way, so a batch changes no score
        with _JEV_LOCK:
            res = jev.rank(jev_query(query), items[b * JEV_BATCH:(b + 1) * JEV_BATCH],
                           instructions or jev.RANK_INSTRUCTIONS, **opts)
            reason = jev.last_reason
        if res is None:      # all or nothing: a partial ranking is not offered as a ranking
            return None, clean("call %d of %d: %s" % (b + 1, n, reason or "no answer"))[:NOTE_CHARS], sent
        scores.update((cid, float(s)) for cid, s in res["ranking"])
    if len(scores) >= 2 and len(set(scores.values())) == 1:
        # VERIFY-JT1 F-24: a query that fills the model's window cuts every chunk off, and each chunk then gets the
        # same score with fan_out intact. The query bound (JEV_QUERY_CHARS) prevents it for the text measured; this
        # catches the rest (the lane report, DD-15). A ranking with no spread carries no information either way.
        return None, "all %d scores are equal (%.4f): no signal (a query over the window cuts every chunk)" % (
            len(scores), next(iter(scores.values()))), sent
    return scores, None, sent


def files_to_read(ordered, mode, scores=None):
    """D-4's "files to read": code chunks aggregated by file (records excluded, DD-8), summed per file. Order by mode:
    `unranked` summed agreement then summed lexical; `lexical` summed lexical; `jev` summed Jev score (the pure
    order, A3's `jev` column). `score` is the summed Jev score whenever scores are given. The best line is the file's
    first chunk in `ordered`."""
    agg = {}
    for c in ordered:
        if c["record"]:
            continue
        f = agg.setdefault(c["path"], {"path": c["path"], "score": 0.0, "scored": False, "agreement": 0, "lexical": 0,
                                       "n": 0, "line": c["line"], "instruments": set()})
        if scores is not None and c["id"] in scores:
            f["score"] += scores[c["id"]]
            f["scored"] = True
        f["agreement"] += c["agreement"]
        f["lexical"] += c["lexical"]
        f["n"] += 1
        f["instruments"].update(c["instruments"])
    if mode == "jev":
        key = lambda f: (-round(f["score"], 9), -f["agreement"], -f["lexical"], f["path"])
    elif mode == "lexical":
        key = lambda f: (-f["lexical"], f["path"])
    else:
        key = lambda f: (-f["agreement"], -f["lexical"], f["path"])
    out = sorted(agg.values(), key=key)
    for f in out:
        f["score"] = round(f["score"], 4)
        f["instruments"] = sorted(f["instruments"])
    return out


def select(pack, k, nfiles):
    """What one fit level shows: the base order's top k items and top nfiles files; with Jev scores, the SAME sets
    reordered (KC-J5: a Jev score never drops an item or a file the base order keeps within the budget)."""
    items, files = pack["base"][:k], (pack["files"] or [])[:nfiles]
    scores = pack["scores"]
    if scores is not None:
        items = reorder(items, lambda c: scores.get(c["id"]))
        files = reorder(files, lambda f: f["score"] if f["scored"] else None)
    return items, files


# ---------- the pack (D-4) ----------

def clamp_budget(budget):
    """-> (budget, note or None); a budget over the hard cap is clamped (AF-AP-183: a hook swaps text over 10,000
    characters for a preview of its head)."""
    if budget > BUDGET_CAP:
        return BUDGET_CAP, "budget clamped to the %d-character hard cap" % BUDGET_CAP
    return budget, None


def _where(c):
    if c["path"].startswith("git:"):
        return "commit " + c["path"][4:]
    return "%s:%d" % (c["path"], c["line"]) if c["line"] else c["path"]


def _score(c, scores):
    if scores is not None:
        return "%.3f" % scores[c["id"]] if c["id"] in scores else "-"
    return "a%d l%d" % (c["agreement"], c["lexical"])


def _fscore(f, scores):
    return ("sum %.3f" % f["score"]) if scores is not None else ("a%d l%d" % (f["agreement"], f["lexical"]))


def _md(pack, snip, k, nfiles):
    scores = pack["scores"]
    items, files = select(pack, k, nfiles)
    out = ["# %s" % pack["title"]]
    out += ["%s: %s" % (label, show(text, QUESTION_SHOWN)) for label, text in pack["head"]]
    out.append(show_note(pack["ranking"], 400))
    out.append("answered: %s" % (", ".join(pack["answered"]) or "none"))
    out += [show_note(x, 400) for x in pack.get("extra", [])]
    out.append("## top %d of %d (score, instruments, where, snippet)" % (len(items), len(pack["base"])))
    for i, c in enumerate(items, 1):
        line = "%d. %s %s %s" % (i, _score(c, scores), "+".join(c["instruments"]), _where(c))
        out.append(line + (" — " + show(c["text"], snip) if snip else ""))
    if pack["files"] is not None:
        out.append("## files to read (%d of %d)" % (len(files), len(pack["files"])))
        for i, f in enumerate(files, 1):
            out.append("%d. %s:%d — %s (%d chunk%s: %s)" % (i, f["path"], f["line"], _fscore(f, scores), f["n"],
                                                        "" if f["n"] == 1 else "s", ", ".join(f["instruments"])))
    out += [show_note(x, 400) for x in pack.get("tail", [])]
    out.append("## unmapped and not run")
    out += ["- " + show_note(n, NOTE_CHARS) for n in pack["notes"]] or ["- (none)"]
    return "\n".join(out) + "\n"


def _json_pack(pack, snip, k, nfiles):
    scores = pack["scores"]
    items, files = select(pack, k, nfiles)
    d = {"tool": pack["title"], "head": {label: show(text, QUESTION_SHOWN) for label, text in pack["head"]},
         "ranking": show_note(pack["ranking"], 400), "answered": pack["answered"],
         "extra": [show_note(x, 400) for x in pack.get("extra", [])], "chunks": len(pack["base"]),
         "top": [{"rank": i, "score": scores.get(c["id"]) if scores is not None else None,
                  "agreement": c["agreement"], "lexical": c["lexical"], "instruments": c["instruments"],
                  "path": c["path"], "line": c["line"], "snippet": show(c["text"], snip) if snip else ""}
                 for i, c in enumerate(items, 1)],
         "notes": [show_note(n, NOTE_CHARS) for n in pack["notes"]],
         "tail": [show_note(x, 400) for x in pack.get("tail", [])]}
    if pack["files"] is not None:
        d["files"] = [{key: f[key] for key in ("path", "line", "score", "agreement", "lexical", "n", "instruments")}
                      for f in files]
    return json.dumps(d, ensure_ascii=False, sort_keys=True) + "\n"


def render(pack, top, budget, as_json=False):
    """The pack within `budget` characters: shorter snippets first, then fewer items and files; a markdown pack that
    still does not fit is cut with a marker line, a JSON pack falls back to its skeleton. Never over the budget."""
    fn = _json_pack if as_json else _md
    tries = [(s, top, FILES_SHOWN) for s in (240, 160, 100, 60)]
    tries += [(60, k, 5) for k in sorted({max(1, top * 3 // 4), max(1, top // 2), max(1, top // 4), 1}, reverse=True)]
    tries += [(0, 1, 3), (0, 0, 0)]
    for snip, k, nf in tries:
        text = fn(pack, snip, k, nf)
        if len(text) <= budget:
            return text
    if as_json:
        skel = json.dumps({"tool": pack["title"], "truncated": True, "ranking": clean(pack["ranking"])[:200],
                           "notes": [clean(n)[:40] for n in pack["notes"]][:12]}, ensure_ascii=False) + "\n"
        if len(skel) <= budget:
            return skel
        return json.dumps({"tool": pack["title"], "truncated": True}) + "\n"
    marker = "\n[cut to the %d-character budget]\n" % budget
    return fn(pack, 0, 0, 0)[:max(0, budget - len(marker))] + marker


def build_pack(title, head, chunks, mode, scores, rank_line, answered, notes, extra=(), tail=(), with_files=True):
    """The pack dict render() takes. `mode` is the base order (unranked or lexical); `scores` (or None) reorders
    within it."""
    base = order_base(chunks, mode)
    return {"title": title, "head": list(head), "ranking": rank_line, "answered": list(answered), "base": base,
            "scores": scores, "files": files_to_read(base, mode, scores) if with_files else None,
            "notes": list(notes), "extra": list(extra), "tail": list(tail)}
