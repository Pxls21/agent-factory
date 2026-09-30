# K2 FOLLOW-UPS: the round-5 verify's follow-ups, before registration (task #420, D-120)

Role: a sandbox code-implementer (Opus 5.5), fresh. PIN: origin 59ad820 (CI run #1191 passed). Authored 2026-09-30
18:2xZ by the coordinator. Read first: D-115, D-117 and D-120 in `docs/08_DECISION_LOG.md`; then
`tasks/briefs/jev-trim/K2-RS-brief.md` (contract revision 5, which this lane keeps); then
`tasks/briefs/jev-trim/VERIFY-K2-RS-report.md`: its coordinator note, items 10, 11 and 13, and the finding inventory's
F1 to F6, F9 and F15. Do NOT spawn subagents.

## WHY

| Round | Verify | Blocker |
|---|---|---|
| 1 | VERIFY-K2: MERGE-READY-WITH-FOLLOWUPS on one condition | F1: a stale index let an untracked file's text through |
| 2 | VERIFY-K2 round 2: NOT-READY | B1: untracked callers through a tracked file's code part |
| 3 | VERIFY-K2 round 3: NOT-READY | R3-1 |
| 4 | VERIFY-K2-R4: NOT-READY | R4-1; the owner chose RE-SCOPE (D-117) |
| 5 | VERIFY-K2-RS: MERGE-READY-WITH-FOLLOWUPS | none; F1 and F2 are frozen clauses with no test |

The re-scope converged. This lane is NOT a repair round: contract revision 5 holds unchanged, and nothing here may
widen what a pack shows. It closes the follow-ups the verifier asked for before registration (its item 13.4 to 13.6).
The owner approved it on 17:36:31Z ("Yes do small follow lane", D-120), with F3 and F4 as the coordinator recommended.
After it, the verifier re-checks; then the owner decides the registration.

## CONTRACT

1. **Premise.** Re-run the block at the end with `bash scripts/premise_block.sh` from the main tree
   (`/home/user/agent-factory`, read-only for you). Stop and report CONTRACT-INVALID on any difference.

2. **F1: the registry's committed source gets its test.** The frozen clause (K2-RS contract item 3): a pack shows "the
   registry rows only when they are computed from the committed blob's lines". Add a check to `tests/test_filepacks.py`
   through the real builders (`codemap.py build`, then `filepacks.py build`) and the real hook. The fixture: a committed
   file with a committed line the AF-AP registry screen hits (the control: its registry row shows), and an uncommitted
   canary line the screen also hits, written after the commit and before the build, with the Edit placed on that line.
   No byte of the canary line may show. The verifier's mutant `registry-from-working-text-fullfp` (`<SR>/mutdrv5.py`:
   `_registry(root, rel, text)` at `scripts/codemap.py:763` fed the working copy instead) must be KILLED by your check;
   at the PIN it passes all of `tests/test_filepacks.py` (the verifier's round 5: 175 passed, `1 files
   set=db64e610236b`). Reference probe: `<SR>/probes/p8disc_b.py`.

3. **F2: head-unresolved covers the tree-less record.** Add to `check_head_unresolved` (`tests/test_filepacks.py:1139`)
   the case of a BUILD.json record with no tree and a git that fails: 0 bytes shown. The verifier's mutant
   `current-none-equals-none` (at `scripts/filepacks.py:544`, the condition `isinstance(want, str) and
   OBJECT_RX.fullmatch(want) is not None and got == want` replaced by `got == want`) must be KILLED. Reference probe:
   `<SR>/probes/p8disc.py` (the PIN showed 0 bytes, the mutant 907).

4. **F3: the two dev CLIs say when their output is not HEAD's code.** A label, not a gate: the owner approved the
   coordinator's recommendation to mark the output (D-120). `codemap.py lookup` and `codemap.py demo` run the checks
   the hook runs before it shows a code part (the build's tree equals `HEAD^{tree}`, the pack's blob is the one
   BLOBS.txt names, `symbols_from` is `"ast"`). When one fails, the FIRST line of their output says the output is not
   HEAD's committed code and names the failed check, in one short line; the rest prints as today. Correct the usage
   line at `scripts/codemap.py:30` ("what L2b would inject"), which is false after a reset. Test: after
   `git reset --mixed HEAD~1` and after `git reset --hard HEAD~1`, both CLIs print the label first; a control at
   HEAD's tree prints none. Reference probe: `<SR>/probes/p5.py`.

5. **F4: the reader's HEAD is this repository's.** `_rev` (`scripts/filepacks.py:553`) runs git with `GIT_DIR`,
   `GIT_WORK_TREE`, `GIT_COMMON_DIR` and `GIT_INDEX_FILE` removed from its environment, and names the repository by its
   root. Test: `GIT_DIR` pointing at a clone with the same tree while this repository's HEAD was reset: nothing shows;
   a leak control with the variables kept shows the packs. Reference probe: `<SR>/probes/p3.py`. For every other git
   call site in the two scripts, one report line: can an inherited `GIT_*` reach it, and what does a foreign value do
   there (fail closed or not)? Change none of them; if one fails open, stop and say so first.

6. **F5: one bad file never aborts a build.** `_ast_starts` (`scripts/codemap.py:624`) lets MemoryError escape: a
   committed 200,000-deep unary chain makes `codemap.py build` exit 1, the files after it get no pack, and
   `build --all` gave 0 packs. Catch RecursionError and MemoryError there (or drop the function, if `_moved` at
   `scripts/codemap.py:644` is its only user and shows nothing; say which you did and why), and give `build()`
   (`scripts/codemap.py:792`) a per-file guard, so a file whose parse fails costs that file's symbols only. Test: the
   chain file and a good file in one build: rc 0, and the good file has its pack. Reference: `<SR>/probes/p2c.py` (its
   A9). Keep the test fast: measure the depth this Python needs, and paste the time.

7. **F6: an honest line for a file with no symbols.** For a committed blob that does not parse, the text says so (for
   example "no symbols: the committed blob does not parse"); for a code file in another language, "no symbols for
   <language>"; never "0 symbols, 0 at top level" (`scripts/codemap.py:1014`, and the pack text the hook shows).
   Reference: `<SR>/probes/p2a.py`.

8. **F9: one sentence.** `scripts/filepacks.py:28` says "Every byte shown is committed text of HEAD's tree". P2's
   commit lines are the build's history, which after a same-tree ref move can hold commits HEAD's history lacks
   (reproduced in `<SR>/probes/p3.py`). Rewrite the sentence so it is true; change nothing else in the docstring.

9. **F15: a crashed build does not leave the hook dark past the next session start.** Today a crash after the marker
   (`"building": True`, `scripts/filepacks.py:1099`) leaves the hook injecting nothing until the next build, and no
   SessionStart step recovers it. At SessionStart, on the `reset` path (`scripts/filepacks.py:795`, which the
   registration patch already calls), when the record is a marker and no build holds `filepacks.lock`
   (`scripts/filepacks.py:1024`), start one build, never beside a live build, and without holding the session start
   longer than a bound you measure and state. Test: a marker left with the lock free, then the SessionStart path: a
   build runs and the hook shows packs again; with a build holding the lock, no second build starts. If this needs a
   change to `tasks/briefs/jev-trim/K2-registration.patch` or `tasks/briefs/jev-trim/K2-post-commit.patch`, make it
   there and recompute the counts through `hook_count`.

10. **Mutants.** Your driver's control first (AF-AP-223), bytecode off, a fresh copy or a cleared `__pycache__` per
    mutant (AF-AP-192). Each must be KILLED: the verifier's two survivors (items 2 and 3, on your bytes); the label
    removed (F3); the environment strip removed (F4); the per-file guard removed (F5); the old "0 symbols" line
    restored (F6); the SessionStart recovery removed (F15); the recovery made to ignore the lock.

## WHERE YOU WORK

A new worktree at the PIN under your scratch (`git -C /home/user/agent-factory -c core.hooksPath=/dev/null worktree add
-q --detach <W> 59ad820`), never the shared tree. Your one shared-tree write is your deliverable,
`tasks/briefs/jev-trim/K2-FU.patch` (`git -C <W> diff 59ad820` over every file you change, new files included). It must
apply at the PIN with `git apply --check`. Remove every worktree you made before you report.

`<SR>` = `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2rs`, the verifier's scratch: READ
only. Copy a probe (with its `common.py` and `p2a_lib.py`) into your scratch before you run or change it; the probes
expect a worktree at `<SR>/wt` on 2df97aa, so point your copies at your own worktree (2df97aa and 59ad820 hold the same
K2 bytes: premise line 3).

Beside you: the Jev relay (a python3 process serving 127.0.0.1:47430) and the codebase-memory daemon. Never stop a
process you did not start. No other lane runs.

## BOUNDARY

- MODIFY, in your worktree only: `scripts/filepacks.py`, `scripts/codemap.py`, `tests/test_filepacks.py`,
  `tests/test_codemap.py`; `tasks/briefs/jev-trim/K2-registration.patch` and `tasks/briefs/jev-trim/K2-post-commit.patch`
  only if F15 needs them.
- CREATE, in the shared tree: `tasks/briefs/jev-trim/K2-FU.patch`.
- READ: every other file.
- NOT yours: `.claude/settings.json`, `scripts/install_session_hooks.py`, `/home/user/.claude/settings.json`, the live
  `.jev/` (its `relay/` folder holds session text: never read it), `scripts/hooks/` in the shared tree, `.agents/`,
  `CLAUDE.md`. Never register a hook.

## GATES

In your worktree, each call under 10 minutes, `--basetemp` as a pytest ARGUMENT with a short path outside every work
tree (such as `/tmp/k2fu/<n>`), `PYTHONDONTWRITEBYTECODE=1`, counts pasted from `scripts/test_summary.sh` with set ids
from `bash scripts/pc_suite.sh set-id -- <files>`:
- `tests/test_filepacks.py` (`1 files set=db64e610236b`) twice;
- `tests/test_codemap.py tests/test_system1_context.py` (`2 files set=395f8af3a0ce`);
- in the both-patches tree (the PIN, your patch, and the two K2 patches): `tests/test_session_hooks.py
  tests/test_search_intercept.py` (`2 files set=2415789b9582`), and `tests/test_vendored_manifest.py -k
  test_committed_manifest_matches_fresh_generation` only (its `.claude/` row drifts there, as round 5's did: say so;
  the coordinator regenerates it at landing);
- every other test that names a file you change (`python3 scripts/stack.py gate paths=<comma-separated paths>
  mode=plan graph=no` in your worktree lists them).

## REPORT

Return the whole report as your final message: the premise re-run; per contract item, its pasted evidence; the F4
call-site table; F15's measured bound; files with line counts and sha256; the patch's sha256 and `git apply --check` at
the PIN; the gates; the mutants; NOT done, first-class; DISCREPANCIES; your self-attack: how could a pack or a CLI still
show a byte HEAD's tree does not hold, without saying so?

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

## PREMISE — MEASURED at authoring (2026-09-30, main tree; PIN origin 59ad820)

Printed by `bash scripts/premise_block.sh` from the main tree. Expected to differ: nothing.

```
$ git merge-base --is-ancestor 59ad820 HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ for f in scripts/filepacks.py scripts/codemap.py tests/test_filepacks.py tests/test_codemap.py tasks/briefs/jev-trim/K2-registration.patch tasks/briefs/jev-trim/K2-post-commit.patch; do printf '%s %s\n' "$(git show 59ad820:$f | sha256sum | cut -c1-16)" "$f"; done
be82ab16c83a1402 scripts/filepacks.py
15f41cb1400f34f2 scripts/codemap.py
0ae34b5c13aaa7d6 tests/test_filepacks.py
08e48d868a92cedb tests/test_codemap.py
1dc53684b8ae5490 tasks/briefs/jev-trim/K2-registration.patch
3fe1a775b7203205 tasks/briefs/jev-trim/K2-post-commit.patch
$ git log -1 --format=%h 59ad820 -- scripts/filepacks.py scripts/codemap.py tests/test_filepacks.py tests/test_codemap.py tasks/briefs/jev-trim/K2-registration.patch tasks/briefs/jev-trim/K2-post-commit.patch
2df97aa
$ git diff --stat 59ad820 HEAD -- scripts/filepacks.py scripts/codemap.py tests/test_filepacks.py tests/test_codemap.py tasks/briefs/jev-trim/K2-registration.patch tasks/briefs/jev-trim/K2-post-commit.patch | tail -1; echo end-of-diff
end-of-diff
$ git show 59ad820:scripts/filepacks.py | grep -n 'Every byte shown\|^    def current\|isinstance(want, str)\|^def _rev\|^def _screened\|^def reset\|^def hook\|^def build\|^def _build\|"building": True\|filepacks.lock'
28:all cut at a line boundary within PACK_BUDGET bytes. Every byte shown is committed text of HEAD's tree (task #353, K2
538:    def current(self):
544:            self._current = isinstance(want, str) and OBJECT_RX.fullmatch(want) is not None and got == want
553:def _rev(root, name):
624:def _screened(pack, packs):
795:def reset(payload, state, now):
838:def hook(argv, state):
1016:def build(root=ROOT, state=None, sha=None):
1024:    lock = s1(state / "pycache").open_regular(str(state / "filepacks.lock"), os.O_WRONLY | os.O_CREAT)
1032:def _build(root, state, sha, t0):
1099:    _write(str(pdir / "BUILD.json"), (json.dumps({"schema": SCHEMA, "commit": sha, "building": True}, sort_keys=True)
$ git show 59ad820:scripts/codemap.py | grep -n 'what L2b would inject\|^def _ast_starts\|^def _moved\|^def _registry\|reg_sec, registry = _registry\|^def build_one\|^def build\|^def lookup\|symbols, %d at top level'
30:  codemap.py demo PAYLOAD.json|-            what L2b would inject for a recorded Edit payload (file_path, old_string)
550:def _registry(root, rel, text):
624:def _ast_starts(text):
644:def _moved(sec, theirs, ours, who):
715:def build_one(root, rel, gn, env, commit):
763:    reg_sec, registry = _registry(root, rel, text)
792:def build(root, rels, env=None, gn=None):
907:def lookup(path, line, end_line=None, root=None, pack=None):
1014:        head = "codemap %s — %d symbols, %d at top level" % (rel, len(syms), len(shown))
$ for f in probes/p8disc_b.py probes/p8disc.py probes/p5.py probes/p3.py probes/p2a.py probes/p2c.py mutdrv5.py; do printf '%s %s\n' "$(sha256sum < /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2rs/$f | cut -c1-16)" "$f"; done
ed8046731c1a2dd7 probes/p8disc_b.py
97627b0bc4f3b5d5 probes/p8disc.py
eba5a35e6b5601f3 probes/p5.py
928ad40c4ef24868 probes/p3.py
144fb6fcb92086c2 probes/p2a.py
54204d9c830dc660 probes/p2c.py
c361dfb60183b9ec mutdrv5.py
$ grep -c 'registry-from-working-text-fullfp\|current-none-equals-none' /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2rs/mutdrv5.py
2
$ bash scripts/pc_suite.sh set-id -- tests/test_filepacks.py
1 files set=db64e610236b
$ bash scripts/pc_suite.sh set-id -- tests/test_codemap.py tests/test_system1_context.py
2 files set=395f8af3a0ce
$ bash scripts/pc_suite.sh set-id -- tests/test_session_hooks.py tests/test_search_intercept.py
2 files set=2415789b9582
$ git show 59ad820:.claude/settings.json | grep -c 'filepacks' || true
0
$ git show 59ad820:tests/test_filepacks.py | grep -n 'head.unresolved\|head_unresolved' | head -5
37:stay), head-unresolved (an unborn branch, no repository, a git that does not answer), and the class test through the
1139:def check_head_unresolved(repo, st, ids, tmp):
1419:          "head-unresolved": check_head_unresolved, "late-code-pack": check_late_code_pack,
1608:    "unresolved-head-trusted": ("head-unresolved", " and got == want\n", " and got in (want, None)\n",
```
