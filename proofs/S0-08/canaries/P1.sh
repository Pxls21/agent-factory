#!/bin/sh
# S0-08 canary P1 — is this process running under the gVisor kernel?
# Emits ONE JSON line of OBSERVATIONS on stdout. It never prints a verdict:
# check_containment.py decides PASS/FAIL. rc is this script's own status
# (0 = the observation was taken), never the property's verdict.
set -u

esc() {
    printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' | tr -d '\000-\037'
}

kernel=$(uname -r 2>/dev/null) || kernel=""

# Capture dmesg's OWN exit status. There must be no pipeline between the tool
# and `$?`: `dmesg | head` reports HEAD's status, which is always 0, so a
# refused dmesg (kernel.dmesg_restrict=1 for a non-root caller) emitted an
# empty first line beside rc 0 and the checker answered with an empty-tailed
# reason instead of "did not observe". Same class as P3's, which was fixed.
dmesg_all=$(dmesg 2>/dev/null); dmesg_rc=$?
dmesg_first=$(printf '%s\n' "$dmesg_all" | head -n 1)

rc=0
[ -n "$kernel" ] || rc=1
[ "$dmesg_rc" -eq 0 ] || rc=1

printf '{"canary":"P1","expect":"uname -r is 4.19.0-gvisor and dmesg line 1 contains Starting gVisor","observed":{"uname_r":"%s","dmesg_first_line":"%s"},"rc":%d}\n' \
    "$(esc "$kernel")" "$(esc "$dmesg_first")" "$rc"
