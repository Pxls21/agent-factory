#!/usr/bin/env bash
# Relaunch the full sandbox test suite, detached (survives the Bash tool's
# 10-min cap and group-kills). Ported from trading-system; paths are this
# repo's (proofs/ spikes/ tests/). Log goes to the session scratchpad when
# present, else /tmp. Idempotent: refuses if a suite is already running.
set -u
if pgrep -f "[p]ytest proofs" >/dev/null; then
  echo "REFUSED: a suite is already running (pgrep '[p]ytest proofs')" >&2
  exit 1
fi
PY="${SUITE_PY:-/root/venv-agent-factory/bin/python}"
"$PY" -c "import pytest" 2>/dev/null || { echo "pytest missing — $PY -m pip install pytest" >&2; "$PY" -m pip install -q pytest; }
SCRATCH=$(ls -d /tmp/claude-0/*/*/scratchpad 2>/dev/null | head -1)
LOG="${SCRATCH:-/tmp}/suite_full_$(date -u +%m%d_%H%M).log"
setsid "$PY" -u -m pytest proofs/ spikes/ tests/ -q -p no:cacheprovider > "$LOG" 2>&1 < /dev/null &
disown
sleep 2
pgrep -f "[p]ytest proofs" >/dev/null && echo "suite launched — log: $LOG" || { echo "LAUNCH FAILED (or finished instantly) — read $LOG" >&2; exit 1; }
