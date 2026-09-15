#!/usr/bin/env bash
# The sandbox dispatcher's role -> SERVER EFFORT mapping and deferred-restart gate.
# A test-only bridge function keeps every command local and records whether the lane launch boundary was crossed.
set -uo pipefail
unset HERMES_MODEL HERMES_REASONING LANE_SERVER_EFFORT ROLE 2>/dev/null || true
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; ROOT="$(cd "$HERE/../.." && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
printf 'PIN: 0000000\nbrief\n' > "$TMP/brief.md"
pass=0; fail=0
check() { if [ "$2" -eq 0 ]; then pass=$((pass+1)); echo "[PASS] $1"; else fail=$((fail+1)); echo "[FAIL] $1"; fi; echo "         because: $3"; }
run() { # run <expected> [ENV=VAL ...] -- role
  local expected="$1"; shift; local envs=(); while [ "$1" != "--" ]; do envs+=("$1"); shift; done; shift
  local out; out="$(env -u PC_LANE_SELF_COPY PC_BRIDGE_URL=http://unused PC_BRIDGE_TOKEN=unused LANE_PRINT_EFFORT=1 "${envs[@]}" bash "$ROOT/scripts/pc_lane.sh" "$TMP/brief.md" hermes "$1" 2>/dev/null | grep '^server-effort=')"
  [ "$out" = "server-effort=$expected" ]; check "$1 ${envs[*]:-} -> $expected" $? "got '$out'"
}
run medium -- code-implementer
run xhigh -- adversarial-verifier
run xhigh HERMES_REASONING=ultra -- code-implementer
run xhigh HERMES_REASONING=high -- adversarial-verifier
run low HERMES_REASONING=low -- code-implementer
run "<cloud route>" HERMES_MODEL=agentfactory-build -- code-implementer
run "<cloud route>" -- researcher
run xhigh HERMES_MODEL=qwen-local/qwen3.8-27b-local HERMES_REASONING=max -- researcher
run low LANE_SERVER_EFFORT=low -- adversarial-verifier

BRIDGE_FN="$TMP/bridge.sh"; BRIDGE_CALLS="$TMP/bridge.calls"; TERMINAL="$TMP/terminal"
cat > "$BRIDGE_FN" <<'SH'
bridge() {
  printf '%s\n' "$1" >> "$PC_LANE_TEST_CALLS"
  case "$1" in
    *'mkdir -p '*'.lanes/'*) echo shipped;;
    *"open('/proc/"*) echo "${PC_LANE_TEST_RUNNING:-mismatch:low}";;
    *'restart-when-idle --max-wait 1800'*)
      case "${PC_LANE_TEST_TERMINAL:-applied}" in
        already) echo 'qwen-server: already applied';;
        *) echo 'qwen-server: pending: watcher 4242';;
      esac;;
    *'qwen-builder/pending/env'*) echo abcdef123456;;
    *"grep -E '^(applied|expired|failed)"*)
      case "${PC_LANE_TEST_TERMINAL:-applied}" in
        applied) echo 'applied 2026-09-15T00:00:00Z env-sha=abcdef123456 argv-sha=111111111111';;
        expired) echo 'expired 2026-09-15T00:00:00Z env-sha=abcdef123456 blocked-by=busy';;
        failed) echo 'failed 2026-09-15T00:00:00Z env-sha=abcdef123456 rc=5';;
      esac;;
    *'test -f '*'/FAILED'*) echo GONE;;
    *'setsid env LANE_ID='*) echo launched;;
    *) echo ok;;
  esac
}
SH
run_dispatch() {
  : > "$BRIDGE_CALLS"
  env -u PC_LANE_SELF_COPY PC_BRIDGE_URL=http://unused PC_BRIDGE_TOKEN=unused PC_LANE_BRIDGE_FN="$BRIDGE_FN" PC_LANE_TEST_CALLS="$BRIDGE_CALLS" \
    PC_AF_REPO=/fake LANE_EFFORT_WAIT_SECONDS=0 LANE_EFFORT_WAIT_POLLS=2 MAX_POLLS=0 OUT_DIR="$TMP/out" \
    "$@" bash "$ROOT/scripts/pc_lane.sh" "$TMP/brief.md" hermes code-implementer > "$TMP/out.txt" 2> "$TMP/err.txt"
}

PC_LANE_TEST_TERMINAL=applied run_dispatch; rc=$?
[ "$rc" -eq 75 ] && grep -q 'restart-when-idle --max-wait 1800' "$BRIDGE_CALLS" && grep -q 'setsid env LANE_ID=' "$BRIDGE_CALLS" && grep -q 'server effort applied' "$TMP/err.txt"
check "local mismatch waits for applied before launch" $? "rc=$rc calls=$(tr '\n' ';' < "$BRIDGE_CALLS")"

PC_LANE_TEST_TERMINAL=expired run_dispatch; rc=$?
[ "$rc" -eq 64 ] && grep -q 'server effort expired: busy' "$TMP/err.txt" && ! grep -q 'setsid env LANE_ID=' "$BRIDGE_CALLS"
check "expired deferred restart blocks lane launch with reason" $? "rc=$rc stderr=$(tr '\n' ';' < "$TMP/err.txt")"

PC_LANE_TEST_TERMINAL=failed run_dispatch; rc=$?
[ "$rc" -eq 5 ] && grep -q 'server effort failed rc=5' "$TMP/err.txt" && ! grep -q 'setsid env LANE_ID=' "$BRIDGE_CALLS"
check "failed deferred restart propagates rc and blocks launch" $? "rc=$rc stderr=$(tr '\n' ';' < "$TMP/err.txt")"

PC_LANE_TEST_TERMINAL=applied run_dispatch HERMES_MODEL=agentfactory-build; rc=$?
[ "$rc" -eq 75 ] && ! grep -q 'restart-when-idle' "$BRIDGE_CALLS" && grep -q 'setsid env LANE_ID=' "$BRIDGE_CALLS"
check "cloud route skips deferred effort step" $? "rc=$rc calls=$(tr '\n' ';' < "$BRIDGE_CALLS")"

echo; echo "pc_lane dispatcher: $pass passed, $fail failed"; [ "$fail" -eq 0 ]
