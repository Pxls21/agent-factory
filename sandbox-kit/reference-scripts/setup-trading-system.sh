#!/usr/bin/env bash
# trading-system environment setup — re-run every ephemeral session.
#
# Installs: Ouroboros (binary + patches + MCP + skills), Council of High Intelligence,
# llm-wiki-compiler, Codebase Memory MCP, git identity, ValueCell env (uv sync +
# bun install). Idempotent and tolerant — warns on optional failures, never
# blocks the session.
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

# Apply patches (P1: ledger self-conflict, P2: interview context cap).
# Must run BEFORE the MCP server starts (server loads constants at import).
if command -v ouroboros &>/dev/null && [ -f "$REPO_ROOT/scripts/patch_ouroboros.py" ]; then
  OOO_PY="$(head -1 "$(command -v ouroboros)" 2>/dev/null | sed 's/^#!//' | tr -d '[:space:]')" || true
  if [ -z "$OOO_PY" ] || [ ! -x "$OOO_PY" ]; then
    # Fallback: uv-tool default location
    OOO_PY="/root/.local/share/uv/tools/ouroboros-ai/bin/python"
  fi
  if [ -x "$OOO_PY" ]; then
    "$OOO_PY" "$REPO_ROOT/scripts/patch_ouroboros.py" \
      && ok "ouroboros patches applied" \
      || warn "ouroboros patches failed (version changed?)"
  else
    warn "could not find ouroboros python interpreter for patching"
  fi
fi

# Register Ouroboros MCP server (local binary, not uvx — see OUROBOROS-SETUP.md §8).
# MCP tools only load on NEXT session start, but registration is idempotent.
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

# --- Honey (Green-PT/honey-for-devs) — token-efficiency skill + hive agents ----
# The SWARM ORCHESTRATION & HONEY section of CLAUDE.md is distilled from this
# repo; installing it wires the actual `honey` skill, the `/honey` command, the
# SessionStart hook, the hive-scout/builder/reviewer subagents, and the eco
# (EcoLogits) meter. Installs to /root/.claude (ephemeral), so re-run per session.
say "Honey (honey-for-devs)"
if command -v node >/dev/null 2>&1; then
  curl -fsSL https://raw.githubusercontent.com/Green-PT/honey-for-devs/main/install.sh 2>/dev/null \
    | bash -s -- --yes --only claude >/dev/null 2>&1 \
    && ok "honey@greenpt installed (skill + /honey + hive agents + eco + statusline)" \
    || warn "honey install failed (network?) — CLAUDE.md honey rules still apply regardless"
else
  warn "node not on PATH — skipping honey install (CLAUDE.md honey rules still apply)"
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

# code-review-graph: own venv (deps clash with venv-trading). Index build is
# LAZY (first use, ~3.5 min) — never at session start.
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

# --- Python venv (trading deps) -----------------------------------------------
say "Python venv"
VENV_PY="/root/venv-trading/bin/python"
if [ -d "/root/venv-trading" ]; then
  ok "venv-trading exists"
else
  warn "venv-trading not found — creating (python3.11 -m venv /root/venv-trading)"
  if command -v python3.11 &>/dev/null; then
    python3.11 -m venv /root/venv-trading 2>&1 && ok "venv-trading created" \
      || warn "venv-trading creation failed"
  else
    warn "python3.11 not found — cannot create venv-trading; vectorbtpro MCP and aleph will not work"
  fi
fi

if [ -x "$VENV_PY" ]; then
  # Phase-0 dependency set: standalone manifest, never the poisoned repo-root requirements.txt.
  if "$VENV_PY" -m pip install -q -r "$REPO_ROOT/scripts/requirements-phase0.txt" 2>&1; then
    ok "phase-0 deps installed (scripts/requirements-phase0.txt)"
  else
    warn "phase-0 deps install failed — venv may be degraded"
  fi

  # Vendored vectorbtpro: fresh containers lose the editable install (bit 2026-08-24 —
  # smoke gate EXIT 3 on every resume until reinstalled). Import check from a neutral
  # cwd so a repo-root shadow can't fake a pass.
  if (cd /tmp && "$VENV_PY" -c "import vectorbtpro" 2>/dev/null); then
    ok "vectorbtpro importable"
  else
    "$VENV_PY" -m pip install -q -e "$REPO_ROOT/vectorbtpro-new" --no-deps 2>&1 \
      && ok "vectorbtpro installed editable (vectorbtpro-new)" \
      || warn "vectorbtpro editable install failed — smoke gate will fail"
  fi

  # MCP-SDK v1 pin for the two venv-trading MCP servers (vectorbtpro.mcp_server + aleph):
  # both import `mcp.server.fastmcp`, which mcp>=2 removed. An unpinned venv drifted to
  # 2.1.1 (2026-09-01) and BOTH servers died at import (CONNECT_TIMEOUT in the harness).
  # Nothing else in venv-trading requires mcp (`pip show mcp` → Required-by: empty).
  if ! "$VENV_PY" -c "from mcp.server.fastmcp import FastMCP" 2>/dev/null; then
    "$VENV_PY" -m pip install -q "mcp==1.29.1" 2>&1 \
      && ok "mcp pinned to 1.29.1 (v1 API for vectorbtpro/aleph MCP servers)" \
      || warn "mcp==1.29.1 install failed — vectorbtpro and aleph MCP servers will not start"
  else
    ok "mcp v1 API present"
  fi

  # Aleph MCP server (.mcp.json → /root/venv-trading/bin/aleph): editable from the vendored
  # source so the served version is the one in the tree (sandbox-kit/aleph, aleph-rlm 0.9.4).
  # Never installed before 2026-09-01 — the .mcp.json entry was ENOENT every session.
  if [ -x /root/venv-trading/bin/aleph ]; then
    ok "aleph present"
  else
    "$VENV_PY" -m pip install -q -e "$REPO_ROOT/sandbox-kit/aleph[mcp]" 2>&1 \
      && ok "aleph installed editable (sandbox-kit/aleph)" \
      || warn "aleph editable install failed — aleph MCP server will not start"
  fi

  # Drift visibility: log actually-resolved top-level versions every session.
  RESOLVED_VERSIONS="$("$VENV_PY" - <<'PYEOF' 2>/dev/null
import importlib.metadata as md
names = ["hmmlearn", "pymoo", "stumpy", "matplotlib", "pytest", "pytest-cov"]
out = []
for n in names:
    try:
        out.append(f"{n}={md.version(n)}")
    except Exception:
        out.append(f"{n}=MISSING")
print(" ".join(out))
PYEOF
)"
  if [ -n "$RESOLVED_VERSIONS" ]; then
    ok "resolved versions: $RESOLVED_VERSIONS"
  else
    warn "could not determine resolved dependency versions"
  fi

  # Phase-0 smoke gate: warn-not-block, never aborts the session.
  if [ -f "$REPO_ROOT/scripts/smoke_phase0.py" ]; then
    "$VENV_PY" "$REPO_ROOT/scripts/smoke_phase0.py"
    SMOKE_RC=$?
    if [ "$SMOKE_RC" -eq 0 ]; then
      ok "phase-0 smoke gate passed"
    else
      warn "PHASE-0 SMOKE GATE FAILED — environment degraded, exit code $SMOKE_RC"
    fi
  else
    warn "scripts/smoke_phase0.py not found — skipping phase-0 smoke gate"
  fi
else
  warn "venv-trading python not executable — skipping phase-0 dep install and smoke gate"
fi

# --- ValueCell (frontend + python subsystem) ----------------------------------
say "ValueCell"
if [ -f "$REPO_ROOT/valuecell/python/pyproject.toml" ]; then
  if command -v uv &>/dev/null; then
    if (cd "$REPO_ROOT/valuecell/python" && uv sync 2>&1); then
      ok "valuecell/python deps installed (uv sync)"
    else
      warn "valuecell/python uv sync failed"
    fi
  else
    warn "uv not found — skipping valuecell/python (uv sync)"
  fi
else
  warn "valuecell/python/pyproject.toml not found — skipping valuecell/python provisioning"
fi

if [ -f "$REPO_ROOT/valuecell/frontend/package.json" ]; then
  if command -v bun &>/dev/null; then
    if (cd "$REPO_ROOT/valuecell/frontend" && bun install 2>&1); then
      ok "valuecell/frontend deps installed (bun install)"
    else
      warn "valuecell/frontend bun install failed"
    fi
  else
    warn "bun not found — skipping valuecell/frontend (bun install)"
  fi
else
  warn "valuecell/frontend/package.json not found — skipping valuecell/frontend provisioning"
fi

# --- Graft (NanoNets context graph — owner-adopted 2026-08-24) ------------------
# Local tree-sitter code graph + linked-markdown repo map; core is $0/no-key/no-network.
# Provenance: docs/THIRD-PARTY-AGENT-TOOLS.md. graft/ is a regenerable local cache
# (gitignored), so every cold container rebuilds it — in the BACKGROUND, never blocking.
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
    ok "graft build launched in background (log: /tmp/graft-build.log; ~7 min cold)"
  else
    ok "graft graph present (graft/INDEX.md); refresh with 'graft build' if stale"
  fi
else
  warn "graft not on PATH — skipping graph build and MCP registration"
fi

# --- Git hooks (HOOKS-QUARTET, owner directive 2026-08-25) ---------------------
# post-commit: background graft build + gitnexus analyze (lock-guarded) + wiki
# staleness marker; pre-push: wiki-freshness warn/block gate.
if [ -d "$REPO_ROOT/scripts/hooks" ]; then
  (cd "$REPO_ROOT" && git config core.hooksPath scripts/hooks) \
    && ok "git hooks active (scripts/hooks: quartet auto-reindex + wiki gate)" \
    || warn "git hooks activation failed"
fi

# --- Output styles (attention-span, vendored: sandbox-kit/output-styles) -------
# Chat-format styles for Claude Code (answer-first / spartan / rundown).
# Install = copy; activation stays a per-session/user choice (/output-style).
if [ -d "$REPO_ROOT/sandbox-kit/output-styles" ]; then
  mkdir -p "$HOME/.claude/output-styles"
  cp -f "$REPO_ROOT"/sandbox-kit/output-styles/*.md "$HOME/.claude/output-styles/" 2>/dev/null \
    && say "output-styles installed (attention-kind / spartan / rundown)" \
    || warn "output-styles copy failed"
fi

say "Done."
