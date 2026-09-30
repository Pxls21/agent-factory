# VERIFY-K2-RS: attack the RE-SCOPE, round 5 of the round table (task #353, D-117)

Role: the VERIFY-K2 verifier, resumed (rounds 2, 3 and 4; sandbox adversarial-verifier, Opus 5.5). Do NOT spawn
subagents. Return the whole report as your final message (your hand-back); write no report file.

K2 RE-SCOPE landed at origin 2df97aa ("K2 RE-SCOPE landed (task #353, D-117): symbols from the committed blob only;
nothing unless the build's tree is HEAD's"), GATED-PENDING-VERIFY; its CI run #1189 passed before this brief was
pushed. The owner took RE-SCOPE (D-117 item 2) on the two conditions of your round-4 report (section 6): (a) a pack's
own symbols come from the committed blob (Python's AST; none for other languages); (b) the hook shows nothing unless
the build's tree is HEAD's. The callers-and-tests surface is gone. Its report of record is
`tasks/briefs/jev-trim/K2-RS-report.md`: read the coordinator note at its top, then Evidence items 2 to 5 and 7, "Found
and fixed" 1 to 3, "Removed tests", NOT done 1 to 7, DISCREPANCIES 1 to 6 and the Self-attack. Treat every claim there
as a hypothesis. The hook is still NOT registered: `tasks/briefs/jev-trim/K2-registration.patch` and
`tasks/briefs/jev-trim/K2-post-commit.patch` stay unapplied.

## THE ROUND TABLE (D-115)

| Round | Verify | Blocker |
|---|---|---|
| 1 | VERIFY-K2: MERGE-READY-WITH-FOLLOWUPS on one condition | F1: a stale index let an untracked file's text through |
| 2 | VERIFY-K2 round 2: NOT-READY | B1: untracked callers through a tracked file's code part |
| 3 | VERIFY-K2 round 3: NOT-READY | R3-1: a caller's name from a file's untracked era, after the file is committed |
| 4 | VERIFY-K2-R4: NOT-READY | R4-1: `git reset --mixed` or `--soft` moves HEAD back and runs no hook, so the packs stay on the undone commit |
| 5 | this verify (the RE-SCOPE, contract revision 5) | ? |

A core blocker here does not start a repair round by itself: the coordinator puts the round table to the owner
(REDESIGN, RE-SCOPE again, ONE MORE ROUND with a written reason it converges, or PARK; D-115). So name the class of
every blocking finding: a byte HEAD's tree does not hold reaching the model (the classes of rounds 1 to 4), or ANOTHER.

The coordinator's landing gate, in the shared tree: `2 files set=bd8d7c79afbe` (`tests/test_filepacks.py
tests/test_codemap.py`) `pytest-summary: 238 passed in 442.27s (0:07:22)`; `3 files set=804c19143d13` (the same two
and `tests/test_system1_context.py`) `pytest-summary: 379 passed in 473.41s (0:07:53)`; `1 files set=21e700b8344c`
(`tests/test_vendored_manifest.py -k test_committed_manifest_matches_fresh_generation`) `pytest-summary: 1 passed, 56
deselected in 1.50s`.

## SCOPE

1. **Premise.** Re-run the block below with `bash scripts/premise_block.sh` from `/home/user/agent-factory`; on a
   difference, stop and report CONTRACT-INVALID with the diff.
2. **Condition (a), symbols from the committed blob** (`scripts/codemap.py` `_committed`, `_ast_symbols`, `build_one`;
   the reader's skip in `scripts/filepacks.py`, the `symbols_from` check). Attack it: a Python file edited and left
   uncommitted, then rebuilt; an untracked file; a committed blob that does not parse (what does the pack say?); a
   blob that is not UTF-8, carries a BOM or CRLF, or is very large; a symlink, a gitlink, a rename; a missing blob in
   `git cat-file --batch`'s answer; a path with spaces, a newline or non-ASCII characters; a legacy pack that claims
   `symbols_from: "ast"`. Does any symbol, name or line from bytes other than the committed blob reach the model?
3. **Condition (b), the tree check** (`Packs.current`, `_rev`, `HEAD_TIMEOUT`). Attack it: `reset` (`--mixed`,
   `--soft`, `--hard`), a checkout to a branch with the same tree and with another, a detached HEAD, `commit --amend`
   (same tree and another), `git stash`, a second worktree of this repo, a rebase or merge stopped half-way, an unborn
   HEAD, a slow or failing `git` (the 2 s timeout), `GIT_DIR`, `GIT_WORK_TREE` or `GIT_INDEX_FILE` in the hook's
   environment (NOT done 5), a BUILD.json that is missing, not JSON, not an object, or whose `tree` misses OBJECT_RX.
   The builder's by-design residuals (a same-tree move keeps the packs, and P2's subjects then come from the build's
   history; HEAD moving after the check): is each one harmless, and is it stated where the owner will read it?
4. **The marker, `still()` and the id** (new this round; no verify has seen them). A build in flight at each point
   between the `building` marker and the final record, through the REAL reader; ABA across two builds; a crash after
   the marker (fail closed: until when, and what does the next build do?); two builds at once; BUILD.json read while
   it is replaced; `still()` comparing the right bytes after both parts. What does the builder's "the hook shows
   nothing while any build runs" cost in a normal session?
5. **The surface is gone.** No caller, test, callers total, risk line or impacted count may reach the model. The graph
   sections stay in the pack file with no reader: can any of their text reach the output another way (registry rows
   through `_screened`, P2 lines, a note, an error string)? The cost the builder measured from the live refresh log
   (74 runs; wait plus build median 113.1 s, p95 379.3 s, during which a changed file's code part is withheld): check
   it on the log, read only.
6. **The class tests and their controls** (`test_a_reset_shows_nothing_through_the_real_hook` and `reset_scenario` in
   `tests/test_filepacks.py`): do they run the real patched post-commit hook and the registration's command? Does the
   leak control fail for the tree check's reason and no other? The builder's AF-AP-251 fix in that test (a private
   `CBM_RUNTIME_DIR`): is it complete?
7. **The removed tests** (the report's list: 11 checks, 5 tests, 26 filepacks mutants; 4 codemap checks or tests, 10
   codemap mutants). For each, is its failure mode now impossible because the surface is gone, or did a concern that
   still applies lose its test? Name any that still applies.
8. **Mutation.** Re-run the builder's driver (`k2-lane-353/rs/mutdrv.py` under the session scratchpad; its 9
   mutants), control first (AF-AP-223: a `--basetemp` parent that no longer exists makes every mutant error at setup
   and read KILLED), bytecode off, a fresh copy or a cleared `__pycache__` per mutant (AF-AP-192). Re-run the mutants
   of your round-4 drivers that still apply. Write new ones for the tree check and the marker, for example: `still()`
   comparing the tree only; the timeout read as current; `HEAD` in place of `HEAD^{tree}`; the marker written after
   `_clean`; a constant id.
9. **The commit hook's screen tells at the landing** (advisory; the premise pastes the counts): AF-AP-175 (a quoted
   HEAD passed to git; 48, one at `scripts/filepacks.py:543`, the tree check's own call), AF-AP-40 (a presence-gated
   check; 14), AP-32 (hashing in edited code; 10), AF-AP-115 (8), AP-1 (6), AF-AP-72 (3). Say for each whether it is
   real, with the lines; start with the tree check's own call.
10. **NOT done 6:** `codemap.py lookup` and `demo`. Can the model reach them, and can they show bytes HEAD's tree does
    not hold?
11. **The two patches.** Apply `K2-post-commit.patch` and `K2-registration.patch` in a clean worktree at the PIN and run
    `tests/test_session_hooks.py tests/test_search_intercept.py` (`2 files set=2415789b9582`): the hook count through
    `hook_count` (the builder: 15, of which ls_req 3 and filepacks 2), and the order in each list.
    `tests/test_vendored_manifest.py -k test_committed_manifest_matches_fresh_generation` is expected to fail on the
    `.claude/` row while the registration is applied; say so if it does. Never the whole manifest test file: it copies
    about 3.4 GB.
12. **Gates at the PIN**, in your own worktree (never the shared tree), `--basetemp` as a pytest ARGUMENT outside every
    work tree, counts pasted from `scripts/test_summary.sh` with set ids, each call under 10 minutes:
    `tests/test_filepacks.py` twice (`1 files set=db64e610236b`); `tests/test_codemap.py tests/test_system1_context.py`
    (`2 files set=395f8af3a0ce`).
13. **What must hold before registration**, rewritten for these bytes (the builder's NOT done 1, 2 and 4: the
    registration, the manifest's `.claude/` row, and `codemap.py build --all` then one `filepacks.py build` at HEAD).
14. **Gate recommendation** under D-034's blocking predicate (MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY /
    CONTRACT-INVALID). A path that puts a byte HEAD's tree does not hold in front of the model is core-blocking. Each
    blocking finding carries its reproduction command and its class.

Out of scope: the items on GitHub issue #83, unless this round changed them.

## STANDING RULES

- A clean detached worktree at the PIN under your scratch dir (`vk2rs/`), removed at the end; no git write in the
  shared tree (a worktree add and remove, hooks off, is the one exception); no outward action, no PC bridge, no
  subagent.
- NEVER register the hook: never touch `/home/user/.claude/settings.json`, the repo's `.claude/settings.json` or
  `scripts/install_session_hooks.py` in the shared tree, or the live `.jev/filepacks*` and `.jev/codemap`.
- This session's codebase-memory MCP server keeps a daemon (pid 32217) on the real cache; never stop it. Any test or
  probe that runs the real cbm binary on a private cache also gets a private short `CBM_RUNTIME_DIR` (a `mkdtemp`
  under /tmp, removed after; AF-AP-251).
- `scripts/stack.py` runs log into the MAIN tree's `.jev/stacks/` even from a worktree (the builder's D4): leave other
  runs' directories alone.
- Never read a secret file (`.pc-bridge.env`, any `*.env`, any key file); a secret in a test is a fake built at run
  time.
- From transcripts, read only compaction boundaries, record types and `tool_use` inputs, never a thinking block. Print
  only counts, bytes and paths.
- A long gate in ONE foreground call; stamps from `date -u`; commits cited by origin id or subject.
- Never a top-level `cd` (AF-AP-249; the builder breached it three times): use `git -C`, absolute paths or a
  `( cd … )` subshell.
- Never `pkill -f` a pattern your own command line matches; stop every process you start, by pid.
- A worker restart may stop you: your scratch dir survives; resume from it.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- This is defensive testing of the owner's own tooling: each probe is a bound to measure, never an exploit.

Deliver as before: every observation with no severity filter, the blocking predicate, a gate recommendation, the class
of each blocker, and the list of what must hold before registration. Head the report "## Round 5 (RE-SCOPE)" with
"Written 2026-09-30 from <date -u stamp>".

## PREMISE — MEASURED at authoring (2026-09-30 15:0xZ, main tree; PIN origin 2df97aa)

Printed by `bash scripts/premise_block.sh` from the main tree. The K2 files are read from the PIN itself (`git show`);
both patches apply at the PIN (a temp index, nothing written but a scratch index file); the hook is registered nowhere
(the `[rc=1]` is grep's exit code for three zero counts). Expected to differ: nothing.

```
$ git merge-base --is-ancestor 2df97aa HEAD && echo 2df97aa-is-an-ancestor-of-HEAD
2df97aa-is-an-ancestor-of-HEAD
$ git log -1 --format=%s 2df97aa | cut -c1-60
K2 RE-SCOPE landed (task #353, D-117): symbols from the comm
$ git diff --stat 2df97aa HEAD -- scripts/filepacks.py tests/test_filepacks.py scripts/codemap.py tests/test_codemap.py tasks/briefs/jev-trim/K2-registration.patch tasks/briefs/jev-trim/K2-post-commit.patch tasks/briefs/jev-trim/K2-RS.patch scripts/hooks/post-commit | wc -l
0
$ for f in scripts/filepacks.py tests/test_filepacks.py scripts/codemap.py tests/test_codemap.py tasks/briefs/jev-trim/K2-registration.patch tasks/briefs/jev-trim/K2-post-commit.patch tasks/briefs/jev-trim/K2-RS.patch; do echo "$(git show 2df97aa:$f | sha256sum | cut -c1-16) $(git show 2df97aa:$f | wc -l) $f"; done
be82ab16c83a1402 1260 scripts/filepacks.py
0ae34b5c13aaa7d6 2176 tests/test_filepacks.py
15f41cb1400f34f2 1142 scripts/codemap.py
08e48d868a92cedb 1050 tests/test_codemap.py
1dc53684b8ae5490 298 tasks/briefs/jev-trim/K2-registration.patch
3fe1a775b7203205 29 tasks/briefs/jev-trim/K2-post-commit.patch
db5904b424f55c62 2892 tasks/briefs/jev-trim/K2-RS.patch
$ git show 2df97aa:scripts/filepacks.py | grep -n -E '^    def (current|still|record)\(|^def (_rev|_committed_only|_screened)\(|^    def entry\(|^def entry\(|^HEAD_TIMEOUT *='
120:HEAD_TIMEOUT = 2                     # seconds the hook waits for `git rev-parse HEAD^{tree}` (a few ms when it answers)
512:    def record(self):
524:    def still(self):
538:    def current(self):
553:def _rev(root, name):
624:def _screened(pack, packs):
699:def entry(rel, tool_input, budget=PACK_BUDGET, *, packs=None, p2=True):
$ git show 2df97aa:scripts/codemap.py | grep -n -E '^def (_committed|_ast_symbols|build_one|_build|widen|wait_for_graphs)\('
226:def wait_for_graphs(root: Path, rels, graphs, lock_dir: Path, wait: float = 1200.0, grace: float = 30.0,
590:def _ast_symbols(data):
685:def _committed(root, commit, files):
715:def build_one(root, rel, gn, env, commit):
817:def widen(root, changed, gn):
$ git show 2df97aa:scripts/filepacks.py | grep -n -E '"building": True|os\.urandom\(8\)|symbols_from'
36:    VERIFY-K2 F1) and its symbols are that blob's own ast (`symbols_from: "ast"`; else `symbols`: a pack of an older
671:    if pack.get("symbols_from") != "ast":
1099:    _write(str(pdir / "BUILD.json"), (json.dumps({"schema": SCHEMA, "commit": sha, "building": True}, sort_keys=True)
1121:           "ms": round((time.monotonic() - t0) * 1000), "id": os.urandom(8).hex()}   # this build's own (Packs.still)
$ T=$(mktemp) && GIT_INDEX_FILE=$T git read-tree 2df97aa && GIT_INDEX_FILE=$T git apply --check --cached tasks/briefs/jev-trim/K2-registration.patch && GIT_INDEX_FILE=$T git apply --check --cached tasks/briefs/jev-trim/K2-post-commit.patch && echo both-patches-apply-at-2df97aa; rm -f $T
both-patches-apply-at-2df97aa
$ grep -c 'filepacks' .claude/settings.json scripts/install_session_hooks.py /home/user/.claude/settings.json
.claude/settings.json:0
scripts/install_session_hooks.py:0
/home/user/.claude/settings.json:0
[rc=1]
$ ls /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/k2-lane-353/rs/mutdrv.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r4/mutdrv_v4.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r4/probe_r6.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r4/fuzz_reader.py | wc -l
4
$ python3 scripts/ap_screen.py scripts/filepacks.py scripts/codemap.py tests/test_filepacks.py tests/test_codemap.py 2>&1 | grep -E '^[A-Z-]+-?[0-9]+: [0-9]+$' | sort | tr '\n' ' '; echo
AF-AP-115: 8 AF-AP-175: 48 AF-AP-25: 1 AF-AP-38: 2 AF-AP-40: 14 AF-AP-41: 1 AF-AP-70: 2 AF-AP-72: 3 AP-1: 6 AP-24: 1 AP-32: 10 
$ bash scripts/pc_suite.sh set-id -- tests/test_filepacks.py | tail -1
1 files set=db64e610236b
$ bash scripts/pc_suite.sh set-id -- tests/test_codemap.py tests/test_system1_context.py | tail -1
2 files set=395f8af3a0ce
$ bash scripts/pc_suite.sh set-id -- tests/test_session_hooks.py tests/test_search_intercept.py | tail -1
2 files set=2415789b9582
```
