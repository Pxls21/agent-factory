# VERIFY-LS-B7: attack the task-list sync before it goes live (task #339, D-102)

Role: adversarial-verifier (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/labeling/VERIFY-LS-B7-report.md`
(write it incrementally). If the harness refuses a report-file write, return the rest of the report as the text of your
final message; never work around the refusal.

Authored 2026-09-28 16:3xZ by the coordinator.

The change under test: the LS-B7 lane's working-tree files in the main tree `/home/user/agent-factory` (uncommitted; their
sha256 prefixes are in the premise): `scripts/task_sync.py`, `tests/test_task_sync.py`, `scripts/install_session_hooks.py`,
`tests/test_session_hooks.py`, `.claude/settings.json`. Contract: `tasks/briefs/labeling/LS-B7-brief.md` (items 1-7).
The builder's report: `tasks/briefs/labeling/LS-B7-report.md`; its claims are hypotheses. The owner's ruling behind it:
D-102 in `docs/08_DECISION_LOG.md` (the task list becomes a view of the ledger, kept in sync by a script, not by hand).

Why it matters: once live, this script owns the harness's task list for the whole session. A wrong close hides open work
from the owner and the coordinator; a wrong open keeps dead work in every task reminder; a write outside the tasks root,
a torn write or a blocked Stop would damage the session itself.

Your copy: never write the main tree, its `.jev/`, or `/root/.claude/`. Make a scratch copy under `/tmp/vlsb7/`:
`git -C /home/user/agent-factory archive HEAD scripts tests .claude/settings.json todo | tar -x -C /tmp/vlsb7/repo` (add a
path only if a test needs it), then copy the five lane files on top. Run the live DIR's copy with `CLAUDE_CONFIG_DIR`
pointed at your scratch, as the builder did. The off switch `/home/user/agent-factory/.jev/task-sync-off` stays in place.

## WHAT TO ATTACK (report every observation; no severity filter)

1. **The grammar.** Mis-bound words (a word that belongs to another id on the same line; a possessive `#NNN's`; a range
   `#291-#293`; a list `#200 + #167`); a later mention that reopens a closed task; a close that a later REGISTERED undoes;
   two lines in one ten-minute bucket; lines outside `## 2.`; `(backlog)` and its conditional forms (`#329 (after
   SCRUB2-R1 lands)`); the override table (malformed rows, duplicate ids, an unknown status, a row for an id the ledger
   never names): does each fail closed with exit 3 and write nothing?
2. **The view on the real ledger.** Re-run the builder's migration on a fresh copy of the live DIR and reproduce its
   plan digest. Read the 27 extra ids of its section 4 against the ledger yourself: is each open status the grammar's
   honest reading?
3. **The sync.** Idempotence; the backup; write-then-rename (no torn file); the `.highwatermark`; the builder's D1 (its
   `flock` does not exclude the harness, which locks with a `.lock.lock` directory): what exactly can happen when a
   harness TaskCreate or TaskUpdate races a sync, and is anything lost that the next sync does not restore? D4 (a
   hand-made task is deleted at the next Stop): confirm it, and say what a coordinator TaskUpdate does between two syncs.
4. **Fail closed.** An unreadable ledger, a parse failure, an empty view: nothing written, exit 3. A DIR outside the
   tasks root refused without `--allow-dir`. **A hostile `session_id` in the Stop payload** (`../x`, an absolute path, a
   NUL, a very long value): does any reach a path outside the tasks root?
5. **What the harness shows the model.** The task reminder repeats each task's subject and description into the
   coordinator's context. Can ledger text put control-shaped text there (a `<system-reminder>` literal, a fake
   `[S1 …]` stamp, an instruction-shaped line)? The ledger quotes lanes and the owner. Measure what reaches the files.
6. **The hooks.** Never exit 2, never `decision: block`, nothing on stdout from Stop; exit 1 with one stderr line only
   for a new error (and the builder's D3 reading of "new"); the off switch as the first statement of each hook (inert
   while present, also mid-build); the 30-second timeouts; SessionStart's print (at most 12 lines).
7. **The installer.** `our_hooks()` and `.claude/settings.json` carry both hooks and change no existing hook; the
   builder's D2 (the vendored manifest row moves when this lands): confirm with the read-only check.
8. **Mutation.** Reproduce at least five of the builder's 51 mutants as FAILED tests, including one each for the
   grammar, fail-closed and the off switch; add a mutant for each contract clause its set does not cover.

## GATE

Apply the blocking predicate of skill `contract-gate` (contract-mapped, reproduced through the real code path, materially
effective, a concrete discriminator, in-boundary) and D-034 (a finding re-opens the build only if it is CORE-BLOCKING;
the rest become follow-ups). One recommendation: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID,
each blocking finding with its reproduction command. Name separately anything that must hold before the first live
`--apply` (the coordinator runs it after your verdict).

## BOUNDARY

READ everything. WRITE only your report and scratch under `/tmp/vlsb7/` (removed at the end). No git writes. Never write
the main tree, `/root/.claude/tasks/` or the main tree's `.jev/`.

## STANDING RULES

- No PC bridge, no outward-facing action.
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, and the GH_TOKEN and GITHUB_TOKEN variables.
- Other lanes hold files in the main tree (`.lanes-live` lists them): SCRUB2-R1 and LS-B9 are live. Touch none.
- The disk is shared (see the premise; the lane gate refuses below 1,500 MB): scratch under 150 MB in all; a private
  `--basetemp` for every pytest run; never run the whole `tests/test_vendored_manifest.py`.
- Test counts are pasted from `scripts/test_summary.sh` with their set ids. Stamps are substituted from `date -u`,
  never typed.
- Long commands in one foreground call, each under 10 minutes; kill by pid only.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.

## PREMISE — MEASURED at authoring (2026-09-28 16:3xZ, the main tree; `bash scripts/premise_block.sh`)

```
$ git rev-parse --short HEAD
c9889ee
$ git status --porcelain -- scripts/task_sync.py tests/test_task_sync.py scripts/install_session_hooks.py tests/test_session_hooks.py .claude/settings.json tasks/briefs/labeling/LS-B7-report.md
 M .claude/settings.json
 M scripts/install_session_hooks.py
 M tests/test_session_hooks.py
?? scripts/task_sync.py
?? tasks/briefs/labeling/LS-B7-report.md
?? tests/test_task_sync.py
$ sha256sum scripts/task_sync.py tests/test_task_sync.py scripts/install_session_hooks.py tests/test_session_hooks.py .claude/settings.json tasks/briefs/labeling/LS-B7-report.md | cut -c1-16,65-
8f6c4626c3728e02  scripts/task_sync.py
5151fb0d0888310f  tests/test_task_sync.py
b78e189d0ac5b7db  scripts/install_session_hooks.py
dddd30002144af50  tests/test_session_hooks.py
03b9e1e1b04d34d7  .claude/settings.json
229c96d812017ea5  tasks/briefs/labeling/LS-B7-report.md
$ git diff --stat -- scripts/install_session_hooks.py tests/test_session_hooks.py .claude/settings.json
 .claude/settings.json            |  18 +++++++
 scripts/install_session_hooks.py |  27 +++++++---
 tests/test_session_hooks.py      | 105 ++++++++++++++++++++++++++++++++++++---
 3 files changed, 135 insertions(+), 15 deletions(-)
$ wc -l scripts/task_sync.py tests/test_task_sync.py
  815 scripts/task_sync.py
  571 tests/test_task_sync.py
 1386 total
$ ls -la .jev/task-sync-off
-rw-r--r-- 1 root root 148 Sep 28 14:58 .jev/task-sync-off
$ ls /root/.claude/tasks/bdab799a-dc80-5933-9c9e-c80f206f9a17/
289.json
295.json
297.json
308.json
310.json
313.json
315.json
316.json
317.json
318.json
319.json
$ cat /root/.claude/tasks/bdab799a-dc80-5933-9c9e-c80f206f9a17/.highwatermark
314$ grep -c '' todo/BUILD-TASKLIST.md
1656
$ grep -n '^## ' todo/BUILD-TASKLIST.md | head -8
25:## 0. STATUS (updated 2026-09-08 00:5xZ — the four-way proof count pasted from proofs/ledger.json)
372:## 1. Tasks
420:## 2. LIVE ledger (append-only sync blocks; newest first)
$ df -m / | tail -1
/dev/vda          258020 36354      1585  96% /
```

The ledger has no `## 1b. Task overrides` section yet: the coordinator adds it for the 27 ids after your verdict, before
the first live `--apply`. The builder's gate, quoted from its report (your item 8 re-runs it): `2 files set=4fbf35b43338`,
`94 passed` three times; mutants `EXPECTED=44 KILLED=44` (task_sync.py) and `EXPECTED=7 KILLED=7` (installer and settings).
