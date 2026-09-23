#!/usr/bin/env bash
# CD1 probe 2 (coordinator, 2026-09-23): unit lifetime + startup writes, inside a no-network user
# namespace (unshare -c -n = total isolation, AF-AP-1's class used ON PURPOSE so nothing leaves the host).
set -u
S=$HOME/s0-05-scratch/cd1-life-$(date -u +%Y%m%dT%H%M%SZ); mkdir -p "$S/home" "$S/hermes-home"
H=/home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp
B=/home/rocco/s0-01-pinned/buzz/target/release/buzz-acp
U="unshare -c -n"
$U true 2>/dev/null || U="unshare -r -n"
echo "== isolation: $U"; $U sh -c 'ls /sys/class/net; id -u'; echo "rc=$?"
HENV="env -i PATH=/usr/bin:/bin HOME=$S/home HERMES_HOME=$S/hermes-home PYTHONDONTWRITEBYTECODE=1"
echo "== hermes-acp --version"; $HENV $U timeout 30 "$H" --version </dev/null 2>&1 | head -5; echo "rc=${PIPESTATUS[0]}"
echo "== hermes-acp --check"; $HENV $U timeout 60 "$H" --check </dev/null 2>&1 | head -25; echo "rc=${PIPESTATUS[0]}"
echo "== hermes-acp, stdin /dev/null, 30 s cap"
t0=$(date +%s.%N); $HENV $U timeout 30 "$H" </dev/null >"$S/h-null.log" 2>&1; rc=$?; t1=$(date +%s.%N)
echo "rc=$rc secs=$(echo "$t1 - $t0" | bc)"; head -c 1500 "$S/h-null.log"; echo
echo "== hermes-acp, stdin held open 10 s then EOF, 30 s cap"
t0=$(date +%s.%N); sleep 10 | $HENV $U timeout 30 "$H" >"$S/h-open.log" 2>&1; rc=${PIPESTATUS[1]}; t1=$(date +%s.%N)
echo "rc=$rc secs=$(echo "$t1 - $t0" | bc)"; head -c 1500 "$S/h-open.log"; echo
echo "== buzz-acp, an INVENTED key, relay unreachable (isolated), agent /bin/false, 20 s cap"
t0=$(date +%s.%N)
env -i PATH=/usr/bin:/bin HOME="$S/home" BUZZ_PRIVATE_KEY=1111111111111111111111111111111111111111111111111111111111111111 \
  $U timeout 20 "$B" --relay-url ws://127.0.0.1:3999 --agent-command /bin/false --agent-args "" </dev/null >"$S/b.log" 2>&1; rc=$?
t1=$(date +%s.%N); echo "rc=$rc secs=$(echo "$t1 - $t0" | bc)"; tail -c 1500 "$S/b.log"; echo
echo "== files written into the scratch tree"
find "$S" -mindepth 1 -not -name '*.log' | sed "s#^$S#<scratch>#" | sort | head -60
echo "== scratch: $S"
