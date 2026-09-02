# ADR 0002 — OmniRoute is the sole model API egress

- Status: accepted
- Date: 2026-09-02

## Context

Direct model providers in Hermes, ai-memory, or evaluators would scatter credentials and make routing, cost, logging, and failover policy hard to prove.

## Decision

All model and embedding traffic uses internal, scoped OmniRoute credentials and tested routes. Provider credentials exist only in OmniRoute. Hermes uses `codex_responses` against the internal `/v1` endpoint and sends the compression-off header.

## Consequences

OmniRoute is a critical dependency and must be persistent, monitored, and load-tested. Direct fallback is prohibited. Tool/web egress is a different boundary and still needs its own proxy and policy.
