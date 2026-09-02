# CLAUDE.md

> Filled instance of `sandbox-kit/CLAUDE.template.md` (vendored from `pxls21/sandbox-kit` @
> `aeb3082` — see `sandbox-kit/VENDORED-FROM.md`) for the **agent-factory** repo. The
> battle-tested protocol text travels VERBATIM; only project specifics were filled in. When a
> rule bites or a tooling quirk surfaces, extend THIS file in place (and the incident log below)
> in the same increment, the way the source repo does. Companion docs:
> `sandbox-kit/OPERATING-GUIDE.md` (day-to-day rules), `GITNEXUS-CLI.md`, `OUROBOROS-SETUP.md`,
> `RESEARCH-PROMPT-GUIDE.md` (+ the two `EXAMPLE-RESEARCH-PROMPT-*.md`),
> `BEHAVIORAL-GUIDELINES.md`, `TELEMETRY-REFERENCE.md`, and the vendored
> `council-of-high-intelligence/` and `llm-wiki-compiler/` tools. Keep it honest — every claim in
> here about what's built should stay independently verifiable, never aspirational.

Guidance for AI coding agents working in the **`agent-factory`** repo.

## SWARM ORCHESTRATION & HONEY (grounded vs installed Green-PT/honey-for-devs, 2026-09-02)

Honey modes: `lite|full|ultra` — no "medium". Levers: 1 less code (never off) · 2 less prose ·
3 dense agent-to-agent handoffs (id-keyed JSON/ESON). A reflexive writing style, not a runtime
switch — never spend reasoning tokens on it; step UP a mode when terseness would cost correctness.
Safety carve-outs (auth, secrets, validation, migrations, deletes, explicit asks) never compressed.

Model routing — cheapest tier that cannot mint an expensive wrong green; honey mode per role:

| Model / tier | Use for | Honey |
|---|---|---|
| **Fable** (main loop) | orchestration, root-cause, design calls, final verification | `lite` — reasoning/explanation IS the deliverable |
| **Opus 4.8** — explorer | long-context forensics, multi-file tracing, hard debugging, audits | `full`: line-bounded findings, evidence anchors, SOLID/UNSURE |
| **Opus 4.6** — executor | spine-critical surgical increments (code + deterministic test) | `ultra` Lever-2: report is DATA — files:lines, verbatim test counts, discrepancies, NOT-done |
| **Sonnet** | mid-complexity builds, test authoring, docs; `hive-builder` (≤2 files) | `full` |
| **Haiku** | `hive-scout`/`hive-reviewer` (read-only), locate/triage/classify, mechanical sweeps | `ultra`; returns = Lever-3 id-keyed JSON (address by `id`, aggregate in code, check `n`) |

- THIS harness's Agent tool exposes TIERS (`fable`/`opus`/`sonnet`/`haiku`) — 4.6-vs-4.8 pinning
  applies where a config takes a model id (e.g. a self-hosted model-server endpoint pinned to a
  specific model); otherwise both profiles ride the `opus` tier and the role lives in the brief.
  Inject the honey mode into each dispatch BRIEF by hand (no SubagentStart hook ships with this kit).
- Escalate a tier when: spine/gate/security files touched · an increment failed review · cross-file
  semantics. De-escalate for mechanical follow-ups. Hive never touches the spine; no tier
  self-accepts spine work — the coordinator re-runs gates regardless (Reflection Firewall:
  file:line refs, ≤2-sentence summaries, never re-paste code). Disjoint file boundaries per agent;
  root-cause + design + final verification stay in the main loop.

Self-correction: monitor child output for degradation (redundant code, dropped imports,
vibes-not-evidence); feed each increment's mistake-patterns into the next brief as do-nots; this
block is editable inline from telemetry. Savings numbers: never hand-estimate token savings — a
number with no COMMITTED meter is unverified; measure with real telemetry or report "unmeasured".
`hive-*` are role LABELS for briefs, not shipped agent types (define your own under
`.claude/agents/` if you want them installable). To-dos come FROM the Ouroboros seed;
status lines are outcome-first (`Verified live:` / `DONE:` / `NOT built.`), never narratives.

**SUCCESSION — no-Fable operation (the standing goal: the tier below must not need the tier
above).** Every protocol in this file is model-agnostic BY CONSTRUCTION — quality tracks the
brief and the gates, not the coordinator's tier. When Opus coordinates:
1. **Never self-accept.** The coordinator's own spine/design work gets an INDEPENDENT
   same-or-higher-tier adversarial review (loaded brief: files:lines, suspicions, demanded
   runnable evidence) before commit — the role split substitutes for the judgment gap.
2. **Replace judgment with STRUCTURE.** Anything the top tier would have eyeballed becomes
   2-of-3 diverse-lens verification (correctness/security/repro) + deterministic gates; when
   reviewer intelligence drops, RAISE gate teeth (negative controls, mutation audits,
   identity assertions) — never lower the bar to match the reviewer.
3. **Tables decide, not intuition.** The Phase-2 measured-value-table discipline is the
   design-call substitute: read the decision off the table; ambiguous table → escalate to the
   human as a PATH-2 text question rather than deciding.
4. **Briefs are the interface.** Pre-flight every brief against the orchestrator checklist
   (verified seams, prior mistake-patterns as do-nots, evidence demands, foreground long
   gates); an under-briefed strong model loses to a well-briefed cheap one.
5. **Keep compounding.** The retrospective rule runs identically — bake lessons here in the
   same increment; the protocol is the institution, the coordinator is replaceable.

## NO STUBS, NO FAKES, NO SHORTCUTS — SURFACE THE BLOCKER INSTEAD (NON-NEGOTIABLE, #1 RULE)

**NEVER replace a real component with a stub, fake, no-op, hardcoded value, tautology, or shortcut
to "get past" a blocker — not in benchmarks, not in harnesses, not anywhere.** A fake-substrate
result is worse than none: it mints a hollow green and destroys trust. **The hollow green lives in
PROSE too:** a doc/wiki/status/handoff that flatters the system (claims an unproven capability,
omits a known gap) is a hollow green in words — state gaps and NOT-built capabilities INSIDE the
artifact.

**On a blocker:** 1. STOP — never route around it with a fake. 2. SURFACE it: "This is a blocker:
<what/why>. I am NOT going to stub it." 3. Offer real options — fix the real integration, run it
where it CAN run (e.g. a bridged/remote host), or propose a research prompt (`docs/research/prompts/`);
and **pivot to the nearest REAL thing you CAN prove** so the turn still lands a genuine result.
4. Wait for direction rather than fabricating a pass.

**Every benchmark/eval MUST exercise the ACTUAL pipeline**, score against a **real independent
oracle**, and report the **hollow-green (gate-false-positive) rate**. A harness that re-implements
or stubs the spine it claims to prove is forbidden.

### Anti-hollow-green TACTICS — operational checklist (every gate, oracle, test, increment)

1. **Test the UNHAPPY path.** Every gate needs a NEGATIVE CONTROL: PASS a compliant fixture AND
   FAIL a violating one — never ship a check with one leg. Assert the EXACT error/exit-code, not
   merely "it failed". Cover null/bad-input/timeout branches, not just the golden path.
2. **Execution guards — make cheating structurally impossible, not policy-forbidden.** (a) Isolate
   the env so the agent can't inject the expected result. (b) Timeouts on every subprocess — hollow
   code hides in loose loops. (c) Verify STATE, not returned flags — check the artifact actually
   changed. (d) A gain on one axis NEVER converts to trust on an orthogonal axis — combine
   quality×confidence with AND (a ceiling), never a sum.
3. **Mutation-testing IS the hollow-green detector.** Inject bugs into the code-under-gate; a gate
   that still passes is hollow. Demand BRANCH coverage. A gate surviving no mutants is a tautology
   — reject it.
4. **Ban hardcoded expected outputs.** The oracle is spec-authored, independent, un-importable by
   the thing it grades. **4a. DROP an inapplicable assertion, NEVER REWRITE it** (rewriting lets
   the graded artifact choose its own oracle value). Drop ONLY when: (a) change provably scoped,
   (b) ≥1 retained assertion is INVARIANT to the change, (c) the reduced gate still fails an
   empty/mutant workflow. Fail any leg → abstain, never mint.
5. **No LLM-judge in the gate spine.** Gate/oracle/assertion execution is deterministic
   exit-code / set-hash comparison; an LLM enters ONLY at codify/generate/tune time.
6. **A stress benchmark's value is the defects it FORCES, not the green it prints.** Design the
   matrix to hunt (adversarial cases, cross-family negatives, modified-requirement asks); a red
   first pass is the expected good outcome.
7. **The tell:** if a green was produced without the part it claims to need actually running (kill
   the model mid-graft and it still "succeeds"; disable the store and cost is unchanged), the
   capability does not exist — that is a falsification to REPORT, never a number to tune past.

## Project

Agent Factory is the planning-stage repo for a governed, memory-aware agent system. The live
pipeline: people in **Buzz** → `buzz-acp` → **Hermes** native ACP server (Hermes is the SOLE
stock production runtime) → every model request through **OmniRoute** → approved models —
with **Fubuki** supplying hash-pinned governance, **ai-memory** supplying the four logical
memory scopes via a first-party composite adapter, and every tool call passing a fail-closed
policy gate inside gVisor containment. A separate improvement plane (GBrain-informed dream
cycles → JIT Harness Foundry → isolated AlphaEval/PandaProbe evaluation → human promotion gate)
feeds reviewable proposals only; it has no production write or execution authority until later
gates pass. **No application code exists yet** — this pass is architecture, contracts, and the
staged build plan.

Ground truth, in order of reliability: `docs/01_ARCHITECTURE.md` … `docs/11_DREAM_PHASE.md` are
the CURRENT plan (most reliable; the reading order is in `README.md`);
`docs/02_COMPONENT_AUDIT.md` is the VERIFIED component inventory — read it FIRST, it corrects
the v2 plan's optimistic claims; `docs/08_DECISION_LOG.md` + `docs/adr/` record why;
`docs/09_PREMORTEM.md` is the failure-mode content (often the most valuable engineering read);
`upstream.lock.yaml` pins the exact upstream commits the audit inspected;
`docs/archive/v2-original/` is the superseded v2 plan (LEAST reliable — preserved verbatim,
corrected by the current docs). The rule that matters: **name which doc is ground truth and read
it before planning.**

**Onboarding map:**
- `README.md` — system-in-one-paragraph, what changed from v2, and the canonical reading order.
- `STATUS.md` — what is complete / intentionally not complete / the next owner decision.
- `wiki/INDEX.md` — compiled codebase wiki once `wiki-init` has run; recompile at every
  natural stopping point (Phase 6 of the deep-work protocol below).
- `docs/07_BUILD_PLAN.md` — the staged backlog. **The current gate: no broad feature work until
  the Stage 0 proof pack validates the Buzz→ACP→Hermes→OmniRoute spine, memory composition,
  Fubuki seams, policy failure behavior, and gVisor compatibility.**
- `docs/08_DECISION_LOG.md` + `docs/adr/` — decisions with their reasons.
- `sandbox-kit/` — the vendored operating kit this repo's workflow comes from (operating guide,
  research-prompt guide, vendored tools; provenance in `sandbox-kit/VENDORED-FROM.md`).
- Remote-execution bridges, if any get set up later (heavy jobs on a bridged host/VM): keep that
  runbook alongside this kit under its own name — the kit deliberately ships no bridge doc,
  because bridge topology is entirely project-specific. None exists today.

## Environment & Tools (summary)

Ephemeral container. `scripts/setup.sh` is the toolchain source of truth — author it for this
project's actual stack (see `sandbox-kit/OPERATING-GUIDE.md` for the pattern: a SessionStart hook
re-runs it every session). Commit and push anything worth keeping.

> **Full details:** `sandbox-kit/OPERATING-GUIDE.md` (day-to-day rules, shell/tool gotchas,
> GitNexus/Ouroboros fallbacks, task tracking, pipeline order).

**Remote-execution bridges, if you set any up** — keep one canonical current-links doc (bridge
URLs are usually ephemeral quick-tunnels) and check it BEFORE declaring any environment blocker:
"it won't install here" → run it on the bridge, don't route around it with a stub.
**Deploy steps come FROM the runbook, not from memory.** Before deploying/restarting any remote
component, grep the runbook for that component first — the quirk you're about to re-learn is
usually already written down; re-reading beats re-deriving from memory.

**GitNexus** — 3-tier fallback (MCP → stdio `scripts/gn_mcp.py` → CLI `node .gitnexus/run.cjs`).
Run `impact` before editing a symbol, `detect_changes` before committing. Stale index? `analyze`.

**Ouroboros** — 3-tier fallback (MCP → stdio `scripts/ooo_mcp.py` → CLI `ouroboros`). **Always
prefer stdio** (`python scripts/ooo_mcp.py` — full MCP tool surface as JSON-RPC, no permission
gates; MCP tools hang on permission prompts when the user is away, the sandbox times out, and
in-flight requests are lost). **Stdio quoting:** shell expansion corrupts curly-brace JSON — write
it to a temp file: `JSONARG=$(cat /path/args.json) && python scripts/ooo_mcp.py tool_name
"$JSONARG"`. The interview tool starts with `initial_context` (not `topic`/`context`) and resumes
with `session_id` + `answer`.

**Never use `AskUserQuestion` for interview routing or design decisions** — it blocks like MCP
(hang → timeout → lost requests). Ask in natural text; the user answers when back. During
interviews: numbered options in text; proceed autonomously on code-answerable questions (PATH
1a/1b — e.g. df pooling when the architecture makes it obvious); leave human-judgment questions
(PATH 2 — real tradeoffs, e.g. hybrid pruning) as text for async answers.

**Document quirks on contact.** Hit a tooling quirk (wrong arg name, quoting, API mismatch) →
immediately append a one-line fix to this file. Don't defer.

**Pipeline order is load-bearing: interview → SEED → task-breakdown → build.** To-dos come FROM
the seed.

**Task tracking** — keep the in-session TODO and project task list IN SYNC. After writing a task
breakdown (`tasks/*.md`), register every increment as a project task (TaskCreate) BEFORE building.
The breakdown is the design record; the task list is the execution tracker. Both must agree.

## Feature Workflow (summary)

> **Full guide:** `sandbox-kit/RESEARCH-PROMPT-GUIDE.md` — read before authoring any research prompt.
> Two worked examples: `sandbox-kit/EXAMPLE-RESEARCH-PROMPT-SETTLED-SPEC.md` and
> `sandbox-kit/EXAMPLE-RESEARCH-PROMPT-EXPLORATORY.md`.

For any substantial new subsystem:
1. **Audit first** — read the actual code; write a grounded findings/plan doc.
2. **Research prompt** — `docs/research/prompts/RESEARCH-PROMPT-N.md`. SETTLE the direction; leave
   open ONLY the technical resolution. ONE self-contained file ending "Decide; do not ask."
3. **Findings** — the returned report becomes the constraint set.
4. **Council debate** — `/council` on the FINDINGS (facts, not hypotheses). Never `--quick`.
5. **Ouroboros interview** — seeded with findings + verdict; drive `ambiguity_score` → ~0.
6. **Seed** — persist to `seeds/seed-<name>-vN.yaml`, commit.
7. **Task breakdown** — decompose the seed BEFORE writing code.
8. **Hand-build** — surgical, test-driven, one commit per increment; every acceptance test
   deterministic and LLM-free.

Cross-cutting invariants: **no-LLM-judge spine · negative-control discipline · heavy jobs on a
bridged host, if one is ever set up (none exists today).**

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

Model-agnostic, per increment, no skipping steps.

1. **Verify every seam BEFORE writing code that calls it.** Read the actual
   signature/regex/contract in the repo — never code from memory or a doc (memory-written code has
   been silently dead; the real contract differed). Doc vs code disagree → code wins, doc gets
   fixed. **When enriching a build (new rung/language/channel/check), guard against
   dead-on-arrival artifacts at GENERATION time: emit only shapes that can actually fire** (e.g.
   scope emission to the parent shape) — an emitted-but-unreachable check is a silent hollow green.
2. **One increment = code + deterministic test + commit.** Test is LLM-free, in-sandbox, with a
   NEGATIVE control failing for the exact expected reason (e.g. a synthetic mutant workflow whose
   gate runs RED and provably never touches the cwd). **De-vacuous the control at WRITE time:** if
   the "failing" fixture passes through an unintended independent code path it proves nothing —
   rebuild it so the guard-under-test is the ONLY reason it fails. Prove STATE, not returned flags
   — assert the file/store/tree changed — **and prove IDENTITY, not just success**: on any path
   that selects/serves/recalls an entity, assert it is the exact entity claimed (id/intent/
   content-hash), never merely that *something* came back (a tier-only assertion passed while the
   WRONG entity served; a surviving SSE badge is not a surviving transcript — status persistence
   is not state persistence). **The commit message IS the reasoning record:** name the rejected
   alternative, the exact level/ordering rationale, and the primary source consulted (e.g.
   "behavioral-build outranks grep because it exercises a real compile; source: the installed
   language-pack"). Several legitimate changes in one file → enumerate disjoint hunks ("TWO logical
   changes: 1… 2…"); a load-bearing ordering decision also gets a comment at the decision SITE.
   Keep commits surgical and cherry-pickable. Commit BEFORE any destructive probe or mutation audit
   touches the same files. **Deterministic-fixture tests (seeded RNG, captured trace, golden
   output): run twice, assert bitwise-identical, before trusting baselines.** **Forced to commit
   mid-increment:** embed recovery state in the message — (a) the acceptance bar + where the result
   stands, (b) WHY it falls short, (c) the concrete plan — "needs redesign" alone forces a full
   re-analysis on the successor.
3. **An unexpected test failure indicts YOUR assumption first — debugging ladder: telemetry →
   isolation → code.** Read the trace FIRST (a 10-line stage_event spy) — a well-instrumented
   failure NAMES the branch (`abstain_divergent_top` pointed straight at the P5.1 guard). Then
   layered isolation probes: rebuild with the smallest REAL-component pipeline, binary-search layer
   by layer, never a mock. **Reproduce before believing any RECORDED diagnosis** — a handoff's
   root cause is a symptom report, not a mechanism; re-derive live (a past handoff named the wrong
   layer). Then probe the actual runtime value (5-line REPL), fix the root cause, not the assertion.
4. **The live run is the real proof — live failures are FINDINGS, never noise.** After
   deterministic green, run the real thing (bridged host / live smoke): paired positive + negative
   control, exact outcomes asserted (oracle rc==0, file present / model blocked, no file) — **and
   assert the probe's INSTRUMENT actually produced the condition under test** (a mode-marker flip,
   not just surviving content: an emulated-browser resize never crossed the CSS breakpoint, so the
   first rotation "survival" proved nothing). A live
   break on an undocumented contract → **resolve from primary source** (read the installed
   package: docs said dict, the package returned an object needing attribute access). Never paper
   over a live failure with a retry or shape guess. **Prove the fix at the OUTERMOST boundary
   where the failure was observed** — re-run the exact entry point that failed (server E2E, full
   solve()), not a narrower harness (a bug "fixed" twice at an inner layer was still broken at the
   outer entry point).
5. **Close the loop in writing.** Update runbook/status docs the moment the live proof lands (a
   doc still saying "blocked" after the fix is a defect); sync TODO with task list; push; stop and
   report. **Status lines open with the OUTCOME, tagged by verification level:** `Verified live:`
   (real path) ≠ `DONE:` (tests green) ≠ `NOT built.` (absent/dormant, stated first-class). The
   verdict leads; the story follows.

## The deep-work protocol ("Fable deep" — serious increments and reviews)

The full method, written as an executable protocol for ANY model — a discipline, not a capability.
"Fable light" stays mandatory inside it. Deep-mode governs on conflict with Karpathy guidelines.
**Invoke for:** new subsystems, gate/security/store spine changes, code review of a stretch,
anything where a wrong green is expensive, or on request. **Skip for:** doc edits, mechanical
renames, single-file obvious fixes (light loop still applies).

**Phase 0 — the prime directive: distrust is the method.** Every artifact is guilty until probed:
docs lie, summaries lie, your memory lies, YOUR OWN earlier conclusions lie, subagent reports lie,
and a green test is the most practiced liar. Admissible evidence = a primary source read this
session or a probe run this session; everything else is hypothesis. **A number with no COMMITTED
producer is UNVERIFIED** — trace every load-bearing figure to its committed producer or re-measure
(the "live token savings" traced to an uncommitted wrapper; honest status was "meter DOES NOT
EXIST", which changed the plan). **ABSENCE read off a capped/paginated query is UNVERIFIED
absence** — before reasoning from "not there", prove the window covered the target (server-side
filter, page to exhaustion, or returned-count < cap); a `first:N` span read minted a false
"spans lost" claim when they sat just past the cap, mis-framing a root-cause.

**Phase 1 — ground (read before you think).**
- **Locate the exact seam first** — the `file:line` where the change lands; a plan naming modules
  but not lines is not grounded.
- **Trace reachability, never assume it.** "Exists" ≠ "wired": grep the call graph from the LIVE
  entry point. A function only tests call is dead code — say so. An import-identity-only test is
  PAPER wiring.
- **Inventory what is already built:** one line per touched component — "we already have X
  (`module:fn`) — it does Y" — before designing anything that could duplicate it.

**Phase 2 — measure before designing.**
- **A design decision that depends on a quantity gets the actual table first.** 10-line probe,
  print the value for EVERY corpus item, read the decision off the table. Never a constant from
  intuition — place it in a measured gap (genuine matches 0.6+, impostors ≤0.25, threshold in the
  empty gap).
- **Front-load the single cheapest probe whose result changes the build ORDER; run it BEFORE
  increment 1** (the "reality probe": run the known-broken artifact + captured test under the
  sandbox — RED means the negative control is already real; GREEN means the behavioral increment
  is load-bearing now). It reorders the plan, so it precedes the first commit.
- **State assumptions; probe the riskiest one first** — 5-line REPL before dependent code.
- **A failed quantitative gate gets per-item root-cause before redesign.** For each item on the
  wrong side (each surviving mutant/false positive): WHY, and what flips it; verify the aggregate
  clears the bar; only then implement. Cap 2 redesign iterations; <20% of the remaining gap per
  iteration → escalate the question (threshold wrong for this class, or approach wrong?).
- **A failed discriminator: print the value table and read the fix off it — escalate resolution,
  never mint a constant.** Progression: boolean → class levels → the continuous MARGIN of an
  existing calibrated artifact (rank by λ̂ − dist rather than adding a hand-tuned threshold beside
  a calibration). **A razor-thin residual gap is the TELL of a boundary, not a threshold site** —
  the signal hit its ceiling; the fix is a NEW orthogonal signal of a different KIND.

**Phase 3 — blast radius before edit.** Impact analysis (GitNexus `impact`, grep-for-callers
fallback) on every symbol whose SEMANTICS change; read every caller. `detect_changes` before every
commit. HIGH/CRITICAL risk gets said out loud with why it is safe.

**Phase 4 — build (light loop per increment), plus:**
- **A mid-build failure is a fork you FOLLOW, not noise to suppress.** Ask if it exposes a defect
  ELSEWHERE (fixture, matcher, broken contract) and chase THAT root (a wiring test failing on an
  unrelated entity exposed a fundamentally weak matcher — fix was a measured redesign, not a
  patched assertion). **Before calling a surfaced failure "pre-existing", PROVE it: reproduce on
  the clean tree (stash/checkout base), confirm identical crash** — then fix in-band as a
  separately-enumerated hunk.
- **Editing a test to pass requires proving the TEST was wrong** (e.g. golden data violating a
  newly-and-correctly-enforced contract), stated in the commit message.
- **A correct precision veto AFTER arbitration becomes a recall collapse — check gate PLACEMENT
  against the candidate LIST, not the single winner.** Any fail-closed filter: does a correct
  rejection of the top candidate fall through to the next, or kill the request?
- **Behavior changes to a golden-traced/bench-contracted spine ship library-default-OFF with an
  env opt-in at the deployment unit** (a default-ON change broke frozen contracts; default-OFF +
  opt-in gave the live fix with zero re-baselining). Committed attrs on hot spans go on the human
  plane unless re-baselining is intended.
- **Every fail-soft is fail-LOUD.** Graceful degradation (embedder won't load → BM25-only;
  optional channel off) MUST emit an explicit logged event naming what degraded and why, plus an
  env opt-out where sensible. Invisible degradation is a hollow-green factory and a defect.
- **Re-Read before Edit after ANY out-of-band write to the same file** (a restore/codegen script
  ran → the editor snapshot is stale; the next Edit rejects or applies against unseen content).

**Phase 5 — adversarial verify (the audit swarm). Done ≠ tests pass; done = a hostile reviewer
failed to break it.**
- **Dispatch scoped review agents in parallel, one dimension each** (typical trio: logic/table
  correctness on tricky inputs · live-path reachability · hollow-green mutation audit). A good
  brief: exact files/functions/lines; your suspicions to confirm/refute; demands runnable-probe
  EVIDENCE, severity, a concrete failing input per claim; and a list of what was verified SOLID
  (silence ≠ checked). Vague brief → vibes; loaded brief → evidence. Same rule for councils and
  research dispatches: the brief carries a CURRENT-STATE CAPABILITY LEDGER (proven-live vs
  built-never-run vs absent) — an under-briefed panel returns confident advice about a system that
  doesn't exist.
- **Mutation-audit every new test suite.** Inject targeted bugs one at a time (tautology the
  check, delete the guard, drop the wiring), record which test kills each, restore, end
  `git status`-clean. A surviving mutant = a hollow test = fix NOW. **Restore discipline
  (NON-NEGOTIABLE — made twice):** restore mutants from a SCRATCHPAD COPY only — `cp` aside before
  the first mutant, `cp` back after each; NEVER `git checkout/restore` a file carrying uncommitted
  work (git restores the COMMITTED version and vaporizes the increment). Best: commit before the
  audit. Watch the vacuous-negative-control trap: a fixture so broken it fails through an
  independent path proves nothing (a PARTIALLY broken fixture isolating the guard is the honest
  control).
- **Never accept an agent finding unverified.** Agents establish where to look; YOU establish what
  is true: independently reproduce every load-bearing claim, and spot-check at least one "SOLID"
  claim. **A delegate's evidence paths/labels are part of the claim** — verify the artifact exists
  at the stated path before trusting the finding (scouts twice reported screenshot paths that
  didn't exist; the real evidence lived elsewhere and once said the opposite).
- **The kill-switch question, on every green:** what is the cheapest way this could have passed
  without the real capability running? If you can name one, add the control that kills it.
- **Forensic pass on benchmark/acceptance verdicts before reporting.** A machine verdict is a
  CLAIM: (a) workspace artifacts match the verdict (bytes, not flags); (b) cost/timing numbers
  cross-referenced against the authoritative source; (c) the baseline was fair — a control arm
  hiding a graded requirement is a rigged experiment; (d) the mechanism path (graft fired, model
  blocked, oracle ran) matches the claim. Fix the experiment and re-run rather than adjust
  thresholds.

**Phase 6 — close.** Re-run affected suites AND adjacent consumers; `detect_changes`; telemetry
sufficiency check ("if this failed in prod tonight, would the trace explain it?" — no → the
missing span is part of THIS increment); docs + task list in the same increment; **recompile the
wiki** (`/wiki-compile`); push; report HONESTLY — including what is NOT built (dormant seams,
deferred scope), never letting "tests green" stand in for "capability exists".

**The retrospective rule — extract the alpha at the end of EVERY sprint.** Triggers: (a) after
every context continuation (first action — lessons freshest); (b) after closing any task >3
increments; (c) before writing any handoff. None fired → session end.
- Two questions: (1) what hard lesson did this stretch produce (mistake, surprise, repeated
  friction, plan-changing probe)? (2) what worked unusually well and should become standard?
- **Bake answers into the protocol IN THE SAME INCREMENT** — general rules here; project-specific
  operational facts in the matching runbook/handoff. A lesson recorded only in a handoff WILL be
  re-learned the expensive way (the mutation-restore mistake was made twice for exactly this).
- **Prefer the GENERAL form** (project example in parentheses as evidence). Only-makes-sense-here
  → runbook, not protocol.
- **Keep the protocol tight:** fold into an existing rule where one fits; a bloated protocol stops
  being read. No lesson → say so; never invent one.

**Context/risk management (meta-rules):**
- **A wait/poll on an external condition must trigger on FAILURE states too, never only success.**
  Success-only silence is ambiguous between "working" and "dead" (a dead dev-server looked like a
  slow compile for 14 minutes). Every wait's exit condition includes failure signatures; a long
  wait → read the LOG, not the monitor.
- **Stop at clean checkpoints.** Never half-build a coupled subsystem late in a session — record
  the settled design on the task (decisions, rejected alternatives, exact seams) and stop. A
  delayed increment beats a rushed gate; be most suspicious of your work when you most want to be
  finished. On low context or a natural stop, LAND: tree clean, full status in TEXT, stop.
- **A handoff doc has a fixed SHAPE** (so a cold successor inherits the *why* and the
  *what-if-I-died*): (1) READ-ORDER up top; (2) PINNED-DECISIONS — each settled constant WITH its
  rejected alternative; (3) every IN-FLIGHT item carries a RECOVERY rule, not just status ("if
  uncommitted when you arrive: REVIEW + re-run their gates + commit each boundary; if absent,
  rebuild from the breakdown"); (4) the honest NOT-built ledger + open-ends keyed to task IDs.
- **Scope the next stage from PRIMARY SOURCE before promising it** — locate the real seams
  (`file:line`) first; let findings resize the plan.
- **Parallel agents for breadth, yourself for depth — and CAP the solo probe loop.** Fan out for
  reading/searching/auditing; design decisions, root-cause calls, final verification stay in the
  main loop. After ~3 FALSIFIED hypotheses on one defect, stop probing and delegate an
  instrumented-forensics agent carrying the full evidence ledger (every probe, result, and killed
  hypothesis) — the ledger is what makes the handoff cheap and the next probe non-redundant (an
  xterm render-loss defect ate 7 main-loop probes before the handoff that should have come at 3).
  Never probe files an agent is concurrently mutating (check `git status` before trusting any
  probe during a mutation audit).
- **Coordinator token economy: the main loop AUTHORS and VERDICTS; it does not EXECUTE.** "Final
  verification stays in the main loop" means reading evidence and issuing the verdict — not
  personally driving every probe/deploy. Mechanical execution (browser-probe plans, VM
  deploy/relaunch sequences, screenshot fetching, gate re-runs) goes to a cheap delegate carrying
  the exact plan + expected outcomes; the coordinator reads the returned steps.jsonl/log lines and
  spot-checks ONE artifact. Coordinator-priced work is only: designs, briefs, dry-run plan
  reviews, security/spine hunk reads, and the kill-switch question on every green.
- **The ORCHESTRATOR protocol (proven over a full MVP sprint): delegate the bulk to well-briefed
  agents, keep review + the hardest seams yourself.** (a) Disjoint file boundaries per parallel
  agent — conflict-free by construction; commit one boundary while another runs. (b) The brief
  carries seams YOU verified + prior mistake-patterns as do-nots (delegates repeat mistakes you
  don't name). (c) Review = re-run the gates yourself + read only security/spine-critical hunks —
  where every real delegate defect was caught (dead-wire tier check, jail escape,
  fabricated-green risk); never accept "all green" without your own gate run. (d) Background-agent
  liveness = transcript-file mtime probe (never read the transcript — context overflow). A stalled
  agent's EXTERNAL artifacts persist — recover by inspecting what it left and finishing lean, not
  re-running from scratch. **Brief delegates to run long gates (full pytest etc.) in ONE foreground
  call — a delegate that backgrounds a run and stops is NEVER rewoken by its completion; it sits
  stalled until the coordinator messages it (two executors parked this way in one sprint).** (e) Commit at every boundary between agent handoffs — a dirty tree
  across turn-ends burns quota and blocks committing finished work. (f) **A push publishes EVERY
  local boundary, reviewed or not: run `git log origin/<branch>..HEAD` before ANY push** and review
  each unreviewed delegate commit first (a routine push once shipped two unreviewed spine commits
  that happened to be sound — the check is one command, the alternative is luck).

## Telemetry (summary)

> **Full specification:** `sandbox-kit/TELEMETRY-REFERENCE.md` (framework API, all 6 rules, standing loop).

Treat the codebase like a PLC — every state, decision, transition externally observable.
Framework: PandaProbe-based observability plane, per `docs/06_EVALUATION.md` — PLANNED, not yet
built; until it lands, every component emits structured JSON events carrying the reason field
(byte-invisible human plane). Key rules:
1. **Every decision/branch/abstain/error emits a span or event carrying the REASON.** Silent
   decision paths are defects.
2. **No shallow spans** — stamp inputs, outcome, discriminating detail.
3. **Session context always attached** — `recording(input_hash, session_id=..., metadata={...})`.
4. **Byte-invisible** — human-plane keys never change committed bytes or force re-baselining.
5. **On every failure, assess telemetry sufficiency** — trace doesn't explain it → fix the
   telemetry gap FIRST.

## Project-specific incident log (`agent-factory`)

> Institutional memory: the incidents behind the rules above. **Log a one-line entry here the
> moment a rule above bites for real** — which section/rule it confirms, the concrete trigger, the
> fix — don't defer it to a handoff doc; a lesson recorded only there WILL be re-learned the
> expensive way (see the deep-work protocol's retrospective rule, above). This section starts
> EMPTY on purpose — the entries below are one illustrative example, not this project's history;
> replace them with your own first incident on contact.

- *(illustrative example — replace with your project's real first entry)* **Rule 1 (verify seams)
  — an idiom mismatch.** Memory-written code assumed one write idiom (e.g. a heredoc); the actual
  call site used another (e.g. `printf`) — the "safety" code was silently dead until a
  seam-verification pass caught it. Fix: read the real contract before writing code that calls it.

## Code-intelligence — GitNexus

`<This block is normally AUTO-GENERATED by GitNexus's `analyze` step (repo name,
symbol/relationship/flow counts, Always/Never-Do usage rules, resource URIs). No code exists to
index yet — run `node .gitnexus/run.cjs analyze` (or `npx gitnexus analyze`) once the first
implementation code lands, delete this placeholder paragraph, and let `analyze` create the block
fresh — don't hand-author the stats.>` Use the tool's MCP/CLI to
understand code, assess impact, and navigate safely; the rules below are GitNexus's own and are
portable if you adopt it:

**Always Do:** MUST run `impact({target, direction: "upstream"})` before editing ANY
function/class/method — report blast radius (callers, processes, risk) and WARN the user on
HIGH/CRITICAL before proceeding (never ignore those warnings). MUST run `detect_changes()` before
every commit (regression review vs default branch: `detect_changes({scope: "compare", base_ref:
"main"})`). Exploring unfamiliar code → `query({search_query})` (process-grouped, ranked) instead
of grep; full symbol context (callers/callees/flows) → `context({name})`; security review →
`explain({target})` (taint source→sink; needs `analyze --pdg`).
**Never Do:** edit a symbol without `impact` first · ignore HIGH/CRITICAL warnings · rename with
find-and-replace (use `rename` — call-graph aware) · commit without `detect_changes()`.

**Resources** — `gitnexus://repo/agent-factory/context` (codebase overview, index freshness) ·
`…/clusters` (functional areas) · `…/processes` (execution flows) · `…/process/{name}`
(step-by-step trace).
**CLI skills**, if vendored (`.claude/skills/gitnexus/gitnexus-<name>/SKILL.md`): `exploring` —
architecture / "how does X work?" · `impact-analysis` — blast radius / "what breaks if I change
X?" · `debugging` — trace bugs / "why is X failing?" · `refactoring` — rename/extract/split ·
`guide` — tools, resources, schema · `cli` — index, status, clean, wiki commands.
