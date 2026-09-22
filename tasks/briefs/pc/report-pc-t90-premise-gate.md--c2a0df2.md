All verified. Final state: gate present in worktree, test 19/0 (rc 0, `Tue Sep 22 08:59:45`), diff scope is exactly the two named files plus the new report. Report drafted (161 lines) and appended to the lane's draft.

---

**DONE (proposal — GATE RECOMMENDATION: MERGE-READY; no verdict, the adversarial-verifier lane grades it).** T90's dispatcher premise gate is built and self-validated. Resume note: attempt 1's report-draft was 0 bytes (died before drafting); its worktree edits were complete and correct — I re-verified every claim by run and made one conformance fix (see DISCREPANCY 2).

**DATA — item 1 (premise, re-measured at c2a0df2)**
- `scripts/pc_lane.sh` sha256 `d5b895574e357727`, 368 lines, last change `ea32017 2026-09-17` — **cryptographic match** to the brief's premise (file byte-identical).
- `test_pc_lane_dispatcher.sh` `84f89b515fd3dec4`, 74 lines, `650b33b 2026-09-15`; `run-all.sh` `d12c3e49e4f859ca` — both match.
- Fresh PIN copy run: `pc_lane dispatcher: 13 passed, 0 failed`, rc 0 (pre-change baseline confirmed).
- **DISCREPANCY 1 (measured, bounded):** the brief's *line-number annotations* for the middle band are off by one (it says `bridge()` hook :125, `LANE_PRINT_EFFORT` exit :150, headroom :152; the bytes say :126, :149, :151 — while the 172+ ship region matches exactly). sha256 match proves the file is unchanged → authoring annotation drift, not a changed file. The contract's insertion point is anchored to two stable code anchors (after the `LANE_PRINT_EFFORT` exit, before the headroom block) — satisfied on the measured truth. Anti-pattern class: **line numbers drift; the hash is the ground truth** (echo candidate for the registry).

**DATA — item 2 (the gate)**
- Worktree `scripts/pc_lane.sh:161-191` (31 new lines, no c2a0df2 revision — span in words): header `# --- 0a. premise gate ---` (:161) · `_premise_block_ok` awk state machine (:169-178; heading `^#{1,6} .*premise.*measured` case-insensitive, then a fence opened/closed by a line that is exactly three backticks holding ≥2 non-empty lines) · resume probe `test -f $PC_AF_REPO/.lanes/$LANE_ID/lane.pid && echo RESUME || echo FIRST` with `2>/dev/null || true` fail-closed (:186) · RESUME → stderr note `pc_lane: premise gate skipped — a resume of $LANE_ID` (:187-188) · else no-block → `die` rc 64 with the contract's exact one-line text, verified byte-for-byte (:189-190). No env escape hatch; no `mkdir -p` before the die (AF-AP-79).
- `bash -n` clean; shellcheck not installed (advisory skipped).

**DATA — item 3 (tests)**
- `test_pc_lane_dispatcher.sh`: fixture `T:8` updated to the WITH-block form (`### premise — measured`, two-line fence); 4 new fixtures (no-block / empty-fence / one-line-fence / heading-missing-`measured`) · fake-bridge `case` arm `*'lane.pid && echo RESUME'*) echo "${PC_LANE_TEST_RESUME:-FIRST}"` (worktree T:44) · new `run_gate` runner (T:72-81) · 6 new checks (T:99-128) covering (a) FIRST+no-block → rc 64, stderr `no MEASURED premise block`, NO `mkdir -p` · (b) same brief + `PC_LANE_TEST_RESUME=RESUME` → rc 75, skip note, `mkdir -p` IS recorded · (c) empty fence → rc 64 · (c') one-line fence → rc 64 · (d) `###` lowercase heading + 2-line block → rc 75 + ships · (e) heading with `premise` but no `measured` → rc 64.
- `bash harness-ports/tests/test_pc_lane_dispatcher.sh`: **19 passed, 0 failed**, rc 0 — run 1 `Tue Sep 22 08:38:38 AM UTC 2026`, runs 2–3 (determinism) `08:38:57` / `08:41:52`, final `08:59:45`. The 9 effort-seam checks unchanged (item 6f); the 4 existing dispatch checks now run on the with-block fixture (item 6d).
- `bash harness-ports/tests/run-all.sh` (one foreground call): final line **`ALL SUITES PASSED`**, rc 0, `Tue Sep 22 08:43:10 AM UTC 2026` (includes `test_pc_lane.sh` 53/0, `test_pc_lane_admission.sh` 22/0, `test_qwen_server.sh` 101/0).

**DATA — item 4 (mutant)**
- Scratch copy with the gate deleted (31 lines), `bash -n` clean, test run against it: **`pc_lane dispatcher: 14 passed, 5 failed`**, rc 1, `Tue Sep 22 08:41:38`. FAIL lines: no-block-FIRST · no-block-RESUME · empty-fence · one-line-fence · missing-`measured`. Mechanism: without the gate a no-block FIRST brief falls through headroom (fail-open) → `mkdir -p` ship → launch (rc 75), so (a) is green-for-the-wrong-reason on the mutant — the gate is load-bearing, not a tautology. The 9 effort + 4 dispatch + 1 positive checks pass on the mutant (they don't depend on it). Restored; re-run 19/0.

**DATA — item 5 (report)**
- `tasks/briefs/pc-t90-support/T90-report.md` (dir created) — full report; also appended to the lane draft `report-draft.md`.
- `report_lint.py … --map D=scripts/pc_lane.sh --map T=harness-ports/tests/test_pc_lane_dispatcher.sh --rev c2a0df2`: round 1 = 19 MISS (root cause: cited worktree line numbers as c2a0df2 `D:NN` — new lines don't exist at the PIN — plus claim tokens on prose lines) → round 2 = 1 MISS (one test-file ref aliased to the dispatcher) → round 3 (final): **`report_lint: 9 refs — OK 6, NEAR 0, MISS 0, UNCHECKABLE 3, UNRESOLVED 0 (at c2a0df2)`, rc 0**. The 3 UNCHECKABLE rows are aliases on token-less prose summary lines — reported, not chased (AF-AP-76).

**DISCREPANCY 2 (fix applied):** attempt 1's gate header was `# --- 0a. premise gate (T90, 2026-09-22) ---` (decoration + dash-fill); contract item 2 specifies the exact `# --- 0a. premise gate ---`. Conformed this session; re-verified 19/0.

**NOT done:** no gate verdict (build lane); `harness-ports/bin/pc-lane.sh` (PC side), the poll/harvest sections, CLAUDE.md/AGENTS.md/.hermes.md, and the four named briefs are all untouched per item 7 — the mirror rule is the coordinator's at harvest.

**Self-attack (3 ways this is wrong, each ruled out):** (1) tautology — ruled out by the mutant (5 red); (2) grammar accepts/rejects wrong — ruled out by the 5-fixture matrix covering every contract branch; (3) resume exemption too loose/tight — ruled out by the fail-closed probe (only literal `RESUME` from the on-PC pidfile exempts) plus checks (a)/(b).

**Retro:** echo candidate = DISCREPANCY 1's class (drifted line annotations in a brief whose own hash proves the file unchanged; hash first, annotations second). No other lessons.
