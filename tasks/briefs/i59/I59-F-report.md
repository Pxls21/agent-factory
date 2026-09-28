> **COORDINATOR NOTE (2026-09-28 16:5xZ):** this copy is the lane's report file from the worktree `/home/user/i59-landing`, copied whole after round 3. Three local commit ids that a push rewrote are replaced by the origin commits with the same tree (370fead; e49b1a1 for two ids that shared one tree), so D-R2-1's sentence about them now names one id twice. The lane's patch of record is `tasks/briefs/i59/I59-F.patch`.

# I59-F report (task #335): the proof-code follow-ups before the owner's re-sign

Written 2026-09-28 14:4xZ by the sandbox build lane (code-implementer, Opus 5.5). Worktree `/home/user/i59-landing`,
HEAD e49b1a1 (docs-only commits past the PIN; see D1). No git write, no push, no PC bridge, no subagent.

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
- Mid-run the coordinator moved HEAD (message: 6aceec4). I measured e49b1a1; `git diff c32ac3f HEAD` over the seven
  files is empty, and `tasks/briefs/i59/` is unchanged since eab2988. No mismatch that matters.

## Per item

### 1. E-1 (S0-03): no failure message prints a value read from the profile

What changed:
- C:91 `import hashlib`. C:237 `def _shape`: `absent` for None, else `<type>, <n> characters, sha256 <8 hex>`.
- C:149 the `transport` template now takes the shape: `transport: profile api_mode ({}) is not in the permitted set`.
- C:802 `_fail("transport", _shape(api_mode))`.
- C:813 `bundle: profile.yaml x-omniroute-compression (<shape>) is not 'off'` (`_shape(value)`).
- C:821 `bundle: profile.yaml key_env (<shape>) is not 'OMNIROUTE_API_KEY'` (`_shape(block.get('key_env'))`).
- New test T3:971 `test_a_failure_names_a_profile_value_by_its_shape_never_the_value`, 4 rows from
  T3:955 `PROFILE_VALUE_PATHS`: api_mode in the model section, api_mode in the provider block, the compression header,
  key_env. T3:935 `_fake_profile_value` builds a fake value at run time: letters alternate with marks (T3:926 `_MARKS`)
  that no checker message holds, so any 4-character run found is the value itself. Each row asserts: no case-folded run
  of 4 in stdout or stderr (T3:942 `_runs_of`), the exact stdout line, stderr empty. Preconditions: no `sk-`, `bearer `
  or `basic ` prefix; the screen finds a printed value; the value reaches the file whole.
- Two existing assertions changed with the contract (they pinned the printed value):
  - T3:449 `_shape_of('codex_app_server')` in `test_conjunct_v_transport`;
  - T3:554 `_shape_of('default')` in `test_conjunct_v_requires_the_compression_header_in_the_profile`.

Red on the PIN (C at 3dbf485f, run before the C edit): `6 failed, 7 passed, 200 deselected in 5.68s`. Each E-1 row
failed on `AssertionError: a run of the profile value was printed`.
Green: `13 passed, 200 deselected in 6.10s`; then the gates below.
Mutants: M-E1a (api_mode printed with `repr`) 2 FAILED; M-E1b (the header by `{value!r}`) 1; M-E1c (key_env by
`!r`) 1; M-E1d (`_shape` hashes `b""`) 6 (the 4 rows and the 2 changed tests).

Messages in C checked for the class (a value read from `hermes/profile.yaml`):
- C:802 `_shape(api_mode)`, C:813 `_shape(value)`, C:821 `_shape(block.get('key_env'))`: printed the value. Fixed.
- C:254 `absent`, C:256 `is not a regular file`: the file name only.
- C:288 `is not valid YAML`: the class name only (I59-E).
- C:761 and C:795 `_obj(profile, "profile.yaml")`, and the providers and provider-block `_obj` reads: no value.
- C:765 `declares {len(providers)} providers`: a count.
- C:806 `provider block has no extra_headers mapping`: no value.
- C:780 and C:784 `carries an inline credential under {child_path}`: mapping KEYS and list indices, never a value.
  Left unchanged (D5).
- Every other message reads `direct.json`, `omniroute-requests.json`, `hermes/leg.json`, the environ record or the
  timeline, not the profile. For example C:457 `sent as {value!r}` quotes the header the direct probe SENT. Out of the
  class; not changed.

### 2. B-1 (S0-05): a root holding a newline is refused, exit 73, nothing written

What changed:
- R:103 `case $EVIDENCE_ROOT in *$'\n'*)`: the root as given. The message names it with `printf %q`.
- R:107 `_real=$(readlink -m -- "$EVIDENCE_ROOT" && printf x)`: a sentinel read, so a trailing newline of the
  resolved path survives the substitution.
- R:110 `case $EVIDENCE_REAL in *$'\n'*)`: the resolved path.
- New test T:4355 `test_i59f_b1_an_evidence_root_that_holds_a_newline_is_refused_before_anything_is_written`, through
  the real runner, 4 rows: the verifier's reproduction (a clone named `nlrepo<newline>`, git itself reads it as a work
  tree); a link to that clone (needs the sentinel); a path through that link (needs the resolved check); a newline
  that `..` drops (no clone: needs the given-path check). Each asserts exit 73, the exact stderr line (quoted with
  bash's own `printf %q`, T:4347 `_quoted`), empty stdout, no entry changed under tmp_path.

Red on the PIN's R (mirror): the rows fail on `assert 1 == 73` (the run went on to its checker); the 4 rows:
`4 failed, 315 deselected in 3.73s`. Green: `4 passed, 315 deselected in 1.37s`.
Mutants: X-B1-given (no given-path case) kills the dotdot row; X-B1-sentinel (`$(readlink -m …)` again) kills the
link row; X-B1-resolved (the resolved case never matches) kills the link row (message) and the through-link row
(state).

### 3. B-2 (S0-05): no mount point on the same filesystem is descended

What changed: R:615 `def mount_id` reads statx `STATX_MNT_ID` on the entry's own descriptor. R:626 `def hand` leaves
an entry whose mount id differs from the root's: `(a mount point: another mount of this filesystem)`. The comment
above `_handback() {` now says so, and why: R:587 `STATX_MNT_ID`.
Mechanism measured first: a bind mount has the root's st_dev (65024) and another mount id (49 against 28).
New test T:4485 `test_i59f_the_handback_leaves_a_mount_under_the_root_as_it_is`, row `a-bind-mount-B2`: a real leg under
sudo; the test bind-mounts a directory outside the root into the unit's HOME while the unit serves, then sends
SIGTERM. Asserts: the mount's content unchanged during the run, the outside directory and its file unchanged (still
65534:65534), exactly one `left as it is` line naming the mount point, and the summary's `1 left as they are`.
Red on the PIN's R: `AssertionError: the handback changed what the mount holds` (the outside entries became
4242:4243). Green: in the gates. Mutant X-B2 (`if mount_id(fd) != mnt:` becomes `if False:`) 1 FAILED.

### 4. B-3 (S0-05): an iterative walk; any depth; every entry left is counted

What changed: the handback program (R:597 `_handback() {` to the heredoc's end). R:639 `def enter` opens a directory
to read and pushes a frame (its path, its st_dev and inode, the names still to walk). R:666 `while stack:` holds ONE
directory open to read. It goes down through the child's O_PATH descriptor and back up through `..`. The way up must
be the directory it came down from, or the walk stops: R:680 `stopped = f"{where} moved while it ran"`, and the
summary says `then it stopped: … so what it had not reached is left as it is`.
Tests:
- T:4572 `test_i59f_b3_the_handback_hands_back_a_1100_level_tree_and_counts_what_it_leaves`, rows
  `the-venue-limit` (20000 here) and `nofile-1024` (set on the runner by `resource.setrlimit`). A real leg under sudo;
  the unit makes `deep` plus 1,099 levels of `d` (T:4542 `DEEP_TREE`) with two names of one file at the bottom. After
  SIGTERM, the census (T:4557 `_owners`, a stack: Python 3.11's `os.walk` and `shutil.rmtree` raise RecursionError at
  this depth, measured) finds every entry the invoker's except the two names, both named on stderr, and the summary
  says `<census - 2> entries … ; 2 left as they are`.
- T:4456 `test_i59f_b3_the_walk_stops_where_a_directory_moved_under_it`: R's own program, cut from R's bytes
  (T:4406 `_handback_program`), with a mover (T:4444 `MOVE_BEFORE_THE_WAY_UP`) that renames `evidence/a/b` out of the
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

What changed: R:138 `if [ "$SUDO_UID" -gt 4294967294 ] || [ "$SUDO_GID" -gt 4294967294 ]` exits 64 before
anything is written (the pattern above it bounds the digits first). In the handback: R:601 `MAX_ID = 4294967294` and a
range check that hands nothing back; `fchownat` gets `argtypes` with `ctypes.c_uint`.
Tests:
- T:4391 `test_i59f_b4_under_sudo_an_id_above_4294967294_is_refused_before_anything_is_written`: 4294967295,
  4294967296 and 4294967297, each as SUDO_UID and as SUDO_GID (6 rows), through the real runner: exit 64, the exact
  line, nothing written.
- T:4423 `test_i59f_b4_the_handback_itself_refuses_an_id_libc_would_cut`: the same three values in each position
  (6 rows) against R's own handback program (the runner refuses first, so only the cut program reaches the check).
  Asserts the refusal line and no change; then the same program with ids in range hands the tree back.
Red on the PIN's R: the runner rows fail on `assert 1 == 64`; the handback rows show the PIN handing back to the cut
id (`… now belong to 4294967295:4243`).
Mutants: X-B4-runner (the R check off) 6 FAILED; X-B4-handback (the range check off) 6 FAILED.
Measured equivalent (SURVIVED, stated): X-B4-argtypes (no `c_uint` argtypes) passes the 11 handback tests. With the
range check in place, ctypes' default int conversion masks to the same 32 bits on this ABI.

### 6. B-6 (S0-05): the other-filesystem branch is covered

Test: T:4485 `test_i59f_the_handback_leaves_a_mount_under_the_root_as_it_is`, row `a-tmpfs-B6`. A tmpfs under the root,
mounted while the unit serves: left as it is, named `(another filesystem)`, its file unchanged, counted in the summary.
It passes on the PIN's R: the branch existed and was only untested (D6). Mutant X6 (`if st.st_dev != dev:` becomes
`if False:`) FAILED: the tmpfs then falls to the mount-id check and is named `(a mount point: another mount of this
filesystem)`.

### 7. Task #331, AF-AP-234 (S0-05 tests): the signal tests start the runner at the default dispositions

What changed: T:1765 `SIGNALS_DEFAULT`, the GW@c32ac3f:316 `INT_DEFAULT` shim extended to SIGINT, SIGHUP and SIGQUIT, and it
also puts back SIGPIPE and SIGXFSZ (D3). Used by:
- T:2075 (x4), T:3097 and T:3135 (e3b_r4), T:4587 (the deep test): `SIGNALS_DEFAULT + ["bash", str(RUNNER)`;
- T:3182 `def _runner_session` (the e3r1 and i59b signal tests).
New test T:4322 `test_i59f_signal_tests_start_the_runner_with_int_hup_and_quit_at_their_defaults`: both launches first
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
- C-1: T4:1333 `test_capture_leg_reports_a_profile_read_error_on_its_own_line`, rows `missing`, `a-fifo`,
  `not-utf-8` (the oracle is this venue's own decoder).
- C-1: T4:1354 `test_capture_leg_reports_an_unreadable_profile_on_its_own_line` (mode 0000, read as uid 65534 when the suite is
  root, as itself otherwise, in a 0711 directory of its own under /tmp). Each pins the whole stderr line and asserts
  stdout empty and no output written.
- C-2: T4:1290 and T4:1320 `assert proc.stdout == ""` in the two I59-C YAML-error tests (22 items).
Red: the PIN's tool is right, so these pass on it (D6). C-X4 (the read moved inside the parse `try`) 4 FAILED;
C-X6 (the last 7 characters of the message printed to stdout) 22 FAILED.

### 9. E-2 (S0-03 tests)

What changed: T3:902 `assert result.stderr == ""` in the I59-E parse-error test (7 rows).
The new E-1 rows assert the same: T3:988 `assert result.stderr == ""`. Scope: D4.
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
  and T3 6 to 7: one new AP-32 tell each, on the display hash in C:237 `def _shape` and T3:929 `def _shape_of`. They
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
- **A-4 (INFERRED, static only).** R:312 `real=$(readlink -m -- "${file:-/nonexistent}")` (the pair identity file)
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

- D1. HEAD is e49b1a1, not the coordinator's 6aceec4: one more docs-only commit (`wiki/topics/live-state.md`). The
  seven files equal the PIN's bytes; the brief is unchanged.
- D2. The brief says "like S0-04's `_short()`". CC@c32ac3f:120 `def _short` prints the value, cut at 60 characters; it is no
  length-and-hash shape. I built the shape the brief names (type, length, sha256 prefix). A-2 is `_short`'s leak.
- D3. **Deviation: SIGNALS_DEFAULT restores five signals, not three.** The GW form hands CPython's startup ignores of
  SIGPIPE and SIGXFSZ to the runner; a runner with SIGPIPE ignored is not the runner a shell starts. Measured
  `0x1001000` through the GW form and `0x0` through mine. Needs your acceptance.
- D4. E-2's scope: `stderr == ""` went where E-X7 lands (the I59-E parse-error test, 7 rows) and into the new E-1 rows.
  The other failure tests of T3 whose failure goes to stdout (about 60) were not swept.
- D5. **Interpretation:** C:780 and C:784 `carries an inline credential under {child_path}` print mapping KEYS
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
  - R@c32ac3f:219 is now R:271, `"$UNIT_USER" =~`;
  - R@c32ac3f:252 is now R:312, `readlink -m -- "${file:-/nonexistent}"`.

## Evidence tiers

- VERIFIED (run here, pasted above): the premise; every red and green pair; the 19 mutants and the 2 equivalents; the
  gates; the signal BEFORE and AFTER; the host state; A-1, A-2, A-3.
- INFERRED: A-4; statx mount-id support on the PC; the PC root's RLIMIT_NOFILE of 1024 (the verifier's inference; the
  test sets 1024 itself).
- ASSUMED: none.

## Round 2 (the fold of A-1..A-4)

Written 2026-09-28 15:3xZ by the same lane, on the coordinator's round-2 message. Worktree HEAD 370fead (D-R2-1).
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
- R:257 comment and R:264 `if [ -n "$UNIT_USER" ] && { ! [[ "$UNIT_USER" =~ ^([1-9][0-9]{0,9}):([1-9][0-9]{0,9})$ ]]`
  with both ids `-gt 4294967294` refused: exit 64 before anything is written and before any unit launches.
- The resolved default keeps the old shape check and A4's not-run row; T:2273's `default-owner` row still passes.
- R:774 `"$UNIT_UID" -eq 0` (numeric) and R:521 `uid[0] != int(want_uid)` (the post-launch compare, numeric).
- T:2273 `["default-owner"]` drops the `explicit` row: its not-run assertion no longer applies. The new `0:0` row covers it; the
  docstring says so.

Tests:
- T:4628 `test_i59f_a1_an_explicit_unit_user_outside_1_to_4294967294_is_refused_before_any_unit_runs`, the 10 rows
  of T:4619 `BAD_UNIT_USERS`, through the real runner with a listener, so a leg past the check would reach its
  launch. Each asserts exit 64, T:4621 `UNIT_USER_REFUSED` as stderr's last line, no stdout, no evidence root, no
  stand-in record, no namespace.
- T:4650 `test_i59f_a1_a_unit_user_in_range_proceeds`: 65534:65534 passes, and the unit's own record says
  65534:65534. It is then stopped with SIGTERM (143).

Red on the current bytes: three rows ran on (`assert 1 == 64`). At 4294967296:4294967296 the stand-in recorded
`'uid': 0`. Coreutils refused the scratch-tree chown (`chown: invalid user`), but the writability probe ran as root
and passed; A7 refused only after the launch (`unit identity not observed: uid 0`). The other seven rows already
exited 64 and failed only on the new message.
Mutants: X-A1-range (2 FAILED), X-A1-zero (1), X-A1-lead (3), X-A1-all (the positive control, 1).
Measured equivalents: R:774 `-eq 0` back to `= 0` (`12 passed`) and the A7 compare back to strings (`19 passed`). The check
above them admits only canonical decimals now.

### A-2 (S0-04): no CC message prints a value of the provider block

What changed:
- CC:49 `import hashlib`. CC:131 `def _shape`, in the format of C's (`absent`, or `<type>, <n> characters, sha256 <8 hex>`).
- CC:355 `config-header-value: {_shape(hits[0][1])}`, CC:358 `base-url-unexpected: {_shape(base_url)}`,
  CC:361 `key-env-not-a-name: {_shape(key_env)}`, and the observation printed `api_mode = {_shape(api_mode)}`
  (round 2; round 3's route B changed that line again, see "Item 1, route B").

Every CC message that reads the provider block (`hermes-provider.json`, CC:341 `_read_json`), with its disposition:

| line | message | disposition |
|---|---|---|
| CC:341 | absent, not regular, too large, not JSON, NaN (`_read_json`) | no value; unchanged |
| CC:345 | `unexpected-provider-fields` | field names (keys); unchanged |
| CC:348, CC:351 | `config-header-absent` | no value; unchanged |
| CC:353 | `config-header-duplicated` | a count; unchanged |
| CC:355, CC:358, CC:361 | header value, base_url, key_env | printed the value; now `_shape` |
| CC:364 | `api-mode-absent` | no value; unchanged |
| CC:370 | the api_mode observation | printed the value; round 2: `_shape`; route B: a known mode by its name, any other value by `_shape` |

CC:275-336's `_short` uses read the request legs' records, not the profile or config: outside the class.

Tests:
- T4:779 `test_a_message_names_a_config_value_by_its_shape_never_the_value`: the 4 rows of
  T4:763 `CONFIG_VALUE_PATHS`. They mirror T3:971 `test_a_failure_names_a_profile_value_by_its_shape_never_the_value`.
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
- It proves the loss at R:312 `real=$(readlink -m -- "${file:-/nonexistent}")`.
- It cannot be a bypass: a stripped trailing newline keeps a path under `.secrets/` inside the prefix
  `"${PIN[BASE]}/.secrets/"*`. The defect is fail-closed: a false refusal under a wrong name.

What changed:
- R:164-182, the comment and the early refusal: exit 73 with `printf '%q'`, before anything is written:
  - R:170 `case $PAIR_IDENTITY in *$'\n'*)` (the given path);
  - R:174 `if _id_real=$(readlink -m -- "$PAIR_IDENTITY" && printf x)` (the sentinel read);
  - R:176 `case $_id_real in *$'\n'*)` (the resolved path).
- A path readlink cannot resolve is left to `_pair_identity`, as before.
- R:307-308: the comment above R:309 `_pair_identity() {` says `No newline` reaches the path now.

Test: T:4682 `test_i59f_a4_a_pair_identity_path_that_holds_a_newline_is_refused_before_anything_is_written`, 4 rows:
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
   - the `S0_05_UNIT_USER` check at R:264-269, cut from R with sed and run in bash on 14 values during the upkeep:
     `1000:1000` and `4294967294:4294967294` admitted, and `1:1`; exit 64 for a trailing or a leading newline,
     4294967295 in either place, a space at either end, 0 in either place, `+1:1`, `1:1:1` and an 11-digit id.
   Left open: A7 records no `Gid:` line, so the real run's gid is inferred; the PC run is not run here.
2. **A-2's leak test is blind, or a CC message that reads the provider block was missed.** Ruled out: each mutant
   that puts `_short` back (X-A2-header, X-A2-url, X-A2-key, X-A2-obs) reds its own row, and X-A2-hash reds 6.
   The table above lists every message in CC:341-370 (route B's bytes), where `_shape` prints each value but a
   known mode in the observation. Left open: the table
   comes from a read of CC, not from a tool.
3. **A-4's refusal fires on a path with no newline, or the sentinel read changes what `_pair_identity` reads.**
   Ruled out: T `333 passed` twice, with T:2302 `test_a6_identity_file_refusals` and the other earlier identity
   tests in it; `_id_real` is read only inside the early block, and
   R:312 `real=$(readlink -m -- "${file:-/nonexistent}")` is unchanged; each X-A4 mutant reds.

### Discrepancies (round 2)

- D-R2-1. HEAD is 370fead: the old e49b1a1 reads e49b1a1 after a push, plus two doc commits. `git diff c32ac3f HEAD`
  over the ten boundary files is empty.
- D-R2-2. **The S0-04 observation now prints the api_mode's shape**, following "every CC message". T4's observation
  pin changed with it. The checker's output no longer names the mode behind the owner's open decision (task #35).
  If the name matters, an allow-list of the known mode names is the alternative. I did not build it: it would
  deviate from the item.
- D-R2-3. A-1's rule covers the explicit `S0_05_UNIT_USER` only, as written. A default resolved from a pinned agent
  owned by `<uid>:0` still gives gid 0 (F11's residual).
- D-R2-4. A-4's refusal is global, as B-1's is: a newline in `S0_05_PAIR_IDENTITY` refuses the whole run (exit 73)
  even when `buzz-acp` is not in the unit list.
- D-R2-5. "The post-launch root check compares numerically": I made both numeric, R:521 `int(want_uid)` (A7,
  post-launch) and R:774 `-eq 0` (A4, pre-launch). Both are measured equivalents now.
- D-R2-6. Not asked, left as it is: R:317 compares the identity file's owner with `"$UNIT_UID"` as strings. Both
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

Written 2026-09-28 16:3xZ by the same lane, on the coordinator's round-3 message. Worktree HEAD 370fead.
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
- CE does not grade the new gid: CE:407 `if 0 in uid` grades the uid only. Not asked; CE is outside my boundary.
- A resolved uid 0 with a group other than 0 keeps A4's per-unit row (`not-run|unit would run as root`), not exit 64.
  The item names gid 0 only.
- No re-mint; no commit. The committed evidence and the fixtures are untouched.
- Not run: the PC, real CI.

### Item 1 (D-R2-2): stopped, with the evidence

- CC has no permitted set for api_mode: CC:342 `allowed` holds field names. C's set is
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
- R:274-280: after the resolution and its shape check, `if [ -n "$UNIT_USER" ] && [ "${UNIT_USER##*:}" -eq 0 ]`
  exits 64 before anything is written and before any unit launches. The message is T:4724 `DEFAULT_GID0_REFUSED`:
  `the unit user resolved from the pinned agent's owner, '<uid>:0', has gid 0 (the root group): set S0_05_UNIT_USER
  to <uid>:<gid>, each id from 1 to 4294967294`. An explicit gid 0 is refused earlier (round 2), so only a resolved
  one reaches this branch.
- R:262-263: the round-2 comment now says a resolved uid 0 keeps A4's row and `its gid 0 is refused after the resolution`.
- The order matters: a resolved 0:0 now exits 64 here, where it was A4's row. So T:2282 (`os.chown`) moves the
  `default-owner` agent to 0:65534, and A4's uid-0 row stays reachable and tested.

Tests, through the real runner:
- T:4730 `test_i59f_r3_a_default_unit_user_with_gid_0_is_refused_before_any_unit_runs`, the rows of
  T:4723 `DEFAULT_GID0_OWNERS` (65534:0 and 0:0): no `S0_05_UNIT_USER`, the stand-in chowned to the row, a
  listener up.
  Each asserts exit 64, the message as stderr's last line, no stdout, no evidence root, no unit record, no namespace.
- Positive controls: T:2226 `test_a2_s0_01_tree_change_fails_the_leg` (a default resolved to 65534:65534 runs, and the
  stand-in records 65534:65534) and T:4650 `test_i59f_a1_a_unit_user_in_range_proceeds` (an explicit 65534:65534).

Red on the round-2 runner: the `65534:0` row launched a unit (`assert 1 == 64`, a stand-in record present). The `0:0`
row got A4's row (`SKIP hermes-acp: unit would run as root`, `assert 1 == 64`).
Mutants: X-R3-default-never (2 FAILED). Under it, the `65534:0` leg launched and round 3's A7 refused it only after
the launch: `SKIP hermes-acp: unit identity not observed: gid 0`. X-R3-default-all (the positive controls, 2).

### Item 2b (VERIFY-E3 F11's other half): A7 records the Gid line and compares it as numbers

What changed:
- R:491 passes `"$UNIT_GID"` after `"$UNIT_UID"`; R:493 `want_gid, out = sys.argv[1:11]`.
- R:505-507: the status file is read once, and the Gid line beside the Uid line (`l.startswith("Gid:")`).
- R:515: the record carries `"gid": gid` beside `"uid": uid`.
- R:522 `problems += ["gid 0"] if 0 in gid else ([f"gid {gid[0]} is not {want_gid}"] if gid[0] != int(want_gid) else [])`,
  in the uid line's form.
- R:487-489: the comment above `_unit_identity() {` says so (`Its Uid and Gid` lines).

Tests:
- T:1324, in T:1207 `test_runner_live_leg`: the whole-record pin now holds `"gid": [UNIT_USER[1]] * 4`. This is the
  positive control through the real runner (65534:65534); the leg runs.
- T:2343 `test_a7_a_unit_not_matching_the_pins_is_not_observed`: a setpriv that drops nothing now shows
  T:2367-2370 `; uid 0; gid 0`, and the record's gid is `[0, 0, 0, 0]`.
- T:2624 `test_d_pair_leg_reaches_the_relay_through_the_dnat`: the binary unit's record carries
  T:2692-2693 `identity["gid"]` too.
- T:4753 `test_i59f_r3_a7_refuses_a_unit_whose_gid_is_not_the_wanted_gid`: a PATH setpriv shim runs the real setpriv
  with `--regid=65532` in place of the asked 65533 (T:4762). The unit user is 65534:65533, so uid and gid differ. The
  row is `not-run|unit identity not observed: gid 65532 is not 65533`, the record holds uid `[65534] * 4` and gid
  `[65532] * 4`, and no canary runs.

Red on the round-2 runner: the live leg's record lacked `{'gid': [65534, 65534, 65534, 65534]}`; the A7 reason lacked
`; gid 0`; the pair test raised `KeyError: 'gid'`. The shim test first raised `KeyError: 'reason'`. I then made its
row read `row.get("reason")` (T:4772), and the red re-run read `assert ('run', None) == ('not-run', '...is not 65533')`:
the leg ran with the wrong gid and its canaries ran. That re-run: `2 failed in 76.91s (0:01:16)`, with the `65534:0` row.
Mutants: X-R3-a7-no-record (2), X-R3-a7-no-zero (1), X-R3-a7-no-compare (1), X-R3-a7-want-uid (1, `gid 65532 is not
65534`), X-R3-a7-uid-line (1, `gid 65534 is not 65533`), X-R3-a7-all (the positive control, 1).

### unit-identity.json: every reader still reads the new record

- `grep -rn 'unit-identity'` over the tree finds one reader of the record's fields: CE:375 `def check_unit_identity`.
  It asks only that CE:111 `IDENTITY_KEYS` be present (CE:392, `any(key not in record for key in IDENTITY_KEYS)`) and
  ignores any other key. So the committed records (no gid) and the new ones (a gid) grade alike.
- The validator only hashes the files for the attestation; it reads no field. The graft indexes name the function.
- T:4782 `test_i59f_r3_the_checker_reads_an_identity_record_that_carries_the_gid`: the synthetic-pass bundle with a
  Gid line added passes and prints the same identity line. Its negative control, X-R3-checker-strict (CE's key test
  made exact, in the mirror only), reds it.
- The other readers are tests. T:1321, T:2368 and T:2690 read the runner's `unit-identity.json`, updated above.
  T:792, T:2219, T:2393, T:2419 and T:2443 read or patch copies of a committed `unit-identity.json`;
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
  - T: 37 to 38. The new tell is AF-AP-115 on T:4763's `shutil.which("setpriv")`. It is a false positive: the shim
    needs the real setpriv's path, resolved before the test changes PATH. It is a test fault, not a verifier's trust
    anchor.
  - With `--tests` (TEST_SCREEN, not run in rounds 1 and 2), T goes from 30 to 31. The new tell is AP-66 on round 1's
    mover line, T:4451 `_os.open = _open_after_a_move`, not a round-3 line.
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
   65534:65534 runs (T:2226 `test_a2_s0_01_tree_change_fails_the_leg`, twice in the gates). Left open: the PC's
   pinned agent owner is inferred, not read here.
2. **A7's gid compare refuses a legitimate unit.** Supplementary groups or a partial setgid could make the four gids
   differ. Ruled out here: the live leg (T:1324) and the pair leg (T:2693) record `[UNIT_USER[1]] * 4` and run, in
   both T gates. A7 compares the real gid and refuses a 0 in any of the four, as the uid line does. Left open: the
   PC's setpriv is not run here.
3. **The new record breaks a reader.** Ruled out: the one field reader (CE:392 `IDENTITY_KEYS`, a subset test),
   T:4782 `test_i59f_r3_the_checker_reads_an_identity_record_that_carries_the_gid` with its
   negative control, and the unchanged committed files and fixtures in both T gates.

### Discrepancies (round 3)

- D-R3-1. **Item 1 stopped** (above). Route A or route B is your call.
- D-R3-2. **A resolved 0:0 now exits 64**, where it was A4's per-unit row. T:2282 moved its fixture to `0, 65534` to
  keep that row tested. A resolved uid 0 with a non-zero gid is still A4's row, not exit 64.
- D-R3-3. **Scratch outside the scratchpad, temporary, as in round 1's D7.** The mirror sat in `/tmp/i59f-r3-mirror`
  (772 KB, mode 0755), because the units run as uid 65534 and `/tmp/claude-0` is 0700. It was deleted after its log
  was read.
- D-R3-4. CE does not grade the gid (NOT-done); the runner's A7 does. A record with no gid still passes CE, as before.
- D-R3-5. The shim test's gids (T:4762 `--regid=65532`, and 65533) have no group entries. setpriv takes numeric
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
- CC:73-77: `KNOWN_API_MODES = frozenset({"chat_completions", "codex_responses"})`. Its comment names the source
  (S0-03's `PERMITTED_API_MODES`) and the T4 pin.
- CC:368-370: the observation prints `api_mode if api_mode in KNOWN_API_MODES else _shape(api_mode)`. Membership is
  exact: no case fold, no strip.
- CC:355, CC:358 and CC:361, the three failure messages, are unchanged: each still calls `_shape`.

Tests (T4):
- T4:831 `test_the_known_api_modes_are_a_copy_of_s0_03s_permitted_set`: it loads CC and reads C's set as data, through
  T4:810 `_s0_03_permitted_api_modes` (`ast.parse`, then T4:818 `ast.literal_eval`; C is never imported or run). It
  asserts that CC's `KNOWN_API_MODES` is a frozenset equal to C's set.
- T4:843 `test_a_known_api_mode_is_observed_by_its_name`, rows `chat_completions` and `codex_responses`. Each row
  first asserts its mode is in C's set. Then: exit 0, the exact T4:807 `OBSERVATION` line with the name, and no shape
  of the name in the output.
- T4:98: the pass bundle's pin is the exact line with the name again: `OBSERVATION.format("chat_completions")`.
- T4:854 `test_a_value_near_a_known_api_mode_is_observed_by_its_shape`, rows `case` (Chat_Completions) and
  `trailing-space` (chat_completions plus a space): the exact line with the shape.
- The unknown fake value is round 2's row T4:771 `"api-mode-observation"` of
  T4:779 `test_a_message_names_a_config_value_by_its_shape_never_the_value`. A fake built at run time prints only its
  shape, and no case-folded run of 4 of its characters reaches stdout or stderr. It is unchanged and passes.
- T4:870 `test_a_failure_prints_a_known_mode_name_by_its_shape`, rows of T4:862 `FAILURE_FIELDS`:
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
HEAD: CC 0 to 1 and T4 4 to 5, the same AP-32 display-hash tells as round 2 (CC:138 is `_shape`'s `digest` line,
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
- D-B-2. **Adjacent, not fixed:** CC:366-367's comment still calls task #35 the `owner's open decision`. The ledger
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
