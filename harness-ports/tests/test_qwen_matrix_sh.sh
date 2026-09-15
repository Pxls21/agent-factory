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
    if [ "${QWEN_CACHE_RAM:-8192}" = 8192 ]; then printf 'baseline unit\n' > "$QWEN_MATRIX_UNIT_PATH"
    else printf 'cell unit %s\n' "$QWEN_CACHE_RAM" > "$QWEN_MATRIX_UNIT_PATH"; fi;;
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
out.write_text(json.dumps({
  "schema": "qwen-matrix-v1",
  "cell": {"name": __import__("os").environ["QWEN_MATRIX_CELL"],
           "argv_text": argv_file.read_text(), "argv_sha256": "fixture",
           "unit_sha256": unit_sha_file.read_text().strip(),
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
  grep -qx 'QWEN_MATRIX_CONCURRENCY=2' "$TMP/matrix/T/env" && [ -s "$TMP/matrix/T/argv.txt" ] && [ -s "$TMP/matrix/T/unit-sha256" ]
check "cell env, argv text, and unit sha are recorded" $? "$(tr '\n' ';' < "$TMP/matrix/T/env")"
python3 - "$TMP/matrix/T/result.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1])); assert d["cell"]["name"]=="T" and d["vram_peak_mib"]==1234
PY
check "result JSON carries cell identity and measured VRAM peak" $? "result.json decoded"

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

# Domain control: only QWEN_NAME=value is accepted.
OUT=$(env "${COMMON[@]}" bash "$RUNNER" bad -- NOT_QWEN=1 2>&1); rc=$?
[ "$rc" -eq 64 ] && case "$OUT" in *"override must be QWEN_NAME=value"*) true;; *) false;; esac
check "non-QWEN override is refused with rc 64" $? "rc=$rc: $OUT"

echo
echo "qwen-matrix-sh: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
