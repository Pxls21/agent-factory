#!/usr/bin/env bash
# run_s0_03_legs.sh — capture the S0-03 evidence bundle. RUNS ON THE PC ONLY. NOT RUN in the
# sandbox: there is no OmniRoute there and a sandbox model server is forbidden (owner ruling
# 2026-09-03, "just use omniroute"). Only `bash -n` and the argument handling are exercised here.
#
#   proofs/S0-03/tools/pc/run_s0_03_legs.sh [--route-id ID] [--evidence DIR]
#
# Legs, in order:
#   preflight        read-only; refuses to continue on any failure
#   direct           leg A  -> <evidence>/direct/direct.json
#   hermes           leg B  -> <evidence>/hermes/{timeline.jsonl,hermes-env-names.json,
#                                                 profile.yaml,leg.json}
#   credential-absent  the negative leg -> <evidence>/credential-absent/
#   collect          OmniRoute's own request rows -> <evidence>/omniroute-requests.json
#
# PROCESS RULE (AF-AP-34 / AF-AP-59): every process this script starts writes its pid to a file
# under $WORK/pids and is stopped with `kill <that pid>`. NO name-matching process command appears
# anywhere in this file — the pattern- and name-matching killers match the owner's production
# processes too, and four such calls aimed at an isolated relay each restarted the owner's
# buzz-prod-relay-1. tests/test_s0_03_omniroute.py asserts their absence over the WHOLE file, so
# they are not written here even inside a comment.
# The owner's OmniRoute and Hermes sessions are never started, stopped, restarted or reconfigured.

set -euo pipefail

ROUTE_ID=""
EVIDENCE=""
BASE_URL=${S0_03_BASE_URL:-http://127.0.0.1:20128/v1}
KEY_FILE=${S0_03_KEY_FILE:-$HOME/.hermes/profiles/agentfactory/.env}

while [ $# -gt 0 ]; do
  case "$1" in
    --route-id)  ROUTE_ID=${2:?--route-id needs a value}; shift 2 ;;
    --evidence)  EVIDENCE=${2:?--evidence needs a value}; shift 2 ;;
    *) echo "run_s0_03_legs: unknown argument $1" >&2; exit 64 ;;
  esac
done

ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
cd "$ROOT"
PROOF=proofs/S0-03
CONFIG=$PROOF/hermes/config.yaml
EVIDENCE=${EVIDENCE:-$PROOF/evidence}

# ONE source for the route id: the proof-owned profile. The spec's --route-id and the launched
# profile therefore cannot drift apart (a second hard-coded copy is how they would).
if [ -z "$ROUTE_ID" ]; then
  ROUTE_ID=$(python3 -c 'import sys,yaml;print((yaml.safe_load(open(sys.argv[1])) or {}).get("default",""))' "$CONFIG")
fi
[ -n "$ROUTE_ID" ] || { echo "run_s0_03_legs: no route id (config.yaml has no default:)" >&2; exit 64; }

WORK=${S0_03_WORKDIR:-$(mktemp -d -t s0-03-XXXXXX)}
mkdir -p "$WORK/pids" "$EVIDENCE"

stop_all() {
  # Only pids WE wrote, each one checked to still exist before the signal.
  for pidfile in "$WORK"/pids/*.pid; do
    [ -e "$pidfile" ] || continue
    pid=$(cat "$pidfile" 2>/dev/null || true)
    case "$pid" in (''|*[!0-9]*) continue ;; esac
    kill "$pid" 2>/dev/null || true
  done
}
trap stop_all EXIT

now() { date -u +%Y-%m-%dT%H:%M:%S.%6NZ; }

# ---------------------------------------------------------------- preflight (read-only)
echo "== preflight =="

# 1. The instance that owns the port is the managed, authoritative one (AF-AP-33: a health 200
#    says nothing about WHICH OmniRoute answers — an orphan already squatted :20128 once).
OMNIROUTE_API_KEY_FILE="$KEY_FILE" bash scripts/omniroute_invariants.sh \
  || { echo "run_s0_03_legs: omniroute_invariants FAILED — not the authoritative instance" >&2; exit 3; }

# 2. The key file exists and is 0600. Its CONTENT is never read here, printed, or echoed.
[ -f "$KEY_FILE" ] || { echo "run_s0_03_legs: key file absent: $KEY_FILE" >&2; exit 3; }
mode=$(stat -c '%a' "$KEY_FILE")
[ "$mode" = "600" ] || { echo "run_s0_03_legs: key file $KEY_FILE is mode $mode, expected 600" >&2; exit 3; }
grep -q '^[[:space:]]*\(export[[:space:]]\+\)\?OMNIROUTE_API_KEY[[:space:]]*=' "$KEY_FILE" \
  || { echo "run_s0_03_legs: $KEY_FILE carries no OMNIROUTE_API_KEY line" >&2; exit 3; }

# 3. The route id appears in the AUTHENTICATED catalog. The key travels in a header FILE
#    (process substitution), never in argv — the technique of scripts/omniroute_invariants.sh:80.
key=$(grep -m1 '^[[:space:]]*\(export[[:space:]]\+\)\?OMNIROUTE_API_KEY[[:space:]]*=' "$KEY_FILE" \
        | cut -d= -f2- | tr -d '\r\n"'"'")
models_body=$(mktemp); trap 'rm -f "$models_body"' RETURN 2>/dev/null || true
code=$(curl -s -o "$models_body" -w '%{http_code}' -m 20 \
       -H @<(printf 'Authorization: Bearer %s\n' "$key") "$BASE_URL/models")
unset key
[ "$code" = "200" ] || { echo "run_s0_03_legs: GET /v1/models -> $code" >&2; exit 3; }
grep -q "\"id\"[[:space:]]*:[[:space:]]*\"$ROUTE_ID\"" "$models_body" \
  || { echo "run_s0_03_legs: route '$ROUTE_ID' absent from the authenticated catalog" >&2; exit 3; }
rm -f "$models_body"
echo "preflight OK: authoritative instance, key file 0600, route '$ROUTE_ID' in the catalog"

# ---------------------------------------------------------------- leg A: direct
echo "== leg A: direct =="
S0_03_DIRECT_AFTER=$(now); export S0_03_DIRECT_AFTER
S0_03_KEY_FILE="$KEY_FILE" S0_03_BASE_URL="$BASE_URL" \
  python3 "$PROOF/tools/pc/direct_responses_probe.py" \
    --route-id "$ROUTE_ID" --out-dir "$EVIDENCE/direct"

# ---------------------------------------------------------------- leg B: hermes
echo "== leg B: hermes =="
S0_03_HERMES_AFTER=$(now); export S0_03_HERMES_AFTER

# THE SEAM THIS LEG NEEDS, AND WHY IT DOES NOT EXIST YET
# -----------------------------------------------------
# The brief pins leg B to the S0-01 capture path by INVOCATION. `proofs/S0-01/tools/pc/
# pc_launch.py` cannot be pointed at another proof's profile today, and S0-01's tools are out of
# this lane's scope to edit:
#   * pc_launch.py:216 reads config.yaml from `pins.PINNED_HERMES_HOME`, and
#     proofs/S0-01/pins.py:18 hard-codes that to "/home/rocco/s0-01-pinned/.hermes-home" with no
#     environment override anywhere in pins.py;
#   * pc_launch.py:189-190 constrains `--leg` to `pins.LEGS` (proofs/S0-01/pins.py:76 — no S0-03
#     leg) and `--model` to `pins.EXPECTED_MODEL.values()` (:78 — the S0-01 scripted models).
# Writing an S0-03 config into that pinned tree would mutate S0-01's evidence base; forking the
# launcher would duplicate the spine. Neither is acceptable, so this leg REFUSES rather than
# substituting a different launcher and calling the result the S0-01 capture path.
#
# The seam required, in the LAUNCH env only (one line in pins.py, no behaviour change for S0-01):
#     PINNED_HERMES_HOME = os.environ.get("S0_03_HERMES_CONFIG_HOME", "/home/rocco/s0-01-pinned/.hermes-home")
# plus opening `--leg`/`--model` to a caller-supplied value. Until that lands, S0_03_HERMES_CONFIG
# must name a launcher that accepts a profile path.
if [ -z "${S0_03_HERMES_CONFIG:-}" ]; then
  cat >&2 <<'BLOCKED'
run_s0_03_legs: BLOCKER — leg B cannot run. proofs/S0-01/tools/pc/pc_launch.py cannot be pointed
at the S0-03 profile (pc_launch.py:216 + proofs/S0-01/pins.py:18/:76/:78 hard-code S0-01's Hermes
home, leg set and model set), and editing S0-01's tools is out of scope for this lane.
This is NOT stubbed and NOT worked around. Set S0_03_HERMES_CONFIG to a launcher that accepts a
profile path, or land the one-line pins.py seam named above, then re-run.
BLOCKED
  exit 5
fi

mkdir -p "$EVIDENCE/hermes"
NONCE2=$(python3 -c 'import secrets;print(secrets.token_hex(8))')
PROMPT="Run the terminal command 'printf $NONCE2' and reply with its output."
python3 - "$EVIDENCE/hermes/leg.json" "$NONCE2" "$PROMPT" "$ROUTE_ID" <<'PY'
import json, sys
out, nonce2, prompt, route = sys.argv[1:5]
json.dump({"leg": "hermes", "nonce2": nonce2, "prompt": prompt, "route_id": route},
          open(out, "w"), indent=2, sort_keys=True)
open(out, "a").write("\n")
PY

# The tool the prompt exercises is Hermes' `terminal` tool: it is in the pinned agent's polished
# toolset (hermes-agent 527da608, acp_adapter/tools.py:68) and reports over ACP as a `tool_call`
# update of kind "execute" with a `tc-<hex>` id (acp_adapter/tools.py:85-92, build_tool_title at
# :96-101). `printf` writes nothing to disk and touches no owner state — the least side effect of
# any executing tool in that set.
# ORDERING (18-class sweep, class 13 / AF-AP-55 family): the env record must be taken WHILE the
# agent is alive. Capturing it after `wait` reads /proc of a dead pid — the tool exits loud, so
# the leg can never produce hermes-env-names.json at all, and a RECYCLED pid would hand back a
# different process's names. `capture_hermes_leg` therefore launches the leg in the background,
# waits for the tee's runtime-identity.json AND a live pid, takes the record, and only then waits
# for the leg to finish.
capture_hermes_leg() {
  # capture_hermes_leg <framedir> <pidfile-name> [extra env assignments...]
  local framedir=$1 tag=$2; shift 2
  mkdir -p "$framedir"
  env "$@" \
    S0_01_FRAMEDIR="$framedir" \
    S0_01_AGENT="${S0_03_HERMES_AGENT:?run_s0_03_legs: S0_03_HERMES_AGENT (hermes-acp path) not set}" \
    python3 "$S0_03_HERMES_CONFIG" --config "$CONFIG" --prompt "$PROMPT" &
  local leg_pid=$!
  echo "$leg_pid" > "$WORK/pids/$tag.pid"

  # FAILURE-AWARE WAIT: the exit conditions are (a) the record was taken, (b) the leg process is
  # gone, (c) the deadline passed. Never success-only silence.
  local rid="$framedir/runtime-identity.json" deadline=$((SECONDS + ${S0_03_RID_WAIT_S:-60})) captured=0
  while [ "$SECONDS" -lt "$deadline" ]; do
    if [ -s "$rid" ] \
       && python3 "$PROOF/tools/pc/hermes_env_names.py" \
            --out-dir "$framedir" --runtime-identity "$rid" 2>"$WORK/$tag.envcap.err"; then
      captured=1; break
    fi
    kill -0 "$leg_pid" 2>/dev/null || {
      echo "run_s0_03_legs: $tag exited before its env record could be taken" >&2
      break
    }
    sleep 0.2
  done
  wait "$leg_pid"; local leg_rc=$?
  cp "$CONFIG" "$framedir/profile.yaml"
  if [ "$captured" -ne 1 ]; then
    echo "run_s0_03_legs: $tag produced NO hermes-env-names.json (leg rc $leg_rc); last error:" >&2
    cat "$WORK/$tag.envcap.err" >&2 || true
    return 6
  fi
  return "$leg_rc"
}

capture_hermes_leg "$EVIDENCE/hermes" hermes-leg S0_03_HERMES_CONFIG="$S0_03_HERMES_CONFIG"

# ---------------------------------------------------------------- the negative leg
echo "== negative leg: credential-absent =="
# The kill switch: OMNIROUTE_API_KEY is unset in THIS LAUNCH ENV ONLY. The owner's profile file
# is not touched, not moved, and not rewritten.
mkdir -p "$EVIDENCE/credential-absent/direct" "$EVIDENCE/credential-absent/hermes"
S0_03_KEY_FILE=/dev/null \
  python3 "$PROOF/tools/pc/direct_responses_probe.py" \
    --route-id "$ROUTE_ID" --out-dir "$EVIDENCE/credential-absent/direct" || true
# The negative leg needs its OWN env record — the checker reads hermes-env-names.json from every
# bundle, and its ABSENCE of OMNIROUTE_API_KEY is half the kill switch's evidence. `env -u` drops
# the name from THIS launch only. A non-zero rc here is the expected outcome, not a failure.
capture_hermes_leg "$EVIDENCE/credential-absent/hermes" hermes-neg -u OMNIROUTE_API_KEY || true
cp "$EVIDENCE/hermes/leg.json" "$EVIDENCE/credential-absent/hermes/leg.json"

# ---------------------------------------------------------------- collect
echo "== collect =="
# Let the service flush its WAL before the immutable read (collect_leg.sh explains why).
sleep "${S0_03_SETTLE_S:-3}"
bash "$PROOF/tools/pc/collect_leg.sh" "$EVIDENCE" "$ROUTE_ID"

echo "S0-03 bundle captured at $EVIDENCE"
