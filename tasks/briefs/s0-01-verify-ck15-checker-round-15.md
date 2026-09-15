# VERIFY-CK15 — adversarial verification of S0-01 checker round 15 as LANDED (lane A5m, in the PIN): the exact-shape exclusivity lock on `_pinned_process_count`, the module-wide comparison/predicate inventories, the compile-and-collect driver with a real-assertion kill rule — graded against VERIFY-CK14's F1/F2 and the checker CONTRACT, never against the builder's own cases (verify lane: PC Hermes `adversarial-verifier`; on the CLOUD verify route the SINGLE-MODEL RULE applies — findings, no verdict; on the LOCAL route a verdict is allowed)

PIN: `bf8a5dc`

**What you grade.** `proofs/S0-01/check_acp_conformance.py` (C, 1906 lines at the PIN), `tests/test_s0_01_check_acp_conformance.py`
(T, 5707 lines), `proofs/S0-01/pins.py` (P, 629 lines, unchanged and read-only), the driver `tasks/briefs/s0-01-a5m-support/mutants.sh`
(D, 154 lines), the builder's report `tasks/briefs/s0-01-a5m-support/A5m-report.md` (its lint on the landing: `26 refs — OK 24, NEAR 2`),
the pack `tasks/briefs/s0-01-a5m-support/VERIFY-CK15-pack.md` (START FROM IT), and the predecessor verdict
`tasks/briefs/s0-01-a5l-support/VERIFY-CK14-report.md` (F1: the ONE-predicate pin was a PRESENCE check — a second local predicate consulted
BEFORE the shared call survived `7 passed, 425 deselected`; F2: A5l's TABLE_ROWS row was a SyntaxError kill, AF-AP-78). The corpus is a
DECLARED input (`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`, read-only; it has NO `run-2` leg — the
determinism check cannot pass by construction until VB-F12's re-capture; that is KNOWN, not a finding). Counts carry their set id: the
coordinator's sandbox gate on the checker file and the driver `EXPECTED=19 KILLED=19 SURVIVED=0 INVALID=0 CONTROL=1`; the lane's PC
`419 passed, 13 xfailed` ×2 (set 31306c49985e), 4-file `656 passed, 13 xfailed`, 13-file `1341 passed, 13 xfailed` (c62435272c99, = the floor).

## Items (every item = a reproduced probe with its exact command, output and file:line)
- **V1 — F1 closed as EXCLUSIVITY, not presence.** `test_ck13_checker_has_no_private_pinned_process_predicate` (`T:2910-3016`): reproduce the
  CK14 survivor exactly (`_is_pinned_process_alt` consulted before the shared call) → red? Then the shapes the lock claims to reject
  (`T:2941` BoolOp/Compare in the classifier; `T:2958` `_is_pinned_process*` names; `T:2959` `pinned_argv` helpers outside the classifier;
  `T:3016` new classifier-like comparisons elsewhere): one scratch mutant each, the exact assertion each dies on. Then the attacks the lock may
  NOT see: a second classifier that never mentions `pinned`, `argv` or `process` in its name and compares `cmd.split()[0]` to a path constant;
  a predicate hidden in a lambda passed to `filter`; a `pins.is_pinned_argv` call whose argument is NOT `cmd.split()` (`shlex.split(cmd)`,
  `cmd.split(" ")`); a classifier that returns `sum(1 for cmd in cmds if pins.is_pinned_argv(cmd.split()) and True)`; a `walrus`; a
  comprehension with two `for` clauses. For each: red or survived — a survivor is a finding with severity.
- **V2 — the inventories fail CLOSED and are not a mirror.** `allowed_compares` (`T:2972`) and `allowed_predicates` (`T:2992`) are finite
  baselines of C's legitimate comparisons/memberships: are they DERIVED from C (a mirror) or WRITTEN as an oracle? Add one legitimate-looking
  comparison to C (e.g. `if env.get("X") == "1":` in an unrelated function): the test must go red (fail closed) — reproduce; then confirm the
  inventory's entries are each a real, reachable line in C today (no stale entry silently allowed).
- **V3 — the classifier's body pin.** `len(classifier.body) == 1` (`T:2918`) and `ast.Return`/`GeneratorExp`/one `comprehension.ifs`: the lane
  removed the docstring to satisfy the one-statement rule — is a docstring now FORBIDDEN in the classifier (a `# comment` allowed, a
  docstring red)? State whether the rule is the right shape; attack with `return int(sum(...))`, `return sum((...))`, a `yield`.
- **V4 — the dead-branch citation drift.** The lane's docstring removal shifted two self-referential citations by one line and the citation
  validator caught it (`test_ck11_dead_branch_comments_cite_a_real_guard`). Reproduce: shift the `raise Failure` guard by one line in a scratch
  copy → the validator red; confirm C's two comments cite the range ending on line 1565 today (`C:1565`) and that the validator reads the
  GUARD, not the comment (a comment that names a range with no guard in it must be red).
- **V5 — the driver (AF-AP-78) with the assertion-detail kill rule.** `D:117-152`: a kill needs both a `FAILED …::<test>` node and an `E `
  detail line. Attack: a mutant that makes the test ERROR at setup (a fixture exception) prints `ERROR` not `FAILED` — counted how? A mutant
  that hangs — is there a timeout row? A mutant whose kill is a `SystemExit` in collection — INVALID or KILLED? Add a probe row for each and
  paste the driver's classification; then rerun the 19 rows and paste `EXPECTED/KILLED/SURVIVED/INVALID/CONTROL`.
- **V6 — the TABLE_ROWS row is now a VALID kill.** `_SCAN_HEADER_RE` `table_rows=(\d+)` → `rows=(\d+)`, killed by
  `test_v24_table_rows_key_cannot_be_replaced_by_rows` with `DID NOT RAISE Failure`: reproduce; then check the key is anchored (a header line
  carrying BOTH `table_rows=` and `rows=` — which wins; a `\btable_rows=` vs `xtable_rows=`).
- **V7 — the F1 mutants' independence.** The six F1 rows all die in the SAME test; is that test one assertion or six? If one `assert False`
  (`T:2941`?) catches everything, the test cannot say WHICH shape it saw — a diagnostic gap, not a hollow green; grade it as such.
- **V8 — the real-leg suite under the declared corpus.** The checker file with the PC corpus: paste the count + set id; with an EMPTY corpus
  dir: the real-producer tests FAIL (paste `N failed`); with `S0_01_VENUE` unset: SKIP by declaration (paste `N skipped`); the `run-2`
  absence: name the exact test(s) that xfail/fail because of it and confirm they are the 13 xfails the count carries, not silent passes.
- **V9 — the report.** Re-verify the FILE IDENTITY table (C/T/D after; P unchanged) against the PIN; `report_lint.py --map C=… --map T=… --map
  P=proofs/S0-01/pins.py --map D=… --min-refs 12`; grade every VERIFIED claim you can reproduce in ≤ 5 min; UNSURE for the rest, never false.

**Output.** `tasks/briefs/s0-01-a5m-support/VERIFY-CK15-report.md`: on the cloud route line 1 `NO VERDICT (single-model rule): findings only`;
on the local route a verdict line (`MERGE-READY` / `NOT-READY: <ids>`); then FINDINGS ranked by severity with the fix shape; per item
SOLID/UNSURE with the command, the output and `file:line` (`C=`, `T=`, `P=`, `D=`; declare the map at the top); a NOT-done list. Report lint
with your map, `--min-refs 15`, the bounded rule (three rounds, then paste and finish). No edits to the landed bytes (scratch mutants only).
