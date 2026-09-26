# VERIFY-I59-BCE: attack three batch builds against their contracts (tasks #313, #314, #327; the issue #59 batch)

Role: adversarial-verifier (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/i59/VERIFY-I59-BCE-report.md`
(write it incrementally). If the harness refuses a report-file write ("Subagents should return findings as text"), return the
rest of the report as the text of your final message; never work around the refusal.

PIN: the landing commit on the local branch `i59-landing` (subject "The issue #59 batch landed (task #315): ..."; its parent
is origin eb48880; the premise gives its local id). Cite it as "the landing commit", never by its local id: the push rewrites
that id. The coordinator's worktree of it is `/home/user/i59-landing`: never write there. Make your own:
`git worktree add --detach /tmp/vbce-wt <landing id>` (a world-traversable path: S0-05's legs drop to a unit user), and remove
it with `git worktree remove --force` when done.

The changes under test (each built by a sandbox lane, re-run by the coordinator, never attacked independently):
- **I59-B** (task #313, S0-05): contract `tasks/briefs/i59/I59-B-brief.md`; builder's report `tasks/briefs/i59/I59-B-report.md`.
- **I59-C** (task #314, S0-04): contract `tasks/briefs/i59/I59-C-brief.md`; report `tasks/briefs/i59/I59-C-report.md`.
- **I59-E** (task #327, S0-03): contract `tasks/briefs/i59/I59-E-brief.md`; report `tasks/briefs/i59/I59-E-report.md`.
The builders' claims are hypotheses. AF-AP-169, AF-AP-232 and AF-AP-233 in `docs/INCIDENT-LOG.md` give the classes.

AUTHORIZATION: first-party, defensive work on the owner's own proofs: S0-05's runner creates network namespaces, iptables
rules and holder processes in this sandbox to prove egress containment (its tests already do); S0-03 and S0-04 are secret-leak
hardening. Every test secret is a FAKE string built at run time.

## WHAT TO ATTACK (report every observation; no severity filter)

1. **I59-B's guard** (item 4a): hostile evidence roots: a symbolic link into a clone, a relative path, a path through `..`,
   a root inside a `.git` directory itself, a `.git` FILE (a linked worktree or a submodule), a deep path that does not exist
   yet under a clone, a name with a newline or a Unicode lookalike. Does any reach the first write? Is exit 73 the only way out?
2. **I59-B's sudo handback** (item 4b-c): a symbolic link swapped in during the walk, a hard link, a FIFO, a socket, a device
   node, a mount point, a tree deep enough for RecursionError, a name with a newline; the existing-root refusal (exit 74); the
   root and non-root paths without SUDO_UID behave as at the parent commit (diff the runner's behaviour, not only its text).
   Every exit path the EXIT trap covers (a census failure, INT, TERM, HUP) runs the handback exactly once.
3. **I59-B's signal tests under load.** The coordinator saw four signal-timing tests fail under load (`4 failed, 293 passed in
   420.08s`, one of them the pre-existing `test_e3b_r4_sigint_stops_the_runner_with_130`), then pass alone and in an unloaded
   run: is it the tests' timing, or a real race in the runner's signal handling? Reproduce under load (a CPU hog you start and
   stop by pid) and say which.
4. **I59-B's words and tests** (items 1-3): limit 8's new words against the census's real behaviour; M1 and M4 killed by the
   new tests as FAILED tests.
5. **I59-C** (`do_config`): any input that still puts part of a value on stderr (a custom tag, an alias expansion, a huge
   document, a MemoryError, a read error); the tests' de-vacuous preconditions; the case-folded 8-character window (a leak of
   fewer than 8 characters).
6. **I59-E** (`_read_yaml`): the same classes through the checker's CLI; is `from None` complete, and does any other S0-03 path
   print a YAML-derived value on an error?
7. **Mutation:** reproduce at least three of each builder's mutants as FAILED tests; add a mutant for each contract clause the
   builders' sets do not cover.

## GATE

Apply the blocking predicate of skill `contract-gate`: contract-mapped, reproduced through the real code path, materially
effective, a concrete discriminator, in-boundary. Return one gate recommendation PER CHANGE (I59-B, I59-C, I59-E):
MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID, each blocking finding with its reproduction command.

## BOUNDARY

READ everything. WRITE only your report and scratch under `/tmp/vbce-*` (removed at the end). Never write the coordinator's
landing worktree, the shared tree's tracked files, a tag or a ref. No git writes except your own worktree add and remove.

## STANDING RULES

- No PC bridge, no outward-facing action.
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, and the GH_TOKEN and GITHUB_TOKEN variables.
- Every namespace, rule and process you create is destroyed by name or pid; `ip netns list` is empty at the end.
- Another lane may hold the shared tree (SCRUB2-R1: the scrubber files); `.lanes-live` lists them.
- The disk is shared (about 1.4 GB free, two verifiers beside each other): a worktree of this repo is about 300 MB. Never
  commit in it: the post-commit hook would build about 740 MB of code-intel indexes there (measured on the landing
  worktree). Scratch under 400 MB, the worktree included; a short `--basetemp`; never run the whole
  `tests/test_vendored_manifest.py`.
- Test counts are pasted from `scripts/test_summary.sh`. Stamps are substituted from `date -u`, never typed.
- Long commands in one foreground call, each under 10 minutes; kill by pid only.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short text of
  its own (under 200 characters; a note only for a 0).

## PREMISE — MEASURED at authoring (2026-09-26 11:2xZ, the sandbox; the landing worktree `/home/user/i59-landing`, clean)

The disk floor matters to you too: `tests/test_lane_gate.py` refuses below 1,500 MB free (exit 66), and the post-commit
hook re-indexes any worktree a commit or a rebase lands in (about 740 MB; task #332): never commit or rebase in yours.

```
$ git -C /home/user/i59-landing log -2 --format='%h %s' | cut -c1-80   (the landing commit, local; its parent is origin's head)
e778cf5 The issue #59 batch landed (task #315): four follow-up patches, FU-4, al
8992772 transcripts: scrubbed sandbox chat digests (2026-09-26)
$ sha256sum tasks/briefs/i59/I59-{A,B,C,E}.patch | cut -c1-16
342e8d4225a2d764 I59-A.patch
c46b5dffe358063a I59-B.patch
d048d18f452996a7 I59-C.patch
ea9da2271112fa58 I59-E.patch
$ git -C /home/user/i59-landing show --stat HEAD | tail -1
 43 files changed, 2052 insertions(+), 384 deletions(-)
$ (in the landing worktree, as root) python3 scripts/validate-ledger integrity --root .   -> rc, PRESENT, INVALID
integrity rc=0 PRESENT=12 INVALID=0
$ python3 scripts/ledger-gen --root . twice, then cmp   -> idempotent; validate-ledger integrity --ledger proofs/ledger.json rc 0; stage1-gate rc 0
$ python3 scripts/check-proof-status.py .   -> rc 0, twelve WARNING lines, nothing else
$ bash scripts/test_summary.sh --ignore=tests/test_vendored_manifest.py --basetemp=/tmp/lbt tests/   (the landing, before its rebase onto 8992772, which changed only docs)
pytest-exit: 1
pytest-summary: 10 failed, 5784 passed, 9 skipped, 8 xfailed in 3044.77s (0:50:44)
#   9 of the 10: tests/test_lane_gate.py, each "lane_gate: only 1408 MB free under ...; a tree copy needs about 1 GB
#   (LANE_GATE_MIN_FREE_MB, default 1500): free space first" (exit 66), the sandbox disk, not the landing
#   the 10th: test_i59b_the_handback_runs_when_a_signal_stops_the_run[HUP], load-sensitive (task #331); alone, unloaded:
3 passed, 294 deselected in 5.20s
$ df -Pm / | awk ...
1453 MB free
```
