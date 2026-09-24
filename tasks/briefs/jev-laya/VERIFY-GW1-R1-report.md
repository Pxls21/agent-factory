# VERIFY-GW1-R1 report: the one repair of scripts/gpu_window.sh (D-031), re-verified

Status: COMPLETE. Gate recommendation: **NOT-READY** (R1-F-1: F-1 not fully closed). Verifier: sandbox, Opus 5.5.
Started 2026-09-24 21:08Z, finished 22:09Z.
Contract: unchanged, `tasks/briefs/jev-laya/VERIFY-GW1-brief.md`. Prior report: `VERIFY-GW1-report.md` (F-1, F-2 blockers).
The repair is cited by content: the commit "gpu_window: GW1-R1, the one repair for VERIFY-GW1 F-1 and F-2 (signals
ignored while restoring; nvidia-smi bounded); F-7 and F-8 ride along (GATED-PENDING-VERIFY)".

## 0. Premise re-measure (step 1)

Measured 2026-09-24 21:08Z at local HEAD:

```
2d373812a9b9  scripts/gpu_window.sh      (HEAD blob = worktree hash-object; git status clean)
547042cb4488  tests/test_gpu_window.py   (HEAD blob = worktree hash-object; git status clean)
pytest-summary: 22 passed in 41.85s      (basetemp /tmp/gwr/bt1)
pytest-summary: 22 passed in 41.57s      (basetemp /tmp/gwr/bt2)
1 files set=65a832bc5b21
pre-repair blob a6ac010f69e3 + the new tests, scratch tree: 5 failed, 17 passed in 116.01s
  (the 5: signal-during-restore exits 6, second TERM during the abort's restore, hung nvidia-smi bounded,
   TERM-ignoring job killed after the grace, numbers decimal and seams checked before anything stops)
```

Every line matches the coordinator's premise. PREMISE HOLDS; the re-verify proceeds.

## 1. The F-1 and F-2 discriminators on the repaired blob (step 2)

Harness: the same `gwh.py` / `sig.py` / `s2b.py` / `race.py` as VERIFY-GW1, pointed at the repaired `scripts/gpu_window.sh`.

| id | shape | pre-repair (VERIFY-GW1) | repaired blob 2d373812a9b9 | right reason? |
|---|---|---|---|---|
| S2 | one TERM while the normal-path `restore` waits (8 s boot) | rc 130, no `back`, 503 at exit | rc 0 after 9.05 s; `start, back, close`; `/v1/models` 200 at exit | yes: the TERM is ignored, the wait completes |
| S3 | a second TERM during the abort's `restore` | rc 130, `abort, start, abort` | rc 130; `abort, start, back`; job dead | yes |
| S2b | a service that never returns; none / TERM / INT during the wait | 6 / **130** / **130** | 6 / **6** / **6**, each with `back ok:false` and "did not answer ... check it" | yes |
| MR1 | forced timing: TERM right before `systemctl --user start` | 0 starts, service stopped | 1 start, `start, back, close`, rc 0 | yes: `trap '' INT TERM` runs before `restored=1` |
| S16 | `nvidia-smi` hangs; `GPU_FREE_WAIT_SECONDS=2`; TERM at 8 s | still stopped at 18 s | rc 130, `abort, start, back`, service back by 18 s | yes: `timeout -k 2 10` ends the probe at 10 s, then the deferred TERM runs |
| MR2 | forced timing: TERM between the fork and `jobpid=$!` | job alive after exit | unchanged (job alive after exit) | not in this repair (F-15, follow-up) |

So the shapes VERIFY-GW1 reproduced for F-1 and F-2 are closed for the right reason.

## 2. F-1 is NOT fully closed: the EXIT-trap hand-off (coordinator measurement, reproduced independently)

Mechanism (AF-AP-145's class): every `exit` taken after the traps are armed hands control to the EXIT trap, and
`restore` ignores INT/TERM only from its FIRST line. A TERM or INT that lands between that `exit` and `restore`'s
first line runs the still-armed `abort` handler INSIDE the EXIT trap; its `exit 130` ends the shell; `restore` never
starts the service. Measured window (an instrumented scratch copy, timestamps only, 30 runs): abort's `exit 130` lands
3.0-19.8 ms after the first TERM (median 5.0 ms), and `restore`'s first line runs 115-160 us after it.

Natural timing, the real repaired script, no hooks (harness `sweep.py`, `exit1.py`, `exit1_stop.py`):

| id | shape | repaired blob | FIX-A (coordinator's shape) | FIX-B |
|---|---|---|---|---|
| R-1 | first TERM during a job, a SECOND TERM 0-12 ms later (0.25 ms steps, 4 passes) | 0 of 196 | not run | not run |
| R-1 | the same aimed at 2.5-6.5 ms (0.05 ms steps, 3 passes) | **2 of 243**: gaps 3.25 and 3.85 ms, rc 130, events `open, stop, gpu_free, abort, abort`, **no start, service stopped** | **0 of 243** | **0 of 243** |
| R-2 | ONE TERM 0-300 us after the `gpu_busy` line (the "GPU did not free" `exit 1`) | **25 of 150**: rc 130, `open, stop, gpu_busy, abort`, **no start, service stopped** | **22 of 150** (not closed) | **0 of 150** |
| R-3 | ONE TERM 0-300 us after the `stop rc 5` line (the "stop failed" `exit 1`) | **13 of 150**: rc 130, `open, stop, abort`, **the start was never issued** | not run (same code path as the repaired blob) | **0 of 150** |
| - | the 22 repo tests | 22 passed | 22 passed in 42.72s | 22 passed in 42.64s |

FIX-A = the coordinator's proposed second repair: `trap 'trap "" INT TERM; abort INT' INT` and the same for TERM.
FIX-B = FIX-A plus `trap '' INT TERM;` right before each of the two `exit 1` calls (the failed stop, line 124; the GPU
that did not free, line 131). Both on scratch copies; `bash -n` clean.

On the proposed shape: it is right but not sufficient. The handler-first ignore closes R-1 (a second signal across
the abort). R-2 and R-3 need no second signal at all: ONE TERM or INT in the ~130 us after either `exit 1` runs the
handler inside the EXIT trap, and the handler's own `exit 130` ends the shell, whether or not it ignores first. The
complete rule: ignore INT/TERM before EVERY `exit` taken after the traps are armed (the handlers, and both `exit 1`s);
`restore` keeps its first-line ignore for the normal-path call at line 148. A helper such as
`leave() { trap '' INT TERM; exit "$1"; }` for the post-arm exits is an equivalent form. `exit 6` (inside `restore`)
and the final `exit "$worst"` (after `restore`) already run with INT/TERM ignored.

## 3. Regression: the VERIFY-GW1 signal suite on the repaired blob

S1, S4, S5, S5b, S6, S7, S12, S13 and S14 give the same results as before the repair (every one restores; S5b
records the budget kill as rc 137; S7 records two `abort` lines; S14 still has no `stop` line, F-9). S9 (HUP under
`setsid nohup`) and S10 (QUIT) are still ignored. S8, S11 and S11b (HUP without nohup, USR1, ALRM) still restart the
service while the job lives (F-3, unchanged by this repair). The lane check (`ln.py`) and the job loop's leftover
behavior (`lo.py`) sit in code this repair did not touch (diff: header, argument checks, `restore`'s first line, the
probe, the kill-after); they were not re-run.

## 4. New shapes against the repair (step 3; harness `r1.py`, the real repaired script)

| id | shape | result |
|---|---|---|
| N1 | HUP / USR1 / ALRM while the normal-path `restore` waits (plain run) | the script dies by the signal (rc -1 / -10 / -14); record ends `start`, no `back`: the wait is abandoned (F-3's class; INT/TERM are ignored there now, these are not) |
| N1 | the documented launch `(setsid nohup bash SCRIPT ARGS > LOG 2>&1 < /dev/null &)` from a non-interactive caller, HUP during `restore` | the caller returned in 0.004 s; the window is a session leader (sid = pgid = pid); HUP ignored; record `start, back, close`; LOG empty. The header's launch form holds |
| N2 | `systemctl start` hangs 20 s inside `restore` | the hung child's SigIgn is 0x4006 (INT and TERM ignored, inherited from `restore`); a TERM to the script and a TERM to the child changed nothing; only KILL moved it (start rc 137, then `back ok:false`, rc 6) |
| N2b | a process-group TERM and INT while `restore` waits | nothing in the group died; rc 0, `start, back, close` |
| N4 | `--max-minutes` 0 / 00 / 0000 / 0241 | rc 64 each. HOLDS |
| N4 | `--max-minutes 000240` | 240 min. HOLDS |
| N4 | `--max-minutes 18446744073709551661` (2^64 + 45) | **accepted as 45 min** (bash arithmetic wraps); the pre-repair blob refused it (rc 64). 2^63, 2^32+45 and 400 nines are refused |
| N5 | each seam = '' / ' 5' / '5 ' / '+5' / an Arabic-Indic digit / '5\n' / '100000' | '' uses the default; every other shape rc 64 before anything. HOLDS |
| N5 | each seam = '00000' (zero) or '99999' | all accepted (except the budget's 99999, over 14400) |
| N5 | `GPU_WINDOW_MAX_SECONDS=0` | accepted; the service was STOPPED, both jobs `skipped: no time left`, restored, rc 1 |
| N5 | `GPU_JOB_KILL_AFTER=0`, a TERM-ignoring job, budget 2 s | `timeout --kill-after=0` sends no KILL: the job was still alive 25 s later with the service stopped; a TERM to the script started the abort, whose `wait` then never returned (still running 15 s later); only killing the job by pid ended it (rc 130, restored). **The seam is new in this repair** |
| N5 | `QWEN_BACK_SECONDS=0`, a 3 s boot | rc 6 after one probe; `/v1/models` answered 200 3 s later |
| N5 | `GPU_FREE_MIB=0` | never "free"; rc 1 after the wait; restored |
| N5 | `GPU_FREE_WAIT_SECONDS=99999`, GPU busy | still waiting at 15 s (27.8 h at most); a TERM restored it |
| N6 | a probe that ignores TERM and hangs | bounded: rc 1 at 12.1 s (10 s + `-k 2`) |
| N6 | a probe that leaves a detached helper holding its stdout | **30.1 s**, the helper's life: `timeout` bounds its process group, not the pipe the command substitution reads |
| N6 | a slow probe (11 s) that would answer | killed at 10 s, never read; rc 1 at 10.2 s (safe) |
| N7 | `nvidia-smi` fails before any job (driver/library version mismatch text) | the service was stopped first, the probe failed after (`gpu_busy used "?"`), rc 1 after the wait, restored. Nothing probes the GPU BEFORE the stop |

## 5. Mutation audit of the 22 tests (step 4; harness `mut2.py`; one fresh scratch tree per mutant; 2 at a time)

| mutant | result |
|---|---|
| MT1 drop `trap '' INT TERM` in `restore` | 2 failed (signal-during-restore exits 6; second TERM during the abort's restore): killed |
| MT2 drop the `timeout` on `nvidia-smi` | 1 failed (hung nvidia-smi): killed |
| MT2b keep `timeout 10`, drop only `-k 2` | **22 passed: survives**. Its effect: a probe that ignores TERM held the window 40.1 s (its own life) instead of 12 s |
| MT3a drop `10#` on `--max-minutes` / MT3b drop the whole decimal line | 1 failed each: killed |
| MT3c drop `10#` on the budget seam | **22 passed: survives** (no leading-zero seam is tested; `010` would be 8 s, `08` an error before the lock) |
| MT3d drop `10#` on the wait and kill-after seams | **22 passed: survives** (same) |
| MT4a-e drop each seam from the check loop in turn | 1 failed each (5 of 5): killed |
| MT6 no budget cap / MT7 seam length 9 | 1 failed each: killed |
| MT9 `restore` ignores TERM only | 1 failed: killed (the test sends TERM, then INT) |
| MT10 the ignore moved after `restored=1` | **22 passed: survives** (MR1's order; forced timing only, not testable deterministically) |
| MT11 kill-after hard-wired to 30 / MT12 GPU wait hard-wired to 180 | 1 and 2 failed: killed |
| MA no INT trap / MB no kill-after / ME no `--noproxy` (VERIFY-GW1 survivors) | 1 failed each: killed |
| MC abort does not wait for the job (VERIFY-GW1 survivor) | **22 passed: survives**. Cause: the TERM-ignoring test's abort half asserts `"job-dead-at-start" in _calls(win)`, which the FIRST half's line already satisfies (calls.log is not reset). With the assertion on the LAST start line, the test passes on the repaired script (1 passed) and fails on MC (1 failed) |
| MD drop `< /dev/null` (VERIFY-GW1 survivor) | 22 passed: an EQUIVALENT mutant (bash gives an asynchronous list `/dev/null` as stdin when job control is off). Correction to VERIFY-GW1 F-11, which counted it as a test gap |
| T1 the shim's zombie check reverted to `kill -0` | 1 failed (TERM-ignoring job): the `/proc/<pid>/stat` check is load-bearing in this container (timeout's group KILL leaves a zombie that `kill -0` calls alive) |

## 6. Finding inventory for this round (no severity filter)

Evidence levels as in VERIFY-GW1. Line numbers are the repaired `scripts/gpu_window.sh` (blob 2d373812a9b9).

**R1-F-1 BLOCKER. F-1 is not fully closed: a signal in the EXIT-trap hand-off still skips the start.** REPRODUCED in
natural timing (section 2). Any `exit` taken after the traps are armed (abort's `exit 130`, line 115; the failed
stop's `exit 1`, line 124; the busy GPU's `exit 1`, line 131) hands over to the EXIT trap while INT and TERM are still
armed; `restore` ignores them only from its first line (94). A TERM or INT in the ~115-160 us between reruns `abort`
inside the EXIT trap, and its `exit 130` ends the shell before `systemctl start`. Shapes: R-1, a second TERM across the
abort (2 of 243; the coordinator 1 of 49); R-2, ONE TERM after the busy-GPU `exit 1` (25 of 150); R-3, ONE TERM after
the failed-stop `exit 1` (13 of 150, the start never issued). Each ends rc 130, the exit code the header documents as
"the service back". Class: AF-AP-145. Fix: FIX-B (section 2): 0 of 243, 0 of 150, 0 of 150; 22 of 22; the section 7
regression clean.

**R1-F-2 FOLLOW-UP (introduced by this repair). `GPU_JOB_KILL_AFTER=0` passes the seam check and disables the KILL.**
REPRODUCED (N5): a TERM-ignoring job outlived its budget, and a TERM could not end the window (abort's `wait` never
returned) until the job was killed by hand. Seam-only on the PC. Fix: require `KILL_AFTER >= 1` (and cap it).

**R1-F-3 FOLLOW-UP. Other seam values that pass but stop the service for nothing.** REPRODUCED (N5):
`GPU_WINDOW_MAX_SECONDS=0` (stop, every job skipped), `GPU_FREE_MIB=0` (never free), `QWEN_BACK_SECONDS=0` (rc 6 during
a normal boot), and 99999 for the waits (27.8 h). Seam-only. Fix: lower bounds of 1 and upper bounds on the waits,
checked with the others before the lock.

**R1-F-4 INFO (introduced by this repair). `10#` arithmetic wraps:** `--max-minutes 18446744073709551661` is accepted
as 45 min; the old `[ -ge ]` check refused it. Not material. Fix: refuse more than three significant digits.

**R1-F-5 FOLLOW-UP (tests).** Survivors: MT2b (`-k 2` untested: a TERM-ignoring probe holds the window for its whole
life), MC (the abort half's vacuous membership assertion; the strict form kills MC), MT3c/MT3d (leading-zero seams
untested), MT10 (forced timing only). MD is equivalent (not a gap; corrects VERIFY-GW1 F-11).

**R1-F-6 FOLLOW-UP (new; pre-existing, not introduced by the repair). No GPU probe BEFORE the stop.** REPRODUCED on
the script side (N7): with `nvidia-smi` failing, the window stops the service, finds the GPU unreadable afterwards,
waits `GPU_FREE_WAIT_SECONDS`, and restarts. INFERRED consequence on the PC, UNVERIFIED here: the usual cause of that
failure (an NVIDIA driver update without a reboot, "Driver/library version mismatch") also stops a NEW vLLM process
from starting, while the running one keeps serving, so the window would turn a working service into a dead one until
a reboot. The script already uses `/v1/models` as the positive control before the stop; the GPU probe has none. Fix:
one `timeout -k 2 10 nvidia-smi ...` before the stop that must return a number (refuse rc 4 otherwise). Recommended
before the first live window.

**R1-F-7 FOLLOW-UP / UNVERIFIED. The probe bound covers timeout's process group, not the pipe.** REPRODUCED (N6): a
detached helper holding the probe's stdout stretched the 10 s bound to 30.1 s. A probe stuck in the kernel (D state, a
common shape of a wedged driver) cannot be killed at all; not reproducible here. Fix: run the probe into a temp file in
the background and poll it with a deadline, abandoning a probe that does not finish.

**R1-F-8 INFO. HUP, USR1 and ALRM during `restore` still abandon the wait** (N1; F-3's class, unchanged). The
documented launch makes HUP ignored (verified, N1); USR1 and ALRM have no sender.

**R1-F-9 INFO (by design). `restore`'s ignore is inherited by its children** (N2: SigIgn 0x4006 on a hung
`systemctl start`; only KILL moves it; a group TERM+INT changes nothing). The real service is spawned by the systemd
user manager, not by the script, so it does not inherit the ignore (STATIC).

**R1-F-10 INFO. `timeout -k 2 10` costs at most 12 s per probe** in the GPU wait and in a deferred TERM; a probe slower
than 10 s is never read (rc 1 after the wait: safe, a wasted window).

**R1-F-11 INFO (positive).** F-1's reproduced shapes (S2, S3, S2b, MR1) and F-2's (S16) are closed for the right
reason; F-7 (decimal) and F-8 (seam garbage) are closed; the header's launch form, the 30 s grace and "exit 6 also
after a signal" hold; 22 passed twice; the new tests fail 5 of 22 on the pre-repair blob; VERIFY-GW1's survivors MA, MB
and ME are now killed.

## 7. The blocking predicate, applied

| finding | 1 contract | 2 canonical path | 3 material | 4 discriminator | 5 in boundary | verdict |
|---|---|---|---|---|---|---|
| R1-F-1 EXIT-trap hand-off | yes: item 2 ("after a failed stop, a GPU that never frees, and INT or TERM") and exit table lines 17-18 | yes: natural timing, the real repaired script, no hooks (R-1 2/243; R-2 25/150; R-3 13/150) | yes: the start is never issued, the service stays down, rc 130 claims it is back | yes: FIX-B 0/243, 0/150, 0/150 on the same harnesses; FIX-A leaves R-2 at 22/150 | yes | **BLOCKER** |
| R1-F-2 kill-after 0 | item 3 | yes | no: a test seam nobody sets on the PC | yes | yes | FOLLOW-UP |
| R1-F-3 seam values | items 2, 3 | yes | no: seams only | yes | yes | FOLLOW-UP |
| R1-F-6 no GPU pre-probe | none of items 1-4 | script side yes; PC consequence UNVERIFIED | UNVERIFIED | partial | yes | FOLLOW-UP |
| R1-F-7 probe bound | item 2 | detached helper yes; D state no | exotic / UNVERIFIED | partial | yes | FOLLOW-UP |

D-031: R1-F-1 is F-1's class, which this repair set out to close and did not, so it qualifies for the one further
repair ("a blocker that this repair introduced or failed to close").

## 8. Gate recommendation

**NOT-READY** on R1-F-1 alone. Every other finding is a follow-up or information. The trigger windows are narrow
(about 130 us), but they are reproduced in natural timing on the real script, and their effect is the one the window
exists to prevent: the owner's service left stopped, with an exit code that says it is back.

The second repair, keyed to blob 2d373812a9b9 and the unchanged contract. The coordinator's shape (FIX-A, the
handler's first command ignores INT/TERM) is right but NOT sufficient: it closes R-1 (0 of 243) but leaves R-2 at 22 of
150, because the handler's own `exit 130` still ends the shell inside the EXIT trap. The sufficient rule: INT and TERM
are ignored before EVERY `exit` taken after the traps are armed. Concretely (FIX-B, verified):
1. `trap 'trap "" INT TERM; abort INT' INT` and `trap 'trap "" INT TERM; abort TERM' TERM`;
2. `trap '' INT TERM;` right before the `exit 1` of the failed stop (line 124) and of the busy GPU (line 131), or one
   `leave() { trap '' INT TERM; exit "$1"; }` used for every exit after the arming;
3. `restore` keeps its first-line ignore (the normal-path call at line 148 is not inside a handler).
Tests: a deterministic structural test (every `exit` after the arming line runs with INT/TERM ignored: the handler
strings start with the ignore, and no bare `exit` follows the arming), plus a statistical smoke that cannot be red on a
fixed script: a watcher that sends one TERM right after the `gpu_busy` line (and after `stop rc 5`), about 30 trials,
none may lose the start (on the repaired blob the per-trial loss rate was 17% and 9%). The coordinator's dense burst
across the abort covers R-1. Cheap ride-alongs: R1-F-2 (`KILL_AFTER >= 1`), R1-F-3 (lower bounds), R1-F-6 (a GPU probe
before the stop), and the strict last-line assertion for MC (R1-F-5).

## 9. What I reproduced, read, and skipped

- Reproduced through the real repaired script: the premise (3 runs), S2, S3, S2b, MR0-MR2, S16, the regression suite,
  N1-N7, the three R shapes, 24 mutants plus the strict-assertion and no-`-k` checks, and FIX-A/FIX-B on scratch copies.
- Measured with an instrumented scratch copy (timestamps only): the exit-to-`restore` window (115-160 us, 3-20 ms after
  the first TERM).
- Tried and discarded: a DEBUG-hook timeline. Inside trap handlers bash keeps `BASH_COMMAND` at the interrupted command
  and the hook stops logging inside the EXIT-trap `restore`, so it cannot target this window.
- Read, not run: real systemd's signal reset for services (R1-F-9), the D-state probe (R1-F-7), vLLM under an NVML
  mismatch (R1-F-6).
- Skipped: the lane check and the leftover shapes (code the repair did not touch); the PC, the bridge and every real
  service (forbidden).
- The repo tree was not changed except this report; the pinned blobs still hash 2d373812a9b9 and 547042cb4488. All
  processes I started were killed by pid; a final sweep found none. Scratch:
  `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/gw1/` (harnesses, `mut2/`, `mut3/`,
  `inst/`) and `/tmp/gwr/` (basetemps). Model: claude-opus-5-5 throughout; no refusal stop.
