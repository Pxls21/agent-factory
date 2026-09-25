#!/usr/bin/env bash
# stamp.sh — the ONLY way a ledger/wiki/task timestamp is produced (AF-AP-37: pasted, never typed; the coordinator typed
# three wrong stamps on 2026-09-07/08). Prints the current UTC time in the ledger's coarse form, e.g. `2026-09-08 00:3xZ`
# (default), the bare ten-minute bucket with -b (`00:3xZ`), or the exact form with -x (`2026-09-08T00:37:12Z`). Use it
# inside edits: $(bash scripts/stamp.sh), $(bash scripts/stamp.sh -b).
# The {DATESTAMP} and {STAMP} tokens (task #268) are the default and the -b form: scripts/safe_commit.sh fills its -m
# message from one run of this script; scripts/stamp_fill.py computes the same forms in Python (anchor_edit.py uses it),
# and tests/test_stamp_fill.py holds the two equal. Each mode reads the clock ONCE: separate reads of the date, the hour
# and the minute could straddle an hour or a day boundary and print a stamp up to a day old.
case "${1:-}" in
  -x) date -u +%Y-%m-%dT%H:%M:%SZ ;;
  -b) t=$(date -u '+%H:%M'); printf '%sxZ\n' "${t%?}" ;;
  *)  t=$(date -u '+%Y-%m-%d %H:%M'); printf '%sxZ\n' "${t%?}" ;;
esac
