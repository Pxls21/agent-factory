#!/usr/bin/env bash
# S0-06 PC leg — bring up ONE private, pinned ai-memory instance. NOT run in the sandbox.
#
# Idempotent clone of the pinned commit, release build with the toolchain the crate itself pins,
# a FRESH temp data dir, a loopback-only bind on a port this script proved is free, the safe
# posture of docs/04 §6, and a run-scoped bearer token in a 0600 file that is never printed.
#
# The instance is this script's OWN process: its pid is written to $RUNDIR/ai-memory.pid and
# run_s0_06_legs.sh stops it with `kill <that pid>` after confirming ownership through
# /proc/<pid>/exe. Never `pkill`/`killall` — on the owner's box those match the production
# containers too (AF-AP-34). The port preflight refuses rather than squatting a bound port.
#
# External commands used (bash builtins excluded; this list is the PC portability contract and is
# enforced by tests/test_s0_06_four_scope.py): awk, cargo, cat, curl, cut, dirname, git, grep, head,
# install, mkdir, nohup, python3, rustc, sed, seq, sha256sum, sleep, ss, tr.
#
#   start_ai_memory.sh <run-dir> [port]
#
# Writes: <run-dir>/{ai-memory.pid, token, curl.cfg, serve.log, substrate.json, data/}
set -euo pipefail

RUNDIR="${1:?usage: start_ai_memory.sh <run-dir> [port]}"
PORT="${2:-48606}"
PINNED_COMMIT="73715b6f1b2f0abb0a8b0ed47c1f69b1bd1b806e"   # upstream.lock.yaml:33-38
PINNED_VERSION="1.39.0"
# The default clone lives INSIDE this run's own dir: `git checkout --detach` on a path the
# operator already uses would move THEIR working tree to the pin (F-19). Set S0_06_SRC to reuse a
# checkout (and its `target/`) deliberately - the default run pays a full clone and release build.
SRC="${S0_06_SRC:-$RUNDIR/src/ai-memory}"
REPO_URL="https://github.com/akitaonrails/ai-memory.git"

mkdir -p "$RUNDIR"

# --- preflight: the port must be free. No squatting on the owner's box. -------------------
if command -v ss >/dev/null 2>&1; then
  if ss -ltn "sport = :$PORT" 2>/dev/null | awk 'NR>1' | grep -q .; then
    echo "start_ai_memory: port $PORT is already bound - refusing to start" >&2
    exit 65
  fi
else
  python3 - "$PORT" <<'PY' || exit 65
import socket, sys
s = socket.socket()
try:
    s.bind(("127.0.0.1", int(sys.argv[1])))
except OSError:
    print("start_ai_memory: port is already bound - refusing to start", file=sys.stderr)
    sys.exit(1)
finally:
    s.close()
PY
fi

# --- pinned checkout (idempotent) ---------------------------------------------------------
if [ ! -d "$SRC/.git" ]; then
  mkdir -p "$(dirname "$SRC")"
  git clone "$REPO_URL" "$SRC"
fi
git -C "$SRC" fetch --quiet origin "$PINNED_COMMIT" || git -C "$SRC" fetch --quiet origin
git -C "$SRC" checkout --quiet --detach "$PINNED_COMMIT"
HEAD_SHA="$(git -C "$SRC" rev-parse HEAD)"
[ "$HEAD_SHA" = "$PINNED_COMMIT" ] || { echo "start_ai_memory: checkout is $HEAD_SHA, not the pin" >&2; exit 66; }

# --- build (release). The crate pins its own toolchain in rust-toolchain.toml (channel 1.95);
# the explicit override keeps the build honest if that file ever moves. The binary target is
# `ai-memory` in package `ai-memory-cli` (crates/ai-memory-cli/Cargo.toml:1-13).
cargo "+${S0_06_TOOLCHAIN:-1.95.0}" build --release --manifest-path "$SRC/Cargo.toml" \
  -p ai-memory-cli --bin ai-memory
BIN="$SRC/target/release/ai-memory"
[ -x "$BIN" ] || { echo "start_ai_memory: $BIN not built" >&2; exit 67; }
BIN_SHA="$(sha256sum "$BIN" | cut -d' ' -f1)"

# --- run-scoped credential. Generated here, 0600, never echoed. ---------------------------
install -m 0600 /dev/null "$RUNDIR/token"
"$BIN" generate-auth-token > "$RUNDIR/token"
# curl reads the header from this config file so the token never appears in a command line or in
# /proc/<pid>/cmdline (AF-AP-39).
install -m 0600 /dev/null "$RUNDIR/curl.cfg"
# ONE derivation, two consumers (F-18): curl's config file and the child's environment must carry
# the SAME bytes. `generate-auth-token` prints exactly one line today
# (crates/ai-memory-cli/src/commands/generate_auth_token.rs:26), but a future banner line would
# otherwise split `sed '$!d'` from `cat` and the server would expect a different token than curl
# sends. `printf` is a bash builtin, so the value never reaches any process argv (AF-AP-39).
TOKEN_VALUE="$(sed -e '$!d' -e 's/[[:space:]]*$//' "$RUNDIR/token" | tr -d '\n')"
printf 'header = "Authorization: Bearer %s"\n' "$TOKEN_VALUE" > "$RUNDIR/curl.cfg"

# --- fresh data dir + safe posture (docs/04 §6; the `__` nesting is real -
# figment.merge(Env::prefixed("AI_MEMORY_").split("__")), crates/ai-memory-cli/src/config.rs:937)
DATA_DIR="$RUNDIR/data"
mkdir -p "$DATA_DIR"
export AI_MEMORY_DATA_DIR="$DATA_DIR"
export AI_MEMORY_AUTO_IMPROVE__REQUIRE_APPROVAL=true
export AI_MEMORY_AUTO_IMPROVE__SCHEDULER__ENABLED=false
export AI_MEMORY_MAINTENANCE__ENABLED=false
export AI_MEMORY_SLOTS__PER_USER=false
# The token reaches the child through the ENVIRONMENT built here, never through argv.
AI_MEMORY_AUTH_TOKEN="$TOKEN_VALUE"
export AI_MEMORY_AUTH_TOKEN

"$BIN" init >> "$RUNDIR/serve.log" 2>&1 || true   # one-time; already-initialised is not an error
nohup "$BIN" serve --transport http --bind "127.0.0.1:$PORT" --enable-web \
  >> "$RUNDIR/serve.log" 2>&1 &
SERVE_PID=$!
echo "$SERVE_PID" > "$RUNDIR/ai-memory.pid"

# --- failure-aware wait: the loop exits on readiness OR on the process dying, never on silence.
ready=no
for _ in $(seq 1 120); do
  if ! kill -0 "$SERVE_PID" 2>/dev/null; then
    echo "start_ai_memory: serve exited during startup; see $RUNDIR/serve.log" >&2
    exit 68
  fi
  if curl -sS --config "$RUNDIR/curl.cfg" -o /dev/null \
       "http://127.0.0.1:$PORT/api/v1/workspaces" 2>/dev/null; then
    ready=yes
    break
  fi
  sleep 0.5
done
[ "$ready" = yes ] || { echo "start_ai_memory: /api/v1 not ready after 60s" >&2; exit 69; }

VERSION_OUT="$("$BIN" --version 2>&1 | head -n 1)"
CARGO_VERSION="$(cargo "+${S0_06_TOOLCHAIN:-1.95.0}" --version 2>&1 | head -n 1)"
RUSTC_VERSION="$(rustc "+${S0_06_TOOLCHAIN:-1.95.0}" --version 2>&1 | head -n 1)"
# The posture is READ BACK from the serving child's own environment, never echoed from the
# exports above: config-presence is not delivery (F-4). ONLY the four posture keys are read - a
# `grep "^AI_MEMORY_"` would also match AI_MEMORY_AUTH_TOKEN and write this run's bearer into the
# evidence bundle.
POSTURE_OBSERVED="$(python3 - "$SERVE_PID" <<'POSTURE'
import json, sys
KEYS = ("AI_MEMORY_AUTO_IMPROVE__REQUIRE_APPROVAL", "AI_MEMORY_AUTO_IMPROVE__SCHEDULER__ENABLED",
        "AI_MEMORY_MAINTENANCE__ENABLED", "AI_MEMORY_SLOTS__PER_USER")
raw = open("/proc/%s/environ" % sys.argv[1], "rb").read().decode("utf-8", "replace")
env = dict(pair.split("=", 1) for pair in raw.split("\0") if "=" in pair)
print(json.dumps({key: env.get(key, "<absent>") for key in KEYS}, sort_keys=True))
POSTURE
)"
case "$VERSION_OUT" in
  *"$PINNED_VERSION"*) : ;;
  *) echo "start_ai_memory: binary reports '$VERSION_OUT', expected $PINNED_VERSION" >&2; exit 70 ;;
esac

# `binary_sha256_observed` is PROVENANCE, not a pin: a release build is not bit-reproducible
# across toolchains and hosts, so no constant in this repo can name the expected digest. Every leg
# re-hashes the same path and the checker requires all five reads to agree - what this field can
# honestly claim is that ONE binary served the whole run (F-2).
cat > "$RUNDIR/substrate.json" <<EOF
{
  "bin_path": "$BIN",
  "binary_sha256_observed": "$BIN_SHA",
  "cargo_version": "$CARGO_VERSION",
  "commit": "$PINNED_COMMIT",
  "component": "ai-memory",
  "data_dir": "$DATA_DIR",
  "port": $PORT,
  "posture": {
    "AI_MEMORY_AUTO_IMPROVE__REQUIRE_APPROVAL": "true",
    "AI_MEMORY_AUTO_IMPROVE__SCHEDULER__ENABLED": "false",
    "AI_MEMORY_MAINTENANCE__ENABLED": "false",
    "AI_MEMORY_SLOTS__PER_USER": "false"
  },
  "posture_observed": $POSTURE_OBSERVED,
  "rustc_version": "$RUSTC_VERSION",
  "version": "$PINNED_VERSION",
  "version_command": "ai-memory --version",
  "version_stdout": "$VERSION_OUT"
}
EOF
echo "start_ai_memory: pid $SERVE_PID on 127.0.0.1:$PORT, data $DATA_DIR"
