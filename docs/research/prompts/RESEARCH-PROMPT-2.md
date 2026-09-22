# RESEARCH-PROMPT-2 — TYPED DECISIONS: how do we put an open 421M-parameter System One model (Laya) to work as an ADVISORY relevance sieve, ranker and typed-decision oracle across a two-venue agent factory — cutting the tokens that reach the expensive coordinator and the slow local builder — without the model ever deciding a gate?

> **At a glance:** Agent Factory is a planning-stage repo for a governed agent system, built today by an
> autonomous coordinator (a frontier model in a cloud sandbox: 4 cores, 15 GB RAM) that dispatches long
> "lanes" (100-250 tool calls each) to a LOCAL Qwen3.8-27B served by vLLM on the owner's PC (Fedora 42, 12 cores,
> 125 GB RAM, one RTX 3090) behind OmniRoute. Two measured facts drive this brief: (1) tool output is the bulk
> of every context — 90.0 % of the bytes stored for the PC lanes and 46.9 % of the coordinator's own transcript
> — and NOTHING prunes it today; (2) a build lane takes 4 h 53 m to 6 h 41 m of wall clock, and the coordinator's
> tokens are the most expensive resource in the project. The owner has decided to integrate a "Jev-class"
> typed-decision model (TypeSafe's System One: typed questions over a JSON state, answered with calibrated
> probabilities in one forward pass) using its open counterpart **Laya** (Apache-2.0, 421M, weights public),
> self-hosted on BOTH venues, with a FIRST-PARTY decision ledger, as an ADVISORY layer only.
> Status: RESEARCH ONLY — nothing is built until findings return, pass a council, and are measured.
> Tracker: task `jev-laya-integration-audit` (#104 in the session task DB; the ledger row in
> `todo/BUILD-TASKLIST.md`); the grounded audit is `docs/research/findings/JEV-LAYA-AUDIT-2026-09-22.md` with five
> evidence reports under `docs/research/findings/jev-audit/`.
> Mode: SETTLED-SPEC — the strategic answer is decided (below, §3); only the technical resolution is open.
> Council (RESEARCH-PROMPT-GUIDE step 1.5): runs on the RETURNED findings, never `--quick`, before any seed.
> This prompt is self-contained: every fact the research needs is inline; the file paths are for the
> coordinator's later verification, not for the researcher to open.

## 1. The measured problem (verify these numbers — do not re-derive them from priors)

**Where the bytes go (measured 2026-09-22).**

- The PC lanes' Hermes session store (`~/.hermes/profiles/agentfactory/state.db`, every session under
  `.lanes/`, the `content` column only — reasoning and tool-call columns excluded): **tool results 123.3 MB of
  137.0 MB = 90.0 %** (37,858 tool messages), assistant text 3.96 MB = 2.9 % (24,936 messages), user/prompt
  text 9.63 MB = 7.0 % (706 messages). Every one of those tool-result bytes re-enters the local model's context
  on every following turn until compaction.
- The coordinator's own session transcript (one sandbox session, 35.3 MB): **tool results 16.5 MB = 46.9 %**
  (9,842 results), tool-call inputs 13.6 MB = 38.5 % (the coordinator's own file writes and scripts), user
  text 10.2 %, assistant text 4.0 %.
- **Nothing prunes tool output in either venue.** Inventory (19 sinks audited): the Claude Code Bash tool feeds
  the coordinator's context unbounded (no PostToolUse hook registered for Bash; the only compressor is the
  vendored "honey" plugin's log-compress hook, which is INERT here — its `~/.claude/.honey-active` gate file does
  not exist — and upstream Claude Code drops a hook's `updatedToolOutput` rewrite for the built-in Bash tool on
  affected builds, anthropics/claude-code#68951); `scripts/test_summary.sh` prints WHOLE pytest runs
  (1,556+ tests) before its two mechanical summary lines; a Hermes `terminal` call inside a PC lane has NO byte
  cap (its cap is time: 420 s); the lane prompt is ~47 KB and the per-call system prompt was 81 KB before a
  skill-index fix. The bounded sinks that do exist are `head`-style caps in scripts (orient, wiki-context,
  lane_context pack, lane_gate, pc_suite) — fixed truncation, not relevance.
- **Lane wall clock.** One build lane: 4 h 53 m (effort `medium`, 386k output tokens, 243 tool calls) to
  6 h 41 m (`xhigh`, 694k) on the same brief; a verify lane about the same; every proof needs several
  build→verify rounds. The local server (vLLM, Qwen3.8-27B) batches to ~310 tok/s aggregate at 7 lanes; four
  local lanes run at once. The owner's words: "the Qwen builder is slow as hell … offload the long menial steps".
  A System One model cannot execute steps; it can decide WHICH bytes a step needs to read and classify what a
  step produced — the throughput lever is fewer and shorter model turns, not a second executor.

**What Laya measures like (the spike, 2026-09-22, both venues, the same script).** `laya` 0.3.5,
`transformers` 5.17.0, `torch` 2.14.0+cpu, float32 (Laya forces float32 on CPU), the English 421M checkpoint,
a winnow-shaped `{task, tool, blocks}` state with a `b001` relevance noul and an `error_present` noul, then 5
and 9 questions over the same state; five repeats each, p50 wall time of one `system_one` call:

| venue | threads | load | RSS | 2 q | 5 q | 9 q | ms / question |
|---|---|---|---|---|---|---|---|
| sandbox (4 cores) | 4 | 28.4 s | 2,950 MB | 2,068 ms | 5,703 ms | 10,169 ms | 1,034-1,141 |
| PC (12 cores, CPU by design) | 6 | 83.8 s (first read of the fresh 843 MB download) | 2,884 MB | 2,387 ms | 5,160 ms | 11,155 ms | 1,032-1,239 |

Facts the table proves: ~1.0-1.25 s per (state, question) pair on CPU float32 on BOTH venues (about 30× the
upstream T4 figure of ~35 ms); the 12-core box is no faster than the 4-core one (each pair is one 512-token
encoder pass; float32 matmul on 4-6 threads is the floor); **batching does NOT amortize** (per-question time is
flat from 2 to 9 questions — N questions cost N passes); the outputs are bit-identical across venues and repeats
(b001 0.863, error_present 0.882 in every run — the decision is deterministic for a fixed input, so a ledger can
replay it); ~2.9 GB RSS per loaded checkpoint. **The PC GPU path is CLOSED by measurement:** the RTX 3090 holds
24,022 of 24,576 MiB for the vLLM container; Laya needs ~1.7 GB (fp16) to ~3.4 GB (fp32); only the owner's own
change to vLLM's memory share and a restart (never the coordinator's) opens it.

**What Laya claims vs what it committed.** The README's typed-decisions accuracy headline is 0.766; the
repository's committed measurement is **0.362 (n = 2,000, ECE 0.17)** with no committed producer for the
headline. Its own CPU latency sweep claims 100-300 ms per one-question call on 4 threads — not reproduced here
(see the table). States longer than the checkpoint's window (512 tokens English, 1,024 multilingual and
typed-decisions) are SILENTLY right-truncated by the library. So: every judgment must be measured on OUR
distribution before it hides a byte, and the model never decides a gate.

**The decisions a model makes in this repo today (17 audited rows; the candidates are marked).** Gate
recommendation of a verify lane (`MERGE-READY` / `-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`) — NOT a
candidate, the coordinator owns the gate and the lane's report is archived evidence · per-finding class
(`BLOCKER`/`FOLLOW-UP`/`INFO`/`UNVERIFIED`) and the five-condition blocking predicate — NOT candidates (gate-adjacent:
the verifier's mutant set becomes the next repair brief's bar) · a build lane's premise true/false and its
"did I reverse a conclusion" escalation — NOT candidates (bounded to three experiments; they produce a
DISCREPANCIES entry) · **hive-reviewer's per-finding severity `H|M|L` + kind slug (Haiku today) — CANDIDATE** ·
**hive-scout's per-hit role `def|caller|config|test|other` (Haiku) — CANDIDATE** · the subagent WORKER/REVIEWER
directive — a regex, stays a regex · **bug-echo's six-dimension rating per finding (Urgency, Risk of Fixing, Risk
of Not Fixing, ROI, Blast Radius, Fix Effort → BUG/OK/REVIEW/WATCH; the coordinator today) — CANDIDATE as advisory
`score` questions; the registry row itself stays a human/coordinator decision** · **bug-echo's breadth routing on
candidate count — CANDIDATE** · prism findings tables (LLM analysis, explicitly advisory) — not a candidate (a
different task shape) · **wiki-context's relevance choice of ≤ 3 pages — today a lexical score (headings ×3, stem
×2, text ×0.1, top-3) — CANDIDATE for a Laya re-rank of the lexical top-10** · graft-first nag ("is this Grep a
semantic identifier search?") — a regex, stays · the turn-retro five questions — the coordinator's · lane state
READY/RUNNING/FAILED and refusal class — regexes on the report's first bytes + pidfile + mtimes, stay (artifact-
landing decisions) · the offload map's "what still costs coordinator tokens" — prose · the chat-format switch —
reflexive, no code.

**The gates that must stay model-free (15 rows, the protected set):** `report_lint.py` (token-in-cited-lines,
`--min-refs` floor), `ap_screen.py` (regex anti-pattern screen), `lane_gate.sh` (static-copy identity table + N
agreeing runs + one RESULT line), `test_summary.sh` (pasted counts), `pc_suite.sh` (`pytest-set:` id + the
no-`passed`-count RED rule), `validate-ledger` (schema + canonical digest + per-file sha256 attestation →
PRESENT/INVALID), `proof-runner` (per-leg stdout/stderr sha256), the seed's frozen `spike_to_class_mapping`, the
dispatcher's premise gate (rc 64) and headroom admission, the pre-commit gates (pyflakes delta, anchor, skill-sync,
mirror, lane-skills, shell syntax), `push_clean.sh` (tree identity across the rewrite, zero trailers, push the
rev-parsed SHA), the lane's git/gh shim (exit 13), `lane_context.sh`'s refusals. A Laya answer may be an INPUT a
human or the coordinator reads; it is never a term in any of these predicates.

## 2. Current-state capability ledger (proven-live vs built-never-run vs absent — do not re-derive)

| Capability | State | Evidence |
|---|---|---|
| Laya weights downloadable, loadable and answering on CPU — sandbox AND PC | PROVEN-LIVE 2026-09-22 (the table above) | the two spike logs |
| A decide HTTP endpoint (`{state, questions} → {answers}`) on either venue | ABSENT (Laya ships no server, no CLI, no quantized export; jevcache expects one and ships nothing) | audit §6 |
| A result-rewriting hook in the sandbox's Claude Code (2.1.278) | ABSENT — function hooks (CC ≥ 2.1.260, `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS`) are NOT enabled; no plugin rewrites Bash output; the honey compressor is inert | our-side inventory T1 rows 1-3 |
| A Hermes result-rewriting seam for the PC lanes | ABSENT as a hook: Hermes's `post_tool_call` is an OBSERVER whose return value is ignored (our adapter spools its output to a file and injects it at the NEXT turn's `pre_llm_call`, or discards it with a stderr line); `pre_tool_call` can block / MODIFY / approve the tool INPUT — so the only live seam is a command REWRITE (the `terminal` command → a wrapper that runs it and returns pruned stdout). The adapter itself is unit-proven in the sandbox and NOT smoke-tested on the PC | `harness-ports/bin/hermes-hook-adapter.py`, `harness-ports/hermes/config-snippet.yaml`; `docs/HARNESS-PORTS.md` |
| A decision ledger with replay | ABSENT (D-041: first-party to build; jevcache rejected) | audit §7 |
| Calibration/labeled data for OUR tool outputs | ABSENT — but the raw material exists: the Hermes `messages` table (37,858 tool results with the assistant turns that followed them), the sandbox transcript JSONL (9,842 results and every later file:line the coordinator cited), `transcripts/pc/*.md` | audit §6 |
| Typed-decision constants in skills (one reviewed file per skill) | ABSENT | the vendored TypeSafe skill's rule |
| The official Jev agent skill | VENDORED verbatim (`.claude/skills/typesafe-ai/`, MIT, typesafe-ai/skills @ 65a39f3) — the owner "had one then lost it" | commit 260aab3 |
| A GPU for Laya on the PC | CLOSED (554 MiB headroom) | `nvidia-smi` 2026-09-22 |
| Any of jevcache / jev-pruner / winnow / Aegis installed | NONE — cloned and read only | audit §3 |

## 3. SETTLED (guardrails only — NOT the solution; do not reopen)

1. **No model judge in the gate spine (NON-NEGOTIABLE).** A Laya/Jev judgment is ADVISORY: it ranks, filters,
   classifies and flags; it never decides a green, a mint, a lint verdict, a lane state, a push, a commit gate or
   a proof class. The protected set in §1 stays exactly model-free. A dropped or summarized block is always
   recoverable from the original bytes on disk. (Rejected alternative: "use the model's confidence as a gate
   threshold" — rejected; so is any LLM-as-judge in a gate.)
2. **The model is LOCAL on each venue and makes no network egress.** The decide service is a loopback process
   (127.0.0.1) on the sandbox and on the PC, one per venue, the SAME code; model bytes come from a ONE-TIME pinned
   download verified by SHA-256 (the checkpoint SHAs, the `laya` package version and the upstream commit go in
   `upstream.lock.yaml` — every upstream pinned by immutable commit or digest is a standing project rule). The
   hosted TypeSafe API (`POST https://api.typesafe.ai/v1/systemone`, SDK `typesafe-sdk` 0.7.1) is permitted ONLY
   as a coordinator-run comparison instrument during calibration; no hosted key ever reaches Hermes, a lane, an
   evaluator or a production path (standing rule 3: OmniRoute is the sole model-API egress; no direct provider
   credentials anywhere). The decide service is a local classifier, not a model-API egress, and it must be
   describable as such: no outbound sockets, ever (a test proves it).
3. **Both venues (owner decision D-040):** sandbox CPU float32 today (4 cores, 15 GB, ~4 GB disk free after the
   spike's venv and cache); PC CPU (12 cores) by default; the PC GPU path only when the owner frees headroom.
   Process model: one worker per loaded checkpoint behind a queue; the English 421M checkpoint is the default;
   the typed-decisions and multilingual checkpoints only after they measure better on our labeled set.
4. **The decision ledger is FIRST-PARTY (owner decision D-041):** every answer recorded with the canonical state
   digest, the question, the typed answer, its probabilities, the model id + checkpoint SHA + export id, latency,
   venue and a timestamp; replay = the same digest + checkpoint + export returns the recorded answer WITHOUT a
   forward pass (bitwise-equal by the determinism measured above). Secrets never enter the ledger: redaction of
   the known secret classes (`sk-…` API keys, `BUZZ_PRIVATE_KEY=` values, bridge tokens, `.secrets/*.env`
   contents) happens BEFORE the state is built and digested. (Rejected: the `jevcache` binary — README-only, no
   source, no license, no checksum.)
5. **Fail-open, loud, and recoverable, for every advisory path** (winnow's rules, adopted): if the service is
   down, slow or errors, the tool output passes through UNCHANGED with a one-line marker; an error in the tool
   output is NEVER hidden (an `error_present` noul or a deterministic error-signature scan keeps such blocks); a
   dropped block is recoverable by id from the original bytes (a recall path); thresholds (winnow's keep ≥ 0.5 /
   drop < 0.1 are the starting shape) are adopted only from OUR calibration, never from upstream defaults.
6. **The integration points are SETTLED as an ordered list; the research resolves each, it does not re-rank
   them:** **A** the sandbox sieve — a winnow-shaped block-level relevance sieve over Bash/tool results feeding
   the coordinator, with a `laya` judge backend (winnow's `Judge` protocol: `nouls(state, questions) →
   JudgeResult`; backends today `typesafe | adapter | off`), forked, not rewritten; **B** the PC-lane sieve — the
   same sieve behind the Hermes `pre_tool_call` MODIFY seam as a command wrapper (`terminal` command →
   `sieve-run -- <cmd>`), preserving exit code, stderr and timing byte-for-byte on a no-op judge; **C** relevance
   ranking for injected context (wiki-context's top-10 → top-3, orient's tails, the lane_context pack); **D**
   typed-decision constants in skills — the candidate rows of §1, each skill's questions in ONE reviewed file
   (the TypeSafe skill's rule) invoked through one CLI; **E** bounded ranking of the code-intel quartet's result
   lists (graft hits, GitNexus impact rows, code-review-graph callers, codebase-memory search) — a ranked VIEW
   beside the instruments' raw output, never a replacement; **F** EXCLUDED: the protected gate set.
7. **Measurement before adoption, shadow mode first.** Every integration ships in shadow mode (judgments
   recorded, nothing altered) until a labeled set from our own transcripts gives its numbers: calibration (ECE,
   Brier), needle retention (the share of later-cited lines that a drop would have removed), regret (a dropped
   block later needed → a recall), byte reduction, added latency. Then ONE A/B on a real lane brief (the same
   brief, the same PIN, baseline arm vs sieve arm) graded by the existing adversarial VERIFY lane — equal or
   better, or the integration stays in shadow. A threshold is never taken from upstream numbers.
8. **Unchanged invariants:** Hermes is the sole stock production runtime (no Codex CLI / Claude Code / Pi as
   parallel runtimes); OmniRoute the sole model-API egress; the owner's running services (the vLLM container, the
   Buzz relay, OmniRoute, Ollama, Phoenix, OpenObserve, neo4j) are never stopped, restarted or reconfigured by a
   lane or the coordinator; `sudo` is the owner's; the lane discipline and D-028's effort split (build `medium`,
   verify `xhigh`) stay; every acceptance test is deterministic and LLM-free (the wrapper's unit tests may use a
   fixed-answer fake judge; the integration test uses the real pinned checkpoint).
9. **Rejected, named:** jevcache; Aegis (22 skills lifted from Superpowers, governance concepts that are
   docs-only for an unbuilt "Runtime Core" — nothing our gates lack); a hosted-API dependency in production;
   fine-tuning BEFORE calibration is measured; a GPU restart by the coordinator; a sandbox model server as an
   egress; any change to the owner's OmniRoute/Hermes route configuration for this feature; "drop by default"
   thresholds; letting the sieve touch a gate script's stdout (the gates' own outputs are exempt from sieving).

## 4. Preliminary findings — INLINE. VERIFY, DEEPEN, CHALLENGE; do not re-derive.

- **F1 — Laya (NandhaKishorM/laya, Apache-2.0; Hugging Face `convaiinnovations/laya`).** Three checkpoints:
  English ModernBERT-large 421M (`model.safetensors` 843 MB, 512-token window), multilingual mmBERT-base 322M
  (`multilingual/`, 644 MB, 1,024), typed-decisions 421M (`typed-decisions/`, 843 MB, 1,024). API:
  `Agent("convaiinnovations/laya", device=…)`, `Agent.system_one(state, questions)` →
  `{"model": "laya-rl-agent", "answers": {qid: {type, noul|choice|score, probabilities, confidence, action}},
  "usage"}`; also `Router.predict`. Question schema `{"type": "choice"|"score"|"noul", "instructions",
  "criteria"}`. CPU is forced to float32; there is no server, CLI, ONNX or quantized export; truncation is silent;
  the training recipe is RLCD-style. Committed accuracy 0.362/ECE 0.17 for typed decisions (README 0.766, no
  producer). Thread-safety and reload behaviour are undocumented; the typed-decisions checkpoint logs
  temperature-clamp warnings.
- **F2 — TypeSafe System One (the reference "Jev").** `POST https://api.typesafe.ai/v1/systemone` with
  `{state, questions}` → `{answers}` (the same shape Laya returns); `typesafe-sdk` 0.7.1 takes `base_url` from
  `TYPESAFE_ENDPOINT`/`TYPESAFE_BASE_URL`, so a local service with the same path is a drop-in for SDK users;
  `system-one-adapter` 0.2.0 exists. The official agent skill's rules: the state is compact JSON of only what
  the question needs; questions are typed with `instructions` + `criteria`; a `noul` is a yes/no probability;
  all of a skill's decisions live in one reviewed file; code owns the workflow, the model supplies narrow
  judgments. Docs (`docs.typesafe.ai`, `llms.txt`, `.md` twins of every page) are saved with the audit.
- **F3 — winnow (GhalebDweikat/winnow).** A Claude Code sieve: function hooks (CC ≥ 2.1.260) rewrite tool results;
  a sidecar `winnow serve` on `127.0.0.1:47311`; blocks of ~25 lines; state
  `{task: {user_request, assistant_intent}, tool: {name, input}, blocks: {b001: …}}`; the per-block question
  "Would the assistant have to look at `blocks.bNNN` to accomplish `task` correctly?" plus an `error_present`
  noul; keep ≥ 0.5, drop < 0.1, the middle summarized (an optional Haiku summarizer); errors never hidden; a
  deterministic digest fallback when the judge is off; a `winnow_recall` MCP tool returns dropped blocks by id;
  judge backends `typesafe | adapter | off` via `WINNOW_JUDGE`. This is the design to FORK: add a `laya` backend
  (in-process or the local HTTP service), keep the state and question shapes, re-derive the thresholds.
- **F4 — jev-pruner (tamaratran/jev-pruner).** A `tool.call` hook that rewrites Bash results through the hosted
  API (`SYSTEM_ONE_URL` is a constant; the `baseUrl` parameter is unused — a local endpoint needs a one-line fix);
  a 10,000-token floor below which nothing is pruned; a portable core `trimOutput(input, asker, options)`; the
  Codex path is a model-invoked wrapper (the model must choose to call it). Useful as the FLOOR pattern (do not
  judge small outputs) and as the explicit-wrapper shape for venues without hooks.
- **F5 — jevcache (hyperspaceai/jevcache).** README-only: a cache/ledger in front of a System One endpoint with
  a local backend contract `JEVCACHE_LOCAL_URL=http://127.0.0.1:8080/v1/decide`, `{state, questions} →
  {answers}`. No source, no license, no checksum → rejected (D-041); its endpoint CONTRACT is worth honouring so
  the first-party service serves both `/v1/systemone` (TypeSafe-shaped) and `/v1/decide` (jevcache-shaped).
- **F6 — Aegis (GanyuanRan/Aegis).** Not adopted (§3.9).
- **F7 — our seams.** Sandbox: Claude Code 2.1.278; hooks registered in `.claude/settings.json` (PostToolUse
  for Edit/Write/Read only); the honey plugin enabled but its compressor inert; function hooks not enabled;
  MCP tools bind at user scope on the next session start (CCR sessions often drop MCP — a CLI is the reliable
  path in this project). PC: Hermes-agent 0.21.0 (pinned commit `527da60844d4dced37879ea50259675371abe10e`,
  MIT) with our hook adapter (`pre_llm_call` inject, `pre_tool_call` block/MODIFY/approve, `post_tool_call`
  observe-only); a lane runs `hermes -z "<prompt>"` from a private worktree; its `terminal` tool has a 420 s per-
  call cap; the lane's git/gh are shimmed. The dispatcher (`scripts/pc_lane.sh`) admits four local-route lanes
  launched 60 s apart.
- **F8 — the spike** (§1 table): ~1.0-1.25 s/question CPU float32 both venues; no batching gain; deterministic;
  ~2.9 GB RSS; HF cache 808 MB per checkpoint; the sandbox venv 1.2 GB.
- **F9 — labels exist in the record.** For the coordinator's sieve: every tool result in the transcript JSONL is
  followed by the coordinator's later citations (`file:line`, quoted lines, the values it pasted) — a block is
  "needed" if any later assistant text or tool input references a line or token from it. For the lane sieve: the
  same over the Hermes `messages` table (tool result → the assistant's next `tool_calls` and text). For the
  lane_context pack: the verify lane's cited `file:line` refs (the report lint already extracts them).
- **F10 — cost sinks already quantified in-repo:** the ~47 KB lane prompt; an 81 KB system prompt per call
  before the 472-skill-index fix; the whole-suite `test_summary.sh` output; a ~45 KB bridge reply cap that
  forces report slicing; hook output on an observer event spooled to the NEXT turn.

## 5. Open questions (bounded — each carries its settled direction and its decision rule; evaluate ALL)

**Q1 — State and question design under a 512/1,024-token window (chunking).** Settled: the winnow state shape
and per-block question; blocks of ~25 lines; the English checkpoint's 512 tokens is the window that must hold
`task + tool + one block + the question`. Open: the exact budget split (task summary ≤ N tokens, block ≤ M),
whether a block is judged alone or with its neighbours' ids, how a 40,000-line pytest log is chunked and judged
in bounded time, whether the 1,024-token checkpoints are worth their lower committed accuracy for long blocks,
and how the state is canonicalized so the ledger digest is stable (sorted keys, normalized whitespace, redacted
secrets). Decision rule: the design with the best needle retention at equal byte reduction on the labeled set;
if no design keeps ≥ 0.98 needle retention at ≥ 40 % byte reduction, the sieve ships in summarize-and-keep mode
(nothing dropped) and the report says so.

**Q2 — Calibration vs fine-tuning.** Settled: calibrate FIRST on our labeled set (temperature scaling, Platt or
isotonic per question type), thresholds from the calibrated curve; fine-tuning (Laya's RLCD recipe on our pairs)
only after. Open: the sample size that makes ECE trustworthy per question type (a power estimate), the split
(by lane, never by block), which of the three checkpoints starts best on our distribution. Decision rule:
fine-tune only if ECE > 0.15 after calibration AND ≥ 2,000 labeled pairs exist; a fine-tuned checkpoint is
pinned by SHA, evaluated on a held-out lane set, and replaces the base only if needle retention and ECE both
improve; otherwise the base stays and fine-tuning is the next prompt.

**Q3 — Serving on 4 CPU cores (the sandbox floor) and on the PC's CPU.** Settled: one worker per checkpoint
behind a queue, warm start ≤ 30 s, `POST /v1/systemone` + `/v1/decide`, no outbound sockets. Open: the
lower-precision export that beats float32 — ONNX Runtime int8 (dynamic quantization of the ModernBERT linear
layers), torch dynamic int8, bf16 on CPU, OpenVINO — with the expected speedup on 4 threads and the accuracy
delta; whether a shared-encoder batch (one padded batch of many (state, question) pairs through the model) helps
on CPU at all (the spike says N passes cost N times; verify from the library's forward path); thread pinning
and `OMP_NUM_THREADS`; the memory budget (two checkpoints loaded = ~6 GB of the sandbox's 15). Decision rule:
adopt the fastest export whose answers agree with float32 within ±0.02 mean absolute probability on the labeled
set AND whose p50 ≤ 300 ms/question on 4 cores; if none does, float32 stays, the synchronous path judges ONE
whole-output question (≤ 1.3 s), and per-block sieving runs asynchronously or PC-only.

**Q4 — The Hermes seam for the PC lanes (integration B).** Settled: the `pre_tool_call` MODIFY of the
`terminal` command into `sieve-run -- <original command>`; the wrapper runs the command, judges its stdout,
returns the pruned stdout with the dropped-block ids and a recall hint, and preserves the exit code, stderr and
timing exactly. Open: the exact MODIFY payload shape in hermes-agent 0.21.0 (READ the pinned source; the
adapter's config snippet shows block/modify/approve); how an interactive or backgrounded command, a pipeline
with `${PIPESTATUS}`, a `cd` chain, a heredoc, and the 420 s cap behave under the wrap; whether the lane's own
gate scripts (`lane_gate.sh`, `test_summary.sh`, `report_lint.py`, `ap_screen.py`) must be exempted by name so a
pasted count is never a pruned count; and the 10,000-token floor (jev-pruner) vs a line floor. Decision rule:
the seam that passes a deterministic byte-for-byte test on a no-op judge (exit code, stderr, stdout order,
timing within 5 %) is adopted; if the MODIFY path cannot preserve one of those, integration B becomes a post-hoc
pack (the sieve summarizes the lane's report INPUTS instead of live results) and the report says so.

**Q5 — The sandbox seam for the coordinator (integration A).** Settled: winnow's design; the explicit wrapper
(`sieve-run -- <cmd>`, callable by the coordinator by hand) ships regardless as the floor. Open: which mechanism
actually rewrites a Bash result in Claude Code 2.1.278 — function hooks (`CLAUDE_CODE_ENABLE_FUNCTION_HOOKS`)
vs PostToolUse `updatedToolOutput` (dropped for built-in Bash per anthropics/claude-code#68951) vs an MCP tool
the coordinator calls instead of Bash — with a primary source for each; the sidecar's lifecycle in an ephemeral
container (setup.sh starts it; the session-start hook checks it); the recall tool's shape (MCP vs a CLI that
prints the block by id). Decision rule: the seam proven by a deterministic fire/no-fire test on 2.1.278 is
adopted; if none fires for Bash, the explicit wrapper is the only sandbox integration and the report says so.

**Q6 — The ledger.** Settled: first-party, append-only JSONL per venue, replay by digest, redaction before
digest, secrets never stored. Open: the canonical JSON rules (key order, float formatting, unicode
normalization), the digest input (state + question + checkpoint SHA + export id), retention and rotation, how a
replay is proven exact (a test that replays a day of decisions and diffs bitwise), how the ledger doubles as the
labeled-set store (an outcome column filled in later from the citation labels), and its size at 40,000 tool
results a day. Decision rule: replay is bitwise-exact for the same digest and checkpoint or the ledger is not
done; a redaction miss found by the existing anti-pattern screen is a blocking defect.

**Q7 — Typed-decision constants in skills (integration D).** Settled: only the CANDIDATE rows of §1 (hive-
reviewer severity/kind, hive-scout role, bug-echo's six-dimension rating as advisory scores, bug-echo's breadth
routing, wiki-context's re-rank); each skill's questions in ONE reviewed file (`decisions/<skill>.json`), invoked
through one CLI (`decide ask <file> <state.json>`); regex-implemented decisions stay regexes; gate-adjacent
decisions stay with the coordinator. Open: the question wording and criteria per row, the labeled-set recipe
per row (≥ 200 examples from landed work), whether Laya replaces the Haiku hive tier for classification (cost
per call vs ~1 s latency) or pre-filters its input, and how a skill's markdown declares "this step is a typed
decision" so the Hermes and Claude Code ports of the skill both route it. Decision rule: a row moves to Laya
only when its labeled set shows agreement with the coordinator's later judgment ≥ the current mechanism's; a
row that cannot be labeled from the record stays as it is.

**Q8 — Ranking the code-intel quartet's output (integration E).** Settled: the instruments' raw output is always
written to disk; the ranked view is an addition capped at a fixed size; a `score` question per row against the
brief's question. Open: the state for a row (the hit's file, symbol, snippet, the brief's question), how many
rows a pack can afford at ~1 s each (the pack is built once per brief — a 200-row pack is 200 s; the budget), and
the retention metric (the lines the lane later cited). Decision rule: adopt only if the ranked pack at 50 % of
the raw size keeps ≥ 95 % of the lines the lane later cited, measured on ≥ 10 landed lanes; otherwise E stays
unbuilt and the report says so.

**Q9 — The evaluation harness and the labeled-set recipe.** Settled: the metrics (ECE, Brier, needle retention,
regret, byte reduction, added latency), labels from the record (F9), shadow mode, the single lane A/B graded by
the existing verify lane. Open: the exact label extraction (what counts as "cited": a file:line, a quoted line,
a pasted value, a symbol name?), the minimum set size per integration, the shadow-mode duration, and the A/B's
acceptance numbers. Decision rule: as §3.7 — equal-or-better grade and ≥ 30 % fewer input tokens on the sieve
arm, or the integration stays in shadow.

**Q10 — The PC deployment.** Settled: a user-level systemd unit (`laya-decide`) on loopback, CPU, ~3 GB RAM per
checkpoint, started at boot after the lane user's session, the same code and config file as the sandbox; the
vLLM container untouched; the sandbox does NOT reach the PC's service (each venue runs its own). Open: the
install/guard pattern (mirror the existing `qwen-server.sh` install + side-effect-free guard), the health check
the dispatcher reads before admitting a sieved lane, log rotation, and what happens to a live lane when the
service restarts (fail-open by §3.5, proven by a test). Decision rule: one config file, one unit, one health
endpoint; a lane never blocks on the service.

**Q11 — The "menial steps" question, bounded.** Settled: Laya judges, it does not execute. Open: from the lane
record, WHICH lane steps are dominated by reading long tool output (the candidates: reading pytest logs to find
the failing test, reading a 400-line graft pack, reading a whole file to find a symbol, reading `git log`/`diff`
output) and what share of a lane's input tokens and turns they hold — quantify from the 37,858 tool results and
name the top five by bytes and by count. Decision rule: the sieve's first target is the step with the largest
(bytes × frequency); a step whose output is a gate's pasted count is exempt.

## 6. PRIMARY DELIVERABLE (one)

**PRIORITY (SETTLED — do not ask which is primary):** the **build specification** for the first-party
typed-decision layer — precise enough that a build lane implements it without design decisions:

1. **`laya-decide`, the service:** the HTTP API (both endpoint shapes, request/response JSON, error codes), the
   process model (workers, queue, timeouts, warm start), the precision/export choice WITH its measured numbers
   (Q3), the canonical state builder and redaction rules, the ledger's format and replay contract (Q6), the two
   venue deployments (Q10), the `upstream.lock.yaml` pins (checkpoint SHAs, package versions, the upstream
   commit), and the no-egress proof.
2. **`sieve-run`, the wrapper:** the CLI contract (`sieve-run [--floor N] [--mode shadow|summarize|drop] --
   <cmd>`), the chunker (Q1), the question set, the thresholds' derivation, the recall path, the fail-open marker,
   the exempt-command list, and the byte-for-byte no-op test (Q4).
3. **The two seams:** the Claude Code mechanism (Q5) and the Hermes MODIFY payload (Q4), each with a
   deterministic fire/no-fire test and the exact primary source it was read from.
4. **The calibration harness and the labeled-set recipe** (Q2, Q9): the extraction scripts' contracts, the
   metrics' definitions, the shadow-mode protocol, the A/B protocol, and the acceptance numbers.
5. **The skills' decision-constants pattern** (Q7): the file schema, the CLI, the candidate rows with their
   question wording, and the routing rule for both harness ports.

Each item in BUILD ORDER with its acceptance test (deterministic, LLM-free; the real checkpoint only in the
integration tests) and its measurement gate. The headline is a NUMBER: the projected input-token reduction per
lane and per coordinator turn on the recommended configuration, and the added latency per judged call.

Subordinate (relationship stated):
- **The measurement protocol** [EMPIRICAL GATE — the validity gate on the primary]: the labeled-set extraction
  from the existing record, shadow-mode numbers per integration, then ONE A/B on a real lane brief graded by the
  existing verify lane.
- **The quartet ranking (E)** [downstream, bounded by Q8's rule].
- **The ceiling statement** [downstream]: what a 421M encoder with a 512-token window cannot do here (gates,
  long-state reasoning, non-English output, anything needing the file system), and the first step beyond it
  (a larger local classifier? the typed-decisions checkpoint fine-tuned? a second GPU?) with its expected gain.

## 7. What would change the plan (each with its resolution — never "come ask")

- **ECE stays > 0.25 after calibration on our set:** shadow mode only; the sieve ships in summarize-and-keep
  mode; fine-tuning is the next prompt; say so with the numbers.
- **No CPU export reaches ≤ 300 ms/question on 4 cores:** per-block sieving is asynchronous or PC-only; the
  synchronous path judges one whole-output question; the coordinator's sandbox gets the explicit wrapper only.
- **Function hooks cannot rewrite a Bash result on Claude Code 2.1.278:** the explicit wrapper is the sandbox
  integration; the report cites the primary source and the version where it changes.
- **Hermes MODIFY cannot preserve exit code, stderr or stdout order:** integration B is the post-hoc pack.
- **The typed-decisions checkpoint measures better than the English base on our set:** it becomes the default for
  `choice`/`score`; else the English base stays; the multilingual checkpoint only if long blocks need 1,024 tokens.
- **Batching or quantization breaks determinism:** the replay key includes the export id; a nondeterministic
  export is rejected regardless of speed.
- **The Hugging Face repository or the license moves:** the pinned, SHA-verified copy on the PC is the source
  of record (mirror once at install; verify on every start); the report states the license text and its terms.
- **The labeled set cannot be extracted from the record (citations too sparse):** a minimal manual labeling
  protocol (200 blocks per integration, two labelers, agreement measured) replaces it; the sieve waits.

## 8. Meta (luck lens — workflow facets, never a verdict input)

Solvency: one service, one wrapper, one JSONL ledger per venue, one decisions file per skill — no new runtime,
no new egress, and everything runs on hardware the project already has. Circulation: every measurement lands in
`docs/research/findings/JEV-LAYA-AUDIT-2026-09-22.md` §5 and the ledger itself becomes the labeled set for the
next calibration, so the loop tightens with use. Path sensitivity: right time — the lane machinery works and its
binding costs are now bytes and turns, which is exactly what a typed-decision sieve trims; wrong time for
fine-tuning, which waits for the calibration numbers. Skin in the game: the sieve's first victims are the
coordinator's own tool results, so a bad drop is felt where it is decided.

## 9. Deliverable shape

A findings report `docs/research/findings/RESEARCH-FINDINGS-2-VERIFIED.md` with: (1) the verified/challenged
version of §4 (each F-row confirmed, corrected or refuted with its source — the Laya forward path, the Hermes
hook source at the pinned commit, the Claude Code hook behaviour at 2.1.278, the winnow and jev-pruner code);
(2) the export/serving measurements of Q3 as a table with the raw commands; (3) the build specification of §6 in
build order with acceptance tests; (4) the labeled-set recipe and the calibration/A/B protocol with acceptance
numbers; (5) the candidate-row table for the skills with question wording; (6) the ceiling statement; (7) the
honest NOT-resolved list — empirical gates only, each as a runnable command with its decision rule, never a
strategic hedge. Every open question above returns a decision-grade verdict; when documentation is silent, go to
the source (Laya, transformers/ModernBERT, hermes-agent, Claude Code's hook docs, winnow) and read it. A report
that leaves any of §5 a bare uncertainty is incomplete and is continued, not accepted.

Decide; do not ask.
