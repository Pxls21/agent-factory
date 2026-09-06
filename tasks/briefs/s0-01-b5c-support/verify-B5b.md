# VERIFY-B5b — round 6, frame tee — **VERDICT: NOT-READY**

**Premise check PASSED at start** (`80160ca` / `ec270f3` / `ad4aac1` / `79f8f5b`, branch `claude/soundbox-kit-migration-iz1jwf`).
**PREMISE SHIFTED MID-RUN — reported loud:** the shared tree moved to `7cd83c7` while I was verifying. `712fe01` ("the late-client-frame control sequences its precondition instead of racing") rewrote `TestLateClientFrameRecorded` in **my lane's file**. `proofs/S0-01/tools/frame_tee.py` is unchanged (sha `214b65e9…` at both). I re-ran every survivor and the idle gate against the new HEAD file; results below are labelled by tree. I changed nothing in the shared tree (`git status --porcelain` on both lane files: empty).

Work location: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vb6/` (`base/` = 80160ca copy, `head/` = 7cd83c7 copy, `pristine*/`, `mutruns*/`, `probes.py`, `hang.py`, `killsnap.py`, `cost.py`, `sigterm_deadlock.py`, `mut.py`).

## Findings

**R6-B5b-F1 [CRITICAL] SOLID — R5-B5-F1 / audit-P2 is fixed in the code but gated by NOTHING; the exact audit defect can be restored with a one-line revert and the suite stays 68/68 green.**
`proofs/S0-01/tools/frame_tee.py:385-399` (c2a drain loop). Mutant **A1** (`while ti.is_alive():` → `while False and ti.is_alive():`) → full suite **68 passed in 59.95s** (and **68 passed in 60.60s** against the HEAD test file). Against that mutant, probe p9 reproduces the round-5 finding verbatim, 3/3:
`P9 trial 0 rc=0 elapsed=0.1s client sent 2 c2a frames, evidence has 1 | drained=True stdin_done=False errs=[] rec_c2a=1 fwd_c2a=1 | CONTRACT_OK=False`
The named closure test **passes on every mutant that reverts the mechanism** — `test_late_client_frame_recorded_or_exit_70`: `1 passed, 67 deselected` on A1, A2, A3, A5, A6 (both the 80160ca and the 712fe01 version). Worse, composing two survivors (**A3+A6**, both individually green) yields the audit's exact P2 signature with a green suite:
`P2 trial 0..4 rc=0 drained=False fwd_c2a=256 rec_c2a=257 n_err=0 []` — *lost a client frame, empty write_errors, exit 0*, while `68 passed in 68.28s`.
**Fix:** a test in the p9 shape whose late frame arrives **after `proc.wait()` has returned** (agent already reaped, client writes ≥1 s later) asserting the frame is in `frames-client-to-agent.jsonl` **and** rc 70; plus a test that pins the drain-stop reason exactly.

**R6-B5b-F2 [HIGH] SOLID — the round-5 test that DID cover the p9 shape was deleted, undisclosed.**
`TestAgentExitsWhileStdinOpen::test_tee_exits_cleanly_with_agent_code` (541648c test file :310-371 — helper writes frame 1, sleeps 1.0 s, writes frame 2; asserts `rc == 0` and `elapsed < 6`) is absent at 80160ca and at HEAD. B5b.md lists the F12 retitle and the F8 rewrite but **not this deletion**. Its assertions both invert under the new semantics (measured: p9 gives rc 70, elapsed 6.1 s) — a test the change turned red was removed rather than re-pointed at the new contract, and it was the only test carrying the finding's shape.
**Fix:** restore it with the round-6 contract (`rc == 70`, frame 2 recorded, `write_errors == ["forward c2a: BrokenPipeError", "drain c2a: stopped with 2 recorded, 1 forwarded"]`).

**R6-B5b-F3 [HIGH] SOLID — HANG (fail-open): an unwritable `frames-client-to-agent.jsonl` kills the c2a pump inside its `finally`, `proc.stdin` is never closed, and the tee hangs forever with an EOF-reading agent.**
`frame_tee.py:249-257` — `df.close()` runs first in the `finally` and re-raises the buffered ENOSPC, so `state["stdin_reader_done"] = True` (:252) and `dst.close()` (:255) never execute. Reproduced (`hang.py`):
```
B-EOF-agent-1-line     n=1   rc=HANG(killed at 25s) status=final=False exit=None errs=1
C-EOF-agent-100-lines  n=100 rc=HANG(killed at 25s) status=final=False exit=None errs=100
   tee stderr: Exception in thread Thread-1 (pump_fd): ... frame_tee.py:250 df.close()
               OSError: [Errno 28] No space left on device
```
The suite's `test_directional_enospc[frames-client-to-agent.jsonl]` masks it: its agent exits after one `readline()`, so case A returns rc 70 in 0.1 s — with the same unhandled thread traceback, unasserted. The tee's own round-6 docstring (:15-19) mandates the EOF-consuming agent shape that hangs. Pre-existing (round-5 file hangs identically, `frame_tee.r5.py:187`, and leaves **no** status at all) but inside this lane's declared class sweep ("every exit path").
**Fix:** `try: df.close() except OSError as e: state["write_errors"].append("directional %s close: %s" % (direction, e))` before the rest of the `finally`; test = case B asserting rc 70 within a bounded wait.

**R6-B5b-F4 [HIGH] SOLID — a race-dependent test fails the mandated contended gate 2/2; AF-AP-46's sibling arm was not swept.**
`tests/test_s0_01_frame_tee.py:1080` at HEAD (`:1051` at 80160ca), `TestConsumeToEofRequired::test_agent_exits_without_consuming_stdin_exit_70`, byte-identical in both trees (`git diff 80160ca..HEAD` touches only the F1 test).
```
CONTENDED-1 (nice 19, 4 burners): 1 failed, 67 passed in 290.29s   E assert 0 == 70
CONTENDED-2 (nice 19, 4 burners): 1 failed, 67 passed in 384.62s   E assert 0 == 70
```
Mechanism reproduced: 100 × ~50 B fits the 64 KB pipe buffer, so whether a `BrokenPipeError` occurs at all is a scheduling race. `f9probe.py`: idle 12/12 `fwd_c2a` 3-9 of 100 → rc 70; under 8 burners `fwd_c2a` reaches **98/100** — two frames from the green-suite failure. `712fe01` fixed the identical shape in the F1 twin and registered AF-AP-46; this arm was left.
**Fix:** the 712fe01 pattern (agent `os.close(0)` before answering; late frames sent after the handshake), or ≥ 64 KB of late payload.

**R6-B5b-F5 [HIGH] SOLID — A21d's running status is not internally consistent: `_write_status` snapshots the counters and `seq[0]` without the timeline lock, and 15/20 SIGKILLed legs fail A21d's own checker rules.**
`frame_tee.py:148-165` takes only `status_lock`; the timeline write + `seq[0] += 1` + `recorded_<dir> += 1` are one atomic step under `lock` (:200-211, :286-297). A snapshot between them counts a seq the counters do not.
Concurrent-reader probe (p10, 20 000 frames): **31 990 / 137 024, 24 022 / 150 639, 5 152 / 103 064 snapshots torn** (`updated_seq != recorded_c2a + recorded_a2c`; first: `updated_seq 10, rec_c2a 8, rec_a2c 1`).
Production-shaped probe (`killsnap.py` — SIGKILL at a random instant, exactly buzz-acp's shutdown per `docs/INCIDENT-LOG.md`, then grade the survivors as A21d says the checker does): **15/20 A21d-FAIL**, e.g. `updated_seq 38187, rec_c2a 19096, tl_c2a 19097, tl_last 38188` → `recorded_c2a != timeline c2a` **and** `updated_seq != timeline last seq`.
`test_rewrite_is_atomic` (:1147) only checks JSON parseability, and runs a c2a-idle scenario, so it cannot see this; mutant **D3** (drop `status_lock` entirely) SURVIVES the full suite in both trees — the lock is untested. Rate-dependent: at real-leg volume (11 frames, mostly idle) the odds per leg are small; the fix is one line.
**Fix:** take `lock` inside `_write_status` while snapshotting (or snapshot `(seq, counters)` as one tuple under `lock`); test = a concurrent reader asserting `updated_seq == recorded_c2a + recorded_a2c` on every snapshot.

**R6-B5b-F6 [HIGH] SOLID — the new SIGTERM handler writes a `final: true` status that satisfies no A21d arm.**
`frame_tee.py:345-352`. Probe p11: `final=true, agent_returncode=null, exit_code=70` → A21d says "when final, A21b" (`exit_code == agent_returncode`, else `128+(-rc)`) and "when not final, both exit fields null"; this status is neither. Reachable exactly where F4 was aimed: `proofs/S0-01/tools/pc/pc_post.sh:97` TERMs surviving tee/agent pids (with no KILL fallback, unlike the buzz-acp path at :94-95). `test_sigterm_writes_status_and_exits_70` (:942) asserts `exit_code`, `write_errors`, `final` — never `agent_returncode`, so the conflict is invisible.
**Fix:** coordinator ruling — either an A21e arm (`final` + `terminated: SIGTERM` ⇒ exit fields exempt from A21b) or `final=false` on the TERM path; then assert `agent_returncode` in that test.

**R6-B5b-F7 [MED] SOLID — `write_errors` is still unbounded; R5-B5-F6 is only half closed.**
The `forward_broken` latch covers the two forward arms only. The directional arms (:188-189, :274-275) and the four timeline arms (:209-210, :224-225, :295-296, :310-311) append **once per frame** with no latch: 3 000-frame leg with an unwritable timeline → **3 003 entries, 194 320-byte tee-status.json**, rewritten once per frame. B5b.md's `not_done` claims F6 is "killed by F3's exact lists + the forward_broken flag" — that is false for the growth class it was raised about.
**Fix:** latch per (arm, direction) with a count, e.g. `"directional c2a: [Errno 28] … (N occurrences)"`; assert the exact single entry.

**R6-B5b-F8 [MED] SOLID — F3 (exact list equality) not met on the drain-stop arm.**
`tests/test_s0_01_frame_tee.py:700`: `assert status["write_errors"][0].startswith("drain a2c: stopped with ")`. Mutants **B2** and **A4** (swap `recorded`/`forwarded` in the a2c and c2a messages) SURVIVE in both trees — the numbers in the reason can be inverted undetected. (The direction inversion **B3** and the omission **B1** are killed; the forward arms' exactness is real — round-5 survivors V36/V37 are dead: **F1**, **F2** killed.)
**Fix:** compute the expected counts from the status and assert `== ["drain a2c: stopped with %d recorded, %d forwarded" % (rec, fwd)]`.

**R6-B5b-F9 [MED] SOLID — F10 is half closed: non-final status-write failures are silent, and the tee exits 0 when it cannot write its own status at all.**
`frame_tee.py:171-173` prints only `if final`. Measured (status + tmp both symlinked to `/dev/full`, 3 frames): **`tee exit code = 0`**, exactly **one** stderr line, no status file. A21 requires the file on every leg; the tee's exit code does not reflect its own evidence-write failure, and `test_status_write_failure_prints_stderr` (:1063) asserts only the stderr substring.
**Fix:** count suppressed failures and print once at exit; make an unwritable status a `write_errors` entry so the leg exits 70.

**R6-B5b-F10 [MED] SOLID — no `tee-status.json` exists before the first frame.**
Probe p12: 1 s after `runtime-identity.json` appears, the framedir holds `frames-*.jsonl`, `runtime-identity.json`, `timeline.jsonl` and **no** `tee-status.json` (the first write is inside the pump loops, :248/:324). Under A21d's own premise (the client SIGKILLs the group) a leg killed before its first frame yields no status → "present" fails. (Zero-frame *clean* legs are fine: empty input → 12 keys, all zeros.)
**Fix:** one `_write_status()` immediately after the identity write.

**R6-B5b-F11 [MED] mechanism SOLID / exploitation UNSURE — the SIGTERM handler can self-deadlock on the non-reentrant `status_lock`.**
`_sigterm_handler` (:345) → `_write_status` → `with status_lock` (:149), while the main thread calls `_write_status` from :375/:380/:394/:399/:419. Mechanism proven with a minimal repro (`lockrepro.py`): the process became **TERM-proof** — `timeout 12` could not kill it, it sat in `futex_do_wait` for 144 s until SIGKILL. Not reproduced in frame_tee (`sigterm_deadlock.py`, 12 trials with a 3 000-entry `write_errors` to widen the window: 0 hangs, all TERMs answered in 0.01 s) — the window is the duration of one status write. Consequence if hit: a tee that ignores `pc_post.sh:97`'s TERM (no KILL fallback there) and becomes an A20(c) survivor.
**Fix:** `signal.signal` sets a flag, or use an RLock, or write the TERM status without the lock via a separate temp name.

**R6-B5b-F12 [MED] SOLID — the lane's own `not_done` is the finding: no mutation pass was run, and 8 of my 43 mutants survive (7 genuinely).**
Every survivor is in the two areas the round-6 work was *for* (the c2a drain, the drain reasons, the status snapshot). B5b.md's "class sweep: … both pumps … both directional files; timeline; every exit path" is not supported by the tests: the timeline/directional cardinality (F7), the drain arm (F1, F8) and the lock (F5) are all ungated.

**R6-B5b-F13 [LOW] SOLID — dead code marking the F6 conflict.** `frame_tee.py:348-350`: `rc_val` is computed with the A21b normalisation and then discarded — `_write_status(..., agent_rc=agent_rc)` passes the raw value. pyflakes rc 0 does not catch unused locals.

**R6-B5b-F14 [LOW] SOLID (cost) / UNSURE (interaction) — the production shape now costs +5 s per leg.** p7 and p9: when the client holds stdin open (the production shape) the tee blocks the full `stall_timeout` in the c2a drain loop before exiting (p9 elapsed 6.1 s vs the round-5 test's `elapsed < 6` assertion). `docs/INCIDENT-LOG.md` (citing `crates/buzz-acp/src/acp.rs:417-442,:519`) says buzz-acp's shutdown kill wait is also **5 s** — I could not read that pinned source from the sandbox, so the interaction (the tee now near-certainly being SIGKILLed *inside* its drain, which is precisely when its status is torn per F5) is UNSURE and worth the coordinator's attention.

**R6-B5b-F15 [LOW] SOLID — A21d has no producer sample (AF-AP-42 class, still open).** The newest real leg `scratchpad/realleg/golden/run-1/` (11 frames: 3 c2a + 8 a2c, 2026-09-06 05:09:59Z) has `runtime-identity.json` + `timeline.jsonl` and **no `tee-status.json`**; its `tee_sha256 = ed1c38f1…` is the **round-5** tee, not `214b65e9…`. Every A21d expectation in the suite is graded against output the test itself just produced.

**R6-B5b-F16 [LOW] SOLID — the twelve-key set is duplicated three ways with no pin.** `frame_tee.py:152-165`, `tests/…:51-55 STATUS_KEYS`, `check_acp_conformance.py:103` (grep only — I did not read the A5c lane's file). `proofs/S0-01/pins.py` has no tee-status pin, so the A22/6-F24 "no local copy" rule is not applied to this artifact.

**R6-B5b-F17 [LOW] SOLID — after SIGKILL the directional file can hold one more frame than the timeline** (`df.write` precedes the timeline write): 5/20 killsnap legs. Timeline lines themselves are never torn (0/20 unparseable, 0/20 missing a trailing newline).

**R6-B5b-F18 [INFO] SOLID — "forwarded" means "written into the pipe", not "received".** In the F4 contended failure the tee reported `drained=True`, `write_errors=[]`, exit 0 while the agent had consumed 1 of 100 frames. The A21/A21d `forwarded == recorded` invariant cannot detect a loss that fits in the 64 KB pipe buffer; the tee docstring (:17-19) overstates it.

**R6-B5b-F19 [INFO] SOLID — the a2c pump has the same unhandled-`finally` traceback** (`frame_tee.py:326`, case D2: rc 70, 5 errors, `Exception in thread Thread-2 (pump_pipe)`); it does not hang because `close_dst` is False there. Confirms B5b.md's "adjacent" note that the tee's stderr and the agent's are mixed.

**R6-B5b-F20 [INFO] — premise shift**, see the header: `712fe01` edited a lane file mid-verify. All eight survivors were re-run against it and all eight still survive.

### Closures I reproduced as genuinely closed
F2 (a2c arm — p2 5/5 now `["drain c2a: stopped with 257 recorded, 256 forwarded"]`, was `errs=[]`), F3 on the forward arms (V36/V37 dead), F4 (handler present, gated by 5 mutants), F5 (p4: `["forward a2c: [Errno 28] No space left on device"]`, rc 70), F7 (p1/p1b rc 64, killed by G1/G3/G4), F8 (both previously flaky tests green in **both** contended runs), F9 semantics (p8 8/8 rc 70, all 5 000 frames recorded), F11, F12 (retitled honestly — 1 000 frames do fit the pipe buffer). Hostile inputs all clean: empty, bare `\n`, NUL byte, `NaN`, `1e999`, no trailing newline, CRLF-only, 8 MB line → rc 0, 12 keys, counters consistent, no hangs. `p5` and a 69-framedir sweep: **0** timeline-vs-status mismatches at rest.

## Mutant table (43 mutants; 34 killed, 8 survived + 1 equivalent)

| # | mutation | result | killed by |
|---|---|---|---|
|A1|delete the c2a drain loop|**SURVIVED**|— (68 passed, both trees)|
|A2|c2a stall timeout 5 s → 0 s|**SURVIVED**|—|
|A3|drop the `drain c2a: stopped` entry|**SURVIVED**|—|
|A4|swap the counts in the `drain c2a` message|**SURVIVED**|—|
|A5|c2a pump stops recording after a forward error|KILLED|test_agent_exits_without_consuming_stdin_exit_70 (**not** the F1 test)|
|A6|`drained` ignores c2a|**SURVIVED**|—|
|A3+A6|composed|**SURVIVED**|— (and p2 → rc 0 with a lost frame)|
|B1|drop the `drain a2c: stopped` entry|KILLED|test_never_reading_client|
|B2|swap the counts in the `drain a2c` message|**SURVIVED**|—|
|B3|`drain a2c` → `drain c2a` (direction inverted)|KILLED|test_never_reading_client|
|C1|no running status from pump_fd|KILLED|test_agent_exits_without_consuming…, test_late_client_frame…|
|C2|no running status from pump_pipe|KILLED|test_sigkill_leaves_nonfinal_status|
|C3|`final` always False|KILLED|7 tests|
|C4|exit fields set when not final|SURVIVED (**equivalent** — every non-final call site already passes None)|—|
|C5|`updated_seq` frozen at 0|KILLED|test_normal_run_writes_status +2|
|C6|`updated_seq` off by one|KILLED|test_normal_run_writes_status|
|C7|drop `updated_utc`|KILLED|test_status_keys_exact +3|
|C8|add a 13th key|KILLED|test_status_keys_exact, test_sigkill_leaves_nonfinal_status|
|C9|`drained` hard-coded true|KILLED|test_c2a_broken_pipe_is_write_error +2|
|D1 / D1b|non-atomic write (with / without an injected delay)|KILLED|test_rewrite_is_atomic|
|D2|unlink+rename instead of `os.replace`|KILLED|test_rewrite_is_atomic|
|D3|drop `status_lock`|**SURVIVED**|—|
|E1|SIGTERM handler not installed|KILLED|test_sigterm_writes_status_and_exits_70|
|E2|handler records no reason|KILLED|same|
|E3|handler exits 0|KILLED|same|
|E4|handler writes a non-final status|KILLED|same|
|E5|handler writes no status|KILLED|same|
|F1|BrokenPipe reason drops the direction (V36)|KILLED|test_c2a_broken_pipe_is_write_error +1|
|F2|BrokenPipe direction inverted, both pumps (V37)|KILLED|same|
|F3|forward-OSError arm removed|KILLED|test_forward_enospc_stdout_devfull|
|F4|directional reason drops the errno|KILLED|test_directional_enospc ×2|
|F5|timeline reason drops the seq|KILLED|test_write_failure_exit_70|
|F6|`forward_broken` latch removed (V16)|KILLED|test_agent_exits_without_consuming…|
|F7|status-write failure never printed|KILLED|test_status_write_failure_prints_stderr|
|G1|`lexists` → `exists`|KILLED|test_framedir_dangling_symlink|
|G2|empty-framedir check removed|KILLED|test_empty_framedir|
|G3|not-a-directory check removed|KILLED|+test_framedir_is_plain_file|
|G4|exit 64 → 1|KILLED|both framedir tests|
|H1|exit code ignores drained/write_errors|KILLED|8 tests|
|H2|exit decision ignores write_errors|KILLED|3 tests|
|H3|signal normalisation removed|KILLED|test_sigterm_agent_exit_143, test_signal_exit_status|
|H4|`stdin_reader_done` never set|KILLED|test_stdin_reader_done_true_on_clean_exit|

## Suite summaries (verbatim `pytest-summary:` lines)

At **80160ca** (the tree lane B5b delivered), scratch copy byte-identical to HEAD-at-the-time:
1. idle: `68 passed in 66.08s (0:01:06)` · 2. idle: `68 passed in 67.05s (0:01:07)`
3. contended (nice 19, 4 burners): `1 failed, 67 passed in 290.29s (0:04:50)` · 4. contended: `1 failed, 67 passed in 384.62s (0:06:24)` — both `test_agent_exits_without_consuming_stdin_exit_70`, `assert 0 == 70`.

At **7cd83c7** (current HEAD, after `712fe01`): idle `68 passed in 67.79s (0:01:07)` · idle `68 passed in 73.77s (0:01:13)`.
**Disclosed gap:** I have no *valid* contended run at HEAD. My first attempt died at 2 s (`pytest-exit: 143`, void); the second ran at idle speed (`68 passed in 68.29s`) because the burners were only getting ~34 % CPU each — the box had picked up the coordinator's `pytest proofs/ spikes/ tests/` plus four parallel `test_s0_01_check_acp_conformance.py` runs (load 14.4). I stopped adding load rather than risk false failures in the live A5c lane. F4 transfers regardless: `git diff 80160ca..HEAD` on the test file touches only the F1 test, so the failing test is byte-identical. Standalone at HEAD under the box's own load it passed 10/10 — the failure needs the full-suite load shape.
pyflakes on both files: **rc 0**. tmp_path hygiene: **PASS** (only `tests/__pycache__` appears in the run tree; all test artifacts under `/tmp/pytest-of-root`). Shared tree: my two files untouched.

## Rewrite-cost measurements (`cost.py`; shipped vs the same file with the two per-frame `_write_status()` calls removed)

| shape | shipped | no per-frame status | delta |
|---|---|---|---|
|11-frame real leg (10 frames, 7 trials)|median **0.058 s** (0.058-0.066)|median 0.060 s (0.057-0.062)|**none measurable**; ~10 rewrites of a 288-byte file|
|10 000 + 10 000 contention shape|**7.18 s**|2.01 s|**+5.17 s, 3.6×** for ~20 000 rewrites (~4 syscalls each)|
|3 000-frame leg with a failing timeline|status file **194 320 bytes**, rewritten per frame|—|O(n²) bytes — see F7|

Caveat: the box was contended by live coordinator lanes during part of the session; the two cost rows above were taken before that (`uptime` load ≈ 2).

## What I reproduced vs reviewed statically, and what I skipped

**Reproduced (ran it myself):** all four suite gates; 43 mutants each against the full 68-test suite (plus the 8 survivors re-run against the HEAD test file); probes p1/p1b/p1c/p2/p4/p5/p6/p7/p8 replayed from `vb5/probes.py`; p9 re-created (it was absent from that file — p3 and p9 are not in it) and run against pristine and mutant trees; new probes p10-p13, `hang.py` (5 cases + a round-5 comparison), `killsnap.py` (20 SIGKILL trials), `sigterm_deadlock.py` (12 trials), `lockrepro.py`, `f9probe.py` (idle 12, 4-burner 12, 8-burner 14, HEAD 10), an 8-case hostile-input battery, and a 69-framedir timeline-vs-status sweep.
**Static only:** the checker's side of A21d (lane A5c is live on `check_acp_conformance.py` — I read one grep line confirming the twelve-key comment exists and nothing else); `crates/buzz-acp/src/acp.rs` (on the PC, not readable here — F14's interaction is UNSURE and cited to the incident log, not verified).
**Deliberately skipped:** a contended suite run at HEAD (would have loaded the box while lane A5c ran its suites — see the disclosure above); `p1c` is meaningless in this sandbox (running as root bypasses the 0500 parent, rc 0).

**VERDICT: NOT-READY.** The lane's code changes are real and most of them are properly gated, but the finding the round existed for — R5-B5-F1 / audit P2 — is protected by no test at all (F1: mutant A1 survives and reproduces the audit's exact signature; the named closure test never went red for the mechanism), the round-5 test that carried that shape was deleted without disclosure (F2), an ENOSPC on the c2a evidence file hangs the tee forever (F3), the A21d running status fails its own contract in 15/20 production-shaped kills (F5), the SIGTERM status satisfies no A21d arm (F6), and the mandated contended gate is red 2/2 (F4). This verdict does not depend on anything I failed to reproduce, with one exception stated in-line: F14's buzz-acp-interaction half is UNSURE because the pinned Rust source is not readable from the sandbox.