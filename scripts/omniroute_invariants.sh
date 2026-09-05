#!/usr/bin/env bash
# omniroute_invariants.sh — READ-ONLY monitor: is the OmniRoute that owns the inference port the
# managed, authoritative instance? (docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md §Recovery runbook,
# handoff remaining-actions 4+5.) It NEVER remediates — no kill, no restart, no config write. Each
# invariant prints one `OK`/`FAIL <check>: <reason>` line; exit 0 = all OK, 1 = at least one FAIL,
# 2 = usage/tool error. Runs on the PC (owner shell or `scripts/pc.sh "$(cat scripts/omniroute_invariants.sh)"`).
#
# Why these checks (2026-09-05 incident): an unmanaged OmniRoute from an old shell squatted :20128
# serving the small default ~/.omniroute database while /api/health still said 200 and systemd
# reported the managed unit "active" inside its EADDRINUSE restart loop. Health alone is blind to
# that; ownership (cgroup) + the listener's OWN environ (kernel truth via /proc, not the unit's
# declared config) + the authenticated catalog are what discriminate.
#
# Env (all optional except the key file for the catalog check):
#   OMNIROUTE_PORT          default 20128
#   OMNIROUTE_SERVICE       default omniroute-migrated.service
#   OMNIROUTE_DATA_DIR      default /home/rocco/.omniroute-migrated
#   OMNIROUTE_BASE_URL      default http://127.0.0.1:$OMNIROUTE_PORT
#   OMNIROUTE_REQUIRED_IDS  space-separated model/combo ids that must appear in /v1/models
#                           default: the four agentfactory-* combos + ollama-cloud/kimi-k3
#   OMNIROUTE_API_KEY_FILE  0600 env file carrying `OMNIROUTE_API_KEY=…`; the key is read from the
#                           file and sent via a header FILE (`curl -H @<fd>`), never placed in argv
#   PROC_ROOT               default /proc (tests point it at a fixture tree)
set -uo pipefail
PORT="${OMNIROUTE_PORT:-20128}"
SERVICE="${OMNIROUTE_SERVICE:-omniroute-migrated.service}"
DATA_DIR="${OMNIROUTE_DATA_DIR:-/home/rocco/.omniroute-migrated}"
BASE="${OMNIROUTE_BASE_URL:-http://127.0.0.1:$PORT}"
REQ="${OMNIROUTE_REQUIRED_IDS:-agentfactory-build agentfactory-verify agentfactory-research agentfactory-sweep ollama-cloud/kimi-k3}"
KEYFILE="${OMNIROUTE_API_KEY_FILE:-}"
PROC="${PROC_ROOT:-/proc}"
fails=0
ok()   { printf 'OK   %s: %s\n' "$1" "$2"; }
fail() { printf 'FAIL %s: %s\n' "$1" "$2"; fails=$((fails + 1)); }
for t in ss systemctl curl grep cut sort tr tail head mktemp wc; do
  command -v "$t" >/dev/null 2>&1 || { echo "omniroute_invariants: tool missing: $t" >&2; exit 2; }
done

# 1. exactly one listener owns the port
pids=$(ss -lntpH "sport = :$PORT" 2>/dev/null | grep -o 'pid=[0-9]*' | cut -d= -f2 | sort -u)
n=$(printf '%s\n' $pids | grep -c .)
if [ "$n" -eq 1 ]; then ok listener "pid $pids owns :$PORT"
else fail listener "expected exactly 1 listener pid on :$PORT, found $n [$(printf '%s ' $pids)]"; fi
pid=$(printf '%s\n' $pids | head -1)

# 2. the listener belongs to the managed unit, not an interactive session scope
if [ -n "$pid" ] && [ -r "$PROC/$pid/cgroup" ]; then
  cg=$(tail -1 "$PROC/$pid/cgroup")
  case "$cg" in
    */"$SERVICE") ok cgroup "$cg" ;;
    *) fail cgroup "listener pid $pid is in '$cg', not $SERVICE (unmanaged duplicate?)" ;;
  esac
else fail cgroup "cannot read $PROC/${pid:-?}/cgroup"; fi

# 3. authoritative DATA_DIR: kernel truth (the listener's own environ) AND the unit's declaration
if [ -n "$pid" ] && tr '\0' '\n' < "$PROC/$pid/environ" 2>/dev/null | grep -qx "DATA_DIR=$DATA_DIR"; then
  ok data_dir_environ "listener environ has DATA_DIR=$DATA_DIR"
else fail data_dir_environ "listener environ lacks DATA_DIR=$DATA_DIR"; fi
if systemctl --user show -p Environment "$SERVICE" 2>/dev/null | grep -q "DATA_DIR=$DATA_DIR"; then
  ok data_dir_unit "$SERVICE declares DATA_DIR=$DATA_DIR"
else fail data_dir_unit "$SERVICE does not declare DATA_DIR=$DATA_DIR (override missing?)"; fi

# 4. the inference plane requires a key (ADR 0002: scoped credentials; standing rule 11)
if [ -n "$pid" ] && tr '\0' '\n' < "$PROC/$pid/environ" 2>/dev/null | grep -qx 'REQUIRE_API_KEY=true'; then
  ok require_api_key "listener environ has REQUIRE_API_KEY=true"
else fail require_api_key "listener environ lacks REQUIRE_API_KEY=true — /v1/* is unauthenticated"; fi

# 5. health
code=$(curl -s -o /dev/null -w '%{http_code}' -m 8 "$BASE/api/health")
if [ "$code" = "200" ]; then ok health "GET /api/health -> 200"; else fail health "GET /api/health -> $code"; fi

# 6. authenticated catalog carries every required id
if [ -z "$KEYFILE" ]; then fail catalog "OMNIROUTE_API_KEY_FILE not set — cannot read the authenticated catalog"
elif [ ! -r "$KEYFILE" ]; then fail catalog "key file $KEYFILE is unreadable"
else
  key=$(grep '^OMNIROUTE_API_KEY=' "$KEYFILE" | head -1 | cut -d= -f2- | tr -d '\r\n"')
  if [ -z "$key" ]; then fail catalog "no OMNIROUTE_API_KEY= line in $KEYFILE"
  else
    body=$(mktemp)
    code=$(curl -s -o "$body" -w '%{http_code}' -m 20 -H @<(printf 'Authorization: Bearer %s\n' "$key") "$BASE/v1/models")
    if [ "$code" != "200" ]; then fail catalog "GET /v1/models -> $code"
    else
      missing=""
      for id in $REQ; do
        grep -q "\"id\"[[:space:]]*:[[:space:]]*\"$id\"" "$body" || missing="$missing $id"
      done
      total=$(grep -o '"id"[[:space:]]*:' "$body" | wc -l | tr -d ' ')
      if [ -z "$missing" ]; then ok catalog "$total ids; every required id present"
      else fail catalog "catalog ($total ids) lacks:$missing"; fi
    fi
    rm -f "$body"
  fi
fi

[ "$fails" -eq 0 ] && exit 0 || exit 1
