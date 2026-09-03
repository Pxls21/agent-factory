---
topic: research-and-seeds
last_compiled: 2026-09-03
---

# Research and Seeds — findings, council, interview, seed, breakdown

## 1. Purpose [coverage: high -- 6 sources]

This topic covers the pipeline that designs a subsystem before code exists: research prompt
(optional) --> findings --> council debate --> Ouroboros interview --> committed seed --> task
breakdown --> build. Pipeline order is load-bearing. Stage 0 ran with NO research prompt by
owner decision (2026-09-02); the plan docs were the settled direction.

The pipeline for Stage 0 is COMPLETE: findings, council verdict, interview (ambiguity 0.10),
seed (8/8 self-validation), and 18-increment breakdown are all committed.

## 2. Architecture [coverage: high -- 5 sources]

**Pipeline artifacts (all committed):**

| Stage | File | Role |
|---|---|---|
| Findings | [docs/research/FINDINGS-STAGE0-v1.md](docs/research/FINDINGS-STAGE0-v1.md) | Probed capability ledger, environment table, per-proof constraints, Chairman addenda |
| Council | [docs/research/COUNCIL-VERDICT-STAGE0-v1.md](docs/research/COUNCIL-VERDICT-STAGE0-v1.md) | Wave-plan-v2 (unanimous), kill criteria KC-1..KC-7, unresolved questions, four-way classification |
| Seed | [seeds/seed-stage0-v1.yaml](seeds/seed-stage0-v1.yaml) | The contract: 12 per-proof blocks, frozen spike_to_class_mapping, repo layout, increment list |
| Breakdown | [tasks/stage0-breakdown.md](tasks/stage0-breakdown.md) | 18-increment decomposition, pinned decisions with rejected alternatives, venue update |

**Council composition:** Feynman (sonnet, 1.5x domain weight), Socrates (opus), Ada (sonnet).
Chairman synthesis only (no vote). Single-provider (Anthropic) caveat noted on unanimity.

**Interview:** Ouroboros `interview_20260902_221203`, final ambiguity 0.10.
Seed: `seed_0933ed382f70`, self-validation 8/8.

## 3. Talks To [coverage: medium -- 3 sources]

- Findings --> council (facts, not hypotheses)
- Council verdict + findings --> Ouroboros interview (constraint set)
- Interview --> seed (spec) --> task breakdown (decomposition)
- Breakdown --> [todo/BUILD-TASKLIST.md](todo/BUILD-TASKLIST.md) (execution tracker)
- Seed `verify_command`s --> deterministic self-validation

## 4. API Surface [coverage: low -- 2 sources]

- Ouroboros: `initial_context` (capped ~1.5k chars), resume with `{session_id, last_question,
  answer, ambiguity_score}`
- Seed format: YAML with `goal`, `task_type`, `brownfield_context`, `constraints`,
  per-proof sections, `spike_to_class_mapping`, `verify_command`s
- Council format: Problem, Composition, Chairman, Provider Routing, Acceptable Compromises,
  Kill Criteria, Concrete Next Step, Unresolved Questions, Consensus, Vote Tally, Key Insights,
  Points of Disagreement

## 5. Data [coverage: medium -- 3 sources]

- Findings: `docs/research/FINDINGS-STAGE0-v1.md` (capability ledger, environment probes)
- Council verdict: `docs/research/COUNCIL-VERDICT-STAGE0-v1.md`
- Seed: `seeds/seed-stage0-v1.yaml`
- Breakdown: `tasks/stage0-breakdown.md`
- Build tasklist: `todo/BUILD-TASKLIST.md` (the SSoT -- this wiki defers to it)

## 6. Key Decisions [coverage: high -- 5 sources]

- No research prompt for Stage 0 (owner, 2026-09-02): plan docs were the settled direction
- Wave-plan-v2 (council, unanimous): proofs classified by type, sequenced by falsification power
- Four-way classification (council): execution / conformance-checked decision /
  blocked-on-external-input / blocked-on-capability
- S0-03 must assert upstream model identity (Socrates): the pack's single most important assertion
- Capability facts logically prior to schedule (council): Wave-0 spikes before proof work
- Spikes classify, never gate (interview): frozen mapping applied mechanically
- Committed canonical fixtures drive REAL binaries (interview): rejected byte-exact, test-time
  gen, stub of SUT
- Chairman addenda (reproduced): bare unshare is total isolation; S0-03 was classification gap

## 7. Gotchas [coverage: high -- 5 sources]

**NOT-built (first-class):**
- The pipeline is complete (all artifacts committed); the BUILD is in progress (increment #1 closed 2026-09-03, #2 in progress)
- No application code, no proof runner, no CI workflow exist yet

**Council caveats:**
- Single-provider routing (Anthropic only) -- read unanimity with that caveat
- 8 unresolved questions remain (S0-03 class, S0-06 class, selective egress feasibility,
  gVisor host procurement, verification scheduling, S0-11 process primitives, cost side unargued)
- Ada's dependency edges unresolved (constraints vs hypotheses)

**Ouroboros quirks (all documented in CLAUDE.md):**
- `IS_SANDBOX=1` required for every backend-driving call
- `initial_context` cap (~1.5k) poisons the session if exceeded
- Shell metacharacters rejected; certain words blocklisted ("subprocess")
- `generate_seed` writes no file -- transcribe to `seeds/` immediately
- Native MCP broken (SDK v2 vs v1.x); stdio fallback works

## 8. Sources

- [docs/research/FINDINGS-STAGE0-v1.md](docs/research/FINDINGS-STAGE0-v1.md)
- [docs/research/COUNCIL-VERDICT-STAGE0-v1.md](docs/research/COUNCIL-VERDICT-STAGE0-v1.md)
- [seeds/seed-stage0-v1.yaml](seeds/seed-stage0-v1.yaml)
- [tasks/stage0-breakdown.md](tasks/stage0-breakdown.md)
- [todo/BUILD-TASKLIST.md](todo/BUILD-TASKLIST.md)
- [docs/07_BUILD_PLAN.md](docs/07_BUILD_PLAN.md)
