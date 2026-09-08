#!/usr/bin/env bash
# _emit.sh — sourced by every canary: the one-JSON-line emitter and the environment scrub.
#
# THE SCRUB IS LOAD-BEARING (measured 2026-09-08, this sandbox): the venue exports
# HTTPS_PROXY=http://127.0.0.1:40173, and curl inside the namespace then fails with
# `(7) Failed to connect to 127.0.0.1 port 40173 ... Couldn't connect to server` — a denial
# produced by the ambient proxy, not by the egress gate under test. That is the AF-AP-22 shape
# (a containment observation satisfied by something other than the mechanism). Two defences:
# the canary unsets the proxy variables, and check_egress.py rejects any denial detail outside
# the mechanism's own vocabulary, so a proxy-shaped failure can never be read as a pass.
EGRESS_SCRUBBED_ENV="HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY http_proxy https_proxy all_proxy no_proxy"
# shellcheck disable=SC2086
unset $EGRESS_SCRUBBED_ENV

emit_canary() {
  # emit_canary <canary> <unit> <target> <kind> <rc|-> <status> <detail> [key=value ...]
  python3 - "$@" <<'PY'
import json, sys
canary, unit, target, kind, rc, status, detail = sys.argv[1:8]
record = {"canary": canary, "unit": unit, "target": target, "kind": kind,
          "rc": None if rc == "-" else int(rc), "status": status,
          "detail": " ".join(detail.split())[:300]}
for pair in sys.argv[8:]:
    key, _, value = pair.partition("=")
    try:
        record[key] = int(value)
    except ValueError:
        record[key] = value
print(json.dumps(record, sort_keys=True))
PY
}

# Every probe that talks to a remote address is bounded: connect timeout 5 s (the brief's pin),
# total 8 s. No canary ever sends a request body to a provider.
EGRESS_CONNECT_TIMEOUT=5
EGRESS_MAX_TIME=8
