#!/usr/bin/env bash
# run_leg.sh — SANDBOX side: drive ONE S0-01 leg end to end over the PC bridge, then collect it.
#   proofs/S0-01/tools/pc/run_leg.sh run-1|run-2|cancel|shutdown|two-users|negative
# Every PC step is one bounded bridge call (the bridge caps a call at ~120 s); the launcher runs
# detached on the PC and is polled through its marker files. Secrets never leave the PC and never
# enter an argv (pc_launch.py / pc_mention.sh read them from files). Prints the PC-side output
# verbatim; a failed step stops the leg (set -e) — failures are FINDINGS, not things to route around.
set -euo pipefail
LEG=${1:?leg}
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"; cd "$ROOT"
PC=pc_quiet
pc_quiet() { bash scripts/pc.sh "$@" 2> >(grep -v "bind: warning" >&2); }
REPO_PC=/home/rocco/agent-factory; L=/home/rocco/s0-01-pinned/.markers; TOOLS=$REPO_PC/proofs/S0-01/tools/pc
FD=$L/v2-$LEG
step() { echo; echo "===== [$LEG] $* ====="; }

if [ "$LEG" = "negative" ]; then
  step "negative probe against the pinned agent"
  $PC "cd $REPO_PC && /usr/bin/python3 $TOOLS/pc_negative.py"
  step "collect"; bash proofs/S0-01/tools/pc/collect_leg.sh negative
  exit 0
fi

case "$LEG" in
  cancel) MODEL=s0-01-slow; RT=owner-only; AL="";;
  two-users) MODEL=s0-01-pong; RT=allowlist; AL=$(python3 -c 'import json; print(json.load(open("proofs/S0-01/fixtures/identities.json"))["user2"])');;
  *) MODEL=s0-01-pong; RT=owner-only; AL="";;
esac

step "PC tree at the pushed tip? (the tee sha is pinned to the committed file)"
$PC "cd $REPO_PC && git rev-parse --short HEAD && git status --short | head -5 && sha256sum proofs/S0-01/tools/frame_tee.py | cut -c1-16"
LOCAL_TEE=$(sha256sum proofs/S0-01/tools/frame_tee.py | cut -c1-16); echo "sandbox tee sha16: $LOCAL_TEE"

step "launch (detached) model=$MODEL respond_to=$RT"
EXTRA=""; [ -n "$AL" ] && EXTRA="--respond-to allowlist --allowlist $AL"
$PC "rm -f $L/v2-$LEG.launch.log; setsid /usr/bin/python3 $TOOLS/pc_launch.py --leg $LEG --model $MODEL $EXTRA </dev/null >$L/v2-$LEG.launch.log 2>&1 & sleep 1; echo launched"
for i in $(seq 1 12); do
  OUT=$($PC "test -f $FD/launch.ready && echo READY || { test -f $FD/buzz-acp.exit && echo DEAD; tail -3 $L/v2-$LEG.launch.log; }")
  case "$OUT" in *READY*) break;; *DEAD*) echo "$OUT"; echo "launch failed"; exit 4;; esac; sleep 5
done
$PC "cat $L/v2-$LEG.launch.log"
step "wait for the pre manifest (it must finish BEFORE the first mention)"
for i in $(seq 1 40); do $PC "test -f $FD/manifest-pre.done && echo PRE-DONE" | grep -q PRE-DONE && break; sleep 5; done
$PC "cat $FD/manifest-pre.summary"

case "$LEG" in
  run-1|run-2)
    step "owner mention → end_turn"; $PC "WHO=owner WAIT_FOR=end_turn bash $TOOLS/pc_mention.sh";;
  shutdown)
    step "owner mention → end_turn"; OUT=$($PC "WHO=owner WAIT_FOR=end_turn bash $TOOLS/pc_mention.sh"); echo "$OUT"
    EID=$(echo "$OUT" | sed -n 's/^EID=//p' | tail -1)
    step "owner !shutdown (thread reply to $EID)"; $PC "WHO=owner TEXT='!shutdown' TAG=shutdown-cmd REPLY_TO=$EID WAIT_FOR=none bash $TOOLS/pc_mention.sh"
    for i in $(seq 1 12); do $PC "test -f $FD/buzz-acp.exit && echo EXITED" | grep -q EXITED && break; sleep 5; done
    $PC "echo exit=\$(cat $FD/buzz-acp.exit 2>/dev/null); tail -2 $L/v2-$LEG.launch.log";;
  cancel)
    step "owner mention on the slow route → wait for the first chunk"; OUT=$($PC "WHO=owner WAIT_FOR=chunk bash $TOOLS/pc_mention.sh"); echo "$OUT"
    EID=$(echo "$OUT" | sed -n 's/^EID=//p' | tail -1)
    step "owner !cancel (thread reply to $EID) → cancelled"; $PC "WHO=owner TEXT='!cancel' TAG=cancel-cmd REPLY_TO=$EID WAIT_FOR=cancelled bash $TOOLS/pc_mention.sh";;
  two-users)
    step "owner + user2 mentions back to back → two end_turns"
    $PC "WHO=owner WAIT_FOR=none bash $TOOLS/pc_mention.sh"
    $PC "WHO=user2 WAIT_FOR=end_turn WAIT_COUNT=2 bash $TOOLS/pc_mention.sh";;
esac

step "post (scan, log, records, post manifest, teardown, leak guard)"
$PC "bash $TOOLS/pc_post.sh"
[ -n "${NO_COLLECT:-}" ] && { echo "NO_COLLECT set — leaving the leg on the PC (dry run)"; exit 0; }
step "collect"; bash proofs/S0-01/tools/pc/collect_leg.sh "$LEG"
