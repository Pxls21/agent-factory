#!/usr/bin/env python3
"""handback_extract.py — a subagent's SubagentHandback message, and its full report when the lane wrote the report as
text, taken from its transcript with the harness's control tags neutralized (task #339, D-103; brief
tasks/briefs/labeling/LS-B9-brief.md; LS-B9 round 2, item 7).

  python3 scripts/handback_extract.py --transcript PATH --out FILE [--report-out REPORT]

The transcript is streamed line by line, never read whole. json.loads runs only on a line that holds the bytes
`"assistant"`, and in an assistant record the code reads only `tool_use` blocks named SubagentHandback and `text`
blocks: it never reads a `thinking` block's text. (In the transcripts measured on 2026-09-28 each record carries one
content block; a record that carried a thinking block beside another would be decoded whole by json.loads, and the
thinking block skipped by its type.)

The LAST call's input.message is written to FILE. A lane may put its whole report in its final assistant TEXT and only
a summary in the hand-back (2026-09-28, the scrubber repair: a 63,540-character report as text, a 3,568-character
hand-back). So with --report-out, the last assistant text block of 1,000 or more characters written in the lane's
LAST ROUND, after the previous hand-back call and before the last one (with one call: before it; with no call: the
last one overall), is written to REPORT when it is longer than the hand-back message. Text written after the last call
is the lane's epilogue, not its report: in that transcript a 2,910-character text followed the call (lines 2495
report, 2496 call, 2499 epilogue), and "the last long text block" was the epilogue. Text written before the previous
call belongs to an earlier round: a resumed lane that wrote its round-1 report as text and only a short round-2
hand-back would otherwise have its round-1 text offered as this round's report (VERIFY-LS-B9 F-11).
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
import sys

NAME = "SubagentHandback"
LONG = 1000               # a text block this long or longer can be a lane's report
TAG_RE = re.compile(r"<(?=/?(?:(?:system-reminder|function_calls|invoke|parameter)(?![\w-])|antml:))", re.IGNORECASE)


def neutralize(text):
    """(text with `<` turned into `<\\` before each control tag, the number of tags neutralized)."""
    return TAG_RE.subn(lambda m: "<\\", text)


def scan(fh):
    """{message, calls, malformed, unparsable, long_text} from a binary line iterator: the last hand-back message, and
    the last assistant text block of LONG or more characters after the previous call and before the last one (with no
    call: the last one overall)."""
    out = {"message": None, "calls": 0, "malformed": 0, "unparsable": 0, "long_text": None}
    last_long = long_at_call = None
    for raw in fh:
        if b'"assistant"' not in raw:
            continue
        try:
            record = json.loads(raw)
        except ValueError:
            if b'"' + NAME.encode() + b'"' in raw:
                out["unparsable"] += 1
            continue
        if not isinstance(record, dict) or record.get("type") != "assistant":
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
                if isinstance(text, str) and len(text) >= LONG:
                    last_long = text
            elif block.get("type") == "tool_use" and block.get("name") == NAME:
                out["calls"] += 1
                given = block.get("input")
                text = given.get("message") if isinstance(given, dict) else None
                if isinstance(text, str):
                    out["message"], long_at_call = text, last_long
                    last_long = None     # this round ends here: an earlier round's text is never a later report
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


def main(argv=None):
    ap = argparse.ArgumentParser(prog="handback_extract.py", description=__doc__.splitlines()[0])
    ap.add_argument("--transcript", required=True, help="a subagent transcript (JSONL)")
    ap.add_argument("--out", required=True, help="the file the neutralized hand-back message is written to")
    ap.add_argument("--report-out", help="the file a longer text report is written to")
    a = ap.parse_args(argv)
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
