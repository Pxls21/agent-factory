#!/usr/bin/env bash
# S0-06 PC leg — capture ONE leg of the evidence bundle. NOT run in the sandbox.
#
#   collect_leg.sh <leg> <bundle-root>        leg = precedence | write-scope | leak | denied
#
# substrate.json is copied FIRST, before any leg file exists, so a bundle can never carry leg
# evidence without the identity of the instance that produced it.
#
# The raw instruments here are plain `curl` reads of `/api/v1`, deliberately NOT the adapter: the
# adapter is the subject of the proof, so every assertion has one instrument that bypasses it.
#   * search      GET /api/v1/search?q&workspace&project&limit   -> [ApiSearchHit]
#                 (crates/ai-memory-web/src/routes/api.rs:41-45, 1254-1263)
#   * page list   GET /api/v1/workspaces/{ws}/projects/{p}/pages -> [PageSummary]
#                 (api.rs:33-36; crates/ai-memory-store/src/reader.rs:1174-1185)
# The bearer token reaches curl through a 0600 --config file, never through argv (AF-AP-39).
#
# Environment (exported by run_s0_06_legs.sh): S0_06_BASE_URL, S0_06_RUNDIR, S0_06_AGENT,
# S0_06_TEAM, S0_06_PROJECT, S0_06_LEAK_AGENT.
# External commands used: curl, python3, mkdir, cp, printf.
set -euo pipefail

LEG="${1:?usage: collect_leg.sh <leg> <bundle-root>}"
ROOT="${2:?usage: collect_leg.sh <leg> <bundle-root>}"
HERE="$(cd "$(dirname "$0")" && pwd)"
PROOF_DIR="$(cd "$HERE/../.." && pwd)"
ADAPTER="$PROOF_DIR/adapter/factory_memory.py"
BASE="${S0_06_BASE_URL:?S0_06_BASE_URL not set}"
RUNDIR="${S0_06_RUNDIR:?S0_06_RUNDIR not set}"
CFG="$RUNDIR/curl.cfg"
QUERY="deploy window"

mkdir -p "$ROOT/$LEG"
cp "$RUNDIR/substrate.json" "$ROOT/substrate.json"

project_for() {   # scope -> ai-memory project name (docs/03 §4, workspace fixed to `factory`)
  case "$1" in
    agent)   printf 'agent--%s' "${2:?}" ;;
    project) printf 'project--%s' "$S0_06_PROJECT" ;;
    team)    printf 'team--%s' "$S0_06_TEAM" ;;
    company) printf '_global' ;;
    *) echo "collect_leg: unknown scope $1" >&2; exit 64 ;;
  esac
}

raw_search() {    # <project> <out>
  curl -sS --fail --config "$CFG" --get \
    --data-urlencode "q=$QUERY" \
    --data-urlencode "workspace=factory" \
    --data-urlencode "project=$1" \
    --data-urlencode "limit=20" \
    "$BASE/api/v1/search" > "$2"
}

raw_pages() {     # <project> <out>
  curl -sS --fail --config "$CFG" \
    "$BASE/api/v1/workspaces/factory/projects/$1/pages" > "$2"
}

tuple_file() {    # <agent> <out> — the caller-supplied identity tuple, no scopes field
  python3 - "$1" "$2" <<'PY'
import json, sys
agent, out = sys.argv[1], sys.argv[2]
import os
json.dump({"actor": "svc-agent-runner", "agent": agent,
           "team": os.environ["S0_06_TEAM"], "project": os.environ["S0_06_PROJECT"]},
          open(out, "w"), indent=2, sort_keys=True)
PY
}

case "$LEG" in
  precedence)
    tuple_file "$S0_06_AGENT" "$ROOT/precedence/tuple.json"
    for run in 1 2; do
      python3 "$ADAPTER" recall --tuple-file "$ROOT/precedence/tuple.json" --query "$QUERY" \
        --base-url "$BASE" --token-file "$RUNDIR/token" \
        --out "$ROOT/precedence/recall-$run.json" \
        --events "$ROOT/precedence/events-$run.jsonl" >/dev/null
    done
    for scope in agent project team company; do
      raw_search "$(project_for "$scope" "$S0_06_AGENT")" "$ROOT/precedence/raw-$scope.json"
    done
    ;;
  write-scope)
    tuple_file "$S0_06_AGENT" "$ROOT/write-scope/tuple.json"
    cat > "$ROOT/write-scope/record.json" <<'REC'
{
  "session": "sess-7f2a",
  "turn": "12",
  "event_id": "evt-0003",
  "body": "# Retention decision\n\nStage-0 observation written by the authorized active scope.\n"
}
REC
    for out in write retry; do
      python3 "$ADAPTER" write --tuple-file "$ROOT/write-scope/tuple.json" --scope agent \
        --record-file "$ROOT/write-scope/record.json" \
        --base-url "$BASE" --token-file "$RUNDIR/token" \
        --out "$ROOT/write-scope/$out.json" \
        --events "$ROOT/write-scope/events-$out.jsonl" >/dev/null
    done
    for scope in agent project team company; do
      raw_pages "$(project_for "$scope" "$S0_06_AGENT")" "$ROOT/write-scope/raw-$scope.json"
    done
    ;;
  leak)
    cp "$PROOF_DIR/fixtures/honeytokens.json" "$ROOT/leak/honeytokens.json"
    tuple_file "$S0_06_LEAK_AGENT" "$ROOT/leak/tuple.json"
    # a-beta is bound to agent+project only in bindings.json, so team/company are never queried.
    python3 "$ADAPTER" recall --tuple-file "$ROOT/leak/tuple.json" --query honeytoken \
      --base-url "$BASE" --token-file "$RUNDIR/token" \
      --out "$ROOT/leak/recall.json" --events "$ROOT/leak/events.jsonl" >/dev/null
    for scope in agent project team company; do
      curl -sS --fail --config "$CFG" --get \
        --data-urlencode "q=honeytoken" \
        --data-urlencode "workspace=factory" \
        --data-urlencode "project=$(project_for "$scope" "$S0_06_LEAK_AGENT")" \
        --data-urlencode "limit=20" \
        "$BASE/api/v1/search" > "$ROOT/leak/raw-$scope.json"
    done
    ;;
  denied)
    # The seed's own negative fixture, at the seed's literal path, against a LIVE instance: the
    # denial has to arrive without a single request reaching the substrate.
    python3 "$ADAPTER" recall \
      --tuple-file "$PROOF_DIR/../../fixtures/s0-06/neg-unauthorized-tuple.json" \
      --query "$QUERY" --base-url "$BASE" --token-file "$RUNDIR/token" \
      --out "$ROOT/denied/recall.json" --events "$ROOT/denied/events.jsonl" && rc=0 || rc=$?
    [ "${rc:-0}" -eq 1 ] || { echo "collect_leg: denied leg exited $rc, expected 1" >&2; exit 71; }
    ;;
  *)
    echo "collect_leg: unknown leg $LEG" >&2; exit 64 ;;
esac
echo "collect_leg: $LEG captured under $ROOT"
