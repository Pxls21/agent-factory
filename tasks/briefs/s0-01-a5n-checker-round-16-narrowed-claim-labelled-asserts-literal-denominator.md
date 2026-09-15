# Lane A5n — S0-01 checker round 16: VERIFY-CK15's two findings and its NOT-done closed — the exclusivity test's claim narrowed to what the lock inventories, labelled failure messages per structural check, the driver's LITERAL denominator with a self-test (AF-AP-84), a per-row timeout that reads INVALID instead of hanging the gate (build lane: PC Hermes `code-implementer`, the cloud build route; sandbox fallback `code-implementer`)

PIN: `A5N-PIN-PLACEHOLDER`

**Ground.** Round 15 (lane A5m) LANDED as d353f92 and was graded by VERIFY-CK15 (`tasks/briefs/s0-01-a5m-support/VERIFY-CK15-report.md`,
findings only): F1 MEDIUM — the brief's claim that "one legitimate-looking comparison anywhere in C must go red" is wider than the lock:
`allowed_compares` (`tests/test_s0_01_check_acp_conformance.py:2972`) inventories only comparisons whose operands intersect
`classifier_operands` (`T:2963`, `T:2983-2987`), so an unrelated `if env.get("X") == "1":` in `check_env` (C:442) stays green — the
process-classifier bypass class stays CLOSED; the claim, not the lock, is wrong. F2 LOW — the six F1 driver rows all collapse to one
`AssertionError: assert False` in `test_ck13_checker_has_no_private_pinned_process_predicate` (`T:2909-3016`): rejection is proven, the shape is
not named. NOT-done — the driver `tasks/briefs/s0-01-a5m-support/mutants.sh` has no per-row timeout (`D:116-120`): a hanging mutant blocks
the gate instead of reading INVALID. Plus the sweep finding AF-AP-84: `D:42`/`D:133`/`D:145` derive `expected` from the executed rows — a
deleted row lowers the denominator silently (VERIFY-N5l F3's class). SOLID and untouched: the lock itself (C:1195-1196 one Return, one
generator predicate; the CK14 alternate/conjunction/helper/hidden-classifier/lambda/`shlex.split`/`cmd.split(" ")`/`and True`/walrus/two-`for`
shapes all die), the citation validator, the TABLE_ROWS kill, the declaration semantics (empty corpus FAILS at collection; `S0_01_VENUE=ci`
skips five). The pack is `tasks/briefs/s0-01-a5m-support/VERIFY-CK15-pack.md` (START FROM IT).

**Boundary.** `tests/test_s0_01_check_acp_conformance.py` (T), `tasks/briefs/s0-01-a5m-support/mutants.sh` (D), your report
`tasks/briefs/s0-01-a5m-support/A5n-report.md`. `proofs/S0-01/check_acp_conformance.py` (C) is READ-ONLY this round (no production change is
needed; if an item forces one, STOP and say why). The class list of the S0-01 sweeps (AF-AP-78/80/81/82/84/85/86) is your preflight.

## Items (in order; every item = the change + a deterministic LLM-free test with its negative control + a pasted line)
1. **The claim narrowed to the lock (F1).** The docstring and name of the exclusivity test state exactly what the inventories cover: every
   comparison/membership/boolean whose operands intersect the CLASSIFIER's operands (process, argv, pinned paths), module-wide — not every
   comparison in C. Add ONE control that documents the boundary honestly: an unrelated `env.get("X") == "1"` comparison in a scratch copy
   stays green (a test that asserts the test's OWN scope: it runs the structural checks over a mutated copy and asserts no red — the
   boundary is declared, not discovered by a verifier again), and one that a comparison against a classifier operand added ANYWHERE in C
   goes red (the existing behavior, now pinned by a named test).
2. **Labelled failure messages (F2).** Every structural assertion in `test_ck13_checker_has_no_private_pinned_process_predicate` carries a
   message naming the shape it rejects (`"classifier body must be one Return, got N statements"`, `"BoolOp/Compare inside the classifier"`,
   `"a second shared-predicate user: <names>"`, …). Re-run the six F1 driver rows: each row's `E ` detail now names its shape — paste the six
   lines. A mutant killed through a generic `assert False` is a FINDING against this item.
3. **The literal denominator (AF-AP-84).** `EXPECTED=19` as a literal at the top of D (the 19 rows the report lists); the final gate
   `[[ $killed -eq $EXPECTED && $survived -eq 0 && $invalid -eq 0 && $control -eq 1 ]]`; the summary prints the literal. `--self-test`:
   copies D to scratch with one row line deleted and asserts the copy exits NON-zero with `EXPECTED=19 KILLED=18 …` — paste both outputs.
4. **The per-row timeout (the NOT-done).** Every row's pytest runs under `timeout <N>s` (N = 3× the checker file's measured serial time for
   ONE selected node, stated in the report); rc 124 is classified INVALID with a `TIMEOUT` line, never KILLED, never a hang. Control: a
   scratch row whose mutant makes the selected test sleep past N reads `INVALID … TIMEOUT` and the summary's INVALID gate fires (non-zero
   exit). Keep the AF-AP-78 rule: a row is KILLED only with a `FAILED …::<test>` node plus an `E ` detail.
5. **Gates.** The checker file with `-n 8` (never serial: ~4.5 min > the 420 s cap) twice → paste both counts + `pc_suite.sh set-id`; the
   driver's full output + the self-test + the timeout control; the 13-file set ONCE with `-n 8` (`1341 passed, 13 xfailed` at the PIN, set
   c62435272c99 — yours with its set id; +N for your new tests, xfails unchanged); pyflakes on T rc 0; `bash -n D`; `git diff --check`; the AP
   screen on T (no new hit class); report lint `--map C=proofs/S0-01/check_acp_conformance.py --map T=tests/test_s0_01_check_acp_conformance.py
   --map P=proofs/S0-01/pins.py --map D=tasks/briefs/s0-01-a5m-support/mutants.sh --min-refs 12`.

**Report.** `tasks/briefs/s0-01-a5m-support/A5n-report.md`: PROPOSAL line first; per item the pasted line and `file:line`; FILE IDENTITY (sha256 +
line count) for T/D before and after and C unchanged; the driver's outputs verbatim; a NOT-done list. No self-acceptance; no edits outside the boundary.
