# 05 — Security and containment

## 1. Objectives

1. A model, generated harness, or dream worker cannot bypass human authorization to cause effects.
2. All model/embedding API traffic goes through OmniRoute.
3. Compromised runtime and research code is contained from host, other scopes, secrets, and unrestricted egress.
4. Inbound/recalled/generated content cannot silently become governance.
5. Memory and harness promotion is attributable, tested, reviewable, and reversible.
6. ACP, evaluation, and observability boundaries fail safely.

## 2. Threat model

| Threat | Prevention | Detection/recovery |
|---|---|---|
| Unauthorized or replayed Buzz event | Allowlist/membership, signature, independent freshness, cursor/de-duplication | Denial/replay event and key rotation |
| `buzz-acp` process/session abuse | Pinned command, fixed args, turn/idle limits, no shell interpolation | ACP lifecycle audit and forced cleanup tests |
| Prompt injection from Buzz/web/memory | Trust-labeled context, immutable Fubuki layer, tool gate | Injection canaries and denied-tool traces |
| Model invents dangerous arguments | Canonical validation, deny by default, modified-arg re-evaluation | Versioned decision log |
| Policy outage/malformed result | Hermes fail-closed pre-tool hook | Availability alert and explicit denial reason |
| Direct model egress | No upstream keys, network enforcement | DNS/connection canaries and egress logs |
| Four-scope memory leak | Authenticated scope tuple, adapter enforcement, least privilege | Cross-scope honeytokens and query pack |
| Dream worker writes directly | Sanitized export, no admin token, proposal-only API | Credential scan and immutable proposal lineage |
| Generated harness auto-deploys | Separate artifact store, no production credentials, signed promotion | Promotion ledger and deployment allowlist |
| Malicious JIT/evaluator/rubric code | gVisor, no host network/secrets, read-only inputs, separate evaluator | Ephemeral teardown, escape/exfiltration tests |
| HarnessRouter expands attack surface | Absent until approved ADR; pinned single-gateway deployment | Conformance/containment review at activation |
| PandaProbe leaks trace/secrets | Redaction before ingestion, private storage, scoped access | Redaction canaries and retention audits |
| Supply-chain drift | Commit/digest pins, SBOM/signature rules, update PRs | Pin-drift CI and upstream release review |

## 3. Policy semantics

The first-party decision service may use a small language or CEL-compatible engine, but must implement:

- deny before allow; any deny wins;
- broken deny rule denies;
- broken allow grants nothing;
- no match/unknown input denies;
- canonical modified arguments are evaluated again;
- every decision includes its policy and governance hashes.

OpenBot is a semantics reference, not a deployable policy service.

## 4. Tool and action classes

| Class | Examples | Default posture |
|---|---|---|
| Local read | Read/list files | Allow inside explicit roots |
| Local mutation | Write/patch/move/delete | Deny until path/operation policy allows |
| Process | Shell/test/compiler | Deny; allow constrained command/cwd/time/resource sets |
| Network read | HTTP/web/search | Allowlisted broker; block metadata/private/link-local targets |
| External mutation | Git push, issue, message | Explicit action approval and scoped broker credential |
| Credential operation | Sign, retrieve secret | Never model-visible; broker one narrow operation |
| Memory mutation | Stage/promote/approve/delete | System staging only; promotion/delete operator workflows |
| Harness promotion | Register/activate candidate | Signed human approval after recorded gates |

## 5. Containment profiles

### Production Hermes

Run the entire Hermes runtime under `runsc`. Validate root-start/s6 setup, privilege drop to `hermes`, required tools, narrow mounts, no Docker socket/home/provider secrets, resource limits, and enforced egress. This is whole-runtime containment, not per-tool isolation.

### Dream and Foundry workers

Use separate gVisor profiles with immutable sanitized inputs, scratch-only writes, no production network, no production credentials, strict CPU/memory/time/process limits, and artifact-only output. Destroy the worker after each job.

### Candidate/evaluation runners

Separate candidate execution from evaluator/rubric execution. Neither receives production credentials or network membership. Evaluators consume exported artifacts rather than sharing the candidate's writable workspace.

### Conditional HarnessRouter

Do not deploy until an approved candidate requires UHP. At activation, verify the official one-container topology, root-to-session-user privilege drop, UHP request semantics, session isolation, resource cleanup, and model egress through OmniRoute.

## 6. Network segmentation

| Source | Allowed destinations |
|---|---|
| `buzz-acp` | Buzz relay and local/private `hermes-acp` endpoint/process only |
| Hermes | OmniRoute, composite memory adapter, policy, approved tool broker |
| Memory adapter | ai-memory and audit sink |
| ai-memory | OmniRoute only when explicitly enabled for embeddings/consolidation |
| OmniRoute | Approved model providers and persistence dependencies |
| Dream/Foundry/candidate/evaluator | Isolated test services and artifact sink only |
| PandaProbe | Redacted telemetry sink and OmniRoute if reviewed judge/repair is enabled |
| HarnessRouter (conditional) | Approved harnesses and OmniRoute only |

## 7. Secrets

- OmniRoute alone owns upstream provider credentials.
- Hermes owns a scoped OmniRoute key; Buzz identity/relay credentials remain in the interaction boundary.
- The composite adapter owns scope-limited memory access; ai-memory admin credentials stay operator-only.
- Dream, JIT, candidates, and rubrics receive synthetic/dedicated test credentials only.
- PandaProbe receives no provider key; any model call uses a scoped OmniRoute key.
- Secrets are removed before child-process environments and redacted before durable logging.

## 8. Release-blocking tests

- Unauthorized/stale/replayed Buzz events cannot start an ACP turn.
- ACP cancellation/timeouts clean up Hermes processes/sessions.
- Policy crash, timeout, invalid JSON, and unknown tool block execution.
- Path traversal, symlink escape, and alternate spellings cannot leave the workspace.
- Hermes, ai-memory, dream, JIT, evaluator, PandaProbe, and conditional HarnessRouter cannot reach providers directly.
- Cross-agent/project/team/company canaries never appear outside authorized recall.
- Stored prompt injection cannot override Fubuki or cause an unapproved tool call.
- Dream output cannot mutate ai-memory; generated candidates cannot reach deployment storage.
- gVisor host-read/escape and evaluation exfiltration canaries fail.
