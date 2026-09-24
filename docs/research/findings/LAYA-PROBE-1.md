# LAYA-PROBE-1 — J0 FP32 latency + determinism probe of the Laya typed-decisions checkpoint

Filed 2026-09-22 (UTC) by the coordinator from the committed harness `scripts/laya_probe.py` (the J0-a lane died with the 18:2xZ worker restart; its harness, fixture set and checker were checkpointed as b67a813 and the sandbox leg was re-run here on an idle box). Raw output: `docs/research/findings/laya-probe-1-sandbox.json` (the verdict run) and `docs/research/findings/laya-probe-1-sandbox-contended.json` (a contended control, not the verdict). Checker: `tests/test_laya_probe_report.py`. The PC is the reference venue; the sandbox is the second venue. J0 never blocks J1 (seed AC 8).

## Method
- checkpoint `typed-decisions` of HF `convaiinnovations/laya` at revision `1c5edc17a7acd8701df6fc341c0d179f1c62c982` (the checkpoint_sha), loaded FP32 on CPU through `laya.load(...)` and answered through `Agent.system_one`; safetensors sha256 `4fa56de72383a9d3efa9cfa78955733c81b9fc8067a587ca4beb82c78107a24e`.
- fixture `tests/fixtures/decisions/probe/questions.json`: 226 states over the seven question types (fixture_sha `571cd075cf174f268fd12494055dbc598b2d147eb57357fdd80651a1979e83d9`), mean 107.3 tokens per state.
- n_per_type = 200 timed calls per question type (1400 per run), 4 threads pinned to CPUs 0-3, three runs: run 1 timed in-process, run 2 an in-process repeat, run 3 in a fresh process; the determinism digest is the sha256 over every call's probability vector.
- verdict rules (the J0 brief): LATENCY SYNC-OK (p50 <= 300 ms at 4 threads) / ASYNC-ONLY (300 < p50 <= 1500) / STOP (p50 > 1500 ms on the PC at 6 threads); DETERMINISM: DETERMINISTIC / NON-DETERMINISTIC (the diagnostic control on a non-deterministic venue is the same run at `--threads 1`); latency_family = the probe's classifier over the overall p50 (`116-256ms` / `193-464ms` / `1000-1250ms` / other).

## Sandbox CPU

The verdict run (started 2026-09-22 21:13:06Z on an idle box; the probe itself saturates the four pinned cores, so loadavg_after is the probe's own load).

- cpu_model: Intel(R) Xeon(R) Processor @ 2.10GHz (nproc 4)
- pin_cpus: 0-3 (affinity [0, 1, 2, 3]); threads: 4; device: cpu; dtype: float32
- torch: 2.14.0+cpu; laya: 0.3.5; transformers: 5.17.0; safetensors: 0.8.0
- checkpoint_sha: 1c5edc17a7acd8701df6fc341c0d179f1c62c982 (the HF revision); safetensors_sha: 4fa56de72383a9d3efa9cfa78955733c81b9fc8067a587ca4beb82c78107a24e; fixture_sha: 571cd075cf174f268fd12494055dbc598b2d147eb57357fdd80651a1979e83d9 (226 states)
- n_per_type: 200 (1400 timed calls per run); wall 374.3 s for the three runs
- loadavg_before: 0.65 2.78 3.16; loadavg_after: 4.01 3.98 3.78
- overall: p50 259.67 ms; p95 357.76 ms; max 872.25 ms (n=1400)

| question type | n | p50 ms | p95 ms | max ms |
|---|---|---|---|---|
| ap.violates_row | 200 | 245.74 | 338.33 | 574.50 |
| b1.finding_kind | 200 | 309.39 | 411.78 | 872.25 |
| b1.finding_sev | 200 | 223.13 | 282.66 | 348.05 |
| b2.hit_role | 200 | 301.20 | 392.11 | 570.34 |
| d1.bug_echo_scores | 200 | 209.53 | 280.82 | 434.10 |
| v1.finding_class | 200 | 271.42 | 347.68 | 470.80 |
| wf.drift | 200 | 235.11 | 314.30 | 430.95 |

- digest_run1: `e39555ceb0bf06665f8ecfc54ec050738e403eaceb86dee3675f324a986b3005`
- digest_run2: `e39555ceb0bf06665f8ecfc54ec050738e403eaceb86dee3675f324a986b3005`
- digest_run3_fresh_process: `e39555ceb0bf06665f8ecfc54ec050738e403eaceb86dee3675f324a986b3005`
- latency_family: 193-464ms — CONFIRMS the 193-464ms family on this venue; REFUTES 116-256ms and 1000-1250ms
- latency_verdict: SYNC-OK (overall p50 259.67 ms at 4 threads against the 300 ms sync bar; on their own these types sit above 300 ms: b1.finding_kind 309.39, b2.hit_role 301.20 — a per-type sync budget is a PC-leg question)
- determinism_verdict: DETERMINISTIC (three identical digests, the third from a fresh process)

### Contended control (not the verdict run)

The first run of the day (20:47Z) started while the sandbox Laya endpoint reloaded its model and a GitNexus reindex ran (loadavg_before 1.63 1.28 0.86, loadavg_after 4.00 4.00 3.55 with competitors). Its three digests are identical to the verdict run's (`e39555ceb0bf06665f8ecfc54ec050738e403eaceb86dee3675f324a986b3005`), so determinism held under contention; its latency did not: p50 266.65 ms, p95 400.42 ms, max 11964.21 ms. It is kept beside the verdict run as `laya-probe-1-sandbox-contended.json` and decides nothing.

## PC CPU

The verdict run on the reference venue (started 2026-09-24 04:11:28Z by the process start time, on a quiet box: no PC lane was live and loadavg_before was 0.20; the probe itself saturates the four pinned cores, so loadavg_after is the probe's own load). The JSON is `laya-probe-1-pc.json` beside this report (sha256 `c557cfd7ce9b19de1325c381da10240009c45a7eecdf6b427d47e8b19cb8e9e0`, the same on the PC and here).

- cpu_model: AMD Ryzen 5 5600X 6-Core Processor (nproc 12)
- pin_cpus: 0-3 (affinity [0, 1, 2, 3]); threads: 4; device: cpu; dtype: float32
- torch: 2.14.0+cu130 (the CUDA build, run on the CPU); laya: 0.3.5; transformers: 5.17.0; safetensors: 0.8.0
- checkpoint_sha: 1c5edc17a7acd8701df6fc341c0d179f1c62c982 (the HF revision); safetensors_sha: 4fa56de72383a9d3efa9cfa78955733c81b9fc8067a587ca4beb82c78107a24e (the same as the sandbox's); fixture_sha: 571cd075cf174f268fd12494055dbc598b2d147eb57357fdd80651a1979e83d9 (226 states; mean 107.3 tokens per state)
- n_per_type: 200 (1400 timed calls per run); wall 513.4 s (the probe's own `wall_time_s`)
- loadavg_before: 0.20 0.15 0.12; loadavg_after: 4.22 4.15 3.48
- overall: p50 336.18 ms; p95 461.70 ms; max 510.41 ms (n=1400)

| question type | n | p50 ms | p95 ms | max ms |
|---|---|---|---|---|
| ap.violates_row | 200 | 326.83 | 351.31 | 366.32 |
| b1.finding_kind | 200 | 456.23 | 463.26 | 475.94 |
| b1.finding_sev | 200 | 317.09 | 330.01 | 339.69 |
| b2.hit_role | 200 | 452.47 | 477.20 | 510.41 |
| d1.bug_echo_scores | 200 | 291.88 | 305.48 | 310.73 |
| v1.finding_class | 200 | 389.83 | 401.24 | 414.98 |
| wf.drift | 200 | 325.15 | 359.52 | 371.84 |

- digest_run1: `e39555ceb0bf06665f8ecfc54ec050738e403eaceb86dee3675f324a986b3005`
- digest_run2: `e39555ceb0bf06665f8ecfc54ec050738e403eaceb86dee3675f324a986b3005`
- digest_run3_fresh_process: `e39555ceb0bf06665f8ecfc54ec050738e403eaceb86dee3675f324a986b3005`
- latency_family: 193-464ms — CONFIRMS the 193-464ms family on the reference venue (overall p50 336.18 ms and p95 461.70 ms fall inside it; the max, 510.41 ms, falls above it); REFUTES 116-256ms and 1000-1250ms
- latency_verdict: ASYNC-ONLY (overall p50 336.18 ms at 4 threads: above the 300 ms sync bar, below the 1500 ms STOP line; six of the seven types sit above 300 ms, the exception is d1.bug_echo_scores at 291.88 ms). The 6-thread STOP check did not run: the brief runs it only when the 4-thread p50 exceeds 1500 ms.
- determinism_verdict: DETERMINISTIC (three identical digests, the third from a fresh process). The digest is also the sandbox's: the two venues give bit-identical answers over the whole fixture set.

How it ran. The harness is the committed `scripts/laya_probe.py` (blob `c58a9f95`, unchanged since b67a813), run from the PC clone at cbd05fa:

```
scripts/laya_probe.py --checkpoint typed-decisions --revision 1c5edc17a7acd8701df6fc341c0d179f1c62c982 --cache /home/rocco/j0b/hf-cache --threads 4 --pin-cpus 0-3 --n 200 --fixture tests/fixtures/decisions/probe/questions.json --out /home/rocco/j0b/laya-probe-1-pc.json
```

- The first launch (04:10Z) ran with `HF_HUB_OFFLINE=1` against the Laya endpoint's own cache (`/home/rocco/hf-laya/hub`) and died with `LocalEntryNotFoundError`: the probe's `snapshot_download` asks for `rl_common.py`, which that cache does not hold. Its log is kept on the PC as `probe-offline-failed.log`.
- The verdict run used a hard-linked copy of that cache (`/home/rocco/j0b/hf-cache`, so the endpoint's cache was not touched) with the network on, as the sandbox run did. It fetched the missing files at the pinned revision (5 files, 65 s); the safetensors sha above matches the sandbox's.
- Two liveness checks at launch self-matched (a `pgrep` label and the bridge's shell wrapper; the incident log's 04:1xZ entry). `ps -o pid,ppid` confirmed one probe process, so the quiet-box evidence is the loadavg line, not those counts.

The reference venue ran slower than the sandbox (p50 336.18 ms against 259.67 ms). The two runs differ in CPU (Ryzen 5 5600X against a 2.10 GHz Xeon) and in the torch build (the CUDA build here, the CPU build there). This probe does not isolate which one causes the gap.

## What this decides and what it does not

- Decides, for the typed-decisions checkpoint at FP32 on 4 pinned CPU threads, per venue (the breakdown's rule: the PC is the reference; the sandbox verdict gates only the sandbox instance):
  - PC: ASYNC-ONLY and DETERMINISTIC. A Laya call on the PC stays off any synchronous path: it runs queued or in the background, never inline in a hook or a gate step.
  - Sandbox: SYNC-OK and DETERMINISTIC, for the sandbox instance only.
  - Both venues confirm the 193-464ms family and give the same determinism digest over the whole fixture set.
- Does not decide: CUDA behaviour (the 3090 is full), the cause of the PC-to-sandbox gap (CPU or torch build), the encoder and multilingual checkpoints, batch throughput, or anything about answer quality — the probe measures latency and determinism only. J0 never blocks J1: J1's ledger stays LLM-free and model-free (seed AC 5) whatever the verdicts say.
