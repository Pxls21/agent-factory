# K2 round 4: provenance by blob, the redesign round (task #353, D-115)

Role: the original K2 builder (sandbox code-implementer), resumed. PIN: origin 14ecd8b. Authored 2026-09-30 by the
coordinator. Read first: D-115 in `docs/08_DECISION_LOG.md` (the owner's deadlock break; its item 4 is this round);
skill `contract-gate` §4, "The deadlock break"; `tasks/briefs/jev-trim/VERIFY-K2-R3-report.md` (R3-1 and its fix, then
the FOLLOW-UPs). Do NOT spawn subagents.

## WHY THIS ROUND IS A REDESIGN (the round table, D-115)

| Round | Verify and recommendation | Blocker | The fix the next round tried |
|---|---|---|---|
| 1 | VERIFY-K2: MERGE-READY-WITH-FOLLOWUPS on one condition | F1: a stale index let an untracked file's text through | round 2: the post-commit build; a caller kept only when its path is a TRACKED.txt line |
| 2 | VERIFY-K2 round 2: NOT-READY | B1: untracked callers reach the model through a tracked file's code part (B2, B3 beside it) | round 3: the path filter made exact, the total dropped when a caller is removed, the code part withheld when its graph is not fresh |
| 3 | VERIFY-K2 round 3: NOT-READY | R3-1: a caller's name from a file's untracked era reaches the model after the file is committed with other text | this round |

One class, three rounds: untracked text reaches the model through the derived code index. Each fix filtered the
graph's output BY PATH after the fact, and the leak moved to the next path. The assumption the blockers keep hitting:
"a name is safe when its file's path is tracked". A tracked path does not mean the graph read committed bytes. This
round drops that assumption, as R3-1's own fix (your NOT done 1 direction) proposes, and makes the blob the rule for
every caller and test name a pack shows.

## CONTRACT (contract revision 4; a new budget under D-115)

1. **Provenance by blob.** At build time, record for each caller file and each test file a pack names: the blob the
   graph indexed (the graph's indexed hash, as `_fresh` reads it for the callee file today) and the file's committed
   blob in the tree the build names (BLOBS.txt). A reader keeps a caller or test name only when the two are equal. A
   file untracked at the build has no committed blob, so none of its names show; a file whose indexed bytes differ from
   its committed blob shows none of its names; a dropped name drops the total, as round 3 does. The path filter may stay
   as a second check; the blob tie is the guard.
2. **The class test.** Committed tests plant a canary identifier in (a) an untracked file outside the refresh paths, (b)
   an untracked file inside them with the refresh held behind its lock, and (c) the untracked era of a file later
   committed with other text. Through the real patched post-commit hook, the canary appears in no pack at any point.
   Each shape has a leak control: the same test with the blob comparison disabled shows the canary, so the test proves
   the guard acts.
3. **R3-1's shapes as committed real-hook tests:** the verifier's `late-outside` and `late-track` shapes of `probe_r3.py`,
   red at the PIN and green after.
4. **Closed with it:** NOT done 1 (tracked working bytes) and NOT done 9's stalled-build shape. Say for each whether it
   closed, with its test.
5. **K2's registration patch, rebased (VERIFY-LS-B11 F-14).** LS-B10's registration landed in 0d0c609, so
   `tasks/briefs/jev-trim/K2-registration.patch` no longer applies at the PIN (the premise shows where). Rebase it onto
   the PIN; the hook-count test counts LS-B10's three hooks and K2's together through `hook_count`. Keep
   `tasks/briefs/jev-trim/K2-post-commit.patch` applying at the PIN.
6. **Mutation:** the verifier's four checks, your earlier mutants, and a named mutant per clause of item 1 (compare the
   path instead of the blob; skip the indexed hash; accept a missing blob; keep the total when a name drops), each
   killed. Each driver runs its control first (AF-AP-223), with bytecode off and a cleared `__pycache__` or a fresh copy
   per mutant (AF-AP-192).
7. **The exit, stated now (D-115).** If this round's verify finds a blocker in the same class again, there is no round
   5: K2 goes to the owner as RE-SCOPE (packs without callers and tests: the file's own committed text only) or PARK. In
   your report, say which you would pick and why.

## WHERE YOU WORK: a worktree, never the shared tree

- A detached worktree at the PIN under your own scratch:
  `git -C /home/user/agent-factory -c core.hooksPath=/dev/null worktree add -q --detach <W> 14ecd8b`. Build and test
  there only.
- The round-3 verifier's probes are your red items:
  `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r3/` (`probe_r3.py` and its logs; the
  report names the commands). Copy what you run into your own scratch and point it at your worktree; never write the
  verifier's scratch.
- Your one deliverable in the shared tree: `tasks/briefs/jev-trim/K2-R4.patch`, the `git -C <W> diff 14ecd8b` of every
  file you changed, new files included. Prove it applies (`git apply --check`) on a fresh worktree at the PIN and that
  the gates pass there.
- Remove every worktree you made and stop every process you started before you report.

## BOUNDARY

- MODIFY, in your worktree only: `scripts/filepacks.py`, `tests/test_filepacks.py`, `scripts/codemap.py` (a builder
  change needs a stated reason, and every existing codemap test stays green), `tests/test_codemap.py`,
  `tasks/briefs/jev-trim/K2-post-commit.patch`, `tasks/briefs/jev-trim/K2-registration.patch`.
- CREATE, in the shared tree: `tasks/briefs/jev-trim/K2-R4.patch`. Nothing else in the shared tree.
- READ: everything above; `scripts/hooks/post-commit`; `.claude/hooks/system1-context.py`; `scripts/hook_context.py`;
  `scripts/install_session_hooks.py` and `tests/test_session_hooks.py` (both now carry LS-B10's registration);
  `tests/test_search_intercept.py`; `.claude/settings.json`.
- Never register a hook: never run `scripts/install_session_hooks.py` outside a test's temp target; never touch
  `/home/user/.claude/settings.json` (it holds this session's LIVE hooks, the chat box included since 02:3xZ), anything
  under the shared tree's `.claude/`, the live `.jev/`, or the shared tree's `scripts/hooks/`.
- Beside you: SCRUB2-R1 round 5Q runs on the PC (not in this tree), and a sandbox lane on the stack labels may start in
  its own worktree. Touch none of their files.

## EVIDENCE DEMANDS

1. Premise: re-run the block below with `bash scripts/premise_block.sh` from `/home/user/agent-factory`; stop and report
   CONTRACT-INVALID on a difference.
2. Red first: R3-1's shapes (a) and (b) reproduce at the PIN in your worktree and pass after; if one does not
   reproduce, stop and say so.
3. Gates, each twice, in your worktree, `--basetemp` as a pytest ARGUMENT outside every work tree, counts pasted from
   `scripts/test_summary.sh` with set ids from `bash scripts/pc_suite.sh set-id -- <files>`:
   `tests/test_codemap.py tests/test_filepacks.py tests/test_system1_context.py` (set 804c19143d13); then, with both
   patches applied, `tests/test_filepacks.py` again, `tests/test_session_hooks.py tests/test_search_intercept.py`, and
   `tests/test_vendored_manifest.py -k test_committed_manifest_matches_fresh_generation` (never the whole file: it copies
   about 3.4 GB). Paste `python3 scripts/vendored_manifest.py --check` with the registration patch applied; it is
   expected to fail on the `.claude/` row until the coordinator regenerates the manifest at landing; say so if it does.
4. Mutation (item 6), on your final bytes.
5. The patch's proof (the worktree section).
6. NOT done and DISCREPANCIES first in the report; then per contract item its pasted evidence; files with line counts
   and sha256; then your self-attack (how could untracked text still reach the model?) and item 7's pick.

## STANDING RULES

- No git write in the shared tree (a worktree add and remove, hooks off, is the one exception); no outward action; no
  PC bridge.
- Never read a secret file (`.pc-bridge.env`, any `*.env`, any key file); a secret-shaped canary in a test is a fake
  built at run time. In any real transcript, read only compaction boundaries and `tool_use` inputs, never a `thinking`
  block, and print only counts, bytes and paths.
- Never a top-level `cd` (AF-AP-249): `git -C`, absolute paths or a `( cd … )` subshell.
- A long gate in ONE foreground call, each under 10 minutes; stamps from `date -u`; commits cited by origin id or
  subject.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- Stop every process you start before you report; kill by pid only.

## PREMISE — MEASURED at authoring (2026-09-30, main tree; PIN origin 14ecd8b)

Printed by `bash scripts/premise_block.sh` from the main tree. Every line reads committed objects at the PIN, except the
probe's path (the verifier's scratch). K2's four files and the post-commit hook are byte-identical to round 3's landing
(a9e5389): the diff stat reads 0 lines. LS-B10's registration is in the PIN (three `ls_req.py` hooks; `hook_count` at
line 117), so K2's registration patch fails in two files. The set id is round 3's gate set. Expected to differ: nothing.

```
$ git merge-base --is-ancestor 14ecd8b HEAD && echo 14ecd8b-is-an-ancestor-of-HEAD
14ecd8b-is-an-ancestor-of-HEAD
$ git diff --stat a9e5389 14ecd8b -- scripts/filepacks.py scripts/codemap.py tests/test_filepacks.py tests/test_codemap.py scripts/hooks/post-commit | wc -l
0
$ git show 14ecd8b:scripts/filepacks.py | sha256sum | cut -c1-16
18c8360473ba0b6d
$ git show 14ecd8b:scripts/codemap.py | sha256sum | cut -c1-16
8be917715cd2a5c9
$ git show 14ecd8b:tests/test_filepacks.py | sha256sum | cut -c1-16
3857536f23325e5d
$ git show 14ecd8b:tests/test_codemap.py | sha256sum | cut -c1-16
76e31571e8008a4d
$ git show 14ecd8b:tasks/briefs/jev-trim/K2-post-commit.patch | sha256sum | cut -c1-16
71ba4c2c0cec81ab
$ git show 14ecd8b:tasks/briefs/jev-trim/K2-registration.patch | sha256sum | cut -c1-16
3e8b979120d0638a
$ git show 14ecd8b:scripts/filepacks.py | grep -n '^def _tracked_only'
571:def _tracked_only(pack, rel, packs, graphs):
$ git show 14ecd8b:scripts/codemap.py | grep -n '^WIDEN_CAP'
755:WIDEN_CAP = 20
$ git show 14ecd8b:.claude/settings.json | grep -c 'scripts/ls_req.py'
3
$ git show 14ecd8b:scripts/install_session_hooks.py | grep -n '^def hook_count'
117:def hook_count(hooks: dict) -> int:
$ T=$(mktemp) && GIT_INDEX_FILE=$T git read-tree 14ecd8b && GIT_INDEX_FILE=$T git apply --check --cached tasks/briefs/jev-trim/K2-registration.patch 2>&1; rm -f $T
error: patch failed: scripts/install_session_hooks.py:1
error: scripts/install_session_hooks.py: patch does not apply
error: patch failed: tests/test_session_hooks.py:1
error: tests/test_session_hooks.py: patch does not apply
$ ls /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r3/probe_r3.py
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r3/probe_r3.py
$ bash scripts/pc_suite.sh set-id -- tests/test_codemap.py tests/test_filepacks.py tests/test_system1_context.py | tail -1
3 files set=804c19143d13
```
