#!/usr/bin/env bash
# gpu_window.sh — run jobs on the PC's GPU inside a window with the vLLM `qwen` service stopped (D-078, D-081; task #242).
# Runs ON the PC. Refuses while any PC lane is live, or when the service is not active and answering to begin with; stops
# qwen.service; waits for the GPU to free; runs each job (one shell command per line of a jobs file) under ONE shared
# time budget; and ALWAYS starts qwen.service again (an EXIT trap; INT or TERM first stops the running job) and waits
# until its /v1/models answers. Start it DETACHED (setsid nohup) so the window closes even if the caller disappears.
# Every step is one JSON line in the record file. Only a SIGKILL skips the restart: then `systemctl --user start qwen`.
# Test seams: GPU_WINDOW_MAX_SECONDS (the job budget in seconds) and GPU_FREE_WAIT_SECONDS (default 180).
#   usage: gpu_window.sh [--max-minutes N] [--dry-run] <jobs-file>
#   exit: 0 every job rc 0 and the service back · 1 a job failed or timed out, the stop failed, or the GPU did not free
#         (the service back) · 3 a lane is live · 4 the service is not active or does not answer · 5 another window
#         holds the lock · 6 the service did not come back · 130 stopped by INT or TERM (the service back) · 64 usage
# The inference key is read from its file into a curl header file descriptor, never into argv (AF-AP-39).
set -uo pipefail
usage() { echo "usage: gpu_window.sh [--max-minutes N] [--dry-run] <jobs-file>" >&2; exit 64; }
MAX_MIN=60; DRY=0; JOBS=""
while [ $# -gt 0 ]; do
  case "$1" in
    --max-minutes) [ $# -ge 2 ] || usage; MAX_MIN="$2"; shift 2;;
    --dry-run) DRY=1; shift;;
    -h|--help) sed -n '2,13p' "$0"; exit 64;;
    -*) usage;;
    *) [ -z "$JOBS" ] || usage; JOBS="$1"; shift;;
  esac
done
case "$MAX_MIN" in ''|*[!0-9]*) echo "gpu_window: --max-minutes needs a whole number" >&2; exit 64;; esac
[ "$MAX_MIN" -ge 1 ] 2>/dev/null && [ "$MAX_MIN" -le 240 ] || { echo "gpu_window: --max-minutes must be 1-240" >&2; exit 64; }
[ -n "$JOBS" ] && [ -f "$JOBS" ] || usage
mapfile -t cmds < <(grep -v -E '^[[:space:]]*(#|$)' "$JOBS")
[ "${#cmds[@]}" -gt 0 ] || { echo "gpu_window: no jobs in $JOBS" >&2; exit 64; }

AF_REPO="${AF_REPO:-$HOME/agent-factory}"
KEY_FILE="${QWEN_KEY_FILE:-$HOME/.config/qwen-builder/api-key}"
MODELS_URL="${QWEN_MODELS_URL:-http://127.0.0.1:8080/v1/models}"
STATE="${GPU_WINDOW_DIR:-$HOME/gpu-window}"
UNIT="${QWEN_UNIT:-qwen}"
FREE_MIB="${GPU_FREE_MIB:-1500}"          # the window's GPU is free when memory.used is under this
BACK_S="${QWEN_BACK_SECONDS:-1200}"        # how long the service gets to answer /v1/models again
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
mkdir -p "$STATE"
REC="$STATE/record.jsonl"
TAG="$(date -u +%Y%m%dT%H%M%SZ)"
rec() { printf '{"ts":"%s","window":"%s","event":"%s"%s}\n' "$(date -u +%FT%TZ)" "$TAG" "$1" "${2:+,$2}" >> "$REC"; }

exec 9>"$STATE/lock"
flock -n 9 || { echo "gpu_window: another window holds $STATE/lock" >&2; exit 5; }

live=()                                     # fail closed: a pid file that holds no pid counts as live
for f in "$AF_REPO"/.lanes/*/lane.pid; do
  [ -f "$f" ] || continue
  p="$(tr -d '[:space:]' < "$f" 2>/dev/null)"
  if [[ "$p" =~ ^[1-9][0-9]*$ ]]; then kill -0 "$p" 2>/dev/null && live+=("$f")
  else live+=("$f (no pid in it)"); fi
done
if [ "${#live[@]}" -gt 0 ]; then
  echo "gpu_window: refusing, ${#live[@]} lane(s) live: ${live[*]}" >&2
  rec refused "\"reason\":\"lane live\",\"count\":${#live[@]}"
  exit 3
fi

models_answer() {                           # the key goes through a pipe as a header file, never argv
  [ -r "$KEY_FILE" ] || return 1
  curl -s -m 5 --noproxy '*' -o /dev/null -w '%{http_code}' \
    -H @<(printf 'Authorization: Bearer %s\n' "$(cat "$KEY_FILE")") "$MODELS_URL" 2>/dev/null | grep -qx 200
}
systemctl --user is-active --quiet "$UNIT" || { echo "gpu_window: $UNIT is not active; nothing to stop or restore" >&2
  rec refused '"reason":"service not active"'; exit 4; }
models_answer || { echo "gpu_window: $MODELS_URL does not answer 200 before the window (the URL or the key)" >&2
  rec refused '"reason":"service does not answer"'; exit 4; }

if [ "$DRY" = 1 ]; then
  echo "gpu_window: dry run: would stop $UNIT, run ${#cmds[@]} job(s) within $MAX_MIN min, start $UNIT, wait for $MODELS_URL"
  printf '  job: %s\n' "${cmds[@]}"
  exit 0
fi

restored=0
restore() {
  [ "$restored" = 1 ] && return
  restored=1
  systemctl --user start "$UNIT"; local src=$?
  rec start "\"rc\":$src"
  [ "$src" = 0 ] || echo "gpu_window: starting $UNIT returned rc $src; still waiting for $MODELS_URL" >&2
  local t0=$SECONDS
  until models_answer; do
    if [ $((SECONDS - t0)) -ge "$BACK_S" ]; then
      rec back '"ok":false'
      echo "gpu_window: $UNIT did not answer $MODELS_URL within ${BACK_S}s; check it: systemctl --user status $UNIT" >&2
      exit 6
    fi
    sleep 5
  done
  rec back "\"ok\":true,\"seconds\":$((SECONDS - t0))"
}
jobpid=""
abort() {                                   # stop the running job now; the EXIT trap then restores the service
  rec abort "\"signal\":\"$1\""
  if [ -n "$jobpid" ]; then kill -TERM "$jobpid" 2>/dev/null; wait "$jobpid" 2>/dev/null; fi
  exit 130
}
trap 'restore' EXIT
trap 'abort INT' INT
trap 'abort TERM' TERM

rec open "\"jobs\":${#cmds[@]},\"max_minutes\":$MAX_MIN"
systemctl --user stop "$UNIT"; src=$?
rec stop "\"rc\":$src"
[ "$src" = 0 ] || { echo "gpu_window: stopping $UNIT failed (rc $src)" >&2; exit 1; }
t0=$SECONDS
while :; do
  used="$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -dc 0-9)"
  [ -n "$used" ] && [ "$used" -lt "$FREE_MIB" ] && break
  if [ $((SECONDS - t0)) -ge "${GPU_FREE_WAIT_SECONDS:-180}" ]; then
    rec gpu_busy "\"used_mib\":\"${used:-?}\""; echo "gpu_window: the GPU did not free (used ${used:-?} MiB)" >&2; exit 1
  fi
  sleep 3
done
rec gpu_free "\"used_mib\":$used"

deadline=$((SECONDS + ${GPU_WINDOW_MAX_SECONDS:-$((MAX_MIN * 60))})); worst=0; n=0
for c in "${cmds[@]}"; do
  n=$((n + 1)); left=$((deadline - SECONDS))
  if [ "$left" -le 0 ]; then rec job "\"n\":$n,\"skipped\":\"no time left\""; worst=1; continue; fi
  log="$STATE/$TAG-job$n.log"; s=$SECONDS
  timeout --kill-after=30 "$left" bash -c "$c" > "$log" 2>&1 < /dev/null &   # in the background, so a signal
  jobpid=$!                                                                  # interrupts the wait at once
  wait "$jobpid"; rc=$?; jobpid=""
  rec job "\"n\":$n,\"rc\":$rc,\"seconds\":$((SECONDS - s)),\"log\":\"$log\""
  [ "$rc" = 0 ] || worst=1
done
restore
rec close "\"rc\":$worst"
exit "$worst"
