#!/usr/bin/env bash
# laya-server.sh — install and run the local Laya System One endpoint as a user service.
set -uo pipefail

LAYA_REPO="${LAYA_REPO:-$HOME/agent-factory}"
LAYA_SCRIPT="${LAYA_SCRIPT:-$LAYA_REPO/scripts/laya_systemone_server.py}"
LAYA_HOME="${LAYA_HOME:-$HOME/laya-server}"
LAYA_VENV="${LAYA_VENV:-$HOME/venv-laya}"
LAYA_HF_HOME="${LAYA_HF_HOME:-$HOME/hf-laya}"
LAYA_UNIT="${LAYA_UNIT:-laya-systemone}"
LAYA_HOST="${LAYA_HOST:-127.0.0.1}"
LAYA_PORT="${LAYA_PORT:-47411}"
LAYA_THREADS="${LAYA_THREADS:-8}"
LAYA_DEVICE="${LAYA_DEVICE:-auto}"
LAYA_REVISION="${LAYA_REVISION:-1c5edc17a7acd8701df6fc341c0d179f1c62c982}"
LAYA_SUBFOLDER="${LAYA_SUBFOLDER:-typed-decisions}"
LAYA_INSTALL_LOG="$LAYA_HOME/install.log"
LAYA_INSTALL_PID="$LAYA_HOME/install.pid"
LAYA_INSTALL_DONE="$LAYA_HOME/install.done"
LAYA_INSTALL_FAILED="$LAYA_HOME/install.failed"
LAYA_SERVICE_LOG="$LAYA_HOME/server.log"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"

fail() {
  local rc=1
  if [ "${!#}" -eq "${!#}" ] 2>/dev/null; then rc=${!#}; set -- "${@:1:$(($# - 1))}"; fi
  echo "laya-server: $*" >&2
  exit "$rc"
}

unit_path() { printf '%s/.config/systemd/user/%s.service\n' "$HOME" "$LAYA_UNIT"; }

unit() {
  cat <<EOF
[Unit]
Description=Local Laya System One endpoint (loopback; convaiinnovations/laya typed-decisions)
StartLimitIntervalSec=300
StartLimitBurst=3

[Service]
Type=simple
WorkingDirectory=$LAYA_HOME
Environment=HF_HUB_OFFLINE=1
Environment=TRANSFORMERS_OFFLINE=1
ExecStart=$LAYA_VENV/bin/python $LAYA_SCRIPT --device $LAYA_DEVICE --port $LAYA_PORT --hf-home $LAYA_HF_HOME --threads $LAYA_THREADS --revision $LAYA_REVISION --subfolder $LAYA_SUBFOLDER
Restart=on-failure
RestartSec=5
StandardOutput=append:$LAYA_SERVICE_LOG
StandardError=append:$LAYA_SERVICE_LOG

[Install]
WantedBy=default.target
EOF
}

install_worker() {
  local worker="$LAYA_HOME/install-worker.sh"
  mkdir -p "$LAYA_HOME" "$LAYA_HF_HOME"
  cat > "$worker" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
: "${LAYA_VENV:?}" "${LAYA_HF_HOME:?}" "${LAYA_REVISION:?}" "${LAYA_INSTALL_DONE:?}" "${LAYA_INSTALL_FAILED:?}"
rm -f "$LAYA_INSTALL_DONE" "$LAYA_INSTALL_FAILED"
python3.11 -m venv "$LAYA_VENV"
"$LAYA_VENV/bin/python" -m pip install --upgrade pip setuptools wheel
"$LAYA_VENV/bin/python" -m pip install torch==2.14.0 laya==0.3.5
LAYA_HF_HOME="$LAYA_HF_HOME" LAYA_REVISION="$LAYA_REVISION" "$LAYA_VENV/bin/python" - <<'PY'
import os
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="convaiinnovations/laya",
    revision=os.environ["LAYA_REVISION"],
    allow_patterns=["typed-decisions/*", "*.json", "*.md"],
    cache_dir=os.path.join(os.environ["LAYA_HF_HOME"], "hub"),
)
PY
date -u +%Y-%m-%dT%H:%M:%SZ > "$LAYA_INSTALL_DONE"
EOF
  chmod +x "$worker"
  export LAYA_VENV LAYA_HF_HOME LAYA_REVISION LAYA_INSTALL_DONE LAYA_INSTALL_FAILED
  nohup bash -c '"$0" || { rc=$?; printf "%s rc=%s\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$rc" > "$LAYA_INSTALL_FAILED"; exit "$rc"; }' "$worker" > "$LAYA_INSTALL_LOG" 2>&1 &
  printf '%s\n' "$!" > "$LAYA_INSTALL_PID"
  echo "laya-server: install started pid=$! log=$LAYA_INSTALL_LOG"
}

install() {
  if [ -s "$LAYA_INSTALL_DONE" ]; then echo "laya-server: install done $(cat "$LAYA_INSTALL_DONE")"; return 0; fi
  if [ -s "$LAYA_INSTALL_PID" ] && kill -0 "$(cat "$LAYA_INSTALL_PID")" 2>/dev/null; then
    echo "laya-server: install running pid=$(cat "$LAYA_INSTALL_PID") log=$LAYA_INSTALL_LOG"
    return 0
  fi
  install_worker
}

start() {
  [ -x "$LAYA_VENV/bin/python" ] || fail "missing venv python: $LAYA_VENV/bin/python (run install first)" 3
  [ -f "$LAYA_SCRIPT" ] || fail "missing server script: $LAYA_SCRIPT" 3
  mkdir -p "$LAYA_HOME" "$HOME/.config/systemd/user"
  unit > "$(unit_path)"
  systemd-analyze --user verify "$(unit_path)" || fail "unit does not verify" 5
  systemctl --user daemon-reload || fail "daemon-reload failed" 5
  systemctl --user reset-failed "$LAYA_UNIT" 2>/dev/null || true
  systemctl --user enable --now "$LAYA_UNIT" >/dev/null || fail "enable --now $LAYA_UNIT failed" 5
  echo "laya-server: unit $LAYA_UNIT enabled; script=$LAYA_SCRIPT; device=$LAYA_DEVICE; revision=$LAYA_REVISION"
}

stop() {
  systemctl --user stop "$LAYA_UNIT" || fail "stop $LAYA_UNIT failed" 5
  echo "laya-server: unit $LAYA_UNIT stopped"
}

status() {
  if [ -s "$LAYA_INSTALL_DONE" ]; then echo "laya-server: install=done $(cat "$LAYA_INSTALL_DONE")";
  elif [ -s "$LAYA_INSTALL_FAILED" ]; then echo "laya-server: install=failed $(cat "$LAYA_INSTALL_FAILED")";
  elif [ -s "$LAYA_INSTALL_PID" ] && kill -0 "$(cat "$LAYA_INSTALL_PID")" 2>/dev/null; then echo "laya-server: install=running pid=$(cat "$LAYA_INSTALL_PID") log=$LAYA_INSTALL_LOG";
  else echo "laya-server: install=not-started"; fi
  systemctl --user is-enabled "$LAYA_UNIT" 2>/dev/null | sed 's/^/laya-server: unit enabled=/' || true
  systemctl --user is-active "$LAYA_UNIT" 2>/dev/null | sed 's/^/laya-server: unit active=/' || true
  health || true
}

health() {
  local h
  h=$(curl -fsS -m 5 "http://$LAYA_HOST:$LAYA_PORT/health" 2>/dev/null) || { echo "laya-server: /health not ok"; return 1; }
  printf '%s\n' "$h"
}

smoke() {
  local body out1 out2 cmp
  body='{"model":"jev-latest","state":{"context":"agent-factory","task":"run the suite","command":"pytest -q","history":[],"diagnosticsAndResults":"","chunks":[{"id":"c1","text":"tests/test_a.py::test_x PASSED\ntests/test_a.py::test_y PASSED\ntests/test_a.py::test_z PASSED"},{"id":"c2","text":"E   AssertionError: expected 4 got 5\ntests/test_b.py:12: AssertionError\nFAILED tests/test_b.py::test_q"},{"id":"c3","text":"collecting ... collected 3 items"}]},"questions":{"c1":{"type":"noul","instructions":"Is this chunk needed to understand the outcome?","criteria":{"true":"errors, failures, results, needed details","false":"routine noise"}},"c2":{"type":"noul","instructions":"Is this chunk needed to understand the outcome?","criteria":{"true":"errors, failures, results, needed details","false":"routine noise"}},"c3":{"type":"noul","instructions":"Is this chunk needed to understand the outcome?","criteria":{"true":"errors, failures, results, needed details","false":"routine noise"}}}}'
  out1=$(curl -fsS -m 300 -H 'Content-Type: application/json' -d "$body" "http://$LAYA_HOST:$LAYA_PORT/v1/systemone") || return $?
  out2=$(curl -fsS -m 300 -H 'Content-Type: application/json' -d "$body" "http://$LAYA_HOST:$LAYA_PORT/v1/systemone") || return $?
  printf 'run1 %s\n' "$out1" | "$LAYA_VENV/bin/python" -c 'import json,sys; p=sys.stdin.read().split(" ",1)[1]; d=json.loads(p); print("run1 c1=%.4f c2=%.4f c3=%.4f fan_out=%s latency_ms=%s" % (d["answers"]["c1"]["noul"], d["answers"]["c2"]["noul"], d["answers"]["c3"]["noul"], d.get("fan_out"), d.get("latency_ms")))'
  printf 'run2 %s\n' "$out2" | "$LAYA_VENV/bin/python" -c 'import json,sys; p=sys.stdin.read().split(" ",1)[1]; d=json.loads(p); print("run2 c1=%.4f c2=%.4f c3=%.4f fan_out=%s latency_ms=%s" % (d["answers"]["c1"]["noul"], d["answers"]["c2"]["noul"], d["answers"]["c3"]["noul"], d.get("fan_out"), d.get("latency_ms")))'
  cmp=$(OUT1="$out1" OUT2="$out2" "$LAYA_VENV/bin/python" - <<'PY'
import json, os
one=json.loads(os.environ['OUT1']); two=json.loads(os.environ['OUT2'])
a={k: v['noul'] for k, v in one['answers'].items()}
b={k: v['noul'] for k, v in two['answers'].items()}
print('answers_bitwise_identical=%s' % (a == b))
PY
)
  printf '%s\n' "$cmp"
}

case "${1:-}" in
  install) install;;
  start) start;;
  stop) stop;;
  status) status;;
  health) health;;
  smoke) smoke;;
  unit) unit;;
  *) echo "usage: laya-server.sh install|start|stop|status|health|smoke|unit"; exit 64;;
esac
