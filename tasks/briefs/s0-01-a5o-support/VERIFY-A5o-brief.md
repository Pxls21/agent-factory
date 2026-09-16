# VERIFY-A5o — adversarial verification of S0-01 checker round 17 (A5o) as LANDED

**Authorization.** Defensive verification of the S0-01 ACP-conformance checker's META-TEST (the test
that pins the checker's classifier so it cannot be silently weakened) and its mutation driver. No
live ACP/Buzz/OmniRoute action. The production checker C is READ-ONLY and stays byte-identical.

**Single-model rule.** You run on the cloud verify route grading a cloud-built lane. Report FINDINGS
only, ranked, with a repro for each. NO merge verdict. Report everything; do not severity-filter.

**Ground (LANDED at the PIN `45e7bf6`; A5o = commit c4d3af4).** A5o closed VERIFY-A5n's two BLOCKERs.
Files: C = `proofs/S0-01/check_acp_conformance.py` (1906 lines, sha `7a13fbff…`, READ-ONLY, must stay
`git diff --quiet c728be5 -- C` = rc 0); T = `tests/test_s0_01_check_acp_conformance.py` (5894 lines,
sha `a27f6857…`); D = `tasks/briefs/s0-01-a5o-support/mutants.sh` (300 lines, sha `990f5e8b…`). The
coordinator gate reproduced: the full-file xdist run `424 passed, 13 xfailed` (set 31306c49985e);
the three escape rows KILLED (`ROWS=18-20 SELECTED=3 KILLED=3`). The two fixes (attack PAST them):
- **F1** the CK16 operand inventory `_assert_ck16_classifier_operand_contract` is now BINDING-AWARE:
  it resolves `Assign`/`AnnAssign`/`NamedExpr` aliases + transitive aliases + module/nested helper
  returns derived from the finite operand set, then applies resolved operands to the comparison
  (T:3060/3074) and BoolOp/membership (T:3091/3113) inventories; the whitelists stay EXACT.
- **F2** the driver derives `TOTAL_ROWS` from `${#cases[@]}` and asserts `total == EXPECTED +
  CONTROL_ROWS` before iteration (D:146-148); `--added-row-control` and `--self-test` fail on exact
  cardinality mismatch.

## Items (V1-V8; every claim gets an independent repro through a SCRATCH COPY; never git-restore the tree)

1. **V1 the binding resolution does not OVER-match.** A checker copy with a name bound to a NON-operand
   value (`x = "literal"; … == x`), or an alias to a pin that is then re-bound to a non-operand before
   the compare, must NOT be flagged (no false `inventory changed`). Confirm the unrelated-comparison
   control (T:3133) holds and construct one new over-match probe; a false positive is a finding.
2. **V2 the binding resolution does not UNDER-match — attack alias depth and scope.** Build checker
   copies that reach a classifier operand through: a transitive chain DEEPER than A5o's fixtures
   (a=pin; b=a; c=b; d=c; … == d); a container hop (`t = (PINNED_TEE_PATH,); … == t[0]`); an aug-assign
   or a walrus nested in a comprehension/genexp/lambda scope; a helper whose return derives from the
   operand via a parameter default; attribute/subscript access. For each: does the audit still RAISE,
   or does the operand escape? Each escape is a BLOCKER-class finding (the same class VERIFY-A5n found).
3. **V3 the three committed escape controls are non-vacuous.** `test_ck17_*` (helper-alias, nested-walrus,
   membership-alias): reproduce RED-before (remove the binding resolution) and GREEN-after; confirm each
   asserts the EXACT `inventory changed` message, not a bare `DID NOT RAISE`.
4. **V4 the driver denominator is set-bound (AF-AP-84 closed) and INVALID-gated (AF-AP-78).** Append a
   row without bumping `EXPECTED` → cardinality mismatch, nonzero. Delete a row → `--self-test` red.
   `--rows` out of range → rc 64. A mutant that does NOT compile / does NOT collect → INVALID, not
   KILLED. `--timeout-control` → INVALID. Re-run the full campaign; paste `EXPECTED=… KILLED=…`.
5. **V5 the three F1 escape driver rows kill through the REAL meta-test.** Rows 18-20 each change C,
   compile, collect `test_ck16_checker_inventories_classifier_operand_predicates_module_wide`, and die
   with the exact inventory-changed message — not through a SyntaxError or a different test.
6. **V6 C is byte-identical.** `git diff --quiet c728be5 -- C` rc 0 before and after every attack.
7. **V7 identities + the outer gate.** Recompute sha256 + line count of T/D/C against the ground above.
   Re-run the full checker file via `scripts/pc_suite.sh launch -n 8 -- tests/test_s0_01_check_acp_conformance.py`
   then `wait` (you MAY use pc_suite from this PC verify lane per the owner carve-out); paste the
   `424 passed …` summary + the `set=` id. `python3 -m py_compile T`, `pyflakes T`, `bash -n D`,
   `git diff --check` → rc 0. `python3 scripts/ap_screen.py --s0-01 T` → rc 0.
8. **V8 report.** Rank findings BLOCKER/SHOULD-FIX/NIT with a one-line repro each; a NOT-DONE list;
   `scripts/report_lint.py --min-refs 12` on the report; the three file identities. No verdict.

**Boundary.** T, D (READ-ONLY — copy into `../scratch` for any hostile edit, never the tracked files),
your report `tasks/briefs/s0-01-a5o-support/VERIFY-A5o-report.md`. C is READ-ONLY. The class list
AF-AP-78/80/84/85 is your preflight. CODE INTEL FIRST: `graft ask` / `ripwire` on T before grep;
attach the pack. The report lint's `fix:` hints apply for at most three rounds, then paste and finish.
Retro: name any new class for the coordinator; bake nothing yourself.
