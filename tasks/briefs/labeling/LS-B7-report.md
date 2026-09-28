# LS-B7 report: the task list as a synced view of the ledger (task #339, D-102)

Written 2026-09-28 16:3xZ by the sandbox code-implementer (Opus 5.5), in the main tree. Nothing committed (the brief:
no git writes). The off switch `/home/user/agent-factory/.jev/task-sync-off` is untouched and still in place.

## Verdict

- **DONE (tests and mutants green; not live):** `scripts/task_sync.py` (the extractor, the view, the plan, the apply,
  the log, both hooks), `tests/test_task_sync.py`, and the two registrations (`scripts/install_session_hooks.py`,
  `.claude/settings.json`) with their tests in `tests/test_session_hooks.py`.
- **Verified on a COPY of the live DIR:** the first Stop run migrates the 11 harness files into a 38-file view in
  0.190 s; the second Stop run plans nothing (0.125 s). No write reached `/root/.claude/tasks/` or the main tree's
  `.jev/` (measured below).
- **The view is the brief's 11 ids plus 27 more.** The ledger's headlines never close or backlog those 27 in the
  brief's grammar words. Each one is named in §4 with the line behind it. The fix is the override table; the rows
  are the coordinator's call.
- **Premise: holds.** No CONTRACT-INVALID. One drift that does not matter (318.json's status), and counts that grow.
- **Two discrepancies you need before the verify round:** (D1) `flock DIR/.lock` does not exclude the harness; the
  harness locks with proper-lockfile directories. (D2) Landing moves the vendored manifest's `.claude/ (kit-adapted)`
  row. See §7.

## 1. Premise, re-measured (evidence demand 1)

| Premise claim (14:2xZ) | Measured 2026-09-28 15:3xZ-16:1xZ | Matters? |
|---|---|---|
| DIR holds `.highwatermark` (314), `.lock` (0 bytes), 11 files 289…319 | Same 11 names, `.highwatermark` = `314`, `.lock` 0 bytes | - |
| per-file id/status/subject (11 rows) | Equal, except `318.json` is now `in_progress` (mtime 15:07; the coordinator's own update). `317.json` changed again at 15:56:46 (same source) | No: both are harness writes the migration replaces |
| keys of 319.json | `id, subject, description, activeForm, status, blocks, blockedBy`; bytes = `JSON.stringify(obj, null, 2)`, no trailing newline (`od -c`: ends `]\n}`) | - |
| the DISK-PROBE (the harness reads files fresh) | NOT re-run: it writes the live DIR, which the brief forbids. Supporting evidence (inferred): the harness code reads each `<id>.json` from disk on every list/get (`Uae`, `qko`, `rx` in `/opt/claude-code/bin/claude`) | Assumed from the coordinator's probe |
| 288 headline lines | 291 in the whole file and 277 inside `## 2.` when work started; 278 at 16:1xZ (line 1656 appended) | No: the ledger grows |
| newest six headlines | Present at lines 1647-1652; lines 1653-1656 appended after authoring | No |
| "section 2 says newest first, lines appended at the end" | True for the headline-first lines (1366-1656). Section 2 ALSO holds 88 older date-first blocks (lines 422-1365, 2026-09-03 to 2026-09-19); 14 headline-first lines sit in section 0 (lines 220-241, 2026-09-23 08:2xZ-13:0xZ) | Handled: both are counted and not read (§2) |
| "harness 318 is ledger task 339" | True (318.json subject `t339-labeling-output-style`) | Handled: the view is keyed by ledger id |

Harness facts read from its own code (verified by grep of `/opt/claude-code/bin/claude`; used by the design):
- A new task id is `max(highest <id>.json, .highwatermark) + 1`, taken under `ke()` = proper-lockfile on `DIR/.lock`
  (a `DIR/.lock.lock` DIRECTORY while held; retries 30, 5-100 ms). A claim locks `DIR/<id>.json.lock`; the plain
  update path (`Ue`) is a `writeFile` with no lock of its own (which path TaskUpdate takes: inferred, not traced).
  No `flock` anywhere.
- The task schema: `id, subject, description` strings, `activeForm` optional, `status` in
  `pending|in_progress|completed`, `blocks`/`blockedBy` string arrays.
- The list id is sanitized with `[^a-zA-Z0-9_-] -> -`; the DIR is `<config>/tasks/<list id>`; `<config>` is
  `$CLAUDE_CONFIG_DIR`, else `~/.claude`.
- No file watcher on the task DIR was found (inferred from grep; not proven). The harness's own writes emit
  `taskList.updated`; an external write does not.

## 2. The grammar (evidence demand 2)

Scope: only headline-first dated lines inside `## 2.` (`**<HEADLINE> — YYYY-MM-DD HH:MxZ<tail>**<body>`, the stamp =
the last dated em dash outside parentheses). Order: date, then ten-minute bucket; only two lines in one bucket fall
back to file order (the append order). The 88 date-first blocks and the 14 section-0 lines are counted, not read; the
newest date-first block is 2026-09-19, older than every placed event of the 27 extra ids, so reading them could not
close any of them.

Word -> status (the brief's list, exactly): REGISTERED -> pending; DISPATCHED, RUNS, RUNNING, RESUMED, BRIEFED, HOME,
LANDED, BUILT -> in_progress; CLOSED, DONE, SUPERSEDED, ACCEPTED -> closed; `(backlog)` -> backlog. Every row below is
a real headline, pinned verbatim as a test case (`test_the_grammar_on_real_ledger_headlines[<id>]`).

| Rule | Real headline (ledger line) | Event it yields |
|---|---|---|
| A list binds the first event after it | 1651 `SYNTH1 OPTION 1 FAILS; TASK #308 CLOSED (SUPERSEDED BY #339); ...; TASK #341 REGISTERED` | #308 CLOSED |
| `BY #N` names the successor, not a subject | 1651 (same) | #339 unknown |
| `#N (backlog...)` in the line registers backlog | 1651 body `#341 (backlog): those readers refuse, ...` | #341 backlog |
| ISSUE(S), RUN, PR before a list: not a task | 1420 `ISSUES #11 AND #17 CLOSED (completed)` | no task mention |
| RUN qualifier; tail with no event of its own follows the last clause | 1369 `CI RUN #988 PASSED; D-058 RECORDED (...) — ... (task #195 created, pending).` | #195 unknown |
| NOT/NO/NEVER before a word cancels it | 1620 `...; SCRUB2-R1 BRIEFED (TASK #321, NOT DISPATCHED)` | #321 BRIEFED; #318 (WIDENED) unknown |
| A possessive is a reference | 1448 `VERIFY-COORD-0924 HOME: ... (rule 0f; #214's hooks, AF-AP-181, D-071)` | #214 unknown (would have reopened #214, closed at 1442) |
| A parenthetical with its own event gives an id without one nothing | 1424 `J0-b HOME: ...; J0 DONE (task #123 closed; J1-4, task #121, unblocked)` | #123 CLOSED; #121 unknown |
| The stamp's tail inherits the last clause's event | 1439 `K170 DISPATCHED — ... (task #170 in progress).` | #170 DISPATCHED |
| ... only the LAST clause's | 1371 `THE SEVEN-LEG S0-02 CAPTURE CAME HOME; ...; B12 QUEUED (AF-AP-156) — ... (task #196 created, ...)` | #196 unknown (not HOME) |
| A range expands | 1607 `THE ISSUE #59 BATCH PLANNED; TASKS #312-#315 REGISTERED` | #312-#315 REGISTERED; issue #59 dropped |
| A list with no event after it takes the nearest unclaimed event before it | 1565 `CI RED ON C0D01E7 FIXED (RUN #1087; TASK #286); D-091 REGISTERED AS TASKS #287-#289` | #287-#289 REGISTERED; #286 unknown |
| A hyphenated compound is not a word | 1391 `C2 LANDED (task #148, the lane done-gate; GATED-PENDING-VERIFY, switched OFF)` | #148 LANDED (not DONE) |
| `RE-` prefix counts | 1552 `... RE-DISPATCHED AS CONTINUATIONS (TASKS #274, #275, #276)` | #274-#276 DISPATCHED |
| Lowercase tail words count | 1382 `VERIFY-S198A HOME: ... (task #203 closed; task #198 increment A done)` | #203 CLOSED; #198 DONE |
| HOME | 1652 `#339: LS-AUDIT HOME, THE DESIGN WRITTEN, THE PREMORTEM DISPATCHED` | #339 HOME |
| BRIEFED | 1653 `D-102: ... (LS-B7 BRIEFED, TASK #339); ...` | #339 BRIEFED |
| LANDED | 1598 `S1-RATE LANDED ON THE OWNER'S RULING (TASK #295, D-095: ...; GATED-PENDING-VERIFY)` | #295 LANDED |
| Backlog pair | 1647 `...; TASK #331 WIDENED; TASKS #336 AND #337 REGISTERED` + body `#336 (backlog)`, `#337 (backlog)` | #336, #337 backlog; #331 unknown |
| `TASK #N REGISTERED (backlog)` in the body | 1655 body `(4) TASK #343 REGISTERED (backlog): ...` | #343 backlog |
| A body `#N (…)` counts only for ids the headline registers | 1648 `TASK #338 REGISTERED (...)` + body `#295 (cee0c8a) inside a --wait loop` (a CI run) | #338 backlog; #295 untouched |
| A date-only stamp places nothing | 1463 `RETRO 14:4xZ — TASK #238 OPENED; ... — 2026-09-24.` | #238 unknown |
| A seconds stamp parses | 1502 `... — 2026-09-25 00:35:59Z.` | run #1050 dropped |
| Backticked text is not read | 1417 ``... IN A `/home/user`-ROOTED SESSION — ... (task #210 ...; task #214 NEW, ...)`` | #210, #214 unknown |
| Em dashes inside the headline | 1383 `T94 LANDED — GATED-PENDING-VERIFY (tasks #200 + #167) — with a ... — 2026-09-23 18:4xZ.` | #200, #167 LANDED |

RUNS, RUNNING, RESUMED, BUILT, SUPERSEDED and ACCEPTED appear in real headlines (1650 `SYNTH1 OPTION 1 RUNS`, 1488
`VERIFY-GW1-R1 RUNNING`, 1643 `THE TWO I59 VERIFIERS RESUMED`, 1655 `I59-F BUILT`, 1651, 1472 `JT1-R1 ACCEPTED (tasks
#224 and #235 CLOSED)`) but never beside a task id of their own on this ledger, so no real line pins their status.
`test_every_grammar_word_maps_to_its_status` (13 words, upper and lower case, spec-authored in the test) pins all 13;
the code-span and date-only rules are pinned by a built line too (no real headline exercises them).

Result on the ledger of 16:1xZ (278 dated lines): 38 in the view (24 in_progress, 14 pending), 20 backlog, 67 closed,
23 ids with no status (every mention unknown), 113 unknown mentions. Same-line conflicts (one line giving one id two
statuses): 0, measured by the scratch prototype on the 277-line snapshot; the final code keeps the last binding of a
line and does not count them.

## 3. `tests/test_task_sync.py` and its mutants (evidence demand 3)

Temp dirs only: every run uses a copy of the script in a temp repo (its log, backups and off switch there), with
`CLAUDE_CONFIG_DIR` and `HOME` at temp dirs. After all runs: the main tree has no `.jev/task-sync/`, and
`/root/.claude/tasks/` holds only the live session dir (measured, `ls`).

Driver (scratch, AF-AP-223's fix shape): the unmutated baseline runs first and must pass; a CONTROL mutant (a local
renamed) must stay green; a kill needs a FAILED target test whose reason is an AssertionError (a crash is
FAILED-OTHER, not a kill); an ERROR or a no-test run is INVALID; the denominator is a literal; each mutant runs in a
fresh copy tree with `PYTHONDONTWRITEBYTECODE=1`. Self-test: the same run with the last row dropped exits 1
(`EXPECTED=43 KILLED=42` at the first version, `EXPECTED=7 KILLED=6` for the installer table).

Brief case -> test -> mutant (pasted from the final run, 16:2xZ):

```
BASELINE (unmutated, 33 targets): rc=0 33 passed in 4.73s
CONTROL GREEN C00-control-renamed-local sha=eefe4dd8c4e4 :: 3 passed in 0.40s
EXPECTED=44 KILLED=44 SURVIVED=0 INVALID=0 FAILED-OTHER=0 CONTROL=green
```

| Mutant | Verdict | Test | Assertion (head) |
|---|---|---|---|
| M01-create-skipped | KILLED | `test_create_writes_one_file_per_view_task_in_the_harness_bytes` | AssertionError: assert [] == ['10.json', '11.json'] |
| M02-update-skipped | KILLED | `test_update_rewrites_a_stale_file_and_delete_removes_one_that_left_the_view` | AssertionError: assert ([10] == [10] |
| M03-delete-skipped | KILLED | `test_update_rewrites_a_stale_file_and_delete_removes_one_that_left_the_view` | assert ([7, 10] == [10] |
| M04-not-idempotent | KILLED | `test_a_second_run_plans_nothing` | assert ((0, '') == (0, '') |
| M05-dry-run-applies | KILLED | `test_the_dry_run_writes_nothing` | assert (0 == 0 and {'.highwaterm...} == {'7.json': ...} |
| M06-undecodable-ledger-escapes | KILLED | `test_an_unreadable_ledger_writes_nothing_and_exits_3[not-utf8]` | AssertionError: assert (1 == 3) |
| M07-malformed-time-skipped | KILLED | `test_a_parse_failure_writes_nothing_and_exits_3[malformed-time]` | AssertionError: |
| M08-empty-view-applied | KILLED | `test_an_empty_view_writes_nothing_and_exits_3` | assert (0 == 3) |
| M09-dir-check-off | KILLED | `test_apply_refuses_a_dir_outside_the_tasks_root` | AssertionError: (PosixPath('/tmp/...') |
| M10-no-flock | KILLED | `test_a_held_lock_is_waited_for_and_never_written_under` | assert (0 == 3) |
| M11-override-ignored | KILLED | `test_the_override_table_wins` | AssertionError: assert {10: 'pending', 12: 'pending'} == {11: 'in_prog...12: 'pending'} |
| M12-references-close | KILLED | `test_unknown_mentions_never_change_a_status` | AssertionError: task_sync: empty view: ... |
| M13-unknown-registers | KILLED | `test_unknown_mentions_never_change_a_status` | assert ('  #10 pending ' in "task_sync: dry run, ... |
| M14-no-activeForm-key | KILLED | `test_the_harness_keys_exactly` | AssertionError: assert (['id', 'subje..., 'blockedBy'] == ['id', 'subje...'blocks', ...] |
| M15-ordered-by-position | KILLED | `test_lines_are_ordered_by_stamp_not_position` | AssertionError: assert {10: 'in_progress'} == {10: 'closed'} |
| M16-no-qualifiers | KILLED | `test_the_grammar_on_real_ledger_headlines[1420-issues-qualifier]` | AssertionError: assert {11: 'CLOSED', 17: 'CLOSED'} == {} |
| M17-by-is-a-subject | KILLED | `...[1651-closed-and-by]` | AssertionError: assert {308: 'CLOSED...ED (backlog)'} == {308: 'CLOSED...E |
| M18-possessive-is-a-subject | KILLED | `...[1448-possessive]` | AssertionError: assert {214: 'HOME'} == {214: None} |
| M19-no-negation | KILLED | `...[1620-negation]` | AssertionError: assert {318: None, 321: 'DISPATCHED'} == {318: None, 321: 'BRIE |
| M20-status-paren-inherits | KILLED | `...[1424-status-paren]` | AssertionError: assert {123: 'CLOSED', 121: 'DONE'} == {123: 'CLOSED', 121: |
| M21-tail-follows-whole-head | KILLED | `...[1371-tail-last-clause]` | AssertionError: assert {196: 'HOME'} == {196: None} |
| M22-code-spans-read | KILLED | `test_backticks_and_a_date_only_stamp_place_nothing` | AssertionError: assert {5: 'DONE'} == {5: None} |
| M23-hyphen-compounds-count | KILLED | `...[1391-hyphen-compound]` | AssertionError: assert {148: 'DONE'} == {148: 'LANDED'} |
| M24-no-re-prefix | KILLED | `...[1552-re-prefix]` | AssertionError: assert {274: None, 2...ne, 276: None} == {274: 'DISPAT... |
| M25-no-ranges | KILLED | `...[1607-range]` | AssertionError: assert {312: 'REGIST... 'REGISTERED'} == {312: 'REGIST... |
| M26-no-binding-before | KILLED | `...[1565-event-before-list]` | AssertionError: assert {286: None, 2...ne, 289: None} == {286: None, 2 |
| M27-no-backlog | KILLED | `...[1647-backlog]` | AssertionError: assert {331: None, 3... 'REGISTERED'} == {331: None, 3...ED (bac |
| M28-date-only-placed | KILLED | `test_backticks_and_a_date_only_stamp_place_nothing` | AssertionError: assert {6: 'DISPATCHED'} == {6: None} |
| M29-hwm-lowered | KILLED | `test_the_highwatermark_is_raised_never_lowered` | AssertionError: assert ('40' == '40' |
| M30-no-backup | KILLED | `test_the_backup_holds_the_pre_state` | assert 0 == 1 |
| M31-every-error-shown | KILLED | `test_a_stop_error_is_shown_once_per_new_error_and_never_blocks` | assert ([1, 1, 1, 1] == [1, 0, 1, 1] |
| M32-stop-exits-2 | KILLED | `test_a_stop_error_is_shown_once_per_new_error_and_never_blocks` | assert ([2, 0, 2, 2] == [1, 0, 1, 1] |
| M33-stop-prints-stdout | KILLED | `test_the_stop_hook_writes_the_view_and_prints_nothing` | AssertionError: assert (0, 'dir=/tmp...b5613b\n', '') == (0, '', '') |
| M34-hooks-ignore-off | KILLED | `test_the_off_switch_makes_both_hooks_inert_and_refuses_apply` | AssertionError: ('stop', 's1') |
| M35-off-line-every-turn | KILLED | `test_the_off_switch_makes_both_hooks_inert_and_refuses_apply` | AssertionError: assert [['off', 'ses...'session=s2']] == [['off', 'ses...'s |
| M36-apply-ignores-off | KILLED | `test_the_off_switch_makes_both_hooks_inert_and_refuses_apply` | assert (0 == 3) |
| M37-view-unbounded | KILLED | `test_session_start_prints_the_view_in_at_most_12_lines_then_the_newest_error` | assert (0 == 0 and '' == '' and 16 == 12) |
| M38-no-error-line-at-start | KILLED | `test_session_start_prints_the_view_in_at_most_12_lines_then_the_newest_error` | AssertionError: assert (0 == 0 and False) |
| M39-slug-uncapped | KILLED | `test_the_harness_keys_exactly` | AssertionError: assert (84 - 4) <= 40 |
| M40-description-uncapped | KILLED | `test_the_harness_keys_exactly` | AssertionError: assert (1624 <= 400) |
| M41-session-id-unsanitized | KILLED | `test_the_stop_hook_writes_the_view_and_prints_nothing` | AssertionError: assert (1, '', 'task...new error)\n') == (0, '', '') |
| M42-quiet-ignored | KILLED | `test_a_second_run_plans_nothing` | assert ((0, 'task_syn...o status):\n') == (0, '') |
| M43-stamp-inside-paren | KILLED | `test_the_stamp_is_the_last_dated_dash_outside_parens` | AssertionError: assert {7: 'closed'} == {7: 'in_progress'} |
| M44-built-closes | KILLED | `test_every_grammar_word_maps_to_its_status[BUILT]` | AssertionError: assert {5: 'closed'} == {5: 'in_progress'} |

The brief's cases map: create M01; update M02; delete M03; idempotence M04, M42; dry run M05; unreadable ledger M06;
parse failure M07; empty view M08; DIR outside the root M09; the lock M10; the override table M11; unknown mentions
M12, M13; the harness keys M14, M39, M40. Red-green: the 33 target tests of the 44 mutants (and the 6 of the
installer table) ran red under their mutant and green on the baseline. Green only, with no mutant of their own:
`test_the_first_apply_migrates_harness_numbered_files`, `test_the_same_ledger_gives_the_same_bytes`,
`test_the_hook_state_paths_are_git_ignored` (it carries its own negative control), the wall-time test, the grammar
rows 1369, 1439, 1382, 1652, 1653, 1598, 1655, 1648, 1463, 1502, 1417, 1383, and 12 of the 13 word-map cases. The
lock test waits until the child holds `DIR/.lock` open (read from `/proc/<pid>/fd`, a structural signature), not for
a fixed delay.

Other tests in the file (not a brief case): the git-ignore check of `.jev/task-sync/*` and `.jev/task-sync-off`
through the repo's own `.gitignore` in a fresh `git init` repo (with a control: `scripts/task_sync.py` is not
ignored); the Stop hook's write scope (every changed file is under the task DIR or `.jev/task-sync/`); the same
ledger gives the same bytes; the backup holds the pre-state; the Stop wall time on the real ledger (bound 10 s).

## 4. The migration on a COPY of the live DIR (evidence demand 4)

Copy: `cp -a` of `/root/.claude/tasks/bdab799a-dc80-5933-9c9e-c80f206f9a17` at 16:18:16Z; ledger snapshot 1656 lines,
sha256 `df27d1e1aa6a`. The script ran from a scratch repo copy with `CLAUDE_CONFIG_DIR=<scratch>/cfg`, the copy at
`<scratch>/cfg/tasks/copy`, through the real hook entry (`--hook stop`, payload `{"session_id":"copy"}`).

The plan (the dry run; pasted, the path shortened to `<copy>`):

```
task_sync: dry run, nothing written
ledger todo/BUILD-TASKLIST.md: 278 dated lines placed (1 with no time); 88 older date-first lines and 14 dated lines outside '## 2.' not read
view: 38 tasks (24 in_progress, 14 pending); backlog 20, closed 67, overrides 0, ids with no status 23, unknown mentions 113
plan: dir=<copy> view=38 create=30 update=8 delete=3 hwm=314->344 digest=7c625d53cb41
  update 289.json t289-upstream-reports [pending]
  update 295.json t295-s1-rate-each-system-1-injection-carries [in_progress]
  update 297.json t297-laya-ranks-trained-on-295-s-scores-and [pending]
  update 310.json t310-hctx1-briefed-and-dispatched-d-097 [in_progress]
  update 313.json t313-i59-b-s0-05-f-6-wording-the-af-ap-169 [in_progress]
  update 315.json t315-i59-d-re-mint-all-twelve-on-the-pc-from [in_progress]
  update 318.json t318-s1-rate-r1-after-synth1-lands-since [pending]
  update 319.json t319-transcript-export-scrub-passes-a-fake [pending]
  create (30 files: 121 148 167 170 196 200 206 210 215 216 221 251 253 256 290 291 293 311 312 314 320 321 322 325 327 329 334 335 339 340)
  delete 308.json (was t318-s1-rate-r1-recorded-scores (VERIFY-S1-RATE F1))
  delete 316.json (was t334-repo-eval-output-substrate)
  delete 317.json (was t335-i59f-proof-code-followups)
  highwatermark 314 -> 344
```

The apply and the second run (the log, pasted):

```
Stop hook run 1: rc=0 wall=0.190 s stdout_bytes=0 stderr_bytes=0
Stop hook run 2: rc=0 wall=0.125 s stdout_bytes=0 stderr_bytes=0
2026-09-28T16:18:25Z ok apply stop dir=<copy> view=38 create=30 update=8 delete=3 hwm=314->344 digest=7c625d53cb41
2026-09-28T16:18:25Z ok apply stop dir=<copy> view=38 create=0 update=0 delete=0 hwm=344 digest=e3b0c44298fc
backups: backup-20260928T161825.700501Z.tar
```

The apply's digest equals the dry run's (the plan shown is the plan applied). The resulting view: 38 files (ids 121
148 167 170 196 200 206 210 215 216 221 251 253 256 289 290 291 293 295 297 310 311 312 313 314 315 318 319 320 321
322 325 327 329 334 335 339 340), `.highwatermark` 344, `.lock` kept.

**The brief's 11 ids: all present.** Status against the harness: 9 equal; #289 and #334 are `pending` from the ledger
(REGISTERED at 1565 and 1643; later mentions are WIDENED/ASSESSED, unknown) where the harness says `in_progress`.
Subjects change to generated slugs (e.g. harness `t340-read-narrowing-hook`, generated `t340-read-narrowing-hook-a-port-of`).

**The 27 other ids, each with the line behind its status** (newest placed event; "later" = the newest unknown mention
after it, when one exists):

| Id | Status (word) | Line | Why it is still open in the grammar |
|---|---|---|---|
| 121 | in_progress (LANDED) | 1426 `J1-4 LANDED, GATED-PENDING-VERIFY: ... (task #121)` | later 1436 `(... tasks #217, #122 closed; #121 confirmed)` |
| 148 | in_progress (LANDED) | 1391 `C2 LANDED (task #148, ...)` | never closed by id |
| 167 | in_progress (HOME) | 1388 `VERIFY-T94 HOME NOT-READY → T94-R1 (tasks #200 + #167)` | never closed by id |
| 170 | in_progress (DISPATCHED) | 1439 `K170 DISPATCHED — ... (task #170 in progress)` | 1461 `K170 AND MOJEV-G0-S LANDED` names no id |
| 196 | in_progress (DISPATCHED) | 1374 `B12 DISPATCHED (task #196 in progress)` | never closed by id |
| 200 | in_progress (HOME) | 1388 (as #167) | never closed by id |
| 206 | in_progress (LANDED) | 1400 `...; A2'' LANDED GATED-PENDING-VERIFY (task #206); ...` | never closed by id |
| 210 | in_progress (BRIEFED) | 1444 `... MOJEV GATE 0 STAGED ON THE PC AND BRIEFED (task #210)` | never closed by id |
| 215 | in_progress (DISPATCHED) | 1429 `... K215 (task #215) DISPATCHED; ...` | later 1437 `(task #219 closed; tasks #215 and #218 VERIFIED)` |
| 216 | in_progress (DISPATCHED) | 1429 `... VERIFY-J1-1-R3 (task #216) ...` | never closed by id |
| 221 | in_progress (DISPATCHED) | 1447 `JT1 DISPATCHED (task #224, #221 steps 1-2); ...` | never closed by id |
| 251 | in_progress (DISPATCHED) | 1509 `...; VERIFY-DSV2 DISPATCHED (TASK #251)` | later 1522 `DSV2 MERGE-READY-WITH-FOLLOWUPS (TASK #251)` |
| 253 | in_progress (LANDED) | 1511 `JEV-MAP LANDED (TASK #253): ...` | never closed by id |
| 256 | in_progress (LANDED) | 1517 `JEV-FIT LANDED: ... (TASK #256); ...` | never closed by id |
| 290 | pending (REGISTERED) | 1567 `RETRO OF THE CI FIX; TASK #290 REGISTERED` | registered before the `(backlog)` convention (1584) |
| 291 | pending (REGISTERED) | 1568 `...; TASKS #291-#293 REGISTERED; #274 CLOSED` | later 1585 `#291 AND #293 CONFIRMED` |
| 293 | pending (REGISTERED) | 1568 (as #291) | later 1585 (as #291) |
| 310 | in_progress (LANDED) | 1609 `HCTX1 LANDED AND CHECKED LIVE ON THE PC (TASK #310, ...)` | 1628 closes #316 and #317 (HCTX1-R1), not #310 |
| 311 | pending (REGISTERED) | 1605 `RETRO 03:4xZ: TASK #311 REGISTERED` | never mentioned again |
| 312 | in_progress (HOME) | 1627 `...; I59-A ROUND 4 HOME, SAVED AS THE PATCH (TASK #312)` | the batch landed (1649 names only #315) |
| 313 | in_progress (HOME) | 1644 `VERIFY-I59-BCE HOME: ... (TASKS #313, #314, #327)` | as #312 |
| 314 | in_progress (HOME) | 1644 (as #313) | as #312 |
| 319 | pending (REGISTERED) | 1610 `...; THE REPAIR S1-RATE-R1 (TASK #318) AND THE SCRUB GAP (TASK #319) REGISTERED` | never mentioned again |
| 320 | pending (REGISTERED) | 1613 `...; TASK #320 REGISTERED` | never mentioned again |
| 322 | pending (REGISTERED) | 1618 `...; TASK #322 REGISTERED` | never mentioned again |
| 327 | in_progress (HOME) | 1644 (as #313) | as #312 |
| 329 | pending (REGISTERED) | 1632 `...; TASKS #327-#329 REGISTERED` + body `#329 (after SCRUB2-R1 lands)` | a conditional registration, not `(backlog)` |

New ledger lines while I worked: 1653-1656. Line 1656 (`... TASK #344 REGISTERED — 2026-09-28 15:5xZ.`) registers
#344 as backlog (outside the view; it raises the `.highwatermark` target to 344).

The fix is the coordinator's: override rows (`## 1b. Task overrides`, `| id | status | note |`, status `closed` or
`backlog`) for the 27, or grammar words for `VERIFIED`/`confirmed`/`MERGE-READY` (a brief change). I did not guess
their statuses.

## 5. The hooks (evidence demand 5)

- **The installer writes both, each with `timeout: 30`:** `our_hooks()` adds one group per event after the existing
  one, the command `[ -f <repo>/scripts/task_sync.py ] || exit 0; cd <repo> || exit 0; python3
  <repo>/scripts/task_sync.py --hook stop|session-start` (the fail-open guard of af3ab70). Tests:
  `test_fresh_install_registers_the_seven_hooks`, `test_the_task_sync_hooks_are_installed_with_a_30_second_timeout`
  (the 7 other hooks carry no timeout), `test_an_older_task_sync_spelling_is_replaced_on_install` (the merge marker),
  `test_the_installed_task_sync_commands_run_against_a_temp_repo` (Stop writes, SessionStart prints, the off switch,
  a sync error exits 1 with one line), `test_the_repo_settings_register_both_task_sync_hooks` (the `$CLAUDE_PROJECT_DIR`
  form, run through `sh -c` against a temp repo).
- **Installer mutants** (pasted): `BASELINE (unmutated, 6 targets): rc=0 6 passed in 1.18s`; control green;
  `EXPECTED=7 KILLED=7 SURVIVED=0 INVALID=0 FAILED-OTHER=0 CONTROL=green`:

| Mutant | Test | Assertion (head) |
|---|---|---|
| I01-no-timeout | `test_the_task_sync_hooks_are_installed_with_a_30_second_timeout` | AssertionError: assert (1 == 1 and <class 'NoneType'> is int) |
| I02-no-sync-marker | `test_an_older_task_sync_spelling_is_replaced_on_install` | assert (2 == 1) |
| I03-stop-unregistered | `test_fresh_install_registers_the_seven_hooks` | AssertionError: assert {...'Stop': 1, ...} == {...'Stop': 2, ...} |
| I04-sync-unguarded | `test_every_installed_command_fails_open_when_the_repo_is_absent` | AssertionError: ('SessionStart', 2, '', "python3: can't open file '/ |
| I05-session-start-runs-stop | `test_the_installed_task_sync_commands_run_against_a_temp_repo` | assert (0 == 0 and False) |
| S01-settings-no-timeout | `test_the_repo_settings_register_both_task_sync_hooks` | AssertionError: assert (<class 'NoneType'> is int) |
| S02-settings-stop-unguarded | `test_the_repo_settings_register_both_task_sync_hooks` | AssertionError: assert 'python3 $CLA...y --hook stop' == '[ -f $CLAUDE...y --ho |

  (I01 and S01 first died on a `KeyError`; the driver scored them FAILED-OTHER, and both tests now assert on
  `.get("timeout")`.)
- **Stop never exits 2 and prints nothing on stdout:** every Stop run in the tests asserts `stdout == ""`; M32 (exit 2)
  and M33 (stdout) are killed. `--hook` never reaches argparse (its usage error is exit 2); an unexpected exception
  becomes a logged reason, never a traceback.
- **Once per new error:** `test_a_stop_error_is_shown_once_per_new_error_and_never_blocks`: A (no LIVE section) exit 1
  and one stderr line; A again exit 0, no stderr; B (unreadable ledger) exit 1; C (no session_id) exit 1; log
  `error` x4. Then a success, then C again: exit 0, silent (see D3).
- **The off switch:** `test_the_off_switch_makes_both_hooks_inert_and_refuses_apply`: stop, session-start, stop (s1)
  and stop (s2) each `(0, "", "")`, no config dir created, log exactly `off session=s1` and `off session=s2`;
  `--apply` exit 3 `off switch set`; the dry run exit 0 and prints the plan. The hook's first statement is the
  `off_switch_set()` check (`scripts/task_sync.py:743`). Measured on the copy: `Stop with the off switch: rc=0 wall=0.120 s
  output_bytes=0`.
- **Wall time on the real ledger, on a copy of the live DIR:** Stop 0.190 s (migration), 0.125 s (no change);
  SessionStart 0.156 s (12 lines, below). The timeout is 30 s. The test bound is 10 s.

SessionStart output on the migrated copy (pasted, the path shortened):

```
Task list = the ledger's view (scripts/task_sync.py, D-102): 38 open (24 in_progress, 14 pending) in <copy>
#339 in_progress t339-labeling-output-style-deep-work-path (BRIEFED 2026-09-28 14:2xZ)
#335 in_progress t335-i59-f-the-proof-code-follow-ups-before (DISPATCHED 2026-09-28 13:2xZ)
#315 in_progress t315-i59-d-re-mint-all-twelve-on-the-pc-from (DISPATCHED 2026-09-26 11:2xZ)
#321 in_progress t321-scrub2-r1-f1-and-f15-together-the-three (DISPATCHED 2026-09-28 12:5xZ)
#327 in_progress t327-batch-s0-03-s-read-yaml-has-i59-c-s-g2 (HOME 2026-09-28 12:4xZ)
#314 in_progress t314-i59-c-s0-04-verify-s0-04-leak-r1-g2-g5 (HOME 2026-09-28 12:4xZ)
#313 in_progress t313-i59-b-s0-05-f-6-wording-the-af-ap-169 (HOME 2026-09-28 12:4xZ)
#312 in_progress t312-i59-a-the-registry-field-extra-attested (HOME 2026-09-26 07:5xZ)
#310 in_progress t310-hctx1-briefed-and-dispatched-d-097 (LANDED 2026-09-26 04:2xZ)
#295 in_progress t295-s1-rate-each-system-1-injection-carries (LANDED 2026-09-26 02:3xZ)
+28 more: python3 scripts/task_sync.py --ledger todo/BUILD-TASKLIST.md --tasks-dir <copy>
```

## 6. Gates (evidence demand 6)

```
$ bash scripts/pc_suite.sh set-id -- tests/test_task_sync.py tests/test_session_hooks.py
2 files set=4fbf35b43338
$ bash scripts/test_summary.sh tests/test_task_sync.py tests/test_session_hooks.py --basetemp=<scratch>/bt/final1
pytest-exit: 0
pytest-summary: 94 passed in 8.53s
$ (run 2, a fresh basetemp)
pytest-exit: 0
pytest-summary: 94 passed in 8.74s
$ (run 3 at 16:35:50Z, HEAD c9889ee plus my working-tree files, the same set id)
pytest-exit: 0
pytest-summary: 94 passed in 8.41s
```

HEAD moved while I worked (3a82a10, 6b1c52e, c9889ee: the coordinator's commits, 16:00:49Z-16:04:36Z). All three
precede the migration run (16:18Z) and the gates; the ledger's last write (15:56:11Z) is inside the 1656-line snapshot.

- pyflakes on `scripts/task_sync.py tests/test_task_sync.py scripts/install_session_hooks.py tests/test_session_hooks.py`: rc 0.
- `python3 scripts/report_lint.py tasks/briefs/labeling/LS-B7-report.md --min-refs 20`:
  `report_lint: 24 refs — OK 24, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`, rc 0.
- `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`: 0 for each of those four, `.claude/settings.json`, and this report.
- Every other test that names a changed path (the build-loop gate rule): `tests/test_jev_context.py
  tests/test_search_intercept.py tests/test_system1_context.py tests/test_strip_cbm_hooks.py`: `297 passed in 128.57s`
  (plain pytest, not test_summary, after the installer and settings edits). `tests/test_vendored_manifest.py`: NOT run
  (it copies about 75 MB per test; the disk had 1.5 GB free, shared); see D2 for the manifest check instead.
- `scripts/ap_screen.py` over the four Python files: 14 tells, all advisory and by design: AF-AP-40 x7 (an absent
  task dir means "no files yet"; a temp-file cleanup; test helpers whose empty result fails the assertion; two
  pre-existing installer lines), AF-AP-72 x4 (`int()` only on names that fullmatched `\d+\.json` or on our own ids),
  AP-32 x2 (the digest labels a plan; only dry run and apply compare it), AP-1 x1 (`CLAUDE_CONFIG_DIR`, read once per
  process, the harness's own resolution).

## 7. NOT done, DISCREPANCIES, deviations

NOT done:
- **The live DIR** (the brief: the coordinator runs the first `--apply`). **CLAUDE.md, AGENTS.md, `.hermes.md`** (the
  coordinator rewrites the task-tracking rules). **No commit, no push.**
- **The override rows for the 27 extra ids** (§4): the coordinator's call, not guessed.
- **`tests/test_vendored_manifest.py`** not run (disk). **The DISK-PROBE** not re-run (it writes the live DIR).
- **Backup retention and log rotation:** none. A backup is taken only when a plan changes something (30,720 bytes
  for the 11 live files, measured); the log grows one line per Stop and SessionStart (174-204 bytes measured with a
  93-character scratch path; the live path is 56). Unbounded in principle.
- **`CLAUDE_CODE_TASK_LIST_ID` and team task lists:** the hook uses the payload's `session_id`, as the brief says. When
  the harness names its list otherwise (that variable, a team name), the hook writes a DIR the harness does not read.
  Not the case in this session (the variable is unset).

DISCREPANCIES:
- **D1. `flock DIR/.lock` excludes other `task_sync` runs, not the harness.** The harness locks with proper-lockfile
  (`DIR/.lock.lock` on create; `DIR/<id>.json.lock` or no lock on update; §1). Built as the brief says. Consequences,
  inferred: a harness TaskCreate during a sync can land between the plan and the write; the next sync deletes it (the
  view owns the DIR). Every write here is a rename, so the harness never reads a torn file. Taking the harness's own
  lock directory was rejected: a stale directory left by a killed sync would block the harness's creates (its retries
  last about 3 s, measured from its options; its stale limit is proper-lockfile's default 10 s, inferred: it sets
  none).
- **D2. Landing moves the vendored manifest.** `.claude/settings.json` is a kit-adapted file
  (`tests/test_vendored_manifest.py` ADAPTED_PATHS). `python3 scripts/vendored_manifest.py --check` (read-only):
  before my edits the first drifted row was `line 21 .claude/ (first-party)` (the known ignored
  `.claude/fast-jev-output/`, task #232); after them it is `line 20 .claude/ (kit-adapted)`. The class does not
  change. Landing step: `vendored_manifest.py --write` in a clean worktree (the 49dd6f5 precedent).
  `sandbox-kit/VENDORED-MANIFEST.md` is outside my boundary.
- **D3. "Only when that error differs from the previous error line" is built literally.** A recurrence of the same
  error after a success stays silent on Stop (pinned in the test). SessionStart still prints the newest log line when
  it is an error. Alternative (a one-line change): compare with the previous log line of any kind, so each new
  episode shows once.
- **D4. The view owns the DIR.** Any `<digits>.json` not in the view is deleted at the next Stop, a hand-made
  TaskCreate included. `.highwatermark` is raised to the largest placed ledger id (344 now), so a new harness id does
  not reuse an existing ledger id.
- **D5. The owner's UI list may refresh late** (inferred: no watcher found on the task DIR; the harness re-reads files
  on its own list and get calls). Not measured.

Deviations from the brief (each small, each flagged):
- **`--hook stop|session-start`** (not in the brief's CLI line): the hook form reads the payload on stdin; without it
  a hook cannot find its DIR.
- **`--lock-wait SECONDS`** (default 10): the lock test's refusal leg runs in 0.3 s instead of 10.
- **The tasks root is the harness's own resolution** (`$CLAUDE_CONFIG_DIR/tasks`, else `~/.claude/tasks`), which is
  `/root/.claude/tasks` here, the brief's literal. The tests move it with `CLAUDE_CONFIG_DIR`; the CLI tests also use
  `--allow-dir` as the brief says.
- **Only lines inside `## 2.` are read** (the brief's words): the 14 section-0 lines and the 88 date-first blocks are
  counted in the plan header, not read.
- **Titles:** the slug comes from the first body mention of the id on its registration line (name, parenthetical
  unless `(backlog…)` or `(open)`, the text after a colon), else the headline clause that names the id; a leading
  "the/a/an" is dropped. Deterministic, but some older slugs read poorly (`t167-lands-is-retired-only-after-verify-t94`).

## 8. Self-attack: the three likeliest ways this is wrong

1. **The grammar mis-binds a word to an id on a line I did not review.** Partly ruled out: of the prototype's 329
   bindings I read all 109 inherited or bound-before ones and all 103 unplaced mentions line by line; the 116
   bound-after ones (the word right after its id list) I checked by count only. The read found two wrong rules, both
   fixed and pinned (the tail took the whole headline: 1371 gave #196 HOME; a possessive bound: 1448 would have
   reopened #214), and 23 real lines are pinned with a mutant per rule. Residual: a future headline shape (an event
   word far from its id) can still bind wrongly; `unknown` catches only what binds nothing.
2. **The hooks go live on the coordinator's session before the verify round.**
   `scripts/setup.sh:438` runs `install_session_hooks.py` from the working tree at every SessionStart. Ruled out by construction and by test: the off switch is the first
   statement of `hook()`, its test (and M34) proves both hooks exit 0 with no output and no task file, and the main
   tree's off switch was present when I wrote the registration last (re-checked at 16:19:11Z).
3. **The migration destroys a task the coordinator still needs.** The first apply deletes 308, 316 and 317 and
   rewrites 8 files. Ruled out for loss: the backup tar holds the pre-state (tested, M30), the dry run shows every
   delete with the old subject, and deleted ids 316/317 (ledger #334/#335) come back as 334.json/335.json. Not ruled
   out: the 27 extra ids crowd the list until the coordinator adds override rows (§4).

## 9. Files (all in `/home/user/agent-factory`)

- CREATE `scripts/task_sync.py` (815 lines). Anchors, one per line:
  - `scripts/task_sync.py:87` `EVENTS` (the word -> status table)
  - `scripts/task_sync.py:171` `_scan` (id lists, qualifiers, BY, possessives, events, negation)
  - `scripts/task_sync.py:190` `_bind_items` (after, then before, then inherited)
  - `scripts/task_sync.py:245` `_stamp` (the last dated em dash outside parentheses)
  - `scripts/task_sync.py:276` `_line_mentions` (clauses, the tail parenthetical)
  - `scripts/task_sync.py:301` `_registration_text` (the title source)
  - `scripts/task_sync.py:375` `extract`
  - `scripts/task_sync.py:427` `build_view`
  - `scripts/task_sync.py:485` `make_plan`
  - `scripts/task_sync.py:517` `_lock` (flock with a bounded wait)
  - `scripts/task_sync.py:556` `apply_plan` (lock, re-plan, backup, rename, delete, highwatermark)
  - `scripts/task_sync.py:633` `allow_dir` (the run function: off switch, DIR check, ledger, empty view)
  - `scripts/task_sync.py:702` `view_lines` (the SessionStart block)
  - `scripts/task_sync.py:720` `_session_dir` (the harness's list-id spelling)
  - `scripts/task_sync.py:742` `hook`
  - `scripts/task_sync.py:743` `off_switch_set` (the hook's first statement)
  - `scripts/task_sync.py:791` `main` (`--hook` never reaches argparse)
- MODIFY `scripts/install_session_hooks.py` anchors:
  - `scripts/install_session_hooks.py:55` `task_sync` (the group, `timeout` 30)
  - `scripts/install_session_hooks.py:62` `task_sync("session-start")`
  - `scripts/install_session_hooks.py:79` `task_sync("stop")`
  - `scripts/install_session_hooks.py:97` `sync_marker`
  - `scripts/install_session_hooks.py:159` `installed 7`
- CREATE `tests/test_task_sync.py` (571 lines, 27 test functions; the parametrized cases make the 66 tests of the gate).
- CREATE `tasks/briefs/labeling/LS-B7-report.md` (this file).
- MODIFY `scripts/install_session_hooks.py` (+19 -8): docstring (seven hooks; the task_sync paragraph; the merge
  marker), `task_sync()` and the two groups in `our_hooks()`, `sync_marker` in `merged()`, "installed 7".
- MODIFY `.claude/settings.json` (+18): one group appended to SessionStart and one to Stop, each `timeout: 30`.
- MODIFY `tests/test_session_hooks.py` (+98 -7, `git diff --numstat`): the docstring, the seven-hook counts
  (9 commands, 10 with a foreign one), `SYNC`, and four new tests.

Scratch (`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ls-b7/`): deleted after this
report. The mutant rows above hold every name, anchor target and verdict a verifier needs to rebuild the driver.
