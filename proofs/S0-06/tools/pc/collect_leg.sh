#!/usr/bin/env bash
# S0-06 PC leg — capture ONE leg of the evidence bundle. NOT run in the sandbox.
#
#   collect_leg.sh <leg> <bundle-root>        leg = precedence | write-scope | leak | denied
#
# substrate.json is copied FIRST, before any leg file exists, so a bundle can never carry leg
# evidence without the identity of the instance that produced it. Each leg also RE-HASHES the
# binary named by that file (`substrate-observed.json`): the digest is provenance, not a pin, and
# what it can prove is that one binary served the whole run (F-2).
#
# The raw instruments here are plain `curl` reads of `/api/v1`, deliberately NOT the adapter: the
# adapter is the subject of the proof, so every assertion has one instrument that bypasses it.
#   * search      GET /api/v1/search?q&workspace&project&limit   -> [ApiSearchHit]
#                 (crates/ai-memory-web/src/routes/api.rs:41-45, 1254-1263)
#   * page list   GET /api/v1/workspaces/{ws}/projects/{p}/pages -> [PageSummary]
#                 (api.rs:33-36; crates/ai-memory-store/src/reader.rs:1174-1185)
# Every raw read records the URL it was actually fetched from (curl's own `%{url_effective}`,
# never a re-typed echo) beside the payload as `raw-<scope>.url`, so a reader can tell four
# scopes from four copies of one project's answer (F-5).
# The bearer token reaches curl through a 0600 --config file, never through argv (AF-AP-39).
#
# The denied and precedence legs also record the instance port's socket table before and after the
# leg (`socket-witness.json`): a SUBSTRATE-SIDE witness for "no request was made", paired with the
# precedence leg as its positive control (D-3b). The pinned server has no per-request access log
# to count instead — see check_four_scope.py's module docstring for the source trace.
#
# Environment (exported by run_s0_06_legs.sh): S0_06_BASE_URL, S0_06_RUNDIR, S0_06_AGENT,
# S0_06_TEAM, S0_06_PROJECT, S0_06_LEAK_AGENT.
# External commands used (bash builtins excluded; this list is the PC portability contract and is
# enforced by tests/test_s0_06_four_scope.py): awk, cat, cp, curl, cut, dirname, mkdir, python3,
# sha256sum, sort, ss.
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
PORT="${BASE##*:}"

command -v ss >/dev/null 2>&1 || {
  echo "collect_leg: ss is required for the substrate-side socket witness" >&2; exit 72; }

mkdir -p "$ROOT/$LEG"
cp "$RUNDIR/substrate.json" "$ROOT/substrate.json"

# --- this leg's own read of the serving binary (F-2) ---------------------------------------
BIN_PATH="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["bin_path"])' \
  "$RUNDIR/substrate.json")"
[ -x "$BIN_PATH" ] || { echo "collect_leg: $BIN_PATH is not executable" >&2; exit 73; }
OBSERVED_SHA="$(sha256sum "$BIN_PATH" | cut -d' ' -f1)"
python3 - "$LEG" "$BIN_PATH" "$OBSERVED_SHA" "$ROOT/$LEG/substrate-observed.json" <<'OBSERVED'
import json, sys
leg, bin_path, digest, out = sys.argv[1:5]
with open(out, "w", encoding="utf-8") as handle:
    json.dump({"bin_path": bin_path, "binary_sha256_observed": digest, "leg": leg},
              handle, indent=2, sort_keys=True)
    handle.write("\n")
OBSERVED

socket_snapshot() {   # every socket 4-tuple currently on the instance's port, one per line
  ss -Htan "( sport = :$PORT or dport = :$PORT )" | awk '{print $4, $5}' | sort
}

write_witness() {     # <leg> <before-file> <after-file>
  python3 - "$PORT" "$2" "$3" "$ROOT/$1/socket-witness.json" <<'WITNESS'
import json, sys
port, before, after, out = sys.argv[1:5]

def lines(path):
    with open(path, encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]

with open(out, "w", encoding="utf-8") as handle:
    json.dump({"after": lines(after), "before": lines(before),
               "instrument": "ss -Htan ( sport = :%s or dport = :%s )" % (port, port),
               "port": int(port)}, handle, indent=2, sort_keys=True)
    handle.write("\n")
WITNESS
}

project_for() {   # scope -> ai-memory project name (docs/03 §4, workspace fixed to `factory`)
  case "$1" in
    agent)   printf 'agent--%s' "${2:?}" ;;
    project) printf 'project--%s' "$S0_06_PROJECT" ;;
    team)    printf 'team--%s' "$S0_06_TEAM" ;;
    company) printf '_global' ;;
    *) echo "collect_leg: unknown scope $1" >&2; exit 64 ;;
  esac
}

raw_search() {    # <project> <out-json> <out-url>
  curl -sS --fail --config "$CFG" --get \
    --data-urlencode "q=$QUERY" \
    --data-urlencode "workspace=factory" \
    --data-urlencode "project=$1" \
    --data-urlencode "limit=20" \
    -o "$2" -w '%{url_effective}\n' \
    "$BASE/api/v1/search" > "$3"
}

raw_pages() {     # <project> <out-json> <out-url>
  curl -sS --fail --config "$CFG" \
    -o "$2" -w '%{url_effective}\n' \
    "$BASE/api/v1/workspaces/factory/projects/$1/pages" > "$3"
}

raw_leak_search() {   # <project> <out-json> <out-url> — the leak leg's own query term
  curl -sS --fail --config "$CFG" --get \
    --data-urlencode "q=honeytoken" \
    --data-urlencode "workspace=factory" \
    --data-urlencode "project=$1" \
    --data-urlencode "limit=20" \
    -o "$2" -w '%{url_effective}\n' \
    "$BASE/api/v1/search" > "$3"
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
    # The POSITIVE CONTROL for the denied leg's witness: this leg genuinely talks to the substrate,
    # so the same instrument must record new connections here or its zero over there means nothing.
    socket_snapshot > "$RUNDIR/witness-before-$LEG"
    for run in 1 2; do
      python3 "$ADAPTER" recall --tuple-file "$ROOT/precedence/tuple.json" --query "$QUERY" \
        --base-url "$BASE" --token-file "$RUNDIR/token" \
        --out "$ROOT/precedence/recall-$run.json" \
        --events "$ROOT/precedence/events-$run.jsonl" >/dev/null
    done
    for scope in agent project team company; do
      raw_search "$(project_for "$scope" "$S0_06_AGENT")" \
        "$ROOT/precedence/raw-$scope.json" "$ROOT/precedence/raw-$scope.url"
    done
    socket_snapshot > "$RUNDIR/witness-after-$LEG"
    write_witness "$LEG" "$RUNDIR/witness-before-$LEG" "$RUNDIR/witness-after-$LEG"
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
      raw_pages "$(project_for "$scope" "$S0_06_AGENT")" \
        "$ROOT/write-scope/raw-$scope.json" "$ROOT/write-scope/raw-$scope.url"
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
      raw_leak_search "$(project_for "$scope" "$S0_06_LEAK_AGENT")" \
        "$ROOT/leak/raw-$scope.json" "$ROOT/leak/raw-$scope.url"
    done
    ;;
  denied)
    # The seed's own negative fixture, at the seed's literal path, against a LIVE instance: the
    # denial has to arrive without a single request reaching the substrate — proven by the
    # adapter's event stream AND by the socket table on either side of this one command.
    socket_snapshot > "$RUNDIR/witness-before-$LEG"
    python3 "$ADAPTER" recall \
      --tuple-file "$PROOF_DIR/../../fixtures/s0-06/neg-unauthorized-tuple.json" \
      --query "$QUERY" --base-url "$BASE" --token-file "$RUNDIR/token" \
      --out "$ROOT/denied/recall.json" --events "$ROOT/denied/events.jsonl" && rc=0 || rc=$?
    socket_snapshot > "$RUNDIR/witness-after-$LEG"
    write_witness "$LEG" "$RUNDIR/witness-before-$LEG" "$RUNDIR/witness-after-$LEG"
    [ "${rc:-0}" -eq 1 ] || { echo "collect_leg: denied leg exited $rc, expected 1" >&2; exit 71; }
    ;;
  *)
    echo "collect_leg: unknown leg $LEG" >&2; exit 64 ;;
esac
echo "collect_leg: $LEG captured under $ROOT"
