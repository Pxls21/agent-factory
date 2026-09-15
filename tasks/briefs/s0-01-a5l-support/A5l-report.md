PROPOSAL — A5l checker round 14

NOT-DONE

- Independent sandbox adversarial-verifier grading is not done. This build-lane output is a proposal, not an acceptance verdict.
- Two single-run archive-copy gates completed with identical counts after the combined `-n 2` invocations exceeded the tool cap:
  - `RESULT: rev=d23762adfaa1 files=5 deleted=0 runs=1 identical=yes rc=0 summary="535 passed, 13 xfailed in 145.24s (0:02:25)"`
  - `RESULT: rev=d23762adfaa1 files=5 deleted=0 runs=1 identical=yes rc=0 summary="535 passed, 13 xfailed in 141.32s (0:02:21)"`
- No live Buzz, ACP, Hermes, tee, relay, or model execution was performed, per brief.

FILE IDENTITY

- `proofs/S0-01/check_acp_conformance.py`: sha256 `0ea35504627a3fec7d913cd7e77be2db592f40cb004a6743a63ea2ca47773b43`, 1907 lines.
- `tests/test_s0_01_check_acp_conformance.py`: sha256 `bf7c54112fda613f5e52096e4f9a7cbb25db0425b023722bcbdf0f55c32bc3a5`, 5615 lines.
- `tests/test_s0_01_audit_cp5_controls.py`: sha256 `457430b171230ffc464091560bdda88514c3ccc5961d89562cd5d3a74edf9f5a`, 144 lines; byte-unchanged.
- `tasks/briefs/s0-01-a5l-support/mutants.sh`: sha256 `d13bef2b0334c54832e95c4fcb4b806bccb04bc1036cae46077a04058d66b24c`, 79 lines.
- `tasks/briefs/s0-01-a5l-support/red-before.patch`: sha256 `f4e1c860a10c38525f5e54a803ca5024c3a1dcfca5719843280b4e9efb4ef96e`, 34 lines.
- `proofs/S0-01/pins.py`: read-only and byte-unchanged, as required.

VERIFIED

- Premise reproduced from the committed CK13 verifier report: private process classifier; local corpus-version inference; open scanner domains; representative-only set checks; M14/M16/M21 survivors; non-integer `SystemExit` conversion gap.
- ONE process list: `check_process_evidence` now passes scan command argv through `pins.is_pinned_argv` via `_pinned_process_count` (`C:1195`); the private `_is_pinned_process` and direct pinned-path imports are removed.
- Strict versions: checker `_captured_leg_version` (`C:1683`) and test `_corpus_version` (`T:2676`) both call `pins.corpus_version`; unknown and mixed versions fail by leg name. v2.2 runtime identity xfails only the exact tee checksum mismatch in `test_real_leg_runtime_identity` (`T:2968`); any other mismatch fails.
- ONE file list: checker allowlists derive from `required = pins.required_files(captured_version)` (`C:1775`) plus `allowed = pins.entry_allowlist()` (`C:1774`). `test_ck12_pinned_required_file_cannot_be_dropped` (`T:5368`) pins complete v2.2/v2.3 required sets and full allowlist, including `argv.txt=required` and `teardown.txt=optional`.
- Scanner domains: `_scan_direct_writes` (`T:3636`) covers bound `Path.open`, `os.link/symlink`, `shutil.move`, and tar/zip extract calls. `_presence_gate_hits` (`T:5001`) covers `stat`, `os.stat`, `getsize`, `isfile`, `glob`, and `next(..., default)`. `_enumerate_read_sites` (`T:5186`) covers `os.fdopen`, `io/gzip/open`, bound path opens, pickle/json loads, copy sources, and subprocess input consumers. Each scanner states exclusions.
- Dead-branch validator `_validate_dead_branch_citations` (`T:5525`) checks every comment block and names citationless, wrong-function, out-of-range, later, and non-guard citations. `_read_site_drift` (`T:5280`) reports both added and removed sets. M14, M16, and M21 are killed by name.
- VB-F12: `_parse_scan_v24` keeps `rows` and `table_rows` distinct (`C:1172`); an explicit key-replacement negative control fails (`T:2516`).
- CLI exit status domain: `except SystemExit as se` (`C:1894`) preserves integer values; `failure_reason: check exited with a non-integer status` (`C:1899`) then returns 70. `test_ck13_main_closes_system_exit_status_domain` (`T:2856`) pins `None -> 70`, `0 -> 0`, `7 -> 7`, and text -> 70.

TEST EVIDENCE

- Focused changed-test run: `53 passed, 377 deselected in 4.42s`, exit 0.
- Headline xdist run: `419 passed, 13 xfailed in 134.76s (0:02:14)`, `headline_rc=0`.
- Four-file xdist run: `535 passed, 13 xfailed in 145.18s (0:02:25)`, `four_file_xdist_rc=0`.
- Mutation driver: `EXPECTED=13 KILLED=13 SURVIVED=0 CONTROL=1`, exit 0. The comment-only negative control was green.
- Pyflakes over the three boundary Python files: `pyflakes_rc=0`.
- `git diff --check`: `diff_check_rc=0`.

INFERRED

- The checker now cannot drift from the producer's process identity semantics without changing the shared `pins.is_pinned_argv` predicate or bypassing `_pinned_process_count`; AST tests prohibit a second private predicate.
- Complete set equality makes required/optional status flips observable rather than only protecting representative names.
- Read and write inventories remain finite AST domains, not proofs against dynamic wrappers, shell parsing, monkey-patched methods, or custom serializers. Those exclusions are explicit in code.

ASSUMED

- `pins.py` remains the canonical producer-side contract and its v2.2/v2.3 values are valid; this lane was forbidden to edit it.
- The read-only real-leg corpus at `/home/rocco/s0-01-pinned/realleg/golden` remains the intended PC corpus.

SELF-ATTACK

1. Wrong classifier seam. Ruled out by monkey-patching `pins.is_pinned_argv`, asserting exact argv received for five token-boundary cases, and AST prohibition of another checker predicate.
2. Scanner appears closed but misses requested syntax. Ruled out by one self-test case per declared syntax family and mutation rows for presence, fd/open class, copy, subprocess, link, move, and archive extraction.
3. Tests can bless their own expected set. Reduced by exact set literals, bidirectional set difference, M21 mutation, required/optional status mutations, and an independent comment-only control. Independent verifier review remains required.

DISCREPANCIES

- Brief path names under `proofs/S0-01/tools/` were stale. Actual files are directly under `proofs/S0-01/`.
- The first direct four-file command used nonexistent `tests/test_s0_01_proof_runner.py` and `tests/test_s0_01_proof_status.py`; it returned `no tests ran`, rc 5. The governing brief's actual four files were then run and passed as reported above.
- Both combined `lane_gate.sh -n 2` attempts exceeded the tool's fixed 420-second execution cap before a RESULT line. Two equivalent fresh archive-copy `-n 1` runs then completed with identical counts and rc 0; their separate RESULT lines are above. This deviates from the requested one-call shape but preserves independent static-copy executions.
- Post-edit code-intel pack invocation exposed a script argument parsing quirk: symbols after the first were treated as files, graft indexed only excluded paths, GitNexus reported index absent in the pack, and CRG reported graph absent. Ripwire still mapped `_pinned_process_count` to two callers and mapped three callers each for the extracted validators. Earlier direct GitNexus impact ran against the clone index.
- `ripwire_review.sh edit-check` is not a supported subcommand in this wrapper and exited 1. The valid `lane_context.sh` pack and direct `detect-changes` were run instead.
- Final report lint: `17 refs — OK 17, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`, rc 0.
- AP screen reports 11 existing checker hits (AF-AP-40 five, AF-AP-72 four, AP-32 two), four test hits (AP-66 two, AF-AP-48 one, AF-AP-57 one), and zero audit-test hits. Changed scanner paths are self-tested; adjacent pre-existing hits were not edited outside brief scope.
- `tests/test_s0_01_audit_cp5_controls.py` needed no source change; the requested owned-survivor and malformed-header behavior was already present and is included in passing gates.

REASONING RECORD

- Rejected duplicating producer constants in checker code because that recreates the drift the brief targets.
- Kept scanner implementation finite and syntax-explicit rather than claiming semantic completeness.
- Kept `pins.py` read-only. Missing shared helpers would have stopped the lane; both required helpers existed.
- Source pin: `d23762a`. Report timestamp: `2026-09-15T09:51:27Z`.

RETRO

- Bug class: gate scanner domain omitted syntactic siblings and could issue a hollow green. Existing AF-AP-40/42/63/64/65/72 classes cover it; coordinator should run bug-echo before landing.
- Proposal requires contract-gate plus independent sandbox adversarial verification. No new reusable skill lesson beyond the existing anti-hollow-green scanner/mutation rules.
