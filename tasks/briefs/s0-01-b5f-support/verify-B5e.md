# VERIFY-B5e — round-10 adversarial grade of lane B5e (S0-01 frame tee: symmetric drain, full SIGTERM window, structural pins)

**Grade venue:** `git archive 19799b17 | tar -x` copies. Shared tree: read-only git only, never modified.

## PREMISE

| item | value |
|---|---|
| PIN | `19799b17fc7d422ed0b5394d3751356f70102cd6` — `git cat-file -e` OK |
| `git rev-parse HEAD` at dispatch | `19799b17fc7d422ed0b5394d3751356f70102cd6` (HEAD **is** the PIN) |
| `git diff --stat 19799b17 HEAD -- <2 scope files>` | EMPTY (rc 0) |
| `proofs/S0-01/tools/frame_tee.py` | sha256 `061dd10c129b75ee4e56a5eb8a289b43c9d8bf40b1704f7ee18b3951db9e6ba7`, **466** lines — matches the brief |
| `tests/test_s0_01_frame_tee.py` | sha256 `82a3d1f9f7abdddaa8d5ac4abd46ab4f55d2745e5f3f526d7cff3ba24c52454e`, **2655** lines — matches the brief |
| worktree = PIN bytes | both files byte-identical at PIN and in the worktree (sha256 re-computed from `git show`) |
| interpreter | `/usr/local/bin/python3` — `Python 3.11.15 (main, Mar  3 2026, 09:26:23) [GCC 13.3.0]`, pytest 9.1.1 |
| collected | `93 tests collected in 0.21s` |
| `df -h /` at start | `/dev/vda 252G 25G 13G 66% /` |
| load average at start | `3.89, 3.71, 3.51` (another verifier's mutant drivers + lane D5h are live) |
| shared-tree dirty set at dispatch | lane D5h's three backend files. **By the end of the run the tree had moved** — HEAD `19799b17` → `e8fdfab`, dirty set now a checker lane's two files. Both B5e scope files byte-identical at the PIN, at `e8fdfab` and in the worktree, and `git status --porcelain`-clean on them at every check. See F-B5e-16. |
| grade venue | `git archive 19799b17 \| tar -x` copies under `…/scratchpad/vb10*`. Shared tree: read-only git only. |

## ITEM 1 — ROUND-9 FINDINGS F1-F16: CLOSURE, AND THE RED STATE THE LANE DID NOT RUN

### 1a. The lane's "RED STATE" line is an `-x` early-stop, reproduced exactly

The lane's report prints, under a heading "RED STATE (parent tee c227f8d + HEAD tests)":

```
1 failed, 53 passed in 20.81s  pytest-exit: 1
FAILED tests/test_s0_01_frame_tee.py::TestTeeStatus::test_grandchild_straggler_recorded
```

93 items are collected. 54 items is not the suite. Reproduced on my own c227f8d venue **with `-x`**:

```
$ cd <venue-c227f8d> && python3 -m pytest tests/test_s0_01_frame_tee.py -x -p no:cacheprovider -q -rf
FAILED tests/test_s0_01_frame_tee.py::TestTeeStatus::test_grandchild_straggler_recorded
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
1 failed, 53 passed in 20.62s          PYTEST_RC=1
```

Byte-for-byte the lane's shape (20.62 s vs 20.81 s). **The lane's red state is `pytest -x`: it stopped at the first
failure and reports 1 of the 10 tests that are actually red.** The lane's own brief said (F4) "a mutant table is a
measurement, not a prediction" — the same rule applies to a red-state line.

### 1b. The red state the lane should have pasted (no `-x`, full suite)

Same venue, lane's own baseline `c227f8d`:
```
10 failed, 83 passed in 163.20s          PYTEST_RC=1
FAILED …::TestTeeStatus::test_grandchild_straggler_recorded
FAILED …::TestTeeStatus::test_grandchild_never_closes_sigterm_required
FAILED …::TestStdinReaderDoneValue::test_stdin_reader_done_false_when_client_never_closes
FAILED …::TestLateFrameAfterAgentDeath::test_late_frame_after_agent_death_recorded[6]
FAILED …::TestLateFrameAfterAgentDeath::test_late_frame_after_agent_death_recorded[8]
FAILED …::TestLateFrameAfterAgentDeath::test_late_frame_after_agent_death_recorded[12]
FAILED …::TestStructuralPins::test_drain_loops_have_no_break_or_timeout
FAILED …::TestEarlySigterm::test_sigterm_during_sha256_produces_status
FAILED …::TestEarlySigterm::test_no_statement_between_signal_and_try
FAILED …::TestSigtermTerminatesAgent::test_sigterm_kills_agent_child
```

**`c227f8d` is also the WRONG baseline.** The tee's own history is
`ea8414f` (B5c, 473 lines) → `736bb94` (B5d, 476 lines) → `19799b1` (B5e, 466 lines). `c227f8d` is a non-tee commit whose
tee content is the **B5c** version — two generations back. Three of the ten reds above
(`test_late_frame_after_agent_death_recorded[6/8/12]`, `test_stdin_reader_done_false_when_client_never_closes`) are
**B5d's** regressions, not B5e's. The correct parent is `736bb94`:

```
<venue-736bb94> full suite, no -x:   6 failed, 87 passed in 170.35s   PYTEST_RC=1
FAILED …::TestTeeStatus::test_grandchild_straggler_recorded
FAILED …::TestTeeStatus::test_grandchild_never_closes_sigterm_required
FAILED …::TestStructuralPins::test_drain_loops_have_no_break_or_timeout
FAILED …::TestEarlySigterm::test_sigterm_during_sha256_produces_status
FAILED …::TestEarlySigterm::test_no_statement_between_signal_and_try
FAILED …::TestSigtermTerminatesAgent::test_sigterm_kills_agent_child
```

### 1c. Every NEW test against the parent tee — red or CONTROL

`git diff` of test `def` names, `0df17d6` (parent test file, 78 defs) → PIN (85 defs): **11 new defs**, 4 of them renames.
Selection sanity on the PIN venue first (a filter that matches nothing exits 0):
`11 passed, 82 deselected in 72.16s  PYTEST_RC=0`. Then the same 11 against tee `736bb94`:
`6 failed, 5 passed, 82 deselected in 73.70s  PYTEST_RC=1`.

| new test | on parent 736bb94 | classification |
|---|---|---|
| `test_grandchild_straggler_recorded` | **RED** (`assert 1 == 2`, recorded_a2c) | genuine regression test for F3 |
| `test_grandchild_never_closes_sigterm_required` | **RED** | genuine regression test for F3 |
| `test_drain_loops_have_no_break_or_timeout` | **RED** (parent has `stall_timeout`) | genuine + kills A2-t*/a2c-t* |
| `test_sigterm_during_sha256_produces_status` | **RED** | genuine regression test for F13 |
| `test_no_statement_between_signal_and_try` | **RED** | genuine regression test for F13 |
| `test_sigterm_kills_agent_child` | **RED** (`state S after 2 s`) | genuine regression test for F14 |
| `test_concurrent_main_thread_status_vs_pump` | GREEN | **CONTROL** — kills N4 + D3 only (see item 5) |
| `test_timeline_before_directional_in_pumps` | GREEN | **CONTROL** — kills N3 only (AST) |
| `test_grandchild_keeps_tee_alive` | GREEN | **CONTROL** (rename of `test_grandchild_does_not_stall_tee`); kills a2c-t0 only |
| `test_late_frame_agent_stdin_closed_before_handshake` | GREEN | **CONTROL** (F7 rename, no behaviour change) |
| `test_agent_stdin_closed_before_handshake_exit_code` | GREEN | **CONTROL** (F7 rename, no behaviour change) |

The lane's report labels the control rows "N/A (structural)" — that is the right *category* but the report never states
that a structural pin's entire value is the mutant it kills, and the lane **ran no mutants** (its own NOT_DONE says so).
Item 3 below is the first measurement.

### 1d. F1-F16 closure table (graded against the round-9 verdict, not the lane's summary)

| round-9 finding | lane claim | my verdict |
|---|---|---|
| **F1** (xfail tripwire never reaches the checker) | "lane A5g's, READ-ONLY, passes" | **CLOSED by A5g, out of B5e scope.** `test_sigterm_status_satisfies_check_tee_status` (T:2184) is green on the PIN and reaches the checker (it imports via the `sys.path` form). Not re-graded here. |
| **F2** (N4/D3/N3 survive) | new tests `test_concurrent_main_thread_status_vs_pump`, `test_timeline_before_directional_in_pumps` | **PARTLY CLOSED — measured, items 3+5.** N3 dies **deterministically** (AST pin). N4 dies **7 runs in 9**, D3 **5 in 9** — both survive the full suite on the other runs. The bar was "must die on a NAMED test". **BLOCKING — F-B5e-3.** |
| **F3** (a2c silent loss) | drain-to-EOF, `test_grandchild_straggler_recorded` | **CLOSED behaviourally** (red on the parent, green on the PIN; reproduced independently, item 4). The docstring's justification is **NOT** closed — see F-B5e-1. |
| **F4** (mutant table asserted, not measured) | "MUTANT TABLE: NOT run here" | **NOT CLOSED — repeated.** The lane again shipped a table of *expected* kills and, for the red state, an `-x` line. The verifier is again the first to measure. |
| **F5** (30 s c2a timeout survives) | `test_drain_loops_have_no_break_or_timeout` | **CLOSED — measured.** A2-t30 and a2c-t30 both die (item 3). |
| **F6** (gap sweep `[1,6,8]`) | `[1, 4, 6, 8, 12]` | **CLOSED.** `T:2045 @pytest.mark.parametrize("gap", [1, 4, 6, 8, 12])`; 5 params collected (93 = 85 defs + 8 extra params). |
| **F7** (misnamed reap tests) | renamed both | **CLOSED.** `test_late_frame_agent_stdin_closed_before_handshake`, `test_agent_stdin_closed_before_handshake_exit_code`. Both green on the parent = pure renames, correctly disclosed. |
| **F8** (no liveness in the never-closes test) | rewritten, 15 s liveness | **CLOSED.** T:1375-1437 gates on `stdin_reader_done is False and recorded_a2c >= 1`, sleeps 15 s, asserts `tee_proc.poll() is None` before SIGTERM. Red on `c227f8d`, green on the PIN. |
| **F9/F10** (invariant list unqualified) | qualified 7-item list in the report | **PARTLY CLOSED** — see item 6; the list is in the *report* only, not in any artifact A5g can consume, and item 6's negative controls expose one wording gap. |
| **F11** (S1 survives) | lag assertion in `test_sigkill_leaves_nonfinal_status` | **NOT CLOSED — measured.** S1 dies **1 run in 16** (6 %). The brief demanded the assertion in TWO tests; it landed in the one with a single SIGKILL sample, not in the 12-trial one. **BLOCKING — F-B5e-2.** |
| **F12** (12 unguarded Popen) | "25 call sites, all 25 guarded" | **CLOSED in substance, WRONG in count** — 27 AST call sites, all 27 guarded (item 8). |
| **F13** (SIGTERM startup window) | handler at :207, try at :208 | **CLOSED structurally** (item 2a: catching scope complete, AST-verified) **and behaviourally 12/12 + 6/6**. Two residual gaps, both ungated: a Popen hoisted above the install (F-B5e-5) and the `proc = None` pre-init (F-B5e-6); the test's stated mechanism is not the one that runs (F-B5e-8). |
| **F14** (agent orphan) | `proc.terminate()` + `test_sigterm_kills_agent_child` | **CLOSED — measured** (ORPHAN dies on the named test). |
| **F15** (12 empty trials) | `assert all(r and r["tl_c2a"] >= 100 …)` | **CLOSED.** Present at T:2038. |
| **F16** (cost) | median 0.0590 s, ratio ~1.02× | see item 9. |

## ITEM 2 — F13, THE FULL SIGTERM WINDOW

### 2a. Structure — reproduced by AST, not by eye

```
main() body has 23 statements.  signal.signal is body[21] at line 207.
body[22] is a Try at line 208.                       -> ZERO statements between install and try
try body spans lines 209..453.
statements AFTER the try in main.body: []            -> the try wraps EVERYTHING after the install
handlers: [('_Terminated', line 454)]
proc = None at line 122 (pre-init)
```

**AF-AP-58 catching scope: COMPLETE (SOLID).** Every free name the `except _Terminated:` path reads — transitively
through `_write_status` — is bound before the install:
`state`(:126) `_write_status`(:157) `lock`(:124) `seq`(:125) `status_lock`(:152) `_status_path`(:153)
`_status_tmp`(:154) `_status_write_failures`(:155) `proc`(:122), plus module-level `_utc_now`. Nothing the except path
reads is bound only inside the try. Verified by an AST reachability walk, not by reading.

### 2b. The two mutants the brief names — both die, on NAMED tests

| mutant | mutation | result | killer (named) |
|---|---|---|---|
| **INSTALL-LATE** | install + try moved below Popen and two sha256 reads (the OLD shape) | **KILLED** | `test_sigterm_during_sha256_produces_status` (`1 failed, 1 passed, 91 deselected in 0.46s`) |
| **GAP-1** | exactly one statement (`_gap = _sha256_file(...)`) between install and try | **KILLED** | BOTH — `test_no_statement_between_signal_and_try` AND `test_sigterm_during_sha256_produces_status` (`2 failed, 91 deselected in 3.05s`) |

Note the asymmetry: INSTALL-LATE is killed by the **behavioural** test only — the AST pin PASSES it, because install and
try are still adjacent, just lower down.

### 2c. Attacking the window test: is the TERM guaranteed to land after the install?

**YES, and structurally — not by timing.** `pgrep -P <tee_pid>` can only return a child once `subprocess.Popen`
(`frame_tee.py:209`) has forked. `signal.signal` is at `:207`. Therefore **the child cannot become visible before the
handler is installed**, and the test's TERM (sent only after the poll succeeds) cannot precede the install.
**Lower flake bound: 0.** This is a stronger property than the docstring's "the tee is in sha256 reads" claim, and the
test's docstring does not state it.

Measured over 12 instrumented runs (an instrumented copy of the PIN tee in the scratchpad printing monotonic marks at
`T_MAIN`/`T_INST`/`T_POPEN`/`T_SHA1`/`T_SHA2`/`T_SHA3`/`T_IDENT`/`T_INIT` and inside the handler at `T_SIG`) — see 2d.

### 2d. What the 234 MB entrypoint actually buys — measured

Standalone measurement on this box (load 0.45–1.20):
```
234 MB comment-line entrypoint:  write 0.179 s   sha256 0.635 s
```
But the whole test runs in **0.21 s**:
```
$ pytest -k test_sigterm_during_sha256_produces_status --durations=3
0.21s call  …::TestEarlySigterm::test_sigterm_during_sha256_produces_status
1 passed, 92 deselected in 0.25s
```
0.21 s < 0.179 + 0.635. **The tee never reaches the 234 MB sha256** — the TERM lands within ~2–5 ms of the fork, i.e.
during `readlink /proc/<pid>/exe` + the *interpreter* sha256 (`:217-218`), long before `_sha256_file(agent_realpath)`
at `:228`. The test's own docstring ("entrypoint >= 200 MB of comment lines (sha256 >= 0.3 s)" … "the tee is in sha256
reads") describes a region the test does not in fact reach on this box. The big file is not useless — it widens the
in-try region from ~80 ms to ~800 ms, which is real insurance on a loaded box — but the determinism comes from the
`pgrep -P` poll, not from the file size, and the report/docstring attribute it to the file.

### 2e. Landing-time distribution — 12 instrumented runs (load average 1.61 before and after)

An instrumented copy of the PIN tee (scratchpad only; the graded file untouched) printing monotonic marks at
`T_MAIN` (first statement of `main()`), `T_INST` (immediately after `signal.signal`), `T_POPEN`, `T_SHA1` (after the
interpreter sha256), `T_SHA2` (tee sha256), `T_SHA3` (the 234 MB agent sha256), `T_IDENT`, `T_INIT`, and `T_SIG`
(inside the handler). The parent harness reproduces the test exactly: 234 MB entrypoint, `pgrep -P` poll every 2 ms,
TERM the instant the child appears.

```
SUMMARY mode=poll n=12  rc={70: 12}  landed={'T_POPEN': 12}  status_present=12/12
spawn->child-visible ms: min 31.28  med 36.36  max 42.03
T_MAIN->T_SIG ms:        min  3.16  med  5.19  max 13.03
T_MAIN->T_INST ms:       min  0.07  med  0.08  max  0.11
runs that reached T_SHA3 (234 MB sha256 done): 0/12
```

Read this carefully:

* **The signal landed after `T_POPEN` in 12/12 runs and never before `T_INST`.** The install is at +0.08 ms; the earliest
  signal is at +3.16 ms — a 39× margin, and structurally the child cannot be visible before the fork at `:209`.
* **`T_SHA1` never even printed** — the tee dies inside `readlink("/proc/<pid>/exe")` + the interpreter sha256 at
  `:217-218`. **0/12 runs reach the 234 MB read.** The test's stated mechanism ("the tee is in sha256 reads" of the
  big entrypoint) is not the mechanism that runs.
* **Flake bound: 0/12 on this box; 0 by construction on the early side.** The late side is also safe: `updated_seq`
  stays 0 no matter how late the TERM lands, because the agent sleeps 30 s and no frame is ever sent. I could not
  produce a flake.

### 2f. TERM at t = 0 — the docstring's uncovered window, confirmed

```
SUMMARY mode=immediate n=12  rc={-15: 12}  landed={None: 12}  status_present=0/12
spawn_to_term_ms: 0.58 .. 0.64
```

**rc −15, no status file, 12/12.** The docstring **does** state it — `frame_tee.py:20-22`
("The only uncovered SIGTERM window is Python interpreter startup before the handler install (default disposition:
rc -15, no status file)") and the code comment at `:202-203`. Quantitatively the claim is accurate: the uncovered
region is ≈ 25–30 ms of interpreter startup plus **0.08 ms** of `main()` prologue (four env checks, `os.makedirs`,
the closure definitions) — 0.3 % of the window. Caveat, stated for completeness: `os.makedirs(framedir)` at `:117`
is a real syscall inside that prologue and could block arbitrarily on a hung filesystem; the docstring's
"interpreter startup" wording does not cover that case. INFO, not blocking. **No test covers the t=0 window** — it is
described in prose only.

## ITEM 3 — THE MUTANT TABLE (a MEASUREMENT; the lane ran none)

Runner: `…/scratchpad/mutb10.py` + `mutb10b.py`, written for this round because mut8/mut9's anchors are aimed at the
B5d tee. Venue = a `git archive` copy of the PIN. Protocol per mutant: restore both files from a pristine copy →
apply → `ast.parse` syntax check → run the **named** killer(s) → if the named run is green, escalate to the **full
suite with no `-x`** → restore. `sha256` of both scope files re-asserted after every mutant; the shared tree's two
scope files re-checked `git status --porcelain`-clean after each batch (they are: I never touched them).

**Anchor audit of the round-9 59-mutant set:** mut9's `DRAIN_OLD`, `FD_STATUS`, `PIPE_STATUS`, `WRITES` and `FWD_BLOCK`
anchors are all keyed to B5d's indentation and to the deleted `stall_timeout` block. In the B5e tee both pumps sit at
the *same* indentation (`def`→`try`→loop→`with lock:`→24 spaces), so mut9's separate `FD_*`/`PIPE_*` anchors are wrong
by construction (one matches twice, the other zero times). I therefore did **not** replay mut9 verbatim; I re-anchored
the mutants the acceptance bar names and added six of my own. **Stated NOT done:** the ~40 mut8 mutants that are
neither in the acceptance bar nor touched by B5e's diff were not re-run this round (they were all KILLED in round 9
against code B5e does not change; re-running them would have cost ~2 h of contended box for no new information).

| id | mutation | result | killer (NAMED) |
|---|---|---|---|
| **INSTALL-LATE** | install + try below Popen + 2 sha256 (OLD shape) | **KILLED** | `test_sigterm_during_sha256_produces_status` |
| **GAP-1** | one statement between `signal.signal` and `try:` | **KILLED** | `test_no_statement_between_signal_and_try` **and** `test_sigterm_during_sha256_produces_status` |
| **EXCEPT-WRONG** | `except Exception:` instead of `except _Terminated:` | **KILLED** | `test_sigterm_writes_status_and_exits_70`, `test_sigterm_during_sha256_produces_status` |
| **EXIT-0** | `os._exit(0)` in the handler | **KILLED** | same two |
| **STATUS-FINAL-TRUE** | `_write_status(final=True)` on the TERM write | **KILLED** | same two |
| **ERR-MISSING** | no `"terminated: SIGTERM"` append | **KILLED** | same two |
| **ORPHAN** | drop `proc.terminate()` | **KILLED** | `test_sigterm_kills_agent_child` |
| **TRY-SHRINK2** | try covers ONLY Popen; sha256/identity/pumps outside every catcher | **KILLED** | `test_sigterm_writes_status_and_exits_70` + 1 |
| **A2-t0 / t1 / t5 / t30** | c2a drain stall timeout 0/1/5/30 s | **KILLED ×4** | `test_drain_loops_have_no_break_or_timeout` (structural) |
| **a2c-t0** | a2c drain stall timeout 0 s | **KILLED** | `test_grandchild_straggler_recorded` **and** `test_drain_loops_have_no_break_or_timeout` |
| **a2c-t5** | a2c drain stall timeout 5 s (the pre-B5e shape) | **KILLED** | both, as above |
| **a2c-t30** | a2c drain stall timeout 30 s | **KILLED** | `test_drain_loops_have_no_break_or_timeout` **only** (`1 failed, 1 passed`) — the behavioural straggler test PASSES it |
| **A2C-DELETE** | delete the a2c drain loop | **KILLED** | both |
| **A2C-WRONG-THREAD** | a2c drain loop waits on `ti` instead of `to` | **KILLED** | `test_grandchild_straggler_recorded` **only** — the structural pin PASSES it (`1 failed, 1 passed`) |
| **N3** | swap timeline/directional write order, both pumps | **KILLED** | `test_timeline_before_directional_in_pumps` (structural, deterministic) |
| **N4** | status snapshot outside the timeline lock | **FLAKY KILL** — see item 5 | `test_concurrent_main_thread_status_vs_pump` |
| **D3** | drop `status_lock` | **FLAKY KILL** — see item 5 | `test_concurrent_main_thread_status_vs_pump` |
| **S1** | status written BEFORE the timeline line (both pumps) | **SURVIVED 5/5 named + full suite `93 passed`** | none |
| **INSTALL-LATE-B** | Popen hoisted above the install; install+try stay adjacent | **SURVIVED** (`93 passed in 169.71s`) | none |
| **NO-PREINIT** | drop `proc = None` (AF-AP-58's own requirement) | **SURVIVED** (`93 passed in 170.68s`) | none |
| **TRY-SHRINK** (mine, malformed) | second catcher retained | SURVIVED — **EQUIVALENT by construction**, superseded by TRY-SHRINK2 |
| **DRAIN-ORDER** | c2a drain loop before the a2c drain loop | SURVIVED — **EQUIVALENT**: both loops are pure waits at 10 Hz; the pumps drain in their own threads regardless of the wait order, and `tl.close()` follows both. |
| **PUMP-TIMEOUT** | 5 s no-data `select()` timeout INSIDE `pump_pipe`'s read loop — the loss cliff returns without touching either drain loop | **KILLED** | `test_grandchild_straggler_recorded` **and** `test_grandchild_never_closes_sigterm_required` (`2 failed, 1 passed, 90 deselected in 20.53s`); the structural pin PASSES it, as it must |

```
TOTAL 26 distinct mutants over 63 runner pytest invocations
  KILLED-BY-NAMED   19   INSTALL-LATE GAP-1 EXCEPT-WRONG EXIT-0 STATUS-FINAL-TRUE ERR-MISSING ORPHAN
                         TRY-SHRINK2 A2-t0 A2-t1 A2-t5 A2-t30 a2c-t0 a2c-t5 a2c-t30 A2C-DELETE
                         A2C-WRONG-THREAD N3 PUMP-TIMEOUT
  FLAKY KILL         2   N4 (7/9)  D3 (5/9)                        -> item 5, BLOCKING
  SURVIVED (real)    3   S1 (1/16) INSTALL-LATE-B NO-PREINIT       -> F-B5e-2/5/6
  EQUIVALENT         2   TRY-SHRINK (malformed, superseded)  DRAIN-ORDER
  PATCH-FAILED       0
```

## ITEM 7 — THE THREE LINT-DELTA SCREEN HITS, LINE BY LINE

`scripts/lint_delta.py` runs `AP_SCREEN` (imported from `.claude/hooks/edit-snapshot.py`) **over ADDED lines only**.
I re-ran the exact regexes over the B5e diff (`git diff -U0 0df17d6 19799b1`), mapping each `+` line to its new line
number. Thirteen ADDED lines hit, plus one in the tee:

### AF-AP-40 — presence-gated check (regex `if <expr>.(exists|is_file|is_dir)\(\)\s*(:|and)`)

| line | site | ruling |
|---|---|---|
| `T:1807` | `test_sigkill_leaves_nonfinal_status`: `if tl_path.exists():` before computing `tl_last_seq` | **FALSE POSITIVE.** `tl_last_seq` is pre-initialised to 0, and the very next statement is `assert 0 <= tl_last_seq - status["updated_seq"] <= 1` with `updated_seq > 0` already asserted. An absent timeline makes the lag **negative** and the assertion **fires**. Fail-closed. |
| `T:2429` | `test_concurrent_main_thread_status_vs_pump`: `if status_path.exists():` inside the spin loop | **FALSE POSITIVE.** `reads` increments only inside the gate and the test ends with `assert reads >= 10000`. A never-appearing status file gives `reads == 0` → red. |
| `T:2610` | `test_sigterm_kills_agent_child`: `if id_path.exists():` waiting for `runtime-identity.json` | **FALSE POSITIVE** (loud, but ugly). `identity` is never pre-bound, so a timeout raises `NameError` at `agent_pid = identity["agent_child_pid"]`. Fails loud as an *error*, not an assertion. Cosmetic fix: pre-bind `identity = None` and `assert identity is not None, "runtime-identity.json never appeared"`. |
| `T:1165` | `test_initial_status_before_first_frame` | **FALSE POSITIVE.** `initial_status = None` pre-bound and `assert initial_status is not None, "tee-status.json never appeared before first frame"` at `T:1182`. Exactly the right shape. |
| `T:1505` | `test_sigterm_writes_status_and_exits_70` | **FALSE POSITIVE.** After the loop the test unconditionally reads the status file; absence → `FileNotFoundError`. |
| `T:1777` | `test_sigkill_leaves_nonfinal_status` (the `forwarded_a2c >= 5` wait) | **FALSE POSITIVE**, same reason — the post-loop `json.loads(status_path.read_text())` plus `assert status["updated_seq"] > 0`. |
| `T:501` | `test_grandchild_keeps_tee_alive` (`recorded_a2c >= 1` wait) | **REAL, low.** The wait is success-only. Failing scenario: the a2c pump records nothing within 10 s → the loop falls through → the test's only assertions are `tee_proc.poll() is None` at ~13 s and `returncode == 70`, both of which a tee that never recorded anything still satisfies. The test would pass having proved nothing about the grandchild. Redundantly covered by `test_grandchild_straggler_recorded`, so severity is low. *Fix:* `assert s is not None and s["recorded_a2c"] >= 1` after the loop. |
| `T:857` | `test_never_reading_client` (`recorded_a2c >= 1` wait) | **REAL, low**, same shape. The final assertions (`rc 70`, `write_errors == ["terminated: SIGTERM"]`) hold whether or not any a2c frame was ever recorded, so the "pump blocked on a full pipe" premise is unverified. *Fix:* assert `recorded_a2c >= 1` before the SIGTERM. |
| `T:1021` | `test_grandchild_never_closes_sigterm_required` | **REAL, low**, same shape. |
| `T:1566` | `test_sigterm_no_deadlock_under_contention` (`updated_seq >= 100` wait) | **REAL — the sharpest of the four.** The test exists to prove SIGTERM does not deadlock *under contention*. If the 15 s wait times out with `updated_seq == 0`, the test SIGTERMs an idle tee and still asserts only `wait(timeout=5)` + `returncode == 70`: the contention premise silently evaporates and the test stays green. Any regression that slows the pumps below ~7 frames/s makes this test vacuous. *Demonstrated:* setting the threshold to `>= 10**9` on a scratch copy leaves the test **GREEN** (`1 passed in 15.19s`). *Fix — the flag form, RUN both ways (see F-B5e-7; the value form I first proposed does NOT kill):* `loaded = False` above the loop, `loaded = True` on the break path, `assert loaded, "no contention: the wait for updated_seq >= 100 timed out"` after it. |

### AF-AP-45 — liveness without the STATE column

| line | site | ruling |
|---|---|---|
| `T:2534` | `test_sigterm_during_sha256_produces_status`: `if os.path.exists("/proc/%d/stat" % child_pid):` | **FALSE POSITIVE.** The regex fires on the `/proc` path, but this is the *state-aware* form the AP row asks for: the very next lines read field 3 and require `Z`, treating absence as gone. The screen cannot see that. |
| `T:2630` | `test_sigterm_kills_agent_child` loop: `if not os.path.exists(...)` | **FALSE POSITIVE**, same reason. |
| `T:2640` | `test_sigterm_kills_agent_child` final check | **FALSE POSITIVE**, same reason. |

**All three AF-AP-45 hits are false positives, and the lane's fix is exactly what AF-AP-45 demands.** The screen's regex
`(exists|isdir|is_dir)\(\s*f?["'][^"'\n]*/proc/` has no negative lookahead for a following `stat` field read, so a
correct implementation still trips it. Suggested (out of B5e's boundary, coordinator item): extend the AF-AP-45 regex
with a same-statement-block exclusion, or accept these as known-good and annotate.

### AF-AP-58 — the handler install itself (`frame_tee.py:207`)

**Catching scope is COMPLETE (SOLID).** See item 2a: install at `:207`, `Try` at `:208` with zero statements between,
try body `209..453`, **zero statements after the try in `main()`**, `except _Terminated` at `:454`, and every free name
the except path reads transitively (`state`, `_write_status`, `lock`, `seq`, `status_lock`, `_status_path`,
`_status_tmp`, `_status_write_failures`, `proc`) is bound *before* the install. Verified by an AST reachability walk.
The one gap AF-AP-58's own remedy names but nothing tests: the `proc = None` pre-init is **ungated** — mutant
NO-PREINIT survives the full suite (item 3).

## ITEM 5 — THE N4/D3 KILLER IS PROBABILISTIC, AND S1 IS ESSENTIALLY UNGATED

The brief asks whether `test_concurrent_main_thread_status_vs_pump` actually FAILS under N4 and D3, "over 3 runs each".
I ran nine each (and sixteen of S1). Each run is the named killer only, full output, no `-x`; the test's own spin loop
runs its full 45 s deadline every time, so wall-clock is constant at ~45.2 s and is not a signal.

| mutant | runs | KILLED | SURVIVED | kill rate | box load during the runs |
|---|---|---|---|---|---|
| **N4** (`with lock:` → `if True:` at `frame_tee.py:162`) | 9 | 7 | **2** | **78 %** | 0.8 → 3.4 |
| **D3** (`with status_lock:` → `if True:` at `frame_tee.py:184`) | 9 | 5 | **4** | **56 %** | 0.8 → 3.4 |
| **S1** (status published before the timeline write, both pumps) | 16 | 1 | **15** | **6 %** | 0.8 → 3.4 |

Raw lines (the runner's own output, three independent batches):
```
batch A:  N4  KILLED-BY-NAMED  1 failed, 92 deselected in 45.21s
          D3  SURVIVED         1 passed, 92 deselected in 45.13s   -> full suite 93 passed in 170.48s
          S1  SURVIVED         2 passed, 91 deselected in  7.20s   -> full suite 93 passed in 172.02s
batch B:  D3  rep1..3          KILLED, KILLED, KILLED
          N4  rep1..3          SURVIVED, SURVIVED, KILLED
          S1  rep1..5          SURVIVED ×5
batch C:  D3  rep1..5          SURVIVED, KILLED, KILLED, SURVIVED, SURVIVED
          N4  rep1..5          KILLED ×5
          S1  rep1..10         KILLED ×1, SURVIVED ×9
```

**The lane brief's acceptance bar was "Every one of N3, N4, D3, S1, A2-t30 must die on a NAMED test, full suite, no `-x`."**
Measured on this box: N3 ✔ deterministic (AST), A2-t30 ✔ deterministic (AST), **N4 ✘ 78 %**, **D3 ✘ 56 %**,
**S1 ✘ 6 %**. Round-9 **F2** and **F11** are therefore **not closed** — they are *mostly* closed for N4/D3 and
essentially open for S1.

**Positive control (the test on the unmutated PIN):** in every clean run the assertion set is met —
`reads >= 10000`, `torn == 0`, `seq_violations == 0`; the test passes in all 11 of my clean executions
(the 11-new-test run, four full-suite runs, plus the escalation runs of the equivalent mutants).

### Why S1 is 6 % and not ~60 % — the mechanism, from primary source

The lane brief demanded the lag assertion **in two tests**:
> "(d) in `test_sigkill_leaves_nonfinal_status` **and** `test_directional_trails_timeline_after_sigkill` assert
> `0 <= timeline_last_seq - status["updated_seq"] <= 1`"

It landed in **one**. `test_sigkill_leaves_nonfinal_status` (`T:1741`) has it at `T:1813-1815` — **one SIGKILL, one
sample**. `test_directional_trails_timeline_after_sigkill` (`T:1925`) runs **12** SIGKILL trials with spread kill
instants (`kill_delay = 0.15 + trial * 0.05`) and is the natural home for it — but it never reads `tee-status.json`
at all; its only assertions are `dir_c2a <= tl_c2a`, `dir_a2c <= tl_a2c`, `len(results) == 12` and the F15 `tl_c2a >= 100`
guard. S1's signature (status one seq AHEAD of the timeline) is therefore sampled once per suite run.

### 5b. Vacuity demo for the AF-AP-40 hit at `T:1566` (reproduced, not argued)

On a scratch copy I changed only `T:1569` `if s.get("updated_seq", 0) >= 100:` → `>= 10**9`, i.e. made the contention
precondition unreachable:
```
1 passed, 92 deselected in 15.19s      (15.01s call — the full wait timeout, then SIGTERM)
```
The test is **green with its precondition never met**. Test file restored byte-identical
(`sha256 82a3d1f9f7abddda…`) after the demo.

---

## ITEM 4 — SYMMETRIC DRAIN (F3), AND WHERE ITS SAFETY ARGUMENT COMES FROM

### 4a. Straggler at 2 / 6 / 9 s — red on the parent, green on the PIN, reproduced independently

My own probe (not the suite): an agent whose grandchild inherits stdout, writes one `late_gc` frame N s after the
agent exits, then closes. Interpreter 3.11.15, load average 2.3–2.5.

```
PIN 19799b1 (466 lines)      delay 2  rc 0 wall 2.18  late_in_timeline true  late_in_a2c true  rec_a2c 2 fwd_a2c 2 drained true write_errors [] exit_code 0
PIN 19799b1                  delay 6  rc 0 wall 6.14  late_in_timeline true  late_in_a2c true  rec_a2c 2 fwd_a2c 2 drained true write_errors [] exit_code 0
PIN 19799b1                  delay 9  rc 0 wall 9.12  late_in_timeline true  late_in_a2c true  rec_a2c 2 fwd_a2c 2 drained true write_errors [] exit_code 0
PARENT 736bb94 (476, B5d)    delay 2  rc 0 wall 2.22  late_in_timeline true  late_in_a2c true  rec_a2c 2
PARENT 736bb94               delay 6  rc 0 wall 5.13  late_in_timeline FALSE late_in_a2c FALSE rec_a2c 1  drained true write_errors [] exit_code 0   <-- SILENT LOSS
PARENT 736bb94               delay 9  rc 0 wall 5.13  late_in_timeline FALSE late_in_a2c FALSE rec_a2c 1  drained true write_errors [] exit_code 0   <-- SILENT LOSS
GRANDPARENT c227f8d (473,B5c) delay 6/9: identical silent loss
```
**The AF-AP-53 shape is gone.** (Correction of my own process: my first parent run reported "recorded" at 6 s — I had
overwritten that venue's tee with the PIN tee an hour earlier for an unrelated `--durations` measurement. Caught,
venue restored from `git show 736bb94:` and re-verified by sha256 `3fc846ceaf4b687b`, results above are the re-run.)

### 4b. Grandchild that never closes → tee alive at 15 s → SIGTERM → rc 70 (reproduced)

```
{"alive_at_15s": true,
 "proc_state_samples": [[11.0,"S",null],[12.0,"S",null],[13.0,"S",null],[14.0,"S",null],[15.0,"S",null],[16.0,"S",null]],
 "rc": 70, "secs_after_term": 0.004, "final": false,
 "write_errors": ["terminated: SIGTERM"], "exit_code": null, "stdin_reader_done": true}
```
Liveness read from `/proc/<pid>/stat` field 3 (state `S`), not from output. The tee answers SIGTERM in 4 ms.

### 4c. **The docstring's justification is FALSE at the pinned commit — F-B5e-1**

`frame_tee.py:16-20`:
> "A client that never closes (c2a) or a grandchild that holds the agent's stdout (a2c) keeps the tee alive; that
> is buzz-acp's shutdown responsibility (**it TERMs/KILLs the group**), and the SIGTERM path covers it."

Re-derived from primary source at the pinned commit
`buzz @ 1c8321cd08feb597f8bcff5195c21148fb3e98ed` (`upstream.lock.yaml:16-19`), file
`crates/buzz-acp/src/acp.rs` (fetched, 5030 lines, sha256 `44e82861763694d2b82d02b15ee100ffd6c78874a2b2282865e6656c539c38f1`):

```rust
// acp.rs:2314-2328
/// Send SIGKILL to an entire process group. Returns `true` if the signal was sent.
fn kill_process_group(pid: u32) -> bool {
    use nix::sys::signal::{killpg, Signal};
    killpg(Pid::from_raw(pid as i32), Signal::SIGKILL).is_ok()
}

// acp.rs:421-444  AcpClient::shutdown
match self.child.id() {
    Some(pid) if kill_process_group(pid) => {}
    _ => { let _ = self.child.start_kill(); }        // start_kill() = SIGKILL, per :419
}
// "Bounded wait: if the child doesn't exit within 5s after SIGKILL, give up"
```
`grep -c SIGTERM crates/buzz-acp/src/acp.rs` → **0**. `grep -c SIGKILL` → **8**.

**buzz-acp never sends SIGTERM. It sends SIGKILL to the process group, then waits 5 s.** SIGKILL cannot be handled,
so the tee's `_Terminated` path — rc 70, non-final status, `write_errors ["terminated: SIGTERM"]` — **does not fire on
a buzz-acp shutdown at all**. This repo's own incident log already recorded the same reading
(`docs/INCIDENT-LOG.md:36`: "the pinned buzz-acp spawns its agent in its own process group and SIGKILLs the whole
group at shutdown, bounded wait 5 s (`crates/buzz-acp/src/acp.rs:417-442`, `:519`). SIGKILL cannot be handled, so an
exit-time status file is unsatisfiable on every leg") — that reading is the entire reason ruling **A21d** exists.

Consequence for this lane's contract: removing the a2c stall timeout is defensible on its merits (drain-to-EOF is the
right contract; the loss cliff is gone), but the *bound* the docstring names is not the bound that exists. A tee wedged
by a grandchild that never closes is **SIGKILLed at +5 s** with a running (non-final) status and **no reason recorded** —
not TERMed with `["terminated: SIGTERM"]`. Two committed artifacts now assert a story the pinned upstream contradicts:
the tee docstring `:16-20` and the comments at `:416-418` / `:422-424`, plus the docstrings of
`test_never_reading_client` ("SIGTERM is required (buzz-acp's responsibility)"),
`test_grandchild_never_closes_sigterm_required` and `test_stdin_reader_done_false_when_client_never_closes`.

---

## ITEM 6 — THE SEVEN QUALIFIED INVARIANTS: ONE POSITIVE AND ONE NEGATIVE EACH

All on the PIN tee, my own probes, load average 2.3–2.6.

**Positive run** — 6 000-frame bidirectional load (client streams, agent echoes), one spinning reader:
```
{"reads": 131982, "torn": 0, "inv1_violations": 0, "inv3_c2a_violations": 0, "inv3_a2c_violations": 0,
 "running_snapshots": 131907, "of_which_drained_false": 131878,
 "final": true, "final_fwd_eq_rec": true, "inv5_dir_le_tl": true, "inv7_lag_final": 0, "rc": 0, "write_errors": []}
```

| # | invariant as the lane states it | positive | negative (the qualification's necessity) | verdict |
|---|---|---|---|---|
| 1 | `updated_seq == recorded_c2a + recorded_a2c` | **0 violations in 131 982 live reads** | N4 mutant breaks it (item 3/5) | **HOLDS, unqualified** |
| 2 | `timeline_last_seq - updated_seq in {0,1}` — **frozen leg only** | SIGSTOP-frozen, 60 samples: `{0: 32, 1: 28}`, **0 outside {0,1}** | LIVE non-atomic two-file read, 60 samples: lag 0..**4**, **26/60 outside {0,1}** | **HOLDS as qualified; the qualification is NECESSARY** |
| 3 | `recorded_<d> - forwarded_<d> in {0,1}` — **only while no `forward <d>:` error is recorded** | 0 violations in 131 982 reads on a clean leg | forward-broken leg: `recorded_c2a 9 / forwarded_c2a 1`, **deficit 8**, `write_errors ["forward c2a: BrokenPipeError"]` | **HOLDS as qualified; unqualified form is FALSE** |
| 4 | `forwarded_<d> == recorded_<d>` on final — same qualification | clean final: `final_fwd_eq_rec true` | same broken leg: `final: true, drained: false, forwarded 1 != recorded 9, exit_code 70, rc 70` | **HOLDS as qualified; unqualified form is FALSE** |
| 5 | directional count ≤ timeline count, both directions | `inv5_dir_le_tl true`; the suite's 12-trial SIGKILL test asserts it per trial | N3 mutant breaks it and dies deterministically | **HOLDS** |
| 6 | running snapshots normally carry `drained: false` | **131 878 / 131 907 = 99.98 %** of running snapshots have `drained: false` | the 0.02 % with `drained: true` are the idle instants between frames | **HOLDS; "normally" is an understatement — it is the rule** |
| 7 | `updated_seq` is never ahead of the timeline | `inv7_lag_final = 0`; lag ≥ 0 on all frozen samples | the S1 mutant produces lag = −1 — **and escapes 15 of 16 runs (item 5)** | **HOLDS in the code; the TEST for it is 6 % effective** |

Two wording gaps worth fixing before this list is handed to the checker lane (A5g):

* **Invariant 2's qualifier says "frozen leg" but the checker reads a leg that is *finished*, not frozen.** A finished
  leg is a special case of frozen, so the rule is safe — but a *running* leg read live (which the A21d running arm does
  when the coordinator samples a live tee) is **not** bounded: I measured lag 4. State it as "a leg whose tee is
  stopped or exited", not "frozen".
* **Invariant 6 says running snapshots "normally" carry `drained: false`.** "Normally" is not a rule a checker can
  encode. The measured truth is: a running snapshot has `drained: false` whenever any frame is in flight, which is
  essentially always under load, and `drained: true` only in the idle gaps. A checker must therefore **not** require
  `drained` on a running snapshot at all — which is what A5g's split already does.

---

## ITEM 9 — COST (F16)

Shape: the 11-frame real-leg shape (3 c2a in, 8 a2c out), full tee spawn→exit wall clock, 15 reps per batch, three
independent batches. **Load average 1.69 before the first batch and 1.72 after the last** (another verifier's mutant
drivers are live on this box; this is the quietest window I had).

```
COST {"reps": 15, "median": 0.0571, "min": 0.0541, "max": 0.1616}
COST {"reps": 15, "median": 0.0543, "min": 0.0523, "max": 0.1550}
COST {"reps": 15, "median": 0.0568, "min": 0.0519, "max": 0.1618}
```

Round-6 baseline 0.058–0.060 s. Median ratio **0.90×–0.98×** — the B5e tee is marginally *cheaper* than the baseline,
comfortably inside the 2× bar. The lane reported median 0.0590 s / ~1.02× at load 2.54; my three medians bracket that.
The `max` outlier in each batch is the first rep (cold page cache for the agent script). **F16: MET.**

## ITEM 10 — INTERPRETERS

| interpreter | present | pytest | what I ran |
|---|---|---|---|
| **3.11.15** (`/usr/local/bin/python3`, the gate interpreter) | yes | 9.1.1 | everything in this report |
| **3.12.3** (`/usr/bin/python3.12`, **CI's** interpreter — `.github/workflows/stage0-ci.yml:17,33,51,68` `python-version: '3.12'`) | yes | **NOT installed** | see below |
| 3.13.12 | yes | not installed | AST-pin logic only |

**Could not reproduce on 3.12: the pytest suite itself** (`import pytest` → ModuleNotFoundError; no network install
attempted). **Did reproduce on 3.12, standalone:**

1. **All three AST structural pins**, re-implemented verbatim against the PIN tee and run under 3.11 / 3.12 / 3.13 —
   identical results on all three (`drain_loops_count == 2`, both loop bodies clean, `pump_fd tl(272) < df(277)`,
   `pump_pipe tl(358) < df(363)`, `signal.signal` at `main.body[21]`, next statement `Try`). **The pins are not
   3.11-specific.**
2. **The tee's own behaviour under 3.12**: F3 straggler probe → PIN records at 2/6/9 s, parent `736bb94` silently
   loses at 6/9 s (identical to 3.11).
3. **The SIGTERM window under 3.12**: 6/6 `rc 70`, status present, signal landed after `T_POPEN` every time,
   `T_MAIN→T_INST` 0.07–0.11 ms, 0/6 reached the 234 MB sha256.
4. **TERM at t=0 under 3.12**: 6/6 `rc −15`, no status.

**Deliberately NOT run (stated, not skipped):** the PC leg (`scripts/pc_suite.sh`, 8 xdist workers) — the venue where
the round-8 20-minute pipe deadlock appeared. `.pc-bridge.env` exists but is dated **2026-09-06** (yesterday, 128 bytes,
`PC_BRIDGE_URL` + `PC_BRIDGE_TOKEN`); no BRIDGE READY banner was pasted for this session, and my brief forbids outward
actions — running commands on the owner's PC is one. I did not touch it. Two of my findings (item 8's process leak, item 5's race rates) are venue-sensitive and would read differently under
8 parallel workers on 12 cores. This is a **sandbox-only, single-worker grade**.

---

## ITEM 8 — POPEN CENSUS, CLEANUP, AND WHAT ACTUALLY SURVIVES A SUITE RUN

### 8a. Census (AST, not grep)

My census binds each `Popen(...)` assignment to its variable and then asks whether the enclosing function has a
`try` whose **`finally` kills that exact variable**:

```
AST Popen call sites total: 27  (all name-bound)
  guarded by a finally that kills THAT variable: 27 ; unguarded: 0
raw textual 'Popen(' occurrences (incl. agent source strings): 31
  => inside string literals (grandchild spawns in agent source): 4
```

**All 27 are guarded** — F12 is substantively closed, and closed better than claimed. **The lane's count is wrong:**
its report says "25 `Popen(` call sites in the test file. All 25 guarded." 25 is the round-9 verdict's number
(23 test spawns + 2 in-string), carried over rather than re-measured; B5e added two more test spawns and two more
in-string grandchild spawns. AF-AP-37 class ("counts pasted, never typed").

### 8b. Leaked processes after the suite — measured, not asserted

```
--- census PRE ---                                    (none)          orphans(ppid==1): 0
=== IDLE SUITE RUN 1 ===  93 passed in 170.36s  PYTEST_RC=0
--- census POST-RUN-1 ---  17601  1  Z  0  [big_agent.py] <defunct>   orphans(ppid==1): 0
=== IDLE SUITE RUN 2 ===  93 passed in 169.63s  PYTEST_RC=0
--- census POST-RUN-2 ---  18730  1  Z  0  [big_agent.py] <defunct>   orphans(ppid==1): 0
--- census FINAL (+130 s) ---                          (none)         orphans(ppid==1): 0
```
**Zero live leaks after the suite.** The single post-run entry each time is the SIGTERMed 234 MB agent in state `Z`,
reparented to init and reaped within seconds (the +130 s census is clean). Counted correctly as gone per AF-AP-45.

**But there is an unowned-lifetime class DURING the run.** A mid-suite census I took at 14:29 caught:
```
5481     1  S   23  /usr/local/bin/python3 -c import time; time.sleep(120)
```
ppid **1** — a grandchild spawned by the fixture agent of `test_grandchild_never_closes_sigterm_required` (`T:990`),
orphaned when the tee was killed, alive for its full 120 s. Nothing in any test's `finally` kills it; it self-expires.
The same applies to `test_grandchild_keeps_tee_alive` (30 s, `T:468`) and
`test_concurrent_main_thread_status_vs_pump` (a 3000-frame/30 s streamer, `T:2381-2387`). Under `pytest -n 8` on the PC
that is up to eight concurrent orphan sets holding pipe fds. The lane brief's boundary says "every spawned tee/agent is
killed in `finally`"; the grandchildren are not.

### 8c. Disk and tmp_path hygiene

`df -h /` 25G used / 13G avail / 67 % at the end (66 % at the start; my venues + mutant runs are ~1 GB, the 234 MB
entrypoint is written once per suite run under `--basetemp` and removed with it). The only file the suite writes inside
the venue tree is `tests/__pycache__/…pyc`; nothing under `proofs/` or `tests/` is modified. Both scope files
re-hash to the PIN values after every mutant batch.

---

## GATE LINES (all mine, on a `git archive` copy of the PIN, no xdist)

```
pyflakes proofs/S0-01/tools/frame_tee.py tests/test_s0_01_frame_tee.py        -> rc 0
collected                                                                      -> 93 tests collected in 0.21s
def test_ count                                                                -> 85   (93 items = 85 defs + 8 parametrised)

idle 1 (load 1.32 before):   93 passed in 170.36s (0:02:50)   PYTEST_RC=0
idle 2 (load 1.83 before):   93 passed in 169.63s (0:02:49)   PYTEST_RC=0
   (+4 more full-suite runs at 169.71 / 170.53 / 170.48 / 172.02 / 170.68 / 170.39 s inside the mutant escalations,
    all "93 passed" on EQUIVALENT or SURVIVING mutants)

RED, true parent tee 736bb94 + PIN tests, no -x:      6 failed, 87 passed in 170.35s   PYTEST_RC=1
RED, lane's baseline c227f8d + PIN tests, no -x:     10 failed, 83 passed in 163.20s   PYTEST_RC=1
RED, lane's baseline c227f8d + PIN tests, WITH -x:    1 failed, 53 passed in  20.62s   PYTEST_RC=1   <- the lane's line

grep startswith in the test file          -> 0
grep '>= 1' on write_errors               -> 0
grep stall_timeout in the tee             -> 0
```

The lane's own two idle runs (`93 passed in 175.67s` / `169.69s`) reproduce.

---

## FINDINGS

**F-B5e-1 [BLOCKING] SOLID — the docstring's justification for removing the a2c stall timeout is false at the pinned
commit: buzz-acp SIGKILLs, it never SIGTERMs.**
`proofs/S0-01/tools/frame_tee.py:16-20` (also the in-code comments at `:416-418` and `:422-424`, and the docstrings of
`tests/test_s0_01_frame_tee.py:817-820`, `:978-982`, `:1375-1379`).
*Observed vs expected:* the tee says "that is buzz-acp's shutdown responsibility (it **TERMs**/KILLs the group), and the
SIGTERM path covers it". Primary source at the pin (`upstream.lock.yaml:16-19`, buzz `1c8321cd08feb597f8bcff5195c21148fb3e98ed`,
`crates/buzz-acp/src/acp.rs`, fetched sha256 `44e828617636…`): `AcpClient::shutdown` (`:421-444`) calls
`kill_process_group(pid)`, which is `killpg(pid, Signal::SIGKILL)` (`:2323-2328`), then waits 5 s; the fallback
`child.start_kill()` is documented at `:419` as "sends SIGKILL". `grep -c SIGTERM` over the whole file → **0**;
`SIGKILL` → **8**. The repo's own `docs/INCIDENT-LOG.md:36` records the identical reading and draws the identical
conclusion ("SIGKILL cannot be handled, so an exit-time status file is unsatisfiable on every leg") — that is why
ruling A21d exists.
*Failing input:* a real leg whose grandchild never closes the agent's stdout. Contract as documented: rc 70 + non-final
status + `write_errors ["terminated: SIGTERM"]`. Contract as it will actually behave under buzz-acp: **SIGKILL at +5 s**,
last RUNNING status, **no reason recorded anywhere**.
*Minimal fix:* reword `:16-20` to name the real bound and cite it —
"A client that never closes (c2a) or a grandchild that holds the agent's stdout (a2c) keeps the tee alive. buzz-acp
ends such a leg with `killpg(SIGKILL)` on the whole process group and a bounded 5 s wait
(`crates/buzz-acp/src/acp.rs:421-444`, `:2323-2328`, pinned `1c8321cd`); SIGKILL cannot be handled, so the leg's
evidence is its last RUNNING status (A21d). The SIGTERM path below covers an operator/systemd TERM, not buzz-acp."
Fix the three test docstrings the same way.
*Exact red test to add:* a doc-anchor guard —
`test_docstring_names_the_pinned_shutdown_signal`: assert the tee's module docstring contains `"SIGKILL"` and
`"acp.rs"` and does **not** contain the string `"TERMs/KILLs"`. It is red today.

**F-B5e-2 [BLOCKING] SOLID — S1 is effectively ungated (killed 1 run in 16); round-9 F11 is NOT closed.**
`tests/test_s0_01_frame_tee.py:1813-1815` is the only lag assertion in the suite, and it samples **one** SIGKILL.
`test_directional_trails_timeline_after_sigkill` (`T:1925-2039`) runs **12** SIGKILL trials with spread kill instants
and never reads `tee-status.json` at all — the lane brief demanded the assertion in **both**.
*Observed vs expected:* expected "S1 dies on a NAMED test, full suite, no `-x`". Observed: 16 runs of the two named
tests → **1 KILLED, 15 SURVIVED (6 %)**; the full suite is `93 passed` under S1.
*Failing input:* any regression that publishes the status before the timeline line. Under SIGKILL it produces
`updated_seq = timeline_last_seq + 1`, which both the PIN checker and A5g's running arm reject — a live A21d failure
the suite sees 6 % of the time.
*Minimal fix (deterministic, mirrors the pin that already works for N3):* an AST pin in `TestStructuralPins` —
in both `pump_fd` and `pump_pipe`, inside the `with lock:` body, the `tl.write` call's lineno is **less than** the
`_write_status()` call's lineno.
*Exact red test to add:*
```python
def test_status_write_follows_timeline_write_in_pumps(self, tmp_path):
    tree = ast.parse(Path(TEE).read_text())
    for pump in ("pump_fd", "pump_pipe"):
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == pump)
        wl = next(n for n in ast.walk(fn) if isinstance(n, ast.With)
                  and any(isinstance(i.context_expr, ast.Name) and i.context_expr.id == "lock"
                          for i in n.items))
        tl = next(c.lineno for c in ast.walk(wl)
                  if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                  and c.func.attr == "write" and getattr(c.func.value, "id", None) == "tl")
        ws = next(c.lineno for c in ast.walk(wl)
                  if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                  and c.func.id == "_write_status")
        assert tl < ws, "%s: _write_status at %d precedes tl.write at %d" % (pump, ws, tl)
```
Plus (cheap, independent): add the existing lag assertion to `test_directional_trails_timeline_after_sigkill`'s
per-trial block — 12 samples instead of 1 raises the behavioural kill rate from ~6 % to ~54 %.

**F-B5e-3 [BLOCKING] SOLID — N4 and D3 die only probabilistically; round-9 F2 is NOT fully closed.**
`tests/test_s0_01_frame_tee.py:2366-2444` (`test_concurrent_main_thread_status_vs_pump`) is the **sole** killer for both.
*Observed vs expected:* expected "N4, D3 must die on a NAMED test, full suite, no `-x`". Observed over 9 runs each:
**N4 7/9 (78 %), D3 5/9 (56 %)**; both SURVIVE the full suite (`93 passed`) on the runs where the named test passes.
Its docstring claims "Kills N4 (snapshot outside lock) and D3 (no status_lock)" without qualification.
*Failing input:* a CI run that happens to schedule the pump and the main-thread drain writer without an interleaving
that tears the snapshot. D3's mechanism explains its lower rate: with `status_lock` dropped, each writer still
`open(..., "w")`s and flushes its whole 300-byte object at close, so torn JSON needs a rarer interleaving than the
`os.replace`/ENOENT collision, which is invisible to this test.
*Minimal fix:* keep the race test (it is a good stress) but add deterministic structural pins beside it —
`_write_status`'s counter snapshot must be inside a `with lock:` and its `os.replace` inside a `with status_lock:`.
*Exact red test to add:*
```python
def test_write_status_snapshot_and_rewrite_are_locked(self, tmp_path):
    tree = ast.parse(Path(TEE).read_text())
    ws = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "_write_status")
    withs = {}
    for n in ast.walk(ws):
        if isinstance(n, ast.With):
            for i in n.items:
                if isinstance(i.context_expr, ast.Name):
                    withs.setdefault(i.context_expr.id, n)
    assert "lock" in withs, "_write_status takes no `with lock:`"
    assert "status_lock" in withs, "_write_status takes no `with status_lock:`"
    assert any(isinstance(c, ast.Name) and c.id == "seq" for c in ast.walk(withs["lock"])), \
        "the counter snapshot is not inside `with lock:`"
    assert any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
               and c.func.attr == "replace" for c in ast.walk(withs["status_lock"])), \
        "os.replace is not inside `with status_lock:`"
```
This is the exact code I executed. **PIN: PASS · N4: KILLED · D3: KILLED**, deterministically.

**F-B5e-4 [BLOCKING] SOLID — the report's "RED STATE" is a `pytest -x` early stop against the wrong baseline;
round-9 F4's class, repeated.**
`tasks/briefs/s0-01-b5e-support/B5e-report.md` § RED STATE / § GATE LINES.
*Observed vs expected:* the report prints `1 failed, 53 passed in 20.81s` under a heading that reads as a full-suite
red state. 93 items are collected. I reproduced the line exactly by adding `-x` (`1 failed, 53 passed in 20.62s`) —
it stops at item 54 of 93 and reports 1 of 10 real failures. Worse, the baseline is `c227f8d`, whose tee content is
**B5c** (473 lines) — two generations back; the true parent is `736bb94` (476 lines). Three of the ten reds against
`c227f8d` are B5d's regressions, not B5e's.
*Minimal fix:* re-paste as `git show 736bb94:proofs/S0-01/tools/frame_tee.py` + PIN tests, **no `-x`**:
`6 failed, 87 passed in 170.35s`, with the six names listed and the five controls labelled as controls with the
mutant each kills.

**F-B5e-5 [MED] SOLID — a Popen hoisted above the handler install is invisible to both F13 tests (mutant
INSTALL-LATE-B survives the full suite).**
`tests/test_s0_01_frame_tee.py:2543-2576` (`test_no_statement_between_signal_and_try`).
*Observed vs expected:* the pin checks only that `main.body[signal_idx + 1]` is a `Try`. Moving
`proc = subprocess.Popen(...)` to `main.body[signal_idx - 1]` keeps install and try adjacent, so the pin passes; and
the behavioural test's TERM is sent only after `pgrep -P` sees the child, i.e. after the fork — so it passes too.
Measured: `2 passed, 91 deselected` named, then `93 passed in 169.71s` full suite. The regression it hides re-opens the
Popen fork/exec (~1–3 ms) as an unhandled-TERM window.
*Minimal fix / exact red test:* in the same AST test, add
`assert not any(isinstance(c, ast.Call) and getattr(c.func, "attr", "") == "Popen" for s in main_fn.body[:signal_idx] for c in ast.walk(s)), "Popen precedes the handler install"`.

**F-B5e-6 [MED] SOLID — the `proc = None` pre-init, which AF-AP-58's own remedy names, is ungated (mutant NO-PREINIT
survives the full suite).**
`proofs/S0-01/tools/frame_tee.py:122`.
*Observed vs expected:* deleting the line leaves `93 passed in 170.68s`. Real failing input: a TERM delivered between
`:207` (install) and `:209` (`proc` bound) → `UnboundLocalError` in the except path **after** the status write,
traceback, rc 1 instead of 70. Every test's TERM arrives after the fork, so nothing sees it.
*Minimal fix / exact red test:* AST pin —
`assert any(isinstance(s, ast.Assign) and getattr(s.targets[0], "id", "") == "proc" and isinstance(s.value, ast.Constant) and s.value.value is None for s in main_fn.body[:signal_idx]), "proc is not pre-initialised to None before the handler install"`.

**F-B5e-7 [MED] SOLID — `test_sigterm_no_deadlock_under_contention` passes with its contention precondition never met.**
`tests/test_s0_01_frame_tee.py:1566-1572` (the `updated_seq >= 100` wait) — an AF-AP-40 screen hit, and a REAL one.
*Observed vs expected:* changing only `T:1569` to `>= 10**9` (precondition unreachable) leaves the test **green**:
`1 passed, 92 deselected in 15.19s` (15.01 s call — the full wait timeout). The test then proves only "a tee answers
SIGTERM", not "a tee answers SIGTERM *under contention*".
*Minimal fix / exact red test — RUN, not reasoned (AF-AP-36/57):*
```python
loaded = False                 # hoist above the wait loop
...
        if s.get("updated_seq", 0) >= 100:
            loaded = True      # set on the break path
            break
...
assert loaded, "no contention: the wait for updated_seq >= 100 timed out"
```
Verified on a scratch copy: clean threshold → `1 passed … in 0.28s`; threshold mutated to `>= 10**9` →
`1 failed … in 15.24s` (AssertionError at the new line).

**My first proposal for this fix was itself a hollow killer, and I caught it by running it.** I first proposed
`assert s is not None and s.get("updated_seq", 0) >= 100` after the loop. RUN against the same mutation it
still **passed** (`1 passed … in 15.18s`): `s` is rebound on every successful read inside the loop, so after a
timeout it holds the last status read, whose `updated_seq` is ≥ 100 anyway. The value-based assertion tests the
tee's throughput; only the flag tests the *wait's exit reason*, which is what this finding is about. Recorded here
as a live instance of AF-AP-57 (a killer whose only discriminator is a value the mutated path still produces) —
a verifier's proposed killer is a hypothesis like any other claim.

**F-B5e-8 [LOW] SOLID — the window test's stated mechanism is not the mechanism that runs.**
`tests/test_s0_01_frame_tee.py:2462-2477` docstring ("entrypoint >= 200 MB … sha256 >= 0.3 s"; "the tee is in sha256
reads").
*Observed vs expected:* 12 instrumented runs, **0/12 reach the 234 MB sha256** (`T_SHA3` never printed; `T_SHA1` never
printed either — the TERM lands during `readlink`/interpreter sha256 at `:217-218`). The test's determinism comes from
`pgrep -P` (the child cannot be visible before the fork at `:209`, which is after the install at `:207`), giving a
**structural** lower bound of 0 flakes; the file size only widens the in-try region as load insurance.
*Minimal fix:* rewrite the docstring to state the structural guarantee ("the child cannot appear before the fork at
`:209`, which follows the install at `:207`, so the TERM can never precede the handler") and describe the 234 MB
entrypoint as load insurance, not as the mechanism.

**F-B5e-9 [LOW] SOLID — `test_grandchild_straggler_recorded`'s docstring overstates what it kills.**
`tests/test_s0_01_frame_tee.py:918` — "Kills the a2c stall-timeout mutants (0 / 5 / 30 s)."
*Observed vs expected:* measured, it kills a2c-t0 and a2c-t5, and **PASSES** under a2c-t30
(`1 failed, 1 passed` — only `test_drain_loops_have_no_break_or_timeout` fails). A 6 s straggler cannot detect a 30 s
timeout; that is precisely why the structural pin exists.
*Minimal fix:* "Kills a2c stall timeouts shorter than the 6 s straggler gap (0 and 5 s); the 30 s case is killed by
`test_drain_loops_have_no_break_or_timeout`."

**F-B5e-10 [LOW] SOLID — the Popen census count is carried over, not measured.**
`tasks/briefs/s0-01-b5e-support/B5e-report.md` § POPEN CENSUS: "25 `Popen(` call sites … All 25 guarded."
*Observed:* 27 AST call sites (all guarded), 31 raw textual occurrences, 4 inside agent source strings. 25 is the
round-9 number. AF-AP-37 class. *Fix:* paste the census tool's output.

**F-B5e-11 [LOW] SOLID — four success-only waits leave their premise unasserted.**
`T:501` (`test_grandchild_keeps_tee_alive`), `T:857` (`test_never_reading_client`),
`T:1021` (`test_grandchild_never_closes_sigterm_required`), `T:1566` (F-B5e-7, the sharp one).
Each polls for a threshold, falls through silently on timeout, and then asserts only outcomes a tee that met no
threshold also satisfies. *Fix:* hoist `s = None` above each loop and add one assertion after it —
`assert s is not None and s.get("recorded_a2c", 0) >= 1, "no a2c frame recorded before the liveness window"`.
For these three the **value** form is the right one (the regression of interest is a tee that records nothing, and
`s` then carries `recorded_a2c == 0`); `T:1566` needs the **flag** form instead, for the reason recorded under
F-B5e-7.

**F-B5e-12 [LOW] SOLID — fixture grandchildren are never killed; they are orphaned to init and self-expire.**
`T:468` (30 s), `T:990` (120 s), `T:2381-2387` (a 3000-frame/30 s streamer). Evidence: a mid-suite census caught
`5481 1 S 23 /usr/local/bin/python3 -c import time; time.sleep(120)` — ppid 1, alive.
Post-suite censuses are clean, so this is unowned lifetime rather than a permanent leak — but the lane brief's boundary
says "every spawned tee/agent is killed in `finally`", and under `pytest -n 8` on the PC this is up to eight concurrent
orphan sets holding pipe fds. *Fix:* have each fixture agent write its grandchild pid into the framedir
(`grandchild.pid`) and kill it in the test's `finally`.

**F-B5e-13 [INFO] SOLID — `_write_status` reads two `state` fields outside the snapshot lock.**
`proofs/S0-01/tools/frame_tee.py:174` (`state["stdin_reader_done"]`) and `:179` (`list(state["write_errors"])`) are
outside the `with lock:` block at `:162-167`. A published status can therefore carry counters from T1 and
`write_errors` from T2 > T1. No checker arm is currently sensitive to the skew (the running arm rejects any
`forward <d>:` entry regardless of the counters), so this is recorded, not charged. *Fix if ever needed:* move both
reads inside the `with lock:`.

**F-B5e-14 [INFO] SOLID — `identity` is unbound on timeout in `test_sigterm_kills_agent_child`.**
`tests/test_s0_01_frame_tee.py:2610-2617`: a 10 s wait that never succeeds raises `NameError` at
`agent_pid = identity["agent_child_pid"]`. Fails loud, but as an error rather than a message. *Fix:* pre-bind
`identity = None` and assert with a reason (the shape `test_initial_status_before_first_frame` already uses at `T:1182`).

**F-B5e-15 [INFO] SOLID — all three AF-AP-45 screen hits are false positives; the screen regex cannot see the fix.**
`T:2534`, `T:2630`, `T:2640` are exactly the state-aware `/proc/<pid>/stat` field-3 form AF-AP-45 prescribes, yet the
regex `(exists|isdir|is_dir)\(\s*f?["'][^"'\n]*/proc/` fires on them. Coordinator item (outside B5e's boundary):
add a same-block exclusion for a following `stat` read, or the screen will keep flagging the correct implementation.

**F-B5e-16 [INFO] — premise shift during the run, grade unaffected.**
HEAD moved `19799b17` → `e8fdfab` (3 commits: `b9d2695` ledger, `d5b1b03` A5h brief, `e8fdfab` lane D5h's backend).
Both B5e scope files are byte-identical at the PIN, at `e8fdfab` and in the worktree
(`061dd10c…` / `82a3d1f9…`; `git diff --stat 19799b17 HEAD -- <both>` empty). The uncommitted set changed from lane
D5h's three backend files to a checker lane's `proofs/S0-01/check_acp_conformance.py` +
`tests/test_s0_01_check_acp_conformance.py`. I graded the PIN's bytes throughout and never touched the shared tree.

**F-B5e-17 [INFO] UNSURE — `os.makedirs` sits in the uncovered pre-install window.**
`proofs/S0-01/tools/frame_tee.py:117`. The docstring attributes the whole uncovered window to "Python interpreter
startup". Measured, the non-startup part of that window is **0.08 ms** (`T_MAIN`→`T_INST`, median over 12 runs) against
~25–30 ms of interpreter startup — so the wording is materially accurate on a normal filesystem. On a hung/NFS
framedir `os.makedirs` could block arbitrarily inside the uncovered window. **Not reproduced** (I did not build a
hung-FS fixture). Recorded for completeness.

**F-B5e-18 [INFO] UNSURE — SIGTERM against a pump wedged inside the status write.**
A pump holds `lock` (`:263`/`:350`) and then `status_lock` (`:184`) while doing file I/O. If that I/O blocks
indefinitely, the `except _Terminated:` path's `_write_status(final=False)` (`:456`) blocks on `lock` and the tee never
answers the TERM. Lock ORDER is consistent (`lock` → `status_lock`, never the reverse), so this is a stall, not a
deadlock, and it needs a wedged filesystem. The suite's cover is `test_sigterm_no_deadlock_under_contention`, which
F-B5e-7 shows can go vacuous. **Not reproduced.**

---

## MY OWN PROPOSED KILLERS, RUN (AF-AP-36: a verifier's proposed killer is a hypothesis like any other)

Every structural test I propose above was executed against the PIN and against the mutant it names, before it entered
this report:

```
F-B5e-2 status_after_timeline      PIN:PASS   S1:KILLED
F-B5e-3 locks_in_write_status      PIN:PASS   N4:KILLED   D3:KILLED
F-B5e-5 no_popen_before_install    PIN:PASS   INSTALL-LATE-B:KILLED   INSTALL-LATE:KILLED
F-B5e-6 proc_preinit               PIN:PASS   NO-PREINIT:KILLED
F-B5e-1 docstring_names_sigkill    PIN:FAIL(module docstring does not name SIGKILL)   <- red today, as claimed
all proposed structural killers behave as claimed: True
```
F-B5e-7's killer was run twice — the first form failed to kill and was replaced (see F-B5e-7).

## ONE MORE ATTACK: CAN THE LOSS CLIFF COME BACK WITHOUT TOUCHING THE DRAIN LOOPS?

Mutant **PUMP-TIMEOUT** — a 5 s no-data `select()` timeout inside `pump_pipe`'s own read loop, which re-creates the
a2c loss cliff while leaving both drain loops textually pristine (the structural pin is blind to it by construction).

```
PUMP-TIMEOUT  KILLED-BY-NAMED   2 failed, 1 passed, 90 deselected in 20.53s
  FAILED test_grandchild_straggler_recorded
  FAILED test_grandchild_never_closes_sigterm_required
  (test_drain_loops_have_no_break_or_timeout PASSED — as expected, it cannot see this)
```
**Good news for the lane: the behavioural tests cover the route the structural pin cannot.** The AF-AP-53 class cannot
return through the pump either.

---

## WHAT I REPRODUCED vs REVIEWED STATICALLY vs DELIBERATELY SKIPPED

**Reproduced (my own runs, this session, on `git archive` copies of the PIN):**
the lane's `-x` red-state line byte-for-byte; the full no-`-x` red state on both the true parent (`736bb94`) and the
lane's baseline (`c227f8d`); all 11 new tests against the parent, individually; 26 distinct mutants over 63 runner pytest
invocations (including 9 reps each of N4 and D3 and 16 of S1); 12+6 instrumented SIGTERM-window runs and
12+6 TERM-at-t=0 runs; the F3 straggler at 2/6/9 s on three tee generations; the never-closing-grandchild liveness by
`/proc` state; the invariant set under bidirectional load (131 982 reads) with SIGSTOP-frozen and live comparisons and
a forward-broken negative control; the Popen census by AST; the process census before/after two full suites and
130 s later; the cost measurement ×3; pyflakes; two idle full suites plus six more inside mutant escalations; the
buzz-acp shutdown mechanism re-derived from the pinned upstream source; the AST-pin logic on 3.11/3.12/3.13; the tee's
behaviour and SIGTERM window under 3.12; the vacuity of `test_sigterm_no_deadlock_under_contention`; and every killer
I propose.

**Reviewed statically only:** F-B5e-13 (the unlocked `state` reads in `_write_status` — I argued the skew from the code,
I did not build a differential that observes it); the claim that `DRAIN-ORDER` is equivalent (argued from the code —
both loops are pure waits — not measured by a differential); the assertion that `test_sigterm_status_satisfies_check_tee_status`
(lane A5g's, read-only for B5e) genuinely reaches the checker — I observed it green and read the import, I did not
mutate the checker to confirm the tripwire fires.

**Deliberately skipped, with reasons:**
* **The PC leg** (`pc_suite.sh`, 8 xdist workers): `.pc-bridge.env` is dated 2026-09-06 and no banner was pasted for
  this session; running commands on the owner's PC is an outward action my brief forbids. Item 8's orphan class and
  item 5's race rates are the two findings a parallel venue would read differently.
* **The pytest suite on 3.12** (CI's interpreter): pytest is not installed for 3.12 here and I did not attempt a
  network install. Substituted with four standalone 3.12 reproductions (item 10).
* **A verbatim replay of round 9's 59-mutant set:** ~40 of them neither appear in this lane's acceptance bar nor touch
  code B5e changed, and mut9's anchors are keyed to B5d's tee. Cost ≈ 2 h of a contended 4-core box for no new
  information. The re-anchor audit is in item 3.
* **Mutating `check_acp_conformance.py` or `pins.py`** — read-only for this lane, and another lane holds them dirty.
* **A hung-filesystem fixture** for F-B5e-17/18 — I could not build one that does not risk the shared box.

**One outward-facing read, disclosed:** I fetched
`https://raw.githubusercontent.com/block/buzz/1c8321cd08feb597f8bcff5195c21148fb3e98ed/crates/buzz-acp/src/acp.rs`
(HTTP 200, 217 424 bytes, 5030 lines, sha256 `44e82861763694d2b82d02b15ee100ffd6c78874a2b2282865e6656c539c38f1`) to
re-resolve the pinned commit against primary source, per Phase 0. Read-only GET of a public file at the pinned SHA;
no state anywhere was changed.

**Shared-tree discipline:** read-only git throughout — no `stash`/`checkout`/`restore`/`reset`/`add`/`commit`/`push`.
Every mutant ran on a scratchpad copy and both scope files were re-hashed to the PIN values after each batch. The
shared tree's two scope files were `git status --porcelain`-clean at every check. I killed only processes I started.
One process error of my own, disclosed: I ran `git init -q .` inside my own scratch venue while probing tmp_path
hygiene; I removed the stray `.git` immediately. It was in the scratchpad, never the repo.

---

## VERDICT

# NOT-READY

**Blocking set (all four reproduced by me; my verdict rests on nothing I did not reproduce):**

1. **F-B5e-3 — N4 (78 %) and D3 (56 %) die only probabilistically.** The lane brief's bar was "must die on a NAMED
   test, full suite, no `-x`"; both survive the full suite on the runs where the single race test happens to pass.
   Round-9 **F2** is not closed. Fix is one AST test, verified to kill both deterministically.
2. **F-B5e-2 — S1 dies 1 run in 16.** Round-9 **F11** is effectively open: the lag assertion landed in one of the two
   tests the brief named, and the one it missed is the 12-trial SIGKILL test. Fix is one AST test, verified to kill.
3. **F-B5e-1 — the docstring's justification for the whole contract change is false at the pinned commit.** buzz-acp
   sends `killpg(SIGKILL)` and waits 5 s; it never sends SIGTERM (0 occurrences in `acp.rs` at `1c8321cd`). The tee,
   two in-code comments and three test docstrings all tell the reader the SIGTERM path is the bound for a wedged leg.
   It is not. This is the prose form of the #1 rule, and the repo's own incident log already records the correct
   reading.
4. **F-B5e-4 — the report's red state is `pytest -x` against a two-generations-old baseline.** `1 failed, 53 passed`
   is 1 of 10 real failures over 54 of 93 items. Round-9 **F4**'s class, repeated one round later.

**Should ship with the blockers (cheap, each verified):** F-B5e-5 (Popen-before-install invisible), F-B5e-6
(`proc = None` ungated), F-B5e-7 (contention test vacuous), F-B5e-8/9 (two docstrings overstate what they prove),
F-B5e-10 (Popen count carried over), F-B5e-11 (four unasserted preconditions), F-B5e-12 (orphaned grandchildren).

**What the lane genuinely landed, verified independently:**
the symmetric drain-to-EOF fix is real and correct — the a2c straggler is recorded at 2, 6 and 9 s where both earlier
tees lost it silently with `rc 0, drained true, write_errors []`; a grandchild that never closes keeps the tee alive
(state `S` at 11–16 s) and SIGTERM answers in 4 ms with `rc 70`, non-final, `["terminated: SIGTERM"]`; the F13 fix is
structurally complete — install at `:207`, `Try` at `:208`, zero statements between, zero statements after the try,
and every name the except path reads bound before the install (AST-verified); the window test is deterministic
(12/12 and 6/6 on two interpreters) for a *better* reason than it claims; 19 of 26 mutants die on named tests,
including all seven SIGTERM-path mutants, all four c2a timeouts, all three a2c timeouts, the a2c-loop deletion, the
wrong-thread wait, N3, and a pump-internal timeout that the structural pin cannot see; the qualified invariant list is
correct and its qualifications are necessary (both negatives reproduced); all 27 `Popen` sites are guarded; no live
process leaks after a suite; pyflakes rc 0; `93 passed` on eight independent full-suite runs; and the cost bar is met
at 0.90–0.98× of the round-6 baseline.

**Venue caveat on the verdict:** this is a sandbox-only, single-worker grade on a 4-core box shared with another
verifier (load 0.4–4.4 across the session, stated per measurement). The two race rates in F-B5e-3 and the orphan
class in F-B5e-12 are the findings most likely to read differently under `pytest -n 8` on the PC's 12 cores — in both
cases I expect them to get *worse*, not better, but I did not measure that venue and say so rather than assume it.
