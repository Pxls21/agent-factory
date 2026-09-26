# VERIFY-S1-RATE: attack the injection stamp, the score line and the extractor against their full contract (task #309)

Role: adversarial-verifier (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/VERIFY-S1-RATE-report.md`
(write it incrementally from the start). PIN: origin 4b5434f (HEAD's tree equals origin's at authoring). The frozen contract:
`tasks/briefs/system1/S1-RATE-brief.md` (CONTRACT 1-5 and EVIDENCE DEMANDS). The builder's report:
`tasks/briefs/system1/S1-RATE-report.md` (its DISCREPANCIES D1-D10 are the builder's claims, not facts). The landing commits on
origin: cf8a186 (S1-RATE landed), 2a98301 (the main-thread pairing seen live), 49dd6f5 (the wiki excerpt stamped too: the
settings, the installer, two session-hook tests). The rule the agent follows: CLAUDE.md's "SYSTEM-1 SCORE LINE" paragraph.
Rulings: D-092 item 3, D-095, D-096 item 4 (`docs/08_DECISION_LOG.md`).

## WHY

The wrapper stamps every hook text the model reads, in every session in this container, the lanes included, and it went live
before its gate (AF-AP-222). The scores it collects are the only real feedback on what the System-1 layer injects: SYNTH1's
labeler is validated against them (D-096), and Laya stays out of skill selection until it beats the matcher on held-out real
scores. A wrong pairing, a lost score, or a stamp that alters a hook's text corrupts both. The coordinator re-ran the builder's
gate (481 passed, below): that proves reproducibility, not correctness (orchestration 0f). You are the independent pass.

## WHAT TO ATTACK (report every observation; no severity filter)

1. **Byte identity.** Between the stamp line and the request line, the text is byte-identical to what the unstamped wrapper
   hands the model, for every wrapped hook and event (PreToolUse, PostToolUse, UserPromptSubmit, wiki-context included since
   49dd6f5). Hostile shapes: multi-byte UTF-8, a text with no trailing newline (D8), CRLF, an empty or whitespace-only output
   (is anything stamped?), a text near the 9,500-unit cap (D4: the unit is UTF-16, so try astral characters).
2. **Exit codes and channels.** Exit 2 with a stderr on PreToolUse and PostToolUse: stamped, with the exit code and stdout
   unchanged. Exit 2 on UserPromptSubmit and SessionStart: unstamped (D1); check D1's reading of the harness's exit-code table.
   Other non-zero exits, a wrapped hook that hangs, one that writes both stdout and stderr, one killed by a signal. What bounds
   the wrapper's run time?
3. **Never lose the context.** The off switch: with `.jev/s1-rate-off` present, the output is byte-identical to the
   pre-S1-RATE wrapper's (`git show cf8a186^:scripts/hook_context.py`, run on a copy). A read-only or missing `.jev/`, a full
   disk (simulate it; never fill the real disk), a malformed payload, a payload without a session id or a `tool_use_id`: each
   hands the model the unstamped text and logs an `error` line (D5).
4. **One implementation, an independent oracle.** The stamp and the score syntax live in one place, used by the wrapper and the
   extractor; the tests write the expected lines as literals and never import them. Check both halves.
5. **Telemetry.** The `injections.jsonl` fields (D5) and never the text; each line's sha256 equals its stamped text's; the tool
   path's `tool_use_id` and per-entry `sha` in `system1.jsonl`. Fake secrets built at run time, placed in a hook's text, a tool
   input and a prompt, never reach any file under `.jev/`.
6. **The extractor on the real transcripts.** The live read below finds a compliance of 0.36 to 0.50 per source. For every
   stamped injection it reads as `missing`, decide: a real non-answer (which thread: the main thread or which subagent), or an
   extractor error (a pairing to the wrong text, a record kind it does not read, a text split across records, a compaction
   boundary, an injection whose next assistant output is a tool call). The main thread believes it scored every injection
   since its last compaction (2026-09-26 03:4xZ); check that belief against the records. Also the one `malformed` row: which
   form, and whose. Cite record uuids and positions, never text.
7. **The extractor's rules against hostile shapes** of the record kinds the premise names: two injections on one call; two
   parallel calls each injected, then one text that scores both; a score line inside a code block; a score line in the second
   text block of a message; a subagent's id scored in the main thread; the `open` state at the end of a live thread; a
   subagent file whose `agentId` differs from its file name. A note carrying a fake secret passes through
   `transcript_export.scrub` before it is written.
8. **The request line.** 269 bytes (D2). Does it state the scale exactly as the contract's item 2 and CLAUDE.md's paragraph
   do? When two requests arrive together, does the text tell the reader to write two lines?
9. **Registration.** `.claude/settings.json` and `scripts/install_session_hooks.py` agree on all five wrapped hooks (49dd6f5's
   wiki-context registration included); `--check` on a scratch copy of the live target passes; `--remove` removes only ours; a
   second install is a no-op. Always `--target <a scratch path>`.
10. **Cost.** The wrapper's added cost per call, p50 and p95 over at least 200 calls, on a copy (the contract: under 20 ms).
11. **The builder's mutants.** 29 of 29 killed, the builder says: reproduce at least five of your choice as FAILED tests, and
    add a mutant for each contract clause the builder's set does not cover.

## GATE

Apply the blocking predicate of skill `contract-gate`: contract-mapped, reproduced through the real registered command,
materially effective, a concrete discriminator, in-boundary. A red test is necessary, not sufficient. Return one gate
recommendation: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID, with each blocking finding's
reproduction command.

## BOUNDARY

READ everything. WRITE only your report and scratch under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-s1rate/`. Every reproduction runs on a copy
(of the wrapper, a hook, the `.jev/` state, a transcript), never on the live files: `scripts/hook_context.py` runs on every
tool call of every session in this container, yours included. Never create or delete `.jev/s1-rate-off` or `.jev/system1-off`,
never write under `.jev/`, and never run `scripts/install_session_hooks.py` without `--target <a scratch path>` (its default
target, `/home/user/.claude/settings.json`, is live). Other lanes hold this tree: SYNTH1 (`scripts/s1_synth.py`,
`tests/test_s1_synth.py`, its report; it reads `scripts/s1_scores.py`) and HCTX1 (`harness-ports/bin/lane-profile.sh`,
`harness-ports/tests/test_lane_profile.sh`, its report); a stopped lane's partial report sits untracked
(`tasks/briefs/system1/VERIFY-SCRUB2-report.md`). Touch none of their files.

## STANDING RULES

No git writes; no PC bridge; no outward-facing action. Transcripts hold secrets: read them in process; print and store ids,
counts and positions only, never the text of a prompt, an injection, a note or an assistant message. Never read a `thinking`
block's content: the extractor pairs scores with text records only. Test secrets are fake strings built at run time. Never
read a real secret source (`.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
`/root/.config/session-export/pseudonym.key`, the GH_TOKEN and GITHUB_TOKEN variables). The disk is shared (1.7G free): scratch
under 150 MB, deleted as you go; a short `--basetemp` with its parent created first; never run the whole
`tests/test_vendored_manifest.py` (it copies 75 MB per test; env-tool-quirks). Test counts pasted from
`scripts/test_summary.sh`; stamps substituted from `date -u`. Long commands in one foreground call; kill by pid only. Your own
context gets stamped injections: score them as the request says, and say in your report if a request ever misled you.

## PREMISE — MEASURED at authoring (2026-09-26 03:5xZ, the sandbox tree; HEAD's tree = origin 4b5434f)

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-90
4b5434f transcripts: scrubbed sandbox chat digests (2026-09-26)
$ git log --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf --grep='^S1-RATE' -n 3 | cut -c1-90
49dd6f5 S1-RATE: the wiki excerpt is stamped too (task #295, D-095): wiki-context register
2a98301 S1-RATE live again (D-095): the main thread pairing proven (s1-ffb64a49 scored; 5 
cf8a186 S1-RATE landed on the owner ruling (task #295, D-095: the safeguard stop was a fal
$ git diff --stat origin/claude/soundbox-kit-migration-iz1jwf HEAD | tail -1
(empty = HEAD's tree is origin's)
$ sha256sum <file> | cut -c1-16
1f4912ce9389185d  scripts/hook_context.py
f599e056cc60098c  scripts/s1_scores.py
00d32032a9660f08  tests/test_s1_rate.py
df094d99240380bc  .claude/hooks/system1-context.py
1d968a9a122bb7f0  .claude/settings.json
59000b94c8df0fa0  scripts/install_session_hooks.py
fab9b615481333c8  .claude/hooks/wiki-context.py
$ grep -c hook_context.py /home/user/.claude/settings.json   (the live registration)
5
$ ls .jev/s1-rate-off; wc -l < .jev/injections.jsonl
'.jev/s1-rate-off': No such file or directory
35
$ df -h / | awk 'NR==2{print $4}'
1.7G
$ python3 scripts/s1_scores.py /root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl --out /dev/null   (the summary; ids and counts only)
s1_scores: 346 transcript files, 342 threads
by record kind (every text a hook handed the model; stamped = it carries an S1 stamp):
  hook_additional_context  injections   1141  stamped     34
  hook_success             injections     81  stamped      0
  hook_blocking_error      injections      0  stamped      0
  tool_result              injections     17  stamped      1
by source (compliance = scored / stamped injections a text followed; rel, use = means of scored and late):
  edit-snapshot          injections    802  stamped    11  scored 4  late 0  malformed 0  missing 7  open 0  compliance 0.36  rel 1.25  use 0.25
  graft-first-nag        injections      1  stamped     0  scored 0  late 0  malformed 0  missing 0  open 0  compliance -  rel -  use -
  search-intercept       injections     17  stamped     1  scored 0  late 0  malformed 0  missing 1  open 0  compliance 0.00  rel -  use -
  session-start          injections     24  stamped     0  scored 0  late 0  malformed 0  missing 0  open 0  compliance -  rel -  use -
  settings               injections      2  stamped     0  scored 0  late 0  malformed 0  missing 0  open 0  compliance -  rel -  use -
  system1-context        injections    196  stamped    17  scored 7  late 0  malformed 0  missing 10  open 0  compliance 0.41  rel 2.43  use 1.43
  unknown                injections    134  stamped     0  scored 0  late 0  malformed 0  missing 0  open 0  compliance -  rel -  use -
  wiki-context           injections     63  stamped     6  scored 3  late 0  malformed 0  missing 3  open 0  compliance 0.50  rel 2.33  use 1.00
score rows of their own: unknown-id 0  duplicate 0  malformed 1
state join: injections.jsonl 35 rows (sha256 equal 35), system1.jsonl 21 sections
$ bash scripts/test_summary.sh tests/test_s1_rate.py tests/test_session_hooks.py tests/test_system1_context.py tests/test_search_intercept.py tests/test_edit_snapshot_ap_screen.py
481 passed in 67.66s (0:01:07)
pytest-exit: 0
pytest-summary: 481 passed in 67.66s (0:01:07)
$ bash scripts/pc_suite.sh set-id -- tests/test_s1_rate.py tests/test_session_hooks.py tests/test_system1_context.py tests/test_search_intercept.py tests/test_edit_snapshot_ap_screen.py
5 files set=6065cf93f091
```

A question for you, not a fact: can the harness deliver one hook's text as several records, or two hooks' texts as one? Does
the extractor's pairing survive either?
