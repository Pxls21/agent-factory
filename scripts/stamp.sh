#!/usr/bin/env bash
# stamp.sh — the ONLY way a ledger/wiki/task timestamp is produced (AF-AP-37: pasted, never typed; the coordinator typed
# three wrong stamps on 2026-09-07/08). Prints the current UTC time in the ledger's coarse form, e.g. `2026-09-08 00:3xZ`
# (default) or the exact form with -x (`2026-09-08T00:37:12Z`). Use it inside edits: $(bash scripts/stamp.sh).
case "${1:-}" in
  -x) date -u +%Y-%m-%dT%H:%M:%SZ ;;
  *)  d=$(date -u +%Y-%m-%d); h=$(date -u +%H); m=$(date -u +%M); printf '%s %s:%sxZ\n' "$d" "$h" "${m:0:1}" ;;
esac
