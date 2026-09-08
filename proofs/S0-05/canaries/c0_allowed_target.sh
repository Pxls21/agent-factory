#!/usr/bin/env bash
# C0 — THE POSITIVE CONTROL. The contained unit must REACH its one allowed target (the seed:
# "each canary first proves its positive control (the unit CAN reach its allowed target)").
# A bundle whose C0 failed is never a pass: it is `positive-control-failed: <unit>`, which is
# exactly what a bare `unshare --net` produces (AF-AP-1).
#   c0_allowed_target.sh <unit> <ip:port|url> [path]
set -u
. "$(dirname "$0")/_emit.sh"
unit=${1:?unit} target=${2:?target} path=${3:-/v1/models}
case "$target" in http://*|https://*) url="$target$path";; *) url="http://$target$path";; esac
err=$(mktemp); code=$(curl -sS --connect-timeout "$EGRESS_CONNECT_TIMEOUT" --max-time "$EGRESS_MAX_TIME" \
      -o /dev/null -w '%{http_code}' "$url" 2>"$err"); rc=$?
detail=$(cat "$err"); rm -f "$err"
[ -n "$detail" ] || detail="curl exit $rc, HTTP $code"
emit_canary C0 "$unit" "$target" http-get "$rc" run "$detail" "http_status=$code"
