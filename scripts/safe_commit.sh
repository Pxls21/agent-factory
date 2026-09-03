#!/usr/bin/env bash
# safe_commit.sh — coordinator commits in a SHARED tree (live delegates).
# Stages ONLY the named paths, prints the staged set, refuses if anything
# else is already staged (a live delegate's staging must never be swept).
# Incident 2026-08-28: a coordinator `git add -A` swept a live delegate's
# mid-increment files into a ruling commit (8th costume of the shared-index
# class). This script replaces raw `git add -A` for coordinator commits.
# Usage: scripts/safe_commit.sh -m "message" path [path...]
set -euo pipefail
[ "${1:-}" = "-m" ] || { echo "usage: safe_commit.sh -m <msg> path..." >&2; exit 1; }
MSG="$2"; shift 2
[ $# -gt 0 ] || { echo "REFUSED: name the paths explicitly." >&2; exit 1; }
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
