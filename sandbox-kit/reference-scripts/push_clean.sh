#!/usr/bin/env bash
# push_clean.sh — the sanctioned push sequence for claude/clean-build.
# Strips model-identifier trailers from the unpushed range, proves tree
# identity across the rewrite, verifies zero trailers remain, then pushes
# the rev-parsed full SHA (never HEAD, never a hand-typed ref).
#
# Refuses to run unless the caller confirms zero delegates are live
# (filter-branch rewrites refs; a live delegate mid-mutation is the known
# ship-unreviewed trap — orchestration skill (f)).
#
# Usage: scripts/push_clean.sh --no-delegates-live
set -euo pipefail

BRANCH="claude/clean-build"
[ "${1:-}" = "--no-delegates-live" ] || {
  echo "REFUSED: pass --no-delegates-live only after confirming zero delegate lanes are active." >&2
  exit 1
}

# filter-branch silently refuses on a dirty tree and the || true below
# swallows it, leaving trailers in place (bit 2026-08-31; the trailer-count
# abort caught it fail-closed but with a misleading cause). Refuse loud.
git diff --quiet && git diff --cached --quiet || {
  echo "REFUSED: dirty working tree — commit or discard (banner churn: git checkout -- AGENTS.md CLAUDE.md) before push_clean." >&2
  exit 1
}
git fetch origin "$BRANCH"
RANGE="origin/$BRANCH..HEAD"
N=$(git rev-list --count "$RANGE")
[ "$N" -gt 0 ] || { echo "Nothing to push."; exit 0; }

echo "== boundary ($N commits) =="
git log "$RANGE" --format='%h %s'

TREE_BEFORE=$(git rev-parse 'HEAD^{tree}')
git filter-branch -f \
  --msg-filter 'grep -v "Co-Authored-By: Claude\|Claude-Session:"' \
  --env-filter 'export GIT_COMMITTER_EMAIL=noreply@anthropic.com GIT_COMMITTER_NAME=Claude GIT_AUTHOR_EMAIL=noreply@anthropic.com GIT_AUTHOR_NAME=Claude' \
  "$RANGE" >/dev/null 2>&1 || true  # exit 1 when nothing needed rewriting is fine
TREE_AFTER=$(git rev-parse 'HEAD^{tree}')
[ "$TREE_BEFORE" = "$TREE_AFTER" ] || { echo "TREE MISMATCH after rewrite — ABORT, do not push." >&2; exit 2; }

LEFT=$(git log "$RANGE" --format='%B' | grep -c 'Co-Authored-By: Claude\|Claude-Session:' || true)
[ "$LEFT" = "0" ] || { echo "$LEFT trailer(s) remain — ABORT." >&2; exit 3; }

SHA=$(git rev-parse HEAD)
echo "== pushing $SHA =="
git push -u origin "$SHA:refs/heads/$BRANCH"
