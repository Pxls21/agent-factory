#!/usr/bin/env python3
"""s1_scores.py — pair every stamped System-1 injection in Claude Code transcripts with the agent's score of it.

S1-RATE (task #295, D-092 item 3). scripts/hook_context.py stamps each text it hands the model: a first line
`[S1 <id> <source>]` and a last line that asks the agent to begin its next text with `S1-RATE <id> rel=<0-3> use=<0-3>`
and an optional note. This script reads a session's transcripts (its main JSONL and every file under `subagents/`),
finds every text a hook handed the model, pairs each stamped one with the first assistant text after it in the same
thread, parses the S1-RATE lines at the top of that text, and writes one JSON line per injection. The stamp and the
score syntax come from hook_context.py (the ONE implementation); nothing here restates them.

The records that hold what a hook hands the model (measured on the transcripts and read from the Claude Code 2.1.280
binary; tasks/briefs/system1/S1-RATE-report.md section 2):
  hook_additional_context   attachment.content: a list of texts, the additionalContext of any event
  hook_success              attachment.content on UserPromptSubmit and SessionStart: a hook's plain stdout
  hook_blocking_error       attachment.blockingError.blockingError: "[<command>]: <stderr>" (a PostToolUse exit 2)
  tool_result               a user record's tool_result with is_error: "<hookName> hook error: [<command>]: <stderr>"
                            (a PreToolUse exit 2: the call was blocked)
The hook_success record of a PreToolUse or PostToolUse hook holds only the raw JSON stdout, which the model never reads;
it is not read here (it would count each additionalContext twice).

Threads: every record belongs to its file and its agentId (`main` when it has none), so the main thread and each
subagent are kept apart. Assistant records the harness writes itself (model `<synthetic>`, API errors) are not texts.

The status of an injection. Its first assistant text decides; later texts can only make it late:
  scored      a well-formed line for its id at the top of that first text (only S1-RATE lines and blank lines before it)
  malformed   a line for it that breaks the syntax: `why` is bad-id (a line at the top with no valid id, given to the
              first injection of that text left without a line), range (a score outside 0-3), order (use before rel),
              note-too-long, syntax (anything else), or below-text (a well-formed line under other text)
  late        no line in its first text; a well-formed line for its id at the top of a later text of the thread
  missing     assistant text came after it, and no text of the thread has a line for it
  open        no assistant text came after it in its thread (yet): not counted in the compliance rate
A line whose id names no injection of its thread before it is a row of its own, `unknown-id`; another line for an id
already settled is a row of its own, `duplicate`; a line at the top with no valid id and no injection left to take it is
a row `malformed` with no id.

Each row: id, source, event, tool, session, agent, time, kind (the record kind, or `score` for a row of its own),
status, why, rel, use, note (through transcript_export.scrub), whole (its last line is its own request: false when the
harness swapped the text for a preview, AF-AP-183), sections (each `full details: <file> § <heading>` pointer line in
the injection; a System-1 block also carries `sha`, the first 16 hex digits of the sha256 of its text from its
`[system1 · ` label line to its pointer line), and with the state files present: from injections.jsonl the wrapper's
tool_use_id and sha_ok (its sha256 equals the text found here); from system1.jsonl each section's row, key, skill,
heading, score and project.

Usage: s1_scores.py [--jev DIR] [--out FILE|-] PATH...
  PATH: a session's main transcript (<session>.jsonl, its <session>/subagents/ read too), a session directory, or one
  .jsonl file. --jev: the state directory (default <repo>/.jev). --out: where the rows go ('-' for stdout); without it
  only the summary is printed. The summary goes to stdout (to stderr with --out -): per record kind, the injections
  found and how many carry a stamp; per source, the injections, the stamped ones, each status, the compliance rate
  (scored over the stamped injections a text followed) and the mean rel and use (scored and late). It holds ids and
  counts only, never an injection's text or a prompt. Exit 0; 2 on a usage error.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hook_context as hc  # noqa: E402  the ONE implementation of the stamp and the score syntax
from transcript_export import scrub  # noqa: E402

ROOT = os.path.dirname(HERE)
KINDS = ("hook_additional_context", "hook_success", "hook_blocking_error", "tool_result")
PLAIN_EVENTS = ("UserPromptSubmit", "SessionStart")        # the events whose plain stdout reaches the model
ANY_ID_RX = re.compile(r"(?<![0-9A-Za-z])" + hc.ID_RX + r"(?![0-9A-Za-z])")
ATTEMPT_RX = re.compile(r"[*_`>#~-]{0,4}\s*S1-RATE\b")    # a line that tries to be a score line
HOOK_ERROR_RX = re.compile(r"([A-Za-z]+):(\S+) hook error: \[")
TAIL_STAMP_RX = re.compile(r"\]: (" + hc.STAMP_RX.pattern + r")\Z")   # a stamped stderr, after the harness's prefix
ERROR_CMD_RX = re.compile(r"hook error: \[(.*?\.(?:py|sh|js|mjs|cjs|rb|pl))\]: ")
POINTER_RX = re.compile(r"full details: (\S+) § (.+)")
LABEL = "[system1 · "
SECTION_FIELDS = ("row", "key", "skill", "heading", "score", "project")
SETTLED = ("scored", "late", "malformed")


def sha16(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def stem(cmd):
    """The stem of the last script a hook command names (the wrapped hook: it comes after the wrapper), or None."""
    names = hc.SCRIPT_RX.findall(cmd or "")
    return names[-1] if names else None


# ---------------------------------------------------------------- reading the transcripts

def transcript_files(path):
    """The files of a PATH: a main transcript and its subagents/ files, a session directory, or one file."""
    if os.path.isdir(path):
        base = path.rstrip("/")
        files = [base + ".jsonl"] if os.path.isfile(base + ".jsonl") else []
    elif os.path.isfile(path):
        base, files = path[:-len(".jsonl")] if path.endswith(".jsonl") else path, [path]
    else:
        raise FileNotFoundError(path)
    return files + sorted(glob.glob(os.path.join(base, "subagents", "**", "*.jsonl"), recursive=True))


def records(path):
    """The records of one JSONL file that can hold a hook's text or an assistant text, in file order."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if '"hook_' not in line and "hook error" not in line and '"assistant"' not in line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if isinstance(r, dict):
                yield r


def injections_of(r):
    """[(kind, event, tool, text, command)]: each text in record `r` that a hook handed the model."""
    out, a = [], r.get("attachment")
    if r.get("type") == "attachment" and isinstance(a, dict):
        kind, ev, name = a.get("type"), a.get("hookEvent"), a.get("hookName")
        tool = name.split(":", 1)[1] if isinstance(name, str) and ":" in name else None
        if kind == "hook_additional_context":
            texts = a.get("content") if isinstance(a.get("content"), list) else [a.get("content")]
            out += [(kind, ev, tool, t, None) for t in texts if isinstance(t, str) and t]
        elif kind == "hook_success" and ev in PLAIN_EVENTS and isinstance(a.get("content"), str) and a["content"]:
            out.append((kind, ev, tool, a["content"], a.get("command")))
        elif kind == "hook_blocking_error":
            b = a.get("blockingError")
            msg, cmd = (b.get("blockingError"), b.get("command")) if isinstance(b, dict) else (b, None)
            if isinstance(msg, str) and msg:
                out.append((kind, ev, tool, msg, cmd if isinstance(cmd, str) else None))
    elif r.get("type") == "user":
        blocks = (r.get("message") or {}).get("content")
        for x in blocks if isinstance(blocks, list) else []:
            if not (isinstance(x, dict) and x.get("type") == "tool_result" and x.get("is_error")):
                continue
            body = x.get("content")
            if isinstance(body, list):
                body = "".join(b.get("text", "") for b in body if isinstance(b, dict) and isinstance(b.get("text"), str))
            m = HOOK_ERROR_RX.match(body) if isinstance(body, str) else None
            if m:
                out.append(("tool_result", m.group(1), m.group(2), body, None))
    return out


def text_of(r):
    """The text of an assistant record the model wrote, or None."""
    if r.get("type") != "assistant":
        return None
    msg = r.get("message") or {}
    if msg.get("model") == "<synthetic>" or r.get("isApiErrorMessage"):
        return None
    for b in msg.get("content") or []:
        if isinstance(b, dict) and b.get("type") == "text" and isinstance(b.get("text"), str) and b["text"].strip():
            return b["text"]
    return None


def stamp_of(kind, text):
    """(id, source, the stamped text as the hook's wrapper wrote it) when `text` carries a stamp, else None."""
    first = text.split("\n", 1)[0]
    if kind in ("tool_result", "hook_blocking_error"):
        m = TAIL_STAMP_RX.search(first)
        start = m.start(1) if m else None
    else:
        m = hc.STAMP_RX.fullmatch(first)
        start = 0 if m else None
    if start is None:
        return None
    s = hc.STAMP_RX.fullmatch(first[start:])
    return s.group(1), s.group(2), text[start:]


def sections(stamped):
    """Each pointer line of a stamped text between its stamp line and its request line, with the sha of the System-1
    block it closes."""
    out, block = [], None
    for line in stamped.rstrip("\n").split("\n")[1:-1]:
        if line.startswith(LABEL):
            block = [line]
        elif block is not None:
            block.append(line)
        m = POINTER_RX.match(line)
        if m:
            sec = {"file": m.group(1), "heading": m.group(2)}
            if block is not None:
                sec["sha"] = sha16("\n".join(block))
            block = None
            out.append(sec)
    return out


# ---------------------------------------------------------------- scoring lines

def attempts(text):
    """[(line, at_top)]: each line of an assistant text that tries to be a score line, stripped. at_top: only such
    lines and blank lines come before it."""
    out, top = [], True
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            continue
        if ATTEMPT_RX.match(s):
            out.append((s, top))
        else:
            top = False
    return out


def why_malformed(line, top):
    """Why a score line is not well formed at its place (None when it is)."""
    if hc.SCORE_RX.fullmatch(line):
        return None if top else "below-text"
    if not ANY_ID_RX.search(line):
        return "bad-id"
    if re.search(r"\buse=\S*\s+rel=", line):
        return "order"
    if re.search(r"\b(?:rel|use)=(?![0-3](?:\s|$))", line):
        return "range"
    m = re.match(r"S1-RATE " + hc.ID_RX + r" rel=[0-3] use=[0-3] (\S.*)\Z", line)
    if m and len(m.group(1)) > hc.NOTE_MAX:
        return "note-too-long"
    return "syntax"


class Thread:
    """One thread's injections, in order, and the state of the pairing."""

    def __init__(self, agent):
        self.agent, self.rows, self.extra = agent, {}, []
        self.pending, self.awaiting = [], set()

    def settle(self, sid, status, line, why):
        row = self.rows[sid]
        row.update(status=status, why=why)
        m = hc.SCORE_RX.fullmatch(line) if why is None else None
        if m:
            row.update(rel=int(m.group(2)), use=int(m.group(3)), note=scrub(m.group(4)) if m.group(4) else None)

    def row_of_its_own(self, r, sid, status, line, why):
        m = hc.SCORE_RX.fullmatch(line) if why is None else None
        known = self.rows.get(sid) or {}
        self.extra.append({"id": sid, "source": known.get("source"), "event": None, "tool": None,
                           "session": r.get("sessionId"), "agent": self.agent, "time": r.get("timestamp"),
                           "kind": "score", "status": status, "why": why,
                           "rel": int(m.group(2)) if m else None, "use": int(m.group(3)) if m else None,
                           "note": scrub(m.group(4)) if m and m.group(4) else None, "whole": None, "sections": []})

    def on_text(self, r, text):
        """Pair the injections since the last text with the lines at the top of this one; settle late ones."""
        first, self.pending = self.pending, []
        answered, bad = set(), []
        for line, top in attempts(text):
            found = ANY_ID_RX.search(line)
            if found is None:
                if top:
                    bad.append(line)                 # below other text with no valid id: prose, not a score
                continue
            sid, why = found.group(0), why_malformed(line, top)
            if sid in first and sid not in answered:
                answered.add(sid)
                self.settle(sid, "scored" if why is None else "malformed", line, why)
            elif sid in self.awaiting:
                self.awaiting.discard(sid)
                self.settle(sid, "late" if why is None else "malformed", line, why)
            elif sid in self.rows:
                self.row_of_its_own(r, sid, "duplicate", line, why)
            else:
                self.row_of_its_own(r, sid, "unknown-id", line, why)
        for line in bad:
            left = [s for s in first if s not in answered]
            if left:
                answered.add(left[0])
                self.settle(left[0], "malformed", line, why_malformed(line, True))
            else:
                self.row_of_its_own(r, None, "malformed", line, why_malformed(line, True))
        self.awaiting.update(s for s in first if s not in answered)

    def close(self):
        for sid in self.awaiting:
            self.rows[sid]["status"] = "missing"
        for sid in self.pending:
            self.rows[sid]["status"] = "open"


def read_session(paths):
    """(rows, counts): the rows of every stamped injection and score row, and the counts of every injection found."""
    rows, counts = [], {"kind": {}, "source": {}, "files": 0, "threads": 0}
    for path in paths:
        for fp in transcript_files(path):
            counts["files"] += 1
            threads, successes, unstamped = {}, {}, []
            for r in records(fp):
                agent = r.get("agentId") if isinstance(r.get("agentId"), str) else "main"
                th = threads.get(agent) or threads.setdefault(agent, Thread(agent))
                a = r.get("attachment")
                if isinstance(a, dict) and a.get("type") == "hook_success":
                    successes.setdefault((a.get("toolUseID"), a.get("hookEvent")), []).append(a)
                text = text_of(r)
                if text is not None:
                    th.on_text(r, text)
                    continue
                for kind, ev, tool, t, cmd in injections_of(r):
                    k = counts["kind"].setdefault(kind, {"injections": 0, "stamped": 0})
                    k["injections"] += 1
                    st = stamp_of(kind, t)
                    if st is None:
                        unstamped.append((kind, ev, a.get("toolUseID") if isinstance(a, dict) else None, t, cmd))
                        continue
                    sid, source, stamped = st
                    k["stamped"] += 1
                    if sid in th.rows:                         # the same record twice in a thread: counted once
                        continue
                    th.rows[sid] = {"id": sid, "source": source, "event": ev, "tool": tool,
                                    "session": r.get("sessionId"), "agent": agent, "time": r.get("timestamp"),
                                    "kind": kind, "status": None, "why": None, "rel": None, "use": None, "note": None,
                                    "whole": stamped.rstrip("\n").rsplit("\n", 1)[-1] == hc.request(sid),
                                    "sections": sections(stamped), "_sha256": hashlib.sha256(
                                        stamped.encode("utf-8")).hexdigest()}
                    th.pending.append(sid)
            for kind, ev, tuid, t, cmd in unstamped:          # the source of an unstamped text, from its hook command
                src = stem(cmd)
                if src is None and kind == "tool_result":
                    m = ERROR_CMD_RX.search(t.split("\n", 1)[0])
                    src = stem(m.group(1)) if m else None
                if src is None and kind == "hook_additional_context":
                    for s in successes.get((tuid, ev), []):
                        try:
                            ctx = json.loads(s.get("stdout") or "")["hookSpecificOutput"]["additionalContext"]
                        except (ValueError, KeyError, TypeError):
                            continue
                        if ctx == t:
                            src = stem(s.get("command"))
                            break
                c = counts["source"].setdefault(src or "unknown", {"injections": 0})
                c["injections"] += 1
            for th in threads.values():
                th.close()
                counts["threads"] += 1
                rows += list(th.rows.values()) + th.extra
    return rows, counts


# ---------------------------------------------------------------- the state files

def jsonl(path):
    out = []
    for p in (path + ".1", path):
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    if isinstance(rec, dict):
                        out.append(rec)
        except OSError:
            continue
    return out


def join_state(rows, jev):
    """Add the wrapper's and the System-1 hook's telemetry to the rows, when the state files are there."""
    stamps, blocks = {}, {}
    for rec in jsonl(os.path.join(jev, "injections.jsonl")):
        if isinstance(rec.get("id"), str):
            stamps.setdefault(rec["id"], []).append(rec)
    for rec in jsonl(os.path.join(jev, "system1.jsonl")):
        for e in rec.get("injected") or []:
            if isinstance(e, dict) and isinstance(e.get("sha"), str):
                blocks.setdefault(e["sha"], e)
    joined = {"stamps": 0, "sha_ok": 0, "sections": 0}
    for row in rows:
        found = stamps.get(row.get("id")) or []
        mine = [s for s in found if s.get("session") == row.get("session")] or found
        if mine and "_sha256" in row:
            best = next((s for s in mine if s.get("sha256") == row["_sha256"]), mine[0])
            row["tool_use_id"], row["sha_ok"] = best.get("tool_use_id"), best.get("sha256") == row["_sha256"]
            joined["stamps"] += 1
            joined["sha_ok"] += row["sha_ok"]
        for sec in row.get("sections") or []:
            e = blocks.get(sec.get("sha"))
            if e:
                sec.update({k: e[k] for k in SECTION_FIELDS if k in e and k not in sec})
                joined["sections"] += 1
    return joined


# ---------------------------------------------------------------- the summary

def summary(rows, counts, joined):
    lines = [f"s1_scores: {counts['files']} transcript files, {counts['threads']} threads"]
    lines.append("by record kind (every text a hook handed the model; stamped = it carries an S1 stamp):")
    for kind in KINDS:
        k = counts["kind"].get(kind, {"injections": 0, "stamped": 0})
        lines.append(f"  {kind:<24} injections {k['injections']:>6}  stamped {k['stamped']:>6}")
    by = {}
    for row in rows:
        if row["kind"] != "score":
            by.setdefault(row["source"], []).append(row)
    lines.append("by source (compliance = scored / stamped injections a text followed; rel, use = means of scored and "
                 "late):")
    for src in sorted(set(by) | set(counts["source"])):
        rs = by.get(src, [])
        n = {s: sum(1 for x in rs if x["status"] == s) for s in ("scored", "late", "malformed", "missing", "open")}
        answerable = len(rs) - n["open"]
        rated = [x for x in rs if x["status"] in ("scored", "late")]
        total = len(rs) + counts["source"].get(src, {}).get("injections", 0)
        comp = f"{n['scored'] / answerable:.2f}" if answerable else "-"
        rel = f"{sum(x['rel'] for x in rated) / len(rated):.2f}" if rated else "-"
        use = f"{sum(x['use'] for x in rated) / len(rated):.2f}" if rated else "-"
        lines.append(f"  {src:<22} injections {total:>6}  stamped {len(rs):>5}  "
                     + "  ".join(f"{s} {v}" for s, v in n.items()) + f"  compliance {comp}  rel {rel}  use {use}")
    own = [x for x in rows if x["kind"] == "score"]
    lines.append("score rows of their own: " + "  ".join(
        f"{s} {sum(1 for x in own if x['status'] == s)}" for s in ("unknown-id", "duplicate", "malformed")))
    lines.append(f"state join: injections.jsonl {joined['stamps']} rows (sha256 equal {joined['sha_ok']}), "
                 f"system1.jsonl {joined['sections']} sections")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Pair stamped System-1 injections with the agent's S1-RATE scores.")
    ap.add_argument("paths", nargs="+", help="a main transcript, a session directory, or one .jsonl")
    ap.add_argument("--jev", default=os.path.join(ROOT, ".jev"), help="the state directory (default <repo>/.jev)")
    ap.add_argument("--out", help="write the rows (JSON lines) here; '-' for stdout")
    args = ap.parse_args(argv)
    try:
        rows, counts = read_session(args.paths)
    except FileNotFoundError as exc:
        print(f"s1_scores: no such transcript: {exc}", file=sys.stderr)
        return 2
    joined = join_state(rows, args.jev)
    text = "\n".join(json.dumps({k: v for k, v in row.items() if not k.startswith("_")}, sort_keys=True)
                     for row in rows)
    if args.out == "-":
        sys.stdout.write(text + "\n" if text else "")
    elif args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n" if text else "")
    print(summary(rows, counts, joined), file=sys.stderr if args.out == "-" else sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
