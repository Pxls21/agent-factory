# 03 — Integration contracts

These contracts are implementation requirements. Provisional first-party file names may change; behavior and boundaries may not change without an ADR.

## 1. Buzz → `buzz-acp` → Hermes

Selected bridge configuration:

```text
BUZZ_ACP_AGENT_COMMAND=hermes-acp
BUZZ_ACP_AGENT_ARGS=
BUZZ_ACP_IDLE_TIMEOUT=900
BUZZ_ACP_MAX_TURN_DURATION=3600
BUZZ_ACP_AGENTS=1
```

Use `BUZZ_ACP_SYSTEM_PROMPT_FILE` for a reviewed bootstrap layer if needed; governance remains Fubuki-owned. Pin Buzz, `buzz-acp`, ACP, and Hermes commits together.

Acceptance tests:

1. An allowed, fresh Buzz event produces one ACP session/turn in `hermes-acp`.
2. Unauthorized, invalid, replayed, stale, and self-authored events produce none.
3. ACP initialize, prompt, streaming updates, cancellation, terminal result, and shutdown conform to the pinned protocol.
4. A thread maps to the intended Hermes session without collision across users/projects.
5. The explicit 900-second idle timeout and maximum turn duration are observed.
6. Restart/duplicate delivery does not duplicate a completed turn.
7. Membership removal or key rotation revokes access independently of NIP-OA timestamps.

Hermes' native Buzz plugin remains a later simplification experiment, not the selected v1 bridge.

## 2. Hermes → OmniRoute

```yaml
providers:
  factory-router:
    base_url: http://omniroute:20128/v1
    api_mode: codex_responses
    key_env: OMNIROUTE_INTERNAL_API_KEY
    extra_headers:
      x-omniroute-compression: "off"
```

Required assertions:

- Hermes has no upstream provider key and cannot reach public model endpoints.
- A `/v1/responses` request streams text and completes a real Hermes tool-call round trip.
- OmniRoute reports compression off, and a deterministic stub proves request preservation.
- OmniRoute failure does not trigger direct fallback.
- State is persistent; bootstrap secrets are non-default; provider setup is explicit and audited.
- `codex_app_server` and OpenAI Codex OAuth remain disabled.

## 3. Fubuki → Hermes governance

Startup flow:

1. Load reviewed Fubuki sources.
2. Lint with corrected violation/review exit behavior.
3. Compile canonical JSON and compute its hash.
4. Project the immutable runtime governance layer into Hermes.
5. Refuse readiness on invalid/unreviewed packets.

Invariant:

```text
session.governance_hash == sha256(canonical_fubuki_packet)
```

For bounded memory, fetch source records with stable IDs, call `evaluate_records`, join allowed `BoundDecision.record_id` values back to records, and log each reason/rule. Never assume the decision contains the source payload.

## 4. Composite memory provider

Implement one Hermes external `MemoryProvider` named `factory_memory`.

Logical mapping:

| Scope | ai-memory `(workspace, project)` |
|---|---|
| Company | `(factory, _global)` |
| Team | `(factory, team--<team-id>)` |
| Project | `(factory, project--<project-id>)` |
| Agent | `(factory, agent--<agent-id>)` |

Read contract:

1. Authenticate the actor/agent/team/project binding outside model control.
2. Query all authorized scopes.
3. Merge with Agent → Project → Team → Company precedence and deterministic de-duplication.
4. Attach scope, stable ID, timestamp, confidence, and provenance.
5. Apply Fubuki bounds and a hard token/character budget.
6. Return an explicit status. On failure, normal turns degrade visibly; `memory_required` turns fail a separate pre-dispatch health check.

Write contract:

- A system-controlled end-of-turn path may append a sanitized, attributed observation only to the authorized active scope.
- The model, dream worker, generated harness, and evaluator receive no raw approve/delete/purge/promotion tool.
- `_global` writes and all upward promotion require a reviewed companion workflow.
- Retries are idempotent by session/turn/event ID.
- The adapter enforces scope authorization because same-workspace ai-memory tokens are not per-project RBAC.

## 5. Hermes → policy service

Use a Hermes `pre_tool_call` hook with `fail_closed: true`.

```json
{
  "schema_version": 1,
  "session_id": "...",
  "turn_id": "...",
  "tool_call_id": "...",
  "actor": {"buzz_pubkey": "...", "agent": "..."},
  "governance_hash": "sha256:...",
  "tool": "write_file",
  "arguments": {},
  "scope": {"team": "...", "project": "...", "workspace_root": "/workspace"}
}
```

Valid outcomes are `allow`, `deny`, and `modify`. Timeout, connection failure, malformed output, unknown input, or unknown governance hash denies. Any deny wins. Modified arguments are canonicalized and re-evaluated before execution.

## 6. Dream worker proposal contract

Input: immutable, sanitized export containing trace/memory IDs, governance hash, scope metadata, and redaction version.

Output: a proposal bundle containing:

- candidate change and target logical scope;
- quoted evidence with source IDs and verification result;
- rationale, conflicts, uncertainty, and reversibility data;
- worker/generator/model versions and input digest;
- deterministic test results and required human disposition.

The worker cannot directly write ai-memory, execute production tools, or change governance. A system-owned validator re-resolves every source quote and rejects stale/missing evidence before review.

## 7. JIT Foundry candidate contract

Each generation run emits an immutable candidate directory:

```text
candidate/<candidate-id>/
├── memory.py
├── planning.py
├── action.py
├── tool_policy.py
├── prompt.yaml
├── harness-spec.yaml
├── provenance.json
└── evaluation.json
```

`harness-spec.yaml` is first-party metadata describing interfaces, tools, model route, permissions, compatibility, resource limits, and source digests. Generation happens without production secrets/network/write authority. A candidate cannot be executed outside the evaluation sandbox or promoted without passing policy/static/security/behavior gates and signed human review.

The normal promotion target is a versioned Hermes plugin/profile. If the candidate is an approved standalone UHP/Responses-only harness, a separate ADR may activate HarnessRouter.

## 8. Evaluation and telemetry contracts

- AlphaEval-derived tasks run in an isolated network with dedicated credentials and artifacts.
- Deterministic evaluators run before calibrated LLM judges; judges use OmniRoute.
- Rubric code runs separately from the candidate, unprivileged and without secrets.
- PandaProbe, if enabled, ingests redacted common-envelope events only and uses no direct provider credentials.
- Production promotion consumes signed evaluation summaries, never mutable dashboard state.

## 9. Common audit envelope

```json
{
  "schema_version": 1,
  "timestamp": "RFC3339",
  "event_id": "uuid",
  "session_id": "...",
  "turn_id": "...",
  "actor_id": "...",
  "governance_hash": "sha256:...",
  "component": "hermes",
  "event_type": "tool.denied",
  "payload": {},
  "redaction_version": "sha256:..."
}
```

Dream, Foundry, evaluation, and promotion records extend this envelope with immutable input/output digests and lineage IDs.
