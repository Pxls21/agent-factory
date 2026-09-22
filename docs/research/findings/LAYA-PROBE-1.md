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

NOT run here: J0-b pending — the PC is the reference venue (6 threads per the brief's STOP rule) and needs a quiet box; at filing time three local lanes (B9, VERIFY-T90-R2, PCJ1) hold it. The same committed harness runs there over the bridge and fills this section from its JSON; until then the sandbox verdicts above are the second venue's only.

## What this decides and what it does not

- Decides: the sandbox venue's latency family (193-464ms) and determinism (DETERMINISTIC) for the typed-decisions checkpoint at FP32 on 4 pinned CPU threads.
- Does not decide: the PC's numbers (the reference venue), CUDA behaviour (the 3090 is full), the encoder and multilingual checkpoints, batch throughput, or anything about answer quality — the probe measures latency and determinism only. J1's ledger stays LLM-free and model-free (seed AC 5) whatever the verdicts say.

