#!/usr/bin/env bash
# Deterministic shell contract for qwen-matrix.sh. All service/network/GPU seams are fakes.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNNER="$HERE/../bin/qwen-matrix.sh"
TMP="$(mktemp -d)" || exit 1
CHILD_PIDS=""
cleanup() {
  local pid
  for pid in $CHILD_PIDS; do kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; done
  rm -rf "$TMP"
}
trap cleanup EXIT
pass=0; fail=0
check() {
  if [ "$2" -eq 0 ]; then pass=$((pass+1)); echo "[PASS] $1"; else fail=$((fail+1)); echo "[FAIL] $1"; fi
  echo "         because: $3"
}

bash -n "$RUNNER"; check "bash -n qwen-matrix.sh" $? "the script parses"
mkdir -p "$TMP/bin" "$TMP/prompts" "$TMP/matrix/baseline" "$TMP/home/.config/systemd/user"
printf '{"messages":[{"role":"user","content":"fixture"}]}\n' > "$TMP/prompts/prompt-001.json"
printf 'QWEN_CACHE_RAM=8192\n' > "$TMP/matrix/baseline/env"
printf 'baseline unit\n' > "$TMP/home/.config/systemd/user/qwen-builder.service"
BASELINE_SHA=$(sha256sum "$TMP/home/.config/systemd/user/qwen-builder.service" | cut -d' ' -f1)
CALLS="$TMP/calls.log"; : > "$CALLS"

cat > "$TMP/bin/qwen-server" <<'SH'
#!/usr/bin/env bash
printf '%s' "$1" >> "$QM_TEST_CALLS"
for name in QWEN_CACHE_RAM QWEN_CTXCP QWEN_CMS QWEN_UBATCH QWEN_SPEC_P_MIN QWEN_SPEC_TYPE; do
  value=${!name-}; [ -z "$value" ] || printf ' %s=%s' "$name" "$value" >> "$QM_TEST_CALLS"
done
printf '\n' >> "$QM_TEST_CALLS"
case "$1" in
  guard)
    [ "${QM_GUARD_RC:-0}" -eq 0 ] || { echo "$QWEN_LANES_DIR/live/lane.pid $QM_LIVE_PID LOCAL"; exit "$QM_GUARD_RC"; };;
  argv) printf '%s\n' fake-server --cache-ram "${QWEN_CACHE_RAM:-8192}" --spec-type "${QWEN_SPEC_TYPE:-draft-mtp}";;
  unit) printf '[Service]\nExecStart=fake --cache-ram %s\n' "${QWEN_CACHE_RAM:-8192}";;
  install)
    if [ "${QM_RESTORE_WRONG_BYTES:-0}" -eq 1 ] && [ "${QWEN_CACHE_RAM:-8192}" = 8192 ]; then printf 'wrong restored unit\n' > "$QWEN_MATRIX_UNIT_PATH"
    elif [ "${QWEN_CACHE_RAM:-8192}" = 8192 ]; then printf 'baseline unit\n' > "$QWEN_MATRIX_UNIT_PATH"
    else printf 'cell unit %s\n' "$QWEN_CACHE_RAM" > "$QWEN_MATRIX_UNIT_PATH"; fi;;
  uninstall)
    [ "${QM_UNINSTALL_LEAVES_UNIT:-0}" -eq 1 ] || rm -f "$QWEN_MATRIX_UNIT_PATH";;
  health) exit 0;;
  *) exit 64;;
esac
SH
chmod +x "$TMP/bin/qwen-server"

cat > "$TMP/bin/qwen-matrix.py" <<'PY'
#!/usr/bin/env python3
import json
import pathlib
import sys
args = sys.argv[1:]
out = pathlib.Path(args[args.index("--out") + 1])
argv_file = pathlib.Path(args[args.index("--argv-file") + 1])
unit_sha_file = pathlib.Path(args[args.index("--unit-sha-file") + 1])
unit_text_file = pathlib.Path(args[args.index("--unit-text-file") + 1])
run_id = args[args.index("--run-id") + 1]
out.write_text(json.dumps({
  "schema": "qwen-matrix-v1",
  "cell": {"name": __import__("os").environ["QWEN_MATRIX_CELL"],
           "argv_text": argv_file.read_text(), "argv_sha256": "fixture",
           "unit_sha256": unit_sha_file.read_text().strip(),
           "unit_text_sha256": __import__("hashlib").sha256(unit_text_file.read_bytes()).hexdigest(),
           "run_id": run_id,
           "props": {"model_alias": "fixture", "total_slots": 2,
                     "default_generation_settings": {"n_ctx": 200000}, "build_info": "fixture"}},
  "summary": {"decode_tps": 1, "prompt_tps": 2, "busy_slots_per_decode": 2, "re_prefill_count": 0},
  "rounds": []}) + "\n")
PY
chmod +x "$TMP/bin/qwen-matrix.py"

cat > "$TMP/bin/nvidia-smi" <<'SH'
#!/usr/bin/env bash
printf '1234\n'
SH
chmod +x "$TMP/bin/nvidia-smi"

COMMON=(HOME="$TMP/home" PATH="$TMP/bin:$PATH" QM_TEST_CALLS="$CALLS"
  QWEN_MATRIX_SERVER="$TMP/bin/qwen-server" QWEN_MATRIX_PY="$TMP/bin/qwen-matrix.py"
  QWEN_MATRIX_ROOT="$TMP/matrix" QWEN_MATRIX_PROMPTS="$TMP/prompts"
  QWEN_MATRIX_UNIT_PATH="$TMP/home/.config/systemd/user/qwen-builder.service"
  QWEN_MATRIX_BASELINE_ENV="$TMP/matrix/baseline/env" QWEN_MATRIX_GPU_INTERVAL_S=1
  QWEN_MATRIX_HEALTH_WAIT_S=2 QWEN_MATRIX_CONCURRENCY=2 QWEN_MATRIX_ROUNDS=1 QWEN_MATRIX_MAX_TOKENS=4)

# Positive dry run: guard -> render -> install -> health -> load -> restore, with identity/state assertions.
OUT=$(env "${COMMON[@]}" bash "$RUNNER" T -- QWEN_CACHE_RAM=32768 QWEN_CTXCP=32 QWEN_CMS=4096 \
  QWEN_UBATCH=1024 QWEN_SPEC_P_MIN=0.25 QWEN_SPEC_TYPE=none 2>&1); rc=$?
[ "$rc" -eq 0 ] && [ "$(sha256sum "$TMP/home/.config/systemd/user/qwen-builder.service" | cut -d' ' -f1)" = "$BASELINE_SHA" ]
check "fake cell run restores baseline unit bytes" $? "rc=$rc baseline=$BASELINE_SHA after=$(sha256sum "$TMP/home/.config/systemd/user/qwen-builder.service" | cut -d' ' -f1): $OUT"
FIRST=$(sed -n '1p' "$CALLS"); [ "$FIRST" = "guard QWEN_CACHE_RAM=32768 QWEN_CTXCP=32 QWEN_CMS=4096 QWEN_UBATCH=1024 QWEN_SPEC_P_MIN=0.25 QWEN_SPEC_TYPE=none" ]
check "launcher guard is the first call and receives every cell override" $? "first=$FIRST"
grep -qx 'install QWEN_CACHE_RAM=8192' "$CALLS" && grep -qx 'install QWEN_CACHE_RAM=32768 QWEN_CTXCP=32 QWEN_CMS=4096 QWEN_UBATCH=1024 QWEN_SPEC_P_MIN=0.25 QWEN_SPEC_TYPE=none' "$CALLS"
check "cell install and baseline-env restore both ran" $? "$(tr '\n' ';' < "$CALLS")"
[ "$(sed -n '1p' "$TMP/matrix/T/env")" = "QWEN_CACHE_RAM=32768" ] && \
  grep -qx 'QWEN_MATRIX_CONCURRENCY=2' "$TMP/matrix/T/env" && [ -s "$TMP/matrix/T/argv.txt" ] && \
  [ -s "$TMP/matrix/T/unit-text" ] && [ -s "$TMP/matrix/T/unit-sha256" ] && [ -s "$TMP/matrix/T/run-complete" ]
check "cell env, argv text, unit text, unit sha, and completion are recorded" $? "$(tr '\n' ';' < "$TMP/matrix/T/env")"
python3 - "$TMP/matrix/T/result.json" "$TMP/matrix/T/run-complete" "$TMP/matrix/T/unit-text" <<'PY'
import hashlib,json,pathlib,sys
d=json.load(open(sys.argv[1])); completion=pathlib.Path(sys.argv[2]).read_text().strip(); unit=pathlib.Path(sys.argv[3]).read_bytes()
assert d["cell"]["name"]=="T" and d["vram_peak_mib"]==1234
assert d["cell"]["run_id"]==completion and d["cell"]["unit_sha256"]==hashlib.sha256(unit).hexdigest()
PY
check "result JSON is bound to completion and persisted unit bytes" $? "result.json decoded"

# Negative control: a completed cell name is immutable, so a rerun cannot leave stale evidence current.
: > "$CALLS"
OUT=$(env "${COMMON[@]}" bash "$RUNNER" T -- QWEN_CACHE_RAM=32768 2>&1); rc=$?
[ "$rc" -eq 3 ] && [ -s "$TMP/matrix/T/result.json" ] && ! grep -q '^install' "$CALLS" && \
  case "$OUT" in *"cell directory already exists; choose a new cell name"*) true;; *) false;; esac
check "existing cell directory is refused before lifecycle effects" $? "rc=$rc calls=$(tr '\n' ';' < "$CALLS"): $OUT"

# Negative control: a real live pid plus the launcher's rc 7 must create no cell dir and make no install call.
: > "$CALLS"; rm -rf "$TMP/matrix/BLOCKED"
env HERMES_MODEL=agentfactory-build-local bash -c 'exec -a qm1-live-lane sleep 60' &
LIVE_PID=$!; CHILD_PIDS="$CHILD_PIDS $LIVE_PID"
mkdir -p "$TMP/lanes/live"; printf '%s\n' "$LIVE_PID" > "$TMP/lanes/live/lane.pid"
OUT=$(env "${COMMON[@]}" QWEN_LANES_DIR="$TMP/lanes" QM_LIVE_PID="$LIVE_PID" QM_GUARD_RC=7 \
  bash "$RUNNER" BLOCKED -- QWEN_CACHE_RAM=32768 2>&1); rc=$?
[ "$rc" -eq 7 ] && [ ! -e "$TMP/matrix/BLOCKED" ] && ! grep -q '^install' "$CALLS" && \
  case "$OUT" in *"$TMP/lanes/live/lane.pid $LIVE_PID LOCAL"*"guard refused cell BLOCKED"*) true;; *) false;; esac
check "live-lane guard refuses rc 7 before cell or service side effects" $? "rc=$rc calls=$(tr '\n' ';' < "$CALLS"): $OUT"
kill "$LIVE_PID" 2>/dev/null || true; wait "$LIVE_PID" 2>/dev/null || true; CHILD_PIDS=""

# Negative control: a load failure still restores the exact baseline unit bytes.
cat > "$TMP/bin/fail-matrix.py" <<'PY'
#!/usr/bin/env python3
raise SystemExit(9)
PY
chmod +x "$TMP/bin/fail-matrix.py"; : > "$CALLS"
OUT=$(env "${COMMON[@]}" QWEN_MATRIX_PY="$TMP/bin/fail-matrix.py" bash "$RUNNER" FAIL -- QWEN_CACHE_RAM=32768 2>&1); rc=$?
[ "$rc" -eq 7 ] && [ "$(sha256sum "$TMP/home/.config/systemd/user/qwen-builder.service" | cut -d' ' -f1)" = "$BASELINE_SHA" ] && \
  grep -qx 'install QWEN_CACHE_RAM=8192' "$CALLS"
check "load failure returns rc 7 and restores baseline" $? "rc=$rc after=$(sha256sum "$TMP/home/.config/systemd/user/qwen-builder.service" | cut -d' ' -f1): $OUT"

cat > "$TMP/bin/fail-after-result-matrix.py" <<'PY'
#!/usr/bin/env python3
import json
import os
import pathlib
import sys
args = sys.argv[1:]
out = pathlib.Path(args[args.index("--out") + 1])
argv_file = pathlib.Path(args[args.index("--argv-file") + 1])
unit_sha_file = pathlib.Path(args[args.index("--unit-sha-file") + 1])
run_id = args[args.index("--run-id") + 1]
out.write_text(json.dumps({
  "schema": "qwen-matrix-v1",
  "cell": {"name": os.environ["QWEN_MATRIX_CELL"], "argv_text": argv_file.read_text(),
           "argv_sha256": "fixture", "unit_sha256": unit_sha_file.read_text().strip(),
           "run_id": run_id},
  "summary": {"requests": 1, "decode_tps": 1, "prompt_tps": 2,
              "busy_slots_per_decode": 2, "re_prefill_count": 0},
  "rounds": []}) + "\n")
PY
chmod +x "$TMP/bin/fail-after-result-matrix.py"
printf 'baseline unit\n' > "$TMP/home/.config/systemd/user/qwen-builder.service"
: > "$CALLS"
OUT=$(env "${COMMON[@]}" QWEN_MATRIX_PY="$TMP/bin/fail-after-result-matrix.py" QM_RESTORE_WRONG_BYTES=1 \
  bash "$RUNNER" AFTER_RESULT_FAIL -- QWEN_CACHE_RAM=32768 2>&1); rc=$?
[ "$rc" -eq 8 ] && [ -s "$TMP/matrix/AFTER_RESULT_FAIL/result.json" ] && \
  [ ! -e "$TMP/matrix/AFTER_RESULT_FAIL/run-complete" ]
check "failed restoration after result write leaves no completion record" $? "rc=$rc: $OUT"

cat > "$TMP/bin/invalid-result-matrix.py" <<'PY'
#!/usr/bin/env python3
import pathlib
import sys
args = sys.argv[1:]
pathlib.Path(args[args.index("--out") + 1]).write_text("not-json\n")
PY
chmod +x "$TMP/bin/invalid-result-matrix.py"
printf 'baseline unit\n' > "$TMP/home/.config/systemd/user/qwen-builder.service"
: > "$CALLS"
OUT=$(env "${COMMON[@]}" QWEN_MATRIX_PY="$TMP/bin/invalid-result-matrix.py" \
  bash "$RUNNER" POSTPROCESS_FAIL -- QWEN_CACHE_RAM=32768 2>&1); rc=$?
[ "$rc" -eq 7 ] && [ -s "$TMP/matrix/POSTPROCESS_FAIL/result.json" ] && \
  grep -qx 'result post-processing failed' "$TMP/matrix/POSTPROCESS_FAIL/run-error" && \
  [ ! -e "$TMP/matrix/POSTPROCESS_FAIL/run-complete" ] && \
  [ "$(sha256sum "$TMP/home/.config/systemd/user/qwen-builder.service" | cut -d' ' -f1)" = "$BASELINE_SHA" ]
check "failed result post-processing restores baseline and leaves no completion record" $? "rc=$rc: $OUT"

cat > "$TMP/bin/signal-matrix.py" <<'PY'
#!/usr/bin/env python3
import os
import signal
os.kill(os.getppid(), signal.SIGTERM)
raise SystemExit(0)
PY
chmod +x "$TMP/bin/signal-matrix.py"
printf 'baseline unit\n' > "$TMP/home/.config/systemd/user/qwen-builder.service"
: > "$CALLS"
OUT=$(env "${COMMON[@]}" QWEN_MATRIX_PY="$TMP/bin/signal-matrix.py" \
  bash "$RUNNER" SIGNAL_FAIL -- QWEN_CACHE_RAM=32768 2>&1); rc=$?
[ "$rc" -eq 143 ] && [ ! -e "$TMP/matrix/SIGNAL_FAIL/run-complete" ] && \
  [ "$(sha256sum "$TMP/home/.config/systemd/user/qwen-builder.service" | cut -d' ' -f1)" = "$BASELINE_SHA" ]
check "TERM interruption restores baseline and leaves no completion record" $? "rc=$rc: $OUT"

# AF-AP-145 (task #176): a SECOND signal while cleanup runs must change nothing. The load generator
# sends the first signal to the runner and starts a helper that sends TERM again 0.3 s later; the
# padded baseline env (300,000 comment lines, about a second of bash-only reading in the sandbox)
# holds cleanup in the step BEFORE the restore, so a second signal that kills bash there leaves the
# cell unit installed. The status must stay the first signal's (130 for INT, 143 for TERM), or the
# run's own failure status (7) when the load generator fails and the only signal is the helper's.
cat > "$TMP/bin/signal2-matrix.py" <<'PY'
#!/usr/bin/env python3
import os
import signal
import subprocess
ppid = os.getppid()
subprocess.Popen(["bash", "-c", f"sleep 0.3; kill -TERM {ppid}"], start_new_session=True)
if os.environ["QM_FIRST_SIGNAL"] == "NONE":  # the run fails on its own: cleanup's own ignore is the guard
    raise SystemExit(1)
os.kill(ppid, getattr(signal, os.environ["QM_FIRST_SIGNAL"]))
raise SystemExit(0)
PY
chmod +x "$TMP/bin/signal2-matrix.py"
python3 -c "import sys; open(sys.argv[1], 'w').write('# padding\n' * 300000 + 'QWEN_CACHE_RAM=8192\n')" \
  "$TMP/matrix/baseline/env-padded"
for first in SIGTERM:143 SIGINT:130 NONE:7; do
  printf 'baseline unit\n' > "$TMP/home/.config/systemd/user/qwen-builder.service"; : > "$CALLS"
  OUT=$(env "${COMMON[@]}" QWEN_MATRIX_PY="$TMP/bin/signal2-matrix.py" QM_FIRST_SIGNAL="${first%%:*}" \
    QWEN_MATRIX_BASELINE_ENV="$TMP/matrix/baseline/env-padded" \
    bash "$RUNNER" "SECOND_${first%%:*}" -- QWEN_CACHE_RAM=32768 2>&1); rc=$?
  [ "$rc" -eq "${first##*:}" ] && [ ! -e "$TMP/matrix/SECOND_${first%%:*}/run-complete" ] && \
    [ "$(sha256sum "$TMP/home/.config/systemd/user/qwen-builder.service" | cut -d' ' -f1)" = "$BASELINE_SHA" ]
  check "a TERM during cleanup after ${first%%:*} still restores the baseline (rc ${first##*:})" $? \
    "rc=$rc unit=$(cat "$TMP/home/.config/systemd/user/qwen-builder.service") calls=$(tr '\n' ';' < "$CALLS"): $OUT"
done

# Initially absent is a distinct baseline state: success and failure must both remove the created unit.
rm -f "$TMP/home/.config/systemd/user/qwen-builder.service"; : > "$CALLS"
OUT=$(env "${COMMON[@]}" bash "$RUNNER" ABSENT_OK -- QWEN_CACHE_RAM=32768 2>&1); rc=$?
[ "$rc" -eq 0 ] && [ ! -e "$TMP/home/.config/systemd/user/qwen-builder.service" ] && grep -qx 'uninstall QWEN_CACHE_RAM=32768' "$CALLS"
check "successful cell restores an initially absent unit to absent" $? "rc=$rc calls=$(tr '\n' ';' < "$CALLS"): $OUT"

rm -f "$TMP/home/.config/systemd/user/qwen-builder.service"; : > "$CALLS"
OUT=$(env "${COMMON[@]}" QWEN_MATRIX_PY="$TMP/bin/fail-matrix.py" bash "$RUNNER" ABSENT_FAIL -- QWEN_CACHE_RAM=32768 2>&1); rc=$?
[ "$rc" -eq 7 ] && [ ! -e "$TMP/home/.config/systemd/user/qwen-builder.service" ] && grep -qx 'uninstall QWEN_CACHE_RAM=32768' "$CALLS"
check "failed cell restores an initially absent unit to absent" $? "rc=$rc calls=$(tr '\n' ';' < "$CALLS"): $OUT"

rm -f "$TMP/home/.config/systemd/user/qwen-builder.service"; : > "$CALLS"
OUT=$(env "${COMMON[@]}" QWEN_MATRIX_PY="$TMP/bin/fail-matrix.py" QM_UNINSTALL_LEAVES_UNIT=1 \
  bash "$RUNNER" ABSENT_BROKEN -- QWEN_CACHE_RAM=32768 2>&1); rc=$?
[ "$rc" -eq 8 ] && [ -e "$TMP/home/.config/systemd/user/qwen-builder.service" ] && \
  case "$OUT" in *"initially absent unit remains after restore"*) true;; *) false;; esac
check "failed absence restore is detected with rc 8" $? "rc=$rc calls=$(tr '\n' ';' < "$CALLS"): $OUT"
printf 'baseline unit\n' > "$TMP/home/.config/systemd/user/qwen-builder.service"

# Domain control: only QWEN_NAME=value is accepted.
OUT=$(env "${COMMON[@]}" bash "$RUNNER" bad -- NOT_QWEN=1 2>&1); rc=$?
[ "$rc" -eq 64 ] && case "$OUT" in *"override must be QWEN_NAME=value"*) true;; *) false;; esac
check "non-QWEN override is refused with rc 64" $? "rc=$rc: $OUT"

echo
echo "qwen-matrix-sh: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
