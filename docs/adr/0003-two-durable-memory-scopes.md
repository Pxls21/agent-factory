# ADR 0003 — Two durable memory scopes in v1

- Status: SUPERSEDED by `0003-four-logical-memory-scopes.md` (owner decision 2026-09-08, the S0-06 rounds' D-2: the seed, the docs and
  the built adapter bind the four-scope decision; this text is the same question answered more narrowly, not a layer beneath it — the
  four-scope ADR already maps every logical scope onto a durable `(workspace, project)` pair; kept as the rejected alternative)
- Date: 2026-09-02

## Context

The original Agent→Project→Team→Company hierarchy was mapped onto ai-memory as if those were native security scopes. Current ai-memory is fundamentally scoped by workspace and project; per-user slots affect injection but are not page RBAC.

## Decision

Use the active project plus the reserved global project as project and company memory. Hermes owns session/local state. Team and durable per-agent scopes are deferred. Company promotion is an explicit operator workflow.

## Consequences

The provider and authorization model remain understandable and testable. Some desired hierarchy is postponed, but no path-name convention is misrepresented as isolation.
