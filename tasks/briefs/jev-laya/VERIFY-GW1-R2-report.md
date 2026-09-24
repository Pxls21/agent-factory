# VERIFY-GW1-R2 report: the second (last) repair of scripts/gpu_window.sh (D-031)

Status: COMPLETE. Gate recommendation: **MERGE-READY-WITH-FOLLOWUPS**. Verifier: sandbox, Opus 5.5.
Started 2026-09-24 22:21Z, finished 23:05Z.
Contract: unchanged, `tasks/briefs/jev-laya/VERIFY-GW1-brief.md`. Prior reports: `VERIFY-GW1-report.md`,
`VERIFY-GW1-R1-report.md` (R1-F-1 qualified this repair). D-031 is spent after this repair: what remains goes to the
follow-up issue (#74) or to the owner. The repair is cited by content: the commit "gpu_window: GW1-R2, the second repair
(D-031): INT and TERM ignored before every exit once the traps are armed; a GPU reading require...".

## 0. Premise re-measure (step 1)

Measured 2026-09-24 22:21-22:30Z at local HEAD:

```
70bda4dca641  scripts/gpu_window.sh      (HEAD blob = worktree hash-object; git status clean)
95e8897833e3  tests/test_gpu_window.py   (HEAD blob = worktree hash-object; git status clean)
pytest-summary: 31 passed in 73.04s (0:01:13)     (basetemp /tmp/gw2/bt1)
pytest-summary: 31 passed in 72.40s (0:01:12)     (basetemp /tmp/gw2/bt2)
1 files set=65a832bc5b21
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---
the 31 tests against the first repair 2d373812a9b9 (scratch tree): 7 failed, 24 passed in 179.67s (0:02:59)
```

ONE LINE DID NOT REPRODUCE: the premise says 8 failed, 23 passed against the first repair; my run gave 7 failed, 24
passed. The missing failure is `test_one_term_right_after_a_plain_exit_never_skips_the_restore[failed stop]` (the
20-trial watcher for R-3). That test alone, five more runs against the first-repair blob: failed, failed, failed,
**passed, passed**. So the line is a random count (7 or 8), not a changed world: the blob ids, both 31-passed runs, the
set id and the screen match exactly. I proceed, and I name it here because it is also the answer to the brief's
question on the watcher's 20 trials (section 4): against the regression it exists to catch, the failed-stop watcher
stayed green in 3 of 6 runs.

## 1. R-1, R-2, R-3 re-run on the new blob at the earlier trial counts (step 2)

Same harnesses (`sweep.py`, `exit1.py`, `exit1_stop.py`), natural timing, no hooks, the real script at 70bda4dca641:

| id | shape | first repair (2d373812a9b9) | second repair (70bda4dca641) |
|---|---|---|---|
| R-1 | a second TERM 2.5-6.5 ms after the first (0.05 ms steps, 3 passes) | 2 of 243 lost the start | **0 of 243** |
| R-2 | ONE TERM 0-300 us after the `gpu_busy` line | 25 of 150 | **0 of 150** (133 rc 1 `start, back`; 17 rc 130 `abort, start, back`) |
| R-3 | ONE TERM 0-300 us after the `stop rc 5` line | 13 of 150 | **0 of 150** (120 rc 1 `start, back`; 30 rc 130 `abort, start, back`) |

R1-F-1 is closed for the right reason: every post-arming exit now runs with INT and TERM ignored, so a late signal can
no longer re-run `abort` inside the EXIT trap. The outcomes where the TERM landed before the `exit 1` still restore
through the abort path (rc 130), and the ones after it are ignored (rc 1).

## 2. Attacks on the new code (step 3; harness `r2.py`, `orphan.py`, the real script at 70bda4dca641)

### 2a. Is any exit after arming still bare?

A listing of every `exit`, `leave` and `return` with its enclosing function and line (the traps arm at line 135):
- Before 135 (no EXIT trap yet, nothing stopped): the usage exits (64), the lock (5), the lane refusal (3), the three
  service and GPU refusals (4), the dry run (0).
- After 135: abort `leave 130` (133), the failed stop `leave 1` (142), the busy GPU `leave 1` (148), the normal end
  `leave "$worst"` (167), and `exit 6` inside `restore` (120), whose first line (109) ignores INT and TERM.
- Functions called after arming: `rec` (no exit), `gpu_used` (runs inside `$(...)`, a subshell), `models_answer` (only
  inside `restore`, `return` only), `restore`, `abort`, `leave`.
- Implicit exits: every variable read after arming is set, and the arithmetic runs on validated values; no `set -e`.
NO bare exit remains after arming. The limit of the repo's structural test is in section 4 (mutant X2).

### 2b. Can the pre-stop probe refuse wrongly? (the same text before and after the stop)

| probe output | result |
|---|---|
| two GPUs, two lines (`100` / `200`) | reads the first line; the window runs (the PC has one GPU) |
| `100 MiB` (a unit) / `[N/A]` / a warning line first / empty output | rc 4 "nvidia-smi gives no reading", record `refused: no GPU reading`, nothing stopped (fails closed) |
| `  100  ` / `100\r` | read as 100 |
| `0100` (zero-padded) | read and accepted; the `gpu_free` record line is invalid JSON (`"used_mib":0100`) |
| 20 digits | accepted before the stop; after it `[ -lt ]` errors ("integer expression expected"), never "free", rc 1, restored |
| the FIRST call takes 11 s (the service running), fast later | the probe is cut at 10 s: rc 4 after 10.0 s, nothing stopped (a false refusal that fails closed) |
| no `nvidia-smi` on PATH | rc 4, nothing stopped |

A real `nvidia-smi` that printed a warning line before the number (for example an infoROM warning) would make every
window refuse; whether it prints such lines on stdout for `--query-gpu` is UNVERIFIED here (no GPU).

### 2c. `leave` inside `abort` and a signal during `wait`

| shape (a TERM-ignoring job, kill-after 5 s or 3 s) | result |
|---|---|
| TERM, then TERM at +1 s, then INT at +2 s | one `abort` (TERM); rc 130 at 5.1 s (the grace); `abort, start, back`; the job dead |
| INT, then TERM at +1 s, then TERM at +2 s | one `abort` (INT); rc 130 at 5.1 s; `abort, start, back` |
| 1,418 alternating INT/TERM over the 3 s grace | one `abort`; rc 130 at 3.0 s; `abort, start, back` |

No bad interaction: once the handler has run, the later signals are ignored, `wait` is not interrupted, and the job
dies at its grace's end.

### 2d. The handler's ignore also keeps the JOB from being orphaned under a signal burst (new)

While the mutation audit ran, the H2 mutant (the TERM handler without its ignore) left jobs running after their
window had exited (`timeout --kill-after=3 3600 bash -c ... while :; do sleep 1; done`, parent pid 1). Each one held the
window lock through the inherited fd 9, so the burst test's next trial refused rc 5 and timed out ("timed out
waiting"). The record of each such trial reads `gpu_free, job (rc 143), abort x8-21, start, back`: the main loop's
`wait` returned 143, the main flow went on to `jobpid=""` and the `job` line, and the aborts ran after that with an
empty `jobpid`, so nobody sent TERM to the job (its `timeout` still had TERM caught, not ignored). The minimal bash
reproduction (a handler without `abort`'s nested `wait`) did not orphan anything in 160 trials once its detector waited
200 ms (my first minimal count of 3 and 2 was a detector race: the job had not died yet). So the trigger needs the
script's nested handlers, each with its own `wait`.

| script | dense burst, one per trial (a signal every ~50 us for 50 ms from the job's start) | orphaned jobs | `job` line before `abort` | start issued |
|---|---|---|---|---|
| H2 mutant (TERM handler without the ignore) | TERM, 60 trials | **3** | 3 | 60 of 60 |
| real blob 70bda4dca641 | TERM, 100 trials | **0** | 0 | 100 of 100 |
| real blob | INT, 60 trials | 0 | 0 | 60 of 60 |
| real blob | alternating INT/TERM, 60 trials | 0 | 0 | 60 of 60 |

So the handler-first ignore, added for AF-AP-145, also keeps `abort` from losing the job under a burst. The real blob
passes. Under a burst the real blob prints bash's benign `warning: run_pending_traps: bad value in trap_list[15]: 0x1`
to stderr (3 of 100 TERM bursts, 1 of 60 mixed): a signal that was pending when the handler switched to ignore.

### 2e. The pre-stop probe and the dry run

| dry run | result |
|---|---|
| normal | rc 0 in 0.1 s; the plan printed (it does not show the reading) |
| `nvidia-smi` fails (NVML mismatch text) | rc 4 in 0.1 s, record `refused: no GPU reading`, nothing stopped |
| `nvidia-smi` hangs | rc 4 after 10.1 s |

The dry run now also answers "would the real run pass the GPU check?", which keeps it a faithful rehearsal. Nothing in
the tests pins that (mutant X4 survives).

### 2f. Other checks

| check | result |
|---|---|
| F-2's hang moved to after the stop (my old S16 shape now trips the pre-stop probe first) | a TERM at +4 s, rc 130 at 10.1 s, `abort, start, back`. HOLDS |
| an error line after the stop | no reading, rc 1, no job ran. F-10 HOLDS closed |
| `GPU_JOB_KILL_AFTER` 0 / 00000 / 301 | rc 64; 1, 00300, 300 accepted. HOLDS |
| `GPU_FREE_WAIT_SECONDS` / `QWEN_BACK_SECONDS` 3601 | rc 64; 3600 and 0 accepted (the zero values are R1-F-3, in #74) |

## 3. Is 20 trials of the watcher enough? (the tests against the first repair, the regression they exist to catch)

| test | red runs against the first repair | reading |
|---|---|---|
| watcher `[gpu_busy]` (20 trials) | 6 of 6, plus the premise run | strong |
| watcher `[failed stop]` (20 trials) | **8 of 12** across all my runs (the premise run was green) | misses the regression about 1 run in 3 |
| burst (8 trials) | 5 of 6, plus the premise run | misses about 1 run in 6 |

My harness's per-trial loss on the first repair was 9% for the failed-stop shape; the test's watcher loses less per
trial (it re-reads the whole record on each poll), about 3-4% (0.965^20 is about 0.5). 20 trials is too few for that
shape: roughly 60 trials would bring the miss rate to about 5%. It matters less than it looks. The structural test
reds every exit-site and handler regression DETERMINISTICALLY (section 4: L1-L4, H1, H2, X1), so the watchers are
the behavioral second line, not the only line.

## 4. Mutation audit of the 31 tests (step 4; harness `mutr2.py`; one fresh scratch tree per mutant; 2 at a time)

| mutant | result |
|---|---|
| L1 abort's `leave 130` made a bare `exit 130` | 1 failed (structural): killed. Behaviorally equivalent: the handler already ignored INT/TERM |
| L2 the failed stop's `leave 1` made bare | 2 failed (the `[failed stop]` watcher, structural): killed |
| L3 the busy GPU's `leave 1` made bare | 2 failed (the `[gpu_busy]` watcher, structural): killed |
| L4 the normal end's `leave` made bare | 1 failed (structural): killed. Behaviorally equivalent (`restore` already ran and ignores INT/TERM) |
| H1 the INT handler without its ignore | 1 failed (structural): killed |
| H2 the TERM handler without its ignore | 2 failed (burst, structural): killed. The burst red came from orphaned jobs (section 2d) |
| P1 no pre-stop probe | 2 failed (the two pre-stop reading tests): killed |
| P2 the loose parse (`tr -dc 0-9`) again | 1 failed (error line after the stop): killed |
| K1 `GPU_JOB_KILL_AFTER=0` allowed | 1 failed (the seam test): killed |
| X1 `leave` without its ignore | 3 failed (both watchers, structural): killed |
| X2 an `exit 70` added inside `rec` (defined before `abort`, called after arming) | **31 passed: survives**. The structural test scans only lines after `abort() {`. No current defect: `rec` has no exit |
| X3 `restore` without its first-line ignore | 2 failed (signal-during-restore, structural): killed |
| X4 the pre-stop probe moved after the dry-run exit | **31 passed: survives**. No test checks that a dry run refuses on no reading |
| X5 the wait caps raised to 99999 | 1 failed (the seam test): killed |

## 5. Finding inventory for this round (no severity filter)

**R2-F-0 (closed).** R1-F-1 is closed for the right reason (section 1: 0 of 243, 0 of 150, 0 of 150); R1-F-6 and F-10
are closed (the pre-stop probe refuses with nothing stopped; an error line is no reading, before and after the stop);
R1-F-2 is closed (`GPU_JOB_KILL_AFTER` 1-300) and the wait seams are capped at 3600 s. No bare exit remains after arming
(section 2a).

**R2-F-1 INFO (positive, new mechanism).** The handlers' first-command ignore is load-bearing twice: besides AF-AP-145's
restore guarantee, it keeps a signal burst from orphaning the running job (the H2 mutant orphaned 3 of 60; the real blob
0 of 100 TERM, 0 of 60 INT, 0 of 60 mixed). REPRODUCED. The structural test pins the handler strings, so this cannot
regress silently.

**R2-F-2 FOLLOW-UP (tests).** Two surviving mutants. X2: an `exit` inside a function defined before `abort` but called
after arming (`rec`) is invisible to the structural test; widen it to every function body reachable after arming, or
forbid `exit` anywhere except `leave`, `usage` and the pre-arming refusals. X4: no test checks that a dry run refuses
on no GPU reading; add one.

**R2-F-3 FOLLOW-UP (tests).** The `[failed stop]` watcher (20 trials) misses its own regression about 1 run in 3 (8 red
of 12 against the first repair) and the burst test about 1 in 6 (5 of 6). The premise's "8 failed" is therefore a
random count: I measured 7 on the first full run. About 60 trials would bring the watcher near 5%; the deterministic
structural test already covers the class.

**R2-F-4 FOLLOW-UP (tests).** A test that fails against a broken build leaves the window's job running: the burst test
on H2 left six `timeout --kill-after=3 3600 ... while :; do sleep 1; done` jobs (parent pid 1, up to an hour), each
holding the window lock through fd 9, so the test's next trial refused rc 5 ("timed out waiting"). The tests' `finally`
kills only the window process. On the PC (`pc_suite.sh`), a red run against a broken build would leave such jobs behind.
Fix: in `finally`, kill the job's process group (the pid in `job.pid` and its parent `timeout`).

**R2-F-5 INFO.** Under a dense signal burst, bash prints `warning: run_pending_traps: bad value in trap_list[15]: 0x1`
to the window's stderr (3 of 100 TERM bursts): benign, a signal pending when the handler switched to ignore. It will
show in the LOG of a window that receives a burst.

**R2-F-6 INFO.** Pre-stop probe edges (section 2b): a unit, `[N/A]`, a warning line first, empty output, an absent
`nvidia-smi`, or a first call slower than 10 s make the window refuse (rc 4, nothing stopped); a zero-padded reading
writes an invalid JSON `gpu_free` line (F-9's class; `nvidia-smi` does not pad).

**R2-F-7 INFO.** The dry run now takes the GPU reading too, refuses on no reading with a record line, and can take
10 s when the probe hangs; its plan does not print the reading.

**Unchanged by this repair (in #74):** F-3, F-4, F-5, F-6, F-9, F-14, F-15, F-16, F-17, R1-F-3, R1-F-4, R1-F-7.

## 6. The blocking predicate, applied

No finding of this round meets it. R2-F-1 is a positive result. R2-F-2, R2-F-3 and R2-F-4 are test-quality gaps with
no production defect behind them (condition 3 fails: the code they would guard is correct today). R2-F-5, R2-F-6 and
R2-F-7 fail closed or are cosmetic (condition 3). The previous blocker, R1-F-1, is closed with a discriminator at the
earlier trial counts (section 1).

## 7. Gate recommendation

**MERGE-READY-WITH-FOLLOWUPS.** D-031 is spent; nothing here asks for a third repair.

What stands between this blob and the FIRST live window. These are preconditions of the run, not script defects:
1. A dry run ON THE PC with this blob (`bash scripts/gpu_window.sh --dry-run <jobs>`) must end rc 0. The new pre-stop
   probe is the one part I could not check against the real `nvidia-smi` output (no GPU here). An rc 4 "no GPU
   reading" there means the real output does not parse; the window would refuse and stop nothing, but it could not run.
2. Launch with the header's detached form `(setsid nohup bash scripts/gpu_window.sh --max-minutes 20 <jobs> > LOG 2>&1
   < /dev/null &)` (verified in VERIFY-GW1-R1: the caller returns at once, HUP is ignored).
3. The jobs file with LF endings, no BOM, and line 2's `<the PC's Laya snapshot>` placeholder replaced (F-16; the
   placeholder is a bash syntax error).
4. No lane live, and no lane dispatched until the record shows `back` (F-14: nothing enforces the second part).
5. Tell the owner the worst case for `--max-minutes 20`: about 20 min of jobs + 0.5 min grace + up to 3 min GPU wait +
   up to 20 min for `/v1/models` (vLLM's boot measured 5-15 min), about 43.5 min offline before the stop's own time.

What can follow (#74): R2-F-2, R2-F-3, R2-F-4 (tests), R2-F-5 to R2-F-7 (information), and the unchanged earlier list.

This recommendation rests on the sandbox shims. Not reproduced here: the real `nvidia-smi` output (item 1), real
systemd, and vLLM's real boot. Nothing ran on the PC.

## 8. What I reproduced, read, and skipped

- Reproduced on the real repaired script: the premise (and its random line), R-1/R-2/R-3 at the earlier counts, the exit
  listing, the pre-stop probe shapes, signals during abort's wait, the dry run, F-2 after the stop, the seam bounds,
  the orphan study (H2 against the real blob, 220 real-blob trials: 100 TERM, 60 INT, 60 mixed), the watchers' power (18 runs against the first
  repair), 14 mutants.
- Read, not run: the bash internals behind section 2d (the empirical discriminator stands without them).
- Skipped: the lane check and the leftover-process shapes (code untouched since VERIFY-GW1); the PC, the bridge and
  every real service (forbidden).
- Hygiene, stated plainly. My VERIFY-GW1-R1 sweep for leftover processes matched a few job shapes by name and missed one:
  the MB mutant's `timeout 2 bash -c trap "" TERM ...` job ran for 49 minutes, until this round found it. This round's
  H2 runs left six more (section 2d). All were killed by pid. The final sweep matches any process that names a shim
  dir, my scratch trees or the script, plus every `timeout` whose parent is pid 1, and it found none. The repo tree is
  unchanged except this report (blobs 70bda4dca641 and 95e8897833e3). Scratch:
  `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/gw1/` (`r2.py`, `orphan.py`, `mutr2.py`,
  `mut4/`, `mini/`) and `/tmp/gw2/`. Model: claude-opus-5-5 throughout; no refusal stop.
