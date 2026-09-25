#!/usr/bin/env bash
# safe_commit.sh — coordinator commits in a SHARED tree (live delegates).
# Stages ONLY the named paths, prints the staged set, refuses if anything
# else is already staged (a live delegate's staging must never be swept).
# Incident 2026-08-28: a coordinator `git add -A` swept a live delegate's
# mid-increment files into a ruling commit (8th costume of the shared-index
# class). This script replaces raw `git add -A` for coordinator commits.
# Usage: scripts/safe_commit.sh -m "message" path [path...]
# Stamp tokens (task #268; six stamps typed ahead of the clock on 2026-09-25): {STAMP} and {DATESTAMP} in the MESSAGE
# are filled from the clock at the commit, with the bare and the dated ten-minute bucket (11:2xZ, 2026-09-25 11:2xZ),
# both from ONE run of scripts/stamp.sh. File content is never filled. The commit-msg hook's future-stamp gate still
# reads the filled message, so a stamp typed ahead of the clock is still refused.
set -euo pipefail
[ "${1:-}" = "-m" ] || { echo "usage: safe_commit.sh -m <msg> path..." >&2; exit 1; }
MSG="$2"; shift 2
[ $# -gt 0 ] || { echo "REFUSED: name the paths explicitly." >&2; exit 1; }
case "$MSG" in
  *"{STAMP}"*|*"{DATESTAMP}"*)   # filled before anything is staged: a refusal here leaves the index as it was
    DS=$(bash "$(dirname "$0")/stamp.sh") || DS=""
    RX='^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]xZ$'
    [[ "$DS" =~ $RX ]] || { echo "REFUSED: scripts/stamp.sh gave '$DS', not a YYYY-MM-DD HH:MxZ stamp; nothing staged." >&2; exit 1; }
    MSG=${MSG//"{DATESTAMP}"/"$DS"}
    MSG=${MSG//"{STAMP}"/"${DS#* }"}
    echo "== stamp tokens filled from the clock: $DS =="
    ;;
esac
PRE=$(git diff --cached --name-only)
if [ -n "$PRE" ]; then
  echo "REFUSED: index already carries staged entries (a delegate's?):" >&2
  echo "$PRE" >&2
  exit 2
fi
git add -- "$@"
echo "== staged set =="
git diff --cached --stat
git commit -m "$MSG"
