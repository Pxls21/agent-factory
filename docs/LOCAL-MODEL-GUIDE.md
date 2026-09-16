# Using the local Qwen 3.8 model (portable guide)

**What this is.** A single Qwen3.8-27B model server runs on the owner's PC (one RTX 3090) as the vLLM
`qwen` container (D-032). It is reachable from any harness or repo **through OmniRoute** — the sole model
egress. This guide is written to be **portable**: copy it into another repo (e.g. `trading-system`) and the
same commands work, because the model, OmniRoute, and the PC are shared infrastructure, not per-repo.

## The one invariant (do not break it)

**Always reach the model through OmniRoute. Never call the container's `:8080` directly.** (Project rule 3 /
ADR-0002: OmniRoute is the sole model API egress; provider credentials live only in OmniRoute; direct
fallback is prohibited.) The container binds loopback `:8080`; OmniRoute binds loopback `:20128` and proxies
to it. Consumers talk to `:20128` only.

## Identifiers (read these off the live system, don't memorize)

| Thing | Value | Where it comes from |
|---|---|---|
| OmniRoute endpoint | `http://127.0.0.1:20128/v1` (loopback on the PC) | `~/.omniroute-migrated` |
| OmniRoute node | `qwen-local` (openai-compatible, → `127.0.0.1:8080`) | `harness-ports/bin/omniroute_local_builder.py` |
| **Model id** | **`qwen-local/qwen3.8-27b-local`** | `<node prefix>/<served alias>`; listed in OmniRoute `/v1/models` |
| Build combo | `agentfactory-build-local` (Qwen first, then the cloud chain) | the local-first combo |
| Verify combo | `agentfactory-verify-local` (Qwen first, then the cloud chain) | the local-first combo |
| Inference API key | `OMNIROUTE_API_KEY` in `~/.hermes/profiles/agentfactory/.env` | OmniRoute requires auth (task #34) |
| Container | `qwen` systemd `--user` Quadlet (`deploy/qwen.container`, D-032) | digest-pinned in `upstream.lock.yaml` |
| Fallback | llama.cpp `qwen-builder` unit — serves the SAME name/port, autostart disabled | D-027 (manual fallback) |

**Model id vs combo — pick deliberately:**
- **`qwen-local/qwen3.8-27b-local`** (the raw model): the request ALWAYS goes to local Qwen. If Qwen is down
  the request errors — visible, and **no silent cloud spend**. Use this for a *cheap local teammate/agent*.
- **`agentfactory-build-local` / `agentfactory-verify-local`** (the combos): Qwen first, then a cloud
  fallback chain. Stays up if Qwen is down, but can **quietly** run up cloud quota. Use this only where
  resilience matters more than cost, and where a silent cloud substitution is acceptable.

## Verify the model is alive (one command, on the PC)

```bash
bash scripts/pc.sh 'cd ~/agent-factory && python3 harness-ports/bin/omniroute_local_builder.py status && python3 harness-ports/bin/omniroute_local_builder.py probe'
```
`status` prints the node/connection/combo + whether OmniRoute lists the model; `probe` sends one completion
through the combo and asserts the LOCAL model served it (`served model='qwen3.8-27b-local' … content='pong'`).

## Consumer pattern 1 — Hermes build/verify lanes (already wired)

The PC build/verify lanes use the combos `agentfactory-build-local` (build, effort `medium`, D-028) and
`agentfactory-verify-local` (verify, effort `xhigh`). Dispatched by `scripts/pc_lane.sh`; provisioned by
`omniroute_local_builder.py ensure`. Nothing to do — this is the default local route.

## Consumer pattern 2 — a Buzz teammate backed by Qwen (`buzz-agent`)

Buzz's "local models feature" is **`buzz-agent`** — block/buzz's own minimal ACP agent. Point it at OmniRoute
by env var (proven live 2026-09-16, D-033):

```bash
BUZZ_AGENT_PROVIDER=openai
OPENAI_COMPAT_BASE_URL=http://127.0.0.1:20128/v1      # OmniRoute — the sole egress
OPENAI_COMPAT_MODEL=qwen-local/qwen3.8-27b-local      # raw model = Qwen only, no silent cloud fallback
OPENAI_COMPAT_API=chat                                # chat completions (ADR-0002)
OPENAI_COMPAT_API_KEY=<OMNIROUTE_API_KEY>             # from ~/.hermes/profiles/agentfactory/.env, or a dedicated Buzz key
```

`buzz-agent` speaks ACP (JSON-RPC over stdio): a client sends `initialize` → `session/new` → `session/prompt`;
the agent calls the LLM and streams `agent_message_chunk` updates back. In the Buzz production stack a teammate
is an ACP agent that **pairs** to the relay separately (it is NOT in the compose) — pairing uses the owner's
Nostr identity + a community, done in the Buzz app. See ADR-0007 and D-033 for the governance rules below.

**Governance caveats for a Buzz teammate (do not skip):**
- **Sole egress:** point at OmniRoute (`:20128`), never `:8080`. (Rule 3 / ADR-0002.)
- **Policy gate:** a `buzz-agent` teammate's own tools do NOT pass Hermes' `pre_tool_call` policy gate (rule 9).
  So a Qwen teammate runs **chat-only (no effectful MCP tools)** until a policy gate is wired for it. Coding /
  tool-effectful / governed work stays on **Hermes** (rule 1).
- **Cost honesty:** prefer the raw model id so the teammate never silently falls back to a paid cloud model.

## Consumer pattern 3 — any OpenAI-compatible client (other repo / other sandbox)

Any tool that speaks OpenAI chat-completions can use the model:
```
POST http://127.0.0.1:20128/v1/chat/completions
Authorization: Bearer <OMNIROUTE_API_KEY>
{"model":"qwen-local/qwen3.8-27b-local","messages":[{"role":"user","content":"…"}]}
```
The response `model` field reads `qwen3.8-27b-local` when Qwen served it.

**Reaching it from a different sandbox.** A cloud sandbox cannot see the PC's loopback directly. Two ways:
1. **Over the PC bridge** (the pattern this and the trading-system repo already use): run the request on the PC
   via `scripts/pc.sh '<curl to 127.0.0.1:20128 …>'`. The bridge link + token are in the untracked
   `.pc-bridge.env`, pasted per session from the owner's BRIDGE READY banner.
2. **Over the tailnet**, IF the owner has exposed OmniRoute on Tailscale (the PC is `fedora.tailbfae9d.ts.net`).
   Not assumed here — confirm with the owner before pointing a remote client at a tailnet OmniRoute address.

## Lifecycle (owner's PC)

- The model server is the `qwen` `--user` Quadlet (`deploy/qwen.container`), `Restart=always`, survives reboot.
- The llama.cpp `qwen-builder` unit is the **manual fallback** (autostart disabled; same name/port, so OmniRoute
  is unaffected by which one runs).
- **Never stop or restart it while a local-route lane is live** — it holds the 3090; a restart kills every lane
  mid-turn (see `PC-BRIDGE.md`, AF-AP-79 / D-030).

## Provenance

`docs/research/findings/VLLM-MIGRATION.md` (the container + the D-032 productionization) ·
`docs/08_DECISION_LOG.md` (D-032, D-033) · `docs/adr/0002-omniroute-sole-model-egress.md` ·
`docs/adr/0007-buzz-agent-local-model-teammates.md` · `harness-ports/bin/omniroute_local_builder.py` ·
`deploy/qwen.container` · `PC-BRIDGE.md`.
