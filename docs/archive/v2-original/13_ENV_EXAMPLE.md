# 13 — .env.example (v2)

Markdown-viewable copy of `compose/.env.example`. Copy the block to a real `.env` (never commit it); `(SECRET)` values belong in a secrets manager in production.

```bash
# Agent Factory v2 — environment (.env.example)
# Copy to .env; never commit. (SECRET) values belong in a secrets manager in prod.
# Variable names are the real ones from source (see docs/03, docs/04, docs/06).

# ─────────────── INTERFACE · Buzz ───────────────
BUZZ_RELAY_URL=ws://localhost:3000
BUZZ_RELAY_PRIVATE_KEY=            # (SECRET) PIN THIS — unset ⇒ random key at startup, breaks discovery (PM #16)
BUZZ_PUBKEY_ALLOWLIST=            # comma-separated npub/hex, or empty to disable
BUZZ_REQUIRE_AUTH_TOKEN=true
BUZZ_PRIVATE_KEY=                 # (SECRET) this agent's nsec — crown jewel; keystore/keys.db chmod 600
BUZZ_ACP_AGENT_COMMAND=hermes    # hermes | claude-code | codex | pi  (all ACP-drivable)
BUZZ_ACP_AGENT_ARGS=acp
BUZZ_ACP_RESPOND_TO=owner-only
BUZZ_PG_USER=buzz
BUZZ_PG_PASSWORD=                # (SECRET)
BUZZ_PG_DB=buzz
BUZZ_S3_ACCESS_KEY=              # (SECRET)
BUZZ_S3_SECRET_KEY=              # (SECRET)

# ─────────────── ROUTING · OmniRoute (sole egress) ───────────────
OMNIROUTE_PORT=20128
OMNIROUTE_INITIAL_PASSWORD=      # (SECRET) default is CHANGEME — MUST set
OMNIROUTE_COMPRESSION_CODE_LANE=off   # HARD RULE (byte integrity)
OPENAI_API_KEY=                  # (SECRET) upstream provider keys (BYO)
ANTHROPIC_API_KEY=               # (SECRET)

# ─────────────── MEMORY · forked ai-memory (:49374) ───────────────
AI_MEMORY_PORT=49374
AI_MEMORY_AUTH_TOKEN=            # (SECRET) bearer for LAN; or use DB-users + token_pepper
AI_MEMORY_TOKEN_PEPPER=          # (SECRET) required for DB-user auth
# LLM + embeddings BOTH route through OmniRoute:
AI_MEMORY_LLM_PROVIDER=openai-compat
AI_MEMORY_LLM_BASE_URL=http://host.docker.internal:20128/v1
AI_MEMORY_LLM_MODEL=             # a NON-reasoning model (strict-JSON consolidation)
LLM_API_KEY=                     # (SECRET) gateway key or any
AI_MEMORY_EMBEDDING_PROVIDER=openai-compat
AI_MEMORY_EMBEDDING_BASE_URL=http://host.docker.internal:20128/v1
AI_MEMORY_EMBEDDING_MODEL=
AI_MEMORY_EMBEDDING_DIM=         # change of {provider,model,dim} ⇒ ai-memory embed --force
AI_MEMORY_RERANKER=llm           # optional
# auto-improve (dream phase) gates:
AI_MEMORY_AUTO_IMPROVE_REQUIRE_APPROVAL=true
# [auto_improve.eval] command points at the distiller scorer (docs/05, docs/08 C) — set in ai-memory config

# ─────────────── GOVERNANCE · Fubuki ───────────────
# invoked as a CLI (like a library); no port. Packet placed as system layer + pre_llm_call hash-pin.
FUBUKI_PACKAGE_DIR=./personas

# ─────────────── SECURITY · containment ───────────────
COMPUTER_RUNTIME=runsc           # gVisor for per-agent tool execution
CREDENTIALS_ENCRYPTION_KEY=      # (SECRET) openssl rand -base64 32

# ─────────────── OBSERVABILITY · PandaProbe (OFF by default) ───────────────
PANDAPROBE_ENABLED=false         # SDK auto-inits if its env is present — keep this false unless debugging
# PANDAPROBE_JUDGE_BASE_URL=http://host.docker.internal:20128/v1

# ─────────────── PHASE 2 · HarnessRouter (not used in v1) ───────────────
HR_UI_PORT=3100                  # remapped from 3000 to avoid the Buzz collision
HR_AUTH_PASSWORD=                # (SECRET) required; pin image >=0.3.0
HR_SECRET_KEY=                   # (SECRET)
```
