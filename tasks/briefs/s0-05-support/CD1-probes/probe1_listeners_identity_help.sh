#!/usr/bin/env bash
# CD1 read-only probe (coordinator, 2026-09-23): listeners, pinned binary identity, --help, scratch-home writes.
set -u
echo "== clock $(date -u +%FT%TZ) host $(hostname) uid $(id -u)"
echo "== listeners (20128 OmniRoute, 3999 relay, 20201 scripted backend)"
ss -ltnH 2>/dev/null | awk '{print $4}' | grep -E ':(20128|3999|20201)$' | sort -u
B=/home/rocco/s0-01-pinned/buzz/target/release/buzz-acp
H=/home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp
echo "== identity"
for f in "$B" "$H"; do stat -c '%U %a %s %n' "$f"; sha256sum "$f" | cut -c1-64; done
head -1 "$H"
echo "== S0-01 framedir owner (CD1's inferred damage; the runner never ran on the PC)"
stat -c '%U %a %y %n' /home/rocco/s0-01-pinned/.markers /home/rocco/s0-01-pinned/.markers/v2-run-1 2>&1
S=$HOME/s0-05-scratch/cd1-$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$S/home" "$S/hermes-home"
echo "== buzz-acp --help (env -i, scratch HOME, stdin /dev/null, 15 s cap)"
env -i PATH=/usr/bin:/bin HOME="$S/home" timeout 15 "$B" --help </dev/null 2>&1 | head -60; echo "rc=${PIPESTATUS[0]}"
echo "== hermes-acp --help (env -i, scratch HOME + HERMES_HOME, stdin /dev/null, 30 s cap)"
env -i PATH=/usr/bin:/bin HOME="$S/home" HERMES_HOME="$S/hermes-home" PYTHONDONTWRITEBYTECODE=1 timeout 30 "$H" --help </dev/null 2>&1 | head -60; echo "rc=${PIPESTATUS[0]}"
echo "== files written into the scratch tree by the two --help calls"
find "$S" -mindepth 1 | sed "s#^$S#<scratch>#" | head -40
echo "== scratch path: $S"
