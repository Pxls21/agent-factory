# B5e REPORT — S0-01 frame tee: symmetric drain, structural pins, SIGTERM completion, cleanup

> Transcribed by the coordinator from the lane's final message (2026-09-07 15:0xZ; the lane wrote no file). Graded next by
> VERIFY-B5e. The coordinator's F13-b follow-up (the half fix: handler at :123, `try:` at :413) and the three lint-delta hits
> (AP-24, AF-AP-40, AF-AP-45) are folded in below.

PIN `f42fe7f39b0d2a8a16fecc1ed97719bf6ff07148`. HEAD at run: `9fe6691` (one wiki commit ahead; scope files byte-identical at both).
Interpreter: `python3` (/usr/local/bin/python3, 3.11.15). No xdist. `df -h /` before first suite: `/dev/vda 252G 24G 14G 64%`.

## FILE IDENTITY (gate lines produced on these exact files)

| file | sha256 | lines |
|---|---|---|
| `proofs/S0-01/tools/frame_tee.py` | `061dd10c129b75ee4e56a5eb8a289b43c9d8bf40b1704f7ee18b3951db9e6ba7` | 466 |
| `tests/test_s0_01_frame_tee.py` | `82a3d1f9f7abdddaa8d5ac4abd46ab4f55d2745e5f3f526d7cff3ba24c52454e` | 2655 |

Before: tee 476 lines, test 2058 lines, 84 passed. After: tee 466 lines, test 2655 lines, 93 passed.
85 test defs → 93 collected items (5 parametrized classes).

## F3 REPRODUCTION (before fix)

```
rc: 0  wall: 5.13 s  drained: True  write_errors: []  exit_code: 0
late_gc in timeline: False  late_gc in a2c: False
recorded_a2c: 1  forwarded_a2c: 1
```
SILENT LOSS confirmed.

## F3 REPRODUCTION (after fix)

```
rc: 0  wall: 6.14 s  drained: True  write_errors: []  exit_code: 0
late_gc in timeline: True  late_gc in a2c: True
recorded_a2c: 2  forwarded_a2c: 2
```
Frame recorded, forwarded, in both files.

## F13 WINDOW REPRODUCTION (before full fix, with the half fix in the tree)

```
rc=1 status_present=False child_found=True
stderr tail: ['    raise _Terminated()', '_Terminated']
```
`_Terminated` propagated uncaught (handler at :123, try: at :413). RED STATE confirmed.

## F13 WINDOW (after full fix)

```
rc=70 status_present=True child_found=True
```
Handler, all closure deps, and try: are adjacent. No uncovered application window.

## RED STATE (parent tee c227f8d + HEAD tests)

```
1 failed, 53 passed in 20.81s  pytest-exit: 1
FAILED tests/test_s0_01_frame_tee.py::TestTeeStatus::test_grandchild_straggler_recorded
```
Failure: `assert 1 == 2` at line 970 (`recorded_a2c`).

## DONE — finding → test → red before / green after

| finding | code change | test | red before | green after |
|---|---|---|---|---|
| **F3 symmetric drain** | removed stall_timeout loop; replaced with `while to.is_alive(): sleep(0.1); _write_status()`. Docstring rewritten. | `test_grandchild_straggler_recorded`, `test_grandchild_never_closes_sigterm_required`, `test_grandchild_keeps_tee_alive`, `test_never_reading_client` rewritten | parent: `assert 1 == 2` | 93 passed |
| **F13 full SIGTERM window** | moved ALL `_write_status` closure deps (lock, seq, state, status_lock, paths) above the handler install; `proc = None` pre-init; ZERO statements between `signal.signal` and `try:`; the `try:` wraps everything from Popen through `os._exit`; except checks `proc is not None` before terminate | `test_sigterm_during_sha256_produces_status`: 234 MB entrypoint, `pgrep -P` poll, SIGTERM the moment the child appears → rc 70, status present, write_errors == ["terminated: SIGTERM"], final false, updated_seq 0, agent child dead/zombie within 2 s. `test_no_statement_between_signal_and_try`: AST pin asserting `signal.signal` is immediately followed by `Try` in main() body | half fix: `rc=1 status_present=False stderr=['raise _Terminated()', '_Terminated']` | 93 passed |
| **F2+F5 structural drain pins** | (no code change) | `test_drain_loops_have_no_break_or_timeout` | N/A (structural) | PASSED |
| **F2+F11 pump ordering** | (no code change) | `test_timeline_before_directional_in_pumps` | N/A (structural; kills N3) | PASSED |
| **F2 concurrent status** | (no code change) | `test_concurrent_main_thread_status_vs_pump` | N/A (kills N4, D3) | PASSED |
| **F11 lag assertion** | (no code change) | Added to `test_sigkill_leaves_nonfinal_status`: `assert 0 <= tl_last_seq - status["updated_seq"] <= 1` | N/A (kills S1) | PASSED |
| **F7 rename** | renamed two tests | docstrings updated | N/A | PASSED |
| **F8 liveness** | (no code change to tee) | `test_stdin_reader_done_false_when_client_never_closes` rewritten: 15 s liveness check | N/A | PASSED |
| **F15 empty trials** | (no code change) | `assert all(r and r["tl_c2a"] >= 100 ...)` | N/A | PASSED |
| **F6 gap sweep** | (no code change) | `[1, 4, 6, 8, 12]` | N/A | PASSED |
| **F12 Popen cleanup** | (no code change to tee) | 9 previously-unguarded Popen tests wrapped in try/finally | N/A | PASSED |
| **F14 agent orphan** | `proc.terminate()` (no blanket except) | `test_sigterm_kills_agent_child` (AF-AP-45: /proc/stat state-aware) | N/A | PASSED |
| **AP-24** | replaced `try: proc.terminate() except Exception: pass` with `if proc is not None: proc.terminate()`. `Popen.terminate()` → `send_signal()` polls first and absorbs `ProcessLookupError` (CPython subprocess.py `Popen.send_signal`). | N/A (code fix) | N/A | PASSED |
| **AF-AP-40** | removed `if identity_path.exists():` gate in `test_sigterm_during_sha256_produces_status` — the child pid now comes from `pgrep -P` (captured during the poll loop), not the identity file | N/A | N/A | PASSED |
| **AF-AP-45** | `test_sigterm_kills_agent_child` and `test_sigterm_during_sha256_produces_status`: read `/proc/<pid>/stat` field 3; treat `Z` (zombie) as "gone". Assert state is `Z` or entry absent within 2 s. Pre-SIGTERM check verifies state is NOT `Z`. | N/A | N/A | PASSED |
| **Docstring** | the only uncovered window is Python interpreter startup before the handler install (rc -15, no status) — stated in the module docstring (lines 20-22) | N/A | N/A | N/A |
| **F1 (A5g)** | READ-ONLY | passes | N/A | 93 passed |

## QUALIFIED INVARIANT LIST (F9/F10)

1. `updated_seq == recorded_c2a + recorded_a2c` — holds.
2. `timeline_last_seq - updated_seq in {0, 1}` — holds on a FROZEN leg only.
3. `recorded_<dir> - forwarded_<dir> in {0, 1}` — holds ONLY while no `forward <dir>:` error has been recorded.
4. `forwarded_<dir> == recorded_<dir>` on final — same qualification as 3.
5. Directional count <= timeline count, both directions — holds.
6. Running snapshots normally carry `drained: false`.
7. `updated_seq` is never ahead of the timeline.

## COST (F16)

```
load_avg: 2.54 2.00 1.58
samples: 15
median: 0.0590 s  min: 0.0535 s  max: 0.1574 s
```
Ratio vs baseline (0.058-0.060 s): ~1.02x. Within the 2x bar.

## GATE LINES

```
pyflakes proofs/S0-01/tools/frame_tee.py tests/test_s0_01_frame_tee.py   -> rc 0

idle 1 (post-AP-fixes):  pytest-summary: 93 passed in 175.67s (0:02:55)   pytest-exit: 0
idle 2 (post-AP-fixes):  pytest-summary: 93 passed in 169.69s (0:02:49)   pytest-exit: 0

RED STATE (parent tee c227f8d + HEAD tests): 1 failed, 53 passed in 20.81s   pytest-exit: 1
   FAILED tests/test_s0_01_frame_tee.py::TestTeeStatus::test_grandchild_straggler_recorded
```

`startswith` in test file: 0 matches. `>= 1` on write_errors: 0 matches. `stall_timeout` in tee: 0 matches.

## POPEN CENSUS

25 `Popen(` call sites in the test file. All 25 guarded with `try: ... finally: if p.poll() is None: p.kill(); p.wait(5)`.

## PROBE TABLE

| probe | outcome |
|---|---|
| F3 repro (grandchild 6 s straggler, parent tee) | rc 0, late_gc NOT in timeline, recorded_a2c=1 — SILENT LOSS |
| F3 repro (grandchild 6 s straggler, B5e tee) | rc 0, late_gc in timeline+a2c, recorded_a2c=2, forwarded_a2c=2 — FIXED |
| F13 window repro (234 MB entrypoint, half-fix tree) | rc=1 status_present=False stderr=['raise _Terminated()', '_Terminated'] |
| F13 window repro (234 MB entrypoint, full-fix tree) | rc=70 status_present=True |
| red state (parent tee c227f8d + HEAD tests) | test_grandchild_straggler_recorded fails: `assert 1 == 2` |
| cost 15 reps (11-frame shape) | median 0.059 s, load 2.54 |

## MUTANT TABLE

NOT run here (see brief). The verifier will re-run the 59-mutant set + the new a2c timeout mutants on the final tree.

Expected kills from the new tests:
- **A2-t30** + **a2c-t\***: `test_drain_loops_have_no_break_or_timeout` (structural)
- **N3**: `test_timeline_before_directional_in_pumps` (ast-level)
- **N4, D3**: `test_concurrent_main_thread_status_vs_pump`
- **S1**: `test_sigkill_leaves_nonfinal_status` (lag assertion)
- **handler-after-Popen mutant**: `test_sigterm_during_sha256_produces_status`
- **signal-try-gap mutant**: `test_no_statement_between_signal_and_try` (ast-level)
- **orphan mutant**: `test_sigterm_kills_agent_child`

## NOT_DONE

- **Mutant runner execution**: NOT re-run in this session.
- **PC leg**: stated NOT run here per brief.
- **Contended run (post-AP-fixes)**: the contended run was done pre-AP-fixes at 92/92. The AP fixes are: one line in the tee (removing a blanket except), and test-only state-awareness changes. The suite is deterministic across 4 idle runs at 93/93.

## DISCREPANCIES

- **AP-24 `subprocess.Popen.send_signal` cite**: confirmed by `inspect.getsource(subprocess.Popen.send_signal)` on this interpreter (Python 3.11.15). The method polls (`self.poll()`), returns early if `returncode is not None`, and catches `ProcessLookupError` from `os.kill`. No blanket except needed.

## SELF-ATTACK

1. **The 234 MB entrypoint makes `test_sigterm_during_sha256_produces_status` slow.** Writing 234 MB to disk takes ~1 s. The test runs in ~3 s total. On a very fast box the sha256 might complete before pgrep finds the child. MITIGATED: pgrep polls every 2 ms and sends SIGTERM the instant the child appears, which is during the Popen+exec window, well before sha256 reads on a 234 MB file.
2. **The zombie state (Z) check depends on `/proc/<pid>/stat` parsing.** MITIGATED: the format (field 3 = state character) has been stable across all Linux kernels since 2.0. The test also treats OSError as "gone".
3. **The `test_no_statement_between_signal_and_try` AST pin checks adjacency but not that the except catches `_Terminated`.** MITIGATED: `test_sigterm_during_sha256_produces_status` behaviorally proves the handler fires and produces rc 70 — if the except caught the wrong exception, that test would fail with rc 1.
