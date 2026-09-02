# 01 — Architecture (v2)

**Version:** 2.0 · **Date:** 2026-09-01

## 1. The seven planes

```
┌────────────────────────────────────────────────────────────────────────────┐
│ INTERFACE   Buzz relay (ws://localhost:3000, NIP-42/kind 22242, NIP-OA owner)│
│   #dev-coding  #stem-engineering  #osint-intel  #sec-ops  #agent-forge       │
└───────────────┬───────────────────────────────────────────────┬─────────────┘
                │ kind 9 @mention (#h channel, #p agent)          │ read/write
                ▼                                                 ▼
┌──────────────────────────┐                        ┌────────────────────────────┐
│ buzz-acp bridge          │                        │ MEMORY  forked ai-memory    │
│ WS→stdio ACP, 1/channel  │                        │ (:49374, git+SQLite,        │
│ NIP-OA owner-only gate    │                       │  single-writer, FTS5-first) │
└───────────────┬──────────┘                        │ scopes: _global/workspace/  │
                │ ACP JSON-RPC 2.0 (stdio)           │   project/operator          │
                ▼                                    └───────────┬────────────────┘
┌──────────────────────────────────────────────┐                │ bounded read (Fubuki bounds.py)
│ GOVERNANCE  Fubuki OS                          │◄──────────────┘   +  dream-phase promote (05)
│  compile → canonical JSON packet + packet_hash │
│  keeps governance ledger (releases/state/audit)│
│  adapters emit placement metadata; NO model call│
└───────────────┬──────────────────────────────┘
                │ Seam A: packet as system layer + pre_llm_call hash-pin
                ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ SAFETY  #sec-ops PreToolUse containment                                      │
│  first-party CEL (deny-before-allow · fail-closed · record-before-act)       │
│  + gVisor(runsc, non-root) + secret/injection scan + anti-pattern registry   │
└───────────────┬──────────────────────────────────────────────────────────────┘
                ▼
┌──────────────────────────┐                        (HarnessRouter/UHP = Phase 2 only)
│ EXECUTION  Hermes / Claude│
│ Code / Codex / Pi (ACP)   │  pre_tool_call hard-block (Hermes/Claude Code); Pi → gVisor
└───────────────┬──────────┘
                ▼ base_url
┌────────────────────────────────────────────────────────────────────────────┐
│ ROUTING  OmniRoute  localhost:20128/v1  (SOLE MODEL EGRESS)                  │
│  compression OFF on code lane · preservation engine · 4-tier fallback · MCP  │
└───────────────┬──────────────────────────────────────────────────────────────┘
                ▼ providers
OBSERVABILITY: PandaProbe spans (CHAIN→AGENT→LLM→TOOL) · off unless env set · byte-invisible
```

## 2. Component inventory

| Component | Origin | License | Role | Port(s) | Notes |
|---|---|---|---|---|---|
| **Buzz** | block/buzz | Apache-2.0 | Interface (NIP-29 relay) | relay `:3000` | Rust/Axum + Postgres + Redis + Blossom/MinIO; `kind.rs` = 127 kinds; owner binding = **NIP-OA** |
| **buzz-acp** | block/buzz crate | Apache-2.0 | relay→agent ACP bridge | stdio | `BUZZ_PRIVATE_KEY`; owner-only; 1/channel; `--respond-to`, `--idle-timeout` 900, `--max-turn-duration` 2h |
| **ACP** | agentclientprotocol | Apache-2.0 | agent↔host protocol | stdio | `initialize/session.new/prompt/update/cancel/request_permission` |
| **Fubuki OS** | NerdHerderDani/fubuki-os | Apache-2.0 | governance / brain compiler | lib | Python 3.10+, stdlib-only; canonical-JSON packet + hash; keeps governance ledger; adapters never call a model |
| **ai-memory (fork)** | akitaonrails/ai-memory | MIT | MEMORY engine | `:49374` | Rust, single-writer git+SQLite, FTS5-first, `ScopeResolver`, auto-improve pending-writes + eval-gate |
| **OmniRoute** | diegosouzapw/OmniRoute | MIT | sole model egress | `:20128` | `/v1` + `/v1/responses`; preservation engine (code/URL/JSON); set `INITIAL_PASSWORD`; compression OFF on code lane |
| **Hermes** | NousResearch/hermes-agent | VERIFY | harness (ACP) | api `:8642` opt | `pre_tool_call` fail-closed hooks; `hermes acp`; base_url→OmniRoute |
| **Claude Code** | Anthropic | Anthropic terms | harness (ACP-native) | — | native PreToolUse hook |
| **Codex** | OpenAI | Apache-2.0 | harness (ACP) | — | expects OpenAI Responses wire |
| **Pi** | earendil-works/pi | (pi) | harness (ACP via adapter) | — | **no native ACP** (community `pi-acp`); no built-in perms → **gVisor mandatory** |
| **HarnessRouter** | HarnessRouter/harnessrouter | Apache-2.0 | multi-harness UHP gateway — **Phase 2** | UI `:3100` (remap) | `/api/harness/v1/responses`; only if a UHP-only harness appears |
| **PandaProbe** | chirpz-ai/pandaprobe | Apache-2.0 (SDK MIT) | observability | `:8000` | **auto-on when env set** → keep env unset / `PANDAPROBE_ENABLED=false`; judge→OmniRoute |
| **OpenBot** (pattern) | CopilotKit/openbot | MIT | CEL + gVisor recipe (harvest) | — | reimplement CEL first-party; non-root USER; do NOT adopt Intelligence |
| **gVisor** | google/gvisor | Apache-2.0 | containment | — | `runsc`; non-root USER |
| **ast-grep / comby** | — | MIT / Apache-2.0 | deterministic codemods | — | ast-grep primary (Python + 26 langs); comby brace/format only |

## 3. Decisions log

| Decision | Verdict | Rationale |
|---|---|---|
| **Memory engine** | **Fork `ai-memory`** (not from scratch) | Mature MIT implementation of markdown-authoritative, FTS5-first, git-single-writer memory with a gated auto-improve loop — exactly our model. Confirmed from source. |
| **Tiering** | **Hybrid** | One shared ai-memory store with per-agent `per_actor`/operator scopes by default; a **dedicated in-gVisor instance** for sensitive agents (#sec-ops) since ai-memory is single-tenant with no per-page RBAC. |
| **Fubuki role** | Governor only | Compiles the canonical packet + keeps the governance ledger (releases/state/audit). Memory tables move to ai-memory (`06` Seam B). |
| **HarnessRouter** | **Phase 2** | Hermes/Claude Code/Codex/Pi are all ACP-drivable → `buzz-acp` drives them directly; no ACP↔UHP shim in v1. |
| **Pi** | in, but **gVisor-wrapped** | ACP only via community adapter; no built-in permission system. |
| **Graph DB (Neo4j)** | OUT | ai-memory uses SQLite+FTS5; no external graph engine. |
| **OpenHarness / Switch / OpenRewrite** | OUT (v1) | OpenHarness → Phase-2 synthesis skeleton (`11`); Switch redundant with Buzz; OpenRewrite is JVM. |
| **CopilotKit Intelligence** | OUT | Reimplement OpenBot's CEL first-party. |

## 4. The four-doors integration taxonomy

Any future component enters through exactly one door; its *shape* decides, not its name.

1. **Harness backend** — a coding-agent runtime. ACP-native → `buzz-acp` direct (preferred). UHP-only → HarnessRouter (Phase 2). Fits: Hermes, Claude Code, Codex, Pi, dsh, OpenHarness.
2. **Own agent identity in Buzz** — an autonomous agent (own keypair + Fubuki brain) that runs its own loop and posts findings. Fits: deep-research agents (node-DeepResearch, AI-Researcher, deepagents-built).
3. **MCP tool / capability** — invoked by an existing agent behind the gate. Fits: deepsec, open-code-review, research pipelines.
4. **Generate a harness on the fly (Phase 2)** — the Genesis Team's Harness Foundry synthesizes a task-specific harness when no stock one fits (`11`).

**Rule:** model-runtime that reads/edits/runs? → 1. Autonomous loop producing findings? → 2. A capability something calls? → 3. A *new* agent needing a runtime no stock harness provides? → 4.

Cross-refs: endpoints/env → `03`; memory → `04`; dream phase → `05`; Fubuki seams → `06`; ports/compose → `09`.
