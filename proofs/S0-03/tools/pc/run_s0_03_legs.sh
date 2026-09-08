#!/usr/bin/env bash
# run_s0_03_legs.sh — capture the S0-03 evidence bundle. RUNS ON THE PC ONLY. NOT RUN in the
# sandbox: there is no OmniRoute there and a sandbox model server is forbidden (owner ruling
# 2026-09-03, "just use omniroute"). Only `bash -n`, the argument handling and the
# runner-vs-launcher flag contract are exercised here.
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
LEG_NAME=${S0_03_LEG_NAME:-s0-03-hermes}

# The S0-01 capture path, by INVOCATION (VERIFY-O1 F-8). S0_03_LAUNCHER exists so a PC clone at
# another path can name the same file; its realpath must BE the pinned launcher. There is no
# escape hatch: the previous version let $S0_03_HERMES_CONFIG name any launcher, which is exactly
# the substitution the comment three lines above it forbade (F-22).
LAUNCHER_PIN=$ROOT/proofs/S0-01/tools/pc/pc_launch.py
LAUNCHER=${S0_03_LAUNCHER:-$LAUNCHER_PIN}
MENTION=$ROOT/proofs/S0-01/tools/pc/pc_mention.sh

# ONE source for the route id: the proof-owned profile, read from the key HERMES reads
# (`model.default`, cli.py:5359-5360 in the pinned hermes-agent 527da608). The top-level
# `default:` the previous version read is a key Hermes never looks at (F-13), so the route id and
# the launched model came from different places.
if [ -z "$ROUTE_ID" ]; then
  ROUTE_ID=$(python3 - "$CONFIG" <<'PY'
import sys, yaml
cfg = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
model = cfg.get("model")
default = model.get("default") if isinstance(model, dict) else None
if not isinstance(default, str) or not default.strip():
    sys.exit("run_s0_03_legs: config.yaml has no model.default — the route must be declared "
             "where Hermes reads it (cli.py:5359-5360)")
# `<provider>/<route>`: the prefix binds the model to the providers entry; OmniRoute is asked
# for the route id alone.
print(default.strip().split("/", 1)[-1])
PY
)
fi
[ -n "$ROUTE_ID" ] || { echo "run_s0_03_legs: no route id (config.yaml has no model.default)" >&2; exit 64; }

WORK=${S0_03_WORKDIR:-$(mktemp -d -t s0-03-XXXXXX)}
mkdir -p "$WORK/pids" "$EVIDENCE"
MODELS_BODY=""

stop_all() {
  # Only pids WE wrote, each one checked to still exist before the signal.
  for pidfile in "$WORK"/pids/*.pid; do
    [ -e "$pidfile" ] || continue
    pid=$(cat "$pidfile" 2>/dev/null || true)
    case "$pid" in (''|*[!0-9]*) continue ;; esac
    kill "$pid" 2>/dev/null || true
  done
  # F-21: the preflight's temp file is removed on EVERY exit path. The old
  # `trap ... RETURN` sat at top level, where it is a no-op, so the `exit 3` paths leaked it.
  if [ -n "$MODELS_BODY" ]; then rm -f "$MODELS_BODY"; fi
  return 0
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
MODELS_BODY=$(mktemp)
code=$(curl -s -o "$MODELS_BODY" -w '%{http_code}' -m 20 \
       -H @<(printf 'Authorization: Bearer %s\n' "$key") "$BASE_URL/models")
unset key
[ "$code" = "200" ] || { echo "run_s0_03_legs: GET /v1/models -> $code" >&2; exit 3; }
grep -q "\"id\"[[:space:]]*:[[:space:]]*\"$ROUTE_ID\"" "$MODELS_BODY" \
  || { echo "run_s0_03_legs: route '$ROUTE_ID' absent from the authenticated catalog" >&2; exit 3; }
rm -f "$MODELS_BODY"; MODELS_BODY=""

# 4. The launcher is the S0-01 one, by realpath. A foreign launcher is not the capture path the
#    seed's assertion leans on, and there is no flag to allow one.
[ -f "$LAUNCHER" ] || { echo "run_s0_03_legs: launcher absent: $LAUNCHER" >&2; exit 3; }
[ "$(realpath "$LAUNCHER")" = "$(realpath "$LAUNCHER_PIN")" ] \
  || { echo "run_s0_03_legs: S0_03_LAUNCHER must BE $LAUNCHER_PIN (got $LAUNCHER)" >&2; exit 3; }

# 5. The launcher's marker tree and pc_mention.sh's must be the SAME tree. pc_mention.sh hard-codes
#    its BASE (its `BASE=` line) and reads the leg's framedir from <BASE>/.markers/current-framedir;
#    if the launcher wrote its markers somewhere else (an $S0_01_HERMES_HOME override), the prompt
#    would be sent into a different leg's session. Resolved through S0-01's own pins module, so the
#    runner cannot drift from the launcher's resolution.
MARKERS=$(python3 - "$ROOT" <<'PY'
import os, sys
sys.path.insert(0, os.path.join(sys.argv[1], "proofs", "S0-01"))
import pins
print(os.path.join(os.path.dirname(pins.hermes_home()), ".markers"))
PY
)
MENTION_BASE=$(sed -n 's/^BASE=\([^;[:space:]]*\).*/\1/p' "$MENTION" | head -1)
[ -n "$MENTION_BASE" ] || { echo "run_s0_03_legs: cannot read BASE from $MENTION" >&2; exit 3; }
[ "$MARKERS" = "$MENTION_BASE/.markers" ] \
  || { echo "run_s0_03_legs: launcher markers $MARKERS != pc_mention.sh tree $MENTION_BASE/.markers" >&2; exit 3; }
echo "preflight OK: authoritative instance, key file 0600, route '$ROUTE_ID' in the catalog,"
echo "preflight OK: launcher $(realpath "$LAUNCHER"), markers $MARKERS"

# ---------------------------------------------------------------- leg A: direct
echo "== leg A: direct =="
S0_03_KEY_FILE="$KEY_FILE" S0_03_BASE_URL="$BASE_URL" \
  python3 "$PROOF/tools/pc/direct_responses_probe.py" \
    --route-id "$ROUTE_ID" --out-dir "$EVIDENCE/direct"

# ---------------------------------------------------------------- leg B: hermes
echo "== leg B: hermes =="
mkdir -p "$EVIDENCE/hermes"
NONCE2=$(python3 -c 'import secrets;print(secrets.token_hex(8))')
PROMPT="Run the terminal command 'printf $NONCE2' and reply with its output."

# The tool the prompt exercises is Hermes' `terminal` tool: it is in the pinned agent's polished
# toolset (hermes-agent 527da608, acp_adapter/tools.py:68) and reports over ACP as a `tool_call`
# update of kind "execute" with a `tc-<hex>` id (acp_adapter/tools.py:85-92, build_tool_title at
# :96-101). `printf` writes nothing to disk and touches no owner state — the least side effect of
# any executing tool in that set.
#
# ORDERING (18-class sweep, class 13 / AF-AP-55 family): the env record must be taken WHILE the
# agent is alive. `pc_launch.py` only returns when buzz-acp exits (its final `proc.wait()`), so it runs
# in the background and the leg is driven through its marker files: poll `launch.ready`
# (the marker it writes last), take the env record off the tee's runtime-identity.json, send the prompt,
# then tear down by the pid the launcher itself recorded.
capture_hermes_leg() {
  local framedir=$1 profile=$2 tag=$3

  # The launched profile is a per-leg COPY, not the committed template: it carries this leg's
  # nonce2 as `x-omniroute-session-id`, which is the header OmniRoute records as
  # call_logs.session_tag (collect_leg.sh explains the chain) and therefore the only thing that
  # binds Hermes' call_logs row to THIS turn. The bundle's profile.yaml is copied back from the
  # launched Hermes home afterwards and checked against the launcher's own
  # `hermes-config.sha256`, so conjunct (v) grades the file the launcher read rather than the
  # repo file the runner started from (F-3).
  python3 - "$CONFIG" "$profile" "$NONCE2" <<'PY'
import sys, yaml
src, dst, nonce2 = sys.argv[1:4]
cfg = yaml.safe_load(open(src, encoding="utf-8")) or {}
providers = cfg.get("providers") or {}
if len(providers) != 1:
    sys.exit(f"run_s0_03_legs: config.yaml declares {len(providers)} providers, expected 1")
(_name, block), = providers.items()
headers = block.setdefault("extra_headers", {})
headers["x-omniroute-session-id"] = nonce2
with open(dst, "w", encoding="utf-8") as fh:
    yaml.safe_dump(cfg, fh, sort_keys=False)
PY

  python3 "$LAUNCHER" --leg "$LEG_NAME" --model "$ROUTE_ID" --profile "$profile" \
      </dev/null > "$WORK/$tag.launch.log" 2>&1 &
  local leg_pid=$!
  echo "$leg_pid" > "$WORK/pids/$tag.pid"

  # FAILURE-AWARE WAIT: the exit conditions are (a) the leg is ready, (b) the launcher is gone,
  # (c) the deadline passed. Never success-only silence.
  local deadline=$((SECONDS + ${S0_03_READY_WAIT_S:-180})) ready=0
  while [ "$SECONDS" -lt "$deadline" ]; do
    if [ -f "$framedir/launch.ready" ]; then ready=1; break; fi
    kill -0 "$leg_pid" 2>/dev/null || {
      echo "run_s0_03_legs: $tag launcher exited before launch.ready" >&2
      break
    }
    sleep 1
  done
  if [ "$ready" -ne 1 ]; then
    echo "run_s0_03_legs: $tag never reached launch.ready; launcher log tail:" >&2
    tail -20 "$WORK/$tag.launch.log" >&2 || true
    return 5
  fi
  # Teardown target: the pid the LAUNCHER recorded for buzz-acp (its `buzz-acp.pid` write). Copied into
  # our own pids dir the moment it exists, so stop_all reaps it on every exit path.
  if [ -s "$framedir/buzz-acp.pid" ]; then
    cp "$framedir/buzz-acp.pid" "$WORK/pids/$tag-buzz-acp.pid"
  else
    echo "run_s0_03_legs: $tag reached launch.ready with no buzz-acp.pid — teardown has no target" >&2
    return 5
  fi

  # The env record, while the agent is alive. The pid key is agent_child_pid (the key the tee's identity dict writes).
  python3 "$PROOF/tools/pc/hermes_env_names.py" \
      --out-dir "$EVIDENCE/hermes" --runtime-identity "$framedir/runtime-identity.json"

  # The prompt travels the way every S0-01 prompt does: a relay mention (`run_leg.sh`'s owner-mention step). There is
  # no prompt flag on the launcher; pc_mention.sh reads the framedir from current-framedir and
  # waits for the turn's end_turn.
  local window_start window_end
  window_start=$(now)
  TEXT="$PROMPT" WHO=owner TAG="$tag" WAIT_FOR=end_turn bash "$MENTION"
  # Let OmniRoute finish writing the row before the window closes: the call_logs row is written
  # when the attempt completes (src/lib/usage/callLogs.ts:489 stamps it then), which is after the
  # client sees the last frame.
  sleep "${S0_03_SETTLE_S:-3}"
  window_end=$(now)

  cp "$framedir/timeline.jsonl" "$EVIDENCE/hermes/timeline.jsonl"
  cp "$profile" "$EVIDENCE/hermes/profile.yaml"
  local launched_sha copied_sha
  launched_sha=$(tr -d '[:space:]' < "$framedir/hermes-config.sha256")
  copied_sha=$(sha256sum "$EVIDENCE/hermes/profile.yaml" | cut -d' ' -f1)
  [ "$launched_sha" = "$copied_sha" ] \
    || { echo "run_s0_03_legs: captured profile.yaml is not the launched config ($copied_sha != $launched_sha)" >&2; return 6; }
  grep -qF "$ROUTE_ID" "$framedir/hermes-model.txt" \
    || { echo "run_s0_03_legs: the launcher read model line $(cat "$framedir/hermes-model.txt") — it does not name '$ROUTE_ID'" >&2; return 6; }

  python3 - "$EVIDENCE/hermes/leg.json" "$NONCE2" "$PROMPT" "$ROUTE_ID" \
           "$window_start" "$window_end" <<'PY'
import json, sys
out, nonce2, prompt, route, start, end = sys.argv[1:7]
json.dump({"leg": "hermes", "nonce2": nonce2, "prompt": prompt, "route_id": route,
           "window_start": start, "window_end": end},
          open(out, "w"), indent=2, sort_keys=True)
open(out, "a").write("\n")
PY

  # Teardown by the launcher's own pidfile, then reap the launcher (it returns when buzz-acp does).
  local pid=""
  if [ -s "$WORK/pids/$tag-buzz-acp.pid" ]; then
    pid=$(cat "$WORK/pids/$tag-buzz-acp.pid")
  fi
  case "$pid" in (''|*[!0-9]*) ;; (*) kill "$pid" 2>/dev/null || true ;; esac
  wait "$leg_pid" || true
  return 0
}

HERMES_HOME_LEG="$WORK/hermes-home"
mkdir -p "$HERMES_HOME_LEG"
capture_hermes_leg "$MARKERS/v2-$LEG_NAME" "$HERMES_HOME_LEG/config.yaml" hermes-leg

# ---------------------------------------------------------------- the negative leg
echo "== negative leg: credential-absent =="
# The kill switch, produced by the ONLY path that can produce it: a request with NO Authorization
# header (`--no-credential`), which is OmniRoute's no-bearer 401 AUTH_002
# (src/server/authz/policies/clientApi.ts:77). The previous version pointed S0_03_KEY_FILE at
# /dev/null, and the probe exits before writing anything, so the committed bundle had no
# producer at all (F-9). The owner's profile file is not touched, not moved, not rewritten.
mkdir -p "$EVIDENCE/credential-absent/direct"
python3 "$PROOF/tools/pc/direct_responses_probe.py" \
    --route-id "$ROUTE_ID" --no-credential \
    --out-dir "$EVIDENCE/credential-absent/direct" || true
cat > "$EVIDENCE/credential-absent/NOT-CAPTURED.md" <<'NOTE'
# credential-absent: what this bundle does NOT contain, and why

There is no `hermes/` half. A key-free Hermes leg cannot be captured through the pinned S0-01
launcher: `proofs/S0-01/tools/pc/pc_launch.py` builds the launch environment in `launch_env`,
which reads `OMNIROUTE_API_KEY` from the owner's profile env FILE (`HERMES_ENV`, a module
constant with no override) and refuses an empty value. `env -u OMNIROUTE_API_KEY` on the launcher
is therefore a no-op for the agent — the old runner did exactly that and would have produced a
negative bundle whose Hermes environ still carried the key.

The kill switch does not need it: the credential is absent from THIS REQUEST, and
`direct/direct.json` records that fact structurally (`credential_presented: false`, and no
`Authorization` key in `request_headers_sent`) beside OmniRoute's 401. The checker grades the
bundle on that evidence.

Making the Hermes half producible needs a seam in S0-01's launcher (a `--hermes-env` argument, or
an `S0_01_HERMES_ENV` override threaded into `launch_env` the way `hermes_home()` threads the
Hermes home). That is S0-01-side work; this proof does not fake it.
NOTE
bash "$PROOF/tools/pc/collect_leg.sh" "$EVIDENCE/credential-absent" "$ROUTE_ID"

# ---------------------------------------------------------------- collect
echo "== collect =="
bash "$PROOF/tools/pc/collect_leg.sh" "$EVIDENCE" "$ROUTE_ID"

echo "S0-03 bundle captured at $EVIDENCE"
