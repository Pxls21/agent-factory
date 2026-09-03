---
topic: infrastructure-and-tooling
last_compiled: 2026-09-03
---

# Infrastructure and Tooling — ephemeral container, hooks, ops scripts, quartet

## 1. Purpose [coverage: high -- 12 sources]

This topic covers the machinery that keeps the ephemeral Claude Code web container usable
session-to-session and the operating kit that enforces the project's development protocols. Three
concerns: (a) a SessionStart hook re-provisions the whole toolchain every session, (b)
code-intelligence tools ship multi-tier fallbacks for the flaky MCP environment, and (c) ops
scripts enforce branch rules, commit discipline, and push cleanliness.

Who depends on it: every build/verify/orchestration increment in the project. CLAUDE.md names
`scripts/setup.sh` as "the toolchain source of truth" and directs agents to
`sandbox-kit/OPERATING-GUIDE.md` for day-to-day rules.

## 2. Architecture [coverage: high -- 10 sources]

**Provisioning chain (session start --> ready toolchain):**
- [.claude/settings.json](.claude/settings.json) registers hooks: SessionStart
  (`session-start.sh`), PostToolUse (`edit-snapshot.py`, `graft-first-nag.py`), UserPromptSubmit
  (`wiki-context.py`), Stop (`turn-retro-gate.sh`)
- [.claude/hooks/session-start.sh](.claude/hooks/session-start.sh): runs
  `scripts/setup.sh`, `scripts/orient.sh`, injects wiki live-state and PYTHONPATH
- [scripts/setup.sh](scripts/setup.sh): git identity, Ouroboros install + patches,
  Council/wiki-compiler/honey install from vendored kit, codebase-memory binary, Python venv,
  MCP server registration at user scope (gitnexus, aleph, codebase-memory, ouroboros,
  phoenix-docs, graft)

**Git hooks** ([scripts/hooks/](scripts/hooks/)):
- **pre-commit**: pyflakes delta gate (new hits only, via `scripts/lint_delta.py`), shell syntax
  gate (`bash -n` on every staged `.sh`), anti-pattern screen
- **post-commit**: marks wiki stale (`.git/wiki-stale`), backgrounds graft + GitNexus reindex
- **pre-push**: model-identifier trailer gate (blocks `Co-Authored-By: Claude` /
  `Claude-Session:` lines from reaching origin), wiki-stale warning

**Ops scripts** ([scripts/](scripts/)):
- `push_clean.sh --no-delegates-live`: strips trailers, proves tree identity, pushes rev-parsed
  SHA (the ONLY push path)
- `safe_commit.sh -m "<msg>" <paths>`: stages ONLY named paths, refuses if anything else staged
- `orient.sh`: three-layer startup orientation (quartet liveness, chat intent, last commits)
- `resume-heal.sh`: mechanical fresh-container resume (ff-sync, hooks, venv, background reindex)
- `relaunch-suite.sh`: detached pytest run surviving the Bash cap
- `why.sh <file> [fn]`: on-demand chronology from primary sources
- `replay_transcript_edits.py`: recover dead delegate edits from transcripts
- `lint_delta.py`: the pyflakes delta gate (new hits only)
- `chat_tail.py`: transcript timestamps/intent extraction
- `patch_ouroboros.py`: upstream patches (ledger self-conflict, initial_context cap)
- `pc.sh '<command>'`: PC bridge helper (JSON-encode, X-Agent-Token, Connection: close, retry)
- `pc_lane.sh`: sandbox-side PC lane spawn coordinator

**Code-intelligence quartet** (owner mandate: USE RELIGIOUSLY):
- **Graft** (FIRST for all code questions): `graft ask "<question>"` before any grep
- **GitNexus** (3-tier: MCP --> stdio `scripts/gn_mcp.py` --> CLI `node .gitnexus/run.cjs`):
  `impact` before editing, `detect_changes` before committing
- **Codebase-memory** (prebuilt binary, MCP at user scope): `search_graph`, `query_graph`,
  `get_architecture`
- **code-review-graph** (venv binary): `callers_of`, `tests_for`, `impact --files`

**Edit-snapshot hook** (`edit-snapshot.py`, PostToolUse): every Edit/Write on `.py` auto-returns
enclosing symbol's GitNexus blast radius + anti-pattern registry screen.

## 3. Talks To [coverage: medium -- 5 sources]

- SessionStart hook --> setup.sh --> orient.sh --> wiki live-state injection
- pre-commit --> lint_delta.py, bash -n, AP screen
- post-commit --> graft build, GitNexus analyze (background)
- push_clean.sh --> filter-branch (trailer strip) --> git push
- edit-snapshot.py --> GitNexus impact, AP registry scan
- graft-first-nag.py --> reminds on code-path grep calls
- wiki-context.py --> relevance-matched wiki excerpts per prompt
- turn-retro-gate.sh --> retro checklist at turn-end

## 4. API Surface [coverage: medium -- 4 sources]

- `scripts/pc.sh '<cmd>'`: POST to `$PC_BRIDGE_URL/exec` with `X-Agent-Token` header
- GitNexus CLI: `impact`, `detect_changes`, `analyze`, `query`, `context`, `explain`
- Graft CLI: `graft ask`, `graft skeleton`, `graft build`
- Ouroboros stdio: `python scripts/ooo_mcp.py <tool> "<json_args>"`
- GitNexus stdio: `python scripts/gn_mcp.py <tool> "<json_args>"`

## 5. Data [coverage: medium -- 3 sources]

- Graft index: `graft/INDEX.md` (built by `graft build`, ~7 min cold)
- GitNexus index: `.gitnexus/` (15749 symbols, 35231 relationships, 784 execution flows)
- Ouroboros state: `~/.ouroboros/data/interview_*.json`, fanout registry
- Transcripts: `/root/.claude/projects/-home-user*/...jsonl` (primary source for session history)
- Wiki stale marker: `.git/wiki-stale` (set by post-commit, checked by pre-push)

## 6. Key Decisions [coverage: high -- 6 sources]

- Skills are the AUTHORITATIVE protocol expansions; CLAUDE.md is their operative index
- Graft-first mandate (owner, 2026-08-25): every semantic code question to graft before grep
- Edit-snapshot hook (owner, 2026-08-25): blast radius + AP screen on every edit
- Push only through `push_clean.sh --no-delegates-live` (no model identifiers reach origin)
- Coordinator commits through `safe_commit.sh` (never sweeps delegate staging)
- MCP servers registered at user scope by setup.sh (project-scope shows "Pending approval" in CCR)
- Ouroboros: always prefer stdio (`scripts/ooo_mcp.py`); native MCP broken (SDK v2 vs v1.x)
- DORMANT/reachability claims need TWO independent instruments
- Full GitNexus `analyze` outlives Bash cap (~3.8k files) -- run detached

## 7. Gotchas [coverage: high -- 8 sources]

**NOT-built (first-class):**
- Wiki compiled from planning docs, not code (this compile is the first)
- Telemetry sinks (OpenObserve, Phoenix) on the PC receive nothing from this project yet
- Harness ports unit-proven in sandbox only; NOT smoke-tested on the PC
- Ouroboros native MCP broken -- stdio fallback works
- `wiki-init` not yet run before this compile (no `.compile-state.json`)

**Known quirks (from CLAUDE.md and incident log):**
- Container cwd resets to `/home/user` after restart -- use absolute paths
- `rsync` absent in sandbox -- use `tar`/`cp -a`
- `git rev-parse --short REV1 REV2` fails in compound commands -- one per call
- `push_clean` races with GitNexus banner rewriter (AGENTS.md/CLAUDE.md index-stat churn)
- `pgrep -f` self-match kills the bridge shell -- use `[b]racket` pattern
- Ouroboros `initial_context` cap (~1.5k) poisons sessions if exceeded

**Anti-pattern registry:** AF-AP-3 (uncommitted work at dispatch boundary), AF-AP-5 (orphaned
lines past exit).

## 8. Sources

- [CLAUDE.md](CLAUDE.md)
- [scripts/setup.sh](scripts/setup.sh)
- [scripts/push_clean.sh](scripts/push_clean.sh)
- [scripts/pc.sh](scripts/pc.sh)
- [.claude/settings.json](.claude/settings.json)
- [.claude/hooks/session-start.sh](.claude/hooks/session-start.sh)
- [.claude/hooks/edit-snapshot.py](.claude/hooks/edit-snapshot.py)
- [scripts/hooks/pre-commit](scripts/hooks/pre-commit)
- [scripts/hooks/post-commit](scripts/hooks/post-commit)
- [scripts/hooks/pre-push](scripts/hooks/pre-push)
- [sandbox-kit/OPERATING-GUIDE.md](sandbox-kit/OPERATING-GUIDE.md)
- [sandbox-kit/VENDORED-FROM.md](sandbox-kit/VENDORED-FROM.md)
