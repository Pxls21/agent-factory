# SESSION-DECISIONS 2026-09-25: the typed decisions our own session records hold, with recorded answers

Task #251's next source (owner 2026-09-25). Brief: `tasks/briefs/jev-laya/DATA-SESSION-brief.md`. Role: evidence-gatherer
(EXPLORE lane, sandbox, Opus 5.5). This report catalogues and counts. It holds no verdict and no recommendation.

STATUS: COMPLETE for this lane, with the NOT-done list in section 6. Written incrementally 2026-09-25T01:36Z-02:1xZ
(`date -u`). The only repo file this lane wrote is this report.

Headline numbers (details and methods below):
- 26 recurring decision types catalogued (R1-R26); 18 carry a D1 (structured field) or D2 (fixed tool line) answer.
- Top five by answered volume: R1 Bash exit status 34,272 (D1); R6 Edit/Write applies 4,173 (D1); R17 test run
  outcome 2,778 answered of 3,324 (D2); R16 commit gate outcome 971 answered of 1,321 (D2); R7 Stop gate 965 (D1).
- Export budget for the top five, scrubbed, full states: 55,776,945 bytes over 44,055 records (answered records only:
  53,983,370 over 43,159); states cut at 2,000 characters: at most 39,730,589 bytes.
- Label caveats measured: 15,946 of 34,272 Bash calls end in a pipe with no `pipefail` (the code is the last pipe
  command's); 883 of 934 red test runs exit 0; the Stop gate's proxy state leaves 600 of 965 rows in states with
  conflicting answers.

Builds on `docs/research/findings/laya-ft-data/INTERNAL-LABELS-2026-09-25.md` sections 3.1 and 3.4 (called IL below):
its counts d3-d7 (owner text 206 + 17, gate-word blocks 186, 255 dispatches, verifier class ids 666) are reused, not
redone, unless a row says so.

Scratch directory for every artifact named below:
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/data-session/` (called `$S` below).
Local HEAD at start: `1e04e52acda43e89adc3b35f69a0cb56a1a51c9a` (2026-09-25T01:35:43Z), branch
`claude/soundbox-kit-migration-iz1jwf`.

## 0. Enumeration (the cells this report must fill)

| # | Cell | Section | State |
|---|---|---|---|
| E1 | record shapes of the sources (record types, block types, attachment kinds, the fields a state or answer can come from) | 1 | filled |
| E2 | tool calls: command + exit code; error family (hiccup_families.tsv) | 2 | filled |
| E3 | gates and hooks: push_clean, CI gate, commit gates, search intercept, edit-snapshot AP screen, stop gate | 2 | filled |
| E4 | verify lanes: gate recommendations, finding classes, repairs | 2 | filled |
| E5 | dispatches: terminal outcome, served-model mix, routing | 2 | filled |
| E6 | owner turns: question and ruling | 2 | filled |
| E7 | retro answers at the stop gate | 2 | filled |
| E8 | bug-echo runs and AF-AP registration | 2 | filled |
| E9 | other recurring typed decisions found in the records | 2 | filled |
| E10 | the catalogue table (evidence demand 1) | 2 | filled |
| E11 | top 5: 3 scrubbed examples each + the label-leak check (evidence demand 2) | 3 | filled |
| E12 | export budget (evidence demand 3) | 4 | filled |
| E13 | factory mapping, one line per row (evidence demand 4) | 5 | filled |
| E14 | NOT-done (evidence demand 5) | 6 | filled |

## 1. Sources and record shapes (E1)

Every count below comes from producers under `$S`, run with `PYTHONDONTWRITEBYTECODE=1` (they import
`scripts/transcript_export.py` and `scripts/hiccup_scan.py` read-only). Each streams every JSONL line by line; none
loads a file whole. No producer writes state text to disk: the instance rows (`$S/inst/<family>.jsonl`) hold lengths, a
normalized-state hash, the answer, the provenance and the scrubbed export size only.

| Source | Size at read | Records / files | Dates | Read by | SOLID/UNSURE |
|---|---|---|---|---|---|
| main session `-home-user/bdab799a-...jsonl` (the live coordinator session) | 704,025,999 bytes (runs 5 and 6, 01:55Z-01:56Z) | 127,944 lines at the first survey; 17,070 distinct `requestId`s | records on 2026-09-02..08, 09-14..19, 09-21..25; none on 09-09..13 and 09-20 (`$S/days_tasks.json`) | all producers | SOLID |
| `-home-user-agent-factory/bdab799a-...jsonl` | 1,583,665 bytes | 280 lines; 19 request ids | 2026-09-02T22:12Z..09-22T16:48Z | all producers | SOLID |
| subagent transcripts `subagents/agent-*.jsonl` | 392,385,356 bytes (first survey) | 257 files (256 read: this lane's own `agent-a306d5b05bcac22ac` is excluded from every count) | 2026-09-02T21:43Z..09-25T01:59Z | all producers | SOLID |
| workflow files `subagents/workflows/wf_*/*.jsonl` | 34,515,856 bytes | 4 workflows: 34 agent transcripts + 4 `journal.jsonl` (`started` 34, `result` 30 records: 18 build reports and 12 verify verdicts, the same field sets as the 30 `structured_output` attachments) | 2026-09-05T12:13Z..09-06T01:14Z | all producers | SOLID |
| task output files `tasks/*.output` | 69,255,887 bytes | 524 regular files (background command outputs) + 126 symlinks to subagent transcripts | mtimes 2026-09-14..09-25 | `days_tasks.py` (counts only) | SOLID |
| committed digests `transcripts/sandbox/chat-*.md`, `transcripts/pc/*.md` | 18 and 119 files | pc digests: 29,211 `## tool result (<tool>)` headings, bodies not exported ("body not exported") | - | IL d1/d2; a heading count here | SOLID |

Record types across all 297 files of the first survey (01:38Z, which still included this lane's own first records; `$S/shapes.py`, `$S/shapes.json`): assistant 92,770; user 46,556; attachment
57,180; system 1,108; plus harness bookkeeping types (`atis-latch`, `mode`, `custom-title`, `last-prompt`,
`queue-operation`, `cost-state`, `ai-title`, workflow `started`/`result`). 22 lines do not parse (8 main, 10 subagent,
4 workflow). Tool calls: 44,734 `tool_use` blocks; 44,722 `tool_result` blocks.

The fields a recorded answer can come from (value sets from `$S/enums.py`, `$S/enums.json`; names and enumerated values
only):

| Answer field | Where | Values seen | Used by rows |
|---|---|---|---|
| `tool_result.is_error` + first line `Exit code N` | user record, tool_result block | Bash: 34,041 not error, 785 error; 669 carry `Exit code N` (N in 1..144) | R1, R3, R6, R14-R17 |
| `toolUseResult.timedOutAfterMs` | user record | 33 (120000 x21, 600000 x5, ...) | R1 |
| `toolUseResult.returnCodeInterpretation` | user record | `No matches found` 87, `Files differ` 2, 1 other | (not used; 89 rows) |
| `user.toolDenialKind` | user record | `automode-blocked` 29, `permission-rule` 14, `user-rejected` 8 | R4 |
| `system` `subtype=stop_hook_summary`: `hookErrors`, `hookInfos`, `preventedContinuation` | system record | 963 records; `hookErrors` non-empty in 260; `preventedContinuation` False in all 963; hooks `stop-hook-git-check.sh` 960, `turn-retro-gate.sh` 107 | R7, R8 |
| `system` `subtype=model_refusal_no_fallback` (`apiRefusalCategory`); `api_error` | system record | 5 (`cyber`); 11 | R20 |
| `assistant.message.stop_reason` | assistant record | `refusal` 27, `tool_use` 53,263, `end_turn` 1,796 | R20 |
| `assistant.message.model`; `toolUseResult.resolvedModel` | assistant record; Agent result | 8 model ids plus `<synthetic>`; `resolvedModel` on 256 Agent results | R11 |
| `<task-notification>` XML (`<status>`, `<summary>` with `exit code N`, `<event>`) | user text and `queued_command` attachments (the same notification can appear in both; deduplicated by task id + status, events by task id + body) | three kinds: Monitor `<event>` (603 records), background command (485), agent completion (236 + 20 + 4); workflow completion 3 | R9, R10, R24 |
| `toolUseResult.statusChange` | TaskUpdate result | 631 (`pending->in_progress` 201, `completed->deleted` 200, `in_progress->completed` 179, ...) | R25 |
| `hook_success.stdout` (JSON `hookSpecificOutput.additionalContext`) | attachment | edit snapshot `registry screen` on 350 Edit/Write calls (346 without this lane) | R18 |
| `structured_output.data` | workflow attachment | 12 verify verdicts (`verdict=NOT-READY` x12), 18 build reports (`pytest_summary_run1/2`, `not_done`, ...) | R21 |
| `mcp__github__actions_list` result JSON (`conclusion`, `head_sha`) | tool_result text | 233 distinct run ids | R19 |

`scripts/decide-harvest` reads a `transcript_jsonl` source only at `transcripts/<file>.jsonl` (3 path parts,
`scripts/decide-harvest:127-128`) and extracts only `hive-scout` / `hive-reviewer` dispatch results
(`:691`, `:725-765`; last change 0d62801 2026-09-24T03:07:58Z). `transcripts/` holds `.md` digests only, and the
sessions hold 0 hive dispatches (IL d5; F11 below: 20 dispatch kinds, none hive). SOLID. These line numbers are
checked against the committed file at `1e04e52` (`git show`). At 02:10Z the working tree showed `scripts/decide-harvest`
and `scripts/laya_ft/common.py` modified: that is the concurrent DSV2 build lane, not this lane (`git status`).

## 2. The catalogue (E2-E10; evidence demand 1)

Label determinism classes used in the tables:
- **D1 structured**: the harness or the tool writes the answer in a typed field (`is_error` + `Exit code N`,
  `toolDenialKind`, `hookErrors`, `<status>`, `resolvedModel`, `stop_reason`, the Actions API `conclusion`).
- **D2 fixed line**: the answer is a fixed-format line the tool itself prints (pytest's summary, `COMMIT BLOCKED ...`,
  `REFUSED ...`, `WAIT by ci-gate`, `== pushing`), read by a regex.
- **D3 committed rule**: a committed regex map over free text (`scripts/hiccup_families.tsv`; the edit-snapshot AP
  screen). The label is the rule's output.
- **D4 actor's choice**: the coordinator's own recorded choice (routing, a task status, the retro answer). Recorded,
  but nothing checks it.
- **D5 human text**: the owner's words. The typed class needs a reader.

Counts are from run 6 of `$S/decisions.py` (`$S/decisions_summary.run6.json`, rows in `$S/inst/`), identical to run 5
(section 2.3), unless the row names another producer. "IL" rows are reused from INTERNAL-LABELS, not recounted.

### 2.1 Decisions, options, answers, counts

| # | Decision as a System 1 question | Type: options | Recorded answer (source; class) | Count (answer split) | Producer | SOLID/UNSURE |
|---|---|---|---|---|---|---|
| R1 | Will this foreground Bash call exit 0? (or: which exit class?) | yes/no; or choice: 0 / 1 / 2 / signal (124, 137, 143, 144) / 127-129 / harness (auto-mode denial, sleep block, hook block, input validation, user declined, isolation lost) / timeout | `tool_result.is_error` + first line `Exit code N`; `toolUseResult.timedOutAfterMs`; D1 | 34,272 calls (main 14,134; sub 18,188; wf 1,950): exit 0 33,454; non-zero 669 (1: 450, 2: 90, 144: 51, 143: 26, 128: 21, 127: 10, 137: 9, other 12); harness or timeout 149 (sleep 56, timeout 33, denial 29, input validation 12, isolation lost 9, hook block 5, declined 5) | `decisions.py` F01 | SOLID |
| R2 | Will the harness block this `sleep N`-first foreground command? | yes/no | error text `Blocked: sleep N followed by: ...`; D1 | 108 sleep-first commands: blocked 55, ran 53 (1 more sleep block was not sleep-first: 56 in R3) | F04 | SOLID (counts); the harness rule itself is not in the repo |
| R3 | Which error family does this failed tool call belong to? | choice: 15 families of `scripts/hiccup_families.tsv` + UNCOVERED | family of the normalized first line (+ next line for `Exit code N`), `hiccup_scan.cluster_key` (`scripts/hiccup_scan.py:100-107`) and `family_of` (`:138-142`), d03e7c4 2026-09-24T16:13:41Z; map 764e516 2026-09-24T13:36:36Z; D3 | 900 failed calls, all tools: `exit code N` (the catch-all last row) 517; sleep 56; edit anchor 54; python exception 45; missing path 41; UNCOVERED 39; pytest run red 34; auto-mode denial 29; Terminated 26; input validation 19; worktree isolation lost 13; edit anchor not unique 9; user declined 8; cwd not repo 6; ripgrep timeout 4 | F02 | SOLID (counts; the label is the map's) |
| R4 | Will this tool call be denied, and by what? | choice: allowed / automode-blocked / permission-rule / user-rejected | `user.toolDenialKind`; D1 | 51 denials (29 / 14 / 8) among 44,722 tool results | F03; `enums.py` | SOLID |
| R5 | Will the search intercept stop this search? | yes/no | hook exit 2, seen as a tool_result error `PreToolUse:<tool> hook error`; D1 | 6 blocks (Bash 5, Grep 1) + 9 PreToolUse graft-nag contexts (Grep 6, Glob 3); the hook and its settings entry landed in 4bfa4da 2026-09-24T19:08:01Z (`.claude/hooks/search-intercept.py`, `.claude/settings.json`, `scripts/install_session_hooks.py`) | `errheads.py`; F01 `harness:hook-block` | SOLID (counts); the population of eligible searches not measured |
| R6 | Will this Edit/Write apply? | choice: applied / anchor not found / file not read / modified since read / anchor not unique / no change | `is_error` + fixed error text; D1 | 4,173 calls (main 1,149; sub 2,804; wf 220): applied 4,108; errors 65 (not found 25, file not read 24, modified since read 5, not unique 9, no change 1, other 1) | F05; `errheads.py` | SOLID |
| R7 | Will the Stop gate block this turn end, and why? | choice: pass / uncommitted / untracked / unpushed / retro gate (and pairs) | `stop_hook_summary.hookErrors` (git check `~/.claude/stop-hook-git-check.sh:28-36,119-123`, a harness file outside the repo, mtime 2026-09-24 14:49; retro gate `.claude/hooks/turn-retro-gate.sh:74`, 855370a 2026-09-24T13:15:53Z); D1 | 965 turn ends: pass 704; uncommitted 144; untracked 53; unpushed 13; retro gate 25; retro gate + a git reason 26 | F06 | SOLID |
| R8 | After the retro gate blocks, what is the retro answer? | choice: baked / nothing to bake / nothing to bake + edits / other tools / text only | the coordinator's next text and tool calls until the next owner message; "baked" = an Edit/Write/Bash naming a skill, the registry, `wiki/`, a hook or CLAUDE.md; D4 | 52 (main 50, second session 2): baked 36; nothing to bake 4; nothing to bake + edits 8; other tools 3; text only 1 | F07 | UNSURE (path regex classes) |
| R9 | Will this background command succeed? | yes/no; or status x exit code | notification `<status>` + `exit code N` in `<summary>`; D1 | 753 distinct notifications: completed exit 0 695; completed, no code 12; failed 45 (exit 1: 19, 144: 15, 70: 6, 143: 3, 124: 1, 3: 1); stopped 1. Joined to the launching call: 559 (main 454 of 487, sub 68 of 207, wf 37 of 59); 588 background launches seen | F08, F01b | SOLID |
| R10 | Will this agent dispatch complete? | choice: completed / failed / killed | agent notification `<status>`; synchronous `toolUseResult.status=completed`; D1 | 234 notifications: completed 214, failed 19 (code-implementer 14, adversarial-verifier 5), killed 1; + 23 synchronous completions = 257 dispatches | F09; `enums.py` | SOLID |
| R11 | Will one model serve this dispatch from start to end? | yes/no (match / mixed) | `toolUseResult.resolvedModel` vs every assistant record's `message.model` in the subagent transcript; D1 | 257 dispatches: match 251; mixed 4 (3 carry refusal stops, served opus-5-5 + opus-4-8; 1 served opus-5 + opus-5-5 with no refusal); no agent id 1; this lane 1. `resolvedModel`: opus-5[1m] 92, opus-5-5 81, opus-4-6[1m] 57, sonnet-5 21, opus-4-8 3, haiku-4-5 2 | F10; `enums.py` | SOLID |
| R12 | Which agent type and model tier for this task? | choice: 20 observed (type, model) pairs | the Agent call's `subagent_type` and `model`; D4 | 257: adversarial-verifier/opus 75, code-implementer/omitted 57, code-implementer/opus 52, adversarial-verifier/omitted 21, evidence-gatherer/opus 14, council-* 26, other 12. `model` omitted on 82 (CLAUDE.md calls omission a routing bug) | F11 | SOLID (counts) |
| R13 | How does the owner answer the coordinator? | choice by prefix: yes / no / option / free text | the owner's next text message (IL's rule: not a tool result, not meta, not an injected prefix); D5 | 224 owner messages (main 207, second session 17); 36 follow a coordinator text with `?` in its last 500 characters; prefix classes: yes 42, no 13, option 1, free 168. D-row join: 84 D-rows at `1e04e52`, 44 quote 4+ words, 17 of those quotes found in a main-session owner message (6-word window). 50 queued owner turns (`queued_command.humanTurn`) counted apart | F14; `drow_join.json` | UNSURE (prefix classes; string join) |
| R14 | Will push_clean push, and if not, why? | choice: pushed / refused (dirty tree, lanes mismatch, stale id, CI red, other) / CI wait / pre-push block / rewrite abort / other | push_clean's own lines (`scripts/push_clean.sh:23,27,53,61,71,125,128,140` refusals and aborts; `:146` `== pushing`; `:45`, `:160` success tails; 46338ed 2026-09-24T22:59:35Z), `WAIT by ci-gate` (`scripts/ci_gate.py:243,252`), `PUSH BLOCKED` (`scripts/hooks/pre-push:11,35,40,58`); D2 | 797 invocations (main 789, sub 8): pushed 714; dirty tree 14; lanes mismatch 8; CI wait 7; stale id 5; CI red 3; pre-push 3; rewrite abort 1; refused other 1; other rc 6; no marker in the output 35 | F16 | SOLID (named classes); UNSURE for the 35 |
| R15 | What will the CI gate say for this branch? | choice: pass (0) / refused (1) / wait (75) / cannot decide (2) | `ci-gate:` / `REFUSED by ci-gate:` / `WAIT by ci-gate:` (`scripts/ci_gate.py:34`, 5689d9f 2026-09-23T09:29:54Z); D2 | 113 direct calls (main 102, sub 11; first 2026-09-23T07:19Z): wait 51, pass 22, refused 5, sleep-blocked 1, no marker 34 | F17 | SOLID (named classes) |
| R16 | Will this commit pass the commit gates? | choice: committed / blocked by one of 8 named gates / staged-set refusal / nothing to commit / other | `COMMIT BLOCKED ...` (`scripts/hooks/pre-commit:19,38,57,77,90,101,112,127,141,154`, 41b79a8 2026-09-24T21:22:36Z; `scripts/hooks/commit-msg:16`, b02e12a 2026-09-24T21:50:04Z); `REFUSED:` (`scripts/safe_commit.sh:12-16`, b3ef7da 2026-09-03T05:13:12Z); git's `[<branch> <sha>]` or `N files changed`; D2 | 1,321 invocations (main 1,217; sub 97; wf 7): committed 881; blocked 67 (never-a-gate screen 24, lane-skills sync 13, future stamp (staged) 11, lint delta 8, skills sync 6, vendored manifest 3, bash -n 1, vendored class counts 1); staged-set refusal 10; nothing 2; other rc 11; no marker 350. 0 MIRROR-gate and 0 message future-stamp blocks seen | F18 | SOLID (named classes); UNSURE for the 350 (includes temp-repo commits inside test fixtures, not separated) |
| R17 | Will this test run be green? | choice: green / red / empty; score: passed and failed counts | the last pytest summary line in the output; D2 | 3,324 invocations of pytest / `test_summary.sh` / `lane_gate.sh` / `run-all.sh` / `pc_suite.sh wait` (main 944; sub 2,071; wf 309): green 1,813; red 934; empty 31; no summary line 546 | F19 | SOLID (named classes) |
| R18 | Which AP-screen tells does this edit hunk trip? | multi-label: none or one or more AP ids | the edit-snapshot hook's `registry screen` lines in `hook_success.stdout` (`.claude/hooks/edit-snapshot.py:132` `AP_SCREEN`, `:613`, `:658`; b6ea4b3 2026-09-24T23:50:37Z); D3 | 346 snapshots since 2026-09-24T11:23Z (main 31, sub 315): none 260; 1+ tells 86 (AP-61 35, AP-60 22, AP-32 16, AP-1 7, AP-24 6, AP-51 5, AP-66 4, AP-2 3, AP-3 1) | F22 | SOLID (counts) |
| R19 | Will CI pass for this pushed head? | choice: success / failure / cancelled | Actions API `conclusion` in `mcp__github__actions_list` results; D1 | 233 distinct runs in 91 listing calls: stage0-ci 131 (success 66, failure 64, cancelled 1); stage1-gate 21 (2 / 19); tests 13 (6 / 7); planning 22, ledger-integrity 22, harness-suites 22 (all success); planning-checks 2 (failure) | `decisions.py` extra `ci_run_conclusion` | UNSURE (only the runs the listings returned; not the full run history) |
| R20 | Will this model request be refused? | yes/no | `stop_reason=refusal`; `model_refusal_no_fallback`; D1 | 27 refusal stops (main 20, sub 7) + 5 no-fallback refusals (category `cyber`), among 40,555 distinct request ids | extra `refusal_stop`; `enums.py` | SOLID |
| R21 | What gate recommendation does this verify lane return? | choice: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID | the word in the verifier's final message; the workflow verdict field; D2 | IL d7: 85 of 110 verifier final messages; IL d4: 66 (lane, word) pairs in the main session; + 12 workflow verify verdicts (`structured_output.verdict=NOT-READY` x12) | IL; `enums.py` | UNSURE (IL's regex) |
| R22 | Which class is this verifier finding? | choice: BLOCKER / FOLLOW-UP / INFO / UNVERIFIED / CONTRACT-DEFECT / KNOWN | the class word on the verifier's anchor line; D2/D3 | IL d7: 666 distinct class-tagged ids in 35 of 110 verifier transcripts, 599 inside committed reports | IL | UNSURE (IL's regex) |
| R23 | Does this lane get a repair round? | yes/no | a later dispatch whose description names a round `R1`..`R9`; D4 | 40 of 257 dispatch descriptions name a round (adversarial-verifier 16 of 96, code-implementer 21 of 109, council 3) | extra `dispatch_repair_round` | UNSURE (description regex; not linked to the NOT-READY it repairs) |
| R24 | How does this PC lane end, seen from the sandbox? | choice: report delivered / patch delivered / timed out (the poller's 60-minute wait) / premise gate | `[lane-<id>] pc_lane: <kind>` lines in Monitor events and task output files; D2 | distinct lanes per kind: report 45, patch 43, timed out 34, premise gate 8 (from 611 distinct Monitor events in main; the 524 task output files give the same sets, 63 files carry the lines) | `pclane` in `decisions.py`; `days_tasks.py` | UNSURE (a lane can show several kinds; the terminal kind per lane is not resolved) |
| R25 | Which status does this task move to? | choice: pending / in_progress / completed / deleted | `toolUseResult.statusChange`; D4 | 631 changes in 1,213 TaskUpdate calls: pending->in_progress 201, completed->deleted 200, in_progress->completed 179, pending->completed 27, in_progress->deleted 13, other 11 | `enums.py` | SOLID (counts) |
| R26 | Which registry class does this defect get (a new AF-AP row or an existing one)? | choice: an AF-AP id or new | the registry row written in the same session; D4 | Skill `bug-echo` invoked 1 time (main); 0 `/bug-echo` slash commands (the only slash command is `/model`, 7); `docs/INCIDENT-LOG.md` writes: 46 Edit + 183 `anchor_edit.py` calls (main), 1 (sub); new registry-row ids visible in Edit inputs: 18 distinct | extras `skill`, `slash_command`, `incident_log_writes` | UNSURE (the `anchor_edit.py` calls pass their text as `@file` values, so their ids are not in the records) |

26 rows; 18 with a D1 or D2 label: R1, R2, R4-R7, R9-R11, R14-R17, R19-R21, R24 (17 rows), and R22 (D2/D3).

### 2.2 State, length and risks per row

State length = characters of the serialized state fields (median / p90). Scrub class (per state, from the repo's
`transcript_export.scrub`, never a value): **c2** = a rule other than the coarse 40+ character opaque-run rule fires
(credential-shaped); **c1** = only the opaque-run rule fires (it also fires on hashes and ids). Near-duplicates: states
are hashed after hex runs -> H, digits -> N and whitespace collapse; "conflicting" = one normalized state with more than
one answer.

| # | State fields | Chars median / p90 (max) | Label leak (measured) | Secret-shaped (scrub) | Near-duplicates |
|---|---|---|---|---|---|
| R1 | `command`, `description` | 411 / 2,245 (75,156) | 15,963 of 34,272 commands end in a pipe (15,946 with no `pipefail`): the code is the last pipe command's; non-zero on 103 of them (0.6%) vs 565 of the 18,288 unpiped ones with no `pipefail` (3.1%). 2,173 end in `echo`/`printf`/`true`/`:`/`\|\| true` (answer 0 on 2,128). A literal `exit N` in 151. Outcome words in the description (written before the call) in 1,490 (non-zero answer on 40) | c2 495, c1 2,073 | 33,624 distinct of 34,272; 1,013 rows in repeated states; 10 conflicting states (25 rows) |
| R2 | `command` | 172 / 500 | none measured | 0 | 104 distinct of 108; 2 conflicting (6 rows): the same command blocked and not blocked |
| R3 | tool name, full input | 694 / 4,610 | the state excludes the output the family is read from; 57% of labels are the catch-all `exit code N` | c2 37, c1 96 | 889 distinct of 900 |
| R4 | tool name, full input | 967 / 8,638 | none measured | c2 4, c1 6 | 50 distinct of 51 |
| R5 | tool name, input | not measured | - | - | - |
| R6 | tool, `file_path`, `old_string`, `new_string` (Edit) or content length (Write) | 641 / 2,975 | the answer depends on the file's bytes and the read history, neither in the state; `old_string == new_string` 1 (no change); 22 retries of a failed (path, anchor) pair (21 then applied) | c2 77, c1 425 | 3,888 distinct of 4,173; 21 conflicting (60 rows) |
| R7 | the record holds no git state; proxy built here = the turn's tool names | 59 / 460 | none; but the proxy does not decide the answer: 24 proxy states with conflicting answers hold 600 rows; 267 turns with 0 tool calls (pass 247, block 20) | c1 2 | 379 distinct of 965 |
| R8 | the gate's checklist text (fixed) + the batch's changes (not built) | - | the answer is the coordinator's own text | - | the prompt is the same fixed text each time |
| R9 | the launched `command` | 216 / 598 | none measured | c1 11 | 453 distinct of 753; 3 conflicting states hold 200 rows (re-launched waits and pollers) |
| R10, R12 | `description` + first 2,000 characters of the prompt | 2,071 / 2,086 (capped) | the description often names the lane and round (R23) | c2 4, c1 52 | 219 distinct of 234 (R10); 256 of 257 (R12) |
| R11 | requested type, requested model, resolved model | 100 / 102 | the answer depends on refusals during the run, not in the state | 0 | 23 distinct of 257 |
| R13 | the coordinator's last text (last 500 characters) + an asked flag | 553 / 558 | the answer is the owner's text; voice-typed personal text | c2 1, c1 2 | 210 distinct of 224 |
| R14 | `command` (often compound: edits, commit and push) | 1,075 / 5,590 | the outcome depends on the tree and CI state, not in the command; override variables (`CI_WAIT_SKIP=`, `STALE_ID_OK=`) in a command force a class (not counted) | c2 2, c1 98 | 687 distinct of 797; 5 conflicting (15 rows) |
| R15 | `command` | 247 / 797 | none measured | c1 1 | 107 distinct of 113; 2 conflicting (7 rows) |
| R16 | `command` (includes the commit message) | 1,843 / 4,581 | bypass flags (`SKIP_STAMP_CHECK=`, `--no-verify`) in 23 (blocked anyway 8, committed 5, no marker 8, other 2); the gates read the staged diff, not in the command | c2 9, c1 173 | 1,319 distinct of 1,321 |
| R17 | `command`, `description` | 571 / 2,176 | outcome words in the description in 515 (red 261, green 157, other 97); an expected count (`N passed`) in the command in 21; 883 of the 934 red runs exit 0 (piped or forced), so R1's label disagrees with R17's; the outcome depends on the code under test, not in the command | c2 29, c1 437 | 3,264 distinct of 3,324; 9 conflicting (26 rows) |
| R18 | tool, `file_path`, hunk (`new_string`, or the first 4,000 characters of the content) | 1,137 / 4,369 | the answer is a fixed function of the hunk (the hook's regexes): learnable exactly, a rule copy | c2 20, c1 17 | 346 distinct of 346 |
| R19 | `head_sha` -> the commit's diff and message (built from git, not the transcript) | not built | - | - | 131 stage0-ci runs over distinct heads |
| R20-R26 | see 2.1 | not built | R25: the new status is an input field of the call (leak by construction) | - | - |

### 2.3 Producers and reproducibility

All under `$S`; every one ran with rc 0.

```
python3 shapes.py                                   # record types, block types, field names -> shapes.json
python3 enums.py                                    # enumerated values -> enums.json
PYTHONDONTWRITEBYTECODE=1 python3 notif.py          # notification tags and kinds -> notif.json
PYTHONDONTWRITEBYTECODE=1 python3 errheads.py       # normalized heads of non-exit-code tool errors (stdout)
PYTHONDONTWRITEBYTECODE=1 python3 decisions.py      # families F01-F22 -> inst/*.jsonl, decisions_summary.json, drow_join.json
python3 famstats.py                                 # distinct / conflicting states, scrub classes -> famstats.json
python3 leaks.py; PYTHONDONTWRITEBYTECODE=1 python3 pipes.py   # label-leak tallies -> leaks.json, pipes.json
python3 days_tasks.py                               # main-session day histogram; task output file counts -> days_tasks.json
```

Reproducibility: `decisions.py` ran six times while its parsers were refined (runs 1-4 are superseded). Runs 5 and 6
(01:55Z and 01:56Z) produced byte-equal summaries and D-row joins (`decisions_summary.run5.json` vs `.run6.json`: no
differing key). Between runs 3 and 4 only R1 moved (+6 rows): the growth was this lane's own transcript, which runs 5
and 6 exclude. The main session file was 704,025,999 bytes in runs 4-6; the running DSV2 build lane's transcript
(`agent-ac9c149483559ffec`) grew between runs 5 and 6 without changing any count. Counts will move as the live
transcripts grow.

Precision of the command-position detector (`invokes` in `decisions.py`; R14-R17 count only calls that RUN the tool,
not calls that read, grep or edit it): 15 hand-written cases incl. 7 negative controls (a `grep` of the script, a
heredoc body holding `git commit`, `pip show pytest`, `pc_suite.sh launch`), 15/15 as expected. The first parser
(substring match) counted 1,085 push_clean calls; the command-position count is 797.

## 3. The top five: examples and label-leak checks (E11; evidence demand 2)

Selection rule (stated, not judged): rank the rows by the number of instances with a D1 or D2 answer, excluding
instances with no answer marker. D3-D5 rows are ranked after them.

| Rank | Row | Class | Instances with an answer | Excluded (no marker) |
|---|---|---|---|---|
| 1 | R1 Bash exit status | D1 | 34,272 | 0 |
| 2 | R6 Edit/Write applies | D1 | 4,173 | 0 |
| 3 | R17 test run outcome | D2 | 2,778 | 546 (no summary line) |
| 4 | R16 commit gate outcome | D2 | 971 | 350 (no marker) |
| 5 | R7 Stop gate | D1 | 965 | 0 |
| next | R3 error family | D3 | 900 | 0 |
| next | R14 push_clean outcome | D2 | 762 | 35 |
| next | R9 background command outcome | D1 | 753 | 0 |

Example rule (`$S/examples.py`, `$S/examples.json`): per row, one instance per chosen answer class, drawn with
`random.Random(20260925)` from instances whose state the repo scrubber leaves unchanged (scrub class 0) and whose state
is at most 400 characters (the commit row's refusal class had none that short; its pool allowed 3,000). The text is
read back from the source line, passed through `transcript_export.scrub`, whitespace-collapsed, scrubbed again and cut
at 110 characters. Provenance "subagent" hides the agent id.

### 3.1 The label-leak checks run

| Row | Check | Result | Producer |
|---|---|---|---|
| R1 | the state holds the call input only; the output the answer is read from is never in it | by construction | `decisions.py` |
| R1 | last segment piped, no `pipefail` (the recorded code is the last pipe command's) | 15,946 of 34,272 (+17 with `pipefail`); non-zero answer on 103 (0.6%) vs 565 of 18,288 unpiped with no `pipefail` (3.1%) | `pipes.py` |
| R1 | forced-zero ending (`echo`, `printf`, `true`, `:`, `\|\| true` last) | 2,173 (answer 0 on 2,128; non-zero on 33; harness 12) | `leaks.py` |
| R1 | literal `exit N` in the command | 151 (non-zero answer on 7) | `leaks.py` |
| R1 | outcome words in the description, written before the call (`fail`, `expect`, `error`, `refuse`, `red`, `green`, ...) | 1,490 (non-zero answer on 40) | `leaks.py` |
| R6 | `old_string == new_string` (decides `no change`) | 1 | `leaks.py` |
| R6 | a retry of a (path, anchor) pair that failed earlier in the same transcript | 22 (21 then applied) | `leaks.py` |
| R6 | does the state decide the answer? | no: it needs the file's bytes and the session's read history | - |
| R17 | outcome words in the description | 515 (red 261, green 157, no summary or empty 97) | `leaks.py` |
| R17 | an expected count (`N passed` / `N failed`) in the command | 21 | `leaks.py` |
| R17 | exit code vs the summary line | 883 of 934 red runs exit 0 (piped, or a forced-zero ending) | `leaks.py`, `pipes.py` |
| R17 | identical normalized commands with different answers (the code under test changed) | 9 states, 26 rows | `famstats.py` |
| R16 | bypass flags in the command (`SKIP_STAMP_CHECK=`, `--no-verify`, `commit -n`) | 23 (blocked anyway 8, committed 5, no marker 8, other 2) | `leaks.py` |
| R16 | a blocked command whose own text names the gate that blocked it | 10 of 67 (never-a-gate screen 3, skills sync 3, bash -n 1, future stamp 1, vendored manifest 1, vendored class counts 1) | `examples.py` |
| R7 | does the proxy state (the turn's tool names) decide the answer? | no: 24 proxy states carry more than one answer and hold 600 of 965 rows; the git state the hooks read is not recorded | `famstats.py` |
| all five | secret-shaped states (scrub class c2 / c1) | R1 495 / 2,073; R6 77 / 425; R17 29 / 437; R16 9 / 173; R7 0 / 2 | `famstats.py` |

### 3.2 Examples (3 per row)

**R1 (Bash exit status)**

| # | Provenance (source, line, time) | State fields (scrubbed, cut) | Recorded answer | Leak flags on this row |
|---|---|---|---|---|
| 1 | subagent line 272, 2026-09-23T15:00:43Z | command `grep -n "^REPO\\|REPO =" scripts/lint_delta.py; sed -n 640,660p tests/test_no_laya_in_gates.py`; description `Find REPO in lint_delta and the closed-set lock test` | `0` | none |
| 2 | subagent line 178, 2026-09-23T03:09:47Z | command `/root/venv-agent-factory/bin/python -m pyflakes tests/test_s0_05_egress.py 2>&1`; description `Run pyflakes on the test file` | `1` | none |
| 3 | main line 93429, 2026-09-23T12:17:08Z | command `sleep 45 2>/dev/null; f=/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/tasks/a6a158a80a6315271....`; description `Read which model serves the new verifier from its transcript` | `harness:harness blocked a foreground sleep` | none |

**R6 (Edit/Write applies)**

| # | Provenance (source, line, time) | State fields (scrubbed, cut) | Recorded answer | Leak flags on this row |
|---|---|---|---|---|
| 1 | main line 8621, 2026-09-04T11:17:57Z | file_path `/home/user/agent-factory/proofs/S0-11/runner_design.md`; content_len 5800 | `applied` | none |
| 2 | subagent line 640, 2026-09-24T06:22:12Z | file_path `/home/user/agent-factory/tasks/briefs/kit-k1-support/K215-report.md`; content_len 34260 | `error:edit anchor` | none |
| 3 | subagent line 217, 2026-09-05T18:39:45Z | file_path `/home/user/agent-factory/.claude/hooks/edit-snapshot.py`; old_string `("AF-AP-38", re.compile(r"""(?:if\s+\w+\.get\([^)]*\)\s*:(?=[^\n]*PINNED_)\|assert\s+\w+\.get\()"""),`; new_string `("AF-AP-38", re.compile(r"""(?:if\s+\w+\.get\([^)]*\)\s*:(?=[^\n]*PINNED_)\|assert\s+\w+\.get\()"""),` | `error:no-change` | same |

**R17 (test run outcome)**

| # | Provenance (source, line, time) | State fields (scrubbed, cut) | Recorded answer | Leak flags on this row |
|---|---|---|---|---|
| 1 | main line 4725, 2026-09-03T21:53:43Z | command `python -m pytest tests/ -q 2>&1`; description `Run pytest suite` | `green` | none; rc 0 |
| 2 | subagent line 499, 2026-09-07T14:57:48Z | command `python3 -m pytest tests/test_s0_01_check_acp_conformance.py -k "ck9_fifo_at_identities or ck9_no_tee_parented ...`; description `Run bundle-dependent new tests` | `red` | none; rc 0 |
| 3 | subagent line 439, 2026-09-08T03:02:55Z | command `SC=/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad; cd $SC/vck12 && S0_01_VENUE=sandb...`; description `Re-run gate chunk 3 of 3` | `empty` | none; rc 0 |

**R16 (commit gate outcome)**

| # | Provenance (source, line, time) | State fields (scrubbed, cut) | Recorded answer | Leak flags on this row |
|---|---|---|---|---|
| 1 | main line 116291, 2026-09-24T12:22:08Z | command `git reset -q; bash scripts/safe_commit.sh -m 'wiki+ledger: live-state 12:2xZ (JT1 dispatched, a sandbox-local ...`; description `Commit the live-state and ledger updates` | `committed` | none |
| 2 | main line 48886, 2026-09-17T09:25:16Z | command `MSG=/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/prism-integrate-msg.txt && bash s...`; description `Commit the prism integration edits` | `blocked:lane-skills sync` | none |
| 3 | main line 52041, 2026-09-17T18:49:53Z | command `echo "=== D-033 present in lane-skills copy? ===" && grep -c "DISPOSITION IS GOOD-STATE-GATED" .agents/lane-sk...`; description `Verify lane-skills copy, commit all four paths` | `refused:staged-set` | none |

**R7 (Stop gate)**

| # | Provenance (source, line, time) | State fields (scrubbed, cut) | Recorded answer | Leak flags on this row |
|---|---|---|---|---|
| 1 | main line 38257, 2026-09-15T08:13:57Z | turn tool names `Bash, Bash, Bash, Bash`; 4 calls | `git:uncommitted`; hook text head `[~/.claude/stop-hook-git-check.sh]: There are uncommitted changes in t...` | none measured (proxy state) |
| 2 | main line 90537, 2026-09-23T10:33:03Z | turn tool names `Bash`; 1 calls | `pass`; no hook text | none measured (proxy state) |
| 3 | main line 116694, 2026-09-24T12:44:08Z | turn tool names `Bash, TaskCreate, Bash, Bash`; 4 calls | `retro-gate`; hook text head `[[ -f /home/user/agent-factory/.claude/hooks/turn-retro-gate.sh ] \|\| e...` | none measured (proxy state) |

Notes on the examples: R6 example 2 is a Write whose error falls in the `edit anchor` family, which lumps "string to
replace not found", "file has not been read yet" and "file has been modified since read" (`scripts/hiccup_families.tsv:16`);
the family does not say which. R17 examples 2 and 3 exit 0 although the summary says red and empty. R7 examples
1 and 2 both have proxy states of Bash calls only (4 and 1) and different answers.

## 4. Export budget (E12; evidence demand 3)

Bytes per record = the UTF-8 length of `json.dumps({"q": <family>, "state": scrub(<state>), "answer": <answer>,
"prov": {"src", "line", "ts"}})`, computed for every instance in `decisions.py` (`Fam.add`) and summed in `$S/budget.json`.
The state is the full scrubbed state of section 2.2 (R7: the proxy of tool names). Non-state bytes (answer, provenance,
keys) are 138-170 bytes per record (median). "Cut at N" is an UPPER bound: each state cut at N raw characters removes at
least one byte per character.

| Row | Records | Bytes per record: mean / median | Total, full states | Answered records only | Cut at 4,000 chars | Cut at 2,000 | Cut at 1,000 |
|---|---|---|---|---|---|---|---|
| R1 | 34,272 | 1,215.0 / 559 | 41,641,597 | 41,641,597 | 34,399,464 | 29,434,441 | 23,858,127 |
| R6 | 4,173 | 1,500.5 / 819 | 6,261,503 | 6,261,503 | 5,333,406 | 4,472,181 | 3,442,434 |
| R17 | 3,324 | 1,248.8 / 723 | 4,150,994 | 3,450,525 (2,778 records) | 3,728,910 | 3,292,126 | 2,656,962 |
| R16 | 1,321 | 2,597.6 / 2,015 | 3,431,379 | 2,338,273 (971 records) | 2,936,578 | 2,240,369 | 1,449,480 |
| R7 | 965 | 302.0 / 198 | 291,472 | 291,472 | 291,472 | 291,472 | 291,472 |
| **total** | **44,055** | - | **55,776,945** (about 55.8 MB) | **53,983,370** (43,159 records) | 46,689,830 | 39,730,589 | 31,698,475 |

The other rows at full state, for scale (`famstats.json`): R3 1,879,112; R14 1,900,105; R9 344,761; R18 819,113; R10
461,070; R12 530,271; R13 144,776; R4 147,802; R2 41,699; R15 59,731; R11 62,219 bytes. Compression was not measured.

## 5. Factory mapping, one line per row (E13; evidence demand 4)

The agent-factory workflow or tool that asks the same question (repo files dated by their last change at `1e04e52`).

- R1 Bash exit status: every tool call a lane makes (the sandbox Bash tool; Hermes `terminal` on the PC lanes, 11,931 results in the PC digests); the fail-closed `pre_tool_call` policy hook (standing rule 9) asks "run or refuse" before, the exit code answers after.
- R2 foreground sleep block: the harness rule; the factory's own form of the question is the QUIRK table of `.claude/hooks/search-intercept.py` (part (b), 4bfa4da 2026-09-24T19:08:01Z).
- R3 error family: `scripts/hiccup_scan.py` + `scripts/hiccup_families.tsv` (the `docs/HICCUPS.md` page); its covering-rule column feeds bug-echo and the registry.
- R4 permission denial: the auto-mode classifier and permission rules here; the factory's `pre_tool_call` policy gate (standing rule 9).
- R5 search intercept: `.claude/hooks/search-intercept.py` (JT3; D-072 item 4).
- R6 Edit/Write applies: the edit tools (Hermes `patch` 5,632 and `write_file` 1,017 results in the PC digests); `scripts/anchor_edit.py` asks the same question for ledger edits (rc 2 on a missed anchor).
- R7 Stop gate: the stop hook (`~/.claude/stop-hook-git-check.sh`, outside the repo; `.claude/hooks/turn-retro-gate.sh`, 855370a 2026-09-24T13:15:53Z).
- R8 retro answer: the retro checklist of `turn-retro-gate.sh` and the deep-work retrospective rule.
- R9 background command outcome: background runs and waits (`scripts/pc_suite.sh launch|wait`, `scripts/relaunch-suite.sh`, the lane pollers).
- R10 agent dispatch outcome: the lane dispatcher (`scripts/pc_lane.sh`, `harness-ports/bin/pc-lane.sh`) and the Agent tool; FAILED vs landed.
- R11 served model: the harvest check CLAUDE.md prescribes (read the served model per assistant record; `scripts/hiccup_scan.py --transcript`, AF-AP-154).
- R12 routing: the CLAUDE.md model routing table; `scripts/pc_lane.sh <brief> hermes <role>` route and role choice.
- R13 owner reply: owner rulings recorded as D-rows in `docs/08_DECISION_LOG.md` (3be2475 2026-09-25T01:35:12Z).
- R14 push_clean outcome: the push path (`scripts/push_clean.sh` 46338ed 2026-09-24T22:59:35Z, `scripts/stale_ids.py` 18d6468 2026-09-24T22:26:17Z, `scripts/hooks/pre-push` 1309479 2026-09-22T14:10:30Z).
- R15 CI gate: `scripts/ci_gate.py` (5689d9f 2026-09-23T09:29:54Z), inside the push path.
- R16 commit gates: `scripts/hooks/pre-commit` (41b79a8 2026-09-24T21:22:36Z), `scripts/hooks/commit-msg` (b02e12a 2026-09-24T21:50:04Z), `scripts/safe_commit.sh` (b3ef7da 2026-09-03T05:13:12Z).
- R17 test run outcome: the gates (`scripts/test_summary.sh`, `scripts/lane_gate.sh`, `scripts/pc_suite.sh`); the contract gate's deterministic test pass.
- R18 AP-screen tells: `.claude/hooks/edit-snapshot.py` `AP_SCREEN` (b6ea4b3 2026-09-24T23:50:37Z) and `scripts/ap_screen.py`; bug-echo and the registry.
- R19 CI conclusion: the `stage0-ci` workflow, read by `scripts/ci_gate.py`.
- R20 refusal: refusal-stop harvest (AF-AP-154); `scripts/hiccup_scan.py` counts `stop_reason: refusal`.
- R21 gate recommendation: the verify lane (adversarial-verifier; skill `contract-gate`, D-031).
- R22 finding class: the verify lane's report; `scripts/decide-harvest` `v1.finding_class`.
- R23 repair round: the contract gate's repair budget (one focused repair per component, D-031).
- R24 PC lane outcome: the lane dispatcher `scripts/pc_lane.sh` / `harness-ports/bin/pc-lane.sh` (report path, patch path, FAILED marker, the 60-minute poller wait).
- R25 task status: the task ledger `todo/BUILD-TASKLIST.md` (TASK-DB mirror rule).
- R26 registry class: bug-echo and the ANTI-PATTERN REGISTRY atop `docs/INCIDENT-LOG.md` (d36ba41 2026-09-25T00:25:51Z).

## 6. NOT-done (E14; evidence demand 5)

1. PC lane tool outcomes: the committed PC digests keep only the tool name and the result size ("body not exported",
   29,211 tool results in 119 files), so the PC lanes' exit codes, test summaries and edit outcomes are not countable
   from them. The Hermes session databases on the PC were not read (no bridge, by the brief).
2. R7: the git state the Stop hooks read is not in the records; the proxy state (the turn's tool names) was built, the
   real state was not.
3. R13: owner messages were classed by their first words only; no message was read to classify a ruling, a question or
   an acknowledgement. The overlap between the 224 messages and the 50 queued owner turns was not measured. The D-row
   join is a 6-word string match over the main session only.
4. R19: only the runs the 91 listing calls returned; the full Actions history was not fetched (no network).
5. R21, R22: reused from IL, not recounted. R23: repair rounds were not linked to the NOT-READY each one repairs.
6. R24: a lane can show several kinds (a time-out, then a report); the terminal kind per lane was not resolved.
7. R26: 183 `anchor_edit.py` calls on the incident log pass their text as `@file` values, so the registry ids they add
   are not in the records; the (defect, AF-AP class) pairs were not built.
8. Rows with no answer marker were not resolved: R17 546 (no summary line), R16 350, R14 35, R15 34. Their outputs were
   cut (`| tail`), redirected to a log, or run in the background; the logs were not joined.
9. R16 counts commits inside temporary test repositories (subagent test fixtures) together with repo commits; they were
   not separated.
10. Recall of every regex-read answer (R8, R13, R14-R17 markers, R23, R24) was not measured; precision was checked
    only for the command-position detector (15 cases).
11. Near-duplicates are exact matches after normalization (hex -> H, digits -> N, whitespace); no fuzzy similarity was
    measured.
12. No export file was written (by the brief's size and scrub limits); section 4 sizes it from per-record lengths.
    Compression was not measured.
13. Not analyzed: the 198 tool-result files under the session directory, the second session's hook stdout files, and
    the SessionStart / UserPromptSubmit hook contexts. The 4 workflow journals were read; their 30 `result` records
    carry the same field sets and the same 12 NOT-READY verdicts as the `structured_output` attachments (not compared
    field by field; R21 counts the attachments only).
14. "Which tool next" (the actor's own next action) was not catalogued: its only label is the action itself.
15. `scripts/decide-harvest`'s `transcript_jsonl` kind was not run on these records (it reads committed
    `transcripts/*.jsonl` only, and committing a transcript is out of scope).

## 7. Adjacent facts and contradictions (recorded, not resolved)

| # | Fact | Evidence | SOLID/UNSURE |
|---|---|---|---|
| X1 | R1 and R17 disagree on the same calls: 883 of the 934 red test runs exit 0 (piped output or a forced-zero ending). | `leaks.json` (`rc0\|red` 883) | SOLID |
| X2 | `stop_hook_summary.preventedContinuation` is False in all 963 summaries, while `hookErrors` is non-empty in 260 of them. "Stop hook feedback" user messages (main 289, second session 2) outnumber summaries with `hookErrors` (main 261, second session 1); the 28-message gap in main was not explained, and whether a feedback message follows each such summary was not checked. | `enums.json`; a direct inline count after run 6 | SOLID (counts); cause UNSURE |
| X3 | CLAUDE.md says a dispatch that omits `model` inherits the session model and calls omission a routing bug (the rule dates from 6289ab6 2026-09-03T05:31:54Z). 82 dispatches omitted `model` (80 after that commit, 2 before it; 37 on 2026-09-06); their transcripts show each agent definition's model, not the session's: code-implementer opus-4-6 57, adversarial-verifier opus-5 21, evidence-gatherer opus-5 3, 1 with no served model. | F11 x F10 join; `git log -S` | SOLID (counts) |
| X4 | One dispatch (2026-09-22T18:07Z) was served by two models (opus-5 97 records, opus-5-5 86) with no refusal stop in its transcript; the three other mixed dispatches each carry refusal stops (1-3). | F10 rows | SOLID |
| X5 | 53 `sleep N`-first foreground commands ran with no block, and 2 normalized commands were blocked once and ran once. The harness rule is not in the repo; its history was not read. | F04 | SOLID (counts) |
| X6 | 714 successful pushes against 131 stage0-ci runs seen in the listings. | R14, R19 | UNSURE (the listings cover part of the history) |
| X7 | IL d3 counted 206 owner messages in the main session (file 700,478,822 bytes); this report counts 207 (file 704,025,999 bytes) with a rule written to match IL's. The two prefix lists were not compared line by line, so the difference is not attributed. | IL 3.1 d3; F14 | UNSURE (cause) |
| X8 | The edit snapshot reaches the transcript in `hook_success.stdout` as JSON (`hookSpecificOutput.additionalContext`); `hook_success.content` was empty on the 31 main-session snapshots checked. | an inline field probe of the main session (content empty on 31 of 31, stdout carrying the snapshot on 31 of 31); `probe_tails.py` (`ap_stdout_head`: 350 of 350 start with `{"`) | SOLID |
| X9 | Personal data in states: owner messages are voice-typed personal text (R13); PC paths carry the PC user's home directory name (seen in a Monitor event body read in the survey, and in all 119 committed PC digests, `grep -l`). Not counted in the session states. | `events.py` sample; `grep -l` over `transcripts/pc/` | UNSURE (not counted in states) |
