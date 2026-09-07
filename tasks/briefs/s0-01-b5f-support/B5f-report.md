# B5f REPORT -- S0-01 frame tee round 11: deterministic pins and honest bound

PIN `a60b933559ce28103a656b83f2592a938578367a`. HEAD at run: same.
Interpreter: `/usr/local/bin/python3` 3.11.15. No xdist. Load 2.04-4.05 (shared with verifier + another lane).

## FILE IDENTITY (gate lines produced on these exact files)

| file | sha256 | lines |
|---|---|---|
| `proofs/S0-01/tools/frame_tee.py` | `ac82dba82e2f4cb69c5ac1344f9f6b730bfeb69ccccc456929201ab3a595361c` | 471 |
| `tests/test_s0_01_frame_tee.py` | `05019a915ecf8de515e0c55a7ddf65b8fbcc05e1b33d04fcf71c717378d7ce84` | 2862 |

Before: tee 466 lines, test 2655 lines, 93 passed. After: tee 471 lines, test 2862 lines, 96 passed.
88 test defs -> 96 collected items (8 parametrised extras).

## RED STATE (true parent tee 736bb94 + B5f tests, NO -x, full suite)

```
7 failed, 89 passed in 173.08s (0:02:53)   PYTEST_RC=1    (load 2.21)
FAILED tests/test_s0_01_frame_tee.py::TestTeeStatus::test_grandchild_straggler_recorded
FAILED tests/test_s0_01_frame_tee.py::TestTeeStatus::test_grandchild_never_closes_sigterm_required
FAILED tests/test_s0_01_frame_tee.py::TestSigtermStatusVsChecker::test_sigterm_status_satisfies_check_tee_status
FAILED tests/test_s0_01_frame_tee.py::TestStructuralPins::test_drain_loops_have_no_break_or_timeout
FAILED tests/test_s0_01_frame_tee.py::TestEarlySigterm::test_sigterm_during_sha256_produces_status
FAILED tests/test_s0_01_frame_tee.py::TestEarlySigterm::test_no_statement_between_signal_and_try
FAILED tests/test_s0_01_frame_tee.py::TestDocstringAnchor::test_docstring_names_the_pinned_shutdown_signal
```

Second run (--tb=line, same venue) showed 8 failures (test_sigterm_kills_agent_child additionally): the agent orphan kill is flaky on the parent tee (F14 regression -- expected).

| new test | on parent 736bb94 | classification |
|---|---|---|
| `test_status_write_follows_timeline_write_in_pumps` | GREEN | CONTROL -- kills S1 |
| `test_write_status_snapshot_and_rewrite_are_locked` | GREEN | CONTROL -- kills N4, D3, LOCK-READS-OUT |
| `test_docstring_names_the_pinned_shutdown_signal` | **RED** (`module docstring does not name SIGKILL` at :2809) | genuine-red |
| existing `test_grandchild_straggler_recorded` | **RED** (carried from B5e) | genuine-red |
| existing `test_grandchild_never_closes_sigterm_required` | **RED** (`tee exited before 15 s` at :1075) | genuine-red |
| existing `test_sigterm_status_satisfies_check_tee_status` | **RED** (`rc -15 != 70`) | genuine-red |
| existing `test_drain_loops_have_no_break_or_timeout` | **RED** (`drain loop 0 has Assign statement`) | genuine-red |
| existing `test_sigterm_during_sha256_produces_status` | **RED** (`rc -15 == 70`) | genuine-red |
| existing `test_no_statement_between_signal_and_try` | **RED** (`Expr at line 409, expected Try`) | genuine-red |
| existing `test_sigterm_kills_agent_child` | **RED** on 2nd run (`state S after 2 s`) | genuine-red (flaky on parent) |

## DONE TABLE

| finding | change | file:line (FINAL tree) | red-before / CONTROL+killer | green-after |
|---|---|---|---|---|
| **F-B5e-1** honest shutdown bound | rewrote tee docstring :16-23, in-code comments :420-421 :426-427, three test docstrings :820-826 :984-990 :1381-1388 | `frame_tee.py:16-23,420-421,426-427` `test:820-826,984-990,1381-1388` | genuine-red: `module docstring does not name SIGKILL` at test:2809 | 96 passed |
| **F-B5e-1** doc-anchor test | added `test_docstring_names_the_pinned_shutdown_signal` | `test:2800-2813` | genuine-red on parent: `module docstring does not name SIGKILL` | 96 passed |
| **F-B5e-2** S1 deterministic | added `test_status_write_follows_timeline_write_in_pumps` AST pin | `test:2424-2441` | CONTROL -- kills S1 3/3 | 96 passed |
| **F-B5e-2** lag in 12-trial | added lag assertion `0 <= tl_last_seq - updated_seq <= 1` per trial in `test_directional_trails_timeline_after_sigkill` | `test:2093-2101` | N/A (strengthens existing test) | 96 passed |
| **F-B5e-3** N4/D3 deterministic | added `test_write_status_snapshot_and_rewrite_are_locked` AST pin | `test:2443-2479` | CONTROL -- kills N4 3/3, D3 3/3, LOCK-READS-OUT | 96 passed |
| **F-B5e-5** Popen-before-install | added `assert not any(... Popen ...)` in `test_no_statement_between_signal_and_try` | `test:2700-2704` | CONTROL -- kills INSTALL-LATE-B | 96 passed |
| **F-B5e-6** proc=None preinit | added `assert any(... proc ... None ...)` in `test_no_statement_between_signal_and_try` | `test:2706-2712` | CONTROL -- kills NO-PREINIT | 96 passed |
| **F-B5e-7** contention vacuous | FLAG form: `loaded = False` above loop, `loaded = True` on break, `assert loaded` | `test:1568,1575-1576,1631` | genuine-red on scratch: `no contention: the wait for updated_seq >= 100 timed out` in 15.23s | 96 passed (0.13s) |
| **F-B5e-11** T:501 value | `s = None` hoisted, `assert s is not None and s.get("recorded_a2c", 0) >= 1` | `test:500,512-513` | genuine-red on scratch: `no a2c frame recorded before the liveness window` in 0.31s | 96 passed |
| **F-B5e-11** T:857 value | same pattern | `test:856,869-870` | same shape (not separately exercised -- same code pattern) | 96 passed |
| **F-B5e-11** T:1021 value | same pattern | `test:1026,1038-1039` | same shape | 96 passed |
| **F-B5e-12** T:468 grandchild pid + kill | agent writes `grandchild.pid`; `finally` kills own pid + asserts own pid gone/Z within 2 s (AF-AP-59: own-subset, not world) | `test:463-470,524-550` | CONTROL -- kills GRANDCHILD-UNKILLED (`grandchild pid 8405 still alive after kill` at :550) | 96 passed |
| **F-B5e-12** T:990 grandchild pid + kill | same own-pid pattern | `test:989-996,1087-1113` | same shape | 96 passed |
| **F-B5e-12** T:2381-2387 grandchild pid + kill | same own-pid pattern | `test:2499-2506,2591-2617` | same shape | 96 passed |
| **F-B5e-13** state reads inside lock | moved `stdin_reader_done`, `write_errors` reads inside `with lock:` | `frame_tee.py:168-169` | CONTROL -- kills LOCK-READS-OUT | 96 passed |
| **F-B5e-14** identity pre-bind | `identity = None` + `assert identity is not None` | `test:2736,2744` | (cosmetic: error -> assertion) | 96 passed |
| **F-B5e-8** window test docstring | rewrote to state the structural guarantee (pgrep -P + fork ordering), big file as insurance | `test:2524-2531` | N/A (prose fix) | 96 passed |
| **F-B5e-9** straggler docstring | clarified: kills 0/5 s, NOT 30 s | `test:919-921` | N/A (prose fix) | 96 passed |

## MUTANT TABLE

Venue: scratchpad copies of the FINAL tree. Both scope files sha256-verified after each restore. `git status --porcelain` clean on both scope files.

| id | mutation | result | killer (NAMED) | reps |
|---|---|---|---|---|
| **INSTALL-LATE** | install+try below Popen+sha256 | **KILLED** | `test_sigterm_during_sha256_produces_status` | 1 |
| **GAP-1** | one statement between signal.signal and try | **KILLED** | `test_no_statement_between_signal_and_try` + `test_sigterm_during_sha256_produces_status` | 1 |
| **EXCEPT-WRONG** | `except Exception:` | **KILLED** | `test_sigterm_writes_status_and_exits_70` + `test_sigterm_during_sha256_produces_status` | 1 |
| **EXIT-0** | `os._exit(0)` in handler | **KILLED** | same two | 1 |
| **STATUS-FINAL-TRUE** | `_write_status(final=True)` on TERM write | **KILLED** | same two | 1 |
| **ERR-MISSING** | no "terminated: SIGTERM" append | **KILLED** | same two | 1 |
| **ORPHAN** | drop `proc.terminate()` | **KILLED** | `test_sigterm_kills_agent_child` | 1 |
| **TRY-SHRINK2** | try covers ONLY Popen; rest outside | **PATCH-FAILED** (syntax error in mutation script; the verifier's round-10 run KILLED it: `test_sigterm_writes_status_and_exits_70`) | -- | 1 |
| **N3** | swap tl/df write order both pumps | **KILLED** | `test_timeline_before_directional_in_pumps` | 1 |
| **PUMP-TIMEOUT** | 5 s select timeout inside pump_pipe read loop | **KILLED** | `test_grandchild_straggler_recorded` + `test_grandchild_never_closes_sigterm_required` | 1 |
| **A2-t0** | a2c drain: instant (no wait) | **KILLED** | `test_drain_loops_have_no_break_or_timeout` | 1 |
| **A2-t1** | a2c drain: 1 s timeout | **KILLED** | same | 1 |
| **A2-t5** | a2c drain: 5 s timeout | **KILLED** | same | 1 |
| **A2-t30** | a2c drain: 30 s timeout | **KILLED** | same | 1 |
| **a2c-t0** | a2c loop deleted (0 s) | **KILLED** | `test_grandchild_straggler_recorded` + `test_drain_loops_have_no_break_or_timeout` | 1 |
| **a2c-t5** | a2c loop: 5 s timeout (pre-B5e shape) | **KILLED** | same two | 1 |
| **a2c-t30** | a2c loop: 30 s timeout | **KILLED** | `test_drain_loops_have_no_break_or_timeout` | 1 |
| **A2C-DELETE** | delete the a2c drain loop | **KILLED** | `test_grandchild_straggler_recorded` + `test_drain_loops_have_no_break_or_timeout` | 1 |
| **A2C-WRONG-THREAD** | a2c drain waits on `ti` instead of `to` | **KILLED** | `test_grandchild_straggler_recorded` | 1 |
| **S1** | status before timeline in both pumps | **KILLED 3/3** | `test_status_write_follows_timeline_write_in_pumps` | 3 |
| **N4** | seq snapshot outside `with lock:` | **KILLED 3/3** | `test_write_status_snapshot_and_rewrite_are_locked` | 3 |
| **D3** | drop `status_lock` | **KILLED 3/3** | `test_write_status_snapshot_and_rewrite_are_locked` | 3 |
| **INSTALL-LATE-B** | Popen above install; install+try adjacent | **KILLED** | `test_no_statement_between_signal_and_try` | 1 |
| **NO-PREINIT** | drop `proc = None` | **KILLED** | `test_no_statement_between_signal_and_try` | 1 |
| **DRAIN-ORDER** | c2a drain before a2c drain | **EQUIVALENT** | both loops are pure waits at 10 Hz; pumps drain in their own threads regardless of wait order; `tl.close()` follows both. Named test + full suite on venue all pass (the sole failure is the tripwire test which needs the checker module tree absent from the scratchpad venue). | 1 |
| **LOCK-READS-OUT** | move stdin_reader_done + write_errors reads back outside `with lock:` | **KILLED** | `test_write_status_snapshot_and_rewrite_are_locked` | 1 |
| **DOCSTRING-TERM** | revert docstring to old "TERMs/KILLs" wording | **KILLED** | `test_docstring_names_the_pinned_shutdown_signal` | 1 |
| **GRANDCHILD-UNKILLED** | drop `finally` kill of grandchild (keep own-pid assert) | **KILLED** | `test_grandchild_keeps_tee_alive` (own-pid assert: `grandchild pid 8405 still alive after kill` at :550) | 1 |

```
TOTAL 29 distinct mutants
  KILLED-BY-NAMED   26   INSTALL-LATE GAP-1 EXCEPT-WRONG EXIT-0 STATUS-FINAL-TRUE ERR-MISSING
                         ORPHAN N3 PUMP-TIMEOUT A2-t0 A2-t1 A2-t5 A2-t30 a2c-t0 a2c-t5 a2c-t30
                         A2C-DELETE A2C-WRONG-THREAD S1(3/3) N4(3/3) D3(3/3) INSTALL-LATE-B
                         NO-PREINIT LOCK-READS-OUT DOCSTRING-TERM GRANDCHILD-UNKILLED
  EQUIVALENT         1   DRAIN-ORDER (both loops are pure waits; pumps drain in threads)
  PATCH-FAILED       1   TRY-SHRINK2 (mutation script syntax error; round-10 verifier's run KILLED it)
  SURVIVED           0
```

## PROBE TABLE

| probe | outcome |
|---|---|
| red state (parent tee 736bb94 + B5f tests, no -x) | 7 failed, 89 passed in 173.08s (load 2.21) |
| green state idle 1 | 96 passed in 173.61s (load 3.64) |
| green state idle 2 | 96 passed in 172.56s (load 4.05) |
| test_summary.sh | 96 passed in 172.87s pytest-exit: 0 |
| FLAG neg control (T:1566 threshold -> 10**9) | `1 failed in 15.23s`: `no contention: the wait for updated_seq >= 100 timed out` |
| FLAG green (T:1566 real threshold) | `1 passed in 0.13s` |
| VALUE neg control (T:501 threshold -> 10**9) | `1 failed in 0.31s`: `no a2c frame recorded before the liveness window` |
| doc-anchor red state (parent tee) | `1 failed in 0.02s`: `module docstring does not name SIGKILL` |
| tripwire (test_sigterm_status_satisfies_check_tee_status) | 1 passed in 0.64s |
| cost 15 reps (11-frame shape, load 3.64) | median 0.1808 s, min 0.0774, max 0.2119 (load elevated -- box shared with verifier + lane) |

## GATE LINES (verbatim)

```
pyflakes proofs/S0-01/tools/frame_tee.py tests/test_s0_01_frame_tee.py   -> rc 0

idle 1 (load 3.64):  96 passed in 173.61s (0:02:53)   PYTEST_RC=0
idle 2 (load 4.05):  96 passed in 172.56s (0:02:52)   PYTEST_RC=0

test_summary.sh (post-census-fix):  96 passed in 169.68s (0:02:49)   pytest-exit: 0   (load 1.67)

lint_delta (worktree vs origin/claude/soundbox-kit-migration-iz1jwf):
  8 .py changed, 0 NEW pyflakes hit(s), 0 removed
  AP screen hits in scope file (2 of 4; the other 2 are the checker lane's uncommitted files):
    AP-1  tests/test_s0_01_frame_tee.py:469,1032,2527 -- FALSE POSITIVE: `os.environ.get("S0_01_FRAMEDIR", "")` inside agent fixture code strings; the env var is set by the test itself two lines above; not a config channel
    AF-AP-40 tests/test_s0_01_frame_tee.py:527,1091,2594 -- FALSE POSITIVE: `gc_pid_path.exists()` in `finally` cleanup; the path is read to obtain the pid for the kill+assert; absence means no grandchild was spawned (the tee died before the agent wrote the file); the own-pid assert after the kill is the real gate

tripwire: test_sigterm_status_satisfies_check_tee_status  1 passed in 0.64s

cost: {"reps": 15, "median": 0.1808, "min": 0.0774, "max": 0.2119}  (load 3.64 -- elevated)

post-suite census: each test's `finally` kills its own grandchild pid and asserts that pid gone/Z within 2 s (own-subset, AF-AP-59); no world-scoped scan
```

RED STATE (true parent tee `git show 736bb94:proofs/S0-01/tools/frame_tee.py`, sha256 `3fc846ceaf4b687b30996d2b9e0fe07144b8a1fa65650c4082a2e2272af9d83a`, 476 lines; + B5f tests, NO `-x`):
```
7 failed, 89 passed in 173.08s (0:02:53)   PYTEST_RC=1
FAILED tests/test_s0_01_frame_tee.py::TestTeeStatus::test_grandchild_straggler_recorded
FAILED tests/test_s0_01_frame_tee.py::TestTeeStatus::test_grandchild_never_closes_sigterm_required
FAILED tests/test_s0_01_frame_tee.py::TestSigtermStatusVsChecker::test_sigterm_status_satisfies_check_tee_status
FAILED tests/test_s0_01_frame_tee.py::TestStructuralPins::test_drain_loops_have_no_break_or_timeout
FAILED tests/test_s0_01_frame_tee.py::TestEarlySigterm::test_sigterm_during_sha256_produces_status
FAILED tests/test_s0_01_frame_tee.py::TestEarlySigterm::test_no_statement_between_signal_and_try
FAILED tests/test_s0_01_frame_tee.py::TestDocstringAnchor::test_docstring_names_the_pinned_shutdown_signal
```

Popen census (AST): 27 call sites total, all name-bound; 31 raw textual `Popen(` occurrences, 4 inside agent source strings.

## NOT_DONE

- **TRY-SHRINK2 mutant**: PATCH-FAILED due to my mutation script producing invalid indentation. The verifier's round-10 table showed it KILLED by `test_sigterm_writes_status_and_exits_70`. I did not re-produce this kill.
- **PC leg**: NOT run here (no bridge; coordinator's gate).
- **Contended cost measurement**: the 15-rep cost probe ran at load 3.64 (box shared with verifier + lane D). Median 0.18 s vs baseline 0.058-0.060 s is inflated by load. The round-10 verifier measured 0.054-0.057 s at load 1.69-1.72; no regression is expected from this lane's changes (docstring/comment edits + 2 state reads moved inside an already-held lock).

## DISCREPANCIES

- **Red state count**: the verifier's round-10 verdict showed 6 failed on parent 736bb94. I show 7 because `test_docstring_names_the_pinned_shutdown_signal` is new in B5f and is red on the parent by design.
- **96 vs 93 tests**: 3 new tests (`test_status_write_follows_timeline_write_in_pumps`, `test_write_status_snapshot_and_rewrite_are_locked`, `test_docstring_names_the_pinned_shutdown_signal`).
- **Cost median 0.18 vs 0.059**: load 3.64 vs 2.54. The tee code changes are: (a) 5 extra lines in the docstring, (b) 2 state reads moved inside the lock (no new I/O). Neither adds measurable runtime.
- **lint_delta AP-1 at test:469,1032,2527**: `os.environ.get("S0_01_FRAMEDIR", "")` inside agent fixture code strings. The env var is set by the test itself; the agent reads it to know where to write `grandchild.pid`. Not a config-channel violation. FALSE POSITIVE.
- **lint_delta AF-AP-40 at test:527,1091,2594**: `gc_pid_path.exists()` in `finally` cleanup blocks. The path is read to obtain the pid for the kill+assert. Absence means no grandchild was spawned (the tee died before the agent wrote the file). The own-pid assert after the kill is the real gate. FALSE POSITIVE.

## SELF-ATTACK

1. **RESOLVED (AF-AP-59). The world-scoped census was a real defect, not a mitigated risk.** Under `-n 8` a sibling worker's reparented grandchild sits at ppid==1 matching the sleep pattern, and the assert fires on another test's process. Fixed: all three tests now read their own `grandchild.pid`, kill that pid, and assert that exact pid is gone or in state Z within 2 s. No world-scoped scan. The GRANDCHILD-UNKILLED mutant (kill line removed, own-pid assert kept) dies: `grandchild pid 8405 still alive after kill` at :550.

2. **The LOCK-READS-OUT structural pin uses `ast.dump` string matching, which is fragile across Python versions.** MITIGATED: `ast.dump` produces a canonical string representation that is stable within a major version (3.11); the check looks for the substring `stdin_reader_done` which is a string constant in the AST dump regardless of dump format.

3. **The lag assertion added to test_directional_trails_timeline_after_sigkill uses `tl_c2a + tl_a2c` as `tl_last_seq` instead of reading the actual max seq from timeline entries.** This assumes timeline entries are exactly the union of c2a and a2c entries, which is true by construction (both pumps write to the same timeline file and nothing else does). If a pump wrote a duplicate or a non-c2a/a2c entry, this count would diverge from the actual max seq. The existing test already counts entries this way for the directional comparison.
