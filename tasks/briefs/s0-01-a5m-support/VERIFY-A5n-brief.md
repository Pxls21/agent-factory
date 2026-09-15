# VERIFY-A5n — adversarial verification of S0-01 checker round 16 (A5n) as LANDED

**Authorization.** Defensive verification of the owner's own S0-01 ACP-conformance checker. Attack
the TEST and the DRIVER, not to weaken them — to prove they cannot pass a broken checker.

**Single-model rule.** You run on the cloud verify route grading a cloud-built lane. Report FINDINGS
only, ranked, with a repro for each. NO merge verdict. Report everything; do not severity-filter.

**Ground (LANDED at the PIN `c728be5`).** A5n (checker round 16) closed VERIFY-CK15's three findings
at the TEST/DRIVER layer with the production checker `proofs/S0-01/check_acp_conformance.py` (C)
BYTE-IDENTICAL to round 15 (sha256 `7a13fbff…`, 1906 lines; `git diff --quiet c41aab6 -- C` = rc 0).
The fixes in `tests/test_s0_01_check_acp_conformance.py` (T) and the mutant driver
`tasks/briefs/s0-01-a5m-support/mutants.sh` (D):
- **F1** the classifier-operand claim, narrowed from "every comparison in C is forbidden" to a
  module-wide inventory over the finite operand domain (`_assert_ck16_classifier_operand_contract`
  T:2909, `classifier_operands` T:2984, the inventory test T:3044) with paired scratch controls
  (T:3057 an UNRELATED comparison stays green; T:3068 a pinned-path comparison is rejected).
- **F2** every structural assertion carries a labelled message with a red-before control
  (T:2917-2960, 2971, 2981, 3009, 3039).
- **F3 / AF-AP-84** a literal `EXPECTED=19` (D:12) with a deleted-row self-test, and a per-row
  `ROW_TIMEOUT_S=4` (D:14) turning a hang into INVALID.

## Items (V1-V8; every claim gets an independent repro through a scratch checker copy)

1. **V1 attack the narrowed F1 claim.** Is the module-wide operand inventory COMPLETE, or can a
   real classifier-operand comparison in a NEW location (a helper, a nested function, a different
   syntactic form — membership, a chained compare, a walrus) escape it? Plant a pinned-path
   comparison in a scratch checker at several sites; each must be REJECTED (reproduce the T:3068
   contract). Plant an unrelated comparison (e.g. `env.get("X") == "1"`); it must stay GREEN (T:3057).
   Confirm the inventory names the ACTUAL operand domain, not a subset that lets a real predicate
   slip.
2. **V2 attack the labelled asserts (F2).** Can a generic `AssertionError: assert False` from an
   unrelated failure still pass for a real structural kill? Confirm each structural assertion carries
   a distinct labelled message AND has a red-before control that fails for the exact expected reason.
   Try mutating one structural target so a DIFFERENT assertion fires — is it distinguishable?
3. **V3 attack the denominator (F3/AF-AP-84).** Is `EXPECTED=19` truly a literal independent of the
   observed rows? Lower it to 18 in a scratch copy — does `--self-test` catch it? Add a row without
   bumping EXPECTED — INVALID or SURVIVED? Delete a row — does the self-test report the mismatch?
4. **V4 attack the per-row timeout (F3).** Does `ROW_TIMEOUT_S=4` (D:14) turn a genuinely hung row
   into INVALID (not a silent pass or a SURVIVED)? Insert a row whose test sleeps > 4 s in a scratch
   driver copy; confirm INVALID and the driver's non-zero disposition. Confirm a fast row is
   unaffected.
5. **V5 the driver is valid (AF-AP-78).** Every mutant row compiles and collects before its test
   runs; INVALID is gated; no row "kills" through a SyntaxError. Re-run the driver + `--self-test`;
   paste `EXPECTED=19 KILLED=19 SURVIVED=0 INVALID=0 CONTROL=1` and the self-test wrapper rc.
6. **V6 C is unchanged.** `git diff --quiet c728be5 -- proofs/S0-01/check_acp_conformance.py;
   echo rc=$?` → rc 0. Recompute sha256 + line count of C (must equal `7a13fbff…`/1906), T, D.
7. **V7 the gate.** `scripts/lane_gate.sh -r c728be5 -f "tests/test_s0_01_check_acp_conformance.py
   tasks/briefs/s0-01-a5m-support/mutants.sh" -t "tests/test_s0_01_check_acp_conformance.py" -n 8`
   (the checker file runs ~15 min serial and hits the 420 s terminal cap — use `-n 8` xdist, ONE
   foreground call). Paste the RESULT line and the pytest-set id. Re-run the driver + self-test.
8. **V8 the AP screen + report.** `python3 scripts/ap_screen.py --s0-01
   tests/test_s0_01_check_acp_conformance.py` — classify every hit; any NEW class is a finding. Rank
   findings BLOCKER/SHOULD-FIX/NIT with a one-line repro each; a NOT-DONE list; `scripts/report_lint.py`
   with the C=/T=/D= maps; end with the file identities. No verdict (single-model rule).

**Boundary.** `tests/test_s0_01_check_acp_conformance.py` (T), `tasks/briefs/s0-01-a5m-support/mutants.sh`
(D), `proofs/S0-01/check_acp_conformance.py` (C, READ-ONLY — scratch copy for any hostile edit), your
report `tasks/briefs/s0-01-a5m-support/VERIFY-A5n-report.md`. The S0-01 sweep class list
AF-AP-78/80/81/82/84/85/87 is your preflight. CODE INTEL FIRST: `graft ask` / `ripwire` before grep.
Retro: name any new class for the coordinator; bake nothing yourself.
