# Jev / Laya integration — the grounded audit and plan (2026-09-22)

> **Status:** audit COMPLETE (five Opus 5 evidence lanes, file:line-cited, verbatim under `jev-audit/`);
> the plan below is the coordinator's synthesis; the research prompt that settles the technical resolution is
> `docs/research/prompts/RESEARCH-PROMPT-2.md`. Nothing is installed in any production runtime; the only
> artifacts so far are the vendored TypeSafe skill (`.claude/skills/typesafe-ai/`, MIT) and two throwaway
> measurement venvs (`/root/venv-laya` in the sandbox, `/home/rocco/laya-venv` on the PC).
> Owner decisions already taken: D-040 (both venues), D-041 (a first-party ledger). Tracker: task #104.

## 1. TL;DR

- **What "Jev" is.** TypeSafe's hosted System One model: typed questions (`choice` / `score` / `noul` = a
  yes/no probability) over a JSON `state`, answered in one forward pass with calibrated probabilities. Code owns
  the workflow; the model supplies narrow judgments. The open counterpart is **Laya** (Convai Innovations,
  Apache-2.0): ModernBERT-large 421M (English, 512 tokens), mmBERT-base 322M (multilingual, 1024) and a 421M
  typed-decisions checkpoint (1024), weights public on Hugging Face, `Agent.system_one(state, questions)` →
  `{model, answers, usage}` — the same response shape as TypeSafe's API.
- **The one place it pays first.** Our own inventory found that NOTHING prunes tool output entering the
  coordinator's context today (the honey compressor is inert here and upstream drops its rewrite for the built-in
  Bash tool), `test_summary.sh` prints whole pytest runs, and a Hermes `terminal` call has no byte cap. A
  block-level relevance sieve (winnow's design) is the highest-value, lowest-risk integration, and it is where the
  Qwen lane's wall time goes.
- **The honest caveats.** Laya's committed measurements put its typed-decisions accuracy at **0.36** (n = 2000,
  ECE 0.17), not the README's headline 0.766 (no committed producer); CPU inference is float32 only and MEASURED at
  ~1.0-1.25 s per question on both venues (§5.1; Laya's own sweep claims 100-300 ms on 4 threads, not reproduced
  here; batching did not amortize); states longer than 512/1024 tokens are
  SILENTLY truncated. So every judgment must be measured on OUR data before it hides anything, and the model never
  decides a gate.
- **Decided:** both venues (D-040); a first-party ledger, not the unlicensed jevcache binary (D-041); Aegis is not
  adopted (nothing our gates lack; its governance concepts are docs-only for an unbuilt "Runtime Core").
- **Next:** the research prompt (attached to chat) → council → interview → seed → breakdown → build with Opus via
  the Workflow, sandbox first, PC second, every step behind a measurement.

## 2. What the owner asked (2026-09-22 11:4xZ, distilled)

Reduce cost and speed up development by integrating a Jev-class typed-decision model everywhere: the sandbox and
Hermes, the skills / workflows / CLAUDE.md stack, the plugins, the code-intel quartet. Offload the Qwen builder's
long menial steps ("slow as hell … doing a bunch of long menial things"). Replace binary / probability decision
steps in skills with typed decisions. Run the 421M model in the sandbox if it fits, else on the PC behind the
bridge or a Cloudflare tunnel; both venues need it. Build it with Opus and the multi-agent Workflow ("ultracode").
Six repositories were named: laya, jevcache, jev-pruner, Aegis ("if advantageous"), winnow, and the lost "skill
for Jev" (found: TypeSafe's official skill, vendored).

## 3. The repositories — facts (each row cited in `jev-audit/<name>-evidence.md`)

| Repo | What it is | License | Load-bearing facts |
|---|---|---|---|
| `NandhaKishorM/laya` @ 573e5b6 | the open System One model + inference runtime | Apache-2.0 | `Agent.system_one` / `Router.predict`; NO server, NO CLI, NO quantization; CPU forced to float32; `snapshot_download` from HF (`model.safetensors` 843 MB English, 644 MB multilingual, 843 MB typed-decisions); states right-truncated at `max_len` silently; in-repo CPU sweep (4 threads): 116-256 ms per 1-question case English, 77-103 ms multilingual, 1392 ms per 5-question typed-decisions case; T4: 33-40 ms; typed-decisions accuracy 0.362 measured vs 0.766 claimed (no producer); `Agent` is not thread-safe (OOM path mutates instance state); the tokenizer config is rewritten in the HF cache at load |
| `typesafe-ai/skills` @ 65a39f3 | the official agent skill (the one the owner lost) | MIT | 10 KB markdown: primitives, patterns, "read the live docs"; vendored verbatim into `.claude/skills/typesafe-ai/` |
| `GhalebDweikat/winnow` @ 51d80b9 | a calibrated context sieve for Claude Code | MIT | `tool.call` function hook (CC ≥ 2.1.260, `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1`) for Read/Bash/Grep; a loopback sidecar (`winnow serve`, port 47311); ~25-line blocks, one `noul` per block + an `error_present` noul, keep ≥ 0.5 / drop < 0.1 / uncertain kept; stubs + `winnow_recall` MCP tool; `Judge` protocol with `typesafe` / `adapter` / `off` backends (a Laya backend = one class + one branch); optional Anthropic-Haiku summarizer with a deterministic digest fallback; a prompt-time memory-file ranker; measured on 300 cases: Jev ECE 0.14-0.18 vs lexical 0.31, regret 0.0 on 23 hidden blocks (hand labels); the author's own "jevlike" local-judge experiments (Qwen2.5-0.5B) reach ECE 0.135-0.168 |
| `tamaratran/jev-pruner` @ 47d017c | a Claude Code plugin that prunes long Bash output with per-chunk nouls | MIT | the endpoint is a constant with a `baseUrl` parameter no caller passes (a non-TypeSafe server needs a source edit); the algorithm core `trimOutput(input, asker, options)` is harness-free and portable; 10,000-token floor, 200-chunk cap, protected diagnostics/results, secrets never archived; the Codex path is a model-invoked wrapper binary because a command hook cannot rewrite results; the accuracy oracle is a planted-needle substring check |
| `hyperspaceai/jevcache` @ a211d13 | a decision ledger CLI (README only) | none stated in a file | no source, no LICENSE file, no checksum file, no installer in the repo; a `curl \| sh` Rust binary; Releases 403 from the sandbox; the IDEA is sound (canonicalize + redact before hashing, per-schema salt, append-only log, `recall` ≠ `decide`, exit 3 on miss, replay) → D-041 first-party |
| `GanyuanRan/Aegis` @ 60321ed | an MIT "method pack" (22 skills from Superpowers, hooks, a workspace CLI) | MIT | gate decision / evidence sufficiency / completion authority / baseline truth / policy snapshot exist only as docs and disclaimer strings; no anti-pattern registry, no hollow-green detection; writes `~/.config/aegis/`, a managed block into `~/.codex/AGENTS.md`, a `docs/aegis/` workspace; benchmark = bounded advisory. NOT adopted |

## 4. Our own decision points (`jev-audit/our-decision-points-evidence.md`)

- **T1 — where long tool output enters a model context, unbounded today:** the Claude Code Bash tool into the
  coordinator's context (no in-repo hook; the honey compressor inert: `~/.claude/.honey-active` absent, and
  claude-code#68951 drops `updatedToolOutput` for the built-in Bash); `scripts/test_summary.sh` prints the whole
  pytest run; Hermes `terminal` output in PC lanes (no byte cap; the 420 s cap is time); the lane prompt ~47 KB;
  `lane_context.sh` packs bounded only by `head -N`.
- **T2 — model-made binary/probability decisions today:** the verify lane's gate recommendation and per-finding
  class (Qwen local / Opus 5) — advisory by contract, evidence artifacts; the builder's premise true/false (bounded
  to three experiments); hive-reviewer severity and hive-scout roles (Haiku); bug-echo's six-dimension rating
  (Fable); prism findings; lane-state classification (regexes — deterministic, stays); `wiki-context.py` relevance
  (lexical scoring, no model); `graft-first-nag` (regex).
- **T3 — protected, model-free, must stay so:** report_lint, ap_screen, lane_gate, test_summary counts, pc_suite
  set ids, validate-ledger, proof-runner attestation, the seed's frozen `spike_to_class_mapping`, the dispatcher's
  premise gate and headroom admission, the pre-commit gates (pyflakes delta, anchors, skill sync, mirror, lane
  skills, shell syntax), push_clean's identity/trailer checks, the lane git shim, lane_context's refusals.
- **T4 — quantified sinks:** 81 KB system prompt per lane call before the skill-index fix; 97k-104k-token requests
  exceeding a 65k context; 95,908 tokens in on one verify-local turn; a lane's 47-minute report_lint loop; 4 h 53 m
  to 6 h 41 m build lanes; 420 s per terminal call; 132 whole-file reads + 456 shell calls in one lane.

## 5. Venue facts (measured 2026-09-22)

- **Sandbox:** 4 cores, 15 GB RAM (14 free), disk 6.2 GB free before the spike (4.8 GB after the 1.2 GB venv);
  Python 3.11.15; Claude Code 2.1.278 (function hooks available, NOT enabled); PyPI and the PyTorch CPU wheel
  index reachable; Hugging Face reachable (the three Laya checkpoints listed, public, ungated); GitHub Releases
  pages 403 through the proxy (git clones work).
- **PC:** Fedora 42, 12 cores, RAM 125 GB total / 106 GB free (the "920 GB" in chat is not what `free -g` reports),
  430 GB free on `/home`; RTX 3090 with 24,022 of 24,576 MiB in use by the vLLM `qwen` container at 100 %
  utilization (no GPU headroom without the owner lowering `gpu_memory_utilization` and restarting that container);
  no torch in the project venv; a throwaway `/home/rocco/laya-venv` (1.2 GB) created for the spike.
- **Spike (real Laya CPU latency on tool-output-shaped states, both venues):** §5.1 — both runs landed (12:02Z sandbox, 12:03Z PC).
- **Byte shares (measured 2026-09-22, the cost premise):** the PC lanes' Hermes session store (`state.db`
  `messages.content`, every session under `.lanes/`; reasoning and tool-call columns excluded): tool results
  123.3 MB of 137.0 MB = 90.0 % (37,858 messages), assistant 3.96 MB = 2.9 % (24,936), user 9.63 MB = 7.0 % (706);
  the coordinator's own sandbox transcript (35.3 MB): tool results 16.5 MB = 46.9 % (9,842), tool-call inputs
  13.6 MB = 38.5 %, user 10.2 %, assistant 4.0 %.


### 5.1 Spike results

Both venues ran the same script (`Agent("convaiinnovations/laya", device="cpu")`, laya 0.3.5, transformers 5.17.0,
torch 2.14.0+cpu, float32 — Laya forces float32 on CPU) over the same states: a winnow-shaped `{task, tool, blocks}`
state with a `b001` relevance noul and an `error_present` noul (2 questions), then 5 and 9 questions against the
same state. Pasted verbatim from the logs (`ms_*` = wall time of one `system_one` call over 5 repeats;
`ms_per_question` = p50 / questions; `input_tokens` = 512 per (state, question) pair as the spike counted them).

Sandbox (4 cores, 4 torch threads; `scratchpad/laya-spike.log`, done 12:02:22Z):

```json
{"load_s": 28.4, "device": "cpu", "dtype": "torch.float32", "rss_mb": 2950}
{"questions": 2, "ms_p50": 2067.8, "ms_min": 1973.2, "ms_max": 2382.4, "ms_per_question": 1033.9, "input_tokens": 1024, "b001_noul": 0.863, "error_present_noul": 0.882}
{"questions": 5, "ms_p50": 5702.5, "ms_min": 5613.6, "ms_max": 6025.0, "ms_per_question": 1140.5, "input_tokens": 2560, "b001_noul": 0.863, "error_present_noul": 0.882}
{"questions": 9, "ms_p50": 10168.8, "ms_min": 9851.2, "ms_max": 10415.4, "ms_per_question": 1129.9, "input_tokens": 4608, "b001_noul": 0.863, "error_present_noul": 0.882}
```

PC (12 cores, 6 torch threads, CPU by design — the 3090 holds 24,022 of 24,576 MiB for the vLLM `qwen` container;
`/home/rocco/laya-spike/spike.log`, done 12:03:49Z; the 83.8 s load includes the first read of the freshly
downloaded 843 MB checkpoint):

```json
{"load_s": 83.8, "device": "cpu", "dtype": "torch.float32", "rss_mb": 2884}
{"questions": 2, "ms_p50": 2387.0, "ms_min": 2343.8, "ms_max": 2538.0, "ms_per_question": 1193.5, "input_tokens": 1024, "b001_noul": 0.863, "error_present_noul": 0.882}
{"questions": 5, "ms_p50": 5159.7, "ms_min": 5107.4, "ms_max": 5219.0, "ms_per_question": 1031.9, "input_tokens": 2560, "b001_noul": 0.863, "error_present_noul": 0.882}
{"questions": 9, "ms_p50": 11154.5, "ms_min": 9387.9, "ms_max": 12628.2, "ms_per_question": 1239.4, "input_tokens": 4608, "b001_noul": 0.863, "error_present_noul": 0.882}
{"rss_mb_end": 2884}
```

What the numbers say:

- **About 1.0-1.25 s per (state, question) pair on CPU float32, on BOTH venues** — roughly 30× the upstream T4
  figure (~35 ms/question). The 12-core PC is no faster than the 4-core sandbox: each pair is one 512-token
  encoder pass, and float32 matmul on 4-6 threads is the floor.
- **Batching did NOT amortize:** per-question time is flat from 2 to 9 questions (1034 → 1130 ms sandbox,
  1194 → 1239 ms PC). N questions cost N encoder passes; on CPU the FLOPs are the cost, so only a lower
  precision (int8/bf16 export), a shorter state, fewer questions, or the GPU changes it — a research-prompt question.
- **The outputs are identical across venues and repeats** (b001 0.863, error_present 0.882 in every line): the
  decision is deterministic for a fixed (state, question) — the ledger's replay premise holds for Laya.
- **Memory:** ~2.9 GB RSS per loaded English checkpoint; the sandbox has 15 GB, so one worker per checkpoint
  fits beside the coordinator's tools; the HF cache costs 808 MB per checkpoint.
- **The GPU path on the PC is CLOSED today:** 554 MiB headroom; Laya needs ~1.7 GB (fp16) to ~3.4 GB (fp32)
  of VRAM; only the owner's `gpu_memory_utilization` change plus a vLLM restart (never the coordinator's) opens it.

## 6. Capability ledger (proven-live / built-never-run / absent)

| Capability | State | Evidence |
|---|---|---|
| Laya weights downloadable, loadable and answering on CPU — sandbox AND PC | PROVEN-LIVE on both venues (2026-09-22 spike, §5.1): ~1.0-1.25 s per question float32, ~2.9 GB RSS, deterministic outputs; the install proven (torch 2.14.0+cpu, transformers 5.17.0, laya 0.3.5) | `laya-spike.log`, `/home/rocco/laya-spike/spike.log` |
| A decide HTTP endpoint (`{state, questions} → {answers}`) | ABSENT everywhere (laya ships none; jevcache expects one) | laya evidence §6 |
| A Claude Code result-rewriting hook in this sandbox | ABSENT (function hooks not enabled; no plugin installed) | our-side T1 |
| A Hermes result-rewriting seam | ABSENT as a hook: `post_tool_call` is an observer whose return is ignored; `pre_tool_call` can block / MODIFY / approve the tool input — the seam is a command REWRITE (`terminal` command → a wrapper that runs it and returns pruned stdout), not a result hook | `harness-ports/bin/hermes-hook-adapter.py:17-19,130-133`; `harness-ports/hermes/config-snippet.yaml:110-143` |
| A decision ledger with replay | ABSENT (D-041: first-party to build) | jevcache evidence |
| Calibration data for our tool outputs | ABSENT — but the raw material exists: `transcripts/pc/*.md`, the Hermes `state.db` messages table, the sandbox transcript JSONL | our-side T1 #10, #19 |
| Typed-decision constants in skills | ABSENT | the TypeSafe skill's "single reviewed file" rule |

## 7. Constraints (settled; not open to the research)

1. **No model judge in the gate spine** (`.claude/skills/anti-hollow-green/SKILL.md:120-121`, D-031). A System One
   judgment prunes, ranks, triages and routes; it never decides a green, a mint, a verdict or a ledger row. A wrong
   judgment must be recoverable (cached full text + recall; an archive path; a "kept" default under uncertainty).
2. **Rule 3:** the hosted TypeSafe API and `TYPESAFE_API_KEY` are not production dependencies. The backend is the
   self-hosted Laya. (Development-time experiments against the hosted API are the owner's call and stay out of
   Hermes, the evaluators and the lanes.)
3. **Rule 13 / S0-12:** every upstream pinned by commit or digest in `upstream.lock.yaml`; the Laya checkpoints
   pinned by their HF revision SHA and file sha256; the unlicensed jevcache binary is out (D-041).
4. **Rule 11:** the decide service binds loopback (sandbox) or the bridge/tunnel with a token (PC); no new egress.
5. **Errors are never hidden** (winnow's rule, adopted): any output the judge marks as showing an error, and every
   protected diagnostic/result line class jev-pruner enumerates, passes through untouched.
6. **The deterministic digest, not an LLM summary, is the default stub** (no summarizer key, no extra model call);
   an LLM summary is an opt-in later.
7. **Everything measured before it hides anything:** ECE and regret on our own labeled tool outputs; a
   needle-retention oracle (substring, deterministic); a lane A/B on tokens and wall time.

## 8. Where a System One judgment fits (ranked; A–D are the build, E is bounded, F is excluded)

- **A. The sandbox tool-output sieve.** A fork of winnow with a `laya` judge backend, the deterministic digest,
  the recall tool, and the function-hook plugin enabled here. Value: every large Read/Bash/Grep result the
  coordinator sees. Risk: low (recoverable, errors never hidden).
- **B. The Hermes-lane sieve (the Qwen cost).** The portable core (jev-pruner's `trimOutput` or winnow's
  sidecar) behind a `terminal` command wrapper, wired by the `pre_tool_call` MODIFY seam so every lane command is
  wrapped mechanically — not by asking the model to wrap it. The pruned stdout + an archive path return to the
  lane; the full output stays on disk under the lane dir. This is the integration that attacks the 4-6 h lanes.
- **C. Relevance ranking for injected context.** `wiki-context.py` (lexical today) and the lane pack's `head -N`
  caps become judge-ranked top-k with a fixed budget; winnow's prompt-time memory ranker is the template.
- **D. Typed-decision constants in skills.** The advisory classifications T2 lists (scout roles, reviewer
  severity, bug-echo breadth routing, prism triage ordering) become questions + thresholds in ONE reviewed file
  per skill, answered by the decide service, with the LLM keeping the judgment-heavy parts.
- **E. Bounded: the code-intel quartet.** A `noul` per graft/GitNexus/ripwire hit ("does this hit bear on the
  question?") to rank packs — only after A–C prove the judge on our data.
- **F. Excluded:** every T3 gate; the dispatcher's lane-state regexes; anything that writes a ledger, a mint, a
  verdict or a report class.

## 9. Design sketch (the settled direction; the technical resolution is the research prompt's job)

1. `decide` service (first-party, Python, stdlib HTTP + laya): loopback `POST /v1/systemone` (TypeSafe-shaped
   `{model, state, questions}` → `{model, answers, usage}`, so the vendored skill, winnow, jev-pruner and the
   TypeSafe SDK's `base_url` all fit) and `POST /v1/decide` (jevcache-shaped); ONE worker per loaded checkpoint
   behind a queue (Laya's `Agent` is not thread-safe); token-length guard that CHUNKS instead of letting Laya
   truncate; health + version endpoints; pinned checkpoint SHAs; a bearer token when bound beyond loopback.
2. Ledger (first-party): canonicalize + redact the state → sha256 with a per-schema salt → append-only JSONL;
   `decide` (recall then compute), `recall` (never computes; exit 3 on a miss), `replay` fixtures for CI drift.
3. Sieve A (sandbox): winnow fork, `WINNOW_JUDGE=laya` → the decide service; function hooks enabled in this
   sandbox's settings; the skill vendored with it.
4. Sieve B (Hermes lanes): the wrapper + the `pre_tool_call` modify hook, the archive under the lane dir, the
   dispatcher's harvest ignoring archives.
5. Calibration harness: label ~300 real blocks from our transcripts, ECE / AUC / regret per threshold, needle
   tests; thresholds live in one constants file; the A/B on a real lane (tokens in, wall time, verify outcome).
6. Skills wiring: the typed-decision constants files, CLAUDE.md's advisory-instrument rule extended, the
   `typesafe-ai` skill adapted with a "local Laya" section.

## 10. Risks and open technical questions (each goes to the research prompt with a decision rule)

- Accuracy on OUR distribution is unknown; the upstream headline is not reproducible. Decision rule: adopt a
  threshold only from our labeled set; if ECE > 0.25 or regret > 2 % at the chosen drop threshold, the sieve runs in
  shadow mode until a calibration or fine-tune fixes it.
- CPU latency is MEASURED at ~1.0-1.25 s per question float32 on both venues (≈30× the T4 figure) and batching
  did not amortize it (§5.1). Decision rule: a judged tool call adds at most ONE question's latency on the
  synchronous path (one whole-output question, ≤ 1.3 s); per-block questions run asynchronously or on a
  lower-precision export (int8/bf16 ONNX or torch quantization) whose accuracy is re-measured on our labeled set
  before it replaces float32; if no export reaches ≤ 300 ms/question on 4 cores, per-block sieving is PC-only.
- Truncation at 512/1024 tokens: the state design (task + tool + block) must fit; long blocks are split.
- Thread safety and reloads: one process per checkpoint; the typed-decisions checkpoint's temperature clamp
  warnings are logged, not hidden.
- Function hooks are early-access in Claude Code; the plugin surface can move under us — pin the CC version in
  the plugin's README and keep the sidecar harness-free.
- Hermes's `pre_tool_call` modify shape must be read from the pinned Hermes source, not assumed.
- The GPU path on the PC is closed by measurement (554 MiB free of 24,576 MiB while vLLM holds the card); CPU is
  the default on both venues; the GPU path opens only by the owner's own vLLM change and restart.

## 11. NOT built / not done (honest ledger)

No decide service, no ledger, no sieve, no hook enabled, no skill wiring, no calibration set, no upstream.lock
pins, no PC service — nothing beyond the audit, the vendored skill and the two measurement venvs. The Aegis
repository stays unadopted. The jevcache binary was never fetched.
