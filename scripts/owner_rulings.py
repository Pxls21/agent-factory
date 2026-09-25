#!/usr/bin/env python3
"""List the owner's rulings in the decision log that mention any of the given words (orchestration 0l; D-087, D-088).

Before a brief, an interview seed or a question to the owner ships, run it with the topic's words: a question a ruling already
answers is never asked (AF-AP-203: asked three times on 2026-09-25, the GPU window question among them, which D-081 had answered).
Rows count as the owner's when their text names OWNER (OWNER RULING, OWNER DIRECTION, OWNER CONFIRMATION, ...). Newest first.

  python3 scripts/owner_rulings.py GPU window            # rows naming the owner that mention "gpu" or "window"
  python3 scripts/owner_rulings.py --all GPU window      # rows that mention both words
  python3 scripts/owner_rulings.py --log FILE --width 400 WORD...

Exit 0 with matches, 1 with none, 2 on a usage error or an unreadable log.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROW = re.compile(r"^\| (D-\d+) \| (.*)$")


def owner_rows(text):
    """Yield (decision id, row text) for every decision-log table row that names the owner."""
    for line in text.splitlines():
        m = ROW.match(line)
        if m and re.search(r"\bOWNER\b", m.group(2)):
            yield m.group(1), m.group(2).rstrip(" |")


def matches(row, words, require_all):
    low = row.lower()
    hits = [w.lower() in low for w in words]
    return all(hits) if require_all else any(hits)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("words", nargs="+")
    ap.add_argument("--log", default=str(ROOT / "docs" / "08_DECISION_LOG.md"))
    ap.add_argument("--all", action="store_true", help="every word must appear (default: any)")
    ap.add_argument("--width", type=int, default=300, help="characters of each row to print")
    args = ap.parse_args(argv)
    try:
        text = Path(args.log).read_text(encoding="utf-8")
    except OSError as e:
        print("owner_rulings: cannot read %s: %s" % (args.log, e), file=sys.stderr)
        return 2
    found = [(d, r) for d, r in owner_rows(text) if matches(r, args.words, args.all)]
    found.sort(key=lambda x: int(x[0][2:]), reverse=True)
    for d, r in found:
        print("%s: %s%s" % (d, r[: args.width], " ..." if len(r) > args.width else ""))
    print("owner_rulings: %d owner row(s) match %s" % (len(found), " AND ".join(args.words) if args.all else " OR ".join(args.words)))
    return 0 if found else 1


if __name__ == "__main__":
    sys.exit(main())
