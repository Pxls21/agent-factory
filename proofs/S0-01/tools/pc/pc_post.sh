#!/usr/bin/env bash
# pc_post.sh — close a leg: process scan, masked log, backend record window, post manifest,
# teardown BY PIDFILE (non-shutdown legs), teardown scan, leak guard.
# Contract v2.1 §12-§14. Kills ONLY pids recorded by our own instruments after an exe check (AF-AP-34).
set -u
BASE=/home/rocco/s0-01-pinned; L=$BASE/.markers; SEC=$BASE/.secrets; REPO=${S0_01_REPO:-/home/rocco/agent-factory}
# `pc_post.sh scan after|teardown <framedir>` runs ONLY the scan (the sandbox producer test drives it this way;
# S0_01_REPO points at the checkout whose pins.py to read). Everything else needs the PC markers.
FD=$(cat $L/current-framedir 2>/dev/null || true); RECDIR=$(cat $L/backend-recdir 2>/dev/null || true)
BA=$BASE/buzz/target/release/buzz-acp; TEE=$REPO/proofs/S0-01/tools/frame_tee.py; HERMES=$BASE/.venv-hermes/bin/hermes-acp
# Process observation v2.3 (audit P1 "cleanup and identity"; checkpoint-5 audit "empty scan rejected /
# owned survivor accepted"): the OWNED set is the full descendant closure of the buzz-acp pid (generic
# children included), computed from the complete process table IN MEMORY (never persisted — other users'
# argv stay private). Line 1 is the ENUMERATION HEADER `# process-scan v2.3 mode=<after|teardown>
# rows=<live full-table rows> buzz_acp_pid=<pid|none> buzz_present=<0|1> owned=<closure size>
# owned_present=<owned pids still LIVE> pinned_present=<live rows naming a pinned path>
# owned_zombies=<owned pids exited but not yet reaped — never survivors> utc=<ts>` —
# it lets the checker tell "enumeration ran and found nothing owned" (a successful shutdown) from "no
# scan ran"; then one `<pid> <ppid> <etimes> <cmd>` line per owned process plus every line naming a pinned
# path; owned-pids.json lists the closure.
scan() { python3 - "$1" "$2" "$REPO" <<'PY'
import datetime, json, subprocess, sys
mode, fd, repo = sys.argv[1], sys.argv[2], sys.argv[3]
if mode not in ("after", "teardown"):
    sys.exit(f"scan: mode must be after|teardown, got {mode!r}")
sys.path.insert(0, f"{repo}/proofs/S0-01")
import pins  # the ONLY pin source — the pinned paths are never repeated as literals here
PINNED = (pins.PINNED_BUZZ_ACP_EXE_REALPATH, pins.PINNED_AGENT_REALPATH, pins.PINNED_TEE_PATH)
rows = []
zombies = set()
for line in subprocess.run(["ps", "-eo", "pid,ppid,etimes,stat,args", "--no-headers"], capture_output=True, text=True).stdout.splitlines():
    parts = line.split(None, 4)
    if len(parts) < 5:
        continue
    if parts[3].startswith("Z"):
        # exited but not yet reaped by its parent: no execution, no resources — never a survivor
        # (a SIGKILLed child stays in the table as <defunct> until its parent waits on it)
        zombies.add(int(parts[0]))
        continue
    rows.append((int(parts[0]), int(parts[1]), int(parts[2]), parts[4]))
try:
    buzz = int(open(f"{fd}/buzz-acp.pid").read().strip())
except (OSError, ValueError):
    buzz = None
if mode == "after":
    try:
        ready = json.load(open(f"{fd}/owned-pids.json"))
        owned = set(ready.get("owned", []))
    except (OSError, ValueError):
        owned = set()
    if buzz is not None and any(r[0] == buzz for r in rows):
        owned.add(buzz)
        changed = True
        while changed:
            changed = False
            for pid, ppid, _, _ in rows:
                if ppid in owned and pid not in owned:
                    owned.add(pid); changed = True
    json.dump({"buzz_acp_pid": buzz, "owned": sorted(owned), "taken_at": "ready+after"}, open(f"{fd}/owned-pids.json", "w"), indent=1)
else:
    owned = set(json.load(open(f"{fd}/owned-pids.json"))["owned"])
keep = [r for r in rows if r[0] in owned or any(p in r[3] for p in PINNED)]
keep = [r for r in keep if "pc_post.sh" not in r[3] and " ps -eo " not in r[3]]
table_pids = {r[0] for r in rows}
header = (f"# process-scan v2.3 mode={mode} rows={len(rows)} buzz_acp_pid={buzz if buzz is not None else 'none'} "
          f"buzz_present={int(buzz in table_pids)} owned={len(owned)} owned_present={len(owned & table_pids)} "
          f"pinned_present={sum(1 for r in rows if any(p in r[3] for p in PINNED))} owned_zombies={len(owned & zombies)} "
          f"utc={datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
with open(f"{fd}/process-scan-{mode}.txt", "w") as out:
    out.write(header + "\n")
    for pid, ppid, et, cmd in sorted(keep):
        out.write(f"{pid} {ppid} {et} {cmd}\n")
print(f"scan-{mode}: {len(keep)} lines, owned={len(owned)}, owned_present={len(owned & table_pids)}")
PY
}
if [ "${1:-}" = "scan" ]; then scan "${2:?after|teardown}" "${3:?framedir}"; exit $?; fi
mask() { tr -d "\000" < "$1" | sed -E "s#\x1b\[[0-9;]*m##g; s#[a-f0-9]{64}#<HEX>#g"; }
echo "=== post: $FD ==="
scan after "$FD"
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
  sleep 1; scan teardown "$FD"
fi
[ -f "$FD/process-scan-teardown.txt" ] || scan teardown "$FD"
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
