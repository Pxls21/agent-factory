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
#   egress_ns_create <ns> <ip:port>...   idempotent; creates the ns, the veth pair, the rules
#   egress_ns_run <ns> <cmd...>          run a command as the contained unit
#   egress_ns_destroy <ns>               remove ns, veth and the per-ns resolv.conf
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

# --- create ----------------------------------------------------------------------------------
# probe.sh:39-58 verbatim in shape: netns add, veth pair, peer into the ns, addresses, links up,
# policy DROP on INPUT/OUTPUT/FORWARD, an ACCEPT pair per allowed ip:port, loopback ACCEPT.
egress_ns_create() {
  local ns=$1; shift
  [ -n "$ns" ] || { echo "egress_ns_create: namespace name required" >&2; return 64; }
  [ "$#" -ge 1 ] || { echo "egress_ns_create: at least one <ip:port> allow entry required" >&2; return 64; }
  local host_if ns_if host_ip ns_ip resolver
  host_if=$(egress_ns_host_if "$ns"); ns_if=$(egress_ns_if "$ns")
  host_ip=$(egress_ns_host_ip "$ns"); ns_ip=$(egress_ns_ip "$ns")
  resolver=$(egress_ns_resolver "$ns")

  # idempotent (probe.sh:36-37): remove any remains of a previous run of THIS namespace
  egress_ns_destroy "$ns"

  ip netns add "$ns" || return 1
  ip link add "$host_if" type veth peer name "$ns_if" || return 1
  ip link set "$ns_if" netns "$ns" || return 1
  ip addr add "${host_ip}/24" dev "$host_if" || return 1
  ip link set "$host_if" up || return 1
  ip netns exec "$ns" ip addr add "${ns_ip}/24" dev "$ns_if" || return 1
  ip netns exec "$ns" ip link set "$ns_if" up || return 1
  ip netns exec "$ns" ip link set lo up || return 1

  # No default route is added: the namespace reaches its own /24 and nothing else. Targets off
  # that /24 therefore fail on ROUTING (ENETUNREACH), targets on it fail on the GATE. Both are
  # recorded per canary; the report says which barrier each canary hit.

  # DNS blocked (docs/05_SECURITY.md:21 "DNS/connection canaries"): a resolver the gate drops.
  mkdir -p "/etc/netns/$ns"
  printf 'nameserver %s\noptions timeout:1 attempts:1\n' "$resolver" > "/etc/netns/$ns/resolv.conf"

  _egress_apply_gate "$ns" "$@"
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
    case "$ip:$port" in
      *:*[!0-9]*|*:) echo "egress: allow entry must be <ip>:<port>, got '$entry'" >&2; return 64;;
    esac
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

# --- destroy ---------------------------------------------------------------------------------
# probe.sh:26-32 (the trap body), by name, never by pattern.
egress_ns_destroy() {
  local ns=$1 host_if
  host_if=$(egress_ns_host_if "$ns")
  ip link del "$host_if" 2>/dev/null || true
  ip netns del "$ns" 2>/dev/null || true
  rm -rf "/etc/netns/$ns"
}
