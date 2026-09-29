# VERIFY-K2 round 2, resumed: a fresh verifier continues from the stopped one's scratch (task #353)

Written 2026-09-29 11:1xZ by the coordinator, for a fresh sandbox `adversarial-verifier` (model opus). Dispatched only on
the owner's word: the harness refuses to resume a user-stopped agent and allows a new one only on the owner's explicit
ask (AF-AP-245). This is D-098's pattern: a fresh agent continues from the saved scratch; the round-2 message below
stays the contract. Do NOT spawn subagents. Return the WHOLE report as your final message.

## What happened

VERIFY-K2's original verifier (round 1: `tasks/briefs/jev-trim/VERIFY-K2-report.md`) was resumed at 09:46Z for round 2
at PIN origin f605913 ("K2 round 2 landed ..."). At 10:35:28Z the owner interrupted the coordinator's turn to run a
local command, and that stopped the verifier (163 tool calls; claude-opus-5-5 on all 430 assistant records; 0 refusal
stops). It wrote no report and no recommendation. Its interim results, read by the coordinator from its tool outputs,
are HYPOTHESES for you to reproduce, never findings:
- its mutation control on the round-2 code: `2 files set=bd8d7c79afbe`, 70 passed;
- the builder's 102 mutation checks: 102 passed;
- the TAIL of its own round-2 grading output (`mutdrv2.py`; the head was not read) shows seven mutants KILLED: `remote-mode-off`, `remote-never-ends`, `words-cap-2`,
  `files-max-1`, `frame-close-any`, `squote-script-as-data`, and one whose name the output cut (killed by
  `n2_grep_attached`);
- 0 of 2,511 recorded commands naming `scripts/pc.sh` lost the file's pack from round 1 to round 2;
- it was stopped while grading survivors on the builder's checks, then its old mutants.

Its scratch survives at `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2/` (probes such as
`probe_p6b.py`, `probe_fifo2.py`, `quad2.py`, `shapes_real.py`, `probe_graphs2.py`; drivers `mutdrv.py` and
`mutdrv2.py`; state dirs; worktrees `wt`, `wt1`, `wtg`, `ptree`). Reuse what helps: run each tool's CONTROL first
(AF-AP-223: a `--basetemp` parent that no longer exists makes every mutant error at setup and read KILLED), and remove
every worktree there that you or it made before you report (`git worktree list` names them).

## The contract: the round-2 message, verbatim

> VERIFY-K2 round 2: check K2 round 2, the repair your report asked for. It landed on origin as f605913. The hook is still NOT registered.
>
> What happened since your report (07:3xZ):
> - The coordinator accepted MERGE-READY-WITH-FOLLOWUPS with your condition and sent the rest back as one focused repair (D-031): `tasks/briefs/jev-trim/K2-R2-brief.md`, built by the original K2 builder.
> - It landed as "K2 round 2 landed (task #353; GATED-PENDING-VERIFY)…", origin f605913, which is the PIN. After it come a ledger-only retro commit (a2b4187) and transcript digests (34977e4).
> - The builder's report: `tasks/briefs/jev-trim/K2-R2-report.md`. Treat every claim there as a hypothesis; read its NOT done 1 to 9 and DISCREPANCIES 1 to 12 first. Your round-1 report is `tasks/briefs/jev-trim/VERIFY-K2-report.md`.
> - The coordinator's gate in a clean worktree: `3 files set=804c19143d13`, `pytest-summary: 326 passed in 500.42s (0:08:20)`.
>
> Round 2's claims to attack:
> 1. **F1 is closed whatever the build did.**
>    - How: the build writes BLOBS.txt from its `ls-tree`, and `_code_part` shows a code part only when the code pack's blob equals the file's blob at the build's commit.
>    - Re-run your `probe_p6.py` scenario, with and without the post-commit patch. Then build new shapes: a tracked file with uncommitted edits (its DISCREPANCY 8: no code part until a commit); a BLOBS.txt edited or missing or linked; a code pack whose blob field is forged to match; the callers sample naming an untracked caller (its NOT done 5).
> 2. **F2:** codemap's five readers use System-1's `open_regular`. Re-run your FIFO race: it claims 0 of 40 stalls per target, where you measured 10 or 11. Check that the builder side is unchanged byte for byte, and whether `_load_pack`'s new O_NOFOLLOW changes any real caller.
> 3. **F3:** the parse is linear. It claims 336 ms at 3,000 pairs. Look for any new quadratic or cubic path in `_Words`, `_frames` or `bash_paths`, including deep frame nesting and many frames.
> 4. **F4 and F5:** your 85-case strace oracle now gives 60 right, 25 misses and 0 wrong, by its claim. Re-run it, then build new shapes against the frame scan: a `case` pattern's `)` inside a subshell (NOT done 4 names it), unbalanced quotes, nested `$( … $( … ) … )`, backticks inside `$( )`, a heredoc under `ssh` (NOT done 4), `pushd` and `popd` imbalance.
> 5. **Your 17 checks and its 30 new mutants.** Do your 17 check names kill your own 17 mutants? It re-anchored them on its own text, so check whether the anchors still mean what yours did. Then run the mutation set with its control first (AF-AP-223), and write new mutants for round 2's new clauses: BLOBS.txt, the frames, the remote blanking, the grep pattern and the word cap.
> 6. **The registration patch** (`tasks/briefs/jev-trim/K2-registration.patch`). Apply it with the post-commit patch in a clean worktree at the PIN. Does it give its claimed 137 passed on `tests/test_session_hooks.py` and `tests/test_search_intercept.py`? Are the "installed 9" count and the new older-spelling test right? What else breaks, for example the whole `tests/test_vendored_manifest.py` after a regeneration run in a scratch worktree only (disk permitting)? And after registration, does anything run on the coordinator's own session start that should not?
> 7. **What must hold before registration**, rewritten for round 2's bytes.
>
> Before reusing your `vk2/` scratch (probes, `mutdrv.py`, the `state` dirs), run each tool's control. The state dirs were built at d812c9b, before BLOBS.txt existed, so rebuild them at the PIN.
>
> Standing rules, unchanged:
> - A clean detached worktree at the PIN under your scratch dir, removed at the end.
> - No git write in the shared tree; no outward action, no PC bridge, no subagent.
> - NEVER register the hook: never touch `/home/user/.claude/settings.json`, the repo's `.claude/settings.json` or `scripts/install_session_hooks.py` in the shared tree, or the live `.jev/filepacks*` and `.jev/codemap`.
> - Never read a secret file, and build fake test secrets at run time.
> - From transcripts, read only compaction boundaries and `tool_use` inputs, never a thinking block. Print only counts, bytes and paths.
> - `--basetemp` as a pytest ARGUMENT outside any work tree; a long gate in ONE foreground call.
> - Counts pasted from `scripts/test_summary.sh` with set ids; stamps from `date -u`; commits cited by origin id or subject.
> - Never `pkill -f` a pattern your own command line matches (the env-tool-quirks rule you hit last round); stop any process you start.
> - This is defensive testing of the owner's own tooling: each probe is a bound to measure, never an exploit.
>
> Deliver as before: every observation with no severity filter, the blocking predicate (D-034; a boundary hole that puts untracked text in front of the model counts as core-blocking), a gate recommendation, and the list of what must hold before registration. Return the report as your final message, headed "## Round 2" with "Written 2026-09-29 from <date -u stamp>".

## PREMISE — MEASURED at authoring (2026-09-29, main tree; PIN origin f605913)

Printed by `bash scripts/premise_block.sh` from the main tree. The K2 files are byte-identical to the PIN, and the hook
is registered nowhere (the `[rc=1]` is grep's exit code for three zero counts). Expected to differ: nothing.

```
$ git merge-base --is-ancestor f605913 HEAD && echo f605913-is-an-ancestor-of-HEAD
f605913-is-an-ancestor-of-HEAD
$ git log -1 --format=%s f605913 | cut -c1-70
K2 round 2 landed (task #353; GATED-PENDING-VERIFY): the stale-index h
$ sha256sum scripts/filepacks.py tests/test_filepacks.py scripts/codemap.py tests/test_codemap.py tasks/briefs/jev-trim/K2-registration.patch tasks/briefs/jev-trim/K2-post-commit.patch | cut -c1-16,65-
017ce2be467fbf53  scripts/filepacks.py
c844aeeb8a4a9097  tests/test_filepacks.py
f504849bf1d4100a  scripts/codemap.py
76e31571e8008a4d  tests/test_codemap.py
3e8b979120d0638a  tasks/briefs/jev-trim/K2-registration.patch
71ba4c2c0cec81ab  tasks/briefs/jev-trim/K2-post-commit.patch
$ git diff --stat f605913 HEAD -- scripts/filepacks.py tests/test_filepacks.py scripts/codemap.py tests/test_codemap.py tasks/briefs/jev-trim/K2-registration.patch tasks/briefs/jev-trim/K2-post-commit.patch | wc -l
0
$ grep -c 'filepacks' .claude/settings.json scripts/install_session_hooks.py /home/user/.claude/settings.json
.claude/settings.json:0
scripts/install_session_hooks.py:0
/home/user/.claude/settings.json:0
[rc=1]
$ ls /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2/mutdrv2.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2/probe_p6b.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2/probe_fifo2.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2/quad2.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2/shapes_real.py | wc -l
5
$ bash scripts/pc_suite.sh set-id -- tests/test_codemap.py tests/test_filepacks.py tests/test_system1_context.py | tail -1
3 files set=804c19143d13
```
