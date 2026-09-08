#!/usr/bin/env bash
# C1 — DNS resolution of a model host must FAIL inside the namespace (docs/05_SECURITY.md:21,
# "DNS/connection canaries"). curl is used for the exact resolver diagnostic; resolution fails
# before any byte is sent, so no request ever reaches the provider.
#   c1_dns_resolve.sh <unit> <host>
set -u
. "$(dirname "$0")/_emit.sh"
unit=${1:?unit} host=${2:?host}
# What the namespace's resolver actually returns is RECORDED, because a venue's /etc/hosts can
# short-circuit DNS entirely (measured 2026-09-08: this sandbox's /etc/hosts:2 maps
# api.anthropic.com to the provider address, so for that host C1 degenerates to a connect test
# and C5 is the canary that still exercises DNS egress). Recording it keeps the venue fact in
# the evidence instead of only in the report. getaddrinfo, not `getent ahostsv4`: measured in
# an isolated namespace, getent exits 2 while getaddrinfo returns the /etc/hosts address — the
# recorded field must show what curl itself resolves.
resolved=$(python3 -c "
import socket, sys
try:
    print(socket.getaddrinfo(sys.argv[1], 443, socket.AF_INET)[0][4][0])
except OSError:
    print('-')" "$host" 2>/dev/null)
err=$(mktemp); curl -sS --connect-timeout "$EGRESS_CONNECT_TIMEOUT" --max-time "$EGRESS_MAX_TIME" \
  -o /dev/null "https://$host/" 2>"$err"; rc=$?
detail=$(cat "$err"); rm -f "$err"
[ -n "$detail" ] || detail="curl exit $rc with no diagnostic"
emit_canary C1 "$unit" "$host" dns-resolve "$rc" run "$detail" "resolved=${resolved:--}"
