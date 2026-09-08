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
# HOW A ROW IS BOUND TO A LEG (VERIFY-O1 F-1 — the round's blocker)
# -----------------------------------------------------------------
# The previous version SELECTed the newest rows of the route and attributed "the earliest row
# at/after a wall-clock stamp" to each leg. On the PC the route `agentfactory-build` is the route
# the owner's OWN build lanes use, so any concurrent request inside the window became "our" row,
# and a hand-written row with a foreign response id passed the identity assertion untouched.
# Nothing bound a row to a leg. Two real bindings exist in the schema and are used here:
#   direct  ->  call_logs.response_id, which is the `resp_…` id the CLIENT streamed
#               (`open-sse/handlers/chatCore/attemptLogging.ts:501`
#               `responseId: extractResponsesId(sourceFormat, clientResponse)`, stored at
#               `src/lib/usage/callLogs.ts:521-524` and inserted as `response_id` at :564-584).
#               `direct.json` already records the same value as `id`, so the two artefacts join
#               on a value neither side can invent. Selected BY that id — not by time.
#   hermes  ->  call_logs.session_tag, which OmniRoute fills from the CLIENT-SUPPLIED
#               `x-omniroute-session-id` header: `src/sse/handlers/chat.ts:822` reads it,
#               `open-sse/services/conversationTracker.ts:465-469` returns it verbatim ("Client
#               override wins outright"), and `open-sse/handlers/chatCore.ts:1096` passes it as
#               `sessionTag`. The runner puts the leg's nonce2 there through the launched
#               profile's `extra_headers`. The header is NOT stripped by the authz pipeline
#               (`src/server/authz/headers.ts:79-87` lists the seven trusted headers it deletes;
#               x-omniroute-session-id is not one of them).
#               Hermes' request is still window-bounded here: this script exports EVERY route row
#               inside the leg's CLOSED window, and the checker fails the proof when there is
#               more than one. Exporting them all is the point — the old code picked the earliest
#               and hid the ambiguity.
# The window comes from the leg's own `hermes/leg.json` (`window_start`/`window_end`, written by
# the runner before and after the turn), so the export cannot widen it without the checker
# seeing: `omniroute-requests.json` carries the window it used and the checker compares it with
# the leg record.

set -euo pipefail

BUNDLE=${1:?usage: collect_leg.sh <bundle-dir> <route-id>}
ROUTE=${2:?usage: collect_leg.sh <bundle-dir> <route-id>}
DATA_DIR=${OMNIROUTE_DATA_DIR:-/home/rocco/.omniroute-migrated}
DB="$DATA_DIR/storage.sqlite"
LIMIT=${S0_03_LOG_LIMIT:-50}

[ -r "$DB" ] || { echo "collect_leg: OmniRoute database unreadable: $DB" >&2; exit 3; }
mkdir -p "$BUNDLE"

# Every value below is BOUND as a query parameter inside python's sqlite3 (VERIFY-O1 F-15): the
# old form interpolated $ROUTE into the SQL text, where one quote breaks or extends the query.
BUNDLE="$BUNDLE" ROUTE="$ROUTE" DB="$DB" LIMIT="$LIMIT" python3 - <<'PY'
import datetime, json, os, sqlite3, sys

bundle, route, db, limit = (os.environ["BUNDLE"], os.environ["ROUTE"],
                            os.environ["DB"], int(os.environ["LIMIT"]))
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
        return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        sys.exit(f"collect_leg: {what} is not an RFC3339 stamp: {value!r}")


def read_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


direct = read_json(os.path.join(bundle, "direct", "direct.json"))
leg = read_json(os.path.join(bundle, "hermes", "leg.json"))
response_id = direct.get("id") if isinstance(direct, dict) else None
if response_id is not None and not isinstance(response_id, str):
    sys.exit(f"collect_leg: direct/direct.json id is not a string: {response_id!r}")

window = None
if isinstance(leg, dict) and leg.get("window_start") is not None:
    start = parse_stamp(leg.get("window_start"), "hermes/leg.json window_start")
    end = parse_stamp(leg.get("window_end"), "hermes/leg.json window_end")
    if end < start:
        sys.exit("collect_leg: hermes/leg.json window_end precedes window_start")
    window = {"start": leg["window_start"], "end": leg["window_end"]}

conn = sqlite3.connect(f"file:{db}?immutable=1", uri=True)
conn.row_factory = sqlite3.Row
requests = []
try:
    if response_id is not None:
        rows = conn.execute(
            f"SELECT {COLUMNS} FROM call_logs "
            "WHERE requested_model = ? AND response_id = ? "
            "ORDER BY timestamp ASC LIMIT ?",
            (route, response_id, limit)).fetchall()
        for row in rows:
            requests.append(dict(row, leg="direct"))
    if window is not None:
        rows = conn.execute(
            f"SELECT {COLUMNS} FROM call_logs "
            "WHERE requested_model = ? ORDER BY timestamp ASC LIMIT ?",
            (route, limit)).fetchall()
        for row in rows:
            stamp = parse_stamp(row["timestamp"], "call_logs.timestamp")
            if start <= stamp <= end:
                requests.append(dict(row, leg="hermes"))
finally:
    conn.close()

record = {
    "source": f"sqlite:{db} table call_logs (read-only, immutable=1)",
    "captured_at": datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"),
    "windows": {} if window is None else {"hermes": window},
    "requests": requests,
}
with open(os.path.join(bundle, "omniroute-requests.json"), "w", encoding="utf-8") as fh:
    json.dump(record, fh, indent=2, sort_keys=True)
    fh.write("\n")

counts = {"direct": 0, "hermes": 0}
for row in requests:
    counts[row["leg"]] += 1
summary = ", ".join(
    f"{r['leg']}={r.get('provider')!r}/{r.get('model')!r} status={r.get('status')} "
    f"session_tag={r.get('session_tag')!r}" for r in requests)
print("omniroute-requests: " + (summary if summary else "no rows"))
print(f"omniroute-requests: direct={counts['direct']} hermes={counts['hermes']} "
      f"(declared: direct={response_id is not None} hermes={window is not None})")

# A DECLARED leg with no row is LOUD: the leg ran, so a missing row means the export looked in
# the wrong place. A leg that was never declared (the negative root has no response id and no
# hermes turn) legitimately contributes nothing.
missing = [name for name, declared in (("direct", response_id is not None),
                                       ("hermes", window is not None))
           if declared and counts[name] == 0]
if missing:
    sys.exit("collect_leg: no call_logs row for the "
             f"{', '.join(missing)} leg — did the legs run against {route!r}?")
PY
