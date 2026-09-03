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

- **Push only through `scripts/push_clean.sh --no-delegates-live`** (the ONLY argument it takes;
  set `PUSH_BRANCH=<branch>` when not on the branch). It strips model-identifier trailers from
  the unpushed range, proves tree identity across the rewrite, verifies zero trailers remain, and
  pushes the rev-parsed SHA — never `HEAD`. The pre-push hook BLOCKS any outgoing commit still
  carrying `Co-Authored-By: Claude` / `Claude-Session:` lines (owner policy: no model identifiers
  reach origin). Run `git log origin/<branch>..HEAD` before ANY push and review every unreviewed
  delegate commit first.
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

**STAGE ROUTING (owner ruling 2026-07-28, inherited with the setup): plan/orchestrate = Fable
(the main loop) · every EXPLORE/VERIFY lane = Opus 5 · every BUILD lane = Opus 4.6 ("throw the
problem and disappear") · Sonnet 4.6 over Sonnet 5 on the rare sonnet dispatch.** Opus 5
analyzes superbly but keeps making errors when left to build-and-fix alone; Opus 4.6 executes
reliably once pointed; Fable points them.

| Model / lane | Use for | Honey |
|---|---|---|
| **Fable 5** (main loop) | orchestration, plans, root-cause calls, design, final verdicts | `lite` — reasoning IS the deliverable |
| **Opus 5** — EXPLORE/VERIFY (`opus` tier, or agents `evidence-gatherer`/`adversarial-verifier`) | forensics, evidence tables, audits, premortems/roasts, adversarial review, every workflow verify stage | `full`: line-bounded findings, evidence anchors, SOLID/UNSURE |
| **Opus 4.6** — BUILD (agent `code-implementer` ONLY — the `opus` TIER resolves to Opus 5, so 4.6 rides the agent definition's literal model id) | fire-and-forget implementation lanes (code + deterministic test) | `ultra` Lever-2: report is DATA — files:lines, verbatim test counts, discrepancies, NOT-done |
| **Sonnet 4.6** (prefer over Sonnet 5 — owner assessment) | rare mid-complexity/mechanical follow-ups; `hive-builder` (≤2 files) | `full` |
| **Haiku 4.5** | `hive-scout`/`hive-reviewer` (read-only), locate/triage/classify, mechanical sweeps | `ultra`; returns = Lever-3 id-keyed JSON |

- The Agent tool exposes TIERS (`fable`/`opus`/`sonnet`/`haiku`); pinned versions (Opus 4.6,
  Sonnet 4.6) are reachable ONLY through `.claude/agents/*.md` frontmatter model ids — dispatch
  builds as `subagent_type: code-implementer` (Agent) / `opts.agentType: 'code-implementer'`
  (Workflow). The honey plugin's SubagentStart hook injects the honey mode into dispatches.
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
- **EXPLICIT `model=` ON EVERY DISPATCH.** A dispatch that omits `model` INHERITS the session
  model — an unrouted delegate is a Fable delegate: coordinator-priced tokens for executor work.
  Omission is a routing bug. Route by STAGE: explore/verify → `opus` (or the Opus-5 agents),
  build → `code-implementer`, scouts/sweeps → `haiku`.

**Brief-writing, Claude-5 delegate tuning, SUCCESSION (no-Fable operation), parallel-agent
liveness, coordinator token economy, and the full ORCHESTRATOR protocol (worktree SHA pins ·
brief-as-file · push-reviewed-SHA-never-HEAD · vocabulary lock tests): skill `orchestration` —
load it before authoring any brief, dispatching agents, or pushing delegate work.** Standing
do-nots that must survive even without the skill loaded: delegates NEVER take outward-facing
actions (PRs, comments, publishing); long gates in ONE foreground call (a delegate that
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
re-implements or stubs the spine it claims to prove is forbidden. In THIS project the one
sanctioned stub is S0-04's deterministic upstream-request-preservation instrument, which sits
BEHIND real OmniRoute at the boundary the plan itself specifies (`docs/03` §2) — every other proof
exercises the REAL pinned component, and a proof that cannot run in the sandbox runs on the PC or
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
gates pass. **No application code exists yet** — the pipeline (findings → council → Ouroboros
interview → seed → task breakdown) is COMPLETE and the Stage 0 build is the next work; the first
pending increment is named in the ledger.

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
   `docs/07_BUILD_PLAN.md` is the staged backlog. **The current gate: no broad feature work until
   the Stage 0 proof pack validates the Buzz→ACP→Hermes→OmniRoute spine, memory composition,
   Fubuki seams, policy failure behavior, and gVisor compatibility.**
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
  NOT smoke-tested on the PC — owner-run smoke steps are in the doc.
- `sandbox-kit/` — the vendored operating kit (operating guide, research-prompt guide + two
  worked examples, telemetry reference, vendored tools; provenance `sandbox-kit/VENDORED-FROM.md`).
- `wiki/` — **PER-COMMIT FRESHNESS MANDATE (owner 2026-08-25, inherited: "wiki is updated at
  every commit — that way it's never outdated").** A commit touching non-wiki files marks the
  wiki stale (post-commit hook writes `.git/wiki-stale`; ledger-plane appends, skill bakes and
  index-stamp churn are exempt); ship the wiki delta in the SAME increment wherever feasible;
  pre-push warns (blocks once `.git/wiki-gate-block` is armed) while stale. Hooks live in
  `scripts/hooks/` (activated by setup.sh via `core.hooksPath`); the same post-commit hook
  auto-reindexes graft + GitNexus in the background so the code-intel quartet never lags the
  tree. **WIKI-AS-CONTINUITY-SPINE (owner directive 2026-08-25, "smarter than transcript
  archaeology"):** `wiki/topics/live-state.md` is the turn-maintained continuity snapshot (active
  lanes, in-flight runs, pending owner decisions, clocks) — updated at the END of any turn that
  lands a material change (the Stop hook `turn-retro-gate.sh` blocks turn-end ONCE PER LANDED
  BATCH with the self-tuning retro checklist — wiki delta · bugs→registry/screen · nuance→matching
  SKILL · next-time-easier tooling — answered by DOING or an explicit "retro: nothing to bake";
  this mechanizes the deep-work retrospective rule); injected at every session start/compaction
  (`session-start.sh`) and relevance-matched wiki excerpts on every prompt (`wiki-context.py`,
  UserPromptSubmit). Resume order: wiki live-state FIRST for orientation, then the three-clock
  reconcile for VERIFICATION — the wiki is a map, never a substitute for primary-source checks.
  **Status: `wiki-init` has NOT run yet** (batch E of the setup port) — until `wiki/INDEX.md`
  exists the ledger is the only continuity source and the wiki hooks are silent by design.

## Environment & Tools (summary)

**COMPUTE PLACEMENT (owner ruling 2026-09-03: "the system is supposed to run on my PC, supposed
to use PC bridge").** Development + verification lanes stay in the sandbox (parallel delegates,
isolation, rollback safety); everything HEAVY or LIVE runs on the PC over the bridge — container
stacks (podman), gVisor/runsc, Rust builds against the owner's toolchain (rustup 1.95.0 is
there), model round trips, long suites. **The model egress is the OmniRoute instance ALREADY
RUNNING on the PC (`:20128`)** — never a sandbox model server, and vLLM is NOT a dependency of
this project (owner ruling 2026-09-03: "just use omniroute"); S0-03's identity assertion is the
routed model id OmniRoute reports. Never stop or restart the owner's running servers (Buzz relay,
OmniRoute, Ollama, Phoenix, OpenObserve, neo4j) without their say-so; `sudo` on the PC needs the
owner's password — surface it, never work around it.

Ephemeral container. `scripts/setup.sh` is the toolchain source of truth (the SessionStart hook
re-runs it every session; idempotent, tolerant). Commit and push anything worth keeping. The ops
scripts, all ported from the source repo and re-pointed at this one: `scripts/resume-heal.sh`
(the mechanical fresh-container resume in ONE command — ff-sync, hooks, venv, background
reindex; judgment steps stay yours) · `scripts/orient.sh` (three-layer startup orientation:
quartet liveness → chat intent via `chat_tail.py` → last commits → ready-to-run `graft ask`
suggestions; hooked at session start) · `scripts/relaunch-suite.sh` (the detached full suite,
`pytest proofs/ spikes/ tests/`, survives the Bash cap) · `scripts/why.sh <file> [fn]`
(on-demand chronology from primary sources) · `scripts/replay_transcript_edits.py` (recover a
dead delegate's edits from its transcript) · `scripts/lint_delta.py` (the pre-commit pyflakes
DELTA gate: new hits only) · `scripts/verify-planning-repo.sh` (the planning docs' own check).

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

**Ouroboros** — 3-tier fallback (MCP → stdio `scripts/ooo_mcp.py` → CLI `ouroboros`). **Always
prefer stdio** (`python scripts/ooo_mcp.py` — full MCP tool surface as JSON-RPC, no permission
gates; MCP tools hang on permission prompts when the user is away, the sandbox times out, and
in-flight requests are lost). **Stdio quoting:** shell expansion corrupts curly-brace JSON — write
it to a temp file: `JSONARG=$(cat /path/args.json) && python scripts/ooo_mcp.py tool_name
"$JSONARG"`. The interview tool starts with `initial_context` (not `topic`/`context`) and resumes
with `session_id` + `answer`.
**Ouroboros stdio quirks (hit 2026-09-02, all reproduced):** every `scripts/ooo_mcp.py` call that
drives the interview/seed backend needs `IS_SANDBOX=1` exported (the nested claude refuses
root+bypassPermissions; symptom: a question-less "cannot complete yet" reply) · `initial_context`
is capped (~1.5k chars) and an oversized one POISONS the session for every later round — start a
fresh interview and push detail through answers · each question issues a Synapse fan-out: submit
`{session_id, fanout_id, correlation_key:"context.lane_id", results:[{key, content}|{key,
undispatched:true}]}` covering the required lanes; `data_context` must match its contract exactly
(`{question_identity, lane_id, data_needed:false, no_evidence_reason, read_requests:[]}`) and the
`question_identity` lives in `~/.ouroboros/data/fanout/<fanout_id>.json` (read the registry
file — `ls -t` over tool-result files picked a stale one) · string values are rejected on shell
metacharacters (`;` `|` `&` backticks `$`) and certain WORDS ("subprocess" → "Potentially
dangerous input"; paraphrase) — scrub before submitting · nothing is retained between partial
submissions — resubmit every lane · `ouroboros_generate_seed` returns YAML and writes NO file —
transcribe to `seeds/` immediately and run the seed's own `verify_command`s (a red first pass is
the gate working: ours caught a missing per-proof section). **Resume uses the EXACT documented
arg shape** `{session_id, last_question, answer, ambiguity_score}` — a bare `{session_id,
answer}` resume and the `ouroboros_session_status` tool both report "No events found" even when
the session file exists under `~/.ouroboros/data/` (status reads a different store). Interview
rounds can take >3 min — run them as background Bash. **`ouroboros mcp serve` is broken in the
installed tool env** (MCP-SDK v2 vs the claude-sdk extra's v1.x — the user-scope MCP registration
shows CONNECTION_CLOSED every session); `scripts/ooo_mcp.py` auto-falls-back to an isolated
`uvx --from 'ouroboros-ai[mcp]'` server on that signature — expect the native attempt to fail
first (one stderr line): that is the fallback working. `scripts/patch_ouroboros.py` (run with the
ooo tool interpreter; setup.sh does it) applies the two idempotent upstream patches
(`sandbox-kit/OUROBOROS-SETUP.md`).

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

**Document quirks on contact.** Hit a tooling quirk (wrong arg name, quoting, API mismatch) →
immediately append a one-line fix to this file. Don't defer.
**A `pgrep -f <pattern>` liveness/wait loop MUST exclude its own command line** — bracket the
first char (`pgrep -f '[p]ytest ...'`) or match the binary with `-x` (two self-matching waiters
spun for a whole lane in the source repo).
**`git rev-parse --short REV1 REV2` fails ("Needed a single revision") in this container's
shell inside a compound command** — one rev-parse per call.
**push_clean can LOSE A RACE with the GitNexus banner rewriter:** AGENTS.md/CLAUDE.md index-stat
churn can regrow between its clean-check and filter-branch ("Cannot rewrite branches: You have
unstaged changes" → "N trailer(s) remain — ABORT"). Run `git checkout -- AGENTS.md CLAUDE.md &&
PUSH_BRANCH=<branch> bash scripts/push_clean.sh --no-delegates-live` as ONE compound command; on
that abort, re-check `git status` before suspecting real leftover trailers. It also REFUSES on a
dirty tree — commit or stash first (bit 2026-09-03).
**The shell's cwd resets to `/home/user` after a container restart** — start every command chain
with `cd /home/user/agent-factory` (or absolute paths).
**`rsync` is absent in the sandbox** — copy trees with `tar` / `cp -a`.

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
resume where it looks empty, rebuild it from the ledger + transcripts, never from memory.

## Feature Workflow (summary)

> **Full guide:** `sandbox-kit/RESEARCH-PROMPT-GUIDE.md` — read before authoring any research prompt.
> Two worked examples: `sandbox-kit/EXAMPLE-RESEARCH-PROMPT-SETTLED-SPEC.md` and
> `sandbox-kit/EXAMPLE-RESEARCH-PROMPT-EXPLORATORY.md`.

For any substantial new subsystem:
1. **Audit first** — read the actual code; write a grounded findings/plan doc.
2. **Research prompt** — `docs/research/prompts/RESEARCH-PROMPT-N.md`. SETTLE the direction; leave
   open ONLY the technical resolution. ONE self-contained file ending "Decide; do not ask."
   **ATTACH-TO-CHAT MANDATE (owner request 2026-08-28, inherited): every authored research prompt
   is ATTACHED to the chat (SendUserFile) in the same turn it is written — the owner pastes it
   into the research tool from the chat, never from the repo. Committing it is not delivery.**
   (Stage 0 ran with NO research prompt by owner decision 2026-09-02 — the plan docs were the
   settled direction; `docs/research/FINDINGS-STAGE0-v1.md` stood in for the findings.)
3. **Findings** — the returned report becomes the constraint set.
4. **Council debate** — `/council` on the FINDINGS (facts, not hypotheses). Never `--quick`. The
   brief carries a CURRENT-STATE CAPABILITY LEDGER (proven-live vs built-never-run vs absent) —
   an under-briefed panel returns confident advice about a system that doesn't exist.
5. **Ouroboros interview** — seeded with findings + verdict; drive `ambiguity_score` → ~0.
6. **Seed** — persist to `seeds/seed-<name>-vN.yaml`, commit, run its own `verify_command`s.
7. **Task breakdown** — decompose the seed BEFORE writing code; register the increments.
8. **Hand-build** — surgical, test-driven, one commit per increment; every acceptance test
   deterministic and LLM-free.

Cross-cutting invariants: **no-LLM-judge spine · negative-control discipline · heavy jobs ON the PC.**

## Behavioral guidelines (Andrej Karpathy skills)

Bias toward caution over speed; for trivial tasks, use judgment.

**1. Think Before Coding — don't assume, don't hide confusion, surface tradeoffs.** State
assumptions; if uncertain, ask. Multiple interpretations → present them, don't pick silently.
Simpler approach exists → say so; push back when warranted. Something unclear → stop, name it, ask.

**2. Simplicity First — minimum code that solves the problem.** No unrequested features,
abstractions for single-use code, speculative "flexibility", or error handling for impossible
scenarios. 200 lines that could be 50 → rewrite. Test: "would a senior engineer call this
overcomplicated?"

**3. Surgical Changes — touch only what you must; clean up only your own mess.** Don't "improve"
adjacent code/comments/formatting or refactor the unbroken; match existing style; mention (don't
delete) unrelated dead code. Remove imports/variables YOUR change orphaned; leave pre-existing
dead code. Test: every changed line traces to the request.

**4. Goal-Driven Execution — define success criteria, loop until verified.** "Add validation" →
"write tests for invalid inputs, make them pass"; "fix the bug" → "write a repro test, make it
pass"; "refactor X" → "tests pass before and after". Multi-step → a brief `[step] → verify:
[check]` plan. Strong criteria let you loop independently.

**Working if:** fewer unnecessary diff lines, fewer overcomplication rewrites, clarifying
questions BEFORE implementation.

When Fable deep-mode rules conflict with these (e.g. chasing a surfaced defect to its root vs
surgical changes), deep-mode governs — a real defect the wiring exposed is not scope creep.

## The meticulous build loop ("Fable light" — mandatory for every code increment)

**Full text + war-story evidence: skill `build-loop` — load it before any code increment.**
Model-agnostic, per increment, no skipping steps. The operative core:

1. **Verify every seam BEFORE writing code that calls it** — vendored-library seams get the
   `vendor-first` pass FIRST (the library probably already built it); read the real contract in
   the repo, from the CONSUMER; measuring inputs ≠ verifying the consuming contract; a test
   written from the code's own assumption is a MIRROR, not a gate. Durable records that guard
   IRREVERSIBLE side effects are written BEFORE the side effect, keyed by a pre-action id; the
   residual fails LOUD. When enriching a build (new rung/check/channel), emit only shapes that
   can actually fire — an emitted-but-unreachable check is a silent hollow green.
2. **One increment = code + deterministic LLM-free test + commit.** Negative control failing for
   the exact expected reason, de-vacuoused at write time; fixtures carry PRODUCTION data types;
   parity gates assert the oracle ACTED and pin discrete metrics EXACTLY; prove STATE and
   IDENTITY (and that the identity key COVERS the changing attribute); at least one negative
   control through the REAL emitter/sink. Commit message = reasoning record (rejected
   alternative, ordering rationale, primary source; enumerate disjoint hunks). Commit BEFORE any
   destructive probe. Deterministic tests: run twice, bitwise. Forced to commit mid-increment →
   embed recovery state in the message (acceptance bar + where it stands, WHY short, the plan).
3. **An unexpected test failure indicts YOUR assumption first** — ladder: telemetry → isolation →
   code; reproduce before believing any recorded diagnosis; `${PIPESTATUS[0]}`, never a piped rc.
4. **The live run is the real proof — live failures are FINDINGS.** Paired positive + negative
   control, exact outcomes asserted; assert the probe's INSTRUMENT fired (or find a structural
   signature only one mode can produce); resolve undocumented contracts from primary source;
   prove the fix at the OUTERMOST boundary where the failure was observed (here: the PC-side
   entry point over the bridge, not a narrower sandbox harness).
5. **Close the loop in writing — and ECHO before closing.** Any real defect this increment
   FOUND or FIXED (bug, wrinkle, wormhole, weird pattern) gets `/bug-echo` run on its
   anti-pattern and the class registered in the ANTI-PATTERN REGISTRY atop
   `docs/INCIDENT-LOG.md` BEFORE the increment closes — part of the validation contract in the
   LIGHT loop too, not just deep-mode Phase 5 (owner mandate 2026-08-20/21/22, inherited: the
   source repo's mega-sweep found unexploded siblings in ~half of all previously-fixed bug
   classes). Docs/runbook updated the moment the live proof lands; TODO ↔ task list synced; push;
   status lines open with the OUTCOME: `Verified live:` ≠ `DONE:` ≠ `NOT built.` (stated
   first-class). Ledger denominators are FOUR-WAY (execution / conformance-checked decision /
   blocked-on-external-input / blocked-on-capability) — never a flat count over the twelve proofs.

## The deep-work protocol ("Fable deep" — serious increments and reviews)

**Full text (Phases 0–6, retrospective rule, all meta-rules) + war stories: skill `deep-work` —
load it whenever the triggers below fire.** "Fable light" stays mandatory inside it; deep-mode
governs on conflict with the Karpathy guidelines.

**Invoke for:** new subsystems, gate/security/store spine changes, code review of a stretch,
anything where a wrong green is expensive, or on request. **Skip for:** doc edits, mechanical
renames, single-file obvious fixes (light loop still applies).

Phase index (each expanded in the skill):
- **Phase 0 — distrust is the method.** Admissible evidence = primary source or probe from THIS
  session. Unverified: numbers with no committed producer · absence off capped queries ·
  wrong-sink and wrong-token grep absences · hash-pinned values (integrity ≠ correctness — pinned
  external identifiers get re-resolved against a live primary source) · **the environment
  inventory read off the sandbox alone** (2026-09-03: the owner's PC held every "blocked"
  capability; probe the host and read the owner's runbooks before classifying a venue).
- **Phase 1 — ground.** Exact `file:line` seams; reachability traced from the LIVE entry point
  ("exists" ≠ "wired"); inventory what's already built — including what the OWNER already runs.
- **Phase 2 — measure before designing.** Value tables before constants; benchmarks at the
  PRODUCTION shape read from live telemetry; the cheapest order-changing reality probe FIRST
  (Stage 0's spike #0 was the bridge probe: it reclassified two proofs before increment 1);
  verify the consuming SELECTOR still discriminates; joint satisfiability for multi-constraint
  walls; escalate resolution, never mint a constant.
- **Phase 3 — blast radius before edit.** `impact` on every semantics-changing symbol;
  `detect_changes` before every commit.
- **Phase 4 — build (light loop), plus:** follow mid-build failure forks; prove "pre-existing"
  on the clean tree; spine behavior changes ship default-OFF; every fail-soft is fail-LOUD
  (config-presence ≠ delivery — acceptance-probe external sinks; events need a real, shared
  production sink); re-Read before Edit after out-of-band writes; pre-init every `finally` local.
- **Phase 5 — adversarial verify.** Done = a hostile reviewer failed to break it: loaded briefs,
  mutation audits (scratchpad-copy restore ONLY — never git-restore/stash a shared tree; never
  disable a guard while tests point at a real protected resource), independently reproduce every
  load-bearing claim AND its mechanism (the Chairman's netns probe was reproduced before it
  entered the findings), the kill-switch question on every green, symmetric finality gates,
  directionality checks on every risk cap, forensic pass on benchmark verdicts, **/bug-echo on
  every real defect FOUND — fixed or merely diagnosed**, **and a thermo-nuclear-review FULL-STACK
  pass before pushing any multi-commit stack (owner mandate 2026-08-26, inherited: the whole
  origin..HEAD diff through the skill's lens set on the verify lane, parallel with the final
  finding-driven verify, BOTH verdicts gating the push)**.
- **Phase 6 — close.** Affected suites + adjacent consumers; full tree at least once per wave;
  telemetry sufficiency; docs + task list same increment; wiki recompile; push; honest report
  including NOT-built.
- **Retrospective rule** — extract the alpha at every continuation/task-close/handoff; bake
  general lessons into the matching SKILL in the same increment; keep the protocol tight; no
  lesson → say so, never invent one.
- **Meta-rules** (all in the skill): structural membership for GC sweeps · bounded in-loop
  diagnostics · live-calibrated defaults · failure-aware waits (a wait's exit condition includes
  failure signatures — never success-only silence) · per-cycle caps in perpetual loops ·
  order-blind set-diff guards · clean checkpoints · handoff shape (read-order · pinned decisions
  with rejected alternatives · recovery rule per in-flight item · NOT-built ledger) · scope from
  primary source · raw output before filters · state-guards not flock for destroy-and-recreate ·
  `ps` liveness not output volume · no timing on a contended box · cap the solo probe loop at ~3
  falsified hypotheses, then delegate an instrumented-forensics agent with the evidence ledger.

## Telemetry (summary)

> **Full specification:** `sandbox-kit/TELEMETRY-REFERENCE.md` (framework API, all 6 rules, standing loop).

Treat the codebase like a PLC — every state, decision, transition externally observable.
Framework: the PandaProbe-based observability plane per `docs/06_EVALUATION.md` is PLANNED, not
built; until it lands every component emits structured JSON events carrying the reason field
(byte-invisible human plane), and the PC-side sinks (OpenObserve `:5080`, Phoenix `:6006`/`:4317`
— running, `docs/OBSERVABILITY-RUNBOOK.md`) receive nothing yet. Key rules:
1. **Every decision/branch/abstain/error emits a span or event carrying the REASON.** Silent
   decision paths are defects.
2. **No shallow spans** — stamp inputs, outcome, discriminating detail.
3. **Session context always attached** — `recording(input_hash, session_id=..., metadata={...})`.
4. **Byte-invisible** — human-plane keys never change committed bytes or force re-baselining.
5. **On every failure, assess telemetry sufficiency** — trace doesn't explain it → fix the
   telemetry gap FIRST.

## SESSION-RESUME CONTINUITY (owner mandate 2026-08-04, inherited)

**On EVERY resume from a compaction summary: fetch origin, then compare the three clocks
(origin tip date · local tip vs origin · transcript timestamps/day-histogram via
`scripts/chat_tail.py`) BEFORE any resumed work or timeline claim.** The summary AND the
workspace disk can both be rolled back behind the real session — they are the same stale snapshot
twice, not two confirmations. Origin ahead of memory = almost always YOUR OWN later work (one
chat, many containers); near-duplicate commit messages are rollback evidence, NOT a "parallel
session". The transcript JSONL (`/root/.claude/projects/-home-user*/…jsonl`) is the primary
source for session history and records every Write call's full content (lost briefs and dead
delegates' edits are recoverable from it — `scripts/replay_transcript_edits.py`). Mechanics:
`scripts/resume-heal.sh`; judgment: skill `session-continuity` — load it on every resume and
whenever owner statements or origin state contradict what you remember. Then re-read the PC
bridge env: a resumed session has NO bridge link until the owner pastes a fresh banner.

**KEEP-ALIVE (owner-optional, NOT enabled here).** The source repo runs two self-bind hourly
Routines that tick the session every 30 min until the build is done. This project has none: the
2026-08-01 trigger-tool caution stands in full until the owner explicitly asks for keep-alive
Routines (they are the one sanctioned exception when enabled; verify both exist on every resume
once they are).

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
`graft/INDEX.md` is absent (the PreToolUse hook `graft-first-nag.py` reminds you on code paths).
One graft pack routinely saves ~100k+ tokens vs reading files whole. The source repo's
coordinator regressed to grep TWICE within hours of correction — if you are about to type a
Grep/sed call to answer code semantics, STOP and rewrite it as `graft ask`.

The owner's standing diagnosis: "there are probably holes everywhere — dead ends — we need to
map things out properly." The counter is MAPPING AS A REFLEX, not an occasional audit.
**Skill `code-intel-trio` is the operative guide** — which instrument for which question, the
exact invocations that work in this container (incl. every known arg/CLI quirk; project slug
`home-user-agent-factory`), and the fresh-container bootstrap. Load it before any Phase-1
grounding, impact analysis, dead-wiring hunt, or DORMANT claim. The core reflexes:

- **GRAFT-FIRST FOR CODE QUESTIONS.** `graft ask "<question>" [--source] [--in <path>]` /
  `graft skeleton <file>` BEFORE any bare grep. Cold container: `graft build` backgrounds
  (setup.sh does this; log `/tmp/graft-build.log`) — check `graft/INDEX.md` exists before relying
  on it, and NAME the fallback instrument when graft wasn't available. MCP tools
  (`graft_find_code`/`graft_trace_calls`/…) register at user scope for the NEXT session; same-
  session use is the CLI. Provenance: `sandbox-kit/docs/THIRD-PARTY-AGENT-TOOLS.md` §Graft.
- **EDIT-SNAPSHOT hook (owner directive 2026-08-25):** every Edit/Write on a production `.py`
  auto-returns a snapshot — enclosing symbol's GitNexus blast radius + an anti-pattern-registry
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
- **After EVERY edit-batch, not just before commit:** `detect_changes`; re-`analyze` (detached)
  on a stale index. Before commit stays mandatory.
- **When grounding (Phase 1) or hunting dead wiring:** codebase-memory (`search_graph` /
  `query_graph` Cypher / `get_architecture`; prebuilt binary `/root/.local/bin/codebase-memory-mcp`,
  MCP connected at user scope) + code-review-graph (`/root/venv-crg/bin/code-review-graph query
  callers_of` / `tests_for` / `impact --files`); re-index after each landed increment so the map
  never lags the tree.
- **DORMANT/reachability claims need TWO independent instruments, named in the report** (e.g.
  crg `callers_of` AND a cbm Cypher trace) — never off one.
- Fallbacks (CCR sessions often drop MCP): GitNexus 3-tier (MCP → stdio `scripts/gn_mcp.py` →
  CLI `node .gitnexus/run.cjs`); codebase-memory prebuilt binary + crg venv are installed by
  setup. **If ALL tiers of the relevant tools are unreachable, say "unmapped — tool
  unavailable" in the report; never imply a mapped claim a tool didn't produce.**
- **Project code lives under `proofs/`, `spikes/`, `scripts/`, `src/` (once it exists)** — the
  hooks and `orient.sh` key on those prefixes; everything under `sandbox-kit/`, `.claude/`,
  `graft/` is vendored and excluded from the wiki compiler and the edit-snapshot screen.

The harness auto-injects the live GitNexus block (index stats + Always/Never-Do rules) every
turn — those rules govern; don't duplicate them here. GitNexus owns the flat
`.claude/skills/gitnexus-*/SKILL.md` set (exploring / impact-analysis / debugging / refactoring /
guide / cli) and rewrites the block below on every `analyze` — commit that churn, never hand-edit
it.

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

<!-- gitnexus:end -->
