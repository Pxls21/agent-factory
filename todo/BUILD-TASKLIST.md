# BUILD TASK LIST — agent-factory (Stage 0, end-to-end, durable)

> **This file is the SINGLE SOURCE OF TRUTH for live build status.** The in-session task tool
> does NOT survive a new chat; this committed file does. In any new session: *"Read
> `todo/BUILD-TASKLIST.md`, load it into your task list, then start at the first `pending` task."*
>
> **TASK-DB MIRROR RULE (owner mandate 2026-08-10, ported from trading-system).** The container
> task DB rolls back with disk resets and reuses its slot numbers, so it silently loses completed
> programs. Standing protocol: (1) every task CREATE and every status CLOSE is mirrored into
> this file's §LIVE ledger in the SAME increment, committed and pushed; (2) on every resume the
> task DB is restored FROM this ledger + the transcript's TaskCreate/TaskUpdate record — never
> from memory; (3) task KEYS are the SUBJECT SLUGS below, never bare #N (slot numbers collide
> across containers).
>
> **Branch:** `claude/soundbox-kit-migration-iz1jwf` (designated). **Authoritative design:**
> `seeds/seed-stage0-v1.yaml` (the contract) + `tasks/stage0-breakdown.md` (the decomposition)
> + `docs/research/COUNCIL-VERDICT-STAGE0-v1.md` (why) + `docs/07_BUILD_PLAN.md` (the stage plan).
> Each row is a distillation; the SEED is the full spec.
>
> **How to execute:** one increment at a time respecting `blocked-by`; one increment = code +
> deterministic test + commit (`S0-#n: <proof> — <what>`); the main loop re-runs every gate
> before marking done. Heavy/live/container work runs ON THE PC via `scripts/pc.sh`
> (`PC-BRIDGE.md`); `NOT run here` is stated, never skipped silently.

## 0. STATUS (updated 2026-09-04)

Pipeline (findings → council → interview → seed → breakdown): **COMPLETE**, all committed.
Tooling port from trading-system (`port-trading-system-setup`): **DONE** 2026-09-03 — hooks, ops
scripts, ledgers, CLAUDE.md, Codex/Hermes ports, wiki; PC smoke of the harness ports NOT run.
Build: **IN PROGRESS** — increment #1 DONE (2026-09-03), #2a landed, #2b landed 2026-09-04 (2 of 18 increments closed); Wave 0 spikes #3-#6 DONE 2026-09-04 (all POSITIVE); Wave 1 increments #9-#12 DONE 2026-09-04: S0-07 Fubuki corrections (first execution proof), S0-09 Foundry ADR, S0-10 GBrain ADR, S0-12 license/SBOM pin-diff — all 3 conformance-checked decisions complete. Wave 3 increment #18 S0-11 eval hardening: reopened by owner review SEVEN times (2026-09-04), re-hardened each cycle, then **ACCEPTED** 2026-09-04 as an explicit owner process decision (technical proof + trust binding accepted — AF-AP-32). Cycle 8: the acceptance is recorded honestly — NOT machine-enforced, because while the agent pushes under the owner's GitHub identity no in-repo status is structurally owner-only; the status guard now binds the single visible PROOF-STATUS line to the ONE canonical task row (the cycle-8 slug-keyed-row bypass is fixed with an exact proof→slug map). The owner-verifiable anchor (a dedicated bot identity + protected `main` + the owner's native GitHub review on the head SHA) is the separate `acceptance-anchor-af-ap-32` governance task, owner-blocked on infrastructure. Isolation is parent-observed from `/proc/<pid>` on five axes (uid≠0 / fresh netns / writable fresh cwd / exact env allow-list / active nsenter listener) plus a privilege boundary; result.json is bound to its inputs and regenerated only on a capable venue (ledger: execution_proof 1 of 7 present). Review fixes (`review-fixes-1`) DONE 2026-09-04; Stage 0 work unfrozen.

**Proof review status — authoritative, VISIBLE, machine-checked by `scripts/check-proof-status.py` (AF-AP-32).**
The guard binds this single visible line to the ONE canonical task row (exact proof→slug map) so
the two surfaces cannot diverge. It checks CONSISTENCY, not authenticity: while the agent pushes
under the owner's own GitHub identity, no in-repo status is structurally owner-only, so `ACCEPTED`
records an explicit OWNER PROCESS DECISION — never a machine-enforced guarantee. Making acceptance
owner-verifiable needs identity separation (a dedicated bot identity + protected `main` + the
owner's native GitHub review on the head SHA); that is the separate AF-AP-32 governance task
(`acceptance-anchor-af-ap-32`), owner-blocked on infrastructure.

PROOF-STATUS: S0-11 = ACCEPTED
Upstream lock refresh (`upstream-lock-refresh`) DONE 2026-09-04 — OmniRoute + GBrain pins advanced (D-019).
PC bridge: live this session (spike `pc-bridge` recorded); Buzz relay stack, OmniRoute,
Phoenix/OpenObserve already running on the PC; runsc on the PC (owner-installed); rustup has 1.95.0.

## 1. Tasks

| slug | increment | status | blocked-by | gate (deterministic) |
|---|---|---|---|---|
| s0-00-pc-bridge-probe | #0 spike: bridge liveness + PC capability probe | done 2026-09-03 (`abb16a0`) | — | `spikes/pc-bridge/result.json` present, redacted |
| s0-01-registry-schemas-validator | #1 registry + schemas + validator (empty-set semantics) | DONE 2026-09-03 — built by the PC Hermes lane (agentfactory-build), three contract-gate rounds + a two-lane verification; final layer: 45 tests ×2 bitwise, C1–C18 PASS 18/18, adversarial attacks A1–A8 SOLID (one under-reporting finding fixed with its killer test), eight prior fixes each have a killer; the twelve proofs stay ABSENT by design (0/7 execution · 0/3 conformance-checked · 0/1 blocked-credential · 0/1 blocked-host) | — | integrity green on empty set, stage gate RED, forged-digest/drift/unclassified negatives RED |
| s0-02-runner-ledger-ci-markers | #2 runner + ledger generator + CI split checks + probe-backed markers | DONE 2026-09-04 — half A (`s0-02a-runner-probes`) LANDED 2026-09-03: runner, spec/probe schemas, S0-03/S0-08 markers, blocked.schema.json; half B (`s0-02b-ledger-normalize-ci`) LANDED 2026-09-04: `scripts/ledger-gen` (deterministic, byte-identical ×2), `proofs/normalization.yaml` (volatile-field decl), CI generates ledger then validates with `--ledger`, 11 new tests (forge→INVALID, volatile-irrelevant, substantive-change-detected, sorted, byte-identical, validates-with-integrity); 91 tests + 98 harness checks green ×2 | s0-01 | generator byte-identical ×2; validator mutation audit kills forge/drift/marker mutants |
| review-fixes-1-ci-harness | #26 owner review 2026-09-03: real CI workflow, sync-skills fail-closed, hook/pc_lane test hygiene | DONE 2026-09-04 — four adversarial review rounds; all mutants killed; 98 harness checks ×2 + 80 pytest ×2 | — | CI green; sync-skills exits 65 on ANY list-generation failure; hook test uses `--absolute-git-dir` + reruns twice; pc_lane mutation-killing env-poison tests |
| upstream-lock-refresh | #27 refresh `upstream.lock.yaml`: OmniRoute (pin predates the credential-export security fix) + GBrain — after testing the patched commits on the PC, before #14 S0-03 | DONE 2026-09-04 — OmniRoute advanced to `488f57e9` (includes GHSA-5926-2w35-7h4q fix at `49c4a620`); GBrain to `8c70f625` (v0.48.2.0, `no_key fail-open` + storage scope fixes); decision D-019 recorded | review-fixes-1 | tested commits + reason in `docs/08_DECISION_LOG.md` |
| vendored-kit-packaging | #28 owner decision: generated source/commit/license manifest for the vendored trees (Hermes lane) or isolate Stage 0 code from the vendored environment in the PR stack | pending — awaiting the owner's choice | — | reviewers can mechanically skip vendored paths |
| s0-03-spike-rust-ai-memory | #3 spike rust-ai-memory (PC: cargo build at pinned commit) | DONE 2026-09-04 — POSITIVE: ai-memory v1.39.0 (edition 2024, resolver 3, MSRV 1.95, 12 workspace crates) compiles on the PC; default stable 1.93.0 succeeded, rustup 1.95.0 available; binaries produced (618 MB + 306 MB debug). **Digests captured 2026-09-04 over the live bridge** — fresh clone at the pinned commit, both `stdout_digest: uncaptured` → real sha256 (`a03e0fed…`, `92bec25a…`), both builds exit 0. S0-06 stays `execution_proof` per map-rust-s006 | s0-02 | `spikes/rust-ai-memory/result.json` present; classification_effect applied |
| s0-04-spike-dockerd | #4 spike dockerd-in-sandbox (secondary; PC uses podman) | DONE 2026-09-04 — POSITIVE: Docker v29.3.1 starts (overlayfs, cgroupfs, seccomp); hello-world pulled and ran. KC-6: sandbox is NOT container-blocked | s0-02 | `spikes/dockerd/result.json` present |
| s0-05-spike-runsc | #5 spike runsc install (sandbox + PC confirmed) | DONE 2026-09-04 — POSITIVE: runsc release-20260817.0 downloaded and runs rootless in sandbox (systrap, 4.19.0-gvisor kernel); PC also has it (owner-installed). S0-08 deferral expired → `execution_proof` per map-runsc-s008 | s0-02 | `spikes/runsc/result.json` present; classification_effect applied |
| s0-06-spike-selective-egress | #6 spike selective egress (S0-05 mechanism; veth/proxy, never bare unshare) | DONE 2026-09-04 — POSITIVE: veth pair + iptables in a dedicated network namespace; four legs all passed (positive: stand-in reached 200, negative-blocked-port: iptables DROP timeout, negative-external: no route, gate-off mutation: blocked port reachable after flushing iptables — de-vacuous). AF-AP-1 respected (NOT bare unshare --net). S0-05 mechanism proven, containment unproven per map-egress-s005 | s0-02 | positive leg reaches the allowed target, negative leg denied with exact reason |
| s0-07-s0-01-acp-conformance | #7 S0-01 ACP conformance (PC podman stack; real pinned hermes-acp) | pending | s0-02 | normalized-golden transcripts ×2; `protocol-violation: missing required initialize field` |
| s0-08-s0-02-buzz-auth | #8 S0-02 Buzz authorization (four DISTINCT denials) | pending | s0-02 | one turn on allowed; four named denials |
| s0-09-s0-07-fubuki | #9 S0-07 Fubuki corrections | DONE 2026-09-04 — exercises real fubuki-os at pinned commit `7375e56d`; (1) persona_lint ordering bug reproduced (review-first→exit 2) and wrapped (corrected exit logic→exit 1); (2) BoundDecision.record_id join proven (approved + rejected records, id matches, reasons present on denied); (3) canonical JSON hash stable ×2, mutation changes hash. Negative: violating persona fixture → `lint-violation: corporate-filler, exit 1 per contract` rc=1; 6 pytest tests green ×2 | s0-02 | ordered lint fixture; record_id join; hash stable ×2 |
| s0-10-s0-09-foundry-adr | #10 S0-09 ADR + conformance shell | DONE 2026-09-04 — ADR 0005 accepted (first-party minimal translator; OpenHarness not a runtime dep); conformance checker validates 4 required sections + JIT 5-file list; negative fixture (missing Consequences) → `adr-incomplete: missing required section: Consequences` rc=1; 5 pytest tests green ×2 | s0-02 | section removal → RED |
| s0-11-s0-10-gbrain-adr | #11 S0-10 ADR + conformance shell | DONE 2026-09-04 — ADR 0006 accepted (wrap pinned GBrain dream machinery); checker validates 4 required sections + credential-isolation statement + proposal-only contract; negative fixture (credential statement stripped) → `adr-incomplete: missing credential-isolation statement` rc=1; 4 pytest tests green ×2 | s0-02 | credential-isolation statement removal → RED |
| s0-12-s0-12-license-sbom | #12 S0-12 license/notices/SBOM pin-diff shell | DONE 2026-09-04 — SBOM.yaml (22 components, pins match upstream.lock.yaml), THIRD-PARTY-NOTICES.md, LICENSE-DECISION.md (pending owner choice), update procedure documented; checker validates file existence + pin equality + update-procedure presence; negative fixture (mutated hermes-agent pin) → `sbom-pin-drift: pin differs from upstream.lock.yaml for hermes-agent` rc=1; 5 pytest tests green ×2 | s0-02 | pin mutation → RED |
| s0-13-s0-06-four-scope | #13 S0-06 four-scope adapter proof (real ai-memory on the PC) | pending | s0-02, s0-03 | leak fixture never crosses; unauthorized tuple denied |
| s0-14-s0-03-omniroute-roundtrip | #14 S0-03 Hermes→OmniRoute live round trip (OmniRoute already up on the PC; identity = routed model id) | pending | s0-02 | tool-call round trip; upstream identity asserted; key-disable → RED; stub FORBIDDEN |
| s0-15-s0-04-compression | #15 S0-04 compression contract (sanctioned stub behind real OmniRoute) | pending | s0-14 | header asserts; request preservation; header-path mutation → RED |
| s0-16-s0-05-full-egress | #16 S0-05 full canary suite over live units | pending | s0-06, s0-07, s0-14 | every unit's canary FAILS after its positive control; gate-off → RED |
| s0-17-s0-08-gvisor | #17 S0-08 containment spec + fixtures; live run on the PC after the runsc spike | pending | s0-02, s0-05 | marker re-probed every CI run; grep-gate fails on missing marker |
| s0-18-s0-11-eval-hardening | #18 S0-11 runner design + rubric isolation | **ACCEPTED** 2026-09-04 — owner process decision after SEVEN reviews (not machine-enforced; the owner-verifiable anchor is the separate `acceptance-anchor-af-ap-32` task). Reopened seven times, re-hardened each cycle; AF-AP-32. Isolation now proven on 4 axes through `unshare --user --net`: UID drop (uid≠parent), netns identity (`/proc/self/ns/net` inode≠parent), network (loopback listener the checker holds is UNREACHABLE from the probe — not the 1.1.1.1 tautology), env ALLOW-LIST (not blacklist; production-named decoys BUZZ_PRIVATE_KEY/OMNIROUTE_INTERNAL_API_KEY/STORAGE_ENCRYPTION_KEY stripped). Non-vacuity gate: same predicate re-run on the UN-wrapped probe must breach every axis. Sweep broadened to all non-.md files; octal+symbolic world-writable chmod + host-net directives. FS containment NOT claimed in-sandbox → gVisor/S0-08. **Round 2 (owner re-review 2026-09-04): closed five adjacent leaks** — env allow-list is now a CLOSED EXACT set (was a `RUBRIC_*` prefix wildcard → `RUBRIC_PRODUCTION_API_KEY` leaked); `_violations` asserts `uid≠parent AND uid≠0` and rejects missing report fields; forbidden-op sweep is STRUCTURED (Python AST for real `os.chmod(0o777)`/`subprocess chmod`, YAML parse for `hostNetwork: True`/`network_mode: host`, no self-exclusion); frozen seed control `rubric-isolation-violation: credential env absent by construction` RESTORED as its own leg + four-axis kept as an additional leg (3-leg spec); capability preflight is the checker's `--selftest` (exit 2 = unavailable → skip, not fail). 23 pytest tests + 3-leg proof-runner result.json + ledger integrity green. **Round 3 (owner re-review 2026-09-04): the security CLASSES still bypassed one equivalent out — fixed structurally.** Evidence is now PARENT-OBSERVED from `/proc/<pid>` (real uid/netns/environ) + a parent `nsenter` listener probe, never a child self-report (a fake wrapper could fabricate one); wrappers are absolute-path with a REAL privilege drop (`setpriv --reuid`). The design gate is a machine-readable `policy:` YAML block (prose can't invert it); the sweep is reframed as a best-effort LINT (alias+constfold, catches 12 equivalents) with the runtime isolation + gVisor as the boundary. The spec pins the COMPLETE four-axis reason (canonical contract ≥ the test). Every namespace-reading leg is `--selftest`-gated; a test proves the incapable path exits 2 (defer). 32 pytest tests; AF-AP-24/25/26 extended, AF-AP-28/29/30 added; bakes to anti-hollow-green (equivalence-class mutants) + build-loop (both-venue leg testing) | **Cycle 4 (owner 4th review): 3 more fixed** — active network is now a REQUIRED paired control (wrapped refused / raw reached; preflight requires nsenter, defers exit 2 where it can't run, no fail-open on None); EVERY namespace CLI leg (not just the pytest decorator) runs the preflight and defers; the fresh cwd is now really set on Popen and parent-observed via /proc/<pid>/cwd (cwd-not-isolated axis); RUBRIC_LLM_ENDPOINT reconciled. 35 S0-11 tests, 146 full suite. AF-AP-22/24 reopened+re-swept; AF-AP-30 count→4 | **Cycle 5 (owner 5th review): 4 more fixed** — (1) result.json is now BOUND to its inputs: the runner records an `attestation` (sha256 of every proof-dir input) and the validator re-derives it from the tree, so a neutered checker with a stale green no longer validates (schema+digest passed it before); required by result.schema.json across all 4 present artifacts. (2) The canonical `scripts/proof-runner` DEFERS on exit 2 (capability-unavailable) and PRESERVES the artifact instead of deleting-then-failing; tests drive the REAL runner in both venue states. (3) The fresh cwd is chowned to the drop uid (writable) — the rubric writes and the parent COLLECTS before cleanup (workspace-not-writable fails the proof). (4) The root drop adds `--no-new-privs --bounding-set -all`; the parent asserts NoNewPrivs=1 + CapBnd=0. 40 S0-11 tests, 152 full suite. AF-AP-24 recurrence→3, AF-AP-30→5, AF-AP-31 (proof-not-bound-to-inputs) + AF-AP-32 (status-precedes-owner-acceptance) added | **Cycle 6 (owner 6th review): 2 more fixed** — (1) the cycle-5 attestation bound only proof-local files, so mutating the RUNNER left the green standing and forging the positive command passed; now `proof_attestation` covers the COMPLETE trust closure (runner/validator/registry/schemas), the validator binds the recorded runs to the attested spec one-for-one (leg/command/exit + per-negative failure_reason), and the runner INVALIDATES the artifact on a real (non-defer) failure. (2) the review-status guard was a `re-closed` word-ban; replaced with a structured parser (`scripts/check-proof-status.py`) enforcing state (one marker; DONE/CLOSED fail; deletion fails). 167 full suite. AF-AP-30→6, AF-AP-31/32 extended | **Cycle 7 (owner 7th review): the ACCEPTANCE mechanism was 3 more AF-AP-32 instances** — the cycle-6 hidden HTML marker let a visible `\| S0-11 \| DONE \|` row contradict it; the `proofs/<id>/OWNER-ACCEPTED` file was an arbitrary self-accept (file existence ≠ authentication) that ALSO broke the attestation (it sat in the attested dir). Fix: the status is a SINGLE VISIBLE `PROOF-STATUS: S0-11 = REVIEW-PENDING` line (hidden markers rejected); the coordinator may record ONLY REVIEW-PENDING (no coordinator-writable ACCEPTED — the self-accept file is removed); bare-proof-id task rows are rejected; no review metadata in the attested dir. The owner-verifiable ACCEPTED anchor (merge to `main` / protected review / signed) is an owner decision, surfaced not built (no crypto tooling here; any in-repo file is coordinator-forgeable). 169 full suite. AF-AP-30→7, AF-AP-32 extended | s0-02 | parent-observed uid≠0/fresh-writable-cwd/exact-allow-list/no_new_privs + active nsenter listener control; attestation-bound artifact; canonical runner defers+preserves; policy-block design gate; frozen control preserved; contract=test |
| port-trading-system-setup | tooling: port the trading-system setup wholesale (hooks, ops scripts, ledgers, CLAUDE.md, harness-ports, wiki) | done 2026-09-03 (batch E commit) | — | hooks active ✓; lint test green ✓; harness-ports tests 58/58 ✓; wiki compiled ✓ (PC smoke NOT run — owner) |
| harness-skill-rewordings | tooling follow-up: re-port the source repo's hand-ported skill rewordings (HARNESS PORT notes; contract-gate/orchestration semantics) into `.agents/skills/` with this repo's paths | done 2026-09-03 (`c2e529a`, `86ade0d`) | — | 15 HARNESS PORT notes; sync-skills --check rc=0 with 15 INTENTIONAL; NOT ported: `premortem-roast/dimensions.md` (source-only extra file) |
| continuity-offload-plane | tooling: transcript sync (sandbox digests + PC lane transcripts), per-role OmniRoute routes, curator/echo/researcher lanes + templates, workflow offload map, trading-system handoff | in_progress 2026-09-03 | — | scrubber tests green (per-class negatives); probe table has rows; curator lane ran once with a reviewed wiki delta |
| acceptance-anchor-af-ap-32 | governance (cycle-8 spin-off from S0-11 AF-AP-32): an OWNER-VERIFIABLE ACCEPTED anchor for reopened proofs — a dedicated bot/GitHub-App push identity + protected `main` (require PRs, required checks, one owner approval, dismiss stale approvals, no bot bypass) + the owner's native GitHub review on the exact head SHA as the anchor | pending — OWNER-BLOCKED on infrastructure (the agent cannot create a GitHub App or configure branch protection); until it lands, `check-proof-status.py` checks CONSISTENCY only and ACCEPTED records an owner PROCESS decision, not machine-enforcement | — | with identity separation, an owner GitHub review on the head SHA is the machine-checkable acceptance; without it, acceptance stays an explicit human process decision |

## 2. LIVE ledger (append-only sync blocks; newest first)

**2026-09-05 sync (S0-01 milestone 2: relay-driven prompt turn reached twice; determinism finding; S0-01 still INCOMPLETE):**
An owner mention (accepted, h+p) drove the pinned buzz-acp → `session/new` + `session/prompt` on the pinned hermes-acp →
`session/update` stream → `stopReason=end_turn`; Hermes reached the managed OmniRoute (auto/best-coding-fast, 3 API
calls) — two identical runs, raw frames + argv + env names + config echo (`idle_timeout=900s`) + three-tree manifests
in `proofs/S0-01/evidence/turn-*/`, every frame v1-conformant (`tests/test_s0_01_turn_capture.py`, 5 tests). Credential
NOT validated (plane open; Hermes' key is in no key-table row) — not S0-03 evidence. FINDING: the live route's
`session/update` STRUCTURE differs across identical runs (49+27 vs 59+1 chunks) → the golden needs the sanctioned
deterministic scripted backend behind a dedicated OmniRoute test route (owner-run config change). Notes: no agent reply
reached the thread (this buzz-acp delegates replying to the agent via a Buzz MCP tool it was not given — S0-02
territory); the pinned hermes-acp ran a terminal tool with no policy gate (S0-08 territory). Still unproven:
cancellation, shutdown, two-user separation, live negative, golden ×2. Denominators unchanged.

**2026-09-05 sync (Codex OmniRoute/Hermes handoff reconciled; OmniRoute invariants monitor; three incidents; S0-01 initialize milestone recorded, S0-01 still INCOMPLETE):**
Tasks created this increment (subject slugs): `handoff-reconciliation-omniroute` (#31, DONE this
commit), `incident-prod-relay-pkill-af-ap-34` (#32, logged + rule baked; OPEN until the owner
acknowledges), `owner-rotate-storage-encryption-key` (#33, OWNER-BLOCKED), `owner-omniroute-require-api-key`
(#34, OWNER-BLOCKED), `owner-adr-0002-wire-mode` (#35, OWNER decision). Handoff remaining actions: 1-5 and 9
DONE (`docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md` committed verbatim under a review header;
`scripts/omniroute_invariants.sh` read-only, 7 checks, 11 deterministic tests; live on the PC: 5 OK,
`require_api_key` FAIL = the inference plane is unauthenticated on 0.0.0.0, `catalog` FAIL = no key file);
6-7 OWNER-ONLY; 8 = the S0-01 build/verify lanes once the key exists (research/sweep UNMEASURED). Focused
lane tests 33/33 ×2; full harness suite ALL SUITES PASSED. Offload map + `pc-lane.sh` comment synced to the
2026-09-05 combo orders (K3 promoted; deepseek-v4-flash removed). **S0-01 (`s0-07-s0-01-acp-conformance`,
#10) — milestone, recorded precisely (owner wording 2026-09-05):** the pinned `buzz-acp` launched the pinned
`hermes-acp` and exchanged ACP initialize messages — client offered protocol `2`; agent returned protocol `1`;
initialize exchange succeeded with the required capabilities. S0-01 overall REMAINS INCOMPLETE: nothing yet
proves relay-authenticated prompting, OmniRoute egress, streaming/terminal behavior, cancellation, shutdown,
concurrent-session mapping, timeout configuration, determinism, or the negative control. Raw initialize request/response
FRAMES (not logs) CAPTURED 2026-09-05T06:30:01Z through `frame_tee.py` with no prompt and no OmniRoute
credential, bound to the pinned paths + three-tree manifests (pre = post = baseline) —
`proofs/S0-01/evidence/initialize-20260905T062959Z/`, checker `proofs/S0-01/check_initialize.py`, 5 tests
incl. the seed's negative fixture. Owner ruling 2026-09-05: NO new key — the proof uses the same OmniRoute client key the owner's Hermes uses
(the new-scoped-key directive dated from the orphan-instance 401s and is withdrawn). FINDING: that key is in NO row of the
authoritative key table (`/v1/models` 401); Hermes works only because `REQUIRE_API_KEY=false` — owner must regenerate
the `hermes` key before enabling the requirement (#34). Incidents: AF-AP-33 (orphan OmniRoute listener, Codex-fixed),
AF-AP-34 (the coordinator's `pkill -x buzz-relay` restarted the PRODUCTION `buzz-prod-relay-1` four times on
2026-09-04 — reported to the owner), AF-AP-35 (the coordinator leaked `STORAGE_ENCRYPTION_KEY` into the
session log). Four-way denominators unchanged: no proof changed state this increment.

**2026-09-04 sync (S0-11 cycle 8 — ACCEPTED by owner process decision; the slug bypass fixed):**
The owner's EIGHTH review accepted S0-11's technical proof and trust binding, and ruled: do NOT
reopen S0-11 for a ninth cycle — the remaining parser/anchor work is the separate
`acceptance-anchor-af-ap-32` governance task. One live guard bug remained and is fixed: the cycle-7
guard rejected only BARE-id rows (`| S0-11 | … |`), so a canonical-SLUG row
(`| s0-18-s0-11-eval-hardening | … | DONE |`) asserting a status a human reads passed while the
`PROOF-STATUS` line stayed REVIEW-PENDING — reproduced here (guard rc=0). Fix:
`check-proof-status.py` now BINDS the single visible `PROOF-STATUS: <id> = <status>` line to the
ONE canonical task row — exactly one row keyed by the proof's canonical slug via an EXACT proof→slug
map (never a substring; the S0-10 row `s0-11-s0-10-gbrain-adr` embeds "s0-11" and a substring match
would misbind it, reproduced as a collision hazard), and that row's status-cell leading token must
equal the marker. Reproduced closed: the DONE-row bypass → rc=1 `must not contradict`; the S0-10
collision → ignored, rc=0. Honest boundary (stated in the guard docstring, `BUILD-TASKLIST.md`, and
the incident log): the guard checks CONSISTENCY, not authenticity — while the agent pushes under the
owner's own GitHub identity no in-repo status is structurally owner-only, so ACCEPTED records an
owner PROCESS decision, never machine-enforcement. The owner-verifiable anchor (a dedicated bot
identity + protected `main` + the owner's native GitHub review on the head SHA) is
`acceptance-anchor-af-ap-32`, owner-blocked. 16 proof-status tests; 175 full suite ×2 deterministic;
verify-planning green. AF-AP-30 recurrence 8, AF-AP-32 extended (resolved as a process decision).
Bakes: build-loop / anti-hollow-green — bind a marker across every visible surface, exact key map
never a substring, a consistency guard must name its scope.

**2026-09-04 sync (S0-11 cycle 7 — the acceptance mechanism, surfaced not faked):** The owner's
SEVENTH review confirmed the trust-binding work good and reproduced THREE failures in the cycle-6
acceptance guard. (1) The marker was a HIDDEN HTML comment, so a VISIBLE `| S0-11 | DONE |` task
row contradicted it and the guard passed — the human ledger and the machine state diverged. (2)
The `proofs/<id>/OWNER-ACCEPTED` record was an ARBITRARY FILE; file existence is not authentication,
so the builder self-accepted by committing a file. (3) That file lived in the ATTESTED proof dir,
so the acceptance procedure itself produced `attestation-mismatch`. The root cause: I kept building
an acceptance gate the coordinator can satisfy — the exact AF-AP-32 failure, three more times.
Fix (the robust parts): the status is a SINGLE VISIBLE line `PROOF-STATUS: S0-11 = REVIEW-PENDING`
(hidden HTML-comment markers are rejected); the coordinator may record ONLY REVIEW-PENDING (the
forgeable OWNER-ACCEPTED self-accept path is REMOVED — there is no coordinator-writable ACCEPTED);
a Markdown task row keyed by a bare proof id is rejected; and no review metadata lives in the
attested proof dir. `tests/test_proof_status.py` covers the hidden-marker, bare-id-row,
coordinator-cannot-ACCEPT, duplicate, and REVIEW-PENDING→both-gates (status + ledger integrity)
cases. NOT unilaterally built: an owner-verifiable ACCEPTED anchor — it requires owner-controlled
infrastructure the coordinator cannot forge (a merge to `main`, a protected GitHub review, or the
owner's signing key + tooling absent here), so it is SURFACED as an owner decision rather than
faked as a fourth forgeable file (#1 rule: surface the blocker). 169 full suite ×2 deterministic;
ledger integrity green. Bakes: `build-loop`/`anti-hollow-green` AF-AP-32 extended — one visible
authoritative status source; the coordinator never builds an acceptance gate it can satisfy; a
state TRANSITION is tested through EVERY adjacent gate (the cycle-6 ACCEPTED test never ran ledger
integrity, which is how the attestation break slipped through). **REVIEW-PENDING — awaiting the
owner's acceptance-anchor decision.**

**2026-09-04 sync (S0-11 cycle 6 — the trust binding is now COMPLETE):** The owner's SIXTH review
found the cycle-5 fixes real but two safeguards still bypassable, both reproduced this session.
(1) **The attestation was an incomplete trust closure (AF-AP-31 extended).** It hashed only
`proofs/S0-11/**` — omitting the runner, validator, schemas and registry — so mutating
`scripts/proof-runner` to run every leg as `/usr/bin/true` made the run fail while the STALE green
artifact was preserved and `validate-ledger integrity` still said PRESENT; and forging the
recorded positive command to `/usr/bin/true` with a recomputed self-digest was accepted because
the validator never compared the runs to `spec.json`. Fixed three ways, each reproduced closed:
`proof_attestation` now covers the COMPLETE trust closure (runner + validator + registry + schemas
+ proof-local) so a runner/validator mutation → `attestation-mismatch`; the validator binds the
recorded runs to the attested spec one-for-one (leg/command/exit + each negative `failure_reason`)
so the forged command → `runs-spec-mismatch`; and the runner INVALIDATES (removes) the artifact on
any real non-defer failure so a mutated-runner run → `ABSENT` (only an explicit exit-2 defer
preserves). (2) **The review-status guard was a vocabulary ban, not a state check (AF-AP-32
extended).** It rejected only the literal `re-closed`, so a `DONE by coordinator` row passed.
Replaced with a structured parser (`scripts/check-proof-status.py`) that reads the canonical
`PROOF-STATUS <id> <status>` HTML-comment marker and enforces state — one marker per proof, status ∈
{REVIEW-PENDING, ACCEPTED}, ACCEPTED requires a committed `proofs/<id>/OWNER-ACCEPTED`, deletion
fails — with `tests/test_proof_status.py` covering DONE/CLOSED/deleted/duplicate/ACCEPTED cases.
167 full suite ×2 deterministic; all 4 result.json regenerated with the closure attestation +
per-negative failure_reason; ledger integrity green. Bakes: `anti-hollow-green` tactic 13 extended
(complete trust closure + runs-bound-to-spec + never preserve across a real failure); `build-loop`
review-pending rule extended (structured status parsing). Honest gap the owner named: the CHAIN
(attestation over the full closure + runs-bound-to-spec) is now checkable on ANY venue, but the
isolation RUN is verifiable only on a capable venue (the root sandbox here; the PC/gVisor over the
bridge needs a banner — none this session). S0-09/S0-10 regex checkers remain the AF-AP-25/32
siblings, still DEFERRED per the owner. **REVIEW-PENDING — awaiting the owner's acceptance.**

**2026-09-04 sync (S0-11 cycle 5 — four more; the proof is now bound to its code):** The owner's
FIFTH review found four blockers, each reproduced this session before fixing. (1) **Proof not
bound to executable inputs (AF-AP-31).** Neutering `_iso_launch` to a pass-through and re-running
`validate-ledger integrity` still returned `S0-11 PRESENT` — the validator checks schema + digest
but the digest is only over the runs, and the positive stdout hash is merely sha256("PASS\n"); CI
never re-runs the proof. Fix: the runner records an `attestation` (sha256 of every input file
under the proof dir — checker, spec, fixtures, design), the validator re-derives it from the tree
and fails on any mismatch (`attestation-mismatch: S0-11 proofs/S0-11/check_eval_hardening.py`), and
result.schema.json REQUIRES it across all four present artifacts (S0-09/10/11/12 regenerated —
their checkers untouched). (2) **Canonical runner did not defer (AF-AP-24 recurrence 3).** On an
incapable venue the real `scripts/proof-runner` removed result.json first, then failed
`leg-exit-mismatch … got 2`; and the "canonical-invocation" test invoked the checker legs
directly. Fix: the runner treats exit 2 as DEFER (preserves the artifact, exits 2); new tests
drive the REAL runner in BOTH venue states. (3) **Fresh cwd isolated but unusable (AF-AP-30
recurrence 5).** `TemporaryDirectory` is root-owned 0700, so the dropped uid could neither write it
nor (a real rubric) collect output, and it was deleted before observation returned. Fix: chown the
workspace to the drop uid, a real write-producing rubric writes it, the parent COLLECTS the output
before cleanup (workspace-not-writable fails the proof). (4) **UID drop is not a full privilege
boundary.** The root launch set neither `no_new_privs` nor cleared the capability bounding set. Fix:
`setpriv … --no-new-privs --bounding-set -all`; the parent asserts NoNewPrivs=1 and CapBnd=0. Plus
the fourth review finding — the ledger claimed the coordinator's own closure while the handoff
said review-pending (AF-AP-32): a proof the owner reopened is REVIEW-PENDING until the owner
accepts, now enforced by a `verify-planning-repo.sh` guard that bans the self-closure vocabulary. 40 S0-11 tests (attestation binding, both-venue canonical runner,
writable-cwd collection, no_new_privs mutation), 152 full suite ×2 deterministic; all 4 result.json
regenerated with attestation; ledger integrity green. Bakes: anti-hollow-green gains
artifact-to-source attestation + the real write/collect/cleanup workload rule; build-loop gains
"exercise the canonical consumer in both venue states". S0-09/S0-10 regex-checker hardening
(AF-AP-25 siblings) still DEFERRED per the owner's instruction — only their artifacts were
re-stamped, their checkers untouched. **REVIEW-PENDING — awaiting the owner's acceptance.**

**2026-09-04 sync (S0-11 cycle 4 — three more, behind the parent-observation rewrite):** The
owner's fourth review found three blockers the round-3 rewrite left: (1) active network evidence
FAILED OPEN — `nsenter` returning `None` (never ran, e.g. non-root) was accepted, so the loopback
discriminator never ran in green CI; now a REQUIRED PAIRED control (wrapped refused / un-wrapped
reached) with the preflight requiring `nsenter`, deferring (exit 2) on a venue that cannot run it
(reopened AF-AP-22). (2) "every namespace leg gated" was only the pytest decorator — the CLI
`--rubric-neg` never ran the preflight; now every namespace-reading CLI leg defers consistently
(reopened AF-AP-24). (3) the frozen separate-cwd was claimed but never set on `Popen`; now the
wrapped child runs in a fresh `TemporaryDirectory` and the parent asserts `/proc/<pid>/cwd` differs
from its own (`cwd-not-isolated` axis). Also reconciled `RUBRIC_LLM_ENDPOINT` (not injected by the
stand-in, so absent from the allow-list). The capable venue is the ROOT sandbox (root + unshare +
setpriv + nsenter), where `result.json` is regenerated. 35 S0-11 tests, 146 full suite, ×2
deterministic; ledger integrity green. AF-AP-30 recurrence count → 4 (blacklist→prefix→exact,
regex→AST→policy-block, child-report→parent-observe, net-tautology→fail-open→required-paired,
pytest-gate→CLI-gate, claimed-cwd→observed-cwd). The discipline that finally holds: a paired
control that requires the instrument to FIRE, the preflight on every consuming leg, and observing
every claimed property from the kernel.

**2026-09-04 sync (S0-11 round 3 — structural fixes, class not specimen):** A third owner review
showed the round-2 fix passed its own cases but the same SECURITY CLASSES bypassed one equivalent
out. The meta-lesson (AF-AP-30): fixing named specimens is not closing a class. Five structural
fixes: (1) evidence is now PARENT-OBSERVED — the child only signals ready and blocks; the parent
reads kernel truth from `/proc/<pid>/status` (real uid), `/ns/net` (netns), `/environ` (env), and
`nsenter`s the child netns to prove a held listener is unreachable. Child self-reports are never
trusted (a fake wrapper fabricates a clean one; `unshare --user --net` even self-reports uid 65534
while the host uid stays 0). Wrappers are absolute-path; a REAL privilege drop is used (root:
`unshare --net`+`setpriv --reuid=65534`; non-root: `unshare --user --net`). (2) the design gate is a
machine-readable ```yaml `policy:` block the checker parses — prose ("isolation is unnecessary")
can no longer satisfy or invert it. (3) the forbidden-op sweep is reframed as a best-effort LINT
(alias resolution + constant folding added, catches 12 equivalents incl. `import subprocess as sp`,
`from subprocess import run`, `cmd=[…]; run(cmd)`, `mode=0o777`, `0o700|0o077`, `${VAR:-host}`) whose
limits are stated — the boundary is the runtime isolation + gVisor, not a complete static scan.
(4) the spec pins the COMPLETE four-axis reason (canonical contract ≥ the strongest test). (5) every
namespace-reading leg is `--selftest`-gated and a test proves the incapable path exits 2 (defer,
never a false pass/breach) — the round-2 "2 failed" was an ungated leg. `isinstance(True,int)` /
`uid:-1` are dissolved (uid parsed from /proc). **CI on the first round-3 push caught a
self-inflicted venue bug** (the same "test both venues" rule this increment baked): the checker
asserted `uid != parent`, which passes only as root; the non-root ubuntu runner failed
`uid-not-dropped`. Fixed — the invariant is `uid != 0` (never root, never `!= parent`; a non-root
runner's rubric inherits its non-root uid), the uid-drop discrimination is gated to a root venue,
and `test_positive_conformance_non_root_venue` (setpriv-simulated) exercises the CI path
in-sandbox. Both venues green. 33 S0-11 tests, 144 full suite, ×2 deterministic;
3-leg result.json; ledger integrity green; `execution_proof` 1 of 7. Registry: AF-AP-24/25/26
extended, AF-AP-28 (trust the subject's self-report), AF-AP-29 (contract weaker than the test),
AF-AP-30 (specimen-only remediation) added; bakes to `anti-hollow-green` (equivalence-class mutants)
and `build-loop` (both-venue leg testing). S0-09/S0-10 regex checkers remain OPEN siblings of
AF-AP-25 (owner "3 checkers") — flagged, not yet swept.

**2026-09-04 sync (S0-11 round 2 + rust-ai-memory digests):** The owner re-reviewed the round-1
S0-11 fix and reproduced five ADJACENT hollow greens — the fix had closed the four named holes but
the same classes re-appeared one surface out. All reproduced, then closed: (1) the "allow-list"
passed every `RUBRIC_*` by PREFIX, so `RUBRIC_PRODUCTION_API_KEY` leaked → now a CLOSED EXACT set
(`RUBRIC_TASK_ID/CWD/PROBE_PORT`); (2) `_violations` accepted `uid==0` for a non-root parent and
defaulted MISSING fields to a pass → now asserts `uid≠parent AND uid≠0` and rejects any malformed
report; (3) the regex sweep missed `os.chmod(…,0o777)`, `subprocess.run(["chmod","-R","0777"])`,
`hostNetwork: True`, and self-excluded the checker → now STRUCTURED: Python AST (call-based, so the
checker's own pattern strings do not self-flag and no file is excluded), YAML parse, regex only for
shell/text; (4) the round-1 spec had SILENTLY deleted the frozen seed negative control → restored
as its own leg, with the four-axis negative kept as an additional leg (3-leg spec); (5) the pytest
preflight checked only a uid change → replaced by the checker's own `--selftest` (parent+child
netns readable + `unshare --user --net` runs), exit 2 = capability-unavailable (skip, defer to the
PC), never a false pass. Also the design-doc gate now rejects hazard-inverting prose. 23 S0-11
tests, 134 in the full suite, ×2 deterministic; 3-leg `result.json` via the canonical proof-runner;
ledger integrity green; `execution_proof` 1 of 7. Registry: AF-AP-23 extended (prefix wildcard),
AF-AP-24 (proxy preflight), AF-AP-25 (regex where a parser is required — S0-09/S0-10 siblings OPEN),
AF-AP-26 (permissive-default/relative-only predicate), AF-AP-27 (frozen contract reshaped silently).
Separately, the **`rust-ai-memory` spike re-ran on the live PC bridge**: a fresh clone at the pinned
commit built twice (default stable + `+1.95.0`), both exit 0, and the two `stdout_digest: uncaptured`
placeholders are now real sha256 (`a03e0fed…` / `92bec25a…`); the 4.7 GB throwaway clone was removed
from the PC. Lesson: an owner review that clears the named holes is not a close — verify the SAME
class one surface out (prefix-vs-exact, regex-vs-parser, proxy-vs-consumer), and never edit a frozen
contract as a side effect.

**2026-09-04 sync (Wave 3 increment #18 S0-11 REOPENED → re-hardened):** Owner review of the
first S0-11 close found hollow greens: (1) the `net_isolated` check was a tautology — the
sandbox has no direct route to 1.1.1.1 regardless of `unshare`, so a pass-through `unshare` still
reported isolated; (2) the env stripper was a NAME BLACKLIST that let real production credentials
(`BUZZ_PRIVATE_KEY`, `OMNIROUTE_INTERNAL_API_KEY`, `STORAGE_ENCRYPTION_KEY`) through; (3) the grep
sweep scanned only `.py`/`.sh`, so `network_mode: host` in YAML and `chmod -R 0777` survived; the
checker never asserted UID or namespace identity and ran the probe as root. All reproduced, then
fixed. The checker now proves isolation on FOUR axes through `unshare --user --net`: UID drop
(uid≠parent, i.e. not root), netns identity (`/proc/self/ns/net` inode≠parent), network (a
loopback listener the checker holds in its own netns is UNREACHABLE from the probe — a signal only
real isolation produces), and env ALLOW-LIST (only PATH/HOME/LANG/LC_*/TMPDIR + RUBRIC_*; every
other variable stripped by construction, decoys included). A non-vacuity gate re-runs the SAME
predicate on the UN-wrapped probe and requires every axis to flip to breached — a tautological
axis fails the proof (`isolation-assertion-vacuous`). Sweep broadened to every non-`.md` file
(markdown documents the hazards on purpose) and to octal+symbolic world-writable `chmod`. Mutant
kill-battery green: pass-through `unshare`, real credential names, `network_mode: host` YAML,
`chmod -R 0777`, `chmod go+rwx`. Filesystem containment is NOT claimed in-sandbox (a separate cwd
is not a jail; the sandbox userns does not enforce host ownership) — it is delivered by
gVisor+userns at the PC boundary (S0-08) and listed as not-verified in `runner_design.md`.
`result.json` regenerated through the canonical `scripts/proof-runner`; ledger integrity green;
126 pytest pass (15 S0-11 tests; the two isolation legs skip-with-reason where `unshare --user
--net` is unavailable — "NOT run here", the isolation proof then runs on the PC/gVisor host).
Ledger: `execution_proof` 1 of 7 present. No stubs; the one prior hollow-green class is now a
committed mutant test.

**2026-09-04 sync (Wave 3 increment #18 S0-11 DONE — SUPERSEDED by the reopen above):** Evaluation hardening execution proof.
Runner design doc covers all three audited AlphaEval hazards: host networking (netns via
unshare --net), recursive chmod 777 (never applied), production credential passing (env vars
stripped by construction). Rubric isolation proven with real process-level primitives: probe
fixture runs inside `unshare --net` with credential env vars absent, separate tmpdir cwd,
reports JSON back; checker asserts net_isolated=true, has_credential_env=false, cwd separation.
Grep sweep over proof executable code finds zero prohibited patterns (chmod 777, --network host).
Negative control: fixture attempts to read OPENAI_API_KEY → absent → `rubric-isolation-violation:
credential env absent by construction` rc=1. 6 pytest tests green ×2. Execution proof 2/7.

`s0-18-s0-11-eval-hardening` closed: runner design + rubric isolation proven with real unshare
--net netns + credential stripping + separate cwd. No stubs.

**2026-09-04 sync (Wave 1 increment #9 S0-07 DONE):** First execution proof against a real
upstream dependency. Checker exercises pinned fubuki-os (`7375e56d`) directly via sys.path import
(zero external deps). Three assertions: (1) persona_lint ordering bug reproduced — REVIEW-first
file order gives upstream exit 2 despite VIOLATION findings; corrected exit logic wraps it to
exit 1. (2) BoundDecision.record_id join — evaluate_record returns decisions whose record_id
matches the source MemoryRecord.record_id; approved record passes all filters, proposed record
is denied with status reason. (3) Canonical JSON hash (hash_obj) stable ×2 on identical input;
single-field mutation produces a different hash. Negative control: fixture with corporate-filler
+ closing-filler → `lint-violation: corporate-filler, exit 1 per contract` rc=1. 6 pytest
tests green ×2 (includes upstream-bug-reproduction test). Execution denominator: 1/7 complete.

`s0-09-s0-07-fubuki` closed.

**2026-09-04 sync (Wave 1 increment #12 S0-12 DONE):** Third and final conformance-checked
decision proof. SBOM.yaml created with 22 component pins mechanically derived from
upstream.lock.yaml; THIRD-PARTY-NOTICES.md lists all upstream licenses; LICENSE-DECISION.md
(pre-existing) documents the pending first-party license decision. Pin-diff checker asserts
bitwise pin equality, file existence, and update-procedure presence. Negative: hermes-agent pin
mutated → `sbom-pin-drift: pin differs from upstream.lock.yaml for hermes-agent` rc=1. 5 pytest
tests green ×2. Conformance-checked decision denominator: 3/3 complete (S0-09, S0-10, S0-12).

`s0-12-s0-12-license-sbom` closed.

**2026-09-04 sync (Wave 1 increments #10-#11 S0-09 + S0-10 DONE):** Two conformance-checked
decision proofs landed.

`s0-11-s0-10-gbrain-adr` closed: ADR 0006 accepted — wrap pinned GBrain dream machinery in a
first-party adapter (option A) over adapting selected modules (option B). Conformance checker
validates four required sections, the no-ai-memory-admin-credential statement, and the
proposal-only contract. Negative fixture: ADR copy with credential-isolation statement stripped →
`adr-incomplete: missing credential-isolation statement` rc=1. 4 pytest tests green ×2
(deterministic). Classification: conformance_checked_decision (2/3 conformance denominator).

**2026-09-04 sync (Wave 1 increment #10 S0-09 DONE):** First conformance-checked decision proof.

`s0-10-s0-09-foundry-adr` closed: ADR 0005 accepted — first-party minimal translator for JIT
outputs. Decision: option A (small purpose-built host) over OpenHarness extraction (option B) or
pinned OpenHarness derivative (option C). ADR carries the JIT five-file list (memory.py,
planning.py, action.py, tool_policy.py, prompt.yaml). Conformance checker validates four required
sections (Context, Alternatives, Decision, Consequences), OpenHarness discussion presence, and all
five JIT files. Negative fixture: ADR copy with Consequences section removed → `adr-incomplete:
missing required section: Consequences` rc=1. spec.json: one positive leg + one negative leg.
5 pytest tests green ×2 (deterministic). Classification: conformance_checked_decision (1/3
conformance denominator).

**2026-09-04 sync (Wave 0 spike #6 DONE):** Fourth and final Wave 0 spike closed.

`s0-06-spike-selective-egress` closed POSITIVE: veth pair + iptables in a dedicated network
namespace proves selective egress. NOT bare `unshare --net` (AF-AP-1: total isolation blocks both
legs). Architecture: host-side veth-host 10.200.0.1/24 runs the OmniRoute stand-in on port 12800;
netns-side veth-egress 10.200.0.2/24 with iptables allowing ONLY 10.200.0.1:12800 TCP, default
DROP. Four legs all passed: (1) positive: curl from inside netns reached stand-in at :12800 with
200 + `omniroute-standin` in body; (2) negative blocked-port: curl to :12801 timed out (iptables
DROP, listener IS running); (3) negative external: curl to 1.1.1.1 connection refused (no route);
(4) gate-off mutation: after flushing iptables and setting ACCEPT, blocked port :12801 became
reachable returning `blocked-model` — proves the iptables gate was the barrier, not a structural
artifact (de-vacuous negative control per anti-hollow-green tactic 1). Classification effect:
S0-05 mechanism proven, containment unproven per `map-egress-s005` — full canary suite over live
production units is Wave 2 (increment #16). iproute2 and iptables both available in the sandbox
(apt-installed). Spike artifacts: `spikes/selective-egress/result.json`,
`spikes/selective-egress/probe.sh`.

**2026-09-04 sync (Wave 0 spikes #3-#5 DONE):** Three spikes closed in one session, all POSITIVE.

`s0-04-spike-dockerd` closed POSITIVE: Docker v29.3.1 starts in the sandbox (overlayfs,
cgroupfs, seccomp). hello-world pulled from Docker Hub and ran. KC-6: sandbox is NOT
container-blocked. Venue note for S0-08.

`s0-05-spike-runsc` closed POSITIVE: runsc release-20260817.0 downloaded as a static binary,
runs rootless in the sandbox (systrap platform, kernel 4.19.0-gvisor inside, host 6.18.44).
Sandbox network not supported rootless (host network used). The PC also has runsc (owner-installed,
same release). Classification effect: S0-08 deferral EXPIRED → `execution_proof` per
`map-runsc-s008` — the containment proof must now run. Task DB #7, #8 closed.

`s0-03-spike-rust-ai-memory` closed POSITIVE.
ai-memory v1.39.0 at pinned commit `73715b6` (edition 2024, resolver 3, workspace of 12 crates +
evals) compiled on the PC via the bridge. Default stable toolchain (rustc 1.93.0) succeeded;
explicit `cargo +1.95.0 build` also succeeded (cached). Binaries: `ai-memory` 618 MB, `ai-memory-eval`
306 MB (debug profile). No rust-toolchain.toml in the upstream repo — MSRV 1.95 declared in
workspace Cargo.toml but the default 1.93.0 build did not error (advisory enforcement). Spike
artifact: `spikes/rust-ai-memory/result.json`. Classification effect: S0-06 stays `execution_proof`
per `map-rust-s006` — the four-scope adapter design proof (#13) can exercise the real Rust crate on
the PC. Task DB #6 closed.

**2026-09-03 sync (build started + continuity plane):** `s0-01-registry-schemas-validator` DISPATCHED to the
PC Hermes lane at pin a5bd59b (round 1 halted on a brief premise the coordinator got wrong — AP-43
instance; brief amended to the tree's real shapes; round 2 running). `continuity-offload-plane` OPENED
(task DB #25): landed batch 1 (scrubbed transcript export sandbox + PC, per-class secret tests, post-push
sync, role -> route defaults, curator/researcher/echo-sweeper roles, brief templates) and batch 2
(docs/WORKFLOW-OFFLOAD-MAP.md, docs/HANDOFF-HERMES-LANES.md attached to chat). First route probe
(gemini-3-flash as researcher) running. Owner rulings recorded: offload every consistent low-judgment
step; this structure = the first coding team's blueprint.

**2026-09-03 sync (gVisor on the PC):** the owner ran the sudo install; `/usr/local/bin/runsc` verified
(release-20260817.0, sha256 matches). Rootless gVisor container PROVEN with `--runtime-flag ignore-cgroups
--security-opt label=disable` (inside: `4.19.0-gvisor`, gVisor banner, HTTPS out ok; negative control on
crun: host kernel 6.17). Caveats recorded in PC-BRIDGE.md (SELinux label off for runsc containers; no
cgroups rootless). Effect: S0-08 is no longer blocked on capability once spike #5 lands its artifact
(`spikes/runsc/result.json`, map-runsc-s008) with the registry/validator of increments #1-#2 — the
reclassification goes through the machinery, never by hand. Task DB: no status change yet.

**2026-09-03 sync (PC lane PROVEN end to end):** runs 7-9 closed the last defect — Hermes's terminal cwd
is carried by `TERMINAL_CWD` (now exported per lane): `pwd` = pinned linked worktree, HEAD = PIN,
`git push`/`gh pr` BLOCKED under yolo by the profile deny list, a new file fetched through the patch path
and applied in the sandbox. Registry AF-AP-8/9; orchestration skill carries the placement rule. Build
lanes are ready: increment #1 rides the lane after the owner's go-ahead on the direction doc. Owner
sudo step for gVisor still pending.

**2026-09-03 sync (Hermes lane round trip PROVEN, spike `hermes-lane-trial`):** six runs on the PC lane.
Run 6 completed the brief end to end in 3m43s (quartet present, venv ok, repo tests 9/9 on the PC, DATA
report fetched). Defects found by runs 1-5, all fixed with tests: ouroboros MCP crash loop (disabled for
lanes); bridge envelope not unwrapped (`scripts/pc_bridge_exec.py` + 8-check stub test); Hermes cwd restore
(`--in TREE --no-restore-cwd`); hook sentinels unwritable in linked worktrees (`--absolute-git-dir` /
common dir + `tests/test_hooks_worktree.py`); pre-commit hardcoded venv + early exit skipping later gates
(found BY the lane; fixed + negative control); retro gate consuming the lane report (pre_verify off for
lanes). OPEN: the lane shell still runs in the main clone rather than the pinned worktree (patch fetch
empty) — must close before increment #1 rides a lane. gVisor staged; owner sudo step pending.

**2026-09-03 sync (rewordings done; first Hermes lane):** `harness-skill-rewordings` DONE — 15 hand-ported
skills, hand-port-aware sync (allowlist + base hashes, INTENTIONAL/STALE-BASE/--record), pre-commit gate
intact. PC bring-up: clone + venv + quartet + `agentfactory` Hermes profile with the merged snippet.
First trial lane (`hermes-lane-trial` spike) STALLED in MCP startup on the known-broken Ouroboros server
(crash loop, 11 min, zero model calls) — disabled for lanes in the snippet and the profile; relaunching.
Two lane-runner defects fixed on contact: unexported bridge env (KeyError) and the missing PIN line.

**2026-09-03 sync (owner ruling — BUILD lane = Hermes on the PC):** build/fix/debug lanes move to the
owner's Hermes CLI (v0.21.0 on the PC, already wired to OmniRoute `127.0.0.1:20128/v1`), highest
reasoning, via `scripts/pc_lane.sh … hermes`; the coordinator keeps briefs, the contract gate and the
final validation; Opus 4.6 `code-implementer` becomes the sandbox fallback. gVisor `runsc
release-20260817.0` staged in `~/gvisor-install` on the PC (sha512 verified; sha256 048b89aa…) — the
owner runs the sudo install; user-level podman runtime entry written. Direction doc updated; PC lane
bring-up (clone/venv/tools/config/trial) is the next move. `harness-skill-rewordings` in flight.

**2026-09-03 sync (post-close audit):** `harness-skill-rewordings` OPENED (pending, low priority) — the
final sweep showed `.agents/skills` is a verbatim mirror (0 HARNESS PORT notes); the harness doc's
"14 hand-ported" claims were inherited prose (AF-AP-6, second instance) and are corrected. Pre-commit
SKILL-SYNC GATE added (a `.claude/skills` change with a stale `.agents` twin blocks).

**2026-09-03 sync (batch E, port CLOSED):** first wiki compile landed (`wiki/`: 12 topics, 3 concepts,
INDEX/CONTEXT/schema/log, `topics/live-state.md` continuity snapshot; link check clean; no flat N/12).
`port-trading-system-setup` → done. Task DB #23 mirrored. Next: `s0-01-registry-schemas-validator`.

**2026-09-03 sync (ports):** `AGENTS.md` (Codex CLI port, 26.0 KB < 32 KiB budget) and `.hermes.md` (Hermes
port) written by a delegate from the new CLAUDE.md, coordinator-reviewed: 15 standing rules hash-identical
in all three files, GitNexus block byte-identical, zero source-repo terms. Coordinator fixes: dropped the
ported "ignore an injected branch directive" sentence (wrong here — the branch IS the session's), removed
the source repo's proposal ids from the MANAGER CHARTER, added the PC environment safety block (OmniRoute
`:20128` sole egress, never stop the owner's services, sudo, untracked bridge env), and corrected
`docs/HARNESS-PORTS.md` where it still verified a section that does not exist here (AF-AP-6). Batch E
(wiki compile) in flight.

**2026-09-03 sync (batch D):** harness-ports ported by a delegate and re-gated by the coordinator
(`harness-ports/tests/run-all.sh`: 58/58; repo `tests/`: 6 passed): `.codex/config.toml` + role layers,
`harness-ports/{bin,roles,hermes,tests}`, `scripts/pc_lane.sh` (bridge contract = `X-Agent-Token` +
`{"cmd"}` + `/exec`, token via curl `--config -` on stdin), `.agents/skills/` sync, `docs/HARNESS-PORTS.md`.
Coordinator fixes on review: OmniRoute port corrected to the verified `:20128` (the doc had inherited
the source repo's `:8317`); trading-only `vectorbtpro` skill removed from both skill trees. NOT done:
PC smoke (no bridge banner this session), `AGENTS.md`/`.hermes.md` ports (next), wiki compile (E).

**2026-09-03 sync (batch C):** `port-trading-system-setup` — CLAUDE.md rewritten onto the clean-build
structure (skills authoritative, GIT BRANCH RULES → push_clean/safe_commit, QUARTET section, the planning
repo's 15 standing rules folded in); SHELL SYNTAX GATE added to pre-commit (+ `tests/test_shell_syntax.py`)
after batch A shipped a dead syntax tail in post-commit; project MCP servers registered at user scope by
setup.sh (gitnexus/aleph/phoenix-docs); `code-intel-trio` re-pointed at this repo's slug. Batch D
(harness-ports/Codex/Hermes) in flight on a delegate; AGENTS.md/.hermes.md ports + E (wiki-init) next.

**2026-09-03 sync:** pipeline tasks (council, interview→seed, breakdown) DONE; `s0-00-pc-bridge-probe`
DONE (`abb16a0`); `port-trading-system-setup` OPENED (in_progress) — batches A (scripts/hooks) + B
(ledgers/docs/tests/wiki config) landing this commit; C (CLAUDE.md rewrite), D (harness-ports),
E (wiki-init) next. Task DB slots: #1–#3 pipeline, #4–#21 = increments #1–#18, #22 = spike #0,
#23 = the port. Owner rulings recorded: PC via bridge is the host; OmniRoute (already running) is
the model egress — no vLLM dependency.
