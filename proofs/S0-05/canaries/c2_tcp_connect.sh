#!/usr/bin/env bash
# C2 — TCP connect to a model provider address. The address is resolved OUTSIDE the namespace by
# run_canaries.sh and passed in, so the canary tests reachability, not resolution. TCP connect
# only: zero bytes are sent.
#   c2_tcp_connect.sh <unit> <host> <ip> [port]
set -u
. "$(dirname "$0")/_emit.sh"
unit=${1:?unit} host=${2:?host} ip=${3:?ip} port=${4:-443}
out=$(python3 "$(dirname "$0")/connect_probe.py" tcp "$ip" "$port" "$EGRESS_CONNECT_TIMEOUT"); rc=$?
emit_canary C2 "$unit" "$host:$port" tcp-connect "$rc" run "$out" "ip=$ip"
