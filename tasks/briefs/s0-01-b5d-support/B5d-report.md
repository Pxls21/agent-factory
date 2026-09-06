# B5d — tee drain-to-EOF, status inside timeline lock, killing tests

## Files
- `proofs/S0-01/tools/frame_tee.py` (473 -> 476 lines)
- `tests/test_s0_01_frame_tee.py` (1725 -> 2056 lines)

## Done

| finding | fix (code) | test | red before / green after |
|---|---|---|---|
| R1/F1/F2/F14 (drain contract) | c2a stall-timeout loop replaced with `while ti.is_alive(): sleep(0.1); _write_status()` (drain to EOF). Docstring rewritten. | `test_late_frame_after_agent_death_recorded` [1/6/8s], `test_late_frame_after_reap_with_client_holding_stdin` (stdin close), `test_tee_exits_cleanly_with_agent_code` (stdin close) | p9 gap 6s: SILENT LOSS -> LOUD(ok) |
| R2/F3 (status inside lock) | `_write_status()` inside the timeline `with lock:` in both pumps; `lock = threading.RLock()` | `test_rewrite_is_atomic` (bidirectional 5000, spinning reader >= 10k reads, seq + fwd invariants) | killsnap diff 2 -> 1 max |
| R2/F5 (snapshot under lock) | `_write_status()` inside `with lock:` (same change) | `test_rewrite_is_atomic` | N4 mutant: from survived to killed (seq violations) |
| R2/F6 (status_lock) | `status_lock` write path unchanged; bidirectional test now creates the two-writer condition | `test_rewrite_is_atomic` | D3 mutant: from survived to killed (torn JSON) |
| R2/F7 (write order) | unchanged (timeline first); test strengthened | `test_directional_trails_timeline_after_sigkill` (12 trials, both dirs, len==12) | N3 mutant: 3/12 directional-ahead |
| R2/F9 (forwarded under lock) | `forwarded_<dir> += 1` inside `with lock:` after forward; `write_errors.append(...)` for forward errors under lock | `test_rewrite_is_atomic` (recorded - forwarded in {0,1}) | forward-lag: 153k violations -> 0 |
| R2/F8 (C1 c2a running status) | `_write_status()` inside timeline lock in pump_fd | `test_running_status_tracks_c2a_before_agent_exits` | C1 mutant: recorded_c2a frozen at 0 |
| R3/F4 (SIGTERM checker) | tee unchanged (non-final, exit 70) | `test_sigterm_status_satisfies_check_tee_status` (xfail strict, reason="checker A21d non-final arms pending (lane A5g)") | xfail as expected |
| R4/F10 (handler structure) | handler unchanged (`raise _Terminated()`) | `test_sigterm_handler_is_raise_terminated` (ast-level) | N6 mutant: handler body != 1 raise |
| R4/F11/N8 (close errors) | directional close errors appended under lock | `test_a2c_directional_close_error_recorded` (exact list equality) | N8 mutant: missing close entry |
| R4/F13 (exact assertions) | -- | `test_bounded_write_errors_dedup` (exact ==), `test_directional_enospc` (exact list), `test_c2a_directional_enospc_eof_agent_exits_70` (exact list) | startswith/>=1 gone (grep: 0 matches on write_errors) |
| R4/F15 (docstring) | "rewritten after every recorded frame", non-final SIGTERM named, drain-to-EOF described | -- | -- |
| R4/F16 (contended) | -- | see gate lines: two real contended runs | -- |
| R4/F18 (rename) | disclosed: `test_agent_burst_within_pipe_buffer_drained` -> `test_agent_burst_drained` (done in B5c) | -- | -- |
| R1 (stdin_reader_done) | `test_stdin_reader_done_false_when_client_never_closes` now SIGTERMs the tee (drain-to-EOF never exits on its own) | asserts rc 70, stdin_reader_done False, write_errors == ["terminated: SIGTERM"] | -- |

## R2 invariant list (for the checker lane)

On EVERY running (non-final) `tee-status.json` snapshot under bidirectional load:
1. `updated_seq == recorded_c2a + recorded_a2c` (seq consistency)
2. `timeline_last_seq - updated_seq in {0, 1}` (status trails timeline by at most one frame)
3. `recorded_c2a - forwarded_c2a in {0, 1}` and `recorded_a2c - forwarded_a2c in {0, 1}` (one in-flight frame per direction)

On the final status:
4. `forwarded_c2a == recorded_c2a` and `forwarded_a2c == recorded_a2c` (all forwarding complete)

On 12 SIGKILL trials with bidirectional 20k-frame load:
5. Directional file count <= timeline count, both directions (directional never ahead)

## Mutant expectations

| # | mutation | expected killer |
|---|---|---|
| A2 | c2a drain exits early (stall timeout 0) | test_late_frame_after_agent_death_recorded |
| A6 | drained ignores c2a | test_late_client_frame_recorded_or_exit_70 (drained is False) |
| C1 | no c2a running status | test_running_status_tracks_c2a_before_agent_exits |
| D3 | drop status_lock | test_rewrite_is_atomic (torn JSON or seq violation) |
| N3 | write order swapped | test_directional_trails_timeline_after_sigkill (dir > tl) |
| N4 | snapshot outside lock | test_rewrite_is_atomic (seq != rec_c2a + rec_a2c) |
| N6 | handler takes lock | test_sigterm_handler_is_raise_terminated (ast body check) |
| N8 | close error swallowed | test_a2c_directional_close_error_recorded (exact list) |
| C4 | exit fields set when not final | EQUIVALENT (all 8 non-final sites pass None defaults) |
| N10 | test drops pins import | EQUIVALENT by construction |

NOTE on A2 re-aiming: mut8.py A2 patches `elif time.monotonic() - stall_start_c2a >= stall_timeout:` which no longer exists in the code. The concept ("drain exits before client EOF") is killed by the gap test. The verifier will need to re-aim A2 against the new `while ti.is_alive():` loop.

## Probe table

| probe | result |
|---|---|
| p9 gap sweep 1/4/6/8 s | all recorded, rc 70, LOUD(ok) 8/8 (was: 6/8s SILENT LOSS) |
| killsnap 20 | A21d-FAIL=8, A21d-PASS=12; all diffs = 0 or 1; `updated_seq == rec_c2a + rec_a2c` on all 20 |
| hang.py A-E | A/B/C rc 70 0.1s; D rc 0; E rc 70 |
| sigterm_deadlock 24 | HUNG=0, all rc 70, secs_after_term 0.0 |
| forward-lag 20k | 460030 reads, 0 violations of recorded - forwarded in {0,1} |
| ordering (test_directional_trails_timeline_after_sigkill) | 12 trials, both dirs, len(results)==12, 0 dir-ahead |

## Gate lines

```
pyflakes proofs/S0-01/tools/frame_tee.py tests/test_s0_01_frame_tee.py -> rc 0
idle 1:      83 passed, 1 xfailed in 88.46s (0:01:28)    pytest-exit: 0
idle 2:      83 passed, 1 xfailed in 89.56s (0:01:29)    pytest-exit: 0
contended 1: 83 passed, 1 xfailed in 535.56s (0:08:55)   pytest-exit: 0  (nice -n 19, 4 burners, load 3.59)
contended 2: 83 passed, 1 xfailed in 588.79s (0:09:48)   pytest-exit: 0  (nice -n 19, 4 burners, load 6.82)
```

## Not done

| item | reason |
|---|---|
| F17 (try/finally on every Popen test) | Added to the critical tests (SIGKILL, SIGTERM, late-frame, burst, C1). The mechanical sweep of all 23 Popen callsites was not completed -- the tests that already had explicit cleanup (communicate/wait/close patterns) were not wrapped. The verifier should flag any remaining leakers. |
| A2 mutant re-run from mut8.py | A2's patch text no longer exists in the code (the stall timeout loop was removed). The concept is killed by test_late_frame_after_agent_death_recorded. The verifier will re-aim. |
| Killsnap 20/20 A21d-PASS | 12/20 PASS, 8/20 A21d-FAIL. All failures show timeline-status diff = 1, `updated_seq == rec_c2a + rec_a2c`. The checker's A21d rule (`recorded == timeline count`) requires a separate checker-lane relaxation to `timeline_last_seq - updated_seq in {0, 1}`. |

## Discrepancies with the brief
- Brief R1: "rc 0 with drained true" for gap tests. Measured: rc 70, drained False (the forward of the late frame fails with BrokenPipeError because the agent already exited). The brief's "rc 0" may have described the pre-fix buggy behavior (SILENT LOSS at gap > 5s). The tests assert the correct post-fix behavior (frame recorded, rc 70).
- Brief A2 mutant: "exit when the agent exits" -- mut8.py A2 patches text that no longer exists. The test kills the concept.

## Adjacent defects (report only)
1. The a2c drain still uses a 5s stall timeout. A grandchild holding stdout open can stall the tee for 5s. Not changed per brief boundary (R1 only addresses c2a).
2. `_write_status()` is called once inside the timeline lock AND the forwarded update is in a separate lock. This means two lock acquisitions per frame per pump (was one). The cost test may show higher contention overhead. The 11-frame real-leg shape should still be within 2x per the brief's bar.
