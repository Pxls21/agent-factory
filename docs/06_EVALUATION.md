# 06 — Evaluation and observability

## 1. Purpose

Evaluation protects both the Hermes production baseline and the retained improvement plane. Every memory proposal, harness candidate, model-route update, governance change, or optional HarnessRouter activation needs evidence against the same versioned task and security packs.

## 2. AlphaEval role

[AlphaEval](https://github.com/GAIR-NLP/AlphaEval) supplies useful full-agent task structure and mixed evaluator patterns. The inspected repository contains 94 tasks spanning seven companies and six domains. It remains in the plan as the basis of an isolated lab, not as a production service.

Required hardening:

- add Hermes and Foundry-candidate runners;
- remove host networking and recursive `chmod 777`;
- never pass production provider credentials to a runner;
- run rubric code in a separate unprivileged gVisor sandbox;
- pin images/installations and review dataset licenses;
- route every judge call through OmniRoute;
- preserve immutable task/input/output/runner digests.

## 3. Task pack shape

```text
evals/tasks/<task-id>/
├── task.yaml
├── prompt.md
├── inputs/
├── expected/
├── evaluators/
│   ├── deterministic.py
│   ├── policy_assertions.yaml
│   └── rubric.json
└── fixtures/
```

Run deterministic assertions first. Use LLM judges only for dimensions that cannot be adequately measured deterministically, calibrate them against human labels, and record the OmniRoute route/model/version.

## 4. Evaluation layers

| Layer | Subject | Required evidence |
|---|---|---|
| Seam conformance | ACP, Responses, memory, Fubuki, policy | Protocol fixtures, error behavior, stable hashes |
| Security | Runtime and all research workers | Denial, escape, egress, secret, scope-leak tests |
| Baseline quality | Stock Hermes configuration | Task success, tool reliability, cost/latency/resource profile |
| Dream proposal | Memory candidate | Quote/evidence verification, leakage/injection/regression delta |
| Harness candidate | JIT output/host adapter | Static policy, interface contract, sandbox, task delta vs Hermes |
| Route/update | Upstream/model change | Full affected seam/task/security packs |
| Promotion | Memory/harness release | Signed summary, owner, rollback/supersession plan |

## 5. Harness Foundry gates

A JIT candidate is rejected unless it has:

1. all five expected generator files plus valid `harness-spec.yaml` and provenance;
2. no secret literals, dynamic unreviewed downloads, or undeclared network destinations;
3. successful static analysis and policy semantics tests;
4. successful isolated execution/resource cleanup;
5. no critical security regression;
6. a measured task-pack benefit or clearly documented specialist value relative to Hermes;
7. a human-signed decision describing whether it becomes a Hermes plugin/profile, stays research-only, or requires a HarnessRouter ADR.

Generated code never receives a production deployment token.

## 6. Dream/promotion gates

- Re-resolve every quoted source ID against the frozen input export.
- Reject invented, stale, conflicting, or out-of-scope evidence.
- Test stored-prompt-injection and cross-scope leakage.
- Measure target-task benefit and unaffected-task regressions.
- Require one-level upward promotion and explicit company-level operator approval.
- Retain rejection reason and candidate lineage so the same bad proposal is not repeatedly rediscovered.

## 7. PandaProbe role

PandaProbe remains an optional trace/observability and analysis layer after the common event envelope works. Before enabling it:

- pin images instead of `latest` and replace default credentials;
- define redaction and retention before ingestion;
- isolate it from production mutation paths;
- route judge/repair model calls through OmniRoute;
- prove it adds value beyond native metrics and AlphaEval artifacts.

Dashboards are advisory. Promotion gates consume immutable signed results, not a dashboard verdict.

## 8. Minimum scorecard

Track task success, deterministic assertion pass rate, critical security failures, unauthorized tool attempts, ACP error/cleanup rate, memory precision/leakage, dream acceptance/regression rate, candidate uplift vs Hermes, latency, token/model cost, peak memory, and reproducibility by digest.

Any critical security regression is an automatic failure regardless of aggregate quality score.
