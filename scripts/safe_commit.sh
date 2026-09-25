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
# THE PUSH LOCK (AF-AP-216, 2026-09-25): scripts/push_clean.sh holds the file `git rev-parse --git-path push-in-flight`
# (its pid) for its whole run, and a commit that lands while it pushes leaves the branch unfollowed. While that pid
# runs: one line, a wait of up to SAFE_COMMIT_LOCK_WAIT seconds (default 600), then a refusal (rc 5) naming it. The wait
# comes before the stamp fill (a stamp names the commit's own moment) and before anything is staged. A lock whose pid
# does not run is stale and does not block; a commit made under push_clean itself (PUSH_IN_FLIGHT_PID = the lock's pid,
# as scripts/hooks/pre-commit reads it) does not wait for its own run.
LOCK="$(git rev-parse --path-format=absolute --git-path push-in-flight)"
MAXWAIT="${SAFE_COMMIT_LOCK_WAIT:-600}"
[[ "$MAXWAIT" =~ ^[0-9]+$ ]] || { echo "usage: SAFE_COMMIT_LOCK_WAIT takes whole seconds, not '$MAXWAIT'" >&2; exit 1; }
WAITED=""
while HOLDER="$(cat "$LOCK" 2>/dev/null)" && [ -n "$HOLDER" ] && [ "$HOLDER" != "${PUSH_IN_FLIGHT_PID:-}" ] &&
      kill -0 "$HOLDER" 2>/dev/null; do
  if [ -z "$WAITED" ]; then
    WAITED=$SECONDS
    echo "== a push is in flight (push_clean pid $HOLDER): waiting up to $MAXWAIT s for it to end =="
  fi
  if [ $((SECONDS - WAITED)) -ge "$MAXWAIT" ]; then
    echo "REFUSED: push_clean (pid $HOLDER) still holds the push lock $LOCK after $MAXWAIT s; nothing staged." >&2
    exit 5
  fi
  sleep 1
done
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
