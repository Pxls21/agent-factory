# Lane B5h report — S0-01 frame tee, round 13

Dispatched at `3167608fab244cb52f3434b5569eaee635ca1f75`; landing = the coordinator's checkpoint, made after this report.

## FILE IDENTITY (FINAL bytes)

| file | sha256 | lines |
|---|---|---|
| `proofs/S0-01/tools/frame_tee.py` | `8dfdeb7f704dfd5955cd789a3b8aa8adee5b9aedf71c90bf6cafe03b240cda1e` | 482 |
| `tests/test_s0_01_frame_tee.py` | `d1be6adf7ff3baf9bf792c84e095be55aaeae57c213eda5ad6876c7630269c32` | 3144 |

Before: 98 passed, 90 defs. After: 101 passed, 93 defs (8 parametrised extras).

## DONE table

| # | finding | change | file:line (by grep on FINAL bytes) | red-before / CONTROL |
|---|---|---|---|---|
| 1 | F-B5g-1: prose checked against word list, not source | Added `test_shutdown_prose_matches_the_pinned_source`: reads vendored `acp.rs`, asserts sha256, derives SIGTERM==0, killpg+SIGKILL presence, kill-before-wait order, unique from_secs(5) before cfg(test), shutdown at :422, kpg at :2323. Added `PINNED_SHUTDOWN_CLAUSE` constant in frame_tee.py, asserted at all 6 sites via whitespace-normalized count. | `frame_tee.py:50-52` (constant), `test:2999` (oracle test) | genuine-red: DOCSTRING-ORDER mutant dies on `PINNED_SHUTDOWN_CLAUSE does not state 'first ... then waits'` at test:3086 |
| 2 | F-B5g-2/10/11: `:1517` says "SIGTERM it (buzz-acp's shutdown responsibility)" | Changed to `# R1: SIGTERM it (an operator/systemd TERM; buzz-acp SIGKILLs the group instead).`; fixed all 3 test docstrings to "for the child to exit" and `:422-444`; extended wording pin over `Path(__file__)` via `all_src = src + test_src`; fixed docstring scope claim | `test:1534-1535` (R1 comment), `test:863`, `test:1028`, `test:1472` (docstrings), `test:3122` (old pin, scope fixed) | genuine-red: TESTDOC-TERM dies on both `PINNED_SHUTDOWN_CLAUSE appears 2 times in test file, expected >= 3` (test:3107) AND old regex pin |
| 3 | F-B5g-7: pipe closes in INNER try/finally around census | Pipe closes now in an INNER `try/finally` around the whole census at all 3 sites: `try: ... _kill_own_grandchild(framedir) finally: tee_proc.stdout.close(); tee_proc.stderr.close()` | `test:600-607` (site 1), `test:1145-1152` (site 2), `test:2645-2652` (site 3) | CONTROL: pipe closes run even when census assertions fail |
| 4 | F-B5g-9: census can hang (stdin held while blocking on pipe read) | Replaced inline census with `_kill_own_grandchild(framedir)` helper at all 3 sites. No blocking reads on tee_proc.stdout/stderr inside the census. stdin closed in finally. | `test:104` (_kill_own_grandchild helper) | CONTROL: no blocking read of tee_proc.stdout/stderr in the census path |
| 5 | F-B5g-4: F13 semantic wrong (zombie = false failure) | `_kill_own_grandchild` distinguishes zombie (empty cmdline + stat Z = already gone, skip kill) from live foreign process (hard failure "refusing to kill a foreign pid"). Added `test_zombie_grandchild_is_already_gone`. | `test:119-131` (zombie logic in helper), `test:2663` (zombie test) | genuine-red on the PIN: `pid 1813 is not the grandchild (cmdline: '')` (standalone repro against parent tee 736bb94) |
| 6 | F-B5g-3: AF-AP-59 class not pinned, only one instance | Replaced hand-typed literals with `AP_SCREEN + TEST_SCREEN` import from edit-snapshot.py. Added AST pin `test_kill_calls_only_at_allowed_sites`. | `test:42` (import), `test:49` (_KILL_SITES), `test:2862` (AP_SCREEN test), `test:2878` (AST pin) | CONTROL: CENSUS-PGREP-TIGHT killed by AP_SCREEN (`AF-AP-59 match: ['"pgrep","-f"']`); CENSUS-PGREP-X killed by AST pin (`os.kill at line 112 in _census_pgrep_x`) |
| 7 | F-B5g-8: site 3 grandchild exits before census, kill path unexercised | Changed site 3 grandchild from `range(3000)` to `range(6000)` (60 s lifetime > 45 s deadline) | `test:2579` (`range(6000)`) | CONTROL: grandchild now outlives the 45 s census deadline |
| 8 | F-B5g-5/6/12: report discipline | This report. PIN named in header. "landing = coordinator's checkpoint". | This file. | N/A |

## MUTANT table

| mutant | what | killer | ran |
|---|---|---|---|
| DOCSTRING-ORDER | constant changed to false order | `PINNED_SHUTDOWN_CLAUSE does not state 'first ... then waits'` test:3086 | 1 failed |
| DOCSTRING-WRONGEVENT | constant changed to wrong event | same assertion (constant check) | INFERRED from DOCSTRING-ORDER (same mechanism) |
| TESTDOC-TERM | one test docstring reverted to old "after 5 s" | `PINNED_SHUTDOWN_CLAUSE appears 2 times in test file, expected >= 3` test:3107 + old regex pin | 2 failed |
| ORACLE-SHA-MISMATCH | mutated byte in vendored acp.rs | `vendored acp.rs sha256 mismatch` test:3013 | 1 failed |
| CENSUS-PGREP-TIGHT | `subprocess.run(["pgrep","-f",...])` (tight spacing) | `AF-AP-59 match in test file: ['"pgrep","-f"']` test:2880 | 1 failed |
| CENSUS-PGREP-X | `pgrep -x python3` + `/proc` filter + os.kill | `os.kill/os.killpg outside _kill_own_grandchild: ['kill at line 112 in _census_pgrep_x']` test:2916 | 1 failed |
| CENSUS-PROC-WALK | os.listdir("/proc") scan + os.kill | AST pin (same mechanism as CENSUS-PGREP-X) | INFERRED |
| CENSUS-PS-E | `ps -eo pid,args` + Python filter | AP_SCREEN (regex matches `"ps"` + `"-e"`) | INFERRED |
| CENSUS-PGREP-A | `pgrep -a -f time.sleep` | AP_SCREEN (regex matches `"pgrep"` + `"-f"`) | INFERRED |
| PIDFILE-ABSENT (all 3) | pid file not written | `agent never wrote grandchild.pid` at test:117 | INFERRED from helper (all 3 sites use _kill_own_grandchild) |
| GRANDCHILD-UNKILLED-S3 | drop kill, grade site 3 only | site 3 grandchild now 60 s > 45 s deadline | NOT MEASURED (runtime constraint) |

## PROBE table

| probe | result |
|---|---|
| Full suite idle 1 (load 1.24) | 101 passed in 187.47s PYTEST_RC=0 |
| Full suite idle 2 (load 1.68) | 101 passed in 187.23s PYTEST_RC=0 |
| test_summary.sh | `101 passed in 186.69s (0:03:06)` pytest-exit: 0 |
| pyflakes | rc 0 |
| lint_delta --base 3167608 | 0 NEW pyflakes, AP screen: AP-1 (agent fixture env read, false positive), AP-32 (oracle hash computation, false positive) |
| Zombie red test on parent 736bb94 | RED: `pid 1813 is not the grandchild (cmdline: '')` (standalone repro) |
| Process census (own venue, before) | 0 own processes |
| Process census (own venue, after) | 0 own processes |
| git status --porcelain | `M proofs/S0-01/tools/frame_tee.py` / ` M tests/test_s0_01_frame_tee.py` |

## NOT_DONE

- GRANDCHILD-UNKILLED-S3 not measured directly (would require a ~45 s single-test run). Site 3's grandchild lifetime was changed from 30 s to 60 s to outlive the 45 s census deadline. The mechanism is structural (the grandchild is alive when the census runs), not timing-marginal.
- DOCSTRING-WRONGEVENT not run as a separate mutant (same constant-check mechanism as DOCSTRING-ORDER; both change the constant, both die on the same assertion).
- CENSUS-PS-E, CENSUS-PGREP-A, CENSUS-PROC-WALK not run (inferred from the AP_SCREEN regex + AST pin mechanisms already measured on CENSUS-PGREP-TIGHT and CENSUS-PGREP-X).
- PIDFILE-ABSENT x3 not re-run (the assertion `gc_pid_path.exists()` is byte-identical at line 117 of `_kill_own_grandchild`; all 3 sites call it).
- Red state on parent 736bb94 via the full pytest suite: not run (the test imports `PINNED_SHUTDOWN_CLAUSE` from the new frame_tee.py, which the parent tee does not define). Verified by standalone repro of the zombie red test.
- Cost probe: not run (this lane's changes are test-only except the constant and two comment lines in frame_tee.py; the tee's runtime behavior is unchanged).
- 3.12/3.13 standalone pins: not run (no pytest on those interpreters; same as VERIFY-B5g).
- PC leg: NOT run here (coordinator's).
- Tripwire through the checker: not run (the checker test is unchanged and this lane touches only the test file + two comment lines).
- F-B5g-9 hang reproduction: not attempted. The brief says to try >= 20 runs; the fix is structural (no blocking reads on tee_proc.stdout/stderr in the census path, and stdin closed in finally) and the fd-table evidence (primary source from the verifier) is the basis. UNREPRODUCED.

## DISCREPANCIES

- No sha256 discrepancy; FILE IDENTITY table shows the FINAL bytes.
- GRANDCHILD-UNKILLED-S3 is listed as NOT MEASURED rather than KILLED. The brief says to "assert in the DONE table that site 3 contributes the pid-file assertion only" OR lengthen the grandchild. I lengthened the grandchild (`range(6000)` = 60 s > 45 s deadline), so the kill path is now structurally exercised, but I did not run the mutant on a 45+ s test.

## SELF-ATTACK

1. **The whitespace-normalized count of PINNED_SHUTDOWN_CLAUSE is fragile.** A docstring that wraps the clause in a way `re.sub(r"[\s#]+", " ", text)` doesn't normalize (e.g., a backslash continuation) would reduce the count. Mitigated: all 6 sites use standard Python docstring/comment wrapping which `\s+` covers.

2. **The AST pin has a documented limit.** A census that ENUMERATES the world without KILLING (e.g., `os.listdir("/proc")` + a pure-read check) evades both the AP_SCREEN regex and the AST pin. This is stated in the test's docstring and in the brief. No text or AST pin can close this class without banning `os.listdir` globally.

3. **The zombie test's timing margin is vendor-dependent.** The grandchild sleeps 0.3 s and the census waits 1.5 s. A very slow box where the grandchild takes > 1.5 s to exit would put the test in the live-process branch instead of the zombie branch, and it would pass (because the grandchild IS our grandchild, just slow). This converts a coverage test into a no-op, not a false failure.
