---
topic: decisions-and-premortem
last_compiled: 2026-09-03
---

# Decisions and Premortem — the reasoning record

## 1. Purpose [coverage: high -- 5 sources]

This topic collects the project's architectural decisions (18 accepted, 7 open implementation
choices, 5 owner inputs pending) and the 20-item ranked premortem. Decisions are the "why it is
shaped this way" layer; the premortem is the "how it fails" layer. Together they set the negative
controls for Stage 0.

## 2. Architecture [coverage: high -- 3 sources]

**Decision records:** compact table in [docs/08_DECISION_LOG.md](docs/08_DECISION_LOG.md),
expanded ADRs in [docs/adr/](docs/adr/) for trust-boundary, data-model, component, or
operational contract changes:
- [0001](docs/adr/0001-hermes-only-runtime.md): Hermes sole runtime
- [0002](docs/adr/0002-omniroute-sole-model-egress.md): OmniRoute sole egress
- [0003](docs/adr/0003-four-logical-memory-scopes.md): four-scope memory
- [0004](docs/adr/0004-isolated-improvement-planes.md): isolated improvement planes

**Premortem:** [docs/09_PREMORTEM.md](docs/09_PREMORTEM.md) -- 20 failure modes ranked by
impact x likelihood, 10 stop-the-line conditions, and an incident template.

## 3. Talks To [coverage: medium -- 3 sources]

- Decisions --> integration contracts (the "what" that follows the "why")
- Premortem --> Stage 0 proof negative controls (each proof kills a premortem risk)
- ADRs --> standing agent rules (AGENTS.md enforces the accepted decisions)
- Open choices (X-001..X-007) --> Stage 0 proofs S0-09, S0-10, and owner inputs

## 4. API Surface [coverage: low -- 1 source]

Not applicable -- decisions and premortem are documents, not code. The ADR format: Status, Date,
Context, Decision, Consequences. Values: proposed, accepted, superseded, rejected.

## 5. Data [coverage: low -- 1 source]

- Decision log: `docs/08_DECISION_LOG.md` (compact table)
- ADR files: `docs/adr/0001..0004` (expanded records)
- Premortem: `docs/09_PREMORTEM.md` (ranked failure modes + stop-the-line list)

## 6. Key Decisions [coverage: high -- 5 sources]

**Accepted (D-001 through D-018):** see [project-overview](topics/project-overview.md) SS6 for the
summary. The load-bearing ones:
- D-001: Hermes sole runtime (removes 4 parallel execution paths)
- D-003: OmniRoute sole egress (centralizes credentials)
- D-006: four-scope memory (adapter as authorization boundary)
- D-009: fail-closed pre_tool_call hook
- D-010: whole-runtime gVisor (not per-tool)
- D-017: auto-improve off; promotion reviewed

**Open:**
- X-001: GBrain adapt vs wrap
- X-002: first-party harness host vs OpenHarness
- X-003: JIT-to-Hermes translation
- X-004: HarnessRouter activation criteria
- X-005: PandaProbe enablement
- X-006: shared workspace vs separate ai-memory instances
- X-007: native Hermes Buzz plugin as simplification

**Owner inputs still needed:** first-party license (Apache-2.0 or MIT), deployment target and
Docker `runsc` availability, initial Buzz users/channels, first OmniRoute route/budget,
default memory degradation policy.

## 7. Gotchas [coverage: medium -- 3 sources]

**NOT-built (first-class):**
- No ADR has driven implementation yet (all are accepted design decisions)
- Open choices X-001..X-007 are live; their Stage 0 proofs (S0-09/10) resolve them
- 5 owner inputs are pending and block operational decisions

**Premortem top-3 risks:**
1. ACP bridge and hermes-acp lifecycle disagreement (turns hang, cancel poorly, duplicate)
2. OmniRoute works for text but corrupts/drops tool calls
3. Four-scope adapter leaks data across scopes

**The premortem's value is the failures it names** -- the doc is often the most valuable
engineering read in the repo.

## 8. Sources

- [docs/08_DECISION_LOG.md](docs/08_DECISION_LOG.md)
- [docs/09_PREMORTEM.md](docs/09_PREMORTEM.md)
- [docs/adr/README.md](docs/adr/README.md)
- [docs/adr/0001-hermes-only-runtime.md](docs/adr/0001-hermes-only-runtime.md)
- [docs/adr/0002-omniroute-sole-model-egress.md](docs/adr/0002-omniroute-sole-model-egress.md)
