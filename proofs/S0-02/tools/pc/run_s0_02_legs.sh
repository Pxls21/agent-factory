#!/usr/bin/env bash
# run_s0_02_legs.sh — PC SIDE: capture the eight S0-02 legs against the isolated
# S0-01 relay stack, one fresh buzz-acp launch per leg.
#
#   bash proofs/S0-02/tools/pc/run_s0_02_legs.sh <evidence-root> [leg ...]
#
# NOT RUN IN THE SANDBOX (no relay, no key material, no bridge banner this
# session). Every PC-side step it takes is listed in the lane report.
#
# Reuse, never copy: the launcher (proofs/S0-01/tools/pc/pc_launch.py), the tee
# it spawns, and the delivery route are INVOKED. Nothing under proofs/S0-01/ is
# edited by this script.
#
# PROCESS OWNERSHIP (AF-AP-34): every process this script stops is stopped by the
# pid in ITS OWN pidfile, after /proc/<pid>/exe confirms the binary. No pkill, no
# killall, no name match — those restarted the owner's production relay four
# times on 2026-09-04.
set -euo pipefail

# Sourcing this file defines its helpers only. Argument parsing, the pin preflight,
# evidence-root creation, and the leg loop are all in main().
REPO=${S0_02_REPO:-/home/rocco/agent-factory}
PINNED=${S0_02_PINNED:-/home/rocco/s0-01-pinned}
SEC=$PINNED/.secrets
MARKERS=$PINNED/.markers
RELAY_HTTP=${S0_02_RELAY_HTTP:-http://127.0.0.1:3999}
LAUNCHER=$REPO/proofs/S0-01/tools/pc/pc_launch.py
DELIVER=$REPO/proofs/S0-02/tools/pc/deliver_event.py
PINS=$REPO/proofs/S0-01/pins.py
# The S0-01 launcher parks each leg's frames here; --leg run-1 is reused because
# pc_launch.py restricts --leg to pins.LEGS and S0-01 is not edited by this lane.
HOST_LEG=run-1
FD=$MARKERS/v2-$HOST_LEG
TURN_WAIT_S=${S0_02_TURN_WAIT_S:-100}
POLL_S=5
# Named return code for the neg-replayed leg: the final live timeline is not an
# exact byte extension of the first snapshot (issue #17 step 5). 8 is free — the
# codes in use before this lane are 0,3,4,5,6,7,9.
S0_02_REPLAY_PREFIX_MISMATCH=8

ALL_LEGS="pos-allowed neg-unauthorized neg-bad-signature neg-replayed neg-stale neg-self-authored neg-not-allowlisted revoked"

say() { echo; echo "===== [S0-02] $* ====="; }

launch_leg() {
  # D3: a previous run owns only these three launcher markers. Preserve the
  # framedir itself, which also carries the current leg's evidence.
  rm -f "$FD/launch.ready" "$FD/buzz-acp.exit" "$FD/buzz-acp.pid"
  rm -f "$MARKERS/s0-02.launch.log"
  setsid /usr/bin/python3 "$LAUNCHER" --leg "$HOST_LEG" --model s0-01-pong \
    --env-set s0-02 \
    </dev/null >"$MARKERS/s0-02.launch.log" 2>&1 &
  for _ in $(seq 1 24); do
    [ -f "$FD/launch.ready" ] && return 0
    if [ -f "$FD/buzz-acp.exit" ]; then
      echo "launch died before ready:" >&2; tail -20 "$MARKERS/s0-02.launch.log" >&2; return 4
    fi
    sleep "$POLL_S"
  done
  echo "launch never became ready" >&2; tail -20 "$MARKERS/s0-02.launch.log" >&2; return 4
}

# Stop ONLY the process this leg started, by its own pidfile, after /proc confirms it.
stop_leg() {
  local pidfile="$FD/buzz-acp.pid" pid exe
  [ -f "$pidfile" ] || { echo "no pidfile — nothing of ours to stop"; return 0; }
  pid=$(cat "$pidfile")
  [ -n "$pid" ] && [ -d "/proc/$pid" ] || { echo "pid $pid already gone"; return 0; }
  exe=$(readlink "/proc/$pid/exe" 2>/dev/null || true)
  case "$exe" in
    *buzz-acp*) kill "$pid" ;;
    *) echo "REFUSING to kill pid $pid: /proc exe is '$exe', not our buzz-acp" >&2; return 5 ;;
  esac
  for _ in $(seq 1 12); do [ -d "/proc/$pid" ] || return 0; sleep 1; done
  echo "pid $pid did not exit after SIGTERM" >&2; return 5
}

# Wait for a turn, or for the window to close. Failure-aware: it also stops early
# when buzz-acp died, so a dead harness is never read as "no turn, as expected".
wait_turn_window() {
  local want=$1 deadline=$((SECONDS + TURN_WAIT_S)) n
  while [ "$SECONDS" -lt "$deadline" ]; do
    # grep -c emits 0 and returns 1 for a no-match file. Preserve its
    # output, neutralize only that status, then supply 0 for an absent file.
    n=$(grep -c '"method":"session/prompt"' "$FD/timeline.jsonl" 2>/dev/null || true); n=${n:-0}
    [ "$n" -ge "$want" ] && [ "$want" -gt 0 ] && return 0
    [ -f "$FD/buzz-acp.exit" ] && { echo "buzz-acp exited during the turn window" >&2; return 6; }
    sleep "$POLL_S"
  done
  return 0
}

# The turn timeline exists before the process stops. It is the only artifact
# collectable at this stage; the masked log is made by pc_post.sh after exit.
collect_leg() {
  local out=$1
  mkdir -p "$out"
  cp "$FD/timeline.jsonl" "$out/timeline.jsonl"
}

# Per-delivery DELTA model (issue #17 / D-036): the replay leg keeps ONE live
# process across both deliveries. The first snapshot is a whole-line prefix of
# the live timeline (a partial trailing line never enters it); the second
# sub-leg receives only the post-boundary bytes. Neither step fabricates lines:
# an empty delta (the relay dropped the duplicate and buzz-acp saw nothing) is
# a valid runner output. Both read the live timeline in $FD and write into the
# leg's sub-legs under the global $out (the replay leg root).
#
# snapshot_timeline : cut the live timeline at its last newline into
# $out/first/timeline.jsonl and print the snapshot's byte length.
snapshot_timeline() {
  local out=$1 size first_bytes
  mkdir -p "$out/first"
  size=$(wc -c < "$FD/timeline.jsonl")
  # Cut at the last newline: the first snapshot ends at the last \n (inclusive),
  # so a partial trailing line (the live writer mid-line) never enters it.
  # Python is the runner's existing producer-side tool (deliver/role_for use
  # it); a one-line rfind is the exact, line-independent cut.
  first_bytes=$(/usr/bin/python3 -c 'import sys; d=open(sys.argv[1],"rb").read(); p=d.rfind(b"\n"); print(p+1 if p>=0 else 0)' "$FD/timeline.jsonl")
  head -c "$first_bytes" "$FD/timeline.jsonl" > "$out/first/timeline.jsonl"
  printf '%s' "$first_bytes"
}

# delta_timeline <first_bytes> : prove the final live timeline is an exact byte
# extension of the first snapshot (cmp -n on the byte count); on a mismatch print
# the named error, write no second timeline, and return the named code. On
# success write only the post-boundary bytes to $out/second/timeline.jsonl.
delta_timeline() {
  local out=$1 first_bytes=$2
  if ! cmp -n "$first_bytes" "$out/first/timeline.jsonl" "$FD/timeline.jsonl"; then
    echo "S0-02: neg-replayed final timeline does not extend the first snapshot (prefix mismatch)" >&2
    return "$S0_02_REPLAY_PREFIX_MISMATCH"
  fi
  mkdir -p "$out/second"
  tail -c +$((first_bytes + 1)) "$FD/timeline.jsonl" > "$out/second/timeline.jsonl"
}

# The masked log is produced by the S0-01 post step (pc_post.sh:107), after the
# process exit marker. Require both post conditions; never copy buzzacp.raw.log.
collect_masked() {
  local out=$1 deadline=$((SECONDS + TURN_WAIT_S))
  while [ "$SECONDS" -lt "$deadline" ]; do
    [ -f "$FD/buzz-acp.exit" ] && [ -f "$FD/buzzacp.log" ] && break
    sleep "$POLL_S"
  done
  if [ ! -f "$FD/buzz-acp.exit" ] || [ ! -f "$FD/buzzacp.log" ]; then
    echo "S0-02: post step incomplete (need buzz-acp.exit + buzzacp.log) in $FD" >&2
    return 9
  fi
  # buzzacp.log is the MASKED log pc_post.sh writes; buzzacp.raw.log is never copied.
  cp "$FD/buzzacp.log" "$out/buzzacp.log"
  if grep -Eq '[0-9a-fA-F]{64}' "$out/buzzacp.log"; then
    echo "REFUSING to keep $out/buzzacp.log: unmasked 64-hex present" >&2
    rm -f "$out/buzzacp.log"; return 7
  fi
}

# D2: pc_post.sh is the authoritative masked-log producer. The runner invokes
# it only after stop_leg; then collect_masked waits for BOTH post artifacts.
post_leg() {
  local deadline=$((SECONDS + TURN_WAIT_S))
  while [ "$SECONDS" -lt "$deadline" ]; do
    [ -f "$FD/buzz-acp.exit" ] && break
    sleep "$POLL_S"
  done
  if [ ! -f "$FD/buzz-acp.exit" ]; then
    echo "S0-02: buzz-acp did not write $FD/buzz-acp.exit before post" >&2
    return 9
  fi
  FD="$FD" S0_01_REPO="$REPO" bash "$REPO/proofs/S0-01/tools/pc/pc_post.sh"
}

deliver() {  # deliver <fixture> <leg-dir> <role> [extra deliver_event.py args...]
  local fixture=$1 legdir=$2 role=$3; shift 3
  ( set -a; . "$SEC/$role.env"; set +a
    exec /usr/bin/python3 "$DELIVER" --fixture "$fixture" --leg-dir "$legdir" \
      --secret "$SEC/$role.env" --relay-http "$RELAY_HTTP" --t0 "$(date +%s)" "$@" )
}

role_for() {
  /usr/bin/python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["signer"]["role"])' \
    "$REPO/proofs/S0-02/fixtures/$1.json"
}

main() {
  DEST=${1:?usage: run_s0_02_legs.sh <evidence-root> [leg ...]}
  shift || true
  LEGS=${*:-$ALL_LEGS}
  # F2: the membership receipt lives OUTSIDE $out so rm -rf "$out" does not wipe it.
  MEMBERSHIP=${S0_02_MEMBERSHIP:-$DEST/revoked-membership.json}

# --- PREFLIGHT: the buzz-acp-decided legs need RUST_LOG=debug ----------------
# neg-replayed, neg-self-authored and neg-not-allowlisted are decided INSIDE
# buzz-acp and their only observables are tracing::debug! lines (relay.rs:2387,
# lib.rs:3258, lib.rs:550). pc_launch.py builds a CLOSED env key set and refuses
# any drift from the selected set (proofs/S0-01/pins.py, enforced at
# pc_launch.py:271). The S0-02 set must pin both the RUST_LOG key and its debug
# value; otherwise the three legs CANNOT be captured. Fail loud and name it.
if ! grep -Eq '^PINNED_ENV_KEYS_S0_02 = .*\{"RUST_LOG"\}' "$PINS" ||
   ! grep -Fqx 'PINNED_ENV_VALUES_S0_02 = {"RUST_LOG": "debug"}' "$PINS"; then
  cat >&2 <<'MSG'
BLOCKER: pins.PINNED_ENV_KEYS_S0_02 / PINNED_ENV_VALUES_S0_02
(proofs/S0-01/pins.py) does not pin RUST_LOG=debug, and pc_launch.py refuses
any env key set that differs from it. buzz-acp would run at INFO, where none
of its three S0-02 observables is emitted:
  relay.rs:2387  debug!("dropping duplicate event for channel {channel_id}")
  lib.rs:3258    tracing::debug!(..., "dropping self-authored event")
  lib.rs:550     debug!("inbound author gate — dropping event")
NOT run: neg-replayed, neg-self-authored and neg-not-allowlisted need
RUST_LOG=debug in the S0-02 launcher environment.
MSG
  exit 3
fi

mkdir -p "$DEST"

for leg in $LEGS; do
  say "$leg"
  out=$DEST/$leg
  rm -rf "$out"
  launch_leg
  case "$leg" in
    neg-replayed)
      # ONE event id delivered twice. The first delivery must produce a turn or
      # the leg proves nothing, so it is checked before the second is sent.
      deliver pos-allowed "$out/first" "$(role_for pos-allowed)"
      wait_turn_window 1
      # issue #17 step 2: cut the first delivery's timeline at its last newline
      # (a partial trailing line never enters the snapshot) and record its byte
      # length; the second delivery's timeline is the post-boundary DELTA.
      first_bytes=$(snapshot_timeline "$out")
      # F5: sleep 1 before the second deliver to avoid the NIP-98 same-second
      # replay guard (crates/buzz-auth/src/nip98_replay.rs). The second sub-leg's
      # t0 is the FIRST sub-leg's t0 (the clock the reused event was signed
      # against), so the checker measures freshness against the right baseline.
      sleep 1
      local_first_t0=$(/usr/bin/python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["t0_epoch_s"])' "$out/first/t0.json")
      deliver neg-replayed "$out/second" "$(role_for neg-replayed)" \
        --reuse "$out/first/delivered-event.json" \
        --t0 "$local_first_t0"
      wait_turn_window 0
      # issue #17 steps 5+6: prove the final live timeline is an exact byte
      # extension of the first snapshot, then write only the post-boundary
      # bytes as the second delivery's timeline. The prefix proof (cmp -n) and
      # the delta write (tail) both live inside delta_timeline, so the tests
      # source exactly these production bytes (item 5's integration test,
      # item 6a's prefix-mismatch control). On a prefix mismatch the function
      # prints the named error, writes NO second timeline, and returns the
      # named code (8) — set -e then aborts the leg. On success an EMPTY delta
      # is a valid output (the relay dropped the duplicate; buzz-acp saw
      # nothing) — the runner never fabricates lines.
      delta_timeline "$out" "$first_bytes"
      ;;
    neg-bad-signature)
      # The positive template signed and corrupted in ONE deliver call: the ONLY
      # difference from a passing event is the signature, and the valid event
      # never leaves deliver_event.py (B12, AF-AP-156: a setup delivery of the
      # positive event put a real turn inside this leg's window).
      deliver neg-bad-signature "$out" "$(role_for neg-bad-signature)" \
        --flip-signature
      wait_turn_window 0
      collect_leg "$out"
      ;;
    revoked)
      # F2: the receipt lives OUTSIDE $out at $MEMBERSHIP so rm -rf "$out" does
      # not delete it. It is copied INTO $out after the wipe, and the documented
      # shape gains http_status (F3).
      if [ ! -f "$MEMBERSHIP" ]; then
        cat >&2 <<MSG
NOT run by this script: the revoked leg needs the sender removed from the NIP-29
group before delivery, and a relay membership WRITE is an owner/coordinator
operation, not a lane operation. Run the removal, write
$MEMBERSHIP as {"removed":true,"removed_pubkey":"<hex>","channel":"<uuid>","at_epoch_s":N,"http_status":NNN},
then re-run this script with \`revoked\` as the only leg argument.
MSG
        stop_leg; continue
      fi
      mkdir -p "$out"
      cp "$MEMBERSHIP" "$out/membership.json"
      deliver revoked "$out" "$(role_for revoked)"
      wait_turn_window 0
      collect_leg "$out"
      ;;
    pos-allowed)
      deliver "$leg" "$out" "$(role_for "$leg")"
      wait_turn_window 1
      collect_leg "$out"
      ;;
    *)
      deliver "$leg" "$out" "$(role_for "$leg")"
      wait_turn_window 0
      collect_leg "$out"
      ;;
  esac
  stop_leg
  post_leg
  if [ "$leg" = "neg-replayed" ]; then
    # M-B (issue #17 / D-036): the checker's replay closure requires buzzacp.log
    # in EACH sub-leg and NOTHING at the leg root (C:569-574, C:143-149). ONE
    # continuous process produces ONE masked log (masking runs only after exit,
    # pc_post.sh:107), so the same log is copied into both sub-legs; the checker
    # scans only the second sub-leg's log for observables (C:609-610) — the first
    # copy exists for the closure, not as a second observation. Every other leg
    # keeps its single root copy.
    collect_masked "$out/first"
    collect_masked "$out/second"
  else
    collect_masked "$out"
  fi
done

say "captured into $DEST"
find "$DEST" -type f | sort

}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
