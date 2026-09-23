#!/usr/bin/env bash
# Routing proof for harness-ports/bin/long-output.sh (PCJ1-R1, 2026-09-22).
#
# WHAT THIS DOES AND DOES NOT PROVE. The ON path is exercised against a FAKE node (a recorder that prints the
# script path, the separator and the argv it was given, plus the three variables the wrapper reads) and a one-shot
# local /health server. That proves the routing only: ON exactly when the wrapper file, a node binary and a healthy
# endpoint are all present; the command and its arguments reach the wrapper verbatim after `--`; exit codes pass
# through on both paths; the gate runner never names or sources the script. It proves NOTHING about pruning itself
# — the live smoke on the PC (docs/HARNESS-PORTS.md) is the real gate for that, and on CPU it fails open at the
# wrapper's fixed 30 s deadline (PCJ1's surfaced blocker).
set -uo pipefail
unset LANE_ID LANE_REPORT_DRAFT PC_LANE_JEV_DIST PC_LANE_JEV_HEALTH_URL PC_LANE_JEV_NODE 2>/dev/null || true
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
LO="$ROOT/harness-ports/bin/long-output.sh"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

pass=0; fail=0
check() { # check <label> <cond-rc> <why>
  if [ "$2" -eq 0 ]; then pass=$((pass+1)); echo "[PASS] $1"; else fail=$((fail+1)); echo "[FAIL] $1"; fi
  echo "         because: $3"
}

FAKE_NODE="$TMP/fake-node"
cat > "$FAKE_NODE" <<'SH'
#!/usr/bin/env bash
# TEST DOUBLE: records how long-output.sh invoked the wrapper, then exits 7 so exit-code passthrough is visible.
echo "FAKE-NODE script=$1"; shift
echo "FAKE-NODE base=${JEV_BASE_URL:-<unset>} key=${TYPESAFE_API_KEY:-<unset>} thread=${CODEX_THREAD_ID:-<unset>}"
for a in "$@"; do printf 'ARG[%s]\n' "$a"; done
exit 7
SH
chmod +x "$FAKE_NODE"
DIST="$TMP/run.js"; : > "$DIST"

health_server() { # health_server <portfile> <ok|down|wrongrev>  — serves ONE GET, then exits
  python3 - "$1" "$2" <<'PY' &
import http.server, json, socketserver, sys
portfile, mode = sys.argv[1:]
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        rev = "1c5edc17a7acd8701df6fc341c0d179f1c62c982" if mode != "wrongrev" else "0000000000000000000000000000000000000000"
        body = json.dumps({"ok": mode in ("ok", "wrongrev"), "revision": rev}).encode()
        self.send_response(200); self.send_header("content-length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, *a): pass
with socketserver.TCPServer(("127.0.0.1", 0), H) as s:
    open(portfile, "w").write(str(s.server_address[1])); s.handle_request()
PY
  HS_PID=$!
  for _ in $(seq 1 200); do [ -s "$1" ] && return 0; sleep 0.01; done
  kill "$HS_PID" 2>/dev/null; return 1
}
closed_port() { python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1",0)); print(s.getsockname()[1])'; }

# 1. usage
out="$(bash "$LO" 2>&1)"; rc=$?
[ "$rc" -eq 64 ] && printf '%s' "$out" | grep -q 'usage: long-output.sh -- <command>'
check "no command is a usage error (rc 64)" $? "rc=$rc out=$out"

# 2. OFF: no wrapper file — the command runs unchanged, arguments intact
out="$(PC_LANE_JEV_DIST="$TMP/absent.js" PC_LANE_JEV_NODE="$FAKE_NODE" bash "$LO" -- printf '%s|' 'a b' c 2>"$TMP/e2")"; rc=$?
[ "$rc" -eq 0 ] && [ "$out" = "a b|c|" ] && grep -q 'pruner OFF (no wrapper)' "$TMP/e2"
check "OFF when the wrapper file is absent: the command runs unchanged" $? "rc=$rc out=$out err=$(cat "$TMP/e2")"

# 3. OFF: exit code passes through on the plain path
PC_LANE_JEV_DIST="$TMP/absent.js" bash "$LO" -- sh -c 'exit 3' 2>/dev/null; rc=$?
[ "$rc" -eq 3 ]
check "OFF path: the command's exit code passes through" $? "rc=$rc (want 3)"

# 4. OFF: node missing, endpoint healthy — never routed
health_server "$TMP/p4" ok || true; P4=$(cat "$TMP/p4" 2>/dev/null)
out="$(PC_LANE_JEV_DIST="$DIST" PC_LANE_JEV_NODE="$TMP/no-such-node" PC_LANE_JEV_HEALTH_URL="http://127.0.0.1:$P4/health" bash "$LO" -- echo plain 2>"$TMP/e4")"; rc=$?
kill "$HS_PID" 2>/dev/null; wait "$HS_PID" 2>/dev/null
[ "$rc" -eq 0 ] && [ "$out" = "plain" ] && grep -q 'pruner OFF (no node)' "$TMP/e4"
check "OFF when no node binary is present" $? "rc=$rc out=$out err=$(cat "$TMP/e4")"

# 5. OFF: endpoint closed
out="$(PC_LANE_JEV_DIST="$DIST" PC_LANE_JEV_NODE="$FAKE_NODE" PC_LANE_JEV_HEALTH_URL="http://127.0.0.1:$(closed_port)/health" bash "$LO" -- echo plain 2>"$TMP/e5")"; rc=$?
[ "$rc" -eq 0 ] && [ "$out" = "plain" ] && ! printf '%s' "$out" | grep -q FAKE-NODE && grep -q 'endpoint not healthy' "$TMP/e5"
check "OFF when the endpoint is closed: the fake wrapper is never invoked" $? "rc=$rc out=$out err=$(cat "$TMP/e5")"

# 6. OFF: endpoint answers ok:false
health_server "$TMP/p6" down; P6=$(cat "$TMP/p6")
out="$(PC_LANE_JEV_DIST="$DIST" PC_LANE_JEV_NODE="$FAKE_NODE" PC_LANE_JEV_HEALTH_URL="http://127.0.0.1:$P6/health" bash "$LO" -- echo plain 2>"$TMP/e6")"; rc=$?
wait "$HS_PID" 2>/dev/null
[ "$rc" -eq 0 ] && [ "$out" = "plain" ] && grep -q 'endpoint not healthy' "$TMP/e6"
check "OFF when /health answers ok:false" $? "rc=$rc out=$out err=$(cat "$TMP/e6")"

# 6b. OFF: /health answers ok but reports another checkpoint revision (a squatter or a stale server, AF-AP-33)
health_server "$TMP/p6b" wrongrev; P6B=$(cat "$TMP/p6b")
out="$(PC_LANE_JEV_DIST="$DIST" PC_LANE_JEV_NODE="$FAKE_NODE" PC_LANE_JEV_HEALTH_URL="http://127.0.0.1:$P6B/health" bash "$LO" -- echo plain 2>"$TMP/e6b")"; rc=$?
wait "$HS_PID" 2>/dev/null
[ "$rc" -eq 0 ] && [ "$out" = "plain" ] && grep -q 'not the pinned revision' "$TMP/e6b"
check "OFF when /health is ok but reports another revision (identity, not liveness)" $? "rc=$rc out=$out err=$(cat "$TMP/e6b")"

# 7. ON: wrapper + node + healthy endpoint — routed through the wrapper, argv verbatim after --, exit code passed through
health_server "$TMP/p7" ok; P7=$(cat "$TMP/p7")
out="$(LANE_REPORT_DRAFT="$TMP/.lanes/pc-x.md--abc/report-draft.md" PC_LANE_JEV_DIST="$DIST" PC_LANE_JEV_NODE="$FAKE_NODE" PC_LANE_JEV_HEALTH_URL="http://127.0.0.1:$P7/health" bash "$LO" -- printf '%s|' 'a b' c 2>"$TMP/e7")"; rc=$?
wait "$HS_PID" 2>/dev/null
want="FAKE-NODE script=$DIST
FAKE-NODE base=http://127.0.0.1:$P7/v1/systemone key=local thread=pc-x.md--abc
ARG[--]
ARG[printf]
ARG[%s|]
ARG[a b]
ARG[c]"
[ "$rc" -eq 7 ] && [ "$out" = "$want" ] && grep -q 'pruner ON' "$TMP/e7"
check "ON: the command reaches the wrapper verbatim after --, with the endpoint base derived from /health, and its exit code passes through" $? "rc=$rc out=$(printf '%s' "$out" | tr '\n' ';') err=$(cat "$TMP/e7")"

# 8. the gate runner neither names nor sources this script (the sieve stays outside every gate's process)
PCL="$ROOT/harness-ports/bin/pc-lane.sh"
n_name=$(grep -c 'long-output' "$PCL"); n_src=$(grep -cE '^[[:space:]]*(\.|source)[[:space:]]+[^=]' "$PCL")
[ "$n_name" -eq 0 ] && [ "$n_src" -eq 0 ]
check "pc-lane.sh (a listed gate file) neither names nor sources long-output.sh" $? "name_hits=$n_name source_lines=$n_src"

echo
echo "long-output: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
