---
topic: live-state
last_compiled: 2026-09-03
---

# Live State -- continuity snapshot

## Clocks

- **Origin tip:** `f42fe7f` 2026-09-07 (`claude/soundbox-kit-migration-iz1jwf`) — checkpoints 8h-8m (the four components' round-9/10 repairs) + the regenerated attestations (SHAs are rewritten at push; names by subject)
- **Local HEAD:** = origin (pushed through `push_clean.sh --lanes-live` while lanes hold the tree); the tree carries the UNCOMMITTED live edits of lane B5e only (D5g, N5g, A5g landed as 8l/8k/8m). An account quota stop at 2026-09-06 20:57Z killed VERIFY-D5g and VERIFY-N5g-b mid-run; both relaunched 2026-09-07 12:4xZ, VERIFY-CK9 dispatched, B5e dispatched. Earlier: checkpoint 7 — round-7 lanes D5c (allow-list framing gate) + N5c (probe/classifier
  survivors) landed with verifier verdicts; checkpoint 7a (A5c header requirement) and 6 are on origin. SHAs are rewritten by `push_clean.sh` at push, so this page names commits by subject.
- **Today:** 2026-09-06

## Active lanes
- **S0-01 ACP conformance `s0-07-s0-01-acp-conformance` (tasks #10, #37) — REPAIR IN PROGRESS, REVIEW-PENDING, nothing minted.**
  **2026-09-07 13:5xZ:** the PROBE is MERGE-READY (VERIFY-N5g-b; sha `b9eb56dd…`); its F1 hardening landed as a PHASE-gated killer after the verifier's call-count killer let mutant DL-INLINE live (run, not reasoned — incident + tactic 3d). Lane B5e (tee) reported (`92 passed` ×3) but its F13 is a half fix (handler moved, `try:` not — TERM in the startup window = traceback rc 1, no status; reproduced twice) → follow-up brief sent, tee edits stay uncommitted in `.lanes-live`. **20:1xZ:** checkpoint 8r — the BACKEND landed again (lane D5i: precheck only on wire-byte sinks, `strip_invis` by category, the lenient re-decode as the sole re-decode op; sandbox 500 / PC 500 passed) → VERIFY-D5i; all four components under verification; **19:3xZ:** checkpoint 8q — the TEE landed again (lane B5f: deterministic AST pins for S1/N4/D3, the honest SIGKILL bound, own-pid grandchild cleanup; sandbox 96 / PC 96 passed) → VERIFY-B5f; checkpoint 8p (checker) under VERIFY-CK10; **18:3xZ:** VERIFY-D5h NOT-READY (the precheck rejects `café` in a JSON body; 20 invisible separators still leak; the record wiring unpinned) → lane D5i dispatched on 618749f (byte-view sinks only, category-based `strip_invis`); checkpoint 8p (checker, lane A5h: cap domain, walk-before-read, FINAL arm exact; mutants measured 21/21) gating from a static worktree → VERIFY-CK10; **17:1xZ:** VERIFY-B5e NOT-READY (race killers probabilistic, S1 1/16, the docstring's SIGTERM bound false — buzz-acp SIGKILLs the group, the red state was `-x`) → lane B5f dispatched with the verifier's verified AST pins; **16:4xZ:** checkpoint 8o — the BACKEND landed (lane D5h: fail-closed on invalid UTF-8, control characters in the closure, every oracle op pinned; sandbox 469 / PC gate) → VERIFY-D5h dispatched; **15:5xZ:** VERIFY-CK9 NOT-READY (five blockers: a non-positive timeout disables the cap, walk-after-read lets a FIFO hang the checker, the F43 scan self-test is hollow, one closure rule and six FINAL-arm rules have no killer) → lane A5h dispatched; **15:2xZ:** checkpoint 8n — the TEE landed (lane B5e + the F13 full-window fix; sandbox 93 / PC 93 passed) → VERIFY-B5e dispatched; **14:4xZ:** VERIFY-D5g NOT-READY (three blockers: `utf8_redecode` fails OPEN on invalid UTF-8 — one junk byte restores the verbatim-record leak; a tautological `_json_safe` test; an oracle op with no self-test) → lane D5h DISPATCHED on dd0cbc2 (fail-CLOSED precheck, `strip_ctl`, oracle strictly wider, 40 mutants); lane RW1 (ripwire) DISPATCHED; VERIFY-CK9 (checker r9) running. Build venue: sandbox Opus 4.6 only until the codex quota resets (~2026-09-07 22:00Z; Hermes walks the codex fallback chain on a 429 regardless of `HERMES_MODEL`).
  Owner review 2026-09-05 DECLINED closure (five mutations passed the checker; result.json WITHDRAWN, S0-01 ABSENT).
  Checkpoint 7 (2026-09-06): round-7 lanes landed — D5c rebuilt the backend framing gate as an ALLOW-LIST over the input domain (192-cell
  table with forged tails; AF-AP-30 recurrence 10 / AF-AP-47 closed at the class) and N5c killed the verifier's 14 survivors (55/55);
  B5b (tee) verdict NOT-READY (20 findings) → lane B5c on the PC Hermes lane (`pc_lane.sh`; brief + probes under
  `tasks/briefs/s0-01-b5c-*`); checkpoints 8f/8g pushed; VERIFY-N5e NOT-READY (an intermediate exec stage recorded as the interpreter, a dead fallback arm, a partial crash evidence set) → lane N5f LANDED at checkpoint 8j (sandbox + PC gates green on 3.11 and 3.13) → VERIFY-N5f NOT-READY (the kept-early-reading arm never executed; the early site can self-sample; the schema pattern accepts a trailing newline) → lane N5g building in the sandbox (every sample site pinned, the pattern's true end anchor with the four attestations regenerated). CI went RED at 8j (runs 106-110): the schema is an ATTESTED input of the four minted proofs — regenerated at f1e1316 (AF-AP-56); VERIFY-D5e NOT-READY (fail-open "fail-closed",
  tautological oracle) → lane D5f LANDED (checkpoint 8h: boolean fail-closed, self-proving oracle; sandbox + PC gates green) → VERIFY-D5f grading; VERIFY-B5c NOT-READY (loss cliff moved to 5 s; status vs timeline) → lane B5d LANDED at checkpoint 8i, sandbox + PC gates green, VERIFY-B5d grading (drain to EOF,
  status inside the lock); A5f landed (8g) → VERIFY-CK8 grading; all in the sandbox (Kimi cooled three times; codex out ~31 h);
  VERIFY-CK8 NOT-READY (5 blockers: untested F13/F19 guards, F14 on 2/5 legs, two A20a rules un-gated, a hollow hardlink source scan) → checker lane A5g RUNNING on the PC Hermes lane (Kimi K3) with every startup value now pinned; pushes run through `--lanes-live` (detached-worktree rewrite; the ref follows origin on tree identity); nothing minted; tree-wide suites now
  run on the PC (`scripts/pc_suite.sh`, 8 workers) after the sandbox disk filled mid-gate; the PC bridge is UP (backend on :20201,
  420 records, PC clone at checkpoint 5 — ff-sync before the re-capture).
  Checkpoint 6 (2026-09-06): the Codex audit of checkpoint 5 repaired (CI collection fix AF-AP-44; scan v2.3 header + zombie rule
  AF-AP-45 with a real-producer sandbox test and committed controls; tee-status consumed per A21d; two-POST = fixture realism);
  round-6 repairs N5b/D5b/A5b landed, B5b (tee) in flight; BRIDGE BACK — five legs + negative rehearsed, finding: buzz-acp
  SIGKILLs the agent group at shutdown (A21d running status); fresh corpus passes 44/46 real-leg checks. NEXT: B5b → A5c → verifies →
  final re-capture → golden pin → real-bundle mutation suite → canonical runner. Round 5 (checkpoint 5): D5/N5/B5 CLOSED every
  assigned finding with revert-reds (69/158/60 passed ×2);
  A5 implemented A19-A26 but left the audit's four mutation tests, the mutation harness, suite speed (~500 s) and three
  ungated screens → lane A5b; verify lanes for N5/B5/D5 run alongside A5b. Repair rounds 2-4 landed at checkpoint 4: single pin module `proofs/S0-01/pins.py` (manifest v2.2, four
  trees incl. the venv, symlinks + modes, baseline re-pinned), `negative_contract.py` (live negative: `-32602 Invalid
  params` from the pinned agent; 42 tests; wiring = round 5), PC capture toolchain under `proofs/S0-01/tools/pc/` (env
  from secret files, owned-pid closure, teardown scans; validated on real PC dry runs), tee `tee-status.json`, backend
  credential screen at the record boundary, checker `--fixtures-dir` + real-leg conformance against four REAL PC
  captures + the real negative. Round-4 suite kills 85/85 round-2 mutants. The owner's Codex audit of `08a4a7d`
  (`docs/reviews/2026-09-05-codex-audit-08a4a7d.md`): six P1 + two P2 — the open ones are round 5 (brief drafted,
  amendments A19-A26: request/response classification, duplicate responses, (check, leg) SEQUENCE guard, header
  credential screen, negative wiring, tee drain gating, backend GET-with-body). FINDING: production `BUZZ_ACP_AGENTS=1`
  + `steering_supported=false` ⇒ two-user turns serialized; the proof asserts ingress concurrency + observed
  serialization. NEXT: round 5 → PC re-capture with the final tools (`run_leg.sh` × 5 + negative; first `git checkout --`
  the staged pc files on the PC clone, ff-sync, `pc_backend_restart.sh`) → pin golden sha → mutation suite on the REAL
  bundle → canonical runner on `pc-bridge` → ledger → owner review. Pending owner: ADR 0002 transport (#35), firewall
  narrowing, #30 acceptance anchor.
- **Code-intel: ripwire v0.4.0 ADOPTED 2026-09-07 as the SIXTH, ADVISORY instrument (owner ask: "worth adding to the quartet"; lane RW1 landed the digest pin, the setup.sh install, `scripts/ripwire_review.sh` + 21 wrapper tests, the docs and the code-intel-trio section; the PC-side install is an owner-run step in THIRD-PARTY-AGENT-TOOLS.md §ripwire):** single offline C++ binary (`ripwire-0.4.0-linux-x64.tar.gz`, sha256 `fd0bd0fa…bfc8` matches the published `.sha256`; integrity only, no signature), tag `v0.4.0` = commit `e663ca8f…`; on this repo with the vendored trees excluded the cold ranked map takes 1.6 s (est_tokens 2766 at top-60), warm graph verbs ~0.1 s (`--callers=_write_status` → main/pump_fd/pump_pipe, correct; `--exercises=<tee test>` 7 symbols; `--test-gate`), the conceptual `--for` route 6.9 s / 4102 tokens with the right two hits first (checker `check_tee_status`, tee `main`). Flat verbs take `--limit=N`, never `--top-k`. Skipped: 98 files unsupported-ext (`.txt/.jsonl/.summary`, extension-less `scripts/proof-runner`). The tarball also ships `skills/` + `hooks/` — NOT installed (binary only, digest-pinned, advisory, never a gate — the sentrux template).
- **Code-intel: sentrux adopted 2026-09-05 as the FIFTH, ADVISORY instrument** (owner decision; same standing as
  slopo): `scripts/sentrux_review.sh save|compare|check`, rules `.sentrux/rules.toml`, pinned by digest in
  `upstream.lock.yaml`; never a gate. Blind spot: Python import resolution is weak here (4/390 specs), so
  complexity/length are the live signal.
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

S0-01 repair, probe MERGE-READY (VERIFY-N5g-b) + B5e follow-up + ripwire spike — 2026-09-07 13:5xZ; next update at the final re-capture with the final tools (golden pin, real-bundle
mutation suite, canonical runner on pc-bridge) or the owner's review. This
page's pre-09-04 lane entries are being brought forward incrementally; the ledger
(`todo/BUILD-TASKLIST.md`) wins on any status disagreement.
