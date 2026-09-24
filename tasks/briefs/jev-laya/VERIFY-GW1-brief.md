# VERIFY-GW1: the independent verify of the guarded GPU window before its first live use (task #242; D-078, D-081)

Role: adversarial-verifier (sandbox, Opus 5.5). PIN: the content of the files hashed below (commit "gpu_window: the guarded
GPU window for the RWKV-7 G0 probe and training", GATED-PENDING-VERIFY). Report: `tasks/briefs/jev-laya/VERIFY-GW1-report.md`
(write it incrementally from the start).

`scripts/gpu_window.sh` runs ON the owner's PC. It stops the owner's vLLM `qwen` service (the local model every PC lane and
the owner's own tools use), runs jobs on the freed GPU, and must ALWAYS start the service again. Its commit message states
the contract; its tests are `tests/test_gpu_window.py`. The owner approved a window only when no lane is live and "only
offline for a few mins" (D-078, D-081). Attack the script against that contract with NEW shapes, never only its own tests.
Report every meaningful observation with no severity filter, then apply the blocking predicate (contract-mapped, reproduced
through the real script, materially effective, a concrete discriminator, in-boundary) and give ONE gate recommendation:
MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID.

## The contract to attack

1. Never stop the service while any lane is live (`$AF_REPO/.lanes/*/lane.pid` with a live pid; a pid file without a pid
   counts as live), when the service is not active, when `/v1/models` does not answer 200 with the key, or while another
   window holds the lock. Each refusal stops nothing.
2. Once stopped, the service is ALWAYS started again and `/v1/models` is waited for: after success, a failing job, a job
   past the budget, a failed stop, a GPU that never frees, and INT or TERM. Only SIGKILL escapes (documented).
3. One shared time budget bounds all jobs; INT or TERM stops the running job at once.
4. The key never appears in any argv, log or record.

## Suspicions to test (not a limit)

- A job that leaves a process behind: a daemon (`setsid`, `nohup ... &`, a double fork) or a child in another process group
  keeps the GPU after the job returns, and the restore starts vLLM onto an occupied GPU. What happens, and does the record
  show it?
- Jobs-file shapes: CRLF line endings, a line with only spaces, a very long line, a job that reads stdin, a job that
  prints megabytes, a job that changes directory or exports variables (does it leak to the next job?).
- The budget: a job that ignores TERM (the `--kill-after=30`), a budget that ends between jobs, `--max-minutes` at 1 and 240,
  GPU_WINDOW_MAX_SECONDS and GPU_FREE_WAIT_SECONDS given garbage (they are test seams: what does garbage do on the PC?).
- Signals: TERM during the GPU-free wait, during `restore`'s own wait, during a job's `--kill-after` grace; INT; a second
  TERM during the abort; HUP (the caller's terminal gone: is the job protected when started with `setsid nohup`?).
- The lane check: a lane.pid of a live process owned by another user (`kill -0` fails with EPERM, so it reads as dead),
  a lane directory created between the check and the stop (a race: can it happen, what is the window?), a symlinked lanes
  dir, thousands of lane dirs.
- The lock: two windows started together; a stale lock file left by a SIGKILLed window (flock is released with the process:
  confirm); the state dir not writable.
- The restore: `systemctl start` failing; the unit in a failed state (`Restart=always` has given up); `/v1/models` answering
  200 before the model can serve a completion (is 200 on `/v1/models` a strong enough "back" signal for vLLM?); the key file
  rotated during the window.
- The record: is every refusal and every step recorded, and can a record line be malformed (a path with a quote)?

## Evidence rules

Reproduce every claim through the real script (PATH shims for systemctl, nvidia-smi and curl are the sanctioned boundary, as
the tests use; a loopback HTTP server stands in for `/v1/models`). Mutants on scratch copies ONLY, one fresh copy per mutant.
Never run the script against the real PC, the bridge or any real service: NO bridge calls at all. Use a short `--basetemp`
(make the parent first). Kill by pid only.

## Standing rules

No outward actions (no commits, pushes, PRs, comments, GitHub writes, bridge calls). Do not spawn subagents. Never create or
remove `.jev/intercept-off` (the JT3 search hook is live in this session: a semantic Grep may be answered by it; repeat the
identical call within 120 s for the raw result). FAKE strings only for anything secret-shaped. Check every file you write
with `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`.

## The planned first window (read it as part of the contract's use)

```
# ~/rwkv-g0/window1.jobs, run as: setsid nohup bash scripts/gpu_window.sh --max-minutes 45 ~/rwkv-g0/window1.jobs
cd ~/agent-factory && ~/venv-rwkv-b/bin/python docs/research/findings/j2b-variants/rwkv7_g0.py --out-dir ~/rwkv-g0/out-b || ~/venv-rwkv/bin/python docs/research/findings/j2b-variants/rwkv7_g0.py --no-cache --out-dir ~/rwkv-g0/out-a
cd ~/agent-factory && HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 ~/venv-laya/bin/python scripts/laya_ft/train.py --dataset ~/laya-ft/ds-0b342c7 --labels docs/research/findings/laya-ft-labels/2026-09-24-openjev/labels.jsonl --out ~/laya-ft/ckpt-head-w1 --mode head --device cuda --epochs 1 --batch-size 8 --eval-loss --model-dir <the PC's Laya snapshot>
```

## PREMISE — MEASURED at authoring (2026-09-24 20:0xZ, /home/user/agent-factory at local HEAD)

```
$ for f in scripts/gpu_window.sh tests/test_gpu_window.py docs/research/findings/j2b-variants/rwkv7_g0.py; do echo "$(git rev-parse --short=12 HEAD:$f) $f"; done
a6ac010f69e3 scripts/gpu_window.sh
62b4de1912d1 tests/test_gpu_window.py
0591a08306f8 docs/research/findings/j2b-variants/rwkv7_g0.py
$ bash scripts/test_summary.sh tests/test_gpu_window.py 2>&1 | tail -1; bash scripts/pc_suite.sh set-id -- tests/test_gpu_window.py
pytest-summary: 14 passed in 9.79s
1 files set=65a832bc5b21
```
