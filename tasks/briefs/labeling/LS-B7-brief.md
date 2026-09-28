# LS-B7: the task list becomes a synced view of the ledger (task #339, D-102)

Authored 2026-09-28 14:2xZ by the coordinator. Lane: sandbox `code-implementer` (Opus 5.5).

## WHY

The owner (D-102): "make the task list a view of the ledger", and "can't you get Jev to keep it in sync, to update the DB
itself. So you don't have to worry about syncing anything." Today the coordinator mirrors every task change by hand into
the harness's task list and the ledger (1,207 task-tool calls in eight days, LS design §2). The harness keeps its task list
as one JSON file per task and reads the files fresh (the premise below proves it). So a script can write the task list
from the ledger, and a hook can run it every turn: one store, no hand sync.

## CONTRACT

1. **The extractor.** Read `todo/BUILD-TASKLIST.md` (read-only) and derive, for each ledger task id, its newest status
   event from the LIVE section's dated lines (`**<HEADLINE> — 2026-MM-DD HH:MxZ.** <body>`). Order the lines by their
   date and time, never by position. The events come from a closed, committed grammar over the headline (and the
   body's `#NNN (backlog)` / `#NNN (…)` registrations): REGISTERED; DISPATCHED, RUNS, RUNNING, RESUMED, BRIEFED;
   HOME, LANDED, BUILT; CLOSED, DONE, SUPERSEDED, ACCEPTED; `(backlog)`. Map each to a view status: `in_progress`,
   `pending`, `backlog` (kept out of the view) or `closed` (removed). A mention the grammar cannot place is recorded as
   `unknown` with its line, never guessed. A small override table the coordinator may add to the ledger
   (`## 1b. Task overrides`, rows `| id | status | note |`) wins over the extractor.
2. **Titles.** Each view task gets `subject` `t<id>-<slug>` (a kebab slug of at most 40 characters from the registration
   text) and a `description` of at most 400 characters naming the newest line's date. Stable: the same ledger gives the
   same bytes.
3. **The sync.** `scripts/task_sync.py --ledger PATH --tasks-dir DIR [--apply] [--quiet] [--allow-dir]` plans creates,
   updates and deletes for the `<digits>.json` files in DIR. Each file has exactly the harness's keys: `id` (the ledger
   id as a string), `subject`, `description`, `activeForm`, `status` (`pending` or `in_progress`), `blocks` `[]`,
   `blockedBy` `[]`. With `--apply` it writes under `flock DIR/.lock`, each file by write-then-rename, raises
   `.highwatermark` to at least the largest id, and first backs up DIR's JSON files to
   `<repo>/.jev/task-sync/backup-<UTC>.tar`. Without `--apply` it prints the plan and writes nothing.
4. **Fail closed, fail loud.** An unreadable ledger, a parse failure, or an empty view writes NOTHING and exits 3 with
   the reason. `--apply` refuses a DIR outside `/root/.claude/tasks/` unless `--allow-dir` (the tests use it). Every run
   appends one line to `<repo>/.jev/task-sync/sync.log` (UTC, counts, the plan's digest, or the error).
5. **Hooks.** Stop: `task_sync.py --apply --quiet` for the session's task dir (the Stop payload's `session_id`), always
   exit 0 (a sync error goes to the log). SessionStart: run the same sync, then print the view (at most 12 lines) and, if
   the newest log line is an error, that line. Register both in `.claude/settings.json` AND in
   `scripts/install_session_hooks.py` (the session loads `/home/user/.claude/settings.json`, which that script writes),
   with their tests.
6. **The first run migrates.** The live DIR today holds harness-numbered files (premise below). The first `--apply`
   replaces them with ledger-numbered files. Show it on a COPY of the live DIR: the plan, then the resulting view. The
   view must be the ledger ids {289, 295, 297, 315, 318, 321, 325, 334, 335, 339, 340}, or you name each difference and
   the ledger line behind it.

Not in this lane: CLAUDE.md, AGENTS.md and `.hermes.md` (the coordinator rewrites the task-tracking rules after your
verify), and the live DIR itself (the coordinator runs the first `--apply`).

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. The grammar table: every rule, with a real headline from the ledger and the event it yields.
3. `tests/test_task_sync.py`: temp dirs only. Cases: create, update, delete; idempotence (a second run plans nothing);
   the dry run writes nothing; an unreadable ledger, a parse failure and an empty view each write nothing (exit 3); a DIR
   outside the root refused; the lock held by another process (the run waits or refuses, never writes unlocked); the
   override table wins; `unknown` mentions never change a status; the harness keys exactly. Each with a named mutant
   that reds it as a FAILED test (AF-AP-223).
4. The migration on a copy of the live DIR (item 6), pasted.
5. The hook tests: the installer writes both hooks; the Stop hook exits 0 on a sync error.
6. `bash scripts/test_summary.sh` twice on your test files plus `tests/test_session_hooks.py`, with the set id;
   pyflakes rc 0; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0 for every file you write.
7. NOT-done and DISCREPANCIES.

## BOUNDARY

- CREATE: `scripts/task_sync.py`, `tests/test_task_sync.py`, your report `tasks/briefs/labeling/LS-B7-report.md`.
- MODIFY: `.claude/settings.json` (the two hook registrations only), `scripts/install_session_hooks.py`,
  `tests/test_session_hooks.py`.
- READ everything else. NEVER write `/root/.claude/tasks/` (read it and copy it; the copy is yours).

## STANDING RULES

- No git writes, no PC bridge, no subagents, no outward-facing action.
- Never read a secret source (`.pc-bridge.env`, any `*.env`, `/root/.codiv/`, `~/.config/qwen-*`,
  `/root/.config/session-export/`).
- The main tree holds another lane's five files (listed in `.lanes-live`); touch only your boundary.
- The disk is shared (about 1.6 GB free): scratch under 100 MB in
  `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ls-b7/`.
- Long commands in one foreground call, each under 10 minutes. Kill by pid only. Stamps from `date -u`, never typed;
  counts pasted from `scripts/test_summary.sh`. Never use an unquoted heredoc for text with backticks.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- If the harness refuses your report-file write, return the whole report as your final message.

## PREMISE — MEASURED at authoring (2026-09-28 14:2xZ, the main tree at the #339 design commit plus D-102)

```
$ ls /root/.claude/tasks/bdab799a-dc80-5933-9c9e-c80f206f9a17/   (and the hidden files)
.highwatermark (contents: 314)  .lock (0 bytes)
289.json 295.json 297.json 308.json 310.json 313.json 315.json 316.json 317.json 318.json 319.json
$ for f in .../*.json: id status subject
289 in_progress t289-upstream-reports (D-091 items 2 and 4)
295 in_progress t295-s1-rate-injection-scores (D-092 item 3)
297 pending t297-l6-laya-ranks-skills (D-093, design L6)
308 pending t318-s1-rate-r1-recorded-scores (VERIFY-S1-RATE F1)
310 in_progress t321-scrub2-r1-repair (VERIFY-SCRUB2 F1, F7, F15)
313 pending t325-laya-probe-cuda-context (AF-AP-231)
315 in_progress t315-i59d-batch-landing (issue #59: re-mint, anchors, verify, re-sign)
316 in_progress t334-repo-eval-output-substrate
317 in_progress t335-i59f-proof-code-followups
318 pending t339-labeling-output-style
319 pending t340-read-narrowing-hook
$ keys of 319.json
id, subject, description, activeForm, status, blocks, blockedBy
$ the probe (2026-09-28 14:2xZ): append " [DISK-PROBE 1]" to 319.json's description under flock .lock; TaskGet 319
Description: ... (median 652). [DISK-PROBE 1]        (the harness read the file fresh)
$ restore from the backup under flock; grep -c DISK-PROBE 319.json
0
$ LIVE headline lines in todo/BUILD-TASKLIST.md (lines starting '**' with ' — 2026-09-' in the first 400 chars)
288
$ the newest six headlines
**TURN RETRO: AF-AP-234 REGISTERED; TASK #331 WIDENED; TASKS #336 AND #337 REGISTERED — 2026-09-28 13:0xZ.**
**TASK #338 REGISTERED (the CI gate read an older run twice) — 2026-09-28 13:1xZ.**
**THE ISSUE #59 BATCH IS ON ORIGIN (TASK #315); I59-F BRIEFED AND DISPATCHED (TASK #335) — 2026-09-28 13:2xZ.**
**D-101: THE OWNER'S RULINGS ON D-100; TASKS #339 AND #340 REGISTERED; SYNTH1 OPTION 1 RUNS; A CLASSIFIER REFUSAL LOGGED — 2026-09-28 13:3xZ.**
**SYNTH1 OPTION 1 FAILS; TASK #308 CLOSED (SUPERSEDED BY #339); AF-AP-235 REGISTERED; TASK #341 REGISTERED — 2026-09-28 14:0xZ.**
**#339: LS-AUDIT HOME, THE DESIGN WRITTEN, THE PREMORTEM DISPATCHED — 2026-09-28 14:1xZ.**
```

Two facts for you to handle, not to hide: the ledger's section 2 heading says "newest first", but lines are appended at
the end (order by stamp); and harness ids and ledger ids differ today (harness 318 is ledger task 339).
