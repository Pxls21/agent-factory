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
# bash reads a script LAZILY: an edit to this file while an instance runs corrupts that run at a byte offset (2026-09-08: the D5l
# poller died with "syntax error near ')'" at line 123 after the FAILED-handling edit landed mid-poll, and exited 0 without
# bringing the report home). Run from a private copy of these bytes; the file on disk may change underneath a live run.
if [ -z "${PC_LANE_SELF_COPY:-}" ]; then
  _self="$(mktemp "${TMPDIR:-/tmp}/pc_lane.sh.XXXXXX")" && cp "$0" "$_self" && PC_LANE_SELF_COPY="$_self" PC_LANE_ORIG="$0" exec bash "$_self" "$@"
fi
trap 'rm -f "$PC_LANE_SELF_COPY"' EXIT
set -uo pipefail

die() { echo "pc_lane: $*" >&2; exit 64; }

# --- headroom admission (testable unit) ----------------------------------------
# Defaults: the 2026-09-15 incident — 4 lanes hit full swap + 3 MB local disk.
# 256 MB disk catches a write-space crisis; 512 MB memory catches swap exhaustion.
: "${PC_LANE_MIN_DISK_MB:=256}"
: "${PC_LANE_MIN_MEM_MB:=512}"

# _admit_verdict <local_disk_mb> <pc_mem_mb> <pc_disk_mb>
#   -1 = unknown (probe failed) — skipped (fail-open).
#   Prints "admit" or "defer: <reason>". Returns 0 or 1.
_admit_verdict() {
  local ld="$1" pm="$2" pd="$3"
  [ "$ld" -ge 0 ] 2>/dev/null && [ "$ld" -lt "$PC_LANE_MIN_DISK_MB" ] && {
    echo "defer: local disk ${ld} MB below floor ${PC_LANE_MIN_DISK_MB} MB"; return 1; }
  [ "$pm" -ge 0 ] 2>/dev/null && [ "$pm" -lt "$PC_LANE_MIN_MEM_MB" ] && {
    echo "defer: PC memory ${pm} MB below floor ${PC_LANE_MIN_MEM_MB} MB"; return 1; }
  [ "$pd" -ge 0 ] 2>/dev/null && [ "$pd" -lt "$PC_LANE_MIN_DISK_MB" ] && {
    echo "defer: PC disk ${pd} MB below floor ${PC_LANE_MIN_DISK_MB} MB"; return 1; }
  if [ "$pm" -lt 0 ] 2>/dev/null && [ "$pd" -lt 0 ] 2>/dev/null; then
    echo "pc_lane: headroom unknown: PC probe unreachable — admitted (fail-open)" >&2
  fi
  echo "admit"
  return 0
}

# _parse_free_mem_mb: stdin = free -m output -> stdout = available MB (or -1).
_parse_free_mem_mb() {
  awk 'NR==1{for(i=1;i<=NF;i++)if($i=="available")ac=i+1}
       /^Mem:/{if(ac+0>0)print $(ac);else print -1;f=1}
       END{if(!f)print -1}'
}

# _parse_df_avail_mb: stdin = df -P output -> stdout = available MB (or -1).
_parse_df_avail_mb() {
  awk 'NR==2{print int($4/1024);f=1} END{if(!f)print -1}'
}

ROOT="$(cd "$(dirname "${PC_LANE_ORIG:-${BASH_SOURCE[0]}}")/.." && pwd)"
[ -f "$ROOT/.pc-bridge.env" ] && . "$ROOT/.pc-bridge.env"
# The env file holds plain KEY=value lines; the bridge() helper below is a python child and
# only sees EXPORTED variables (bit 2026-09-03 on the first real lane: KeyError PC_BRIDGE_URL).
export PC_BRIDGE_URL PC_BRIDGE_TOKEN 2>/dev/null || true

# admit-check subcommand — the testable unit for headroom admission.
if [ "${1:-}" = "admit-check" ]; then
  shift
  case "${1:-}" in
    --parse-free) _parse_free_mem_mb; exit;;
    --parse-df) _parse_df_avail_mb; exit;;
    *) [ $# -ge 3 ] || die "admit-check: requires 3 args (local_disk_mb pc_mem_mb pc_disk_mb)"
       _admit_verdict "$1" "$2" "$3"; exit $?;;
  esac
fi

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
[ -z "${PC_LANE_BRIDGE_FN:-}" ] || . "$PC_LANE_BRIDGE_FN"
if ! declare -F bridge >/dev/null; then
  bridge() { # bridge <shell-command>  -> remote stdout on stdout, remote stderr on stderr, remote rc
    # The envelope unwrapping lives in scripts/pc_bridge_exec.py (tested by
    # harness-ports/tests/test_pc_bridge_exec.py). Bit 2026-09-03: the inline version printed the
    # JSON envelope, so the poll "worked" by substring luck and the report fetch base64-decoded JSON.
    python3 "$ROOT/scripts/pc_bridge_exec.py" "$1"
  }
fi

echo "pc_lane: lane=$LANE_ID harness=$HARNESS role=${ROLE:-none} pin=$PIN" >&2

# --- 1. ship the brief -------------------------------------------------------
# The effort-only seam exits before bridge I/O so its role table is testable without the PC.
server_effort_for_role() { # role [HERMES_MODEL] [HERMES_REASONING] -> the server effort, or "" for a cloud route
  local role="$1" model="${2:-}" eff="${3:-}"
  case "$role" in code-implementer) : "${model:=agentfactory-build-local}"; : "${eff:=medium}";;
                  adversarial-verifier) : "${model:=agentfactory-verify-local}"; : "${eff:=xhigh}";;
                  *) [ -n "$model" ] || { echo ""; return; };; esac
  case "$model" in agentfactory-*-local|qwen-local/*) ;; *) echo ""; return;; esac
  case "$eff" in low|medium|xhigh) echo "$eff";; high|ultra|max) echo xhigh;; "") echo medium;; *) echo xhigh;; esac
}
SERVER_EFFORT="${LANE_SERVER_EFFORT:-$(server_effort_for_role "${ROLE:-}" "${HERMES_MODEL:-}" "${HERMES_REASONING:-}")}"
if [ "${LANE_PRINT_EFFORT:-0}" = 1 ]; then echo "server-effort=${SERVER_EFFORT:-<cloud route>}"; exit 0; fi

# --- 0. headroom admission check -----------------------------------------------
if [ "${PC_LANE_SKIP_ADMIT:-0}" != 1 ]; then
  _adm_ld="$(df -P "${PC_LANE_LOCAL_MOUNT:-$ROOT}" 2>/dev/null | _parse_df_avail_mb)"
  [ "$_adm_ld" -ge 0 ] 2>/dev/null || _adm_ld=-1
  _adm_pm=-1; _adm_pd=-1
  if declare -F bridge >/dev/null 2>&1; then
    _adm_raw="$(bridge 'free -m 2>/dev/null; echo __ADMSEP__; df -P /home 2>/dev/null' 2>/dev/null)" || _adm_raw=""
    if [ -n "$_adm_raw" ]; then
      _adm_pm="$(printf '%s\n' "$_adm_raw" | sed '/__ADMSEP__/,$d' | _parse_free_mem_mb)"
      _adm_pd="$(printf '%s\n' "$_adm_raw" | sed '1,/__ADMSEP__/d' | _parse_df_avail_mb)"
    fi
  fi
  [ "$_adm_pm" -ge 0 ] 2>/dev/null || _adm_pm=-1
  [ "$_adm_pd" -ge 0 ] 2>/dev/null || _adm_pd=-1
  _adm_v="$(_admit_verdict "$_adm_ld" "$_adm_pm" "$_adm_pd")"
  _adm_rc=$?
  if [ $_adm_rc -ne 0 ]; then
    echo "pc_lane: DEFERRED — $_adm_v" >&2; exit 75
  fi
fi

# --- 1. ship the brief -------------------------------------------------------
# base64 so arbitrary brief content (quotes, $(), backticks) survives the trip
# without shell interpretation on either side.
B64="$(base64 -w0 < "$BRIEF")"
REMOTE_BRIEF="$PC_AF_REPO/.lanes/$LANE_ID/brief.md"
bridge "mkdir -p $PC_AF_REPO/.lanes/$LANE_ID && printf %s '$B64' | base64 -d > $REMOTE_BRIEF && wc -c $REMOTE_BRIEF" \
  || die "failed to ship the brief"

# --- 1b. ship an optional patch: a sandbox lane's uncommitted files on top of the PIN ---------------
# LANE_PATCH=<git diff> (2026-09-08: the quota stop left five sandbox lanes' files uncommitted and the owner
# routed the next rounds to the PC — the PC lane must start from PIN + those bytes). Shipped in 40 000-char
# slices like pc_suite.sh (the bridge caps one reply/request), sha-verified on the PC, applied by pc-lane.sh
# with `git apply --index` before the harness starts; a patch that does not apply is a FAILED lane.
if [ -n "${LANE_PATCH:-}" ]; then
  [ -s "$LANE_PATCH" ] && grep -q '^diff --git' "$LANE_PATCH" || die "LANE_PATCH=$LANE_PATCH is not a non-empty git diff"
  PSHA="$(sha256sum "$LANE_PATCH" | cut -d' ' -f1)"; RD="$PC_AF_REPO/.lanes/$LANE_ID"
  PB64="$(mktemp)"; base64 -w0 < "$LANE_PATCH" > "$PB64"; PTOTAL="$(wc -c < "$PB64")"; i=0; off=0
  bridge "rm -f $RD/part.*" >/dev/null
  while [ "$off" -lt "$PTOTAL" ]; do
    CH="$(dd if="$PB64" bs=1 skip="$off" count=40000 2>/dev/null)"
    bridge "printf %s '$CH' > $RD/part.$(printf %04d $i)" >/dev/null || die "lane patch part $i failed"
    off=$((off+40000)); i=$((i+1))
  done
  rm -f "$PB64"
  PGOT="$(bridge "cat $RD/part.* | base64 -d > $RD/lane.patch && rm -f $RD/part.* && sha256sum $RD/lane.patch | cut -d' ' -f1" | tail -1)"
  [ "$PGOT" = "$PSHA" ] || die "lane patch sha mismatch on the PC (got ${PGOT:-nothing}, want $PSHA)"
  echo "pc_lane: lane patch shipped — $(grep -c '^diff --git' "$LANE_PATCH") file(s), sha ${PSHA:0:12} (applied on the PIN by pc-lane.sh)" >&2
fi

# --- 1c. the LOCAL model's effort is set at the SERVER per lane role (2026-09-14) ----------------------
# Measured that day: this llama-server build ignores a top-level `reasoning_effort` (a `max` answered normally where the
# Qwen3.8 template would raise) and Hermes sends no per-request template kwargs, so the effort a lane runs at is the
# server's own `--chat-template-kwargs` default. Build lanes run at medium, verify lanes at xhigh (owner 2026-09-14:
# build and verify alternate on the one slot), so the dispatcher queues a deferred restart BEFORE launch when the running
# process's `reasoning_effort` differs. It waits for qwen-server.sh's terminal record for the exact pending env sha; a lane
# never starts against the wrong server effort. The per-request path
# (`chat_template_kwargs.reasoning_effort`, forwarded by OmniRoute — proven by the same raise) is the refinement for
# concurrent mixed efforts; it needs a Hermes profile `extra_body` and is not wired.
if [ -n "$SERVER_EFFORT" ] && [ "${LANE_SET_SERVER_EFFORT:-1}" = 1 ]; then
  QWEN_PENDING_LOG="${QWEN_PENDING_LOG:-$PC_AF_REPO/qwen-builder/logs/deferred-restart.log}"
  # The MainPID lookup + argv read runs ON THE PC. systemctl --user needs XDG_RUNTIME_DIR (the bridge
  # shell has none) and the substitutions are ESCAPED so they resolve on the PC, not in the sandbox:
  # an unescaped $(systemctl ...) inside this double-quoted bridge argument expands LOCALLY to empty
  # (the sandbox has no user bus), which silently read /proc//cmdline (= the kernel cmdline) and
  # forced a false 'mismatch' that queued a needless restart (AF-AP-89). MP is passed as argv, not
  # interpolated into the quoted heredoc (a quoted heredoc is not PC-expanded).
  EFF_STATE="$(bridge "export XDG_RUNTIME_DIR=/run/user/\$(id -u); MP=\$(systemctl --user show -p MainPID --value qwen-builder 2>/dev/null); python3 - \"\$MP\" <<'PY'
import sys
wanted = '$SERVER_EFFORT'
mp = sys.argv[1] if len(sys.argv) > 1 else ''
if not mp or mp == '0':
    # qwen-builder llama-server is not running (vLLM is the local server since D-032). Its
    # chat-template-kwargs effort default does not apply, and restarting the retired unit would
    # collide with vLLM on :8080/GPU. Never manage effort against it — run at the vLLM default.
    print('inactive'); sys.exit(0)
seen = ''
for raw in open('/proc/' + mp + '/cmdline', 'rb').read().split(b'\\0'):
    text = raw.decode('utf-8', 'replace')
    if 'reasoning_effort' in text:
        seen = text.split('reasoning_effort', 1)[1].lstrip('\\\" :=').split('\\\"', 1)[0].split('}', 1)[0]
        break
print('match' if seen == wanted else 'mismatch:' + (seen or 'unknown'))
PY")" || die "server effort not read from the running argv"
  if [ "$EFF_STATE" = inactive ]; then
    echo "pc_lane: local route — qwen-builder llama-server not running (vLLM is the local server since D-032); server-effort restart skipped, lane runs at the vLLM server default" >&2
  elif [ "$EFF_STATE" != match ]; then
    echo "pc_lane: local route — queueing server effort $SERVER_EFFORT and waiting before launch" >&2
    EFF_OUT="$(bridge "cd $PC_AF_REPO && QWEN_EFFORT=$SERVER_EFFORT bash harness-ports/bin/qwen-server.sh restart-when-idle --max-wait 1800")" || die "server effort restart not queued: ${EFF_OUT##*$'\n'}"
    case "$EFF_OUT" in
      *already\ applied*) echo "pc_lane: server effort already applied" >&2;;
      *pending:\ watcher*)
        EFF_SHA="$(bridge "sha256sum $PC_AF_REPO/qwen-builder/pending/env | cut -d' ' -f1 | cut -c1-12")" || die "server effort pending env sha unavailable"
        [ -n "$EFF_SHA" ] || die "server effort pending env sha empty"
        EFF_WAIT_POLLS="${LANE_EFFORT_WAIT_POLLS:-360}"; EFF_WAIT_SECONDS="${LANE_EFFORT_WAIT_SECONDS:-5}"; EFF_I=0; EFF_DONE=0
        while [ "$EFF_I" -lt "$EFF_WAIT_POLLS" ]; do
          EFF_I=$((EFF_I+1))
          EFF_TERM="$(bridge "grep -E '^(applied|expired|failed) .* env-sha=$EFF_SHA( |$)' $QWEN_PENDING_LOG | tail -1" 2>/dev/null || true)"
          case "$EFF_TERM" in
            applied\ *) echo "pc_lane: server effort applied ($EFF_SHA)" >&2; EFF_DONE=1; break;;
            expired\ *) die "server effort expired: ${EFF_TERM##*blocked-by=}";;
            failed\ *) EFF_RC="${EFF_TERM##* rc=}"; echo "pc_lane: server effort failed rc=$EFF_RC" >&2; exit "${EFF_RC:-64}";;
          esac
          sleep "$EFF_WAIT_SECONDS"
        done
        [ "$EFF_DONE" -eq 1 ] || die "server effort wait ended without a terminal record for env-sha=$EFF_SHA"
        ;;
      *) die "server effort restart returned no pending or already-applied state: ${EFF_OUT##*$'\n'}";;
    esac
  fi
fi

# --- 2. launch DETACHED (replay-idempotent) ----------------------------------
# setsid + </dev/null + redirected output: a bridge curl that times out must not
# take the lane down with it. pc-lane.sh's own state guard makes a replayed
# launch a no-op rather than a second lane.
# Forward the per-lane overrides the PC runner honours (model/effort/profile/toolsets) —
# without this the first route probe silently ran the role default (2026-09-03).
FWD=""
# 2026-09-08: the capacity-retry knobs travel too — under route contention the PC default (3 retries, 60 s doubling)
# gave up in ~7 min while the admitted sibling lanes were still refusing to yield a slot.
for v in HERMES_MODEL HERMES_REASONING HERMES_PROFILE HERMES_TOOLSETS LANE_BRANCH LANE_CAPACITY_RETRIES LANE_CAPACITY_BACKOFF LANE_CAPACITY_MAX_WAIT; do
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
  # A report that is only the route's refusal line is NOT ready: pc-lane.sh keeps that line in report.md during its
  # capacity-retry backoff, and the poller read it as READY and brought the refusal home as the lane's report — for six
  # lanes at once, A5k's five-hour tree included (2026-09-08 08:1xZ). The retry loop's next attempt truncates it; until
  # then the lane is RUNNING.
  # The no-pidfile fallback is bounded to the LAUNCH WINDOW (launch.log younger than 5 min): the old `pgrep -f pc-lane.sh`
  # matched any SIBLING lane's launcher shell, so a poller whose own lane had been stopped by pid polled RUNNING for hours
  # (two stale pollers on 2026-09-08 — the owner saw seven background tasks for four lanes).
  # A Hermes `No reply:` line (session_persistence_failed — the shared state.db refused a write, 2026-09-08 13:3xZ, VERIFY-B5j
  # at item 5) is the harness failing, the same class as a refusal: never READY; FAILED-UNRETRIED once the loop is dead.
  # READY also needs the lane LOOP gone (its pidfile is removed by pc-lane.sh's exit trap): report.md is complete the moment the
  # harness exits, but the transcript export into the tree runs AFTER that, and a fetch in between ships the stale staged
  # transcript (2026-09-08 15:20Z, VERIFY-B5j: the resumed session's 631-line transcript came home as the dead attempt's 990).
  probe="$(bridge "test -f $PC_AF_REPO/.lanes/$LANE_ID/FAILED && echo FAILED || (test -s $REMOTE_REPORT && grep -Eq '^API call failed|^(⚠️ )?No reply: ' $REMOTE_REPORT && ! kill -0 \$(cat $PC_AF_REPO/.lanes/$LANE_ID/lane.pid 2>/dev/null) 2>/dev/null && echo FAILED-UNRETRIED) || (test -s $REMOTE_REPORT && ! grep -Eq '^API call failed|^(⚠️ )?No reply: ' $REMOTE_REPORT && ! kill -0 \$(cat $PC_AF_REPO/.lanes/$LANE_ID/lane.pid 2>/dev/null) 2>/dev/null && echo READY || (kill -0 \$(cat $PC_AF_REPO/.lanes/$LANE_ID/lane.pid 2>/dev/null) 2>/dev/null && echo RUNNING || (test ! -f $PC_AF_REPO/.lanes/$LANE_ID/lane.pid && [ -n \"\$(find $PC_AF_REPO/.lanes/$LANE_ID/launch.log -mmin -5 2>/dev/null)\" ] && echo RUNNING || echo GONE)))")"
  case "$probe" in
    *FAILED-UNRETRIED*) echo "pc_lane: LANE FAILED — the harness died on an API failure the PC side did not retry (the line stands as report.md; not a report). Reason:" >&2
               bridge "head -c 300 $REMOTE_REPORT" >&2 2>/dev/null
               echo "pc_lane: remove .lanes/$LANE_ID/report.md on the PC and re-dispatch (the tree keeps the work)" >&2
               exit 70;;
    *FAILED*)  echo "pc_lane: LANE FAILED — the PC route refused every attempt (no report to grade). Reason:" >&2
               bridge "cat $PC_AF_REPO/.lanes/$LANE_ID/FAILED" >&2 2>/dev/null
               echo "pc_lane: re-dispatch later, or run the lane in the sandbox (code-implementer); the lane dir keeps the refusal" >&2
               exit 70;;
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
