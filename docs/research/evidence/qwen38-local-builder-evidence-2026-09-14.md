# Evidence pack: replacing the cloud BUILD lane with a local llama.cpp Qwen3.8-27B server

Gathered 2026-09-14 by an evidence-gatherer. **EVIDENCE ONLY — no verdicts, no recommendations,
no ranking of options.** The coordinator concludes.

Assistant knowledge cutoff is May 2026. The model in the brief was released 2026-08-14, i.e.
*after* the cutoff, so every C1/C2 fact below comes from a fetch, never from memory. Rows that
could not be sourced say NOT-FOUND or NOT-FETCHED and are never filled in.

**Reddit is unreachable from this sandbox** (`www.reddit.com` and `old.reddit.com` both refused by
WebFetch; Exa returns SOURCE_NOT_AVAILABLE). Every Reddit claim below is therefore sourced from a
mirror (`bittide.aicompass.dev`, which reproduces thread bodies and links the canonical permalink)
and is marked accordingly. **Upvote and comment counts were not obtainable for any thread** — the
mirror does not carry them. Those cells are NOT-FETCHED, not guesses.

---

## 0. Ground-truth architecture (the basis of all C7/C8 arithmetic)

From the official `config.json`, fetched raw 2026-09-14
(https://huggingface.co/Qwen/Qwen3.8-27B/raw/main/config.json):

```
num_hidden_layers       = 64
layer_types             = 16 x [linear_attention, linear_attention, linear_attention, full_attention]
                          -> 48 Gated-DeltaNet (linear) layers, 16 full-attention layers
full_attention_interval = 4
num_attention_heads     = 24     num_key_value_heads = 4      head_dim = 256
linear_num_key_heads    = 16     linear_key_head_dim   = 128
linear_num_value_heads  = 48     linear_value_head_dim = 128   linear_conv_kernel_dim = 4
hidden_size             = 5120   intermediate_size = 17408     vocab_size = 248320
mtp_num_hidden_layers   = 1      max_position_embeddings = 262144
partial_rotary_factor   = 0.25   rope_theta = 10000000
architectures = ["Qwen3_5ForConditionalGeneration"], model_type = qwen3_5
vision_config present (depth 27, out_hidden_size 5120) -> natively multimodal
tie_word_embeddings = false   (so embed_tokens and lm_head are two separate 1.27 B tensors)
```

The single most load-bearing fact: **only 16 of 64 layers hold a growing KV cache.** The other 48
hold a fixed-size recurrent state that does not grow with context.

---

## 1. Evidence table

| id | verdict | primary source | quote / number (<=25 words) | source date |
|---|---|---|---|---|
| **C1 — the model** |
| C1.1 Does "Qwen3.8-27B" exist | CONFIRMED | https://huggingface.co/Qwen/Qwen3.8-27B | Official Qwen org repo; card: "Qwen3.8-27B brings these advances to a compact, deployment-friendly dense model" | card 2026-08-13 |
| C1.2 Release date | CONFIRMED | https://github.com/QwenLM/Qwen3.8 (README news list) | "2026-08-14: Qwen3.8-27B is now available on Hugging Face Hub and ModelScope" | 2026-08-14 |
| C1.3 Official blog | CONFIRMED (but titled for Max, not 27B) | https://qwen.ai/blog?id=qwen3.8 | "Qwen3.8-Max: A New Bar for Coding and Cowork" — the 27B's own citation block points here | 2026-08-02 |
| C1.4 Dense or MoE | CONFIRMED dense | config.json (no expert keys) + https://www.alibabacloud.com/blog/alibaba-unveils-qwen3-8-27b-and-releases-weights-of-qwen3-8-flagship-model_603463 | "This native multimodal dense model balances high performance with cost-efficiency" | 2026-08-17 |
| C1.5 Parameter count | CONFIRMED ~27B | HF card | "27B"; BF16 checkpoint reported as 55.6 GB across 18 safetensors shards | 2026-08-13 |
| C1.6 Layer count | CONFIRMED 64 | config.json `num_hidden_layers` | `64` | 2026-09-14 fetch |
| C1.7 Attention design — HYBRID, not plain GQA | CONFIRMED | config.json `layer_types`, `full_attention_interval` | 48 linear (Gated DeltaNet) : 16 full attention, 3:1 repeating; `full_attention_interval: 4` | 2026-09-14 fetch |
| C1.8 KV heads / head_dim (full-attn layers) | CONFIRMED | config.json | `num_attention_heads 24`, `num_key_value_heads 4`, `head_dim 256` | 2026-09-14 fetch |
| C1.9 Linear-attn dims | CONFIRMED | config.json | `linear_num_key_heads 16`, `linear_num_value_heads 48`, key/value head_dim 128, conv kernel 4 | 2026-09-14 fetch |
| C1.10 MTP heads present | CONFIRMED | config.json `mtp_num_hidden_layers: 1`; HF card | card: "MTP (Multi-Token Prediction): trained with multiple steps" | 2026-08-13 |
| C1.11 Context length | CONFIRMED | HF card + config.json | "262,144 natively and extensible up to 1,000,000 tokens" (`max_position_embeddings 262144`) | 2026-08-13 |
| C1.12 License | CONFIRMED Apache-2.0 | HF card metadata | `license: apache-2.0` | 2026-08-13 |
| C1.13 Reasoning control: `reasoning_effort` | CONFIRMED | HF card, quoted verbatim by Simon Willison | "xhigh (default) … medium: balancing accuracy and speed … low: efficient reasoning optimizing for speed and cost" | 2026-08-13 / 2026-08-16 |
| C1.14 Levels are low/medium/xhigh — **there is no `high`** | CONFIRMED | https://huggingface.co/Qwen/Qwen3.8-27B/discussions/113 | "Only those three level names work. llama.cpp also accepts minimal, high and max, but this model's template throws an error" | 2026-08-16 |
| C1.15 Other thinking switches | CONFIRMED | HF card / discussions/113 | `enable_thinking` (on by default) and `preserve_thinking` (on by default), passed inside `chat_template_kwargs` | 2026-08-13 |
| C1.16 No `/think` `/no_think` switch for 3.8 | NOT-FOUND | — | no primary source found describing a /think toggle for this model; only the kwargs above | — |
| C1.17 Sibling "Flash-Next" is real | CONFIRMED | https://llm-stats.com/models/compare/qwen3.8-27b-vs-qwen3.8-flash-next ; https://huggingface.co/RadixArk/Qwen3.8-Flash-Next-NVFP4 | Official name `Qwen3.8-Flash-Next`; 125B MoE main model + 51B n-gram table + 4B MTP ≈ 180B, 6B active | 2026-08-14 onward |
| C1.18 Flash-Next licence differs | PARTLY (secondary only) | https://inferya.com/guides/qwen38-27b-vs-flash-next/ | "Flash-Next uses Qwen Community License 1.0" — not verified against the HF card itself | undated page |
| C1.19 Other family members | CONFIRMED | https://github.com/QwenLM/Qwen3.8 | Qwen3.8-2.4T-A95B (2026-08-12), Qwen3.8-27B (2026-08-14); Qwen3.6-27B (2026-04-22) also exists | repo README |
| **C2 — the Unsloth GGUF** |
| C2.1 Repo exists | CONFIRMED | https://huggingface.co/unsloth/Qwen3.8-27B-GGUF | repo present, 37 commits, 472 GB total | — |
| C2.2 UD-IQ4_XS size | CONFIRMED 14.3 GB | https://huggingface.co/unsloth/Qwen3.8-27B-GGUF (file table) | "UD-IQ4_XS: 14.3 GB" (a third-party PPL sweep quotes 14.6 GB; a GPTQ card quotes "14.5 GiB") | file added ~2026-08-19 |
| C2.3 Unsloth recommended sampling (thinking) | CONFIRMED | https://unsloth.ai/docs/models/qwen3.8 | "temperature=1.0, top_p=0.95, top_k=20, min_p=0.0, presence_penalty=0.0, repetition_penalty=1.0" | page updated 2026-09-08 |
| C2.4 Unsloth recommended sampling (non-thinking) | CONFIRMED | same | "temperature=0.7, top_p=0.80, top_k=20, min_p=0.0, presence_penalty=1.5" | 2026-09-08 |
| C2.5 Unsloth's own effort flag syntax | CONFIRMED | same | "`--chat-template-kwargs '{\"reasoning_effort\":\"medium\"}'`" | 2026-09-08 |
| C2.6 What "UD" means | CONFIRMED | https://unsloth.ai/docs/basics/dynamic-3.0-ggufs ; https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/discussions/74 | "Unsloth Dynamic V3.0"; claim ">10% top-1% better accuracy at the same size compared to every other provider" | 2026-08-19 |
| C2.7 **Does UD-IQ4_XS still contain the MTP head?** | CONFIRMED yes | https://unsloth.ai/docs/basics/dynamic-3.0-ggufs | "We also removed the MTP module from smaller quants under `UD-Q2_K_XL` (8.37GB and lower)" — IQ4_XS at 14.3 GB is above that line | 2026-08-19 |
| C2.8 A standalone MTP module also exists | CONFIRMED | https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/tree/main | file `mtp-Qwen3.8-27B-Q4_0.gguf` (renamed from `…-Q4_K.gguf`) | ~2026-09-07 |
| C2.9 Unsloth's own MTP invocation | CONFIRMED | https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/discussions/102 | "Use `--spec-type draft-mtp --spec-draft-n-max 2` in llama.cpp to enable it. It will use more RAM" | undated thread |
| C2.10 Unsloth example llama.cpp command | CONFIRMED (minimal) | https://unsloth.ai/docs/models/qwen3.8 | `llama-cli --model …UD-Q4_K_XL.gguf --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0.0` — no -ngl/-fa/ctx guidance given | 2026-09-08 |
| **C3 — benchmarks vs Claude Opus** |
| C3.1 Official table exists and includes an Opus column | CONFIRMED | https://huggingface.co/Qwen/Qwen3.8-27B/raw/main/README.md | Columns: Qwen3.8-27B, Qwen3.6-27B, Qwen3.7-Plus, Muse Glimmer-30B, **Opus4.6 Max** | 2026-08-13 |
| C3.2 Terminal Bench 2.1 | CONFIRMED — **Opus ahead** | same | Qwen3.8-27B **73.0** vs Opus4.6 Max **78.2** | 2026-08-13 |
| C3.3 SWE-bench Pro | CONFIRMED — **Qwen ahead** | same | Qwen3.8-27B **61.7** vs Opus4.6 Max **53.4** | 2026-08-13 |
| C3.4 NL2Repo-Bench | CONFIRMED — Opus ahead | same | **42.3** vs **47.6** | 2026-08-13 |
| C3.5 QwenSWEBench (vendor's own benchmark) | CONFIRMED — Qwen ahead | same | **79.0** vs **63.8** | 2026-08-13 |
| C3.6 CoWorkBench | CONFIRMED — Qwen ahead | same | **70.7** vs **68.2** | 2026-08-13 |
| C3.7 LiveCodeBench v6 | CONFIRMED — Qwen ahead | same | **90.3** vs **88.8** | 2026-08-13 |
| C3.8 GPQA Diamond / HLE / IFBench | CONFIRMED mixed | same | GPQA 89.2 vs 91.3; HLE 30.8 vs **40.0**; IFBench 79.5 vs 62.5 | 2026-08-13 |
| C3.9 **Methodology asymmetry in that table** | CONFIRMED | same (footnote) | "Except for Opus4.6 Max, which uses the officially reported score, all models are evaluated with the Claude Code harness at temp=1.0…" | 2026-08-13 |
| C3.10 DeepSWE 1.1 / JobBench / Agents' Last Exam have **no** Opus column | CONFIRMED | same | DeepSWE 42.2, JobBench 33.4, ALE 20.4/42.9; Opus cells are `--` | 2026-08-13 |
| C3.11 Opus 4.6 official SWE-bench Verified | PARTLY (secondary) | https://www.anthropic.com/news/claude-opus-4-6 via https://www.vellum.ai/blog/claude-opus-4-6-benchmarks | 80.8% SWE-bench Verified, averaged over 25 trials; Terminal-Bench 2.0 65.4% at max effort | 2026-02 |
| C3.12 **Opus 5 numbers** — Anthropic's own page publishes no raw SWE-bench/Terminal-Bench figure | CONFIRMED (absence on that page) | https://www.anthropic.com/news/claude-opus-5 | Page cites Frontier-Bench v0.1, CursorBench 3.2, ARC-AGI 3, OSWorld 2.0 — "does not contain verbatim numbers for SWE-bench Verified … or Terminal-Bench" | 2026-07-24 |
| C3.13 Opus 5 figures circulating | UNSURE (secondary only) | https://www.morphllm.com/claude-benchmarks ; https://datanorth.ai/news/claude-opus-5-by-anthropic | "96.0% on SWE-bench Verified and 79.2% on SWE-bench Pro"; "89.1% on Terminal-Bench 2.1" — **not confirmed on anthropic.com** | 2026-07/08 |
| C3.14 Qwen3.8-27B vs **Opus 5** on the two directly comparable rows | PARTLY | C3.2/C3.3 vs C3.13 | SWE-bench Pro 61.7 vs 79.2; Terminal-Bench 2.1 73.0 vs 89.1 — Opus 5 ahead on both, but the Opus 5 side is secondary-sourced | — |
| C3.15 **"performs better than Opus for surgical edits"** — Aider polyglot / edit-format evidence | **NOT-FOUND** | https://aider.chat/docs/leaderboards/ searched | No Qwen3.8-27B entry found on the Aider polyglot or code-editing leaderboards; no `percent_cases_well_formed` figure for this model exists in any source found | searched 2026-09-14 |
| C3.16 An independent "no format-error measurement yet" statement | PARTLY (secondary) | https://codersera.com/blog/qwen-3-8-27b-local-claude-code-replacement-2026/ | "There's no independent format-error measurement yet" | 2026-08-18 |
| C3.17 Aider polyglot exists and does measure edit-format compliance | CONFIRMED | https://aider.chat/docs/leaderboards/ | "percent_cases_well_formed" measures responses that correctly followed the specified edit_format | current |
| C3.18 BFCL / tau-bench numbers for this model | **NOT-FOUND** | — | neither benchmark appears in the official card nor in any source found | — |
| C3.19 Independent composite (Artificial Analysis) | PARTLY (secondary) | https://www.yottalabs.ai/post/qwen-3-8-vs-deepseek-v4-flash-2026 | "Flash-Next 56, Qwen3.8-27B 52, DeepSeek V4 Flash 52" on AA Intelligence Index, early September | 2026-09-03 |
| C3.20 Knowledge regression vs 3.6 | PARTLY (secondary) | https://tokenfeed.ai/qwen38-27b-knows-more-code-knows-less-everything-else | "On Artificial Analysis's Omniscience evaluation … Qwen3.8-27B scores noticeably below its predecessor" | 2026-08-20 |
| **C4 — reasoning effort: "medium ≈ 98% of the intelligence at 1/20th the thinking time"** |
| C4.1 Thread `1vtq8hc` itself | **NOT-FETCHED** | https://www.reddit.com/r/LocalLLaMA/comments/1vtq8hc | Reddit refused by WebFetch and Exa; no mirror found that maps to this exact ID. Existence, title, score, comment count all unverified | — |
| C4.2 A near-identical claim does exist in public | CONFIRMED (mirror) | https://bittide.aicompass.dev/article/7e490676-ad80-467b-8e1d-ad6d31a10b89 | Title: "The difference between 'medium' and 'xhigh' reasoning effort for Qwen3.8-27B is actually insane." | undated mirror |
| C4.3 That poster's numbers (RTX 2080 Ti 22 GB, UD-Q4_K_XL) | CONFIRMED (mirror) | same | "medium … barely any thinking at all, a couple thousand tokens max"; xhigh "15k to 20k … pacman … 40 thousand" | undated |
| C4.4 **Measured per-effort quality table** (the strongest counter-evidence) | CONFIRMED | https://kodesage.ai/blog/qwen-3-8-27b-llm-model-review | Substance: low 7.79, **medium 8.18**, **xhigh 8.61**; median latency 95 s / 75.5 s / 143.1 s | 2026-08-19 |
| C4.5 → the "98%" figure | REFUTED as stated | derived from C4.4 | 8.18 / 8.61 = **95.0%**, not 98%; and that source ran each config **once**, with noise estimated at 0.18 substance | 2026-08-19 |
| C4.6 → the "1/20th thinking time" figure | REFUTED as stated | C4.4 | medium 75.5 s vs xhigh 143.1 s median = **1/1.9**, not 1/20 | 2026-08-19 |
| C4.7 Best-case ratio found anywhere (thinking tokens, same machine) | CONFIRMED | https://rizz.dev/feed/qwen-38-overthinks-default-reasoning-setting (Danmoreng, RTX 5080 laptop, IQ3_XXS, 3 seeds) | low 4,418 / medium 5,918 / xhigh 39,398 reasoning tokens → medium is **1/6.7** of xhigh | 2026-08-21 |
| C4.8 Same source, wall clock | CONFIRMED | same | "Low … 111.6 seconds. Medium used 5,918 and 127.4 seconds. X-high used 39,398 and 717.8 seconds" → **1/5.6** | 2026-08-21 |
| C4.9 Largest controlled sweep found (on RTX 3090s) | PARTLY (relayed through a mirror, original on X) | https://bittide.aicompass.dev/article/80df6b48-f75c-4b9d-86c9-0b6b9a39d72a | "@superalesha … 67-hour benchmark … all on RTX 3090s … xhigh burned **7–11× more tokens than low for 0–4.7 points**" | mirror undated |
| C4.10 Same sweep, the surprising row | PARTLY (same) | same | "GGUF Q4_K_M at low effort scored the same 89.3% as xhigh — on 86k reasoning tokens instead of 651k" | — |
| C4.11 **Counter-evidence that higher effort wins on coding** | CONFIRMED | C4.4 + https://news.ycombinator.com/item?id=49324985 | xhigh 8.61 > medium 8.18 on substance; HN: "on the Medium setting it can get stuck in loops like 3.6 does" | 2026-08-16/19 |
| C4.12 Vendor's own warning against lowering effort for agents | CONFIRMED | https://huggingface.co/Qwen/Qwen3.8-27B/raw/main/README.md | card notes lower effort "doesn't necessarily reduce completion time" in multi-turn tasks due to insufficient analysis | 2026-08-13 |
| C4.13 Why effort and latency decouple in agent loops | CONFIRMED | https://kodesage.ai/blog/qwen-3-8-27b-llm-model-review | "low is both slower and worse than medium, because thinking less at each step costs extra agentic rounds" | 2026-08-19 |
| C4.14 Per-request effort (HTTP body) | CONFIRMED | https://huggingface.co/Qwen/Qwen3.8-27B/discussions/113 | `{"chat_template_kwargs": {"reasoning_effort": "medium"}}` | 2026-08-16 |
| C4.15 Server-wide via a dedicated flag | CONFIRMED | llama.cpp `tools/server/README.md` | `--reasoning-effort`: "reasoning effort level given to the chat template: 'default' … 'minimal', 'low', 'medium', 'high', 'xhigh' or 'max'" | master, 2026-09-14 |
| C4.16 Server-wide via template kwargs | CONFIRMED | same README | `--chat-template-kwargs STRING`: "sets additional params for the json template parser, must be a valid json object string" | master |
| C4.17 `--reasoning-budget` also exists | CONFIRMED | same README | "token budget for thinking: -1 for unrestricted, 0 for immediate end, N>0 for token budget" | master |
| C4.18 `--jinja` needed for any of it | CONFIRMED | discussions/113 + llama.cpp README | "You need llama-server with `--jinja` for it"; README: `--jinja, --no-jinja` "(default: enabled)" on master | 2026-08-16 / master |
| C4.19 A reported failure of `--chat-template-kwargs` | CONFIRMED exists (cause unresolved) | https://github.com/ggml-org/llama.cpp/issues/20409 | "Qwen3.5 enable_thinking=false via --chat-template-kwargs is ignored across all shells" — **closed as not planned**, no fix given | 2026-03-11 |
| **C5 — the Reddit quirks** |
| C5a.1 Thread `1vvsokm` exists and is correctly cited | CONFIRMED (mirror) | https://bittide.aicompass.dev/article/6fc2278a-4aed-4c75-b257-39a4c5468e7b → permalink https://www.reddit.com/r/LocalLLaMA/comments/1vvsokm/tested_in_coding_q8_k_xl_qwen38_27b_vs_bf16/ | Title: "Tested in Coding: Q8_K_XL Qwen3.8 27B vs BF16 Qwen3.6 27B" | mirror stamps 2026-08-23 |
| C5a.2 It does say the git thing | CONFIRMED | same | "Both models are very keen to execute write Git commands - despite instructions to the contrary - which then causes major verification issues" | 2026-08-23 |
| C5a.3 **But it is not specific to 3.8** | CONFIRMED | same | "Both models" = Qwen3.6 **and** 3.8; author's net line: "neither should be granted extended Git access" | 2026-08-23 |
| C5a.4 That poster's overall verdict is positive | CONFIRMED | same | "Qwen3.8 is meaningfully and significantly more capable and more trustworthy than Qwen3.6 on every axis except one" | 2026-08-23 |
| C5a.5 Score / comment count | **NOT-FETCHED** | — | mirror carries neither; Reddit unreachable | — |
| C5a.6 An independent instruction-following failure report | CONFIRMED | https://github.com/QwenLM/Qwen3/discussions/1898 | Model "intermittently executes an unrelated Codex skill after completing a coding task"; author notes it was not reproducible | 2026-08-18 |
| C5b.1 Thread `1w8h0cb` ("claims to be Claude") | **NOT-FOUND** | https://www.reddit.com/r/LocalLLaMA/comments/1w8h0cb | Reddit unreachable; no mirror, cache or secondary article found that references this ID or a Qwen3.8-identifies-as-Claude claim | searched 2026-09-14 |
| C5b.2 A **different, well-documented** identity story exists — in the opposite direction | CONFIRMED | https://blog.kilo.ai/p/did-claude-opus-48-distill-alibabas | Claude Opus 4.8 sometimes answered "Qwen" to a Chinese identity prompt (May 2026). Not Qwen claiming to be Claude | 2026-06-03 |
| C5b.3 General caution on self-identification | CONFIRMED | same | "A model saying 'I am Qwen' does not mean it is Qwen. It means it generated the sentence" | 2026-06-03 |
| C5b.4 A plausible mechanism for a *Qwen*→Claude confusion exists in this ecosystem | PARTLY | https://huggingface.co/Qwen/Qwen3.8-27B/discussions/68 | Community ships a "claude code fixed template" for this model — a Claude-Code-shaped system prompt is commonly in context | 2026-08-15 |
| C5c.1 Threads `1w1e1uq`, `1w7tndw`, `1w2e40k` | **NOT-FETCHED** | those three reddit.com URLs | Reddit unreachable; no mirror matched these IDs. Titles, dates, scores, comment counts all unverified | — |
| C5c.2 A 27B-vs-Flash-Next community comparison does exist | CONFIRMED (mirror) | https://bittide.aicompass.dev/article/c5cc4618-3913-44e4-a414-951edff5fb59 | "Can someone please tell me if it's worth running Qwen 3.8 Flash Next on 4x3090 yet over 27B? 27B is good but damn it is indecisive" | undated mirror |
| C5c.3 The "Flash-Next weaker on deep code" claim, community side | PARTLY (secondary) | https://www.mindstudio.ai/blog/qwen-3-8-27b-vs-flash-next-local-agents | "Qwen 3.8 27B at FP16 handled a two day agentic coding session that Qwen 3.8 Flash Next at INT4 could not finish" — quad-3090, one user | 2026-09-06 |
| C5c.4 **The vendor table says the opposite** | CONFIRMED | official card, relayed by https://ai.rs/ai-developer/qwen3-8-flash-next-vs-deepseek-v4-flash-vs-qwen3-8-27b and https://llm-stats.com/models/compare/qwen3.8-27b-vs-qwen3.8-flash-next | Flash-Next leads on **all 11** shared language benchmarks: SWE-bench Pro 62.5 v 61.7, DeepSWE 58.7 v 42.2, JobBench 55.7 v 33.4 | 2026-08-14 |
| C5c.5 A separate benchmark run favouring Flash-Next locally | PARTLY (mirror) | https://bittide.aicompass.dev/article/57d1a74d-a925-4474-811d-4633b968c100 | "almost highest score of all local model I tested, the most efficient … all in medium reasoning. (xhigh is not useful…)" | undated |
| C5c.6 Flash-Next is not a single-3090 option | CONFIRMED | https://inferya.com/guides/qwen38-27b-vs-flash-next/ ; myclaw.ai comparison | 125B main + 51B n-gram + 4B MTP ≈ 180B; "FP8 checkpoint 172.78 GiB"; a 4-bit quant ≈ 111 GB | 2026-08/09 |
| C5c.7 llama.cpp support for Flash-Next | PARTLY (secondary) | https://mindpattern.ai/f/22364 | "llama.cpp Support Is Still an Unmerged PR"; one compiler reports "MTP not working and KV cache scaling oddities" | 2026-08-27 |
| **C6 — every flag in the proposed command** |
| C6.1 `--ctx-size 262144` | CONFIRMED flag; value is the model's native max | llama.cpp server README | "-c, --ctx-size N … (default: 0, 0 = loaded from model)" | master |
| C6.2 `--ngl 54` | CONFIRMED flag | same | "-ngl, --gpu-layers, --n-gpu-layers N … either an exact number, 'auto', or 'all' (default: auto)" | master |
| C6.3 `--ngl 54` of **how many** | CONFIRMED denominator = 64 (+1 MTP layer) | config.json | 54/64 ⇒ 10 repeating layers on CPU; note `mtp_num_hidden_layers: 1` may make llama.cpp report 65 | 2026-09-14 |
| C6.4 Which specific layers go to CPU | **UNSURE** | — | llama.cpp's layer-assignment order not read this session. Matters: of the last 10 layers, indices 55/59/63 are full-attention, so 3 of the 16 KV-bearing layers could land host-side | — |
| C6.5 `--cache-type-k q4_0` | CONFIRMED | server README | "-ctk, --cache-type-k TYPE … allowed: f32, f16, bf16, q8_0, q4_0, q4_1, iq4_nl, q5_0, q5_1 (default: f16)" | master |
| C6.6 `--cache-type-v q4_0` | CONFIRMED | same | "-ctv, --cache-type-v TYPE" — same allowed set, default f16 | master |
| C6.7 **Does quantized V still require flash attention?** | PARTLY — no hard requirement in the README, but a real CUDA kernel-coverage trap exists | https://github.com/ggml-org/llama.cpp/issues/28455 | "quantized KV cache (q5_x, q4_x) with -fa on silently fallback CPU attn … The user gets no error and no warning; performance collapses" | 2026-09-05, closed by PR #28456 |
| C6.8 **q4_0/q4_0 specifically IS in the default CUDA build** | CONFIRMED | https://raw.githubusercontent.com/ggml-org/llama.cpp/master/docs/build.md | default compiles FA kernels for "q4_0-q4_0;q8_0-q8_0;f16-f16;bf16-bf16"; others "fall back to f16-f16 kernel with a warning" | master |
| C6.9 Measured cost of landing outside that set | CONFIRMED | issue #28455 | "Same q5_1/q5_1 benchmark after rebuild: 1509.70 t/s" vs 197.15 t/s default; "a 3 s TTFT turned into a ~95 s TTFT" | 2026-09-05 |
| C6.10 `--flash-attn` — **current spelling takes a value** | CONFIRMED | server README | "-fa, --flash-attn [on\|off\|auto] … (default: 'auto')" | master |
| C6.11 Does bare `--flash-attn` still parse | **UNSURE** | — | the argument is shown as optional (`[on\|off\|auto]`); whether a bare form is accepted was not verified against `arg.cpp` | — |
| C6.12 `--threads 12` | CONFIRMED flag | server README | "-t, --threads N … (default: -1)" | master |
| C6.13 `--threads 12` vs a 6-core/12-thread CPU | **UNSURE — no primary llama.cpp guidance found** | — | no repo statement found this session on physical-core vs SMT thread counts; a measurement item, not a documented fact | — |
| C6.14 `--spec-type draft-MTP` — **the type exists, the spelling does not** | REFUTED as written | server README + https://raw.githubusercontent.com/ggml-org/llama.cpp/master/docs/speculative.md | Accepted list is lower-case: "none,draft-simple,draft-eagle3,**draft-mtp**,draft-dflash,draft-dspark,ngram-simple,…" | master |
| C6.15 `--spec-draft-max 2` — **flag does not exist** | REFUTED | server README | The real flag is "**--spec-draft-n-max N** … number of tokens to draft for speculative decoding (default: 3)" | master |
| C6.16 Other real speculative flags | CONFIRMED | same | `--model-draft`/`-md`; `--spec-draft-n-min`; `--draft-p-min` (alias `--spec-draft-p-min`); `--spec-draft-ngl` | master |
| C6.17 ngram variants exist and are separately selectable | CONFIRMED | docs/speculative.md | `ngram-simple`, `ngram-map-k`, `ngram-map-k4v`, `ngram-mod`, `ngram-cache`; can be combined comma-separated | master |
| C6.18 `--chat-template-kwargs` exists | CONFIRMED | server README | "sets additional params for the json template parser, must be a valid json object string" | master |
| C6.19 **Since which version** | **NOT-FOUND** | — | the introducing PR was not located this session; the flag is present on master and in a 2026-08-15 user command on the Qwen card discussion | — |
| C6.20 `-np` / `--parallel` | CONFIRMED | server README | "-np, --parallel N … number of server slots (default: -1, -1 = auto)" | master |
| C6.21 `--cache-reuse` | CONFIRMED | same | "min chunk size to attempt reusing from the cache via KV shifting, requires prompt caching to be enabled (default: 0)" | master |
| C6.22 Prompt caching default | CONFIRMED | same | "--cache-prompt, --no-cache-prompt whether to enable prompt caching (default: enabled)" | master |
| C6.23 **Does llama.cpp support MTP speculative decoding for THIS model?** | CONFIRMED for the family; 3.8-specific evidence is from the quant publisher, not the llama.cpp repo | https://github.com/ggml-org/llama.cpp/pull/22673 ; https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/discussions/102 | PR "llama + spec: MTP Support" by am17an, **merged 2026-05-16**, implemented for Qwen 3.6 (27B and 35B-A3B); Unsloth instructs `--spec-type draft-mtp` for 3.8 | 2026-05-16 / undated |
| C6.24 MTP weights ship inside the same GGUF | CONFIRMED | PR #22673 | "MTP weights are embedded in the same GGUF file; no separate distribution needed" (Unsloth additionally ships a standalone module) | 2026-05-16 |
| C6.25 A known MTP cost | CONFIRMED | PR #22673 | "Prompt processing speed typically takes a negative hit" when MTP is enabled | 2026-05-16 |
| C6.26 A known MTP regression elsewhere | CONFIRMED exists | https://github.com/ggml-org/llama.cpp/issues/23752 | "MTP speculative decoding degrades throughput on Metal (Apple Silicon) — net loss at every configuration" (not CUDA) | — |
| **C7 — VRAM / KV arithmetic** (worked out in §2) |
| C7.1 KV bytes/token f16 | CONFIRMED by arithmetic + measurement | config.json; cross-check below | **65,536 B/token (64 KiB)** | — |
| C7.2 KV bytes/token q8_0 | CONFIRMED | same | **34,816 B/token (34 KiB)** | — |
| C7.3 KV bytes/token q4_0 | CONFIRMED | same | **18,432 B/token (18 KiB)** | — |
| C7.4 Independent measured cross-check on a 24 GB card | CONFIRMED | https://bittide.aicompass.dev/article/80df6b48-f75c-4b9d-86c9-0b6b9a39d72a (@analogalok RTX 4090 matrix) | "FP16 KV tops out at 100k ctx (40.9 t/s); q8 KV reaches 170k; q4_0 KV fits the full 262k native context in 24GB at 40.7 t/s" | mirror undated |
| C7.5 → my formula predicts those three ceilings | CONFIRMED | §2 arithmetic | predicts ~150k f16 / ~282k q8_0 / ~532k q4_0 with the *smaller* IQ4_XS weights; same ordering and magnitude | — |
| C7.6 **Is 262,144 on-GPU feasible?** | CONFIRMED feasible at q4_0 KV with IQ4_XS weights | §2 | total ≈ **17.97 GiB of 24.00 GiB**, leaving ≈ 6.0 GiB — and `--ngl 54` is not required by the memory arithmetic | — |
| C7.7 Linear-attention state sizing | PARTLY — formula from config dims, llama.cpp's own allocator not read | config.json | ≈ **144 MiB/slot fp32** recurrent + ≈ 6 MB conv; independent report says vLLM's default fp32 state is halvable with bf16 | — |
| C7.8 An independent per-token KV figure for this model | CONFIRMED — matches | https://www.contextstudios.ai/blog/qwen-3-8-27b-hardware-guide | "~64 KB/token BF16 per sequence in the 16 full-attention layers (FP8: half)" | 2026-08-19 |
| **C8 / C14 — bandwidth** (worked out in §3) |
| C8.1 RTX 3090 bus + memory | CONFIRMED | https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3090-3090ti/ | "24 GB GDDR6X", "384-bit" (NVIDIA's page does not print a GB/s figure) | current |
| C8.2 RTX 3090 bandwidth | PARTLY (computed + secondary) | computed 384/8 × 19.5 Gbps; secondary: thefpsreview / gpuzoo | **936 GB/s** (commonly quoted 936.2) | — |
| C8.3 DDR4-3200 dual channel theoretical | CONFIRMED by arithmetic | JEDEC arithmetic: 2 ch × 8 B × 3200 MT/s | **51.2 GB/s** | — |
| C8.4 DDR4 effective (measured) on this box | **NOT-FOUND — measurement item** | — | no measured STREAM figure for the owner's 5600X obtained; theoretical only | — |
| C8.5 DDR5-5600 dual channel (for contrast only) | CONFIRMED by arithmetic | 2 × 8 × 5600 | **89.6 GB/s** — **not applicable**: AM4/5600X is DDR4-only (C14) | — |
| C8.6 Theoretical decode for 14.3 GB fully on a 3090 | computed | §3 | **65.5 tok/s** weights-only ceiling; ~49 tok/s once a full 262k q4_0 KV is also read each token | — |
| C8.7 Measured community decode, 27B ~4-bit on a 3090 | CONFIRMED | https://www.contextstudios.ai/blog/qwen-3-8-27b-hardware-guide | RTX 3090 "Baseline decode **40 t/s**"; tuned vLLM stack "~114 t/s single · ~1,000 t/s @64" | 2026-08-19 |
| C8.8 Measured, the exact quant in the brief (different card) | CONFIRMED | bittide 80df6b48 perf matrix | "RTX 5060 Ti 16GB · UD-IQ4_XS + MTP-1, Q4_0 KV · 64k · **45.6 t/s**" | mirror undated |
| C8.9 Cost of offloading 10 of 64 layers to DDR4 | computed, **not measured** | §3 | ceiling drops 65.5 → **~17.7 tok/s** (~3.7×) on theoretical DDR4-3200; ~14.8 t/s at 80% efficiency | — |
| C8.10 `--no-kv-offload` semantics | CONFIRMED | server README | "-kvo, --kv-offload … whether to enable KV cache offloading (default: enabled)"; `--no-kv-offload` disables (KV to host) | master |
| C8.11 **"2-5 t/s with a 200k host-side KV" — is it measured?** | **NOT-FOUND / unsourced** | — | no measured figure for this model with host-side KV found anywhere. Arithmetic bracket in §3 spans **3.3–13.9 t/s** depending on whether RAM or PCIe binds | — |
| **C9 — speculative/MTP speedups on a 3090 or similar** |
| C9.1 MTP on an RTX 3090, previous generation, llama.cpp | CONFIRMED | https://github.com/ggml-org/llama.cpp/pull/22673 | "RTX 3090 · Qwen3.6-27B Q6_K · ~1.85x · 22.97→42.45 tok/s with MTP" | 2026-05-16 |
| C9.2 Other cards in the same PR | CONFIRMED | same | 3× RTX 3060 Qwen3.6-27B Q4_K_M 18.51→32.24 (1.74×); RTX 3060 laptop 22.92→29.39 (1.28×) | 2026-05-16 |
| C9.3 MTP on Qwen3.8-27B, RTX 3090, **vLLM** (not llama.cpp) | CONFIRMED | https://github.com/syv-ai/qwen38-27b-rtx3090 | "no speculation 46 / 46 tok/s" → MTP fast variant "**~114 / 118-124**" single-stream, 250 W power limit | 2026-09-11 |
| C9.4 Draft-depth tuning, same repo | CONFIRMED | same | k=4 is "the knee"; "Going deeper (k=5) loses again: 106 / 105" | 2026-09-11 |
| C9.5 Optimal `num_speculative_tokens` on a different stack | CONFIRMED | https://huggingface.co/pearsonkyle/Qwen3.8-27B-GPTQ-W4A16 | "Best setting: num_speculative_tokens: 2 — 1.71× decode at 71.2% acceptance. Qwen3.8 has one nextn layer" | undated |
| C9.6 → so the brief's draft depth of 2 is a defensible choice | CONFIRMED (for vLLM/MTP) | C9.5 + C2.9 | Unsloth also instructs `--spec-draft-n-max 2`; one community llama.cpp user runs 4 | — |
| C9.7 llama.cpp MTP speedup measured on a 3090 **for Qwen3.8 specifically** | **NOT-FOUND** | — | every 3090 MTP number found is either Qwen3.6 (llama.cpp) or Qwen3.8 (vLLM). A measurement item | — |
| C9.8 MTP is a single-stream optimisation | CONFIRMED | https://huggingface.co/Twu31/Qwen3.8-27B-AWQ-INT4-MTP-LowLatency | "MTP roughly doubles per-turn latency at 5 concurrent streams; … turn it off for multi-user endpoints" | undated |
| **C10 — multi-session serving** |
| C10.1 How `-np` divides context | PARTLY | https://github.com/ggml-org/llama.cpp/issues/11681 ; PR #24124 | Historically `--ctx-size M` with `--parallel N` gives **M/N per slot**; unified KV changed this — `--kv-unified-per-slot` now sets "context limit per parallel slot" | PR #24124 |
| C10.2 `--parallel` default is not 1 in practice | CONFIRMED exists | https://github.com/ggml-org/llama.cpp/issues/17989 | "'--parallel 1' initializes 4 slots, while docs say default is 1" | — |
| C10.3 → the brief omits `-np` entirely | CONFIRMED (absence) | the brief | with `-np` unset (`-1 = auto`) the 262,144 budget may be split across auto-chosen slots | — |
| C10.4 Practical concurrent 100k agent sessions on 24 GB, llama.cpp | **NOT-FOUND** | — | no source measured N × 100k-token llama.cpp slots for this model on one 24 GB card. Arithmetic in §2 gives the KV budget; a measurement item | — |
| C10.5 vLLM on ONE 3090, measured | CONFIRMED | https://huggingface.co/biMEMO/Qwen3.8-27B-int4-AutoRound | "1 GPU … weights alone take about 18GB, leaving enough headroom for a 32K-token context window"; 1×3090 aggregate 223.6 tok/s at 4 concurrent | undated |
| C10.6 vLLM on one 3090, the tuned repo | CONFIRMED | https://github.com/syv-ai/qwen38-27b-rtx3090 | "~1,000 tok/s at 64 concurrent"; concurrency ladder at 4k prompts: 1/2/4/8 streams → 126/103/46/23 per-stream tok/s | 2026-09-11 |
| C10.7 That repo's slot-count caveat | CONFIRMED | same | "A resident request reserves 1+k = 8 recurrent-state slots — 15.8% of the 69,758-token CTX=fast pool"; "Seven fit with 128-token prompts, five with 4k-token ones and **two with 16k ones**" | 2026-09-11 |
| C10.8 More slots can be *worse* | CONFIRMED | same | forcing 8 seats on `CTX=huge` gave "10 preemptions … aggregate down to 10.3 from 13.0"; 2 seats gave "0 preemptions and 14.4 tok/s" | 2026-09-11 |
| C10.9 Ampere and FP8 | PARTLY | https://huggingface.co/avyukth/Qwen3.8-27B-AWQ-INT4 | "Symmetric W4A16, chosen for **Marlin support on Ampere**"; the 3090 stacks above use int8/int4, and one uses `--kv-cache-dtype fp8_e4m3` (emulated on sm_86) | undated |
| C10.10 FP8 KV is low-value on this architecture | CONFIRMED | https://huggingface.co/Twu31/Qwen3.8-27B-AWQ-INT4-MTP-LowLatency | "FP8 KV cache is not worth it here (only 16 of 64 layers keep KV)" | undated |
| C10.11 A known vLLM/hybrid-GDN prefix-cache trap | CONFIRMED | same | vLLM "forces the attention block size to ceil(GDN state bytes / KV bytes per token) — 784 tokens with the default fp32 state"; `--mamba-ssm-cache-dtype bfloat16` → 400-token blocks, hit rate 51%→79% | undated |
| C10.12 An SGLang trap on this model | CONFIRMED | https://www.contextstudios.ai/blog/qwen-3-8-27b-hardware-guide | "`--mamba-full-memory-ratio` (default 0.9) over-provisions the KV pool and silently caps concurrency" | 2026-08-19 |
| C10.13 AWQ quality caveat on this architecture | CONFIRMED | https://huggingface.co/avyukth/Qwen3.8-27B-AWQ-INT4 | "48 of 64 layers received INT4 without activation-aware scaling" because `Qwen3_5GatedDeltaNet.forward` has signature `(self, *args, **kwargs)` | undated |
| C10.14 **Ollama cannot set this model's reasoning effort** | CONFIRMED | https://huggingface.co/Qwen/Qwen3.8-27B/discussions/113 | "Ollama replaces the model's own template with a generic one, and the reasoning-effort setting lives in the template it throws away" | 2026-08-16 |
| C10.15 Ollama's effort vocabulary mismatches this model | CONFIRMED | https://www.ssdnodes.com/learn/reasoning-effort-settings-local-llm | "Ollama's vocabulary for reasoning levels is low, medium, high and max, while model templates like Qwen3.8's may define … low, medium and xhigh" | — |
| C10.16 Ollama KV quant / parallelism env vars | CONFIRMED | https://pkg.go.dev/github.com/ollama/ollama/envconfig | `OLLAMA_KV_CACHE_TYPE` (q8_0 halves, q4_0 quarters KV); `OLLAMA_NUM_PARALLEL` default 0 = auto-select 4 or 1 | current |
| **C11 — bind address and auth** |
| C11.1 Default bind | CONFIRMED — **127.0.0.1**, not 0.0.0.0 | llama.cpp server README | "--host HOST ip address to listen … (default: 127.0.0.1)"; server "listens on `127.0.0.1:8080`" | master |
| C11.2 Default port is **8080**, not 8000 | CONFIRMED | same | "--port PORT port to listen (default: 8080)" — the brief's "port 8000" matches vLLM/SGLang's default, not llama-server's | master |
| C11.3 `--api-key` exists | CONFIRMED | same | "API key to use for authentication, multiple keys can be provided as a comma-separated list (default: none)" | master |
| C11.4 UNIX socket bind is possible | CONFIRMED | same | "or bind to an UNIX socket if the address ends with .sock" | master |
| C11.5 The Cloudflare-tunnel step | out of scope by instruction | — | recorded as stated in the brief; a localhost bind + local gateway registration needs no tunnel. **No gateway config designed here** | — |
| **C13 — llama.cpp Linux binaries and containers (coordinator's addition)** |
| C13.1 **Linux releases ship NO CUDA build** | CONFIRMED | https://github.com/ggml-org/llama.cpp/releases (b10955) | Ubuntu assets: `x64`, `arm64`, `s390x`, `vulkan-x64`, `vulkan-arm64`, `rocm-10.0-x64`, `openvino-…`, `sycl-fp32/fp16`. "does **not** include dedicated CUDA-specific Linux binaries" | b10955, 14 Sep |
| C13.2 CUDA is Windows-only in releases | CONFIRMED | same | "Windows builds feature CUDA 12 and CUDA 13 variants, but Ubuntu assets focus on CPU, Vulkan, ROCm, OpenVINO, and SYCL" | b10955 |
| C13.3 Same true for the owner's b8184 | CONFIRMED | https://github.com/ggml-org/llama.cpp/releases/tag/b8184 | assets `ubuntu-x64`, `ubuntu-vulkan-x64`, `ubuntu-rocm-7.2-x64`, `ubuntu-s390x`. "No … CUDA-specific Linux/Ubuntu asset" | tag page: 01 Mar |
| C13.4 Same true for b8631 | CONFIRMED | https://github.com/ggml-org/llama.cpp/releases/tag/b8631 | `ubuntu-x64`, `ubuntu-arm64`, `ubuntu-s390x`, `vulkan-x64/arm64`, `rocm-7.2-x64`, `openvino-2026.0-x64`. No CUDA Linux asset | tag page: 02 Apr |
| C13.5 **Both local tarballs predate the model** | CONFIRMED by ordering | b8184 (01 Mar), b8631 (02 Apr), b10955 (14 Sep 2026, current); model released 2026-08-14 | b8631 < b10955, and b10955 is today's build, so b8631 is ≤ 02 Apr 2026 — months before the `qwen3_5` arch existed in llama.cpp | — |
| C13.6 …and predate MTP support | CONFIRMED by ordering | PR #22673 merged 2026-05-16 | both b8184 (Mar) and b8631 (Apr) precede the merge, so neither can have `--spec-type` | — |
| C13.7 The release-page year for b8184/b8631 | **UNSURE** | — | GitHub omits the year for current-year releases; WebFetch rendered b8631 as "2024", which conflicts with the build ordering. Ordering is certain, the printed year is not | — |
| C13.8 Official container images | CONFIRMED | https://raw.githubusercontent.com/ggml-org/llama.cpp/master/docs/docker.md | Registry `ghcr.io/ggml-org/llama.cpp`; tags include **`server-cuda`** (CUDA 12) and **`server-cuda13`** | master |
| C13.9 Host-side requirement | CONFIRMED | same | "Assuming one has the nvidia-container-toolkit properly installed on Linux … cuBLAS should be accessible inside the container" | master |
| C13.10 Podman/CDI instructions | **NOT-FOUND in llama.cpp docs** | same | "No podman-specific instructions are provided in the documentation." The `nvidia-ctk cdi generate` step is an NVIDIA-toolkit procedure, not documented by llama.cpp | master |
| C13.11 Building CUDA from source needs the toolkit | CONFIRMED | https://raw.githubusercontent.com/ggml-org/llama.cpp/master/docs/build.md | "Make sure to have the CUDA toolkit installed"; docs give no nvcc-free path | master |
| **C14 — DDR4 on AM4** |
| C14.1 The 5600X platform is DDR4-only | taken from the coordinator's measured FACT 2, not re-verified here | — | AM4 socket; DDR5 figures are therefore inapplicable to the offload arithmetic | 2026-09-14 (coordinator) |
| C14.2 Figure used in §3 | CONFIRMED by arithmetic | 2 ch × 8 B × 3200 MT/s | **51.2 GB/s** theoretical; effective unmeasured (C8.4) | — |
| **C15 — the `llama.cpp-mtp` checkout** |
| C15.1 The upstream MTP work is **merged**, not a fork | CONFIRMED | https://github.com/ggml-org/llama.cpp/pull/22673 | "llama + spec: MTP Support" by am17an — **Merged 2026-05-16** | 2026-05-16 |
| C15.2 Follow-on model coverage | CONFIRMED | same | "GLM-5.2 (GLM_DSA) … added in subsequent PRs"; "Gemma 4 models … follow-up work" | 2026-05-16 |
| C15.3 Measured speedup on a 3090 | CONFIRMED | same | "RTX 3090 · Qwen3.6-27B Q6_K · ~1.85x · 22.97→42.45 tok/s" | 2026-05-16 |
| C15.4 A second MTP-related PR referenced by the quant publisher | CONFIRMED exists | https://github.com/ggml-org/llama.cpp/pull/26296 (cited by Unsloth discussions/102) | referenced as the MTP reference alongside https://unsloth.ai/docs/models/mtp; **contents NOT-FETCHED** | — |
| C15.5 Which fork the owner's `llama.cpp-mtp` directory is | **UNSURE — not determinable remotely** | — | could be a pre-merge checkout of #22673, a Qwen-specific branch, or a personal clone. Needs a local `git log`/`git remote` read | — |
| C15.6 A known community llama.cpp branch in this space | CONFIRMED exists | https://github.com/alainnothere/llama.cpp/tree/disk-cache-eviction | adds per-message reasoning-effort switching, template KV-cache patch, conversation-to-disk; **not upstream** | 2026-08 (HN) |
| C15.7 A third-party PR referenced for big speedups | PARTLY (mirror) | bittide 80df6b48 | "RTX PRO 6000 96GB · llama.cpp **PR #27342** DFlash2, Q4_K_M · 262k · 153.9 t/s = 2.26× plain"; merge status NOT-FETCHED | mirror undated |

---

## 2. C7 — the KV-cache and VRAM arithmetic, written out

**Step 1 — bytes per token of KV cache.** Only the 16 `full_attention` layers cache K and V. The
48 `linear_attention` (Gated DeltaNet) layers have no growing cache at all; they carry a fixed
recurrent state, sized separately in step 4.

```
elements/token = 2 (K and V) x n_layer_with_kv x n_kv_heads x head_dim
               = 2 x 16 x 4 x 256
               = 32,768 elements per token
```

GGUF block sizes (32 weights per block):
* `f16`  = 2 bytes/element
* `q8_0` = 32 int8 + one f16 scale = 34 bytes / 32 elements = 1.0625 bytes/element
* `q4_0` = 16 packed bytes + one f16 scale = 18 bytes / 32 elements = 0.5625 bytes/element

```
f16  : 32,768 x 2.0000 =  65,536 B/token =  64 KiB/token
q8_0 : 32,768 x 1.0625 =  34,816 B/token =  34 KiB/token
q4_0 : 32,768 x 0.5625 =  18,432 B/token =  18 KiB/token
```

The 64 KiB/token f16 figure is independently confirmed by an outside write-up of this model:
"~64 KB/token BF16 per sequence in the 16 full-attention layers" (contextstudios.ai, 2026-08-19).

**Step 2 — KV cache at the brief's full 262,144 tokens.**

```
f16  : 262,144 x 65,536 = 17,179,869,184 B = 16.000 GiB
q8_0 : 262,144 x 34,816 =  9,126,805,504 B =  8.500 GiB
q4_0 : 262,144 x 18,432 =  4,831,838,208 B =  4.500 GiB   <- the brief's setting
```

**Step 3 — does it fit on 24 GB with the UD-IQ4_XS weights resident?**
Card = 24576 MiB = 24.000 GiB = 25,769,803,776 B. Weights = 14.3 GB (decimal, as HF lists) =
14,300,000,000 B = 13.318 GiB. Reserve 1.5 GB = 1,500,000,000 B for CUDA context + compute buffers,
as the brief specifies.

```
free for cache = 25,769,803,776 - 14,300,000,000 - 1,500,000,000 = 9,969,803,776 B = 9.285 GiB
minus GDN state (step 4, 1 slot, fp32)          -     156,893,184 B
                                                = 9,812,910,592 B = 9.139 GiB

max context, q4_0 : 9,812,910,592 / 18,432 = 532,383 tokens
max context, q8_0 : 9,812,910,592 / 34,816 = 281,846 tokens
max context, f16  : 9,812,910,592 / 65,536 = 149,733 tokens
```

**So 262,144 tokens on the GPU is feasible at `q4_0`/`q4_0` — with roughly 2x headroom.** The full
residency budget at that setting is:

```
weights 14,300,000,000 + KV 4,831,838,208 + state 156,893,184 = 19,288,731,392 B = 17.965 GiB
remaining on a 24.000 GiB card                                                   =  6.035 GiB
```

It also fits at `q8_0`/`q8_0`, with about 7% margin. It does **not** fit at `f16`.

A consequence worth stating plainly: **by this arithmetic `--ngl 54` is not required.** Full offload
would fit. Whatever motivates the 10-layer CPU split, the KV/weights budget is not it.

**Step 4 — the linear-attention state** (computed from the config's GDN dimensions; llama.cpp's own
allocator was **not** read this session, so treat the exact figure as UNSURE):

```
recurrent state = 48 layers x linear_num_value_heads(48) x linear_key_head_dim(128) x linear_value_head_dim(128)
                = 48 x 786,432 = 37,748,736 elements
                fp32 -> 150,994,944 B = 144 MiB per slot   (bf16 -> 72 MiB)

conv state      = 48 layers x (conv_kernel_dim - 1 = 3) x (2 x 16 x 128 + 48 x 128 = 10,240)
                = 48 x 30,720 = 1,474,560 elements -> fp32 5,898,240 B = 5.6 MiB

total          ~ 157 MB per slot at fp32
```

This does **not** grow with context, but it **does** multiply by the number of parallel slots. An
independent vLLM-side report puts the same quantity at "0.88 GiB" per resident request in its own
paging scheme — a different accounting (it includes verify blocks and padding), recorded rather
than reconciled.

**Step 5 — the `--ngl 54` split.** 54 of 64 repeating layers on GPU leaves 10 on the CPU
(`mtp_num_hidden_layers: 1` may make llama.cpp report 65 rather than 64 — UNSURE). Weights moved
off-GPU ≈ 14.3 GB × 10/64 ≈ 2.23 GB. Which ten is not established (C6.4); if they are the last ten,
indices 55, 59 and 63 are `full_attention`, so **3 of the 16 KV-bearing layers** and 3/16 of the KV
cache would sit host-side too.

**Cross-check against a measurement.** A community RTX 4090 (also 24 GB) matrix on UD-Q4_K_XL
reports: f16 KV tops out at 100k, q8 KV reaches 170k, q4_0 KV fits the full 262k. Running the same
formula with heavier UD-Q4_K_XL weights lands in the same place and the same order — the ceilings
scale exactly as 64 : 34 : 18 KiB/token. The formula and the measurement agree.

---

## 3. C8 / C14 — the bandwidth arithmetic, written out

**Step 1 — device bandwidths.**

```
RTX 3090 : 384-bit bus / 8 = 48 B per transfer x 19.5 Gbps = 936 GB/s
           (NVIDIA publishes "384-bit" and "24 GB GDDR6X" but no GB/s; 936.2 GB/s is the
            widely quoted product figure - secondary)
DDR4-3200 dual channel : 2 x 8 B x 3200 MT/s = 51.2 GB/s  theoretical   <- the owner's AM4 box
DDR5-5600 dual channel : 2 x 8 B x 5600 MT/s = 89.6 GB/s  theoretical   <- NOT APPLICABLE here
PCIe 4.0 x16           : ~32 GB/s theoretical, ~25 GB/s typical effective
```

**Step 2 — decode ceiling with all weights on the 3090.** A dense model reads every weight once per
token, so the ceiling is bandwidth / bytes-per-token.

```
936 GB/s / 14.3 GB = 65.5 tok/s          (weights only, KV traffic ignored)
per-token time = 14.3 / 936 = 15.28 ms
```

Add the KV read, which at long context is not negligible — attention reads the whole cache each token:

```
at 100k ctx, q4_0 : 100,000 x 18,432 = 1.84 GB -> +1.97 ms -> ceiling ~58 tok/s
at 262k ctx, q4_0 : 262,144 x 18,432 = 4.83 GB -> +5.16 ms -> ceiling ~49 tok/s
```

Measured community baselines bracket this: RTX 3090 llama.cpp baseline **40 t/s**
(contextstudios.ai), RTX 5060 Ti on the exact UD-IQ4_XS quant with MTP-1 and q4_0 KV at 64k
**45.6 t/s**. 40/65.5 = 61% of the theoretical ceiling, which is the usual llama.cpp efficiency band.

**Step 3 — the cost of `--ngl 54` (10 of 64 layers read from DDR4 every token).**

```
GPU share : 14.3 x 54/64 = 12.07 GB / 936 GB/s   = 12.89 ms
CPU share : 14.3 x 10/64 =  2.23 GB / 51.2 GB/s  = 43.62 ms   (theoretical DDR4-3200)
                                   / 41   GB/s   = 54.5  ms   (at 80% efficiency)

total     = 56.5 ms/token -> 17.7 tok/s   (both at 100% efficiency)
            67.4 ms/token -> 14.8 tok/s   (CPU side at 80%)

versus 65.5 tok/s fully resident  ->  a ~3.7x reduction in the ceiling
```

For contrast only, had the box been DDR5-5600: CPU share 2.23/89.6 = 24.9 ms, total 37.8 ms →
26.5 tok/s. The owner's AM4 platform cannot reach that figure (C14).

These are bandwidth ceilings, not predictions: they ignore CPU compute time for those 10 layers on
six physical cores, and PCIe round trips.

**Step 4 — `--no-kv-offload` with a 200k host-side KV.** The flag exists (`-kvo, --kv-offload`,
default enabled; `--no-kv-offload` disables). A 200,000-token q4_0 cache is
200,000 × 18,432 = 3.686 GB, and attention must read all of it per token:

```
if RAM-bandwidth-bound  : 3.686 / 51.2 GB/s = 72.0 ms  -> 13.9 tok/s
if PCIe-4.0-bound       : 3.686 / 25   GB/s = 147  ms  ->  6.8 tok/s
if PCIe-3.0-bound       : 3.686 / 12   GB/s = 307  ms  ->  3.3 tok/s
```

**The brief's "2-5 t/s" is not a measured figure from any source I could find (C8.11).** It sits at
the pessimistic end of this arithmetic bracket. Whether it is right depends on which bus binds,
which is exactly what the bracket cannot settle.

---

## 4. Claims in the brief with no primary-source support

1. **`--spec-draft-max 2`** — no such flag. The real one is `--spec-draft-n-max` (C6.15).
2. **`--spec-type draft-MTP`** — the accepted value list is lower-case `draft-mtp` (C6.14).
3. **`--flash-attn`** with no value — the current spelling is `-fa, --flash-attn [on|off|auto]`,
   default `auto`; whether the bare form still parses was not verified (C6.10, C6.11).
4. **"port 8000"** — llama-server's defaults are `127.0.0.1` and port **8080** (C11.1, C11.2).
   8000 is vLLM's and SGLang's default, which is what the official Qwen deploy snippets use.
5. **"medium yields ~98% of the intelligence"** — the only measured per-effort quality table found
   gives 8.18/8.61 = **95.0%**, from a single un-replicated run whose own noise estimate is 0.18
   against a 0.43 gap (C4.4, C4.5).
6. **"at 1/20th the thinking time"** — no source produces 1/20 for medium-vs-xhigh. Measured
   ratios found: **1/1.9** (median latency), **1/5.6** (wall clock, same machine), **1/6.7**
   (thinking tokens, same machine). The 7–11× figure that does exist is **low** vs xhigh, not
   medium (C4.6–C4.10).
7. **"Flash-Next faster but weaker on deep code"** — the vendor's own table has Flash-Next ahead of
   the 27B on **all eleven** shared benchmarks including every coding row (C5c.4). One community
   report supports the brief's direction on long agentic sessions (C5c.3). Both recorded; not
   reconciled.
8. **"performs better than Opus for surgical edits"** — no Aider polyglot entry, no
   `percent_cases_well_formed`, no edit-format measurement of any kind exists for this model
   (C3.15). On the vendor's own table Opus4.6 Max is **ahead** on Terminal Bench 2.1 (78.2 v 73.0)
   and NL2Repo-Bench (47.6 v 42.3), and the table's Opus column uses officially reported scores
   while every other column was re-run in a Claude Code harness (C3.9).
9. **"identity crisis: sometimes claims to be Claude"** — thread `1w8h0cb` not reachable and no
   corroborating source found anywhere (C5b.1). The well-documented incident runs the other way:
   Claude Opus 4.8 answering "Qwen" (C5b.2).
10. **"keen to execute git commands"** — the claim is real and correctly located, but the source
    attributes it to **Qwen3.6 and Qwen3.8 alike**, not to 3.8 as a new regression (C5a.3).
11. **"2-5 t/s" with a 200k host-side KV** — unsourced (C8.11); §3 brackets it at 3.3–13.9 t/s.
12. **`--threads 12`** — no llama.cpp guidance found either way; the box has 6 physical cores
    (C6.13).
13. **`--ngl 54`** — the memory arithmetic in §2 does not require any CPU offload for this quant at
    this KV setting; the brief gives no stated reason for the 10-layer split (C7.6).
14. **The model name in the brief, "Qwen 3.8 27B"** — the official string is `Qwen3.8-27B`, and the
    brief's filename `unsloth-qwen3.8-27b-UD-IQ4_XS.gguf` does not match the published
    `Qwen3.8-27B-UD-IQ4_XS.gguf`. Cosmetic, recorded for completeness.
15. **Unstated but load-bearing:** the model is **natively multimodal** with a vision tower
    (`vision_config`, depth 27) and `tie_word_embeddings: false` giving two 1.27 B vocab tensors.
    Both affect footprint and quantization behaviour and appear nowhere in the brief.

---

## 5. What can only be settled by measuring on the PC

Named measurements, not a plan:

1. **Whether the installed binary can load the model at all** — `llama-server --version` and a load
   attempt of a `qwen3_5` GGUF on b8184/b8631. Both builds predate the model's 2026-08-14 release
   (C13.5).
2. **Whether `--spec-type` exists in the installed binary** — `llama-server --help | grep spec-type`.
   Both local builds predate the 2026-05-16 MTP merge (C13.6).
3. **What `llama.cpp-mtp` on disk actually is** — `git -C llama.cpp-mtp log -1` and `git remote -v`
   (C15.5).
4. **Whether a CUDA-capable llama-server can be obtained on this host at all** — there is no CUDA
   Linux release asset (C13.1) and no nvcc, so the routes are: build with the CUDA toolkit
   installed, or run `ghcr.io/ggml-org/llama.cpp:server-cuda`. For podman the CDI spec is the open
   question — `/etc/cdi` is empty (coordinator FACT 1) and llama.cpp's docs carry no podman
   instructions (C13.10).
5. **Real decode rate, fully resident vs `--ngl 54`** — `llama-bench` (or a fixed prompt through
   the server) at f16/q8_0/q4_0 KV and at 4k / 64k / 262k context. §3 gives ceilings of ~65 / ~49
   tok/s resident and ~15–18 tok/s with 10 CPU layers; only measurement closes the gap between
   ceiling and reality.
6. **Effective DDR4 read bandwidth on this 5600X** — a STREAM or `mbw` run. §3 used the 51.2 GB/s
   theoretical figure (C8.4).
7. **Whether q4_0/q4_0 KV actually takes the GPU flash-attention path on the build in use** —
   compare tok/s at `-ctk q4_0 -ctv q4_0` against `-ctk f16 -ctv f16`; a collapse is the silent
   CPU-fallback signature (C6.7–C6.9). q4_0/q4_0 is in the documented default kernel set (C6.8),
   but that is a statement about master, not about whichever binary ends up installed.
8. **MTP acceptance rate and speedup for Qwen3.8-27B under llama.cpp on this 3090** — no such
   measurement exists publicly (C9.7). Every 3090 MTP number found is Qwen3.6-under-llama.cpp or
   Qwen3.8-under-vLLM.
9. **Actual per-slot context division under `-np N`** — read `/slots` (or the startup log's
   `n_ctx_per_seq`) at the intended `-np`. Upstream behaviour changed with unified KV and
   `--kv-unified-per-slot` (C10.1), and `--parallel 1` has been reported to open 4 slots (C10.2).
10. **How many concurrent ~100k-token sessions actually hold** — §2 gives a KV budget of ~532k
    q4_0 tokens total, which is two 262k sessions or five 100k sessions *by arithmetic alone*, before
    per-slot GDN state and compute buffers. No published measurement exists for llama.cpp on this
    card (C10.4), and the nearest vLLM measurement found the opposite of intuition: fewer admitted
    slots did 40% more work (C10.8).
11. **Reasoning effort on the owner's own briefs** — the per-effort tables that exist are one-shot
    web/SVG tasks, not hours-long agent sessions with 100–200k-token contexts. The one source that
    measured agentic rounds found low was *slower* than medium because it needed six more rounds
    (C4.13). Round count × time per round is the quantity; nobody has measured it for this workload.
12. **Whether the chat template's `preserve_thinking` default breaks prompt-cache reuse across
    turns** — the HN thread describes the harness/template mismatch that forces full reprocessing
    (see C15.6's branch); measurable as cache-hit rate in the server log.

---

## 6. Fetch log — every URL tried

| URL | result |
|---|---|
| huggingface.co/Qwen/Qwen3.8-27B | LOADED |
| huggingface.co/Qwen/Qwen3.8-27B/raw/main/config.json | LOADED (full JSON) |
| huggingface.co/Qwen/Qwen3.8-27B/raw/main/README.md | LOADED (2 prompts) |
| huggingface.co/Qwen/Qwen3.8-27B/discussions/113 | LOADED (WebFetch + Exa) |
| huggingface.co/Qwen/Qwen3.8-27B/discussions/68 | LOADED (via Exa highlights) |
| github.com/QwenLM/Qwen3.8 | LOADED |
| github.com/QwenLM/Qwen3.8/blob/main/README.md | LOADED (via Exa) |
| qwen.ai/blog?id=qwen3.8 | LOADED (via Exa) |
| alibabacloud.com/blog/…qwen3-8-27b…_603463 | LOADED (via Exa) |
| huggingface.co/unsloth/Qwen3.8-27B-GGUF | LOADED |
| huggingface.co/unsloth/Qwen3.8-27B-GGUF/tree/main | LOADED (via Exa) |
| huggingface.co/unsloth/Qwen3.8-27B-GGUF/discussions/74 | LOADED (via Exa) |
| huggingface.co/unsloth/Qwen3.8-27B-GGUF/discussions/102 | LOADED (via Exa) |
| unsloth.ai/docs/models/qwen3.8 | LOADED |
| unsloth.ai/docs/basics/dynamic-3.0-ggufs | LOADED (via Exa) |
| raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/server/README.md | LOADED (2 prompts) |
| raw.githubusercontent.com/ggml-org/llama.cpp/master/docs/speculative.md | LOADED |
| raw.githubusercontent.com/ggml-org/llama.cpp/master/docs/docker.md | LOADED |
| raw.githubusercontent.com/ggml-org/llama.cpp/master/docs/build.md | LOADED |
| github.com/ggml-org/llama.cpp/pull/22673 | LOADED |
| github.com/ggml-org/llama.cpp/issues/22947 | LOADED (thin) |
| github.com/ggml-org/llama.cpp/issues/28455 | LOADED |
| github.com/ggml-org/llama.cpp/issues/24485 | LOADED (did not answer the kernel-set question) |
| github.com/ggml-org/llama.cpp/issues/20409 | LOADED |
| github.com/ggml-org/llama.cpp/releases | LOADED (b10955) |
| github.com/ggml-org/llama.cpp/releases/tag/b8184 | LOADED |
| github.com/ggml-org/llama.cpp/releases/tag/b8631 | LOADED (year field suspect) |
| github.com/ggml-org/llama.cpp/pull/26296 | NOT-FETCHED (referenced only) |
| github.com/ggml-org/llama.cpp/pull/27342 | NOT-FETCHED (referenced only) |
| nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3090-3090ti/ | LOADED (no GB/s printed) |
| techpowerup.com/gpu-specs/geforce-rtx-3090.c3622 | **FAILED** — HTTP 403 (WebFetch), JS shell only (Exa) |
| anthropic.com/news/claude-opus-5 | LOADED (no raw SWE-bench figures) |
| anthropic.com/news/claude-opus-4-6 | reached via search summary only — **NOT-FETCHED directly** |
| aider.chat/docs/leaderboards/ | reached via search summary only — no Qwen3.8 entry surfaced |
| **www.reddit.com/r/LocalLLaMA/comments/1vtq8hc** | **FAILED** — "unable to fetch from www.reddit.com" |
| **old.reddit.com/r/LocalLLaMA/comments/1vtq8hc** | **FAILED** — "unable to fetch from old.reddit.com" |
| reddit .json suffix variants | **NOT ATTEMPTED** — same blocked domains |
| Exa fetch of /1vtq8hc/, /1vvsokm/, /1w8h0cb/ | **FAILED** — SOURCE_NOT_AVAILABLE (all three) |
| bittide.aicompass.dev/article/6fc2278a-… | LOADED — mirrors thread 1vvsokm, gives its permalink |
| bittide.aicompass.dev/article/7e490676-… | LOADED (via Exa) — medium-vs-xhigh thread |
| bittide.aicompass.dev/article/80df6b48-… | LOADED (via Exa) — one-week roundup + perf matrix |
| bittide.aicompass.dev/article/c5cc4618-…, 57d1a74d-…, a74a4cb3-…, 5d3a095e-… | LOADED (via Exa) |
| news.ycombinator.com/item?id=49324985, 49355510 | LOADED (via Exa highlights) |
| simonw.substack.com/p/qwen-38-27b-is-excellent-but-it-defaults | LOADED (via Exa) |
| kodesage.ai/blog/qwen-3-8-27b-llm-model-review | LOADED (via Exa) |
| rizz.dev/feed/qwen-38-overthinks-default-reasoning-setting | LOADED (via Exa) |
| github.com/syv-ai/qwen38-27b-rtx3090 (+ /blob/main/README.md) | LOADED (via Exa) |
| huggingface.co/avyukth/Qwen3.8-27B-AWQ-INT4 | LOADED (via Exa) |
| huggingface.co/biMEMO/Qwen3.8-27B-int4-AutoRound | LOADED (via Exa) |
| huggingface.co/pearsonkyle/Qwen3.8-27B-GPTQ-W4A16 | LOADED (via Exa) |
| huggingface.co/Twu31/Qwen3.8-27B-AWQ-INT4-MTP-LowLatency | LOADED (via Exa) |
| contextstudios.ai/blog/qwen-3-8-27b-hardware-guide | LOADED (via Exa) |
| inferya.com, myclaw.ai, llm-stats.com, ai.rs, yottalabs.ai, mindstudio.ai comparisons | LOADED (via Exa) |
| blog.kilo.ai/p/did-claude-opus-48-distill-alibabas | LOADED (via Exa) |
| github.com/QwenLM/Qwen3/discussions/1898 | LOADED (via Exa) |
| pkg.go.dev/github.com/ollama/ollama/envconfig | reached via search summary only |
| vellum.ai / morphllm.com / datanorth.ai Opus pages | reached via search summary only — **NOT-FETCHED directly** |

**Source-quality note.** Rows citing `bittide.aicompass.dev`, `kodesage.ai`, `rizz.dev`,
`contextstudios.ai`, `inferya.com`, `ai.rs`, `mindstudio.ai`, `llm-stats.com`, `yottalabs.ai`,
`codersera.com` and `tokenfeed.ai` are **secondary**. They are used only where the primary is
unreachable (Reddit, X) or does not exist (per-effort quality measurements). Every architecture,
flag, licence, size and official-benchmark row is primary: the HF model card, the raw
`config.json`, the QwenLM GitHub repo, the Unsloth docs and repo, and the llama.cpp repository.
