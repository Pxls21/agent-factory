#!/bin/bash
# pc_egress_watch.sh — watch one PC lane's network peers from OUTSIDE the lane (task #365, H1b).
# Every 0.5 s it lists the TCP and UDP sockets (`ss -tunpH`) of every process whose command line carries
# `-p <profile>` (the runner starts Hermes as `hermes -p <lane profile>`), and of their children down to
# DEPTH levels, and appends "<epoch> <pid> <proto> <peer>" lines to <out>. It reads socket tables only,
# never payloads, and needs no root for the owner's own processes. It ends GRACE seconds after the lane's
# processes are gone, or after <max-seconds>, and writes <out>.summary: "WATCH-END seen=<0|1> lines=<n>",
# then one "<count> <proto> <peer>" line per peer. A sampler misses a connection that opens and closes
# between two samples; the smoke lane's startup call to openrouter.ai showed in one sample of 1,275.
# Usage: pc_egress_watch.sh <lane-profile> <out-file> [max-seconds]
#   start it BEFORE the lane (setsid nohup ... &), with a command line that does not itself hold
#   `-p <profile>`, or the watch sees its caller as a lane process.
set -u
[ $# -ge 2 ] || { echo "usage: pc_egress_watch.sh <lane-profile> <out-file> [max-seconds]" >&2; exit 64; }
PROF="$1"; OUT="$2"; MAX="${3:-5400}"
case "$PROF" in
  aflane*[!a-z0-9]*|aflane) echo "pc_egress_watch: refusing '$PROF': not a lane profile name (aflane + [a-z0-9])" >&2; exit 64;;
  aflane*) ;;
  *) echo "pc_egress_watch: refusing '$PROF': not a lane profile name (aflane + [a-z0-9])" >&2; exit 64;;
esac
case "$MAX" in ''|*[!0-9]*) echo "pc_egress_watch: max-seconds must be a whole number" >&2; exit 64;; esac
GRACE="${EGRESS_WATCH_GRACE:-60}"; DEPTH="${EGRESS_WATCH_DEPTH:-4}"
case "$GRACE$DEPTH" in *[!0-9]*) echo "pc_egress_watch: EGRESS_WATCH_GRACE and EGRESS_WATCH_DEPTH are whole numbers" >&2; exit 64;; esac
END=$(( $(date +%s) + MAX )); SEEN=0; GONE_SINCE=0
: > "$OUT" || exit 1
while [ "$(date +%s)" -lt "$END" ]; do
  LEVEL=$(pgrep -f -- "-p ${PROF}( |$)" 2>/dev/null | tr '\n' ' ')
  ALL="$LEVEL"; d=0
  while [ -n "${LEVEL// /}" ] && [ "$d" -lt "$DEPTH" ]; do
    NEXT=""
    for p in $LEVEL; do NEXT="$NEXT $(pgrep -P "$p" 2>/dev/null | tr '\n' ' ')"; done
    LEVEL="$NEXT"; ALL="$ALL $NEXT"; d=$((d + 1))
  done
  ALL=$(echo $ALL)
  if [ -n "$ALL" ]; then
    SEEN=1; GONE_SINCE=0
    RX=$(echo "$ALL" | tr ' ' '|')
    ss -tunpH 2>/dev/null | grep -E "pid=($RX)," | awk -v t="$(date +%s)" '{
      match($0, /pid=[0-9]+/); p = substr($0, RSTART + 4, RLENGTH - 4); print t, p, $1, $6 }' >> "$OUT"
  elif [ "$SEEN" -eq 1 ]; then
    [ "$GONE_SINCE" -eq 0 ] && GONE_SINCE=$(date +%s)
    [ $(( $(date +%s) - GONE_SINCE )) -ge "$GRACE" ] && break
  fi
  sleep 0.5
done
{ echo "WATCH-END seen=$SEEN lines=$(wc -l < "$OUT")"
  awk '{print $3, $4}' "$OUT" | sort | uniq -c | sort -rn; } > "$OUT.summary"
