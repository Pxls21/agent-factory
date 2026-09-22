# A5q — issue #8 (the four CK16 classifier-operand meta-oracle defects, closed in ONE sweep; T only) — final report

Role: code-implementer (local Qwen build route). PIN: 236bec7. Venue: pc (tasks/briefs/pc/VENUE-MAP.md).
This lane output is a PROPOSAL until the sandbox adversarial-verifier grades it; no gate verdict issued, no commit, no push, no outward action, no production bytes touched.

## Outcome

Verified build-lane proposal: all four issue-#8 defects are fixed in T with five named tests (A5P-01 control plus A5P-02..05 regressions); every individual revert and flipped expectation is red; C, P, and all proofs remain byte-identical to PIN. Final gate: 483 passed twice. Independent adversarial verification remains pending.

## Item 1 — premise (four reds + one green at the PIN)

Premise VERIFIED at PIN 236bec7. Baseline full gate (before any edit): `478 passed in 107.25s (0:01:47)` (467 T + 11 spec_runner; the brief says the PIN collects 478 — matches). G2 region at the PIN begins at T@236bec7:2010 `def test_golden_synchronous_frame_order_still_binds():` and ends at T@236bec7:2152 `cc.check_golden(bundle / "golden")`; `git diff 236bec7 -- T` produced 0 hunk headers (file byte-identical to PIN pre-edit).

The five named tests were inserted into T and run UNFIXED (model at the PIN). Result:

```
4 failed, 1 passed, 463 deselected in 1.55s
FAILED ...::test_ck16_a5p02_local_rebind_of_reserved_name_clears
FAILED ...::test_ck16_a5p03_kwonly_default_seeds_derived
FAILED ...::test_ck16_a5p04_posonly_defaults_align_to_trailing_params
FAILED ...::test_ck16_a5p05_bare_truth_test_is_a_boolean_context
```

Exact `E` / failure lines, verbatim:

- A5P-02 (false positive — reserved spelling matched before binding state):
  `E       AssertionError: classifier-operand comparison inventory changed: [('argv_local', 'value == argv')]`
- A5P-03 (false negative — kwonly default not seeded):
  `E       Failed: DID NOT RAISE AssertionError`
- A5P-04 (wrong-parameter binding — `value == 'x'` raised, `pin == 'x'` did not):
  `E       AssertionError: classifier-operand comparison inventory changed: [('posonly_align', "value == 'x'")]`
  and, for the `pin == 'x'` discriminator: `E       Failed: DID NOT RAISE AssertionError`
- A5P-05 (false negative — bare truth test not inventoried):
  `E       Failed: DID NOT RAISE AssertionError`
- A5P-01 control (ordinary alias rebind — already green at PIN, stays green): passed.

Every failure matches the class stated in issue #8. No premise conflict.

## Item 2 — A5P-02 (last-binding state takes precedence for reserved spellings)

Fix in `_assert_ck16_classifier_operand_contract`: added `reserved_operand_names = {"argv"}` and a separate `parameter_seeds` pass. A parameter named `argv` is seeded as the intended classifier operand; in `value_is_derived`, a reserved Name then resolves through the LAST binding (scope-local first, then the scope's globals) — it is derived ONLY if that final binding is the reserved operand, never after a local rebind to a non-operand. This is the exact inverse of the old bug (unparse spelling matched before binding state). `cmd.split()` remains a direct expression operand, not a bare Name spelling.

Green: `test_ck16_a5p02_local_rebind_of_reserved_name_clears` passes (see item 5 run below).
A5P-01 control stays green (ordinary alias rebind is unchanged and still NO_RAISE).

## Item 3 — A5P-03 (pair each kwonlyarg with its kw_default, skipping None)

`default_seeds` now zips `args.kwonlyargs` with `args.kw_defaults`, skipping `None` (required kwonly has no default), and adds a seed for each kwonlyarg whose default is a derived operand.

Green: `test_ck16_a5p03_kwonly_default_seeds_derived` now RAISES (the kwonly-derived `pin` is inventoried).

## Item 4 — A5P-04 (align defaults to the trailing portion of posonlyargs + args)

`default_seeds` now computes `positional = args.posonlyargs + args.args` and pairs `positional[-len(args.defaults):]` with `args.defaults` (the actual `ast.arguments` semantics), instead of zipping only `args.args`. Both discriminators flip to the expected outcome: `value == 'x'` NO_RAISE, `pin == 'x'` RAISE.

Green: `test_ck16_a5p04_posonly_defaults_align_to_trailing_params` passes (both branches).

## Item 5 — A5P-05 (deliberate boolean-context inventory, per the coordinator's PIN)

In `visit` (inside `analyze_body`), the existing Compare/BoolOp use detection remains, and the boolean-context domain is expanded deliberately by node type:

- A `BoolOp` containing any derived operand → boolean-context use (the existing BoolOp domain; preserved).
- `UnaryOp(Not)` whose operand is derived → boolean-context use.
- `IfExp` whose test is derived → boolean-context use.

The WHOLE test expression of `If` / `While` / `Assert` is inventoried at the expression's source-order position, before the body is visited. The named A5P-05 test exercises all five new shapes independently (`if_pin`, `while_pin`, `assert_pin`, `ifexp_pin`, `not_pin`) and asserts each appears in the emitted inventory.

A new downstream assert `allowed_boolean_tests` (initially empty) freezes this domain.

DOMAIN STATEMENT (honest, in the report as required):

- IN: `Compare` and `BoolOp` (existing, operand-level), `If.test`, `While.test`, `Assert.test`, `IfExp.test`, `UnaryOp(Not).operand` as whole test/operand expressions.
- OUT (explicitly NOT inventoried): a derived value passed to a boolean CALL (`bool(x)`, `any(x)`, `all(x)`, `len(x)`), a derived value in a comprehension/`for` iterable, and a derived value used only as a non-test operand of `UnaryOp` other than `Not` (e.g. `~`). These remain a stated limit; a real use landing there is a future FINDING, not a silent expansion.

## Item 6 — the production checker C still satisfies the contract

Ran the C-contract test in isolation on the UNMODIFIED C:

```
tests/test_s0_01_check_acp_conformance.py::test_ck16_checker_inventories_classifier_operand_predicates_module_wide
1 passed in 0.20s
```

`-k "ck16 or ck17"` subset (14 pre-existing CK16/CK17 + the 5 new A5P tests = 19):

```
19 passed, 449 deselected in 2.15s
```

C and pins are byte-identical to the PIN:

```
C identical to PIN (git diff rc=0)
pins identical to PIN (git diff rc=0)
868b8705699b5e78b1468252ecbdec93736d2a7e2f4819424311c31c243db46a  proofs/S0-01/check_acp_conformance.py
1a2f9a38ddba14e3ea75c06e77e43083a059e8dc5caf5499c7e54e9013921981  proofs/S0-01/pins.py
```

Note (see DISCREPANCIES): the two `check_config_echo` `'--…' not in argv` entries that the A5o round had pinned in `allowed_predicates` are removed — in `check_config_echo`, `argv` is a local list of argv.txt lines, not the classifier operand, so those entries were themselves artifacts of the A5P-02 bug (the reserved spelling was matched before the binding state was consulted). Their removal is part of the A5P-02 fix, not a C change.

## Item 7 — mutation audit (scratch copies of T only)

Each mutant was applied to a scratch copy under `../scratch/mut/`; T was never overwritten. The companion A5P-01 control was the named `test_ck16_a5p01_ordinary_alias_rebind_control_is_not_classifier_operand`. Exact final results:

| Mutant | Named killer | Exact result / assertion | A5P-01 control |
|---|---|---|---|
| M1 revert A5P-02 last-binding guard + restore the two old `check_config_echo` entries (complete pre-A5q A5P-02 model) | `test_ck16_a5p02_local_rebind_of_reserved_name_clears` | `1 failed, 1 passed in 0.92s`; `E       AssertionError: classifier-operand comparison inventory changed: [('argv_local', 'value == argv')]` | PASS |
| M2 delete kwonly default pairing only | `test_ck16_a5p03_kwonly_default_seeds_derived` | `1 failed, 1 passed in 0.78s`; `E               Failed: DID NOT RAISE AssertionError` | PASS |
| M3 revert `posonlyargs + args` trailing alignment to old `args.args` zip only | `test_ck16_a5p04_posonly_defaults_align_to_trailing_params` | `1 failed, 1 passed in 0.82s`; `E       AssertionError: classifier-operand comparison inventory changed: [('posonly_align', "value == 'x'")]` | PASS |
| M4 delete the new If/While/Assert/IfExp/Not boolean-context inventory + final assert | `test_ck16_a5p05_bare_truth_test_is_a_boolean_context` | `1 failed, 1 passed in 0.68s`; `E               Failed: DID NOT RAISE AssertionError` | PASS |

The M1 mutation is a COMPLETE fix revert: the pre-A5q model matched reserved spellings before binding state and also carried two `check_config_echo` allowed entries produced by that same bug. Reverting only the guard while leaving the corrected allowed inventory causes both the named A5P-02 test and the production C-contract control to fail; restoring the dependent old entries isolates the requested named killer while retaining the A5P-01 control.

### De-vacuous pass (flip each new test's expected outcome; scratch only; restored)

- A5P-02 expected RAISE instead of NO_RAISE: `d1-a5p02-expect-raise: RED at own assert rc=1 | 1 failed in 0.68s`; `>       with pytest.raises(`; `E               Failed: DID NOT RAISE AssertionError`.
- A5P-03 expected NO_RAISE instead of RAISE: `d2-a5p03-expect-no-raise: RED at own assert rc=1 | 1 failed in 0.73s`; `E       AssertionError: classifier-operand comparison inventory changed: [('kwonly_pin', 'value == pin')]`.
- A5P-04 `value == 'x'` expected RAISE instead of NO_RAISE: `d3a-a5p04-value-expect-raise: RED at own assert rc=1 | 1 failed in 0.65s`; `E                       Failed: DID NOT RAISE AssertionError`.
- A5P-04 `pin == 'x'` expected NO_RAISE instead of RAISE: `d3b-a5p04-pin-expect-no-raise: RED at own assert rc=1 | 1 failed in 0.74s`; `E       AssertionError: classifier-operand comparison inventory changed: [('posonly_align', "pin == 'x'")]`.
- A5P-05 expected NO_RAISE instead of RAISE: `d4-a5p05-expect-no-raise: RED at own assert rc=1 | 1 failed in 0.64s`; `E       AssertionError: classifier-operand boolean-test inventory changed: [('truth_contexts', 'assert_pin'), ('truth_contexts', 'if_pin'), ('truth_contexts', 'ifexp_pin'), ('truth_contexts', 'not_pin'), ('truth_contexts', 'while_pin')]`.

All scratch mutants were removed after each run. No mutant bytes remain in T.

## Final gates (final T bytes)

Two required xdist runs used `-n 4 -q -p no:cacheprovider`, the two named test files, the declared PC real-leg inputs, and separate absolute short basetemps:

```
RUN 1: 483 passed in 104.99s (0:01:44)
RUN 2: 483 passed in 104.27s (0:01:44)
```

Both runs have ZERO failed and ZERO xfailed. The PIN collected 478; the exact +5 is the five new named A5P tests. Counts agree bit-for-bit at 483.

Final CK16/CK17 evidence:

```
C-contract isolated: 1 passed in 0.23s
-k "ck16 or ck17": 19 passed, 449 deselected in 2.38s
-k ck16: 8 passed, 460 deselected in 1.09s
```

Static gates:

```
python -m pyflakes tests/test_s0_01_check_acp_conformance.py
pyflakes rc=0
git diff --check 236bec7 -- tests/test_s0_01_check_acp_conformance.py
diff-check rc=0
```

`ap_screen --tests` final output:

```
--- TEST_SCREEN over 1 path(s): 4 hits over 1 files ---
AP-66: 2
    tests/test_s0_01_check_acp_conformance.py:88: nv._point_mul = _cached_pm
    tests/test_s0_01_check_acp_conformance.py:90: nv._point_mul = _orig_pm
AF-AP-48: 1
    tests/test_s0_01_check_acp_conformance.py:6378: assert all(site[3] in {"walk", "require_regular_file", "stdin", "consumer"}
AF-AP-57: 1
    tests/test_s0_01_check_acp_conformance.py:5821: if call_count[0] == 2:
ap_screen rc=0
```

RUN classification: all four are PRE-EXISTING and outside every A5q hunk (`git diff --unified=0` found no added/removed matching screen line): AP-66 monkeypatch/restore pair at T:88 `nv._point_mul = _cached_pm` and T:90 `nv._point_mul = _orig_pm`; AF-AP-57 deterministic second-call fault injection at T:5821 `if call_count[0] == 2:`; AF-AP-48 finite allowed call-site category assertion at T:6378 `assert all(site[3] in {"walk", "require_regular_file", "stdin", "consumer"}`. NEW hits: 0.

## Item 8 — boundary / G2 preservation

FILE IDENTITY:

```
75fad3cd77ce3fa41baf2bccfdaa061d1def2472af4587d572b23d14e74a996e  tests/test_s0_01_check_acp_conformance.py
868b8705699b5e78b1468252ecbdec93736d2a7e2f4819424311c31c243db46a  proofs/S0-01/check_acp_conformance.py
1a2f9a38ddba14e3ea75c06e77e43083a059e8dc5caf5499c7e54e9013921981  proofs/S0-01/pins.py
```

Boundary commands:

```
git diff --quiet 236bec7 -- proofs/; rc=0
git diff --quiet 236bec7 -- proofs/S0-01/check_acp_conformance.py; rc=0
git diff --quiet 236bec7 -- proofs/S0-01/pins.py; rc=0
git diff 236bec7 -- tests/test_s0_01_check_acp_conformance.py | grep -c '^@@'
11
```

All 11 hunk headers, verbatim:

```
@@ -3273,13 +3273,28 @@ def _assert_ck16_classifier_operand_contract(checker_path):
@@ -3292,6 +3307,9 @@ def _assert_ck16_classifier_operand_contract(checker_path):
@@ -3302,14 +3320,41 @@ def _assert_ck16_classifier_operand_contract(checker_path):
@@ -3317,6 +3362,12 @@ def _assert_ck16_classifier_operand_contract(checker_path):
@@ -3345,17 +3396,46 @@ def _assert_ck16_classifier_operand_contract(checker_path):
@@ -3387,10 +3467,12 @@ def _assert_ck16_classifier_operand_contract(checker_path):
@@ -3411,22 +3493,26 @@ def _assert_ck16_classifier_operand_contract(checker_path):
@@ -3456,9 +3542,13 @@ def _assert_ck16_classifier_operand_contract(checker_path):
@@ -3476,6 +3566,27 @@ def _assert_ck16_classifier_operand_contract(checker_path):
@@ -3483,9 +3594,15 @@ def test_ck16_checker_inventories_classifier_operand_predicates_module_wide():
@@ -3719,6 +3836,120 @@ def test_ck17_classifier_operand_attribute_hop_is_stated_limit(tmp_path):
```

No hunk header or hunk touches the PIN G2 region beginning at T@236bec7:2010 `def test_golden_synchronous_frame_order_still_binds():` and ending at T@236bec7:2152 `cc.check_golden(bundle / "golden")`. G2 is UNTOUCHED.

Final intended repository files are T plus this report only. `report-draft.md`, mutation drivers, basetemps, and context pack are lane-side scratch artifacts outside the tree and are not harvest inputs.

## Evidence tiers

VERIFIED:

- T:3296 `reserved_operand_names = {"argv"}` and T:3309 `def value_is_derived` implement reserved-name binding state; T:3327 `def parameter_seeds` preserves intended `argv` parameters.
- T:3335 `def default_seeds` plus T:3344 `positional = args.posonlyargs + args.args` implement keyword-only defaults and AST-correct trailing positional-default alignment.
- T:3359 `def analyze_body` and T:3365 `def record_boolean_context` inventory source-ordered `If` / `While` / `Assert` whole tests; T:3429 `isinstance(node, (ast.UnaryOp, ast.IfExp))` adds `IfExp.test` and `UnaryOp(Not).operand` while retaining Compare/BoolOp inventory.
- T:3528 `allowed_compares`, T:3551 `allowed_predicates`, and T:3575 `allowed_boolean_tests` freeze the comparison, BoolOp/membership, and boolean-test inventories. The two false `check_config_echo` entries are absent and documented.
- T:3839 `test_ck16_a5p01_ordinary_alias_rebind_control_is_not_classifier_operand`, T:3857 `test_ck16_a5p02_local_rebind_of_reserved_name_clears`, T:3875 `test_ck16_a5p03_kwonly_default_seeds_derived`, T:3894 `test_ck16_a5p04_posonly_defaults_align_to_trailing_params`, and T:3921 `test_ck16_a5p05_bare_truth_test_is_a_boolean_context` supply the control and four regressions. A5P-04 tests both discriminators; A5P-05 verifies all five new node shapes.
- Two 483-test final runs, targeted CK16/17 runs, four mutation kills, five de-vacuous kills, pyflakes, AP screen, proofs identity, and G2 hunk boundary are measured in this session.

INFERRED:

- None used for acceptance.

ASSUMED:

- None.

## Self-attack

1. LIKELY WRONG: A5P-02 might clear `argv` but also stop recognizing a genuine `argv` parameter. RULED OUT: `parameter_seeds` marks the intended parameter; the complete pre-fix mutation dies on A5P-02 while A5P-01 survives, and the unchanged C contract plus both 483-test runs pass.
2. LIKELY WRONG: positional defaults might still align to `args.args` instead of the combined Python AST sequence. RULED OUT: the named test has independent NO_RAISE (`value`) and RAISE (`pin`) discriminators; each flipped expectation dies independently, and reverting alignment produces the exact wrong-`value` failure.
3. LIKELY WRONG: A5P-05 might claim five boolean shapes while only the `If` sample fires. RULED OUT: the final named test injects distinct derived aliases for If/While/Assert/IfExp/Not and asserts all five inventory tuples; removing the new inventory makes it red. Calls such as `bool()`/`any()` remain explicitly OUT.

## DISCREPANCIES

- The brief's parenthetical says “every pre-existing CK16 test stays green (`-k ck16` subset).” Exact final results are `8 passed` for literal `-k ck16` and `19 passed` for `-k "ck16 or ck17"`; the latter includes the A5p model's pre-existing CK17 scope/data-flow controls plus the five new A5P cases. Both were run and pasted.
- The brief's known AP-screen line numbers T@236bec7:5590/T@236bec7:6147 drift to final T:5821 `if call_count[0] == 2:` and T:6378 `assert all(site[3] in {"walk", "require_regular_file", "stdin", "consumer"}` because A5q adds lines before them. The same exact pre-existing tokens remain; no A5q hunk touches them.
- `report_lint` final bounded run: `report_lint: 31 refs — OK 28, NEAR 0, MISS 0, UNCHECKABLE 3, UNRESOLVED 0 (worktree)`; floor 12 satisfied. The three UNCHECKABLE rows are verbatim AP-screen output lines, not report claims.
- GitNexus `impact "_assert_ck16_classifier_operand_contract"` against the clone index returned “No symbols found matching”; per-function `scripts/why.sh` found no commit history for this post-PIN helper. The mandated post-edit `detect-changes` did run and reported `Changes: 1 files, 20 symbols`, `Affected processes: 0`, `Risk level: low`; its clone-HEAD symbol list is stale/noisy and includes unrelated functions, so it is recorded as advisory only. `graft ask`, ripwire callers, and the final lane context pack were also run.
- The report lives at `tasks/briefs/s0-01-a5p-support/A5q-report.md` in the repository as required. The brief's separate `git status` wording (“exactly T and your report”) is evaluated after that required report copy below.

## NOT-done

- NOT committed, pushed, tagged, published, or posted.
- NOT independently accepted. This remains a code-implementer proposal until the sandbox adversarial-verifier grades it.
- NOT widened into the stated OUT domain (boolean calls, container/subscript hops, attribute hops, closures beyond the frozen direct cases, global/nonlocal, path sensitivity).
- NOT changed: production checker C, pins P, proofs/evidence, spec runner, ledger, or sibling-lane files.

## GATE RECOMMENDATION

MERGE-READY as a build-lane proposal, contingent on the separate sandbox adversarial-verifier. Four issue-#8 defects reproduce red at the PIN, turn green after the T-only fixes, die under individual reverts, and retain a green A5P-01 control. Final deterministic gate is 483/483 twice with C/P/proofs byte-identical to PIN and G2 hunks untouched.
