# Council brief — the Jev/Laya "System One" layer for the Agent Factory (v1, 2026-09-22)

**Pipeline position:** audit (five repositories, `docs/research/findings/jev-audit/`) → RESEARCH-PROMPT-2 → its two findings (`docs/research/findings/RESEARCH-FINDINGS-2-part1-laya-sieve-fp32-build-spec.md`, `…-part2-system-one-integration-map.md`) → **this council** → Ouroboros interview → seed → breakdown → build (owner: Opus + ultracode). The council debates the FINDINGS as facts and returns a verdict with kill criteria; it does not re-research.

## 0. The question

Should the factory build a self-hosted, advisory typed-decision layer (Laya, a ~421M-parameter encoder answering typed questions with calibrated probabilities) now, in what order, on which venue, gated how — and which of the ~20 candidate integration points earn a place in the first increment? The council must answer: (Q1) build now vs after the Stage 0 proof pack closes; (Q2) the first three integration points and the rejection of the rest; (Q3) the shadow → calibrate → A/B rollout gates and their numeric thresholds; (Q4) the venue (sandbox CPU / PC CPU / PC GPU) per stage; (Q5) what would make the whole layer a mistake (kill criteria KC-J1…).

## 1. CURRENT-STATE CAPABILITY LEDGER (read this before any advice; an under-briefed panel returns confident advice about a system that does not exist)

| Capability | Status | Evidence |
|---|---|---|
| A local Laya checkpoint on either venue | **ABSENT** | no download, no install; the sandbox has no checkpoint, the PC has none (audit 2026-09-22; `docs/research/findings/jev-audit/laya-evidence.md`) |
| The `laya-decide` loopback service (`/v1/systemone` + `/v1/decide`) | **ABSENT** | spec only (findings part 1, "Build spec — laya-decide") |
| The `sieve-run` wrapper | **ABSENT** | spec only |
| The first-party decision ledger (canonical(redact(state)) digest, append-only, replay) | **ABSENT** (D-041 decided it is first-party, not jevcache) | `docs/08_DECISION_LOG.md` D-041 |
| Any Laya-backed decision in any skill/workflow | **ABSENT** | `docs/research/findings/jev-audit/our-decision-points-evidence.md` inventories the candidate points; none wired |
| Measured FP32 latency on THIS hardware | **NOT MEASURED HERE** | the findings cite ~1.0–1.25 s/question FP32 on 4 cores from Laya's own repo and community ports; the Ryzen 5 5600X (Zen 3, no VNNI) is expected to REGRESS on INT8 (~1.7×) — projection, not a local measurement |
| Sandbox CPU/RAM | **MEASURED** | 4 cores, 15 GB; torch forces float32 on CPU (≈1.7 GB per 421M checkpoint) |
| PC GPU headroom for a GPU path | **MEASURED, NONE TODAY** | 24,022 of 24,576 MiB in use by the vLLM `qwen` container (2026-09-22); the GPU path needs the owner's restart of that container (D-040) |
| Claude Code hook seams in the sandbox | **PRESENT, UNFIRED** | CLI 2.1.278; `session.compact`/`turn.complete`/`CLAUDE_CODE_ENABLE_FUNCTION_HOOKS` strings present in the binary; `PostToolUse updatedToolOutput` may be INERT for Bash (issue #68951, unverified on 2.1.278); the Q5 fire-test has NOT been run |
| Hermes hook seams on the PC | **PRESENT, UNFIRED** | `transform_terminal_output` exists in BOTH Hermes trees (pinned 527da60 and the lane runtime b3399c1, measured 2026-09-22); the Q4 fire-test + inner-deadline test NOT run |
| Compaction on the coordinator session | **BUILT-IN ONLY** | Claude Code's own summary; `tamaratran/fast-jev-compaction` (MIT, e3f262a) is a function-hook plugin with an injectable `baseUrl` — audited, not installed (`jev-audit/fast-jev-compaction-evidence.md`) |
| Tool-output pruning | **NONE** | jev-pruner / winnow audited (MIT), neither installed; the byte-share numbers (tool output = 46.9 % of the coordinator transcript, 90 % of PC-lane context bytes) are the findings' projections from our own stores |
| Labeled data for calibration | **ABSENT** | zero labeled (block, keep/drop) pairs; the findings require ≥ 200–750 labels per question type for a trustworthy ECE |
| The deterministic gate spine (report lint, AP screen, lane gates, ledger validator, proof runner, pre-commit/pre-push) | **BUILT, LIVE** | rule 12 + the project's #1 rule: no LLM-judge in the gate spine; Laya is ADVISORY by decision |
| Local model egress | **LIVE** | every model request through OmniRoute on the PC (`:20128`); a hosted TypeSafe key would be a SECOND egress and a direct provider credential (rule 3) — the findings' answer is the first-party loopback service |
| Stage 0 proof pack | **IN PROGRESS** | the standing gate: spine-dependent feature work waits on Stage 0; a minted proof's component builds in its own lane (D-029) — the Laya layer touches NO proof and no production spine |

## 2. The constraint set (from the findings; treat as facts)

1. **FP32 only on this CPU.** INT8 slows Zen 3 by ~1.7× (no VNNI); bf16 is emulated; batching does not amortize (each question is a separate ~512-token encoder pass); ~1.0–1.25 s/question is the floor → inline synchronous sieving on the coordinator's critical path is infeasible; background/offline/PC-only by default.
2. **Advisory only, by construction.** Never a term in a gate/merge/lint/commit/push/proof predicate. Rank, filter, classify, flag, score. A dropped item must be recoverable from original bytes.
3. **The base checkpoint is a specialist:** zero-shot typed-decisions accuracy 0.362 (below the 0.461 majority baseline), over-confident as shipped (ECE 0.175 typed / 0.466 raw); English only (non-Latin scripts collapse while confident); ≤ ~20 options per question; calibration must be re-fit locally per question type (temperature scaling, equal-frequency bins B = 10–15, ≥ 200–750 labels/type); the fine-tuned checkpoint (0.766) is the ceiling case and needs the project's own labels (~30k questions, 2×T4 ≈ 4–5 h).
4. **Seams:** Claude Code — `PreToolUse updatedInput` (reliable) → `sieve-run -- <cmd>` wrapper; `PostToolUse updatedToolOutput` possibly inert for Bash (fire-test first); function hooks early-access. Hermes — `transform_terminal_output` (purpose-built, abandoned-not-fail-closed on timeout → the sieve enforces its own inner deadline, fail-open with a `[sieve: fail-open]` marker); `pre_tool_call` fails CLOSED on timeout (avoid).
5. **Rejection checklist** (any true → reject the integration point): a regex already does it correctly and cheaply · it would enter a gate predicate · the state cannot be compacted below the window without losing the deciding signal · no labels can be produced · the decision is rare · it needs generation/reasoning/tool use/non-English · a dropped item is unrecoverable.
6. **The ~20 candidate points, Tier 1 per the map:** B2 hit-role (def/caller/config/test/other) for code-search hits · B1 finding severity/kind · D1 the bug-echo six advisory scores · C2 breadth routing (pre-filter of the Haiku hive tier) · C1 tier routing; E1 verify-outcome prediction SHADOW-ONLY; G1 protect-vs-summarize tagging for compaction; Q8 the ranked view beside raw code-search (PC-only/offline at ~1 s/row).
7. **Rollout:** Stage 0 build the service (FP32, both endpoints, the ledger) → Stage 1 fire-tests (adopt only the seam proven to fire) → Stage 2 shadow mode one week on both lanes (regret ≤ 2 % at the chosen drop threshold on hand labels; ≥ 80 % of bytes above the floor) → Stage 3 calibrate then A/B (needle retention ≥ 98 %; a net token reduction that survives the added latency) → Stage 4 specialize (fine-tune) only if accuracy is the bottleneck.
8. **Empirical gates NOT resolved** (each a runnable command + rule; part 1 §NOT-RESOLVED): FP32 p50 on 4 cores; the Bash `updatedToolOutput` fire-test; the Hermes `transform_terminal_output` fire + inner-deadline test; the per-venue byte floor; regret vs threshold on ~100 hand labels; ECE per question type; a bitwise ledger replay of one day; the no-outbound-socket proof; the INT8 sanity run (expected negative).

## 3. Decisions already made (not for re-litigation)

- **D-040** both venues: a first-party local decide service in the sandbox on CPU and on the PC (GPU when headroom exists; CPU otherwise).
- **D-041** the ledger is first-party (jevcache ships no source, no license, no checksum; unpinnable under rule 13).
- **Rule 12 / the #1 rule:** deterministic gates stay deterministic; Laya informs, never decides a green.
- **Rule 3:** sole model egress through OmniRoute — no hosted TypeSafe key; the service is loopback-only with a no-outbound-socket proof.
- **Rule 13:** every upstream (the Laya checkpoint revision, the `laya` PyPI version, any vendored plugin such as fast-jev-compaction) pinned by immutable commit/digest in `upstream.lock.yaml` and the vendored manifest.

## 4. What the council must return

1. A verdict on Q1–Q5 with the reasoning, in the shape of `docs/research/COUNCIL-VERDICT-STAGE0-v1.md` (a wave plan + kill criteria).
2. **Kill criteria KC-J1…** (numeric where possible): e.g. FP32 p50 > N ms on 4 cores AND no async seam fires → stop; regret > 2 % at every drop threshold on hand labels → shadow only, never active; ECE > 0.05 after temperature fit with ≥ 200 labels → the point is rejected; any Laya output found inside a gate predicate → the layer is pulled.
3. The FIRST increment's boundary (files, venue, the deterministic acceptance test per step) so the Ouroboros interview can seed it — including whether the first increment is the service alone (part 1's Stage 0) or the service plus ONE integration point in shadow mode.
4. An explicit list of the integration points REJECTED by the checklist, with the failing clause each.
5. Where the council disagrees with the findings, say which finding, why, and what measurement would settle it.

## 5. Panel guidance

Facts over hypotheses: cite the findings files by section. Every quantitative claim traces to part 1 or part 2, or is marked as the council's own estimate. The Chairman's synthesis carries a CURRENT-STATE line first ("nothing of this layer runs on either venue today") so the verdict cannot be read as a status claim.
