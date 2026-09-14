# FINDINGS — a local Qwen3.8-27B as the BUILD-lane model (validation of the owner's brief, 2026-09-14)

**Verdict first.** The idea holds; the brief's numbers mostly do not. Qwen3.8-27B is real (released 2026-08-14, Apache-2.0, 27B dense,
hybrid attention, an MTP head, 262k native context). On the owner's RTX 3090 the WHOLE model plus a FULL 262,144-token q4_0 KV cache fits
on the GPU with about 6 GiB to spare, so the brief's central move (offload ten layers to RAM to make room) is unnecessary and would cost
roughly 3.7× decode speed on this DDR4 box. Two of the brief's flags do not exist as written, the default port is wrong, and the
"medium = 98% of xhigh at 1/20th the time" claim is refuted by every measured source found (the measured ratios are ~95% of the quality at
1/2 to 1/7 of the thinking). "Better than Opus for surgical edits" has no measured basis anywhere; the vendor's own table is mixed against
Opus 4.6 and behind Opus 5 on the two comparable rows. What the model does buy is real: free, unlimited, on-site build lanes at ~40 t/s,
a second model family in the loop, and a plausible bug-finder. Whether it builds OUR lanes well is not on the internet — it is measured
here, on the PC, against briefs whose verifier verdicts we already hold. The evidence pack with every source is beside this file:
`docs/research/evidence/qwen38-local-builder-evidence-2026-09-14.md` (56 rows, every number sourced; Reddit was unreachable, so three of
the brief's Reddit threads could not be verified at all and are marked as such).

## 1. The one fact that changes the math

From the official `config.json`: 64 layers, of which only **16 are full attention** (4 KV heads × head_dim 256); the other 48 are
Gated-DeltaNet linear-attention layers with a fixed recurrent state (~150 MB per slot) that does not grow with context.

| KV cache (16 layers) | bytes/token | at 262,144 tokens |
|---|---|---|
| f16 | 65,536 | 16.0 GiB |
| q8_0 | 34,816 | 8.5 GiB |
| q4_0 (the brief's choice) | 18,432 | **4.5 GiB** |

Weights UD-IQ4_XS 14.3 GB (13.3 GiB) + q4_0 KV at 262k 4.5 GiB + state 0.15 GiB = **18.0 GiB of 24.0** — fully resident, ~6 GiB free.
An independent RTX 4090 (also 24 GB) measurement confirms the ordering (f16 KV tops out ~100k, q8 ~170k, q4_0 the full 262k). The brief's
`--ngl 54` is therefore not motivated by memory. Its cost: ten layers read from DDR4 (51.2 GB/s theoretical, AM4 is DDR4-only) each token →
a ceiling of ~15-18 t/s instead of ~50-65 t/s (measured baselines for this class on a 3090: ~40 t/s).

## 2. What the brief gets wrong (each row is sourced in the evidence pack)

1. `--spec-draft-max 2` does not exist; the flag is `--spec-draft-n-max 2` (C6.15). `--spec-type draft-MTP` is spelled `draft-mtp` (C6.14).
2. `--flash-attn` now takes a value: `-fa on` (default `auto`); whether the bare form parses is unverified (C6.10-11).
3. llama-server binds `127.0.0.1:8080` by default; "port 8000" is vLLM's (C11.1-2). No tunnel is needed or wanted: OmniRoute is the sole
   model egress (project rule 3) and it runs on the same host.
4. "medium ≈ 98% of xhigh at 1/20th the thinking": the only measured quality table gives medium 8.18 vs xhigh 8.61 = **95%** (one run,
   noise 0.18); thinking tokens medium ≈ **1/6.7** of xhigh (3 seeds), wall clock 1/5.6, median latency 1/1.9. The 7-11× figure that exists is
   LOW vs xhigh (C4.4-C4.10). xhigh wins on coding substance; the vendor warns lower effort can COST time in multi-turn agent work because it
   spends more rounds, and one source measured low as slower than medium for that reason (C4.11-13). Levels are low/medium/xhigh only — the
   model's template rejects `high` (C1.14).
5. "performs better than Opus for surgical edits": no Aider-polyglot entry, no edit-format measurement of any kind exists for this model
   (C3.15). Vendor table vs Opus 4.6 Max: Terminal-Bench 2.1 73.0 vs 78.2 (Opus ahead), SWE-bench Pro 61.7 vs 53.4 (Qwen ahead), NL2Repo
   42.3 vs 47.6 (Opus ahead), LiveCodeBench 90.3 vs 88.8; the Opus column is the official score while every other column was re-run in a
   Claude Code harness (C3.2-C3.9). Against Opus 5 (secondary numbers only) Opus leads both comparable rows (C3.14).
6. "identity crisis (claims to be Claude)": the cited thread could not be fetched and nothing corroborates it (C5b.1).
7. "keen to execute git commands": real, but the source says it of Qwen3.6 AND 3.8 alike (C5a.2-3). Our lanes already run in a private
   worktree and cannot push; the harvest is the lane's diff, so a stray local commit is harmless. One line goes into the role prompt anyway.
8. "Flash-Next faster but dumber": the vendor table has Flash-Next ahead on all eleven shared benchmarks; one community report supports the
   brief's direction on long sessions. Moot here: Flash-Next is ~180B and needs four 3090s (C5c.4-6).
9. "2-5 t/s with a 200k host-side KV": unsourced; the arithmetic bracket is 3.3-13.9 t/s depending on which bus binds (C8.11).
10. `--threads 12`: no primary guidance exists; the box has 6 physical cores. A measurement item, and moot once nothing is offloaded.

## 3. What the brief gets right

The model, the quant (UD-IQ4_XS 14.3 GB, MTP head included — Unsloth strips MTP only below UD-Q2_K_XL), q4_0/q4_0 KV (in the default
CUDA flash-attention kernel set — other quant pairs silently fall back to CPU attention with a ~7× collapse, C6.7-9), `--chat-template-kwargs
'{"reasoning_effort":"medium"}'` (Unsloth's own syntax; `--reasoning-effort medium` also exists on master), draft depth 2 for MTP (Unsloth's
instruction; a vLLM sweep found k=2 the best ratio at 71% acceptance), 128 GB RAM as headroom (irrelevant to VRAM, useful for nothing here
unless we offload, which we should not).

## 4. What is on the PC today

- `/usr/local/bin/llama-server` is the prebuilt **b8184 (March 2026), CPU-only** — it lists no CUDA device. The newer b8631 tarball is
  also CPU-only: the Linux release assets carry no CUDA build at all (C13.1-4). Both predate the model (2026-08-14) and the MTP merge
  (2026-05-16).
- A **CUDA build of upstream master 00139b6 (2026-06-24)** sits at `~/Desktop/projects/llama-cpp/llama.cpp-mtp/build/bin/` — it sees
  `CUDA0: NVIDIA GeForce RTX 3090 (24122 MiB)` and has `--spec-type draft-mtp`, `--chat-template-kwargs`, `--reasoning-budget`, `-np`,
  `--cache-reuse`, `--api-key`. It postdates the MTP merge and the `qwen3_5` architecture, so it should load the 3.8 GGUF; that is the
  first measurement, not an assumption. `nvcc` is absent, so a newer CUDA build needs the CUDA toolkit installed (owner, sudo) or the
  official container `ghcr.io/ggml-org/llama.cpp:server-cuda` under podman with a CDI spec (`/etc/cdi` is empty today; `nvidia-ctk cdi
  generate` needs sudo).
- Ryzen 5 5600X (6c/12t, DDR4 only), 125 GB RAM, the 3090 idle (246 MiB used), 675 GB free on /home, the HF cache already holds four
  Qwen3.6-27B INT4 quants. The Qwen3.8-27B UD-IQ4_XS download (14.3 GB) was started 2026-09-14 12:1xZ into that cache.
- Ollama 0.19 is installed but is the wrong host for this: it replaces the model's chat template and cannot set `reasoning_effort`
  (C10.14-15).

## 5. The corrected command (a draft to be measured, not a recommendation yet)

```
~/Desktop/projects/llama-cpp/llama.cpp-mtp/build/bin/llama-server \
  -m ~/.cache/huggingface/hub/models--unsloth--Qwen3.8-27B-GGUF/snapshots/<rev>/Qwen3.8-27B-UD-IQ4_XS.gguf \
  --host 127.0.0.1 --port 8080 --api-key-file <a file only OmniRoute reads> \
  -ngl all -c 262144 -fa on -ctk q4_0 -ctv q4_0 \
  --alias qwen3.8-27b-local -np 4 --cache-reuse 256 \
  --spec-type draft-mtp --spec-draft-n-max 3 \
  --jinja --chat-template-kwargs '{"reasoning_effort":"medium"}' \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0
```

Why each line: everything on the GPU (§1); the context the model natively supports; the KV pair that has a CUDA kernel; two server slots
(the KV budget at 262k holds two full sessions or five 100k ones — `-np` DIVIDES the context between slots, so the per-slot figure must be
read from `/slots` at startup, C10.1-3); MTP as Unsloth instructs; Unsloth's thinking-mode sampling. `-np` and the effort level are the two
knobs the measurements decide.

## 6. What only a measurement settles (the plan)

1. Load test: the June CUDA build loads the GGUF and answers one prompt (rc 0, the served model name, tokens in/out).
2. `llama-bench`-style decode at 4k / 64k / 262k context, fully resident vs `-ngl 54`, q4_0 vs f16 KV — the ceilings in §1 vs reality; a
   collapse on q4_0/q4_0 is the CPU-fallback signature.
3. MTP acceptance rate and speedup on THIS card for THIS model (every published 3090 MTP number is Qwen3.6 or vLLM).
4. Slot division under `-np 2` and `-np 4` (the startup log's per-slot context), then two and four concurrent lane-shaped requests.
5. The effort A/B that matters — AS RUN (2026-09-14 16:5xZ, owner: "one test … compared to max … if the output quality is better or medium's is not
   good enough, switch"): ONE brief, TWO arms, ONE grader. Arm A = lane N5k on `agentfactory-build-local` at `medium` (the live lane,
   dispatched 15:5xZ); arm B = the same brief on the same PIN in a fresh tree at `xhigh` (`tasks/briefs/pc/pc-n5k-xhigh.md`), dispatched
   when arm A lands; then ONE comparative verify lane on `agentfactory-verify-local` grades both reports against the brief's own gates
   (items closed, the red tests that went green, mutants killed, discrepancies stated, false claims) plus wall clock and tokens. "Max" for
   this model IS `xhigh`: the Qwen3.8 chat template accepts only `xhigh` (default), `medium`, `low` (`high` → `xhigh`; anything
   else raises). Decision rule: `xhigh` becomes the build default if arm B closes more of the brief, or arm A's report is NOT-READY on
   blockers arm B avoided; otherwise `medium` stays and `xhigh` remains the per-brief override. Mechanism note: Hermes sends
   `extra_body.reasoning={"effort": …}` on this wire; whether that reaches the template through OmniRoute is measured by the probe
   `~/qwen-builder/probes/` on the PC (results recorded here when they land) — if it does not, arm B's effort is set at the server
   (`QWEN_EFFORT=xhigh`, a unit restart between arms, never under a live lane), and the dispatch note names the mechanism used.
6. Effective DDR4 bandwidth (a STREAM run) — only if any offload is ever considered.

### §6 measured — 2026-09-14 12:52-12:58Z, the June CUDA build `00139b6`, the 3090, one coding prompt at temperature 0

Step 1, the load test: PASSED. The download completed (blob 14,252,845,984 bytes, sha256 `40fac405…`, snapshot `4ca72078`); the June
build loaded the UD-IQ4_XS fully resident and answered `/health` in ~6 s from page cache; the first prompt (`reasoning_effort: medium`
through `chat_template_kwargs`) returned a correct iterative `fib` with a doctest, the thinking split by the template (596 reasoning
chars / 184 content chars), 36 prompt tokens at 102.9 t/s, 300 generated at 44.2 t/s, `finish_reason: stop`, GPU 98 % during decode.
The served model id is the GGUF path (`--alias` names it for OmniRoute).

Steps 2-4, the matrix (`~/qwen38-probe/matrix.sh` on the PC; rows in `docs/research/evidence/qwen38-matrix-2026-09-14.jsonl`; every
case the same 36-token fib prompt at temperature 0 with `max_tokens 400`; every case produced the SAME 305 tokens — content sha `6b7c01ad`
— so MTP is lossless here and the rows are comparable):

| case | server args beyond `-ngl 99 -fa on --jinja` | VRAM MiB | prompt t/s | decode t/s | MTP draft / accepted |
|---|---|---|---|---|---|
| base | `-c 32768 -ctk q4_0 -ctv q4_0 -np 1` | 14,586 | 119.4 | 44.28 | — |
| kv-f16 | `-c 32768 -np 1` (f16 KV) | 15,972 | 119.5 | 44.67 | — |
| ngl54 (the brief's offload) | `-ngl 54 -c 32768 -ctk q4_0 -ctv q4_0` | 12,436 | 33.9 | **6.32** | — |
| mtp-n2 | base + `--spec-type draft-mtp --spec-draft-n-max 2` | 15,154 | 98.0 | **79.92** | 212 / 200 (94.3 %) |
| mtp-n3 | base + `--spec-type draft-mtp --spec-draft-n-max 3` | 15,304 | 97.8 | **86.93** | 246 / 222 (90.2 %) |
| ctx262k | `-c 262144 -ctk q4_0 -ctv q4_0 -np 1` | 19,738 | 119.4 | 44.11 | — |
| ctx262k-np2 | the same, `-np 2` → 131,072 per slot | 19,760 | 119.4 | 43.95 | — |
| ctx262k-np4 | the same, `-np 4` → 65,536 per slot | 19,996 | 119.9 | 44.06 | — |

What the table settles: (1) the brief's `--ngl 54` offload is **7.0× slower** than resident (6.3 vs 44.3 t/s) — worse than §1's
estimate, and it saves only 2.1 GiB that nothing needs; (2) MTP is the real lever on this card: **~1.8× at n=2, ~2.0× at n=3** with
90-94 % acceptance on code, lossless at temperature 0 — the builder decodes at ~87 t/s; (3) the full 262k q4_0 KV FITS resident at
19.7 GiB used (4.6 GiB spare, not §1's ~6), and `-np 4` costs 0.26 GiB more with 65k of context per slot — four concurrent build lanes
at 65k each, or two at 131k, are the shapes; (4) f16 KV buys nothing at 32k (+1.4 GiB, +0.4 t/s) and cannot fit at 262k; (5) the 32k
and 262k servers decode identically on a short prompt — the per-token cost of the hybrid attention at a FILLED long context is the one
number still pending: the first long-prompt cases failed before reaching the server (a ~400 KB request body passed on curl's command
line — the argv limit, the harness's bug, not the model's) re-run from a file (`matrix2.sh`): a **67,250-token** prompt prefills at **1,007.5 t/s** (66.7 s) and then decodes at
**28.87 t/s** with the context filled (row `long60k`; `finish: length` at 200 tokens, the model still thinking) — the hybrid
attention's long-context cost is −35 % against the short-prompt 44.3 t/s, far from the collapse a dense-attention 27B would show at
67k on this card; with MTP n=3 the same 67k case decodes at **59.51 t/s** (170 drafted / 142 accepted, 83.5 %; VRAM 21,546 MiB; row `long60k-mtp`) —
2.06× over the non-MTP long case, so a build lane at a filled 67k context still gets ~60 t/s. (The evidence file carries twelve rows:
the first matrix's ten, including the two argv-limit failures as the record of that failure, then the two re-runs.)
Not measured: the effort A/B on real briefs (§6 step 5 — it needs the OmniRoute provider, §8), the DDR4 bandwidth (moot: no offload).


## 7. Integration shape (behind OmniRoute, nothing else changes)

- llama-server stays on localhost with an API key; OmniRoute gains an OpenAI-compatible provider pointing at `http://127.0.0.1:8080/v1`
  (the owner adds it exactly as `s0-01-scripted` was added on 2026-09-04); the model id it exposes becomes the FIRST member of a new combo
  `agentfactory-build-local` (local first, the present cloud chain as the fallback), or is promoted inside `agentfactory-build` once the
  measurements pass.
- `harness-ports/bin/pc-lane.sh`'s role→route table gets the combo name for `code-implementer`; the verify lanes stay on
  `agentfactory-verify` (Opus/terra-class reasoning is what a grade needs); the coordinator's final verification stays here.
- The role prompt gains one line: no git write commands — edit the worktree, run the tests, write the report; the coordinator commits.
- Concurrency: two to four local build lanes (the KV budget), not seven; the cloud chain keeps serving the rest when quota allows.
- The usage record every lane already writes (`usage.json`) names the served model, so a lane report can never hide which route built it.

## 8. Decisions that are the owner's

1. The CUDA build path — ANSWERED by the measurement: the June build loads and serves the model with MTP and the full 262k KV, so it
   is the builder host for now; a newer CUDA build (the toolkit, or the `server-cuda` container + CDI) is an optimisation to schedule,
   not a prerequisite.
2. The OmniRoute provider + combo — ANSWERED by the build (2026-09-14 15:4xZ; owner: "if it can be done just build it"): node `qwen-local` + connection + combo `agentfactory-build-local` created by `harness-ports/bin/omniroute_local_builder.py ensure` with the installed CLI's machine-bound loopback token — no owner step; the server itself is user unit `qwen-builder` (`harness-ports/bin/qwen-server.sh`); §7's shape, live.
3. Whether the local model builds at `medium` by default — PROVISIONALLY `medium` (the measured default in `pc-lane.sh` since 2026-09-14 15:4xZ; §6 step 5's A/B is the FIRST lane's verify verdict — N5k, dispatched on the local route the same afternoon; `HERMES_REASONING=xhigh` per lane until then if a brief needs it).

Nothing in this document is a claim that the local builder works for our lanes. That claim is minted by §6, or not at all.
