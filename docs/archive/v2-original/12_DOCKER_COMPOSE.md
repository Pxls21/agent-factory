# 12 — docker-compose (v2)

Markdown-viewable copy of `compose/docker-compose.yml`. The raw file is what you actually run; this renders for reading.

```yaml
# Agent Factory v2 — docker-compose (v1 spine)
# Grounding: Postgres/Redis/MinIO use REAL official images. Buzz, OmniRoute, ai-memory (and Phase-2
# HarnessRouter, PandaProbe) are self-hosted-from-source; they use build contexts against ./vendor/<name>
# (our forks/clones) or a confirmed published image — do NOT trust an invented tag.
# ai-memory publishes `akitaonrails/ai-memory` (multi-arch) — but we run our FORK, so build from ./vendor/ai-memory.
# Only Buzz :3000, OmniRoute :20128, ai-memory :49374 are published. Every service runs non-root.
#
# Usage:
#   cp .env.example .env && edit .env
#   git submodule update --init                # vendor/ai-memory (fork), vendor/buzz, vendor/omniroute, vendor/fubuki-os
#   docker compose up -d                       # v1 spine
#   docker compose --profile phase2 up -d      # + HarnessRouter (only if a UHP-only harness appears)

name: agent-factory

services:
  buzz-postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${BUZZ_PG_USER}
      POSTGRES_PASSWORD: ${BUZZ_PG_PASSWORD}
      POSTGRES_DB: ${BUZZ_PG_DB}
    volumes: [ buzz_pg:/var/lib/postgresql/data ]
    healthcheck: { test: ["CMD-SHELL","pg_isready -U ${BUZZ_PG_USER}"], interval: 10s, timeout: 5s, retries: 5 }
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: ["redis-server","--save","60","1"]
    volumes: [ redis_data:/data ]
    healthcheck: { test: ["CMD","redis-cli","ping"], interval: 10s, timeout: 5s, retries: 5 }
    restart: unless-stopped

  minio:
    image: minio/minio:latest
    command: ["server","/data","--console-address",":9001"]
    environment:
      MINIO_ROOT_USER: ${BUZZ_S3_ACCESS_KEY}
      MINIO_ROOT_PASSWORD: ${BUZZ_S3_SECRET_KEY}
    volumes: [ minio_data:/data ]
    restart: unless-stopped

  buzz-relay:
    build: { context: ./vendor/buzz }        # TODO: submodule (Rust/Axum workspace)
    depends_on:
      buzz-postgres: { condition: service_healthy }
      redis: { condition: service_healthy }
      minio: { condition: service_healthy }
    environment:
      BUZZ_RELAY_PRIVATE_KEY: ${BUZZ_RELAY_PRIVATE_KEY}   # PIN — else random key at startup (PM #16)
      BUZZ_PUBKEY_ALLOWLIST: ${BUZZ_PUBKEY_ALLOWLIST}
      BUZZ_REQUIRE_AUTH_TOKEN: ${BUZZ_REQUIRE_AUTH_TOKEN}
      DATABASE_URL: postgres://${BUZZ_PG_USER}:${BUZZ_PG_PASSWORD}@buzz-postgres:5432/${BUZZ_PG_DB}
      REDIS_URL: redis://redis:6379
      S3_ENDPOINT: http://minio:9000
    ports: [ "3000:3000" ]
    restart: unless-stopped

  omniroute:
    build: { context: ./vendor/omniroute }   # TODO: submodule (diegosouzapw/OmniRoute)
    environment:
      INITIAL_PASSWORD: ${OMNIROUTE_INITIAL_PASSWORD}     # default CHANGEME — MUST set
      PORT: ${OMNIROUTE_PORT}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      # compression OFF on the code lane — enforce in OmniRoute config too (PM #1)
    ports: [ "${OMNIROUTE_PORT}:20128" ]      # bind 127.0.0.1 in prod
    restart: unless-stopped

  ai-memory:
    build: { context: ./vendor/ai-memory }   # OUR FORK (provenance overlay + distiller companion)
    depends_on:
      omniroute: { condition: service_started }
    environment:
      AI_MEMORY_AUTH_TOKEN: ${AI_MEMORY_AUTH_TOKEN}
      AI_MEMORY_TOKEN_PEPPER: ${AI_MEMORY_TOKEN_PEPPER}
      AI_MEMORY_LLM_PROVIDER: ${AI_MEMORY_LLM_PROVIDER}
      AI_MEMORY_LLM_BASE_URL: ${AI_MEMORY_LLM_BASE_URL}
      AI_MEMORY_LLM_MODEL: ${AI_MEMORY_LLM_MODEL}
      LLM_API_KEY: ${LLM_API_KEY}
      AI_MEMORY_EMBEDDING_PROVIDER: ${AI_MEMORY_EMBEDDING_PROVIDER}
      AI_MEMORY_EMBEDDING_BASE_URL: ${AI_MEMORY_EMBEDDING_BASE_URL}
      AI_MEMORY_EMBEDDING_MODEL: ${AI_MEMORY_EMBEDDING_MODEL}
      AI_MEMORY_EMBEDDING_DIM: ${AI_MEMORY_EMBEDDING_DIM}
      AI_MEMORY_AUTO_IMPROVE_REQUIRE_APPROVAL: ${AI_MEMORY_AUTO_IMPROVE_REQUIRE_APPROVAL}
    volumes:
      - ai_memory_data:/data          # /data/{wiki(git),raw,db,models,logs} — wiki is authoritative
    extra_hosts: [ "host.docker.internal:host-gateway" ]   # reach OmniRoute
    ports: [ "${AI_MEMORY_PORT}:49374" ]    # loopback + bearer in prod
    restart: unless-stopped

  # Harnesses (Hermes/Claude Code/Codex/Pi) are launched per-agent by buzz-acp over ACP stdio, each
  # inside gVisor (runsc) with the CEL gate on — NOT long-running compose services. base_url → OmniRoute.
  # Fubuki is invoked as a CLI by the loader adapter; no service.

  # ─────────────── PHASE 2 (profile: phase2) ───────────────
  harnessrouter:
    profiles: ["phase2"]
    build: { context: ./vendor/harnessrouter }   # pin >=0.3.0; only for a UHP-only harness
    environment:
      HR_AUTH_PASSWORD: ${HR_AUTH_PASSWORD}
      HR_SECRET_KEY: ${HR_SECRET_KEY}
    ports: [ "${HR_UI_PORT}:3000" ]     # host 3100 -> container 3000 (avoids Buzz clash)
    extra_hosts: [ "host.docker.internal:host-gateway" ]
    restart: unless-stopped

volumes:
  buzz_pg:
  redis_data:
  minio_data:
  ai_memory_data:

# Reality caveats: replace every ./vendor/<name> with a real fork/clone or a confirmed pinned image.
# gVisor runtime (runtime: runsc) applies to the per-agent execution sandboxes spawned at runtime, not to
# these infra services. In prod, bind published ports to 127.0.0.1 behind a TLS-terminating proxy.
```
