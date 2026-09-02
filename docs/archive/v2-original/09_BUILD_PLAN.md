# 09 — Build Plan (v2)

**Version:** 2.0 · **Date:** 2026-09-01

Build in stages. **Do not advance until the benchmark passes with a real command and real output** (§0 no hollow greens).

---

## 1. Repo layout

```
~/agent-factory/
├── docs/                      # this spec set (00–11)
├── compose/                   # docker-compose.yml + .env.example
├── vendor/
│   ├── ai-memory/             # our FORK (submodule) — memory engine
│   ├── fubuki-os/             # governance (submodule)
│   ├── buzz/                  # interface (submodule)
│   └── omniroute/             # egress (submodule)
├── companions/
│   └── agent-factory-distiller/   # Adapter C (ai-memory companion crate)
├── adapters/
│   ├── fubuki_loader/         # Adapter A (loader + pre_llm_call hash-pin)
│   ├── fubuki_ai_memory_read/ # Adapter B (bounded read → bounds.py)
│   ├── cel_gate/              # Adapter D
│   ├── codemod/               # Adapter F
│   └── egress_guards/         # Adapter G
├── personas/<slug>/           # Fubuki persona packages (manifest + modes + banned_tokens.txt)
├── ai-memory-data/            # ai-memory data dir (wiki=git, db=derived)  [gitignored except wiki]
├── keystore/keys.db           # nsec keys · chmod 600 · NEVER in git
└── NOTICE                     # ai-memory (MIT), Fubuki (Apache-2.0)
```

## 2. Port map

| Service | Port | Notes |
|---|---|---|
| Buzz relay | `3000` | canonical |
| Buzz Postgres/Redis/MinIO | 5432 / 6379 / 9000 | internal |
| OmniRoute | `20128` | sole egress; `INITIAL_PASSWORD` set; bind 127.0.0.1 in prod |
| **ai-memory** | `49374` | loopback + bearer; data volume |
| Hermes API (optional) | 8642 | `API_SERVER_KEY` |
| PandaProbe (off by default) | 8000 | env unset / `PANDAPROBE_ENABLED=false` |
| **HarnessRouter UI (Phase 2)** | `3100` | remapped from 3000 |
| gVisor runsc sandboxes | — | per-agent; no published port |

Compose publishes only Buzz `:3000`, OmniRoute `:20128`, ai-memory `:49374`. Every image runs non-root.

## 3. Staged rollout

### Stage 0 — scaffolding
Fork ai-memory; add submodules; write `NOTICE`; resolve open decisions that gate your path (D3–D6, D9, D10 — `06`). **Benchmark:** `docker compose config` validates; decisions recorded.

### Stage 1 — spine up (Interface → Execution → Routing)
Buzz relay + stores; one agent nsec; `buzz-acp` with `BUZZ_ACP_AGENT_COMMAND=hermes`; harness `base_url` → OmniRoute with **compression OFF on the code lane**.
**Benchmark:** a kind:9 @mention in `#dev-coding` round-trips a **byte-identical** diff (Adapter G byte-echo canary green).
**Threshold:** if any OmniRoute mode mutates the fixture bytes, keep compression permanently off on that lane.

### Stage 2 — memory engine (forked ai-memory)
Stand up ai-memory `:49374`; providers → OmniRoute; map scopes (`_global`=Company, workspace=Team via `.ai-memory.toml`, project=Project, operator=Agent); land the provenance-overlay migration (Adapter E).
**Benchmarks:** `memory_query` returns lexical hits with **no** provider configured (proves lexical-first); a superseded fact is queryable point-in-time (not deleted); `reindex` round-trips all overlay fields.

### Stage 3 — governance (Fubuki, Seam A + B)
Adapter A (compile → packet → system-layer inject → `pre_llm_call` hash-pin) + Adapter B (bounded read → `bounds.py`). Keep Fubuki's governance ledger; memory tables served by ai-memory.
**Benchmarks:** identical compile inputs → identical `packet_hash` across 3 runs; a tampered packet is **blocked**; a `restricted` record never reaches a third-party-visible packet (bounds.py filter 4).

### Stage 4 — containment (#sec-ops)
Adapter D (CEL) + gVisor (non-root) + scanners + registry **before** granting any write/exec tool; Pi only ever inside gVisor.
**Benchmark:** a deny rule fires and writes an audit row **before** the tool runs; a compile-broken policy refuses; a canary secret in a distillation is caught before promotion.

### Stage 5 — dream phase (distillation)
Adapter C (distiller companion) + `[auto_improve] require_approval=true` + `[auto_improve.eval] command=<distiller scorer>`; schedule the nightly curator agent.
**Benchmarks:** an un-stripped identifier fails the eval-gate and lands as a **rejected candidate**, never a write; a proven lesson promotes Project→Team with identifiers stripped and a human approval recorded; consolidation never lowers the retro-gate pass rate (else auto-revert).

### Stage 6 — hardening + observability
Dedicated in-gVisor ai-memory instance for #sec-ops (hybrid tiering); enable PandaProbe only for debugging (env-gated).
**Threshold:** if ai-memory's SQLite ever diverges from the git wiki, halt agent writes and `reindex` from wiki.

## 4. Definition of done
A `#dev-coding` task flows end-to-end (post → compile+hash-pin → contain → run → egress → verify → signed reply → git push) with every gate real; memory supersedes-not-deletes and promotes with identifiers stripped; no shell runs without a prior audit row; gVisor holds even with hooks disabled; no gate reports a pass without a backing command+output.

## 5. Tech notes
Adapters in Python (Fubuki, bounds.py, personas) or Rust (ai-memory companion). Dependency-light. No graph DB, no JVM. Point ai-memory's non-reasoning consolidation model + embeddings at OmniRoute; prove zero-LLM (FTS5) mode first.
