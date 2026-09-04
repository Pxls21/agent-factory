# ADR 0006 — GBrain seam: wrap pinned dream machinery

- Status: accepted
- Date: 2026-09-04

## Context

GBrain is a full knowledge system, not a drop-in ai-memory plugin. The dream phase uses GBrain's architectural patterns — triage, constrained parallel analysis, quote verification, provenance, orchestrator validation, and reverse writing — to turn accumulated traces and memory into evidence-backed proposals.

Two integration strategies exist: wrap the pinned GBrain dream machinery in a first-party adapter, or adapt selected MIT-licensed modules into a custom implementation. Both strategies must preserve the credential-isolation and proposal-only invariants specified in ADR 0004.

## Alternatives considered

### Option A: Wrap pinned GBrain dream machinery

Pin a GBrain release, wrap it in a first-party adapter that mediates between Agent Factory's snapshot format and GBrain's input contract. The wrapper translates inputs and outputs but does not modify GBrain's internal logic. Updates arrive as version bumps of the pinned release.

Tradeoff: depends on GBrain's release cadence and internal design. But the GBrain patterns (triage, parallel analysis, provenance, quote verification) are mature and tested in their original context. Wrapping preserves those guarantees without reimplementation risk.

### Option B: Adapt selected MIT-licensed modules

Extract individual GBrain modules (triage, analysis, verification) and integrate them into a custom dream-phase implementation. Discard GBrain's orchestrator and replace it with a first-party one.

Tradeoff: maximum control but reimplements orchestration logic that GBrain already solves. The extracted modules drift from upstream, creating a fork maintenance burden. Each GBrain update requires manual assessment of which extracts to refresh.

## Decision

Use option A: wrap pinned GBrain dream machinery in a first-party adapter. The adapter is a translation layer, not a reimplementation.

The GBrain release is pinned in `upstream.lock.yaml` by immutable commit digest. The adapter's boundaries are:

- Input: receives an immutable, sanitized snapshot with record/trace IDs and governance hash.
- Output: produces proposal bundles in Agent Factory's schema.
- Authority: the dream worker and its subagents receive no ai-memory admin credentials, no production tool access, no governance-write authority, and no Buzz keys. The worker operates in an ephemeral gVisor container with read-only access to the snapshot and write access only to scratch analysis and the proposal artifact sink.

The dream worker is a proposal-only plane. It cannot apply its own proposals, mutate production memory, or bypass the human promotion gate. Worker failure produces no production mutation.

## Consequences

- GBrain's proven dream patterns are available without reimplementation.
- The first-party adapter is small and auditable — it translates formats, not logic.
- Credential isolation is enforced by containment, not by GBrain's own access controls: the worker's gVisor sandbox has no route to ai-memory admin, Buzz, policy mutation, production workspace, or direct provider credentials.
- A proof spike (deferred to a later stage) will validate the wrapped integration end-to-end with deterministic fixtures before any production use.
- Switching from wrap to adapt remains possible if the proof spike reveals an incompatibility.
