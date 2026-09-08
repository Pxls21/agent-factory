#!/bin/sh
# S0-08 canary P5 — the host-read canary must FAIL.
#
# The runner writes a nonce-named sentinel on the HOST, mounts it NOWHERE,
# and records its host-side readability in runtime-identity.json. That host
# read is the POSITIVE control: without it, "unreadable inside" proves
# nothing (the file might never have existed — AF-AP-22).
#
# S0_08_SENTINEL_PATH is a per-run value supplied by the runner via
# `podman exec -e`. It is read once and ECHOED into the observation, so the
# checker can bind this line to the identity file's recorded path.
#
# Emits ONE JSON line of OBSERVATIONS. The checker decides PASS/FAIL.
set -u

esc() {
    printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' | tr -d '\000-\037'
}

sentinel="${S0_08_SENTINEL_PATH:-}"

sentinel_readable="no"
sentinel_error=""
if [ -n "$sentinel" ]; then
    if sentinel_error=$(cat "$sentinel" 2>&1 >/dev/null); then
        # cat succeeded: the host file IS readable from inside the container.
        sentinel_readable="yes"
        sentinel_error=""
    fi
else
    sentinel_error="S0_08_SENTINEL_PATH not supplied"
fi

# Recorded, not asserted: what the container can see of the host's home tree.
home_entries=$(ls -1 /home 2>/dev/null | sort | tr '\n' ',' | sed -e 's/,$//')
[ -n "$home_entries" ] || home_entries=""

container_hostname=$(cat /etc/hostname 2>/dev/null) || container_hostname=""

rc=0
[ -n "$sentinel" ] || rc=1

printf '{"canary":"P5","expect":"the host sentinel is UNREADABLE inside the container","observed":{"sentinel_path":"%s","sentinel_readable":"%s","sentinel_error":"%s","home_entries":"%s","container_hostname":"%s"},"rc":%d}\n' \
    "$(esc "$sentinel")" "$(esc "$sentinel_readable")" "$(esc "$sentinel_error")" \
    "$(esc "$home_entries")" "$(esc "$container_hostname")" "$rc"
