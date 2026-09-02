---
name: deep-work
description: The deep-work protocol ("Fable deep") — general-purpose, any project: Phases 0-6 plus the retrospective rule and the operational meta-rules, full text with war-story evidence. Load for new subsystems, gate/security/store spine changes, code review of a stretch, root-cause investigations, anything where a wrong green is expensive, long-running probes/measurements, GC/retention sweeps, handoffs, or session close-outs. CLAUDE.md carries the trigger list and phase index — this skill is the authoritative expansion.
---

# The deep-work protocol ("Fable deep" — serious increments and reviews)

The full method, written as an executable protocol for ANY model — a discipline, not a capability.
The build-loop skill ("Fable light") stays mandatory inside it. Deep-mode governs on conflict with
the Karpathy guidelines. **Invoke for:** new subsystems, gate/security/store spine changes, code
review of a stretch, anything where a wrong green is expensive, or on request. **Skip for:** doc
edits, mechanical renames, single-file obvious fixes (light loop still applies).

**Phase 0 — the prime directive: distrust is the method.** Every artifact is guilty until probed:
docs lie, summaries lie, your memory lies, YOUR OWN earlier conclusions lie, subagent reports lie,
and a green test is the most practiced liar. Admissible evidence = a primary source read this
session or a probe run this session; everything else is hypothesis. **A number with no COMMITTED
producer is UNVERIFIED** — trace every load-bearing figure to its committed producer or re-measure
(the "live token savings" traced to an uncommitted wrapper; honest status was "meter DOES NOT
EXIST", which changed the plan). **ABSENCE read off a capped/paginated query is UNVERIFIED
absence** — before reasoning from "not there", prove the window covered the target (server-side
filter, page to exhaustion, or returned-count < cap); a `first:N` span read minted a false
"spans lost" claim when they sat just past the cap, mis-framing a root-cause. **Same rule for the
WRONG-SINK variant: before claiming an event never fired, trace the emitter's actual routing to
its sink** — multi-plane telemetry (per-run events vs runner-level runtime_events vs OTel) means a
clean grep of ONE file proves nothing about emission (a warm_start grep of the per-run events.jsonl
nearly minted "reseed never fired" while the events sat in runtime_events.jsonl — `_emit_stage` →
`emit_runtime_event` routes to a different plane than `ctx.events`). **And the WRONG-TOKEN
variant: a label/codename grep absence is not capability absence** — search for the artifacts the
capability would PRODUCE (function names, files, `git log --grep`), and cross-check the task
ledger before consuming any delegate's "X does not exist" (an evidence pass grepped `trading/`
for the literal "ST7" and reported the gene-registration scaffold absent; it lives at
`scripts/gene_scaffold.py` without that token, the ledger showed #291 completed, and the false
premise reached an interview answer before the ledger contradiction caught it). **A HASH-PINNED
VALUE is INTEGRITY-verified, NOT CORRECTNESS-verified** — the pin freezes a wrong value exactly as
firmly as a right one, and every pinned-hash gate stays green over garbage. Any pinned registry of
external identifiers (token mints, feed ids, pool/contract addresses) must be verified against a
LIVE PRIMARY SOURCE — that the identifier actually RESOLVES to the claimed asset — not merely
eyeballed at author time (DX11c: the DX3-pinned Solana USDC mint was truncated by one char
`…Dt1`→`…Dt1v`, resolved to NOTHING on GeckoTerminal, yet passed the DX3 self-review and every
hash gate for four increments — caught only when a downstream cross-check re-resolved it live).

**Phase 1 — ground (read before you think).**
- **Locate the exact seam first** — the `file:line` where the change lands; a plan naming modules
  but not lines is not grounded.
- **Trace reachability, never assume it.** "Exists" ≠ "wired": grep the call graph from the LIVE
  entry point. A function only tests call is dead code — say so. An import-identity-only test is
  PAPER wiring.
- **Inventory what is already built:** one line per touched component — "we already have X
  (`module:fn`) — it does Y" — before designing anything that could duplicate it.

**Phase 2 — measure before designing.**
- **A process ordered killed is a measurement asset — profile it BEFORE killing it.** A live
  process exhibiting the defect at production shape is the one profiling substrate no fixture
  reproduces; py-spy it first, kill second (2026-08-26 K4 speed wave: the 90s pre-kill profile
  pinned metrics-extraction 32% / occupancy-telemetry 16% / GPU-sim 4.5% and made both fix
  briefs evidence-based; killed first, the same evidence needs a full relaunch to recover).
- **py-spy reading discipline (2026-08-26 W5 hunt, three bites in one wave):** (a) speedscope
  frames key by (name, file, CURRENT line) — per-frame totals are LOWER BOUNDS per function;
  re-aggregate by (name, file) before ranking, and never read "A% < B%" across functions as a
  containment contradiction. (b) SELF time at a call line means the callee has no Python frame
  — that is native/jitted CALLEE time (numba kernel, C encoder, deviceSynchronize), not
  dispatch overhead at that line; verify what the line IS before naming the mechanism (the
  "5% launch overhead" was the kernel's execution wall; "iterencode 2.5%" was the C encoder
  attributed to its wrapper). (c) a micro-benchmark that reuses one instance measures the warm
  cache, not production (per-fold Portfolios are cold — real cost was 2.4x the in-repo bench);
  bench with a fresh instance per iteration when production constructs fresh.
- **A design decision that depends on a quantity gets the actual table first.** 10-line probe,
  print the value for EVERY corpus item, read the decision off the table. Never a constant from
  intuition — place it in a measured gap (genuine matches 0.6+, impostors ≤0.25, threshold in the
  empty gap).
- **A benchmark justifying an optimization MUST run at the PRODUCTION SHAPE, and the shape must be
  read from LIVE TELEMETRY, never chosen for fixture convenience — pin EVERY size dimension in the
  brief, not just the obvious one.** A speedup that decays with a size parameter is not a speedup,
  it is a CROSSOVER, and a fixture below the crossover reports the opposite of the truth (#365: the
  M2 signal batching measured 2.1x at 3 symbols x 2000 bars and shipped that as its justification;
  the same code is 1.42x at production's 5300 bars — read off a live `multi_symbol_alignment`
  event — 0.97x at 10000 and 0.86x at 17559, i.e. a SLOWDOWN. My own brief caused this: it pinned
  the genome count "≥64, ideally 560" and said nothing about bar count). Corollary: **an
  optimization whose sign depends on a data-shape parameter ships FLIPPABLE at the deployment
  seam** — a later data change (here, backfilling history) silently inverts it, and an
  unconditional default gives no way to back out without a code change.
- **Front-load the single cheapest probe whose result changes the build ORDER; run it BEFORE
  increment 1** (the "reality probe": run the known-broken artifact + captured test under the
  sandbox — RED means the negative control is already real; GREEN means the behavioral increment
  is load-bearing now). It reorders the plan, so it precedes the first commit.
- **State assumptions; probe the riskiest one first** — 5-line REPL before dependent code.
- **A failed quantitative gate gets per-item root-cause before redesign.** For each item on the
  wrong side (each surviving mutant/false positive): WHY, and what flips it; verify the aggregate
  clears the bar; only then implement. Cap 2 redesign iterations; <20% of the remaining gap per
  iteration → escalate the question (threshold wrong for this class, or approach wrong?).
- **A timing bucket named after its EXPECTED dominant component hides everything else in it —
  decompose to the level where a decision changes, and name each part by what it DOES.** An
  aggregate phase is not a measurement, it is a hypothesis with a stopwatch on it; optimising
  against one is optimising against the name (#373: `sim_s` was 47% of every generation, so three
  waves of work aimed at the simulation and its GPU kernel — the decomposition showed the metric
  READOUT inside it costs 25% of a generation, 1.5x the `simulate()` call, while the GPU kernel is
  ~3.6%; the readout had ALREADY been vectorised ~23x and was still second-largest). Corollary: a
  residual you cannot name is not "overhead", it is the part you have not measured.
- **Before tuning ANYTHING an optimizer consumes, verify the operator that consumes it can still
  DISCRIMINATE.** Objectives, constraints, weights, floors, reference directions are all downstream
  of a selection/ranking step, and a degenerate selector is invisible to every value-level health
  metric — spread, diversity, feasibility and distinct-value counts all look perfect while the
  search has zero pressure. Measure the SELECTOR's own output distribution (rank/front sizes,
  tie counts, how many candidates the comparator can actually separate), not just the values fed
  to it, and verify it with a brute-force reimplementation before acting (#372: 495/495 and
  560/560 of the population sat in ONE non-dominated front with literally zero dominating pairs,
  so 90 generations of "plateau" was Pareto ranking contributing nothing and niching random-walking
  the bests — every objective-level table looked healthy the whole time).
- **A search stuck at zero under MULTIPLE hard constraints: measure the JOINT satisfiability
  frontier, never tune one constraint at a time.** Individually-reasonable constraints can
  conjoin to EMPTY over real data, and fixing the currently-binding one just moves the wall
  (#351: activity floor → sharpe leg — two valleys, one mechanism). The degenerate-selection
  telltale is min==median violation across the population (duplicate collapse: an all-infeasible
  pop under feasibility-first survival is greedy scalar truncation with no niching). The probe is
  a per-item PAIRED readout (each candidate's distance to EACH constraint), shipped as a
  telemetry increment so one live cycle prints the decision table.
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
  the clean tree (via `git show HEAD:<file>` to scratchpad — never stash/checkout a shared tree),
  confirm identical crash** — then fix in-band as a separately-enumerated hunk.
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
  **CONFIG-PRESENCE IS NOT DELIVERY: a plane that ships to an EXTERNAL sink needs a one-shot
  ACCEPTANCE probe at init, not just a "is it configured?" check** — a batching/background
  transport reports rejection asynchronously, per-batch, into its own logger, so the run's own
  telemetry cannot see it and every config assertion stays green over a dead plane. Probe the
  cheapest thing that proves ACCEPTANCE and nothing else (verify the discriminator against the
  real sink FIRST), and fail CLOSED on rejection — "on but rejected" hides the failure again
  (2026-07-25: `TRADING_OTEL=1` + valid endpoint + a headers value + `otel_degraded`=0, while
  every OTLP POST answered 401 because the credentials file had gone stale against its container;
  a whole day of spans lost, and it was the SECOND half-fix on that seam — flag, then
  endpoint+headers, then credentials actually accepted, each found only by trying to USE what the
  previous fix claimed to restore).
  **A discrete event whose ONLY production sink is a throwaway default reaches NO consumer —
  emitting it is half the fix; trace the LIVE wiring to a real sink.** An injectable `event_sink`
  that the live entrypoint leaves `None` collapses back to a per-instance logger (identical to the
  pre-event log line the event was meant to replace); test-only injection is a reachability
  hollow-green. Verify the production caller injects a real/shared sink — and that sibling
  components share ONE instance, not two private defaults (DX11e: `run_dex_execution` left
  `build_aggregate_source`'s `event_sink=None`, so the new `DexLegUnconfiguredEvent` and the
  aggregate's staleness events each hit a separate throwaway `LoggingEventSink`; the fix injected
  one shared `OTelSinkBridge(LoggingEventSink())`, the codebase's live-consumer seam).
- **Re-Read before Edit after ANY out-of-band write to the same file** (a restore/codegen script
  ran → the editor snapshot is stale; the next Edit rejects or applies against unseen content).
- **Every local a `finally`/cleanup block references must be pre-initialized BEFORE the `try` —
  an exception raised inside `finally` SUPERSEDES the in-flight exception,** so one missing
  pre-init turns every early failure into the same unrelated UnboundLocalError and the real
  error becomes invisible (dex_exec crashed 5/5 restarts showing only 'watchdog'; the true
  startup failure surfaced only after the pre-init fix). Audit the cleanup path's reads against
  the pre-init block whenever either changes; test = an early-raise probe asserting the ORIGINAL
  exception type propagates.

**Phase 5 — adversarial verify (the audit swarm). Done ≠ tests pass; done = a hostile reviewer
failed to break it.**
- **BUG-ECHO ON EVERY REAL DEFECT — FOUND, not just fixed (owner mandate 2026-08-20, widened
  2026-08-21).** The moment a genuine defect is FOUND — fixed or merely diagnosed, bug or
  wrinkle or weird pattern — run `/bug-echo` (or its inline equivalent: derive the
  anti-pattern from the defect's mechanism, validate it matches the defective code, sweep the
  relevant chain, classify each match individually) BEFORE closing the increment. A real
  defect is proof the pattern matters in THIS codebase; its unexploded siblings are the
  cheapest bugs you will ever find. Evidence: 2026-08-20 — one test-fixture fix (f7944a00)
  echoed into 3 production BUGs on the champion chain; 2026-08-21 — the full-history mega
  sweep (bafa14a0) found unexploded siblings in 6 of 13 swept classes (~half of every fixed
  bug had a live copy). Register every new class in the ANTI-PATTERN REGISTRY at the top of
  `docs/INCIDENT-LOG.md` (id, one-line mechanism, greppable signature, proven instance) in
  the SAME increment — the registry is the sweep corpus for the next echo. Skip only for
  doc/rename/pure-test edits with no behavioral pattern.
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
  work (git restores the COMMITTED version and vaporizes the increment). `git stash` is the same
  vaporization class on a shared tree — to prove a failure pre-existing, copy the committed
  version out via `git show HEAD:<file>` to a scratchpad path and test THAT; never mutate the
  shared tree (a delegate stashed a tree carrying two other agents' uncommitted work). **Never
  run a guard-DISABLING mutant while any test points the guarded code at a REAL protected
  resource** — repoint to a tmp copy first, or the mutant defeats the very protection under test
  (a disabled live-dir gate let the audit write into the hash-pinned compliance config). Best:
  commit before the audit. Watch the vacuous-negative-control trap: a fixture so broken it fails
  through an independent path proves nothing (a PARTIALLY broken fixture isolating the guard is
  the honest control).
- **Never accept an agent finding unverified.** Agents establish where to look; YOU establish what
  is true: independently reproduce every load-bearing claim, and spot-check at least one "SOLID"
  claim. **A delegate's evidence paths/labels are part of the claim** — verify the artifact exists
  at the stated path before trusting the finding (scouts twice reported screenshot paths that
  didn't exist; the real evidence lived elsewhere and once said the opposite). **The finding's
  stated MECHANISM is itself a load-bearing claim — re-derive it from primary source, not just its
  existence; a right-smell/wrong-mechanism finding points at a REAL defect but its proposed fix can
  be dead code, so verify the mechanism and RE-DERIVE the fix (DX8b-2: a MEDIUM "+inf slips the
  `<=0` guard into sizing" was, on re-derivation, an uncaught OverflowError — expo-bounded scaling
  can't reach +inf — so the agent's proposed isfinite guard would have been unreachable; the real
  fix was catching OverflowError, and the isfinite guard belonged at a different, reachable boundary).**
- **The kill-switch question, on every green:** what is the cheapest way this could have passed
  without the real capability running? If you can name one, add the control that kills it.
- **A fail-loud/finality gate that protects against ROLLBACK must be SYMMETRIC across outcomes.**
  Gating only the outcome whose early-acceptance is the obvious hazard leaves the MIRROR hole: the
  other outcome, acted on early + paired with state cleanup, can be equally unsafe when the same
  under-committed event later flips (DX10-D2: gating a Solana SUCCESS on `>= confirmed` but
  returning a REVERT at any commitment let a `processed`-err orphan re-land as SUCCESS after the
  revert row was already deleted → double-swap). Likewise a DANGER-vs-CLEAN classification on a
  safety control needs BOTH-direction tests — a false positive breaks autonomy, a false negative
  breaks safety; testing only the ACTION it dispatches (not the DECISION) is a hollow green.
- **A cap/ceiling that limits EXPOSURE must not gate the action that REDUCES it — check every
  risk gate's DIRECTIONALITY.** A deployment/growth ceiling (max capital-at-risk, max position,
  max aggregate) is meaningful only on the INCREASING side; applying it to a reducing/exit/close
  action is a safety INVERSION — a "risk control" that blocks de-risking, the exact opposite of
  its purpose (DX13: the aggregate-exposure cap gated exit SELLs identically to entry BUYs, and
  because the position is still open at check-time, `projected = current_exposure + sell_notional`
  REJECTED the very exit needed to cut a loss — a losing position could not be flattened). The
  guard: thread the order side/`is_reducing` into the check and skip the growth ceiling for a
  reduction (only bad-data guards still apply); test that the exact order REJECTED as an increase
  PASSES as a reduction. Also mirrors the fail-open-cap rule — a cap VALUE is externally-sourced
  too: guard it `isfinite` AND positive at construction, not just the injected input (a NaN cap in
  a `min()` masks a finite sibling and disables the gate).
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
deferred scope), never letting "tests green" stand in for "capability exists". **At least once
per wave, run the FULL tree, not just affected suites** — per-suite gates are structurally blind
to cross-suite env leaks and to stale pins in suites nothing recently touched (one sweep caught
both: a secrets-API test leaking HL_API_URL two suites downstream, and an arb-suite 52-gene pin
red since the 59-gene expansion because that suite sat outside every per-suite gate).

**The retrospective rule — extract the alpha at the end of EVERY sprint.** Triggers: (a) after
every context continuation (first action — lessons freshest); (b) after closing any task >3
increments; (c) before writing any handoff. None fired → session end.
**MECHANIZED 2026-08-25 (owner directive):** the Stop hook `turn-retro-gate.sh` now fires this
rule's checklist once per landed commit-batch — wiki delta · bugs→registry/screen ·
nuance→matching skill · next-time-easier tooling. The hook is the floor, not the ceiling:
answer by DOING, or by an explicit "retro: nothing to bake"; never by dismissing the gate.
- Two questions: (1) what hard lesson did this stretch produce (mistake, surprise, repeated
  friction, plan-changing probe)? (2) what worked unusually well and should become standard?
- **Luck lens on the SETUP (skill `luck`, owner mandate 2026-08-27):** apply the seven-facet
  diagnostic to the workflow change itself — does it circulate (lessons/telemetry flow back to
  where the next task reads them) and integrate (connect siloed parts), or pool as a one-off?
  Meta-workflow only — never in verdicts or delegate briefs.
- **Bake answers into the protocol IN THE SAME INCREMENT** — general rules into the matching
  skill/CLAUDE.md section; project-specific operational facts in the matching runbook/handoff. A
  lesson recorded only in a handoff WILL be re-learned the expensive way (the mutation-restore
  mistake was made twice for exactly this).
- **Prefer the GENERAL form** (project example in parentheses as evidence). Only-makes-sense-here
  → runbook, not protocol.
- **Keep the protocol tight:** fold into an existing rule where one fits; a bloated protocol stops
  being read. No lesson → say so; never invent one.

## Context/risk management (meta-rules)

- **A retention/GC sweep over a SHARED root needs a STRUCTURAL membership test for what it may
  delete — "every child of the root" breaks the moment any component co-locates persistent state
  there** (the janitor rmtree'd the OSINT packet sink + LLM transcripts on the PC; fix = only
  committed run-id NAME formats are delete-eligible, future persistent dirs protected by default).
  Corollary: dir-mtime is NOT a liveness signal for a dir whose files are appended IN PLACE —
  POSIX dir mtime advances only on entry create/delete/rename.
- **A periodic in-loop diagnostic whose cost scales with a size knob is a latent wedge — bound it
  by construction (fixed subset/top-K + a per-invocation budget that degrades LOUDLY), never by
  hoping the knob stays small** (the in-run PBO monitor re-simmed the whole pop: 70–122 min per
  invocation at pop 560 vs 15 s fitness gens; three runs stacked wedged at monitor boundaries).
  Corollary: **the canonical deploy env lives in the TRACKED runbook; an untracked wrapper is a
  copy that sheds flags silently** (TRADING_GPU_SIM vanished at a wrapper rewrite — weeks of
  "GPU" runs were CPU-only with no signal).
- **A default calibrated for TESTS (zero-sleep polls, tiny budgets, stub-sized caps) that reaches
  a production binding unchanged is a latent outage** — calibrate externally-facing defaults
  against a LIVE measurement and expose them as env knobs at the deployment seam (the L2
  adapter's 50-poll x 0s-sleep default busy-polled ~26s and timed out every HEALTHY MiroShark
  task, which completed ~5s later; fix = 150 x 2s measured against the real task duration).
- **A wait/poll on an external condition must trigger on FAILURE states too, never only success.**
  Success-only silence is ambiguous between "working" and "dead" (a dead dev-server looked like a
  slow compile for 14 minutes). Every wait's exit condition includes failure signatures; a long
  wait → read the LOG, not the monitor.
- **A resource cap sized for a bounded JOB (wall-clock, iterations, token/$ budget) must be measured
  PER-CYCLE when enforced inside a PERPETUAL loop — never cumulative-since-loop-start.** A cumulative
  measure against a bounded cap goes into PERMANENT overrun after the first cap-crossing; if the
  overrun pages/alerts, it then floods every cycle forever (a dead-signal in reverse — the alert is
  always on, so it means nothing). Reset the measurement window each iteration and measure THIS
  cycle's cost (ST8: the steering BudgetGuard measured cumulative wall-clock + cycle-count against
  the 4h/500 Backtest-Runner per-job caps, so a 24h flywheel paged the owner every cycle past hour 4
  — caught by the adversarial verify, whose builder's own budget tests only ever covered an early
  cycle).
- **A "did anything change?" guard computed by SET comparison is blind to ORDER — before treating a
  reordered-same-set input as a no-op, check whether order is load-bearing downstream.** If a
  POSITIONAL consumer exists (array columns, ref-dir association, positional `F[0]` reads), a
  reordered-but-same-set input is a REAL change a set-diff misses: canonicalize the identity case to a
  fixed order (making the no-op truly bitwise) or emit the change event — never return the reordered
  input silently, no event (ST8: an identity objective_selection in a different order was returned
  verbatim with no telemetry, permuting the F-vector columns that flow positionally into NSGA-III;
  the docstring even claimed "bitwise-identical").
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
- **An expensive measurement's RAW output is written to a file BEFORE any filter touches it — a
  grep is a VIEW, never the record.** A 30-minute production-shape sweep was destroyed by my own
  `grep -vE "^  "`, because right-aligned numeric columns begin with spaces, so every data row was
  silently dropped while the header survived and the run looked like it had produced nothing.
  `tee` the raw log first, filter the copy.
- **A `kill` in the command DEFEATS the downstream `flock` guard — a concurrency guard is not an
  idempotence guard.** The standing rule (bridge runbook, bit 5x on 2026-07-21) is that any
  bridge-launched process carries its own on-PC guard; `flock -n` satisfies it for *concurrent*
  re-delivery. But a retrying transport re-runs the WHOLE command, and `kill + relaunch` re-run
  SEQUENTIALLY passes the flock every time — the kill removes the very holder the lock relied on.
  So a destroy-and-recreate command needs a guard on the STATE IT INTENDS TO CREATE, not on
  mutual exclusion: "already running the target SHA? -> exit 0" (2026-07-25: three kill+relaunch
  cycles in five minutes off ONE tool call, two GA cycles destroyed, and the PID churn read exactly
  like a crashloop until my own launch logs were counted). Corollary: **PID churn is ambiguous
  evidence — count your own launch attempts before diagnosing a crashloop.**
- **A long-running probe is NOT dead because its output stopped growing — liveness is `ps`, never
  output volume.** Buffered pipes, slow fixture builds and per-iteration prints all make a live job
  look hung; I declared the same sweep dead and restarted it while it was still running, and the
  original eventually produced the decisive table. Check the process before concluding anything
  from an empty log — and never restart a heavy job on the strength of a quiet file.
- **Never take a TIMING measurement on a contended box.** Serialize benchmark work against known
  heavy jobs (a delegate's full pytest, another probe) — three-way contention here both corrupted
  timings and OOM-killed a probe. If a heavy job is live, either wait or state the contention
  alongside the number; a precise-looking figure measured under load is contention, not signal.

## Phase 5 addendum — thermo-nuclear full-stack pass (owner mandate 2026-08-26)

Before pushing ANY stack containing more than one code commit, a
`thermo-nuclear-review` pass runs over `origin/<branch>..HEAD` as ONE diff, on the
verify lane, in addition to (parallel with) the finding-driven adversarial verify.
Rationale: finding-driven verifies grade each increment against its own contract and
are structurally too focused to see cross-commit interactions, breaking changes to
consumers outside the diff, devex regressions, and feature-gate leaks — the thermo
skill's lens set exists for exactly that altitude. The push waits on BOTH verdicts.
This is the same standing integration bug-echo has (every real fix gets swept for
siblings); thermo is the stack-level twin, not an on-request extra.
