# Stage 0 build direction — for owner review before increment #1

STATUS: proposal, 2026-09-03. Waiting for the owner's notes or "go ahead". Nothing below is built.
Sources this distills (they win on any disagreement): `seeds/seed-stage0-v1.yaml` (the contract),
`tasks/stage0-breakdown.md` (the 18 increments + pinned decisions), `todo/BUILD-TASKLIST.md` (live
status), `docs/research/COUNCIL-VERDICT-STAGE0-v1.md` (wave-plan-v2, kill criteria KC-1..KC-7),
`docs/07_BUILD_PLAN.md` §Stage 0.

## 1. What "build Stage 0" means

Twelve proofs S0-01..S0-12, each an executable gate with exit evidence, classified FOUR ways
(execution proof / conformance-checked decision / blocked on external input / blocked on
capability — never a flat N/12). No application code exists, so the first code is the proof
harness itself: `proofs/` (registry, schemas, validator, per-proof specs + fixtures + runners),
`spikes/` (Wave-0 facts), `tests/` (deterministic gates), a generated ledger and a two-job CI.
The gate the docs set: **no broad feature work until the proof pack validates the
Buzz→ACP→Hermes→OmniRoute spine, memory composition, Fubuki seams, policy failure behavior, and
gVisor compatibility.** Stage 1 features are out of scope for this whole plan.

## 2. Order — wave-plan-v2, 18 increments

**Wave F — foundation (sandbox, first, sequential):**
- #1 registry + JSON schemas + validator with EMPTY-SET semantics: integrity check green on the
  honest empty set, the stage gate RED; forged digest / drift / unclassified proof → RED for the
  exact stated reason; validator mutation-audited.
- #2 runner + ledger generator + CI split checks (`ledger-integrity` vs `stage1-gate`) +
  probe-backed `NOT run here` markers re-evaluated on every CI run (a marker is never a static
  file). Generator byte-identical on two runs.

**Wave 0 — spikes (ON THE PC over the bridge, parallel; facts recorded either way):**
- #3 rust-ai-memory: `cargo +1.95.0` build of the pinned commit. Decides S0-06's class through the
  frozen mapping `map-rust-s006` (spikes classify, never gate).
- #5 runsc: static install + one trivial runsc container run, systrap platform (no KVM needed).
  Needs `sudo` → owner step; confirms or lifts S0-08's blocked-on-capability label.
- #6 selective egress: the veth/proxy-shaped mechanism that lets a unit reach OmniRoute `:20128`
  and NOTHING else. Bare `unshare --net` is total isolation and is banned as S0-05 evidence
  (registry row AF-AP-1). Positive leg reaches the allowed target; negative leg is denied with
  the exact reason.
- #4 dockerd-in-sandbox: secondary (the PC uses podman); recorded, not load-bearing.
- Prerequisite on the PC, done over the bridge: clone this repo at `~/agent-factory` on the
  designated branch, a `python3.11` venv, and the pinned upstream checkouts from
  `upstream.lock.yaml` under `~/agent-factory/upstream/`. The harness-ports PC smoke falls out of
  this step for free.

**Wave 1 — disjoint proofs (parallel delegates; spec + fixtures in the sandbox, live legs on the PC):**
- #7 S0-01 ACP conformance: `buzz-acp` launches the REAL pinned `hermes-acp` in a podman stack;
  normalized golden transcripts stable ×2; the exact `protocol-violation: missing required
  initialize field` on the negative fixture.
- #8 S0-02 Buzz authorization/freshness: exactly one turn on the allowed fixture; FOUR distinct,
  named denials (unauthorized / invalid signature / replayed / stale) produce NO turn.
- #9 S0-07 Fubuki corrections: `persona_lint` exit-2 ordering fix with an ordered regression
  fixture; `BoundDecision.record_id` join; governance hash stable ×2.
- #10 S0-09, #11 S0-10, #12 S0-12: ADR + machine-checkable conformance shell each (a removed
  section, a removed credential-isolation statement, a mutated pin → RED).

**Wave 2 — dependent proofs (after the spikes classify):**
- #13 S0-06 four-scope adapter against REAL pinned ai-memory on the PC: auth tuple validated
  outside model control; Agent→Project→Team→Company precedence; leak fixtures never cross;
  unauthorized tuple denied.
- #14 S0-03 Hermes→OmniRoute LIVE round trip on the PC: `codex_responses` wire mode, `key_env`
  only, a real tool-call; identity assertion = the routed model id OmniRoute reports;
  key-disable → RED; a stub is FORBIDDEN.
- #15 S0-04 compression contract: request/response headers asserted; the ONE sanctioned
  deterministic stub (request-preservation instrument) sits BEHIND real OmniRoute.
- #16 S0-05 full canary suite over the live units: every unit's egress canary FAILS after its
  positive control; gate-off → RED.
- #17 S0-08 gVisor containment spec + fixtures; live run on the PC once the runsc spike lands;
  the NOT-run marker re-probed every CI run until then.
- #18 S0-11 evaluation hardening: runner design + rubric isolation (unprivileged, no
  credentials, no network); zero `chmod 777` / host-network hits in the fixtures.

## 3. How every increment is built

- One increment = code + deterministic LLM-free test + commit (`S0-#n: <proof> — <what>`);
  negative control failing for the exact expected reason; deterministic runs twice, bitwise;
  mutation audit on every gate; `/bug-echo` on every real defect; the ledger and task DB updated
  in the same increment; four-way status lines only.
- Delegation: build lanes go to `code-implementer` with a brief-as-file and disjoint boundaries
  (one `proofs/<id>/` tree per lane); verify lanes to Opus 5; root cause, design and the final
  verdict stay in the main loop; commit + push before every dispatch.
- Venue: the sandbox for code, specs, fixtures and unit gates; the PC via `scripts/pc.sh` for
  anything live, container, Rust or model-bound. A proof that cannot run where it is gets spec +
  fixture + an explicit `NOT run here: <reason>` marker — never a fake green.
- Fixtures are committed and canonical; they drive the REAL pinned binaries. The only stub in the
  whole pack is S0-04's instrument, at the boundary `docs/03` §2 itself specifies.
- Kill criteria KC-1..KC-7 from the council verdict are checked at each wave boundary.

## 4. Decisions that need the owner

1. **`sudo` on the PC** for the runsc install (spike #5). `modprobe kvm_amd` is optional — systrap
   needs no KVM.
2. **S0-02 test target:** the plan is a FRESH throwaway Buzz relay stack in podman (own ports, own
   database) for the authorization fixtures — never the running `buzz-prod` stack. Confirm, or
   name the instance you want used. Your test Buzz stays up either way; nothing on the PC is
   stopped or restarted without your say-so, now or when we go live.
3. **S0-03 target:** which OmniRoute model id the live round trip should route to (that id becomes
   the identity assertion), and the environment variable name Hermes reads the OmniRoute key
   from (`key_env` only — no key in the repo, no direct provider credential anywhere).
4. **PC checkouts:** cloning this repo and the six pinned upstreams under `~/agent-factory/` on
   the PC over the bridge is the first PC-side step. Say if you want a different location.
5. **Parallelism:** Wave 1 proofs run as parallel delegate lanes by default (council: parallel by
   component). Say if you prefer strict S0-01→S0-12 order.

## 5. What will NOT be done

No stubs, fakes or hard-coded values beyond S0-04's instrument; no LLM judge in any gate; no flat
proof counts; no direct provider credentials; no Stage 1 features; no changes to running PC
services without the owner; no claim of "runnable" before the executable acceptance gate passes.

## 6. First moves after "go ahead"

1. #1 registry/schemas/validator (sandbox) → 2. #2 runner/ledger/CI (sandbox) → 3. PC prep over
the bridge → Wave 0 spikes #3 / #5 / #6 in parallel, each recorded either way → 4. Wave 1 lanes.
Expected shape: Waves F and 0 in the next working session, Wave 1 after that, Wave 2 once the
spikes have classified S0-06 and S0-08.
