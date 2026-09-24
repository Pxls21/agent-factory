# VERIFY-GW1 report: the guarded GPU window (scripts/gpu_window.sh), independent adversarial verify

Status: COMPLETE. Gate recommendation: **NOT-READY** (F-1, F-2). Verifier: sandbox, Opus 5.5.
Started 2026-09-24 20:08Z, finished 20:52Z.

## 0. Premise re-measure (brief step 1)

Measured 2026-09-24 20:08:37Z at local HEAD c08eeb9 (the brief's own commit):

```
a6ac010f69e3 scripts/gpu_window.sh
62b4de1912d1 tests/test_gpu_window.py
0591a08306f8 docs/research/findings/j2b-variants/rwkv7_g0.py
(worktree hash-object: the same three values; git status clean on all three)
pytest-summary: 14 passed in 10.57s
1 files set=65a832bc5b21
```

All three blob ids, the pass count and the set id match the brief's PREMISE block. Result: PREMISE HOLDS; the
verify proceeds. (`pc_suite.sh set-id` is a local sha256 of the path strings, `scripts/pc_suite.sh:46`; it calls no
bridge.)

## 1. Method and boundary

- Harness: `gwh.py` in the session scratchpad (not in the repo). Shims on PATH for `systemctl` and `nvidia-smi` (state
  files stand in for the unit and the GPU), an argv-logging wrapper that `exec`s the REAL curl, and a loopback HTTP
  server for `/v1/models` that answers 200 only while the unit is "active" and the bearer matches. Extra seams over the
  repo tests: a stop/start delay, a start rc, a readiness delay after start (models vLLM's boot), a hanging
  `nvidia-smi`, verbatim `nvidia-smi` text, and a "GPU holder" pid (a leftover process that keeps the GPU busy).
- The script is run unmodified from `scripts/gpu_window.sh` (blob a6ac010f69e3). Mutants run on fresh scratch copies.
- No bridge call, no PC, no real service. The key is the FAKE string `FAKE-gw1-key-0000-not-a-secret`.
- A `/proc` sampler reads every process's `cmdline` and `environ` for the key while a window runs.
  Instrument check (this matters): my FIRST positive control was hollow. It "hit" only because my own tool shell and
  `sed` carried the key in their argv. After excluding the harness's ancestors and masking inside Python, a child that
  holds the key in argv was caught 478 times, and one that holds it in environ 1,009 times. Only then was the real
  window's zero count admissible.

## 2. Reproduced results, in the order run

- A0 (harness sanity): the success path gives rc 0 and `open, stop, gpu_free, job, job, start, back, close`, the same
  sequence the repo test asserts. The harness is sound.
- A1 (contract 4, the key): a window with a 6 s service boot (4 curl calls): 0 key hits in 11,141 `/proc` samples of
  every process's cmdline and environ; the key is in no file under the run dir except the key file; curl's argv holds
  `-H @/dev/fd/63`. CONTRACT 4 HOLDS on argv, environ, logs and record.
- A1x: `bash -x scripts/gpu_window.sh ...` (an operator tracing it) prints
  `++ printf 'Authorization: Bearer %s\n' <key>` to stderr. That is operator-induced, outside the contract's shapes.

### Signals (harness `sig.py`; real script, sanctioned shims; each line reproduced as written)

| id | shape | result |
|---|---|---|
| S1 | TERM during the GPU-free wait (GPU busy) | rc 130 after 2.07 s; `open, stop, abort, start, back`; service back. HOLDS |
| S2 | ONE TERM while `restore` waits for `/v1/models` on the NORMAL path (jobs done, service boot 8 s) | rc 130 after 4.03 s; record `..., job, start, abort`: NO `back`, NO `close`; `/v1/models` answered **503** when the script exited. The header documents 130 as "stopped by INT or TERM (the service back)" |
| S3 | a SECOND TERM while the abort's `restore` waits (boot 8 s) | rc 130, 4.0 s after the 2nd TERM; record `..., abort, start, abort`: NO `back` |
| S4 | TERM while a TERM-ignoring job (`trap '' TERM`) runs in budget | rc 130 after **30.05 s** (timeout's `--kill-after=30` armed by abort's TERM); restore done |
| S5 | TERM during a job's kill-after grace (budget 2 s already spent) | rc 130 22.09 s after the TERM (the rest of the grace); restore done |
| S5b | budget expires on a TERM-ignoring job (no signal) | rc 1 after 32.1 s; the job is recorded **rc 137**, not 124; job 2 `skipped: no time left` |
| S6 | INT during a job | rc 130 after 0.06 s; `abort` signal INT; job dead; service back. HOLDS |
| S7 | two TERMs 2 s apart, TERM-ignoring job | two `abort` lines, rc 130 at 30.07 s, restore done. HOLDS |
| S8 | HUP, plain run (no nohup) | script killed by HUP in 0.06 s; the EXIT trap ran `start, back` **while the job was still alive**; no `abort` line |
| S9 | HUP under `setsid nohup` | ignored (still running 12 s later, job alive); a later TERM restores. The planned invocation is protected |
| S10 | QUIT | ignored by bash ("in all cases, Bash ignores SIGQUIT"); the window continues; a later TERM restores |
| S11 / S11b | USR1 / ALRM | as S8: killed, the EXIT trap restarts the service **while the job lives** |
| S12 | stderr is a pipe with no reader; a failure path writes to it (GPU never frees) | killed by SIGPIPE (rc -13) but the EXIT trap restored (`gpu_busy, start, back`) |
| S13 | SIGKILL during a job | service stays down (documented). The job holds fd 9 on `state/lock` (inherited): a new window refuses **rc 5 "another window holds"** while the job lives, and that refusal is **not recorded**; after the job ends, rc 4 "not active" |
| S14 | TERM during a 3 s `systemctl stop` | deferred until the stop returns, then rc 130; the record is `open, abort, start, back`: the executed stop has **no `stop` line** |
| S16 | `nvidia-smi` hangs after the stop; `GPU_FREE_WAIT_SECONDS=2` | still running at 8 s (the 2 s limit is never checked); TERM at 8 s: still running at 18 s with the service **stopped** (the trap waits behind the foreground `nvidia-smi`); only killing `nvidia-smi` by pid let it abort and restore (rc 130) |

### Leftover processes (harness `lo.py`)

| id | job shape | result |
|---|---|---|
| L1 | `sleep 300 &` (same process group) | window rc 0, full record ending `close rc 0`; the child is **alive after the window**, holds fd 9 on `state/lock`; the next window refuses **rc 5 "another window holds"** |
| L2 | `setsid sleep 300 &` | same as L1 |
| L3 | `nohup sleep 300 >/dev/null 2>&1 &` | same as L1 |
| L4 | double fork `( ( sleep 300 & ) & )` | same as L1 |
| L5 | a `setsid` leftover that holds the GPU; the modeled vLLM cannot start while it lives | job rc 0, `start`, `back ok:false`, rc 6 ("did not answer ... within 4s"; 20 min at the default). The record holds **no GPU reading after the jobs** and nothing about the leftover |
| L6 | budget expiry with a `setsid` child and a same-group child | timeout's group kill takes the same-group child; the `setsid` child **survives** |
| L7 | TERM (abort) with the same two children | same as L6 |

The planned jobs (`rwkv7_g0.py`, `scripts/laya_ft/train.py`) spawn no subprocesses, DataLoader workers or signal handlers
(grep for subprocess/Popen/multiprocessing/num_workers/fork/setsid/daemon/signal/os.system: no hit).

### Lane check (harness `ln.py`)

| shape | result |
|---|---|
| live lane pid owned by ANOTHER uid (root), window run as `nobody` (`kill -0` gets EPERM) | **rc 0, the service was STOPPED** (full window) |
| control: live lane pid owned by the SAME uid, window as `nobody` | rc 3 refused, nothing stopped |
| hidden lane dir `.lanes/.x/lane.pid` (live pid) | rc 0, stopped (the glob `*` skips dot-dirs) |
| `lane.pid` a dangling symlink / a directory / a FIFO | rc 0, stopped (`[ -f ]` skips them) |
| `AF_REPO` does not exist | rc 0, stopped (no lanes seen) |
| `lane.pid` = "P\n9" (P live) | rc 0, stopped (`tr -d [:space:]` makes "P9", a dead pid) |
| `lane.pid` = 99999999999999999999 or 4294967297 | rc 0, stopped (read as a dead pid, not as "no pid") |
| `.lanes` or a lane dir is a symlink to a live lane | rc 3 refused |
| empty file, "0", "-1" | rc 3 "(no pid in it)" |
| live pid with CRLF; a zombie pid | rc 3 refused |
| 5,000 dead lanes / 5,000 with one live | 14.5 s, rc 0 / 14.3 s, rc 3 |

Writer check (`harness-ports/bin/pc-lane.sh:89,110-111`): a lane writes `echo $$ > lane.pid` (one pid, truncate then
write: the empty moment reads as live, by design) and removes it on EXIT. So two-pid files are not produced by the writer.

### Signal follow-up: a service that never comes back (harness `s2b.py`)

| signal during `restore`'s wait (`never-back`, `QWEN_BACK_SECONDS=12`) | rc | record tail | stderr |
|---|---|---|---|
| none | **6** | `start, back(ok:false)` | "did not answer ... check it" |
| TERM | **130** | `start, abort` (no `back`) | empty |
| INT | **130** | `start, abort` (no `back`) | empty |

The header documents rc 130 as "stopped by INT or TERM (the service back)". With one TERM or INT the script reports
the opposite of the truth and drops the failure it would otherwise report.

### Lock, state dir, jobs files, budget, seams, restore, record (harness `misc.py`)

| id | shape | result |
|---|---|---|
| K1 | two windows started together | rc 0 and rc 5; one stop only; the rc 5 refusal writes **no record line** |
| K2 | state dir not writable (run as `nobody`) | `exec 9>` fails, `flock: 9: Bad file descriptor`, then the misleading "another window holds ... lock", rc 5; nothing stopped |
| K3 | `record.jsonl` cannot be written (it is a directory); the lock can | rc 0: **the whole stop, jobs, start cycle ran with NO record** (7 stderr lines "Is a directory") |
| J | CRLF jobs file | job 1 prints `a\r`; job 2 creates a file literally named `out-b\r`; `$'true\r'` rc 127 |
| J | space-only and tab-only lines | filtered; 1 job. HOLDS |
| J | a 200 KB line | `timeout: Argument list too long`, rc 126; service back |
| J | a job that reads stdin | EOF at once (`rc=1 got=[]`). HOLDS |
| J | a job that prints 20 MB | 20,000,000-byte log; fine |
| J | `cd /; export LEAK=1; X=2`, then a second job | the second job sees the start dir and `leak=unset x=unset`. HOLDS (no leak) |
| J | a NUL byte in the jobs file | grep "binary file matches", 0 jobs, rc 64, nothing stopped |
| J | a UTF-8 BOM | `﻿echo: command not found`, rc 127 |
| J | the planned line 2 with its placeholder `<the PC's Laya snapshot>` | rc 2: `unexpected EOF while looking for matching '` (the apostrophe in "PC's") |
| B | `--max-minutes 1` / `240` | `timeout --kill-after=30 60` / `14400`. HOLDS |
| B | `--max-minutes 010` / `045` | `timeout ... 480` / `2220` (read as octal: 8 and 37 minutes); the `open` line is **invalid JSON** (`"max_minutes":010`) |
| B | `--max-minutes 08` | passes the 1-240 check, **stops the service**, waits for the GPU, then `value too great for base` and `n: unbound variable`; no job ran; restored; rc 1 |
| B | `GPU_WINDOW_MAX_SECONDS` = `10s` / `abc` / `a[$(touch X)]` | each ends the window AFTER the stop with no job run (rc 1, restored); the command substitution did not run (set -u stopped at `a`) |
| B | `GPU_WINDOW_MAX_SECONDS=-5` | every job `skipped: no time left`, rc 1 |
| B | `GPU_WINDOW_MAX_SECONDS=999999999` | `timeout --kill-after=30 999999999`: **the 1-240 minute cap is bypassed** |
| B | `GPU_FREE_WAIT_SECONDS=3m`, GPU busy | **never ends** (still running at 12 s: `[ -ge "3m" ]` errors, the if is false); a TERM restored it |
| B | `QWEN_BACK_SECONDS=20m`, never back | the restore wait never ends; a TERM ends it as rc 130 with no `back` (same as S2b) |
| B | `GPU_FREE_MIB=1.5G` | never "free", rc 1, restored (fails safe) |
| R1 | `systemctl start` rc 1, never back | `start rc 1`, "still waiting", rc 6. HOLDS |
| R2 | `systemctl start` rc 1 but the service answers | `back ok:true`, rc 0. HOLDS |
| R3 | the key file rotated mid-window and the service reads the new one | back, rc 0 (the probe re-reads the file each call). HOLDS |
| R4 | the key file rotated but the service keeps the old key | rc 6 "did not answer": the service is up; the message does not mention the key |
| RC1 | `GPU_WINDOW_DIR` holds a `"` | the `job` line (`"log":"..."`) is invalid JSON |
| RC2 | `nvidia-smi` prints `Unable to determine the device handle for GPU0000:01:00.0: Unknown Error` | `tr -dc 0-9` gives `000001000` = 1000 < 1500: **"GPU free"**, the job ran, and the `gpu_free` line is invalid JSON |
| RC2 | `[N/A]` / `No devices were found` | `gpu_busy used_mib "?"`, rc 1, restored. HOLDS |
| RC2 | `  1024  ` / `1,024` | 1024. HOLDS |

### Forced-timing races (harness `race.py`; the script file is not modified)

bash's own `BASH_ENV` hook installs a DEBUG trap (functrace on) that sends ONE TERM right before a named command. This
is a timing harness: it shows what the code does if a signal lands in that gap. In natural timing each gap is
microseconds wide.

| id | TERM lands right before | result |
|---|---|---|
| MR0 (control) | `wait "$jobpid"` (the designed abort path) | rc 130, job killed, `abort, start, back` |
| MR1 | `systemctl --user start "$UNIT"` (after `restored=1`) | rc 130, **0 start calls, the service stays STOPPED**; record ends `job, abort` |
| MR2 | `jobpid=$!` (after the fork) | rc 130, `abort, start, back`, **the job is alive after the script exits** (abort saw an empty jobpid) |

### Mutation audit of `tests/test_gpu_window.py` (harness `mut.py`; one fresh scratch tree per mutant)

| mutant | result |
|---|---|
| MA: delete `trap 'abort INT' INT` | **14 passed (survives)**. Its effect (S6 on MA): INT kills the script (rc -2), the EXIT trap restarts the service, **the job lives** |
| MB: drop `--kill-after=30` | **14 passed (survives)**. Its effect (S5b on MB): the budget never ends a TERM-ignoring job; my 45 s harness cap fired |
| MC: abort does not `wait` for the job | **14 passed (survives)**. Its effect (S4 on MC): rc 130 in 0.06 s, the service restarts **while the job lives** |
| MD: drop `< /dev/null` | 14 passed (survives) |
| ME: drop `--noproxy '*'` | 14 passed (survives; no `http_proxy` here) |
| MF2: disable the lock | 1 failed (`test_a_held_lock_refuses`): killed |
| M3 re-derived: no EXIT trap | 3 failed: killed (the commit says 3) |
| M5 re-derived: job in the foreground | 3 failed: killed (the commit says 3) |
| M6 re-derived: key in argv | 1 failed: killed (the commit says 1) |
| M1 re-derived: lane refusal skipped | 2 failed: killed (the commit says 2) |

The four re-derived author mutants die with the stated counts. Five properties the contract names have no test.

### Discriminators: candidate fixes on scratch copies

| fix (one change each) | the 14 tests | the defect it targets |
|---|---|---|
| `restore()` starts with `trap '' INT TERM` | 14 passed | S2: waits, `start, back, close`, `/v1/models` 200 at exit, rc 0. S3: `abort, start, back`, rc 130. MR1: start issued, service active |
| `timeout 10 nvidia-smi ...` | 14 passed | S16: restored by 18 s (unfixed: still stopped at 18 s) |
| `{ kill -0 "$p" 2>/dev/null \|\| [ -e "/proc/$p" ]; }` | 14 passed | EPERM: rc 3 refused (unfixed: rc 0, stopped) |

Unfixed control re-run in the same session: S2 rc 130 with `start, abort`; S3 rc 130 with `start, abort`. Deterministic.

### Gate runs

```
$ python3 -m pytest tests/test_gpu_window.py -q -p no:cacheprovider --basetemp /tmp/gw1/bt-final1   (then bt-final2)
14 passed in 9.61s     rc=0
14 passed in 9.65s     rc=0
```

### The planned first window (static reading plus one local measurement)

- `setsid` without `-f` forks only when its caller leads a process group. Measured here from a non-interactive
  caller: `bash -c 'setsid nohup sleep 3 ...; echo'` blocked the caller 3.01 s; with `setsid -f`, 0.006 s. So the
  planned line `setsid nohup bash scripts/gpu_window.sh --max-minutes 45 ...` (no `-f`, no `&`, no redirection) does
  not detach when a script or the bridge runs it. `PC-BRIDGE.md:38-50` requires
  `setsid bash <guard.sh> > /tmp/<job>.log 2>&1 < /dev/null &` and "NEVER hold an HTTP call open past ~2 min"; `pc.sh`
  re-runs a command that outlives its call (AF-AP-92), and each re-run would refuse rc 5, unrecorded. The script header
  (line 6, "Start it DETACHED (setsid nohup)") gives the same incomplete advice. Launched from a terminal, nohup writes
  `nohup.out` into the current directory (the PC clone).
- Line 2's placeholder must be replaced before the run (the apostrophe makes it a syntax error, row J above).
- The owner's words (chat 2026-09-24, `transcripts/sandbox/chat-2026-09-24.md:4067`): "it will only be offline for a
  few mins". The planned `--max-minutes 45` allows about 45 min of jobs + 0.5 min kill-after + up to 3 min GPU wait +
  up to 20 min restore wait, about 68 minutes offline in the worst case, before the stop's own time.

## 3. Finding inventory (no severity filter)

Evidence levels: REPRODUCED (the real script at blob a6ac010f69e3, sanctioned shims, natural timing), FORCED-TIMING
(the real script, a signal placed by bash's DEBUG hook), MEASURED (a local measurement outside the script), STATIC
(read, not run), UNVERIFIED (needs the PC, the real driver or vLLM). Line numbers are `scripts/gpu_window.sh`.

**F-1 BLOCKER. INT or TERM during `restore` ends the script without the verified restore, and rc 130 then claims
"the service back".** Evidence: REPRODUCED (S2, S3, S2b), FORCED-TIMING (MR1). `abort` (96-100) calls `exit 130`
even while `restore` (78-94) runs, and `restore` sets `restored=1` (80) before its work, so the EXIT trap's second
`restore` returns at once. One TERM or INT during the restore wait (vLLM's boot, about 5-15 min per
`docs/research/findings/VLLM-MIGRATION.md:37,84`) exits 130 within 5 s: no `back` line, no warning; with a service
that never returns, rc 130 replaces rc 6 (S2b). With forced timing, a TERM between `restored=1` and the start skips the
start for good (MR1: 0 starts, service stopped). Contract: item 2 ("ALWAYS started again and `/v1/models` is waited
for ... after INT or TERM") and the exit table (line 12). Canonical path: yes (S2/S2b are natural timing). Material:
the exit code and the record claim or imply a restored service that is not verified, and the service is left
unwatched in its most fragile phase. Discriminator: `sig.py S2 S3`, `s2b.py`; the fix below turns them green.
Fix (verified on a scratch copy, 14/14 green): make `restore` immune to INT/TERM as its first command
(`trap '' INT TERM`, or a trap that only records a late signal). Also fix header lines 7 and 12.

**F-2 BLOCKER. `nvidia-smi` runs with no time bound while the service is stopped (line 111).** Evidence: REPRODUCED
through the `nvidia-smi` shim (S16); the hang itself is UNVERIFIED on the real driver. A probe that never returns keeps
the service stopped with no limit: the `GPU_FREE_WAIT_SECONDS` check (113) is never reached, and INT/TERM wait behind
the foreground probe (still stopped 10 s after TERM). The only way out is SIGKILL, which (per the header) skips the
restore. Contract: item 2 ("a GPU that never frees" and "INT or TERM"). Canonical path: the real script; the shim is
the same boundary the repo's own "GPU never frees" test uses. Material: the owner's service stays down without bound,
and the documented abort does not work. Trigger: a driver or GPU fault, or a slow teardown (rare). Discriminator:
`sig.py S16`. Fix (verified with `timeout 10`, 14/14 green, S16 restored by 18 s): `timeout -k 2 10 nvidia-smi ...`
(`-k` because a probe that ignores TERM would hold `timeout` too; a probe stuck in the kernel still cannot be killed).

**F-3 FOLLOW-UP. Catchable signals other than INT/TERM restart the service while the job still holds the GPU.**
REPRODUCED: HUP without nohup (S8), USR1 (S11), ALRM (S11b): bash runs the EXIT trap for them (an EXIT trap makes a
non-interactive bash catch its terminating signals), so `restore` starts the service, but `abort` never ran and the
job lives on under its own budget. Not reachable in the documented launch: `setsid nohup` makes HUP ignored (S9);
bash ignores QUIT (S10); SIGPIPE hits only failure paths with no job running (S12 restored). Contract: none of items
1-4 names these signals (the header's "only SIGKILL skips the restart" stays true). Fix: `trap 'abort HUP' HUP` and the
same for USR1, USR2, ALRM, PIPE, XCPU, XFSZ, VTALRM.

**F-4 FOLLOW-UP. A job's leftover processes outlive the window, the budget does not bound them, and the record does
not show them.** REPRODUCED (L1-L7): on the normal path any leftover survives (same-group child, `setsid`, `nohup &`,
double fork); on budget expiry and abort a `setsid` child survives. The record still ends `close rc 0`. A leftover that
holds the GPU makes the restore end rc 6 with no GPU reading after the jobs (L5; 20 min at the default). Leftovers
inherit fd 9, hold the lock, and make the next window refuse rc 5 "another window holds" (unrecorded). Contract: item
3 in substance ("one shared time budget bounds all jobs"). Not material for the planned window: the planned jobs start
no subprocesses (grep, section 2). Fix: after each job, kill timeout's process group (`kill -KILL -- -$jobpid`;
catches same-group leftovers); read `nvidia-smi` before `restore` and record it (refuse or warn on a busy GPU); run
jobs with fd 9 closed (`9>&-`); a `systemd-run --user --scope` per job would catch `setsid` too.

**F-5 FOLLOW-UP. EPERM reads a live lane as dead (line 52).** REPRODUCED as `nobody`: a live root-owned lane pid, rc 0,
**the service was stopped**; same-user control rc 3. Contract: item 1 literally ("a live pid"), and the commit's own
stated reason for rejecting `qwen-server.sh guard` ("reads an unreadable pid as stale"). Not material on the PC: lanes
and the window run as the same user, so an EPERM pid there is a recycled pid of a dead lane. Fix (verified, 14/14
green, EPERM refused rc 3): `{ kill -0 "$p" 2>/dev/null || [ -e "/proc/$p" ]; }`.

**F-6 FOLLOW-UP. Other lane shapes read as "no lane".** REPRODUCED: a hidden lane dir (`.lanes/.x`), a `lane.pid`
that is a dangling symlink, a directory or a FIFO, a missing `AF_REPO`, two pids in one file (`tr -d '[:space:]'`
joins them), a pid above pid_max. The writer (`harness-ports/bin/pc-lane.sh:85-111`) makes none of these; a wrong
`AF_REPO` or HOME is the plausible one. Fix: refuse unless `$AF_REPO/.git` exists (as `pc-lane.sh:73` does); treat any
non-regular `lane.pid`, a multi-token file, or a pid beyond `/proc/sys/kernel/pid_max` as live.

**F-7 FOLLOW-UP. A leading-zero `--max-minutes` passes validation (26-27).** REPRODUCED: `010` gives 480 s and `045`
gives 2,220 s (bash arithmetic reads them as octal), and the `open` line is invalid JSON; `08` passes, stops the
service, then dies on `value too great for base` after the GPU wait: no job ran, one needless restart of the owner's
service, rc 1. Class: AF-AP-197 (a precondition found invalid only after the step it protects). Fix: normalize with
`MAX_MIN=$((10#$MAX_MIN))` after the digit check, or reject a leading zero.

**F-8 FOLLOW-UP. The test seams are unvalidated and evaluated as bash arithmetic after the stop.** REPRODUCED:
`GPU_WINDOW_MAX_SECONDS=999999999` bypasses the 1-240 minute cap; `10s`/`abc` end the window after the stop with no
job; `-5` skips every job; `GPU_FREE_WAIT_SECONDS=3m` makes a busy-GPU wait endless (a TERM rescued it);
`QWEN_BACK_SECONDS=20m` makes the restore wait endless. `GPU_FREE_MIB` garbage fails safe. On the PC these apply only
if someone exports them. Fix: validate each as digits before taking the lock, or honor them only under a test flag.

**F-9 FOLLOW-UP. Record gaps.** REPRODUCED: (a) the lock refusal (rc 5) writes no line (K1, S13, L1); (b) a TERM
during a slow stop drops the `stop` line although the stop ran (S14); (c) an unwritable `record.jsonl` does not stop
the window: a full stop/jobs/start cycle ran with no record (K3; AF-AP-197 class); (d) invalid JSON lines from a `"`
in the state path (RC1), a leading-zero `max_minutes` (F-7) and a zero-padded `used_mib` (F-10). Contract: none of
items 1-4 (the commit says "one JSON line per step"). Fix: check the record is writable before the stop; record the
lock refusal (one appended line needs no lock); write the stop intent before `systemctl stop`; build lines with a
JSON encoder or escape strings.

**F-10 FOLLOW-UP / UNVERIFIED. `tr -dc 0-9` takes digits from any first line (line 111).** REPRODUCED with shim text:
`Unable to determine the device handle for GPU0000:01:00.0: Unknown Error` becomes 1000 MiB, so the GPU reads as
"free", the jobs run, and the `gpu_free` line is invalid JSON. UNVERIFIED: whether the real `nvidia-smi --query-gpu`
prints such a line on stdout (no GPU here). Fix: accept only a first line that matches `^[0-9]+$`.

**F-11 FOLLOW-UP. Test gaps (five surviving mutants).** REPRODUCED: no INT test (MA: without the INT trap, INT
restarts the service under a live job); no TERM-ignoring job (MB: without `--kill-after`, the budget never ends it;
MC: an abort that does not wait restarts the service under a live job); no stdin test (MD); no proxy test (ME). The
repair for F-1 and F-2 should add: INT during a job; a second TERM during `restore`; a TERM during the normal-path
restore wait; a hung `nvidia-smi`; a TERM-ignoring job (budget and abort); and "job dead BEFORE `systemctl start`"
by the order in `calls.log`.

**F-12 INFO. "Stops the running job at once" is up to 30 s for a job that ignores TERM.** REPRODUCED (S4: 30.05 s;
S5: the rest of the grace). A budget kill of such a job is recorded rc 137, not 124 (S5b). Document it.

**F-13 FOLLOW-UP (escalation: the planned launch, outside the script).** MEASURED plus STATIC: plain `setsid`
does not detach from a non-interactive caller (3.01 s blocked vs 0.006 s with `setsid -f`). The planned line has no
`-f`, no `&`, no redirection; the runbook (`PC-BRIDGE.md:38-50`) requires `setsid ... > log 2>&1 < /dev/null &`.
Through the bridge the call would be held past the ~120 s cap and `pc.sh` would re-run it (AF-AP-92); the re-runs
refuse rc 5, unrecorded. What the bridge server does to the held process at its cap is UNVERIFIED (its source is not
in this repo); if it sent SIGKILL to that pid, the service would stay down. Also: the header line 6 gives the same
incomplete advice; line 2's placeholder is a syntax error if left (rc 2); the owner said "only offline for a few
mins", and the worst case of the planned `--max-minutes 45` is about 68 minutes offline (section 2). Fix: launch as
`setsid -f bash scripts/gpu_window.sh --max-minutes N <jobs> > ~/gpu-window/run.log 2>&1 < /dev/null`; correct line 6;
state the worst-case downtime to the owner or cut the budget.

**F-14 FOLLOW-UP (escalation, outside the script). Nothing stops a lane launch during the window.** STATIC: no
reference to the window or its lock in `scripts/pc_lane.sh` or `harness-ports/bin/pc-lane.sh`; the script checks lanes
once, up to about 5 s (the pre-check curl's cap) before the stop. Fix: the dispatcher refuses while
`~/gpu-window/lock` is held (`flock -n`), or the coordinator's discipline.

**F-15 FOLLOW-UP (forced timing only). The job is forked before `jobpid` is set (125-126).** FORCED-TIMING (MR2): a
TERM in that gap leaves the job running under a restarted service. Natural gap: microseconds. Fix: let `abort` fall
back to `$!` when `jobpid` is empty during a spawn (a flag set just before the fork), or block the traps across the
fork and re-deliver a pending signal after `jobpid=$!`.

**F-16 INFO. CRLF and BOM jobs files corrupt job argv** (REPRODUCED: a file named `out-b\r`; `$'true\r'` rc 127;
`﻿echo` rc 127). The service is restored. Fix: refuse a jobs file with `\r` or a BOM before the stop.

**F-17 INFO. An unwritable state dir gives the wrong message** (K2: "another window holds ... lock" after `Permission
denied`). Fails closed. `exec 9>` also truncates the lock file each run (harmless).

**F-18 INFO. `bash -x` prints the key to stderr** (A1x). Operator-induced; `models_answer` could drop xtrace locally.

**F-19 INFO. The restore check proves "something answers 200 with the key", not that `qwen` answers.** STATIC: the
documented fallback `qwen-builder` serves the same port, key and names (`deploy/qwen.container:12-13`). And R4
(REPRODUCED): a key rotated in the file but not in the service gives rc 6 "did not answer" with no hint about the key.

**F-20 UNVERIFIED. Is 200 on `/v1/models` enough for vLLM 0.28?** vLLM's server binds HTTP after the engine is
built, so 200 should mean ready; not verifiable here. `BACK_S=1200` covers the measured 5-15 min boot.

**F-21 INFO (static). bash `SECONDS` follows the wall clock**, so a clock step during a window moves the budget
and every wait. Not run (changing the sandbox clock is unsafe).

**F-22 INFO (positive, REPRODUCED or verified from source).** Contract 4 holds (A1: 0 hits in 11,141 samples with a
de-vacuoused sampler; curl sees `@/dev/fd/63`; the key is in no log or record). Contract 1 holds for every same-user
shape tested (symlinked `.lanes` and lane dirs, empty/0/-1/CRLF/zombie pids, 5,000 lanes). The lock serializes two
windows (K1, one stop). INT/TERM during a job or the GPU wait restore (S1, S4-S7). A closed stderr still restores
(S12). The defaults match `deploy/qwen.container` (port 8080, key file, unit `qwen`). Idle VRAM was measured at
246 MiB (`docs/research/FINDINGS-LOCAL-BUILDER-QWEN38.md:73`), well under `GPU_FREE_MIB=1500`. The retired
`qwen-builder` pending watcher cannot fire during a window (`harness-ports/bin/qwen-server.sh:322-334`: its idle test
needs `llamacpp:requests_processing 0` from `:8080/metrics`, which fails while the port is dead).

**F-23 INFO. After a SIGKILL (documented), the job keeps the lock through fd 9 until it ends** (S13): "flock is
released with the process" holds only once every process that inherited fd 9 has exited.

**F-24 INFO. The lane check forks one `tr` per lane** (5,000 lanes: 14.5 s).

**F-25 INFO (static). Jobs inherit fd 9**: a job that ran `flock -u 9` would release the window's lock.

**F-26 INFO (static). The lane check misses a Hermes process orphaned by a SIGKILLed runner** (`lane.pid` holds the
runner's pid). Conformant to the contract's definition of "live".

## 4. The blocking predicate, applied

| finding | 1 contract | 2 canonical path | 3 material | 4 discriminator | 5 in boundary | verdict |
|---|---|---|---|---|---|---|
| F-1 signal during `restore` | yes: item 2 + exit table line 12 | yes: S2, S2b in natural timing | yes: rc 130 "service back" while it is not; no `back`; MR1 no start | yes: S2/S3/S2b; the fix turns them green | yes | **BLOCKER** |
| F-2 unbounded `nvidia-smi` | yes: item 2 ("GPU never frees", "INT or TERM") | yes: real script, the shim boundary the repo tests use | yes: service stopped without bound; TERM ineffective | yes: S16; the fix restores by 18 s | yes | **BLOCKER** |
| F-3 other signals | no: items name INT/TERM only | yes | no: documented launch ignores HUP | yes | yes | FOLLOW-UP |
| F-4 leftovers | item 3 in substance | yes | no: the planned jobs start no subprocesses | yes | yes | FOLLOW-UP |
| F-5 EPERM | yes: item 1 literally | yes (as `nobody`) | no: same-user lanes on the PC | yes | yes | FOLLOW-UP |
| F-7 leading zeros | usage table, item 3 | yes | no: hypothetical input; octal only shortens | yes | yes | FOLLOW-UP |
| F-9(c) no record | no: not in items 1-4 | yes | evidence lost, but only in a broken environment | yes | yes | FOLLOW-UP |
| F-13 launch line | the brief's planned use | measured locally; bridge part UNVERIFIED | UNVERIFIED | partial | no: the launch, not the script | escalation |

No finding needed the CONTRACT-DEFECT route: F-1's false rc 130 already maps to the frozen contract.

## 5. Gate recommendation

**NOT-READY.** F-1 and F-2 meet the whole blocking predicate. F-1 is pure bash trap semantics, reproduced in natural
timing (S2, S3, S2b) with a forced-timing extension (MR1). F-2's trigger (a real `nvidia-smi` that never returns) is
modeled through the sanctioned shim: I did not reproduce a real driver hang. Nothing ran on the PC.

Suggested ONE focused repair, keyed to `scripts/gpu_window.sh` blob a6ac010f69e3 and the brief's frozen contract:
1. `restore()`: ignore (or only record) INT/TERM as its first command. Verified on a scratch copy: 14/14 green; S2
   waits and ends `back, close`; S3 ends `abort, start, back`; MR1 starts the service.
2. Line 111: `timeout -k 2 10 nvidia-smi ...`. Verified with `timeout 10`: 14/14 green; S16 restored by 18 s.
3. Header lines 6, 7 and 12, and the commit's "at once", corrected (F-12, F-13).
4. Tests: INT during a job; one TERM during the normal-path restore wait with a service that never returns (expect
   rc 6, not 130); a second TERM during the abort's restore; a hung `nvidia-smi`; a TERM-ignoring job (budget and
   abort); the job dead before `systemctl start`.

Cheap in-boundary follow-ups that could ride in the same repair (not needed for readiness): F-5 (one line, verified),
F-7, F-9(a)(c), F-10, F-3. Escalations for the coordinator before the first live window: F-13 (launch with
`setsid -f ... > log 2>&1 < /dev/null`, replace line 2's placeholder, state the worst-case downtime to the owner or
cut the budget) and F-14 (the lane dispatcher does not know about the window).

## 6. What I reproduced, what I read, what I skipped

- Reproduced through the real script: A0-A1, S1-S16, S2b, L1-L7, the lane shapes and EPERM, K1-K3, the jobs-file
  shapes, B, R1-R4, RC1-RC2, MR0-MR2 (forced timing), 10 mutants and 3 fixes, and two fresh gate runs.
- Read, not run: the bridge server's behavior at its cap (source not in the repo), F-14, F-19, F-20, F-21, F-25,
  F-26, and the vLLM readiness semantics.
- Skipped on purpose: the PC, the bridge and every real service (forbidden by the brief); the jobs' internals beyond a
  grep for process spawning and signals (they are inputs, not the component); SIGSTOP/SIGCONT (operator action); a
  clock step (unsafe in the sandbox); the code-intel quartet (one standalone bash file; a repo-wide literal grep finds
  no caller, only docs and the probe's docstring).
- Harness honesty: my first key-sampler control was hollow (it matched my own tool's argv); fixed and re-controlled
  before any key claim. My cleanup in the MC run orphaned one TERM-ignoring `sleep`, and the capped MB run left its
  processes: all killed by pid, a final sweep found none. The repo tree was not changed except this report. Scratch:
  `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/gw1/` (harnesses, runs, mutants) and
  `/tmp/gw1/` (short basetemps, the `nobody` runs, the EPERM-fix copy).
- Model: every turn of this verify ran on claude-opus-5-5; no refusal stop.
