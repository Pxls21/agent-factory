# RESEARCH-FINDINGS-1 — VERIFIED digest (lane throughput on the one RTX 3090)

**Status 2026-09-15 12:0xZ.** The owner returned two reports for `docs/research/prompts/RESEARCH-PROMPT-1.md` (filed verbatim,
unaudited: `RESEARCH-FINDINGS-1-part1-single-3090-recipe.md` — the ranked llama.cpp recipe; `…-part2-multi-agent-landscape.md` —
the multi-agent serving landscape). This digest checks every load-bearing claim against PRIMARY SOURCES on the owner's PC read this
session (the running server's log `~/qwen-builder/logs/server.log`, the binary's `--help`, the unit's `ExecStart`, the Hermes
source at `b3399c1`, `nvidia-smi`, `free`) and against our own measurements. It is the constraint set for what happens next.
Nothing here is adopted yet; every lever carries its accuracy tag and its gate.

## 1. What the PC says today (primary source, this session)

| Fact | Value | Source |
|---|---|---|
| Server | `llama-server`, `version: 1 (00139b6)`, mainline ggml-org/llama.cpp at 2026-06-24 (`ui: loading bar below the model picker (#24931)`; a 1-commit shallow clone — the `llama.cpp-mtp` directory name is the build dir, not a fork) | `git -C ~/Desktop/projects/llama-cpp/llama.cpp-mtp log -1` |
| Flags (unit) | `-ngl 99 -c 262144 -fa on -ctk q4_0 -ctv q4_0 -np 1 --cache-reuse 256 --spec-type draft-mtp --spec-draft-n-max 3 --jinja --chat-template-kwargs {"reasoning_effort":"<per lane role>"} --metrics --slots` | `systemctl --user cat qwen-builder` |
| Slots | ONE, `new slot, n_ctx = 262144` (the 2026-09-14 `-np 4` × 65K overflow decided this) | server.log, the last startup block |
| MTP draft context | `estimated memory usage of MTP context is 1348.02 MiB`; the DRAFT's KV is `cache_k=f16, cache_v=f16` regardless of `-ctk` | server.log |
| `--cache-reuse` | **`cache_reuse is not supported by this context, it will be disabled`** — the flag is INERT on this hybrid model | server.log |
| Prompt cache | `prompt cache is enabled, size limit: 8192 MiB` (`--cache-ram` default); live state `3 prompts, 7568.324 MiB (limits: 8192.000 MiB, 262144 tokens)`; a 91,614-token prompt = `total state size = 2121.391 MiB (draft: 359.615 MiB)`; a 40-token prompt = 150.487 MiB (the fixed recurrent state) | server.log |
| KV per token (q4_0) | (2121 − 360 − 150) MiB / 91,614 ≈ **17.6 KiB/token** → ≈ 4.5 GiB at 262,144; q8_0 ≈ 9 GiB; f16 ≈ 18 GiB | arithmetic on the lines above |
| GPU | 21,587 of 24,576 MiB used with the server + one live lane → ≈ 2.9 GiB free | `nvidia-smi` |
| RAM | 125 GiB total, 78 GiB available | `free -g` |
| Re-prefill tax (the last 20,000 log lines = the VERIFY-N5k lane's window) | 380 tasks; prompt tokens 4,373,729 (mean 11,510, max 98,452) in 5,815,650 ms = 752 t/s; **42 tasks > 50K tokens** (full re-processings; 64 `forcing full prompt re-processing due to lack of cache data (likely due to SWA or hybrid/recurrent memory)` warnings) and 271 tasks < 2K (served from the prompt cache); decode 475,313 tokens in 10,193,809 ms = **46.6 t/s**, mean 1,251 per task | server.log `print_timing` lines |
| Prefill share | 5,816 s / (5,816 + 10,194) s = **36 %** of the model's busy time in the verify lane's window (the prompt's 20 % was the whole-life average); the 42 full re-processings ≈ 87 % of the prefill work | same |
| MTP acceptance (server life) | `#gen tokens = 1,499,628, #acc tokens = 875,568` → 58.4 % of drafted tokens accepted; `#acc drafts 376,022 / #gen drafts 499,876` = 75.2 % | server.log `statistics draft-mtp` |
| Speculative types on this build | `none, draft-simple, draft-eagle3, draft-mtp, ngram-simple, ngram-map-k, ngram-map-k4v, ngram-mod, ngram-cache` — **no `draft-dflash`** | `llama-server --help` |
| Other flags present | `--spec-draft-p-min` (default 0.00), `-ctxcp/--ctx-checkpoints`, `-cms 8192`, `-kvu/--kv-unified`, `-ub` (default 512) | `--help` |
| Hermes profile | `compression.threshold: 0.5`, `protect_first_n: 3`, `protect_last_n: 20`; `file_read_max_chars` unset → `_DEFAULT_MAX_READ_CHARS = 100_000` (`tools/file_tools.py:47`); no `model.context_length` set — the window is live-resolved from the model catalog (`agent_init.py:161-171`, `_scope_context_length_to_default_runtime` :1602) | `~/.hermes/profiles/agentfactory/config.yaml`, the source |
| Effort mechanism | a per-request `reasoning_effort` is IGNORED by this build (measured 2026-09-14; Hermes `--reasoning` inert); the SERVER default via `--chat-template-kwargs` is what works, set per lane role by `scripts/pc_lane.sh` | `docs/research/FINDINGS-LOCAL-BUILDER-QWEN38.md` |
| The effort A/B so far | arm A `medium`: substantive completion 4 h 53 m, 386,202 output tokens, `113 passed`; arm B v3 `xhigh`: 6 h 41 m, 694,413 output tokens (1.8×), `119 passed` on its tree, 8 new tests; the comparative grade VERIFY-N5k is in flight on the local slot | the ledger |

## 2. The claims, checked

| # | Claim (report) | Verdict | Evidence |
|---|---|---|---|
| 1 | `reasoning_effort xhigh → medium` cuts ~1.8× output tokens (part 1 lever 1) | **CONSISTENT** on tokens (694k vs 386k = 1.8×); **accuracy PENDING** the oracle (VERIFY-N5k); the mechanism named (`chat_template_kwargs` per request) is **CONTRADICTED** on this build — the server default is the lever (already how the dispatcher sets it) | §1 rows Effort mechanism, A/B |
| 2 | `q4_0` KV costs 30–37 % decode at long context; move to `q8_0`, it fits because only 16/65 layers hold KV (lever 2) | decode penalty **UNVERIFIED** here (a matrix cell); the fit claim **CONTRADICTED at 262K**: q8_0 needs ≈ +4.5 GiB and ≈ 2.9 GiB is free — q8_0 fits only at ≈ 180K total context or less; the small per-token KV (17.6 KiB) is consistent with a 16-attention-layer hybrid | §1 KV per token, GPU |
| 3 | MTP and `-np > 1` do not compose; the non-MTP path scales aggregate throughput with `-np` (lever 4, the pivotal experiment) | **UNVERIFIED** — exactly the L1 matrix; we have no concurrent-throughput number of our own (the one `-np 4` run overflowed on context before any measurement) | the ledger 2026-09-14 |
| 4 | an external `--model-draft` is a net loss on this pairing | accepted as the report's reading; matches the prompt's rejected-alternatives list; no action | — |
| 5 | vLLM/SGLang/TensorRT-LLM do not rescue one 3090; keep llama.cpp (both parts agree) | accepted; the substrate stays as settled in the prompt | — |
| 6 | decode is bandwidth-bound (~65 t/s batch-1 ceiling; 44–87 observed) | **CONSISTENT**: 46.6 t/s effective in the verify window, 86.9 t/s peak on code at 90 % acceptance (2026-09-14) | §1 |
| 7 | prefix caching via `--cache-reuse` + a byte-stable prefix + `protect_first_n` (lever 7) | **PARTLY CONTRADICTED**: `--cache-reuse` is DISABLED by the server on this model; the working reuse is the whole-state prompt cache (`--cache-ram`), and it fails into a FULL re-prefill on 42 of 380 tasks. The actionable, lossless levers are (a) a larger `--cache-ram` (8192 → 32768 MiB; 78 GiB RAM available) so saved states survive alternation — mandatory for two lanes on one server, (b) measuring whether context checkpoints (`-ctxcp`, `-cms`) can turn a full re-prefill into a partial one on this build, (c) finding what makes Hermes's history non-append-only between turns (compression, the read-dedup stubs) — every rewrite of an earlier message busts the saved state | §1 re-prefill rows |
| 8 | `-ub` 768/1024/2048 sweep (lever 5) | **UNVERIFIED**, lossless; stage 2 of the matrix | `--help` shows `-ub` default 512 |
| 9 | upgrade llama.cpp for the GDN `rsqrt` fix and the checkpoint changes; `-cms` replaced older flags (lever 6) | **PARTLY VERIFIED**: the build is mainline at 2026-06-24, so a Sept-2026 GDN fix is NOT in it (an upgrade is output-changing → A/B gate); the flag claim is moot — this build already has `-cms` and `-ctxcp` | §1 Server, Other flags |
| 10 | Hermes trims: lower `file_read_max_chars`, cap `tool_output.max_bytes` (lever 3) | `file_read_max_chars` **VERIFIED** (default 100,000, unset in the profile); `tool_output.max_bytes` **NOT FOUND** under that name in `hermes_cli/config.py` (only an error-body cap in `bounded_response.py`) — the key must be located before it is cited; accuracy LOW; queued behind the A/B (one variable at a time) | §1 Hermes profile |
| 11 | compaction tuning (`threshold`, `protect_*`) | keys **VERIFIED**; our earlier read: the threshold is floored at 0.75 for windows < 512K; VERIFY-N5k compressed once (message count 436 → 189) and the lane continued | the source, state.db |
| 12 | DFlash 2.5–3.4× single-stream on a 3090 (part 2) | **CONTRADICTED for this binary** (no `draft-dflash`); **POSSIBLE via lucebox** (checked 2026-09-15 12:1xZ on github.com/Luce-Org/lucebox + lucebox-hub: Apache-2.0; a trained DFlash2 draft exists for OUR exact model — `incoai/Qwen3.8-27B-DFlash2`, shipped as `qwen38-dflash2-q8_0.gguf`; UD-IQ4_XS is among the quants it lists; CUDA 12+; PFlash is "lossy prompt compression … keep it off for exact-retrieval" — never for our lanes; its multi-client numbers are on an AMD R9700, its 3090 numbers on this page are for a different 33B model, so OUR number does not exist yet); lucebox describes itself as its own speculative inference server, so whether it exposes the llama-server flag surface the matrix runner drives is UNVERIFIED — a matrix cell I only after A–H have a baseline, behind the A/B gate; the "numerically safe at greedy" claim presumes greedy sampling — our lanes' sampling settings are not pinned (a precondition to state before any DFlash trial) | `--help`; the two GitHub pages |
| 13 | optillm (best-of-N / MoA) as an opt-in accuracy lane (part 2) | out of scope for throughput; a council item because it adds a proxy inside the egress path (rule 3: OmniRoute is the sole egress — any proxy sits behind it on loopback) and multiplies tokens | STANDING PROJECT RULES |
| 14 | a second GPU is the clean route to two independent full-context lanes (both parts) | **OWNER DECISION** — hardware; both reports rank it above every single-card lever for the 2-lane goal; not for the coordinator to assume | — |

## 3. What this changes in the plan

1. **The prefill tax is a first-class target the prompt under-weighted.** In the verify lane's window prefill is 36 % of busy time and 87 %
   of it comes from 42 full re-prefills of ~90K tokens (≈ 120 s each at 752 t/s). Two lossless levers attack it before any accuracy question:
   `--cache-ram 32768` (RAM is there) and the checkpoint mechanism (`-ctxcp`/`-cms`, measured, not assumed). Both go into the matrix.
2. **q8_0 KV is a context trade, not a free win.** It fits at ≈ 180K total, not 262K. The matrix measures q4_0 vs q8_0 at the context the
   lanes actually use (the N5k arms peaked near 100K; the verify lane's max prompt 98,452) — a 2 × 90K q8_0 configuration is a real cell.
3. **The MTP-vs-`-np` fork is the pivotal cell** and we have no number for it. The decision rule from the report stands: adopt `-np 2` without
   MTP only if its aggregate decode for two concurrent lane-shaped requests is ≥ 1.5× MTP single-stream; else keep MTP `-np 1` and serialize.
4. **`-np 2` has a Hermes precondition:** each local lane must believe the window is the SLOT size (131K), or it overflows the slot exactly as
   the 2026-09-14 `-np 4` run did. Hermes live-resolves the window from the model catalog (no `context_length` in the profile); the clean
   seam is a per-slot-size model alias advertised by OmniRoute (e.g. a `qwen-local-131k` combo) — the load-generator lane names the exact seam.
5. **Effort stays `medium` provisionally** (D-028) until VERIFY-N5k grades arm A against arm B; the council on adopting it as the default,
   on the Hermes trims and on any build upgrade runs AFTER that verdict (it is the oracle's input).
6. **DFlash and the GDN fix both live behind an upgrade** of the model server — output-changing, so an A/B on the N5k brief per the prompt's
   guard; not before the matrix has a baseline on the current build.

## 4. The L1 matrix (protocol; runs when the local slot is free — no live lane during server restarts)

Load: a replay generator sends N concurrent chat completions built from the exported lane transcripts (`~/qwen-builder/ab/n5k-*.md`, 62–218 KB
each) trimmed to lane-shaped prompts (~100K tokens) with 1,000-token generations, reads `/metrics` before and after, and prints per cell:
aggregate decode t/s, prompt t/s, `n_busy_slots_per_decode`, the count of `forcing full prompt re-processing` lines, VRAM peak, and the exact
server flags. Cells (one variable at a time from A):

| Cell | Server | Concurrency | Measures |
|---|---|---|---|
| A (baseline) | current unit flags (MTP n=3, `-np 1`, q4_0, 262K, cache-ram 8192) | 1, then 2 queued | the baseline single-stream decode + the queueing cost |
| B | A + `--cache-ram 32768` | 2 alternating | the re-prefill count with two saved states |
| C | A + `-ctxcp 32 -cms 4096` | 1 with a rewritten mid-history turn | whether checkpoints turn a full re-prefill into a partial one |
| D | no MTP, `-np 2` (2 × 131K), q4_0 | 2 concurrent | aggregate decode vs A (the ≥ 1.5× rule) |
| E | D with `-ctk q8_0 -ctv q8_0 -c 180224` (2 × 90K) | 2 concurrent | the q8_0 decode gain at the real context, and the fit |
| F | D + `--spec-type ngram-mod` | 2 concurrent | the shared-pool speculation under slots |
| G | MTP n=3 + `-np 2` | 2 concurrent | the report's "does not stack" claim, measured |
| H | the winner + `-ub 1024`, then 2048 | 2 concurrent | the prefill gain, the OOM edge |
| I (later) | lucebox + the `Qwen3.8-27B-DFlash2` q8_0 draft on our GGUF, greedy pinned, PFlash OFF | 1, then 2 | DFlash vs MTP on OUR model and card (no published number exists); only if lucebox can be driven by the runner or a runner is written for it; adoption = provenance audit + digest pin (rule 13) + the A/B gate |

Decision rules: adopt D/E/F only at ≥ 1.5× aggregate over A for two lanes; adopt B/C on any reduction of full re-prefills at equal accuracy
(lossless); adopt H on prompt t/s without OOM at the max prompt; every adopted server change is written into `harness-ports/bin/qwen-server.sh`
defaults with its measurement pasted, and the dispatcher's one-lane rule is lifted only for the measured slot count.

## 5. Owner decisions (yours, not mine)

1. **A second GPU.** Both reports say it is the clean route to two independent 2–3 h lanes; the single-card ceiling is ~2–2.5× on inference plus
   the workload-side wins. Say yes or no; the matrix runs either way.
2. **Restart windows for the model unit.** The matrix restarts `qwen-builder` per cell (≈ 10 s to load) — it runs only with no live local lane;
   I will not restart under VERIFY-N5k.
3. **The Hermes-side trims** (read cap, output cap, compaction) change lane behaviour; they wait for the A/B to close so the oracle reads one
   variable at a time. Say if you want them sooner.

## 6. NOT done here

**The six repositories the owner named (checked 2026-09-15 12:1xZ against their GitHub pages; one verdict each against OUR bottleneck — decode 80 %, the full re-prefills, one 24 GB card, llama.cpp + GGUF, OmniRoute the sole egress):** lucebox — the only one that attacks decode on this card with a draft trained for our exact model; cell I above, after the baseline, behind the gate. flashtensors — model loading/hot-swap for vLLM only (no llama.cpp integration yet); our one model is resident and loads in 6.6 s; no. oLLM — SSD-streamed weights/KV at "1 tok/2 s" on an 8 GB card, no batching, no GGUF; the opposite of our need; no. ovllm — a Python wrapper around vLLM for DSPy; we run neither; no. optillm — an OpenAI-compatible proxy that spends N× tokens per answer (best-of-N, MoA, self-consistency) on a GPU that is already the bottleneck; it changes outputs and would sit inside the request path (behind OmniRoute on loopback if ever), and its selection is a voting/verification judge that can never enter the gate spine — a council item for the verify lane on a second GPU at most; not now. LMCache — a KV layer for vLLM (a daemon; no llama.cpp path); on llama.cpp the same lever is the built-in prompt cache (`--cache-ram`, cell B) and the hybrid recurrent state defeats block-level reuse anyway; no.

The matrix itself (the local slot is busy), the council (needs the oracle's verdict), the `tool_output` cap key's real name, the
DFlash/GDN upgrade trial, the second-GPU question. The council, when it runs, debates THIS digest plus VERIFY-N5k's report, not the prompts.
