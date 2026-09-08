#!/bin/sh
# S0-08 canary P2 — root start, s6 supervision, privilege drop.
#
# The pinned image (hermes-agent 527da608) starts as root so s6-overlay's
# stage2 hook can usermod/chown the data volume (Dockerfile:298, :309-311),
# then drops the MAIN PROGRAM to the hermes user (uid 10000) in
# docker/main-wrapper.sh:31.  The supervised `main-hermes` service is a
# deliberate root no-op sleeper (docker/s6-rc.d/main-hermes/run:27) and the
# `dashboard` service is DOWN unless HERMES_DASHBOARD is truthy
# (docker/s6-rc.d/dashboard/run:9-20) — both are RECORDED here, never asserted.
#
# Emits ONE JSON line of OBSERVATIONS. The checker decides PASS/FAIL.
set -u

esc() {
    printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' | tr -d '\000-\037'
}

uid_of() { awk '/^Uid:/{print $2; exit}' "/proc/$1/status" 2>/dev/null; }
cmdline_of() { tr '\0' ' ' < "/proc/$1/cmdline" 2>/dev/null | sed -e 's/ *$//'; }

# The container's main program. The runner is the SINGLE source of this
# string: it passes the same value it gave `podman run` as S0_08_MAIN_CMDLINE
# in the exec env (tools/pc/run_containment.sh). There is deliberately NO
# default — a canary that invented one could silently observe a different
# process than the container's main program.
MAIN_CMDLINE="${S0_08_MAIN_CMDLINE:-}"

pid1_uid=$(uid_of 1)
pid1_comm=$(cat /proc/1/comm 2>/dev/null) || pid1_comm=""
pid1_cmdline=$(cmdline_of 1)

# Owned-subset scan: report EVERY process whose cmdline is exactly the main
# cmdline, never just the first one the glob reached. Selecting by an exact
# cmdline is only safe when the cmdline is unique, and the image ships a root
# `exec sleep infinity` no-op that is up by default
# (docker/s6-rc.d/main-hermes/run:27) — with the old `sleep infinity` CMD two
# processes matched and glob order decided which uid P2 reported. The checker
# refuses an ambiguous set by name. Every other row is counted, never asserted
# equal to a spawn set (AF-AP-59).
main_uids=""
main_pids=""
proc_count=0
for d in /proc/[0-9]*; do
    p=${d#/proc/}
    proc_count=$((proc_count + 1))
    [ -n "$MAIN_CMDLINE" ] || continue
    if [ "$(cmdline_of "$p")" = "$MAIN_CMDLINE" ]; then
        main_pids="${main_pids}${main_pids:+,}${p}"
        main_uids="${main_uids}${main_uids:+,}$(uid_of "$p")"
    fi
done

rc=0
[ -n "$pid1_uid" ] || rc=1
[ -n "$MAIN_CMDLINE" ] || rc=1

printf '{"canary":"P2","expect":"pid 1 uid 0 running s6 init; exactly one process has the main cmdline (%s) and it runs as uid 10000","observed":{"pid1_uid":"%s","pid1_comm":"%s","pid1_cmdline":"%s","main_cmdline":"%s","main_pids":"%s","main_uids":"%s","proc_count":"%s"},"rc":%d}\n' \
    "$(esc "$MAIN_CMDLINE")" "$(esc "$pid1_uid")" "$(esc "$pid1_comm")" \
    "$(esc "$pid1_cmdline")" "$(esc "$MAIN_CMDLINE")" \
    "$(esc "$main_pids")" "$(esc "$main_uids")" \
    "$(esc "$proc_count")" "$rc"
