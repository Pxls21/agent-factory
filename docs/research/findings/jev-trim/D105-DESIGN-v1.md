# D-105: the context trimmer, feasibility and design v1 (task #346)

- **Status:** DESIGN PROPOSAL, written in the main loop 2026-09-28 22:4xZ. Nothing here is built. The owner's answers
  (§8) come before the seed and the task breakdown.
- **Evidence:** `docs/research/findings/jev-trim/TRIM-AUDIT-2026-09-28.md` (cited as "audit §N"), plus the Hermes code
  read at 527da60 in the main loop (cited by file:line) and one web search for prior art (§3.2).
- **Rule:** a number below with no committed producer is marked UNVERIFIED.
- **CORRECTION 2026-09-29 (T0-REPLAY round 1, §9):** the "about 200k" budget for this session (§1 item 2, §3.3, §8
  question 1) is NOT supported. The first rule set, with the last two turns protected, cut the median active context
  from 454,522 to 332,932 and reached no budget from 100k to 250k. Round 2 measures wider rules and a trim guard.

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

