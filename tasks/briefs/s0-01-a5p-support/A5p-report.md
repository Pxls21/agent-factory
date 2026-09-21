# A5p — S0-01 checker round 18 report

NOT done: this build-lane output is a proposal until the separate sandbox adversarial-verifier grades it. I did not issue a gate verdict, change production checker bytes, mint a proof, commit, push, or take any live ACP/Buzz/OmniRoute action.

## Outcome

Verified in this lane: V1's reassigned-local false positive is fixed in T, the deliberately finite CK16 classifier-operand domain is stated exactly, V2 regressions are committed in T, and the A5o mutation driver now certifies the new boundary. The production checker C and `pins.py` remain byte-identical to PIN `798ce74`.

## VERIFIED

### Premise

- The verifier's frozen hostile suite reproduced before edits: `7 failed, 1 passed in 1.98s`.
- C and pins were unchanged when the premise was measured, and remain unchanged: `checker_pin_diff_rc=0`; `pins_pin_diff_rc=0`.
- The old accumulating set used `function_operand_aliases` at T@798ce74:3039 and returned the unchanged `aliases` set at T@798ce74:3049; it could not kill a name after rebinding.

### V1 — honest finite domain

T:2989 (`CK16`) states the finite domain; T:2993 names covered `Assign` / `AnnAssign` / `AugAssign` / `NamedExpr` classes; T:2994 names `transitive` aliases; and T:2995 names `lambda/function defaults`. `_assert_ck16_classifier_operand_contract` tracks these forms in source order:

- simple-name `Assign`, `AnnAssign`, `AugAssign`, and `NamedExpr` bindings;
- transitive simple-name aliases;
- module-scope aliases visible when a function is defined;
- lambda and function default arguments;
- direct plain-name helper calls when every explicit return expression derives inside the same finite model.

T:2998 names the `container/subscript` and attribute limits; T:2999 adds nested closures, path sensitivity, and module walrus; T:3000 adds `global/nonlocal`. The model does NOT claim those classes. T:3407 defines `test_ck17_classifier_operand_container_hop_is_stated_limit`; T:3423 defines `test_ck17_classifier_operand_attribute_hop_is_stated_limit`. A real checker use in a stated-limit form is a finding, not an automatic contract expansion.

The rebind fix is explicit: T:3035 initializes current `state`; T:3043 handles `Assign` / `AnnAssign` / `AugAssign`; T:3058 replaces `state[name]` for each supported assignment instead of accumulating aliases.

### V2 — committed boundary regressions

T:3297 defines `test_ck17_classifier_operand_rebound_local_is_not_classifier_operand`. T:3314 defines `test_ck17_classifier_operand_transitive_local_chain_is_rejected`; T:3333 defines `test_ck17_classifier_operand_module_alias_chain_is_rejected`; T:3353 defines `test_ck17_classifier_operand_augmented_alias_is_rejected`; T:3371 defines `test_ck17_classifier_operand_lambda_default_is_rejected`; T:3387 defines `test_ck17_classifier_operand_default_argument_helper_is_rejected`.

T:3407 defines `test_ck17_classifier_operand_container_hop_is_stated_limit`. T:3423 defines `test_ck17_classifier_operand_attribute_hop_is_stated_limit`.

Focused execution:

```text
14 passed, 431 deselected in 3.17s
```

Independent red-before-green instrument in D:22 (`--old-model-control`) inserts the same eight new tests into T from PIN `798ce74`. Its exact result was:

```text
OLD_MODEL_CONTROL rc=1 did_not_raise=4 | 5 failed, 3 passed, 437 deselected in 3.08s | E       AssertionError: classifier-operand comparison inventory changed: [('unrelated', 'value == pin')]
```

That pins both directions: the PIN model false-positives the reassigned local and misses four newly claimed hostile forms. The three passing cases are the two stated limits plus the additional supported case the PIN happened to cover.

### Mutation driver

The named A5o driver was updated in place, as required by the boundary. D:9 contains `PIN=${PIN:-798ce74}`. D:12 contains `EXPECTED=24`. D:176 contains `A5P_REBIND`; D:177 contains `A5P_TRANSITIVE`. Full result:

```text
EXPECTED=24 KILLED=24 SURVIVED=0 INVALID=0 CONTROL=1
```

Control results:

```text
SELF_TEST rc=1 CARDINALITY_MISMATCH rows=24 expected=25 destructive=24 control=1
ADDED_ROW_CONTROL rc=1 CARDINALITY_MISMATCH rows=26 expected=25 destructive=24 control=1
TIMEOUT_CONTROL rc=1 INVALID F1_SECOND_IF TIMEOUT after=4s | EXPECTED=24 KILLED=23 SURVIVED=0 INVALID=1 CONTROL=1
```

### Outer gate and static checks

The required bridge launch could not run because this local PC lane has no `PC_BRIDGE_URL` or `PC_BRIDGE_TOKEN`, and the PC clone check reported that it did not have the detached lane SHA. I did not read or print `.pc-bridge.env`. I ran the same declared file directly on this PC with the required venv, venue, corpus, short absolute basetemp, and `-n 8`:

```text
432 passed, 13 xfailed in 129.09s (0:02:09)
```

Equivalent set identity for the sole test path is `1 files set=31306c49985e — tests/test_s0_01_check_acp_conformance.py`.

`py_compile`, `pyflakes`, `bash -n`, and `git diff --check` returned rc 0. The final context pack is `../scratch/A5p-final-pack3.md` (270 lines). GitNexus `detect-changes` reported 3 files, 27 symbols, 0 affected processes, risk low; its clone index also counted the pre-staged brief file outside this lane's edit boundary.

## FILE IDENTITY

- T `tests/test_s0_01_check_acp_conformance.py`: `_assert_ck16_classifier_operand_contract` at T:2909; 6,129 lines; `d8e630ca4da6879e344d653cce0439a7930d2af294cc89682e5c82d4a0bcfae3`.
- D `tasks/briefs/s0-01-a5o-support/mutants.sh`: `EXPECTED=24` at D:12; 335 lines; `ac64b9a26b6ffeaf71b6dbafa763ee3e1df9a8380b513dc6ccffad6f8da31153`.
- C `proofs/S0-01/check_acp_conformance.py`: 1,906 lines; `7a13fbffed9fae2cc74be89bd400237a5db25ba0ae477e4e45571a4bfc347bcb`; byte-identical to PIN.
- P `proofs/S0-01/pins.py`: 629 lines; `41fa933d131ac24701100ba52b8959f3c7d2740b9be4336041388ab891bb83a4`; byte-identical to PIN.

## SELF-ATTACK

1. Most likely failure: the new model merely trades the rebind false positive for broader unclaimed misses. Ruled out for the claimed domain by five hostile-form regressions, the PIN-model red control, and 24/24 killed mutants. Not ruled out beyond the stated limits; those remain explicit.
2. Most likely failure: production checker behavior changed or the test passed against different source bytes. Ruled out by `checker_pin_diff_rc=0`, `pins_pin_diff_rc=0`, SHA identity above, and the full real-corpus T run.
3. Most likely failure: mutation rows are invalid, vacuous, or a timeout is counted as a kill. Ruled out by compile/collect checks per row, `INVALID=0`, the green comment control, cardinality remove/add controls, and the exact timeout control producing `INVALID=1`, not a kill.

## DISCREPANCIES

- The literal `scripts/pc_suite.sh launch` command was unavailable in this PC lane: it requires bridge credentials not provided to the lane and a base commit available in the PC clone. Direct local-PC xdist execution supplied the same pytest file/worker/venue/corpus boundary, but it does not produce `pc_suite.sh`'s literal `pytest-summary:`/`pytest-set:` labels.
- `scripts/test_summary.sh` is serial and exceeded Hermes's 420-second tool cap. Its timeout is not counted as a test result. The required xdist execution completed separately in 129.09 seconds.
- Ripwire `edit-check` could not disambiguate the test-file contract and returned rc 1. Graft/lane-context and GitNexus supplied final mapping evidence.
- AP screen returned four pre-existing hits in T at unrelated lines 87, 89, 5311, and 5866; none intersect the A5p hunks. D had 0 hits.
- Final report lint: `report_lint: 29 refs — OK 28, NEAR 1, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.
- The worktree already contains staged `tasks/briefs/pc/pc-a5p.md`; I did not create or edit it, and it is outside FILE IDENTITY.

## INFERRED

- The production checker contains no derived aliases in the chosen domain, so the old and new inventories agree for its current bytes. This is also exercised by the full T gate.
- A verifier may reasonably request less test-side static-analysis code. D-034 permits a finite model rather than an unbounded engine; this implementation follows that decision but is still a non-trivial AST walker.

## ASSUMED

- The sandbox coordinator will run the separate adversarial-verifier lane before acceptance and will treat any surviving classifier-operand bypass as a `verify-followup`, not a round 19.

## NOT DONE

- No independent verifier result exists in this lane.
- No literal bridge-produced `pytest-summary:`/`pytest-set:` lines exist for this run.
- No new proof artifact was minted or re-signed.
- No unrelated findings or stated-limit forms were expanded.
- No commit, push, tag, branch write, PR, issue, or outward-facing action.

## Reasoning record

Rejected alternative: chase every container, subscript, attribute, closure, and path-sensitive form. D-034 explicitly stops that treadmill. Ordering rationale: first kill current-name state on rebind, then add only cheap ordinary flows, then state and pin limits. Primary source: VERIFY-A5o V1/V2 plus the hostile suite reproduced in this lane. Disjoint hunks: T's finite model/regressions and D's red-control/campaign extensions.

## Retro

Defect class: AF-AP-30 / resolver-mirror variant, already recorded by VERIFY-A5o. Lesson: any alias inventory must state its lifetime/scope domain and pin both an over-match negative and an under-match hostile form. No new general lesson beyond that existing registry entry; nothing else to bake.

## AUDIT DISPOSITION (coordinator, 2026-09-21) — read this before the sections above

The independent audit of 2026-09-21 ran the hostile pass this lane did not have (line 112 above
is honest: no independent verifier result existed). Its findings A5P-02..A5P-05 were REPRODUCED by
the coordinator with executable evidence against this lane's model and filed as GitHub issue #8
(`verify-followup` + `stage0`): a reserved `argv` local rebind still false-positives (the literal
spelling is matched before the binding state), keyword-only defaults are not processed, positional-
only defaults are zipped to the wrong parameter, and bare truth tests (`if pin:`) are not
inventoried. The V1 fix itself (A5P-01, the ordinary reassigned-alias false positive) HOLDS.

Consequently the wording "the deliberately finite CK16 classifier-operand domain is stated exactly"
(line 7) and the "## VERIFIED" heading overstate the landing. Corrected status: MECHANICALLY GATED —
MERGE-READY-WITH-FOLLOWUPS / GATED-PENDING-VERIFY. The coordinator's 432 passed / 13 xfailed was a
re-run of this lane's own gate, not independent verification. Per D-034 no checker round 19 is opened
for these; they stay parked in #8. The production checker and pins.py remain byte-identical to the PIN.
