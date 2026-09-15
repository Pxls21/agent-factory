# A5o — S0-01 checker round 17: close VERIFY-A5n's two BLOCKERs

**Authorization.** Defensive hardening of the S0-01 ACP-conformance checker's META-TEST (the test that
pins the checker's classifier so it cannot be silently weakened) and its mutation driver. No live
ACP/Buzz/OmniRoute action. The production checker C is READ-ONLY and stays byte-identical.

**Ground (PIN `99ecb36`).** A5n (checker round 16) landed the module-wide classifier-operand inventory.
VERIFY-A5n (`tasks/briefs/s0-01-a5m-support/VERIFY-A5n-report.md` — READ IT WHOLE; its repros are your
acceptance targets) returned TWO BLOCKERs; V2 (labelled asserts) SOLID, the driver baseline 19/19
reproduced. Files:
- C = `proofs/S0-01/check_acp_conformance.py` (1906 lines, sha256 `7a13fbff…`) — READ-ONLY, must stay
  `git diff --quiet c728be5 -- C` = rc 0. A change to C is a finding, not a fix.
- T = `tests/test_s0_01_check_acp_conformance.py` (5770 lines, sha256 `396c13c8…`) — the meta-test.
- The A5n driver `tasks/briefs/s0-01-a5m-support/mutants.sh` (259 lines, sha256 `59becb2c…`) is your
  STARTING POINT; you write the A5o driver at `tasks/briefs/s0-01-a5o-support/mutants.sh`.

## Items (in order; each = code + a deterministic LLM-free control; attack through SCRATCH COPIES only)

1. **F1 [BLOCKER] the operand inventory is spelling-based, not binding-aware (T:2984-3041).**
   `_assert_ck16_classifier_operand_contract` builds each comparison's `operands` from raw
   `ast.unparse(node.left)` + `ast.unparse(comparator)` (T:3005-3008) and its BoolOp/membership set the
   same way (T:3036-3038), then intersects with the finite `classifier_operands` spellings
   (T:2984-2987). A classifier pin behind a LOCAL NAME (`x = PINNED_TEE_PATH; … == x`), a walrus
   (`(x := PINNED_TEE_PATH)`), or a helper returning a pin is therefore INVISIBLE — VERIFY-A5n proved
   three escapes (helper-direct, nested-helper, membership-alias), each deriving its compared value from
   `PINNED_TEE_PATH`/`PINNED_AGENT_REALPATH`.
   FIX: make the audit BINDING-AWARE. Within each function (and its nested scopes), resolve names/walrus
   targets whose value derives — directly or transitively — from a `classifier_operands` member (an
   `Assign`/`AnnAssign`/`NamedExpr` whose RHS unparse is a classifier operand, or references an
   already-resolved alias, or a return-value of a module helper that returns such), and treat those
   aliases as classifier operands when scanning Compare/BoolOp/membership nodes. Keep the existing
   `allowed_compares`/`allowed_predicates` inventories EXACT (T:2993-3024) — the fix widens detection,
   it does not relax the whitelist. TEST: three new controls, one per escape, each building a checker
   copy with the alias form and asserting the audit RAISES
   `"classifier-operand comparison inventory changed"` (mirror T:3068-3079's shape). Negative control:
   the binding-resolution removed → each alias form loads clean (red). The unrelated-comparison control
   (T:3057-3065, `env.get("X") == "1"`) MUST stay green — an alias to a NON-operand value is not pinned.

2. **F2 [BLOCKER, AF-AP-84 recurrence] the driver denominator is a fixed literal, not the set
   (D:12-13, D:127-131).** `TOTAL_ROWS=20` caps the loop by ORDINAL, so an appended `cases` row past 20
   is silently skipped and `EXPECTED=19` still passes (VERIFY-A5n: `extra_row_driver_rc=0`).
   FIX (in the A5o driver): derive the cardinality from `${#cases[@]}`; assert
   `${#cases[@]} == EXPECTED + CONTROL_ROWS` (destructive + the one CONTROL_COMMENT) BEFORE the loop, so
   an added row with an unchanged `EXPECTED` FAILS; make `--rows` bound to the derived cardinality, not
   the literal. Carry over A5n's INVALID gating (compile + collect + `ROW_TIMEOUT_S`, AF-AP-78), the
   `--self-test` (a deleted row → red) and `--timeout-control`. ADD a permanent `--added-row-control`:
   append a duplicate destructive row WITHOUT bumping `EXPECTED` and assert the driver EXITS NONZERO with
   a cardinality-mismatch message. Add the three F1 escape mutations (helper-direct, nested-helper,
   membership-alias — each a C mutation the binding-aware audit now kills) as new driver rows; bump
   `EXPECTED` to match the real destructive-row count.

## Gates (paste every line; counts pasted from output, never typed)

- `python3 -m py_compile T`, `pyflakes T`, `bash -n <a5o driver>`, `git diff --check` → rc 0 each.
- `git diff --quiet c728be5 -- proofs/S0-01/check_acp_conformance.py` → rc 0 (C untouched).
- The CK16 meta-tests pass, and the THREE new escape controls are RED without the binding fix and GREEN
  with it (paste each red-then-green). The unrelated-comparison control stays green.
- The A5o driver full run: `EXPECTED=<n> KILLED=<n> SURVIVED=0 INVALID=0 CONTROL=1` (n = the new
  destructive count); `--self-test` rc≠0 with the deleted-row summary; `--timeout-control` rc≠0 INVALID;
  `--added-row-control` rc≠0 with the cardinality-mismatch line. Paste each.
- **GATE VENUE (Finding 3): the checker file runs ~15 min serial — use `scripts/pc_suite.sh` xdist,
  NEVER `lane_gate.sh -n` (its `-n` is RUNS, not xdist).** Run the checker file's set on 8 workers via
  `pc_suite.sh launch -n 8 -- tests/test_s0_01_check_acp_conformance.py`, `wait <RUN_ID>`; paste the
  `pytest-set: … set=<sha12>` line beside the summary.
- `python3 scripts/ap_screen.py --s0-01 T` → rc 0 (no new class); `scripts/report_lint.py --min-refs 12`
  on the report (the `fix:` hints apply for at most three rounds, then paste and finish — AF-AP-76).

**Boundary.** T, the A5o driver `tasks/briefs/s0-01-a5o-support/mutants.sh`, and your report
`tasks/briefs/s0-01-a5o-support/A5o-report.md`. Nothing else; C is READ-ONLY. The class list
AF-AP-78/79/80/84/85/88 is your preflight (F2 is an AF-AP-84 recurrence — the report's "AF-AP-88"
label is stale, that number is the persisted-digest class). CODE INTEL FIRST: `graft ask` / `ripwire`
on T before editing; attach the pack. NOT for you: no change to C, no live ACP action, no commit, push,
or tag. Retro: name any new class for the coordinator; bake nothing yourself.
