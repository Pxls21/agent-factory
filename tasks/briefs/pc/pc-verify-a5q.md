# PC lane — VERIFY-A5q (targeted adversarial verification of ONE repair: issue #8, the CK16 classifier-operand meta-oracle sweep)

PIN: 2e02afd

Role: adversarial-verifier. Route: the LOCAL Qwen verify route (`agentfactory-verify-local`, the pc_lane.sh default for
adversarial-verifier — do NOT set HERMES_MODEL; the effort is the vLLM server's default, D-028's xhigh is not
verifiable on this route). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first. Report: draft after EACH item at
`tasks/briefs/s0-01-a5p-support/VERIFY-A5q-report.md`, return it whole as your final message. You VERIFY; you never
fix. A finding is file:line-bounded, reproduced through the real path, and graded by the blocking predicate
(contract-mapped · reproduced canonically · materially effective · a concrete discriminator · in-boundary). Emit a GATE
RECOMMENDATION (MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID), never a verdict — the
coordinator decides; under D-034 a non-blocking finding becomes a `verify-followup` issue. THREE sibling lanes may share
this host (K1-c, S4H, B7) — never touch their files or trees. Owner authorization: defensive test-oracle work on the
owner's own repository.

## Scope — one repair, nothing else
Issue #8 (GitHub; its four executable cases are reproduced below) recorded four defects in the TEST-SIDE model
`_assert_ck16_classifier_operand_contract` (T = `tests/test_s0_01_check_acp_conformance.py`, T:3190 at the PIN): the
reserved `argv` spelling matched before binding state (A5P-02, false positive), keyword-only defaults never seeded
(A5P-03, false negative), positional defaults zipped against `args.args` only (A5P-04, wrong-parameter binding), and
bare truth tests outside the `Compare`/`BoolOp` inventory (A5P-05, false negative). The repair A5q (brief
`tasks/briefs/pc/pc-a5q.md`, report `tasks/briefs/s0-01-a5p-support/A5q-report.md`, built on 236bec7, landed at the
PIN) touched T ONLY: `reserved_operand_names` + the last-binding rule in `value_is_derived` (T:3296-3312),
`parameter_seeds` (T:3327), `default_seeds` with the `posonlyargs + args` trailing alignment and the `kw_defaults`
pairing (T:3335-3357), `record_boolean_context` + the If/While/Assert whole-test path and the IfExp/UnaryOp(Not) path
(T:3365-3440), the frozen `allowed_boolean_tests = set()` (T:3575-3589), the two `check_config_echo` entries removed
from `allowed_predicates` (T:3551), five named tests T:3839-3947. The production checker C
(`proofs/S0-01/check_acp_conformance.py`), the pins P (`proofs/S0-01/pins.py`), the golden, the spec runner S and the
mint `proofs/S0-01/result.json` (e458801) are byte-identical to 236bec7. The coordinator re-ran the lane's own gates
and three of its mutants — that is NOT independent verification (orchestration rule 0f); THIS lane is the independent
hostile pass, and its shapes must be NEW, never the builder's own five cases.

## The changed equivalence class (what the model now claims — from the T:3273-3293 comment block and the T:3592-3606 docstring)
- Binding forms tracked: Assign / AnnAssign / AugAssign / NamedExpr, transitive simple-name aliases, module aliases
  visible at definition, positional / positional-only / keyword-only defaults (trailing alignment), direct calls to
  helpers whose explicit returns are all derived.
- Reserved spelling `argv` (`classifier_operands`, T:3265-3268): an operand only while its LAST binding (scope-local,
  then the scope's globals) resolves to it; a parameter named `argv` is seeded as the operand; a rebind clears it.
- Boolean contexts: the WHOLE test of If / While / Assert, `IfExp.test`, `UnaryOp(Not).operand`, plus the Compare /
  BoolOp operand inventory.
- Stated limits (OUT): container/subscript hops, attribute hops, closures beyond a direct default/walrus use,
  control-flow path sensitivity, module walrus, global/nonlocal, and derived values passed to boolean CALLS
  (`bool()`/`any()`/`all()`/`len()`).

## Items (each: what you did · the exact command · the exact output · SOLID/UNSURE · blocking? each predicate clause)
1. PREMISE (first; stop on failure): `git diff --stat 236bec7 2e02afd -- proofs/ tests/test_s0_01_spec_runner.py
   scripts/proof-runner scripts/validate-ledger` must be EMPTY and `git diff --stat 236bec7 2e02afd -- tests/` must name
   only T; `sha256sum tests/test_s0_01_check_acp_conformance.py` must read
   75fad3cd77ce3fa41baf2bccfdaa061d1def2472af4587d572b23d14e74a996e; `git diff 236bec7 2e02afd -- tests/test_s0_01_check_acp_conformance.py | grep '^@@'`
   must show 11 hunks, none inside the G2 region T:2010-2152. Paste all four. Any other change since the verified
   base means the premise of this targeted round is false: report CONTRACT-INVALID and stop.
2. The issue's ORIGINAL cases (issue #8 §Reproduction — the injected functions in its table, NOT the lane's tests):
   rebuild the coordinator's scratch driver (import `_ck16_checker_copy` + `_assert_ck16_classifier_operand_contract`
   from the repo test module; inject each function ahead of `def _pinned_process_count(commands):`) and run all seven
   rows (A5P-01 control, A5P-02, A5P-03, A5P-04 exact shape `value == pin`, A5P-04a `value == 'x'`, A5P-04b
   `pin == 'x'`, A5P-05 `if pin:`). Paste expected/observed per row; every row must read MATCHES-CONTRACT on the PIN.
   Then confirm the five named tests: `python -m pytest -q -p no:cacheprovider --basetemp ../scratch/bt/a5p
   tests/test_s0_01_check_acp_conformance.py -k a5p0` (the lane pasted `19 passed` for `-k "ck16 or ck17"`).
3. NEW HOSTILE SHAPES against each repaired family — you design them; the list below is the floor, not the ceiling.
   For every shape: write the contract's EXPECTED outcome from the claims above BEFORE running, run it through the real
   `_assert_ck16_classifier_operand_contract` on a `_ck16_checker_copy`, paste expected/observed, and grade a mismatch
   by the predicate (a shape inside a STATED LIMIT that misbehaves is a follow-up unless the docstring claims it; a
   shape inside the CLAIMED domain that misbehaves is in-boundary).
   a. Reserved-name binding state (A5P-02): a module-level `argv = PINNED_TEE_PATH` then `value == argv` in a function
      (expect RAISE) vs module-level `argv = []` (expect NO_RAISE); the rebind through each tracked binding form —
      AugAssign, AnnAssign, NamedExpr — and through the UNTRACKED forms (`for argv in …`, `with … as argv`,
      `except E as argv`, `import x as argv`, a comprehension target, `global argv`): state per form whether the
      model clears, keeps, or is blind, and whether the comment block declares it; a nested function rebinding `argv`
      while the OUTER parameter `argv` is compared (expect the outer compare inventoried); a rebind AFTER the use in
      source order (`return value == argv` then `argv = object()` — expect RAISE: last binding BEFORE the use). Then
      the seeding rule itself: enumerate EVERY function in C with a parameter named `argv` (`graft ask "which
      functions take a parameter named argv" --in proofs/S0-01/check_acp_conformance.py` + `grep -n 'def .*\bargv\b'`)
      and state for each whether that parameter IS the classifier operand; a parameter named `argv` that is not the
      operand makes `parameter_seeds` an over-approximation — grade it.
   b. Keyword-only defaults (A5P-03): `def f(value, *args, pin=PINNED_TEE_PATH, other=None)` (expect `pin` derived,
      `other` not); a required kwonly `def f(value, *, pin)` (expect not derived); a kwonly default that is a
      module-level ALIAS of an operand (`_p = PINNED_TEE_PATH` at module scope, `pin=_p`) and one that is a derived
      HELPER call (expect derived through globals/helpers); `**kwargs` named `argv`.
   c. Positional alignment (A5P-04): `def f(a, b=PINNED_TEE_PATH, /, c=None, *, d=PINNED_AGENT_REALPATH)` (expect b
      and d derived, a and c not); `def f(a, /, b, c=PINNED_TEE_PATH)` (expect c only); a lambda with a
      positional-only default (`lambda a, /, b=PINNED_TEE_PATH: b == 'x'`, expect RAISE); zero defaults with
      positional-only parameters (expect nothing seeded).
   d. Boolean contexts (A5P-05): `elif pin:` (an If in orelse), `while not pin:`, `assert pin, "msg"`,
      `x = 1 if pin else 2`, `if not (pin):`, an If nested in try/for/with bodies (expect RAISE each); the WALRUS test
      `if (x := pin):` (the claim says the WHOLE test expression — derive the expectation from the claim, then measure;
      a mismatch is graded against the docstring's words); `x = pin if cond else y` (`pin` in IfExp.body, not the test
      — expect NO_RAISE); `if bool(pin):`, `if pin.attr:`, `if pin[0]:` (stated OUT — expect NO_RAISE and say whether
      the docstring's OUT list names each); a derived value reaching an If.test through a helper call
      (`pin = helper()` with the helper returning an operand — expect RAISE); the same `if pin:` inside
      `_pinned_process_count` (skipped by design at T:3578 — state why the skip is sound).
   e. The dropped `check_config_echo` entries (T:3543-3551): confirm from C:1184-1195 that `argv` there is the
      argv.txt LINE LIST (a local Assign, not the classifier operand) so the two membership tests are correctly
      un-inventoried; then prove NOTHING ELSE moved — on a scratch copy of T print `actual_compares`,
      `actual_predicates` and `actual_boolean_tests` for the real C under the PIN's model and under 236bec7's model
      (`git show 236bec7:tests/test_s0_01_check_acp_conformance.py` into scratch): the only difference must be the two
      removed rows. Paste both inventories. Enumerate every `argv` binding in C (function · binding form · operand?).
4. MUTATION AUDIT on scratch copies of T (`git archive 2e02afd`, one mutant tree at a time, deleted after each run;
   never the shared tree): the lane's M1-M4 by NAME (M1 the complete pre-A5q A5P-02 model — the guard reverted AND the
   two old entries restored; M2 the kw_defaults pairing deleted; M3 `positional = args.args`; M4 the boolean-context
   inventory + final assert deleted) — paste each `1 failed` line with its assertion; then YOUR mutants of the new
   code, at least: `parameter_seeds` seeding EVERY parameter; `record_boolean_context` recording without the
   `value_is_derived` guard; the reserved-name lookup defaulting to True when unbound
   (`globals_state.get(node.id, True)`); the If/While path skipping `orelse`; the UnaryOp path accepting every op (not
   only `Not`); `positional[-len(args.defaults):]` replaced by `positional[:len(args.defaults)]`. For each: the named
   killer and its assertion, or SURVIVES — a survivor is a finding graded by the predicate (an over-approximation the
   C-contract test kills is a kill; one nothing kills is a finding). A mutant must compile and collect (AF-AP-78).
5. The de-vacuous pass on the five named tests: flip each expected outcome → red at its OWN assert (paste); and the
   A5P-01 control's discriminating power: state which mutant of the new code ONLY the control catches, or that none
   does (then the control is a regression guard for the A5o V1 fix, not for A5q — say so).
6. Gates on the PIN's bytes (four lanes share the 12 cores): `python -m pytest -n 4 -q -p no:cacheprovider
   --basetemp ../scratch/bt/<run> tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_spec_runner.py` TWICE
   (the lane pasted `483 passed` ×2 — paste yours); `python -m pyflakes tests/test_s0_01_check_acp_conformance.py`
   rc 0; `python3 scripts/ap_screen.py --tests tests/test_s0_01_check_acp_conformance.py` last block (the four
   pre-existing hits at T:88, T:90, T:5821, T:6378 are known — anything else is a finding).
7. Anything else INSIDE the A5q hunks (T:3273-3606, T:3839-3947). Exhaustive discovery; disciplined disposition.

## Boundary
READ-ONLY on the tree: attack through SCRATCH COPIES only (`../scratch`); never git-restore/stash/checkout the shared
tree; never `git add/commit/push`; never touch the corpus `/home/rocco/s0-01-pinned/realleg/golden`, the model server,
any unit, or another lane's tree. No live captures, no relay deliveries, no outward-facing action.

## Gate mechanics (each call under Hermes's 420 s terminal cap)
- `export S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`;
  `/home/rocco/venv-agent-factory/bin` first on PATH; `mkdir -p ../scratch/bt`; an absolute SHORT `--basetemp`.
- pytest on this host: `python -m pytest -n 4 -q -p no:cacheprovider --basetemp ../scratch/bt <files>` DIRECTLY
  (`scripts/pc_suite.sh` is the SANDBOX's launcher and cannot run here). T alone is ~15 min serial — always `-n 4`.
- CODE INTEL FIRST: `graft skeleton` / `graft ask` before any whole-file read (T is >6,500 lines — read by range).
  `report_lint` gates on a FLOOR (`--min-refs 12`); apply its `fix:` hints for at most THREE rounds, then paste and
  finish; paste its summary as PLAIN text.

## Report shape (DATA)
Per item: command · exact output · SOLID/UNSURE · blocking? (the predicate, each clause answered) · the file:line.
Then: the shape table (item 3: shape · claimed domain IN/OUT · expected · observed · grade), the mutant table (item 4:
mutant · killer · assertion · `N failed` or SURVIVES), DISCREPANCIES, NOT-done, GATE RECOMMENDATION. Never a fix,
never a verdict.
