---
name: code-intel-trio
description: Use the three code-intelligence tools (GitNexus, codebase-memory, code-review-graph) together — which one for which question, exact CLI invocations that work in this container, bootstrap steps on a fresh container, and the two-instrument rule for dormancy claims. Load before any Phase-1 grounding, impact analysis, dead-wiring hunt, pre-commit check, or DORMANT/reachability claim.
---

> **HARNESS PORT.** This copy is read by Codex CLI (`.agents/skills/`) and by Hermes
> (via `skills.external_dirs`). It is the same protocol as `.claude/skills/code-intel-trio/SKILL.md`;
> only lines naming a Claude-Code-specific mechanism were reworded — see `docs/HARNESS-PORTS.md`.
> "the project instructions file" = `AGENTS.md` on Codex, `.hermes.md` on Hermes.
> Model-tier names below ("Fable light", "Opus 5 lane") are PROTOCOL LABELS, not routing
> instructions: these harnesses run ONE model. Where the protocol calls for an independent
> verifier, hand the work BACK to the sandbox lane — never self-accept.

# The code-intel trio — one map, three instruments

Owner mandate: mapping is a REFLEX, not an audit. Use these RELIGIOUSLY. Each has
a distinct strength; a serious claim uses at least two of them.

## Which tool for which question

| Question | Tool | Why |
|---|---|---|
| "What breaks if I change symbol X?" (BEFORE editing) | **GitNexus** `impact` | symbol-level, direction-aware (upstream/downstream), diff-scoped |
| "What did my edits touch?" (BEFORE every commit) | **GitNexus** `detect-changes` | the mandated pre-commit gate |
| "Who calls X / what does X call / tests for X?" | **code-review-graph** `query callers_of\|callees_of\|tests_for X` | fastest single-question answer, honest output |
| "Is seam X DORMANT (zero production callers)?" | **BOTH** crg `callers_of` AND cbm Cypher | two independent instruments — never claim DORMANT off one |
| Arbitrary structural query (fan-out, orphans, cross-file chains) | **codebase-memory** `query_graph` (Cypher) | full 60k-node graph incl. vendored vbt, real query language |
| "Map this subsystem / architecture overview" (Phase-1 grounding) | **codebase-memory** `get_architecture` + crg `architecture`/`communities` | complementary views |
| "Which files must a reviewer read for this diff?" | **code-review-graph** `impact --files ...` | file-level blast radius, built for review scoping |
| Fuzzy "where is the thing that does Y?" | **codebase-memory** `search_graph` (BM25) | ranked, qualified names returned |
| "Where is the seam for Y?" / one-file API surface / repo map (4th instrument, owner-adopted 2026-08-24) | **graft** `ask "<question>"` · `skeleton <file>` · `map` (CLI; MCP tools `graft_find_code`/`graft_trace_calls`/... next session) | local tree-sitter graph incl. vendored vbt; returns ranked symbols with exact file:line spans; $0/no-key. Cache `graft/` is gitignored + rebuilt per cold container by setup.sh (background, ~7 min — check `graft/INDEX.md` exists before relying on it). Provenance: docs/THIRD-PARTY-AGENT-TOOLS.md §Graft. |
| **GRAFT-FIRST RULE (owner mandate 2026-08-25)** | any SEMANTIC code question goes to `graft ask` (add `--source` for inline crux excerpts, `--in <path>` to scope) BEFORE bare grep | bare Grep remains correct only for literal-token sweeps (exact strings/env vars, non-code files) and as the NAMED fallback while `graft/INDEX.md` is absent -- never silently substitute grep for a graph query. SCOPE BOUNDARY (measured 2026-08-28, owner-requested A/B): graft indexes CODE only -- `graft build` on a 3.8MB markdown chat-history corpus parsed 0 of 0 files (language-grammar parsers; prose has no wiring) and `ask` returned empty. Chat-history/transcript questions go to `scripts/chat_tail.py` (+ `--export` and Read for semantic nuance -- session-continuity skill carries the rule), never to graft |

## Exact invocations that WORK here (quirks baked in)

### GitNexus (tier ladder: native MCP → stdio → CLI; prefer richest alive)
```bash
python scripts/gn_mcp.py --list                                    # tier 2 liveness
python scripts/gn_mcp.py impact '{"target":"<symbol>","direction":"upstream","summaryOnly":true}'
python scripts/gn_mcp.py detect_changes '{"scope":"compare","base_ref":"<pre-change-commit>"}'
node .gitnexus/run.cjs impact <symbol> --summary-only              # tier 3
node .gitnexus/run.cjs detect-changes -s compare -b <commit>
node .gitnexus/run.cjs status                                      # index freshness
```
- Quirk: stdio needs stdin kept OPEN across the async call — gn_mcp.py handles it;
  naive subprocess.run silently gets nothing.
- Stale index silently breaks impact on NEW symbols — `analyze` after adding modules.

### codebase-memory (binary: /root/.local/bin/codebase-memory-mcp; MCP on stdio or `cli` one-shots)
```bash
codebase-memory-mcp cli index_repository --repo-path /home/user/agent-factory   # after each landed increment
codebase-memory-mcp cli search_graph --project home-user-agent-factory --query "<free text>"
codebase-memory-mcp cli query_graph --project home-user-agent-factory \
  --query "MATCH (a)-[:CALLS]->(b {name: '<fn>'}) RETURN a.name, a.file_path LIMIT 20"
codebase-memory-mcp cli detect_changes --project home-user-agent-factory        # incremental reindex
```
- QUIRK: arg is `repo_path`/`--repo-path`, NOT `path`. A wrong arg produces a
  MISLEADING "Indexing worker crashed on a file" hint — read the worker log
  (~/.cache/codebase-memory-mcp/logs/) before believing a crash.
- QUIRK: CLI-mode `trace_path` returns an empty echo of its args — use
  `query_graph` Cypher for caller/callee traces instead (works, verified).
- Project name = slugged path (`home-user-agent-factory`); `list_projects` when unsure.

### code-review-graph (venv: /root/venv-crg/bin/code-review-graph)
```bash
code-review-graph build -q --data-dir <scratchpad>/crg-data       # ~3.5 min full repo, once per container
code-review-graph query callers_of <symbol-or-qualified-name>     # disambiguates if ambiguous
code-review-graph query tests_for <Class>; ... importers_of <module>
code-review-graph impact --files <changed.py> --depth 2           # FILE-level blast radius
code-review-graph dead-code; ... communities; ... architecture
```
- Quirk: `impact` takes FILES not symbols; symbol questions go through `query`.
- Ambiguous names return a candidates list — re-run with the qualified_name.
- Keep the DB out of the repo (`--data-dir` in scratchpad; `.git/info/exclude` has
  `.code-review-graph/` as belt-and-braces).

## Fresh-container bootstrap (the rollback lesson: NONE of this survives)
1. `bash sandbox-kit/codebase-memory-mcp/install.sh --dir=/root/.local/bin`
   (EQUALS form — the space form `--dir /path` is silently ignored by its arg
   parser; prebuilt release download — the in-repo SOURCE build is impossible
   by design: vendored C deps were never committed; do not "fix" the make error)
2. `npx --yes gitnexus@1.6.7 analyze .` (recreates .gitnexus/ + index)
3. `python3 -m venv /root/venv-crg && /root/venv-crg/bin/pip install code-review-graph`
4. Index: cbm `index_repository` + crg `build` (lazy — first use, not session start)
Then verify each with a known-truth probe (e.g. callers of apply_seal_fence =
exactly load_ohlcv/load_ohlcv_aligned/load_batch + 1 direct test).

## The rules
- BEFORE editing a symbol: GitNexus impact. BEFORE committing: detect-changes.
  AFTER each landed increment: re-index all three (cbm detect_changes, crg
  update/build, gitnexus analyze if new modules).
- DORMANT/reachability claims: two instruments minimum, named in the report.
- If a tier is down, ESCALATE DOWN THE LADDER and say which tier answered;
  "unmapped — tool unavailable" only when ALL tiers of ALL relevant tools failed.
- **MCP connect failures at session start are NOT a grep license (bit 2026-08-27:
  a dormancy claim shipped on bare grep while every CLI tier was alive).** The
  CLI/binary tiers survive MCP outages and container recycles independently —
  before regressing to grep, spend the 10 seconds: `ls graft/INDEX.md` ·
  `codebase-memory-mcp cli list_projects` · `ls /root/venv-crg/bin/`. Tick-cadence
  time pressure is exactly when unverified single-instrument claims slip out.
- These are DEV-PLANE tools: never in the gate spine, never a production dependency.

## sentrux — the fifth, ADVISORY instrument (architecture health; adopted 2026-09-05)

Axis: not reachability (the quartet) but STRUCTURE — did a lane make the codebase worse?
Invocations (sandbox; the wrapper composes a copy of proofs/ scripts/ tests/ harness-ports/ spikes/
src/ under `.sentrux-runtime/tree` because the tool cannot exclude `sandbox-kit/` any other way):
- `bash scripts/sentrux_review.sh save` — baseline BEFORE a build lane (kept in `.sentrux-runtime/`).
- `bash scripts/sentrux_review.sh compare` — after the lane: quality / coupling / cycles / god-files
  delta and "No degradation detected" or the degradation list. Paste the block into the verify brief.
- `bash scripts/sentrux_review.sh check` — the `.sentrux/rules.toml` report (max_cycles 0, max_cc 25,
  max_fn_lines 100). Long single-pass validators (the S0-01 checker functions) exceed max_cc by
  design — a report line, not a verdict.
Never a gate: the wrapper exits 0; `--strict` exists only for a future CI opt-in.
Blind spot (measured 2026-09-05): Python import resolution here is 4/390 specs, so coupling, cycles
and the main-sequence distance are near-empty on this tree; complexity/length are the live signal.
Pins + telemetry posture: `upstream.lock.yaml` `advisory_tooling.sentrux`;
`sandbox-kit/docs/THIRD-PARTY-AGENT-TOOLS.md` §sentrux. Missing binary → `scripts/setup.sh`.

## ripwire — the sixth, ADVISORY instrument (ranked symbol map + call graph; adopted 2026-09-07)

Axis: not reachability (the quartet) or structure (sentrux) but ORIENTATION and CALL-GRAPH QUERIES
in a single deterministic binary. Use for:
- **Cold orientation map:** `bash scripts/ripwire_review.sh map --top-k=60` — ranked symbols by
  PageRank with call edges, ~2.8k tokens, 1.6 s cold. The starting point when reading a new
  subsystem.
- **Semantic lookup (SECOND opinion after `graft ask`, never instead):**
  `bash scripts/ripwire_review.sh for "where is the status file written"` — BM25 route, ~7 s /
  ~4.1k tokens. Use when graft returned nothing or you want a second instrument's take.
- **Pre-edit advisory line:** `bash scripts/ripwire_review.sh edit-check SYMBOL` — callers +
  exercises + test-gate in one pass. An advisory complement to the mandatory GitNexus `impact`.
- **Test coverage advisory:** `bash scripts/ripwire_review.sh test-gate FILE...` — reports
  tested/untested symbols. Advisory only, never a gate.
- **DORMANT claim (direct-call edges ONLY):** `bash scripts/ripwire_review.sh exercises TESTFILE`
  as a SECOND instrument when the edge is a direct call — NEVER for subprocess-exercised tools
  (the tool reports `tests="0" impacted="0"` for them; the blind spot is documented and
  `counts_floor="1"` is the tool's own disclosure). For subprocess edges, use the quartet.
- **Call hierarchy:** `bash scripts/ripwire_review.sh callers SYM` /
  `bash scripts/ripwire_review.sh impact SYM`.
- **Parser coverage:** `bash scripts/ripwire_review.sh skipped` — files the parser could not
  index (extension-less scripts, unsupported extensions).

Wrapper: `scripts/ripwire_review.sh` bakes in the five `--exclude` flags and routes `--limit` to
flat verbs (default `RIPWIRE_LIMIT=20`), `--top-k` to `map` only.
Never a gate: a ripwire zero is "none found", never "none exists".
Pins + telemetry posture: `upstream.lock.yaml` `advisory_tooling.ripwire`; no telemetry found.
`sandbox-kit/docs/THIRD-PARTY-AGENT-TOOLS.md` §ripwire. Missing binary → `scripts/setup.sh`.
