#!/usr/bin/env bash
# Selective-egress spike: prove that a veth/proxy netns mechanism can
# selectively allow traffic to an OmniRoute stand-in while blocking
# everything else.  This is NOT bare `unshare --net` (AF-AP-1: total
# isolation blocks both legs).
#
# Architecture:
#   Host netns:  veth-host  10.200.0.1/24  — runs the stand-in listener
#   Test netns:  veth-egress 10.200.0.2/24 — iptables allow only 10.200.0.1:12800
#
# Positive leg: curl inside netns reaches the stand-in → 200
# Negative leg: curl inside netns to a blocked port → connection refused / timeout
set -euo pipefail

NS="egress-spike"
VETH_HOST="veth-host"
VETH_NS="veth-egress"
HOST_IP="10.200.0.1"
NS_IP="10.200.0.2"
ALLOWED_PORT=12800
BLOCKED_PORT=12801
RESULT_FILE="${1:-/dev/stdout}"

cleanup() {
  kill "$STANDIN_PID" 2>/dev/null || true
  kill "$BLOCKED_PID" 2>/dev/null || true
  ip link del "$VETH_HOST" 2>/dev/null || true
  ip netns del "$NS" 2>/dev/null || true
}
trap cleanup EXIT

echo "=== setup ===" >&2

ip netns del "$NS" 2>/dev/null || true
ip link del "$VETH_HOST" 2>/dev/null || true

ip netns add "$NS"
ip link add "$VETH_HOST" type veth peer name "$VETH_NS"
ip link set "$VETH_NS" netns "$NS"

ip addr add "${HOST_IP}/24" dev "$VETH_HOST"
ip link set "$VETH_HOST" up

ip netns exec "$NS" ip addr add "${NS_IP}/24" dev "$VETH_NS"
ip netns exec "$NS" ip link set "$VETH_NS" up
ip netns exec "$NS" ip link set lo up

ip netns exec "$NS" iptables -P OUTPUT DROP
ip netns exec "$NS" iptables -P INPUT DROP
ip netns exec "$NS" iptables -P FORWARD DROP

ip netns exec "$NS" iptables -A OUTPUT -d "$HOST_IP" -p tcp --dport "$ALLOWED_PORT" -j ACCEPT
ip netns exec "$NS" iptables -A INPUT  -s "$HOST_IP" -p tcp --sport "$ALLOWED_PORT" -j ACCEPT

ip netns exec "$NS" iptables -A OUTPUT -o lo -j ACCEPT
ip netns exec "$NS" iptables -A INPUT  -i lo -j ACCEPT

echo "=== stand-in listener on ${HOST_IP}:${ALLOWED_PORT} ===" >&2
python3 -c "
import http.server, json, threading
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'object':'list','data':[{'id':'omniroute-standin'}]}).encode())
    def log_message(self, *a): pass
s = http.server.HTTPServer(('${HOST_IP}', ${ALLOWED_PORT}), H)
s.serve_forever()
" &
STANDIN_PID=$!
sleep 0.5

python3 -c "
import http.server, json
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.end_headers()
        self.wfile.write(b'{\"id\":\"blocked-model\"}')
    def log_message(self, *a): pass
s = http.server.HTTPServer(('${HOST_IP}', ${BLOCKED_PORT}), H)
s.serve_forever()
" &
BLOCKED_PID=$!
sleep 0.5

echo "=== positive leg: reach the allowed stand-in ===" >&2
set +e
POS_OUTPUT=$(ip netns exec "$NS" curl -sS --connect-timeout 5 "http://${HOST_IP}:${ALLOWED_PORT}/v1/models" 2>&1)
POS_RC=$?
set -e
echo "POS_RC=$POS_RC POS_OUTPUT=$POS_OUTPUT" >&2

echo "=== negative leg: blocked port (model endpoint not on the allow-list) ===" >&2
set +e
NEG_OUTPUT=$(ip netns exec "$NS" curl -sS --connect-timeout 5 "http://${HOST_IP}:${BLOCKED_PORT}/v1/models" 2>&1)
NEG_RC=$?
set -e
echo "NEG_RC=$NEG_RC NEG_OUTPUT=$NEG_OUTPUT" >&2

echo "=== negative leg 2: external endpoint ===" >&2
set +e
NEG2_OUTPUT=$(ip netns exec "$NS" curl -sS --connect-timeout 5 "http://1.1.1.1/" 2>&1)
NEG2_RC=$?
set -e
echo "NEG2_RC=$NEG2_RC NEG2_OUTPUT=$NEG2_OUTPUT" >&2

echo "=== gate-off mutation: drop iptables, blocked port becomes reachable ===" >&2
ip netns exec "$NS" iptables -F OUTPUT
ip netns exec "$NS" iptables -P OUTPUT ACCEPT
ip netns exec "$NS" iptables -F INPUT
ip netns exec "$NS" iptables -P INPUT ACCEPT
set +e
GATEOFF_OUTPUT=$(ip netns exec "$NS" curl -sS --connect-timeout 5 "http://${HOST_IP}:${BLOCKED_PORT}/v1/models" 2>&1)
GATEOFF_RC=$?
set -e
echo "GATEOFF_RC=$GATEOFF_RC GATEOFF_OUTPUT=$GATEOFF_OUTPUT" >&2

POS_PASS="false"
NEG_PASS="false"
NEG2_PASS="false"
GATEOFF_PASS="false"

if [ "$POS_RC" = "0" ] && echo "$POS_OUTPUT" | grep -q "omniroute-standin"; then
  POS_PASS="true"
fi
if [ "$NEG_RC" != "0" ]; then
  NEG_PASS="true"
fi
if [ "$NEG2_RC" != "0" ]; then
  NEG2_PASS="true"
fi
if [ "$GATEOFF_RC" = "0" ] && echo "$GATEOFF_OUTPUT" | grep -q "blocked-model"; then
  GATEOFF_PASS="true"
fi

if [ "$POS_PASS" = "true" ] && [ "$NEG_PASS" = "true" ] && [ "$GATEOFF_PASS" = "true" ]; then
  OUTCOME="positive"
else
  OUTCOME="negative"
fi

RAN_AT="$(date -u +%Y-%m-%dT%H:%M:%S+00:00)"
KERNEL="$(uname -r)"

export OUTCOME RAN_AT KERNEL
export NS VETH_HOST VETH_NS HOST_IP NS_IP ALLOWED_PORT BLOCKED_PORT
export POS_RC POS_OUTPUT POS_PASS NEG_RC NEG_OUTPUT NEG_PASS
export NEG2_RC NEG2_OUTPUT NEG2_PASS GATEOFF_RC GATEOFF_OUTPUT GATEOFF_PASS

python3 << 'PYEOF' > "$RESULT_FILE"
import json, sys, os

e = os.environ
result = {
    "spike_id": "selective-egress",
    "schema": "proofs/schemas/spike.schema.json",
    "outcome": e["OUTCOME"],
    "ran_at": e["RAN_AT"],
    "env_fingerprint": f"ccr-sandbox:linux:{e['KERNEL']}",
    "mechanism": "veth pair + iptables in a dedicated network namespace; NOT bare unshare --net (AF-AP-1)",
    "architecture": {
        "host_side": f"{e['VETH_HOST']} {e['HOST_IP']}/24 — runs the OmniRoute stand-in on port {e['ALLOWED_PORT']}",
        "netns_side": f"{e['VETH_NS']} {e['NS_IP']}/24 — iptables OUTPUT/INPUT allow only {e['HOST_IP']}:{e['ALLOWED_PORT']}, default DROP",
        "stand_in": "Python HTTP server returning {object:list, data:[{id:omniroute-standin}]}",
    },
    "runs": [
        {
            "label": "positive-leg",
            "command": f"ip netns exec {e['NS']} curl http://{e['HOST_IP']}:{e['ALLOWED_PORT']}/v1/models",
            "exit_code": int(e["POS_RC"]),
            "stdout_excerpt": e["POS_OUTPUT"][:200],
            "pass": e["POS_PASS"] == "true",
            "notes": "Unit inside netns reaches the allowed OmniRoute stand-in",
        },
        {
            "label": "negative-leg-blocked-port",
            "command": f"ip netns exec {e['NS']} curl http://{e['HOST_IP']}:{e['BLOCKED_PORT']}/v1/models",
            "exit_code": int(e["NEG_RC"]),
            "stdout_excerpt": e["NEG_OUTPUT"][:200],
            "pass": e["NEG_PASS"] == "true",
            "notes": "Same unit fails to reach a non-allowed port — iptables DROP",
        },
        {
            "label": "negative-leg-external",
            "command": f"ip netns exec {e['NS']} curl http://1.1.1.1/",
            "exit_code": int(e["NEG2_RC"]),
            "stdout_excerpt": e["NEG2_OUTPUT"][:200],
            "pass": e["NEG2_PASS"] == "true",
            "notes": "Same unit fails to reach an external IP — no route / iptables DROP",
        },
        {
            "label": "gate-off-mutation",
            "command": "iptables -F + -P ACCEPT then curl blocked port",
            "exit_code": int(e["GATEOFF_RC"]),
            "stdout_excerpt": e["GATEOFF_OUTPUT"][:200],
            "pass": e["GATEOFF_PASS"] == "true",
            "notes": "Gate-off mutation: dropping iptables rules makes the blocked port reachable (proves the gate was the barrier, not a structural artifact)",
        },
    ],
    "classification_effect": [
        {
            "affected_proof": "S0-05",
            "class": "execution_proof",
            "rule_id": "map-egress-s005",
            "reason": "mechanism proven (veth + iptables selective egress), containment unproven (full canary suite over live units is Wave 2, increment #16)",
        }
    ],
    "not_verified": [
        "Full canary suite over live production units (Wave 2, increment #16)",
        "UDP/ICMP egress (only TCP tested)",
        "DNS resolution inside the netns (no resolver configured)",
        "Performance under load",
        "Persistence across container restarts",
    ],
}
json.dump(result, sys.stdout, indent=1)
print()
PYEOF

echo "=== RESULT ===" >&2
echo "OUTCOME=$OUTCOME POS=$POS_PASS NEG=$NEG_PASS NEG2=$NEG2_PASS GATEOFF=$GATEOFF_PASS" >&2
