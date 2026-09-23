#!/usr/bin/env python3
"""stamp_check.py: refuse a NEW ledger-plane stamp that is later than the clock.

Born 2026-09-23. Four date-prefixed ledger, incident-log and wiki stamps were typed from the
clock in the coordinator's head instead of pasted, and each was committed AHEAD of its own commit
(by 3.3 to 9.7 minutes; three bare times rode along); on 2026-09-07 the same class ran 2.8 h
ahead (docs/INCIDENT-LOG.md, AF-AP-37). The rule "a stamp is pasted from date -u or the commit
clock" was prose. This makes its future half mechanical: a stamp can still be wrong in the
past, but a stamp later than the clock at commit time is always wrong.

Scope: the STAGED copies of the ledger-plane files (LEDGER_PLANE). A stamp is date-prefixed:
YYYY-MM-DD HH:MxZ (a ten-minute bucket; its earliest instant HH:M0 is compared),
YYYY-MM-DD HH:MMZ, or YYYY-MM-DDTHH:MM:SSZ. A stamp whose exact text already occurs in HEAD's
copy of the same file is not new and is not checked (a re-edited line keeps its old stamps).
NOT checked, by design: bare times with no date (a re-edited running paragraph re-adds bare
times from earlier days, so a bare time cannot be placed on the clock), and stamps in any other
file.

Exit 0 clean; 1 a new stamp later than the clock plus the slack, or one that names no valid
instant (one stderr line each); 2 usage error (argparse).
"""
import argparse
import datetime
import re
import subprocess
import sys

LEDGER_PLANE = (
    "todo/BUILD-TASKLIST.md",
    "docs/INCIDENT-LOG.md",
    "wiki/topics/live-state.md",
    "docs/08_DECISION_LOG.md",
)
STAMP_RX = re.compile(r"(?<![0-9])(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d)([x0-9])(?::(\d{2}))?Z")
UTC = datetime.timezone.utc


def _git(*args):
    return subprocess.run(["git", *args], capture_output=True)


def _blob(spec):
    """The text at SPEC (':path' = the index, 'HEAD:path'), or '' when no such blob exists."""
    r = _git("show", spec)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else ""


def _instant(match):
    """The earliest instant a stamp names, or None when it names no valid instant."""
    year, month, day, hour, tens, unit, second = match.groups()
    if unit == "x" and second is not None:
        return None
    minute = int(tens) * 10 + (0 if unit == "x" else int(unit))
    try:
        return datetime.datetime(int(year), int(month), int(day), int(hour), minute,
                                 int(second or 0), tzinfo=UTC)
    except ValueError:
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Refuse a new ledger-plane stamp later than the clock.")
    ap.add_argument("--staged", action="store_true", required=True,
                    help="check the index copies of the ledger-plane files against HEAD")
    ap.add_argument("--now", help="the clock as YYYY-MM-DDTHH:MM:SSZ (tests); default: the system clock")
    ap.add_argument("--slack-seconds", type=int, default=120)
    args = ap.parse_args(argv)
    if args.now is None:
        now = datetime.datetime.now(UTC).replace(microsecond=0)
    else:
        try:
            now = datetime.datetime.strptime(args.now, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        except ValueError:
            ap.error(f"--now {args.now!r} is not YYYY-MM-DDTHH:MM:SSZ")
    limit = now + datetime.timedelta(seconds=args.slack_seconds)
    now_text = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    staged = _git("diff", "--cached", "--name-only", "--diff-filter=ACMR")
    if staged.returncode != 0:
        print("stamp_check: git diff --cached failed: " + staged.stderr.decode("utf-8", "replace").strip(),
              file=sys.stderr)
        return 1
    paths = [p for p in staged.stdout.decode("utf-8", "replace").splitlines() if p in LEDGER_PLANE]

    problems, checked = set(), set()
    for path in paths:
        head = _blob("HEAD:" + path)
        for match in STAMP_RX.finditer(_blob(":" + path)):
            stamp = match.group(0)
            if stamp in head:
                continue
            checked.add((path, stamp))
            instant = _instant(match)
            if instant is None:
                problems.add(f"stamp_check: {path}: '{stamp}' names no valid instant")
            elif instant > limit:
                ahead = (instant - now).total_seconds() / 60
                problems.add(f"stamp_check: {path}: '{stamp}' is {ahead:.1f} min ahead of the clock "
                             f"{now_text} — paste stamps from date -u or the commit clock")
    for line in sorted(problems):
        print(line, file=sys.stderr)
    if paths and not problems:
        print(f"stamp_check: {len(checked)} new stamp(s) in {len(paths)} ledger-plane file(s), "
              f"none ahead of the clock {now_text}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
