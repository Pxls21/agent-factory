#!/usr/bin/env bash
# collect_leg.sh — S0-03's SECOND IDENTITY INSTRUMENT: OmniRoute's own record of both requests.
#
# RUNS ON THE PC. Read-only. It never touches the owner's OmniRoute process, its config, or its
# port; it opens the service's SQLite database in immutable mode and copies out the rows.
#
#   proofs/S0-03/tools/pc/collect_leg.sh <bundle-dir> <route-id>
#
# Writes <bundle-dir>/omniroute-requests.json:
#   {"source": ..., "captured_at": ..., "requests": [{leg, timestamp, method, path, status,
#    model, requested_model, provider, connection_id, combo_name}, ...]}
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

set -euo pipefail

BUNDLE=${1:?usage: collect_leg.sh <bundle-dir> <route-id>}
ROUTE=${2:?usage: collect_leg.sh <bundle-dir> <route-id>}
DATA_DIR=${OMNIROUTE_DATA_DIR:-/home/rocco/.omniroute-migrated}
DB="$DATA_DIR/storage.sqlite"
LIMIT=${S0_03_LOG_LIMIT:-50}

[ -r "$DB" ] || { echo "collect_leg: OmniRoute database unreadable: $DB" >&2; exit 3; }
command -v sqlite3 >/dev/null || { echo "collect_leg: sqlite3 not found" >&2; exit 3; }
mkdir -p "$BUNDLE"

# The two rows we want are the most recent rows for THIS route: leg A hit /v1/responses directly,
# leg B came through Hermes. Both carry requested_model = the route id. Ordering is newest-first;
# the JSON assembly below picks the newest row per leg and labels it.
ROWS=$(sqlite3 -readonly -json "file:$DB?immutable=1" \
  "SELECT timestamp, method, path, status, model, requested_model, provider,
          connection_id, combo_name
     FROM call_logs
    WHERE requested_model = '$ROUTE'
    ORDER BY timestamp DESC
    LIMIT $LIMIT;")

[ -n "$ROWS" ] && [ "$ROWS" != "[]" ] || {
  echo "collect_leg: no call_logs row with requested_model='$ROUTE' — did the legs run?" >&2
  exit 4
}

# Label the newest row per leg. The direct leg's path is /v1/responses and so is Hermes'
# (api_mode codex_responses), so path cannot discriminate: the runner records each leg's request
# window and passes it in. S0_03_DIRECT_AFTER / S0_03_HERMES_AFTER are RFC3339 stamps written by
# run_s0_03_legs.sh immediately before each leg starts.
DIRECT_AFTER=${S0_03_DIRECT_AFTER:?collect_leg: S0_03_DIRECT_AFTER not set by the runner}
HERMES_AFTER=${S0_03_HERMES_AFTER:?collect_leg: S0_03_HERMES_AFTER not set by the runner}

ROWS="$ROWS" DIRECT_AFTER="$DIRECT_AFTER" HERMES_AFTER="$HERMES_AFTER" \
python3 - "$BUNDLE/omniroute-requests.json" "$DB" <<'PY'
import datetime, json, os, sys

out_path, db = sys.argv[1], sys.argv[2]
rows = json.loads(os.environ["ROWS"])
windows = {"direct": os.environ["DIRECT_AFTER"], "hermes": os.environ["HERMES_AFTER"]}

def ts(row):
    return str(row.get("timestamp") or "")

# The hermes leg starts after the direct leg, so the earliest row at/after HERMES_AFTER is the
# hermes request and the earliest row in [DIRECT_AFTER, HERMES_AFTER) is the direct one.
picked = {}
ordered = sorted(rows, key=ts)
for row in ordered:
    t = ts(row)
    if t >= windows["hermes"]:
        picked.setdefault("hermes", row)
    elif t >= windows["direct"]:
        picked.setdefault("direct", row)

missing = [leg for leg in ("direct", "hermes") if leg not in picked]
if missing:
    sys.exit(f"collect_leg: no call_logs row inside the {', '.join(missing)} leg window")

requests = []
for leg in ("direct", "hermes"):
    row = dict(picked[leg])
    row["leg"] = leg
    requests.append(row)

record = {
    "source": f"sqlite:{db} table call_logs (read-only, immutable=1)",
    "captured_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    "windows": windows,
    "requests": requests,
}
with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(record, fh, indent=2, sort_keys=True)
    fh.write("\n")
print("omniroute-requests: " + ", ".join(
    f"{r['leg']}={r.get('provider')!r}/{r.get('model')!r} status={r.get('status')}"
    for r in requests))
PY
