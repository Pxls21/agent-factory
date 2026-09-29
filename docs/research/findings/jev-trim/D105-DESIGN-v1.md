# D-105: the context trimmer, feasibility and design v1 (task #346)

- **Status:** DESIGN PROPOSAL, written in the main loop 2026-09-28 22:4xZ. Nothing here is built. The owner's answers
  (§8) come before the seed and the task breakdown.
- **Evidence:** `docs/research/findings/jev-trim/TRIM-AUDIT-2026-09-28.md` (cited as "audit §N"), plus the Hermes code
  read at 527da60 in the main loop (cited by file:line) and one web search for prior art (§3.2).
- **Rule:** a number below with no committed producer is marked UNVERIFIED.
- **CORRECTION 2026-09-29 (T0-REPLAY round 1, §9):** the "about 200k" budget for this session (§1 item 2, §3.3, §8
  question 1) is NOT supported. The first rule set, with the last two turns protected, cut the median active context
  from 454,522 to 332,932 and reached no budget from 100k to 250k. Round 2 measures wider rules and a trim guard.
- **RE-SCOPED 2026-09-29 by D-106 (the owner's answers to §8):** Hermes adopts the LCM plugin if T1 finds it good
  enough; this Claude Code session gets no trimmer (§3.3's C1 and C3 are parked) and instead a measured compaction
  point, a richer compaction and context packs; Jev acts only after it beats the fixed rules on the replay. The plan is
  §10; §3.3, §6 and §8 stay as the record of what was proposed.

## 0. The ask, in the owner's words (D-105, 2026-09-28 18:23:30Z)

Use Jev to trim the context window itself, so "we never get to a stage where we need compaction, because the context
stays at the optimum level" (the owner recalled "100k or something"; D-097 set 131k for Hermes). Above that level, a
model looks at the transcript, finds "which parts of the transcripts are useless to what we're doing" and removes them
from the active context, "almost on a turn-by-turn basis". "The logs are still there ... It's just the active context".
"If it is [feasible], it will be the final piece."

## 0b. What is installed in this domain already (orchestration 0l)

- **jev-pruner** (function-hook plugin, enabled in this session since 2026-09-22; owner-recommended; PARKED for the
  Hermes lanes by D-053). It asks a Jev per 20-line chunk of a Bash output whether to keep it, and replaces only the
  current result. Its endpoint here, 127.0.0.1:47411, has no listener now (audit E1c), so every call fails open.
- **The System-1 layer** (`.claude/hooks/system1-context.py`): adds skill lines to the context; it never removes (E7).
- **The P1 replay and its miss accounting** (`scripts/jev_pipes/transcript.py`, `scripts/jev_pipes/accounting.py`):
  the pinned-length transcript walker and the committed "miss" definition. T0 reuses both.
- **The budget probes** (`docs/research/findings/jev-pipes/context_budget.py`, `inject_cost.py`): what the context is
  made of (audit §3.10).
- **Hermes's built-ins** (off in the lane profiles as far as the repo records): the proactive tool-result prune (B7) and
  micro-compaction (B8).

## 1. Verdict

1. **Hermes lanes and production: feasible now.** Hermes has a seam built for this. A context engine's
   `select_context()` replaces the message list for one request and never touches the stored history (audit B2). It runs
   on every provider request (B3), in the lanes and on the production ACP path alike (B12). The compression trigger reads
   the selected list (`agent/conversation_loop.py:2688`, then the pressure estimate at `:2855`; read at 527da60, the
   lane pin b3399c1 not re-read), so a lane held under the budget never reaches the lossy compressor. An engine can also
   give the model its own tools (`get_tool_schemas()` and `handle_tool_call()`, which receive the live message list,
   `agent/context_engine.py:413-431`), so the recall path lives in the engine. The stock `session_search` cannot serve:
   its scroll refuses an anchor in the current session while the row is still active ("scroll rejected: anchor lives in
   the current session lineage", `tools/session_search_tool.py:582-605`), and a request-only trim leaves every row
   active.
2. **This Claude Code session: feasible in part.**
   - A 100k budget is below this session's fixed start. Every segment starts near 130k: the system prompt and tools
     about 91k, and the post-compaction messages about 39k (audit §3.3). 131,072 is below the start in 3 of 6 segments.
   - The one seam that can remove old messages is the early-access function hook `session.compact`, and it runs only
     between turns (audit A1.11). Its behavior at 2.1.283 is not verified.
   - ~~A realistic first budget here is about 200k~~ (withdrawn 2026-09-29, §9): the first rule set, measured, holds the
     median at about 333k (from 454,522), far from the 784k compaction point but above every budget the owner named. The
     fixed start must shrink before 131k is possible here (§3.3, C3).
3. **The Jev judge: not yet.** No judge has been measured on the question "useless to the current work?" (audit §2).
   On other questions: Laya was rejected on every KC-J3 line; the local jev-pruner replay pruned 0 of 3,153 results, but
   its scorer never saw the chunk, so that run measured a broken path, not a judge (E1b); the Qwen teacher beats its
   baseline on two question types and not on two others, and its run is pending verify (E4). The council's KC-J5 also
   forbids a Laya score deciding what is dropped. So in v1, plain rules trim, every trimmed item leaves a pointer, and
   Jev runs in SHADOW until it beats the rules on a replay (§4).

## 2. What the measurements say

| Quantity | This session (audit §3) | A Hermes lane |
|---|---|---|
| Fixed start of the context | ~130k (system + tools ~91k; CLAUDE.md, re-injected skills, listings and summary ~39k) | small (role + `.hermes.md` ≤ 48,000 chars + brief); not measured |
| Mean prompt per API call | median 461,918 per request (D-105; whole session to 09-25) | 50,680 to 100,119 tokens per session, over the six newest lane profiles' 16 sessions with calls ((input + cache read) / calls from each profile's `state.db`; read-only bridge probe, 2026-09-28 23:0xZ) |
| Live compression settings | auto-compaction near 784k | every probed lane profile: `compression.enabled: true`, `threshold: 0.5` (the code floors it to 0.75), `target_ratio: 0.2`, `protect_first_n: 3`, `protect_last_n: 20`; no `context.engine` line (the built-in compressor); `context_length: 131072` in the newest profile only |
| Growth per request | median 1,565 tokens; p90 4,161; max 26,740 | not measured (the session store keeps per-session totals, not per-request sizes) |
| Largest parts of an over-budget context | prior thinking (25.8% of the whole, median); Bash results; tool results 51-200 requests old | NOT measured here |
| Where compaction happens now | ~784k (six automatic compactions in the audit's window, 116-206 s each) | ~98k: the built-in threshold is floored at 0.75 under a 512K window (audit B6) |
| Prompt cache | 99.4% of re-sent tokens are cache reads | vLLM prefix cache; a change to an earlier message re-prefills the rest |
| Budget the owner named | 100k: below the fixed start in 6 of 6 segments | 131,072 (D-097): the model limit; the lane compresses near 98k |

## 3. The design

### 3.1 One policy, three venues

The trim policy is a pure function: history + budget B + low-water mark L + protected set → the active list + the
archive map. It is deterministic and decides nothing with a model. The same spec runs in each venue.

**Rules, cheapest loss first.**
1. Superseded copies: every task reminder except the newest; a file's Read result when the same file was read again
   later; a hook injection that a newer one from the same source replaced.
2. Old thinking: thinking blocks before the current turn.
3. Old tool output: a tool result older than A requests becomes a one-line stub (tool, command head, exit status, size,
   recall pointer).
4. Old tool input: a large tool-call body (a Write or Edit text) older than A requests becomes a stub.

**Protected, never trimmed.**
- The system prompt, the first user message (the brief), the Fubuki governance packet in production.
- The newest copy of every loaded skill body and role body. AF-AP-17 and AF-AP-19 record what happens when these go:
  the lane continues under weaker rules.
- The owner's typed messages; everything in the current turn; the last K turns.
- Tool-call pairing: a stub keeps its call and result paired, because a provider rejects an orphan.

**Hysteresis.** Trim only when the active context crosses B, and trim down to L. Between trims the list only grows at
the end, so the prompt cache stays warm. One rebuild of the prefix after the edit point pays for (B − L) / growth
requests of smaller reads. The cost model is UNVERIFIED until T0 prices it on this session's own record.

**Every stub carries a pointer to the full bytes** (KC-J6: the original recoverable next to what is shown). The log
itself stays whole: the Claude Code transcript JSONL is append-only, and Hermes's `select_context()` never writes the
stored history.

### 3.2 Hermes: the lanes first, then production

- **Seam:** a context engine plugin (`context.engine: <name>` in the profile's config; loaded from
  `plugins/context_engine/<name>/` or `~/.hermes/plugins/`, `agent/agent_init.py:2728-2760`). It subclasses the built-in
  `ContextCompressor` and overrides `select_context()` only, so the built-in compressor stays as the last resort.
- **Behavior:** request-only, fail-open (an exception, `None` or an empty list keeps the original list, audit B2).
- **Recall:** each stub names the message's position; the engine's own tool (`context_recall`, a name to grep at
  authoring) returns the original from the live message list, capped and paged. Not `session_search` (§1, item 1).
- **Budget:** B about 90k and L about 64k at 131,072, under the compressor's ~98k (both UNVERIFIED until T0 and one
  measured lane).
- **Payoff beyond quality:** the vLLM KV pool holds 215,112 tokens (D-099). Two lanes held under 90k fit together;
  today only one long-context local lane runs at a time.
- **Prior art to read first:** `hermes-lcm` (stephenschoettler/hermes-lcm), `hermes-lcm-x` (in the Hermes plugin
  catalog) and `lossless-hermes-py` (PyPI). As their pages describe them (not read yet): a SQLite store of every raw
  message, a DAG of summaries, a bounded live prompt, and tools that recover exact detail; based on the LCM paper by
  Ehrlich and Blackman (Voltropy PBC, 2026-02). They summarize with a model, which our v1 policy does not. Adopt or build
  is decided after a pinned audit (T1): code read, license, tests, fit with b3399c1 and 527da60 (standing rule 13).
- **Production:** after the Stage 0 gate (D-029): the trimmer changes what the production model sees. Rule 14's tests:
  normal behavior, failure behavior (fail-open, a floor on what stays), and the security boundary (the governance packet,
  the policy hook's view and the memory scopes never change). S0-04 is not touched: the trimmer changes what Hermes
  sends, not what OmniRoute forwards, and OmniRoute's compression stays off.

### 3.3 This Claude Code session (D-087: our workflow is the test bed)

Three layers, the safest first.
- **C1, a stable seam, buildable now.** PostToolUse `updatedToolOutput` replaces the current tool output before the
  model sees it (audit A1.3). A size rule caps a large output at birth: the full text goes to an archive file, and the
  model sees the head, the tail and the file path. It edits no history, so it costs no cache and no thinking. The
  harness already does this above about 30,000 characters (audit A1.18); C1 lowers that line. jev-pruner does it with a
  model; C1 does it with a size rule.
- **C2, early access, probe first.** A function-hook plugin calls `$.session.compact()` between turns when
  `$.session.usage()` passes B, and its `session.compact` hook returns the §3.1 list in place of a summary (audit A1.11).
  - The curated list drops every thinking block before the edit point. The API counts that as valid; the model loses
    that reasoning, and the prompt cache restarts at the edit (audit D6, D7).
  - The probe runs in a throwaway session with its own config directory, never first in the owner's working session.
    It answers audit §7 cells 1-4 and 7.
  - Limit: between turns only. A long autonomous turn still grows before the next trim: median +7.3k, p90 +71k, max
    +350k per turn at stop-hook boundaries (audit §3.8). That stays far below the 784k compaction point.
- **C3, the fixed start.** `tool.describe` gives a one-line description to each tool this project never calls (cached
  once per session, so the cache does not churn), and `prompt.section` leaves out system sections that do not apply
  (audit A1.12, A1.13). CLAUDE.md stays whole (D-090). Only C3 can bring this session toward 131k.
- **Budget here:** not yet set. The first rule set reaches no budget from 100k to 250k (§9); round 2 measures what the
  wider rules reach.

## 4. Where Jev fits

The owner's picture is System 1 filtering what reaches attention. What the evidence allows today:
- **Jev never decides a drop in v1** (KC-J5; no measured signal, §1).
- **Jev runs in shadow.** At each trim it scores the items the rules archive and a sample of the items they keep ("is
  this useless to the current work?"). The scores are logged and change nothing.
- **The label is free and independent of any judge.** A RECALL (the model reads an archived item back) or a
  USE-AFTER-ARCHIVE (the model later cites a token that only an archived item held) marks that item as needed.
- **Graduation is the owner's call.** The Jev ordering must beat the plain orderings (age, random, word overlap with
  the current goal) on the replay, at equal context size, on a committed sample (deep-work Phase 2). Only then may it
  change which items archive first. The pointer and the protected set stay.

This is the RLM idea (Zhang, Kraska and Khattab, arXiv 2512.24601) made safe: the whole log is the environment, the
active context stays small, and the model pulls back what it needs.

## 5. Premortem: how this fails

| Failure | Guard |
|---|---|
| An archived item changes a decision (needle loss) | Stub plus recall on every item. Tripwire: one confirmed incident sets the trimmer to rule 1 only (superseded copies) until the owner reviews it (KC-J5's spirit, applied to the rules too). |
| Governance or skill text trimmed (AF-AP-17, AF-AP-19) | The protected set, with a test per protected kind. |
| The prompt cache rebuilds too often | Hysteresis; T0 prices the rebuilds against the savings before any build. |
| Later thinking invalid after an edit (Claude API) | C2 drops thinking before the edit point; Qwen lanes have no such check. |
| An orphan tool result | Stubs keep the pair; a test per provider shape. |
| The early-access seam changes | Only C2 depends on it; C1 and C3 do not. |
| A stub reads like an instruction | Stubs are fixed-format data lines, and a test rejects any other text. |
| A bug empties the context | Fail-open in Hermes; a floor test (the protected set plus the last K turns always stay). |
| Recall floods the context again | Recall output is capped and paged. |

## 6. Increments (a proposal; the seed follows the owner's answers)

| Id | What | Venue | Needs the owner? |
|---|---|---|---|
| T0 | The replay: the §3.1 policy over this session's transcript and the longest sandbox lanes. It reports the context profile, the trims, the cache cost and the USE-AFTER-ARCHIVE counts per rule and age, and chooses A, B, L. It prints counts and ids only, never content. | sandbox | no |
| T1 | The LCM audit: hermes-lcm and its forks at a pinned commit (what runs per request, recall tools, license, tests, fit with our pins). Adopt or build. | sandbox EXPLORE | no |
| T2 | The Hermes engine: `select_context()` with stubs and the engine's own recall tool; normal, failure and security tests; one lane beside a control lane. | PC build lane | Q3 |
| T3 | C1: the PostToolUse size cap. | sandbox | Q1 |
| T4 | C2: the probe in a throwaway session, then the plugin. | sandbox | Q1 |
| T5 | C3: the fixed start. | sandbox | Q1 |
| T6 | The Jev shadow scorer and the recall labels. | PC | Q2 |

## 7. Open cells that can change the order

- Audit §7 cells 1-4 and 7 (the Claude Code function hooks at 2.1.283; the account's thinking-check date). T4's probe
  answers them.
- Audit §7 cell 10: the lanes' live context per request and their compression events (PC only). T2's control lane
  measures them.
- NEW: whether hermes-lcm already does what T2 would build (T1).

## 8. Questions for the owner

1. **The budget for this Claude Code session.** 100k is below its fixed start of about 130k.
   (a) Trim history only, at whatever level round 2 shows the rules can hold. (b) Also shrink the fixed start (C3).
   (c) Keep compaction here and trim only in Hermes. Recommended: decide after T0 round 2 (the first rule set held about
   333k, §9).
2. **Jev and KC-J5.** The council's KC-J5 forbids a Laya score deciding what is dropped; D-105 asks Jev to decide.
   Recommended: Jev in shadow until it beats the plain rules on the replay; then you decide whether it may act.
3. **The order.** Recommended: T0 and T1 now (no answer needed), then the Hermes lanes (T2), then this session (T3 to
   T5), then Jev (T6).
4. **Adopt or build on Hermes.** If T1 finds hermes-lcm clean and pinned, adopt it (it summarizes with a model), or
   keep our own rule-based engine? Recommended: decide after T1.

## 9. T0-REPLAY round 1 (2026-09-29): what the first rule set does

Source: `tasks/briefs/jev-trim/T0-REPLAY-report.md` and `docs/research/findings/jev-trim/replay-2026-09-28/` (the tool
`scripts/jev_trim/replay.py`, reusing the P1 walker and miss definition; the cross-check reproduces the audit's table).

- **This session (1,898 requests, 7 segments), rules R1 to R4, the last two stop-hook turns protected, A=20, between
  turns:** median active context 332,932 and p90 438,523 against the real 454,522 and 722,281; net cache cost -0.3% at
  Opus 5.5's read price (0.05 of base; UNSURE, a parameter). Every budget from 100k to 250k gives the same result: the
  protected turns alone pass 200k in 63.7% of requests, so each trim archives everything eligible and still ends above
  the budget.
- **What stays:** no rule covers the hand-back texts or the attachments (listings, nested memory, edited-file
  snippets), and this session's turns are long (up to 130 requests between two stops).
- **The needle proxy (the P1 miss definition, a lower bound on need):** 95 of 1,957 archived items (4.9%) were used
  again within 20 steps, 353 (18%) later in the segment; for R1 alone (superseded copies) 6 and 17 of 322.
- **Three long sandbox lanes, only the last 3 requests protected (the Hermes-like case), per request:** median 253k
  to 338k against 406k to 459k. A trimmer that cannot reach L fires again on the next request, so it fired on most
  requests and the modeled cache cost rose 57% to 368%.
- **What this changes:** protection by a request window, not by turns; rules for hand-backs (saved to the repo by the
  harvest stack) and superseded attachments; a trim guard (fire only when the eligible items can reach L, or at most
  once per N requests); and a pessimistic cache bound (the 20-block lookback, the report's D16). Round 2 measures them.


## 10. D-106 (2026-09-29): the re-scope and the plan

The owner's answers (D-106, transcript 00:51:42Z) replace §3.3 and answer §8. Nothing below is built; every number it
needs comes from a measurement named here, never from intuition (the "about 200k" of §1 was the lesson).

### 10.1 What changes

- **Hermes (the lanes, then production):** adopt the LCM plugin if T1 finds it good enough (license, pins, model calls
  through OmniRoute only, what it exposes to the model, its tests). T2 (our own engine) is built only if T1 rejects LCM.
  LCM's thresholds for the Qwen lanes come from 10.2's Qwen rows.
- **This session:** no trimmer. §3.3's C1 (the size cap) and C3 (the fixed start) are parked. C2's seam
  (`session.compact`, audit A1.11) is re-used to enrich the compaction and to choose its moment (10.3 P4, P5), not to
  hand back a trimmed list.
- **Jev:** acts only after it beats the fixed rules on the replay (§4 stands; the score is 10.3's).
- **T0 round 2** finishes as briefed (it was mid-run at the ruling); its composition table feeds 10.3.

### 10.2 Where to compact (task #352)

The question: at what fill does this session's work get worse, and what does one compaction cost? The owner's candidate
is about 500k on the 1M-context models; the current point is about 784k (audit A1.15). Four measurements decide it.

- **R-A, published curves** (a sandbox EXPLORE lane with web access): accuracy against input length for each model we
  run (Opus 5.5 in the main loop and the sandbox lanes, Fable 5 when it is the main loop, Qwen3.8-27B on the PC lanes at
  131k) and its nearest measured siblings (MRCR, GraphWalks, RULER, NoLiMa, LongBench v2, Fiction.LiveBench, the
  context-rot studies, agentic long-horizon results), plus the vendors' own compaction guidance. An evidence table with
  sources and dates, vendor claims marked; no verdict.
- **R-B, our own quality curve** (the replay tool; counts only): per main-session request, the fill; per following step,
  signals that need no judge: tool errors, failed edits (the `old_string` not found), a file read again with no change
  in between, a command run again with no edit in between, hook refusals (the future-stamp gate, stale ids). Rates per
  100k of fill, compared inside each segment (early against late) so that the fill is separated from the task mix.
- **R-C, the loss at each compaction** (the replay tool): at each compaction boundary in the transcripts, what the
  session fetched again in the next N steps that it held before the boundary (the same file read again, the same
  command run again, the transcript or the ledger searched), in steps and tokens, and which of those the summary and the
  SessionStart injections already held. This is the cost of one compaction, and the score in 10.3.
- **R-D, a live A/B** after R-A to R-C: segments at the candidate point (set with `CLAUDE_CODE_AUTO_COMPACT_WINDOW` or
  `/autocompact`, audit A1.14; how it combines with `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80` is measured first), compared
  with the 784k segments on R-B's rates and R-C's loss.

The choice: the fill at which the quality lost to a fuller context (R-A, R-B) exceeds the loss of one more compaction
(R-C) spread over a segment. The cache cost per request is a third column, not the decider.

### 10.3 A richer compaction and context packs (task #353)

What exists (§0b's rule): System-1 L1 injects skill text on Edit, Write and Bash, once per context window, and resets at
compaction; L3 and `wiki-context.py` inject per prompt; SessionStart (compact) injects the task view, the live-state
block and the chat tail; `scripts/codemap.py` builds a pack per code file after each commit (L2a, task #284: symbols,
callers and risk, tests, registry rows). Not built: L2b (show a code pack when the file is touched), packs for other
files, packs per task.

- **P1, file packs on touch (L2b):** the first Read, Edit or Write of a file in a context window injects the relevant
  part of its pack (the symbol being edited; the file's header on a Read), within the System-1 budget, once per window.
- **P2, packs beyond code:** for any tracked file, the lines that name it in the ledger, the decision log, the incident
  log and its AF-AP rows, the quirk skills, the briefs and reports; its last commit subjects; its open issues. Built
  after each commit like L2a, read in milliseconds.
- **P3, task packs:** per active task in the ledger view, its headline lines, its brief and report paths, its files,
  its live agent id or PC lane, and its last state line. Injected at compaction (SessionStart, for the tasks in flight)
  and when a task's file or id is touched.
- **P4, the summarizer's instructions:** tell the summarizer what R-C shows it loses (for example the owner's exact
  words, agent ids, file paths, numbers with their producers, pending commands). The stable route is an instruction in
  the context the summarizer reads; `session.compact` ("rewrite `instructions` ... on the way down", audit A1.11) is the
  early-access route, probed first in a throwaway session.
- **P5, the moment:** a function-hook plugin compacts between turns (`$.session.compact()`, audit A1.11) at a good
  boundary (after a landing or a push, no edit in flight) once the fill passes the point 10.2 chooses; the built-in
  threshold stays as the backstop. Early access: probed first in a throwaway session.
- **Jev (D-106 item 5):** at each compaction Jev writes its own selection of pack items and a digest, in shadow: logged,
  never injected. On the replay both are scored by R-C: the share of the post-compaction re-fetches each would have
  prevented, at the same token budget. Jev's selection replaces the fixed rules only after it beats them on a committed
  sample (deep-work Phase 2); the owner decides.

### 10.4 Increments (they replace §6)

| Id | What | Venue | Waits on |
|---|---|---|---|
| K0 | R-A, the published curves | sandbox EXPLORE (web) | a free lane slot |
| K1 | R-B and R-C in the replay tool (T0 round 3) | sandbox build | T0 round 2's report |
| K2 | P1 (L2b) and P2 | sandbox build | a free lane slot |
| K3 | P3, then P4 by the stable route | sandbox build | K1 (what a compaction loses) |
| K4 | the throwaway-session probe of `session.compact` and `$.session.compact()`, then P5 | sandbox | K0, K1 (the point) |
| K5 | R-D, the live A/B | this session | K0, K1 |
| K6 | Jev in shadow, scored on the replay | PC | K1, K3 |
| H1 | LCM for the Hermes lanes, pinned in `upstream.lock.yaml`, its thresholds from K0's Qwen rows | PC | T1's verdict |

### 10.5 K0: what the published evidence says (2026-09-29)

Source: `tasks/briefs/jev-trim/K0-COMPACTION-POINT-report.md` (evidence only; the reading at the end is the main loop's).

- **Our Claude models.** No per-length curve exists for Opus 5.5 or Fable 5. Their nearest measured siblings on the
  hardest retrieval test (MRCR v2 with 8 needles, Context Arena, independent) fall below 85% of their 8k score at 128k to
  256k and below 50% by 512k (Opus 5: 91.3 at 128k, 65.6 at 256k, 42.5 at 512k). On graph reasoning, Mythos 5 (Fable 5's
  sibling) scores 91.1 at 256k and 79.4 at 1M (GraphWalks BFS). Long-document QA near 100k (AA-LCR) is 82 to 85 for all
  three models we run.
- **Qwen3.8-27B** (the PC lanes, served at 131k with 4-bit weights): 97.9 at 64k and 78.9 at 128k on the same retrieval
  test.
- **The vendors' own practice.** Anthropic's evaluations compact at 200k (orchestrators at 100k); the API's threshold
  compaction defaults to 150k (minimum 50k); Claude Code compacts native-1M models at about 967k by default; the docs
  name the effect "context rot". Hermes compresses at 0.75 of the window below 512k.
- **A compaction costs.** Compactors kept 17% of injected state on average (COMPINT, contexts of 100k); a 24-turn agent
  under 5x compression kept its completion rate but made up to three times as many retrieval calls; summaries keep later
  content better than earlier content.
- **A setting trap.** `CLAUDE_CODE_AUTO_COMPACT_WINDOW=500k` reads as 500 and clamps to the 100K minimum; write `500000`
  (the Claude Code docs, K0's G8).
- **The main loop's reading.** The evidence argues for compacting well below this session's 786k. Our post-compaction
  start is about 130k, so a point near Anthropic's 200k would leave about 70k of working room and compact every few turns.
  K1 measures what each of our compactions loses and models the count at 300k to 785k; the point comes from K1's table,
  then the live test (R-D).

### 10.6 K1: what our own compactions cost (2026-09-29)

Source: `tasks/briefs/jev-trim/K1-COMPACTION-LOSS-report.md` and the outputs under
`docs/research/findings/jev-trim/compaction-2026-09-29/` (measurements; the reading at the end is the main loop's;
VERIFY-K1 attacks them).

- **Scope.** This session's 139 compactions (121 on the 1M window, 18 early ones on a 200k window) and 21 in 16
  subagent transcripts.
- **The loss per compaction, main (1M class).** A compaction removes about 658k modeled tokens and keeps about 58k (the
  summary and the start injections). The next 20 requests used 86 distinctive removed tokens that the kept start lacked
  (301 over 100 requests, 411 over the rest of the segment). But the session re-fetched little beyond its normal rate:
  26.4 re-fetch calls per 100 requests in the first 20 requests against 23.9 at control points, and none above the
  control after that (21.9 against 25.6 over 100). The kind shifts: more Reads of known files and ledger reads, fewer
  identical re-runs.
- **Subagents lose more:** 34.8, 30.4 and 27.4 re-fetch calls per 100 requests against 22.1, 14.9 and 14.9 (7 control
  points only), mostly transcript searches and Reads of known files.
- **Quality by fill, main.** Tool errors 1.45% to 2.11% of calls per 100k from 100k to 800k, with no rise. Inside a
  segment, errors fall from the first third to the last (1.89% to 1.58%), while re-runs of an unchanged command rise
  (0.23% to 1.39% of Bash calls; waiting loops are among them).
- **The cost model (a model).** At 785k it reproduces the observed count (119 against 121). At 500k: 206 compactions,
  mean fill 306k, 6.19 billion cache-read tokens against 9.24 billion. At 400k: 278, 256k, 5.17 billion. At 300k: 427,
  205k, 4.10 billion. The modeled missed tokens grow with the count (48,940 at 785k, 84,720 at 500k, 175,610 at 300k).
- **The main loop's reading (its basis struck by VERIFY-K1: see the next item).** The published curves (§10.5) say the work gets worse as the fill passes about 256k; our
  mechanics show no decline, and a compaction costs this session little re-fetching, because the ledger, the live-state
  block and the start hook restore its state. So moving the point down from 785k is cheap, and 500k cuts the cache reads
  by a third. The first live arm (R-D) is the owner's 500k: `autoCompactWindow` 500000 (never "500k", §10.5), with the
  real point read from the next boundary's preTokens (the 80% override may bring it near 400k). The subagents' larger
  loss is an item for §10.3: their start holds no ledger or live-state block, so task packs (P3) matter most there.
- **VERIFY-K1's correction (2026-09-29 04:2xZ; `tasks/briefs/jev-trim/VERIFY-K1-report.md`).** The numbers above reproduce
  exactly (an independent reader, 0 differences), but the reading does not stand as written. K1's shapes counted writes
  as re-fetches (about a third of all counted calls; 45% of the ledger "reads" were edits and commits), and they could
  not see this session's main re-fetch forms: a Bash view of a file known before the boundary (10.97 per 100 requests
  after a boundary against 3.87 at sliding control points) and a repeated `git log` or `git show`. Corrected, the first
  20 requests after a compaction carry +12.6 to +16.5 re-fetch calls per 100 over four controls: +2.5 to +3.3 calls and
  about +7k tokens per boundary, five to seven times K1's. Over 100 requests the excess stays positive (+1.5 to +3.7
  per 100), and the ledger is re-read 4 to 10 times, the live-state about 9 times, their normal rates. The cost model's
  constant growth per request fails in the data; a position-aware variant gives 247 compactions at 500k, not 206. What
  may survive, as the verifier's inference (not measured): at 500k the extra re-fetching stays under a tenth of the
  cache-read cut. K1 round 2 (`tasks/briefs/jev-trim/K1-R2-brief.md`) re-measures with the corrected shapes. Until
  then the first live arm stays 500000 on that inference, not on the struck reason. For §10.3: the dominant re-fetch
  after a boundary is a Bash view of a known file, which is what K2's file packs trigger on.
  Its +2.5 to +3.3 calls per boundary undercounts: its classifier stopped at the first heredoc and counted commit
  sequences as searches (VERIFY-K1 round 2's R2-F8); K1 round 2's +3.9 to +4.1, below, is the better figure.
- **K1 round 2 (2026-09-29 06:0xZ; `tasks/briefs/jev-trim/K1-R2-report.md`, outputs under `compaction-2026-09-29-r2/`;
  GATED-PENDING-VERIFY).** Measured with the corrected shapes (writes and commits out, the strict set in, the loose set
  apart) against three controls. Main, 1M class: the first 20 requests after a compaction carry 38.07 re-fetch calls per
  100 against 17.51 to 18.52 at the controls, +3.9 to +4.1 calls and +9.2k to +9.6k tokens per boundary, every 95%
  interval clear of 0; requests 20 to 99 carry +2.9 to +3.6 per 100, the first 100 +6.0 to +7.1. Subagents pooled: +25.8
  to +31.9 per 100 in the first 20 requests. The main forms: a Bash view of a known file (11.95 per 100 against 3.60 to
  5.00) and a ledger read (8.89 against 1.92 to 2.54). The position-aware cost model, calibrated to the observed 121 at
  785k, gives 246 compactions at 500k (the flat model 206). Moving from 785k to 500k adds about 0.8 to 1.2 million
  re-fetched tokens over the first 20 requests after each compaction (1.1 to 1.8 million over 100), against 3.1 to 3.4
  billion fewer cache-read tokens. So 500k stays cheap in cache terms; the extra calls (about four per compaction) are the
  live test's to weigh. VERIFY-K1 round 2 (2026-09-29 06:5xZ, the same report, "Round 2") corrects three things: priced with
  cache writes (which rise 10% to 28%), 500k saves 17% to 21% of the cache cost, not a third; only the re-fetch excess is
  measured (at about 785k), while the 500k side is a model calibrated at 785k; and the requests 20 to 99 excess is weak
  (it vanishes under two direction-rule variants). The first-20 excess holds at +3.5 to +4.2 calls under every defensible
  rule, and +1.6 to +2.7 if a read were to win over a write or a commit, a choice no test pins yet (task #362). The builder's excess is larger than VERIFY-K1's because its direction rules
  exclude more writes and commits at the controls (its DISCREPANCIES 1 to 8); VERIFY-K1 round 2 confirmed that reading
  on a hand-labeled sample of 144 real commands (its R2-F2 and R2-F8).
