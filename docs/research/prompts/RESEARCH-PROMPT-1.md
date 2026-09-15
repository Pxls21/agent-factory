# RESEARCH-PROMPT-1 — LANE THROUGHPUT: how do we get a 5–10 h Qwen3.8-27B build/verify lane on one RTX 3090 down to 2–3 h, with two or more lanes in flight, at equal-or-better accuracy?

> **At a glance:** Agent Factory's Stage 0 proofs are built and verified by autonomous Hermes lanes on the
> owner's PC, each lane a long agentic session (100–250 tool calls) against a LOCAL Qwen3.8-27B served by
> llama.cpp on a single RTX 3090 behind OmniRoute. One lane at a time is admitted to the local model, a build
> lane takes 4 h 53 m to 6 h 41 m of wall clock, a verify lane about the same, and every proof needs several
> build→verify rounds. Lane throughput is now the binding constraint on the whole project — a good problem,
> because the machinery around it works. This brief researches HOW to make the lanes faster and more parallel
> on this hardware WITHOUT lowering the accuracy the verify lanes measure — ideally raising it.
> Status: RESEARCH ONLY — nothing changes on the PC until findings return and are A/B-measured. Tracker: task
> `lane-throughput-research` (#61 in the session task DB; the ledger row in `todo/BUILD-TASKLIST.md`).
> Mode: EXPLORATORY-HYPOTHESIS — the solution space is open; a better approach than the candidates below is a
> first-class outcome. Council (RESEARCH-PROMPT-GUIDE step 1.5): **SKIPPED for this brief** by the owner's direct
> ask for the prompt (2026-09-15); the questions were framed from the measured evidence below and the luck-lens
> facets are applied inline (§Meta). If the returned findings propose a change that trades accuracy or security
> for speed, the coordinator runs a focused full-protocol council BEFORE it is adopted — never `--quick`.

## 1. The measured problem (verify these numbers — do not re-derive them from priors)

All numbers are pasted from primary sources on 2026-09-14/15 (`docs/research/FINDINGS-LOCAL-BUILDER-QWEN38.md`
§6, `docs/research/evidence/qwen38-matrix-2026-09-14.jsonl`, the running server's `/metrics`, the Hermes session
exports `~/qwen-builder/ab/*.md` on the PC).

**Hardware / OS.** Fedora 42 bare metal, kernel `6.17.11-200.fc42.x86_64`; AMD Ryzen 5 5600X (6 cores / 12
threads, 32 MiB L3); 125 GiB RAM (60 used, 67 buff/cache at measurement, an 8 GiB zram swap 100 % full — note it);
NVIDIA GeForce RTX 3090 24,576 MiB, driver 580.126.18, CUDA 13.0; NVMe home. The GPU is otherwise free: nothing
else may run on it while the model unit is up (it uses 21,587 MiB at 95 % utilisation during a lane).

**The server (the `qwen-builder` user unit, `harness-ports/bin/qwen-server.sh`).** llama.cpp `llama-server`
build `b1-00139b6` (a June 2026 CUDA build with MTP support, at
`~/Desktop/projects/llama-cpp/llama.cpp-mtp/build/bin/llama-server`), model `unsloth/Qwen3.8-27B-GGUF`
`Qwen3.8-27B-UD-IQ4_XS.gguf` (14,252,845,984 bytes), flags:
`-ngl 99 -c 262144 -fa on -ctk q4_0 -ctv q4_0 -np 1 --cache-reuse 256 --spec-type draft-mtp --spec-draft-n-max 3
--jinja --chat-template-kwargs {"reasoning_effort":"medium"|"xhigh"} --metrics --slots`, loopback `:8080`,
API-keyed, ONE slot holding the whole 262,144-token context. The reasoning effort is the SERVER default
(this build ignores a per-request top-level `reasoning_effort`; the llama.cpp-native
`chat_template_kwargs.reasoning_effort` does reach the template but Hermes does not send it), set by the sandbox
dispatcher per lane role before launch: build = `medium`, verify = `xhigh` (D-028, decided 2026-09-15).

**The measured matrix (one 36-token coding prompt, temperature 0, `max_tokens 400`, identical 305-token output
in every case — content sha `6b7c01ad` — so MTP was lossless here):**

| case | args beyond `-ngl 99 -fa on --jinja` | VRAM MiB | prompt t/s | decode t/s | MTP draft/accepted |
|---|---|---|---|---|---|
| base | `-c 32768 -ctk q4_0 -ctv q4_0 -np 1` | 14,586 | 119.4 | 44.28 | — |
| kv-f16 | `-c 32768 -np 1` | 15,972 | 119.5 | 44.67 | — |
| ngl54 (CPU offload) | `-ngl 54 -c 32768 q4_0 KV` | 12,436 | 33.9 | **6.32** | — |
| mtp-n2 | base + `--spec-type draft-mtp --spec-draft-n-max 2` | 15,154 | 98.0 | **79.92** | 212/200 (94.3 %) |
| mtp-n3 | base + `… --spec-draft-n-max 3` | 15,304 | 97.8 | **86.93** | 246/222 (90.2 %) |
| ctx262k | `-c 262144 q4_0 KV -np 1` | 19,738 | 119.4 | 44.11 | — |
| ctx262k-np2 | same, `-np 2` → 131,072 per slot | 19,760 | 119.4 | 43.95 | — |
| ctx262k-np4 | same, `-np 4` → 65,536 per slot | 19,996 | 119.9 | 44.06 | — |
| long60k | a 67,250-token prompt, no MTP | — | 1,007.5 | 28.87 | — |
| long60k-mtp | the same with MTP n=3 | 21,546 | — | **59.51** | 170/142 (83.5 %) |

The `-np 2` / `-np 4` rows measured ONE request each — **aggregate throughput under two or four CONCURRENT
lane-shaped requests was never measured** (§6 step 4 of the findings, still open). That is the first gap this
brief closes.

**The live counters (the server's `/metrics`, cumulative since its last restart, read 2026-09-15 08:20Z while a
verify lane ran):** `prompt_tokens_total 4.5843e+06` over `prompt_seconds_total 6262.45` → **732 prompt tokens/s
average**; `tokens_predicted_total 1.12724e+06` over `tokens_predicted_seconds_total 25700.5` → **43.9 generated
tokens/s average**; `n_decode_total 421781` → **2.67 tokens per decode step** (MTP accepting well). So of the
server's busy time, **80 % is decode and 20 % is prefill.** The lanes are decode-bound at the long, filled
contexts they run in, where the measured per-request decode is 44–60 t/s with MTP (not the 87 t/s of a short
prompt).

**What a lane consumes (Hermes session exports; the SAME brief three times):**

| lane | effort | messages / tool calls | input tokens (new) | output tokens | cache-read tokens | wall clock |
|---|---|---|---|---|---|---|
| N5k arm A | medium | 483 / 243 | 5,678,025 | 386,202 | 23,332,700 | 4 h 53 m to substantive completion |
| N5k arm B v2 | xhigh | 186 / 96 | 536,387 | 284,368 | 9,364,881 | 2 h 05 m, stopped (two investigation loops, one line of code) |
| N5k arm B v3 | xhigh | 281 / 139 | 4,503,614 | 694,413 | 29,547,152 | 6 h 41 m to substantive completion |

Read the arithmetic: 386 k output tokens at ~44 t/s ≈ 2.4 h of pure decode; 694 k ≈ 4.4 h; 4.5–5.7 M NEW input
tokens at 732–1,007 t/s ≈ 1.3–2.1 h of prefill; the rest is tool execution (pytest runs of 50–680 s, the gates)
and harness overhead. **Two facts dominate:** (a) `xhigh` roughly doubles output tokens for the same brief
(the reasoning stream), which is why D-028 keeps builds at `medium`; (b) a lane feeds ~23 k NEW tokens per tool
call on average (5.68 M / 243) — the tool RESULTS (whole-file reads of a 3,600-line test file are ~40 k tokens
each; pytest output; grep dumps) are the prefill load, and Hermes's default `file_read_max_chars` is 100,000
chars (≈25–35 k tokens per read).

**The harness facts that bound the design (all primary-sourced, 2026-09-15):**
- Hermes (`b3399c1`, `~/.hermes/hermes-agent`) compresses the conversation when usage exceeds
  `compression.threshold` = 0.5 of the model window, FLOORED at 0.75 for windows below 512 K
  (`hermes_cli/config_defaults.py:524-548`; the lane profile `~/.hermes/profiles/agentfactory/config.yaml:85-90`
  sets enabled, threshold 0.5, target_ratio 0.2, protect_last_n 20, protect_first_n 3; `tail_mode` = `lean`).
  The window Hermes believes in comes from `agent/agent_init.py:1673 _resolve_context_length` (the profile's
  `model.context_length` if set, else the provider's model metadata). **The first lane on a 4-slot server
  (65,536 tokens per slot) overflowed the slot four times in eight minutes because Hermes believed a ~200 K
  window and never compacted** — the slot size and the window Hermes compacts against MUST agree. That is a
  configuration fact, not a model limit.
- Hermes `file_read_max_chars` = 100,000 (default; the profile does not override it); `context_file_max_chars`
  = 60,000 (pinned); the project context file `.hermes.md` is 43 K chars, injected every turn (cached).
- OmniRoute (`:20128`, the SOLE model egress; `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=2` +
  `OMNIROUTE_CHAT_ADMISSION_HEALTHY_HEADROOM=2` = four heavy requests in flight, a 60 s admission queue; a fifth
  waits, a refusal is `HTTP 503 … capacity is busy` and costs the lane one in-flight turn) fronts the local
  server as node `qwen-local`, combos `agentfactory-build-local` and `agentfactory-verify-local`
  (`harness-ports/bin/omniroute_local_builder.py`). OmniRoute's `call_logs` table records every call (S0-03's
  checker reads it: `proofs/S0-03/check_omniroute_roundtrip.py`) — the primary source for per-call latency.
- The dispatcher (`scripts/pc_lane.sh` → `harness-ports/bin/pc-lane.sh`) enforces ONE local lane at a time,
  sets the server effort per role (a unit restart only when the unit text changed and NO lane pidfile is
  alive), gives each lane a detached worktree with a graft index, and resumes a refused or killed lane from its
  incremental draft. Five STANDING LANE RULES ride in every prompt (CONTEXT BUDGET — read by symbol/range, never
  whole; INCREMENTAL REPORT; MECHANICAL GATES ARE BOUNDED; PREMISE CONFLICTS ARE BOUNDED; CODE INTEL FIRST).
- The cloud route (`agentfactory-build` = the owner's OpenAI model through OmniRoute at `ultra`) is the
  sanctioned FALLBACK when the local slot is busy; it shares the four-request admission with the owner's own
  interactive sessions. It is not the answer to this brief.

## 2. Current-state capability ledger (proven-live vs built-never-run vs absent — do not re-derive)

- **Proven live:** the `qwen-builder` unit and every flag above (`harness-ports/bin/qwen-server.sh`: env-default
  shape, `install|argv|probe|restart` subcommands, health wait, the live-lane refusal); the OmniRoute node +
  two combos; the dispatcher's server-effort step; MTP n=3 at 90 % acceptance on code and 83.5 % at a filled
  67 K context; the full 262 K q4_0 KV resident (19.7 GiB); the Hermes lanes end to end (three N5k runs, one
  verify lane and one cloud lane live at the time of writing); the incremental-draft resume; the A/B METHOD
  (D-028's protocol: ONE brief, two arms, ONE adversarial-verifier grader on the brief's own gates — items
  closed, red tests gone green, mutants killed, discrepancies, false claims — plus wall clock and tokens).
- **Built, never run:** `-np 2` and `-np 4` under CONCURRENT lane traffic (only single requests measured);
  the llama.cpp-native per-request `chat_template_kwargs.reasoning_effort` through OmniRoute (proven to reach
  the template; Hermes does not send it — a profile `extra_body` could); `--cache-reuse 256` is on but its
  hit behaviour under lane traffic was never read from `/metrics` or `/slots`.
- **Absent:** any per-slot window matching between llama-server and Hermes (`model.context_length` unset in
  the lane profile); any tool-output cap below Hermes's defaults (`file_read_max_chars` 100 K); any
  measurement of OmniRoute's added latency per call; any prefill batch tuning (`-b`/`-ub` are llama.cpp
  defaults); any KV-cache quality comparison (q4_0 vs q8_0 vs f16) on LANE outputs rather than one prompt; a
  second draft model; any non-llama.cpp server on this PC for this model.
- **Falsified already (do NOT propose again):** CPU offload `-ngl 54` — 7.0× slower decode (6.32 vs 44.28 t/s)
  for 2.1 GiB nothing needs; f16 KV at 262 K — does not fit in 24 GiB; a 4-slot server with Hermes unaware of the
  slot size — overflowed in 8 min (the mismatch, not the slot, is the cause); Hermes `--reasoning` on the local
  model — inert by measurement; a 65 K→"just use a smaller context" answer that ignores that lanes legitimately
  grow past 100 K without compaction.

## 3. SETTLED (guardrails only — NOT the solution; do not reopen)

1. **Accuracy-never-worse, measured by the existing oracle (NON-NEGOTIABLE).** The only accuracy instrument is
   the adversarial VERIFY lane's grade of a lane's output against the brief's own gates (items closed, red
   tests gone green, mutant kills, discrepancies stated, false claims) plus the sandbox/PC test gates. NO
   LLM-as-judge is added to the gate spine. Every speed lever that could change model OUTPUTS (quantisation, KV
   type, sampling, compaction frequency, effort, a different server or draft) ships ONLY through the A/B method
   (same brief, same PIN, baseline arm vs candidate arm, one grader) and becomes a default only if the grade is
   equal or better. A lever that is faster and worse is REJECTED regardless of the speedup. (Rejected
   alternative: adopting a speed setting on throughput numbers alone.)
2. **The substrate is fixed for this brief:** a LOCAL model on the owner's one RTX 3090, served on loopback,
   API-keyed, fronted by OmniRoute as the sole egress, driven by Hermes lanes through the existing dispatcher.
   The model family is Qwen3.8-27B (the 4-bit UD-IQ4_XS GGUF today). The cloud route stays the fallback, not
   the plan. A different SERVER for the same model is in scope only as §5-L5 (bounded); a different MODEL as the
   builder is out of scope (accuracy first) except as a DRAFT for speculative decoding (§5-L4).
3. **Security invariants unchanged:** OmniRoute the sole egress; no direct provider credentials anywhere; the
   loopback bind and the API key stay; secrets never in any sink or report; the owner's other services (Buzz
   relay, OmniRoute, Ollama, Phoenix, OpenObserve, neo4j) are never stopped or reconfigured by a lane or the
   coordinator; the model unit is restarted only through `qwen-server.sh install` with no live lane, and `sudo`
   is the owner's.
4. **The lane discipline stays and is an accuracy lever, not a cost:** the five standing lane rules, the
   code-intel-first wiring, the bounded gates, the incremental draft, D-028's effort split (build `medium`,
   verify `xhigh`) — a recipe may TIGHTEN these (e.g. a hard read cap) but never loosen them for speed.
5. **The deliverable is a measured recipe for THIS setup, not a harness rewrite.** Every recommendation names
   the exact knob (`file:key` or flag), its measured or primary-sourced effect, its accuracy risk, and the A/B
   gate that admits it. ADOPT existing mechanisms (llama.cpp flags, Hermes config keys, OmniRoute env, the
   dispatcher's env defaults) over inventing new ones.
6. **Rejected, named:** CPU offload; f16 KV at 262 K; `--quick` council; "run everything on the cloud route"
   (the four-request admission is shared with the owner's own sessions and the owner chose the local builder);
   "lower the verify effort to save time" (xhigh verifies — D-028); trading determinism (temperature 0 stays for
   the gates that use it).

## 4. Preliminary findings — INLINE. VERIFY, DEEPEN, CHALLENGE; do not re-derive.

- **F1 (decode-bound).** 80 % of server time is decode at ~44 t/s effective, 20 % prefill at ~730 t/s. Per lane
  the output side (0.4–0.7 M tokens) costs 2.4–4.4 h; the new-input side (4.5–5.7 M tokens) 1.3–2.1 h. Any
  recipe that does not raise AGGREGATE decode throughput or cut output tokens cannot reach 2–3 h. Challenge:
  read `/metrics` again over one full lane (start-to-end deltas, not cumulative) and split by phase.
- **F2 (the concurrency hypothesis, strongest candidate).** Decode on a 3090 is memory-bandwidth-bound; two or
  three sequences decoded in one batch cost little more per step than one. The matrix shows `-np 2` costs
  0.02 GiB and `-np 4` 0.26 GiB of VRAM over one slot at the full 262 K, so the KV budget allows 2 × 131 K or
  4 × 65 K slots. The expected aggregate gain is 1.6–2.5× at `-np 2..3` IF the per-step cost stays flat — the
  unmeasured quantity. Two conditions: (i) Hermes must compact against the SLOT size (set the lane profile's
  `model.context_length` = per-slot tokens, or the OmniRoute-advertised context, so the 0.75 floor fires at
  ~98 K on a 131 K slot); (ii) MTP with `-np > 1` — verify in the llama.cpp source and by run that speculative
  drafting works per slot (it may be disabled or serialised under parallel slots in this build).
- **F3 (the token diet).** ~23 k new tokens per tool call means tool RESULTS dominate prefill. Levers: Hermes
  `file_read_max_chars` (100 K → e.g. 24 K chars forces ranged reads, which the CONTEXT BUDGET rule already
  demands), a tool-output cap for `terminal` (pytest/grep dumps) if Hermes has one (primary-source the config
  keys; `hermes_cli/config_defaults.py`), `compression.tail_mode lean` (already default) and a LOWER threshold
  than 0.75 so compaction happens earlier and prefill per turn shrinks — each compaction is LOSSY and is a
  summariser call on the same model, so its accuracy effect is A/B-gated.
- **F4 (effort).** `xhigh` ≈ 1.8× the output tokens of `medium` on the same brief with no better landing
  (v3 landed the same items in 6 h 41 m vs 4 h 53 m); D-028 already keeps builds at `medium`. The per-request
  `chat_template_kwargs.reasoning_effort` path exists and reaches the template through OmniRoute — a per-LANE
  effort would let build and verify lanes share one server without a restart (today the server effort is
  global and a change refuses under a live lane).
- **F5 (kernel levers).** MTP n=3 gives 2.0× on a short prompt and 2.06× at a filled 67 K context; acceptance
  falls from 90 % to 83.5 % with context — n=4/5 may win or lose at 150 K+, measure. Prefill batch sizes
  (`-b`, `-ub`) are llama.cpp defaults (2048/512 in mainline); the 3090 usually prefills faster with a larger
  micro-batch. KV `q8_0` costs ~2× the q4_0 KV bytes (fits at 131 K per slot × 2? compute it) and may change
  outputs at long context — A/B-gated. A newer llama.cpp build than `b1-00139b6` may carry faster
  hybrid-attention (Qwen3.8's gated-delta layers) and MTP kernels — primary-source the changelog and measure;
  the current build is pinned by its behaviour, not by a lock file.
- **F6 (harness overhead).** Each tool call is a full HTTP round trip through OmniRoute plus Hermes's tool
  loop; OmniRoute's admission queue, logging and the `call_logs` write add per-call latency that is unmeasured.
  With 100–250 calls per lane, 5 s of overhead per call is 8–20 min — small against decode, but measure it from
  `call_logs` timestamps vs the server's own timing before dismissing it.
- **F7 (the round count).** A proof needs several build→verify rounds (S0-01 is at round 16); every NOT-READY
  verdict costs another 5–10 h. The code-intel wiring (graft index in the lane tree, the pack, the five rules)
  landed 2026-09-15 to raise first-pass quality; it is not this brief's subject, but the report's model of
  "time to a green proof" must include rounds, not only hours per lane.
- **F8 (host state).** The 8 GiB zram swap was 100 % full with 60 GiB RAM used and 67 GiB in page cache while
  a lane ran; the model lives on the GPU, so this is not the model — but memory pressure can stall the harness
  and the test runs. Name what holds the RAM (the HF cache pages? Hermes? OmniRoute?) and whether it matters.

## 5. Candidate levers (bounded-open; evaluate ALL, RECOMMEND by the criteria in §6 — do not ask which we want)

- **L1 — Concurrent slots (`-np 2` or `-np 3`) with the Hermes window matched to the slot.** `[EMPIRICAL GATE —
  run FIRST]` Measure aggregate decode t/s and per-request decode t/s with 1, 2, 3, 4 concurrent lane-shaped
  requests (a 60–100 K prefilled context each, 2–4 K generated tokens, MTP on and off), at the per-slot
  contexts 262 K / 131 K / 87 K / 65 K. Decision rule: adopt the largest `-np` whose per-request decode stays
  ≥ 70 % of the single-slot rate AND whose slot fits a lane after compaction at the 0.75 floor; below 1.3×
  aggregate at `-np 2`, concurrency is not the lever and L2/L3 lead.
- **L2 — The per-lane token diet.** `[PRIMARY-SOURCE TECHNICAL, then EMPIRICAL]` Resolve from Hermes's source
  which caps exist (`file_read_max_chars`, any terminal/tool-output truncation, compression thresholds and
  `tail_mode`, the skills index size in the system prompt) and what each does; propose the exact profile
  values; measure the new-input tokens per tool call and the compaction count on the same brief. Decision
  rule: a diet setting is adopted if the A/B grade holds and new-input tokens per lane fall ≥ 30 %.
- **L3 — Decode/prefill kernel levers on the current server:** MTP `n` at 100–200 K contexts, `-b`/`-ub`,
  KV `q8_0` vs `q4_0` at the chosen slot size, `--cache-reuse` behaviour under lane traffic (read `/slots`),
  thread count `-t` for the CPU-side work, a NEWER llama.cpp build with the same model. `[EMPIRICAL — each
  one variable at a time, the matrix's method]`
- **L4 — Speculative decoding beyond MTP:** a small draft model (`--model-draft`, e.g. a Qwen3.8 ~1–2 B GGUF)
  vs the built-in MTP head; VRAM cost vs acceptance at long context. `[PRIMARY-SOURCE (does this build allow a
  draft model together with MTP? the two are exclusive in mainline) then EMPIRICAL]`
- **L5 — The inference server (paradigm dial, BOUNDED to one section):** would vLLM / SGLang / TensorRT-LLM
  with a 4-bit quant (AWQ/GPTQ/FP8-KV) of Qwen3.8-27B on ONE 3090 give higher aggregate decode under
  continuous batching than llama.cpp with slots, with MTP/speculative support for this hybrid-attention
  architecture and a 100 K+ context? Recommend keep-or-switch with evidence (published 3090 numbers count only
  if the architecture, quant and context match; otherwise state the measurement to run). Default: keep
  llama.cpp. A switch is admitted only at ≥ 2× aggregate decode at equal A/B grades AND it sits behind OmniRoute
  as the same `qwen-local` node.
- **L6 — Harness overhead:** per-call latency added by OmniRoute (from `call_logs` timestamps vs the
  server's timing), Hermes's turn loop, tool-execution time (the pytest gates: 50–680 s each — can the lanes run
  fewer or narrower gates without losing the contract? the brief author's lever, name it), and parallel tool
  calls if Hermes supports them. `[PRIMARY-SOURCE + measurement]`
- **L7 — Per-lane effort without a server restart:** send `chat_template_kwargs.reasoning_effort` per lane
  (Hermes profile `extra_body`, proven to reach the template through OmniRoute) so build (`medium`) and verify
  (`xhigh`) lanes share one server concurrently. `[DESIGN — settled direction: do it if L1 admits ≥ 2 slots;
  OPEN: the exact Hermes config path and that the cloud fallback members ignore the key harmlessly]`

**Thesis-stance dial (SETTLED):** the thesis "this setup can run lanes 2–3× faster at equal accuracy" is on
trial — develop BOTH the best-fair-chance recipe AND, if the measurements say the ceiling on one 3090 is below
2×, the honest ceiling statement with what the next hardware step (a second GPU, owner's decision, out of this
brief's scope) would buy. **Paradigm/substrate dial (SETTLED):** the server is challengeable only in L5; the
model family, the GPU, OmniRoute-as-egress and Hermes-as-harness are fixed.

## 6. PRIMARY DELIVERABLE (one)

**PRIORITY (SETTLED — do not ask which is primary):** a single ranked **throughput recipe** for this PC —
the ordered list of changes to make, each with (i) the exact knob (`file:key` / flag / env), (ii) the expected
effect on lane wall clock AND lanes in flight, with the evidence (a run on this PC where the brief asks for
one, a primary-source derivation otherwise), (iii) the accuracy risk and the A/B gate that admits it, (iv) the
order to apply them in (one variable at a time, the cheapest order-changing measurement first). The recipe's
headline is a NUMBER: the projected wall clock of the N5k-shaped build lane and of a verify lane, and the
projected lanes in flight, on the recommended configuration.

Subordinate (relationship stated):
- **The measurement protocol** [EMPIRICAL GATE — the validity gate on the primary]: the concurrency matrix of
  L1 (exact commands for `llama-server`, the request shapes, what to read from `/metrics` and `/slots`), then
  ONE A/B on a real brief (the N5k brief on PIN `3277373` is the calibrated baseline: arm A `113 passed`,
  4 h 53 m, 243 tool calls; use it) on the recommended configuration, graded by the existing verify lane.
  Acceptance: the grade equal or better, wall clock ≤ 60 % of baseline, and no slot overflow.
- **The accuracy guard set** [DESIGN — direction settled (the verify lane's grade + the test gates + mutant
  kills); OPEN-technical: the exact metric list and its operating point, e.g. "NOT-READY findings count and
  blocking class, items closed, mutants killed, discrepancies stated, false claims — equal or better on every
  metric, never a sum"].
- **The ceiling statement** [downstream]: the measured maximum lanes-in-flight and the wall clock at that
  point on one 3090, and the first hardware or architecture step beyond it, with its expected gain.

## 7. What would change the plan (each with its resolution — never "come ask")

- **L1 gives < 1.3× aggregate at `-np 2`:** concurrency is not the lever; lead with L2 + L3 and say so.
- **Compaction at a smaller slot lowers the A/B grade:** keep fewer, larger slots (`-np 2` at 131 K) and
  make the token diet (L2) do the work; never trade the grade.
- **MTP acceptance collapses above ~150 K context:** recommend `n=2`, or a context ceiling with earlier
  compaction; the report states which by measurement.
- **The current llama.cpp build cannot do MTP with `-np > 1`:** measure the newest mainline build that can;
  if none, concurrency without MTP vs one slot with MTP is decided by the aggregate number, not by preference.
- **A server switch (L5) is faster but changes outputs:** it is admitted only through the A/B; if the grade
  drops, it is rejected and the report says so.
- **The numbers say one 3090 tops out below 2×:** the report returns the honest ceiling, the best recipe
  under it, and the second-GPU projection for the owner — it does NOT return "uncertain".

## 8. Meta (luck lens — workflow facets, never a verdict input)

Solvency: every knob is an env default in `qwen-server.sh` or a key in the lane profile / OmniRoute env — one
script and one profile to maintain, no new component. Circulation: every measurement lands in
`docs/research/FINDINGS-LOCAL-BUILDER-QWEN38.md` §6 and `docs/research/evidence/*.jsonl`, and the recipe's
defaults into `qwen-server.sh`, so the next tuning starts from data. Path sensitivity: right time — the proof
machinery is built, lanes are the binding constraint, and seven proofs are queued behind one slot.

## 9. Deliverable shape

A findings report `docs/research/findings/RESEARCH-FINDINGS-1-VERIFIED.md` with: (1) the verified/challenged
version of §4 (each F-row confirmed, corrected or refuted with its source); (2) the L1 concurrency matrix as a
table with the raw commands; (3) the ranked recipe of §6 with the headline numbers; (4) the accuracy guard set
and the A/B run plan; (5) the ceiling statement; (6) the honest NOT-resolved list — empirical gates only, each
as a runnable command with its decision rule, never a strategic hedge. Every open question above returns a
decision-grade verdict; when documentation is silent, go to the source (llama.cpp, Hermes, OmniRoute) and read
it. A report that leaves any of §5 a bare uncertainty is incomplete and is continued, not accepted.

Decide; do not ask.
