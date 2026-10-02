# SGLANG-EVIDENCE report (task #454): SGLang against vLLM for the PC's model server

Lane: evidence-gatherer (sandbox, Opus 5.5). Brief: `tasks/briefs/serving/SGLANG-EVIDENCE-brief.md` (landed in dd14c6c2).
PIN: 610cb123db21c2a043667bb401a58b36313d8cd4. HEAD at the lane's start: 426d37a20a88d6db07936f0c350b6db1688578aa
(a transcripts-only commit after dd14c6c2). Started 2026-10-01 20:5xZ; closed 2026-10-01 22:1xZ. Sections B, C and D were written first after the
coordinator's re-prioritization; E and F are brief; A3 moved into C0.

Row grammar: fact or claim | source (a URL pinned to a commit, tag or date, or `file:line` at the PIN) | the source's
date | SOLID (read in a primary source this session) or UNSURE (secondary, inferred, or contradicted: both rows given).
"vendor-run" marks a benchmark a project ran on its own engine. No verdict, no recommendation, no ranking.

## 0. Premise re-run (item 1 of the brief)

| # | Check | Result | Evidence | Mark |
|---|---|---|---|---|
| 0.1 | The 13 premise commands (brief lines 235-321), re-run verbatim from the repo root at HEAD 426d37a2 | Byte-identical to the brief's transcript: 87 lines, sha256 125a97d313ca8edce47af6255731f73dcc2c9a0a971209009a1c0f0a2217b0d2 on both sides; `diff` empty | runner: each `$ ` line of the brief executed with `bash -c` in `/home/user/agent-factory`, output captured, diffed against brief lines 235-321 | SOLID |
| 0.2 | The last command (`git diff --stat 610cb123 HEAD -- <12 files>` piped to `wc -l`) | prints `0`: no commit after the PIN changed the files the other commands read | same run | SOLID |
| 0.3 | Negative control on the comparison | two mutated commands (the PIN replaced by dd14c6c2; `GPU_UTIL=0.96` by `0.97`) give a 12-line diff, so the comparison can go red | same runner on a mutated command list | SOLID |
| 0.4 | Working tree for the premise's files | `git status --short` shows only untracked paths of the S3-5-VIEW lane (`scripts/s1_train/`, `tasks/briefs/jev-laya/S3-5-VIEW-report.md`, `tests/test_s1_train_view.py`); none of the premise's files is modified | `git status --short` at 2026-10-01 20:5xZ | SOLID |

Premise verdict for item 1: no mismatch; the lane proceeds. (The PC-side block, brief lines 324-353, cannot be re-run
here: no bridge. It is used below as the coordinator's measurement, cited by brief line.)

## A. The recipe and its pieces

Pinned sources used in this group (all read 2026-10-01 between 20:52Z and 21:5xZ (the end stamp substituted from `date -u` when the group was written)):
- REG = `github.com/0xSero/local-ai-registry` at main `7cff950ab003b334e845e35bc44bce092c4b8ab6` (`git ls-remote`, raw files).
- IMGB = `github.com/0xSero/local-ai-images` branch `sglang-exl3-image` at `bd929f3ed3253979cf294d627ef447c590699a71`
  (2026-09-26; plugin snapshot `a25f837a`). IMG = the same repo's main at `b76987d17cfc5ad64a816b7cb394421fa7e1020c`.
- GHCR = the registry manifest and config blob of `ghcr.io/0xsero/sglang-exl3@sha256:84f75f34…` (metadata only; no layer
  pulled): index -> amd64 manifest `sha256:76097ca5…`, config `sha256:825e0319…`.
- SGL = `github.com/sgl-project/sglang` at tag `v0.5.20` = commit `94602c9c2b7cbdb8efd5c52802dac6a1c180089e`.
- The recipe page `https://local.sybilsolutions.ai/gpu/rtx-3090-24gb/qwen3.8-27b.sglang.200k/`, fetched raw with curl at
  2026-10-01T20:52:44Z (27,755 bytes); quotes below are from that copy, not from a summarizer.

### A1. The image `ghcr.io/0xsero/sglang-exl3`

| # | Fact or claim | Source | Source date | Mark |
|---|---|---|---|---|
| A1.1 | The recipe's digest `sha256:84f75f3424c99a3d63392a4e0348292bdeba9cf7efba2ff1aa9b85c8fc0131e8` is the tag `v0.5.1-ampere` (224 downloads) | `https://github.com/users/0xSero/packages/container/sglang-exl3/versions` (Exa fetch) | "Published 8 days ago" at an unknown crawl time | SOLID (tag and digest); UNSURE (date) |
| A1.2 | Tags in order: `v0.1.0-ampere`, `v0.2.0-ampere`, `v0.3.0-ampere`, `v0.4.0-ampere`, `v0.5.0-ampere` (each "9 days ago"), `v0.5.1-ampere` (8 days), `v0.6.0-ampere` (7 days, `fe511aef…`), `v0.7.0-ampere` (6 days, `c8922bd7…`), `v0.7.0-multiarch` (4 days, `9d95829a…`), `ft-flashnext-2677501` (3 days) | same page | relative dates, crawl time unknown | SOLID (list); UNSURE (dates) |
| A1.3 | Source repository of the image: `0xSero/local-ai-images`, directory `sglang-exl3/`, on branch `sglang-exl3-image`. At main the directory does not exist (raw `sglang-exl3/Dockerfile` answers 404 at IMG; IMG's README table has no `sglang-exl3` row, only images built FROM `sglang-exl3 v0.7.0-ampere`) | IMGB `sglang-exl3/Dockerfile`; IMG `README.md:11-19` | 2026-09-26 / 2026-10-01 | SOLID |
| A1.4 | The registry's record names the build: workflow run `35845374392`, Dockerfile link `…/blob/main/sglang-exl3/Dockerfile` (a path that 404s at main today) | REG `data/registry/recipe/qwen38-27b-exl3-3bpw-rtx3090-sglang-tp1.json`, keys `launch.container.source`, `launch.provenance` | captured 2026-09-23T12:14:17Z | SOLID (the record says so) |
| A1.5 | Run `35845374392` = "release-image · 0xSero/local-ai-images@6194b68", branch `sglang-exl3-image`, "Manually triggered September 23, 2026 09:51", "Status Success", "Total duration 27m 19s" | `https://github.com/0xSero/local-ai-images/actions/runs/35845374392` (Exa fetch) | 2026-09-23 | SOLID |
| A1.6 | Commit `6194b68` (2026-09-23): "sglang-exl3: vendor plugin @ 50caaf39da79890a2694dc59e86bb7d3f947a13d (pinned-host embedding option); v2 token maps (special tokens only)". Later commits on the branch: `79171ab` (09-24, plugin @ `15f7de9a`, "EXL3 DFlash drafts …"), `bd929f3` (09-26, plugin @ `a25f837a`, "fp16-accumulate prefill GEMMs, per-segment SDPA ViT attention, row-chunked ViT MLP, CPU fast image processor; all opt-in"). Earlier on 09-23: `6bf6fbe` (image created), `5dbaa2a`, `2606791`, `76e9c67`, `7dd8ac5` | `https://github.com/0xSero/local-ai-images/commits/sglang-exl3-image/` (Exa fetch) | 2026-09-23 to 2026-09-26 | SOLID |
| A1.7 | The image's own config: `created 2026-09-23T10:05:21Z`; labels `ai.sglang.image.tag=lmsysorg/sglang:v0.5.20`, `ai.sglang.build.commit=94602c9c2b7cbdb8efd5c52802dac6a1c180089e`, `ai.omarchy.engine.version=0.5.20`, `ai.omarchy.quant=exl3`; env `TORCH_CUDA_ARCH_LIST=8.6`, `AIKIDO_KBITS=3,4,5,6`, `PYTHONPATH=/opt/sglang-exl3/csrc/build/lib`, `CUDA_VERSION=13.0.3`; `Entrypoint ['/opt/entrypoint.sh']`; `ExposedPorts 22/tcp, 30000/tcp`; no `User` set | GHCR config blob `sha256:825e0319…` | 2026-09-23 | SOLID |
| A1.8 | SGLang version: v0.5.20. The tag `v0.5.20` peels to `94602c9c2b7cbdb8efd5c52802dac6a1c180089e`, the commit in the image's labels (A1.7) | `git ls-remote --tags https://github.com/sgl-project/sglang` | 2026-10-01 | SOLID |
| A1.9 | The registry's record also says "stock SGLang v0.5.20 through the sglang-exl3 quantization plugin" and `engine.version "0.5.20"` | REG data record (A1.4), key `description`, `engine` | 2026-09-23 | SOLID |
| A1.10 | What the image adds, in its Dockerfile's words: "stock SGLang v0.5.20 + EXL3 (ExLlamaV3 trellis) quantization for Ampere (sm_86) and up. Adds: exllamav3 1.5.1 extension built for the arch list below, the sglang-exl3 plugin (registers `--quantization exl3` through the sglang.srt.plugins entry point, no SGLang source edits) and its Marlin-template EXL3 kernels (K=3/4/6)." Base `FROM lmsysorg/sglang@sha256:06e4f2ed21afde4ff513cda65070124e727ba23ccaeff7712b8c40e1097d611f` ("v0.5.20, linux/amd64, inspected 2026-09-23"); exllamav3 at commit `6b84a21b6f1e5da3f291b9e1019061f0de788279` (comment: "ExLlamaV3 v1.5.1 (MIT, turboderp)"); `openssh-server` installed, port 22 exposed | IMGB `sglang-exl3/Dockerfile:1-37` | 2026-09-26 (a later commit than the one that built 84f75f…: A1.5, A1.6) | SOLID for bd929f3e; UNSURE that 6194b68's Dockerfile was identical |
| A1.11 | The plugin repository `0xSero/sglang-exl3` is private: "Vendor a source snapshot of 0xSero/sglang-exl3 (private) into ./src at one commit"; the vendoring deletes the plugin's `tests`, `docker`, `scripts`, `notes`. Anonymous `git ls-remote https://github.com/0xSero/sglang-exl3` answers "could not read Username"; Exa: `CRAWL_NOT_FOUND` | IMGB `sglang-exl3/sync-src.sh:2,9`; ls-remote and Exa at 2026-10-01 | 2026-09-26 | SOLID |
| A1.12 | Plugin package: `name = "sglang-exl3"`, `version = "0.1.0"`, entry point `[project.entry-points."sglang.srt.plugins"] exl3 = "sglang_exl3.plugin:activate"`; no license field | IMGB `sglang-exl3/src/pyproject.toml:1-16` | 2026-09-26 | SOLID |
| A1.13 | `activate()` sets `QUANTIZATION_METHODS["exl3"] = Exl3Config`, adds the CLI choice, patches the MTP `fc` and DFlash drafts, and installs optional patches by env: `SGLANG_EXL3_EMBED_HOST`, `SGLANG_EXL3_VIT_SDPA`, `SGLANG_EXL3_MM_FAST_CPU`, `SGLANG_EXL3_VIT_MLP_CHUNK`. Its docstring: "Runs in the launcher, the engine and every scheduler subprocess." | IMGB `sglang-exl3/src/src/sglang_exl3/plugin.py:1-3,15-41` | 2026-09-26 | SOLID |
| A1.14 | `SGLANG_EXL3_EMBED_HOST=1`: "keep the target's bf16 token embedding (2.5 GB on Qwen3.8-27B) in pinned host memory and gather rows over PCIe (SGLang's own pinned-host embedding from qwen4_exp, Triton gather, CUDA-graph safe). Decode reads a few 10 KB rows per step; the freed VRAM goes to the KV pool (~80k fp8 tokens on the 27B). The MTP draft shares it." It wraps `sglang.srt.models.qwen3_5.Qwen3_5ForCausalLM._build_embed_tokens` with `Qwen4ExpPinnedHostEmbedding` | IMGB `plugin.py:47-72` | 2026-09-26 | SOLID |
| A1.15 | Second size for the same table: the registry record says "the 2.4 GB bf16 token embedding lives in pinned host memory" | REG data record (A1.4), `description` | 2026-09-23 | SOLID (both rows: 2.4 GB here, 2.5 GB in A1.14) |
| A1.16 | `SGLANG_EXL3_KERNEL`: "(auto \| exllamav3 \| marlin)". ExLlamaV3's own `exllamav3_ext` kernels are the "bit-faithful reference" (`exllamav3`); the Marlin-template EXL3 kernels "from aikido-exl3" run under `auto\|marlin`, "decoded weights bit-identical to `exllamav3_ext.reconstruct`, flat cost from 1 to 16 rows". "Prefill (>= 144 rows) reconstructs fp16 weight slices and runs cuBLAS". Other knobs: `SGLANG_EXL3_HOPPER_MAX_N`, `_DENSE_ROWS` (144), `_DENSE_SLICE_MB` (64), `_SLICED` (1), `_DRAFT_SHARE_EMBED` (1), `_MODEL_PATH` ("override the checkpoint dir for the header scan") | IMGB `sglang-exl3/src/README.md:13-16,30-32` | 2026-09-26 | SOLID |
| A1.17 | The token map: the Dockerfile copies "Hot-token lists for --speculative-token-map (32k tokens; public corpora, tokenmaps/make_token_map.py)" to `/opt/sglang-exl3/tokenmaps`. With an EXL3 target, the plugin builds a dense bf16 draft head for the hot tokens from the target's EXL3 head; "The target keeps verifying with the full quantized head, so outputs are unchanged; only draft acceptance can move." | IMGB `Dockerfile:31-32`; `plugin.py:204-223` | 2026-09-26 | SOLID (the source's claim; not tested here) |
| A1.18 | `/opt/entrypoint.sh`: no argument -> `python3 -m sglang.launch_server --help`; one argument -> `/bin/sh -c "$1"`; otherwise `exec "$@"` | IMGB `sglang-exl3/entrypoint.sh:1-11` | 2026-09-26 | SOLID |
| A1.19 | The plugin README's own number: "RTX 3090 with the desktop resident, ~19 GiB usable … Qwen3.8-27B EXL3 3.0 bpw, MTP 3/1/4, fp8 KV, ExLlamaV3 kernels for the K=3 layers: prose 61.7 tok/s, code 88.7 tok/s per stream at C1 (AWQ-INT4 in the same engine on a bare 3090: 45 tok/s, no speculative decoding)" | IMGB `sglang-exl3/src/README.md:34-37` | 2026-09-26 | SOLID (vendor-run) |
| A1.20 | Licenses: the registry is MIT ("Copyright (c) 2026 0xSero"); `local-ai-images` has no `LICENSE`, `LICENSE.md` or `COPYING` at IMG or IMGB (all 404) and its repo page shows no license; the plugin's pyproject names none; SGLang is Apache-2.0 at SGL; exllamav3 is "MIT" per the Dockerfile comment (not read at its source). The "aikido-exl3" kernels' license: NOT FOUND (no public repo found; searches: the vendored README, GitHub code search not run on a private repo) | REG `LICENSE`; raw 404s; SGL `LICENSE:1-3`; IMGB `Dockerfile:18` | 2026-10-01 | SOLID (registry, absences, SGLang); UNSURE (exllamav3, read second-hand) |
| A1.21 | Activity: `local-ai-images` created 2026-09-02T22:27:51Z, 8 stars, 1 fork, top contributor 0xSero (24 contributions); main's last commit is `b76987d` on Oct 1, 2026 ("Merge pull request #10 …glm53-flash-offload"). Open issues: the repo metadata says "Open issues: 1"; the issues page (default open filter) says "No results matched your search" (GitHub's open-issue count includes open PRs) | `https://github.com/0xSero/local-ai-images` and `/issues` and `/commits/main/` (Exa fetches) | 2026-10-01 | SOLID (both rows given) |
| A1.22 | The plugin repo's commit activity, last commit date and open issues | NOT FOUND: private (A1.11); only the vendored snapshots and their commit titles (A1.6) are visible | — | — |
| A1.23 | EXL3 in upstream SGLang: none found. GitHub PR search `exl3 repo:sgl-project/sglang`: `total_count 0`; `exllama repo:sgl-project/sglang`: 1 hit, unrelated (#22685, "[CPU] [Quantization] Add GPTQ/AWQ 4bits quantization support for CPU", closed 2026-04-22); code search `exl3 repo:sgl-project/sglang`: `total_count 0`; a semantic issue search ("exl3 exllamav3 quantization support", 20 of 65 hits read): no EXL3 item | GitHub search API via the session's GitHub tools | 2026-10-01 | SOLID (PR search, uncapped zero); UNSURE (code search covers the default branch only, and its index coverage cannot be proven) |
| A1.24 | The plugin's design depends on SGLang's plugin entry point `sglang.srt.plugins` and imports internal modules (`sglang.srt.models.qwen3_5`, `qwen4_exp`, `qwen3_5_mtp`, `sglang.srt.arg_groups.choices`, `sglang.srt.runtime_context`, `sglang.srt.speculative.spec_utils`) | IMGB `plugin.py:20-22,51-53,79,210-213` | 2026-09-26 | SOLID (the imports); the upkeep consequence is the coordinator's |

### A2. The registry's six checks and its benchmark method for this recipe

| # | Fact or claim | Source | Source date | Mark |
|---|---|---|---|---|
| A2.1 | The page shows "135 tok/s decode", "591 tok/s prefill", "200K context window", "Tested on this card Sep 26, 2026", "Passed all six checks on a real RTX 3090 on Sep 26, 2026", "Tested: owner, RTX 3090"; launch command identical to the brief's lines 68-103 | recipe page (raw copy), text lines 3-8, 15-50, 57, 69 | fetched 2026-10-01 | SOLID |
| A2.2 | The six checks as the page states them: load ("Loads and serves within an hour"), chat ("Answers a plain question and stops on its own"), reasoning ("Thinks separately and gets 17 × 23 right"), tools ("Calls a tool with the right arguments and uses the result"), context ("Recalls a code buried in a prompt that fills 85% of the window"), speed ("Decodes at 15 tok/s or more") | recipe page, text lines 51-56 | 2026-10-01 | SOLID |
| A2.3 | The recipe file holds THREE proofs, not one: 2026-09-28 "owner", "NVIDIA GeForce RTX 3090", `tps 110.0`, `prefill 620`, log `sha256:c5bd9c1e664ef82f`; 2026-09-26 "owner", `tps 135.0`, `prefill 591`, log `sha256:3dc365ad2d0e2404`; 2026-09-25 "vast", `tps 138.8`, `prefill 583`, log `sha256:90038ff37062c789`. The page shows the 09-26 proof | REG `registry/recipes/nvidia/rtx-3090-24gb/qwen3.8-27b.sglang.200k.json` (one line) | file history: added 09-26 (`9c428cb`), last changed 2026-09-29 (`e0cb32d`, PR #137) | SOLID |
| A2.4 | In the lab, "owner" means `--on endpoint` (a machine the runner points at), "vast" a rented Vast host | REG `lab/lab.py:379-382,388` | 2026-10-01 (REG head) | SOLID |
| A2.5 | Decode method (`tps`): ONE streamed chat answer to "Write a detailed 600-word story about a lighthouse keeper." at `temperature 0.8`, concurrency 1, no `max_tokens`; rate = tokens (reasoning plus content) in the first 30 s after the first token, divided by that span; tokens counted with the server's tokenizer endpoint (`/v1/token/encode`, `/tokenize`, `/v1/tokenize`) or, failing that, `len(text)//4` | REG `lab/lab.py:154-166,182-212,263-267` | 2026-10-01 | SOLID |
| A2.6 | "Prefill" method: `prefill = round(prompt_tokens / seconds)` of the context-gate request, where `seconds` is the WHOLE chat call (prefill, any thinking, and the answer) at `temperature 0.6` with no `max_tokens`. It is not a prefill-only timing | REG `lab/lab.py:169-179,253-260,268` | 2026-10-01 | SOLID |
| A2.7 | Context gate: a filler prompt sized to `int(ctx * 0.85)` (0.85 × 204,800 = 174,080 target tokens) with a vault code near the end; passes if the code comes back and `prompt_tokens >= ctx * 0.6` | REG `lab/lab.py:253-259` | 2026-10-01 | SOLID |
| A2.8 | Number of runs: one request per gate per proof; each proof is one run (`proof` keeps the newest three passing runs with the same weights, engine and settings) | REG `lab/lab.py:215-270,415` | 2026-10-01 | SOLID |
| A2.9 | Raw results: each run writes `lab/runs/<card>.<model>.<profile>.<ctx//1024>k.<UTC stamp>.json`; the proof's `log` is the first 16 hex of that text's sha256. `lab/runs/*` is git-ignored (`.gitignore` lines `lab/runs/*`, `!lab/runs/.gitkeep`); at REG `lab/runs/` holds only `.gitkeep`. The run files for the 09-25 and 09-26 proofs are not published; the 09-28 run's full evidence JSON is pasted in PR #137's body | REG `lab/lab.py:401-407`, `.gitignore`; tree listing of `lab/runs` at REG (WebFetch); PR #137 | 2026-10-01 / 2026-09-28 | SOLID |
| A2.10 | Commit `9c428cb` (2026-09-26T10:55:44Z, 0xSero, co-authored by Claude Opus 5.5): "the existing 27B 200k profile re-run on the same card: 135.0 / 591"; the same commit adds a 208k MTP+vision profile ("27B 208k decode 129.0 / prefill 786 tok/s") on "sglang-exl3 v0.7.0-ampere", image `c8922bd7` | `https://github.com/0xSero/local-ai-registry/commit/9c428cb` (Exa fetch) | 2026-09-26 | SOLID (vendor-run) |
| A2.11 | PR #137 (safzanpirani, merged 2026-09-29T09:46:37Z, merge commit `e0cb32d3`): the 110.0 tok/s proof. Context gate "166,667 prompt tokens (268.9 s)" -> prefill 620; speed "110.0 tok/s over the first 30 s of a streamed answer (16,387 tokens in 151.0 s total)"; run at "a 350 W limit" on "an idle card"; command `lab.py try … --on endpoint --endpoint http://127.0.0.1:12434`; "no `max_tokens` anywhere" | `https://github.com/0xSero/local-ai-registry/pull/137` (Exa fetch, body quoted) | 2026-09-28 | SOLID |
| A2.12 | The same PR: "The first proof submitted here (83.3 tok/s) was measured while the agent's own requests were queued on the same GPU and the card was power-capped at 280 W. It was dropped … and the gates were rerun on an idle card at a 350 W limit" | PR #137 body | 2026-09-28 | SOLID |
| A2.13 | The same PR: "The new proof ranks below the 208k MTP+vision proof on decode speed, so the catalog's first pick for the 3090 is the 208k recipe; the 200k recipe stays in `more`." | PR #137 body | 2026-09-28 | SOLID |
| A2.14 | The 208k recipe (a different launch and image): `engine "sglang-qwen3.8-27b-exl3-3bpw-mtp-vision-208k@c8922bd7256c"`, proofs 2026-09-26 `tps 129.0`/`prefill 786` and 2026-09-26 `tps 94.9`/`prefill 787` | REG `registry/recipes/nvidia/rtx-3090-24gb/qwen3.8-27b.sglang.208k.json` | 2026-09-26 | SOLID |
| A2.15 | A second, earlier harness measured this launch before the lab: "rtx-3090/bench/harness.py (inference-tuning-protocol v1.0.0 panel)", run directory `a256_27b_turboderp`, measured 2026-09-23, every row at concurrency 1, at `max_context_tokens 262144` (the launch before its 0.88 -> 0.80 change, A3): C1 decode per stream prose 98.83 (thinking off, 5 samples), 146.56 (thinking on, 1 sample), code 143.28 (6 samples); at a 32,768-token prompt: prose 89.57, prefill 904.0 tok/s, TTFT 36.3 s; 10-minute soak at 32k: 14 requests, 0 failed, `preemptions 0`, 98.75 tok/s per stream; `peak_memory_bytes 24739011624` | REG `data/registry/speed-sweep/qwen38-27b-exl3-3bpw-rtx3090-sglang-tp1-sweep.json` | 2026-09-23 | SOLID (vendor-run) |
| A2.16 | The same record's coherence ladder (one request each): TTFT 201,622.7 ms at 131,095 prompt tokens; 543,863.6 ms at 258,040 tokens; 35,700.6 ms at 32,714 | REG data record (A1.4), `metadata.acceptance.coherence_ladder` | 2026-09-23 | SOLID (vendor-run) |
| A2.17 | Re-run tools: `lab.py` is "Standard library only" and can target any OpenAI-compatible endpoint (`--on endpoint --endpoint URL`); the harness `rtx-3090/bench/harness.py` is not in REG (its repository was not found; not searched further) | REG `lab/lab.py:1-15`; A2.15 | 2026-10-01 | SOLID (lab.py); NOT FOUND (harness source) |

### A3. Each recipe flag's meaning and the memory arithmetic

Moved to C0 (the coordinator's re-prioritization put it with concurrency): C0.1-C0.13 give each flag's help text at
v0.5.20, the queue-versus-refuse answer (queued; refused only with `--max-queued-requests`), and the arithmetic with
each input's source (B1.11 for the state size).

### A4. Quality evidence for the two weight formats

| # | Fact | Source | Mark |
|---|---|---|---|
| A4.1 | `turboderp/Qwen3.8-27B-exl3` revision `6fe61ad6…` is the head of the repo's `3.00bpw` branch; `quantization_config`: `"quant_method": "exl3", "version": "1.4.2", "bits": 3.0, "head_bits": 6, "mtp_bits": 4`; files 13,843,803,198 B in all (the two safetensors 13,819,939,309 B) | HF API `refs` and `tree/6fe61ad6…?recursive=1`; `config.json` | SOLID |
| A4.2 | The same repo also has `SC_*` branches (for example `SC_3.00bpw_H4_V4`, `SC_4.00bpw_H5_V6`) beside the plain `2.00bpw` to `6.00bpw` branches | HF API `refs` | SOLID |
| A4.3 | Perplexity, KL divergence or benchmark deltas for EXL3 3.0 bpw against BF16 and 4-bit formats (turboderp or exllamav3 tables); the `dbirks/Qwen3.8-27B-W4A16-AutoRound` model card's numbers | NOT FOUND: not extracted within the re-prioritized time (the EXL3 model card, 65,012 B, was fetched; its "Benchmark Results" section is the base model's table and was not parsed) | — |
| A4.4 | The fork author's numeric check between kernel settings: "top-20 logprob KL vs fp32-acc 0.0015 nats" (not a 3-bit-versus-4-bit comparison) | REG `metadata.tuning` | SOLID (vendor-run) |

## B. Caching and memory pressure (C-2, C-3)

Pinned sources: SGL = SGLang `v0.5.20` = `94602c9c2b7cbdb8efd5c52802dac6a1c180089e` (the fork's base, A1.8); VLL = vLLM
`v0.28.0` = `2cf0a6915ce544dc493a0990f2ea38d81601128a` (`git ls-remote --tags`; the live engine logs "V1 LLM engine
(v0.28.0)", brief line 334). Raw files read 2026-10-01. Paths are relative to each repository's root.

### B1. SGLang's prefix cache on the hybrid model (Gated DeltaNet + full attention)

| # | Fact or claim | Source | Source date | Mark |
|---|---|---|---|---|
| B1.1 | The class is `MambaRadixCache` ("The radix tree data structure for managing the hybrid (full and Mamba) KV cache"); each tree node holds token KV (`value`) and optionally one linear-attention state (`mamba_value`), plus `mamba_host_value` for a host copy | SGL `python/sglang/srt/mem_cache/mamba_radix_cache.py:18-20,73-100,444` | v0.5.20 | SOLID |
| B1.2 | Token-level radix tree: a prefix match walks children token by token and SPLITS a node at a partial match (`_split_node`), so two chats share every common token, not whole blocks (page size 1 in the recipe; `MambaRadixCache` v1 asserts page size 1 without the extra buffer) | SGL `mamba_radix_cache.py:467-470,1120-1139` | v0.5.20 | SOLID |
| B1.3 | A hit is cut back to the deepest matched node that HOLDS a linear-attention state: `best_value_len` advances only at nodes with `mamba_value`, then `value = value[:best_value_len]`. Tokens matched past that node are recomputed | SGL `mamba_radix_cache.py:1120-1145,1213` | v0.5.20 | SOLID |
| B1.4 | Where states are snapshot: at a "branching point" aligned to `mamba_cache_chunk_size` = "max(the model's mamba chunk size, page_size)" (the FLA chunk size by default); decode tracks the state every `--mamba-track-interval` tokens (default 256) | SGL `mamba_radix_cache.py:1187-1197`; `runtime_context.py:1996-2001`; `arg_groups/overrides.py:1896-1910`; `arg_groups/fields/exec_.py:385-388` | v0.5.20 | SOLID |
| B1.5 | Two LRU lists: full KV (`full_lru_list`) and states (`mamba_lru_list`); a hit refreshes the whole matched path's KV but only the one state it uses ("Refreshing ancestors would keep a whole session's states adjacent in the mamba LRU and evict cold sessions wholesale") | SGL `mamba_radix_cache.py:498-500,1167-1176` | v0.5.20 | SOLID |
| B1.6 | Separate eviction for states and KV: `evict_mamba(mamba_num)` and `evict_full(full_num_tokens)`; a request that needs a state slot and finds none evicts one (`self.evict(EvictParams(num_tokens=0, mamba_num=1))`) | SGL `mamba_radix_cache.py:864-915,1200-1209` | v0.5.20 | SOLID |
| B1.7 | `--mamba-radix-cache-strategy` choices `auto`, `no_buffer`, `extra_buffer`, `extra_buffer_lazy`; `auto` resolves to `extra_buffer` when the overlap scheduler is on (or page size > 1) and the architecture is in the supported list (it includes `Qwen3_5ForConditionalGeneration`, this checkpoint's architecture) on the `triton` linear-attention backend (the default); otherwise `no_buffer` AND the overlap scheduler is turned off | SGL `arg_groups/fields/exec_.py:367-374,397-403`; `arg_groups/overrides.py:474-555` | v0.5.20 | SOLID |
| B1.8 | What `--max-mamba-cache-size` bounds: the number of state slots in the mamba pool (running requests AND cached snapshots share it). Help text: "The maximum size of the mamba cache." Each running request needs `ratio` slots: base 3 (minus 1 with `SGLANG_OPT_MAMBA_SKIP_DECODE_LOCK=1`), plus 2 for `extra_buffer` with overlap, 1 without overlap or lazy, 1 for `no_buffer` under the skip flag; `max_running_requests` is capped to `max_mamba_cache_size // ratio` (warning text: "max_running_requests is capped to %d by the mamba state cache") | SGL `arg_groups/fields/schedule.py:199-202`; `mem_cache/kv_cache_configurator.py:167-172,2203-2232,2278-2294` | v0.5.20 | SOLID |
| B1.9 | For the recipe (no strategy flag, overlap on, no skip env): ratio = 3 + 2 = 5, so `--max-mamba-cache-size 5` gives `5 // 5 = 1` running request and no spare slot for cached snapshots beyond it | derived from B1.7 and B1.8 | — | UNSURE (derived; not observed in a log) |
| B1.10 | The registry's other launches pair the knobs the same way: 208k single-stream `--max-mamba-cache-size 3` with `--mamba-radix-cache-strategy no_buffer --disable-overlap-schedule` and `SGLANG_OPT_MAMBA_SKIP_DECODE_LOCK=1` (ratio 3, so 1 request); the C4 candidate `--max-mamba-cache-size 12 --max-running-requests 4` with the same three settings (12 // 3 = 4) | REG data records `qwen38-27b-exl3-3bpw-mtp-vision-…` and `…-c4-mtp-vision-…` (`launch.arguments`, `launch.environment`) | 2026-09-26 | SOLID (the flags); UNSURE (the ratio reading) |
| B1.11 | State size per slot for this model, by SGLang's formula `(conv numel × conv bytes + temporal numel × ssm bytes) × linear layers`: conv `(10,240 × 3)`, temporal `(48 × 128 × 128)`, bf16 for both (`--mamba-ssm-dtype bfloat16`; conv default `SGLANG_MAMBA_CONV_DTYPE="bfloat16"`), 48 linear layers = 1,634,304 B per layer = 78,446,592 B (74.81 MiB) per slot; fp32 SSM would be 153,944,064 B | formula SGL `configs/mamba_utils.py:115-125,222-230`, `configs/qwen3_next.py:288-312`, `environ.py:1366-1367`; inputs `config.json` of `turboderp/Qwen3.8-27B-exl3@6fe61ad6` (`text_config`: 64 layers, `full_attention_interval 4`, 48 `linear_attention`, `linear_num_value_heads 48`, `linear_num_key_heads 16`, key/value head dims 128, `linear_conv_kernel_dim 4`) | 2026-10-01 arithmetic | UNSURE (my arithmetic on SOLID inputs) |
| B1.12 | When the state cache arrived and its history | NOT FOUND within this lane's time: searches not run (the coordinator's re-prioritization cut them); `Qwen3NextForCausalLM` is in the same supported list (B1.7) | — | — |
| B1.13 | HiCache (host-memory KV tier) exists at the tag: `--enable-hierarchical-cache` (default off), `--hicache-ratio` ("Defaults to 2.0 in cache mode"), `--hicache-size` (GB), `--hicache-host-memory-mode cache|buffer_only`. The recipe does not enable it. Whether it covers the hybrid states end to end: the node has `mamba_host_value` and `host_mamba_ref_counter`, which points to host copies of states | SGL `arg_groups/fields/memory.py:100-118`; `mamba_radix_cache.py:83,99-100` | v0.5.20 | SOLID (flags); UNSURE (hybrid coverage) |
| B1.14 | Option to keep reasoning out of the tree: `--strip-thinking-cache` ("Skip caching reasoning-model output (thinking + answer) in the radix tree on finish; keep only the prompt prefix") | SGL `arg_groups/fields/serving.py:210-213` | v0.5.20 | SOLID |

### B2. SGLang under KV pressure

| # | Fact or claim | Source | Source date | Mark |
|---|---|---|---|---|
| B2.1 | Admission: a new request is prefilled only while the budget allows; for a hybrid model the budget is `available_size() + tree_cache.full_evictable_size()`, so unreferenced cached prefixes count as free space and are evicted to make room | SGL `managers/schedule_policy.py:719-741` | v0.5.20 | SOLID |
| B2.2 | A request that does not fit, or that exceeds `max_running_requests`, stays in `waiting_queue`: `get_num_allocatable_reqs` = `pp_max_micro_batch_size - running_bs`, and `pp_max_micro_batch_size = max(max_running_requests // pp_size, 1)`; at 0 the scheduler marks `batch_is_full` and schedules no prefill | SGL `managers/scheduler.py:1190-1196,3710-3728,3796-3802` | v0.5.20 | SOLID |
| B2.3 | Refusal happens only with `--max-queued-requests` set (default `None`): then "The request queue is full." with HTTP 503 (`SERVICE_UNAVAILABLE`); a server-side wait timeout exists but is off by default (`SGLANG_REQ_WAITING_TIMEOUT = EnvFloat(-1)`) | SGL `scheduler.py:3193-3206,3258-3302,3311`; `environ.py:623`; `fields/schedule.py:42-45` | v0.5.20 | SOLID |
| B2.4 | Running requests under decode pressure: when `check_decode_mem()` fails, `batch.retract_decode()` takes requests out of the running batch, frees their memory and puts them back in the waiting queue (`_add_request_to_queue(req, is_retracted=True)`); some can be aborted instead (`reqs_to_abort`). Log line: "KV cache pool is full. Retract requests." The order is `--retraction-policy` (default `length`: "retracts short-output, long-input requests first") | SGL `scheduler.py:4101-4171`; `fields/schedule.py:128-140` | v0.5.20 | SOLID |
| B2.5 | `--schedule-conservativeness` (default 1.0): "Use a larger value if you see requests being retracted frequently" | SGL `fields/schedule.py:141-144` | v0.5.20 | SOLID |
| B2.6 | Remaining OOM paths (outside the KV pool): `--mem-fraction-static` covers only "model weights and KV cache memory pool"; help: "Use a smaller value if you see out-of-memory errors." The KV budget is `free memory after load − pre_load_memory × (1 − mem_fraction_static)`, and start-up raises "Loaded weights leave no GPU memory for the KV cache" when it goes negative | SGL `fields/schedule.py:34-37`; `kv_cache_configurator.py:2148-2201` | v0.5.20 | SOLID |
| B2.7 | Observed OOM on this exact model and card in the fork: "prefill CUDA graphs capped at 512 tokens: 1.05 GB graph memory; 4096^2 image OOM (HTTP 500)", rejected; also the recipe's change log: "context 262144 -> 204800 and --mem-fraction-static 0.88 -> 0.80 so the prefill graph capture fits (1.37 GB)" | REG data records (`metadata.tuning`; `metadata.graphs_check`) | 2026-09-23 / 2026-09-26 | SOLID (vendor-run) |
| B2.8 | Soak results on the fork (no preemptions recorded): C1 at 32k: 14 requests, 0 failed, `preemptions 0`; C4 at 32k: 25 requests in 656.7 s, 0 failed, `preemptions 0`, 16.56 tok/s per stream, drift 11.87 % | REG speed sweeps (`rows[kind=soak]`) | 2026-09-23 / 2026-09-26 | SOLID (vendor-run) |
| B2.9 | Public issues reporting SGLang OOM or crashes under concurrency on 24 GiB cards | see E1 (searched there) | — | — |

### B3. vLLM 0.28 on the same questions (the live configuration)

| # | Fact or claim | Source | Source date | Mark |
|---|---|---|---|---|
| B3.1 | `mamba_cache_mode` values `all`, `align`, `none`; "align: only cache the mamba state of the last token of each scheduler step and when the token is at position i * block_size. This is the default when prefix caching is enabled." | VLL `vllm/config/cache.py:39,137-145` | v0.28.0 | SOLID |
| B3.2 | With prefix caching on, `none` becomes `align`; `align` requires chunked prefill; `mamba_block_size` defaults to the attention `block_size` | VLL `vllm/model_executor/models/config.py:602-629` | v0.28.0 | SOLID |
| B3.3 | The block size it forces: for hybrids vLLM raises the attention `block_size` to `kernel_block_alignment_size × cdiv(mamba_page_size, kernel_block_alignment_size × attn_page_size_1_token)` so one attention page is at least one state ("Setting attention block size to %d tokens to ensure that attention page size is >= mamba page size."), then in `align` mode sets `mamba_block_size = block_size` and pads the state page to the attention page | VLL `vllm/platforms/interface.py:767-930` | v0.28.0 | SOLID |
| B3.4 | Applied to this model (16 attention layers sharing pages with 48 state layers; per layer fp8 KV 2 × 4 × 256 = 2,048 B/token; one state 1,634,304 B, B1.11) with a 16-token kernel alignment: `16 × cdiv(1,634,304, 16 × 2,048) = 16 × 50 = 800` tokens per block, so prefix-cache hits land on 800-token boundaries | derived from B3.3; the alignment size per backend was not read | — | UNSURE (derived; the live log line "Setting attention block size" is not in the premise block) |
| B3.5 | Pool full: when `allocate_slots` fails, the scheduler preempts (FCFS: `self.running.pop()`, the newest running request; PRIORITY: the lowest priority), frees its blocks, sets `num_computed_tokens = 0` (recompute from the start, prefix cache permitting) and increments `num_preemptions`; the request returns to the waiting queue | VLL `vllm/v1/core/sched/scheduler.py:628-688,1336-1371` | v0.28.0 | SOLID |
| B3.6 | The live server reports `vllm:num_preemptions_total … 0.0` and a prefix cache hit ratio of `4.40416e+07 / 6.4929219e+07` (67.8 %) since its start on 09-26 | brief lines 341-348 (the coordinator's PC measurement) | 2026-10-01 | SOLID (as measured by the coordinator) |
| B3.7 | An open vLLM PR touches this path: #55601 "[Bugfix] Seed hybrid mamba state index with mamba_block_size on prefix-cache hits" (open, created 2026-09-06) | GitHub PR search (`exllamav3 OR exl3 is:pr repo:vllm-project/vllm` returned it) | 2026-09-06 | SOLID (exists, open); its effect on this model: not read |
| B3.8 | The image's own patches: the startup log shows "PASS  mamba-chunked-prefill-align.patch applied" | brief line 332 | 2026-09-26 (log) | SOLID (as measured); the patch's content: NOT FOUND (the image's repository was not read in this lane) |
| B3.9 | Where vLLM still OOMs: allocations outside the pool at run time (B4.1, B4.2, B4.3) | B4 | — | SOLID (records) |

### B4. This project's own records of vLLM failures (at the PIN)

| # | Date | What happened | Cause the record states | Knob or rule that closed it | Source | Mark |
|---|---|---|---|---|---|---|
| B4.1 | 2026-09-24 23:4xZ | The vLLM `qwen` engine died; systemd restarted it; about 5 minutes down | AF-AP-201: a request with `prompt_logprobs: 0`; "a full-vocabulary log-softmax per prompt token needed 758 MiB with 148 MiB free" | Never send `prompt_logprobs` or `best_of` to the shared server; `scripts/s1_synth.py` `FORBIDDEN_BODY_KEYS = ("prompt_logprobs", "best_of", "echo", "n")` | `docs/INCIDENT-LOG.md:162,844`; `PC-BRIDGE.md:211`; `scripts/s1_synth.py:168-169` (at PIN 610cb123) | SOLID |
| B4.2 | 2026-09-25 09:1xZ | In a GPU test window at `GPU_UTIL` 0.88 beside the RWKV reader, Qwen's first requests got HTTP 500; "vLLM's EngineCore asked for 24 MiB with 4.94 MiB free (`torch.OutOfMemoryError`, `EngineDeadError`) while the reader held 2,168 MiB" | "vLLM allocates past its budget at run time, and a chunked read with a carried state peaks above G0's single forward (1,794 against 1,514 MiB)" | Contained by the window job; rule orchestration 0d'' (a resource budget counts every measured consumer); "a resident reader caps its own memory so it fails before Qwen" | `docs/INCIDENT-LOG.md:130` | SOLID |
| B4.3 | 2026-09-26 07:52:10Z | "the `qwen` service's engine died on a CUDA OOM (`expandable_segments: memory mapping failed with OOM on device 0 while trying to map 20971520 bytes (free: 5242880 ...)`, `num_running_reqs=4`)"; systemd restarted it 11 times, each start failing the free-memory check (22.8 GiB free, 22.9 GiB wanted) | AF-AP-231: `laya-systemone`'s probe kept a 256 MiB CUDA context; at `GPU_UTIL` 0.972 vLLM had 63 MiB of slack | D-099: `GPU_UTIL=0.96` ("At 0.96 the KV pool is 6.83 GiB = 215,112 tokens (1.64x at 131,072) and 796 MiB stays free beside laya"); "No second CUDA process while `qwen.service` runs" | `docs/INCIDENT-LOG.md:86,874`; `PC-BRIDGE.md:176,216` | SOLID |
| B4.4 | 2026-09-23 10:5xZ (third instance) | Three local lanes starved one: "a third lane's request waits inside vLLM (`Waiting: 1`) past OmniRoute's 80 s first-event limit and dies 504" | AF-AP-146: "the binding constraint at production context lengths is the vLLM KV cache, 222,822 tokens. Lanes that have run for hours send 57-90k-token prompts. Two fit" | Run ONE long-context local lane; the next goes to a sandbox agent | `docs/INCIDENT-LOG.md:297,789`; `.claude/skills/pc-bridge-lanes/SKILL.md` (premise line 318-319) | SOLID |
| B4.5 | Two KV pool figures in the records | 222,822 tokens (AF-AP-146, before D-099) and 215,112 tokens (at 0.96, D-099; the live log, brief line 335) | — | — | as above | SOLID (both rows) |

## C. Speed and concurrency (C-1, C-4)

### C0. The recipe's flags, and what limits concurrent chats (brief A3; the coordinator's points 1 and 3)

Flag meanings are SGLang's own help strings at SGL (v0.5.20). "Derived" rows are my arithmetic on the cited inputs.

| # | Fact or claim | Source | Source date | Mark |
|---|---|---|---|---|
| C0.1 | `--max-running-requests 1`: "The maximum number of running requests." A second concurrent request is QUEUED, not refused: the scheduler's micro-batch budget is `max(max_running_requests // pp_size, 1)` = 1, so with one request running `get_num_allocatable_reqs` is 0 and no prefill is scheduled (`batch_is_full`); the request waits in `waiting_queue` with no server timeout by default | SGL `arg_groups/fields/schedule.py:38-41`; `managers/scheduler.py:1190-1196,3193-3206,3710-3728,3796-3802`; `environ.py:623` | v0.5.20 | SOLID |
| C0.2 | It is refused only if `--max-queued-requests N` is set and the queue is full: HTTP 503, "The request queue is full." | SGL `scheduler.py:3258-3302`; `fields/schedule.py:42-45` | v0.5.20 | SOLID |
| C0.3 | `--max-mamba-cache-size 5`: the state-slot pool; with the recipe's defaults one request takes 5 slots (B1.8, B1.9), and SGLang caps `max_running_requests` at `max_mamba_cache_size // ratio` | SGL `kv_cache_configurator.py:2203-2232,2278-2294` | v0.5.20 | SOLID (code); UNSURE (ratio 5 for this launch is derived) |
| C0.4 | `--cuda-graph-max-bs-decode 1`: "Maximum batch size captured for the decode cuda graph." A decode batch larger than the captured size fails `can_run_graph` (`cuda_graph_bs <= self.max_bs`) and does not use the graph | SGL `arg_groups/fields/exec_.py:482-484`; `model_executor/runner/decode_cuda_graph_runner.py:635-686` | v0.5.20 | SOLID (the check); UNSURE (that it then runs eager: the caller was not read) |
| C0.5 | `--mem-fraction-static 0.80`: "The fraction of the memory used for static allocation (model weights and KV cache memory pool)." The KV budget = free memory after loading − `pre_load_memory × (1 − 0.80)`; the state pool (and the speculative intermediate states) are subtracted from it | SGL `fields/schedule.py:34-37`; `kv_cache_configurator.py:2148-2201,2433-2454,2534-2540` | v0.5.20 | SOLID |
| C0.6 | `--chunked-prefill-size 1024`: "The maximum number of tokens in a chunk for the chunked prefill." `--max-prefill-tokens 1024`: "The maximum number of tokens in a prefill batch. The real bound will be the maximum of this value and the model's maximum context length." (default 16384) | SGL `fields/schedule.py:59-62,74-84` | v0.5.20 | SOLID |
| C0.7 | `--speculative-algorithm NEXTN`: `NEXTN` is a reserved alias that resolves to `EAGLE` (the model's own MTP layer as the draft); served by `EAGLEWorkerV2` "even with overlap disabled". `--speculative-num-steps 3`: "The number of steps sampled from draft model"; `--speculative-eagle-topk 1`: "The number of tokens sampled from the draft model in eagle2 each step"; `--speculative-num-draft-tokens 4`: "The number of tokens sampled from the draft model in Speculative Decoding"; `--speculative-token-map`: "The path of the draft model's small vocab table" (the fork builds a 32k hot-token bf16 draft head from it, A1.17) | SGL `speculative/spec_registry.py:194`; `speculative/spec_info.py:50-66,346-358`; `fields/spec.py:37-40,60-71,122-125` | v0.5.20 | SOLID |
| C0.8 | Speculative decoding reserves extra state memory: `stage_per_req × (capped_reqs + 1) × speculative_num_draft_tokens` | SGL `kv_cache_configurator.py:2443-2454` | v0.5.20 | SOLID |
| C0.9 | Memory inputs for this model: KV per token in fp8 = 2 × 4 KV heads × 256 × 16 full-attention layers × 1 B = 32,768 B (plus 2,048 B for the 1-layer MTP draft, whose pool shares the target's slot index space: "The draft pool is allocated with one slot per target token"); one state slot = 78,446,592 B (B1.11); the recipe's state memory = (5 + 1) × 78,446,592 = 470,679,552 B (0.438 GiB) plus speculative intermediates 78,446,592 × (1 + 1) × 4 = 627,572,736 B (0.584 GiB) | config.json (B1.11); SGL `fields/spec.py:148-159`; formulas in C0.5 and C0.8 | 2026-10-01 arithmetic | UNSURE (derived; the MTP layer's KV shape is assumed equal to the main attention's) |
| C0.10 | Weights: the checkpoint's two safetensors are 8,575,532,487 + 5,244,406,822 B (13.82 GB; the launch file says `"sizeGb": 13.84`); `SGLANG_EXL3_EMBED_HOST=1` moves the 2.4 to 2.5 GB bf16 embedding to pinned host memory (A1.14, A1.15) | HF API `models/turboderp/Qwen3.8-27B-exl3/tree/6fe61ad6…`; REG launch file | 2026-10-01 | SOLID |
| C0.11 | The KV pool SGLang reached with this launch, two figures in the same record: "KV pool 212823 tokens" after the 0.88 -> 0.80 change (`metadata.graphs_check`, 2026-09-23), and `serving.kv_cache_tokens 272369` (also the launch file's `kvTokens`; the description says "pool 272k tokens" for the earlier 262,144-token window) | REG data record `qwen38-27b-exl3-3bpw-rtx3090-sglang-tp1`; REG launch file | 2026-09-23 | SOLID (both rows; which one the 0.80 launch has: the graphs_check text says 212,823) |
| C0.12 | Chats that fit the pool by tokens (prefill KV only; derived): 212,823 tokens holds 2.36 chats of 90k or 3.73 of 57k; 272,369 holds 3.03 or 4.78. With `--max-running-requests 1` only ONE runs; the others wait (C0.1) and the radix tree can keep their prefixes cached while space lasts (B1, B2.1) | arithmetic on C0.11 and the brief's 57-90k prompts (brief line 53-54) | — | UNSURE (derived) |
| C0.13 | The live vLLM for comparison: 215,112 tokens, "Maximum concurrency for 131,072 tokens per request: 1.64x"; `max_num_seqs 64`; `max_num_batched_tokens 2048` | brief lines 333-335 (the coordinator's PC log) | 2026-09-26 log | SOLID (as measured) |
| C0.14 | What the fork's author changed to run four streams on the same card and model (the "C4 candidate", image `v0.7.0-ampere`): `--max-running-requests 4 --max-mamba-cache-size 12 --cuda-graph-max-bs-decode 4 --mem-fraction-static 0.83 --context-length 172032 --chunked-prefill-size 4096 --max-prefill-tokens 4096 --prefill-decode-interval 16 --mamba-radix-cache-strategy no_buffer --disable-overlap-schedule`, env `SGLANG_OPT_MAMBA_SKIP_DECODE_LOCK=1`, `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`; pool 177,010 tokens, max context 167,932 | REG data record `qwen38-27b-exl3-3bpw-c4-mtp-vision-rtx3090-sglang-tp1` | 2026-09-26 | SOLID (vendor-run) |
| C0.15 | The cost the same record states: "the C4 cells at 32K cannot hold four decoding streams on this card (short answers end before the fourth cold 32k prefill is served; greedy 10k-token long-form answers loop), so a C4 claim fails gate 7"; `accepted_at: null`; failed gates "panel incomplete", "panel G0 C4/ctx32768/prose/thinkoff: flagged:LOOP,STREAM_ENDED,UNDERFILLED" | same record (`description`, `metadata.acceptance`) | 2026-09-26 | SOLID (vendor-run) |
| C0.16 | The C4 panel at a 32,768-token prompt: aggregate 74.21 tok/s, 61.19 per stream, prefill 541.0 tok/s, TTFT p50 54,636 ms, p95 160,244 ms, 18 samples, flagged. The same record's prose: "C4/32K 10-minute soak passed (TTFT p95 78.7 s < 4x cold)" | REG speed sweep `…-c4-mtp-vision-…-sweep.json` row `C4/ctx32768/prose/thinkoff`; data record `description` | 2026-09-26 | SOLID (both rows, vendor-run) |
| C0.17 | Brief context for the two TTFT rows: OmniRoute ends a request whose first event takes longer than 80 s (504) | brief lines 40-41 | 2026-10-01 | SOLID (the brief's statement) |

### C1. Published comparisons of SGLang and vLLM

| # | Fact or claim | Source | Source date | Who ran it | Mark |
|---|---|---|---|---|---|
| C1.1 | Same card, same model, SGLang fork only (no vLLM in the same run), C1 vs C4 vs C8 aggregate decode (prompt ~0, "per-stream decode, 3 waves, T 0"): no drafter C1 prose 52.4, C4 195.5, C8 362.5 agg; NEXTN 3/1/4 C1 95.2 to 96.9, C4 277.6 to 278.7 (code 408.0 to 408.7); NEXTN 3/1/4 on the C8 launch: "C8 prose 349.1 agg (below no-drafter), pool 129,569", rejected at C8; NEXTN 1/1/2 on C8: "C8 prose 413.3 agg (+14 %), pool 172,661" | REG data records, `metadata.tuning` (both MTP-vision records) | 2026-09-26 | the fork's author (vendor-run for the fork) | SOLID |
| C1.2 | This project's vLLM on the same card and model family (W4A16 AutoRound): about 45 tok/s single-request decode in the batch profile, near-linear to about 310 tok/s at 7 lanes; batch C64 about 1,035 tok/s ("Container-measured batch: ~1,042 tok/s @ C64"); the image's single-user profile 118 to 133 tok/s (382 with DFlash2, the image doc's reproduction) | `docs/research/findings/VLLM-MIGRATION.md:32-33,85,91-92` at PIN (premise-verified) | 2026-09-16 to 2026-09-26 | this project (C64 figure: the image's doc and a container run) | SOLID (as recorded) |
| C1.3 | Same engine, two weight formats, one 3090: "AWQ-INT4 in the same engine on a bare 3090 (prior validated recipe, no draft): 45 tok/s" | REG data record `qwen38-27b-exl3-3bpw-rtx3090-sglang-tp1` `description`; plugin README A1.19 | 2026-09-23 | the fork's author | SOLID (vendor-run) |
| C1.4 | A vLLM issue claims SGLang is "approximately 3.1× to 5.3×" faster on Qwen3.5-35B-A3B on one GPU; a reply in the same thread posts `vllm bench serve … --max-concurrency 32 --random-output-len 1024 --num-prompts 256` with vLLM output throughput 1,743.30 tok/s and states "vLLM outperformed SGLang under the default configurations" | `https://github.com/vllm-project/vllm/issues/36215` (Exa result highlights; thread not read in full) | 2026-03-06 | issue author and a commenter (third parties) | UNSURE (secondary excerpt; the two sides disagree; hardware not in the excerpt) |
| C1.5 | Third-party blog posts compare the two (RunPod "SGLang vs vLLM: Multi-Turn Chat and KV Cache Reuse", undated; Jarvislabs "SGLang vs vLLM: H100 Benchmarks, with TensorRT-LLM", 2026-05-18); a hobby repository claims "SGLang beats vLLM by 4.5× under 16 concurrent requests" | `https://www.runpod.io/blog/sglang-vs-vllm-kv-cache`; `https://jarvislabs.ai/blog/vllm-sglang-trtllm-comparison`; `https://github.com/zkzkGamal/concurrent-llm-serving` (search highlights only) | 2026-03 to 2026-05 | third parties | UNSURE (not read; not hybrid-on-Ampere) |
| C1.6 | A vLLM-Ascend issue reports that with the experimental mamba `align` mode, prefix caching made Qwen3.5-35B slower ("Qwen3-30B-W8A8 becomes almost 2x faster than Qwen3.5-35B-W8A8") on Ascend 910B | `https://github.com/vllm-project/vllm-ascend/issues/11711` (search highlight) | undated in the result | third party | UNSURE (other hardware; not read in full) |
| C1.7 | A primary-source SGLang-vs-vLLM comparison on a hybrid GDN model, on Ampere or a 24 GiB card, with multi-turn shared prefixes | NOT FOUND (one Exa search, 8 results; the registry branch `vllm-sglang-runs` is "tested vLLM and SGLang recipes on Blackwell and Ada", not read further) | — | — | — |

### C2. Speculative decoding above one request

| # | Fact or claim | Source | Source date | Mark |
|---|---|---|---|---|
| C2.1 | SGLang runs EAGLE/NEXTN with more than one request: the C4 launch runs NEXTN 3/1/4 with `--max-running-requests 4` and decode CUDA graphs for bs 1-4 (`"graph_mode": "full decode CUDA graphs (bs 1-4)"`), with the overlap scheduler disabled in that launch | REG C4 data record (`engine.graph_mode`, `launch.arguments`) | 2026-09-26 | SOLID (vendor-run) |
| C2.2 | Effect as concurrency grows, on this card and model: at C4 the drafter raised aggregate prose from 195.5 to 277.6 tok/s and code from 198.1 to 408.7; at C8 NEXTN 3/1/4 fell below the no-drafter run (349.1 vs 362.5) and shrank the pool to 129,569 tokens; NEXTN 1/1/2 at C8 gave 413.3 (+14 %) with pool 172,661 | REG `metadata.tuning` (C1.1) | 2026-09-26 | SOLID (vendor-run) |
| C2.3 | vLLM side: the live Quadlet sets `SPEC=mtp`, but the engine logs `speculative_config=None` (the batch profile runs no speculative decoding); the project doc says "Serving mode: batch mode (SPEC=mtp, GPU_UTIL 0.90) for the fire-and-forget lanes; single-user DFlash2 mode is available" | brief lines 34-36, 334; `docs/research/findings/VLLM-MIGRATION.md:34,56-57` | 2026-09-26 / 2026-09-16 | SOLID |
| C2.4 | Why the image's batch profile runs without MTP (its README or entrypoint) | NOT FOUND (the `syv-ai/qwen38-27b-rtx3090` image source was not read in this lane) | — | — |

### C3. Ampere (sm_86) support for each piece

| # | Fact or claim | Source | Source date | Mark |
|---|---|---|---|---|
| C3.1 | SGLang's default attention backend for an MHA model (Qwen) off Hopper/Blackwell: "we will use flashinfer if available, otherwise use triton"; FA3 is chosen only on Hopper ("We will turn on FA3 on hopper …") | SGL `arg_groups/model_override_base.py:295-343` | v0.5.20 | SOLID |
| C3.2 | GDN (linear attention) kernels: `--linear-attn-backend` default `triton`; SGLang carries its own FLA port (`sglang.kernels.ops.attention.fla.chunk_delta_h`) | SGL `fields/exec_.py:397-403`; `arg_groups/overrides.py:1908-1910` | v0.5.20 | SOLID |
| C3.3 | fp8_e4m3 KV on sm_86 in SGLang: the fork's runs on an RTX 3090 with `--kv-cache-dtype fp8_e4m3` passed (ladder to 258,040 tokens; six gates) | REG data records and proofs | 2026-09-23 to 2026-09-28 | SOLID (vendor-run); which attention backend those runs used: NOT FOUND (no run log published) |
| C3.4 | EXL3 kernels on sm_86: the image is built with `TORCH_CUDA_ARCH_LIST=8.6`; the plugin README: "Ampere (RTX 3090, sm_86) first"; its Dockerfile comment: "for Ampere (sm_86) and up" | A1.7; A1.10; IMGB `sglang-exl3/src/README.md:3` | 2026-09-23 / 2026-09-26 | SOLID |
| C3.5 | The vLLM path on sm_86: the live engine runs on the 3090 with `kv_cache_dtype=fp8`, `mamba_ssm_cache_dtype float16`, compressed-tensors W4A16 | brief lines 333-334 | 2026-09-26 | SOLID (as measured) |
| C3.6 | Each dependency's own arch gate read in build code (FlashInfer, FLA, exllamav3 setup) | NOT FOUND within the re-prioritized time; only the image's `TORCH_CUDA_ARCH_LIST=8.6` (C3.4) was read | — | — |

## D. Compatibility with this project's clients

All SGLang rows are SGL (v0.5.20) source, `python/sglang/srt/entrypoints/openai/` unless another path is given. The fork
adds no API code (A1.10, A1.13). Project files are cited at the PIN 610cb123.

### D1. `/v1/completions` with token ids (`scripts/qwen_jev.py`)

| # | Fact or claim | Source | Source date | Mark |
|---|---|---|---|---|
| D1.1 | A `prompt` that is a list of ints is passed as `input_ids` (a string, or a list of strings, goes as `text`) | `serving_completions.py:96-102` | v0.5.20 | SOLID |
| D1.2 | `logprobs: N` sets `return_logprob=True`, `top_logprobs_num=N`; with `echo` false `logprob_start_len = -1` (no prompt logprobs), so `top_logprobs[0]` belongs to the first generated token | `serving_completions.py:76-91,115-121` | v0.5.20 | SOLID |
| D1.3 | Each `top_logprobs` entry is a dict of token text to logprob: `{token[2]: token[0] for token in tokens}` (the shape `qwen_jev.py:277-282` requires) | `openai/utils.py:34-41` | v0.5.20 | SOLID |
| D1.4 | `model` in the response is `request.model` (echoed), so `qwen_jev.py:270` (`served != self.sent_id`) compares the id it sent with itself; the completions validator checks only for an empty prompt, not the model name | `serving_completions.py:62-68,385,462,485,631` | v0.5.20 | SOLID |
| D1.5 | `usage.prompt_tokens` comes from the engine's `meta_info["prompt_tokens"]` per choice | `serving_completions.py:237-259,391`; `UsageProcessor` | v0.5.20 | SOLID (path); UNSURE that it equals `len(token_ids)` in every case (not tested) |
| D1.6 | SGLang's own tests for this shape | NOT FOUND within the time (not searched) | — | — |
| D1.7 | The live vLLM path this replaces: `qwen_jev.py:184` documents "the dict, token string to logprob, as vLLM /v1/completions" | `scripts/qwen_jev.py:184,208-211,270-282` (premise lines 279-286) | PIN | SOLID |

### D2. Chat completions (OmniRoute's Hermes traffic; `scripts/s1_synth.py`)

| # | Fact or claim | Source | Source date | Mark |
|---|---|---|---|---|
| D2.1 | Tool parser `qwen3_coder` exists (`"qwen3_coder": Qwen3CoderDetector`); reasoning parser `qwen3` exists (`"qwen3": Qwen3Detector`) | `python/sglang/srt/function_call/function_call_parser.py:98`; `python/sglang/srt/parser/reasoning_parser.py:2181` | v0.5.20 | SOLID |
| D2.2 | Reasoning text field: `reasoning_content`, in streamed deltas (when a reasoning parser is set and `separate_reasoning`, default `True`) and in the final message (`ChatMessage(… reasoning_content=reasoning_text if reasoning_text else None)`) | `serving_chat.py:835-860,2257-2261`; `protocol.py:936` | v0.5.20 | SOLID |
| D2.3 | `chat_template_kwargs` per request (and `--default-chat-template-kwargs` server default, request wins); `enable_thinking` read from it | `serving_chat.py:568,1210-1214,1241-1242`; `arg_groups/fields/serving.py:200-209` | v0.5.20 | SOLID |
| D2.4 | `seed: Optional[int]` on both request types; `stream_options` with `include_usage` (default False) and `continuous_usage_stats` | `protocol.py:218,349,352,874,877`; `openai/utils.py:92-102` | v0.5.20 | SOLID |
| D2.5 | `usage.prompt_tokens_details.cached_tokens` only with `--enable-cache-report` ("Return number of cached tokens in usage.prompt_tokens_details for each openai request", default False; the recipe does not set it) | `arg_groups/fields/serving.py:187-190`; `serving_completions.py:623-627` | v0.5.20 | SOLID |
| D2.6 | The model name: chat's validator checks messages and tools, not the model; streamed chunks carry `model=request.model` | `serving_chat.py:950-990,857,904,932` | v0.5.20 | SOLID (validator lines read 950-990) |
| D2.7 | The fork's six gates exercised tools (`get_weather` with `{"city": "Paris"}`, the reply used the result) and separate thinking (118 thinking chars, answer `391`) through this parser pair | PR #137 evidence JSON (A2.11) | 2026-09-28 | SOLID (vendor-run, one sample each) |
| D2.8 | `s1_synth.py` sends exactly `model, messages, max_tokens, temperature, chat_template_kwargs` and never `prompt_logprobs`, `best_of`, `echo`, `n` (AF-AP-201) | `scripts/s1_synth.py:168-169,773-786` (premise lines 287-296) | PIN | SOLID |
| D2.9 | How SGLang handles `prompt_logprobs` / large logprob requests memory-wise (the AF-AP-201 class) | NOT FOUND within the time | — | — |

### D3. The serving surface

| # | Fact or claim | Source | Source date | Mark |
|---|---|---|---|---|
| D3.1 | `--served-model-name` is ONE string (`Optional[str]`, "Override the model name returned by the v1/models endpoint"); `/v1/models` lists exactly `[tokenizer_manager.served_model_name]` (plus LoRA adapters). vLLM's takes several (the live server serves two, brief line 333) | `arg_groups/fields/serving.py:163-166`; `entrypoints/http_server.py:1868-1897` | v0.5.20 | SOLID |
| D3.2 | Requests naming another model are not refused by the OpenAI handlers (D1.4, D2.6), so a second alias would be answered but not listed by `/v1/models` | D1.4, D2.6, D3.1 | v0.5.20 | UNSURE (derived from the validators read; not tested) |
| D3.3 | API key: `--api-key` ("Set API key of the server. It is also used in the OpenAI API compatible server"); the middleware is installed when it is set. No `*_API_KEY` environment variable for it in `environ.py` (the only one is `EXA_API_KEY`). A YAML file can carry any CLI option: `--config` "Read CLI options from a config file" (merged inside the process) | `arg_groups/fields/serving.py:155-158`; `http_server.py:2588-2606`; `environ.py:734-737`; `server_args.py:395-400,704-711` | v0.5.20 | SOLID (flags); UNSURE that a key given through `--config` stays out of the process list (inference: argv holds only the file path) |
| D3.4 | `/health` and `/health_generate` routes exist | `http_server.py:669-670` | v0.5.20 | SOLID |
| D3.5 | `/metrics` needs `--enable-metrics` (default False; the recipe does not pass it) | `arg_groups/fields/observability.py:77`; `http_server.py:287-289,2573-2574` | v0.5.20 | SOLID |
| D3.6 | SGLang metric names for the same facts: `sglang:num_running_reqs`, `sglang:num_queue_reqs`, `sglang:token_usage`, `sglang:full_token_usage`, `sglang:mamba_usage`, `sglang:cache_hit_rate`, `sglang:cached_tokens_total`, `sglang:prompt_tokens_total`, `sglang:generation_tokens_total`, `sglang:num_retracted_requests_total`, `sglang:time_to_first_token_seconds`, `sglang:inter_token_latency_seconds`, `sglang:queue_time_seconds`, `sglang:gen_throughput`, `sglang:spec_accept_length`, `sglang:spec_accept_rate`, `sglang:max_total_num_tokens` | `python/sglang/srt/observability/metrics_collector.py` (lines 280-1754) | v0.5.20 | SOLID |
| D3.7 | What this project's tools parse AT THE PIN: `qwen-server.sh` decides idle from `llamacpp:requests_processing` (`:331-332`; absent metric prints `busy`) and starts llama-server-style flags (`:122` `--metrics --slots`); `qwen_matrix.py` REQUIRES `llamacpp:prompt_tokens_total`, `llamacpp:tokens_predicted_total`, `llamacpp:prompt_seconds_total`, `llamacpp:tokens_predicted_seconds_total` (`:23-27,197-213`) and reads llama.cpp's `/props` (`:324-342`). Neither names a `vllm:` metric; last changed `a670c803` 2026-09-16 | `harness-ports/bin/qwen-server.sh`, `harness-ports/bin/qwen_matrix.py` at PIN | 2026-09-16 | SOLID |
| D3.8 | The vLLM names the coordinator read on the live server: `vllm:num_requests_running`, `vllm:num_requests_waiting`, `vllm:num_requests_waiting_by_reason`, `vllm:kv_cache_usage_perc`, `vllm:prefix_cache_queries_total`, `vllm:prefix_cache_hits_total`, `vllm:num_preemptions_total` | brief lines 340-348 | 2026-10-01 | SOLID (as measured) |

### D4. The container

| # | Fact or claim | Source | Source date | Mark |
|---|---|---|---|---|
| D4.1 | Fork image `84f75f…`: amd64 only, 77 layers, 15,352,065,249 compressed bytes; no `User` (runs as the image's root, which rootless podman maps to the invoking user); exposes 22 and 30000; installs `openssh-server` | GHCR manifest and config (A1.7, A1.10) | 2026-09-23 | SOLID |
| D4.2 | Live vLLM image `ghcr.io/syv-ai/qwen38-27b-rtx3090@sha256:c52d9033…`: 15 layers, 4,551,792,695 compressed bytes, no `User` | GHCR manifest and config, read 2026-10-01 | — | SOLID |
| D4.3 | Both images carry `CUDA_VERSION=13.0.3` and `NVIDIA_REQUIRE_CUDA=cuda>=13.0 …` (same string head), so the PC's driver already runs a CUDA 13.0.3 image (the live vLLM) | both configs | 2026-10-01 | SOLID (configs); the PC's driver version itself: NOT FOUND (not in the premise; bridge off limits) |
| D4.4 | The recipe uses Docker's `--gpus all` and `--shm-size 16g`; the live Quadlet uses `PodmanArgs=--ipc=host --device nvidia.com/gpu=all` (CDI) | recipe page lines 15-26; `deploy/qwen.container:39` (premise line 249) | 2026-10-01 / PIN | SOLID |
| D4.5 | The fork's runs were made with Docker ("runtime": "docker", `network_mode: bridge`, launched by `omarchy-local-ai`); no record of rootless podman or CDI in the registry | REG data record `launch` | 2026-09-23 | SOLID (what is recorded); rootless podman + CDI with this image: NOT FOUND |
| D4.6 | `minDriver: ""` in the launch file (no stated minimum) | REG launch file | 2026-10-01 | SOLID |

### D5. The change list (no edits made; the line and why)

| File (PIN) | Line(s) | What would change and why | Mark |
|---|---|---|---|
| `deploy/qwen.container` | 21 `Image=…syv-ai…@sha256:c52d9033…`; 22 `Exec=batch`; 23 `PublishPort=8080:8080`; 27-38 `Environment=PORT/SPEC/MAX_LEN/PREFIX_CACHE/GPU_UTIL/EXTRA_ARGS`; 39 `PodmanArgs` | The image and digest; `Exec` becomes the SGLang argv (the fork's entrypoint execs it, A1.18); the env knobs are the vLLM image's own and have SGLang flags instead (`--context-length`, `--mem-fraction-static`, `--served-model-name`, …); the container port is 30000 unless `--port 8080`; `EXTRA_ARGS` passes two served names, SGLang takes one (D3.1); the key file needs `--api-key` or a `--config` YAML (D3.3) | SOLID (lines); UNSURE (the replacement form) |
| `upstream.lock.yaml` | 228-232 (`image`, `digest`, `base_model`, `engine`, `served_model_names`) | All five values change (fork image, EXL3 weights `turboderp/Qwen3.8-27B-exl3@6fe61ad6`, engine "SGLang v0.5.20 + sglang-exl3 plugin"); the file is an attested input of S0-06 and S0-12 (`proofs/registry.yaml:17,23`), and D-110: a change voids both attestations (brief lines 59-60) | SOLID |
| `harness-ports/bin/qwen-server.sh` | 30-32 (alias, port); 122 (llama-server flags); 221-225 (`/health` then `/v1/models` must list the alias); 331-332 (idle from `llamacpp:requests_processing`) | `/health` exists in SGLang (D3.4); `/v1/models` lists one name (D3.1); the idle check needs `--enable-metrics` and `sglang:num_running_reqs`/`sglang:num_queue_reqs` (D3.5, D3.6); note the PIN version already reads llama.cpp names, not vLLM's (D3.7) | SOLID |
| `harness-ports/bin/qwen_matrix.py` | 20 (`:8080`); 23-27 `REQUIRED_METRICS` (llamacpp names); 197-213 parser; 306 default model; 324-342 `/props` | SGLang has neither `llamacpp:*` counters nor llama.cpp's `/props`; equivalents are `sglang:prompt_tokens_total`, `sglang:generation_tokens_total`, `sglang:time_to_first_token_seconds` (D3.6); `/props`' replacement not checked | SOLID (lines); NOT FOUND (`/props` equivalent) |
| `harness-ports/bin/omniroute_local_builder.py` | 44 `LOCAL_URL …:8080`; 46 `ALIAS "qwen3.8-27b-local"` ("what llama-server --alias serves"); 58 `chatPath`, `modelsPath` | Unchanged if the server keeps port 8080 and serves `qwen3.8-27b-local` as its one name; the OpenAI paths exist in SGLang (`http_server.py:1739,1747,1868`) | SOLID |
| `scripts/gpu_window.sh` | 49, 59 (`/v1/models` back-check on :8080); 89-140 (`systemctl --user` stop/start of the unit) | Unchanged if the unit name, port and `/v1/models` stay; the "reduces its KV" path named in the brief (line 51) was not found by a grep for `kv`/`util`/`mem` in this file | SOLID (lines); UNSURE (the KV path) |
| `scripts/qwen_jev.py` | 184, 208-211, 270-282 | Body shape accepted (D1.1-D1.3); `model` echo makes `:270` pass trivially (D1.4); `:274` depends on `usage.prompt_tokens` equality (D1.5) | SOLID / UNSURE as in D1 |
| `scripts/s1_synth.py` | 44, 168-176, 773-786 | Body keys supported (D2.3); the AF-AP-201 rationale is vLLM's memory behaviour, SGLang's not checked (D2.9) | SOLID (lines) |
| `harness-ports/bin/lane-profile.sh`; `scripts/t93r1_apply_profile.sh` | 19; 64 | Route and model ids only; unchanged if the served id stays `qwen3.8-27b-local` | SOLID |
| Tests and fixtures: `harness-ports/tests/test_lane_profile.sh`, `test_omniroute_local_builder.py`, `test_pc_lane_dispatcher.sh`, `test_qwen_server.sh`; `tests/fixtures/qwen_jev/completion-choice.json`, `completion-noul.json`; `tests/test_gpu_side_by_side.py`, `test_qwen_jev.py`, `test_s1_synth.py` | not read line by line | They match the server strings above (premise line 259-277); the fixtures encode the response shape D1 compares | UNSURE (lines not read) |

## E. Risk and upkeep (brief, per the coordinator's re-prioritization)

### E1. Open issues for Qwen3.8 / Qwen3-Next-class hybrids

Searches: two semantic issue searches in `sgl-project/sglang`, sorted by update; the first matched 765 issues, the second
418; only the top 12 and 8 were read, so absence of other issues is UNVERIFIED. The fork's plugin repository is private
(A1.11): its issues NOT FOUND.

| # | Item | State, dates | Source | Mark |
|---|---|---|---|---|
| E1.1 | "Prefill CUDA graph reserves ~1.8 GB and starves quantized-KV long-context prefill on small cards (no auto-disable rule looks at free VRAM)" | open, created 2026-09-18 | `https://github.com/sgl-project/sglang/issues/40094` | SOLID (title, state) |
| E1.2 | "--enable-linear-replayssm forces no_buffer, which degrades mamba prefix caching and inflates TTFT up to 4.7x" (the C4 launch uses `no_buffer`, C0.14) | open, created 2026-09-03 | `…/issues/37834` | SOLID (title, state) |
| E1.3 | "[Bug][Simulator] --max-total-tokens on a hybrid mamba/GDN model crashes with TypeError: NoneType // int — the mamba sizing step is skipped on that branch" | open, created 2026-09-29 | `…/issues/41654` | SOLID (title, state) |
| E1.4 | "[Bug] Qwen3.8-Flash-Next thinking + qwen3_coder tool parser loops on token ID 0" | closed 2026-09-25, created 2026-08-26 | `…/issues/36537` | SOLID (title, state) |
| E1.5 | "[Bug] Qwen3 Coder buffers large string tool-call arguments during streaming" | closed 2026-08-02, created 2026-06-02 | `…/issues/27005` | SOLID (title, state) |
| E1.6 | The fork's own record of looping: "greedy 10k-token long-form answers loop" at C4/32K; panel flag `LOOP` | 2026-09-26 | REG C4 data record (C0.15) | SOLID (vendor-run) |
| E1.7 | vLLM side, open: PR #55601 "[Bugfix] Seed hybrid mamba state index with mamba_block_size on prefix-cache hits" | open, created 2026-09-06 | B3.7 | SOLID (title, state) |
| E1.8 | Issues on radix cache × speculative decoding interactions specifically | NOT FOUND in the rows read | — | — |

### E2. Release cadence and pinning

| # | Fact | Source | Mark |
|---|---|---|---|
| E2.1 | SGLang tags `v0.5.15` … `v0.5.20` (= `94602c9c`, the fork's base) and `v0.5.21` (`e00930c5`) exist; dates not read | `git ls-remote --tags https://github.com/sgl-project/sglang` (2026-10-01) | SOLID (tags); NOT FOUND (dates) |
| E2.2 | vLLM tags after the live `v0.28.0` (`2cf0a691`): `v0.28.1rc0`, `v0.29.0`, `v0.30.0` (`ced6857a`) | `git ls-remote --tags https://github.com/vllm-project/vllm` | SOLID |
| E2.3 | The fork image: eight tags `v0.1.0-ampere` to `v0.7.0-multiarch` plus `ft-flashnext-2677501` within about ten days; the recipe pins `v0.5.1-ampere`'s digest; the registry's newer launches pin `v0.7.0-ampere` (`c8922bd7`) | A1.2; REG 208k/C4 records | SOLID (tags); UNSURE (dates, relative) |
| E2.4 | How the fork follows upstream: the plugin is vendored at a recorded commit (`VERSION`) into `local-ai-images` and built FROM a digest-pinned `lmsysorg/sglang:v0.5.20`; it needs "no SGLang source edits" but imports SGLang internals (A1.24); every published digest "carries BuildKit provenance, an SBOM, and a GitHub build attestation" | IMGB `sync-src.sh`, `Dockerfile:1-6`; IMG `README.md:3-9` | SOLID |
| E2.5 | The registry's own CI: "ci: verify every FROM is digest-pinned before a release build" (local-ai-images commit `0610a84`, 2026-09-21) | `…/local-ai-images/commits/sglang-exl3-image/` | SOLID |

## F. Inputs for the A/B design (evidence only)

| # | Fact | Source | Mark |
|---|---|---|---|
| F1.1 | SGLang metrics for TTFT, decode, throughput, cache, retractions, queue: D3.6 (requires `--enable-metrics`, D3.5) | SGL `observability/metrics_collector.py` | SOLID |
| F1.2 | vLLM metrics the live server exposes: D3.8; this project's tools at the PIN parse neither engine's names (D3.7) | brief lines 340-348; D3.7 | SOLID |
| F2.1 | SGLang's benchmark: `python -m sglang.bench_serving` still works but is "deprecated", the code lives in `sglang.benchmark.serving`; options `--backend`, `--base-url`, `--dataset-name`, `--num-prompts`, `--random-input-len`, `--random-output-len`, `--request-rate`, `--max-concurrency`, `--seed`, `--disable-ignore-eos`; shared-prefix workload `generated-shared-prefix` with `--gsp-num-groups`, `--gsp-prompts-per-group`, `--gsp-system-prompt-len`, `--gsp-question-len`, `--gsp-output-len`; other datasets include `sharegpt`, `random`, `random-ids`, `mooncake`, `custom`, `openai` | SGL `python/sglang/bench_serving.py:1-19`; `python/sglang/benchmark/serving.py:2211-2645`; `benchmark/datasets/__init__.py` | SOLID (options exist); multi-turn chat replay: UNSURE (not confirmed for any dataset) |
| F2.2 | vLLM's `vllm bench serve`: `--backend`, `--base-url`, `--endpoint`, `--max-concurrency`, `--request-rate` at v0.28.0; its dataset module (`vllm/benchmarks/datasets.py`) is not at that path at the tag (404), datasets not read | VLL `vllm/benchmarks/serve.py:1558-1658` | SOLID (options); NOT FOUND (dataset list, multi-turn) |
| F2.3 | The registry's `lab.py` targets any OpenAI-compatible endpoint (`--on endpoint --endpoint URL`) and runs the six gates with single samples (A2.5-A2.8) | REG `lab/lab.py` | SOLID |
| F3.1 | A short check the fork's author used to compare numerics: "top-20 logprob KL vs fp32-acc 0.0015 nats (chunk-size change alone 0.0010)" | REG `metadata.tuning` | SOLID (vendor-run; method details not published) |
| F3.2 | vLLM has an open PR "[Core] Add score mode with perplexity and KLD computation" (#35961, created 2026-03-04) | GitHub PR search result | SOLID (exists, open) |
| F3.3 | A named fixed quality check that separates 3-bit from 4-bit on this model class within a GPU window | NOT FOUND (A4 tables not extracted, see A4) | — |

## G. Gaps index

NOT FOUND (a cell this lane could not fill; the row says which searches ran):
- A1.20 the "aikido-exl3" kernels' license; A1.22 the private plugin repository's activity and issues; A2.17 the
  `rtx-3090/bench/harness.py` source that produced the speed sweeps.
- A4.3 EXL3 3.0 bpw and W4A16 AutoRound quality tables (perplexity, KL, benchmark deltas): not extracted.
- B1.12 when SGLang's hybrid (mamba) radix cache arrived; B3.8 the content of the vLLM image's
  `mamba-chunked-prefill-align.patch`.
- C1.7 a primary-source SGLang-vs-vLLM comparison on a hybrid model on Ampere or a 24 GiB card; C2.4 why the vLLM
  image's batch profile runs without MTP; C3.3 the attention backend the fork's 3090 runs used; C3.6 each dependency's
  arch gate in its build code.
- D1.6 SGLang's own tests for the token-id completions shape; D2.9 SGLang's memory behaviour for `prompt_logprobs`-class
  requests; D4.3 the PC's NVIDIA driver version; D4.5 any run of the fork image under rootless podman with CDI; D5 the
  replacement for llama.cpp's `/props` in `qwen_matrix.py`.
- E1.8 radix-cache-with-speculative-decoding issues; E2.1 SGLang tag dates; F2.2 vLLM's benchmark dataset list and
  multi-turn replay at v0.28.0; F3.3 a short fixed 3-bit-versus-4-bit quality check.

UNSURE rows that are derived arithmetic or inference (inputs SOLID): B1.9 (ratio 5, so 5 slots = 1 request), B1.11 and
C0.9 (state and KV bytes), B3.4 (vLLM's 800-token block for this model), C0.12 (chats per pool), C0.4 (eager fallback),
D3.2 (a second alias answered but not listed), D3.3 (a `--config` key stays out of the process list).

Contradictions recorded with both rows: decode 135.0 (09-26) vs 110.0 (09-28) vs 138.8 (09-25) tok/s (A2.3); KV pool
212,823 vs 272,369 tokens in one record (C0.11); C4/32K TTFT p95 160.2 s (panel) vs 78.7 s (soak prose) (C0.16);
embedding 2.4 GB vs 2.5 GB (A1.14, A1.15); vLLM KV 222,822 vs 215,112 tokens before and after D-099 (B4.5); a vLLM issue
claiming SGLang 3.1-5.3x faster vs a reply measuring vLLM ahead (C1.4); `local-ai-images` "Open issues: 1" vs an empty
issues page (A1.21).

## H. Coordinator addendum at harvest (2026-10-01 22:2xZ): vLLM's own host-memory KV tier

The lane covered SGLang's host-memory tier (HiCache, B1.13) and not vLLM's. The coordinator read vLLM v0.28.0's raw
files at the tag (VLL as above):

| # | Fact | Source | Mark |
|---|---|---|---|
| H1 | `--kv-offloading-size` (GiB): "By default, this is set to None, which means no KV offloading is enabled. When set, vLLM will enable KV cache offloading to CPU using the kv_offloading_backend." `--kv-offloading-backend`: `native` (the default) or `lmcache` | VLL `vllm/config/cache.py:189-198`; `vllm/engine/arg_utils.py:746-747,1253-1256` | SOLID |
| H2 | `native` selects `OffloadingConnector` (`SimpleCPUOffloadConnector` when `VLLM_USE_SIMPLE_KV_OFFLOAD` is set), with `cpu_bytes_to_use` = the size × 2^30 and the role `kv_both` | VLL `vllm/config/vllm.py:948-982` | SOLID |
| H3 | The connector declares hybrid support (`class OffloadingConnector(KVConnectorBase_V1, SupportsHMA)`). A Mamba group is a one-chunk window ("Mamba depends on a single state"); in `align` or `all` mode the hit window is rounded down to the offloaded chunk size; MTP/EAGLE draft groups have their own rule (`is_eagle_group`); a hybrid needs `--enable-prefix-caching` so that the block sizes align | VLL `kv_connector/v1/offloading_connector.py:49`; `kv_connector/v1/offloading/scheduler.py:100-125,149-169`; `kv_connector/v1/offloading/config.py:58-65` | SOLID (code); UNSURE (never run on this model) |
| H4 | A preempted request's pending stores are flushed before its blocks are reused, and a later lookup (`get_num_new_matched_tokens`) loads the tokens the CPU tier holds beyond the GPU prefix-cache hit: a preempted chat can reload from host memory instead of recomputing | VLL `kv_connector/v1/offloading/scheduler.py:936-960,1453-1459` | SOLID (code path); UNSURE (never run) |
| H5 | The live unit runs prefix caching (`Environment=PREFIX_CACHE=1`), so its state cache is in `align` mode (B3.2). The unit does not set `--kv-offloading-size`. It passes extra vLLM flags through `EXTRA_ARGS` (it sets `--served-model-name qwen3.8-27b-local qwen3.8-27b` that way), so the flag has a place to go; the unit also sets `SPEC=mtp`, while C2.4 records the `batch` profile running without MTP | `deploy/qwen.container` (`Exec=batch`, the `Environment=` lines); B3.2; C2.4 | SOLID (the unit's lines); UNSURE (how the profile orders `EXTRA_ARGS` against its own flags: not read) |

What this changes for the A/B (a design input, not a verdict): both servers can park a waiting chat's KV in host
memory and reload it, SGLang through HiCache and vLLM through `--kv-offloading-size`; both are off today. A fair test
runs each with its tier on, at the same host-memory budget, on the same multi-chat load, beside the recipe's defaults
and the live unit's defaults.

## I. Community and third-party evidence (the owner's D-129: "use Exa search"; read 2026-10-02 00:1xZ)

Seven Exa searches and two page reads, aimed at the owner's question: which engine serves Hermes-style agent loops
(long multi-turn chats, tool calls, several sessions at once) better. Kind of source: M = measured by the writer, C =
claimed without a published method, U = a user's own report, P = a project that ran both engines.

| # | Source | What it says | Kind |
|---|---|---|---|
| I1 | RunPod, "SGLang vs vLLM: Multi-Turn Chat and KV Cache Reuse" (runpod.io/blog/sglang-vs-vllm-kv-cache) | Equal on fresh context; RadixAttention "about a 10% boost over vLLM at the same context loads" in larger multi-turn conversations once the cache is used; "SGLang emerges as the clear winner for ... multi-turn conversations with shared context" | M |
| I2 | DeepInfra, "vLLM vs SGLang" (deepinfra.com/blog/vllm-vs-sglang, 2026-08-04) | The radix tree handles partial and branching overlap, "the exact shape of agent traces and multi-turn conversations"; "Go with SGLang if you measured high prefix reuse, run multi-turn conversations or agentic traffic against a stable preamble" | C (cites I1's ~20%) |
| I3 | ByteByteGo newsletter, "Ollama vs vLLM vs SGLang" (2026-08-22) | "SGLang is best for AI agents and tool loops, multi-turn chats, and JSON/regex outputs"; vLLM "best for high-traffic serving ... thousands of concurrent requests" | C |
| I4 | Spheron, "vLLM vs SGLang 2026" (spheron.network/blog/vllm-vs-sglang-2026) | Multi-turn agent: SGLang; at 80% shared prefix and 50 concurrent requests TTFT p50 310 ms (vLLM) against 195 ms; with vLLM's prefix caching on, the gap narrows to about 15-18% at 10 concurrent | M (H100, short prompts) |
| I5 | Effloow, "SGLang RadixAttention vs vLLM on One H100" (2026-09-17) | SGLang ahead on its highest-reuse trace; "Deploy SGLang if ... your agent platform repeatedly sends the same tool definitions ... multi-turn sessions preserve substantial common history" | M |
| I6 | Particula, "SGLang vs vLLM in 2026" (2026-03-26); devcheolu (2026-05-27) | 29% throughput on H100 (Llama 3.1 8B) and "up to 6.4x" on prefix-heavy work; multi-turn p95 TTFT 103 ms against 79 ms | C |
| I7 | dev.to and n1n.ai "architecture showdown" (2026-09-20) | 4,096-token prompts, 75% overlap, 64 concurrent: TTFT p50 380 ms against 85 ms, hit rate 41% against 79% | C (no method or hardware given) |
| I8 | r0b0tlab/hermes-concurrent-agents, `docs/tuning-guide.md` (a Hermes multi-worker project) | "Recommendation: SGLang for multi-agent setups (RadixAttention is the differentiator)"; keep system prompts identical across workers so the KV is reused | P (its table marks vLLM "no" for KV reuse, which overlooks vLLM's prefix caching) |
| I9 | NousResearch/hermes-agent issue #523, a user's comment | Ran "Hermes on vLLM tuned to the hilt for a long time", now runs a tuned SGLang with Qwen 3.6 27B: "Hermes is running, very well" (DGX Spark) | U |
| I10 | hermes-agent.ai, local LLM support page | "vLLM and SGLang are better fits for shared GPU servers and concurrent agent workloads" | C |
| I11 | noonghunna/club-3090, `docs/engines/SGLANG.md` (Qwen3-Next family on RTX 3090s, status 2026-05-21) | Stock SGLang v0.5.12's CUDA-graph capture hung on Ampere (decode 15-18 tok/s without graphs), so the project parked SGLang for this family and kept vLLM with MTP; it calls SGLang "a strong alternative ... RadixAttention prefix sharing" and notes an 8-bit KV floor against vLLM's 3-bit TurboQuant | P (dual 3090, an EAGLE-3 drafter, stock image) |
| I12 | A Reddit thread snapshot (reddit.sentinel-team.org, 2026-09-04) | Several users run Qwen3.8-27B on vLLM with Hermes without trouble (FP8, MTP 2); none compares engines or concurrency | U |

What it adds to sections A to H: the write-ups and the Hermes-specific sources agree with the owner that SGLang is the
engine recommended for agent loops and for several agents at once, and they name the radix tree's reuse of each chat's
history and of the shared system prompt as the reason. The measured gains are on H100s with short prompts (I1, I4,
I5); none measures 50k-90k-token chats on a 24 GiB card. The one Ampere warning (I11, stock SGLang's CUDA graphs
hanging) concerns the stock image; the fork in use (A1) is built for sm_86 and its recipe runs with CUDA graphs and MTP
at 110-139 tok/s (A2.3). The GPU window measures both points on this card.

## J. The GPU window, measured (2026-10-02 00:28:52Z to 01:56:25Z; task #454, D-088; written 02:0xZ)

The coordinator's harness, `scripts/serving_ab/` (task #462; the window ran its scratch copy, the same two Python
files byte for byte), replayed one fixed workload in every arm: `/home/rocco/sglang-ab/workload-1.json` (sha256 prefix
24068ffecf69fe37), four chats whose first prompts are 86,999, 57,000, 77,000 and 67,000 tokens by vLLM's own
`/tokenize` (chat template included), then three follow-up turns of 2,500 tokens each; replies capped at 512 tokens,
thinking off; each run's system prompt opens with its own run id; chats start 20 s apart. A first token later than 80 s
(OmniRoute's first-event limit) counts as a miss. In every run the server's first-turn prompt count equalled the plan
(`turn1_plan_diff_max` 0), so the two servers count these prompts alike.

Arms. **V0**: the live vLLM unit as it runs (`deploy/qwen.container`). **S0**: the recipe as published (A2: one
running request, 5 state slots, prefill chunk 1,024, context 204,800). **S1**: the registry's C4 flags (B1.10: 4
running requests, 12 state slots, `no_buffer`, overlap off, `SGLANG_OPT_MAMBA_SKIP_DECODE_LOCK=1`, chunk 4,096,
context 131,072) plus HiCache (`--hicache-size 24 --hicache-write-policy write_through`). Both SGLang arms ran the
recipe image (A1.1), fp8 KV and MTP (NEXTN 3/1/4). S0 at 3 and 4 chats was skipped by design: over half of its 2-chat
requests missed the limit. S1b (no HiCache) did not run, because S1 booted.

### J1. Per run ("cold" = a chat's first turn; "warm" = turns 2 to 4)

| Arm | Chats | Answered | Past 80 s | Cold first token, p50 (max) | Warm first token, p50 (max) | Decode p50 | Wall |
|---|---|---|---|---|---|---|---|
| V0 | 2 | 8 of 8 | 1 of 8 | 72.1 s (85.9) | 3.2 s (4.1) | 27.4 tok/s | 165 s |
| V0 | 3 | 12 of 12 | 8 of 12 | 88.4 s (122.6) | 84.7 s (183.3) | 5.3 tok/s | 796 s |
| V0 | 4 | 16 of 16 | 15 of 16 | 88.6 s (163.2) | 196.0 s (261.5) | 7.0 tok/s | 1,047 s |
| S0 | 2 | 8 of 8 | 8 of 8 | 132.2 s (185.3) | 200.5 s (215.3) | 76.0 tok/s | 843 s |
| S1 | 2 | 8 of 8 | 2 of 8 | 169.4 s (210.0) | 4.8 s (34.1) | 37.7 tok/s | 273 s |
| S1 | 3 | 12 of 12 | 4 of 12 | 145.2 s (206.6) | 17.9 s (109.3) | 54.4 tok/s | 319 s |
| S1 | 4 | 16 of 16 | 6 of 16 | 144.9 s (254.3) | 32.7 s (178.8) | 50.2 tok/s | 437 s |

No arm had an error, a loop or a request without usage.

### J2. The caches and the servers

| | V0 | S0 | S1 |
|---|---|---|---|
| Prompt tokens served from the prefix cache | 75.4% at 2 chats, 3.6% at 3, 2.7% at 4 (`vllm:prefix_cache_hits_total` over `..._queries_total`, before and after each run; the usage's `cached_tokens` sums agree: 460,000, 33,600, 33,600) | 0: 601 prefill chunks, none with a cached token | 76.0% over its three runs: 2,103,749 of 2,766,856 prompt tokens (the log's `#cached-token`, 29 of 174 chunks) |
| Preemptions or retracts | 1 at 3 chats, 1 at 4 (`vllm:num_preemptions_total`) | 0 in the log | 0 in the log |
| KV pool on the GPU | about 215k tokens (C0.13) | 199,776 tokens | 146,098 tokens, full at 0.98 |
| Host-memory tier | none | none | KV 447,407 tokens (15.58 GB) and states 8.47 GB |
| State slots in use, max | n/a | 0.80 with one request running | 0.83 |
| GPU memory, max sampled | 24,064 MiB | 22,822 MiB | 23,816 MiB |
| Start to serving | 280 s (the restore) | 380 s | 640 s (251.9 s of it capturing the prefill CUDA graphs) |

### J3. What the numbers show

1. **The recipe as published (S0) cannot serve two lanes.** One running request, and no cache hit at all: with one
   request running, the state pool sat at 0.80 and no snapshot was kept (B1.9, now observed). Each turn recomputed the
   whole chat and waited for the other chat's turn, so all 8 requests passed 80 s.
2. **With S1's flags, follow-up turns reuse the cache under load; vLLM's do not.** From 3 chats, vLLM's GPU-only
   prefix cache was evicted turn by turn: 3.6% and 2.7% of prompt tokens hit, so each turn re-read 60k to 95k tokens
   and decode fell to a median of 5.3 and 7.0 tok/s per chat. S1 served 76% of its prompt tokens from the cache with
   its GPU pool full; its warm turns took 3.8 to 5.7 s at 2 chats (one at 34.1 s, behind the other chat's cold
   prefill), and turns 3 and 4 took 23 to 35 s at 4 chats.
3. **S1's slow warm turns waited behind cold prefills.** At 4 chats, chat 0 turn 2 (178.8 s) and chat 1 turn 2 (113.2
   s) arrived while chats 2 and 3 ran their cold first turns. The scheduler takes requests first come, first served:
   `--schedule-policy` defaults to `fcfs` (SGLang `arg_groups/fields/schedule.py:89-104` at v0.5.20); `lpm` serves the
   longest cached prefix first.
4. **Cold first turns are slower on SGLang.** Every S1 first turn of 57k to 87k tokens took over 80 s (106 to 254 s);
   chat 0's 86,999-token first turn, alone for its first 20 s, took 106.3 s and 106.4 s on S1 at 3 and 4 chats (169.4
   s at 2 chats, the arm's first run) against 72.1 to 73.2 s on vLLM.
   The engine also starts slower (640 s against 280 s).
5. **No crash, no error, no retract** on any arm, including S1 with its GPU pool full at 4 chats.

### J4. Gaps this window leaves (added to section G's list)

- A cold long prompt through OmniRoute: OmniRoute ends a request with no first event in 80 s (never changed, standing
  rule), and every S1 cold first turn of 57k tokens or more took longer. Whether a retry after that cut reuses the
  chunks already computed was not measured. A new lane's first turn, a turn right after Hermes compacts, and a resumed
  lane are cold.
- `lpm` scheduling, a larger prefill chunk (for cold prefill speed) and `extra_buffer` with overlap were not run.
- Chats smaller than 57k tokens, and more than 4 at once, were not run (the owner's question is about many lanes).
- `--enable-cache-report` was off on both SGLang arms, so the client-side cached count is vLLM's only; the SGLang
  count comes from the server log.

## K. The second GPU window, measured (S2: 2026-10-02 02:29:13Z to 03:04:52Z; S3: 03:10:26Z to 03:33:15Z; task #454, D-088; written 03:3xZ)

The window script `scripts/serving_ab/abwin2.sh` ran S2 from its first landing. S3's boot then failed: S2's container
outlived two `podman rm -f` calls whose output the script dropped, and `podman run` refused the name ("the container
name sglang-ab is already in use", rc 125). The fixed script (it waits until podman says the container is gone, and runs
the arms `ABWIN_ARMS` names) ran S3 alone in a second, shorter window. Both windows ran the committed bytes, shipped
by sha256 (`chat_load.py` 36864ee7d87a5ef1; `abwin2.sh` 44e4cf0e26911196, then 74ec84164e8f5880). No lane was live,
and vLLM was restored after each window (03:04:52Z, 240 s; 03:33:15Z, 200 s). In the S3 window the container again
outlived `podman rm -f`: the log holds two "could not be stopped" errors at 03:29Z, and the fixed script waited until
podman reported the container gone before it restored vLLM.

Workloads, both sized by vLLM's own `/tokenize`: `workload-1.json` (sha256 prefix 24068ffecf69fe37) is window 1's four
long chats (first prompts 86,999, 57,000, 77,000 and 67,000 tokens). `workload-2.json` (632497c65f726308) is eight
chats of lane size: first prompts 58,000, 24,000, 46,000, 32,000, 52,000, 20,000, 40,000 and 27,999 tokens, from the
repo's own docs, scripts, tasks and tests under its `.hermes.md` as the system prompt, then three follow-ups of 2,500
tokens. Replies are capped at 512 tokens, thinking off, chats 20 s apart, each run's system prompt opens with its own
run id. A cut run (`chat_load.py --cut-after 80 --retries 3`) does what OmniRoute and Hermes do: it ends an attempt
that has sent no event 80 s after it began and sends it again, up to 3 more times. In every run the server's
first-turn count equalled the plan (`turn1_plan_diff_max` 0); no run had a loop or a request without usage.

Arms. **S2**: window 1's S1 (4 running requests, 12 state slots, `no_buffer`, overlap off, chunk 4,096, context 131,072,
HiCache 24 GB write-through) plus `--schedule-policy lpm` and `--enable-cache-report`. **S3**: S2 with a prefill
chunk of 8,192 (`--chunked-prefill-size` and `--max-prefill-tokens`) and `--disable-prefill-cuda-graph`.

### K1. Per run ("cold" = a chat's first turn; "warm" = turns 2 to 4; a cut request's wait counts every attempt)

| Arm | Workload, chats | Answered | Cut at 80 s (requests) | Cold first token, p50 (max) | Warm first token, p50 (max) | Decode p50 | Wall |
|---|---|---|---|---|---|---|---|
| S2 | 1, 4, no cut | 16 of 16 | (6 past 80 s) | 144.5 s (308.2) | 16.1 s (91.4) | 50.8 tok/s | 412 s |
| S2 | 1, 4, cut | 15 of 16 | 4 | 197.3 s (302.0) | 16.4 s (76.0) | 42.0 tok/s | 452 s |
| S2 | 2, 6, cut | 24 of 24 | 3 | 74.7 s (185.4) | 12.6 s (74.7) | 21.7 tok/s | 326 s |
| S2 | 2, 8, cut | 32 of 32 | 6 | 91.5 s (291.3) | 16.9 s (54.3) | 18.5 tok/s | 432 s |
| S3 | 1, 4, cut | 15 of 16 | 5 | 194.6 s (288.2) | 7.9 s (89.6) | 29.3 tok/s | 510 s |
| S3 | 2, 8, cut | 31 of 32 | 5 | 90.0 s (146.5) | 26.2 s (72.8) | 17.4 tok/s | 452 s |

### K2. The caches and the servers

Prompt tokens served from the prefix cache (each answered request's `cached_tokens`):

| Arm, workload, chats | All turns | First turns | Turns 2 to 4 | Requests answered after a cut |
|---|---|---|---|---|
| S2, 1, 4, no cut | 82.3% | 15.3% | 96.7% | (none cut) |
| S2, 1, 4, cut | 90.3% | 67.4% | 95.7% | 67.4% |
| S2, 2, 6, cut | 89.8% | 70.0% | 94.1% | 78.4% |
| S2, 2, 8, cut | 87.4% | 58.9% | 94.1% | 61.6% |
| S3, 1, 4, cut | 90.6% | 65.6% | 96.6% | 72.4% |
| S3, 2, 8, cut | 88.5% | 58.2% | 94.1% | 62.4% |

The server logs (the prefill batch lines): S2's four runs 76, 84, 64 and 82 prefill chunks, 13, 15, 20 and 30 of them
with cached tokens; S3's two runs 56 and 53 (19 and 27). At most 1 request ran at once on workload 1 and 3 on
workload 2; the queue held at most 3 (workload 1) and 4 to 5 (workload 2). The full-token pool peaked at 0.97 to 0.98
(S2) and at 0.99 and 0.93 (S3), the Mamba state pool at 0.58 to 0.83. Neither log has a retract, abort or error line.

Boot and memory (each arm's boot lines): both arms allocate a KV pool of 146,098 tokens (fp8) and 12 Mamba state
slots. S2's target prefill CUDA graphs took 104.3 s and 2.27 GB; S2 served after 210 s at 23,302 MiB, with 1.17 GB of
GPU memory left to SGLang. S3, without those graphs, served after 120 s at 20,936 MiB, with 3.46 GB left. Window 2
sampled no GPU peak under load; window 1's S1 (S2's memory flags) peaked at 23,812 to 23,816 MiB of 24,576, and vLLM
at 24,064 MiB (section J's runs).

### K3. What the numbers show

1. **A retry after the 80 s cut resumes from the chunks the server already computed.** Chat 0's 86,999-token first
   turn was cut once; the retry found 69,632 tokens cached (17 chunks of 4,096) and answered in 28.6 s, 108.7 s in
   all. Chat 2's 77,000 tokens: two cuts, then 61,440 cached and 37.2 s, 197.3 s in all. So a cold long prompt
   through OmniRoute costs time, not the request: Hermes retries 3 times, and `harness-ports/bin/pc-lane.sh` then
   retries the lane after a 60 s backoff (`LANE_CAPACITY_RETRIES=3`, pc-lane.sh:271-291), each attempt starting where
   the last one stopped.
2. **One long first turn of 16 was never answered in its run.** Chat 1 (57,000 tokens) took 4 attempts and 302.0 s;
   chat 3 (67,000) was cut 4 times. At workload 1's sizes one request ran at a time (the server log: max running 1,
   max queue 3), and `lpm` serves cached prefixes first, so a cold attempt can spend much of its 80 s queued
   (INFERRED from those counts; the queue time per attempt was not logged). Chat 3's next turn found 58,928 of 69,517
   tokens cached and answered in 26.4 s: the cut attempts' chunks were kept. In a lane, the lane-level retry
   continues from there.
3. **`lpm` halves the warm waits at 4 long chats; the cold maximum grows.** S2 without cuts against window 1's S1
   (`fcfs`), same workload: warm p50 16.1 s against 32.7 s, warm max 91.4 s against 178.8 s; cold p50 144.5 s against
   144.9 s, cold max 308.2 s against 254.3 s.
4. **Lane-size chats: every request answered at 6 and 8 chats.** 3 and 6 first turns needed one to three retries;
   warm turns p50 12.6 s and 16.9 s. At most 3 requests ran at once (the GPU pool), the rest waited (max queue 4 and 5).
5. **The cache holds at 6 and 8 chats:** 89.8% and 87.4% of all prompt tokens came from the prefix cache (the usage's
   `cached_tokens`), 94.1% of the warm turns'.
6. **No crash, no error, no retract** in S2's log over its four runs (27 minutes of load; the harvest's line parser).
   The window log's case-insensitive counts `retract-lines 1` and `abort-lines 1` match argument names on the log's
   line 7, the startup dump (`retraction_policy`, `abort_on_priority_when_disabled`).
7. **S3's larger prefill chunk traded the warm turns for the cold maximum.** On workload 2 at 8 chats its cold first
   token peaked at 146.5 s against S2's 291.3 s (p50 90.0 s against 91.5 s), while its warm turns waited longer (p50
   26.2 s against 16.9 s; max 72.8 s against 54.3 s, nearer the 80 s cut) and one first turn went unanswered (chat 4,
   52,000 tokens, four cuts; S2 answered all 32). On workload 1 its cold times matched S2's (p50 194.6 s against
   197.3 s) and its decode fell (p50 29.3 against 42.0 tok/s). INFERRED, not measured: each prefill chunk holds the
   running decodes for its duration, and an 8,192-token chunk holds them about twice as long (per-step times were not
   logged).

### K4. The choice for the switch

**S2 ships** (`deploy/qwen.container`): chunk 4,096 with the prefill CUDA graphs, `lpm`, and the cache report. The
rule, set before S3's numbers were read: S3 replaces S2 only if its cold first-token times are better or equal and its
warm and decode times are not much worse. Its cold times were (equal p50, lower maximum); its warm turns at 8 chats
(p50 +55%) and its decode at 4 long chats (p50 -30%) were not, and both differences are larger than the 17% that
separates S2's own two runs of workload 1 (K5). Lanes send most requests as warm turns (each turn after a lane's
first extends a cached prefix; the workloads model it with 2,500-token turns), and a warm turn past 80 s is cut and
sent again. S3's other gains, a boot 90 s shorter and 2.3 GB more GPU memory, match what S2's boot lines put on the
prefill CUDA graphs (104.3 s, 2.27 GB), not the chunk: S2 without those graphs is an arm not yet run (K5).

**Changed after the deploy (K6):** with the prefill CUDA graphs the server ran out of GPU memory on the first Hermes
lane's first long prompt; since 2026-10-02 04:15:19Z the unit runs S2's flags without those graphs.

### K5. Gaps this window leaves (added to section G's list)

- vLLM did not run workload 2: at 6 and 8 lane-size chats there is no vLLM figure beside S2's. Window 1 showed its
  cache gone at 3 and 4 long chats (3.6% and 2.7% of prompt tokens).
- HiCache holds 24 GB of the PC's host memory while the server runs (window 1: KV 15.58 GB and states 8.47 GB).
- The boot time varies: S2 served after 210 s, window 1's S1 after 640 s (the page cache's state is the likely cause;
  not measured).
- A cold attempt can spend its 80 s queued behind warm turns (K3 item 2); `--schedule-policy lpm` with a priority for
  long waits was not run.
- `extra_buffer` with overlap, and more than 8 chats, were not run.
- S2 without the prefill CUDA graphs, at chunk 4,096, was not run: it may keep S2's warm and decode times with S3's
  boot time and memory.
- Each arm ran each workload once. S2's two runs of workload 1 (cut and uncut) differ by 17% in decode p50 (42.0 and
  50.8 tok/s), so a smaller difference between arms is within one rerun's spread.

### K6. The deploy, the out-of-memory stop and the fix (2026-10-02 03:43Z to 04:26Z; written 04:2xZ)

1. **The deploy (S2's flags, 03:43:23Z to 03:48:36Z).** A key check ran on the GPU first, with a fake key built on the
   PC. Passed on SGLang's own command line, the argument dump showed it (`control found=1 key=1 redacted=0`); through
   `deploy/sglang_start.py` the dump showed `<redacted>` and no key (`start found=1 key=0 redacted=1`). The unit then
   served after 212 s at 22,972 MiB; the live log held the real key 0 times (podman logs 289 lines, the journal 393).
   The smoke at 03:50Z went straight to the server: `/v1/models`, a chat, a tool call with `tool_choice: "auto"`, a
   thinking answer, `/v1/completions` with `logprobs: 20`; OmniRoute's probe through the build combo was served by
   `qwen3.8-27b-local`. Every smoke request had a short prompt, and none forced constrained output.
2. **The stop (03:53:56Z to 03:53:58Z).** The first SGL-SMOKE lane (Hermes on the raw local id) sent its first long
   prompt. SGLang logged `Triton kernel 'apply_token_bitmask_inplace_kernel' device-loaded after serving started (free
   device mem: 0.66 GiB)`, the same at 0.09 GiB, then `torch.OutOfMemoryError: CUDA out of memory. Tried to allocate
   48.00 MiB ... of which 35.12 MiB is free`. The container exited 137, systemd restarted it (restart counter 1), and
   the lane's request ended in a 502; the coordinator stopped the lane. That kernel applies the grammar mask of
   constrained output (forced tool calls, JSON schemas). Which field of the lane's request asked for it was not read.
3. **Why the margin was short.** SGLang's `srt/utils/triton_load_watch.py` (in the image) gives the mechanism: Triton
   loads each kernel onto the GPU at its first launch, that load needs free memory outside PyTorch's allocator, and "a
   specialization first used mid-serving ... can die in `cuModuleLoadData` with CUDA OOM, minutes or hours in". The
   image has no switch to pre-load kernels; it warns when a late load starts under 1 GiB free
   (`SGLANG_TRITON_LOAD_WARNING_THRESHOLD_GB`, default 1.0). S2's boot left 1.17 GB free (K2). The KV pool did not run
   out: the failure was outside it.
4. **The direct test (the owner's request: no OmniRoute; 04:04:25Z).** On the restarted server a forced tool call and
   a JSON-schema answer both returned 200; free memory fell from 0.72 to 0.11 GiB as the grammar kernels loaded (23,386
   to 24,008 MiB). These short prompts did not crash it. INFERRED from item 6 (a long cold prefill took 884 MiB more):
   the next long prompt would have.
5. **The fix: S2 without the prefill CUDA graphs** (`--disable-prefill-cuda-graph`, chunk 4,096 kept: the arm K5 names
   as not run). Restart at 04:12:45Z (the old container stopped by SIGKILL, exit 137: SGLang did not stop on SIGTERM
   within podman's 10 s, as at the key check); serving at 04:15:19Z, after 142 s. Boot lines: `Disable prefill CUDA
   graph because cuda_graph_config resolved prefill.backend='disabled'`; the KV pool 146,098 tokens (fp8) as before;
   `available_gpu_mem=3.46 GB`; 20,962 MiB on the GPU; the real key 0 times in 234 journal lines.
   `tests/test_qwen_units.py` pins the flag (negative control: the assertion fails on the unit without it).
6. **The direct tests after the fix (04:16:00Z to 04:19:45Z, no OmniRoute, no cut):**

   | Requests (each forces constrained output) | Prompt tokens | Result | GPU MiB after (peak) |
   |---|---|---|---|
   | (start) | | | 21,226 |
   | a tool call and a JSON schema, short | | 200 in 1.8 s and 0.8 s (the answer, 391, is right) | 21,868 |
   | a tool call, cold | 87,182 | 200 in 106.0 s, one tool call | 22,752 |
   | a tool call and a JSON schema at once, cold | 56,501 and 52,235 | 200 in 114.4 s and 55.3 s (1,333 lines, right) | 22,752 |

   The grammar kernels took 642 MiB at their first use; the first long cold prefill 884 MiB more; the two at once
   none. Restart count 0 throughout; no late-load memory warning.
7. **The Hermes smoke again (SGL-SMOKE2, `tasks/briefs/pc/pc-sgl-smoke2.md`, about 04:21Z to 04:26Z).** The lane met its
   contract: the premise re-run matched, three tool round trips pasted, a file read quoted, "UNEXPECTED: None"; it
   changed no file. The dispatcher's route line: every request served by `qwen-local/qwen3.8-27b-local`, 10 answered
   (200) and 1 closed before an answer (499; its cause was not read). After the lane: restart count 0, 22,756 MiB, no
   late-load memory warning since the redeploy, and 11 slow-compile notes (a kernel compiled after serving started, a
   1 to 4 s stall each).
8. **Left open (added to K5's list):** this arm's speed under the A/B workloads is not measured; S2 and S3 bound it,
   but S3 also doubled the chunk (K3 item 7). Kernels compiled after serving started stall the engine 1 to 4 s each,
   and the Triton cache lives in the container, so every restart compiles them again (a mounted cache is not set up).
   The margin covers the kernels these requests loaded, not every kernel a new request shape may load: the journal's
   `device-loaded after serving started` line (under 1 GiB free) is the warning to watch.
