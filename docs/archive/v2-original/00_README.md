# Agent Factory — Build Specification (v2)

**Version:** 2.0 · **Date:** 2026-09-01 · **Status:** buildable. All prior open unknowns are resolved from source except a handful of small verifications (see `06`/`09`).

> v2 changes vs v1: the MEMORY plane is now a **fork of `akitaonrails/ai-memory`** (read from source), not a from-scratch build; the **dream phase** (propose→dispose distillation) is its own doc; **Fubuki's Seams A and B are locked** against the real code (canonical-JSON hash, the governance-vs-memory table split, the bounds engine, `persona_lint`); **HarnessRouter is Phase 2** (all four harnesses are ACP-drivable). Everything here is grounded in files that were actually read.

---

## 0. What this is

The complete, self-contained specification for a self-hosted, multi-agent "agent factory": one machine that turns channels into a fleet of governed, memory-equipped AI coding/research agents under cryptographic identity, deterministic governance, and hard containment. **A coding agent should be able to build the whole system from these documents alone.**

## 1. Reading order

| # | Document | Purpose |
|---|---|---|
| 00 | `00_README.md` | Principles, glossary, build order, licensing |
| 01 | `01_ARCHITECTURE.md` | Seven planes, component inventory, decisions log, the four-doors taxonomy |
| 02 | `02_DATAFLOW_AND_TOPOLOGY.md` | Request lifecycle, the brain hierarchy as ai-memory scopes, fault topology |
| 03 | `03_COMPONENT_SPECS.md` | Per-component surface: endpoints, event kinds, env, auth, ports |
| 04 | `04_MEMORY_ENGINE.md` | Forked ai-memory: scopes, provenance overlay, retrieval, write path, `/api/v1`, config |
| 05 | `05_DREAM_PHASE.md` | Propose→dispose distillation, two tiers, the nightly curator agent |
| 06 | `06_GOVERNANCE_AND_FUBUKI_SEAMS.md` | Fubuki compile/hash (Seam A), the continuity split (Seam B), bounds engine, `persona_lint`, the build-discipline gates, open decisions |
| 07 | `07_SECURITY_AND_CONTAINMENT.md` | #sec-ops: CEL gate, gVisor, secrets, hybrid-tier isolation |
| 08 | `08_ADAPTERS_AND_SEAMS.md` | The glue to build, with interface sketches |
| 09 | `09_BUILD_PLAN.md` | Repo layout, ports, compose, staged rollout with benchmarks |
| 10 | `10_PRE_MORTEM.md` | Ranked failure modes + a living skeleton |
| 11 | `11_HARNESS_FOUNDRY.md` | **Phase 2** — the Genesis Team + on-the-fly harness synthesis (Door 4) |

Docs `00`–`10` are the **v1 system** (build first, in the order of `09_BUILD_PLAN.md`). Doc `11` is **Phase 2**.

## 2. The system in one paragraph

Humans and agents meet in **Buzz** (a self-hosted Nostr workspace) in channels like `#dev-coding`, `#sec-ops`, `#agent-forge`. Each agent is a Nostr keypair bound to its human owner by **NIP-OA** attestation. When a task is posted, `buzz-acp` drives the assigned harness (Hermes / Claude Code / Codex / Pi — all ACP-drivable) directly over **ACP**. Before the model runs, **Fubuki OS** compiles that agent's persona + a bounded memory slice into a byte-identical, hash-stamped **canonical-JSON packet** (the brain), placed as the system layer and hash-pinned at every model call. Memory lives in a **forked `ai-memory`** engine — one git-versioned markdown store, FTS5-first retrieval, arranged into four scopes (Company/Team/Project/Agent). Lessons move up only through a **deterministic propose→dispose pipeline** (the dream phase). Every tool call passes a first-party **CEL gate** and runs inside **gVisor**. Every model call exits only through **OmniRoute** (`localhost:20128`). **PandaProbe** can trace it all, off by default.

## 3. Non-negotiable principles

1. **BRAIN vs HANDS.** Fubuki (deterministic; compiles context; never calls a model — its adapters only emit placement metadata) is strictly separate from the harness (runs the model, edits files, runs shell).
2. **Markdown is authoritative.** All state of record is git-versioned markdown; SQLite/vector indexes are rebuildable derivatives. ai-memory enforces this natively (single-writer actor over a git wiki).
3. **Lexical before embeddings.** Retrieval generates candidates from FTS5 + entities + graph; embeddings only re-rank. (ai-memory is FTS5-first by design.)
4. **Invalidate, never delete.** A superseded fact gets `status: superseded`/`valid_to`/a supersedes link; history is preserved.
5. **Nothing third-party in the deterministic verification-gate spine.** Memory/observability/harness libraries live in their planes; the gate that decides "did this pass" is first-party (Fubuki `persona_lint`, the CEL gate, the retro gate).
6. **No hollow greens.** A gate never reports a pass it didn't verify; "verified" is banned without a backing command+output; roles can't grade their own work.
7. **Default-deny containment.** Every tool/shell action is checked (deny-before-allow; missing/broken policy refuses) and sandboxed. Fail closed.
8. **Provenance travels with every claim.** Every fact carries what it is (`provenance_class`) and its status; a claim can't become authority until verified. Memory enters as `proposed`; only the deterministic pipeline (or a human) promotes it — the write path cannot self-approve.
9. **Continuity authority order:** git-origin > KB wiki > task ledger.
10. **Audited before installed.** Dev-plane tools are read before entry; agent CLIs are pinned + checksummed.

## 4. Glossary

- **Plane** — a horizontal layer (interface, governance, memory, routing, execution, safety, observability).
- **Brain** — an agent's compiled persona + bounded memory slice (Fubuki packet); loosely, its ai-memory scope.
- **Scope** — one memory level: Company (`_global`) / Team (workspace) / Project (project) / Agent (operator).
- **Dream phase** — the propose→dispose distillation cycle (`05`).
- **Seam** — a boundary where glue must be written (`08`).
- **Retro gate** — the post-output verification (independent oracle + de-vacuoused negative control).
- **Genesis Team** — the foundational agents that build other agents (`11`).

## 5. Licensing

Buzz (Apache-2.0), Fubuki OS (Apache-2.0), OmniRoute (MIT), ai-memory (MIT), PandaProbe (Apache-2.0 platform / MIT SDK), HarnessRouter (Apache-2.0). Ship a `NOTICE` crediting the ai-memory fork (MIT, akitaonrails) and Fubuki (Apache-2.0, Dani Schlarmann). Hermes' license is unconfirmed — do not redistribute it in an image until verified. GBrain/Gorgias are pattern-only (no code copied).
