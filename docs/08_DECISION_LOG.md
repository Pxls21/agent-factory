# 08 — Decision log

## Accepted

| ID | Decision | Rationale |
|---|---|---|
| D-001 | Hermes is the sole stock production workhorse | Removes duplicate Codex/Claude/Pi execution and policy paths without deleting the surrounding system |
| D-002 | Keep ACP and `buzz-acp`; launch `hermes-acp` | Preserves the intended Buzz integration while using Hermes' native ACP server |
| D-003 | OmniRoute is the sole model/embedding API egress | Centralizes provider credentials, routing, and evidence |
| D-004 | Codex-capable models use Hermes `codex_responses` via OmniRoute | Codex remains a model/backend choice, not another runtime |
| D-005 | Codex app-server/OAuth, Codex CLI, Claude Code, Pi, and their ACP adapters are not stock runtimes | Avoids parallel harness and credential paths |
| D-006 | Preserve Company, Team, Project, and Agent memory as logical scopes | Retains the design goal using an explicit adapter over ai-memory's native model |
| D-007 | The composite memory adapter is an authorization boundary | Same-workspace ai-memory tokens are not native per-project RBAC |
| D-008 | Normal recall degrades visibly; strict workflows preflight | Matches Hermes' non-fatal provider contract honestly |
| D-009 | Tool authorization uses a fail-closed Hermes pre-tool hook | Supported deterministic block/modify seam |
| D-010 | gVisor contains the whole Hermes runtime initially | Honest achievable boundary; per-tool isolation requires a broker |
| D-011 | Retain GBrain-informed dream work as a proposal-only plane | Preserves reflective learning without direct memory-write authority |
| D-012 | Retain JIT and the Harness Foundry | Harness candidates are valuable when isolated, evaluated, and human-promoted |
| D-013 | JIT candidates normally target Hermes plugins/profiles | Keeps Hermes the main workhorse while allowing specialization |
| D-014 | Keep HarnessRouter conditional for approved UHP-only harnesses | Avoids core-path complexity without deleting the Phase 2 option |
| D-015 | Retain AlphaEval as a hardened evaluation lab | Its task/evaluator patterns are useful after runner hardening |
| D-016 | Retain PandaProbe as optional later observability | Preserve the capability subject to egress, credential, and retention proof |
| D-017 | Auto-improve scheduler/maintenance start off; promotion is reviewed | Prevents silent learning, deletion, or cross-scope changes |
| D-018 | Preserve the original v2 documents unchanged | Maintains provenance while current docs apply source corrections |
| D-019 | Advance OmniRoute pin to `488f57e9` (HEAD, v3.8.51) and GBrain pin to `8c70f625` (HEAD, v0.48.2.0) | OmniRoute: the prior pin (`500568a1`) predates GHSA-5926-2w35-7h4q — a credential-export vulnerability where `POST /api/providers/{id}/claude-auth/export` and `.../codex-auth/export` fail open under `requireLogin=false` (the local-first default). The PC's OmniRoute listens on `0.0.0.0:20128`, making this actively relevant. Fix landed at commit `49c4a620` (PR #12600); the new pin includes it. GBrain: the prior pin (`e9a14c9`, v0.48.1.0) missed the `no_key fail-open` fix and storage scope fix shipped in v0.48.2.0. PC action: the owner must upgrade OmniRoute from npm 3.8.48 to at least a git-source build at `488f57e9` — the fix is NOT on npm (latest 3.8.50 predates it). |
| D-020 | ADR 0003 conflict resolved (owner 2026-09-08): the four-logical-scope ADR is v1; `0003-two-durable-memory-scopes.md` marked SUPERSEDED | the seed, the docs and the built adapter (S0-06 lanes M1/M2) bind four scopes; the two-durable text is the same question answered more narrowly, already subsumed by the four-scope mapping onto (workspace, project) pairs — not a layer worth keeping |
| D-021 | ADR 0002 transport amended (owner 2026-09-08): `chat_completions` is the live v1 transport, `codex_responses` permitted per route; every proof asserts and records the mode it observes | the repaired live profiles run chat_completions (handoff 2026-09-05) with no recorded failure of codex_responses; the pinned Hermes supports both with per-provider extra_headers, so the compression-off contract holds in either |
| D-022 | S0-02 live legs (owner 2026-09-08): an S0-02-only pinned extension of S0-01's closed launcher environment carries `RUST_LOG`; the revoked leg's relay membership removal is an owner-run command the coordinator prepares; key rotation stays synthetic-only | S0-01's golden corpus stays valid (its closed set unchanged); the least owner effort per leg; the pinned relay's REST surface has no key rotation |
| D-023 | Vendored kit in review (owner 2026-09-08): a generated source/commit/license manifest for the vendored trees — a Hermes lane job | reviewers skip the vendored trees mechanically; cheaper than splitting the PR stack |
| D-024 | ACCEPTED anchor (owner 2026-09-08): a signed git tag per accepted proof, `accepted/<proof-id>`, verified by the ledger validator | machine-verifiable and owner-only; a ledger line is not |
| D-025 | `assertion_count` deleted from the registry (coordinator 2026-09-08, owner-delegated) | documentation wearing a gate's clothes — AF-AP-66's second instance; no checker reports a count to bind against |
| D-026 | PC lane concurrency widened to NINE lanes at once (owner 2026-09-08 16:4xZ: "widen the bins, fit more lanes") | six ran stably for hours on the repaired runtime; launches stay staggered 60-120 s and the health probe records admission, memory and swap |
| D-027 | The BUILD lane's default route is the LOCAL Qwen3.8-27B (UD-IQ4_XS, June CUDA llama.cpp 00139b6, the 3090) behind OmniRoute — user unit `qwen-builder` on loopback :8080 behind an API-key file, OmniRoute node `qwen-local` + combo `agentfactory-build-local` (local first, the `agentfactory-build` chain as fallback), effort `medium`; the cloud route stays one env away (`HERMES_MODEL=agentfactory-build HERMES_REASONING=ultra`) (owner 2026-09-14: "if it can be done just build it … let's get Qwen to do the heavy lifting"; built + live 2026-09-14 15:4xZ with no owner step) | 23 days of build time lost to cloud quota; the measurement (FINDINGS-LOCAL-BUILDER-QWEN38 §6) showed the whole model + a 262k q4_0 KV resident on the card at 60-87 t/s; rule 3 holds (OmniRoute the sole egress — Hermes never talks to :8080); `medium` measured at ~95 % of xhigh substance for 1/2-1/7 of the thinking, the A/B on real briefs pending (N5k's verdict) |
| D-028 | The VERIFY lane runs on the local Qwen too, alternating with the build lane on the one 262k slot (owner 2026-09-14 16:5xZ: "it does both the build and verify lane and goes back and forth"): combo `agentfactory-verify-local` (local first, the `agentfactory-verify` chain as fallback), effort `xhigh`; on every local route `pc-lane.sh` clamps ultra/max/high to `xhigh`; ONE bounded effort test decides the build default — the N5k brief run at `medium` (the live lane) and again at `xhigh`, both graded by one comparative verify lane on the local route; `xhigh` becomes the build default if it closes more of the brief or `medium`'s report is NOT-READY on blockers `xhigh` avoided (owner: "obviously slower … but if the output quality is better or medium's is not good enough, switch"). **DECIDED 2026-09-15 by the owner ("both perform comparably, medium is faster — medium as the builder and xhigh for analysing the code"): `medium` stays the BUILD default, `xhigh` the VERIFY/analysis effort — the routing as wired. Evidence: medium reached `113 passed` in 4 h 53 m and flagged the false premise at 14 min; xhigh v3 reached `119 passed` in 6 h 41 m on the corrected brief with 48 min before its first write, and v2 spent 2 h 05 m on the premise (A/B data points 1-2). RE-AFFIRMED by the owner 2026-09-15 12:2xZ after the throughput research came back ("I guess we're going to have to deal with speed. Just keep it on medium … the verifier arms will catch anything left"): the comparative verify (VERIFY-N5k) informs the port list, it no longer gates the default; speed is pursued on the lossless levers (the L1 matrix) and never by raising the build effort.** | the cloud verify route is quota-gated the same way the build route was; the Qwen3.8 template accepts only xhigh/medium/low (any other value raises → the request would fall through to the cloud silently); a decision on effort needs the same brief on both settings under the same grader, not a benchmark table |



## Open implementation choices

| ID | Choice | Required evidence |
|---|---|---|
| X-001 | Adapt selected GBrain modules vs wrap pinned repository | Smallest seam that preserves evidence/provenance and proposal-only authority |
| X-002 | First-party minimal harness host vs OpenHarness derivative | Interface fit, licensing, footprint, isolation, and maintenance proof |
| X-003 | Exact JIT→Hermes plugin/profile translation | Reproducible five-file mapping and no semantic/policy loss |
| X-004 | Enable HarnessRouter for a specific candidate | Approved candidate cannot use ACP, UHP conformance, containment ADR |
| X-005 | Enable PandaProbe | Measured telemetry gap, safe redaction/retention, OmniRoute-only judges |
| X-006 | Shared ai-memory workspace vs stronger tenant separation | Threat classification and cross-scope authorization tests |
| X-007 | Native Hermes Buzz plugin as future simplification | Demonstrated parity and approved change to the `buzz-acp` contract |

## Owner inputs still needed

1. First-party license: Apache-2.0 or MIT.
2. Initial deployment target and Docker `runsc` availability.
3. Initial Buzz relay/community and exact authorized users/channels.
4. First OmniRoute provider/model route and budget.
5. Default degradation policy for normal conversations when memory is unavailable.
