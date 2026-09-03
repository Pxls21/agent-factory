---
topic: project-overview
last_compiled: 2026-09-03
---

# Project Overview — governed agent system, planning stage

## 1. Purpose [coverage: high -- 13 sources]

Agent Factory is the planning repository for a governed, memory-aware agent system built around
**Hermes Agent as the sole stock production workhorse**. The live pipeline:
people in Buzz --> `buzz-acp` --> Hermes native ACP server --> every model request through
OmniRoute --> approved models, with Fubuki supplying hash-pinned governance, ai-memory supplying
four logical memory scopes through a first-party composite adapter, and every tool call passing a
fail-closed policy gate inside gVisor containment. A separate improvement plane
(GBrain-informed dream cycles, JIT Harness Foundry, isolated AlphaEval/PandaProbe evaluation,
human promotion gate) feeds reviewable proposals only; it has no production write or execution
authority until later gates pass.

**No application code exists.** The repository contains reviewed architecture, integration
contracts, security boundaries, the complete component audit, configuration examples, upstream
pins, and the Stage 0 proof pack contract. The Stage 0 build is IN PROGRESS (increment #1 done, #2 in progress, frozen for review fixes on 2026-09-03); the first pending
increment is `s0-01-registry-schemas-validator`.

## 2. Architecture [coverage: high -- 8 sources]

The system spans two planes (production and improvement) with ten ownership areas:

| Plane | Components | Responsibility |
|---|---|---|
| Interaction | Buzz relay, `buzz-acp`, ACP | Human collaboration, transport |
| Runtime | Hermes Agent | Conversation, planning, tool orchestration |
| Model routing | OmniRoute | Sole model/embedding API egress |
| Governance | Fubuki | Canonical persona/governance packet, bounds, lint, hash |
| Memory | ai-memory + composite adapter | Four logical scopes, provenance, staging, promotion |
| Tool security | Policy service + gVisor | Fail-closed authorization and runtime containment |
| Dream/learning | GBrain-informed worker | Offline reflection, evidence, reviewable proposals |
| Harness Foundry | JIT + adapters + optional OpenHarness | Generate candidate harness bundles |
| Evaluation | AlphaEval, PandaProbe | Isolated acceptance tests, trajectory analysis |
| Conditional access | HarnessRouter | Phase 2 UHP bridge for approved non-ACP harnesses |

Key files: [docs/01_ARCHITECTURE.md](docs/01_ARCHITECTURE.md) (production and improvement
topologies), [docs/02_COMPONENT_AUDIT.md](docs/02_COMPONENT_AUDIT.md) (the verified
inventory -- read FIRST, corrects the v2 plan),
[docs/07_BUILD_PLAN.md](docs/07_BUILD_PLAN.md) (six-stage backlog).

## 3. Talks To [coverage: high -- 6 sources]

Every component in the production plane depends on the layer below it:

- Buzz users --> Buzz relay --> `buzz-acp` (launches `hermes-acp`)
- Hermes --> OmniRoute (sole model egress; `codex_responses` provider mode)
- Hermes <--> four-scope memory adapter <--> ai-memory
- Hermes --> fail-closed policy gate (pre_tool_call hook) --> gVisor containment
- Fubuki packets injected into Hermes context assembly

The improvement plane reads sanitized exports and writes proposals only:
- Dream worker --> immutable sanitized snapshots --> proposals
- JIT --> candidate harness bundles --> evaluation --> human promotion gate

Integration contracts: [docs/03_INTEGRATION_CONTRACTS.md](docs/03_INTEGRATION_CONTRACTS.md).

## 4. API Surface [coverage: medium -- 4 sources]

No runtime API exists (no application code). The planned surface is defined by contracts:

- ACP protocol: initialize, prompt, streaming, cancellation, terminal states, shutdown
  ([docs/03_INTEGRATION_CONTRACTS.md](docs/03_INTEGRATION_CONTRACTS.md) SS1)
- OmniRoute: `/v1` endpoint, `codex_responses` mode, `x-omniroute-compression: off` header
- Memory adapter: auth tuple `(workspace, project)` mapped to four logical scopes
- Policy service: deny-before-allow CEL-compatible engine, every decision includes governance hash
- Configuration: [.env.example](.env.example) names all planned env vars (values are
  placeholders)

## 5. Data [coverage: medium -- 3 sources]

No persisted runtime data exists. Planned stores:

- ai-memory: `(factory, _global)` (Company), `team--<id>`, `project--<id>`, `agent--<id>`
- Fubuki: canonical JSON governance packets, hash-pinned per session
- Proof artifacts: `proofs/<s0-NN>/result.json` (Stage 0 runner output with digests)
- Common audit envelope: schema_version, session/turn ids, governance_hash, event_type, payload

Existing on-disk artifacts: `spikes/pc-bridge/result.json` (spike #0, the only completed
increment), `upstream.lock.yaml` (pinned upstream commits).

## 6. Key Decisions [coverage: high -- 8 sources]

All from [docs/08_DECISION_LOG.md](docs/08_DECISION_LOG.md) and `docs/adr/`:

- **D-001 / ADR 0001:** Hermes sole runtime; Codex/Claude/Pi removed as parallel workhorses
- **D-002:** ACP retained; `buzz-acp` launches `hermes-acp`
- **D-003 / ADR 0002:** OmniRoute sole model API egress; no direct provider credentials elsewhere
- **D-006 / ADR 0003:** Four logical memory scopes composed over ai-memory's native `(workspace, project)`
- **D-009:** Fail-closed `pre_tool_call` hook for tool authorization
- **D-010:** gVisor contains the whole Hermes runtime initially (not per-tool)
- **D-011 / ADR 0004:** Dream and JIT Foundry isolated as proposal/candidate planes
- **D-017:** Auto-improve scheduler/maintenance off; promotion reviewed

Open implementation choices X-001 through X-007 and five owner inputs (license, deployment
target, Buzz community, first OmniRoute route, degradation policy) remain unresolved.

Council verdict (2026-09-02): unanimously adopted **wave-plan-v2** for Stage 0 execution --
three-way (later four-way) proof classification, capability spikes before proof work, Wave-0/1/2
ordering by falsification power. Seven kill criteria KC-1..KC-7 gate the build.

## 7. Gotchas [coverage: high -- 10 sources]

**NOT-built (first-class):**
- No application code for the spine exists -- STATUS.md: Stage 0 MACHINERY in progress (registry, schemas, validator, proof runner, probe-backed markers)
- No production container, Compose deployment, provider credentials, or live smoke test
- No Hermes Fubuki extension, composite memory adapter, policy service, or evaluation runner
- No JIT, GBrain worker, HarnessRouter integration, or PandaProbe deployment
- The Stage 0 proof pack (1 of 18 increments closed — #1; #2a landed; spike #0 done,
  `pc-bridge` liveness probe)
- The wiki (this file) is compiled from planning docs, not from code

**Stage 0 build status (four-way classification per council verdict -- never a flat N/12):**
- Execution proofs: 0 complete of 7 planned (S0-01/02/03/06/07 + S0-04/11)
- Conformance-checked decisions: 0 complete of 3 planned (S0-09/10/12)
- Blocked on external input: 0 resolved (formerly S0-03, now reclassified after PC probe)
- Blocked on capability: 1 remaining (S0-08 pending runsc install on the PC)

**Known blockers and risks:**
- gVisor (runsc) absent on the PC; KVM modules unloaded (owner `sudo modprobe kvm_amd`)
- `podman-compose` absent on the PC (but buzz-prod containers exist via some compose path)
- No real upstream model credential configured yet in OmniRoute (local vLLM `sim9b` available)
- The Rust toolchain on the PC has 1.95.0 via rustup, but ai-memory build is unproven
- Security blockers listed in [SECURITY.md](SECURITY.md): policy hook, gVisor deployment,
  memory restrictions, Buzz revocation, sandbox hardening -- all absent

**Anti-pattern registry:** `docs/INCIDENT-LOG.md` carries AF-AP-1 through AF-AP-5 (total
isolation as selective egress, collective reference satisfying per-item gate, uncommitted work at
dispatch boundary, sandbox-probe-as-world, orphaned lines past top-level exit).

## 8. Sources

- [README.md](README.md)
- [STATUS.md](STATUS.md)
- [CLAUDE.md](CLAUDE.md)
- [AGENTS.md](AGENTS.md)
- [SECURITY.md](SECURITY.md)
- [docs/01_ARCHITECTURE.md](docs/01_ARCHITECTURE.md)
- [docs/02_COMPONENT_AUDIT.md](docs/02_COMPONENT_AUDIT.md)
- [docs/07_BUILD_PLAN.md](docs/07_BUILD_PLAN.md)
- [docs/08_DECISION_LOG.md](docs/08_DECISION_LOG.md)
- [docs/09_PREMORTEM.md](docs/09_PREMORTEM.md)
- [docs/adr/0001-hermes-only-runtime.md](docs/adr/0001-hermes-only-runtime.md)
- [docs/adr/0004-isolated-improvement-planes.md](docs/adr/0004-isolated-improvement-planes.md)
- [todo/BUILD-TASKLIST.md](todo/BUILD-TASKLIST.md)
