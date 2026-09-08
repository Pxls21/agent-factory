# MATERIAL PACK — S0-02 (Buzz authorization / freshness)

> EVIDENCE ONLY. Verbatim extraction + located inventory. No design, no judgement, no
> recommendation. Assembled 2026-09-07 from the working tree at branch
> `claude/soundbox-kit-migration-iz1jwf`, HEAD `cc46704` (`git log --oneline -1`). Other lanes
> hold uncommitted edits; every quote below is from the tree as read this session, and every
> `file:line` is from that read.
> **This pack carries the §7 CLASS PREFLIGHT verbatim for all six packs; material-S0-03/04/05/06/08
> reference it rather than repeat it.**

---

## 0. INVENTORY TABLE

| item | source file:line | exists? | venue |
|---|---|---|---|
| Seed per-proof block S0-02 | `seeds/seed-stage0-v1.yaml:362-381` | yes | — |
| Seed `spike_to_class_mapping` entry for S0-02 | `seeds/seed-stage0-v1.yaml:564-586` / `proofs/registry.yaml:29-35` | **no** — S0-02 appears in no mapping rule (`spike_dependency: []`, seed:367) | — |
| Breakdown increment #8 | `tasks/stage0-breakdown.md:59` | yes | in-sandbox (row) / PC (venue update) |
| Breakdown venue update | `tasks/stage0-breakdown.md:28-38` | yes | PC |
| Findings per-proof constraint | `docs/research/FINDINGS-STAGE0-v1.md:43` | yes | — |
| Council kill criteria touching S0-02 | `docs/research/COUNCIL-VERDICT-STAGE0-v1.md:36,37,59` | yes | — |
| Plan-doc seam: acceptance tests | `docs/03_INTEGRATION_CONTRACTS.md:5-29` | yes | — |
| Plan-doc seam: NIP-OA / revocation | `docs/02_COMPONENT_AUDIT.md:36-43` | yes | — |
| Plan-doc seam: release-blocking test | `docs/05_SECURITY.md:98` | yes | — |
| upstream pin `buzz` | `upstream.lock.yaml:16-20` | yes | — |
| upstream pin `agent-client-protocol` | `upstream.lock.yaml:5-9` | yes | — |
| upstream pin `hermes-agent` | `upstream.lock.yaml:10-15` | yes | — |
| `proofs/S0-02/` directory | — | **no** (`ls proofs/` → S0-01, S0-03, S0-07, S0-08, S0-09, S0-10, S0-11, S0-12 only) | — |
| `proofs/S0-02/spec.json` | — | **no** | — |
| `proofs/S0-02/result.json` | — | **no**; ledger state `ABSENT` (`proofs/ledger.json`) | — |
| Fixtures `fixtures/s0-02/*` | seed:376-379 names five paths | **no** — no `fixtures/` tree at repo root; `find . -path ./sandbox-kit -prune -o -name 'neg-unauthorized*'` → none | — |
| Registry entry S0-02 | `proofs/registry.yaml:13` | yes | — |
| Result schema S0-02 must satisfy | `proofs/schemas/result.schema.json:1-67` | yes | — |
| Spec schema S0-02 must satisfy | `proofs/schemas/spec.schema.json:1-44` | yes | — |
| Minted EXECUTION exemplar S0-07 | `proofs/S0-07/spec.json`, `proofs/S0-07/result.json` | yes | sandbox |
| Minted EXECUTION exemplar S0-11 | `proofs/S0-11/spec.json`, `proofs/S0-11/result.json` | yes | sandbox |
| Minted DECISION exemplar S0-09 | `proofs/S0-09/spec.json`, `proofs/S0-09/result.json` | yes | sandbox |
| Runner mint path | `scripts/proof-runner:131-223` | yes | either |
| Validator checks | `scripts/validate-ledger:82-205, 216-342, 396-478` | yes | either |
| Reusable Nostr signer/verifier | `proofs/S0-01/tools/nostr_verify.py` (9 defs, see §5.6) | yes | either |
| Reusable signed relay-event fixtures | `proofs/S0-01/fixtures/relay-events-2026-09-05.json` | yes | either |
| Reusable identity fixture (owner/agent/relay/user2) | `proofs/S0-01/fixtures/identities.json` | yes | either |
| Reusable PC relay-stack scripts | `proofs/S0-01/tools/pc/` (8 scripts) | yes | PC |
| Wave-0 spike bearing on S0-02 | — | **no spike names S0-02** (`spikes/*/result.json` `classification_effect` list S0-03/05/06/08 only) | — |
| Blocked marker for S0-02 | — | **no** (S0-02 is `execution_proof`) | — |
| Ledger task row | `todo/BUILD-TASKLIST.md:65` (`s0-08-s0-02-buzz-auth … pending`) | yes | — |

---

## 1. THE SEED — per-proof block and mapping

### 1.1 `seeds/seed-stage0-v1.yaml:362-381` (verbatim)

```yaml
- proof_id: S0-02
  classification: execution_proof
  wave: 1
  increment_index: 8
  ledger_denominator: execution
  spike_dependency: []
  fixture_format: four SEPARATE committed negative Buzz-event fixtures plus one positive,
    each negative carrying its own expected_failure block in-file
  assertions:
  - an allowed fresh signed event produces exactly one ACP session/turn
  - membership removal or key rotation revokes access independent of NIP-OA created_at
  - restart/duplicate delivery does not duplicate a completed turn (idempotency by event id)
  negative_control:
    fixtures:
    - {fixture: fixtures/s0-02/neg-unauthorized.json, expected_failure_reason: 'denied: sender-not-in-allowlist'}
    - {fixture: fixtures/s0-02/neg-bad-signature.json, expected_failure_reason: 'denied: signature-invalid'}
    - {fixture: fixtures/s0-02/neg-replayed.json, expected_failure_reason: 'denied: event-replayed'}
    - {fixture: fixtures/s0-02/neg-stale.json, expected_failure_reason: 'denied: event-stale'}
    rule: four DISTINCT reasons required; one blanket rejection fails the proof
  owner_placeholder: none
```

### 1.2 Frozen `spike_to_class_mapping` entry for S0-02

**NOT SPECIFIED in `seeds/seed-stage0-v1.yaml`** — the frozen block (`:564-586`) declares rules only
for `rust-ai-memory`, `runsc`, `dockerd`, `selective-egress`; `proofs/registry.yaml:29-35` adds
`pc-bridge`. No rule's `affected_proof` is `S0-02`, and the seed's own S0-02 block carries
`spike_dependency: []` (seed:367), matching `proofs/registry.yaml:13`
(`"spike_dependencies": []`).

### 1.3 Seed constraints that bind this proof (`seeds/seed-stage0-v1.yaml:100-122`, verbatim excerpts)

```yaml
- Execution proofs are exactly S0-01, S0-02, S0-04, S0-05-mechanism, S0-07, S0-11;
  conformance-checked decisions are exactly S0-09, S0-10, S0-12
- Every proof ships a spec-time negative control that fails for a named exact reason
- All gates are deterministic and LLM-free; no LLM judge anywhere in the gate spine
- Every acceptance criterion is either executable in this environment or explicitly
  deferred with a machine-checkable reason
- Upstream components stay commit-pinned via upstream.lock.yaml
```

### 1.4 Seed ontology fields every proof block must carry (`seeds/seed-stage0-v1.yaml:214-269`, field names verbatim)

`proof_id` · `classification` · `wave` · `assertions` · `negative_control` · `fixture_format` ·
`blocked_marker` · `ledger_denominator` · `spike_dependency` · `increment_index` ·
`owner_placeholder` — each `required: true`. `negative_control` description (`:236-237`):
"The spec-time failing fixture plus its named exact expected_failure_reason, colocated so fixture
and asserted reason cannot drift".

---

## 2. THE BREAKDOWN

### 2.1 Increment #8 (`tasks/stage0-breakdown.md:59`, verbatim row; header at `:50-51`)

```
| # | Increment | Deliverables | Acceptance (deterministic) | Negative control | Venue / gate |
|---|---|---|---|---|---|
| 8 | S0-02 Buzz authorization | `proofs/s0-02/fixtures/{pos-allowed, neg-unauthorized, neg-bad-signature, neg-replayed, neg-stale}.json` | Allowed event ⇒ exactly one ACP turn; revocation independent of NIP-OA `created_at`; duplicate delivery idempotent | Four DISTINCT reasons (`sender-not-in-allowlist`, `signature-invalid`, `event-replayed`, `event-stale`); one blanket reject fails the proof | in-sandbox (Wave 1) |
```

### 2.2 Pinned decisions with their rejected alternatives (`tasks/stage0-breakdown.md:14-26`, verbatim)

```
| Decision | Rejected alternative | Source |
|---|---|---|
| Runner-emitted `result.json` is the single source of truth; ledger is GENERATED, CI drift-fails | Hand-authored ledger cross-checked by CI (two sources of truth; prose can lie) | interview Q1 |
| Execution denominator = artifacts with digest-verified `runs[]` (both control legs) — blocked proofs structurally lack `runs[]` | Class label by convention | interview Q1 |
| Two SPLIT CI checks: `ledger-integrity` (green when honest, even empty) and `stage1-gate` (RED by design until the registry's required set is satisfied) | One check doing both (empty repo would read as passing) | interview Q4 |
| Spikes classify, never gate; frozen `spike_to_class_mapping` applied mechanically; undeclared transitions need a reviewed commit | All spikes must pass before Wave 1 (runsc would deadlock Stage 0) | interview Q2 |
| Committed canonical fixtures drive the REAL pinned binaries; normalized-then-golden compare; `expected_failure_reason` inside each negative fixture | Byte-exact goldens (volatile fields) / test-time generation (oracle drift) / stub of the SUT (NO-STUBS) | interview Q3 |
| Blocked markers carry a probe run re-evaluated every CI run; `credential_rejected` ⇒ proof-RED, never blocked; blocker gone ⇒ `deferral_expired` RED | Static marker checked for presence | interview Q5 |
| S0-05 split: mechanism (Wave 0, selective egress via veth/proxy — bare `unshare --net` is proven TOTAL block) vs full live-unit proof (Wave 2) | Wholesale host-deferral of S0-05 | council + Chairman probe |
| Four-way classification; status lines never a flat N/12 | 12 undifferentiated proofs | council |
| S0-03 blocks on a real credential; pass asserts upstream model identity, never a 200; the S0-04 stub is forbidden for S0-03 | Run S0-03 against the S0-04 stub (stub-drift hollow green) | council (Socrates) |
| Machinery = increments 1–2 only; later proofs extend schemas by need | Five machinery increments / lazy machinery inside proof 1 | interview Q4 |
```

### 2.3 Venue update (`tasks/stage0-breakdown.md:28-38`, verbatim)

```
## Venue update (owner, 2026-09-03): the PC bridge is the execution host
`PC-BRIDGE.md` / `scripts/pc.sh`. Bridge-side (via `scripts/pc.sh`, results still written as
`result.json` with `env_fingerprint = pc-bridge:<host>`): the runsc/KVM spike and S0-08's live
run (#5, #17); podman-compose stacks for S0-01/S0-02 (#7, #8), S0-03/S0-04 (#14, #15) and
S0-06 (#13); S0-05's full canaries (#16). S0-03's upstream = the PC's local vLLM
(`localhost:8010/v1`, identity `sim9b`) behind OmniRoute — the credential question is closed.
**New Wave-0 spike #0 — `pc-bridge` liveness + capability probe** (needs the owner's BRIDGE
READY banner): `hostname`, `/dev/kvm`, `podman`, `runsc`, `rustup`/`cargo`, `curl localhost:8010/v1/models`.
The in-sandbox spikes #4 (dockerd) and #5 (runsc) become secondary: they record the SANDBOX
fact; the PC probe records the venue that matters. Without a banner in a session, bridge-side
items are `NOT run here: no bridge banner` — never silently skipped.
```

**Contradiction recorded, not resolved:** the increment table's venue cell for #8 reads
`in-sandbox (Wave 1)` (`:59`) while the venue update assigns "podman-compose stacks for
S0-01/S0-02 (#7, #8)" to the PC (`:31`), as does `PC-BRIDGE.md:69`.

### 2.4 Standing prerequisites (`tasks/stage0-breakdown.md:40-46`, verbatim)

```
## Standing prerequisites
- Pinned upstream sources: attach each repo via `add_repo` before cloning at the pinned commit
  (`upstream.lock.yaml`); public reads may be proxy-served — record every failure honestly.
- Every increment: `IS_SANDBOX`-free (no LLM in gates), deterministic test run TWICE (byte-identical),
  negative control authored BEFORE the positive leg, commit before any mutation audit, push at
  every boundary (incident log 2026-09-02).
- Commit message = reasoning record (rejected alternative, ordering rationale, primary source).
```

### 2.5 Ordering rationale (`tasks/stage0-breakdown.md:71-77`, verbatim)

```
Waves by falsification power then dependency (council): #1–2 machinery (self-verifying from an
empty set); #3–6 Wave-0 spikes in parallel (facts that reorder the plan); #7–12 Wave 1 in
parallel (disjoint components, real pinned binaries); #13 when its spike resolves; #14–16 the
spine (credential-gated S0-03 first so its RED-pending state is visible early); #17 spec now, run
later; #18 last (soft-depends on Wave 2's shape). Ada's verification-batching alternative stays an
open measurement: time #9's adversarial clearance vs wall-clock saved (KC-7).
```

### 2.6 NOT-built ledger (`tasks/stage0-breakdown.md:79-82`, verbatim, as at breakdown time)

```
## NOT-built ledger (honest, at breakdown time)
Nothing below exists yet: registry, schemas, validator, runner, generator, CI workflow, any spike,
any proof, any fixture, any ADR from S0-09/10, SBOM. `wiki-init` not yet run. Honey meter absent.
`ouroboros` MCP server does not connect natively — stdio fallback only.
```

Live ledger line touching S0-02 (`todo/BUILD-TASKLIST.md:32`, verbatim excerpt):
"· ABSENT 4 — S0-02, S0-04, S0-05, S0-06".

### 2.7 Owner answers (`tasks/stage0-breakdown.md:84-89`, verbatim) — none names S0-02

```
## Owner answers (2026-09-03)
- **#14 / KC-2:** credential = the PC's local vLLM endpoint behind OmniRoute. S0-03 is no longer
  blocked-on-external-input once the bridge is up; its class flips to execution via the
  `pc-bridge` spike (declared transition — add to `spike_to_class_mapping` in increment #1).
- **#17 / KC-1:** gVisor host = the PC (bare metal, KVM). S0-08 runs live via the bridge.
- **Ordering:** parallel-by-component stands.
```

---

## 3. FINDINGS + COUNCIL

### 3.1 Capability ledger (`docs/research/FINDINGS-STAGE0-v1.md:9-15`, verbatim)

```
## 1. Current-state capability ledger (honest, for council/interview briefs)

| State | Items |
|---|---|
| **Proven live this session** | Planning docs verified (`scripts/verify-planning-repo.sh` green); operating kit installed and probed: Ouroboros 0.53.0 + stdio fallback round trip (`scripts/ooo_mcp.py --list` returned full tool surface via the isolated-uvx retry), gitnexus 1.6.10, codebase-memory-mcp 0.10.8, aleph venv, /council + /wiki-* skills, graft graph built |
| **Built, never run** | Nothing — no application code exists (`STATUS.md`) |
| **Absent** | Everything in `docs/07_BUILD_PLAN.md`: all Stage 0 proofs, spine, adapters, policy service, evaluation lab. Honey: RESOLVED 2026-09-03 — vendored + installed offline from the local marketplace (plugin honey@greenpt 1.3.1, 14 skills, hive agents, eco meter). Wiki (`wiki-init` not yet run) |
```

### 3.2 Environment table rows that bear on S0-02 (`docs/research/FINDINGS-STAGE0-v1.md:19-29`, verbatim)

```
| Capability | Probe result | Stage 0 consequence |
|---|---|---|
| Python 3.11.15, uv 0.8.17 | present | Hermes (0.21.0, Python) plausibly installable in-sandbox |
| Node 22.22.2 / npm 10.9.7 | present | OmniRoute (3.8.51, Node) plausibly runnable in-sandbox |
| Docker CLI 29.3.1 | present, **daemon NOT running** (no /var/run/docker.sock) | Compose topologies unavailable unless dockerd-in-sandbox proves out (untested); plan spikes process-level first |
| **PC bridge** (learned 2026-09-03 from the owner) | The owner's PC is the execution host: Fedora 42 bare metal (KVM), podman + podman-compose, local vLLM OpenAI-compatible endpoint `localhost:8010/v1` (`sim9b`), reached via a token-gated HTTP bridge with per-session ephemeral links (`PC-BRIDGE.md`) | S0-08 (runsc/KVM), all container stacks (Buzz relay, OmniRoute, ai-memory), and S0-03's model upstream run THERE. No third-party model credential is needed: OmniRoute's upstream = the PC's vLLM, identity asserted as `sim9b` |
| Network | pip/npm/uv installs worked; raw.githubusercontent.com curl blocked; GitHub repo access is session-scoped — upstream clones need `add_repo` per repo (public read may be proxy-served) | Pinned upstream checkouts are feasible but each repo needs explicit attachment; record every failure honestly |
```

### 3.3 Per-proof constraint (`docs/research/FINDINGS-STAGE0-v1.md:43`, verbatim)

```
| S0-02 | Buzz authorization/freshness | Negative legs are the point: unauthorized/invalid/replayed/stale/self-authored produce NO turn (`03` §1.2); NIP-OA `created_at` is not revocation (`02` §2) |
```

**Note (fact, not judgement):** the findings row names FIVE negative classes
("unauthorized/invalid/replayed/stale/self-authored"); the seed's negative_control block names
FOUR fixtures (`seeds/seed-stage0-v1.yaml:375-380`) and `proofs/registry.yaml:13` records
`"required_negative_controls": 4`. `docs/03_INTEGRATION_CONTRACTS.md:22` lists five
("Unauthorized, invalid, replayed, stale, and self-authored events produce none.").

### 3.4 Cross-cutting invariants (`docs/research/FINDINGS-STAGE0-v1.md:55-69`, verbatim)

```
## 4. Cross-cutting invariants that bind the seed

- NO STUBS in the spine (CLAUDE.md #1): every proof exercises the REAL pinned component; the
  one sanctioned stub is S0-04's deterministic upstream-request-preservation instrument, which
  sits BEHIND real OmniRoute at the boundary the plan itself specifies.
- No-LLM-judge spine: all Stage 0 exit evidence is deterministic (exit codes, fixtures, header
  asserts, canary failures).
- Negative-control discipline: S0-02/S0-05/S0-08 are *defined by* their failing legs; every
  other proof needs at least one violating fixture failing for the exact expected reason.
- Fail-closed semantics: policy outage/malformed ⇒ deny (`03` §5, `05` §3); recall degradation
  is visible, `memory_required` uses a separate preflight because `pre_llm_call` fails open
  (`01` §5, `04` §4).
- Environment blockers are surfaced, not routed around: if gVisor (or dockerd) cannot run here,
  the proof is delivered as spec + fixture + explicit `NOT run here: <reason>` + host runbook,
  never a fake green.
```

### 3.5 Chairman-verified addenda (`docs/research/FINDINGS-STAGE0-v1.md:92-114`) — none names S0-02

Addenda 1 (bare netns), 2 (S0-03 unclassified), 3 (S0-06 class disputed). No S0-02 item.

### 3.6 Council lines that touch S0-02 (`docs/research/COUNCIL-VERDICT-STAGE0-v1.md`, verbatim)

Kill Criterion 4 (`:36`):
```
4. **If any Stage 0 status line published during Wave 1 reads as a flat "N/12"**, the three-way classification has failed in practice; halt and re-issue the ledger with separate denominators before further proof work.
```

Kill Criterion 5 (`:37`):
```
5. **If two or more Wave-1 proofs pass without a negative control that fails for a named exact reason**, negative-control discipline has decayed — halt Wave 2 until the passing proofs are mutation-audited.
```

Recommended next step 5 (`:59`, verbatim, S0-02 clause emphasised in source):
```
5. Author every proof's negative control at spec time, before its positive leg, each naming the exact expected error or exit code. Feynman's four kills are the seed set: S0-05 asserts the exact denial reason and dies when the gate is mutated off; S0-04 dies when OmniRoute's real header-set code is mutated; S0-02 demands four *distinct* error reasons, not four failures; S0-08's `NOT run here` marker is grep-checked and gates Stage 1.
```

Wave-plan placement (`docs/research/COUNCIL-VERDICT-STAGE0-v1.md:71` vote line + seed constraint
`seeds/seed-stage0-v1.yaml:103-105`): S0-02 is a **Wave 1** proof —
"then Wave 1 (S0-01/02/07 + decision shells), Wave 2 spine (S0-03/04/05), Wave 3 (S0-11)".

---

## 4. PLAN-DOC SEAMS AND PINS

### 4.1 `docs/03_INTEGRATION_CONTRACTS.md:5-29` (verbatim — §1 Buzz → buzz-acp → Hermes)

```
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
```

### 4.2 `docs/02_COMPONENT_AUDIT.md:36-43` (verbatim — Buzz and `buzz-acp`)

```
### Buzz and `buzz-acp` — selected interaction bridge

- Buzz is Apache-2.0 and supplies the human collaboration relay.
- Configure `BUZZ_ACP_AGENT_COMMAND=hermes-acp`; `BUZZ_ACP_AGENT_ARGS` may be blank.
- Set `BUZZ_ACP_IDLE_TIMEOUT` explicitly. Source currently defaults to 1500 seconds while the README table says 620; this plan selects 900 pending load tests.
- Source-backed bridge variables include agent command/args, MCP command, idle timeout, max turn duration, system prompt/file, agent count, and agent owner.
- The production relay layout uses Postgres 17, passworded append-only Redis, pinned MinIO plus initialization, and `BUZZ_S3_*` configuration. Do not revive the earlier Postgres 16, unauthenticated Redis, mutable MinIO, or incorrect S3 variables.
- NIP-OA `created_at` is agent-declared metadata, not revocation. Enforce membership removal/key rotation and independent freshness.
```

### 4.3 `docs/01_ARCHITECTURE.md` (verbatim lines)

`:93` — "- Unknown Buzz senders and invalid/replayed events are denied."
`:116` — "| Buzz → `buzz-acp` | Membership/allowlist, signature verification, independent freshness and replay controls |"
`:117` — "| `buzz-acp` → Hermes | Pinned `hermes-acp`, bounded session lifetime, explicit timeouts, audited process ownership |"

### 4.4 `docs/05_SECURITY.md` (verbatim lines)

`:16` — "| Unauthorized or replayed Buzz event | Allowlist/membership, signature, independent freshness, cursor/de-duplication | Denial/replay event and key rotation |"
`:17` — "| `buzz-acp` process/session abuse | Pinned command, fixed args, turn/idle limits, no shell interpolation | ACP lifecycle audit and forced cleanup tests |"
`:78` — "| `buzz-acp` | Buzz relay and local/private `hermes-acp` endpoint/process only |"
`:98` — "- Unauthorized/stale/replayed Buzz events cannot start an ACP turn."

### 4.5 `docs/09_PREMORTEM.md:15` (verbatim)

```
| 9 | Buzz revocation relies on author timestamp | Removed user still starts turns | Independent membership/key/freshness enforcement |
```

`docs/09_PREMORTEM.md:32` (stop-the-line): "- an unauthorized/stale/replayed Buzz event starts an ACP turn;"

### 4.6 `docs/07_BUILD_PLAN.md:10` (verbatim)

```
| S0-02 | Buzz authorization/freshness | Allowed event succeeds; unauthorized/replayed/stale events fail |
```

### 4.7 ADRs

`docs/adr/0001-hermes-only-runtime.md:14` (verbatim): "Use `buzz-acp` to launch `hermes-acp`.
Hermes is the only stock production workhorse. …"
No ADR under `docs/adr/` is specifically about Buzz authorization — **NOT SPECIFIED in `docs/adr/`**.

### 4.8 `upstream.lock.yaml` pins (verbatim, `:5-20`)

```yaml
  agent-client-protocol:
    repository: https://github.com/agentclientprotocol/agent-client-protocol.git
    commit: 37a7d4f8a0a0632653a14084b8140ceb486ab0e8
    license: Apache-2.0
    role: buzz_to_hermes_protocol_contract
  hermes-agent:
    repository: https://github.com/NousResearch/hermes-agent.git
    commit: 527da60844d4dced37879ea50259675371abe10e
    observed_version: 0.21.0
    license: MIT
    role: main_production_workhorse_and_native_acp_server
  buzz:
    repository: https://github.com/block/buzz.git
    commit: 1c8321cd08feb597f8bcff5195c21148fb3e98ed
    license: Apache-2.0
    role: human_interface_relay_and_buzz_acp
```

### 4.9 `.env.example` variables naming the S0-02 surface (verbatim lines 4-18)

```
BUZZ_RELAY_URL=https://replace-with-buzz-relay
BUZZ_PRIVATE_KEY=replace-from-secret-store
BUZZ_CHANNELS=replace-with-comma-separated-channel-ids
BUZZ_ALLOWED_USERS=replace-with-comma-separated-npubs-or-hex-keys
BUZZ_ALLOW_ALL_USERS=false
BUZZ_ACP_AGENT_COMMAND=hermes-acp
BUZZ_ACP_AGENT_ARGS=
BUZZ_ACP_MCP_COMMAND=
BUZZ_ACP_IDLE_TIMEOUT=900
BUZZ_ACP_MAX_TURN_DURATION=3600
BUZZ_ACP_SYSTEM_PROMPT_FILE=/etc/agent-factory/bootstrap.md
BUZZ_ACP_AGENTS=1
BUZZ_ACP_AGENT_OWNER=replace-with-owner-public-key
```

---

## 5. WHAT EXISTS TODAY

### 5.1 `ls -la proofs/S0-02/`

```
ls: cannot access 'proofs/S0-02/': No such file or directory
```

`ls -la proofs/` returns: `S0-01 S0-03 S0-07 S0-08 S0-09 S0-10 S0-11 S0-12 ledger.json
normalization.yaml registry.yaml schemas/`. No `S0-02`, no `blocked.json`, no `probe.json`, no
`spec.json`, no fixtures for S0-02 anywhere in the tree.

### 5.2 Registry entry (`proofs/registry.yaml:13`, verbatim)

```json
  {"proof_id": "S0-02", "title": "Buzz authorization and freshness", "classification": "execution_proof", "wave": 1, "spike_dependencies": [], "required_negative_controls": 4, "assertion_count": 3},
```

Registry class denominators (`proofs/registry.yaml:3-9`, verbatim):
```json
"classes": {
  "execution_proof": {"ledger_denominator": 7},
  "conformance_checked_decision": {"ledger_denominator": 3},
  "blocked_credential": {"ledger_denominator": 1},
  "blocked_host": {"ledger_denominator": 1}
},
"class_aliases": {"blocked_capability": "blocked_host"},
"waves": [0, 1, 2, 3],
```

Ledger state today (`proofs/ledger.json`): `{"classification": "execution_proof", "proof_id":
"S0-02", "state": "ABSENT"}` — no `normalized_digest`.

### 5.3 Schema fields an S0-02 artifact must satisfy

`proofs/schemas/spec.schema.json` (verbatim, `:6-42`) — the runner's input:

```json
  "additionalProperties": false,
  "required": ["proof_id", "legs"],
  "properties": {
    "proof_id": {"type": "string", "pattern": "^S0-(0[1-9]|1[0-2])$"},
    "legs": {
      "type": "array",
      "minItems": 2,
      "items": {"$ref": "#/$defs/leg"},
      "contains": {"type": "object", "properties": {"leg": {"const": "positive"}}, "required": ["leg"]},
      "minContains": 1,
      "allOf": [{"contains": {"type": "object", "properties": {"leg": {"const": "negative"}}, "required": ["leg"]}, "minContains": 1}]
    }
  },
  "$defs": {
    "leg": {
      "type": "object",
      "additionalProperties": false,
      "required": ["leg", "cmd", "cwd", "timeout_s", "expect"],
      "properties": {
        "leg": {"enum": ["positive", "negative"]},
        "cmd": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        "cwd": {"type": "string", "pattern": "^(?!/)(?!.*(^|/)\\.\\.(/|$)).*$"},
        "timeout_s": {"type": "integer", "minimum": 1, "maximum": 3600},
        "env": {"type": "object", "additionalProperties": {"type": "string"}},
        "expect": {
          "type": "object",
          "additionalProperties": false,
          "required": ["exit_code"],
          "properties": {
            "exit_code": {"type": "integer"},
            "failure_reason": {"type": "string", "minLength": 1, "pattern": "^\\S(.*\\S)?(?![\\s\\S])"}
          }
        }
      },
      "if": {"properties": {"leg": {"const": "negative"}}, "required": ["leg"]},
      "then": {"properties": {"expect": {"required": ["exit_code", "failure_reason"]}}}
    }
  }
```

`proofs/schemas/result.schema.json` (verbatim, `:7-37`):

```json
  "required": ["proof_id", "classification", "recorded_at", "env_fingerprint", "runs", "negative_control", "attestation", "digest"],
  "properties": {
    "proof_id": {"type": "string", "pattern": "^S0-(0[1-9]|1[0-2])$"},
    "classification": {"enum": ["execution_proof", "conformance_checked_decision"]},
    "recorded_at": {"type": "string", "format": "date-time", "pattern": "Z$"},
    "env_fingerprint": {"type": "string", "pattern": "^(pc-bridge|sandbox):.+$"},
    "runs": {
      "type": "array",
      "minItems": 2,
      "contains": {"type": "object", "properties": {"leg": {"const": "positive"}}, "required": ["leg"]},
      "minContains": 1,
      "allOf": [{"contains": {"type": "object", "properties": {"leg": {"const": "negative"}}, "required": ["leg"]}, "minContains": 1}],
      "items": {"$ref": "#/$defs/run"}
    },
    "negative_control": {
      "type": "object",
      "additionalProperties": false,
      "required": ["fixture", "expected_failure_reason", "observed_failure_reason"],
      …
    },
    "attestation": {
      "type": "object",
      "description": "Binds this artifact to the exact proof inputs that produced it: a map of every input file under the proof directory (checker, spec, fixtures, design) to its sha256. The validator recomputes it from the tree and fails on any mismatch, so a neutered checker with a stale green artifact no longer validates.",
      "minProperties": 1,
      "additionalProperties": {"$ref": "#/$defs/sha256"}
    },
    "digest": {"$ref": "#/$defs/sha256"}
  },
```

`run` object required fields (`result.schema.json:53`): `["leg", "cmd", "started_at",
"finished_at", "exit_code", "stdout_sha256", "stderr_sha256"]`; optional `failure_reason`,
`artifacts`.

**Recorded fact:** the result schema's `runs` requires `minItems: 2` with at least one positive
and one negative leg; the seed's S0-02 block names FOUR distinct negative fixtures and
`registry.yaml:13` records `required_negative_controls: 4`, while
`scripts/validate-ledger` (read this session, `:216-342`) contains no check that reads
`required_negative_controls`. `grep -n required_negative_controls scripts/*` → matches only in
`scripts/validate-ledger:170-196` as a *presence/typing* check
(`"registry-schema: {proof_id} {field} must be an integer >= {floor}"`), never as a count over the
artifact's legs.

### 5.4 Minted EXECUTION exemplars

**S0-07 `proofs/S0-07/spec.json` (verbatim, whole file):**

```json
{
  "proof_id": "S0-07",
  "legs": [
    {
      "leg": "positive",
      "cmd": ["python3", "proofs/S0-07/check_fubuki_corrections.py", "/home/user/nerdherderdani/fubuki-os"],
      "cwd": ".",
      "timeout_s": 60,
      "expect": {
        "exit_code": 0
      }
    },
    {
      "leg": "negative",
      "cmd": ["python3", "proofs/S0-07/check_fubuki_corrections.py", "--lint-check", "proofs/S0-07/fixtures/neg-violating-persona", "/home/user/nerdherderdani/fubuki-os"],
      "cwd": ".",
      "timeout_s": 60,
      "expect": {
        "exit_code": 1,
        "failure_reason": "lint-violation: corporate-filler, exit 1 per contract"
      }
    }
  ]
}
```

**`graft skeleton proofs/S0-07/check_fubuki_corrections.py` (verbatim tool output):**

```
- L22-L24  function _add_fubuki  def _add_fubuki(fubuki_root: Path)
- L27-L34  function _correct_lint_exit  def _correct_lint_exit(findings: list) -> int
- L37-L76  function check_lint_ordering  def check_lint_ordering(fubuki_root: Path) -> bool
- L79-L132  function check_bound_decision_join  def check_bound_decision_join(fubuki_root: Path) -> bool
- L135-L171  function check_hash_stability  def check_hash_stability(fubuki_root: Path) -> bool
- L174-L198  function lint_check_fixture  def lint_check_fixture(fixture_dir: Path, fubuki_root: Path) -> int
- L201-L231  function main  def main()
```

**S0-07 `result.json` shape (verbatim head + attestation, `proofs/S0-07/result.json:1-6, 37-58`):**

```json
{
  "proof_id": "S0-07",
  "classification": "execution_proof",
  "recorded_at": "2026-09-07T23:46:16.763007Z",
  "env_fingerprint": "sandbox:vm",
  "runs": [ … ],
  "negative_control": {
    "fixture": "python3 proofs/S0-07/check_fubuki_corrections.py --lint-check proofs/S0-07/fixtures/neg-violating-persona /home/user/nerdherderdani/fubuki-os",
    "expected_failure_reason": "lint-violation: corporate-filler, exit 1 per contract",
    "observed_failure_reason": "lint-violation: corporate-filler, exit 1 per contract"
  },
  "attestation": {
    "scripts/proof-runner": "40fbbf9fc85a5457c067d06bebfc4aa012136b3ee5747d961eea75d1c531c0ce",
    "scripts/validate-ledger": "ba218c9d05884b69c070e52f27b1311d2d124a64545f2f7321cbab534de228bb",
    "proofs/registry.yaml": "f480161e2b0b6018327e48347c11b905a40663a094d29909919216410440f779",
    "proofs/schemas/blocked.schema.json": "bbe4a1a68dc3f1c3dfc38855846d7c2540adda8e332721991622824f88e705b6",
    "proofs/schemas/probe.schema.json": "bd71b22e47bea10f92f17fbc79d62ed729e514a4734223f9da2d6e7a0492e80e",
    "proofs/schemas/result.schema.json": "9a165ceb4bee63ed4c3f2346bcef786062ead3b825a8ff35931fb4f41af85ea6",
    "proofs/schemas/spec.schema.json": "30a2806e7825b0f0e99e1d4918264b8e19f026a570096243018ca1ed72c7c305",
    "proofs/schemas/spike.schema.json": "d2c3ad52b76b48e727cb748cfde9f9ad1e92ad801a6bbef3266b6f4342a6c773",
    "proofs/S0-07/check_fubuki_corrections.py": "a2337d2a51fbf226d92dc1d56714cf476ff1b177b3dd00ad4b278f5985982d7a",
    "proofs/S0-07/fixtures/neg-violating-persona/violation.txt": "78b7e384ce481b94160907346ee24a5c5b6aec745c88743cf7d702bc4256f24b",
    "proofs/S0-07/fixtures/ordered-lint/01-review-only.txt": "97bb8f5b93882d907b6e2a8d20e4e9ae3e9534e8601f7cbfe26473ef82bdbd00",
    "proofs/S0-07/fixtures/ordered-lint/02-has-violation.txt": "f4a38ef916261fd19d68f84dc9fbcc1e64f67c722c5eb2269785cd412e25f6f8",
    "proofs/S0-07/fixtures/ordered-lint/clean.txt": "2a393f13c05bb16f92f5c8cc7c2668f4f893f3a21b4c5729426386c1fb03f18c",
    "proofs/S0-07/spec.json": "bc4954affea29122d0a552f409e34e6a38ae75e5988de9d5a1b0b4a10c162c01"
  },
  "digest": "6e4d69c2c2789c96a08fd582e8cce880dc3ebb94af8eabbda8136d5027654be3"
}
```

**S0-11 `proofs/S0-11/spec.json` (verbatim, whole file) — the three-leg exemplar (one positive,
TWO negatives, each with its own pinned complete reason):**

```json
{
  "proof_id": "S0-11",
  "legs": [
    {
      "leg": "positive",
      "cmd": ["python3", "proofs/S0-11/check_eval_hardening.py", "proofs/S0-11"],
      "cwd": ".",
      "timeout_s": 60,
      "expect": {
        "exit_code": 0
      }
    },
    {
      "leg": "negative",
      "cmd": ["python3", "proofs/S0-11/check_eval_hardening.py", "--rubric-neg-cred", "proofs/S0-11/fixtures/neg_credential_read.py", "proofs/S0-11"],
      "cwd": ".",
      "timeout_s": 60,
      "expect": {
        "exit_code": 1,
        "failure_reason": "rubric-isolation-violation: credential env absent by construction"
      }
    },
    {
      "leg": "negative",
      "cmd": ["python3", "proofs/S0-11/check_eval_hardening.py", "--rubric-neg", "proofs/S0-11/fixtures/rubric_probe.py", "proofs/S0-11"],
      "cwd": ".",
      "timeout_s": 60,
      "expect": {
        "exit_code": 1,
        "failure_reason": "rubric-isolation-violation: cwd-not-isolated,env-not-allowlisted,netns-not-isolated"
      }
    }
  ]
}
```

**`graft skeleton proofs/S0-11/check_eval_hardening.py` (verbatim tool output, 39 defs):**

```
- L91-L95  function _net_ns  def _net_ns()
- L98-L108  function _iso_launch  def _iso_launch(child_cmd)
- L111-L132  class _LoopbackListener  class _LoopbackListener
- L112-L118  method __init__  def __init__(self)
- L120-L126  method _serve  def _serve(self)
- L128-L132  method close  def close(self)
- L135-L140  function _proc_uid  def _proc_uid(pid)
- L143-L147  function _proc_env_keys  def _proc_env_keys(pid)
- L150-L161  function _proc_privilege  def _proc_privilege(pid)
- L164-L171  function _collect_output  def _collect_output(workspace)
- L174-L194  function _nsenter_reach  def _nsenter_reach(pid, port)
- L197-L207  function _release  def _release(proc)
- L210-L260  function _observe_child  def _observe_child(launch, base_env, port, fresh_cwd)
- L263-L278  function _violations  def _violations(obs, parent_net_ns, parent_cwd)
- L281-L286  function _stable_breaches  def _stable_breaches(obs, parent_net_ns, parent_cwd)
- L289-L299  function _with_decoys  def _with_decoys(fn)
- L302-L304  function _allow_env  def _allow_env()
- L307-L308  function _full_env  def _full_env()
- L311-L332  function _capability_status  def _capability_status()
- L336-L350  function check_runner_design  def check_runner_design(proof_dir)
- L353-L362  function _extract_policy  def _extract_policy(text)
- L377-L385  function _symbolic_world_write  def _symbolic_world_write(text)
- L388-L395  function _text_prohibited  def _text_prohibited(text)
- L398-L406  function _call_name  def _call_name(func)
- L409-L419  function _fold_int  def _fold_int(node, int_consts)
- L422-L429  function _strings_of  def _strings_of(node, str_lists)
- L432-L492  function _python_prohibited  def _python_prohibited(text)
- L495-L519  function _yaml_walk  def _yaml_walk(node)
- L522-L531  function _yaml_prohibited  def _yaml_prohibited(text)
- L534-L551  function check_forbidden_ops  def check_forbidden_ops(proof_dir)
- L555-L612  function check_rubric_isolation  def check_rubric_isolation(proof_dir)
- L564-L571  function run  def run()
- L615-L627  function positive  def positive(proof_dir)
- L630-L658  function rubric_neg  def rubric_neg(probe, proof_dir)
- L645-L650  function run  def run()
- L661-L692  function rubric_neg_cred  def rubric_neg_cred(fixture, proof_dir)
- L670-L677  function run  def run()
- L695-L721  function main  def main()
```

**S0-09 — the minted DECISION exemplar. `proofs/S0-09/spec.json` (verbatim, whole file):**

```json
{
  "proof_id": "S0-09",
  "legs": [
    {
      "leg": "positive",
      "cmd": ["python3", "proofs/S0-09/check_conformance.py", "docs/adr/0005-foundry-host.md"],
      "cwd": ".",
      "timeout_s": 30,
      "expect": {"exit_code": 0}
    },
    {
      "leg": "negative",
      "cmd": ["python3", "proofs/S0-09/check_conformance.py", "proofs/S0-09/fixtures/neg-missing-section.md"],
      "cwd": ".",
      "timeout_s": 30,
      "expect": {"exit_code": 1, "failure_reason": "adr-incomplete: missing required section"}
    }
  ]
}
```

`graft skeleton proofs/S0-09/check_conformance.py` → `- L10-L29  function check  def check(path)`.

S0-09 `result.json:29-39` records `"failure_reason": "adr-incomplete: missing required section:
Consequences"` against `"expected_failure_reason": "adr-incomplete: missing required section"` —
i.e. the spec's `failure_reason` is a *substring* of the observed line (the binding rule is quoted
in §5.5 below).

### 5.5 How `scripts/proof-runner` mints (file:line)

- `main` — `scripts/proof-runner:274-293`: `verb ∈ {run, probe}`, `--proof`, `--venue ∈ {sandbox,
  pc-bridge}`, `--root`; `Deferred` → exit 2, any other exception → exit 1.
- `run_proof` — `:131-145` (verbatim):
  ```python
  def run_proof(root, proof_id, venue):
      proof_dir = root / "proofs" / proof_id
      result_path = proof_dir / "result.json"
      try:
          _run_proof(root, proof_id, venue, proof_dir, result_path)
      except Deferred:
          # Incapable venue: PRESERVE the capable-venue artifact untouched.
          raise
      except Exception:
          # A real capable-run FAILURE invalidates the stale artifact — otherwise a
          # mutated runner that makes the proof fail leaves the previous green in
          # place and the validator still reports PRESENT. Only an explicit defer
          # preserves.
          _remove(result_path)
          raise
  ```
- `_run_proof` — `:148-223`: loads `spec.json`, validates against `spec.schema.json` (`:154`),
  proof-id match (`:155-156`), registry lookup (`:157-159`); per leg: `cwd` must resolve inside
  root (`:164-168`), `_run_process` (`:169-175`), **exit 2 ⇒ `Deferred`** (`:181-185`), exit-code
  equality (`:186-191`); for a negative leg the expected `failure_reason` must appear as a
  substring of some stdout/stderr line (`:192-199`, verbatim):
  ```python
          if leg["leg"] == "negative":
              expected_reason = leg["expect"]["failure_reason"]
              observed_reason = next(
                  (line for line in (stdout + "\n" + stderr).splitlines() if expected_reason in line),
                  None,
              )
              if observed_reason is None:
                  raise ValueError(f"negative-control-unmet: {proof_id}")
  ```
  then `run["failure_reason"] = observed_reason` (`:203`) and the FIRST negative leg fills
  `negative_control` (`:204-209`). Artifact assembled `:212-221` with
  `env_fingerprint = f"{venue}:{platform.node()}"` (`:216`),
  `attestation = validator.proof_attestation(root, proof_id)` (`:219`),
  `digest = validator.canonical_digest(runs)` (`:220`); validated against
  `result.schema.json` (`:222`) then written (`:223`).
- Environment: `PASSTHROUGH_ENV = ("PATH", "HOME", "LANG")` (`:18`); `_clean_env` `:72-82`.
- `run_probe` — `:226-271` (blocked proofs only; see material-S0-03/S0-08).

### 5.6 What `scripts/validate-ledger` checks (file:line)

- `CANONICAL_CLASSES` `:12-17`; `PROOF_ID_RE` `:19`.
- `ATTESTATION_CLOSURE = ("scripts/proof-runner", "scripts/validate-ledger",
  "proofs/registry.yaml")` `:52`; `proof_attestation` `:55-79` — closure + `proofs/schemas/*.json`
  + `rglob` of the proof dir, excluding `result.json`, `blocked.json`, `__pycache__`.
- `_registry` `:82-205` — comment-stripped JSON parse of `registry.yaml` (`:85-88`); required top
  keys `{"classes","class_aliases","waves","proofs","spike_to_class_mapping"}` (`:95`); classes
  must be the canonical four *in order* (`:101`); every proof entry needs
  `{"proof_id","title","classification","wave","spike_dependencies",
  "required_negative_controls","assertion_count"}` (`:170-177`); `spike_dependencies` members must
  exist in the mapping (`:189-191`); blocked proofs need exactly
  `{"owner","unblock_condition","marker_path"}` (`:197-201`); ids must be S0-01…S0-12 (`:202-204`).
- `_artifact_states` `:216-342` — both artifacts present ⇒ `INVALID` (`:224-227`); schema validate;
  `proof_id` match; `classification` must equal the registry's (`:242-247`); runs must carry both
  legs (`:249-256`); `digest` recomputed (`:257-260`); **attestation recomputed from the tree and
  compared** (`:265-274`); **runs bound to the attested spec** — same count/order/leg/cmd/expected
  exit, and each negative leg's recorded reason must contain the spec's `failure_reason`
  (`:281-306`). States: `PRESENT` / `INVALID` / `BLOCKED` / `EXPIRED` / `ABSENT`.
- `_mapped_spikes` `:373-393` — every spike artifact's `classification_effect` transition must be
  a *declared* transition (`undeclared-transition` finding).
- `_ledger` `:396-416` — `ledger-drift: {proof_id} claimed {X} but {Y}`.
- `integrity` `:440-457` — prints per-proof state and `classification numerator=… denominator=…`
  where the numerator counts `PRESENT` or `BLOCKED` (`:449-453`); exit 1 iff findings.
- `stage1_gate` `:460-478` — expected state is `BLOCKED` for `blocked_*` classes else `PRESENT`;
  `EXPIRED` prints "deferral expired — the proof must run"; exit 2 iff anything missing.
- `main` `:481-500` — refuses to run without the `date-time` format checker (exit 3).

`scripts/ledger-gen` (`:26-57`) strips the volatile fields declared in `proofs/normalization.yaml`
before hashing:

```json
  "result": [
    "recorded_at",
    "env_fingerprint",
    "runs.*.started_at",
    "runs.*.finished_at",
    "digest"
  ],
  "blocked": [
    "env_fingerprint",
    "marker.probe_run.started_at",
    "marker.probe_run.finished_at"
  ]
```

CI wiring (`.github/workflows/stage0-ci.yml:47-61`): `ledger-gen --root .` → `git diff
--exit-code -- proofs/ledger.json` → `validate-ledger integrity --root . --ledger
proofs/ledger.json`; `stage1-gate` job at `:63-` runs with `continue-on-error: true`.

### 5.7 S0-01 assets that already exist and touch the S0-02 subject (located, not evaluated)

- `proofs/S0-01/tools/nostr_verify.py` — `graft skeleton` (verbatim):
  ```
  - L28-L42  function _point_add  def _point_add(P, Q)
  - L45-L56  function _point_mul  def _point_mul(k, P)
  - L59-L69  function _lift_x  def _lift_x(x)
  - L75-L78  function _tagged_hash  def _tagged_hash(tag, msg)
  - L84-L92  function event_id  def event_id(event)
  - L98-L131  function schnorr_verify  def schnorr_verify(pubkey_bytes, msg, sig_bytes)
  - L141-L171  function schnorr_sign  def schnorr_sign(seckey32, msg32, aux32)
  - L177-L216  function verify_event  def verify_event(event)
  - L222-L262  function sign_event  def sign_event(privkey_hex, fields)
  ```
- `proofs/S0-01/fixtures/identities.json` (verbatim, whole file):
  ```json
  {
    "agent": "ff4d48deaa326bcae60687e64cca48dd7f70099933fbda0ae40d2561485f4ce1",
    "channel": "73701f66-6e12-42ff-b561-7d36db1ad91b",
    "owner": "2267fe91571e5c9166ddf1a80176e988bdd00b9023edcc33375e1be85928000c",
    "relay": "80bbcbe534e1108571a91390b283e08f9d658212674ae7c4779763710217d4b2",
    "relay_url": "ws://127.0.0.1:3999",
    "user2": "fec645734c4bdd1a6867ab061b0a7aca7f8128d98ace364707814043b090ea22"
  }
  ```
- `proofs/S0-01/fixtures/relay-events-2026-09-05.json` — array of signed kind-9 events with
  `id`/`pubkey`/`sig`/`tags` (`h` = channel, `p` = agent); first record verbatim head:
  `{"content":"S0-01 fixture prompt: respond with one short terminal answer.","created_at":1788563660,"id":"d532f549…","kind":9,"pubkey":"2267fe91…","sig":"8a2325c5…","tags":[["h","73701f66-…"],["p","ff4d48de…"]]}`
- `proofs/S0-01/fixtures/bip340-test-vectors.csv`, `proofs/S0-01/fixtures/acp-schema-v1.json`,
  `proofs/S0-01/fixtures/upstream-token.fingerprint`, `proofs/S0-01/fixtures/neg-malformed-initialize.json`.
- `proofs/S0-01/tools/pc/` — `collect_leg.sh`, `pc_backend_restart.sh`, `pc_launch.py`,
  `pc_manifest.sh`, `pc_mention.sh`, `pc_negative.py`, `pc_post.sh`, `run_leg.sh`.
- `proofs/S0-01/GROUNDING.md:142-146` (verbatim) — the isolated relay stack the S0-02 work would
  meet:
  ```
  - [x] Throwaway Buzz relay + Nostr identity isolated from production (`buzz-prod-*`): own ports (3999/3998/3997,
        postgres 5471, redis 6471, minio 9471), own containers `s0-01-harness-*`, own keys. **CAVEAT (AF-AP-34):** four
        `pkill -x buzz-relay` calls on 2026-09-04 aimed at THIS relay restarted the production `buzz-prod-relay-1`
        (its binary shares the bare name in the host process table) — reported to the owner; teardown now goes
        through pidfiles + `/proc/<pid>/exe`, never names.
  ```
- `proofs/S0-01/GROUNDING.md:152-156` (verbatim) — relay/authorization facts already observed:
  ```
  - Isolated relay stack up on the PC (relay `127.0.0.1:3999`, `RELAY_URL=ws://127.0.0.1:3999` — identical
    authority everywhere, the fail-closed tenant binding bit once as a WebSocket 404); relay/agent/owner Nostr
    identities registered; channel `73701f66-…` created (kind 9007) with the agent as member (kind 39002);
    buzz-acp (`BUZZ_ACP_RESPOND_TO=owner-only`, `SESSION_POLICY=thread`, idle timeout set) subscribed; an owner
    `buzz messages send --mention` was `accepted: true` with the `h` + `p` tags.
  ```
- `todo/BUILD-TASKLIST.md:253-255` (verbatim) — an S0-02 observation recorded during S0-01:
  ```
  reached the thread (this buzz-acp delegates replying to the agent via a Buzz MCP tool it was not given — S0-02
  territory); the pinned hermes-acp ran a terminal tool with no policy gate (S0-08 territory). Still unproven:
  ```
- `proofs/S0-01/GROUNDING.md:59-65` (verbatim) — the buzz-acp drive-mode fact:
  ```
  - `buzz-acp` is a **relay daemon**: `main() -> buzz_acp::run()`; requires `--private-key` (Nostr) and
    `--relay-url` (default `ws://localhost:3000`). It launches the agent via
    `--agent-command <bin> --agent-args <...>` (defaults `goose acp`) and drives it over stdio.
    Its `AcpClient` (spawn → initialize → session_new → session_prompt_with_idle_timeout →
    cancel_with_cleanup → shutdown) is in a **private** `mod acp` — NOT externally linkable, and there
    is **no fixture/oneshot/stdin drive mode**. So a faithful "launched by the real buzz-acp" run must
    go through the relay path.
  ```

---

## 6. VENUE FACTS

### 6.1 `PC-BRIDGE.md` lines that place S0-02 (verbatim)

`:59` — "| Containers = **podman** (rootless; `systemctl --user start podman.socket`,
`DOCKER_HOST=unix:///run/user/1000/podman/podman.sock`, `podman-compose`, volumes need `:Z` for
SELinux) | Buzz relay stack (Postgres 17 / Redis / MinIO), OmniRoute, ai-memory run here via
podman-compose, not docker |"

`:66-70` (verbatim):
```
## What Stage 0 runs where

- **Sandbox:** machinery (#1–2), fixture authoring, Fubuki (S0-07), ADR shells (S0-09/10/12), rubric-isolation fixtures (S0-11), selective-egress netns mechanism spike.
- **PC via bridge:** `runsc`/KVM spike + S0-08 live run · podman stacks for S0-01/S0-02 (Buzz relay + buzz-acp + hermes-acp), S0-03/S0-04 (OmniRoute + vLLM upstream), S0-06 (ai-memory) · the full S0-05 egress canaries over live units.
- Every bridge-side proof still writes the same `result.json` artifact family; the runner records `env_fingerprint = pc-bridge:<hostname>` so ledger entries name their venue.
```

`:9-12` (verbatim): "**Links and tokens are EPHEMERAL — never commit them.** The owner pastes a
"BRIDGE READY" banner per session (`AGENT_TOKEN` + `trycloudflare` URL); PC-side they live in
`~/.agent_token` and `~/.agent_url`. A new bridge launch mints a new URL and token. Sandbox-side,
put them in the untracked `.pc-bridge.env` (gitignored)".

`:164-169` (verbatim, the process-kill rule that bit on the S0-01 relay):
```
- **Never kill by name on this host (AF-AP-34).** The production Buzz relay's binary shows up in the
  host process table as `buzz-relay`, so `pkill -x buzz-relay` aimed at the isolated S0-01 relay
  restarted `buzz-prod-relay-1` four times on 2026-09-04. Every server started over the bridge writes
  a pidfile (`setsid <cmd> </dev/null >log 2>&1 & echo $! > <name>.pid`); stop it with
  `kill "$(cat <name>.pid)"` only after `readlink /proc/$(cat <name>.pid)/exe` shows YOUR binary path;
  diagnose port collisions with `ss -lntp 'sport = :<port>'` + `/proc/<pid>/cgroup`, never with a sweep.
```

### 6.2 Live PC facts from the Wave-0 `pc-bridge` spike (`spikes/pc-bridge/result.json:18`, verbatim `facts.containers`)

```
"containers": "podman 5.7.0, user podman.socket active; podman-compose ABSENT; `docker` binary present but no server; live compose project buzz-prod: postgres:17-alpine, redis:7-alpine, minio RELEASE.2025-09-07, buzz relay (3001->3000), buzz pairing-relay (100.64.254.33:5000); also phoenix 17.26.0 (6006/4317), openobserve (5080), neo4j x2, mirofish/miroshark, osint/analyst stacks",
```

Spike header (`spikes/pc-bridge/result.json:2-6`, verbatim): `"spike_id": "pc-bridge"`,
`"outcome": "positive"`, `"ran_at": "2026-09-03T05:05:20+00:00"`,
`"env_fingerprint": "pc-bridge:fedora:6.17.11-200.fc42.x86_64"`.
Its `classification_effect` (`:29-51`) names S0-03, S0-08, S0-06 — **not S0-02**.

### 6.3 Sandbox venue facts

`spikes/dockerd/result.json:4-6, 24-33` (verbatim): `"outcome": "positive"`,
`env_fingerprint "ccr-sandbox:linux:6.18.44-fc-v24"`, facts `"docker_version": "29.3.1"`,
`"storage_driver": "overlayfs"`, `"network": "outbound pull from Docker Hub succeeded"`,
`"kvm": "ABSENT (/dev/kvm not present)"`; `classification_effect` names S0-08 only.

### 6.4 Observability

`docs/OBSERVABILITY-RUNBOOK.md:44-46` (verbatim):
```
## Status
`NOT built.` here: no exporter, no envelope emitter, no dashboards wired — this runbook records the
live PC endpoints and the lessons so the first telemetry increment starts from facts.
```

### 6.5 Blocked marker

**None.** S0-02 is `execution_proof` (`proofs/registry.yaml:13`); `proofs/registry.yaml` carries a
`blocked` object only for S0-03 (`:14`) and S0-08 (`:19`).

---

## 7. CLASS PREFLIGHT (carried once here; other packs reference this section)

### 7.1 The 18 defect classes — source note

`tasks/briefs/s0-01-b5i-tee-sandbox-fallback.md:101`,
`tasks/briefs/s0-01-b5i-tee-one-sentence-joined-by-equality-honest-census-structural-hang-pin.md:99`
and `tasks/briefs/s0-01-d5l-backend-the-class-closed-structural-ban-record-pinned-one-extras-literal.md:88`
all cite `tasks/briefs/s0-01-sweep-support/SWEEP-prod.md` § "The classes".
**Recorded fact: SWEEP-prod.md contains no heading literally named "The classes"**
(`grep -n "^#" tasks/briefs/s0-01-sweep-support/SWEEP-prod.md` → `## THE TABLE` (`:54`),
`## COUNTS PER CLASS (production file set)` (`:116`), `## DEFECT ROWS RANKED BY BLAST RADIUS`
(`:141`), `## WHAT I COULD NOT RUN, AND WHY` (`:167`), `## RIG / TREE HYGIENE` (`:186`),
`## CURRENCY NOTE (the branch moved mid-sweep)` (`:196`)). The enumerated class list lives in
§ COUNTS PER CLASS; the citing briefs also carry an inline parenthetical enumeration. **Both are
quoted verbatim below.**

### 7.2 `tasks/briefs/s0-01-sweep-support/SWEEP-prod.md:116-139` (verbatim)

```
## COUNTS PER CLASS (production file set)

| class | instances enumerated | RUN | DEFECT | SAFE | DOCUMENTED-LIMIT | EQUIVALENT |
|---|---|---|---|---|---|---|
| 1 presence-gated | 44 | 44 (12 of them by one covering run on `build_capture_record`) | 8 | 22 | 0 | 14 |
| 2 reads outside walk / S_ISREG | 150 receivers, 23 distinct guarded paths | 23 | 7 (6 hangs) | 16 | 0 | 0 |
| 3 stale `[-1]` | 7 | 7 | 1 (not run — PC-only) | 3 | 0 | 3 |
| 4 negative acceptance | 298 raw → 6 genuine | 6 | 0 | 4 | 0 | 2 |
| 5 substring / tail anchors | 138 raw → 4 outcome-classifying | 4 | 2 | 2 | 0 | 0 |
| 6 env-domain fail-opens | 7 | 7 | 2 | 5 | 0 | 0 |
| 7 lossy decodes | 9 | 9 | 1 | 5 | 3 | 0 |
| 8 broad catches | 10 | 10 | 2 | 4 | 0 | 4 |
| 9 waits and polls | 6 | 5 (1 PC-only) | 2 | 2 | 1 | 1 |
| 10 skips | **0** | — | — | — | — | — |
| 11 world-scoped enumerations | 2 | 2 | 1 | 1 | 0 | 0 |
| 12 signal-handler installs | 3 | 3 | 0 | 3 | 0 | 0 |
| 13 `/proc/<pid>/exe` races | 6 | 6 | 2 | 4 | 0 | 0 |
| 14 mirrors | 4 | 4 | 1 | 2 | 0 | 1 |
| 15 counters over different populations | 1 | 1 | 1 | 0 | 0 | 0 |
| 16 provably redundant / dead | 5 | 5 | 0 | 0 | 0 | 5 |
| 17 hardlink-clobbering writes | **0** | — | — | — | — | — |
| 18 other families | 7 | 6 (1 PC-only) | 6 | 0 | 1 | 0 |

**Empty classes (a result): 10 (skips) and 17 (hardlink-clobbering writes) have ZERO production instances.**
```

### 7.3 The briefs' inline enumeration of the same 18 classes (`tasks/briefs/s0-01-b5i-tee-sandbox-fallback.md:100-110`, verbatim)

```
9. **The 18-class self-sweep over YOUR test file(s) (the owner's mandate: classes, not instances).** Run the class list of
   `tasks/briefs/s0-01-sweep-support/SWEEP-prod.md` § "The classes" (presence-gated checks, reads outside the walk / no
   S_ISREG, stale `[-1]` over produced records, negative acceptance assertions, substring/tail anchors classifying outcomes,
   env-domain fail-opens, lossy decodes on a decision path, broad catches, waits/polls + ordinal gates in fakes (AF-AP-57),
   skips/xfails that cannot fire, world-scoped enumerations (AF-AP-59), signal installs before their try (AF-AP-58),
   `/proc/<pid>/exe` races (AF-AP-55), mirrors of the code under test, two counters over different populations asserted
   equal, provably redundant guards, hardlink-clobbering writes, anything else that is a family) over your test files by AST
   or grep, RUN every instance (a mutant or a planted input), and table them: `class | file:line | verdict (DEFECT / SAFE —
   guard named / DOCUMENTED-LIMIT / EQUIVALENT) | the run | fix | red test`. Fix every DEFECT row in THIS round. An Opus-5
   sweep lane is grading the same files in parallel; its table reaches the verifier — a class you missed and it found is a
   blocker, a class you both found is closed. An empty class is a result: say so.
```

### 7.4 AF-AP registry rows whose mechanism names the S0-02 subject (Buzz events, allowlist, signatures, freshness/replay)

All from `docs/INCIDENT-LOG.md` (registry header `:133-143`), quoted verbatim, `id | mechanism |
greppable signature | proven instance | status`.

`:178` (AF-AP-34 — names the Buzz relay directly):
```
| AF-AP-34 | name-based process kill on a shared host — `pkill -x <name>`, `pkill -f <pattern>`, `killall` match EVERY process with that binary name or command line: other installs, container processes (visible in the host table under the bare name), or the caller's own shell carrying the pattern | `pkill`/`killall`/`kill $(pgrep …)` in ops scripts or bridge commands; a stop that names a BINARY instead of reading a pidfile | 2026-09-04: four `pkill -x buzz-relay` aimed at the isolated S0-01 relay each restarted the owner's production `buzz-prod-relay-1` (RestartCount 4; last start 7 s after the last kill); `pkill -f target/release/buzz-relay` killed the bridge shell that carried the pattern | OPEN(2026-09-05) — rule baked (deep-work meta-rules, PC-BRIDGE.md): every server you start writes a pidfile; stop = `kill <pid from YOUR pidfile>` after `readlink /proc/<pid>/exe` or the cgroup line confirms ownership; edit-snapshot screen row; the S0-01 stack teardown must follow it |
```

`:182` (AF-AP-38 — names `BUZZ_ACP_MAX_TURN_DURATION`):
```
| AF-AP-38 | presence instead of exact value — a checker asserts that a configuration/echo field EXISTS or is truthy where the contract pins a VALUE, so drift (and outright contract breaches) pass | `if echo.get(x):` / `assert field` on a contract-pinned value; a capture that echoes a default the contract forbids and still passes | S0-01 2026-09-05: `max_turn` accepted `1s` and the recorded `7200s` while docs/03 pins `BUZZ_ACP_MAX_TURN_DURATION=3600`; four checkers per the owner's review | OPEN(2026-09-05) — every contract-pinned value is asserted EXACTLY against the contract document's value; each exact assertion has a mutant test (one off / default / absent) |
```

`:183` (AF-AP-39 — names `BUZZ_PRIVATE_KEY`):
```
| AF-AP-39 | secret-in-argv launcher — a shell launcher passes a secret through `bash -c "… KEY='$VALUE' …"` / `env -i … KEY=$VALUE cmd`, so the value sits in `/proc/<pid>/cmdline` (world-readable) for the process lifetime and lands verbatim in any `ps`-derived evidence | `env\s+-i[^\n]*(KEY/TOKEN/SECRET)=`, `bash -c "[^"]*(KEY/TOKEN/SECRET)=`, an f-string interpolating a `*KEY*`/`*TOKEN*`/`*SECRET*` value into a command line | S0-01 2026-09-05: the v1/v2 shell launchers carried `BUZZ_PRIVATE_KEY` and `OMNIROUTE_API_KEY` in argv; caught by the coordinator's secret-form grep before any v2 capture (the committed v1 evidence carries no value) | OPEN(2026-09-05) — the launcher builds the env in a Python dict from secret FILES and `Popen(argv, env=…)`; a shell path uses `set -a; . secret.env; exec cmd` — values only ever in the environment; edit-snapshot screen row |
```

`:185` (AF-AP-41 — names the buzz-acp startup line):
```
| AF-AP-41 | last-wins parse of a config echo — `dict(re.findall(…))` (or any last-assignment loop) over a startup line lets a duplicated key token override the real value, so a one-token forgery passes an exact-value gate; sibling: two terminal responses for one request id collapsing to the last one | `dict\(\s*re\.findall`; `for k, v in pairs: d[k] = v` over an echo line with no duplicate check; `by_id[rid] = frame` with no "already seen" Failure | S0-01 2026-09-05 verify round 1: a duplicated `max_turn=3600s` token overrode the real `max_turn=1s` on the buzz-acp startup line; Codex audit of `08a4a7d`: conflicting terminal responses collapsed | OPEN(2026-09-05) — tokenise the whole line, require each pinned key EXACTLY ONCE, compare each value with `==`; a second response for a request id is a Failure, never an overwrite; edit-snapshot screen row |
```

`:186` (AF-AP-42 — names the relay/backend evidence shape):
```
| AF-AP-42 | fixture-shaped hollow green — a synthetic test fixture diverges from the real producer's shape (key case, record layout, token format), so the checker passes the fixture, rejects (or would accept fake) REAL evidence, and the suite cannot notice | a fixture builder for a producer that exists, with no test pinning the builder's output to a committed real sample; the real-bundle CLI test patched, skipped or pointed at throwaway fixtures | S0-01 2026-09-05: the suite's synthetic bundle used a lowercase `host` header key while the real backend stored the wire case — the checker could never pass real evidence; `test_cli_pass_path_fails_on_golden_pin` read the tracked fixtures a lane had overwritten | OPEN(2026-09-05) — every fixture builder is pinned to ONE committed real producer sample (key set + case + format asserted equal); the real-bundle CLI test runs unpatched; the real-leg conformance section grades every per-leg check against real PC captures (`--fixtures-dir` keeps tests off the tracked fixtures); recurrence 2 (2026-09-06, Codex audit of 541648c): the synthetic shutdown fixture carried a `/sbin/init` row the producer can never emit and `test_real_leg_process_evidence` had no body — fixtures now come from RUNNING `pc_post.sh scan` (tests/test_s0_01_pc_post_scan.py) |
```

`:167` (AF-AP-23 — allow-list mechanism; S0-02's positive gate is an allowlist):
```
| AF-AP-23 | OPEN-ENDED filter passed off as an allow-list — a credential stripper keyed on a NAME blacklist, a sweep gated on a FILE-EXTENSION allowlist, OR an env allow-list keyed on a NAME PREFIX (`RUBRIC_*`): each silently passes an out-of-set member. A prefix is not a closed set. | an env "clean" builder that `continue`s on named keys / a suffix set; a sweep `if path.suffix not in (…)`; `k.startswith("RUBRIC_")` (or any prefix) as the env allow rule | S0-11 round 1: `_clean_env` blacklist + `.py`/`.sh`-only sweep. S0-11 round 2: the "fix" allow-listed every `RUBRIC_*` by prefix → `RUBRIC_PRODUCTION_API_KEY` passed (owner review 2026-09-04). | SWEPT(2026-09-04 r2) — env is now a CLOSED EXACT set (`ENV_ALLOWLIST ∪ {RUBRIC_TASK_ID,RUBRIC_CWD,RUBRIC_PROBE_PORT}`, no prefix); `test_allowlist_is_closed_exact_set`. Design signature. RECURRED once as a prefix — the fix for a blacklist must be an EXACT allow-list, never a prefix. |
```

`:191` (AF-AP-47 — guard narrowed to a specimen; the four-distinct-reasons rule is a domain gate):
```
| AF-AP-47 | guard narrowed to serve a specimen — a fix that changes a guard's condition to admit one reported value (`Content-Length: 0` must be served → `if cl > 0:` around the reject) silently widens the ACCEPTED domain to every value the new condition does not name (all negatives, `-0`), re-opening the arm below; the specimen test goes green, the previous build's refusal is lost, and nothing tests the widened side | a reject block moved INSIDE a narrowed `if` / a condition changed from `is not None` to `> 0` (or the reverse) with tests only on the named value; a deny-list guard extended by one case per review round | 2026-09-06 D5b: round 5 refused `GET` + `Content-Length: -1` (400, 0 records); round 6 served it and smuggled a forged upstream record — found by the round-6 verifier's domain probe | OPEN(2026-09-06) — guards are ALLOW-LISTS over the whole input domain with table-driven tests over the domain (values × routes × credential), each rejection proven with a forged tail; a fix that touches a guard condition ships the negative side of the change as a test (the value the old guard refused must still be refused) |
```

### 7.5 AF-AP rows that bind EVERY mint (quoted once here; referenced by all six packs)

`:180` (AF-AP-36 — pre-mint gate):
```
| AF-AP-36 | mint-before-mutants — a proof artifact (result.json / PRESENT) is minted while reviewer-reported mutations of its evidence still pass the checker, because the findings were fixed as prose or specimens instead of committed failing tests | a review that lists concrete mutations followed by a commit that mints or re-mints the artifact without a test per mutation; a checker whose tests pass only the builder's own bundle | S0-11 seven closure rounds + S0-01 2026-09-05 (five mutations, all PASS after minting) | OPEN(2026-09-05) — PRE-MINT GATE: every reported mutation becomes a committed failing regression test BEFORE the artifact exists; the checker is graded against hostile bundles (adversarial verify lane), never only the golden one; rule baked in build-loop + CLAUDE.md; recurrence (2026-09-06): the ledger's checkpoint-5 block listed a two-POST-per-window GATE that was only a fixture shape, and the 2026-09-05 entry's REPAIR sentence read as delivered — prose claims are bound to a named test or marked PLAN |
```

`:200` (AF-AP-56 — attested inputs):
```
| AF-AP-56 | attested-input change without regeneration — an edit to a file that minted artifacts attest by hash (a schema, the runner, the validator, the registry, a proof's own inputs) flips every dependent artifact INVALID; the venue gates that run the touched suites stay green because none of them runs the integrity check | a diff under `proofs/schemas/`, `scripts/proof-runner`, `scripts/validate-ledger`, `proofs/registry.yaml`, or `proofs/<minted>/`; CI red on `attestation-mismatch` after a green lane gate | regenerate the dependent artifacts in the same increment (`proof-runner run`), then `validate-ledger integrity` + `ledger-gen` + `git diff --exit-code proofs/ledger.json` in the gate; name the attested paths in any brief whose boundary touches one | 2026-09-06 CI runs 106-110, checkpoint 8j |
```

`:171` (AF-AP-27 — a frozen seed contract changes only by owner decision):
```
| AF-AP-27 | a FROZEN contract (seed/registry) reshaped in an implementation without an explicit owner decision — the negative control the seed pinned is deleted or its reason changed under cover of an unrelated fix | a spec/registry edit that drops or rewrites a seed-declared `negative_control`/`expected_failure_reason`/frozen mapping; the change appears only in the diff, never surfaced | S0-11 round-1 deleted the frozen `rubric-isolation-violation: credential env absent by construction` control; registry repair reshaped mappings (owner: "2 examples") | SWEPT(2026-09-04) — frozen credential control restored as its own leg, four-axis added as an ADDITIONAL leg; the spec test asserts the frozen reason is present. Rule = a frozen contract changes only by an explicit owner decision, never as a side effect. Process signature |
```

`:173` (AF-AP-29 — the canonical contract must be at least as strong as the strongest test):
```
| AF-AP-29 | the machine-checkable CONTRACT is weaker than the test — the canonical runner accepts a result a committed test would reject (a spec `failure_reason` prefix vs the full reason; a schema looser than an assertion) | a proof/spec `expect.failure_reason` that is a prefix/substring while the test asserts the complete string; any canonical gate laxer than the strongest test of the same property | S0-11 round-2 spec required only `rubric-isolation-violation:`; the test required all axes, so a one-axis result passed the runner | SWEPT(2026-09-04) — the spec pins the COMPLETE deterministic reason (the venue-stable pair `…: env-not-allowlisted,netns-not-isolated`; the uid axis is venue-dependent so it is not in the pinned reason, and is exercised by the positive non-vacuity gate on a root venue); `test_spec_valid_and_contract_matches_test`. Rule = the canonical contract is at least as strong as the strongest test of the same claim. Process signature |
```

`:174` (AF-AP-30 — specimen-only remediation, the meta-class; verbatim, whole row):
```
| AF-AP-30 | specimen-only remediation — a review's named cases are fixed and the whole CLASS declared closed, so the same defect re-appears one equivalent out (prefix→exact, blacklist→prefix, regex→AST, child-report→parent-observe) | a "fixed" claim after a review whose tests cover only the reported instances; no equivalence-class mutants (alias/computed/defaulted forms, boundary values, the observe-vs-report axis) | S0-11 reopened FIVE times (rounds 1→2→3→cycle-4→cycle-5); each fix passed its own cases and the next review broke the adjacent equivalent (blacklist→prefix→exact; regex→AST→policy-block; child-report→parent-observe; net-tautology→active-probe-fail-open→required-paired-control; pytest-gate→CLI-gate→canonical-runner-defer; claimed-cwd→observed-cwd→writable/collected-cwd; artifact-trusted→artifact-bound-to-source→bound-to-the-COMPLETE-closure; acceptance word-ban→hidden-marker→visible-single-source-owner-anchored) | OPEN (meta-class; the discipline, not a single site) — recurrence count 8 (cycle-8: the cycle-7 status guard fixed the hidden-marker and self-accept SPECIMENS but left the slug-keyed-row equivalent — a canonical-slug `DONE` row passed because only BARE-id rows were rejected; the class "authoritative review state across surfaces" needed the one visible `PROOF-STATUS` marker BOUND to the one canonical task row via an EXACT proof→slug map. This is where the meta-class finally resolved: the owner accepted the proof as a process decision and moved the residual anchor work to a separate task, so the loop ends by naming the guard's real scope rather than fixing an eighth equivalent) (cycle-7: the cycle-6 status guard fixed the word-ban SPECIMEN but left three equivalents — a hidden marker diverging from a visible row, an arbitrary self-accept file, and that file breaking the attestation; the class "authoritative review state" needed a single visible source + no coordinator-writable acceptance) (cycle-6: the cycle-5 attestation bound only the proof-local files, so mutating the RUNNER/VALIDATOR left the green standing, and the validator never compared the recorded runs to the attested spec — the class "trust binding" was fixed for the named files and left open for the tooling that runs/checks them). Mitigation: `anti-hollow-green` now mandates EQUIVALENCE-CLASS mutation testing (test the class, not the specimen), binding the COMPLETE trust closure (every file that produces OR checks the verdict), and exercising the CANONICAL CONSUMER under both a capable and an incapable environment. The tell: a review that clears the named cases is the moment to attack the class before claiming closure. Behavioral signature; recurrence 9 (2026-09-05, S0-01: five owner mutations passed the checker after minting — the class is the missing pre-mint gate, AF-AP-36); recurrence 10 (2026-09-06, backend framing gate: D5 → D5b → D5c, three rounds of vector-by-vector closure each leaving the adjacent equivalent open — resolved by the allow-list redesign, AF-AP-47) |
```

Where the remaining cross-referenced rows are quoted verbatim: `:148` (AF-AP-4) in
material-S0-03.md §7.1 and material-S0-08.md §7.1 · `:184` (AF-AP-40) in material-S0-04.md §7.1 ·
`:169` (AF-AP-25) in material-S0-08.md §7.1 · `:195` (AF-AP-51) in material-S0-05.md §7.1.
The registry runs AF-AP-1 … AF-AP-61 (`docs/INCIDENT-LOG.md:145-203`, table rows; header
`:133-143`).
