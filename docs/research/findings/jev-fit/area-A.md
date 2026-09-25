> Auditor A's design report, verbatim from its hand-back (2026-09-25; read-only audit at origin 934bc8a). The plan that
> synthesizes the three areas is `PLAN-2026-09-25.md` in this directory.

**JEV-FIT area A: the coordinator session. Auditor A, 2026-09-25 04:2xZ, origin 934bc8a. Read-only. No files written.**

**The short answer.** The project's hooks inject only about 1% of the coordinator's context, so a Jev that picks what a hook injects can save at most about 1%. The real cost is the number of requests: every request re-sends the whole context. The main session made 17,241 requests with a median context of 460,526 tokens, and 7.75 billion of its context tokens were cache reads. The waste sits in a few classes of requests. Three of my top five fixes are plain rules. The best fit for the RWKV reader is ranking what the coordinator needs after a compaction. The best fit for Laya is suggesting where the retro gate's lesson should be baked.

**How I measured.** I read the five hooks, both settings files, `scripts/hook_context.py`, `scripts/install_session_hooks.py`, the harness Stop hook, and the harness type file (`/root/.claude/plugins/cache/fast-jev-output/fast-jev-output/0.1.0/types/claude-code.d.ts`, the plugin's copy of it). I counted the main transcript `/root/.claude/projects/-home-user/bdab799a-….jsonl` with streaming inline Python. It grew from 708 to 710 MB while I read it, so counts move by a few units between probes. I quote no transcript text. I read how task reminders are rendered from `/opt/claude-code/bin/claude`.

### 1. Where the context goes, and which requests are wasted

**Table 1. Context by source, since the task-list cleanup (2026-09-24T12Z to 09-25T04Z: 2,018 requests, 995M context tokens).** For each request I counted the characters each source added since the last compaction, at 4.06 characters per token. That rate is a least-squares fit over 17,084 pairs of consecutive requests.

| Source | Share |
|---|---|
| Coordinator's own tool inputs | 6.8% |
| Bash results of 8k characters or less | 6.4% |
| CLAUDE.md reloaded after each compaction (85k characters, 9 loads) | 4.5% |
| Other harness attachments | 3.4% |
| Skills re-attached after each compaction (bug-echo, orchestration, council, rwkv) | 3.3% |
| Task reminders, as rendered | 2.4% |
| Tool results over 8k characters | 1.8% |
| All hooks, project and plugin | 1.0% |
| Rest: thinking, message wrappers, system prompt, tool schemas | about 67% (the split between them is not known) |

**A correction to JEV-LEVERAGE §2.** Task-reminder records are 43% of the transcript's bytes (1,982 records, 303.7 MB). But the harness renders only `#id. [status] subject` plus a fixed nudge. That is at binary line 1,341,690, and the reminder fires when both `TURNS_SINCE_WRITE:10` and `TURNS_BETWEEN_REMINDERS:10` are met. The descriptions never reach the model; in one sampled reminder they were a median 742 characters per task. The cleanup on 09-24 cut the rendered reminder from a median 34,349 characters to 2,635. Over the whole session reminders were 12.4% of context; since the cleanup they are 2.4%. There is nothing left to gain there.

**Table 2. Wasted requests in the main session, 2026-09-02 to 09-25.**

| Class | Count | Requests | Context tokens re-sent |
|---|---|---|---|
| Re-orienting after a compaction (the calls before the first Edit, Write, Agent, commit, push or lane launch) | 126 compactions, 2,095 calls; median 12 per compaction, p90 28 | 1,405 | 246M |
| Extra turns after a Stop-hook block | 276 blocks in 993 turn ends | 1,110 | 602M |
| · git check only | 219 | 587 | 317M |
| · retro gate involved | 57 | 523 | 285M |
| Requests that only touch the task list | – | 551 (44 since 09-24T12Z) | 271M |
| Requests that only load deferred tools (ToolSearch) | 274 calls, 123 of them load one tool | 212 | 82M |
| Failed tool calls | 307 of 19,221 (Bash 270) | – | – |
| Retries after a failure, within 3 calls | Bash 46, Edit 9 | – | – |
| Bash timeouts | 54 (27 are `scripts/pc.sh`) | – | at least 1.9 h of wall time |
| Re-reads with nothing written since / identical re-runs with identical output | 9 / 7 | – | negligible |

What the re-orientation calls were: Bash file reads 1,013, git state 366, lane and PC state 289, Read 163, task list 81, ToolSearch 50. Of the 3,462 paths those reads touched, 2,235 (65%) had been touched in the interval before the compaction. 1,923 (56%) are named in the compaction summary.

### 2. Integration points

**Table 3a. Where each point plugs in and what it does.**

| ID | Seam | Trigger | Input | Question | Action |
|---|---|---|---|---|---|
| A1 Resume pack | `.claude/hooks/session-start.sh:36-47`, which cuts `orient.sh` to 3,000 characters at `:45`; `scripts/orient.sh:27`; registered for every session source at `scripts/install_session_hooks.py:47-48` | SessionStart when `source` is compact or resume (`claude-code.d.ts:7646-7648`) | the transcript tail from the payload's `transcript_path`; git; `.lanes-live`; `.lanes/*/lane.pid`; the head of the ledger's LIVE section | none (a rule) | Print at most 9,000 characters (AF-AP-183): HEAD against origin, uncommitted files split by `.lanes-live`, live lanes, the last status of each running background task, one `ToolSearch select:` line naming the deferred tools used before the compaction. Commits come before chat. |
| A2 Stop attribution | a new Stop hook beside `turn-retro-gate.sh`, registered like `install_session_hooks.py:56-57`; it repeats the checks in `/root/.claude/stop-hook-git-check.sh:7-10,27,33,116` | Stop, and only when that harness check will block | `git status --porcelain`, `.lanes-live`, and the Stop payload's `background_tasks` and `last_assistant_message` (`claude-code.d.ts:7912-7922`) | none (a rule) | One line: uncommitted files split into declared lane files, files this turn wrote, and others; running tasks; unpushed count. |
| A3 Resume ranker | as A1, plus the `scripts/jev.py:372-383` venues | SessionStart after a compaction | the RWKV state of the stream up to the compaction; candidates are the paths touched in the interval plus the paths named in the summary (PostCompact's `compact_summary`, `claude-code.d.ts:5472-5478`) | a score for each candidate: "will the coordinator read this in its first 20 calls?" | A1's pack adds the top 5 paths, each read fresh by the hook. The Jev only points. |
| A4 Retro hint | `.claude/hooks/turn-retro-gate.sh:66-74`, after the block decision is fixed at `:58` | the retro gate blocks | one block of at most 1,000 characters: the batch's commit subjects and `git diff --stat`, against the lexical top 16 candidates (skill headings, registry rows, wiki pages) | a ranking: "should this batch's lesson be baked here?" | Add three targets marked "suggested, unverified". |
| A5 Doomed-call advisory | `.claude/hooks/search-intercept.py:1161-1198` (`decide`); the block-once escape hatch at `:1111-1150`; the 5% false-positive bar at `:597-601` | PreToolUse on Bash | the command plus `.jev/advice.json`, the stream answers computed per batch (no PC call on this path) | a choice: exit 0, non-zero, or harness block or timeout | Block once with the reason when a timeout is predicted with confidence; an identical repeat passes. Otherwise do nothing. |

**Table 3b. Payoff, labels, model and size.**

| ID | Payoff (counts from this audit, main session) | Labels, and the rule to beat on held-out data | Model | Build |
|---|---|---|---|---|
| A1 | The rule-answerable re-orientation calls: git 366 + lane 289 + task list 81 + ToolSearch 50 = 786 calls. That is about 527 requests and 92M tokens (these requests average 1.49 calls and 175k tokens each). | Replay: count, per compaction, the calls the pack would have answered. Live: calls before the first productive call (median 12-14 today). | A rule is enough. | Small; needs nothing new. |
| A2 | At most 368 requests and 199M tokens: the git-only extra-turn requests beyond one reply. This is an upper bound, because the records do not say who made the uncommitted changes (JEV-MAP §5 item 9). | Live, before and after: requests per git-only block (2.7 today). | A rule. A Jev adds nothing to a fact that `git status` already gives. | Small. |
| A3 | Ceiling: the 1,203 file-read calls, about 807 requests and 141M tokens. The realistic share is not measured. | The paths read in the first 20 calls after each compaction (2,025 pairs, JEV-MAP D17). Hold out the last 30 of the 126 compactions. Beat "named in the summary" and "the last 10 paths touched" at recall@5 and precision@5. | The RWKV stream reader. One interval is about 158k Laya tokens (JEV-MAP §3.5); Laya's window is 1,024. | Large: a transcript tailer, a PC stream server, a trained student, and room on the GPU beside vLLM. |
| A4 | Ceiling: 132 reads of skills, registry, wiki and CLAUDE.md during retro extra turns, about 89 requests and 48M tokens. Not measured beyond that. | The targets of the 54 bake edits, plus teacher labels only where no answer is recorded (D-083). Beat wiki-context's lexical scorer (`wiki-context.py:114-120`). | Laya per block. | Medium; the labels are the work, and the Laya server already exists (`scripts/jev_local.sh`). |
| A5 | Small: 307 failed calls out of 19,221. In the bridge slice, 30 of 2,177 foreground `pc.sh` calls timed out under `curl -m 120` (`scripts/pc.sh:14-20`), at most about 1 h of wall time. | `is_error`, `Exit code N`, `timedOutAfterMs` (34,486 Bash outcomes, JEV-MAP D01). A verb rule (loop, wait, long sleep, build, pytest, analyze) flags 946 calls and catches only 13 of the 30 timeouts, so a rule fails here. It ships only if false positives stay at or under 5%. | RWKV: the stream shows when a lane just launched or the PC is busy. | Medium to large; it runs on A3's infrastructure. |

**Why these designs:**
- **A1 also fixes a live bug.** `orient.sh:27` reads `/root/.claude/projects/-home-user-agent-factory/*.jsonl`. That is a 1.6 MB file from a second session, last written 2026-09-22. Since the hooks went live, all 8 session-start outputs spend 2,643 characters on that file's 2026-09-22 chat. All 8 are cut before the commits section. Re-orientation did not shrink once the hook began to fire: a median of 14 calls per compaction before, 13.5 after (n = 8).
- **The extra turn after a git-only block rarely does anything.** 120 of the 219 are text only. Of the 99 with tool calls, 81 open with a git-state call, and only 20 of the 219 commit. So most of the uncommitted work is not the coordinator's to commit.
- **A2 must never add a turn.** It speaks only when the harness check will block anyway. It runs the same three checks and honours `stop_hook_active`. It uses Stop `additionalContext` (`claude-code.d.ts:1042`), which the running 2.1.280 binary may not honour; if not, it exits 2.
- **A4 and A5 follow the search-intercept precedent** (`search-intercept.py:977-1002`). A Jev can change what a message says, never whether it blocks. A5 stops a waste but does not act as a gate: a wrong block costs one repeated call.

### 3. Top five, ranked by payoff against build size

1. **A1, the resume pack (rule).** About 527 requests and 92M tokens; small; fixes a live bug.
2. **A2, the Stop attribution line (rule).** At most 368 requests and 199M tokens; small.
3. **A3, the RWKV resume ranker.** Ceiling 807 requests and 141M tokens; large. It is the best RWKV fit here and has the most labels for free.
4. **A4, the Laya retro hint.** Ceiling 89 requests; medium.
5. **A5, the RWKV doomed-call advisory.** Small payoff; medium to large. Worth building only as the student's first question, on the infrastructure A3 needs anyway.

**Where a plain rule beats a Jev:**
- **wiki-context.** It injected 126,325 characters over 35 prompts. 11 of the 35 live-state blocks repeat one already injected in the same interval (`wiki-context.py:93-96`), so skip repeats. Drop the shadow reranker JEV-LEVERAGE planned: it could save less than 0.4% of context.
- **CLAUDE.md size.** It is 4.5% of context; trimming it to its index saves more than any Jev in this area.
- **Task-list bookkeeping.** Put Task* calls in the same response as real work (551 requests that did nothing else).
- **Omitted `model` on dispatch.** This was 82 of 275 overall but only 1 of 62 on 09-24 and 09-25, so the habit is already fixed.
- **D23, waves of agent failures.** This cannot be acted on at dispatch. None of the 19 failed agents was dispatched after a sibling failed. The waves (15 on 09-08, 4 on 09-23) kill agents that are already running.
- **Output pruning.** Results over 8k characters are only 1.8% of context. The seam exists (`updatedToolOutput`, `claude-code.d.ts:1039`), but the gain is small.

**What JEV-MAP missed:** the orient bug; the 1,110 extra-turn requests after Stop blocks; that reminders render subjects only; that D23 is a signal at notification time, not a lever at dispatch; the lone ToolSearch requests (212) and task-list requests (551); and the Stop, PostCompact and PostToolUse hook fields cited above.

### 4. Shared infrastructure

1. **A hook shim with a decision log.** `scripts/hook_context.py:20-42` already wraps the tool hooks. Add Stop to `EVENTS` at `:20`, and wrap all five hooks in `install_session_hooks.py:46-58`. Then write one row per hook run to `.jev/hooks.jsonl` (mode 0600): time, session, event, tool, exit code, output length, duration, `transcript_path` and byte offset. The offset turns each hook decision into a pointer into the stream, which makes it a label (D-086). All five points need it.
2. **A transcript tailer** (new `scripts/jev_tail.py`). SessionStart starts it the way `scripts/jev_local.sh` starts the Laya server: a pidfile, safe to run twice. It turns the transcript into SESSION-EXPORT D-1 events and runs `transcript_export.scrub` and the D-2 path denylist before any byte leaves. It sends 2 to 7 batched bridge calls per active hour (JEV-MAP §3.4), keeps a bounded spool, and fails open.
3. **A stream-state server on the PC** (new). It runs the RWKV student, keeps one state per session, and answers append and ask requests on the `/v1/systemone` contract of `scripts/laya_systemone_server.py`, so `jev.py` stays the only client. It connects directly to its own model (D-082). Whether it fits on the GPU beside vLLM is not measured: the 3090 numbers ran with vLLM stopped (1.26 GB peak for a 2,048-token forward, 10.5 GB at 61,440 tokens). So append in chunks of 2k tokens or less, or run it inside a GPU window.
4. **An advice cache**, `.jev/advice.json`: the answers from each batch, with the stream offset they were computed at. Hooks read it in microseconds. If it is stale or missing, nothing changes.
5. **The existing sandbox Laya server**, for A4.

### 5. How this carries over to the agent factory

The factory runs Hermes on the PC, and the seams map one to one:
- The resume pack and ranker become Hermes context compression plus a `pre_llm_call` injection (30 s, `harness-ports/hermes/config-snippet.yaml:137-139`).
- The retro hint becomes lesson routing in the dream phase (`docs/11_DREAM_PHASE.md:99`, D-058).
- The doomed-call advisory becomes a `post_tool_call` observer (`:154-157`) whose output is spooled into the next `pre_llm_call`, one turn late. It never goes into `pre_tool_call`, the fail-closed policy seam (standing rule 9, KC-J1).
- The decision log becomes the factory's event stream, where every decision carries its reason.

There the RWKV server sits beside the GPU, so no bridge is needed. The questions are the same (what to reload after compression, where a lesson belongs, which call is doomed), so a student trained on our stream should serve the factory. That needs an adapter from Hermes' `state.db` to the D-1 schema, which nobody has read yet (JEV-MAP §5 item 1).

**Not measured:**
- How the remaining two thirds of context splits between thinking and the system prompt.
- Whether the 2.1.280 binary honours Stop `additionalContext`.
- RWKV on the GPU beside vLLM, and RWKV speed on CPU.
- Who made the uncommitted changes behind each Stop block.
- How precisely any ranker performs: no Jev was trained or scored in this audit.

### Critical files for implementation
- /home/user/agent-factory/.claude/hooks/session-start.sh
- /home/user/agent-factory/scripts/orient.sh
- /home/user/agent-factory/.claude/hooks/turn-retro-gate.sh
- /home/user/agent-factory/scripts/hook_context.py
- /home/user/agent-factory/scripts/install_session_hooks.py