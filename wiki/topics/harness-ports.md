---
topic: harness-ports
last_compiled: 2026-09-03
---

# Harness Ports — Codex CLI, Hermes Agent, PC-side spawn

## 1. Purpose [coverage: high -- 5 sources]

The owner is standing up a PC-side manager agent. The harness-ports subsystem carries this
project's full agent environment (rules, skills, hooks, agents, workflows, output styles, spawn
path) to the two harnesses that will run there: Codex CLI and Hermes Agent. An exact clone of
`.claude/` in spirit, not in mechanism -- the rules are identical, only mechanism names changed.

**Unit-proven in the sandbox; NOT smoke-tested on the PC.** What cannot be cloned is listed
honestly in the doc.

## 2. Architecture [coverage: high -- 4 sources]

**Deliverables** (from [docs/HARNESS-PORTS.md](docs/HARNESS-PORTS.md)):
- `AGENTS.md`: Codex CLI project instructions (includes the 15 standing rules verbatim)
- `.hermes.md`: Hermes project instructions
- `.agents/skills/<name>/SKILL.md`: all 382 ported skills (synced by `harness-ports/bin/sync-skills.sh`)
- `harness-ports/roles/`: 3 lane roles (code-implementer, adversarial-verifier, evidence-gatherer)
- `.codex/config.toml`: Codex hooks + MCP configuration
- `harness-ports/hermes/config-snippet.yaml`: Hermes hooks + MCP + provider (merge by hand)
- `harness-ports/bin/`: hook shim, payload adapters (Codex/Hermes), MCP launcher, smoke probe,
  role builder, spool reader, spawn path
- `scripts/pc_lane.sh`: sandbox-side PC lane spawn coordinator

**Spawn path:** `harness-ports/bin/pc-lane.sh` (PC-side, invoked over the bridge) takes a role,
task brief, and branch; sets up the Codex/Hermes session with the right role prepended and
the project's MCP servers connected.

**Skill sync:** `harness-ports/bin/sync-skills.sh` keeps `.agents/skills/` in sync with
`.claude/skills/` -- run after any skill change.

## 3. Talks To [coverage: medium -- 3 sources]

- `.claude/skills/` (source) --> `.agents/skills/` (synced mirror for Codex/Hermes)
- `scripts/pc_lane.sh` (sandbox) --> `harness-ports/bin/pc-lane.sh` (PC-side, over bridge)
- `harness-ports/bin/hook-shim.sh` --> pre-commit, post-commit, pre-push (shared logic)
- `harness-ports/bin/mcp-smoke.sh` --> MCP server liveness check (owner runs on PC)

## 4. API Surface [coverage: medium -- 3 sources]

- `pc_lane.sh <role> <brief> [branch]`: sandbox-side spawn (calls `pc.sh` with the PC-side script)
- `sync-skills.sh`: one-directional sync `.claude/skills/` --> `.agents/skills/`
- `mcp-smoke.sh`: acceptance probe for MCP server connectivity
- Bridge contract for lanes: `X-Agent-Token` + `{"cmd": "bash harness-ports/bin/pc-lane.sh ..."}` + `/exec`

## 5. Data [coverage: low -- 2 sources]

- `.codex/config.toml`: Codex project configuration
- `harness-ports/hermes/config-snippet.yaml`: Hermes merge fragment
- `harness-ports/roles/*.md`: role instruction files

## 6. Key Decisions [coverage: high -- 3 sources]

- Rules identical across all three harnesses (Claude Code, Codex, Hermes) -- AGENTS.md carries
  the 15 standing rules verbatim
- OmniRoute port corrected to verified `:20128` (the doc had inherited source repo's `:8317`)
- Trading-only `vectorbtpro` skill removed from both skill trees
- Batch D review: 5 silent except sites (AP-24) caught by the pre-commit delta gate on the
  wholesale port -- fixed fail-LOUD with stderr reason before each fallback
- Vendored trees excluded from lint_delta.py (class fix, not count fix)

## 7. Gotchas [coverage: high -- 4 sources]

**NOT-built (first-class):**
- NOT smoke-tested on the PC (no bridge banner this session for that test)
- Owner action required: merge Hermes config snippet, run MCP smoke probe, verify spawn path
- `AGENTS.md` and `.hermes.md` ports are the Codex/Hermes equivalents of CLAUDE.md -- but
  the harness lacks some Claude Code features (PostToolUse hooks work differently in Hermes;
  `turn-retro-gate.sh` may not trigger the same way)

**What is NOT identical** (stated first-class in `docs/HARNESS-PORTS.md`):
- PostToolUse hook timing differs between harnesses
- Hermes spool-reader is a workaround for edit-snapshot's PostToolUse model
- `turn-retro-gate.sh` (Stop hook) behavior is harness-dependent
- Wiki-context injection is harness-dependent

## 8. Sources

- [docs/HARNESS-PORTS.md](docs/HARNESS-PORTS.md)
- [AGENTS.md](AGENTS.md)
- [.codex/config.toml](.codex/config.toml)
- [scripts/pc_lane.sh](scripts/pc_lane.sh)
- [sandbox-kit/VENDORED-FROM.md](sandbox-kit/VENDORED-FROM.md)
