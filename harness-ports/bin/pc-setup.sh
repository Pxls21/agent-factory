#!/usr/bin/env bash
# pc-setup.sh — bring the PC up as the BUILD host for Hermes lanes (owner ruling 2026-09-03).
# The PC-side sibling of scripts/setup.sh: user-level, no sudo, idempotent, tolerant (an
# optional install that fails WARNs and the script continues). Mirrors what the sandbox
# session-start rebuilds, at PC paths:
#   AF_REPO   clone of this repo                default $HOME/agent-factory
#   AF_VENV   project venv (pyflakes/pytest/aleph) default $HOME/venv-agent-factory
#   CRG_VENV  code-review-graph venv           default $HOME/venv-crg
# Heavy index builds (gitnexus analyze, graft build) run DETACHED at the end — they outlive
# any bridge call; watch $AF_REPO/.lanes/pc-setup.log and the two index logs.
# Run it over the bridge detached:  nohup bash harness-ports/bin/pc-setup.sh > .lanes/pc-setup.log 2>&1 &
set -uo pipefail
: "${AF_REPO:=$HOME/agent-factory}"; : "${AF_VENV:=$HOME/venv-agent-factory}"; : "${CRG_VENV:=$HOME/venv-crg}"
export DO_NOT_TRACK=1
ok()   { echo "  ✓ $*"; }
warn() { echo "  ⚠ $*"; }
say()  { echo "== $* =="; }
PY311="$(command -v python3.11 || command -v python3)"
mkdir -p "$AF_REPO/.lanes" "$HOME/.local/bin"
cd "$AF_REPO" || { echo "no clone at $AF_REPO" >&2; exit 1; }
echo "pc-setup start $(date -u +%FT%TZ) on $(hostname) repo=$AF_REPO head=$(git log -1 --format=%h)"

say "git hooks"
git config core.hooksPath scripts/hooks && ok "core.hooksPath=scripts/hooks"

say "project venv ($AF_VENV)"
[ -x "$AF_VENV/bin/python" ] || "$PY311" -m venv "$AF_VENV" || warn "venv create failed"
if [ -x "$AF_VENV/bin/python" ]; then
  "$AF_VENV/bin/pip" install -q --upgrade pip >/dev/null 2>&1
  "$AF_VENV/bin/pip" install -q pyflakes pytest "mcp==1.29.1" >/dev/null 2>&1 && ok "pyflakes pytest mcp==1.29.1" || warn "base pip install failed"
  "$AF_VENV/bin/pip" install -q -e "$AF_REPO/sandbox-kit/aleph[mcp]" >/dev/null 2>&1 && ok "aleph (editable, [mcp])" || warn "aleph install failed"
  "$AF_VENV/bin/python" -c "from mcp.server.fastmcp import FastMCP" 2>/dev/null && ok "mcp v1 API present" || warn "mcp v1 API missing — aleph MCP server will not start"
fi

say "node tools (npm prefix $(npm config get prefix 2>/dev/null))"
command -v gitnexus >/dev/null 2>&1 || { npm i -g --ignore-scripts gitnexus@1.6.10 >/dev/null 2>&1 && npm rebuild -g @ladybugdb/core >/dev/null 2>&1; }
command -v gitnexus >/dev/null 2>&1 && ok "gitnexus $(gitnexus --version 2>/dev/null | head -1)" || warn "gitnexus not installed"
command -v graft >/dev/null 2>&1 || npm install -g @nanonets/graft@0.16.0 >/dev/null 2>&1
command -v graft >/dev/null 2>&1 && { graft telemetry disable >/dev/null 2>&1; ok "graft $(graft --version 2>/dev/null | head -1)"; } || warn "graft not installed"

say "codebase-memory-mcp (prebuilt)"
if [ -x "$HOME/.local/bin/codebase-memory-mcp" ]; then ok "binary present"
elif [ -f "$AF_REPO/sandbox-kit/codebase-memory-mcp/install.sh" ]; then
  bash "$AF_REPO/sandbox-kit/codebase-memory-mcp/install.sh" --dir="$HOME/.local/bin" >/dev/null 2>&1 && ok "installed" || warn "prebuilt install failed"
else warn "no install.sh"; fi

say "code-review-graph ($CRG_VENV)"
[ -x "$CRG_VENV/bin/code-review-graph" ] || { "$PY311" -m venv "$CRG_VENV" && "$CRG_VENV/bin/pip" install -q code-review-graph >/dev/null 2>&1; }
[ -x "$CRG_VENV/bin/code-review-graph" ] && ok "present" || warn "install failed"

say "ouroboros (uv tool)"
command -v ouroboros >/dev/null 2>&1 || uv tool install ouroboros-ai==0.53.0 >/dev/null 2>&1
if command -v ouroboros >/dev/null 2>&1; then
  ok "ouroboros $(ouroboros --version 2>/dev/null | head -1)"
  OOO_PY="$HOME/.local/share/uv/tools/ouroboros-ai/bin/python"
  [ -x "$OOO_PY" ] && "$OOO_PY" "$AF_REPO/scripts/patch_ouroboros.py" >/dev/null 2>&1 && ok "patches applied" || warn "patch_ouroboros skipped"
else warn "ouroboros not installed"; fi

say "harness-port checks"
bash harness-ports/bin/sync-skills.sh --check >/dev/null 2>&1 && ok "skills in sync" || warn "skills drift — run harness-ports/bin/sync-skills.sh"
"$PY311" harness-ports/bin/build-roles.py --check >/dev/null 2>&1 && ok "roles match" || warn "roles drift — run build-roles.py"

say "indexes (detached)"
if command -v gitnexus >/dev/null 2>&1 && [ ! -f .gitnexus/run.cjs ]; then
  ( flock -n 9 || exit 0; nohup gitnexus analyze > .lanes/gitnexus-analyze.log 2>&1 ) 9>.lanes/gitnexus-analyze.lock & ok "gitnexus analyze launched (.lanes/gitnexus-analyze.log)"
else ok "gitnexus index present or tool absent"; fi
if command -v graft >/dev/null 2>&1 && [ ! -f graft/INDEX.md ]; then
  ( flock -n 9 || exit 0; nohup graft build > .lanes/graft-build.log 2>&1 ) 9>.lanes/graft-build.lock & ok "graft build launched (.lanes/graft-build.log)"
else ok "graft index present or tool absent"; fi
echo "pc-setup done $(date -u +%FT%TZ)"
