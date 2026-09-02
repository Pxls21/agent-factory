# Research Prompt Authoring Guide (extracted from CLAUDE.md)

Full guide for authoring `docs/research/prompts/RESEARCH-PROMPT-N.md` briefs.
CLAUDE.md carries a compressed summary of the feature workflow; read this file
before authoring any research prompt.

---

## The feature workflow (research → interview → seed → build)

For any substantial new subsystem, drive entropy out **before** writing code, in this order.
This is the proven pipeline (used for the practice-gate subsystem and the Tier-2 reuse loop):

1. **Audit first.** Before planning an integration, *read the actual code* (dispatch parallel
   agents for breadth) and write a grounded findings/plan doc. Never plan on assumptions.
1.5. **Council debate (frame the QUESTIONS before the research prompt).** `/council` — the Council of
   High Intelligence (vendored at `sandbox-kit/council-of-high-intelligence/`, auto-installed by
   `scripts/setup.sh`, 18 persona agents, structured-disagreement protocol: blind Round 1 → anonymized
   cross-examination → final positions → Chairman verdict that LEADS with what's unresolved). Run it
   BEFORE authoring the research prompt, on two things: (a) *what is even worth optimizing/building* (risk
   vs reward per target), and (b) *how to frame the research questions* so the brief doesn't execute a
   badly-posed question (the Granite-swap failure mode). The verdict's unresolved-questions list + dissents
   become the raw material the research prompt must SETTLE. In this sandbox the council runs Claude-only
   (one backbone — still useful for orthogonal perspectives); for true multi-provider diversity run it on
   the PC (`--no-auto-route` off, with Gemini/Ollama/NIM CLIs present). Skippable for small/obvious work;
   mandatory before any change that could trade away security/accuracy/robustness for speed.
   **NEVER use `--quick`.** Quick mode is a 2-round poll with NO cross-examination — it skips the one part
   that makes the council worth running (blind Round 1 → *anonymized cross-examination* → final positions →
   Chairman verdict). Every council MUST run the full multi-round debate. To bound cost, shrink the PANEL
   (a focused `--members`/`--triad`), never the protocol. If cost/time truly forbids a full debate, do NOT
   substitute `--quick` — either run a focused full-protocol panel or skip the council and say so explicitly.
   **Luck lens (skill `luck`, owner mandate 2026-08-27):** alongside the council framing, run the
   seven-facet diagnostic over the PROPOSED artifact/workflow change itself (solvency: can we
   maintain it? circulation: do its outputs flow back into the system? path sensitivity: is this
   the right point in the build sequence?). Feed binding-constraint findings into the questions the
   research prompt must settle. Meta-workflow lens only — never a factor in measurement verdicts.
2. **Research prompt** — `docs/research/prompts/RESEARCH-PROMPT-N.md`, the "first filter." A deep-research brief.
   **The one rule that makes it work: SETTLE the strategic direction so the agent just executes;
   leave open ONLY the technical resolution under it.** A good brief (see #13–#15) the agent runs
   end-to-end without coming back to ask; a bad one (#16/#17, and #18 before rework) leaves a
   *research-direction* fork open, so the agent stops to ask "which do you want?". Concretely:
   - **Separate the research DIRECTION from the research QUESTION.** Direction = scope/strategy/
     deliverable-shape/which-paradigm (e.g. "adopt vs build", "metric = cost vs success-lift"). **You
     decide direction and mark it SETTLED — never ask the agent to pick it.** The QUESTION is only
     what *primary-source research* can answer (exact formulation, verify which option qualifies,
     what controls are sufficient). If a question reads "decide approach A or B at the strategy
     level", you've leaked a direction into the question — pull it up into SETTLED.
   - **Lead with the real question, not the substrate.** Name the thing only research resolves; demote
     means/substrate (e.g. *which* benchmark) to a downstream verification sub-task.
   - **ONE primary deliverable. Never double-label "the crux".** (The #19 mistake: Q1 marked "highest" AND
     Q3 marked "THE crux" AND the deliverable called the controls "the heart" — three things crowned, so the
     agent stopped to ask "is it (a) or (b)?". Two co-equal cruxes IS a direction fork.) Pick the SINGLE
     primary deliverable; mark every other open question explicitly **subordinate** with its relationship
     stated (validity-GATE-on-the-primary / substrate / downstream), never as a competing primary. If two
     things feel co-equal, name which is the *measurement* (primary) and which is the *gate that makes the
     measurement mean anything* (subordinate) — mirroring #18 (metric = primary; validity controls = gate).
     Add a one-line **PRIORITY (SETTLED — do not ask which is primary)** so the fork is pre-closed in text.
   - **Detect a BUNDLED brief and FORK it before authoring — two problems crammed into one deliverable is
     a hidden co-equal-crux.** When a scoping pass (or a council) finds the ask conflates two orthogonal
     questions (e.g. P1 correctness-oracle vs P2 recall-at-scale), split them into SEPARATE research prompts
     and state the non-substitutability in one line ("better recall does NOTHING for correctness — a perfect
     fingerprint serves a broken artifact faster"), so neither brief inherits the other's fork.
   - **Each open question carries its settled direction** ("north star settled by PF1; OPEN = the exact
     formulation"), **its inline resolution-KIND token** (`[DESIGN fork — DECIDE]` / `[PRIMARY-SOURCE
     TECHNICAL — resolve to a verdict]` / `[EMPIRICAL GATE — run FIRST]`), and **maps to a concrete
     metric/control/module change.**
   - **PRE-CLOSE every DESIGN fork; leave OPEN only the irreducibly-EMPIRICAL gate.** (The RP-33 failure: the
     brief left three *design* sub-mechanism forks in the OPEN buckets — "the witness-adequacy criterion",
     "soundness with side effects", "how to keep eviction from becoming an attack surface" — so the returned
     report LED with a "What remains genuinely uncertain" list of four, even though its own body then resolved
     three of them. A settle-able fork parked in OPEN *licenses* the agent to hand it back as an "uncertainty"
     instead of closing it.) Before shipping, TRIAGE every OPEN item into exactly one of three kinds and route it:
     - **(a) DESIGN fork you can decide** (which mechanism, which guard, which fallback, the abstain rule, the
       ordering) → **MOVE it into SETTLED with the decision made** (name the rejected alt). It is NOT open.
     - **(b) primary-source TECHNICAL question** (exact formalism, which citation qualifies, the derivation) →
       stays OPEN, but the brief DEMANDS the agent RESOLVE it to a verdict from primary sources (no bare hedge).
     - **(c) irreducibly-EMPIRICAL gate** (only running against *our* data/corpus answers it — e.g. RP-33's
       extractable-fraction) → stays OPEN as a **runnable gate**: exact corpus + metric + operating-point +
       attached decision rule (HIGH→X / LOW→Y). This is the ONLY kind that may end the report unresolved.
     Pre-flight test: for each OPEN item ask "could a competent author DECIDE this without new data?" If yes it
     is (a) — pull it into SETTLED. The tell you got it wrong: the returned report has a "what's still
     uncertain" section listing more than the empirical gates. One empirical gate open is fine; three
     design forks masquerading as uncertainties is the defect.
   - **`what-the-system-IS` is MANDATORY and must be a CONCRETE, EXHAUSTIVE INVENTORY of what is ALREADY BUILT
     — name the module:function and what each does — so the agent never reinvents or contradicts existing
     infrastructure.** (The RP-35 miss: the brief said "Rundeck = FORMAT + OFFLINE oracle" but never stated
     **we already have our OWN execution engine** — `skill2workflow/execute.py:run_workflow` runs the Workflow
     natively, wrapped by `reverify.py`, exit-code only — so the research went off studying how to run
     Rundeck's JVM engine, a runtime we never use. Same root cause as the "skill" vs "Rundeck workflow" wording
     drift: the agent decided from a mis-stated current state.) Rules, every brief:
     - **List every built component the question touches, one line each: "we already have X (`module:fn`) — it
       does Y."** Cover the runtime, the store, the gate, the export/format, the oracle(s), the capture path —
       whatever the question could otherwise assume is missing.
     - **Where a candidate direction would DUPLICATE or REPLACE a built component, say so in-line: "do NOT
       propose building/adopting Z — we already have X."** The agent cannot know our infra unless the brief
       states it; unstated = assumed-absent = wasted research.
     - **Name the artifact and substrate PRECISELY** (it is a *Rundeck JOB-YAML workflow* run by *our*
       `execute.run_workflow`, not a "skill", not "Rundeck's engine"). Loose nouns cause wrong research paths.
     - **If you are unsure whether something is built, AUDIT the code before shipping the brief** (grep the
       seams, read the module) — never ship a current-state section you didn't verify. The #1 research failure
       mode is the agent not knowing what we already built; the current-state inventory is the fix.
   - **ONE self-contained file. The deliverable IS `docs/research/prompts/RESEARCH-PROMPT-N.md` and NOTHING else** — the
     human pastes exactly that one file into the research tool. **NEVER split it into a separate
     `RESEARCH-FINDINGS-N.md` preliminary doc and NEVER make the prompt say "see/START in <other file>"**
     (that broke #17–#20: whichever file got pasted, the tool reported "the matching one isn't pasted").
     Put the preliminary findings INLINE as a self-contained section the brief says to **VERIFY + DEEPEN +
     CHALLENGE, not re-derive**; flag unverifiable/hallucinated citations to recheck. The ONLY separate
     findings doc is the RETURNED report from the research run (e.g.
     `docs/research/findings/RESEARCH-FINDINGS-N-VERIFIED.md`), which the human brings back — you never
     pre-author it.
   - **House structure (all in the ONE self-contained `RESEARCH-PROMPT-N.md`):** question-first · intended
     design · what-the-system-IS (audited) · **SETTLED** (direction/constraints) · preliminary findings
     (INLINE) · **ranked open questions** (each: settled direction + maps-to-change) · "what would change
     the plan" · deliverable. **ADOPT, don't invent;
     prefer deterministic/exit-code; flag any LLM-judge.** End with **"Decide; do not ask."**

---

## Two Research-Prompt Modes

**SETTLED-SPEC (guarded) vs EXPLORATORY-HYPOTHESIS.** Same house
structure, same invariants above — what changes is the *stance toward the preliminary findings*.

### SETTLED-SPEC (guarded; low-variance, execution-leaning)

e.g. RP-26/27/28. The strategic answer is already decided and often already proven in-repo; the brief
locks the mechanism into SETTLED (RP-26: "Rundeck = the FORMAT + an OFFLINE engine oracle"; RP-27:
"Execute-and-replace. Locked"; RP-28: the whole "layer on top, never in the spine" doctrine) and names
the exact build seam (RP-28 even cites `risk_score()` in `decide.py`). The agent's job is to **VERIFY +
DEEPEN + CHALLENGE, do not re-derive** and formalize a near-decided direction with tight guardrails.
SETTLED holds the *answer*; only the technical formalization under it is OPEN. "What would change the
plan" lists bounded fallbacks within the frame.

### EXPLORATORY-HYPOTHESIS (discovery-leaning, higher-variance)

e.g. RP-29. The solution space is genuinely open / novel-hard / the thesis itself is in doubt (RP-29
followed a `decision=PIVOT` and a never-run live join). The council's directions are framed as **"strong
candidate hypotheses, NOT settled answers"** — VERIFY · DEEPEN · actively **CHALLENGE**, and *"finding a
better approach we haven't considered is a first-class outcome, more valuable than confirming our guess."*
SETTLED holds only **constraints/guardrails** (the spine, determinism, security-never-worse, substrate),
never the solution; "what would change the plan" admits paradigm-level reframes/pivots; the report
RESOLVES every open question to a decision-grade verdict (residual uncertainty surfaces ONLY bundled with
a default-to-proceed + residual-risk + how-to-settle — never a bare hedge).

**Exploratory must stay QUESTION-PROOF — "open" means "open within stated bounds + an attached
decision rule", NEVER "come ask me".** (RP-29 paused with 3 clarifying questions; that is a BRIEF
DEFECT, not agent behaviour — §9 invited challenges without saying how to resolve the forks
autonomously.) Before shipping an exploratory brief, pre-resolve every fork the agent could hit:
- **Thesis-stance dial:** state explicitly whether the core thesis is *genuinely on trial* (then
  say "develop BOTH a best-fair-chance re-test AND a real pivot/what-to-build-instead branch") or a
  fixed commitment. Never leave "recommend the pivot if it fails" without saying whether to actually
  design the pivot.
- **Each architecture fork:** when the solution space has candidates (A vs B vs C), write "evaluate
  all, **RECOMMEND** by criteria X — do NOT ask which we want," and state any lean. Bounded-open with
  the decision rule attached, never a bare menu.
- **Paradigm/substrate dial:** state whether the substrate itself (e.g. the trace→DAG-workflow
  paradigm) is in-scope to challenge or fixed; if in-scope, BOUND it ("one dedicated section;
  recommend keep-or-switch with evidence; don't rewrite the report around it").
- **Self-resolution on EVERY open question + every "what would change the plan" trigger:** each
  carries HOW to resolve it without us, so **"Decide; do not ask" governs META-choices too**, not
  just the technical resolution.
- **Pre-flight (author's check):** simulate the agent's clarifying questions; if any survive, fold
  the answer into SETTLED / the decision rule. A shipped exploratory brief the agent could rationally
  pause on is INCOMPLETE. (Mantra: exploratory settles the *guardrails + decision rules*, not the
  answers.)

**Exploratory must END ON ANSWERS, not uncertainties — the deliverable RESOLVES open questions, it
does NOT hand back a "what's still uncertain" list.** (RP-29 led with "What Is Still Genuinely
Uncertain" and punted the real questions — is-the-PIVOT-a-filter-artifact, unstructured-secret
completeness, Hermes `execute_code` capture-visibility, skill formalism — into a "Part 2." That is a
deliverable FAILURE: the entire point of the research engine is to RETURN answers, not catalogue
doubts.) The brief MUST demand, and you MUST refuse to accept a report that violates:
- **Every open question → a decision-grade verdict:** a yes/no WITH primary-source evidence. Not
  "maybe", "it depends", "unproven", or "leans toward."
- **When docs/literature are silent, RESOLVE FROM PRIMARY SOURCE — go to the code.** "The docs don't
  say" is not an answer: read the actual implementation (e.g. the Hermes `execute_code` RPC listener +
  state-DB persistence path; the `pre_tool_call` hook-dispatch return-value handling), reverse-engineer
  the format (e.g. the `github_pat_` checksum), run the check. Instruct the agent to do this.
- **Genuinely-empirical unknowns become RUNNABLE GATES, never hedges:** a question only an experiment
  can settle (e.g. is-the-PIVOT-a-filter-artifact, the break-even precision threshold) comes back as a
  concrete decision rule — exact dataset/metric/operating-point/threshold + the experiment that
  settles it — so it is a gate to RUN, not a "we don't know."
- **Truly UNCONFIRMED-after-exhausting-sources ships ONLY as a triple:** (a) the default to proceed
  on, (b) the residual risk/consequence, (c) the first build/experiment task that settles it. A bare
  "still uncertain" is forbidden.
- **Pre-flight (output side):** the brief enumerates the questions the research MUST answer and states
  that a returned report leaving ANY of them a bare uncertainty is INCOMPLETE — it is re-run/continued,
  not accepted, and never spawns a "Part 2" to do the job the first run was supposed to do. (Mantra:
  the research engine exists to CONVERT uncertainty into decisions — a report that returns uncertainty
  did not do its job.)

### Mode selection

**The tell (which a problem needs):** is the *answer* already known and proven, or only the
*constraints*? Known answer + located seam → SETTLED-SPEC. Open answer / thesis in doubt / want a
better idea than ours → EXPLORATORY-HYPOTHESIS. Equivalently: guarded *confirms*, exploratory *hunts*.

**Use SETTLED-SPEC** for a narrow, already-validated seam (one harness, one signal, one trigger
point) where you want low-variance buildable detail fast. **Use EXPLORATORY-HYPOTHESIS** for a
whole-foundation blueprint, a novel/unproven thesis, or after a gate said STOP — anytime the best
move is to let the literature beat our guess.

**Both modes obey ALL the invariants above** — ONE self-contained `RESEARCH-PROMPT-N.md`, inline
findings to VERIFY/DEEPEN/CHALLENGE, ONE primary deliverable with `PRIORITY (SETTLED — do not ask
which is primary)`, each open question carrying its settled direction + maps-to-change, SETTLE the
direction (only the *technical resolution* is ever open — even in exploratory mode the *guardrails*
are settled, not the strategy fork), ADOPT-don't-invent, prefer deterministic/exit-code, flag every
LLM-judge, and end with **"Decide; do not ask."** The mode is a stance dial on the fixed template.

**REFERENT REALITY CHECK (AP-53, baked 2026-09-01): every component the SETTLED section names as
load-bearing must pass the two-instrument reachability check BEFORE it enters the prompt** — a
dormant referent laundered into SETTLED survives the researcher, the council, and the addendum,
because every layer audits the argument, not the referent's existence (live instance: "the HMM
bear regime label" traveled through all four layers; HMMRegimeProvider had zero production
callers and no bear label exists). "Exists in the tree" ≠ "wired"; cite the wiring evidence
inline next to the name.

### Core system invariants (NON-NEGOTIABLE in EITHER mode)

**CORE SYSTEM INVARIANTS ARE SETTLED GUARDRAILS — NEVER expose them as open / pressure-test / paradigm
questions, in EITHER mode.** (The RP-29 AWM failure: the brief put a core invariant — "DAG-replay vs
workflow-as-context" — in the exploratory/pressure-test bucket, so the agent "got lazy" and recommended
AWM, the exact opposite of the premise. A settled invariant leaked into an open question is the #19-style
leak, and it is the single most expensive prompt-authoring mistake.) The load-bearing invariants —
**replay-blocks-the-model (substitute the recomputed RESULT, never call the model twice; AWM/workflow-
as-context is REJECTED, never a fallback)**, the **no-LLM-judge exit-code spine**, the **false-negative-
first gate (stored ≡ working-by-construction; failures park→heal→graft→spawn children)**, **no
newest-wins eviction**, and **secrets never in any sink** — go in SETTLED verbatim as NON-NEGOTIABLES,
with the rejected alternative NAMED as rejected. Even exploratory briefs may challenge *mechanism/
formalism under* an invariant, never the invariant itself. Pre-flight check: if an open question, when
answered "the lazy way," could delete one of these invariants, you have leaked a guardrail — pull it
up into SETTLED and name the wrong answer as rejected.

---

## Workflow Steps 3–7

3. **Findings** — the returned report becomes the constraint set (read it fully before step 4).
4. **Ouroboros interview** — `mcp__ouroboros__ouroboros_interview`, seeded with the findings.
   Answer each Socratic question with a **research-grounded, decisive** choice; drive
   `ambiguity_score` toward ~0 (we land ~0.05–0.06). Keep `last_question` free of shell
   metacharacters (`;` etc. are rejected).
5. **Seed** — `ouroboros_generate_seed` → persist to `seeds/seed-<name>-vN.yaml` and commit.
   This is the immutable spec (goal, constraints, acceptance criteria, ontology).
6. **Task breakdown (do this BEFORE writing any code).** Decompose the seed into the **complete**
   set of build tasks up front — one per acceptance criterion / increment, in dependency order, each
   with its deterministic verify — and record them (a committed `tasks/` checklist or the harness
   todo list) so **nothing is lost as the build drifts**. The seed says *what*; this says *every step
   to get there*. Update it as tasks complete; never discover a missed acceptance criterion at the end.
7. **Hand-build** — implement against the seed + task list: surgical, test-driven, one commit per increment.
   **Every acceptance test must be deterministic and LLM-free** (commit the artifact; the test
   reads it). Do **NOT** run `ooo execute`/`run_seed` unless explicitly asked — hand-build from
   the seed as the spec.

Cross-cutting invariants this workflow protects: the **no-LLM-judge spine** (LLM only at
codify/generate time; all gate execution is exit-code), the **negative-control discipline** for
any auto-generated check (must pass a compliant fixture AND fail a violating one), and running
**heavy/long jobs ON the PC** (sandbox is ephemeral — see `sandbox-kit/PC-BRIDGE.md`).
