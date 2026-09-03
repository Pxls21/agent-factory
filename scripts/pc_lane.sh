#!/usr/bin/env bash
# pc_lane.sh — SANDBOX side. Ship a brief to the PC, run one lane there, fetch
# the report back.
#
#   scripts/pc_lane.sh <brief-file> [codex|hermes] [role]
#
# The PC side is harness-ports/bin/pc-lane.sh. This script only moves the brief
# over, launches that detached, polls, and brings report.md home.
#
# ---------------------------------------------------------------------------
# Bridge rules this obeys (docs/PC-BRIDGE-RUNBOOK.md — read those sections
# before changing anything here; each of these was learned from an incident):
#
#   "Bridge calls cap at ~120s client-side — long waits poll LOCALLY"
#     A lane takes minutes. So the PC-side run is DETACHED and this script polls
#     from the sandbox with SHORT probes — one test per call, never a sleep loop
#     inside a bridge call. An 11-minute in-call watch that once appeared to work
#     was luck-of-the-retry, not a contract.
#
#   "Bridge-launched background processes MUST self-guard"
#     A curl timeout does NOT mean the command did not run; the retry can spawn
#     concurrent copies. The launch below is therefore replay-idempotent, and the
#     guard lives PC-SIDE inside pc-lane.sh (report exists -> re-print; pidfile
#     alive -> do not start a second lane). Rule 1b applies too: the guard keys
#     on the STATE it intends to create, not on mutual exclusion, because a
#     kill+relaunch would defeat a plain flock.
#
#   The REPLAY hazard
#     Every mutating call here is safe to run twice. Nothing kills anything.
#
# SECRETS: the bridge token is read from the environment or the untracked
# .pc-bridge.env (matching scripts/pc.sh). It is never echoed and never passed
# as an argv element that would show up in `ps`. The token reaches curl through
# `--config -` on STDIN — the one channel that is neither the process table nor
# the filesystem.
#   export PC_BRIDGE_URL=...   export PC_BRIDGE_TOKEN=...
# ---------------------------------------------------------------------------
set -uo pipefail

die() { echo "pc_lane: $*" >&2; exit 64; }

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[ -f "$ROOT/.pc-bridge.env" ] && . "$ROOT/.pc-bridge.env"
# The env file holds plain KEY=value lines; the bridge() helper below is a python child and
# only sees EXPORTED variables (bit 2026-09-03 on the first real lane: KeyError PC_BRIDGE_URL).
export PC_BRIDGE_URL PC_BRIDGE_TOKEN 2>/dev/null || true

BRIEF="${1:-}"; HARNESS="${2:-codex}"; ROLE="${3:-}"
[ -n "$BRIEF" ] || die "usage: scripts/pc_lane.sh <brief-file> [codex|hermes] [role]"
[ -f "$BRIEF" ] || die "brief not found: $BRIEF"
[ -n "${PC_BRIDGE_URL:-}" ]   || die "PC_BRIDGE_URL not set (see the current-links doc or .pc-bridge.env)"
[ -n "${PC_BRIDGE_TOKEN:-}" ] || die "PC_BRIDGE_TOKEN not set — export it or add to .pc-bridge.env"

: "${PC_AF_REPO:=\$HOME/agent-factory}"   # expanded PC-side, not here
: "${POLL_SECONDS:=15}"
: "${MAX_POLLS:=240}"                            # 240 * 15s = 60 min
OUT="${OUT_DIR:-$(dirname "$BRIEF")}"

PIN="$(grep -oiE '^[[:space:]]*(PIN|SHA|BASE)[[:space:]:]+[0-9a-f]{7,40}' "$BRIEF" \
        | head -1 | grep -oiE '[0-9a-f]{7,40}$' || true)"
[ -n "$PIN" ] || die "brief pins no SHA — add 'PIN: <sha>'. pc-lane.sh refuses to guess."
LANE_ID="$(basename "$BRIEF" | tr -c 'A-Za-z0-9_.-' '-' | cut -c1-40)-${PIN:0:8}"

# One place that speaks to the bridge. The command travels as JSON so quoting
# survives the trip.
#
# Bridge contract matches scripts/pc.sh: header X-Agent-Token, Connection: close,
# retry on non-JSON (connection-poisoning quirk — PC-BRIDGE.md), POST to /exec.
# The token reaches curl through `--config -` on STDIN, never as an argv element
# and never in a file. Stdin is the one channel that is neither the process table
# nor the filesystem.
bridge() { # bridge <shell-command>
  python3 - "$1" <<'PY'
import json, os, subprocess, sys, tempfile, time
cmd = sys.argv[1]
body = json.dumps({"cmd": cmd}).encode()
with tempfile.NamedTemporaryFile("wb", suffix=".json", delete=False) as fh:
    fh.write(body)                    # the command is not secret; the token is
    data_path = fh.name
try:
    url = os.environ["PC_BRIDGE_URL"].rstrip("/") + "/exec"
    cfg = (
        f'url = "{url}"\n'
        'request = "POST"\n'
        'header = "Content-Type: application/json"\n'
        f'header = "X-Agent-Token: {os.environ["PC_BRIDGE_TOKEN"]}"\n'
        'header = "Connection: close"\n'
        f'data-binary = "@{data_path}"\n'
        'silent\nshow-error\nmax-time = 110\n'
    )
    # Connection: close + retry-on-non-JSON: both required (connection-poisoning
    # quirk, PC-BRIDGE.md). Matches scripts/pc.sh retry contract.
    r = None
    for attempt in range(3):
        r = subprocess.run(["curl", "--config", "-"], input=cfg,
                           capture_output=True, text=True)
        if r.stdout.lstrip().startswith("{"):
            break
        if attempt < 2:
            time.sleep(1)
    sys.stdout.write(r.stdout)
    # curl's stderr carries harmless per-call noise on this bridge (the runbook
    # says to ignore the bash-hook "bind" warnings), so surface it ONLY when the
    # call actually failed. Blanket-suppressing it would hide real errors, and a
    # silent bridge failure reads exactly like a lane that produced nothing.
    if r.returncode != 0:
        sys.stderr.write(f"bridge: curl exited {r.returncode}\n{r.stderr}")
finally:
    os.unlink(data_path)
PY
}

echo "pc_lane: lane=$LANE_ID harness=$HARNESS role=${ROLE:-none} pin=$PIN" >&2

# --- 1. ship the brief -------------------------------------------------------
# base64 so arbitrary brief content (quotes, $(), backticks) survives the trip
# without shell interpretation on either side.
B64="$(base64 -w0 < "$BRIEF")"
REMOTE_BRIEF="$PC_AF_REPO/.lanes/$LANE_ID/brief.md"
bridge "mkdir -p $PC_AF_REPO/.lanes/$LANE_ID && printf %s '$B64' | base64 -d > $REMOTE_BRIEF && wc -c $REMOTE_BRIEF" \
  || die "failed to ship the brief"

# --- 2. launch DETACHED (replay-idempotent) ----------------------------------
# setsid + </dev/null + redirected output: a bridge curl that times out must not
# take the lane down with it. pc-lane.sh's own state guard makes a replayed
# launch a no-op rather than a second lane.
LAUNCH="cd $PC_AF_REPO && setsid env LANE_ID=$LANE_ID \
  bash harness-ports/bin/pc-lane.sh $REMOTE_BRIEF $HARNESS ${ROLE:-} \
  > .lanes/$LANE_ID/launch.log 2>&1 < /dev/null & echo launched"
bridge "$LAUNCH" || die "launch call failed (it may still have started — polling anyway)"

# --- 3. poll LOCALLY, short probes ------------------------------------------
REMOTE_REPORT="$PC_AF_REPO/.lanes/$LANE_ID/report.md"
echo "pc_lane: polling every ${POLL_SECONDS}s (max $((POLL_SECONDS*MAX_POLLS/60)) min)…" >&2
i=0; done_flag=0
while [ "$i" -lt "$MAX_POLLS" ]; do
  i=$((i+1))
  probe="$(bridge "test -s $REMOTE_REPORT && echo READY || (pgrep -f '[p]c-lane.sh' >/dev/null && echo RUNNING || echo GONE)")"
  case "$probe" in
    *READY*)   done_flag=1; break;;
    *RUNNING*) ;;
    *GONE*)    echo "pc_lane: no report and no live lane process — check .lanes/$LANE_ID/launch.log" >&2
               done_flag=2; break;;
  esac
  sleep "$POLL_SECONDS"
done

if [ "$done_flag" = 0 ]; then
  echo "pc_lane: timed out after $((POLL_SECONDS*MAX_POLLS/60)) min. The lane may still be running;" >&2
  echo "         re-run this script — the PC-side guard makes it resume, not restart." >&2
  exit 75
fi

# --- 4. bring the report home ------------------------------------------------
mkdir -p "$OUT"
LOCAL_REPORT="$OUT/report-$LANE_ID.md"
bridge "test -s $REMOTE_REPORT && base64 -w0 $REMOTE_REPORT" > "$LOCAL_REPORT.b64" 2>/dev/null
if [ -s "$LOCAL_REPORT.b64" ] && base64 -d < "$LOCAL_REPORT.b64" > "$LOCAL_REPORT" 2>/dev/null; then
  rm -f "$LOCAL_REPORT.b64"
  echo "pc_lane: report -> $LOCAL_REPORT" >&2
  cat "$LOCAL_REPORT"
  [ "$done_flag" = 2 ] && exit 70
  exit 0
fi
rm -f "$LOCAL_REPORT.b64"
echo "pc_lane: could not fetch the report. Tail of the PC-side log:" >&2
bridge "tail -40 $PC_AF_REPO/.lanes/$LANE_ID/lane.log 2>/dev/null; tail -20 $PC_AF_REPO/.lanes/$LANE_ID/launch.log 2>/dev/null" >&2
exit 70
