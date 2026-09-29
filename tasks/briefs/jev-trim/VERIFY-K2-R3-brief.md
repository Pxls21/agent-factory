# VERIFY-K2 round 3: re-check B1, B2, B3 and the round's other items (task #353)

Role: the VERIFY-K2 verifier, resumed (sandbox adversarial-verifier, Opus 5.5). Do NOT spawn subagents. Return the
whole report as your final message (your hand-back); write no report file.

K2 round 3 landed at a9e5389 ("K2 round 3 landed ..."), GATED-PENDING-VERIFY. The owner asked for this third round
(D-111), past D-031's one-repair budget. It answers your round-2 report (`tasks/briefs/jev-trim/VERIFY-K2-R2-report.md`):
its B1, B2 and B3, the seven checks its mutation run found missing (its finding 4) and the stale documents (its
finding 8). Its report of record is `tasks/briefs/jev-trim/K2-R3-report.md`: read the coordinator note at its top,
then its NOT done (1 to 11) and DISCREPANCIES (1 to 11). Treat every claim there as a hypothesis. The hook is still
NOT registered; the registration stays the unapplied `tasks/briefs/jev-trim/K2-registration.patch` with
`tasks/briefs/jev-trim/K2-post-commit.patch`.

The coordinator's landing gate, in the shared tree with the round-3 patch applied: `1 files set=db64e610236b` (`tests/test_filepacks.py`) `pytest-summary: 167 passed in 232.81s (0:03:52)` and
`pytest-summary: 167 passed in 251.45s (0:04:11)`; `2 files set=395f8af3a0ce` (`tests/test_codemap.py
tests/test_system1_context.py`) `pytest-summary: 197 passed in 403.51s (0:06:43)` and `pytest-summary: 197 passed in
392.65s (0:06:32)`.

## SCOPE (the re-check, narrow)

1. **Premise.** Re-run the block below with `bash scripts/premise_block.sh` from `/home/user/agent-factory`; on a
   difference, stop and report CONTRACT-INVALID with the diff.
2. **B1 through the real patched hook.** Re-run your `probe_callers2.py` (scratch `vk2r2/`) at the PIN: the untracked
   function name and path are absent, the tracked caller and test present (the control). Then attack the reader-side
   filter: the exact-line match on TRACKED.txt and its newline and NUL guard (`_tracked_only`); a caller file untracked
   after the build (the report's NOT done 9); the total dropped, never recounted, whenever the filter removes a sampled
   caller (its DISCREPANCY 1); the names drawn from the file itself (its DISCREPANCY 2).
3. **NOT done 1: uncommitted text in a TRACKED caller or test file.** The builder's own probe shows it reaching the
   model (GitNexus indexes a file's working bytes; TRACKED.txt vouches for a path, not its bytes). Your round-2 report
   rated that class FOLLOW-UP. Re-derive it on round 3's bytes through the real hook, and grade it under D-034: does
   the rating stand, and why?
4. **B2.** Re-run the untracked shape (`probe_f1b.py ... sg-untracked`) and the tracked-revert shape (`probe_f1.py ...
   sg-tracked`) at the PIN: 0 canary bytes on Edit, Read and `cat`. Attack the clause: it reads the graph that
   `symbols_from` names, and a pack with symbols but no source graph is withheld (the check `sourceless-symbols`). The
   stamp-then-read window (NOT done 7): measure it if you can, or say why not.
5. **B3.** `tests/test_filepacks.py` gives 0 failed in a worktree WITHOUT the post-commit patch and in one WITH it
   applied, and the negative control reads the unpatched hook from a fixed commit, never the working copy.
6. **The seven ported checks and the mutants.** Run your `mutdrv3.py` against round 3's checks, its control first
   (AF-AP-223: a `--basetemp` parent that no longer exists makes every mutant error at setup and read KILLED). The
   builder's claim: your 57 mutants against 72 checks, every one killed except `pre-image-unchecked`, which it calls
   equivalent while `UNPATCHED_AT`'s hook is the patch's pre-image (NOT done 4). Write new mutants for round 3's new
   clauses (the caller and test filter, the stale-graph clause, the fixed-commit negative control).
7. **The stale documents.** `docs/research/findings/jev-trim/D105-DESIGN-v1.md` and
   `tasks/briefs/jev-trim/K2-R2-report.md` carry dated notes; the round-2 record is annotated, not rewritten.
8. **The two patches.** Apply `K2-post-commit.patch` and `K2-registration.patch` in a clean worktree at the PIN and
   re-run their proof. `tasks/briefs/labeling/LS-B10-registration.patch` changes the same three files
   (`.claude/settings.json`, `scripts/install_session_hooks.py`, `tests/test_session_hooks.py`): do the two
   registration patches conflict at the PIN? (A question: the coordinator rebases whichever lands second.)
9. **Gates at the PIN**, in your own worktree (never the shared tree), `--basetemp` as a pytest ARGUMENT outside every
   work tree, counts pasted from `scripts/test_summary.sh` with set ids, each call under 10 minutes:
   `tests/test_filepacks.py` twice (`1 files set=db64e610236b`); `tests/test_codemap.py tests/test_system1_context.py`
   (`2 files set=395f8af3a0ce`).
10. **What must hold before registration**, rewritten for round 3's bytes.
11. **Gate recommendation** under D-034's blocking predicate. A boundary hole that puts untracked text in front of the
    model counts as core-blocking.

Out of scope, on GitHub issue #83: your round-2 findings 5, 6, 7, 9, 12 and 15.

## STANDING RULES

- A clean detached worktree at the PIN under your scratch dir, removed at the end; no git write in the shared tree (a
  worktree add and remove, hooks off, is the one exception); no outward action, no PC bridge, no subagent.
- NEVER register the hook: never touch `/home/user/.claude/settings.json`, the repo's `.claude/settings.json` or
  `scripts/install_session_hooks.py` in the shared tree, or the live `.jev/filepacks*` and `.jev/codemap`.
- Never read a secret file (`.pc-bridge.env`, any `*.env`, any key file); a secret in a test is a fake built at run time.
- From transcripts, read only compaction boundaries, record types and `tool_use` inputs, never a thinking block. Print
  only counts, bytes and paths.
- A long gate in ONE foreground call; stamps from `date -u`; commits cited by origin id or subject.
- Never a top-level `cd` (AF-AP-249): use `git -C`, absolute paths or a `( cd … )` subshell.
- Never `pkill -f` a pattern your own command line matches; stop every process you start, by pid.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- This is defensive testing of the owner's own tooling: each probe is a bound to measure, never an exploit.

Deliver as before: every observation with no severity filter, the blocking predicate, a gate recommendation, and the
list of what must hold before registration. Head the report "## Round 3" with "Written 2026-09-29 from <date -u stamp>".

## PREMISE — MEASURED at authoring (2026-09-29, main tree; PIN origin a9e5389)

Printed by `bash scripts/premise_block.sh` from the main tree. The K2 files are byte-identical to the PIN, the two
patches are round 2's bytes (round 3 did not need to change them), and the hook is registered nowhere (the `[rc=1]` is
grep's exit code for three zero counts). Expected to differ: nothing.

```
$ git merge-base --is-ancestor a9e5389 HEAD && echo a9e5389-is-an-ancestor-of-HEAD
a9e5389-is-an-ancestor-of-HEAD
$ git log -1 --format=%s a9e5389 | cut -c1-70
K2 round 3 landed (task #353; GATED-PENDING-VERIFY): no untracked call
$ sha256sum scripts/filepacks.py tests/test_filepacks.py scripts/codemap.py tests/test_codemap.py tasks/briefs/jev-trim/K2-registration.patch tasks/briefs/jev-trim/K2-post-commit.patch | cut -c1-16,65-
18c8360473ba0b6d  scripts/filepacks.py
3857536f23325e5d  tests/test_filepacks.py
8be917715cd2a5c9  scripts/codemap.py
76e31571e8008a4d  tests/test_codemap.py
3e8b979120d0638a  tasks/briefs/jev-trim/K2-registration.patch
71ba4c2c0cec81ab  tasks/briefs/jev-trim/K2-post-commit.patch
$ git diff --stat a9e5389 HEAD -- scripts/filepacks.py tests/test_filepacks.py scripts/codemap.py tests/test_codemap.py tasks/briefs/jev-trim/K2-registration.patch tasks/briefs/jev-trim/K2-post-commit.patch | wc -l
0
$ grep -c 'filepacks' .claude/settings.json scripts/install_session_hooks.py /home/user/.claude/settings.json
.claude/settings.json:0
scripts/install_session_hooks.py:0
/home/user/.claude/settings.json:0
[rc=1]
$ ls /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/mutdrv3.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/probe_callers2.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/probe_f1.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/probe_f1b.py | wc -l
4
$ bash scripts/pc_suite.sh set-id -- tests/test_filepacks.py | tail -1
1 files set=db64e610236b
$ bash scripts/pc_suite.sh set-id -- tests/test_codemap.py tests/test_system1_context.py | tail -1
2 files set=395f8af3a0ce
```
