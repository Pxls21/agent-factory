#!/bin/bash
# Startup orientation — the owner's three-layer hybrid (directive 2026-08-28):
#   1. CHAT (intent):   read the transcript raw — what was said/decided last.
#   2. COMMITS (delta): what files the last commits actually touched.
#   3. GRAFT (wiring):  connect the dots — ask graft about the touched areas.
# Layers 1-2 are mechanical and printed here, bounded. Layer 3 needs judgment:
# this script prints READY-TO-RUN `graft ask` suggestions per touched area; the
# agent runs the ones that matter BEFORE resuming work there. Runs at every
# session start (hooked from .claude/hooks/session-start.sh) and on demand.
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || echo .)}" || exit 0

N_COMMITS="${1:-12}"
BR="${ORIENT_BRANCH:-$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)}"

echo "── orient: layer 0 — QUARTET (which instruments are live in THIS container) ──"
# Owner directive 2026-08-28: every restart resumes with the full code-intel
# quartet visible "right on your face". MCP registrations only bind NEXT
# session — these are the SAME-SESSION paths (code-intel-trio skill = usage).
echo "  graft:        $( [ -f graft/INDEX.md ] && echo "OK (graft ask/skeleton/callers)" || echo "INDEX ABSENT — 'graft build' backgrounds ~7min; fallback: GitNexus/grep, NAME it" )"
echo "  gitnexus:     $( [ -f .gitnexus/run.cjs ] && echo "OK (node .gitnexus/run.cjs impact/detect_changes)" || echo "ABSENT — npx gitnexus analyze" )"
echo "  cbm:          $( [ -x /root/.local/bin/codebase-memory-mcp ] && echo "OK (binary; stdio search_graph/query_graph)" || echo "ABSENT" )"
echo "  crg:          $( [ -x /root/venv-crg/bin/code-review-graph ] && echo "OK (/root/venv-crg/bin/code-review-graph query callers_of/tests_for)" || echo "ABSENT" )"

echo ""
echo "── orient: layer 1 — CHAT (intent) ──"
TR=$(ls -t /root/.claude/projects/-home-user-agent-factory/*.jsonl 2>/dev/null | head -1)
if [ -n "$TR" ] && [ -f "scripts/chat_tail.py" ]; then
  PY=$(command -v python3 || echo /root/venv-agent-factory/bin/python)
  "$PY" scripts/chat_tail.py "$TR" --turns 6 --day "$(date -u +%F)" 2>/dev/null \
    | head -40 || echo "(chat_tail failed — read the transcript manually: $TR)"
  echo "(deeper: scripts/chat_tail.py $TR --turns 20; semantic: --export <dir> then Read the day file)"
else
  echo "(no transcript found on this disk — sibling-session recovery: wiki live-state + origin commits)"
fi

echo ""
echo "── orient: layer 2 — COMMITS (what moved) ──"
git fetch origin $BR -q 2>/dev/null
echo "origin tip: $(git log --oneline -1 origin/$BR 2>/dev/null || echo unknown)"
echo "local  tip: $(git log --oneline -1 2>/dev/null)  (dirty files: $(git status --porcelain 2>/dev/null | wc -l))"
git log --oneline -"$N_COMMITS" origin/$BR 2>/dev/null | sed 's/^/  /'
echo "touched files (last $N_COMMITS commits, by touch count):"
git log --name-only --format= -"$N_COMMITS" origin/$BR 2>/dev/null \
  | grep -v '^$' | sort | uniq -c | sort -rn | head -12 | sed 's/^/  /'

echo ""
echo "── orient: layer 3 — GRAFT (connect the dots; agent runs these) ──"
if [ -f "graft/INDEX.md" ]; then
  # Per top touched PRODUCTION file (tests/docs/wiki excluded): skeleton is
  # deterministic (always yields the file's API); ask needs CONTENT words —
  # a generic meta-phrase returns empty (measured 2026-08-28), so the real
  # questions come from the agent's own confusion after layers 1-2.
  git log --name-only --format= -"$N_COMMITS" origin/$BR 2>/dev/null \
    | grep -E '^(proofs|spikes|scripts|src)/.*\.py$' | grep -v '/tests/' \
    | sort | uniq -c | sort -rn | head -5 \
    | awk '{print "  graft skeleton " $2 "   # then: graft callers <symbol> on anything surprising"}'
  echo "  (per area of confusion: graft ask \"<content words from the commits/chat>\" --source --in <dir>)"
else
  echo "  graft/INDEX.md ABSENT — named fallback: GitNexus impact / bare grep until 'graft build' completes"
fi
echo "── orient done — now the three-clock verify before any resumed work ──"
