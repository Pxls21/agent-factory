#!/usr/bin/env bash
# collect_leg.sh — S0-03's SECOND IDENTITY INSTRUMENT: OmniRoute's own record of both requests.
#
# RUNS ON THE PC. Read-only. It never touches the owner's OmniRoute process, its config, or its
# port; it opens the service's SQLite database in immutable mode and copies out the rows.
#
#   proofs/S0-03/tools/pc/collect_leg.sh <bundle-dir> <route-id>
#
# Writes <bundle-dir>/omniroute-requests.json:
#   {"source": ..., "captured_at": ..., "windows": {"hermes": {"start":..., "end":...}},
#    "requests": [{leg, id, timestamp, method, path, status, model, requested_model, provider,
#                  connection_id, combo_name, correlation_id, session_tag, response_id}, ...]}
#
# WHY THIS INSTRUMENT, AND NOT THE HTTP API
# -----------------------------------------
# `/api/usage/request-logs` requires MANAGEMENT auth (`requireManagementAuth`,
# src/app/api/usage/request-logs/route.ts:6-7), i.e. a dashboard session — a route the owner
# ruled OUT for this work (docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md:33-40: the coordinator does
# not use the owner's password). The client API key cannot read it. The same rows are in the
# service's own database, which the owner's account can read directly.
#
# The table is `call_logs` and the columns are exactly the ones the identity claim needs —
# `model` (the RESOLVED upstream model), `requested_model` (what the client asked for) and
# `provider` / `connection_id` (which provider connection served it) are separate columns
# (src/lib/usage/callLogs.ts:564-572). The response body cannot show a stub route; this can.
# DATA_DIR resolution: `SQLITE_FILE = path.join(DATA_DIR, "storage.sqlite")`
# (src/lib/db/core.ts:104-106); on the PC DATA_DIR is /home/rocco/.omniroute-migrated
# (PC-BRIDGE.md:153-163), overridable here with OMNIROUTE_DATA_DIR.
#
# `file:...?immutable=1` opens the database without taking a lock and without writing a WAL or
# journal file — a live service keeps serving, undisturbed. Consequence, stated: rows still only
# in the WAL are not visible, so the runner passes --settle first.
#
# HOW A ROW IS BOUND TO A LEG (live-capture 2026-09-18, AF-AP-103 realign)
# -----------------------------------------------------------------
# Two real bindings exist in the schema:
#   direct  ->  call_logs.id, which is the x-omniroute-request-id response header the client
#               receives. `direct.json.response_headers['x-omniroute-request-id']` records it.
#               The old binding on `response_id` was dead (always NULL in call_logs).
#   hermes  ->  call_logs.session_tag == the leg's nonce2 (injected as x-omniroute-session-id),
#               AND combo_name == the route id. The round trip logs MANY rows (>=1), all tagged.
#               Window is kept as a sanity bound (every tagged row must fall within), not a
#               uniqueness rule.
# Route filter: combo_name, NOT requested_model (which holds the resolved ref
# `codex/gpt-5.6-sol-ultra`, never the route id `agentfactory-build`).

set -euo pipefail

BUNDLE=${1:?usage: collect_leg.sh <bundle-dir> <route-id>}
ROUTE=${2:?usage: collect_leg.sh <bundle-dir> <route-id>}
DATA_DIR=${OMNIROUTE_DATA_DIR:-/home/rocco/.omniroute-migrated}
DB="$DATA_DIR/storage.sqlite"
[ -r "$DB" ] || { echo "collect_leg: OmniRoute database unreadable: $DB" >&2; exit 3; }
mkdir -p "$BUNDLE"

# Every value below is BOUND as a query parameter inside python's sqlite3 (VERIFY-O1 F-15): the
# old form interpolated $ROUTE into the SQL text, where one quote breaks or extends the query.
BUNDLE="$BUNDLE" ROUTE="$ROUTE" DB="$DB" python3 - <<'PY'
import datetime, json, os, sqlite3, sys

bundle, route, db = os.environ["BUNDLE"], os.environ["ROUTE"], os.environ["DB"]
COLUMNS = ("id, timestamp, method, path, status, model, requested_model, provider, "
           "connection_id, combo_name, correlation_id, session_tag, response_id")


def parse_stamp(value, what):
    """RFC3339 -> aware datetime. The two producers write different fractional precision —
    the runner's `date -u +%…%6NZ` is 6 digits, OmniRoute's `new Date().toISOString()` is 3
    (src/lib/usage/callLogs.ts:489) — and comparing those as STRINGS puts a row up to a
    millisecond before the window start inside it ('Z' > '4'). Compare as instants (F-14)."""
    if not isinstance(value, str) or not value:
        sys.exit(f"collect_leg: {what} is not an RFC3339 stamp: {value!r}")
    try:
        parsed = datetime.datetime.fromisoformat(
            value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError:
        sys.exit(f"collect_leg: {what} is not an RFC3339 stamp: {value!r}")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        sys.exit(f"collect_leg: {what} is not an RFC3339 stamp with an offset: {value!r}")
    return parsed.astimezone(datetime.timezone.utc)


def read_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


direct = read_json(os.path.join(bundle, "direct", "direct.json"))
leg = read_json(os.path.join(bundle, "hermes", "leg.json"))

# Direct leg binding: x-omniroute-request-id from the response headers (== call_logs.id).
# NOT direct.json.id, which is the resp_... Responses-API body id (a different thing).
resp_headers = direct.get("response_headers") if isinstance(direct, dict) else None
request_id = None
if isinstance(resp_headers, dict):
    request_id = resp_headers.get("x-omniroute-request-id")
if request_id is not None and not isinstance(request_id, str):
    sys.exit(f"collect_leg: x-omniroute-request-id is not a string: {request_id!r}")

# Hermes leg binding: session_tag (the nonce2).
nonce2 = leg.get("nonce2") if isinstance(leg, dict) else None
if nonce2 is not None and not isinstance(nonce2, str):
    sys.exit(f"collect_leg: hermes/leg.json nonce2 is not a string: {nonce2!r}")

window = None
if isinstance(leg, dict) and leg.get("window_start") is not None:
    start = parse_stamp(leg.get("window_start"), "hermes/leg.json window_start")
    end = parse_stamp(leg.get("window_end"), "hermes/leg.json window_end")
    if end < start:
        sys.exit("collect_leg: hermes/leg.json window_end precedes window_start")
    window = {"start": leg["window_start"], "end": leg["window_end"]}
    # SQLite compares RFC3339 values as raw text here. Offset-bearing rows can represent an
    # in-window instant while their local date sorts outside the UTC date prefix. RFC3339
    # permits offsets only through +/-23:59, so one full day on each side makes this lexical
    # query a proven superset; the aware-instant comparison below remains authoritative.
    sql_start = (start - datetime.timedelta(days=1)).astimezone(
        datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    sql_end = (end + datetime.timedelta(days=1)).astimezone(
        datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

conn = sqlite3.connect(f"file:{db}?immutable=1", uri=True)
conn.row_factory = sqlite3.Row
requests = []
try:
    if request_id is not None:
        rows = conn.execute(
            f"SELECT {COLUMNS} FROM call_logs "
            "WHERE combo_name = ? AND id = ? "
            "ORDER BY timestamp ASC",
            (route, request_id)).fetchall()
        for row in rows:
            requests.append(dict(row, leg="direct"))
    if nonce2 is not None and window is not None:
        rows = conn.execute(
            f"SELECT {COLUMNS} FROM call_logs "
            "WHERE combo_name = ? AND session_tag = ? "
            "ORDER BY timestamp ASC",
            (route, nonce2)).fetchall()
        for row in rows:
            stamp = parse_stamp(row["timestamp"], "call_logs.timestamp")
            if start <= stamp <= end:
                requests.append(dict(row, leg="hermes"))
finally:
    conn.close()

counts = {"direct": 0, "hermes": 0}
for row in requests:
    counts[row["leg"]] += 1
record = {
    "source": f"sqlite:{db} table call_logs (read-only, immutable=1)",
    "captured_at": datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"),
    "windows": {} if window is None else {"hermes": window},
    "row_counts": counts,
    "requests": requests,
}
with open(os.path.join(bundle, "omniroute-requests.json"), "w", encoding="utf-8") as fh:
    json.dump(record, fh, indent=2, sort_keys=True)
    fh.write("\n")

summary = ", ".join(
    f"{r['leg']}={r.get('provider')!r}/{r.get('model')!r} status={r.get('status')} "
    f"session_tag={r.get('session_tag')!r}" for r in requests)
print("omniroute-requests: " + (summary if summary else "no rows"))
print(f"omniroute-requests: direct={counts['direct']} hermes={counts['hermes']} "
      f"(declared: direct={request_id is not None} hermes={nonce2 is not None and window is not None})")

# A DECLARED leg with no row is LOUD: the leg ran, so a missing row means the export looked in
# the wrong place. A leg that was never declared (the negative root has no request-id header and
# no nonce2) legitimately contributes nothing.
missing = [name for name, declared in (("direct", request_id is not None),
                                       ("hermes", nonce2 is not None and window is not None))
           if declared and counts[name] == 0]
if missing:
    sys.exit("collect_leg: no call_logs row for the "
             f"{', '.join(missing)} leg — did the legs run against {route!r}?")
PY
