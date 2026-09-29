# VERIFY-K2: attack the file packs before they are registered on every tool call (task #353, D-106)

Written 2026-09-29 from 05:5xZ (clock read at 05:58:07Z) by the coordinator. Role: sandbox `adversarial-verifier`, model
opus. Do NOT spawn subagents. Return the WHOLE report as your final message (a report-file write is refused for
subagents).

The change under test: K2, landed GATED-PENDING-VERIFY and NOT registered: `scripts/filepacks.py`,
`tests/test_filepacks.py`, `tasks/briefs/jev-trim/K2-post-commit.patch` (not applied), and the additive
`codemap.file_entry` in `scripts/codemap.py` with its check in `tests/test_codemap.py`. The builder's account:
`tasks/briefs/jev-trim/K2-FILE-PACKS-report.md` (every claim a hypothesis; read its NOT done list and DISCREPANCIES 1 to 15
first). The contract: `tasks/briefs/jev-trim/K2-FILE-PACKS-brief.md` (items 1 to 8). The design:
`docs/research/findings/jev-trim/D105-DESIGN-v1.md` §10.3 (P1, P2).

Why it matters: once registered, `filepacks.py hook` runs on every Read, Edit, Write and Bash call of every session and
subagent, through `scripts/hook_context.py`, and its text reaches the model. The builder measured about 100 ms per call
and, on the replay, a median of 30 injections and 27 KB per context window. A wrong pack misleads; a slow or hung hook
stalls every call; a hole in its boundary puts an untracked file's text in front of the model.

## What to attack (the full frozen contract, never only the builder's cases)

1. **Premise.** Re-run the PREMISE block below; on a difference, stop and report CONTRACT-INVALID.
2. **The boundary (the project's rule 14, security).** Only files tracked at the last build reach the model. Build your
   own hostile shapes beyond the builder's: symlinked directories on the path to a pack, `TRACKED.txt` edited or swapped
   between calls, a pack whose `rel` field names another file, a Bash command whose argument reaches an untracked file
   through `cd`, `pushd`, `~`, `$HOME`, a glob or a variable, a file tracked at build time and untracked (or replaced by a
   link) since. Name every shape you tried and its result.
3. **Hangs and time.** The builder's NOT done 4 (AF-AP-70: `_code_part` checks the code pack and the working file by
   name, then codemap's readers reopen them by name; a FIFO swapped in between stalls the hook until the wrapper's 55 s
   timeout). Reproduce it; measure the window; find any other path to a hang or a long stall (a huge pack, a huge
   `TRACKED.txt`, a lock held by a dead process, a deep `cd` chain). Measure the hook's cost through the real wrapper
   on your own sample of recorded payloads (p50, p95, max) and against the System-1 hook's on the same sample.
4. **The Bash parser.** Which files does a real command count as touched? Build cases around the System-1 parser's
   known limits: `cd` inside `$(...)` or a subshell, `&&` chains across directories, `xargs`, `find -exec`, `git show
   REV:path`, a reader word as an argument (`timeout 5 cat x`, `sudo cat x`, `env cat x`), here-strings, process
   substitution. For each, is the result right, a miss, or a wrong file?
5. **The packs are right.** For a sample of at least 20 tracked files (code and documents, often and rarely named),
   compare the pack against an oracle you build yourself from the sources at the build's commit: the newest three
   mentions per source, the registry ids, the headlines, the snippets, the briefs by last commit, the commit subjects.
   Report every difference.
6. **The entry is right.** For a sample of Edit, Read (with and without `offset` and `limit`) and Bash payloads: the code
   part (symbol, callers, risk, tests), the STALE mark on a changed file, the budget cut on a line boundary, the once per
   window keys, the reset on compact, resume and clear.
7. **The patch.** Apply `K2-post-commit.patch` in a clone; check that it never blocks or fails a commit (a broken
   builder, a held lock, a burst of commits, a missing `python3`), that it runs one build at a time, and that the
   never-a-gate screen stays clean.
8. **The registration text.** The report's two entries (the PreToolUse group and the SessionStart reset) and the
   installer spelling it proposes: do they match what the tests run (`REG_PRE`, `REG_RESET`), and what breaks in
   `tests/test_session_hooks.py` when they are added (the report lists the edits; check the list is complete)?
9. **Mutation.** Re-run the builder's 55 mutants on the final bytes (40 in `tests/test_filepacks.py`, 15 in
   `tests/test_codemap.py`), then write your own for the clauses no mutant covers, and report killed and survived with the
   test that kills each.

## Rules

- Work in a clean detached worktree under your own scratch dir at the PIN the dispatch names
  (`git -c core.hooksPath=/dev/null worktree add -q --detach <W> <PIN>`), and remove it at the end. No git write in the
  shared tree; no outward action, no PC bridge, no subagent.
- NEVER register the hook: never touch `/home/user/.claude/settings.json`, the repo's `.claude/settings.json` or
  `scripts/install_session_hooks.py` in the shared tree, and never write under the live `.jev/filepacks*` or
  `.jev/codemap`. Build packs into a state directory of your own.
- Never read a secret file (`.pc-bridge.env`, any `*.env`, any key file); a secret in a test is a fake string built at run
  time. When you read transcripts, read only compaction boundaries and `tool_use` inputs, never a thinking block, and
  print only counts, bytes and file paths.
- `--basetemp` as a pytest ARGUMENT outside any work tree, never `PYTEST_ADDOPTS`; a long gate in ONE foreground call;
  counts pasted from `scripts/test_summary.sh` with their set ids; stamps from `date -u`; commits cited by origin id or
  subject. Before a mutation driver counts kills, run its control (AF-AP-223).

## Report

Every observation with no severity filter; then the blocking predicate (D-034: only a CORE-BLOCKING finding, one that
shows the headline capability is fake, re-opens the build; a security-boundary hole that puts an untracked file's text
in front of the model counts as core-blocking here); then a gate recommendation (MERGE-READY /
MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID); and a separate list of what must hold before registration.

## PREMISE — MEASURED at authoring (2026-09-29, main tree; origin 7db59b9 plus the K2 files, uncommitted then)

Printed by `bash scripts/premise_block.sh` from the main tree before the landing commit; the dispatch names the PIN
(the landing commit's origin id). The `[rc=1]` after the three zero counts is grep's exit code when nothing matches:
the hook is registered nowhere. The coordinator's gate in a clean worktree, on the same bytes: `3 files
set=804c19143d13`, `pytest-summary: 255 passed in 369.58s (0:06:09)` (the builder's: 255 passed, twice). Expected to
differ: nothing.

```
$ git merge-base --is-ancestor 7db59b9 HEAD && echo 7db59b9-is-an-ancestor-of-HEAD
7db59b9-is-an-ancestor-of-HEAD
$ sha256sum scripts/filepacks.py tests/test_filepacks.py tasks/briefs/jev-trim/K2-post-commit.patch scripts/codemap.py tests/test_codemap.py | cut -c1-16,65-
46ee3aea2f1e428b  scripts/filepacks.py
20688549adc7c296  tests/test_filepacks.py
71ba4c2c0cec81ab  tasks/briefs/jev-trim/K2-post-commit.patch
ea28c5add97fac24  scripts/codemap.py
a1b9fa4652c47181  tests/test_codemap.py
$ grep -n '^REG_PRE\|^REG_RESET' tests/test_filepacks.py | cut -c1-60
8:REG_RESET). State never touches the real .jev/: AF_FILEPAC
40:REG_PRE = ("[ -f $CLAUDE_PROJECT_DIR/scripts/filepacks.py
43:REG_RESET = ("[ -f $CLAUDE_PROJECT_DIR/scripts/filepacks.
$ grep -c 'filepacks' .claude/settings.json scripts/install_session_hooks.py /home/user/.claude/settings.json
.claude/settings.json:0
scripts/install_session_hooks.py:0
/home/user/.claude/settings.json:0
[rc=1]
$ grep -n 'def file_entry\|^FILE_SYMBOLS' scripts/codemap.py
948:FILE_SYMBOLS = 8                    # symbols a file-level entry names
951:def file_entry(path, line=None, end_line=None, root=None):
$ bash scripts/pc_suite.sh set-id -- tests/test_codemap.py tests/test_filepacks.py tests/test_system1_context.py | tail -1
3 files set=804c19143d13
```
