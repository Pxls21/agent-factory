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

| Cell | Server config | Load | busy_slots | decode t/s (aggregate, metric) | end-to-end t/s | VRAM MiB |
|---|---|---|---:|---:|---:|---:|
| **A** | MTP n=3, `-np 1`, q4_0 (default) | 1 request | 1.000 | **45.27** | **33.10** | 21585 |
| **Aq** | MTP n=3, `-np 1`, q4_0 | 2 requests | 1.000 (serialized) | 52.13 | 23.45 | 21585 |
| **G2** | MTP n=3, `-np 2`, q4_0 | 2 concurrent | 1.920 | 21.94 | 7.80 | 21927 |
| **D2** | no-MTP, `-np 2`, q4_0 | 2 concurrent | 1.984 | 16.36 | 7.83 | 19791 |

Decision rule (from the plan): adopt `-np 2` only if aggregate decode ≥ 1.5× A (≥ 68 t/s).
- G2 (MTP + `-np 2`): 21.94 = **0.48× A → NO.**
- D2 (no-MTP + `-np 2`): 16.36 = **0.36× A → NO.**

**Verdict: on a single 3090, `-np 2` genuinely runs both lanes at once (busy_slots ≈ 2) but total
throughput HALVES or worse.** Two concurrent lanes deliver ~16–22 t/s combined vs 45 t/s for one
lane; each lane then runs at ~1/4 speed. Stacking two requests on the current `-np 1` is also worse
(Aq end-to-end 23.45 < A 33.10 — the 2nd request just queues). The single card's compute is SHARED
between slots, not added. MTP's win is a `-np 1` phenomenon; under `-np 2` it collapses (G2 ~11 t/s
per slot).

This VALIDATES the current default (MTP, one 262K slot) and the dispatcher's one-local-lane rule.
The "89 t/s" reference was a low-context figure; at a real ~85K lane context single-stream is
45 t/s decode / 33 t/s end-to-end (decode slows with the attention span). **The only way to run two
concurrent lanes at full speed is a second GPU** (the owner's pending decision — now answered).

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

- **Concurrency:** keep `-np 1` MTP as the default; do NOT enable `-np 2` on one card. Re-open only
  with a second GPU. (Cells D/D2/E/F/G decided against.)
- **Lossless levers:** **no change to `harness-ports/bin/qwen-server.sh` defaults.** The measured
  optimum IS the current unit (MTP n=3, `-np 1`, q4_0, `--cache-ram 8192`, default ubatch). Every
  tried lever either matched the default (cache-ram) or lost (ngram, ub 2048). The matrix's job was
  to find a real win or prove none exists at this scale; it proved none.
- **The bottleneck is the single 24 GB card**, not any server flag. The next real speed lever is
  hardware (a 2nd GPU) or a model-server upgrade (the DFlash/GDN A/B, gated, future).

- **Concurrency:** keep `-np 1` MTP as the default; do NOT enable `-np 2` on one card. Re-open only
  with a second GPU. (Cells D/D2/E/F/G decided against.)
- **Lossless levers:** pending the optimization sweep; any adopted change is written into
  `harness-ports/bin/qwen-server.sh` defaults with its measurement pasted here.
