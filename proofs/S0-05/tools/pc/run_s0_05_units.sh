#!/usr/bin/env bash
# run_s0_05_units.sh — the LIVE-UNIT legs of S0-05, on the owner's PC.
#
#   NOT run here. Authored in the sandbox (lane E1, 2026-09-08) and never executed: it needs the
#   live units, and lane delegates do not touch the PC bridge. Every claim below about the PC is
#   a PLAN read from docs/05_SECURITY.md:74-85 and proofs/S0-01/tools/pc/, not an observation.
#
#   run_s0_05_units.sh <evidence-root> [unit...]      (default: every unit in the table)
#
# For each unit: create its own selective-egress namespace with ONLY that unit's allowed
# destinations from the docs/05 §6 table, PREFLIGHT that the unit's positive control can pass,
# launch the unit inside the namespace, run the canary suite as that unit, collect, tear down.
# Units that cannot run are declared in units.json as `not-run` with their reason — check_egress.py
# does not count them, and a declared-absent unit can never be read as a pass.
#
# TWO THINGS THIS SCRIPT DOES NOT DO, said plainly rather than worked around:
#  1. It does NOT create a route or NAT out of the namespace. So a model endpoint fails on
#     ROUTING (ENETUNREACH) as well as on the gate; only C6 (a routable, non-allow-listed
#     endpoint) is discriminated by the firewall alone. A NAT-ed variant, in which the general
#     internet is reachable and only the allow-list holds providers back, is NOT BUILT.
#  2. The canaries share the unit's network namespace; they are not the unit's own sockets. That
#     proves the NAMESPACE cannot reach a provider, which is the containment boundary docs/05 §6
#     specifies — it does not prove anything about the unit's in-process client behaviour.
#
# PREFLIGHT, not a workaround: if OmniRoute (or the Buzz relay) is bound to 127.0.0.1 on the PC,
# no namespace can reach it — a fresh namespace has its own empty loopback (findings §6a,
# docs/research/FINDINGS-STAGE0-v1.md:98-108). The script then ABORTS with
# `positive-control-unreachable` and names the two real fixes (bind the service on the veth host
# address, or add a host-side DNAT for it). It never falls back to a listener of its own.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
P="$(cd "$HERE/../.." && pwd)"
# shellcheck source=proofs/S0-05/netns_lib.sh
. "$P/netns_lib.sh"

EVIDENCE_ROOT=${1:?usage: run_s0_05_units.sh <evidence-root> [unit...]}; shift || true

# --- the unit table: docs/05_SECURITY.md:74-85, one row per source ---------------------------
# unit | allowed destinations (ip:port, resolved on the PC) | launch command | status
#
# ALLOWED_* values are PLACEHOLDERS the operator sets for their host: the row's comment names the
# docs/05 destination each one stands for. An unset value makes that unit `not-run` with the
# reason recorded, never a silent skip.
ALLOWED_HERMES=${ALLOWED_HERMES:-}        # docs/05 §6 "Hermes -> OmniRoute": OmniRoute :20128
ALLOWED_BUZZACP=${ALLOWED_BUZZACP:-}      # docs/05 §6 "buzz-acp -> Buzz relay and local hermes-acp"
ALLOWED_BACKEND=${ALLOWED_BACKEND:-}      # the S0-01 scripted backend behind its OmniRoute test route

S0_01_TOOLS=${S0_01_TOOLS:-$P/../S0-01/tools/pc}

declare -A ALLOWED LAUNCH ABSENT
ALLOWED[hermes-acp]=$ALLOWED_HERMES
LAUNCH[hermes-acp]="$S0_01_TOOLS/pc_launch.py --leg run-1 --model s0-01-pong"
ALLOWED[buzz-acp]=$ALLOWED_BUZZACP
LAUNCH[buzz-acp]="$S0_01_TOOLS/pc_launch.py --leg run-1 --model s0-01-pong"
ALLOWED[s0-01-backend]=$ALLOWED_BACKEND
LAUNCH[s0-01-backend]="$S0_01_TOOLS/pc_backend_restart.sh"
# Units the plan names that DO NOT EXIST yet (docs/05 §6 rows with no implementation):
ABSENT[memory-adapter]="unit does not exist"
ABSENT[ai-memory]="unit does not exist"
ABSENT[dream-foundry]="unit does not exist"
ABSENT[pandaprobe]="unit does not exist"
ABSENT[harness-router]="unit does not exist (conditional, not deployed in v1)"

UNITS=("$@")
[ ${#UNITS[@]} -gt 0 ] || UNITS=(hermes-acp buzz-acp s0-01-backend)

status=$(egress_ns_capable) || { echo "run_s0_05_units: cannot run here ($status)" >&2; exit 2; }

mkdir -p "$EVIDENCE_ROOT"
declare -A RESULT
NS_LIVE=""
cleanup() { for ns in $NS_LIVE; do egress_ns_destroy "$ns"; done; }
trap cleanup EXIT INT TERM

for unit in "${UNITS[@]}"; do
  allowed=${ALLOWED[$unit]:-}
  if [ -z "$allowed" ]; then
    RESULT[$unit]="not-run|no allowed destination configured for $unit (set ALLOWED_* from the docs/05 §6 row)"
    echo "SKIP $unit: no allowed destination configured" >&2
    continue
  fi
  ns="s0-05-$unit"
  echo "=== $unit: namespace $ns, allowed $allowed ==="
  egress_ns_create "$ns" "$allowed" || { RESULT[$unit]="not-run|namespace creation failed"; continue; }
  NS_LIVE="$NS_LIVE $ns"

  # PREFLIGHT the exact predicate the proof consumes (AF-AP-24): C0 itself, before launching
  # anything. A unit whose allowed target is unreachable from its namespace is a blocker.
  if ! egress_ns_run "$ns" curl -sS --connect-timeout 5 -o /dev/null "http://$allowed/v1/models"; then
    echo "positive-control-unreachable: $unit $allowed" >&2
    echo "  the service is not reachable from inside the namespace. Fix it, do not stub it:" >&2
    echo "  (a) bind the service on $(egress_ns_host_ip "$ns") (the veth host address), or" >&2
    echo "  (b) add a host-side DNAT from that address to the service. NOT BUILT here." >&2
    RESULT[$unit]="not-run|positive control unreachable: $allowed not reachable from $ns"
    egress_ns_destroy "$ns"; continue
  fi

  # Launch the unit INSIDE the namespace, then run the canaries as that unit.
  # NOT VERIFIED: no S0-01 launch has ever been run inside a network namespace.
  launch_pid=""
  if [ -n "${LAUNCH[$unit]:-}" ]; then
    # shellcheck disable=SC2086
    egress_ns_run "$ns" setsid /usr/bin/python3 ${LAUNCH[$unit]} </dev/null \
      >"$EVIDENCE_ROOT/$unit.launch.log" 2>&1 &
    launch_pid=$!
    # Failure-aware wait: the exit condition includes the FAILURE signature (the process is
    # gone), so the loop stops the moment the unit dies instead of sleeping through it. A blind
    # `sleep N` accepts a unit that died in second 1 and cannot notice one that dies in second
    # N+1 (18-class sweep, class 9). It waits for liveness only — readiness markers belong to the
    # S0-01 launcher and are NOT consumed here.
    for _ in $(seq 1 30); do
      kill -0 "$launch_pid" 2>/dev/null || break     # died: stop waiting, do not burn the window
      sleep 1
    done
    if ! kill -0 "$launch_pid" 2>/dev/null; then
      RESULT[$unit]="not-run|launch exited within the settle window; see $EVIDENCE_ROOT/$unit.launch.log"
      egress_ns_destroy "$ns"; continue
    fi
  fi

  bash "$P/run_canaries.sh" "$unit" "$ns" "$allowed" "$EVIDENCE_ROOT" "" pc
  RESULT[$unit]="run|contained live unit"

  [ -n "$launch_pid" ] && kill "$launch_pid" 2>/dev/null || true
  egress_ns_destroy "$ns"
done

# units.json: every unit the plan names, run or NOT, with its reason.
{
  printf '{\n  "units": [\n'
  first=1
  for unit in "${!RESULT[@]}"; do
    st=${RESULT[$unit]%%|*}; why=${RESULT[$unit]#*|}
    [ $first -eq 1 ] || printf ',\n'; first=0
    if [ "$st" = "run" ]; then
      printf '    {"unit": "%s", "status": "run", "note": "%s"}' "$unit" "$why"
    else
      printf '    {"unit": "%s", "status": "not-run", "reason": "%s"}' "$unit" "$why"
    fi
  done
  for unit in "${!ABSENT[@]}"; do
    [ $first -eq 1 ] || printf ',\n'; first=0
    printf '    {"unit": "%s", "status": "not-run", "reason": "%s"}' "$unit" "${ABSENT[$unit]}"
  done
  printf '\n  ]\n}\n'
} > "$EVIDENCE_ROOT/units.json"

echo "=== units.json ==="; cat "$EVIDENCE_ROOT/units.json"
echo "=== checker ==="
python3 "$P/check_egress.py" "$EVIDENCE_ROOT" --units "$(IFS=,; echo "${UNITS[*]}")"
