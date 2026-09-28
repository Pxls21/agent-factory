# Five repos and the output-block idea (task #334)

Written 2026-09-28 12:5xZ by the coordinator, for the owner's message of 2026-09-28 12:17Z (D-100). Every repo was
cloned shallow and READ; nothing from them was installed or run. Numbers a repo states are its author's; numbers about
the owner's PC were measured over the bridge today, read-only.

## TL;DR

- **Strata** runs a 125B model well on a gaming PC, but it serves one request at a time. It cannot run beside vLLM on
  the one 3090, and it cannot run inside vLLM. Its 3090 speeds are estimates made with a faster CPU and faster RAM than
  the owner's. It is worth one measured trial in a GPU window as a one-lane route. It is not a way to run lanes in
  parallel.
- **The three Jev repos** are clients of TypeSafe's Jev API. BorisLeMeec/jev is the tool that attacks the re-reading of
  the same tokens; its Read-narrowing hook is the one piece this repo lacks. hermes-jev-skills plugs into Hermes, but it
  calls TypeSafe from inside Hermes, which production rule 3 forbids. jgrep overlaps graft. The skillsdirectory entry is
  prose only.
- **The output-block idea** is sound, and this repo already runs its first instance: the `S1-RATE` line. Its best value
  is clean labels from System 2's own choices, the thing SYNTH1's synthetic labeler failed to give. Its token saving is
  real for write-only bookkeeping and near zero for questions whose answers the next step needs. It needs a gate before
  it executes anything.

## Strata (Niko1221/Strata at d551edf, 2026-09-28)

**What it is.** A C++/CUDA engine, built partly from llama.cpp/ggml (MIT), that runs Qwen3.8-Flash-Next, a 125B MoE:
48 layers, 24,576 experts, top-10 routing, an MTP draft layer, and a 28.8 GB n-gram table (`docs/DETAILS.md`, "How it
works"). The GPU holds attention, the routers, the shared experts and a cache of the most-used experts. The CPU computes
the other experts in RAM at the same time. The n-gram table stays on the SSD. The MTP layer drafts up to 3 tokens a
pass (2.4 to 3.2 accepted on average). The server speaks the OpenAI and Anthropic APIs.

**The author's numbers.** Measured on an RTX 5070 (12 GB), a Ryzen 5 7600 (Zen 4, AVX-512) and 64 GB of DDR5-5200:
output 52 to 90 tokens/s on short prompts and 40 to 67 at 128K; prompt reading 1,070 to 1,310 tokens/s at 32K. The
RTX 3090 row is an ESTIMATE (plus or minus 20%) made with the same Zen 4 CPU and DDR5: about 128 to 140 tokens/s output
on short prompts and 100 to 115 at 64K to 128K for Q2_0. The docs say "RTX 30/40 are untested". The repo reports no
coding benchmark; IQ3_S "matches the full model on the published tests" refers to the quantizer's own tests.

**The owner's PC (measured 2026-09-28 over the bridge, read-only).**

| Part | Value | Why it matters |
|---|---|---|
| GPU | RTX 3090, driver 580.126.18, PCIe gen4 x16 | Driver meets Strata's 580 floor |
| GPU memory | 23,542 MiB held by vLLM, 256 MiB by one more process, of 24,576 | Strata needs the card to itself |
| CPU | Ryzen 5 5600X, 6 cores (Zen 3), AVX2, no AVX-512 | The CPU share runs on the slower kernel |
| RAM | 125 GB, 104 GB available | Every Strata size fits |
| Disk | /home 367 GB free | The 66 to 76 GB download fits |
| CUDA toolkit | /usr/local/cuda-12.9, not on PATH | Strata's Fedora notes name CUDA 13 |

**The owner's questions, answered.**
1. **Beside vLLM, in parallel?** No. There is one 3090, and vLLM holds 96% of it by design (D-099). Strata's speed comes
   from filling the card with experts. Running Strata means stopping the `qwen` container: a GPU window, on the owner's
   say-so.
2. **Several lanes at once on Strata?** No. "Current limits (v1): one request at a time, and one conversation cached at
   a time (switching between two chats re-reads the other one)" (`docs/DETAILS.md`, "Using it"). `serve/server.py`
   serializes requests behind one lock. Two Hermes lanes would re-read each other's 60,000 to 90,000-token prompts at
   every switch.
3. **Inside vLLM?** No. It is a different engine: GGUF i-quants, CPU expert kernels and an SSD table. vLLM's own CPU
   offload streams weights over PCIe at every step, which is a different and slower design.
4. **Faster?** Plausibly, for ONE lane. Our vLLM route measured about 45 tokens/s for one request and about 310 tokens/s
   in total at 7 lanes (2026-09-16, `PC-BRIDGE.md`). In practice one long-context local lane runs at a time (the KV
   limit, AF-AP-146). Strata's 3090 estimate is two to three times 45 per stream, but the estimate assumed a Zen 4 CPU
   and DDR5. The 5600X has DDR4 and no AVX-512, so the CPU-side experts run slower here; by how much, only a run
   settles. A first read of a 90,000-token lane prompt takes one to three minutes; follow-up turns read only the new
   part.
5. **More accurate?** Unknown. A 125B model at 2 to 3 bits against a 27B dense model at full precision is a real
   question with no answer in the repo. Only our own lanes, graded by their deterministic gates, can answer it.

**Risks found in the read.**
- The repo has no LICENSE file for Strata's own code (llama.cpp's parts are MIT; the weights carry their own licenses;
  Swift 1.5 has the Swift Open License).
- `setup.py` downloads an unpinned prebuilt engine (`releases/latest/download/`) and unpinned model files
  (`resolve/main`), with no hash check. Rule 13 needs a source build at a pinned commit and pinned model revisions with
  their sha256.
- The default port 8080 is the vLLM route's port. The default CUDA architecture is 120; a 3090 is 86.
- The "experimental speed projection" is a control vector that changes the model's answers. It stays off.

**Proposal (X-009).** One measured trial, in a GPU window the owner opens:
1. Build the engine from source at d551edf on the PC; download IQ2_XS at a pinned revision; record the hashes.
2. Run Strata's own benchmark on this PC: output and prompt tokens/s at 4K, 32K and 128K.
3. Put it behind a new OmniRoute route on another port. Run ONE Hermes build lane on an already-verified task, replayed,
   and the same task on the vLLM route: wall time, tokens, rounds, and the task's own deterministic gate.
4. Decide from that table. If Strata wins, the likely shape is a scheduled window for the one long-context lane, with
   vLLM back for short parallel work.

## The Jev repos

All three are MIT-licensed clients of TypeSafe's Jev: a "System One" model that answers typed questions (pick one,
score this, yes or no) with calibrated probabilities and never writes text.

**BorisLeMeec/jev (e81c1d0, Go, a Claude Code plugin).** This is the tool that attacks re-reading. Its measurement over
nine real sessions: 422,164,852 cache-read tokens against 196,317 tokens of tool results. The context re-sent each turn
is the cost, so the lever is keeping bytes out of the context in the first place. It offers `jev find` (P@1 0.96
against 0.33 for BM25 on 24 queries in 3 repos), `jev ask`, and a Read hook that narrows a file over 400 lines to the
part asked about (41% fewer billed tokens, 0 lost targets in 50 reads). It saves tokens, not time.
- This repo already has most of it: graft first, the search intercept (semantic Grep answered from graft), `jev_locate`
  and the System-1 excerpts. It has no Read-narrowing hook.
- **Proposal (X-011):** a Read-narrowing hook, measured the way the author measured it: paired runs, billed tokens and
  correct answers. Laya or TypeSafe behind it (D-078 allows TypeSafe after the scrub).

**kerpopule/hermes-jev-skills (89b073f, Python).** A Hermes plugin and ten skills: model routing, search, memory
screening, web-result screening (70 of 79 planted attacks caught against 11 for Hermes's own scan; 0 of 1,520 clean
chunks withheld), handoffs, turn choice, skill selection (377 skills in about 2.8 s), triage, computer use and browser
use. It registers `pre_llm_call`, `transform_llm_output`, `transform_tool_result` and `post_tool_call` hooks, fails open
by design, and calls `api.typesafe.ai` from inside Hermes (a custom endpoint is supported).
- For the Agent Factory's production Hermes it conflicts with rule 3 (a second model API egress), rule 9 (fail-open
  hooks that change the model's output) and rule 13 (pinning).
- For our PC build lanes it is worth studying: the web screen, and skill selection, which is Laya's L6 (task #297,
  gated by D-096: it must beat the matcher on held-out real scores).

**kyu1204/jgrep (c56119f, TypeScript, npm `jevgrep`).** Semantic grep: 16 code chunks and 16 yes/no questions per
request, a `src/` tree in about 2 s for about a cent, and a diff mode ("endpoint with no auth check in my diff"). It
overlaps graft and `jev_locate`; the diff screen is the one new idea. Low priority.

**skillsdirectory.com, jzkk720-jev.** A prose-only skill: setup notes for Jev through OpenRouter or TypeSafe. Its CLI is
excluded from the bundle. Nothing to adopt.

## The output-block idea

**The idea, restated.** The coordinator writes typed blocks in its own output: a code question, a wiki or ledger update
(the target, the content, the place). A hook finds them after the turn, runs them through scripts in the background, and
returns the results. Each block is also a labeled record, state to System 2's typed decision to outcome, for training
System-1 models. The owner wants it here now and in the Agent Factory later.

**What holds.**
- This repo already runs the first instance. The `S1-RATE <id> rel=<0-3> use=<0-3>` line is a typed block in the output,
  and `scripts/s1_scores.py` collects it as labeled data. The idea generalizes it from "rate this injection" to "do
  this".
- The labels are real: made by the model that acts, when it acts. SYNTH1's synthetic labeler failed the check against
  the real scores (rel exact 0.3846 on 52 sections against a 0.75 bar), so real labels from real decisions are the
  better data.
- Write-only bookkeeping gets cheaper: ledger lines, incident entries, wiki blocks, task closes. Today each is a tool
  call plus a stamp ritual. A block applied by a script is one output section, and the script takes the stamp from the
  clock, which ends the typed-stamp incident class (at least five instances, CLAUDE.md) by construction.
- Questions whose answers are needed only later (a graft pack for the next increment) can run in the background.

**What does not hold, or needs care.**
- A question whose answer the next step needs saves nothing. Its answer must come back as a new turn, and a new turn
  re-reads the whole context: the same cost as a tool call. Independent tool calls can already share one message.
- The expensive part is the context re-read per turn. It falls only when blocks cut the number of turns or keep bytes
  out of the context. So the pilot measures turns per task and cache-read tokens, before and after.
- **Security.** Running text from model output is a new effectful channel. It must not become a way around the harness's
  permissions or the policy gate (rule 9). The minimum: a per-session nonce in the block fence, so a quoted report, a
  pasted document or a subagent's text cannot forge a block; a closed list of verbs, each with a schema; no shell; write
  targets limited to named paths, with the existing gates (lossless, stamps, mirrors, the tests that name the path);
  every block logged with its result; an off-switch file; and the executor reads only the coordinator's own final text,
  never tool results.
- Labels carry selection bias: they record System 2's choices, not the truth. Each block needs an outcome signal (was
  the answer used, did the edit survive review), as the S1-RATE `use` score does.
- **In the Agent Factory** the channel already exists: a Hermes tool call IS a typed block the runtime parses, and it
  passes the fail-closed `pre_tool_call` gate. The factory needs no second channel. It needs every tool call logged with
  its state and its outcome as the labeled record, under the scrub. The new work there is the outcome labels.

**Proposal (X-010).** A two-verb pilot in this repo:
1. `book` blocks: a ledger line, an incident entry, a wiki block or a task close. The script checks the target, takes
   the stamp from the clock, applies the change, runs the tests that name the path, and reports.
2. `ask` blocks: a batch of graft or Jev questions, run in the background, with the answers injected by the next hook.

Every block and its outcome becomes a JSONL record, behind the scrub and the value gate. Run it for a week and measure
tool calls per task, turns per task, cache-read tokens, and blocks the gate refused; then decide. It is a new subsystem
with a security surface, so the deep-work path applies before the build (research prompt, design, council, seed),
unless the owner wants the small pilot first.
