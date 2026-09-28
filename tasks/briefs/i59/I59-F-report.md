# I59-F report (task #335): the proof-code follow-ups before the owner's re-sign

Written 2026-09-28 14:4xZ by the sandbox build lane (code-implementer, Opus 5.5). Worktree `/home/user/i59-landing`,
HEAD d433571 (docs-only commits past the PIN; see D1). No git write, no push, no PC bridge, no subagent.

Aliases for every `file:line` below (working tree unless written `alias@c32ac3f:NN`):
C = `proofs/S0-03/check_omniroute_roundtrip.py`, T3 = `tests/test_s0_03_omniroute.py`,
R = `proofs/S0-05/tools/pc/run_s0_05_units.sh`, T = `tests/test_s0_05_egress.py`,
T4 = `tests/test_s0_04_compression.py`, W = `.github/workflows/stage0-ci.yml`, NL = `tests/test_no_laya_in_gates.py`,
GW = `tests/test_gpu_window.py`, CC = `proofs/S0-04/check_compression.py`.

## TL;DR

- All ten contract items are built and gated. New tests: 22 in T, 4 in T3, 4 in T4. The CI line and its pin changed.
- Gates, each run twice with its set id: T3 `213 passed`, T4 `182 passed`, NL `121 passed`, T `319 passed`.
- Mutation table: `EXPECTED=19 KILLED=19 SURVIVED=0 INVALID=0`. It includes the verifier's X6, C-X4, C-X6 and E-X7.
- Task #331: with INT, HUP and QUIT ignored at launch, the four named tests went `4 failed in 175.76s` before the
  shim and `4 passed in 11.53s` after it. The whole of T under that launch: `319 passed`.
- **Adjacent defect A-1 (containment, verified, NOT fixed): `S0_05_UNIT_USER=4294967296:4294967296` runs the unit as
  root.** It is B-4's class at a seam the brief does not name. Only the post-launch A7 check refuses the leg, after the
  unit ran.
- Red by design until the coordinator's re-mint: `validate-ledger integrity` reports S0-03 (C) and S0-05 (R) INVALID,
  and three adjacent tests fail on that one call.

## NOT-done

- No re-mint. `proofs/*/result.json` and `proofs/ledger.json` are untouched. S0-03 and S0-05 read INVALID
  (`attestation-mismatch` on C and R) until the coordinator re-mints. `tests/test_validate_ledger.py` (2 tests) and
  `tests/test_proof_status.py` (1 test) fail on exactly that.
- No commit: the brief forbids git writes.
- Not run: `tests/test_lane_gate.py` (its disk floor; it names none of the seven files), the PC, real CI.
- A-1 to A-4 are reported, not fixed: each is outside the boundary.
- Two fail-closed branches of the new handback are unreachable here and untested: libc without `statx`, and a kernel
  whose statx sets no mount-id bit. Both hand nothing back and name the reason.
- The walk's stop arm (the way back up is not home) is reached only through a fault-injection mover in a test. At a
  real handback no unit or canary is left to move anything.

## Premise (evidence demand 1): re-measured, holds

- `git status --porcelain | wc -l` = 0 at start. The seven sha256 prefixes equal the premise's: 3dbf485fc95ca591,
  dc541933f0209d50, b6780a867b67aceb, cf0ba1cd5f359124, 16f8e425dace7457, a76ac2136095c8a0, 64c6043337ec9362.
- The grep lines match: C@c32ac3f:148, C@c32ac3f:800, C@c32ac3f:808, C@c32ac3f:789; R@c32ac3f:95, 99, 109, 118, 219,
  252, 525, 535, 538, 554; 0 `SIG_DFL` or `preexec_fn` in T; GW@c32ac3f:317's `SIG_DFL`.
- The `-q -rs` lines: W@c32ac3f:46 `pytest tests/ -q -rs` and NL@c32ac3f:873 `pytest tests/ -q -rs`.
- Floors, pasted from `scripts/test_summary.sh`:
  - T3 (1 files set=696563f67d3c): `pytest-summary: 209 passed in 37.12s`
  - T4 (1 files set=2e5825a9019e): `pytest-summary: 178 passed in 21.52s`
  - NL (1 files set=e3695f80792b): `pytest-summary: 121 passed in 13.20s`
  - T (1 files set=9f0502080347), 13:44:12Z-13:48:39Z: `pytest-summary: 297 passed in 266.39s (0:04:26)`
- The four signal tests with INT and HUP ignored reproduce the verifier's failures (see item 7).
- Mid-run the coordinator moved HEAD (message: 6aceec4). I measured d433571; `git diff c32ac3f HEAD` over the seven
  files is empty, and `tasks/briefs/i59/` is unchanged since eab2988. No mismatch that matters.

## Per item

### 1. E-1 (S0-03): no failure message prints a value read from the profile

What changed:
- C:91 `import hashlib`. C:237 `def _shape`: `absent` for None, else `<type>, <n> characters, sha256 <8 hex>`.
- C:149 the `transport` template now takes the shape: `transport: profile api_mode ({}) is not in the permitted set`.
- C:824 `_fail("transport", _shape(api_mode))`.
- C:835 `bundle: profile.yaml x-omniroute-compression (<shape>) is not 'off'` (`_shape(value)`).
- C:843 `bundle: profile.yaml key_env (<shape>) is not 'OMNIROUTE_API_KEY'` (`_shape(block.get('key_env'))`).
- New test T3:991 `test_a_failure_names_a_profile_value_by_its_shape_never_the_value`, 4 rows from
  T3:967 `PROFILE_VALUE_PATHS`: api_mode in the model section, api_mode in the provider block, the compression header,
  key_env. T3:943 `_fake_profile_value` builds a fake value at run time: letters alternate with marks (T3:934 `_MARKS`)
  that no checker message holds, so any 4-character run found is the value itself. Each row asserts: no case-folded run
  of 4 in stdout or stderr (T3:950 `_runs_of`), the exact stdout line, stderr empty. Preconditions: no `sk-`, `bearer `
  or `basic ` prefix; the screen finds a printed value; the value reaches the file whole.
- Two existing assertions changed with the contract (they pinned the printed value):
  - T3:451 `_shape_of('codex_app_server')` in `test_conjunct_v_transport`;
  - T3:556 `_shape_of('default')` in `test_conjunct_v_requires_the_compression_header_in_the_profile`.

Red on the PIN (C at 3dbf485f, run before the C edit): `6 failed, 7 passed, 200 deselected in 5.68s`. Each E-1 row
failed on `AssertionError: a run of the profile value was printed`.
Green: `13 passed, 200 deselected in 6.10s`; then the gates below.
Mutants: M-E1a (api_mode printed with `repr`) 2 FAILED; M-E1b (the header by `{value!r}`) 1; M-E1c (key_env by
`!r`) 1; M-E1d (`_shape` hashes `b""`) 6 (the 4 rows and the 2 changed tests).

Messages in C checked for the class (a value read from `hermes/profile.yaml`):
- C:824 `_shape(api_mode)`, C:835 `_shape(value)`, C:843 `_shape(block.get('key_env'))`: printed the value. Fixed.
- C:256 `absent`, C:258 `is not a regular file`: the file name only.
- C:296 `is not valid YAML`: the class name only (I59-E).
- C:769 and C:817 `_obj(profile, "profile.yaml")`, and the providers and provider-block `_obj` reads: no value.
- C:773 `declares {len(providers)} providers`: a count.
- C:828 `provider block has no extra_headers mapping`: no value.
- C:802 and C:806 `carries an inline credential under {child_path}`: mapping KEYS and list indices, never a value.
  Left unchanged (D5).
- Every other message reads `direct.json`, `omniroute-requests.json`, `hermes/leg.json`, the environ record or the
  timeline, not the profile. For example C:465 `sent as {value!r}` quotes the header the direct probe SENT. Out of the
  class; not changed.

### 2. B-1 (S0-05): a root holding a newline is refused, exit 73, nothing written

What changed:
- R:103 `case $EVIDENCE_ROOT in *$'\n'*)`: the root as given. The message names it with `printf %q`.
- R:107 `_real=$(readlink -m -- "$EVIDENCE_ROOT" && printf x)`: a sentinel read, so a trailing newline of the
  resolved path survives the substitution.
- R:110 `case $EVIDENCE_REAL in *$'\n'*)`: the resolved path.
- New test T:4363 `test_i59f_b1_an_evidence_root_that_holds_a_newline_is_refused_before_anything_is_written`, through
  the real runner, 4 rows: the verifier's reproduction (a clone named `nlrepo<newline>`, git itself reads it as a work
  tree); a link to that clone (needs the sentinel); a path through that link (needs the resolved check); a newline
  that `..` drops (no clone: needs the given-path check). Each asserts exit 73, the exact stderr line (quoted with
  bash's own `printf %q`, T:4355 `_quoted`), empty stdout, no entry changed under tmp_path.

Red on the PIN's R (mirror): the rows fail on `assert 1 == 73` (the run went on to its checker); the 4 rows:
`4 failed, 315 deselected in 3.73s`. Green: `4 passed, 315 deselected in 1.37s`.
Mutants: X-B1-given (no given-path case) kills the dotdot row; X-B1-sentinel (`$(readlink -m …)` again) kills the
link row; X-B1-resolved (the resolved case never matches) kills the link row (message) and the through-link row
(state).

### 3. B-2 (S0-05): no mount point on the same filesystem is descended

What changed: R:629 `def mount_id` reads statx `STATX_MNT_ID` on the entry's own descriptor. R:640 `def hand` leaves
an entry whose mount id differs from the root's: `(a mount point: another mount of this filesystem)`. The comment
above `_handback() {` now says so, and why: R:595 `STATX_MNT_ID`.
Mechanism measured first: a bind mount has the root's st_dev (65024) and another mount id (49 against 28).
New test T:4493 `test_i59f_the_handback_leaves_a_mount_under_the_root_as_it_is`, row `a-bind-mount-B2`: a real leg under
sudo; the test bind-mounts a directory outside the root into the unit's HOME while the unit serves, then sends
SIGTERM. Asserts: the mount's content unchanged during the run, the outside directory and its file unchanged (still
65534:65534), exactly one `left as it is` line naming the mount point, and the summary's `1 left as they are`.
Red on the PIN's R: `AssertionError: the handback changed what the mount holds` (the outside entries became
4242:4243). Green: in the gates. Mutant X-B2 (`if mount_id(fd) != mnt:` becomes `if False:`) 1 FAILED.

### 4. B-3 (S0-05): an iterative walk; any depth; every entry left is counted

What changed: the handback program (R:611 `_handback() {` to the heredoc's end). R:678 `def enter` opens a directory
to read and pushes a frame (its path, its st_dev and inode, the names still to walk). R:705 `while stack:` holds ONE
directory open to read. It goes down through the child's O_PATH descriptor and back up through `..`. The way up must
be the directory it came down from, or the walk stops: R:665 `f"{where} moved while it ran"` (round 4's `off_the_way`), and the
summary says `then it stopped: … so what it had not reached is left as it is`.
Tests:
- T:4580 `test_i59f_b3_the_handback_hands_back_a_1100_level_tree_and_counts_what_it_leaves`, rows
  `the-venue-limit` (20000 here) and `nofile-1024` (set on the runner by `resource.setrlimit`). A real leg under sudo;
  the unit makes `deep` plus 1,099 levels of `d` (T:4550 `DEEP_TREE`) with two names of one file at the bottom. After
  SIGTERM, the census (T:4565 `_owners`, a stack: Python 3.11's `os.walk` and `shutil.rmtree` raise RecursionError at
  this depth, measured) finds every entry the invoker's except the two names, both named on stderr, and the summary
  says `<census - 2> entries … ; 2 left as they are`.
- T:4464 `test_i59f_b3_the_walk_stops_where_a_directory_moved_under_it`: R's own program, cut from R's bytes
  (T:4414 `_handback_program`), with a mover (T:4452 `MOVE_BEFORE_THE_WAY_UP`) that renames `evidence/a/b` out of the
  root just before the first climb. Asserts the stop line; `a/c` and `z` are left; decoys at `outside/c` and a `z`
  beside the root are untouched.
Red on the PIN's R: the deep rows fail with entries left from path length 2014 (about level 1,000) and from path
length 1040 (about level 505). The PIN's program, cut from R and run directly: 1,100 levels at this venue's limit
gave `997 entries of … ; 1 left as they are` with `RecursionError` (104 entries not handed back); 700 levels under
`ulimit -n 1024` gave `511 entries of … ; 1 left as they are` with `OSError: [Errno 24] Too many open files`. The
stop test fails: the PIN never climbs `..`, so there is no stop line.
Mutants: X-B3-fd (the walk keeps each directory open) kills `nofile-1024`; X-B3-up (no identity check on the way up)
kills the stop test (the walk goes on from `outside/` and hands back the decoys); X-B3-count (the summary prints
`min(len(left), 1)`) kills both deep rows.

### 5. B-4 (S0-05): SUDO ids above 4294967294 refused; the handback checks its ids and types them

What changed: R:139 `if [ "$SUDO_UID" -gt 4294967294 ] || [ "$SUDO_GID" -gt 4294967294 ]` exits 64 before
anything is written (the pattern above it bounds the digits first). In the handback: R:615 `MAX_ID = 4294967294` and a
range check that hands nothing back; `fchownat` gets `argtypes` with `ctypes.c_uint`.
Tests:
- T:4399 `test_i59f_b4_under_sudo_an_id_above_4294967294_is_refused_before_anything_is_written`: 4294967295,
  4294967296 and 4294967297, each as SUDO_UID and as SUDO_GID (6 rows), through the real runner: exit 64, the exact
  line, nothing written.
- T:4431 `test_i59f_b4_the_handback_itself_refuses_an_id_libc_would_cut`: the same three values in each position
  (6 rows) against R's own handback program (the runner refuses first, so only the cut program reaches the check).
  Asserts the refusal line and no change; then the same program with ids in range hands the tree back.
Red on the PIN's R: the runner rows fail on `assert 1 == 64`; the handback rows show the PIN handing back to the cut
id (`… now belong to 4294967295:4243`).
Mutants: X-B4-runner (the R check off) 6 FAILED; X-B4-handback (the range check off) 6 FAILED.
Measured equivalent (SURVIVED, stated): X-B4-argtypes (no `c_uint` argtypes) passes the 11 handback tests. With the
range check in place, ctypes' default int conversion masks to the same 32 bits on this ABI.

### 6. B-6 (S0-05): the other-filesystem branch is covered

Test: T:4493 `test_i59f_the_handback_leaves_a_mount_under_the_root_as_it_is`, row `a-tmpfs-B6`. A tmpfs under the root,
mounted while the unit serves: left as it is, named `(another filesystem)`, its file unchanged, counted in the summary.
It passes on the PIN's R: the branch existed and was only untested (D6). Mutant X6 (`if st.st_dev != dev:` becomes
`if False:`) FAILED: the tmpfs then falls to the mount-id check and is named `(a mount point: another mount of this
filesystem)`.

### 7. Task #331, AF-AP-234 (S0-05 tests): the signal tests start the runner at the default dispositions

What changed: T:1766 `SIGNALS_DEFAULT`, the GW@c32ac3f:316 `INT_DEFAULT` shim extended to SIGINT, SIGHUP and SIGQUIT, and it
also puts back SIGPIPE and SIGXFSZ (D3). Used by:
- T:2076 (x4), T:3105 and T:3143 (e3b_r4), T:4595 (the deep test): `SIGNALS_DEFAULT + ["bash", str(RUNNER)`;
- T:3190 `def _runner_session` (the e3r1 and i59b signal tests).
New test T:4330 `test_i59f_signal_tests_start_the_runner_with_int_hup_and_quit_at_their_defaults`: both launches first
ignore INT, HUP and QUIT, as a detached gate does. Bare: `trap -- '' SIGINT` and the three ignore bits set. Through the
shim: all three traps set, and none of the five signals ignored.
Measured, the verifier's launch form `nohup bash -c '… & wait'` (its background job's `SigIgn: 0000000000000007`):
- BEFORE (the PIN's T, 13:41:02Z-13:43:58Z): `pytest-summary: 4 failed in 175.76s (0:02:55)`. The same lines as the
  verifier's, with the same reasons (`assert 1 == 130`, a timeout waiting for cleanup's SIGTERM, `assert 1 == -1`):
  - T@c32ac3f:3084 `assert runner.returncode == 130`;
  - T@c32ac3f:1880 `timed out waiting for`;
  - T@c32ac3f:4236 `assert runner.returncode == rc` (the INT and HUP rows).
- AFTER (14:17:21Z-14:17:33Z): `pytest-summary: 4 passed in 11.53s`.
- The whole of T under the same form (14:35:47Z-14:40:32Z): `pytest-summary: 319 passed in 284.81s (0:04:44)`.
Mutants: X-S1 (the shim resets SIGINT only) and X-S2 (no PIPE and XFSZ restore) each FAILED the shim test.

### 8. C-1 and C-2 (S0-04 tests)

What changed (tests only; `capture_leg.py` is right and untouched):
- C-1: T4:1400 `test_capture_leg_reports_a_profile_read_error_on_its_own_line`, rows `missing`, `a-fifo`,
  `not-utf-8` (the oracle is this venue's own decoder).
- C-1: T4:1421 `test_capture_leg_reports_an_unreadable_profile_on_its_own_line` (mode 0000, read as uid 65534 when the suite is
  root, as itself otherwise, in a 0711 directory of its own under /tmp). Each pins the whole stderr line and asserts
  stdout empty and no output written.
- C-2: T4:1357 and T4:1387 `assert proc.stdout == ""` in the two I59-C YAML-error tests (22 items).
Red: the PIN's tool is right, so these pass on it (D6). C-X4 (the read moved inside the parse `try`) 4 FAILED;
C-X6 (the last 7 characters of the message printed to stdout) 22 FAILED.

### 9. E-2 (S0-03 tests)

What changed: T3:910 `assert result.stderr == ""` in the I59-E parse-error test (7 rows).
The new E-1 rows assert the same: T3:1009 `assert result.stderr == ""`. Scope: D4.
Red: passes on the PIN (D6). E-X7 (the last 7 characters of the parse message written to stderr) 7 FAILED.

### 10. F2 (CI): `-rfEs`

What changed: W:46 `python -m pytest tests/ -q -rfEs` with its comment; NL:873 the pin, the same string exactly.
Red: on the PIN's workflow, NL's two YH tests fail with `ValueError: '…-rfEs…' is not in list` (FAILED, not ERROR).
Green: `2 passed, 119 deselected in 0.55s`.
Shown on a three-test file with pytest 9.1.1 (CI's version): `-q -rs` lists only `SKIPPED`; `-q -rfEs` lists
`FAILED`, `ERROR` and `SKIPPED`.

## Gates (evidence demand 4), pasted from `scripts/test_summary.sh`

- T3, `1 files set=696563f67d3c`: `pytest-summary: 213 passed in 43.14s` and `pytest-summary: 213 passed in 42.92s`
  (209 + 4).
- T4, `1 files set=2e5825a9019e`: `pytest-summary: 182 passed in 20.01s` and `pytest-summary: 182 passed in 23.05s`
  (178 + 4).
- NL, `1 files set=e3695f80792b`: `pytest-summary: 121 passed in 15.23s` and `pytest-summary: 121 passed in 15.93s`.
- T, `1 files set=9f0502080347`, foreground: 14:20:36Z-14:25:33Z `pytest-summary: 319 passed in 295.93s (0:04:55)`,
  and 14:25:38Z-14:30:23Z `pytest-summary: 319 passed in 284.52s (0:04:44)` (297 + 22).
- Adjacent (every test file that names a changed path, the gate rule), once:
  - `10 files set=24177fcfb3a3` (`test_edit_snapshot_ap_screen`, `test_ci_gate`, `test_stage0_ci_workflow`,
    `test_decisions_no_model`, `test_attested_inputs`, `test_validate_ledger`, `test_ledger_gen`, `test_proof_runner`,
    `test_s0_08_containment`, `test_s0_01_pc_tools`): `pytest-summary: 2 failed, 719 passed in 206.74s (0:03:26)`.
    The 2 are `test_validate_ledger.py`'s `test_registry_rows_carry_no_key_the_validator_does_not_read` and
    `test_committed_pc_bridge_spike_validates_and_declares_all_effects`, both on `validate-ledger integrity`.
  - `1 files set=cce0ecd44cb2` (`test_proof_status.py`, `--basetemp=/tmp/i59f-ps/bt`):
    `pytest-summary: 1 failed, 32 passed in 8.82s`, the same integrity call.
  - `python3 scripts/validate-ledger integrity --root .` (read only): 10 PRESENT, and exactly
    `attestation-mismatch: S0-03 proofs/S0-03/check_omniroute_roundtrip.py` and
    `attestation-mismatch: S0-05 proofs/S0-05/tools/pc/run_s0_05_units.sh`. The coordinator's re-mint clears these.

## Mutation table (evidence demand 3)

The driver (scratch, deleted) copies the worktree file into a mirror, applies one anchored replacement (the anchor
occurs once), checks it (`py_compile`, `bash -n`, and a compile of the cut handback program), collects the target
items (their count must equal the row's literal), then runs them. A KILL is FAILED lines and no ERROR.
`EXPECTED=19 KILLED=19 SURVIVED=0 INVALID=0` (14:14:09Z-14:15:36Z).

| row | mutant | FAILED |
|---|---|---|
| M-E1a | api_mode printed with `repr` | 2 |
| M-E1b | compression header printed `!r` | 1 |
| M-E1c | key_env printed `!r` | 1 |
| M-E1d | `_shape` hashes `b""` | 6 |
| E-X7 | verifier's: 7 characters of the parse message to stderr | 7 |
| C-X4 | verifier's: `read_regular` inside the parse `try` | 4 |
| C-X6 | verifier's: 7 characters of the message to stdout | 22 |
| X6 | verifier's: `if st.st_dev != dev:` becomes `if False:` | 1 |
| X-B2 | `if mount_id(fd) != mnt:` becomes `if False:` | 1 |
| X-B1-given | no given-path newline case | 1 |
| X-B1-sentinel | plain `$(readlink -m …)` | 1 |
| X-B1-resolved | the resolved-path case never matches | 2 |
| X-B4-runner | R's range check off | 6 |
| X-B4-handback | the handback's range check off | 6 |
| X-B3-fd | the walk keeps each directory open | 1 |
| X-B3-up | no identity check on the way up | 1 |
| X-B3-count | the summary counts `min(len(left), 1)` | 2 |
| X-S1 | the shim resets SIGINT only | 1 |
| X-S2 | the shim keeps SIGPIPE and SIGXFSZ ignored | 1 |

Measured equivalents, stated, not in the 19: X-B4-argtypes (`11 passed`) and X-B3-up-ino (the way up compares the
inode only: `3 passed`; a rename cannot change st_dev).

## Static checks and host state (evidence demands 5 and 6)

- `bash -n` R: rc 0. pyflakes over C, T3, T, T4 and NL: rc 0.
- `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`: 0 for each of the seven files and for this report.
- `scripts/report_lint.py` over this report (aliases above, the working tree): `report_lint: 95 refs — OK 90, NEAR 0, MISS 0, UNCHECKABLE 5, UNRESOLVED 0 (worktree)`. The 5 are the premise's list of PIN grep lines.
- `scripts/ap_screen.py`, whole files, mine against HEAD's bytes: R 16 = 16, T 37 = 37, T4 4 = 4, NL 0 = 0. C 0 to 1
  and T3 6 to 7: one new AP-32 tell each, on the display hash in C:237 `def _shape` and T3:937 `def _shape_of`. They
  hash the same UTF-8 bytes for every tested value, and nothing stored is compared to them: false positives.
- Host, after every S0-05 gate and at the end: `ip netns list` 0 lines; iptables stable form
  (`iptables-save | grep -v '^#' | sed -E 's/\[[0-9]+:[0-9]+\]$/[n:n]/' | sha256sum`) `0528d077bca3781a` before
  (13:40:41Z) and after; the mount-point list hash `2dd93d06015feb4d` before and after; no mount left.

- The bytes every gate above ran on (sha256, first 16): 562465f01d356ada C, bffa82c76b574bcf T3,
  2580c2a93a3c99cc R, b1c404f6249c6667 T, d61829558b67ecd0 T4, 594fc5b0d0564392 W, df54c0b7b883d2d1 NL.
  `git status --porcelain` at the end: the seven files ` M` and this report `??`, nothing else.

## Adjacent defects (reported, not fixed)

- **A-1 (containment, VERIFIED through the real runner).** R@c32ac3f:219 `"$UNIT_USER" =~` admits ten digits.
  R@c32ac3f:642 `[ "$UNIT_UID" = 0 ]` compares the uid as a string. R@c32ac3f:737 hands it to setpriv, which cuts `--reuid=4294967296` to
  0. Measured: `setpriv --reuid=4294967296 … id -u` prints 0, and so does `--reuid=4294967295` (no change: root
  stays). Through the runner with `unit_user="4294967296:4294967296"`: the stand-in recorded uid 0, gid 0; the A4 line
  never printed; the post-launch A7 check refused the leg (`unit identity not observed: uid 0`) after the unit ran as
  root. Fix shape: B-4's bound, and a numeric root check.
- **A-2 (VERIFIED).** CC@c32ac3f:344 `key-env-not-a-name`, CC@c32ac3f:338 `config-header-value` and CC@c32ac3f:341 `base-url-unexpected`
  print a config value through CC@c32ac3f:120 `def _short`, a 60-character cut. A copy of the pass bundle with
  `key_env: Zq~FAKEnot-a-key~X9^v` printed `failure_reason: config: key-env-not-a-name: Zq~FAKEnot-a-key~X9^v`. The
  E-1 class in S0-04.
- **A-3 (VERIFIED).** GW@c32ac3f:316 `INT_DEFAULT` hands the script under test SIGPIPE and SIGXFSZ ignored: CPython ignores
  both at startup, and `os.execvp` keeps an ignore. Measured `SigIgn: 0000000001001000` through that form.
- **A-4 (INFERRED, static only).** R:315 `real=$(readlink -m -- "${file:-/nonexistent}")` (the pair identity file)
  drops a trailing newline before the `.secrets` path refusal: B-1's mechanism at another seam. Not reproduced.
- **A-5 (known, VERIFY-I59-LANDING F2).** `scripts/test_summary.sh` runs `-rs`, so a gate log names no FAILED line.
  It hit here: the adjacent run's two failures showed only as `F` marks.

## Self-attack: the three likeliest ways this change is wrong

1. **The new walk under a hostile move.** A directory moved out of the root WHILE the walk reads it still has the
   entries it holds handed back where they now are. No descriptor walk can see that move, and the PIN's recursive
   walk had the same window. What I ruled out: the walk never climbs anywhere but home. X-B3-up shows that without the
   check it hands back the decoys outside; with the check it stops and says so. No unit or canary is alive at a real
   handback, so only a third process could move anything.
2. **statx on another venue.** The mount-id check needs statx `STATX_MNT_ID` (Linux 5.8, glibc 2.28). Without it the
   handback now hands nothing back and names why; before, it ran without the bind-mount check. This kernel (6.18)
   fills the mount id (measured). The PC (Fedora 42) is INFERRED to support it; the fail-closed branch is untested.
3. **The shape leaks less, not nothing.** It prints 32 bits of sha256. For a guessable value (an api_mode, a header
   word) that confirms a guess. For a key it reveals nothing useful. The credential walk's path message still prints
   mapping keys (D5). The 4-character screen proves the value itself never prints, whatever its prefix.

## DISCREPANCIES and deviations

- D1. HEAD is d433571, not the coordinator's 6aceec4: one more docs-only commit (`wiki/topics/live-state.md`). The
  seven files equal the PIN's bytes; the brief is unchanged.
- D2. The brief says "like S0-04's `_short()`". CC@c32ac3f:120 `def _short` prints the value, cut at 60 characters; it is no
  length-and-hash shape. I built the shape the brief names (type, length, sha256 prefix). A-2 is `_short`'s leak.
- D3. **Deviation: SIGNALS_DEFAULT restores five signals, not three.** The GW form hands CPython's startup ignores of
  SIGPIPE and SIGXFSZ to the runner; a runner with SIGPIPE ignored is not the runner a shell starts. Measured
  `0x1001000` through the GW form and `0x0` through mine. Needs your acceptance.
- D4. E-2's scope: `stderr == ""` went where E-X7 lands (the I59-E parse-error test, 7 rows) and into the new E-1 rows.
  The other failure tests of T3 whose failure goes to stdout (about 60) were not swept.
- D5. **Interpretation:** C:802 and C:806 `carries an inline credential under {child_path}` print mapping KEYS
  (the provider name and key names), never a value. I left
  them: the brief ("Today three do") and the verifier's E-1 count three. A secret pasted as a KEY would print; changing
  it would rewrite 9 path-pinning tests and drop the operator's locator. Your call.
- D6. Items 6, 8 and 9 are test-strength items: the PIN's production bytes behave, so their new tests pass on the PIN.
  Their red is the named mutant on the PIN's bytes (X6, C-X4, C-X6, E-X7). Evidence demand 2 cannot hold literally
  for them. The same holds for item 7's shim test (a T-only helper); item 7's red is the measured BEFORE run.
- D7. **Deviation: scratch outside the scratchpad, twice, temporary.** `/tmp/claude-0` is 0700, so a uid-65534 child
  cannot read a mirror there. The S0-04 mutation rows ran in `/tmp/i59f-s004-*` (about 3 MB), and
  `test_proof_status.py` used `/tmp/i59f-ps/bt` (the env-tool-quirks rule for gpg's socket path). Both deleted. The new
  tests make and remove their own /tmp directories at run time, as `e3dir` does.
- D8. Two `/tmp/e3-*` directories (13:10Z and 13:11Z) predate this lane (it began 13:22Z). Not mine; left.
- D9. "One directory descriptor open at a time": the walk holds one directory open to read. At a descent it briefly
  also holds the entry's O_PATH descriptor and the next directory's (at most 4 descriptors, never one per level).
- D10. My B-1 and B-4 lines moved two premise lines; their defects are A-1 and A-4:
  - R@c32ac3f:219 is now R:274, `"$UNIT_USER" =~`;
  - R@c32ac3f:252 is now R:315, `readlink -m -- "${file:-/nonexistent}"`.

## Evidence tiers

- VERIFIED (run here, pasted above): the premise; every red and green pair; the 19 mutants and the 2 equivalents; the
  gates; the signal BEFORE and AFTER; the host state; A-1, A-2, A-3.
- INFERRED: A-4; statx mount-id support on the PC; the PC root's RLIMIT_NOFILE of 1024 (the verifier's inference; the
  test sets 1024 itself).
- ASSUMED: none.

## Round 2 (the fold of A-1..A-4)

Written 2026-09-28 15:3xZ by the same lane, on the coordinator's round-2 message. Worktree HEAD 34d3af0 (D-R2-1).
New aliases for this section: CC = `proofs/S0-04/check_compression.py`, GW = `tests/test_gpu_window.py` (as above);
R, T and T4 are this round's bytes.

Report upkeep (15:4xZ): round 2 moved lines in R, T, T4, CC and GW, so I re-pointed the round-1 sections' line
refs to these bytes. A ref to code that round 2 changed now carries the PIN (alias@c32ac3f:NN, checked at that
revision). No round-1 claim changed otherwise. The `report_lint` result is under Static checks.

### TL;DR

- A-1, A-2, A-3 and A-4 are folded in. Both preconditions were checked first: the code does not deliberately allow
  gid 0, and A-4 proves as a lost newline (a false refusal under a wrong path), not as a bypass.
- New tests: T 15 new and 1 row dropped (net 14), T4 4, GW 1. Three existing pins changed with the contract.
- Red on the current bytes: `21 failed, 2 passed, 528 deselected in 47.60s`. Green: `23 passed, 528 deselected in 7.84s`.
- Mutation table: `EXPECTED=15 KILLED=15 SURVIVED=0 INVALID=0`, plus two measured equivalents.
- Gates, twice each: T `333 passed`, T4 `186 passed`, GW `32 passed`, `test_edit_snapshot_ap_screen.py` `197 passed`,
  `test_gpu_side_by_side.py` `74 passed`.
- Expected reds until the re-mint: `validate-ledger integrity` now names S0-03 (C), S0-04 (CC) and S0-05 (R).

### NOT-done

- No re-mint; `proofs/*/result.json` and `proofs/ledger.json` untouched. No commit. A-5 untouched (the coordinator's).
- A gid of 0 through the RESOLVED default (a pinned agent owned by `<uid>:0`) is still accepted: the new rule covers the
  explicit `S0_05_UNIT_USER`, as the item says. F11's other half (A7 records the `Gid:` line) is not done.
- The S0-04 api_mode observation now prints a shape, not the mode's name (D-R2-2).
- Not run: the PC, real CI, `tests/test_lane_gate.py`.

### A-1 (S0-05 containment): an explicit unit user outside [1, 4294967294] is refused, exit 64

Precondition (gid 0): not deliberate, so no stop.
- The gid part of the old pattern `(0|[1-9][0-9]{0,9})` carries no comment, test or ruling.
- VERIFY-E3's F11 recorded "A unit gid of 0 is accepted … Fix: refuse gid 0 too and record the `Gid:` line" as a
  FOLLOW-UP. The ledger's VERIFY-E3 line closes F2 and F3 and never rules on F11. A4's text is uid-only.
- VERIFY-E3 concluded "no uid bypass" from 4294967295 only (`--init-groups` needs a passwd entry). 4294967296 cuts
  to uid 0, which has one: that is how round 1's run executed as root.

What changed:
- R:258 comment and R:267 `if [ -n "$UNIT_USER" ] && { ! [[ "$UNIT_USER" =~` (each class a range in round 2,
  `[1-9][0-9]{0,9}`; an explicit list since round 4)
  with both ids `-gt 4294967294` refused: exit 64 before anything is written and before any unit launches.
- The resolved default keeps the old shape check and A4's not-run row; T:2274's `default-owner` row still passes.
- R:812 `"$UNIT_UID" -eq 0` (numeric) and R:527 `uid[0] != int(want_uid)` (the post-launch compare, numeric).
- T:2274 `["default-owner"]` drops the `explicit` row: its not-run assertion no longer applies. The new `0:0` row covers it; the
  docstring says so.

Tests:
- T:4640 `test_i59f_a1_an_explicit_unit_user_outside_1_to_4294967294_is_refused_before_any_unit_runs`, the 10 rows
  of T:4627 `BAD_UNIT_USERS`, through the real runner with a listener, so a leg past the check would reach its
  launch. Each asserts exit 64, T:4633 `UNIT_USER_REFUSED` as stderr's last line, no stdout, no evidence root, no
  stand-in record, no namespace.
- T:4662 `test_i59f_a1_a_unit_user_in_range_proceeds`: 65534:65534 passes, and the unit's own record says
  65534:65534. It is then stopped with SIGTERM (143).

Red on the current bytes: three rows ran on (`assert 1 == 64`). At 4294967296:4294967296 the stand-in recorded
`'uid': 0`. Coreutils refused the scratch-tree chown (`chown: invalid user`), but the writability probe ran as root
and passed; A7 refused only after the launch (`unit identity not observed: uid 0`). The other seven rows already
exited 64 and failed only on the new message.
Mutants: X-A1-range (2 FAILED), X-A1-zero (1), X-A1-lead (3), X-A1-all (the positive control, 1).
Measured equivalents: R:812 `-eq 0` back to `= 0` (`12 passed`) and the A7 compare back to strings (`19 passed`). The check
above them admits only canonical decimals now.

### A-2 (S0-04): no CC message prints a value of the provider block

What changed:
- CC:49 `import hashlib`. CC:135 `def _shape`, in the format of C's (`absent`, or `<type>, <n> characters, sha256 <8 hex>`).
- CC:363 `config-header-value: {_shape(hits[0][1])}`, CC:366 `base-url-unexpected: {_shape(base_url)}`,
  CC:369 `key-env-not-a-name: {_shape(key_env)}`, and the observation printed `api_mode = {_shape(api_mode)}`
  (round 2; round 3's route B changed that line again, see "Item 1, route B").

Every CC message that reads the provider block (`hermes-provider.json`, CC:347 `_read_json`), with its disposition:

| line | message | disposition |
|---|---|---|
| CC:347 | absent, not regular, too large, not JSON, NaN (`_read_json`) | no value; unchanged |
| CC:353 | `unexpected-provider-fields` | field names (keys); unchanged |
| CC:356, CC:359 | `config-header-absent` | no value; unchanged |
| CC:361 | `config-header-duplicated` | a count; unchanged |
| CC:363, CC:366, CC:369 | header value, base_url, key_env | printed the value; now `_shape` |
| CC:372 | `api-mode-absent` | no value; unchanged |
| CC:378 | the api_mode observation | printed the value; round 2: `_shape`; route B: a known mode by its name, any other value by `_shape` |

CC:281-342's `_short` uses read the request legs' records, not the profile or config: outside the class.

Tests:
- T4:785 `test_a_message_names_a_config_value_by_its_shape_never_the_value`: the 4 rows of
  T4:767 `CONFIG_VALUE_PATHS`. They mirror T3:991 `test_a_failure_names_a_profile_value_by_its_shape_never_the_value`.
  The fake value is built at run time (T4:750 `_fake_config_value`). Each row asserts no case-folded 4-character run
  in stdout or stderr, the exact line, and empty stderr. A failure row pins stdout whole; the observation row passes
  and pins its line.
- Pins changed with the contract: the observation pin in T4:95 `test_observations_are_recorded_not_asserted` (round 2:
  `_shape_of('chat_completions')`; route B: the name again) and T4:724 `_shape_of('on')`.

Red on the PIN's CC: the 4 rows `AssertionError: a run of the config value was printed`, and the 2 pins.
Mutants: X-A2-header (2), X-A2-url (1), X-A2-key (1), X-A2-obs (2), X-A2-hash (6).

### A-3 (test harness): GW's shim puts back SIGPIPE and SIGXFSZ

What changed: GW:318 `INT_DEFAULT` now runs GW:320 `for name in ('SIGINT', 'SIGPIPE', 'SIGXFSZ'):`, and its
comment says why.
Test: GW:330 `test_scripts_under_test_start_with_int_pipe_and_xfsz_at_their_defaults`. Both launches first ignore
SIGINT. The bare launch shows `{SIGINT}` ignored (the probe can see an ignore); through the shim, none of the three.
Red: `AssertionError: SigIgn:	0000000001001000` (SIGPIPE and SIGXFSZ). Green: in the gates.
Mutants: X-A3-pipe, X-A3-xfsz and X-A3-int (1 each).

### A-4 (S0-05): the pair identity path, proven first, then B-1's treatment

Proof, on the current bytes, through the real runner:
- The identity file was a valid one: mode 0600, owned by the unit user, with a key line. It was named `.secrets` plus
  a newline and sat beside S0-01's `.secrets`, not under it.
- The runner refused it as `SKIP buzz-acp: identity file refused: S0-01 path <e3dir>/s0-01-pinned/.secrets`, a path
  the file does not have. The same happened through a link to it.
- It proves the loss at R:315 `real=$(readlink -m -- "${file:-/nonexistent}")`.
- It cannot be a bypass: a stripped trailing newline keeps a path under `.secrets/` inside the prefix
  `"${PIN[BASE]}/.secrets/"*`. The defect is fail-closed: a false refusal under a wrong name.

What changed:
- R:165-183, the comment and the early refusal: exit 73 with `printf '%q'`, before anything is written:
  - R:171 `case $PAIR_IDENTITY in *$'\n'*)` (the given path);
  - R:175 `if _id_real=$(readlink -m -- "$PAIR_IDENTITY" && printf x)` (the sentinel read);
  - R:177 `case $_id_real in *$'\n'*)` (the resolved path).
- A path readlink cannot resolve is left to `_pair_identity`, as before.
- R:310-311: the comment above R:312 `_pair_identity() {` says `No newline` reaches the path now.

Test: T:4694 `test_i59f_a4_a_pair_identity_path_that_holds_a_newline_is_refused_before_anything_is_written`, 4 rows:
the file itself, a link to it, a path through a link to a directory named with a newline, and a newline that `..`
drops. Each asserts exit 73, the exact line as stderr's last, no stdout, no evidence root, and no key printed.
Red: 4 × `assert 1 == 73`.
Mutants: X-A4-given (2: the dotdot row by state, the file row by message), X-A4-sentinel (1), X-A4-resolved (2).

### Gates, pasted from `scripts/test_summary.sh`, twice each

The gate list is every file that names a changed file (`grep -l` over `tests/*.py` and `harness-ports/tests/*`):
- R: named by `test_edit_snapshot_ap_screen.py` and T.
- T: named by `test_edit_snapshot_ap_screen.py`.
- CC: named by `test_edit_snapshot_ap_screen.py` and T4.
- T4: named by none.
- GW: named by `test_gpu_side_by_side.py` and T.

| file | set | run 1 | run 2 |
|---|---|---|---|
| T | `1 files set=9f0502080347` | `333 passed in 300.99s (0:05:00)` | `333 passed in 306.96s (0:05:06)` |
| T4 | `1 files set=2e5825a9019e` | `186 passed in 21.98s` | `186 passed in 22.02s` |
| GW | `1 files set=65a832bc5b21` | `32 passed in 81.37s (0:01:21)` | `32 passed in 80.90s (0:01:20)` |
| `test_edit_snapshot_ap_screen.py` | `1 files set=3d4383148bd3` | `197 passed in 0.34s` | `197 passed in 0.24s` |
| `test_gpu_side_by_side.py` | `1 files set=9b506ab184e5` | `74 passed in 40.54s` | `74 passed in 40.14s` |

- Counts: T is 319 + 14. T4 is 182 + 4. GW is 31 + 1 (a collect-only of HEAD's GW gives `31 tests collected`).
- Expected reds, each twice:
  - `test_validate_ledger.py` (`1 files set=852bbd75ee1d`): `2 failed, 33 passed in 11.83s` and `2 failed, 33 passed in 12.43s`.
    The two are `test_committed_pc_bridge_spike_validates_and_declares_all_effects` and
    `test_registry_rows_carry_no_key_the_validator_does_not_read`.
  - `test_proof_status.py` (`1 files set=cce0ecd44cb2`, short `--basetemp`): `1 failed, 32 passed in 8.13s` and
    `1 failed, 32 passed in 7.59s`. The one is `test_committed_state_passes_status_and_ledger`.
  - All three fail on one cause, `validate-ledger integrity`. It now reports S0-03, S0-04 and S0-05 INVALID, with
    exactly `attestation-mismatch: S0-03 proofs/S0-03/check_omniroute_roundtrip.py`,
    `attestation-mismatch: S0-04 proofs/S0-04/check_compression.py` and
    `attestation-mismatch: S0-05 proofs/S0-05/tools/pc/run_s0_05_units.sh`. The coordinator's re-mint clears them.

### Mutation table (scratch mirror, deleted after its log was read)

`EXPECTED=15 KILLED=15 SURVIVED=0 INVALID=0` (15:13:18Z-15:15:40Z). Every kill is FAILED lines with no ERROR, after
`bash -n`, a compile of every R heredoc, and a collect count equal to the row's literal.

| row | mutant | FAILED |
|---|---|---|
| X-A1-range | no `-gt 4294967294` checks | 2 |
| X-A1-zero | the pattern admits 0 | 1 |
| X-A1-lead | the pattern admits leading zeros | 3 |
| X-A1-all | the check refuses every value (the positive control) | 1 |
| X-A4-given | the given-path case never matches | 2 |
| X-A4-sentinel | a plain `$(readlink -m …)` | 1 |
| X-A4-resolved | the resolved-path case never matches | 2 |
| X-A2-header | `config-header-value` back to `_short` | 2 |
| X-A2-url | `base-url-unexpected` back to `_short` | 1 |
| X-A2-key | `key-env-not-a-name` back to `_short` | 1 |
| X-A2-obs | the observation back to `_short` | 2 |
| X-A2-hash | `_shape` hashes `b""` | 6 |
| X-A3-pipe | the shim leaves SIGPIPE ignored | 1 |
| X-A3-xfsz | the shim leaves SIGXFSZ ignored | 1 |
| X-A3-int | the shim leaves SIGINT ignored | 1 |

The first run of the table had X-A1-range INVALID: my anchor left a `\;`, and `bash -n` refused the mutant. I fixed
the anchor and reran the whole table.

### Static checks and host state

- `bash -n` R: rc 0. The five R heredocs compile. pyflakes over the seven Python files I have changed: rc 0.
- `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`: 0 for R, T, CC, T4, GW and this report.
- `scripts/ap_screen.py` against HEAD, whole files:
  - R 16 = 16 and T 37 = 37.
  - GW 9 = 9. One AF-AP-58 tell moved from the old one-line shim to GW's probe line `signal.signal(signal.SIGINT,
    signal.SIG_IGN)`. It is a false positive: it installs an ignore in a `preexec_fn`, not a raising handler.
  - CC 0 to 1 and T4 4 to 5: an AP-32 tell on each display hash (`def _shape`, `def _shape_of`), false positives as in
    round 1.
- `scripts/report_lint.py` over the whole report (aliases C, T3, R, T, T4, W, NL, GW, CC; the working tree),
  after the upkeep at the section head: `report_lint: 148 refs — OK 143, NEAR 0, MISS 0, UNCHECKABLE 5, UNRESOLVED 0 (worktree)`.
  The 5 are round 1's premise list of PIN grep lines. Before the upkeep:
  `report_lint: 143 refs — OK 85, NEAR 19, MISS 30, UNCHECKABLE 9, UNRESOLVED 0 (worktree)`.
- Host, after each S0-05 gate and at the end: `ip netns list` 0 lines, iptables stable form `0528d077bca3781a`,
  mount-point hash `2dd93d06015feb4d`, no `/tmp/i59f-*`.
- Disk fell to 1,503 MB during the runs. The growth was the harness logs under `/tmp/claude-0` and another lane's
  live pytest run (`pytest-422`); my scratch stayed under 100 KB. No gate stopped.

### Final sha256 prefixes (the bytes every round-2 gate ran on)

562465f01d356ada C, bffa82c76b574bcf T3, a6f721345bce4c32 R, d1c98c2f7ee55454 T, 256328623c90966f T4,
594fc5b0d0564392 W, df54c0b7b883d2d1 NL, 2627b89306128491 CC, d0f1d1e6bbdc6411 GW. `git status --porcelain`: these
nine ` M`, the report `??`, nothing else.

### Self-attack (round 2): the three likeliest ways this round is wrong

1. **A-1 refuses the owner's real run at the re-mint, or still admits a value that reaches root.** Ruled out:
   - the committed evidence ran both units as uid 1000 (`unit-identity.json` of hermes-acp and of buzz-acp:
     `'uid': [1000, 1000, 1000, 1000]`), and the S0-01 census records gid 1000 for the pinned files;
   - the `S0_05_UNIT_USER` check (round 2's bytes, now R:267-272), cut from R with sed and run in bash on 14 values during the upkeep:
     `1000:1000` and `4294967294:4294967294` admitted, and `1:1`; exit 64 for a trailing or a leading newline,
     4294967295 in either place, a space at either end, 0 in either place, `+1:1`, `1:1:1` and an 11-digit id.
   Left open: A7 records no `Gid:` line, so the real run's gid is inferred; the PC run is not run here.
2. **A-2's leak test is blind, or a CC message that reads the provider block was missed.** Ruled out: each mutant
   that puts `_short` back (X-A2-header, X-A2-url, X-A2-key, X-A2-obs) reds its own row, and X-A2-hash reds 6.
   The table above lists every message in CC:347-378 (route B's bytes), where `_shape` prints each value but a
   known mode in the observation. Left open: the table
   comes from a read of CC, not from a tool.
3. **A-4's refusal fires on a path with no newline, or the sentinel read changes what `_pair_identity` reads.**
   Ruled out: T `333 passed` twice, with T:2303 `test_a6_identity_file_refusals` and the other earlier identity
   tests in it; `_id_real` is read only inside the early block, and
   R:315 `real=$(readlink -m -- "${file:-/nonexistent}")` is unchanged; each X-A4 mutant reds.

### Discrepancies (round 2)

- D-R2-1. HEAD is 34d3af0: the old d433571 reads a3b2228 after a push, plus two doc commits. `git diff c32ac3f HEAD`
  over the ten boundary files is empty.
- D-R2-2. **The S0-04 observation now prints the api_mode's shape**, following "every CC message". T4's observation
  pin changed with it. The checker's output no longer names the mode behind the owner's open decision (task #35).
  If the name matters, an allow-list of the known mode names is the alternative. I did not build it: it would
  deviate from the item.
- D-R2-3. A-1's rule covers the explicit `S0_05_UNIT_USER` only, as written. A default resolved from a pinned agent
  owned by `<uid>:0` still gives gid 0 (F11's residual).
- D-R2-4. A-4's refusal is global, as B-1's is: a newline in `S0_05_PAIR_IDENTITY` refuses the whole run (exit 73)
  even when `buzz-acp` is not in the unit list.
- D-R2-5. "The post-launch root check compares numerically": I made both numeric, R:527 `int(want_uid)` (A7,
  post-launch) and R:812 `-eq 0` (A4, pre-launch). Both are measured equivalents now.
- D-R2-6. Not asked, left as it is: R:320 compares the identity file's owner with `"$UNIT_UID"` as strings. Both
  sides are canonical decimals, so it is equivalent too.

### Evidence tiers (round 2)

- VERIFIED (run here, pasted above): the red and green pairs; the 15 mutants and the 2 equivalents; the gates, twice
  each; the expected reds and their one cause; the static checks; the host state; the A-4 proof through the runner;
  the A-1 boundary run on R's real lines; the committed units' uid 1000; `report_lint`.
- INFERRED: A-4 cannot be a bypass (from the `.secrets/` prefix check, not a run); D-R2-6's equivalence (both sides
  canonical decimals, no mutant); the real run's gid 1000 (from the S0-01 census, not a unit record); "gid 0 is not
  deliberate" (no ruling found in the ledger or in VERIFY-E3: an absence, not a statement).
- ASSUMED: nothing beyond the NOT-done list. The PC, real CI and `tests/test_lane_gate.py` are not run here.

## Round 3 (D-R2-2 and D-R2-3)

Written 2026-09-28 16:3xZ by the same lane, on the coordinator's round-3 message. Worktree HEAD 34d3af0.
New aliases for this section: CE = `proofs/S0-05/check_egress.py`, TA = `tests/test_attested_inputs.py`. R and T are
this round's bytes; C, T3, CC, T4, GW, W and NL are unchanged since round 2.

Report upkeep (16:3xZ): round 3 moved lines in R and T again, so the 50 R and T refs of rounds 1 and 2 now
point at the round-3 bytes. The line map is difflib's, from the round-2 bytes rebuilt by reversing this round's
edits; the rebuilt files matched round 2's sha256 prefixes (a6f721345bce4c32 R, d1c98c2f7ee55454 T). No ref
pointed at a line that round 3 changed.

### TL;DR

- **Item 1 (D-R2-2) is NOT done: I stopped on a boundary conflict.** CC has no mode set of its own, so the known set
  is C's. A CC read of C reds S0-04's drift guard (measured). Its fix is a line in `proofs/registry.yaml`, outside my
  boundary. A copy of the set in CC is the "new list" the item rules out. Two routes are below; your call.
- Item 2 (D-R2-3, VERIFY-E3 F11, both halves) is done. A default resolved with gid 0 exits 64 before anything is
  written. A7 records the Gid line beside the Uid line and compares it as numbers.
- Red on the round-2 runner: `6 failed, 4 passed in 226.08s (0:03:46)`. Green: `10 passed in 179.93s (0:02:59)`.
- Mutation table: 9 rows, each `KILLED`, after an unmutated mirror baseline `10 passed in 180.68s (0:03:00)`.
- Gates, twice each: T `337 passed`, `test_edit_snapshot_ap_screen.py` `197 passed`. The expected reds are the same
  three attestation mismatches.

### NOT-done

- Item 1 (D-R2-2): nothing built. See "Item 1: stopped".
- CE does not grade the new gid: CE@34d3af0:407 `if 0 in uid` grades the uid only. Not asked; CE is outside my boundary.
- A resolved uid 0 with a group other than 0 keeps A4's per-unit row (`not-run|unit would run as root`), not exit 64.
  The item names gid 0 only.
- No re-mint; no commit. The committed evidence and the fixtures are untouched.
- Not run: the PC, real CI.

### Item 1 (D-R2-2): stopped, with the evidence

- CC has no permitted set for api_mode: CC:350 `allowed` holds field names. C's set is
  C:215 `PERMITTED_API_MODES = frozenset({"chat_completions", "codex_responses"})`.
- CC can take that set only by reading C at run time, as C reads S0-01 (C:115 `spec_from_file_location`). S0-04's
  row in proofs/registry.yaml:15 (`"proof_id": "S0-04"`) declares no `extra_attested_inputs`, and TA:612
  `test_every_repo_file_a_checker_reads_is_attested` reds on an undeclared read.
- Measured at 15:58:46Z: a temporary CC that loads C's set that way. The S0-04 row of the guard failed with
  `AssertionError: S0-04: its checker reads repo files its attestation does not cover; declare them in proofs/registry.yaml extra_attested_inputs: ['proofs/S0-03/check_omniroute_roundtrip.py']`.
  CC was restored at once (sha256 `2627b89306128491`). The guard's S0-04 and S0-05 rows pass on the final bytes
  (`2 passed in 1.58s`).
- Route A (the item as written): you add `"extra_attested_inputs": ["proofs/S0-03/check_omniroute_roundtrip.py"]` to
  S0-04's registry row, or widen my boundary to that file. CC then loads C's set as C loads S0-01. The probe named
  only C as the new read. S0-04's attestation then covers C, so a change to C invalidates S0-04 too.
- Route B (a deviation only you can accept): CC holds its own copy of the two names, and a T4 test pins it equal to
  C's `PERMITTED_API_MODES`. No registry change, but it is the "new list" the item rules out.
- Either route gets the tests the item names: a known mode prints its name (the exact line pinned), and an unknown
  fake value built at run time prints only its shape, with no case-folded 4-character run of it in stdout or stderr.
  Each gets a named mutant.

### Item 2a (D-R2-3): a default resolved with gid 0 exits 64

What changed:
- R:277-283: after the resolution and its shape check, `if [ -n "$UNIT_USER" ] && [ "${UNIT_USER##*:}" -eq 0 ]`
  exits 64 before anything is written and before any unit launches. The message is T:4736 `DEFAULT_GID0_REFUSED`:
  `the unit user resolved from the pinned agent's owner, '<uid>:0', has gid 0 (the root group): set S0_05_UNIT_USER
  to <uid>:<gid>, each id from 1 to 4294967294`. An explicit gid 0 is refused earlier (round 2), so only a resolved
  one reaches this branch.
- R:263-264: the round-2 comment now says a resolved uid 0 keeps A4's row and `its gid 0 is refused after the resolution`.
- The order matters: a resolved 0:0 now exits 64 here, where it was A4's row. So T:2283 (`os.chown`) moves the
  `default-owner` agent to 0:65534, and A4's uid-0 row stays reachable and tested.

Tests, through the real runner:
- T:4742 `test_i59f_r3_a_default_unit_user_with_gid_0_is_refused_before_any_unit_runs`, the rows of
  T:4735 `DEFAULT_GID0_OWNERS` (65534:0 and 0:0): no `S0_05_UNIT_USER`, the stand-in chowned to the row, a
  listener up.
  Each asserts exit 64, the message as stderr's last line, no stdout, no evidence root, no unit record, no namespace.
- Positive controls: T:2227 `test_a2_s0_01_tree_change_fails_the_leg` (a default resolved to 65534:65534 runs, and the
  stand-in records 65534:65534) and T:4662 `test_i59f_a1_a_unit_user_in_range_proceeds` (an explicit 65534:65534).

Red on the round-2 runner: the `65534:0` row launched a unit (`assert 1 == 64`, a stand-in record present). The `0:0`
row got A4's row (`SKIP hermes-acp: unit would run as root`, `assert 1 == 64`).
Mutants: X-R3-default-never (2 FAILED). Under it, the `65534:0` leg launched and round 3's A7 refused it only after
the launch: `SKIP hermes-acp: unit identity not observed: gid 0`. X-R3-default-all (the positive controls, 2).

### Item 2b (VERIFY-E3 F11's other half): A7 records the Gid line and compares it as numbers

What changed:
- R:495 passes `"$UNIT_GID"` after `"$UNIT_UID"`; R:497 `want_gid, out = sys.argv[1:11]`.
- R:509-511: the status file is read once, and the Gid line beside the Uid line (`l.startswith("Gid:")`).
- R:520: the record carries `"gid": gid` beside `"uid": uid`.
- R:528 `problems += ["gid 0"] if 0 in gid else ([f"gid {gid[0]} is not {want_gid}"] if gid[0] != int(want_gid) else [])`,
  in the uid line's form.
- R:490-492: the comment above `_unit_identity() {` says so (`Its Uid and Gid` lines).

Tests:
- T:1324, in T:1207 `test_runner_live_leg`: the whole-record pin now holds `"gid": [UNIT_USER[1]] * 4`. This is the
  positive control through the real runner (65534:65534); the leg runs.
- T:2344 `test_a7_a_unit_not_matching_the_pins_is_not_observed`: a setpriv that drops nothing now shows
  T:2367-2372 `; uid 0; gid 0`, and the record's gid is `[0, 0, 0, 0]`.
- T:2632 `test_d_pair_leg_reaches_the_relay_through_the_dnat`: the binary unit's record carries
  T:2700-2701 `identity["gid"]` too.
- T:4766 `test_i59f_r3_a7_refuses_a_unit_whose_gid_is_not_the_wanted_gid`: a PATH setpriv shim runs the real setpriv
  with `--regid=65532` in place of the asked 65533 (T:4775). The unit user is 65534:65533, so uid and gid differ. The
  row is `not-run|unit identity not observed: gid 65532 is not 65533`, the record holds uid `[65534] * 4` and gid
  `[65532] * 4`, and no canary runs.

Red on the round-2 runner: the live leg's record lacked `{'gid': [65534, 65534, 65534, 65534]}`; the A7 reason lacked
`; gid 0`; the pair test raised `KeyError: 'gid'`. The shim test first raised `KeyError: 'reason'`. I then made its
row read `row.get("reason")` (T:4785), and the red re-run read `assert ('run', None) == ('not-run', '...is not 65533')`:
the leg ran with the wrong gid and its canaries ran. That re-run: `2 failed in 76.91s (0:01:16)`, with the `65534:0` row.
Mutants: X-R3-a7-no-record (2), X-R3-a7-no-zero (1), X-R3-a7-no-compare (1), X-R3-a7-want-uid (1, `gid 65532 is not
65534`), X-R3-a7-uid-line (1, `gid 65534 is not 65533`), X-R3-a7-all (the positive control, 1).

### unit-identity.json: every reader still reads the new record

- `grep -rn 'unit-identity'` over the tree finds one reader of the record's fields: CE@34d3af0:375 `def check_unit_identity`.
  It asks only that CE@34d3af0:111 `IDENTITY_KEYS` be present (CE@34d3af0:392, `any(key not in record for key in IDENTITY_KEYS)`) and
  ignores any other key. So the committed records (no gid) and the new ones (a gid) grade alike.
- The validator only hashes the files for the attestation; it reads no field. The graft indexes name the function.
- Round 3's `test_i59f_r3_the_checker_reads_an_identity_record_that_carries_the_gid` (round 4 replaced it): the
  synthetic-pass bundle with a
  Gid line added passes and prints the same identity line. Its negative control, X-R3-checker-strict (CE's key test
  made exact, in the mirror only), reds it.
- The other readers are tests. T:1321, T:2370 and T:2698 read the runner's `unit-identity.json`, updated above.
  T:792, T:2220, T:2396, T:2427 and T:2451 read or patch copies of a committed `unit-identity.json`;
  they pass unchanged in the gates.
- The committed evidence and both fixtures (`evidence-synthetic-pass`, `evidence-synthetic-uid0`) are unchanged.

### Gates, pasted from `scripts/test_summary.sh`, twice each

The gate list (`grep -l` over `tests/*.py` and `harness-ports/tests/*`): R is named by `test_edit_snapshot_ap_screen.py`
and T; T is named by `test_edit_snapshot_ap_screen.py`.

| file | set | run 1 | run 2 |
|---|---|---|---|
| T | `1 files set=9f0502080347` | `337 passed in 316.44s (0:05:16)` | `337 passed in 317.07s (0:05:17)` |
| `test_edit_snapshot_ap_screen.py` | `1 files set=3d4383148bd3` | `197 passed in 0.34s` | `197 passed in 0.31s` |

- Count: T is 333 + 4.
- Expected reds, each twice, the same three as round 2:
  - `test_validate_ledger.py` (`1 files set=852bbd75ee1d`): `2 failed, 33 passed in 10.45s` and `2 failed, 33 passed in 10.31s`.
    The two are `test_registry_rows_carry_no_key_the_validator_does_not_read` and
    `test_committed_pc_bridge_spike_validates_and_declares_all_effects`.
  - `test_proof_status.py` (`1 files set=cce0ecd44cb2`, short `--basetemp`): `1 failed, 32 passed in 6.99s` and
    `1 failed, 32 passed in 6.83s`. The one is `test_committed_state_passes_status_and_ledger`.
  - One cause: `validate-ledger integrity` reports S0-03, S0-04 and S0-05 INVALID, with exactly
    `attestation-mismatch: S0-03 proofs/S0-03/check_omniroute_roundtrip.py`,
    `attestation-mismatch: S0-04 proofs/S0-04/check_compression.py` and
    `attestation-mismatch: S0-05 proofs/S0-05/tools/pc/run_s0_05_units.sh`.
- Also run, outside the gate list: the S0-04 and S0-05 rows of TA's drift guard, `2 passed in 1.58s`.

### Mutation table (a mirror at /tmp/i59f-r3-mirror, deleted after its log was read)

Baseline, the unmutated mirror over the 10 tests: `10 passed in 180.68s (0:03:00)` (16:12:00Z-16:15:03Z). Rows ran
16:15:09Z-16:20:05Z. Each line reads `KILLED FAILED=n ERROR=0 EXPECTED=n`, with n the row's literal. Each row was checked
first: every anchor occurs once, `bash -n` passes, the 5 R heredocs compile (py_compile for CE), and the collect
count equals the row's literal.

| row | mutant | FAILED |
|---|---|---|
| X-R3-default-never | the resolved-gid check never fires (`-eq -1`) | 2 |
| X-R3-default-all | it fires for every resolved user (`-ge 0`; the positive controls) | 2 |
| X-R3-a7-no-record | the record drops `gid` | 2 |
| X-R3-a7-no-zero | no `gid 0` problem | 1 |
| X-R3-a7-no-compare | no compare with the wanted gid | 1 |
| X-R3-a7-want-uid | A7 is handed `$UNIT_UID` as the wanted gid | 1 |
| X-R3-a7-uid-line | the gid read from the Uid line | 1 |
| X-R3-a7-all | every gid refused (the positive control) | 1 |
| X-R3-checker-strict | CE refuses any key beyond its seven (mirror only) | 1 |

### Static checks and host state

- `bash -n` R: rc 0. R's 5 heredocs compile. pyflakes T: rc 0. U+2028/U+2029: 0 in R, T and this report.
- `scripts/ap_screen.py` against HEAD, whole files, as in round 2:
  - R: 16 = 16.
  - T: 37 to 38. The new tell is AF-AP-115 on T:4776's `shutil.which("setpriv")`. It is a false positive: the shim
    needs the real setpriv's path, resolved before the test changes PATH. It is a test fault, not a verifier's trust
    anchor.
  - With `--tests` (TEST_SCREEN, not run in rounds 1 and 2), T goes from 30 to 31. The new tell is AP-66 on round 1's
    mover line, T:4459 `_os.open = _open_after_a_move`, not a round-3 line.
- `scripts/report_lint.py` over the whole report (aliases C, T3, R, T, T4, W, NL, GW, CC, CE, TA; the working
  tree): `report_lint: 198 refs — OK 193, NEAR 0, MISS 0, UNCHECKABLE 5, UNRESOLVED 0 (worktree)`. The 5 are round 1's premise list of PIN grep lines.
- Host, after every S0-05 run and at the end: `ip netns list` 0 lines, iptables stable form `0528d077bca3781a`,
  mount-point hash `2dd93d06015feb4d`. The mirror is removed, and no `/tmp/i59f-*` is left. The two `/tmp/e3-*` from
  13:10Z and 13:11Z are round 1's D8, not mine.
- Disk: 1,556 MB free at round 3's start and 1,578 MB after the mirror was removed (16:35:32Z). No floor was hit.

### Final sha256 prefixes (the bytes every round-3 gate ran on)

Changed in round 3: c00ce864603003c3 R, ffd90cb561100381 T. Unchanged since round 2: 562465f01d356ada C,
bffa82c76b574bcf T3, 2627b89306128491 CC, 256328623c90966f T4, d0f1d1e6bbdc6411 GW, 594fc5b0d0564392 W,
df54c0b7b883d2d1 NL. `git status --porcelain`: these nine ` M`, the report `??`, nothing else.

### Self-attack (round 3): the three likeliest ways this round is wrong

1. **The resolved-gid rule refuses the owner's real run at the re-mint.** The committed units ran as uid 1000, and the
   S0-01 census records gid 1000 (round 2's check). The new branch reads only the gid, and a default resolved to
   65534:65534 runs (T:2227 `test_a2_s0_01_tree_change_fails_the_leg`, twice in the gates). Left open: the PC's
   pinned agent owner is inferred, not read here.
2. **A7's gid compare refuses a legitimate unit.** Supplementary groups or a partial setgid could make the four gids
   differ. Ruled out here: the live leg (T:1324) and the pair leg (T:2701) record `[UNIT_USER[1]] * 4` and run, in
   both T gates. A7 compares the real gid and refuses a 0 in any of the four, as the uid line does. Left open: the
   PC's setpriv is not run here.
3. **The new record breaks a reader.** Ruled out: the one field reader (CE@34d3af0:392 `IDENTITY_KEYS`, a subset test),
   round 3's `test_i59f_r3_the_checker_reads_an_identity_record_that_carries_the_gid` (replaced in round 4) with its
   negative control, and the unchanged committed files and fixtures in both T gates.

### Discrepancies (round 3)

- D-R3-1. **Item 1 stopped** (above). Route A or route B is your call.
- D-R3-2. **A resolved 0:0 now exits 64**, where it was A4's per-unit row. T:2283 moved its fixture to `0, 65534` to
  keep that row tested. A resolved uid 0 with a non-zero gid is still A4's row, not exit 64.
- D-R3-3. **Scratch outside the scratchpad, temporary, as in round 1's D7.** The mirror sat in `/tmp/i59f-r3-mirror`
  (772 KB, mode 0755), because the units run as uid 65534 and `/tmp/claude-0` is 0700. It was deleted after its log
  was read.
- D-R3-4. CE does not grade the gid (NOT-done); the runner's A7 does. A record with no gid still passes CE, as before.
- D-R3-5. The shim test's gids (T:4775 `--regid=65532`, and 65533) have no group entries. setpriv takes numeric
  gids, so none are needed.

### Evidence tiers (round 3)

- VERIFIED (run here, pasted above): the red and green pairs; the mirror baseline and the 9 mutants; the gates, twice
  each; the expected reds and their one cause; the drift-guard probe and CC's restore; the static checks; the host
  state.
- INFERRED: route A needs only the one registry line (the probe named only C); the PC's agent owner has a non-zero
  gid (round 2's census); CE is the only field reader (a grep, not a tool).
- ASSUMED: nothing beyond the NOT-done list.

### Item 1, route B

Written 2026-09-28 16:5xZ, on the coordinator's ruling: route B. CC keeps its own copy of the two mode names, and a T4
test pins the copy equal to C's `PERMITTED_API_MODES`, reading C as data in the test only. This is a deliberate
deviation from the round-3 "no new list" line, ruled by the coordinator: route A would make S0-04's attestation cover
S0-03's checker.

TL;DR:
- Done. A known mode is observed by its name, any other value by its shape. Failure messages print shapes, a mode
  name included. The copy is pinned to C's set.
- Red on the round-2 CC: `4 failed, 9 passed in 1.33s`. Green: `13 passed in 0.94s`.
- Mutation table: 8 rows, each `KILLED`, after a mirror baseline `13 passed in 1.38s`.
- Gates, twice each: T4 `194 passed`, `test_edit_snapshot_ap_screen.py` `197 passed`. TA's S0-04 and S0-05 drift-guard
  rows: `2 passed`, twice. S0-04's checker reads no new repo file.

What changed:
- CC:73-81: `KNOWN_API_MODES` held the two names `{"chat_completions", "codex_responses"}` (round 4 adds
  `openai_chat`, F-1). Its comment names the source
  (S0-03's `PERMITTED_API_MODES`) and the T4 pin.
- CC:376-378: the observation prints `api_mode if api_mode in KNOWN_API_MODES else _shape(api_mode)`. Membership is
  exact: no case fold, no strip.
- CC:363, CC:366 and CC:369, the three failure messages, are unchanged: each still calls `_shape`.

Tests (T4):
- Route B's `test_the_known_api_modes_are_a_copy_of_s0_03s_permitted_set` (round 4 replaced it with
  T4:861 `test_the_known_api_modes_are_pinned_to_their_sources`): it loads CC and reads C's set as data, through
  T4:825 `_s0_03_permitted_api_modes` (`ast.parse`, then T4:833 `ast.literal_eval`; C is never imported or run). It
  asserts that CC's `KNOWN_API_MODES` is a frozenset equal to C's set.
- T4:885 `test_a_known_api_mode_is_observed_by_its_name`, rows `chat_completions` and `codex_responses`. Each row
  first asserts its mode is in C's set. Then: exit 0, the exact T4:814 `OBSERVATION` line with the name, and no shape
  of the name in the output.
- T4:98: the pass bundle's pin is the exact line with the name again: `OBSERVATION.format("chat_completions")`.
- T4:896 `test_a_value_near_a_known_api_mode_is_observed_by_its_shape`, rows `case` (Chat_Completions) and
  `trailing-space` (chat_completions plus a space): the exact line with the shape.
- The unknown fake value is round 2's row T4:778 `"api-mode-observation"` of
  T4:785 `test_a_message_names_a_config_value_by_its_shape_never_the_value`. A fake built at run time prints only its
  shape, and no case-folded run of 4 of its characters reaches stdout or stderr. It is unchanged and passes.
- T4:912 `test_a_failure_prints_a_known_mode_name_by_its_shape`, rows of T4:904 `FAILURE_FIELDS`:
  config-header-value, base-url-unexpected and key-env-not-a-name. The value is `chat_completions` in each field,
  and the whole output is the one failure line, with the shape.

Red on the round-2 CC (16:46:53Z): `4 failed, 9 passed in 1.33s`. The pass pin and both known rows got the shape (for
chat_completions, `str, 16 characters, sha256 7f1bb7df`). The pin raised
`AttributeError: module 'check_compression' has no attribute 'KNOWN_API_MODES'`. The near, failure and fake rows
passed already: round 2 printed shapes everywhere. Green (16:47:27Z): `13 passed in 0.94s`.

Mutation table (a mirror in the scratchpad, 41 files, 1.1 MB, deleted after its log was read). Baseline, unmutated:
`13 passed in 1.38s`. Rows ran 16:48:04Z-16:48:24Z. Each row passed py_compile and a collect count of 13 first, then
read `KILLED FAILED=n ERROR=0 EXPECTED=n`, with n the row's literal.

| row | mutant | FAILED | killed by |
|---|---|---|---|
| X-B-known-shape | the observation always prints the shape (round 2) | 3 | the pass pin, both known rows |
| X-B-unknown-raw | the observation always prints the value | 3 | both near rows, the fake row (`a run of the config value was printed`) |
| X-B-casefold | membership after `casefold()` and `strip()` | 2 | both near rows |
| X-B-failure-header | config-header-value prints a known mode by its name | 1 | its failure row |
| X-B-failure-url | base-url-unexpected prints a known mode by its name | 1 | its failure row |
| X-B-failure-key | key-env-not-a-name prints a known mode by its name | 1 | its failure row |
| X-B-pin-drop | CC's copy lacks `codex_responses` | 2 | the pin, the `codex_responses` row |
| X-B-pin-add | CC's copy adds `responses` | 1 | the pin |

Gates, pasted from `scripts/test_summary.sh`, twice each. The gate list: CC is named by
`test_edit_snapshot_ap_screen.py` and T4; T4 is named by none.

| file | set | run 1 | run 2 |
|---|---|---|---|
| T4 | `1 files set=2e5825a9019e` | `194 passed in 21.39s` | `194 passed in 22.02s` |
| `test_edit_snapshot_ap_screen.py` | `1 files set=3d4383148bd3` | `197 passed in 0.26s` | `197 passed in 0.24s` |

- Count: T4 is 186 + 8.
- TA's drift guard, rows S0-04 and S0-05: `2 passed in 1.69s` and `2 passed in 1.47s`. S0-04's checker reads no new
  repo file: the copy is a literal in CC, and only T4 reads C.
- Expected reds, twice, unchanged: `test_validate_ledger.py` (`1 files set=852bbd75ee1d`) `2 failed, 33 passed in 10.20s`
  and `2 failed, 33 passed in 10.30s`, the same two tests; `test_proof_status.py` (`1 files set=cce0ecd44cb2`, short
  `--basetemp`) `1 failed, 32 passed in 7.19s` and `1 failed, 32 passed in 7.06s`, the same one. `validate-ledger
  integrity` names the same three attestation mismatches: S0-03, S0-04 and S0-05.

Static checks: pyflakes CC and T4: rc 0. U+2028/U+2029: 0 in CC, T4 and this report. `scripts/ap_screen.py` against
HEAD: CC 0 to 1 and T4 4 to 5, the same AP-32 display-hash tells as round 2 (CC:144 is `_shape`'s `digest` line,
moved by the new constant). No new tell. `scripts/report_lint.py` over the whole report: `report_lint: 217 refs — OK 212, NEAR 0, MISS 0, UNCHECKABLE 5, UNRESOLVED 0 (worktree)` (the aliases of round 3; the 5 are round 1's premise list).

Report upkeep: route B moved lines in CC and T4, so the report's 24 CC and T4 refs now point at route B's bytes. The
method is the one above; the rebuilt pre-route-B files matched `2627b89306128491` CC and `256328623c90966f` T4. Four
refs of round 2 pointed at lines route B changed: its observation bullet now reads in words, and its table row, its
pin line and its self-attack range cite route B's lines.

Final sha256 prefixes: changed by route B, 542a13df94edabda CC and 85bac4b5c079eac6 T4. Unchanged: 562465f01d356ada C,
bffa82c76b574bcf T3, c00ce864603003c3 R, ffd90cb561100381 T, d0f1d1e6bbdc6411 GW, 594fc5b0d0564392 W,
df54c0b7b883d2d1 NL. `git status --porcelain`: nine ` M`, the report `??`, nothing else.

NOT-done and discrepancies:
- D-B-1. **Deliberate deviation, ruled by the coordinator:** CC carries a copy of C's set, pinned by T4. A change to
  C's set reds T4's pin until CC's copy follows. S0-04's attestation does not cover C.
- D-B-2. **Adjacent, not fixed (round 4 fixed it, F-10):** route B's CC comment still called task #35 the
  `owner's open decision`. The ledger
  row todo/BUILD-TASKLIST.md:404 (`owner-adr-0002-wire-mode`) and docs/08_DECISION_LOG.md:32 (`D-021`) record it
  DECIDED on 2026-09-08. `D-021` also says every proof asserts the mode it observes, and S0-04 only records it. The
  observation text `(RECORDED, not asserted - ADR 0002 deviation, owner task #35)` is pinned by T4 and unchanged.
- D-B-3. CE is left alone, as ruled. Its gid grading (D-R3-4) goes to the verify round.
- Not run: the PC, real CI.

Self-attack (route B):
1. **The pin is blind.** It could compare the copy with itself, or with a stale parse. Ruled out: T4 reads C from
   C's own file with `ast`, never through CC. X-B-pin-drop and X-B-pin-add each red the pin, and each known row
   asserts its mode is in C's set as read.
2. **A near name, or a secret-shaped value, prints as a known mode.** Ruled out: membership is exact (X-B-casefold
   reds both near rows), and the fake-value row still asserts that no 4-character run reaches the output.
3. **The name printing leaks into a failure message.** Ruled out: the three failure rows pin the whole output with
   `chat_completions` in each field, and each X-B-failure mutant reds its row.

Evidence tiers:
- VERIFIED (run here, pasted above): the red and green pair; the mirror baseline and the 8 mutants; the gates and the
  drift guard, twice each; the expected reds; the static checks.
- INFERRED: "S0-04 reads no new repo file" rests on the drift guard's instruments. TA's docstring lists what they
  cannot see; none of it applies to a literal constant.
- ASSUMED: nothing.

## Round 4 (the verify fold and task #344)

Written 2026-09-28 21:0xZ by the same lane, on the coordinator's round-4 message. Worktree HEAD 34d3af0.
New aliases for this section: S1C = `proofs/S0-01/check_acp_conformance.py`, BCR =
`proofs/S0-01/tools/build_capture_record.py`, T1L = `tests/test_s0_01_manifest_parse_linear.py` (new). Round 4
changed C, T3, CC, T4, R, T, CE, the two synthetic fixtures, S1C and BCR, and added T1L. W, NL and GW are unchanged
since round 2.

Report upkeep (21:0xZ): round 4 moved lines in C, T3, CC, T4, R, T and CE. The line map is difflib's, from route
B's bytes. I rebuilt them by applying the harvested `tasks/briefs/i59/I59-F.patch` (main tree) to HEAD's bytes, and
they matched route B's sha256 prefixes (562465f01d356ada C, bffa82c76b574bcf T3, 542a13df94edabda CC, 85bac4b5c079eac6
T4, c00ce864603003c3 R, ffd90cb561100381 T). CE's round-3 bytes are HEAD's. 143 refs moved with their lines. 23
pointed at lines that round 4 changed: 18 now cite the same thing on its new line; 4 read in words, because round 4
replaced what they named (round 3's gid reader test, twice; route B's pin test; route B's CC comment); and round 3's
five CE refs now cite HEAD's CE as `CE@34d3af0:<line>`, where round 3's claims about CE hold. One new ref names the
test that replaced route B's pin: T4:861 `test_the_known_api_modes_are_pinned_to_their_sources`. Lint before the
upkeep: `report_lint: 217 refs — OK 57, NEAR 26, MISS 129, UNCHECKABLE 5, UNRESOLVED 0 (worktree)`. After it, before
this section: `report_lint: 214 refs — OK 209, NEAR 0, MISS 0, UNCHECKABLE 5, UNRESOLVED 0 (worktree)`.

### TL;DR

- Done: F-1, F-2, F-3 and F-8, F-4 and F-12, F-6, F-7, F-9, F-10, F-11, F-13 and F-14, and task #344. The
  verifier's surviving mutants N1 to N5 now die, each on the rows the verifier named.
- Each code change went red on its pre-fix bytes first, then green. F-3 and F-8 are test gaps (the code was right),
  so their red is the verifier's mutants.
- Mutation table: 30 rows, each `KILLED` in its final pass, after an unmutated baseline per group. One row survived
  its first pass (X-R4-F4-chain); a new positive control kills it (below).
- Gates, twice each, 12 files. All pass except T, `8 failed, 345 passed`, twice. The 8 have one cause, the expected
  F-11 red: the committed S0-05 evidence has no gid, and CE now requires one. The PC re-capture at the re-mint
  records it.
- TA's drift guard: S0-01 and S0-04 pass. S0-05 reds on the same F-11 cause; its read half, observed apart, is clean.
- **Another red: `validate-ledger integrity` names five attestation mismatches, not four. S0-02 is the fifth.**
  S0-02's registry row declares S1C an attested input, and task #344 changed S1C. S0-02 must join the re-mint.
- Task #344: 11 of 11 golden manifests give byte-identical digests (the old code from a scratch copy, both tools).
  T1L's 200,000-line parse: the old code misses the 20 s bound (red); the new code passes (`15 passed in 9.69s`).
  `tests/test_s0_01_check_acp_conformance.py`, alone: 1298.27 s before, 165.52 s after (the same four chunks); as
  one run after, 156.72 s and 160.58 s.

### NOT-done

- F-1, the Responses transport: no pinned source in the repo names one. Every `transport:` in proofs/ is
  `openai_chat` (S0-03's config, its 8 fixtures and its evidence; S0-04's config). So none is in CC's set, and
  such a value would print by its shape.
- F-5 (out of scope, a follow-up issue by the ruling); F-15 and F-16 are notes.
- No re-mint and no commit. The committed evidence is untouched, so CE reds it until the PC re-capture (F-11).
- Not run: the PC, real CI.
- R:134's `SUDO_UID and SUDO_GID must be decimal ids` refusal still quotes raw. F-14 named the explicit unit-user
  refusal only; sudo sets both ids.

### Red and green runs (each on the pre-fix bytes of the file it fixes, then on the fix)

| run | the bytes under test | selection | result |
|---|---|---|---|
| red, 18:56:02Z | HEAD's S1C and BCR | T1L, 15 | `2 failed, 13 passed in 94.40s (0:01:34)` |
| green, 18:56:32Z | the fix | T1L, 15 | `15 passed in 9.69s` |
| red, 19:05:38Z | route B's CC | T4, 20 | `13 failed, 7 passed in 2.88s` |
| green, 19:06:23Z | the fix | T4, 20 | `20 passed in 1.55s` |
| red, 19:07:51Z | round 3's C | T3, 12 | `6 failed, 6 passed in 6.37s` |
| green, 19:09:03Z | the fix | T3, 12 | `12 passed in 3.51s` |
| red, 19:16:06Z | round 3's R and CE, fixtures without a gid | T, 27 | `9 failed, 18 passed in 4.28s` |
| red, 19:19:01Z | round 3's R | T (network namespaces), 24 | `24 failed in 155.89s (0:02:35)` |
| green, 19:20:47Z | the fix | T, 27 | `6 failed, 21 passed in 3.17s`: the 6 are F-11's expected red |
| green, 19:24:04Z | the fix, plus 2 positive controls | T (network namespaces), 26 | `26 passed in 177.76s (0:02:57)` |

The times are the logs' closing times. Each run used a private `--basetemp` under `/tmp/i59f-bt-*`, removed after it.

### 1. F-1 (CC, T4): the known set holds Hermes' provider transport names too

What changed:
- CC:73-81 `KNOWN_API_MODES = frozenset({"chat_completions", "codex_responses", "openai_chat"})`. The comment says
  why (the captured field is the provider block's `api_mode`, else Hermes' `transport`) and cites each source.
  - proofs/S0-04/tools/pc/capture_leg.py:121 fills it with `block.get("transport")` when `api_mode` is absent.
  - C:215 `PERMITTED_API_MODES` gives the two api_modes.
  - proofs/S0-03/hermes/config.yaml:21 and proofs/S0-04/hermes/config.yaml:26 hold `transport: openai_chat`.
  - proofs/S0-04/evidence/config/hermes-provider.json:2 holds `"api_mode": "openai_chat"`.

Tests (T4):
- T4:861 `test_the_known_api_modes_are_pinned_to_their_sources` replaces route B's pin. It asserts that CC's set
  equals the union of four sources, and that each source names at least one mode.
- T4:853 `def _known_mode_sources` reads the sources as data: C's set through `_s0_03_permitted_api_modes` (`ast`,
  never run), each config's transports through T4:846 `def _hermes_transports` (`yaml.safe_load`), and the real
  provider block's `api_mode`.
- T4:874 `test_the_real_bundle_observes_its_transport_by_name`: `proofs/S0-04/evidence` passes, and its observation
  line is pinned exactly: `observation: config api_mode = openai_chat (RECORDED, not asserted - task #35 was decided by
  D-021 on 2026-09-08)`.
- T4:884 adds the row `"openai_chat"` to T4:885 `test_a_known_api_mode_is_observed_by_its_name`.
- An unknown value still prints only its shape: the fake-value row `api-mode-observation` of
  T4:785 `test_a_message_names_a_config_value_by_its_shape_never_the_value`, and the rows `case` and `trailing-space` of
  T4:896 `test_a_value_near_a_known_api_mode_is_observed_by_its_shape`.

Red on route B's CC: the pin (`frozenset({'c...x_responses'}) == frozenset({'c...openai_chat'})`), the real-bundle
line and the `openai_chat` row (both printed the shape).
Mutants: X-R4-F1-drop (the set without `openai_chat`): 3. X-R4-F1-add (the set adds `openai_responses`, a name with
no source): 1, the pin.

### 2. F-2 (CC): a provider block that is not a JSON object

What changed: CC:348-349 `if not isinstance(provider, dict):` fails `provider block is not a JSON object` before
any field is read.

Tests: T4:921 `test_a_provider_block_that_is_not_a_json_object_is_refused_and_prints_nothing_of_it`, the rows
of T4:920 `["array", "string", "number"]`. Each asserts exit 1, the whole stdout is the one line
`failure_reason: config: provider block is not a JSON object`, stderr is empty, and no case-folded run of 4
characters of the fake value reaches the output.

Red on route B's CC: the array printed its element through `unexpected-provider-fields` (21 runs of the fake value);
the string printed its sorted characters (`unexpected-provider-fields: %,*,+,;,?,...`); the number failed as
`failure_reason: malformed evidence: TypeError: 'int' object is not iterable`.
Mutant: X-R4-F2-guard (the check removed): 3.

### 3. F-3 and F-8 (tests): the rows the verifier's mutants needed

What changed (tests only):
- T:4627 `BAD_UNIT_USERS` adds `4294967296:65534`, `65534:4294967296`, `4294967295:65534`, `65534:4294967295`,
  `0:65534` and `65534:0` (F-3), and `65534:65534` plus a newline (F-14, item 9).
- T:4639 shows the newline in the row's id as `<newline>`, and each row gets its own listener port:
  T:4644 `port = 18180 + BAD_UNIT_USERS.index(value)`.
- T3:967 `PROFILE_VALUE_PATHS` adds T3:973 `"api_mode-a-list"` and T3:983 `"key_env-a-list"`.
- T4:767 `CONFIG_VALUE_PATHS` adds T4:776 `"key-env-a-list"`.
- A new last column plants the fake value as it is (T3:963 `def _as_is`, T4:763 `def _as_is`) or inside a list:
  a non-string (F-8).

Red: the code was right (the verifier said so), so the red is on the mutants. On the round-3 runner all 17
`BAD_UNIT_USERS` rows failed too, but on item 9's new quoting, not on their own values.
Mutants (the verifier's, now killed):
- N1 (the uid bound removed): 2, `4294967296:65534` and `4294967295:65534`. Under N1 the first launched the
  stand-in as uid 0 (`'uid': 0` in its record), and A7 refused it only after the launch
  (`SKIP hermes-acp: unit identity not observed: uid 0`): round 1's hole.
- N2 (the gid bound removed): 2, `65534:4294967296` and `65534:4294967295`.
- N3 (the explicit pattern admits uid 0): 1, `0:65534`. It reached A4's `SKIP hermes-acp: unit would run as root`
  (exit 1, not 64).
- N4 (C's `_shape` prints a non-string whole): 2, the two T3 list rows.
- N5 (CC's `_shape` prints a non-string whole): 1, the T4 list row.

### 4. F-4 and F-12 (R's walk): every climb checks the way up to the root

What changed:
- R:653 `def off_the_way(fd, where)`: from the directory a climb reached, it checks each `..` up to the root against
  the stack's frames (st_dev and inode, the root's frame included). It holds at most two descriptors of its own.
  It returns "" while the walk is inside the root, else the stop reason:
  - R:663 `a mount appeared above {where} while it ran`: the st_dev or the mount id differs (F-12);
  - R:665 `{where} moved while it ran`: the directory itself moved;
  - R:666 `an ancestor of {where} moved out of the root while it ran` (F-4's second case);
  - R:674 `could not be checked`, with the error's class.
- R:717 `stopped = off_the_way(cur, where)`: every climb runs the check. Round 1 checked the directory itself only.
- R:588 `It changes only what it finds` replaces "It changes nothing outside the root", and points at the limit.
  R:603-608 states what holds: `every climb checks the whole way up`, and between two climbs a live process can still
  move an entry out and have it handed back where it then is (F-5 names such a process; out of scope).

Tests:
- T:4827 `test_i59f_r4_the_walk_stops_when_an_ancestor_moved_out_of_the_root`: a mover renames the ancestor `p` out
  of the root the first time the walk opens `..`. The walk stops at that climb with the exact line (4 entries
  handed back), and `outside/p/zz-decoy`, which it had not reached, keeps its owner.
- T:4880 `test_i59f_r4_the_walk_names_a_mount_on_its_way_up_as_a_mount`: a mover mounts a tmpfs on `d` at the
  first `..` (T:4868 `MOUNT_BEFORE_THE_WAY_UP`). The stop line names a mount, `d/c` keeps its owner, and the tmpfs
  is unmounted by its path.
- T:4848 `test_i59f_r4_the_walk_climbs_a_clean_tree_to_its_end`, the positive control: four levels with a file at
  each; all 8 entries are handed back, and the summary names no stop.
- Round 1's B-3 tests pass unchanged, the 1,100-level tree included.

Red on the round-3 runner: in the ancestor case the walk handed back 5 entries, one of them outside the root, and
stopped late with `<tmp>/evidence/p moved while it ran`. The mount case said `<tmp>/evidence/d/b moved while it ran`.
Mutants: X-R4-F4-first-only (only the directory itself is checked, round 1's rule): 1, the ancestor test.
X-R4-F4-chain (the climb never opens `..`): 1, the clean-tree test. X-R4-F12-word (the mount branch never taken): 1,
the mount test.
X-R4-F4-chain SURVIVED its first pass (19:26Z): the ancestor test's stop line matched under it by chance. I then
added the clean-tree positive control and X-R4-F4-first-only; the re-run killed both.
Cost: the 1,100-level handback takes 4.82 s and 4.77 s per row now, against 2.46 s and 2.37 s on route B's R (one
run each, in a mirror). Each climb re-checks the way up, so a walk is quadratic in its depth.

### 5. F-7 (R's launch and A7): no supplementary group is inherited

What changed:
- Both launches take `--clear-groups` where they took `--init-groups`: the agent launch
  (R:909 `--clear-groups -- "${PIN[$exe_pin]}"`) and the pair launch (R:914 `--clear-groups -- "$PY_BIN"`). The list
  is explicit and empty, the one the scratch probe already used (R:883 `--clear-groups`).
- setpriv here is util-linux 2.39.3, and its help lists `--clear-groups` (`clear supplementary groups`). Run as
  65534:65534, the Groups line is empty with it, and `65534` with `--init-groups`.
- A7 reads the Groups line (R:512 `startswith("Groups:")`) and records it (R:520 `"groups": groups`).
- R:529 `problems += ["supplementary group 0"] if 0 in groups else []`.
- The comments say so: R:490-493 (`a 0 in it refused`) and R:898-900 (`--clear-groups`).

Tests:
- T:1325 `"groups": []`: the live leg's whole-record pin, the positive control through the real runner.
- T:2700-2701: the pair leg's record holds `identity["groups"]` equal to `[]`.
- T:2367-2373 (`supplementary group 0`): in the A7 not-matching test, setpriv drops nothing, so the record holds
  the suite's own groups (`identity["groups"] == os.getgroups()`), and the reason ends `; supplementary group 0`
  when they hold a 0.
- T:4901 `test_i59f_r4_a7_refuses_a_unit_with_supplementary_group_0`: a PATH setpriv shim replaces every group
  option with T:4912 `--groups=0,65534`, as `--init-groups` would on a host that lists the unit user in group 0. The
  row is `not-run|unit identity not observed: supplementary group 0`. The record holds uid and gid `[65534] * 4`
  and groups `[0, 65534]`, and no canary runs.

Red on the round-3 runner: the three records lacked `groups`, and the shim leg ran with group 0.
Mutants: X-R4-F7-launch (`--init-groups` at the agent launch): 1, the live leg (`{'groups': [65534]} != {'groups':
[]}`). X-R4-F7-pair (the same at the pair launch): 1, the pair leg. X-R4-F7-a7 (no group-0 problem): 1, the shim
test. X-R4-F7-record (the record drops `groups`): 2.

### 6. F-11 (CE, the two fixtures): CE grades the gid

What changed:
- CE:113 `IDENTITY_KEYS` adds `"gid"` after `"uid"`. A record without a gid fails at CE:394-395 (`lacks one of`).
- CE:411-415: a gid that is not four non-negative ints fails `is not the four gids of the Gid line`, and a 0 in it
  fails `refuse("gid 0")`. Both print as `unit-identity-invalid: <unit> <detail>`.
- CE:48-49 (`no gid 0`) and CE:111-112 (`the gid since I59-F round 4`) say so.
- Both synthetic fixtures' `hermes-acp/unit-identity.json` gain `"gid": [1000, 1000, 1000, 1000]`. The uid0
  fixture keeps uid `[0, 0, 0, 0]`, so the two still differ in the uid only.

Tests: four rows join `test_a7_the_checker_refuses_an_identity_that_is_not_the_pin`, each with its exact line.
- T:2412-2414: a 0 in the gid (`"gid 0"`), a gid that is not a list, and a bool in it.
- T:2418 `"drop-gid"`: the key deleted. T:2421 names the four `"effective-gid-0"`, `"gid-not-a-list"`, `"gid-bool"`
  and `"missing-gid"`.
- The `missing-key` row names the new key list. Both fixture tests pass.

Red on round 3's CE: the three gid rows passed as valid (`assert 0 == 1`), `missing-key` named the old key list,
and `missing-gid` raised `KeyError: 'gid'` (the fixture had no gid yet).
Mutants: X-R4-F11-gid0 (no gid-0 refusal): 1. X-R4-F11-key (the key list without `gid`): 2.

**The expected red (F-11), one cause.** The committed evidence (`proofs/S0-05/evidence`) was captured before round 3,
so its two records carry no gid, and CE now refuses them:
`unit-identity-invalid: buzz-acp unit-identity.json lacks one of unit, pid, exe_realpath, entrypoint_realpath, entrypoint_sha256, uid, gid, argv`.
It reds 8 tests in T (listed under Gates), TA's S0-05 row, and S0-05's spec leg 1. The PC re-capture at the re-mint
runs the round-4 runner, whose A7 writes the gid and the groups.

### 7. F-9 (C): no traceback, and a read error is named as one

What changed:
- C:823 `if not isinstance(api_mode, str) or api_mode not in PERMITTED_API_MODES:`. A list or a mapping fails with
  its shape (the transport reason), not `TypeError: unhashable type`.
- C:779 `def _walk_credentials` keeps the ids of the mappings and lists open on the current path:
  C:787 `_open.add(id(node))`.
- A node met again on its own path fails with C:786 `has a recursive alias under` and the path, never
  `RecursionError`. A node aliased twice side by side is walked twice: C:791 `_open.discard(id(node))`.
- The walk's body moved to C:794 `def _walk_node`.
- C:278 `def _read_yaml`: the read has its own try block, and C:284 catches `OSError` and `UnicodeError`. It fails with
  C:287 `cannot be read` and the class name. The parse keeps C:296 `is not valid YAML`.

Tests (T3):
- T3:973 `"api_mode-a-list"` (item 3) is F-9's unhashable value.
- T3:1023 `test_a_recursive_alias_in_the_provider_block_fails_by_name`, the rows of T3:1015 `RECURSIVE_ALIASES` (a
  list inside itself, a mapping inside itself): exit 1, the one line naming where the alias closes, empty stderr.
- T3:1034 `test_an_anchor_used_twice_without_a_cycle_is_no_recursive_alias`, the negative control: it passes.
- T3:1046 `test_a_profile_that_cannot_be_read_is_named_a_read_error`, rows `not-utf-8` (read as root) and
  `unreadable` (mode 0000, read as uid 65534 in a 0711 directory of its own under /tmp):
  `failure_reason: bundle: hermes/profile.yaml cannot be read (<class>)`.
- T3:876 `def _profile_refusal`: the two parse-error tests (T3:907 and T3:922 `_profile_refusal(cls)`) now expect
  `cannot be read (UnicodeDecodeError)` for their `invalid-utf8` row. See D-R4-2.

Red on round 3's C: `api_mode-a-list` gave an empty stdout (a traceback); both alias rows ended in `RecursionError`;
both read rows said `is not valid YAML (UnicodeDecodeError)` and `is not valid YAML (PermissionError)`.
The red run expected `profile.yaml cannot be read`; the checker names the file `hermes/profile.yaml`, so I corrected
the test before the green. Round 3's C fails either way: it says `is not valid YAML`.
Mutants: X-R4-F9-hash (the type check removed): 1. X-R4-F9-cycle (the cycle check never fires): 2. X-R4-F9-ever (a
node stays open after its walk): 1, the negative control. X-R4-F9-read (the read's `except` catches nothing, and the
read moves back into the parse): 2.

### 8. F-10 (CC, T4): the observation says task #35 is decided

What changed: CC:374-379 end the observation with `task #35 was decided by D-021 on 2026-09-08`. The comment
says so and cites docs/08_DECISION_LOG.md:32 (`D-021`). A grep finds neither `open decision` nor
`ADR 0002 deviation` in CC, T4 or any other test.

Tests: T4:814 `OBSERVATION` and every pin that uses it: T4:95 `test_observations_are_recorded_not_asserted`, the
known and near rows, the fake-value row and the real bundle.
Red on route B's CC: the 8 pins of the observation line. Mutant: X-R4-F10-text (route B's text back): 8.

### 9. F-13 and F-14 (R): explicit classes, and `printf %q` in the refusals

What changed:
- The three id patterns spell every class as an explicit list, `[123456789][0123456789]{0,9}`, as netns_lib.sh's
  rule X1 spells them (proofs/S0-05/netns_lib.sh:75 `every class is an explicit list`):
  - R:133 `SUDO_UID` with `SUDO_GID`;
  - R:267 `[123456789][0123456789]{0,9}`, an explicit unit user;
  - R:274 `[123456789][0123456789]{0,9}`, a resolved one.
- The comments say so: R:132 and R:264-266 (`explicit list`).
- R:269 and R:275 quote an explicit value with `printf '%q' "$UNIT_USER"`, and R:281 a resolved one, so a newline
  cannot split the line.

Tests:
- T:4815 `test_i59f_r4_the_id_patterns_spell_their_classes_as_explicit_lists`: R's three id patterns hold no range.
- T:4633 `UNIT_USER_REFUSED` and T:4736 `DEFAULT_GID0_REFUSED` take the value through T:4355 `def _quoted`, bash's
  own `printf %q` (T:4655 `_quoted(value)`). The new row `65534:65534` plus a newline is refused on one line.
- T:2297 pins `got 00:0 ` for the resolved-shape refusal.

Red on the round-3 runner: the pattern test found three range patterns, and every refusal row failed on the quoting
(`got '...'`).
Mutants: X-R4-F13-range (the SUDO pattern's first class back to `[1-9]`): 1. X-R4-F14-raw (the explicit refusal
quotes raw): 2, the newline row and `0:65534`.

### 10. F-6 (C, CC): `_shape` says what it protects

What changed: C:237 `def _shape` and CC:135 `def _shape`. Each docstring now says it protects a high-entropy value
(a key, a token) only, and that a short or guessable value is recoverable by `brute force`: C:241-243 and CC:139-140.

Tests: T3:1078 and T4:936 `test_shape_says_it_protects_a_high_entropy_value_only`, a documentation pin read with
`ast`.
Red: both pins failed on the pre-fix docstrings. Mutants: X-R4-F6-doc-C and X-R4-F6-doc-CC (the sentence removed):
1 each.

### 11. Task #344 (S1C, BCR, T1L): each digest in linear time, over the same bytes

What changed (both line-count neutral):
- S1C:1058 `digests[tree_name] = []` and S1C:1066 `digests[current_tree].append(line)` collect each tree's lines.
- S1C:1078 `"".join(f"{line}\n" for line in lines)` joins them once, then hashes them.
- BCR:42 `sections[current] = []`, BCR:44 `sections[current].append(line)` and
  BCR:45 `"".join(f"{line}\n" for line in v)` do the same.
- Why: CPython extends a string in place only when nothing else holds it. The dict held each section, so every `+=`
  copied the whole section: quadratic.

Byte identity (run at 20:34Z): on each of the 11 committed golden manifests, the old code and the new code give
equal digests, in both tools, and the two tools agree. The old code ran from scratch copies of HEAD's bytes
(868b8705699b5e78 S1C, c9709755c60bfe99 BCR), each tool in a child process. The script's last line:
`11 of 11 golden manifests: old == new in both tools, and the two tools agree`.

Tests (T1L, new):
- T1L:82 `test_the_checker_parses_200000_lines_within_the_bound` and
  T1L:100 `test_the_record_builder_parses_200000_lines_within_the_bound`: a 200,000-line manifest (four trees of
  T1L:28 `LINES_PER_TREE`, in the pinned header order and line shape) is parsed in a child process whose timeout is
  T1L:29 `BOUND` (20 s).
- The checker must read to the end and refuse the per-tree count with the exact line. The builder's digests must
  equal those of T1L:59 `def _oracle`, which is computed apart from both tools.
- T1L:72 `test_the_big_manifest_is_one_the_checker_parses_line_by_line`: the big manifest is well formed, so the
  checker reads every line.
- T1L:115 `test_there_are_committed_golden_manifests` (11), and
  T1L:121 `test_a_committed_golden_manifest_keeps_its_digests_in_both_tools`: both tools equal the oracle on each.

Red on the old code: the two bound tests, each `subprocess.TimeoutExpired` at 20 s. Measured once here, the old code
needed 113.94 s in the checker and 53.51 s in the builder.
Mutants (a mirror in the scratchpad, the golden manifests linked read only): X-344-c-old (S1C's `+=` back): 1.
X-344-b-old (BCR's): 1. X-344-c-bytes (the join drops the last newline, S1C): 11. X-344-b-bytes (the same, BCR): 12,
the golden rows and the builder's bound test (its oracle compare).

Wall time of `tests/test_s0_01_check_acp_conformance.py` (468 tests), alone, each call with a private `--basetemp`:
- Before (HEAD's S1C): one run did not finish inside one call's 590 s bound (it started 18:16Z). So I split the file
  into four chunks and ran them one after another, 18:27Z to 18:49Z: `142 passed in 397.79s (0:06:37)`,
  `114 passed in 235.70s (0:03:55)`, `118 passed in 453.70s (0:07:33)`, `94 passed in 211.08s (0:03:31)`. Sum:
  1298.27 s.
- After (the final S1C), the same four chunks, 19:40Z to 19:43Z: `142 passed in 52.35s`, `114 passed in 34.52s`,
  `118 passed in 49.99s`, `94 passed in 28.66s`. Sum: 165.52 s. As one run (the two gate runs):
  `468 passed in 156.72s (0:02:36)` and `468 passed in 160.58s (0:02:40)`.
- The host is shared: other sessions' processes ran during both measurements.

### unit-identity.json readers (F-7: "update the record's readers as in round 3")

- `grep -rln 'unit-identity'` over the tree's *.py, *.sh and *.yml finds CE, R and T only.
- CE:377 `def check_unit_identity` is the one field reader. It grades its eight keys (CE:113 `IDENTITY_KEYS`) and
  ignores any other, so it does not grade `groups`; the runner's A7 refuses a 0 there.
- T:4795 `test_i59f_r4_the_checker_reads_an_identity_record_that_carries_the_groups` replaces round 3's gid reader
  test. The synthetic-pass bundle with `"groups": []` added passes and prints the same identity line.
- The tests that read the runner's records assert `groups`: T:1325, T:2373 and T:2700.
- The validator hashes the files for the attestation and reads no field. The committed evidence is unchanged (no
  gid, no groups): that is F-11's red.

### Gates, pasted from `scripts/test_summary.sh`, twice each

The gate list (`grep -l` of each changed file's name over `tests/*.py` and `harness-ports/tests/*`):
- S1C: `test_pc_suite_set_id.py`, `test_s0_01_audit_cp5_controls.py`, `test_s0_01_check_acp_conformance.py`,
  `test_s0_01_frame_tee.py`, T1L, `test_s0_01_pc_tools.py`, `test_s0_01_spec_runner.py` and T3.
- BCR: `test_edit_snapshot_ap_screen.py`, T1L, `test_s0_01_pc_tools.py` and `test_s0_01_scripted_backend.py`
  (`tests/conftest.py` names it too; every file loads it).
- CC: `test_edit_snapshot_ap_screen.py` and T4. C: T3 and T4. R: `test_edit_snapshot_ap_screen.py` and T.
- CE and the fixtures: T. T: `test_edit_snapshot_ap_screen.py`. T3, T4 and T1L: named by none.

| file | set | run 1 | run 2 |
|---|---|---|---|
| T1L | `1 files set=b00026b98230` | `15 passed in 8.47s` | `15 passed in 8.84s` |
| T4 | `1 files set=2e5825a9019e` | `201 passed in 21.76s` | `201 passed in 20.72s` |
| `test_edit_snapshot_ap_screen.py` | `1 files set=3d4383148bd3` | `197 passed in 0.21s` | `197 passed in 0.21s` |
| `test_pc_suite_set_id.py` | `1 files set=aca91e7d0b0f` | `3 passed in 0.20s` | `3 passed in 0.19s` |
| T3 | `1 files set=696563f67d3c` | `221 passed in 39.42s` | `221 passed in 41.47s` |
| `test_s0_01_audit_cp5_controls.py` | `1 files set=17a682bf802d` | `3 passed in 1.44s` | `3 passed in 1.39s` |
| `test_s0_01_frame_tee.py` | `1 files set=7756619494e8` | `121 passed in 177.61s (0:02:57)` | `121 passed in 196.94s (0:03:16)` |
| `test_s0_01_pc_tools.py` | `1 files set=852dc4610aeb` | `106 passed in 2.81s` | `106 passed in 3.56s` |
| `test_s0_01_spec_runner.py` | `1 files set=cf2007c5ce13` | `15 passed in 10.89s` | `15 passed in 13.13s` |
| `test_s0_01_scripted_backend.py` | `1 files set=b10e41027c9e` | `348 passed in 101.69s (0:01:41)` | `348 passed in 101.04s (0:01:41)` |
| `test_s0_01_check_acp_conformance.py` | `1 files set=31306c49985e` | `468 passed in 156.72s (0:02:36)` | `468 passed in 160.58s (0:02:40)` |
| T | `1 files set=9f0502080347` | `8 failed, 345 passed in 380.58s (0:06:20)` | `8 failed, 345 passed in 373.65s (0:06:13)` |

- Counts: T3 is 213 + 8. T4 is 194 + 7 (route B's pin test replaced, not added). T is 337 + 16 (round 3's gid
  reader test replaced). T1L is new: 3 + 1 + 11.
- T's 8, the same in both runs, all F-11's one cause (item 6): `test_the_committed_live_root_needs_its_unit_list`,
  `test_every_spec_leg_behaves_exactly_as_declared`, `test_the_committed_live_bundle_passes_with_every_line_pinned`,
  and five rows of `test_a_hostile_copy_of_the_live_bundle_fails_by_name` (`c2-egress-open`, `c1-proxy-new-spelling`,
  `gate-inert`, `override-present`, `identity-not-pinned`). Each run's last failure reads item 6's line.
- The first whole-file T3 run, on an earlier T3 (sha256 5244e38c7cda3451), failed 2: the `invalid-utf8` rows of the
  two parse-error tests. `_profile_refusal` followed (D-R4-2), and both T3 runs above are after it.
- TA's drift guard, rows S0-01, S0-04 and S0-05 of `test_every_repo_file_a_checker_reads_is_attested`
  (a selection of `1 files set=96d60da64331`): `1 failed, 2 passed in 6.07s` and `1 failed, 2 passed in 6.26s`.
  S0-01 and S0-04 pass. The S0-05 row fails at the guard's first assert, a leg's exit: leg 1 (the committed
  evidence) exits 1 where its spec says 0, F-11's cause.
  - That assert hides the guard's read half, so I observed it apart with TA's own `_observe` and the validator's
    `proof_attestation`, read only: S0-05 reads 14 repo files, and none is outside its attestation, none is tested
    outside it, none inside is uncovered, and no child process escapes.
- Expected reds, each twice:
  - `test_validate_ledger.py` (`1 files set=852bbd75ee1d`): `2 failed, 33 passed in 10.96s` and
    `2 failed, 33 passed in 10.47s`. The two are `test_registry_rows_carry_no_key_the_validator_does_not_read` and
    `test_committed_pc_bridge_spike_validates_and_declares_all_effects`, as in rounds 2 and 3.
  - `test_proof_status.py` (`1 files set=cce0ecd44cb2`, short `--basetemp`): `1 failed, 32 passed in 7.97s` and
    `1 failed, 32 passed in 6.76s`. The one is `test_committed_state_passes_status_and_ledger`.
  - Their one cause: `python3 scripts/validate-ledger integrity` (twice, the same output) reports S0-01 to S0-05
    INVALID and S0-06 to S0-12 PRESENT, with exactly these five lines:
    - `attestation-mismatch: S0-01 proofs/S0-01/check_acp_conformance.py`
    - `attestation-mismatch: S0-02 proofs/S0-01/check_acp_conformance.py`
    - `attestation-mismatch: S0-03 proofs/S0-01/check_acp_conformance.py`
    - `attestation-mismatch: S0-04 proofs/S0-04/check_compression.py`
    - `attestation-mismatch: S0-05 proofs/S0-05/check_egress.py`
  - Each line names the first changed input only (sorted). All of them, from the validator's own
    `proof_attestation` against each committed result: S0-01: S1C and BCR. S0-02: S1C. S0-03: S1C and C. S0-04: CC.
    S0-05: CE, both fixtures and R.
- **The red outside the expected list: S0-02.** S0-02's checker loads S1C:
  proofs/S0-02/check_buzz_authz.py:98 `_load_by_path("s0_01_check_acp_conformance", S0_01_CHECKER)`.
  So proofs/registry.yaml:13 lists S1C in S0-02's `extra_attested_inputs`. Task #344 changed S1C, so S0-02's
  attestation no longer matches. S0-02 needs the re-mint too.

### Before the re-mint (a dry run, read only)

Each spec leg, run now, against its committed stdout hash (S0-01 with the sandbox venue's defaults of
`scripts/test_summary.sh`):
- S0-01 (2 legs), S0-02 (6) and S0-03 (5): every leg exits as its spec says, and every stdout is the same. Only the
  attestation changes.
- S0-04: the positive leg's stdout changes (the observation text: F-1 and F-10). The negative leg's is the same.
- S0-05: legs 0, 2 and 3 are the same. Leg 1 (the committed evidence) exits 1 where the spec says 0 (F-11) until the
  PC re-capture.

### Mutation table

Mirrors: `/tmp/i59f-r4-mirror` (mode 0755: the units run as uid 65534, and one T3 row reads as uid 65534) and
`scratchpad/i59f/mirror-344`. Each was deleted after its log was read. Each row was checked first: every anchor
occurs once; py_compile passes, or `bash -n` and R's 5 heredocs; the collect count equals the row's literal. A row is
`KILLED` when it gives exactly its expected FAILED count, `ERROR=0` and exit 1.
- Passes: the task #344 rows at 18:58Z, the rest at 19:25Z to 19:34Z. The S1C rows re-ran at 19:39Z on S1C's final,
  line-neutral form (D-R4-5). Group B and the BCR rows re-ran on the final bytes at 20:27Z to 20:29Z, because T3 and
  S1C changed after their first pass. The pair row ran at 20:42Z to 20:43Z.
- Baselines, unmutated: A `20 passed in 1.57s`; B `12 passed in 3.57s` (the re-run); C `21 passed in 2.55s`;
  network namespaces `8 passed in 72.72s (0:01:12)`; pair `1 passed in 39.54s`; #344 `15 passed in 9.76s` (the
  re-run).

| row | mutant | FAILED |
|---|---|---|
| X-R4-F1-drop | CC's set without `openai_chat` | 3 |
| X-R4-F1-add | CC's set adds `openai_responses` | 1 |
| X-R4-F2-guard | the not-an-object check removed | 3 |
| X-R4-F10-text | route B's observation text back | 8 |
| N5 | CC's `_shape` prints a non-string whole | 1 |
| X-R4-F6-doc-CC | CC's `_shape` docstring sentence removed | 1 |
| X-R4-F9-hash | C's api_mode type check removed | 1 |
| X-R4-F9-cycle | the recursive-alias check never fires | 2 |
| X-R4-F9-ever | a node stays open after its walk | 1 |
| X-R4-F9-read | the read error caught by nothing, the read back in the parse | 2 |
| N4 | C's `_shape` prints a non-string whole | 2 |
| X-R4-F6-doc-C | C's `_shape` docstring sentence removed | 1 |
| X-R4-F13-range | the SUDO pattern's first class back to `[1-9]` | 1 |
| X-R4-F4-chain | the climb never opens `..` (SURVIVED its first pass) | 1 |
| X-R4-F4-first-only | only the directory itself is checked | 1 |
| X-R4-F12-word | the mount branch never taken | 1 |
| X-R4-F11-gid0 | CE's gid-0 refusal removed | 1 |
| X-R4-F11-key | CE's key list without `gid` | 2 |
| N1 | the uid bound removed | 2 |
| N2 | the gid bound removed | 2 |
| N3 | the explicit pattern admits uid 0 | 1 |
| X-R4-F14-raw | the explicit refusal quotes raw | 2 |
| X-R4-F7-launch | `--init-groups` at the agent launch | 1 |
| X-R4-F7-pair | `--init-groups` at the pair launch | 1 |
| X-R4-F7-a7 | no supplementary-group-0 problem | 1 |
| X-R4-F7-record | the record drops `groups` | 2 |
| X-344-c-old | S1C's `+=` back | 1 |
| X-344-b-old | BCR's `+=` back | 1 |
| X-344-c-bytes | S1C joins without the last newline | 11 |
| X-344-b-bytes | BCR joins without the last newline | 12 |

### Static checks and host state

- pyflakes over the nine Python files I changed (T1L included): rc 0. `bash -n` R: rc 0, and R's 5 heredocs
  compile. U+2028 and U+2029: 0 in every changed file and in this report.
- `scripts/ap_screen.py` against HEAD, whole files:
  - S1C 14 = 14, BCR 17 = 17, CE 2 = 2, R 16 = 16.
  - C 0 to 1, CC 0 to 1, T3 6 to 7 and T4 4 to 5: the AP-32 display-hash tells of round 1 and route B, unchanged.
  - T 37 to 39. The new AF-AP-115 tell is round 4's shim, T:4913 `shutil.which("setpriv")`. It is the same false
    positive as round 3's at T:4776 `shutil.which("setpriv")`: the shim needs the real setpriv's path, resolved
    before the test changes PATH.
  - T1L 2 (a new file): AP-32 on T1L:54 and T1L:68 (`hexdigest()`), the fake lines' hashes and the oracle. The
    oracle hashes exactly the bytes the tools hash; the golden rows prove it.
  - With `--tests`: T 30 to 32. The new tell is AP-66 on T:4875 `_os.open = _open_after_a_mount`, program text that
    the handback's child runs, so it cannot leak into a later test. Round 1's mover is the same case:
    T:4459 `_os.open = _open_after_a_move`.
  - With `--tests`: T4 3 to 4. The tell is AF-AP-80 on T4:798 `assert value in path.read_text()`, round 2's
    precondition that the planted value reached the bundle whole; round 4 did not write that line. T3 6 = 6; T1L 0.
- Host, after every S0-05 run and at the end: `ip netns list` 0 lines, iptables stable form `0528d077bca3781a`, and
  mount-point hash `2dd93d06015feb4d`. No `/tmp/i59f-*` and no `/tmp/s0-03-unreadable-*` is left.
- Disk: 11876 MB free at the end. My scratch stayed under 2 MB.
- `scripts/report_lint.py` over the whole report (aliases C, T3, R, T, T4, W, NL, GW, CC, CE, TA, S1C, BCR, T1L; the
  working tree): `report_lint: 357 refs — OK 352, NEAR 0, MISS 0, UNCHECKABLE 5, UNRESOLVED 0 (worktree)`.
  The 5 are round 1's premise list of PIN grep lines.

### Final sha256 prefixes (the bytes every round-4 gate ran on)

Changed in round 4: 41014abdff4601cf S1C, 1557dc3010401225 BCR, 4784750397ef56ca T1L (new), 1e69424390142b44 C,
9720944aa3e6da44 T3, 09c45268d76dbfd1 CC, ffd707f874d74f28 T4, 5c4600661faeaf29 R, aaca225c88805245 T,
383bbddc7b8140bc CE, af1b9d92cbc1e4e7 `evidence-synthetic-pass/hermes-acp/unit-identity.json`, 7b176e89a4892b85
`evidence-synthetic-uid0/hermes-acp/unit-identity.json`. Unchanged since round 2: 594fc5b0d0564392 W,
df54c0b7b883d2d1 NL, d0f1d1e6bbdc6411 GW. `git status --porcelain`: 14 ` M`, T1L and this report `??`, nothing else.

### Self-attack (round 4): the three likeliest ways this round is wrong

1. **The gid grading (F-11) or the group list (F-7) refuses the owner's real re-capture.** The PC re-capture runs
   the round-4 runner. Ruled out here: the live leg and the pair leg run through the real runner and record the gid
   and an empty Groups line (T:1325 `"groups": []`, T:2700 `identity["groups"]`), in both T gates. The
   synthetic-pass fixture with a gid passes CE. Left open: the PC's setpriv and its /etc/group are not run here.
   util-linux 2.39.3 here takes `--clear-groups`; the PC's version is not read.
2. **The per-climb check stops a legitimate handback, or costs too much.** Ruled out: the clean-tree positive
   control hands back every entry (T:4848 `test_i59f_r4_the_walk_climbs_a_clean_tree_to_its_end`), and round 1's
   1,100-level tree is handed back whole, in both T gates. The cost is measured: 4.8 s against 2.4 s per row for
   1,100 levels. A real evidence tree is a few levels deep. Left open: between two climbs, a live process can still
   move an entry out and have it handed back, as R:605-607 says (`Between two climbs`); F-5 is out of scope.
3. **The widened set (F-1) is the wrong vocabulary again, or prints a value it should not.** The observed field is
   the provider block's `api_mode`, else its `transport` (capture_leg.py, item 1). Every pinned transport in the
   repo is `openai_chat`, and the real bundle now prints it by name:
   T4:874 `test_the_real_bundle_observes_its_transport_by_name`. Membership is exact (the near rows). The pin reds
   on an added or a dropped name (X-R4-F1-add, X-R4-F1-drop), and the fake-value row still finds no 4-character run
   of the value. Left open: a future Responses transport prints by its shape until a pinned source names it.

### Discrepancies (round 4)

- D-R4-1. **A fifth attestation mismatch: S0-02** (Gates). The coordinator's list names S0-01, S0-03, S0-04 and
  S0-05. S0-02 declares S1C, so task #344 invalidates it too. S0-02's legs give the same stdout (the dry run), so its
  re-mint changes the attestation only.
- D-R4-2. **A non-UTF-8 profile is now a read error.** C's read raises UnicodeDecodeError, so C names it
  `cannot be read (UnicodeDecodeError)`, where round 3 said `is not valid YAML (UnicodeDecodeError)`. I read F-9's
  "a read error is named as a read error" that way; S0-04's capture_leg reports a non-UTF-8 profile on the read's
  own line too (round 1's C-1 rows). T3:876 `def _profile_refusal` keeps the two existing parse-error tests on that
  one rule.
  If you read a decode error as a parse error, one move reverses it: the decode back into the parse `try` of
  C:278 `def _read_yaml`; the helper then flips.
- D-R4-3. F-2's rows are an array, a string and a number. The item named the first two; the number failed with a
  generic `malformed evidence: TypeError` line before.
- D-R4-4. The S0-01 wall time before the fix is four chunks run one after another, not one run: one run did not fit
  one call's 590 s bound. After the fix, both forms are given.
- D-R4-5. S1C's edit is line-count neutral on purpose. A first form added two lines. It moved S1C's lines, and
  `test_ck11_dead_branch_comments_cite_a_real_guard` in `tests/test_s0_01_check_acp_conformance.py` failed: lines
  1605 and 1621 of that test file cite S1C lines 1561 to 1565, which then held no guard. That file may not be
  edited, so the comment rides on the `digests[tree_name] = []` line (S1C:1058).
- D-R4-6. The harness moved one gate call to the background (its note: "did not complete within its 600s
  timeout"): T3 and five S0-01 companion files, twice each, 19:47Z to 19:58Z. I waited on its logs; every run in it
  passed (the table). No gate was backgrounded by choice.
- D-R4-7. Scratch outside the scratchpad, temporary, as in round 3's D-R3-3: the mirror `/tmp/i59f-r4-mirror`,
  private basetemps `/tmp/i59f-bt-*` and `/tmp/i59f-ps`, and T3's own `/tmp/s0-03-unreadable-*`. Each was deleted
  after use.
- D-R4-8. The report upkeep edited earlier rounds' refs (the section head). Their claims stand as written for their
  round.

Adjacent defects (reported, not fixed):
- C's credential walk calls `is_credential_name` on every mapping key. An int, a bool or a null key in the profile
  ends in `AttributeError` (`'int' object has no attribute 'upper'`), a traceback, in round 3's C and in round 4's.
- proofs/S0-05/netns_lib.sh:172 `^[1-9][0-9]{0,9}$` (the owner pid) uses ranges, against its own rule X1. It is
  outside my boundary.

### Evidence tiers (round 4)

- VERIFIED (run here, pasted above): the red and green runs; the 30 mutant rows and their baselines; the gates,
  twice each; TA's rows and the read half; the expected reds and S0-02's cause; the per-proof changed inputs; the
  dry run of every spec leg of S0-01 to S0-05; the byte identity on 11 of 11 golden manifests; the wall times;
  setpriv's options here; the static checks; the host state.
- INFERRED: the PC's setpriv takes `--clear-groups` (here, util-linux 2.39.3 does); the PC re-capture passes CE,
  because the round-4 runner writes the gid (not run here); CE is the only field reader (a grep, not a graph query).
- ASSUMED: nothing beyond the NOT-done list.
