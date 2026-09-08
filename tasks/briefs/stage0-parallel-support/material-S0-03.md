# MATERIAL PACK — S0-03 (Hermes → OmniRoute live round trip, credential-gated)

> EVIDENCE ONLY. Verbatim extraction + located inventory. No design, no judgement, no
> recommendation. Assembled 2026-09-07 from the working tree at branch
> `claude/soundbox-kit-migration-iz1jwf`, HEAD `cc46704`. Other lanes hold uncommitted edits.
> **The 18 defect classes and the mint-wide AF-AP rows are carried once in
> `material-S0-02.md` §7 — read that section with this pack.**

---

## 0. INVENTORY TABLE

| item | source file:line | exists? | venue |
|---|---|---|---|
| Seed per-proof block S0-03 | `seeds/seed-stage0-v1.yaml:382-405` | yes | — |
| Seed header owner-answer note on S0-03 | `seeds/seed-stage0-v1.yaml:17-22` | yes | — |
| Frozen `spike_to_class_mapping` — seed | `seeds/seed-stage0-v1.yaml:564-586` | **partial** — no `pc-bridge` rule in the seed | — |
| `spike_to_class_mapping` — registry (`pc-bridge` added) | `proofs/registry.yaml:27, 34` | yes | — |
| Breakdown increment #14 | `tasks/stage0-breakdown.md:65` | yes | PC |
| Owner answer #14 / KC-2 | `tasks/stage0-breakdown.md:85-87` | yes | PC |
| Findings per-proof constraint | `docs/research/FINDINGS-STAGE0-v1.md:44` | yes | — |
| Findings §6a addendum 2 (fourth class) | `docs/research/FINDINGS-STAGE0-v1.md:109-112` | yes | — |
| Council KC-2 | `docs/research/COUNCIL-VERDICT-STAGE0-v1.md:34` | yes | — |
| Plan-doc seam `docs/03` §2 | `docs/03_INTEGRATION_CONTRACTS.md:31-51` | yes | — |
| ADR 0002 | `docs/adr/0002-omniroute-sole-model-egress.md:1-16` | yes | — |
| Decision D-019 (OmniRoute pin advance) | `docs/08_DECISION_LOG.md:25` | yes | — |
| upstream pin `omniroute` | `upstream.lock.yaml:21-26` | yes | — |
| `proofs/S0-03/` directory | `ls -la proofs/S0-03/` | yes — 3 files | — |
| `proofs/S0-03/blocked.json` | (whole file in §5.2) | yes | recorded `pc-bridge:fedora` |
| `proofs/S0-03/probe.json` | (whole file in §5.2) | yes | — |
| `proofs/S0-03/probe_omniroute.py` | (whole file in §5.2) | yes | either |
| `proofs/S0-03/spec.json` | — | **no** | — |
| `proofs/S0-03/result.json` | — | **no**; ledger state `BLOCKED` | — |
| Any S0-03 fixture / checker | — | **no** | — |
| Registry entry S0-03 | `proofs/registry.yaml:14` | yes | — |
| Blocked-marker schema | `proofs/schemas/blocked.schema.json:1-53` | yes | — |
| Probe schema | `proofs/schemas/probe.schema.json:1-21` | yes | — |
| Runner probe path | `scripts/proof-runner:226-271` | yes | either |
| Validator's S0-03-specific rule | `scripts/validate-ledger:336-338` | yes | — |
| Wave-0 spike `pc-bridge` (flips S0-03) | `spikes/pc-bridge/result.json:29-36` | yes — POSITIVE | PC |
| OmniRoute live on the PC | `spikes/pc-bridge/result.json:19`; `PC-BRIDGE.md:153-163` | yes | PC |
| vLLM upstream `sim9b` | `spikes/pc-bridge/result.json:20`; `PC-BRIDGE.md:61` | yes | PC |
| Transport deviation (`chat_completions` vs `codex_responses`) | `docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md:17` | yes — OPEN owner decision (task #35) | PC |
| `REQUIRE_API_KEY=true` state | `docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md:15` | yes — RESOLVED 2026-09-05 | PC |
| OmniRoute invariants monitor | `scripts/omniroute_invariants.sh:1-23` | yes | PC |
| Ledger task row | `todo/BUILD-TASKLIST.md:71` (`s0-14-s0-03-omniroute-roundtrip … pending`) | yes | PC |

---

## 1. THE SEED

### 1.1 `seeds/seed-stage0-v1.yaml:382-405` (verbatim)

```yaml
- proof_id: S0-03
  classification: blocked_credential
  wave: 2
  increment_index: 14
  ledger_denominator: blocked_external_input
  spike_dependency: []
  fixture_format: live round trip only — the S0-04 deterministic stub is FORBIDDEN here
  assertions:
  - a /v1/responses request through real OmniRoute streams text and completes a real
    Hermes tool-call round trip
  - the pass asserts upstream model identity (response model id + non-stub fingerprint),
    never a bare 200
  - Hermes holds no upstream provider key (env assertion) and OmniRoute failure does not
    trigger direct fallback
  negative_control:
    kill_switch: disable the credential -> the proof goes RED
    expected_failure_reason: 'blocked: credential_absent'
  blocked_marker:
    probe: secret-presence check, then (only when present) one authenticated no-op via OmniRoute
    reason_enum: [credential_absent, credential_rejected]
    rule: credential_rejected maps to proof-RED, never to blocked; probe re-runs every CI
      execution; probe success flips the deferral RED (deferral_expired)
    unblock_condition: 'secret OMNIROUTE_UPSTREAM_KEY present and accepted'
  owner_placeholder: TBD-owner-credential
```

### 1.2 Seed header note declaring the S0-03 transition (`seeds/seed-stage0-v1.yaml:17-22`, verbatim)

```
# Owner answers (2026-09-03), superseding the placeholders in-body: the execution
# host is the owner's PC via the token-gated bridge (PC-BRIDGE.md). S0-08's host
# = the PC (bare-metal KVM). S0-03's "credential" = the PC's local vLLM endpoint
# behind OmniRoute (identity `sim9b`); a `pc-bridge` Wave-0 spike is added and
# its positive result is a DECLARED transition S0-03: blocked_credential ->
# execution_proof (increment 1 adds it to spike_to_class_mapping).
```

### 1.3 The frozen mapping entry

**In the seed:** `seeds/seed-stage0-v1.yaml:564-586` declares rules for `rust-ai-memory`,
`runsc`, `dockerd`, `selective-egress` only — **no `pc-bridge` rule, and no rule whose
`affected_proof` is S0-03.** The seed's S0-03 block carries `spike_dependency: []` (`:387`).

**In the registry (the machine-read source):** `proofs/registry.yaml:34` (verbatim):

```json
  {"spike": "pc-bridge", "probe": "probe the owner PC for OmniRoute identity and gVisor host capability", "positive_effect": {"affected_proof": "S0-03", "from_class": "blocked_credential", "to_class": "execution_proof", "rule_id": "map-pcbridge-s003"}, "negative_effect": {"affected_proof": "S0-08", "from_class": "blocked_host", "to_class": "blocked_host", "rule_id": "map-pcbridge-s008"}}
```

with the coordinator decision recorded in-file at `proofs/registry.yaml:27` (verbatim):

```
# COORDINATOR DECISION — ADDITION (owner answer 2026-09-03): pc-bridge joins the frozen mapping through the two rule ids already recorded by its existing artifact; any spike may cite a declared rule whose probe satisfies the rule's negative or positive branch.
```

`proofs/registry.yaml:14` records `"spike_dependencies": ["pc-bridge"]` for S0-03 — i.e. the
registry's S0-03 dependency list differs from the seed's empty list.

### 1.4 Seed constraints binding S0-03 (`seeds/seed-stage0-v1.yaml:106-117`, verbatim excerpts)

```yaml
- Execution proofs are exactly S0-01, S0-02, S0-04, S0-05-mechanism, S0-07, S0-11;
  conformance-checked decisions are exactly S0-09, S0-10, S0-12
- S0-03 is blocked on a real model credential and its pass condition must assert upstream
  model identity, not merely a successful response
- Every proof ships a spec-time negative control that fails for a named exact reason
- All gates are deterministic and LLM-free; no LLM judge anywhere in the gate spine
- Owner questions (credential owner, gVisor host owner, Buzz hosting) are out of scope
  and are represented by placeholders in the Seed
```

---

## 2. THE BREAKDOWN

### 2.1 Increment #14 (`tasks/stage0-breakdown.md:65`, verbatim row)

```
| 14 | S0-03 Hermes→OmniRoute live round trip | `proofs/s0-03/` fixtures + runner ready; marker live from #2 | Streams text + real tool-call round trip via real OmniRoute; pass asserts upstream model identity; no upstream key in Hermes; OmniRoute failure ⇒ no fallback | Credential-disable kill switch ⇒ RED (`blocked: credential_absent`); S0-04 stub FORBIDDEN here | RED-pending real credential (owner TBD-owner-credential); needs add_repo OmniRoute |
```

### 2.2 Pinned decision with its rejected alternative (`tasks/stage0-breakdown.md:25`, verbatim)

```
| S0-03 blocks on a real credential; pass asserts upstream model identity, never a 200; the S0-04 stub is forbidden for S0-03 | Run S0-03 against the S0-04 stub (stub-drift hollow green) | council (Socrates) |
```

Also binding (`:22`, verbatim):
```
| Blocked markers carry a probe run re-evaluated every CI run; `credential_rejected` ⇒ proof-RED, never blocked; blocker gone ⇒ `deferral_expired` RED | Static marker checked for presence | interview Q5 |
```

The full pinned-decision table is quoted in `material-S0-02.md` §2.2.

### 2.3 Owner answer (`tasks/stage0-breakdown.md:84-87`, verbatim)

```
## Owner answers (2026-09-03)
- **#14 / KC-2:** credential = the PC's local vLLM endpoint behind OmniRoute. S0-03 is no longer
  blocked-on-external-input once the bridge is up; its class flips to execution via the
  `pc-bridge` spike (declared transition — add to `spike_to_class_mapping` in increment #1).
```

Original (now-answered) question kept in the file (`:92`, verbatim):
```
- **#14 / KC-2:** who supplies the real upstream model credential for S0-03, and by when? If none exists when Wave 2 opens, S0-03 stays RED-pending (never runs against the stub).
```

### 2.4 Venue update (`tasks/stage0-breakdown.md:28-38`) — S0-03 clauses (verbatim excerpt)

```
podman-compose stacks for S0-01/S0-02 (#7, #8), S0-03/S0-04 (#14, #15) and
S0-06 (#13); S0-05's full canaries (#16). S0-03's upstream = the PC's local vLLM
(`localhost:8010/v1`, identity `sim9b`) behind OmniRoute — the credential question is closed.
```

Full section quoted in `material-S0-02.md` §2.3.

### 2.5 Ordering rationale clause (`tasks/stage0-breakdown.md:74-75`, verbatim excerpt)

```
#14–16 the
spine (credential-gated S0-03 first so its RED-pending state is visible early); #17 spec now, run
later;
```

### 2.6 NOT-built ledger lines touching S0-03

Breakdown-time (`tasks/stage0-breakdown.md:79-82`): "Nothing below exists yet: … any proof, any
fixture …". Live ledger (`todo/BUILD-TASKLIST.md:32`, verbatim excerpt): "**BLOCKED 2 — S0-03
(credential) and S0-08 (host; marker EXPIRED).**"

Live ledger row (`todo/BUILD-TASKLIST.md:71`, verbatim):
```
| s0-14-s0-03-omniroute-roundtrip | #14 S0-03 Hermes→OmniRoute live round trip (OmniRoute already up on the PC; identity = routed model id) | pending | s0-02 | tool-call round trip; upstream identity asserted; key-disable → RED; stub FORBIDDEN |
```

`todo/BUILD-TASKLIST.md:250-251` (verbatim excerpt) — an S0-03-adjacent fact recorded during
S0-01:
```
in `proofs/S0-01/evidence/turn-*/`, every frame v1-conformant (`tests/test_s0_01_turn_capture.py`, 5 tests). Credential
NOT validated (plane open; Hermes' key is in no key-table row) — not S0-03 evidence.
```

---

## 3. FINDINGS + COUNCIL

### 3.1 Capability-ledger and environment rows

Capability ledger — see `material-S0-02.md` §3.1 (verbatim,
`docs/research/FINDINGS-STAGE0-v1.md:9-15`); the "Absent" cell names "all Stage 0 proofs".

Environment row that decides S0-03's venue (`docs/research/FINDINGS-STAGE0-v1.md:28`, verbatim):

```
| **PC bridge** (learned 2026-09-03 from the owner) | The owner's PC is the execution host: Fedora 42 bare metal (KVM), podman + podman-compose, local vLLM OpenAI-compatible endpoint `localhost:8010/v1` (`sim9b`), reached via a token-gated HTTP bridge with per-session ephemeral links (`PC-BRIDGE.md`) | S0-08 (runsc/KVM), all container stacks (Buzz relay, OmniRoute, ai-memory), and S0-03's model upstream run THERE. No third-party model credential is needed: OmniRoute's upstream = the PC's vLLM, identity asserted as `sim9b` |
```

Also (`:22`, verbatim): "| Node 22.22.2 / npm 10.9.7 | present | OmniRoute (3.8.51, Node)
plausibly runnable in-sandbox |".

### 3.2 Per-proof constraint (`docs/research/FINDINGS-STAGE0-v1.md:44`, verbatim)

```
| S0-03 | Hermes→OmniRoute | `codex_responses` provider, key_env only, no upstream key in Hermes, real tool-call round trip; failure ≠ fallback (`03` §2) |
```

### 3.3 Cross-cutting invariant naming S0-03's forbidden stub (`docs/research/FINDINGS-STAGE0-v1.md:57-59`, verbatim)

```
- NO STUBS in the spine (CLAUDE.md #1): every proof exercises the REAL pinned component; the
  one sanctioned stub is S0-04's deterministic upstream-request-preservation instrument, which
  sits BEHIND real OmniRoute at the boundary the plan itself specifies.
```

### 3.4 Open questions (`docs/research/FINDINGS-STAGE0-v1.md:79-90`, verbatim)

```
**PATH 2 — RESOLVED by the owner 2026-09-03 ("the system runs on my PC via the PC bridge"):**
gVisor host = the PC (bare-metal Fedora 42, KVM); S0-03 credential = the PC's local vLLM behind
OmniRoute (no third-party key); container stacks = podman on the PC. Ordering preference not
stated → parallel-by-component stands. Original questions kept below for the record.

**PATH 2 (as originally posed):**
1. Stage 0 ordering/parallelism: strict S0-01→S0-12 vs seam-parallel batches (spine proofs
   S0-01…S0-05 first, decisions S0-09/S0-10/S0-12 interleaved)?
2. Is a bridged host (real VM with gVisor+docker) planned for S0-08, or should Stage 0 accept
   spec+canary-fixture evidence with live execution deferred to Stage 1 infrastructure?
3. Which OmniRoute upstream provider(s) get real credentials for S0-03's live round trip, and
   who supplies them (secrets never enter the repo)?
```

### 3.5 Chairman addendum 2 — the fourth class (`docs/research/FINDINGS-STAGE0-v1.md:109-112`, verbatim)

```
2. **The three-way classification covers 11 of 12 proofs — S0-03 is unclassified.** It needs a
   FOURTH class: *execution proof blocked on an external input* (a real upstream credential —
   procurable on a different timescale/owner than S0-08's host). Ledger denominators are
   therefore four-way; no status line may read a flat "N/12".
```

### 3.6 Council verdict lines that touch S0-03 (verbatim)

Acceptable compromise 2 (`docs/research/COUNCIL-VERDICT-STAGE0-v1.md:27`):
```
2. **S0-04's deterministic upstream stub stands as the one sanctioned instrument**, because the plan itself specifies it at the boundary behind real OmniRoute (findings §4). This is a boundary instrument, not a spine stub.
```

Kill Criterion 2 (`:34`):
```
2. **If no named owner and date for a real upstream credential exists by the close of the first Wave-1 execution session**, S0-03 must be marked RED-pending and Stage 1 must not open. Running S0-03 against S0-04's stub invalidates the verdict outright.
```

Unresolved question 1 (`:45`):
```
1. **Who supplies S0-03's real upstream credential, and by when?** Open in findings §5 PATH-2 #3 *before* the council convened, and still open after three rounds. Socrates' closing question is the sharpest form: if no credential exists when Wave 2 opens, does S0-03 block RED-pending, or run against S0-04's stub — and if the latter, **what assertion distinguishes a real model answer from the stub?** No member offered one. If none exists, Stage 0's most load-bearing green is hollow by construction.
```

Unresolved question 2 (`:46`):
```
2. **Which class does S0-03 occupy?** The crystallized three-way split enumerates 7 + 3 + 1 = **11 of 12**. S0-03 is unenumerated. It appears to need a fourth class — *execution proof blocked on an external input* — structurally distinct from S0-08's *blocked on a kernel feature*, because a credential is procurable on a different timescale and by a different owner than a host.
```

Consensus, load-bearing agreement 4 (`:68`):
```
- **S0-03 blocks on a real credential, and a pass must assert upstream model identity — never a 200.** Socrates held this from R1 through R3 unopposed; it is the pack's single most important assertion.
```

Socrates' key insight (`:75`):
```
- **Socrates** — *stub-drift as the pack's characteristic hollow green.* S0-03 and S0-04 both terminate at OmniRoute's upstream edge; if S0-03 runs against the sanctioned S0-04 instrument, the instrument silently becomes the spine and S0-03 proves only that Hermes reaches OmniRoute — never that a model answered. The remedy (assert upstream model identity, with a credential-disable kill switch) is the strongest single control the council produced. Equally sharp: a gate that cannot fail is not a proof, and counting it inflates the denominator.
```

Chairman reservation (`:88`):
```
- **Chairman's reservation — not a member position, recorded so it is not mistaken for one.** The unanimity settled proof *ordering* while leaving both of Stage 0's genuine external dependencies unowned: S0-03's credential and S0-08's host. A plan can be perfectly ordered and still stall on inputs nobody was assigned to procure. I would not treat the unanimous verdict as authorizing Wave 1 until question 1 has a named owner.
```

Follow-up Trigger B (`:97`, verbatim excerpt):
```
**Trigger B:** the owner answers the S0-03 credential question — if the answer is "no credential available," the council must return to design the identity assertion Socrates demanded, or formally re-scope S0-03, before Wave 2 opens.
```

Recommended next step 4 (`:58`):
```
4. Put question 1 to the owner as a PATH-2 text question *now*, in parallel with Wave 0, rather than at Wave 2's opening — the answer has a procurement lead time the schedule cannot absorb late.
```

---

## 4. PLAN-DOC SEAMS AND PINS

### 4.1 `docs/03_INTEGRATION_CONTRACTS.md:31-51` (verbatim — §2 Hermes → OmniRoute)

```
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
```

### 4.2 `docs/02_COMPONENT_AUDIT.md:49-56` (verbatim — OmniRoute)

```
### OmniRoute — sole model/embedding API egress

- MIT; observed version 3.8.51; native `/v1/responses` and tool calls; final image user `node`.
- Persist state and configure `JWT_SECRET`, `API_KEY_SECRET`, `STORAGE_ENCRYPTION_KEY`, `DATA_DIR`, and a non-default `INITIAL_PASSWORD`.
- Provider setup is stateful through setup/dashboard workflows, not just an upstream key environment variable.
- The old `OMNIROUTE_COMPRESSION_CODE_LANE` variable is unsupported. Send `x-omniroute-compression: off`, assert `X-OmniRoute-Compression`, and compare a deterministic stub request at the boundary.
- Size memory from concurrent long Responses measurements; 1 GiB is not an accepted estimate.
- OmniRoute is sole model API egress, not automatically sole web/tool egress.
```

`docs/02_COMPONENT_AUDIT.md:26-28` (verbatim — the Hermes side of the same seam):
```
- Native ACP server is available as `hermes-acp` / `hermes acp` with the optional ACP dependency.
- Custom providers support `base_url`, `api_mode`, `key_env`, and `extra_headers`.
- Select `codex_responses` through OmniRoute; do not enable `codex_app_server` or OpenAI Codex OAuth in v1.
```

### 4.3 `docs/01_ARCHITECTURE.md` (verbatim lines)

`:13` — "Hermes sends every model request through OmniRoute. A Codex-capable model is selected
through Hermes' `codex_responses` provider mode; that does not create a second runtime."
`:95` — "- OmniRoute failure fails the model turn; Hermes never falls back to a direct provider."
`:118` — "| Hermes → OmniRoute | Internal scoped key, fixed base URL, no upstream keys, compression assertion |"
`:21` — "| Model routing | OmniRoute | Sole model/embedding API egress, provider credentials, route selection |"

### 4.4 `docs/05_SECURITY.md` (verbatim lines)

`:6` — "2. All model/embedding API traffic goes through OmniRoute."
`:21` — "| Direct model egress | No upstream keys, network enforcement | DNS/connection canaries and egress logs |"
`:79` — "| Hermes | OmniRoute, composite memory adapter, policy, approved tool broker |"
`:82` — "| OmniRoute | Approved model providers and persistence dependencies |"
`:89-90` (§7 Secrets) —
```
- OmniRoute alone owns upstream provider credentials.
- Hermes owns a scoped OmniRoute key; Buzz identity/relay credentials remain in the interaction boundary.
```
`:102` — "- Hermes, ai-memory, dream, JIT, evaluator, PandaProbe, and conditional HarnessRouter cannot reach providers directly."

### 4.5 `docs/09_PREMORTEM.md` (verbatim lines)

`:8` — "| 2 | OmniRoute works for text but corrupts/drops tool calls | Text test passes; tool args change or hang | Real tool round-trip and deterministic gateway fixture |"
`:19` — "| 13 | Direct provider path returns during debugging | Upstream key in a non-OmniRoute service | Secret ownership rule, egress deny, recurring canaries |"
`:23` — "| 17 | OmniRoute OOMs on long concurrent Responses | Restarts during realistic coding runs | Measured concurrency profile and resource sizing |"
`:34` (stop-the-line) — "- any component reaches a model provider without OmniRoute;"

### 4.6 `docs/07_BUILD_PLAN.md:11` (verbatim)

```
| S0-03 | Hermes→OmniRoute | Text and real tool-call round trip over `codex_responses` |
```

`docs/07_BUILD_PLAN.md:27` (Stage 1) — "- OmniRoute persistence, secure bootstrap, and one tested
`codex_responses` route."

### 4.7 `docs/adr/0002-omniroute-sole-model-egress.md` (verbatim, whole file)

```
# ADR 0002 — OmniRoute is the sole model API egress

- Status: accepted
- Date: 2026-09-02

## Context

Direct model providers in Hermes, ai-memory, or evaluators would scatter credentials and make routing, cost, logging, and failover policy hard to prove.

## Decision

All model and embedding traffic uses internal, scoped OmniRoute credentials and tested routes. Provider credentials exist only in OmniRoute. Hermes uses `codex_responses` against the internal `/v1` endpoint and sends the compression-off header.

## Consequences

OmniRoute is a critical dependency and must be persistent, monitored, and load-tested. Direct fallback is prohibited. Tool/web egress is a different boundary and still needs its own proxy and policy.
```

### 4.8 `docs/08_DECISION_LOG.md:25` (verbatim — D-019, the pin advance and its security reason)

```
| D-019 | Advance OmniRoute pin to `488f57e9` (HEAD, v3.8.51) and GBrain pin to `8c70f625` (HEAD, v0.48.2.0) | OmniRoute: the prior pin (`500568a1`) predates GHSA-5926-2w35-7h4q — a credential-export vulnerability where `POST /api/providers/{id}/claude-auth/export` and `.../codex-auth/export` fail open under `requireLogin=false` (the local-first default). The PC's OmniRoute listens on `0.0.0.0:20128`, making this actively relevant. Fix landed at commit `49c4a620` (PR #12600); the new pin includes it. GBrain: the prior pin (`e9a14c9`, v0.48.1.0) missed the `no_key fail-open` fix and storage scope fix shipped in v0.48.2.0. PC action: the owner must upgrade OmniRoute from npm 3.8.48 to at least a git-source build at `488f57e9` — the fix is NOT on npm (latest 3.8.50 predates it). |
```

Related open owner input (`docs/08_DECISION_LOG.md:44`): "4. First OmniRoute provider/model route
and budget."

### 4.9 `upstream.lock.yaml:21-26` (verbatim)

```yaml
  omniroute:
    repository: https://github.com/diegosouzapw/OmniRoute.git
    commit: 488f57e9d3fccc8d1741fdf21d35d5730b118a18
    observed_version: 3.8.51
    license: MIT
    role: sole_model_api_gateway
```

and `upstream.lock.yaml:10-15` (verbatim):

```yaml
  hermes-agent:
    repository: https://github.com/NousResearch/hermes-agent.git
    commit: 527da60844d4dced37879ea50259675371abe10e
    observed_version: 0.21.0
    license: MIT
    role: main_production_workhorse_and_native_acp_server
```

`upstream.lock.yaml:2` — `snapshot_date: "2026-09-04"`.

### 4.10 `.env.example` (verbatim line 24)

```
OMNIROUTE_INTERNAL_API_KEY=replace-from-omniroute-key-creation
```

**Naming discrepancy, recorded not resolved:** the seed's `unblock_condition` names
`OMNIROUTE_UPSTREAM_KEY` (`seeds/seed-stage0-v1.yaml:404`); `docs/03` §2 and `.env.example` name
`OMNIROUTE_INTERNAL_API_KEY`; the committed probe reads `OMNIROUTE_API_KEY`
(`proofs/S0-03/probe.json` `key_env`, `proofs/S0-03/probe_omniroute.py:10`).

---

## 5. WHAT EXISTS TODAY

### 5.1 `ls -la proofs/S0-03/`

```
total 20
drwxr-xr-x  2 root root 4096 Sep  3 18:40 .
drwxr-xr-x 11 root root 4096 Sep  4 20:00 ..
-rw-r--r--  1 root root  922 Sep  3 18:40 blocked.json
-rw-r--r--  1 root root  280 Sep  3 18:40 probe.json
-rwxr-xr-x  1 root root  702 Sep  3 18:40 probe_omniroute.py
```

No `spec.json`, no `result.json`, no `fixtures/`, no checker.

### 5.2 Verbatim content of every file in `proofs/S0-03/`

**`proofs/S0-03/blocked.json`:**

```json
{
  "proof_id": "S0-03",
  "classification": "blocked_credential",
  "env_fingerprint": "pc-bridge:fedora",
  "marker": {
    "probe_cmd": [
      "python3",
      "proofs/S0-03/probe_omniroute.py",
      "http://127.0.0.1:20128/v1/models"
    ],
    "probe_run": {
      "leg": "negative",
      "cmd": [
        "python3",
        "proofs/S0-03/probe_omniroute.py",
        "http://127.0.0.1:20128/v1/models"
      ],
      "started_at": "2026-09-03T18:33:34.401518Z",
      "finished_at": "2026-09-03T18:33:34.505499Z",
      "exit_code": 10,
      "stdout_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    },
    "blocker_status": "absent",
    "unblock_condition": "secret OMNIROUTE_UPSTREAM_KEY present and accepted",
    "owner": "TBD-owner-credential",
    "reason": "credential_absent"
  }
}
```

(`e3b0c442…b855` is the sha256 of the empty string — both streams empty.)

**`proofs/S0-03/probe.json`:**

```json
{
  "proof_id": "S0-03",
  "probe_cmd": [
    "python3",
    "proofs/S0-03/probe_omniroute.py",
    "http://127.0.0.1:20128/v1/models"
  ],
  "timeout_s": 10,
  "key_env": "OMNIROUTE_API_KEY",
  "reason_map": {
    "10": "credential_absent",
    "11": "credential_rejected"
  }
}
```

**`proofs/S0-03/probe_omniroute.py`:**

```python
#!/usr/bin/env python3
"""Probe whether OmniRoute accepts the explicitly supplied bearer credential."""
import os
import sys
import urllib.error
import urllib.request


def main():
    key = os.environ.get("OMNIROUTE_API_KEY")
    if not key:
        return 10
    request = urllib.request.Request(
        sys.argv[1],
        headers={"Authorization": f"Bearer {key}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return 0 if 200 <= response.status < 300 else 11
    except urllib.error.HTTPError:
        return 11
    except urllib.error.URLError:
        return 11


if __name__ == "__main__":
    raise SystemExit(main())
```

### 5.3 Registry entry (`proofs/registry.yaml:14`, verbatim)

```json
  {"proof_id": "S0-03", "title": "Hermes to OmniRoute", "classification": "blocked_credential", "wave": 2, "spike_dependencies": ["pc-bridge"], "required_negative_controls": 1, "assertion_count": 3, "blocked": {"owner": "TBD-owner-credential", "unblock_condition": "secret OMNIROUTE_UPSTREAM_KEY present and accepted", "marker_path": "proofs/S0-03/blocked.json"}},
```

Ledger state today (`proofs/ledger.json`):
```json
    {
      "classification": "blocked_credential",
      "normalized_digest": "b095ef6b9fafcc9634b85cfdba56cabce0a0e43608e2a7b3eacb861d7451f3d8",
      "proof_id": "S0-03",
      "state": "BLOCKED"
    },
```

### 5.4 Schemas an S0-03 artifact must satisfy

**`proofs/schemas/blocked.schema.json:1-25` (verbatim):**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "proofs/schemas/blocked.schema.json",
  "title": "Stage 0 blocked marker",
  "type": "object",
  "additionalProperties": false,
  "required": ["proof_id", "classification", "env_fingerprint", "marker"],
  "properties": {
    "proof_id": {"type": "string", "pattern": "^S0-(0[1-9]|1[0-2])$"},
    "classification": {"enum": ["blocked_credential", "blocked_host"]},
    "env_fingerprint": {"type": "string", "pattern": "^(pc-bridge|sandbox):.+$"},
    "marker": {
      "type": "object",
      "additionalProperties": false,
      "required": ["probe_cmd", "probe_run", "blocker_status", "unblock_condition", "owner"],
      "properties": {
        "probe_cmd": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        "probe_run": {"$ref": "#/$defs/run"},
        "blocker_status": {"enum": ["absent", "rejecting", "expired"]},
        "reason": {"enum": ["credential_absent", "credential_rejected", "capability_absent", "capability_present_but_failing"]},
        "unblock_condition": {"type": "string", "minLength": 1},
        "owner": {"type": "string", "minLength": 1}
      }
    }
  },
```

**`proofs/schemas/probe.schema.json:6-19` (verbatim):**

```json
  "additionalProperties": false,
  "required": ["proof_id", "probe_cmd", "timeout_s", "reason_map"],
  "properties": {
    "proof_id": {"type": "string", "pattern": "^S0-(0[1-9]|1[0-2])$"},
    "probe_cmd": {"type": "array", "minItems": 1, "items": {"type": "string"}},
    "timeout_s": {"type": "integer", "minimum": 1, "maximum": 600},
    "env": {"type": "object", "additionalProperties": {"type": "string"}},
    "key_env": {"type": "string", "pattern": "^[A-Z][A-Z0-9_]*$"},
    "reason_map": {
      "type": "object",
      "minProperties": 1,
      "propertyNames": {"pattern": "^[1-9][0-9]*$"},
      "additionalProperties": {"enum": ["credential_absent", "credential_rejected", "capability_absent", "capability_present_but_failing"]}
    }
  }
```

**Result schema** (for the day S0-03 mints a `result.json`): `classification` enum is
`["execution_proof", "conformance_checked_decision"]` only
(`proofs/schemas/result.schema.json:10`) — a `blocked_credential` value is not accepted by the
result schema, and `scripts/validate-ledger:224-227` marks a proof `INVALID` if both
`result.json` and `blocked.json` exist.

### 5.5 Exemplars

Minted EXECUTION exemplars S0-07 and S0-11, and the minted DECISION exemplar S0-09 — full
verbatim `spec.json` files, `graft skeleton` outputs and S0-07's `result.json` attestation block
are in `material-S0-02.md` §5.4.

### 5.6 How the runner produces a blocked marker (`scripts/proof-runner:226-271`, verbatim)

```python
def run_probe(root, proof_id, venue):
    proof_dir = root / "proofs" / proof_id
    blocked_path = proof_dir / "blocked.json"
    _remove(blocked_path)
    probe = _load_json(proof_dir / "probe.json")
    _validate(probe, root / "proofs" / "schemas" / "probe.schema.json")
    if probe["proof_id"] != proof_id:
        raise ValueError(f"proof-id-mismatch: expected {proof_id} got {probe['proof_id']}")
    registry_proof = _registry_proof(root, proof_id)
    if registry_proof is None or "blocked" not in registry_proof:
        raise ValueError(f"not-blocked-proof: {proof_id}")

    run, _stdout, _stderr, timed_out = _run_process(
        probe["probe_cmd"],
        root,
        probe["timeout_s"],
        _clean_env(probe.get("env"), probe.get("key_env")),
        "negative",
    )
    reason = probe["reason_map"].get(str(run["exit_code"]))
    if timed_out or (run["exit_code"] != 0 and reason is None):
        raise ValueError(f"probe-invalid: {proof_id} exit {run['exit_code']}")
    if run["exit_code"] == 0:
        blocker_status = "expired"
    elif reason.endswith("_absent"):
        blocker_status = "absent"
    else:
        blocker_status = "rejecting"

    marker = {
        "probe_cmd": probe["probe_cmd"],
        "probe_run": run,
        "blocker_status": blocker_status,
        "unblock_condition": registry_proof["blocked"]["unblock_condition"],
        "owner": registry_proof["blocked"]["owner"],
    }
    if reason is not None:
        marker["reason"] = reason
    blocked = {
        "proof_id": proof_id,
        "classification": registry_proof["classification"],
        "env_fingerprint": f"{venue}:{platform.node()}",
        "marker": marker,
    }
    _validate(blocked, root / "proofs" / "schemas" / "blocked.schema.json")
    _write_json(blocked_path, blocked)
```

CLI: `python3 scripts/proof-runner probe --proof S0-03 --venue <sandbox|pc-bridge> --root .`
(`scripts/proof-runner:274-293`). The mint path for a `result.json` is quoted in
`material-S0-02.md` §5.5.

### 5.7 What the validator checks for S0-03 specifically (`scripts/validate-ledger:328-339`, verbatim)

```python
            blocker_status = artifact.get("marker", {}).get("blocker_status")
            # COORDINATOR DECISION (2026-09-03, increment #2a): an expired deferral is an honest
            # STATE for `integrity` (the marker is well-formed and truthful: the blocker is gone)
            # and a RED for `stage1-gate` (the proof must now run). Reporting it as an integrity
            # finding made the committed tree's integrity red forever, contradicting the split-check
            # design (integrity green when honest, even empty; the gate carries the RED).
            expired = blocker_status == "expired"
            # S0-03's credential_rejected state is proof-RED, never a valid deferral.
            if proof_id == "S0-03" and blocker_status == "rejecting":
                findings.add("registry-schema: S0-03 credential rejection is not a valid blocked marker")
                valid = False
            states[proof_id] = ("EXPIRED" if expired else "BLOCKED") if valid else "INVALID"
```

Also `scripts/validate-ledger:468-475` (`stage1_gate`, verbatim):
```python
        expected = "BLOCKED" if proof["classification"].startswith("blocked_") else "PRESENT"
        state = states.get(proof["proof_id"])
        if state == "EXPIRED":
            missing.append(
                f"missing: {proof['proof_id']} ({proof['classification']}; deferral expired — the proof must run)"
            )
        elif state != expected:
            missing.append(f"missing: {proof['proof_id']} ({proof['classification']})")
```

Full validator map: `material-S0-02.md` §5.6.

---

## 6. VENUE FACTS

### 6.1 Which host each leg needs

`PC-BRIDGE.md:61` (verbatim):
```
| Local **vLLM** OpenAI-compatible endpoint `http://localhost:8010/v1`, served-model-name `sim9b`, guard `~/vllm_serve.sh` (setsid+flock), tool calling ON (`qwen3_xml` parser), thinking off via `chat_template_kwargs` | OmniRoute's upstream provider for S0-03 = this endpoint. The S0-03 pass asserts upstream identity = `sim9b` in the response `model` field. **No third-party API key needed.** |
```

`PC-BRIDGE.md:69` (verbatim excerpt): "- **PC via bridge:** … podman stacks for S0-01/S0-02 (Buzz
relay + buzz-acp + hermes-acp), **S0-03/S0-04 (OmniRoute + vLLM upstream)**, S0-06 (ai-memory) …"

`PC-BRIDGE.md:70` (verbatim): "- Every bridge-side proof still writes the same `result.json`
artifact family; the runner records `env_fingerprint = pc-bridge:<hostname>` so ledger entries
name their venue."

`PC-BRIDGE.md:153-163` (verbatim — the authoritative OmniRoute unit):
```
## OmniRoute on the PC — the managed unit, and the process-kill rule (2026-09-05)

- **The authoritative OmniRoute is `omniroute-migrated.service`** (systemd --user; exec
  `~/.omniroute-migration-npm/node_modules/.bin/omniroute serve --port 20128`; data dir
  `~/.omniroute-migrated`, pinned by the unit override `~/.config/systemd/user/omniroute-migrated.service.d/10-data-dir.conf`).
  Env files load in this order: `~/.omniroute-migrated/.env` → `~/omniroute-migration-20260829/candidate-home/.omniroute/.env`
  (the unit's `HOME`) → the npm package `.env`; the first setter of a variable wins. `~/.omniroute/.env` is
  read by nothing managed — it belonged to the 2026-09-05 orphan (`docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md`,
  INCIDENT-LOG 2026-09-05, AF-AP-33). Health 200 says nothing about WHICH instance answers: run
  `bash scripts/pc.sh "$(cat scripts/omniroute_invariants.sh)"` (read-only; set `OMNIROUTE_API_KEY_FILE`
  for the catalog check) before trusting the port.
```

`PC-BRIDGE.md:170-172` (verbatim — owner-only actions):
```
- **Owner-only actions surfaced 2026-09-05:** `REQUIRE_API_KEY=true` (the inference plane is
  unauthenticated on `0.0.0.0`, task #34); the `STORAGE_ENCRYPTION_KEY` rotation (task #33); client-key
  creation for S0-01 (needs a dashboard session — the coordinator does not use the owner's password).
```

Bridge protocol (`PC-BRIDGE.md:21-27`, verbatim excerpt): "Endpoint: `POST <URL>/exec` · auth
header **`X-Agent-Token: <token>`** … body `{"cmd": "<shell command>"}` · response `{"rc": <int>,
"stdout": "<str>", "stderr": "<str>"}`"; "Tunnel is HTTP/HTTPS only (sandbox egress is 80/443 via
the gateway) — Tailscale/SSH do NOT work from the sandbox."

### 6.2 What the Wave-0 spike proved for S0-03

`spikes/pc-bridge/result.json` — header (`:2-6`), the two facts, and the S0-03 effect (verbatim):

```json
 "spike_id": "pc-bridge",
 "schema": "proofs/schemas/spike.schema.json",
 "outcome": "positive",
 "ran_at": "2026-09-03T05:05:20+00:00",
 "env_fingerprint": "pc-bridge:fedora:6.17.11-200.fc42.x86_64",
```

```json
  "omniroute": "port 20128 listening on 0.0.0.0 -> HTTP 307 to /dashboard (OmniRoute already running)",
  "models": "vLLM at localhost:8010/v1 serving id `sim9b` (max_model_len 16384, root /home/rocco/models/huihui-qwen3.5-9b-abliterated-awq); Ollama on 11434 (bge-m3 embeddings) and mirofish-ollama on 11435; guards ~/vllm_serve.sh, ~/llama_server_restore.sh present",
```

```json
  {
   "affected_proof": "S0-03",
   "from_class": "blocked_credential",
   "to_class": "execution_proof",
   "rule_id": "map-pcbridge-s003",
   "reason": "OmniRoute running on the PC and a local model (vLLM sim9b) available as its upstream; identity assertable as `sim9b`"
  },
```

`spikes/pc-bridge/result.json:52-56` — `not_verified` (verbatim):
```json
 "not_verified": [
  "podman compose subcommand availability (buzz-prod containers exist, so SOME compose path worked)",
  "who launched OmniRoute on 20128 and its persistence/config state",
  "vLLM tool-calling flags currently in effect"
 ]
```

**Recorded contradiction, not resolved:** the spike's declared effect is
`blocked_credential → execution_proof`, and `proofs/registry.yaml:34` declares that transition;
the committed `proofs/S0-03/blocked.json` still records `blocker_status: "absent"` /
`reason: "credential_absent"` and the ledger still reads `BLOCKED`
(`proofs/ledger.json`), while `proofs/registry.yaml:14` still classifies S0-03
`blocked_credential`. `spikes/pc-bridge/result.json` is present, so
`scripts/validate-ledger:373-393` reads its `classification_effect` and checks only that the
transition is *declared* — it does not rewrite the registry class.

### 6.3 The transport deviation (`docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md:17`, verbatim)

```
> | Hermes transport | DEVIATION from ADR 0002 / `docs/03_INTEGRATION_CONTRACTS.md` §2 (`api_mode: codex_responses`, `x-omniroute-compression: off`): both repaired profiles use `chat_completions`. Owner decision (task #35): amend the ADR or revert the transport. The pinned S0-01 Hermes (0.21.0) supports both modes and per-provider `extra_headers` |
```

### 6.4 Credential state on the PC (`docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md:15-16, 33-40`, verbatim)

```
> | **SECURITY FINDING (new) — RESOLVED 2026-09-05 by the owner via Codex: `REQUIRE_API_KEY=true` in both loaded env layers, service restarted; reproduced no-key/bogus → 401, key → 200, monitor 7/7. Residual: LAN reachability behind auth, firewall narrowing deferred.** Original finding: the first-loaded env file set `REQUIRE_API_KEY=false` and the unit binds `OMNIROUTE_SERVER_HOST=0.0.0.0`: `POST {}` to `/v1/chat/completions` and `/v1/responses` with NO key, and with a bogus key, returns 400 (body validation) — there is no auth gate on the inference plane. firewalld's default zone opens `1025-65535/tcp`; the host has a LAN address (`192.168.40.12/24`) besides Tailscale. …
> | **Hermes client key (new finding) — RESOLVED 2026-09-05: the `hermes` key was rotated and written into every Fedora/laptop Hermes profile.** Original finding: the `OMNIROUTE_API_KEY` in `~/.hermes/profiles/agentfactory/.env` and the inline `api_key` in both `config.yaml` files are one value whose 12-char prefix matches NO row of the authoritative `api_keys` table (one row: `hermes`, prefix `sk-3c3c93f39`, active, scopes `["self:usage"]`); `/v1/models` answers `401` to it, and a bogus key behaves identically on `/v1/chat/completions` (400 = body validation). The owner's Hermes works ONLY because `REQUIRE_API_KEY=false`. …
```

```
> **Client key: use the one Hermes already uses (owner ruling 2026-09-05).** The earlier "create a
> new scoped S0-01 key" directive was issued while every key returned `401 AUTH_002`; the cause was the
> orphan instance serving a database without the owner's key, not the key. With the managed instance back
> the owner's existing key works (`hermes` → `ping`/`pong`), OmniRoute's model is one client key for many
> models, and the S0-01 proof reads that same key from the owner's Hermes config at launch — never copied
> into the repo, printed, or passed in argv. The sandbox classifier had blocked the coordinator's
> management-API login twice; that route is dropped, not worked around. `scripts/omniroute_invariants.sh`
> takes the same key via `OMNIROUTE_API_KEY_FILE`.
```

### 6.5 The read-only OmniRoute monitor (`scripts/omniroute_invariants.sh:1-23`, verbatim header)

```bash
#!/usr/bin/env bash
# omniroute_invariants.sh — READ-ONLY monitor: is the OmniRoute that owns the inference port the
# managed, authoritative instance? (docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md §Recovery runbook,
# handoff remaining-actions 4+5.) It NEVER remediates — no kill, no restart, no config write. Each
# invariant prints one `OK`/`FAIL <check>: <reason>` line; exit 0 = all OK, 1 = at least one FAIL,
# 2 = usage/tool error. Runs on the PC (owner shell or `scripts/pc.sh "$(cat scripts/omniroute_invariants.sh)"`).
#
# Why these checks (2026-09-05 incident): an unmanaged OmniRoute from an old shell squatted :20128
# serving the small default ~/.omniroute database while /api/health still said 200 and systemd
# reported the managed unit "active" inside its EADDRINUSE restart loop. Health alone is blind to
# that; ownership (cgroup) + the listener's OWN environ (kernel truth via /proc, not the unit's
# declared config) + the authenticated catalog are what discriminate.
#
# Env (all optional except the key file for the catalog check):
#   OMNIROUTE_PORT          default 20128
#   OMNIROUTE_SERVICE       default omniroute-migrated.service
#   OMNIROUTE_DATA_DIR      default /home/rocco/.omniroute-migrated
#   OMNIROUTE_BASE_URL      default http://127.0.0.1:$OMNIROUTE_PORT
#   OMNIROUTE_REQUIRED_IDS  space-separated model/combo ids that must appear in /v1/models
#                           default: the four agentfactory-* combos + ollama-cloud/kimi-k3
#   OMNIROUTE_API_KEY_FILE  0600 env file carrying `OMNIROUTE_API_KEY=…`; the key is read from the
#                           file and sent via a header FILE (`curl -H @<fd>`), never placed in argv
#   PROC_ROOT               default /proc (tests point it at a fixture tree)
```

Tests: `tests/test_omniroute_invariants.py` (present in `tests/`).

### 6.6 Observability

`docs/OBSERVABILITY-RUNBOOK.md:44-46` (verbatim): "`NOT built.` here: no exporter, no envelope
emitter, no dashboards wired — this runbook records the live PC endpoints and the lessons so the
first telemetry increment starts from facts."

### 6.7 The blocked marker's stated reason

`proofs/S0-03/blocked.json` `marker.reason` = `"credential_absent"`,
`marker.blocker_status` = `"absent"`, `marker.owner` = `"TBD-owner-credential"`,
`marker.unblock_condition` = `"secret OMNIROUTE_UPSTREAM_KEY present and accepted"`,
`env_fingerprint` = `"pc-bridge:fedora"`, probe exit code `10` (mapped by `probe.json` to
`credential_absent`), recorded `2026-09-03T18:33:34Z`.

---

## 7. CLASS PREFLIGHT

**The 18 defect classes** are quoted verbatim once in `material-S0-02.md` §7.2-§7.3 (source note:
SWEEP-prod.md has no heading literally named "The classes"; the enumerated list is
§ COUNTS PER CLASS at `tasks/briefs/s0-01-sweep-support/SWEEP-prod.md:116-139`).
**The mint-wide AF-AP rows** (AF-AP-36 pre-mint gate, AF-AP-56 attested inputs, AF-AP-27 frozen
contract, AF-AP-29 contract-weaker-than-test, and the AF-AP-30 meta-class) are quoted verbatim in
`material-S0-02.md` §7.5.

### 7.1 AF-AP rows whose mechanism names the S0-03 subject (credentials, OmniRoute, model egress)

`docs/INCIDENT-LOG.md:177` (AF-AP-33 — names OmniRoute and the port-squat that makes a 200
meaningless):
```
| AF-AP-33 | health-200 ≠ the right instance — a duplicate/unmanaged process squats the service port and answers health while serving a divergent dataset or config, so port-level liveness reads green during an outage of the real service | a liveness check that hits only `/health` or `/api/health`; a systemd unit reported "active" inside an `EADDRINUSE` restart loop; two processes with the same binary name and different `HOME`/data dirs | OmniRoute 2026-09-05: an orphan on `:20128` served the small `~/.omniroute` DB (catalog ~622 vs 2,626; combos gone; Ollama Cloud "no credentials") while health said 200 | SWEPT(2026-09-05) — `scripts/omniroute_invariants.sh`: exactly one listener, its cgroup = the managed unit, its OWN environ carries the authoritative `DATA_DIR` (+ `REQUIRE_API_KEY=true`), health, and the authenticated catalog carries every required id; edit-snapshot screen flags health-only probes |
```

`docs/INCIDENT-LOG.md:179` (AF-AP-35 — names OmniRoute's `STORAGE_ENCRYPTION_KEY`):
```
| AF-AP-35 | redaction keyed on the secret's VALUE — a filter or regex built from the value puts the value into the command line, the tool output or the transcript it was meant to protect, and a quoting slip echoes it verbatim | `sed "s/$SECRET/…/"`, `s/$(printf …)/`, `.replace(secret, …)`, `re.sub(secret, …)`; any command that expands a `*KEY*`/`*SECRET*`/`*TOKEN*`/`*PASSWORD*` variable into argv | 2026-09-04: a sed built from `$(printf …)` echoed OmniRoute's `STORAGE_ENCRYPTION_KEY` into the session log; the owner had to declare it compromised (29 encrypted provider credentials; no in-app rotation) | OPEN(2026-09-05) — rule baked (deep-work meta-rules): redact by KEY NAME or pattern class (`s/^\(KEY\|SECRET\|TOKEN\)=.*/\1=<redacted>/`), print only lengths/digests of secrets, dry-run every redaction on a dummy first; edit-snapshot screen row |
```

`docs/INCIDENT-LOG.md:183` (AF-AP-39 — names `OMNIROUTE_API_KEY` in argv): quoted verbatim in
`material-S0-02.md` §7.4.

`docs/INCIDENT-LOG.md:151` (AF-AP-7 — a config diagnostic that prints a credential):
```
| AF-AP-7 | a config diagnostic prints a whole block that carries a credential (the redaction lived in one probe, not in the method) | any bridge/CLI print of a config dict/block without a structural `api_key|token|secret|password` filter | Hermes profile probe 2026-09-03 | OPEN — no mechanical screen yet; rule = mask in code on every config print |
```

`docs/INCIDENT-LOG.md:148` (AF-AP-4 — the class that governs a `blocked_credential` label):
```
| AF-AP-4 | sandbox-probe-as-world: venue classification from the sandbox alone while the owner's live host holds the capability | any "blocked_host/blocked_credential" label with no PC-bridge probe record | findings v1 §2 + council KC-1/KC-2 | SWEPT(2026-09-03) — spike #0 |
```

`docs/INCIDENT-LOG.md:167` (AF-AP-23 — credential stripper keyed on a name blacklist): quoted
verbatim in `material-S0-02.md` §7.4.

`docs/INCIDENT-LOG.md:191` (AF-AP-47 — guard narrowed to a specimen; relevant to a
credential-disable kill switch's accepted domain): quoted verbatim in `material-S0-02.md` §7.4.

`docs/INCIDENT-LOG.md:171` (AF-AP-27 — a frozen seed contract, e.g. "the S0-04 stub is FORBIDDEN
here", changed as a side effect): quoted verbatim in `material-S0-02.md` §7.5.
