# Stage 0 task breakdown — from `seeds/seed-stage0-v1.yaml` (wave-plan-v2)

> Design record for the build. The project task list (TaskCreate, one task per increment) is
> the execution tracker; both must agree. Pipeline provenance: findings → council verdict →
> Ouroboros interview (ambiguity 0.10) → seed (8/8 self-validation) → this breakdown → build.

## Read order (cold successor)
1. `CLAUDE.md` (rules; incident log; Ouroboros quirks)
2. `seeds/seed-stage0-v1.yaml` — the contract: constraints, 12 per-proof blocks, frozen spike mapping
3. `docs/research/COUNCIL-VERDICT-STAGE0-v1.md` — why (kill criteria KC-1…KC-7)
4. `docs/research/FINDINGS-STAGE0-v1.md` — probed environment + Chairman addenda (§6a)
5. `docs/03_INTEGRATION_CONTRACTS.md`, `docs/05_SECURITY.md` §8 — the acceptance tests each proof encodes

## Pinned decisions (each with its rejected alternative)
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

## Standing prerequisites
- Pinned upstream sources: attach each repo via `add_repo` before cloning at the pinned commit
  (`upstream.lock.yaml`); public reads may be proxy-served — record every failure honestly.
- Every increment: `IS_SANDBOX`-free (no LLM in gates), deterministic test run TWICE (byte-identical),
  negative control authored BEFORE the positive leg, commit before any mutation audit, push at
  every boundary (incident log 2026-09-02).
- Commit message = reasoning record (rejected alternative, ordering rationale, primary source).

## Increments (one increment = code + deterministic test + commit)

| # | Increment | Deliverables | Acceptance (deterministic) | Negative control | Venue / gate |
|---|---|---|---|---|---|
| 1 | Registry + schemas + validator | `proofs/registry.yaml` (12 entries, classes, waves, spike deps, required negative-control counts, blocked owners/unblock_conditions), `proofs/schemas/{result,blocked,spike}.schema.json` (incl. `env_fingerprint`), `scripts/validate-ledger` with empty-set semantics | Over an EMPTY artifact set: `ledger-integrity` exits 0 reporting all 12 ABSENT, zero numerators, four denominators from the registry; `stage1-gate` exits non-zero with named reasons | Forged `runs` digest ⇒ integrity RED; hand-edited ledger claiming 1 proof over empty set ⇒ RED; registry entry without class ⇒ schema fail | in-sandbox |
| 2 | Runner + ledger generator + CI + markers | `scripts/proof-runner` (writes `result.json` only from real subprocess runs: cmd, timestamps, exit, sha256 digests, env_fingerprint), `scripts/ledger-gen` (deterministic, run twice), `.github/workflows/stage0-ledger.yml` (two split checks), `proofs/normalization.yaml`, probe-backed blocked markers for S0-03 and S0-08 | Generator byte-identical across two runs; CI shows integrity green + gate red on an empty set; markers validate with recorded probe runs | Validator mutation audit: forged digest, ledger drift, absent/malformed NOT-run marker — each killed by a named check; marker with `credential_rejected` maps to proof-RED | in-sandbox |
| 3 | Spike: rust-ai-memory | `spikes/rust-ai-memory/result.json` | Fact recorded either way: cargo build of pinned ai-memory on 1.94.1, then rustup 1.95 fetch attempt; `classification_effect` per mapping `map-rust-s006` | spike-errored (crash/timeout) is distinct from spike-negative and blocks only S0-06 | in-sandbox (Wave 0) |
| 4 | Spike: dockerd | `spikes/dockerd/result.json` | dockerd start + hello-world attempt recorded; venue note only (KC-6 if positive) | as above | in-sandbox (Wave 0) |
| 5 | Spike: runsc | `spikes/runsc/result.json` | static runsc install attempt + trivial run; confirms/expires S0-08 deferral via `map-runsc-s008` | as above | in-sandbox (Wave 0) |
| 6 | Spike: selective-egress (S0-05 mechanism) | `spikes/selective-egress/result.json` + the veth/proxy netns script | Positive leg: unit reaches a local OmniRoute-stand-in listener; negative leg: same unit fails a model endpoint with the exact denial reason; label `mechanism proven, containment unproven` | Bare `unshare --net` offered as evidence ⇒ rejected (blocks BOTH legs — Chairman probe); gate-off mutation ⇒ RED | in-sandbox (Wave 0; KC-1 if negative) |
| 7 | S0-01 ACP conformance | `proofs/s0-01/{fixtures,runner}`; pinned buzz-acp + hermes-acp installed at `upstream.lock.yaml` commits | Seed S0-01 assertions (initialize, prompt/stream/terminal, cancel, shutdown, session mapping, timeouts) on normalized transcripts, run twice identical | `neg-malformed-initialize.json` ⇒ `protocol-violation: missing required initialize field` | in-sandbox (Wave 1; needs add_repo for hermes-agent, buzz, agent-client-protocol) |
| 8 | S0-02 Buzz authorization | `proofs/s0-02/fixtures/{pos-allowed, neg-unauthorized, neg-bad-signature, neg-replayed, neg-stale}.json` | Allowed event ⇒ exactly one ACP turn; revocation independent of NIP-OA `created_at`; duplicate delivery idempotent | Four DISTINCT reasons (`sender-not-in-allowlist`, `signature-invalid`, `event-replayed`, `event-stale`); one blanket reject fails the proof | in-sandbox (Wave 1) |
| 9 | S0-07 Fubuki corrections | `proofs/s0-07/` + lint fix/wrapper + ordered regression fixture | `persona_lint` status correct regardless of violation ordering; `BoundDecision.record_id` join; canonical hash stable twice, mutated packet changes it | `neg-violating-persona/` ⇒ named rule id, documented exit status | in-sandbox (Wave 1; needs add_repo fubuki-os) |
| 10 | S0-09 Foundry host decision (shell) | `docs/adr/000N-foundry-host.md` + `proofs/s0-09/conformance-check` | ADR sections present; JIT five-file list matches pinned generator enumeration | Remove a required section ⇒ checker RED (`adr-incomplete`) | in-sandbox (Wave 1) |
| 11 | S0-10 GBrain seam decision (shell) | `docs/adr/000N-gbrain-seam.md` + `proofs/s0-10/conformance-check` | ADR sections + explicit no-admin-credential statement | Strip the statement ⇒ RED (`adr-incomplete: missing credential-isolation statement`) | in-sandbox (Wave 1) |
| 12 | S0-12 license/release policy (shell) | `LICENSE`, `THIRD-PARTY-NOTICES.md`, `SBOM.yaml`, update procedure, `proofs/s0-12/pin-diff-check` | SBOM pins diff EQUAL to `upstream.lock.yaml` | Mutate one SBOM pin ⇒ RED (`sbom-pin-drift`) | in-sandbox (Wave 1) |
| 13 | S0-06 four-scope adapter design | `proofs/s0-06/` against a real pinned ai-memory instance | Auth tuple outside model control; deterministic precedence merge (twice identical); write only active scope; honeytoken leak fixture never crosses scopes | `neg-unauthorized-tuple.json` ⇒ `denied: scope-tuple-unauthorized` | spike-gated on #3 (`map-rust-s006`); needs add_repo ai-memory |
| 14 | S0-03 Hermes→OmniRoute live round trip | `proofs/s0-03/` fixtures + runner ready; marker live from #2 | Streams text + real tool-call round trip via real OmniRoute; pass asserts upstream model identity; no upstream key in Hermes; OmniRoute failure ⇒ no fallback | Credential-disable kill switch ⇒ RED (`blocked: credential_absent`); S0-04 stub FORBIDDEN here | RED-pending real credential (owner TBD-owner-credential); needs add_repo OmniRoute |
| 15 | S0-04 compression contract | `proofs/s0-04/` + the ONE sanctioned deterministic upstream stub behind real OmniRoute | Request carries `x-omniroute-compression: off`; response `X-OmniRoute-Compression` asserted; stub-received request byte-equals sent fixture | Mutate OmniRoute's real header path ⇒ RED (`compression-header-missing`) | in-sandbox (Wave 2, after #14's OmniRoute install) |
| 16 | S0-05 full egress proof | `proofs/s0-05/` canary suite over live units | Every non-OmniRoute unit's canary FAILS after its positive control proves reachability of its allowed target | Egress gate off ⇒ suite RED (`egress-permitted: gate-disabled`) | Wave 2; depends on #6 mechanism + live units from #7/#14 |
| 17 | S0-08 gVisor spec + fixtures | `proofs/s0-08/` containment test spec + canaries, lint-checked; marker live from #2 | Spec + fixtures parse and lint; marker's probe re-runs every CI run | Stage-1 grep-gate FAILS when marker absent/malformed; runsc appearing ⇒ `deferral_expired` | deferred run (owner TBD-owner-gvisor-host); spec increment in-sandbox |
| 18 | S0-11 evaluation hardening | `proofs/s0-11/` runner design doc + rubric-isolation fixtures | Rubric runs unprivileged, separate cwd, no credential env vars, netns applied; grep sweep zero chmod-777/host-network hits | Rubric fixture reading a credential env var ⇒ `rubric-isolation-violation` | in-sandbox (Wave 3; unshare-based isolation) |

## Ordering rationale
Waves by falsification power then dependency (council): #1–2 machinery (self-verifying from an
empty set); #3–6 Wave-0 spikes in parallel (facts that reorder the plan); #7–12 Wave 1 in
parallel (disjoint components, real pinned binaries); #13 when its spike resolves; #14–16 the
spine (credential-gated S0-03 first so its RED-pending state is visible early); #17 spec now, run
later; #18 last (soft-depends on Wave 2's shape). Ada's verification-batching alternative stays an
open measurement: time #9's adversarial clearance vs wall-clock saved (KC-7).

## NOT-built ledger (honest, at breakdown time)
Nothing below exists yet: registry, schemas, validator, runner, generator, CI workflow, any spike,
any proof, any fixture, any ADR from S0-09/10, SBOM. `wiki-init` not yet run. Honey meter absent.
`ouroboros` MCP server does not connect natively — stdio fallback only.

## Owner answers (2026-09-03)
- **#14 / KC-2:** credential = the PC's local vLLM endpoint behind OmniRoute. S0-03 is no longer
  blocked-on-external-input once the bridge is up; its class flips to execution via the
  `pc-bridge` spike (declared transition — add to `spike_to_class_mapping` in increment #1).
- **#17 / KC-1:** gVisor host = the PC (bare metal, KVM). S0-08 runs live via the bridge.
- **Ordering:** parallel-by-component stands.

## Open owner questions (PATH-2, async) — keyed to increments (ORIGINAL, now answered above)
- **#14 / KC-2:** who supplies the real upstream model credential for S0-03, and by when? If none exists when Wave 2 opens, S0-03 stays RED-pending (never runs against the stub).
- **#17 / KC-1:** is a gVisor-capable host (runsc + KVM) going to be procured, by whom, by when? Until then S0-08 is spec+fixtures with a re-probed NOT-run marker.
- **Ordering preference:** the breakdown runs Wave-1 proofs in parallel by disjoint component; say so if strict sequential is preferred.
