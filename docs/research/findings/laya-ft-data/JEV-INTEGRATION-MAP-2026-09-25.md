# JEV-INTEGRATION-MAP: where a System 1 Jev can read the session and act (2026-09-25)

Lane: JEV-MAP (task #253; owner direction D-086). Role: evidence-gatherer (EXPLORE, sandbox, Opus 5.5). Brief:
`tasks/briefs/jev-laya/JEV-MAP-brief.md`. Repository head at start: origin `e6bab18` (2026-09-25T02:39:31Z) on
`claude/soundbox-kit-migration-iz1jwf`. Scratch: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/jev-map/`.

STATUS: COMPLETE for this lane (written incrementally 2026-09-25T02:4xZ-03:2xZ, `date -u`). The only repository file this
lane wrote is this report. The NOT-done list is section 5.

This is a map and a set of measurements. It holds no verdicts. Each row is SOLID (read or measured in this session) or
UNSURE (inferred, or read from another report without a re-run).

**Headline measurements** (details and commands below):
- 35 decision points mapped (section 1); ten measured in depth (section 2).
- Where the prefix holds the cause, and where it does not:
  - An "unpushed" Stop follows a commit since the last push 17 of 18 times (passes: 122 of 708).
  - A re-run test with no write in between repeats its outcome 86 of 89 times.
  - An anchor miss shows an absent anchor in the visible file 13 of 13 times, when the whole file is visible.
  - A failed agent follows a sibling failure within 15 minutes 10 of 13 times (completed agents: 0 of 215).
  - An "uncommitted" Stop follows an uncommitted change of the coordinator's own turn 10 of 84 times (passes: 28 of
    499), in the window where the harness records Bash changes (from 2026-09-14T11:49Z).
  - Pre-push test outcomes do not separate CI failure from success (n = 43).
- The stream a reader would see: main session 59,514,467 characters, about 20.1 million Laya tokens, in 48,203 events
  (median 143 tokens each). Per compaction interval that is about 158,000 Laya tokens, against a median API context of
  785,712 tokens at compaction. Median per active hour: 166,573 characters, 129 events.
- The scrubbed export as specified loses three things these points need:
  - the 40-hex sha that joins a push to its CI run (the scrubber replaces it);
  - the harness's `edited_text_file` notices and its `bashEditDiff` record of files changed by Bash;
  - each assistant record's model, stop reason and API-error flags.

**The brief's three questions, measured:**
1. *Median session length between compactions.* The API context at compaction has a median `preTokens` of 785,712
   (126 main-session compactions; p10 147,894; p90 795,051), matching MOJEV's about 787k. The event stream a reader
   would see per interval is about 158,000 Laya tokens (UNSURE: a sampled tokenizer ratio, not RWKV's).
2. *Does the harness give a hook the transcript path?* Yes. Every classic hook's stdin carries `transcript_path`,
   `session_id` and `prompt_id` (the harness type declarations). Two harness hook scripts on disk already read the
   transcript that way; neither is registered.
3. *Which hooks have a timeout short enough to rule out a PC round trip?* None, by the measured round trips (0.62 s and
   1.64 s, n = 2). The only explicit timeouts are the cbm hooks' 5 s. The defaults are 15, 30 or 120 s by event, or 600 s
   (UNSURE which). The binding cost is added latency: a synchronous round trip on every PreToolUse call, against a 1.0 s
   median gap between the main session's records.

## 0. Method and sources

- **Transcripts.** A manifest froze every transcript's byte size at 2026-09-25T02:51:02Z (`$J/manifest.json`, A-7):
  298 files, 1,139,055,158 bytes: the main session (705,586,594 bytes), 259 subagent files (398,952,708) and 38 workflow
  files (34,515,856). This lane's own transcript (`agent-a085c903c7570bd07`) is excluded from every count. Every probe
  reads each file line by line, only up to its frozen size, so the counts do not move while the files grow. 22 lines do
  not parse (main 8, subagent 10, workflow 4) and are counted, not used. SOLID.
- **Probes** (all under `$J` = `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/jev-map/`):
  `p0_events.py` (Monitor event shapes), `p1_compact.py` (compaction sizes, request context), `p2_stream.py` (the
  decision points in stream order: labels, prefix features, record features, stream size), `p3_tokens.py` (tokens per
  event), `p4_analyze.py` (the cells of section 2, from p2's rows). Commands in Appendix A. No probe writes transcript
  text to disk: rows hold classes, booleans, line numbers and timestamps only.
- **Labels.** p2 copies DATA-SESSION's detectors (`invokes`, `segments`, the test, commit and push classes) so its classes
  match DATA-SESSION's R-rows. Counts differ slightly because the transcripts grew between the two reads (R1 34,272 then
  34,486; R6 4,173 then 4,205).
- **Determinism.** The final code, `p2_stream.py` runs 9 and 10 over the same manifest, gave a byte-identical summary
  (sha256 prefix `72cafe748da3c970`) and 22 byte-identical row files (digest of their concatenation `ad9adc3387d4903d`).
  Earlier pairs were identical too (runs 5/6, 7/8). Runs 7 and 9 each added features; a cell-by-cell comparison found 0
  changes to any earlier cell (A-10). Run 4 exposed one row file whose order depended on Python's per-process string
  hashing; the fix (a sorted list) is in the run-5 code. `p4_analyze.py` gave identical output on the run-5 and the
  final rows. SOLID.
- **Contention.** Two build lanes (DSV2, SESSION-EXPORT) and the sandbox Laya server ran during every probe (load
  average 0.36 / 1.12 / 1.58 at 03:05Z; 16 GB RAM, 11 GB available). No latency in this report is measured by these
  probes. Every speed is quoted from its own source with that source's method.
- **The scrubber.** The probes import `scrub` from the working tree's `scripts/transcript_export.py`, which the
  SESSION-EXPORT lane was changing (`git status` at 03:1xZ: modified; sha256 prefix `d0f7037f19c25c90` against HEAD's
  `f63cd97ef441b817`). It affects only the token sample of p3 and one printed error head. This report quotes no
  transcript text except harness-fixed shapes that passed `scrub`.
- **Code intelligence.** `graft skeleton .claude/hooks/search-intercept.py` returned "no definitions indexed" (graft
  excludes `.claude/`). The fallback was literal `grep -n` sweeps of definitions and constants in the hook files, which
  are named in the rows. No symbol was edited, so no impact analysis was run.
- **Other reports are claims.** DATA-SESSION (`SESSION-DECISIONS-2026-09-25.md`, 020bb21 2026-09-25T02:14:40Z),
  JEV-LEVERAGE (f601035 2026-09-24T12:12:55Z), MOJEV (817509b 2026-09-24T03:22:01Z) and the RWKV window-2 README
  (0f8c1b5 2026-09-24T23:35:43Z) are cited as UNSURE wherever this lane did not re-measure them.

## 1. The map table (evidence demand 1)

35 decision points. Table 1a says where and when each is asked, what an answer would change and the time budget. Table
1b gives its label, the cause measurements and the model. The ten points of section 2 are marked **[T]**. Every measured
cell names its command (A-n, Appendix A). "Prefix" means the same transcript's events before the decision. "Record" means
the decision record's own fields (the tool call's input, or the stop record).

Time-budget legend (section 3 has the evidence):
- **T-PRE / T-POST / T-UPS / T-STOP**: the harness default for a command hook with no `timeout` set (our five project hooks
  set none). The binary holds two values: a per-event table (PreToolUse and PostToolUse 15 s, UserPromptSubmit 30 s, Stop
  120 s) and a local-path default of 600 s. Which one governs this session is UNSURE (A-4).
- **Costs:** Q-RWKV = 0.046 s for a 15-token question from a copy of a saved 61,440-token state (3090, the README; UNSURE
  here). BR = one sandbox-to-PC bridge round trip through `scripts/jev.py`: 0.62 s and 1.64 s (n = 2; A-5). Q-LAYA = 1.0 s
  per question on the sandbox CPU (median; p10 0.47 s, p90 3.0 s; 240 rank calls; A-5).

### 1a. Where, when, effect, budget

| ID | Family | Question (type: options) | Event just before | Seam (file:line, last change) | What an answer would change | Time budget |
|---|---|---|---|---|---|---|
| D01 [T] | PreToolUse | Which exit class will this Bash call get? (choice: 0 / non-zero / harness block or timeout) | the assistant's Bash `tool_use` | PreToolUse `Grep\|Bash` (`scripts/install_session_hooks.py:53-55`, 4bfa4da 2026-09-24); hook `.claude/hooks/search-intercept.py:1161` `decide` | warn (KC-J1: never block) | T-PRE; the call waits. Q-RWKV + BR = 0.7-1.7 s; Q-LAYA 1.0 s. Main-session median gap between consecutive timestamped records 1.0 s (A-10) |
| D02 | PreToolUse | Will the harness block this sleep-first command? (yes/no) | Bash `tool_use` whose command starts `sleep N` | same seam; the rule is the harness's, not in the repo | warn, or rewrite as a background wait | T-PRE |
| D03 | PreToolUse | Will this call be denied, and by what? (choice: allowed / auto-mode / permission rule / user) | any `tool_use` | same seam for Bash and Grep; the auto-mode classifier's order relative to PreToolUse is UNSURE | warn | T-PRE |
| D04 [T] | PreToolUse | Will this Edit/Write apply? (choice: applied / anchor miss / not read / modified since read / not unique / no change) | Edit or Write `tool_use` | NO PreToolUse registration on Edit/Write today (matcher `Grep\|Bash`); PostToolUse `Edit\|Write\|Read` exists (`install_session_hooks.py:51-52`; `.claude/hooks/edit-snapshot.py`, b6ea4b3 2026-09-24T23:50Z) | warn; auto-Read before the Edit | T-PRE; Q-RWKV + BR |
| D05 | PreToolUse | Does this Edit need a Read first? (yes/no) | Edit or Write `tool_use` | as D04 | prefetch the Read | T-PRE |
| D06 | PreToolUse | Will the search intercept stop this search? (yes/no) | Grep or Bash search `tool_use` | `.claude/hooks/search-intercept.py:1161-1216` (4bfa4da); its Jev rank switch `:977-1000`, off by default (`:1208-1209`) | route to graft (already deterministic) | own budget 45 s (`:57`); rank timeout 20 s (`:61`) |
| D07 | PreToolUse | Is this Read redundant (same path and range, nothing written since)? (yes/no) | Read `tool_use` | no PreToolUse on Read today; PostToolUse `Read` exists (H3, H8) | skip the Read | T-PRE |
| D08 [T] | PreToolUse | Will this test run be green? (choice: green / red / empty / no summary; score: counts) | Bash `tool_use` that runs pytest, `test_summary.sh`, `lane_gate.sh`, `run-all.sh` or `pc_suite.sh wait` | the Bash seam of D01 | skip a run whose outcome is known; warn | T-PRE |
| D09 | PostToolUse | Which error family is this failure? (choice: 15 families + UNCOVERED) | the failed `tool_result` | `scripts/hiccup_scan.py:100-107,138-142` (d03e7c4 2026-09-24); map `scripts/hiccup_families.tsv` (764e516) | route to a registry row or quirk line | T-POST |
| D10 | PostToolUse | Which AP rows does this hunk resemble? (multi-label) | Edit/Write `tool_result` | `.claude/hooks/edit-snapshot.py:132` `AP_SCREEN` (a gate file: JEV-LEVERAGE §5 puts Jev in a separate hook) | warn (suggested, unverified) | T-POST; the wrapper allows 55 s (`scripts/hook_context.py:21`) |
| D11 | PostToolUse | Prune this large Bash output, and which chunks to keep? (score per chunk) | Bash `tool_result` over 10,000 estimated tokens | function hook `tool.call` on Bash, `fast-jev-output/0.1.0/hooks/fast-jev-output.ts:153-273` (plugin, not in the repo) | prune, with a recovery footer | the plugin sets no timeout |
| D12 | PostToolUse | Was this file changed outside the model? (yes/no) | harness attachment `edited_text_file` | harness-written stream event (no hook) | re-read before the next Edit | none (no model needed) |
| D13 [T] | Stop | Will the Stop git check fire, and why? (choice: pass / uncommitted / untracked / unpushed; plus retro gate) | the turn's last assistant text | Stop `~/.claude/stop-hook-git-check.sh:12-37,116-119` (harness, launcher settings); `.claude/hooks/turn-retro-gate.sh:74` (855370a 2026-09-24) | nudge before turn end: commit or push | T-STOP |
| D14 | Stop | After the retro gate blocks: bake or nothing? (choice: baked / nothing / nothing + edits / other) | the retro gate's feedback message | `.claude/hooks/turn-retro-gate.sh:66-74` | suggest the bake target | T-STOP |
| D15 | UserPromptSubmit | Which wiki, registry or skill file will this turn open? (rank over candidates) | the owner's text message | `.claude/hooks/wiki-context.py:77-139` (af3ab70 2026-09-24T12:39Z); harness events skipped (`:34-35,88`) | inject the section; cut the lexical 8 KB block | T-UPS |
| D16 | Stop / UserPromptSubmit | How will the owner answer? (choice: yes / no / option / free) | the coordinator's last text | no seam | none; prefetch the likely next step | - |
| D17 | SessionStart (compact) | Which files, ledger lines and tasks will the coordinator touch after this compaction? (rank over paths) | `compact_boundary`, then the `isCompactSummary` text | `.claude/hooks/session-start.sh:36-41` (af3ab70); cbm `compact` matcher (5 s) | inject or prefetch those files' lines | SessionStart: no table entry (600 s path); cbm 5 s |
| D18 [T] | Commit path | Will this commit pass the gates, or which gate blocks? (choice: committed / 8 gates / staged-set refusal / nothing) | Bash `tool_use` running `safe_commit.sh` or `git commit` | `scripts/hooks/pre-commit:19-154` (41b79a8 2026-09-24T21:22Z); `scripts/hooks/commit-msg:16` (b02e12a); `scripts/stamp_check.py:48,159` | warn before the commit | T-PRE (the Bash seam) |
| D19 [T] | Push path | Will push_clean push, refuse or wait? (choice: pushed / 6 refusals / wait / abort / pre-push block) | Bash `tool_use` running `push_clean.sh` | `scripts/push_clean.sh:23-146` (46338ed 2026-09-24T22:59Z) | warn; skip a doomed push | T-PRE |
| D20 | Push path | What will the CI gate say? (choice: pass / wait / refused / cannot decide) | Bash `tool_use` running `ci_gate.py` | `scripts/ci_gate.py:229-263` (5689d9f 2026-09-23) | skip a wait | T-PRE; `--wait 1800` exists |
| D21 [T] | Push path | Will stage0-ci pass for this pushed head? (choice: success / failure / cancelled) | the push's `tool_result` with `== pushing <sha> ==` | `scripts/ci_gate.py:229` reads it later | warn before the next push ("a CI red before the push") | minutes (a CI run) |
| D22 [T] | Dispatch | Will this background command succeed? (choice: ok / fail / stopped) | Bash `tool_use` with `run_in_background` | the Bash seam; the outcome arrives as a `<task-notification>` | skip a doomed wait; prepare the fallback | T-PRE |
| D23 [T] | Dispatch | Will this agent complete, fail or be killed? (choice) | Agent `tool_use` | no PreToolUse on Agent; SubagentStart: cbm 5 s, honey plugin | hold or re-route dispatches in a quota window | SubagentStart 15 s (table) |
| D24 | Lane dispatcher | How will this PC lane end? (choice: report / patch / timed out / premise gate / FAILED) | Monitor `<event>` lines | `scripts/pc_lane.sh:143-144,367-431` (1a94bbb 2026-09-23T18:47Z); premise gate `:185-222` | stop a lane early; re-dispatch | poll every 15 s, up to 60 min |
| D25 | Lane dispatcher | Is this lane stuck, looping on refusals or starved of KV cache? (yes/no per lane) | heartbeat `<event>` | no committed heartbeat script; runner retries `harness-ports/bin/pc-lane.sh:269-276,483-499` | stop or re-launch the lane | the heartbeat interval (ad hoc) |
| D26 | Routing | Which agent type and model tier for this task? (choice: 20 pairs) | Agent `tool_use` | CLAUDE.md routing table (no hook) | warn on a mismatch or an omitted `model` | T-PRE if a hook existed |
| D27 [T] | Verify lane | What gate recommendation will this verifier return? (choice: 4 words) | the verifier's last `tool_result` before its final text | the verifier's own stream; SubagentStop (not registered) | early triage (advisory only) | SubagentStop 120 s (table) |
| D28 | Verify lane | Which class is this finding? (choice: 6 classes) | a finding's anchor line in the report | `scripts/decide-harvest` `v1.finding_class` | rank findings | none (batch) |
| D29 | Verify lane | Will this lane get a repair round? (yes/no) | the NOT-READY verdict | the contract gate (D-031) | schedule the repair | none |
| D30 | Harvest | Did one model serve this dispatch start to end? (yes/no) | assistant records in the agent's stream | `scripts/hiccup_scan.py` (d03e7c4) | flag the mix at harvest | none (batch) |
| D31 | Harvest | Will this request be refused? (yes/no) | assistant `tool_use` / prompt | none | split a brief before dispatch | none |
| D32 | Bug-echo | Which registry class does this defect get? (rank over AF-AP rows) | the defect discussion | skill `bug-echo`; `docs/INCIDENT-LOG.md` | rank candidate rows | none |
| D33 | Factory runtime | Should this Hermes tool call run? (advisory annotation only) | the Hermes tool call | Hermes `pre_tool_call` offers only block, modify or approve, no advisory channel (`harness-ports/hermes/config-snippet.yaml:181-193`, 569914b 2026-09-15) | advisory note only: a Jev value in the policy decision is out (standing rule 9; KC-J1) | the snippet's commented `pre_tool_call` 20 s (`:192`) |
| D34 | Factory runtime | Dream triage: keep / promote-candidate / near-duplicate / noise (choice) | a snapshot record or a proposal | `docs/11_DREAM_PHASE.md:99-122` (fd2aa30 2026-09-23) | queue order label; never a filter | batch |
| D35 | Factory runtime | Is this Hermes lane done, stuck or failing? (choice) | Hermes session messages (PC) | `harness-ports/bin/pc-lane.sh:135-140,470-542`; Hermes state.db per cloned profile | stop a lane early | the runner's retry backoff (60 s doubling, `:274-276`) |

### 1b. Label, cause, model

| ID | Label (source field; class; count by answer) | Cause in the prefix (measured) | Cause in the record (measured) | Model | S/U | Cmd |
|---|---|---|---|---|---|---|
| D01 | R1: `is_error` + leading `Exit code N`, `timedOutAfterMs` (D1); 34,486 foreground calls: exit 0 33,660, non-zero 677, harness or timeout 149 | the same command ran earlier in the stream: 673 calls; same class 622 (exit 0 601 of 643; non-zero 21 of 30). A script the command names was edited since its last exit-0 run: non-zero 33 of 399 script-naming calls, exit 0 894 of 18,319 | forced-zero ending (`echo`, `printf`, `true`, `:`, `\|\| true`): exit 0 on 2,136 of 2,182 | both | SOLID | A-10, A-11 |
| D02 | R2: error text `Blocked: sleep N followed by` (D1); 108: blocked 55, ran 53 | an earlier block in the stream: blocked 31 of 55, ran 41 of 53 (no separation) | the sleep length: at most 5 s: blocked 0 of 33; 6-30 s: 10 of 30; 31 s or more: 45 of 45 | Laya | SOLID | A-10, A-11 |
| D03 | R4: `toolDenialKind` (D1); 51: auto-mode 29, permission rule 14, user 8 | an earlier denial in the stream: 38 of 51; the rate among allowed calls not measured | tool: Bash 39, SubagentHandback 8, Grep 2, Read 2 | both | SOLID (counts) | A-10, A-11 |
| D04 | R6: `is_error` + the error text (D1); 4,205: applied 4,140, anchor miss 25, not read 24, not unique 9, modified 5, no change 1, other 1 | a read or write of the same path earlier in the stream: applied 2,999 of 4,140; anchor miss 23 of 25; not read 14 of 24; not unique 9 of 9; modified 5 of 5. Main-session Edits: 652, prior 612, errors 11, errors with prior 9. With the whole file visible in the stream: the anchor is absent in 13 of 13 anchor misses and in 137 of 1,128 applied Edits. An outside change since the last read: modified 4 of 5, applied 437 of 4,140 | `old_string == new_string` decides no-change (1 of 1); nothing else in the record decides a class | RWKV (needs file bytes and read history) | SOLID | A-10, A-11 |
| D05 | R6 subset: "has not been read" (D1); 24: Edit 18, Write 6 | no read or write of the path earlier in the stream: 10 of 24; a read since the last compaction and still "not read": 13 of 24 (cause not visible). Applied Edits with no earlier read or write in the stream: 93 of 2,987 | none | RWKV | SOLID (counts); harness rule UNSURE | A-11, A-14 |
| D06 | R5: hook exit 2 (`PreToolUse:<tool> hook error`); 6 blocks + 9 nag contexts since 2026-09-24T19:08Z (DATA-SESSION) | not measured (the hook decides deterministically) | the search pattern and flags (the hook's classifier) | Laya (record) or none | UNSURE (not re-counted) | - |
| D07 | NEW, stream-derived: the same `(file_path, offset, limit)` read earlier with no write or outside change since; 2,437 Reads: redundant 32 | by definition (a rule over the prefix) | path, offset, limit | none needed (rule); RWKV optional | SOLID | A-10, A-11 |
| D08 | R17: the last pytest summary line (D2); 3,337: green 1,820, red 938, no summary 548, empty 31 | the same command ran earlier in the stream: 193 runs. No Edit/Write or repo-writing Bash between: outcome repeats 86 of 89. A write between: 60 of 104. Main only: 22 re-runs (no edit 12 of 13, edit 8 of 9) | outcome words in the description: red 261, green 157, no summary 95, empty 3. Exit code vs summary: 887 of 938 red runs exit 0 | both | SOLID | A-10, A-11 |
| D09 | R3: `hiccup_families.tsv` over the first error line (D3); 908: exit code N 523, sleep 56, edit anchor 54, python exception 47, missing path 41, UNCOVERED 39, other 148 | the same (tool, normalized first line) earlier in the stream: 216 of 908 | the error text decides by rule | Laya (record) or none | SOLID | A-10, A-11 |
| D10 | R18: `hook_success.stdout` registry screen (D3); 346 snapshots: none 260, one or more tells 86 (DATA-SESSION) | not measured | the hunk decides (the screen's regexes) | Laya (record) | UNSURE (not re-counted) | - |
| D11 | NEW: `toolUseResult.persistedOutputPath` (the harness saved a large output); 56 Bash results. No label for "which chunks mattered" | not measured | output size | Laya per chunk (the plugin's design) | SOLID (56) | A-10 |
| D12 | NEW: attachment `edited_text_file` (harness-written); 461 | it IS a prefix event | - | none | SOLID | A-10 |
| D13 | R7: `stop_hook_summary.hookErrors` (D1); 974: pass 708, uncommitted 164, untracked 60, unpushed 18, retro gate alone 24 (retro gate within a block: 28) | unpushed: a commit since the last push 17 of 18 (pass 122 of 708). Retro alone: a commit in the last 15 min 24 of 24 (pass 463 of 708). Uncommitted: any visible write since the last commit 110 of 164 (pass 385 of 708). Untracked: 25 of 60. The harness's own `bashEditDiff`, per turn, from 2026-09-14 (680 Stops): a Bash change after the turn's last commit before uncommitted 10 of 84, untracked 8 of 58, pass 28 of 499. After an uncommitted block, the next Stop passes 154 of 164 | the record's `cwd` does not decide: 85 blocks carry `cwd=/home/user`, not a git repository | RWKV | SOLID | A-10, A-11, A-14, A-16 |
| D14 | R8: DATA-SESSION F07 (D4 regex); 52: baked 36, nothing 4, nothing + edits 8, other 3, text 1 | not measured | the fixed checklist text | RWKV | UNSURE | - |
| D15 | NEW: the first Read or Bash touching `wiki/`, `docs/INCIDENT-LOG.md` or `.claude/skills/` in the turn after an owner prompt; 223 prompts: 113 followed (Bash 108, Read 5) | the prompt and the turns before (not scored) | the prompt text | Laya rank or RWKV | SOLID (counts); label precision UNSURE | A-10, A-11 |
| D16 | R13: DATA-SESSION F14 (D5 prefix classes); 224: yes 42, no 13, option 1, free 168; asked 36 | not measured | - | RWKV | UNSURE | - |
| D17 | NEW: paths read, edited or named by the first 20 calls after each compaction; 2,025 (compaction, path) pairs. Of the 126 main-session compactions: the ledger `todo/BUILD-TASKLIST.md` touched after 75, `wiki/topics/live-state.md` after 34, a task tool used after 48 (TaskList 11) | named (path or basename) in the compaction summary: 1,381 of 2,025 pairs. The summary names the ledger in 123 of 126 compactions (touched and named 73 of 75) and live-state in 106 (touched and named 34 of 34) | none | RWKV, or Laya rank | SOLID | A-10, A-11, A-19 |
| D18 | R16: `COMMIT BLOCKED` / `REFUSED:` lines, git's `[branch sha]` (D2); 1,326: committed 886, rc 0 with no marker 350, blocked 67, staged-set 10, other 13 | never-a-gate: the previous attempt was blocked by the same gate 11 of 24. Future stamp (gate live from 2026-09-23T02:07Z): a future stamp in the Edits and Writes since the last commit 2 of 10 blocks | a future stamp in the commit command itself: 8 of 10 blocks; either source 8 of 10 blocks vs 35 of 469 commits in the window. Bypass flags: 23 rows (never-a-gate blocked anyway 8) | both | SOLID | A-10, A-11, A-13 |
| D19 | R14: push_clean's own lines (D2); 799: pushed 715, rc 0 no marker 35, dirty tree 14, lanes mismatch 8, CI wait 7, stale id 6, CI red 3, pre-push 3, other 8 | dirty tree: a repo-writing Bash since the last commit 14 of 14 (pushed 285 of 715); an Edit/Write since the last commit 3 of 14 (pushed 144 of 715). CI red: a `REFUSED by ci-gate` line in the prior 30 min 2 of 3 | `--lanes-live` on 8 of 8 lanes-mismatch refusals (pushed 185 of 715); override variables on 9 rows | RWKV | SOLID | A-10, A-11 |
| D20 | R15: `ci-gate:` / `WAIT by` / `REFUSED by` (D2); 114: wait 52, pass 22, refused 5, other 35 | the previous verdict within 30 min: wait after wait 24 of 52; pass after pass 4 of 22 | - | RWKV | SOLID | A-10, A-11 |
| D21 | R19: `conclusion` in `mcp__github__actions_list` results for the pushed `head_sha` (D1); 434 pushes with a sha; 43 joined: failure 22, success 20, cancelled 1; 391 unseen | test outcomes since the previous push: failure: green 7, none 11, red 4; success: green 6, none 10, red 4 (no separation, n = 43) | none | RWKV plus the diff (not built) | SOLID (43); coverage UNSURE | A-10, A-11 |
| D22 | R9: notification `<status>` + `exit code N` (D1); 756: ok 710, fail 45, stopped 1 (launch matched 562) | the same command earlier with a known outcome: 64; the outcome repeats 61 | `pc_lane.sh` in the command: fail 7 of 45, ok 119 of 710 | both | SOLID | A-10, A-11 |
| D23 | R10: agent `<status>`; synchronous `toolUseResult.status` (D1); 247 agents with a transcript: completed 233, failed 13, killed 1 | a sibling failure notified in the 15 min before: failed 10 of 13, completed 0 of 215 (18 unknown). The agent's own stream: an API-error record in failed 13 of 13, always the last record (lead 0 s), and in completed 6 of 233 | dispatch type: failed code-implementer 9, adversarial-verifier 4 | RWKV | SOLID | A-10, A-11 |
| D24 | R24: `[lane-<id>] pc_lane: <kind>` (D2); DATA-SESSION: distinct lanes: report 45, patch 43, timed out 34, premise gate 8 | not measured (the heartbeat-to-lane join is not done) | premise gate: a deterministic function of the brief (`scripts/pc_lane.sh:193`) | RWKV | UNSURE | - |
| D25 | NEW: heartbeat lines in Monitor events; 113 heartbeat events of 467; 359 lane marks: alive 294, DEAD 65, `failed=F` 13, `msg_age` of 1,800 s or more 1; vLLM lines 46, `wait>0` 1, `wait>0` with `kv>=0.75` 0 | the heartbeats ARE prefix events; lead time to death not measured | - | RWKV or a rule | SOLID (counts) | A-9, A-10 |
| D26 | R12: `subagent_type` + `model` (D4); 257; `model` omitted 82 (DATA-SESSION) | not measured | the description and brief | Laya | UNSURE | - |
| D27 | R21: the word in the verifier's final text (D2); 93 verifiers: NOT-READY 57, WITH-FOLLOWUPS 22, MERGE-READY 4, CONTRACT-INVALID 2, none 8 | any red test run in the verifier's stream: NOT-READY 39 of 57, WITH-FOLLOWUPS 13 of 22, MERGE-READY 2 of 4 | the brief in the dispatch | RWKV | SOLID | A-10, A-11 |
| D28 | R22: class word per finding (IL); 666 ids | not measured | the finding text | Laya | UNSURE | - |
| D29 | R23: a later dispatch naming `R1`..`R9` (D4); 40 of 257 | not measured | - | RWKV | UNSURE | - |
| D30 | R11: `resolvedModel` vs `message.model` (D1); mixed 4 of 257 | a refusal stop before the first record of the second model: 3 of 4 | - | none (a count) | SOLID | A-10, A-11 |
| D31 | R20: `stop_reason=refusal` 27 + 5 no-fallback (DATA-SESSION) | not measured | - | RWKV | UNSURE | - |
| D32 | R26: registry ids in Edit inputs, 18 (DATA-SESSION; `anchor_edit.py` hides the rest) | not measured | - | Laya rank | UNSURE | - |
| D33 | none here: PC digests carry no result bodies; Hermes state.db not read | not measured | - | RWKV on the PC | UNSURE | - |
| D34 | none: the dream phase is not built; capture-only `dp.*` types need 200 human labels first (`docs/11_DREAM_PHASE.md:115`) | - | - | Laya per record or RWKV per snapshot | SOLID (absence, by the doc) | - |
| D35 | runner markers `FAILED`, `report.md`, `usage.json` (PC); not read | not measured | - | RWKV on the PC | UNSURE | - |

## 2. The ten points: cause-in-prefix, cause-in-record, label classes, leak risks (evidence demand 2)

**Selection rule (stated, not judged).**
1. Take the points whose label is a harness field or a fixed tool line (D1 or D2), with at least 40 labelled instances.
2. Drop the points a deterministic rule already answers: D02 (the sleep length), D07 (a stream rule), D09, D10 and D30
   (their labels are rule outputs or counts).
3. Fold D20 (114 CI-gate calls) into D19, the push path it belongs to.
4. Leave out D24 (lane outcomes): its terminal kind per lane is not resolved (section 5).
5. Ranked by labelled instances, the rest are D01 (34,486), D04 (4,205), D08 (3,337), D18 (1,326), D13 (974),
   D19 (799), D22 (756), D23 (247), D27 (93) and D03 (51), then D21 (43).
6. D21 takes D03's place: the brief names "a CI red before the push". D03's cells are in table 1b.

**How each count was made** (`p2_stream.py`, A-10; `p4_analyze.py`, A-11). The prefix features are computed when the
tool call is read, before its result, from the same transcript's earlier events only:
- "earlier read or write": a successful Read of the path, or a successful Write or Edit of it;
- "visible file": the last full Read's `toolUseResult.file.content` (whole when `startLine` is 1 and `numLines` reaches
  `totalLines`), or the last Write's content, with each later applied Edit's replacement applied to it;
- "outside change since the last read": an `edited_text_file` attachment for the file; a Bash command that names the
  file's basename and writes into the repository by the heuristic `bash_writes_repo`; or a `git`
  checkout/restore/stash/reset/apply;
- "since the last commit / push": since the last commit invocation whose class is `committed` or rc 0 without a marker, or
  since the last `pushed` push; a commit clears only the paths it names.

"Cause in the record" uses the decision record's own fields only.

### 2.1 D01: which exit class will this Bash call get? (R1)

| Answer class | Count | Same command earlier in the stream | Its class repeats | Record rule |
|---|---|---|---|---|
| exit 0 | 33,660 | 643 | 601 | forced-zero ending: 2,136 |
| non-zero | 677 | 30 | 21 | forced-zero ending: 34 |
| harness block or timeout | 149 | 0 | - | forced-zero ending: 12 |

- Cause in the prefix: 622 of 34,486 calls (1.8%) have an identical earlier command whose class repeats. A script the command
  names was edited since its last exit-0 run: non-zero 33 of 399 script-naming calls (8.3%), exit 0 894 of 18,319 (4.9%).
- Cause in the record: a forced-zero ending decides exit 0 on 2,136 of 2,182 such calls.
- Leak risks (measured): the description is written before the call. It holds outcome words in 1,494 calls (exit 0
  1,451, non-zero 40, harness 3). A literal `exit N` appears in 152 commands (exit 0 143, non-zero 7, harness 2). In
  pipelines with no `pipefail` the recorded code is the last command's (15,946 of 34,272 in DATA-SESSION). The result
  follows the call directly, so a training window cut one event late holds the answer.

### 2.2 D04 (and D05): will this Edit/Write apply? does it need a Read first? (R6)

| Answer class | Count | Earlier read or write | Seen since the last compaction | Anchor absent in the visible file (whole file visible) | Outside change since the last read |
|---|---|---|---|---|---|
| applied | 4,140 (Edit 2,987, Write 1,153) | 2,999 | 2,921 | 137 of 1,128 | 437 |
| anchor miss | 25 | 23 | 22 | 13 of 13 | 3 |
| not read | 24 (Edit 18, Write 6) | 14 | 13 | 0 of 1 | 10 |
| not unique | 9 | 9 | 9 | - (no file visible in all 9) | 0 |
| modified since read | 5 | 5 | 4 | 0 of 1 | 4 |
| no change | 1 | 1 | 1 | - | 0 |
| other | 1 | 0 | 0 | - | 0 |

- The coordinator's premise shape, re-measured on main-session Edits: 652 Edits, 612 with an earlier read or write, 11
  errors, 9 of them with an earlier read or write (premise: 652 / 614 / 11 / 9).
- Cause in the prefix. Anchor miss: when the whole file is visible, the anchor is absent in all 13 misses. The same test
  fires on 137 of 1,128 applied Edits: the stream's view had drifted from the file. The 12 other misses had no whole file
  visible. Modified since read: an outside change is visible in 4 of 5. Not read: no earlier read or write in 10 of 24.
  In the other 13, the stream shows a read since the last compaction. So the harness's own read state is not a function
  of the stream there (UNSURE why). 93 of 2,987 applied Edits had no earlier read or write in their stream.
- Cause in the record: only no-change (`old_string == new_string`, 1 of 1).
- Leak risks: the error result follows the call; DATA-SESSION counts 22 retries of a failed (path, anchor) pair. The
  earlier failure is a real cause, but it inflates accuracy on retries. `toolUseResult.originalFile` (1,130 results,
  DATA-SESSION) holds the whole pre-edit file, which the model never saw. D-1 does not export it; if an export did,
  the state would hold more than the model saw.
- Size risk: 169 Read results and 48 Write inputs exceed D-3's 32,768-character cap (A-12). For those files the
  reconstructed view is cut to the head and tail.
- The harness-exact outside-change signal (a `bashEditDiff` entry for the file since its last read; main session from
  2026-09-14T11:49Z): modified 1 of 1, applied 30 of 726, anchor miss 0 of 6.

### 2.3 D08: will this test run be green? (R17)

| Answer class | Count | Same command earlier in the stream | Its outcome repeats | Outcome words in the description | Exit code 0 |
|---|---|---|---|---|---|
| green | 1,820 | 151 | 119 | 157 | 1,805 |
| red | 938 | 29 | 18 | 261 | 887 |
| no summary | 548 | 13 | 9 | 95 | 498 |
| empty | 31 | 0 | - | 3 | 30 |
| all re-runs | - | 193 | no write between: 86 of 89; a write between: 60 of 104 | - | - |

- Cause in the prefix: an identical command ran earlier in 193 of 3,337 runs (5.8%). With no Edit, Write or repo-writing
  Bash between, the outcome repeats 86 of 89 times. With a write between, it repeats 60 of 104 times. Main session only:
  22 re-runs, repeating 12 of 13 with no edit between and 8 of 9 with one. The premise probe counted 40 re-runs (17 of
  18; 15 of 22). Its command matcher is not published; this lane matches the whole command after collapsing whitespace.
- Cause in the record: outcome words in the description, written before the run (red 261 of 938; green 157 of 1,820).
- Leak risks: the description words above; DATA-SESSION found an expected count in the command in 21 runs. The exit code
  disagrees with the summary on 887 of 938 red runs. So `outcome.exit_code` alone is a wrong label for them; the label
  must come from the summary line in `text`.

### 2.4 D18: will this commit pass the gates? (R16)

| Answer class | Count | Cause in the prefix | Cause in the record |
|---|---|---|---|
| committed | 886 | - | bypass flags 5 |
| rc 0, no marker | 350 | - | bypass flags 8 |
| blocked: never-a-gate | 24 | previous attempt blocked by the same gate: 11 | bypass flag present (it does not bypass this gate): 8 |
| blocked: lane-skills sync | 13 | a `.claude/skills/` Edit since the last sync run: 0 (the trigger was not an Edit call in the stream; what it was is UNSURE) | - |
| blocked: future stamp | 11 (10 inside the gate window) | a future stamp in the Edits/Writes since the last commit: 2 of 10 | a future stamp in the commit command itself: 8 of 10 |
| blocked: lint delta | 8 | a `.py` Edit since the last commit: 6 | - |
| blocked: skills sync | 6 | a `.claude/skills/` Edit since the last sync: 2 | - |
| blocked: vendored manifest 3, bash -n 1, class counts 1 | 5 | not measured | - |
| refused: staged set | 10 | previous attempt blocked: 4 | - |
| other (nothing 2, rc non-zero 11) | 13 | - | - |

- Gate windows (A-13): a gate's label exists only after the gate landed. Future stamp from 8d50443
  2026-09-23T02:07:28Z (497 commit calls after it). Message stamps from b02e12a 2026-09-24T21:50:04Z (69 after).
  Never-a-gate from 98a604a 2026-09-22T17:13:59Z. Lane-skills sync f2e94ee and skills sync 0fce196, both 2026-09-03.
  Lint delta b3ef7da 2026-09-03T05:13:12Z. Vendored manifest 1309479 2026-09-22T14:10:30Z. One block falls before its
  gate's commit time. The git hooks run from the working tree (`core.hooksPath`), so a gate is live before its commit
  lands; that this explains the row is UNSURE.
- Future stamp inside its window: either source flags 8 of 10 blocks and 35 of 469 commits that passed.
- Leak risks: 11 of 24 never-a-gate blocks are retries, with the block text already in the prefix. Compound commands
  carry the staged text in the command.

### 2.5 D13: will the Stop git check fire, and why? (R7)

| Answer class | Count | Commit since the last push | Commit in the last 15 min | Any visible write since the last commit | Edit/Write since the last commit | Agent completion since the last commit |
|---|---|---|---|---|---|---|
| pass | 708 | 122 | 463 | 385 | 106 | 29 |
| uncommitted (with or without the retro gate) | 164 | 61 | 114 | 110 | 40 | 10 |
| untracked | 60 | 29 | 53 | 25 | 2 | 0 |
| unpushed | 18 | 17 | 17 | 4 | 1 | 0 |
| retro gate alone | 24 | 24 | 24 | 3 | 3 | 0 |

- The hook reports only its first failing check, in order: uncommitted, untracked, unsigned commits, unpushed
  (`stop-hook-git-check.sh:26-37,116-119`). "Any visible write" is Edit/Write, repo-writing Bash, agent or background
  completion, or a lane's report or patch.
- Cause in the prefix: unpushed 17 of 18 and retro gate 24 of 24 have their cause visible (pass: 122 and 463 of 708).
  "Any visible write since the last commit": uncommitted 110 of 164 (67%), untracked 25 of 60 (42%), pass 385 of 708
  (54%). Only 40 of the 164 uncommitted Stops had an Edit/Write since the last commit.
- The harness's own record of Bash changes, `toolUseResult.bashEditDiff`, exists in the main session from
  2026-09-14T11:49Z (1,722 Bash results; `changedFiles` holds repo paths; `files[]` holds `filePath`, `hunks` and a
  `created` or `deleted` flag; A-16). In that window (680 Stops):
  - A repo file changed by Bash in the same turn after the turn's last commit: uncommitted 10 of 84, untracked 8 of 58,
    pass 28 of 499.
  - The same with an Edit/Write added: uncommitted 11 of 84, pass 30 of 499.
  - Any Bash-changed repo file not named by a later commit: pass 481 of 499. It does not separate; commits rarely name
    the files Bash touched.
  So most uncommitted and untracked Stops follow no visible uncommitted change of the coordinator's own turn. Which
  writers made those changes (other agents in the shared tree, lane outputs, background hooks, earlier turns) is UNSURE:
  not attributed per Stop (section 5, item 9).
- Cause in the record: none. The record's `cwd` is `/home/user` (not a git repository) on 85 of the blocks and 213 of
  the passes.
- Leak risks: the Stop feedback message ("Stop hook feedback: ...") is in the prefix of the next turn. After an
  uncommitted block the next Stop passes 154 of 164 times; 473 of 973 Stops repeat the previous class. The retro gate's
  label exists only from a12e672 2026-09-24T11:08:22Z in this session (118 Stops after it).

### 2.6 D19: will push_clean push, refuse or wait? (R14, with D20)

| Answer class | Count | Repo-writing Bash since the last commit | Edit/Write since the last commit | Gate verdict in the prior 30 min | Record |
|---|---|---|---|---|---|
| pushed | 715 | 285 | 144 | pass 28, wait 21, refused 3, other 8 | `--lanes-live` 185; override variables 4 |
| rc 0, no marker | 35 | 20 | 8 | pass 2, wait 2, other 4 | override 2 |
| refused: dirty tree | 14 | 14 | 3 | none | - |
| refused: lanes mismatch | 8 | 4 | 4 | - | `--lanes-live` 8 |
| wait: CI unknown | 7 | 1 | 0 | refused 1, wait 1, other 2 | override 1 |
| refused: stale id | 6 | 0 | 0 | pass 2, wait 1, other 1 | - |
| refused: CI red | 3 | 2 | 1 | refused 2 | override 2 |
| blocked: pre-push 3, abort 1, other 7 | 11 | - | - | - | - |

- Windows (A-13): the CI gate from 010d1bc 2026-09-23T06:29:44Z (111 push calls after it); stale ids from 2304181
  2026-09-24T21:30:44Z (17 after it).
- D20 (the CI gate alone, 114 calls): wait follows wait within 30 minutes in 24 of 52.
- The harness-exact signal (a `bashEditDiff` path since the last commit, main session from 2026-09-14T11:49Z) is on 2
  of 2 dirty-tree refusals and 439 of 451 pushes in that window. It does not separate, for the reason given in 2.5.
- Leak risks: override variables force a class (9 rows). Retries follow refusals, with the refusal text in the prefix.

### 2.7 D21: will stage0-ci pass for this pushed head? (R19)

- Label coverage: 434 pushes printed a sha. Only 43 matched a stage0-ci run that the 91 listing calls returned (failure
  22, success 20, cancelled 1); 391 did not.
- Cause in the prefix: main-stream test outcomes since the previous push. Failure: green 7, none 11, red 4. Success:
  green 6, none 10, red 4. No separation at n = 43. Most gates ran on the PC or in lanes, whose outputs the main stream
  sees only as reports.
- Cause in the record: none (the push command).
- Leak risks: the conclusion appears later in the same stream (`actions_list` results; the next push's CI gate line), so
  a window must end at the push.

### 2.8 D22: will this background command succeed? (R9)

| Answer class | Count | Launch command matched | Same command earlier with a known outcome | Outcome repeats | `pc_lane.sh` in the command |
|---|---|---|---|---|---|
| ok | 710 | 546 | 62 | 61 | 119 |
| fail | 45 | 16 | 2 | 0 | 7 |
| stopped | 1 | 0 | 0 | - | 0 |

- Leak risks: a Monitor event on the same task can show its output before the completion notification (a real, early
  cause; not counted). `pc_lane.sh` exits 75 at its 60-minute poll limit, so the command itself sets that outcome.

### 2.9 D23: will this agent complete, fail or be killed? (R10)

| Answer class | Count | Sibling failure notified in the 15 min before (main stream) | API-error record in the agent's own stream | Its lead before the end |
|---|---|---|---|---|
| completed | 233 | 0 of 215 (18 unknown) | 6 | - |
| failed | 13 (code-implementer 9, adversarial-verifier 4) | 10 | 13 | 0 s in all 13 |
| killed | 1 | 0 | 0 | - |

- The failures cluster in time: a failure that follows another within 15 minutes has its cause in the main prefix; the
  first failure of a cluster does not. The failed agents' own streams carry a `quotaLimits` field on an assistant record
  in 13 of 13 (completed: 6 of 233).
- Leak risks: in the agent's own stream the error IS the last record. DATA-SESSION counted 19 failed notifications;
  this lane has 13 agents whose transcript exists and whose last notification says failed.

### 2.10 D27: what gate recommendation will this verifier return? (R21)

| Answer class | Count | Any red test run in the verifier's stream | The word written into a file before the final message | BLOCKER in its text or plain thinking before the final message |
|---|---|---|---|---|
| NOT-READY | 57 | 39 | 10 | 6 |
| MERGE-READY-WITH-FOLLOWUPS | 22 | 13 | 7 | 3 |
| MERGE-READY | 4 | 2 | 0 | 0 |
| CONTRACT-INVALID | 2 | 1 | 1 | 0 |
| none found | 8 (4 of them failed agents) | 3 | 0 | 0 |

- Cause in the prefix: red runs are common in every class (verifiers run mutants on purpose), so "a red run" does not
  separate NOT-READY (39 of 57) from WITH-FOLLOWUPS (13 of 22).
- Cause in the record: the dispatch brief only.
- Leak risks: 18 of 93 verifiers wrote the recommendation word into a file (their incremental report) before their final
  message. Plain-text thinking exists in only 4,727 of 33,371 thinking blocks (the rest are signature-only), so the
  BLOCKER count is a floor.

## 3. The runtime path (evidence demand 3)

### 3.1 The hooks this harness runs in this session (read 2026-09-25 02:4xZ; hook entries and timeouts only)

Harness: Claude Code `2.1.280` (`claude --version`), a compiled binary at `/opt/claude-code/bin/claude` (233,709,640 bytes).
The session is rooted in `/home/user`, so four settings files feed it. Each row is one registered command hook.

| # | Event | Matcher | Command (script) | Registered in | Timeout set | SOLID/UNSURE |
|---|---|---|---|---|---|---|
| H1 | SessionStart | (all) | `.claude/hooks/session-start.sh` (af3ab70 2026-09-24T12:39:30Z) | `/home/user/.claude/settings.json` (written by `scripts/install_session_hooks.py:47-48`, 4bfa4da 2026-09-24T19:08:01Z) | none | SOLID |
| H2 | UserPromptSubmit | (all) | `.claude/hooks/wiki-context.py` (af3ab70) | same (`install_session_hooks.py:49-50`) | none | SOLID |
| H3 | PostToolUse | `Edit\|Write\|Read` | `scripts/hook_context.py PostToolUse -- .claude/hooks/edit-snapshot.py` (b6ea4b3 2026-09-24T23:50:37Z) | same (`:51-52`) | none (the wrapper's own subprocess cap is 55 s, `scripts/hook_context.py:21`) | SOLID |
| H4 | PreToolUse | `Grep\|Bash` | `scripts/hook_context.py PreToolUse -- .claude/hooks/search-intercept.py` (4bfa4da) | same (`:53-55`) | none (the hook's own budget 45 s, `search-intercept.py:57`) | SOLID |
| H5 | Stop | (all) | `.claude/hooks/turn-retro-gate.sh` (855370a 2026-09-24T13:15:53Z) | same (`:56-57`) | none | SOLID |
| H6 | Stop | (empty) | `~/.claude/stop-hook-git-check.sh` (harness file, mtime 2026-09-24 14:49) | `/root/.claude/launcher-settings.json` | none | SOLID |
| H7 | PreToolUse | `Grep\|Glob` | `$HOME/.claude/hooks/cbm-code-discovery-gate` | `/root/.claude/settings.json` | 5 s | SOLID |
| H8 | PostToolUse | `Read` | same gate | same | 5 s | SOLID |
| H9 | SessionStart | `startup`, `resume`, `clear`, `compact` | `$HOME/.claude/hooks/cbm-session-reminder` | same | 5 s | SOLID |
| H10 | SubagentStart | `*` | `$HOME/.claude/hooks/cbm-subagent-reminder` | same | 5 s | SOLID |
| H11 | SessionStart, SubagentStart, PostToolUse(`Bash`) | - | honey plugin hooks (`/root/.claude/plugins/cache/greenpt/honey/1.3.1/hooks/hooks.json`) | enabled plugin `honey@greenpt` | none | SOLID |
| H12 | SessionStart (`startup\|clear\|compact`) | - | aegis plugin (`.../aegis/2.10.6/hooks/hooks.json`) | enabled plugin `aegis@aegis-dev` | none | SOLID |
| H13 | function hook `tool.call` on `Bash` | - | `fast-jev-output` (`.../fast-jev-output/0.1.0/hooks/fast-jev-output.ts:153`); it calls a Jev scorer over HTTP and reads the whole session through `$.session.messages()` (`:193`) | enabled plugin `fast-jev-output@fast-jev-output`; option key `baseUrl` set (value not read) | none; engages only above 10,000 estimated output tokens (`src/output.ts:7`) | SOLID (code); engagement: JEV-LEVERAGE says 0 real pruner footers (UNSURE here, not re-measured) |

Present on disk but NOT registered in any settings file read: `/root/.claude/stop-hook-reply-gate.py` and
`/root/.claude/user-prompt-submit-reply-reminder.py`. Both already read the transcript through the hook input's
`transcript_path` (`stop-hook-reply-gate.py:327-328`, `user-prompt-submit-reply-reminder.py:51-54`). SOLID (file read);
their registration anywhere else (managed or remote settings) is UNSURE: `/root/.claude/remote-settings.json` is 2 bytes.

### 3.2 What a hook receives, and the timeouts

- Every classic hook's stdin JSON carries `session_id`, `transcript_path`, `cwd`, `prompt_id`, `permission_mode`, and
  `agent_id` / `agent_type` inside a subagent (`BaseHookInput` in the harness type file the fast-jev-output plugin
  vendors: `/root/.claude/plugins/cache/fast-jev-output/fast-jev-output/0.1.0/types/claude-code.d.ts:554-570`). So a hook CAN tail the transcript file: two harness hooks already do
  (3.1). SOLID for the type declaration and the two readers; that the running 2.1.280 sends the same fields is UNSURE
  (the type file is the plugin's copy, dated 2026-09-22 by its mtime).
- Hook kinds the running binary accepts (strings in `/opt/claude-code/bin/claude`): `command`, `prompt` (an LLM prompt
  hook), `http` ("URL to POST the hook input JSON to"), `mcp_tool`, `agent` ("Timeout in seconds for agent execution
  (default 60)"), plus plugin `function` hooks. An `http` hook would hand every event's JSON to a local reader
  directly, without a process spawn. SOLID (strings present); not exercised.
- Classic event names in the type file: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`,
  `PermissionRequest`, `PermissionDenied`, `UserPromptSubmit`, `UserPromptExpansion`, `Stop`, `StopFailure`,
  `SubagentStart`, `SubagentStop`, `SessionStart`, `SessionEnd`, `PreCompact`, `PostCompact`, `Notification`,
  `TaskCreated`, `TaskCompleted`, `FileChanged`, `CwdChanged`, `InstructionsLoaded`, `ConfigChange` and others (33 names;
  command in Appendix A, A-3).
- Default timeouts, two values in the binary (a CONTRADICTION, recorded, not resolved):
  - The local command-hook path: `Qt=e.timeout?e.timeout*1000:Ia` with `Ia=600000` (10 minutes). SOLID (string).
  - A per-event table `fTn={PreToolUse:15,PostToolUse:15,PostToolUseFailure:15,PostToolBatch:15,PermissionDenied:15,
    SubagentStart:15,UserPromptSubmit:30,UserPromptExpansion:30,Stop:120,StopFailure:120,SubagentStop:120}` in seconds,
    used by `defaultTimeoutMs` (`function nKr(e){return fTn[e]*1000`) beside a `cloud-transcript.jsonl` placeholder, which
    suggests a hook-worker path for cloud sessions. Which path runs this session's hooks is UNSURE.
  - Repo comments claim a third value: "Claude Code's 60 s default hook timeout" (`scripts/hook_context.py:21`) and
    "Claude Code 60 s" (`.claude/hooks/search-intercept.py:57`). The comments and the binary differ.
- A hook's text over 10,000 characters is swapped for a 2 KB preview (claim in `session-start.sh:19` and
  `wiki-context.py:37`, citing VERIFY-COORD-0924 F-L1-3). UNSURE here (not re-read from the binary).

### 3.3 The Jev services that exist today (measured)

- A sandbox-local Laya server IS running: pid 30467, `scripts/laya_systemone_server.py --threads 2 --device cpu`,
  up 14 h 29 min at 02:4xZ, RSS 2,850,588 KiB (`ps`). SOLID.
- `scripts/jev.py` (d03e7c4 2026-09-24T16:13:41Z) is the client: venues local `127.0.0.1:47411` then the PC over the
  bridge (`:62-63`, `:372-383`), default timeout 30 s (`:65`), health probe 1 s (`:64`), a call log in
  `.jev/calls.jsonl` (`:71-72`).
- Its call log (245 lines, 2026-09-24T12:48Z-16:48Z): fields `answers, cmd, latency_ms, n_questions, ok, qtypes, reason,
  state_sha256, ts, venue`; `rank` 240 calls (1-8 questions each, median 8), `ask` 1, `classify` 1, `health` 3; venue
  local 243, pc 2. Measured cost per question on the sandbox CPU (rank latency / questions): median 999.5 ms, p10
  472.4 ms, p90 3,024.4 ms; one `ask` 384.5 ms, one `classify` 427.8 ms. Contention during those calls was not
  recorded (agents were running that day). SOLID (the log's own numbers).
- The search intercept (H4) already calls `jev.rank` behind a switch that is OFF by default (`search-intercept.py:18-20`,
  `:977-1000`, `:1208-1209`; the file `.jev/intercept-jev-rank-on` or `AF_SEARCH_INTERCEPT_JEV_RANK=1`), with a
  20 s rank timeout (`:61`) inside a 45 s hook budget (`:57`). SOLID.

### 3.4 How a stream reader would receive the session live

**Venue A: this sandbox** (Claude Code 2.1.280; the session is rooted in `/home/user`).
- **Tail the transcript.** Every classic hook receives `transcript_path`, `session_id` and `prompt_id` (3.2). A reader keeps
  a byte offset and parses the new JSONL lines. At 02:51Z the main file held 705,586,594 bytes. The D-1-like stream in it
  is 59,514,467 characters, 8.4% of the raw bytes. The rest is attachments (task and token reminders), harness copies
  such as `toolUseResult.originalFile`, and record metadata (A-7, A-10). SOLID for the counts; tailing live was not
  exercised.
- **Hook payloads.** Registered today: PreToolUse (`Grep|Bash`), PostToolUse (`Edit|Write|Read`), UserPromptSubmit, Stop and
  SessionStart (3.1). The type file also lists `PostToolUseFailure`, `PostToolBatch`, `SubagentStop`, `PreCompact`,
  `PostCompact`, `TaskCompleted` and `Notification`, none registered here. An `http` hook would POST each event's JSON to
  a local URL without spawning a process.
- **A function-hook plugin** reads the session in process through `$.session.messages()` and calls an endpoint through
  `$.http.fetch` (`fast-jev-output.ts:193,236`).
- **Where the model runs.** The sandbox has no GPU (no `nvidia-smi`, no `/dev/nvidia*`; 4 CPUs), and RWKV-7's CPU speed is
  not measured. So in this venue every state update or question crosses the bridge to the PC, or events are shipped in
  batches. One bridge call carries one argument of at most 131,072 bytes (SESSION-EXPORT brief D-7 ships 96,000 base64
  characters per call, about 72,000 raw bytes).
- **Live rate** (main session, A-10): 283 active hours. Per active hour, the median is 166,573 stream characters (p90
  476,149) and 129 events (p90 369). The median gap between consecutive timestamped records is 1.0 s (p90 13.8 s; 93,212
  gaps). At those rates the stream needs about 2 to 7 batched bridge calls per active hour.

**Venue B: PC lanes (Hermes).**
- The lane runs on the PC beside the GPU, so no bridge is needed. Sources:
  - Hermes' session store (`state.db` per cloned lane profile; CLAUDE.md).
  - The lane directory: `report-draft.md`, `usage.json`, `FAILED` (`harness-ports/bin/pc-lane.sh:135-140,324,470-542`,
    1a94bbb 2026-09-23).
  - Hermes shell hooks, which get JSON on stdin (`harness-ports/hermes/config-snippet.yaml:103`), with timeouts:
    `on_session_start` 300 s (`:131`), `pre_llm_call` 30 s (`:139`), `post_tool_call` 60 s and 20 s (`:157`, `:164`).
- Hermes discards `post_tool_call` output. The spool reaches the model at the next `pre_llm_call`, one turn late
  (`:143-153`). What the Hermes hook JSON carries (a session id, a transcript path) was NOT read.
- **The 3090.** The RWKV numbers were measured inside a GPU window that stops the vLLM `qwen` service and refuses to open
  while any lane is live (`scripts/gpu_window.sh:2-5,19-21`, aa1eb84 2026-09-24T22:21:13Z). `g0.json` records 23,606 of
  24,122 MiB free at the run. Peak memory in the ladder was 1,260 MiB for a 2,048-token forward and 10,474 MiB at
  61,440 tokens. A live reader beside running local-route lanes would share the GPU with vLLM (CLAUDE.md: a KV cache of
  222,822 tokens). That co-residency is NOT measured.

**Venue C: the factory runtime (planned).**
- Hermes `pre_tool_call` is the fail-closed policy seam (standing rule 9). It offers block, modify or approve, and no
  advisory channel (`config-snippet.yaml:184`). KC-J1 keeps any Jev value out of it (MOJEV §5).
- An advisory reader fits the observer path: `post_tool_call`, then the spool into `pre_llm_call`, one turn late.
- The dream triage (D-058) reads an exported snapshot in a batch (`docs/11_DREAM_PHASE.md:99-122`); it has no live path.

### 3.5 What one state update and one question cost

| Item | Value | Method or source | S/U |
|---|---|---|---|
| Stream, main session | 59,514,467 characters in 48,203 events | p2 over the frozen manifest; each event capped at 32,768 characters as in D-3 (A-10) | SOLID |
| Stream, all transcripts | 165,496,796 characters in 114,407 events (subagent 96,802,138 / 60,636; workflow 9,180,191 / 5,568) | same | SOLID |
| Characters per token, Laya's tokenizer (ModernBERT vocabulary, 50,368) | 2.962 overall; tool call 2.858; tool result 2.967; text 3.616; thinking 3.933 | p3: every 20th main-session event (2,350 events), scrubbed, capped (A-12) | SOLID for Laya. The RWKV World tokenizer is not in the sandbox; its ratio is NOT measured |
| Tokens per event (Laya) | median 143, p90 940 | same | SOLID |
| Main stream in Laya tokens | about 20.1 million | 59,514,467 / 2.962 | UNSURE (a sampled ratio) |
| All streams in Laya tokens | about 55.9 million | 165,496,796 / 2.962 | UNSURE |
| Main stream per compaction interval | about 468,600 characters, about 158,000 Laya tokens (127 intervals) | arithmetic | UNSURE |
| For contrast: the API context | at compaction, median `preTokens` 785,712 (126 main-session compactions; p10 147,894; p90 795,051); per request, median 459,258 (main), 237,766 (subagents), 177,146 (workflow) | p1: `compactMetadata.preTokens`; `message.usage` input + cache read + cache creation per distinct request (A-6) | SOLID |
| RWKV forward throughput | 61,440 tokens in 1.174 s (about 52,300 tokens/s); 32,768 in 0.64 s | the README ladder, `g0.json` (3090, vLLM stopped) | UNSURE (not re-run) |
| RWKV question from a saved state | 0.0456 s (median of 5, 61,440-token state); 0.0372 s (16,384-token state) | `g0.json` `state_reuse` | UNSURE |
| One RWKV state update per event | compute about 0.003 s for 143 tokens (p90 940 tokens, about 0.018 s); a small forward's fixed cost is not measured; the nearest measured small call is the 15-token question, 0.046 s | arithmetic from the two rows above | UNSURE |
| One active hour of main stream (RWKV) | median 166,573 characters, about 56,000 Laya tokens, about 1.1 s of forward; 129 events | arithmetic | UNSURE |
| Cold replay | main stream about 6.4 min; all streams about 18 min | 20.1M and 55.9M tokens at 52,300 tokens/s; assumes chunked forwards keep that rate | UNSURE |
| Laya question on the sandbox CPU (2 threads) | median 1.0 s (p10 0.47, p90 3.0) per question inside rank calls; one `ask` 0.38 s; one `classify` 0.43 s | `.jev/calls.jsonl`, 245 lines, 2026-09-24 12:48Z-16:48Z; contention not recorded (A-5) | SOLID (the log's own numbers) |
| Laya window | `max_len` 1,024, `head_max_len` 256 (`rl_agent_config.json`); encoder `max_position_embeddings` 8,192. The brief and MOJEV say 512 | the snapshot's config (A-15); `scripts/laya_systemone_server.py` sets no length | SOLID (config); which length the library enforces is UNSURE |
| Sandbox-to-PC round trip | 0.62 s (health) and 1.64 s (rank) | `.jev/calls.jsonl`, venue pc, n = 2 | SOLID (n = 2) |

### 3.6 Which seams rule out a PC round trip

- **Explicit timeouts.** Only the cbm hooks set one: 5 s (H7-H10). One measured round trip (0.62-1.64 s) fits in 5 s.
  `scripts/pc.sh` retries a non-JSON reply up to 3 times under `curl -m 120` (CLAUDE.md), so its worst case does not fit.
- **Defaults.** 15 s (PreToolUse, PostToolUse), 30 s (UserPromptSubmit) and 120 s (Stop, SubagentStop) by the binary's
  table, or 600 s by its local path (UNSURE which). No default is shorter than one measured round trip.
- **Added latency is the binding cost.** PreToolUse runs before every Bash and Grep call (34,486 Bash calls in the
  records). A synchronous round trip adds 0.6-1.6 s to each, against a 1.0 s median gap between the main session's
  consecutive records.
- **On the PC.** A reader for Hermes lanes sits next to the GPU, so no bridge is needed; `pre_llm_call` allows 30 s.
- **The lane poller** checks every 15 s (`scripts/pc_lane.sh:143`). A 0.046 s question plus one round trip fits in each
  poll.

## 4. What SESSION-EXPORT must keep (evidence demand 4)

Checked against the SESSION-EXPORT brief's D-1 schema (e6bab18 2026-09-25T02:39:31Z):
- Fields: `seq, src, line, ts, role, kind, tool, call_id, text, truncated, outcome`.
- Kinds: `text`, `thinking`, `tool_call`, `tool_result`, `hook`, `notification`, `summary`.
- `outcome`, on tool results only: `is_error`, the leading `Exit code N`, `timed_out_after_ms`, `denial_kind`; on
  stop-hook summaries: `hook_errors`.
- Plus D-2 (scrub and the secret-path denylist) and D-3 (a cap of 32,768 characters: the first 24,576 and the last
  8,192).

The lane's in-progress report (`tasks/briefs/jev-laya/SESSION-EXPORT-report.md`, untracked at 03:1xZ) states an
attachment rule by type but did not yet list the types kept (UNSURE).

| Point | Events and fields it needs, in stream order | Where a training window ends | In D-1? | Gap or risk (measured) |
|---|---|---|---|---|
| D01 Bash exit | Bash `tool_call` (command, description, `run_in_background`, `timeout`); every earlier call and result with `outcome.is_error`, `exit_code`, `timed_out_after_ms`; earlier Edit/Write calls naming the script | at the Bash `tool_call`, before its result | yes | harness blocks carry no exit code: their class is in `text` (the error line) |
| D04 Edit apply, D05 needs a Read | Read `tool_call` (`file_path`, `offset`, `limit`) and its result text; Write content; Edit `old_string`, `new_string`, `replace_all`; the error text; the harness's `edited_text_file` attachments (`filename`, `snippet`); the compaction position; the harness's `bashEditDiff` | at the Edit or Write `tool_call` | partly | G1: `edited_text_file` (461 events) is not one of D-1's kinds, yet it is the visible cause for 4 of 5 "modified" and 10 of 24 "not read". G5: `toolUseResult.bashEditDiff` (1,722 results) is not an outcome field D-1 names. G3: the cap cuts 169 Read results and 48 Write inputs. The compaction boundary has no kind of its own (only the summary text follows it). D-2 empties secret-path Reads and Writes by design |
| D08 test outcome | Bash `tool_call` (command, description) and its result text up to the final pytest summary line; earlier runs of the same command; writes between runs | at the `tool_call` | yes | D-3's tail keeps the summary: 0 of 3,177 test outputs with a summary exceed the cap (A-12). `outcome.exit_code` is not the label: 887 of 938 red runs exit 0 |
| D18 commit gates | the commit `tool_call` (message, paths) and its result text (`COMMIT BLOCKED`, `[branch sha]`); the call's `ts`; Edit/Write calls since the last commit, with their text | at the commit `tool_call` | yes | the future-stamp cause needs `ts` (kept). Messages and texts passed as `@file` values are outside the transcript |
| D13 Stop | the stop-hook summary as a `hook` event with `outcome.hook_errors`; the "Stop hook feedback" text; commit and push calls and results; agent, background and Monitor notifications; `bashEditDiff` | at the turn's last assistant event, before the stop summary | mostly | G5 as above. The summary's `cwd`, `hookInfos` and `stopReason` are not kept; `cwd` does not decide (85 blocks carry `/home/user`) |
| D19 push, D20 CI gate | the push `tool_call` (flags, override variables) and its result text (`REFUSED`/`WAIT` lines, `== pushing <sha> ==`); earlier CI gate outputs; commits and Bash writes since the last commit | at the push `tool_call` | yes | see G6 for the sha |
| D21 CI conclusion | the push result's `== pushing <sha> ==`; `mcp__github__actions_list` results (`head_sha`, `conclusion`, `created_at`, `name`) | at the push result; the label arrives later in the same stream | yes | G6: `scrub` (HEAD and the working-tree version) replaces a 40-hex sha in both the push line and the Actions JSON (A-17, FAKE strings). The join key is lost in the export. Short shas, agent ids and tool-use ids survive. One Actions result exceeds the cap |
| D22 background | the background Bash `tool_call` (its `call_id`); its result text (the task id); the `<task-notification>` (`<tool-use-id>` = that `call_id`, `<status>`, `<summary>` with the exit code) | at the `tool_call` | yes | G4: a notification appears both as user text and as a `queued_command` attachment (DATA-SESSION). Keep one per (task id, status), or the labels double |
| D23 agent outcome | the Agent `tool_call` (`subagent_type`, `model`, description, prompt); its result text, which carries the agent id (258 of 258, A-12); completion notifications; the subagent stream (`src` = `subagents/agent-<id>.jsonl`) | at the Agent `tool_call` | mostly | G2: the assistant records' `message.model`, `stop_reason` and API-error flags (`isApiErrorMessage`, `apiErrorStatus`, `error`) have no D-1 field. The failure cause (13 of 13), the refusal stops (27) and the served-model switch (3 of 4 after a refusal) need them. Whether the API-error record also carries its message as a text block is UNSURE |
| D27 verify recommendation | the verifier's stream: its tool calls (report Writes and Edits), test runs and final text; the parent's dispatch (`subagent_type`) | before the verifier's first write of the recommendation word, else at its last tool result | yes | leak: the word is written into a file before the final message in 18 of 93 verifiers. Plain-text thinking exists in 4,727 of 33,371 thinking blocks; the rest are signature-only (the SESSION-EXPORT report counts 4,724 of 33,375) |

Cross-cutting, measured:
- **Position.** Every tool result follows its call. A window must end at the call, or the answer is inside the state
  (all ten points).
- **Role.** Owner text must be told apart from harness-injected user text: notifications, Stop feedback, reminders and
  compaction summaries. D15 and D16 labels depend on it. D-1 leaves the rule to the exporter.
- **Stream size after the cap** (p2's approximation of D-1): 165,496,796 characters in 114,407 events. 357 events would
  be capped (tool results 188, tool calls 89, text 39, notifications 40, summary 1; A-10).

## 5. NOT-done (evidence demand 5)

1. **The PC side was not read** (no bridge, by the brief). Not read: Hermes' `state.db`, the PC lanes' transcripts, the
   fields Hermes passes to a shell hook, and whether the lane profiles carry the hook snippet. So D33 and D35 have no
   labels here, and D24 and D25 lack the join from heartbeat lane names to `pc_lane` ids and terminal kinds.
2. **RWKV tokens and costs.** The RWKV World tokenizer is not in the sandbox, so every token count is a Laya-tokenizer
   count. RWKV speeds are the README's (not re-run; the sandbox has no GPU). Not measured: RWKV's CPU speed, the fixed
   cost of a small forward, and co-residency with vLLM on the 3090.
3. **The default hook timeout.** The binary holds a 15/30/120 s table and a 600 s local default. Which one governs this
   session was not probed: a live probe would need a sleeping hook and a settings change, outside a read-only lane.
4. **Live paths were read, not exercised.** Tailing `transcript_path` from a hook, an `http` hook, and a plugin's
   `$.session.messages()` are known from code and type declarations only.
5. **Rows reused, not re-measured:** D06, D10, D14, D16, D24, D26, D28, D29, D31, D32 (DATA-SESSION or INTERNAL-LABELS
   counts).
6. **D21 coverage.** Only 43 of 434 pushes joined a stage0-ci run; the 91 listing calls cover part of the history (no
   network).
7. **D03.** The denial rate among allowed calls was not measured, so "an earlier denial" (38 of 51) has no base rate.
   Whether PreToolUse runs before the auto-mode classifier was not determined.
8. **D04 view.** The visible-file reconstruction ignores Bash edits and other agents' writes (hence 137 false "anchor
   absent" among applied Edits) and does not stitch partial Reads. The harness's read-state rule behind 13 "not read"
   errors that follow a read is unknown.
9. **D13.** The git state the hook reads is not in the records. Writers outside the main stream (subagents in the shared
   tree, lanes, background hooks such as the post-commit reindex) were not attributed per Stop. The meaning of
   `bashEditDiff.shared` (491 rows) was not resolved.
10. **D27.** The 12 workflow verify verdicts were not included. Signature-only thinking limits the BLOCKER count to a
    floor.
11. **The agent output files** under the session's `tasks/` directory were not read by this lane (DATA-SESSION counted
    them).
12. **Laya's enforced window.** The config says 1,024 and the brief says 512; the library's runtime limit was not
    measured.
13. **D15's label** counts accesses to wiki, registry and skill files. Whether the file opened was the section the prompt
    needed was not measured.
14. **No predictor was trained or scored.** Section 2 gives feature counts per answer class only; no precision, recall
    or baseline comparison was computed.
15. **R20 (refusal).** The earlier-refusal feature was not computed.

## Appendix A. Commands

`$J` = `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/jev-map`. Every transcript probe reads
the frozen manifest (A-7) and prints counts, names and numbers only.

| Id | Command (abridged where long; the scripts hold the full text) | Output |
|---|---|---|
| A-1 | inline `python3` printing only the `hooks` key of `/home/user/agent-factory/.claude/settings.json`, `/home/user/.claude/settings.json`, `/root/.claude/settings.json`, `/root/.claude/launcher-settings.json` and every `/root/.claude/plugins/**/hooks.json`; `claude --version` | table 3.1; `2.1.280` |
| A-2 | Read of `.../fast-jev-output/0.1.0/hooks/fast-jev-output.ts` lines 1-300; `grep -rn "on(\"\|register(\|timeoutMs\|threshold\|minTokens" hooks/ src/` | H13; D11 |
| A-3 | `grep -n "hook_event_name: '" types/claude-code.d.ts` (33 names); `sed -n 540,575p types/claude-code.d.ts` | 3.2 |
| A-4 | `grep -a -o -E 'fTn=\{[^}]{0,900}\}' /opt/claude-code/bin/claude`; `grep -a -o -E '[,;{ ](Ia)=[0-9][0-9e*]{0,10}[,;]' ...`; `grep -a -o -E '(function nKr\(\|nKr=\(\|nKr=function)[^}]{0,300}' ...`; `grep -a -o -E '.{0,120}\.timeout\*(1e3\|1000)[^;]{0,90}' ...`; `grep -a -o -E '.{0,120}(Timeout in seconds\|timeout in seconds)[^"]{0,160}' ...` | 3.2 (timeouts, hook kinds) |
| A-5 | `ps -eo pid,etime,pcpu,rss,args \| grep -E '[l]aya_systemone\|[s]erver.*4741'`; inline `python3` over `.jev/calls.jsonl` (field names, latency per command, ms per question in `rank`, the `pc` rows) | 3.3, 3.5 |
| A-6 | `PYTHONDONTWRITEBYTECODE=1 python3 $J/p1_compact.py` | `$J/p1_compact.json` |
| A-7 | inline `python3`: `os.stat` of every `*.jsonl` under `/root/.claude/projects/-home-user`; own transcript found by its brief line | `$J/manifest.json` (2026-09-25T02:51:02Z) |
| A-8 | inline `python3` collecting repo paths of Read/Edit/Write; `GIT_OPTIONAL_LOCKS=0 git check-ignore --stdin` | `$J/repo_paths.txt`, `$J/ignored.txt` (1 of 820) |
| A-9 | `PYTHONDONTWRITEBYTECODE=1 python3 $J/p0_events.py $J/manifest.json` | 467 distinct Monitor events; line heads |
| A-10 | `PYTHONDONTWRITEBYTECODE=1 python3 $J/p2_stream.py $J/manifest.json` (runs 9 and 10; about 30 s each) | `$J/p2_summary.json` (sha256 prefix `72cafe748da3c970`), `$J/rows/*.jsonl` (digest `ad9adc3387d4903d`) |
| A-11 | `python3 $J/p4_analyze.py` | `$J/p4_analysis.json` |
| A-12 | `/root/venv-laya-probe/bin/python $J/p3_tokens.py $J/manifest.json` | `$J/p3_tokens.json` |
| A-13 | `git log -S"<marker>" --format='%h %cI' --reverse -- <file> \| head -1` for 14 (file, marker) pairs: future-stamp (in `pre-commit` and in `commit-msg`), never-a-gate, lane-skills, skills sync, lint_delta, vendored root, ci_gate.py, stale_ids.py, PUSH BLOCKED, lanes-live, turn-retro-gate, search-intercept, _premise_block_ok | section 2.4, 2.5, 2.6 windows |
| A-14 | inline `python3`: the Stop `cwd` tally over the main session; the commit command shapes; the not-read cross-tab and the Stop transitions over `$J/rows` | 2.2, 2.5 |
| A-15 | reads of the Laya snapshot's `typed-decisions/rl_agent_config.json`, `encoder/config.json`, `tokenizer/tokenizer_config.json`; `grep -n "max_len\|512\|1024\|window\|truncat\|MAX_" scripts/laya_systemone_server.py` | 3.5 (window) |
| A-16 | `PYTHONDONTWRITEBYTECODE=1 python3 $J/p5_bashdiff.py $J/manifest.json` | the `bashEditDiff` shape (2.5) |
| A-17 | inline `python3` loading HEAD's and the working tree's `scripts/transcript_export.py` and calling `scrub` on FAKE strings (a made-up 40-hex sha, a 17-hex agent id, a tool-use id) | G6 in section 4 |
| A-18 | `ls /dev/nvidia*`; `nproc`; `g0.json` env and ladder rows; `sed -n 1,40p scripts/gpu_window.sh \| grep -n -i -E "vllm\|stop\|window"` | 3.4 (venues) |
| A-19 | `PYTHONDONTWRITEBYTECODE=1 python3 $J/p6_after_compact.py $J/manifest.json` | D17 ledger, live-state and task-tool counts |

