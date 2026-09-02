# 07 — Build plan

Implementation is staged so the full plan survives while authority is added only after evidence.

## Stage 0 — proof pack and seam locks

| ID | Proof | Exit evidence |
|---|---|---|
| S0-01 | `buzz-acp` launches pinned `hermes-acp` | ACP initialize/prompt/stream/cancel/shutdown fixture |
| S0-02 | Buzz authorization/freshness | Allowed event succeeds; unauthorized/replayed/stale events fail |
| S0-03 | Hermes→OmniRoute | Text and real tool-call round trip over `codex_responses` |
| S0-04 | Compression contract | Response header plus deterministic stub request preservation |
| S0-05 | No direct model egress | Network canaries fail from every non-OmniRoute unit |
| S0-06 | Four-scope adapter design | Auth tuple, precedence, write-target, and leak fixtures |
| S0-07 | Fubuki corrections | Lint ordering and BoundDecision join tests |
| S0-08 | gVisor compatibility | Hermes root-init/drop and required tools work; escape canaries fail |
| S0-09 | Foundry host decision | JIT five-file translation; OpenHarness extract/integrate/decline ADR |
| S0-10 | GBrain seam decision | Wrap vs adapt spike with proposal-only proof |
| S0-11 | Evaluation hardening | Hermes runner design and rubric isolation proof |
| S0-12 | License/release policy | First-party license, notices, pins, SBOM/update procedure |

## Stage 1 — minimal production spine

- Pinned Buzz relay dependencies following the upstream production shape.
- Pinned `buzz-acp` with explicit Hermes command, args, 900-second idle timeout, turn limit, and authorization.
- Pinned Hermes with ACP support and no Codex/Claude/Pi runtime adapters.
- OmniRoute persistence, secure bootstrap, and one tested `codex_responses` route.
- Common audit envelope, correlation IDs, health/readiness, restart/idempotency.

## Stage 2 — four-scope memory

- ai-memory deployment from `docker/Dockerfile`, scheduler/maintenance off and approval on.
- First-party composite Hermes provider covering Agent, Project, Team, and Company mappings.
- Identity/scope binding, deterministic precedence/de-duplication, Fubuki-bound results, and visible degradation.
- Authorized active-scope staging writes only; no model-callable mutation/promotion/delete tools.
- Cross-scope leakage, retry/idempotency, and sensitive-tenant isolation tests.

## Stage 3 — governance

- Fubuki linter fix/wrapper and complete declared test suite.
- Canonical compile/hash and immutable Hermes governance projection.
- BoundDecision-to-record adapter and negative cases.
- Governance hash attached to ACP sessions, tool events, recalls, writes, and later research artifacts.

## Stage 4 — production security gate

- Deterministic policy service and fail-closed Hermes hook.
- Canonical argument validation and modification re-evaluation.
- Production gVisor profile, mounts, resources, secret filtering, and egress broker.
- External mutation approvals and threat regression suite.

No production pilot exits Stage 4 with a critical failure.

## Stage 5 — GBrain-informed dream phase

- Frozen sanitized trace/memory export with provenance.
- Isolated GBrain wrap/adaptation implementing triage, constrained analysis, quote verification, and proposal creation.
- System-side revalidation, deterministic evaluation, human queue, rejection memory, and supersession/rollback.
- One-level Agent→Project→Team→Company promotion; company always operator-approved.

No dream worker receives ai-memory admin credentials.

## Stage 6 — JIT Harness Foundry

- Pinned/frozen JIT generator and five-file output capture.
- First-party `HarnessSpec` translator, manifest, provenance, and immutable candidate store.
- Static/policy/security gates and hardened AlphaEval-style candidate runner.
- Best-of-N comparison against the stock Hermes baseline.
- Human-signed disposition.

Preferred approved outcome: Hermes plugin/profile. OpenHarness remains a possible host only after the Stage 0 decision. No generated candidate auto-deploys.

## Stage 7 — conditional HarnessRouter and observability

- If an approved standalone candidate is UHP/Responses-only and cannot use ACP, create an ADR and add a pinned, contained HarnessRouter gateway.
- Verify official one-container topology, root-to-session-user lifecycle, session isolation, cleanup, and OmniRoute-only model egress.
- Harden and optionally enable PandaProbe for redacted trace analysis if it adds measurable value.

HarnessRouter and PandaProbe are retained roadmap components, not required core services.

## Stage 8 — hardening and operations

- Load/soak/failure testing, especially OmniRoute long Responses memory use.
- Backup/restore, key rotation, disaster recovery, data retention/deletion, upgrade/rollback drills.
- Pinned-upstream release monitoring and contract-test update workflow.
- Runbooks, SLOs, incident response, and promotion audit review.

## Definition of done

- Buzz→`buzz-acp`→`hermes-acp` operates reliably with explicit authorization and cleanup.
- Hermes is the only stock production runtime; every model request uses OmniRoute.
- Four memory scopes are authorized, attributable, bounded, leak-tested, and visibly degraded on failure.
- Fubuki identity is canonical/hash-pinned across runtime and improvement artifacts.
- Tools fail closed and gVisor/egress tests pass.
- Dream outputs and JIT harnesses remain proposal/candidate artifacts until deterministic and human gates pass.
- AlphaEval-derived suites and optional PandaProbe telemetry meet retention/security requirements.
- HarnessRouter is absent unless a documented approved UHP-only need activates it.

## GitHub milestones

| Milestone | Scope |
|---|---|
| M0 Proof pack | S0-01 through S0-12 |
| M1 Spine | Buzz, `buzz-acp`, ACP, Hermes, OmniRoute |
| M2 Memory | Four-scope provider and isolation |
| M3 Governance | Fubuki compile/bounds/hash |
| M4 Security | Policy, gVisor, egress, approvals |
| M5 Dream | GBrain-informed proposal/promotion workflow |
| M6 Foundry | JIT, candidate schema, AlphaEval gates |
| M7 Expansion | Conditional HarnessRouter, PandaProbe |
| M8 Operations | SLOs, recovery, updates, release readiness |
