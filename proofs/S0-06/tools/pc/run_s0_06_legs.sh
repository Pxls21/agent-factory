#!/usr/bin/env bash
# S0-06 PC runner — the whole proof against a REAL pinned ai-memory. NOT run in the sandbox.
#
#   run_s0_06_legs.sh [<bundle-root>] [<port>]      default bundle root: proofs/S0-06/evidence
#
# Order: start a private instance -> seed the four scopes through the raw write surface -> capture
# the four legs -> stop the instance by ITS OWN pid -> grade the bundle with check_four_scope.py.
#
# The instance is this run's own process on its own loopback port with its own temp data dir. It
# never touches the owner's running services, and the stop path reads the pid from the pidfile
# this run wrote and confirms /proc/<pid>/exe before signalling (AF-AP-34: `pkill`/`killall` on
# the PC also match the owner's production containers).
#
# External commands used (bash builtins excluded; this list is the PC portability contract and is
# enforced by tests/test_s0_06_four_scope.py): bash, cat, dirname, mkdir, mktemp, python3, readlink,
# shred.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PROOF_DIR="$(cd "$HERE/../.." && pwd)"
REPO_ROOT="$(cd "$PROOF_DIR/../.." && pwd)"
BUNDLE="${1:-$PROOF_DIR/evidence}"
PORT="${2:-48606}"

# The identities come from the committed authorization table, never from this script.
export S0_06_AGENT="${S0_06_AGENT:-a-alpha}"        # bindings.json row 1: all four scopes
export S0_06_LEAK_AGENT="${S0_06_LEAK_AGENT:-a-beta}"  # row 2: agent + project only
export S0_06_TEAM="${S0_06_TEAM:-t-core}"
export S0_06_PROJECT="${S0_06_PROJECT:-p-atlas}"

RUNDIR="$(mktemp -d "${TMPDIR:-/tmp}/s0-06-run-XXXXXX")"
export S0_06_RUNDIR="$RUNDIR"
export S0_06_BASE_URL="http://127.0.0.1:$PORT"

stop_instance() {
  local pidfile="$RUNDIR/ai-memory.pid" pid exe
  [ -f "$pidfile" ] || return 0
  pid="$(cat "$pidfile")"
  [ -n "$pid" ] || return 0
  kill -0 "$pid" 2>/dev/null || return 0
  exe="$(readlink "/proc/$pid/exe" 2>/dev/null || true)"
  case "$exe" in
    */target/release/ai-memory) kill "$pid" ;;
    *) echo "run_s0_06_legs: pid $pid is '$exe', not our ai-memory - NOT signalling" >&2 ;;
  esac
}

# The run-scoped credential dies with the run (F-18). serve.log and substrate.json stay: the
# operator needs both, and neither carries the token. This is NOT gated on the pidfile - a run
# that fails before the instance starts must still leave no credential behind.
shred_credentials() {
  local secret
  for secret in "$RUNDIR/token" "$RUNDIR/curl.cfg"; do
    [ -f "$secret" ] && shred -u "$secret"
  done
  return 0
}

cleanup() {
  stop_instance
  shred_credentials
}
trap cleanup EXIT

bash "$HERE/start_ai_memory.sh" "$RUNDIR" "$PORT"

python3 "$HERE/seed_scopes.py" --base-url "$S0_06_BASE_URL" --token-file "$RUNDIR/token" \
  --agent "$S0_06_AGENT" --team "$S0_06_TEAM" --project "$S0_06_PROJECT"
# The leak leg recalls as $S0_06_LEAK_AGENT, so `agent--<leak-agent>` has to exist and has to hold
# its own honeytoken: without this the raw read 404s (`lookup_project` ->
# `ScopeResolutionError::ProjectNotFoundInWorkspace` -> 404,
# crates/ai-memory-web/src/routes/api.rs:993-1007), the adapter degrades, the CLI exits 3 and
# `set -e` aborts the leg before anything is graded (F-1). Re-seeding the three SHARED projects is
# a no-op, not a double-stage: `upsert_page_in_tx` keys on (workspace, project, path) and returns
# the existing page id unchanged when body, frontmatter, title, tier and pinned all match
# (crates/ai-memory-store/src/ops.rs:711-762, asserted by `upsert_page_is_noop_when_body_unchanged`
# at `:6204-6237`, "no duplicate row for unchanged content").
python3 "$HERE/seed_scopes.py" --base-url "$S0_06_BASE_URL" --token-file "$RUNDIR/token" \
  --agent "$S0_06_LEAK_AGENT" --team "$S0_06_TEAM" --project "$S0_06_PROJECT"

mkdir -p "$BUNDLE"
for leg in denied precedence write-scope leak; do
  bash "$HERE/collect_leg.sh" "$leg" "$BUNDLE"
done
cat > "$BUNDLE/PROVENANCE.md" <<EOF
# PROVENANCE — live S0-06 evidence bundle

Captured by proofs/S0-06/tools/pc/run_s0_06_legs.sh against the private ai-memory origin recorded
in substrate.json. This file is required by the checker's exact root manifest.
EOF

cleanup
trap - EXIT

python3 "$PROOF_DIR/check_four_scope.py" "$BUNDLE"
echo "run_s0_06_legs: bundle at $BUNDLE (run dir $RUNDIR kept for serve.log and substrate.json;"
echo "run_s0_06_legs:  token and curl.cfg were shredded - delete the run dir when done)"
echo "run_s0_06_legs: mint with  python3 $REPO_ROOT/scripts/proof-runner run --proof S0-06 --venue pc-bridge --root $REPO_ROOT"
