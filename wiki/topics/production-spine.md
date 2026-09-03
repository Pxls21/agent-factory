---
topic: production-spine
last_compiled: 2026-09-03
---

# Production Spine — Buzz, ACP, Hermes, OmniRoute

## 1. Purpose [coverage: high -- 8 sources]

The production spine is the live interaction path from human input to model response:
Buzz relay --> `buzz-acp` --> Hermes native ACP server --> OmniRoute --> approved model providers.
Each component is pinned by commit in [upstream.lock.yaml](upstream.lock.yaml) and has
specific integration contracts in [docs/03_INTEGRATION_CONTRACTS.md](docs/03_INTEGRATION_CONTRACTS.md).

**No component in this spine has been deployed or smoke-tested.** The contracts exist as
acceptance-test specifications; the Stage 0 proof pack (S0-01 through S0-05) will validate them.

## 2. Architecture [coverage: high -- 7 sources]

**Buzz relay** (Apache-2.0, pinned at `1c8321c`): human collaboration relay. Postgres 17,
passworded append-only Redis, pinned MinIO, `BUZZ_S3_*` configuration. Selected idle timeout 900s
(over source default 1500s and README-stated 620s).

**buzz-acp** (from the same Buzz repo): launches `hermes-acp` with
`BUZZ_ACP_AGENT_COMMAND=hermes-acp`. Source-backed bridge variables: agent command/args, MCP
command, idle timeout (900s), max turn duration (3600s), system prompt file, agent count (1),
agent owner.

**Hermes Agent** (MIT, v0.21.0, pinned at `527da60`): sole stock production workhorse. Native
ACP server via `hermes-acp`. Custom providers support `base_url`, `api_mode`, `key_env`,
`extra_headers`. `pre_tool_call` hooks support `fail_closed: true`. `pre_llm_call` context
injection fails open (strict memory workflows need external preflight). Container starts as root
for s6/UID setup, then drops to `hermes` user.

**OmniRoute** (MIT, v3.8.51, pinned at `500568a`): sole model/embedding API egress. Native
`/v1/responses` and tool calls. Final image user `node`. Provider setup is stateful through
dashboard workflows. Hermes config: `api_mode: codex_responses`, `key_env: OMNIROUTE_INTERNAL_API_KEY`,
header `x-omniroute-compression: off` (the old `COMPRESSION_CODE_LANE` var is unsupported).

**ACP** (Apache-2.0, pinned at `37a7d4f`): the typed session/turn boundary. Pin the protocol
and verify initialize, prompt, streaming, cancellation, terminal states, and clean shutdown.

## 3. Talks To [coverage: high -- 5 sources]

- Buzz users --> Buzz relay (Postgres, Redis, MinIO backing)
- Buzz relay --> `buzz-acp` (authorized events only)
- `buzz-acp` --> `hermes-acp` (ACP initialize/prompt/stream/cancel/shutdown)
- Hermes --> OmniRoute `/v1` (`codex_responses`, internal API key)
- OmniRoute --> configured upstream model providers (credentials in OmniRoute only)
- Hermes --> memory adapter, policy hook, governance (separate topics)

## 4. API Surface [coverage: medium -- 4 sources]

Planned contracts (no runtime exists):

- **Buzz authorization** (S0-02): allowlist/membership, signature, independent freshness,
  cursor/de-duplication. NIP-OA `created_at` is agent-declared metadata, not revocation.
- **ACP conformance** (S0-01): seven acceptance tests covering the full lifecycle.
- **OmniRoute round trip** (S0-03): text + tool-call; pass asserts upstream model identity
  (never just a 200); the S0-04 stub is FORBIDDEN for this proof.
- **Compression contract** (S0-04): `x-omniroute-compression: off` sent, `X-OmniRoute-Compression`
  response header asserted, deterministic stub proves request preservation. The ONE sanctioned
  stub in Stage 0.

## 5. Data [coverage: medium -- 3 sources]

No runtime data stores exist. Planned: Buzz uses Postgres 17 for relay state, Redis for
session/pub-sub, MinIO for object storage. OmniRoute needs `DATA_DIR`, `JWT_SECRET`,
`API_KEY_SECRET`, `STORAGE_ENCRYPTION_KEY` for persistence.

## 6. Key Decisions [coverage: high -- 6 sources]

- Hermes sole runtime (D-001/ADR 0001): removes duplicate execution paths
- ACP retained (D-002): `buzz-acp` launches `hermes-acp`; Hermes native Buzz plugin is a
  later experiment, not v1
- OmniRoute sole egress (D-003/ADR 0002): centralizes credentials, routing, evidence
- Codex via `codex_responses` (D-004): Codex is a model choice, not another runtime
- Codex app-server/OAuth not enabled in v1 (D-005)
- Idle timeout 900s selected over 1500s (source) and 620s (README) -- pending load test
- Council verdict: S0-03 blocks on a real credential; pass asserts upstream model identity,
  never a 200; the S0-04 stub is forbidden for S0-03 (Socrates' strongest control)
- PC bridge probe (2026-09-03): OmniRoute already running on the owner's PC at `:20128`;
  local vLLM (`sim9b`) available as upstream -- credential question closed

## 7. Gotchas [coverage: high -- 7 sources]

**NOT-built (first-class):**
- No component has been installed, configured, or run
- No ACP conformance test, Buzz authorization test, or OmniRoute round trip executed
- No compression contract validation
- No egress canary suite

**Known issues from the component audit:**
- `pre_llm_call` context injection fails open -- strict memory workflows need external preflight
  ([docs/02_COMPONENT_AUDIT.md](docs/02_COMPONENT_AUDIT.md) SS2.1)
- OmniRoute size must be measured from concurrent long Responses; 1 GiB is not accepted
- Buzz source currently defaults idle timeout to 1500s vs README 620s (neither matches the
  selected 900s)
- NIP-OA `created_at` is metadata, not revocation -- enforce membership independently

**Premortem top risks (#1, #2, #9, #17):** ACP lifecycle disagreement, OmniRoute corrupting
tool calls, Buzz relying on author timestamp, OmniRoute OOM on concurrent Responses.

## 8. Sources

- [docs/01_ARCHITECTURE.md](docs/01_ARCHITECTURE.md)
- [docs/02_COMPONENT_AUDIT.md](docs/02_COMPONENT_AUDIT.md)
- [docs/03_INTEGRATION_CONTRACTS.md](docs/03_INTEGRATION_CONTRACTS.md)
- [docs/07_BUILD_PLAN.md](docs/07_BUILD_PLAN.md)
- [docs/09_PREMORTEM.md](docs/09_PREMORTEM.md)
- [docs/adr/0001-hermes-only-runtime.md](docs/adr/0001-hermes-only-runtime.md)
- [docs/adr/0002-omniroute-sole-model-egress.md](docs/adr/0002-omniroute-sole-model-egress.md)
- [upstream.lock.yaml](upstream.lock.yaml)
