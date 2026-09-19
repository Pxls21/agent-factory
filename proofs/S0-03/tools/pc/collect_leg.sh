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
#                  connection_id, combo_name, correlation_id, session_tag, response_id,
#                  recorded_input (direct leg only: OmniRoute's own recorded requestBody)}, ...]}
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
# `file:...?mode=ro` opens the database READ-ONLY and WAL-aware. This DB runs in WAL mode, so a
# live service keeps serving undisturbed (WAL allows concurrent readers + one writer) AND rows
# still in the -wal file ARE visible. `immutable=1` was WRONG here: it reads only the main DB file
# and MISSES any row not yet checkpointed out of the WAL — measured 2026-09-19, a fresh
# /v1/responses row stayed invisible to immutable for minutes while mode=ro saw it at once
# (AF-AP-104). The runner still passes --settle so the row is COMMITTED before the read.
#
# HOW A ROW IS BOUND TO A LEG (docs + live measurement 2026-09-19, AF-AP-103 / Blocker 4)
# -----------------------------------------------------------------
#   direct  ->  the fresh 16-hex nonce the direct leg sent (`direct.json.nonce`), which OmniRoute
#               records verbatim in the row's ARTIFACT requestBody. /v1/responses exposes no
#               client-visible header or column that maps to call_logs on 3.8.50: routing_decisions
#               is empty, response_id is NULL for a streaming row, and x-request-id /
#               x-omniroute-request-id / correlation_id are three distinct id-spaces (none equal the
#               epoch-suffix call_logs.id). We scan the route's /v1/responses rows in the direct
#               leg's window, read each row's artifact (<DATA_DIR>/call_logs/<artifact_relpath>) and
#               select the ONE whose requestBody carries the nonce; that recorded request travels on
#               as `recorded_input` so the checker re-verifies the binding from the bundle alone.
#               Mirrors the hermes binding: a fresh client nonce OmniRoute records independently.
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
BUNDLE="$BUNDLE" ROUTE="$ROUTE" DB="$DB" DATA_DIR="$DATA_DIR" python3 - <<'PY'
import datetime, json, os, sqlite3, sys

bundle, route, db = os.environ["BUNDLE"], os.environ["ROUTE"], os.environ["DB"]
data_dir = os.environ["DATA_DIR"]
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


def read_artifact_request(relpath):
    """OmniRoute's own recorded client request for a call_logs row, serialized — or None.

    request_detail_logs is empty on 3.8.50; the per-request detail is an artifact FILE under
    <DATA_DIR>/call_logs/<artifact_relpath>, with the client request under `requestBody`.
    Serializing it (dict or str) makes the nonce a decidable substring check regardless of the
    Responses-API `input` shape (a string, or a list of message blocks)."""
    if not relpath:
        return None
    path = os.path.join(data_dir, "call_logs", relpath)
    try:
        with open(path, encoding="utf-8") as fh:
            art = json.load(fh)
    except (OSError, ValueError):
        return None
    body = art.get("requestBody") if isinstance(art, dict) else None
    if body is None:
        return None
    return body if isinstance(body, str) else json.dumps(body, sort_keys=True)


# Direct leg binding (Blocker 4): the fresh nonce direct.json sent, recorded by OmniRoute in the
# row's artifact requestBody. No client-visible header/column maps to call_logs for /v1/responses
# on 3.8.50; the fresh nonce, which OmniRoute records independently, is the identity (mirrors
# hermes). Only a SUCCEEDED (200) leg is bound: a 401 negative leg produces no bound success row
# and is graded on direct.json's own evidence.
direct_nonce = None
direct_window = None
if isinstance(direct, dict) and direct.get("status") == 200:
    direct_nonce = direct.get("nonce")
    if direct_nonce is not None and not isinstance(direct_nonce, str):
        sys.exit(f"collect_leg: direct.json nonce is not a string: {direct_nonce!r}")
    if direct.get("started_at") is not None:
        d_start = parse_stamp(direct.get("started_at"), "direct.json started_at")
        d_end = parse_stamp(direct.get("finished_at"), "direct.json finished_at")
        if d_end < d_start:
            sys.exit("collect_leg: direct.json finished_at precedes started_at")
        # A lexical superset for the SQL fetch (RFC3339 fractional precision differs between the two
        # producers; widen by a day and precise-filter below — the same rule as the hermes window).
        d_sql_start = (d_start - datetime.timedelta(days=1)).astimezone(
            datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        d_sql_end = (d_end + datetime.timedelta(days=1)).astimezone(
            datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        direct_window = (d_start, d_end, d_sql_start, d_sql_end)

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

conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
conn.row_factory = sqlite3.Row
requests = []
try:
    if direct_nonce is not None:
        # Scan the route's /v1/responses rows and select the ONE whose recorded request carries the
        # nonce. The window bounds the fetch cheaply; the fresh nonce is the identity.
        if direct_window is not None:
            _, _, d_sql_start, d_sql_end = direct_window
            rows = conn.execute(
                f"SELECT {COLUMNS}, artifact_relpath FROM call_logs "
                "WHERE combo_name = ? AND path LIKE '%/v1/responses' "
                "AND timestamp >= ? AND timestamp <= ? "
                "ORDER BY timestamp ASC",
                (route, d_sql_start, d_sql_end)).fetchall()
        else:
            rows = conn.execute(
                f"SELECT {COLUMNS}, artifact_relpath FROM call_logs "
                "WHERE combo_name = ? AND path LIKE '%/v1/responses' "
                "ORDER BY timestamp ASC",
                (route,)).fetchall()
        matches = []
        for row in rows:
            if direct_window is not None:
                stamp = parse_stamp(row["timestamp"], "call_logs.timestamp")
                slack = datetime.timedelta(seconds=5)
                if not (direct_window[0] - slack <= stamp <= direct_window[1] + slack):
                    continue
            recorded_input = read_artifact_request(row["artifact_relpath"])
            if recorded_input is not None and direct_nonce in recorded_input:
                out = {k: row[k] for k in row.keys() if k != "artifact_relpath"}
                out["leg"] = "direct"
                out["recorded_input"] = recorded_input
                matches.append(out)
        if len(matches) > 1:
            sys.exit(f"collect_leg: {len(matches)} /v1/responses rows carry the direct nonce — "
                     "the nonce must select exactly one row")
        requests.extend(matches)
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
    "source": f"sqlite:{db} table call_logs (read-only, mode=ro, WAL-aware)",
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
      f"(declared: direct={direct_nonce is not None} hermes={nonce2 is not None and window is not None})")

# A DECLARED leg with no row is LOUD: the leg ran, so a missing row means the export looked in
# the wrong place. A leg that was never declared (the negative root's direct leg 401s, so no
# succeeded row, and it has no nonce2) legitimately contributes nothing.
missing = [name for name, declared in (("direct", direct_nonce is not None),
                                       ("hermes", nonce2 is not None and window is not None))
           if declared and counts[name] == 0]
if missing:
    sys.exit("collect_leg: no call_logs row for the "
             f"{', '.join(missing)} leg — did the legs run against {route!r}?")
PY
