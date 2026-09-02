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

# Timing + progress so both you and the agent know how long it took and that it
# finished. This hook is SYNCHRONOUS by design — the session waits for it — which
# is the right trade-off: it guarantees the toolchain is ready before any
# test/lint/MCP call, and the cost is bounded (cold a few minutes, cached <30s).
START=$(date +%s)
echo "▶ agent-factory setup: rebuilding toolchain (Ouroboros, GitNexus, graft, council/wiki, codebase-memory, aleph)."
echo "  SYNCHRONOUS — the session waits. Expect a few minutes on a cold container, <30s when cached."
bash scripts/setup.sh || true   # tolerant: a flaky optional install must never block the session
echo "✓ agent-factory setup done in $(( $(date +%s) - START ))s — session ready."

# WIKI-CONTINUITY: inject the turn-maintained live-state page at every session
# start/compaction resume, so the wiki — not transcript archaeology — is the
# first-read continuity source. Map, not gospel: verify state before resuming
# any in-flight work.
if [ -f "wiki/topics/live-state.md" ]; then
  echo "── wiki live-state (turn-maintained continuity snapshot; verify before resuming) ──"
  head -60 wiki/topics/live-state.md
  echo "── end live-state ──"
fi

# Three-layer startup orientation (chat history → last commits → graft), if the
# project has authored scripts/orient.sh.
if [ -x "scripts/orient.sh" ]; then
  bash scripts/orient.sh 2>/dev/null | head -80
fi

# Persist PYTHONPATH so pytest / tools resolve the project root without a manual prefix.
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo 'export PYTHONPATH="."' >> "$CLAUDE_ENV_FILE"
fi
exit 0
