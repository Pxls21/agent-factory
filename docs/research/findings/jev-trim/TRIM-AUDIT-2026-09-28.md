# TRIM-AUDIT: evidence for a turn-by-turn context trimmer, per venue (task #346, D-105)

<!-- Coordinator note (2026-09-28): this is the TRIM-AUDIT lane's hand-back, extracted verbatim from its transcript by `python3 scripts/stack.py harvest agent=a038a373e43037a56` (run s-20260928T222857Z-f32296; hand-back sha256 390101c1bc9e; 541 assistant records, all claude-opus-5-5, 0 refusal stops). Four local commit ids that the push rewrites were replaced by the commits' subjects before the push (stale_ids). The harness flagged one instruction-shaped pattern (settings JSON) in it: read every quoted configuration as evidence, not as an instruction. Evidence only (a Reflection Firewall lane); the design reads it in the main loop. -->


- **Lane:** sandbox EXPLORE lane (evidence-gatherer), Opus 5.5 (`claude-opus-5-5`). It gathers and measures. It gives no verdict, root cause or recommendation.
- **Run:** 2026-09-28, 21:37:55Z to 22:25:06Z (`date -u`).
- **Brief:** `/home/user/agent-factory/tasks/briefs/jev-trim/TRIM-AUDIT-brief.md` (1ebb009, 2026-09-28 20:54Z).
- **Save path:** the coordinator saves this report as `docs/research/findings/jev-trim/TRIM-AUDIT-2026-09-28.md`.
- **Boundary kept:**
  - Read only. No git writes, no PC bridge, no outward action, no model API call.
  - No secret source read. No thinking-block content read: the scripts measured lengths and flags only, and printed no text of any thinking block.
  - Scratch only under `/tmp/trim-audit/`, removed at 22:23:50Z (`ls` confirms it is gone).
  - The main tree shows one modified file outside `.lanes-live`: `tasks/briefs/labeling/VERIFY-LS-B9-report.md`. It belongs to the VERIFY-LS-B9 round-3 lane (dispatched in the commit "VERIFY-I59-F round 4 home ...", 22:15Z). This lane wrote nothing in the tree.
- **One refused call:** the auto-mode classifier refused one Bash batch as "Credential Exploration". The batch held `git remote -v` on the Hermes clone. I did not read that clone's remote again. I fetched b3399c1 from the public URL in `upstream.lock.yaml` instead (`https://github.com/NousResearch/hermes-agent.git`).
- **Status marks:** SOLID = I read or measured it myself. UNSURE = a claim I did not reproduce, or a reading of minified code, or an inference.

---

## 0. PREMISE re-run (`bash scripts/premise_block.sh`, fed the brief's nine `$` commands, 21:37:55Z)

| Line | Brief (20:5xZ) | Now | Status |
|---|---|---|---|
| `git rev-parse --short HEAD` | 2d46ba8 | 417450d. Later still: the commit "VERIFY-I59-F round 4 home ..." at 22:21Z. | SOLID |
| settings grep, README head, hooks/src listing, CONTEXT-BUDGET table, Hermes clone head, `upstream.lock.yaml` commits, `.claude/hooks` listing | as in the brief | identical | SOLID |
| `df -m /` | 25839 used, 12100 avail, 69% | 26113 used, 11826 avail, 69% | SOLID |

- Commits 2d46ba8..417450d: 1ebb009, 98c7f97, d71197e, d773575, 27c1e5d, 417450d. They touch briefs, the ledger, the wiki, two skills, the incident log and the manifest. None touches jev-pruner, the hooks, Hermes or the budget scripts.
- Later, push_clean rewrote the local ids on origin. 417450d now appears as b50711c (same subject, 21:37Z).
- The later commits 82a0686, a430de7, the commit "Task #342 widened ..." and the commit "VERIFY-I59-F round 4 home ..." are LS-B9, VERIFY-I59-F and ledger work.
- The cited ledger lines 1681, 1690 and 1700 still hold the quoted text at the commit "VERIFY-I59-F round 4 home ..." (SOLID, re-grepped 22:21Z).

---

## 1. The seams, per venue

Column "Remove or replace an EARLIER message?" gives the extension's reach as the source states it:
- *add only*;
- *current item only*: the result that is being produced now;
- *request only*: a replaced list for one provider call, with the stored history untouched;
- *persisted*: the stored history changes.

### 1A. This Claude Code coordinator session and its subagents

- **Version:** `claude --version` gives `2.1.283 (Claude Code)`.
- **Binary:** `/opt/claude-code/bin/claude`, 241,556,664 bytes, a closed ELF.
- **Docs:** fetched from `code.claude.com/docs/en/*.md` at 21:41Z. Line numbers refer to those fetched copies; the docs are live and may change.
- **Environment, measured by name:**
  - `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80`. Its source was not found in the repo, `/root/.claude/settings.json`, `/etc/environment`, `.bashrc` or `.profile` (UNSURE).
  - `CLAUDE_CODE_REMOTE=true`.
  - `ANTHROPIC_BASE_URL=https://api.anthropic.com`.
  - `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1`, from the `env` block of `/root/.claude/settings.json`. That file is not version-controlled; I read it at 21:4xZ.
  - Unset: `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, `DISABLE_AUTO_COMPACT`, `DISABLE_COMPACT`, `BASH_MAX_OUTPUT_LENGTH`, `MAX_MCP_OUTPUT_TOKENS`, `CLAUDE_CODE_MAX_CONTEXT_TOKENS`, `CLAUDE_CODE_DISABLE_1M_CONTEXT`.

| # | Cell | Evidence | Remove or replace an EARLIER message? | Status |
|---|---|---|---|---|
| A1.1 | Who builds the message list | The closed binary. The transcript JSONL is the stored record. A `prompt_snapshot` attachment records each segment's system prompt: 11 parts, 28,161 chars, the same in all 6 segments. It also records the tools: 44 tools of 169,442 and 170,096 chars on 09-26; 46 tools of 176,687 chars on 09-28 (measured, §3). | — | SOLID |
| A1.2 | JSON hook events | `hooks.md` 35-69 lists 30 events, PreCompact, PostCompact, PostToolBatch and MessageDisplay among them. All ten names I relied on appear in the binary: grep counts PostCompact 41, PreCompact 38, PostToolBatch 46, `updatedToolOutput` 39. | — | SOLID |
| A1.3 | What JSON hooks may return | `hooks.md` 1023-1051: rewrites exist only for PreToolUse `updatedInput`, PermissionRequest `updatedInput` and PostToolUse `updatedToolOutput`. "UserPromptSubmit: can't replace the prompt". MessageDisplay `displayContent` is "Display-only: the transcript and what Claude sees keep the original" (1040). `additionalContext` is wrapped as a system reminder "at the point where the hook fired" (986) and capped at 10,000 chars; above that it becomes a file path plus a 2,000-char preview (923-927, 1009). Injected text is saved in the transcript and replayed on resume (1021). | PostToolUse: *current item only* ("Replaces the tool's output ... before it is sent to Claude", 2023). All others: *add only*. | SOLID |
| A1.4 | PostToolBatch | Fires "before Claude Code sends the next request". It returns `additionalContext` or blocks the loop (2142-2197). | *add only* | SOLID |
| A1.5 | PreCompact | Input: `trigger` (manual/auto) and `custom_instructions` (null on auto) (3057-3070). It can BLOCK: exit 2 or `decision:"block"`. A proactive auto-compaction is then skipped; a compaction answering a context-limit error fails the request (3051-3053). `systemMessage` and `continue` are discarded (3055). | — | SOLID |
| A1.6 | PostCompact | Input: `trigger` and `compact_summary`. "no decision control. They can't affect the compaction result" (3083-3098). | — | SOLID |
| A1.7 | SessionStart:compact | matcher/source `compact` (1119, 1138). Returns `additionalContext` "at the start of the conversation" (1175). | *add only* | SOLID |
| A1.8 | Function-hook plugin runtime | EARLY ACCESS, enabled here by `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1`. Declarations: `/root/jev-plugins/jev-pruner/types/claude-code.d.ts`, "Written by Claude Code 2.1.274", at jev-pruner 47d017c (2026-09-19). The names are present in the 2.1.283 binary: `session.compact` 32, `turn.step` 29, `prompt.context` 27, `prompt.section` 22, `tool.describe` 23. Their exact semantics at 2.1.283 are not re-derived. | see A1.9-A1.13 | SOLID (names), UNSURE (2.1.283 semantics) |
| A1.9 | `tool.call` | jev-pruner wraps `next()` for Bash and returns `{ result }` with a new stdout (`hooks/fast-jev-output.ts:153-273`). | *current item only* | SOLID |
| A1.10 | `turn.step` | "one model request inside a turn ... A hook rewrites `model` or `effort` going down; the rest is pinned"; `messageCount` "Pinned: the messages are the engine's" (d.ts 8858-8905). It can rewrite the streamed response chunks (8841-8850). | No | SOLID (text) |
| A1.11 | `session.compact` | "Rewrite `instructions` or `messages` on the way down, the messages on the way up, or answer `{ messages }` of your own; `{ skip: reason }` leaves the conversation as it is" (3311-3322). Messages carry an engine `handle`, so a returned list maps to the engine's own messages (7489-7495). `SessionCompacted.messages` is "What the transcript becomes" (7210-7222). A plugin starts it with `$.session.compact()`: trigger `plugin`, "between turns", "It runs through every hook but the calling one ... rejects while a turn runs" (2343-2354). `$.session.usage()` gives the context fill (2324-2342). | *persisted*, at compaction events only, between turns | SOLID (text), UNSURE (behavior at 2.1.283) |
| A1.12 | `prompt.context` and `prompt.section` | `prompt.context`: "the context blocks the engine prepends to a conversation's first user message" (`claudeMd`, `userEmail`, `attachedProject`, `currentDate`); "one left out is not sent" (5773-5779; example `() => ({ blocks: [] })` 3200-3204). `prompt.section`: one named system-prompt section; "null to leave it out" (5961-5977). | Drops fixed-start content (system sections, first-message blocks) | SOLID (text) |
| A1.13 | `tool.describe` | Rewrites a tool's description once per session, cached; "an unstable answer spends the model's prompt cache on every call" (3205-3216). It does not remove a tool. | — | SOLID (text) |
| A1.14 | Auto-compaction window | Settable 100K-1M through `/autocompact`, `--autocompact`, `autoCompactWindow` or `CLAUDE_CODE_AUTO_COMPACT_WINDOW`; the env var wins (`model-config.md` 734-748). Native-1M models compact at about 967K by default, and "Cloud sessions compact as the conversation approaches the model's limit" (752-757). `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` "can't raise the threshold ... Applies to both main conversations and subagents" (`env-vars.md` 196). | — | SOLID |
| A1.15 | Measured compaction point | 12 automatic compactions from 09-25 to 09-28 at preTokens 783,982-793,736. None manual (§3.2). | — | SOLID |
| A1.16 | Built-in clearing of old tool results: docs vs code vs measured | **Docs:** "It clears older tool outputs first, then summarizes the conversation if needed" (`how-claude-code-works.md` 138). **Binary:** a "time-based microcompact" / "KEEP-RECENT MC" path. It replaces results with `[Old tool result content cleared]` (4 hits) and keeps the last `keepRecent` results (default not readable). It runs only when `tokensSaved >= 20000` (`xar=20000`), and saves each cleared content first (`persist`). It sends body field `context_hint` under beta `context-hint-2026-04-09`, only for `querySource` starting with `repl_main_thread`; on a server "context-hint reject" it clears and retries. It writes `microcompact_boundary` records. **Measured:** the main transcript (777,005,680 bytes) has 0 `"subtype":"microcompact_boundary"`, 0 `[Old tool result content cleared]` and 0 `context_hint` (grep -c). | *persisted* (engine-internal, not a plugin seam) | SOLID (docs text, string counts, measured zeros); UNSURE (reading of minified code: trigger, default, subagent scope) |
| A1.17 | API context management the binary uses | Beta constant `context-management-2025-06-27` (3 hits). Function `qlt` returns `{edits:[{type:"clear_thinking_20251015",keep:"all"}]}` when thinking is present. `clear_tool_uses_20250919`: 0 hits. `compact-2026-09-04`: 0 hits. `compact_20260112` appears only inside an SDK deprecation message. | — | SOLID (strings); UNSURE (whether `qlt` is sent on every main request) |
| A1.18 | Tool-output caps | Bash: inline up to about 30,000 chars; past that a file path plus a 2,000-char preview; failures get a 10,000-char head and tail (`tools-reference.md` 161-174). Measured: the session folder holds `tool-results/` with 220 files, 301,374,704 bytes, 11 of them created since 09-26. | — | SOLID |
| A1.19 | Subagents | Each has its own window, "sized by its own model"; it auto-compacts by the same logic; its transcript is a separate file (`sub-agents.md` 1057, 1078, 1118-1141). Measured: 730 subagent files, 648,949,962 bytes. This lane itself received Hermes's 95,906-byte `AGENTS.md` as "tool.call hook additional context" after one Read of `agent/context_engine.py` at 527da60. | — | SOLID |
| A1.20 | User-side removal paths | `/compact [instructions]`; `/rewind` → "Summarize from here" / "Summarize up to here" ("original messages stay in the session transcript") (`checkpointing.md` §Rewind and summarize); `/clear`. | *persisted*, by the user only | SOLID |
| A1.21 | Gateway seam | `ANTHROPIC_BASE_URL` points Claude Code at a gateway. The rollout doc says a gateway must "Forward headers and body unchanged" (`llm-gateway-rollout.md` 34). Whether a cloud (CCR) session honors a changed base URL was not checked. | a gateway can rewrite anything; the doc says forward unchanged | SOLID (doc); UNSURE (CCR) |
| A1.22 | Prompt-cache rule | "The match is exact, so a change anywhere in the prefix recomputes everything after it" (`prompt-caching.md` 17). The main conversation gets a 1-hour TTL on a subscription within plan usage (264-277). Compaction invalidates the conversation layer (175-184). `/rewind` re-hits the earlier cache (244-248). | — | SOLID |
| A1.23 | Coordinator's reading in D-105 | "Claude Code owns this session's history (a hook cannot delete past messages)" (`docs/08_DECISION_LOG.md:116`). JSON hooks: consistent (A1.3-A1.7). Function hooks: `session.compact` can hand up a message list of its own, between turns (A1.11). Both sides recorded. | — | SOLID (both texts) |

### 1B. Hermes: the lanes run b3399c1, the proof/production pin is 527da60

**Pins.**
- b3399c1 is `upstream.lock.yaml:242` (the lane runtime). Author and commit dates are 2026-09-08 14:05:24 +0000 (bot author, GitHub committer). I fetched it into scratch, blob-less, depth 1.
- 527da60 is `upstream.lock.yaml:12`. Author date 2026-09-02 03:45:08 -0700, committer 06:36:16 -0700. The clone `/home/user/nerdherderdani/hermes-agent` has a clean tree (0 porcelain lines).

**Layout differs.** The two pins differ in size and layout:

| File | 527da60 | b3399c1 |
|---|---|---|
| `agent/conversation_loop.py` | 9,229 lines | 1,605 lines |
| `agent/context_compressor.py` | 8,944 lines | 4,910 lines |
| `run_agent.py` | 10,124 lines | 1,544 lines |
| `agent/context_engine.py` | 489 lines | 242 lines |

b3399c1 splits the loop into `agent/turn_*.py`. The branch topology between the two pins is not known (UNSURE).

| # | Cell | 527da60 | b3399c1 | Remove or replace an EARLIER message? | Status |
|---|---|---|---|---|---|
| B1 | Pluggable engine (ABC) | `agent/context_engine.py:1-26`: config `context.engine`, default `"compressor"`, one engine active. Base defaults: `threshold_percent` 0.75, `protect_first_n` 3, `protect_last_n` 6 (121-123). | same ABC; seams at lines 109, 120, 142 | — | SOLID |
| B2 | `select_context()` | 215-279: "choose/replace the context for THIS request ... MUST NOT be treated as persisted transcript state"; "Unlike the `pre_llm_call` plugin hook ... `select_context()` may *replace* the message list". It runs before cache-control and the sanitizers. Helper `_apply_context_engine_selection` (`conversation_loop.py:1845-1927`) is fail-open: an exception, `None` or an empty list keeps the original. Inputs are cloned. `budget_tokens` = `context_length`. | helper at `conversation_loop.py:1153`; call at `turn_request_assembly.py:142` | *request only* | SOLID |
| B3 | How often B2 runs | Inside the per-request `while` loop (`conversation_loop.py:2244`, loop at 4-space indent; call at 2688, 8-space indent, with no 4-space line between) | `conversation_loop.py:1484-1488`: each loop pass runs `begin_iteration`, `prepare_iteration`, `assemble_api_request` → `turn_request_assembly.py:106,142` | every provider request | SOLID |
| B4 | `compress()` | 163-190: "returns a (possibly shorter) list ... free to summarize, build a DAG, or do anything else" | same | *persisted* | SOLID |
| B5 | Built-in compressor defaults | `ContextCompressor.__init__`: threshold 0.50, protect_first_n 3, protect_last_n 20, summary_target_ratio 0.20, `threshold_tokens_cap`, `proactive_prune_*`, `tail_mode` "lean" (`context_compressor.py:3419-3441`). Config: enabled True, threshold 0.50, threshold_tokens None, target_ratio 0.20, tail_mode lean, protect_last_n 20, min_tail_user_messages 1, max_attempts 3 (`hermes_cli/config_defaults.py:855-904`). | config: threshold 0.50 (536), tail_mode lean (546) | — | SOLID |
| B6 | Small-window floor | `_SMALL_CTX_WINDOW_LIMIT = 512_000`, `_SMALL_CTX_THRESHOLD_PERCENT = 0.75` (1359-1360). `_effective_threshold_percent`: under 512K "trigger at no less than 75%" (3348-3362). `_compute_threshold_tokens` works on `context_length - max_tokens`, floored at `MINIMUM_CONTEXT_LENGTH` = 64,000 (`agent/model_metadata.py:465`) and capped at 85% (3364-3415). | same constants (987-988) | — | SOLID |
| B7 | Proactive tool-result prune (deterministic, no LLM) | `prune_tool_results_only` (4397-4486) runs `_prune_old_tool_results` (4094-4163): (1) dedup byte-identical results, keeping the newest; (2) replace non-tail results over `min_prune_chars` (8,000) with a one-line summary such as "[terminal] ran `npm test` -> exit 0, 47 lines output"; (3) truncate large tool-call args; (3.5) retire old images. Gates: `proactive_prune_tokens` (0 = off), a minimum reclaim of 4,096 tokens, a re-arm after regrowth. "PROMPT-CACHE CONTRACT: a committed prune ... invalidat[es] the cached prefix". Persisted through `session_db.archive_and_compact`. Config `proactive_prune_tokens: 0` (904). | 2822; config 559, 562, 565 | *persisted* | SOLID |
| B8 | Micro-compaction (per completed turn, LLM) | `compression.micro_compact: False`, `every_n_turns` 1, `defrag_threshold_tokens` 2000 (`config_defaults.py:927-946`). `docs/micro-compaction.md` (401 lines): after each completed turn it folds the oldest un-absorbed exchange into a rolling summary through the auxiliary model; "Your messages are never compacted"; "breaks the provider prompt-cache prefix every turn" (202-240). | `agent/micro_compaction.py:1-5, 199-259` ("OFF by default: every pass rewrites the prompt prefix"); config 566-575 | *persisted* | SOLID (code and defaults); UNSURE (doc measurements, see §5) |
| B9 | General plugin hooks | `VALID_HOOKS`, 37 names (`hermes_cli/plugins.py:163`, parsed with `ast`). `website/docs/user-guide/features/hooks.md:441-452` (last change 091cc0e8be, 2026-08-02): `transform_tool_result` "before conversation append; first string replaces the result"; `transform_terminal_output`; `pre_llm_call` "Once per turn before the loop ... injected into the user message"; `pre_api_request` "Observer ... return ignored". | the same 37 names (`plugins.py:107`) | `transform_*`: *current item only*; `pre_llm_call`: *add only*; `pre_api_request`: none | SOLID |
| B10 | Plugin middleware | `hermes_cli/middleware.py:1-40`: kinds `tool_request`, `tool_execution`, `llm_request`, `llm_execution`. `apply_llm_request_middleware` may return `{"request": {...}}` "to replace the effective provider kwargs"; call at `conversation_loop.py:3404-3421` receives `api_kwargs` (`messages` or `input`) on each provider attempt. | same kinds (`middleware.py:24-26`); call at `agent/turn_api_request.py:151` | *request only*, after the sanitizers | SOLID |
| B11 | The fail-closed `pre_tool_call` policy hook | "first valid `block` or `approve` directive wins, and `modify` returns are shallow-merged into the tool arguments" (hooks.md:441) | same hook name | tool arguments only | SOLID |
| B12 | ACP path (production: `buzz-acp` → `hermes-acp`) | `acp_adapter/session.py:615, 687` builds `AIAgent`; `acp_adapter/server.py:2075` calls `run_conversation(`: the same loop and seams | `session.py:421`; `server.py:768` | — | SOLID |
| B13 | Tool-output caps | `tools/file_tools.py:65` `_DEFAULT_MAX_READ_CHARS = 100_000`; config `file_read_max_chars: 100_000` (760); terminal head 40% / tail 60% of `get_max_bytes()` (`tools/terminal_tool.py:3739-3750`); `max_result_size_chars=100_000` (4259) | not checked | — | SOLID (527da60) |
| B14 | Native server-side compaction | `agent/native_compaction.py:1-40`: OpenAI Responses `context_management` compaction, "gpt-5.6 family only", "Direct OpenAI routes only ... Every other Responses surface (xAI, GitHub/Copilot, relays, local servers) never sees the field" | not checked | — | SOLID (527da60) |
| B15 | Upstream's own policy | AGENTS.md at 527da60: "Per-conversation prompt caching is sacred ... Anything that mutates past context ... We do not do it (the one exception is context compression)" | — | — | SOLID (quoted) |

**Per-profile context settings, from what the repo holds** (the live PC profiles are PC only):

| Cell | Evidence | Status |
|---|---|---|
| Lane profile `context_length` | `harness-ports/bin/lane-profile.sh` (cda2d3d, 2026-09-26 06:58Z) writes `models.<id>.context_length` for the local models from the quadlet's `[Container] MAX_LEN`, falling back to 131072 with a stderr line (18, 29-71, 104-157, 479-480). HCTX1 landed 847d3eb (2026-09-26 04:27Z); HCTX1-R1 cda2d3d (06:58Z); both GATED-PENDING-VERIFY. | SOLID (code) |
| The owner's Hermes profile (cloned per lane) | Measured 2026-09-15: `compression.threshold: 0.5`, `protect_first_n: 3`, `protect_last_n: 20`, `file_read_max_chars` unset (100,000), no `model.context_length` (`docs/research/findings/RESEARCH-FINDINGS-1-VERIFIED.md`, table row "Hermes profile", 7537910 2026-09-15). The current value is PC only. | SOLID (2026-09-15); current NOT measured here: PC only |
| Server context | D-097 (`docs/08_DECISION_LOG.md:108`): vLLM `MAX_LEN=131072`, KV 222,822 tokens; OmniRoute reports context_length 200,000 for both local combos. D-099 (`:110`): after `GPU_UTIL` 0.96 the KV pool is 215,112 tokens, 1.64x concurrency at 131,072. QJ2: `--max-model-len 131072` read from the process args (`tasks/briefs/jev-laya/QJ2-report.md:87`). | SOLID (as recorded) |
| **Contradiction:** where a lane compacts | Side 1: D-097 says "a lane compresses near 100k (the profile's threshold 0.5)" with 200,000 reported. Side 2: the code at both pins raises any threshold under a 512K window to 0.75 (B6), which gives about 150,000 at 200,000 and about 98,304 at 131,072 before the `max_tokens` reservation. The incident of 2026-09-14 15:5xZ also reads "Hermes compacts only at 75 % of the context length OmniRoute reports ... so it never compacts below ~150k" (`docs/INCIDENT-LOG.md:574`). Not resolved here. | SOLID (both texts) |

### 1C. OmniRoute, the model egress

- **Pin:** 488f57e, 2026-09-04 00:45:38 -0300 (`upstream.lock.yaml:24`).
- **Checkouts read:** `/home/user/diegosouzapw/omniroute` and `/home/user/nerdherderdani/OmniRoute`, both at 488f57e, 0 porcelain lines.

| # | Cell | Evidence | Status |
|---|---|---|---|
| C1 | Request compression pipeline | `docs/compression/COMPRESSION_GUIDE.md` (f81ce2a2, 2026-09-03), 11-119. Modes: Off; Lite (~15%: whitespace, dedupe system prompt, "compressToolResults"); Standard (Caveman filler removal); Aggressive ("Message Aging — older messages get progressively compressed", tool-result summarization, tool pair guards, "Context Window Awareness"); Ultra ("Heuristic Pruning — removes messages below relevance threshold", code thinning, "Binary Search Truncation"); RTK (49 command filters for tool output); Stacked (RTK then Caveman). | SOLID (doc text) |
| C2 | Progressive aging (turn distance) | Guide 376-415: turns 0-3 verbatim, 4-8 lite, 9+ caveman, 20+ "Heavily summarized or dropped"; "always on for aggressive and ultra"; `open-sse/services/compression/progressiveAging.ts` tags `[COMPRESSED:aging:<tier>]`. | SOLID (text) |
| C3 | Hard budget | `hardBudget.ts:1-9`: "compress to ≤ N cl100k tokens ... drops the lowest-saliency units ... Units containing FORCE_PRESERVE_RE anchors (errors, numbers, URLs, code) are never dropped". Deterministic. | SOLID (text) |
| C4 | Cache-aware compression | Guide 329-374: with `cache_control` on a caching provider it downgrades aggressive/ultra to standard, skips the system prompt and uses deterministic transforms only; "always on". | SOLID (text) |
| C5 | Defaults at the pin | `open-sse/services/compression/types.ts:420-423`: `enabled: false`, `defaultMode: "off"`, `autoTriggerTokens: 0`. | SOLID |
| C6 | Controls | Dashboard, auto-trigger threshold, per-combo mode and pipeline. Per-request header `x-omniroute-compression` has "the highest precedence"; values `off`, `default`, `engine:<id>`, `<combo>`; the response echoes `X-OmniRoute-Compression: <mode>; source=<source>` (guide 185-238). | SOLID (text) |
| C7 | Delegated Anthropic context editing | `open-sse/config/contextEditing.ts:1-60` (d898d1a9, 2026-09-01): adds `clear_tool_uses_20250919` to `context_management.edits[]` on Claude-provider requests when enabled (trigger 100,000; keep 3). Wiring: `open-sse/handlers/chatCore.ts:1339-1365`. | SOLID (code text) |
| C8 | What S0-04 pins | `proofs/S0-04/check_compression.py:1-45` (a525376, 2026-09-25): A1, the Hermes-side request carries `x-omniroute-compression: off`; A2, the response reports off; A3, the stub upstream's received request equals the sent fixture by JSON value and wire byte length. Stated residual: "a re-serialization that PERMUTES keys without changing the total byte length is invisible". Legs `off`, `off-large`, `config` (`spec.json`, 6d54935, 2026-09-08). Live capture 2026-09-19: the value was `off; source=request-header` on both legs (`LIVE-CAPTURE-FINDINGS.md:1-35`, 1428c0b). | SOLID |
| C9 | Header in the proof config vs production | The proof-owned `proofs/S0-04/hermes/config.yaml:22-29` (ec93bd2, 2026-09-19) carries `extra_headers: {x-omniroute-compression: "off"}`. On 2026-09-19 "the live production `omniroute-fedora` provider carries NO `extra_headers` at all" (`LIVE-CAPTURE-FINDINGS.md` Deviation 1). The lanes' and production's current headers and OmniRoute's live compression settings: NOT measured here: PC only. | SOLID (texts); live unknown |
| C10 | A measured transform in transit | "OmniRoute drops it; vLLM keeps it": the final assistant turn's `reasoning_content` (`docs/research/findings/j2b-variants/qwen27b/TRANSPORT-2026-09-24.md:51-52, 76`, 2969794, 2026-09-25). | SOLID (committed finding) |
| C11 | Which traffic passes through OmniRoute | System 2 (Hermes lanes, production) does. System 1 (the Jevs) "connects directly to its local model server" (D-082, `docs/08_DECISION_LOG.md:93`). This Claude Code session goes to `https://api.anthropic.com` (env). | SOLID |

### 1D. Claude API features

Docs fetched from `platform.claude.com/docs/en/*.md`, 2026-09-28 about 22:0xZ. Line numbers refer to the fetched copies.

| # | Cell | Evidence | Status |
|---|---|---|---|
| D1 | Context editing | Beta `context-management-2025-06-27`. `clear_tool_uses_20250919`: `trigger` default 100,000 input tokens, `keep` 3 tool uses, `clear_at_least`, `exclude_tools`, `clear_tool_inputs` (context-editing 28-40, 1730-1738). "applied server-side ... Your client application maintains the full, unmodified conversation history" (61-65). The response reports `context_management.applied_edits` with `cleared_input_tokens` (1740-1792). | SOLID |
| D2 | Thinking clearing | `clear_thinking_20251015`. Default "Keep all prior thinking": Opus 4.5 and later, Sonnet 4.6 and later, all Fable and Mythos; "last turn only" for earlier models and Haiku (42-59, 920-926). | SOLID |
| D3 | Editing and caching | Clearing tool results "Invalidates cached prompt prefixes ... Use the `clear_at_least` parameter"; kept thinking preserves the cache, cleared thinking invalidates it at the clearing point (67-73). | SOLID |
| D4 | Server compaction | Two kinds (compaction overview page). "On demand": beta `compact-2026-09-04`, top-level `compaction` parameter, can keep recent turns word for word, can run in the background. "At a token threshold": `compaction-threshold` page; the SDK string in the binary names the edit `compact_20260112`. | SOLID (doc) |
| D5 | Memory tool | "operates client-side: Claude requests file operations, and your application executes them"; files under `/memories` (memory-tool 11, 29-31). | SOLID |
| D6 | Preserved-thinking prefix check | Applies to Fable 5.1, Opus 5.5 and Sonnet 5.5. "a thinking block stays valid only while everything you sent before it is unchanged": `system`, `tools`, every earlier message (preserved-thinking 72-79). Default `"error"` is a 400. `"drop_block"` drops the failing block and all later thinking, and "the prompt cache restarts at the edit"; it needs beta `thinking-binding-controls-2026-08-01` (88-118). Enforced by default for accounts created on or after 2026-08-31 00:00 UTC; on older accounts only when `prefix_mismatch_behavior` is set (14). | SOLID |
| D7 | What counts as an edit | "Clear or shorten an earlier `tool_result` ... Invalid for every later thinking block"; "Edit, reorder, or delete any earlier ... message: Invalid"; "Server-side compaction or context editing removes or replaces content: Valid"; "Remove `thinking` blocks from the start of the history, from the end, or all of them: Valid (the model loses that reasoning)" (404-428). "Nothing changes for you if Claude Code ... builds your requests" (18). "Trim context on the server" (1414-1422). "A library, proxy, or gateway ... its own rewrites count as edits" (1681-1690). "Cutting turns out of the middle ... invalidates every thinking block after them" (1672-1676). | SOLID |
| D8 | Venue fit, as facts | **This session:** every main-thread request in the window ran on `claude-opus-5-5` (3,787 of 3,787 in the walk, §3), and the binary sends `clear_thinking` with keep `all` (A1.17). Whether this account was created on or after 2026-08-31: unknown. **OmniRoute** can attach `clear_tool_uses` for Claude providers (C7). **Hermes:** no Anthropic `context_management` use found in `agent/` or `plugins/model-providers` at 527da60; the hits are the Codex/OpenAI `context_management` (B14). **Local Qwen lanes:** the Claude API features do not apply to that model. | SOLID (facts); UNSURE (account date) |

---

## 2. What can judge "useless to the current work"

| # | Judge | Question it answers | Input it needs | Accuracy (committed) | Latency (committed) | Status |
|---|---|---|---|---|---|---|
| E1 | jev-pruner (`fast-jev-output`, 47d017c, 2026-09-19; read only) | Per 20-line chunk, one `noul`: "Chunk N contains at least one line that should remain available to the agent for its ongoing task" (`src/output.ts:209-211`). Context prompt at `output.ts:17`. | The current Bash stdout (or the engine-saved file). `history` = `$.session.messages()`: the main conversation, newest 4,096 messages (hook:193; README 80-91). `goal` = the last 3 typed prompts, 500 chars each (hook:112-123). | Author-reported on 2026-09-18 with hosted `jev-latest`: standard 8/8 retention, 83% mean reduction; accuracy 36/36, 87%; real captures 10/10, 54%; needle matrix 9/9 (`evals/README.md:245-280`). Also 240 ms mean latency (`docs/research/findings/jev-audit/jev-pruner-evidence.md` row 6.7, fb90a0d, 2026-09-22). | author-reported only | SOLID (code); UNSURE (author numbers) |
| E1a | … its limits and endpoint | Floor 10,000 estimated tokens, which config cannot lower (`output.ts:7`; hook:77,181). Documents, JSON, diffs and `cat` are never cut. Drop only at ≤ 0.1 and below `keepThreshold` 0.5 (`retention.ts:37,54`). 30,000 tokens per request, 200 chunks (`output.ts:11,13`); `maxStateTokens` 25,000; at most 12 requests (hook:19-28,208-211). | **Endpoint:** default `https://api.typesafe.ai/v1/systemone` (`src/jev.ts:1`); configured here as `http://127.0.0.1:47411/v1/systemone` (pluginConfigs, 21:4xZ). **Key:** it requires an API key or it returns the result unchanged (hook:189-191). **Archive:** `.claude/fast-jev-output/bash-<id>.txt`, kept (README 59-68; hook:18,198). **Scope:** replaces only the current result (hook:268-273). | — | — | SOLID |
| E1b | … the committed replay on this session (P1) | Same question, on the local Laya CPU scorer at the 127.0.0.1:47411 port (2 threads) | 3,153 Bash results of 2,000 chars or more | Pruned 0. 254 reached the scorer and all failed open. Every answer scored 0.5163-0.5988. The scorer never saw the chunk: the state is kept left-first, `max_len` 1024, and the chunk comes last (`docs/research/findings/jev-pipes/P1-replay-2026-09-25.md:3-34, 52-69`, a09dda3, 2026-09-25). | p50 3,800.9 ms per chunk question; p50 12,019.1 ms per result, on a contended box (P1 §6) | SOLID (committed) |
| E1c | … right now | `ss -ltnp`: nothing listens on 127.0.0.1:47411; no laya process (22:0xZ) | — | — | — | SOLID |
| E2 | Laya `typed-decisions` (rev 1c5edc17…) | Typed `noul`/`choice`/`score` questions over a state | state ≤ 1,024 tokens, head 256 | J2: `ap.violates_row` top-1 0.05 vs lexical 0.59; `v1.finding_class` accuracy 0.21 vs majority 0.43; "Laya has no usable signal on either type. Both are rejected by KC-J3" (`docs/research/findings/J2-SIGNAL-PROBE-2026-09-24.md:10-11, 20-43`, 9eed18e 2026-09-24). J2c on whole findings: 0.17 (§6). Head checkpoint "rejected on every KC-J3 line" (commit d36ba41, 2026-09-25). | J0: p50 260 ms per question in the sandbox (4 threads), 336 ms on the PC (`JEV-LEVERAGE-AUDIT-2026-09-24.md:67`, f601035) | SOLID (committed) |
| E3 | `laya-systemone` on the PC (D-082, D-099) | Same Laya questions | — | as E2 | "`--device auto`, running on the CPU", holding a 256 MiB CUDA context beside vLLM (`docs/08_DECISION_LOG.md:110`) | SOLID (as recorded) |
| E4 | Qwen3.8-27B teacher (simple-jev pattern, D-079; direct vLLM, D-082) | `choice`/`noul` from next-token label logprobs | Token-id path to vLLM (`qwen_jev.py`) | QJ2: v1 titles choice 0.40-0.43 (majority 0.43); whole findings 0.49-0.54; `ap_choice` top-1 0.65-0.67 vs lexical 0.59; `ap_noul` top-1 0.03-0.39 (`tasks/briefs/jev-laya/QJ2-report.md:99-135`, fe1d471 2026-09-25, GATED-PENDING-VERIFY) | From the committed run summaries: v1 200 requests in 170.7-221.2 s (0.85-1.11 s each); `v1_blocking` 100 in 24.9-31.1 s (0.25-0.31 s); `ap_noul` 100 in 487.7-646.6 s (4.9-6.5 s, 16 rows each) (`j2b-variants/qwen27b/*/run-summary.json`) | SOLID (numbers as committed); UNSURE (pending verify) |
| E5 | OpenJev (codiv.ai, hosted; not called) | `choice`/`noul` | scrubbed state | v1 whole findings `choice` 0.54 (Haiku 4.5: 0.60, majority 0.43); `ap_choice` top-1 0.58, top-3 0.74 (J2 page §7, 176-214). S1-RATE `rel` exact 0.2692 on 52 sections (ledger `todo/BUILD-TASKLIST.md:1690`). | ~1.05 s pacing (J2 §7) | SOLID (committed) |
| E6 | RWKV-7 G0 0.4B zero-shot | same | long input | Under or at the baselines on every line (`j2b-variants/rwkv7-g0/2026-09-24-window2/README.md:13-25`, 0f8c1b5) | not given there | SOLID |
| E7 | S1 layer (`.claude/hooks/system1-context.py`, cf8a186, 2026-09-26) | Which skill sections match this tool input or prompt | tool input or prompt text | No model: keyword and idf matching, "no instrument, no network, no model" (1-49). Adds only, once per window, ≤ 2,048 bytes per tool call and ≤ 4,096 per prompt. | "a prompt plans in 23 ms at the median and 36 ms at p95"; the whole process 64/90 ms (header) | SOLID |
| E8 | S1-RATE (the agent's own scores) as a label source | relevance and use of each injection | the injection plus the live context | Labelers that see only the recorded prompt or tool input miss the live scores: local Qwen `rel` exact 0.3846 [0.2647, 0.5204] on 52; OpenJev 0.2692 [0.1677, 0.4025]; bar 0.75 (ledger 1681, 1690) | — | SOLID (committed) |
| E9 | Labels and stacks (D-103, LS-B9) | none: a label names a fixed tool sequence; "not jev, decide" (`docs/08_DECISION_LOG.md:114`) | label plus typed parameters | deterministic | — | SOLID (ruling text); stack contents not read (the lane is live) |
| E10 | Task list as a view of the ledger (D-102) | which tasks are active (pending or in progress) | ledger headlines | Deterministic grammar (`scripts/task_sync.py:1-25`, 6bb590b 2026-09-28 19:37Z). Task-reminder share of re-sent tokens, by `inject_cost.py`: 12.0% (whole session to 2026-09-25, CONTEXT-BUDGET) and 0.9% (slice 09-25 21:58Z to 09-28 21:44Z, §3.10). The two windows differ, so the cause of the change is not attributed. | — | SOLID |
| E11 | Hermes built-ins | compressor summary (LLM); micro-compaction (auxiliary LLM, B8); proactive prune (size and dedup rules, no model, B7) | the message list | Upstream-reported only (§5) | micro passes 2-37 s, median about 31 s on a small local model (§5) | SOLID (code); UNSURE (upstream numbers) |
| E12 | OmniRoute heuristics | relevance and saliency scores (Ultra, hard budget), turn distance (aging) | the request body | deterministic; no accuracy found | "<1ms" for lite (guide) | UNSURE (upstream text) |

---

## 3. This session, measured (main transcript; 2026-09-26 and 2026-09-28; there are no 2026-09-27 records)

**Method.**
- **Source:** `/root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl`, pinned at 777,005,680 bytes at 21:51:34Z. First record 2026-09-02T21:10:09Z.
- **Streaming:** one pass per script, with `json.loads` per line and 9 unparseable lines in the file.
- **Request:** the first assistant record of each `requestId`, `isSidechain` false. Its context = `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`, the committed walker's definition (`scripts/jev_pipes/transcript.py:132-149`, e8c14bf 2026-09-25). `output_tokens` is the maximum over the request's records.
- **Segments** start at `system/compact_boundary` records.
- **Window:** the walk starts at the 09-25 offset 698,757,094. The report covers timestamps ≥ 2026-09-26, so the segment open at 09-26 00:12Z is walked from its own start (09-25 21:58:11Z).
- **Excluded:** 6 `<synthetic>` assistant records with zero usage (09-26). One of them, at 12:26:32Z, gave a 776,076 → 0 pair.
- **Sizes:** the API's token counts are exact. The per-source split of user-side content is modeled from characters (fit in §3.4). Assistant output uses the exact `output_tokens`. Thinking is bounded from output tokens minus the visible characters at 3.0-4.06 chars per token.
- **Scripts:** ad-hoc Python in scratch, now removed per the brief. The two committed probes were run unchanged (§3.10).
- **Noise:** counts are deterministic, so there are no timing measurements and box contention does not apply. The composition tables use every third over-budget request (525 of 1,573 at 100k; 524 of 1,570 at 131,072), stated as a sample.

### 3.1 Per UTC day

| Day | Active span | Requests | Context median | p90 | max | min | Compactions |
|---|---|---:|---:|---:|---:|---:|---:|
| 2026-09-26 | 00:12:50Z to 14:24:45Z | 781 | 545,883 | 733,680 | 783,173 | 130,278 | 2 |
| 2026-09-27 | no records (the day's first-offset jumps from 744,582,551 to 758,644,821) | 0 | — | — | — | — | 0 |
| 2026-09-28 | 12:17:26Z to 21:44:16Z (pin) | 792 | 460,505 | 714,430 | 783,147 | 127,359 | 3 |

All 3,787 non-synthetic main-thread requests from 09-25 to 09-28 name model `claude-opus-5-5`. D-105's figure is a median 461,918 per request (whole session to 2026-09-25).

### 3.2 Compactions (`compactMetadata`)

| Time | Trigger | preTokens | postTokens | durationMs |
|---|---|---:|---:|---:|
| 2026-09-25 21:58:11Z (opens the first reported segment) | auto | 784,009 | 39,609 | 130,256 |
| 2026-09-26 03:41:24Z | auto | 787,091 | 38,702 | 148,799 |
| 2026-09-26 07:47:54Z | auto | 783,986 | 42,362 | 116,486 |
| 2026-09-28 12:20:55Z | auto | 793,736 | 40,047 | 205,638 |
| 2026-09-28 14:48:35Z | auto | 784,251 | 37,390 | 137,729 |
| 2026-09-28 18:57:06Z | auto | 785,458 | 38,324 | 135,830 |

The seven compactions earlier on 09-25 have preTokens 783,982-788,490. Whole file: 0 microcompact records (A1.16).

### 3.3 The start of each segment: system plus tools vs messages

System plus tools = the first request's context − `postTokens`.

| Segment first request | Context | System prompt + tools | Post-compaction messages (`postTokens`) | Requests reported |
|---|---:|---:|---:|---:|
| 09-25 21:58:15Z | 131,080 | 91,471 | 39,609 | 133 |
| 09-26 03:41:31Z | 130,278 | 91,576 | 38,702 | 304 |
| 09-26 07:47:59Z | 137,086 | 94,724 | 42,362 | 344 |
| 09-28 12:21:01Z | 131,279 | 91,232 | 40,047 | 307 |
| 09-28 14:48:46Z | 127,359 | 89,969 | 37,390 | 268 |
| 09-28 18:57:11Z | 129,409 | 91,085 | 38,324 | 217 |

What the start messages hold, modeled at chars/4.35 (an upper bound; listings are counted at record size): re-injected skill bodies ≈ 18,678; CLAUDE.md ≈ 10,068-10,169; listings 8,981-22,722; the compaction summary 4,082-5,874; harness file re-reads 1,179-7,007; hook context 2,334-2,527. Their sum exceeds `postTokens`, so these are upper bounds (UNSURE). The docs cap re-injected skills at 5,000 tokens each and 25,000 in total (`context-window.md` 1606).

### 3.4 Growth per request and what it is made of (1,568 consecutive pairs within one segment)

**Growth (Δcontext):** median 1,565, p90 4,161, p99 12,616, max 26,740; 0 negative pairs.

**Is thinking sent back?** I took the 28 pairs whose previous output was at least 3,000 tokens while its visible text was under 2,000 chars and the new user content under 2,000 chars. Median Δcontext / previous output = **1.10** (range 1.01-1.26). One example: an output of 11,108 tokens with 364 visible chars grew the next request by 11,371. The stored thinking text is empty in 1,280 of 1,485 thinking blocks (all 1,485 carry a signature).

**Fit:** (Δcontext − previous output_tokens) = 223.9 + user-side chars / 2.90, R² = 0.848.

**Decomposition** of Σ Δcontext 3,431,987:

| Source | Share of growth | Mean tokens per request |
|---|---:|---:|
| Prior thinking (output − visible/3.0; low estimate) | 36.1% (40.3% at visible/4.06) | 791.0 |
| Visible assistant output (text and tool inputs) | 15.9% | 347.2 |
| Bash results | 14.2% | 312.0 |
| Fixed per-request constant (fit intercept) | 10.2% | 223.9 |
| Typed or queued user messages | 3.7% | 81.5 |
| Hook context | 3.1% | 67.8 |
| Read results | 2.5% | 55.2 |
| Listings (upper bound) | 2.2% | 49.0 |
| Meta text | 2.2% | 48.4 |
| Task reminders | 1.8% | 40.1 |
| Nested-memory instruction files | 1.8% | 38.9 |
| MCP results | 1.3% | 27.7 |
| Skill bodies | 1.2% | 26.4 |
| Edited-file snippets | 1.2% | 25.9 |
| `total_tokens_reminder` | 0.7% | 16.0 |
| Agent hand-back notifications | 0.5% | 10.5 |
| CLAUDE.md | 0.4% | 9.7 |

- Mean modeled growth: 2,190 tokens per request.
- Tool results added per request: median 136 tokens, p90 931, p99 4,298, max 9,774; 111 of 1,568 requests add none.

### 3.5 Budgets (all 1,573 requests)

| Budget | Requests over | Excess median | p90 | max | Segment starts over the budget |
|---|---:|---:|---:|---:|---:|
| 100,000 | 1,573 of 1,573 (100.0%) | 398,113 | 627,819 | 683,173 | 6 of 6 |
| 131,072 | 1,570 of 1,573 (99.8%) | 367,504 | 596,747 | 652,101 | 3 of 6 |

The steady-state removal per turn equals the growth per request (§3.4): median 1,565, max 26,740 tokens.

### 3.6 What an over-budget request holds (sample, modeled)

Budget 100,000; every third request, n=525. The 131,072 sample (n=524) is within ±1% on every row.

| Part of the context | Median | p90 |
|---|---:|---:|
| Assistant output since the segment start (exact tokens, thinking included) | 181,670 | 316,899 |
| … of which prior thinking (low-high) | 132,988-145,553 | 222,523-247,247 |
| … prior thinking as a share of the WHOLE context | 25.8% | 31.4% |
| Bash results | 58,431 | 96,528 |
| Fixed per-request constant | 35,152 | 63,364 |
| Nested-memory instruction files | 15,254 | 15,254 |
| Listings (upper bound) | 8,702 | 21,820 |
| Hook context | 7,267 | 17,668 |
| Task reminders (all) | 6,143 | 10,488 |
| … superseded task reminders (all but the newest) | 5,831 | 10,113 |
| Typed or queued user messages | 4,526 | 28,037 |
| Read results | 4,143 | 18,247 |
| … superseded Read copies (same file read again later), every third request | 0 (103 of 525 have any; max 18,428) | 2,402 |
| Tool results aged 0-10 requests | 3,367 | 8,517 |
| Tool results aged 11-50 requests | 13,713 | 28,198 |
| Tool results aged 51-200 requests | 49,241 | 66,927 |
| Tool results aged 201+ requests | 0 | 49,431 |
| Harness edited-file snippets | 0 | 11,575 |
| Unattributed (context − segment start − modeled growth) | 1,273 | 14,726 |

### 3.7 Arithmetic under stated rules

These rules are arithmetic, not policies. Cell = the requests where the rule's tokens ≥ the excess.

| Rule | 100,000 (n=525) | 131,072 (n=524) |
|---|---:|---:|
| R1: tool results older than 50 requests | 0 | 0 |
| R2: tool results older than 10 requests | 0 | 0 |
| R3: R2 + superseded task reminders + all prior thinking (low estimate) | 0 | 0 |
| R4: all growth since the segment start | 0 | 262 |
| R5: the segment start alone exceeds the budget | 525 | 262 |
| R6: system prompt + tools alone exceed the budget | 0 | 0 |

### 3.8 Turns: how often a between-turn hook could act (A1.11)

| Turn boundary | Turns | Requests per turn: median / p90 / max | Growth inside a turn: median / p90 / max |
|---|---:|---|---|
| The `promptId` of the latest user record, split at compactions | 54 | 15 / 77 / 142 | 31,840.5 / 198,284 / 371,579 |
| `stop_hook_summary` or `compact_boundary` records | 102 | 5.5 / 35 / 130 | 7,348.5 / 70,770 / 350,309 |

Which boundary equals a "turn" for `$.session.compact()`: UNSURE.

### 3.9 Prompt-cache profile (the same slice)

| Day | Requests | Σ re-sent | Cache read | Cache creation | Creation per request: median / p90 | Requests with creation > 50k | 1-hour-TTL creation |
|---|---:|---:|---:|---:|---|---:|---:|
| 09-25 (part) | 200 | 68,768,865 | 99.3% | 0.7% | 1,482 / 4,049 | 1 | 477,795 |
| 09-26 | 781 | 394,167,730 | 99.4% | 0.6% | 1,561 / 3,841 | 3 | 2,278,632 |
| 09-28 | 792 | 366,720,968 | 99.4% | 0.6% | 1,574 / 4,682 | 3 | 2,124,668 |

Uncached input is 0.00%, and 5-minute-TTL creation is 0.

### 3.10 The committed probes, re-run unchanged (22:0xZ)

The slice runs from the 09-25 21:58:11Z `compact_boundary` (offset 740,755,248) to the pin, 36,250,432 bytes; it includes 200 requests of 09-25.

- `python3 docs/research/findings/jev-pipes/context_budget.py <slice>`: 0.84 s, rc 0.
  - "re-sent 829,657,563 tokens | segment base 233,750,870 (28.2%) | in-segment growth 595,906,693 (71.8%)"
  - "attributed ... 174,712,792 tokens (29.3% of the growth)"
  - Rows as a share of re-sent: Bash results 8.8%; Bash inputs 5.7%; user-side text 2.5%; Read results 1.1%; Write inputs 0.6%; assistant text 0.6%; gitnexus detect_changes results 0.3%; Agent inputs 0.3%; SendMessage inputs 0.2%; Edit inputs 0.1%; add_repo results 0.1%; "assistant thinking (if kept)" 0.1% (1,042,759); Agent results 0.1%; github job logs 0.1%; actions list 0.1%; the rest 0.2%.
- `python3 docs/research/findings/jev-pipes/inject_cost.py <slice>`: 0.81 s, rc 0.

| Attachment | n | Share of re-sent |
|---|---:|---:|
| `invoked_skills` | 6 | 4.3% |
| `deferred_tools_record` (record size, upper bound) | 341 | 3.3% |
| `instructions` | 7 | 2.6% |
| `nested_memory` | 5 | 1.7% |
| `deferred_tools_delta` | 12 | 1.0% |
| `task_reminder` | 202 | 0.9% |
| `agent_listing_delta` | 6 | 0.7% |
| `mcp_instructions_delta` | 6 | 0.4% |
| `skill_listing` | 22 | 0.2% |

- **Contradiction (both sides recorded).** `context_budget.py` prices thinking at 0.1% because it measures stored thinking text, which is empty in 86% of blocks. The usage fit (§3.4) puts prior thinking at 36.1-40.3% of growth and a median 25.8% of the whole context.
- **Contradiction.** The docs say Claude Code "clears older tool outputs first" (A1.16). The measured transcript has 0 clearing events in 777 MB.

---

## 4. The Hermes lanes, measured from what the repo holds

| Cell | Evidence | Status |
|---|---|---|
| Prompt tokens per request over one verify lane's window (llama-server era) | VERIFY-N5k window, the last 20,000 log lines: 380 tasks; prompt tokens processed 4,373,729 (mean 11,510, max 98,452); 42 tasks > 50K were full re-processings with 64 "forcing full prompt re-processing ... (likely due to SWA or hybrid/recurrent memory)" warnings; 271 tasks < 2K were served from the prompt cache. Prefill 752 t/s; decode 46.6 t/s; prefill = 36% of busy time; `--cache-reuse` "INERT on this hybrid model" (`docs/research/findings/RESEARCH-FINDINGS-1-VERIFIED.md` table rows, 7537910 2026-09-15). These are tokens processed per task, not whole-context sizes. | SOLID (committed) |
| One overflow event | 2026-09-14 15:5xZ: "`request (96944 tokens) exceeds the available context size (65536 tokens)` four times (97k → 104k tokens)" (`docs/INCIDENT-LOG.md:574`) | SOLID |
| The current server | vLLM, `--max-model-len 131072` (QJ2 report); KV 215,112 tokens after D-099 | SOLID |
| Lane-profile context settings | §1B | SOLID |
| Whole-context size per request over a lane's life, compression events per lane, the live values of `compression.*` and `micro_compact`/`proactive_prune` in the lane profiles, OmniRoute's live compression and context-editing settings, vLLM prefix-cache behavior when an earlier message changes | none in the repo | NOT measured here: PC only |

---

## 5. Prior art, with sources

arXiv metadata came from `export.arxiv.org` (all 12 ids resolved). Claims come from the abstracts unless marked.

| Source | What it does | What it reports on losing a needed line, or on quality vs cost | Status |
|---|---|---|---|
| Zhang, Kraska, Khattab, *Recursive Language Models*, arXiv 2512.24601 (2025-12-31) | The prompt lives in an external environment; the model examines it and calls itself on snippets | "process inputs up to two orders of magnitude beyond model context windows"; on GPT-5, median +26% vs compaction and +13% vs Claude Code across four tasks at comparable cost. HTML v3: "median RLM run is cheaper ... but more expensive on average due to outlier trajectories where the RLM struggles to find an answer"; Qwen3-Coder syntax errors "propagate" to sub-calls. | SOLID (abstract); UNSURE (body excerpts) |
| Anthropic, *Managing context on the Claude Developer Platform* (2025-09-29) | Context editing plus the memory tool | Memory + context editing +39% over baseline; context editing alone +29%; a 100-turn web search: "complete workflows that would otherwise fail ... reducing token consumption by 84%" | SOLID (page text) |
| Claude API docs: context editing, compaction, preserved thinking (fetched 2026-09-28) | §1D | Server-side edits keep thinking valid; client-side edits of earlier turns invalidate later thinking (D6, D7) | SOLID |
| Lindenbauer et al., *The Complexity Trap*, arXiv 2508.21433 (2025-08-29) | Observation masking vs LLM summarization in SWE-agent | Masking "halves cost ... while matching, and sometimes slightly exceeding, the solve rate of LLM summarization"; summaries cause "trajectory elongation"; masking window M=10 (HTML) | SOLID (abstract); UNSURE (HTML details) |
| Kang et al., *ACON*, arXiv 2510.00615 (2025-10-01) | Compression guidelines refined from failure analysis | Peak tokens −26% to −54% "while improving task success"; "ensuring critical state information is preserved" | SOLID (abstract) |
| Ye et al., *AgentFold*, arXiv 2510.24699 (2025-10-28) | Learned folding at several scales | Fixed full-history summarization "risk[s] the irreversible loss of critical details"; BrowseComp 36.2% | SOLID (abstract) |
| Sun et al., *Context-Folding*, arXiv 2510.11967 (2025-10-13) | Branch and fold sub-trajectories (RL) | Matches or beats ReAct "using an active context 10× smaller"; beats summarization-based management | SOLID (abstract) |
| Wu et al., *ReSum*, arXiv 2509.13313 (2025-09-16) | Periodic summaries | +4.5% over ReAct training-free, +8.2% with ReSum-GRPO | SOLID (abstract) |
| Zhou et al., *MEM1*, arXiv 2506.15841 (2025-06-18) | Constant internal state per turn (RL) | 3.5x performance and 3.7x less memory vs Qwen2.5-14B on 16-objective QA | SOLID (abstract) |
| Pan et al., *LLMLingua-2*, arXiv 2403.12968 (2024-03-19) | Token classification; "compress prompts without losing crucial information" | 2x-5x compression, 1.6x-2.9x lower latency | SOLID (abstract) |
| Jiang et al., *LongLLMLingua*, arXiv 2310.06839 (2023-10-10) | Question-aware compression | +21.4% on NaturalQuestions with about 4x fewer tokens | SOLID (abstract) |
| Chirkova et al., *Provence*, arXiv 2501.16214 (2025-01-27) | RAG context pruning as sequence labeling | "negligible to no drop in performance" | SOLID (abstract) |
| Liu et al., *Lost in the Middle*, arXiv 2307.03172 (2023-07-06) | Position effects | Performance "significantly degrades when models must access relevant information in the middle" | SOLID (abstract) |
| Hong, Troynikov, Huber, *Context Rot*, Chroma (2025-07-14) | 18 LLMs vs input length | "performance grows increasingly unreliable as input length grows" | SOLID (page text) |
| Packer et al., *MemGPT*, arXiv 2310.08560 (2023-10-12) | OS-style memory tiers | Qualitative; no loss rate in the abstract | SOLID (abstract) |
| Hermes, `evals/compaction/results/SCORECARD-2026-08-15.md` (at 527da60) | 15-question recall exams on 4 real 500K transcripts; LLM-generated questions and LLM judge | Uncompacted 96.7%; batch "current" 45.8% at about 162K; lean 40.0% at about 49K; lean plus one `session_search` round-trip 68.3% at about 49K; real Codex CLI compaction 36.7% | UNSURE (upstream, LLM-judged) |
| Hermes `docs/micro-compaction.md` (at 527da60) | Per-turn rolling fold | One session, 400K window: occupancy flattened at about 22% of the threshold; passes 2-37 s (median about 31 s) on a local 7B; the first pass costs about +300 tokens of scaffolding (342-380) | UNSURE (upstream) |

---

## 6. What the repo already knows about losing context

| Item | Evidence (file:line, date) | Status |
|---|---|---|
| AF-AP-17: each compaction prunes the governing role or skill text, and the lane continues under weaker rules | `docs/INCIDENT-LOG.md:612` (file 98c7f97, 2026-09-28 21:06Z) | SOLID |
| AF-AP-19: compaction prunes loaded skills, the reload refills the context; "the task's own contract is what gets summarized away" | `docs/INCIDENT-LOG.md:614` | SOLID |
| AF-AP-154: after a refusal the harness drops thinking blocks (`thinking_drop`, `model_mismatch`) and changes the model mid-run | `:749` | SOLID |
| AF-AP-180: after a compaction a Hermes lane's final reply echoed the injected context and was saved as its report | `:775` | SOLID |
| AF-AP-182: a context hook fired on harness events. The measure behind it: `task_reminder` records were 44.4% of transcript bytes; `wiki-context.py` injected 11,484 bytes per harness event (incident `:147`, 2026-09-24 12:0xZ) | `:777` | SOLID |
| AF-AP-183: hook text over 10,000 chars becomes a 2 KB preview of its head and hides the payload | `:778` | SOLID |
| AF-AP-218: rules to load a skill, with nothing that loads it (12 Skill calls in the main transcripts) | `:813` | SOLID |
| A hand-back summary that hid the full report | "the lane's 63,540-character final text; its hand-back held only a summary, which the `harvest` stack alone would have saved" (`todo/BUILD-TASKLIST.md:1700`, 2026-09-28 18:1xZ) | SOLID |
| The harness refused a subagent's report-file write | `docs/INCIDENT-LOG.md:34` (2026-09-26 08:5xZ) | SOLID |
| Stale compaction summaries | 2026-08-04: resumed "from a compaction summary frozen at Jul 31", redid pushed work and invented a false timeline (`.claude/skills/session-continuity/SKILL.md:10-20`, 6bb590b 2026-09-28). "the summary is a lossy cache" (40-48). 2026-08-28: "a summary claimed a 4-commit stack was local-only; it had been pushed" (60-66). | SOLID |
| Lane overflow when the model slot was smaller than the context Hermes was told | `docs/INCIDENT-LOG.md:574` (2026-09-14) | SOLID |
| Rulings | D-053 `:64` (pruner PARKED for Hermes lanes; the lane's own compression is "NOT measured" as cover); D-079 `:90`; D-082 `:93` (System 1 direct, System 2 through OmniRoute); D-087 `:98` (our Claude Code workflow is the test bed; Jevs in pipelines); D-093 `:104` (Laya should manage skills so they don't all feed the context); D-097 `:108` (131k); D-099 `:110`; D-102 `:113`; D-103 `:114`; D-105 `:116` (all in `docs/08_DECISION_LOG.md`, 54877b9 2026-09-28) | SOLID |
| KC-J1: no Laya or System-1 value reachable from a gate, merge, lint, commit, push or proof predicate; an absorbing barrier | `docs/research/COUNCIL-VERDICT-JEV-LAYA-v1.md:45` (ec50851, 2026-09-22); screen `scripts/no_laya_in_gates.py` (0cade80, 2026-09-24), exit 3 = violation, 4 = completeness | SOLID |
| KC-J1b: a Laya score never the sole evidence for an AP registry row or a verifier per-finding class | `COUNCIL-VERDICT-JEV-LAYA-v1.md:46` | SOLID |
| KC-J5: needle loss. "If one incident occurs in which a dropped or hidden item changed a decision ... drop mode is off permanently and everywhere" | `:50`; restated in J2 §3 ("no Laya score may decide what is dropped (KC-J5)", `J2-SIGNAL-PROBE-2026-09-24.md:59-60`) | SOLID |
| KC-J6: provenance and recoverability: "the original bytes recoverable adjacent" to any shown score | `:51` | SOLID |
| No LLM judge in the gate spine | `CLAUDE.md:193` (tactic 5); standing rule 12 (`CLAUDE.md:228`) | SOLID |

---

## 7. Open cells (unknown or not measured)

1. Claude Code: the `keepRecent` default and the exact trigger of the binary's microcompact.
2. Claude Code: whether `clear_thinking` keep `all` is sent on every main request.
3. Claude Code: the 2.1.283 behavior of the function hooks (the declarations are from 2.1.274).
4. Claude Code: which record boundary equals a "turn" for `$.session.compact()`.
5. Claude Code: whether a CCR session honors a changed `ANTHROPIC_BASE_URL`.
6. The source of `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80`.
7. Whether this account was created on or after 2026-08-31, which decides whether the API enforces the thinking prefix check by default.
8. The branch topology between the Hermes pins 527da60 and b3399c1.
9. b3399c1's tool-output caps and native-compaction module (not read).
10. All live PC values: lane profiles, OmniRoute compression, context editing and headers, vLLM prefix caching under edits, per-lane context size and compression events. NOT measured here: PC only.
11. The live LS-B9 stack contents (the lane is running).
12. A fixed-start split of the system prompt vs the tool schemas in tokens: chars are measured (28,161 and 169,442-176,687), tokens only as a sum.
13. A real-tokenizer check of the 2.90 chars-per-token fit.
