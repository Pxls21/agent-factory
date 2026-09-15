PROPOSAL — A5n build-lane evidence only. Independent sandbox adversarial verification has not run.

NOT DONE

- Independent sandbox adversarial verification has not run. This lane cannot self-accept or issue a gate verdict.
- No production checker change was needed. No proof was minted. No corpus bytes were changed. No commit, push, service restart, or outward-facing action occurred.

GROUND AND PREMISE

- PIN: `c41aab6a5ac4552034cdfb40240f75cc135742c3`.
- F1 reproduced before the edit on two scratch checker copies. An unrelated `env.get("X") == "1"` comparison produced `1 passed, 431 deselected`; a comparison against `PINNED_TEE_PATH` produced `1 failed, 431 deselected`. Combined result: `PREMISE unrelated_rc=0 classifier_operand_rc=1`.
- F2 reproduced from the landed driver: its six F1 rows selected one structural test, and generic structural failures included `AssertionError: assert False`.
- AF-AP-84 reproduced at the PIN: D derived `expected` inside the executed-row loop and decremented it for an INVALID row.
- The timeout gap reproduced at D@c41aab6:116-120: pytest ran directly, with no external per-row timeout.

FILE IDENTITY

Before, at PIN `c41aab6`:
- C: sha256 `7a13fbffed9fae2cc74be89bd400237a5db25ba0ae477e4e45571a4bfc347bcb`, 1906 lines.
- T: sha256 `70914ea3c4785a722e91e2b35057ea93b62f2d3e9effba9000d7edf552acc491`, 5707 lines.
- D: sha256 `b746a525cfeb539118d4ae5325528dadfb88fb0b583452a0788e6016e5790804`, 154 lines.

After:
- C unchanged: sha256 `7a13fbffed9fae2cc74be89bd400237a5db25ba0ae477e4e45571a4bfc347bcb`, 1906 lines.
- T: sha256 `396c13c8e1a373616098d7ab144bdae21dee687ba27db9770b70240651ef3c0a`, 5770 lines.
- D: sha256 `59becb2c74076c0d11e5500f4303786b7878facd91e912ef84b3fd034b67f2e3`, 259 lines.

VERIFIED

Item 1, narrowed claim:
- T:2909 `_assert_ck16_classifier_operand_contract` accepts a checker path, so both production and scratch copies execute the same contract.
- T:2984 `classifier_operands` defines the finite operand domain; T:3007 and T:3037 add only comparisons, memberships, or boolean forms whose direct operands intersect that domain.
- T:3044 `test_ck16_checker_inventories_classifier_operand_predicates_module_wide` names the actual module-wide inventory rather than claiming every comparison in C is forbidden.
- T:3057 `test_ck16_unrelated_comparison_is_outside_classifier_operand_contract` plants an unrelated comparison in a scratch checker and remains green.
- T:3068 `test_ck16_classifier_operand_comparison_anywhere_is_rejected` plants a pinned-path comparison in the same location and requires `classifier-operand comparison inventory changed`.
- Focused CK16 run: `3 passed, 431 deselected in 1.01s`.

Item 2, labelled structural assertions:
- T:2917-2960 labels the exact classifier body, return, `sum`, generator, target, iterable, predicate, call-count, and BoolOp/Compare shapes.
- T:2971 labels a second shared-predicate user; T:2981 labels private helper names; T:3009 and T:3039 label comparison and BoolOp/membership inventory drift.
- Red-before control on a scratch T with the two inventory labels removed: `1 failed, 2 passed, 431 deselected in 1.23s`; `RED_BEFORE_LABELS_RC=1`.
- Final six F1 driver lines:

KILLED F1_ALT_USE | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck16_checker_inventories_classifier_operand_predicates_module_wide | E       AssertionError: classifier predicate must be the shared predicate call
KILLED F1_AND | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck16_checker_inventories_classifier_operand_predicates_module_wide | E       AssertionError: classifier predicate must be the shared predicate call
KILLED F1_LOCAL_HELPER_USE | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck16_checker_inventories_classifier_operand_predicates_module_wide | E       AssertionError: classifier predicate must call pins.is_pinned_argv
KILLED F1_DEAD_PIN_COMPARE | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck16_checker_inventories_classifier_operand_predicates_module_wide | E       AssertionError: classifier-operand comparison inventory changed: [('_dead_pin_compare', 'argv[0] == PINNED_TEE_PATH')]
KILLED F1_SECOND_SHARED_USER | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck16_checker_inventories_classifier_operand_predicates_module_wide | E       AssertionError: a second shared-predicate user: ['unrelated_shared_user']
KILLED F1_SECOND_IF | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck16_checker_inventories_classifier_operand_predicates_module_wide | E       AssertionError: classifier predicate must be the shared predicate call

Item 3, literal denominator:
- D:12 fixes `EXPECTED=19`; D:13 separately records 20 total rows, including the one green control.
- D:22-47 copies D, deletes exactly the `F1_SECOND_IF` row, runs the copy, and requires its non-zero literal-denominator summary.
- D:240-243 prints the literal and requires exactly `KILLED=19`, `SURVIVED=0`, `INVALID=0`, `CONTROL=1`.
- Final full driver:

KILLED M14 | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck13_dead_branch_citation_mutants_die | E       assert False
KILLED M16 | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck13_dead_branch_citation_mutants_die | E       assert False
KILLED M21 | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck13_read_site_drift_validator_rejects_rebound_expected | E       AssertionError: assert (set(), set()) == ({('a.py', 'f...'unguarded')})
KILLED TABLE_ROWS | FAILED tests/test_s0_01_check_acp_conformance.py::test_v24_table_rows_key_cannot_be_replaced_by_rows | E       Failed: DID NOT RAISE Failure
KILLED ARGV_OPTIONAL | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck12_pinned_required_file_cannot_be_dropped | E       AssertionError: assert frozenset({'b...v.json', ...}) == frozenset({'a...cp.log', ...})
KILLED TEARDOWN_REQUIRED | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck12_pinned_required_file_cannot_be_dropped | E       AssertionError: assert frozenset({'a...cp.log', ...}) == frozenset({'a...cp.log', ...})
KILLED AP40_STAT | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck13_presence_gate_detector_covers_each_probe_family[path_stat-def f(p):\n    try:\n        return p.stat()\n    except OSError:\n        return None\n-p.stat()] | E       AssertionError: ('path_stat', set())
KILLED READ_FDOPEN | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck13_read_inventory_covers_each_declared_family | E           AssertionError: ('os_fdopen', {('os_fdopen.py', 'f', 'fd', 'unguarded')})
KILLED READ_COPY | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck13_read_inventory_covers_each_declared_family | E           AssertionError: ('subprocess', set())
KILLED READ_SUBPROCESS | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck13_read_inventory_covers_each_declared_family | E           AssertionError: ('subprocess', set())
KILLED WRITE_LINK | FAILED tests/test_s0_01_check_acp_conformance.py::test_f43_no_direct_writes_outside_rewrite | E       AssertionError: F43 self-test categories: {'.hardlink_to', '.touch', '.write_text', '.chmod', 'archive.extractall', 'os.replace', 'io.open', 'shutil.move', 'archive.extract', 'gzip.open', 'os.utime', 'json.dump', 'shutil.copy', '.rename', 'op', 'open', 'os.truncate', '.symlink_to', '.open', '.write_bytes'}
KILLED WRITE_MOVE | FAILED tests/test_s0_01_check_acp_conformance.py::test_f43_no_direct_writes_outside_rewrite | E       AssertionError: F43 self-test categories: {'.hardlink_to', '.touch', '.write_text', '.chmod', 'archive.extractall', 'os.replace', 'io.open', 'archive.extract', 'gzip.open', 'os.link', 'os.utime', 'json.dump', 'shutil.copy', '.rename', 'op', 'open', 'os.truncate', '.symlink_to', 'os.symlink', '.open', '.write_bytes'}
KILLED WRITE_EXTRACT | FAILED tests/test_s0_01_check_acp_conformance.py::test_f43_no_direct_writes_outside_rewrite | E       AssertionError: F43 self-test categories: {'.hardlink_to', '.touch', '.write_text', '.chmod', 'os.replace', 'io.open', 'shutil.move', 'gzip.open', 'os.link', 'os.utime', 'json.dump', 'shutil.copy', '.rename', 'op', 'open', 'os.truncate', '.symlink_to', 'os.symlink', '.open', '.write_bytes'}
KILLED F1_ALT_USE | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck16_checker_inventories_classifier_operand_predicates_module_wide | E       AssertionError: classifier predicate must be the shared predicate call
KILLED F1_AND | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck16_checker_inventories_classifier_operand_predicates_module_wide | E       AssertionError: classifier predicate must be the shared predicate call
KILLED F1_LOCAL_HELPER_USE | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck16_checker_inventories_classifier_operand_predicates_module_wide | E       AssertionError: classifier predicate must call pins.is_pinned_argv
KILLED F1_DEAD_PIN_COMPARE | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck16_checker_inventories_classifier_operand_predicates_module_wide | E       AssertionError: classifier-operand comparison inventory changed: [('_dead_pin_compare', 'argv[0] == PINNED_TEE_PATH')]
KILLED F1_SECOND_SHARED_USER | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck16_checker_inventories_classifier_operand_predicates_module_wide | E       AssertionError: a second shared-predicate user: ['unrelated_shared_user']
KILLED F1_SECOND_IF | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck16_checker_inventories_classifier_operand_predicates_module_wide | E       AssertionError: classifier predicate must be the shared predicate call
CONTROL_GREEN CONTROL_COMMENT
EXPECTED=19 KILLED=19 SURVIVED=0 INVALID=0 CONTROL=1
DRIVER_LAST_RC=0

- Deleted-row self-test:

SELF_TEST rc=1 EXPECTED=19 KILLED=18 SURVIVED=0 INVALID=0 CONTROL=1
SELF_SMOKE_RC=0

Item 4, per-row timeout:
- One selected structural node measured `1 passed in 0.81s`; whole-process wall was `1.18s`. D:14 sets `ROW_TIMEOUT_S=4`, which is greater than 3× both the test time and measured process wall.
- D:202 runs every mutation pytest invocation under `timeout "$ROW_TIMEOUT_S"`; D:207-210 turns rc 124 into `INVALID <row> TIMEOUT`, before control or KILLED classification.
- D:50-77 changes one scratch row so its selected CK16 test sleeps for 60 seconds, then requires the driver's INVALID gate to fail.
- Final timeout control:

TIMEOUT_CONTROL rc=1 INVALID F1_SECOND_IF TIMEOUT after=4s | EXPECTED=19 KILLED=18 SURVIVED=0 INVALID=1 CONTROL=1
TIMEOUT_SMOKE_RC=0

- D:228-238 retains AF-AP-78: non-zero pytest counts as KILLED only when both a `FAILED ...::<test>` node and an `E       ` detail exist.

Item 5, gates:
- Checker set identity: `1 files set=31306c49985e`.
- Checker run 1: `421 passed, 13 xfailed in 135.56s (0:02:15)`.
- Checker run 2: `421 passed, 13 xfailed in 135.86s (0:02:15)`.
- Joint identity: `13 files set=c62435272c99`.
- Joint run: `1354 passed, 13 xfailed in 177.89s (0:02:57)`; measured PIN baseline: `1352 passed, 13 xfailed in 193.22s (0:03:13)`, so this lane's delta is `+2 passed`, `+0 xfailed`. The brief's stated 1341 floor was stale at the declared PIN.
- `python -m pyflakes T`: rc 0.
- `bash -n D`: rc 0.
- `git diff --check`: rc 0.
- AP screen: `4 hits over 1 files`: AP-66 at T:87 `nv._point_mul = _cached_pm` and T:89 `nv._point_mul = _orig_pm`, AF-AP-57 at T:4952 `call_count`, AF-AP-48 at T:5507 `site[3]`. All are pre-existing and outside the CK16 helper beginning at T:2909 `_assert_ck16_classifier_operand_contract`; no new hit class.
- Final lane-context pack: `lane_context: pack written to ../scratch/a5n/pack-final/final-pack.md (183 lines)`.

INFERRED

- The inventory is intentionally strict only inside its declared classifier-operand domain. A future legitimate use of a pinned process/argv/path operand requires explicit review and an update to T:2993 `allowed_compares` or T:3015 `allowed_predicates`; unrelated operands remain outside this contract.
- The driver results are build-lane evidence. A separate adversarial-verifier must independently reproduce and attack the contract before acceptance.

ASSUMED

- None. Load-bearing statements above come from current-tree source reads or commands run in this lane.

SELF-ATTACK

1. The narrower name could hide weakened behavior. Ruled out by the paired scratch tests at T:3057 and T:3068, plus six distinct F1 driver mutants that all produced named structural failures.
2. The denominator could still shrink with the declared rows. Ruled out by D:12's literal, D:240-243's exact final condition, and the deleted-row self-test: its inner driver exited 1 with only 18 kills while still printing EXPECTED=19.
3. A hanging row could be credited as a kill. Ruled out by the 60-second sleep control: the 4-second outer timeout emitted `INVALID F1_SECOND_IF TIMEOUT after=4s`, KILLED fell to 18, INVALID rose to 1, and the inner driver exited 1.

DISCREPANCIES

- The brief's stated 13-file PIN floor is `1341 passed`, but an actual archive of PIN c41aab6 produced `1352 passed, 13 xfailed`. The current tree produced 1354, the expected +2 from this lane.
- The brief says 3× the checker file's measured serial time for one selected node. The node took 0.81s, while whole-process wall took 1.18s. `ROW_TIMEOUT_S=4` clears both interpretations: 4 > 3×1.18.
- The first required checker run exposed this lane's direct `checker.write_text(...)` as a prohibited F43 write: `1 failed, 420 passed, 13 xfailed`. The helper now calls the existing T:489 `_rewrite` seam. Both final checker runs and the joint run are green. This is a local test-harness defect found and fixed before accepting evidence.
- The first timeout-control attempts did not reach the timeout because the planted delay changed the classifier shape and the structural test failed immediately. The final control puts the sleep in the selected scratch test body, so collection succeeds and the actual selected node reaches the outer timeout without changing production code.
- GitNexus returned target-not-found/risk UNKNOWN for the old and new structural symbols. Graft and ripwire mapped the test seam; executable tests provide the behavioral evidence. The post-edit clone-index `detect-changes` reported 4 files/12 symbols, 0 affected processes, low risk, but attributed unrelated real-leg symbols because its clone index does not map this detached lane diff reliably.
- Graft does not index the extensionless shell driver. D was inspected by bounded line reads and exercised directly.
- Report lint: `report_lint: 34 refs — OK 25, NEAR 1, MISS 0, UNCHECKABLE 8, UNRESOLVED 0 (worktree)`.

RETRO

- Bug found and fixed: a new scratch-copy helper bypassed the test suite's `_rewrite` write seam and triggered the existing F43 scanner. Anti-pattern class: direct test-fixture writes outside the one mutation seam. The existing guard caught it before final evidence; the coordinator should run `/bug-echo` and register it if the class is not already covered by F43/AF-AP-48.
- Nuance: timeout controls for structural tests must preserve the checked AST through collection and place the delay on an executed path outside that AST. Otherwise the structural guard fails before the timeout instrument fires. This belongs in `anti-hollow-green` under instrument-fired controls.
- Next-time-easier: run the repository's direct-write scanner immediately after adding any test helper that writes a scratch file.
