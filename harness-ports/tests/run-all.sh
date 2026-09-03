#!/usr/bin/env bash
# Run every harness-port test. Deterministic, LLM-free, no network, no harness
# binary required. Exit 0 only if all suites pass.
#
#   bash harness-ports/tests/run-all.sh
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
cd "$ROOT" || exit 1

fail=0
for t in test_codex_hook_adapter.py test_hermes_hook_adapter.py \
         test_hermes_spool.py test_bridge_token_handling.py test_pc_bridge_exec.py \
         test_hermes_session_export.py; do
  printf '%-34s ' "$t"
  out="$(python3 "$HERE/$t" 2>&1)"; rc=$?
  printf '%s\n' "$(printf '%s' "$out" | tail -1)"
  [ $rc -ne 0 ] && { fail=$((fail+1)); printf '%s\n' "$out" | tail -20; }
done

printf '%-34s ' "test_pc_lane.sh"
out="$(bash "$HERE/test_pc_lane.sh" 2>&1)"; rc=$?
printf '%s\n' "$(printf '%s' "$out" | tail -1)"
[ $rc -ne 0 ] && { fail=$((fail+1)); printf '%s\n' "$out" | tail -20; }

printf '%-34s ' "test_sync_skills.sh"
out="$(bash "$HERE/test_sync_skills.sh" 2>&1)"; rc=$?
printf '%s\n' "$(printf '%s' "$out" | tail -1)"
[ $rc -ne 0 ] && { fail=$((fail+1)); printf '%s\n' "$out" | tail -20; }

printf '%-34s ' "build-roles --check"
out="$(python3 "$ROOT/harness-ports/bin/build-roles.py" --check 2>&1)"; rc=$?
printf '%s\n' "$out"
[ $rc -ne 0 ] && fail=$((fail+1))

echo
if [ "$fail" -eq 0 ]; then echo "ALL SUITES PASSED"; else echo "$fail SUITE(S) FAILED"; fi
exit "$fail"
