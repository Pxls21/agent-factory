# Agent Factory — Progress Report & Reviewer Handoff (2026-09-22)

**Audience:** an external code reviewer (e.g. OpenAI Codex) doing a deep pass over branch
`claude/soundbox-kit-migration-iz1jwf` of `Pxls21/agent-factory`, and the owner.
**Purpose:** say what was built, what was *proven*, what was *decided*, and what is **not done** — written
to be checked against primary sources, never to flatter. Every claim names the file, commit or command
that lets you falsify it. Times are UTC.

> **Read this first, then trust the repo over this doc.** The single source of truth for build status is
> `todo/BUILD-TASKLIST.md` (the ledger; its newest notes sit at the top of §LIVE). Decisions live in
> `docs/08_DECISION_LOG.md`; incidents and the anti-pattern registry in `docs/INCIDENT-LOG.md`. This
> report is a distillation and can drift; on any disagreement the ledger wins. The previous report of
> this kind is `docs/PROGRESS-REPORT-2026-09-17.md`; this one covers 2026-09-17 → 2026-09-22 02:5xZ.

---

## 1. Where things stand (one paragraph)

Stage 0 is an executable proof pack over the integration seams of a governed agent pipeline
(Buzz → `buzz-acp` → Hermes → OmniRoute → models; Fubuki governance; ai-memory scopes; a fail-closed
policy gate; gVisor). Twelve proofs are registered (`proofs/registry.yaml`). **Ten are minted**
(`proofs/ledger.json`: seven execution proofs PRESENT of nine — S0-01, S0-03, S0-04, S0-06, S0-07,
S0-08, S0-11 — and three conformance-checked decisions of three; no blocked markers). **Two are
ACCEPTED by the owner's GPG-signed tags**: S0-11 (2026-09-04; its tag needs a re-sign, see §6) and
**S0-01 (2026-09-22 02:39Z, this report's headline)**. **Two execution proofs are absent**: S0-02
(the eight-leg live capture — its runner needs a one-line environment selection, lane B7 is doing it,
then the owner runs one relay-membership command) and S0-05 (the live-unit legs — the units it would
measure do not exist yet). The first application code (`src/agent_factory/governance`, GOV1/GOV2)
exists and is unchanged since the 09-17 report.

## 2. Proof table (2026-09-22)

| proof | class | state (from `proofs/ledger.json` + the ledger) | verify state |
|---|---|---|---|
| S0-01 ACP conformance | execution | **ACCEPTED 2026-09-22** — minted e458801 (2026-09-21, venue pc-bridge) over the v2.4 live capture; tag `accepted/S0-01` on 0b3a7d4, object `docs/governance/tags/accepted-S0-01.tag` | VERIFY-VB-F12 NOT-READY (one test-oracle blocker) → G2 repair → VERIFY-G2 MERGE-READY-WITH-FOLLOWUPS (issue #10) |
| S0-02 Buzz authz/freshness | execution | ABSENT — checker good-state (rounds B1-B5); B6 landed 2026-09-22 (issue #3); the capture is lane B7's | verify-followups #3 (closed by B6, pending verify), #5 |
| S0-03 Hermes→OmniRoute round trip | execution | PRESENT (minted 2026-09-19) | verify-followup #6 |
| S0-04 compression contract | execution | PRESENT (minted 2026-09-19); lane S4H (issue #7 batch 2) running | verify-followup #7 |
| S0-05 no direct egress over live units | execution | ABSENT — canaries/library/checker landed (lane E1, 2026-09-08); `proofs/S0-05/evidence/units.json` on the PC (2026-09-19): every unit not-run (three positive controls unreachable, five units do not exist) | — |
| S0-06 four-scope adapter | execution | PRESENT (minted 2026-09-19) | verify-followup #4 |
| S0-07 Fubuki corrections | execution | PRESENT (2026-09-07) | — |
| S0-08 gVisor containment | execution | PRESENT (minted 2026-09-18) | — |
| S0-09 / S0-10 / S0-12 | conformance-checked decisions | PRESENT (2026-09-04) | — |
| S0-11 evaluation hardening | execution | PRESENT; **ACCEPTED 2026-09-04** — the tag must be RE-SIGNED (the result was regenerated 2026-09-14 after an attested-input change; `check-proof-status.py` says so) | — |

Check it: `python3 scripts/validate-ledger integrity --root .` (7/9, 3/3, 0/1, 0/1) ·
`python3 scripts/check-proof-status.py` (today: only the S0-11 re-sign line) ·
`git verify-tag accepted/S0-01` after `git hash-object -w -t tag docs/governance/tags/accepted-S0-01.tag`
(the object is content-addressed; the committed public key is `docs/governance/owner-signing-key.asc`).

## 3. Timeline 2026-09-21 → 2026-09-22 (what landed, in order)

| when (UTC) | event | primary source |
|---|---|---|
| 09-21 12:50 | The independent audit's findings dispositioned: A5p re-labelled GATED-PENDING-VERIFY (a coordinator re-run of a builder's gate is not independent verification), four meta-oracle defects reproduced → issue #8, the recapture criterion widened | 36b08ab |
| 09-21 13:37–14:30 | **S0-01 v2.4 live recapture** on the PC over the bridge: the isolated harness restarted after a host reboot (relay + backend + three containers), the preflight found and fixed an AF-AP-105 sibling red-first, five legs + the negative ×3, run-1 AND run-2 captured; committed NOT minted — the golden showed a race | 36dac29, 38ad46b; `tasks/briefs/s0-01-vb-f12-recapture-v24.md` |
| 09-21 15:23 | T2 (local-Qwen build lane): the committed bundle pinned through the REAL proof-runner | a3774a2 |
| 09-21 16:3x | **Owner decision (a) → D-035**: the golden made order-free for asynchronous session-metadata notifications (`session_info_update`), everything else stays bound | `docs/08_DECISION_LOG.md` D-035 |
| 09-21 20:46–21:06 | G1 (local-Qwen build lane) lands the order-free normalizer; **S0-01 MINTED** e458801 (venue pc-bridge); a deferral-test fix | c52bcda, e458801, 955ab74 |
| 09-21 22:28 | VERIFY-VB-F12 (local-Qwen verify lane): NOT-READY on ONE test-oracle blocker — G1's reorder controls duplicated a neighbour instead of swapping, so two production mutants survived the suite while the real checker's verdicts changed → AF-AP-109 | 85836a5; `tasks/briefs/s0-01-vb-f12-support/VERIFY-VB-F12-report.md` |
| 09-22 00:12 | G2 (local-Qwen build lane) repairs the controls (true swaps, self-verifying) and adds two `check_golden`-level tests that kill M4/M8; T only, the mint unchanged | f84265f |
| 09-22 00:19 | PC 13-file S0-01 gate on the pushed head: `1405 passed in 156.20s` (set c62435272c99) | 236bec7 (ledger) |
| 09-22 01:1x | **Owner ruling**: up to FOUR Hermes lanes at once on the vLLM route (the coordinator's one-lane premise was the retired llama.cpp unit's); CLAUDE.md corrected; three build lanes dispatched beside VERIFY-G2 | fe28648 |
| 09-22 01:30 | Correction: the S0-02 capture uses the ISOLATED harness (up), not the production Buzz stack; its real prerequisites named | b398af6 |
| 09-22 02:18 | **VERIFY-G2**: MERGE-READY-WITH-FOLLOWUPS — the repair reproduced, M1–M8 all killed by named tests, three `478 passed` suites; F1/F2 → issue #10 | 8494671, d92bfcf |
| 09-22 02:39 | **Owner signs `accepted/S0-01`** (Good signature, key 6F6C…19C1); the PC's tag push drew HTTP 403, the tag object came over the bridge and is committed; ledger row + `PROOF-STATUS` marker flipped together; STATUS.md refreshed | 587e5b2 |
| 09-22 02:5x | B6 landed (issue #3: the S0-02 F3 refusal executed through the real CLI against an owned listener) | c439580 |

## 4. The S0-01 acceptance, unpacked (what a reviewer should check)

1. **The capture is real and reproducible.** `proofs/S0-01/evidence/golden/` holds five positive legs
   (run-1, run-2, cancel, shutdown, two-users) and the negative leg, produced on the owner's PC by the
   pinned tools (`proofs/S0-01/tools/pc/`) against the isolated harness (throwaway `buzz-relay`, the
   scripted deterministic backend behind real OmniRoute — the ONE sanctioned stub, owner-sanctioned
   2026-09-04). Manifests and per-tree digests are pinned in `proofs/S0-01/pins.py`
   (`PINNED_BASELINE_*`, `PINNED_GOLDEN_SHA256`).
2. **The checker is frozen and hostile-tested.** `proofs/S0-01/check_acp_conformance.py` (round 18,
   D-034 declared-final) grades every leg; `tests/test_s0_01_check_acp_conformance.py` (6,400 lines)
   holds the meta-oracle: golden regeneration, hostile bundles (AF-AP-36), the reorder controls, the
   M1–M8 mutant kills. Run: `python -m pytest -n 8 tests/test_s0_01_check_acp_conformance.py
   tests/test_s0_01_spec_runner.py` → `478 passed` (needs `S0_01_REAL_LEG_DIR` + `S0_01_VENUE`; in CI the
   real-corpus tests skip by declaration).
3. **Decision (a) is narrow.** Only the raw position of `session_info_update` frames is order-free
   (`pins.ASYNC_SESSION_UPDATES`, a closed tuple); count, payload shape and session identity of those
   frames stay bound; every other frame's order stays bound (`normalize_timeline`, C:795-887). The
   verify round proved a duplicate, a foreign session id, a changed payload and a widened set are each
   refused.
4. **The mint is attested.** `proofs/S0-01/result.json` hashes its inputs (AF-AP-56); a second mint
   differs only in timestamps/digest; `validate-ledger integrity` reports PRESENT.
5. **Independent verification happened twice** (VERIFY-VB-F12, VERIFY-G2), both by a different model
   lane than the builder, both with GATE RECOMMENDATIONS, both graded by the coordinator under the
   blocking predicate; the one blocker found was repaired (G2) and re-verified. Coordinator re-runs of
   lane gates are labelled as such everywhere and never counted as verification.
6. **The owner's acceptance is a signature, not a status word.** `check-proof-status.py` verifies the
   signed annotated tag against the committed public key and that the tagged commit holds a
   byte-identical `result.json`; a status cell alone cannot flip a proof to ACCEPTED (AF-AP-32).

## 5. Lanes in flight at 02:5xZ (all on the owner's PC, local Qwen3.8-27B via vLLM; four at once)

| lane | issue / goal | boundary | brief |
|---|---|---|---|
| A5q | #8 — the CK16 classifier-operand meta-oracle's four audited defects (A5P-02..05), red control per row; the boolean-context claim made TRUE (If/While/Assert/IfExp tests + `not` inventoried) | `tests/test_s0_01_check_acp_conformance.py` outside the G2 hunks | `tasks/briefs/pc/pc-a5q.md` (PIN 236bec7) |
| K1-c | the vendored-tree manifest (source/commit/license/tree-sha per vendored root) resumed from the recovered 2026-09-08 draft under AMENDMENT 1's symlink rule | `scripts/vendored_manifest.py`, `tests/test_vendored_manifest.py`, `sandbox-kit/VENDORED-MANIFEST.md` | `tasks/briefs/pc/pc-k1-c.md` (PIN 236bec7) |
| S4H | #7 batch 2 — S0-04 checker: killing tests for four un-killed guards (or a declared equivalence) + a 2xx response-status assert; attested → re-mint by the coordinator | `proofs/S0-04/check_compression.py`, `tests/test_s0_04_compression.py` | `tasks/briefs/pc/pc-s4h.md` (PIN d92bfcf) |
| B7 | S0-02: the leg runner selects the S0-02 pinned env (`--env-set s0-02`), the test pin follows, the SEVEN owner-free legs captured against the isolated harness, the owner's revoked-leg command derived read-only | `proofs/S0-02/tools/pc/run_s0_02_legs.sh`, the test pin, `proofs/S0-02/evidence/**` | `tasks/briefs/pc/pc-b7.md` (PIN c439580) |

Every landing is graded by the coordinator (gates re-run, mutants re-run where cheap) and then gets a
targeted adversarial verify before it counts as verified; B6's verify is batched with B7's (same file).

## 6. NOT done, and honest limits

- **S0-02 is not minted.** Prerequisites: B7 (running); then the owner's one relay-membership removal
  command for the `revoked` leg (B7 derives it); then the eighth leg, the checker's verdict, the mint.
- **S0-05 is not minted and cannot be yet**: the live-unit legs need the production units deployed
  under the egress gate; on 2026-09-19 every unit read not-run (`proofs/S0-05/evidence/units.json`).
  The mechanism (selective egress via veth/iptables in a netns) is proven by the spike; containment
  over live units is unproven. This is design + owner work, not a lane.
- **S0-11's tag must be re-signed** by the owner (the same one-line pattern as S0-01, with
  `git tag -d accepted/S0-11` first and a force push of the tag; `docs/governance/README.md`).
  `tests/test_proof_status.py` shows `3 failed, 30 passed` until then — by design.
- **Reasoning effort on the vLLM route is the server default.** Lane reports label themselves
  "xhigh"/"medium"; that is the role's intent, not a measured fact — the per-role restart is skipped on
  the vLLM route (D-032). Recorded in the ledger wherever a verify round is cited.
- **A coordinator re-run of a lane's own gate is not independent verification.** It proves
  reproducibility of the same oracle. Wherever this report says "verified", a separate verify lane ran.
- **Open verify-followups**: #3 (closed by B6, verify pending), #4 (S0-06 named rc 78), #5 (S0-02
  execute-and-diff closure oracle — the durable rewrite), #6 (S0-03 two hardenings), #7 (S0-04: batch 1
  F2/F7 need a PC re-capture; batch 2 running), #8 (running as A5q), #9 (S0-01 cosmetic doubled prefix —
  touches the attested checker, so it waits for a batch that re-mints), #10 (S0-01 adjacency
  self-check + the V5 narrative).
- **STATUS.md** was refreshed only for the minted/accepted rows; other rows keep their older text.
  The wiki (`wiki/`) is not initialised; the ledger is the continuity source.
- **Nothing runs in production.** No component ships telemetry to the PC-side sinks yet; the
  application code is the governance core only.

## 7. Decisions and rules added in this window

- **D-035** (2026-09-21): the S0-01 golden is order-free for asynchronous session-metadata notifications
  only; what stays bound is enumerated; rejected alternatives recorded (`docs/08_DECISION_LOG.md`).
- **Owner ruling 2026-09-22**: up to four Hermes lanes in parallel on the vLLM route (CLAUDE.md
  §Environment; the measured basis in `PC-BRIDGE.md` §vLLM).
- **AF-AP-107** (the golden's async race), **AF-AP-108** (a remote `[ -f X ] &&` as the last statement),
  **AF-AP-109** (a control mutation is itself verified: same length, same multiset, different order,
  paired with a named production mutant) — `docs/INCIDENT-LOG.md`.
- **Orchestration skill rule 0g**: a discriminator VALUE a brief names is checked against the
  production filter at authoring (the `title`-is-volatile incident, caught twice by the lanes'
  premise checks) — `.claude/skills/orchestration/SKILL.md`.
- Process: a lane PIN is the POST-PUSH SHA (push_clean rewrites the range); long pollers are
  `setsid`; a PC-resident lane runs pytest directly (xdist), never the sandbox launcher.

## 8. How to review this efficiently

1. `git log --oneline 36b08ab..origin/claude/soundbox-kit-migration-iz1jwf` — every commit message is
   a reasoning record (what, why, rejected alternative, pasted gate lines).
2. The three S0-01 verify reports under `tasks/briefs/s0-01-vb-f12-support/` (VERIFY-VB-F12, G2,
   VERIFY-G2): each item carries the command and the exact output; `scripts/report_lint.py <report>`
   checks their file:line citations against the tree.
3. The lane briefs under `tasks/briefs/pc/` state boundary, gates and the blocking predicate; the
   harvested reports/patches/transcripts sit beside them (`report-pc-*.md`, `patch-pc-*.diff`,
   `transcripts/pc/`).
4. Governance: `python3 scripts/check-proof-status.py` and `docs/governance/README.md`.
5. If something here disagrees with the ledger, the ledger is right and this report is wrong.
