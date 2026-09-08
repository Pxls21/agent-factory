#!/usr/bin/env bash
# run_canaries.sh — run the S0-05 canary suite INSIDE an already-created egress namespace, as
# one contained unit, and write that unit's evidence bundle.
#
#   run_canaries.sh <unit> <ns> <allowed ip:port> [evidence-root] [blocked ip:port] [venue]
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

UNIT=${1:?usage: run_canaries.sh <unit> <ns> <allowed ip:port> [evidence-root] [blocked ip:port] [venue]}
NS=${2:?ns}
ALLOWED=${3:?allowed ip:port}
EVIDENCE_ROOT=${4:-"$HERE/evidence"}
HOST_IP=$(egress_ns_host_ip "$NS")
ALLOWED_PORT=${ALLOWED##*:}
BLOCKED=${5:-"$HOST_IP:$((ALLOWED_PORT + 1))"}
VENUE=${6:-sandbox}
RESOLVER=$(egress_ns_resolver "$NS")

MODEL_HOSTS="api.openai.com api.anthropic.com generativelanguage.googleapis.com"
INTERNET_HOST=example.com

OUT="$EVIDENCE_ROOT/$UNIT"
mkdir -p "$OUT"
JSONL="$OUT/canaries.jsonl"
: > "$JSONL"

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

# C0 — the positive control first: if the unit cannot reach its allowed target, nothing else means anything.
run_canary c0_allowed_target.sh "$UNIT" "$ALLOWED"

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

python3 - "$OUT" "$UNIT" "$NS" "$ALLOWED" "$RULES_SHA" "$DROP_BEFORE" "$DROP_AFTER" \
        "$(uname -r)" "$(iptables --version)" "$VENUE" "$SCRUBBED" "$RULES_TXT" "$GATE_STATE" "$MECHANISM" <<'PY'
import json, os, sys
(out, unit, ns, allowed, rules_sha, before, after, kernel, ipt, venue, scrubbed, rules_txt,
 gate_state, mechanism) = sys.argv[1:15]
gate = {"gate": gate_state, "mechanism": mechanism, "netns": ns, "unit": unit,
        "allowed": [allowed], "rules_sha256": rules_sha}
runtime = {"venue": venue, "unit": unit, "kernel": kernel, "iptables_version": ipt,
           "rules": rules_txt.splitlines(), "drop_counter_before": int(before),
           "drop_counter_after": int(after), "proxy_env_scrubbed": scrubbed.split()}
for name, payload in (("gate.json", gate), ("runtime.json", runtime)):
    with open(os.path.join(out, name), "w") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
PY
echo "$OUT"
