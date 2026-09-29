#!/usr/bin/env python3
"""handback_extract.py — a subagent's SubagentHandback message, and its full report when the lane wrote the report as
text, taken from its transcript with the harness's control tags neutralized (task #339, D-103; brief
tasks/briefs/labeling/LS-B9-brief.md; LS-B9 round 2, item 7).

  python3 scripts/handback_extract.py --transcript PATH --out FILE [--report-out REPORT]
  python3 scripts/handback_extract.py --local-ids FILE...

The transcript is streamed line by line, never read whole. json.loads runs only on a line that holds the bytes
`"assistant"`, or, between a hand-back call and the next message to the lane, the bytes `"user"`; in an assistant
record the code reads only `tool_use` blocks named SubagentHandback and `text` blocks: it never reads a `thinking`
block's text. (In the transcripts measured on 2026-09-28 each record carries one content block; a record that carried
a thinking block beside another would be decoded whole by json.loads, and the thinking block skipped by its type.)

The LAST call's input.message is written to FILE. A lane may put its whole report in its final assistant TEXT and only
a summary in the hand-back (2026-09-28, the scrubber repair: a 63,540-character report as text, a 3,568-character
hand-back). So with --report-out, the last assistant text block of 1,000 or more characters written in the lane's
LAST ROUND is written to REPORT when it is longer than the hand-back message. The last round runs from the resume
message after the previous hand-back call to the last call (with one call: from the start to it; with no call: the
last long text block overall). Text written after the last call is the lane's epilogue, not its report: in that
transcript a 2,910-character text followed the call (lines 2495 report, 2496 call, 2499 epilogue), and "the last long
text block" was the epilogue. Text written before the previous call belongs to an earlier round (VERIFY-LS-B9 F-11),
and so does the previous round's epilogue, written after its call and before the resume: in the LS-B9 lane's
transcript round 2's 3,995-character epilogue (line 1866) lay between its call (1863) and round 3's resume (1867), and
a short round-3 hand-back would have been paired with it (VERIFY-LS-B9 R3-F3). The resume message is the first user
record after the previous call that carries text: never the call's own tool result (the user record right after every
call; in 23,522 tool-result records measured on 2026-09-29 none also carried text), and never a compaction summary
(`isCompactSummary`; the LS-B9 lane compacted after its round-3 call and wrote a 1,262-character text before round
4's resume).

--local-ids FILE...: each commit id cited in the files that `git log origin/<branch>..HEAD` shows as local (the
current branch; the tokens and the prefix rule are scripts/stale_ids.py's). push_clean.sh rewrites that range, so such
an id points at nothing on origin, and stale_ids.py refuses the push of a committed text that cites it (T1-LCM-AUDIT's
report cited two on 2026-09-29, caught by hand). It prints a summary line, then one line per citation: the file, the
line number, the id, the local commit it names and its subject, the line's text. exit: 0 none cited · 1 some cited ·
2 not checked (HEAD detached, no origin/<branch>, git failed, an unreadable file), with the reason on stdout.
Both files are UTF-8, with `<` written `<\\` in front of these tags, opening or closing: system-reminder,
function_calls, invoke, parameter, and every antml: tag, so a reader of either file meets no text a harness could
take for its own tag.

stdout is one line, the path of the longer of FILE and REPORT (the file to lint), and only when the hand-back is found:
the stack chains it, so with no hand-back the lint step is skipped. The status goes to stderr, never the message:
  handback: found calls=N chars=C bytes=B neutralized=K sha256=<the first 12 hex of FILE's sha256> out=FILE
  handback: absent calls=N
  report: saved chars=C bytes=B neutralized=K sha256=<12 hex> out=REPORT (the longer: C characters against the
          hand-back's H)   |   report: none longer than the hand-back (...)   |   report: none (...)
(`malformed=M` is added when M calls carry no string message, `unparsable=U` when U candidate lines are not JSON.)

exit: 0 hand-back found; 1 absent (FILE is not written; REPORT may be); 2 usage, an unreadable transcript or an
unwritable file.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys

NAME = "SubagentHandback"
LONG = 1000               # a text block this long or longer can be a lane's report
TAG_RE = re.compile(r"<(?=/?(?:(?:system-reminder|function_calls|invoke|parameter)(?![\w-])|antml:))", re.IGNORECASE)


def neutralize(text):
    """(text with `<` turned into `<\\` before each control tag, the number of tags neutralized)."""
    return TAG_RE.subn(lambda m: "<\\", text)


def opens_round(record):
    """True for a message to the lane (the resume): a user record that carries text, never a tool result and never a
    compaction summary."""
    if record.get("isCompactSummary"):
        return False
    body = record.get("message")
    content = body.get("content") if isinstance(body, dict) else None
    if isinstance(content, str):
        return bool(content.strip())
    kinds = [b.get("type") for b in content if isinstance(b, dict)] if isinstance(content, list) else []
    return "text" in kinds and "tool_result" not in kinds


def scan(fh):
    """{message, calls, malformed, unparsable, long_text} from a binary line iterator: the last hand-back message, and
    the last assistant text block of LONG or more characters in the last round, from the resume message after the
    previous call to the last call (with one call: before it; with no call: the last one overall)."""
    out = {"message": None, "calls": 0, "malformed": 0, "unparsable": 0, "long_text": None}
    last_long = long_at_call = None
    in_round = True          # False from a hand-back call to the next message to the lane (the resume)
    for raw in fh:
        wants_user = not in_round and b'"user"' in raw
        if not wants_user and b'"assistant"' not in raw:
            continue
        try:
            record = json.loads(raw)
        except ValueError:
            if b'"' + NAME.encode() + b'"' in raw:
                out["unparsable"] += 1
            continue
        if not isinstance(record, dict):
            continue
        if record.get("type") == "user":
            if not in_round and opens_round(record):
                in_round = True
            continue
        if record.get("type") != "assistant":
            continue
        body = record.get("message")
        content = body.get("content") if isinstance(body, dict) else None
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text":
                text = block.get("text")
                if in_round and isinstance(text, str) and len(text) >= LONG:
                    last_long = text
            elif block.get("type") == "tool_use" and block.get("name") == NAME:
                out["calls"] += 1
                given = block.get("input")
                text = given.get("message") if isinstance(given, dict) else None
                if isinstance(text, str):
                    out["message"], long_at_call = text, last_long
                    last_long = None     # this round ends here: an earlier round's text is never a later report,
                    in_round = False     # nor is its epilogue, written before the next resume message (R3-F3)
                else:
                    out["malformed"] += 1
    out["long_text"] = long_at_call if out["message"] is not None else last_long
    return out


def write(path, text):
    """(chars, bytes, neutralized, sha256) of the neutralized text written to path; OSError propagates."""
    clean, count = neutralize(text)
    data = clean.encode("utf-8", errors="replace")
    with open(path, "wb") as fh:
        fh.write(data)
    return len(text), len(data), count, hashlib.sha256(data).hexdigest()[:12]


def git_out(*args):
    """git's stdout, or raises OSError with git's first stderr line."""
    try:
        r = subprocess.run(["git", *args], capture_output=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise OSError("git %s: %s" % (args[0], e))
    if r.returncode != 0:
        why = r.stderr.decode("utf-8", "replace").strip().splitlines()
        raise OSError("git %s failed: %s" % (" ".join(args), why[0] if why else "exit %d" % r.returncode))
    return r.stdout.decode("utf-8", "surrogateescape")


def local_ids(paths):
    """Mode --local-ids: print each commit id the files cite that `git log origin/<branch>..HEAD` shows as local.
    exit 0 none, 1 some, 2 not checked."""
    try:
        import stale_ids         # the tokens and prefix rule of the check this one predicts (sys.path[0] = scripts/)
        try:
            branch = git_out("symbolic-ref", "--short", "-q", "HEAD").strip()
        except OSError:
            raise OSError("HEAD is detached: there is no origin/<branch>..HEAD")
        rng = "origin/%s..HEAD" % branch
        log = git_out("log", "--format=%H%x00%s", rng, "--")
        subject = dict(ln.split("\0", 1) for ln in log.splitlines() if "\0" in ln)
        hits = []
        for path in dict.fromkeys(paths):    # a path given twice is read once
            with open(path, encoding="utf-8", errors="replace") as fh:
                for num, line in enumerate(fh, 1):
                    found = stale_ids.stale_in(line, subject)
                    hits += [(path, num, tok, full, line.rstrip("\n")) for tok, full in found]
    except (ImportError, OSError) as e:
        print("local ids: not checked — %s" % e)
        return 2
    held = "%s holds %d local commit%s" % (rng, len(subject), "" if len(subject) == 1 else "s")
    if not hits:
        print("local ids: none cited (%s)" % held)
        return 0
    print("local ids: %d cited — %s; push_clean.sh rewrites them, so cite each by its subject (or by its origin id "
          "after the push)" % (len(hits), held))
    for path, num, tok, full, text in hits:
        print("%s:%d: %s is local %s \"%s\" · %s" % (path, num, tok, full[:12], subject[full],
                                                   text if len(text) <= 200 else text[:200] + "…"))
    return 1


def main(argv=None):
    ap = argparse.ArgumentParser(prog="handback_extract.py", description=__doc__.splitlines()[0])
    ap.add_argument("--transcript", help="a subagent transcript (JSONL)")
    ap.add_argument("--out", help="the file the neutralized hand-back message is written to")
    ap.add_argument("--report-out", help="the file a longer text report is written to")
    ap.add_argument("--local-ids", nargs="+", metavar="FILE", help="list the local commit ids these files cite")
    a = ap.parse_args(argv)
    if a.local_ids is not None:
        if a.transcript or a.out or a.report_out:
            ap.error("--local-ids takes no --transcript, --out or --report-out")
        return local_ids(a.local_ids)
    if not (a.transcript and a.out):
        ap.error("--transcript and --out are required (or --local-ids FILE...)")
    try:
        with open(a.transcript, "rb") as fh:
            got = scan(fh)
    except OSError as e:
        sys.stderr.write("handback_extract: cannot read the transcript %s: %s\n" % (a.transcript, e.strerror or e))
        return 2
    extra = "".join(" %s=%d" % (k, got[k]) for k in ("malformed", "unparsable") if got[k])
    message, long_text = got["message"], got["long_text"]
    try:
        target = None
        if message is None:
            sys.stderr.write("handback: absent calls=%d%s\n" % (got["calls"], extra))
        else:
            c, b, k, sha = write(a.out, message)
            target = a.out
            sys.stderr.write("handback: found calls=%d chars=%d bytes=%d neutralized=%d sha256=%s out=%s%s\n"
                             % (got["calls"], c, b, k, sha, a.out, extra))
        if a.report_out:
            hb_chars = len(message) if message is not None else 0
            if long_text is None:
                sys.stderr.write("report: none (no assistant text block of %d or more characters in the last round)\n"
                                 % LONG)
            elif len(long_text) <= hb_chars:
                sys.stderr.write("report: none longer than the hand-back (the last long text block: %d characters, "
                                 "the hand-back: %d)\n" % (len(long_text), hb_chars))
            else:
                c, b, k, sha = write(a.report_out, long_text)
                sys.stderr.write("report: saved chars=%d bytes=%d neutralized=%d sha256=%s out=%s (the longer: %d "
                                 "characters against the hand-back's %d)\n" % (c, b, k, sha, a.report_out, c, hb_chars))
                if message is not None:
                    target = a.report_out
    except OSError as e:
        sys.stderr.write("handback_extract: cannot write: %s\n" % e)
        return 2
    if target is None:
        return 1
    print(target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
