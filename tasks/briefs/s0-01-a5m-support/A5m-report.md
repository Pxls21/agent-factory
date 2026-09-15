NOT DONE

Independent sandbox adversarial verification has not run. This PC build lane cannot self-accept or issue a gate verdict. No production proof was minted, and no real-corpus bytes were changed.

FILE IDENTITY

Before, at PIN `1231624`:
- C: `0ea35504627a3fec7d913cd7e77be2db592f40cb004a6743a63ea2ca47773b43`, 1907 lines.
- T: `bf7c54112fda613f5e52096e4f9a7cbb25db0425b023722bcbdf0f55c32bc3a5`, 5615 lines.
- P: `41fa933d131ac24701100ba52b8959f3c7d2740b9be4336041388ab891bb83a4`, 629 lines.

After:
- C: `7a13fbffed9fae2cc74be89bd400237a5db25ba0ae477e4e45571a4bfc347bcb`, 1906 lines; the classifier-only docstring was removed so its body is exactly one Return as required, and two nearby dead-branch citations were shifted to the real `raise Failure` guard ending on line 1565.
- T: `70914ea3c4785a722e91e2b35057ea93b62f2d3e9effba9000d7edf552acc491`, 5707 lines.
- P: `41fa933d131ac24701100ba52b8959f3c7d2740b9be4336041388ab891bb83a4`, 629 lines, unchanged and read-only.
- D: `b746a525cfeb539118d4ae5325528dadfb88fb0b583452a0788e6016e5790804`, 154 lines.

VERIFIED

Item 1, F1 exclusivity pin:
- T:2910 states the forbidden shape classes in `test_ck13_checker_has_no_private_pinned_process_predicate`: the CK14 local-helper form, prefilters, conjunctions, and the divergence risk from a second classifier.
- T:2918 pins `len(classifier.body) == 1`; T:2920 requires `ast.Return`; T:2926 requires `ast.GeneratorExp`; T:2933 requires exactly one `comprehension.ifs`; T:2936 pins `pins.is_pinned_argv`; T:2937 pins its only argument to `cmd.split()`; T:2941 rejects `ast.BoolOp` and `ast.Compare` anywhere in the classifier.
- T:2944 builds the module-wide `functions` inventory; T:2953 pins `shared_predicate_users` to `_pinned_process_count`; T:2958 rejects `_is_pinned_process*`; T:2959 rejects `pinned_argv` helper names outside the classifier.
- T:2963 defines `classifier_operands`; T:2972 pins `allowed_compares` for finite non-membership equality checks; T:2992 pins `allowed_predicates` for legitimate membership/boolean checks; T:3016 requires exact `actual_predicates` equality and rejects new classifier-like comparisons, memberships, or boolean wrappers elsewhere in C.
- C's live classifier starts at C:1195 as `_pinned_process_count`; C:1196 is its only statement and returns one `pins.is_pinned_argv(cmd.split())` generator predicate.
- Selected baseline after the final one-Return/allowlist correction: `7 passed, 425 deselected in 0.78s`.

Items 2-3, valid mutation driver and F1 rows:
- D:4-D:7 states the validity contract.
- D:48-D:87 gives every row a fresh `git archive` tree and refuses an edit unless its target changes exactly once and its SHA changes.
- D:89-D:101 compiles every mutated Python file.
- D:103-D:115 requires successful collect-only output with at least one selected test.
- D:117-D:152 runs the named test and accepts a kill only when pytest emits both a `FAILED ...::<test>` node and an `E       ` assertion/exception detail; D:141-D:142 prefers pytest's own exception summary when it is present on the failure line.
- D:152-D:154 emits and gates the five-field summary.
- The TABLE_ROWS row mutates C's `_SCAN_HEADER_RE` from `table_rows=(\d+)` to `rows=(\d+)`; its named test printed `E       Failed: DID NOT RAISE Failure`.
- The required CK14 scratch mutant is one atomic F1_ALT_USE row: it defines `_is_pinned_process_alt(argv)` and consults it before the shared predicate. The other required atomic rows cover the conjunction, named local wrapper plus its use, and dead pin comparison. The two extra rows attack a second shared-predicate user and a second comprehension guard.

Full driver output:

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
KILLED F1_ALT_USE | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck13_checker_has_no_private_pinned_process_predicate | E       AssertionError: assert False
KILLED F1_AND | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck13_checker_has_no_private_pinned_process_predicate | E       AssertionError: assert False
KILLED F1_LOCAL_HELPER_USE | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck13_checker_has_no_private_pinned_process_predicate | E       AssertionError: assert '_pinned_argv_local' == 'pins.is_pinned_argv'
KILLED F1_DEAD_PIN_COMPARE | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck13_checker_has_no_private_pinned_process_predicate | E       assert {('_dead_pin_...XE_REALPATH")} == {('check_env'...XE_REALPATH")}
KILLED F1_SECOND_SHARED_USER | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck13_checker_has_no_private_pinned_process_predicate | E       AssertionError: assert {'_pinned_pro..._shared_user'} == {'_pinned_process_count'}
KILLED F1_SECOND_IF | FAILED tests/test_s0_01_check_acp_conformance.py::test_ck13_checker_has_no_private_pinned_process_predicate | E       AssertionError: assert False
CONTROL_GREEN CONTROL_COMMENT
EXPECTED=19 KILLED=19 SURVIVED=0 INVALID=0 CONTROL=1

Item 4, PC gates:
- Checker file, `1 files set=31306c49985e`, final run 1: `419 passed, 13 xfailed in 263.13s (0:04:23)`.
- Checker file, `1 files set=31306c49985e`, final run 2: `419 passed, 13 xfailed in 285.56s (0:04:45)`.
- Four-file set, `4 files set=a1e3aa327409`, final run: `656 passed, 13 xfailed in 165.87s (0:02:45)`.
- Joint glob, `13 files set=c62435272c99`, final run: `1341 passed, 13 xfailed in 218.34s (0:03:38)`.
- Joint-floor delta: `+0 passed`, `+0 xfailed`; item 1 replaces one test body and adds no test node.
- `python3 -m pyflakes proofs/S0-01/check_acp_conformance.py tests/test_s0_01_check_acp_conformance.py`: rc 0.
- `bash -n tasks/briefs/s0-01-a5m-support/mutants.sh`: rc 0.
- `git diff --check`: rc 0.

INFERRED

- The exact AST inventory is intentionally strict. Any legitimate future identity/config/evidence predicate added to C will require an explicit review and update to T:2972 `allowed_compares` and T:2992 `allowed_predicates`. This is the mechanism that makes the module-wide exclusivity rule fail closed.
- The driver output is build-lane evidence only. Its mutant set and its own results require independent reproduction by the sandbox adversarial-verifier.

ASSUMED

- None. Load-bearing claims above come from this lane's current-tree source reads or command output.

SELF-ATTACK

1. The exclusivity test could remain hollow if it only asserted shared-predicate presence. Ruled out locally by six valid F1 mutations: alternate local classifier before the shared call, conjunction, local wrapper definition/use, dead pin comparison, second shared-predicate user, and second guard. Each compiled, collected the exact structural test, and produced an assertion detail.
2. A mutation row could be counted through an invalid edit or syntax/collection failure. Ruled out locally by D:65 `before`, D:76 `count`, D:89 `py_compile`, and D:103 `--collect-only`; exact one-site replacement, changed SHA, compilation of all mutated Python, and positive named-test collection precede verdict classification. The final summary reports `INVALID=0`.
3. The AST lock could reject current legitimate process-evidence checks or break the real-leg suite. Ruled out locally by the finite baselines at T:2972 `allowed_compares` and T:2992 `allowed_predicates`, plus two identical checker-file outcome counts and the four-file and 13-file PC runs.

DISCREPANCIES

- The initial driver draft exposed three validity defects during its own run: TABLE_ROWS matched the wrong escaped text, AP40 selected a stale test name, and READ_COPY/F1_SECOND_IF generated invalid edits. They were corrected before any evidence was accepted. The final run is the only reported mutation result and has `INVALID=0`.
- One final checker run failed only because removing the classifier docstring shifted two self-referential dead-branch citations by one line: `test_ck11_dead_branch_comments_cite_a_real_guard` reported that the range ending on line 1564 contained no guard. C's two comments now cite the actual range ending on line 1565; the next two checker runs were green.
- Two attempted four-file commands named files not in the brief/tree (`test_s0_01_process_evidence.py`, `test_s0_01_immutable_inputs.py`, `test_s0_01_gate.py`) and correctly returned `no tests ran`, rc 5. The exact brief selection (`test_s0_01_check_acp_conformance.py`, `test_s0_01_pc_tools.py`, `test_s0_01_pc_post_scan.py`, `test_s0_01_acp_probe.py`) then produced the recorded 656-test green.
- The CK14-style premise helper also made three adjacent shared-predicate behavior parameter cases red (`3 failed, 4 passed, 425 deselected in 1.16s`), while CK14 reported all seven selected cases green. The load-bearing F1 premise still reproduced: the old presence-only structural test itself remained green. The final atomic F1_ALT_USE row targets that structural test and dies there.
- A5l's TABLE_ROWS replacement was invalid through SyntaxError. The replacement here changes the compiled regex key and reaches the requested `DID NOT RAISE Failure` assertion.
- GitNexus's clone index returned `Target ... not found` and `risk: UNKNOWN` for `test_ck13_checker_has_no_private_pinned_process_predicate`. The final lane-context pack also reports GitNexus and code-review-graph unmapped, while graft and ripwire mapped the classifier/test definitions and two callers. Ripwire's static test-gate reported subprocess blind spots; the explicit PC pytest runs are the executable evidence.
- The first final-pack command used the second `-s` symbol as a file argument and correctly refused a hollow pack, rc 64. The corrected repeated-`-s` command wrote a 239-line final pack.
- Registry screen: C has 11 pre-existing hits outside edited lines 1195-1196 and 1579/1594; T has four pre-existing hits outside the edited 2909-3016 region; D and the report have zero hits.
- Final report lint: `report_lint: 22 refs — OK 21, NEAR 1, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.

RETRO

- Bug classes found and closed in this lane: AF-AP-78, a mutation counted through invalid syntax; and line-number citation drift after a line-count-changing checker edit. The driver now requires changed bytes, compilation, positive named-test collection, and an actual pytest assertion detail before counting a kill. The existing citation validator caught both shifted guard references.
- Next-time-easier: run the citation validator immediately after any line-count-changing checker edit. The coordinator should run `/bug-echo` and update the incident registry when landing.
- No new reusable skill lesson was needed beyond the existing anti-hollow-green mutation-validity rule. No incident-log or ledger edit was made because those files are outside this lane's boundary.

NOT DONE

- Independent sandbox adversarial verification has not run. This report and diff are a proposal until that separate lane grades the full contract and its own hostile mutants.
- No production proof/result was minted. No corpus recapture was attempted. The known five-leg corpus discrepancy remains the coordinator's VB-F12 work.
- No commit, push, service restart, or outward-facing action was performed.
