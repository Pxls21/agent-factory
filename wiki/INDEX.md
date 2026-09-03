# agent-factory Knowledge Base

Last compiled: 2026-09-03
Total topics: 12 | Total concepts: 3 | Total sources: 62 (sum of per-topic source lists;
files feeding several topics are counted once per topic)

A governed, memory-aware agent system with Hermes as the sole stock production workhorse,
currently in architecture and planning stage on branch `claude/soundbox-kit-migration-iz1jwf`.
**No application code exists.** Start with [project-overview](topics/project-overview.md) for
the shape of the system, [stage0-proof-pack](topics/stage0-proof-pack.md) for what comes next,
and [CONTEXT.md](CONTEXT.md) for how to use this wiki without over-trusting it.

**Authority order.** `todo/BUILD-TASKLIST.md` wins over this wiki on any build-status or count
disagreement; the planning docs and their tests win over any wiki paraphrase; this wiki is a
distillation and will drift.

## Topics

| Topic | Also Known As | Sources | Last Updated | Status |
|-------|---------------|---------|--------------|--------|
| [project-overview](topics/project-overview.md) | Agent Factory, governed agent system, Hermes workhorse, build spine, planning stage, ground truth | 13 | 2026-09-03 | active |
| [production-spine](topics/production-spine.md) | Buzz, buzz-acp, hermes-acp, ACP, OmniRoute, codex_responses, live path, interaction bridge | 8 | 2026-09-03 | active |
| [memory-and-governance](topics/memory-and-governance.md) | four scopes, ai-memory, Fubuki, composite adapter, persona_lint, BoundDecision, governance hash | 6 | 2026-09-03 | active |
| [security-and-containment](topics/security-and-containment.md) | policy gate, gVisor, runsc, egress, threat model, fail-closed, containment, canaries | 6 | 2026-09-03 | active |
| [evaluation-and-improvement](topics/evaluation-and-improvement.md) | AlphaEval, dream phase, GBrain, JIT Foundry, PandaProbe, OpenHarness, HarnessRouter, promotion | 6 | 2026-09-03 | active |
| [stage0-proof-pack](topics/stage0-proof-pack.md) | S0-01..S0-12, twelve proofs, wave-plan-v2, kill criteria KC-1..KC-7, spikes, four-way classification | 7 | 2026-09-03 | active |
| [decisions-and-premortem](topics/decisions-and-premortem.md) | D-001..D-018, ADR, X-001..X-007, premortem, failure modes, stop-the-line | 5 | 2026-09-03 | active |
| [research-and-seeds](topics/research-and-seeds.md) | findings, council, Ouroboros, interview, seed, breakdown, wave plan, pipeline | 6 | 2026-09-03 | active |
| [infrastructure-and-tooling](topics/infrastructure-and-tooling.md) | setup.sh, hooks, ops scripts, GitNexus, graft, Ouroboros, quartet, push_clean, resume-heal | 12 | 2026-09-03 | active |
| [pc-bridge-and-environment](topics/pc-bridge-and-environment.md) | PC, Fedora, bridge, podman, OmniRoute, vLLM, OpenObserve, Phoenix, sandbox, ephemeral | 6 | 2026-09-03 | active |
| [incident-lessons](topics/incident-lessons.md) | anti-pattern registry, AF-AP-*, bug-echo, operational lessons, delta gate | 5 | 2026-09-03 | active |
| [harness-ports](topics/harness-ports.md) | Codex CLI, Hermes Agent, AGENTS.md, .hermes.md, skill sync, pc-lane, spawn path | 5 | 2026-09-03 | active |

## Concepts

| Concept | Topics Connected | Last Updated |
|---------|------------------|--------------|
| [hollow-green-discipline](concepts/hollow-green-discipline.md) | project-overview, stage0-proof-pack, security-and-containment, research-and-seeds, decisions-and-premortem, incident-lessons | 2026-09-03 |
| [fail-closed-fail-loud](concepts/fail-closed-fail-loud.md) | production-spine, memory-and-governance, security-and-containment, stage0-proof-pack, evaluation-and-improvement, decisions-and-premortem | 2026-09-03 |
| [isolation-by-design](concepts/isolation-by-design.md) | security-and-containment, evaluation-and-improvement, memory-and-governance, production-spine, stage0-proof-pack, pc-bridge-and-environment | 2026-09-03 |

## Also see

- [schema.md](schema.md) -- topic/concept registry, article structure, naming and honesty
  conventions, evolution log.
- [CONTEXT.md](CONTEXT.md) -- navigation guide for agents: coverage tags, when NOT to use the wiki.
- [log.md](log.md) -- compile history.

## Recent Changes

- 2026-09-03: **Initial compile.** 12 topic articles and 3 concept articles written from a
  codebase-mode scan of the repo root (planning docs, tooling, config; no application code).
  Schema, index, context guide, and compile state created. This wiki is compiled from planning
  documents only -- it will need recompilation when the first application code lands.
