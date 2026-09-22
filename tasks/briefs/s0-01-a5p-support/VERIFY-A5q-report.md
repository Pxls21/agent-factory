# VERIFY-A5q — independent adversarial verification of issue #8 (CK16 classifier-operand meta-oracle sweep)

Role: adversarial-verifier (LOCAL Qwen verify route, `agentfactory-verify-local`). PIN: 2e02afd. Base: 236bec7.
Venue: pc (tasks/briefs/pc/VENUE-MAP.md). This lane VERIFIES; it never fixes. It emits a GATE RECOMMENDATION, never a verdict.

## Item 1 — premise

Commands (all from the lane tree, PIN 2e02afd):
- `git diff --stat 236bec7 2e02afd -- proofs/ tests/test_s0_01_spec_runner.py scripts/proof-runner scripts/validate-ledger` → **empty** (no output, rc=0). C/P/S/proof-runner/validate-ledger byte-identical.
- `git diff --stat 236bec7 2e02afd -- tests/` → **names TWO files**: `tests/test_s0_01_check_acp_conformance.py` (+246/−15) and `tests/test_s0_02_buzz_authz.py` (+171/−0).
- `sha256sum tests/test_s0_01_check_acp_conformance.py` → **75fad3cd77ce3fa41baf2bccfdaa061d1def2472af4587d572b23d14e74a996e** (matches the brief's expected hash exactly).
- Hunk-boundary check: the diff produced **11 hunk headers**; the first/last and G2 range are named in the command output only, rather than cited as T source coordinates. **No hunk falls inside the G2 region.**

DISCREPANCY (item 1, D2): the brief said `git diff --stat 236bec7 2e02afd -- tests/` "must name only T". Measured output names T PLUS `tests/test_s0_02_buzz_authz.py`. Bounded disambiguation (3 experiments):
- `git merge-base --is-ancestor 236bec7 2e02afd` → 236bec7 IS an ancestor of 2e02afd.
- `git log --oneline 236bec7..2e02afd` → 16 commits in the range. The extra test file was added by `c439580 S0-02 B6 LANDED (issue #3)` — a DIFFERENT increment (S0-02, not S0-01) that landed on the shared branch between A5q's base (236bec7) and A5q's parent (78745d3).
- `git diff --stat c439580 2e02afd -- tests/test_s0_02_buzz_authz.py` → empty (A5q did not touch that file); `git log --oneline 236bec7..78745d3 -- tests/test_s0_01_check_acp_conformance.py` → empty (T untouched by every intervening increment, so A5q's T-diff is identical vs either 236bec7 or 78745d3); `git diff --stat 78745d3 2e02afd -- tests/` → names ONLY T.

Conclusion: the extra file is **shared-branch base drift** (S0-02 B6), not an A5q change to the production surface. A5q's own commit (2e02afd vs its real parent 78745d3) touches ONLY T; C/P/S/proof-runner/validate-ledger and the S0-01 mint are byte-identical to 236bec7 (hashes below). The item-1 premise — "A5q touched T only and left the production spine intact" — is TRUE at the level that matters for this round. I build on the measured truth and log the D2 wording as a DISCREPANCY rather than stopping with CONTRACT-INVALID.

S0-01 mint/production byte-identity (base 236bec7 vs PIN 2e02afd), measured:
- `proofs/S0-01/result.json`: bb98b1a4… identical
- `proofs/S0-01/check_acp_conformance.py` (C): 868b8705699b5e78b1468252ecbdec93736d2a7e2f4819424311c31c243db46a (identical)
- `proofs/S0-01/pins.py` (P): 1a2f9a38ddba14e3ea75c06e77e43083a059e8dc5caf5499c7e54e9013921981 (identical)

SOLID. Blocking? No. The premise's SUBSTANTIVE checks (C/P/S/proof-runner/validate-ledger empty vs base; T hash exact; 11 hunks outside G2) all pass. The single D2 wording mismatch is a non-blocking discrepancy (base drift from a sibling S0-02 increment), not an A5q defect — it does not contradict any frozen criterion of THIS increment.

## Item 2 — original issue-#8 cases + named-test collection

I rebuilt an independent scratch driver (`../scratch/a5q_item2_driver.py`) that imports the PIN's real `_assert_ck16_classifier_operand_contract` and `_ck16_checker_copy` from T, injects the original issue shapes ahead of C's exact `def _pinned_process_count(commands):` anchor, and executes each static C-contract analysis. It does not invoke the builder's five tests as its oracle.

Command:
`python ../scratch/a5q_item2_driver.py`

Exact output:
```
ROW        EXPECTED    OBSERVED    VERDICT
----------------------------------------------------------------
A5P-01    NO_RAISE    NO_RAISE   MATCHES-CONTRACT
A5P-02    NO_RAISE    NO_RAISE   MATCHES-CONTRACT
A5P-03    RAISE       RAISE      MATCHES-CONTRACT
A5P-04    RAISE       RAISE      MATCHES-CONTRACT
A5P-04a   NO_RAISE    NO_RAISE   MATCHES-CONTRACT
A5P-04b   RAISE       RAISE      MATCHES-CONTRACT
A5P-05    RAISE       RAISE      MATCHES-CONTRACT
----------------------------------------------------------------
rows matching contract: 7/7
```

A5P-01 is the issue's A5o-V1 control: ordinary `pin` starts derived then rebinds to `'literal'`, and the later `value == pin` stays **NO_RAISE**. A5P-02 uses a reserved `argv` parameter then locally rebinds it to `object()` and stays **NO_RAISE**. A5P-03 (derived kwonly default), A5P-04 (`value == pin`), A5P-04b (`pin == 'x'`), and A5P-05 (`if pin:`) each raise the relevant frozen inventory assertion; A5P-04a (`value == 'x'`) stays **NO_RAISE**. All seven observed outcomes match the explicit contract.

Named-test command:
`python -m pytest -q -p no:cacheprovider --basetemp ../scratch/bt/a5p tests/test_s0_01_check_acp_conformance.py -k a5p0`

Exact output: `5 passed, 463 deselected in 1.12s`.

SOLID. Blocking? No: all contract rows reproduce against the actual PIN model and exact C-copy path. Predicate: contract mapping yes; canonical model consumer yes; material effect yes (the expected frozen inventory assertion is present/absent per row); concrete discriminator yes; task ownership yes. No finding.

## Item 3 — new hostile shapes, C audit, and inventories

Method: `python ../scratch/a5q_item3_driver.py` injects each NEW shape ahead of C's `_pinned_process_count` anchor, executes the PIN's actual `_assert_ck16_classifier_operand_contract`, and compares its observed `RAISE`/`NO_RAISE` against the expectation written from the comment/docstring before the run. `python ../scratch/a5q_item3_trace.py` then localized the four initially flagged cases. This is a static model (the real C-contract consumer), so each injection has no runtime effect on the checker.

### Shape table

| Shape(s) | Claimed domain | Expected → observed | Grade |
|---|---|---|---|
| a1 module `argv = PINNED_TEE_PATH`; `value == argv` | IN: module alias visible at definition | RAISE → RAISE | SOLID |
| a2 module `argv = []`; `value == argv` | IN: module rebind clears | NO_RAISE → NO_RAISE | SOLID |
| a3 parameter `argv`; `argv += object()`; compare | IN: AugAssign tracked | RAISE → RAISE. AugAssign preserves derivedness because its pre-binding is derived. | SOLID |
| a4 parameter `argv`; `argv: int = object()`; compare | IN: AnnAssign tracked and clears | NO_RAISE → NO_RAISE | SOLID |
| a5 parameter `argv`; `(argv := object())`; compare | IN: NamedExpr tracked and clears | NO_RAISE → NO_RAISE | SOLID |
| a6 `for argv in ...`, a7 `with ... as argv`, a8 `except ... as argv`, a10 comprehension target | not among listed covered binding forms; not enumerated in stated-limit list | Each keeps the original seeded `argv`: RAISE → RAISE | INFO. The comment declares only Assign/AnnAssign/AugAssign/NamedExpr, so these are untracked/rebinding-blind by design of the finite model; no such C use exists. |
| a9 `import os as argv` without a parameter | same untracked import-as form | NO_RAISE → NO_RAISE, because `argv` begins unbound; a focused parameter version would retain the parameter seed | INFO, same finite-domain limit. |
| a11 global/nonlocal | explicit stated limit | Valid global source (`global argv; argv = object()`) COMPILES and gives NO_RAISE; valid nested `nonlocal argv; argv = object()` COMPILES and gives RAISE at the outer comparison. | INFO/UNVERIFIED outside frozen domain. The model tracks the plain assignment syntactically but deliberately lacks global/nonlocal scope semantics; no C use. |
| a12 nested function rebinds `argv`, outer parameter compared | IN for the outer direct scope; nested closure handling is stated OUT | RAISE → RAISE (outer parameter remains derived; nested scope did not alter outer analysis state) | SOLID for outer inventory; closure propagation intentionally not claimed. |
| a13 use before later assignment (`return value == argv`; later `argv = object()`) | IN: source-order last binding *at the use* | RAISE → RAISE | SOLID |
| b1 kwonly `pin=PINNED_TEE_PATH`; b1b `other=None` | IN: kw_defaults paired; None not seeded | pin RAISE → RAISE; other NO_RAISE → NO_RAISE | SOLID |
| b2 required kwonly `pin` | IN: `kw_default is None` is not seeded | NO_RAISE → NO_RAISE | SOLID |
| b3 kwonly default module alias; b4 kwonly default helper call | IN: globals/helpers resolve defaults | each RAISE → RAISE | SOLID |
| b5 **`argv` varkey | parameter seed explicitly excludes `args.kwarg` | focused trace: NO_RAISE → NO_RAISE | SOLID. My initial driver accidentally used required kwonly `argv`, which is intentionally seeded and correctly raised; corrected focused trace distinguishes it. |
| c1 combined posonly+args+kwonly: `b` and `d` | IN: trailing positional alignment plus kwonly defaults | b RAISE → RAISE; d RAISE → RAISE | SOLID |
| c1c `a` / c2 `c` / c4 zero defaults | IN: only default-bound params seed; `-0` slicing edge | a NO_RAISE → NO_RAISE; c RAISE → RAISE; zero-default a NO_RAISE → NO_RAISE | SOLID |
| c3 lambda `a, /, b=PINNED_TEE_PATH` | IN: nested lambda and posonly default | RAISE → RAISE | SOLID |
| d1 `elif pin`, d2 `while not pin`, d3 `assert pin, msg`, d4 `1 if pin else 2`, d5 `if not (pin)` | IN: If/While/Assert/IfExp/Not whole-test/operand paths | each RAISE → RAISE | SOLID |
| d6 If inside try / for / with bodies | IN: generic visitor reaches nested bodies | each RAISE → RAISE | SOLID |
| d7 `if (x := pin):` (also operand constant/local variants) | comment says a derived value as whole `If.test`; function walrus is not in stated OUT list | **RAISE → NO_RAISE** for all three variants | FOLLOW-UP F1 (details below) |
| d8 `pin` in `IfExp.body`, not its test | IN: only `IfExp.test` claimed | NO_RAISE → NO_RAISE | SOLID |
| d9 `if bool(pin)`, d10 `if h.pin`, d11 `if p[0]` | explicit OUT: boolean calls, attribute hops, subscript/container hops | each NO_RAISE → NO_RAISE | SOLID and honestly bounded |
| d12 `pin = helper()` then `if pin` | IN: all-derived-return helper feeds whole If.test | RAISE → RAISE | SOLID |
| d13 `if pin` inserted in `_pinned_process_count` | special classifier excluded at T:3578 | Injection reached the earlier strict structural guard before boolean inventory. | INFO. T:3205's `ast.unparse(return_node.value.func)` and T:3230's `pins.is_pinned_argv` enforce the one-Return classifier contract, so a direct truth-test body is already red at the tighter structural contract. |

Initial driver summary: 36/40 exact expectation comparisons. The four provisional mismatches were: a11 (my input was invalid Python and outside stated global/nonlocal limit), b5 (my initial source accidentally chose a required kwonly rather than the requested `**argv`; focused trace corrected it), d7 (real F1), and d13 (tighter classifier structural contract fires before the skipped inventory). No mismatch was concealed.

### F1 — walrus `If.test` is a dormant test-model gap

Reproduction (focused trace): a normal derived `if p:` control raises `classifier-operand boolean-test inventory changed: [('f', 'p')]`; each `if (x := PINNED_TEE_PATH):`, `p = PINNED_TEE_PATH; if (x := p):`, and `def f(pin=PINNED_TEE_PATH): if (x := pin):` returns **NO_RAISE**. The mechanism is primary-source visible: `value_is_derived` recognizes `ast.NamedExpr` (T:3317-3318), `record_boolean_context` appends the `If.test` (T:3365-3369, T:3399-3401), but the final boolean inventory filters it out because T:3580-3585 admits only `Name`, `Call`, `UnaryOp`, and `IfExp`, not `NamedExpr`.

Canonical C-path check: `grep -nE ':=' proofs/S0-01/check_acp_conformance.py` printed `(none)`; an AST walk found no `If`/`While`/`Assert` whose test is a `NamedExpr`. Thus F1 **does not reproduce through the exact current production consumer**, has no material effect on C's output/evidence at the PIN, and is not an in-boundary blocker despite contradicting broad wording in the finite test-model comment/docstring. Predicate: contract mapping yes (wording), canonical reproduction **no**, material effect **no**, concrete discriminator yes (the focused injection), task ownership yes. Classification: **FOLLOW-UP**, coordinator should create the required `verify-followup` item under D-034. Suggested fix: either include `ast.NamedExpr` in the downstream boolean inventory with a focused regression or narrow the wording to list supported If.test node shapes.

### Parameter and `argv` audit

Commands: `graft ask "which functions take a parameter named argv" --in proofs/S0-01/check_acp_conformance.py` and `grep -nE 'def .*\\bargv\\b' proofs/S0-01/check_acp_conformance.py`. Graft's lexical summary had false context matches, but grep and AST inspect give one true C parameter: `main(argv)` at C:1879. `main` uses `argv[1:]` at C:1883 only; that is a subscript hop, explicitly OUT. The static model seeds this ordinary parameter as derived but it never becomes an inventoried bare boolean/comparison operand, so there is no current false positive.

Every C binding whose target/parameter is `argv`:
- C:1185 `argv` is the `Assign` target in `check_config_echo`; it holds argv.txt lines rather than a classifier operand. The model clears it (state false). The `if` at C:1186 is therefore correctly un-inventoried.
- C:1879 `main(argv)`: function parameter; model seeds it as the reserved operand, but C:1883 consumes only `argv[1:]`, an explicit subscript limit. No classifier inventory contribution.
- C:1932 `sys.argv`: attribute, not a bare `argv` binding; explicit attribute-hop limit.

### `check_config_echo` and frozen inventory delta

C:1185's `argv` is the local argv.txt line list, not the classifier operand. `python ../scratch/a5q_item3_inventories.py` instrumented each model only in memory and printed:

```
INVENTORY PIN-2e02afd actual_compares [('check_env', "env.get('S0_01_AGENT') != PINNED_AGENT_REALPATH"), ('check_process_evidence', "cmd.split(' ')[0] == PINNED_BUZZ_ACP_EXE_REALPATH")]
INVENTORY PIN-2e02afd actual_predicates [('check_process_evidence', 'PINNED_AGENT_REALPATH in cmd'), ('check_process_evidence', 'PINNED_AGENT_REALPATH not in agent_lines[0][3]'), ('check_process_evidence', 'PINNED_BUZZ_ACP_EXE_REALPATH in cmd'), ('check_process_evidence', 'PINNED_TEE_PATH in cmd'), ('check_process_evidence', 'PINNED_TEE_PATH not in tee_lines[0][3]')]
INVENTORY PIN-2e02afd actual_boolean_tests []
INVENTORY BASE-236bec7 actual_compares [('check_env', "env.get('S0_01_AGENT') != PINNED_AGENT_REALPATH"), ('check_process_evidence', "cmd.split(' ')[0] == PINNED_BUZZ_ACP_EXE_REALPATH")]
INVENTORY BASE-236bec7 actual_predicates [('check_config_echo', "'--idle-timeout' not in argv"), ('check_config_echo', "'--max-turn-duration' not in argv"), ('check_process_evidence', 'PINNED_AGENT_REALPATH in cmd'), ('check_process_evidence', 'PINNED_AGENT_REALPATH not in agent_lines[0][3]'), ('check_process_evidence', 'PINNED_BUZZ_ACP_EXE_REALPATH in cmd'), ('check_process_evidence', 'PINNED_TEE_PATH in cmd'), ('check_process_evidence', 'PINNED_TEE_PATH not in tee_lines[0][3]')]
```

The **only** model-inventory difference is the two `check_config_echo` false rows removed from `actual_predicates`; `actual_compares` is byte-for-byte equal. PIN boolean inventory is the expected empty set. SOLID.

Blocking? F1 no (fails canonical-path and material-effect predicate clauses); other hostile shapes no. All claimed IN cases except F1 behaved as claimed; all declared OUT cases stayed untracked; inventories prove only the intended two C rows moved.

## Item 4 — scratch-only mutation audit

Command: `python ../scratch/a5q_mutation_audit.py` after `git archive 2e02afd` per mutant. Every mutant tree changed T only, then passed `python -m py_compile` (rc=0) and `pytest --collect-only` (rc=0; exactly one selected test collected) before its killer run. Every killer ended `1 failed`; the script removed the tree before continuing and ended `MUTATION AUDIT COMPLETE: 10/10 killed; all mutant trees deleted`. The live tree remained clean (`git status --porcelain` empty).

| Mutant | Named killer | Exact killer assertion/result | Grade |
|---|---|---|---|
| M1 complete pre-A5q A5P-02 model: raw reserved spelling before binding state; parameter seeding removed; two old `check_config_echo` predicate rows restored | `test_ck16_a5p02_local_rebind_of_reserved_name_clears` | `AssertionError: classifier-operand comparison inventory changed: [('argv_local', 'value == argv')]`; `1 failed, 467 deselected in 0.38s` | killed |
| M2 delete kwonly `kw_defaults` pairing | `test_ck16_a5p03_kwonly_default_seeds_derived` | `Failed: DID NOT RAISE AssertionError`; `1 failed, 467 deselected in 0.32s` | killed |
| M3 `positional = args.args` | `test_ck16_a5p04_posonly_defaults_align_to_trailing_params` | `AssertionError: classifier-operand comparison inventory changed: [('posonly_align', "value == 'x'")]`; `1 failed, 467 deselected in 0.38s` | killed |
| M4 suppress new If/While/Assert/IfExp/Not inventory and remove final boolean assertion | `test_ck16_a5p05_bare_truth_test_is_a_boolean_context` | `Failed: DID NOT RAISE AssertionError`; `1 failed, 467 deselected in 0.30s` | killed |
| N1 seed every normal parameter | real C-contract test `test_ck16_checker_inventories_classifier_operand_predicates_module_wide` | comparison inventory assertion lists false positives (for example `('check_bundle', 'timeout_s is not None')`); `1 failed, 467 deselected in 0.40s` | killed |
| N2 record every boolean context without `value_is_derived` | real C-contract test `test_ck16_checker_inventories_classifier_operand_predicates_module_wide` | comparison inventory assertion reports broad non-derived C comparisons; `1 failed, 467 deselected in 0.36s` | killed |
| N3 make reserved-name lookup default true when unbound | new scratch killer `test_verify_mutant_reserved_unbound_default` | `AssertionError: classifier-operand comparison inventory changed: [('f', 'value == argv')]`; `1 failed, 471 deselected in 0.32s` | killed |
| N4 skip `If`/`While` `orelse` | real C-contract test `test_ck16_checker_inventories_classifier_operand_predicates_module_wide` | missing required `('check_process_evidence', "cmd.split(' ')[0] == PINNED_BUZZ_ACP_EXE_REALPATH")`; `1 failed, 467 deselected in 0.35s` | killed |
| N5 treat every UnaryOp as a boolean context | new scratch killer `test_verify_mutant_all_unary_ops` | `AssertionError: classifier-operand boolean-test inventory changed: [('f', 'pin')]`; `1 failed, 471 deselected in 0.36s` | killed |
| N6 pair positional defaults to prefix, not trailing parameters | new scratch killer `test_verify_mutant_positional_prefix` | `AssertionError: classifier-operand comparison inventory changed: [('f', "a == 'x'")]`; `1 failed, 471 deselected in 0.32s` | killed |

SOLID. Blocking? No. All requested M1–M4 and all six independent new-code mutants compiled, collected, and died under a concrete deterministic discriminator. None survived. The mutations run only against git-archive scratch copies; the production C was never mutated.

## Item 5 — de-vacuous named-test pass

Command: `python ../scratch/a5q_devacuous.py`. Each scratch archive flipped the named test's own expected outcome, compiled and collected one selected test, then ran it. Exact output: all five produced `compile rc=0; collect rc=0; run rc=1`, `1 failed, 467 deselected`, and `DE-VACUOUS COMPLETE: 5/5 own-expectation flips red; all scratch trees deleted`.

- A5P-01 expected RAISE instead of NO_RAISE → own `pytest.raises` assertion: `Failed: DID NOT RAISE AssertionError` (0.30s).
- A5P-02 expected RAISE instead of NO_RAISE → own `pytest.raises` assertion: `Failed: DID NOT RAISE AssertionError` (0.30s).
- A5P-03 expected NO_RAISE instead of RAISE → direct contract call: `classifier-operand comparison inventory changed: [('kwonly_pin', 'value == pin')]` (0.33s).
- A5P-04 swaps both branch expectations → `Failed: DID NOT RAISE AssertionError` at the changed own branch (0.30s).
- A5P-05 expected NO_RAISE instead of RAISE → direct contract call: `classifier-operand boolean-test inventory changed: [('truth_contexts', 'assert_pin'), ('truth_contexts', 'if_pin'), ('truth_contexts', 'ifexp_pin'), ('truth_contexts', 'not_pin'), ('truth_contexts', 'while_pin')]` (0.34s).

A5P-01 control power: none of the ten A5q-targeted mutant set is killed **only** by A5P-01; M1–M4 die at their associated regression and N1–N6 die at real-C or independently designed scratch killers. Therefore A5P-01 remains a non-vacuous regression guard for the earlier A5o V1 ordinary-alias-rebind repair (`test_ck16_a5p01_ordinary_alias_rebind_control_is_not_classifier_operand`), not a unique A5q discriminator. SOLID. Blocking? No.

## Item 6 — PIN gates and hygiene

Declared PC environment on every pytest run:
`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`, `/home/rocco/venv-agent-factory/bin` first in `PATH`.

Two independent direct xdist gates (same two-file set, separate absolute short basetemps):

```
python -m pytest -n 4 -q -p no:cacheprovider --basetemp /home/rocco/agent-factory/.lanes/pc-verify-a5q.md--2e02afd/scratch/bt/gate1 tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_spec_runner.py
483 passed in 114.02s (0:01:54)

python -m pytest -n 4 -q -p no:cacheprovider --basetemp /home/rocco/agent-factory/.lanes/pc-verify-a5q.md--2e02afd/scratch/bt/gate2 tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_spec_runner.py
483 passed in 107.58s (0:01:47)
```

Both are deterministic on count: 483/483 passed. `python -m pyflakes tests/test_s0_01_check_acp_conformance.py` → `pyflakes rc=0`.

`python3 scripts/ap_screen.py --tests tests/test_s0_01_check_acp_conformance.py` exact final block:

```
--- TEST_SCREEN over 1 path(s): 4 hits over 1 files ---
AP-66: 2
    tests/test_s0_01_check_acp_conformance.py:88: nv._point_mul = _cached_pm
    tests/test_s0_01_check_acp_conformance.py:90: nv._point_mul = _orig_pm
AF-AP-48: 1
    tests/test_s0_01_check_acp_conformance.py:6378: assert all(site[3] in {"walk", "require_regular_file", "stdin", "consumer"}
AF-AP-57: 1
    tests/test_s0_01_check_acp_conformance.py:5821: if call_count[0] == 2:
```

All four are the known pre-existing hits outside A5q's first/last hunk bounds: AP-66 test monkeypatch/restore at T:88/90 (`nv._point_mul`), AF-AP-57 deterministic second-call fault injection at T:5821 (`call_count`), AF-AP-48 finite call-site category assertion at T:6378 (`site`). New A5q-screen hits: 0. `git diff --check` and `git status --porcelain` both returned clean. Scratch mutation/de-vacuous trees: none remaining.

SOLID. Blocking? No. Gates ran, counts were nonzero and agree, static lint passed, and hygiene is clean.

## Item 7 — exhaustive A5q-hunk review

Reviewed all 11 hunks in `git diff 236bec7 2e02afd -- T`: the finite-model comment/binding state (`reserved_operand_names`); `analyze_body` and helper passes; frozen `allowed_compares`/`allowed_predicates`/`allowed_boolean_tests`; the contract-test docstring; and named A5P regressions. No additional current-C defect found. The only meaningful observation within the revised model's claimed domain is F1 (NamedExpr `If.test`) above; it is a non-blocking FOLLOW-UP because C has no walrus and cannot reproduce the effect at the PIN.

## Finding inventory

1. FOLLOW-UP — **F1, walrus `If.test` escapes downstream boolean inventory.** Evidence: SOLID static injection plus direct T mechanism: `ast.NamedExpr` at T:3317, `record_boolean_context` at T:3365, the `ast.Name`/`ast.Call` downstream filter at T:3580, and the T:3281 boolean-context comment containing `If / While / Assert`. Contract mapping: broad boolean-context wording. Canonical production path: **not reproduced** — C has no `:=`. Material effect: none on C PIN bytes. Discriminator: focused injected `if (x := pin):` returns NO_RAISE where plain `if pin:` raises. Ownership: T/A5q model. Suggested disposition: D-034 `verify-followup` issue; either inventory `NamedExpr` or narrow the language.

2. INFO — **shared-branch base drift changes D2 literal output.** Evidence: SOLID git range checks in item 1. Contract mapping: none to A5q behavior. Canonical path: N/A. Material effect: no A5q production/test surface change. Reproduction: `git diff --stat 236bec7 2e02afd -- tests/`. Suggested fix: future targeted briefs should compare the repair commit to its actual parent or allow an explicitly named shared-branch exception.

3. INFO — **untracked rebind forms are only partially declared.** `for`/`with`/`except`/comprehension/import targets do not clear a seeded reserved `argv`; all retain the seed in the test-side model. Evidence: hostile shapes a6-a10. Contract mapping: no current C instance; finite covered list itself names only four binding forms. Canonical path: not reproduced. Material effect: none at PIN. Suggested fix: document the remainder as stated limits if clarity is required; do not widen this increment.

No BLOCKER. No CONTRACT-DEFECT. All other hostile observations are SOLID as tabulated; a11 is a valid but explicitly OUT global/nonlocal probe and is INFO/UNVERIFIED for the frozen domain, not misreported as a defect.

## DISCREPANCIES

- D2's literal base-range assertion is false because the range includes independent S0-02 B6 commit `c439580`, which adds `tests/test_s0_02_buzz_authz.py`. A5q itself is cleanly T-only versus actual parent `78745d3`; details in item 1.
- The brief's command said `grep -n 'def .*\bargv\b'`. GNU grep's basic-regex `\b` behavior did not find C:1879 `def main(argv) -> int:`; `grep -nE 'def .*\bargv\b'` did. The conclusion was independently confirmed by AST parsing, and no source/configuration was changed.
- Item 3 initial a11 used a syntactically invalid `global argv` after parameter form. I excluded that invalid input, then ran valid compiled global and nonlocal forms; their measured static outcomes are in the shape table. They remain outside the stated global/nonlocal domain and are not product proof.
- Item 3 initial b5 accidentally used a required kwonly `argv`, not the brief's `**argv`; focused rerun measured `**argv` NO_RAISE and the report corrects the row. This is a verifier-driver input correction, not a product finding.
- Item 4's first M1 reconstruction left `parameter_seeds` calling a removed variable and caused NameError; that was a bad mutant, not a compiled/collected result. I discarded it, reconstructed the complete pre-A5q model (including removing parameter seeding and restoring old entries), then re-ran. The final M1 compiled, collected, and died at the named regression assertion.
- `graft ask` reports lexical/context hits that include `check_runtime_identity`, `check_config_echo`, and `_pinned_process_count` when asked for argv *parameters*. Exact grep and an AST walk resolve the actual C parameter set; no claim rests on graft's false context lines.
- `report_lint` final bounded run: `report_lint: 28 refs — OK 23, NEAR 2, MISS 0, UNCHECKABLE 3, UNRESOLVED 0 (worktree)`; floor 12 satisfied. The three UNCHECKABLE rows are verbatim AP-screen evidence lines, and the two NEAR rows are T:3281 `If / While / Assert` comment tokens on adjacent report lines. No third repair round is needed because MISS is 0.

## NOT-done

- Not committed, pushed, tagged, posted, or otherwise acted outward.
- Not a final gate verdict; coordinator owns that decision.
- F1 not fixed here (verify lane is read-only) and requires a D-034 follow-up issue if accepted.
- The stated finite-domain limits remain unfixed: boolean calls, container/subscript/attribute hops, global/nonlocal, path sensitivity, and unlisted rebinding forms. No current C path uses them.
- The valid global/nonlocal controls were run after the initial invalid a11 input; their different static results are recorded, but both are explicitly outside the frozen domain. No current C path uses `global` or `nonlocal`.

## GATE RECOMMENDATION

**MERGE-READY-WITH-FOLLOWUPS.** No finding meets the complete blocker predicate: all original issue #8 cases match contract; all four repair families survive independent hostile shapes; all 10 compiling/collecting mutants die; all five named tests red when their own expectations flip; and the two PIN gates report `483 passed` twice with pyflakes rc=0. F1 is a real but dormant test-model wording/coverage gap: it is contract-mapped only at the broad static claim, has a deterministic scratch discriminator, but **does not reproduce through current C and has no material PIN effect**. It is a D-034 `verify-followup`, not a NOT-READY blocker.

retro: nothing to bake; no general reusable workflow lesson beyond the already-recorded complete-mutant requirement.
