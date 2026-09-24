#!/usr/bin/env bash
# push_clean.sh — the sanctioned push sequence (branch = PUSH_BRANCH or the current branch).
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

BRANCH="${PUSH_BRANCH:-$(git rev-parse --abbrev-ref HEAD)}"
# --lanes-live (2026-09-06): sandbox build lanes edit the SHARED tree for hours, so a clean-tree push never comes.
# The reviewed commits never contain their files (safe_commit stages named paths only); what blocks the push is
# filter-branch refusing a dirty worktree. In this mode the dirty set must be EXACTLY a subset of the paths declared
# in .lanes-live (one path per line — the live lanes' files, written at dispatch), the rewrite + push run in a
# throwaway DETACHED worktree of HEAD (clean by construction; the branch ref moves, the shared tree does not), and
# the transcript sync is skipped (it commits from the worktree). Any other dirty path → refuse.
MODE="${1:-}"
if [ "$MODE" = "--lanes-live" ]; then
  [ -f .lanes-live ] || { echo "REFUSED: --lanes-live needs a .lanes-live file listing the live lanes' paths." >&2; exit 1; }
  DIRTY=$(git status --porcelain --untracked-files=no | awk '{print $2}' | sort -u)
  ALLOWED=$(grep -v "^#" .lanes-live | sed "/^$/d" | sort -u)
  EXTRA=$(comm -23 <(echo "$DIRTY") <(echo "$ALLOWED"))
  [ -z "$EXTRA" ] || { echo "REFUSED: dirty paths outside the declared live lanes: $EXTRA" >&2; exit 1; }
  [ -n "$DIRTY" ] || { echo "tree is clean — use --no-delegates-live"; exit 1; }
  WT="$(mktemp -d /tmp/push-clean-wt.XXXXXX)"
  git worktree add -q --detach "$WT" HEAD || { echo "REFUSED: worktree add failed" >&2; exit 1; }
  echo "== --lanes-live: dirty set is exactly the declared lane files; rewriting/pushing from a detached worktree =="
  # The inner run is the worktree's own COMMITTED push_clean.sh, and so HEAD's ci_gate.py, never this working copy: a
  # lane may hold either script dirty (VERIFY-CI-GATE F20). `|| rc=$?` keeps errexit from skipping the cleanup below
  # when the inner run fails (F2: each refusal leaked the worktree).
  rc=0
  ( cd "$WT" && TRANSCRIPT_SYNC=0 PUSH_BRANCH="$BRANCH" bash "$WT/scripts/push_clean.sh" --no-delegates-live ) || rc=$?
  git worktree remove --force "$WT" 2>/dev/null; git worktree prune
  if [ $rc -eq 0 ]; then
    # The rewrite ran in the worktree: origin now carries the stripped SHAs while this branch ref still names the
    # pre-rewrite commits (same tree — bit 2026-09-06: local 152d023 vs origin 220ffde). Follow origin ONLY when the
    # trees are identical; never move the ref otherwise.
    LT=$(git rev-parse "refs/heads/$BRANCH^{tree}"); OT=$(git rev-parse "refs/remotes/origin/$BRANCH^{tree}")
    if [ "$LT" = "$OT" ]; then
      git update-ref "refs/heads/$BRANCH" "$(git rev-parse "refs/remotes/origin/$BRANCH")"
      echo "== branch ref followed origin to $(git rev-parse --short "refs/heads/$BRANCH") (identical tree; lane edits untouched) =="
    else
      echo "WARNING: origin/$BRANCH tree differs from the branch tree after the push — ref NOT moved; reconcile by hand." >&2
    fi
  fi
  exit $rc
fi
[ "$MODE" = "--no-delegates-live" ] || {
  echo "REFUSED: pass --no-delegates-live only after confirming zero delegate lanes are active (or --lanes-live with .lanes-live)." >&2
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
# The range and the gate read the FULL remote-tracking ref: a local branch named origin/<branch> would shadow the short
# name (VERIFY-CI-GATE F1). A fetch refspec that does not map the branch there updates FETCH_HEAD only and leaves that
# ref stale, and the gate would read an older head's verdict: refuse.
ORIGIN_REF="refs/remotes/origin/$BRANCH"
FETCHED=$(git rev-parse --verify --quiet FETCH_HEAD || true)
if [ -z "$FETCHED" ] || [ "$(git rev-parse --verify --quiet "$ORIGIN_REF" || true)" != "$FETCHED" ]; then
  echo "REFUSED: $ORIGIN_REF is not the commit 'git fetch origin $BRANCH' just fetched (FETCH_HEAD $FETCHED):" \
       "the fetch refspec (remote.origin.fetch) does not map the branch there. Restore the default:" \
       "git config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'" >&2
  exit 2
fi
RANGE="$ORIGIN_REF..HEAD"
N=$(git rev-list --count "$RANGE")
[ "$N" -gt 0 ] || { echo "Nothing to push."; exit 0; }

# CI GATE (AF-AP-126; owner 2026-09-23: "my email is littered … the third time"): every push onto a red head mails
# the owner a failure notice, and "read the run before the next push" was forgotten twice. The gate enforces that rule:
# it reads the newest stage0-ci run in origin's history and allows only a run that passed (or a push that names the
# red run it fixes: CI_FIX=<run id>). It exits 1 on a red verdict; 75 while the verdict is unknown (the run is still
# going, or pushes after it have no run registered yet: wait with `ci_gate.py --wait`, or push anyway with
# CI_WAIT_SKIP=<reason>); 2 when it cannot decide (CI_GATE_OFFLINE=<reason> rescues only the Actions API's data, never
# a local git failure); 64 on a usage error. The code passes through. CI_GATE_RUNS_JSON is a test input: the gate
# refuses it (64) when origin is a github.com remote.
python3 "$(dirname "$0")/ci_gate.py" --branch "$BRANCH" --origin-ref "$ORIGIN_REF" \
  ${CI_GATE_RUNS_JSON:+--runs-json "$CI_GATE_RUNS_JSON"} || exit $?

echo "== boundary ($N commits) =="
git log "$RANGE" --format='%h %s'

# Only commits that CARRY a model-identifier trailer are rewritten (message + identity); every other commit in the
# range keeps its object id — a foreign commit (the owner's, a signed one, a tag target) must survive the push byte for
# byte (2026-09-08: the unconditional identity filter rewrote the owner's signed-key commit 80422cb into e719da8 and
# orphaned the tag `accepted/S0-11`, AF-AP-69).
OLD_IDS=$(mktemp /tmp/push-clean-ids.XXXXXX)   # the range's ids before the rewrite, oldest first (stale_ids.py)
trap 'rm -f "$OLD_IDS"' EXIT                   # every exit path, the aborts below included (VERIFY-T243-245 A-F5)
git rev-list --reverse "$RANGE" > "$OLD_IDS"
HEAD_BEFORE=$(git rev-parse --verify 'HEAD^{commit}')   # a stale-id refusal puts the branch back here (A-F1)
TREE_BEFORE=$(git rev-parse 'HEAD^{tree}')
git filter-branch -f \
  --msg-filter 'grep -v "Co-Authored-By: Claude\|Claude-Session:"' \
  --env-filter 'if git log -1 --format=%B "$GIT_COMMIT" | grep -q "Co-Authored-By: Claude\|Claude-Session:"; then export GIT_COMMITTER_EMAIL=noreply@anthropic.com GIT_COMMITTER_NAME=Claude GIT_AUTHOR_EMAIL=noreply@anthropic.com GIT_AUTHOR_NAME=Claude; fi' \
  "$RANGE" >/dev/null 2>&1 || true  # exit 1 when nothing needed rewriting is fine
TREE_AFTER=$(git rev-parse 'HEAD^{tree}')
[ "$TREE_BEFORE" = "$TREE_AFTER" ] || { echo "TREE MISMATCH after rewrite — ABORT, do not push." >&2; exit 2; }

LEFT=$(git log "$RANGE" --format='%B' | grep -c 'Co-Authored-By: Claude\|Claude-Session:' || true)
[ "$LEFT" = "0" ] || { echo "$LEFT trailer(s) remain — ABORT." >&2; exit 3; }

# STALE-ID CHECK (task #243; 2026-09-24: the ledger, the wiki and the incident log cited four commits by their LOCAL
# ids, and the rewrite above replaced each): an added line of the range that cites a commit this rewrite replaced
# would point at nothing on origin. Refuse (4), naming the old and the new id; a commit message that cites one is a
# warning only. STALE_ID_OK=<reason> pushes anyway.
src=0
python3 "$(dirname "$0")/stale_ids.py" --old "$OLD_IDS" --origin-ref "$ORIGIN_REF" || src=$?
if [ "$src" != 0 ]; then
  if [ "$src" = 4 ] && [ -n "${STALE_ID_OK:-}" ]; then
    echo "stale_ids: pushing anyway (STALE_ID_OK=$STALE_ID_OK)" >&2
  else
    # Put the branch back on its pre-rewrite commits (the tree is the same, proven above): left rewritten, the next
    # run's rewrite would be a no-op, stale_ids would see nothing rewritten, and the stale note would push (A-F1).
    git update-ref HEAD "$HEAD_BEFORE"
    echo "REFUSED by stale_ids (rc $src): NOT pushed; the branch is back on its pre-rewrite commits. Cite each commit by its subject or by the new id named above (the next run gives the same ids), commit, and run push_clean again." >&2
    exit 4
  fi
fi

SHA=$(git rev-parse HEAD)
echo "== pushing $SHA =="
git push -u origin "$SHA:refs/heads/$BRANCH"

# TRANSCRIPT SYNC (owner ask 2026-09-03): after every successful push, refresh the scrubbed daily
# chat digests under transcripts/sandbox/ and push them as their own ledger-plane commit (no
# trailers, exempt from the wiki-stale marker). Never blocks the push above; a failed export is
# reported and skipped. Set TRANSCRIPT_SYNC=0 to skip (e.g. while a gate of record is running).
if [ "${TRANSCRIPT_SYNC:-1}" = "1" ] && [ -f scripts/transcript_export.py ]; then
  if python3 scripts/transcript_export.py --out transcripts/sandbox >/dev/null 2>&1 \
     && [ -n "$(git status --porcelain -- transcripts/sandbox)" ]; then
    git add -- transcripts/sandbox \
      && git commit -q -m "transcripts: scrubbed sandbox chat digests ($(date -u +%F))" -- transcripts/sandbox \
      && git push -q origin "$(git rev-parse HEAD):refs/heads/$BRANCH" \
      && echo "== transcripts synced: $(git rev-parse --short HEAD) ==" \
      || echo "transcript sync: commit/push failed — code push above already succeeded" >&2
  else
    echo "transcript sync: nothing new (or export unavailable)"
  fi
fi
