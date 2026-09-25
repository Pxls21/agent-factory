# SBS1 report: the side-by-side GPU window job (task #262; D-088)

Lane: SBS1 build (sandbox, Opus 5.5). Brief: `tasks/briefs/jev-pipes/SBS1-brief.md`. PIN 6ee9322; local head at start
91a173b (the brief's own commit, a descendant of the PIN); local head at close 4b5b1bb (the coordinator's and the P1
lane's commits; the three premise files show 0 diff lines against the PIN there, and none of my paths is in them).

STATUS (2026-09-25 08:4xZ): BUILT AND GATED IN THE SANDBOX; NOT RUN ON THE GPU. Four files created, nothing else
modified, no git writes. Tests `105 passed` twice on set `2c5776d02fd6`; the brief's five mutants all killed, plus 16
extra mutants all killed. The GPU phases and the real container were not run (no GPU, no podman, no bridge here): the
coordinator runs the window. **Read section 7 before the window: the premise's own numbers say the second
configuration (0.92, C=2048) does not fit beside Qwen, and the first (0.90, C=4096) fits by about 62 MiB before
allocator overhead.**

## 1. Premise re-measured (evidence demand 1)

Sandbox half, re-measured this session at local head 91a173b:

```
$ git show 6ee9322:<file> | sha256sum | cut -c1-16      and the working tree
9f44e29c479dfbfd  scripts/gpu_window.sh                                (PIN and working tree: equal)
7583bf5f3281a9a4  docs/research/findings/j2b-variants/rwkv7_g0.py      (PIN and working tree: equal)
da7deec82c3d6850  deploy/qwen.container                                (PIN and working tree: equal)
$ git diff 6ee9322 HEAD -- <the three files> | wc -l
0
$ grep -n 'timeout --kill-after' scripts/gpu_window.sh
159:  timeout --kill-after="$KILL_AFTER" "$left" bash -c "$c" > "$log" 2>&1 < /dev/null &   # in the background, so a signal
$ grep -n "^def load\|^def real_text_ids\|^class Scorer\|^    def forward\|^SNAPSHOT" .../rwkv7_g0.py
43:SNAPSHOT = Path(os.path.expanduser(
83:class Scorer:
90:    def forward(self, ids, cache=None):
135:def load(rec, args):
152:def real_text_ids(tok, n):
$ grep -n "Image=\|Exec=\|PublishPort\|Volume=\|Environment=\|PodmanArgs" deploy/qwen.container
21-32: identical to the brief's block, line for line
```

PC half (the live unit read on the PC, the image's start script, the running server's log lines, the G0 window run): NOT
re-measured here. No PC bridge in this lane (standing rule). Tier: ASSUMED from the brief. The G0 numbers are backed by the
committed `docs/research/findings/j2b-variants/rwkv7-g0/2026-09-24-window2/g0.json`, which I read (it matches the brief).

Verdict: the premise re-measures. No CONTRACT-INVALID.

## 2. Seams read before code (verified this session)

| seam | where | what it means for SBS1 |
|---|---|---|
| job signals | `scripts/gpu_window.sh:159` (plain `timeout --kill-after=30 ... bash -c`) | plain `timeout` makes its OWN process group (measured: its pgid = its pid; `--foreground` keeps the caller's). The runner's TERM and, 30 s later, KILL go to that whole group. So every inner `timeout` in the job is `--foreground`, the pattern `tasks/briefs/jev-laya/window1.jobs` already states. |
| key header | `scripts/gpu_window.sh:84-88` `models_answer` | reused verbatim: `-H @<(printf 'Authorization: Bearer %s\n' "$(cat "$KEY_FILE")")`, `--noproxy '*'` |
| bash on TERM | measured: an untrapped TERM still runs the EXIT trap, then bash dies of the signal (a `wait` in bash reads 143; Popen reads -15, section 5) | the "TERM trap removed" mutant is caught by the exit code and the summary's reason, not by the cleanup |
| background jobs | measured: a non-interactive shell's `&` child has SigIgn 0x6 (INT and QUIT ignored) | the cleanup TERMs the reader itself; an orphaned reader would hold GPU memory the restored service needs |
| G0 | `rwkv7_g0.py:83-96,119-159` | `phase_env`, `load`, `real_text_ids`, `Scorer.forward` (`logits_to_keep=1`) imported, not copied; torch only inside functions. The G0 question is an inline literal in `phase_ladder` (no constant): the probe repeats the literal and a test pins it to that AST node of G0. |
| unit | `deploy/qwen.container:19-32` | `ContainerName=qwen`, `Image=` digest, `Exec=batch`, `PublishPort=8080:8080`, 3 volumes (key mount `:ro` at `/app/api_key.txt`), 5 environment lines, `PodmanArgs=--ipc=host --device nvidia.com/gpu=all`. |
| G0 window2 | `.../2026-09-24-window2/window-record.jsonl`, `g0.json` | GPU used with Qwen stopped: 255 MiB. torch total 24,122 MiB, free 23,606 MiB at G0 start (so G0's own CUDA context ~261 MiB). Steady forward ~50k tokens/s (61,440 in 1.174 s). |
| findings | `VLLM-RWKV-2026-09-25.md` (The PC section) | "The Qwen vLLM holds 24,022 of 24,576 MiB" (nvidia-smi, util 0.972). |

## 3. What was built (the four files; nothing else touched)

| file | what it does |
|---|---|
| `scripts/gpu_side_by_side.sh` | one configuration: usage (64), window check (3), unit parse and digest check (3), `podman run` of the temporary server, boot wait on `/v1/models`, sizing from `podman logs qwen`, the probe, `summary.json`; cleanup once on every exit path after the start |
| `docs/research/findings/jev-pipes/rwkv_sbs_probe.py` | the reader probe: `alone`, `qwen_idle_rwkv`, `together`, each written as it completes; torch only inside functions; G0 imported |
| `tests/test_gpu_side_by_side.py` | the job at the system boundary (PATH shims, real curl, loopback `/v1/models`, fake probe on the seam) and the probe's harness (fake engine, loopback chat server) |
| `docs/research/findings/jev-pipes/sbs-window.jobs` | the brief's two configurations, each under `timeout --foreground -k 40 1200`, each writing under `~/gpu-window/` |

Where each contract line lives (all four files are new and untracked; line numbers at the report's close):

- `scripts/gpu_side_by_side.sh:75` `podman container exists qwen` and `:70` `gpu_used`: the window check (exit 3)
- `scripts/gpu_side_by_side.sh:86` `unit="$(python3`: the unit parse (to `:175`); `:179` `sha256`: the digest check
- `scripts/gpu_side_by_side.sh:185` `models_answer`: the key header through a process substitution
- `scripts/gpu_side_by_side.sh:195` `cleanup`: once, INT and TERM ignored, the reader stopped, the bounded removal
- `scripts/gpu_side_by_side.sh:209` `summary`: `summary.json` and the final rc; `:254` `leave`, `:255` `finish`
- `scripts/gpu_side_by_side.sh:265` `on_signal TERM`: the TERM trap; `:271` `podman run`: the temporary server
- `scripts/gpu_side_by_side.sh:277` `until models_answer`: the boot wait; `:285` `qwen-boot.log`: the sizing parse
- `scripts/gpu_side_by_side.sh:340` `"$PROBE"`: the probe run; `:346` `finish 0`
- `docs/research/findings/jev-pipes/rwkv_sbs_probe.py:91` `read`, `:115` `questions`, `:130` `chunk_check`
- `docs/research/findings/jev-pipes/rwkv_sbs_probe.py:140` `smi_apps`, `:202` `chat_load`, `:193` `scrubber`
- `docs/research/findings/jev-pipes/rwkv_sbs_probe.py:262` `phase_together`, `:305` `run_phases`, `:347` `main`

Design choices beyond the letter of the contract (each one is a place the coordinator may veto; none changes what the
contract asks for):

- **`together` keeps RWKV working until the load ends (DESIGN INTERPRETATION, flagged).** Pass 1 is "the alone read and
  questions again", recorded in full. While the load still runs, further passes (each summarized) keep RWKV busy, so
  Qwen's aggregate is measured "while RWKV works". Reason: G0 measured about 50k tokens/s, so one 16,384-token read plus
  five questions takes about 0.5 s, while 4 x 512 tokens of Qwen load takes seconds. With one pass, Qwen's number would
  be almost entirely RWKV-idle time. The record carries `overlap` (load and RWKV intervals, `load_fraction_with_rwkv`,
  `first_pass_inside_load`), so coverage is checkable, not assumed.
- **Extra refusals (exit 3, nothing started), all fail-closed:** `ContainerName=` must be `qwen` (the `--replace`
  rationale depends on it); `Exec=` must be `batch`; a `[Container]` key or `PodmanArgs` token the job does not copy
  refuses instead of being dropped; the key mount must be read-only at `/app/api_key.txt`, and its host path is the key
  file the job reads (one source for the server's key and the client's); any line naming `VLLM_API_KEY` refuses; a
  missing probe or Python refuses before the server starts.
- **Extra failure conditions (exit 1):** the server's reported `Desired GPU memory utilization` must equal U
  (`util_applied`), else the sizing is of another configuration; non-finite logits fail the phase; a failed
  `nvidia-smi` call fails the phase it measures; a failed `podman rm` makes the rc 1. The chunk check's `same_argmax`
  is recorded, NOT gated: bf16 noise can flip a near tie (G0: largest difference 0.1875 at 2,048 tokens).
- **`--pull=never`** on the run: the digest is the one the live unit runs, so it is already on the PC; a pull would
  spend the window.
- **Test seams** (validated before anything starts, like the runner's): `SBS_PORT` (default 8081; the address is
  always 127.0.0.1, and a test pins the default argv `-p 127.0.0.1:8081:8080`), `BOOT_SECONDS`, `GPU_FREE_MIB`,
  `SBS_RM_SECONDS` (at most 20), `SBS_PYTHON`, `SBS_PROBE`.
- **`podman logs -f qwen > DIR/qwen.log`** in the background from the start: with `--rm`, a server that crashes (an OOM
  beside RWKV is a plausible outcome) is removed, and its log with it.
- **The probe's URL must be loopback** (`http://127.0.0.1:`), so the key goes nowhere else; the probe's error text is
  scrubbed in process by pattern class (any `Bearer <token>`) and by value.
- **The jobs file wraps each job in `timeout --foreground -k 40 1200`** (the `window1.jobs` pattern), so one hung
  configuration cannot eat the other's time. The cleanup needs at most about 24 s (reader 2 s, `podman rm` bound
  20 + 2 s).

## 4. Tests (evidence demand 2) — VERIFIED

Pasted verbatim (`bash scripts/test_summary.sh tests/test_gpu_side_by_side.py tests/test_gpu_window.py`, each run's rc
read directly, no pipe):

```
run 1 start 2026-09-25T08:42:00Z
run 1 rc=0
pytest-exit: 0
pytest-summary: 105 passed in 109.07s (0:01:49)
run 2 start 2026-09-25T08:43:49Z
run 2 rc=0
pytest-exit: 0
pytest-summary: 105 passed in 109.22s (0:01:49)
$ bash scripts/pc_suite.sh set-id -- tests/test_gpu_side_by_side.py tests/test_gpu_window.py
2 files set=2c5776d02fd6
```

The set is 74 new tests plus the 31 of `tests/test_gpu_window.py` (its baseline at lane start: `31 passed in 70.42s`).
`pyflakes docs/research/findings/jev-pipes/rwkv_sbs_probe.py tests/test_gpu_side_by_side.py`: rc 0.
`bash -n scripts/gpu_side_by_side.sh`: rc 0. `shellcheck`: NOT RUN (not installed in the sandbox).
`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`: 0 on all five files.

What the 74 tests cover (all LLM-free and deterministic; the job at the system boundary as `tests/test_gpu_window.py`
does it: PATH shims for `podman` (JSON argv log, a state file for the container) and `nvidia-smi`, the REAL curl behind
a logging shim, a loopback `/v1/models` that answers 200 only for the fake bearer key while the fake container is up,
and a fake probe on `SBS_PROBE`; the unit is the repo's own `deploy/qwen.container` with only the key path moved):

- refusals start nothing, exact rc and message: 18 usage cases (64), 7 seam cases (64), a container named qwen (3, and
  the existing container is left alone), podman unable to tell (3), no nvidia-smi reading (3), GPU at 1500 MiB (3; 1499
  runs), 7 unpinned image forms (3), 9 unit shapes the job does not copy (3; the refusal never echoes the key), a
  missing unit (3), a missing probe or Python (3)
- one configuration end to end: the podman argv equals the one written from the brief's premise lines (loopback only,
  `--rm`, `batch`, `GPU_UTIL` last); `/v1/models` saw only `Bearer <fake key>` and the curl argv shows `@/dev/fd/`;
  the probe argv is exact and its key file is the served key; the sizing parses the premise's numbers; the removal ran
  once; the log follower is dead; the key is in no argv and no file but its own
- failures that still remove once: a boot that never answers, a server that exits during boot (fails at once, not
  after 600 s), a failed start, a probe rc 1, a probe that reports a phase without its measurement, each missing
  sizing line (recorded as missing, never a zero), a zero or an unreadable number, a share the server did not apply
- signals: TERM to the job's process group mid-probe (rc 130, the reader dead, removal once), TERM to the job alone
  (the cleanup stops the reader), INT during the boot wait, signals during the cleanup ignored, a hung `podman rm`
  KILLed at its bound (rc 137 recorded), and the composition: `scripts/gpu_window.sh` running this job, a TERM to the
  runner reaching the reader through the runner's own timeout, the removal before the runner's `systemctl start`
- structure: every inner `timeout` is `--foreground` (per occurrence, with a negative control), the AF-AP-145 trap
  shape; the jobs file holds exactly the brief's two configurations and each passes the job's own validation
- the probe: imports without torch; asks G0's own question and G0's forward keeps one position (both scoped to the AST
  node, AF-AP-80); `main()` end to end with a stand-in torch module and a stand-in G0 (it takes env, model, ids and
  question from G0's functions, runs every phase inside `inference_mode`, writes no key); the read carries the state
  chunk to chunk; the questions read a fresh copy; the chunk check compares two halves with one whole; N requests go
  out at once (a server barrier), with only the four keys and the key only in the header; the aggregate pinned exactly
  on a tick clock (148 tokens / 2.25 s = 65.778); a response without usage fails its row; an echoed key is scrubbed
  (whole, in a header, and cut off); `together` keeps RWKV working until the load ends; a failed phase keeps earlier
  rows and the next phase runs; NaN logits and a failed nvidia-smi fail their phase; nvidia-smi rows parsed as given
  (`[N/A]` is `None`, never 0); the real entry point fails loud without a model and leaks no key

Development record: the first full run had one red, my own test's assumption (a rounded wall time checked against an
unrounded rate at an 11 ms wall), replaced by the exact tick-clock pin above. The together test first ran all phases
and sat 30 s on a held load in `qwen_idle_rwkv`; it now drives `phase_together` directly (0.5 s).

## 5. Mutants (evidence demand 3) — VERIFIED

Driver: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/sbs1/mutate.py` (scratch, not
delivered). Every mutant runs in a FRESH copy of the files the tests read, never the shared tree. The old snippet must
occur exactly once; the mutant must pass `bash -n` or `compile()`; the copy must collect 74 tests like the clean copy;
the test module must resolve SCRIPT and PROBE inside the copy (printed); `PYTHONDONTWRITEBYTECODE=1`. A kill is rc 1
with a pasted FAILED line and assertion. The denominator is a literal (5 required, 16 extra). Self-test: with the first
row dropped the driver printed `EXPECTED=5 KILLED=4` and exited 1. The production files hashed the same before and
after every run (`f21ee328149e7464` script, `871d4cd22e40769d` probe, `b888bec6a42bed53` tests, `98d4f43cb51376c1` jobs).
Final runs on the final files: `REQUIRED driver rc=0 ... EXPECTED=5 KILLED=5 SURVIVED=0 INVALID=0`;
`EXTRA driver rc=0 ... EXPECTED=16 KILLED=16 SURVIVED=0 INVALID=0`.

The brief's five:

| mutant | what it changes | killed by (pasted) |
|---|---|---|
| M1 cleanup's `podman rm` removed | `RM_RC=0` in place of the bounded `podman rm -f -i qwen` | `test_a_run_starts_the_server_waits_records_the_sizing_runs_the_probe_and_removes_it`: `AssertionError: assert ('run' == 'run' ... 'logs' == 'rm'` (the last podman call is not a removal); also the group-TERM test |
| M2 digest check removed | the `@sha256:` regex line replaced by `:` | `test_an_unpinned_image_refuses_before_anything_starts[...:latest]` and its 6 siblings: `assert (0 == 3)` |
| M3 key moved into argv | curl `-H "Authorization: Bearer $(cat "$KEY_FILE")"` | the end-to-end test: `assert '@/dev/fd/' in '-s -m 5 --noproxy * ... -H Authorization: Bearer SBS7-fake-side-by-side-key-41d9 ...'` |
| M4 a missing KV line read as success | the parser returns `(0, None)` for a missing line | `test_a_missing_sizing_line_is_a_recorded_failure_never_a_zero[...]` (4 params): `assert 0 == 1` (rc) |
| M5 TERM trap removed | the `trap ... on_signal TERM' TERM` line deleted | `test_term_to_the_job_group_stops_the_reader_and_removes_once`: `assert (-15 == 130)`; also the TERM-alone test |

M5 detail (a correction to my own early note): with no TERM trap, bash still runs the EXIT trap (the cleanup runs) and
then dies of the signal, so the parent sees -15 (a `wait` in bash shows 143). My early probe read 143 through `wait`
and I first wrote "exits 143"; the kill does not depend on which, since the test pins rc 130 and the reason.

Extra mutants (mine, to test the suite's power beyond the brief): X1 INT trap removed; X2 cleanup leaves the reader
running (`_dead(pid)` false); X3 `-e VLLM_API_KEY=...` added to podman's argv; X4 a missing line not counted; X5
questions without `deepcopy`; X6 the read drops the state; X7 the load sequential (the server barrier breaks); X8
`together` one pass only (`len(more_passes) == 0`); X9 the share check off; X10 the loopback check off; X11 the free
threshold `-lt` to `-le`; X12 positivity off (a 0-token KV cache accepted); X13 the rm `timeout` without
`--foreground`; X14 the cleanup without its ignore; X15 `logprobs` added to the payload (AF-AP-201); X16 the Bearer
scrub off (the cut-off key leaks). All 16 killed; X13 and X14 are killed only by the structural tests.

## 6. What the sandbox cannot run (evidence demand 4)

NOT RUN HERE, said plainly: the probe's GPU phases (torch is not installed in the sandbox and there is no GPU), the
real container (no podman), the real vLLM server and its log, the real nvidia-smi, the real timing of `podman rm -f` on
a vLLM container, and the window itself. Everything above runs against stand-ins at those boundaries; no number in
this report is a measurement of the side-by-side. The coordinator runs the window on the PC. Before it, the PC clone
needs these four files (the job line runs `cd ~/agent-factory && ... bash scripts/gpu_side_by_side.sh`).

## 7. The brief's two questions

**Does `nvidia-smi --query-compute-apps` list a rootless podman container's vLLM process by a host pid?** Not
measurable here. INFERRED: NVML reports the kernel's global pids, so on the host the container's engine process should
appear under a host pid (the known symptom is the reverse: inside a container, nvidia-smi shows host pids it cannot
match). The probe does not depend on it: it records every row (`pid`, `used_mib`, the raw line) and its own pid, and
marks its own row absent (`own_mib: null`), never zero. The window's `smi` records answer the question.

**Is a free-memory margin needed beside the 0.90 and 0.92 shares?** Yes. The premise's own numbers say the second
configuration does not fit and the first fits by about 62 MiB before allocator overhead. The arithmetic, computed in
code from committed numbers (tiers per input):

| input | value | source | tier |
|---|---|---|---|
| CUDA-visible total | 24,122 MiB | `g0.json` env `total_mib` (torch, Qwen stopped) | VERIFIED (committed file) |
| other GPU users, Qwen stopped | 255 MiB | window2 `gpu_free.used_mib` (nvidia-smi) | VERIFIED (committed file) |
| an RWKV process's CUDA context | 261 MiB | 24,122 - 23,606 (G0's free at start) - 255 | INFERRED (two instruments) |
| vLLM beyond its budget | 320 MiB | 24,022 used at 0.972 (findings doc) - 255 - 0.972 x 24,122 | INFERRED (two readings, 6 h apart) |
| KV GiB at U | U x 23.56 - 15.82 | the log's own accounting (22.9 - 14.73 - 1.09 = 7.08) | INFERRED (weights and activation fixed) |
| KV tokens per GiB | 31,472 | 222,822 / 7.08 | INFERRED |
| RWKV torch peak | 1,514 MiB (C=4096), 1,260 (C=2048) | `g0.json` ladder, weights included | VERIFIED values; ASSUMED equal for a chunked read with a carried state |

The model reproduces the one known point: at U=0.972 it gives 222,832 KV tokens (actual 222,822), 1.70x concurrency,
and about 100 MiB left (nvidia-smi read 24,022 of 24,122 used).

| U | KV tokens | vs today | max concurrency at 131,072 | left for the RWKV process |
|---|---|---|---|---|
| 0.972 | ~222,832 | 0% | 1.70x | 100 MiB |
| 0.92 | ~184,275 | -17% | 1.41x | 1,354 MiB |
| 0.90 | ~169,445 | -24% | 1.29x | 1,837 MiB |
| 0.89 | ~162,031 | -27% | 1.24x | 2,078 MiB |
| 0.88 | ~154,616 | -31% | 1.18x | 2,319 MiB |

- configuration 1 (U 0.90, C 4096): needs 1,775 MiB (context 261 + peak 1,514) of 1,837: margin +62 MiB before the
  caching allocator's rounding and fragmentation, and before any growth of the desktop's 255 MiB. Likely an OOM, or
  the edge.
- configuration 2 (U 0.92, C 2048): needs 1,521 MiB of 1,354: short by 167 MiB. Expected to OOM on the RWKV side.
- for a 500 MiB margin: U at most 0.8818 for C=4096, 0.8924 for C=2048, 0.9022 for C=1024 (the C=1024 peak, 1,023 MiB,
  is a slope estimate from the ladder, INFERRED).

What a failed configuration still yields: the sizing (KV tokens, the Qwen side of the trade-off) comes from the server
log before the probe runs, so even an RWKV OOM records what Qwen gives up; the probe records the OOM text, and the
job exits 1. The jobs file keeps the contract's two configurations; changing them is the coordinator's decision
(DISCREPANCY D1).

## 8. Self-attack: the three most likely ways this is wrong

1. **The temporary server is not the live unit in some way that matters.** The premise's `ExecStart` is redacted
   (`... --publish 8080:8080 ...`); quadlet adds its own flags (`--cidfile`, `--cgroups=split`, `--sdnotify=conmon`,
   `-d`, `--replace`, `--rm`). If it added something the GPU needs (an SELinux label option, for example), the
   temporary server would fail its boot. Ruled out as far as the sandbox can: the job copies every key of the unit and
   refuses any key or `PodmanArgs` token it does not copy (tested with `SecurityLabelDisable=true` and
   `--shm-size=16g`), and the unit has no key that becomes a label option. Not ruled out: the elided flags. Cheap
   check before the window: compare `systemctl --user cat qwen.service`'s `ExecStart` with the job's run line. A
   mismatch fails loud (`boot:` in `summary.json`, the log in `qwen.log`), never silent.
2. **The sizing lines are phrased differently from the premise.** The fixture is the premise's own lines, verbatim
   (the motivating instance), and the parser takes the last match anywhere in a line, joined or split (both tested).
   The image is pinned by digest, so the vLLM build that printed them is the one that runs. A missing or changed line
   is a recorded failure with rc 1, never a zero (M4, X4, X12 killed).
3. **The cleanup overruns the runner's 30 s.** The cleanup is: reader TERM, up to 2 s, KILL; then `podman rm -f -i
   qwen` bounded at 20 s + 2 s KILL grace (about 24 s in all). vLLM's own stop within podman's default 10 s is
   INFERRED, not measured here. If it overruns, the runner KILLs the job's group (the reader included) and its restore
   (`podman run --name qwen --replace`) removes the leftover: the name `qwen` is the fallback, and a test pins that
   the unit's `ContainerName` is `qwen`, since the fallback depends on it.

## 9. NOT done

- The window: not run (section 6). No GPU number exists from this lane.
- `shellcheck`: not run (not installed in the sandbox).
- The PC half of the premise: not re-measured (no bridge in this lane, by rule).
- The runbook, the findings and the ledger: not updated (outside the boundary; the coordinator's).
- No commit, no push, no PC copy of the files.
- The configurations were not changed despite section 7 (a contract change is the coordinator's).

## 10. DISCREPANCIES and flagged choices

- **D1 (the one that matters): the brief's configurations likely do not fit** (section 7). Suggested, for the
  coordinator to decide: C=2048 at 0.89 and C=4096 at 0.88, or a C=1024 row at 0.90, to keep about 500 MiB free.
- **D2 (interpretation): `together` repeats the read until the load ends** (section 3); single-pass would make Qwen's
  "while RWKV works" rate mostly RWKV-idle time. The `overlap` record shows the coverage.
- **D3 (the G0 question is a repeated literal).** G0 has no constant for it (it is inline in `phase_ladder`), and the
  boundary forbids editing G0; the probe repeats the string and a test pins it to G0's AST node, so drift is red.
  Code is imported, never copied (a test checks the probe defines none of G0's functions). `phase_env` is reused too,
  beyond the three the brief names.
- **D4 (additions beyond the letter):** listed in section 3; each is a refusal or a failure, none relaxes the contract.
  `peak_reserved_mib` is recorded beside the required `max_memory_allocated`.
- **Adjacent observation (INFERRED, not a proven defect, not fixed):** `scripts/gpu_window.sh:68-69` `exec 9>"$STATE/lock"`
  holds the window lock on fd 9 without close-on-exec, so every job's descendants inherit it; a descendant that outlived the runner (a
  container monitor the job failed to remove) could hold the window lock and make the next window exit 5. This job
  removes its container, and the restore's `--replace` removes a leftover, so the exposure is bounded. A check during
  a window: `ls -l /proc/<conmon pid>/fd | grep lock`.
