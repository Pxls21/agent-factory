# PC lane — A5q (issue #8: the CK16 classifier-operand meta-oracle's four audited defects, closed in ONE sweep; T only)

PIN: 236bec7

Role: code-implementer. Route: the LOCAL Qwen build route (`agentfactory-build-local`; the pc_lane.sh default for
code-implementer — do NOT set HERMES_MODEL). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first. Report: draft after
EACH item at `tasks/briefs/s0-01-a5p-support/A5q-report.md`, return it whole as your final message. THREE sibling lanes
share this host tonight (VERIFY-G2 reads T at its own worktree; B6 owns `tests/test_s0_02_buzz_authz.py`; K1-c owns
`scripts/vendored_manifest.py` + `tests/test_vendored_manifest.py` + `sandbox-kit/VENDORED-MANIFEST.md`) — never touch
their files or trees. Owner authorization: this is defensive test-oracle work on the owner's own repository.

## Source (read WHOLE, in this order)
1. GitHub issue #8 (its text is reproduced below — the four executable cases and the required disposition).
2. `tasks/briefs/s0-01-a5p-support/A5p-report.md` (the round that built the model) and the meta-oracle itself in
   T = `tests/test_s0_01_check_acp_conformance.py`: `_assert_ck16_classifier_operand_contract` T:3190, the
   `Compare`/`BoolOp`-only inventory T:3239 and T:3353-3354, the membership/compare helpers T:3438-3473, the defaults
   binding `zip(args.args[-len(args.defaults):], args.defaults)` T:3309-3310, `_ck16_checker_copy` T:3493 (line
   numbers at the PIN — re-read them from the tree, they move as you edit).
3. The FROZEN production checker `proofs/S0-01/check_acp_conformance.py` (C) and `proofs/S0-01/pins.py` (P): READ-ONLY.
   The model must keep passing on C unchanged (C's source uses none of the hostile shapes).

## The four defects (from issue #8, each reproduced by the coordinator on 2026-09-21 against the real A5p model)
Each case is a hostile function injected ahead of `def _pinned_process_count(commands):` via `_ck16_checker_copy`, then
graded by `_assert_ck16_classifier_operand_contract` (RAISED = the contract flags a classifier-operand comparison).
| ID | Injected function | Contract expects | Observed at the PIN | Class |
|----|-------------------|------------------|---------------------|-------|
| A5P-02 | `def f(value, argv):\n    argv = object()\n    return value == argv` | NO finding (local `argv` rebound to a non-operand) | RAISED `('f', 'value == argv')` | false positive: the literal classifier-operand spelling is matched via `ast.unparse` before the source-order binding state is consulted |
| A5P-03 | `def f(value, *, pin=PINNED_TEE_PATH):\n    return value == pin` | finding (`pin` seeded derived via a keyword-only default) | NO_RAISE | false negative: `args.args`/`args.defaults` processed, `kwonlyargs`/`kw_defaults` not |
| A5P-04 | `def f(pin=PINNED_TEE_PATH, /, value=None):` with discriminators `return value == 'x'` (expect NO_RAISE) and `return pin == 'x'` (expect RAISED) | `pin` derived, `value` not | `value == 'x'` RAISED, `pin == 'x'` NO_RAISE | wrong-parameter binding: Python aligns `defaults` to the TRAILING parameters of `posonlyargs + args`; the model zips only `args.args` |
| A5P-05 | `def f(pin=PINNED_TEE_PATH):\n    if pin:\n        return True\n    return False` | finding (a derived value in a boolean context) | NO_RAISE | false negative: only `Compare`/`BoolOp` nodes are inventoried |
Control A5P-01 (an ordinary alias rebound) MATCHES the contract at the PIN and must keep matching.

## Items (in order; each: RED control first, then the fix, then the control green — paste every line)
1. PREMISE: reproduce all four on the PIN's T before touching anything — write the four cases as NAMED tests in T
   (`test_ck16_a5p02_local_rebind_of_reserved_name_clears`, `test_ck16_a5p03_kwonly_default_seeds_derived`,
   `test_ck16_a5p04_posonly_defaults_align_to_trailing_params` — with BOTH discriminators, `test_ck16_a5p05_bare_truth_test_is_a_boolean_context`)
   plus the A5P-01 control test; run them: the four must be RED for the issue's stated reason (paste each `E` line), the
   control GREEN. A case that is not red at the PIN is a premise conflict: stop and report it (rule: a lane is never the
   first place stale coordinator state is found — say what you found).
2. A5P-02: last-binding state takes precedence for locally-bound names — the reserved literal spelling counts only when
   the name resolves to the intended module/outer binding (parameter or module-level classifier operand), never after a
   local rebind to a non-operand. Keep A5P-01 green.
3. A5P-03: pair each `kwonlyarg` with its `kw_default`, skipping `None` entries (a required keyword-only parameter has no
   default).
4. A5P-04: align `defaults` against the trailing portion of `posonlyargs + args` per the AST semantics (`ast.arguments`:
   `defaults` covers the last len(defaults) of `posonlyargs + args`). Both discriminators must flip to the expected
   outcome.
5. A5P-05 — COORDINATOR'S PIN (the stronger of the issue's two options): MEET the documented boolean-context claim rather
   than narrowing it. Inventory, deliberately and by node type, a derived value appearing as the WHOLE test expression of
   `If.test`, `While.test`, `Assert.test`, `IfExp.test`, and as the operand of `UnaryOp(Not)` — in addition to the existing
   `Compare`/`BoolOp` inventory. State in the report which shapes are IN the domain and which are OUT (e.g. a derived value
   passed to `bool()`/`any()` is OUT unless you inventory it — say so explicitly; an honest narrowed domain beats a vague one).
6. The production checker C still satisfies the contract: `_assert_ck16_classifier_operand_contract(C)` passes on the
   unmodified C — paste the run; every pre-existing CK16 test stays green (`-k ck16` subset, paste the summary).
7. MUTATION AUDIT on scratch copies of T: revert each of the four fixes individually → its named test red (paste the four
   `1 failed` lines with the assertion); the A5P-01 control survives every revert. Then a de-vacuous pass: flip each new
   test's expected outcome → red at its own assert; restore.
8. Boundary check: `git status --porcelain` lists exactly T and your report; `git diff --quiet 236bec7 -- proofs/` rc 0;
   the G2 hunks T:2010-2152 UNTOUCHED (`git diff 236bec7 -- tests/test_s0_01_check_acp_conformance.py | grep -c '^@@'` and
   the hunk headers pasted — none inside 2010-2152).

## Boundary
T (`tests/test_s0_01_check_acp_conformance.py`) + your report ONLY. C, P, the evidence, `tests/test_s0_01_spec_runner.py`
and every other file: byte-identical to the PIN. A production change you believe necessary is a FINDING, never a fix here.
No git write, no commit, no push, no outward action; no live captures.

## Gate (every call under Hermes's 420 s terminal cap; paste verbatim)
- `export S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`;
  `/home/rocco/venv-agent-factory/bin` first on PATH; `mkdir -p ../scratch/bt`; an absolute SHORT `--basetemp`.
- Four lanes share the 12 cores tonight: `python -m pytest -n 4 -q -p no:cacheprovider --basetemp ../scratch/bt/<run>
  tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_spec_runner.py` TWICE on the final bytes (the PIN collects
  478; paste your counts, ZERO failed/xfailed); `python -m pyflakes tests/test_s0_01_check_acp_conformance.py` rc 0;
  `python3 scripts/ap_screen.py --tests tests/test_s0_01_check_acp_conformance.py` last line (four pre-existing hits at
  T:88, T:90, T:5590, T:6147 are known — new hits are yours to explain); `sha256sum` of the final T (FILE IDENTITY).
- CODE INTEL FIRST: `graft skeleton` / `graft ask` before any whole-file read (T is 6,400 lines — read by range).
  `report_lint` gates on a FLOOR (`--min-refs 12`); apply its `fix:` hints for at most THREE rounds, then paste and finish.

## Report shape (DATA)
FILE IDENTITY · item 1's four red lines + the control · per-item fix + green line · item 6 · the mutation table · the
de-vacuous lines · the two pytest summaries · pyflakes/ap_screen · DISCREPANCIES · NOT-done · GATE RECOMMENDATION (a
proposal; the coordinator grades and a targeted verify follows).
