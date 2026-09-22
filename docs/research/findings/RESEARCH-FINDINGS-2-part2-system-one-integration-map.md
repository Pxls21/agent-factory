# Strategic Integration Map: Routing "System One" Tasks to a Local Typed-Decision Model (Laya) Across an Autonomous Agent-Factory Workflow

## TL;DR
- **Laya can earn its keep in ~20 distinct integration points across the factory, but only as an advisory ranker/classifier/scorer/router that feeds a human or the coordinator — never as a term in any gate/merge/proof predicate.** The highest-impact wins are pre-lane verify-outcome prediction, breadth/tier routing (replacing/pre-filtering the Haiku hive tier), finding severity/kind and hit-role tagging, and relevance ranking that shrinks what the coordinator and local LLM must read.
- **The optimal strategy is a uniform "one reviewed-decisions file per skill + single `decide ask` CLI" invocation surface, rolled out shadow → calibrate (per-question-type temperature) → A/B, with the decision ledger doubling as the labeled-data flywheel.** Because Laya costs ~1 s/question on this CPU and does not amortize over batches, treat it as an offline/async sieve by default and cap synchronous inline use to a few questions.
- **Reject anything needing generation, multi-step reasoning, >512-token state, non-English, tool use, or a hard gate decision.** Those stay with regex (cheaper/safer), the coordinator (reasoning), or a future fine-tuned typed-decisions checkpoint (the ceiling case).

## Key Findings

1. **Laya is a specialist, not a zero-shot engine.** The base English checkpoint scores ~0.35 on the typed-decisions benchmark (barely above the 0.318 random baseline) [Convaiinnovations](https://laya.convaiinnovations.com/) and ships badly miscalibrated (raw ECE ~0.466); [AI Weekly](https://aiweekly.co/alerts/convai-ships-laya-a-non-autoregressive-multilingual-system-1-decision-model-at) it only reaches useful accuracy (0.766 on the fine-tuned typed-decisions checkpoint) and good calibration (ECE ~0.081) *after* [AI Weekly](https://aiweekly.co/alerts/convai-ships-laya-a-non-autoregressive-multilingual-system-1-decision-model-at) per-question-type temperature fitting on the project's own labels. This makes **calibration on the ledger a hard prerequisite** for every integration point, not an optional nicety.

2. **TypeSafe's own published guidance maps almost one-to-one onto this factory.** TypeSafe recommends System One for classification, detection, scoring, routing, search, retrieval, ranking, verification, feature extraction, and structured-extraction-validation — and explicitly for "harness engineering" ("model routing, semantic context retrieval, LLM error detection and guardrails, reasoning trace classification at lightspeed and a fraction of the cost") and "universal verification" ("Verify the input prompt, extractions, reasoning traces, tool calls, or inputs of any other AI"). It also names "semantic code linting" — verbatim: "Use Jev queries to add automated semantic lints to code and writing… Run these checks in CI and flag violations for review." Crucially, TypeSafe's "How to build with System One" guidance is emphatic that **code keeps control flow and deterministic rules; the model only supplies "programmable common sense," and its answers drive "smart if-statements," never replace them** — verbatim: "Keep control flow, deterministic rules, and side effects in code… Outputs are sortable and can drive smart `if` statements, thresholds, and comparisons." This is exactly the advisory-only constraint here.

3. **Production practice converges on the same pattern the factory needs.** Semantic/classifier routers (RouteLLM, FrugalGPT, vLLM Semantic Router), cross-encoder rerankers (ms-marco-MiniLM class), guardrail classifiers (Llama Guard, Prompt Guard/mDeBERTa), and confidence-gated cascades all sit a cheap model *in front of* an expensive one and escalate on low confidence. The binding constraint, per the cascade-routing theory literature (Dekoninck, Baader & Vechev, "A Unified Approach to Routing and Cascading for LLMs," ICML 2025), is **the quality estimator's own calibration** — verbatim: "we identify good quality estimators as the critical factor for the success of model selection paradigms" — which again points back to calibrating Laya before trusting its thresholds.

4. **The ~1 s CPU-floor latency is the dominant design constraint.** Because N questions cost N encoder passes and batching does not amortize on this Ryzen 5 5600X, Laya's natural home is the **asynchronous/offline sieve and the "map-reduce over big data" pass** (TypeSafe's own framing: "100x cheaper means you can process giant datasets… classify giant agent traces"), plus a tightly bounded (a few-question) synchronous use only where it demonstrably saves a coordinator round-trip or a 4-7 h lane.

## Details

### 1. The Litmus Test — "Is this a System One task?"

**Route to Laya only if ALL of these hold:**
- **Bounded output.** The answer is a yes/no (noul), one of ≤~20 labeled options (choice), or a bounded ordinal/score — decided at request time, no free text.
- **Compact state.** The evidence needed fits in ≤~320 usable tokens (English, after the 192-token head) or ≤~1024 (multilingual/typed-decisions checkpoints), or can be chunked into such units without losing the signal. (Right-truncation is silent, so over-long state = wrong answer at high confidence.)
- **English (Latin script).** The base checkpoint collapses on non-Latin scripts while staying overconfident (the model card reports Khmer at 0.000 accuracy and 0.952 confidence), so confidence-gating cannot rescue it.
- **Single-pass judgment.** No multi-step reasoning, no chained tool calls, no "figure out X then decide Y."
- **Advisory consumer.** The output is read by a human or the coordinator, or used to rank/filter/deprioritize a list where every dropped item stays recoverable from the original bytes. It is **never** a term in a gate/merge/lint/commit/push/proof-class predicate.
- **Labelable.** You can produce (or already have, in the ledger) a few hundred to a few thousand labeled examples of this exact decision to calibrate and validate.
- **Worth it.** It replaces a coordinator token-spend, a Haiku call, or a slow manual triage — and the ~1 s/question cost is amortized off the critical path or clearly beats the alternative.

**Disqualifiers (keep it away from Laya if ANY hold):**
- Needs to **generate** anything (text, code, a patch, a summary, an explanation).
- Needs **multi-step reasoning** or planning.
- Needs **long context** (a full lane transcript, a whole file, a multi-thousand-token report) that cannot be compacted. The 512-token English window is "roughly one email, not a support thread."
- Is **non-English** or heavily symbolic/non-Latin.
- Needs **tool use, filesystem, or state mutation.**
- Is **cheaper, safer, and exact as a regex or deterministic rule** (identity checks, digests, counts, schema validation, sha256).
- Would land as a **term in a gate/predicate** — i.e., anything on the model-free gate spine.
- Has a **large label space** (>~20 options) that cannot be split into a coarse-to-fine hierarchy or shortlisted first (Banking77's 77 labels: Laya 0.425 vs Jev 0.870, because options share a fixed 192-token head budget → ~3-4 tokens/label).
- Cannot be **labeled** for calibration.

### 2. Candidate Integration Points, by Task Category

Throughout: **noul** = P(true); **choice** = one of N labeled options + distribution; **score** = bounded ordinal. Venue = sandbox (coordinator side) or PC (local builder). Default placement = **async/offline** unless a synchronous saving is explicit.

#### (a) Relevance Filtering & Ranking
*(Note: the tool-output SIEVE, injected-context ranking, and code-intel quartet ranking are already covered by a separate spec; the points below are the "everything else" in this category.)*

- **A1. Near-duplicate finding/task/memory dedup.** For a candidate finding/task/memory vs. an existing one:
  - `noul`: "Do these two findings describe the same underlying issue?" or `score`: "How redundant is candidate B given A? (0 distinct … 3 identical)."
  - State: the two short records (title + one-line body), ≤~200 tokens. Venue: either. Async (backlog-grooming pass). Replaces: nothing / manual. Consumer: task DB / memory writer (collapses duplicates, keeps both bytes). Risk: false-merge — mitigate by keeping both originals and only *flagging* the merge.
- **A2. Backlog / build-tasklist relevance-to-goal ranking.** Per task vs. current epic:
  - `score`: "How relevant is this task to the stated current objective? (0 unrelated … 3 directly on-path)."
  - State: task line + one-line objective. Async. Consumer: coordinator's queue view.
- **A3. Pre-read ranking of search hits before an expensive `read_file`.** Given a query and a one-line hit preview:
  - `score`: "How likely does this hit contain what the query is looking for?" Rank, read top-k first. Async or bounded-sync on PC. Replaces: reading in arbitrary order. Consumer: the builder agent. (This is the cross-encoder rerank pattern; keep it advisory — never drop unread hits, only reorder.)

#### (b) Classification & Tagging
- **B1. Finding severity + kind (hive-reviewer).** Today Claude Haiku. Per finding:
  - `choice` severity {H, M, L}; `choice` kind {slug set, ≤~20}. State: finding text + minimal code context, ≤~300 tokens. Venue: either; async batch over a review's findings. **Direct Haiku replacement** once calibrated agreement is high. Consumer: the reviewer's output table. Risk: severity miscalibration → keep H/M/L advisory, coordinator still reads.
- **B2. Hit role (hive-scout).** Today Haiku. Per code hit:
  - `choice` {def, caller, config, test, other}. State: the hit line + a few lines of surrounding context. Async batch. **Direct Haiku replacement.** Consumer: scout output. This is a near-ideal Laya task (small fixed label set, compact state, high labelability).
- **B3. Error-type of a failed command.** Given the tail (last ≤255 lines, tagged) of a failed Bash/test run:
  - `choice` {real-failure, flaky-test, infra/runner-gone, concurrency/timeout, quota/empty, config}. State: compacted log tail. Async on PC. Replaces: manual/coordinator triage. Consumer: coordinator or a repair packet. (Mirrors the documented CI-triage-from-log-tail pattern: a Choice over failure class plus a Choice over which line is the cause.) Risk: log tail truncation — chunk and ask per-chunk if needed.
- **B4. Change-type of a patch/diff.** Given a compact diff summary (files + hunk headers):
  - `choice` {feature, bugfix, refactor, test-only, docs, config, revert}. Async. Consumer: task DB / retro. Keep advisory (labels the commit note, not a gate).
- **B5. File/test/config typing.** `choice` over role of a path/blob when metadata is ambiguous. Cheap; **but check first whether a regex on the path already does this deterministically** — if so, disqualified (use the regex).
- **B6. "Is this Grep a semantic search?" (graft nag).** Today a regex. `noul`: "Would this text-search be better served by a semantic identifier search?" State: the grep pattern + intent line. Sync (tiny). **Augments** the regex: keep the regex as the cheap floor, use Laya only on the cases the regex is unsure about (and only as a nag, never blocking).

#### (c) Triage & Routing (Laya-as-router in front of the tiers)
- **C1. Model-tier routing (the flagship pattern).** Before dispatching a subtask, put Laya in front of {Haiku hive tier, local Qwen LLM, coordinator}:
  - `score` complexity: "How much reasoning does this subtask need? (0 trivial/lookup … 3 deep multi-step)"; `noul`: "Does this need code generation or multi-step reasoning?" High-confidence "trivial" → Haiku/local; low confidence or "deep" → coordinator. State: the subtask description, ≤~250 tokens. Sync (worth it — one 1 s call saves a coordinator round-trip). This is the RouteLLM/FrugalGPT classifier-routing pattern; **confidence-gate the escalation.**
- **C2. Breadth routing on candidate count (bug-echo).** Today the coordinator. `choice`/`score` over the candidate set size + character: "Given N candidates, route to {single-pass, sampled, full-sweep}." State: candidate summary + count. Sync. Replaces coordinator judgment. Consumer: bug-echo.
- **C3. "Is this worth a full 4-7 h lane?"** `score`: "How likely is this task to need a full build/verify lane vs. a quick local fix? (0 quick fix … 3 definitely a lane)." State: task description + rough scope. Async/sync. Consumer: coordinator's dispatch decision. High leverage because a lane is 4-7 h.
- **C4. Escalation from the Haiku/local tier.** When the cheap tier's own confidence is low, Laya (or the tier's calibrated confidence) triggers escalation to the coordinator — the uncertainty-gated cascade. Advisory input to the harness's routing.
- **C5. WORKER/REVIEWER subagent directive.** Today a regex. `choice` {worker, reviewer} when the regex is ambiguous. Augment-the-regex pattern (regex is the floor).

#### (d) Prioritization & Scoring
- **D1. Bug-echo six-dimension ratings.** Today the coordinator rates Urgency, Risk-of-Fixing, Risk-of-Not-Fixing, ROI, Blast-Radius, Fix-Effort, then buckets into {BUG, OK, REVIEW, WATCH}. Ask **six independent `score` questions in one state**, then compose the bucket **in code** (weighted sum + thresholds), not in Laya — exactly TypeSafe's documented "combine question outputs in code" pattern (e.g. `quality = 0.4*answers_request + 0.4*citations_supported + 0.2*(1 - contradicts_context)`):
  - e.g. `score` "Blast radius if this breaks in production? (0 isolated … 3 systemic)". State: the finding + minimal context. Async batch. **Replaces coordinator tokens** on a repetitive rating task — a strong win. Consumer: bug-echo's table; the BUG/OK/REVIEW/WATCH cut stays deterministic code over the scores.
- **D2. Task-queue / backlog prioritization.** `score` urgency/importance per task; sort in code. Async. Consumer: coordinator queue.
- **D3. ROI/risk pre-scoring of proposed work.** `score` expected-value and risk as advisory features fed to the coordinator's planning. Async. (TypeSafe's "ML feature extraction" pattern: probabilities become numeric features for a downstream decision.)

#### (e) Gate-Adjacent Advisory Pre-Screens (predict, never gate)
- **E1. Verify-outcome prediction before spending a lane.** Given a compacted build-lane summary (what changed + RESULT-line-style claims):
  - `noul`: "Is an adversarial VERIFY lane likely to reject this?" / `score`: "How likely is this to pass verify on the first round?" State: compact change+claim summary, chunked if needed. Async, on PC. **Advisory only** — the lane gate stays model-free; this just lets the coordinator decide whether to spend 4-7 h now or fix first. Highest wall-clock leverage in the whole map. Risk: over-truncated state → false confidence; treat as a hint, always run the real lane.
- **E2. Probable premise conflict.** `noul`: "Does this task's stated premise conflict with the recorded project state/premises?" State: premise line + a compact premise digest. Async. Advisory input to the dispatcher premise gate's *human/coordinator reader* — never the gate term itself.
- **E3. Likely-incomplete report pre-screen.** Before a report hits the model-free report lint: `noul` "Does this report section appear empty or truncated?"; `noul` "Do the cited lines plausibly support the claim?" State: the section + cited lines. Async. Consumer: coordinator (fix before lint) — the lint itself stays token-in-cited-lines/min-refs, model-free.

#### (f) Quality & Completeness Signals
- **F1. Tool-output anomaly/error flag.** `noul`: "Does this tool output contain an error or anomaly?" State: compacted output. Async (this is a natural companion to the already-specced sieve). Consumer: the agent's attention.
- **F2. Truncation detector.** `noul`: "Does this block look truncated mid-structure?" Small state. Sync-cheap. Consumer: agent (re-fetch).
- **F3. Claim-support / groundedness pre-check.** `noul` per claim: "Is this claim supported by the cited lines?" (NLI-style entailment). Async batch. Consumer: coordinator/report author. Advisory; the deterministic citation verifier (token-in-cited-lines) remains the actual check.
- **F4. Empty-section detector.** `noul`: "Is this report section effectively empty?" Trivial state. **Check first whether a length/regex rule suffices** — if so, disqualified.

#### (g) Memory & Compaction Support
- **G1. Protect-vs-summarize turn tagging (Hermes compaction).** Before the lossy summarizer runs, per turn/block:
  - `score`: "How important is this block to keep verbatim vs. safe to summarize? (0 safe-to-drop … 3 must-keep-verbatim)" or `noul`: "Does this block contain a file path, error string, or decision that must survive verbatim?" State: the block, chunked to ≤~320 tokens. Async or bounded-sync at the compaction event. Consumer: the compactor (protect list). This directly attacks summarization drift (the loss of `src/…:52` and `ECONNREFUSED`-type detail). Advisory — the compactor still runs; Laya just biases what it keeps.
- **G2. Persist-to-long-term-memory decision.** `noul`: "Is this worth persisting to long-term memory?" Async. Consumer: memory writer.
- **G3. Recall relevance.** `score` relevance of a stored memory to the current task before injecting it. Async. (Overlaps the injected-context ranking already specced — coordinate, don't duplicate.)

#### (h) Others surfaced by research
- **H1. Flaky-test flag.** `noul`: "Given this failure's text and recent history summary, is this a flaky test rather than a real regression?" State: failure + compact history line. Async. **Advisory only** — quarantine stays a policy/gate decision in code (per the flaky-test-tracking literature: keep classifier and gate separate so history is replayable).
- **H2. Route a test failure to a likely owner/area.** `choice` over a small set of code areas/owners. Async. Consumer: routing/notification. Advisory.
- **H3. Reasoning-trace / turn-retro classification.** `choice`/`score` over turn-retro reflection prompts (e.g., "Did this turn make progress? {yes, no, blocked}"). Async. Consumer: retro log. (TypeSafe's "reasoning-trace classification" harness use case.)
- **H4. Lane-state classification sanity flag.** Lane state (READY/RUNNING/FAILED) is derived deterministically from artifacts — **keep it deterministic**; Laya may only *flag* "this lane looks stuck/anomalous" as an advisory nudge, never set the state.
- **H5. Orient / lane_context pack relevance.** `score` each candidate context item for inclusion in the orient/lane_context pack. Async. Overlaps injected-context ranking — coordinate.
- **H6. Offload-map prioritization.** `score` each remaining coordinator-token cost item by "how ripe is this for offload to Laya/Haiku/local?" — a meta use that helps sequence this very rollout.

### 3. The Optimal Leverage Strategy

**Prioritization (impact × feasibility × labelability).** Rank order to build:

*Tier 1 — do first (high impact, high feasibility, already labelable from Haiku/coordinator logs):*
- B2 hit-role, B1 finding severity/kind (direct Haiku replacements; small fixed label sets; the Haiku outputs are ready-made labels).
- D1 bug-echo six scores + C2 breadth routing (replaces repetitive coordinator token-spend).
- C1 model-tier routing (the compounding cost win; the whole point of a cheap front-tier).

*Tier 2 — high value, needs more calibration data or care:*
- E1 verify-outcome prediction (biggest wall-clock lever, but hardest state-compaction and highest failure cost — ship in shadow long).
- A1 dedup, A2/A3 ranking, G1 compaction protection, B3 error-type.

*Tier 3 — nice-to-have / augment-the-regex:*
- B6 semantic-grep nag, C5 WORKER/REVIEWER, F2/F4 truncation/empty (only if not already a cheap regex), H1/H2 flaky/owner routing, H3 retro.

**Venue / sync / async placement pattern.**
- **Default async/offline** (the ~1 s/question, no-batch-amortization floor makes this mandatory for anything off the critical path): B1-B4, D1-D3, A1-A3, E1-E3, F1/F3, G1-G3, H1-H3.
- **Bounded synchronous (≤ a few questions)** only where one Laya call demonstrably saves a coordinator round-trip or a lane: C1, C2, C3, B6, F2.
- **Venue:** run Laya where the data already is — sieve/log/tool-output tasks on the PC (local builder), coordinator-planning tasks (routing, backlog, offload-map) on the sandbox. The GPU is occupied by the local LLM, so Laya runs **CPU FP32** (INT8 regresses ~1.7× on Zen 3 without AVX-VNNI); keep the checkpoint **preloaded** in memory (a cold rebuild costs ~7-10 s on CPU) and avoid Router language-switch reloads by pinning the English checkpoint.

**Uniform invocation surface.**
- **"One reviewed decisions file per skill."** Every skill that calls Laya declares its questions in a single reviewed file: the exact question wording, type, criteria, the state-builder, the per-question-type temperature, the confidence thresholds, and the consumer. Nothing calls the model ad hoc.
- **A single `decide ask` CLI** is the only entry point. Every call goes through it so that (i) every decision is logged to the ledger with its inputs, outputs, distribution, and model/temperature version; (ii) determinism-for-fixed-input makes every decision replayable from the ledger without re-running the model; (iii) calibration and A/B live in one place.

**Rollout: shadow → calibrate → A/B, applied uniformly.**
1. **Shadow.** Run Laya alongside the incumbent (Haiku/coordinator/regex); log both, act on neither. Costs nothing but CPU time; builds the labeled set.
2. **Calibrate.** Fit one temperature per question type on the shadow labels; measure ECE and argmax agreement vs. the incumbent. Do not trust probabilities until calibrated (raw ECE ~0.466 → ~0.081 only after fitting). [Flowtivity](https://flowtivity.ai/blog/laya-open-source-jev-alternative/) [AI Weekly](https://aiweekly.co/alerts/convai-ships-laya-a-non-autoregressive-multilingual-system-1-decision-model-at)
3. **A/B, confidence-gated.** Promote Laya to act only above a per-question calibrated confidence threshold; everything below the floor escalates to the incumbent (the uncertainty-gated cascade). TypeSafe's own docs give illustrative starting bands (note: two of their pages use *different* example numbers — a 0.5 floor with a >0.9 high-stakes gate on the confidence page, versus a 0.6 floor with a >0.85 gate on the confidence-routing pattern page; the self-consistency cookbooks use a top-Choice-probability ≥ 0.60 floor and a Noul "uncertain band" of 0.30-0.70). All are explicitly labeled illustrative, not calibrated guarantees. Start conservative, tune on the cost of wrong actions vs. review.

**The ledger-as-labeled-set flywheel.** The first-party decision ledger is both the audit trail and the training/calibration corpus: every `decide ask` call plus the eventual ground truth (did verify pass? was the finding real? did the human accept the merge?) becomes a labeled example. This is what eventually funds a **fine-tuned typed-decisions checkpoint** on the project's own labels — the ceiling upgrade.

**Laya-as-cheap-tier routing.** Where shadow-mode labeled agreement with Haiku is high (B1, B2 especially), Laya **replaces** the Haiku hive tier for that decision; where agreement is marginal, Laya **pre-filters** (handles the confident bulk, escalates the uncertain tail to Haiku). OmniRoute remains the sole model-API egress; Laya is a local, non-egress tier below it.

**Avoiding over-application — rejection checklist.** Reject a proposed Laya integration if any is true:
- A regex/deterministic rule already does it correctly and cheaply → keep the rule.
- It would become a term in a gate/merge/proof predicate → forbidden.
- The state can't be compacted below the window without losing the deciding signal.
- You can't produce labels to calibrate it.
- The decision is rare (the ~1 s cost and the calibration overhead aren't worth it).
- It needs generation, reasoning, tool use, or non-English.
- A dropped/deprioritized item wouldn't be recoverable from original bytes.

### 4. External Patterns to Import

- **Classifier / semantic routing (RouteLLM — Ong et al., "RouteLLM: Learning to Route LLMs with Preference Data," LMSYS/UC Berkeley/Anyscale, ICLR 2025, arXiv:2406.18665).** A small model classifies query complexity/intent and routes to the cheapest capable tier. Reported: "cost reductions of over 85% on MT Bench, 45% on MMLU, and 35% on GSM8K as compared to using only GPT-4, while still achieving 95% of GPT-4's performance"; the matrix-factorization router "achieve[s] 95% of GPT-4 performance using 26% GPT-4 calls," dropping to ~14% of calls with LLM-judge data augmentation. The LMSYS RouteLLM blog frames the economics as ~$24.7/M tokens (GPT-4) vs ~$0.24/M (Mixtral 8x7B), "cost savings of up to 3.66x." **Transfers to:** C1/C2/C3 tier and breadth routing. Router overhead is small relative to inference — but Laya's ~1 s CPU cost is *not* small vs. a local call, so gate its use to where it saves a coordinator/lane.
- **Cascade routing (FrugalGPT — Chen, Zaharia & Zou, Stanford, arXiv:2305.05176).** Try the cheap model first, escalate on low confidence. Reported: "FrugalGPT can match the performance of the best individual LLM (e.g. GPT-4) with up to 98% cost reduction or improve the accuracy over GPT-4 by 4% with the same cost." **Transfers to:** C4 escalation and the whole shadow→A/B cascade. The cascade-routing theory (Dekoninck, Baader & Vechev, "A Unified Approach to Routing and Cascading for LLMs," ICML 2025, arXiv:2410.10347) shows the **quality estimator's calibration is the binding constraint** — "we identify good quality estimators as the critical factor for the success of model selection paradigms" → calibrate Laya.
- **Cross-encoder reranking (cross-encoder/ms-marco-MiniLM-L-6-v2, 22M params; Cohere Rerank; BGE/Jina).** Two-stage retrieve-broadly-then-rank-precisely. Per TianPan.co (2026): "Cross-encoders consistently outperform bi-encoder retrieval by 5–10 nDCG points on standard benchmarks," with ms-marco-MiniLM running "~50ms for 100 pairs on CPU" for "~35% accuracy improvement over pure vector retrieval," and Jina Reranker v3 at "61.94 nDCG@10 on the BEIR benchmark… at under 200ms." **Transfers to:** A2/A3 and the already-specced context/quartet ranking. Keep advisory (reorder, never drop).
- **Guardrail / verification classifiers (Llama Guard, Meta Prompt Guard/mDeBERTa, ProtectAI DeBERTa; TypeSafe "universal verification").** Small models screen inputs/outputs/tool-calls. **Transfers to:** F1/F3 quality signals and B3 error-typing — but here strictly advisory, because the factory's safety is the model-free gate spine, not a classifier.
- **LLM-as-judge vs. typed-decision tradeoff (Zheng et al., "LLM-as-a-Judge"; Chuang et al., "Trust or Escalate," arXiv:2407.18370).** Judges give free-text rationales but are slow, costly, unparseable, and can hallucinate; typed decisions give calibrated, parseable numbers and can't emit a malformed value. TypeSafe's self-consistency cookbook benchmarks a 14-question Noul call at $0.000043 / 111 ms against $0.0018 / ~1.8 s for claude-haiku-4-5 and ~$0.033 / 11-14 s for reasoning models (vendor figures, historical pricing, explicitly "not verified current billing"). **Transfers to:** D1 six-dimension scoring, E-series pre-screens — prefer Laya's typed scores over a Haiku "judge," then compose in code.
- **Calibration (Guo et al. temperature scaling; per-class/isotonic; strictly-proper scoring).** Post-hoc temperature scaling makes confidences trustworthy without changing argmax. **Transfers to:** the mandatory per-question-type calibration step.
- **Memory compaction (MemGPT/Letta; verbatim-vs-summarize, Morph/Factory.ai).** Summarization drift destroys exact detail; deletion/protection scoring preserves it. **Transfers to:** G1 protect-vs-summarize tagging.

### 5. The Ceiling and the Anti-Pattern List

**Tasks that look like System One tasks but are NOT (and why):**
- **Any gate/merge/lint/commit/push/proof predicate** (report lint, anti-pattern regex, lane gate, ledger validator, proof runner, pre-commit gates, clean-push, git/gh shim). Forbidden by construction — Laya is advisory, deterministic gates must stay model-free and replayable from bytes. A Laya answer may be an input a human/coordinator reads *near* these, never a term *in* them.
- **Writing the patch, the report, the summary, the commit message, the plan.** Generation — stays with the coordinator/local LLM.
- **Reasoning across a whole lane transcript or a large file.** Exceeds the window and needs multi-step reasoning — coordinator, or chunk-and-aggregate only for narrow per-chunk noul/score signals.
- **Large-label-space classification** (e.g., "which of 200 files/owners") in one shot — degrades badly past ~20 options (Banking77: 0.425 vs Jev's 0.870). [Flowtivity](https://flowtivity.ai/blog/laya-open-source-jev-alternative/) Use coarse-to-fine hierarchy or a shortlist step first.
- **Anything non-English / symbolic-heavy** — base checkpoint collapses while overconfident.
- **Exact/deterministic checks** (counts, digests, identity, schema) — a rule is cheaper, exact, and safe.
- **High-frequency inline hot-path decisions** where ~1 s/question would bottleneck — either async them or keep the regex.

**First step beyond a 421M/512-token encoder for the tempting-but-out-of-reach cases:**
1. **Fine-tune the typed-decisions checkpoint on the project's own ledger labels** — the primary upgrade. It clears the teacher ceiling on its four fine-tuned workflows (0.766) [Hugging Face](https://huggingface.co/convaiinnovations/laya/blob/main/README.md) and would specialize to the factory's own severity/role/error-type/verify-outcome distributions; the ledger flywheel supplies the labels.
2. **Use the multilingual/typed-decisions checkpoints' 1024-token window** (or raise `head_max_len`) for the borderline-too-long states (E1 verify summaries, G1 large blocks) before concluding a task is out of reach.
3. **Coarse-to-fine or shortlist** (`predict_shortlist`) for large-label tasks.
4. **Keep it with the coordinator** for anything genuinely needing reasoning/generation — that's not a failure of Laya, it's the correct boundary. A larger *local* classifier is only worth it if a specific decision is provably high-volume, high-value, and calibration on the fine-tuned checkpoint still underperforms.

## Recommendations

1. **Build the invocation surface first.** Ship the `decide ask` CLI + one-reviewed-decisions-file-per-skill convention + ledger logging before wiring any decision. This makes everything else shadow-able and replayable. Benchmark to change course: if per-decision logging + replay isn't working, stop and fix it before adding integration points.
2. **Start with B2 (hit-role) and B1 (severity/kind) in shadow.** They have ready-made labels (Haiku's current outputs), tiny fixed label spaces, and compact state — the cleanest first calibration. **Threshold to promote:** calibrated argmax agreement with a human-audited sample ≥ your Haiku baseline and ECE ≤ ~0.10 per question type.
3. **Then add C1 tier-routing and D1 bug-echo scores** — the compounding coordinator-token wins. **Threshold:** in A/B, coordinator tokens down measurably with no rise in escalations that a human overturns.
4. **Ship E1 (verify-outcome prediction) only after a long shadow run** because its failure cost is a wasted 4-7 h lane or a false "skip." Keep it advisory forever; the lane gate never sees it. **Threshold to act on it:** its predicted-pass calibration curve tracks actual verify outcomes on ≥ several hundred logged lanes.
5. **Calibrate per question type, always, before trusting probabilities.** Refit temperature whenever the checkpoint, the question wording, or the input distribution changes. Use the two-tier confidence bands as a *starting* policy and tune on your own cost-of-error.
6. **Once the ledger holds a few thousand labeled decisions per high-value question, fine-tune the typed-decisions checkpoint** on them and re-run A/B against the base checkpoint. That is the path to raising the ceiling without leaving the 421M/CPU envelope.
7. **Apply the rejection checklist to every proposal.** When in doubt between a regex and Laya for an exact check, choose the regex.

## Caveats

- **Every accuracy/latency/cost number for the model family is vendor- or author-reported and largely days-old at time of writing (Laya launched mid-September 2026, Jev September 15 2026).** The 0.766 typed-decisions accuracy is on the benchmark's own train-split fine-tune; [Hugging Face](https://huggingface.co/convaiinnovations/laya-typed-decisions) zero-shot is ~0.35. [Convaiinnovations](https://laya.convaiinnovations.com/) TypeSafe's own cookbook cost figures use historical/self-reported pricing explicitly labeled "not verified current billing," and were run with LLM conditions in a 16-way concurrent pool while Laya/Jev were sampled sequentially — affecting the latency comparison. Independent benchmarks on the factory's own data are required before trusting any figure.
- **Calibration is work, not a property.** Confidence-gating only rescues the deployment if probabilities are calibrated on the project's distribution; and it never rescues the non-English collapse (overconfident-and-wrong).
- **The ~1 s CPU floor is the design-shaping fact.** Anything that must be inline and fast is either a bounded few-question call or stays a regex. Don't design synchronous multi-question Laya calls into a hot path.
- **The advisory-only invariant is absolute.** If any proposed integration would make a Laya answer a term in a gate/merge/proof predicate, it is out of scope regardless of accuracy. Deprioritized/dropped items must always be recoverable from the original bytes.
- **Published confidence thresholds are illustrative, not calibrated guarantees** — the vendor's own docs say so and even use different example numbers in different places (0.5/0.9 vs 0.6/0.85 vs the 0.60 Choice / 0.30-0.70 Noul cookbook bands). Treat them as starting points to be tuned on labeled data and the cost of wrong actions.
- **Two integration points (H4 lane-state, and any gate-spine item) are listed only to mark them explicitly out of bounds** — they are enumerated so the exploring agent does not mistakenly route them to Laya.