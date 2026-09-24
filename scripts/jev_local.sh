#!/usr/bin/env bash
# jev_local.sh start [--threads N] | stop | status -- the sandbox-local Laya System One server (task #221, D-7).
#
# start   runs the UNCHANGED scripts/laya_systemone_server.py with /root/venv-laya-probe/bin/python, --device cpu,
#         --threads N (default 2: this box shares 4 CPUs with agent test runs), on loopback 127.0.0.1:47411, under
#         setsid nohup ... </dev/null &; the pid goes to .jev/server.pid, the log to .jev/server.log. Idempotent: a
#         healthy server, or this server's process still loading (the model loads for about two minutes before
#         /health answers), means no second start. Exit 2, one line naming the path, when the pinned snapshot is absent.
# stop    kills the pidfile's pid after checking that pid is this server (never pkill -f), then removes the pidfile.
# status  prints the health JSON (exit 0) or `down` (exit 3).
# Exit 64 = usage error.
set -u
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PY=/root/venv-laya-probe/bin/python
SERVER=scripts/laya_systemone_server.py
HF_HOME_DIR=/root/hf-laya-probe
REVISION=1c5edc17a7acd8701df6fc341c0d179f1c62c982
SNAPSHOT=$HF_HOME_DIR/hub/models--convaiinnovations--laya/snapshots/$REVISION
HOST=127.0.0.1
PORT=47411
DIR=$ROOT/.jev
PIDFILE=$DIR/server.pid
LOG=$DIR/server.log

healthy() {   # prints the health JSON when the endpoint answers ok within 1 s AND serves the pinned revision
  local out
  out=$(curl -s --noproxy '*' -m 1 "http://$HOST:$PORT/health" 2>/dev/null) || return 1
  printf '%s' "$out" | grep -q '"ok": *true' || return 1
  printf '%s' "$out" | grep -q "\"revision\": *\"$REVISION\"" || return 1   # a squatter on the port is not this server
  printf '%s\n' "$out"
}

alive() {     # the pid exists and is not a zombie
  local st
  st=$(sed -E 's/^.*\) ([A-Za-z]).*$/\1/' "/proc/$1/stat" 2>/dev/null) || return 1
  [ -n "$st" ] && [ "$st" != Z ]
}

our_pid() {   # prints the pidfile's pid when that process is alive and is this server
  local pid
  [ -f "$PIDFILE" ] || return 1
  pid=$(tr -dc '0-9' < "$PIDFILE")
  [ -n "$pid" ] && alive "$pid" || return 1
  tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null | grep -q 'laya_systemone_server[.]py' || return 1
  printf '%s\n' "$pid"
}

cmd_start() {
  local threads=2 out pid i
  while [ $# -gt 0 ]; do
    case "$1" in
      --threads) threads=${2:-}; shift; [ $# -gt 0 ] && shift ;;
      --threads=*) threads=${1#--threads=}; shift ;;
      *) echo "jev_local: usage: jev_local.sh start [--threads N]" >&2; return 64 ;;
    esac
  done
  case "$threads" in ''|*[!0-9]*|0*) echo "jev_local: --threads must be a positive integer" >&2; return 64 ;; esac
  if out=$(healthy); then
    echo "jev_local: already running: $out"
    return 0
  fi
  if pid=$(our_pid); then
    echo "jev_local: already starting (pid $pid); /health answers once the model has loaded"
    return 0
  fi
  if [ ! -d "$SNAPSHOT" ]; then
    echo "jev_local: no Laya snapshot at $SNAPSHOT" >&2
    return 2
  fi
  mkdir -p "$DIR" || return 2
  chmod 700 "$DIR"
  rm -f "$PIDFILE"
  cd "$ROOT" || return 2
  export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
  # the inner shell writes its own pid, then execs the server in place: the pidfile names the server process
  setsid nohup bash -c 'echo $$ > "$1"; exec "$2" "$3" --device cpu --threads "$4" --host "$5" --port "$6" --hf-home "$7"' _ "$PIDFILE" "$PY" "$SERVER" "$threads" "$HOST" "$PORT" "$HF_HOME_DIR" > "$LOG" 2>&1 < /dev/null &
  for i in $(seq 1 50); do
    if pid=$(our_pid); then
      echo "jev_local: started (pid $pid, --threads $threads, log $LOG); /health answers once the model has loaded (about two minutes)"
      return 0
    fi
    sleep 0.1
  done
  echo "jev_local: the server did not start; see $LOG" >&2
  return 2
}

cmd_stop() {
  local pid i
  if ! pid=$(our_pid); then
    if [ -f "$PIDFILE" ]; then
      rm -f "$PIDFILE"
      echo "jev_local: the pidfile named no running server; removed it"
    else
      echo "jev_local: not running (no pidfile)"
    fi
    return 0
  fi
  kill -TERM "$pid"
  for i in $(seq 1 40); do
    alive "$pid" || break
    sleep 0.25
  done
  if alive "$pid"; then
    kill -KILL "$pid"
  fi
  rm -f "$PIDFILE"
  echo "jev_local: stopped (pid $pid)"
}

cmd_status() {
  local out
  if out=$(healthy); then
    printf '%s\n' "$out"
    return 0
  fi
  echo down
  return 3
}

case "${1:-}" in
  start) shift; cmd_start "$@" ;;
  stop) shift; [ $# -eq 0 ] || { echo "jev_local: usage: jev_local.sh stop" >&2; exit 64; }; cmd_stop ;;
  status) shift; [ $# -eq 0 ] || { echo "jev_local: usage: jev_local.sh status" >&2; exit 64; }; cmd_status ;;
  *) echo "jev_local: usage: jev_local.sh start [--threads N] | stop | status" >&2; exit 64 ;;
esac
