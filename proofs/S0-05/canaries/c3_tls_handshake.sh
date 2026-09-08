#!/usr/bin/env bash
# C3 — TLS handshake to the same model provider address. Handshake only: the socket is closed
# the moment the handshake resolves, so no HTTP request and no credential ever leaves.
#   c3_tls_handshake.sh <unit> <host> <ip> [port]
set -u
. "$(dirname "$0")/_emit.sh"
unit=${1:?unit} host=${2:?host} ip=${3:?ip} port=${4:-443}
out=$(python3 "$(dirname "$0")/connect_probe.py" tls "$ip" "$port" "$EGRESS_CONNECT_TIMEOUT" "$host"); rc=$?
emit_canary C3 "$unit" "$host:$port" tls-handshake "$rc" run "$out" "ip=$ip"
