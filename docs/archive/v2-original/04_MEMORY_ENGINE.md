# 04 — Memory Engine (forked ai-memory) (v2)

**Version:** 2.0 · **Date:** 2026-09-01

The MEMORY plane is a **fork of `akitaonrails/ai-memory`** (MIT, Rust). We do not hand-build memory mechanics — ai-memory already provides markdown-authoritative, git-single-writer storage; FTS5-first authority-aware retrieval; supersession; and a gated auto-improve loop. We fork it to (1) map four scopes, (2) add a provenance overlay, (3) add a gated upward-promotion companion, (4) route models through OmniRoute. All extension happens at the **companion-crate boundary** plus one additive migration; core is touched only where noted.

---

## 1. Scope mapping (Company/Team/Project/Agent → ai-memory)

| Level | ai-memory primitive | How |
|---|---|---|
| **Company** | `_global` scope | union-read into every query; company rules/heuristics/sec-corpus; write-only via dream pipeline + human |
| **Team** | workspace | one per channel (`dev-coding`, `sec-ops`, …); set via `.ai-memory.toml` `workspace=` |
| **Project** | project | repo/cwd-keyed; `.ai-memory.toml` `project=`, `project_strategy="repo-root"` |
| **Agent** | operator/actor scope | per-agent DB-user token + `[auto_scope] mode="per_actor"` + `_slots` (`[slots] per_user=true`) |

Resolution is native via `ScopeResolver` (`resolve_current_or_project(explicit_project, actor) → ResolvedScope::as_tuple`): an agent read returns its project + its operator slots + the `_global` union, with sibling-project/workspace scoping available. This gives the agent→project→team→company read order for free. **No core fork for the read side** — it's config.

Company (`_global`) union read: `[recall] default_global="true"` on a scope makes it read company-wide.

## 2. Provenance overlay (the fork's one additive migration)

Fubuki's `memory-record.schema.json` defines the provenance fields; map them onto ai-memory pages, **adding** the ones ai-memory lacks:

| Fubuki field | ai-memory native | Action |
|---|---|---|
| `status` {proposed, approved, rejected, expired, superseded} | tags (`superseded`/`historical`) + auto-improve pending/approved | **map** proposed/approved onto the pending-writes gate; add `record_status` for the rest |
| `record_type` {fact, decision, preference_signal, event, correction} | `kind` | map to `kind` |
| `provenance_class` {operator_stated, operator_confirmed, observed, imported, inferred} | — | **ADD** `provenance_class` frontmatter + column |
| `confidence` {low, medium, high, confirmed} | — | **ADD** `confidence` |
| `branch` | — | **ADD** `branch` (maps to a Fubuki branch; distinct from workspace) |
| `sensitivity` {normal, sensitive, restricted} | tags/tier | **ADD** `sensitivity` |
| `validity.not_before/not_after` | `expires_at` only | **ADD** `valid_from`/`valid_to` |
| `evidence_pointer` | — | **ADD** `evidence_pointer` |
| `tags` | `tags`/`entities` | reuse |
| `created_at` | `created_at` | map to `recorded_at`; add `occurred_at` |
| supersession | `supersedes`/`is_latest` | reuse (invalidate-don't-delete) |

**Migration mechanics:** frontmatter is additive (new YAML keys ride along; the reindex path preserves them). Only fields you must *query* need a `pages` column via an additive SQLite migration (follow ai-memory's existing additive-migration pattern in `ai-memory-store`); the rest are pass-through YAML. Parser/serializer extension lives in `ai-memory-wiki`; surface in `/api/v1` page responses.

## 3. Retrieval & ranking (native — configure, don't build)

ai-memory fuses FTS5 + entity-match RRF + graph-neighbor RRF + optional vector RRF, then a bounded source-authority adjustment favors `_rules/`/`decisions/`/`procedures/`/`gotchas/` over episodic pages, before truncation. This *is* lexical-before-embeddings (FTS5/entity/graph are candidate generators; vector is optional). **Configuration:** keep vector optional; keep authority adjustment on; retrieved text stays untrusted evidence (never gains instruction authority) — which matches principle #8. Nothing to build here.

## 4. Write path (sanctioned) + invalidate-don't-delete

The only sanctioned wiki mutation is `Wiki::write_page` / `Wiki::apply_batch` (single-writer, git commit; markdown primary, SQLite derived; installed-files-then-index with best-effort rollback). **Never write wiki files directly.** A new fact is a `proposed` record; supersession sets the old page `superseded`/`is_latest=false` + a supersedes link — never a delete. Promotion up a scope is a `Wiki::apply_batch` via the auto-improve approval path (`05`).

## 5. Bounded read for Fubuki

Fubuki does **not** read raw memory. The Fubuki→ai-memory adapter (`08` Adapter B) issues a scoped `/api/v1` query, maps each page to a Fubuki `MemoryRecord`, and runs `memory/bounds.py` (the 7-filter default-deny engine — `06`) before the allowed set becomes the packet's `bounded_context`. So ai-memory is the store; Fubuki's bounds engine is the gate.

## 6. Provider config → OmniRoute (from source)

```
AI_MEMORY_LLM_PROVIDER=openai-compat
AI_MEMORY_LLM_BASE_URL=http://host.docker.internal:20128/v1
AI_MEMORY_LLM_MODEL=<non-reasoning model>          # strict-JSON consolidation needs non-reasoning
LLM_API_KEY=<gateway key or any>
AI_MEMORY_EMBEDDING_PROVIDER=openai-compat
AI_MEMORY_EMBEDDING_BASE_URL=http://host.docker.internal:20128/v1
AI_MEMORY_EMBEDDING_MODEL=<model>
AI_MEMORY_EMBEDDING_DIM=<dim>                        # change of {provider,model,dim} ⇒ ai-memory embed --force
AI_MEMORY_AUTH_TOKEN=<bearer>                        # or DB-users + token_pepper
```
Both LLM and embeddings egress through OmniRoute; zero code change. Zero-LLM mode (FTS5 + entities + graph + rule summaries) works with no provider — use it to prove lexical-first first.

## 7. The fork boundary (what we change vs reuse)

- **Reuse as-is:** storage, retrieval fusion, supersession, `/api/v1`, MCP/CLI, auth ladder, auto-improve scheduler + eval-gate + `require_approval`, curator, handoff.
- **Add (companion crate, calls HTTP/MCP — like `companions/ai-memory-importer`):** the four-level promotion policy + identifier-strip + `persona_lint` provenance check (the dream-phase distiller, `05`), and the Fubuki bounded-read client (`08`).
- **Add (core, additive migration):** the provenance-overlay columns (§2).
- **Possible core change (only if needed):** if the auto-improve approval path won't accept an external executable scorer as a hard pre-write gate, add that hook at the pending-writes→approval transition in `ai-memory-consolidate`. Try the `[auto_improve.eval] command=…` path first — it is exactly this.

## 8. Hybrid tiering (isolation)

Default: one shared ai-memory store; per-agent isolation via operator token + `per_actor` auto-scope (context-injection isolation, not RBAC). Because ai-memory is single-tenant with no per-page RBAC, **sensitive agents (#sec-ops) run a dedicated ai-memory instance inside their gVisor sandbox** holding Agent+Project, federating to the hub for Team+Company via the same `/api/v1` client. Decision recorded as D7 (`06`).

## 9. Attribution
`NOTICE`: ai-memory (MIT, akitaonrails). If any Letta/mem0/Graphiti code is later lifted, add their Apache-2.0 notices; as of v2 they are reference-only (ai-memory supersedes that hand-built layer).

Cross-refs: the dream phase that drives promotion → `05`; Fubuki bounds engine + seams → `06`; the adapters → `08`.
