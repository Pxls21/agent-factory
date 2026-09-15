PROPOSAL — A5o build-lane evidence only. Independent sandbox adversarial verification has not run.

## Item 1 — binding-aware CK16 classifier-operand inventory

DONE: the CK16 meta-test now resolves `Assign`, `AnnAssign`, and `NamedExpr` aliases, including transitive aliases and calls to module or nested helpers whose returns derive from the finite classifier-operand set. The exact `allowed_compares` and `allowed_predicates` inventories remain unchanged.

Premise reproduced on a scratch copy before the fix:

```text
FAILED ...::test_ck17_classifier_operand_helper_alias_is_rejected - Failed: DID NOT RAISE AssertionError
FAILED ...::test_ck17_classifier_operand_nested_walrus_alias_is_rejected - Failed: DID NOT RAISE AssertionError
FAILED ...::test_ck17_classifier_operand_membership_alias_is_rejected - Failed: DID NOT RAISE AssertionError
3 failed, 434 deselected in 1.57s
red_alias_controls_rc=1
```

Binding-resolution-removed negative control:

```text
FAILED ...::test_ck17_classifier_operand_helper_alias_is_rejected - Failed: DID NOT RAISE AssertionError
FAILED ...::test_ck17_classifier_operand_nested_walrus_alias_is_rejected - Failed: DID NOT RAISE AssertionError
FAILED ...::test_ck17_classifier_operand_membership_alias_is_rejected - Failed: DID NOT RAISE AssertionError
3 failed, 434 deselected in 1.58s
binding_resolution_removed_clean_rc=1
```

Green after the fix, including the unrelated-comparison control:

```text
......                                                                   [100%]
6 passed, 431 deselected in 1.40s
```

Evidence:
- `T:2989` `assignment_binding` and `T:3039` `function_operand_aliases` compute binding/helper derivation to a fixed point.
- `T:3060` `allowed_compares` stays exact, while `T:3074` `derived` applies resolved operands to comparison inventory.
- `T:3091` `allowed_predicates` stays exact, while `T:3113` `operand_derivation` applies the same resolution.
- `T:3133` `test_ck16_unrelated_comparison_is_outside_classifier_operand_contract` proves a non-operand comparison stays outside the inventory.
- `T:3158` `test_ck17_classifier_operand_helper_alias_is_rejected`, `T:3175` `test_ck17_classifier_operand_nested_walrus_alias_is_rejected`, and `T:3191` `test_ck17_classifier_operand_membership_alias_is_rejected` supply the permanent controls.
- Context pack: `../scratch/A5o-context-pack.md`.

## Item 2 — set-derived mutation-driver denominator

DONE: the A5o driver derives `TOTAL_ROWS` from `${#cases[@]}`, checks it against `EXPECTED + CONTROL_ROWS` before iteration, and validates `--rows` against that derived total. It retains compile, collect, per-row timeout, deleted-row self-test, and timeout control. It adds an appended-row control and the three F1 destructive rows.

Premise reproduced against the A5n driver:

```text
EXPECTED=19 KILLED=19 SURVIVED=0 INVALID=0 CONTROL=1
extra_row_driver_rc=0
```

Permanent cardinality controls:

```text
SELF_TEST rc=1 CARDINALITY_MISMATCH rows=22 expected=23 destructive=22 control=1
self_test_wrapper_rc=0
ADDED_ROW_CONTROL rc=1 CARDINALITY_MISMATCH rows=24 expected=23 destructive=22 control=1
added_row_wrapper_rc=0
TIMEOUT_CONTROL rc=1 INVALID F1_SECOND_IF TIMEOUT after=4s | EXPECTED=22 KILLED=21 SURVIVED=0 INVALID=1 CONTROL=1
timeout_wrapper_rc=0
```

Derived range control:

```text
invalid row range: 1-24 (total=23)
range_rc=64
```

The three new mutation rows each compile, collect, and die through the module-wide meta-test:

```text
KILLED F1_HELPER_DIRECT | FAILED ...::test_ck16_checker_inventories_classifier_operand_predicates_module_wide | E       AssertionError: classifier-operand comparison inventory changed: [('_alias_classifier', 'value == pin')]
KILLED F1_NESTED_HELPER | FAILED ...::test_ck16_checker_inventories_classifier_operand_predicates_module_wide | E       AssertionError: classifier-operand comparison inventory changed: [('_outer_classifier_alias', 'value == (pin := PINNED_AGENT_REALPATH)'), ('nested', 'value == (pin := PINNED_AGENT_REALPATH)')]
KILLED F1_MEMBERSHIP_ALIAS | FAILED ...::test_ck16_checker_inventories_classifier_operand_predicates_module_wide | E       AssertionError: classifier-operand BoolOp/membership inventory changed: [('_membership_classifier', 'pin in values')]
ROWS=18-20 SELECTED=3 KILLED=3 SURVIVED=0 INVALID=0 CONTROL=0
driver_new_rows_rc=0
```

Full driver:

```text
EXPECTED=22 KILLED=22 SURVIVED=0 INVALID=0 CONTROL=1
driver_full_rc=0
```

Evidence:
- `D:12` `EXPECTED=22` declares the destructive denominator; `D:13` `CONTROL_ROWS=1` declares the control.
- `D:22` `--self-test` and `D:50` `--added-row-control` make deleted and appended rows fail on exact cardinality mismatch.
- `D:108` `--rows` parses a range without a fixed cap.
- `D:120` `cases=(` starts the complete 23-row set; `D:138` `F1_HELPER_DIRECT`, `D:139` `F1_NESTED_HELPER`, and `D:140` `F1_MEMBERSHIP_ALIAS` are the new escapes.
- `D:146` `TOTAL_ROWS=${#cases[@]}` derives cardinality; `D:148` `TOTAL_ROWS != DECLARED_ROWS` checks it before iteration; `D:156` `row_end > TOTAL_ROWS` bounds ranges to that set.
- `D:215` `py_compile`, `D:229` `--collect-only`, and `D:243` `timeout` retain compile, collect, and timeout gating.


## Static, identity, and review checks

```text
py_compile_rc=0
pyflakes_rc=0
bash_n_rc=0
git_diff_check_rc=0
checker_pin_diff_rc=0
```

- `python3 scripts/ap_screen.py --s0-01 T` returned rc 0. It reported the existing S0-01 corpus classes only; the sole hit in T's changed file is pre-existing `AP-66` at `T:87` `nv._point_mul = _cached_pm` and `T:89` `nv._point_mul = _orig_pm`, outside this diff. The direct driver screen returned `0 hits over 1 files`.
- GitNexus `detect-changes --scope all` returned `Changes: 3 files, 14 symbols`, `Affected processes: 0`, `Risk level: low`; its clone index did not identify the newly added CK16 symbols, so this is advisory and incomplete.
- Ripwire `for` and `impact` both returned rc 0. Impact found six direct tests of `_assert_ck16_classifier_operand_contract`, including all three new escape controls, but labels all six `radius_untested`; that is the known test-to-helper indexing blind spot, not an absence of pytest execution.
- Final context pack: `../scratch/A5o-final-context-pack.md` (`223 lines`).
- Lane process census found one matching process: this Hermes lane itself; no mutation-driver or pytest process remains.

## File identity

- `T` = `tests/test_s0_01_check_acp_conformance.py`: 5894 lines, sha256 `a27f685795580ce1c2df9b8207e54a68eaf4b37289257af94141b1ba3833cfbe`.
- `D` = `tasks/briefs/s0-01-a5o-support/mutants.sh`: 300 lines, mode 755, sha256 `990f5e8b8cf56c8b40db74bb2a02619e85149bef43d4d97fde830a70aa825ed9`.
- `C` = `proofs/S0-01/check_acp_conformance.py`: 1906 lines, sha256 `7a13fbffed9fae2cc74be89bd400237a5db25ba0ae477e4e45571a4bfc347bcb`.

## Self-attack

1. Binding propagation could overmatch unrelated local expressions. Ruled out for the exercised boundary by `test_ck16_unrelated_comparison_is_outside_classifier_operand_contract`, which stayed green in the focused `6 passed` run; direct derivation accepts only an exact operand spelling, a resolved alias name, a resolved helper call, or a walrus RHS.
2. One of the three advertised escapes could be a vacuous test. Ruled out by the pre-fix and binding-removed RED controls (`DID NOT RAISE` for all three), then by the three driver rows that each changed C, compiled, collected the module-wide test, and died with the intended exact inventory message.
3. The driver could print a green denominator while skipping an added row. Ruled out by deriving `TOTAL_ROWS` from the case array before range validation and by both permanent controls: one deleted row and one appended duplicate each exited nonzero with the exact cardinality mismatch. The full campaign reported 22 kills plus one green control.

## Evidence tiers

- VERIFIED: focused CK16 execution, RED controls, all mutation rows, driver self-controls, static checks, checker byte identity, screens, file identity, and lane-process census above.
- INFERRED: no other S0-01 behavior changed, based on the exact-inventory checks and focused tests. The required full-file xdist run did not start.
- ASSUMED: none.

## DISCREPANCIES

- The required outer xdist gate is blocked before pytest starts. Two launch attempts of `scripts/pc_suite.sh launch -n 8 -- tests/test_s0_01_check_acp_conformance.py` returned rc 2 because this lane has no bridge environment. Its remote probe then emitted `pc_suite: the PC clone does not have ... — push the head first`; a direct local `git -C /home/rocco/agent-factory cat-file -t 99ecb3679ad974490bf2d5e45fab8c396e252364` returned `commit`, so that second text is a downstream artifact of the unavailable bridge and is not evidence that the local PC clone lacks the PIN.
- The failed launch expanded the missing-variable diagnostics from `scripts/pc.sh`; no bridge value was present or printed. I did not read `.pc-bridge.env`, push the detached PIN, or replace the required xdist outer gate with a narrower serial run. A bounded Graft check could not map either shell script (`nothing indexed` / `no definitions indexed`).
- The first ripwire edit-check call used a file path where this verb required a uniquely qualified contract. It returned rc 1 with an ambiguity list. The symbol-qualified `ripwire for` and `ripwire impact` calls then returned rc 0.
- Final report lint: `report_lint: 27 refs — OK 27, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.

## Retro

- No new anti-pattern class found. F2 reproduces the existing AF-AP-84 fixed-denominator recurrence. Nothing to bake in this lane.

## NOT DONE

- Required outer xdist gate remains BLOCKED as stated above; no `pytest-set` hash or whole-file count exists.
- Independent sandbox adversarial verification has not run.
- No production checker change, live ACP/Buzz/OmniRoute action, proof mint, commit, push, or tag.
