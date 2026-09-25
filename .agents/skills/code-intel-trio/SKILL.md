---
name: code-intel-trio
description: Use the three code-intelligence tools (GitNexus, codebase-memory, code-review-graph) together — which one for which question, exact CLI invocations that work in this container, bootstrap steps on a fresh container, and the two-instrument rule for dormancy claims. Load before any Phase-1 grounding, impact analysis, dead-wiring hunt, pre-commit check, or DORMANT/reachability claim; and when an MCP server fails to connect (the CLI is the path; moved from CLAUDE.md by CTX1).
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

## prism — deep structural review (ADVISORY prompt-skills; adopted 2026-09-17)

Axis: not code-graph facts (the quartet/ripwire) or architecture health (sentrux) but a DEEP
STRUCTURAL READ of one artifact — the bugs and trade-offs a checklist misses. Prompt-only skills
(`.agents/skills/`, from `.claude/skills/`; vendored super-hermes MIT,
`.claude/skills/PROVENANCE-PRISM.md`). Invoke via the skill mechanism. Use for:
- **`prism-scan`** — cook a custom analytical lens for THIS artifact, execute it → findings table
  (location · what breaks · severity · fixable-or-structural). The default entry on a hard-to-see
  bug or an important file / design / spec.
- **`prism-full`** — multi-pass + a MANDATORY adversarial self-correction pass (attack your own
  findings, retract overclaims). The deep-work Phase-5 ethos in prompt form; for a core module or
  a design about to be committed to.
- **`prism-3way`** — WHERE/WHEN/WHY orthogonal passes + synthesis; findings corroborated by ≥2
  passes are the real ones.
- **`prism-discover`** — enumerate the analysis domains worth taking BEFORE committing a scan.
- **`prism-reflect`** — constraint transparency (what the analysis maximized vs sacrificed);
  writes `.prism-history.md` (gitignored) so later scans steer around exhausted angles.

NEVER a gate: LLM analysis FINDS and INFORMS; it never DECIDES a green (no LLM-judge in the gate
spine). A prism's findings feed the human/coordinator verdict and the deterministic gates, the
same posture as slopo/sentrux/ripwire; a prism is not one of the two independent instruments a
reachability/containment claim still needs.

## § lane_context — the ONE-COMMAND tool pass (owner escalation 2026-09-07)

`scripts/lane_context.sh [-q "<question>"] [-s SYMBOL]... [-o pack.md] FILE...` runs the whole quartet + ripwire +
the whole-file registry screen for a brief's files in one command: graft skeleton per file, graft ask for the
brief's question, and per symbol GitNexus impact + code-review-graph callers_of/tests_for + ripwire callers (two
independent instruments for every reachability claim), ripwire test-gate over the files (the tests to run + the
UNTESTED blast radius), `ap_screen.py` over whole files. Symbols come from `-s` plus the `def` names in each
file's working-tree diff, so a verifier's pack sees exactly what the lane touched. Every build AND verify brief
attaches its pack; the coordinator runs it BEFORE writing the design (Phase 1 grounding) and again on the lane's
diff before dispatching the verifier. Every instrument is optional and tolerant — an absent one prints
`unmapped — <tool> unavailable`, never a silent blank. Why this exists: eleven S0-01 rounds passed without a
single instrument run on a lane delta; graft's MCP had timed out at session start (the startup stampede, not the
index — `MCP_TIMEOUT=120000` is the environment fix), the code-review-graph graph had never been built ("lazy,
first use"), and the registry screen only ever saw edited hunks. An instrument that is not in a script on the
path is not in the loop.

## Moved from CLAUDE.md by CTX1 (D-089, 2026-09-25)

CLAUDE.md was shortened losslessly (the owner, D-089, 2026-09-25): the text below left it VERBATIM, and CLAUDE.md points
here.

### The core reflexes (CLAUDE.md's code-intelligence section)

- **GRAFT-FIRST FOR CODE QUESTIONS.** `graft ask "<question>" [--source] [--in <path>]` /
  `graft skeleton <file>` BEFORE any bare grep. Cold container: `graft build` backgrounds
  (setup.sh does this; log `/tmp/graft-build.log`) — check `graft/INDEX.md` exists before relying
  on it, and NAME the fallback instrument when graft wasn't available. MCP tools
  (`graft_find_code`/`graft_trace_calls`/…) register at user scope for the NEXT session; same-
  session use is the CLI. Provenance: `sandbox-kit/docs/THIRD-PARTY-AGENT-TOOLS.md` §Graft.
- **EDIT-SNAPSHOT hook (owner directive 2026-08-25):** every Edit/Write on a production `.py`
  auto-returns a snapshot (**to the model through `scripts/hook_context.py`, which turns the hook's plain text into additionalContext — plain
  PostToolUse/PreToolUse stdout reaches only the transcript view, measured live 2026-09-24; the graft nag runs through it too, and
  the hook scripts stay plain text for the Codex/Hermes adapters — AF-AP-172**) — enclosing symbol's GitNexus blast radius + an anti-pattern-registry
  screen of the hunk (`.claude/hooks/edit-snapshot.py`, PostToolUse; venv
  `/root/venv-agent-factory`, package prefix `agent_factory`, `sandbox-kit/` excluded). READ it,
  act on flags; it says "index rebuilding" during the post-commit reanalyze window — re-check
  impact before commit then. It informs, never blocks. **Every new registry row with a
  mechanical signature extends the hook's AP_SCREEN in the same increment** (the screen ships
  with the source repo's inherited AP-1…AP-70 signatures; this project's rows are `AF-AP-*`).
- **TRACE-BACK RECIPE (`scripts/why.sh <file> [function]`):** the per-function "histogram of
  edits and why" is COMPUTED on demand from primary sources (git `log -L` chronology + the last
  change's full reasoning-record commit body + incident-log/findings/wiki mentions + current
  blast radius) — never stored in the wiki, which would drift per commit. Wiki carries the
  MEANING layers (map, key decisions with SHA anchors, live-state, do-not-trust list); git
  carries the chronology; why.sh joins them.
- **Before editing any symbol:** GitNexus `impact` (who calls this, what breaks).
- **THE PACK (owner escalation 2026-09-07):** `scripts/lane_context.sh -q '<question>' -s SYM -s SYM2… -o pack.md FILE...` —
  the whole quartet + ripwire + the whole-file registry screen in ONE command; every build and verify brief attaches
  its pack; the coordinator runs it before designing and on the lane's diff before the verifier. `scripts/report_lint.py`
  and `scripts/ap_screen.py --s0-01` gate every checkpoint (`report_lint.py --min-refs N`: a report that cites nothing lints clean by construction — B3's `0 refs — MISS 0`, 2026-09-14 — so a checkpoint gates on a FLOOR, never on the MISS count alone; the LANE side is BOUNDED — the lint's own `fix:` hints applied for at most three rounds, then paste and finish, injected into every lane prompt by `pc-lane.sh` since N5k looped 47 minutes on an unbounded `MISS 0` bar, AF-AP-76). An instrument that is not in a script on the path AND in the LANE TREE and its prompt is not in the loop (2026-09-15: no lane had used the quartet — a lane worktree carries no index and the briefs named none; `pc-lane.sh` now builds the graft index at launch, overlays the current lint and injects the CODE INTEL FIRST standing rule). An instrument that is not in a script on the path is not in
  the loop.
- **After EVERY edit-batch, not just before commit:** `detect_changes`; re-`analyze` (detached)
  on a stale index. Before commit stays mandatory.
- **When grounding (Phase 1) or hunting dead wiring:** codebase-memory (`search_graph` /
  `query_graph` Cypher / `get_architecture`; prebuilt binary `/root/.local/bin/codebase-memory-mcp`,
  MCP connected at user scope) + code-review-graph (`/root/venv-crg/bin/code-review-graph query
  callers_of` / `tests_for` / `impact --files`); re-index after each landed increment so the map
  never lags the tree.
- **Advisory instruments (NEVER gates; owner decision 2026-09-05):** slopo (semantic duplicates,
  `slopo review --base <push-base>`) and **sentrux** (architecture health: `scripts/sentrux_review.sh
  save` BEFORE a build lane, `compare` after it, `check` any time; rules in `.sentrux/rules.toml`;
  pinned by digest in `upstream.lock.yaml`; provenance `sandbox-kit/docs/THIRD-PARTY-AGENT-TOOLS.md`
  §sentrux). **ripwire** (owner ask 2026-09-07, adopted as the SIXTH advisory instrument): ranked symbol map + static call
  graph, `scripts/ripwire_review.sh map|for|callers|impact|exercises|test-gate|edit-check|skipped`; blind to subprocess
  edges (a zero is "none found", never "none exists"); binary pinned by digest in `upstream.lock.yaml`, the bundled
  skills/hooks are never installed. Attach a lane's `compare` delta to its verify brief; a "degraded" line is information
  for the verifier, not a verdict. Known blind spot: Python import resolution is weak on this tree,
  so its coupling/cycle numbers are near-empty here; complexity and function length are the live signal.
- **The prism review skills (advisory, NEVER a gate; owner 2026-09-17):** `prism-scan`/`prism-full`/`prism-3way`/`prism-discover`/`prism-reflect` (`.claude/skills/`, mirrored to `.agents/skills/`; vendored super-hermes MIT, `.claude/skills/PROVENANCE-PRISM.md`). On a hard-to-see bug or an important artifact, run one — it cooks a custom analytical lens for THAT artifact and reports a findings table (location · what breaks · severity · fixable-or-structural); `prism-full` adds a mandatory adversarial self-correction pass (attack your own findings, retract overclaims), the deep-work Phase-5 ethos in prompt form. LLM analysis, so a prism FINDS and INFORMS; it never DECIDES a green (no LLM-judge in the gate spine) — its output feeds the human/coordinator verdict and the deterministic gates, exactly like slopo/sentrux/ripwire.
- **DORMANT/reachability claims need TWO independent instruments, named in the report** (e.g.
  crg `callers_of` AND a cbm Cypher trace) — never off one.
- Fallbacks (CCR sessions often drop MCP): GitNexus 3-tier (MCP → stdio `scripts/gn_mcp.py` →
  CLI `node .gitnexus/run.cjs`); codebase-memory prebuilt binary + crg venv are installed by
  setup. **If ALL tiers of the relevant tools are unreachable, say "unmapped — tool
  unavailable" in the report; never imply a mapped claim a tool didn't produce.**

### MCP servers are NOT the path (CLAUDE.md's Environment section)

**MCP servers are NOT the path (owner ruling 2026-09-07: "the MCP server not working — just use the CLI, it's more reliable").**
The graft CONNECT_TIMEOUT on a fresh container (2026-09-07 12:37Z: the startup reindex stampede hit the 30 s limit; the server
answers `initialize` in 0.5 s idle) was the symptom; the rule is the CLI on every venue — `graft ask` / `graft skeleton`,
`node .gitnexus/run.cjs` (or `scripts/gn_mcp.py`), `codebase-memory-mcp cli <tool> --flag value`, `/root/venv-crg/bin/code-review-graph`,
`scripts/ripwire_review.sh` — all wrapped by `scripts/lane_context.sh`. A failed MCP connect is never worked around and needs no
`MCP_TIMEOUT`; the background builds stay delayed and niced so a connect that does happen is quiet.

### Superseded by CTX1: the GitNexus block's pre-CTX1 wording (history only)

Since CTX1 every automatic `gitnexus analyze` passes `--skip-agents-md`, the GitNexus block in CLAUDE.md and AGENTS.md
is ours, and its volatile counts line is gone. Until then the block opened with the counts line, and CLAUDE.md said what
follows. Neither is true now; they stay here as the record.

```text
This project is indexed by GitNexus as **agent-factory** (15749 symbols, 35231 relationships, 784 execution flows).

The harness auto-injects the live GitNexus block (index stats + Always/Never-Do rules) every
turn — those rules govern; don't duplicate them here. GitNexus owns the flat
`.claude/skills/gitnexus-*/SKILL.md` set (exploring / impact-analysis / debugging / refactoring /
guide / cli) and rewrites the block below on every `analyze` — commit that churn, never hand-edit
it.
```
