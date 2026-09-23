#!/usr/bin/env bash
# netns_lib.sh — the S0-05 selective-egress mechanism as a sourceable library.
#
# LIFTED from the Wave-0 spike `spikes/selective-egress/probe.sh` (POSITIVE, 2026-09-04); the
# per-function provenance is cited on each function. Nothing here re-derives the mechanism: the
# topology, the address plan and the rule set are the spike's, parameterised by namespace name
# and allow-list so several units can be contained at once.
#
#   Host netns:  <host-if>  10.201.<oct>.1/24  — the allowed endpoint lives here
#   Unit netns:  <ns-if>    10.201.<oct>.2/24  — iptables: policy DROP + an ACCEPT per allowed
#                                                 ip:port and for loopback
#
# NOT bare `unshare --net` (AF-AP-1 in docs/INCIDENT-LOG.md): total isolation blocks the
# positive control too, so it can never be evidence for S0-05. `fixtures/evidence-bare-unshare/`
# is the committed control for that class.
#
# API
#   egress_allow_entry_ok <entry>        G: the ONE allow-entry rule, a silent predicate (0 valid)
#   egress_ns_create <ns> <ip:port>...   idempotent; claims the name, creates the ns, the veth
#                                        pair, the rules; a failed step rolls all of it back (X2)
#   egress_ns_run <ns> <cmd...>          run a command as the contained unit
#   egress_ns_destroy <ns>               remove the relay reach, every process in the ns, the veth,
#                                        the ns, the per-ns resolv.conf and the owner record
#   egress_relay_reach_add <ns> <port> <ip:port> / egress_relay_reach_del <ns>
#                                        D-051: the pair's one DNAT to the loopback relay
#   egress_gate_off <ns> [gate.json]     THE negative control: flush the DROP rules and stamp
#                                        "gate": "disabled" into the run's gate.json
#   egress_ns_create_isolated <ns> <ip:port>...
#                                        the AF-AP-1 CONTROL: the same gate with NO veth, i.e.
#                                        total isolation — the positive control cannot pass
#   egress_ns_gate_state <ns>            "enabled" (OUTPUT policy DROP) | "disabled" (ACCEPT)
#   egress_ns_mechanism <ns>             "veth-iptables" | "netns-no-veth" (observed, not claimed)
#   egress_ns_rules <ns>                 canonical (sorted) `iptables -S` of the ns
#   egress_ns_rules_sha256 <ns>          sha256 over the canonical rules
#   egress_ns_drop_counter <ns>          packets dropped by the OUTPUT policy (the gate firing)
#   egress_ns_host_ip <ns> / egress_ns_host_if <ns> / egress_ns_if <ns>
#
# Every function needs root and iproute2 + iptables (`egress_ns_capable` reports; the callers
# defer rather than fail-open).  Bash 4+; `set -u` safe.

# --- derivation: one deterministic address plan + interface pair per namespace name ----------
# Interface names must fit IFNAMSIZ (15 usable chars); the netns name does not, so both are
# derived from a hash of it.
_egress_hash() { printf '%s' "$1" | sha256sum | cut -c1-8; }

egress_ns_host_if() { printf 'eh%s\n' "$(_egress_hash "$1")"; }
egress_ns_if()      { printf 'en%s\n' "$(_egress_hash "$1")"; }

_egress_octet() {
  # 1..254 from the hash: the third octet of the /24 this namespace owns.
  local n; n=$((0x$(printf '%s' "$1" | sha256sum | cut -c1-2)))
  printf '%d\n' $(( n % 254 + 1 ))
}
egress_ns_host_ip() { printf '10.201.%s.1\n' "$(_egress_octet "$1")"; }
egress_ns_ip()      { printf '10.201.%s.2\n' "$(_egress_octet "$1")"; }
# The blackhole resolver: inside the namespace's own /24, no listener, never allow-listed, so a
# DNS query is dropped by the gate itself rather than failing for want of a configured resolver
# (the spike's `not_verified` item "DNS resolution inside the netns (no resolver configured)").
egress_ns_resolver() { printf '10.201.%s.53\n' "$(_egress_octet "$1")"; }

egress_ns_capable() {
  [ "$(id -u)" = "0" ] || { echo "not-root"; return 1; }
  command -v ip >/dev/null 2>&1 || { echo "no-iproute2"; return 1; }
  command -v iptables >/dev/null 2>&1 || { echo "no-iptables"; return 1; }
  echo "ok"
}

# --- the allow-entry rule (G) ------------------------------------------------------------------
# ONE rule for an allow entry, held in three places: here, run_canaries.sh (which calls this) and
# check_egress.py's _split_ip_port (the same set; a parity test drives one table through both). A
# dotted quad of four decimal octets 0-255 with no leading zero (a lone 0 is fine), then a port
# 1-65535 with no leading zero. X1 (VERIFY-E2-R1 F1, AF-AP-129): the port's DIGIT COUNT is bounded
# before the arithmetic — five digits cannot overflow, while a longer string made `[ -gt ]` exit 2,
# which `||` read as false; and `[` parses a number, where `[[ -gt ]]` would EVALUATE an expression.
# ASCII-only under any locale: every class is an explicit list, never a range a locale may widen.
# SILENT: no output; status 0 valid, 1 not.
egress_allow_entry_ok() {
  local entry=${1-} d='[0123456789]' nz='[123456789]' octet ip port
  octet="(0|${nz}${d}?|1${d}${d}|2[01234]${d}|25[012345])"
  local ip_re="^${octet}\\.${octet}\\.${octet}\\.${octet}\$" port_re="^${nz}${d}{0,4}\$"
  ip=${entry%:*}; port=${entry##*:}
  [[ "$port" =~ $port_re ]] && [ "$port" -le 65535 ] && [[ "$ip" =~ $ip_re ]]
}

# --- create ----------------------------------------------------------------------------------
# probe.sh:39-58 verbatim in shape: netns add, veth pair, peer into the ns, addresses, links up,
# policy DROP on INPUT/OUTPUT/FORWARD, an ACCEPT pair per allowed ip:port, loopback ACCEPT.
egress_ns_create() {
  local ns=$1; shift
  [ -n "$ns" ] || { echo "egress_ns_create: namespace name required" >&2; return 64; }
  [ "$#" -ge 1 ] || { echo "egress_ns_create: at least one <ip:port> allow entry required" >&2; return 64; }

  # F11/F12 + X1: validate EVERY allow entry up front, before any namespace/veth/rule/record work,
  # by the one allow-entry rule (egress_allow_entry_ok, above).
  local entry
  for entry in "$@"; do
    egress_allow_entry_ok "$entry" || { echo "egress: allow entry must be <ip>:<port>, got '$entry'" >&2; return 64; }
  done

  local host_if ns_if host_ip ns_ip resolver
  host_if=$(egress_ns_host_if "$ns"); ns_if=$(egress_ns_if "$ns")
  host_ip=$(egress_ns_host_ip "$ns"); ns_ip=$(egress_ns_ip "$ns")
  resolver=$(egress_ns_resolver "$ns")

  # F2 + X3: claim the name BEFORE destroy-first and creation (_egress_ns_claim, below). A claim
  # held by a live pid other than $$ is refused (65); a stale one (dead pid) is taken over atomically.
  _egress_ns_claim "$ns" || return $?

  # idempotent (probe.sh:36-37): remove any remains of a previous run of THIS namespace.
  # F2: use _egress_ns_teardown (not egress_ns_destroy) so our fresh claim is preserved.
  _egress_ns_teardown "$ns"

  # F6: refuse when the /24 this name derives is already assigned to any host interface after
  # the destroy-first step.
  local octet subnet collision_if
  octet=$(_egress_octet "$ns"); subnet="10.201.${octet}.0/24"
  collision_if=$(ip -o -4 addr show 2>/dev/null \
    | awk -v pfx="10.201.${octet}." 'index($4, pfx) == 1 {print $2; exit}')
  if [ -n "$collision_if" ]; then
    _egress_ns_release "$ns"
    echo "address-plan-collision: $ns $subnet on $collision_if" >&2; return 65
  fi

  # X2: from the first namespace mutation on, a step that fails rolls back EVERYTHING this create
  # made (namespace, veth, /etc/netns/<ns>, gate) and then the claim, and returns 1; the failing
  # command's own message is already on stderr.
  ip netns add "$ns" || { _egress_ns_rollback "$ns"; return 1; }
  ip link add "$host_if" type veth peer name "$ns_if" || { _egress_ns_rollback "$ns"; return 1; }
  ip link set "$ns_if" netns "$ns" || { _egress_ns_rollback "$ns"; return 1; }
  ip addr add "${host_ip}/24" dev "$host_if" || { _egress_ns_rollback "$ns"; return 1; }
  ip link set "$host_if" up || { _egress_ns_rollback "$ns"; return 1; }
  ip netns exec "$ns" ip addr add "${ns_ip}/24" dev "$ns_if" || { _egress_ns_rollback "$ns"; return 1; }
  ip netns exec "$ns" ip link set "$ns_if" up || { _egress_ns_rollback "$ns"; return 1; }
  ip netns exec "$ns" ip link set lo up || { _egress_ns_rollback "$ns"; return 1; }

  # No default route is added: the namespace reaches its own /24 and nothing else. Targets off
  # that /24 therefore fail on ROUTING (ENETUNREACH), targets on it fail on the GATE. Both are
  # recorded per canary; the report says which barrier each canary hit.

  # DNS blocked (docs/05_SECURITY.md:21 "DNS/connection canaries"): a resolver the gate drops.
  mkdir -p "/etc/netns/$ns" || { _egress_ns_rollback "$ns"; return 1; }
  printf 'nameserver %s\noptions timeout:1 attempts:1\n' "$resolver" > "/etc/netns/$ns/resolv.conf" \
    || { _egress_ns_rollback "$ns"; return 1; }

  _egress_apply_gate "$ns" "$@" || { _egress_ns_rollback "$ns"; return 1; }
}

# --- the claim (X3, VERIFY-E2-R1 F4) ---------------------------------------------------------
# The claim IS the owner record `<ns>.owner`, installed atomically WITH its content: link(2) of a
# fully written temp file fails when a record exists and never shows a half-written one, so there
# is no window in which a claim exists with no owner, or with a stale owner (E2-R1's mkdir of a
# claim dir, then a write of the record, had both). A record whose pid is dead is taken over by an
# atomic rename of THAT record to a unique tombstone, then the normal link claim. Of two creators
# that read the same stale record, only one rename can move it; a later rename that finds a live
# record instead (the winner's, installed after the stale read) moves it straight back with a
# link, which never overwrites, and that creator is then refused naming the winner. State guards
# only: no lock is held, least of all across destroy-and-recreate. Declared limit: a THIRD
# creator that links a fresh claim inside the microseconds between such a rename and its move
# back can orphan the winner's record; three creators on one name at once is out of this model.
# Returns 0 holding the claim; 65 with the `namespace-live` line when a live pid other than $$
# holds it; 1 when the record cannot be written at all.
_egress_ns_claim() {
  local ns=$1 owner_file tmp tomb owner_pid moved attempt
  owner_file=$(egress_ns_owner_file "$ns")
  mkdir -p "$EGRESS_OWNER_DIR" || return 1
  tmp="$EGRESS_OWNER_DIR/.$ns.owner.$$.$RANDOM"
  printf '%s\n' "$$" > "$tmp" || { rm -f "$tmp"; return 1; }
  for attempt in 1 2 3 4 5 6 7 8 9 10; do
    if ln "$tmp" "$owner_file" 2>/dev/null; then rm -f "$tmp"; return 0; fi
    owner_pid=$(cat "$owner_file" 2>/dev/null)
    if [ "$owner_pid" = "$$" ]; then rm -f "$tmp"; return 0; fi   # the same shell re-creating
    if [[ "$owner_pid" =~ ^[1-9][0-9]{0,9}$ ]] && kill -0 "$owner_pid" 2>/dev/null; then
      rm -f "$tmp"; echo "namespace-live: $ns owned by pid $owner_pid" >&2; return 65
    fi
    # stale (a dead or unreadable pid): move exactly the record that was read, never overwrite it
    tomb="$EGRESS_OWNER_DIR/.$ns.tomb.$$.$RANDOM"
    if mv -T "$owner_file" "$tomb" 2>/dev/null; then
      moved=$(cat "$tomb" 2>/dev/null)
      [ "$moved" = "$owner_pid" ] || ln "$tomb" "$owner_file" 2>/dev/null
      rm -f "$tomb"
    fi
  done
  rm -f "$tmp"
  echo "namespace-live: $ns owned by pid $(cat "$owner_file" 2>/dev/null) (claim churn after $attempt attempts)" >&2
  return 65
}

# X2: undo a failed create. The claim goes only when the teardown left nothing alive behind, so
# a leftover the rollback could not remove stays owned by $$: the runner's cleanup reaps a name
# only while its owner record is the runner's pid (E2-R1 F3), and that record is still here.
_egress_ns_rollback() { _egress_ns_teardown "$1" && _egress_ns_release "$1"; }

# Drop the claim: the owner record, and the E2-R1 claim dir a pre-X3 library may have left.
_egress_ns_release() {
  rm -f "$(egress_ns_owner_file "$1")"
  rm -rf "$EGRESS_OWNER_DIR/${1}.claim"
}

# probe.sh:50-58: policy DROP on the three chains, one ACCEPT pair per allowed ip:port, loopback
# ACCEPT. check_egress.py derives the SAME set from the declared allow-list and compares digests,
# so this function and the checker's `expected_rules` are the two halves of one pinned contract.
_egress_apply_gate() {
  local ns=$1; shift
  local chain entry ip port
  for chain in INPUT OUTPUT FORWARD; do
    ip netns exec "$ns" iptables -P "$chain" DROP || return 1
  done
  for entry in "$@"; do
    ip=${entry%:*}; port=${entry##*:}
    # F19: validation is done up front in egress_ns_create before any state is touched.
    ip netns exec "$ns" iptables -A OUTPUT -d "$ip" -p tcp --dport "$port" -j ACCEPT || return 1
    ip netns exec "$ns" iptables -A INPUT  -s "$ip" -p tcp --sport "$port" -j ACCEPT || return 1
  done
  ip netns exec "$ns" iptables -A OUTPUT -o lo -j ACCEPT || return 1
  ip netns exec "$ns" iptables -A INPUT  -i lo -j ACCEPT || return 1
}

# --- the AF-AP-1 control ---------------------------------------------------------------------
# The same namespace and the same gate, with NO veth pair: the class bare `unshare --net`
# belongs to (findings §6a, docs/research/FINDINGS-STAGE0-v1.md:98-108). The unit is totally
# isolated, so its POSITIVE control cannot pass and the bundle can never be S0-05 evidence.
# Committed as `fixtures/evidence-bare-unshare/`.
egress_ns_create_isolated() {
  local ns=$1; shift
  [ -n "$ns" ] || { echo "egress_ns_create_isolated: namespace name required" >&2; return 64; }
  [ "$#" -ge 1 ] || { echo "egress_ns_create_isolated: at least one <ip:port> allow entry required" >&2; return 64; }
  egress_ns_destroy "$ns"
  ip netns add "$ns" || return 1
  ip netns exec "$ns" ip link set lo up || return 1
  mkdir -p "/etc/netns/$ns"
  printf 'nameserver %s\noptions timeout:1 attempts:1\n' "$(egress_ns_resolver "$ns")" > "/etc/netns/$ns/resolv.conf"
  _egress_apply_gate "$ns" "$@"
}

# --- run / inspect ---------------------------------------------------------------------------
# The gate's state is OBSERVED from the namespace's own OUTPUT policy, never asserted by whoever
# writes the evidence: `egress_gate_off` flips the policy to ACCEPT, so a bundle collected after
# the mutation records "disabled" whether or not the collector meant to say so.
egress_ns_gate_state() {
  case "$(ip netns exec "$1" iptables -S OUTPUT | sed -n '1p')" in
    "-P OUTPUT DROP") echo enabled;;
    *) echo disabled;;
  esac
}

# Which shape this namespace actually has, read from the namespace: a veth peer present means
# selective egress; its absence means total isolation (the AF-AP-1 class).
egress_ns_mechanism() {
  if ip netns exec "$1" ip -o link show "$(egress_ns_if "$1")" >/dev/null 2>&1; then
    echo veth-iptables
  else
    echo netns-no-veth
  fi
}

egress_ns_run() { local ns=$1; shift; ip netns exec "$ns" "$@"; }

egress_ns_rules() { ip netns exec "$1" iptables -S | sed 's/[[:space:]]\+/ /g; s/[[:space:]]*$//' | LC_ALL=C sort; }

egress_ns_rules_sha256() { egress_ns_rules "$1" | sha256sum | cut -d' ' -f1; }

# The OUTPUT policy's packet counter: proof that the gate ACTUALLY dropped traffic during the
# run. A suite whose canaries all failed for other reasons leaves this at zero.
# A DROP policy reports its packet count; an ACCEPT policy (the gate switched OFF) drops nothing
# by policy and reports 0. Only a chain that cannot be read at all prints NOTHING, and the
# collector treats that empty string as a broken instrument and refuses to write a bundle.
# Bit 2026-09-08: reading only the DROP form made `run_canaries.sh` exit 3 on every gate-OFF
# collection and leave an empty fixture behind.
egress_ns_drop_counter() {
  ip netns exec "$1" iptables -L OUTPUT -v -n -x 2>/dev/null | sed -n \
    -e '1s/.*policy DROP \([0-9]\+\) packets.*/\1/p' \
    -e '1s/.*policy ACCEPT [0-9]\+ packets.*/0/p'
}

# --- the negative control --------------------------------------------------------------------
# probe.sh:113-116: flush the chains and set the policies to ACCEPT — the gate, and only the
# gate, is switched off. The run's gate.json is stamped so the checker sees a disabled gate
# BEFORE it looks at any canary.
egress_gate_off() {
  local ns=$1 gate_json=${2:-}
  local chain
  for chain in INPUT OUTPUT FORWARD; do
    ip netns exec "$ns" iptables -F "$chain" || return 1
    ip netns exec "$ns" iptables -P "$chain" ACCEPT || return 1
  done
  [ -n "$gate_json" ] || return 0
  python3 - "$gate_json" "$(egress_ns_rules_sha256 "$ns")" <<'PY'
import json, sys
path, sha = sys.argv[1], sys.argv[2]
with open(path) as fh:
    gate = json.load(fh)
gate["gate"] = "disabled"
gate["rules_sha256"] = sha
with open(path, "w") as fh:
    json.dump(gate, fh, indent=2, sort_keys=True)
    fh.write("\n")
PY
}

# The F23 owner record lives OUTSIDE /etc/netns/<ns>/: `ip netns exec` bind-mounts every file in
# that directory over /etc inside the namespace, so an `owner` file there made every exec print
# `Bind /etc/netns/<ns>/owner -> /etc/owner failed` (the E2 landing, 2026-09-23).
EGRESS_OWNER_DIR=${EGRESS_OWNER_DIR:-/run/s0-05-egress}
egress_ns_owner_file() { printf '%s/%s.owner\n' "$EGRESS_OWNER_DIR" "$1"; }

# --- D-051: the relay reach (the buzz-acp pair's leg only) ------------------------------------
# The pinned relay listens on 127.0.0.1 only, and a namespace has its own loopback. For the pair's
# leg the ROOT runner adds ONE host nat rule on the pair's veth host end — tcp to <host ip>:<port>
# is DNAT-ed to the relay — and sets route_localnet=1 on that ONE interface (the kernel will not
# route a loopback destination arriving on any other interface). No service is touched, rebound or
# restarted. Every teardown removes the reach while the interface still exists: a nat rule naming a
# deleted interface outlives it.
#   egress_relay_reach_add <ns> <port> <dest ip:port>
#   egress_relay_reach_del <ns>      every nat PREROUTING rule naming <ns>'s host interface, and
#                                    route_localnet back to 0 while the interface exists
egress_relay_reach_add() {
  local ns=$1 port=$2 dest=$3 host_if host_ip
  host_if=$(egress_ns_host_if "$ns"); host_ip=$(egress_ns_host_ip "$ns")
  sysctl -q -w "net.ipv4.conf.${host_if}.route_localnet=1" || return 1
  iptables -t nat -A PREROUTING -i "$host_if" -p tcp -d "$host_ip" --dport "$port" \
    -j DNAT --to-destination "$dest" || { egress_relay_reach_del "$ns"; return 1; }
}

egress_relay_reach_del() {
  local ns=$1 host_if rule spec removed=0
  host_if=$(egress_ns_host_if "$ns")
  # by the rule's own spec, one at a time, bounded (a rule that will not delete fails loud)
  while rule=$(iptables -t nat -S PREROUTING 2>/dev/null | grep -m1 -F -- " -i $host_if "); [ -n "$rule" ]; do
    read -r -a spec <<< "${rule#-A }"
    iptables -t nat -D "${spec[@]}" || return 1
    removed=$((removed + 1)); [ "$removed" -lt 16 ] || return 1
  done
  if [ -e "/proc/sys/net/ipv4/conf/$host_if" ]; then
    sysctl -q -w "net.ipv4.conf.${host_if}.route_localnet=0" || return 1
  fi
}

# --- destroy ---------------------------------------------------------------------------------
# probe.sh:26-32 (the trap body), by name, never by pattern.
# F7: kill every process in the namespace BEFORE deleting the veth and the netns.
# F1: SIGTERM first, then SIGKILL survivors; fail loud if any remain.
#
# _egress_ns_teardown: the resource cleanup (relay reach, processes, veth, netns, /etc/netns)
# without touching the ownership claim. Used by create's destroy-first step so it doesn't wipe its
# own fresh claim.
_egress_ns_teardown() {
  local ns=$1 host_if pid rc=0
  host_if=$(egress_ns_host_if "$ns")
  # D-051: the relay reach goes first, explicitly, while its interface still exists.
  egress_relay_reach_del "$ns" || { echo "egress: relay reach of $ns not removed" >&2; rc=1; }
  # SIGTERM every process still inside the namespace.
  for pid in $(ip netns pids "$ns" 2>/dev/null); do
    kill "$pid" 2>/dev/null
  done
  # Bounded, failure-aware wait: stop the moment all are gone or the budget is spent.
  local remaining=50  # 50 * 0.1s = 5s
  while [ $remaining -gt 0 ]; do
    local alive=0
    for pid in $(ip netns pids "$ns" 2>/dev/null); do
      kill -0 "$pid" 2>/dev/null && alive=1 && break
    done
    [ $alive -eq 0 ] && break
    sleep 0.1
    remaining=$((remaining - 1))
  done
  # F1: escalate to SIGKILL for any SIGTERM-ignoring survivors.
  local survivors=""
  for pid in $(ip netns pids "$ns" 2>/dev/null); do
    if kill -0 "$pid" 2>/dev/null; then
      kill -KILL "$pid" 2>/dev/null
      survivors="$survivors $pid"
    fi
  done
  if [ -n "$survivors" ]; then
    # Wait briefly for SIGKILL to take effect.
    local kwait=20  # 20 * 0.1s = 2s
    while [ $kwait -gt 0 ]; do
      local kalive=0
      for pid in $survivors; do
        kill -0 "$pid" 2>/dev/null && kalive=1 && break
      done
      [ $kalive -eq 0 ] && break
      sleep 0.1
      kwait=$((kwait - 1))
    done
    # Fail loud if any process is still alive after SIGKILL.
    local final_survivors=""
    for pid in $survivors; do
      kill -0 "$pid" 2>/dev/null && final_survivors="$final_survivors $pid"
    done
    if [ -n "$final_survivors" ]; then
      echo "egress: namespace $ns still has live pids:$final_survivors" >&2
      ip link del "$host_if" 2>/dev/null || true
      ip netns del "$ns" 2>/dev/null || true
      rm -rf "/etc/netns/$ns"
      return 1
    fi
  fi
  ip link del "$host_if" 2>/dev/null || true
  ip netns del "$ns" 2>/dev/null || true
  rm -rf "/etc/netns/$ns"
  return $rc
}

egress_ns_destroy() {
  _egress_ns_teardown "$1"
  local rc=$?
  _egress_ns_release "$1"
  return $rc
}
