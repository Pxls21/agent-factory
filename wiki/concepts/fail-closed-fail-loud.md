---
concept: Fail-Closed Fail-Loud
last_compiled: 2026-09-03
topics_connected: [production-spine, memory-and-governance, security-and-containment, stage0-proof-pack, evaluation-and-improvement, decisions-and-premortem]
status: active
---

# Fail-Closed Fail-Loud — ambiguity resolves to REJECT

## Pattern

Every authorization boundary in the system resolves ambiguity to denial. Policy outage, malformed
result, broken deny rule, no match, unknown input -- all deny. The complementary principle is
fail-LOUD: every failure carries a reason, every degradation is visible, every silent path is a
defect. The two together mean: the system never silently does the wrong thing, and when it stops,
it says why.

This pattern appears at every trust boundary the architecture defines, even though none of them
have been built yet.

## Instances

- **Policy service** in [security-and-containment](topics/security-and-containment.md): deny
  before allow; any deny wins; broken deny rule denies; broken allow grants nothing; no
  match/unknown denies. Hermes `pre_tool_call` with `fail_closed: true`. Premortem #8: policy
  outage must not fail open.
- **Memory adapter** in [memory-and-governance](topics/memory-and-governance.md): `pre_llm_call`
  fails open (known Hermes behavior), so strict memory workflows need a SEPARATE preflight. Normal
  recall degrades visibly (D-008). Auto-improve starts off (D-017).
- **Hermes runtime** in [production-spine](topics/production-spine.md): OmniRoute failure is
  not a fallback to a direct provider -- the sole-egress rule means failure = denial, never
  degradation to an uncontrolled path.
- **Stage 0 proofs** in [stage0-proof-pack](topics/stage0-proof-pack.md): blocked markers map
  `credential_rejected` to proof-RED (never blocked). CI's `stage1-gate` is RED by design until
  every required proof satisfies. An empty set never passes.
- **Evaluation** in [evaluation-and-improvement](topics/evaluation-and-improvement.md):
  generated harness security veto is independent of aggregate quality score (premortem #7). A
  quality pass with a security regression still fails.
- **Telemetry** in the planned common audit envelope: every decision/branch/abstain/error emits
  an event carrying the REASON. Silent decision paths are defects.

## What This Means

The pattern is load-bearing because the system handles model-generated arguments, untrusted
memory, and generated harness code. A fail-open boundary at any of these points turns a
prompt-injection or a corrupted recall into authorized action. The architecture's response is to
make the closed state the default everywhere and the loud state the only degraded mode -- never
silent degradation. The one known exception (`pre_llm_call` fails open) is called out honestly
and mitigated with a separate preflight.

## Sources

- [production-spine](topics/production-spine.md)
- [memory-and-governance](topics/memory-and-governance.md)
- [security-and-containment](topics/security-and-containment.md)
- [stage0-proof-pack](topics/stage0-proof-pack.md)
- [evaluation-and-improvement](topics/evaluation-and-improvement.md)
- [decisions-and-premortem](topics/decisions-and-premortem.md)
