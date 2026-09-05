---
topic: live-state
last_compiled: 2026-09-03
---

# Live State -- continuity snapshot

## Clocks

- **Origin tip:** `61c9f77` 2026-09-04 (`claude/soundbox-kit-migration-iz1jwf`) — chat-digest sync after the S0-01 grounding corrections
- **Local HEAD:** 1 commit ahead of origin at write time (the 2026-09-05 handoff-reconciliation
  increment: OmniRoute invariants monitor + tests, incidents AF-AP-33/34/35, docs sync). SHAs are
  rewritten by `push_clean.sh` at push, so this page names commits by subject.
- **Today:** 2026-09-05

## Active lanes
- **S0-01 ACP conformance `s0-07-s0-01-acp-conformance` (task #10) — PROOF RUN RECORDED 2026-09-05, REVIEW-PENDING.**
  Pinned clones on the PC (`~/s0-01-pinned/{hermes-agent@527da60,buzz@1c8321c,acp@37a7d4f8}`), isolated relay stack,
  sanctioned scripted route `s0-01-scripted` behind the real OmniRoute (task #36, owner/Codex). Five legs captured as RAW
  frames with identical pre/post manifests: golden ×2 (11 normalized lines, byte-identical), `!cancel` → cancelled with
  zero orphans, `!shutdown` → exit 0, two users under allowlist → two sessions. `check_acp_conformance.py` PASS; spec
  wired into the canonical runner. NEXT: runner on the PC venue → result.json → ledger-gen/validate → owner review.
  History: initialize milestone (client offered 2 / agent returned 1) and two live-model turns (structure
  non-reproducible → scripted golden) on 2026-09-05. Credential caveat applies only to the two live runs.
- **Handoff reconciliation (task #31) — DONE 2026-09-05:** Codex's OmniRoute/Hermes handoff ported verbatim
  under a review header (reproduced vs reported); `scripts/omniroute_invariants.sh` (read-only, 7 checks,
  11 deterministic tests) — live: 5 OK, `require_api_key` FAIL, `catalog` FAIL (no key file); offload map +
  `pc-lane.sh` comment synced to the 2026-09-05 combo orders; focused lane tests 33/33 ×2, full harness
  suite green. **Incidents logged:** AF-AP-33 (orphan listener), AF-AP-34 (the coordinator's `pkill -x`
  restarted the PRODUCTION Buzz relay 4× on 2026-09-04 — reported), AF-AP-35 (the coordinator leaked the
  OmniRoute `STORAGE_ENCRYPTION_KEY` into the session log).
- **S0-11 eval hardening `s0-18-s0-11-eval-hardening` — ACCEPTED 2026-09-04** (owner process
  decision after 8 reviews; technical proof + trust binding accepted). Cycle 8 fixed the last live
  guard bug: `check-proof-status.py` now BINDS the visible `PROOF-STATUS` line to the ONE canonical
  task row via an EXACT proof→slug map (the S0-10 slug `s0-11-s0-10-gbrain-adr` embeds "s0-11", so a
  substring match would misbind it). Acceptance is a human process decision, NOT machine-enforced
  (the agent pushes under the owner's GitHub identity); the owner-verifiable anchor is the open,
  owner-blocked `acceptance-anchor-af-ap-32` task (#30). **NOTE: the lane entries below predate the
  2026-09-04 Stage-0 wave (S0-07/09/10/12 done; S0-11 cycles 1-8) — the ledger
  (`todo/BUILD-TASKLIST.md`) is authoritative on status, this page is being brought forward.**
- **Increment #1 `s0-01-registry-schemas-validator`** — contract-gate ROUND 2. Round 1 (PC Hermes
  lane, sol-ultra, four runs: wrong premise → two 503 deaths → success at pin c39b64f) was
  harvested 2026-09-03: C1–C3 green in the sandbox; the lane's 33/33 was a host-python green
  (AF-AP-11, harness fixed); the coordinator's spine read shipped three gaps as five RED tests
  (AF-AP-12/13/14). Repair brief `tasks/briefs/s0-01b-repair-spine-gaps.md` → then the verify lane
  (`harness-ports/briefs/verify-contract.md`, terra-xhigh) → coordinator final layer.
- **Continuity + offload plane** (`continuity-offload-plane`, task #25): transcript sync live
  (`transcripts/sandbox/`), lane roles/templates committed, offload map written; first route probe
  (Gemini flash as researcher) running; curator lane not yet run.

- **`port-trading-system-setup`** — DONE with this commit: batches A-D landed, the Codex/Hermes
  ports (`AGENTS.md`, `.hermes.md`) reviewed and committed, batch E (this wiki compile) landed.
  NOT done inside it: PC smoke of the harness ports (needs a bridge banner + the owner).
- **`harness-skill-rewordings`** (pending, low priority): `.agents/skills` is a verbatim mirror of
  `.claude/skills` — the source repo's 14 hand-ported skill rewordings were not carried over;
  the mechanism table in `AGENTS.md`/`.hermes.md` carries translation meanwhile.
- **Stage 0 build:** increment #1 of 18 DONE (machinery: registry + schemas + validator); the
  twelve proofs stay ABSENT by design until their increments run. Pipeline (findings, council,
  interview, seed, breakdown) COMPLETE, all committed. `tests/` fully green (45).

## In-flight runs
- **PC lane bring-up** (2026-09-03): DONE and PROVEN — clone at `~/agent-factory`, pc-setup complete
  (quartet, venv, gitnexus 1.6.10), Hermes profile `agentfactory` with the merged snippet; spike
  `hermes-lane-trial` runs 8-9: shell in the pinned worktree (`TERMINAL_CWD`), push/PR blocked
  under yolo, patch path home. Next lane = increment #1, after the owner's go-ahead. gVisor INSTALLED by
  the owner and a rootless runsc container verified (see PC-BRIDGE.md for the invocation + caveats).

- **FROZEN 2026-09-03 (owner review):** no new increment work until the review-fixes lane lands —
  real CI (`stage0-ci.yml`), fail-closed `sync-skills.sh`, hygienic hook-adapter test (task #26);
  then the upstream-lock refresh (#27) and the vendored-kit packaging decision (#28, owner).
- **Increment #2a LANDED (2026-09-03):** runner + probes + committed markers; the honest ledger on
  the PC now reads `S0-03 BLOCKED (credential_absent)`, `S0-08 EXPIRED` (runsc works there → the
  gate demands the proof run). D5 re-ruled: expiry is a state for integrity, a RED for the gate.
  NEXT: 2a adversarial lane (`agentfactory-verify`) + 2b build lane (`agentfactory-build`) in parallel.
- **Increment #2 SPLIT into 2a/2b (2026-09-03)** after three PC lanes failed to land it: two brief
  defects caught by the lanes' premise checks (fixed, rules 0a/0c baked) and one compaction loop
  (AF-AP-19; CONTEXT BUDGET rule now in every lane prompt). `s0-02a-runner-probes` is the next
  dispatch on `agentfactory-build`; `s0-02b-ledger-normalize-ci` follows its landing. OWNER ACTION:
  raise the lane profile's `compression.threshold` to 0.8 / `protect_first_n` to 6 (INCIDENT-LOG).
- **Increment #1 CLOSED 2026-09-03.** Adversarial lane `s0-01e` returned one under-reporting
  finding (fixed in the main loop under the round cap, killer test in `tests/red/`); attacks A1–A8
  SOLID; 45 tests ×2; C1–C18 18/18. NEXT: increment #2 `s0-02-runner-ledger-ci` dispatched to the
  `agentfactory-build` lane (brief committed, PIN at dispatch). Owner action pending: rebuild the
  `agentfactory-sweep` combo (dead head routes — INCIDENT-LOG). Repair lane `s0-01d` DONE on
  `agentfactory-build` (44 passed ×2; first lane to run under the incremental-report rule — its
  report-draft.md was written). Verify lane `s0-01c` died mid-run after 167 calls (AF-AP-16/17);
  its transcript and red suite were recovered. Repair lane `s0-01b` DONE (39 passed ×2).

## Pending owner decisions
- **RESOLVED 2026-09-05 (owner via Codex): OmniRoute auth** — `hermes` key rotated everywhere, `REQUIRE_API_KEY=true`,
  reproduced (401/401/200; monitor 7/7). `STORAGE_ENCRYPTION_KEY`: owner decided NOT to rotate now (#33 closed).
  Residual: port 20128 LAN-reachable behind auth — firewall narrowing deferred (owner).
- **S0-01 golden route (owner or Codex):** add an `openai-compatible` provider connection in OmniRoute pointing at the
  deterministic scripted backend (`proofs/S0-01/tools/scripted_backend.py`; recipe in GROUNDING) — the live route's
  event structure is non-deterministic (demonstrated 2026-09-05 with two runs).
- **(#35) ADR 0002 wire mode:** live Hermes profiles use `chat_completions`; the ADR pins `codex_responses` +
  `x-omniroute-compression: off` — amend or revert.
- Handoff items 6 (Web2API re-auth + real generation test) and 7 (Google keys' Cloud project/billing identity).
- **BUILD lane = Hermes on the PC (owner ruling 2026-09-03):** bring-up in progress (clone, venv,
  config merge, trial lane); the OmniRoute model id for the lane is being resolved from `/v1/models`.
- **Build-direction review** (`tasks/stage0-build-direction.md`, 2026-09-03): the owner asked for
  the direction summary before increment #1; building waits for their notes or "go ahead".

- `sudo modprobe kvm_amd` on the PC (KVM modules present but unloaded; needed before gVisor tests)
- runsc install on the PC (absent; systrap platform needs no KVM but the binary is missing)
- Keep-alive Routines: NOT enabled (owner-optional; the 2026-08-01 trigger-tool caution stands)
- PC smoke of the harness ports (owner must merge Hermes config, run MCP smoke probe)
- Five owner inputs from the decision log: first-party license, deployment target, Buzz community,
  first OmniRoute route/budget, default memory degradation policy
- podman-compose availability on the PC (absent; buzz-prod containers exist via some compose path)

## Do-not-trust

This wiki is a map, not the territory. The ledger (`todo/BUILD-TASKLIST.md`) wins on any
build-status or count disagreement.

**NOT-built (first-class):**
- No application code for the spine exists (STATUS.md: Stage 0 machinery in progress)
- Telemetry plane planned; sinks (OpenObserve 5080, Phoenix 6006) running on the PC but receive
  nothing from this project
- Harness ports unit-proven in the sandbox only; NOT smoke-tested on the PC
- Ouroboros native MCP broken (MCP-SDK v2 vs v1.x); stdio fallback (`scripts/ooo_mcp.py`) works
- Wiki compiled from planning docs, not from code
- Pre-commit now runs three gates (pyflakes delta, shell syntax, skill-sync); none of them is a
  test of the Stage 0 spine — that spine does not exist yet
- Stage 0 proof pack: 1 of 18 increments closed (#1), #2a landed; the twelve proofs ABSENT by design

## Last updated

S0-01 proof run recorded (five legs, golden ×2, checker PASS) — 2026-09-05; next update when result.json + ledger
land from the PC venue and the owner reviews. This
page's pre-09-04 lane entries are being brought forward incrementally; the ledger
(`todo/BUILD-TASKLIST.md`) wins on any status disagreement.
