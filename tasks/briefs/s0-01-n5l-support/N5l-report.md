# N5l — S0-01 ACP probe round 15 build report

## OUTCOME

PROPOSAL READY FOR ADVERSARIAL VERIFICATION. This PC Hermes build lane implemented all N5l items and self-validated them. It does not issue an independent gate verdict.

PIN: `97bb0c0`

NOT done:

- No commit, push, tag, proof result, or acceptance artifact was created.
- The sandbox-side `adversarial-verifier` has not graded this proposal.
- No Buzz, ACP, Hermes, or owner service was launched or changed.

## EVIDENCE TIERS

### VERIFIED

- The `READ_NOFOLLOW_DROP` premise reproduces behaviorally: the mutated `_read_regular` follows a final symlink and returns known bytes; the real fixture-loader chain exits 0 with empty stderr after following that symlink.
- The landed `_read_regular` rejects the same final symlink with `errno.ELOOP`, and the real caller chain emits its exact named refusal.
- The actual probe `Popen` uses explicit `close_fds=True` at `probe:371-374`.
- The real-emitter census writes `CENSUS=0\n` on landed bytes and `CENSUS=1\n` under the three-part fd-leak mutant.
- All 10 hostile driver rows died; its control stayed green; no mutant was invalid.
- Final serial, four-file, and 13-file PC runs completed with rc 0.

### INFERRED

- No adjacent S0-01 regression was detected by the required suites. This does not replace the separate verifier.
- The final patch has medium blast radius according to GitNexus `detect-changes`; its three reported flows all originate from `main`.

### ASSUMED

- The read-only real-leg directory and venue exports supplied by the dispatcher are the intended N5l inputs.

## FILE IDENTITY

### PIN

```text
e71ec3cfc7db220424b08fb90070166983c35a69cdc6cd78270dc216db9d3726  proofs/S0-01/tools/acp_probe.py  677 lines
ee29b9584fdc3908ad57ea5e6b1c6c6a34d302d664b45363f3597d6e9435e617  tests/test_s0_01_acp_probe.py  3592 lines
```

### FINAL

```text
f42a9025ba5436c0109ad601709a1730c9a78880d4647e74fc7734ca135ec6b2  proofs/S0-01/tools/acp_probe.py  678 lines
6d5da2b2ed0da69b931328f29c4193dab79c558d59b3494e212a45a5ed2d65e5  tests/test_s0_01_acp_probe.py  3868 lines
376105ab9258fa44608b2021ac6601c99cae06f40d9c70d9d7334e9c371b39bd  tasks/briefs/s0-01-n5l-support/mutants.sh  141 lines
```

## ITEM 0 — PREMISE

Before editing, a private scratch probe loaded the `READ_NOFOLLOW_DROP` mutant from the lane scratch directory. Direct `_read_regular` returned `b'N5L-KNOWN-CONTENT'`; the real fixture-loading caller exited `rc=0` with empty stderr. The landed primitive refused the same direct shape with `errno=40`, equal to `errno.ELOOP`, without returning the content.

Code intelligence mapped `_read_regular` to `_sha256_file`, `_write_evidence`, module hashing, and `main`. Ripwire independently reported those reaches. The clone GitNexus index did not map this PIN's `_read_regular`; that risk remained UNKNOWN before edit and is reported below.

## ITEM 1 — FINAL-SYMLINK RED

The direct test at `test:3652-3673` creates a regular file with known bytes and a final-component symlink. It asserts `caught.value.errno == errno.ELOOP` at `test:3661-3669`, asserts `returned_content is None` there, and rechecks the target bytes at `test:3669`.

The real fixture-loader test at `test:3672-3702` replaces `neg-malformed-initialize.json` with a final symlink. It builds exact `expected` stderr and asserts `result.returncode == 64`, `result.stderr == expected`, empty stdout, and absent `runtime-identity.json` at `test:3696-3702`.

The behavioral scratch mutation at `test:3768-3795` drops `O_NOFOLLOW`, loads that exact mutated file, and observes its known content. It does not use a source substring as the oracle. Driver evidence:

```text
KILLED READ_NOFOLLOW_DROP rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_regular_refuses_final_symlink_with_eloop
```

## ITEM 2 — V3 READ-PRIMITIVE PORTS

- Regular bytes: `test_probe_read_primitive_reads_a_regular_file` at `test:3705-3711` asserts exact `b"abc123"`.
- Named refusals: `test_probe_read_primitive_refuses_named_non_regular_shapes` at `test:3737-3768` covers FIFO, directory, `/dev/zero`, and AF_UNIX socket. It asserts `str(caught.value) == expected` at `test:3768`.
- FD closure: `test_probe_read_primitive_leaves_no_fd_on_refusal` at `test:3771-3787` records the whole `/proc/self/fd` set, asserts `fd_delta == 0`, and asserts exact set equality.
- Existing isolated `F_SETFD` control remains at `test:3508-3576`; no duplicate v3 isolated control was added.

The AF_UNIX test initially used the long pytest basetemp path and failed before `_read_regular` with `OSError: AF_UNIX path too long`. The fixture now obtains a short `/tmp/n5l-sock-*` path through `_short_unix_socket_path` at `test:257-258`. The deterministic negative control at `test:3718-3734` reproduces the exact long-path refusal and confirms that the helper's path is shorter. Cleanup calls `held_socket.close()`, `target.unlink()`, and `target.parent.rmdir()` at `test:3765-3767`.

Driver evidence for the ported contracts:

```text
KILLED READ_NONBLOCK_DROP rc=124 FAILED <timeout> - bounded timeout
KILLED READ_SISREG_DROP rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_refuses_named_non_regular_shapes[devzero]
KILLED READ_NO_CLOSE_ON_REFUSAL rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_leaves_no_fd_on_refusal
KILLED CLOSE_BEFORE_FSTAT rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_reads_a_regular_file
KILLED NONREG_ERROR_TEXT rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_refuses_named_non_regular_shapes[devzero]
KILLED FD_CLOSE_REDIRECT rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_leaves_no_fd_on_refusal
```

## ITEM 3 — REAL-EMITTER CENSUS

The census agent at `test:3820-3849` reads its own `/proc/self/fd`, resolves directory descriptors, and writes `CENSUS=<n>\n`. `test_probe_census_agent_sees_no_framedir_fd_on_final_bytes` launches that agent through the real `_run_probe`/`Popen` chain at `test:3852-3867`. It requires rc 0, an emitted census file, and exact `CENSUS=0\n` at `test:3862-3867`.

The `FD_LEAK_TRIPLE` row removes framedir `O_CLOEXEC`, calls `os.set_inheritable(framedir_fd, True)`, and sets `close_fds=False` in one scratch copy. It died with:

```text
KILLED FD_LEAK_TRIPLE rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_census_agent_sees_no_framedir_fd_on_final_bytes
AssertionError: the real agent inherited the framedir fd: 'CENSUS=1\n'
```

## ITEM 4 — EXPLICIT CLOSE_FDS UNDER A SCOPED PIN

The production launch is explicit at `probe:371-374`: `stderr=subprocess.PIPE, close_fds=True`.

`_agent_popen_close_fds_value` at `test:3579-3608` parses the AST, selects only a `subprocess.Popen` assigned to `proc`, refuses `**kwargs`, requires exactly one `close_fds` keyword, and recognizes only literal booleans. The test at `test:3611-3632` requires literal True. Its inline comment mutant proves that `close_fds=False  # close_fds=True` remains false under the parser. There is no file-wide `in source` oracle.

```text
KILLED CLOSE_FDS_FALSE rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_agent_launch_pins_the_close_fds_default_second_defence
KILLED CLOSE_FDS_COMMENT_ONLY rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_agent_launch_pins_the_close_fds_default_second_defence
```

## ITEM 5 — MUTATION DRIVER

`tasks/briefs/s0-01-n5l-support/mutants.sh` archives PIN `97bb0c0`, overlays the final probe and test, and uses one fresh tree per row at `driver:32-39`. `mutate_exact` requires exactly one anchor at `driver:41-54`. Each mutant must pass `python3 -m py_compile` and `--collect-only` at `driver:81-94`; failures increment `invalid` and print `INVALID` at `driver:96-100`. The FIFO mutant runs under `timeout 15s` at `driver:102-110`. The summary and final zero-invalid/zero-survivor/one-control assertion are at `driver:138-141`.

Final full output:

```text
KILLED READ_NOFOLLOW_DROP rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_regular_refuses_final_symlink_with_eloop
KILLED READ_NONBLOCK_DROP rc=124 FAILED <timeout> - bounded timeout
KILLED READ_SISREG_DROP rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_refuses_named_non_regular_shapes[devzero]
KILLED READ_NO_CLOSE_ON_REFUSAL rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_leaves_no_fd_on_refusal
KILLED CLOSE_BEFORE_FSTAT rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_reads_a_regular_file
KILLED FD_LEAK_TRIPLE rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_census_agent_sees_no_framedir_fd_on_final_bytes
KILLED CLOSE_FDS_FALSE rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_agent_launch_pins_the_close_fds_default_second_defence
KILLED CLOSE_FDS_COMMENT_ONLY rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_agent_launch_pins_the_close_fds_default_second_defence
KILLED NONREG_ERROR_TEXT rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_refuses_named_non_regular_shapes[devzero]
KILLED FD_CLOSE_REDIRECT rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_leaves_no_fd_on_refusal
CONTROL_GREEN CONTROL_COMMENT
EXPECTED=10 KILLED=10 SURVIVED=0 INVALID=0 CONTROL=1
```

`NONREG_ERROR_TEXT` and `FD_CLOSE_REDIRECT` are the two added rows on the ported contracts. The control changes a docstring only and stays green.

## ITEM 6 — PC GATES

Environment used: `S0_01_VENUE=pc`, read-only `S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`, `/home/rocco/venv-agent-factory/bin` first on PATH, and an absolute lane-scratch basetemp.

Two complete post-port serial runs before the final fixture negative control:

```text
123 passed in 51.27s
1 files set=a5097bab1417
123 passed in 51.05s
1 files set=a5097bab1417
```

Final serial run after all edits:

```text
124 passed in 51.36s
1 files set=a5097bab1417
```

Four-file xdist set after all edits:

```text
667 passed, 13 xfailed in 148.75s (0:02:28)
4 files set=a1e3aa327409
```

Thirteen-file xdist set after all edits:

```text
1352 passed, 13 xfailed in 234.53s (0:03:54)
13 files set=c62435272c99
```

The PIN floor was 113 serial and `1341 passed, 13 xfailed` across 13 files. Final delta is +11 passed, with xfails unchanged. `python -m pyflakes proofs/S0-01/tools/acp_probe.py tests/test_s0_01_acp_probe.py` returned rc 0. `bash -n` and `git diff --check` returned rc 0.

## SCREENS AND BLAST RADIUS

Whole-file screen results:

- Probe: eight pre-existing hits, unchanged classes: AF-AP-55 ×3 at lines 393, 469, and 560; AP-1 ×2; AP-32 ×2; AP-24 ×1.
- Test: one pre-existing AF-AP-57 hit at line 1448 in the transient-readlink bounded-count rig.
- Driver: one AF-AP-70 lexical hit at `driver:22`, where the driver deliberately names and mutates `fstat`; classified as a mutation fixture, not production stat-before-open behavior.

The final lane context pack was written at `../scratch/n5l/final-pack2.md`. Graft mapped the target symbols. Ripwire reported `_short_unix_socket_path` as a new two-caller helper and no incompatible callers. GitNexus `detect-changes` reported six visible worktree files, two indexed changed symbols, three affected flows, and `Risk level: medium`. Its clone index could not map new/PIN-only symbols, so those individual impacts remain `risk: UNKNOWN`, not low.

## SELF-ATTACK

1. **The final-symlink test could inspect source instead of behavior.** Ruled out by loading and executing the scratch mutant: `The scratch mutation drops O_NOFOLLOW` and then asserts `observed == content` at `test:3793-3795`. The independent driver also kills `test_probe_read_regular_refuses_final_symlink_with_eloop`.

2. **The fd census could test an artificial fork/exec path rather than the production launch.** Ruled out because the new census calls `_run_probe` at `test:3856`, which invokes the probe process; the probe launches the census agent through the real `subprocess.Popen` at `probe:371-374`. The three-part mutant changes that production launch and produces exact `CENSUS=1\n`.

3. **A comment could satisfy the close_fds guard.** Ruled out because `_agent_popen_close_fds_value` parses `ast.Assign` and the selected `Popen` keywords at `test:3579-3608`, and by the `CLOSE_FDS_COMMENT_ONLY` row. The actual keyword is false while the comment still contains `close_fds=True`; the pin stays red.

## DISCREPANCIES

- The brief says `close_fds` absent or True passes while also requiring explicit `close_fds=True`. The final pin requires exactly one literal True so deleting the explicit keyword cannot survive. This is stricter than the phrase “absent or True” and matches the explicitness requirement.
- The initial AF_UNIX fixture inherited the lane's long absolute basetemp and failed with exact `OSError: AF_UNIX path too long`. The fixture now uses a short private `/tmp` directory and has its own negative control.
- The first two mutation-driver attempts exposed delimiter and anchor defects in the new driver and were INVALID. They were fixed before grading. Final output is `INVALID=0`; no invalid attempt was counted as a kill.
- The first two `lane_context.sh` attempts passed multiple `-s` symbols incorrectly and returned rc 64. The corrected invocation used one `-s` per symbol and wrote `final-pack2.md`.
- GitNexus per-symbol impact did not map PIN-only/new symbols and returned `risk: UNKNOWN`. `detect-changes` did run after the final edit batch and reported medium aggregate risk.
- The report lint result is: `report_lint: 33 refs — OK 30, NEAR 3, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.

## REASONING RECORD

Rejected alternative: port the v3 file-wide substring assertion. It lets a comment satisfy the gate (AF-AP-80). The chosen AST selector binds the assertion to the `subprocess.Popen` assigned to `proc`.

Ordering: establish the behavioral symlink red first; port normal/refusal/fd-close tests; add the real-emitter census; make `close_fds=True` explicit under the scoped pin; then grade each claim with compile-and-collect-validated mutants. This keeps each green tied to an independently observed negative.

Primary sources: the executable probe and tests at PIN `97bb0c0`, arm B's `N5k-xhigh-v3.diff`, and VERIFY-N5k's measured report. Comments were checked against the executed paths rather than accepted as evidence.

Disjoint hunks: production changes only the real `Popen` keyword at `probe:371-374`; test ports and hostile rigs occupy the N5l block plus the short socket helper; the driver is a new support file. No unrelated source was edited.

## RETRO

Bug found: long absolute pytest basetemps can exceed AF_UNIX's pathname limit and make a socket-shape test fail before its intended oracle. Anti-pattern class: fixture fails before instrument. The new test now reproduces the failure class and asserts the short-path fixture seam. This should be echoed by the coordinator into the incident registry if accepted.

No further skill or tooling change belongs in this lane. The `lane_context.sh` one-`-s`-per-symbol CLI mismatch is already stated as a discrepancy for coordinator review.
