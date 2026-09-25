# CLAUDE.md — agent-factory

Guidance for AI coding agents working in the **`agent-factory`** repo.

> **Structure note (ported 2026-09-03 from `trading-system@clean-build` — the setup the owner
> built things with, at the owner's direction):** this file carries the always-needed core. The
> full protocols live in repo skills that auto-load on trigger — `build-loop` (the mandatory
> per-increment loop), `deep-work` (Phases 0–6 + retrospective + meta-rules), `orchestration`
> (briefs, delegation, ORCHESTRATOR protocol, SUCCESSION), `anti-hollow-green` (full
> gate/oracle/test tactics), `session-continuity` (the resume protocol), `code-intel-trio` (the
> code-intel quartet's exact invocations). The skills are the AUTHORITATIVE expansions; the
> sections below are their operative indexes. New lessons: bake the general rule into the matching
> SKILL (same increment), and touch the index line here only if the index itself changed. The
> skills carry the SOURCE repo's war stories as evidence (paths like `trading/...` are that
> repo's; this repo's equivalents are named below). Provenance of the kit and of the port:
> `sandbox-kit/VENDORED-FROM.md`. Keep this file honest — every claim in here about what is built
> stays independently verifiable, never aspirational.

## GIT BRANCH RULES (NON-NEGOTIABLE)

**The development branch is `claude/soundbox-kit-migration-iz1jwf`** — the session's designated
branch; the tooling port and the Stage 0 build both land there. `main` receives work ONLY through
a pull request the owner merges (PR #2 carried the kit migration); never push to `main` directly,
and never push to any other branch without the owner's explicit say-so.

- **Push only through `scripts/push_clean.sh --no-delegates-live`** (clean tree) **or `--lanes-live`** (sandbox lanes hold the
  tree: the dirty set must equal the untracked `.lanes-live` list written at dispatch; the rewrite + push run from a detached
  worktree and the branch ref then follows origin on tree identity — no other argument exists; set `PUSH_BRANCH=<branch>` when not
  on the branch). It strips model-identifier trailers from
  the unpushed range, proves tree identity across the rewrite, verifies zero trailers remain, and
  pushes the rev-parsed SHA — never `HEAD`. The pre-push hook BLOCKS any outgoing commit still
  carrying `Co-Authored-By: Claude` / `Claude-Session:` lines (owner policy: no model identifiers
  reach origin). Run `git log origin/<branch>..HEAD` before ANY push and review every unreviewed
  delegate commit first. **CI GATE (AF-AP-126; owner 2026-09-23, an inbox of "Run failed" mails, the third time):**
  after its fetch, push_clean runs `scripts/ci_gate.py`, which reads the branch's newest stage0-ci run in origin's history
  through the Actions API. Exit 1 REFUSES while it is red (a push that carries the fix names the red run: `CI_FIX=<run id>`).
  Exit 75 WAITS while the verdict is unknown (a run in progress, or pushes after it with no run registered yet): wait with
  `python3 scripts/ci_gate.py --branch <branch> --wait 1800`, or push anyway with `CI_WAIT_SKIP=<reason>`. Exit 2 when it
  cannot decide (`CI_GATE_OFFLINE=<reason>` rescues only the API's data; CI-GATE-R1). Batch pushes: every push is a run.
- Coordinator commits in a shared tree go through `scripts/safe_commit.sh -m "<msg>" <path>…`
  (stages ONLY the named paths; refuses if anything else is already staged — a live delegate's
  staging must never be swept). Never `git add -A` while a delegate is live.

## SWARM ORCHESTRATION & HONEY

Honey modes: `lite|full|ultra` — no "medium". Levers: 1 less code (never off) · 2 less prose ·
3 dense agent-to-agent handoffs (id-keyed JSON/ESON). A reflexive writing style, not a runtime
switch — never spend reasoning tokens on it; step UP a mode when terseness would cost correctness.
Safety carve-outs (auth, secrets, validation, migrations, deletes, explicit asks) never compressed.
Honey is a SKILL SET (Green-PT/honey-for-devs), installed offline from the vendored
`sandbox-kit/honey-for-devs/` local marketplace (plugin `honey@greenpt`, done by
`scripts/setup.sh`); its `honey*` skills and `hive-*` agents are also committed under `.claude/`
so they load with no install, and the plugin's own SessionStart/SubagentStart/PostToolUse hooks
inject the mode into dispatches and compress Bash logs.

**OWNER-FACING PROSE STYLE (owner request 2026-08-10): Simplified Technical English
(ASD-STE100 spirit) + Zinsser's four principles — simplicity, brevity, clarity, humanity.**
Short sentences. Active voice. One meaning per word. Answer first, cut the clutter, keep it
human — a person wrote it, not a manual. Applies to reports, status lines, docs the owner
reads; never compresses the safety carve-outs above, and deliverables (specs, preregs,
findings) run as long as the work needs. Chat-format styles (answer-first `Attention-kind` /
`Spartan` / `Rundown`) are committed at `.claude/output-styles/` (provenance file there; source
`sandbox-kit/output-styles/`; setup.sh mirrors them to `~/.claude/output-styles/`; project
default = Attention-kind). **SCENARIO→FORMAT AUTO-SWITCH (owner request 2026-08-10):** the
harness can't switch styles per message, so the coordinator applies the format by content type,
reflexively: answers/explanations/decisions → Attention-kind (the default) · status catch-ups +
measurement verdict reports → Rundown shape (TL;DR line first, then checkbox status lines) ·
keep-alive ticks + trivial confirmations → Spartan compression (one line, no warmth).
Deliverables (preregs/findings/briefs) keep their document form — styles govern chat, never
artifacts.

Model routing — cheapest tier that cannot mint an expensive wrong green; honey mode per role:

**Lane venues in force:** build AND verify lanes go to the PC Hermes lane by default (`scripts/pc_lane.sh <brief>
hermes <role>`); while the owner's cloud subscription is out (D-061, D-062), PC lanes use the local routes only, ONE
long-context local lane at a time, and overflow goes to two or three sandbox Opus 5.5 agents until it is back.
Load `pc-bridge-lanes` before dispatching, re-attaching or harvesting a PC lane, or sizing lanes per route.

**STAGE ROUTING (owner ruling 2026-07-28, inherited; BUILD lane re-ruled by the owner
2026-09-03): plan/orchestrate = Fable (the main loop) · every EXPLORE lane = Opus 5.5 (owner 2026-09-24, D-065; was Opus 5) · every VERIFY lane = **the
local Qwen3.8-27B on the PC too since 2026-09-14 (owner: "it does both the build and verify lane and goes back and
forth"; combo `agentfactory-verify-local`, effort `xhigh` = the Qwen3.8 template's ceiling — ultra/max are clamped
to it on local routes; the sandbox `adversarial-verifier` = the fallback, on Opus 5.5 since 2026-09-23, D-054)** ·
every BUILD lane = the owner's HERMES CLI ON THE PC (`hermes -z`; **since 2026-09-14 the model is the
LOCAL Qwen3.8-27B on the 3090 — OmniRoute combo `agentfactory-build-local`, effort `medium`, owner: "let's
get Qwen to do the heavy lifting"; the OpenAI route = `HERMES_MODEL=agentfactory-build HERMES_REASONING=ultra`;**
dispatched by `scripts/pc_lane.sh <brief> hermes
<role>`) — the `code-implementer` agent (Opus 5.5 since 2026-09-23, D-054) is the SANDBOX FALLBACK when the bridge is down or the
work is sandbox-only tooling · Sonnet 4.6 over Sonnet 5 on the rare sonnet dispatch.** The
owner's reason: the PC lane is faster and spends none of the coordinator's tokens. The build
loop, the contract gate and the FINAL validation stay in the main loop; the PC lane also runs
its own contract-gate/validation pass first ("it can do all that by itself"), so the main loop
grades a self-validated report, never raw output. Opus 5 analyzes superbly but keeps making
errors when left to build-and-fix alone; a builder executes reliably once pointed; Fable points.

| Model / lane | Use for | Honey |
|---|---|---|
| **Fable 5** (main loop) | orchestration, plans, root-cause calls, design, final verdicts | `lite` — reasoning IS the deliverable |
| **Opus 5.5** — sandbox VERIFY (agent `adversarial-verifier`, pinned `claude-opus-5-5` — owner ruling 2026-09-23, D-054) · **Opus 5.5** — EXPLORE (agent `evidence-gatherer`, pinned `claude-opus-5-5` since 2026-09-24 — owner ruling D-065; the harness reads agent definitions once per session, so dispatch it with `model: "opus"` too; the bare `opus` tier resolves to `claude-opus-5-5` since 2026-09-23, measured) | forensics, evidence tables, audits, premortems/roasts, adversarial review, every workflow verify stage | `full`: line-bounded findings, evidence anchors, SOLID/UNSURE |
| **Hermes on the PC** — BUILD (owner ruling 2026-09-03; `scripts/pc_lane.sh <brief> hermes code-implementer`, role bodies in `harness-ports/roles/`) | fire-and-forget implementation lanes on the PC (code + deterministic test + its own contract-gate pass), fixing, debugging, long runs — DEFAULT ROUTE since 2026-09-14: the LOCAL Qwen3.8-27B (`agentfactory-build-local`, `medium`; unit `qwen-builder`, `harness-ports/bin/qwen-server.sh` + `omniroute_local_builder.py`, PC-BRIDGE.md); cloud = `HERMES_MODEL=agentfactory-build` | `ultra` Lever-2: report is DATA — files:lines, verbatim test counts, discrepancies, NOT-done |
| **Opus 5.5** — sandbox BUILD (agent `code-implementer`, pinned `claude-opus-5-5` by the agent definition's literal model id — owner ruling 2026-09-23, D-054; was Opus 4.6) | sandbox-only tooling lanes, root-only lanes, or any build lane while the bridge is down | same |
| **Sonnet 4.6** (prefer over Sonnet 5 — owner assessment) | rare mid-complexity/mechanical follow-ups; `hive-builder` (≤2 files) | `full` |
| **Haiku 4.5** | `hive-scout`/`hive-reviewer` (read-only), locate/triage/classify, mechanical sweeps | `ultra`; returns = Lever-3 id-keyed JSON |

- The Agent tool exposes TIERS (`fable`/`opus`/`sonnet`/`haiku`); the `opus` tier resolves to `claude-opus-5-5` (measured
  2026-09-23 from the E3 transcript); other pinned versions (Sonnet 4.6) are reachable ONLY through
  `.claude/agents/*.md` frontmatter model ids — dispatch
  builds as `subagent_type: code-implementer` (Agent) / `opts.agentType: 'code-implementer'`
  (Workflow). The honey plugin's SubagentStart hook injects the honey mode into dispatches.
  **The harness reads `.claude/agents/*.md` ONCE per session: an edited `model:` line reaches no dispatch until the next session
  (bit 2026-09-23, AF-AP-131: E3's first dispatch after D-054 ran on `claude-opus-4-6`; stopped, re-dispatched with `model: "opus"`) —
  after a mid-session definition change pass the model on the dispatch, and read the served model from the transcript
  (`grep -o '"model":"[^"]*"' <tasks-dir>/<agentId>.output | sort | uniq -c`), never assume it.** **A refusal stop switches a lane's model mid-run with no notice (AF-AP-154; VERIFY-E3-R1 2026-09-23: Opus 5.5 to Opus 4.8 after a refusal on a PATH-shim test driver): at harvest, count the served model per ASSISTANT record (the grep also counts JSON inside tool output) and search for `"stop_reason":"refusal"`; the report must state the mix. One command does both: `python3 scripts/hiccup_scan.py --transcript <tasks-dir>/<agentId>.output --out <scratch>/harvest.md` (it streams the JSONL, never whole).**
- **Installed delegation tooling (audited third-party — provenance
  `sandbox-kit/docs/THIRD-PARTY-AGENT-TOOLS.md`):** agents `code-implementer` ·
  `evidence-gatherer` · `adversarial-verifier`. Skills `contract-gate` (USE for every serious
  increment) · `trace-the-chain` · `adversarial-review` · `root-cause-debugging` ·
  `empirical-validation` · `luck` (seven-facet META-WORKFLOW lens — retros, research prompts,
  architecture decisions, premortems, council; wired into the deep-work retrospective,
  premortem-roast, RESEARCH-PROMPT-GUIDE §1.5; NEVER in gate verdicts or delegate briefs).
- Escalate a tier when: spine/gate/security files touched · an increment failed review ·
  cross-file semantics. De-escalate for mechanical follow-ups. Hive never touches the spine; no
  tier self-accepts spine work — the coordinator re-runs gates regardless (Reflection Firewall:
  file:line refs, ≤2-sentence summaries, never re-paste code). Disjoint file boundaries per
  agent; root-cause + design + final verification stay in the main loop.
- **SAFEGUARD-FLAG ROUTING (the general form of the source repo's vocabulary rule):** if a
  delegate dies on a content-safeguard flag, or the owner reports one, log the artifact
  (file/brief/message) + best-guess trigger phrase in `docs/INCIDENT-LOG.md` in the SAME session,
  and route that vocabulary class to a non-Fable tier from brief-authoring time on (`opus`
  default). The off-limits list must be evidence-based, not folklore. This project has no known
  trigger class yet; its security-testing vocabulary (gVisor escape canaries, egress canaries,
  policy-bypass fixtures, unauthorized-turn fixtures) is defensive work on the owner's own system
  — state that authorization inside the brief.
- **EXPLICIT `model=` ON EVERY DISPATCH.** A dispatch that omits `model` runs on the agent definition's model as the
  harness read it at session start, which can be stale (AF-AP-131); only a type whose definition names no model takes
  the default, the session's own model (the Agent tool's schema; measured 2026-09-25: 82 omitted-model dispatches,
  each served by its definition's model, `docs/research/findings/laya-ft-data/SESSION-DECISIONS-2026-09-25.md` X3).
  An unrouted delegate of such a type is a Fable delegate: coordinator-priced tokens for executor work.
  Omission is a routing bug. Route by STAGE: explore/verify → `opus` (the agent types with `model: "opus"`; D-065),
  build → `code-implementer`, scouts/sweeps → `haiku`.

**Brief-writing, Claude-5 delegate tuning, SUCCESSION (no-Fable operation), parallel-agent
liveness, coordinator token economy, and the full ORCHESTRATOR protocol (worktree SHA pins ·
brief-as-file · push-reviewed-SHA-never-HEAD · vocabulary lock tests): skill `orchestration` —
load it before authoring any brief, dispatching agents, or pushing delegate work.** **Before any brief, interview seed or question to the owner, run `python3 scripts/owner_rulings.py <topic words>` (the owner's rulings on the topic, newest first; orchestration 0l): a question a ruling already answers is never asked (asked three times on 2026-09-25; the GPU window question was D-081's).** Standing
do-nots that must survive even without the skill loaded: delegates NEVER take outward-facing
actions (PRs, comments, publishing; the ONE carve-out, owner ruling 2026-09-07: a VERIFY lane may run
pytest-only gates on the PC through `scripts/pc_suite.sh launch|wait` — no other bridge use, no lane
dispatch, no server touch); long gates in ONE foreground call (a delegate that
backgrounds a run and stops is never rewoken by its completion); `git log origin/<branch>..HEAD`
before ANY push and push the reviewed SHA explicitly; commit+push BEFORE any multi-agent dispatch
(2026-09-02: a container restart killed a council agent mid-round with the brief's source doc
uncommitted — recover a dead agent's work from its transcript under the session tasks dir before
paying to re-run it).

## NO STUBS, NO FAKES, NO SHORTCUTS — SURFACE THE BLOCKER INSTEAD (NON-NEGOTIABLE, #1 RULE)

**NEVER replace a real component with a stub, fake, no-op, hardcoded value, tautology, or shortcut
to "get past" a blocker — not in benchmarks, not in harnesses, not anywhere.** A fake-substrate
result is worse than none: it mints a hollow green and destroys trust. **The hollow green lives in
PROSE too:** a doc/wiki/status/handoff that flatters the system (claims an unproven capability,
omits a known gap) is a hollow green in words — state gaps and NOT-built capabilities INSIDE the
artifact.

**On a blocker:** 1. STOP — never route around it with a fake. 2. SURFACE it: "This is a blocker:
<what/why>. I am NOT going to stub it." 3. Offer real options — fix the real integration, run it
where it CAN run (the PC over the bridge), or propose a research prompt (`docs/research/prompts/`);
and **pivot to the nearest REAL thing you CAN prove** so the turn still lands a genuine result.
4. Wait for direction rather than fabricating a pass.

**Every benchmark/eval MUST exercise the ACTUAL pipeline**, score against a **real independent
oracle**, and report the **hollow-green (gate-false-positive) rate**. A harness that
re-implements or stubs the spine it claims to prove is forbidden. In THIS project the
sanctioned stubs are TWO, both sitting BEHIND real OmniRoute at the boundary the plan itself specifies
(`docs/03` §2): S0-04's deterministic upstream-request-preservation instrument, and S0-01's deterministic
scripted model backend behind a dedicated OmniRoute test route (owner-sanctioned 2026-09-04 for the
golden, after two live runs proved the model route's ACP event structure non-reproducible) — every other
proof exercises the REAL pinned component, and a proof that cannot run in the sandbox runs on the PC or
is delivered as spec + fixture + an explicit `NOT run here: <reason>` marker, never a fake green.

**Tactic index — full text + war stories in skill `anti-hollow-green` (load when designing or
reviewing ANY gate/oracle/test/guard):**
1. Negative control on every gate; assert the EXACT error/exit-code; numeric guards reject the
   WHOLE unusable class (`isfinite` + positivity on the FINAL value — NaN is a fail-open wormhole).
2. Make cheating structurally impossible (env isolation, subprocess timeouts, verify STATE,
   AND-not-sum trust, `os.environ` is NOT a config channel — resolve once, thread explicitly).
3. Mutation-testing IS the hollow-green detector; a gate surviving no mutants is a tautology.
4. Oracle independent + un-importable; DROP an inapplicable assertion, never rewrite it.
5. No LLM-judge in the gate spine.
6. A stress benchmark's value is the defects it FORCES; a red first pass is the good outcome.
7. The tell: green without the claimed part actually running = capability does not exist.
8. Parameter/config DOMAINS are attack surface — validity floors locked by tests; a check run on
   one engine/instrument is blind to cross-instrument artifacts (two independent instruments for
   any reachability or containment claim).

## Project

Agent Factory is the planning-stage repo for a governed, memory-aware agent system. The live
pipeline: people in **Buzz** → `buzz-acp` → **Hermes** native ACP server (Hermes is the SOLE
stock production runtime) → every model request through **OmniRoute** → approved models —
with **Fubuki** supplying hash-pinned governance, **ai-memory** supplying the four logical
memory scopes via a first-party composite adapter, and every tool call passing a fail-closed
policy gate inside gVisor containment. A separate improvement plane (GBrain-informed dream
cycles → JIT Harness Foundry → isolated AlphaEval/PandaProbe evaluation → human promotion gate)
feeds reviewable proposals only; it has no production write or execution authority until later
gates pass. **The first application code exists** (the Stage 3 governance core under
`src/agent_factory/`, landed 2026-09-15 by D-029, its verify round pending) — the pipeline
(findings → council → Ouroboros interview → seed → task breakdown) is COMPLETE and the Stage 0
build continues; the first pending increment is named in the ledger.

### STANDING PROJECT RULES (the planning repo's own — binding on every harness; mirrored verbatim in `AGENTS.md` / `.hermes.md`)

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

### GROUND TRUTH — read in this order before ANY build work:
1. **`todo/BUILD-TASKLIST.md`** — THE build spine and the SINGLE SOURCE OF TRUTH for live build
   status (task count, what's done, what's pending) — this file is a distillation and will drift;
   the ledger wins on any count/status disagreement. TASK-DB MIRROR RULE: every task create and
   every status close is mirrored into its §LIVE ledger in the SAME increment; on every resume the
   task DB is restored FROM the ledger (+ the transcript's TaskCreate/TaskUpdate record), never
   from memory; task KEYS are SUBJECT SLUGS, never bare #N (slot numbers collide across
   containers). (New session: "read `todo/BUILD-TASKLIST.md`, load into the task list, start at
   the first pending task.")
2. **`docs/02_COMPONENT_AUDIT.md`** — the VERIFIED component inventory: read it FIRST among the
   plan docs, it corrects the v2 plan's optimistic claims. Then `docs/01_ARCHITECTURE.md` …
   `docs/11_DREAM_PHASE.md` (the CURRENT plan; reading order in `README.md`);
   `docs/07_BUILD_PLAN.md` is the staged backlog. **The current gate (narrowed by D-029, owner
   2026-09-15): spine-dependent feature work waits until the Stage 0 proof pack validates the
   Buzz→ACP→Hermes→OmniRoute spine, memory composition, Fubuki seams, policy failure behavior,
   and gVisor compatibility; a component whose Stage 0 proof is MINTED builds now, in its own
   lane, in parallel with the remaining proofs (first: GOV1, the Stage 3 governance core from
   S0-07).**
3. **`seeds/seed-stage0-v1.yaml`** (the Stage 0 contract — Ouroboros-generated, self-validation
   8/8, twelve per-proof blocks + the frozen `spike_to_class_mapping`) + **`tasks/stage0-breakdown.md`**
   (the 18-increment decomposition, pinned decisions with rejected alternatives, owner answers).
   The SEED is the full spec; the ledger distills it.
4. **`docs/research/FINDINGS-STAGE0-v1.md`** (capability ledger, environment table, per-proof
   constraints, Chairman-verified addenda) + **`docs/research/COUNCIL-VERDICT-STAGE0-v1.md`**
   (wave-plan-v2, kill criteria KC-1…KC-7) — why the plan has the shape it has.
5. **`docs/08_DECISION_LOG.md` + `docs/adr/`** — decisions with their reasons;
   `docs/09_PREMORTEM.md` — the failure-mode content (often the most valuable engineering read);
   `upstream.lock.yaml` — the exact upstream commits the audit inspected;
   `docs/archive/v2-original/` — the superseded v2 plan (LEAST reliable — preserved verbatim,
   corrected by the current docs). The rule that matters: **name which doc is ground truth and
   read it before planning.**

**Onboarding map (real files):**
- `todo/BUILD-TASKLIST.md` — build spine / start-here (above).
- `docs/INCIDENT-LOG.md` — the incident detail + this project's ANTI-PATTERN REGISTRY (`AF-AP-*`).
- `README.md` / `STATUS.md` — system-in-one-paragraph + reading order; what is complete /
  intentionally not complete / the next owner decision.
- `PC-BRIDGE.md` — the owner's PC (Fedora 42 bare metal, 12 cores / 125 GB / RTX 3090, podman
  5.7; OmniRoute on `:20128`, the Buzz relay stack, Ollama, Phoenix + OpenObserve, neo4j — all
  RUNNING, verified live 2026-09-03) is the EXECUTION HOST for containers, gVisor, the model
  egress, and every long/live job, reached through a token-gated HTTP bridge (`scripts/pc.sh`).
  Links + tokens are pasted per session into the untracked `.pc-bridge.env` — never committed.
- `docs/OBSERVABILITY-RUNBOOK.md` — the PC-side OpenObserve/Phoenix facts + the
  credential-staleness preflight lesson (no component ships telemetry to them yet — NOT built).
- `docs/HARNESS-PORTS.md` — the Codex CLI / Hermes Agent ports of this context (`AGENTS.md`,
  `.hermes.md`, `.agents/skills/` synced by `harness-ports/bin/sync-skills.sh`, `harness-ports/`
  adapters + lane roles + the PC-side spawn path `scripts/pc_lane.sh`): what each harness
  enforces and what it does NOT. Unit-proven in the sandbox (`harness-ports/tests/run-all.sh`);
  NOT smoke-tested on the PC — owner-run smoke steps are in the doc. **The three instruction files are
  gated (2026-09-15): `harness-ports/tests/test_context_mirrors.sh` holds section parity keyed off THIS
  file's `## ` list (a new section here with no mirror is red), the caps (`.hermes.md` ≤ 48,000 chars —
  Hermes drops an over-cap file's MIDDLE; `AGENTS.md` ≤ 32 KiB, Codex's budget) and the STANDING PROJECT
  RULES hash; it runs in `run-all.sh` and as the pre-commit MIRROR gate.** Hermes loads ONE project
  context type, `.hermes.md` first (its `prompt_builder.py`); `AGENTS.md` is Codex-only.
- `sandbox-kit/` — the vendored operating kit (operating guide, research-prompt guide + two
  worked examples, telemetry reference, vendored tools; provenance `sandbox-kit/VENDORED-FROM.md`).
- `wiki/` — the continuity spine: load `session-continuity` when updating `wiki/topics/live-state.md` or answering the
  retro gate (the per-commit freshness mandate, its hooks, the resume order).

## Environment & Tools (summary)

**COMPUTE PLACEMENT (owner ruling 2026-09-03: "the system is supposed to run on my PC, supposed
to use PC bridge").** Development + verification lanes stay in the sandbox (parallel delegates,
isolation, rollback safety); everything HEAVY or LIVE runs on the PC over the bridge — container
stacks (podman), gVisor/runsc, Rust builds against the owner's toolchain (rustup 1.95.0 is
there), model round trips, long suites. Every code-intel instrument runs on BOTH venues (owner directive
2026-09-07): `harness-ports/bin/pc-setup.sh` installs/builds them on the PC (digest-pinned sentrux + ripwire, the
four graphs, a stale graft/gitnexus index refreshed) so `scripts/lane_context.sh` works for the PC build lanes. **The model egress is the OmniRoute instance ALREADY
RUNNING on the PC (`:20128`)** — never a sandbox model server, and vLLM is NOT a dependency of
this project (owner ruling 2026-09-03: "just use omniroute"); S0-03's identity assertion is the
routed model id OmniRoute reports. Never stop or restart the owner's running servers (Buzz relay,
OmniRoute, Ollama, Phoenix, OpenObserve, neo4j; the `qwen-builder` model unit — a restart kills every lane mid-turn) without their say-so; `sudo` on the PC needs the
owner's password — surface it, never work around it; an owner-run package command is written with `-y` (`sudo dnf install -y …`): the owner's terminal does not take a typed answer at dnf's `[y/N]` prompt (2026-09-24, PC-BRIDGE.md).

Ephemeral container: `scripts/setup.sh` is the toolchain source of truth; commit and push anything worth keeping.
Load `env-tool-quirks` before using an ops script (resume-heal, orient, relaunch-suite, pc_suite, why,
replay_transcript_edits, lint_delta, verify-planning-repo, anchor_edit).

> **Full details:** `sandbox-kit/OPERATING-GUIDE.md` (day-to-day rules, shell/tool gotchas,
> GitNexus/Ouroboros fallbacks, task tracking, pipeline order).

**The PC bridge is this project's remote-execution host** (`PC-BRIDGE.md`; helper `scripts/pc.sh
'<cmd>'`; current link+token in the untracked `.pc-bridge.env`, pasted per session from the
owner's BRIDGE READY banner). Check it BEFORE declaring any environment blocker: "it won't
install here" → run it on the PC, don't route around it with a stub. No banner this session → the
PC-side items are `NOT run here` with the bridge named as the reason, never silently skipped.
**Deploy steps come FROM the runbook, not from memory.** Before deploying/restarting any remote
component, grep the runbook for that component first — the quirk you're about to re-learn is
usually already written down; re-reading beats re-deriving from memory.

**GitNexus** — 3-tier fallback (MCP → stdio `scripts/gn_mcp.py` → CLI `node .gitnexus/run.cjs`).
Run `impact` before editing a symbol, `detect_changes` before committing. Stale index? `analyze`.
**On this 3.8k-file tree `analyze` outlives the Bash tool's 240 s cap** (2026-09-03: "Terminated",
`run.cjs` absent) — run it detached (`nohup gitnexus analyze >/tmp/gitnexus-analyze.log &`, which
is what the post-commit hook and resume-heal do), never foreground. The index is dominated by
vendored code (`sandbox-kit/`, `.claude/`); read symbol counts with that in mind.
**Since CTX1 every automatic `analyze` passes `--skip-agents-md`** (post-commit, resume-heal, pc-setup): no analyze
rewrites CLAUDE.md or AGENTS.md, and a manual run takes the flag too. The post-commit hook re-indexes a graph only
when a commit changed a file it reads (a docs-only commit re-indexes none; `/tmp/post-commit-reindex.log`).

Load `ouroboros-stdio` before any Ouroboros interview round, fan-out submission, resume or seed generation (the stdio
client `scripts/ooo_mcp.py` and its measured quirks).

**Never use `AskUserQuestion` for interview routing or design decisions** — it blocks like MCP
(hang → timeout → lost requests). Ask in natural text; the user answers when back. During
interviews: numbered options in text; proceed autonomously on code-answerable questions (PATH
1a/1b); leave human-judgment questions (PATH 2 — real tradeoffs) as text for async answers.

**NEVER call manual-approval MCP tools from a CCR session (owner rule 2026-08-01, inherited) —
this includes the CCR trigger/scheduler tools (`send_later`, `create_trigger`, `update_trigger`,
`fire_trigger`, …) and ANY MCP tool that pops a permission prompt.** The approval prompt blocks
and SHUTS OFF THE SANDBOX — same failure class as AskUserQuestion. Use a CLI/stdio path instead
where one exists (the Ouroboros/GitNexus pattern above); where none exists, do WITHOUT the tool:
rely on subagent completion notifications for liveness, and ask the owner in plain text when a
scheduled nudge would otherwise be needed. Project-scope `.mcp.json` servers show "Pending
approval" in CCR — `scripts/setup.sh` registers the same servers at USER scope (graft, gitnexus,
aleph, codebase-memory, phoenix-docs, ouroboros) so they connect without a prompt; tools bind on
the NEXT session start.

Load `env-tool-quirks` before a background job, a `pgrep` or `pkill`, a commit, a push, an anchor edit, a test gate or
pasted count, a proof regeneration, a `vendored_manifest.py --write` or a worktree-isolated Agent dispatch.
Load `pc-bridge-lanes` before a `pc.sh`, `pc_lane.sh` or `pc_suite.sh` call, or a PC-side sqlite, systemctl or podman
command.
**Document quirks on contact, in the quirk skill** (shell, git, tool, test gate: `env-tool-quirks`; PC:
`pc-bridge-lanes`; Ouroboros: `ouroboros-stdio`), never here.

**Pipeline order is load-bearing: interview → SEED → task-breakdown → build.** To-dos come FROM
the seed.

**Task tracking** — keep the in-session TODO and project task list IN SYNC. After writing a task
breakdown (`tasks/*.md`), register every increment as a project task (TaskCreate) BEFORE building.
The breakdown is the design record; the task list is the execution tracker. Both must agree.
**TASK-SURFACE SYNC (owner ruling 2026-08-31, inherited: "keep them where they are now, but
update them more often").** The task surfaces stay AS-IS — no consolidation: `todo/BUILD-TASKLIST.md`
(SSoT), `tasks/*.md` breakdowns/briefs, the in-session task DB, and wiki live-state's active-lanes
block. The DUTY is freshness: when a task's status materially changes, the SAME increment updates
the ledger AND the task DB, and the wiki live-state at the next stop-gate; a `tasks/*.md`
breakdown whose work lands gets a one-line STATUS stamp at its top (date + outcome + commit)
rather than deletion. The in-session task DB is EXPENDABLE (container resets wipe it); on any
resume where it looks empty, rebuild it from the ledger + transcripts, never from memory. **The DB holds ACTIVE tasks only (2026-09-25, measured: the harness's task-list reminder re-sent 12.0% of this session's context tokens, `docs/research/findings/jev-pipes/CONTEXT-BUDGET-2026-09-25.md`): in flight or next up; the rest of the backlog stays open in the ledger and returns to the DB when it becomes active. Before that, open tasks only (2026-09-24, AF-AP-182's sibling): a task closed in the ledger is deleted from the DB (`TaskUpdate status=deleted`) in the same increment, because every task reminder repeats the whole list; 200 closed rows rode along in each reminder until then. A rebuild restores open tasks only.**

## Feature Workflow (summary)

Load `deep-work` before starting a substantial new subsystem or authoring a research prompt (audit → research prompt →
findings → council → Ouroboros interview → seed → task breakdown → hand-build).

Cross-cutting invariants: **no-LLM-judge spine · negative-control discipline · heavy jobs ON the PC.**

## Behavioral guidelines (Andrej Karpathy skills)

Load `build-loop` before writing code (the four behavioral guidelines: think before coding, simplicity first, surgical
changes, goal-driven execution; deep-mode governs on conflict).

## The meticulous build loop ("Fable light" — mandatory for every code increment)

**Full text + war-story evidence: skill `build-loop` — load it before any code increment.**

Load `build-loop` before any code increment, test or commit (its operative core moved there verbatim). The count and
stamp rule holds on every turn, so it stays here:

Test counts in reports and commit messages are PASTED from `scripts/test_summary.sh` output verbatim, never typed (AF-AP-37: '217 tests green' was a collection total). Timestamps are the same rule — pasted from `date -u` or the commit clock (2026-09-07: the day's ledger stamps drifted 2.8 h ahead); a ten-minute bucket comes from the clock too, `date -u +'%H:%M' | sed 's/[0-9]$/xZ/'`, never rounded up to the bucket an event is expected in (three ahead-of-clock stamps on 2026-09-25; the future-stamp gate blocked the one that reached a commit); a fourth at 04:5xZ, typed in the same call that ran `date`). **A stamp is SUBSTITUTED, never typed:** `export STAMP=$(date -u +'%H:%M' | sed 's/[0-9]$/xZ/')` and the text uses `$STAMP` (or `os.environ['STAMP']`) in the same command. **The Write tool cannot substitute:** a file written through Write takes its stamp from a `date -u` run just before it, pasted from that output, or is written through a Bash heredoc that expands `$STAMP` (the P1-R1 brief's premise heading, typed 09:2xZ at 09:18Z, the fifth; the future-stamp gate blocked the commit).

## The deep-work protocol ("Fable deep" — serious increments and reviews)

**Full text (Phases 0–6, retrospective rule, all meta-rules) + war stories: skill `deep-work` —
load it whenever the triggers below fire.** "Fable light" stays mandatory inside it; deep-mode
governs on conflict with the Karpathy guidelines.

**Invoke for:** new subsystems, gate/security/store spine changes, code review of a stretch,
anything where a wrong green is expensive, or on request. **Skip for:** doc edits, mechanical
renames, single-file obvious fixes (light loop still applies).

Load `deep-work` before a new subsystem, a gate, security or store spine change, a code review of a stretch, or any
work where a wrong green is expensive (the phase index moved there verbatim).

## Telemetry (summary)

> **Full specification:** `sandbox-kit/TELEMETRY-REFERENCE.md` (framework API, all 6 rules, standing loop).

The observability plane is PLANNED, NOT built (no component ships telemetry to the PC sinks yet).
Load `build-loop` before adding a decision path, an event or a span to a component (the five key rules).

## SESSION-RESUME CONTINUITY (owner mandate 2026-08-04, inherited)

**Load `session-continuity` on EVERY resume from a compaction summary, BEFORE any resumed work or timeline claim**
(fetch origin, compare the three clocks, re-read the PC bridge env). KEEP-ALIVE: owner-optional, NOT enabled.

## Project-specific incident log

**Full log: `docs/INCIDENT-LOG.md`** — the incidents behind the rules above, plus the
ANTI-PATTERN REGISTRY (`AF-AP-*`). **Log a one-line entry THERE the moment a rule above bites
for real** (trigger, rule confirmed, fix) — never defer it to a handoff doc. GENERAL rules
distilled from an incident still get baked into the matching skill/section; the log carries the
incident detail. Read the log before any work touching: the PC bridge (idempotent launches,
ephemeral links), Ouroboros stdio, GitNexus on this tree, multi-agent dispatch boundaries, S0-05
egress fixtures (bare `unshare --net` is TOTAL isolation — AF-AP-1), venue classification
(sandbox-probe-as-world — AF-AP-4).

## Code-intelligence — the QUARTET: Graft + GitNexus + Codebase-Memory + code-review-graph (USE RELIGIOUSLY — owner mandate 2026-07-28; Graft tight-integration mandate 2026-08-25; both inherited)

**GRAFT FIRST.** EVERY semantic code question ("who calls/sets/supplies X", "where is the seam
for Y", "how does Z resolve") goes to `graft ask "<question>"` (add `--source` / `--in <path>`)
BEFORE any grep/Read exploration. Bare Grep stays legal ONLY for literal-token sweeps (exact
strings, env-var names, JSONL/telemetry logs, non-code files) and as the named fallback while
`graft/INDEX.md` is absent (the PreToolUse hook `search-intercept.py`, JT3, answers semantic Grep/grep/rg searches graft-first with `graft-first-nag.py`'s classifier in-process; it is off while `.jev/intercept-off` exists).
One graft pack routinely saves ~100k+ tokens vs reading files whole. The source repo's
coordinator regressed to grep TWICE within hours of correction — if you are about to type a
Grep/sed call to answer code semantics, STOP and rewrite it as `graft ask`.

The owner's standing diagnosis: "there are probably holes everywhere — dead ends — we need to
map things out properly." The counter is MAPPING AS A REFLEX, not an occasional audit.
**Skill `code-intel-trio` is the operative guide** — which instrument for which question, the
exact invocations that work in this container (incl. every known arg/CLI quirk; project slug
`home-user-agent-factory`), and the fresh-container bootstrap. Load it before any Phase-1
grounding, impact analysis, dead-wiring hunt, or DORMANT claim. The core reflexes:

- Load `code-intel-trio` before any semantic code question, Phase-1 grounding, impact analysis, dead-wiring hunt or
  DORMANT claim, and when an MCP server fails to connect (the core reflexes; the CLI, not MCP, on every venue).
- **Project code lives under `proofs/`, `spikes/`, `scripts/`, `src/` (once it exists)** — the
  hooks and `orient.sh` key on those prefixes; everything under `sandbox-kit/`, `.claude/`,
  `graft/` is vendored and excluded from the wiki compiler and the edit-snapshot screen.

The GitNexus block below is injected every turn; its rules govern. **It is OURS since CTX1 (D-089):** every automatic
`gitnexus analyze` passes `--skip-agents-md`, the volatile counts line is gone (live counts: `gitnexus status`), and
it is edited by hand and kept last. `analyze` still rewrites the gitnexus-* skills; commit that churn.
Load `code-intel-trio` before editing this block (its pre-CTX1 wording, verbatim).

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

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

<!-- gitnexus:end -->
