---
topic: stage0-proof-pack
last_compiled: 2026-09-03
---

# Stage 0 Proof Pack — twelve proofs, four-way classification, wave plan

## 1. Purpose [coverage: high -- 7 sources]

Stage 0 is the current gate: no broad feature work until it validates the
Buzz-->ACP-->Hermes-->OmniRoute spine, memory composition, Fubuki seams, policy failure behavior,
and gVisor compatibility. Twelve proofs (S0-01 through S0-12) are decomposed into 18 build
increments plus a Wave-0 spike set, sequenced by the council's wave-plan-v2.

**Build status: NOT STARTED.** Spike #0 (pc-bridge liveness) is done; 0 of 18 increments
complete; the first pending is `s0-01-registry-schemas-validator`. The authoritative status lives
in [todo/BUILD-TASKLIST.md](todo/BUILD-TASKLIST.md) -- this article defers to it.

## 2. Architecture [coverage: high -- 6 sources]

**Twelve proofs** with four-way classification (never a flat N/12):

| Class | Proofs | Denominator |
|---|---|---|
| Execution proof | S0-01, S0-02, S0-03, S0-04, S0-05, S0-06 (spike-gated: the rust-ai-memory spike can flip it to blocked-on-capability, `map-rust-s006`), S0-07, S0-11 | artifacts with digest-verified `runs[]` (both control legs) |
| Conformance-checked decision | S0-09, S0-10, S0-12 | ADR sections + machine-checkable shell |
| Blocked on external input | (none currently; S0-03 reclassified after PC probe) | credential/input from the owner |
| Blocked on capability | S0-08 | runsc install on the PC |

**Wave structure** (wave-plan-v2, council-approved):
- Wave 0 (spikes, parallel): #3 rust-ai-memory, #4 dockerd, #5 runsc, #6 selective-egress,
  plus spike #0 (pc-bridge, DONE)
- Wave 1 (disjoint proofs, parallel): #7 S0-01, #8 S0-02, #9 S0-07, #10 S0-09, #11 S0-10,
  #12 S0-12
- Wave 2 (spine, sequential): #13 S0-06, #14 S0-03, #15 S0-04, #16 S0-05
- Wave 3: #17 S0-08 (spec now, run after runsc), #18 S0-11

**Machinery increments** (1-2): registry + schemas + validator, runner + ledger generator +
CI + markers. Self-verifying from an empty artifact set.

Key files: [seeds/seed-stage0-v1.yaml](seeds/seed-stage0-v1.yaml) (the contract),
[tasks/stage0-breakdown.md](tasks/stage0-breakdown.md) (the 18-increment decomposition),
[docs/07_BUILD_PLAN.md](docs/07_BUILD_PLAN.md) (the stage plan).

## 3. Talks To [coverage: medium -- 4 sources]

- Proof runner --> `proofs/<s0-NN>/result.json` (commands, timestamps, exit codes, digests,
  env_fingerprint)
- Ledger generator --> `proofs/ledger.yaml` (deterministic, run twice, byte-identical)
- CI: two split checks -- `ledger-integrity` (green on honest set, even empty) and `stage1-gate`
  (RED by design until registry's required set satisfied)
- Spikes --> `spikes/<name>/result.json` (facts, classification effects via frozen
  `spike_to_class_mapping`)

## 4. API Surface [coverage: high -- 5 sources]

Planned schemas (increment #1):
- `proofs/registry.yaml`: 12 entries with classes, waves, spike deps, required negative-control
  counts, blocked owners/unblock_conditions
- `proofs/schemas/{result,blocked,spike}.schema.json`: including `env_fingerprint`
- `proofs/normalization.yaml`: volatile-field list for golden-transcript comparison
- Runner: writes `result.json` only from real subprocess runs (cmd, timestamps, exit, sha256
  digests, env_fingerprint); never from stubs

## 5. Data [coverage: medium -- 3 sources]

- Proof artifacts: `proofs/<s0-NN>/result.json` with sha256 digests
- Spike results: `spikes/<name>/result.json` with classification_effect
- Existing: `spikes/pc-bridge/result.json` (spike #0, done 2026-09-03)
- Ledger: generated (never hand-authored), byte-identical across runs
- Blocked markers: probe-backed, re-evaluated every CI run; `credential_rejected` maps to
  proof-RED (never blocked)

## 6. Key Decisions [coverage: high -- 7 sources]

**Pinned decisions from the interview** (each with rejected alternative in
[tasks/stage0-breakdown.md](tasks/stage0-breakdown.md)):
- Runner-emitted `result.json` is SSoT; ledger GENERATED, CI drift-fails (rejected: hand-authored
  ledger)
- Two SPLIT CI checks (rejected: one check doing both -- empty repo would pass)
- Spikes classify, never gate; frozen `spike_to_class_mapping` (rejected: all spikes must pass)
- Committed canonical fixtures drive REAL binaries; normalized-then-golden compare (rejected:
  byte-exact / test-time generation / stub of SUT)
- Blocked markers carry probe re-evaluated every CI run (rejected: static presence check)
- Four-way classification; status lines never a flat N/12 (rejected: 12 undifferentiated proofs)
- S0-03 blocks on real credential; pass asserts upstream model identity (rejected: run against
  S0-04 stub)
- S0-05 mechanism split (rejected: wholesale host-deferral)

**Council kill criteria KC-1 through KC-7** gate the build (full text in
[docs/research/COUNCIL-VERDICT-STAGE0-v1.md](docs/research/COUNCIL-VERDICT-STAGE0-v1.md)).

## 7. Gotchas [coverage: high -- 7 sources]

**NOT-built (first-class):**
- 0 of 18 increments complete (only spike #0 done)
- No registry, no schemas, no validator, no runner, no ledger generator, no CI workflow
- No spike completed except pc-bridge (#0)
- No proof has been executed

**Build constraints:**
- Every proof exercises the REAL pinned component; the one sanctioned stub is S0-04's
  deterministic upstream behind real OmniRoute
- Every proof needs at least one negative control failing for the exact expected reason
- Tests deterministic and LLM-free; run twice, byte-identical
- S0-08 deferred (runsc absent); spec + fixture + `NOT run here: <reason>` marker is accepted
  evidence ONLY when paired with procurement of a real host
- S0-03's upstream = the PC's local vLLM behind OmniRoute (identity `sim9b`); the credential
  question is closed but the round trip has not been executed

**Kill criteria that could invalidate the plan:**
- KC-1: if Wave-0 selective-egress spike fails, S0-05 placement invalidated
- KC-2: if no named owner/date for real credential by Wave-1 close, S0-03 RED-pending and
  Stage 1 must not open
- KC-4: if any status line reads as a flat "N/12", three-way classification has failed
- KC-5: if two+ Wave-1 proofs pass without named negative controls, discipline has decayed

## 8. Sources

- [seeds/seed-stage0-v1.yaml](seeds/seed-stage0-v1.yaml)
- [tasks/stage0-breakdown.md](tasks/stage0-breakdown.md)
- [docs/07_BUILD_PLAN.md](docs/07_BUILD_PLAN.md)
- [docs/research/FINDINGS-STAGE0-v1.md](docs/research/FINDINGS-STAGE0-v1.md)
- [docs/research/COUNCIL-VERDICT-STAGE0-v1.md](docs/research/COUNCIL-VERDICT-STAGE0-v1.md)
- [todo/BUILD-TASKLIST.md](todo/BUILD-TASKLIST.md)
- [spikes/pc-bridge/result.json](spikes/pc-bridge/result.json)
