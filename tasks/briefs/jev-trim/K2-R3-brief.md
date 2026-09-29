# K2 round 3: untracked callers, symbols tied to the blob, the post-commit patch's own tests, the seven checks (task #353, D-111)

Role: code-implementer, the original K2 builder, resumed (sandbox, Opus 5.5). Do NOT spawn subagents. Return the whole
report as your final message.

Authored 2026-09-29 17:1xZ by the coordinator. The owner authorized this round past D-031's one-repair budget
(D-111: "run round 3"). Your round 2 landed at f605913 ("K2 round 2 landed (task #353; GATED-PENDING-VERIFY) ...") and
stays inert: the hook is not registered. VERIFY-K2 round 2, `tasks/briefs/jev-trim/VERIFY-K2-R2-report.md` (READ it in
full, the coordinator note at its top first), returned NOT-READY on three blockers. Round 1's and round 2's contracts
stay true in full; every item the verifier found holding stays holding.

## CONTRACT (this round)

1. **B1: no untracked caller or test reaches the model.** The code part carries only the callers and tests whose file
   TRACKED.txt lists (the exact-line match you already use), and its total is recounted over what is kept, or dropped.
   The verifier's case: an untracked `scripts/caller_new.py` calls tracked `scripts/alpha.py`'s `helper`, the real
   patched post-commit hook runs, every graph reads `fresh`, and an Edit injects the untracked function name and path
   (`callers 5 (2 in tests): <UNT> scripts/caller_new.py:4 · ...`); its scratch filter still printed "callers 5". Fix it
   on the reader side (`_code_part` in `scripts/filepacks.py`, or the readers when a pack is handed to them). Port
   `probe_callers2.py` as a test through the real patched hook: the untracked name and path absent, the tracked caller
   and test present (the control), and a named mutant that removes the filter.
2. **B2: a pack's symbols are tied to its blob.** After the blob check (`scripts/filepacks.py:601-602` at the PIN),
   withhold the code part when the pack's symbol-source graph is not `fresh` (the pack records `symbols_from` and
   `instruments.graft.graph`), and record why (the verifier's scratch fix wrote `code_skip: stale-graph`). Port both
   shapes as tests: (a) the untracked shape of `probe_f1b.py ... sg-untracked` (0 canary bytes on Edit, Read and `cat`),
   (b) the tracked-revert shape of `probe_f1.py ... sg-tracked`; each with a named mutant that drops the clause. If you
   find a way to tie the symbols to the blob itself that is simpler and closes both shapes, say why it is equivalent.
3. **B3: the post-commit patch passes its own tests once it lands.** `hook_dir` (`tests/test_filepacks.py:1200`) knows
   whether the hook it copies already carries the patch; the negative control
   (`test_negative_control_the_hook_without_the_patch_runs_no_build`) runs on the unpatched hook's bytes taken from a
   fixed commit (`git show f605913:scripts/hooks/post-commit` or the PIN's), never the working copy. Proof:
   `tests/test_filepacks.py` gives 0 failed in a worktree WITHOUT the post-commit patch and in one WITH it applied (the
   verifier's patched run: `3 failed, 126 passed`, set db64e610236b).
4. **The seven checks the verifier's mutation run found missing** (report finding 4), each ported into
   `tests/test_filepacks.py` with its mutant, from `mutdrv3.py`'s killers: `blob-fail-open` (`n2_blobs_missing`: the
   live state has no BLOBS.txt, so this one guards the registration state), `grep-long-value-dropped`
   (`n2_grep_long_value`), `grep-attached-ignored` (`n2_grep_attached`), `frame-close-any` (`n2_script_paren`),
   `dq-sub-not-opened` (`n3_dq_substitution`), `grep-double-dash-dropped` (`n3_grep_double_dash`), `files-max-off`
   (`n3_files_max`). Keep every existing check.
5. **The stale documents** (report finding 8): `docs/research/findings/jev-trim/D105-DESIGN-v1.md:281` ("Not built:
   L2b") says what is built and what is not; `tasks/briefs/jev-trim/K2-R2-report.md` line 8 ("F1: closed by the blob
   check") and its self-attack 1 get a dated note that VERIFY-K2 round 2's B1 and B2 falsified them, pointing to this
   round's report. Annotate; never rewrite the round-2 record.
6. **The two patches still apply and still prove out.** If round 3 changes what `tasks/briefs/jev-trim/K2-post-commit.patch`
   or `tasks/briefs/jev-trim/K2-registration.patch` must hold, update them; either way re-prove both in a clean worktree
   at the PIN with your round-3 files applied (round 2's item 8 proof, re-run). `tasks/briefs/labeling/LS-B10-registration.patch`
   changes the same three files as yours (`.claude/settings.json`, `scripts/install_session_hooks.py`,
   `tests/test_session_hooks.py`); keep your hunks minimal, and the coordinator rebases whichever lands second.

Out of scope, on GitHub issue #83: report findings 5 (`pack-not-handed`), 6 (the parser's remaining wrong files), 7 (the
builder's `language()` depends on the System-1 hook), 9, 12 and 15. Leave them.

## WHERE YOU WORK: a worktree, never the shared tree (orchestration 0p)

- This round differs from round 2: you do NOT edit the shared tree. Make a detached worktree at the PIN under your own
  scratch: `git -C /home/user/agent-factory -c core.hooksPath=/dev/null worktree add -q --detach <W> 99583a2`. Build and
  test there only.
- The verifier's probes are your red items: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/`
  (`probe_callers2.py`, `probe_f1.py`, `probe_f1b.py`, `probe_blobs.py`, `probe_forge.py`, `mutdrv3.py`; logs in
  `logs/`; how to re-run them in its §7). Copy what you run into your own scratch and point it at your worktree; never
  write the verifier's scratch.
- Your one deliverable in the shared tree: `tasks/briefs/jev-trim/K2-R3.patch`, the `git -C <W> diff` against the PIN of
  every file you changed. Prove it applies (`git apply --check`) on a fresh worktree at the PIN and that the gates pass
  there.
- Remove every worktree you made, and stop every process you started, before you report.

## BOUNDARY

- MODIFY, in your worktree only: `scripts/filepacks.py`, `tests/test_filepacks.py`, `scripts/codemap.py` (its readers;
  a builder change needs a stated reason, and every existing codemap test stays green), `tests/test_codemap.py`,
  `tasks/briefs/jev-trim/K2-post-commit.patch`, `tasks/briefs/jev-trim/K2-registration.patch`,
  `docs/research/findings/jev-trim/D105-DESIGN-v1.md` (the L2b lines only), `tasks/briefs/jev-trim/K2-R2-report.md` (the
  two annotations only).
- CREATE, in the shared tree: `tasks/briefs/jev-trim/K2-R3.patch`. Nothing else in the shared tree.
- READ: everything named above; `scripts/hooks/post-commit`; `.claude/hooks/system1-context.py`; `scripts/hook_context.py`;
  `scripts/install_session_hooks.py`; `tests/test_session_hooks.py`; `tests/test_search_intercept.py`; `.claude/settings.json`.
- Never register the hook: never run `scripts/install_session_hooks.py` outside a test's temp target; never touch
  `/home/user/.claude/settings.json`, anything under the shared tree's `.claude/`, the live `.jev/`, or the shared tree's
  `scripts/hooks/`.
- Three lanes run beside you (VERIFY-SCRUB2-R1-R4, VERIFY-H1a, LS-B10 round 2), each in its own worktree; touch none of
  their files.

## EVIDENCE DEMANDS

1. Premise: re-run the block below with `bash scripts/premise_block.sh` from `/home/user/agent-factory`; stop and report
   CONTRACT-INVALID on a difference.
2. Red first: B1, B2 (a) and B3 reproduce at the PIN in your worktree through the verifier's probes, and pass after; if
   one does not reproduce, stop and say so. B2 (b) before and after. The seven mutants survive the PIN's suite and are
   killed after.
3. Gates, each twice, in your worktree, with `--basetemp` as a pytest ARGUMENT outside every work tree, counts pasted
   from `scripts/test_summary.sh` with set ids from `bash scripts/pc_suite.sh set-id -- <files>`:
   `tests/test_codemap.py tests/test_filepacks.py tests/test_system1_context.py` (set 804c19143d13 at the PIN); then,
   with both patches applied, `tests/test_filepacks.py` again (0 failed, B3), `tests/test_session_hooks.py
   tests/test_search_intercept.py`, and `tests/test_vendored_manifest.py -k test_committed_manifest_matches_fresh_generation`
   (never the whole file: it copies about 3.4 GB). Paste `python3 scripts/vendored_manifest.py --check` with the
   registration patch applied; it is expected to fail on the `.claude/` row until the coordinator regenerates the
   manifest at landing; say so if it does.
4. Mutation on your final bytes, each driver's control first (AF-AP-223: check the `--basetemp` parent exists before you
   count a kill): your own mutants of rounds 1 and 2, the verifier's 60 (`mutdrv3.py`), and a new named mutant per
   clause of items 1 to 3.
5. The patch's proof (the worktree section).
6. NOT done and DISCREPANCIES first in the report; then per item its pasted evidence; files with line counts and sha256;
   then your self-attack: how could untracked text still reach the model?

## STANDING RULES

- No git write in the shared tree (a worktree add and remove, hooks off, is the one exception); no outward action; no PC
  bridge.
- Never read a secret file (`.pc-bridge.env`, any `*.env`, any key file); a secret-shaped canary in a test is a fake built
  at run time. In any real transcript, read only compaction boundaries and `tool_use` inputs, never a `thinking` block,
  and print only counts, bytes and paths.
- The sandbox VM rebooted twice today while tests ran (14:09:29Z, about 14:20:10Z; cause open): run `free -m` before a
  heavy command, keep each run's evidence on disk as you go, and say which runs a reboot voided.
- A long gate in ONE foreground call, each under 10 minutes; stamps from `date -u`, substituted, never typed; commits
  cited by origin id or subject.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- Stop every process you start before you report; kill by pid only. `graft build` in a test can leave a detached
  `graft _update-check` child (env-tool-quirks, "Test gates and pasted counts"); check for it before you report.

## PREMISE — MEASURED at authoring (2026-09-29, main tree@99583a2; PIN origin 99583a2)

Printed by `bash scripts/premise_block.sh` from the main tree at origin 99583a2, before this brief's commit (which
touches no boundary file). The two patches apply at HEAD; the hook is registered nowhere (the three 0 counts; `[rc=1]` is
grep's exit code for them). The verifier's scratch holds its probes and logs; it does not survive a container reset.
Expected to differ: nothing. Re-run every `$` line from `/home/user/agent-factory`; on any difference, stop and report
CONTRACT-INVALID with the diff.

```
$ git merge-base --is-ancestor 99583a2 HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ git diff --quiet 99583a2 HEAD -- scripts/filepacks.py tests/test_filepacks.py scripts/codemap.py tests/test_codemap.py scripts/hooks/post-commit tasks/briefs/jev-trim/K2-post-commit.patch tasks/briefs/jev-trim/K2-registration.patch docs/research/findings/jev-trim/D105-DESIGN-v1.md tasks/briefs/jev-trim/K2-R2-report.md && echo boundary-unchanged-since-PIN
boundary-unchanged-since-PIN
$ git log -1 --format=%s -- scripts/filepacks.py | cut -c1-70
K2 round 2 landed (task #353; GATED-PENDING-VERIFY): the stale-index h
$ git log -1 --format=%s -- tests/test_filepacks.py | cut -c1-70
CI run 1145 fix: the filepacks no-word-cap control sized for CI's fast
$ sha256sum scripts/filepacks.py tests/test_filepacks.py scripts/codemap.py tests/test_codemap.py scripts/hooks/post-commit tasks/briefs/jev-trim/K2-post-commit.patch tasks/briefs/jev-trim/K2-registration.patch tasks/briefs/jev-trim/VERIFY-K2-R2-report.md | cut -c1-16,65-
017ce2be467fbf53  scripts/filepacks.py
d4eaf8d8c3eb03d7  tests/test_filepacks.py
f504849bf1d4100a  scripts/codemap.py
76e31571e8008a4d  tests/test_codemap.py
23c605f1ec16c1d6  scripts/hooks/post-commit
71ba4c2c0cec81ab  tasks/briefs/jev-trim/K2-post-commit.patch
3e8b979120d0638a  tasks/briefs/jev-trim/K2-registration.patch
9ba00a5cd38b931c  tasks/briefs/jev-trim/VERIFY-K2-R2-report.md
$ wc -l scripts/filepacks.py tests/test_filepacks.py scripts/codemap.py tests/test_codemap.py | tail -1
  4641 total
$ grep -n '^def _code_part\|^def hook(\|^def _build\|^def _clean\|    def blob' scripts/filepacks.py
483:    def blob(self, rel):
568:def _code_part(rel, ti, packs):
761:def hook(argv, state):
913:def _clean(pdir, keep):
955:def _build(root, state, sha, t0):
$ grep -n '^def hook_dir\|^PATCH = ' tests/test_filepacks.py
1196:PATCH = ROOT / "tasks" / "briefs" / "jev-trim" / "K2-post-commit.patch"
1200:def hook_dir(tmp, patch):
$ grep -n '^def wait_for_graphs\|^def build_one\|^def edit_context\|^def file_entry\|^def language' scripts/codemap.py
105:def language(root: Path, rel: str) -> str | None:
223:def wait_for_graphs(root: Path, rels, graphs, lock_dir: Path, wait: float = 1200.0, grace: float = 30.0,
660:def build_one(root, rel, gn, env, commit):
953:def edit_context(file_path, old_string, root=None, replace_all=False, pack=None):
987:def file_entry(path, line=None, end_line=None, root=None, pack=None):
$ git apply --check tasks/briefs/jev-trim/K2-post-commit.patch && echo post-commit-patch-applies-at-HEAD
post-commit-patch-applies-at-HEAD
$ git apply --check tasks/briefs/jev-trim/K2-registration.patch && echo registration-patch-applies-at-HEAD
registration-patch-applies-at-HEAD
$ grep -c 'filepacks' .claude/settings.json scripts/install_session_hooks.py /home/user/.claude/settings.json
.claude/settings.json:0
scripts/install_session_hooks.py:0
/home/user/.claude/settings.json:0
[rc=1]
$ ls /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/mutdrv3.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/probe_callers2.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/live_callers.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/probe_blobs.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/probe_forge.py
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/live_callers.py
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/mutdrv3.py
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/probe_blobs.py
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/probe_callers2.py
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/probe_forge.py
$ ls /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/logs/b1-callers-real.txt /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/logs/b2-sg-untracked-real.txt /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/logs/mut3-builderonly.txt
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/logs/b1-callers-real.txt
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/logs/b2-sg-untracked-real.txt
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/logs/mut3-builderonly.txt
$ bash scripts/pc_suite.sh set-id -- tests/test_codemap.py tests/test_filepacks.py tests/test_system1_context.py | tail -1
3 files set=804c19143d13
```
