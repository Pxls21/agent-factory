# 11 — Harness Foundry & the Genesis Team (Phase 2) (v2)

**Version:** 2.0 · **Date:** 2026-09-01 · **Status:** Phase 2 — do NOT block the v1 build on this.

Build the v1 system (`00`–`10`) on fixed, vetted harnesses first. A generated harness is unproven code every time, which collides with "audited-before-install" and "no hollow greens" — so it must boot inside gVisor+CEL and pass a conformance + negative-control gate before it's trusted.

---

## 1. The idea
Just as the factory makes agents on the fly, it makes their harness on the fly when needed:
```
new agent needed
  ├─ needs no harness → MCP tool/capability (Door 3)
  ├─ stock suffices  → Hermes / Claude Code / Codex / Pi  (Door 1, ACP-direct)
  └─ needs custom    → SYNTHESIZE a harness in the Harness Foundry  (Door 4)
```

## 2. The Genesis Team (agents that build agents) — channel `#agent-forge`
| Role | Makes | Responsibility |
|---|---|---|
| **Architect** | the agent | persona + brain scope + skill pack + tool grants; drives Fubuki compile |
| **Harness Smith** | the harness | runs the decision tree; operates the Foundry for custom harnesses |
| **Conformance Warden** | trust | runs the conformance + negative-control gate on the Smith's output (must be a *different* agent — roles can't grade their own work) |
| **Registrar** | the catalog | curates the registry of agent configs / harnesses / tools / skill packs; answers "do we already have one?" |
| **Curator** | memory | the nightly dream-phase promotion agent (`05`) |

Each Genesis agent is a normal factory agent (own keypair, own Fubuki brain, ai-memory scope, behind CEL+gVisor). The system bootstraps itself; the first agents are built by hand from these docs.

## 3. The Harness Foundry (Door 4)
JIT-Agent-style: given a task spec + target protocol + tool/skill registry + retrieved prior harnesses, it emits an executable, task-specific harness (structured code, not free-form) factored into four modules against **our** interfaces:

| Module | Binds to |
|---|---|
| Memory | the forked **ai-memory** scope (`04`) — NOT a bespoke store |
| Planning | free to vary (task-specific) |
| Action | every tool call through the **CEL gate** + **gVisor** (`07`) |
| Capability | model calls **only through OmniRoute**; the harness speaks **ACP** so `buzz-acp` drives it |

Frozen generator, evolving archive (revise from traces, keep versions) — maps onto BRAIN/HANDS and the dream loop. Generate **into the OpenHarness skeleton** (a vetted minimal base) rather than emitting a whole runtime — smaller, safer diffs. A degenerate case is a deterministic tool driver (e.g. a thin driver whose capability module is Fubuki's CLI, no model egress).

## 4. The trust gate (non-negotiable for Door 4)
A generated harness is new code → cannot inherit stock trust. Before real use: (1) boots inside gVisor with CEL on from its first call; (2) passes a harness-conformance suite (clean ACP handshake; egress only to OmniRoute; every tool call hits CEL); (3) passes a de-vacuoused negative-control task; (4) enters the Registrar's catalog as a versioned, hash-pinned artifact with a rollback target. The Warden runs this and is a different agent from the Smith.

## 5. Registry (why it's a team, not a script)
```
registry/
  agents/<slug>/            # persona manifest + brain scope + harness ref + skill pack refs
  harnesses/
    stock/                  # hermes, claude-code, codex, pi (vetted, pinned)
    generated/<hash>/       # Foundry output: builder + 4 module providers + conformance report
  skill-packs/<name>/       # SKILL.md bundles
  tools/<name>/             # MCP descriptors + CEL policy + containment profile
  frameworks/               # adapters for deepagents/langchain/etc.
```
The catalog is ai-memory-backed (markdown + provenance) and distillation-eligible (a harness pattern that keeps working is promoted; one that keeps failing becomes an anti-pattern entry).

## 6. When HarnessRouter comes back
If a generated or third-party harness speaks **UHP/Responses but not ACP**, fold in HarnessRouter (`:3100`) + the **ACP↔UHP shim** here. That's the only scenario that resurrects the shim dropped from v1.

## 7. Build order (Phase 2)
1. Ship v1 on fixed harnesses.
2. Stand up Architect + Harness Smith + Registrar (stock harnesses only) — high value, low risk.
3. Add the Conformance Warden + trust gate **before** the Foundry.
4. Add the Foundry, generating into OpenHarness; start with deterministic tool drivers.
5. Turn on the trace→revise→archive loop.

## 8. Pre-mortem additions (fold into `10`)
Generated harness malicious/broken → gVisor+CEL from first call + conformance gate; non-determinism → hash-pin + best-of-N then freeze; cost blowout → decision tree gates synthesis (stock by default); archive drift → Registrar dedup + distillation; Warden grades Smith's work → independent verifier; generated harness bypasses egress → conformance asserts OmniRoute-only + ACP.

## 9. Open items [V]
JIT internal four-module contract + license (read `harness_factory/` + `jit/` from source before building the generator); the generator model host (local vs OmniRoute — mirror D6).
