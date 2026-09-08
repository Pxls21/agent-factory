#!/usr/bin/env bash
# pc_suite.sh — run the test suite on the owner's PC (12 cores, pytest-xdist) instead of the 4-core sandbox.
# Compute-placement ruling 2026-09-03: heavy jobs run on the PC. The sandbox stays the editing venue; the
# PC runs the gate on EXACTLY the sandbox's bytes: HEAD (which must exist on the PC clone, i.e. be pushed)
# plus the working tree as ONE binary patch (tracked edits + untracked files, .gitignore honoured), applied
# in a detached git worktree under the PC clone. Never touches the PC clone's checked-out branch.
#
#   scripts/pc_suite.sh launch [-n <workers>] [-- <pytest paths/args>]  → prints RUN_ID (default set: tests/ proofs/ spikes/); PC_SUITE_BASE=<pushed sha> when HEAD is unpushed
#   scripts/pc_suite.sh wait <RUN_ID> [max-minutes]                      → polls with SHORT bridge probes; prints the pasted
#                                                                           summary line + FAILED lines; exit = pytest's rc
#   scripts/pc_suite.sh log <RUN_ID> [tail-bytes]                         → the log's tail (bridge replies cap ~45 KB, AF-AP-15)
#
# Bridge rules obeyed (PC-BRIDGE.md, scripts/pc_lane.sh): every call < 120 s; long waits poll LOCALLY; the
# PC-side run is setsid + </dev/null + redirected and REPLAY-IDEMPOTENT (a timed-out curl may still have run:
# the launch refuses when the run dir already has a pid); uploads travel in numbered parts, each written with
# `>` so a retried call overwrites and never appends; the assembled patch is sha256-verified on the PC.
# bash reads a script LAZILY: an edit to this file while an instance runs corrupts that run at a byte offset (2026-09-08: the D5l
# poller died with "syntax error near ')'" at line 123 after the FAILED-handling edit landed mid-poll, and exited 0 without
# bringing the report home). Run from a private copy of these bytes; the file on disk may change underneath a live run.
if [ -z "${PC_SUITE_SELF_COPY:-}" ]; then
  _self="$(mktemp "${TMPDIR:-/tmp}/pc_suite.sh.XXXXXX")" && cp "$0" "$_self" && PC_SUITE_SELF_COPY="$_self" PC_SUITE_ORIG="$0" exec bash "$_self" "$@"
fi
trap 'rm -f "$PC_SUITE_SELF_COPY"' EXIT
set -uo pipefail
ROOT="$(cd "$(dirname "${PC_SUITE_ORIG:-${BASH_SOURCE[0]}}")/.." && pwd)"
PC="$ROOT/scripts/pc.sh"
PC_AF_REPO="${PC_AF_REPO:-/home/rocco/agent-factory}"
# The project venv on the PC (harness-ports/bin/pc-setup.sh installs the pinned deps there); /usr/bin/python3 lacks
# rfc3339-validator, so scripts/validate-ledger fails closed under it (39 venue reds on the first PC run, 2026-09-06).
PC_PY="${PC_PY:-/home/rocco/venv-agent-factory/bin/python}"
# The declared S0-01 real-leg corpus on the PC (scripts/realleg_sync.sh pc-build; byte-identical to the sandbox copy by
# sha256) — exported to every PC run so the checker's real-leg tests FAIL loud when it is absent, never skip (VERIFY-CK10 F-R10-25).
PC_REAL_LEG_DIR="${PC_REAL_LEG_DIR:-/home/rocco/s0-01-pinned/realleg/golden}"
die() { echo "pc_suite: $*" >&2; exit 2; }
bridge() { "$PC" "$1"; }

cmd="${1:-}"; shift || true
case "$cmd" in
launch)
  WORKERS=8
  while [ $# -gt 0 ]; do case "$1" in -n) WORKERS="$2"; shift 2;; --) shift; break;; *) die "unknown arg $1";; esac; done
  SET="${*:-tests/ proofs/ spikes/}"
  cd "$ROOT" || die "no repo"
  # PC_SUITE_BASE=<sha>: diff against a commit the PC already has (e.g. the last pushed head) when HEAD is a local,
  # unpushed commit — the patch then carries the unpushed commits AND the working tree (lane A5e hit this 2026-09-06).
  BASE=$(git rev-parse "${PC_SUITE_BASE:-HEAD}") || die "no such base: ${PC_SUITE_BASE:-HEAD}"
  RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)-${BASE:0:7}"
  RD="$PC_AF_REPO/.suite/$RUN_ID"; WT="$RD/tree"
  # the working tree as ONE binary patch against HEAD, untracked files included (temp index — the real index is untouched)
  # worktree-safe: in a detached worktree .git is a FILE and the index lives under the common dir (bit 2026-09-06)
  IDX=$(git -C "$ROOT" rev-parse --git-path index); case "$IDX" in /*) ;; *) IDX="$ROOT/$IDX";; esac
  TMPI=$(mktemp); cp "$IDX" "$TMPI"
  GIT_INDEX_FILE="$TMPI" git add -A . >/dev/null 2>&1
  PATCH=$(mktemp); GIT_INDEX_FILE="$TMPI" git diff --cached --binary "$BASE" > "$PATCH"; rm -f "$TMPI"
  PSHA=$(sha256sum "$PATCH" | cut -d' ' -f1); PBYTES=$(wc -c < "$PATCH")
  bridge "cd $PC_AF_REPO && { git cat-file -e $BASE^{commit} 2>/dev/null && echo HAVE; } || { git fetch -q origin && git cat-file -e $BASE^{commit} && echo FETCHED; }" | grep -q "HAVE\|FETCHED" \
    || die "the PC clone does not have $BASE — push the head first (the PC runs pushed commits + your patch)"
  bridge "test -e $RD/pid && echo EXISTS || { mkdir -p $RD && echo NEW; }" | grep -q NEW || die "run dir $RD already launched"
  B64=$(mktemp); base64 -w0 < "$PATCH" > "$B64"; TOTAL=$(wc -c < "$B64"); i=0; off=0
  while [ "$off" -lt "$TOTAL" ]; do
    CH=$(dd if="$B64" bs=1 skip="$off" count=40000 2>/dev/null)
    bridge "printf %s '$CH' > $RD/part.$(printf %04d $i)" >/dev/null || die "part $i failed"
    off=$((off+40000)); i=$((i+1))
  done
  [ "$TOTAL" -eq 0 ] && bridge ": > $RD/part.0000" >/dev/null
  GOT=$(bridge "cat $RD/part.* | base64 -d > $RD/tree.patch && sha256sum $RD/tree.patch | cut -d' ' -f1" | tail -1)
  [ "$GOT" = "$PSHA" ] || die "patch sha mismatch on the PC (got ${GOT:-nothing}, want $PSHA)"
  bridge "cd $PC_AF_REPO && git worktree prune && git worktree add -q --detach $WT $BASE && cd $WT && { [ $PBYTES -eq 0 ] || git apply --binary --whitespace=nowarn $RD/tree.patch; } && echo APPLIED" | grep -q APPLIED \
    || die "worktree/apply failed on the PC"
  # PC-side wrapper script: the run's state (pid, rc) is written by the wrapper itself, so the launch
  # guard keys on state the run creates (rule 1b), and a replayed launch call is a no-op.
  RUNSH="#!/bin/bash
cd $WT || exit 97
S0_01_VENUE=pc S0_01_REAL_LEG_DIR=$PC_REAL_LEG_DIR $PC_PY -m pytest $SET -q -p no:cacheprovider -n $WORKERS --basetemp=$RD/tmp > $RD/log 2>&1 < /dev/null
echo \$? > $RD/rc
[ \"\$(cat $RD/rc)\" = 0 ] && rm -rf $RD/tmp
"
  bridge "printf %s '$(printf %s "$RUNSH" | base64 -w0)' | base64 -d > $RD/run.sh && chmod +x $RD/run.sh && echo SHIPPED" | grep -q SHIPPED || die "run.sh ship failed"
  # PRECEDENCE HAZARD (bit 2026-09-06): "a && b && setsid x ... &" backgrounds the WHOLE and-list in a subshell that
  # still holds the bridge's stdout pipe, so the bridge call blocks until the job ends and the client's retries
  # launch duplicates. Statements are separated with ";" so only the setsid command is backgrounded.
  LAUNCH="if [ -s $RD/pid ]; then echo GUARD; else setsid bash $RD/run.sh > $RD/launch.log 2>&1 < /dev/null & echo \$! > $RD/pid; fi; cat $RD/pid"
  OUT=$(bridge "$LAUNCH" 2>&1 | tail -1)
  case "$OUT" in [0-9]*) ;; *) echo "pc_suite: launch call did not confirm (${OUT:-no reply}) — wait will tell" >&2;; esac
  rm -f "$PATCH" "$B64"
  echo "pc_suite: launched $RUN_ID on the PC — base $BASE + patch ${PBYTES}B (sha ${PSHA:0:12}), set '$SET', -n $WORKERS" >&2
  echo "$RUN_ID" ;;
wait)
  RUN_ID="${1:?RUN_ID}"; MAXMIN="${2:-40}"; RD="$PC_AF_REPO/.suite/$RUN_ID"; n=0
  while :; do
    ST=$(bridge "test -s $RD/rc && echo DONE || { P=\$(cat $RD/pid 2>/dev/null); [ -n \"\$P\" ] && [ -d /proc/\$P ] && echo RUNNING || echo NOPROC; }" 2>/dev/null | tail -1)
    case "$ST" in
      DONE) break;;
      RUNNING) if [ $((n % 8)) = 0 ]; then BAD=$(bridge "grep -c 'INTERNALERROR\|No space left on device' $RD/log" | tail -1); [ "${BAD:-0}" != 0 ] && echo "pc_suite: WARNING the log shows INTERNALERROR/ENOSPC ($BAD lines) — the run is compromised" >&2; fi ;;
      NOPROC) sleep 3; ST2=$(bridge "test -s $RD/rc && echo DONE || echo GONE" | tail -1); [ "$ST2" = DONE ] && break; die "run $RUN_ID: no process and no rc (GONE) — see: pc_suite.sh log $RUN_ID";;
      *) echo "pc_suite: bridge probe unclear: $ST" >&2;;
    esac
    n=$((n+1)); [ $n -gt $((MAXMIN*4)) ] && die "run $RUN_ID still running after $MAXMIN min (see: pc_suite.sh log $RUN_ID)"
    sleep 15
  done
  RC=$(bridge "cat $RD/rc" | tail -1)
  bridge "grep '^FAILED\|^ERROR' $RD/log | head -40"
  SUM=$(bridge "grep -v '^\$' $RD/log | tail -n 1" | tail -1)
  echo "pytest-exit: $RC"; echo "pytest-summary: $SUM"
  case "$SUM" in *" passed"*) ;; *) echo "pc_suite: RED — the summary line carries no passed count (pytest rc $RC is not trusted)" >&2; exit 3;; esac
  exit "$RC" ;;
log)
  RUN_ID="${1:?RUN_ID}"; RD="$PC_AF_REPO/.suite/$RUN_ID"; bridge "tail -c ${2:-4000} $RD/log" ;;
*) die "usage: pc_suite.sh launch [-n N] [-- <pytest args>] | wait <RUN_ID> [max-min] | log <RUN_ID> [bytes]" ;;
esac
