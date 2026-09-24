#!/usr/bin/env python3
"""jev_echo: Jev-assisted bug-echo (task #229; D-072 item 4; the brief tasks/briefs/jev-laya/JT2-brief.md, D-6).

  jev_echo.py --diff <commit | patch file> [--top K] [--budget N] [--json]
              [--root DIR] [--instruments LIST] [--order lexical|unranked|jev] [--jev-url URL] [--jev-timeout S]
              [--no-jev-log]

The removed lines of the diff's code hunks are the anti-pattern, the added lines of THOSE hunks the fix, and their
file and hunk the fixed site (a hunk that only adds, such as a new test, is not the fix). Candidates, the fixed site
excluded: rg for the removed lines' distinctive tokens (rg-token) and for their shape (rg-shape: the line with its
local names, strings and numbers generalized) across the code dirs, plus `graft ask "code like: <removed snippet>"`.
Each candidate carries 3 lines of context on each side. Output: the top K sites (default 10), in the lexical order by
default (D-077). With `--order jev` (opt-in), Jev scores each against "the defect: <removed>; fixed as: <added>" with
the question "Does this code show the same defect as the one fixed?" and reorders the lexical selection (KC-J5).
Advisory only (KC-J1b): an order or a score is a lead; the BUG/WATCH/OK call stays with the model.

Exit 0 with a pack (also when nothing is found, every instrument is unmapped or Jev is down); 64 on a usage error,
including a --diff that is neither a readable patch file nor a commit the root's git can show.
"""
import argparse
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import jev_context as jc  # noqa: E402
from jev_locate import Usage, check_budget, parse_instruments, rank_chunks  # noqa: E402

ECHO_INSTRUMENTS = ("rg-token", "rg-shape", "graft")
ECHO_TOP = 10
ECHO_TOKENS = 6
ECHO_SHAPES = 2
CONTEXT = 3
SIDE_CHARS = 560
INSTRUCTIONS = "Does this code show the same defect as the one fixed?"
NOTE = ("note: a score is a lead, not a verdict: the BUG/WATCH/OK call on each site stays with the model "
        "(KC-J1b; a Jev score is never the only evidence).")
NONCODE = (".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".sha256", ".lock", ".csv", ".tsv", ".log",
           ".html", ".css", ".svg", ".png", ".ini", ".cfg", ".xml")


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Usage(message)


# ---------- the diff ----------

def _side_path(s):
    s = s.split("\t", 1)[0].strip()
    if s == "/dev/null":
        return None
    return s[2:] if s[:2] in ("a/", "b/") else s


def parse_patch(text):
    """A unified diff -> [{path, hunks: [{new_start, new_len, removed, added}]}]. Hunk bodies are read by their
    header's line counts, so a removed line that starts with `--` is never taken for a file header."""
    files, cur, hunk, old_left, new_left = [], None, None, 0, 0
    for ln in text.split("\n"):
        if hunk is not None and (old_left > 0 or new_left > 0):
            if ln.startswith("\\"):
                continue
            tag, body = ln[:1], ln[1:]
            if tag == "-":
                hunk["removed"].append(body)
                old_left -= 1
            elif tag == "+":
                hunk["added"].append(body)
                new_left -= 1
            else:
                old_left -= 1
                new_left -= 1
            continue
        hunk = None
        if ln.startswith("diff --git "):
            cur = {"path": None, "hunks": []}
            files.append(cur)
        elif ln.startswith("--- "):
            if cur is None or cur["hunks"]:
                cur = {"path": None, "hunks": []}
                files.append(cur)
            cur["path"] = cur["path"] or _side_path(ln[4:])
        elif ln.startswith("+++ ") and cur is not None:
            cur["path"] = _side_path(ln[4:]) or cur["path"]
        elif ln.startswith("@@") and cur is not None:
            m = re.match(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", ln)
            if m:
                old_left = int(m.group(2)) if m.group(2) is not None else 1
                new_left = int(m.group(4)) if m.group(4) is not None else 1
                hunk = {"new_start": int(m.group(3)), "new_len": new_left, "removed": [], "added": []}
                cur["hunks"].append(hunk)
    return [f for f in files if f["path"]]


def is_code(path):
    return bool(path) and not path.lower().endswith(NONCODE) and jc.norm_path(path, jc.ROOT) is not None


def defect(files):
    """-> (removed lines, added lines, fixed sites, touched sites); a site is (path, first, last) on the new side.
    The defect and its fix come from the hunks that remove code; EVERY code hunk of the diff is touched (a hunk that
    only adds, such as the fix's new helper, is the fix too) and is excluded from the candidates."""
    removed, added, sites, touched = [], [], [], []
    for f in files:
        if not is_code(f["path"]):
            continue
        for h in f["hunks"]:
            site = (f["path"], h["new_start"], h["new_start"] + max(h["new_len"], 1) - 1)
            touched.append(site)
            rem = [x.strip() for x in h["removed"] if x.strip()]
            if rem:
                removed += rem
                added += [x.strip() for x in h["added"] if x.strip()]
                sites.append(site)
    return removed, added, sites, touched


# ---------- tokens and shapes of the removed lines ----------

_LIT = re.compile(r'"[^"\n]{2,80}"|\'[^\'\n]{2,80}\'')
_DOTTED = re.compile(r"(?<![\w.])[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+(?!\w)")
_WORD = re.compile(r"(?<![\w.])[A-Za-z_]\w*(?!\w)")
_TOK = re.compile(r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\'|\d+(?:\.\d+)?|[A-Za-z_]\w*|\S')
_META = set("\\.^$|?*+()[]{}")


def echo_tokens(removed, added):
    """The removed lines' distinctive tokens, the ones the fix REMOVED first: string literals (with their quotes),
    dotted names, error class names, snake_case or camelCase names of 6+ characters."""
    text, found = "\n".join(removed), {}
    for m in _LIT.finditer(text):
        found.setdefault(m.group(0), 0)
    for m in _DOTTED.finditer(text):
        found.setdefault(m.group(0), 1)
    for m in _WORD.finditer(text):
        w = m.group(0)
        if re.fullmatch(r"[A-Z]\w*(?:Error|Exception|Warning)", w):
            found.setdefault(w, 2)
        elif len(w) >= 6 and ("_" in w.strip("_") or re.search(r"[a-z][A-Z]", w)) and w not in jc._KEYWORDS:
            found.setdefault(w, 3)
    fix = "\n".join(added)
    ranked = sorted(found.items(), key=lambda kv: (kv[0] in fix, kv[1], -len(kv[0]), kv[0]))
    return [t for t, _ in ranked][:ECHO_TOKENS]


def shape(line):
    """(regex, kept): the line as a pattern with its local names, strings and numbers generalized; `kept` counts
    the API names it keeps (attribute and call names, capitalized names), the measure of how specific it is."""
    toks = _TOK.findall(line.strip())
    out, kept, prev_word = [], 0, False
    for i, t in enumerate(toks):
        prv, nxt = (toks[i - 1] if i else ""), (toks[i + 1] if i + 1 < len(toks) else "")
        word = False
        if t[0] in "\"'":
            piece = '"[^"]*"' if t[0] == '"' else "'[^']*'"
        elif t[0].isdigit():
            piece, word = r"\d+", True
        elif re.match(r"[A-Za-z_]", t):
            word = True
            local = (t[0].islower() or t[0] == "_") and t not in jc._KEYWORDS and prv != "." and nxt not in ("(", ".")
            if local:
                piece = r"\w+"
            else:
                piece = t
                kept += 0 if t in jc._KEYWORDS else 1
        else:
            piece = "\\" + t if t in _META else t
        out.append(("" if not out else (r"\s+" if word and prev_word else r"\s*")) + piece)
        prev_word = word
    return "".join(out), kept


def shapes(removed):
    """The ECHO_SHAPES most specific removed lines' shapes (at least 2 kept API names each), distinct."""
    cands = sorted({(shape(r), r) for r in removed}, key=lambda x: (-x[0][1], -len(x[1]), x[1]))
    out = []
    for (rx, kept), line in cands:
        if kept >= 2 and rx not in [s for s, _ in out]:
            out.append((rx, line))
    return out[:ECHO_SHAPES]


# ---------- candidates ----------

def _context(root, path, line, cache):
    if path not in cache:
        cache[path] = jc._read_lines(root, path) or []
    lines = cache[path]
    lo, hi = max(1, line - CONTEXT), min(len(lines), line + CONTEXT)
    return "\n".join(lines[lo - 1:hi])


def candidates(ctx, removed, added, touched, instruments):
    """-> (hits with their context, notes, answered). Every touched hunk (+-MERGE_LINES) and every line that equals a
    line of the fix are excluded: the fixed site is not an echo."""
    dirs = [d for d in jc.CODE_DIRS if os.path.isdir(os.path.join(ctx.root, d))]
    budget, raw, notes, answered = jc._Budget(ctx.timeout), [], [], []
    if not dirs and ("rg-token" in instruments or "rg-shape" in instruments):
        notes.append(jc._unmapped("rg", "no code directory under the root"))
    elif dirs:
        if "rg-token" in instruments:
            toks = echo_tokens(removed, added)
            for t in toks:
                h, reason = jc.rg_fixed(ctx, t, dirs, budget.left(), instrument="rg-token")
                if reason:
                    notes.append(jc._unmapped("rg-token -F %s" % t[:40], reason))
                else:
                    raw += h
                    answered.append("rg-token")
            if not toks:
                notes.append("not run — rg-token: no distinctive token in the removed lines")
        if "rg-shape" in instruments:
            shp = shapes(removed)
            for rx, _line in shp:
                h, reason = jc.rg_search(ctx, rx, dirs, budget.left(), instrument="rg-shape")
                if reason:
                    notes.append(jc._unmapped("rg-shape", reason))
                else:
                    raw += h
                    answered.append("rg-shape")
            if not shp:
                notes.append("not run — rg-shape: no removed line keeps 2 or more API names")
    if "graft" in instruments:
        if not os.path.isfile(os.path.join(ctx.root, "graft", "INDEX.md")):
            notes.append(jc._unmapped("graft", "graft/INDEX.md absent"))
        else:
            best = shapes(removed)
            snippet = (best[0][1] if best else max(removed, key=len))[:200]
            rc, out, reason = jc.run_tool(ctx.tools["graft"] + ["ask", "code like: " + snippet], ctx.root,
                                          ctx.timeout)
            if reason:
                notes.append(jc._unmapped("graft", reason))
            else:
                raw += jc.parse_graft(out, ctx.root)
                answered.append("graft")
    notes += ["not run — %s: not selected (--instruments)" % n for n in ECHO_INSTRUMENTS if n not in instruments]
    fix = set(added)
    cache, hits = {}, []
    for h in raw:
        if any(h["path"] == p and a - jc.MERGE_LINES <= h["line"] <= b + jc.MERGE_LINES for p, a, b in touched):
            continue
        if not os.path.isfile(os.path.join(ctx.root, h["path"])):
            continue
        text = h["text"]
        if h["line"]:
            text = _context(ctx.root, h["path"], h["line"], cache) or text
            lines = cache.get(h["path"]) or []
            if 0 < h["line"] <= len(lines) and lines[h["line"] - 1].strip() in fix:
                continue
        hits.append(jc.hit(h["instrument"], h["path"], h["line"], text))
    return hits, notes, sorted(set(answered), key=ECHO_INSTRUMENTS.index)


def get_patch(arg, root, tools):
    if os.path.isfile(arg):
        try:
            with open(arg, encoding="utf-8", errors="replace") as fh:
                return fh.read()
        except OSError as e:
            raise Usage("cannot read the patch file %s: %s" % (arg, e.strerror))
    if not arg or arg.startswith("-"):
        raise Usage("--diff takes a commit or a patch file")
    rc, out, reason = jc.run_tool(tools["git"] + ["show", "--format=", "--no-color", "--no-ext-diff", "-U3", arg,
                                                  "--"], root, jc.INSTRUMENT_TIMEOUT)
    if reason:
        raise Usage("--diff %s is neither a patch file nor a commit git can show (%s)" % (arg, reason))
    return out


def main(argv=None):
    ap = _Parser(prog="jev_echo.py", description=__doc__.splitlines()[0])
    ap.add_argument("--diff", required=True)
    ap.add_argument("--top", type=int, default=ECHO_TOP)
    ap.add_argument("--budget", type=int, default=jc.BUDGET_DEFAULT)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--root", default=jc.ROOT)
    ap.add_argument("--instruments", default=",".join(ECHO_INSTRUMENTS))
    ap.add_argument("--order", choices=jc.ORDERS, default=jc.DEFAULT_ORDER,
                    help="the sites' order (default %s, D-077); jev asks the local endpoint and only reorders the "
                         "%s selection" % (jc.DEFAULT_ORDER, jc.JEV_BASE))
    ap.add_argument("--jev-url")
    ap.add_argument("--jev-timeout", type=float, default=jc.JEV_TIMEOUT)
    ap.add_argument("--no-jev-log", action="store_true")
    t0 = time.monotonic()
    try:
        a = ap.parse_args(argv)
        if not 1 <= a.top <= jc.MAX_JEV_CHUNKS:
            raise Usage("--top must be 1-%d" % jc.MAX_JEV_CHUNKS)
        budget, budget_note = check_budget(a.budget)
        instruments = parse_instruments(a.instruments, ECHO_INSTRUMENTS)
        root = os.path.abspath(a.root)
        if not os.path.isdir(root):
            raise Usage("--root %s is not a directory" % a.root)
        if not (a.jev_timeout > 0):
            raise Usage("--jev-timeout must be above 0")
        tools = jc.default_tools(os.path.expanduser("~"))
        files = parse_patch(get_patch(a.diff, root, tools))
    except Usage as e:
        sys.stderr.write("jev_echo: usage: %s\n" % e)
        return 64
    ctx = jc.Context(root, tools)
    removed, added, sites, touched = defect(files)
    head = [("diff", a.diff), ("defect (removed)", " | ".join(removed) or "(none)"),
            ("fix (added)", " | ".join(added) or "(none)")]
    extra = ["fixed site: " + (", ".join("%s:%d-%d" % s for s in sites) or "(none)")]
    extra += [budget_note] if budget_note else []
    mode, scores, chunks, notes, answered = (jc.JEV_BASE if a.order == "jev" else a.order), None, [], [], []
    if not removed:
        rank = "nothing to echo: the diff removes no code line, so it names no anti-pattern (Jev not asked)"
    else:
        hits, notes, answered = candidates(ctx, removed, added, touched, instruments)
        chunks = jc.merge(hits, jc.words("\n".join(removed)))
        query = "the defect: %s; fixed as: %s" % ("\n".join(removed)[:SIDE_CHARS], "\n".join(added)[:SIDE_CHARS])
        mode, scores, rank = rank_chunks(a.order, query, chunks, a.top, a, instructions=INSTRUCTIONS,
                                         what="candidate sites")
        if scores is not None:
            rank += "; question: " + INSTRUCTIONS
    pack = jc.build_pack("jev echo", head, chunks, mode, scores, rank, answered, notes, extra=extra, tail=[NOTE],
                         with_files=False)
    sys.stdout.write(jc.render(pack, a.top, budget, a.json))
    sys.stderr.write("jev_echo: %d removed lines, %d candidate sites, %d ranked by Jev, wall %.1f s\n"
                     % (len(removed), len(chunks), len(scores or {}), time.monotonic() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
