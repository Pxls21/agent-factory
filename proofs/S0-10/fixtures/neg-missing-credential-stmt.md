# ADR 0006 — GBrain seam: wrap pinned dream machinery

- Status: accepted
- Date: 2026-09-04

## Context

GBrain is a full knowledge system, not a drop-in ai-memory plugin. The dream phase uses GBrain's architectural patterns to turn accumulated traces and memory into evidence-backed proposals.

Two integration strategies exist: wrap the pinned GBrain dream machinery, or adapt selected MIT-licensed modules.

## Alternatives considered

### Option A: Wrap pinned GBrain dream machinery

Pin a GBrain release, wrap it in a first-party adapter.

### Option B: Adapt selected MIT-licensed modules

Extract individual GBrain modules and integrate them into a custom implementation.

## Decision

Use option A: wrap pinned GBrain dream machinery in a first-party adapter.

The GBrain release is pinned in `upstream.lock.yaml` by immutable commit digest. The adapter translates inputs and outputs.

The dream worker is a proposal-only plane. It cannot apply its own proposals or mutate production memory.

## Consequences

- GBrain's proven dream patterns are available without reimplementation.
- The first-party adapter is small and auditable.
- A proof spike will validate the wrapped integration end-to-end.
