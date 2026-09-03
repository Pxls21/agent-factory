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
bridge() { # bridge <shell-command>  -> remote stdout on stdout, remote stderr on stderr, remote rc
  # The envelope unwrapping lives in scripts/pc_bridge_exec.py (tested by
  # harness-ports/tests/test_pc_bridge_exec.py). Bit 2026-09-03: the inline version printed the
  # JSON envelope, so the poll "worked" by substring luck and the report fetch base64-decoded JSON.
  python3 "$ROOT/scripts/pc_bridge_exec.py" "$1"
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
# Forward the per-lane overrides the PC runner honours (model/effort/profile/toolsets) —
# without this the first route probe silently ran the role default (2026-09-03).
FWD=""
for v in HERMES_MODEL HERMES_REASONING HERMES_PROFILE HERMES_TOOLSETS LANE_BRANCH; do
  [ -n "${!v:-}" ] && FWD="$FWD $v=$(printf %q "${!v}")"
done
LAUNCH="cd $PC_AF_REPO && setsid env LANE_ID=$LANE_ID$FWD \
  bash harness-ports/bin/pc-lane.sh $REMOTE_BRIEF $HARNESS ${ROLE:-} \
  > .lanes/$LANE_ID/launch.log 2>&1 < /dev/null & echo launched"
bridge "$LAUNCH" || die "launch call failed (it may still have started — polling anyway)"

# --- 3. poll LOCALLY, short probes ------------------------------------------
REMOTE_REPORT="$PC_AF_REPO/.lanes/$LANE_ID/report.md"
echo "pc_lane: polling every ${POLL_SECONDS}s (max $((POLL_SECONDS*MAX_POLLS/60)) min)…" >&2
i=0; done_flag=0
while [ "$i" -lt "$MAX_POLLS" ]; do
  i=$((i+1))
  # Liveness is THIS lane's pidfile (two lanes now run concurrently; a bare pgrep for any
  # pc-lane.sh would report a dead lane as RUNNING while its sibling is alive — 2026-09-03).
  # The pgrep stays as the fallback for the launch window before the pidfile exists.
  probe="$(bridge "test -s $REMOTE_REPORT && echo READY || (kill -0 \$(cat $PC_AF_REPO/.lanes/$LANE_ID/lane.pid 2>/dev/null) 2>/dev/null && echo RUNNING || (test ! -f $PC_AF_REPO/.lanes/$LANE_ID/lane.pid && pgrep -f '[p]c-lane.sh' >/dev/null && echo RUNNING || echo GONE))")"
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
  # Bring the lane's CHANGES home too (the lane never pushes): stage everything in the pinned
  # worktree and ship the cached diff. Apply in the sandbox with `git apply --index <patch>` on
  # a branch at the same PIN, then review/gate/commit here. Added 2026-09-03 after the first
  # lane produced files nobody could fetch.
  LOCAL_PATCH="$OUT/patch-$LANE_ID.diff"
  # Diff against the PIN, not HEAD: a lane that commits its increments in the worktree (checkpoint
  # discipline) would otherwise ship an empty patch. Index vs PIN covers committed + uncommitted work.
  # The bridge caps a reply at ~45 KB of stdout (bit 2026-09-03: a 150 KB patch came back as its
  # last 45 KB — transcript text where "diff --git" should be). So: materialize the base64 on the
  # PC, pull it in 40,000-char slices, verify the char count, then decode.
  REMOTE_B64="$PC_AF_REPO/.lanes/$LANE_ID/patch.b64"
  TOTAL="$(bridge "cd $PC_AF_REPO/.lanes/$LANE_ID/tree 2>/dev/null && git add -A . >/dev/null 2>&1 && git diff --cached --binary $PIN | base64 -w0 > $REMOTE_B64 && wc -c < $REMOTE_B64" 2>/dev/null | tr -dc 0-9)"
  : > "$LOCAL_PATCH.b64"; GOT=0
  if [ -n "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then
    off=1; step=40000
    while [ "$off" -le "$TOTAL" ]; do
      end=$((off+step-1))
      bridge "cut -c${off}-${end} $REMOTE_B64" 2>/dev/null | tr -d '\n' >> "$LOCAL_PATCH.b64"
      off=$((end+1))
    done
    GOT="$(wc -c < "$LOCAL_PATCH.b64")"
    [ "$GOT" = "$TOTAL" ] || echo "pc_lane: patch transfer size mismatch (got $GOT of $TOTAL base64 chars)" >&2
  fi
  if [ "$GOT" != 0 ] && [ "$GOT" = "$TOTAL" ] && base64 -d < "$LOCAL_PATCH.b64" > "$LOCAL_PATCH" 2>/dev/null && grep -q '^diff --git' "$LOCAL_PATCH"; then
    echo "pc_lane: patch  -> $LOCAL_PATCH ($(grep -c '^diff --git' "$LOCAL_PATCH") file(s))" >&2
  else
    echo "pc_lane: no changes in the lane worktree (or patch fetch failed)" >&2; rm -f "$LOCAL_PATCH"
  fi
  rm -f "$LOCAL_PATCH.b64"
  cat "$LOCAL_REPORT"
  [ "$done_flag" = 2 ] && exit 70
  exit 0
fi
rm -f "$LOCAL_REPORT.b64"
echo "pc_lane: could not fetch the report. Tail of the PC-side log:" >&2
bridge "tail -40 $PC_AF_REPO/.lanes/$LANE_ID/lane.log 2>/dev/null; tail -20 $PC_AF_REPO/.lanes/$LANE_ID/launch.log 2>/dev/null" >&2
exit 70
