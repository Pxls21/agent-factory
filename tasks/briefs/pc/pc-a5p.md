# PC lane — A5p (S0-01 checker round 18, THE DECLARED-FINAL round: close VERIFY-A5o's V1)

PIN: 798ce74

Role: code-implementer. Route: the LOCAL Qwen build route (`agentfactory-build-local`, medium —
the pc_lane.sh default for code-implementer; do NOT set HERMES_MODEL). Venue:
`tasks/briefs/pc/VENUE-MAP.md` — read it first.

**The brief governs**: `tasks/briefs/s0-01-a5o-support/VERIFY-A5o-report.md` — READ IT WHOLE. Close
its ONE blocker (V1) and its SHOULD-FIX (V2). Your worktree IS `git archive 798ce74` plus the lane
patch (this brief). Save your report at `tasks/briefs/s0-01-a5p-support/A5p-report.md`, draft after
EACH item, return it whole as your final message.

**THIS IS THE FINAL S0-01 CHECKER ROUND (owner ruling D-034).** After A5p lands green the checker is
declared GOOD-STATE and its tools FREEZE for the coordinator's VB-F12 re-capture. Any classifier-
operand bypass still surviving after this round is a `verify-followup` GitHub issue, NOT a round 19.
Do not open new fronts; close V1's named cases and stop.

## The blocker and its FROZEN red control
- **V1 — the CK16 classifier-operand contract (`_assert_ck16_classifier_operand_contract`,
  `T:3012-3050`) is bypassable.** It over-matches a REASSIGNED local (accumulates an alias once
  derived, never kills it after a later assignment) and under-matches ordinary data-flow forms
  (container/subscript, augmented assignment, lambda/default, attribute, module-scope). The
  verifier's hostile repro `../scratch/test_ck17_hostile.py` gets `7 failed, 1 passed`:
  `pin = PINNED_TEE_PATH; pin = 'literal'; return value == pin` FALSELY raises; `(PINNED_TEE_PATH,)[0]`,
  `pin += PINNED_TEE_PATH`, lambda/default, attribute, and module-alias-chain copies each `DID NOT
  RAISE`.
- **Preferred fix (D-034 — do NOT build an unbounded static-analysis engine): STATE THE HONEST
  DOMAIN.** If the contract deliberately covers a smaller domain, narrow the claim: stop calling it
  a module-wide inventory, name the exact expression classes it DOES cover, add a scope-correct
  rebind-negative control (a re-assigned alias must NOT falsely raise), and let the un-covered exotic
  forms be a stated, documented limit. Only add supported expression classes where they are cheap and
  the red control is exact. The bar is: an HONEST contract whose claim matches its coverage, with the
  rebind false-positive fixed — not a contract that chases every dataflow form (that is the treadmill
  D-034 stops).
- **Red control (AF-AP-36):** the hostile mutations become COMMITTED regression tests — the
  false-positive rebind case goes green (no false raise) and each case whose form you now claim to
  cover reds on a real bypass. State in the report which forms are covered vs stated-as-limit.
- **V2 — SHOULD-FIX:** add committed regressions for the chosen domain, including the rebind-negative
  test. (The three permanent CK17 controls at `T:3158-3203` are green but do not pin the boundary.)

## Boundary (touch ONLY these)
- `tests/test_s0_01_check_acp_conformance.py` (the meta-test T — V1/V2 live here) and the A5o mutant
  driver.
- The production checker `proofs/S0-01/check_acp_conformance.py` (C) MUST stay BYTE-IDENTICAL to the
  PIN (`git diff --quiet 798ce74 -- proofs/S0-01/check_acp_conformance.py` = rc 0) — a change to C is
  a FINDING, not a fix. `proofs/S0-01/pins.py` unchanged. Report adjacent defects, never fix them.

## Gate (a script, not a paragraph)
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; `S0_01_VENUE=pc
  S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden` exported before every gate run; an
  absolute SHORT `--basetemp` and an absolute short `A5M_MUTANT_DIR` under your lane's `../scratch`
  (a RELATIVE mutant dir turns TABLE_ROWS INVALID — VERIFY-A5n discrepancy).
- Hermes's `terminal` tool caps ONE call at 420 s and the checker runs ~15 min SERIAL, so the pytest
  gate MUST be `scripts/pc_suite.sh launch -n 8 -- tests/test_s0_01_check_acp_conformance.py` then
  `wait <RUN_ID>` (xdist ~2-3 min) — NEVER `lane_gate.sh -n` (its `-n` is RUNS). The mutant driver's
  rows each run under `ROW_TIMEOUT_S`; run the driver detached if the sweep would exceed the cap and
  read its log. Paste the `pytest-summary:` + `pytest-set:` lines and the driver's
  EXPECTED/KILLED/SURVIVED/INVALID/CONTROL line verbatim.
- Attack through SCRATCH COPIES only — never git-restore/stash/checkout the shared tree. CODE INTEL
  FIRST: `graft ask` / `ripwire` on T before grep; the pack is built at launch. `report_lint` gates
  on a FLOOR; apply its `fix:` hints for at most THREE rounds, then paste and finish.
- Other lanes run on this host in their own trees — never touch their files, the model server, or any
  unit.
