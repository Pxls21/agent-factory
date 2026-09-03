#!/usr/bin/env bash
# agent-factory environment setup — re-run every ephemeral session.
#
# Derived from the sandbox-kit reference pattern
# (sandbox-kit/reference-scripts/setup-trading-system.sh) with the trading-only
# pieces removed. Installs: Ouroboros (binary + MCP registration), Council of
# High Intelligence, llm-wiki-compiler, Codebase Memory MCP, GitNexus, honey,
# graft, code-review-graph, the aleph venv, output styles, git identity.
# Idempotent and tolerant — warns on optional failures, never blocks the session.
#
# When the implementation stack lands (Hermes adapters, policy gate, buzz-acp —
# see docs/07_BUILD_PLAN.md), add its real toolchain here: this file is the
# toolchain source of truth referenced by CLAUDE.md and the SessionStart hook.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

say()  { printf '\n\033[1;34m◆ %s\033[0m\n' "$*"; }
ok()   { printf '  \033[1;32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[1;33m!\033[0m %s\n' "$*"; }

# Git identity — container restarts wipe local config.
git -C "$REPO_ROOT" config user.email noreply@anthropic.com 2>/dev/null || true
git -C "$REPO_ROOT" config user.name  Claude 2>/dev/null || true

# --- Ouroboros ----------------------------------------------------------------
say "Ouroboros"

if command -v ouroboros &>/dev/null; then
  ok "ouroboros already installed: $(ouroboros --version 2>/dev/null || echo 'unknown version')"
else
  say "Installing Ouroboros..."
  if uv tool install ouroboros-ai==0.53.0 2>&1; then
    # Refresh PATH for this script (uv installs to ~/.local/bin)
    export PATH="$HOME/.local/bin:$PATH"
    if command -v ouroboros &>/dev/null; then
      ok "ouroboros installed: $(ouroboros --version 2>/dev/null || echo 'unknown version')"
    else
      warn "ouroboros install ran but binary not on PATH"
    fi
  else
    warn "ouroboros install failed (network?)"
  fi
fi

# Apply the vendored Ouroboros patches (ported from trading-system, scripts/patch_ouroboros.py):
# P1 ledger self-conflict tie-break, P2 interview initial_context cap 3500 -> 10000.
# They patch the uv TOOL env (CLI + native `mcp serve`); the isolated-uvx fallback
# that scripts/ooo_mcp.py uses when native serve fails is a SEPARATE env and stays
# unpatched — keep initial_context short on that path (CLAUDE.md quirks).
if command -v ouroboros &>/dev/null && [ -f "$REPO_ROOT/scripts/patch_ouroboros.py" ]; then
  OOO_PY="$(head -1 "$(command -v ouroboros)" 2>/dev/null | sed 's/^#!//' | tr -d '[:space:]')" || true
  if [ -z "$OOO_PY" ] || [ ! -x "$OOO_PY" ]; then
    OOO_PY="/root/.local/share/uv/tools/ouroboros-ai/bin/python"
  fi
  if [ -x "$OOO_PY" ]; then
    "$OOO_PY" "$REPO_ROOT/scripts/patch_ouroboros.py" \
      && ok "ouroboros patches applied (ledger tie-break, interview cap 10000)" \
      || warn "ouroboros patches failed (version changed?)"
  else
    warn "could not find the ouroboros interpreter for patching"
  fi
fi

# Register Ouroboros MCP server (local binary, not uvx — see
# sandbox-kit/OUROBOROS-SETUP.md §8). MCP tools only load on NEXT session
# start, but registration is idempotent. The stdio fallback
# (scripts/ooo_mcp.py) works immediately either way.
if command -v ouroboros &>/dev/null && command -v claude &>/dev/null; then
  claude mcp remove ouroboros --scope user 2>/dev/null || true
  claude mcp add ouroboros --scope user -- ouroboros mcp serve 2>/dev/null \
    && ok "ouroboros MCP server registered (tools load on next session start)" \
    || warn "ouroboros MCP registration failed"
fi

# --- Council of High Intelligence (/council) --------------------------------
say "Council of High Intelligence"
if [ -f "$REPO_ROOT/sandbox-kit/council-of-high-intelligence/install.sh" ]; then
  bash "$REPO_ROOT/sandbox-kit/council-of-high-intelligence/install.sh" >/dev/null 2>&1 \
    && ok "/council installed" \
    || warn "council install failed"
else
  warn "sandbox-kit/council-of-high-intelligence/install.sh not found — skipping"
fi

# --- llm-wiki-compiler (codebase wiki) ---------------------------------------
say "llm-wiki-compiler"
if [ -f "$REPO_ROOT/sandbox-kit/llm-wiki-compiler/install.sh" ]; then
  bash "$REPO_ROOT/sandbox-kit/llm-wiki-compiler/install.sh" >/dev/null 2>&1 \
    && ok "/wiki-* installed" \
    || warn "wiki-compiler install failed"
else
  warn "sandbox-kit/llm-wiki-compiler/install.sh not found — skipping"
fi

# --- Honey (Green-PT/honey-for-devs) — VENDORED, installs offline -------------
# The SWARM ORCHESTRATION & HONEY section of CLAUDE.md is grounded against this
# tool. Source is vendored at sandbox-kit/honey-for-devs (skills + hive agents are
# ALSO committed under .claude/ so they load with no install at all). This block
# registers the vendored tree as a LOCAL plugin marketplace (no network — the
# raw.githubusercontent installer path is blocked in this sandbox), installs the
# plugin (the /honey command, SessionStart hook, eco meter), and wires the CO2
# statusline. Installs to /root/.claude (ephemeral), so re-run per session.
say "Honey (honey-for-devs, vendored)"
HONEY_SRC="$REPO_ROOT/sandbox-kit/honey-for-devs"
if [ -f "$HONEY_SRC/.claude-plugin/marketplace.json" ] && command -v claude >/dev/null 2>&1; then
  claude plugin marketplace add "$HONEY_SRC" >/dev/null 2>&1 || true   # idempotent: exists -> no-op
  if claude plugin install honey@greenpt >/dev/null 2>&1; then
    ok "honey@greenpt installed from the vendored local marketplace"
  else
    warn "honey plugin install failed — vendored skills/agents under .claude/ still load"
  fi
  if command -v node >/dev/null 2>&1; then
    node "$HONEY_SRC/bin/install.js" --yes --only claude >/dev/null 2>&1 || true   # statusline+eco; its GitHub marketplace step may fail harmlessly
    [ -f "$HOME/.claude/honey/statusline.js" ] && ok "honey statusline + eco meter wired" || warn "honey statusline not wired"
  fi
else
  warn "vendored honey source or claude CLI missing — skipping (CLAUDE.md honey rules still apply)"
fi

# --- Code-intel trio (skill: .claude/skills/code-intel-trio) ------------------
# codebase-memory-mcp: PREBUILT release install ONLY. The in-repo source build
# is impossible BY DESIGN (vendored C deps were never committed) — do not "fix"
# the make error; install.sh downloads the release binary.
say "Codebase Memory MCP"
if [ -x "/root/.local/bin/codebase-memory-mcp" ]; then
  ok "codebase-memory-mcp binary present"
elif [ -f "$REPO_ROOT/sandbox-kit/codebase-memory-mcp/install.sh" ]; then
  bash "$REPO_ROOT/sandbox-kit/codebase-memory-mcp/install.sh" --dir=/root/.local/bin >/dev/null 2>&1 \
    && ok "codebase-memory-mcp installed (prebuilt release)" \
    || warn "codebase-memory-mcp prebuilt install failed (network?)"
else
  warn "codebase-memory-mcp: no binary and no install.sh"
fi

# GitNexus: pinned global install (1.6.10). --ignore-scripts avoids the
# @ladybugdb/core postinstall network fetch racing npm's extract; the explicit
# rebuild then runs it once, deterministically.
say "GitNexus CLI"
if command -v gitnexus >/dev/null 2>&1 || [ -f "$REPO_ROOT/.gitnexus/run.cjs" ]; then
  ok "gitnexus present"
elif command -v npm >/dev/null 2>&1; then
  (npm i -g --ignore-scripts gitnexus@1.6.10 && npm rebuild -g @ladybugdb/core) >/dev/null 2>&1 \
    && ok "gitnexus@1.6.10 installed globally" \
    || warn "gitnexus install failed (network?)"
else
  warn "npm not on PATH — skipping gitnexus install"
fi

# code-review-graph: own venv (keep it isolated from the project venv). Index
# build is LAZY (first use) — never at session start.
say "code-review-graph"
if [ -x "/root/venv-crg/bin/code-review-graph" ]; then
  ok "code-review-graph venv present"
elif command -v python3 >/dev/null 2>&1; then
  (python3 -m venv /root/venv-crg && /root/venv-crg/bin/pip install -q code-review-graph) >/dev/null 2>&1 \
    && ok "code-review-graph installed (/root/venv-crg)" \
    || warn "code-review-graph install failed (network?)"
else
  warn "python3 not on PATH — skipping code-review-graph"
fi

# --- Python venv (aleph MCP + lint tooling) -----------------------------------
say "Python venv"
VENV_PY="/root/venv-agent-factory/bin/python"
if [ -d "/root/venv-agent-factory" ]; then
  ok "venv-agent-factory exists"
elif command -v python3 &>/dev/null; then
  python3 -m venv /root/venv-agent-factory 2>&1 && ok "venv-agent-factory created" \
    || warn "venv-agent-factory creation failed"
else
  warn "python3 not found — cannot create venv-agent-factory; aleph MCP will not work"
fi

if [ -x "$VENV_PY" ]; then
  # pyflakes powers the edit-snapshot hook's lint-delta tell.
  "$VENV_PY" -m pip install -q pyflakes pytest "jsonschema==4.25.1" "rfc3339-validator==0.1.4" 2>&1 \
    && ok "pyflakes installed (edit-snapshot hook lint delta)" \
    || warn "pyflakes install failed — edit-snapshot hook loses its pyflakes delta"

  # MCP-SDK v1 pin for the aleph MCP server: it imports `mcp.server.fastmcp`,
  # which mcp>=2 removed. An unpinned venv drifting to 2.x kills the server at
  # import (CONNECT_TIMEOUT in the harness).
  if ! "$VENV_PY" -c "from mcp.server.fastmcp import FastMCP" 2>/dev/null; then
    "$VENV_PY" -m pip install -q "mcp==1.29.1" 2>&1 \
      && ok "mcp pinned to 1.29.1 (v1 API for the aleph MCP server)" \
      || warn "mcp==1.29.1 install failed — aleph MCP server will not start"
  else
    ok "mcp v1 API present"
  fi

  # Aleph MCP server (.mcp.json → /root/venv-agent-factory/bin/aleph): editable
  # from the vendored source so the served version is the one in the tree
  # (sandbox-kit/aleph).
  if [ -x /root/venv-agent-factory/bin/aleph ]; then
    ok "aleph present"
  else
    "$VENV_PY" -m pip install -q -e "$REPO_ROOT/sandbox-kit/aleph[mcp]" 2>&1 \
      && ok "aleph installed editable (sandbox-kit/aleph)" \
      || warn "aleph editable install failed — aleph MCP server will not start"
  fi
else
  warn "venv-agent-factory python not executable — skipping aleph/pyflakes install"
fi

# --- Graft (NanoNets context graph) -------------------------------------------
# Local tree-sitter code graph + linked-markdown repo map; core is $0/no-key/
# no-network. Provenance: sandbox-kit/docs/THIRD-PARTY-AGENT-TOOLS.md. graft/ is
# a regenerable local cache (gitignored), so every cold container rebuilds it —
# in the BACKGROUND, never blocking.
say "Graft"
export DO_NOT_TRACK=1
if ! command -v graft &>/dev/null; then
  npm install -g @nanonets/graft@0.16.0 >/dev/null 2>&1 || warn "graft npm install failed (network?)"
fi
if command -v graft &>/dev/null; then
  ok "graft present: $(graft --version 2>/dev/null)"
  graft telemetry disable >/dev/null 2>&1 || true
  if command -v claude &>/dev/null; then
    claude mcp remove graft --scope user 2>/dev/null || true
    claude mcp add graft --scope user -- graft mcp "$REPO_ROOT" 2>/dev/null \
      && ok "graft MCP server registered (tools load on next session start)" \
      || warn "graft MCP registration failed"
  fi
  if [ ! -f "$REPO_ROOT/graft/INDEX.md" ]; then
    (cd "$REPO_ROOT" && nohup graft build >/tmp/graft-build.log 2>&1 &)
    ok "graft build launched in background (log: /tmp/graft-build.log)"
  else
    ok "graft graph present (graft/INDEX.md); refresh with 'graft build' if stale"
  fi
else
  warn "graft not on PATH — skipping graph build and MCP registration"
fi

# --- Project MCP servers at USER scope ----------------------------------------
# The .mcp.json (project-scope) servers sit at "Pending approval" in CCR sessions
# — nobody answers the prompt while the owner is away (2026-09-03) — so the same
# servers are registered at user scope, where they connect without one. Tools
# bind on the NEXT session start. codebase-memory (as codebase-memory-mcp), graft
# and ouroboros are registered by their own blocks above. `claude mcp list` then
# prints a "conflicting scopes" diagnostic for gitnexus (user entry absolute-pathed
# on purpose vs the relative project one) — cosmetic; both resolve to run.cjs.
if command -v claude &>/dev/null; then
  say "Project MCP servers (user scope)"
  if [ -f "$REPO_ROOT/.gitnexus/run.cjs" ]; then
    claude mcp remove gitnexus --scope user 2>/dev/null || true
    claude mcp add gitnexus --scope user -- node "$REPO_ROOT/.gitnexus/run.cjs" mcp 2>/dev/null \
      && ok "gitnexus MCP registered (user scope)" || warn "gitnexus MCP registration failed"
  else
    warn "gitnexus: .gitnexus/run.cjs absent (index still building?) — MCP registration skipped this run"
  fi
  if [ -x /root/venv-agent-factory/bin/aleph ]; then
    claude mcp remove aleph --scope user 2>/dev/null || true
    claude mcp add aleph --scope user -e ALEPH_WORKSPACE="$REPO_ROOT" -- /root/venv-agent-factory/bin/aleph --workspace-mode any --tool-docs concise 2>/dev/null \
      && ok "aleph MCP registered (user scope)" || warn "aleph MCP registration failed"
  fi
  claude mcp remove phoenix-docs --scope user 2>/dev/null || true
  claude mcp add --transport http phoenix-docs https://arizeai-433a7140.mintlify.app/mcp --scope user 2>/dev/null \
    && ok "phoenix-docs MCP registered (user scope)" || warn "phoenix-docs MCP registration failed"
fi

# --- Git hooks -----------------------------------------------------------------
# Activate repo-managed git hooks when the project authors them
# (scripts/hooks/: post-commit reindex, pre-push wiki gate — see the reference
# setup script for the trading repo's quartet pattern).
if [ -d "$REPO_ROOT/scripts/hooks" ]; then
  (cd "$REPO_ROOT" && git config core.hooksPath scripts/hooks) \
    && ok "git hooks active (scripts/hooks)" \
    || warn "git hooks activation failed"
fi

# --- Output styles (vendored: sandbox-kit/output-styles) -----------------------
# Chat-format styles for Claude Code (attention-kind / spartan / rundown).
# Install = copy; activation stays a per-session/user choice (/output-style).
# .claude/settings.json selects "Attention-kind" by default.
if [ -d "$REPO_ROOT/sandbox-kit/output-styles" ]; then
  mkdir -p "$HOME/.claude/output-styles"
  cp -f "$REPO_ROOT"/sandbox-kit/output-styles/*.md "$HOME/.claude/output-styles/" 2>/dev/null \
    && say "output-styles installed (attention-kind / spartan / rundown)" \
    || warn "output-styles copy failed"
fi

say "Done."
