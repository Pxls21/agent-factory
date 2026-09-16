# L1 throughput matrix — RESULTS (2026-09-16)

Live measurements on the owner's single RTX 3090, Qwen3.8-27B UD-IQ4_XS on the June CUDA
llama.cpp-mtp build, server effort `medium`. Companion to the plan + cell table in
`RESEARCH-FINDINGS-1-VERIFIED.md` §4. Runner: `harness-ports/bin/qwen-matrix.sh` +
`qwen_matrix.py` (VERIFY-QM1-d MERGE-READY). Every number below is pasted from the cell
`result.json` summaries, not typed.

## Method + one corpus fix (AF-AP-90)

Load = replay prompts built from an exported lane transcript (`n5k-armA`, ~101K tokens),
trimmed to lane-shaped prefixes, 1000-token generations, `/metrics` read before/after.

**Cell A's first live run exposed a real defect in the corpus builder.** `build_corpus` truncated
the transcript at an ASSISTANT boundary, so the chat/completions generation prompt asked the model
to speak AFTER a complete assistant turn — greedy decode emitted end-of-turn at once (1 token,
`predicted_seconds` 0). The round guard `metrics delta predicted seconds must be positive` fired and
the runner wrote `run-error` with no `result.json` (the QM1-d completion boundary working; a red
first pass is the good outcome — anti-hollow-green tactic 6). A short "pong" completion moved the
same counter +0.53, proving the metric sound: the corpus was wrong, not the instrument. **Fixed
(7da1518):** `build_corpus` ends replay prompts at a USER/TOOL boundary (a real assistant
generation). AF-AP-90 registered.

Two prompts, both ending at a user turn: `prompt-001` = 85,001 tokens, `prompt-002` = 60,584 tokens.

## Concurrency — the owner's question (does `-np 2` match speeds?)

Each concurrency cell ran two SYMMETRIC full-length (1000-token) generations at ~85K context.
`busy_slots` = llama.cpp `n_busy_slots_per_decode` (≈2 ⇒ both slots genuinely concurrent). The
`metric` decode t/s is prefill-independent; the end-to-end t/s = total tokens / round wall time.

> **CORRECTION (2026-09-16, later the same day, after owner pushback).** The verdict first written
> here — "`-np 2` halves throughput, buy a 2nd GPU" — was **WRONG**. It was confounded twice: (1)
> these cells ran at an 85K context, so a large COLD prefill dominated the end-to-end wall and
> masked the decode; (2) the number I labelled "aggregate decode t/s" is actually the **per-request**
> rate (the llama.cpp metric counter sums per-slot seconds), so ~16–22 is *one* lane's rate under
> sharing, not the combined rate. A clean re-measure (below) shows concurrency **HELPS**. The
> confounded cells are kept for the record; the clean test is the authority.

**CONFOUNDED cells** (85K context, prefill-dominated wall, per-request rate mislabelled "aggregate"):

| Cell | Server config | Load | busy_slots | per-req decode t/s | end-to-end t/s (incl. prefill) |
|---|---|---|---:|---:|---:|
| A | MTP n=3, `-np 1`, q4_0 | 1 req | 1.000 | 45.27 | 33.10 |
| Aq | MTP n=3, `-np 1`, q4_0 | 2 req | 1.000 (serial) | 52.13 | 23.45 |
| G2 | MTP n=3, `-np 2`, q4_0 | 2 concurrent | 1.920 | 21.94 | 7.80 |
| D2 | no-MTP, `-np 2`, q4_0 | 2 concurrent | 1.984 | 16.36 | 7.83 |

### Clean re-measure (2026-09-16) — the authority

Short "quick job" prompt (prefill ~0.1 s, so it isolates DECODE), warm, 500-token generations,
reading each request's own `timings.predicted_per_second` and the concurrent wall. Aggregate =
total tokens decoded / wall.

| Setup | Chats | Aggregate t/s | Per-chat t/s |
|---|---:|---:|---:|
| MTP, `-np 1` | 1 | **62.4** | 65 |
| MTP, `-np 1` | 4 (serial/queued) | 64.2 | 65 each, one at a time |
| MTP, `-np 2` | 2 (batched) | 60.1 | 30.9 each |
| **no-MTP, `-np 2`** | **2 (batched)** | **70.6** | 36.3 each, concurrent |
| **no-MTP, `-np 4`** | **4 (batched)** | **93.0** | 25 each, concurrent |
| MTP, `-np 4` | 4 (batched) | 62.4 | 16 each |
| no-MTP, `-np 4` | 1 | 42.6 | 44 |

Source logs (PC): `run-conctest.log` (np1/np4), `run-np2test.log` (MTP-np2 60.1), `run-np2b.log`
(no-MTP-np2 70.6). **no-MTP aggregate scales monotonically with slot count: 62 → 70.6 → 93** as
slots go 1 → 2 → 4; MTP does NOT (60.1 at np2, 62.4 at np4 — no gain over single-stream).

**Corrected verdict: concurrency HELPS.** 4 batched chats (no-MTP `-np 4`) do **93 t/s combined vs
64 serial** — ~1.45× more total throughput on the one card. llama.cpp's continuous batching works.
Two findings fall out:
1. **Throughput-vs-latency trade.** One chat with MTP is fastest per-chat (62 t/s); four batched is
   more TOTAL work (93 t/s) but each chat is slower (~25 t/s). For fire-and-forget build lanes,
   total throughput wins.
2. **MTP does NOT stack with batching on this build.** MTP `-np 4` collapses to 62 (16 t/s/chat) —
   the speculative draft/verify overhead doesn't parallelize. So concurrency ⇒ drop MTP:
   **fast-single (MTP `-np 1`, 62) OR high-concurrent (no-MTP `-np N`, 93 at N=4)**, not both.

The `-np 1` MTP default is right for running lanes ONE AT A TIME (fastest per-lane). To run several
lanes at once, no-MTP `-np N` is the win — a 2nd GPU is NOT required for concurrency (it would raise
the ceiling further, but the one card already gains ~1.45× from batching 4-up). The "89 t/s"
reference was a low-context figure; at short/quick-job context single-stream MTP is ~62 t/s, at a
real ~85K lane context ~45 t/s (decode slows with the attention span).

> **Incident during the run (AF-AP-91).** The concurrency probes restarted `qwen-builder` ~7× by
> hand in a few minutes; the unit's `StartLimitBurst=3` / `StartLimitIntervalSec=5min` tripped, so
> np2b's `restore -np 1` step logged `restart qwen-builder failed 5` and left the unit `failed`
> (server DOWN). Recovered with `systemctl --user reset-failed qwen-builder && … start`; confirmed
> healthy on the `-np 1` MTP baseline. Any restart-per-iteration probe needs `reset-failed` between
> restarts (or a wider burst limit), and the restore step must treat `failed N` as a server-down
> finding, not a log line.

## Lossless single-lane levers (cache-ram, ngram vs MTP, prefill ubatch)

All at the winning `-np 1` config. Bb/B alternate the two prompts over 4 rounds (the re-prefill
test — a big cache should avoid full re-processing on a revisited state). Fs/H are single-stream.

| Cell | Lever | decode t/s | prompt t/s | re_prefills | VRAM MiB | Verdict |
|---|---|---:|---:|---:|---:|---|
| **Bb** | baseline (cache-ram 8192), 4 rounds alt | 51.92 | 752.7 | **0** | 21585 | re-prefill baseline |
| **B** | cache-ram 32768, 4 rounds alt | 51.88 | 750.4 | **0** | 21585 | **no gain** — 8192 already holds both states |
| **Fs** | `--spec-type ngram-mod` (vs MTP) | **25.96** | 882.5 | 0 | 19767 | **reject** — 0.57× MTP decode |
| **H** | `-ub 2048` | 46.78 | 825.5 | 0 | **23615** | **reject** — no prefill gain, +2 GB VRAM (~960 MiB from OOM) |

**No lossless lever beats the default.** The prompt cache already avoids re-prefills for two
lane-shaped states at the default `--cache-ram 8192` (Bb and B both 0). ngram speculation is far
weaker than the trained MTP draft head. A bigger prefill ubatch buys no throughput here and pushes
VRAM to the edge of the 24 GB card.

NOT run: **C** (`-ctxcp/-cms` checkpoints) needs an edited-mid-history workload to show its benefit,
and the baseline re-prefill is already 0, so there is nothing for it to save at this scale; **E**
(q8_0 KV) is a context trade that fits ~180K, but `-np 1` already carries the full 262K at q4_0, so
q8_0 only costs decode speed with no context to gain. Both are deferred, not adopted.

## Decisions

- **Concurrency (CORRECTED):** llama.cpp DOES batch — 4 concurrent no-MTP chats = 93 t/s aggregate
  vs 64 serial (~1.45×). To run several lanes at once, use no-MTP `-np N` (drop MTP under batching).
  A 2nd GPU is NOT required for concurrency; it would raise the ceiling but the one card already
  gains from batching.
  - **Context-per-slot constraint:** `-np N` splits the 262K context into 262K/N per slot. `-np 4`
    = 65K/slot (build lanes grow past that — overflow). `-np 2` = 131K/slot (fits real lanes). The
    DEPLOYABLE concurrent config for build lanes is `-np 2` no-MTP — **70.6 t/s aggregate, two lanes
    at 36 t/s each** (`run-np2b.log`), a +13% aggregate gain over single-stream while each lane runs
    at ~55% of a solo lane's rate. It needs the Hermes-side window cap noted in
    `RESEARCH-FINDINGS-1-VERIFIED.md` §4 (each lane must believe its window is the slot size), or
    lanes overflow exactly as the `-np 4` N5k run did.
- **Single-lane speed:** MTP `-np 1` is fastest for ONE lane (62 t/s short context, 45 at 85K).
  Keep it as the default while lanes run one at a time.
- **Lossless levers:** **no change to the `-np 1` defaults.** cache-ram 32768 matched the default,
  ngram and ub 2048 lost (see §Lossless).
- **vLLM:** the real upgrade for high concurrency. Its paged-attention batching beats llama.cpp's
  AND its speculative decoding (EAGLE-style) stacks with batching — removing the MTP-vs-batch trade.
  It sits behind OmniRoute like llama.cpp does now (no egress-rule conflict) but is a re-decision of
  the 2026-09-03 "no vLLM" call and likely a different quant (AWQ/GPTQ/FP8, not this GGUF). If
  concurrent lanes matter, the data says vLLM is worth the switch.
