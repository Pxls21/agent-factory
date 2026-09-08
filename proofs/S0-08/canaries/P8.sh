#!/bin/sh
# S0-08 canary P8 — resource limits: RECORDED, NOT ASSERTED.
#
# The verified rootless podman+runsc invocation needs --runtime-flag
# ignore-cgroups (PC-BRIDGE.md:146-150): rootless runsc cannot set up cgroups
# on the PC, so NO resource limits apply in this configuration. docs/05
# §5 lists resource limits as part of the production profile; this run cannot
# demonstrate them, so the canary records the cgroup state and the spec
# carries the gap as a documented limit rather than a silent pass.
#
# Emits ONE JSON line of OBSERVATIONS. The checker RECORDS this line and
# asserts nothing from it.
set -u

esc() {
    printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' | tr -d '\000-\037'
}

cgroup_lines=$(cat /proc/self/cgroup 2>/dev/null | tr '\n' ';' | sed -e 's/;$//')
[ -n "$cgroup_lines" ] || cgroup_lines=""

mem_max=$(cat /sys/fs/cgroup/memory.max 2>/dev/null) || mem_max=""
cpu_max=$(cat /sys/fs/cgroup/cpu.max 2>/dev/null) || cpu_max=""
pids_max=$(cat /sys/fs/cgroup/pids.max 2>/dev/null) || pids_max=""

rc=0

printf '{"canary":"P8","expect":"recorded only: no resource limits under rootless runsc (ignore-cgroups)","observed":{"cgroup":"%s","memory_max":"%s","cpu_max":"%s","pids_max":"%s"},"rc":%d}\n' \
    "$(esc "$cgroup_lines")" "$(esc "$mem_max")" "$(esc "$cpu_max")" "$(esc "$pids_max")" "$rc"
