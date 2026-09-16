# VERIFY-A5o — adversarial verification report

NOT built: the binding-aware CK16 inventory remains bypassable. Findings below are reproduced from scratch copies. No merge verdict issued, per the single-model rule.

## V1–V3 — binding audit

1. [BLOCKER] The asserted binding model over-matches a reassigned local and under-matches ordinary data-flow forms. `_assert_ck16_classifier_operand_contract` accumulates aliases once derived and never kills an alias after later assignment (`T:3039-3050`). Its derivation accepts only exact spelling, a resolved `Name`, helper call, or walrus RHS (`T:3012-3026`), so it misses container/subscript, augmented assignment, lambda/default, attribute, and module-scope flows.

   Repro: `../scratch/test_ck17_hostile.py`, with `/home/rocco/venv-agent-factory/bin` first on `PATH`, `S0_01_VENUE=pc`, and the declared real-leg corpus. Output: `7 failed, 1 passed in 1.94s`.

   - `pin = PINNED_TEE_PATH; pin = 'literal'; return value == pin` falsely raises `classifier-operand comparison inventory changed`.
   - `(PINNED_TEE_PATH,)[0]`, `pin += PINNED_TEE_PATH`, lambda/default-argument, attribute, and module-alias-chain copies each produce `Failed: DID NOT RAISE AssertionError`.

   Minimal fix: define and implement the static-analysis domain. If the contract claims all classifier-operand data flow, add scope-correct last-binding analysis and the supported expression classes, with red controls. If it deliberately has a smaller domain, state that limit and stop calling it a module-wide inventory.

2. [SHOULD-FIX] The three permanent CK17 controls do not pin the broader resolution boundary. They exercise direct helper return, nested walrus, and `AnnAssign` membership only (`T:3158-3203`). The committed focused selector itself is green: `6 passed, 431 deselected in 1.29s`, despite the seven hostile failures above.

   Minimal fix: add committed regressions for the chosen domain, including a rebind-negative test.

## V4 — mutation driver controls

Reproduced:

```text
SELF_TEST rc=1 CARDINALITY_MISMATCH rows=22 expected=23 destructive=22 control=1
ADDED_ROW_CONTROL rc=1 CARDINALITY_MISMATCH rows=24 expected=23 destructive=22 control=1
invalid row range: 1-24 (total=23)
self=0 added=0 range=64
TIMEOUT_CONTROL rc=1 INVALID F1_SECOND_IF TIMEOUT after=4s | EXPECTED=22 KILLED=21 SURVIVED=0 INVALID=1 CONTROL=1
timeout_control=0
```

The wrappers correctly certify their intentional red state. `--timeout-control` at `D:76` drives the `TIMEOUT_CONTROL` arm; `TOTAL_ROWS` at `D:146` and `row_end` at `D:156` enforce derived cardinality and range.

## V5–V6 — escape rows and checker identity

Reproduced:

```text
KILLED F1_HELPER_DIRECT | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck16_checker_inventories_classifier_operand_predicates_module_wide | E       AssertionError: classifier-operand comparison inventory changed: [('_alias_classifier', 'value == pin')]
KILLED F1_NESTED_HELPER | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck16_checker_inventories_classifier_operand_predicates_module_wide | E       AssertionError: classifier-operand comparison inventory changed: [('_outer_classifier_alias', 'value == (pin := PINNED_AGENT_REALPATH)'), ('nested', 'value == (pin := PINNED_AGENT_REALPATH)')]
KILLED F1_MEMBERSHIP_ALIAS | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck16_checker_inventories_classifier_operand_predicates_module_wide | E       AssertionError: classifier-operand BoolOp/membership inventory changed: [('_membership_classifier', 'pin in values')]
ROWS=18-20 SELECTED=3 KILLED=3 SURVIVED=0 INVALID=0 CONTROL=0
rows_18_20=0
```

Rows 18–20 compile, collect, and die through the exact real CK16 meta-test selector: `compile_rc` begins at `D:219`, `collected` is validated at `D:234`, and `killer`/`detail` are required at `D:269-275`.

Reproduced: `git diff --quiet c728be5 -- proofs/S0-01/check_acp_conformance.py` returned rc 0. C remained byte-identical.

## V7 — static checks and focused execution

Reproduced:

```text
checker_pin_diff_rc=0
git_diff_check_rc=0
6/437 tests collected (431 deselected) in 0.69s
collect_ck16_rc=0
6 passed, 431 deselected in 1.29s
real_ck16_rc=0
```

Full checker-file xdist and the complete 22-row campaign were deliberately not run after the BLOCKER reproduced. Those gates cannot overturn a direct red boundary test.

Static checks reproduced: `py_compile=0 pyflakes=0 bash_n=0 ap_screen=0`; `git diff --check` was also rc 0.

## File identity

- T `tests/test_s0_01_check_acp_conformance.py`: `ROOT` at `T:27`; 5,894 lines; `a27f685795580ce1c2df9b8207e54a68eaf4b37289257af94141b1ba3833cfbe`.
- D `tasks/briefs/s0-01-a5o-support/mutants.sh`: `EXPECTED=22` at `D:12`; 300 lines; `990f5e8b8cf56c8b40db74bb2a02619e85149bef43d4d97fde830a70aa825ed9`.
- C `proofs/S0-01/check_acp_conformance.py`: `def main` at `C:1853`; 1,906 lines; `7a13fbffed9fae2cc74be89bd400237a5db25ba0ae477e4e45571a4bfc347bcb`.

## Mapping and evidence status

- Pack: `../scratch/VERIFY-A5o-context-pack.md` (229 lines). Graft mapped `def _assert_ck16_classifier_operand_contract` at `T:2909`; Ripwire mapped the `test_ck16_checker_inventories_classifier_operand_predicates_module_wide` caller at `T:3120` plus `test_ck17_classifier_operand_membership_alias_is_rejected` and four controls through `T:3191`. GitNexus and code-review-graph were unavailable, so this report makes no dormant/reachability absence claim.
- Reproduced: identities, C byte identity, diff check, focused collection/run, hostile scratch suite, driver cardinality/range/timeout controls, and rows 18–20.
- Static review only: full campaign mechanics beyond the executed controls.

## NOT DONE

- Full-file outer xdist and the complete 22-row campaign were not run after the direct BLOCKER repro.
- No production source changed, no proof minted, no commit/push/tag, and no live ACP/Buzz/OmniRoute action.

## DISCREPANCIES

- The brief V1 premise says a rebinding to a non-operand must not flag. It flags: verified by the first hostile case.
- The brief calls this a “module-wide” inventory, but `function_operand_aliases` at `T:3039` resolves aliases inside each function and ignores module assignments; the module-alias hostile case escaped.
- GitNexus and code-review-graph were unavailable in the lane; Graft and Ripwire supplied the mapping evidence.
- Final report lint: `report_lint: 16 refs — OK 16, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.

## Retro

New recurrence: AF-AP-30 / resolver-mirror variant. A syntax inventory that models aliases but not scope/lifetime is simultaneously false-positive and fail-open. Put the static-analysis domain into the pre-registered contract before a repair lane expands it.
