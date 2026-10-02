#!/bin/bash
# heat_guard.sh <unit> [limit C] [every s] [readings] — the PC's CPU heat guard (D-136, AF-AP-263).
# Every <every> seconds it reads the CPU's Tctl from `sensors`. When <readings> readings in a row are at or above
# <limit> C, or cannot be read, it stops <unit> with `systemctl --user stop`. A unit stopped by hand stays stopped:
# systemd's Restart= does not restart it, so the owner or the coordinator starts it again once the PC is cool.
# Defaults: 90 C, every 5 s, 3 readings. On 2026-10-02 SGLang's start took the CPU from 63 C to 92.5 C in 50 s
# (about 1.3 cores busy, an old liquid cooler); the PC went down four times that day.
# It logs to stdout (the journal under deploy/heat-guard.service): each hot or unreadable reading, each stop, and one
# line every 5 minutes. Deployed as ~/.config/qwen-serving/heat_guard.sh.
U=${1:?usage: heat_guard.sh <unit> [limit C] [every s] [readings]}
LIMIT=${2:-90}
EVERY=${3:-5}
NEED=${4:-3}
for v in "$LIMIT" "$EVERY" "$NEED"; do
  case "$v" in
    '' | *[!0-9]*) ok= ;;
    *) ok=$((10#$v > 0)) ;;
  esac
  if [ "$ok" != 1 ]; then
    echo "heat_guard: limit, every and readings must be whole numbers above 0, got '$v'" >&2
    exit 64
  fi
done
LIMIT=$((10#$LIMIT)); EVERY=$((10#$EVERY)); NEED=$((10#$NEED))
BEAT=$((300 / EVERY))
[ "$BEAT" -ge 1 ] || BEAT=1
n=0
i=0
echo "heat_guard: watching $U; stop after $NEED readings at or above $LIMIT C or unreadable, one every $EVERY s"
while true; do
  T=$(sensors 2>/dev/null | awk '/^Tctl:/ {gsub(/[+°C]/, "", $2); print $2; exit}')
  # an unreadable sensor counts as hot: the guard fails closed
  if awk -v t="$T" -v l="$LIMIT" 'BEGIN { exit !(t !~ /^[0-9]+(\.[0-9]+)?$/ || t + 0 >= l + 0) }'; then
    n=$((n + 1))
    echo "heat_guard: hot reading tctl=${T:-unreadable} ($n of $NEED)"
  else
    n=0
  fi
  if [ "$n" -ge "$NEED" ]; then
    case "$(systemctl --user is-active "$U" 2>/dev/null)" in
      active | activating | reloading)
        systemctl --user stop "$U"
        echo "heat_guard: STOPPED $U after $NEED readings at or above $LIMIT C or unreadable (last tctl=${T:-unreadable})" ;;
      *)
        echo "heat_guard: hot with $U not running (tctl=${T:-unreadable}); nothing to stop" ;;
    esac
    n=0
  fi
  i=$((i + 1))
  [ $((i % BEAT)) -eq 0 ] && echo "heat_guard: alive, tctl=${T:-unreadable}"
  sleep "$EVERY"
done
