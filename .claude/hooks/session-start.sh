#!/bin/bash
# SessionStart hook for agent-factory (Claude Code on the web).
#
# The web container is ephemeral — global installs vanish on reclaim — so every
# session must rebuild the toolchain: Ouroboros, GitNexus, graft, the council and
# wiki-compiler tools, codebase-memory MCP, and the aleph venv. scripts/setup.sh
# is the project's source of truth and is idempotent + tolerant (it warns rather
# than dying on an optional install), so it is safe to run at the start of every
# session and benefits from container caching after the first run.
set -uo pipefail

# Web-only: local dev manages its own toolchain.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

# The harness swaps any hook text over 10,000 characters for a 2 KB preview of its head (VERIFY-COORD-0924 F-L1-3,
# read from the running binary). Setup printed about 18 KB first, so the live-state below never reached the model at a
# compaction (18,836 characters at 2026-09-24 11:24Z). So: setup's output goes to a log and only its problem lines are
# shown; the live-state is its newest block; orientation is cut; the whole text stays under 9,000 characters.
# SYNCHRONOUS by design: the session waits (cold a few minutes, cached <30s), so the toolchain is ready first.
SETUP_LOG="${AF_SETUP_LOG:-/tmp/agent-factory-setup.log}"
# Cut to N characters, never inside a UTF-8 sequence (head -c counts bytes and can split one).
cut_chars() { python3 -c 'import sys; sys.stdout.write(sys.stdin.buffer.read().decode("utf-8", "replace")[:int(sys.argv[1])])' "$1"; }
OUT="$(mktemp)"
START=$(date +%s)
bash scripts/setup.sh > "$SETUP_LOG" 2>&1   # tolerant: a flaky optional install must never block the session
SETUP_RC=$?
{
  echo "▶ agent-factory setup: done in $(( $(date +%s) - START ))s, rc ${SETUP_RC}; full log ${SETUP_LOG}"
  # setup.sh marks a problem with warn() ("  ! <text>"); strip the colour codes first.
  sed 's/\x1b\[[0-9;]*m//g' "$SETUP_LOG" | grep -E '^  ! |Traceback|[Ee]rror:' | head -5 | cut -c1-200

  # WIKI-CONTINUITY: the live-state page's newest block at every start or compaction (the page holds the rest).
  if [ -f "wiki/topics/live-state.md" ]; then
    echo "── wiki live-state: the newest block (a map; verify before resuming in-flight work) ──"
    python3 .claude/hooks/wiki-context.py --live-block
    echo "── end live-state ──"
  fi

  # Three-layer startup orientation (chat history, last commits, graft), cut to its first 3,000 characters.
  if [ -x "scripts/orient.sh" ]; then
    bash scripts/orient.sh 2>/dev/null | head -80 | cut_chars 3000
    echo
  fi
} > "$OUT" 2>/dev/null
cut_chars 9000 < "$OUT"
rm -f "$OUT"

# Persist PYTHONPATH so pytest / tools resolve the project root without a manual prefix.
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo 'export PYTHONPATH="."' >> "$CLAUDE_ENV_FILE"
fi
exit 0
