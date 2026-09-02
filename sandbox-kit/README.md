# sandbox-kit — portable operating kit for Claude Code on the web

A self-contained bundle of the hard-won knowledge for running a project inside the **Claude Code on
the web** ephemeral sandbox. **Designed to be copied wholesale into a new repo** — but not every
file here should travel: some are the portable "alpha," some are this specific repo's live
operational state (VM identities, bridge URLs, hardware quirks). See the manifest below before you
copy.

## Manifest: PORTABLE vs PROJECT-SPECIFIC

**PORTABLE — copy these into a new repo's `sandbox-kit/`:**

| File | What it covers |
|---|---|
| [`CLAUDE.template.md`](CLAUDE.template.md) | Full generalized `CLAUDE.md` — swarm/honey model routing, the NO-STUBS anti-hollow-green rules, behavioral guidelines, the "Fable light"/"Fable deep" build protocols, telemetry rules — with project specifics as `<PLACEHOLDERS>`. Rename to `CLAUDE.md` and fill in. |
| [`OPERATING-GUIDE.md`](OPERATING-GUIDE.md) | Day-to-day rules: ephemeral-container discipline, SessionStart hook, branch verification, GitNexus/Ouroboros MCP behavior, shell/tool gotchas. Repo-specific values inside (branch names, test subsets) are marked as examples. |
| [`RESEARCH-PROMPT-GUIDE.md`](RESEARCH-PROMPT-GUIDE.md) | Full research-prompt authoring rules (SETTLED-SPEC vs EXPLORATORY-HYPOTHESIS modes, the AWM-hardening rules). Illustrative RP references inside are this repo's history, kept as evidence citations — the rules themselves are generic. |
| [`BEHAVIORAL-GUIDELINES.md`](BEHAVIORAL-GUIDELINES.md) | Standalone copy of the Karpathy behavioral guidelines (also inlined in `CLAUDE.template.md`) — link out to this instead if you'd rather not inline the whole thing. |
| [`GITNEXUS-CLI.md`](GITNEXUS-CLI.md) | Driving GitNexus code-intelligence — MCP → stdio (`scripts/gn_mcp.py`) → CLI, in that order, when the native MCP integration is flaky. |
| [`OUROBOROS-SETUP.md`](OUROBOROS-SETUP.md) | Running the spec-first Ouroboros workflow headlessly in a fresh sandbox: the headless install + the two MCP-registration gotchas. |
| [`TELEMETRY-REFERENCE.md`](TELEMETRY-REFERENCE.md) | Full telemetry specification (also summarized in `CLAUDE.template.md`). **Genericize the framework paths inside** (`obs/trace.py` etc.) to your own observability module before use. |
| [`EXAMPLE-RESEARCH-PROMPT-SETTLED-SPEC.md`](EXAMPLE-RESEARCH-PROMPT-SETTLED-SPEC.md) | Worked SETTLED-SPEC research-prompt example (invented neutral subject) — a fully paste-ready shape to copy from. |
| [`EXAMPLE-RESEARCH-PROMPT-EXPLORATORY.md`](EXAMPLE-RESEARCH-PROMPT-EXPLORATORY.md) | Worked EXPLORATORY-HYPOTHESIS research-prompt example (same neutral subject) — contrasts with the SETTLED-SPEC one. |
| [`council-of-high-intelligence/`](council-of-high-intelligence) | Vendored multi-persona deliberation tool (`/council`) used at Feature Workflow step 1.5/4. Self-contained (own README/CLAUDE.md/install.sh). |
| [`llm-wiki-compiler/`](llm-wiki-compiler) | Vendored codebase-wiki compiler used at deep-work-protocol Phase 6 (`/wiki-compile`). Self-contained. |

**REPO-ROOT PORTABLES — live outside `sandbox-kit/` in the source repo; copy them too:**

| Path | What it covers |
|---|---|
| `.claude/` | The committed skills library (630 files: gitnexus skills, the UI/UX skill pack, phoenix-cli/evals/tracing, output/impeccable, …) + `settings.json` + the SessionStart hook pattern (`hooks/session-start.sh` → calls `scripts/setup.sh`; web-only guard). Copy the whole tree into the new repo's `.claude/`; the hook expects a `scripts/setup.sh` to exist (the bootstrap checklist has you author one). |
| `.wiki-compiler.json` | Worked example of the wiki build config consumed by `/wiki-compile`. Copy, then change `name`, and replace the `topic_hints` with your project's own areas (or delete them — `wiki-init` regenerates). |
| `scripts/ooo_mcp.py` | Ouroboros stdio fallback (tier 2 of the MCP → stdio → CLI ladder) — the full MCP tool surface as JSON-RPC with no permission gates. CLAUDE.md's "always prefer stdio" rule depends on this file existing. |
| `scripts/gn_mcp.py` | GitNexus stdio fallback (tier 2 of its ladder). Both scripts are self-contained; copy into the new repo's `scripts/`. |
| `.mcp.json` | MCP server registration (gitnexus stdio + phoenix-docs). Strip any entries pointing at project-private tunnels before copying. |

**PROJECT-SPECIFIC — do NOT copy; these are this repo's live operational state, not reusable rules:**

| File | Why it stays behind |
|---|---|
| [`HERMES-VM.md`](HERMES-VM.md) | Runbook for one named GCP VM (Hermes) this repo uses for live benchmarking — identity, install quirks, and a service name specific to that box. |
| [`ACTIVE-LINKS.md`](ACTIVE-LINKS.md) | This session's ephemeral bridge URLs — by definition not durable, not portable. |
| [`PC-BRIDGE.md`](PC-BRIDGE.md) | Setup procedure tied to one specific home PC's GPU/model-server stack. |
| [`PC-STATE.md`](PC-STATE.md) | Hardware-state snapshot (known faults, physical machine) for that same PC. |
| [`PC-THERMAL.md`](PC-THERMAL.md) | Fan-control runbook naming that PC's specific hwmon paths and GPU model. |
| [`ENVIRONMENT-REFERENCE.md`](ENVIRONMENT-REFERENCE.md) | Full environment doc written "for the agent-distiller repo" — a superset of the genericized summary already in `CLAUDE.template.md`. |
| [`HUMAN-PLANE.md`](HUMAN-PLANE.md) | Describes this repo's specific two-plane OTel telemetry deployment (dashboards, exporters) layered on top of the portable rules in `TELEMETRY-REFERENCE.md`. |
| the filled root `CLAUDE.md` | `CLAUDE.template.md`'s filled sibling — this repo's actual, non-generic instructions. Use it as a worked reference, never copy it verbatim. |

Classification was verified against each file's actual header/content, not assumed from the
filename — if you find one misfiled, it's a one-line fix to the row above, not a redesign.

## New-project bootstrap checklist

1. **Create the new repo.**
2. **Copy the PORTABLE set above** into the new repo's `sandbox-kit/` (whole folder for the two
   vendored tools; individual files for the rest). Leave the PROJECT-SPECIFIC set behind.
3. **Rename `CLAUDE.template.md` → `CLAUDE.md`** at the new repo's root and fill every
   `<PLACEHOLDER>` — project description, onboarding map, `<OBS_FRAMEWORK>` path, GitNexus repo
   name. Delete sections that genuinely don't apply; keep the verbatim protocol text as-is.
4. **Author a new `scripts/setup.sh`** for the new project's actual toolchain. Use this repo's
   `scripts/setup.sh` as the *reference pattern* (SessionStart-hook-driven, idempotent, prints
   start/elapsed banners) — do **not** copy it verbatim, it installs agent-distiller-specific
   dependencies (GitNexus, Ouroboros, the council/wiki tools' own installers) that a fresh project
   may not need in that exact combination.
5. **`wiki-init`** (the `llm-wiki-compiler` skill) to stand up the codebase wiki referenced from
   `CLAUDE.md`'s onboarding map.
6. **`node .gitnexus/run.cjs analyze`** (or `npx gitnexus analyze`) to build the first code-
   intelligence index; let it populate the `CLAUDE.md` Code-intelligence section instead of hand-
   authoring the stats.
7. **Write the first real research prompt** from the two `EXAMPLE-RESEARCH-PROMPT-*.md` shapes —
   copy whichever mode fits (mode-selection rule is in `RESEARCH-PROMPT-GUIDE.md`), swap in the
   real subject, and start the feature workflow (`CLAUDE.md`'s Feature Workflow section) from
   there: interview → seed → task-breakdown → build.
