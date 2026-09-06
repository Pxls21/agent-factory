Verification complete. Report follows.

---

# VERIFY-B5c — round 8, frame tee (drain / status / exit paths) — **VERDICT: NOT-READY**

## Premise + disk

```
git log --oneline -8  (at start, 13:31 UTC)
fcd0cbf transcripts: scrubbed sandbox chat digests (2026-09-06)      <- accepted per brief
0f96585 S0-01 WIP checkpoint 8e: ... (lane D5e)
ea8414f S0-01 WIP checkpoint 8d: the frame tee's drain, status and exit paths ... (lane B5c)
PREMISE OK.
df -h /tmp/claude-0 | tail -1   ->  /dev/vda  252G  22G  16G  58% /   (end of run: 16G, 59%)
```

**PREMISE SHIFTED MID-RUN — reported loud.** At 15:20 UTC the shared tree was at `57a7df6` (checkpoint 8f, lane N5e). All four scope/context files are **byte-identical** at `fcd0cbf` and at `57a7df6` (`git diff --stat fcd0cbf..HEAD` on them is empty; `frame_tee.py` sha256 `b6d54a68684b9320…`, test file `6fa0574fd88ac4d7…`, both matching my copy). The grade transfers unchanged. I changed nothing in the shared tree (`git status --porcelain` on the three lane/context files: empty at the end).

Work copy: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vb8/repo` (from `git archive HEAD`), harnesses in `…/vb8/work/`. One mutant tree at a time, deleted after each run; `--basetemp` per run under my scratch dir. 4 cores, no xdist; the contended pair ran last, serially.

## Mutant table — 54 mutants (the 43 re-aimed + 11 new), **44 KILLED / 10 SURVIVED**

`mut.py`'s anchors are aimed at the round-6 file: **25 of its 42 entries PATCH-FAIL against this tee** (A1 A3 A4 A6 B1 B2 C1–C9 D3 E3 E4 E5 F3 F4 F5 F7 H1 H3). Every mutation below was re-expressed against the round-8 code (runner: `…/vb8/work/mut8.py`, dry-run verified: 54/54 apply, 54/54 parse). Runs used `-x`, so "killed by" is the first failing test.

| # | mutation (re-expressed) | result | killed by |
|---|---|---|---|
|A1|c2a drain loop dead-coded (`while False and …`)|KILLED|test_late_frame_after_reap_with_client_holding_stdin|
|**A2**|**c2a stall timeout 5 s → 0 s**|**SURVIVED**|— (78 passed in 61.7 s)|
|A3|drop the `drain c2a: stopped` entry|KILLED|test_late_frame_after_reap_with_client_holding_stdin|
|A4|swap the counts in the `drain c2a` message|KILLED|same|
|A5|c2a pump stops recording after a forward error|KILLED|test_late_client_frame_recorded_or_exit_70|
|**A6**|**`drained` ignores c2a**|**SURVIVED**|— (78 passed in 75.4 s)|
|A3+A6|composed (round 6's dangerous pair)|KILLED|test_late_frame_after_reap_with_client_holding_stdin|
|B1|drop the `drain a2c: stopped` entry|KILLED|test_never_reading_client|
|B2|swap the counts in the `drain a2c` message|KILLED|test_never_reading_client|
|B3|`drain a2c` → `drain c2a`|KILLED|test_never_reading_client|
|**C1**|**no per-frame status from pump_fd**|**SURVIVED**|— (78 passed in 72.2 s) — *round 6: KILLED*|
|C2|no per-frame status from pump_pipe|KILLED|test_sigkill_leaves_nonfinal_status|
|C3|`final` always False|KILLED|test_normal_run_writes_status|
|C4|exit fields set when not final|SURVIVED (**equivalent**, re-derived: all 8 non-final call sites pass the `None` defaults — :293 :363 :393 :415 :420 :434 :439 :468)|—|
|C5|`updated_seq` frozen at 0|KILLED|test_normal_run_writes_status|
|C6|`updated_seq` off by one|KILLED|test_normal_run_writes_status|
|C7|drop `updated_utc`|KILLED|test_normal_run_writes_status|
|C8|add a 13th key|KILLED|test_status_keys_exact|
|C9|`drained` hard-coded true|KILLED|test_late_client_frame_recorded_or_exit_70|
|D1 / D1b|non-atomic write (with / without delay)|KILLED|test_rewrite_is_atomic|
|D2|unlink+rename instead of `os.replace`|KILLED|test_sigterm_no_deadlock_under_contention|
|**D3**|**drop `status_lock`**|**SURVIVED**|— (78 passed in 74.6 s)|
|E1|SIGTERM handler not installed|KILLED|test_sigterm_writes_status_and_exits_70|
|E2|TERM path records no reason|KILLED|same|
|E3|TERM path exits 0|KILLED|same|
|E4|TERM path writes a FINAL status|KILLED|same|
|E5|TERM path writes no status|KILLED|same|
|F1|BrokenPipe reason drops the direction (V36)|KILLED|test_late_client_frame_recorded_or_exit_70|
|F2|BrokenPipe direction inverted, both pumps (V37)|KILLED|same|
|F3|forward-OSError arm removed from pump_pipe|KILLED|test_forward_enospc_stdout_devfull|
|F4|directional reason drops the errno (both pumps)|KILLED|test_directional_enospc[frames-client-to-agent.jsonl]|
|F5r|timeline reason drops the errno (re-aimed: seq is no longer in the text)|KILLED|test_write_failure_exit_70|
|F6|`forward_broken` latch removed in pump_fd|KILLED|test_late_client_frame_recorded_or_exit_70|
|F7|status-write-failure stderr line never printed|KILLED|test_status_write_failure_prints_stderr|
|G1–G4|framedir validation (4)|KILLED|test_framedir_dangling_symlink / test_empty_framedir / test_framedir_is_plain_file ×2|
|H1|exit code ignores drained/write_errors|KILLED|test_late_client_frame_recorded_or_exit_70|
|H2|write_errors ignored in the exit decision|KILLED|test_write_failure_exit_70|
|H3|signal normalisation removed|KILLED|test_sigterm_agent_exit_143|
|H4|`stdin_reader_done` never set|KILLED|test_c2a_directional_enospc_eof_agent_exits_70|
|N1|bounded latch: occurrence count off by one|KILLED|test_bounded_write_errors_dedup|
|N2|bounded latch never set (unbounded again)|KILLED|test_bounded_write_errors_dedup|
|**N3**|**write order swapped back (F17 revert)**|**SURVIVED**|— (78 passed in 75.8 s)|
|**N4**|**status snapshot outside the timeline lock (F5 revert)**|**SURVIVED**|— (78 passed in 75.2 s)|
|N5|initial status write dropped (F10 revert)|KILLED|test_initial_status_before_first_frame|
|**N6**|**TERM handler writes the status itself under `status_lock` (F11 revert)**|**SURVIVED**|— (78 passed in 75.4 s)|
|N7|unwritable FINAL status no longer forces exit 70|KILLED|test_unwritable_status_exits_70|
|**N8**|**directional-close error swallowed**|**SURVIVED**|— (78 passed in 76.2 s)|
|N8b|directional close not wrapped (the F3 hang regression)|KILLED|test_bounded_write_errors_dedup|
|N9|`pins.py` key ORDER perturbed|KILLED|test_status_keys_order_matches_pin (the pin is genuinely read)|
|N10|test drops the pins import for an identical local tuple|SURVIVED (**equivalent** by construction)|—|

**Totals: 54 run · 44 KILLED · 10 SURVIVED (2 equivalent: C4, N10) · 0 PATCH-FAILED.**
**Acceptance bar (A1 A2 A3 A4 A5 A6 A3+A6 B2 D3 each killed by a NAMED test): 6/9 met. A2, A6, D3 unmet.**

## Probe table

| probe | result |
|---|---|
|p1 / p1b|rc 64, exact stderr — ok|
|p2 (c2a in-flight race, 5 trials)|`exit70=5/5 ; exit70-with-EMPTY-write_errors=0/5`, each `['drain c2a: stopped with 257 recorded, 256 forwarded']`|
|p4 (stdout=/dev/full)|rc 70, `["forward a2c: [Errno 28] No space left on device"]`|
|p5|timeline `{'c2a':4,'a2c':3}` == status; drained True, errs []|
|p6|tee rc 143, `agent_returncode -15`, `exit_code 143` (A21b normalisation ok)|
|p7 (client never closes, 5 trials)|rc 0, drained True, `stdin_done False` 5/5|
|p8 (8 trials, 5000 frames)|rc 70 8/8, `['forward c2a: BrokenPipeError']`, all 5000 recorded|
|**p9 (audit-P2 shape, 3 trials)**|**pristine 3/3 CONTRACT_OK, wall 6.1 s** — but see p9-gap below|
|p9 vs **A2 mutant**|**3/3 `rc=0 … evidence has 1 … drained=True errs=[] rec_c2a=1 fwd_c2a=1 CONTRACT_OK=False`**|
|p9 vs A1 mutant (control)|3/3 same signature|
|**p9-gap sweep (mine)**|gap 1 s / 4 s → rc 70 LOUD 4/4. **gap 6 s / 8 s → rc 0, recorded 1 of 2, `drained:true`, `errs:[]` — SILENT LOSS 4/4**|
|p10 (torn status)|**pristine 0 torn / 573 924 reads** · **N4 mutant 267–767 torn / ~138k reads each** (first: `updated_seq 92, rec_c2a 46, rec_a2c 45`)|
|p11|rc 70, `final false`, both exit fields null, `["terminated: SIGTERM"]`|
|p12|`tee-status.json` present 1 s after identity (F10 closed)|
|p13 (2000-frame failing directional)|rc 70, 2 entries, 442-byte status|
|hang.py A–E|A/B/C rc 70 in 0.1 s (**F3 hang gone**); E rc 70; D is a **vacuous case** (its EOF agent emits no a2c frame, so nothing is lost — not a defect)|
|**killsnap 20 trials**|**A21d-FAIL 19 / PASS 1** (bar: 20/20). Every failure is `updated_seq != timeline last seq` (+ `recorded_<dir> != timeline count`); internal consistency `updated_seq == rec_c2a+rec_a2c` holds in 19/19|
|sigterm_deadlock (12 trials, 3000-entry write_errors)|**12/12, `secs_after_term` 0.00 s, rc 70, final false, 4 errors — HUNG=0**|
|**lockrepro (mechanism)**|**process became TERM-PROOF**: SIGTERM at t=60 s ignored, still alive at t≈11 min in `futex`, only SIGKILL ended it|
|f9probe (old racy shape) idle 12|`{70: 12}`, `fwd_c2a` 2–14 of 100|
|f9probe under 8 burners|**`{70: 10, 0: 2}`** — the pre-712fe01 shape is still race-dependent (the shipped test's determinism comes from `os.close(0)`, not from the tee)|
|ordering (12 SIGKILLs, bidirectional 20k)|**pristine: directional-ahead 0/12** · **N3 mutant: 3/12**|
|pipe capacity (F_SETPIPE_SZ 4096 and 1 MiB)|`test_agent_burst_drained` PASS/PASS · `test_rewrite_is_atomic` PASS/PASS (reads 93 / 181) — **F-PC-1/F-PC-2 are genuinely capacity-independent**|
|hostile inputs (10 cases)|8 MiB line, NUL, NaN, Infinity, 1e999, no-trailing-NL, CRLF, empty, bare-NL, invalid-UTF-8 → **all rc 0, 12 keys, fwd==rec, no hangs**|
|write_errors on 3000 frames + unwritable timeline|**exactly 2 entries, 455 bytes**: `'timeline c2a: [Errno 28] No space left on device (3000 occurrences)'`, same for a2c (round 6: 3003 entries / 194 320 bytes)|
|forward-lag probe (20k frames)|**153 507 of 346 574 running snapshots have `forwarded < recorded` and `drained:false`**; final status correct (`fwd==rec==20000`, rc 0)|
|30 clean legs|0 invariant violations|
|cost|11-frame leg: shipped median **0.068 s** vs no-status 0.062 s (round 6: 0.058/0.060) — within the 2× bar. 10000+10000: **8.29 s vs 2.28 s = +6.01 s** (round 6: +5.17 s). Production-shape drain: **5 s/leg**, p9 wall 6.1 s|

## A21d verdict table — the tee's own output through `check_acp_conformance.check_tee_status`

(`check_tee_status` is reachable: registered at `check_acp_conformance.py:193/:209`, invoked at `:1543` via `_run_check`.)

| leg | tee rc | `check_tee_status` verdict |
|---|---|---|
|clean (5 c2a + 5 a2c, agent 0)|0|**A21d-PASS**|
|SIGKILL mid-stream (bidirectional)|-9|**A21d-FAIL**: `tee-status.json recorded_c2a 18969 != timeline c2a count 18970`|
|**SIGTERM**|70|**A21d-FAIL**: `tee-status.json write_errors is not empty` — dies at `:1272`, never reaches the non-final arm at `:1304`|
|drain-stop (client never reads)|70|**A21d-FAIL**: `tee-status.json drained is not true` (expected for a failed leg; recorded for completeness)|

---

## Findings

**R8-B5c-F1 [CRITICAL] SOLID — the audit-P2 defect is reproducible on the SHIPPED tee, no mutant needed: a client frame arriving more than 5 s after the previous one is silently lost with exit 0.**
`…/vb8/repo/proofs/S0-01/tools/frame_tee.py:425-439` (c2a drain, fixed `stall_timeout = 5` at `:404`) and the docstring at `:22-24`.
Proof (`…/vb8/work/p9delay.py`, agent reads one line, answers, exits 0; client holds stdin open, sends frame 2 after a gap):
```
gap=1.0s rc=70 recorded=2 errs=['forward c2a: BrokenPipeError','drain c2a: stopped with 2 recorded, 1 forwarded'] -> LOUD(ok)
gap=4.0s rc=70 recorded=2 (same)                                                                                   -> LOUD(ok)
gap=6.0s rc=0  wall=5.2s client_sent=2 recorded=1 drained=True errs=[]  -> *** SILENT LOSS ***
gap=8.0s rc=0  wall=5.1s client_sent=2 recorded=1 drained=True errs=[]  -> *** SILENT LOSS ***   (2/2 each)
```
Observed: the tee unilaterally exits 0 five seconds after the agent exits, while the client still holds the session pipe open; the frame is absent from `frames-client-to-agent.jsonl` and the leg is A21d-clean. Expected (docstring `:22-24`): "A frame the client wrote before the tee exits MUST be recorded in frames-client-to-agent.jsonl, or the tee exits 70". The drain loop moved the cliff from 0 s to 5 s; it did not remove it.
Red test to add: `test_late_frame_after_the_drain_window_is_loud` — p9 shape with a 7 s gap, asserting the frame is recorded **and** `rc == 70` **and** `write_errors != []`. (Closing it requires a coordinator ruling: either the c2a drain runs until client EOF, or a stall-stop with `stdin_reader_done False` is itself a `write_errors` entry and exit 70.)

**R8-B5c-F2 [CRITICAL] SOLID — mutant A2 survives and reproduces the audit signature verbatim with a fully green suite; the bar named A2 explicitly.**
`frame_tee.py:431` (`elif time.monotonic() - stall_start_c2a >= stall_timeout:` → `>= 0`). Suite: `78 passed in 61.69s`. p9 against it, 3/3:
`P9 trial 0 rc=0 elapsed=0.2s client sent 2 c2a frames, evidence has 1 | drained=True stdin_done=False errs=[] rec_c2a=1 fwd_c2a=1 | CONTRACT_OK=False`
— byte-for-byte the round-6 F1 signature. Mechanism: both F1/F2 tests send the late frame while the agent is still sleeping 1 s, so the frame is recorded **before** `proc.wait()` returns; they kill A1 only through the missing `drain c2a: stopped` entry, never through frame loss. The test named `test_late_frame_after_reap_with_client_holding_stdin` (`tests/test_s0_01_frame_tee.py:344`) is **not** an after-reap test — its docstring and name assert a precondition the code does not establish.
Red test to add: the F1 fix above; additionally re-point `test_late_frame_after_reap_with_client_holding_stdin` so the client waits for the agent's *exit* (poll `tee-status.json` for `final`/the agent's death, or have the agent write a sentinel file on exit) before sending the late frame.

**R8-B5c-F3 [HIGH] SOLID — killsnap is 19/20 A21d-FAIL; the lane brief's bar was 20/20, and this is worse than round 6's 15/20.**
`frame_tee.py:253-271` (timeline write + `seq[0] += 1` + `recorded_*` under `lock`) vs `:293` (`_write_status()` **after** the lock is released). 20 SIGKILLs at random instants, graded exactly as `check_tee_status` grades:
```
{"i":0,"verdict":"A21d-FAIL","failed":["recorded_c2a==timeline_c2a","updated_seq==timeline_last_seq"],
 "updated_seq":38307,"rec_c2a":19154,"rec_a2c":19153,"tl_c2a":19155,"tl_a2c":19153,"tl_last":38308}
SIGKILL-at-random-instant trials=20  A21d-FAIL/NO-STATUS=19  A21d-PASS=1
```
Reproduced through the checker itself (A21d table, SIGKILL row). Observed: the status is now internally consistent but **stale** — the timeline leads it by 1–2 entries. Expected (incident-log ruling, `docs/INCIDENT-LOG.md:20`): "`updated_seq` == the timeline's last seq". Structural: two files cannot be written atomically together.
Red test to add: `test_sigkill_status_matches_timeline_20_trials` (bidirectional load, 20 kills, assert `recorded_<dir> == timeline count` and `updated_seq == last seq` every trial). It will be RED — this needs a coordinator ruling (write the status **inside** `lock` before releasing it, so the status can only trail the timeline by whole frames and the checker's rule is relaxed to `updated_seq <= last_seq` with an explicit skew bound; or the tee writes the seq it is *about* to commit).

**R8-B5c-F4 [HIGH] SOLID — the SIGTERM status the F6 ruling specifies is rejected by the checker, and not by the arm it was written for.**
`frame_tee.py:466-469` produces `write_errors: ["terminated: SIGTERM"]`; `proofs/S0-01/check_acp_conformance.py:1272` raises `write_errors is not empty` **unconditionally**, before the `final`/non-final split at `:1297/:1304`. Measured verdict: `A21d-FAIL: sigterm: tee-status.json write_errors is not empty`. `test_sigterm_writes_status_and_exits_70` (`:1273`) asserts the fields but never feeds the status to the checker, so the collision is invisible.
Red test to add: `test_sigterm_status_satisfies_check_tee_status` — import `check_tee_status`, run the TERM leg, assert it passes. Fixing it is a checker-side ruling (exempt non-final legs from the `drained`/`write_errors` gates, or whitelist `terminated: SIGTERM`) — out of this lane's two-file boundary, so it must be raised, not silently left.

**R8-B5c-F5 [HIGH] SOLID — the F5 fix is real but gated by nothing: mutant N4 reverts it and the suite stays 78/78 green.**
`frame_tee.py:195-200` (`with lock:` around the snapshot) → `if True:`. Suite `78 passed in 74.97s`. The property is measurable: p10 with bidirectional load and a spinning reader gives **pristine 0 torn in 573 924 reads**, **N4 267 / 767 / 267 torn**. `test_rewrite_is_atomic` (`tests/…:1593`) cannot see it for two structural reasons: its agent produces **a2c only** (stdin closed at `:1613`), so the only status writer while frames flow is the a2c pump itself — the concurrent-writer condition never exists — and its reader polls with `time.sleep(0.001)`, yielding 93–181 reads against p10's ~150 000.
Red test to add: `test_status_snapshot_is_never_torn_under_bidirectional_load` — client streams ≥5 000 c2a frames while the agent echoes, reader thread spins with **no** sleep, assert `updated_seq == recorded_c2a + recorded_a2c` on every read and `reads > 10_000`.

**R8-B5c-F6 [HIGH] SOLID — mutant D3 survives; `status_lock` is still untested, and the lane's `not_done` predicted the opposite.**
`frame_tee.py:217` (`with status_lock:` → `if True:`). Suite `78 passed in 74.37s`. B5c-report.md `not_done` says "D3 (drop status_lock): expected killed by test_rewrite_is_atomic's seq consistency check" — measured false. Why it survives: `os.replace` publishes atomically regardless, and the tmp-file collision needs two concurrent writers, which `test_rewrite_is_atomic`'s a2c-only workload never creates.
Red test to add: the F5 test above will kill D3 too (concurrent writers truncating the same `.tee-status.tmp`); add an explicit assertion that no read of `tee-status.json` ever fails to parse across ≥10 000 reads under bidirectional load.

**R8-B5c-F7 [HIGH] SOLID — the F17 write order is ungated: mutant N3 reverts it green, while the property it protects is real and measurable.**
`frame_tee.py:260-270` and `:341-350` (timeline first, then directional). N3 (order swapped in both pumps): `78 passed in 75.50s`. My ordering probe, 12 SIGKILLs, bidirectional 20 000-frame load: **pristine directional-AHEAD 0/12**; **N3 3/12** (trial 0 `tl_a2c=18541 dir_a2c=18542`; trial 3 `tl_c2a=18736 dir_c2a=18737`; trial 6 `tl_a2c=18985 dir_a2c=18986`). `test_directional_trails_timeline_after_sigkill` (`tests/…:1650`) is too weak: 5 trials, a2c-only, 500 frames, kill once `forwarded_a2c >= 10`, and `assert len(results) >= 3` lets two trials silently drop out.
Red test to add: same test at 12 trials, **both** directions loaded (client streams while the agent echoes), 20 000 frames, kill instants spread over 0.15–0.75 s, asserting `dir_c2a <= tl_c2a and dir_a2c <= tl_a2c` on every trial and `len(results) == 12`.

**R8-B5c-F8 [HIGH] SOLID — mutant C1 survives and is exploitable; this is a regression, C1 was KILLED in round 6.**
`frame_tee.py:293` (the c2a pump's `_write_status()` → `pass`). Suite `78 passed in 71.98s`. Exploitation (`…/vb8/work/c1probe.py`, agent consumes but never replies, so the main thread is parked in `proc.wait()` and the c2a pump is the only status writer; 10 frames at 0.2 s intervals, then SIGKILL):
```
shipped    client_sent=10 timeline_lines=10  recorded_c2a=10 forwarded_c2a=10 updated_seq=10  A21d(recorded==timeline)=True
C1-mutant  client_sent=10 timeline_lines=10  recorded_c2a=0  forwarded_c2a=0  updated_seq=0   A21d(recorded==timeline)=False
```
The F10 initial status write plus the main thread's drain-loop writes mask the loss for every test in the suite. Observed: a c2a-only leg's running status frozen at zeros; expected: A21d's "rewritten after every … frame".
Red test to add: `test_running_status_tracks_c2a_before_the_agent_exits` — long-lived agent that consumes and stays silent, client sends N frames, poll `tee-status.json` and assert `recorded_c2a` reaches N **while the tee is still running**.

**R8-B5c-F9 [HIGH] SOLID — the forward write outside the lock makes ~44 % of running snapshots A21d-inconsistent; the lane's "adjacent defect 2" understates it.**
`frame_tee.py:272-292` (forward + `forwarded_* += 1` outside `lock`) vs `:199-202` (the snapshot). On a clean 20 000-frame bidirectional leg:
```
reads=346574  snapshots with forwarded<recorded=153507  first={'recorded_c2a':7,'forwarded_c2a':6,'recorded_a2c':2,'forwarded_a2c':2,'drained':False,'updated_seq':9}
FINAL: rc=0 fwd_c2a=20000 rec_c2a=20000 fwd_a2c=20000 rec_a2c=20000 drained=True errs=[]
```
The final status is correct (30/30 clean legs, 0 violations), but any SIGKILL landing in that window leaves a status the checker rejects at `check_acp_conformance.py:1270` (`drained is not true`) and `:1274` (`forwarded_c2a != recorded_c2a`) — a **second, independent** A21d hole beyond F3. B5c-report.md says "The F5 invariant … is unaffected because it only involves seq and recorded": true for the seq invariant, false for A21d.
Red test to add: `test_running_status_forwarded_never_lags_recorded` (spinning reader over ≥100 000 reads, assert `forwarded_c2a == recorded_c2a` on every snapshot). It will be RED — the fix is to increment `forwarded_*` under `lock` after the forward, or to snapshot `(recorded, forwarded)` as one pair taken *after* the forward completes.

**R8-B5c-F10 [MED] SOLID — the F11 fix is ungated (mutant N6 green), and the mechanism it prevents makes the process TERM-proof.**
`frame_tee.py:387-388` (`def _sigterm_handler … raise _Terminated()`). N6 restores the round-6 shape (handler takes `status_lock` and writes the status itself): `78 passed in 75.21s`. `test_sigterm_no_deadlock_under_contention` (`tests/…:1324`) cannot see it — the window is one status write, so it is probabilistic. Mechanism reproduced (`lockrepro.py`): the process **ignored SIGTERM at t = 60 s and was still alive ≈11 minutes later**, ending only on SIGKILL. The shipped code is correct: `sigterm_deadlock.py` 12/12, `secs_after_term` 0.00 s, rc 70, with a 3 000-entry `write_errors`.
Red test to add: a structural assertion rather than a timing one — `test_sigterm_handler_takes_no_lock`: `inspect.getsource(frame_tee)`-style check is fragile, so instead run the tee with `S0_01_FRAMEDIR` on `/dev/full` for the **status tmp** (making each status write slow) and TERM 20 times, asserting every TERM is answered within 1 s; N6 hangs on a meaningful fraction there. Cheapest robust alternative: assert the handler body is exactly `raise _Terminated()` via `ast` on the source file.

**R8-B5c-F11 [MED] SOLID — the F19 close-error entry is emitted but asserted by no test (mutant N8 green): the named F19 test is a tautology.**
`frame_tee.py:295-298` / `:366-368`. N8 (both `except OSError as e: … append(...)` → `except OSError: pass`): `78 passed in 75.94s`. Measured entries in the exact scenarios the tests use:
```
a2c on /dev/full, 3-frame agent -> ["directional a2c: [Errno 28] … (3 occurrences)", "directional a2c close: [Errno 28] …"]
c2a on /dev/full, 1-frame agent -> ["directional c2a: [Errno 28] …",                  "directional c2a close: [Errno 28] …"]
```
`test_a2c_directional_close_error_recorded` (`tests/…:1163`, the lane's F19 deliverable) asserts `len([e for e in write_errors if "a2c" in e]) >= 1` — satisfied by the **first** entry alone. `test_directional_enospc` (`:1130-1131`) uses `for e in status["write_errors"][1:]: assert e.startswith(...)`, which becomes **vacuous** the moment the entry is gone.
Red test to add: exact list equality — `assert status["write_errors"] == ["directional a2c: [Errno 28] No space left on device (3 occurrences)", "directional a2c close: [Errno 28] No space left on device"]`.

**R8-B5c-F12 [MED] SOLID (survivor) / UNSURE (exploitability) — mutant A6 survives; I could not build a leg where it changes behaviour.**
`frame_tee.py:445-446`. Suite `78 passed in 75.17s`. A6 changes the exit code only when `forwarded_c2a != recorded_c2a` **and** `write_errors == []` at `:454`. I traced every route out of the c2a drain (`:425-439`): the loop exits either because `ti` died (the pump's `finally` has run, so all forwards completed or errored — and every forward error appends an entry at `:278/:286`) or because `c2a_stalled` (which appends the drain entry at `:436`). So the difference set appears empty and A6 is argued **equivalent w.r.t. the exit decision**. Flagged UNSURE because that is my argument, not a test's, and it breaks the instant any other arm changes — which is exactly what A3+A6 did in round 6.
Red test to add: none that A6 alone would fail; instead keep A3+A6 (killed) in the standing mutant set and assert the exit code's *reason* (`status["drained"]` and `status["write_errors"]` together) rather than the code alone.

**R8-B5c-F13 [MED] SOLID — exact-reason discipline is not met on four assertions the brief singled out, and the F7 ruling's own bar is unmet.**
`tests/test_s0_01_frame_tee.py`: `:963` + `:965` (`startswith` filter, then `"(5 occurrences)" in dir_errors[0]` — F7's ruling said "assert the exact single entry"); `:1130-1131` (`for … [1:] … startswith`, vacuous when empty); `:1159-1160` (`startswith` + `>= 1`); `:1191-1192` (`"a2c" in e` + `>= 1`). Counts pasted from grep: `startswith` ×3; substring asserts ×3 in `write_errors`; `>=`/`<` on counts ×22 file-wide, of which `:1160`, `:1192` and `:1724` (`assert len(results) >= 3`) are slack on the assertion itself rather than on an inequality that is genuinely two-sided.
Red test to add (F7): `assert status["write_errors"] == ["directional c2a: [Errno 28] No space left on device (5 occurrences)"]`.

**R8-B5c-F14 [MED] SOLID — the lane's `not_done` is materially wrong, not merely incomplete, and the runner it deferred to could not have run.**
B5c-report.md lists D3, B2, A2/A3/A4/A6/A3+A6 as "expected killed … needs verification". Measured: B2 ✓, A3 ✓, A4 ✓, A3+A6 ✓ — **A2 ✗, A6 ✗, D3 ✗**. Separately, running `tasks/briefs/s0-01-b5c-support/probes/mut.py` as-is would have reported **17 of 42** mutants and silently classed the other **25 as PATCH-FAILED** (neither killed nor survived) — the anchors are aimed at the 424-line round-6 file. The report's `not_done` names only the missing `PROBE_WORK` env, not the re-aiming.

**R8-B5c-F15 [LOW] SOLID — two docstring claims are falsified by the code they describe.**
`frame_tee.py:11` "tee-status.json is rewritten after every **forwarded** frame" — the calls at `:293` and `:363` sit **outside** the `if not forward_broken:` block, so it is rewritten after every **recorded** frame (p8: 5 000 recorded / 51 forwarded, with a rewrite per recorded frame). `:12-13` "The `final` field is true only on the exit write" — there are two exit writes and the SIGTERM one (`:468`) is `final=false`; the closing paragraph at `:29-30` contradicts the opening. F18's "forwarded means written into the pipe" and F14's 5 s drain cost are both accurate and confirmed (p9 wall 6.1 s).
Fix: "…after every recorded frame…"; "…true only on the clean-exit write (`:459`); the SIGTERM write at `:468` is non-final."

**R8-B5c-F16 [LOW] SOLID — the lane's fourth gate line is not a contended run.**
B5c-report.md pastes `78 passed in 454.41s` and `78 passed in 159.75s` as the contended pair. Under the brief's recipe (`nice -n 19`, four `yes > /dev/null`, load 5.8–7.0) I measured **426.97 s** and **439.17 s**; my idle runs were 74.76 s and 74.93 s. 159.75 s is ~2× idle — that run was effectively uncontended, so the mandated pair is really 1 valid run, not 2.

**R8-B5c-F17 [LOW] SOLID — a failing tee test leaks the tee and its agent.**
After my N8b mutant run, `mutruns/N8b/proofs/S0-01/tools/frame_tee.py` and `…/pt/test_bounded_write_errors_dedu0/agent.py` were still running **22 minutes** later (`ps -eo etime`), after the mutant tree had been deleted. Cause: `test_bounded_write_errors_dedup` (`tests/…:945`) calls `tee_proc.wait(timeout=15)` with no `try/finally: tee_proc.kill()`. Same shape at `:759` (`test_agent_burst_drained`), `:806` (`test_never_reading_client`), `:1218`, `:1312`, `:1362`, `:1569`, `:1636`, `:1690`. On the PC's 8-worker runs this is how a red turns into a wedged box.
Fix: wrap every `Popen`-based test body in `try/finally` with `kill()` + `wait(timeout=5)`, as `TestLateClientFrameRecorded` already does at `:337-339`.

**R8-B5c-F18 [LOW] SOLID — an undisclosed rename of the test that carried the F-PC-2 shape.**
`test_agent_burst_within_pipe_buffer_drained` is absent; `test_agent_burst_drained` (`tests/…:735`) replaces it. The report's table lists only the new name under F-PC-2. Round 6's F2 was raised for exactly this class (a test carrying a shape disappearing without disclosure); the rename is legitimate here, the silence is not.

**R8-B5c-F19 [INFO] SOLID — cost moved the right way on the real-leg shape and the wrong way on the contention shape.**
11-frame real-leg shape: shipped median **0.068 s** (min 0.062, max 0.174) vs the no-status variant 0.062 s — within the brief's 2× bar against round 6's 0.058 s. 10 000 + 10 000 shape: **8.29 s vs 2.28 s (+6.01 s, 3.6×)** against round 6's +5.17 s; the extra ~0.8 s is the F5 `with lock:` snapshot now contending with both pumps 20 000 extra times. Production-shape drain cost unchanged at 5 s/leg (p9 wall 6.1 s), as F14 rules.

**R8-B5c-F20 [INFO] — premise shift**, see the header. `fcd0cbf → 57a7df6` mid-run; all four scope/context files byte-identical at both; grade unaffected.

### Closures I reproduced as genuinely closed

**F3** (hang gone — hang.py B/C rc 70 in 0.1 s; round 6: HANG at 25 s). **F4** (the contended gate is **GREEN 2/2**, 426.97 s and 439.17 s, where round 6 was `1 failed` 2/2; also 10/10 under `taskset -c 0` in 23.16 s). **F6 code-side** (non-final, both exit fields null, `["terminated: SIGTERM"]`, rc 70 — E1–E5 all killed; the checker collision is F4 above). **F7** (2 entries / 455 bytes on a 3 000-frame leg vs 3 003 entries / 194 320 bytes; N1 and N2 both killed). **F8** (B1/B2/B3 all killed by `test_never_reading_client`'s computed exact list). **F9** (N7 and mutant F7 both killed). **F10** (N5 killed; p12 shows the status present before the first frame). **F11 code-side** (12/12 TERM answered in 0.00 s with a 3 000-entry `write_errors`). **F13** (`rc_val` absent). **F16** (local `STATUS_KEYS` gone; N9 — perturbing `pins.py` — is KILLED, so the pin is genuinely load-bearing). **F17 code-side** (0/12 directional-ahead). **F19 code-side** (the entry is emitted; only its assertion is hollow — F11 above). **F-PC-1 / F-PC-2** (both tests pass with a 1-page and a 1-MiB pipe — no capacity assumption remains). **Hostile inputs** 10/10 clean, including an 8 MiB line (0.6 s) and invalid UTF-8. Boundary respected: `ea8414f` touches only the two lane files plus the report; line counts 424→473 and 1213→1724 verified against `2877327`; all 17 tests the report names exist at the lines given.

## Gate summaries (verbatim `pytest-summary:` lines, on my scratch copy)

```
idle 1     : 78 passed in 74.76s (0:01:14)          pytest-exit: 0
idle 2     : 78 passed in 74.93s (0:01:14)          pytest-exit: 0
contended 1: 78 passed in 426.97s (0:07:06)         pytest-exit: 0    (nice -n 19, 4 burners, load 5.80)
contended 2: 78 passed in 439.17s (0:07:19)         pytest-exit: 0    (nice -n 19, 4 burners, load 6.97)
taskset -c 0 subset: 10 passed, 68 deselected in 23.16s   pytest-exit: 0   (subset RAN: 10 selected)
pyflakes proofs/S0-01/tools/frame_tee.py tests/test_s0_01_frame_tee.py -> rc 0
```
tmp_path hygiene: PASS — the only files appearing in the run tree are `__pycache__/*.pyc`; every test artifact lands under `/tmp/pytest-of-root` (≈102 MB per suite run).

## Reproduced vs static vs skipped

**Reproduced (ran it myself):** all four suite gates plus the `taskset -c 0` subset; 54 mutants against the full 78-test suite; probes p1, p1b, p2, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13; `hang.py` A–E; `killsnap.py` 20 trials; `sigterm_deadlock.py` 12 trials; `lockrepro.py`; `f9probe.py` idle 12 + 8-burner 12; `cost.py` (re-aimed); plus six probes I wrote — the p9 gap sweep, the bidirectional SIGKILL ordering probe (pristine + N3), the pipe-capacity variants of the two PC-venue tests, the 10-case hostile-input battery, the forward-lag probe, and the C1 exploitability probe — and the A21d conformance run through the real `check_tee_status`.
**Static only:** `check_acp_conformance.py`'s own test suite (lane A5e is live on that file — I imported the module and called one function, and read `:1260-1309`, `:193`, `:209`, `:1543`); `crates/buzz-acp/src/acp.rs` (on the PC, not readable here — the 5 s shutdown-kill figure in F1's production framing is cited to `docs/INCIDENT-LOG.md:20`, not verified).
**Deliberately skipped:** `p1c` (running as root bypasses the 0500 parent — meaningless in this sandbox); the PC venue (no bridge banner this session, so the PC-side 8-worker shape is `NOT run here`); mutating `check_acp_conformance.py` (outside this lane's boundary and a live lane's file).

---

## **VERDICT: NOT-READY.**

The lane closed a great deal that was genuinely broken — the ENOSPC hang, the contended-gate red, the unbounded `write_errors`, the missing initial status, the TERM-path deadlock, both PC pipe deadlocks, and the exact-text arms — and I reproduced every one of those closures. But the finding the round exists for is still open: **the audit-P2 shape reproduces on the shipped tee with a 6 s gap (F1, 4/4) and on a one-line surviving mutant with a fully green suite (F2)**, the A21d running status fails its own checker on 19 of 20 production-shaped kills (F3) and on the SIGTERM leg the coordinator's own ruling produces (F4), and the four fixes the round was graded on — the lock snapshot (F5), `status_lock` (F6), the write order (F7), the c2a running status (F8) — are each reverted green by a mutant.

**Blocking: R8-B5c-F1, F2, F3, F4, F5, F6, F7, F8, F9.** Non-blocking but to be fixed in the same lane: F10–F18.

This verdict does not depend on anything I failed to reproduce. Two statements are qualified in-line: **F12** (mutant A6 is a survivor I argue is equivalent — the argument is analytic, not measured) and the production framing in **F1** (buzz-acp's 5 s shutdown wait is cited to the incident log; the pinned Rust source is not readable from the sandbox).