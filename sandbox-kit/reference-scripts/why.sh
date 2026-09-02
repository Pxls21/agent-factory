#!/bin/bash
# why.sh — on-demand chronology of a file or function (owner directive
# 2026-08-25: "trace it back really easily"). The per-function histogram is
# COMPUTED from primary sources, never stored — git is the record, commit
# messages are the reasoning (house discipline), the ledgers carry the
# incidents. Zero drift by construction.
#
# Usage:
#   scripts/why.sh <file> [function_name]
#   scripts/why.sh trading/backtest/gate.py run_gate
set -euo pipefail
FILE="${1:?usage: why.sh <file> [function]}"
SYM="${2:-}"
N="${WHY_DEPTH:-12}"

echo "══ WHY: $FILE${SYM:+ :: $SYM} ══"

if [ -n "$SYM" ]; then
  echo "── edit chronology (git log -L, newest first, ${N} max) ──"
  # -L :funcname:file follows the function across edits; fall back to whole
  # file when the funcname regex finds nothing.
  git log -n "$N" --format="%h %ad %s" --date=short -L ":$SYM:$FILE" --no-patch 2>/dev/null \
    || git log -n "$N" --format="%h %ad %s" --date=short -- "$FILE"
else
  echo "── edit chronology (file, newest first, ${N} max) ──"
  git log -n "$N" --format="%h %ad %s" --date=short -- "$FILE"
fi

echo "── reasoning record of the LAST change (full commit body) ──"
if [ -n "$SYM" ]; then
  LAST=$(git log -n 1 --format="%H" -L ":$SYM:$FILE" --no-patch 2>/dev/null || true)
fi
LAST="${LAST:-$(git log -n 1 --format="%H" -- "$FILE")}"
git log -1 --format="%B" "$LAST" | sed 's/^/  /'

echo "── incident-log + findings + wiki mentions ──"
BASE="$(basename "$FILE")"
grep -rln --include="*.md" -e "$BASE"${SYM:+ -e "$SYM"} \
  docs/INCIDENT-LOG.md docs/research/findings/ wiki/ 2>/dev/null \
  | sed 's/^/  /' || echo "  (none)"

if [ -n "$SYM" ] && command -v gitnexus >/dev/null 2>&1; then
  echo "── current blast radius (gitnexus impact) ──"
  timeout 10 gitnexus impact "$SYM" 2>/dev/null \
    | python3 -c "import json,sys
try:
    t=sys.stdin.read(); d=json.loads(t[t.index('{'):])
    s=d.get('summary') or {}
    print(f\"  risk {d.get('risk')} · {s.get('direct','?')} direct callers · {s.get('processes_affected','?')} flows\")
except Exception: print('  (index unavailable — rebuilding or symbol unknown)')" \
    || echo "  (index unavailable)"
fi
