#!/usr/bin/env bash
# jev_relay_up.sh: start the Jev relay when it is not running and can serve (task #419, D-119).
#
# The output pruner (fast-jev-output@fast-jev-output) posts its Jev requests to the relay on 127.0.0.1:<port> (its
# pluginConfigs baseUrl). With no relay it fails open and prunes nothing, and nothing says so (AF-AP-252); a container
# restart stops the relay. scripts/setup.sh runs this at every session start.
#
#   jev_relay_up.sh [--port N] [--env-file F] [--off-file F] [--log F] [-- relay serve args...]
#
# Prints one status line: off, NOT started (no key file, or the start failed), already running (and whether it runs
# the code in scripts/jev_relay.py), or started. Exit 0 on every status, so a session start never fails on the relay;
# 64 on a usage error. "Running" means a relay answered /health on the port, never only that something listens there
# (AF-AP-33); a relay running older code is reported, never stopped: the stop is by its pid, by hand.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT=47430
ENV_FILE=/root/.codiv/api.env
OFF="$ROOT/.jev/relay-off"
LOG=/tmp/jev-relay.log
EXTRA=()
while [ $# -gt 0 ]; do
  case "$1" in
    --port|--env-file|--off-file|--log)
      [ $# -ge 2 ] || { echo "jev_relay_up: $1 needs a value" >&2; exit 64; }
      case "$1" in --port) PORT="$2" ;; --env-file) ENV_FILE="$2" ;; --off-file) OFF="$2" ;; --log) LOG="$2" ;; esac
      shift 2 ;;
    --) shift; EXTRA=("$@"); break ;;
    *) echo "jev_relay_up: usage: [--port N] [--env-file F] [--off-file F] [--log F] [-- relay serve args...]" >&2
       exit 64 ;;
  esac
done
case "$PORT" in ''|*[!0-9]*) echo "jev_relay_up: --port takes a number" >&2; exit 64 ;; esac

# health PORT SECONDS: 0 when a relay answers /health on the port within SECONDS ("<pid> <relay_sha256>" on stdout),
# else 1.
health() {
  python3 - "$1" "$2" <<'PY'
import json, sys, time, urllib.request
port, deadline = sys.argv[1], time.monotonic() + float(sys.argv[2])
op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
while True:
    try:
        h = json.loads(op.open("http://127.0.0.1:%s/health" % port, timeout=1).read())
        if h.get("ok") is True and "upstream_host" in h:
            print(h.get("pid"), h.get("relay_sha256"))
            sys.exit(0)
    except Exception:
        pass
    if time.monotonic() >= deadline:
        sys.exit(1)
    time.sleep(0.1)
PY
}

if [ -e "$OFF" ]; then
  echo "jev relay: off ($OFF exists); the pruner prunes nothing"
  exit 0
fi
if [ ! -f "$ENV_FILE" ]; then
  echo "jev relay: NOT started, no key file ($ENV_FILE); the pruner prunes nothing"
  exit 0
fi
if FOUND=$(health "$PORT" 0); then
  PID=${FOUND%% *}
  HERE_SHA=$(sha256sum "$ROOT/scripts/jev_relay.py")
  if [ "${FOUND#* }" = "${HERE_SHA%% *}" ]; then
    echo "jev relay: already running on 127.0.0.1:$PORT (pid $PID)"
  else
    echo "jev relay: already running on 127.0.0.1:$PORT (pid $PID) with code other than scripts/jev_relay.py;" \
      "stop it by that pid and run this again to update"
  fi
  exit 0
fi
setsid nohup python3 "$ROOT/scripts/jev_relay.py" serve --port "$PORT" --env-file "$ENV_FILE" "${EXTRA[@]}" \
  >> "$LOG" 2>&1 < /dev/null &
if FOUND=$(health "$PORT" 5); then
  echo "jev relay: started on 127.0.0.1:$PORT (pid ${FOUND%% *}, log $LOG)"
else
  echo "jev relay: NOT started (no /health answer on 127.0.0.1:$PORT within 5 s; see $LOG); the pruner prunes nothing"
fi
exit 0
