#!/usr/bin/env bash
# S0-04 leg runner — RUNS ON THE PC ONLY. NOT run by the sandbox lane that wrote it.
#
# Captures the three S0-04 legs against the OmniRoute instance already running on :20128 and the
# S0-01 scripted backend behind the `s0-01-scripted` provider connection, then leaves an evidence
# bundle `check_compression.py` can grade.
#
# EVERY external call this script makes, in order:
#   1. curl  GET  $OMNIROUTE_BASE/api/health                      (unauthenticated preflight)
#   2. curl  GET  $OMNIROUTE_BASE/v1/models                       (authenticated; header FILE, never argv)
#   3. python3 capture_leg.py --leg off        (HTTP POST to $OMNIROUTE_BASE/v1/chat/completions)
#   4. python3 capture_leg.py --leg off-large  (HTTP POST to $OMNIROUTE_BASE/v1/chat/completions)
#   5. python3 capture_leg.py --find-record  x2                   (local file copy, no network)
#   6. python3 capture_leg.py --config                            (local file read, no network)
# It starts the scripted backend ONLY if its pidfile does not name a live, owned process, and it
# stops NOTHING it did not start. Process identity is read from the pidfile plus
# /proc/<pid>/exe — never `pkill -f`/`pgrep -f` by name (AF-AP-34).
#
# Environment:
#   OMNIROUTE_BASE        default http://127.0.0.1:20128
#   OMNIROUTE_KEY_FILE    0600 env file carrying `OMNIROUTE_API_KEY=…` (read in place by
#                         capture_leg.py; this script only passes the PATH)
#   S0_01_HOME            default $HOME/s0-01-pinned  (token file, markers, record dirs)
#   HERMES_PROFILE        default $HOME/.hermes/profiles/agentfactory/config.yaml
#   HERMES_PROVIDER       default factory-router
#   OUT_ROOT              default <repo>/proofs/S0-04/evidence
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROOF_DIR="$(cd "$HERE/../.." && pwd)"
REPO_ROOT="$(cd "$PROOF_DIR/../.." && pwd)"
BASE="${OMNIROUTE_BASE:-http://127.0.0.1:20128}"
KEYFILE="${OMNIROUTE_KEY_FILE:-${OMNIROUTE_API_KEY_FILE:-}}"
S0_01_HOME="${S0_01_HOME:-$HOME/s0-01-pinned}"
PROFILE="${HERMES_PROFILE:-$HOME/.hermes/profiles/agentfactory/config.yaml}"
PROVIDER="${HERMES_PROVIDER:-factory-router}"
OUT="${OUT_ROOT:-$PROOF_DIR/evidence}"
CAPTURE="$HERE/capture_leg.py"
BACKEND="$REPO_ROOT/proofs/S0-01/tools/scripted_backend.py"
TOKEN_FILE="$S0_01_HOME/.secrets/scripted-upstream.env"
PIDFILE="$S0_01_HOME/.markers/s0-04-backend.pid"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
RECORD_DIR="$S0_01_HOME/records/s0-04-$RUN_ID"
STARTED_BACKEND=0

die() { printf 'run_s0_04_legs: FAIL %s\n' "$*" >&2; exit 1; }
say() { printf 'run_s0_04_legs: %s\n' "$*"; }

for tool in curl python3 date grep readlink; do
  command -v "$tool" >/dev/null 2>&1 || die "tool missing: $tool"
done
[ -n "$KEYFILE" ] || die "OMNIROUTE_KEY_FILE is not set"
[ -r "$KEYFILE" ] || die "key file $KEYFILE is unreadable"
[ -f "$CAPTURE" ] || die "capture_leg.py not found at $CAPTURE"
[ -f "$BACKEND" ] || die "scripted backend not found at $BACKEND"
[ -f "$PROFILE" ] || die "hermes profile not found at $PROFILE"
python3 -c 'import yaml' 2>/dev/null || die "PyYAML is absent; --config cannot parse the profile"

# 1. OmniRoute is up (health says nothing about WHICH instance answers — AF-AP-33; the model
#    listing below is the discriminating check).
code=$(curl -s -o /dev/null -w '%{http_code}' -m 20 "$BASE/api/health") \
  || die "curl to $BASE/api/health failed"
[ "$code" = "200" ] || die "GET $BASE/api/health -> $code"
say "health 200"

# 2. the scripted models are exposed through OmniRoute, and the id the FIXTURES carry is one of
#    them. The fixture body is COMMITTED BYTES: a mismatch is resolved with the coordinator, it
#    is never patched here (that would break the byte comparison the proof exists to make).
MODEL=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["body_b64"])' \
  "$PROOF_DIR/fixtures/request-baseline.json" \
  | python3 -c 'import base64,json,sys; print(json.loads(base64.b64decode(sys.stdin.read()))["model"])') \
  || die "cannot read the fixture model id"
catalog=$(mktemp) || die "mktemp failed"
code=$(curl -s -o "$catalog" -w '%{http_code}' -m 30 \
       -H @<(printf 'Authorization: Bearer %s\n' \
             "$(grep '^OMNIROUTE_API_KEY=' "$KEYFILE" | head -1 | cut -d= -f2- | tr -d '\r\n"')") \
       "$BASE/v1/models")
if [ "$code" != "200" ]; then rm -f "$catalog"; die "GET $BASE/v1/models -> $code"; fi
if ! grep -q "\"id\"[[:space:]]*:[[:space:]]*\"$MODEL\"" "$catalog"; then
  observed=$(grep -o '"id"[[:space:]]*:[[:space:]]*"[^"]*s0-01[^"]*"' "$catalog" | tr '\n' ' ')
  rm -f "$catalog"
  die "fixture model '$MODEL' is not in the OmniRoute catalog; observed scripted ids: ${observed:-none}. \
The fixture is committed bytes — resolve the routed id with the coordinator, do not edit it here"
fi
rm -f "$catalog"
say "catalog exposes $MODEL"

# 3. the scripted backend: reuse the running one by PIDFILE + /proc/<pid>/exe, never by name.
if [ -f "$PIDFILE" ] && pid=$(cat "$PIDFILE" 2>/dev/null) && [ -n "${pid:-}" ] \
   && [ -d "/proc/$pid" ] && readlink "/proc/$pid/exe" 2>/dev/null | grep -q 'python'; then
  # /proc/<pid> can be a RECYCLED pid (AF-AP-55): confirm the SERVICE answers, not just the pid.
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 5 "http://127.0.0.1:20201/healthz") || code=000
  [ "$code" = "200" ] || die "pidfile names pid $pid but :20201/healthz -> $code; not reusing it"
  say "reusing scripted backend pid $pid (pidfile $PIDFILE, /healthz 200)"
  RECORD_DIR="$S0_01_HOME/.markers/upstream-records"
else
  [ -r "$TOKEN_FILE" ] || die "scripted backend is not running and $TOKEN_FILE is unreadable"
  mkdir -p "$RECORD_DIR" "$(dirname "$PIDFILE")" || die "cannot create $RECORD_DIR"
  setsid python3 "$BACKEND" --port 20201 --token-file "$TOKEN_FILE" \
    --record-dir "$RECORD_DIR" --pidfile "$PIDFILE" \
    </dev/null >"$S0_01_HOME/.markers/s0-04-backend.log" 2>&1 &
  STARTED_BACKEND=1
  for _ in $(seq 1 40); do
    code=$(curl -s -o /dev/null -w '%{http_code}' -m 2 "http://127.0.0.1:20201/healthz") || code=000
    [ "$code" = "200" ] && break
    # failure-aware wait: a dead backend must not be waited out to the full deadline
    if [ -f "$PIDFILE" ]; then p=$(cat "$PIDFILE"); [ -d "/proc/$p" ] || die "backend exited during startup"; fi
    sleep 0.25
  done
  [ "$code" = "200" ] || die "scripted backend did not answer /healthz"
  say "started scripted backend pid $(cat "$PIDFILE") records $RECORD_DIR"
fi

# 4-6. the three legs.
rc=0
for leg in off off-large; do
  case "$leg" in
    off)       fixture="$PROOF_DIR/fixtures/request-baseline.json" ;;
    off-large) fixture="$PROOF_DIR/fixtures/request-large.json" ;;
  esac
  nonce=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["nonce"])' "$fixture") \
    || die "cannot read the nonce of $fixture"
  OMNIROUTE_KEY_FILE="$KEYFILE" python3 "$CAPTURE" --leg "$leg" --fixture "$fixture" \
    --out "$OUT/$leg" --base-url "$BASE" || { rc=1; say "leg $leg capture FAILED"; continue; }
  python3 "$CAPTURE" --leg "$leg" --find-record --record-dir "$RECORD_DIR" \
    --nonce "$nonce" --out "$OUT/$leg" || { rc=1; say "leg $leg record copy FAILED"; }
done
python3 "$CAPTURE" --leg config --config --profile "$PROFILE" --provider "$PROVIDER" \
  --out "$OUT/config" || { rc=1; say "config leg FAILED"; }

if [ "$STARTED_BACKEND" = "1" ]; then
  pid=$(cat "$PIDFILE" 2>/dev/null || true)
  if [ -n "${pid:-}" ] && [ -d "/proc/$pid" ]; then kill "$pid" && say "stopped backend pid $pid (ours)"; fi
fi

say "evidence at $OUT — grade it with: python3 $PROOF_DIR/check_compression.py $OUT"
exit "$rc"
