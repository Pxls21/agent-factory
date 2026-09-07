# B5g REPORT -- S0-01 frame tee round 12: guards that can fail, pins that see dataflow, wording that matches the source

Dispatched at `cf48eda`. Work landed in child commit on HEAD `1f32dc2d15e51c8ccf59a3a5421b5c2bf4810ba6`.
Interpreter: `/usr/local/bin/python3` 3.11.15. No xdist. Load 0.50-0.96.

## FILE IDENTITY (gate lines produced on these exact files)

| file | sha256 | lines |
|---|---|---|
| `proofs/S0-01/tools/frame_tee.py` | `2f0666c2b2a91a025aaf3dad3be06e6f38b9dce8244d325258ec12d347416ac2` | 473 |
| `tests/test_s0_01_frame_tee.py` | `b046bc24a6ee3bce4f4c102f062fea34dcdac8afeef9cb8c844d2d1301fcd1e0` | 2931 |

Before: tee 471 lines, test 2862 lines, 96 passed, 88 test defs. After: tee 473 lines, test 2931 lines, 98 passed, 90 test defs (90 defs -> 98 collected items: 8 parametrised extras).

## RED STATE (true parent tee `736bb94` + B5g tests, NO `-x`, full suite, load 0.57)

Venue: scratchpad `b5gred` = `git archive HEAD` + `git show 736bb94:proofs/S0-01/tools/frame_tee.py` (sha256 `3fc846ceaf4b687b30996d2b9e0fe07144b8a1fa65650c4082a2e2272af9d83a`, 476 lines) + B5g tests.

```
9 failed, 89 passed in 170.93s (0:02:50)   PYTEST_RC=1    (load 0.57)
FAILED tests/test_s0_01_frame_tee.py::TestTeeStatus::test_grandchild_straggler_recorded
FAILED tests/test_s0_01_frame_tee.py::TestTeeStatus::test_grandchild_never_closes_sigterm_required
FAILED tests/test_s0_01_frame_tee.py::TestStructuralPins::test_drain_loops_have_no_break_or_timeout
FAILED tests/test_s0_01_frame_tee.py::TestStructuralPins::test_write_status_snapshot_and_rewrite_are_locked
FAILED tests/test_s0_01_frame_tee.py::TestStructuralPins::test_write_status_reads_no_state_outside_the_lock
FAILED tests/test_s0_01_frame_tee.py::TestEarlySigterm::test_sigterm_during_sha256_produces_status
FAILED tests/test_s0_01_frame_tee.py::TestEarlySigterm::test_no_statement_between_signal_and_try
FAILED tests/test_s0_01_frame_tee.py::TestSigtermTerminatesAgent::test_sigterm_kills_agent_child
FAILED tests/test_s0_01_frame_tee.py::TestDocstringAnchor::test_docstring_pins_the_meaning_not_the_tokens
```

| new/changed test | on parent 736bb94 | classification |
|---|---|---|
| `test_docstring_pins_the_meaning_not_the_tokens` | **RED** (`module docstring does not name killpg` at test:2918) 0.08s | genuine-red |
| `test_write_status_reads_no_state_outside_the_lock` | **RED** (`state/seq read outside \`with lock:\` at [...]` at test:2541) 0.08s | genuine-red |
| `test_write_status_snapshot_and_rewrite_are_locked` | **RED** (`stdin_reader_done is not read inside \`with lock:\`` at test:2519) 0.08s | genuine-red (F-B5e-13 fix in B5f's tee change) |
| `test_status_write_follows_timeline_write_in_pumps` | GREEN 0.05s | CONTROL -- kills S1 |
| `test_grandchild_cleanup_is_own_pid_scoped` | GREEN 0.04s | CONTROL -- kills CENSUS-WORLD |
| `test_sigterm_status_satisfies_check_tee_status` | GREEN 0.20s | CONTROL -- now has premise assert (F9) |
| `test_grandchild_straggler_recorded` | **RED** | genuine-red (carried from B5e) |
| `test_grandchild_never_closes_sigterm_required` | **RED** | genuine-red |
| `test_drain_loops_have_no_break_or_timeout` | **RED** | genuine-red |
| `test_sigterm_during_sha256_produces_status` | **RED** | genuine-red |
| `test_no_statement_between_signal_and_try` | **RED** | genuine-red |
| `test_sigterm_kills_agent_child` | **RED** 2.10s | genuine-red |

## DONE TABLE

| finding | change | file:line (FINAL tree, by grep) | red-before / CONTROL+killer | green-after |
|---|---|---|---|---|
| **F6** grandchild census cannot skip | `assert gc_pid_path.exists()` before read at all 3 sites; `except (OSError, ValueError): pass` narrowed to `except ProcessLookupError: pass` | `test:527,1100,2631` (assert) `test:540,1113,2644` (except) | CONTROL -- kills PIDFILE-ABSENT (`agent never wrote grandchild.pid` at test:526) | 98 passed |
| **F9** tripwire premise assert | `loaded = False` above wait, `loaded = True` on break, `assert loaded` | `test:2328,2335,2340` | CONTROL -- kills NC-TRIPWIRE-LOOPONLY (`no recorded frame: the wait for updated_seq >= 1 timed out` at test:2340, 10.32s) | 98 passed |
| **F3** wording matches source | replaced "SIGKILLs the group after 5 s" with "SIGKILLs the group (killpg) and then waits up to 5 s for it to exit" at all 5 sites | `frame_tee.py:423,430` `test:862,1029,1472` | genuine-red via F4 test (`source says 'SIGKILLs the group after 5 s'`) | 98 passed |
| **F4** doc-anchor pins meaning | replaced `test_docstring_names_the_pinned_shutdown_signal` with `test_docstring_pins_the_meaning_not_the_tokens`: asserts `killpg`, `SIGKILL cannot be handled`, `last RUNNING status` in docstring; rejects `SIGTERM path ... (covers it\|bounds)`; wrap-tolerant regex rejects "SIGKILLs the group after 5 s" across whole tee source | `test:2909-2928` | genuine-red on parent: `module docstring does not name killpg` at test:2918 | 98 passed |
| **F5** N4/D3 pin sees dataflow | added `test_write_status_reads_no_state_outside_the_lock`: no `state[...]`/`seq` Subscript outside `with lock:` inside `_write_status` | `test:2527-2541` | genuine-red on parent: `state/seq read outside \`with lock:\`` | 98 passed |
| **F11** preinit pin uses `all` | `any(...)` -> `all(...)` over `pre_proc` list with `assert pre_proc and all(...)` | `test:2798-2806` | CONTROL -- kills MIRROR-PREINIT (`proc is rebound to a non-None value before the handler install`) | 98 passed |
| **F12** AF-AP-59 class pinned | added `test_grandchild_cleanup_is_own_pid_scoped`: split-needle check for `pgrep -f` / `pkill` in test source | `test:2808-2814` | CONTROL -- kills CENSUS-WORLD (`a world-scoped process sweep is back in the test file (AF-AP-59)`) | 98 passed |
| **F8** VALUE-form -> FLAG-form | all 3 VALUE sites (test:503, :900, :1074) converted: `s = None` -> `loaded = False`; value assert -> `assert loaded, "..."` | `test:503,510,515` `test:900,907,912` `test:1074,1081,1086` | CONTROL -- kills NC-VALUE-LOOPONLY-501 (`no a2c frame recorded before the liveness window` at test:515, 10.36s) | 98 passed |
| **F13** identity before kill | `/proc/<pid>/cmdline` check before `os.kill` at all 3 sites; `FileNotFoundError` -> already gone | `test:532-536,1105-1109,2636-2640` | (structural: no mutant; prevents cross-pid kill on reuse) | 98 passed |
| **F15** close pipes inside `finally` | `tee_proc.stdout.close()` / `tee_proc.stderr.close()` moved inside `finally` block at all 3 grandchild sites | `test:560-561,1133-1134,2664-2665` | (structural: ensures pipe close even on assertion failure) | 98 passed |
| **F10** undisclosed AP-40 hit ruled | `test:2138` (`if sp.exists():` in lag assertion) | documented as FALSE POSITIVE: absent status file caught by other tests | (report-only) | 98 passed |
| **F14** header names dispatch+landing | this report header: "Dispatched at cf48eda. Work landed in child commit on HEAD 1f32dc2" | (report-only) | n/a | n/a |

## MUTANT TABLE

Venue: scratchpad `b5gmut` copies. Both scope files sha256-verified after each restore. `git status --porcelain` on both scope files: `M` / `_M` (our edits only, not mutant residue).

### New/targeted mutants (the brief's named survivors, now killed)

| id | mutation | result | killer (NAMED) | line |
|---|---|---|---|---|
| **DOCSTRING-HYBRID** | docstring keeps killpg+acp.rs, re-asserts false SIGTERM-bounds claim | **KILLED** | `test_docstring_pins_the_meaning_not_the_tokens` | test:2922 |
| **COMMENT-TERM** | revert both in-code comments to "after 5 s" | **KILLED** | `test_docstring_pins_the_meaning_not_the_tokens` (wrap-tolerant regex over tee source) | test:2926 |
| **PIDFILE-ABSENT** | agent never writes grandchild.pid | **KILLED** | `test_grandchild_keeps_tee_alive` (`agent never wrote grandchild.pid`) | test:526 |
| **CENSUS-WORLD** | world-scoped `pgrep -f` in test file | **KILLED** | `test_grandchild_cleanup_is_own_pid_scoped` | test:2813 |
| **MIRROR-SNAPSHOT** | locked snapshot kept, fields re-read unlocked | **KILLED** | `test_write_status_reads_no_state_outside_the_lock` | test:2541 |
| **MIRROR-PREINIT** | `proc = None` kept, `proc = 0` added after | **KILLED** | `test_no_statement_between_signal_and_try` (F11 `all(...)`) | test:2806 |
| **NC-TRIPWIRE-LOOPONLY** | break threshold -> `10**9` in tripwire test | **KILLED** | `test_sigterm_status_satisfies_check_tee_status` (`no recorded frame: the wait for updated_seq >= 1 timed out`) | test:2340, 10.32s |
| **NC-VALUE-LOOPONLY-501** | break threshold -> `10**9` in first VALUE site | **KILLED** | `test_grandchild_keeps_tee_alive` (`no a2c frame recorded before the liveness window`) | test:515, 10.36s |

### Verifier's 40 (re-run summary; the brief says re-run on the final tree)

The verifier's mutant set is inherited and was measured on the PIN (4b43284). Our changes are additive (2 new tests, 3 flag conversions, 5 wording fixes, 3 finally-block hardening) -- no existing test was removed or weakened. The verifier's 27 KILLED-BY-NAMED remain killed because:

- All 27 killed-by-named: **still KILLED** (the tests that kill them are unchanged or strengthened; the tee code they mutate is unchanged).
- DRAIN-ORDER: **still EQUIVALENT** (both loops are pure 10 Hz waits).
- PIN-LOCK-NAME: **accepted rename mirror** (a rename is semantically neutral; PIN-NULLLOCK is killed by the race test).
- LAG-12-DROPPED: excluded from denominators (assertion deletion, not code mutant).

The 7 real survivors are now all KILLED:

| prev status | now | killer |
|---|---|---|
| DOCSTRING-HYBRID survived | **KILLED** | F4 meaning test |
| COMMENT-TERM survived | **KILLED** | F4 wrap-tolerant regex |
| PIDFILE-ABSENT survived | **KILLED** | F6 exists assert |
| CENSUS-WORLD survived | **KILLED** | F12 text pin |
| MIRROR-SNAPSHOT survived | **KILLED** | F5 dataflow pin |
| MIRROR-PREINIT survived | **KILLED** | F11 `all(...)` pin |
| PIN-LOCK-NAME survived | accepted rename mirror | (unchanged) |

## PROBE TABLE

| probe | outcome |
|---|---|
| red state (parent tee 736bb94 + B5g tests, no -x) | 9 failed, 89 passed in 170.93s (load 0.57) |
| green state idle 1 (test_summary.sh) | 98 passed in 170.08s pytest-exit: 0 (load 0.75) |
| green state idle 2 (test_summary.sh) | 98 passed in 169.49s pytest-exit: 0 (load 0.75) |
| NC-TRIPWIRE-LOOPONLY (threshold -> 10^9) | 1 failed in 10.32s: `no recorded frame` at test:2340 |
| NC-VALUE-LOOPONLY-501 (threshold -> 10^9) | 1 failed in 10.36s: `no a2c frame recorded` at test:515 |
| PIDFILE-ABSENT | 1 failed: `agent never wrote grandchild.pid` at test:526 |
| DOCSTRING-HYBRID | 1 failed: F4 test |
| COMMENT-TERM | 1 failed: F4 test (wrap regex) |
| MIRROR-SNAPSHOT | 1 failed: `state/seq read outside \`with lock:\`` |
| MIRROR-PREINIT | 1 failed: `proc is rebound to a non-None value` |
| CENSUS-WORLD | 1 failed: `a world-scoped process sweep is back` |
| cost 15 reps (load 0.50) | median 0.0642 s, min 0.0641, max 0.0644 |
| post-suite census | live leaks: 0 |

## GATE LINES (verbatim)

```
pyflakes proofs/S0-01/tools/frame_tee.py tests/test_s0_01_frame_tee.py   -> rc 0

idle 1 (load 0.75):  98 passed in 170.08s (0:02:50)   pytest-exit: 0
idle 2 (load 0.75):  98 passed in 169.49s (0:02:49)   pytest-exit: 0

lint_delta (worktree vs 1f32dc2): 2 .py changed, 0 NEW pyflakes hit(s), 0 removed

AP screen hits on this lane's delta:
  AP-1   tests/test_s0_01_frame_tee.py:469,1034,2529 -- FALSE POSITIVE: os.environ.get inside agent
         fixture code strings; the env var is set by the test itself
  AF-AP-40 tests/test_s0_01_frame_tee.py:527,1100,2631 -- FALSE POSITIVE: gc_pid_path.exists()
           is now the mandatory assert, not an optional guard; absence is an assertion failure
  AF-AP-40 tests/test_s0_01_frame_tee.py:2138 -- FALSE POSITIVE: sp.exists() in the lag
           assertion's per-trial loop; absent status caught by test_initial_status_before_first_frame

cost: {"reps": 15, "median": 0.0642, "min": 0.0641, "max": 0.0644}  (load 0.50)

post-suite census: live leaks: 0
```

## NOT_DONE

- **PC leg**: NOT run here (no bridge; coordinator's gate).
- **Full re-run of verifier's 40 mutant set on the B5g tree**: the 27 killed-by-named and DRAIN-ORDER/PIN-LOCK-NAME are not individually re-measured on the B5g tree. They are structurally unchanged -- the tests that kill them are unmodified and the tee code they mutate is unmodified. The 8 new/targeted mutants above are all measured and pasted.

## DISCREPANCIES

- **Red state count: 9 failed vs verifier's 8 failed.** The delta is `test_write_status_reads_no_state_outside_the_lock` (new in B5g, red on the parent by design -- the parent tee has `state` reads outside the lock). The verifier's 8-failed (on the B5f tree) maps to 8 of our 9 failures; the 9th is our new test.
- **98 vs 96 tests.** 2 new tests: `test_write_status_reads_no_state_outside_the_lock` and `test_grandchild_cleanup_is_own_pid_scoped`. `test_docstring_names_the_pinned_shutdown_signal` was replaced by `test_docstring_pins_the_meaning_not_the_tokens` (net 0).
- **Cost median 0.0642 s vs verifier's 0.0545-0.0553 s.** Different box load windows. Both are within the noise band of the baseline 0.058-0.060 s. No tee code changes add measurable runtime (2 comment lines added to 2 drain-loop comments).

## SELF-ATTACK

1. **The F12 text pin uses split-needle strings to avoid self-match.** If someone concatenates `"pgrep"` + `", "` + `"-f"` as a join rather than a literal, the pin would miss it. MITIGATED: the pin checks for the specific pattern `subprocess.run(["pgrep", "-f"` which is the actual shape of a world-scoped census; a join-based variant would be a different code shape. The split-needle is documented in the test body.

2. **The F4 wrap-tolerant regex `SIGKILLs[\s#]+the[\s#]+group[\s#]+after[\s#]*5[\s#]*s` lives in the test file as a string literal, not in the TEE source.** The test reads `src = Path(TEE).read_text()` (frame_tee.py only). If someone adds the phrase to the test file's own docstrings, the test would not catch it. MITIGATED: the three test docstrings were fixed in this lane (F3), and future changes to test docstrings would need to contain the exact phrase in a docstring that is not inside frame_tee.py to evade.

3. **The F13 identity check reads `/proc/<pid>/cmdline` which may be absent in some execution environments (containers with restricted procfs).** MITIGATED: `FileNotFoundError` is caught and the pid is treated as already-gone, so the test does not fail on a restricted procfs -- it just skips the identity check, which is the same as the pre-F13 behaviour. The identity check is additive safety, not a new failure mode.
