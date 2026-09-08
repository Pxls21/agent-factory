#!/usr/bin/env bash
# run_s0_02_legs.sh — PC SIDE: capture the seven S0-02 legs against the isolated
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

DEST=${1:?usage: run_s0_02_legs.sh <evidence-root> [leg ...]}
shift || true
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

ALL_LEGS="pos-allowed neg-unauthorized neg-bad-signature neg-replayed neg-stale neg-self-authored revoked"
LEGS=${*:-$ALL_LEGS}

say() { echo; echo "===== [S0-02] $* ====="; }

# --- PREFLIGHT: the two buzz-acp-decided legs need RUST_LOG=debug ------------
# neg-replayed and neg-self-authored are decided INSIDE buzz-acp and their only
# observables are tracing::debug! lines (relay.rs:2387, lib.rs:3258). pc_launch.py
# builds a CLOSED env key set and refuses any drift from pins.PINNED_ENV_KEYS
# (proofs/S0-01/pins.py:44-48, enforced at pc_launch.py:268), and RUST_LOG is
# not in it. Until that set carries RUST_LOG the two legs CANNOT be captured.
# Fail loud and name it: a leg captured at INFO would produce a log with no
# observable, and the checker would (correctly) call that a missing observable
# rather than a missing capability.
if ! grep -q '"RUST_LOG"' "$PINS"; then
  cat >&2 <<'MSG'
BLOCKER: pins.PINNED_ENV_KEYS (proofs/S0-01/pins.py:44-48) does not carry RUST_LOG,
and pc_launch.py:267-269 refuses any env key set that differs from it. buzz-acp
would run at INFO, where neither of its two S0-02 observables is emitted:
  relay.rs:2387  debug!("dropping duplicate event for channel {channel_id}")
  lib.rs:3258    tracing::debug!(..., "dropping self-authored event")
NOT run: neg-replayed and neg-self-authored need RUST_LOG=debug in the launcher.
This is the coordinator's call (it touches proofs/S0-01/, outside this lane).
MSG
  exit 3
fi

mkdir -p "$DEST"

launch_leg() {
  rm -f "$MARKERS/s0-02.launch.log"
  setsid /usr/bin/python3 "$LAUNCHER" --leg "$HOST_LEG" --model s0-01-pong \
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
    n=$(grep -c '"method":"session/prompt"' "$FD/timeline.jsonl" 2>/dev/null || echo 0)
    [ "$n" -ge "$want" ] && [ "$want" -gt 0 ] && return 0
    [ -f "$FD/buzz-acp.exit" ] && { echo "buzz-acp exited during the turn window" >&2; return 6; }
    sleep "$POLL_S"
  done
  return 0
}

collect_leg() {
  local out=$1
  mkdir -p "$out"
  cp "$FD/timeline.jsonl" "$out/timeline.jsonl"
  # buzzacp.log is the MASKED log pc_launch.py writes; buzzacp.raw.log is never copied.
  cp "$FD/buzzacp.log" "$out/buzzacp.log"
  if grep -Eq '[0-9a-fA-F]{64}' "$out/buzzacp.log"; then
    echo "REFUSING to keep $out/buzzacp.log: unmasked 64-hex present" >&2
    rm -f "$out/buzzacp.log"; return 7
  fi
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
      collect_leg "$out/first"
      deliver neg-replayed "$out/second" "$(role_for neg-replayed)" \
        --reuse "$out/first/delivered-event.json"
      wait_turn_window 0
      collect_leg "$out/second"
      # The second sub-leg's fixture.json must be the neg-replayed fixture, and
      # its t0/delivered-event come from the reuse — both already written by
      # deliver_event.py.
      ;;
    neg-bad-signature)
      # The positive event with one signature byte flipped: the ONLY difference
      # from a passing event is the signature.
      deliver pos-allowed "$out/.probe" "$(role_for pos-allowed)"
      deliver neg-bad-signature "$out" "$(role_for neg-bad-signature)" \
        --reuse "$out/.probe/delivered-event.json" --flip-signature
      rm -rf "$out/.probe"
      wait_turn_window 0
      collect_leg "$out"
      ;;
    revoked)
      cat >&2 <<'MSG'
NOT run by this script: the revoked leg needs the sender removed from the NIP-29
group before delivery, and a relay membership WRITE is an owner/coordinator
operation, not a lane operation. Run the removal, write
<leg>/membership.json as {"removed":true,"removed_pubkey":"<hex>","channel":"<uuid>","at_epoch_s":N},
then re-run this script with `revoked` as the only leg argument.
MSG
      [ -f "$out/membership.json" ] || { stop_leg; continue; }
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
done

say "captured into $DEST"
find "$DEST" -type f | sort
