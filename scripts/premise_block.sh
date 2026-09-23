#!/usr/bin/env bash
# premise_block.sh — print a brief's PREMISE measurements: every command read from stdin is echoed EXACTLY as it is run
# (`$ <command>`), then its output, then `[rc=N]` when it exits non-zero. The echoed line and the executed line are the same
# string, so a lane re-running the premise runs the command the author ran (VERIFY-J1-3 2026-09-23: a hand-typed echo line
# differed from the command run, and the commit list was measured before push_clean rewrote the SHAs — run this at the PIN,
# after the push).
# Usage: scripts/premise_block.sh < commands.txt      (one command per line; blank lines and lines starting with # skipped)
set -uo pipefail
while IFS= read -r cmd || [ -n "$cmd" ]; do
  case "$cmd" in ''|'#'*) continue;; esac
  printf '$ %s\n' "$cmd"
  bash -c "$cmd" 2>&1
  rc=$?
  [ "$rc" -eq 0 ] || printf '[rc=%s]\n' "$rc"
done
