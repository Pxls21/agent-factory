#!/usr/bin/env bash
# pc_fetch.sh — bring ONE file home from the PC in size-verified chunks.
#
#   scripts/pc_fetch.sh <remote-path> <local-path>
#
# The bridge caps a reply at ~45 KB and a truncated base64 tail decodes to a plausible file
# (AF-AP-15, 2026-09-03: a lane patch came home as its last 45 KB). So: base64 on the PC,
# read the exact char count, pull 40 000-char slices, refuse on any size mismatch, then decode.
set -uo pipefail
die() { echo "pc_fetch: $*" >&2; exit 64; }
[ $# -eq 2 ] || die "usage: pc_fetch.sh <remote-path> <local-path>"
REMOTE="$1"; LOCAL="$2"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [ -z "${PC_BRIDGE_URL:-}" ] || [ -z "${PC_BRIDGE_TOKEN:-}" ]; then
  [ -f "$ROOT/.pc-bridge.env" ] && { set -a; . "$ROOT/.pc-bridge.env"; set +a; }
fi
export PC_BRIDGE_URL PC_BRIDGE_TOKEN
bridge() { python3 "$ROOT/scripts/pc_bridge_exec.py" "$1"; }
B64="/tmp/pc_fetch.$$.b64"
TOTAL="$(bridge "test -f $REMOTE && base64 -w0 $REMOTE > $B64 && wc -c < $B64" 2>/dev/null | tr -dc 0-9)"
[ -n "$TOTAL" ] && [ "$TOTAL" -gt 0 ] || die "remote file missing or empty: $REMOTE"
: > "$LOCAL.b64"
off=1; step=40000
while [ "$off" -le "$TOTAL" ]; do
  end=$((off+step-1))
  bridge "cut -c${off}-${end} $B64" 2>/dev/null | tr -d '\n' >> "$LOCAL.b64"
  off=$((end+1))
done
bridge "rm -f $B64" >/dev/null 2>&1
GOT="$(wc -c < "$LOCAL.b64")"
[ "$GOT" = "$TOTAL" ] || { rm -f "$LOCAL.b64"; die "size mismatch: got $GOT of $TOTAL base64 chars"; }
base64 -d < "$LOCAL.b64" > "$LOCAL" && rm -f "$LOCAL.b64" && echo "pc_fetch: $REMOTE -> $LOCAL ($(wc -c < "$LOCAL") bytes)" >&2
