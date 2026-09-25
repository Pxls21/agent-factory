# Side by side on one RTX 3090: Qwen vLLM plus the RWKV-7 stream reader (measured 2026-09-25)

A GPU test window (D-088) on the owner's PC, window `20260925T090708Z` (09:07:08Z to 09:12:56Z): `scripts/gpu_window.sh` stopped
`qwen.service` and ran `docs/research/findings/jev-pipes/sbs-window.jobs`. Each job started a temporary Qwen server from the live unit's
own definition at a smaller `GPU_UTIL` (loopback 8081) and ran the RWKV-7 0.4B reader (`RWKV/RWKV7-Goose-World2.9-0.4B-HF`, bf16, fla
0.3.0, torch 2.7.1+cu128, `~/venv-rwkv-b`) beside it: alone, then with Qwen under load (4 requests at once, 512 tokens each, temperature
0), then both working at once. The service came back after the jobs (75 s, `/v1/models` 200). Raw records: `sbs-2026-09-25/` (the two
`summary.json` files, sha256 checked against the PC; no key found by the PC-side known-values check). Tooling: SBS1 (task #262).

## Result

**At Qwen 0.90 with 1,024-token RWKV chunks, both engines served together. At Qwen 0.88 with 4,096-token chunks, Qwen's engine died of
CUDA out-of-memory on its first requests.**

| | Qwen 0.90, RWKV chunk 1,024 | Qwen 0.88, RWKV chunk 4,096 |
|---|---|---|
| Qwen KV cache | 5.38 GiB, 169,622 tokens (-23.9%) | 4.91 GiB, 154,973 tokens (-30.4%) |
| Qwen concurrency at 131,072 tokens | 1.29x (today 1.70x) | 1.18x |
| Qwen boot | 81 s | 76 s |
| RWKV process (nvidia-smi) | 1,722 MiB beside Qwen's 21,798 | 2,168 MiB beside Qwen's 21,338 |
| RWKV torch peak (allocated / reserved) | 1,296 / 1,408 MiB | 1,794 / 1,854 MiB |
| RWKV read, steady, alone | 0.039 s per 1,024 tokens (about 26k tokens/s) | 0.090 s per 4,096 tokens (about 45k tokens/s) |
| RWKV question from a copied state, alone | 0.0315 s median (15 tokens) | 0.0319 s median |
| Qwen, 4 requests, RWKV loaded and idle | 155.3 tokens/s | engine dead (HTTP 500) |
| Qwen, 4 requests, RWKV reading the whole time | 88.4 tokens/s (-43%) | not reached |
| RWKV under that Qwen load | 0.059 s per chunk (+52%); questions 0.036 s (+14%) | not reached |
| Two half-chunks against one chunk | same argmax, largest logit difference 0.375 | same argmax, 0.5 |

The first calls compile Triton kernels: the first chunk took 19.9 s and 19.7 s, the second 6.0 s and 2.0 s, the first question 4.5 s and
4.0 s. A resident reader warms up once at start.

## What it means

1. **Side by side works at 0.90.** Qwen gives up about a quarter of its KV cache: 222,822 tokens become 169,622. Two long-context lanes
   of about 85k tokens each still fit; today's rule (one long-context local lane while the cloud route is out, D-061/D-062) is not bound
   by it.
2. **The reader slows Qwen only while it reads.** The -43% was measured with the reader reading for the whole load, the worst case.
   Stream reads are bursts: at about 26k tokens/s a 2k-token tool result takes under 0.1 s.
3. **Qwen is the process that dies when memory runs out, not the reader.** vLLM allocates past its `GPU_UTIL` budget at run time; at 0.88
   the reader held 2,168 MiB and Qwen's engine died asking for 24 MiB with 4.94 MiB free (`torch.OutOfMemoryError`, then
   `EngineDeadError`). A resident reader must cap its own memory (`torch.cuda.set_per_process_memory_fraction`, the cache released after
   each read) so that it fails first, and must never hold its peak while idle.
4. **The budget model predicted Qwen exactly and the reader short.** SBS1's table (its report, section 7) gave 169,445 and 154,616 KV
   tokens (measured 169,622 and 154,973). For the reader it used G0's single-forward peaks; a chunked read that carries its state peaks
   higher (1,794 against 1,514 MiB at 4,096 tokens) and the process holds its reserved cache plus its CUDA context (2,168 MiB).

## For the owner (D-088: a permanent change is the owner's)

No change is needed now: the reader has no job yet (the G0 zero-shot probe found no signal; the student is not trained). When it has
one, the measured choice is Qwen at 0.90 (169,622 KV tokens) beside a reader capped near 1.5 GiB reading 1,024-token chunks, or keeping
the reader to GPU windows with no permanent cut.

## NOT measured

A reader capped by `set_per_process_memory_fraction`; long reads (the read covered 16,384 tokens); lanes' real prompts under the cut;
the cost of Triton compilation after a restart with a warm cache.
