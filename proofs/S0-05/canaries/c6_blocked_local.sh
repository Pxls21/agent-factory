#!/usr/bin/env bash
# C6 — a ROUTABLE endpoint that is NOT on the allow-list (the spike's negative leg 1,
# probe.sh:98-103). This is the only canary the iptables gate itself discriminates: on the
# namespace's own /24 there is no routing barrier, so a denial here is the gate and nothing
# else, and switching the gate off flips it to a 200 (measured: rc 28 -> rc 0). Every other
# denial canary targets an address the namespace has no route to at all.
# ADDITION to the brief's C0-C5 set — see the report's DISCREPANCIES.
#   c6_blocked_local.sh <unit> <ip:port>
set -u
. "$(dirname "$0")/_emit.sh"
unit=${1:?unit} target=${2:?target}
err=$(mktemp); code=$(curl -sS --connect-timeout "$EGRESS_CONNECT_TIMEOUT" --max-time "$EGRESS_MAX_TIME" \
      -o /dev/null -w '%{http_code}' "http://$target/v1/models" 2>"$err"); rc=$?
detail=$(cat "$err"); rm -f "$err"
[ -n "$detail" ] || detail="curl exit $rc, HTTP $code"
emit_canary C6 "$unit" "$target" tcp-connect-local "$rc" run "$detail" "http_status=$code"
