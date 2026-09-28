# VERIFY-LS-B7 report: the task-list sync under attack (task #339, D-102)

Started 2026-09-28 18:0xZ by the sandbox adversarial-verifier (Opus 5.5). Written incrementally; finished 2026-09-28
18:3xZ. Recommendation: MERGE-READY-WITH-FOLLOWUPS (GATE section).

## 0. Premise, re-measured

- The six sha256 prefixes (task_sync.py 8f6c4626c3728e02, test_task_sync.py 5151fb0d0888310f, install_session_hooks.py
  b78e189d0ac5b7db, test_session_hooks.py dddd30002144af50, .claude/settings.json 03b9e1e1b04d34d7, LS-B7-report.md
  229c96d812017ea5): all equal to the premise; the same five lane files hash the same in the scratch copy.
- HEAD moved c9889ee -> c4b87d1 (five coordinator commits, 16:44Z-17:35Z). Under scripts/, tests/, .claude/settings.json
  and todo/ they change only todo/BUILD-TASKLIST.md (+2 lines: 1657 LS-B7 HOME, 1658 RETRO 16:4xZ; 1659 lines now).
- The off switch /home/user/agent-factory/.jev/task-sync-off is present (148 bytes, 14:58). The live DIR still holds the
  11 harness files (317.json rewritten 17:02 by the harness). /home/user/.claude/settings.json (mtime Sep 26) carries
  no task_sync hook yet: the registration is not live.
- Disk: 1334 MB free at start (premise 1585).


## 1. The builder's gate, reproduced (item 8's re-run)

Scratch copy `/tmp/vlsb7/repo`: `git archive HEAD(c4b87d1) scripts tests .claude/settings.json todo .gitignore`, plus
`.claude/hooks` (four pre-existing `tests/test_session_hooks.py` tests run the real hook scripts; without them they fail
with JSONDecodeError/exit codes, unrelated to LS-B7), plus the five lane files (hashes equal to the premise). One more
pre-existing test (`test_a_real_read_from_another_cwd_reaches_the_model_form`) needs `git log` history of the file it
reads, so the copy was made a throwaway git repo (one scratch commit; the project repo untouched). Pasted:

```
$ bash scripts/pc_suite.sh set-id -- tests/test_task_sync.py tests/test_session_hooks.py
2 files set=4fbf35b43338
$ bash scripts/test_summary.sh tests/test_task_sync.py tests/test_session_hooks.py --basetemp=/tmp/vlsb7/bt/g1   (then g2)
pytest-exit: 0
pytest-summary: 94 passed in 7.99s
pytest-exit: 0
pytest-summary: 94 passed in 7.87s
```

pyflakes on the four Python files: rc 0. `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`: 0 for all five lane files.

## 2. Item 2: the view on the real ledger

**The digest reproduces.** The builder's ledger is `c9889ee:todo/BUILD-TASKLIST.md` (1656 lines, sha256 df27d1e1aa6a,
the same blob at 3a82a10 and 6b1c52e). Its dry run against a fresh `cp -a` of the live DIR (18:04Z, same 11 names,
`.highwatermark` 314): `view=38 create=30 update=8 delete=3 hwm=314->344 digest=7c625d53cb41`, equal to the report.
On the current ledger (1660 lines, sha256 831760a7e15e): the same 38 ids, `hwm=314->345 digest=bb78d5fbf5a7` (line
1656 registers #344 backlog, a later line #345; no view change). Lines 1657-1660 name #339 only in their bodies.

**The grammar is faithful on all 27 extra ids; the ledger's prose closes or parks most of them where the grammar does
not read.** I read every mention of each id in the whole file (all sections, headline and body). I found no mis-binding:
each open status is what the committed rules give. But for 22 of the 27 the prose says the task is finished or parked,
in a body, in a word outside the list (VERIFIED, ACCEPTED in a body, MERGE-READY, CONFIRMED, "on origin"), or in the
L1581 body's explicit backlog list. The override table is the designed fix; this table is my reading for its rows
(the coordinator's call, not mine):

| Id | Grammar (line) | What the ledger says after it | My reading |
|---|---|---|---|
| 121 | LANDED (1426) | 1436 headline: `J1-4 AND J1-5 VERIFIED, MERGE-READY-WITH-FOLLOWUPS (...; #121 confirmed)` | closed |
| 148 | LANDED (1391) | 1394 body: VERIFY-C2's mutants were reasoned, "so C2 STAYS GATED-PENDING-VERIFY"; nothing later | open (stale since 09-23) |
| 167 | HOME (1388) | 1394 body: "T94 (tasks #167 + #200) is ACCEPTED" | closed |
| 170 | DISPATCHED (1439) | 1461 body: "K170 landed GATED-PENDING-VERIFY ... VERIFY-K170 goes to the PC after MoJev G0" | open (verify owed) |
| 196 | DISPATCHED (1374) | 1379 body: "B12 (task #196 ...) landed as 375ea55", batched into VERIFY-S0-02; 1440: all twelve proofs ACCEPTED | closed (inferred) |
| 200 | HOME (1388) | 1394 body: ACCEPTED (as #167) | closed |
| 206 | LANDED (1400) | S0-05 minted (1402), VERIFY-S0-05 dispatched (1403), all twelve ACCEPTED (1440) | closed (inferred) |
| 210 | BRIEFED (1444) | MoJev Gate 0 staged; no later mention | open (stale?) |
| 215 | DISPATCHED (1429) | 1437 headline tail: "(task #219 closed; tasks #215 and #218 VERIFIED)" | closed |
| 216 | DISPATCHED (1429) | 1432 body: "Tasks: #216 closed, #202 closed NOT-READY" (the grammar's own word, in a body) | closed |
| 221 | DISPATCHED (1447) | steps continue (1450, a stamp-less line: "#221 step 3") | open |
| 251 | DISPATCHED (1509) | 1522 headline: "DSV2 MERGE-READY-WITH-FOLLOWUPS (TASK #251)" | closed |
| 253 | LANDED (1511) | JEV-MAP, an evidence lane, landed its report; no later mention | closed (inferred) |
| 256 | LANDED (1517) | "THE OWNER'S INTERVIEW NEXT"; no later mention | open (stale?) |
| 290 | REGISTERED (1567) | 1581 body: "the backlog stays open here (#273, ..., #290-#294, #298-#300)" | backlog |
| 291 | REGISTERED (1568) | 1581 body: backlog; 1585: CONFIRMED (a real gap, still owed) | backlog |
| 293 | REGISTERED (1568) | as #291 | backlog |
| 310 | LANDED (1609) | 1617 HCTX1-R1 (#316, #317) dispatched from its verify; 1628: "HCTX1-R1'S PC CHECK PASSES; TASKS #316 AND #317 CLOSED" | closed (inferred) |
| 311 | REGISTERED (1605) | 1612: #273 "moves ahead of #311 as the root fix"; never active | backlog |
| 312 | HOME (1627) | 1649: "THE ISSUE #59 BATCH IS ON ORIGIN (TASK #315)" | closed |
| 313 | HOME (1644) | 1644: MERGE-READY-WITH-FOLLOWUPS; batch on origin (1649) | closed |
| 314 | HOME (1644) | as #313 | closed |
| 319 | REGISTERED (1610) | 1617: confirmed as a new gap; 1643: "follow-ups under #319's scope"; never active | backlog (or pending) |
| 320 | REGISTERED (1613) | named as a design area (1621, 1627, 1646); never active | backlog |
| 322 | REGISTERED (1618) | never mentioned again | backlog (or pending) |
| 327 | HOME (1644) | as #313 | closed |
| 329 | REGISTERED (1632) | body: "#329 (after SCRUB2-R1 lands)", a deferred registration; #321 still in round 2 | backlog (deferred) |

Tally of my reading (counted from the table rows by a script): closed 14 (121 167 196 200 206 215 216 251 253 310 312 313 314 327), open 5 (148 170 210 221 256), backlog 8 (290 291 293 311 319 320 322 329). The
grammar's reading for #329 (`(after ...)` read as a plain registration, pending) is its committed rule; the contract
names only `(backlog)` as the backlog marker, so this is honest, not a defect.

Of the brief's 11 ids: #289 and #334 come out `pending` (REGISTERED 1565 and 1643; later mentions WIDENED, ASSESSED
are outside the list), where the harness shows `in_progress`. #334's prose reads finished (1645 "ASSESSED (D-100)";
1649 lands its commit 67ed2ca). #315: "THE ISSUE #59 BATCH IS ON ORIGIN (TASK #315)" (1649) is not a list word, so it
stays DISPATCHED; whether the re-mint keeps it open is the coordinator's call.

**Accounting gap (FOLLOW-UP F-6 below).** 14 bold lines inside `## 2.` carry no ` — YYYY-MM-DD` stamp (a time-only
headline, 2026-09-2x legacy shape: L426, 428, 1450, 1458, 1477, 1478, 1481, 1483, 1485, 1486, 1491, 1492, 1499, 1542).
The extractor skips them with no count in the plan header and no `unknown` record. Two of them close task ids in the
grammar's own word: L1486 `JT3 RE-ARMED 20:06:30Z; TASKS #228, #225, #236 CLOSED.` and L1499 `...; TASK #246 CLOSED.`
None of those ids has any other placed event, so today's view does not change. The report's "not read" accounting
(88 date-first, 14 outside `## 2.`) omits this third class.

## 3. Item 1: the grammar

Drivers: `/tmp/vlsb7/an/g1.py` (statuses through the real `extract` + `build_view`) and `/tmp/vlsb7/an/cli1.py` (the
real CLI, `--apply --allow-dir`, a seeded DIR; "unchanged" = the DIR's file hashes before and after).

**On the real ledger: no mis-binding found.** An instrumented copy of `_bind_items` (`/tmp/vlsb7/an/bindings.py`)
listed all 172 bindings on the 1660-line ledger: 93 "after" (every one the event right after its id list), 2 "before"
(L1565 `REGISTERED AS TASKS #287-#289`, L1653 `BRIEFED, TASK #339`) and 77 "inherited" (a parenthetical taking its
clause's event). I read all 172; each is right. No id above 400 is placed (no phantom run or line number), and the
risky shapes below occur 0 times in the ledger's headlines (`RUNS #`, `CI #`, `LINE #`, `<event> AND CLOSED`,
`(BACKLOG)`, `( backlog`).

**Constructed shapes (the real extractor; none occurs in today's ledger):**

| Case | Headline | Result | Honest reading |
|---|---|---|---|
| A1a | `OLD LANE CLOSED AND NEW LANE (TASK #7) DISPATCHED` | #7 closed | in_progress (the paren prefers the event BEFORE it) |
| A1b | `TASK #7 WAITS UNTIL B11 LANDED` | #7 in_progress | pending |
| A1c | `TASK #7 REPLACES THE SUPERSEDED DESIGN` | #7 closed | pending (adjective) |
| A1d | `TASK #7: THE WORK DONE SO FAR IS SAVED` | #7 closed | in_progress (lower-case noun use) |
| A1f | `TASK #7 LANDED AND CLOSED` | #7 in_progress | closed (the first event after a list wins) |
| A1g | `TASK #7 REGISTERED AND CLOSED` | #7 pending | closed |
| A1h | `TASK #7 NOT IN FACT DISPATCHED` | #7 in_progress | pending (negation looks back 2 words) |
| A1i | `CI RUNS #1087 AND #1088 PASSED` | phantom #1087, #1088 in_progress | no task (RUNS is not a qualifier; RUNS binds) |
| A1j | `CI #1090 GREEN AND LANDED; ...` | phantom #1090 in_progress | no task |
| A1k | `D-058 LANDED (SEE LEDGER LINE #1500)` | phantom #1500 in_progress | no task |
| A2a-d | `#7'S HOOKS LANDED`, `#7’S`, `#7's hooks closed`, `#7 AND #8'S HOOKS CLOSED` | unknown, status unchanged | correct |
| A3a-c | `#291-#293`, `#291 – #293` (en dash), `#291-293` | 291, 292, 293 | correct |
| A3d | `TASKS #200-#230 CLOSED` (span 30 > 20) | only #200 and #230 closed; 201-229 untouched, not even `unknown` | a silent partial close |
| A3e | `TASKS #293-#291 CLOSED` (reversed) | #291, #293 closed; #292 untouched | as A3d |
| A4a-c | `#200 + #167`, `#1, #2, and #3` | all bound | correct |
| A4b | `TASK #200 OR #167 CLOSED` | #167 closed, #200 unknown | conservative, fine |
| A5 | CLOSED 09:0xZ, then `VERIFY-X DISPATCHED (TASK #7)` 10:0xZ | reopened, in_progress | by the contract (newest event) |
| A6a | CLOSED, then a later `TASKS #9-#11 REGISTERED` | #10 reopened, pending | by the contract; a re-used or typo range reopens silently |
| A6b/c | `TASK #10 CLOSED; TASK #10 REGISTERED` / reversed, one line | pending / closed | the last binding in the line wins |
| A7a | two lines in one bucket, CLOSED then DISPATCHED in file order | in_progress | file order, as documented |
| A7b | `10:09:59Z` DISPATCHED then `10:0xZ` CLOSED | closed | same bucket, file order, as documented |
| A7c | an older stamp appended later | ordered by stamp | correct |

A phantom id also raises `.highwatermark` for good (the view never lowers it): A1i leaves it at 1088.

**The override table (the real CLI):**

| Case | Result |
|---|---|
| J1 a row with 2 cells; J3 status `done`; J4 `Closed`; J5 a `|` in the note (4 cells); J6 id `t10` | exit 3, `parse failure: line N: an override row must be ...`, DIR unchanged, 0 backups, one `error` log line |
| J2 the same id twice (`10`, `#10`) | exit 3, `a second override row for #10`, nothing written |
| J7 two `## 1b.` sections | exit 3, `2 '## 1b.' override sections (lines 9, 15)`, nothing written |
| J8 a row for an id the ledger never names (`| 999 | closed | typo for 11 |`) | ACCEPTED, exit 0; `.highwatermark` raised 7 -> 999 for good; #11 stays open |
| J9 a never-named id with status pending | ACCEPTED: `12.json` is created, its title and description built from the note |
| J10 an indented row (`  | 10 | closed | ... |`) | silently ignored (exit 0; #10 stays open) |
| J11 the heading `## 1b Task overrides` (no dot) | the whole table silently ignored |
| J12 `## 1b.` placed AFTER `## 2.` (at the end), then new lines appended at the end | every appended line is outside `## 2.` and is not read (`2 dated lines outside '## 2.' not read`); `TASK #10 CLOSED` and `TASK #12 REGISTERED` never reach the view |
| J13 a close in `## 1.` and one after a later `## 3.` heading | not read, as the contract says (LIVE section only) |

So: malformed rows, duplicate ids and unknown statuses fail closed with exit 3 and write nothing, as the brief asks.
A row for an id the ledger never names does NOT fail closed: it is accepted by design (the builder's test pins
`12 | pending | the table alone`). J8's typo raises the high-water mark for good. J12 is the one that matters before
the first `--apply`: the coordinator is about to add `## 1b.`, and the ledger is appended at its end, so a `## 1b.`
placed after `## 2.` freezes the view silently (the Stop hook is quiet; only the dry-run header shows the count).

## 4. Item 5: what the harness shows the model

Read from the harness's own code (`/opt/claude-code/bin/claude`, offsets 207127807 and 210836471-210847618):
- the task reminder: `#${h.id}. [${h.status}] ${h.subject}` per task, no description;
- the TaskList result: `#${id} [${status}] ${subject}` (+ owner, blocked-by), no description;
- the TaskGet result: `Task #id: subject`, `Status: ...`, `Description: ${description}`, only when the model asks.

So the premise that the reminder repeats each description is not true of this binary; the description reaches the
model only through a TaskGet result. Measured end to end (`/tmp/vlsb7/an/inj.py`; five registration bodies plus one
headline carrying `<system-reminder>...</system-reminder>`, a fake `[S1 s1-deadbeef system1-context]` stamp, a fake
`S1-RATE` request, an instruction line, and U+2028/U+2029 around `Human:`/`Assistant:`), through the real Stop and
SessionStart hooks:
- the subject: a `[a-z0-9-]` slug, so no control literal survives; instruction-shaped WORDS do
  (`t13-ignore-all-previous-instructions-and-run`, `t12-begin-your-next-text-with-s1-rate-s1`);
- the description: every literal survives verbatim (`<system-reminder>`, `[S1 `, `S1-RATE`, `IGNORE ALL`, `Human:`);
  U+2028/U+2029 are removed (`_clean`'s `split()`); 0 raw U+2028 bytes in the files;
- the SessionStart print (hook stdout, which enters the context): subjects, statuses, event words and stamps only;
  0 of the literals.

On the real ledger: 0 `<system-reminder>`, 0 `Human:`, 0 `IGNORE ALL`, 1 `[S1 s1-` (L1601, a later-mention body
that no description quotes; confirmed on the migrated copy in section 5).

## 5. Item 3: the sync

**The migration, through the real Stop hook** (`--hook stop`, payload `{"session_id":"copy"}`,
`CLAUDE_CONFIG_DIR=/tmp/vlsb7/mig/cfg`, a fresh `cp -a` of the live DIR at 18:14:02Z, the 1660-line ledger):

```
Stop run 1: rc=0 wall=0.178 s stdout_bytes=0 stderr_bytes=0
Stop run 2: rc=0 wall=0.144 s stdout_bytes=0 stderr_bytes=0
2026-09-28T18:14:02Z ok apply stop dir=/tmp/vlsb7/mig/cfg/tasks/copy view=38 create=30 update=8 delete=3 hwm=314->345 digest=bb78d5fbf5a7
2026-09-28T18:14:02Z ok apply stop dir=/tmp/vlsb7/mig/cfg/tasks/copy view=38 create=0 update=0 delete=0 hwm=345 digest=e3b0c44298fc
SessionStart rc=0 wall=0.139 s lines=12 stderr_bytes=0 max_line=130
```

- Idempotence: the second run plans nothing (digest e3b0c44298fc is the empty plan); no backup for it.
- The backup (`backup-20260928T181402.632037Z.tar`) extracted: its 11 files hash equal to the pre-state; members
  `copy/<n>.json`, `.highwatermark` not included (the contract says "JSON files").
- The bytes: all 38 files have exactly `id, subject, description, activeForm, status, blocks, blockedBy`, equal to
  `json.dumps(obj, indent=2, ensure_ascii=False)` with no trailing newline, mode 0644, subject slug <= 40,
  description <= 400 (max 400), 0 control literals. No `.tmp-` file is left.
- Write-then-rename: `_write_atomic` writes `.<name>.tmp-<pid>`, fsyncs, `os.replace`s; the harness lists only names
  ending in `.json` (read from its code), so a temp file is never listed.

**D1, the race with the harness, from the harness's own code** (file store, offsets ~202926617-202936000):
TaskCreate takes proper-lockfile on `DIR/.lock` (a `.lock.lock` directory; retries 30, 5-100 ms), sets
id = max(largest `<n>.json`, `.highwatermark`) + 1, and writes the file with a plain `writeFile` (truncate, then
write: not atomic). TaskUpdate reads the file, locks `<id>.json.lock`, re-reads, merges, `writeFile`s. Delete raises
`.highwatermark` with a plain `writeFile` when the id is larger, and unlinks with no list lock. A reader
(`Uae`) that meets a torn or invalid file logs it and treats the task as absent. `flock DIR/.lock` excludes none of
this. What can happen, each checked against the code:
1. A TaskCreate during the FIRST migration (hwm 314, files up to 319) takes id 320, which the plan is creating for
   ledger #320: whichever write lands last wins. If the sync's rename lands last, the model was told
   "Task #320 created successfully: <its subject>" while the file holds ledger #320. After the migration the
   high-water mark covers every placed ledger id, so a collision needs a ledger id registered since the last Stop.
2. A TaskUpdate racing a sync: the sync may read the harness's half-written file; it then plans an update and
   renames the view's bytes over it. The harness's remaining bytes go to the old (renamed-away) inode, or its later
   `writeFile` overwrites the view until the next Stop. No torn file persists; the harness never sees a torn file of
   the sync's (renames only).
3. A delete racing the sync can write a LOWER `.highwatermark` after the sync raised it (the harness read the old
   value first). Its next TaskCreate then gets a smaller id; the next Stop deletes that hand task (D4) and raises the
   mark again.
4. `resetTaskList` (which deletes every task file) runs from a UI timer only when every task is `completed`; the view
   never writes `completed`, so it fires only if the coordinator hand-completes every task; the next Stop re-creates.

Measured (`/tmp/vlsb7/an/race.py`): 40 `--apply` syncs raced an emulated harness doing 2,474 operations (637 creates
at the harness's next id, 1,273 two-chunk torn updates, 564 deletes). Every sync exited 0; no temp file left; the
emulated harness never read a torn file; after one quiet sync the DIR was byte-identical to a clean apply of the same
ledger (38 files, `.highwatermark` 345); 0 error log lines. **So nothing the ledger holds is lost; what a race loses
is harness-side hand state (a TaskCreate, a hand update, a hand delete), which D4 discards at the next Stop by
design.** One gap: a hand change written between the backup and the sync's writes is in no backup.

**D4, confirmed through the real Stop hook** on the migrated copy: a hand TaskCreate at the harness's next id
(346.json) is deleted at the next Stop (it is in that Stop's backup); a hand TaskUpdate of #339 (`completed`, a new
subject) is rewritten to the ledger's bytes (`in_progress`, `t339-labeling-output-style-deep-work-path`); a hand
delete of 340.json is undone. Log: `create=1 update=1 delete=1 hwm=345`. So between two Stops a coordinator
TaskUpdate is visible to the harness and the owner (the reminder shows its status and subject); at the next Stop it
is gone. A task can be closed only in the ledger (a CLOSED/DONE headline) or by an override row; TaskUpdate
`completed` no longer closes anything.

**Backups grow without bound** (the builder's NOT-done, measured): every Stop whose plan changes something writes a
tar. A view task's description names its newest ledger line, so any ledger line that mentions an open task changes
that file at the next Stop, and a backup follows. The 40-sync race wrote 42 tars.

## 6. Item 4: fail closed

- Unreadable ledger (missing, not UTF-8), parse failures (no `## 2.`, no dated line, malformed time, bad date, a bad
  override row), an empty view: the builder's tests cover each (exit 3, DIR bytes unchanged); the override variants
  J1-J7 above re-checked them through the CLI, with 0 backups and exactly one `error` log line each.
- A DIR outside the tasks root without `--allow-dir`: refused (the builder's test, three shapes: elsewhere, a
  grandchild, the root itself). The hook form always builds `<root>/<sanitized id>`.
- **Hostile `session_id` through the real Stop hook** (`/tmp/vlsb7/an/hostile.py`; I listed every path under the
  scratch universe before and after each payload): `../x` -> `---x`, `../../../../tmp/vlsb7-escape` ->
  `------------tmp-vlsb7-escape`, `/tmp/vlsb7-abs` -> `-tmp-vlsb7-abs`, `.` -> `-`, `..` -> `--`, `a\u0000b` -> `a-b`,
  a newline, 200 characters (accepted, one component), `s\u00e9ss\u2028/x` -> `s-ss--x`, `~root`, `$HOME`, `..\..\x`:
  each lands in ONE directory directly under the tasks root; 0 paths outside it; the escape canaries do not exist.
  201 characters, `""`, `"   "`, an int, a list, a missing key, non-JSON, invalid UTF-8, a 2 MB payload (read cut at
  1 MiB, so the JSON breaks): refused as `hook payload: no usable session_id` (exit 1 once, then silent per D3).
  A 100,000-deep nested JSON array: `stop hook failed: RecursionError ...`, exit 1, one line (caught).
- Found: **the off path does not catch that RecursionError**: with the off switch set, the deep-nest payload gives a
  25-line Python traceback and exit 1 (`_log_off_once` catches only `Refused` and `OSError`). Hostile payload only.
- Found: **two ledger inputs escape `Refused` on the CLI**: `TASK #10 REGİSTERED` (U+0130; `re.IGNORECASE`
  matches it, `.upper()` keeps it, `EVENTS[word]` raises `KeyError: 'REGİSTERED'`) and 1,200 nested parentheses
  (`RecursionError`). Both: exit 1 with a traceback, no log line (the contract: exit 3 with the reason, one log line
  per run); nothing written. Through the hook both are caught (exit 1, one line). A long s (U+017F) in `DIſPATCHED`
  is accepted as DISPATCHED; full-width digits `#１２` place task 12; `#99999999999999999999` creates that file and
  sets `.highwatermark` to it.

## 7. Item 6: the hooks

- Stop never prints on stdout: 0 bytes in every Stop run above (the migration, the hostile payloads, D3, the off
  variants). Exit codes seen: 0 and 1 only. `grep -n 'decision\|exit(2\|return 2' scripts/task_sync.py`: no hit; the
  `--hook` form never reaches argparse (a wrong event word returns 0).
- The off switch: `hook()`'s first statement (`scripts/task_sync.py:743`); inert as a file, a directory and a
  dangling symlink (exit 0, no output, no task file re-created); `--apply` refuses with exit 3 (builder's test).
  The live `/home/user/.claude/settings.json` does not yet carry the registration (mtime Sep 26), and the main
  tree's off switch is present, so nothing runs on the coordinator's session today. I did not run the main tree's
  script: its off path appends to the main tree's `.jev/task-sync/sync.log`, which this brief forbids.
- **D3, measured** (`/tmp/vlsb7/an/d3.py`): busy lock -> exit 1, one line (10.1 s, the 10 s lock wait); two
  successes; a second busy episode -> exit 0, silent, while the view misses the new #12. The log: `error, ok, ok,
  error`. The contract's words ("differs from the previous error line") support D3 literally; its stated purpose ("a
  persistent error is shown once, not every turn") is equally met by comparing with the previous line of any kind,
  which also shows each new episode. SessionStart prints the newest error line, so the owner learns at the next
  session start at the latest.
- SessionStart: 12 lines on the 38-task view (header, 10 tasks, `+28 more: ...`); at most 160 characters a line. Its
  `+N more` hint is a repo-relative command (`python3 scripts/task_sync.py --ledger todo/BUILD-TASKLIST.md ...`); the
  session's cwd is `/home/user`, so it works only after `cd agent-factory`.
- Wall times (the real ledger, a copy of the live DIR): Stop 0.178 s (migration) and 0.144 s; SessionStart 0.139 s;
  a lock-busy Stop 10.1 s. All under the 30 s timeout.

## 8. Item 7: the installer and settings; D2

- The lane's installer (the main tree's file; it writes only `--target`) on a scratch copy of the live
  `/home/user/.claude/settings.json`: HEAD's installer (ROOT pinned to the repo) says `present`, the lane's says
  `MISSING or stale`; the install gives `installed 7`, a second run `unchanged`, then `--check` `present`. JSON-level:
  the result minus the two task_sync groups equals the original, key and event order kept; the new groups sit at
  `SessionStart[1]` and `Stop[1]` (after the existing ones), each one hook with `timeout: 30` and the command
  `[ -f /home/user/agent-factory/scripts/task_sync.py ] || exit 0; cd /home/user/agent-factory || exit 0; python3
  /home/user/agent-factory/scripts/task_sync.py --hook stop|session-start`. On an empty target the lane's output minus
  the sync groups equals HEAD's output. No existing hook changes.
- `.claude/settings.json`: the lane's file minus the two groups equals `c4b87d1:.claude/settings.json`; the groups
  are `SessionStart[1]` and `Stop[1]` with `timeout: 30` and the `$CLAUDE_PROJECT_DIR` form.
- Git ignores `.jev/` whole (`.gitignore:68`), so the log, backups and the off switch never show in `git status`
  (the Stop hooks that run in parallel read git state, not these files).
- **D2, confirmed read-only** (`vendored_manifest.py --check` runs only `git rev-parse`; run with
  `PYTHONDONTWRITEBYTECODE=1` on the main tree): `FAIL: vendored manifest drift: line 20` `.claude/ (kit-adapted)`
  committed `6b8ef19ad16f...` generated `c6cab0768ae6...`; plus the known `.claude class drift:
  fast-jev-output/.gitignore` (task #232). `.claude/settings.json` is the only tracked change under `.claude/`, so the
  line-20 move is this lane's. Landing needs `vendored_manifest.py --write` from a clean worktree (before the push).

## 9. Item 8: mutation

Driver `/tmp/vlsb7/an/mut.py`: one exact-once replacement in the scratch copy; the FULL two-file suite (94 tests) runs
against each mutant, so every killing test shows, not only a named target; `PYTHONDONTWRITEBYTECODE=1`, a private
basetemp; the pristine bytes restored and re-hashed (`8f6c4626c3728e02`) after each. Baseline `94 passed in 7.49s`;
the control C00 (a renamed local in `_paren_groups`) stays green (`94 passed`).

| Mutant | Clause | Verdict | Killing tests (FAILED) |
|---|---|---|---|
| M17 BY is a subject | grammar | KILLED | `...[1651-closed-and-by]`, `test_unknown_mentions_never_change_a_status` |
| M18 possessive is a subject | grammar | KILLED | `...[1448-possessive]` |
| M19 no negation | grammar | KILLED | `...[1620-negation]` |
| M06 undecodable ledger escapes | fail-closed | KILLED | `test_an_unreadable_ledger_writes_nothing_and_exits_3[not-utf8]` |
| M08 empty view applied | fail-closed | KILLED | `test_an_empty_view_writes_nothing_and_exits_3` |
| M34 hooks ignore the off switch | off switch | KILLED | `test_the_off_switch_makes_both_hooks_inert_and_refuses_apply`, `test_the_installed_task_sync_commands_run_against_a_temp_repo` |
| M36 --apply ignores the off switch | off switch | KILLED | `test_the_off_switch_makes_both_hooks_inert_and_refuses_apply` |
| M10 no flock | the lock | KILLED | `test_a_held_lock_is_waited_for_and_never_written_under` |
| M31 every error shown | Stop once per new error | KILLED | `test_a_stop_error_is_shown_once_per_new_error_and_never_blocks` |
| M32 Stop exits 2 | never exit 2 | KILLED | the same, and `test_the_installed_task_sync_commands_run_against_a_temp_repo` |
| **N1** `os.replace` -> `path.write_bytes(data)` | item 3: each file by write-then-rename | **SURVIVED** (94 passed) | none |
| **N2** SessionStart runs with `apply=(event == "stop")` | item 5: SessionStart runs the same sync | **SURVIVED** (94 passed) | none |
| **N3** the CLI `--apply` success writes no log line | item 4: every run appends one log line | **SURVIVED** (94 passed) | none |
| N4 the description carries the pid | item 2: the same ledger gives the same bytes | KILLED | `test_the_same_ledger_gives_the_same_bytes`, `test_a_second_run_plans_nothing`, `test_create_...` |
| N5 no backup taken | item 3: first backs up | KILLED | `test_the_backup_holds_the_pre_state`, `test_a_second_run_plans_nothing` |
| N6 `.highwatermark` never written | item 3: raises the mark | KILLED | four tests, `test_the_highwatermark_is_raised_never_lowered` among them |
| N7 no `off` log line | item 7: one off line per session | KILLED | `test_the_off_switch_makes_both_hooks_inert_and_refuses_apply` |
| N8 the Stop error not logged | item 5: logs the error | KILLED | the Stop-error test and the SessionStart test |
| IN1 the installer drops the retro gate from Stop | item 7 (verify): no existing hook changes | KILLED | 5 tests, `test_fresh_install_registers_the_seven_hooks` among them |
| SN1 settings.json's retro gate replaced | the same | KILLED | `test_the_repo_settings_register_both_task_sync_hooks` |

All ten reproduced builder mutants die as FAILED tests on the tests the report names. N1, N2 and N3 survive: the code
does each thing (N1: `_write_atomic` read and exercised by the race run; N2: a real SessionStart on a fresh DIR wrote
`10.json`, log `ok apply session-start`; N3: a real CLI `--apply` logged `ok apply dir=...`), but no test pins it.

## 10. Finding inventory (no severity filter)

Reproduction snippet R (self-contained; run from the repo root; pure functions, writes nothing):

```
python3 - <<'PY'
import importlib.util; s = importlib.util.spec_from_file_location("ts", "scripts/task_sync.py"); ts = importlib.util.module_from_spec(s); s.loader.exec_module(ts)
EM = chr(0x2014); H = "## 2. LIVE\n\n"
for head in ["OLD LANE CLOSED AND NEW LANE (TASK #7) DISPATCHED", "TASK #7 REPLACES THE SUPERSEDED DESIGN", "TASK #7 LANDED AND CLOSED", "CI RUNS #1087 AND #1088 PASSED"]:
    print(repr(head), ts.build_view(ts.extract(H + f"**{head} {EM} 2026-09-28 10:0xZ.**\n"))["status"])
t = (H + f"**TASK #10 REGISTERED {EM} 2026-09-28 10:0xZ.**\n\n## 1b. Task overrides\n\n| id | status | note |\n|---|---|---|\n| 11 | closed | x |\n\n"
     f"**TASK #10 CLOSED {EM} 2026-09-28 11:0xZ.**\n")
ex = ts.extract(t); print("J12:", ts.build_view(ex)["status"], ex["stats"])
try:
    ts.extract(H + f"**TASK #10 REGİSTERED {EM} 2026-09-28 10:0xZ.**\n")
except Exception as e:
    print("F-7:", type(e).__name__, e, "| is Refused:", isinstance(e, ts.Refused))
PY
```

Its output at the PIN (pasted): `{7: 'closed'}`, `{7: 'closed'}`, `{7: 'in_progress'}`, `{1087: 'in_progress', 1088:
'in_progress'}`; `J12: {10: 'pending', 11: 'closed'} {'dated': 1, 'date_only': 0, 'legacy': 0, 'outside': 1}`;
`F-7: KeyError 'REGİSTERED' | is Refused: False`.

| # | Class | Finding | Evidence | Contract mapping | Canonical path | Material effect | Reproduction | Suggested fix |
|---|---|---|---|---|---|---|---|---|
| F-1 | FOLLOW-UP | Grammar mis-binds constructed shapes: a paren prefers the event BEFORE it (`X CLOSED AND Y (TASK #7) DISPATCHED` -> closed); adjectives and noun uses count (`THE SUPERSEDED DESIGN`, `THE WORK DONE`); the first of two events wins (`LANDED AND CLOSED` -> in_progress; `REGISTERED AND CLOSED` -> pending); negation looks back 2 words; RUNS, CI, LINE are not qualifiers (phantom tasks #1087, #1088, #1090, #1500, each raising `.highwatermark` for good) | reproduced (real extractor, built lines) | item 1 ("never guessed"): arguable; the binding rules are the builder's committed design | yes, on built input; 0 occurrences in the real ledger (172 real bindings read, all right) | none today; a future headline in these shapes gives a wrong status, and a wrong close hides open work | snippet R; `/tmp`-free | qualifiers += RUNS, CI, LINE, COMMIT; a paren with events on both sides, or a list with two conflicting events, becomes `unknown`; an event after THE/A/AN is not an event; a ledger-writing convention `TASK #N <EVENT>` |
| F-2 | FOLLOW-UP (pre-apply) | A `## 1b.` section (or any `## ` heading) placed after `## 2.` ends the LIVE section there; every line appended later (the ledger's habit) is silently not read, and the Stop hook stays quiet | reproduced (CLI J12 and snippet R: `outside: 1`) | none (placement unspecified) | yes | the view freezes silently from that point | snippet R | refuse (exit 3) a `## 1b.` after `## 2.`, or any dated headline after the LIVE section's end |
| F-3 | FOLLOW-UP | An override row for an id the ledger never names is accepted (a typo `| 999 | closed |` raises `.highwatermark` 7 -> 999 for good and leaves the meant task open; a `pending` row creates a task from its note) | reproduced (CLI J8, J9) | none (the builder's test pins it as intended) | yes | a typo is silent and permanent in the mark | CLI J8 | refuse or warn on a never-named override id; do not raise the mark from override-only ids |
| F-4 | INFO | An indented override row and the heading `## 1b Task overrides` (no dot) are ignored silently | reproduced (J10, J11) | none | yes | the override does not apply (visible: the task stays in the view) | CLI J10, J11 | accept `## 1b` without the dot; refuse an indented `|` row inside the section |
| F-5 | FOLLOW-UP | No test pins three contract clauses: N1 write-then-rename (item 3), N2 SessionStart runs the sync (item 5), N3 the CLI apply's log line (item 4); each mutant leaves 94 of 94 green. The code does all three (verified) | reproduced (mutation driver) | items 3, 4, 5 (not in the evidence demands' test lists) | yes | none on the code; a regression would pass the gate | replace `os.replace(tmp, path)` by `path.write_bytes(data)` in `_write_atomic` (and the two others, section 9), run the two-file gate: `94 passed` | a torn-read test (a reader thread parses every file while `--apply` runs), a SessionStart-on-a-fresh-DIR test, `log_kinds == ["ok"]` after a CLI apply |
| F-6 | FOLLOW-UP | D3: Stop compares with the previous ERROR line, so a new episode of an old error (lock busy after successes) is silent while the view misses a new task | reproduced (`error, ok, ok, error`; second busy: exit 0, no stderr, #12 missing) | item 5 literal text supports D3 | yes | the owner learns at the next SessionStart only | section 7 | compare with the previous log line of any kind (the builder's one-line alternative) |
| F-7 | FOLLOW-UP | Two ledger inputs escape `Refused` on the CLI: `REGİSTERED` (U+0130: `re.IGNORECASE` matches, `.upper()` keeps it, `KeyError`) and 1,200 nested parens (`RecursionError`): exit 1, a traceback, no log line; nothing written. The hook catches both | reproduced (CLI + snippet R) | item 4 (exit 3 with the reason; one log line per run) | yes | none on state; hostile or absurd input only | snippet R | `re.ASCII` on EVENT_RE; a depth cap on parens (parse failure); `main` maps any other exception to exit 3 + a log line |
| F-8 | INFO | The off path does not catch a `RecursionError` from a 100,000-deep JSON payload: 25-line traceback, exit 1 | reproduced | item 7 (off: exit 0) | yes, hostile payload the harness never sends | none in practice | section 6 | `except Exception` in the off branch |
| F-9 | FOLLOW-UP | 14 stamp-less bold lines in `## 2.` are dropped with no header count and no `unknown` record; two close ids in the grammar's own word (L1486 #228, #225, #236; L1499 #246) | reproduced (a count over the ledger) | item 1 (unknown mentions recorded) arguably; these are not "dated lines" | yes | none today (those ids have no other event) | section 2 | count them in the plan header; record their id mentions as `unknown` |
| F-10 | FOLLOW-UP | The docstring (`scripts/task_sync.py:54-55`) says exit 3 means "nothing written" for "a failed backup or write"; a write failing after the first op leaves `10.json` written (the error text names the backup, honestly) | reproduced | none (doc accuracy) | yes | a reader trusts a false "nothing written" | a DIR with `11.json` as a directory, `--apply` of `#10 AND #11` | fix the docstring: a failed write leaves a partial apply; the backup and the next sync restore |
| F-11 | FOLLOW-UP | Backups and the log grow without bound; any ledger line that mentions an open task changes its description ("newest ledger line"), so most turns with a ledger edit write a tar | reproduced (42 tars in the race run) | none (the builder's NOT-done) | yes | disk, slowly | section 5 | retention: keep the newest N tars |
| F-12 | INFO | Descriptions carry ledger text verbatim, control-shaped literals included; subjects are slugs but keep instruction-shaped words; 0 such literals in today's view | reproduced (`inj.py`) | none | yes | reaches the model only through a TaskGet result | section 4 | optional: neutralize `<`, `>` and `[S1 ` in descriptions |
| F-13 | INFO | Premise correction (brief item 5): the task reminder and TaskList show `#id [status] subject` only; the description appears only in a TaskGet result | primary source (harness code) | n/a | n/a | narrows item 5's exposure | section 4 offsets | none |
| F-14 | INFO | D1 re-derived from the harness code: TaskCreate locks `DIR/.lock` (`.lock.lock`); TaskUpdate DOES lock, per task (`<id>.json.lock`, via `qke` -> `Ci` -> `Ue`), correcting the report's "no lock of its own" inference; delete takes no list lock; all writes are plain `writeFile`s; `flock` excludes none. Nothing the ledger holds is lost (stress run) | primary source + reproduced | item 3 (the lock, as built) | yes | hand state only, discarded by D4 anyway; a hand change written between the backup and the sync's writes is in no backup | `race.py` (section 5) | none required |
| F-15 | INFO | D4 confirmed: hand TaskCreate, TaskUpdate and delete are undone at the next Stop | reproduced (real hook) | item 3 ("the view owns the DIR" as designed) | yes | the coordinator's rules must change with the go-live | section 5 | CLAUDE.md task-tracking rules (the coordinator's, after this verify) |
| F-16 | INFO | `DIR/.lock` is opened with `O_CREAT` through a symlink, and the temp name `.<name>.tmp-<pid>` is predictable and opened without `O_EXCL`/`O_NOFOLLOW` (chmod follows too): a planted symlink in the root-owned DIR could redirect a write | reviewed statically | none | not reproduced (needs a hostile local writer) | hypothetical | none | `O_NOFOLLOW`, `O_EXCL` or `mkstemp` in the DIR |
| F-17 | INFO | SessionStart's `+N more:` hint is a repo-relative command; the session's cwd is `/home/user` | reproduced (the print) | none | yes | the hint fails as typed | section 7 | print the absolute paths |
| F-18 | INFO | The 27 extra ids: the grammar is faithful on all; the prose closes 14 and parks 8 of them outside the grammar's reach | reproduced (every mention read) | item 6 (differences named) | yes | the first view would show 22 finished or parked tasks as open | section 2 table | override rows (pre-apply P1) |
| F-19 | INFO | A range wider than 20, or reversed, binds only its two endpoints; the ids between get nothing, not even `unknown` | reproduced (A3d, A3e) | item 1 | yes | a silent partial close is possible | section 3 | record the middle ids as `unknown` |
| F-20 | INFO | Unicode: full-width digits are ids (`#１２` -> 12); U+017F spells DISPATCHED; `#99999999999999999999` creates that file and sets the mark to it; a FIFO ledger blocks the hook until the 30 s timeout | reproduced | none | yes | hypothetical input | section 6 | `re.ASCII`; an id ceiling (a parse failure above, say, 100000) |
| F-21 | UNVERIFIED | The harness's list id is `CLAUDE_CODE_TASK_LIST_ID` or a team name or `da()` or the leader team or `Y()`; `da()`/`Y()` are minified aliases I could not resolve. Here the DIR name equals the session id and the variable is unset (measured), so the hook's DIR is the harness's | primary source, partial | item 5 (the payload's session_id) | n/a | if they ever differ, the hook syncs a DIR nobody reads, silently | none | check after the first live Stop (P5) |
| F-22 | INFO | D2 confirmed (manifest line 20 moves; landing needs `--write`) | reproduced read-only | none | yes | CI red at the push without the regen | section 8 | the landing step (P6) |
| F-23 | INFO | The builder's gate, digest, migration and hook timings reproduce: set 4fbf35b43338 `94 passed` twice; digest 7c625d53cb41 on its ledger; the migration 0.178 s; SessionStart 12 lines | reproduced | items 3-6 | yes | none | sections 1, 2, 5 | none |

## 11. Reproduced, reviewed, skipped

- Reproduced through the real code: the gate (twice), the digest on the builder's ledger, the dry run on the current
  ledger and (read-only) on the live DIR, the migration and second run through the Stop hook, the backup, the bytes,
  SessionStart, D1 (stress), D4, the override and fail-closed cases, the hostile payloads, D3, the off-switch
  variants, the installer and settings comparisons, D2 (read-only), 20 mutants plus a control.
- Read from primary source (the harness binary): the reminder, TaskList and TaskGet renderings; the file store's
  create, update, delete, reset and lock paths; the list-id function (partly, F-21).
- Reviewed statically only: F-16.
- Skipped, and why: the whole `tests/test_vendored_manifest.py` (the brief forbids it; D2 by the read-only check);
  running the main tree's script (its off path appends to the main tree's `.jev/`); the DISK-PROBE (it writes the live
  DIR); the builder's other 41 mutants (10 reproduced, 8 new, 2 on the installer and settings); `report_lint` and
  `ap_screen` claims (report tooling this lane did not change); the owner's UI refresh (D5; not measurable here);
  anything on the PC.
- The live DIR was only copied and read. `/root/.claude/tasks/` holds only the live session DIR; the main tree has no
  `.jev/task-sync/`; my only main-tree write is this report. The live DIR's `310.json` changed at 18:16:59Z: the
  coordinator's TaskUpdate (its subject keeps the harness spelling `t321-scrub2-r1-repair (...)`), not a sync write.

## GATE

**Recommendation: MERGE-READY-WITH-FOLLOWUPS.** No finding meets the whole blocking predicate. The contract's items 1-7
hold through the real code on the real ledger; each finding with a contract mapping fails another condition: F-5 is
test strength on correct code (D-034: a follow-up), F-6 follows the contract's literal words, F-7 and F-8 change no
state and need hostile input, F-1's shapes occur 0 times in today's ledger. No CONTRACT-DEFECT. This recommendation
does not depend on anything I did not reproduce, except F-21 (the list id outside this session), which P5 checks.

Follow-ups for the issue queue (D-034): F-1, F-2, F-3, F-5, F-6, F-7, F-9, F-10, F-11; INFO items at the coordinator's
choice.

## MUST HOLD BEFORE THE FIRST LIVE `--apply`

- **P1. The override table, placed right.** Add `## 1b. Task overrides` BETWEEN `## 1. Tasks` and `## 2. LIVE`, never
  after `## 2.`, and add no `## ` heading after `## 2.` ever (F-2). Rows for the extra ids you decide (my per-id
  reading, section 2: 14 closed, 8 backlog, 5 open). Then dry-run and check: the header still says `14 dated lines
  outside '## 2.'` (a larger number means lines fell outside), `overrides` equals the rows added, and the view holds
  exactly the ids you intend (a typo'd row id is accepted and raises `.highwatermark` for good, F-3).
- **P2. Dry run, then apply, on the live DIR.** At 18:28:58Z (the ledger at 1662 lines, read-only dry run of the
  same bytes against the live DIR): `view=39 create=31 update=8 delete=3 hwm=314->346 digest=f2e42f9ce0f9` (39 = the
  38 plus #346, registered at 18:2xZ). The deletes are 308, 316, 317 (the harness-numbered copies of ledger #318,
  #334, #335, which come back as 318/334/335.json). The apply's log line must carry the dry run's digest, and the
  backup tar must exist after it.
- **P3. No hand TaskCreate in the turn of the first apply.** The harness's next id is 320 today (max of 319 and
  314, plus 1), and the migration creates 320.json for ledger #320; whichever write lands last wins (F-14).
- **P4. The rules change with it.** A hand TaskCreate, TaskUpdate or delete lasts until the next Stop (D4, measured);
  a task closes only by a ledger headline with a list word beside its id (`TASK #N CLOSED`) or an override row; the
  shapes in section 3 (for example `X CLOSED AND Y (TASK #N) DISPATCHED`) bind wrongly, so write the event next to
  its id.
- **P5. After the first live Stop:** the log line's `dir=` must be `/root/.claude/tasks/bdab799a-dc80-5933-9c9e-c80f206f9a17`
  (F-21), and one TaskList call must show the view.
- **P6. Before the push (landing, not the apply):** `vendored_manifest.py --write` from a clean worktree (D2).
