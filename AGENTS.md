# Instructions for coding agents

These rules apply to the whole repository.

1. Hermes is the sole stock production workhorse. Do not add Codex CLI, Claude Code, Pi, or their ACP adapters as parallel runtimes.
2. ACP remains the v1 interface contract: `buzz-acp` launches Hermes through `hermes-acp`. Do not replace this path without an approved ADR.
3. OmniRoute is the sole model API egress. Do not add direct provider credentials to Hermes, GBrain, JIT, or any evaluator.
4. Do not enable the Codex app-server/OAuth path in v1. Use Hermes' `codex_responses` wire mode against the internal OmniRoute endpoint.
5. Retain the JIT Harness Foundry and GBrain-informed dream phase. They are isolated proposal/generation planes with no direct production write or execution authority.
6. HarnessRouter remains conditional: use it only for an approved generated or third-party UHP-only harness that cannot use ACP.
7. Treat `docs/archive/v2-original/` as read-only evidence. Update current documents instead.
8. Treat Fubuki packets as immutable, canonical, and hash-pinned for a session.
9. All effectful Hermes tools must pass a fail-closed `pre_tool_call` policy hook. A prompt instruction is not a security control.
10. Persistent memory writes start at their authorized logical scope. Upward promotion requires an explicit reviewed proposal. Do not expose delete or promotion tools to a model or generated harness.
11. Preserve sole egress, least privilege, non-root service users, secret separation, and gVisor containment in every deployment change.
12. Prefer deterministic evaluation before LLM-as-judge. Never let JIT, GBrain, AlphaEval, or rubric code share production credentials or host networking.
13. Every upstream dependency must be pinned by immutable commit or digest and recorded in `upstream.lock.yaml`.
14. Feature PRs must include tests for normal behavior, failure behavior, and the relevant security boundary.
15. Do not claim a service is runnable or production-ready until its executable acceptance gate passes.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **agent-factory** (15749 symbols, 35231 relationships, 784 execution flows).

> Index stale? Run `node .gitnexus/run.cjs analyze --index-only` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? Bootstrap with `npx`, `bunx`, or `pnpm dlx` — e.g. `bunx gitnexus@latest analyze` (npm 11 npx crash; #1939).

## Always Do

- **MUST run impact analysis before editing.** Use `impact({target: "symbolName", direction: "upstream"})` (MCP) or `node .gitnexus/run.cjs impact "symbolName" --direction upstream --repo .` (CLI fallback); report callers, processes, and risk. Never substitute grep for graph analysis.
- **MUST analyze graph changes before committing.** Use `detect_changes({scope: "all"})` (MCP) or `node .gitnexus/run.cjs detect-changes --scope all --repo .` (CLI fallback). `partial: true` or `truncated: true` is not a clean check — a zero means unseen, not unaffected; re-run it. For regression review: `detect_changes({scope: "compare", base_ref: "main"})` or `node .gitnexus/run.cjs detect-changes --scope compare --base-ref "main" --repo .`.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- **MUST treat `risk: UNKNOWN` as unresolved, not as low.** An empty caller set is not evidence the symbol is unused — it can also mean the callers are not resolvable by the index (plain-object property access, dynamic dispatch, cross-language calls). `impact` pairs `UNKNOWN` with a `riskNote` saying so. Confirm with a text search before treating the symbol as safe to change or delete; do not proceed on the strength of a zero.
- When exploring unfamiliar code, use `query({search_query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `context({name: "symbolName"})`.
- For security review, `explain({target: "fileOrSymbol"})` lists taint findings (source→sink flows; needs `analyze --pdg`).

## Never Do

- NEVER edit a function, class, or method before MCP/CLI impact analysis.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis, and never read `UNKNOWN` as an all-clear — it means the walk could not answer, which is the one verdict that requires confirming by other means.
- NEVER rename symbols with find-and-replace — use `rename` which understands the call graph.
- NEVER commit before MCP/CLI graph change analysis.

## Resources

| Resource | Use for |
| --- | --- |
| `gitnexus://repo/agent-factory/context` | Codebase overview, check index freshness |
| `gitnexus://repo/agent-factory/clusters` | All functional areas |
| `gitnexus://repo/agent-factory/processes` | All execution flows |
| `gitnexus://repo/agent-factory/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
| --- | --- |
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus-cli/SKILL.md` |
| Work in the Tests area (865 symbols) | `.claude/skills/gitnexus-area-tests/SKILL.md` |
| Work in the Pipeline area (762 symbols) | `.claude/skills/gitnexus-area-pipeline/SKILL.md` |
| Work in the Mcp area (422 symbols) | `.claude/skills/gitnexus-area-mcp/SKILL.md` |
| Work in the Repl area (364 symbols) | `.claude/skills/gitnexus-area-repl/SKILL.md` |
| Work in the Cypher area (177 symbols) | `.claude/skills/gitnexus-area-cypher/SKILL.md` |
| Work in the Store area (165 symbols) | `.claude/skills/gitnexus-area-store/SKILL.md` |
| Work in the Foundation area (156 symbols) | `.claude/skills/gitnexus-area-foundation/SKILL.md` |
| Work in the Cli area (147 symbols) | `.claude/skills/gitnexus-area-cli/SKILL.md` |
| Work in the Aleph area (143 symbols) | `.claude/skills/gitnexus-area-aleph/SKILL.md` |
| Work in the Ui area (108 symbols) | `.claude/skills/gitnexus-area-ui/SKILL.md` |
| Work in the Discover area (93 symbols) | `.claude/skills/gitnexus-area-discover/SKILL.md` |
| Work in the Semantic area (85 symbols) | `.claude/skills/gitnexus-area-semantic/SKILL.md` |
| Work in the Components area (76 symbols) | `.claude/skills/gitnexus-area-components/SKILL.md` |
| Work in the Scripts area (72 symbols) | `.claude/skills/gitnexus-area-scripts/SKILL.md` |
| Work in the Eso area (64 symbols) | `.claude/skills/gitnexus-area-eso/SKILL.md` |
| Work in the Repro area (54 symbols) | `.claude/skills/gitnexus-area-repro/SKILL.md` |
| Work in the Integrations area (41 symbols) | `.claude/skills/gitnexus-area-integrations/SKILL.md` |
| Work in the Watcher area (36 symbols) | `.claude/skills/gitnexus-area-watcher/SKILL.md` |
| Work in the Providers area (35 symbols) | `.claude/skills/gitnexus-area-providers/SKILL.md` |
| Work in the Sub_query area (27 symbols) | `.claude/skills/gitnexus-area-sub-query/SKILL.md` |

<!-- gitnexus:end -->
