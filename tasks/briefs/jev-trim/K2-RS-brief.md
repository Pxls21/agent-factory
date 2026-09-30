# K2 RE-SCOPE: a pack shows committed text only, and only while the build's tree is HEAD's (task #353, D-117)

Role: the original K2 builder, resumed (a sandbox code-implementer, Opus 5.5). PIN: origin 631dc86 (CI run #1181
passed). Authored 2026-09-30 10:4xZ by the coordinator. Read first: D-115 and D-117 in `docs/08_DECISION_LOG.md`; then
`tasks/briefs/jev-trim/VERIFY-K2-R4-report.md`: its coordinator note, R4-1, §6 (the two conditions) and §7 (what must
hold before registration). Do NOT spawn subagents.

## THE ROUND TABLE (D-115)

| Round | Verify | Blocker |
|---|---|---|
| 1 | VERIFY-K2: MERGE-READY-WITH-FOLLOWUPS on one condition | F1: a stale index let an untracked file's text through |
| 2 | VERIFY-K2 round 2: NOT-READY | B1: untracked callers through a tracked file's code part |
| 3 | VERIFY-K2 round 3: NOT-READY | R3-1: a caller's name from a file's untracked era, after the file is committed |
| 4 | VERIFY-K2-R4: NOT-READY | R4-1: `git reset --mixed` or `--soft` moves HEAD back and runs no hook, so the packs stay on the undone commit |

The failing assumption, after four rounds: that a pack built at a commit still describes the tree the model reads. The
owner chose RE-SCOPE (D-117, 10:1xZ: "Also rescope"). This is a NEW contract (revision 5), not a fifth repair: one build
round, then its verify. If that verify finds a blocker, the coordinator runs D-115's review before anything else.

## CONTRACT (revision 5: RE-SCOPE)

1. **Premise.** Re-run the block at the end with `bash scripts/premise_block.sh` from the main tree. Stop and report
   CONTRACT-INVALID on any difference.

2. **Condition (a): a pack's own symbols come from the committed blob.** The symbol list a pack shows (names, kinds,
   line spans, signatures) is parsed from the file's blob at the build's commit, the blob BLOBS.txt names: Python's
   `ast` for a `.py` file, no symbols for any other language. No symbol, name, line or count comes from graft,
   GitNexus, code-review-graph, codebase-memory or any other derived index. This closes your round-4 NOT done 7.

3. **The callers-and-tests surface goes.** A pack shows no caller, no test, no callers total, no risk line and no
   impacted count. What stays: the symbol entry from (a), the registry rows only when they are computed from the
   committed blob's lines, and the ledger part (P2). Remove what only the removed surface used; keep the change as
   small as it can be. Where the code map keeps building graph sections that no reader shows any more, say what you
   kept and why (the post-commit refresh's cost is the measure).

4. **Condition (b): nothing unless the build's tree is HEAD's.** The reader injects nothing, in any part of a pack (the
   code part and P2), unless the file-pack build's tree equals `HEAD^{tree}`.
   - The build records its tree id (for example in BUILD.json, beside the commit). The reader resolves `HEAD^{tree}`
     once per hook call and compares.
   - Trees, not commits: `scripts/push_clean.sh:69-72` moves the branch ref to a commit with the same tree after its
     rewrite, and the packs must stay through that.
   - A HEAD that cannot be resolved (no repository, an unborn branch, a git error or timeout) injects nothing.
   - Measure the cost: the median and the p95 of the hook call with the check, over 50 calls, against the PIN's hook.

5. **The class tests, committed, through the real patched hook** (the both-patches tree, as round 4's tests ran):
   - `git reset --mixed HEAD~1`, `git reset --soft HEAD~1`, and the P2 shape (an uncommitted ledger line after a
     reset): after each, no pack shows any byte that HEAD's tree does not hold. Each shape has a leak control: the same
     test with the tree check disabled shows the leak, so the test proves the check acts.
   - A same-tree ref move (`git commit-tree` of HEAD's tree with another message, then `git update-ref`, as push_clean
     does): the packs still show.
   - Condition (a): an untracked file's symbols and an edited file's uncommitted symbols never show; a control shows a
     committed symbol does. The shapes of rounds 1 to 4 that pass through the committed text part stay green; the ones
     that tested only the removed surface go, each named in your report.

6. **The verifier's §7 items, as they apply after the re-scope.** Items 1 and 2 are items 5 and 2 above. Items 4 and 5
   (the tests line, answer text in a note) go with the removed surface: say so, one line each. Item 6: update
   `tasks/briefs/jev-trim/K2-post-commit.patch` if the build's record changes; one build at HEAD writes TRACKED.txt,
   BLOBS.txt and BUILD.json before any session loads the hook. Item 8: update `tasks/briefs/jev-trim/K2-registration.patch`
   to your bytes, its counts recomputed through `hook_count`; it stays a patch, NOT registered. Items 7, 10 and 11 are
   the coordinator's and the owner's (the manifest row at the landing base; the installer only with the owner's yes;
   the issue-#83 findings as known gaps).

7. **Mutants.** Your driver's control first (AF-AP-223), bytecode off, a fresh copy or a cleared `__pycache__` per
   mutant (AF-AP-192). Each killed: the tree check removed; the check made on commits instead of trees (the same-tree
   control must fail); the symbols taken from the working copy instead of the blob; the symbols taken from graft; a
   caller line restored; P2 left outside the check.

## WHERE YOU WORK

A new worktree at the PIN under your scratch (`git -C /home/user/agent-factory -c core.hooksPath=/dev/null worktree add
-q --detach <W> 631dc86`), never the shared tree. Your one shared-tree write is your deliverable,
`tasks/briefs/jev-trim/K2-RS.patch` (`git -C <W> diff 631dc86` over every file you change, new files included). It must
apply at the PIN with `git apply --check`. Remove every worktree you made before you report.

Beside you: VERIFY-LS-B12-R1 (a sandbox verifier in its own worktree, on the stack labels) and the scrubber's option A
build on the PC. Never stop a process or a daemon you did not start; say so and go on.

## BOUNDARY

- MODIFY, in your worktree only: `scripts/filepacks.py`, `scripts/codemap.py`, `tests/test_filepacks.py`,
  `tests/test_codemap.py`, `tasks/briefs/jev-trim/K2-registration.patch`, `tasks/briefs/jev-trim/K2-post-commit.patch`.
- READ: every other file.
- NOT yours: `.claude/settings.json`, `scripts/install_session_hooks.py`, `/home/user/.claude/settings.json`, the live
  `.jev/`, `scripts/hooks/` in the shared tree, `.agents/`, `CLAUDE.md`. Never register a hook.

## GATES

In your worktree, each call under 10 minutes, `--basetemp` as a pytest ARGUMENT outside every work tree, counts pasted
from `scripts/test_summary.sh` with set ids from `bash scripts/pc_suite.sh set-id -- <files>`:
- `tests/test_filepacks.py` (`1 files set=db64e610236b`) twice;
- `tests/test_codemap.py tests/test_system1_context.py` (`2 files set=395f8af3a0ce`);
- in the both-patches tree: `tests/test_session_hooks.py tests/test_search_intercept.py` (`2 files set=2415789b9582`),
  and `tests/test_vendored_manifest.py -k test_committed_manifest_matches_fresh_generation` (its `.claude/` row drifts
  there, as round 4's did: say so, the coordinator regenerates it at landing);
- every other test that names a file you change (`python3 scripts/stack.py gate paths=<comma-separated paths> mode=plan
  graph=no` in your worktree lists them).

## REPORT

Return the whole report as your final message: the premise re-run; per contract item its pasted evidence; the hook's
cost; files with line counts and sha256; the patch's sha256 and `git apply --check` at the PIN; the gates; the mutants;
the tests you removed with the surface, by name; NOT done, first-class; DISCREPANCIES; your self-attack: how could a
pack still show a byte HEAD's tree does not hold?

## STANDING RULES

- No git write in the shared tree (a worktree add and remove, hooks off, is the one exception); no outward action; no
  PC bridge; never register a hook.
- Never read a secret file (`.pc-bridge.env`, any `*.env`, any key file). In any real transcript, read only `text`
  blocks, `tool_use` inputs and record types, never a `thinking` block, and print only counts, bytes and ids.
- Never a top-level `cd` (AF-AP-249): `git -C`, absolute paths or a `( cd ... )` subshell.
- A long gate in ONE foreground call; stamps from `date -u`; commits cited by origin id or subject.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- Stop every process you start before you report (a codebase-memory daemon included); kill by pid only, found with an
  anchored pattern (`pgrep -f '^python3 ...'`).

## PREMISE — MEASURED at authoring (2026-09-30, main tree; PIN origin 631dc86)

Printed by `bash scripts/premise_block.sh` from the main tree. The six file hashes are round 4's final bytes (your
round-4 report's Files table). Expected to differ: nothing.

```
$ git merge-base --is-ancestor 631dc86 HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ for f in scripts/filepacks.py scripts/codemap.py tests/test_filepacks.py tests/test_codemap.py tasks/briefs/jev-trim/K2-registration.patch tasks/briefs/jev-trim/K2-post-commit.patch; do printf '%s %s\n' "$(git show 631dc86:$f | sha256sum | cut -c1-16)" "$f"; done
31606f07fa64c948 scripts/filepacks.py
e1a56e0b0cf8e8ed scripts/codemap.py
32d3bcd4e7935ed7 tests/test_filepacks.py
d8002fbbeb8217ae tests/test_codemap.py
1dc53684b8ae5490 tasks/briefs/jev-trim/K2-registration.patch
71ba4c2c0cec81ab tasks/briefs/jev-trim/K2-post-commit.patch
$ git log -1 --format=%h 631dc86 -- scripts/filepacks.py scripts/codemap.py tests/test_filepacks.py tests/test_codemap.py
e2f4f08
$ git show 631dc86:scripts/filepacks.py | grep -n '^class Packs\|    def built\|    def blob\|    def commit\|^def _p2_lines\|^def _committed_only\|^def _code_part\|^def entry\|^def hook\|^def _build\|BUILD.json'
19:`ls-tree`) and <state>/filepacks/BUILD.json records the SHA, the counts and the milliseconds. A named path can only be
464:class Packs:
476:    def built(self):
488:    def blob(self, rel):
501:    def commit(self):
504:                self._commit = str(json.loads(s1().read_regular(str(self.dir / "BUILD.json")))["commit"])[:7]
542:def _p2_lines(rel, packs):
573:def _committed_only(pack, rel, packs, graphs):
608:def _code_part(rel, ti, packs):
674:def entry(rel, tool_input, budget=PACK_BUDGET, *, packs=None, p2=True):
808:def hook(argv, state):
969:            if top and name in ("BUILD.json", "TRACKED.txt", "BLOBS.txt") and not link:
988:    <state>). Returns the BUILD.json record."""
1002:def _build(root, state, sha, t0):
1065:             for p, by in kept.items() if p != "BUILD"}      # a root file named BUILD would be BUILD.json
1088:    _write(str(pdir / "BUILD.json"), (json.dumps(rec, sort_keys=True) + "\n").encode("utf-8"))
$ git show 631dc86:scripts/push_clean.sh | sed -n 69,72p
    # trees are identical; never move the ref otherwise.
    LT=$(git rev-parse "refs/heads/$BRANCH^{tree}"); OT=$(git rev-parse "refs/remotes/origin/$BRANCH^{tree}")
    if [ "$LT" = "$OT" ]; then
      git update-ref "refs/heads/$BRANCH" "$(git rev-parse "refs/remotes/origin/$BRANCH")"
$ git show 631dc86:tasks/briefs/jev-trim/VERIFY-K2-R4-report.md | grep -n '^### 6\|^### 7\|^### 8'
366:### 6. The item-7 pick: RE-SCOPE, on two conditions
383:### 7. What must hold before registration (round 4's bytes)
396:### 8. Reproduced, static, skipped
$ bash scripts/pc_suite.sh set-id -- tests/test_filepacks.py
1 files set=db64e610236b
$ bash scripts/pc_suite.sh set-id -- tests/test_codemap.py tests/test_system1_context.py
2 files set=395f8af3a0ce
$ bash scripts/pc_suite.sh set-id -- tests/test_session_hooks.py tests/test_search_intercept.py
2 files set=2415789b9582
$ git show 631dc86:.claude/settings.json | grep -c 'filepacks' || true
0
```
