---
concept: Isolation by Design
last_compiled: 2026-09-03
topics_connected: [security-and-containment, evaluation-and-improvement, memory-and-governance, production-spine, stage0-proof-pack, pc-bridge-and-environment]
status: active
---

# Isolation by Design — untrusted planes cannot reach production authority

## Pattern

Every plane that processes untrusted or model-generated material is structurally isolated from
production authority. The dream worker has no ai-memory admin credential. JIT candidates have no
production secrets or network. AlphaEval runners have no host networking. The composite memory
adapter is the authorization boundary, not ai-memory's native token. gVisor contains the whole
runtime, not individual tools. OmniRoute is the sole egress -- no direct provider path exists to
fall back to.

The pattern is: make the bad state unrepresentable rather than checking for it at runtime.

## Instances

- **Dream worker** in [evaluation-and-improvement](topics/evaluation-and-improvement.md): reads
  immutable sanitized snapshots, writes proposal bundles only, never receives ai-memory admin
  credentials or production tool access. ADR 0004 codifies this.
- **JIT Foundry** in [evaluation-and-improvement](topics/evaluation-and-improvement.md):
  candidates run in a no-secret/no-production-network sandbox. Output is an untrusted artifact
  until static, behavioral, security, and human gates complete.
- **AlphaEval** in [evaluation-and-improvement](topics/evaluation-and-improvement.md): stock
  runner is UNSAFE (host net, chmod 777, credential passing). Hardening removes all three. Rubric
  code in a separate unprivileged gVisor sandbox.
- **Memory adapter** in [memory-and-governance](topics/memory-and-governance.md): the adapter
  is the authorization boundary (D-007). Same-workspace ai-memory tokens are not per-project RBAC.
  Promotion is a separate reviewed workflow.
- **OmniRoute** in [production-spine](topics/production-spine.md): no upstream keys in Hermes
  or any other component. OmniRoute failure = denial, not fallback. S0-05 proves no direct egress.
- **gVisor** in [security-and-containment](topics/security-and-containment.md): contains the
  whole Hermes runtime (D-010). Per-tool isolation requires a broker that does not exist.
- **Selective egress** in [stage0-proof-pack](topics/stage0-proof-pack.md): bare `unshare --net`
  is total isolation (proven). Selective egress (allow OmniRoute, deny model endpoints) needs
  veth/proxy -- a structural mechanism, not a runtime check.
- **PC bridge** in [pc-bridge-and-environment](topics/pc-bridge-and-environment.md): bridge
  tokens are ephemeral and never committed. The bridge is HTTP-only (sandbox egress is 80/443).
  No direct host access from the sandbox.

## What This Means

The architecture bets that structural isolation (no credential exists, no network route exists,
no file is writable) is stronger than runtime checks (deny rules, permission prompts, policy
hooks). Every trust boundary in the design is a credential/network boundary, not a software
check -- and the Stage 0 proof pack tests the structural properties (canary FAILS, not canary
PASSES a check). The risk is that structural isolation makes the system harder to operate and
debug, but the premortem (#5, #6, #13, #14) shows that the alternative -- runtime checks that
can be misconfigured or bypassed -- is the dominant failure mode.

## Sources

- [security-and-containment](topics/security-and-containment.md)
- [evaluation-and-improvement](topics/evaluation-and-improvement.md)
- [memory-and-governance](topics/memory-and-governance.md)
- [production-spine](topics/production-spine.md)
- [stage0-proof-pack](topics/stage0-proof-pack.md)
- [pc-bridge-and-environment](topics/pc-bridge-and-environment.md)
