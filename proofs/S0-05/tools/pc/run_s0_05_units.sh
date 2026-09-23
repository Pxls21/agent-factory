#!/usr/bin/env bash
# run_s0_05_units.sh — the LIVE-UNIT legs of S0-05, on the owner's PC.
#
#   NOT run here. Authored in the sandbox (lanes E1, E2, E2-R1, E3) and never executed on the PC: it
#   needs the live units, and lane delegates do not touch the PC bridge. Every claim below about the
#   PC is a PLAN read from docs/05_SECURITY.md:74-85, CD1 (tasks/briefs/s0-05-support/CD1-AMENDMENT.md,
#   whose three probes measured the units on the PC) and D-051 — not an observation of this script.
#
#   run_s0_05_units.sh <evidence-root> [unit...]      (default: hermes-acp buzz-acp)
#
# For each unit: check the pinned unit on disk (A1), create its own selective-egress namespace with
# ONLY that unit's allowed destinations (A8), PREFLIGHT that each one answers 2xx on its health path
# from inside it (E3-b R1, R2), launch
# the REAL unit in it as the non-root unit user (A4) with a clean environment (A5), its stdio on pipes
# (A3) and its own scratch tree (A2), record which process actually runs (A7), run the canary suite
# as that unit, stop it, tear down. Units that cannot run are declared in units.json as `not-run`
# with their reason — check_egress.py does not count them, and a declared-absent unit is never a pass.
#
# INPUTS (environment; resolved ONCE below and threaded explicitly):
#   S0_05_OMNIROUTE_PORT  OmniRoute's port (default 20128). A8: every allow entry is formed HERE as
#                         `$(egress_ns_host_ip <ns>):<port>`; there is no operator-typed address.
#   S0_05_UNIT_USER       <uid>:<gid> both units run as (A4). Default: the owner of the pinned agent
#                         realpath (uid 1000 on the PC). A resolved uid 0 is `not-run|unit would run as root`.
#   S0_05_PAIR_IDENTITY   the buzz-acp pair's S0-05 identity (A6): a file holding a `BUZZ_PRIVATE_KEY=`
#                         line, owned by the unit user, with no group/other bits. Read, never printed;
#                         the value reaches only the pair's environment. Never S0-01's .secrets.
#   S0_05_PIN_OVERRIDE    THE RECORDED OVERRIDE (A1): a JSON object {pin name: value} that replaces
#                         pinned values for a stand-in run (the sandbox cannot hold the PC's pinned
#                         binaries). Every unit row in units.json then carries "override": {...}, and
#                         check_egress.py refuses such a bundle for a live (pc-venue) claim, so a
#                         stand-in run can never pass as the live leg. LEAVE IT UNSET ON THE PC.
# Every pinned value (paths, digests, the buzz-acp argv shape, PATH, the relay URL, the S0-01 tree)
# is read from proofs/S0-01/pins.py at run time — the one source of truth; nothing here retypes one.
#
# DECLARED LIMITS, said plainly rather than worked around:
#  1. The canaries share the unit's network namespace; they are not the unit's own sockets. That
#     proves the NAMESPACE cannot reach a provider, which is the containment boundary docs/05 §6
#     specifies — it does not prove anything about the unit's in-process client behaviour.
#  2. No route or NAT leads OUT of a namespace: a model endpoint fails on ROUTING (ENETUNREACH) as
#     well as on the gate, and only C6 is discriminated by the firewall alone. The one host-side NAT
#     is D-051's relay reach: for the buzz-acp leg only, ONE nat PREROUTING rule on the pair's veth
#     host end forwards <host ip>:<relay port> to the pinned relay on 127.0.0.1, and route_localnet=1
#     lets that ONE interface route to loopback for the leg. egress_ns_destroy removes both, at the
#     leg's teardown and in `cleanup`.
#  3. A wrong pair identity file only fails the pair's C0 / relay handshake: this script checks its
#     place, mode, owner and shape, never whether the relay accepts the key.
#  4. unit-identity.json is unkeyed: it binds the process that ran to the pins, not against a forger
#     with root on the PC.
#  5. The two probe paths (E3-b R1: OmniRoute /api/health, the relay /health) are facts about the
#     services on the PC today; if one changes, the preflight refuses with the named not-2xx reason
#     (fail closed) and the fix is a one-line constant (OMNI_PROBE_PATH / RELAY_PROBE_PATH below).
#  6. A 2xx from a health path proves that the unit's namespace reaches that ip:port; it does not
#     prove the model API behind it would serve the unit (that is S0-03), nor which instance answers
#     (the AF-AP-33 class: health-200 is not the right instance).
#
# PREFLIGHT, not a workaround: a service bound only to 127.0.0.1 is unreachable from a namespace (a
# fresh namespace has its own empty loopback — findings §6a, docs/research/FINDINGS-STAGE0-v1.md:98-108).
# OmniRoute listens on 0.0.0.0:20128 (CD1 probe 1); the relay listens on 127.0.0.1:3999 only, which is
# what the relay reach is for. A destination that does not answer from the namespace is `not-run|
# positive control unreachable: ...`; one that answers outside 2xx is `not-run|positive control not
# 2xx: ...` (E3-b R2: the preflight is the collector's own C0 request, graded by the checker's own
# predicate); the script never falls back to a listener of its own.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
P="$(cd "$HERE/../.." && pwd)"
# shellcheck source=proofs/S0-05/netns_lib.sh
. "$P/netns_lib.sh"

EVIDENCE_ROOT=${1:?usage: run_s0_05_units.sh <evidence-root> [unit...]}; shift || true

status=$(egress_ns_capable) || { echo "run_s0_05_units: cannot run here ($status)" >&2; exit 2; }
SETPRIV_BIN=$(command -v setpriv) || { echo "run_s0_05_units: cannot run here (no-setpriv)" >&2; exit 2; }
ENV_BIN=$(command -v env); IP_BIN=$(command -v ip); PY_BIN=$(command -v python3)

OMNI_PORT=${S0_05_OMNIROUTE_PORT:-20128}
# R1 (E3-b): the path each allowed service answers 2xx on, asked by the preflight and by C0. Facts about
# the services on the PC, measured 2026-09-23 06:57Z by the coordinator's bridge probes (quoted in
# tasks/briefs/s0-05-support/E3-b-brief.md): OmniRoute `/api/health` 200 application/json while
# `/v1/models` is 401 (it now requires a key); the relay `/health` 200 text/plain while `/v1/models` is
# 404. If a service moves its health path, the preflight refuses it as not-2xx: change the constant.
OMNI_PROBE_PATH=/api/health
RELAY_PROBE_PATH=/health
UNIT_USER=${S0_05_UNIT_USER:-}
PAIR_IDENTITY=${S0_05_PAIR_IDENTITY:-}
PIN_OVERRIDE=${S0_05_PIN_OVERRIDE:-}
if [ -n "${ALLOWED_HERMES:-}${ALLOWED_BUZZACP:-}${S0_01_TOOLS:-}" ]; then
  echo "run_s0_05_units: ALLOWED_HERMES, ALLOWED_BUZZACP and S0_01_TOOLS are retired (A8: allow" \
       "entries are formed from the namespace's host address and a port; A1: no S0-01 tool); ignored" >&2
fi

# --- the pins, read ONCE from proofs/S0-01/pins.py, with the recorded override applied (A1) ------
declare -A PIN
PAIR_ARGV=()
_pins=$(mktemp) || exit 2
python3 -B - "$P/../S0-01" "$PIN_OVERRIDE" "$(egress_ns_host_ip s0-05-buzz-acp)" > "$_pins" <<'PY'
import ipaddress, json, os, sys
from urllib.parse import urlsplit
sys.path.insert(0, sys.argv[1])
import pins  # noqa: E402  (proofs/S0-01/pins.py: the one source of truth for every pinned value)
OVERRIDABLE = ("PINNED_AGENT_REALPATH", "PINNED_AGENT_ENTRYPOINT_SHA256",
               "PINNED_AGENT_INTERPRETER_REALPATH", "PINNED_BUZZ_ACP_EXE_REALPATH",
               "PINNED_BUZZ_ACP_SHA256", "PINNED_HERMES_HOME", "PINNED_RELAY_URL")
value = {name: getattr(pins, name) for name in OVERRIDABLE + ("PINNED_PATH",)}
override = {}
if sys.argv[2]:
    try:
        with open(sys.argv[2]) as fh:
            override = json.load(fh)
    except (OSError, ValueError) as exc:
        sys.exit(print(f"run_s0_05_units: S0_05_PIN_OVERRIDE unreadable: {exc}", file=sys.stderr) or 64)
    if (not isinstance(override, dict) or not override
            or any(k not in OVERRIDABLE or not isinstance(v, str) or not v for k, v in override.items())):
        sys.exit(print("run_s0_05_units: S0_05_PIN_OVERRIDE must map pin names (" + " ".join(OVERRIDABLE)
                       + ") to non-empty strings", file=sys.stderr) or 64)
    value.update(override)
relay = urlsplit(value["PINNED_RELAY_URL"])
try:
    ipaddress.IPv4Address(relay.hostname or "")
    relay_port = relay.port
except ValueError:
    relay_port = None
if relay.scheme != "ws" or not relay_port:
    sys.exit(print(f"run_s0_05_units: PINNED_RELAY_URL {value['PINNED_RELAY_URL']!r} is not "
                   "ws://<ipv4>:<port>", file=sys.stderr) or 2)
shape = list(pins.PINNED_LAUNCH_ARGV)
try:
    r, a = shape.index("--relay-url"), shape.index("--agent-command")
    fits = (shape[0] == pins.PINNED_BUZZ_ACP_EXE_REALPATH and shape[r + 1] == pins.PINNED_RELAY_URL
            and shape[a + 1] == pins.PINNED_TEE_PATH)
except ValueError:
    fits = False
if not fits:
    sys.exit(print("run_s0_05_units: pins.PINNED_LAUNCH_ARGV no longer has the shape this runner "
                   "substitutes into", file=sys.stderr) or 2)
# A6: the pinned shape with three substitutions only — the relay URL on the relay-reach address, the
# agent itself as the agent command (not S0-01's tee), and the S0-05 identity (environment, not argv).
# argv[0] is the pinned buzz-acp realpath; it moves only under a recorded override.
argv = [value["PINNED_BUZZ_ACP_EXE_REALPATH"]] + shape[1:]
argv[r + 1] = f"ws://{sys.argv[3]}:{relay_port}"
argv[a + 1] = value["PINNED_AGENT_REALPATH"]
pairs = dict(value, BASE=os.path.dirname(value["PINNED_HERMES_HOME"]), RELAY_HOST=relay.hostname,
             RELAY_PORT=str(relay_port),
             OVERRIDE=json.dumps(override, sort_keys=True, separators=(",", ":")) if override else "")
out = sys.stdout.buffer
for key, item in list(pairs.items()) + [("PAIR_ARGV", item) for item in argv]:
    out.write(key.encode() + b"\0" + item.encode() + b"\0")
PY
rc=$?
[ "$rc" -eq 0 ] || { rm -f "$_pins"; exit "$rc"; }
while IFS= read -r -d '' key && IFS= read -r -d '' item; do
  if [ "$key" = PAIR_ARGV ]; then PAIR_ARGV+=("$item"); else PIN[$key]=$item; fi
done < "$_pins"
rm -f "$_pins"
if [ -n "${PIN[OVERRIDE]}" ]; then
  echo "run_s0_05_units: PIN OVERRIDE ACTIVE — recorded on every unit row in units.json; this run" \
       "can never pass as the live leg: ${PIN[OVERRIDE]}" >&2
fi

# --- A4: the unit user, resolved ONCE ----------------------------------------------------------
[ -n "$UNIT_USER" ] || UNIT_USER=$(stat -Lc '%u:%g' -- "${PIN[PINNED_AGENT_REALPATH]}" 2>/dev/null)
if [ -n "$UNIT_USER" ] && ! [[ "$UNIT_USER" =~ ^(0|[1-9][0-9]{0,9}):(0|[1-9][0-9]{0,9})$ ]]; then
  echo "run_s0_05_units: S0_05_UNIT_USER must be <uid>:<gid>, got '$UNIT_USER'" >&2; exit 64
fi
UNIT_UID=${UNIT_USER%%:*}; UNIT_GID=${UNIT_USER##*:}

# --- the unit table: docs/05_SECURITY.md:74-85, one row per source ---------------------------
# A1: each unit row NAMES the pin of its executable, run directly from that realpath with no
# interpreter prefix — the kernel reads the unit's own shebang, so F8's "bash script handed to
# python3" cannot recur, and no S0-01 tool, .markers or .secrets path can appear in a row.
declare -A UNIT_EXE ABSENT
UNIT_EXE[hermes-acp]=PINNED_AGENT_REALPATH          # docs/05 §6 "Hermes -> OmniRoute"
UNIT_EXE[buzz-acp]=PINNED_BUZZ_ACP_EXE_REALPATH     # docs/05 §6 "buzz-acp -> Buzz relay and local hermes-acp"
# F10: s0-01-backend is NOT a docs/05 §6 source. It is the model-provider stand-in on
# OmniRoute's upstream side (the sanctioned stub in CLAUDE.md). Not a unit here.
# Units the plan names that DO NOT EXIST yet (docs/05 §6 rows with no implementation):
ABSENT[memory-adapter]="unit does not exist"
ABSENT[ai-memory]="unit does not exist"
ABSENT[dream-foundry]="unit does not exist"
ABSENT[pandaprobe]="unit does not exist"
ABSENT[harness-router]="unit does not exist (conditional, not deployed in v1)"
ABSENT[s0-01-backend]="not a docs/05 §6 source: the S0-01 scripted backend is the model-provider stand-in behind OmniRoute"

UNITS=("$@")
[ ${#UNITS[@]} -gt 0 ] || UNITS=(hermes-acp buzz-acp)

# A1: the file at a pinned path IS its own realpath and carries the pinned sha256.
_pin_ok() { [ -f "$1" ] && [ "$(readlink -f -- "$1")" = "$1" ] && [ "$(sha256sum -- "$1" | cut -d' ' -f1)" = "$2" ]; }

# A6: the pair's identity file, checked in this order and read without printing. Sets PAIR_KEY, or
# ID_REFUSED to the refusal detail. S0-01's .secrets is refused by PATH, before the file is opened.
_pair_identity() {
  local file=$PAIR_IDENTITY real mode line
  PAIR_KEY=""; ID_REFUSED=""
  real=$(readlink -m -- "${file:-/nonexistent}")
  case "$real/" in "${PIN[BASE]}/.secrets/"*) ID_REFUSED="S0-01 path $real"; return 1;; esac
  { [ -n "$file" ] && [ -e "$file" ]; } || { ID_REFUSED=absent; return 1; }
  mode=$(stat -Lc '%a' -- "$file")
  [[ "$mode" =~ ^[0-7]{1,4}$ ]] && [ $(( 8#$mode & 8#077 )) -eq 0 ] || { ID_REFUSED="mode $mode"; return 1; }
  [ "$(stat -Lc '%u' -- "$file")" = "$UNIT_UID" ] || { ID_REFUSED="owner uid $(stat -Lc '%u' -- "$file")"; return 1; }
  [ -f "$file" ] || { ID_REFUSED=shape; return 1; }   # never open a FIFO or a device
  while IFS= read -r line || [ -n "$line" ]; do
    case $line in BUZZ_PRIVATE_KEY=?*) PAIR_KEY=${line#BUZZ_PRIVATE_KEY=}; break;; esac
  done < "$file"
  [ -n "$PAIR_KEY" ] || { ID_REFUSED=shape; return 1; }
}

# A2: a stat census of S0-01's tree — <pinned base>/.markers and every v2-* directory in it — taken
# before the first unit and after the last. The base is pins.py's (the directory holding
# PINNED_HERMES_HOME), never a literal; a tree absent on this venue is recorded, not failed.
_s0_01_census() {
  python3 -B - "${PIN[BASE]}" <<'PY'
import json, os, stat, sys
markers = os.path.join(sys.argv[1], ".markers")
def snap(path):
    st = os.lstat(path)
    return [st.st_ino, st.st_uid, st.st_gid, stat.S_IMODE(st.st_mode), st.st_mtime_ns, st.st_ctime_ns]
entries = {}
try:
    entries[markers] = snap(markers)
    if stat.S_ISDIR(os.lstat(markers).st_mode):
        for name in sorted(os.listdir(markers)):
            path = os.path.join(markers, name)
            if name.startswith("v2-") and stat.S_ISDIR(os.lstat(path).st_mode):
                entries[path] = snap(path)
except FileNotFoundError:
    pass
print(json.dumps({"base": sys.argv[1], "entries": entries}, sort_keys=True))
PY
}

# A7: which process runs in the namespace, read from /proc at canary time and written to
# <unit>/unit-identity.json. Prints "ok" or every mismatch against the pins ("; "-joined).
_unit_identity() {  # <pid> <unit> <kind agent|binary> <exe pin> <entrypoint pin> <sha256 pin>
  python3 -B - "$1" "$ns" "$2" "$3" "$4" "$5" "$6" "$UNIT_UID" "$EVIDENCE_ROOT/$2/unit-identity.json" <<'PY'
import hashlib, json, os, subprocess, sys
pid, ns, unit, kind, want_exe, want_entry, want_sha, want_uid, out = sys.argv[1:10]
def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()
try:
    exe = os.path.realpath(f"/proc/{pid}/exe")
    with open(f"/proc/{pid}/cmdline", "rb") as fh:
        argv = [a.decode(errors="surrogateescape") for a in fh.read().split(b"\0")[:-1]]
    with open(f"/proc/{pid}/status") as fh:
        uid = [int(v) for v in next(l for l in fh if l.startswith("Uid:")).split()[1:5]]
    entry = os.path.realpath(argv[1]) if kind == "agent" and len(argv) > 1 else exe
    entry_sha = sha256(entry if kind == "agent" else f"/proc/{pid}/exe")
    in_ns = pid in subprocess.run(["ip", "netns", "pids", ns], capture_output=True, text=True).stdout.split()
except (OSError, StopIteration, ValueError, IndexError) as exc:
    sys.exit(print(f"no unit process {pid}: {exc.__class__.__name__}") or 1)
with open(out, "w") as fh:
    json.dump({"unit": unit, "pid": int(pid), "exe_realpath": exe, "entrypoint_realpath": entry,
               "entrypoint_sha256": entry_sha, "uid": uid, "argv": argv}, fh, indent=2, sort_keys=True)
    fh.write("\n")
problems = [f"pid {pid} not in {ns}"] if not in_ns else []
problems += [f"exe {exe} is not {want_exe}"] if exe != want_exe else []
problems += [f"entrypoint {entry} is not {want_entry}"] if entry != want_entry else []
problems += [f"entrypoint sha256 {entry_sha} is not the pin"] if entry_sha != want_sha else []
problems += ["uid 0"] if 0 in uid else ([f"uid {uid[0]} is not {want_uid}"] if str(uid[0]) != want_uid else [])
print("; ".join(problems) or "ok")
sys.exit(1 if problems else 0)
PY
}

# R2 (E3-b): the preflight is the collector's OWN C0 request — the real canaries/c0_allowed_target.sh
# inside the namespace, in the canaries' scrubbed environment (the `env -u` wrapper run_canaries.sh
# puts on every canary, its list read from canaries/_emit.sh), with the same path and the canaries' own
# connect and total timeouts — graded by the checker's OWN predicate (check_egress.c0_proves). Prints
# `ok`, `not-2xx <code>` (curl rc 0 with an HTTP status outside 2xx) or `unreachable` (no HTTP answer,
# or anything else that fails the predicate).
C0_SCRUB=(env)
for _var in $(bash -c '. "$1" && printf "%s" "$EGRESS_SCRUBBED_ENV"' _ "$P/canaries/_emit.sh"); do C0_SCRUB+=(-u "$_var"); done
[ "${#C0_SCRUB[@]}" -gt 1 ] || { echo "run_s0_05_units: cannot read the canaries' scrub list (canaries/_emit.sh)" >&2; exit 2; }
_c0_preflight() {  # <ns> <unit> <ip:port> <path>
  local record
  record=$(egress_ns_run "$1" "${C0_SCRUB[@]}" bash "$P/canaries/c0_allowed_target.sh" "$2" "$3" "$4")
  python3 -B - "$P/check_egress.py" "$record" <<'PY'
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("check_egress", sys.argv[1])
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
try:
    record = json.loads(sys.argv[2])
except ValueError:
    record = None
status = record.get("http_status") if isinstance(record, dict) else None
if isinstance(record, dict) and checker.c0_proves(record):
    print("ok")
elif (isinstance(record, dict) and record.get("rc") == 0 and checker._is_int(status) and status > 0
        and not 200 <= status < 300):
    print(f"not-2xx {status}")
else:
    print("unreachable")
PY
}

# One leg's teardown, on every path after the launch: close the unit's stdin if still held, destroy
# the namespace (it kills whatever is left inside and removes the relay reach — the backstop), drop
# the name from NS_LIVE, reap the log pipe's reader BY PID, remove the pipes.
_leg_teardown() {
  if [ -n "${unit_in:-}" ]; then exec {unit_in}>&-; unit_in=""; fi
  egress_ns_destroy "$ns"; NS_LIVE=${NS_LIVE//$ns/}; NS_LIVE=${NS_LIVE# }
  local _ pid keep=""
  for _ in $(seq 1 50); do kill -0 "$log_pid" 2>/dev/null || break; sleep 0.1; done
  _kill_our_child "$log_pid"; wait "$log_pid" 2>/dev/null
  for pid in $LOG_PIDS; do [ "$pid" = "$log_pid" ] || keep="$keep $pid"; done
  LOG_PIDS=$keep
  rm -rf "$fifo_dir"
}

# Kill a pid only while it is still THIS runner's child (a reaped pid may be reused).
_kill_our_child() { [ "$(ps -o ppid= -p "$1" 2>/dev/null | tr -d ' ')" = "$$" ] && kill -KILL "$1" 2>/dev/null; }

mkdir -p "$EVIDENCE_ROOT"
declare -A RESULT
NS_LIVE=""; LOG_PIDS=""; FIFO_DIRS=""
# F3: cleanup destroys only namespaces this runner created and still owns (owner record = $$);
# destroy also removes a relay reach (D-051). Then any log reader left, by pid, and the pipes.
cleanup() {
  local ns owner_pid pid dir
  for ns in $NS_LIVE; do
    owner_pid=$(cat "$(egress_ns_owner_file "$ns")" 2>/dev/null)
    [ "$owner_pid" = "$$" ] && egress_ns_destroy "$ns"
  done
  for pid in $LOG_PIDS; do _kill_our_child "$pid"; done
  for dir in $FIFO_DIRS; do rm -rf "$dir"; done
}
# R4 (E3-b): a stop stops. `cleanup` runs ONCE, on EXIT; SIGINT and SIGTERM exit 130 / 143 through it,
# so no further unit leg starts, no units.json is written, and neither the census comparison nor the
# checker runs. (`trap cleanup EXIT INT TERM` ran cleanup on the signal and then CONTINUED, E3.)
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

CENSUS_BEFORE=$(_s0_01_census)

for unit in "${UNITS[@]}"; do
  exe_pin=${UNIT_EXE[$unit]:-}
  if [ -z "$exe_pin" ]; then
    RESULT[$unit]="not-run|no allowed destination configured for $unit (not a unit this runner launches)"
    echo "SKIP $unit: no allowed destination configured" >&2
    continue
  fi
  ns="s0-05-$unit"
  # A1: the pinned unit is on disk as pinned (for the pair, the agent it launches too).
  mismatch=""
  if [ "$unit" = hermes-acp ]; then
    _pin_ok "${PIN[PINNED_AGENT_REALPATH]}" "${PIN[PINNED_AGENT_ENTRYPOINT_SHA256]}" \
      || mismatch=${PIN[PINNED_AGENT_REALPATH]}
  else
    if ! _pin_ok "${PIN[PINNED_BUZZ_ACP_EXE_REALPATH]}" "${PIN[PINNED_BUZZ_ACP_SHA256]}"; then
      mismatch=${PIN[PINNED_BUZZ_ACP_EXE_REALPATH]}
    elif ! _pin_ok "${PIN[PINNED_AGENT_REALPATH]}" "${PIN[PINNED_AGENT_ENTRYPOINT_SHA256]}"; then
      mismatch=${PIN[PINNED_AGENT_REALPATH]}
    fi
  fi
  if [ -n "$mismatch" ]; then
    RESULT[$unit]="not-run|unit identity mismatch: $mismatch"; echo "SKIP $unit: unit identity mismatch: $mismatch" >&2
    continue
  fi
  # A4: never as root.
  if [ -z "$UNIT_UID" ]; then
    RESULT[$unit]="not-run|unit user unresolved (set S0_05_UNIT_USER)"; echo "SKIP $unit: unit user unresolved" >&2
    continue
  fi
  if [ "$UNIT_UID" = 0 ]; then
    RESULT[$unit]="not-run|unit would run as root"; echo "SKIP $unit: unit would run as root" >&2
    continue
  fi
  # A6: the pair's S0-05 identity.
  if [ "$unit" = buzz-acp ] && ! _pair_identity; then
    RESULT[$unit]="not-run|identity file refused: $ID_REFUSED"; echo "SKIP $unit: identity file refused: $ID_REFUSED" >&2
    continue
  fi
  # A8: every allow entry is formed here, from the namespace's veth host address and a port input
  # (never word-split: a malformed port reaches egress_ns_create whole and is refused by name).
  # The pair's allow-set is exactly {relay, OmniRoute} (D-051); its agent is its own child.
  # R1 (E3-b): each entry carries its service's probe path (probe_paths[i] for allowed[i]);
  # egress_ns_create still gets the ip:port entries alone, never a path.
  host_ip=$(egress_ns_host_ip "$ns")
  allowed=("$host_ip:$OMNI_PORT"); probe_paths=("$OMNI_PROBE_PATH")
  [ "$unit" = buzz-acp ] && { allowed=("$host_ip:${PIN[RELAY_PORT]}" "$host_ip:$OMNI_PORT")
                              probe_paths=("$RELAY_PROBE_PATH" "$OMNI_PROBE_PATH"); }
  echo "=== $unit: namespace $ns, allowed ${allowed[*]} ==="
  # X2: the name enters the reap set BEFORE create runs, and stays there when create fails, so a
  # leftover that create could not roll back (its shell killed mid-way) is still reaped by
  # `cleanup` at exit — under the F3 ownership check, i.e. only while its owner record is $$. A
  # refused create (a live sibling's name) is therefore safe here: its record names the sibling.
  NS_LIVE="${NS_LIVE:+$NS_LIVE }$ns"
  # F23: capture refusal text from egress_ns_create.
  create_err=$(egress_ns_create "$ns" "${allowed[@]}" 2>&1 >/dev/null)
  if [ $? -ne 0 ]; then
    RESULT[$unit]="not-run|${create_err:-namespace creation failed}"
    echo "SKIP $unit: ${create_err:-namespace creation failed}" >&2
    continue
  fi
  # D-051: the pair reaches the pinned relay through ONE DNAT on its veth host end, for this leg only.
  if [ "$unit" = buzz-acp ]; then
    reach_err=$(egress_relay_reach_add "$ns" "${PIN[RELAY_PORT]}" "${PIN[RELAY_HOST]}:${PIN[RELAY_PORT]}" 2>&1 >/dev/null)
    if [ $? -ne 0 ]; then
      RESULT[$unit]="not-run|relay reach not established: ${reach_err:-no detail}"
      echo "SKIP $unit: relay reach not established: ${reach_err:-no detail}" >&2
      egress_ns_destroy "$ns"; NS_LIVE=${NS_LIVE//$ns/}; NS_LIVE=${NS_LIVE# }; continue
    fi
  fi

  # PREFLIGHT the exact predicate the proof consumes (AF-AP-24), before launching anything: for EVERY
  # allowed destination, in order, the collector's own C0 request graded by the checker's own predicate
  # (_c0_preflight, R2). No HTTP answer keeps the `unreachable` texts; an HTTP answer outside 2xx is
  # `not-2xx`, named with the path it asked.
  verdict=ok
  for i in "${!allowed[@]}"; do
    entry=${allowed[$i]}; probe=$entry${probe_paths[$i]}
    verdict=$(_c0_preflight "$ns" "$unit" "$entry" "${probe_paths[$i]}")
    [ "$verdict" = ok ] || break
  done
  if [ "$verdict" != ok ]; then
    case $verdict in
      "not-2xx "*)
        echo "positive-control-not-2xx: $unit $probe HTTP ${verdict#not-2xx }" >&2
        RESULT[$unit]="not-run|positive control not 2xx: $probe answered HTTP ${verdict#not-2xx } from $ns";;
      *)
        echo "positive-control-unreachable: $unit $entry" >&2
        echo "  the service is not reachable from inside the namespace. Fix it, do not stub it: listen on" >&2
        echo "  $(egress_ns_host_ip "$ns") (the veth host address) or 0.0.0.0; the relay's reach is D-051's DNAT." >&2
        RESULT[$unit]="not-run|positive control unreachable: $entry not reachable from $ns";;
    esac
    egress_ns_destroy "$ns"; NS_LIVE=${NS_LIVE//$ns/}; NS_LIVE=${NS_LIVE# }; continue
  fi

  # A2: the unit's own scratch tree under the evidence root, owned by the unit user: its HOME and
  # HERMES_HOME (the Hermes unit writes eleven entries there at startup, CD1 probe 2).
  scratch="$EVIDENCE_ROOT/$unit/scratch"
  mkdir -p "$scratch/home" "$scratch/hermes-home" \
    && chown "$UNIT_UID:$UNIT_GID" "$scratch/home" "$scratch/hermes-home" \
    && chmod 0700 "$scratch/home" "$scratch/hermes-home"
  if ! "$SETPRIV_BIN" --reuid="$UNIT_UID" --regid="$UNIT_GID" --clear-groups \
        test -w "$scratch/home" -a -w "$scratch/hermes-home"; then
    RESULT[$unit]="not-run|unit scratch tree not writable by uid $UNIT_UID: $scratch"
    echo "SKIP $unit: unit scratch tree not writable by uid $UNIT_UID: $scratch" >&2
    egress_ns_destroy "$ns"; NS_LIVE=${NS_LIVE//$ns/}; NS_LIVE=${NS_LIVE# }; continue
  fi

  # A3: stdin is a pipe the runner holds open for the canary window; stdout+stderr are a pipe whose
  # reader writes the unit log. Never /dev/null, never a regular file: either makes the ACP adapter
  # crash at startup (CD1 probe 2). The runner opens the stdin pipe read-write, so no open blocks.
  fifo_dir=$(mktemp -d); FIFO_DIRS="$FIFO_DIRS $fifo_dir"
  mkfifo -m 0600 "$fifo_dir/in" "$fifo_dir/out"
  exec {unit_in}<>"$fifo_dir/in"
  cat <"$fifo_dir/out" >"$EVIDENCE_ROOT/$unit.launch.log" {unit_in}>&- &
  log_pid=$!; LOG_PIDS="$LOG_PIDS $log_pid"
  # A4 + A5: dropped to the unit user INSIDE the namespace, with an environment built from nothing:
  # PATH (pinned), HOME and HERMES_HOME (the scratch tree), the locale, and PYTHONDONTWRITEBYTECODE
  # (the CD1 probes' own recipe: the agent must never write bytecode into S0-01's pinned tree). The
  # pair's identity reaches ITS environment through fd 3 and a tiny exec shim, never through an argv.
  # Every exec keeps the pid, so $! IS the unit.
  unit_env=(PATH="${PIN[PINNED_PATH]}" HOME="$scratch/home" HERMES_HOME="$scratch/hermes-home"
            LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1)
  if [ "$unit" = hermes-acp ]; then
    ( cd "$scratch/home" && exec "$ENV_BIN" -i "${unit_env[@]}" "$IP_BIN" netns exec "$ns" \
        "$SETPRIV_BIN" --reuid="$UNIT_UID" --regid="$UNIT_GID" --init-groups -- "${PIN[$exe_pin]}"
    ) <"$fifo_dir/in" >"$fifo_dir/out" 2>&1 {unit_in}>&- &
  else
    # shellcheck disable=SC2016
    ( cd "$scratch/home" && exec "$ENV_BIN" -i "${unit_env[@]}" "$IP_BIN" netns exec "$ns" \
        "$SETPRIV_BIN" --reuid="$UNIT_UID" --regid="$UNIT_GID" --init-groups -- "$PY_BIN" -I -c \
        'import os, sys; key = os.read(3, 65536).decode().rstrip("\n"); os.close(3); os.environ["BUZZ_PRIVATE_KEY"] = key; os.execv(sys.argv[1], sys.argv[1:])' \
        "${PAIR_ARGV[@]}" 3<<<"$PAIR_KEY"
    ) <"$fifo_dir/in" >"$fifo_dir/out" 2>&1 {unit_in}>&- &
  fi
  launch_pid=$!
  # Failure-aware wait: the exit condition includes the FAILURE signature (the process is
  # gone), so the loop stops the moment the unit dies instead of sleeping through it. A blind
  # `sleep N` accepts a unit that died in second 1 and cannot notice one that dies in second
  # N+1 (18-class sweep, class 9). It waits for liveness only.
  for _ in $(seq 1 30); do
    kill -0 "$launch_pid" 2>/dev/null || break     # died: stop waiting, do not burn the window
    sleep 1
  done
  if ! kill -0 "$launch_pid" 2>/dev/null; then
    RESULT[$unit]="not-run|launch exited within the settle window; see $EVIDENCE_ROOT/$unit.launch.log"
    _leg_teardown; continue
  fi
  # A7: the canaries run only if the process in the namespace is the pinned unit, as the unit user.
  if [ "$unit" = hermes-acp ]; then
    identity=$(_unit_identity "$launch_pid" "$unit" agent "${PIN[PINNED_AGENT_INTERPRETER_REALPATH]}" \
      "${PIN[PINNED_AGENT_REALPATH]}" "${PIN[PINNED_AGENT_ENTRYPOINT_SHA256]}")
  else
    identity=$(_unit_identity "$launch_pid" "$unit" binary "${PIN[PINNED_BUZZ_ACP_EXE_REALPATH]}" \
      "${PIN[PINNED_BUZZ_ACP_EXE_REALPATH]}" "${PIN[PINNED_BUZZ_ACP_SHA256]}")
  fi
  if [ "$identity" != ok ]; then
    RESULT[$unit]="not-run|unit identity not observed: $identity"
    echo "SKIP $unit: unit identity not observed: $identity" >&2
    _leg_teardown; continue
  fi

  # R3 (E3-b): the collector gets the unit's WHOLE entry list, comma-joined in this runner's order (the
  # pair: relay, then OmniRoute), each entry with its probe path (R1): its gate.json records every
  # allowed ip:port, so the rule pin can hold for the pair (E3 section 9), and C0 asks what R2 asked.
  entries=""
  for i in "${!allowed[@]}"; do entries="${entries:+$entries,}${allowed[$i]}${probe_paths[$i]}"; done
  bash "$P/run_canaries.sh" "$unit" "$ns" "$entries" "$EVIDENCE_ROOT" "" pc
  RESULT[$unit]="run|contained live unit"

  # A3 + F9: the stop is closing stdin (the adapter exits 0 at EOF, CD1 probe 3); the namespace
  # destroy in the teardown is the backstop, never `kill "$launch_pid"`.
  exec {unit_in}>&-; unit_in=""
  stopped=""
  for _ in $(seq 1 50); do kill -0 "$launch_pid" 2>/dev/null || { stopped=yes; break; }; sleep 0.2; done
  if [ -n "$stopped" ]; then
    wait "$launch_pid"; echo "=== $unit: exited $? on stdin EOF ==="
  else
    echo "=== $unit: still running 10 s after stdin EOF; namespace destroy is the backstop ==="
  fi
  _leg_teardown
done

# A2: the census after the last unit; anything changed in S0-01's tree fails the leg.
census_changed=$(python3 -B - "$CENSUS_BEFORE" "$(_s0_01_census)" "$EVIDENCE_ROOT/s0-01-census.json" <<'PY'
import json, sys
before, after = json.loads(sys.argv[1]), json.loads(sys.argv[2])
b, a = before["entries"], after["entries"]
changed = sorted(p for p in set(b) | set(a) if b.get(p) != a.get(p))
with open(sys.argv[3], "w") as fh:
    json.dump({"base": before["base"], "before": b, "after": a, "changed": changed,
               "tree": "present" if (b or a) else "absent on this venue (recorded, not failed)"},
              fh, indent=2, sort_keys=True)
    fh.write("\n")
for path in changed:
    print(path)
PY
)

# F4: units.json encoded through python3 json.dumps, never printf with raw strings.
# Every unit the plan names, run or NOT, with its reason; A1: the recorded override on every unit row.
_json_tmp=$(mktemp)
for unit in "${!RESULT[@]}"; do
  st=${RESULT[$unit]%%|*}; why=${RESULT[$unit]#*|}
  printf '%s\0%s\0%s\0%s\0' unit "$st" "$unit" "$why" >> "$_json_tmp"
done
for unit in "${!ABSENT[@]}"; do
  printf '%s\0%s\0%s\0%s\0' absent "not-run" "$unit" "${ABSENT[$unit]}" >> "$_json_tmp"
done
python3 -c '
import json, sys
data = open(sys.argv[1], "rb").read()
override = json.loads(sys.argv[2]) if sys.argv[2] else None
fields = data.split(b"\x00")
units = []
i = 0
while i + 3 < len(fields):
    kind = fields[i].decode()
    st = fields[i+1].decode(); unit = fields[i+2].decode(); detail = fields[i+3].decode()
    if st == "run":
        row = {"unit": unit, "status": "run", "note": detail}
    else:
        row = {"unit": unit, "status": "not-run", "reason": detail}
    if kind == "unit" and override is not None:
        row["override"] = override
    units.append(row)
    i += 4
json.dump({"units": units}, sys.stdout, indent=2)
print()
' "$_json_tmp" "${PIN[OVERRIDE]}" > "$EVIDENCE_ROOT/units.json"
rm -f "$_json_tmp"

echo "=== units.json ==="; cat "$EVIDENCE_ROOT/units.json"
if [ -n "$census_changed" ]; then
  while IFS= read -r path; do echo "s0-01-tree-changed: $path" >&2; done <<< "$census_changed"
  echo "=== S0-01's tree changed during the leg: the leg FAILS (census: $EVIDENCE_ROOT/s0-01-census.json) ===" >&2
  exit 1
fi
echo "=== checker ==="
python3 -B "$P/check_egress.py" "$EVIDENCE_ROOT" --units "$(IFS=,; echo "${UNITS[*]}")"
