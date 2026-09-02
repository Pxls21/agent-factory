# 02 — Component and source audit

Audit snapshot: 2026-09-02. Exact inspected commits are recorded in `upstream.lock.yaml`.

## 1. Executive findings

The full Agent Factory design remains useful. The source audit changes several integration claims and removes only redundant stock runtimes.

| Finding | Planning consequence |
|---|---|
| Hermes exposes a native ACP server | Keep `buzz-acp`, but point it at `hermes-acp`; no Codex/Claude/Pi ACP adapter is needed |
| Hermes supports `codex_responses` custom providers | Codex-capable models run through Hermes + OmniRoute without Codex CLI/app-server |
| Hermes also has a native Buzz plugin | Retain as a future simplification spike; it is not the selected live path |
| ai-memory has native `(workspace, project)` scope only | Preserve four logical scopes through a first-party composite authorization adapter |
| JIT generates a five-file agent design | Retain it in an isolated Foundry with a translation/manifest step, not direct production output |
| GBrain has a rich dream cycle but is a full knowledge system | Reuse/adapt its proposal, provenance, verification, and orchestrator patterns in an isolated worker |
| HarnessRouter's official shape is a UHP gateway, not the earlier invented three-port layout | Keep it conditional for an approved UHP-only harness |
| OpenHarness is a full harness, not a minimal skeleton | Evaluate it as a reference or host; do not assume it is a lightweight scaffold |
| AlphaEval evaluates complete agents but has unsafe stock runner defaults for this threat model | Retain its task/evaluator format behind a hardened Hermes/harness runner |

## 2. Core selected components

### Hermes Agent — sole stock production workhorse

- MIT; observed version 0.21.0.
- Native ACP server is available as `hermes-acp` / `hermes acp` with the optional ACP dependency.
- Custom providers support `base_url`, `api_mode`, `key_env`, and `extra_headers`.
- Select `codex_responses` through OmniRoute; do not enable `codex_app_server` or OpenAI Codex OAuth in v1.
- `pre_tool_call` hooks can block/modify and shell hooks support `fail_closed: true`.
- `pre_llm_call` context injection fails open; strict memory workflows need an external preflight.
- One external `MemoryProvider` is supported and errors are non-fatal, so the four-scope logic belongs behind one composite provider.
- The container starts as root for s6/UID setup, then services drop to `hermes`; test that exact lifecycle under gVisor.

Build: Fubuki extension, composite ai-memory provider, policy hook, audit envelope, and ACP conformance tests.

### Buzz and `buzz-acp` — selected interaction bridge

- Buzz is Apache-2.0 and supplies the human collaboration relay.
- Configure `BUZZ_ACP_AGENT_COMMAND=hermes-acp`; `BUZZ_ACP_AGENT_ARGS` may be blank.
- Set `BUZZ_ACP_IDLE_TIMEOUT` explicitly. Source currently defaults to 1500 seconds while the README table says 620; this plan selects 900 pending load tests.
- Source-backed bridge variables include agent command/args, MCP command, idle timeout, max turn duration, system prompt/file, agent count, and agent owner.
- The production relay layout uses Postgres 17, passworded append-only Redis, pinned MinIO plus initialization, and `BUZZ_S3_*` configuration. Do not revive the earlier Postgres 16, unauthenticated Redis, mutable MinIO, or incorrect S3 variables.
- NIP-OA `created_at` is agent-declared metadata, not revocation. Enforce membership removal/key rotation and independent freshness.

### Agent Client Protocol — selected interface contract

ACP remains the typed session/turn boundary between `buzz-acp` and Hermes. Pin the protocol and verify initialize, prompt, streaming, cancellation, terminal states, and clean process shutdown against `hermes-acp`.

### OmniRoute — sole model/embedding API egress

- MIT; observed version 3.8.51; native `/v1/responses` and tool calls; final image user `node`.
- Persist state and configure `JWT_SECRET`, `API_KEY_SECRET`, `STORAGE_ENCRYPTION_KEY`, `DATA_DIR`, and a non-default `INITIAL_PASSWORD`.
- Provider setup is stateful through setup/dashboard workflows, not just an upstream key environment variable.
- The old `OMNIROUTE_COMPRESSION_CODE_LANE` variable is unsupported. Send `x-omniroute-compression: off`, assert `X-OmniRoute-Compression`, and compare a deterministic stub request at the boundary.
- Size memory from concurrent long Responses measurements; 1 GiB is not an accepted estimate.
- OmniRoute is sole model API egress, not automatically sole web/tool egress.

### Fubuki — selected governance library with corrections

- Apache-2.0; observed version 0.1.0; Python 3.10+; standard library.
- Canonical JSON and packet hashing fit immutable governance identity.
- `bounds.evaluate_records` returns `BoundDecision` values. Join allowed `record_id` values to source records; do not read a nonexistent payload.
- `persona_lint` can retain exit code 2 after a later violation. Fix/wrap it and add an ordered regression fixture.
- Audit run: 129 unittest cases passed; one import failed because `pytest` was absent. Treat this as partial evidence, not a complete green suite.
- Fubuki is a library/CLI, not a long-running governance service.

### ai-memory — selected durable substrate for four logical scopes

- MIT; observed version 1.39.0; Rust 1.95; image Dockerfile is `docker/Dockerfile`; runtime user `ai-memory`.
- Native scope is `(workspace, project)` and `_global` is a reserved project.
- Map Company, Team, Project, and Agent to distinct project IDs behind one first-party composite provider. The provider enforces identity, read precedence, write target, bounds, and leakage tests.
- Same-workspace tokens are not native per-project RBAC. The adapter is a security boundary; high-sensitivity tenants may require separate instances/workspaces.
- `/api/v1` is read-only; writes are admin/MCP surfaces.
- Nested environment keys use double underscores, including `AI_MEMORY_AUTO_IMPROVE__REQUIRE_APPROVAL`.
- Auto-improve scheduling defaults on and approval defaults off when configured. Start with scheduler and maintenance off, approval on, and no model-callable mutation tools.
- Cross-scope promotion is a companion workflow, not native auto-improve.

### gVisor and policy service — selected security controls

gVisor initially contains the whole Hermes runtime, including tools; it is not per-tool isolation without a broker. The first-party policy service provides fail-closed semantic authorization. Research/evaluation workers also use isolated gVisor profiles.

## 3. Retained improvement and evaluation components

### JIT — Harness Foundry generator

- MIT; generates `memory.py`, `planning.py`, `action.py`, `tool_policy.py`, and `prompt.yaml`.
- Includes best-of-N generation, selection, and evaluation concepts.
- It is neither ACP-native nor OpenHarness-specific.

Retain it as an offline generator. Freeze the generator version; emit the five files plus a first-party `HarnessSpec` manifest and provenance; run in a no-secret/no-production-network sandbox; evaluate against the Hermes baseline; require signed human promotion.

### GBrain — dream-phase mechanism source

- MIT; observed version 0.48.1.0.
- Its dream cycle uses LLM triage, constrained subagents, orchestrator-controlled validation/writes, quote verification, provenance, and reverse writing.
- It is a full knowledge system rather than an ai-memory extension.

Retain the capability by adapting/wrapping pinned dream modules or patterns. The worker reads sanitized snapshots/traces, produces proposals only, and never receives ai-memory admin credentials.

### HarnessRouter — conditional Phase 2 gateway

- Apache-2.0; current inspected UHP specification is dated 2026-08-11.
- Official deployment is a one-container gateway and starts as root before dropping to per-session users.

Do not place it on the core Buzz→Hermes path. Activate it only if an approved generated or third-party harness is UHP/Responses-only and cannot use ACP. Re-audit its current spec and containment at that gate.

### OpenHarness — Foundry reference/possible host

- MIT; observed version 0.1.9.
- It is a complete standalone harness, not a minimal skeleton.

Stage 0/Foundry research must decide whether to extract interface patterns, build a minimal first-party host, or integrate a pinned OpenHarness derivative. No decision is implied yet.

### AlphaEval — isolated acceptance laboratory

- MIT; inspected version contains 94 tasks across seven companies and six domains.
- Useful mixed evaluators and complete-agent task structure.
- No Hermes runner is supplied; stock flows use host networking, recursive `chmod 777`, credential passing, and rubric subprocesses in the workspace.

Build a Hermes/candidate runner, isolate rubric execution, remove production secrets/host networking, pin dependencies, and route any judge calls through OmniRoute.

### PandaProbe — retained optional observability plane

Useful for trace analysis and evaluation once its data, credential, retention, and model-call behavior are hardened. Stock self-host examples use mutable images/default credentials. Judge or repair calls must use OmniRoute. It is optional operationally, but remains in the roadmap.

## 4. Development/reference components

- ast-grep and Comby: deterministic development codemods, exposed only through controlled wrappers when used by an agent.
- OpenBot: source of fail-closed CEL semantics; not a drop-in policy daemon.

## 5. Not selected as stock runtimes

| Component | Reason |
|---|---|
| Codex CLI / Codex app-server | Hermes reaches Codex-capable models through OmniRoute; another tool runtime adds a duplicate trust path |
| `codex-acp` | `buzz-acp` launches `hermes-acp` directly |
| Claude Code / `claude-agent-acp` | Parallel stock engine intentionally removed |
| Pi / `pi-acp` | Parallel stock engine intentionally removed |

This exclusion does not remove JIT, GBrain, OpenHarness research, AlphaEval, PandaProbe, or conditional HarnessRouter.

## 6. Audit limits

This is a source-level planning audit, not production qualification. No target-host Docker/gVisor deployment, live Buzz relay, live provider, end-to-end ACP turn, four-scope adapter, JIT run, dream cycle, or hardened evaluation execution has yet passed. The build plan makes those executable gates rather than assumptions.
