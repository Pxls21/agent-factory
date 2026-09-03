#!/usr/bin/env bash
# pc.sh — run one shell command on the owner's PC through the token-gated HTTP bridge.
# Usage: scripts/pc.sh '<command>'
# Reads PC_BRIDGE_URL / PC_BRIDGE_TOKEN from the environment or the untracked .pc-bridge.env
# (never commit links or tokens). Protocol + quirks: PC-BRIDGE.md.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[ -f "$ROOT/.pc-bridge.env" ] && . "$ROOT/.pc-bridge.env"
: "${PC_BRIDGE_URL:?set PC_BRIDGE_URL (from the owner's BRIDGE READY banner)}"
: "${PC_BRIDGE_TOKEN:?set PC_BRIDGE_TOKEN (from the owner's BRIDGE READY banner)}"
[ $# -ge 1 ] || { echo "usage: scripts/pc.sh '<command>'" >&2; exit 2; }
BODY=$(python3 -c 'import json,sys; print(json.dumps({"cmd": sys.argv[1]}))' "$*")
RESP=""
# Connection: close + retry-on-non-JSON: both required (connection-poisoning quirk, PC-BRIDGE.md).
for attempt in 1 2 3; do
  RESP=$(curl -sS -m 120 -X POST "${PC_BRIDGE_URL%/}/exec" \
    -H "X-Agent-Token: $PC_BRIDGE_TOKEN" -H "Content-Type: application/json" \
    -H "Connection: close" --data "$BODY" 2>&1) || true
  case "$RESP" in "{"*) break;; esac
  sleep 1
done
python3 - "$RESP" <<'PY'
import json, sys
raw = sys.argv[1]
try:
    r = json.loads(raw)
except Exception:
    sys.stderr.write("bridge: non-JSON response after 3 attempts:\n" + raw[:400] + "\n"); sys.exit(3)
if "error" in r and "rc" not in r:
    sys.stderr.write("bridge error: %s\n" % r["error"]); sys.exit(4)
sys.stdout.write(r.get("stdout", "")); sys.stderr.write(r.get("stderr", ""))
sys.exit(int(r.get("rc", 1)))
PY
