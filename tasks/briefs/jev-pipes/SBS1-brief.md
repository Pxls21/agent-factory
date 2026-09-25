# SBS1: the side-by-side GPU window job (RWKV stream reader beside Qwen; task #262; D-088)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/jev-pipes/SBS1-report.md` (write it
incrementally from the start). PIN: 6ee9322 (origin; the three READ files below are unchanged since, measured).

## WHY

The owner wants two engines on the one RTX 3090: their vLLM Qwen server unchanged, and a small RWKV-7 Jev beside it (D-087, D-088).
The owner's pointer, `rwkv-rs/vllm-rwkv`, cannot run RWKV-7 on this card (FlashRWKV refuses to build below SM90; the 3090 is SM86;
`docs/research/findings/jev-pipes/VLLM-RWKV-2026-09-25.md`, AF-AP-207). The engine is the plan's own RWKV stream reader on the FLA
stack (D-079's pinned checkpoint), which ran on this card in the 2026-09-24 window with Qwen stopped. What nobody has measured: the
two side by side. A permanent cut of Qwen's memory share goes to the owner with the measured trade-off (D-088), so this job
measures it inside a GPU test window: what Qwen gives up (KV tokens, which is lane capacity) and what each side does to the other's
speed.

## CONTRACT

Two programs and their tests. Both run ON the PC, inside a window that `scripts/gpu_window.sh` opens (it has stopped `qwen.service`,
seen the GPU free, and will ALWAYS start the service again when the jobs end). The window's job file is one line per configuration.

**1. `scripts/gpu_side_by_side.sh`** (CREATE), one configuration per run:
`gpu_side_by_side.sh --util U --chunk C --tokens T --load N --out DIR`
- Refuses (exit 3, nothing started) unless it is inside a window: a container named `qwen` exists, or the GPU's memory.used is at or
  over `GPU_FREE_MIB` (default 1500, the runner's rule). Usage errors exit 64; validate every number (U a decimal 0.50-0.97; C
  1024-16384; T C-65536; N 0-8).
- Starts a TEMPORARY Qwen server from the live unit's own definition: read `Image=` from `~/.config/containers/systemd/qwen.container`
  (refuse, exit 3, unless it is digest-pinned `@sha256:`), and the unit's volumes, environment, device and IPC arguments (premise
  below), plus `GPU_UTIL=U`, published on `127.0.0.1:8081` only, command `batch`, `--rm`. Name the container `qwen` ON PURPOSE and
  say why in a comment: the unit's `ExecStart` runs `podman run --name qwen --replace`, so the runner's restore removes a leftover
  even if this job was killed. The key reaches the server ONLY through the unit's read-only file mount; never `-e VLLM_API_KEY`
  (that puts it in podman's argv, the old manual recipe's defect).
- ALWAYS removes the temporary container on exit, on a failed phase and on INT or TERM (`podman rm -f -i qwen`, bounded), once, with
  further signals ignored while it cleans up; the runner gives a job 30 s after TERM before KILL (`gpu_window.sh:159`).
- Waits for `http://127.0.0.1:8081/v1/models` to answer 200 (the key in a header read from its file through a process substitution,
  never argv or a log; `gpu_window.sh`'s `models_answer` is the pattern), up to `BOOT_SECONDS` (default 900).
- Records the server's own sizing from `podman logs qwen`: `Available KV cache memory`, `GPU KV cache size` (tokens), `Maximum
  concurrency`, and the `Desired GPU memory utilization` line, as numbers. A line that is missing is a recorded failure (exit 1), never
  a silent zero.
- Runs the reader probe (2) once, which measures every phase in one process, then merges the server's sizing and the probe's record
  into `DIR/summary.json` with the configuration and an `rc`. Exit 0 only when every phase produced its measurement.

**2. `docs/research/findings/jev-pipes/rwkv_sbs_probe.py`** (CREATE), run with `~/venv-rwkv-b/bin/python`:
- Reuses `docs/research/findings/j2b-variants/rwkv7_g0.py` by import (its `load`, `real_text_ids` and `Scorer.forward`, which sends
  `logits_to_keep=1`); no copy of its code. Imports torch only inside functions (as G0 does), so the sandbox tests can import it.
- Phases, each written to the output JSON as it completes (a later failure keeps the earlier rows, as G0 does):
  - `alone`: read T real tokens in chunks of C, carrying the state (`past_key_values`) from chunk to chunk: per-chunk seconds, the
    torch peak (`max_memory_allocated`), and the process's own GPU memory from `nvidia-smi --query-compute-apps=pid,used_memory`
    (record every compute app's pid and MiB; do not assume which pid is Qwen's). Then the G0 question 5 times from a `copy.deepcopy`
    of the final state (median, all). Then one check: two chunks of C/2 give the same last-position argmax as one forward of C
    (record the largest logit difference).
  - `qwen_idle_rwkv`: Qwen alone under load while the RWKV model sits loaded and idle: N concurrent chat completions (fixed prompt
    built from repo text, `max_tokens` 512, `temperature` 0, model `qwen3.8-27b-local`) to `http://127.0.0.1:8081/v1/chat/completions`;
    aggregate completion tokens per second from each response's `usage` and the wall time. Skipped (recorded) when N is 0.
  - `together`: the same load started, and while it runs the `alone` read and questions again: RWKV's numbers under Qwen load, and
    Qwen's tokens per second while RWKV works (the reverse impact).
- The load requests carry only `model`, `messages`, `max_tokens`, `temperature` (AF-AP-201: never `logprobs`, `prompt_logprobs`,
  `n`, `best_of` or `echo` to this server). The key is read from `--key-file` in process into a header; never printed, never argv.

**3. `tests/test_gpu_side_by_side.py`** (CREATE): the job at the system boundary only, as `tests/test_gpu_window.py` does it (PATH
shims for `podman` and `nvidia-smi` that log their argv; the REAL curl behind a logging shim; a loopback HTTP server for `/v1/models`
that checks the bearer key; a FAKE key string; a fake reader probe on a seam). And the probe's harness logic with an injected fake
forward and a loopback fake chat server (chunk boundaries and state threading; the aggregation; the key only in a header). Negative
controls assert exact exit codes and messages.

**4. `docs/research/findings/jev-pipes/sbs-window.jobs`** (CREATE): two configurations for the window, each writing under
`~/gpu-window/`: `--util 0.90 --chunk 4096` and `--util 0.92 --chunk 2048`, both `--tokens 16384 --load 4`.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. The tests, twice: `bash scripts/test_summary.sh tests/test_gpu_side_by_side.py tests/test_gpu_window.py` (paste both summaries and
   the set id from `bash scripts/pc_suite.sh set-id -- <the two files>`); pyflakes rc 0 on the new Python files; `bash -n` and
   `shellcheck` (if installed) on the new script.
3. Mutants, each red on a named test: the cleanup's `podman rm` removed; the digest check removed; the key moved into argv; a missing
   KV line read as success; the TERM trap removed.
4. What the sandbox cannot run, said plainly: the probe's GPU phases and the real container. The coordinator runs the window.
5. NOT-done and DISCREPANCIES.

## BOUNDARY

CREATE only the four files above and your report. READ everything else; MODIFY nothing (the coordinator updates the runbook and the
findings after the real run). Scratch: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/sbs1/`.

## STANDING RULES

No network beyond loopback test servers; no PC bridge; no git writes; no outward-facing action. Never read a real secret file
(`.pc-bridge.env`, `/root/.codiv/api.env`, any `*.env`, any key file); every key in a test is a FAKE string you invent. Two other
lanes are live in this tree on other files: touch nothing outside your boundary. Check every file you write with
`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` (0 expected).

## PREMISE — MEASURED at authoring (2026-09-25 07:5xZ; the sandbox at 6ee9322, and the PC read-only)

```
$ git show 6ee9322:<file> | sha256sum | cut -c1-16      (unchanged at the local head: 0 diff lines)
9f44e29c479dfbfd  scripts/gpu_window.sh
7583bf5f3281a9a4  docs/research/findings/j2b-variants/rwkv7_g0.py
da7deec82c3d6850  deploy/qwen.container
$ grep -n 'timeout --kill-after' scripts/gpu_window.sh
159:  timeout --kill-after="$KILL_AFTER" "$left" bash -c "$c" > "$log" 2>&1 < /dev/null &
$ grep -n "^def load\|^def real_text_ids\|^class Scorer\|^    def forward\|^SNAPSHOT" docs/research/findings/j2b-variants/rwkv7_g0.py
43:SNAPSHOT = Path(os.path.expanduser(
83:class Scorer:
90:    def forward(self, ids, cache=None):
135:def load(rec, args):
152:def real_text_ids(tok, n):
$ grep -n "Image=\|Exec=\|PublishPort\|Volume=\|Environment=\|PodmanArgs" deploy/qwen.container   (the live unit matches, read on the PC)
21:Image=ghcr.io/syv-ai/qwen38-27b-rtx3090@sha256:c52d9033527df5249d2f7306b35173a47f4f87d45bb60927fbe93fdb4986aacb
22:Exec=batch
23:PublishPort=8080:8080
24:Volume=qwen-cache:/cache
25:Volume=/home/rocco/qwen-serving/models:/app/models
26:Volume=/home/rocco/.config/qwen-builder/api-key:/app/api_key.txt:ro
27:Environment=PORT=8080
28:Environment=SPEC=mtp
29:Environment=MAX_LEN=131072
30:Environment=PREFIX_CACHE=1
31:Environment="EXTRA_ARGS=--served-model-name qwen3.8-27b-local qwen3.8-27b"
32:PodmanArgs=--ipc=host --device nvidia.com/gpu=all
$ (PC) systemctl --user cat qwen.service | grep ExecStart      (redacted)
ExecStart=/usr/bin/podman run --name qwen --replace --rm --cgroups=split --sdnotify=conmon -d ... --publish 8080:8080 ... batch
$ (PC) podman run --rm --entrypoint cat <the image> /app/batch/start_qwen.sh   (the fp8-KV branch, the default)
GPU_UTIL=${GPU_UTIL:-0.972}
if [ -z "$VLLM_API_KEY" ] && [ -f "$REPO/api_key.txt" ]; then export VLLM_API_KEY="$(cat "$REPO/api_key.txt")"; fi
exec venv/bin/vllm serve "$MODEL" --served-model-name qwen3.8-27b --host 0.0.0.0 --port $PORT --gpu-memory-utilization $GPU_UTIL ...
$ (PC) podman logs qwen | grep ...    (the running server's boot after the 2026-09-24 window; container clock)
Model loading took 14.26 GiB memory and 17.888750 seconds
Available KV cache memory: 7.08 GiB
GPU KV cache size: 222,822 tokens, Maximum concurrency for 131,072 tokens per request: 1.70x
Free memory on device (23.05/23.56 GiB) on startup. Desired GPU memory utilization is (0.972, 22.9 GiB). Actual usage is 14.73 GiB for consumed memory (weights + non-torch), 1.09 GiB for peak activation, and 0.71 GiB for CUDAGraph memory.
$ G0 on the 3090 with Qwen stopped (docs/research/findings/j2b-variants/rwkv7-g0/2026-09-24-window2/g0.json; ~/venv-rwkv-b:
  torch 2.7.1+cu128, transformers 4.53.3, fla 0.3.0, triton 3.3.1)
load 0.44 s, 859 MiB allocated; one forward: 2048 tokens peak 1260 MiB | 4096: 1514 | 8192: 2154 | 16384: 3434
first 2048 forward 42.9 s (Triton compile); first question from a copied state 9.6 s, then 0.037 s
```

Questions for you, not facts: does `nvidia-smi --query-compute-apps` list a rootless podman container's vLLM process by a host pid
(record all rows; do not depend on it)? Is a free-memory margin needed beside the 0.90 and 0.92 shares (say what the numbers imply)?
