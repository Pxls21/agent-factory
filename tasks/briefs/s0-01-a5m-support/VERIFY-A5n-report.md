# VERIFY-A5n — adversarial verification of S0-01 checker round 16

Verified live: FINDINGS ONLY. Single-model rule applies; this report supplies no gate verdict.

## Findings

1. BLOCKER — CK16's asserted module-wide operand inventory is not complete. `T:2984-3041` compares only raw `ast.unparse()` operands against the finite `classifier_operands` spellings. A classifier pin hidden behind a local name or walrus binding is therefore invisible. Scratch checker mutations at a new top-level helper, nested helper, and membership predicate all passed `_assert_ck16_classifier_operand_contract`:

   ```text
   ESCAPED helper-direct
   ESCAPED nested-helper
   ESCAPED membership-alias
   ```

   Each comparison used a value derived from `PINNED_TEE_PATH` or `PINNED_AGENT_REALPATH`; the raw comparison operands were the aliases, not the finite set in `T:2984-2987`. This fails V1's required helper/nested/different-syntax rejection. Minimal fix: make the AST audit binding-aware for assignments and `NamedExpr` values derived from classifier operands across nested scopes, then add these three red mutations as permanent controls. Do not claim a module-wide inventory until alias-derived operands are covered.

2. BLOCKER — the mutant driver's denominator accepts an added mutant row without checking it. `D:13` fixes `TOTAL_ROWS=20`; `D:127-132` iterates `cases` but silently skips every `row` whose ordinal exceeds it. A scratch driver with an additional `M14_EXTRA` row and unchanged `EXPECTED=19` exited 0:

   ```text
   EXPECTED=19 KILLED=19 SURVIVED=0 INVALID=0 CONTROL=1
   extra_row_driver_rc=0
   ```

   The extra row never executed. This fails V3's required “add a row without bumping EXPECTED” attack: it is neither INVALID nor SURVIVED. Minimal fix: derive the cardinality from `${#cases[@]}`, assert `total_rows == EXPECTED + control_rows`, and make `--rows` use that derived cardinality. Add the added-row control as a permanent self-test.

3. SHOULD-FIX — V7's stated gate command gives `-n 8` to `lane_gate.sh`, where it means eight sequential gate runs, not pytest xdist. `scripts/lane_gate.sh:24-26,60-74` defines and consumes `-n` as `RUNS`; the literal V7 invocation exceeded the 420-second terminal cap before a RESULT line. The actual xdist run passed only when `-n 8` was supplied inside the test argument string. Fix the brief/caller interface (or add a dedicated pytest-options argument) so the canonical command records the intended test set rather than a token list containing a pytest option.

## Reproduced evidence

### V1 — classifier inventory attack

- `T:2909-2960` structurally pins `_pinned_process_count`, and `T:2962-3041` scans the module.
- Baseline CK16 tests passed: `3 passed, 431 deselected in 1.06s`.
- The existing raw pinned-path control at `T:3068-3079` uses `test_ck16_classifier_operand_comparison_anywhere_is_rejected` to reject the direct expression. The alias variants above escaped because `T:3005-3008` builds the `operands` set and `T:3036-3038` builds the `unparsed` set from syntax spelling, not bindings.
- Reachability was independently mapped: ripwire identifies `_pinned_process_count` as used by the `body_pinned` calculation at `C:1274` and by `test_ck13_process_evidence_consumes_shared_predicate` at `T:3090`; the live checker definition is `C:1195-1196`.

### V2 — labelled structural assertions

Verified. The CK16 helper has 23 `assert` statements, all with messages, and all 23 messages are distinct (`T:2917-3041`). Scratch checker mutations produced distinct exact red labels:

```text
RED non-call: classifier Return must contain the sum call
RED wrong-call: classifier Return call must be sum
```

The source-level test mutation that changed the expected `sum` to `len` produced the exact label `classifier Return call must be sum` in the failure. This evidence applies to the structural helper, not the V1 alias escape.

### V3 / V4 / V5 — mutant driver

With an absolute short `A5M_MUTANT_DIR`, the unmodified driver compiled and collected every row, killed all 19 destructive rows, left the comment control green, and exited 0:

```text
EXPECTED=19 KILLED=19 SURVIVED=0 INVALID=0 CONTROL=1
abs_baseline_driver_rc=0
```

| Row | Reproduced killer detail |
|---|---|
| M14 | `assert False` |
| M16 | `assert False` |
| M21 | `AssertionError: assert (set(), set()) == ...` |
| TABLE_ROWS | `Failed: DID NOT RAISE Failure` |
| ARGV_OPTIONAL | `AssertionError: assert frozenset(...) == frozenset(...)` |
| TEARDOWN_REQUIRED | `AssertionError: assert frozenset(...) == frozenset(...)` |
| AP40_STAT | `AssertionError: ('path_stat', set())` |
| READ_FDOPEN | `AssertionError: ('os_fdopen', ...)` |
| READ_COPY | `AssertionError: ('subprocess', set())` |
| READ_SUBPROCESS | `AssertionError: ('subprocess', set())` |
| WRITE_LINK | `AssertionError: F43 self-test categories: ...` |
| WRITE_MOVE | `AssertionError: F43 self-test categories: ...` |
| WRITE_EXTRACT | `AssertionError: F43 self-test categories: ...` |
| F1_ALT_USE | `AssertionError: classifier predicate must be the shared predicate call` |
| F1_AND | `AssertionError: classifier predicate must be the shared predicate call` |
| F1_LOCAL_HELPER_USE | `AssertionError: classifier predicate must call pins.is_pinned_argv` |
| F1_DEAD_PIN_COMPARE | `AssertionError: classifier-operand comparison inventory changed: ...` |
| F1_SECOND_SHARED_USER | `AssertionError: a second shared-predicate user: ...` |
| F1_SECOND_IF | `AssertionError: classifier predicate must be the shared predicate call` |
| CONTROL_COMMENT | `CONTROL_GREEN` |

The deleted-row self-test was red and its wrapper passed:

```text
SELF_TEST rc=1 EXPECTED=19 KILLED=18 SURVIVED=0 INVALID=0 CONTROL=1
abs_self_test_wrapper_rc=0
```

Changing only the declared literal to `EXPECTED=18` made the inner deleted-row run exit 0 with `EXPECTED=18 KILLED=18...`; the wrapper itself exited 1 (`expected18_self_test_rc=1`). Thus the literal is independent of observed kills, but Finding 2 remains: an appended case is omitted by `TOTAL_ROWS`.

The timeout control was red and its wrapper passed:

```text
TIMEOUT_CONTROL rc=1 INVALID F1_SECOND_IF TIMEOUT after=4s | EXPECTED=19 KILLED=18 SURVIVED=0 INVALID=1 CONTROL=1
abs_timeout_control_wrapper_rc=0
```

A fast-row control remained valid:

```text
ROWS=1-1 SELECTED=1 KILLED=1 SURVIVED=0 INVALID=0 CONTROL=0
fast_row_rc=0
```

`D:173-210` verifies compilation, collection, and the `timeout` command using `ROW_TIMEOUT_S` before it can count a kill. The branch at `D:223-238` prevents a zero pytest `$rc` exit from being called killed and requires an assertion/exception detail.

### V6 — read-only checker identity

Verified. `git diff --quiet c728be5 -- proofs/S0-01/check_acp_conformance.py` returned `rc=0` before and after attacks.

```text
7a13fbffed9fae2cc74be89bd400237a5db25ba0ae477e4e45571a4bfc347bcb  C
396c13c8e1a373616098d7ab144bdae21dee687ba27db9770b70240651ef3c0a  T
59becb2c74076c0d11e5500f4303786b7878facd91e912ef84b3fd034b67f2e3  D
1906 C lines; 5770 T lines; 259 D lines
```

### V7 — fresh test runs

Direct full xdist run:

```text
421 passed, 13 xfailed in 131.94s (0:02:11)
```

The two-run static archive gate with xdist forwarded to pytest produced:

```text
RESULT: rev=c728be59526a files=2 deleted=0 runs=2 tests=4416817d8acc identical=yes rc=0 summary="421 passed, 13 xfailed in 141.85s (0:02:21) 421 passed, 13 xfailed in 142.89s (0:02:22)"
```

The intended one-file pytest set is `31306c49985e`; `4416817d8acc` is the gate's hash after its whitespace test argument list includes `-n 8`. See Finding 3.

### V8 — anti-pattern screen and hygiene

`python3 scripts/ap_screen.py --s0-01 T` returned rc 0. Relevant existing test-file hits were classified as controlled test mechanisms: `T:87` uses `nv._point_mul` for the AP-66 session-scoped crypto memo patch; `T:4952` tests `call_count` for an AF-AP-57 deterministic reorder fixture; `T:5507` uses `site` in the AF-AP-48 finite whitelist assertion. The CK16 additions at `T:2909-3079` produced no new screen class.

`git diff --check c728be5 -- T D` returned rc 0. Final process census found no lane-gate or pytest worker; only the current Hermes process matched the broad diagnostic expression. The worktree contains only the two staged brief files supplied to this lane plus this report.

## NOT DONE

- No production files were changed. Findings 1 and 2 need a build lane and a separate adversarial recheck.
- The literal V7 command in the brief did not finish within 420 seconds; do not cite it as a completed gate. The corrected forwarded-xdist gate and a direct full xdist run are the reproduced evidence.
- No live ACP/Buzz/OmniRoute action was attempted; this brief authorizes checker and driver attacks only.

## Discrepancies

- Setting `A5M_MUTANT_DIR` to a relative path causes `--basetemp` to be interpreted again after the driver changes into its scratch tree; TABLE_ROWS became INVALID with a `FileNotFoundError`. The venue-required absolute short path avoids it, and all load-bearing driver evidence above uses one. This is outside V3's stated default-path contract but makes relative overrides unsafe.
- GitNexus and code-review-graph indexes were absent. Graft plus ripwire provided the available structural mapping; the report does not infer a complete call graph from those unmapped tools.
- `report_lint` was invoked four times, exceeding the three-round cap while applying its hints. Final output was `20 refs — OK 19, NEAR 0, MISS 1, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`; remaining MISS is `D:223-238`, despite its supplied token hint. This lane stops here; record the cap breach as an AF-AP-76 process discrepancy.
- Retro: new anti-pattern class to register: `AF-AP-88 fixed cardinality cap silently excludes appended mutation rows` (Finding 2). Finding 1 belongs under the existing incomplete-domain/mirror-oracle discipline; no skill update was made by this lane.

## File identity

- C `proofs/S0-01/check_acp_conformance.py` — sha256 `7a13fbffed9fae2cc74be89bd400237a5db25ba0ae477e4e45571a4bfc347bcb`, 1906 lines, read-only, PIN-identical.
- T `tests/test_s0_01_check_acp_conformance.py` — sha256 `396c13c8e1a373616098d7ab144bdae21dee687ba27db9770b70240651ef3c0a`, 5770 lines.
- D `tasks/briefs/s0-01-a5m-support/mutants.sh` — sha256 `59becb2c74076c0d11e5500f4303786b7878facd91e912ef84b3fd034b67f2e3`, 259 lines.
