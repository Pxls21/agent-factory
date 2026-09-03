---
topic: evaluation-and-improvement
last_compiled: 2026-09-03
---

# Evaluation and Improvement — AlphaEval, dream phase, JIT Foundry

## 1. Purpose [coverage: high -- 6 sources]

The improvement plane generates proposals (dream cycles) and candidate harnesses (JIT Foundry),
evaluates them in isolation (AlphaEval, PandaProbe), and promotes only after deterministic tests,
security veto, and human review. It has no direct production write or execution authority.

**Nothing in this plane has been built.** The architecture, workflow, and hardening requirements
are specified; S0-09 (Foundry host decision), S0-10 (GBrain seam decision), and S0-11
(evaluation hardening) are the relevant Stage 0 proofs.

## 2. Architecture [coverage: high -- 5 sources]

**JIT Harness Foundry** (MIT, [docs/10_HARNESS_FOUNDRY.md](docs/10_HARNESS_FOUNDRY.md)):
generates five source files (`memory.py`, `planning.py`, `action.py`, `tool_policy.py`,
`prompt.yaml`) plus a first-party `HarnessSpec` manifest and provenance. Includes best-of-N
generation, selection, and evaluation. Not ACP-native or OpenHarness-specific. Runs in a
no-secret/no-production-network sandbox.

**GBrain-informed dream phase** (MIT, v0.48.1.0,
[docs/11_DREAM_PHASE.md](docs/11_DREAM_PHASE.md)): LLM triage, constrained subagents,
orchestrator-controlled validation/writes, quote verification, provenance, reverse writing.
GBrain is a full knowledge system, not an ai-memory extension. The dream worker reads sanitized
snapshots, produces proposals only, and never receives ai-memory admin credentials.

**AlphaEval** (MIT, 94 tasks, 7 companies, 6 domains): full-agent task structure and mixed
evaluators. Stock runner is UNSAFE: host networking, recursive chmod 777, credential passing,
rubric subprocesses in the workspace. Required hardening: Hermes/candidate runner, rubric
isolation, no production secrets, gVisor sandbox, pinned images, OmniRoute-only judge calls.

**PandaProbe**: trace analysis and evaluation. Retained as optional later observability.
Requires redaction before ingestion, private storage, scoped access. Not deployed.

**OpenHarness** (MIT, v0.1.9): a complete standalone harness, not a minimal skeleton. Stage 0
must decide: extract patterns, build minimal first-party host, or integrate pinned derivative.

**HarnessRouter** (Apache-2.0): one-container UHP gateway. Conditional on an approved non-ACP
harness. Not on the core path. Activation requires a separate ADR.

## 3. Talks To [coverage: medium -- 4 sources]

- Dream worker --> sanitized trace/memory export (immutable, read-only)
- Dream worker --> proposal bundle --> system validator --> deterministic + AlphaEval tests
- JIT --> candidate harness bundle --> evaluation --> human promotion gate
- AlphaEval runners --> isolated gVisor, no host network, no production credentials
- Approved candidate --> Hermes plugin/profile (normal path)
- HarnessRouter --> conditional, only for approved UHP-only harness

## 4. API Surface [coverage: low -- 2 sources]

All planned, nothing implemented:
- JIT: five-file output + manifest + provenance
- Dream worker: proposal bundle format (evidence, provenance, verification)
- AlphaEval: task pack shape (`evals/tasks/<task-id>/` with task.yaml, prompt.md, inputs,
  expected, evaluators, fixtures)
- Promotion: signed human approve/reject decision, supersession/rollback

## 5. Data [coverage: low -- 2 sources]

- Dream worker: immutable sanitized snapshots (input), proposal bundles (output)
- JIT: candidate harness bundles in separate artifact store
- AlphaEval: task/input/output/runner digests (immutable)
- PandaProbe: trace data with pre-ingest redaction

## 6. Key Decisions [coverage: high -- 5 sources]

- D-011/ADR 0004: dream and Foundry isolated as proposal/candidate planes
- D-012: retain JIT and Foundry (valuable when isolated, evaluated, promoted)
- D-013: JIT candidates normally target Hermes plugins/profiles
- D-014: HarnessRouter conditional for approved UHP-only harnesses
- D-015: retain AlphaEval as hardened evaluation lab
- D-016: retain PandaProbe as optional later observability
- X-001 (open): adapt GBrain modules vs wrap pinned repository
- X-002 (open): first-party minimal host vs OpenHarness derivative
- X-003 (open): exact JIT-to-Hermes plugin translation
- X-004 (open): HarnessRouter activation for a specific candidate

## 7. Gotchas [coverage: high -- 5 sources]

**NOT-built (first-class):**
- No JIT runner, no dream worker, no AlphaEval hardened runner
- No rubric isolation, no gVisor evaluation profile
- No PandaProbe deployment, no trace redaction
- No HarnessRouter (conditional, no approved candidate exists)
- No OpenHarness decision (S0-09 pending)
- No GBrain seam decision (S0-10 pending)

**Safety critical:**
- AlphaEval stock runner uses host networking, chmod 777, and passes credentials --
  UNSAFE and not approved
- Dream worker must never receive ai-memory admin credentials or production tool access
- Generated harness security veto must be independent of aggregate quality score
  (premortem #7)
- Rubric/judge model calls must use OmniRoute (never direct provider)

## 8. Sources

- [docs/10_HARNESS_FOUNDRY.md](docs/10_HARNESS_FOUNDRY.md)
- [docs/11_DREAM_PHASE.md](docs/11_DREAM_PHASE.md)
- [docs/06_EVALUATION.md](docs/06_EVALUATION.md)
- [docs/02_COMPONENT_AUDIT.md](docs/02_COMPONENT_AUDIT.md)
- [docs/adr/0004-isolated-improvement-planes.md](docs/adr/0004-isolated-improvement-planes.md)
- [docs/09_PREMORTEM.md](docs/09_PREMORTEM.md)
