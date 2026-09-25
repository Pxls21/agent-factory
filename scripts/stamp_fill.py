#!/usr/bin/env python3
"""stamp_fill.py — fill the {STAMP} and {DATESTAMP} tokens from the clock, in place (task #268).

Six stamps were typed ahead of the clock on 2026-09-25 (commit messages, a brief written with the Write tool, ledger
text); the future-stamp gate (scripts/stamp_check.py) blocked each committed one and each cost a fix cycle. The rule
"a stamp is substituted, never typed" was prose, and the Write tool cannot substitute. Type the TOKEN instead; the
tools fill it from the clock at the moment of the write or the commit:

    {STAMP}      the bare ten-minute bucket, e.g. 11:2xZ               (what `bash scripts/stamp.sh -b` prints)
    {DATESTAMP}  the dated ten-minute bucket, e.g. 2026-09-25 11:2xZ   (what `bash scripts/stamp.sh` prints)

    stamp_fill.py FILE...

fills both tokens in each FILE in place (a brief written with the Write tool) and prints one line per file with its
count; a file with no token is never written. Run it by hand before the commit: nothing calls it automatically.
scripts/safe_commit.sh fills the tokens in its -m message, and scripts/anchor_edit.py in its NEW and TEXT values
(through fill() below, the one Python computation; tests/test_stamp_fill.py holds it equal to scripts/stamp.sh).
One clock read serves every token of one run. Every FILE is read and decoded (UTF-8) before any is written: one that
cannot be refuses the run with rc 2 and nothing written. rc 64: no FILE. The bytes around a token are kept as they are
(line endings included). Declared limits: a write that fails part-way (a full disk) can leave the earlier files filled;
a literal token cannot be written through this tool (it is always filled).
"""
import datetime
import sys

UTC = datetime.timezone.utc
TOKENS = ("{STAMP}", "{DATESTAMP}")


def clock():
    """The one read of the clock a run's tokens share."""
    return datetime.datetime.now(UTC)


def stamps(now):
    """('HH:MxZ', 'YYYY-MM-DD HH:MxZ') for NOW, an aware datetime, in UTC."""
    dated = now.astimezone(UTC).strftime("%Y-%m-%d %H:%M")[:-1] + "xZ"
    return dated[11:], dated


def fill(text, now):
    """(TEXT with every {STAMP} and {DATESTAMP} filled from NOW, the number of tokens filled)."""
    count = sum(text.count(token) for token in TOKENS)
    if not count:
        return text, 0
    bare, dated = stamps(now)
    return text.replace("{DATESTAMP}", dated).replace("{STAMP}", bare), count


def main(argv):
    paths = argv[1:]
    if not paths or any(path.startswith("-") for path in paths):
        print(__doc__, file=sys.stderr)
        return 64
    now = clock()
    planned = []
    for path in paths:                          # every file read and decoded before any is written
        try:
            with open(path, "rb") as fh:
                text = fh.read().decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print("stamp_fill: REFUSED, nothing written — %s: %s" % (path, exc), file=sys.stderr)
            return 2
        planned.append((path, *fill(text, now)))
    dated = stamps(now)[1]
    for path, text, count in planned:
        if not count:
            print("stamp_fill: 0 token(s) in %s, untouched" % path)
            continue
        with open(path, "wb") as fh:
            fh.write(text.encode("utf-8"))
        print("stamp_fill: %d token(s) filled in %s (%s)" % (count, path, dated))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
