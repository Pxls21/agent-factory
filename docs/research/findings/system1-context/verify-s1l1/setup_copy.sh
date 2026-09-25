#!/bin/bash
# Rebuild the VERIFY-S1-L1 scratch copies from the live tree (read-only on the tree): repo/ (hook, table, session-start,
# wiki-context, settings, wrapper, installer, the 19 corpus skills) and repo_m/ (the same plus the builder's test file,
# for mutate.py). Every reproduction script in this directory runs the registered command strings against these copies.
set -euo pipefail
S="$(cd "$(dirname "$0")" && pwd)"
A=/home/user/agent-factory
for R in "$S/repo" "$S/repo_m"; do
  rm -rf "$R"; mkdir -p "$R/.claude/hooks" "$R/scripts" "$R/.claude/skills"
  cp "$A"/.claude/hooks/{system1-context.py,system1-situations.json,session-start.sh,wiki-context.py} "$R/.claude/hooks/"
  cp "$A/.claude/settings.json" "$R/.claude/"
  cp "$A"/scripts/{hook_context.py,install_session_hooks.py} "$R/scripts/"
  python3 - "$A" "$R" <<'PY'
import json, os, shutil, sys
A, R = sys.argv[1], sys.argv[2]
t = json.load(open(f"{A}/.claude/hooks/system1-situations.json"))
for s in sorted({r["skill"] for r in t["rows"]} | set(t["prompt_corpus"])):
    os.makedirs(f"{R}/.claude/skills/{s}", exist_ok=True)
    shutil.copy2(f"{A}/.claude/skills/{s}/SKILL.md", f"{R}/.claude/skills/{s}/SKILL.md")
PY
done
mkdir -p "$S/repo_m/tests" && cp "$A/tests/test_system1_context.py" "$S/repo_m/tests/"
echo "rebuilt $S/repo and $S/repo_m"
