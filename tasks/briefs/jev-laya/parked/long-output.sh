#!/usr/bin/env bash
# long-output.sh — run a command whose stdout may be long, trimming only the MODEL'S VIEW of it when the local
# pruner is available (PCJ1, 2026-09-22). A lane model calls it by name for long, read-only output it only needs to
# skim (a log tail, a grep over a tree, a long listing). Gate, test and check commands whose counts, verdicts or exit
# codes are pasted or graded run WITHOUT it — the role paragraph says so.
#
#   bash "$AF_REPO/harness-ports/bin/long-output.sh" -- <command> [args...]
#
# ON only when BOTH hold: the built wrapper exists (~/jev-plugins/jev-pruner/dist/codex/run.js, built by
# jev-pruner-setup.sh) AND the loopback endpoint's /health answers "ok": true and the pinned revision within 3 s. Then this script execs the
# wrapper, which runs the command, archives its full stdout, and trims only a SUCCESSFUL command's long stdout; it
# fails open (the original output) on any error, including its fixed 30 s request deadline. Otherwise the command
# runs unchanged. Either way the command's exit code is this script's exit code.
#
# NOT a gate file and never run by one: pc-lane.sh (listed in scripts/gate_files.txt) neither names nor sources it,
# so the sieve stays outside every gate's process, not only outside its text (KC-J1; the never-a-gate screen).
# Test seams: PC_LANE_JEV_DIST, PC_LANE_JEV_HEALTH_URL, PC_LANE_JEV_NODE. TYPESAFE_API_KEY=local is a placeholder the
# loopback endpoint ignores, not a credential.
set -u
[ "${1:-}" = "--" ] && shift
[ "$#" -gt 0 ] || { echo "long-output: usage: long-output.sh -- <command> [args...]" >&2; exit 64; }

dist="${PC_LANE_JEV_DIST:-$HOME/jev-plugins/jev-pruner/dist/codex/run.js}"
health_url="${PC_LANE_JEV_HEALTH_URL:-http://127.0.0.1:47411/health}"
node_bin="${PC_LANE_JEV_NODE:-node}"
# Identity, not just liveness (AF-AP-33): the endpoint must report the pinned checkpoint revision.
want_rev="${PC_LANE_JEV_REVISION:-1c5edc17a7acd8701df6fc341c0d179f1c62c982}"

if [ ! -f "$dist" ]; then
  echo "long-output: pruner OFF (no wrapper)" >&2
elif ! command -v "$node_bin" >/dev/null 2>&1; then
  echo "long-output: pruner OFF (no node)" >&2
else
  health="$(curl -s -m 3 "$health_url" 2>/dev/null || true)"
  case "$health" in
    *'"ok": true'*|*'"ok":true'*) ;;
    *) health="" ;;
  esac
  case "$health" in
    *"\"revision\": \"$want_rev\""*|*"\"revision\":\"$want_rev\""*)
      thread="${LANE_ID:-}"
      [ -n "$thread" ] || { [ -n "${LANE_REPORT_DRAFT:-}" ] && thread="$(basename "$(dirname "$LANE_REPORT_DRAFT")")"; }
      export JEV_BASE_URL="${health_url%/health}/v1/systemone" TYPESAFE_API_KEY="local" CODEX_THREAD_ID="${thread:-long-output}"
      echo "long-output: pruner ON" >&2
      exec "$node_bin" "$dist" -- "$@" ;;
  esac
  echo "long-output: pruner OFF (endpoint not healthy or not the pinned revision)" >&2
fi
exec "$@"
