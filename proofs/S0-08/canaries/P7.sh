#!/bin/sh
# S0-08 canary P7 — egress posture: RECORDED, NOT ASSERTED.
#
# S0-08 does not assert egress. Enforced egress is S0-05's proof. This canary
# exists so the containment run RECORDS the network posture it ran under,
# because the production compose file uses host networking
# (hermes-agent docker-compose.yml:35 and :67, `network_mode: host`) while the
# containment run deliberately does NOT (the runner passes --network none).
# The gap between the two is a documented limit, stated in CONTAINMENT-SPEC.md.
#
# Emits ONE JSON line of OBSERVATIONS. The checker RECORDS this line and
# asserts nothing from it.
set -u

esc() {
    printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' | tr -d '\000-\037'
}

interfaces=$(ls -1 /sys/class/net 2>/dev/null | sort | tr '\n' ',' | sed -e 's/,$//')
[ -n "$interfaces" ] || interfaces=""

netns=$(readlink /proc/self/ns/net 2>/dev/null) || netns=""

rc=0

printf '{"canary":"P7","expect":"recorded only: S0-08 asserts no egress property (S0-05 owns egress)","observed":{"interfaces":"%s","net_namespace":"%s"},"rc":%d}\n' \
    "$(esc "$interfaces")" "$(esc "$netns")" "$rc"
