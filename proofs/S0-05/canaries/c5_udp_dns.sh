#!/usr/bin/env bash
# C5 — UDP/53 to a resolver. The spike tested TCP only (`not_verified`: "UDP/ICMP egress
# filtering"); this closes that leg. Inside the namespace the packet is dropped by the OUTPUT
# policy, which the kernel reports to the sender as EPERM — a signature only the gate produces.
#   c5_udp_dns.sh <unit> <resolver-ip> [port]
set -u
. "$(dirname "$0")/_emit.sh"
unit=${1:?unit} ip=${2:?resolver-ip} port=${3:-53}
out=$(python3 "$(dirname "$0")/connect_probe.py" udp "$ip" "$port" 3); rc=$?
emit_canary C5 "$unit" "$ip:$port" udp-dns "$rc" run "$out"
