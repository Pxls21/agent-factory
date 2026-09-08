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

## Note (2026-09-08, lane M1 — read from the pinned ai-memory source 73715b6f)

`(factory, _global)` is NOT ai-memory's reserved global scope. The reserved scope is resolved only inside the default workspace (`lookup_global_scope` → `DEFAULT_WORKSPACE_NAME` + `GLOBAL_SCOPE_PROJECT`, `crates/ai-memory-store/src/scope.rs:254-292`; `DEFAULT_WORKSPACE_NAME = "default"`, `crates/ai-memory-core/src/lib.rs:28`). In the `factory` workspace, `_global` is an ordinary project: the MCP `scope: "global"` argument cannot address it, the default `memory_query` union does not include it, and nothing refuses to create it. The S0-06 adapter therefore addresses Company explicitly as `workspace=factory&project=_global` on both the read and the write surface. A second accepted ADR with this number (`0003-two-durable-memory-scopes.md`) conflicts with this one; which is live is an open owner decision (task `adr-0003-conflict`).
