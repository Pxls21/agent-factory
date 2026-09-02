# ADR 0003 — Four logical memory scopes over ai-memory

- Status: accepted
- Date: 2026-09-02

## Context

Agent Factory requires Company, Team, Project, and Agent memory. ai-memory natively scopes records by `(workspace, project)` and reserves `_global`; per-user slots are injection constraints, not page-level RBAC. Dropping Team and Agent would discard intended behavior, while presenting path conventions as native isolation would be inaccurate.

## Decision

Retain all four logical scopes behind one first-party composite Hermes provider:

- Company: `(factory, _global)`
- Team: `(factory, team--<team-id>)`
- Project: `(factory, project--<project-id>)`
- Agent: `(factory, agent--<agent-id>)`

The adapter authenticates the actor/agent/team/project binding, reads with Agent→Project→Team→Company precedence, applies Fubuki bounds, and writes only to the authorized active scope. Promotion is a separate reviewed one-level workflow.

## Consequences

The four-level goal survives, but the adapter becomes a security-critical authorization boundary with extensive leak tests. Same-workspace tokens are not treated as per-project RBAC; sensitive tenants may require separate instances/workspaces.
