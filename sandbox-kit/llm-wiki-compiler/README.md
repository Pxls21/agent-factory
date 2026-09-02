# llm-wiki-compiler (vendored)

Vendored from https://github.com/ussumant/llm-wiki-compiler (MIT, see LICENSE) at commit
`0f734fd3fba7dbc6a3b58efb4fb5fbaf7ce7565d` (v2.1, 2026-05). The `plugin/assets/` screenshots
(~5.3 MB) are excluded; everything functional is kept verbatim.

## What it is

A Claude Code plugin that compiles a codebase (or markdown knowledge base) into a topic-based
WIKI — synthesized articles about each subsystem with coverage badges, backlinks to sources, and
an interactive knowledge-graph visualizer. The Karpathy "LLM Knowledge Base" pattern: compile
once, then sessions read the INDEX + 2 articles (~330 lines) instead of re-reading raw files.
Complements GitNexus: GitNexus answers symbol-level questions (impact, callers, flows); the wiki
answers subsystem-level ones (what is this module FOR, how is everything wired, why built this way).

The "compiler" is the session agent itself following `plugin/skills/wiki-compiler/SKILL.md` +
`plugin/commands/*.md` — no external API, no extra cost beyond the session's own tokens.

## Install (auto-run by scripts/setup.sh)

`./install.sh` copies the commands into `~/.claude/commands/` and the skill into
`~/.claude/skills/wiki-compiler/`, rewriting `${CLAUDE_PLUGIN_ROOT}` to this vendored
`plugin/` directory's absolute path. Like the council, slash commands load NEXT session.

## Use

- `/wiki-init` — one-time config (`.wiki-compiler.json`; already committed for this repo,
  codebase mode → `wiki/`).
- `/wiki-compile` — recompile changed sources into the wiki (parallel subagents per topic).
- `/wiki-search <q>` / `/wiki-query <q>` — search / answer from the compiled wiki.
- `/wiki-lint` — health check (dead links, stale articles, coverage).
- `/wiki-visualize` — `node plugin/visualize/server.js --wiki-dir wiki` → interactive
  knowledge graph in the browser.

The compiled wiki for THIS repo lives at `wiki/` (committed — it is the browsable map of how
everything is wired). Keep it fresh: after a substantial subsystem change, run `/wiki-compile`.
