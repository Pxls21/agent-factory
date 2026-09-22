# VERIFY-A5q — independent adversarial verification of issue #8 (CK16 classifier-operand meta-oracle sweep)

Role: adversarial-verifier (LOCAL Qwen verify route, `agentfactory-verify-local`). PIN: 2e02afd. Base: 236bec7.
Venue: pc (tasks/briefs/pc/VENUE-MAP.md). This lane VERIFIES; it never fixes. It emits a GATE RECOMMENDATION, never a verdict.

## Item 1 — premise

Commands (all from the lane tree, PIN 2e02afd):
- `git diff --stat 236bec7 2e02afd -- proofs/ tests/test_s0_01_spec_runner.py scripts/proof-runner scripts/validate-ledger` → **empty** (no output, rc=0). C/P/S/proof-runner/validate-ledger byte-identical.
- `git diff --stat 236bec7 2e02afd -- tests/` → **names TWO files**: `tests/test_s0_01_check_acp_conformance.py` (+246/−15) and `tests/test_s0_02_buzz_authz.py` (+171/−0).
- `sha256sum tests/test_s0_01_check_acp_conformance.py` → **75fad3cd77ce3fa41baf2bccfdaa061d1def2472af4587d572b23d14e74a996e** (matches the brief's expected hash exactly).
- Hunk-boundary check: the diff produced **11 hunk headers**; the first/last and G2 range are named in the command output only, rather than cited as T source coordinates. **No hunk falls inside the G2 region.**

DISCREPANCY (item 1, D2): the brief said `git diff --stat 236bec7 2e02afd -- tests/` “must name only T”. Measured output names T PLUS `tests/test_s0_02_buzz_authz.py`. Bounded disambiguation (3 experiments):
- `git merge-base --is-ancestor 236bec7 2e02afd` → 236bec7 IS an ancestor of 2e02afd.
- `git log --oneline 236bec7..2e02afd` → 16 commits in the range. The extra test file was added by `c439580 S0-02 B6 LANDED (issue #3)` — a DIFFERENT increment (S0-02, not S0-01) that landed on the shared branch between A5q’s base (236bec7) and A5q’s parent (78745d3).
- `git diff --stat c439580 2e02afd -- tests/test_s0_02_buzz_authz.py` → empty (A5q did not touch that file); `git log --oneline 236bec7..78745d3 -- tests/test_s0_01_check_acp_conformance.py` → empty (T untouched by every intervening increment, so A5q’s T-diff is identical vs either 236bec7 or 78745d3); `git diff --stat 78745d3 2e02afd -- tests/` → names ONLY T.

Conclusion: the extra file is **shared-branch base drift** (S0-02 B6), not an A5q change to the production surface. A5q’s own commit (2e02afd vs its real parent 78745d3) touches ONLY T; C/P/S/proof-runner/validate-ledger and the S0-01 mint are byte-identical to 236bec7. The item-1 premise — “A5q touched T only and left the production spine intact” — is TRUE at the level that matters for this round. I build on the measured truth and log the D2 wording as a DISCREPANCY rather than stopping with CONTRACT-INVALID.

S0-01 mint/production byte-identity (base 236bec7 vs PIN 2e02afd), measured:
- `proofs/S0-01/result.json`: bb98b1a4… identical
- `proofs/S0-01/check_acp_conformance.py` (C): `868b8705699b5e78b1468252ecbdec93736d2a7e2f4819424311c31c243db46a` (identical)
- `proofs/S0-01/pins.py` (P): `1a2f9a38ddba14e3ea75c06e77e43083a059e8dc5caf5499c7e54e9013921981` (identical)

SOLID. Blocking? No. The premise’s substantive checks pass. The single D2 wording mismatch is a non-blocking discrepancy from a sibling increment, not an A5q defect.

## Item 2 — original issue-#8 cases + named-test collection

I rebuilt an independent scratch driver (`../scratch/a5q_item2_driver.py`) that imports the PIN’s real `_assert_ck16_classifier_operand_contract`, injects the original issue shapes ahead of C’s exact `def _pinned_process_count(commands):` anchor, and executes each static C-contract analysis. It does not invoke the builder’s five tests as its oracle.

Command:

`python ../scratch/a5q_item2_driver.py`

Exact output:

```text
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

A5P-01 is the issue’s A5o-V1 control: ordinary `pin` starts derived then rebinds to `'literal'`, and the later `value == pin` stays **NO_RAISE**. A5P-02 uses a reserved `argv` parameter then locally rebinds it to `object()` and stays **NO_RAISE**. A5P-03 (derived kwonly default), A5P-04 (`value == pin`), A5P-04b (`pin == 'x'`), and A5P-05 (`if pin:`) each raise the relevant frozen inventory assertion; A5P-04a (`value == 'x'`) stays **NO_RAISE**. All seven observed outcomes match the explicit contract.

Named-test command:

`python -m pytest -q -p no:cacheprovider --basetemp ../scratch/bt/a5p tests/test_s0_01_check_acp_conformance.py -k a5p0`

Exact output: `5 passed, 463 deselected in 1.12s`.

SOLID. Blocking? No: all contract rows reproduce against the actual PIN model and exact C-copy path. Predicate: contract mapping yes; canonical model consumer yes; material effect yes; concrete discriminator yes; task ownership yes. No finding.

## Item 3 — new hostile shapes, C audit, and inventories

Method: `python ../scratch/a5q_item3_driver.py` injects each NEW shape ahead of C’s `_pinned_process_count` anchor, executes the PIN’s actual `_assert_ck16_classifier_operand_contract`, and compares its observed `RAISE`/`NO_RAISE` against the expectation written from the comment/docstring before the run. `python ../scratch/a5q_item3_trace.py` then localized the four initially flagged cases. This is a static model, so each injection has no runtime effect on the checker.

| Shape(s) | Claimed domain | Expected → observed | Grade |
|---|---|---|---|
| a1 module `argv = PINNED_TEE_PATH`; `value == argv` | IN: module alias visible at definition | RAISE → RAISE | SOLID |
| a2 module `argv = []`; `value == argv` | IN: module rebind clears | NO_RAISE → NO_RAISE | SOLID |
| a3 parameter `argv`; `argv += object()`; compare | IN: AugAssign tracked | RAISE → RAISE. AugAssign preserves derivedness because its pre-binding is derived. | SOLID |
| a4 parameter `argv`; `argv: int = object()`; compare | IN: AnnAssign tracked and clears | NO_RAISE → NO_RAISE | SOLID |
| a5 parameter `argv`; `(argv := object())`; compare | IN: NamedExpr tracked and clears | NO_RAISE → NO_RAISE | SOLID |
| a6 `for argv`, a7 `with … as argv`, a8 `except … as argv`, a10 comprehension target | Not among listed covered binding forms | Each keeps the original seeded `argv`: RAISE → RAISE | INFO. The finite model names only Assign/AnnAssign/AugAssign/NamedExpr. No C use exists. |
| a9 `import os as argv` without a parameter | Same untracked import-as form | NO_RAISE → NO_RAISE, because `argv` begins unbound | INFO |
| a11 global/nonlocal | Explicit stated limit | Valid global source compiles and gives NO_RAISE; valid nested nonlocal source compiles and gives RAISE at the outer comparison. | INFO/UNVERIFIED outside frozen domain. |
| a12 nested function rebinds `argv`, outer parameter compared | IN for outer direct scope; closure handling OUT | RAISE → RAISE | SOLID for outer inventory |
| a13 use before later assignment | IN: source-order binding at use | RAISE → RAISE | SOLID |
| b1 kwonly derived default; b1b `other=None` | IN: kw_defaults paired; None not seeded | pin RAISE → RAISE; other NO_RAISE → NO_RAISE | SOLID |
| b2 required kwonly `pin` | IN: no default, not seeded | NO_RAISE → NO_RAISE | SOLID |
| b3 module-alias kwonly default; b4 helper-call kwonly default | IN: globals/helpers resolve defaults | each RAISE → RAISE | SOLID |
| b5 `**argv` varkey | Parameter seed excludes `args.kwarg` | NO_RAISE → NO_RAISE | SOLID |
| c1 combined posonly+args+kwonly: `b` and `d` | IN: trailing alignment plus kwonly defaults | RAISE → RAISE each | SOLID |
| c1c `a`; c2 `c`; c4 zero defaults | IN: only default-bound params seed | a NO_RAISE → NO_RAISE; c RAISE → RAISE; zero-default a NO_RAISE → NO_RAISE | SOLID |
| c3 lambda `a, /, b=PINNED_TEE_PATH` | IN: nested lambda and posonly default | RAISE → RAISE | SOLID |
| d1 `elif pin`, d2 `while not pin`, d3 `assert pin, msg`, d4 `1 if pin else 2`, d5 `if not (pin)` | IN: whole boolean-test paths | each RAISE → RAISE | SOLID |
| d6 If inside try / for / with bodies | IN: generic visitor reaches nested bodies | each RAISE → RAISE | SOLID |
| d7 `if (x := pin):` | Comment claims a derived whole `If.test`; function walrus not stated OUT | **RAISE → NO_RAISE** | FOLLOW-UP F1 |
| d8 `pin` in `IfExp.body`, not its test | IN: only `IfExp.test` claimed | NO_RAISE → NO_RAISE | SOLID |
| d9 `if bool(pin)`, d10 `if h.pin`, d11 `if p[0]` | Explicit OUT | each NO_RAISE → NO_RAISE | SOLID |
| d12 helper-derived `pin` reaches `If.test` | IN | RAISE → RAISE | SOLID |
| d13 `if pin` inserted in `_pinned_process_count` | Special classifier excluded at T:3578 | Earlier strict structural guard fires before boolean inventory | INFO. T:3205’s `ast.unparse(return_node.value.func)` and T:3230’s `pins.is_pinned_argv` enforce the classifier contract. |

Initial driver summary: 36/40 exact expectation comparisons. The provisional mismatches were a11 (initial invalid global input), b5 (initially used required kwonly rather than `**argv`), d7 (F1), and d13 (tighter structural contract fires first). No mismatch was concealed.

### F1 — walrus `If.test` is a dormant test-model gap

Reproduction: a normal derived `if p:` control raises `classifier-operand boolean-test inventory changed: [('f', 'p')]`; each `if (x := PINNED_TEE_PATH):`, `p = PINNED_TEE_PATH; if (x := p):`, and `def f(pin=PINNED_TEE_PATH): if (x := pin):` returns **NO_RAISE**.

Mechanism: `value_is_derived` recognizes `ast.NamedExpr` at T:3317-3318; `record_boolean_context` appends the `If.test` at T:3365-3369 and T:3399-3401; but the downstream boolean inventory accepts only `Name`, `Call`, `UnaryOp`, and `IfExp` at T:3580-3585. It drops `NamedExpr`.

Canonical C-path check: `grep -nE ':=' proofs/S0-01/check_acp_conformance.py` printed `(none)`; an AST walk found no `If`/`While`/`Assert` whose test is a `NamedExpr`.

F1 **does not reproduce through the exact current production consumer** and has no material effect on C output/evidence at the PIN. Predicate: contract mapping yes at wording level; canonical reproduction no; material effect no; concrete discriminator yes; task ownership yes.

Classification: **FOLLOW-UP**. Suggested follow-up: either include `ast.NamedExpr` in the downstream boolean inventory with a focused regression or narrow the wording to list supported `If.test` node shapes.

### Parameter and `argv` audit

Commands:

```text
graft ask "which functions take a parameter named argv" --in proofs/S0-01/check_acp_conformance.py
grep -nE 'def .*\bargv\b' proofs/S0-01/check_acp_conformance.py
```

Graft’s lexical summary included false context matches, but grep and AST inspection establish one true C parameter: `main(argv)` at C:1879. `main` uses `argv[1:]` at C:1883 only; that is a subscript hop, explicitly OUT. The static model seeds this parameter but it never becomes an inventoried bare boolean/comparison operand.

Every C binding whose target/parameter is `argv`:
- C:1185 `argv` is the `Assign` target in `check_config_echo`; it holds argv.txt lines rather than a classifier operand. The model clears it. The `if` at C:1186 is correctly un-inventoried.
- C:1879 `main(argv)`: the model seeds it, but C:1883 uses only `argv[1:]`, an explicit subscript limit.
- C:1932 `sys.argv`: attribute, not a bare `argv` binding; explicit attribute-hop limit.

### `check_config_echo` and frozen inventory delta

C:1185’s `argv` is the local argv.txt line list, not the classifier operand. `python ../scratch/a5q_item3_inventories.py` instrumented each model only in memory and printed:

```text
INVENTORY PIN-2e02afd actual_compares [('check_env', "env.get('S0_01_AGENT') != PINNED_AGENT_REALPATH"), ('check_process_evidence', "cmd.split(' ')[0] == PINNED_BUZZ_ACP_EXE_REALPATH")]
INVENTORY PIN-2e02afd actual_predicates [('check_process_evidence', 'PINNED_AGENT_REALPATH in cmd'), ('check_process_evidence', 'PINNED_AGENT_REALPATH not in agent_lines[0][3]'), ('check_process_evidence', 'PINNED_BUZZ_ACP_EXE_REALPATH in cmd'), ('check_process_evidence', 'PINNED_TEE_PATH in cmd'), ('check_process_evidence', 'PINNED_TEE_PATH not in tee_lines[0][3]')]
INVENTORY PIN-2e02afd actual_boolean_tests []
INVENTORY BASE-236bec7 actual_compares [('check_env', "env.get('S0_01_AGENT') != PINNED_AGENT_REALPATH"), ('check_process_evidence', "cmd.split(' ')[0] == PINNED_BUZZ_ACP_EXE_REALPATH")]
INVENTORY BASE-236bec7 actual_predicates [('check_config_echo', "'--idle-timeout' not in argv"), ('check_config_echo', "'--max-turn-duration' not in argv"), ('check_process_evidence', 'PINNED_AGENT_REALPATH in cmd'), ('check_process_evidence', 'PINNED_AGENT_REALPATH not in agent_lines[0][3]'), ('check_process_evidence', 'PINNED_BUZZ_ACP_EXE_REALPATH in cmd'), ('check_process_evidence', 'PINNED_TEE_PATH in cmd'), ('check_process_evidence', 'PINNED_TEE_PATH not in tee_lines[0][3]')]
```

The only model-inventory difference is the two `check_config_echo` false rows removed from `actual_predicates`; `actual_compares` is identical. PIN boolean inventory is the expected empty set.

Blocking? F1 no. It fails the canonical-path and material-effect predicate clauses. Other hostile shapes produced no blocker.

## Item 4 — scratch-only mutation audit

Command: `python ../scratch/a5q_mutation_audit.py`, using `git archive 2e02afd` per mutant.

Every mutant tree changed T only, passed `python -m py_compile` (rc=0), passed `pytest --collect-only` (rc=0; exactly one selected test), then ran one killer. Every killer ended `1 failed`; each scratch tree was removed. Final line:

```text
MUTATION AUDIT COMPLETE: 10/10 killed; all mutant trees deleted
```

| Mutant | Named killer | Exact killer assertion/result | Grade |
|---|---|---|---|
| M1 complete pre-A5q A5P-02 model | `test_ck16_a5p02_local_rebind_of_reserved_name_clears` | `classifier-operand comparison inventory changed: [('argv_local', 'value == argv')]`; `1 failed, 467 deselected in 0.38s` | killed |
| M2 delete kwonly `kw_defaults` pairing | `test_ck16_a5p03_kwonly_default_seeds_derived` | `Failed: DID NOT RAISE AssertionError`; `1 failed, 467 deselected in 0.32s` | killed |
| M3 `positional = args.args` | `test_ck16_a5p04_posonly_defaults_align_to_trailing_params` | `classifier-operand comparison inventory changed: [('posonly_align', "value == 'x'")]`; `1 failed, 467 deselected in 0.38s` | killed |
| M4 suppress new boolean-context inventory | `test_ck16_a5p05_bare_truth_test_is_a_boolean_context` | `Failed: DID NOT RAISE AssertionError`; `1 failed, 467 deselected in 0.30s` | killed |
| N1 seed every normal parameter | real C-contract test | False-positive inventory including `('check_bundle', 'timeout_s is not None')`; `1 failed, 467 deselected in 0.40s` | killed |
| N2 record every boolean context without `value_is_derived` | real C-contract test | Broad non-derived C comparisons enter inventory; `1 failed, 467 deselected in 0.36s` | killed |
| N3 default unbound reserved lookup to true | scratch killer | `classifier-operand comparison inventory changed: [('f', 'value == argv')]`; `1 failed, 471 deselected in 0.32s` | killed |
| N4 skip `If`/`While` `orelse` | real C-contract test | Required check-process comparison missing; `1 failed, 467 deselected in 0.35s` | killed |
| N5 treat every UnaryOp as boolean | scratch killer | `classifier-operand boolean-test inventory changed: [('f', 'pin')]`; `1 failed, 471 deselected in 0.36s` | killed |
| N6 pair positional defaults to prefix | scratch killer | `classifier-operand comparison inventory changed: [('f', "a == 'x'")]`; `1 failed, 471 deselected in 0.32s` | killed |

SOLID. Blocking? No. All requested M1–M4 and six independent new-code mutants compiled, collected, and died under concrete deterministic discriminators. None survived. Production C was never mutated.

## Item 5 — de-vacuous named-test pass

Command: `python ../scratch/a5q_devacuous.py`.

Each scratch archive flipped the named test’s own expected outcome, compiled and collected one selected test, then ran it. All five produced:

```text
compile rc=0; collect rc=0; run rc=1
1 failed, 467 deselected
DE-VACUOUS COMPLETE: 5/5 own-expectation flips red; all scratch trees deleted
```

- A5P-01 expected RAISE instead of NO_RAISE → `Failed: DID NOT RAISE AssertionError` (0.30s).
- A5P-02 expected RAISE instead of NO_RAISE → `Failed: DID NOT RAISE AssertionError` (0.30s).
- A5P-03 expected NO_RAISE instead of RAISE → `classifier-operand comparison inventory changed: [('kwonly_pin', 'value == pin')]` (0.33s).
- A5P-04 swaps both branch expectations → `Failed: DID NOT RAISE AssertionError` (0.30s).
- A5P-05 expected NO_RAISE instead of RAISE → `classifier-operand boolean-test inventory changed: [('truth_contexts', 'assert_pin'), ('truth_contexts', 'if_pin'), ('truth_contexts', 'ifexp_pin'), ('truth_contexts', 'not_pin'), ('truth_contexts', 'while_pin')]` (0.34s).

A5P-01 control power: none of the ten A5q-targeted mutants is killed only by A5P-01. It remains a non-vacuous regression guard for the earlier A5o V1 ordinary-alias-rebind repair, not a unique A5q discriminator.

SOLID. Blocking? No.

## Item 6 — PIN gates and hygiene

Declared PC environment on every pytest run:

```text
S0_01_VENUE=pc
S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden
S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz
```

`/home/rocco/venv-agent-factory/bin` was first in `PATH`.

Two independent direct xdist gates:

```text
python -m pytest -n 4 -q -p no:cacheprovider \
  --basetemp /home/rocco/agent-factory/.lanes/pc-verify-a5q.md--2e02afd/scratch/bt/gate1 \
  tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_spec_runner.py

483 passed in 114.02s (0:01:54)

python -m pytest -n 4 -q -p no:cacheprovider \
  --basetemp /home/rocco/agent-factory/.lanes/pc-verify-a5q.md--2e02afd/scratch/bt/gate2 \
  tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_spec_runner.py

483 passed in 107.58s (0:01:47)
```

Both are deterministic on count: **483/483 passed**.

`python -m pyflakes tests/test_s0_01_check_acp_conformance.py`:

```text
pyflakes rc=0
```

`python3 scripts/ap_screen.py --tests tests/test_s0_01_check_acp_conformance.py`:

```text
--- TEST_SCREEN over 1 path(s): 4 hits over 1 files ---
AP-66: 2
    tests/test_s0_01_check_acp_conformance.py:88: nv._point_mul = _cached_pm
    tests/test_s0_01_check_acp_conformance.py:90: nv._point_mul = _orig_pm
AF-AP-48: 1
    tests/test_s0_01_check_acp_conformance.py:6378: assert all(site[3] in {"walk", "require_regular_file", "stdin", "consumer"}
AF-AP-57: 1
    tests/test_s0_01_check_acp_conformance.py:5821: if call_count[0] == 2:
```

All four are known pre-existing hits outside A5q hunk bounds: AP-66 at T:88/90 (`nv._point_mul`), AF-AP-57 at T:5821 (`call_count`), AF-AP-48 at T:6378 (`site`). New A5q-screen hits: 0.

`git diff --check` and `git status --porcelain` both returned clean before the required untracked report artifact was written. Scratch mutation/de-vacuous trees: none remaining.

SOLID. Blocking? No.

## Item 7 — exhaustive A5q-hunk review

Reviewed all 11 hunks in `git diff 236bec7 2e02afd -- T`: finite-model comment/binding state (`reserved_operand_names`); `analyze_body` and helper passes; frozen `allowed_compares`/`allowed_predicates`/`allowed_boolean_tests`; contract-test docstring; and named A5P regressions.

No additional current-C defect found. The only meaningful observation inside the revised model’s claimed domain is F1. It is a non-blocking FOLLOW-UP because C has no walrus and cannot reproduce the effect at the PIN.

## Finding inventory

1. FOLLOW-UP — **F1, walrus `If.test` escapes downstream boolean inventory.**
   - Evidence: SOLID static injection plus T:3317 `ast.NamedExpr`, T:3365 `record_boolean_context`, T:3580 `ast.Name`/`ast.Call` filter, and the T:3281 comment containing `If / While / Assert`.
   - Contract mapping: broad boolean-context wording.
   - Canonical production path: **not reproduced** — C has no `:=`.
   - Material effect: none on C PIN bytes.
   - Discriminator: injected `if (x := pin):` returns NO_RAISE while plain `if pin:` raises.
   - Ownership: T/A5q model.
   - Suggested disposition: D-034 `verify-followup`; inventory `NamedExpr` or narrow the language.

2. INFO — **Shared-branch base drift changes D2 literal output.**
   - Evidence: SOLID git-range checks.
   - Contract mapping: none to A5q behavior.
   - Canonical path: N/A.
   - Material effect: no A5q production/test-surface change.
   - Suggested fix: future targeted briefs should compare repair commit to actual parent or allow an explicit shared-branch exception.

3. INFO — **Untracked rebind forms are only partially declared.**
   - `for`/`with`/`except`/comprehension/import targets do not clear a seeded reserved `argv`.
   - Evidence: hostile shapes a6-a10.
   - Canonical path: not reproduced.
   - Material effect: none at PIN.
   - Suggested fix: document these forms as stated limits if clarity is needed. Do not widen this increment.

No BLOCKER. No CONTRACT-DEFECT. a11 is a valid but explicitly OUT global/nonlocal probe and remains INFO/UNVERIFIED for the frozen domain.

## DISCREPANCIES

- D2’s literal base-range assertion is false because the range includes independent S0-02 B6 commit `c439580`, which adds `tests/test_s0_02_buzz_authz.py`. A5q itself is T-only versus actual parent `78745d3`.
- The brief’s `grep -n 'def .*\bargv\b'` did not find C:1879 `def main(argv) -> int:` under GNU basic regex. `grep -nE 'def .*\bargv\b'` did. AST parsing independently confirmed the conclusion.
- Item 3 initially used invalid `global argv` after a parameter form. I excluded it, then ran valid compiled global and nonlocal forms. Both remain outside the frozen domain.
- Item 3 initially used a required kwonly `argv`, not the required `**argv` varkey. Focused rerun measured `**argv` NO_RAISE. This corrected verifier-driver input, not product behavior.
- Item 4’s first M1 reconstruction left `parameter_seeds` referring to a removed variable and caused NameError. It was discarded as a bad mutant. The final M1 fully reconstructed the relevant pre-A5q behavior, compiled, collected, and died at the named assertion.
- `graft ask` returned lexical/context false matches for argv-parameter queries. Exact grep and AST inspection established the true C parameter set.
- `report_lint` final bounded run: `report_lint: 28 refs — OK 23, NEAR 2, MISS 0, UNCHECKABLE 3, UNRESOLVED 0 (worktree)`; floor 12 satisfied. The three UNCHECKABLE rows are verbatim AP-screen lines. The two NEAR rows are T:3281 comment tokens on adjacent report lines.

## NOT-done

- Not committed, pushed, tagged, posted, or otherwise acted outward.
- Not a final gate verdict; the coordinator owns that decision.
- F1 is not fixed here. This verify lane is read-only. It needs a D-034 follow-up issue if accepted.
- Stated finite-domain limits remain: boolean calls, container/subscript/attribute hops, global/nonlocal, path sensitivity, and unlisted rebinding forms. No current C path uses them.
- Valid global/nonlocal controls were run after the initial invalid a11 input. Their different static results are recorded, but both remain explicitly outside the frozen domain.

## GATE RECOMMENDATION

**MERGE-READY-WITH-FOLLOWUPS.**

No finding meets the complete blocker predicate. All original issue-#8 cases match contract; all four repair families survive independent hostile shapes; all 10 compiling/collecting mutants die; all five named tests red when their own expectations flip; and two PIN gates report **483 passed** twice with pyflakes rc=0.

F1 is real but dormant: it is contract-mapped only at broad static wording, has a deterministic scratch discriminator, but **does not reproduce through current C and has no material PIN effect**. It is a D-034 `verify-followup`, not a NOT-READY blocker.

retro: nothing to bake; no general reusable workflow lesson beyond the already-recorded complete-mutant requirement.
