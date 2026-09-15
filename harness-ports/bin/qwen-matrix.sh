#!/usr/bin/env bash
# qwen-matrix.sh — run one L1 matrix cell, then restore the baseline unit on every exit.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QWEN_SERVER="${QWEN_MATRIX_SERVER:-$HERE/qwen-server.sh}"
QWEN_MATRIX_PY="${QWEN_MATRIX_PY:-$HERE/qwen_matrix.py}"
QWEN_MATRIX_ROOT="${QWEN_MATRIX_ROOT:-$HOME/qwen-builder/matrix}"
QWEN_MATRIX_PROMPTS="${QWEN_MATRIX_PROMPTS:-$HOME/qwen-builder/matrix/prompts}"
QWEN_MATRIX_CONCURRENCY="${QWEN_MATRIX_CONCURRENCY:-2}"
QWEN_MATRIX_ROUNDS="${QWEN_MATRIX_ROUNDS:-1}"
QWEN_MATRIX_MAX_TOKENS="${QWEN_MATRIX_MAX_TOKENS:-1000}"
QWEN_MATRIX_HEALTH_WAIT_S="${QWEN_MATRIX_HEALTH_WAIT_S:-180}"
QWEN_MATRIX_GPU_INTERVAL_S="${QWEN_MATRIX_GPU_INTERVAL_S:-5}"
QWEN_MATRIX_UNIT_PATH="${QWEN_MATRIX_UNIT_PATH:-$HOME/.config/systemd/user/qwen-builder.service}"
QWEN_MATRIX_BASELINE_ENV="${QWEN_MATRIX_BASELINE_ENV:-$HOME/qwen-builder/matrix/baseline/env}"
PYTHON="${QWEN_MATRIX_PYTHON:-python3}"

fail() { echo "qwen-matrix: $*" >&2; exit "${2:-1}"; }
valid_int() { [[ "$2" =~ ^[1-9][0-9]*$ ]] || fail "$1 must be a positive integer (got ${2@Q})" 64; }

usage() {
  echo "usage: qwen-matrix.sh <cell-name> -- [QWEN_NAME=value ...]" >&2
  exit 64
}

[ "$#" -ge 2 ] || usage
CELL=$1; shift
[ "$1" = -- ] || usage
shift
[[ "$CELL" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || fail "unsafe cell name: ${CELL@Q}" 64
valid_int QWEN_MATRIX_CONCURRENCY "$QWEN_MATRIX_CONCURRENCY"
valid_int QWEN_MATRIX_ROUNDS "$QWEN_MATRIX_ROUNDS"
valid_int QWEN_MATRIX_MAX_TOKENS "$QWEN_MATRIX_MAX_TOKENS"
valid_int QWEN_MATRIX_HEALTH_WAIT_S "$QWEN_MATRIX_HEALTH_WAIT_S"
valid_int QWEN_MATRIX_GPU_INTERVAL_S "$QWEN_MATRIX_GPU_INTERVAL_S"

OVERRIDES=()
for assignment in "$@"; do
  case "$assignment" in
    QWEN_[A-Z0-9_]*=*) OVERRIDES+=("$assignment");;
    *) fail "override must be QWEN_NAME=value (got ${assignment@Q})" 64;;
  esac
done

[ -x "$QWEN_SERVER" ] || fail "server launcher is not executable: $QWEN_SERVER" 2
[ -f "$QWEN_MATRIX_PY" ] || fail "load generator is absent: $QWEN_MATRIX_PY" 2
[ -d "$QWEN_MATRIX_PROMPTS" ] || fail "prompt directory is absent: $QWEN_MATRIX_PROMPTS" 2

# The launcher owns route classification. The runner never copies or weakens this guard.
GUARD_OUT=$(env "${OVERRIDES[@]}" bash "$QWEN_SERVER" guard); GUARD_RC=$?
[ -z "$GUARD_OUT" ] || printf '%s\n' "$GUARD_OUT"
[ "$GUARD_RC" -eq 0 ] || fail "qwen-server guard refused cell $CELL" "$GUARD_RC"

CELL_DIR="$QWEN_MATRIX_ROOT/$CELL"
[ ! -e "$CELL_DIR" ] || fail "cell directory already exists; choose a new cell name: $CELL_DIR" 3
mkdir -p "$CELL_DIR" || fail "cannot create cell directory: $CELL_DIR" 3
ENV_FILE="$CELL_DIR/env"
ARGV_FILE="$CELL_DIR/argv.txt"
RESULT_FILE="$CELL_DIR/result.json"
PEAK_FILE="$CELL_DIR/vram-peak-mib"
UNIT_TEXT_FILE="$CELL_DIR/unit-text"
RUN_COMPLETE="$CELL_DIR/run-complete"
RUN_ERROR="$CELL_DIR/run-error"
RUN_ID=$("$PYTHON" -c 'import secrets; print(secrets.token_hex(32))') || fail "cannot generate run id" 3
[[ "$RUN_ID" =~ ^[0-9a-f]{64}$ ]] || fail "generated run id is not lowercase sha256-shaped" 3
: > "$ENV_FILE"
for assignment in "${OVERRIDES[@]}"; do printf '%s\n' "$assignment" >> "$ENV_FILE"; done
# Bind the execution controls too; they are matrix inputs even though qwen-server does not consume them.
printf '%s\n' "QWEN_MATRIX_CONCURRENCY=$QWEN_MATRIX_CONCURRENCY" \
  "QWEN_MATRIX_ROUNDS=$QWEN_MATRIX_ROUNDS" "QWEN_MATRIX_MAX_TOKENS=$QWEN_MATRIX_MAX_TOKENS" >> "$ENV_FILE"

env "${OVERRIDES[@]}" bash "$QWEN_SERVER" argv > "$ARGV_FILE" || fail "cell argv did not render" 3
env "${OVERRIDES[@]}" bash "$QWEN_SERVER" unit > "$UNIT_TEXT_FILE" || fail "cell unit did not render" 3
UNIT_SHA=$(sha256sum "$UNIT_TEXT_FILE" | cut -d' ' -f1)
printf '%s\n' "$UNIT_SHA" > "$CELL_DIR/unit-sha256"
if [ ! -s "$QWEN_MATRIX_BASELINE_ENV" ]; then
  # The baseline is the launcher's measured defaults, never this cell's overrides.
  : > "$QWEN_MATRIX_BASELINE_ENV.tmp"
  grep -q '^QWEN_CACHE_RAM=' "$QWEN_MATRIX_BASELINE_ENV.tmp" || printf 'QWEN_CACHE_RAM=8192\n' >> "$QWEN_MATRIX_BASELINE_ENV.tmp"
  grep -q '^QWEN_SPEC_TYPE=' "$QWEN_MATRIX_BASELINE_ENV.tmp" || printf 'QWEN_SPEC_TYPE=draft-mtp\n' >> "$QWEN_MATRIX_BASELINE_ENV.tmp"
  mv "$QWEN_MATRIX_BASELINE_ENV.tmp" "$QWEN_MATRIX_BASELINE_ENV"
fi

if [ -f "$QWEN_MATRIX_UNIT_PATH" ]; then
  BASELINE_SHA=$(sha256sum "$QWEN_MATRIX_UNIT_PATH" | cut -d' ' -f1)
else
  BASELINE_SHA=absent
fi
printf '%s\n' "$BASELINE_SHA" > "$CELL_DIR/baseline-unit-sha256"

RESTORE_NEEDED=0
GPU_PID=""
cleanup() {
  local rc=$?
  trap - EXIT INT TERM
  if [ -n "$GPU_PID" ]; then
    kill "$GPU_PID" 2>/dev/null || true
    wait "$GPU_PID" 2>/dev/null || true
  fi
  if [ "$RESTORE_NEEDED" -eq 1 ]; then
    if [ "$BASELINE_SHA" = absent ]; then
      # Restore absence through the launcher's lifecycle seam; direct rm/systemctl here would
      # duplicate that ownership boundary. The launcher repeats its guard immediately pre-write.
      env "${OVERRIDES[@]}" bash "$QWEN_SERVER" uninstall || rc=8
      if [ -e "$QWEN_MATRIX_UNIT_PATH" ]; then
        echo "qwen-matrix: initially absent unit remains after restore" >&2
        rc=8
      fi
    else
      restore_args=()
      if [ -s "$QWEN_MATRIX_BASELINE_ENV" ]; then
        while IFS= read -r line || [ -n "$line" ]; do
          [ -z "$line" ] || case "$line" in \#*) ;; QWEN_[A-Z0-9_]*=*) restore_args+=("$line");; *) echo "qwen-matrix: invalid baseline env line: ${line@Q}" >&2; rc=8;; esac
        done < "$QWEN_MATRIX_BASELINE_ENV"
      fi
      if [ "$rc" -ne 8 ]; then
        env "${restore_args[@]}" bash "$QWEN_SERVER" install || rc=8
        if [ ! -f "$QWEN_MATRIX_UNIT_PATH" ]; then
          echo "qwen-matrix: baseline unit restore missing" >&2
          rc=8
        elif [ "$(sha256sum "$QWEN_MATRIX_UNIT_PATH" | cut -d' ' -f1)" != "$BASELINE_SHA" ]; then
          echo "qwen-matrix: baseline unit sha mismatch after restore" >&2
          rc=8
        fi
      fi
    fi
  fi
  if [ "$rc" -eq 0 ]; then
    printf '%s\n' "$RUN_ID" > "$RUN_COMPLETE.tmp" || rc=8
    if [ "$rc" -eq 0 ]; then
      mv "$RUN_COMPLETE.tmp" "$RUN_COMPLETE" || rc=8
    fi
  fi
  exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# install is the launcher's only persistent cell path. The guard above is intentionally before it;
# install repeats the guard at its own pre-write boundary.
RESTORE_NEEDED=1
env "${OVERRIDES[@]}" bash "$QWEN_SERVER" install || fail "cell install failed" 5

healthy=0
for _ in $(seq 1 "$QWEN_MATRIX_HEALTH_WAIT_S"); do
  if env "${OVERRIDES[@]}" bash "$QWEN_SERVER" health >/dev/null 2>&1; then healthy=1; break; fi
  sleep 1
done
[ "$healthy" -eq 1 ] || fail "cell $CELL did not become healthy within ${QWEN_MATRIX_HEALTH_WAIT_S}s" 6

sample_gpu() {
  local peak=0 value
  while :; do
    value=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | sort -nr | sed -n '1p') || value=
    if [[ "$value" =~ ^[0-9]+$ ]] && [ "$value" -gt "$peak" ]; then peak=$value; printf '%s\n' "$peak" > "$PEAK_FILE"; fi
    sleep "$QWEN_MATRIX_GPU_INTERVAL_S"
  done
}
if command -v nvidia-smi >/dev/null 2>&1; then sample_gpu & GPU_PID=$!; else printf '0\n' > "$PEAK_FILE"; fi

if ! QWEN_MATRIX_CELL="$CELL" "$PYTHON" "$QWEN_MATRIX_PY" run \
  --prompts "$QWEN_MATRIX_PROMPTS" --concurrency "$QWEN_MATRIX_CONCURRENCY" \
  --max-tokens "$QWEN_MATRIX_MAX_TOKENS" --rounds "$QWEN_MATRIX_ROUNDS" \
  --argv-file "$ARGV_FILE" --unit-sha-file "$CELL_DIR/unit-sha256" \
  --unit-text-file "$UNIT_TEXT_FILE" --run-id "$RUN_ID" --out "$RESULT_FILE"; then
  printf 'load generator failed\n' > "$RUN_ERROR"
  fail "load generator failed for cell $CELL" 7
fi
if [ -n "$GPU_PID" ]; then kill "$GPU_PID" 2>/dev/null || true; wait "$GPU_PID" 2>/dev/null || true; GPU_PID=""; fi
[ -s "$PEAK_FILE" ] || printf '0\n' > "$PEAK_FILE"

if ! "$PYTHON" - "$RESULT_FILE" "$PEAK_FILE" <<'PY'
import json
import pathlib
import sys
result = pathlib.Path(sys.argv[1])
data = json.loads(result.read_text())
data["vram_peak_mib"] = int(pathlib.Path(sys.argv[2]).read_text().strip())
result.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
PY
then
  printf 'result post-processing failed\n' > "$RUN_ERROR"
  fail "result post-processing failed for cell $CELL" 7
fi
printf 'qwen-matrix: cell %s recorded at %s; restoring baseline\n' "$CELL" "$RESULT_FILE"
