# Third-party agent tooling — provenance & audit ledger

Installed 2026-07-28 (owner directive: "install the repos... mine whatever offer you can").
Both repos were cloned to scratchpad, every file read in full before anything entered this
tree. Verdict: clean — pure method prompts, no injection, no executables installed (the ACG
demo code was NOT installed, only its loop distilled into a skill).

## Lunarsong/Claude-Opus-5-tools (CC0 / public domain)

| Installed as | Source file | Changes |
|---|---|---|
| `.claude/skills/trace-the-chain/` | same path upstream | verbatim |
| `.claude/skills/adversarial-review/` | same path upstream | verbatim |
| `.claude/skills/root-cause-debugging/` | same path upstream | verbatim |
| `.claude/skills/empirical-validation/` | same path upstream | verbatim |
| `.claude/agents/code-implementer.md` | `.claude/agents/code-implementer.md` | merged with this repo's standing delegate do-nots; pinned `model: claude-opus-4-6` (owner stage routing) |
| `.claude/agents/evidence-gatherer.md` | `.claude/agents/evidence-gatherer.md` | merged with Reflection-Firewall/SOLID-UNSURE rules; pinned `model: claude-opus-5` |
| `.claude/agents/adversarial-verifier.md` | derived from `adversarial-review` skill | new agent wrapping the playbook + this repo's Phase-5 verify (mutation audit, fail-open input class, scratchpad-restore discipline); pinned `model: claude-opus-5` |
| (folded into CLAUDE.md) | `working-agreements.md` | the agreements not already law here were added to the CLAUDE-5 delegation section |

## Archive228/adversarial-contract-gate (MIT)

Distillation of Anthropic's "Build Agents That Run for Hours" workshop (Prabaker/Wilson).
Its Python demo (`src/*.py`) was audited but NOT installed — it is an offline teaching demo
(`exec()`-based, scripted builder). What was installed is the LOOP:

| Installed as | What it carries |
|---|---|
| `.claude/skills/contract-gate/` | the negotiate → build → adversarial-evaluate → bounded-repair → fail-closed loop, mapped to this repo's agents and gates |

Key lecture anchors preserved: 39:00 (self-evaluation is a trap), 20:05 (critique cheaper than
creation), 26:00 (grade against the negotiated contract, not the spec), 26:47 (separate
context windows + adversarial pressure), ~25:33 (the repair loop).

## Owner stage-routing ruling (2026-07-28)

- **Fable** — plans/orchestrates (the main loop). Never dispatched as a delegate.
- **Opus 5** — every EXPLORE/VERIFY lane: forensics, evidence gathering, premortems, roasts,
  adversarial review, any workflow verify stage. "Great at analyzing; point it right."
- **Opus 4.6** — every BUILD lane: "throw the problem and disappear." Pinned by literal model
  id in agent frontmatter because the harness `opus` TIER resolves to Opus 5.
- **Sonnet 4.6 over Sonnet 5** on the rare sonnet-tier dispatch (owner assessment; sonnet-tier
  is de-emphasized).
- Re-audit upstream before ever re-syncing: these files are third-party content; a future
  upstream commit is unaudited until read.

## Code-intel trio additions (2026-08-03, owner mapping mandate)

| Installed as | Source | Audit / changes |
|---|---|---|
| `sandbox-kit/codebase-memory-mcp/` (vendored) + prebuilt binary via `install.sh` | github.com/bosun-ai/codebase-memory-mcp (Apache-2.0) | vendored tree audited; SOURCE build impossible by design (vendored C deps never committed) — setup installs the prebuilt release ONLY. Dev-plane, never in the gate spine. |
| `gitnexus@1.6.7` (npm global, pinned) | npmjs.com/package/gitnexus (MIT) | pinned exact version; `--ignore-scripts` + explicit `npm rebuild -g @ladybugdb/core` (postinstall race). Index lives in `.gitnexus/` (committed run.cjs shim). |
| `code-review-graph` (PyPI, own venv `/root/venv-crg`) | pypi.org/project/code-review-graph (MIT) | separate venv (deps clash with venv-trading); DB kept OUT of the repo (scratchpad `--data-dir`; `.git/info/exclude` belt-and-braces). |
| `.claude/skills/code-intel-trio/` | authored in-repo | the trio's operative guide: tool-per-question table, container-verified invocations + quirks, bootstrap, two-instrument dormancy rule. |
| `sandbox-kit/output-styles/` (vendored .md ×3) | github.com/alexgreensh/attention-span v0.3 (AGPL-3.0) | chat-FORMAT styles only (`keep-coding-instructions: true`), never in the gate spine; AGPL noted in PROVENANCE.md (private in-repo use with attribution); setup.sh copies to `~/.claude/output-styles/`, activation per-session. |

## Graft (2026-08-24, owner-directed adoption)

| Installed as | Source | Audit / changes |
|---|---|---|
| `@nanonets/graft@0.12.1` (npm global; setup.sh installs latest) | github.com/NanoNets/Graft (MIT, ~4.7k stars) | Context-graph layer for coding agents: tree-sitter structural graph (42,457 nodes / 92,310 edges over this repo incl. vendored vbt) + linked-markdown repo map. Core commands (`build`/`ask`/`skeleton`/`grep`/`map`/`mcp`) are LOCAL, deterministic, $0, no API key, no network. `--deep` (LLM summaries) NOT used — would need a key; skipped by policy. Telemetry disabled in setup.sh (`graft telemetry disable` + `DO_NOT_TRACK=1`). MCP server registered user-scope (`graft mcp`); tools: graft_find_code / graft_trace_calls / graft_find_all / graft_file_api / graft_repo_map / graft_check_freshness. `graft/` output dir is a regenerable local cache — graft itself gitignored it and wrote `.ignore` to keep it ripgrep-visible; rebuilt per cold container in background by setup.sh. Dev-plane navigation only, NEVER in the gate spine. |

## effective-html (2026-08-24, owner-directed adoption)

| Installed as | Source | Audit / changes |
|---|---|---|
| `.claude/skills/{html,html-diagram,html-plan,html-prototype,html-wireframe,design-artifact}` (committed, survives containers; installed via `npx skills add plannotator/effective-html`) | github.com/plannotator/effective-html (MIT, ~2k stars) | Agent skills for self-contained single-file HTML deliverables (reports, diagrams, plans, wireframes, prototypes). Pure prompt/skill content — no network, no keys, no runtime. Used for owner-facing visual reports/diagrams; NEVER in the gate spine. |

| thermo-nuclear-review (skill) | cursor/plugins thermos/skills/thermo-nuclear-review @ main, vendored 2026-08-25 (owner request; 12.4K installs, Socket/Snyk/Trust-Hub pass) | Branch security+correctness audit prompt. AUDITED clean (no injection/exfil/tool abuse). Vendored to .claude/skills/thermo-nuclear-review with 3 house amendments (over-reporting override for delegate lanes; PR-discussion -> prior verdict files; composes with adversarial-review). Its devex-breakage + gate-leak lenses baked into adversarial-review attack set items 10-11. |

## luck (2026-08-27, owner-directed adoption)

| Installed as | Source | Audit / changes |
|---|---|---|
| `.claude/skills/luck/` (vendored SKILL.md) | github.com/soleio/luck @ main (MIT, ~191 stars, markdown-only) | "The Geometry of Luck" — seven-facet strategic-diagnostic lens (Assembly Theory extension). AUDITED clean 2026-08-27 (full read: no code, no install scripts, no directives beyond the lens itself). Vendored verbatim with a house header: scope = META-WORKFLOW deliberation only (retros, research prompts, architecture decisions, premortems, council, seed reviews — owner mandate 2026-08-27: "optimize the workflow, the way this AI system workflow is set up"); BARRED from the gate spine, all measurement/certification verdicts, and delegate briefs (no-LLM-judge law). Integration points: turn-retro hook question 5, deep-work retrospective rule, premortem-roast attack set, RESEARCH-PROMPT-GUIDE council step. Measurement/falsifiability section summarized (upstream carries full text). |

## ai-memory (github.com/akitaonrails/ai-memory) — EVALUATED 2026-08-31, NOT ADOPTED
Owner-suggested as wiki-infra replacement during the rollback-heavy 08-29..31 stretch.
Verdict: its core design (git-versioned markdown wiki + hook-injected recall + authority
tiers) is what wiki/ + live-state + the SessionStart/UserPromptSubmit hooks already
implement, minus its Rust HTTP/MCP daemon + SQLite/FTS index — extra per-container moving
parts with the SAME durability boundary (git push) and no coverage of our actual loss modes
(unpushed commits, wrong-cell launches; fixed instead by push-when-green, transcript
recovery, verify_cell.sh). STEAL-LATER: entity-frontmatter + FTS5 hybrid retrieval as a
wiki-context.py matcher upgrade IF keyword-injection misses become a felt pain (rebuildable
index, no daemon required). Re-evaluate only after a concrete retrieval-miss incident.
