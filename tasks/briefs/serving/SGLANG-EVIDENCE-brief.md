# SGLANG-EVIDENCE (task #454): SGLang against vLLM for the PC's model server

Role: evidence-gatherer (sandbox, Opus 5.5). PIN: 610cb123 (the origin head at authoring; full id in the premise).
Report: `tasks/briefs/serving/SGLANG-EVIDENCE-report.md` (write it incrementally from the start, one section per question
group, filled as you go: the report file is the deliverable). Do NOT spawn subagents. Read-only everywhere except the
report. No verdict, no recommendation, no fix: evidence tables only (the coordinator writes the verdict).

## WHY

D-127 (the owner, 2026-10-01; the row in `docs/08_DECISION_LOG.md`): "I'm thinking to get rid of [vLLM] ... I found a
recipe for SGLang ... much better suited for our use case ... it can handle more concurrent chats ... Don't take my word
for it though. Go do a bit of research on SGLang and look at it in comparison to [vLLM] for our setup and our agent
factory ... we're budget constrained ... let's switch to SGLang". The owner's reasons, as heard; each is a claim this
lane collects evidence on, for and against:

- **C-1:** SGLang handles more concurrent chats on one 3090.
- **C-2:** when memory runs short, vLLM runs out of memory (OOM), where SGLang evicts the least used cached prefixes.
- **C-3:** SGLang keeps chats in a tree of cached prefixes (RadixAttention), so a chat is not read again in full on
  every turn.
- **C-4:** the recipe's numbers: 135 tok/s decode, 591 tok/s prefill, a 200K context, on an RTX 3090.

After this lane (not this lane's work): the coordinator writes the verdict from the evidence; then an A/B in a GPU test
window (D-088) on this project's load shape, with the same port and served model id; then the switch if the
measurements hold, with the measured trade-off reported to the owner (D-127, D-088).

## THE SETUP (what a switch would replace; the premise block below measures it)

- **The PC:** Fedora 42, one RTX 3090 (24 GiB, Ampere, sm_86), rootless podman 5.7 with the CDI device
  `nvidia.com/gpu=all`, the server run by a systemd --user Quadlet (`deploy/qwen.container`).
- **The server:** the image `ghcr.io/syv-ai/qwen38-27b-rtx3090` (digest-pinned), vLLM 0.28 with the image's patches,
  `Exec=batch`; the model `dbirks/Qwen3.8-27B-W4A16-AutoRound` (4-bit weights); max_model_len 131,072 (D-097, the owner's
  sweet spot for Hermes); fp8 KV; prefix caching on, with `mamba_cache_mode: align`; max_num_seqs 64;
  max_num_batched_tokens 2048; `gpu_memory_utilization` 0.96 (D-099); two served names (`qwen3.8-27b-local`,
  `qwen3.8-27b`); the API key read from a file mounted read-only. KV pool: 215,112 tokens (1.64 requests at 131,072).
  `SPEC=mtp` is set, but the live engine reports `speculative_config=None`: the batch profile runs no speculative
  decoding.
- **The clients** (the switch must keep each working, or name what changes):
  - **OmniRoute** (the PC's model gateway, `:20128`): the Hermes lanes' chat completions, streamed, with tools (the
    `qwen3_coder` parser) and reasoning (the `qwen3` parser). Its local provider entry is built by
    `harness-ports/bin/omniroute_local_builder.py`. OmniRoute ends a request whose first event takes longer than 80 s
    (a 504).
  - **The Qwen Jev adapter** `scripts/qwen_jev.py` (System 1, wired straight to the server, D-082): `POST
    /v1/completions` with a list of token ids as `prompt`, `max_tokens` 1, `temperature` 0, `logprobs` 20. It reads
    `choices[0].logprobs.top_logprobs[0]` as a dict (token to logprob), and refuses a response whose `model` differs
    from the id sent or whose `usage.prompt_tokens` differs from its own token count.
  - **The labeler** `scripts/s1_synth.py`: chat completions with `chat_template_kwargs: {enable_thinking}` and
    temperature 0; it can never send `prompt_logprobs`, `best_of`, `echo` or `n` (AF-AP-201: one `prompt_logprobs`
    request OOM-killed the shared vLLM).
  - **The tools:** `harness-ports/bin/qwen-server.sh` (start, stop, restart-when-idle; it reads `/metrics` to tell idle
    from busy), `harness-ports/bin/qwen_matrix.py` (the load generator; `/metrics` before and after), and
    `scripts/gpu_window.sh` (the GPU test window: it stops the server or reduces its KV, then restores it and checks
    `/v1/models`).
- **The load** (`.claude/skills/pc-bridge-lanes/SKILL.md`, measured): long Hermes lanes send 57k to 90k-token prompts; two
  long lanes fit the KV pool, and a third waits past OmniRoute's 80 s and dies with a 504; today one long lane runs at a
  time, beside short System-1 calls. On this server (`docs/research/findings/VLLM-MIGRATION.md`): about 45 tok/s
  single-request decode in the batch profile, near-linear to about 310 tok/s at 7 concurrent lanes; batch C64 about
  1,035 tok/s aggregate; the image's single-user profile 118 to 133 tok/s (382 with DFlash2, the image doc's
  reproduction).
- **The pin:** `upstream.lock.yaml` holds the image's digest, and that file is an attested input of the signed proofs
  S0-06 and S0-12 (D-110: a change to it voids both attestations; the PC-lane tool pins went to `pc-lane.lock.yaml`).

## THE RECIPE (read by the coordinator at authoring; read it again yourself)

`https://local.sybilsolutions.ai/gpu/rtx-3090-24gb/qwen3.8-27b.sglang.200k/`, with its registry
`https://github.com/0xSero/local-ai-registry` (MIT). The page's launch command, as the coordinator's fetch returned it:

```
docker run --rm \
  --gpus all \
  -p 8000:30000 \
  --shm-size 16g \
  -e CUDA_DEVICE_ORDER=PCI_BUS_ID \
  -e HF_HUB_OFFLINE=1 \
  -e SGLANG_EXL3_EMBED_HOST=1 \
  -e SGLANG_EXL3_KERNEL=auto \
  -e SGLANG_EXL3_MODEL_PATH=/models/turboderp-Qwen3.8-27B-exl3-3.00bpw \
  -v ~/models/Qwen3.8-27B-exl3-6fe61ad6:/models/turboderp-Qwen3.8-27B-exl3-3.00bpw:ro \
  --entrypoint /opt/entrypoint.sh \
  ghcr.io/0xsero/sglang-exl3@sha256:84f75f3424c99a3d63392a4e0348292bdeba9cf7efba2ff1aa9b85c8fc0131e8 \
  python3 \
  -m sglang.launch_server \
  --model-path /models/turboderp-Qwen3.8-27B-exl3-3.00bpw \
  --quantization exl3 \
  --trust-remote-code \
  --host 0.0.0.0 \
  --port 30000 \
  --served-model-name turboderp-Qwen3.8-27B-exl3-3.00bpw \
  --context-length 204800 \
  --mem-fraction-static 0.80 \
  --kv-cache-dtype fp8_e4m3 \
  --mamba-ssm-dtype bfloat16 \
  --max-running-requests 1 \
  --max-mamba-cache-size 5 \
  --cuda-graph-max-bs-decode 1 \
  --chunked-prefill-size 1024 \
  --max-prefill-tokens 1024 \
  --reasoning-parser qwen3 \
  --tool-call-parser qwen3_coder \
  --speculative-algorithm NEXTN \
  --speculative-num-steps 3 \
  --speculative-eagle-topk 1 \
  --speculative-num-draft-tokens 4 \
  --speculative-token-map /opt/sglang-exl3/tokenmaps/qwen38_hot32k_v2.pt
```

The page states: "135 tok/s decode", "591 tok/s prefill", a 200K context, "Tested on this card Sep 26, 2026"; the model
`turboderp/Qwen3.8-27B-exl3 @ 6fe61ad620abfe97c5b49f9722c2bceeea4ccc28`, EXL3 at 3 bits per weight; no SGLang version.
The registry's README: "Every recipe here is the output of a run that passed six checks on that card", made by
`python3 lab/lab.py try <repo>@<commit> --model <id> --engine tabbyapi-exl3 --card <card>`, which rents the card on Vast
or RunPod. The fetch tool summarizes pages: quote the page yourself before you cite it.

## QUESTIONS (the report answers each with an evidence table)

Every row: the fact or claim; its source (a URL pinned to a commit, a tag or a date, or `file:line` at the PIN); the
source's date; SOLID (read in a primary source this session) or UNSURE (a secondary source, an inference, or a source
another one contradicts: give both rows). A question with no evidence gets a NOT FOUND row that names the searches
tried. Mark a benchmark run by a project about its own engine as vendor-run.

**A. The recipe and its pieces**

- **A1.** The image `ghcr.io/0xsero/sglang-exl3`: its source repository; the SGLang version or commit it is built from;
  what it changes (the EXL3 path, `SGLANG_EXL3_EMBED_HOST`, `SGLANG_EXL3_KERNEL`, the token map, `/opt/entrypoint.sh`);
  its license, commit activity, last commit date and open issues. Is EXL3 in upstream SGLang, proposed in a PR, or only
  in the fork?
- **A2.** The registry's six checks and its benchmark method for this recipe: prompt length, output length, concurrency,
  number of runs, the tool that measured 135 and 591; and where the recipe's raw results live (link the files).
- **A3.** Each recipe flag's meaning, from SGLang's source or docs at the fork's base version:
  `--max-running-requests 1`, `--max-mamba-cache-size 5`, `--cuda-graph-max-bs-decode 1`, `--mem-fraction-static
  0.80`, `--chunked-prefill-size` and `--max-prefill-tokens` 1024, the NEXTN flags, `--speculative-token-map`. With
  `--max-running-requests 1`, what happens to a second concurrent request (it waits in the queue, or it is refused)?
  How many concurrent long chats could this configuration hold, from the memory arithmetic the sources give (the
  weights, the KV bytes per token for this model in fp8, the GDN state per request, the 0.80 fraction)? Show the
  arithmetic with each input's source.
- **A4.** The model `turboderp/Qwen3.8-27B-exl3` at 3.00 bpw (revision `6fe61ad6...`): its size; published quality
  evidence for EXL3 at 3.0 bpw on Qwen3.x-class models (perplexity, KL divergence, benchmark deltas against BF16 and
  against 4-bit formats) from turboderp's or exllamav3's own tables; and the same for `dbirks/Qwen3.8-27B-W4A16-AutoRound`
  (its model card's numbers). Two tables side by side, no comparison verdict.

**B. Caching and memory pressure (C-2, C-3)**

- **B1.** SGLang's prefix cache on a hybrid model (Qwen3.8's Gated DeltaNet layers beside its full-attention layers):
  how the radix cache keeps the linear-attention state (state snapshots at which token boundaries; the cache class and
  its current name; what `--max-mamba-cache-size` bounds), the version it arrived in, and its limits (does a hit need a
  snapshot at the exact branch point; how many snapshots fit).
- **B2.** SGLang under KV pressure: what the scheduler does when a new or a growing request does not fit (LRU eviction
  of unreferenced radix nodes; retraction of running requests; the queue; any OOM path), cited in the scheduler source at
  a pinned commit; and issues that report an OOM or a crash under concurrency on 24 GiB cards.
- **B3.** vLLM 0.28 on the same questions, for the live configuration: prefix caching with `mamba_cache_mode: align`
  (what "align" means; the block size it forces), and what happens when the KV pool is full (the queue; preemption by
  recompute; `num_preemptions_total`), cited at v0.28.0, plus the image's patches where they touch this (the image's
  own repository or README).
- **B4.** This project's own records of vLLM failures (grep `docs/INCIDENT-LOG.md` and `todo/BUILD-TASKLIST.md`; do not
  read them whole): AF-AP-201 (the `prompt_logprobs` OOM), AF-AP-231 and D-099 (the CUDA OOM in the prefill workspace
  beside a 256 MiB CUDA context of another process), AF-AP-146 (the 504 waits at long contexts), and any other vLLM OOM
  or crash. One row each: the date, what happened, the cause the record states, and the knob or rule that closed it.
  This table feeds C-2: state the records, not a judgement.

**C. Speed and concurrency (C-1, C-4)**

- **C1.** Published comparisons of SGLang and vLLM: throughput and latency, preferably on hybrid (GDN or Mamba) models,
  on Ampere or 24 GiB cards, and on multi-turn loads with shared prefixes (agents, long contexts). Prefer primary
  sources (the projects' blogs, papers, benchmark repositories that can be re-run); give each row its method, versions
  and date, and who ran it.
- **C2.** Speculative decoding: SGLang's NEXTN or EAGLE with more than one running request (supported; with the overlap
  scheduler; CUDA graphs per batch size), and its effect on throughput as concurrency grows; vLLM's MTP for Qwen3.8 above
  one request, and why the image's batch profile runs without it (the image's README or entrypoint: `Exec=batch` and
  `SPEC`); the image's single-user profile numbers.
- **C3.** Ampere (sm_86) support for each piece: SGLang's kernels for the GDN layers (flash-linear-attention or its
  own); the attention backend it picks on sm_86 (FlashInfer, Triton; FA3 is Hopper-only); fp8_e4m3 KV storage on sm_86
  (Ampere has no fp8 tensor cores: storage only, and which backends allow it); the EXL3 kernels on sm_86; and the same
  for the vLLM path. Read each dependency's own arch gate in its build or setup code (an upstream's docs once said "CUDA
  only" while a pinned dependency refused anything below sm_90: AF-AP-207).

**D. Compatibility with this project's clients**

- **D1.** SGLang's `/v1/completions` with a list of token ids as `prompt` and `logprobs: 20`: is
  `choices[0].logprobs.top_logprobs[0]` a dict of token to logprob (the shape `scripts/qwen_jev.py` requires); is
  `usage.prompt_tokens` the prompt's token count; is `model` the served name sent? Cite SGLang's OpenAI adapter source
  and its tests.
- **D2.** Chat completions: tools with the `qwen3_coder` parser; reasoning with the `qwen3` parser (the field that holds
  the reasoning text, in streamed chunks and in the final message); `chat_template_kwargs.enable_thinking`; `seed`; the
  streamed chunk shape; usage in a stream (`stream_options.include_usage`); `usage.prompt_tokens_details.cached_tokens`
  (the live vLLM sets `enable_prompt_tokens_details`).
- **D3.** The serving surface: two served names (vLLM's `--served-model-name` takes several; SGLang's?); `/v1/models`;
  the API key (does SGLang take it only on the command line, where the process list shows it, or also from a file or an
  environment variable?); `/health`; `/metrics` (the metric names `harness-ports/bin/qwen-server.sh` and
  `harness-ports/bin/qwen_matrix.py` parse at the PIN, and the SGLang names that carry the same facts: running and
  waiting requests, KV use, cache hits).
- **D4.** The container: rootless podman with CDI; `--ipc=host` or `--shm-size`; any need for root or for a given host
  driver version; the fork image's size.
- **D5.** The change list (no edits): every file in the premise block's consumer list, with the line that would change
  and why; plus `upstream.lock.yaml` and its attestation (D-110).

**E. Risk and upkeep**

- **E1.** Open issues in SGLang and in the fork for Qwen3.8 or Qwen3-Next-class hybrids on consumer cards: crashes,
  leaks, wrong outputs, interactions of the radix cache with speculative decoding, tool-call parser bugs; with dates
  and states.
- **E2.** Release cadence and pinning: tags, image digests, and how the fork follows upstream.

**F. Inputs for the A/B design (evidence only; the coordinator designs it)**

- **F1.** The metrics each server exports for time to first token, per-request decode speed, aggregate throughput,
  cache hit rate, preemptions or retractions, and queue depth.
- **F2.** Benchmark tools (`python -m sglang.bench_serving`, `vllm bench serve`, others): does each replay multi-turn
  chats with shared prefixes, with a fixed seed, against any OpenAI-compatible endpoint; the options that set
  concurrency and the prompt and output lengths.
- **F3.** A short fixed quality check that separates 3-bit from 4-bit weights on this model class and fits a GPU window,
  if the sources name one.

## STANDING RULES

- Write only the report. Never commit, stash, checkout or reset in `/home/user/agent-factory`. No outward-facing action:
  no GitHub issue, comment or PR, no `add_repo`, no post anywhere.
- No PC bridge (`scripts/pc.sh`, `scripts/pc_lane.sh` and `scripts/pc_suite.sh` are off limits); the PC-side facts are
  in the premise block, as the coordinator measured them.
- Do not run third-party code, install packages, pull images or clone repositories. Read sources on the web: GitHub
  pages and raw files at a pinned commit, docs, release notes, issues, PRs, Hugging Face model cards. Load the web tools
  with ToolSearch (`select:WebFetch,WebSearch`); Context7 (`mcp__Context7__resolve-library-id`,
  `mcp__Context7__query-docs`) and Exa (`mcp__Exa__web_search_exa`, `mcp__Exa__web_fetch_exa`) are also available.
- Never read secrets: `.pc-bridge.env`, any `*.env`, `/root/.codiv/`, key files, `.jev/`. The coordinator's scratchpad
  is off limits.
- Every number carries its source; never a number from memory. When sources disagree, give both rows.
- No verdict, no recommendation, no ranking of the two servers. You may state what a source claims and whether a second
  source confirms it.
- Your final message: the report's path, line count and sha256; one line per question group (rows filled, NOT FOUND
  rows); and the three facts you judge most load-bearing for the coordinator's verdict (facts, not a verdict).

## PREMISE — MEASURED at authoring (2026-10-01 20:2xZ, /home/user/agent-factory@610cb123)

Item 1 of your work: re-run each command below at your HEAD and compare. The last command checks that no commit after
the PIN changed the files the others read (it prints 0). Stop and report on any mismatch.

```
$ git rev-parse --verify 610cb123db21c2a043667bb401a58b36313d8cd4^{commit}
610cb123db21c2a043667bb401a58b36313d8cd4
$ git merge-base --is-ancestor 610cb123db21c2a043667bb401a58b36313d8cd4 HEAD && echo the PIN is an ancestor of HEAD
the PIN is an ancestor of HEAD
$ grep -n -E '^(Image|Exec|PublishPort|Environment|PodmanArgs)' deploy/qwen.container
21:Image=ghcr.io/syv-ai/qwen38-27b-rtx3090@sha256:c52d9033527df5249d2f7306b35173a47f4f87d45bb60927fbe93fdb4986aacb
22:Exec=batch
23:PublishPort=8080:8080
27:Environment=PORT=8080
28:Environment=SPEC=mtp
29:Environment=MAX_LEN=131072
30:Environment=PREFIX_CACHE=1
37:Environment=GPU_UTIL=0.96
38:Environment="EXTRA_ARGS=--served-model-name qwen3.8-27b-local qwen3.8-27b"
39:PodmanArgs=--ipc=host --device nvidia.com/gpu=all
$ grep -n -E 'image:|digest:|base_model:|engine:|served_model_names:' upstream.lock.yaml | grep -n -A0 -E 'syv-ai|c52d9033|AutoRound|vLLM 0.28|qwen3.8-27b-local'
6:228:    image: ghcr.io/syv-ai/qwen38-27b-rtx3090:latest
7:229:    digest: sha256:c52d9033527df5249d2f7306b35173a47f4f87d45bb60927fbe93fdb4986aacb
8:230:    base_model: dbirks/Qwen3.8-27B-W4A16-AutoRound
9:231:    engine: "vLLM 0.28 (MTP/batch), one RTX 3090, OpenAI-compatible on loopback :8080"
10:232:    served_model_names: [qwen3.8-27b-local, qwen3.8-27b]  # qwen3.8-27b-local = the id OmniRoute's agentfactory-*-local combos forward
$ grep -n 'upstream.lock.yaml' proofs/registry.yaml | grep -o -E '^[0-9]+:|"proof_id": "S0-[0-9]+"' | paste -d' ' - -
17: "proof_id": "S0-06"
23: "proof_id": "S0-12"
$ git grep -l -E 'localhost:8080|127\.0\.0\.1:8080|:8080/v1|qwen3\.8-27b-local' -- scripts harness-ports src deploy tests | sort
deploy/qwen.container
harness-ports/bin/lane-profile.sh
harness-ports/bin/omniroute_local_builder.py
harness-ports/bin/qwen-server.sh
harness-ports/bin/qwen_matrix.py
harness-ports/tests/test_lane_profile.sh
harness-ports/tests/test_omniroute_local_builder.py
harness-ports/tests/test_pc_lane_dispatcher.sh
harness-ports/tests/test_qwen_server.sh
scripts/gpu_window.sh
scripts/qwen_jev.py
scripts/s1_synth.py
scripts/t93r1_apply_profile.sh
tests/fixtures/qwen_jev/completion-choice.json
tests/fixtures/qwen_jev/completion-noul.json
tests/test_gpu_side_by_side.py
tests/test_qwen_jev.py
tests/test_s1_synth.py
$ grep -n -E '"prompt": list\(token_ids\)|"logprobs": 20|top_logprobs|served != self.sent_id|prompt_tokens != len' scripts/qwen_jev.py
33:is refused (not scored). Each label's logprob is read from choices[0].logprobs.top_logprobs[0]
184:    logprob from top_logprobs[0] (the dict, token string to logprob, as vLLM /v1/completions
208:        "prompt": list(token_ids),
211:        "logprobs": 20,
270:        if served != self.sent_id:
274:        if prompt_tokens != len(branch.token_ids):
277:        top_row = (resp["choices"][0].get("logprobs") or {}).get("top_logprobs") or [{}]  # type: ignore[union-attr]
282:            return None, [], False, "top_logprobs[0] is %s, not the token->logprob dict D-4 expects" % type(top).__name__, usage
$ grep -n -E 'ALLOWED_BODY_KEYS|FORBIDDEN_BODY_KEYS|chat_template_kwargs' scripts/s1_synth.py
44:  of ALLOWED_BODY_KEYS and never one of FORBIDDEN_BODY_KEYS (AF-AP-201: one such request OOM-killed the shared
168:ALLOWED_BODY_KEYS = frozenset(("model", "messages", "max_tokens", "temperature", "chat_template_kwargs"))
169:FORBIDDEN_BODY_KEYS = ("prompt_logprobs", "best_of", "echo", "n")   # per-prompt-token output or extra sequences
176:    """A vLLM request body with a key outside ALLOWED_BODY_KEYS: it is never sent."""
773:    """A vLLM body leaves only with EXACTLY ALLOWED_BODY_KEYS (AF-AP-201)."""
775:    bad = sorted(keys - ALLOWED_BODY_KEYS) + sorted(k for k in FORBIDDEN_BODY_KEYS if k in keys)
776:    if bad or keys != ALLOWED_BODY_KEYS:
777:        raise ForbiddenParam("a vLLM body must carry exactly %s; refused keys %s" % (sorted(ALLOWED_BODY_KEYS), bad))
786:            "chat_template_kwargs": {"enable_thinking": bool(thinking)}}
$ git grep -n -E '/metrics' -- scripts harness-ports/bin
harness-ports/bin/qwen-server.sh:331:  metrics=$(curl_key 5 "http://$QWEN_HOST:$QWEN_PORT/metrics" 2>/dev/null) || { echo "busy"; return; }
harness-ports/bin/qwen_matrix.py:79:    if path == "/metrics":
harness-ports/bin/qwen_matrix.py:381:        before = parse_metrics(request(base_url, "/metrics", key, timeout=30))
harness-ports/bin/qwen_matrix.py:389:        after = parse_metrics(request(base_url, "/metrics", key, timeout=30))
$ grep -n -i -E 'tok/s|concurren|aggregate' docs/research/findings/VLLM-MIGRATION.md
32:- **Measured throughput (one 3090, 250 W):** single-user 118–133 tok/s (382 with DFlash2 doc-repro);
33:  **batch C64 ≈ 1,035 tok/s aggregate** (8 slots). vs the current llama.cpp: 62 single / 93 at 4-up.
45:   launch the vLLM server (batch mode for lanes), benchmark single + 2/4/8/64 concurrent, confirm the
46:   ~1000 tok/s figure and the context that fits, wire it on the port OmniRoute expects with
85:  Container-measured batch: **~1,042 tok/s @ C64**; `single` profile = DFlash2 (owner chose MTP/batch).
91:Qwen3.8-27B under BOTH `qwen3.8-27b-local` and `qwen3.8-27b` on :8080; measured ~45 tok/s single-request
92:decode, near-linear to ~310 tok/s aggregate at 7 concurrent lanes. Image digest pinned in
$ grep -n -E 'KEEPER local model server|served-model-name|prompt_logprobs|second CUDA process|GPU_UTIL=0.96' PC-BRIDGE.md | cut -c1-200
61:| Local **vLLM** OpenAI-compatible endpoint `http://localhost:8010/v1`, served-model-name `sim9b`, guard `~/vllm_serve.sh` (setsid+flock), tool calling ON (`qwen3_xml` parser), thinking off via `ch
157:## The vLLM Qwen container — the KEEPER local model server (2026-09-16, D-032)
166:  `--served-model-name qwen3.8-27b` and appends `${EXTRA_ARGS}` last; vLLM's `--served-model-name` is
176:- **`GPU_UTIL=0.96` since 2026-09-26 (D-099; the image default is 0.972):** `laya-systemone` keeps a 256 MiB CUDA context (AF-AP-231), and at 0.972 vLLM had 63 MiB of slack: it crashed under four 
211:- **Never send `prompt_logprobs` (or `best_of`) to the shared server (AF-AP-201, 2026-09-24):** vLLM computes a float32
216:- **No second CUDA process while `qwen.service` runs (measured 2026-09-24 18:0xZ; a CPU-only service counts when it creates a context: `laya-systemone`'s probe holds 256 MiB, AF-AP-231, D-099):** 
$ grep -o -E 'the vLLM KV cache holds [0-9,]+ tokens and lanes that have run for hours send [0-9-]+k-token prompts, so TWO fit; a third lane.s request waits in vLLM past OmniRoute.s 80 s first-event limit and dies 504|run ONE long-context local lane and send the next to a sandbox agent' .claude/skills/pc-bridge-lanes/SKILL.md
the vLLM KV cache holds 222,822 tokens and lanes that have run for hours send 57-90k-token prompts, so TWO fit; a third lane's request waits in vLLM past OmniRoute's 80 s first-event limit and dies 504
run ONE long-context local lane and send the next to a sandbox agent
$ git diff --stat 610cb123db21c2a043667bb401a58b36313d8cd4 HEAD -- deploy/qwen.container upstream.lock.yaml proofs/registry.yaml scripts/qwen_jev.py scripts/s1_synth.py harness-ports/bin/qwen-server.sh harness-ports/bin/qwen_matrix.py harness-ports/bin/omniroute_local_builder.py scripts/gpu_window.sh docs/research/findings/VLLM-MIGRATION.md PC-BRIDGE.md .claude/skills/pc-bridge-lanes/SKILL.md | wc -l
0
```

### The PC (measured by the coordinator over the bridge at 2026-10-01 20:2xZ; you cannot re-run these; values named `api_key` and tokens of 40 or more characters were masked before the output was saved)

```
== podman ps (qwen)
qwen | ghcr.io/syv-ai/qwen38-27b-rtx3090@sha256:<long> | Up 5 days
== unit
active
== startup log lines
  PASS  mamba-chunked-prefill-align.patch applied
(APIServer pid=1) INFO 09-26 08:08:56 [api_utils.py:272] non-default args: {'model_tag': '/app/models/Qwen3.8-27B-W4A16-AutoRound', 'enable_auto_tool_choice': True, 'tool_call_parser': 'qwen3_coder', 'enable_prompt_tokens_details': True, 'host': '0.0.0.0', 'port': 8080, 'model': '/app/models/Qwen3.8-27B-W4A16-AutoRound', 'max_model_len': 131072, 'served_model_name': ['qwen3.8-27b-local', 'qwen3.8-27b'], 'reasoning_parser': 'qwen3', 'gpu_memory_utilization': 0.96, 'kv_cache_dtype': 'fp8', 'enable_prefix_caching': True, 'mamba_ssm_cache_dtype': 'float16', 'mamba_cache_mode': 'align', 'language_model_only': True, 'max_num_batched_tokens': 2048, 'max_num_seqs': 64, 'async_scheduling': True, 'compilation_config': {'mode': None, 'debug_dump_path': None, 'cache_dir': '', 'compile_cache_save_format': 'binary', 'backend': 'inductor', 'custom_ops': ['+rms_norm', '+silu_and_mul'], 'ir_enable_torch_wrap': None, 'splitting_ops': None, 'compile_mm_encoder': False, 'cudagraph_mm_encoder': False, 'encoder_cudagraph_token_budgets': [], '<long>': 0, 'encoder_cudagraph_max_frames_per_batch': None, 'compile_sizes': None, 'compile_ranges_endpoints': None, 'inductor_compile_config': {'enable_auto_functionalized_v2': False, 'combo_kernels': True, 'benchmark_combo_kernel': True}, 'inductor_passes': {}, 'cudagraph_mode': None, 'cudagraph_num_of_warmups': 0, 'cudagr
(EngineCore pid=392) INFO 09-26 08:09:08 [core.py:184] Initializing a V1 LLM engine (v0.28.0) with config: model='/app/models/Qwen3.8-27B-W4A16-AutoRound', speculative_config=None, tokenizer='/app/models/Qwen3.8-27B-W4A16-AutoRound', skip_tokenizer_init=False, tokenizer_mode=auto, revision=None, tokenizer_revision=None, trust_remote_code=False, dtype=torch.bfloat16, max_seq_len=131072, download_dir=None, load_format=auto, tensor_parallel_size=1, pipeline_parallel_size=1, data_parallel_size=1, decode_context_parallel_size=1, dcp_comm_backend=ag_rs, disable_custom_all_reduce=False, quantization=compressed-tensors, quantization_config=None, enforce_eager=False, enable_return_routed_experts=False, kv_cache_dtype=fp8, device_config=cuda, <long>(backend='auto', disable_any_whitespace=False, disable_additional_properties=False, reasoning_parser='qwen3', reasoning_parser_plugin='', enable_in_reasoning=False), <long>(show_hidden_metrics_for_version=None, otlp_traces_endpoint=None, collect_detailed_traces=None, kv_cache_metrics=False, kv_cache_metrics_sample=0.01, cudagraph_metrics=False, enable_layerwise_nvtx_tracing=False, enable_mfu_metrics=False, enable_mm_processor_stats=False, enable_logging_iteration_details=False, jit_monitor_mode='warn', jit_monitor_verbose=False), seed=0, served_model_name=qwen3.8-27b-
(EngineCore pid=392) INFO 09-26 08:09:41 [kv_cache_utils.py:2065] GPU KV cache size: 215,112 tokens, Maximum concurrency for 131,072 tokens per request: 1.64x
== gpu
NVIDIA GeForce RTX 3090, 24064 MiB, 24576 MiB
2223047, 256 MiB
2653216, 23542 MiB
== metrics
vllm:num_requests_running{engine="0",model_name="qwen3.8-27b-local"} 0.0
vllm:num_requests_waiting{engine="0",model_name="qwen3.8-27b-local"} 0.0
vllm:num_requests_waiting_by_reason{engine="0",model_name="qwen3.8-27b-local",reason="capacity"} 0.0
vllm:num_requests_waiting_by_reason{engine="0",model_name="qwen3.8-27b-local",reason="deferred"} 0.0
vllm:kv_cache_usage_perc{engine="0",model_name="qwen3.8-27b-local"} 0.0
vllm:prefix_cache_queries_total{engine="0",model_name="qwen3.8-27b-local"} 6.4929219e+07
vllm:prefix_cache_hits_total{engine="0",model_name="qwen3.8-27b-local"} 4.40416e+07
vllm:num_preemptions_total{engine="0",model_name="qwen3.8-27b-local"} 0.0
== live lanes
1
== the startup args, characters 560 to 1100 of the same line
 'mamba_cache_mode': 'align', 'language_model_only': True, 'max_num_batched_tokens': 2048, 'max_num_seqs': 64, 'async_scheduling': True, 'compilation_config': {'mode': None, 'debug_dump_path': None, 'cache_dir': '', 'compile_cache_save_format': 'binary', 'backend': 'inductor', 'custom_ops': ['+rms_norm', '+silu_and_mul'], 'ir_enable_torch_wrap': None, 'splitting_ops': None, 'compile_mm_encoder': False, 'cudagraph_mm_encoder': False, 'encoder_cudagraph_token_budgets': [], '<long>': 0, 'encoder_cudag
```
