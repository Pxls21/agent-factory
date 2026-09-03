#!/usr/bin/env bash
# MCP smoke test — ONE call per server, run on the PC.
#
# WHY THIS EXISTS: the harness MCP configs in .codex/config.toml and
# harness-ports/hermes/config-snippet.yaml were written from each server's
# committed definition, NOT from a working connection. The servers live on the
# PC; the sandbox that authored them cannot reach them. "Configured" is not
# "delivered" — this script is the acceptance probe that closes that gap.
#
# It does not use either harness. It speaks raw MCP over stdio: initialize,
# then tools/list. If a server answers with a tool list, it is genuinely up. If
# it hangs, crashes, or answers nothing, you get a named failure instead of a
# harness that quietly shows fewer tools than you expected.
#
# Usage:
#   bash harness-ports/bin/mcp-smoke.sh              # every stdio server
#   bash harness-ports/bin/mcp-smoke.sh gitnexus     # just one
#
# Env overrides are the same ones mcp-server.sh documents (AF_REPO,
# AF_VENV, CODEBASE_MEMORY_BIN, GRAFT_BIN, OUROBOROS_BIN).
#
# phoenix-docs is HTTP, not stdio, and is checked with a plain request instead.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Two statements, not `git || cd && pwd` — that parses as (git||cd)&&pwd and
# yields a two-line ROOT on the success path.
ROOT="$(git -C "$HERE" rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$ROOT" ]; then ROOT="$(cd "$HERE/../.." && pwd)"; fi
LAUNCH="$HERE/mcp-server.sh"
PHOENIX_URL="https://arizeai-433a7140.mintlify.app/mcp"
TIMEOUT="${MCP_SMOKE_TIMEOUT:-45}"

STDIO_SERVERS=(gitnexus aleph codebase-memory ouroboros graft)
[ $# -gt 0 ] && STDIO_SERVERS=("$@")

pass=0; fail=0
printf '%-18s %-8s %s\n' SERVER RESULT DETAIL
printf '%-18s %-8s %s\n' ------ ------ ------

probe_stdio() {
  local name="$1" out rc tools
  # Minimal MCP handshake: initialize -> initialized -> tools/list.
  out="$(
    {
      printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"mcp-smoke","version":"1"}}}'
      sleep 2
      printf '%s\n' '{"jsonrpc":"2.0","method":"notifications/initialized"}'
      printf '%s\n' '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
      sleep 4
    } | timeout "$TIMEOUT" bash "$LAUNCH" "$name" 2>/dev/null
  )"
  rc=$?
  if [ -z "$out" ]; then
    printf '%-18s %-8s %s\n' "$name" FAIL "no response (rc=$rc) — server did not start or never answered"
    return 1
  fi
  # Count tool names in the tools/list result without needing jq.
  tools="$(printf '%s' "$out" | python3 -c '
import json,sys
n=0
for line in sys.stdin:
    line=line.strip()
    if not line.startswith("{"): continue
    try: m=json.loads(line)
    except Exception: continue
    if m.get("id")==2 and "result" in m:
        n=len(m["result"].get("tools",[]))
print(n)
' 2>/dev/null)"
  if [ -n "$tools" ] && [ "$tools" -gt 0 ] 2>/dev/null; then
    printf '%-18s %-8s %s\n' "$name" PASS "$tools tools listed"
    return 0
  fi
  if printf '%s' "$out" | grep -q '"result"'; then
    printf '%-18s %-8s %s\n' "$name" WARN "initialized but tools/list returned none"
    return 1
  fi
  printf '%-18s %-8s %s\n' "$name" FAIL "no usable JSON-RPC result"
  return 1
}

for s in "${STDIO_SERVERS[@]}"; do
  if probe_stdio "$s"; then pass=$((pass+1)); else fail=$((fail+1)); fi
done

# HTTP server: a reachable MCP endpoint, checked separately.
code="$(curl -s -o /dev/null -w '%{http_code}' -m 20 \
        -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
        -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"mcp-smoke","version":"1"}}}' \
        "$PHOENIX_URL" 2>/dev/null)"
if [ "$code" = "200" ] || [ "$code" = "202" ]; then
  printf '%-18s %-8s %s\n' phoenix-docs PASS "HTTP $code"
  pass=$((pass+1))
else
  printf '%-18s %-8s %s\n' phoenix-docs FAIL "HTTP ${code:-none}"
  fail=$((fail+1))
fi

echo
echo "$pass passed, $fail failed"
echo
echo "On a FAIL, do NOT edit the harness config to hide it:"
echo "  - name the server that is down in your status line;"
echo "  - the Ouroboros and GitNexus MCP tiers have stdio fallbacks that work"
echo "    when MCP does not — scripts/ooo_mcp.py and scripts/gn_mcp.py;"
echo "  - if every tier of a tool is unreachable, report 'unmapped — tool"
echo "    unavailable'. Never imply a mapped claim a tool did not produce."
exit $([ "$fail" -eq 0 ] && echo 0 || echo 1)
