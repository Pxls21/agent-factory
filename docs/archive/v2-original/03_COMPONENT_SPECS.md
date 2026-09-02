# 03 — Component Specifications (v2)

**Version:** 2.0 · **Date:** 2026-09-01
Confidence: **[H]** read-the-source · **[M]** doc/secondary · **[V]** verify.

---

## 1. Buzz (Interface) [H]
- NIP-29 Nostr over WebSocket; relay `ws://localhost:3000`. Channel scoping via `#h` tags. Auth = NIP-42 (kind 22242).
- Stack: `buzz-relay` + `buzz-core` (`kind.rs` = the `ALL_KINDS` registry, 127 kinds; kinds declared `pub const KIND_*: u32 = 4XXXX`) + `buzz-db` (Postgres) + `buzz-pubsub` (Redis) + `buzz-search` (FTS/NIP-50) + `buzz-audit` (SHA-256 hash-chain) + `buzz-media` (Blossom/MinIO) + `buzz-workflow` (YAML).
- Kinds: 9 chat (**needs `#h`**), 7 reaction, 5 deletion, 0 profile, 22242 AUTH, 39000/39001/39002 channel metadata/membership, 9007 create-group + admin kinds. Do not depend on deferred kinds.
- **Owner binding = NIP-OA (Nostr Owner Attestation)** — an owner signs a narrowly scoped authorization; the agent signs its own work; authorship never transfers; revoking the agent doesn't touch the human identity. (Not vanilla NIP-26.)
- git → threads: `git-sign-nostr`/`git-credential-nostr` sign pushes; git events land as signed events.

### buzz-acp [H]
`Buzz relay ─WS→ buzz-acp ─stdio→ harness`. Spawns the harness as an ACP subprocess; listens for kind-9 with the agent's pubkey in `#p`; NIP-42 on connect; **one in-flight prompt per channel** (batched). Env: `BUZZ_PRIVATE_KEY` (required, nsec), `BUZZ_RELAY_URL` (`ws://localhost:3000`), `BUZZ_ACP_AGENT_COMMAND` (set `hermes`/`claude-code`/`codex`/`pi`), `BUZZ_ACP_AGENT_ARGS` (`acp`). Flags: `--respond-to owner-only|allowlist|anyone|nobody`, `--idle-timeout 900`, `--max-turn-duration 7200`, `--dedup-mode Drop|Queue`.

## 2. ACP [H]
JSON-RPC 2.0 over stdio: `initialize`, `session/new` (declares `mcpServers`), `session/prompt`, `session/update` (stream), `session/cancel`, `session/request_permission` (Allow*/Deny), `fs/*`, `terminal/*`. Local stdio only (remote transport still in dev).

## 3. Fubuki OS (Governance) [H — read from source]
- Repo `NerdHerderDani/fubuki-os`, Apache-2.0, Python 3.10+ stdlib-only, v0.1.0, author Dani Schlarmann. Entry `fubuki = fubuki_os.cli:main`. Layout: `compiler/`, `release/` (hashing, registry), `state/`, `memory/` (bounds, store, models, records, preferences, permissions), `package/` (loader, manifest, validator), `audit/`, `adapters/` (base, claude, chatgpt), `lint/persona_lint.py`, `schemas/` (7 frozen), `migrations/` (2), `personas/example-ledger/`.
- **CLI:** `python3 -m fubuki_os doctor` · `package inspect <pkg>` · `--json compile examples/compile-request.json --package <pkg>`.
- **Canonicalization (`release/hashing.py`):** `json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False)`; **floats forbidden**; `hash_obj = "sha256:"+sha256(canonical_bytes)`; `hash_file = "sha256:"+sha256(raw bytes)`; `normalize_text` CRLF→LF.
- **Packet (`compiler/compiler.py` + `schemas/compiled-packet.schema.json`, id `fubuki-compiled-packet/0.1`):** required keys `packet_schema, package_id, core_hash, package_hash, adapter, adapter_notes, mode, register, state, resident_kernel, mode_manifest, bounded_context, selected_examples, output_contract, hard_constraints, memory_cutoff, source_pointers, packet_hash`; optional `compiled_at` (only if `time_override`). `packet_hash = "sha256:"+sha256(canonical_bytes(packet without packet_hash))`. **No wall-clock in the packet.** `adapter_notes` carry `placement=system` ("host may inject its own scaffold; persona packet layered beneath it").
- **Manifest (`schemas/persona-package.schema.json`, id `fubuki-persona-package/0.1`):** required `package_schema, persona_id, persona_version, core_hash, files[]`; file `role ∈ {constitution,doctrine,mode,examples,knowledge,schema,evaluation,adapter,asset}`, `load_condition ∈ {always,on_demand,never}`.
- **Adapters never call a model** — they resolve placement/token-budget metadata only. This is the "null adapter" property in practice.
- Full seam design (compile → hash-pin; the governance-vs-memory split) → `06`.

## 4. ai-memory (MEMORY, forked) [H — read from source]
- Repo `akitaonrails/ai-memory`, MIT, Rust, ~8-crate workspace. Single binary; server `:49374`; data dir `<data>/{wiki,raw,db,models,logs}`. Docker `akitaonrails/ai-memory` (multi-arch). Markdown-authoritative git wiki + derived SQLite (WAL), single-writer actor.
- **Crates:** `ai-memory-core` (types), `ai-memory-store` (SQLite + writer + reader pool + **`ScopeResolver`**/`ActorContext`), `ai-memory-wiki` (`Wiki::write_page`/`apply_batch` — only sanctioned writes; `extract_links`), `ai-memory-mcp`, `ai-memory-hooks` (sanitiser + `/hook`), `ai-memory-llm` (`LlmProvider`/`Embedder`), `ai-memory-consolidate` (auto-improve/curator), `ai-memory-cli`.
- **Scopes:** `_global` (company preferences, union-read), workspace, project (cwd/git-root; `.ai-memory.toml` overrides `workspace`/`project`/`project_strategy`), per-operator `_slots`. `[auto_scope] mode = single|per_session|per_actor`. Full mapping → `04`.
- **Retrieval:** FTS5 + entity-match RRF + graph-neighbor RRF + optional vector RRF; bounded source-authority adjustment before truncation; retrieved text never gains instruction authority. Lexical-first.
- **Frontmatter:** `title, entities (≤10), pinned, expires_at, tier (working/episodic/semantic/procedural), kind (decision/gotcha/rule/fact/…), tags (canonical/active/source-of-truth/superseded/historical/test-fixture/do-not-answer-from), supersedes/is_latest, salience`.
- **Auto-improve (`ai-memory-consolidate`):** scheduler reviews finished sessions → **pending-writes** proposals → `approve_auto_improve_proposal` (sanctioned promotion write). Gates: `[auto_improve] require_approval=true` (human), `[auto_improve.eval] enabled=true command="…" targets=["_rules","procedures"] min_delta=…` (executable scorer), `[auto_improve.scheduler] interval_secs/max_sessions_per_tick/min_session_age_secs`. Rule-based `curator` (report-only unless `--stage`). Invariants: never bypass `ScopeResolver`, never write wiki directly, never auto-delete semantic pages.
- **`/api/v1` (read-only):** `/workspaces`, `/projects`, `.../pages`, `.../pages/{path}`, `.../recent`, `.../briefing`, `.../overview`, `.../handoffs`, `GET/POST /search`. Bearer + host-allowlist.
- **Providers → OmniRoute:** `AI_MEMORY_LLM_PROVIDER=openai-compat`, `AI_MEMORY_LLM_BASE_URL=http://…:20128/v1`, `AI_MEMORY_LLM_MODEL`, `LLM_API_KEY`; `AI_MEMORY_EMBEDDING_PROVIDER=openai-compat`, `AI_MEMORY_EMBEDDING_BASE_URL`, `AI_MEMORY_EMBEDDING_MODEL`, `AI_MEMORY_EMBEDDING_DIM`; `AI_MEMORY_LLM_COMPAT_STRICT` (json_schema), `AI_MEMORY_RERANKER=llm`. Auth: loopback / `AI_MEMORY_AUTH_TOKEN` / DB-users (`token_pepper`, first user flips `/admin/*` root-only) / SSO (`actor_proxy_bearer_token` + `X-Memory-Actor-*`). **Single-tenant, no per-page RBAC** → sensitive isolation = dedicated instance.

## 5. OmniRoute (Routing, sole egress) [M]
- `localhost:20128/v1` + `/v1/responses`; MCP at `/api/mcp/stream`. **Preservation engine** protects code/URLs/JSON; compression is per-combo toggleable → **code lane = no engines** (Caveman/RTK off). 4-tier fallback + circuit breakers. Set `INITIAL_PASSWORD` (default `CHANGEME`); `JWT_SECRET`, `API_KEY_SECRET`, `DATA_DIR`, `PORT`. **Add a byte-echo canary on the code lane regardless (`08`).**

## 6. Hermes (Execution/Safety) [H/M]
- `~/.hermes/config.yaml` (behavior) + `.env` (secrets). Hooks: `pre_tool_call` (**blocks, fail-closed, structured JSON**), `post_tool_call`, `pre_llm_call`, `post_llm_call`, `on_session_start/end`, `pre_gateway_dispatch`; per-hook context capped 10k chars. Transports include ChatCompletions/Responses → set base_url to OmniRoute. `hermes acp` launcher. **License [V]** — don't image until confirmed. Buzz-managed runtime auto-approves permissions → forbid for privileged agents.

## 7. Pi (Execution) [H]
- `earendil-works/pi` — **no native ACP** (community `pi-acp` spawns `pi --mode rpc`; limits: no FS/terminal delegation, no MCP passthrough, no `request_permission`). **No built-in permission system** → **must run in gVisor.**

## 8. HarnessRouter (Phase 2) [M]
- `POST /api/harness/v1/responses` (UHP = OpenAI-Responses). UI `:3100` (remap from 3000), Gateway `:8080`, Runner `:8081`. `HR_AUTH_PASSWORD`, `HR_SECRET_KEY`, pin ≥0.3.0. Only for a UHP-only harness (`11`).

## 9. PandaProbe (Observability) [M]
- SDK decorators/wrappers; CHAIN→AGENT→LLM→TOOL. **Auto-initializes from env** → to keep off, don't set its env or set `PANDAPROBE_ENABLED=false`. Judge via LiteLLM → OmniRoute. Local `:8000`.

## 10. #sec-ops toolchain → `07`. Codemods (ast-grep/comby) → `08`.
