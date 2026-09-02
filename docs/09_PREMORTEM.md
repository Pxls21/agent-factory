# 09 — Pre-mortem

Assume the pilot failed. These are the most likely causes by combined impact and likelihood.

| Rank | Failure mode | Early signal | Prevention / trigger |
|---:|---|---|---|
| 1 | ACP bridge and `hermes-acp` disagree on lifecycle/streaming | Turns hang, cancel poorly, or duplicate | Pinned conformance pack for initialize/stream/cancel/shutdown/idempotency |
| 2 | OmniRoute works for text but corrupts/drops tool calls | Text test passes; tool args change or hang | Real tool round-trip and deterministic gateway fixture |
| 3 | Four-scope adapter leaks data | Team/agent canary appears in another scope | Auth tuple, deny-by-default adapter, honeytoken suite, stronger tenant split |
| 4 | Memory silently disappears | Answers ignore known facts without a status | Visible degraded marker and strict-workflow preflight |
| 5 | Dream worker becomes a hidden writer | Proposal job changes ai-memory directly | No admin token/network route; artifact-only output; credential tests |
| 6 | JIT candidate reaches production without adequate review | Generated code appears in deploy branch/image | Separate candidate store, signed promotion allowlist, no deploy token |
| 7 | Generated harness passes quality but violates security | Score improves while egress/tool policy regresses | Critical security veto independent of aggregate score |
| 8 | Policy outage fails open | Tool executes during timeout/crash | `fail_closed: true`; crash/timeout/malformed tests |
| 9 | Buzz revocation relies on author timestamp | Removed user still starts turns | Independent membership/key/freshness enforcement |
| 10 | ai-memory learns/deletes without review | Unexpected scope changes or missing records | Scheduler/maintenance off, approval on, no model mutation tools |
| 11 | Fubuki gate reports wrong severity or joins wrong record | Review masks violation or memory mismatch | Linter ordering and BoundDecision join regression tests |
| 12 | gVisor incompatibility causes bypass | Developers switch to default runtime | Target-host proof; no waiver without ADR |
| 13 | Direct provider path returns during debugging | Upstream key in a non-OmniRoute service | Secret ownership rule, egress deny, recurring canaries |
| 14 | AlphaEval/rubric compromises host or secrets | Runner uses host network/777/shared env | Separate gVisor candidate/evaluator, minimal UID/GID, test credentials |
| 15 | HarnessRouter is introduced as a generic router | Extra gateway exists with no approved UHP candidate | Conditional ADR gate and absence test in core deployment |
| 16 | PandaProbe exposes sensitive traces | Secrets appear in dashboard/storage | Pre-ingest redaction canaries, access/retention controls |
| 17 | OmniRoute OOMs on long concurrent Responses | Restarts during realistic coding runs | Measured concurrency profile and resource sizing |
| 18 | Upstream drift invalidates assumptions | Release update changes env/API/security | Immutable pins, monitored releases, contract-test PRs |
| 19 | Audit evidence cannot link runtime, dream, candidate, and promotion | Hash/IDs diverge across systems | Common envelope and lineage tests before dashboards |
| 20 | Project stalls under full-stack scope | Many partial services; no thin working path | Staged milestones with Hermes spine first and isolated parallel research |

## Stop-the-line conditions

Pause deployment or promotion if:

- an unauthorized/stale/replayed Buzz event starts an ACP turn;
- a tool executes without a valid allow decision;
- any component reaches a model provider without OmniRoute;
- memory crosses Agent/Project/Team/Company authorization boundaries;
- a dream worker mutates production memory;
- a generated harness is deployed without a signed gate record;
- a company memory changes without operator evidence;
- a governance hash is missing or changes inside a session/artifact chain;
- a secret appears in a subprocess, trace, memory, dream, Foundry, or evaluation artifact;
- production or research containment is bypassed.

## Incident template

```text
ID / title:
Detected at:
Impact and affected scopes:
Session / ACP / proposal / candidate IDs:
First bad event ID:
Governance and policy hashes:
Runtime and upstream pins:
Containment actions:
Root cause:
Corrective tests:
Recovery / rollback / supersession evidence:
Owner and due date:
```
