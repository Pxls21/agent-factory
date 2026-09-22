#!/usr/bin/env bash
# The sandbox dispatcher's role -> SERVER EFFORT mapping, deferred-restart gate, and the
# MEASURED-premise gate (T90): a FIRST launch is refused (rc 64) when the brief has no
# measured premise block; a resume of an already-launched lane is exempt. The test-only
# bridge function keeps every command local and records each bridge call, so a refusal
# must show NO mkdir -p (the guard runs before the write, AF-AP-79).
set -uo pipefail
unset HERMES_MODEL HERMES_REASONING LANE_SERVER_EFFORT ROLE PC_LANE_TEST_POLL_STATE PC_LANE_TEST_PROVIDER_MIX PC_LANE_TEST_PROVIDER_MIX_RC PC_LANE_TEST_SQL_CAPTURE PC_LANE_TEST_RESUME PC_LANE_TEST_EVAL_PREMISE PC_LANE_TEST_PREMISE_ERROR PC_LANE_TEST_LANE_PID PC_LANE_TEST_AF_REPO 2>/dev/null || true
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; ROOT="$(cd "$HERE/../.." && pwd)"
TMP="$(mktemp -d)"; FIXTURE_PIDS=()
cleanup() {
  local pid
  for pid in "${FIXTURE_PIDS[@]}"; do kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; done
  rm -rf "$TMP"
}
trap cleanup EXIT

# The fixture briefs. brief.md (the dispatch fixture) carries a measured premise block —
# the heading is at ### depth, lowercase, to prove the gate matches case-insensitively
# and at that depth. brief-noblock.md has NO block (the legacy form). The malformed
# fixtures separate empty, one-line, whitespace-only, and mixed-content blocks.
printf 'PIN: 0000000\nbrief\n\n### premise — measured at authoring (2026-09-22, c2a0df2)\n```\nsed -n 1p scripts/pc_lane.sh -> line 1\nrc=0\n```\n' > "$TMP/brief.md"
printf 'PIN: 0000000\nbrief\n' > "$TMP/brief-noblock.md"
printf 'PIN: 0000000\nbrief\n\n## premise — measured at authoring (2026-09-22, c2a0df2)\n```\n```\n' > "$TMP/brief-empty.md"
printf 'PIN: 0000000\nbrief\n\n## premise — measured at authoring (2026-09-22, c2a0df2)\n```\nline1\n```\n' > "$TMP/brief-oneline.md"
printf 'PIN: 0000000\nbrief\n\n## premise — measured at authoring (2026-09-22, c2a0df2)\n```\n  \n\t\n```\n' > "$TMP/brief-whitespace.md"
printf 'PIN: 0000000\nbrief\n\n## premise — measured at authoring (2026-09-22, c2a0df2)\n```\nreal\n  \n```\n' > "$TMP/brief-mixed.md"
printf 'PIN: 0000000\nbrief\n\n## premise at authoring (2026-09-22, c2a0df2)\n```\na\nb\n```\n' > "$TMP/brief-nomeasured.md"
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
    *'test -f '*'/FAILED && echo FAILED'*) echo "${PC_LANE_TEST_POLL_STATE:-GONE}";;
    *'mkdir -p '*'.lanes/'*) echo shipped;;
    *'.lanes/'*'kill -0 '*)
      [ "${PC_LANE_TEST_PREMISE_ERROR:-0}" -eq 0 ] || return 5
      if [ "${PC_LANE_TEST_EVAL_PREMISE:-0}" -eq 1 ]; then
        if [ -n "${PC_LANE_TEST_LANE_PID:-}" ]; then
          eval "readlink() { case \"\$*\" in *'/proc/$PC_LANE_TEST_LANE_PID/cwd'*) printf '%s\\n' \"${PC_LANE_TEST_AF_REPO:-/fake}/.lanes/brief-noblock.md--0000000/work\";; *) command readlink \"\$@\";; esac; }; $1"
        else
          eval "$1"
        fi
      else
        echo "${PC_LANE_TEST_RESUME:-FIRST}"
      fi;;
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
    *'test -f '*'/FAILED && echo FAILED'*) echo "${PC_LANE_TEST_POLL_STATE:-GONE}";;
    *'cat '*'/FAILED'*) printf '%s\n' "${PC_LANE_TEST_FAILED_TEXT:-route-capacity: exhausted}";;
    *'test -s '*'/report.partial.md && base64 -w0'*) printf '%s' "${PC_LANE_TEST_PARTIAL_B64:-}";;
    *'test -s '*'/report.md && base64 -w0'*) printf '%s' "${PC_LANE_TEST_REPORT_B64:-}";;
    *'sqlite3 -readonly '*)
      sql_path="$(printf '%s\n' "$1" | sed -n 's/.*base64 -d > \([^ ]*\).*/\1/p')"
      sql_b64="${1#*printf %s \' }"; sql_b64="${sql_b64#*printf %s \'}"; sql_b64="${sql_b64%%\'*}"
      [ -n "$sql_path" ] && printf '%s' "$sql_b64" | base64 -d > "$sql_path" 2>/dev/null
      [ -n "${PC_LANE_TEST_SQL_CAPTURE:-}" ] && cp "$sql_path" "$PC_LANE_TEST_SQL_CAPTURE"
      [ "${PC_LANE_TEST_PROVIDER_MIX_RC:-0}" -eq 0 ] || { echo "${PC_LANE_TEST_PROVIDER_MIX_ERROR:-sqlite failed}" >&2; return "${PC_LANE_TEST_PROVIDER_MIX_RC}"; }
      printf '%s' "${PC_LANE_TEST_PROVIDER_MIX:-}";;
    *'setsid env LANE_ID='*) echo launched;;
    *) echo ok;;
  esac
}
SH
run_dispatch() { # run_dispatch [ENV=VAL ...]
  local envs=()
  while [ "$#" -gt 0 ] && [ "$1" != "--" ]; do envs+=("$1"); shift; done
  : > "$BRIDGE_CALLS"
  env -u PC_LANE_SELF_COPY PC_BRIDGE_URL=http://unused PC_BRIDGE_TOKEN=unused PC_LANE_BRIDGE_FN="$BRIDGE_FN" PC_LANE_TEST_CALLS="$BRIDGE_CALLS" \
    PC_AF_REPO=/fake LANE_EFFORT_WAIT_SECONDS=0 LANE_EFFORT_WAIT_POLLS=2 MAX_POLLS=0 OUT_DIR="$TMP/out" \
    "${envs[@]}" bash "$ROOT/scripts/pc_lane.sh" "$TMP/brief.md" hermes code-implementer > "$TMP/out.txt" 2> "$TMP/err.txt"
}
run_gate() { # run_gate <brief> [ENV=VAL ...] --  (sets GATE_RC; stderr in $TMP/err.txt, calls in $BRIDGE_CALLS)
  local brief="$1"; shift
  local envs=()
  while [ "$#" -gt 0 ] && [ "$1" != "--" ]; do envs+=("$1"); shift; done
  : > "$BRIDGE_CALLS"
  env -u PC_LANE_SELF_COPY PC_BRIDGE_URL=http://unused PC_BRIDGE_TOKEN=unused PC_LANE_BRIDGE_FN="$BRIDGE_FN" PC_LANE_TEST_CALLS="$BRIDGE_CALLS" \
    PC_AF_REPO="${PC_LANE_TEST_AF_REPO:-/fake}" LANE_EFFORT_WAIT_SECONDS=0 LANE_EFFORT_WAIT_POLLS=2 MAX_POLLS=0 OUT_DIR="$TMP/out" \
    "${envs[@]}" bash "$ROOT/scripts/pc_lane.sh" "$brief" hermes code-implementer > "$TMP/out.txt" 2> "$TMP/err.txt"
  GATE_RC=$?
}
run_copy() { # run_copy <tmpdir> <brief> [ENV=VAL ...] --  (sets COPY_RC; no inherited bridge config)
  local tmpdir="$1" brief="$2"; shift 2
  local envs=()
  while [ "$#" -gt 0 ] && [ "$1" != "--" ]; do envs+=("$1"); shift; done
  : > "$BRIDGE_CALLS"
  env -u PC_LANE_SELF_COPY -u PC_BRIDGE_URL -u PC_BRIDGE_TOKEN PC_LANE_BRIDGE_FN="$BRIDGE_FN" PC_LANE_TEST_CALLS="$BRIDGE_CALLS" \
    PC_AF_REPO=/fake TMPDIR="$tmpdir" "${envs[@]}" bash "$ROOT/scripts/pc_lane.sh" "$brief" hermes code-implementer \
    > "$TMP/out.txt" 2> "$TMP/err.txt"
  COPY_RC=$?
}
run_poll() { # run_poll [ENV=VAL ...] --  (one poll, no wait; sets POLL_RC)
  local envs=()
  while [ "$#" -gt 0 ] && [ "$1" != "--" ]; do envs+=("$1"); shift; done
  : > "$BRIDGE_CALLS"; rm -rf "$TMP/poll-out"; mkdir -p "$TMP/poll-out"
  env -u PC_LANE_SELF_COPY PC_BRIDGE_URL=http://unused PC_BRIDGE_TOKEN=unused PC_LANE_BRIDGE_FN="$BRIDGE_FN" PC_LANE_TEST_CALLS="$BRIDGE_CALLS" \
    PC_AF_REPO=/fake PC_LANE_SKIP_ADMIT=1 LANE_SET_SERVER_EFFORT=0 POLL_SECONDS=0 MAX_POLLS=1 OUT_DIR="$TMP/poll-out" \
    PC_LANE_TEST_RESUME="${PC_LANE_TEST_RESUME-RESUME 1790000000}" \
    "${envs[@]}" bash "$ROOT/scripts/pc_lane.sh" "$TMP/brief.md" hermes code-implementer > "$TMP/out.txt" 2> "$TMP/err.txt"
  POLL_RC=$?
}

# T90-R1 self-copy — failure is terminal before config or bridge access.
run_copy /nonexistent "$TMP/brief-noblock.md" --
[ "$COPY_RC" -eq 64 ] \
  && grep -Fq 'pc_lane: refusing to run from the lazily-read original — private copy failed (mktemp/cp): ' "$TMP/err.txt" \
  && [ "$(wc -l < "$TMP/err.txt")" -eq 1 ] \
  && ! grep -q 'PC_LANE_SELF_COPY\|PC_BRIDGE_URL' "$TMP/err.txt" && [ ! -s "$BRIDGE_CALLS" ]
check "a private-copy failure refuses the original before any bridge call" $? \
  "rc=$COPY_RC stderr=$(tr '\n' ';' < "$TMP/err.txt") bridge_calls=$(wc -l < "$BRIDGE_CALLS")"

mkdir -p "$TMP/copy-ok"
run_copy "$TMP/copy-ok" "$TMP/missing-brief.md" PC_LANE_DEBUG_ENV=1 --
[ "$COPY_RC" -eq 64 ] \
  && grep -Fq 'pc_lane: private copy active: ' "$TMP/err.txt" \
  && grep -Fq 'pc_lane: brief not found:' "$TMP/err.txt" && ! grep -q 'unbound variable' "$TMP/err.txt" \
  && [ ! -s "$BRIDGE_CALLS" ]
check "a writable TMPDIR execs the private copy with PC_LANE_SELF_COPY set" $? \
  "rc=$COPY_RC stderr=$(tr '\n' ';' < "$TMP/err.txt") bridge_calls=$(wc -l < "$BRIDGE_CALLS")"

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

# T90-R1 premise gate. Every refusal asserts no ship write; every probe is one
# command and contains both the liveness check and this lane id.
assert_first_refusal() {
  [ "$GATE_RC" -eq 64 ] && grep -q 'no MEASURED premise block' "$TMP/err.txt" \
    && ! grep -q 'mkdir -p' "$BRIDGE_CALLS" \
    && [ "$(grep -c 'kill -0' "$BRIDGE_CALLS")" -eq 1 ] \
    && grep -q 'brief-noblock.md--0000000' "$BRIDGE_CALLS"
}

# A stale pidfile is evaluated by the fake bridge against a temp lane directory.
PROBE_REPO="$TMP/probe-repo"; PROBE_LANE="$PROBE_REPO/.lanes/brief-noblock.md--0000000"
mkdir -p "$PROBE_LANE"; printf '99999999\n' > "$PROBE_LANE/lane.pid"
PC_LANE_TEST_AF_REPO="$PROBE_REPO" run_gate "$TMP/brief-noblock.md" PC_LANE_TEST_EVAL_PREMISE=1 --
assert_first_refusal
check "a stale pidfile is FIRST and a premise-less brief is refused with no ship write" $? \
  "rc=$GATE_RC no_ship_writes=$(grep -c 'mkdir -p' "$BRIDGE_CALLS") calls=$(tr '\n' ';' < "$BRIDGE_CALLS")"

# A live pid whose process does not name or run under this lane is also FIRST.
sleep 30 & OTHER_PID=$!; FIXTURE_PIDS+=("$OTHER_PID"); printf '%s\n' "$OTHER_PID" > "$PROBE_LANE/lane.pid"
PC_LANE_TEST_AF_REPO="$PROBE_REPO" run_gate "$TMP/brief-noblock.md" PC_LANE_TEST_EVAL_PREMISE=1 --
assert_first_refusal
check "a live pid from another lane is FIRST and refused with no ship write" $? \
  "rc=$GATE_RC no_ship_writes=$(grep -c 'mkdir -p' "$BRIDGE_CALLS") calls=$(tr '\n' ';' < "$BRIDGE_CALLS")"

# A live process with cwd inside this lane binds the pid to the lane. Set mtime to
# the epoch fixture that also drives the re-attach mix-window assertion below.
mkdir -p "$PROBE_LANE/work"; sleep 30 & LANE_PID=$!; FIXTURE_PIDS+=("$LANE_PID")
printf '%s\n' "$LANE_PID" > "$PROBE_LANE/lane.pid"; touch -d @1790000000 "$PROBE_LANE/lane.pid"
PC_LANE_TEST_AF_REPO="$PROBE_REPO" run_gate "$TMP/brief-noblock.md" PC_LANE_TEST_EVAL_PREMISE=1 PC_LANE_TEST_LANE_PID="$LANE_PID" --
[ "$GATE_RC" -eq 75 ] && grep -q 'premise gate skipped — a resume of' "$TMP/err.txt" \
  && grep -q 'mkdir -p' "$BRIDGE_CALLS" && [ "$(grep -c 'kill -0' "$BRIDGE_CALLS")" -eq 1 ]
check "a live pid bound to this lane returns RESUME with its launch epoch and ships" $? \
  "rc=$GATE_RC calls=$(tr '\n' ';' < "$BRIDGE_CALLS")"

run_gate "$TMP/brief-noblock.md" PC_LANE_TEST_PREMISE_ERROR=1 --
assert_first_refusal
check "a premise-probe bridge error is FIRST and refused with no ship write" $? \
  "rc=$GATE_RC no_ship_writes=$(grep -c 'mkdir -p' "$BRIDGE_CALLS") calls=$(tr '\n' ';' < "$BRIDGE_CALLS")"

# Unit-level premise counter controls through the dispatcher gate.
run_gate "$TMP/brief-whitespace.md" --
[ "$GATE_RC" -eq 64 ] && ! grep -q 'mkdir -p' "$BRIDGE_CALLS"
check "two whitespace-only premise lines are refused with no ship write" $? "rc=$GATE_RC"

run_gate "$TMP/brief-mixed.md" --
[ "$GATE_RC" -eq 64 ] && ! grep -q 'mkdir -p' "$BRIDGE_CALLS"
check "one real and one whitespace premise line are refused with no ship write" $? "rc=$GATE_RC"

# a heading with an EMPTY fenced block is not a block
run_gate "$TMP/brief-empty.md"
[ "$GATE_RC" -eq 64 ] && grep -q 'no MEASURED premise block' "$TMP/err.txt" && ! grep -q 'mkdir -p' "$BRIDGE_CALLS"
check "a heading with an empty fenced block is refused" $? "rc=$GATE_RC stderr=$(tr '\n' ';' < "$TMP/err.txt")"

# a heading with a ONE-line fenced block is not a block (needs at least TWO non-space lines)
run_gate "$TMP/brief-oneline.md"
[ "$GATE_RC" -eq 64 ] && grep -q 'no MEASURED premise block' "$TMP/err.txt" && ! grep -q 'mkdir -p' "$BRIDGE_CALLS"
check "a heading with a one-line fenced block is refused" $? "rc=$GATE_RC stderr=$(tr '\n' ';' < "$TMP/err.txt")"

# the fixture brief.md (### depth, lowercase heading) passes the gate and ships
run_gate "$TMP/brief.md"
[ "$GATE_RC" -eq 75 ] && grep -q 'server effort applied' "$TMP/err.txt" && grep -q 'mkdir -p' "$BRIDGE_CALLS"
check "a ### depth lowercase heading with a two-line block passes and ships" $? "rc=$GATE_RC stderr=$(tr '\n' ';' < "$TMP/err.txt")"

# the heading must contain BOTH 'premise' and 'measured' (case-insensitive); a heading
# with only 'premise' is not a block even with a two-line fence
run_gate "$TMP/brief-nomeasured.md"
[ "$GATE_RC" -eq 64 ] && grep -q 'no MEASURED premise block' "$TMP/err.txt" && ! grep -q 'mkdir -p' "$BRIDGE_CALLS"
check "a heading missing 'measured' is not a block" $? "rc=$GATE_RC stderr=$(tr '\n' ';' < "$TMP/err.txt")"

# T91 poll/harvest seam — a single local poll with canned bridge state.
PARTIAL_TEXT='PARTIAL REPORT — retained draft'
PARTIAL_B64="$(printf '%s\n' "$PARTIAL_TEXT" | base64 -w0)"
run_poll PC_LANE_TEST_POLL_STATE=FAILED \
  "PC_LANE_TEST_FAILED_TEXT=safety-filter: ⚠️  The model provider's safety filter blocked this request" \
  "PC_LANE_TEST_PARTIAL_B64=$PARTIAL_B64" --
[ "$POLL_RC" -eq 70 ] \
  && grep -q "LANE FAILED — the model provider's safety filter refused the request" "$TMP/err.txt" \
  && grep -q '^safety-filter:' "$TMP/err.txt" \
  && grep -q 'partial ->' "$TMP/err.txt" \
  && grep -q '^PARTIAL REPORT' "$TMP/poll-out/report-brief.md--0000000.partial.md"
check "a safety-filter FAILED probe prints its terminal message and brings report.partial.md home" $? \
  "rc=$POLL_RC stderr=$(tr '\n' ';' < "$TMP/err.txt")"

READY_TEXT='REAL DISPATCH REPORT'
READY_B64="$(printf '%s\n' "$READY_TEXT" | base64 -w0)"
SQL_CAPTURE="$TMP/provider-mix.sql"
MIX_ONE=$'MIX\tqwen:200=2 codex:200=1\t\t\t\nTAG\tconv_abcd\t09:15:46\t09:16:10\t3\nMETA\tdb_missing\t0\t\t\nMETA\tother\t0\t\t'
run_poll PC_LANE_TEST_POLL_STATE=READY "PC_LANE_TEST_REPORT_B64=$READY_B64" "PC_LANE_TEST_PROVIDER_MIX=$MIX_ONE" HERMES_MODEL="agentfactory-build-local'; DROP TABLE call_logs; --" LANE_SERVER_EFFORT= HOME=/sandbox-should-not-be-used "PC_LANE_TEST_SQL_CAPTURE=$SQL_CAPTURE" --
[ "$POLL_RC" -eq 0 ] \
  && grep -q '^REAL DISPATCH REPORT' "$TMP/poll-out/report-brief.md--0000000.md" \
  && grep -Fq 'report ->' "$TMP/err.txt" \
  && grep -Fq "combo-window provider mix (per-lane provenance UNVERIFIED) agentfactory-build-local'; DROP TABLE call_logs; -- " "$TMP/err.txt" \
  && grep -Fq 'qwen:200=2 codex:200=1 | tags: conv_abcd(09:15:46-09:16:10,n=3)' "$TMP/err.txt" \
  && ! grep -Fq 'COMBO-WINDOW aggregate' "$TMP/err.txt" \
  && ! grep -Fq '/sandbox-should-not-be-used/.omniroute-migrated' "$BRIDGE_CALLS" \
  && [ -n "$SQL_CAPTURE" ] && grep -Fq "combo_name = 'agentfactory-build-local''; DROP TABLE call_logs; --'" "$SQL_CAPTURE" \
  && grep -Fq "api_key_name = 'hermes'" "$SQL_CAPTURE" && grep -Fq "provider LIKE 'openai-compatible-chat-%'" "$SQL_CAPTURE"
check "NEGATIVE CONTROL: a READY probe still harvests; one-tag mix has no caveat and the shipped read-only SQL escapes its combo filter" $? \
  "rc=$POLL_RC stderr=$(tr '\n' ';' < "$TMP/err.txt") sql=$SQL_CAPTURE"

MIX_TWO=$'MIX\tqwen:200=4 codex:200=2\t\t\t\nTAG\tconv_abcd\t09:15:46\t09:17:10\t4\nTAG\tconv_other\t09:15:50\t09:17:12\t2\nMETA\tdb_missing\t0\t\t\nMETA\tother\t1\t\t'
# Restore role-derived combo selection after the hostile explicit-model SQL-escaping control.
unset HERMES_MODEL LANE_SERVER_EFFORT
run_poll PC_LANE_TEST_POLL_STATE=READY "PC_LANE_TEST_REPORT_B64=$READY_B64" "PC_LANE_TEST_PROVIDER_MIX=$MIX_TWO" "PC_LANE_TEST_SQL_CAPTURE=$SQL_CAPTURE" --
[ "$POLL_RC" -eq 0 ] \
  && grep -q 'qwen:200=4 codex:200=2 | tags: conv_abcd(09:15:46-09:17:10,n=4) conv_other(09:15:50-09:17:12,n=2)' "$TMP/err.txt" \
  && grep -Fq 'pc_lane: the mix is a COMBO-WINDOW aggregate — 1 conversation tag(s) shared it; per-lane execution provenance is UNVERIFIED (no lane key in call_logs; T92)' "$TMP/err.txt" \
  && ! grep -Fq "the lane's own share is the tag(s) starting at launch" "$TMP/err.txt" \
  && grep -Fq "timestamp >= '2026-09-21T14:12:20Z'" "$SQL_CAPTURE"
check "a RESUME mix is labelled as a combo-window aggregate and starts at lane launch minus 60 seconds" $? \
  "rc=$POLL_RC stderr=$(tr '\n' ';' < "$TMP/err.txt") sql=$SQL_CAPTURE"

run_poll PC_LANE_TEST_POLL_STATE=READY "PC_LANE_TEST_REPORT_B64=$READY_B64" $'PC_LANE_TEST_PROVIDER_MIX=META\tdb_missing\t1\t\t\nMETA\tother\t0\t\t' --
[ "$POLL_RC" -eq 0 ] && grep -q 'provider-mix: no call_logs rows in the window (db=' "$TMP/err.txt"
check "an empty call-log result is reported, never silent, and harvest remains successful" $? \
  "rc=$POLL_RC stderr=$(tr '\n' ';' < "$TMP/err.txt")"

run_poll PC_LANE_TEST_POLL_STATE=READY "PC_LANE_TEST_REPORT_B64=$READY_B64" PC_LANE_TEST_PROVIDER_MIX_RC=5 "PC_LANE_TEST_PROVIDER_MIX_ERROR=database unavailable" --
[ "$POLL_RC" -eq 0 ] && grep -q 'provider-mix unavailable: database unavailable' "$TMP/err.txt"
check "a provider-mix bridge/sqlite failure is loud but does not change harvest rc" $? \
  "rc=$POLL_RC stderr=$(tr '\n' ';' < "$TMP/err.txt")"

# FIRST uses this poller's current launch time, not a stale or resume epoch.
FIRST_BEFORE="$(date -u +%s)"
PC_LANE_TEST_RESUME= run_poll PC_LANE_TEST_POLL_STATE=READY "PC_LANE_TEST_REPORT_B64=$READY_B64" "PC_LANE_TEST_PROVIDER_MIX=$MIX_ONE" "PC_LANE_TEST_SQL_CAPTURE=$SQL_CAPTURE" --
FIRST_AFTER="$(date -u +%s)"
FIRST_BOUND="$(sed -n "s/.*timestamp >= '\([^']*\)'.*/\1/p" "$SQL_CAPTURE" | head -1)"
FIRST_BOUND_EPOCH="$(date -u -d "$FIRST_BOUND" +%s 2>/dev/null || printf 0)"
[ "$POLL_RC" -eq 0 ] && [ "$FIRST_BOUND_EPOCH" -ge "$((FIRST_BEFORE-65))" ] \
  && [ "$FIRST_BOUND_EPOCH" -le "$((FIRST_AFTER-55))" ]
check "a FIRST mix window starts within five seconds of now minus 60 seconds" $? \
  "rc=$POLL_RC before=$FIRST_BEFORE after=$FIRST_AFTER sql_bound=$FIRST_BOUND epoch=$FIRST_BOUND_EPOCH"

OLD_ATTR_COUNT="$(grep -c "the lane's own share is the tag(s) starting at launch" "$ROOT/scripts/pc_lane.sh" || true)"
[ "$OLD_ATTR_COUNT" -eq 0 ]
check "the old per-lane attribution sentence is absent from the dispatcher" $? "grep_count=$OLD_ATTR_COUNT"

echo; echo "pc_lane dispatcher: $pass passed, $fail failed"; [ "$fail" -eq 0 ]
