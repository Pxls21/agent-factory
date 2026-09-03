---
topic: memory-and-governance
last_compiled: 2026-09-03
---

# Memory and Governance — four scopes, Fubuki, composite adapter

## 1. Purpose [coverage: high -- 6 sources]

Memory and governance are two separate concerns with a shared boundary. **ai-memory** provides
durable record storage; **Fubuki** provides immutable governance packets (persona, invariants,
bounds). A first-party **composite adapter** maps four logical scopes onto ai-memory's native
`(workspace, project)` model and enforces authorization at the adapter boundary.

Memory is untrusted data, not system instruction. Neither a dream proposal nor a generated
harness can rewrite governance.

**Nothing in this topic has been built.** The component audit and integration contracts define
what will be built; the four-scope adapter proof is S0-06 in the Stage 0 pack.

## 2. Architecture [coverage: high -- 5 sources]

**ai-memory** (MIT, v1.39.0, Rust 1.95, pinned at the `upstream.lock.yaml` commit):
- Native scope is `(workspace, project)` with `_global` as a reserved project
- `/api/v1` is read-only; writes are admin/MCP surfaces
- Container Dockerfile at `docker/Dockerfile`; runtime user `ai-memory`
- Nested environment keys use double underscores
- Auto-improve scheduler and maintenance default on; approval defaults off when configured
  -- the plan starts with scheduler/maintenance OFF, approval ON, and no model-callable
  mutation tools (D-017)

**Fubuki** (Apache-2.0, v0.1.0, Python 3.10+, standard library, pinned at `7375e56`):
- Canonical JSON and packet hashing for immutable governance identity
- `bounds.evaluate_records` returns `BoundDecision` values; join allowed `record_id` to source
  records (no payload field exists)
- `persona_lint` has a known bug: exit code 2 can be retained after a later violation
- Audit: 129 unittest cases passed; one import failed (pytest absent) -- partial evidence

**Composite adapter** (planned first-party):

| Logical scope | ai-memory mapping | Write authority |
|---|---|---|
| Company | `(factory, _global)` | Operator-reviewed promotion only |
| Team | `(factory, team--<team-id>)` | Reviewed project-to-team promotion |
| Project | `(factory, project--<project-id>)` | Authorized project turn/staging |
| Agent | `(factory, agent--<agent-id>)` | Authorized system adapter for that agent |

Recall precedence: Agent --> Project --> Team --> Company for overridable facts; Fubuki/company
invariants marked non-overridable remain authoritative.

Key files: [docs/04_MEMORY_AND_GOVERNANCE.md](docs/04_MEMORY_AND_GOVERNANCE.md),
[docs/03_INTEGRATION_CONTRACTS.md](docs/03_INTEGRATION_CONTRACTS.md) SS4,
[docs/adr/0003-four-logical-memory-scopes.md](docs/adr/0003-four-logical-memory-scopes.md).

## 3. Talks To [coverage: medium -- 4 sources]

- Hermes <--> composite adapter (one MemoryProvider; errors non-fatal)
- Composite adapter <--> ai-memory (auth token, workspace `factory`)
- Fubuki packets --> Hermes context assembly (bounds applied to recalled records)
- Composite adapter <--> policy service (scope tuple validation)
- Dream worker --> sanitized snapshot (read-only) --> proposals (never direct memory write)

## 4. API Surface [coverage: medium -- 3 sources]

Planned adapter contract (from [docs/03_INTEGRATION_CONTRACTS.md](docs/03_INTEGRATION_CONTRACTS.md)):
- Auth tuple validated outside model control on every request
- Deterministic recall precedence (Agent > Project > Team > Company)
- Write only to the authorized active scope
- Visible degradation on recall failure; `memory_required` uses a separate preflight (because
  `pre_llm_call` fails open)
- Cross-scope promotion: a separate reviewed one-level workflow, never native auto-improve

Fubuki: `bounds.evaluate_records(records, bounds)` --> `BoundDecision` per record.
`persona_lint(persona_doc)` --> exit code (known ordering bug).
Canonical `compile_packet()` + `hash_packet()`.

## 5. Data [coverage: medium -- 3 sources]

- ai-memory stores: `AI_MEMORY_DATA_DIR` on the server; workspace `factory` with project-coded
  scopes
- Fubuki: canonical JSON packets, hash-pinned per session; governance hash attached to ACP
  sessions, tool events, recalls, writes, and research artifacts
- Env vars: see [.env.example](.env.example) `FACTORY_MEMORY_*` and `AI_MEMORY_*` sections

## 6. Key Decisions [coverage: high -- 5 sources]

- D-006/ADR 0003: four logical scopes over ai-memory (not native hierarchical RBAC)
- D-007: composite adapter is an authorization boundary (same-workspace tokens are NOT per-project RBAC)
- D-008: normal recall degrades visibly; strict workflows preflight
- D-017: auto-improve scheduler/maintenance OFF; promotion reviewed
- X-006 (open): shared workspace vs separate instances for sensitive tenants
- Council verdict: S0-06 is four-scope adapter design -- auth tuple, precedence, write-target,
  leak fixtures; spike-gated on the Rust build (#3 `map-rust-s006`)

## 7. Gotchas [coverage: high -- 6 sources]

**NOT-built (first-class):**
- No composite adapter, no Fubuki extension, no memory deployment
- No leak fixtures, honeytoken suite, or cross-scope authorization tests
- No governance hash projection into ACP sessions or tool events
- ai-memory build on the PC (Rust 1.95.0 available via rustup) is plausible but unproven
  (spike #3 pending)

**Known issues:**
- Fubuki `persona_lint` exit-code-2 ordering bug -- fix/wrap and add ordered regression
  fixture (S0-07)
- `BoundDecision` has no payload field -- join on `record_id` (misread risk from the v2 plan)
- `pre_llm_call` fails open -- memory-required workflows need a separate preflight, not
  the Hermes hook
- Same-workspace ai-memory tokens are not native per-project RBAC -- the adapter is the
  security boundary

**Premortem risks (#3, #4, #5, #10, #11):** four-scope data leak, memory silently disappearing,
dream worker writing directly, ai-memory learning/deleting without review, Fubuki gate
reporting wrong severity.

## 8. Sources

- [docs/04_MEMORY_AND_GOVERNANCE.md](docs/04_MEMORY_AND_GOVERNANCE.md)
- [docs/02_COMPONENT_AUDIT.md](docs/02_COMPONENT_AUDIT.md)
- [docs/03_INTEGRATION_CONTRACTS.md](docs/03_INTEGRATION_CONTRACTS.md)
- [docs/05_SECURITY.md](docs/05_SECURITY.md)
- [docs/adr/0003-four-logical-memory-scopes.md](docs/adr/0003-four-logical-memory-scopes.md)
- [upstream.lock.yaml](upstream.lock.yaml)
