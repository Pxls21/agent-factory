# VERIFY-K2-R4: the verifier's report of record (task #353)

> **Coordinator note (2026-09-30 08:3xZ).** The round-3 verifier, resumed for round 4, came home at 08:2xZ; its
> hand-back is saved verbatim below (harvest run s-20260930T082921Z-0f29ed: 949 assistant records, every one
> claude-opus-5-5, 0 refusal stops; hand-back sha256 prefix 4c35ca4025fa). The harness marked the hand-back as
> instruction-shaped (a settings-json pattern): it describes the registration patch's hook order, and nothing in it
> was acted on. Recommendation: NOT-READY on R4-1, the SAME class. The coordinator's gate: NOT-READY.
> **D-115's exit.** The round-4 brief set it before the dispatch: a same-class blocker in round 4 means no round 5,
> and K2 goes to the owner as RE-SCOPE or PARK. The round table:
>
> | Round | Verify | Blocker |
> |---|---|---|
> | 1 | MERGE-READY-WITH-FOLLOWUPS on one condition | F1: a stale index let an untracked file's text through |
> | 2 | NOT-READY | B1: untracked callers through a tracked file's code part |
> | 3 | NOT-READY | R3-1: a caller's name from a file's untracked era, after the file is committed |
> | 4 | NOT-READY | R4-1: `git reset --mixed` or `--soft` moves HEAD back and runs no hook, so the packs stay on the undone commit (callers, a test, an untracked file's symbols, an uncommitted ledger line) |
>
> The failing assumption, after four rounds: that a pack built at a commit still describes the tree the model reads.
> Round 4 made each name true at build time (the committed blob); git moves HEAD without a hook, and the reader never
> compares the build with HEAD. The verifier's discriminator (a 10-line HEAD check in the reader) turns every point
> after the reset to 0 bytes with the controls green.
> **The options for the owner:** RE-SCOPE (the builder's pick; the verifier agrees on two conditions: (a) the file's own
> symbols come from the committed blob's AST, never from graft, which closes NOT done 7; (b) the reader injects nothing
> unless the build's tree equals `HEAD^{tree}`, trees not commits, so push_clean's same-tree ref move keeps the packs,
> which closes R4-1, the ledger part included). RE-SCOPE drops the callers-and-tests surface, where the class lived for
> four rounds; the cost is one HEAD-tree read per hook call. Or PARK: K2 stays off (it was never registered). The
> coordinator recommends RE-SCOPE with both conditions, as a new contract with one build round and its verify.

---

## Round 4

Written 2026-09-30 from `Wed Sep 30 08:25:15 UTC 2026` (date -u).

**Recommendation: NOT-READY on one blocker, R4-1. It is in the SAME class.** Every piece of evidence it rests on is reproduced through the real patched hook. The redesign works for every shape that goes through a commit: R3-1's two shapes, NOT done 1 and NOT done 9 are closed [R]. But the build snapshot follows the last post-commit build, not HEAD. `git reset --mixed HEAD~1` or `git reset --soft HEAD~1` moves HEAD back and runs no hook. Until the next commit, the model is then shown untracked callers, an untracked test, an untracked file's own symbols and an uncommitted ledger line [R]. Under D-115 there is no round 5, so K2 goes to the owner as RE-SCOPE or PARK. I agree with RE-SCOPE on two conditions, not one (section 6).

Scratch: `S4=/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r4`. Tags: [R] reproduced, [S] static, [I] inferred.

### 1. Premise
- I ran `bash scripts/premise_block.sh` from the main tree at 06:4xZ. It printed 11 commands. The output is identical to the brief's block: both texts hash to `2e3e45f0b9a9e2ed` (`$S4/premise_expected.txt`, `$S4/premise_actual.txt`). This rules out CONTRACT-INVALID.
- My worktrees held the landing's bytes:
  - filepacks.py `31606f07fa64`
  - test_filepacks.py `32d3bcd4e793`
  - codemap.py `e1a56e0b0cf8`
  - test_codemap.py `d8002fbbeb82`

### 2. Gates
Setup for every gate:
- `$S4/wt` was detached at e2f4f08. `$S4/wtboth` was the same commit with both K2 patches applied.
- `--basetemp` was a pytest argument under `$S4/bt`. Each call took under 10 minutes.
- Counts are pasted from `test_summary.sh`.

| Set | Tree | Result |
|---|---|---|
| `1 files set=db64e610236b` (test_filepacks.py), run A | wt | `pytest-summary: 188 passed in 254.18s (0:04:14)`, exit 0 |
| same, run B | wt | `pytest-summary: 188 passed in 269.17s (0:04:29)`, exit 0 |
| `2 files set=395f8af3a0ce` (test_codemap.py, test_system1_context.py) | wt | `pytest-summary: 209 passed in 461.02s (0:07:41)`, exit 0 |
| `2 files set=2415789b9582` (test_session_hooks.py, test_search_intercept.py) | wtboth | `pytest-summary: 144 passed in 54.85s`, exit 0 |
| `1 files set=21e700b8344c` (`-k test_committed_manifest_matches_fresh_generation`) | wtboth | `pytest-summary: 1 failed, 56 deselected in 1.38s`: the drift is line 20, the `.claude/` row, as the brief expects |

- `vendored_manifest.py --check` in wtboth exits with rc 1, one drift. It is on line 20, the `.claude/` row: the committed hash is `15a1c639…` and the generated one is `f880024c…`. The brief expects this.
  - The builder measured a different pair at its own PIN, 14ecd8b.
  - Regenerate this row at the registration's landing base.
- Hook order in wtboth's `.claude/settings.json`:
  - **SessionStart:** session-start.sh, task_sync, `filepacks.py hook --reset`, ls_req. The reset comes before the chat form.
  - **PreToolUse:** search-intercept, system1-context, `filepacks.py hook`. K2's hook is last.
- Hook counts:
  - `hook_count` of the repo settings is 14.
  - The fresh-install test asserts the families `{ls_req: 3, filepacks: 2}` and 15 in all. It passes.
  - The builder's seven registration and pre-image mutants are killed (item 8).

### 3. The scope items

**Item 2: the builder's blob tie.**

- **Real-graph probe of odd caller files [R].**
  - Setup: `probe_d1.py` (log: `logs/probe-d1.txt`) ran real graft, GitNexus and code-review-graph with a temp HOME, then the landing's `codemap.py build`.
  - The callers of one function sit in these files:
    - a decorated def
    - a decorated staticmethod
    - a method
    - a path with a space
    - a non-ASCII path (`scripts/été.py`)
    - a CRLF file
    - a module-level call
    - a tracked symlink to a tracked file
  - What I found:
    - Every provenance blob equals git's own blob id.
    - Every regular file is vouched for (indexed equals blob), including the space, non-ASCII and CRLF paths.
    - Decorated callers carry their def line (`deco_caller` :6, `smeth_caller` :12), so D1 passes them.
    - GitNexus indexes the symlink `link.py` with its target's bytes, so its record never equals the link's blob. Its names drop, and the symbol's total becomes None. This fails closed.
- **A record newer than its nodes, or a re-index between the Cypher answer and the record read [S].**
  - D1 is the backstop. A name must be a def of that bare name that starts on that line of the committed blob.
  - A name from other bytes passes only by coincidence. Then the shown name is committed text, and only the edge can be wrong.
  - `builder-names-unchecked` removes all of D1. It is killed by `provenance-record-lies` in my gates.
- **D1 clause by clause:** see item 8. The line clause, the word boundary, the SyntaxError branch, the `<module>` exemption and the dotted base each have no killing test.
- **Dotted names [S].**
  - Q_CALLERS returns `a.name` (codemap.py:67-68), which is bare in the pinned GitNexus.
  - D1 checks only the part after the last dot. So a dotted name's prefix would go unchecked.
  - That is harmless today: my mutant `d1-dotted-full-name` survives because no dotted name occurs.
- **`<module>` callers** carry a path and a line, never text of the file [S]. In probe_d1, `modlevel.py` is vouched for.
- **Path edge cases [R builder side, S BLOBS side].**
  - Spaces and non-ASCII work end to end. `_committed` sends whole lines to `cat-file --batch`. BLOBS.txt comes from `ls-tree -r -z` with `core.quotePath=false` (filepacks.py:857, 1008).
  - A path with a tab never enters BLOBS.txt (filepacks.py:1012), and a path with a newline is never asked (codemap.py:676). Both drop.
  - A gitlink is not a blob, and a path inside a submodule is not in the tree. Both drop [S].
- **CRLF and filters:** see item 10.

**Item 3: the reader.**

- **In-process fuzz of `_committed_only` [R]** (`fuzz_reader.py`, `logs/fuzz-reader.txt`): 12 of 12 cases behave as expected.
  - The control shows its caller, test and total.
  - Each malformed record hides every name and the total:
    - a legacy pack with no provenance
    - a list in place of the provenance, or of a graph's section
    - a string record
    - an int blob
    - a missing `indexed`, or a missing `blob`
    - `{blob: None, indexed: None}` (a file untracked at the build)
    - another blob id, a 39-character prefix of it, or the id in upper case
  - Odd pack shapes fail closed:
    - An int `symbols` or an int `sample` raises TypeError. The hook's catch-all (filepacks.py:840) then injects nothing.
    - A dict caller file, a string `caller_files` or a caller path with a newline shows nothing from that caller.
- **A stale BLOBS.txt from a stalled build:** NOT done 9 is closed [R] (item 4).
- **The file-itself freshness clause:** the builder's mutants `same-file-names-from-stale-graphs` and `keep-rel-any-graph` are killed in my gate runs [R].
- **The trust root [S]:**
  - It is sound against accidental leaks. It is not sound against a writer in the working tree.
  - Anything that can write `.jev/codemap/` can plant provenance: a lane, a script, or the model's own Write.
  - The post-commit hook runs the working copy's codemap.py and filepacks.py (the AF-AP-222 class).
  - Such a writer could just as well edit the hooks, so I rate this INFO.

**Item 4: R3-1 and the class on the landing.**

- **D9 is true [R].** probe_r4.py differs from probe_r3.py only in its anchor line. Its docstring still names `_tracked_only`.
- **late-outside is closed [R].** At every point, no early canary is in alpha's pack or in the model's context. The Edit line reads `callers in tracked files (the total is left out): __init__ scripts/alpha.py:10`.
- **late-track is closed [R].** In the window (c2's build done, its refresh still running) the line is the same. After the refresh, the later caller shows.
- **Class shapes from the brief:**
  - **A committed file edited and left uncommitted, then re-indexed:** nd1 is closed [R].
  - **`git reset --mixed` and `git reset --soft`:** these leak. This is R4-1 [R].
  - **A third version:** covered by the builder's `provenance-record-lies` and D1 [S].
  - **`git stash`:** no leak [S]. Stash puts the working tree back to HEAD. The packs were built with the edit present, so the tie had already dropped its names. A pop brings back text that the packs never held.
  - **A rename:** a committed rename goes through the hook and is rebuilt. An uncommitted `git mv` leaves the new path out of TRACKED.txt, and the old path's names are still committed at HEAD [S].
  - **A second worktree:** it keeps its own `<root>/.jev` state (filepacks.py:74, 470) [S].
  - **Branch switch, checkout, fast-forward merge, pull:** nothing rebuilds, because the repo's hooks are only commit-msg, post-commit, pre-commit and pre-push. Files the new HEAD lacks are deleted from the working tree. Files it adds are not in TRACKED.txt. The result is stale committed text, not untracked text [S].
- **Design input for R4-1's fix:** `scripts/push_clean.sh:69-72` runs `update-ref` to move the branch to origin's rewritten commit, which has an identical tree, and no hook runs. So after every push, BUILD.json's commit differs from HEAD while the tree is the same.

**Item 5: NOT done 7 [R]** (`logs/nd7-*.txt`).

- **The window:** over 7 runs, the time from the stamp to graft's first index open was min 860.5, median 895.8 and max 987.4 ms.
- **Forced race, tracked shape:** `leak_<CANARY>` shows on Read, in the symbols line. The pack's blob equals BLOBS.txt's, and graft reads fresh.
- **Forced race, untracked shape:** the canary shows on Read and on Edit, including the signature `def leak_<CANARY>(token="<CANARY>-arg")`.
- **Grade: the SAME class. The FOLLOW-UP rating stands under D-034.**
  - The interleaving is forced: a PATH shim acts inside a window of about 0.9 s.
  - The leaked text is the touched file's own text, which the Read returns anyway.
  - It is not "the one known channel", because R4-1 is another.
  - Any RE-SCOPE must close it (condition (a) in section 6).

**Item 6: the adjacent defects 2a to 2d.**

- **2a [R]** (nd1, nd9, reset and late-* logs):
  - The line reads `tests of the file (code-review-graph) 0 (none found; a test that runs the file as a subprocess leaves no edge)`.
  - Committed tests exist and were withheld. In nd1, test_trk_t.py's committed test drops because that file has an uncommitted edit.
  - This is a false statement the model reads.
- **2b [S]:** `unmatched` is in the pack JSON and is never rendered.
- **2c [R]:** nd1 shows `risk LOW — GitNexus: 4 impacted within 3 hops, 4 direct (tests excluded)` beside one shown caller. These are numbers and a level, never text.
- **2d: a surrogate reproduction plus static analysis.**
  - The surrogate (`probe_2d.py`) uses a fake GitNexus session that answers a Cypher call with a non-empty list.
    - `_rows` then raises with `str(val)[:80]`.
    - The rendered risk line reads `risk: none — GitNexus error (ValueError: a Cypher answer of an unknown shape: [{'name': '<CANARY>', 'file': 'scripts/untracked_x.py'}])`.
  - Why there is no live path with the pinned GitNexus 1.6.10 [S]:
    - It answers struct rows with a dict and empty results with `[]`.
    - json's own errors carry only positions. The other messages carry only counts.
  - If this path ever fires, it is the SAME class.

**Item 7: the class test and its controls [R]** (`class_split.py`, `logs/class-split-*.txt`).

- **Each guard alone keeps the context clean at all six observation points.**
  - **Builder tie off, real reader:** alpha's pack holds every canary (a, b, c1, d1, e, u1, u1t, u9). The context holds only the committed controls (ok, okt, c2).
  - **Reader tie off, real builder:** alpha's pack holds only committed names. `trk`, `u1` and `u9` sit only in their own file's pack (D3). The context holds only the committed controls.
- **So the leak control fails for the guard's reason.** With either guard on, nothing leaks. With both off, every LEAKS canary reaches the model (asserted, and green in both gate runs).
- **D2 is confirmed.**
  - The class test's `[real]` variant sees the builder guard: `class-builder-tie-off` is KILLED because canaries reach the packs.
  - It cannot see the reader guard: `class-reader-tie-off` SURVIVES.
- **The reader clauses are proven through the real reader.** Planted packs cover every clause in the builder's table, and all are killed in my gates. One exception: the `+ [rel]` term of `all_kept` (item 8).
- **Every class-test shape passes through a commit.** None moves HEAD without one, so R4-1 lies outside them.

**Item 8: mutation.**

- **The builder's `mutdrv_r4.py`, in wtboth [R]:**
  - Control: `6 passed in 68.28s`.
  - 9 of 9 as expected: the 7 registration and pre-image mutants are KILLED, `class-builder-tie-off` is KILLED with the class message, and `class-reader-tie-off` SURVIVES (by design).
  - The restored sha256 values equal the originals. `logs/mutdrv-r4.txt`.
- **My round-3 `mutdrv4.py`, on the landing [R]:**
  - Control: 4 of 4 PASS.
  - KILLED by their target checks: r3-tests-by-gitnexus, r3-callers-by-crg, r3-fresh-unless-stale, r3-clause-not-indexed-passes, r3-sample-shrink-ignored.
  - INVALID:
    - r3-listed-substring, r3-keep-rel-any-graph and r3-files-not-list-ok: their anchor count is 0, because round 4 replaced `listed(...)`.
    - r3-tests-rel-unfiltered: its replacement calls `listed`, which no longer exists. The result is a NameError, not a kill.
  - The builder's table ports all nine to round 4's code, and they pass in my gates.
- **My ten new round-4 mutants [R]** (`mutdrv_v4.py`, `logs/mutdrv-v4-[a-g].txt`):
  - Each call ran its control first, with `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared.
  - Each mutant was applied in place in `$S4/wt`, then restored and checked by sha256. `git status` of wt was clean after every call.
  - Controls: 5 provenance checks `5 passed` (59.26 s, 53.88 s), all 13 codemap checks `13 passed` (70.53 s, 72.40 s), the class test `1 passed` (69.35 s, 67.77 s), the 67 planted-pack checks `67 passed` (34.33 s).

| Mutant (file) | Change | Checks run | Result |
|---|---|---|---|
| committed-misaligned (codemap `_committed`) | `i += n` for `i += n + 1` | 5 provenance | KILLED: provenance, provenance-same-file, provenance-record-lies, pack-fields |
| blob-str-unchecked (filepacks `proven`) | `"blob" in rec` for the str check | 67 planted-pack | KILLED: blob-tie, untracked-callers |
| d1-line-insensitive | a def of that name on any line | 5, 13, class | SURVIVED |
| d1-nonpy-substring | word boundaries dropped | 5, 13, class | SURVIVED |
| d1-syntaxerror-true | an unparseable blob passes | 5, 13, class | SURVIVED |
| d1-module-not-exempt | `<module>` fails (the fail-closed direction) | 5, 13, class | SURVIVED |
| d1-dotted-full-name | base = the full name | 5, 13, class | SURVIVED (equivalent: names are bare) |
| crg-hash-skipped | code-review-graph's record not compared | 5, 13, class | SURVIVED |
| rel-not-named | the file itself not always in the provenance | 5, 13, class | SURVIVED (equivalent in the fixtures) |
| all-kept-without-rel (filepacks) | `files` for `files + [rel]` | 67 planted-pack | SURVIVED |

What the survivors mean [S]:
- Only `d1-syntaxerror-true` would open a path if the code had it. That takes an unparseable committed Python caller whose graph record equals the blob while its nodes came from other bytes. The landing returns False there; only the test is missing.
- Every other survivor lets through committed text only, or changes a count.
- The builder's claim that "test_codemap's provenance checks kill every builder clause" holds for item 1's named clauses. It does not hold for D1's sub-clauses or for code-review-graph's own record check.

**Item 9:** see section 2.

**Item 10: the AP tells.**

- **AP-32** at codemap.py:694 (`_committed`: sha256 of the blob's bytes) and test_codemap.py:493, 528, 534 and 607. **Real tell, reviewed safe.**
  - Each graph's record is the sha256 of the bytes that graph read from the working tree: GitNexus's `meta.json` fileHashes, and code-review-graph's File `file_hash` by realpath. The builder hashes the committed blob's bytes.
  - The two agree exactly when the checkout converts nothing. This repo has no `.gitattributes`, and `core.autocrlf` and `filter.*` are unset (git config rc 1). `ls-files --eol` shows 39 CRLF files, identical in the index and the working tree.
  - Real records match the builder's hash in these controls:
    - check_provenance: `cached` keeps 2 callers, fetch and main
    - the class test: ok, okt and c2 show
    - probe_d1: the CRLF file is vouched for
  - With autocrlf, a smudge filter or LFS, every name from such a file drops. This fails closed.
  - The tests write records in the same form the real graphs use.
- **AF-AP-175** at test_codemap.py:466, 469, 497 and 546, and test_filepacks.py:1127, 1189, 1194, 1225 and 1997. **Real tell, reviewed safe.**
  - Each resolves HEAD in a fixture repo right after the test's own commit. The post-commit jobs never commit.
  - Production's `_head` (codemap.py:665) reads HEAD once per build and passes it on. The reader never reads HEAD at all, and that is R4-1's root.
- **AF-AP-40** at test_filepacks.py:1918 and 2006. **Real tell, reviewed safe.**
  - Both are waits that require a log line before a deadline. A missing file keeps the loop polling until it asserts.
  - The lock loop's `if not exists: continue` skips a lock no job made. `fixture_processes` checks for leftover jobs on its own.

**Item 11:** see section 2.

### 4. Finding inventory (no severity filter)

**1. BLOCKER, SAME class. R4-1: a reset leaves the packs on the undone commit. [R]**

*What happens:*
- Only a post-commit build refreshes TRACKED.txt, BLOBS.txt, the code packs and P2.
- The reader compares nothing with HEAD. Its boundary is "tracked at the last build" (filepacks.py:52).
- `git reset --mixed HEAD~1` and `git reset --soft HEAD~1` move HEAD back and run no hook. The probe logged `a hook job started: False`.
- So names from files that are now untracked or uncommitted reach the model:
  - **Edit in alpha.py's `helper`, after the reset (1153 B):**
    - `callers 3 (1 in tests): <RST> scripts/caller_r.py:4 · __init__ scripts/alpha.py:10 · test_<RSTT> tests/test_r.py:6`
    - `tests of the file (code-review-graph) 1: tests/test_r.py:6 test_<RSTT>`
  - **Read of the untracked `scripts/caller_r.py` (442 B):** `symbols: <RST> L4-5`
  - Both are the same 30 s later. `TRACKED.txt lists caller_r.py: True; BUILD.json commit acf1b64` (c1), while HEAD is 277de75.
  - **The soft reset:** the same injections, while status lists both files as `A`.
  - **The P2 half** (the part RE-SCOPE keeps): a ledger line committed at c1 is no longer in HEAD's ledger after the reset, only in its working copy. A Read of beta.py still injects `ledger L10: **T9 HOME.** <LEDGERLINE>: a line naming scripts/beta.py` (217 B).
- Everything clears only after the next commit's build.

*Evidence and reproduction:*
- Logs: `logs/reset.txt`, `logs/reset-soft.txt`, `logs/reset-p2.txt`.
- Reproduction (about 90 s for `reset`, 20 s for `reset-p2`):
  - `git -C /home/user/agent-factory -c core.hooksPath=/dev/null worktree add -q --detach <W> e2f4f08`
  - `VK2_WT=<W> python3 $S4/probe_r5.py $S4 reset`, or with `reset-soft` or `reset-p2` in place of `reset`
- Discriminator:
  - `VK2_WT=<W> VK_FP_TEXT_FILE=$S4/disc/filepacks_head_check.py python3 $S4/probe_r6.py $S4 reset`, and the same with `reset-p2`.
  - The discriminator is a 10-line scratch HEAD check in `Packs.built()`. It is not a proposed patch.
  - Result: `injected 0 B` at every point after the reset, in both modes. The controls stay green: before the reset the names show (1153 B), and after c2 the committed caller shows. Logs: `logs/disc-reset*.txt`.

*Grading:*
- Contract mapping: verify brief item 13, the coordinator's class definition, and round-4 brief item 2 ("in no pack at any point"). Item 1's letter ("the tree the build names") is met; the class invariant is not.
- Canonical path: the real patched post-commit hook, real graft, GitNexus and code-review-graph, and the real hook command (REG_PRE), at the landing's bytes.
- Material effect: names from untracked files the model did not touch, an untracked file's own symbols, and a verbatim uncommitted ledger line. This covers the common flow "commit by mistake, then `git reset HEAD~1`".

*Suggested fix:* the reader injects nothing unless the file-pack build's tree equals `HEAD^{tree}`.
- Compare trees, not commits. push_clean's same-tree ref move would otherwise blank every pack after each push.
- The build can record its tree in BUILD.json.

**2. FOLLOW-UP, SAME class. NOT done 7: graft's stamp-then-read race [R, forced].**
- Details are under item 5.
- Contract mapping: the class.
- Canonical path: only with a forced interleaving.
- Fix: the file's own symbols from the committed blob's AST. Or check graft's symbols against that AST and stamp again after the read.

**3. FOLLOW-UP, ANOTHER class (a false statement). 2a: "none found" when tests were withheld [R].**
- Fix: say "N withheld (not committed)" in place of "none found". This goes away under RE-SCOPE.

**4. FOLLOW-UP, ANOTHER class (numbers). 2c: the risk level and the impacted and direct counts include untracked files [R].**
- These are numbers and a level, never text.

**5. FOLLOW-UP, SAME class if it fires; UNVERIFIED as live. 2d: the note path [surrogate R, S].**
- A malformed Cypher answer's first 80 characters render in the risk line.
- The pinned GitNexus gives no live path.
- Fix: never echo answer text in a note.

**6. FOLLOW-UP. Mutation gaps [R].**
- No test proves D1's five sub-clauses, code-review-graph's own record comparison, the file always being named, or the reader's `+ [rel]`.
- The builder's clause-level claim is overstated to that degree.
- Fix, one check each:
  - a name defined on another line of the blob
  - a non-Python substring
  - an unparseable committed caller under a record lie
  - a crg-only record lie
  - a same-file name that fails D1 while GitNexus reads fresh

**7. INFO. The file-level tie costs whole files [R].**
- Any uncommitted edit in a caller file drops all its names, committed ones too (nd1: the committed `trk` caller and test). This feeds item 3.

**8. INFO. A symlinked caller file drops its names and the symbol's total [R probe_d1].** This fails closed.

**9. INFO. The trust root [S].**
- Any writer of `.jev/codemap/` can plant provenance.
- The hook runs the working copy's codemap.py and filepacks.py.

**10. INFO. Pack JSON on disk holds untracked paths and working-copy symbols [R].**
- Untracked paths sit in `caller_files` and in the provenance keys (nd1: `caller_new.py`, `test_new_u.py` in alpha's pack).
- The file's own working-copy symbols are there too (D3).
- No renderer prints them.

**11. INFO. Registry messages come from the working copy of `.claude/hooks/edit-snapshot.py` at build time [S].**
- The same working copy runs live as the PostToolUse hook and injects the same messages.

**12. INFO. `codemap.py lookup` and `codemap.py demo` read packs without the reader's blob check or `_committed_only` [S].**
- They are manual tools. The builder filters callers and tests first, but the file's own working-copy symbols show.

**13. INFO. Other HEAD moves give stale committed text, not untracked text [S].**
- This covers branch switch, checkout, fast-forward merge, pull and stash.
- push_clean moves the ref to a same-tree commit (push_clean.sh:69-72). This is design input for item 1's fix.

**14. INFO. 2b: `unmatched` is in the JSON and never rendered [S].**

**15. INFO. WIDEN_CAP [S].**
- Under the blob tie, a pack it leaves stale can hold only names whose file's blob is unchanged. That is staleness, not untracked text.

**16. INFO (closed). R3-1, NOT done 1 and NOT done 9 are closed [R].**
- Logs: `late-*.txt`, `nd1.txt`, `nd9.txt`.
- nd9: `u9` never shows. After the build, TRACKED.txt drops the file.

**17. INFO. The class test and D2 behave as the builder states [R]** (item 7).

**18. INFO. Four of my round-3 mutants are INVALID on round 4** (item 8). The builder's ports cover them.

**19. INFO. The manifest's `.claude/` row pair (15a1c639 / f880024c) differs from the builder's measurement at 14ecd8b** (section 2).

**20. INFO. The hook's state log `filepacks.jsonl` stores symbol names [R].**
- Under the NOT done 7 race, a record key held the canary's name. This is a state file, not the model's context.

**21. INFO. Evidence audit [R].**
- The builder's premise table, D2, D9, the mutdrv_r4 results (9 of 9, same sha256 values) and every gate count reproduce.

### 5. Blocking predicate and recommendation

R4-1 meets all five conditions:
1. **Contract mapping.** Verify brief item 13 and the coordinator's class definition, both frozen before dispatch, plus round-4 brief item 2.
2. **Canonical reproduction.** The real patched hook, the real graphs and REG_PRE, at e2f4f08.
3. **Material effect.** Untracked and uncommitted text in the model's context. It lasts until the next commit.
4. **Concrete discriminator.** A deterministic probe. A 10-line HEAD check turns every point after the reset to 0 B, with the controls green.
5. **Task ownership.** The fix sits in filepacks.py's reader, inside K2's boundary.

Its class is the SAME. No other finding meets the whole predicate.

**NOT-READY on R4-1 (SAME class).** Under D-115's exit, K2 goes to the owner as RE-SCOPE or PARK. This recommendation rests only on reproduced evidence.

### 6. The item-7 pick: RE-SCOPE, on two conditions

I agree that RE-SCOPE beats PARK, but only with both conditions:
- **(a) The builder's condition.** The file's own symbols come from the committed blob (the AST for Python, none for other languages), never from graft.
  - It closes NOT done 7: graft's symbols can come from bytes read about 0.9 s after the stamp, and a committed blob cannot change.
- **(b) Mine.** The reader injects nothing unless the file-pack build's tree equals `HEAD^{tree}`.
  - It closes R4-1 in every part of a pack.
  - RE-SCOPE as framed keeps P2, and reset-p2 shows P2 carrying an uncommitted ledger line [R]. So the builder's premise ("the committed-text part … has not been a blocker in four rounds") no longer holds.

Why RE-SCOPE and not PARK:
- With (a) and (b), every byte a pack shows comes from HEAD's committed tree, and no derived graph is in the path. That is a small surface a test can pin.
- The callers-and-tests surface goes. That surface held the class for four rounds, and 2a, 2c, 2d and the mutation gaps go with it.

PARK is the better pick if either holds:
- the owner will not pay one HEAD-tree read per hook call;
- the owner judges packs without callers and tests not worth their context bytes (the builder's value question).

### 7. What must hold before registration (round 4's bytes)
1. R4-1 is closed by a tree check in the reader, covering every part of a pack. A committed real-hook test covers the reset shapes (mixed, soft, P2), each with a leak control. A control shows that a same-tree ref move (push_clean) keeps the packs.
2. NOT done 7 is closed by condition (a), or by an AST check of graft's symbols plus a stamp after the read.
3. The owner rules on RE-SCOPE or PARK (D-115). Items 4 and 5 apply only if callers and tests survive the ruling.
4. The tests line never says "none found" when tests were withheld (2a).
5. No answer text goes into a note (2d). There is one check per D1 clause, and one for code-review-graph's own record (item 6 of the inventory).
6. `K2-post-commit.patch` lands with or before the registration. One build at HEAD writes TRACKED.txt, BLOBS.txt and BUILD.json before any session loads the hook.
7. The manifest's `.claude/` row is regenerated at the landing base.
8. Whichever registration patch lands second is rebased, with its counts recomputed through `hook_count`.
9. The patched tree passes `db64e610236b` twice, `395f8af3a0ce`, `2415789b9582` and `21e700b8344c` (after regeneration), plus the new reset test.
10. The patched installer lands only with the owner's yes (setup.sh registers hooks at every session start).
11. The owner accepts the issue-#83 findings as known gaps.

### 8. Reproduced, static, skipped
- **Reproduced:**
  - the premise and every gate
  - late-outside and late-track
  - reset, reset-soft and reset-p2, and the discriminator
  - nd1, nd9, the nd7 window and both races
  - mutdrv_r4, my mutdrv4 and my ten new mutants
  - the item-9 gates
  - the AP screens
  - the reader fuzz, probe_d1 and class_split
  - the 2d surrogate (a surrogate, labeled as one)
- **Static:**
  - 2b, the WIDEN_CAP path
  - stash, rename, second worktree, branch switch, fast-forward merge and pull
  - gitlinks, the trust root, the registry message source, the CLI consumers
  - the pinned GitNexus answer shapes
- **Skipped:**
  - `tests/test_filepacks.py` with both patches: not in the verify brief's item 9, and the builder ran it.
  - A JS or TS caller: the fixture has no cross-language edge. My substring mutant shows the word check is untested.
  - A natural-timing NOT done 7 loop.
  - The issue-#83 items: out of scope.
  - The PC: the rules forbid the bridge.
  - The coordinator's 8-file landing gate: not asked.

### 9. Files and hygiene
- **Probes and drivers** (all in `$S4/`):
  - probe_r5.py: modes reset, reset-soft, reset-p2 and the round-3 modes
  - probe_r6.py: probe_r5 plus `VK_FP_TEXT_FILE`
  - disc/filepacks_head_check.py: the scratch discriminator, sha256 `841072061a1141a0`
  - probe_nd7.py, probe_d1.py, probe_2d.py, fuzz_reader.py, class_split.py
  - mutdrv_v4.py (mine), mutdrv4.py (my copy), mutdrv_r4.py (the builder's, copied)
- **Logs:** `$S4/logs/`, 36 files. **Notes:** `$S4/PROGRESS.md`.
- **Cleanup:**
  - `$S4/wt` and `$S4/wtboth` were removed with `worktree remove --force`, hooks off. `git worktree list` shows none under vk2r4.
  - 0 processes have a cwd under `$S4` or name it on their command line.
  - The fixture directories under `$S4/bt` are removed; `$S4` is now 508K.
- **Rules held:**
  - My only git writes in the shared tree were the worktree add and remove, hooks off.
  - The shared tree's one untracked path, `tasks/briefs/labeling/VERIFY-LS-B12-report.md`, is not mine.
  - `grep -c filepacks` gives 0 in `.claude/settings.json`, `scripts/install_session_hooks.py` and `/home/user/.claude/settings.json` (at 08:24Z).
  - I read no secret file and no transcript. I used no PC bridge, no subagent and no outward action.
  - The builder's scratch was read and copied only.
  - Every stamp came from `date -u`.
- **Slips:**
  - One top-level `cd` (AF-AP-249): a `cd /tmp && grep …` call in the item-2 consumer search. It wrote nothing. Every other call used absolute paths or a `( cd … )` subshell.
  - The probes' exit cleanup killed post-commit jobs by pid that the probes had not waited for: 11 in reset-p2 and 2 in each nd7 race.
- **S1-RATE lines**, each written as its own short text: s1-816b8b9c, s1-b42c1c57, s1-25f13da8, s1-20f6b792, s1-fe62e02b, s1-c9f929e5, s1-88d56305, s1-087b99aa.