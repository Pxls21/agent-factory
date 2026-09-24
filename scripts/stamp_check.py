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
Also checked (2026-09-24, two more slips in files outside that list): in a staged Markdown file under
`tasks/`, the stamps on a MEASUREMENT line only (a line holding "MEASURED at authoring", "measured at
authoring" or starting "STATUS "): a brief's premise heading and a plan's status stamp say when something
was measured, so they can never be later than the commit. Other stamps in those files may be plans
(a window, a deadline) and stay unchecked.
NOT checked, by design: bare times with no date (a re-edited running paragraph re-adds bare
times from earlier days, so a bare time cannot be placed on the clock), and stamps in any other
file.

A BUCKET stamp (HH:MxZ) gets no slack: it already spans ten minutes, so its earliest instant must not be later than
the clock (2026-09-24: a `20:1xZ` wiki block written at 20:08:53Z passed the 120 s slack). The minute and ISO forms
keep the slack.
--message FILE (the commit-msg hook, 2026-09-24: a "retro 21:5xZ" subject was committed at 21:45Z; the staged
files were clean, the message was not): every dated stamp in the message, and every BARE stamp (HH:MxZ, HH:MMZ) on its
subject line, must not be later than the clock. A bare subject stamp is placed on the clock's date, or the day before
when that date puts it more than 12 h ahead (a batch stamped 23:5xZ and committed after midnight). Lines starting "#"
are git's comments and are skipped; a bare time in the body is not checked (it may name another day).
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
MEASURED_RX = re.compile(r"(?i)measured at authoring|^STATUS ")
STAMP_RX = re.compile(r"(?<![0-9])(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d)([x0-9])(?::(\d{2}))?Z")
BARE_RX = re.compile(r"(?<!\d{4}-\d{2}-\d{2}[ T])(?<![0-9:.T-])(\d{2}):(\d)([x0-9])Z(?![0-9A-Za-z])")
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


def check_message(path, now, limit, now_text):
    """-> the problems of the commit message at PATH (see --message in the module docstring)."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = [line for line in fh.read().splitlines() if not line.startswith("#")]
    subject = next((line for line in lines if line.strip()), "")
    problems = []
    for match in STAMP_RX.finditer("\n".join(lines)):
        instant = _instant(match)
        if instant is None:
            problems.append(f"stamp_check: the commit message: '{match.group(0)}' names no valid instant")
        elif instant > (now if match.group(6) == "x" else limit):
            problems.append(f"stamp_check: the commit message: '{match.group(0)}' is "
                            f"{(instant - now).total_seconds() / 60:.1f} min ahead of the clock {now_text}")
    for match in BARE_RX.finditer(subject):
        hour, tens, unit = match.groups()
        minute = int(tens) * 10 + (0 if unit == "x" else int(unit))
        if int(hour) > 23 or minute > 59:
            problems.append(f"stamp_check: the commit subject: '{match.group(0)}' names no valid time")
            continue
        instant = now.replace(hour=int(hour), minute=minute, second=0)
        if instant - now > datetime.timedelta(hours=12):
            instant -= datetime.timedelta(days=1)
        if instant > (now if unit == "x" else limit):
            problems.append(f"stamp_check: the commit subject: '{match.group(0)}' is "
                            f"{(instant - now).total_seconds() / 60:.1f} min ahead of the clock {now_text} — "
                            f"paste stamps from date -u")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description="Refuse a new ledger-plane stamp later than the clock.")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--staged", action="store_true",
                      help="check the index copies of the ledger-plane files against HEAD")
    mode.add_argument("--message", metavar="FILE", help="check a commit message (the commit-msg hook)")
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
    if args.message is not None:
        try:
            problems = check_message(args.message, now, limit, now_text)
        except OSError as exc:
            print(f"stamp_check: cannot read the commit message: {exc}", file=sys.stderr)
            return 1
        for line in problems:
            print(line, file=sys.stderr)
        return 1 if problems else 0

    staged = _git("diff", "--cached", "--name-only", "--diff-filter=ACMR")
    if staged.returncode != 0:
        print("stamp_check: git diff --cached failed: " + staged.stderr.decode("utf-8", "replace").strip(),
              file=sys.stderr)
        return 1
    names = staged.stdout.decode("utf-8", "replace").splitlines()
    paths = [p for p in names if p in LEDGER_PLANE]
    measured = [p for p in names if p.startswith("tasks/") and p.endswith(".md") and p not in LEDGER_PLANE]

    def _texts(path):
        text = _blob(":" + path)
        if path in LEDGER_PLANE:
            return text
        return "\n".join(line for line in text.splitlines() if MEASURED_RX.search(line))

    problems, checked = set(), set()
    for path in paths + measured:
        head = _blob("HEAD:" + path)
        for match in STAMP_RX.finditer(_texts(path)):
            stamp = match.group(0)
            if stamp in head:
                continue
            checked.add((path, stamp))
            instant = _instant(match)
            if instant is None:
                problems.add(f"stamp_check: {path}: '{stamp}' names no valid instant")
            elif instant > (now if match.group(6) == "x" else limit):   # a bucket gets no slack
                ahead = (instant - now).total_seconds() / 60
                problems.add(f"stamp_check: {path}: '{stamp}' is {ahead:.1f} min ahead of the clock "
                             f"{now_text} — paste stamps from date -u or the commit clock")
    for line in sorted(problems):
        print(line, file=sys.stderr)
    if paths and not problems:
        n_plane = sum(1 for path, _ in checked if path in LEDGER_PLANE)
        print(f"stamp_check: {n_plane} new stamp(s) in {len(paths)} ledger-plane file(s), "
              f"none ahead of the clock {now_text}", file=sys.stderr)
    n_meas = sum(1 for path, _ in checked if path not in LEDGER_PLANE)
    if n_meas and not problems:
        print(f"stamp_check: {n_meas} new measurement stamp(s) in {len(measured)} tasks/ file(s), "
              f"none ahead of the clock {now_text}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
