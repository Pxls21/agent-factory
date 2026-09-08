#!/bin/sh
# S0-08 canary P6 — escape attempts must not yield HOST state.
#
# MEASURED under runsc release-20260817.0 (sandbox, 2026-09-08), not assumed:
#   `mount -t proc proc <dir>` SUCCEEDS (rc 0) inside a gVisor sandbox and
#   yields the SANDBOX's own procfs. Asserting "mount is denied" would fail
#   on a correctly-contained container. The containment signature is WHOSE
#   process table the mount reveals: the container's (PID 1 == the container's
#   own init) and not the host's.
#   `unshare -n` likewise SUCCEEDS and creates a namespace INSIDE the sandbox.
#   Both results are recorded verbatim; neither is asserted as a denial.
#
# Emits ONE JSON line of OBSERVATIONS. The checker decides PASS/FAIL.
set -u

esc() {
    printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' | tr -d '\000-\037'
}

# --- Raw host devices must be absent ---
# gVisor exposes a minimal synthetic /dev. Any of these names would mean the
# container was handed a real host device.
dangerous=""
for dev in /dev/kvm /dev/mem /dev/kmsg /dev/sda /dev/nvme0n1 /dev/loop0 /dev/dm-0; do
    [ -e "$dev" ] && dangerous="${dangerous}${dangerous:+,}${dev}"
done
[ -n "$dangerous" ] || dangerous=""
dev_entries=$(ls -1 /dev 2>/dev/null | sort | tr '\n' ',' | sed -e 's/,$//')

# --- mount -t proc: allowed, but must reveal only the sandbox ---
# Unique per invocation: two concurrent runs must never share a mount point.
mp=/tmp/s0-08-p6-proc.$$
mkdir -p "$mp" 2>/dev/null
mount_err=$(mount -t proc proc "$mp" 2>&1 >/dev/null)
mount_rc=$?
mounted_pid1_comm=""
mounted_pid_count=""
if [ "$mount_rc" -eq 0 ]; then
    mounted_pid1_comm=$(cat "$mp/1/comm" 2>/dev/null) || mounted_pid1_comm=""
    mounted_pid_count=$(ls -d "$mp"/[0-9]* 2>/dev/null | grep -c .) || mounted_pid_count=0
    umount "$mp" 2>/dev/null || true
fi
rmdir "$mp" 2>/dev/null || true

own_pid1_comm=$(cat /proc/1/comm 2>/dev/null) || own_pid1_comm=""
own_pid_count=$(ls -d /proc/[0-9]* 2>/dev/null | grep -c .) || own_pid_count=0

# --- unshare -n: recorded verbatim, not asserted ---
unshare_err=$(unshare -n true 2>&1 >/dev/null)
unshare_rc=$?

rc=0

printf '{"canary":"P6","expect":"no raw host devices; a mounted procfs shows the container PID 1, not the host","observed":{"dangerous_devices":"%s","dev_entries":"%s","mount_proc_rc":"%d","mount_proc_error":"%s","mounted_pid1_comm":"%s","mounted_pid_count":"%s","own_pid1_comm":"%s","own_pid_count":"%s","unshare_net_rc":"%d","unshare_net_error":"%s"},"rc":%d}\n' \
    "$(esc "$dangerous")" "$(esc "$dev_entries")" \
    "$mount_rc" "$(esc "$mount_err")" \
    "$(esc "$mounted_pid1_comm")" "$(esc "$mounted_pid_count")" \
    "$(esc "$own_pid1_comm")" "$(esc "$own_pid_count")" \
    "$unshare_rc" "$(esc "$unshare_err")" "$rc"
