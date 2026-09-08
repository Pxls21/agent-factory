# B5i report — S0-01 frame tee, round 14 (SANDBOX fallback lane)

**PIN: `58741bb23b28ecd574b4f8472cd88dba658ceaad`; landing = the coordinator's checkpoint, made after this report.**
Written 2026-09-08 00:34Z (`date -u`). The shared tree's HEAD moved to `23a3458729430078565f47657e2b5e03d787b7d1`
while I worked (coordinator commits on other paths); my two scope files are byte-identical at the PIN and at that
HEAD's parent commit set — `git diff 58741bb -- <the two files>` was empty at dispatch, so the PIN venue and the
shared tree agree on my inputs.

**Venue:** every gate ran from a `git archive 58741bb | tar -x` copy under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/b5i/venue` plus my two files copied in
(`sync.sh`); the pristine copy is `…/b5i/pin`. Mutants were applied to that copy only, restored by `cp` from the
shared tree, never by git. Every pytest run carried an explicit `--basetemp` under that scratch dir. No
`git stash/checkout/restore/reset/add/commit/push`, no outward action, no PC bridge, no network. Every kill I issued
was `os.kill(<pid I started>, 9)` or `Popen.kill()`; no `pkill`/`pgrep` anywhere. Box: 4 cores, shared with other
lanes; load stated next to every timing. Interpreter `/usr/local/bin/python3` = 3.11.15, pytest 9.1.1.

**Shared-tree note for the coordinator:** by the end of this lane the shared tree carried other lanes' uncommitted
edits to `proofs/S0-01/pins.py`, `tools/acp_probe.py`, `tools/build_capture_record.py`, `tools/pc/*` and three other
test files, plus new untracked `proofs/S0-02/`, `S0-04/`, `S0-08/` trees. I touched none of them, and my gates ran
against the PIN's copies of all of them — so a shared-tree run of this suite could differ if one of those edits
changes `PINNED_TEE_STATUS_KEYS`, which my test file imports.

---

## FILE IDENTITY (FINAL bytes)

| file | sha256 | lines |
|---|---|---|
| `proofs/S0-01/tools/frame_tee.py` | `49e3cce4b280a1273cf39a60f6d137c41c9f779cb4c61de1b69e9b84684f5801` | 542 |
| `tests/test_s0_01_frame_tee.py` | `2b5479158898710a8e4e80bd53a8d93b8c01ff1366804ef73bf65b3bbde4675f` | 3738 |

PIN bytes were `8dfdeb7f704d…` / 482 lines and `d1be6adf7ff3…` / 3144 lines. The vendored oracle
`proofs/S0-01/vendor/buzz-acp/acp.rs` is untouched: `44e82861763694d2…`, and it was never written, only read.
`grep -c 'def test_'` = **106** (PIN: 93); collected+passed **114** (PIN: 101).

### GATE LINES (verbatim, one foreground call each, on the FINAL bytes)

```
# run 1   LOAD-BEFORE 4.42 2.64 1.93   (bash scripts/test_summary.sh tests/test_s0_01_frame_tee.py --basetemp=…/gate1)
114 passed in 169.22s (0:02:49)
pytest-exit: 0
pytest-summary: 114 passed in 169.22s (0:02:49)

# run 2   LOAD-BEFORE 1.88 2.36 1.97   (…--basetemp=…/gate2)
114 passed in 174.08s (0:02:54)
pytest-exit: 0
pytest-summary: 114 passed in 174.08s (0:02:54)

# PIN baseline, my own, same venue construction   LOAD-BEFORE 2.07 2.49 2.12
101 passed in 195.24s (0:03:15)
pytest-exit: 0
pytest-summary: 101 passed in 195.24s (0:03:15)
```

+13 tests and ~21-26 s FASTER than the PIN: the `range(3000)` revert and site 3's early stdin close give back more
than the new tests cost.

---

## DONE

| # | item | where (FINAL bytes) | red-before (my run) | green (my run) |
|---|---|---|---|---|
| 1 | One sentence in the repo, joined by EQUALITY | `tee:51` `PINNED_SHUTDOWN_CLAUSE = (`; the built sentence and `assert PINNED_SHUTDOWN_CLAUSE == expected_clause` at `test:3619`; docstring presence `test:3633` `assert clause_norm in doc_norm`; citations `test:3649` `assert (start, end) == (sd_start, sd_end)` and `test:3653` `assert (start, end) == (kpg_start, kpg_end)`; negatives `test:3661` `assert token not in residue`, `test:3666` `assert "SIGTERM" not in head`, `test:3697` `assert ref_norm in _ws_norm(text)`, `test:3700` `assert token not in text` | On the PIN, the order-reversed constant propagated to all six sites **SURVIVES**: `2 passed, 99 deselected in 0.24s` | Same mutant on my bytes: `AssertionError: PINNED_SHUTDOWN_CLAUSE is not the sentence acp.rs derives` (`1 failed, 1 passed, 112 deselected in 0.35s`) |
| 1b | The five reference sites carry only the reference | `tee:494`, `tee:500` (`buzz-acp's shutdown bound: see PINNED_SHUTDOWN_CLAUSE in frame_tee.py`), the three test docstrings enumerated at `test:3686-3695` `for fname in ("test_never_reading_client",`; constant `test:53` `CLAUSE_REF = ` | PIN: the six sites each restate the bound, and a false sentence beside the true one passes (VERIFY-B5h SEVENTH-SITE) | `COMMENT-TERM` / `TESTDOC-TERM` / `SEVENTH-SITE` all die (mutant table) |
| 2 | The census helper returns its branch | `test:110` `def _kill_own_grandchild`, `test:150` `return "gone"`, `test:172` `return "live"`; callers `test:653`, `test:1268` (`== "live"`), `test:2788` (`== "gone"`) | PIN helper returns `None`, so no site states its branch; `GRANDCHILD-UNKILLED-S3` survives (reproduced, `1 passed, 113 deselected in 30.80s`) | Sites 1/2 kill the mutant (`grandchild pid N still alive after kill`, `test:171`); site 3 asserts `"gone"` and says WHY in the code comment above it |
| 2b | `range(6000)` reverted, stale comment fixed | `test:2706` `"for i in range(3000):` and `test:2703` `# grandchild streams a2c frames for 30 s` | PIN cost: site 3 alone 61.6 s (`PIDFILE-ABSENT-S3` on the PIN, VERIFY-B5h) | site 3 alone now **31.1 s** (`PIDFILE-ABSENT-S3`, my run) |
| 3 | Kill guarded, identity read fail-closed | `test:152` `os.kill(gc_pid, sig.SIGKILL)` inside `try` with `test:154` `return "gone"`; `test:136` `except PermissionError:` → `test:137` `cannot identify pid` | `PROCESSLOOKUP-UNGUARDED` (= the PIN's shape) → `E ProcessLookupError: [Errno 3] No such process` | `1 passed` on the four-path driver `test:3253` `class TestKillOwnGrandchildBranches` |
| 4 | AST kill-site pin as a SUBTRACTION; `_KILL_SITES` gone | `test:3017` `def test_kill_calls_only_at_allowed_sites`, violation assert `test:3059` `assert not violations` | `KILL-MODULE-LEVEL` **survives on the PIN**: `1 passed, 100 deselected in 0.32s` | Same mutant on my bytes: `os.kill/os.killpg outside _kill_own_grandchild: ['kill at line 63 in <module scope>']` |
| 4b | AF-AP-59 row re-run | `test:3001` `def test_grandchild_cleanup_is_own_pid_scoped`, assert `test:3014` `assert not hits` | (coordinator's registry fix is in the PIN) | `CENSUS-PKILL-DQ` and `CENSUS-PGREP-A` both **die** on the PIN's row — pasted below |
| 5 | Hang class closed by a structural pin | `test:3062` `def test_no_unbounded_tee_pipe_reads`, assert `test:3107` `assert not bad`; bounded reader `test:175` `def _read_with_deadline`; six call sites `test:451` `test:504` `test:561` `test:1905` `test:2335` `test:2735`, each `assert answer, "no handshake line from the tee within 30 s"` | RED on the PIN: **6** unbounded sites (`readline at line 407/459/515/1785/2209/2607`) — the brief's list of five plus `:407`, which the verdict missed | `114 passed`; `PIPEREAD-UNBOUNDED` and `HANG-UNBOUNDED-READ` both die on the pin |
| 5b | The hang itself, as a test | `test:3110` `def test_a_silent_agent_cannot_wedge_a_bounded_read`, assert `test:3147` `assert line is None` | Standalone probe on the PIN's tee: `HANG: readline still blocked at 12.0 s`, wchan/fd table pasted below | `1 passed`; reverting the site-3 close (`HANG-REINTRODUCED-STDIN`) dies with `subprocess.TimeoutExpired … timed out after 30 seconds` at `test:2772` `tee_proc.wait(timeout=30)` |
| 6 | Interpreter identity sampled at the first a2c byte | `tee:270` `def _resample_interpreter`, hook `tee:409` `_late_sampled[0] = True`, short-circuit `tee:289` `if rp == identity["agent_interpreter_realpath"]:`; tests `test:3383` `def test_interpreter_is_resampled_at_the_first_a2c_byte` and `test:3452` `def test_resample_that_loses_the_race_is_loud_not_silent` | PIN, 20 trials, two-stage agent: **20/20 `/usr/bin/bash`** | My tee, same fixture: **20/20 `/usr/bin/python3.11`**; `IDENTITY-EARLY-ONLY` dies |
| 7 | `S0_01_AGENT` validated like `S0_01_FRAMEDIR` | `tee:131` `S0_01_AGENT is empty`, `tee:134` `is not an executable file`, `tee:234` `cannot spawn S0_01_AGENT`; tests `test:863` `def test_empty_agent`, `test:874` `def test_non_executable_agent`, `test:886` `def test_directory_agent`, `test:896` `def test_agent_that_cannot_be_spawned` | PIN: `rc=1`, uncaught `PermissionError: [Errno 13] Permission denied: ''`, framedir empty (same for a directory, a plain file and a FIFO) | rc **64** with the named line and no traceback in all four shapes; the control run still exits 0 and writes all five artifacts |
| 8 | Hygiene | `tee:34` `# imported by tests/test_s0_01_frame_tee.py`; `report_lint` summary below | VERIFY-B5h F14 (import at collection time, unmarked) | line present; `pyflakes` rc 0 on both files |
| 9 | 18-class self-sweep over my test file | table below | rows 1.1/1.2/1.3/10.5/14.1 were DEFECT at the PIN | all five fixed and each fix has a mutant that kills it |

### What changed in the tee's prose, and why (item 1)

The module docstring keeps every fact it had; the SIGTERM paragraph moved BELOW the shutdown paragraph so the
negative guard `assert "SIGTERM" not in head` (`test:3666`) can hold — on the PIN the docstring named SIGTERM three
times before the anchor sentence `The SIGTERM path below covers an operator/systemd TERM` (`tee:20`), so the guard
the verdict proposed would have failed on the PIN's own bytes. Nothing was dropped: the `final`-field paragraph now
follows the anchor.

The kill-helper citation was corrected from `:2323-2328` to `:2323-2329` (`tee:17`). Derived by one mechanical rule —
a function spans from its `fn` line to the closing brace at the same indent — `shutdown()` is 422-444 (exactly what
the docstring already cited) and `kill_process_group` is 2323-**2329**; the old citation stopped one line short of
the closing brace, i.e. it used a different convention from the citation beside it. Both are now asserted, not typed.

---

## MUTANT TABLE — 43 rows, 43 ran, 42 killed, 1 survives by construction

Protocol: restore both scope files by copy → apply → `ast.parse` both files → run the named killer with its own
`--basetemp` → restore. `git status --porcelain` on the shared tree showed only my two files modified (plus lane
A5j's, which I never touched) at every checkpoint.

### Item 1 — the prose oracle (14 rows, all re-run against the FINAL bytes)

| mutant | result | killer (from the run) |
|---|---|---|
| FALSECONST-ORDER (order reversed at every site) | **KILLED** | `AssertionError: PINNED_SHUTDOWN_CLAUSE is not the sentence acp.rs derives:` — `1 failed, 1 passed, 112 deselected in 0.35s` (`test:3619`) |
| CONST-ORDER | **KILLED** | same assertion, `0.14s` |
| CONST-WRONGEVENT | **KILLED** | same assertion, `0.15s` |
| DOCSTRING-ORDER | **KILLED** | `AssertionError: frame_tee.py's module docstring does not carry PINNED_SHUTDOWN_CLAUSE verbatim` (`test:3633` `assert clause_norm in doc_norm`) |
| DOCSTRING-WRONGEVENT | **KILLED** | same assertion |
| DOCSTRING-HYBRID | **KILLED ×2** | same assertion + `module docstring does not state SIGKILL cannot be handled` — `2 failed, 112 deselected in 0.20s` |
| SITECOUNT-DUP (clause deleted from the docstring, duplicated into a comment) | **KILLED ×2** | same assertion — the pin is per-site presence now, not a file-wide count |
| SEVENTH-SITE (false sentence beside the true clause) | **KILLED** | `AssertionError: frame_tee.py's module docstring states the shutdown bound outside PINNED_SHUTDOWN_CLAUSE ('5 s')` (`test:3661` `assert token not in residue`) |
| CITE-421 | **KILLED** | `AssertionError: frame_tee.py cites acp.rs:421-444; shutdown() spans 422-444` (`test:3649` `assert (start, end) == (sd_start, sd_end)`) |
| CITE-KPG-2324 | **KILLED** | `AssertionError: frame_tee.py cites :2324-2329; kill_process_group spans 2323-2329` (`test:3653` `assert (start, end) == (kpg_start, kpg_end)`) |
| CITE-421-TEST (a wrong citation added to a test docstring) | **KILLED** | `AssertionError: test file cites acp.rs:421-444; shutdown() spans 422-444` |
| COMMENT-TERM (both R1 comments restate the bound) | **KILLED ×2** | `AssertionError: frame_tee.py comment above 'while to.is_alive():' does not carry the reference` (`test:3697-3698` `does not carry the reference`) + the wrap-tolerant regex |
| TESTDOC-TERM | **KILLED ×2** | `AssertionError: test docstring test_never_reading_client does not carry the reference` |
| UNION-DOCROT (SEVENTH-SITE + all three citation mutants) | **KILLED, FULL SUITE** | `1 failed, 113 passed in 170.37s (0:02:50)`; first failure `frame_tee.py cites acp.rs:421-444` |

### Items 2-9 (29 rows)

| mutant | result | killer (from the run) |
|---|---|---|
| GRANDCHILD-UNKILLED-S1 | **KILLED** `5.6s` | `AssertionError: grandchild pid 15589 still alive after kill` (`test:171` `grandchild pid %d still alive after kill`) |
| GRANDCHILD-UNKILLED-S2 | **KILLED** `17.6s` | same assertion, pid 15602 |
| GRANDCHILD-UNKILLED-S3 | **SURVIVES — by construction** `31.0s` | `1 passed, 113 deselected in 30.80s`. Site 3's `finally` cannot run until `tee_proc.wait()` returns, the tee cannot exit until its a2c pump sees EOF, and a2c EOF *is* the grandchild's death: the grandchild is guaranteed dead before the census there for ANY lifetime. The code says exactly this above `test:2788` and the site asserts `== "gone"`. |
| ZOMBIE-OLDSEMANTIC | **KILLED** `2.0s` | `AssertionError: pid 15473 is not the grandchild (cmdline: )` |
| PROCESSLOOKUP-UNGUARDED | **KILLED** | `E ProcessLookupError: [Errno 3] No such process` in `test_pid_that_raced_us_to_exit_reports_gone` |
| PERMISSION-UNGUARDED | **KILLED** | `Failed: DID NOT RAISE AssertionError` in `test_unidentifiable_pid_is_never_signalled` |
| HELPER-MSG (the fail-closed message reworded) | **KILLED** | `assert ('cannot identify pid %d -- not killing' % 18818) in 'pid 18818 unreadable'` (`test:3340`) |
| KILL-MODULE-LEVEL | **KILLED** | `os.kill/os.killpg outside _kill_own_grandchild: ['kill at line 63 in <module scope>']` (`test:3059-3060` `os.kill/os.killpg outside _kill_own_grandchild`) |
| KILL-LAMBDA (class-body lambda) | **KILLED** | same assertion, `['kill at line 63 in <module scope>']` |
| CENSUS-PKILL-DQ | **KILLED** | `AF-AP-59 match in test file: ['"pkill", "-f"']` (`test:3014-3015` `AF-AP-59 match in test file`) |
| CENSUS-PGREP-A | **KILLED** | `AF-AP-59 match in test file: ['"pgrep", "-a", "-f"']` |
| CENSUS-WORLD | **KILLED** | `AF-AP-59 match in test file: ['"pgrep", "-f"']` |
| CENSUS-PGREP-X | **KILLED** | `os.kill/os.killpg outside _kill_own_grandchild: ['kill at line 65 in <module scope>']` |
| PIPEREAD-UNBOUNDED | **KILLED** | `unbounded read of a tee pipe outside a bounded helper: ['readline at line 2334 in test_late_frame_after_agent_death_recorded']` (`test:3107-3108` `unbounded read of a tee pipe outside a bounded helper`) |
| HANG-UNBOUNDED-READ | **KILLED** | `unbounded read of a tee pipe outside a bounded helper: ['readline at line 3145 in test_a_silent_agent_cannot_wedge_a_bounded_read']` |
| HANG-REINTRODUCED-STDIN (site 3's early close reverted) | **KILLED** `75.6s` | `E subprocess.TimeoutExpired: Command '[…frame_tee.py]' timed out after 30 seconds` at `tee_proc.wait(timeout=30)` (`test:2772`; `:2764` in the mutated file) |
| IDENTITY-EARLY-ONLY | **KILLED** `10.3s` | `trial 0: runtime-identity.json names '/usr/bin/bash', expected the interpreter that spoke (/usr/bin/python3.11)` (`test:3421-3423` `assert seen == python_real`) |
| RESAMPLE-ALWAYS-SHORTCIRCUIT | **KILLED** `10.3s` | same assertion — the cost short-circuit cannot swallow the real case |
| RESAMPLE-SILENT (re-sample forced to fail, stderr marker removed) | **KILLED** | `trial 0: no marker on stderr, so the resample ran -- it must record the interpreter that spoke, not '/usr/bin/bash'` (`test:3486` `no marker on stderr, so the resample ran`) |
| IDENTITY-KEYSET (an extra key in the identity record) | **KILLED** | `the re-sample changed runtime-identity.json's key set` (`test:3435`) |
| AGENT-EMPTY-UNGUARDED | **KILLED** | `assert 'frame_tee: S...cutable file:' == 'frame_tee: S...GENT is empty'` |
| AGENT-NONEXEC-UNGUARDED | **KILLED** | `assert "frame_tee: c...t0/plain.txt'" == 'frame_tee: S...nt0/plain.txt'` |
| AGENT-SPAWN-UNGUARDED | **KILLED** | `assert 1 == 64` in `test_agent_that_cannot_be_spawned` |
| PIDFILE-ABSENT-S1 | **KILLED** `3.6s` | `AssertionError: agent never wrote grandchild.pid` (`test:129` `agent never wrote grandchild.pid`) |
| PIDFILE-ABSENT-S2 | **KILLED** `15.6s` | same assertion |
| PIDFILE-ABSENT-S3 | **KILLED** `31.1s` | same assertion (PIN: 61.6 s) |
| R19-COLLECTOR (tee unlinks its evidence before `os._exit`) | **KILLED** | `AssertionError: tee wrote no timeline.jsonl` (`test:230` `tee wrote no timeline.jsonl`) — `1 failed, 103 deselected, 10 errors in 1.49s`; on the PIN seven of those tests passed vacuously |
| TRIAL-ARTIFACT-ABSENT | **KILLED** | `trial 0: tee wrote no timeline.jsonl` (`test:2245` `trial %d: tee wrote no timeline.jsonl`) |
| R18-DEVFULL (`_DEV_FULL` repointed) | **KILLED** | `S0_01_VENUE=sandbox but /dev/full is absent -- the tee's write-failure proofs cannot run in this venue and would skip green` (`test:921`) |

---

## PROBES

### Cost probe — 15 reps × 3 batches, PIN tee vs this lane's tee, back to back in one window

11-frame real-leg shape (3 c2a in, 8 a2c out), full spawn→exit wall clock.

```
FIRST MEASUREMENT (before the fix it forced)      LOAD-BEFORE 1.18 1.38 1.59
PIN  sha256 8dfdeb7f704dfd59      LANE sha256 1b802defdf7abfb4
PIN   batch0 {"reps": 15, "median": 0.0533, …}    LANE batch0 {"reps": 15, "median": 0.1565, …}
PIN   batch1 {"reps": 15, "median": 0.0571, …}    LANE batch1 {"reps": 15, "median": 0.1576, …}
PIN   batch2 {"reps": 15, "median": 0.0547, …}    LANE batch2 {"reps": 15, "median": 0.1561, …}
  -> 2.9x SLOWER: the re-sample re-hashed the interpreter binary on every leg.

AFTER the short-circuit (frame_tee.py line 289)  LOAD-BEFORE 1.23 1.37 1.58
PIN  sha256 8dfdeb7f704dfd59      LANE sha256 49e3cce4b280a127
PIN   batch0 {"reps": 15, "median": 0.0539, "min": 0.0508, "max": 0.1543}
LANE  batch0 {"reps": 15, "median": 0.054,  "min": 0.051,  "max": 0.1535}
PIN   batch1 {"reps": 15, "median": 0.0541, "min": 0.0495, "max": 0.1558}
LANE  batch1 {"reps": 15, "median": 0.0535, "min": 0.0514, "max": 0.154}
PIN   batch2 {"reps": 15, "median": 0.0528, "min": 0.0504, "max": 0.154}
LANE  batch2 {"reps": 15, "median": 0.0553, "min": 0.0526, "max": 0.1805}
  -> per-batch LANE/PIN 1.00x / 0.99x / 1.05x; median-of-medians 0.0539 vs 0.0540 = 1.00x.
```

The re-sample now re-reads `/proc/<pid>/exe` on every leg but re-hashes only when the path CHANGED — a single-stage
agent pays one readlink. This was found by measuring, not by review: the first build was a real 3x regression.

### The hang, reproduced on the PIN's tee (bounded probe, tee SIGKILLed by pid)

```
HANG: readline still blocked at 12.0 s
  tee pid 6304 state=S threads=['6304', '6307']
    tid 6304 wchan=hrtimer_nanosleep      <- the tee's main-thread drain loop
    tid 6307 wchan=anon_pipe_read         <- the c2a reader, blocked on the tee's stdin
    TEST fd 4 -> pipe:[547083]
    TEE  fd 0 -> pipe:[547083]            <- the SAME pipe: the test holds the write end
PROBE RESULT: DEADLOCK REPRODUCED (tee SIGKILLed by pid 6304)
```

### The structural pin, RED on the PIN

```
UNBOUNDED-TEE-PIPE-READS: 6
  readline at line 407 in test_late_client_frame_recorded_or_exit_70
  readline at line 459 in test_late_frame_agent_stdin_closed_before_handshake
  readline at line 515 in test_agent_stdin_closed_before_handshake_exit_code
  readline at line 1785 in test_agent_exits_without_consuming_stdin_exit_70
  readline at line 2209 in test_late_frame_after_agent_death_recorded
  readline at line 2607 in test_concurrent_main_thread_status_vs_pump
```

### Interpreter identity, 20 trials each (two-stage agent: a bash wrapper that `exec`s python)

```
PIN  tee: 20 /usr/bin/bash          (the production sweep measured 18/20 on its box)
LANE tee: 20 /usr/bin/python3.11    (deterministic shape: the agent blocks on stdin, the test holds the tee's stdin)
```

### `S0_01_AGENT` domain on the PIN (red-before, verbatim)

```
--- A: S0_01_AGENT empty ---            rc=1
PermissionError: [Errno 13] Permission denied: ''     framedir contents: (empty)
--- B: S0_01_AGENT = a directory ---    rc=1   PermissionError: [Errno 13] Permission denied: '…/agentenv'
--- C: S0_01_AGENT = plain file ---     rc=1   PermissionError: [Errno 13] Permission denied: '…/plain.txt'
```

Green, my tee: `rc=64` + `frame_tee: S0_01_AGENT is empty` / `… is not an executable file: <path>` (directory, plain
file and FIFO) / `frame_tee: cannot spawn S0_01_AGENT <path>: [Errno 2] No such file or directory` (an executable
script with a missing shebang interpreter — the arm that proves the `except OSError` at `tee:233` is reachable, not
dead). No traceback in any of them; the framedir stays empty.

### Standalone pins on 3.11 / 3.12 / 3.13 (pytest is installed for 3.11 only)

```
3.11.15  {'sha_ok': True, 'sigterm': 0, 'kpg': (2323, 2329), 'sd': (422, 444), 'kill<wait': True,
          'equality': True, 'doc_carries_clause': True, 'residue_clean': True, 'head_clean': True,
          'cites': ([(422, 444)], [(2323, 2329)]), 'cites_ok': True, 'ref_sites': 5, 'ref_ok': True,
          'kill_sites': [(152, '_kill_own_grandchild')], 'kill_pin_ok': True, 'unbounded_reads': [],
          'ap59_hits': [[]]}
3.12.3   identical
3.13.12  identical
```

### The mechanical checkers

```
$ python3 -m pyflakes proofs/S0-01/tools/frame_tee.py tests/test_s0_01_frame_tee.py     rc=0   (no output)

$ python3 scripts/lint_delta.py --base 58741bb23b28ecd574b4f8472cd88dba658ceaad
lint_delta (worktree vs 58741bb23b28ecd574b4f8472cd88dba658ceaad): 8 .py changed, 0 NEW pyflakes hit(s), 0 removed
anti-pattern screen (TELLS on added lines — verify each, advisory):
  AF-AP-55 proofs/S0-01/tools/frame_tee.py: identity sampled from /proc/<pid>/exe …
  AP-1     tests/test_s0_01_frame_tee.py: env read in edited code …
  AF-AP-40 tests/test_s0_01_frame_tee.py: presence-gated check …
lint_delta rc=0
```
(The two `tests/test_s0_01_check_acp_conformance.py` rows in that output belong to lane A5j's uncommitted edits, not
to me — `lint_delta` scans the whole worktree delta.) Classification of my three tells: **AF-AP-55** is the row's own
remedy being applied — the late re-sample plus a multi-stage fixture at `test:3383` `def test_interpreter_is_resampled_at_the_first_a2c_byte`.
**AP-1** is `test:57` `_VENUE = os.environ.get`, resolved once at module scope and gated by `test:911` `def test_dev_full_declared`.
**AF-AP-40** is the poll gate `test:3412` `if id_path.exists():`, followed by the loud `test:3421` `assert seen == python_real`.

```
$ python3 scripts/report_lint.py tasks/briefs/s0-01-b5i-support/B5i-report.md \
      --map tee=proofs/S0-01/tools/frame_tee.py --map test=tests/test_s0_01_frame_tee.py
report_lint: 156 refs — OK 149, NEAR 0, MISS 0, UNCHECKABLE 7, UNRESOLVED 0 (worktree)
```
The seven UNCHECKABLE lines are inside the pasted `ap_screen.py` output block below: the tool's own
`<path>:<line>: <text>` lines carry no backticked claim token for the linter to test. They are verbatim tool output,
not references I typed.

```
$ python3 scripts/ap_screen.py --tests tests/test_s0_01_frame_tee.py
--- TEST_SCREEN over 1 path(s): 1 hits over 1 files ---
AP-66: 1
    tests/test_s0_01_frame_tee.py:1039: timer.daemon = True

$ python3 scripts/ap_screen.py proofs/S0-01/tools/frame_tee.py
--- AP_SCREEN over 1 path(s): 13 hits over 1 files ---
AP-24: 4   (frame_tee.py:368, :376, :395, :473)
AP-1: 3    (frame_tee.py:116, :126, :259)
AF-AP-55: 2 (frame_tee.py:244, :284)
AP-51: 2   (frame_tee.py:6, :7)
AF-AP-58: 1 (frame_tee.py:229)
AP-32: 1   (frame_tee.py:67)
```

**The AF-AP-59 row produces ZERO hits on the test file** — no line in the screen output, and my own pin
(`test:3001` `def test_grandchild_cleanup_is_own_pid_scoped`) reads that same registry row and asserts the same, as
does the standalone `ap59_hits: [[]]` on all three interpreters. Classification of the rest, each by running it:
AP-66 at `test:1039` `timer.daemon = True` is a `threading.Timer`
created two lines above inside the test's own agent-code string (nothing outside can observe it; unchanged by me).
AP-24 ×4 are `except Exception: pass` around `dst.close()` in the pumps (pre-existing, unchanged). AP-1 ×3 are the
two config reads that resolve once and fail closed: `tee:118` `S0_01_FRAMEDIR is not set` … `tee:136` `raise SystemExit(64)`.
An identity field is the third. AF-AP-55 ×2 are
the spawn-time sample and my re-sample — the pair the row asks for. AP-51 ×2 are docstring prose. AF-AP-58 is the
handler install with `try:` on the next statement, pinned by `test_no_statement_between_signal_and_try`. AP-32 is
the interpreter hash.

### Process census after every run (own-venue scoped, no `pgrep`/`pkill`)

```
# right after the last gate run
processes with a cmdline: 24
processes naming my scratch venue: 1        <- the census command's own shell
processes with a time.sleep grandchild cmdline anywhere on the box: 1   <- the same shell (the pattern is in its script text)

# final census, 00:44:44Z
live processes naming my venue: 0 []
orphaned time.sleep grandchildren: 4  -> pid 2477 ppid 1 started 00:43:05Z (age 99 s)
                                        pid 2979 ppid 1 started 00:43:29Z (age 75 s)
                                        pid 3121 ppid 1 started 00:43:31Z (age 73 s)
                                        pid 4341 (another lane's buzz/tee/agent fixture) — gone by the second read
```

Zero live tee/pytest/agent processes of mine. The four sleepers in the final census are **not mine**: they started at
00:43Z, fifteen minutes after my last pytest run ended (00:28:38Z), their cmdlines name no path of mine, and one of
them carries another lane's `parent = "buzz"; child = "tee"; grandchild = "agent"` fixture text. I did not signal
them. My own runs did create up to three such grandchildren by design — `GRANDCHILD-UNKILLED-S2` and
`PIDFILE-ABSENT-S2` both abort before the census can kill one — and each self-exits inside its own 120 s sleep; none
was alive at either census.

---

## ITEM 9 — the 18-class self-sweep over `tests/test_s0_01_frame_tee.py` (FINAL bytes)

Enumeration by AST where the shape allowed (classes 1, 3, 4, 8, 9, 13, 17), by grep otherwise. Verdicts: **D**efect ·
**S**afe (guard named) · **DL** documented limit · **E**quivalent/redundant.

| class | instances | file:line | verdict | the run | fix |
|---|---|---|---|---|---|
| 1 presence-gated (AF-AP-40) | 16 | 14 pre-existing poll gates + `test:3412` `if id_path.exists():` (mine) | **S** | every one sits in a bounded poll with a loud post-assert; mine is `test:3421` `assert seen == python_real`, proven by IDENTITY-EARLY-ONLY | none |
| 1 (collector) | 4 defaults in `_run_tee` | `test:230` `tee wrote no timeline.jsonl` · `test:237` `tee wrote no frames-client-to-agent.jsonl` · `test:241` `tee wrote no frames-agent-to-client.jsonl` · `test:245` `tee wrote no runtime-identity.json` | **D → FIXED** | R19-COLLECTOR: on the PIN 7 tests passed with no evidence at all; now `1 failed, 103 deselected, 10 errors` | absence is an assertion, not a default |
| 1 (trial loop) | 5 gates | `test:2245` `trial %d: tee wrote no timeline.jsonl` · `test:2259-2260` `trial %d: tee wrote no frames-client-to-agent.jsonl` · `test:2261-2262` `trial %d: tee wrote no frames-agent-to-client.jsonl` · `test:2280` `trial %d: tee wrote no tee-status.json` · `test:2045` `tee wrote no timeline.jsonl` | **D → FIXED** | TRIAL-ARTIFACT-ABSENT → `trial 0: tee wrote no timeline.jsonl` | `is_file()` assertions; the `results.append(None)` branch is gone |
| 2 reads outside a walk / no `S_ISREG` | 4 | the four collector reads | **S** | the new assertions use `is_file()` (S_ISREG), not `exists()`; a FIFO or directory fails | — |
| 3 stale `[-1]` | 1 | `test:3554` `line.split("fn")[0].split("//")[-1]` | **E** | a parser split, not a last-artifact read | — |
| 4 negative acceptance | 11 `assert not …` | `test:3014` `assert not hits` · `test:3059` `assert not violations` · `test:3107` `assert not bad` · `test:2686` `assert not stray` · `test:2580` `assert not isinstance(child, ast.Break)` · `test:2985` `assert not any(` · `test:3705` `test:3712` `test:3730` `test:3735` `assert not re.search` | **S** | each structural `assert not` has a mutant that makes it fire (CENSUS-*, KILL-*, PIPEREAD-*, COMMENT-TERM, MIRROR-SNAPSHOT) | — |
| 5 substring/tail anchors classifying an outcome | 17 | `test:843` `frame_tee: S0_01_FRAMEDIR is not set` · `test:871` `assert b"Traceback" not in proc.stderr` · `test:1941` `tee-status.json write failure` · `test:3292` `refusing to kill a foreign pid` · `test:3340` `cannot identify pid` | **S** | AGENT-EMPTY/NONEXEC/SPAWN-UNGUARDED and HELPER-MSG all die; the stderr checks are `==`, not `in` | — |
| 6 env-domain fail-opens | 2 (`_VENUE` `test:57`, `_DEV_FULL` `test:60`) | | **S** | R18-DEVFULL fails the declaration instead of skipping eight tests | one name, read by the predicates and the declaration |
| 7 lossy decodes on a decision path | 1 | `test:1940` `errors="replace"` | **S** | SWEEP-tests R16: a replacement char cannot forge the ASCII anchor; unchanged by me | — |
| 8 broad catches | 1 new | `test:190` `except (OSError, ValueError):` | **S** | both mean "no line"; the caller's `test:451` `no handshake line from the tee within 30 s` then fails loudly — HANG-UNBOUNDED-READ and PIPEREAD-UNBOUNDED exercise the path | — |
| 9 waits/polls, ordinal gates (AF-AP-57) | 31 `while` | all bounded by `time.monotonic() < deadline` or a pipe EOF | **S** | each is followed by a loud assertion; no fake in this file gates on a call ORDINAL | — |
| 10 skips/xfails that cannot fire | 8 | `test:1096` and `test:1947` `pytest.skip("/dev/full not available")` (six more between) | **D → FIXED** | R18-DEVFULL now makes `test:911` `def test_dev_full_declared` fail; before, the eight retired green | venue declaration + one shared name |
| 11 world-scoped enumerations (AF-AP-59) | 0 | — | **S — empty class, and that is a result** | `ap_screen --tests` prints no AF-AP-59 row; CENSUS-PKILL-DQ/-PGREP-A/-WORLD/-PGREP-X all die | — |
| 12 signal installs before their try (AF-AP-58) | 1 pin over the tee | `test:2955` `def test_no_statement_between_signal_and_try` | **S** | unchanged this round; SWEEP-tests 12.1 graded it (the SIGUSR1 mutant dies ten times over in neighbours) | — |
| 13 `/proc/<pid>/exe` races (AF-AP-55) | 2 in the tee | `tee:244` and `tee:284` `os.readlink("/proc/%d/exe" % proc.pid)` | **D → FIXED, residual named** | 20/20 bash → 20/20 python; the residual race is pinned by `test:3452` `def test_resample_that_loses_the_race_is_loud_not_silent` | late re-sample + loud fallback |
| 14 mirrors of the code under test | 2 | `test:3715` `def test_docstring_pins_the_meaning_not_the_tokens` and `test:3496` `def test_shutdown_prose_matches_the_pinned_source` | **D → FIXED / S** | R14's false sentence now dies on the residue guard (SEVENTH-SITE class); the oracle derives, it does not mirror | (d)+(f) in the oracle test |
| 15 two counters over different populations | 1 (mine, removed) | was in `test_resample_that_loses_the_race_is_loud_not_silent` | **D → REMOVED** | `resampled + raced == 20` was a tautology (each trial increments exactly one) | the per-trial coherence asserts carry the test |
| 16 provably redundant guards | 2 | `test:3705` and `test:3735` `assert not re.search` (the same wording ban, once over the tee and once over both files); `test:3618` `expected_clause = "buzz-acp %s first and then %s"` | **E** | deleting the tee-only copy leaves the all-files one; the `else` branch that would build the reversed sentence is unreachable while the sha and the derived order hold | kept, and named here rather than silently |
| 17 hardlink-clobbering writes | 0 | — | **empty class — a result** | the nine `os.symlink` calls create names in a fresh `tmp_path` framedir | — |
| 18 other families | 3 | `test:3035` and `test:3076` `def _map(node, fname):` (deliberately duplicated); `test:175` `def _read_with_deadline` (its daemon reader outlives a timed-out read) | **E / DL** | the two pins are deliberately independent; the daemon thread dies with the interpreter and is documented in the helper's docstring | — |

**Empty classes (a result): 11 and 17 have ZERO instances in this file.**

---

## NOT_DONE

1. **The PC `-n 8` gate of record.** NOT run here: the lane's non-negotiables forbid the bridge, and this is the
   sandbox fallback lane. Two rows would read differently under 8 workers: the AF-AP-59 class (world sweeps) and
   tmp-dir contention. The coordinator's leg remains the gate of record.
2. **`pytest` on 3.12 / 3.13.** NOT run: pytest is installed for 3.11 only, and I attempted no install. The pins ran
   standalone on all three instead (identical output).
3. **`pytest -n 4` / xdist.** NOT run: xdist is not installed in this container.
4. **The hanging form of HANG-UNBOUNDED-READ through pytest.** Deliberately NOT run: a deadlocked pytest+tee pair is
   the failure the brief warns about. The mutant is killed statically by the structural pin (pasted), and the hang
   itself is reproduced by the bounded standalone probe with a 12 s watchdog that SIGKILLs the tee by pid.
5. **A real `PermissionError` from a restricted `/proc`.** The fail-closed path is driven with a monkeypatched
   `builtins.open` in `test:3327` `def test_unidentifiable_pid_is_never_signalled`; I did not restrict procfs for
   one process, which would need to touch the box.
6. **A naturally-forced ProcessLookupError race.** `test:3312` `def test_pid_that_raced_us_to_exit_reports_gone`
   uses a pid ABOVE `pid_max`, so the `os.kill` syscall
   really runs and really returns ESRCH, but the timing race itself is not forced.
7. **Re-running the predecessor's 48-mutant catalogue.** Only the rows this delta can move were run (43 rows).

## DISCREPANCIES

1. **The structural pin flags SIX sites on the PIN, not five.** The brief and VERIFY-B5h F9 list `:2607`, `:2209`,
   `:1785`, `:459`, `:515`; `:407` (`test_late_client_frame_recorded_or_exit_70`) is a sixth unbounded
   `tee_proc.stdout.readline()` that the verdict's own enumeration missed. All six are fixed.
2. **`HANG-REINTRODUCED` as the brief defines it does NOT survive** — I expected it to, and it does not. Reverting
   site 3's early `stdin.close()` fails the test at `tee_proc.wait(timeout=30)` (`test:2772`) with
   `subprocess.TimeoutExpired`, because the tee can no longer exit once its a2c pump drains. Killed, but by the wait
   timeout, not by a designed assertion.
3. **The verdict's F12 negative guard fails on the PIN's own bytes.** `assert "SIGTERM" not in
   doc.split("The SIGTERM path")[0]` is false at the PIN: the docstring names SIGTERM three times before that
   anchor. Implementing it required moving the SIGTERM paragraph below the anchor (no fact dropped).
4. **The kill-helper citation was off by one line under its own convention.** `:2323-2328` stopped before
   `kill_process_group`'s closing brace while the citation beside it (`422-444`) includes `shutdown()`'s. Corrected
   to `:2323-2329` (`tee:17`) and both ends are now derived.
5. **The first build of the re-sample cost 2.9× per leg** (0.053 s → 0.156 s), from re-hashing the interpreter
   binary. Found by the cost probe, fixed by `tee:289` `if rp == identity["agent_interpreter_realpath"]:`, re-measured at 1.00×.
6. **The re-sample has an irreducible race** when the agent answers and exits at once: measured **1/20** under
   full-suite load (0/20 idle). It is now loud — stderr marker plus the early reading — and the coherence is pinned
   by `test:3452` `def test_resample_that_loses_the_race_is_loud_not_silent`. The reason goes to stderr and not
   into the record because
   `proofs/S0-01/check_acp_conformance.py` rejects a runtime-identity key-set change, and `write_errors` would flip
   the tee's exit code to 70.
7. **`/dev/full` needed one more change than the sweep row named.** Repointing the eight predicates alone does not
   fail a declaration test that hard-codes `/dev/full`; the predicates and the declaration now read one name
   (`test:60` `_DEV_FULL`), which is what makes R18 a kill.
8. **Pre-existing, NOT mine, reported only:** the real-leg corpus records `tee_sha256`
   `ed1c38f100af22cc8ae33ad6764f5e0a10e6fff71cd98c9507858ab5a878a3dd` while the repo's tee hashed
   `8dfdeb7f704d…` at the PIN — the two already disagreed before my change, so
   `check_acp_conformance.py`'s `_chk("tee_sha256", …)` cannot be satisfied by that corpus with any recent tee. I
   touched nothing there; the corpus is another lane's surface.

## SELF-ATTACK — the three most likely ways this change is wrong

1. **"The equality only looks strong; the derived facts are unfalsifiable."** True, and stated inside the test's own
   docstring: while the sha256 premise holds, every fact derived from `acp.rs` is a pure function of pinned bytes and
   cannot go red. What the equality adds is real and measured: the false-ORDER constant that passes the PIN
   (`2 passed`) fails here, because the sentence is now BUILT from the derived order and seconds rather than checked
   against a word list. The residual is that `expected_clause`'s `else` branch (wait-then-kill) is unreachable while
   `kill_line < wait_line` holds — no mutant can separate it, and I say so rather than claiming coverage.
2. **"The five reference sites are a hand-written list; site six is unguarded."** Also true. The list is enumerated
   by name at `test:3686-3695` `for fname in ("test_never_reading_client",`, so a false shutdown sentence added to a
   test docstring OUTSIDE those three names is caught only by the wrap-tolerant regex over both files
   (`test:3735` `assert not re.search`). I chose the named list over a file-wide docstring ban because a file-wide
   ban on the two-character-plus-space string would fire on legitimate prose: `test:1133` `5 s); the 30 s case is killed by` — and a ban on
   `killpg` fires on the AST pin's own docstring. The limit is written into the oracle
   test's docstring, not only into this report.
3. **"The census helper's branch assertions could be the wrong way round, and site 3 hides a real defect."** The
   three sites now state which branch they can produce, and two of them kill GRANDCHILD-UNKILLED. Site 3 cannot
   reach the kill for a structural reason I re-derived and re-measured (its grandchild is dead before the census for
   any lifetime, which is why `range(6000)` bought 16 s and nothing else). If that reasoning is wrong, the
   observable would be `_kill_own_grandchild(framedir) == "gone"` failing at `test:2788` — it passed 5 full-suite
   runs. The kill path itself is covered by sites 1 and 2 plus the four-path driver, not by site 3.

Two more I checked and could not break: the hardened `_run_tee` collector could have broken a legitimate run whose
agent produces no frames — `test:756` `_run_tee(tmp_path / "bt"` runs an agent that exits at once — the tee opens all four artifacts at
startup, so the files exist and the suite is green twice; and the bounded reader could have masked a real regression
by returning `None` where a frame was due — every call site asserts the line is present (`assert answer` at
`test:451` `no handshake line from the tee within 30 s`, and five siblings), so a missing handshake is louder.
