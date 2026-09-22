<!-- Evidence lane report (Opus 5 evidence-gatherer), 2026-09-22, extracted verbatim from the lane transcript; file:line anchors refer to the cloned repositories at their audited heads -->

EVIDENCE REPORT — NandhaKishorM/laya @ 573e5b6 (Apache-2.0), read-only at `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/jev/laya`. Clone is a single squashed commit (`git rev-list --count HEAD` = 1, dated 2026-09-21 23:47 +0530), so per-file git chronology is unavailable — every file dates to that one commit. No installs, no imports of torch, no network calls were made. All paths below are repo-relative.

## 1. Public API

| Symbol | Signature (file:line) | Takes / returns | Mark |
|---|---|---|---|
| `laya.__all__` | `laya/__init__.py:27-55` | 21 names + `__version__`="0.3.5" (`:26`) | SOLID |
| `Agent(...)` | `laya/agent.py:103-109` | `(model_id_or_path="convaiinnovations/laya", device=None, token=None, subfolder=None)` | SOLID |
| `Agent.system_one` | `laya/agent.py:265-368`, `@torch.no_grad()` | `(state: str|dict|list, questions: Dict[qid, qdef]) -> {"model":"laya-rl-agent","answers":{...},"usage":{"input_tokens":N,"output_tokens":0}}` | SOLID |
| `Agent.predict` | `laya/agent.py:370` | alias of `system_one` | SOLID |
| `RLAgent` | `laya/agent.py:373` | alias of `Agent` | SOLID |
| `load(...)` | `laya/agent.py:376-385` | thin ctor wrapper | SOLID |
| `Router` | `laya/router.py:145-155` | `(models=None, device=None, token=None, max_loaded=1, default="english", auto_task_detection=False, standalone_repos=False, preload=False)` | SOLID |
| `Router.route` | `laya/router.py:257-312` | `(state, questions=None, model=None, task=None, lang=None) -> RouteDecision`; loads/runs nothing | SOLID |
| `Router.predict` / `.system_one` | `laya/router.py:315-333` | `system_one` payload + `result["routing"] = dict(decision)` | SOLID |
| `Router.load/attach/preload/unload/loaded` | `:175,209,223,239,251` | lifecycle; `loaded` is LRU order | SOLID |
| `RouteDecision` | `laya/router.py:83-98` | `dict` subclass, keys `model, repo, reason, detection, workflow`; `.model`/`.reason` props | SOLID |
| `DEFAULT_MODELS` | `laya/router.py:38-42` | `{english:(repo,None), multilingual:(repo,"multilingual"), typed-decisions:(repo,"typed-decisions")}`; `STANDALONE_MODELS` `:45-49` | SOLID |
| `shortlist_choice` | `laya/shortlist.py:27-48` | `(state, criteria, embed_fn, k=20, *, instructions=None) -> List[label]` | SOLID |
| `predict_shortlist` | `laya/shortlist.py:51-108` | `(agent, state, questions, embed_fn, k=20, **predict_kwargs)` → model result + `["shortlist"][qid] = {labels,scores,k,n,passthrough}` | SOLID |
| `embed_fn_from_agent` | `laya/shortlist.py:111-163` | mean-pool of `agent.model.encoder`, `(texts)->(n,dim)` np.float32 | SOLID |
| `detect_language`(=`lang.analyse`)/`detect_script`/`is_english` | `laya/lang.py:208,111,240` | see §7 | SOLID |
| `clean_email_body`/`email_state` | `laya/email.py:37,58` | quoted-history/signature/disclaimer stripper; `max_chars=3000` | SOLID |
| presets | `laya/presets.py:5,45,82,122,154` | `triage_/email_/guard_/moderation_/router_questions()` → question dicts | SOLID |
| `proper_reward`,`td_lambda_targets`,`ece_score`,`confidence_from_probs`,`render_options`,`QTYPES`,`QTYPE_NAMES` | `laya/common.py:150,179,197,210,33,11,12` | training/metric helpers; `QTYPES={"choice":0,"score":1,"noul":2}` | SOLID |

**Question schema** (`laya/agent.py:255-263`, `laya/common.py:33-46`): `{"type": "choice"|"score"|"noul", "instructions": str-or-JSONable, "criteria": ...}`. `choice` criteria = dict `{label: description|None}` or a plain list (list → `{c: None}`, `agent.py:258-259`). `score` criteria = ordered list, rendered `"level %d: %s"`. `noul` criteria optional dict `{"true":…,"false":…}`; absent → defaults `"no, the statement does not hold"/"yes, the statement holds"` (`common.py:41-46`); option order is always `[false, true]`.

**Returns** (`agent.py:337-362`) — probabilities are softmax over per-option logits divided by a temperature bucket (`agent.py:329-332`; bucket = `(qtype, option-count)`, `common.py:219-221`):
- `choice`: `{type, choice, probabilities:{label:p}, confidence, action:{act_probability}}`
- `score`: `{type, score = Σ i·p_i (expected level), legend:{"0":…}, probabilities:{"0":p}, confidence, action}`
- `noul`: `{type, noul = p[1], confidence = max(p1,1-p1), action}`
`confidence` for choice/score is normalized-entropy `1 - H(p)/log k` (`common.py:210-216`), **not** the top probability — SOLID. Calibration: temperatures ship in the checkpoint but are clamped to [0.5, 5.0] at load (`common.py:228-240`, `agent.py:206-220`) with a `RuntimeWarning`; the English checkpoint's shipped `choice:11+` = 0.1006 is rejected by that clamp (source comment `common.py:224-228`; value confirmed at `research/results/t4_colab_benchmark.json:31`). `laya-multilingual` ships all-1.0 temperatures (`t4_colab_benchmark.json:57-58`-region, `caveats.shipped_calibration`).

**Batching**: one call = ONE forward pass over all questions for ONE state (`agent.py:291` `collate_items([items], pad_id)`). `collate_items` (`common.py:247`) accepts a list of groups, so multi-state batching exists internally but **no public entry point exposes it** — SOLID.

**Router dispatch rule** (`router.py:270-312`), precedence: explicit `model` > explicit `task` > detected typed-decisions workflow (only if `auto_task_detection=True`, exact question-id set match against 4 signatures `router.py:75-80`) > explicit `lang` > detected script/language > `default`. Script≠latin → multilingual; latin but not English → multilingual; else english. `preload()` (`router.py:223-237`) raises `max_loaded` to fit, loads each missing name, returns `self`; `Router(preload=True)` loads all three (~1.16B params, `router.py:134-135`).

## 2. Model loading

| Fact | Evidence | Mark |
|---|---|---|
| Fetch call is `snapshot_download` only; no `hf_hub_download` anywhere | `laya/agent.py:126,137`; grep over repo | SOLID |
| Files fetched: `rl_agent_config.json`, `model.safetensors`, `tokenizer/*`, `encoder/*`, each prefixed by `<subfolder>/` | `agent.py:130-136` | SOLID |
| Token: `token` arg or `HF_TOKEN` env (only env vars laya reads, with `router.py:160`) | `agent.py:132` | SOLID |
| No `cache_dir` is passed → huggingface_hub default cache (`~/.cache/huggingface/hub`, `HF_HOME`/`HF_HUB_CACHE` honoured by the library, not by laya) | `agent.py:131-137` (absence) | SOLID absence / UNSURE on exact path |
| If the checkpoint has no `encoder/` dir, `AutoModel.from_pretrained(cfg["encoder"])` downloads the base encoder; same fallback for the tokenizer | `common.py:139-147`, `agent.py:184-188` | SOLID |
| Checkpoint byte sizes: **not stated anywhere**. Params are: 421.29M total / 394.78M encoder (laya), 321.91M / 306.94M (multilingual) | `t4_colab_benchmark.json:13-14,46-47`; README.md:31-35 | SOLID |
| dtype: `amp_dtype` → bf16 only if cfg says `"bf16"`, else fp16 (`common.py:243-244`); CUDA cap<8 → fp16; **CPU and MPS forced to float32**; autocast enabled only on CUDA | `agent.py:221-226,292-295` | SOLID |
| No int8/4-bit/quantization/ONNX anywhere (grep: int8, bitsandbytes, quantiz, gptq, awq, load_in_) | repo-wide grep, zero hits in `laya/` | SOLID |
| CPU path is first-class: device auto-resolves cuda→mps→cpu; requested-but-absent cuda/mps warns and falls back; OOM at load and at inference falls back to CPU | `agent.py:165-182,228-252,303-317` | SOLID |
| `reference_compile=False` set on the encoder to keep torch.compile off | `agent.py:196-202` | SOLID |
| Context limits come from the checkpoint cfg: `max_len` default 512, `head_max_len` default 192; shipped = 512/192 (laya), 1024/256 (multilingual, typed-decisions) | `agent.py:281-282`; `t4_colab_benchmark.json:19-20,52-53`; README.md:366-369 | SOLID |
| **Longer states are silently truncated, never chunked, never an error**: state ids are cut to the remaining room, right-truncated (`st[:room]`); `truncate_left=True` exists but `system_one` never passes it | `common.py:82-86`, `agent.py:286` | SOLID |
| Options that don't fit the head budget: first shrunk per-option, then the instruction head is cut; if markers are still lost, `ValueError("question %r options exceed head_max_len=%d")` | `common.py:68-75`, `agent.py:287-288` | SOLID |
| Weight/arch verification before `load_state_dict(strict=True)`: required cfg keys, required prefixes, shape mismatches, missing tensors | `agent.py:53-97,192-194` | SOLID |

## 3. Dependencies and floors

| Fact | Evidence |
|---|---|
| `requires-python = ">=3.10"` | `pyproject.toml:10` (SOLID) |
| Deps: `torch>=2.0.0`, `transformers>=4.48.0`, `safetensors>=0.4.0`, `huggingface_hub>=0.20.0`, `numpy>=1.20.0` | `pyproject.toml:27-33` (SOLID) |
| **No optional extras, no `[project.scripts]`, no entry points** | `pyproject.toml:35-41` (absence, SOLID) |
| `setup.py` is a 4-line shim; metadata only in pyproject | `setup.py:1-4` (SOLID) |
| Nothing blocks a CPU-only install: CI itself installs CPU-wheel torch and runs the suite | `.github/workflows/ci.yml:37-51` (SOLID) |
| No CUDA-only import/code path; `torch.cuda.*` calls are all guarded by `is_available()` / device-type checks | `agent.py:168,177,223,232,303` (SOLID) |
| Packaging is gated by a test (transformers floor ≥4.48 "ModernBERT support", classifiers ≥ floor, CI pythons ≥ floor) | `tests/test_packaging.py:40-71` (SOLID) |
| README claims the 3.10 floor comes from "`huggingface_hub` 1.x, `transformers` 5.x and `torch` 2.14" — the pins do not say that | `README.md:45` vs `pyproject.toml:27-33` (SOLID discrepancy) |

## 4. Performance evidence

**Measured in-repo (T4, `research/results/t4_colab_benchmark.json`; meta `gpu="Tesla T4"`, torch 2.11.0+cu128, transformers 5.17.0, seed 13, per_lang 300, ts 2026-09-19 04:45):** latency block gives laya p50 39.5 / 84.5 / 158.6 / 771.3 ms at 1/5/10/50 questions (p95 44.8/86.0/160.1/806.7) and multilingual 32.8 / 40.1 / 72.3 / 337.4 ms (p95 38.8/43.5/74.4/**693.7**) — per-question 15.43 and 6.75 ms at batch 50. Sample count per latency point is NOT recorded in the JSON (UNSURE). Option-order flip rates: laya 0.15/0.04/0.00, multilingual 0.23/0.09/0.015 on massive_intent.en / en.emotion / xnli.en, n=200 each. English macro: laya 0.684 acc / 0.1938 ECE, multilingual 0.6192 / 0.2842 over 2516 questions, 5 suites. typed_decisions summary: **laya 0.362 acc, ECE 0.1741; laya-multilingual 0.3515 acc, ECE 0.3144**, n=2000. Calibration repair (out-of-sample refit) per suite, e.g. typed_decisions ECE 0.2071→0.1287, massive_intent.en 0.2562→0.1140, massive_intent.de 0.5463→0.0925. All SOLID.

**Measured in-repo (CPU, `research/results/cpu_51_language_sweep.json`; meta `device="cpu"`, torch 2.8.0, laya **0.2.0**, `threads: 4`, ts 2026-09-19 11:04; lines 2-8):** the CPU **model** is not recorded — no processor string anywhere (UNSURE/not-found). part_a: 51 langs × 100 cases × 20 options; per-language wall time **11.6–25.6 s** (english, median 20.2) and **7.7–10.3 s** (multilingual, median 8.6) → **116–256 ms/case** and **77–103 ms/case** at 4 threads, 1 question per case. Macro accuracy 0.2269 / 0.3661, macro ECE 0.7331 / 0.3869, above-3×-random 23 / 45 of 51. part_b (typed-decisions, 2000 decisions, 400 cases, 5 questions per case) contains **only the `english` model**: acc 0.3615, ECE 0.1747, Brier 0.7497, soft 0.3315, score_MAE 0.6937, 557.0 s, **`ms_per_case` 1392.5** (`:1339-1352`). All SOLID.

**Third-party / not measured here (explicitly flagged by the repo):** every Jev figure. `BENCHMARKS.md:3`, `research/README.md:51-58` ("no TypeSafe API credential… Jev was never run here"), `cpu_51_language_sweep.json:1334`. Sources named: AbdelStark/jev-benchmarks (AG News 0.910, Banking77 0.870, Emotion 0.480) and nibzard/decision-model-benchmark (ECE 0.246, banking77 0.763, flip rate 13%, 264–276 ms p50) — `research/README.md:54-58`. Headline Jev figures in `BENCHMARKS.md:17-21`: 0.727 / 0.910 / 0.480 / ECE 0.246 / 236-276 ms.

**Claims with NO committed producer in this tree (UNVERIFIED, evidence of absence):**
- `laya-typed-decisions` appears in **no** result file: `t4_colab_benchmark.json` meta has only `laya` and `laya-multilingual`; CPU `part_b.by_model` has only `english`. The headline **0.766** typed-decisions accuracy (`BENCHMARKS.md:17,142`; `README.md:281,308`) and the four per-workflow numbers (0.730/0.764/0.804/0.766, `BENCHMARKS.md:152-155`) are therefore not reproducible from the committed data. SOLID (absence proven by full-file parse, not a capped query).
- `BENCHMARKS.md:9` cites `research/results/app_benchmark.json`; the directory holds exactly two files (`ls research/results/`). Every "Themes" number (`BENCHMARKS.md:112-134`) and the AG News / Emotion / banking77 rows come from that missing file. SOLID.
- CPU deployment figures in `README.md:144,167` ("7.4 s median reload on CPU", "10.3 s on T4", "193–464 ms (CPU)") have no committed JSON: `bench_latency.py:37` writes `latency_benchmark_results.json` at repo root, which is absent. SOLID.
- `README.md:256` links `notebooks/laya_benchmark_colab.ipynb`; the file lives at `research/scripts/laya_benchmark_colab.ipynb` (`notebooks/` holds only the fine-tune notebook). SOLID.
- Internal inconsistency: typed-decisions Brier is 0.061 in `BENCHMARKS.md:142` and 0.062 in `README.md:308`; laya accuracy 0.361 vs 0.362; multilingual zero-shot 0.342 (`BENCHMARKS.md:144`) vs 0.352 (`README.md:362`) vs measured 0.3515 (T4 JSON). SOLID.

## 5. Tests

| File | Asserts | Needs weights/network? |
|---|---|---|
| `tests/test_router.py` (435 L, 84 checks) | script detection over 13+ scripts, `is_english`, `latin_profile` fields, `analyse` keys, alias/normalise, `match_typed_decisions_workflow`, LRU/evict/attach/preload, `clamp_temperature`/`temp_bucket`, **8- and 20-thread concurrent `load()` dedup** (`:354-427`) | No — "No model weights are loaded: `Router.route` is pure" (`:1`); Agent is monkeypatched |
| `tests/test_shortlist.py` (488 L, 79) | exports, k validation, cosine ranking/tie order, passthrough when k≥n, criteria dict/list, non-mutation of caller dict, `embed_fn` arg validation | No — fake `embed_fn`, mocked predict (`:1-5`) |
| `tests/test_criteria.py` (122 L, 32) | `render_criterion` str/dict/list/int/bool/non-ascii/unserialisable; the PR-#2 `noul`-dict crash | No |
| `tests/test_email.py` (105 L, 11) | disclaimer stripping must not eat the request; quote headers; empty body | No |
| `tests/test_decision_model.py` (101 L, 3 tests) | issue #96 single-option `topk(2)` crash; `top1-top2 == 1.0`; multi-option unaffected | No — tiny from-config BERT, "no pretrained weights downloaded" (`:1-5`) |
| `tests/test_download.py` (119 L, 4 tests) | `snapshot_download` called once with the right repo/token; **only the selected subfolder's files are fetched** (real `filter_repo_objects` semantics); local paths never download | No — transport patched, tiny local safetensors built in setUp (`:29-95`) |
| `tests/test_packaging.py` (78 L, 7) | see §3 | No |
| `tests/test_local_e2e.py` (220 L, 13) | routing + presets on **real weights**, defaults to `~/laya_models` with all three checkpoints (`:27-31`), device via `LAYA_DEVICE` | **YES** — and it is the one file **not** run in CI (`ci.yml:44-54`) |

No pytest/unittest discovery config; six files are executable scripts run directly by CI. `security.yml` adds gitleaks (diff + working tree) and a dependency-CVE job; dependabot weekly for pip and actions.

## 6. HTTP / serving surface

**NONE FOUND.** Searched the whole tree (excluding `.git`) for `fastapi|flask|uvicorn|aiohttp|starlette|bottle|tornado|http.server|BaseHTTPRequestHandler|/v1/decide|@app\.|app\.post|serve(|listen(|socket|gradio|endpoint|requests.post`, plus `argparse|click.command|console_scripts|entry_points|def main(|__main__`. Every hit is a benchmark/asset script (`research/scripts/bench_*.py`, `assets/make_logo.py`) or a test `__main__` guard; `pyproject.toml` declares no `[project.scripts]`. The only "server" mentions are prose in `router.py:136,228` and `README.md:146`. There is **no CLI and no `{state, questions} -> {answers}` HTTP endpoint** in the repo — the in-process shape `Router.predict(state, questions) -> {"answers":…, "routing":…}` (`router.py:315-331`) is the closest match and would have to be wrapped by the caller. `RouteDecision` is a `dict` subclass "so it serialises straight into an API response" (`router.py:86`). An external HF Space demo is referenced (`README.md:16,411`) but its code is not in this repo. SOLID.

## 7. Long-lived local service notes

| Fact | Evidence | Mark |
|---|---|---|
| `Router` guards load/unload/attach/preload + LRU with a `threading.RLock`; **inference is deliberately outside the lock** so concurrent predictions share a checkpoint | `router.py:166-170,181,232` | SOLID |
| Concurrent `load()` dedup is tested (8 and 20 threads) | `tests/test_router.py:354-427` | SOLID |
| `Agent` itself has **no lock**, and `system_one`'s OOM handler mutates shared instance state (`self.device`, `self.dtype`, `self.model.to(cpu)`) mid-call | `agent.py:303-315` (absence of lock: `agent.py` has no `threading` import) | SOLID |
| `Agent.__init__` **writes to the downloaded cache**: `_fix_tokenizer_config` rewrites `tokenizer/tokenizer_config.json` in place, swallowing all exceptions | `agent.py:25-50,146` | SOLID |
| Model reload cost: prose only — "a cold load costs seconds", "7 to 10 s on every language switch" (`README.md:166`), "7.4 s median reload on CPU and 10.3 s on T4" (`README.md:144`) — no committed measurement | see §4 absence | UNSURE (claim, no producer) |
| Memory: three checkpoints ≈1.16B params (`router.py:134-135`); `max_loaded` default 1 with LRU eviction; `attach()` avoids a duplicate 421M copy; `unload()` frees. No byte figures, no `gc`/`empty_cache` call anywhere | `router.py:145-254` | SOLID |
| `lang.py` detection is **dependency-free pure Python**: exact Unicode-block script detection over 25 named ranges (`:17-43`), a 9-language function-word list (`:47-69`), and a non-English-diacritic set with a 0.02 rate threshold (`:74-83,155`). `analyse` returns `{script, script_profile, language, is_english, language_undecided, diacritic_rate, non_latin_fraction}`; state is flattened to ≤4000 chars, dict keys ignored, recursion capped at depth 6 (`:87-108`). "Undecided is not English" (`:228-233`) | `laya/lang.py` | SOLID |
| `agent.py` is the **inference runtime**, not an agent-tool/tool-calling helper: it loads a checkpoint and answers typed questions. `Agent`/`RLAgent` is the "RL Agent decision model" of the RLCD training (error strings `agent.py:61,70`); `rl_agent_config.json` is the checkpoint config | `agent.py:1,100-101,373` | SOLID |
| `laya.email_questions` resolves to the **presets** copy; `laya/email.py:70-104` holds a second, byte-identical definition (diff: docstring only) | `__init__.py:13,16-22`; diff of `presets.py:45-79` vs `email.py:70-104` | SOLID |
| `Router.route` typed-decisions branch returns the raw spec tuple as `repo` instead of `_repo_str(...)` used by every other branch | `router.py:282` vs `:272,277,288,311` | SOLID |
| Only env vars read by the package: `HF_TOKEN` (twice). No config-by-environment | `agent.py:132`, `router.py:160` | SOLID |

## 8. License and provenance

`LICENSE` is verbatim Apache-2.0 boilerplate, 176 lines, head `Apache License / Version 2.0, January 2004` (`LICENSE:1-3`); it ends at "END OF TERMS AND CONDITIONS" (`:176`) — **the standard Appendix and any copyright-holder line are absent** (grep for `Copyright (c)` finds only the body's generic uses). `pyproject.toml:11` `license = { text = "Apache-2.0" }`, author `Convai Innovations` (`:12-14`). `README.md:448`: "Apache 2.0. Developed by Convai Innovations."

Model cards / hosted artifacts referenced: `convaiinnovations/laya`, `convaiinnovations/laya-multilingual`, `convaiinnovations/laya-typed-decisions` (`router.py:37-49`, `README.md:33-35`), Space `convaiinnovations/laya-demo` (`README.md:16,411`), homepage/demo URLs in `pyproject.toml:39-41`.

**Jev/TypeSafe relationship as the README states it: purely a competitive comparison, no affiliation, no code or API dependency.** `README.md:273-298` "Laya (with routing) vs Jev"; `README.md:277` and `BENCHMARKS.md:3` both say Jev figures are "third-party published, never measured here (no TypeSafe API access)"; `research/README.md:51` "There is no TypeSafe API credential in this project, so **Jev was never run here**". The comparison table lists Jev as "closed API… $0.042 / 1M tokens" against Laya "Apache 2.0… $0 self-hosted" (`README.md:288-289`). The repo also concedes where Jev leads (`README.md:294-298`): >20-option label spaces (banking77 0.870 vs 0.425), soft-distribution match (0.580 vs 0.471), raw pre-temperature ECE (0.144 vs 0.213). No `jev`/`typesafe` import, URL call or credential exists in code — grep hits are documentation only.

## UNSURE / not found
1. **Checkpoint byte sizes** — nowhere in the repo; only parameter counts (421.29M / 321.91M) and the 421M/322M/421M README table. The typed-decisions checkpoint's params are stated only in README prose, never in a result file.
2. **CPU model/host for the CPU sweep** — `meta` records only `device: "cpu"`, `torch 2.8.0`, `threads: 4` (`cpu_51_language_sweep.json:2-8`). No processor string, no RAM, no contention note.
3. **Sample counts / repetitions behind the T4 latency p50/p95** — not recorded in `latency` (only p50/p95/ms_per_question).
4. **Any measurement of `laya-typed-decisions`** — absent from both committed result files (see §4); the 0.766 headline, the four workflow scores, the per-primitive numbers (noul 0.857 / choice 0.733 / score 0.723, `README.md:319`), and every "Themes" row have no committed producer here. `research/results/app_benchmark.json` (cited `BENCHMARKS.md:9`) does not exist.
5. **CPU latency for a *server-shaped* call** — the only CPU timings are 100-case sweeps (1 question) and a 400-case typed-decisions run (5 questions, 1392.5 ms/case). No p50/p95, no batch curve, no per-question breakdown, no thread-count sweep. README's "193–464 ms (CPU)" and the 7.4 s / 10.3 s reload figures have no committed JSON.
6. **Exact HF cache path** — laya passes no `cache_dir`; the location is whatever huggingface_hub defaults to. Inferred, not read in this source.
7. **Concurrency behaviour of `Agent.system_one` under real load** — no lock and an instance-mutating OOM path are visible in source, but no test or measurement exercises concurrent `predict` on one Agent (only concurrent `load()`). No thread-safety statement exists for `Agent`.
8. **Per-file git chronology** — the clone is one squashed commit; I could not date any individual change, and the referenced issues/PRs (#2, #34, #95, #96, #102) are cited only in docstrings, not verifiable from this tree.
9. **Encoder base-model download size/identity when `encoder/` is absent** — depends on `cfg["encoder"]` inside the checkpoint, which is not in this repo (README names ModernBERT-large / mmBERT-base).
10. **The HF Space demo's serving code** — not in this repository; whether it exposes an HTTP decide endpoint could not be determined from source here.

