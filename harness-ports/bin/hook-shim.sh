#!/usr/bin/env bash
# Harness hook shim — ONE implementation of each project hook, reused by every harness.
#
# The five project hooks live in .claude/hooks/. Copying them per harness would
# guarantee drift: a fix would land in one copy and rot in the others. Instead each
# harness's hook config calls THIS shim, which:
#   1. resolves the repo root (hook cwd differs per harness and per session subdir),
#   2. exports CLAUDE_PROJECT_DIR, which the hook scripts already read,
#   3. execs the real hook with stdin/stdout/stderr and the exit code passed straight
#      through — the block contract (exit 2 + stderr) must survive the shim intact.
#
# Usage: hook-shim.sh <hook-file-name> [args...]
#   e.g. hook-shim.sh session-start.sh
#        hook-shim.sh wiki-context.py
#
# Exit codes are the hook's own. A shim failure exits 0 (never block a turn because
# the plumbing broke) EXCEPT that a missing hook file is reported on stderr — silence
# there would be a hook that "fires" and does nothing, which is a hollow green.
set -uo pipefail

HOOK_NAME="${1:-}"
if [ -z "$HOOK_NAME" ]; then
  echo "hook-shim: no hook name given" >&2
  exit 0
fi
shift

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$ROOT" ]; then
  # Not in a git work tree: fall back to this script's own location (…/harness-ports/bin).
  ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fi

HOOK="$ROOT/.claude/hooks/$HOOK_NAME"
if [ ! -f "$HOOK" ]; then
  echo "hook-shim: $HOOK not found — hook did NOT run" >&2
  exit 0
fi

export CLAUDE_PROJECT_DIR="$ROOT"
cd "$ROOT" || exit 0

case "$HOOK_NAME" in
  *.py) exec python3 "$HOOK" "$@" ;;
  *)    exec bash "$HOOK" "$@" ;;
esac
