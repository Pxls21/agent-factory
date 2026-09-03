# Provenance

This `sandbox-kit/` tree was vendored wholesale from the portable operating kit at
**`pxls21/sandbox-kit` @ `aeb3082`** ("Refresh: full trading-system environment snapshot,
2026-09-02"), following that repo's own README manifest (PORTABLE + repo-root portables).

What was installed where in this repo:

| Source (pxls21/sandbox-kit) | Here | Notes |
|---|---|---|
| `dot-claude/` | `.claude/` | Skills (372), agents, workflows, hooks, `settings.json`. Adapted: `vectorbtpro` MCP entries removed; hook paths re-pointed (`/root/venv-agent-factory`, `agent_factory` package, `sandbox-kit/` exclusion); `session-start.sh` rewritten for this repo. |
| `example.mcp.json` | `.mcp.json` | `vectorbtpro` (trading-only) dropped; aleph re-pointed at `/root/venv-agent-factory/bin/aleph` with `ALEPH_WORKSPACE=/home/user/agent-factory`. Original preserved as `sandbox-kit/example.mcp.json`. |
| `scripts/gn_mcp.py`, `scripts/ooo_mcp.py` | `scripts/` | Self-contained stdio fallbacks — copied verbatim. |
| `scripts/setup.sh` | `sandbox-kit/reference-scripts/setup-trading-system.sh` | Worked example only; this repo's live `scripts/setup.sh` was authored fresh from it. |
| other `scripts/*` | `sandbox-kit/reference-scripts/` | Trading-repo worked examples — see the README there. |
| `CLAUDE.template.md` | `sandbox-kit/` + filled as root `CLAUDE.md` | Verbatim protocol text kept; placeholders filled for agent-factory. |
| portable docs, vendored tools, `output-styles/` | `sandbox-kit/` | `OPERATING-GUIDE`, `RESEARCH-PROMPT-GUIDE`, examples, `aleph/`, `codebase-memory-mcp/`, `council-of-high-intelligence/`, `llm-wiki-compiler/`, `docs/THIRD-PARTY-AGENT-TOOLS.md`. |

**Added 2026-09-03 (not in the kit snapshot):** `sandbox-kit/honey-for-devs/` — Green-PT/honey-for-devs
(shallow clone, main, 2026-09-03), vendored because the kit's curl-installer URL is blocked here;
its `skills/honey*` and `agents/hive-*.md` are also copied into `.claude/` so they load without any
install. `PC-BRIDGE.md` + `scripts/pc.sh` — the owner's PC bridge runbook, adapted from
`trading-system/docs/PC-BRIDGE-RUNBOOK.md` (the kit deliberately leaves bridge docs behind).

The source repo's PROJECT-SPECIFIC set (HERMES-VM, PC-bridge/thermal docs, ACTIVE-LINKS, the
filled trading `CLAUDE.md`) was deliberately left behind, per its manifest.
