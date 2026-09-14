#!/usr/bin/env bash
# qwen-server.sh — the LOCAL BUILD-LANE MODEL as a user service on the PC (owner ask 2026-09-14: "let's get
# Qwen to do the heavy lifting"): Qwen3.8-27B UD-IQ4_XS on the June CUDA llama.cpp build, fully resident on
# the 3090, MTP on, the full 262k context split over four slots — the shape MEASURED in
# docs/research/FINDINGS-LOCAL-BUILDER-QWEN38.md §6 (2026-09-14). It listens on loopback only, behind an API
# key that ONLY OmniRoute reads (project rule 3: OmniRoute is the sole model egress — Hermes never talks to
# this port directly; harness-ports/bin/omniroute_local_builder.py wires the provider node + combo).
#
#   harness-ports/bin/qwen-server.sh argv|unit|keygen|install|start|stop|restart|status|health|probe|uninstall
#
#   argv      print the llama-server argv (one token per line) — the testable surface
#   unit      print the systemd --user unit text
#   keygen    create the API key file (0600, 64 hex) if absent; the value is never printed
#   install   verify binary + model identity, keygen, write the unit, enable --now, wait for /health
#   status    unit state + the served model list (no key ever printed)
#   health    rc 0 iff /health is ok AND /v1/models lists the alias
#   probe     one 24-token completion through the server; prints the served model id + timings
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
QWEN_MTP_N="${QWEN_MTP_N:-3}"            # draft-mtp n=3: 86.9 t/s at 90 % acceptance on code (n=2: 79.9)
QWEN_EFFORT="${QWEN_EFFORT:-medium}"     # the server-side default; a request's own reasoning_effort wins
QWEN_CACHE_REUSE="${QWEN_CACHE_REUSE:-256}"
QWEN_KEY_FILE="${QWEN_KEY_FILE:-$HOME/.config/qwen-builder/api-key}"
QWEN_UNIT="${QWEN_UNIT:-qwen-builder}"
QWEN_HOME="${QWEN_HOME:-$HOME/qwen-builder}"
QWEN_HEALTH_WAIT_S="${QWEN_HEALTH_WAIT_S:-180}"
QWEN_LANES_DIR="${QWEN_LANES_DIR:-$HOME/agent-factory/.lanes}"   # live lane pidfiles: install never restarts under one
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"

die() { echo "qwen-server: $*" >&2; exit "${2:-1}"; }

resolve_model() {
  if [ -n "$QWEN_MODEL_GGUF" ]; then printf '%s\n' "$QWEN_MODEL_GGUF"; return; fi
  local m
  m=$(ls -d "$QWEN_MODEL_REPO_DIR"/snapshots/*/"$QWEN_MODEL_FILE" 2>/dev/null | head -1)
  printf '%s\n' "$m"
}

argv() {
  local model; model=$(resolve_model)
  printf '%s\n' "$QWEN_LLAMA_SERVER" \
    -m "$model" \
    --alias "$QWEN_ALIAS" \
    --host "$QWEN_HOST" --port "$QWEN_PORT" \
    --api-key-file "$QWEN_KEY_FILE" \
    -ngl "$QWEN_NGL" -c "$QWEN_CTX" -fa on -ctk "$QWEN_KV_TYPE" -ctv "$QWEN_KV_TYPE" \
    -np "$QWEN_SLOTS" --cache-reuse "$QWEN_CACHE_REUSE" \
    --spec-type draft-mtp --spec-draft-n-max "$QWEN_MTP_N" \
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

verify_inputs() {
  [ -x "$QWEN_LLAMA_SERVER" ] || die "llama-server binary absent or not executable: $QWEN_LLAMA_SERVER" 2
  local model; model=$(resolve_model)
  [ -n "$model" ] && [ -f "$model" ] || die "model GGUF absent under $QWEN_MODEL_REPO_DIR/snapshots/*/$QWEN_MODEL_FILE" 3
  local blob; blob=$(basename "$(readlink -f "$model")")
  [ "$blob" = "$QWEN_MODEL_SHA256" ] || die "model identity mismatch: blob $blob, expected sha256 $QWEN_MODEL_SHA256" 3
  local magic; magic=$(head -c 4 "$model")
  [ "$magic" = "GGUF" ] || die "model file is not a GGUF (magic ${magic@Q})" 3
}

curl_key() { curl -s -m "${1:-5}" -H "Authorization: Bearer $(cat "$QWEN_KEY_FILE")" "${@:2}"; }

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
  verify_inputs
  mkdir -p "$QWEN_HOME/logs" "$HOME/.config/systemd/user"
  keygen
  local unit_path="$HOME/.config/systemd/user/$QWEN_UNIT.service" changed=0
  if [ -f "$unit_path" ] && ! unit | cmp -s - "$unit_path"; then changed=1; fi
  unit > "$unit_path"
  systemd-analyze --user verify "$unit_path" || die "unit does not verify (systemd-analyze)" 5
  systemctl --user daemon-reload || die "daemon-reload failed" 5
  systemctl --user enable --now "$QWEN_UNIT" >/dev/null 2>&1 || die "enable --now $QWEN_UNIT failed" 5
  if [ "$changed" = 1 ] && systemctl --user is-active --quiet "$QWEN_UNIT"; then
    # enable --now is a no-op on a running unit: a changed argv only takes effect through a restart. A restart
    # kills every lane mid-turn — install refuses while a lane pidfile is alive (check .lanes/*/lane.pid first).
    local live; live=$(for f in "$QWEN_LANES_DIR"/*/lane.pid; do [ -f "$f" ] && kill -0 "$(cat "$f")" 2>/dev/null && echo "$f"; done)
    [ -z "$live" ] || die "unit text changed but a lane is alive ($live) — stop it by pid first, then re-run install" 7
    echo "qwen-server: unit text changed and the unit is running — restarting it"
    systemctl --user restart "$QWEN_UNIT" || die "restart $QWEN_UNIT failed" 5
  fi
  echo "qwen-server: unit $QWEN_UNIT enabled; llama-server $("$QWEN_LLAMA_SERVER" --version 2>&1 | head -1); model blob $QWEN_MODEL_SHA256"
  wait_health
}

status() {
  systemctl --user is-enabled "$QWEN_UNIT" 2>/dev/null | sed 's/^/qwen-server: unit enabled=/'
  systemctl --user is-active "$QWEN_UNIT" 2>/dev/null | sed 's/^/qwen-server: unit active=/'
  loginctl show-user "$(id -un)" -p Linger 2>/dev/null | sed 's/^/qwen-server: user /'   # Linger=yes keeps the unit alive with no login session
  grep -o 'reasoning_effort[^}]*' "$HOME/.config/systemd/user/$QWEN_UNIT.service" 2>/dev/null | head -1 | sed 's/^/qwen-server: unit effort /'
  health || true
  command -v nvidia-smi >/dev/null && nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader | sed 's/^/qwen-server: gpu /'
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

case "${1:-}" in
  argv) argv;;
  unit) unit;;
  keygen) keygen;;
  verify) verify_inputs && echo "qwen-server: inputs verified (binary, model, sha256 $QWEN_MODEL_SHA256, GGUF magic)";;
  install) install;;
  start|stop|restart) systemctl --user "$1" "$QWEN_UNIT";;
  status) status;;
  health) health;;
  probe) probe;;
  uninstall) systemctl --user disable --now "$QWEN_UNIT" 2>/dev/null; rm -f "$HOME/.config/systemd/user/$QWEN_UNIT.service"; systemctl --user daemon-reload; echo "qwen-server: unit removed (key file and logs kept)";;
  *) sed -n '2,20p' "$0"; exit 64;;
esac
