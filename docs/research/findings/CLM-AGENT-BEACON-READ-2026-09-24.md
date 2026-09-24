# CLM and agent-beacon: static read (evidence only)

- Date: 2026-09-24 (lane clock start 11:10:28Z). Model: Opus 5.5 (`claude-opus-5-5`), evidence-gatherer lane.
- Task #222 (D-069 item 6). Brief: `tasks/briefs/jev/CLM-AGENT-BEACON-READ-brief.md` (78f9cc2). Our repo HEAD read: 78f9cc2.
- **Contrastive-LM/clm HEAD `7956937c58ed5839c06ddc4dc6b6b61c3a3e4094`**: root commit "Initial Commit", 2026-09-24T10:08:57Z, author `jackyk02`.
- **Asymptote-Labs/agent-beacon HEAD `5303224c63ddb73b7c2a125278f4233d807348d9`**: merge "docs: rewrite the Fleet and S3 rollout guide (#648)", 2026-09-24T01:06:32+02:00 (= 2026-09-23T23:06:32Z).
- Posture: EVIDENCE ONLY. No verdict, no recommendation. The coordinator decides.

## 0. Method, limits, legend

```
df -B1 /home/user                       -> avail 1,421,074,432 B at 11:10Z (floor used: 800 MiB = 838,860,800 B)
GIT_LFS_SKIP_SMUDGE=1 GIT_TERMINAL_PROMPT=0 timeout 570 git clone --depth 1 --no-checkout <url> <path>
   (+ a disk watchdog that kills the clone below 912,261,120 B free; it never fired)
git ls-tree -r -l HEAD                  -> tree size measured BEFORE any file was written
GIT_LFS_SKIP_SMUDGE=1 git reset --hard HEAD
```

- Deviation from the brief's command: `--no-checkout`, `GIT_TERMINAL_PROMPT=0` and the watchdog, so the floor check ran
  before any file was written; the end state is the same. git-lfs is not installed; no LFS pointers, no `.gitattributes`.
- Sizes: CLM pack 915.72 KiB, 45 files, 2,198,119 B on disk. agent-beacon pack 38.45 MiB, 1,500 files, 92,765,790 B on
  disk. Lowest free space seen: 1,650,393,088 B.
- Static only: nothing from either repo was executed, imported, installed or built. Our tools on their data: grep, sed,
  awk, nl; python3 `json` (CLM results); python3 `zipfile` (catalogue and 64 header bytes of `beacon.zip`, not extracted);
  the Read tool on two CLM PNGs. agent-beacon's own `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.cursor/` were read as data only.
- Legend: SOLID / UNSURE = confidence. MEASURED-IN-REPO = a test, fixture or committed output in the repo asserts it (not
  re-run by me). CLAIMED-ONLY = prose, figure or comment with no producer or output in the repo. DERIVED = my arithmetic (§2.3).
- Git dates: CLM HEAD has no parent (`git cat-file -p HEAD`), so every CLM file dates 2026-09-24T10:08:57Z. agent-beacon is
  a shallow clone of a merge commit: per-file dates UNKNOWN, 2026-09-23T23:06:32Z is an upper bound. Our files: §4.

## 1. Side by side

| # | Dimension | CLM | agent-beacon |
|---|---|---|---|
| R2 | README purpose | "a new class of System One model trained with a contrastive learning objective that connects states and actions. This repo serves CLM-8B behind a TypeSafe-compatible API" (README.md:20-23) | "captures agent session history across Claude Code, Cursor, Codex, OpenCode, and 20+ other harnesses, then turns useful workflows, corrections, and debugging patterns into reusable knowledge" (README.md:26, 34) |
| R3 | What the code does | FastAPI `clm-serve`, a client and an in-process `Engine`: texts go to an external `/v1/embeddings` server (vLLM Qwen3-8B), two MLP heads project them, a softmax over scaled cosines is the answer (engine.py:103-136; embedder.py:40-57; heads.py:41-65); fine-tune and best-of-N eval scripts | CLI `beacon`, hook binary `beacon-hooks` and collector `beacon-otelcol` write one normalized JSONL log; offline rule scan, dashboard, MCP server, memory loop (§3) |
| R4 | License | Apache-2.0. `LICENSE` sha256 `cfc7749b…d30` is byte-identical to `/usr/share/common-licenses/Apache-2.0` (appendix placeholder unfilled, LICENSE:190); pyproject.toml:11. Weights "Apache 2.0 on Hugging Face" (README.md:333): CLAIMED-ONLY, not checked | MIT, "Copyright (c) 2026 Asymptote Labs" (LICENSE:1-3); README.md:371 |
| R5 | Languages, size | 25 .py (5,772 lines), 1 .js (925), 1 .css, 1 .html, 2 .sh, 4 .png (859 KB); 45 files | 726 .go (188,588 lines: 394 non-test, 332 test), 66 .ts, 232 .mdx, 55 .sh, 100 .yaml, 92 .png (25 MB), 1 .zip (16.3 MB); 1,500 files |
| R6 | Tests | None (`find` for tests, conftest, tox, Makefile: nothing) | 332 Go test files, 2,960 Test/Fuzz/Benchmark funcs; TS unit and Playwright tests; rule conformance (§3.6); live harness `beacon-sandbox` (17 scenarios, Claude Code only, no committed outputs) |
| R7 | CI | None (no `.github/`) | ci.yml on push and PR (ci.yml:3-5): `go test` for 4 modules, macOS and Linux, `-race` on internal/endpoint (188-245, 357-387), sandbox vet+test (267-287), TS jobs; no Go linter or vuln scanner; status at HEAD UNKNOWN |
| R8 | Dependencies | Lower bounds only, no lockfile (pyproject.toml:23-35: numpy, requests; torch>=2.1, fastapi, uvicorn, huggingface_hub, vllm>=0.6); requirements.txt:4-5 `-e .[serve,vllm]` + httpx; train/requirements.txt:1-5 | go.mod + go.sum in 5 modules (go 1.25.0): cobra, bubbletea, lipgloss, go-toml, yaml.v3, modernc sqlite, cel-go, OTel collector v0.121.0, zap, modal-client/go; beacon-hooks needs cobra only |
| R9 | Entry points | `clm-serve`, `clm-download` (pyproject.toml:37-39); `CLMClient`, `Engine`, `Noul/Choice/Score` (src/clm/__init__.py:15-35); HTTP `/v1/systemone`, `/v1/rank`, `/v1/models`, `/health`, `/` (server.py:82-162) | `beacon` (endpoint, traces, scan, rules, memory, mcp, cloud, ci, version); `beacon-hooks --platform <p> <event>`; GitHub Action (action.yml:1-2); browser extension; `@asymptote/sdk` |
| R10 | Configuration | Env: CLM_PORT, CLM_EMB_URL, CLM_EMB_MODEL, CLM_EMB_MAX_TOKENS, CLM_CKPT, CLM_CKPT_DIR, CLM_DEVICE, CLM_ACTION_CACHE, CLM_API_KEY, CLM_BASE_URL (server.py:170-208; heads.py:25, 31, 158; engine.py:39-40, 63; client.py:145-146). Examples: TYPESAFE_API_KEY or JEV_API_KEY, TYPESAFE_BASE_URL, TYPESAFE_MODEL, CLM_MODEL, and a `<repo>/.env` loader (examples/common.py:40-58) | 72 distinct quoted `BEACON_*` strings in non-test Go (two are prefixes). Files `~/.beacon/endpoint/config.json`, `otelcol.yaml`, `install-manifest.json`; MDM `managed.json` (selfupdate/mode.go:30-34) |
| R11 | Data collected | State and candidate texts; in-memory embedding LRU (embedder.py:59-80) and device arena (cache.py:83-105); no persistent server log; examples keep an sqlite answer cache (examples/common.py:120-124) | Prompts, responses, reasoning, tool I/O, commands, file diffs, approvals, MCP, tokens; hostname, OS, user name/uid, working dir, git repo/branch (§3.2) |
| R12 | Egress | §2.5 | §3.4 |
| R13 | Credentials read | CLM_API_KEY (server.py:208; client.py:146); TYPESAFE_API_KEY/JEV_API_KEY and `<repo>/.env` (examples/common.py:49-58, 110-112); HF token implicitly (heads.py:141-142; hf_embeddings.py:170-173) | TYPESAFE_API_KEY/BEACON_JEV_API_KEY (cmd/memory.go:213); AWS_* keys, BEACON_CLOUD_GCS_CREDENTIALS_B64, BEACON_CLOUD_DEVICE_KEY (cloudshuttle/shuttle.go:104-116); a 0600 device-key file (asymptote/asymptote.go:1-9); HEC tokens; ANTHROPIC_API_KEY (beacon-sandbox) |
| R14 | Files written | `~/.cache/clm/CLM_v0.1-8B.pt` (heads.py:25, 133-153); `<clone>/../logs/vllm_demo_8b.log`, OUTSIDE the clone (serve_qwen3_8b.sh:13-14, 25); `examples/t_rex/results/<tag>.json` over the committed results by default (run.py:133) | Harness configs (`~/.claude/settings.json`, `~/.hermes/config.yaml`, `~/.codex/config.toml`, ...); `~/.beacon/endpoint/` (log, memory.db, rules); `<project>/.agents/skills/`; service units (§3.1, §3.2, §3.5) |
| R15 | Shell, subprocess | None in `src/clm/`; `exec vllm serve` (serve_qwen3_8b.sh:16); curl or hf CLI (download_head.sh:20-27) | sudo, systemctl, launchctl, loginctl, dscl, icacls, rundll32, xdg-open, open, docker, ngrok, `/bin/sh -c`, sw_vers, stat, plus 14 variable-program sites (grep count); the policy provider exec (internal/policy/policy.go:73) |
| R16 | Tree hazards | No symlinks, no submodules, 2 executable files, no LFS | No symlinks or submodules, 57 executable files, a committed and unreferenced Mach-O binary in `cli/beacon/beacon.zip` (§3.5) |

## 2. CLM

### 2.1 What the model is

| # | Dimension | Evidence | Status |
|---|---|---|---|
| C1 | Architecture | Dual encoder. A frozen LLM (Qwen3-8B, last-token pooling, vLLM `--runner pooling`) makes a 4096-d L2-normalized embedding of the state text and of each candidate text. A state head and an action head (MLP 4096 -> width -> ... -> 512, GELU, optional LayerNorm or residual) project them to 512-d. Score = exp(logit_scale) x cosine, capped at 100 (heads.py:1-11, 21-22, 41-65, 95; embedder.py:1-8; README.md:204-206, 213-219) | SOLID (code) |
| C2 | Parameter count | "CLM-8B" is the frozen 8B encoder plus the heads. README.md:204: "Each encoder is a frozen LLM backbone plus a 20M-parameter trainable projection head". The code defaults (width 1536, depth 3, LayerNorm; finetune.py:259-263, bon_eval.py:33-36) give 9,443,840 per head and 18,887,681 for the pair plus the scale, 75.55 MB in fp32 (DERIVED, §2.3). That matches README.md:59 "75 MB" for the PAIR. The released checkpoint's `cfg` is on HF and was not read | UNSURE |
| C3 | Context length | Served: texts truncated at 2048 tokens (`truncate_prompt_tokens`, embedder.py:42-43; server.py:173; vLLM `--max-model-len 2048`, README.md:57, serve_qwen3_8b.sh:12). Training: 8192 for agentic traces (finetune.py:723), 2048 for typed choice (finetune.py:733); states keep their TAIL (embed_utils.py:4-7, 43-49). On the served path vLLM decides which end is kept; the repo does not say | numbers SOLID; served truncation end UNSURE |
| C4 | Training objective | Bidirectional in-batch InfoNCE, same-group codes masked, logit_scale starts at log(1/0.07) (finetune.py:174-183, 289; README.md:223-230). Hard-negative mid-training (README.md:232-238): no code in the repo. Choice task: InfoNCE over the batch's distinct option texts or a per-question softmax, soft or hard targets (finetune.py:10-14) | code SOLID; pre- and mid-training CLAIMED-ONLY |
| C5 | Where the weights live | Not in git (no LFS; `.gitignore:4-7` ignores `*.pt`). HF `Contrastive-LM/CLM-v0.1-8B`, file `CLM_v0.1-8B.pt`, "~75 MB" (README.md:59, 295-297; heads.py:23-24), from `resolve/main`, no revision pin, no checksum (heads.py:142, 145; download_head.sh:20-26). Encoder `Qwen/Qwen3-8B` via vLLM (README.md:56). Other HF ids: `Contrastive-LM/deepswe-clm-embeddings-8k`, `-train-embeddings-8k` (hf_embeddings.py:33-34), `Contrastive-LM/deepswe-clm-heads-8k` (README.md:166), `LocalLLaMA/typed-decisions` (README.md:178). None checked (no network) | UNSURE |
| C6 | Inference needs | "Linux and an NVIDIA GPU" (README.md:46); encoder with `--gpu-memory-utilization 0.35` (README.md:57; serve_qwen3_8b.sh:11); figures "on one RTX 4090" (README.md:123, 463), agentic latency "on an H100" (README.md:153). Heads run on the CPU without a GPU (README.md:431; heads.py:28-38); CPU arena 2% of 8 GiB (cache.py:27, 91-101). No CPU path for the 8B encoder in the repo. Any OpenAI-compatible `/v1/embeddings` URL is accepted (embedder.py:28-45), but "a head only makes sense with the encoder and pooling it was trained against" (README.md:301-302). DERIVED: 0.35 x 24 GiB = 8.4 GiB; Qwen3-8B weight size not in the repo (UNKNOWN) | UNSURE |
| C7 | Published evaluations | §2.2 | |
| C8 | Scoring / classification head | No fixed-label classifier head. Every question is a softmax over candidates the caller supplies: `noul` (default texts "Yes. This is true: ..." / "No. This is false: ...", schema.py:93-101), `choice` (option dict), `score` (ordered levels, answer = expected index) (schema.py:75-145); `confidence` = top minus the mean of the rest (schema.py:122-128). `rank` over free-form strings (engine.py:138-149; server.py:121-153). `clm-raw` = cosine in the encoder space with no head (engine.py:120-124). Wire format = TypeSafe `POST /v1/systemone` (schema.py:3-5; server.py:15-16; client.py:1 "shaped like typesafe_sdk") | SOLID |

### 2.2 Published evaluations

| Claim | Source | Setup | Numbers | Reproducible from the repo? | Class |
|---|---|---|---|---|---|
| T-Rex, zero-shot | README.md:138-142; assets/zero-shot.png; examples/t_rex | 5 seeds x 60 s real time, shield on, prompt `labeled` (examples/t_rex/README.md:8-31) | Both 5/5 survived. Client p50 16.5 ms (CLM) vs 149.8 ms (Jev), model p50 2.6 vs 131.9 ms. Agreement with the planner's best move 0.658 vs 0.987. Shield interventions 4,883 of 16,709 CLM decisions (29.2%) vs 28 of 5,595 (0.5%). Answers discarded 1,250 vs 2,926 (clm_realtime.json:2-22; jev_realtime.json:2-22) | Script (run.py) and committed outputs; a re-run needs a GPU encoder and a TypeSafe key | MEASURED-IN-REPO (outputs; not re-run) |
| T-Rex task shape | backends.py:35-48 | Prompt `labeled` writes the planner's verdict into each option ("Safe. ... Best." / "Unsafe. ... Collision."); "The model reads those labels" (t_rex/README.md:13-14); survival "measures the combined system" (:19-21) | | | SOLID |
| BFCL v4 tool calling | assets/zero-shot.png | not described | 95.2% vs 99.2%; 76.8 vs 125.5 ms | No code or data in the repo | CLAIMED-ONLY |
| WikiRacing | zero-shot.png; README.md:139-141 | not described | 26/30 vs 30/30; 79.8 vs 225 ms | No | CLAIMED-ONLY |
| Super Mario | zero-shot.png | not described | 5/5 vs 5/5; 33.5 vs 132.6 ms | No | CLAIMED-ONLY |
| DeepSWE verifier | README.md:150-156, 164-169; assets/agentic.png | 38 held-out tasks, best of 4, candidates from Opus 5; head fine-tuned, task-disjoint | 81.6% (31/38) vs Jev 71.1%; pass@1 73.7%; 79 vs 449 ms (H100) | A command is given, but it needs HF embeddings and heads (not in the repo). `bon_eval.py` has no expected-result constants (bon_eval.py:6-9). No committed output | CLAIMED-ONLY (a reproduction path exists; it depends on external artifacts) |
| Terminal-Bench 2.1 verifier | README.md:150-156; agentic.png | 30 held-out tasks, best of 5, candidates from Fable 5 | 87.6% vs 83.1%; pass@1 84.0%; 32 vs 131 ms; the y-axis starts at 80% | No command in the README; no data | CLAIMED-ONLY |
| Training data, scaling laws, hard-negative top-1 | README.md:25-27, 240-293 | ~60M Nemotron DQA, ~30M Gemini hard negatives, ~1M agent traces | 52.1 / 69.2 / 62.4% | No code (README.md:369-372: research repo) | CLAIMED-ONLY |
| Vector-cache speed-up | README.md:462-471 | RTX 4090, server p50 | 28.6 -> 28.0 ms new state; 1.7 -> 0.6 ms revisited | No benchmark script | CLAIMED-ONLY |
| Typed-decision accuracy | README.md:177-179 | `LocalLLaMA/typed-decisions` | None published. The trainer prints val, test, zero-shot and majority accuracy (finetune.py:634-639) | Script only | no claim |

### 2.3 Pasted arithmetic (DERIVED)

```
train/eval default: width1536 depth3 LN: per_head=9,443,840 pair+scale=18,887,681 fp32_bytes=75,550,724 (75.55 MB, 72.05 MiB)
alt: width2048 depth2 noLN: per_head=9,439,744 pair+scale=18,879,489 fp32_bytes=75,517,956 (75.52 MB, 72.02 MiB)
T-Rex ratios: jev/clm client p50 = 9.08 | model p50 = 50.7
shield share: clm 0.2922 jev 0.005
zero-shot latency ratios: {'trex': 9.08, 'bfcl': 1.63, 'wiki': 2.82, 'mario': 3.96}
agentic ratios: deepswe 5.68 tb2.1 4.09
deepswe 81.6% of 38 = 31.01 | tb2.1 87.6% of 30 = 26.28 | pass@1 tb 84.0% of 30 = 25.2
0.35 x 24 GiB = 8.4 GiB
```

### 2.4 README against code (CLM); both sides kept

| # | README says | Code or data says | Status |
|---|---|---|---|
| D1 | `Engine(emb_url=...)  # reference head, downloaded if missing` (README.md:100) | `Engine` never downloads: it uses `default_checkpoint()` (engine.py:43-45), which returns None when the file is absent (heads.py:156-162). Only `clm-serve` downloads (server.py:193-195). With no file, `Engine` serves only `clm-raw`, and `rank()` defaults to `clm-latest` -> `ModelNotFound` (engine.py:110-115, 138-139) | SOLID |
| D2 | Fine-tuning guide (README.md:160-162; link text "Fine-Tuning Tutorial", README.md:17) | `docs/FINETUNING.md` is an autonomous agent-loop prompt: "an experiment to have the LLM autonomously improve CLM fine-tuning" (:3), "LOOP FOREVER ... do not ask whether to continue" (:73-89) | SOLID |
| D3 | "performs on par with Jev ... with up to 9x lower latency" (README.md:28-29) | Figure: lower success on BFCL (95.2 vs 99.2%) and WikiRacing (26/30 vs 30/30). The 9x is T-Rex only; the other latency ratios are 1.63-3.96x (§2.3). Committed T-Rex agreement 0.658 vs 0.987 | SOLID (figures read) |
| D4 | "Each encoder is ... plus a 20M-parameter trainable projection head" (README.md:204) | Code defaults give 9.44M per head, 18.89M for the pair (§2.3); "75 MB" (README.md:59) fits the pair in fp32 | UNSURE (released cfg not seen) |
| D5 | Env equivalents CLM_PORT, CLM_EMB_URL, CLM_EMB_MODEL, CLM_CKPT, CLM_DEVICE, CLM_ACTION_CACHE (README.md:432-435) | Code also reads CLM_EMB_MAX_TOKENS (server.py:173) and CLM_CKPT_DIR (heads.py:25) | SOLID |
| D6 | Scripts named in help and docstrings: `embed_shard.py`, `merge_embeddings.py` (bon_eval.py:134; finetune.py:17), `download_trials.py` (bon_eval.py:144) | None of the three is in the 45-file tree | SOLID |
| D7 | Diagram: "clm-serve (CPU, :8700)" (README.md:214) | `default_device()` picks cuda when torch sees a GPU (heads.py:28-38); README.md:431 says the same | SOLID |

### 2.5 CLM network egress and listeners

| Destination | When | Evidence |
|---|---|---|
| huggingface.co, `Contrastive-LM/CLM-v0.1-8B` via `resolve/main` | `clm-serve` without `--ckpt` or `--no-download`; `clm-download`; download_head.sh | server.py:185, 193-195; heads.py:133-153; download_head.sh:20-26 |
| huggingface.co datasets and models | `bon_eval --hf-dataset`; `finetune --hf-dataset/--data`; `hf_embeddings download`; `push` (upload, `--push` only) | bon_eval.py:162-165; finetune.py:409-411; hf_embeddings.py:44-54, 168-174 |
| huggingface.co `Qwen/Qwen3-8B`, with `trust_remote_code=True` | vLLM serve; the training tokenizer and offline vLLM | README.md:56; embed_utils.py:27, 63-65 |
| Embedder URL, default `http://127.0.0.1:8090/v1/embeddings` | every cache miss; every `GET /health` | embedder.py:29, 45, 84 |
| api.typesafe.ai, Bearer TYPESAFE_API_KEY | examples only (`run.py --model jev`) | examples/common.py:43; examples/t_rex/trex/backends.py:20 |
| Inbound: `0.0.0.0:8700` by default; auth off unless CLM_API_KEY is set; `/health` needs no auth; CORS off by default | always when serving | server.py:169, 208, 78-80, 82-89, 73-76 |
| Browser playground: fetches only the base URL the user types (or the same origin); the API key is kept in `localStorage` key `clm.playground.apiKey`; share links carry only the request, not the key or base URL | when the UI is used | app.js:18-23, 180-189, 786-790, 861-865 |

URL sweep of all files: no analytics host; only HF, TypeSafe, GitHub, doc links, loopback, w3.org SVG namespaces.

### 2.6 CLM security-relevant behavior

| Behavior and evidence | Status |
|---|---|
| `torch.load` with no `weights_only` (heads.py:83); `weights_only=False` explicit in bon_eval.py:31 and finetune.py:256, 495, 630; torch floor `>=2.1` / `>=2.0` (pyproject.toml:30; train/requirements.txt:2). The default's effect depends on the unpinned torch version | code SOLID; effect UNSURE |
| Hot reload: a new mtime on the checkpoint file reloads it (heads.py:97-102); `--ckpt-dir` loads every `*.pt` in the directory (engine.py:46-48) | SOLID |
| Unpinned remote weights: `resolve/main`, no hash (heads.py:142, 145) | SOLID |
| `trust_remote_code=True` for the tokenizer and offline vLLM (embed_utils.py:27, 63-65) | SOLID |
| Server binds `0.0.0.0` by default; the bearer key is compared with `!=` (server.py:169, 79) | SOLID |
| The serve script writes its log outside the clone: `LOGDIR=$(dirname $0)/../logs` (serve_qwen3_8b.sh:13-14, 25) | SOLID |
| Examples export every `KEY=VALUE` line of `<repo>/.env` into `os.environ` (examples/common.py:49-58) | SOLID |
| Mock tool: a fake n-gram encoder; the server reports `mock: true`; the UI shows a banner; binds 127.0.0.1 (tools/playground_mock.py:1-16, 118; server.py:87-88; app.js:222) | SOLID |
| Classifier "Private :: Do Not Upload" blocks a PyPI upload (pyproject.toml:16) | SOLID |

## 3. agent-beacon

### 3.1 How it attaches to each harness

| Harness | Mechanism | Evidence | Status |
|---|---|---|---|
| Claude Code, hooks | Ten events: SessionStart, UserPromptSubmit (30 s), PreToolUse (Bash, Edit, Write, MultiEdit, Read, Glob, Grep, WebFetch, WebSearch, Agent, `mcp__.*`), PostToolUse, PostToolUseFailure, Stop (45 s), SubagentStart, SubagentStop, PermissionRequest, SessionEnd; each runs `'<bin>' --platform claude --log ... --config ... <event>`. Target `~/.claude/settings.json` (default) or `./.claude/settings.json`. Keeps other hooks and unmodelled fields; rewrites the file with `json.MarshalIndent` + `os.WriteFile(0600)` | hooks/claude.go:63-104; settings_hooks.go:10-17, 174-205, 240-252; runtime.go:35-66, 149-174 | file edit MEASURED-IN-REPO (6 tests, claude_test.go:11-131); live harness exists, no committed outputs |
| Claude Code, OTel | Writes into `env`: CLAUDE_CODE_ENABLE_TELEMETRY=1, OTEL_LOGS_EXPORTER=otlp, OTEL_METRICS_EXPORTER=otlp, delta temporality, protocol grpc, OTEL_EXPORTER_OTLP_ENDPOINT=<local collector>, OTEL_LOG_TOOL_DETAILS=1, OTEL_LOG_USER_PROMPTS=1. Backup first; a JSON parse error is discarded (`_ = json.Unmarshal`) | harness/harness.go:359-397 (367, 368, 376-387) | code SOLID |
| Claude Code, poll | `beacon endpoint claude sync` reads `~/.claude/projects/*.jsonl`: prompts, tool results, assistant text, thinking blocks, tool_use, usage, summaries; marked `collection_method=poll`; cannot deny | cmd/endpoint_claude.go:17-27; claudesession/mapper.go:68-248 | SOLID |
| Claude Code on the web | `beacon cloud claude-web print-setup` script: curl a GitHub release tarball (no checksum step); take the first `.git` 2-3 levels under `/home/user`; overwrite `$REPO/.claude/settings.local.json`; append to `.git/info/exclude`; log `/tmp/beacon/runtime.jsonl`; upload to GCS/S3 if configured | cmd/cloud.go:40-72, 225-261; cloudshuttle/shuttle.go:89-145 | code SOLID; live UNKNOWN |
| Hermes Agent, hooks | Nine events in `~/.hermes/config.yaml`: on_session_start, pre_llm_call (30 s), pre_tool_call (`.*`, 10 s), post_tool_call, pre_approval_request, post_approval_response, subagent_stop, on_session_end, on_session_finalize; project level refused | hooks/hermes.go:76-97, 222-229 | YAML edit MEASURED-IN-REPO (5 tests, hermes_test.go:11-155); the code says "Hermes is not a runtime this repository can exercise" (hermes.go:106-109): live behavior CLAIMED-ONLY |
| Hermes Agent, poll | `beacon endpoint hermes sync` reads `~/.hermes/state.db` read-only (`mode=ro`, `busy_timeout(1000)`), tables `sessions`, `messages`; `--db` overrides | cmd/endpoint_hermes.go:16-28, 61; hermessession/collect.go:114, 344, 391, 429, 435-446 | code SOLID |
| Codex CLI | OTel block in `~/.codex/config.toml` with prompt logging, plus hooks | harness/harness.go:399-417 | code SOLID |
| Cursor (cloud) | `.cursor/hooks.json` command hooks call `/tmp/beacon/bin/beacon-hooks`; the repo uses this on itself | .cursor/hooks.json; cmd/cloud.go:264-285 | SOLID |
| Browsers | MV3 extension; permissions storage, alarms, scripting; hosts claude.ai, chatgpt.com, chat.openai.com, 127.0.0.1, localhost; posts to the local OTLP receiver | browser-extension/src/manifest.json | SOLID |
| Coverage table | 29 local runtimes (README.md:240-268), 2 browser sites, 4 cloud rows, 4 SDK surfaces. Hook installer files exist for 22 platforms (`hooks/*.go`). A live harness exists for Claude Code only (beacon-sandbox launches no other agent CLI; grep) | README.md:238-293 | most rows CLAIMED-ONLY at the live level |

### 3.2 Data model, storage, UI

| Item | Evidence |
|---|---|
| One JSON object per line. `vendor` "beacon", `product` "endpoint-agent", `schema_version` "1.0". Nested: event{kind, action, category, fidelity}, severity, endpoint{hostname, os, agent_version}, user{name, uid}, harness{name, version, executable_path, config_path, collection_method}, origin, run, session{id, working_directory}, trace, tool, file, command, mcp, approval, policy, prompt, content, destination, gen_ai, model, repository, branch, raw | pkg/asymptoteobserve/event.go:11-13, 65-90, 444-493 |
| Provenance: `collection_method` hook, plugin, otlp or poll; `event.fidelity` observed or inferred | docs/telemetry-schema/event-schema.mdx:39-51 |
| Log: `~/.beacon/endpoint/logs/runtime.jsonl` (user mode); rotation 10 MiB x 5 archives | cli/beacon-hooks/internal/logging/logging.go:521-528; SECURITY.md:20; cmd/endpoint_claude.go:34-39 |
| Memory store: SQLite `memory.db` beside the logs directory; tables evaluations, candidates, memories | learning/store.go:20, 50-59, 72, 104, 117, 131 |
| Redaction: four regexes (bearer; key/token/secret/password assignments; `sk-` + 20+ chars) plus repeats of assigned values; truncation (4096, raw 2048) runs BEFORE redaction; on in hooks and exporter | privacy.go:9-21, 28-72; logging.go:535-547; beaconjsonexporter/config.go:28 |
| UI: TUI `beacon traces`; dashboard `127.0.0.1:8765`, 15 `/api/*` read routes, no POST/PUT/DELETE found | README.md:111-119; dashboard/server.go:22, 92-311 |
| MCP server: stdio, or HTTP on `127.0.0.1:8766` (loopback enforced). Seven tools: search_activity, summarize_activity, get_activity_event, list_activity_filters, search_memory, get_memory, get_memory_context | cmd/mcp.go:21, 58-59, 73; internal/mcpserver/server.go:267-359 |
| Collector: OCB v0.121.0; otlpreceiver on 127.0.0.1:4317 (gRPC) and 4318 (HTTP); batch and memory_limiter; exporters beaconjson, falcon HEC, splunk HEC; health check. It has NO OTLP exporter (the builder list and a grep of the config generator both show none) | collector-builder/builder.yaml:1-22; endpoint/config/config.go:24-25; endpoint/collector/collector.go:155-157, 177 |

### 3.3 Memory loop and its Jev use

| Step | Evidence |
|---|---|
| `beacon memory evaluations run` is explicit: "hooks and collectors do not call Jev"; a dry run makes no request | learning/evaluator.go:170-180; docs/security/data-inventory.mdx:87-90 |
| Default endpoint `https://api.typesafe.ai/v1/systemone`, model `jev-latest`; overrides `--jev-endpoint` / BEACON_JEV_ENDPOINT; key `--jev-api-key`, then TYPESAFE_API_KEY, then BEACON_JEV_API_KEY; timeout 10 s; cost default $0.00035 per trace | evaluator.go:18-22, 270-273; cmd/memory.go:194-198, 212-215 |
| Request `{model, state: {trace: <projection>, rubric_version, rubric_hash}, questions}`: three `noul` questions (task_success, reusable_correction, evidence_supported) with true/false criteria; Bearer auth | evaluator.go:31-35, 276-295, 344-357 |
| What leaves the host: at most 80 events (the first 40 and the last 40), each title, summary and content redacted and cut to 1200 chars; the repository remote URL or path; harness; trace title | evaluator.go:23-24, 182-227, 439-446 |
| Output: noul probabilities, no rationale ("TypeSafe Noul answers contain probabilities, not rationale"). Candidates -> a human approves, rejects or supersedes them with a reason -> `skills install` writes `<project>/.agents/skills/<slug>/SKILL.md` (mode 0644) | learning/candidate.go:172-175; docs/cli/memory.mdx:8-121; learning/skills.go:84-96 |

### 3.4 agent-beacon network egress and listeners

| Destination | Trigger | Data | Evidence |
|---|---|---|---|
| None (local JSONL) | default | | README.md:115; SECURITY.md:11-18 |
| beacon.sh (login, dashboard auth; BEACON_AUTH_URL, BEACON_DASHBOARD_URL) | interactive endpoint setup, login | account auth | account/login.go:21-27; auth/dashboard.go:23-25; README.md:48-52 |
| `auth.asymptotelabs.ai/functions/v1/beacon-signup` (BEACON_SIGNUP_ENDPOINT) | onboarding wizard (user mode, TTY, not CI, not root); BEACON_ONBOARDING=0 skips it | install id, email, usage, OS/arch/version, install mode, detected runtimes | onboarding/submit.go:17-57, 87-115; cmd/endpoint_onboarding.go:21-37, 366-394 |
| Beacon Managed ingest (URL from enrollment): `/v1/ingest/runtime`, `/v1/ingest/inventory` via Vector, bearer device key | user confirms Managed (preselected) or runs `endpoint connect`; BEACON_MANAGED_INGEST=0 hides it; privacy `standard` (default) or `metadata_only` | runtime JSONL, inventory | asymptote/asymptote.go:1-9, 33-48; asymptote/enroll.go:16-22, 51-60; managedprivacy/privacy.go:8-22 |
| api.typesafe.ai | `beacon memory evaluations run` | trace projection (§3.3) | learning/evaluator.go:20 |
| GCS (oauth2 and storage.googleapis.com) or S3 | cloud mode with a bucket and credentials set | runtime JSONL | cloudshuttle/shuttle.go:35-36, 89-145, 316, 460 |
| Splunk HEC, Falcon LogScale HEC | configured at install | events | collector-builder/builder.yaml:14-19; packaging/linux/install-endpoint.sh:23-29, 47-53 |
| Vector packs (CloudWatch, Datadog, Elastic, Sentinel, Sumo Logic, Wazuh, Rapid7, S3, GCS) | customer configured | JSONL | README.md:303-320 |
| github.com, api.github.com | `beacon version check`; self-update (default off; precedence env, managed.json, local); cloud setup downloads | manifest (sha256 per artifact), binaries | updatecheck/source.go:10; manifest.go:17-31; selfupdate/mode.go:13-28, 71-93; cmd/version_check.go:18-23 |
| api.devin.ai | Devin cloud poll | Devin sessions | devincloud/client.go:23 |
| ngrok public tunnel to the local OTLP HTTP receiver; basic auth `user:password` passed in ngrok argv | only `beacon endpoint cowork ... --ngrok` | inbound Cowork OTLP | cmd/endpoint_cowork.go:40, 52, 173-177 |
| Modal (with ANTHROPIC_API_KEY) | dev harness `beacon-sandbox` | scenario runs | beacon-sandbox/go.mod; .claude/skills/self-verify-beacon-in-sandbox/SKILL.md |
| Listeners 127.0.0.1: 4317/4318 collector, 8765 dashboard, 8766 MCP HTTP; health 13133 | when run | | config.go:24-25, 219; dashboard/server.go:22; cmd/mcp.go:21 |

### 3.5 agent-beacon security-relevant behavior

| Behavior | Evidence | Status |
|---|---|---|
| The policy seam fails OPEN by design. It runs only when BEACON_POLICY_PROVIDER names an executable; timeout 2 s; any error, timeout, non-zero exit or malformed output means allow; "the open Beacon build never blocks a tool call by default" | internal/policy/policy.go:1-9, 25-31, 45-88; cmd/policy.go:71-100 | SOLID; MEASURED-IN-REPO (policy_test.go:40, 70, 82) |
| PermissionRequest hook: Claude and Hermes get `{}` (observe only); `devin` and `devin-cli` get `{"decision":"approve"}`, also when the input does not parse | cli/beacon-hooks/cmd/permission_request.go:22-66; cmd/helpers.go:43, 63-65 | SOLID |
| Detection is offline. The rule engine is imported only by cmd/rules.go, cmd/scan.go, endpoint/dashboard/detections.go and endpoint/detect/detect.go; the hook binary and the collector do not import it | grep of `asymptoteobserve/threatrules"` importers | SOLID |
| Unreferenced committed binary: `cli/beacon/beacon.zip` (16,293,651 B, sha256 `3d98b12c…5ccf`) holds `beacon/beacon`, 35,712,304 B, Mach-O 64-bit arm64, dated 2026-06-18, plus a macOS `._beacon`; `git grep beacon.zip` finds no reference. The CLI embeds `hooks.bin`, built from source at release, gitignored | zipfile catalogue (this session); embedded/embed.go:11, 23; .gitignore:22; .goreleaser.yaml:65; release.yml:163 | SOLID |
| Root postinstall: `endpoint install --system --harness claude,codex` on 4317/4318, then the installing user's (SUDO_USER or logind) Claude Code and Codex settings, then the updater and the inventory schedule ("on by default") | packaging/linux/install-endpoint.sh:17-19, 37-40; nfpm/postinstall.sh:12-40 | SOLID |
| `sudo` exec in `endpoint connect`; `docker` for the Elastic pack; `/bin/sh -c` for the updater reload | cmd/endpoint_connect.go:261; cmd/endpoint_elastic.go:90; endpoint/service/updater.go:64 | SOLID |
| The cloud setup scripts download and unpack a release tarball with no checksum check | cmd/cloud.go:233-237; .cursor/install.sh (install_from_release) | SOLID |
| Settings writes are not atomic (`os.WriteFile` truncates and writes) | hooks/settings_hooks.go:204; harness/harness.go:396 | SOLID |
| Redaction order: truncate, then redact; the `sk-` rule needs 20 or more chars after the prefix | privacy.go:18, 66-72 | facts SOLID; effect not tested |

### 3.6 Detection rules

- 75 YAML rules in 10 folders: risky-command 13, context-exfiltration 12, sensitive-edit 11, prompt-injection 10,
  credential-access 9, external-access 5, source-control 5, agent-control 4, approval-abuse 3, resource-consumption 3.
- All are `posture: detect`. Status: 56 stable, 19 experimental. Severity: 7 critical, 51 high, 16 medium, 1 low.
  Fixtures: 286 `match`, 223 `no_match`; every rule has at least one `no_match` (grep counts, this session).
- Format: CEL over the Beacon event, with session-scoped correlation windows (for example 300 s,
  rules/approval-abuse/approval-denied-command-executed-anyway.rule.yaml:22-33); OWASP LLM and MITRE ATLAS tags.
- spec/threat-rules/SPEC.md:8-10: "the rule format and corpus are open; an evaluation engine that consumes them may be
  separate (and closed)".
- MEASURED-IN-REPO: `TestPackConformance` runs every fixture (pkg/asymptoteobserve/threatrules/conformance_test.go:36-66),
  with meta-tests that a bogus field or a fixture mismatch fails (conformance_meta_test.go:13-31); CI runs them (ci.yml:242-243).
- CLAIMED-ONLY (a comment): before v1.0.6, Claude Code commands made no `command.executed` event, which "silently
  disabled every rules/risky-command/ rule for Claude Code" (beacon-sandbox/scenarios/s02-bash-command.yaml:5-9).

### 3.7 README and docs against code (agent-beacon); both sides kept

| # | Doc says | Code or other doc says |
|---|---|---|
| B-D1 | Hermes Agent "Hooks + poll", all main columns ticked (README.md:256) | "Hermes is not a runtime this repository can exercise" (hooks/hermes.go:106-109); docs/security/data-inventory.mdx has 0 mentions of Hermes |
| B-D2 | "Forwarding: Optional and customer configured" (SECURITY.md:17) | Interactive setup "preselects Beacon Managed, with an explicit Local opt-out"; forwarding starts after the user confirms (README.md:48-52, 128-132) |
| B-D3 | "a common OpenTelemetry-based event model" (README.md:201) | The stored record is Beacon's own JSON schema (event.go:444-493), fed by OTLP, hooks, plugins and polls; the collector exports no OTLP (builder.yaml) |
| B-D4 | "local, read-only dashboard" (README.md:220) | Consistent: no mutating route found (dashboard/server.go:92-311) |

## 4. Overlap with our system (facts from both sides; no verdict)

Last commits of our cited files (`git log -1`): CLAUDE.md a12e672 09-24; OBSERVABILITY-RUNBOOK b3ef7da 09-03; JEV-LAYA-AUDIT
2eaf06e 09-22; MOJEV-AUDIT 817509b 09-24; CANNY-AUDIT 6a6cd4a 09-23; LAYA-PROBE-1 8804c26 09-24; laya_systemone_server.py and
jev-pruner-setup.sh 6406750 09-23; COUNCIL-VERDICT-JEV-LAYA ec50851 09-22; .claude/settings.json 9924dd2 09-24; hooks:
edit-snapshot de06db6 09-24, graft-first-nag d201f8a 09-15, turn-retro-gate 1e8ecee 09-03, session-start and wiki-context 3c0d49e 09-02.

| # | Our side | CLM / agent-beacon side | Overlap or difference (fact) |
|---|---|---|---|
| O1 | Jev = "TypeSafe's hosted System One model" (JEV-LAYA-AUDIT-2026-09-22.md:12-14) | CLM: "TypeSafe's hosted Jev (`jev-latest`)", answered as `jev-1.13.0`, at `https://api.typesafe.ai` (examples/t_rex/README.md:3, 34; examples/common.py:43). Beacon: the same URL and `jev-latest` (evaluator.go:20-21) | The same host string appears in all three |
| O2 | Laya `/v1/systemone` on port 47411 (scripts/laya_systemone_server.py:206; harness-ports/bin/jev-pruner-setup.sh:9); MoJev on the TypeSafe `system_one` shape (MOJEV-AUDIT-2026-09-24.md:31) | CLM `POST /v1/systemone`, `noul`/`choice`/`score` (server.py:96; schema.py:23). Beacon posts `noul` questions to a configurable endpoint (evaluator.go:28; cmd/memory.go:194, 212) | Same route and question types. Beacon's `state` is a nested object (evaluator.go:278-282); CLM renders objects as `key: value` prose (schema.py:27-59). Compatibility NOT tested |
| O3 | Laya: ModernBERT-large 421M, 512 tokens (typed-decisions 1024), CPU, PC p50 336.18 ms at 4 threads, deterministic (JEV-LAYA-AUDIT-2026-09-22.md:14-16; LAYA-PROBE-1.md:70-71). MoJev: Qwen3.5-0.8B, 854,036,544 params, 16,384-token state (MOJEV-AUDIT-2026-09-24.md:32-34) | CLM: frozen 8B encoder on a GPU + about 18.9M head params (DERIVED); 2048 tokens served, 8192 in agentic training (§2.1) | Sizes, windows and venues differ as stated |
| O4 | Laya checkpoint `typed-decisions` of HF `convaiinnovations/laya` (LAYA-PROBE-1.md:6) | CLM `--task choice` trains on HF dataset `LocalLLaMA/typed-decisions` (README.md:178; finetune.py:10) | Same name; identity NOT checked (UNSURE) |
| O5 | — | CLM's T-Rex engine, planner and pilot come from `github.com/virajbhartiya/laya-vs-jev` (Apache-2.0) (examples/t_rex/trex/__init__.py:3-6; examples/t_rex/README.md:10) | That repo was not cloned (no network) |
| O6 | Hosted TypeSafe API and key "are not production dependencies" (JEV-LAYA-AUDIT-2026-09-22.md:163-165); Rule 3, OmniRoute sole egress (CLAUDE.md:213) | CLM examples (common.py:43) and Beacon's explicit evaluator (evaluator.go:20, 170-180) default to api.typesafe.ai | Both overridable (TYPESAFE_BASE_URL; `--jev-endpoint`) |
| O7 | Rule 9: a fail-closed `pre_tool_call` policy hook (CLAUDE.md:219). Canny: deny-capable PreToolUse and Stop decisions (CANNY-AUDIT-2026-09-23.md:9-13) | Beacon's policy seam fails open (internal/policy/policy.go:6-9) and adds its own `pre_tool_call` entry to `~/.hermes/config.yaml` (hooks/hermes.go:85) | Opposite default: our rule is fail-closed; Beacon's seam is fail-open |
| O8 | Five scripts in `.claude/hooks/` on SessionStart, PreToolUse, PostToolUse, UserPromptSubmit, Stop, in `/home/user/agent-factory/.claude/settings.json` and `/home/user/.claude/settings.json`; neither sets `OTEL_*` or CLAUDE_CODE_ENABLE_TELEMETRY (read this session) | User level writes `$HOME/.claude/settings.json`; here `HOME=/root`, and `/root/.claude/settings.json` exists (hooks PostToolUse, PreToolUse, SessionStart, SubagentStart; an `env` block, not printed). Beacon adds ten events incl. Stop (45 s) and UserPromptSubmit (30 s) and sets OTEL_LOG_USER_PROMPTS=1 (hooks/claude.go:63-78; harness/harness.go:376-387) | Beacon's events include Stop and UserPromptSubmit, where our turn-retro gate and wiki-context run; its target file differs from ours |
| O9 | Canny: a hook layer with a per-session JSONL ledger under `~/.canny/sessions/`; a done-gate, pattern denies and advisory Jev checks (CANNY-AUDIT-2026-09-23.md:9-14) | Beacon: hook, OTel and poll capture into `runtime.jsonl`; offline CEL detection; no blocking by default; Jev only in the explicit memory evaluation | Both keep per-session JSONL and both hook Claude Code and Codex; Canny enforces, Beacon observes |
| O10 | PC Phoenix: UI 6006, OTLP gRPC 4317; OpenObserve 5080 OTLP HTTP (docs/OBSERVABILITY-RUNBOOK.md:18-22); our plane "NOT built" (:45) | Beacon collector 127.0.0.1:4317/4318 by default (config.go:24-25; collector.go:155-157), overridable (install-endpoint.sh:18-19); no OTLP exporter (builder.yaml); JSONL out via Vector or HEC | Same default port 4317 on one host |
| O11 | Our lanes keep Hermes sessions per profile, `~/.hermes/profiles/<profile>/state.db` (CLAUDE.md:434 paragraph) | Beacon's Hermes poll defaults to `~/.hermes/state.db` (hermessession/collect.go:114); `--db` overrides it (cmd/endpoint_hermes.go:61). `/root/.hermes` does not exist in this sandbox | Default paths differ |
| O12 | Rule 13: every upstream pinned by commit or digest (CLAUDE.md:223) | CLM fetches its head from `resolve/main` with no revision or hash (heads.py:142, 145). Beacon's Go deps are pinned by go.sum; the committed `beacon.zip` is an unreferenced binary | As stated |
| O13 | Rule 1: Hermes is the sole production runtime (CLAUDE.md:211); KC-J1: no System-One value in a gate predicate (COUNCIL-VERDICT-JEV-LAYA-v1.md:45) | Beacon installs into Claude Code, Codex, Hermes and ~20 more; its Jev output feeds human review only (docs/cli/memory.mdx:99-114). CLM is a scorer service | As stated |

## 5. Gaps and unknown cells

- Not fetched (no network beyond the clones): CLM's released head `cfg` and real parameter count, all HF datasets and heads,
  `virajbhartiya/laya-vs-jev`, agent-beacon CI status at HEAD, per-file agent-beacon dates (shallow clone).
- Not in the repo: Qwen3-8B weight size and GPU memory at the documented flags; which end vLLM keeps under
  `truncate_prompt_tokens`; Beacon Managed's server side; the "separate (and closed)" rule engine (SPEC.md:9).
- Not run (static only): every CLM number; Beacon on Hermes (the repo itself cannot exercise it, hermes.go:106-109).
- Not checked: whether `LocalLLaMA/typed-decisions` is the data behind Laya's `typed-decisions` checkpoint; what the
  `beacon.zip` binary is beyond its header; the 14 variable-program exec sites one by one; whether the Linux postinstall
  installs an updater unit when the mode is off; the contents of agent-beacon's `CLAUDE.md` and `AGENTS.md`.

## 6. Cleanup

```
11:38:06Z rm -rf /home/user/contrastive-lm/clm /home/user/asymptote-labs/agent-beacon (two calls)
avail before 1,646,448,640 B -> after 1,746,264,064 B (+99,815,424 B); ls of both paths: No such file or directory
df -h /home/user: /dev/vda 252G 36G 1.7G 96% /
```
The empty parent directories `/home/user/contrastive-lm` and `/home/user/asymptote-labs` (from my `mkdir -p`) remain,
because the brief allows `rm -rf` of the two clone paths only.
