#!/usr/bin/env bash
# C4 — a NON-model internet target. RECORDED, never asserted: docs/02_COMPONENT_AUDIT.md:56 —
# "OmniRoute is sole model API egress, not automatically sole web/tool egress". The checker
# records C4's outcome so the report can state what this mechanism does to general web egress.
#   c4_internet_target.sh <unit> <host> <ip> [port]
set -u
. "$(dirname "$0")/_emit.sh"
unit=${1:?unit} host=${2:?host} ip=${3:?ip} port=${4:-443}
out=$(python3 "$(dirname "$0")/connect_probe.py" tcp "$ip" "$port" "$EGRESS_CONNECT_TIMEOUT"); rc=$?
emit_canary C4 "$unit" "$host:$port" tcp-connect-internet "$rc" run "$out" "ip=$ip"
