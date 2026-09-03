# Wiki Schema

This file defines the structure and conventions for this knowledge base wiki. It is generated on
first compile and co-evolved between human and LLM on subsequent runs.

**Human:** You can edit this file to rename topics, merge them, add conventions, or change the
article structure. The compiler will respect your changes on the next run.

**Compiler:** Read this file before classifying sources. Follow its conventions. Add new topics
here when discovered. Never remove topics without human approval.

Mode: `codebase` (per `.wiki-compiler.json`). Scan root is the repo root with
`wiki/`, `.gitnexus/`, `graft/`, `.claude/`, `.agents/`, `sandbox-kit/`, `docs/archive/`,
`node_modules/`, `dist/`, `.git/`, `vendor/`, `__pycache__/`, `.build/`, `target/`, `coverage/`
excluded.

## Topics

- `project-overview`: what the system is, planning-stage status, the build spine, the six-stage gate pipeline, dormant seams and NOT-built first-class.
- `production-spine`: the live interaction path (Buzz --> buzz-acp --> Hermes --> OmniRoute), component pins, integration contracts, acceptance tests.
- `memory-and-governance`: four logical memory scopes over ai-memory, Fubuki governance packets, the composite adapter as authorization boundary.
- `security-and-containment`: policy gate, gVisor, egress enforcement, threat model, stop-the-line conditions.
- `evaluation-and-improvement`: AlphaEval, GBrain dream phase, JIT Harness Foundry, PandaProbe, OpenHarness, HarnessRouter -- all retained as isolated proposal/candidate planes.
- `stage0-proof-pack`: twelve proofs, four-way classification, wave-plan-v2, kill criteria, 18 increments, spike results.
- `decisions-and-premortem`: the reasoning record -- 18 accepted decisions, 7 open choices, 5 owner inputs, 20-item ranked premortem.
- `research-and-seeds`: how a subsystem is designed before code -- findings, council, Ouroboros interview, seed, task breakdown.
- `infrastructure-and-tooling`: ephemeral container provisioning, hooks, ops scripts, code-intelligence quartet, vendored kit.
- `pc-bridge-and-environment`: the owner's PC as execution host, bridge protocol, probed facts, observability sinks.
- `incident-lessons`: anti-pattern registry (AF-AP-*), operational lessons, the /bug-echo loop.
- `harness-ports`: Codex CLI and Hermes Agent environment ports, skill sync, PC-side spawn path.

## Concepts

Cross-cutting patterns that span 3+ topics. Interpretive, not just factual.

- `hollow-green-discipline`: never mint a green the claimed mechanism did not produce; the refusal is the product -- connects [project-overview, stage0-proof-pack, security-and-containment, research-and-seeds, decisions-and-premortem, incident-lessons]
- `fail-closed-fail-loud`: ambiguity resolves to REJECT, failures carry reasons, silent paths are defects -- connects [production-spine, memory-and-governance, security-and-containment, stage0-proof-pack, evaluation-and-improvement, decisions-and-premortem]
- `isolation-by-design`: untrusted planes cannot reach production authority; structural isolation over runtime checks -- connects [security-and-containment, evaluation-and-improvement, memory-and-governance, production-spine, stage0-proof-pack, pc-bridge-and-environment]

## Article Structure

Codebase-mode articles follow the section set declared in `.wiki-compiler.json`:

- **Purpose** [coverage] -- what the module/subsystem does and who depends on it (required)
- **Architecture** [coverage] -- key files, structure, entry points, with `file:line` anchors
- **Talks To** [coverage] -- dependencies, seams, inter-module calls
- **API Surface** [coverage] -- exported functions/classes, config knobs, event kinds
- **Data** [coverage] -- stores, artifacts, persisted state, telemetry streams owned
- **Key Decisions** [coverage] -- seed refs, owner rulings, council verdicts, rejected alternatives
- **Gotchas** [coverage] -- known issues, DORMANT/NOT-built seams stated first-class, failure modes, incident-log entries
- **Sources** -- backlinks to every contributing file (required)

Concept articles use: **Pattern** / **Instances** (dated, linking `../topics/<slug>.md`) /
**What This Means** / **Sources**.

## Naming and Honesty Conventions

- Topic slugs: lowercase-kebab-case, stable identifiers. Renaming breaks inbound links.
- NOT-built capabilities stated FIRST-CLASS in every Gotchas section.
- Build status defers to `todo/BUILD-TASKLIST.md` (the SSoT) -- never override its counts.
- Stage 0 denominators are four-way (execution / conformance-checked decision /
  blocked-on-external-input / blocked-on-capability) -- never a flat "N/12."
- Coverage tags are honest: low means "read the raw file." Hedges mean exactly what they say.

## Evolution Log

- 2026-09-03: Initial schema generated from 12 topics, 3 concepts (first compile, codebase mode, planning docs only -- no application code).
