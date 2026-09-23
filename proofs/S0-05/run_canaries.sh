#!/usr/bin/env bash
# run_canaries.sh — run the S0-05 canary suite INSIDE an already-created egress namespace, as
# one contained unit, and write that unit's evidence bundle.
#
#   run_canaries.sh <unit> <ns> <allowed> [evidence-root] [blocked ip:port] [venue]
#
#   <allowed>  the unit's WHOLE allow-set (E3-b A): comma-separated ENTRIES, each `<ip>:<port>`
#              optionally followed by the path its C0 asks (P: `/` and at most 63 characters of
#              [A-Za-z0-9._~/-]); an entry without a path asks /v1/models. No two entries share an
#              ip:port (the path is not part of identity). gate.json `allowed` records every ip:port,
#              in the given order, without paths; C0 runs once per entry, in that order.
#   [blocked]  C6's routable target that is NOT allow-listed: `<ip>:<port>`, never in the allowed
#              set; default <the namespace's host ip>:<the FIRST entry's port + 1>.
#
# The namespace's lifecycle belongs to the CALLER (egress_ns_create / egress_ns_destroy in a
# trap): this script only observes. It writes
#   <evidence-root>/<unit>/canaries.jsonl   one JSON line per canary observation
#   <evidence-root>/<unit>/gate.json        gate state + the pinned rule digest
#   <evidence-root>/<unit>/runtime.json     kernel, iptables, the exact rule list, DROP counters
# and prints the bundle path. It asserts NOTHING — check_egress.py is the oracle.
#
# Model hostnames are resolved OUTSIDE the namespace (the only place resolution can work) and
# the ADDRESSES are handed to the canaries, so C2/C3/C4 test reachability rather than
# resolution. A host that will not resolve is recorded `status: not-run` with its reason; the
# checker then DEFERS (exit 2) — a discriminator that could not run is never a pass (AF-AP-24).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=proofs/S0-05/netns_lib.sh
. "$HERE/netns_lib.sh"

UNIT=${1:?usage: run_canaries.sh <unit> <ns> <allowed ip:port[/path],...> [evidence-root] [blocked ip:port] [venue]}
NS=${2:?ns}
EVIDENCE_ROOT=${4:-"$HERE/evidence"}

# E3-b A: arguments 3, 5 and 6 are validated in that order; the first failure exits 64 with its
# text, BEFORE any arithmetic on an input, any namespace access, any directory or file and any
# canary. An ip:port passes the library's one allow-entry rule (egress_allow_entry_ok); a path
# passes P's, ASCII only under any locale (an explicit list, never a range a locale may widen).
refuse() { printf 'run_canaries: %s\n' "$1" >&2; exit 64; }
PROBE_PATH_RE='^/[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._~/-]{0,63}$'
ALLOWED=(); PROBE_PATHS=()
rest="${3-},"          # the appended comma keeps a leading, trailing or doubled one an EMPTY entry
while [ -n "$rest" ]; do
  entry=${rest%%,*}; rest=${rest#*,}
  ipport=${entry%%/*}; path=${entry#"$ipport"}
  if [ -z "$entry" ] || ! egress_allow_entry_ok "$ipport" || { [ -n "$path" ] && ! [[ "$path" =~ $PROBE_PATH_RE ]]; }; then
    refuse "allowed entry '$entry' is not <ip>:<port>[/<path>]"
  fi
  for seen in "${ALLOWED[@]}"; do [ "$seen" != "$ipport" ] || refuse "allowed entry '$ipport' is listed twice"; done
  ALLOWED+=("$ipport"); PROBE_PATHS+=("${path:-/v1/models}")
done
BLOCKED=${5-}
if [ -n "$BLOCKED" ]; then
  egress_allow_entry_ok "$BLOCKED" || refuse "blocked entry '$BLOCKED' is not <ip>:<port>"
else
  # Computed only now: the first entry's port is a validated 1-65535 with no leading zero.
  first_port=${ALLOWED[0]##*:}
  [ "$first_port" -lt 65535 ] || refuse "default blocked port 65536 is out of range; pass a blocked entry"
  BLOCKED="$(egress_ns_host_ip "$NS"):$((first_port + 1))"
fi
for seen in "${ALLOWED[@]}"; do [ "$seen" != "$BLOCKED" ] || refuse "blocked entry '$BLOCKED' is in the allowed set"; done
VENUE=${6:-}
# F11: venue is required and must be sandbox or pc.
case "$VENUE" in
  sandbox|pc) ;;
  *) echo "run_canaries: venue must be sandbox or pc, got '$VENUE'" >&2; exit 64;;
esac
RESOLVER=$(egress_ns_resolver "$NS")

MODEL_HOSTS="api.openai.com api.anthropic.com generativelanguage.googleapis.com"
INTERNET_HOST=example.com

OUT="$EVIDENCE_ROOT/$UNIT"
JSONL="$OUT/canaries.jsonl"

# The environment each canary runs with: the venue's proxy variables removed (canaries/_emit.sh).
SCRUBBED="HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY http_proxy https_proxy all_proxy no_proxy"
scrub_env=(env)
for v in $SCRUBBED; do scrub_env+=(-u "$v"); done

run_canary() {
  local script=$1; shift
  egress_ns_run "$NS" "${scrub_env[@]}" bash "$HERE/canaries/$script" "$@" >> "$JSONL"
}

# Resolution happens OUTSIDE the namespace, before anything is contained.
resolve4() {
  python3 -c "
import socket, sys
try:
    print(socket.getaddrinfo(sys.argv[1], 443, socket.AF_INET)[0][4][0])
except OSError:
    pass" "$1" 2>/dev/null
}
not_run() {  # not_run <canary> <target> <kind> <reason>
  python3 - "$1" "$UNIT" "$2" "$3" "$4" <<'PY' >> "$JSONL"
import json, sys
canary, unit, target, kind, reason = sys.argv[1:6]
print(json.dumps({"canary": canary, "unit": unit, "target": target, "kind": kind,
                  "rc": None, "status": "not-run", "detail": reason}, sort_keys=True))
PY
}

DROP_BEFORE=$(egress_ns_drop_counter "$NS")
# A counter that will not read is a broken instrument, not a zero: defaulting it would inflate
# the recorded delta and fail-OPEN the checker's gate-inert rule (18-class sweep, class 6).
[ -n "$DROP_BEFORE" ] || { echo "run_canaries: cannot read the OUTPUT DROP counter of $NS" >&2; exit 3; }

# F3+F17: create the output directory and canaries.jsonl only AFTER the DROP_BEFORE instrument
# guard passes, so an exit-3 collection leaves no canaries.jsonl behind.
mkdir -p "$OUT"
: > "$JSONL"

# C0 — the positive control first: if the unit cannot reach its allowed target, nothing else means anything.
# E3-b A + P: once per entry, in the given order, the entry's ip:port as target and its path passed explicitly.
for i in "${!ALLOWED[@]}"; do
  run_canary c0_allowed_target.sh "$UNIT" "${ALLOWED[$i]}" "${PROBE_PATHS[$i]}"
done

# C1 — DNS resolution of every model host must fail inside the namespace.
for h in $MODEL_HOSTS; do run_canary c1_dns_resolve.sh "$UNIT" "$h"; done

# C2 / C3 — TCP connect and TLS handshake to each model host's address.
for h in $MODEL_HOSTS; do
  ip=$(resolve4 "$h")
  if [ -z "$ip" ]; then
    not_run C2 "$h:443" tcp-connect "resolve-failed: $h has no A record from this venue"
    not_run C3 "$h:443" tls-handshake "resolve-failed: $h has no A record from this venue"
    continue
  fi
  run_canary c2_tcp_connect.sh "$UNIT" "$h" "$ip"
  run_canary c3_tls_handshake.sh "$UNIT" "$h" "$ip"
done

# C4 — a non-model internet target. RECORDED, not asserted (docs/02_COMPONENT_AUDIT.md:56).
ip=$(resolve4 "$INTERNET_HOST")
if [ -z "$ip" ]; then
  not_run C4 "$INTERNET_HOST:443" tcp-connect-internet "resolve-failed: $INTERNET_HOST has no A record from this venue"
else
  run_canary c4_internet_target.sh "$UNIT" "$INTERNET_HOST" "$ip"
fi

# C5 — UDP/53 to the namespace's resolver (the spike tested TCP only).
run_canary c5_udp_dns.sh "$UNIT" "$RESOLVER"

# C6 — a routable endpoint that is NOT allow-listed: the leg the gate itself discriminates.
run_canary c6_blocked_local.sh "$UNIT" "$BLOCKED"

DROP_AFTER=$(egress_ns_drop_counter "$NS")
[ -n "$DROP_AFTER" ] || { echo "run_canaries: cannot read the OUTPUT DROP counter of $NS" >&2; exit 3; }
RULES_TXT=$(egress_ns_rules "$NS")
RULES_SHA=$(egress_ns_rules_sha256 "$NS")
# Both are OBSERVED from the namespace, never asserted here: a bundle collected after
# `egress_gate_off` records gate "disabled" by construction, and a namespace with no veth
# records the total-isolation mechanism.
GATE_STATE=$(egress_ns_gate_state "$NS")
MECHANISM=$(egress_ns_mechanism "$NS")

python3 - "$OUT" "$UNIT" "$NS" "$(IFS=,; printf '%s' "${ALLOWED[*]}")" "$RULES_SHA" "$DROP_BEFORE" "$DROP_AFTER" \
        "$(uname -r)" "$(iptables --version)" "$VENUE" "$SCRUBBED" "$RULES_TXT" "$GATE_STATE" "$MECHANISM" <<'PY'
import json, os, sys
(out, unit, ns, allowed, rules_sha, before, after, kernel, ipt, venue, scrubbed, rules_txt,
 gate_state, mechanism) = sys.argv[1:15]
# E3-b A: every entry's ip:port, in the given order, without paths (a validated ip:port has no comma).
gate = {"gate": gate_state, "mechanism": mechanism, "netns": ns, "unit": unit,
        "allowed": allowed.split(","), "rules_sha256": rules_sha}
runtime = {"venue": venue, "unit": unit, "kernel": kernel, "iptables_version": ipt,
           "rules": rules_txt.splitlines(), "drop_counter_before": int(before),
           "drop_counter_after": int(after), "proxy_env_scrubbed": scrubbed.split()}
for name, payload in (("gate.json", gate), ("runtime.json", runtime)):
    with open(os.path.join(out, name), "w") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
PY
echo "$OUT"
