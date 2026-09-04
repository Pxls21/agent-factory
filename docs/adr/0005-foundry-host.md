# ADR 0005 — Foundry host: first-party minimal translator

- Status: accepted
- Date: 2026-09-04

## Context

The JIT Harness Foundry generates five source files per candidate:

- `memory.py`
- `planning.py`
- `action.py`
- `tool_policy.py`
- `prompt.yaml`

These files need a host to load, normalize, and execute them inside the evaluation sandbox. The host is the runtime that turns JIT output into a runnable candidate for AlphaEval comparison against the Hermes baseline.

Three hosting options exist, each with different complexity, trust surface, and maintenance cost. The decision affects the containment profile and the promotion path for approved candidates.

## Alternatives considered

### Option A: First-party minimal host

A small translator written and owned by the project. It loads the five JIT files, wraps them in a HarnessSpec manifest, and exposes the candidate through the evaluation sandbox interface. No external framework. The host code is auditable in full and shares no dependency tree with the candidate it runs.

Tradeoff: must implement tool dispatch and memory/planning orchestration from scratch, but the surface is small (the five files have a fixed shape) and the host never needs to track an external project's releases.

### Option B: OpenHarness interface extraction

Extract a limited subset of interface patterns from OpenHarness — enough to load the five JIT files and dispatch tool calls. Discard the rest.

Tradeoff: inherits OpenHarness's interface contracts without its test suite or maintenance. The extracted subset drifts from upstream on each OpenHarness release, creating a fork maintenance burden for a surface area that option A covers with less code.

### Option C: Pinned, hardened OpenHarness derivative

Pin a full OpenHarness release, harden it (strip unnecessary capabilities, lock network/filesystem access, add containment shims), and use it as the candidate host.

Tradeoff: brings the full OpenHarness dependency tree into the trust surface. Hardening a general-purpose framework is more work than building a minimal host for a fixed five-file shape. Every upstream update requires a re-hardening pass. OpenHarness is a full standalone harness, not a minimal skeleton — deploying it merely because it is listed as a Foundry component violates the smallest-option principle.

## Decision

Use option A: a first-party minimal host that loads the five JIT output files (`memory.py`, `planning.py`, `action.py`, `tool_policy.py`, `prompt.yaml`), wraps them in a HarnessSpec manifest with digest locks, and exposes the candidate through the evaluation sandbox.

The host is purpose-built for the known JIT output shape. It does not import or depend on OpenHarness. Generated `tool_policy.py` can reduce candidate behavior but cannot override the external Agent Factory policy service. The candidate runs only in the isolated evaluation sandbox — never with production credentials, memory tokens, or host networking.

An approved candidate's normal promotion path is translation into a versioned Hermes plugin or profile (per ADR 0001). A standalone harness or HarnessRouter activation requires a separate ADR (per standing rule 6).

## Consequences

- The Foundry host is a small, fully auditable codebase with no external framework dependency.
- JIT output shape changes require host updates, but the five-file contract is pinned by the generator and changes are versioned.
- OpenHarness remains available as reference material but is not a runtime dependency.
- The promotion path stays through Hermes plugin/profile translation, preserving the single-runtime guarantee.
- Containment is simpler: the host shares no code with the candidate it runs and has no capabilities beyond loading the five files and dispatching through the policy gate.
