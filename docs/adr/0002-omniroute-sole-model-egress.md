# ADR 0002 — OmniRoute is the sole model API egress

- Status: accepted
- Date: 2026-09-02
- Amended: 2026-09-08 (the Hermes transport — owner decision, task #35)

## Context

Direct model providers in Hermes, ai-memory, or evaluators would scatter credentials and make routing, cost, logging, and failover policy hard to prove.

## Decision

All model and embedding traffic uses internal, scoped OmniRoute credentials and tested routes. Provider credentials exist only in OmniRoute. Hermes talks to the internal `/v1` endpoint over `chat_completions` — the transport the owner's repaired live profiles run (the Codex
handoff of 2026-09-05 recorded no failure of the other mode; it chose this one) — with `codex_responses` PERMITTED per route for
Codex-capable models that need the Responses API. Either mode sends the compression-off header (a per-provider `extra_headers`
entry the pinned Hermes supports in both modes), and every proof asserts and records the wire mode it observes rather than assuming one.

## Consequences

OmniRoute is a critical dependency and must be persistent, monitored, and load-tested. Direct fallback is prohibited. Tool/web egress is a different boundary and still needs its own proxy and policy.
