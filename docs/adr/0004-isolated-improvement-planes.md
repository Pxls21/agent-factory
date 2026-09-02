# ADR 0004 — Isolate dream and Harness Foundry planes

- Status: accepted
- Date: 2026-09-02

## Context

GBrain-informed dream cycles and JIT-generated harnesses can improve memory and agent behavior, but both process untrusted/model-generated material. Direct production credentials or self-deployment would collapse the boundary between proposing and authorizing a change.

## Decision

Retain both capabilities as ephemeral gVisor-contained planes that read immutable sanitized inputs and write proposal/candidate artifacts only. System validators, deterministic/AlphaEval tests, and humans control promotion. Generated harnesses normally target Hermes plugins/profiles; conditional HarnessRouter requires a separate ADR for an approved UHP-only harness.

## Consequences

The original learning and Foundry goals remain, with additional artifact schemas, lineage, sandboxing, and review infrastructure. Improvement is slower than auto-deployment but reversible and auditable.
