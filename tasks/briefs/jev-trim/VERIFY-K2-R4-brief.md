# VERIFY-K2 round 4: attack provenance by blob, the redesign round (task #353, D-115)

Role: the VERIFY-K2 verifier, resumed (rounds 2 and 3; sandbox adversarial-verifier, Opus 5.5). Do NOT spawn
subagents. Return the whole report as your final message (your hand-back); write no report file.

K2 round 4 landed at e2f4f08 ("K2 round 4 landed ..."), GATED-PENDING-VERIFY. It is the redesign round under D-115: the
round table in `tasks/briefs/jev-trim/K2-R4-brief.md` shows your round-3 R3-1 as the third blocker of one class
(untracked text reaches the model through the derived code index), and this round replaces "a tracked path is safe"
with "the graph indexed the committed blob". Its report of record is `tasks/briefs/jev-trim/K2-R4-report.md`: read the
coordinator note at its top, then its NOT done (1 to 4) and DISCREPANCIES (D1 to D11). Treat every claim there as a
hypothesis. The hook is still NOT registered: `tasks/briefs/jev-trim/K2-registration.patch` and
`tasks/briefs/jev-trim/K2-post-commit.patch` stay unapplied.

**The exit, stated in the round-4 brief (item 7, D-115): there is no round 5.** If you find a blocker in the same
class, K2 goes to the owner as RE-SCOPE (packs without callers and tests: the file's own committed text only) or PARK.
So name the class of every blocking finding: the SAME class (untracked or uncommitted text reaching the model through a
derived index, in any part of a pack) or ANOTHER. The builder's own pick is RE-SCOPE, on one condition (the file's own
symbols from the committed blob, never from graft); say whether you agree and why.

The coordinator's landing gate, in the shared tree with the round-4 patch applied: `8 files set=6660a3f91663` (`tests/test_codemap.py tests/test_filepacks.py tests/test_system1_context.py
tests/test_hiccup_scan.py tests/test_mojev_probe.py tests/test_post_commit_reindex.py tests/test_shell_syntax.py
tests/test_slopo.py`) `pytest-summary: 590 passed, 1 skipped in 828.62s (0:13:48)` (the skip is
`tests/test_mojev_probe.py:888`, a declared NOT-run-here that waits on a PC run).

## SCOPE

1. **Premise.** Re-run the block below with `bash scripts/premise_block.sh` from `/home/user/agent-factory`; on a
   difference, stop and report CONTRACT-INVALID with the diff.
2. **The builder's blob tie** (`scripts/codemap.py`: `_committed`, `_named_here`, `_provenance`, `_proven`,
   `build_one`). Attack each clause. A graph record equal to the blob while its nodes came from other bytes (the
   record newer than the nodes, the lie `_moved` flags for the file itself; a re-index between the Cypher answer and
   the record read). The builder's D1 (a name must sit on its line in the committed blob): a name from other bytes
   that passes it by coincidence (a def of that name on that line), a non-Python file ("a word on the line"), the
   exempt `<module>` callers, decorated defs, methods, CRLF bytes, a path with spaces or non-ASCII characters, a
   symlinked path, a gitlink.
3. **The reader** (`scripts/filepacks.py` `_committed_only`): a stale BLOBS.txt from a stalled build, a legacy pack
   with no provenance, a malformed `provenance` (a non-string blob, a missing key), a path with a newline, the
   file-itself freshness clause. The reader trusts a pack's provenance as written (the builder's self-attack 7): is a
   pack that only `scripts/codemap.py` writes by atomic replace a sound trust root here, or a hole?
4. **R3-1 and the class, on the landing's bytes.** Re-run your `probe_r3.py` shapes `late-outside` and `late-track`
   (the builder's copy `k2-lane-353/r4/vk/probe_r4.py` changes only its anchor line, its D9: check that). Then build
   new shapes of the class, for example: a committed file edited and left uncommitted, then re-indexed; a rename; a
   file whose committed blob equals its working bytes while the graph indexed a third version; `git stash`; a second
   worktree of the same repo; a branch switch between the build and the read.
5. **NOT done 7** (the file's own code part: graft's symbols and signatures, with the stamp-then-read window you
   forced in round 3 with `probe_nd7.py`). Re-run it on the landing's bytes and grade it under D-034. You rated it
   FOLLOW-UP in round 3; it is now the one known channel left. Does the rating stand, and is it the same class?
6. **The builder's adjacent defects 2a to 2d.** 2a: the tests line reads "none found" when the filter withheld every
   test (a false statement the model reads). 2b: `instruments.gitnexus.unmatched` in the pack JSON. 2c: the risk
   level and counts from GitNexus's whole graph. 2d: a failed section's `note` and a symbol's `risk_error` in the risk
   line, where `_rows` can put up to 80 characters of a malformed Cypher answer: can untracked text reach the model
   that way? If it can, that is the same class.
7. **The class test and its controls.** The builder's D2: the reader guard alone survives the class test by design,
   and planted packs prove each reader clause. Is every reader clause proven through the real reader? Does the leak
   control fail for the guard's reason and no other?
8. **Mutation.** Re-run your `vk2r3/mutdrv4.py` and the builder's `k2-lane-353/r4/mutdrv_r4.py`, each control first
   (AF-AP-223: a `--basetemp` parent that no longer exists makes every mutant error at setup and read KILLED), with
   bytecode off and a cleared `__pycache__` or a fresh copy per mutant (AF-AP-192). Write new mutants for round 4's
   new clauses.
9. **The two patches.** Apply `K2-post-commit.patch` and `K2-registration.patch` in a clean worktree at the PIN and
   run `tests/test_session_hooks.py tests/test_search_intercept.py`: the hook count through `hook_count` (LS-B10's
   three and K2's), the order in each list. `tests/test_vendored_manifest.py -k
   test_committed_manifest_matches_fresh_generation` is expected to fail on the `.claude/` row until the coordinator
   regenerates the manifest at the registration's landing; say so if it does. Never the whole manifest test file: it
   copies about 3.4 GB.
10. **The commit hook's screen tells at the landing** (advisory; printed by the pre-commit AP screen): AP-32 (hashing
    in edited code) in `scripts/codemap.py` and `tests/test_codemap.py`: is the hashed form exactly what each graph's
    record holds (a graph hashes the bytes it read; the builder hashes the blob's bytes: CRLF, a clean or smudge
    filter, `core.autocrlf`)? AF-AP-175 (a quoted HEAD passed to git) in `tests/test_codemap.py` and
    `tests/test_filepacks.py`; AF-AP-40 (a presence-gated check) in `tests/test_filepacks.py`. Say for each whether it
    is real, with the lines.
11. **Gates at the PIN**, in your own worktree (never the shared tree), `--basetemp` as a pytest ARGUMENT outside every
    work tree, counts pasted from `scripts/test_summary.sh` with set ids, each call under 10 minutes:
    `tests/test_filepacks.py` twice (`1 files set=db64e610236b`); `tests/test_codemap.py tests/test_system1_context.py`
    (`2 files set=395f8af3a0ce`).
12. **What must hold before registration**, rewritten for round 4's bytes.
13. **Gate recommendation** under D-034's blocking predicate (MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY /
    CONTRACT-INVALID). A boundary hole that puts untracked or uncommitted text in front of the model counts as
    core-blocking. Each blocking finding carries its reproduction command and its class (the exit above).

Out of scope: the items on GitHub issue #83, unless round 4 changed them.

## STANDING RULES

- A clean detached worktree at the PIN under your scratch dir (`vk2r4/`), removed at the end; no git write in the
  shared tree (a worktree add and remove, hooks off, is the one exception); no outward action, no PC bridge, no
  subagent.
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

Deliver as before: every observation with no severity filter, the blocking predicate, a gate recommendation, the class
of each blocker, and the list of what must hold before registration. Head the report "## Round 4" with "Written
2026-09-30 from <date -u stamp>".

## PREMISE — MEASURED at authoring (2026-09-30, main tree; PIN origin e2f4f08)

Printed by `bash scripts/premise_block.sh` from the main tree. The K2 files are byte-identical to the PIN and to the
builder's table in its report; both patches apply at the PIN (a temp index, nothing written but a scratch index file);
the hook is registered nowhere (the `[rc=1]` is grep's exit code for three zero counts). Expected to differ: nothing.

```
$ git merge-base --is-ancestor e2f4f08 HEAD && echo e2f4f08-is-an-ancestor-of-HEAD
e2f4f08-is-an-ancestor-of-HEAD
$ git log -1 --format=%s e2f4f08 | cut -c1-60
K2 round 4 landed: provenance by blob, the redesign round (t
$ git diff --stat e2f4f08 HEAD -- scripts/filepacks.py tests/test_filepacks.py scripts/codemap.py tests/test_codemap.py tasks/briefs/jev-trim/K2-registration.patch tasks/briefs/jev-trim/K2-post-commit.patch | wc -l
0
$ sha256sum scripts/filepacks.py tests/test_filepacks.py scripts/codemap.py tests/test_codemap.py tasks/briefs/jev-trim/K2-registration.patch tasks/briefs/jev-trim/K2-post-commit.patch tasks/briefs/jev-trim/K2-R4.patch | cut -c1-16,65-
31606f07fa64c948  scripts/filepacks.py
32d3bcd4e7935ed7  tests/test_filepacks.py
e1a56e0b0cf8e8ed  scripts/codemap.py
d8002fbbeb8217ae  tests/test_codemap.py
1dc53684b8ae5490  tasks/briefs/jev-trim/K2-registration.patch
71ba4c2c0cec81ab  tasks/briefs/jev-trim/K2-post-commit.patch
7e126aea056518cb  tasks/briefs/jev-trim/K2-R4.patch
$ git show e2f4f08:scripts/filepacks.py | grep -n '^def _committed_only'
573:def _committed_only(pack, rel, packs, graphs):
$ git show e2f4f08:scripts/codemap.py | grep -n '^def _committed\|^def _named_here\|^def _provenance\|^def _proven'
669:def _committed(root, commit, files):
699:def _named_here(data, rel, names):
729:def _provenance(root, rel, commit, gn_sec, gn_recs, crg_sec, tests):
758:def _proven(prov, graph, f):
$ T=$(mktemp) && GIT_INDEX_FILE=$T git read-tree e2f4f08 && GIT_INDEX_FILE=$T git apply --check --cached tasks/briefs/jev-trim/K2-registration.patch && GIT_INDEX_FILE=$T git apply --check --cached tasks/briefs/jev-trim/K2-post-commit.patch && echo both-patches-apply-at-e2f4f08; rm -f $T
both-patches-apply-at-e2f4f08
$ grep -c 'filepacks' .claude/settings.json scripts/install_session_hooks.py /home/user/.claude/settings.json
.claude/settings.json:0
scripts/install_session_hooks.py:0
/home/user/.claude/settings.json:0
[rc=1]
$ ls /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r3/probe_r3.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r3/probe_nd7.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r3/mutdrv4.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/k2-lane-353/r4/vk/probe_r4.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/k2-lane-353/r4/mutdrv_r4.py | wc -l
5
$ bash scripts/pc_suite.sh set-id -- tests/test_filepacks.py | tail -1
1 files set=db64e610236b
$ bash scripts/pc_suite.sh set-id -- tests/test_codemap.py tests/test_system1_context.py | tail -1
2 files set=395f8af3a0ce
```
