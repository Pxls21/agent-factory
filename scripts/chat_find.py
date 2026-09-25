#!/usr/bin/env python3
"""chat_find: where did this bug first appear in the chat? (D-090, design L5; brief tasks/briefs/system1/L5-brief.md)

usage: chat_find.py "<description or error text>" [--match words|error] [--order lexical|jev] [--hits N]
                    [--since T] [--until T] [--kind K ...] [--exclude NAME ...] [--json] [--excerpt]
                    [--projects-dir DIR] [--jev-url URL] [--no-jev-log]

The corpus: every transcript under the projects dir (default: the parent of hiccup_scan.DEFAULT_PROJECT_DIR, so every
session root, `-home-user-agent-factory` too): each project folder's `*.jsonl` (main sessions), `*/subagents/*.jsonl`
(subagents) and `*/subagents/workflows/*/*.jsonl` (workflow agents); a `journal.jsonl` is not a transcript. Each file is
streamed line by line by hiccup_scan.Scan.feed (imported: record() is overridden, the loop is reused), so memory holds one
line plus the candidates, never a whole transcript.

A document is one content block of one record, with a first line of the record's own fields (`tool_use Bash`,
`tool_result Bash is_error`, `hook PostToolUse <name>`, `system api_error`, `stop_reason refusal` for an assistant record
whose stop is not routine). Kinds: tool_error, tool_result, tool_input, assistant_text, thinking, user_text (a queued
prompt too), hook, system; `attachment` (the other attachment types: file and skill re-injections, reminders) only with
`--kind attachment`. Other record types (last-prompt, mode, titles) are not searched.

--match words (the default): BM25 (k1 1.2, b 0.75) over hiccup_scan's words (`[a-z][a-z0-9_]{2,}` of the lower-cased text,
its stop words out); N, the mean length and each term's document frequency are counted over the documents the kind and time
filters keep. The hits are the top N by score (ties: file order, line, block). --match error: the query and every document
pass the part of hiccup_scan.excerpt's normalization that removes numbers, ids and paths (control characters and
separators to spaces, URLs U, runs of 20+ identifier characters T, numbers N), whitespace runs become one space, and a
document matches when it holds the normalized query; every match is a hit, earliest first. Its value-hiding rules
(KEY=value to KEY=V, a quoted string over 40 characters to S) stay out of the match: over a whole document they swallow
the error itself (AF-AP-181's first appearance is a CI log inside one JSON string, one S), and its scrub and its cut are
for display.

--order jev reorders the top N hits (N at most 48) through the local Laya server by scripts/jev_context.py's jev_rank (the
local endpoint only, never the bridge; D-074: Jev stays model-based; KC-J5: it reorders the hits, it never replaces them).
When the server does not answer, ONE stderr line says so and the lexical order stands.

The first appearance: the earliest hit overall and the earliest hit in each transcript (time, transcript, line = the
JSONL line number, block, kind, and the tool call: the record's own call, the call its result answers, the call a hook or
system record names, or else the last call before it in that transcript).

No transcript text by default: the output holds counts, ids, times and positions only, and the query is shown as a
sha256 prefix. --excerpt adds, per hit, the whole block scrubbed by transcript_export.scrub_payload (scrub's named rules
first), then a window around the match passed through hiccup_scan.excerpt (scrub, normalize, scrub, cut at 160 characters).
Wall time and peak memory go to stderr, so two runs over the same bytes print the same stdout.

exit: 0 searched (with or without hits); 2 no transcript, or the projects dir is missing; 64 usage error. Standard library.
"""
import argparse
import collections
import datetime
import glob
import hashlib
import json
import math
import os
import re
import resource
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import hiccup_scan  # noqa: E402  (the transcript streaming loop, timestamps, tool-result text, the excerpt)
# hiccup_scan's private word and normalization patterns, imported (never copied) so both tools read text one way
from hiccup_scan import (_CTRL, _NUM, _RUN, _SEPARATORS, _STOP, _URL, _WORD, CUT, canon_ts, excerpt,  # noqa: E402
                         result_text)
from transcript_export import scrub, scrub_payload  # noqa: E402

DEFAULT_PROJECTS = os.path.dirname(hiccup_scan.DEFAULT_PROJECT_DIR)
KINDS = ("tool_error", "tool_result", "tool_input", "assistant_text", "thinking", "user_text", "hook", "system",
         "attachment")
DEFAULT_KINDS = KINDS[:-1]
ROUTINE_STOPS = (None, "tool_use", "end_turn", "stop_sequence")
K1, B = 1.2, 0.75
HITS = 10
JEV_MAX = 48                    # = jev_context.MAX_JEV_CHUNKS (tests hold the two equal)
JEV_WINDOW = 600                # characters of a hit's scrubbed text around the match sent to Jev
JEV_INSTRUCTIONS = "Does this transcript record show the problem the query describes?"
SYSTEM_SKIP = frozenset(("type", "subtype", "cwd", "entrypoint", "gitBranch", "isSidechain", "isMeta", "level",
                         "parentUuid", "logicalParentUuid", "sessionId", "slug", "timestamp", "userType", "uuid",
                         "version", "agentId", "requestId", "refusedUserMessageUuid", "toolUseID"))
_WS = re.compile(r"\s+")
_WHEN = re.compile(r"^(\d{4}-\d\d-\d\d)(?:T(\d\d)(?::(\d\d)(?::(\d\d)(?:\.(\d{1,9}))?)?)?)?Z?$")
_UNSTABLE = re.compile(r"[NTU ?]")         # what normalize() can write (`?` for a lone surrogate); the rest is raw text


class Usage(Exception):
    pass


# ---------- the corpus ----------

def discover(projects):
    """Every transcript path, sorted within each project folder: hiccup_scan.main()'s glob pair (`*.jsonl`,
    `*/subagents/*.jsonl`; inline in its main(), so not importable) per folder, plus the workflow agents it never
    reaches."""
    out = []
    for proj in sorted(os.listdir(projects)):
        d = os.path.join(projects, proj)
        if not os.path.isdir(d):
            continue
        for pat in (("*.jsonl",), ("*", "subagents", "*.jsonl"), ("*", "subagents", "workflows", "*", "*.jsonl")):
            out += sorted(p for p in glob.glob(os.path.join(d, *pat)) if os.path.basename(p) != "journal.jsonl")
    return out


def describe(path, projects):
    """{root, kind, session, agent, workflow, path} from where the file sits (never from its content)."""
    rel = os.path.relpath(path, projects)
    parts = rel.split(os.sep)
    stem = parts[-1][:-len(".jsonl")]
    agent = stem[len("agent-"):] if stem.startswith("agent-") else stem
    if len(parts) == 2:
        return {"root": parts[0], "kind": "main", "session": stem, "agent": None, "workflow": None, "path": rel}
    if len(parts) == 6:
        return {"root": parts[0], "kind": "workflow", "session": parts[1], "agent": agent, "workflow": parts[4],
                "path": rel}
    return {"root": parts[0], "kind": "subagent", "session": parts[1], "agent": agent, "workflow": None, "path": rel}


def label(t):
    who = t["session"] if t["kind"] == "main" else (t["agent"] if t["kind"] == "subagent" else
                                                     "%s/%s" % (t["workflow"], t["agent"]))
    return "%s %s %s" % (t["kind"], t["root"], who)


# ---------- documents ----------

def flatten(value):
    """Every string and number in a JSON value, depth first, in stored order (iterative: no recursion limit)."""
    out, stack = [], [value]
    while stack:
        v = stack.pop()
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, bool) or v is None:
            continue
        elif isinstance(v, (int, float)):
            out.append(str(v))
        elif isinstance(v, dict):
            stack.extend(reversed(list(v.values())))
        elif isinstance(v, list):
            stack.extend(reversed(v))
    return "\n".join(out)


def result_texts(content):
    """A tool result's text: hiccup_scan.result_text gives the first text part; the other parts follow it."""
    first, _ = result_text(content)
    if isinstance(content, list):
        parts = [p["text"] for p in content if isinstance(p, dict) and p.get("type") == "text"
                 and isinstance(p.get("text"), str)]
        if len(parts) > 1:
            return "\n".join(parts)
    return first


def _s(v):
    return v if isinstance(v, str) else ""


def docs_of(r, calls, want=KINDS):
    """[(block, kind, meta, text, tool, call_id, relation)] for one record, for the kinds in `want` only (a text is
    built only when its kind is wanted). `calls` is the transcript's state: `names` (tool_use id -> tool name) and
    `last` (the last (name, id) seen); it is updated whatever `want` holds."""
    t = r.get("type")
    m = r.get("message") if isinstance(r.get("message"), dict) else {}
    c = m.get("content")
    prev = calls["last"]
    out = []
    if t == "assistant":
        stop = m.get("stop_reason")
        head = "stop_reason %s" % stop if stop not in ROUTINE_STOPS and isinstance(stop, str) else ""
        for i, b in enumerate(c if isinstance(c, list) else []):
            if not isinstance(b, dict):
                continue
            bt = b.get("type")
            if bt == "text" and "assistant_text" in want:
                out.append((i, "assistant_text", head, _s(b.get("text"))) + prev)
            elif bt == "thinking" and "thinking" in want:
                out.append((i, "thinking", head, _s(b.get("thinking"))) + prev)
            elif bt == "tool_use":
                name = b.get("name") if isinstance(b.get("name"), str) and b.get("name") else "?"
                uid = b.get("id") if isinstance(b.get("id"), str) and b.get("id") else None
                if uid:
                    calls["names"][uid] = name
                prev = calls["last"] = (name, uid, "preceding")
                if "tool_input" in want:
                    out.append((i, "tool_input", ("tool_use %s %s" % (name, head)).strip(), flatten(b.get("input")),
                                name, uid, "self"))
        if head and not (isinstance(c, list) and c) and "assistant_text" in want:
            out.append((0, "assistant_text", head, "") + prev)
    elif t == "user":
        if isinstance(c, str) and "user_text" in want:
            out.append((0, "user_text", "", c) + prev)
        for i, b in enumerate(c if isinstance(c, list) else []):
            if not isinstance(b, dict):
                continue
            if b.get("type") == "text" and "user_text" in want:
                out.append((i, "user_text", "", _s(b.get("text"))) + prev)
            elif b.get("type") == "tool_result":
                uid = b.get("tool_use_id") if isinstance(b.get("tool_use_id"), str) else None
                name = calls["names"].get(uid, "<unmatched>")
                err = b.get("is_error") is True
                if ("tool_error" if err else "tool_result") not in want:
                    continue
                out.append((i, "tool_error" if err else "tool_result",
                            "tool_result %s%s" % (name, " is_error" if err else ""), result_texts(b.get("content")),
                            name, uid, "result"))
    elif t == "attachment" and isinstance(r.get("attachment"), dict):
        a = r["attachment"]
        at = a.get("type") if isinstance(a.get("type"), str) else "?"
        named = _named(a.get("toolUseID"), calls, prev)
        if at.startswith("hook"):
            if "hook" in want:
                meta = "hook %s %s" % (_s(a.get("hookEvent")), _s(a.get("hookName")))
                out.append((0, "hook", meta, flatten([a.get(k) for k in ("command", "stdout", "stderr", "content")]))
                           + named)
        elif at == "queued_command":
            if "user_text" in want:
                out.append((0, "user_text", "", flatten(a.get("prompt"))) + prev)
        elif "attachment" in want:
            out.append((0, "attachment", "attachment %s" % at, flatten({k: v for k, v in a.items() if k != "type"}))
                       + named)
    elif t == "system" and "system" in want:
        body = flatten({k: v for k, v in r.items() if k not in SYSTEM_SKIP})
        out.append((0, "system", "system %s" % _s(r.get("subtype")), body) + _named(r.get("toolUseID"), calls, prev))
    return out


def _named(uid, calls, prev):
    if isinstance(uid, str) and uid in calls["names"]:
        return (calls["names"][uid], uid, "named")
    return prev


# ---------- matching ----------

def terms_of(query):
    """The query's words, in order, once each (hiccup_scan's word pattern and stop words)."""
    seen = []
    for w in _WORD.findall(query.lower()):
        if w not in _STOP and w not in seen:
            seen.append(w)
    return seen


def normalize(text):
    """hiccup_scan.excerpt's normalization of numbers, ids and paths, in its order (not its KEY=V and S rules, its scrub
    or its cut), then one space per whitespace run."""
    s = str(text).encode("utf-8", "replace").decode("utf-8")
    s = _CTRL.sub(" ", s.translate(_SEPARATORS))
    s = _URL.sub("U", s)
    s = _RUN.sub("T", s)
    s = _NUM.sub("N", s)
    return _WS.sub(" ", s).strip()


def anchor_of(nq):
    """The longest piece of the normalized query that normalize() cannot have written (no N, T, U, ? or space):
    a document whose normalized text holds the query holds this piece verbatim in its raw text (every replacement
    writes one of those characters and never an empty string), so it is a safe pre-filter."""
    return max(_UNSTABLE.split(nq), key=len)


class _Scan(hiccup_scan.Scan):
    """hiccup_scan.Scan with record() replaced: the streaming (feed) is the parent's; each record becomes documents."""

    def __init__(self, cfg):
        super().__init__([])
        self.cfg = cfg
        self.file = None
        self.docs = self.records = self.total_len = 0
        self.kinds = collections.Counter()
        self.cands = []
        self.df = [0] * len(cfg["terms"])

    def start(self, idx):
        self.file = idx
        self.calls = {"names": {}, "last": (None, None, "none")}
        self.lines0 = sum(v[2] for v in self.inputs.values())
        self.bytes0 = sum(v[1] for v in self.inputs.values())

    def record(self, r, nbytes, file_agent):
        self.records += 1
        line = sum(v[2] for v in self.inputs.values()) - self.lines0          # feed counted this line already
        off = sum(v[1] for v in self.inputs.values()) - self.bytes0 - nbytes
        cfg = self.cfg
        docs = docs_of(r, self.calls, cfg["kinds"])
        if not docs:
            return
        ts = canon_ts(r.get("timestamp"))
        if cfg["since"] or cfg["until"]:
            if ts is None or (cfg["since"] and ts < cfg["since"]) or (cfg["until"] and ts[:len(cfg["until"])] > cfg["until"]):
                return
        for block, kind, meta, text, tool, call, rel in docs:
            self.docs += 1
            self.kinds[kind] += 1
            doc = meta + "\n" + text if meta else text
            pos = (self.file, line, block, kind, ts, tool, call, rel, off)
            if cfg["match"] == "error":
                a = cfg["anchor"]
                if (not a or a in doc) and cfg["nq"] in normalize(doc):
                    self.cands.append(pos + (None, None))
                continue
            toks = _WORD.findall(doc.lower())
            self.total_len += len(toks)
            got = collections.Counter(toks)
            tf = tuple(got.get(w, 0) for w in cfg["terms"])
            if any(tf):
                for i, f in enumerate(tf):
                    if f:
                        self.df[i] += 1
                self.cands.append(pos + (tf, len(toks)))


def rank_words(sc):
    """[(candidate, BM25 score)], best first; ties by file, line, block."""
    n = sc.docs
    avgdl = sc.total_len / n if n and sc.total_len else 1.0
    idf = [math.log(1 + (n - d + 0.5) / (d + 0.5)) for d in sc.df]
    scored = []
    for c in sc.cands:
        tf, dl = c[9], c[10]
        norm = K1 * (1 - B + B * dl / avgdl)
        s = sum(idf[i] * f * (K1 + 1) / (f + norm) for i, f in enumerate(tf) if f)
        scored.append((-s, c[0], c[1], c[2], c))
    scored.sort(key=lambda x: x[:4])
    return [(c, -neg) for neg, _, _, _, c in scored]


def when_key(c):
    return (c[4] or "~", c[0], c[1], c[2])


# ---------- text for a hit (only with --excerpt or --order jev) ----------

def hit_text(path, c):
    """The hit's block text, re-read from its line (its byte offset), whole: nothing is cut before the scrub."""
    try:
        with open(path, "rb") as fh:
            fh.seek(c[8])
            r = json.loads(fh.readline())
    except (OSError, ValueError, RecursionError):
        return ""
    for block, kind, meta, text, *_ in docs_of(r, {"names": {}, "last": (None, None, "none")}, (c[3],)):
        if block == c[2] and kind == c[3]:
            return text
    return ""


def window(text, cfg, width):
    """A window of the SCRUBBED text around the first match (a query word, or the error anchor)."""
    s = scrub_payload(text)
    low = s.lower()
    keys = [cfg["anchor"].lower()] if cfg["match"] == "error" and cfg["anchor"] else cfg["terms"]
    at = min((p for p in (low.find(k) for k in keys) if p >= 0), default=0)
    start = max(0, at - width // 4)
    return s[start:start + width]


# ---------- the Jev order ----------

def jev_order(query, hits, paths, cfg):
    """(hits reordered, None) or (hits unchanged, reason)."""
    if not hits:
        return hits, "no hit to rank"
    try:
        import jev_context
        rank, reorder = jev_context.jev_rank, jev_context.reorder
    except Exception as e:
        return hits, "scripts/jev_context.py did not import (%s)" % type(e).__name__
    chunks = []
    for i, (c, s) in enumerate(hits):
        text = "%s %s\n%s" % (c[3], c[5] or "", window(hit_text(paths[c[0]], c), cfg, JEV_WINDOW))
        chunks.append({"id": "h%d" % i, "path": cfg["labels"][c[0]], "line": c[1], "instruments": ["chat"],
                       "text": text, "lexical": sum(1 for f in (c[9] or ()) if f), "agreement": 1})
    scores, reason, _sent = rank(query, chunks, instructions=JEV_INSTRUCTIONS, url=cfg["jev_url"],
                                 log=cfg["jev_log"], protect=chunks)
    if scores is None:
        return hits, reason or "no answer"
    ids = {id(h): "h%d" % i for i, h in enumerate(hits)}
    return reorder(hits, lambda h: scores.get(ids[id(h)])), None


# ---------- output ----------

def hit_row(rank, c, score, tr, text=None):
    row = {"rank": rank, "score": None if score is None else round(score, 4),
           "terms_matched": None if c[9] is None else sum(1 for f in c[9] if f),
           "time": (c[4][:23] + "Z") if c[4] else None, "transcript": tr, "line": c[1], "block": c[2], "kind": c[3],
           "tool": None if c[5] is None else scrub(c[5]), "call_id": None if c[6] is None else scrub(c[6]),
           "call": c[7]}
    if text is not None:
        row["excerpt"] = text
    return row


def line_of(h, nterms):
    score = "" if h["score"] is None else "score %.4f terms %d/%d | " % (h["score"], h["terms_matched"], nterms)
    call = "%s %s (%s)" % (h["tool"] or "-", h["call_id"] or "-", h["call"])
    return "rank %d | %s%s | %s | line %d block %d | %s | %s" % (
        h["rank"], score, h["time"] or "-", label(h["transcript"]), h["line"], h["block"], h["kind"], call)


def render_text(res):
    q, c = res["query"], res["corpus"]
    order = res["order"] + (" (jev fell back)" if res.get("jev_fallback") else "")
    L = ["chat_find: match=%s order=%s hits=%d window=%s..%s kinds=%s query=sha256:%s chars=%d terms=%s" % (
        res["match"], order, res["hits_asked"], res["window"]["since"] or "-", res["window"]["until"] or "-",
        ",".join(res["kinds"]), q["sha256_12"], q["chars"], q["terms"] if q["terms"] is not None else "-"),
        "corpus: transcripts=%d (main %d, subagent %d, workflow %d) excluded=%d unreadable=%d records=%d unparsable=%d "
        "documents=%d candidates=%d" % (c["transcripts"], c["main"], c["subagent"], c["workflow"], c["excluded"],
                                        c["unreadable"], c["records"], c["unparsable"], c["documents"],
                                        c["candidates"])]
    nt = q["terms"] or 0
    if res["first"] is None:
        L.append("first: none (no hit)")
    else:
        L.append("first: " + line_of(res["first"], nt))
        L.append("per transcript (the earliest hit in each, earliest first; %d of %d transcripts):" % (
            len(res["per_transcript"]), res["per_transcript_total"]))
        L += ["  " + line_of(h, nt) for h in res["per_transcript"]]
        L.append("hits (%d shown of %d, in %s order):" % (len(res["hits"]), res["hits_total"],
                                                         "time" if res["match"] == "error" else res["order"]))
        for h in res["hits"]:
            L.append("  " + line_of(h, nt))
            if "excerpt" in h:
                L.append("    excerpt: " + h["excerpt"])
    return "\n".join(L) + "\n"


# ---------- the command ----------

def _when(v, what):
    m = _WHEN.match(v or "")
    if not m:
        raise Usage("%s must be YYYY-MM-DD[THH[:MM[:SS[.fff]]]][Z], got %r" % (what, v))
    try:
        datetime.date.fromisoformat(m.group(1))
        if m.group(2) is not None:
            datetime.time(int(m.group(2)), int(m.group(3) or 0), int(m.group(4) or 0))
    except ValueError as e:
        raise Usage("%s: %s" % (what, e))
    return v[:-1] if v.endswith("Z") else v


def peak_mb():
    """This process's own peak RSS in MB: VmHWM (per address space, so exec resets it). ru_maxrss keeps the PARENT's
    high-water mark across fork and exec (measured: one run reported 24.0 MB from a small parent, 310.0 MB from a parent
    holding 300 MB); it is the fallback where /proc is absent."""
    try:
        with open("/proc/self/status") as fh:
            for ln in fh:
                if ln.startswith("VmHWM:"):
                    return int(ln.split()[1]) / 1024.0
    except (OSError, ValueError, IndexError):
        pass
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Usage(message)


def parse(argv):
    ap = _Parser(prog="chat_find.py", description=__doc__.splitlines()[0])
    ap.add_argument("query")
    ap.add_argument("--match", choices=("words", "error"), default="words")
    ap.add_argument("--order", choices=("lexical", "jev"), default="lexical")
    ap.add_argument("--hits", type=int, default=HITS)
    ap.add_argument("--since")
    ap.add_argument("--until")
    ap.add_argument("--kind", action="append", choices=KINDS)
    ap.add_argument("--exclude", action="append", default=[], help="a transcript's file name, agent id or session id")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--excerpt", action="store_true", help="add a scrubbed excerpt of 160 characters per hit")
    ap.add_argument("--projects-dir", default=DEFAULT_PROJECTS)
    ap.add_argument("--jev-url", help="pin one loopback Laya endpoint (tests)")
    ap.add_argument("--no-jev-log", action="store_true", help="skip .jev/calls.jsonl")
    a = ap.parse_args(argv)
    if not a.query.strip():
        raise Usage("the query is empty")
    if a.hits < 1:
        raise Usage("--hits must be at least 1")
    if a.order == "jev" and a.match == "error":
        raise Usage("--order jev reorders word hits; an error string's hits are in time order")
    if a.order == "jev" and a.hits > JEV_MAX:
        raise Usage("--order jev takes at most %d hits" % JEV_MAX)
    a.since = _when(a.since, "--since") if a.since is not None else None
    a.until = _when(a.until, "--until") if a.until is not None else None
    return a


def search(a):
    """The whole run as a result dict (render_text / json.dumps print it)."""
    if not os.path.isdir(a.projects_dir):
        raise FileNotFoundError("no projects dir: %s" % a.projects_dir)
    trs, excluded = [], 0
    for p in discover(a.projects_dir):
        t = describe(p, a.projects_dir)
        if {os.path.basename(p), t["agent"], t["session"] if t["kind"] == "main" else None} & set(a.exclude):
            excluded += 1
            continue
        trs.append((p, t))
    if not trs:
        raise FileNotFoundError("no transcript under %s" % a.projects_dir)
    terms = terms_of(a.query)
    nq = normalize(a.query) if a.match == "error" else None
    if a.match == "words" and not terms:
        raise Usage("the query has no word of 3+ letters outside the stop words")
    if a.match == "error" and not nq:
        raise Usage("the error string is empty after normalization")
    cfg = {"match": a.match, "terms": terms if a.match == "words" else [], "nq": nq,
           "anchor": anchor_of(nq) if nq else None, "kinds": set(a.kind or DEFAULT_KINDS), "since": a.since,
           "until": a.until, "jev_url": a.jev_url, "jev_log": not a.no_jev_log,
           "labels": [label(t) for _, t in trs]}
    sc = _Scan(cfg)
    unreadable = 0
    for i, (p, _t) in enumerate(trs):
        sc.start(i)
        try:
            sc.feed(p)
        except OSError:
            unreadable += 1
    if a.match == "words":
        ranked = rank_words(sc)
        hits = ranked[:a.hits]
        total = len(ranked)
    else:
        ranked = [(c, None) for c in sorted(sc.cands, key=when_key)]
        hits, total = ranked, len(ranked)
    res = {"tool": "chat_find", "match": a.match, "order": a.order if a.match == "words" else "time",
           "order_requested": a.order, "hits_asked": a.hits,
           "query": {"sha256_12": hashlib.sha256(a.query.encode("utf-8", "replace")).hexdigest()[:12],
                     "chars": len(a.query), "terms": len(terms) if a.match == "words" else None},
           "window": {"since": a.since, "until": a.until}, "kinds": sorted(cfg["kinds"]),
           "corpus": {"transcripts": len(trs), "main": sum(1 for _, t in trs if t["kind"] == "main"),
                      "subagent": sum(1 for _, t in trs if t["kind"] == "subagent"),
                      "workflow": sum(1 for _, t in trs if t["kind"] == "workflow"), "excluded": excluded,
                      "unreadable": unreadable, "records": sc.records,
                      "unparsable": sum(v[3] for v in sc.inputs.values()), "documents": sc.docs,
                      "documents_by_kind": dict(sorted(sc.kinds.items())), "candidates": len(sc.cands)},
           "hits_total": total}
    if a.order == "jev" and a.match == "words":
        hits, why = jev_order(a.query, hits, [p for p, _ in trs], cfg)
        if why is not None:
            res["order"], res["jev_fallback"] = "lexical", str(why)[:160]
    shown = hits[:a.hits]
    first = min(shown, key=lambda h: when_key(h[0]), default=None)
    per = {}
    for h in hits:                  # words: the top N; error: every match
        if h[0][0] not in per or when_key(h[0]) < when_key(per[h[0][0]][0]):
            per[h[0][0]] = h
    per_sorted = sorted(per.values(), key=lambda h: when_key(h[0]))
    rank_of = {id(h[0]): i + 1 for i, h in enumerate(hits)}

    def row(h):
        c, s = h
        text = excerpt(window(hit_text(trs[c[0]][0], c), cfg, 2 * CUT)) if a.excerpt else None
        return hit_row(rank_of[id(c)], c, s, trs[c[0]][1], text)

    res["first"] = row(first) if first else None
    res["per_transcript"] = [row(h) for h in per_sorted[:a.hits]]
    res["per_transcript_total"] = len(per_sorted)
    res["hits"] = [row(h) for h in shown]
    return res


def main(argv=None):
    t0 = time.monotonic()
    try:
        a = parse(sys.argv[1:] if argv is None else argv)
        res = search(a)
    except Usage as e:
        sys.stderr.write("usage: chat_find.py \"<description or error text>\" [options] (see --help)\nchat_find: %s\n" % e)
        return 64
    except FileNotFoundError as e:
        sys.stderr.write("chat_find: %s\n" % e)
        return 2
    if res.get("jev_fallback"):
        sys.stderr.write("chat_find: --order jev fell back to the lexical order: %s\n" % res["jev_fallback"])
    sys.stdout.write(json.dumps(res, sort_keys=True) + "\n" if a.json else render_text(res))
    sys.stderr.write("chat_find: wall_s=%.1f peak_rss_mb=%.1f\n" % (time.monotonic() - t0, peak_mb()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
