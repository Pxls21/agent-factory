# VERIFY-B5f — round-11 adversarial grade of lane B5f (S0-01 frame tee: deterministic pins, honest SIGKILL bound, own-pid grandchild cleanup)

**Grade venue:** `git archive 4b432847… | tar -x` copies under the session scratchpad (`vb11`, `vb11red`, `vb11mut*`).
Shared tree: read-only git only, never modified. **STATUS: FINAL.**

## PREMISE

| item | value |
|---|---|
| PIN | `4b432847b685a0070fc37996dd1d89cea971a337` — `git cat-file -e` OK |
| `git rev-parse HEAD` at dispatch | `4b432847b685a0070fc37996dd1d89cea971a337` (HEAD **is** the PIN) |
| PIN subject | `S0-01 WIP checkpoint 8q: tee races pinned by deterministic AST tests, the shutdown bound stated as buzz-acp really behaves (SIGKILL), own-pid grandchild cleanup (lane B5f) — REVIEW-PENDING, nothing minted` |
| PIN parent | `9b2803c` (checkpoint 8p, lane A5h) — the B5f commit touches 5 files, only 2 of them in scope |
| `proofs/S0-01/tools/frame_tee.py` | sha256 `ac82dba82e2f4cb69c5ac1344f9f6b730bfeb69ccccc456929201ab3a595361c`, **471** lines — matches the lane report's FILE IDENTITY table |
| `tests/test_s0_01_frame_tee.py` | sha256 `05019a915ecf8de515e0c55a7ddf65b8fbcc05e1b33d04fcf71c717378d7ce84`, **2862** lines — matches |
| worktree = PIN bytes | both scope files byte-identical in the shared worktree and at the PIN; `git status --porcelain` on them: EMPTY |
| shared-tree dirty set | lane D5i's `proofs/S0-01/tools/scripted_backend.py`, `tests/red/test_s0_01_backend_credential_screen.py`, `tests/test_s0_01_scripted_backend.py` — untouched by me |
| interpreter | `/usr/local/bin/python3` — Python 3.11.15, pytest 9.1.1 |
| xdist | **NOT installed** (`ModuleNotFoundError: No module named 'xdist'`) — item 5's `-n 4` request is unrunnable; substituted concurrent pytest processes |
| collected | `96 tests collected in 0.18s`; `grep -c "    def test_"` → **88** (96 = 88 defs + 8 parametrised extras) — matches the report |
| nproc / `df -h /` | 4 cores; `/dev/vda 252G 26G 12G 69% /` |
| load average at start | `1.12 1.25 1.55` |

**Note on the lane report's PIN line.** The report's header says `PIN a60b933559ce…  HEAD at run: same`. `a60b933` is the
commit the lane was *dispatched at* (the brief commit), not the commit its work landed in; `git diff --stat a60b933 4b43284`
spans two commits (`9b2803c` A5h + `4b43284` B5f). The report's FILE IDENTITY sha256s are the FINAL files and match the
PIN exactly, so the grade is unaffected — but the header line is wrong as written (a reader who runs `git show a60b933:…`
gets the pre-B5f tee).

## ITEM 8 (run first, quietest window) — COST (F16)

`vb11cost.py` (the round-10 verifier's 11-frame real-leg shape, re-implemented: 3 c2a in, 8 a2c out, full tee
spawn→exit wall clock), 15 reps × 3 batches, **PIN tee and the parent tee 736bb94 measured back-to-back in the same
window**.

```
LOAD-BEFORE 0.59 0.93 1.38          LOAD-AFTER 0.71 0.95 1.38
PIN   4b43284  batch0 {"reps": 15, "median": 0.0546, "min": 0.0528, "max": 0.0679}
PIN   4b43284  batch1 {"reps": 15, "median": 0.0545, "min": 0.0535, "max": 0.1535}
PIN   4b43284  batch2 {"reps": 15, "median": 0.0553, "min": 0.0528, "max": 0.1511}
PARENT 736bb94 batch0 {"reps": 15, "median": 0.0564, "min": 0.0537, "max": 0.0744}
PARENT 736bb94 batch1 {"reps": 15, "median": 0.0543, "min": 0.0524, "max": 0.0580}
PARENT 736bb94 batch2 {"reps": 15, "median": 0.0577, "min": 0.0534, "max": 0.1551}
```

**Load 0.59 → 0.71 (1-min) across all six batches.** PIN median 0.0545–0.0553 s; ratio vs the 0.058–0.060 baseline
**0.91×–0.95×**. The A/B against the parent tee in the same window (0.0543–0.0577) shows **no measurable cost from
this lane's changes** — the difference is inside the batch-to-batch noise. The lane's 0.1808 s median is a load
artefact, exactly as its DISCREPANCIES section says; my measurement is the confirmation it could not make.
**F16: MET (SOLID, reproduced).**

## ITEM 10a — GATE LINES, MINE, ON THE PIN VENUE

```
pyflakes proofs/S0-01/tools/frame_tee.py tests/test_s0_01_frame_tee.py   -> rc 0
collected                                                                -> 96 tests collected in 0.18s
def test_ count                                                          -> 88

PIN full suite, no -x (load 0.55 before, 1.55 after):
  96 passed in 169.38s (0:02:49)     PYTEST_RC=0
```
The coordinator's gate of record (`96 passed in 169.50s`) **reproduces** (169.38 s vs 169.50 s, load 0.55).

## ITEM 1 (part) — THE RED STATE DOES **NOT** REPRODUCE: 8 FAILED, NOT 7

Venue `vb11red` = `git archive 4b43284` + `git show 736bb94:proofs/S0-01/tools/frame_tee.py`
(sha256 `3fc846ceaf4b687b30996d2b9e0fe07144b8a1fa65650c4082a2e2272af9d83a`, 476 lines — matches the lane's stated
parent), PIN tests (sha256 `05019a91…`), full suite, **no `-x`**:

```
LOAD-BEFORE 1.46 1.03 1.31
8 failed, 88 passed in 171.80s (0:02:51)   PYTEST_RC=1
FAILED tests/test_s0_01_frame_tee.py::TestTeeStatus::test_grandchild_straggler_recorded
FAILED tests/test_s0_01_frame_tee.py::TestTeeStatus::test_grandchild_never_closes_sigterm_required
FAILED tests/test_s0_01_frame_tee.py::TestStructuralPins::test_drain_loops_have_no_break_or_timeout
FAILED tests/test_s0_01_frame_tee.py::TestStructuralPins::test_write_status_snapshot_and_rewrite_are_locked
FAILED tests/test_s0_01_frame_tee.py::TestEarlySigterm::test_sigterm_during_sha256_produces_status
FAILED tests/test_s0_01_frame_tee.py::TestEarlySigterm::test_no_statement_between_signal_and_try
FAILED tests/test_s0_01_frame_tee.py::TestSigtermTerminatesAgent::test_sigterm_kills_agent_child
FAILED tests/test_s0_01_frame_tee.py::TestDocstringAnchor::test_docstring_names_the_pinned_shutdown_signal
```

Two deltas against the lane's pasted `7 failed, 89 passed` (which is also the coordinator's gate of record):

1. **`test_write_status_snapshot_and_rewrite_are_locked` is RED on the parent — the lane's table says GREEN/CONTROL.**
   This is **deterministic**, not a flake: run alone against the parent tee it fails in 0.15 s at
   `tests/test_s0_01_frame_tee.py:2498` — `assert "stdin_reader_done" in lock_src` — because the F-B5e-13 fix that
   moved those two `state` reads inside `with lock:` is part of *this* lane's tee change. The lane's own report row
   ("`test_write_status_snapshot_and_rewrite_are_locked` | on parent 736bb94: **GREEN** | CONTROL — kills N4, D3,
   LOCK-READS-OUT") is therefore wrong on its face. See F1.
2. **`test_sigterm_status_satisfies_check_tee_status` PASSED here; the lane lists it as RED.** Conversely
   `test_sigterm_kills_agent_child` FAILED in my single run; the lane saw it only on its *second* run. Both are the
   timing-sensitive pair, and the lane's own report flags the second one. See F2.

Deterministic-pin sanity, individually, on the parent tee (0.05–0.15 s each, no timing component):
```
test_write_status_snapshot_and_rewrite_are_locked   1 failed  (:2498 stdin_reader_done)   <- lane says GREEN
test_status_write_follows_timeline_write_in_pumps   1 passed                              <- CONTROL, as claimed
test_docstring_names_the_pinned_shutdown_signal     1 failed  (:2859 no SIGKILL)          <- genuine red, as claimed
test_no_statement_between_signal_and_try            1 failed  (:2742)                     <- genuine red, as claimed
test_drain_loops_have_no_break_or_timeout           1 failed  (:2411)                     <- genuine red, as claimed
```


## ITEM 2 — THE HONEST BOUND (F-B5e-1): RE-RESOLVED, AND THE PIN IS STRING-ONLY

### 2a. Primary source re-resolved independently

`curl` (read-only GET, the one outward action my brief allows) of
`raw.githubusercontent.com/block/buzz/1c8321cd08feb597f8bcff5195c21148fb3e98ed/crates/buzz-acp/src/acp.rs`:

```
sha256 44e82861763694d2b82d02b15ee100ffd6c78874a2b2282865e6656c539c38f1     5030 lines
grep -c SIGTERM -> 0        grep -c SIGKILL -> 8
```
sha256 **matches the round-10 verifier's byte-for-byte**. `upstream.lock.yaml:16-19` pins buzz at that commit.

Cited ranges read in full:
* `acp.rs:422-444` `pub async fn shutdown(&mut self)` — `match self.child.id() { Some(pid) if kill_process_group(pid) => {} _ => { let _ = self.child.start_kill(); } }`, then
  `tokio::time::timeout(Duration::from_secs(5), self.child.wait())` with the comment
  *"Bounded wait: if the child doesn't exit within 5s after SIGKILL, give up"* (`:436-439`).
* `acp.rs:2323-2329` `fn kill_process_group(pid)` → `killpg(Pid::from_raw(pid as i32), Signal::SIGKILL)` (`:2328`).
* `Drop for AcpClient` (`:2297-2311`) also killpg(SIGKILL)s the group, then a **non-blocking** `try_wait()` — no 5 s wait.
* `shutdown()` is a real production path, not test-only: `crates/buzz-acp/src/lib.rs` calls `acp.shutdown().await`
  at ≥ 20 sites (`:3951`, `:3968`, `:3976`, `:3992`, `:5187`, …) and `pool.rs` at 6 more. (Checked because the only
  `.shutdown()` inside `acp.rs` itself is at `:3093`, inside `#[cfg(test)] mod tests` which opens at `:2351`.)
* The ONLY production `from_secs(5)` in `acp.rs` is the post-kill wait at `:439` — every other one is in `mod tests`.

**The module docstring (`frame_tee.py:16-25`) is accurate.** *"buzz-acp ends such a leg with `killpg(SIGKILL)` on the
whole process group and a bounded 5 s wait … SIGKILL cannot be handled, so the leg's evidence is its last RUNNING
status (A21d). The SIGTERM path below covers an operator/systemd TERM, not buzz-acp."* — every clause reproduces
against the pinned source. (Nit: the citation `:421-444` starts one line inside the doc comment; `shutdown()` is
`:422-444`. Immaterial.)

### 2b. But five other artifacts invert the source — see F3

The two in-code comments and three test docstrings the lane rewrote say **"buzz-acp SIGKILLs the group *after 5 s*"**.
The source does the opposite: it SIGKILLs **first**, then waits **up to** 5 s for the child to exit. There is no
5-second delay before the kill anywhere in `acp.rs` (the grep above). The wording is attributed to the same citation
that contradicts it.

### 2c. The doc-anchor test is a string-only tautology — MEASURED, not argued

Mutant **DOCSTRING-HYBRID** (mine): rewrite the docstring so it still contains `SIGKILL` and `acp.rs`, still lacks
`TERMs/KILLs`, but re-asserts the false claim the lane was told to remove —
*"…and the SIGTERM path below is what bounds a wedged leg: it records ``terminated: SIGTERM`` so every wedged leg
leaves a reason."*

```
DOCSTRING-TERM     KILLED          (module docstring does not name SIGKILL, test:2859)
DOCSTRING-HYBRID   survived-named  1 passed, 95 deselected in 0.04s
DOCSTRING-HYBRID   FULL-SUITE  SURVIVED   96 passed in 169.16s (0:02:49)
COMMENT-TERM       survived-named  1 passed, 95 deselected in 0.04s
```
**The pin checks three string tokens, not the meaning.** The exact counter-example my brief predicted — a docstring
that names SIGKILL and acp.rs and still says the SIGTERM path bounds a wedged leg — passes the whole suite. See F4.

## ITEM 3 — THE FOUR AST PINS: 3× ON THEIR MUTANTS, THEN ATTACKED AS MIRRORS

Runner `vb11mut.py` + `vb11muts.py` (mine). Venue = a `git archive 4b43284` copy under `…/scratchpad/vb11mut`.
Protocol per mutant: restore both scope files from the pristine archive → apply → `ast.parse` both → run the NAMED
killer(s) → escalate to the full suite (no `-x`) on a green → restore → re-assert sha256 (`ac82dba82e2f` /
`05019a915ecf` after every mutant; printed by the runner).

### 3a. On their mutants — all deterministic

| pin | mutant | reps | result | message |
|---|---|---|---|---|
| `test_status_write_follows_timeline_write_in_pumps` | **S1** | 3 | **KILLED 3/3** | `pump_fd: _write_status at 275 precedes tl.write at 278` (test:2476) |
| same | **S1F** (faithful round-10 shape: status before the timeline line but *after* the recorded counter, so invariant-1 still holds) | 3 | **KILLED 3/3** | `pump_fd: _write_status at 276 precedes tl.write at 279` |
| `test_write_status_snapshot_and_rewrite_are_locked` | **N4** | 3 | **KILLED 3/3** | `_write_status takes no \`with lock:\`` (test:2492) |
| same | **D3** | 3 | **KILLED 3/3** | `_write_status takes no \`with status_lock:\`` (test:2493) |
| same | **LOCK-READS-OUT** | 1 | **KILLED** | `stdin_reader_done is not read inside \`with lock:\`` (test:2498) |
| `test_no_statement_between_signal_and_try` | **INSTALL-LATE-B** | 1 | **KILLED** | `Popen precedes the handler install` (test:2746) |
| same | **NO-PREINIT** | 1 | **KILLED** | `proc is not pre-initialised to None before the handler install` (test:2752) |

F-B5e-2/3/5/6 are closed *deterministically*, reproduced. The round-10 probabilistic kills (N4 78 %, D3 56 %,
S1 6 %) are now 3/3 each on a structural test that runs in 0.10 s.

**The 12-trial lag assertion is independently load-bearing** (measured on the faithful S1F, 5 reps each):

```
S1F vs test_directional_trails_timeline_after_sigkill (the NEW per-trial lag assert, test:2123):
  KILLED 5/5   e.g. "trial 0: lag -1 not in {0,1}: tl_last_seq=729 updated_seq=730"
S1F vs test_sigkill_leaves_nonfinal_status (the round-10 single-sample lag, test:1897-ish):
  survived 5/5   1 passed, 95 deselected
```
The round-10 verdict predicted the 12-sample form would raise the behavioural kill rate "from ~6 % to ~54 %"; measured
it is **5/5 vs 0/5**. The lane's second F-B5e-2 fix does real work.

### 3b. Attacking the pins as MIRRORS — two of the four are mirrors

| mirror mutant | what it does | pin | behavioural | full suite |
|---|---|---|---|---|
| **MIRROR-SNAPSHOT** | keeps the `with lock:` snapshot of `seq`/`stdin_reader_done`/`write_errors` **and then re-reads every field OUTSIDE the lock** into the same names, so the published object is a non-atomic read — semantically identical to N4 | **PASSES** | `test_concurrent_main_thread_status_vs_pump` **PASSES 5/5** (45.1-45.8 s each) | **SURVIVED — `96 passed in 169.50s`** |
| **MIRROR-PREINIT** | keeps `proc = None` (pin passes) and adds `proc = 0` immediately after, before the install → the except path does `0.terminate()` → `AttributeError`, rc 1, on any TERM in the install→Popen window | **PASSES** | `test_sigterm_during_sha256_produces_status` PASSES | **SURVIVED — `96 passed in 169.89s`** |
| **MIRROR-S1-FLUSH** | `tl.write` stays textually before `_write_status` (pin passes) but `tl.flush()` moves **after** it, so the timeline line can still sit in the buffer when the status publishes | PASSES | **KILLED** by `test_directional_trails_timeline_after_sigkill`: `trial 2: dir a2c (391) > timeline a2c (390)` (test:2115) | n/a |
| **PIN-LOCK-NAME** | renames `status_lock` → `stlock` in the tee **and** in the pin's string | PASSES (by construction) | — | **SURVIVED — `96 passed in 169.57s`**; an acceptable mirror (a rename is semantically neutral). The sharper form, `status_lock = contextlib.nullcontext()`, keeps the name and IS caught — see PIN-NULLLOCK below |

**MIRROR-SNAPSHOT is the significant one: a tee with exactly the N4 defect passes the new deterministic pin AND the
race test AND the whole suite.** See F5.

## ITEM 7 (part) — TRY-SHRINK2, RUN CORRECTLY

The lane's `run_mutants.py:168-177` deletes the `try:` line and leaves the body indented and the `except _Terminated:`
dangling → `SyntaxError` (its own PATCH-FAILED). My implementation rebuilds the block: the `try:` covers **only** the
`Popen` line, the `except _Terminated:` handler follows it immediately, and lines `215..458` are dedented and left
outside every catcher.

```
TRY-SHRINK2   KILLED   0.7s
  FAILED …::TestSigtermHandler::test_sigterm_writes_status_and_exits_70        AssertionError: assert 1 == 70  (test:1601)
  FAILED …::TestEarlySigterm::test_sigterm_during_sha256_produces_status       AssertionError: assert 1 == 70  (test:2684)
  2 failed, 94 deselected in 0.52s
```
**KILLED by two named tests.** The lane's NOT_DONE row is closed; the round-10 verifier's result reproduces.

```
GRANDCHILD-UNKILLED  KILLED  5.5s   AssertionError: grandchild pid 18323 still alive after kill  (test:549)
LAG-12-DROPPED       survived-named 7.4s   ->  FULL-SUITE SURVIVED  96 passed in 170.39s
```
LAG-12-DROPPED is a test-side deletion, so "what kills it now" is *nothing* — as it must be for any assertion
deletion; the meaningful measure is 3a's S1F 5/5, which says the assertion is not decorative.


## ITEM 4 — THE PREMISE ASSERTS (F-B5e-7 / F-B5e-11)

Negative controls, each on a scratchpad copy. **Two different mutations, and they say different things:**

| control | what is mutated | result |
|---|---|---|
| **NC-FLAG-LOOPONLY** — only the *loop's* break threshold at `test:1649` → `>= 10**9`; `assert loaded` untouched | the sharp one (AF-AP-57 shape) | **KILLED** `AssertionError: no contention: the wait for updated_seq >= 100 timed out` (test:1655), `1 failed, 95 deselected in 15.25s` |
| **NC-VALUE-LOOPONLY-501** — only the loop's break threshold at `test:508` → `>= 10**9`; `assert … >= 1` untouched | same shape, value form | **SURVIVED** `1 passed, 95 deselected in 13.34s` |
| **NC-VALUE-BOTH-501** — loop *and* assert thresholds → `>= 10**9` (this is the lane's control) | the weak one | **KILLED** `no a2c frame recorded before the liveness window` (test:513), `1 failed in 10.37s` |
| **NC-PREMISE-REAL-501** — the REAL regression: the fixture agent never writes the handshake response, so the tee records **no** a2c frame | the honest one, run by nobody before me | **KILLED** `no a2c frame recorded before the liveness window`, `1 failed in 10.38s` |

Reading: the **flag** form at `test:1643/1650/1655` is robust under the sharpest control — F-B5e-7 is properly closed.
The three **value** forms (`test:513`, `:902`, `:1075`) are *vacuous under the loop-only mutation* — the exact AF-AP-57
trap the round-10 verifier documented — **but they do fire on the regression class they exist for** (NC-PREMISE-REAL).
The lane's own negative control mutated the assertion's own threshold, which is close to a tautology; the
regression-class control (mine) is the one that shows the assert has teeth. Recorded as F8 (LOW, not blocking).

**Negative direction — the whole suite under 4 CPU burners** (`nproc` = 4, so the box is 2× oversubscribed):

```
LOAD-WITH-BURNERS 2.44 2.03 1.73      LOAD-END 7.45 4.81 2.90
96 passed in 204.20s (0:03:24)    PYTEST_RC=0
```
**No premise assert fired: 0 flakes in 1 loaded run** (96/96 green at 1-minute load 7.45, wall +21 % vs the idle
169 s). The lane introduced no contention flake at 2× oversubscription on this box.

## ITEM 5 — OWN-PID GRANDCHILD CLEANUP (F-B5e-12 / AF-AP-59)

### 5a. No world-scoped census remains — confirmed by exhaustive grep

```
grep -n 'pgrep|pkill|"ps"|ps -eo|psutil|listdir("/proc")'  tests/test_s0_01_frame_tee.py
  2662,2667  ["pgrep", "-P", str(tee_proc.pid)]   <- OWN child, scoped by the test's own tee pid
(no other pgrep/pkill/ps/psutil/proc-walk anywhere in the file)
grep -n '/proc/' -> 16 hits, every one `"/proc/%d/stat" % <pid the test itself obtained>`
```
**SOLID: the world-scoped census is gone; nothing enumerates the box.** AF-AP-59 is satisfied *for the code as it
stands*.

### 5b. `pytest -n 4` is not runnable here — substituted concurrent processes

`python3 -c "import xdist"` → `ModuleNotFoundError`. Substitute per the brief: **two pytest processes of the three
affected tests, concurrently, 5 rounds** (10 worker runs):

```
round1 A: 3 passed, 93 deselected in 63.69s   B: 3 passed … 63.65s
round2 A: 63.61s   B: 63.61s
round3 A: 63.58s   B: 63.73s
round4 A: 63.76s   B: 63.56s
round5 A: 63.59s   B: 63.68s
LOAD-START 4.97 → LOAD-END 6.05      post-run census of `time.sleep` processes: clean
```
**10/10 green, zero cross-test interference, zero surviving sleepers.** Each worker kills only the pid it recorded,
so a sibling worker's grandchild is untouched — the AF-AP-59 fix behaves as designed under concurrency.

### 5c. GRANDCHILD-UNKILLED dies on the own-pid assert — reproduced

```
GRANDCHILD-UNKILLED  KILLED  5.5s
  AssertionError: grandchild pid 18323 still alive after kill   (test:549)
  FAILED …::TestGrandchildStdout::test_grandchild_keeps_tee_alive
```

### 5d. **But the census is fail-open: the AF-AP-40 `exists()` guard is a silent hole (my brief's item (a))**

Mutant **PIDFILE-ABSENT** (mine): delete the three `if fd: open(.../grandchild.pid).write(str(gc.pid))` lines from
the fixture agents — the grandchildren are still spawned, nothing records their pids.

```
PIDFILE-ABSENT   named killers = the three affected tests
  3 passed, 93 deselected in 63.47s      <- ALL GREEN
ORPHAN CENSUS immediately after:
  23435  ppid 1  S  60s  /usr/local/bin/python3 -c import time; time.sleep(120)
```
**The exact defect F-B5e-12 was opened for — an orphaned grandchild at ppid 1 — comes back, and all three tests stay
green.** `if gc_pid_path.exists():` (`test:527`, `:1091`, `:2594`) makes the entire kill-and-assert optional; so does
the `if fd:` guard inside each agent source string, and so does the `except (OSError, ValueError): pass` around
`int(...)`. The lane's lint_delta note calls the AF-AP-40 hit a FALSE POSITIVE on the grounds that "absence means no
grandchild was spawned"; the measurement says absence means *the census does not run*. See F6.

## ITEM 6 — F-B5e-13, THE TWO `state` READS NOW INSIDE THE LOCK

* **Structurally closed and pinned:** LOCK-READS-OUT dies on `test_write_status_snapshot_and_rewrite_are_locked`
  (`stdin_reader_done is not read inside \`with lock:\``, test:2498), and the pin's `ast.dump` substring check
  reproduces identically on 3.11 / 3.12 / 3.13 (`stdin_in_lock=True errs_in_lock=True` on all three) — the lane's
  SELF-ATTACK #2 worry about `ast.dump` fragility is measured away.
* **Behaviourally the skew is essentially unobservable, and I could not build an instrument that sees it.**
  I built one (`vb11torn.py`): a leg where the agent exits (so the MAIN thread drives `_write_status` from the drain
  loops at 10 Hz, the only path where the reads were ever unlocked), a grandchild keeps streaming a2c (so a PUMP
  mutates `state` concurrently), and the client stops reading a2c so `forward a2c: BrokenPipeError` is appended at a
  definite seq. Inversion test: `N_max` (max `updated_seq` among statuses WITHOUT the error) must be < `E_min` (min
  `updated_seq` among statuses WITH it).

```
PIN             rep0/1/2  samples 1.42-1.43 M   E_min 43  N_max 42  inverted False
LOCK-READS-OUT  rep0/1/2  samples 1.43-1.49 M   E_min 43  N_max 42  inverted False
```
  **Neither tee inverts, in ~8.6 M samples.** The mechanism, re-derived from primary source: `lock` is an `RLock`
  (`frame_tee.py:127`) and both pumps call `_write_status()` *inside* their own `with lock:` (`:288`, `:374`), so the
  whole function — snapshot and file write — runs under the pump's already-held lock; the unlocked window exists only
  on the four main-thread calls (`:415`, `:426`, `:432`, `:461`). And both out-of-lock fields are *one-shot monotone*
  (`stdin_reader_done` flips once; `write_errors` is bounded to one entry per `(arm, direction)` by
  `_record_write_error`, `:137-153`), so the tear has a single microsecond-wide opportunity per run. F-B5e-13 was
  correctly rated INFO by the round-10 verifier, the fix is correct, and **the AST pin is the only instrument that can
  hold it** — which is what the lane shipped. No finding; recorded because the lane's DONE table calls the pin's kill
  of LOCK-READS-OUT a proof of behaviour, and it is a proof of *structure*.

## ITEM 7 — THE MUTANT TABLE, RE-RUN ON THE PIN (mine, 40 distinct mutants)

Venue/protocol as in item 3. sha256 of both scope files re-asserted after every mutant (`ac82dba82e2f` /
`05019a915ecf`, printed by the runner at the end of every batch); the shared tree's two scope files
`git status --porcelain`-clean before and after every batch.

| id | mutation | result | killer (NAMED) | reps |
|---|---|---|---|---|
| INSTALL-LATE | install+try below Popen+sha256 | **KILLED** | `test_sigterm_during_sha256_produces_status` (`-15 == 70`) **and** `test_no_statement_between_signal_and_try` (`Popen precedes the handler install`) — the AST pin now catches it too, which it did not in round 10 | 1 |
| GAP-1 | one statement between install and try | **KILLED** | `test_no_statement_between_signal_and_try` (`statement after signal.signal is Assign at line 213`) | 1 |
| EXCEPT-WRONG | `except Exception:` | **KILLED** | `test_sigterm_writes_status_and_exits_70` + `test_sigterm_during_sha256_produces_status` (`1 == 70`) | 1 |
| EXIT-0 | `os._exit(0)` | **KILLED** | same two (`0 == 70`) | 1 |
| STATUS-FINAL-TRUE | `final=True` on the TERM write | **KILLED** | same two | 1 |
| ERR-MISSING | no `terminated: SIGTERM` append | **KILLED** | same two (`[] == ['terminated: SIGTERM']`) | 1 |
| ORPHAN | drop `proc.terminate()` | **KILLED** | `test_sigterm_kills_agent_child` (`agent pid 29605 state S after 2 s`) | 1 |
| **TRY-SHRINK2** | try covers ONLY Popen; the rest outside every catcher | **KILLED** | `test_sigterm_writes_status_and_exits_70` + `test_sigterm_during_sha256_produces_status` — **the lane's PATCH-FAILED row is now measured** | 1 |
| N3 | swap tl/df order, both pumps | **KILLED** | `test_timeline_before_directional_in_pumps` | 1 |
| PUMP-TIMEOUT | 5 s select timeout inside `pump_pipe` | **KILLED** | `test_grandchild_straggler_recorded` + `test_grandchild_never_closes_sigterm_required` | 1 |
| A2-t0/t1/t5/t30 | c2a drain bounded 0/1/5/30 s | **KILLED ×4** | `test_drain_loops_have_no_break_or_timeout` | 1 ea |
| a2c-t0 / a2c-t5 | a2c drain bounded 0 / 5 s | **KILLED ×2** | straggler + structural pin | 1 ea |
| a2c-t30 | a2c drain bounded 30 s | **KILLED** | structural pin only (the 6 s straggler cannot see 30 s — F-B5e-9's wording is correct) | 1 |
| A2C-DELETE | delete the a2c drain loop | **KILLED** | straggler + structural pin | 1 |
| A2C-WRONG-THREAD | a2c drain waits on `ti` | **KILLED** | `test_grandchild_straggler_recorded` only | 1 |
| S1 | status before the timeline line, both pumps | **KILLED 3/3** | AST pin | 3 |
| S1F (faithful, invariant-1 preserved) | as above but after the recorded counter | **KILLED 3/3** AST · **5/5** on the 12-trial lag · **0/5** on the single-sample lag | | 3+5+5 |
| N4 | seq snapshot outside `with lock:` | **KILLED 3/3** | AST pin | 3 |
| D3 | drop `status_lock` | **KILLED 3/3** | AST pin | 3 |
| INSTALL-LATE-B | Popen above install | **KILLED** | AST pin | 1 |
| NO-PREINIT | drop `proc = None` | **KILLED** | AST pin | 1 |
| LOCK-READS-OUT | the two reads back outside the lock | **KILLED** | AST pin | 1 |
| DOCSTRING-TERM | old `TERMs/KILLs` wording | **KILLED** | doc-anchor test | 1 |
| GRANDCHILD-UNKILLED | drop the `finally` kill | **KILLED** | own-pid assert (test:549) | 1 |
| DRAIN-ORDER | c2a drain before a2c drain | **EQUIVALENT** — `2 passed` named, `96 passed in 169.96s` full suite. Both loops are pure 10 Hz waits, the pumps drain in their own threads, and `tl.close()` follows both; termination is identical. Accepted. | 1 |
| **DOCSTRING-HYBRID** *(new)* | docstring keeps `SIGKILL`+`acp.rs`, loses `TERMs/KILLs`, re-asserts the false SIGTERM-bounds-the-leg claim | **SURVIVED** `96 passed in 169.16s` | 1 |
| **COMMENT-TERM** *(new)* | revert the two in-code comments only | **SURVIVED (named)**; provably invisible — the pin reads `ast.get_docstring(module)`, comments are not in the AST and no test greps the source | 1 |
| **PIDFILE-ABSENT** *(new)* | fixture agents never write `grandchild.pid` | **SURVIVED** `3 passed` + a live ppid-1 orphan | 1 |
| **CENSUS-WORLD** *(new)* | revert the census to a world-scoped `pgrep -f "import time; time.sleep"` + `assert stdout == ""` | **SURVIVED (named)** `3 passed, 93 deselected in 63.53s` | 1 |
| **LAG-12-DROPPED** *(new)* | delete the per-trial lag assertion | **SURVIVED** `96 passed in 170.39s` | 1 |
| **PIN-LOCK-NAME** *(new)* | rename `status_lock`→`stlock` in the tee **and** the pin | **SURVIVED** `96 passed in 169.57s` | 1 |
| **MIRROR-SNAPSHOT** *(new)* | lock-snapshot kept (pin passes), every field re-read outside the lock | **SURVIVED** `96 passed in 169.50s` | 1 |
| **MIRROR-PREINIT** *(new)* | `proc = None` kept (pin passes), `proc = 0` right after it | **SURVIVED** `96 passed in 169.89s` | 1 |
| **MIRROR-S1-FLUSH** *(new)* | `tl.write` before `_write_status` (pin passes), `tl.flush()` moved after | **KILLED** | `test_directional_trails_timeline_after_sigkill` (`dir a2c (391) > timeline a2c (390)`, test:2115) | 1 |
| **PIN-NULLLOCK** *(new)* | `with status_lock:` kept (pin passes), `status_lock = contextlib.nullcontext()` | **KILLED** | race test: `2 torn reads out of 2590665` (test:2621) | 1 |
| **PIN-NULLLOCK-L** *(new)* | `with lock:` kept everywhere (pin passes), `lock = contextlib.nullcontext()` | **KILLED** | race test: `16 snapshots where updated_seq != recorded_c2a + recorded_a2c` (test:2622) | 1 |
| **NC-FLAG-LOOPONLY / NC-VALUE-LOOPONLY-501 / NC-VALUE-BOTH-501 / NC-PREMISE-REAL-501** | item 4 | KILLED / SURVIVED / KILLED / KILLED | | 1 ea |

```
TOTAL 40 distinct mutants
  KILLED-BY-NAMED  27   INSTALL-LATE GAP-1 EXCEPT-WRONG EXIT-0 STATUS-FINAL-TRUE ERR-MISSING ORPHAN
                        TRY-SHRINK2 N3 PUMP-TIMEOUT A2-t0/t1/t5/t30 a2c-t0/t5/t30 A2C-DELETE
                        A2C-WRONG-THREAD S1(3/3) S1F(3/3) N4(3/3) D3(3/3) INSTALL-LATE-B NO-PREINIT
                        LOCK-READS-OUT DOCSTRING-TERM GRANDCHILD-UNKILLED MIRROR-S1-FLUSH
                        PIN-NULLLOCK PIN-NULLLOCK-L
  EQUIVALENT        1   DRAIN-ORDER
  SURVIVED (real)   7   DOCSTRING-HYBRID  COMMENT-TERM  PIDFILE-ABSENT  CENSUS-WORLD
                        MIRROR-SNAPSHOT  MIRROR-PREINIT  PIN-LOCK-NAME
  (LAG-12-DROPPED is an assertion deletion, not a code mutant — excluded from the denominators)
  PATCH-FAILED      0
```

## ITEM 10a — EVERY `file:line` IN THE LANE REPORT, SPOT-CHECKED ON THE PIN

The lane brief said "**Every file:line on the FINAL tree**". Fourteen of the sixteen refs in the DONE table are wrong.

| lane report claims | actual on the PIN | delta |
|---|---|---|
| `frame_tee.py:16-23` docstring | new sentences at `:18-23`, block ends `:25` | ~2 |
| `frame_tee.py:420-421` comment | `:421-423` (`:420` is `proc.wait()`) | 1-2 |
| `frame_tee.py:426-427` comment | `:427-429` (`:426` is `_write_status()`) | 1-2 |
| `frame_tee.py:168-169` state reads | **`:171-172`** | 3 |
| `test:2800-2813` doc-anchor test | **`:2851-2862`** | 51 |
| `test:2424-2441` S1 pin | **`:2459-2476`** | 35 |
| `test:2443-2479` N4/D3 pin | **`:2478-2504`** | 35 |
| `test:2700-2704` Popen assert | **`:2745-2750`** | 45 |
| `test:2706-2712` preinit assert | **`:2751-2757`** | 45 |
| `test:1568,1575-1576,1631` flag form | **`:1643, :1649-1650, :1655`** | 24-75 |
| `test:500,512-513` value form | `:502, :513-514` | 1-2 |
| `test:463-470` grandchild pid write | `:466-471` | 1-3 |
| `test:524-550` kill+assert | `:524-550` ✔ | 0 |
| `test:2093-2101` lag assertion | **`:2117-2126`** | 24 |
| `test:2736,2744` identity pre-bind | **`:2796, :2807`** | 60 |
| `test:2524-2531` window docstring | **`:2633-2638`** | 109 |
| `test:919-921` straggler docstring | **`:953-957`** | 34 |
| `test:820-826 / 984-990 / 1381-1388` three docstrings | **`:853-857 / :1017-1021 / :1454-1457`** | 33-73 |
| `test:2809` red-state line ref | **`:2859`** | 50 |
| `test:527,1091,2594` (lint_delta AF-AP-40) | `:527, :1091, :2594` ✔ | 0 |
| `test:469,1032,2527` (lint_delta AP-1) | `:469, :1034, :2529` | 0-2 |

The two ranges the lane pasted from a *tool* (lint_delta) are right; the ones it typed are wrong. AF-AP-37's class,
applied to line numbers instead of counts. See F7.

### Popen census — re-measured by AST, not carried over

```
AST Popen call sites total: 27      name-bound: 27   unbound: 0
raw textual 'Popen(' occurrences: 31     inside string literals: 4
```
**Reproduces the lane's numbers exactly.** F-B5e-10 closed.

### The AST pins are not 3.11-specific (item 9, part)

Same pin logic re-implemented and run standalone under three interpreters against the PIN tee:
```
3.11.15  pumps={'pump_fd': (277, 288, True), 'pump_pipe': (363, 374, True)} locks=['lock','status_lock']
         stdin_in_lock=True errs_in_lock=True next_after_install=Try popen_before=False preinit=True
         doc_SIGKILL=True doc_acprs=True doc_no_TERMsKILLs=True
3.12.3   identical
3.13.12  identical
```


## ITEM 9 — INTERPRETERS

| interpreter | pytest | what I ran |
|---|---|---|
| **3.11.15** (`/usr/local/bin/python3`, the gate interpreter) | 9.1.1 | everything in this report |
| **3.12.3** (`/usr/bin/python3.12`, CI's) | **NOT installed** | the four AST pins (identical results) **and** the tee's real SIGTERM behaviour, standalone |
| 3.13.12 | not installed | the four AST pins (identical results) |

Standalone SIGTERM-window probe (`vb11py312.py`, no pytest), 6 reps per mode per interpreter:
```
3.11  POLL n=6 rc={70: 6} status_present=6/6  write_errors ["terminated: SIGTERM"] final false updated_seq 0
3.11  t=0  n=6 rc={-15: 6} status_present=0/6
3.12  POLL n=6 rc={70: 6} status_present=6/6  (identical last-status object)
3.12  t=0  n=6 rc={-15: 6} status_present=0/6
```
**The tee behaves identically on CI's interpreter**, and the docstring's "uncovered window → rc −15, no status file"
reproduces 6/6 on both. **Could not run:** the pytest suite on 3.12 (no pytest, no network install attempted).

## ITEM 10b — REPORT DISCIPLINE, THE REST

```
tripwire  test_sigterm_status_satisfies_check_tee_status   1 passed, 95 deselected in 0.25s
pyflakes  both scope files                                  rc 0
lint_delta --base 9b2803c (the PIN's parent):
  5 .py changed, 0 NEW pyflakes hit(s), 0 removed
  AP-1      tests/test_s0_01_frame_tee.py:469  :1032  :2527   (os.environ.get inside agent source strings)
  AF-AP-40  tests/test_s0_01_frame_tee.py:527  :1091  :2594  **:2120**
```
(The lane's own `--base origin/...` line is no longer reproducible: origin has moved to `fc35fbb`, which already
contains the PIN, so lint_delta against it reports `0 .py changed`. I re-based on `9b2803c`, the PIN's parent, which
is exactly the B5f delta.)

**Process census across two idle full suites** (PIN venue, load 1.24 → 2.33):
```
--- census PRE ---          31960  1  Z  [agent.py] <defunct>          live leaks: 0
=== IDLE SUITE RUN 1 ===    96 passed in 169.57s (0:02:49)
--- census POST-RUN-1 ---   407 1 Z [big_agent.py] <defunct>, 410 1 Z [agent.py] <defunct>   live leaks: 0
=== IDLE SUITE RUN 2 ===    96 passed in 170.44s (0:02:50)
--- census POST-RUN-2 ---   1370 1 Z [big_agent.py], 1372 1 Z [agent.py]                     live leaks: 0
--- delayed census (+~40 s) ---   (clean — every zombie reaped)
df -h /  ->  /dev/vda 252G 27G 11G 71%
```
**Zero live leaks after either suite; the only survivors are reaped zombies.** The F-B5e-12 orphan class is closed on
the PIN — which is exactly why F6 (the fail-open guard) matters: the fix works, and nothing gates it.

## ITEM 11 (mine) — THE MECHANISM BEHIND THE `proc = None` PIN, REPRODUCED

Three scratchpad tees, each with `time.sleep(0.6)` injected as the FIRST statement of the `try` (so the
install→Popen window is real and wide); TERM at 0.25 s; 3 reps each:

```
PIN             rc 70  status true  write_errors ["terminated: SIGTERM"]      3/3
NO-PREINIT      rc 1   status true  stderr: UnboundLocalError: cannot access local variable 'proc' …   3/3
MIRROR-PREINIT  rc 1   status true  stderr: AttributeError: 'int' object has no attribute 'terminate'  3/3
```
**F-B5e-6 guards a real failure** (rc 1 instead of 70, after the status write) — the AST pin is not decorative. It is
also the exact evidence that the pin's `any(...)` quantifier is too weak (F11).

## ITEM 1 — F-B5e-1…18 CLOSURE TABLE (one row each)

| # | round-10 finding | lane's claim | my verdict (all reproduced unless stated) |
|---|---|---|---|
| **F-B5e-1** [BLOCKING] docstring's justification false at the pin | docstring + 2 comments + 3 test docstrings reworded; doc-anchor test added | **PARTLY CLOSED.** The *module docstring* is now accurate — every clause re-derived from `acp.rs` @ `1c8321cd` (sha256 re-fetched, matches). But **the two comments and all three test docstrings say "buzz-acp SIGKILLs the group AFTER 5 s", which inverts the source** (kill first, then wait ≤ 5 s; no `from_secs(5)` precedes any kill) — **F3**. And the anchor is a **string-only tautology**: DOCSTRING-HYBRID (SIGKILL + acp.rs present, false claim restored) → `96 passed` — **F4**. |
| **F-B5e-2** [BLOCKING] S1 ungated (1/16) | AST pin + 12-trial lag assertion | **CLOSED, and better than claimed.** AST pin kills S1 **3/3** and faithful S1F **3/3**, in 0.10 s. The 12-trial lag assertion independently kills S1F **5/5** where the old single-sample test kills **0/5**. |
| **F-B5e-3** [BLOCKING] N4 78 % / D3 56 % | AST pin `test_write_status_snapshot_and_rewrite_are_locked` | **CLOSED for the shape (N4 3/3, D3 3/3, deterministic), NOT for the semantics** — MIRROR-SNAPSHOT (locked snapshot kept, every field re-read unlocked) passes the pin, the race test 0/5, and the full suite — **F5**. |
| **F-B5e-4** [BLOCKING] red state was `-x` on the wrong baseline | full suite, no `-x`, on 736bb94: `7 failed, 89 passed` | **NOT CLOSED.** My run on the same parent, same tests, no `-x`: **`8 failed, 88 passed in 171.80s`**; one row the lane calls a GREEN CONTROL is a deterministic RED (**F1**), one row it lists as RED passes 5/5 in isolation and one it calls "flaky" fails 5/5 (**F2**). |
| **F-B5e-5** [MED] Popen-before-install invisible | assert added to the F13 AST pin | **CLOSED.** INSTALL-LATE-B **KILLED** (`Popen precedes the handler install`, test:2746); INSTALL-LATE is now killed by the pin *as well as* the behavioural test (it was not in round 10). |
| **F-B5e-6** [MED] `proc = None` ungated | assert added to the F13 AST pin | **CLOSED for the deletion, open for a rebinding.** NO-PREINIT **KILLED**. The guarded behaviour is real (injected-window probe: PIN rc 70 3/3, NO-PREINIT rc 1 + `UnboundLocalError` 3/3). But the pin's `any(...)` lets MIRROR-PREINIT (`proc = None` then `proc = 0`) through — full suite `96 passed`, real behaviour rc 1 + `AttributeError` 3/3 — **F11**. |
| **F-B5e-7** [MED] contention test vacuous | FLAG form at `test:1643/1650/1655` | **CLOSED, verified under the sharp control.** Loop-only threshold mutation → **KILLED**, `no contention: the wait for updated_seq >= 100 timed out` (test:1655). |
| **F-B5e-8** [LOW] window-test mechanism misstated | docstring rewritten to the structural guarantee | **CLOSED.** `test:2633-2638` now states the `pgrep -P` / fork ordering and calls the 234 MB entrypoint load insurance. Prose matches the round-10 measurement. |
| **F-B5e-9** [LOW] straggler docstring overstates | "kills 0 and 5 s; 30 s is the structural pin's" | **CLOSED and re-measured:** a2c-t30 dies on the structural pin ONLY; a2c-t0/t5 die on both. The new wording is exactly right. |
| **F-B5e-10** [LOW] Popen census carried over | 27 AST sites pasted from the tool | **CLOSED.** My own AST census: 27 call sites, 27 name-bound, 31 raw textual, 4 in string literals — identical. |
| **F-B5e-11** [LOW] four success-only waits | FLAG at `:1655`, VALUE at `:513/:902/:1075` | **PARTLY CLOSED.** The four named sites are fixed and the value form fires on the real regression (NC-PREMISE-REAL, `1 failed`). But the *fifth* site of the same class — the coordinator's own tripwire, `test_sigterm_status_satisfies_check_tee_status` (`test:2279-2320`) — has **no premise assert at all** and is **vacuous**: loop-only mutation → `1 passed in 10.30s` — **F9**. And the lane's negative control for the value form mutated the assertion's own threshold — **F8**. |
| **F-B5e-12** [LOW] fixture grandchildren orphaned | own-pid write + `finally` kill + own-pid assert (AF-AP-59) | **CLOSED in the code, NOT gated.** No world-scoped census remains (exhaustive grep); 10/10 green under two concurrent pytest processes × 5 rounds; GRANDCHILD-UNKILLED **KILLED** on the own-pid assert; zero live leaks over two suites. But PIDFILE-ABSENT → `3 passed` **and a live ppid-1 orphan** — the `exists()` guard makes the whole census optional — **F6**. |
| **F-B5e-13** [INFO] two `state` reads outside the lock | both moved inside; pinned by `ast.dump` substring | **CLOSED structurally.** LOCK-READS-OUT **KILLED** (test:2498); the `ast.dump` check reproduces on 3.11/3.12/3.13, so SELF-ATTACK #2's fragility worry is measured away. Behaviourally the skew is unobservable with the current fields (item 6, 8.6 M samples, 0 inversions on either tee) — the AST pin is the right and only instrument. |
| **F-B5e-14** [INFO] `identity` unbound on timeout | `identity = None` + assert with a reason | **CLOSED.** `test:2796` / `:2807` (`runtime-identity.json never appeared`). |
| **F-B5e-15** [INFO] AF-AP-45 screen false positives | (coordinator item) | **NOT APPLICABLE this round** — the B5f delta produces **zero** AF-AP-45 hits (it adds `open("/proc/…/stat")`, not `exists()`). Carry-forward unchanged. |
| **F-B5e-16** [INFO] premise shift during the run | n/a | **RECURRED, grade unaffected.** During my run HEAD moved `4b43284` → `c4805df` (D5i) → `f0ae7eb` → `fc35fbb`. `git diff PIN fc35fbb -- <both scope files>` is EMPTY and the worktree copies still hash `ac82dba…` / `05019a91…`, `git status --porcelain`-clean. **F17.** |
| **F-B5e-17** [INFO] UNSURE `os.makedirs` in the uncovered window | not addressed (not in the brief) | **UNCHANGED.** `frame_tee.py:120` still sits in the pre-install window and `:23-25` still attributes the whole window to "Python interpreter startup". Carry-forward — **F18**. |
| **F-B5e-18** [INFO] UNSURE TERM against a wedged pump | not addressed (not in the brief) | **UNCHANGED but better covered:** its only cover, `test_sigterm_no_deadlock_under_contention`, is no longer vacuous (F-B5e-7 closed). Still not reproduced by anyone. |

### Every new/changed test against the TRUE parent tee (`736bb94`), individually

| test | on parent | lane's label | my label |
|---|---|---|---|
| `test_docstring_names_the_pinned_shutdown_signal` | **RED** `module docstring does not name SIGKILL` (test:2859) | genuine-red | **agree** |
| `test_status_write_follows_timeline_write_in_pumps` | GREEN (0.05 s) | CONTROL — kills S1 | **agree** (S1 3/3, S1F 3/3) |
| `test_write_status_snapshot_and_rewrite_are_locked` | **RED** `stdin_reader_done is not read inside \`with lock:\`` (test:2498), 0.15 s, deterministic | **GREEN / CONTROL** | **DISAGREE — F1** |
| `test_grandchild_straggler_recorded` | **RED** 5/5 | genuine-red | agree |
| `test_grandchild_never_closes_sigterm_required` | **RED** | genuine-red | agree |
| `test_drain_loops_have_no_break_or_timeout` | **RED** (test:2411) | genuine-red | agree |
| `test_sigterm_during_sha256_produces_status` | **RED** | genuine-red | agree |
| `test_no_statement_between_signal_and_try` | **RED** (test:2742) | genuine-red | agree |
| `test_sigterm_kills_agent_child` | **RED 5/5 in isolation** | "genuine-red (flaky on parent)", not in the pasted 7 | **DISAGREE — F2**: deterministic here |
| `test_sigterm_status_satisfies_check_tee_status` | **GREEN 5/5 in isolation**, GREEN in my full suite | listed as RED (`rc -15 != 70`) | **DISAGREE — F2**; the lane's `rc -15` is F9's vacuity firing on a loaded box |
| the three own-pid `finally` blocks | GREEN on the parent | (not labelled) | CONTROL — kills GRANDCHILD-UNKILLED |
| the four premise asserts | GREEN on the parent | (not labelled) | CONTROL — kills NC-FLAG-LOOPONLY / NC-PREMISE-REAL |

---

# FINDINGS

**F1 [BLOCKING] SOLID — the report's RED STATE does not reproduce, and one row of its red-state table is
deterministically wrong: `test_write_status_snapshot_and_rewrite_are_locked` is RED on the parent, not a GREEN
CONTROL.**
`tasks/briefs/s0-01-b5f-support/B5f-report.md` § RED STATE + the classification table (row 2), and
`tests/test_s0_01_frame_tee.py:2496-2501`.
*Observed vs expected:* expected the lane's `7 failed, 89 passed`. Observed, same parent (`736bb94`, sha256
`3fc846ce…`, 476 lines), same PIN tests, no `-x`: **`8 failed, 88 passed in 171.80s  PYTEST_RC=1`**. The extra failure
is `TestStructuralPins::test_write_status_snapshot_and_rewrite_are_locked`, which the report's table lists as
"on parent 736bb94: **GREEN** | CONTROL — kills N4, D3, LOCK-READS-OUT". Run alone against the parent tee it fails in
**0.15 s** at `test:2498` — `assert "stdin_reader_done" in lock_src` — because the F-B5e-13 fix that moves those two
reads inside `with lock:` is part of this lane's own tee change. There is no timing component; this is not a flake.
*Failing input:* `git show 736bb94:proofs/S0-01/tools/frame_tee.py` + PIN tests, `-k test_write_status_snapshot_and_rewrite_are_locked`.
*Minimal fix:* re-paste the red state from a real full-suite run and move that row from "CONTROL" to "genuine-red"
(it is a stronger claim for the lane, not a weaker one — the test is BOTH a control for N4/D3 and a regression test
for F-B5e-13).
*Exact red test to add:* none — the test already exists; the report is what is wrong.

**F2 [MED] SOLID — the red list contains a row that passes 5/5 in isolation and omits one that fails 5/5.**
Same report section.
*Observed vs expected:* the report lists `TestSigtermStatusVsChecker::test_sigterm_status_satisfies_check_tee_status`
as RED on the parent with `rc -15 != 70`. On my parent venue it is **`1 passed` 5/5** (0.20–0.21 s each) and it passed
inside my full-suite red run. Conversely `TestSigtermTerminatesAgent::test_sigterm_kills_agent_child`, which the
report calls "flaky on the parent tee" and leaves out of the pasted 7, fails **5/5 in isolation** (2.17–2.22 s) and
failed in my full-suite run. The lane's `rc -15` is explainable and is itself a finding: see **F9** — that test's
success-only wait can time out under load, and on the parent tee (handler installed after Popen + sha256) the
resulting TERM lands pre-install → `rc -15`.
*Minimal fix:* re-paste from a real run; label `test_sigterm_kills_agent_child` genuine-red (it is), and drop the
tripwire row or annotate it as load-dependent with the mechanism.

**F3 [BLOCKING] SOLID — five committed artifacts state a shutdown ordering the pinned source contradicts: they say
buzz-acp SIGKILLs "after 5 s"; buzz-acp SIGKILLs FIRST and then waits up to 5 s.**
`proofs/S0-01/tools/frame_tee.py:422-423` and `:428-429`; `tests/test_s0_01_frame_tee.py:853-854`, `:1017-1018`,
`:1454-1455`.
*Observed vs expected:* the artifacts read *"buzz-acp SIGKILLs the group after 5 s (acp.rs:421-444, pinned 1c8321cd)"*.
Primary source, re-fetched this session (sha256 `44e82861763694d2b82d02b15ee100ffd6c78874a2b2282865e6656c539c38f1`,
5030 lines, matching the round-10 verifier byte-for-byte): `AcpClient::shutdown` (`acp.rs:422-444`) calls
`kill_process_group(pid)` → `killpg(…, SIGKILL)` (`:2328`) **immediately**, then
`tokio::time::timeout(Duration::from_secs(5), self.child.wait())` (`:439`) with the comment *"Bounded wait: if the
child doesn't exit within 5s **after SIGKILL**, give up"* (`:436-437`). `grep -n "from_secs(5)"` over the file: the
only production occurrence is that post-kill wait; every other is inside `#[cfg(test)] mod tests` (opens at `:2351`).
There is no 5-second delay before any kill anywhere in the file.
*Failing input:* a reader (or the next lane) deriving a timing budget from these comments: they will allow the tee 5 s
of grace that does not exist. The wedged leg is killed at t≈0, not t≈5 s.
*Minimal fix:* replace "SIGKILLs the group after 5 s" with the module docstring's own correct wording in all five
places (regex-located: `frame_tee.py:422`, `:428`; `tests/test_s0_01_frame_tee.py:853`, `:1019`, `:1454`) — "SIGKILLs the group (`killpg`) and then waits up to 5 s for it to exit".
*Exact red test to add:* extend `test_docstring_names_the_pinned_shutdown_signal` to read the tee source and assert
`"SIGKILLs the group after 5 s" not in source`, and to assert the same three test docstrings via
`ast.get_docstring` on those three `FunctionDef`s. Red today at five sites.

**F4 [BLOCKING] SOLID — the doc-anchor test is a string-only tautology: a docstring that names SIGKILL and acp.rs and
still asserts the false SIGTERM bound passes the whole suite.**
`tests/test_s0_01_frame_tee.py:2851-2862`.
*Observed vs expected:* the pin asserts three tokens (`"SIGKILL" in doc`, `"acp.rs" in doc`,
`"TERMs/KILLs" not in doc`). Mutant **DOCSTRING-HYBRID** rewrites `frame_tee.py:18-25` to
*"…buzz-acp ends such a leg with `killpg(SIGKILL)` … and the SIGTERM path below is what bounds a wedged leg: it
records `terminated: SIGTERM` so every wedged leg leaves a reason"* — the exact claim F-B5e-1 was opened to remove.
Result: **`1 passed` named, `96 passed in 169.16s` full suite**. The negative token is an exact-string blacklist, so
`TERMs / KILLs`, `TERMs and KILLs`, or any paraphrase also evades it. And the pin reads
`ast.get_docstring(tree)` — the *module* docstring only — so mutant **COMMENT-TERM** (both in-code comments reverted
to the old wording) survives by construction, as would any revert of the three test docstrings.
*Failing input:* the DOCSTRING-HYBRID text above, or simply re-wording "TERMs/KILLs" as "TERMs / KILLs".
*Minimal fix:* pin the MEANING, not the tokens: assert the docstring contains `killpg` **and** `SIGKILL cannot be
handled` **and** `last RUNNING status`, and that it does **not** contain the regex
`SIGTERM path[^.]*(covers it|bounds)` — plus extend the scan to the whole source file and to the three test
docstrings (F3's fix).
*Exact red test to add:*
```python
def test_docstring_pins_the_meaning_not_the_tokens(self):
    src = Path(TEE).read_text()
    doc = ast.get_docstring(ast.parse(src))
    assert "killpg" in doc and "SIGKILL cannot be handled" in doc and "last RUNNING status" in doc
    assert not re.search(r"SIGTERM path[^.]*(covers it|bounds)", doc), \
        "docstring still claims the SIGTERM path bounds a wedged leg"
    assert not re.search(r"SIGKILLs[\s#]+the[\s#]+group[\s#]+after[\s#]*5[\s#]*s", src), \
        "buzz-acp SIGKILLs first and then waits <=5s; it does not wait 5s before killing"
```
(The wrap-tolerant regex is required: the phrase is broken across lines at four of its five sites, so a literal
`"SIGKILLs the group after 5 s" not in src` misses them — I ran the literal form first and it passed on the PIN,
which is why this line reads as it does.) **RUN:** on the PIN the first two assertions PASS and the third is
**RED at 5 sites** — `frame_tee.py:422`, `:428`; `tests/test_s0_01_frame_tee.py:853`, `:1019`, `:1454`. On
DOCSTRING-HYBRID and DOCSTRING-TERM the first assertion is already RED.

**F5 [MED] SOLID — the new N4/D3 pin is a MIRROR for the defect it names: a tee with exactly the N4 semantics passes
the pin, the race test 0/5, and the full suite.**
`tests/test_s0_01_frame_tee.py:2478-2504`.
*Observed vs expected:* the pin asserts only that a `with lock:` **containing a `seq` Name** exists in `_write_status`,
and that `stdin_reader_done`/`write_errors` appear in that block's `ast.dump`. Mutant **MIRROR-SNAPSHOT** keeps that
block intact and adds, immediately after it, an *unlocked* re-read of all seven fields into the same names — the
published object is then a non-atomic read, which is precisely N4. Result: pin **PASSES**;
`test_concurrent_main_thread_status_vs_pump` **passes 5/5** (45.2–45.8 s each); full suite **`96 passed in 169.50s`**.
For contrast, the pins are *not* mirrors for outright lock removal: **PIN-NULLLOCK**
(`status_lock = contextlib.nullcontext()`) dies on the race test with `2 torn reads out of 2590665` and
**PIN-NULLLOCK-L** (`lock = nullcontext()`) with `16 snapshots where updated_seq != recorded_c2a + recorded_a2c`.
*Failing input:* the MIRROR-SNAPSHOT diff (7 unlocked re-reads appended after the locked snapshot).
*Minimal fix:* pin the DATAFLOW, not the presence: assert that every value the published `obj` dict uses is a name
bound **inside** the `with lock:` block, and that no `state[...]` subscript or `seq[0]` read occurs in `_write_status`
outside it.
*Exact red test to add:*
```python
def test_write_status_reads_no_state_outside_the_lock(self):
    ws = next(n for n in ast.walk(ast.parse(Path(TEE).read_text()))
              if isinstance(n, ast.FunctionDef) and n.name == "_write_status")
    wl = next(n for n in ast.walk(ws) if isinstance(n, ast.With)
              and any(getattr(i.context_expr, "id", "") == "lock" for i in n.items))
    inside = {id(n) for n in ast.walk(wl)}
    stray = [n.lineno for n in ast.walk(ws)
             if isinstance(n, ast.Subscript) and getattr(n.value, "id", "") in ("state", "seq")
             and id(n) not in inside]
    assert not stray, "state/seq read outside `with lock:` at %s" % stray
```
**RUN:** PIN **PASS** · MIRROR-SNAPSHOT **RED** (`state/seq read outside \`with lock:\` at [174,175,176,177,…]`) · N4 **RED** · LOCK-READS-OUT **RED** (`[177, 182]`) · D3 **PASS** — so this is an ADDITION beside the existing `status_lock`/`os.replace` assertion, not a replacement for it.

**F6 [BLOCKING] SOLID — the own-pid grandchild census is fail-open: with the pid file absent every kill+assert is
silently skipped, all three tests stay green, and the ppid-1 orphan F-B5e-12 was opened for comes straight back.**
`tests/test_s0_01_frame_tee.py:527`, `:1091`, `:2594` (`if gc_pid_path.exists():`), plus the `if fd:` guard inside each
agent source string (`:469-471`, `:1032-1034`, `:2527-2529`) and the `except (OSError, ValueError): pass` at
`:531-532` / `:1095-1096` / `:2598-2599`.
*Observed vs expected:* the guard is supposed to skip only when no grandchild was spawned. Mutant **PIDFILE-ABSENT**
deletes the three pid-file writes (the grandchildren are still spawned):
```
3 passed, 93 deselected in 63.47s              <- all three affected tests GREEN
ps: 23435  ppid 1  S  60s  /usr/local/bin/python3 -c import time; time.sleep(120)
```
The lane's DISCREPANCIES section rules the AF-AP-40 screen hit a FALSE POSITIVE because "absence means no grandchild
was spawned". Absence means **the census does not run**. Three independent silent-skip paths (`if fd:`,
`if …exists():`, `except …: pass`) each defeat the entire F-B5e-12 fix while the suite stays green — the AF-AP-40
class exactly as the registry states it.
*Why the guard is unnecessary:* in both grandchild tests the body has already asserted the tee is alive at 3 s /15 s,
which is only possible **because** a grandchild holds the agent's stdout; and the agent writes `grandchild.pid`
before `sys.exit(0)`, i.e. before `proc.wait()` returns in the tee. The file must exist by the time `finally` runs.
*Minimal fix:* `assert gc_pid_path.exists(), "agent never wrote grandchild.pid"` before the read, and let the
`int()`/`os.kill` failure paths raise rather than `pass` (keep only `ProcessLookupError`, which means "already gone").
*Exact red test to add:* the unconditional assert, **RUN both ways**:
```python
gc_pid_path = framedir / "grandchild.pid"
assert gc_pid_path.exists(), "agent never wrote grandchild.pid"
```
applied at all three sites — PIN: `3 passed, 93 deselected in 63.68s`; under PIDFILE-ABSENT: **KILLED**,
`AssertionError: agent never wrote grandchild.pid` (test:1087). The pid file was present in 10/10 concurrent runs and
in every PIN run I made, so the assert adds no flake.

**F7 [BLOCKING] SOLID — fourteen of the sixteen typed `file:line` refs in the DONE table are wrong on the FINAL tree,
by up to 109 lines.** (The lane brief's item 9: "Every file:line on the FINAL tree".)
`tasks/briefs/s0-01-b5f-support/B5f-report.md` § DONE TABLE.
*Observed vs expected:* full table in item 10a above. Worst offenders: `test:2524-2531` for the window docstring
(actual `:2633-2638`, **+109**); `test:2736,2744` for the identity pre-bind (actual `:2796, :2807`, **+60**);
`test:2800-2813` for the doc-anchor test (actual `:2851-2862`, **+51**); `test:2700-2712` for the two F13 asserts
(actual `:2745-2757`, **+45**). `frame_tee.py:168-169` for the moved state reads is actually `:171-172`. The only
correct ranges are the two pasted from a tool (lint_delta) and `test:524-550`.
*Failing input:* open `tests/test_s0_01_frame_tee.py` at the report's line 2524 — you land in the middle of a
fixture's agent source string, not on the window docstring.
*Minimal fix:* regenerate the DONE table's refs from `grep -n` on the final tree (as I did) rather than from an
in-flight editor state. Same AF-AP-37 discipline as test counts: paste, never type.

**F8 [LOW] SOLID — the three VALUE-form premise asserts are vacuous under the sharp negative control, and the lane's
own negative control mutated the assertion's own threshold.**
`tests/test_s0_01_frame_tee.py:513-514`, `:902-903`, `:1075-1076`; report § PROBE TABLE
("VALUE neg control (T:501 threshold -> 10**9)").
*Observed vs expected:* mutating only the **loop's** break threshold (`test:508` → `>= 10**9`) leaves the test
**GREEN** (`1 passed, 95 deselected in 13.34s`) — `s` is rebound on every read, so after a timeout it holds the last
status, whose `recorded_a2c` is ≥ 1. That is the exact AF-AP-57 shape the round-10 verifier documented for
`T:1566`. Mutating **both** thresholds (the lane's control) is close to a tautology: it proves an assert fires when
its own constant is unreachable. *In mitigation, and measured:* the regression these three exist for **does** fire
them — mutant **NC-PREMISE-REAL-501** (the fixture agent never emits the handshake response, so the tee records no a2c
frame) → `1 failed`, `no a2c frame recorded before the liveness window`. So the asserts have teeth for their
regression class; only the lane's *evidence* for them is weak.
*Minimal fix:* use the FLAG form at all four sites (it is strictly stronger and already written at `:1643/1650/1655`),
or, if the value form is kept, paste the NC-PREMISE-REAL control instead of the threshold-mutation control.

**F9 [BLOCKING] SOLID — the coordinator's tripwire gate is vacuous: `test_sigterm_status_satisfies_check_tee_status`
passes with its wait timed out, TERMing an idle tee and feeding the checker an all-zeros status.**
`tests/test_s0_01_frame_tee.py:2279-2320` (the wait at `:2309-2319`, the TERM at `:2320`).
*Observed vs expected:* this is the fifth instance of the F-B5e-11 class in B5f's own scope file and the only one with
**no** post-loop premise assertion at all (`s` is not even pre-bound). Mutant **NC-TRIPWIRE-LOOPONLY** (break
threshold `>= 1` → `>= 10**9`, nothing else touched): **`1 passed, 95 deselected in 10.30s`** — 10.3 s is the full
wait timeout, so the test proved nothing about a recorded frame and `cc.check_tee_status` accepted the resulting
status. The lane's own red-state row for this test (`rc -15 != 70` on the parent tee) is this vacuity firing under
load. Both the lane brief and the coordinator's gate list this test as "the tripwire … still green" — a gate that can
be green having exercised nothing.
*Failing input:* any regression that slows the first status write past 10 s (or any loaded CI box) — the test
TERMs an idle tee and still asserts only `returncode == 70` plus a checker call the all-zeros status satisfies.
*Minimal fix:* the FLAG form, identical to `:1643/1650/1655`:
```python
loaded = False
...
        if s.get("updated_seq", 0) >= 1:
            loaded = True
            break
...
assert loaded, "no recorded frame: the wait for updated_seq >= 1 timed out"
```
*Exact red test to add:* that assertion, **RUN both ways** — PIN: `1 passed, 95 deselected in 0.36s`; with the
break threshold made unreachable: **KILLED**, `AssertionError: no recorded frame: the wait for updated_seq >= 1 timed
out` (test:2322), `1 failed` in 10.56 s.

**F10 [LOW] SOLID — one AF-AP-40 screen hit on this lane's own added lines is undisclosed.**
`tests/test_s0_01_frame_tee.py:2120` (`if sp.exists():`, the new per-trial lag assertion's presence gate).
*Observed vs expected:* the lane brief required "report each hit as REAL or FALSE POSITIVE with the line". Running
`AP_SCREEN` (imported from `.claude/hooks/edit-snapshot.py`) over the added lines of `git diff -U0 9b2803c 4b43284`
gives **7 hits**: AP-1 at `:469`, `:1032`, `:2527` and AF-AP-40 at `:527`, `:1091`, `:2594` **and `:2120`**. The report
lists six and omits `:2120`.
*Adjudication (mine):* `:2120` is a FALSE POSITIVE in effect — an absent status file is caught loudly by
`test_initial_status_before_first_frame` and `test_sigkill_leaves_nonfinal_status` — but it had to be listed and ruled.
*Minimal fix:* add the row with that ruling.

**F11 [LOW] SOLID — the `proc = None` pin uses `any(...)`, so a rebinding before the install passes it; the real
failure is rc 1.**
`tests/test_s0_01_frame_tee.py:2751-2757`; `proofs/S0-01/tools/frame_tee.py:125`.
*Observed vs expected:* mutant **MIRROR-PREINIT** keeps `proc = None` and adds `proc = 0` on the next line. Pin
passes; full suite **`96 passed in 169.89s`**. The behaviour it hides, reproduced with a 0.6 s window injected before
the Popen (`vb11window.py`, 3 reps each): PIN → `rc 70`, status, `["terminated: SIGTERM"]`; MIRROR-PREINIT → `rc 1`,
`AttributeError: 'int' object has no attribute 'terminate'`; NO-PREINIT → `rc 1`,
`UnboundLocalError: cannot access local variable 'proc'`.
*Minimal fix:* quantify over **all** `proc` assignments before the install, not one:
```python
pre = [s for s in main_fn.body[:signal_idx]
       if isinstance(s, ast.Assign) and getattr(s.targets[0], "id", "") == "proc"]
assert pre and all(isinstance(s.value, ast.Constant) and s.value.value is None for s in pre), \
    "proc is rebound to a non-None value before the handler install"
```
**RUN:** PIN **PASS** · MIRROR-PREINIT **RED** · NO-PREINIT **RED**.

**F12 [LOW] SOLID — the AF-AP-59 class is not pinned; only the current instance is correct.**
`tests/test_s0_01_frame_tee.py:524-550`, `:1088-1114`, `:2591-2617`; `.claude/hooks/edit-snapshot.py` AP_SCREEN.
*Observed vs expected:* mutant **CENSUS-WORLD** reverts the three `finally` blocks to a world-scoped
`pgrep -f "import time; time.sleep"` sweep plus `assert stdout == ""`. Named killers: **`3 passed, 93 deselected in
63.53s`** — nothing in the suite notices, because in a serial sandbox the world *is* empty. It would only go red on
the PC under `-n 8`, which is exactly how AF-AP-59 was found. Separately, AP_SCREEN carries rows for AF-AP-40/45/58
but **no AF-AP-59 signature**, so the edit-snapshot hook would not flag the reversion either (CLAUDE.md: "every new
registry row with a mechanical signature extends the hook's AP_SCREEN in the same increment"; AF-AP-59 was added
2026-09-07 by the A5h/PC incident, so this is a coordinator/A5h item, not B5f's).
*Minimal fix (cheap, in B5f's file):* an AST/text pin in `TestStructuralPins` —
`assert "pgrep" not in <the three finally blocks' source>` is too blunt; better:
```python
def test_grandchild_cleanup_is_own_pid_scoped(self):
    src = Path(__file__).read_text()
    assert 'subprocess.run(["pgrep", "-f"' not in src and '"pkill"' not in src, \
        "a world-scoped process sweep is back in the test file (AF-AP-59)"
```
**RUN:** PIN **PASS** · CENSUS-WORLD **RED**. And add an AF-AP-59 regex to AP_SCREEN (coordinator item).

**F13 [LOW] UNSURE — the grandchild kill has no identity check: `os.kill(<pid from a file>, SIGKILL)`.**
`tests/test_s0_01_frame_tee.py:529-530`, `:1093-1094`, `:2596-2597`.
*Observed vs expected:* the pid is read from a file written seconds earlier and SIGKILLed with no check that it is
still the process the test spawned. If the grandchild exited and the pid was recycled, the test kills an unrelated
process — the mirror image of AF-AP-59 (own-scoped but not identity-checked). On this 4-core sandbox with
`sleep(30)`/`sleep(120)` grandchildren the window is negligible; under `-n 8` on the PC with heavy pid churn it is
not. **NOT REPRODUCED** — I did not force pid reuse (it would risk the shared box and another lane's processes).
*Minimal fix:* before the kill, require identity —
`assert "time.sleep" in open("/proc/%d/cmdline" % gc_pid).read().replace("\0", " ")` (and treat a missing
`/proc/<pid>` as already-gone).

**F14 [INFO] SOLID — the report's header names the dispatch commit as the PIN.**
`tasks/briefs/s0-01-b5f-support/B5f-report.md:3` — "PIN `a60b933559ce…`. HEAD at run: same." `a60b933` is the brief
commit; the work landed in `4b43284`, two commits later. The FILE IDENTITY sha256s are the final files and match
`4b43284`, so the grade is unaffected — but `git show a60b933:proofs/S0-01/tools/frame_tee.py` gives the pre-B5f tee.
*Minimal fix:* state both ("dispatched at `a60b933`; work landed in `4b43284`").

**F15 [INFO] SOLID — `assert gone` sits inside `finally:` and before the pipe closes.**
`tests/test_s0_01_frame_tee.py:550`, `:1114`, `:2617`. If the assertion fires, `tee_proc.stdout.close()` /
`stderr.close()` (the statements *after* the `finally`) never run for that test, and any in-flight failure from the
try body is reported as the chained `__context__` rather than as the primary failure. Cosmetic; noted because the
same three blocks are F6's subject and will be touched anyway. *Fix:* close the pipes inside the `finally` before the
assertion, or collect `gone` and assert after the `finally`.

**F16 [INFO] SOLID — the new lag assertion has two silent-skip paths inside the 12-trial loop.**
`tests/test_s0_01_frame_tee.py:2120` (`if sp.exists():`) and `:2125-2126`
(`except (json.JSONDecodeError, ValueError): pass  # torn status after SIGKILL`). A trial whose status file is absent
or torn contributes no sample. Harmless today (S1F dies 5/5 anyway, and absence is caught by other tests), but it
means "12 samples" is an upper bound, not a count. *Fix if ever wanted:* count the samples actually taken and
`assert sampled >= 6`.

**F17 [INFO] — premise shift during my run; grade unaffected.**
HEAD moved `4b43284` → `c4805df` (lane D5i, checkpoint 8r) → `f0ae7eb` (transcripts) → `fc35fbb` (CLAUDE.md) while I
was measuring, and the working tree went from three uncommitted D5i files to fully clean.
`git diff --stat 4b43284 fc35fbb -- proofs/S0-01/tools/frame_tee.py tests/test_s0_01_frame_tee.py` is **EMPTY**, and
the worktree copies still hash `ac82dba…` / `05019a91…` with `git status --porcelain` empty on both. I graded the
PIN's bytes throughout and never wrote to the shared tree. One consequence: the lane's
`lint_delta --base origin/…` line is no longer reproducible against origin (origin now *contains* the PIN); I
re-based on `9b2803c` instead.

**F18 [INFO] UNSURE — carry-forward: `os.makedirs` still sits inside the uncovered pre-install window.**
`proofs/S0-01/tools/frame_tee.py:120`, docstring `:23-25`. Unchanged from round 10 (not in B5f's brief). The
docstring still attributes the whole uncovered window to "Python interpreter startup"; a hung/NFS framedir would
block inside it. **Not reproduced** (no hung-FS fixture).

**F19 [INFO] SOLID — DRAIN-ORDER equivalence accepted, and reproduced.**
Swapping the two drain loops: `2 passed` on the named tests, **`96 passed in 169.96s`** on the full suite. Both loops
are pure 10 Hz waits, both pumps drain in their own threads, and `tl.close()` follows both, so termination and all
observable state are identical. The lane's EQUIVALENT ruling stands.

---

## WHAT I REPRODUCED vs REVIEWED STATICALLY vs DELIBERATELY SKIPPED

**Reproduced (my own runs this session, on `git archive 4b43284` copies; load stated at every timing claim):**
the PIN full suite ×4 (`96 passed` at 169.38 / 169.57 / 170.44 / 169.16 s) plus 6 more full suites inside mutant
escalations; the full no-`-x` red state on the true parent `736bb94` (`8 failed, 88 passed in 171.80s`); five
individual reps each of the three disputed red rows; **40 distinct mutants** over ~70 runner pytest invocations
(S1/S1F/N4/D3 3× each, S1F 5× on two different behavioural killers, MIRROR-SNAPSHOT 5×); the four premise-assert
negative controls in two different shapes plus a regression-class control; the whole suite under 4 CPU burners
(`96 passed in 204.20s`, load 7.45); 10 concurrent-process runs of the three grandchild tests; the process census
across two suites plus a delayed census; the AST Popen census; the AP_SCREEN mapping over the B5f delta; the cost
probe 3×15 reps on **both** the PIN and the parent tee in one quiet window (load 0.59); the SIGTERM window and the
TERM-at-t=0 mode 6× each on 3.11 **and** 3.12; the injected-window `proc` probe 3× on three tee variants; the
torn-snapshot probe 3× on two tees (8.6 M samples); the pinned `acp.rs` re-fetched and sha256-matched, with the two
cited ranges, the `Drop` path, the `from_secs(5)` census and the production `.shutdown()` call sites read from source.

**Reviewed statically only:** F15 (the `finally` assert ordering — Python semantics, not run); F16 (the lag
assertion's skip paths — argued from the code); the claim that `COMMENT-TERM` survives the *full* suite (it survives
the named killer; the full-suite escalation was skipped because comments are provably absent from the AST and no test
greps the source for them — a 170 s run for a provable answer).

**Deliberately skipped, with reason:**
* **The PC leg** (`scripts/pc_suite.sh`, 8 xdist workers). No BRIDGE READY banner this session and my brief forbids
  outward actions beyond the one read-only source fetch. Two of my findings are venue-sensitive and would read
  differently there: **F12** (CENSUS-WORLD is invisible in a serial venue *by construction* — it is a PC-only red) and
  **F13** (pid reuse). This is a **sandbox-only, single-worker grade**.
* **`pytest -n 4`** — xdist is not installed on this interpreter (`ModuleNotFoundError`). Substituted two concurrent
  pytest processes × 5 rounds, as my brief directs.
* **The pytest suite on 3.12** — pytest is not installed for it; no network install attempted. The AST pins and the
  tee's real SIGTERM behaviour were run there standalone instead.
* **Forcing pid reuse** for F13 — it would require churning thousands of pids on a box shared with another live lane.
* **A hung-filesystem fixture** for F18 — same reason as round 10.
* **Re-running the ~40 round-9 mut8 mutants** that neither the acceptance bar nor the B5f diff touches.

## ONE MORE THING THE MEASUREMENTS SAY

The pins the lane added are *good* pins — deterministic, 0.1 s, and every realistic regression in the acceptance bar
dies on one. Where they are weak is uniform and worth stating once: **all four are presence/order pins, and each one's
mirror is "keep the shape, break the dataflow".** MIRROR-SNAPSHOT (keep the lock, re-read outside), MIRROR-PREINIT
(keep `proc = None`, rebind), PIN-LOCK-NAME (keep the name, and by extension `PIN-NULLLOCK` keeps the name while
making it not a lock — that one the race test *does* catch), DOCSTRING-HYBRID (keep the tokens, invert the claim).
Three of the four fixes in F4/F5/F11 are one assertion each and turn presence into dataflow.

## MY OWN PROPOSED KILLERS, RUN (AF-AP-36: a verifier's proposed killer is a hypothesis like any other)

Every test this verdict proposes was executed against the PIN **and** against the mutant it names, before it entered
the report. Runner `vb11killers.py` (AST killers, evaluated over the mutated source) and `vb11killers2.py` (runtime
killers, applied to the venue test file and run under pytest).

```
F4  docstring_pins_the_meaning     PIN:PASS  DOCSTRING-HYBRID:RED  DOCSTRING-TERM:RED
                                   (3rd assertion RED on the PIN today at 5 sites -- that IS F3)
F5  no_state_read_outside_lock     PIN:PASS  MIRROR-SNAPSHOT:RED  N4:RED  LOCK-READS-OUT:RED  D3:PASS(*)
F11 proc_preinit_all               PIN:PASS  MIRROR-PREINIT:RED  NO-PREINIT:RED
F12 cleanup_is_own_pid_scoped      PIN:PASS  CENSUS-WORLD:RED
F6  assert grandchild.pid exists   PIN:3 passed 63.68s   PIDFILE-ABSENT:KILLED ("agent never wrote grandchild.pid")
F9  tripwire flag form             PIN:1 passed 0.36s    threshold-unreachable:KILLED ("no recorded frame: the wait
                                                          for updated_seq >= 1 timed out", test:2322, 10.56s)
(*) D3 is already covered by the existing `status_lock`/os.replace assertion -- F5's killer is an addition, not a
    replacement. Stated because a killer that silently drops an existing arm is the AF-AP-36 failure mode.
```
**One of my own proposed killers was wrong and I caught it by running it:** the first form of F4's third assertion was
the literal `"SIGKILLs the group after 5 s" not in src`, which **PASSED on the PIN** — the phrase is line-wrapped at
four of its five sites, so the literal string never appears. Replaced with the wrap-tolerant regex, which finds all
five. Recorded here as a live instance of the same class as AF-AP-57.

---

## VERDICT

# NOT-READY

The engineering in this increment is good and most of it is closed better than the lane claims: the four AST pins are
genuinely deterministic (S1 3/3, S1F 3/3, N4 3/3, D3 3/3, LOCK-READS-OUT, INSTALL-LATE-B, NO-PREINIT — all in 0.10 s
where round 10 measured 6 %/78 %/56 %); the 12-trial lag assertion kills S1F 5/5 where the old single-sample test
kills 0/5; TRY-SHRINK2 is now measured and **KILLED**, closing the lane's only NOT_DONE mutant; the own-pid census
holds 10/10 under concurrent processes with zero cross-test interference and zero live leaks over two suites; the
suite is green under 4 CPU burners with no premise-assert flake; there is no cost regression (PIN 0.0545–0.0553 s vs
parent 0.0543–0.0577 s measured back-to-back at load 0.59); and the tee behaves identically on CI's 3.12.

It is NOT-READY on six items, four of which are the same failure this round was called to fix — a guard that cannot
fail, and a report whose evidence does not reproduce.

**Blocking set**

1. **F6 — the headline fix is fail-open.** With the pid file absent, all three `finally` blocks skip the kill and the
   own-pid assert, the three tests pass, and the ppid-1 orphan that F-B5e-12 was opened for comes straight back
   (measured: `3 passed` + `23435 ppid 1 S /usr/local/bin/python3 -c import time; time.sleep(120)`). The report rules
   the AF-AP-40 screen hit a FALSE POSITIVE; the measurement says otherwise. Fix + red test both run:
   `assert gc_pid_path.exists()` at `test:527/1091/2594` → PIN `3 passed`, PIDFILE-ABSENT KILLED.
2. **F9 — the coordinator's own tripwire gate is vacuous.** `test_sigterm_status_satisfies_check_tee_status`
   (`test:2279-2320`) passes with its wait timed out (`1 passed in 10.30s`), TERMing an idle tee and handing the
   checker an all-zeros status. It is a fifth site of the F-B5e-11 class inside B5f's own scope file, unfixed and
   undisclosed, and it is the mechanism behind the lane's own unreproducible `rc -15` red row. Fix + red test run.
3. **F3 — five committed artifacts invert the pinned source.** `frame_tee.py:422`, `:428` and
   `tests/test_s0_01_frame_tee.py:853`, `:1019`, `:1454` say buzz-acp "SIGKILLs the group **after 5 s**". The pinned
   `acp.rs` (sha256 re-verified) SIGKILLs immediately and then waits **up to** 5 s; the only production `from_secs(5)`
   in the file is that post-kill wait. This is F-B5e-1's own class, re-introduced in the increment that was supposed
   to close it.
4. **F4 — the doc-anchor test cannot see F3, or anything else that matters.** DOCSTRING-HYBRID (SIGKILL and acp.rs
   present, `TERMs/KILLs` absent, the false SIGTERM-bounds-the-leg claim restored) survives the full suite
   (`96 passed in 169.16s`), and the pin reads only the module docstring, so COMMENT-TERM survives by construction.
   Three string tokens are not a meaning pin. Fix + red test run.
5. **F1 — the red state does not reproduce.** `8 failed, 88 passed`, not `7 failed, 89 passed`, and the extra failure
   is a row the report classifies as a GREEN CONTROL —
   `test_write_status_snapshot_and_rewrite_are_locked` is a *deterministic* red on the parent (0.15 s, test:2498).
   Round 10's F-B5e-4 was blocking for exactly this; the class repeats.
6. **F7 — fourteen of sixteen typed `file:line` refs in the DONE table are wrong on the final tree**, by up to 109
   lines, against a brief that demanded "every file:line on the FINAL tree". The only correct ones are those pasted
   from a tool.

**Should ship with the blockers (cheap, each verified):** F5 (the N4/D3 pin is a mirror — MIRROR-SNAPSHOT survives
pin, race test 0/5, and full suite; one added dataflow assertion, run), F11 (`proc = None` pin's `any(...)` → `all`,
run), F12 (nothing gates a reversion to a world-scoped census; one text pin, run), F8 (use the FLAG form at the three
value sites, or paste the regression-class control), F10 (the undisclosed seventh AP screen hit at `test:2120`),
F2 (two wrong rows in the red-state table), F14 (the header PIN sha is the dispatch commit).
**Recorded, not charged:** F13 (UNSURE, pid-reuse hazard, not reproduced), F15, F16, F17, F18 (carry-forward, UNSURE),
F19.

**This verdict's dependence on things I did not reproduce:** none of the six blockers rests on an unreproduced claim —
each has a pasted run above, and each proposed fix was executed against the PIN and its mutant. Two *non-blocking*
findings are venue-limited and I say so in the finding: **F12** is invisible in a serial sandbox by construction (it
would only go red under `pytest -n 8` on the PC, which I did not run — no bridge banner this session), and **F13** is
not reproduced at all. This is a **sandbox-only, single-worker grade**: no PC leg, no xdist, no pytest on 3.12.

**Shared-tree hygiene:** every mutant ran on `git archive` copies under `…/scratchpad/vb11*`; both scope files
re-hashed to `ac82dba82e2f…` / `05019a915ecf…` after every batch (the runner prints it); the shared tree's two scope
files were `git status --porcelain`-clean at every check and I never wrote to it. Every process I started was
accounted for and killed; another lane's processes (a `ck10` verifier's bash, visible in one census) were left alone.
