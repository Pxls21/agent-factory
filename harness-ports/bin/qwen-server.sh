#!/usr/bin/env bash
# qwen-server.sh — the LOCAL BUILD-LANE MODEL as a user service on the PC (owner ask 2026-09-14: "let's get
# Qwen to do the heavy lifting"): Qwen3.8-27B UD-IQ4_XS on the June CUDA llama.cpp build, fully resident on
# the 3090, MTP on, the full 262k context split over four slots — the shape MEASURED in
# docs/research/FINDINGS-LOCAL-BUILDER-QWEN38.md §6 (2026-09-14). It listens on loopback only, behind an API
# key that ONLY OmniRoute reads (project rule 3: OmniRoute is the sole model egress — Hermes never talks to
# this port directly; harness-ports/bin/omniroute_local_builder.py wires the provider node + combo).
#
#   harness-ports/bin/qwen-server.sh argv|unit|keygen|guard|install|restart-when-idle|start|stop|restart|status|health|probe|uninstall
#
#   argv      print the llama-server argv (one token per line) — the testable surface
#   unit      print the systemd --user unit text
#   keygen    create the API key file (0600, 64 hex) if absent; the value is never printed
#   guard     report live lane routes; rc 7 when a local-route lane makes a service change unsafe
#   install   guard before writes, verify binary + model, write/enable the unit, wait for /health
#   restart-when-idle [--max-wait S] [--poll S] — queue a unit change until every server consumer is idle
#   status    unit state + served model + pending restart state (no key ever printed)
#   health    rc 0 iff /health is ok AND /v1/models lists the alias
#   probe     one content-gated completion through the server; prints model id + timings
#
# Every knob is an env override with the measured default (never edit the defaults in place — re-measure).
set -uo pipefail

QWEN_LLAMA_SERVER="${QWEN_LLAMA_SERVER:-$HOME/Desktop/projects/llama-cpp/llama.cpp-mtp/build/bin/llama-server}"
QWEN_MODEL_GGUF="${QWEN_MODEL_GGUF:-}"   # resolved from the HF cache snapshot when empty
QWEN_MODEL_REPO_DIR="${QWEN_MODEL_REPO_DIR:-$HOME/.cache/huggingface/hub/models--unsloth--Qwen3.8-27B-GGUF}"
QWEN_MODEL_FILE="${QWEN_MODEL_FILE:-Qwen3.8-27B-UD-IQ4_XS.gguf}"
# The HF blob name IS the sha256 of the bytes (verified 2026-09-14: blob 40fac405…, 14,252,845,984 bytes).
QWEN_MODEL_SHA256="${QWEN_MODEL_SHA256:-40fac4050e940397dbf13087afd50f4734a11805bf9d65ef8ddd7483470e6199}"
QWEN_ALIAS="${QWEN_ALIAS:-qwen3.8-27b-local}"
QWEN_HOST="${QWEN_HOST:-127.0.0.1}"
QWEN_PORT="${QWEN_PORT:-8080}"
QWEN_CTX="${QWEN_CTX:-262144}"
QWEN_SLOTS="${QWEN_SLOTS:-1}"            # ONE slot = the whole 262k context per lane. The first lane (N5k, 2026-09-14) grew
                                         # to 97-104k tokens in 8 min and overflowed a 65k slot (-np 4) four times; Hermes
                                         # compacts at 75 % of the 200k OmniRoute reports for the combo, so a slot must hold
                                         # >= 200k. Parallel lanes need a Hermes-side context cap first (a follow-up).
QWEN_NGL="${QWEN_NGL:-99}"               # everything resident: the brief's -ngl 54 offload measured 7.0x slower
QWEN_KV_TYPE="${QWEN_KV_TYPE:-q4_0}"
QWEN_MTP_N_EXPLICIT="${QWEN_MTP_N+x}"
QWEN_MTP_N="${QWEN_MTP_N:-3}"            # draft-mtp n=3: 86.9 t/s at 90 % acceptance on code (n=2: 79.9)
QWEN_EFFORT="${QWEN_EFFORT:-medium}"     # the server-side default; a request's own reasoning_effort wins
QWEN_CACHE_REUSE="${QWEN_CACHE_REUSE:-256}"
QWEN_CACHE_RAM="${QWEN_CACHE_RAM:-8192}"       # MiB; rendered so a saved unit identifies the matrix cell
QWEN_CTXCP="${QWEN_CTXCP:-}"
QWEN_CMS="${QWEN_CMS:-}"
QWEN_UBATCH="${QWEN_UBATCH:-}"
QWEN_SPEC_P_MIN="${QWEN_SPEC_P_MIN:-}"
QWEN_SPEC_TYPE="${QWEN_SPEC_TYPE-draft-mtp}"  # the matrix admits only draft-mtp, none and ngram-mod
QWEN_KEY_FILE="${QWEN_KEY_FILE:-$HOME/.config/qwen-builder/api-key}"
QWEN_UNIT="${QWEN_UNIT:-qwen-builder}"
QWEN_HOME="${QWEN_HOME:-$HOME/qwen-builder}"
QWEN_HEALTH_WAIT_S="${QWEN_HEALTH_WAIT_S:-180}"
QWEN_LANES_DIR="${QWEN_LANES_DIR:-$HOME/agent-factory/.lanes}"
QWEN_PROC_ROOT="${QWEN_PROC_ROOT:-/proc}"       # tests point this at a fixture only for unreadable-environ failure
QWEN_PENDING_MAX_WAIT="${QWEN_PENDING_MAX_WAIT:-28800}" # 8 h
QWEN_PENDING_POLL="${QWEN_PENDING_POLL:-30}"
QWEN_PENDING_DIR="$QWEN_HOME/pending"
QWEN_PENDING_ENV="$QWEN_PENDING_DIR/env"
QWEN_PENDING_PID="$QWEN_PENDING_DIR/watcher.pid"
QWEN_PENDING_STATE="$QWEN_PENDING_DIR/state"
QWEN_DEFERRED_LOG="$QWEN_HOME/logs/deferred-restart.log"
QWEN_MATRIX_LOCK="$QWEN_HOME/matrix/.cell.lock"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"

die() { echo "qwen-server: $*" >&2; exit "${2:-1}"; }

resolve_model() {
  if [ -n "$QWEN_MODEL_GGUF" ]; then printf '%s\n' "$QWEN_MODEL_GGUF"; return; fi
  local m
  m=$(ls -d "$QWEN_MODEL_REPO_DIR"/snapshots/*/"$QWEN_MODEL_FILE" 2>/dev/null | head -1)
  printf '%s\n' "$m"
}

validate_knobs() {
  local name value
  for name in QWEN_CACHE_RAM QWEN_CTXCP QWEN_CMS QWEN_UBATCH; do
    value=${!name}
    [ -z "$value" ] || [[ "$value" =~ ^[1-9][0-9]*$ ]] || die "$name must be a positive integer (got ${value@Q})" 3
  done
  if [ -n "$QWEN_SPEC_P_MIN" ]; then
    python3 - "$QWEN_SPEC_P_MIN" <<'PY' || die "QWEN_SPEC_P_MIN must be a finite number in [0,1] (got ${QWEN_SPEC_P_MIN@Q})" 3
import math
import sys
try:
    value = float(sys.argv[1])
except ValueError:
    raise SystemExit(1)
raise SystemExit(0 if math.isfinite(value) and 0 <= value <= 1 else 1)
PY
  fi
  case "$QWEN_SPEC_TYPE" in
    draft-mtp|none|ngram-mod) ;;
    *) die "QWEN_SPEC_TYPE must be one of draft-mtp, none, ngram-mod (got ${QWEN_SPEC_TYPE@Q})" 3;;
  esac
  [ "$QWEN_SPEC_TYPE" = draft-mtp ] || [ -z "$QWEN_MTP_N_EXPLICIT" ] || \
    die "QWEN_MTP_N applies only to QWEN_SPEC_TYPE=draft-mtp" 3
}

argv() {
  validate_knobs
  local model; model=$(resolve_model)
  printf '%s\n' "$QWEN_LLAMA_SERVER" \
    -m "$model" \
    --alias "$QWEN_ALIAS" \
    --host "$QWEN_HOST" --port "$QWEN_PORT" \
    --api-key-file "$QWEN_KEY_FILE" \
    -ngl "$QWEN_NGL" -c "$QWEN_CTX" -fa on -ctk "$QWEN_KV_TYPE" -ctv "$QWEN_KV_TYPE" \
    -np "$QWEN_SLOTS" --cache-reuse "$QWEN_CACHE_REUSE" \
    --cache-ram "$QWEN_CACHE_RAM"
  [ -z "$QWEN_CTXCP" ] || printf '%s\n' -ctxcp "$QWEN_CTXCP"
  [ -z "$QWEN_CMS" ] || printf '%s\n' -cms "$QWEN_CMS"
  [ -z "$QWEN_UBATCH" ] || printf '%s\n' -ub "$QWEN_UBATCH"
  [ -z "$QWEN_SPEC_P_MIN" ] || printf '%s\n' --spec-draft-p-min "$QWEN_SPEC_P_MIN"
  case "$QWEN_SPEC_TYPE" in
    draft-mtp) printf '%s\n' --spec-type draft-mtp --spec-draft-n-max "$QWEN_MTP_N";;
    ngram-mod) printf '%s\n' --spec-type ngram-mod;;
    none) ;;
  esac
  printf '%s\n' \
    --jinja --chat-template-kwargs "{\"reasoning_effort\":\"$QWEN_EFFORT\"}" \
    --metrics --slots
}

sd_quote() {
  # systemd's ExecStart is NOT a shell: bash's %q form (\{ \}) is an unknown escape it keeps verbatim (the
  # "Invalid escape sequences in line, correcting" warning) and llama-server would then see broken JSON. Use
  # systemd.syntax(7) quoting: double quotes, \\ and \" escaped, a literal $ as $$ and a literal % as %%.
  local s=$1
  s=${s//\\/\\\\}; s=${s//\"/\\\"}; s=${s//\$/\$\$}; s=${s//%/%%}
  printf '"%s"' "$s"
}

unit() {
  # Process-substitution failures do not set the while loop's status, so validate in this shell too.
  validate_knobs
  local exec="" tok
  while IFS= read -r tok; do exec+="$(sd_quote "$tok") "; done < <(argv)
  cat <<EOF
[Unit]
Description=Qwen3.8-27B local build-lane model (llama-server, loopback, API-keyed; FINDINGS-LOCAL-BUILDER-QWEN38 §6)
StartLimitIntervalSec=300
StartLimitBurst=3

[Service]
Type=simple
WorkingDirectory=$QWEN_HOME
ExecStart=${exec% }
Restart=on-failure
RestartSec=5
TimeoutStopSec=30
StandardOutput=append:$QWEN_HOME/logs/server.log
StandardError=append:$QWEN_HOME/logs/server.log

[Install]
WantedBy=default.target
EOF
}

keygen() {
  if [ -s "$QWEN_KEY_FILE" ]; then echo "qwen-server: key file present ($QWEN_KEY_FILE)"; return 0; fi
  mkdir -p "$(dirname "$QWEN_KEY_FILE")" && chmod 700 "$(dirname "$QWEN_KEY_FILE")"
  ( umask 077; openssl rand -hex 32 > "$QWEN_KEY_FILE" ) || die "keygen failed" 4
  chmod 600 "$QWEN_KEY_FILE"
  echo "qwen-server: key file created ($QWEN_KEY_FILE, 0600); the value is never printed"
}

guard() {
  local f pid route environ model
  local local_live=0
  for f in "$QWEN_LANES_DIR"/*/lane.pid; do
    [ -f "$f" ] || continue
    pid=$(cat "$f" 2>/dev/null || true)
    if ! [[ "$pid" =~ ^[1-9][0-9]*$ ]] || ! kill -0 "$pid" 2>/dev/null; then
      printf '%s %s stale\n' "$f" "${pid:-<empty>}"
      continue
    fi
    environ="$QWEN_PROC_ROOT/$pid/environ"
    if [ ! -r "$environ" ]; then
      route=LOCAL
    else
      model=$(tr '\0' '\n' < "$environ" 2>/dev/null | awk -F= '$1 == "HERMES_MODEL" && !found {sub(/^[^=]*=/, ""); value=$0; found=1} END {if (found) print value}') || model=
      case "$model" in
        *-local) route=LOCAL;;
        '') route=LOCAL;;
        *) route=CLOUD;;
      esac
    fi
    printf '%s %s %s\n' "$f" "$pid" "$route"
    [ "$route" != LOCAL ] || local_live=1
  done
  [ "$local_live" -eq 0 ] && return 0
  return 7
}

guard_or_die() {
  local out rc
  out=$(guard); rc=$?
  [ -z "$out" ] || printf '%s\n' "$out"
  [ "$rc" -eq 0 ] || die "a local-route lane is alive — service change refused" "$rc"
}

verify_inputs() {
  [ -x "$QWEN_LLAMA_SERVER" ] || die "llama-server binary absent or not executable: $QWEN_LLAMA_SERVER" 2
  local model; model=$(resolve_model)
  [ -n "$model" ] && [ -f "$model" ] || die "model GGUF absent under $QWEN_MODEL_REPO_DIR/snapshots/*/$QWEN_MODEL_FILE" 3
  local blob; blob=$(basename "$(readlink -f "$model")")
  [ "$blob" = "$QWEN_MODEL_SHA256" ] || die "model identity mismatch: blob $blob, expected sha256 $QWEN_MODEL_SHA256" 3
  local magic; magic=$(head -c 4 "$model")
  [ "$magic" = "GGUF" ] || die "model file is not a GGUF (magic ${magic@Q})" 3
}

curl_key() { curl -s -m "${1:-5}" -H "Authorization: Bearer $(<"$QWEN_KEY_FILE")" "${@:2}"; }

health() {
  local h; h=$(curl -s -m 3 "http://$QWEN_HOST:$QWEN_PORT/health" 2>/dev/null)
  case "$h" in *'"ok"'*) ;; *) echo "qwen-server: /health not ok: ${h:-<no answer>}"; return 1;; esac
  local models; models=$(curl_key 5 "http://$QWEN_HOST:$QWEN_PORT/v1/models" 2>/dev/null)
  case "$models" in *"\"$QWEN_ALIAS\""*) echo "qwen-server: healthy — /v1/models lists $QWEN_ALIAS"; return 0;;
    *) echo "qwen-server: /v1/models does not list $QWEN_ALIAS: ${models:0:200}"; return 1;; esac
}

wait_health() {
  local i; for i in $(seq 1 "$((QWEN_HEALTH_WAIT_S / 3))"); do
    if health >/dev/null 2>&1; then health; return 0; fi
    systemctl --user is-active --quiet "$QWEN_UNIT" || { echo "qwen-server: unit $QWEN_UNIT is not active" >&2; systemctl --user status "$QWEN_UNIT" --no-pager | tail -5 >&2; return 1; }
    sleep 3
  done
  echo "qwen-server: no healthy answer within ${QWEN_HEALTH_WAIT_S}s" >&2; return 1
}

install() {
  local unit_path="$HOME/.config/systemd/user/$QWEN_UNIT.service"
  local candidate changed=1 was_active=0
  validate_knobs
  candidate=$(unit) || exit $?
  if [ -f "$unit_path" ] && printf '%s\n' "$candidate" | cmp -s - "$unit_path"; then changed=0; fi
  if [ "$changed" -eq 0 ] && [ "${QWEN_PENDING_FORCE_RESTART:-0}" != 1 ]; then
    verify_inputs
    echo "qwen-server: unit $QWEN_UNIT unchanged; no service change needed"
    return 0
  fi
  guard_or_die
  verify_inputs
  # This observation is intentionally after the pre-write guard: it decides whether a changed running unit needs restart.
  systemctl --user is-active --quiet "$QWEN_UNIT" >/dev/null 2>&1 && was_active=1
  mkdir -p "$QWEN_HOME/logs" "$HOME/.config/systemd/user"
  keygen
  printf '%s\n' "$candidate" > "$unit_path"
  systemd-analyze --user verify "$unit_path" || die "unit does not verify (systemd-analyze)" 5
  systemctl --user daemon-reload || die "daemon-reload failed" 5
  systemctl --user enable --now "$QWEN_UNIT" >/dev/null 2>&1 || die "enable --now $QWEN_UNIT failed" 5
  if [ "$changed" -eq 1 ] && [ "$was_active" -eq 1 ]; then
    echo "qwen-server: unit text changed and the unit is running — restarting it"
    systemctl --user restart "$QWEN_UNIT" || die "restart $QWEN_UNIT failed" 5
  fi
  echo "qwen-server: unit $QWEN_UNIT enabled; llama-server $("$QWEN_LLAMA_SERVER" --version 2>&1 | head -1); model blob $QWEN_MODEL_SHA256"
  wait_health
}

status_pending() {
  local env_sha since pid alive=dead last=none terminal
  if [ ! -f "$QWEN_PENDING_ENV" ]; then
    echo "qwen-server: pending restart: none"
    return
  fi
  env_sha=$(sha256sum "$QWEN_PENDING_ENV" | awk '{print substr($1,1,12)}')
  since=$(awk -F= '$1 == "since" {sub(/^[^=]*=/, ""); print; exit}' "$QWEN_PENDING_STATE" 2>/dev/null)
  last=$(awk -F= '$1 == "last" {sub(/^[^=]*=/, ""); print; exit}' "$QWEN_PENDING_STATE" 2>/dev/null)
  pid=$(cat "$QWEN_PENDING_PID" 2>/dev/null || true)
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null && [ ! -f "$QWEN_PENDING_DIR/watcher.rc" ]; then alive=alive; else pid=none; fi
  if [ "$alive" = dead ]; then
    terminal=$(awk -v sha="$env_sha" '$1 ~ /^(expired|failed)$/ && $0 ~ "env-sha=" sha {line=$0} END {print line}' "$QWEN_DEFERRED_LOG" 2>/dev/null)
    case "$terminal" in *blocked-by=*) last=${terminal##*blocked-by=};; failed\ *) last=failed;; esac
  fi
  echo "qwen-server: pending restart: env-sha=$env_sha since=${since:-unknown} watcher=$pid alive=$alive last=${last:-none}"
}

status() {
  systemctl --user is-enabled "$QWEN_UNIT" 2>/dev/null | sed 's/^/qwen-server: unit enabled=/'
  systemctl --user is-active "$QWEN_UNIT" 2>/dev/null | sed 's/^/qwen-server: unit active=/'
  loginctl show-user "$(id -un)" -p Linger 2>/dev/null | sed 's/^/qwen-server: user /'   # Linger=yes keeps the unit alive with no login session
  grep -o 'reasoning_effort[^}]*' "$HOME/.config/systemd/user/$QWEN_UNIT.service" 2>/dev/null | head -1 | sed 's/^/qwen-server: unit effort /'
  status_pending
  health || true
  command -v nvidia-smi >/dev/null && nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader | sed 's/^/qwen-server: gpu /'
}

pending_env_snapshot() {
  local name
  for name in QWEN_LLAMA_SERVER QWEN_MODEL_GGUF QWEN_MODEL_REPO_DIR QWEN_MODEL_FILE QWEN_MODEL_SHA256 QWEN_ALIAS \
              QWEN_HOST QWEN_PORT QWEN_CTX QWEN_SLOTS QWEN_NGL QWEN_KV_TYPE QWEN_MTP_N QWEN_EFFORT \
              QWEN_CACHE_REUSE QWEN_CACHE_RAM QWEN_CTXCP QWEN_CMS QWEN_UBATCH QWEN_SPEC_P_MIN QWEN_SPEC_TYPE \
              QWEN_KEY_FILE QWEN_UNIT QWEN_HOME QWEN_HEALTH_WAIT_S QWEN_LANES_DIR QWEN_PROC_ROOT \
      QWEN_TEST_METRIC_FILE QWEN_TEST_CALLS QWEN_TEST_ACTIVE_RC QWEN_TEST_ANALYZE_RC; do
    [ -v "$name" ] && printf '%s=%q\n' "$name" "${!name}"
  done
  printf 'QWEN_PENDING_FORCE_RESTART=%q\n' "${QWEN_PENDING_FORCE_RESTART:-0}"
}

pending_state() { # pending_state LAST_REASON
  local tmp="$QWEN_PENDING_STATE.tmp.$$"
  printf 'since=%s\nlast=%s\n' "${QWEN_PENDING_SINCE:-$(date -u +%Y-%m-%dT%H:%M:%SZ)}" "$1" > "$tmp"
  mv -f "$tmp" "$QWEN_PENDING_STATE"
}

pending_log() { # pending_log TERMINAL [DETAIL]
  mkdir -p "$QWEN_HOME/logs"
  printf '%s %s%s\n' "$1" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${2:+ $2}" >> "$QWEN_DEFERRED_LOG"
}

pending_log_for_env() { # pending_log_for_env TERMINAL ENV_SHA [DETAIL]
  local terminal=$1 env_sha=$2 detail=${3:-}
  pending_log "$terminal" "env-sha=$env_sha${detail:+ $detail}"
}

pending_guard_reason() {
  local out rc
  out=$(guard); rc=$?
  if [ "$rc" -ne 0 ]; then
    printf 'local lane %s\n' "$(printf '%s\n' "$out" | awk '$3 == "LOCAL" {print $1; exit}')"
    return
  fi
  [ ! -e "$QWEN_MATRIX_LOCK" ] || { echo "matrix cell"; return; }
  local metrics value
  metrics=$(curl_key 5 "http://$QWEN_HOST:$QWEN_PORT/metrics" 2>/dev/null) || { echo "busy"; return; }
  value=$(printf '%s\n' "$metrics" | awk '$1 == "llamacpp:requests_processing" {print $2; found=1} END {if (!found) exit 1}') || { echo "busy"; return; }
  [ "$value" = 0 ] || { echo "busy"; return; }
  echo "idle"
}

pending_watcher() { # internal: pending_watcher MAX_WAIT POLL START_EPOCH
  local max_wait=$1 poll=$2 started=$3 reason last_reason=none idle_count=0 rc env_sha current_sha argv_sha
  local watcher_pid=$$
  trap 'rc=$?; printf "%s\\n" "$rc" > "$QWEN_PENDING_DIR/watcher.rc"; [ "$(cat "$QWEN_PENDING_PID" 2>/dev/null || true)" != "$watcher_pid" ] || rm -f "$QWEN_PENDING_PID"' EXIT
  while :; do
    env_sha=$(sha256sum "$QWEN_PENDING_ENV" | awk '{print substr($1,1,12)}')
    if [ "$(( $(date +%s) - started ))" -ge "$max_wait" ]; then
      pending_log_for_env expired "$env_sha" "blocked-by=$last_reason"
      exit 75
    fi
    reason=$(pending_guard_reason)
    if [ "$reason" = idle ]; then
      current_sha=$(sha256sum "$QWEN_PENDING_ENV" | awk '{print substr($1,1,12)}')
      if [ "$current_sha" != "$env_sha" ]; then
        idle_count=0; env_sha=$current_sha
      fi
      idle_count=$((idle_count + 1))
    else
      idle_count=0
    fi
    if [ "$idle_count" -ge 2 ]; then
      # The latest atomically-replaced snapshot wins. Require its identity to survive a final gate pass before any effect.
      current_sha=$(sha256sum "$QWEN_PENDING_ENV" | awk '{print substr($1,1,12)}')
      if [ "$current_sha" != "$env_sha" ]; then idle_count=0; env_sha=$current_sha; continue; fi
      set -a; . "$QWEN_PENDING_ENV"; set +a
      reason=$(pending_guard_reason)
      if [ "$reason" != idle ]; then
        idle_count=0
        if [ "$reason" != "$last_reason" ]; then pending_state "$reason"; echo "waiting: $reason" >> "$QWEN_PENDING_DIR/watcher.log"; last_reason=$reason; fi
        sleep "$poll"
        continue
      fi
      set +e
      ( install )
      rc=$?
      set -e
      if [ "$rc" -ne 0 ]; then
        pending_log_for_env failed "$env_sha" "rc=$rc"
        exit "$rc"
      fi
      health >/dev/null 2>&1 || { rc=$?; pending_log_for_env failed "$env_sha" "rc=$rc"; exit "$rc"; }
      argv_sha=$(argv | sha256sum | awk '{print substr($1,1,12)}')
      pending_log_for_env applied "$env_sha" "argv-sha=$argv_sha"
      rm -f "$QWEN_PENDING_ENV" "$QWEN_PENDING_STATE"
      return 0
    fi
    if [ "$reason" != "$last_reason" ]; then
      pending_state "$reason"
      echo "waiting: $reason" >> "$QWEN_PENDING_DIR/watcher.log"
      last_reason=$reason
    fi
    sleep "$poll"
  done
}

restart_when_idle() {
  local max_wait=$QWEN_PENDING_MAX_WAIT poll=$QWEN_PENDING_POLL arg candidate unit_path pid tmp started
  shift
  while [ "$#" -gt 0 ]; do
    arg=$1; shift
    case "$arg" in
      --max-wait) [ "$#" -gt 0 ] || die "--max-wait needs seconds" 64; max_wait=$1; shift;;
      --poll) [ "$#" -gt 0 ] || die "--poll needs seconds" 64; poll=$1; shift;;
      *) die "restart-when-idle: unknown argument $arg" 64;;
    esac
  done
  [[ "$max_wait" =~ ^[1-9][0-9]*$ ]] || die "--max-wait must be a positive integer" 64
  [[ "$poll" =~ ^[1-9][0-9]*$ ]] || die "--poll must be a positive integer" 64
  validate_knobs
  candidate=$(unit) || exit $?
  unit_path="$HOME/.config/systemd/user/$QWEN_UNIT.service"
  if [ "${QWEN_PENDING_FORCE_RESTART:-0}" != 1 ] && [ -f "$unit_path" ] && printf '%s\n' "$candidate" | cmp -s - "$unit_path" && health >/dev/null 2>&1; then
    echo "qwen-server: already applied"
    return 0
  fi
  mkdir -p "$QWEN_PENDING_DIR" "$QWEN_HOME/logs"
  exec 9> "$QWEN_PENDING_DIR/launch.lock"
  flock 9
  tmp="$QWEN_PENDING_ENV.tmp.$$"; pending_env_snapshot > "$tmp"; mv -f "$tmp" "$QWEN_PENDING_ENV"
  QWEN_PENDING_SINCE=$(date -u +%Y-%m-%dT%H:%M:%SZ); export QWEN_PENDING_SINCE
  pending_state none
  # Hold the launch lock until the pending env and watcher pid are both published.
  pid=$(cat "$QWEN_PENDING_PID" 2>/dev/null || true)
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null && [ ! -f "$QWEN_PENDING_DIR/watcher.rc" ]; then
    echo "qwen-server: pending: watcher $pid"
    return 0
  fi
  rm -f "$QWEN_PENDING_PID" "$QWEN_PENDING_DIR/watcher.rc"
  started=$(date +%s)
  # setsid detaches from the caller. Tests may set QWEN_TEST_WATCH_RC to keep the child waitable.
  if [ -n "${QWEN_TEST_WATCH_RC:-}" ]; then
    pending_watcher "$max_wait" "$poll" "$started" > "$QWEN_PENDING_DIR/watcher.out" 2>&1 &
  else
    setsid env QWEN_PENDING_SINCE="$QWEN_PENDING_SINCE" bash "$0" _pending-watcher "$max_wait" "$poll" "$started" \
      > "$QWEN_PENDING_DIR/watcher.out" 2>&1 < /dev/null &
  fi
  pid=$!; printf '%s\n' "$pid" > "$QWEN_PENDING_PID"
  flock -u 9
  echo "qwen-server: pending: watcher $pid"
}

probe() {
  # One real completion. Qwen3.8 THINKS first (reasoning_content) — a 24-token budget returns finish=length with an
  # EMPTY content (seen at the first install 2026-09-14: predicted_n=24, content=''), so the budget is 256 and the
  # gate is the CONTENT, never the token count (tactic 7: green without the claimed part is not a capability).
  health >/dev/null || die "not healthy" 6
  local body; body='{"model":"'"$QWEN_ALIAS"'","messages":[{"role":"user","content":"Reply with the single word pong."}],"max_tokens":256,"temperature":0}'
  curl_key 180 -H 'Content-Type: application/json' -d "$body" "http://$QWEN_HOST:$QWEN_PORT/v1/chat/completions" | python3 -c '
import json,sys
d=json.load(sys.stdin); t=d.get("timings") or {}; m=d["choices"][0]["message"]; c=(m.get("content") or "").strip()
print("qwen-server: probe served model=%s finish=%s prompt_n=%s predicted_n=%s decode_tps=%.1f reasoning_chars=%d content=%r" % (
  d.get("model"), d["choices"][0].get("finish_reason"), t.get("prompt_n"), t.get("predicted_n"), t.get("predicted_per_second",0),
  len(m.get("reasoning_content") or ""), c[:40]))
sys.exit(0 if "pong" in c.lower() else 7)' || die "probe returned no pong in content" 7
}

change_service() {
  guard_or_die
  systemctl --user "$1" "$QWEN_UNIT"
}

uninstall() {
  guard_or_die
  systemctl --user disable --now "$QWEN_UNIT" 2>/dev/null || true
  rm -f "$HOME/.config/systemd/user/$QWEN_UNIT.service"
  systemctl --user daemon-reload || die "daemon-reload failed" 5
  echo "qwen-server: unit removed (key file and logs kept)"
}

case "${1:-}" in
  argv) argv;;
  unit) unit;;
  keygen) keygen;;
  guard) guard; exit $?;;
  verify) verify_inputs && echo "qwen-server: inputs verified (binary, model, sha256 $QWEN_MODEL_SHA256, GGUF magic)";;
  install) install;;
  restart-when-idle) restart_when_idle "$@";;
  _pending-watcher) pending_watcher "$2" "$3" "$4";;
  start|stop|restart) change_service "$1";;
  status) status;;
  health) health;;
  probe) probe;;
  uninstall) uninstall;;
  *) sed -n '2,22p' "$0"; exit 64;;
esac
