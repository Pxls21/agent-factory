#!/usr/bin/env bash
# pc_backend_restart.sh — (re)start the scripted upstream backend with a FRESH record dir.
# Kills only the pid in OUR pidfile after exe + cmdline checks (AF-AP-34). Records the record dir
# path in $L/backend-recdir for pc_post.sh.
set -u
BASE=/home/rocco/s0-01-pinned; L=$BASE/.markers; SEC=$BASE/.secrets; REPO=/home/rocco/agent-factory
PIDF=$L/scripted-backend.pid
if [ -f "$PIDF" ]; then P=$(cat "$PIDF"); if [ -d /proc/$P ] && [ "$(readlink /proc/$P/exe)" = "/usr/bin/python3.13" ] && tr "\0" " " < /proc/$P/cmdline | grep -q "scripted_backend.py"; then kill -TERM $P; for i in $(seq 1 20); do [ -d /proc/$P ] || break; sleep 0.25; done; echo "stopped backend $P"; else echo "pidfile stale ($P)"; fi; fi
REC=$L/upstream-records-v2-$(date -u +%Y%m%dT%H%M%SZ); mkdir -p "$REC"; echo "$REC" > $L/backend-recdir
setsid /usr/bin/python3 "$REPO/proofs/S0-01/tools/scripted_backend.py" --bind 127.0.0.1 --port 20201 --token-file "$SEC/scripted-upstream.env" --record-dir "$REC" --pidfile "$PIDF" --slow-delay 2.0 </dev/null > "$L/backend-v2.log" 2>&1 &
sleep 1.5; echo "backend pid $(cat "$PIDF" 2>/dev/null) log: $(tail -2 "$L/backend-v2.log")"; curl -s -m 5 http://127.0.0.1:20201/healthz; echo
sha256sum "$REPO/proofs/S0-01/tools/scripted_backend.py" | cut -c1-16
