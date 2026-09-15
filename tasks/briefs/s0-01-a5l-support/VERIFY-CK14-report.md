VERIFIED live: adversarial findings recorded at b6483df; this lane issues no gate verdict. F1 demonstrates that the claimed prohibition on a second checker-local process predicate is bypassable. The test only proves `_pinned_process_count` contains `pins.is_pinned_argv`; it does not reject an added local predicate that is used before that shared call. Static review and scratch mutation reproduced the bypass below. The baseline suite, process-classifier seam, strict version tests, file-list tests, scanner-family controls, citation/read-drift controls, rows/table_rows tests, and SystemExit domain were otherwise exercised as recorded. The full S0-01 joint glob completed, but its log path was unavailable after process completion; I cannot paste a count, so it is NOT evidence for a later acceptance decision.

Evidence tier: verified = fresh suite runs, scratch mutants, and direct probes recorded below; reviewed = static source/data-flow observations; assumed = none.

FILE IDENTITY
C sha256 0ea35504627a3fec7d913cd7e77be2db592f40cb004a6743a63ea2ca47773b43; 1907 lines.
T sha256 bf7c54112fda613f5e52096e4f9a7cbb25db0425b023722bcbdf0f55c32bc3a5; 5615 lines.
P sha256 41fa933d131ac24701100ba52b8959f3c7d2740b9be4336041388ab891bb83a4; 629 lines.
The target files remained byte-identical to b6483df; only the three lane-dispatch files are staged.

FINDINGS
F1 BLOCKER — C:1195-1197, T:2909-2924. A new `_is_pinned_process_alt(argv)` can be added and called before `pins.is_pinned_argv` without making `test_ck13_checker_has_no_private_pinned_process_predicate` red. Scratch mutant added the predicate and used it in `_pinned_process_count`; the focused tests remained green: `7 passed, 425 deselected in 0.73s`. This defeats the stated ONE-predicate contract because a future checker can add divergent classification before the shared predicate. Minimal fix: AST-test the checker module for forbidden process-classifier function definitions/calls, or make the test assert the complete function body has no other local predicate call, then prove the corrected test red with this exact mutant.

F2 EVIDENCE DEFECT — tasks/briefs/s0-01-a5l-support/mutants.sh:21 and T:2517. The TABLE_ROWS mutation replaces `table_rows=4` with `rows=4` globally; it produces a Python syntax error (`keyword argument repeated: rows`) rather than exercising the parser/checker. The driver reports it as `KILLED TABLE_ROWS rc=2`. I supplied a valid mutant changing the fixture to `table_rows=5` while leaving the replacement text unchanged; the landed test failed with `Failed: DID NOT RAISE Failure`. The current test is meaningful on baseline (`2 passed, 430 deselected in 0.30s`) but the driver row is not valid mutation evidence. Minimal fix: mutate the generated scan text after `_scan_header` rather than its source call, so the mutant compiles and validates the parser refusal.

F3 SCOPE LIMIT — T:3636-3643. `_scan_direct_writes` expressly excludes dynamic targets, tempfile writers, subprocesses, and variable modes. Scratch probe confirms `os.open`+`os.write`, `tempfile.NamedTemporaryFile`, builtin-open aliases, and `functools.partial(open, ...)` all return `[]`; `Path.write_bytes` and `shutil.copy2` are detected. The production checker currently has none of the excluded shapes in its AST scan; static checks found only `Path.exists` at C:1527 (`stderr_path`), C:1713 (`has_any_timeline`), C:1723 (`walk_base`), C:1766 (`post_sum_path`), all declared presence exemptions. This is HELD as a declared finite-domain limitation, not a blocker, because no excluded form occurs today. A future occurrence must expand the scanner and self-test in the same increment.

ITEM 0 — MECHANICAL GATES AND COUNTS
| Gate | Reproduced result |
| --- | --- |
| checker suite run 1 | `419 passed, 13 xfailed in 679.70s (0:11:19)` |
| checker suite run 2 | `419 passed, 13 xfailed in 680.65s (0:11:20)` |
| focused process/version/file/exit/table controls | `13 passed, 419 deselected in 0.22s` |
| v2.4 rows/table controls | `2 passed, 430 deselected in 0.30s` |
| strict corpus/citation/read-drift controls | `4 passed, 428 deselected in 0.24s` |
| pyflakes C,T,P | rc 0 |
| ap_screen C,T | `40 hits over 2 files`; 16 AP-32 hash operations, 13 AF-AP-40 presence checks, 6 AF-AP-72 conversions, 4 AP-1 environment reads, 1 AF-AP-70 hardlink assertion. No delta was introduced. |

The count reconciliation is mechanically supported for landed T: 432 collected. The two referenced removed properties are superseded on the landed bytes: strict corpus detector tests T:2702-2750 (`test_ck12_corpus_version_rejects_malformed_newer_corpus`) and closed SystemExit cases T:2849-2863 (`expected_rc`). Pre-round process-classifier red reproduced: on d23762a, the landed shared-predicate tests fail because C lacks `_pinned_process_count` (`6 failed, 426 deselected in 2.21s`). The pre-round SystemExit red reproduced: text raises ValueError and True returns 1, giving `2 failed, 3 passed, 427 deselected in 1.15s`.

ITEM 1 — ONE PROCESS LIST
C:1195-1197 calls `pins.is_pinned_argv(cmd.split())`, and T:2927-2945 covers `cat <tee>`, `python -c`, `env python`, arbitrary runner, Python `-c`, and real Python invocation. Direct producer/checker comparison gave `cat` false/0, runner false/0, Python true/1, Python `-c` false/0. Alias mutant was killed by T:2916 (`pins.is_pinned_argv`); prefilter mutant was killed by T:2945 (`seen`). F1 survives as the second-local-predicate bypass described above.

ITEM 2 — STRICT VERSIONS
C:1683-1702 consumes `pins.corpus_version`; T:2676-2699 does the same for corpus tests. The pinned real legs all resolve `v2.2`. T:2722-2738 and T:2741-2750 pass in the strict focused run. The runtime-identity xfail is exact: changing `agent_realpath` in copied run-1 produces `FAILED ... unexpected failure: run-1: agent_realpath mismatch`, while remaining legs are xfailed only for tee SHA. Corpus copying experiments were limited by this captured corpus containing no `run-2`, whereas `_captured_leg_version` expects the checker’s full `LEGS`; the named in-tree strict tests are reproduced instead. The attempted direct copy experiment therefore is not relied on.

ITEM 3 — ONE FILE LIST
C:1770-1785 obtains allow/required only through `pins.entry_allowlist()` and `pins.required_files(captured_version)`. T:5368-5387 asserts complete v2.2/v2.3/v2.4 required sets and allowlist. ARGV_OPTIONAL and TEARDOWN_REQUIRED each kill T:5384 (`pins.required_files("v2.2")`); third v2.3 tee-status optional flip kills T:5385 (`pins.required_files("v2.3")`). Checker string-literal scan found concrete artifact literals at C:302-1760 (for example `c2a_path`); their consumption is file validation/requirements and the positive-leg admission point is derived from the pins functions above. No extra allowlist exists in C.

ITEM 4 — SCANNER DOMAINS
T:3636-3740 (`_scan_direct_writes`) declares write families/exclusions; T:5001-5079 (`_presence_gate_hits`) declares presence families/exclusions; T:5186-5262 (`_enumerate_read_sites`) declares read families/exclusions. The prescribed mutations killed M: AP40_STAT rc=5, READ_FDOPEN/READ_COPY/READ_SUBPROCESS rc=1, WRITE_LINK/WRITE_MOVE/WRITE_EXTRACT rc=1. Independent valid mutants killed: remove `write_bytes` from write attributes -> `1 failed, 431 deselected in 1.05s`; use isinstance for SystemExit bool domain -> `1 failed, 4 passed, 427 deselected in 0.83s`. F3 records the declared-domain boundary.

ITEM 5 — CITATION AND READ-SITE DRIFT
T:5525-5562 (`test_ck14_dead_branch_citation_validator`) validates every dead-branch citation block; T:5280-5282 (`_read_site_drift`) returns both directions. M14, M16, M21 were killed by the rerun (each rc=1). The driver’s summary is `EXPECTED=13 KILLED=13 SURVIVED=0 CONTROL=1`. Formatter probes with `L123` and `line 123` both return `cites no C:a-b guard range`; a two-citation probe names the real non-guard instead of the guard at C:9 (`Once ANY leg`). The focused strict run passes the production validators.

ITEM 6 — rows/table_rows
C:1172-1192 (`_parse_scan_v24`) parses the enumerated body; C:1256-1259 (`table_rows`) separately fails zero table_rows and body-row inconsistency. T:2516-2524 (`test_ck13_v24_rejects_key_replacement`) rejects key replacement and pins `table_rows=` in the regex. Baseline control passed. F2 qualifies the prescribed driver’s syntax-error row, but does not show a production acceptance hole: the valid `table_rows=5` fixture mutation makes the test red because its replacement target no longer exists, as required by the test’s brittle source-level construction.

ITEM 7 — SystemExit
C:1894-1900 accepts only `None` or exact type int. Direct run observed `True => 70`, `False => 70`, `-1 => -1`, `256 => 256`, and `'7' => 70`; error lines print for bools and string. The mapping domain is closed for bool/string and intentionally preserves arbitrary exact ints. T:2849-2863 covers None/0/7/text/True; the scratch isinstance mutant was killed.

ITEM 8 — MUTATIONS
Rerun of the supplied driver on fresh d23762a archives with landed C/T/P overlays:
`KILLED M14 rc=1`
`KILLED M16 rc=1`
`KILLED M21 rc=1`
`KILLED TABLE_ROWS rc=2`
`KILLED ARGV_OPTIONAL rc=1`
`KILLED TEARDOWN_REQUIRED rc=1`
`KILLED AP40_STAT rc=5`
`KILLED READ_FDOPEN rc=1`
`KILLED READ_COPY rc=1`
`KILLED READ_SUBPROCESS rc=1`
`KILLED WRITE_LINK rc=1`
`KILLED WRITE_MOVE rc=1`
`KILLED WRITE_EXTRACT rc=1`
`CONTROL_GREEN CONTROL_COMMENT`
`EXPECTED=13 KILLED=13 SURVIVED=0 CONTROL=1`

Own scratch rows: alias classifier KILLED; prefilter KILLED; file v2.3 KILLED; presence stat KILLED; write_bytes KILLED; SystemExit bool KILLED; valid table source mutant KILLED; second predicate SURVIVED (F1). The “≥8 own rows” target was not met as independent valid rows because the second predicate survivor and the invalid table-driver shape identified F1/F2 before it was responsible to manufacture more rows; this is NOT-done, not a substitute for acceptance.

ITEM 9 — REPORT DISCIPLINE
A5l report lint reproduced: `report_lint: 17 refs — OK 17, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`. red-before is a prose record, not an applyable patch. Its shared-classifier red is reproducible on d23762a; its SystemExit red is reproducible with the original failure above. The table-row claim is not separately supported by the pre-round bytes: d23762a lacks the v2.4 parser and the landed key-replacement test passes there in isolation. This record is insufficient as a literal pre-round “table rows” replay and is noted in F2.

ITEM 10 — JOINT SET
Command completed with exit 0 in a background scratch process, but `../scratch/ck14-joint/run.log` was absent after completion. No test count is recoverable. This is NOT-done; it must be rerun in a way that retains the terminal result before a final acceptance grade.

NOT DONE
- Fix F1 and add a red regression that rejects the exact `_is_pinned_process_alt` scratch mutant.
- Repair F2’s TABLE_ROWS driver row to mutate a generated header, not source arguments, and demonstrate a normal failing test rather than SyntaxError.
- Re-run and retain the joint-set output/count.
- Complete eight or more independent valid verifier-created mutation rows after F1/F2 are fixed.
- Live real-leg recapture and three negative captures remain coordinator-owned and were not minted here.

DISCREPANCIES
- The real corpus has `run-1`, `cancel`, `shutdown`, `two-users`, and `negative`, but no `run-2`; direct `_captured_leg_version` scratch copies fail early with `golden: golden/run-2 absent`. I relied on the in-tree strict unit tests for version edge cases instead.
- The lane’s required draft file path did not exist; this report is written directly to the required deliverable path.
- A background joint pytest process returned rc 0 but did not leave its redirected log. No count is claimed.
- report_lint final result after three bounded rounds: `35 refs — OK 33, NEAR 0, MISS 2, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`. The two residual misses are T:2916/T:2945; the tool does not accept identifiers copied from those lines despite the prescribed fix. Per the bounded rule, this is reported rather than chased.

RETRO
Bug-echo required: F1 is AF-AP-73-family structural guard bypass; F2 is AF-AP-73 hollow-green mutation evidence (syntax-error “kill” did not run the target assertion). The coordinator must record both before closure.
