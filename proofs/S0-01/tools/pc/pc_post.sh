#!/usr/bin/env bash
# pc_post.sh — close a leg: process scan, masked log, backend record window, post manifest,
# teardown BY PIDFILE (non-shutdown legs), teardown scan, leak guard.
# Contract v2.1 §12-§14. Kills ONLY pids recorded by our own instruments after an exe check (AF-AP-34).
set -u
BASE=/home/rocco/s0-01-pinned; L=$BASE/.markers; SEC=$BASE/.secrets; REPO=/home/rocco/agent-factory
FD=$(cat $L/current-framedir); RECDIR=$(cat $L/backend-recdir)
BA=$BASE/buzz/target/release/buzz-acp; TEE=$REPO/proofs/S0-01/tools/frame_tee.py; HERMES=$BASE/.venv-hermes/bin/hermes-acp
scan() { ps -eo pid,ppid,cmd --no-headers | grep -E "s0-01-pinned|frame_tee|proofs/S0-01" | grep -vE " grep -E | ps -eo " ; }
mask() { tr -d "\000" < "$1" | sed -E "s#\x1b\[[0-9;]*m##g; s#[a-f0-9]{64}#<HEX>#g"; }
echo "=== post: $FD ==="
scan > "$FD/process-scan-after.txt" || true; echo "scan-after lines: $(wc -l < "$FD/process-scan-after.txt")"
mask "$FD/buzzacp.raw.log" > "$FD/buzzacp.log"
curl -s -m 5 http://127.0.0.1:20201/healthz > "$FD/backend-healthz-after.json"
B0=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["records"])' "$FD/backend-healthz-before.json")
B1=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["records"])' "$FD/backend-healthz-after.json")
echo "backend records window: $B0 -> $B1"
for n in $(seq $((B0+1)) $B1); do f=$(printf "%s/%06d.json" "$RECDIR" $n); [ -f "$f" ] && cp "$f" "$FD/upstream-records/"; done
echo "copied records: $(ls "$FD/upstream-records" | wc -l) (POST: $(grep -l '"method": "POST"' "$FD"/upstream-records/*.json 2>/dev/null | wc -l))"
rm -f "$FD/manifest-post.done"; PHASE=post FD=$FD BASE=$BASE setsid bash "$REPO/proofs/S0-01/tools/pc/pc_manifest.sh" </dev/null >"$FD/manifest-post.log" 2>&1 &
# --- teardown (non-shutdown legs): SIGTERM the buzz-acp pid from OUR pidfile after an exe check ---
if [ ! -f "$FD/buzz-acp.exit" ]; then
  PID=$(cat "$FD/buzz-acp.pid")
  if [ -d /proc/$PID ] && [ "$(readlink /proc/$PID/exe)" = "$BA" ]; then
    TEEPID=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("tee_pid",""))' "$FD/runtime-identity.json")
    AGPID=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("agent_child_pid",""))' "$FD/runtime-identity.json")
    kill -TERM $PID; for i in $(seq 1 30); do [ -d /proc/$PID ] || break; sleep 0.5; done
    [ -d /proc/$PID ] && { echo "buzz-acp ignored TERM; KILL"; kill -KILL $PID; sleep 1; }
    for p in $TEEPID $AGPID; do
      [ -n "$p" ] && [ -d /proc/$p ] && case "$(tr "\0" " " < /proc/$p/cmdline)" in *"$TEE"*|*"$HERMES"*) echo "TERM survivor $p"; kill -TERM $p;; esac
    done
    echo "teardown: SIGTERM buzz-acp pid $PID (exe verified) at $(date -u +%FT%TZ); tee=$TEEPID agent=$AGPID" > "$FD/teardown.txt"
  else
    echo "teardown: buzz-acp pid $PID not alive or not the pinned exe" | tee "$FD/teardown.txt"
  fi
  for i in $(seq 1 30); do [ -f "$FD/buzz-acp.exit" ] && break; sleep 0.5; done
  sleep 1; scan > "$FD/process-scan-teardown.txt" || true; echo "scan-teardown lines: $(wc -l < "$FD/process-scan-teardown.txt")"
fi
echo "buzz-acp.exit: $(cat "$FD/buzz-acp.exit" 2>/dev/null || echo '<absent>')"
# --- leak guard: no secret VALUE may appear in any evidence file (pattern file is 0600, never printed) ---
PAT=$(mktemp -p "$L" .leakpat.XXXXXX); chmod 600 "$PAT"
python3 - "$PAT" "$SEC" "$HOME/.hermes/profiles/agentfactory/.env" <<'PY'
import sys, os
pat, sec, henv = sys.argv[1:4]
vals = []
def kv(path, key):
    for line in open(path, encoding="utf-8"):
        if line.startswith(key + "="):
            v = line[len(key) + 1:].strip().strip('"').strip("'")
            if v: vals.append(v)
for who in ("agent", "owner", "user2"): kv(os.path.join(sec, who + ".env"), "BUZZ_PRIVATE_KEY")
kv(os.path.join(sec, "scripted-upstream.env"), "UPSTREAM_TOKEN"); kv(henv, "OMNIROUTE_API_KEY")
open(pat, "w").write("\n".join(vals) + "\n"); print("leak patterns:", len(vals))
PY
LEAKS=$(grep -rlF -f "$PAT" "$FD" 2>/dev/null || true); rm -f "$PAT"
if [ -n "$LEAKS" ]; then echo "LEAK DETECTED — deleting:"; echo "$LEAKS"; echo "$LEAKS" | xargs rm -f; exit 9; fi
echo "leak guard: clean"
for i in $(seq 1 240); do [ -f "$FD/manifest-post.done" ] && break; sleep 0.5; done
[ -f "$FD/manifest-pre.done" ] && echo "pre : $(cat "$FD/manifest-pre.txt.gz.sha256") $(tr '\n' ' ' < "$FD/manifest-pre.summary")"
[ -f "$FD/manifest-post.done" ] && echo "post: $(cat "$FD/manifest-post.txt.gz.sha256") $(tr '\n' ' ' < "$FD/manifest-post.summary")" || echo "post manifest still running"
