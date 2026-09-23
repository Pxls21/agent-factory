#!/usr/bin/env bash
# CD1 probe 3: the isolation instrument (/proc/net/dev + ip link, never sysfs) and hermes-acp with BOTH ends piped.
set -u
S=$HOME/s0-05-scratch/cd1-pipe-$(date -u +%Y%m%dT%H%M%SZ); mkdir -p "$S/home" "$S/hermes-home"
H=/home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp
U="unshare -c -n"
echo "== host view: interfaces in /proc/net/dev"; awk -F: 'NR>2{gsub(/ /,"",$1); printf "%s ", $1}' /proc/net/dev; echo
echo "== isolated view: /proc/net/dev + ip -o link (inside $U)"
$U sh -c 'awk -F: "NR>2{gsub(/ /,\"\",\$1); printf \"%s \", \$1}" /proc/net/dev; echo; ip -o link 2>&1 | cut -d" " -f2 | tr "\n" " "; echo'
HENV="env -i PATH=/usr/bin:/bin HOME=$S/home HERMES_HOME=$S/hermes-home PYTHONDONTWRITEBYTECODE=1"
echo "== hermes-acp, stdin a pipe held open 10 s, stdout+stderr a pipe into cat (inside $U), 30 s cap"
t0=$(date +%s.%N)
sleep 10 | $HENV $U timeout 30 "$H" 2>&1 | cat > "$S/h-pipe.log"; rcs="${PIPESTATUS[*]}"
t1=$(date +%s.%N); echo "rcs(sleep,hermes,cat)=$rcs secs=$(echo "$t1 - $t0" | bc)"
grep -c 'Traceback' "$S/h-pipe.log" | sed 's/^/tracebacks=/'; head -c 900 "$S/h-pipe.log"; echo; echo ...; tail -c 600 "$S/h-pipe.log"; echo
echo "== scratch: $S"
