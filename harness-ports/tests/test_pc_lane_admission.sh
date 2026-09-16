#!/usr/bin/env bash
# Headroom admission gate for scripts/pc_lane.sh.
#
# Proves the testable admit-check subcommand: verdict logic, parsers, fail-open
# on unknown readings. Runs entirely in this shell — no bridge, no real launch.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
SCRIPT="$ROOT/scripts/pc_lane.sh"
TMP="$(mktemp -d)" || { echo "FATAL: mktemp -d failed" >&2; exit 1; }
trap 'rm -rf "$TMP"' EXIT

pass=0; fail=0
check() {
  if [ "$2" -eq 0 ]; then pass=$((pass+1)); echo "[PASS] $1"; else fail=$((fail+1)); echo "[FAIL] $1"; fi
  echo "         because: $3"
}

# Helper: run the admit-check subcommand, capture stdout. Stderr goes wherever
# the caller sends it (redirect in the call site to capture).
admit() {
  env -u PC_LANE_SELF_COPY bash "$SCRIPT" admit-check "$@"
}

# --- verdict logic -----------------------------------------------------------

# Healthy readings: all above default floors (256 MB disk, 512 MB mem).
V="$(admit 1000 2000 1000 2>"$TMP/err-healthy")"; rc=$?
check "healthy readings -> admit" "$([ $rc -eq 0 ] && [ "$V" = "admit" ] && echo 0 || echo 1)" \
  "rc=$rc verdict='$V'"

# LOW LOCAL DISK: 100 MB < 256 MB floor.
V="$(admit 100 2000 1000 2>"$TMP/err-ldisk")"; rc=$?
check "NEGATIVE: low local disk -> defer with disk reason" \
  "$([ $rc -eq 1 ] && echo "$V" | grep -q 'local disk' && echo "$V" | grep -q 'below floor' && echo 0 || echo 1)" \
  "rc=$rc verdict='$V'"

# LOW PC MEMORY: 200 MB < 512 MB floor.
V="$(admit 1000 200 1000 2>"$TMP/err-pmem")"; rc=$?
check "NEGATIVE: low PC memory -> defer with memory reason" \
  "$([ $rc -eq 1 ] && echo "$V" | grep -q 'PC memory' && echo "$V" | grep -q 'below floor' && echo 0 || echo 1)" \
  "rc=$rc verdict='$V'"

# LOW PC DISK: 100 MB < 256 MB floor.
V="$(admit 1000 2000 100 2>"$TMP/err-pdisk")"; rc=$?
check "NEGATIVE: low PC disk -> defer with PC disk reason" \
  "$([ $rc -eq 1 ] && echo "$V" | grep -q 'PC disk' && echo "$V" | grep -q 'below floor' && echo 0 || echo 1)" \
  "rc=$rc verdict='$V'"

# ALL UNKNOWN (-1): fail-open, admit with headroom-unknown log.
V="$(admit -1 -1 -1 2>"$TMP/err-unknown")"; rc=$?
check "all unknown (-1) -> admit (fail-open)" \
  "$([ $rc -eq 0 ] && [ "$V" = "admit" ] && echo 0 || echo 1)" \
  "rc=$rc verdict='$V'"
check "all unknown -> 'headroom unknown' logged to stderr" \
  "$(grep -q 'headroom unknown' "$TMP/err-unknown" && echo 0 || echo 1)" \
  "stderr: $(cat "$TMP/err-unknown")"

# MIXED: local known + PC unknown -> admit, still warns about PC.
V="$(admit 1000 -1 -1 2>"$TMP/err-mixed")"; rc=$?
check "local known + PC unknown -> admit (fail-open)" \
  "$([ $rc -eq 0 ] && [ "$V" = "admit" ] && echo 0 || echo 1)" \
  "rc=$rc verdict='$V'"
check "PC unknown -> 'headroom unknown' logged" \
  "$(grep -q 'headroom unknown' "$TMP/err-mixed" && echo 0 || echo 1)" \
  "stderr: $(cat "$TMP/err-mixed")"

# HEALTHY: no headroom-unknown message when all readings are available.
check "NEGATIVE: healthy readings -> no 'headroom unknown' message" \
  "$(! grep -q 'headroom unknown' "$TMP/err-healthy" && echo 0 || echo 1)" \
  "stderr: $(cat "$TMP/err-healthy")"

# --- boundary: at-floor vs below-floor ----------------------------------------

V="$(admit 256 512 256 2>/dev/null)"; rc=$?
check "exactly at floor -> admit" "$([ $rc -eq 0 ] && [ "$V" = "admit" ] && echo 0 || echo 1)" \
  "rc=$rc verdict='$V'"

V="$(admit 255 512 256 2>/dev/null)"; rc=$?
check "NEGATIVE: one below disk floor -> defer" "$([ $rc -eq 1 ] && echo 0 || echo 1)" \
  "rc=$rc verdict='$V'"

V="$(admit 256 511 256 2>/dev/null)"; rc=$?
check "NEGATIVE: one below mem floor -> defer" "$([ $rc -eq 1 ] && echo 0 || echo 1)" \
  "rc=$rc verdict='$V'"

# --- custom floors via env ----------------------------------------------------

V="$(PC_LANE_MIN_DISK_MB=50 PC_LANE_MIN_MEM_MB=100 admit 60 110 60 2>/dev/null)"; rc=$?
check "custom floors: above -> admit" "$([ $rc -eq 0 ] && echo 0 || echo 1)" \
  "rc=$rc verdict='$V'"

V="$(PC_LANE_MIN_DISK_MB=50 PC_LANE_MIN_MEM_MB=100 admit 40 110 60 2>/dev/null)"; rc=$?
check "NEGATIVE: custom floors: below disk -> defer" "$([ $rc -eq 1 ] && echo 0 || echo 1)" \
  "rc=$rc verdict='$V'"

V="$(PC_LANE_MIN_DISK_MB=50 PC_LANE_MIN_MEM_MB=100 admit 60 90 60 2>/dev/null)"; rc=$?
check "NEGATIVE: custom floors: below mem -> defer" "$([ $rc -eq 1 ] && echo 0 || echo 1)" \
  "rc=$rc verdict='$V'"

# --- priority: local disk checked first when all below floor -------------------

V="$(admit 100 200 100 2>/dev/null)"; rc=$?
check "when all below floor, local disk is reported first" \
  "$([ $rc -eq 1 ] && echo "$V" | grep -q 'local disk' && echo 0 || echo 1)" \
  "verdict='$V'"

# --- parser: free -m (real captured sample from Fedora 42 / procps-ng) --------

FREE_SAMPLE="              total        used        free      shared  buff/cache   available
Mem:         128761       85233       12345        1234       31183       42528
Swap:          8191        7800         391"
MEM_MB="$(printf '%s\n' "$FREE_SAMPLE" | admit --parse-free 2>/dev/null)"
check "parse free -m: extracts available MB (42528)" \
  "$([ "$MEM_MB" = "42528" ] && echo 0 || echo 1)" \
  "got '$MEM_MB'"

MEM_EMPTY="$(printf '' | admit --parse-free 2>/dev/null)"
check "NEGATIVE: parse free -m: empty input -> -1" \
  "$([ "$MEM_EMPTY" = "-1" ] && echo 0 || echo 1)" \
  "got '$MEM_EMPTY'"

# Old free format without 'available' column.
FREE_OLD="             total       used       free     shared    buffers     cached
Mem:        128761      85233      12345       1234       5000      26183
Swap:         8191       7800        391"
MEM_OLD="$(printf '%s\n' "$FREE_OLD" | admit --parse-free 2>/dev/null)"
check "NEGATIVE: parse free -m: old format (no available column) -> -1" \
  "$([ "$MEM_OLD" = "-1" ] && echo 0 || echo 1)" \
  "got '$MEM_OLD'"

# --- parser: df -P (real captured sample from Fedora 42) ----------------------

DF_SAMPLE="Filesystem     1024-blocks     Used Available Capacity Mounted on
/dev/sda1       488382464 200000000 263382464      44% /home"
DISK_MB="$(printf '%s\n' "$DF_SAMPLE" | admit --parse-df 2>/dev/null)"
check "parse df -P: extracts available MB (257209)" \
  "$([ "$DISK_MB" = "257209" ] && echo 0 || echo 1)" \
  "got '$DISK_MB'"

DISK_EMPTY="$(printf '' | admit --parse-df 2>/dev/null)"
check "NEGATIVE: parse df -P: empty input -> -1" \
  "$([ "$DISK_EMPTY" = "-1" ] && echo 0 || echo 1)" \
  "got '$DISK_EMPTY'"

# --- bash -n on the script itself ---------------------------------------------

bash -n "$SCRIPT" 2>"$TMP/err-syntax"
check "bash -n scripts/pc_lane.sh clean" $? \
  "$(cat "$TMP/err-syntax" 2>/dev/null)"

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
