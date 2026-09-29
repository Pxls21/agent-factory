> Coordinator note (2026-09-29 09:3xZ): the report of record, extracted by `scripts/stack.py harvest` (run s-20260929T093439Z-26be5b). Served model: claude-opus-5-5 on all 625 assistant records of this lane (its two rounds), 0 refusal stops, 3 tool-error clusters, 1 compaction. `report_lint`: 2 refs, 1 OK, 1 UNCHECKABLE. Local ids: none cited (a2a25ba, 39d9f82 and d812c9b are origin ids). The six files' sha256 prefixes match the report. Landed GATED-PENDING-VERIFY; the VERIFY-K2 verifier is resumed for round 2; the hook stays unregistered until it passes and the owner says yes to the cost.

# K2 round 2 report (task #353, D-106): F1 closed, the parser fixed, the registration delivered as a patch

Written 09:3xZ, 2026-09-29. This is the original K2 builder, resumed. Contract: `tasks/briefs/jev-trim/K2-R2-brief.md`. PIN: origin 39d9f82. The hook is still NOT registered anywhere.

**Verdict: all nine items are done and gated twice clean on the final bytes.**
- **F1:** closed by the blob check. The post-commit patch alone also closes it; each guard is tested on its own.
  > **Note (2026-09-29 18:5xZ, K2 round 3): falsified.** VERIFY-K2 round 2 found untracked text past the blob
  > check: B1 (an untracked caller's name and path in a tracked file's code part) and B2 (a pack's symbols come
  > from a graph that had indexed other bytes). The repair: `tasks/briefs/jev-trim/K2-R3-report.md`.
- **F2, F3, F4/F5, F14, F12:** fixed. Each has checks, and each check has a mutant that it kills.
- **Registration:** `tasks/briefs/jev-trim/K2-registration.patch` is proven in a clean worktree at the PIN: 137 passed.
- **Deviations:** 5, listed under DISCREPANCIES (1 to 5).
- **Gate run 1 failed** on my own new graft test. I fixed the test and re-gated twice.

Evidence tiers: [V] means verified by a run in this session. [I] means inferred. [A] means assumed.

## 1. Premise re-run (item 1)

**At round start (07:58:23Z):**
- Tree and HEAD: the main tree, HEAD a2a25ba. That commit is the coordinator's "Retro: task #363 registered …", which changes only the ledger and live-state.
- Hashes: the five file hashes matched the brief before any edit: 46ee3aea2f1e428b, 20688549adc7c296, ea28c5add97fac24, a1b9fa4652c47181, 71ba4c2c0cec81ab. [V]
- Unchanged files: `git diff 39d9f82 HEAD --stat` over every file this round reads or changes is empty. [V]
- Result: no difference, so the contract is valid.

**Verbatim block:** I re-ran the premise at 09:30:23Z in a clean detached worktree at 39d9f82, where the files are still the PIN's bytes. [V]
```
$ git merge-base --is-ancestor d812c9b HEAD && echo d812c9b-is-an-ancestor-of-HEAD
d812c9b-is-an-ancestor-of-HEAD
$ git log -1 --format=%s -- scripts/filepacks.py | cut -c1-60
K2 landed (task #353; GATED-PENDING-VERIFY): file context pa
$ sha256sum ... | cut -c1-16,65-
46ee3aea2f1e428b  scripts/filepacks.py
20688549adc7c296  tests/test_filepacks.py
ea28c5add97fac24  scripts/codemap.py
a1b9fa4652c47181  tests/test_codemap.py
71ba4c2c0cec81ab  tasks/briefs/jev-trim/K2-post-commit.patch
9387fceacb47d9e0  tasks/briefs/jev-trim/VERIFY-K2-report.md
$ grep -n '^def _args\|^def _code_part\|^def entry\|^def build(\|    def tracked' scripts/filepacks.py
160:def _args(code, cmd, start):
256:    def tracked(self, rel):
331:def _code_part(rel, ti, root):
377:def entry(rel, tool_input, budget=PACK_BUDGET, *, packs=None, p2=True):
686:def build(root=ROOT, state=None, sha=None):
$ grep -n '^def _load_pack\|^def lookup\|^def file_entry\|^def edit_context\|^def language' scripts/codemap.py
81:def language(root: Path, rel: str) -> str | None:
865:def _load_pack(root, rel):
878:def lookup(path, line, end_line=None, root=None):
918:def edit_context(file_path, old_string, root=None, replace_all=False):
951:def file_entry(path, line=None, end_line=None, root=None):
$ grep -c 'filepacks' .claude/settings.json scripts/install_session_hooks.py /home/user/.claude/settings.json
.claude/settings.json:0
scripts/install_session_hooks.py:0
/home/user/.claude/settings.json:0
[rc=1]
$ ls .../vk2/probe_p6.py .../vk2/mutdrv.py
.../vk2/mutdrv.py
.../vk2/probe_p6.py
$ bash scripts/pc_suite.sh set-id -- tests/test_codemap.py tests/test_filepacks.py tests/test_system1_context.py | tail -1
3 files set=804c19143d13
```

## 2. Files (final bytes; the gates ran on these, compared with `cmp`)

| File | Lines | sha256 | vs PIN |
|---|---|---|---|
| /home/user/agent-factory/scripts/filepacks.py | 1179 | 017ce2be467fbf5304319a5911870ac33e712aada09fb83408fea7395cef8d78 | 423 lines changed |
| /home/user/agent-factory/tests/test_filepacks.py | 1363 | c844aeeb8a4a909749c0128c229e917050535b29e9d6fe325cb92859730edd95 | 490 lines changed |
| /home/user/agent-factory/scripts/codemap.py | 1153 | f504849bf1d4100a5649d484deb42d8c7926d702edfaa0cfad89f60771e1d5fc | +78; readers and `_system1` only |
| /home/user/agent-factory/tests/test_codemap.py | 943 | 76e31571e8008a4dfca11e31b8b5ae47985af4eba5b000ab68d20e43f24da65d | 105 lines changed |
| /home/user/agent-factory/tasks/briefs/jev-trim/K2-registration.patch (NEW) | 224 | 3e8b979120d0638a4b4832a7e6061138aeece56cc46b478ae528651b39d92eee | new |
| /home/user/agent-factory/tasks/briefs/jev-trim/K2-post-commit.patch | 26 | 71ba4c2c0cec81abd5d672d7f89d246a39a11cf0a530523b00d48e15affe9ef1 | UNCHANGED; `git apply --check` passes; the patched hook is fce110fe82d8b183, as in round 1 |

- **codemap.py:** `git diff -U0` shows hunks only in the new `_S1`/`_system1` and in `language`, `_load_pack`, `lookup`, `edit_context` and `file_entry`. The builder's bytes are unchanged. [V]
- **Shared tree:** `git status` shows the four M files and the one new patch file, nothing else. [V]

## 3. Items, with evidence

### Item 2: F1, closed whatever the build did

**Code (filepacks.py):**
- `_build` (:955) reads one full `ls-tree -r -z` (:961). It writes BLOBS.txt, `<path>TAB<blob>` lines (:1037), before TRACKED.txt.
- `_clean` keeps BLOBS.txt (:922).
- `Packs.blob` (:483) does an exact `\n<path>\t` lookup. A missing BLOBS.txt reads as no blob.
- `_code_part` (:568):
  - It reads the code pack once, with System-1's `read_regular`, and checks its schema and blob field.
  - It compares the pack's blob with BLOBS.txt (:601). On a mismatch it shows no code part, only the P2 lines.
  - It passes the same pack to codemap's readers (`pack=`), so the pack it checked is the pack it shows.
- The record logs `code_skip: "blob"` (:711), or a skip with why `blob`.

**Tests (tests/test_filepacks.py):**
- Check `untracked-since-build` (:742), with the patch absent. [V]
  - The verifier's P6 scenario, on a stale TRACKED.txt: a canary goes into gamma.py, and its pack is rebuilt from the working copy in codemap's format.
  - Edit, Read and `cat` inject 0 canary bytes; the P2 lines only are shown; the record says `code_skip=blob`.
  - Mutant `no-blob-check` is killed: "the untracked file's text reached the model".
- `test_untracked_since_build_with_the_real_code_map_refresh[real|no-blob-check]` (:1270): probe_p6.py exactly. [V]
  - Steps: `graft build`; a filepack build; `git rm --cached`; a commit; the canary; `graft build`; then `python3 scripts/codemap.py refresh --commit c9 --lock-dir … --graphs graft --wait 60 --grace 5 -- scripts/gamma.py`.
  - The real code shows the canary on none of the three calls (Edit, Read, cat).
  - The no-blob-check control shows it on all three, which proves the real refresh's pack carries the canary.
  - Where graft is absent, the test skips loudly.
- `test_untracked_since_build_with_the_post_commit_patch[real|no-blob-check]` (:1256), with the patch applied. [V]
  - The real post-commit hook runs with `git apply`'s patch; its build finishes at HEAD; then Edit, Read and `cat` inject nothing.
  - It passes on the no-blob-check mutant too: the patch alone closes F1.
  - Negative control `test_negative_control_the_hook_without_the_patch_runs_no_build`: killed, "the post-commit hook ran no file-pack build".
- Check `root-untracked-suffix`: TRACKED.txt's exact line is kept. Mutant `tracked-suffix-match` is killed. [V]
- Check `blobs-exact-path` (:754) with mutant `blobs-suffix-match`: killed. The check also holds BLOBS.txt equal to `git ls-tree -r HEAD`'s blob ids, an independent oracle. [V]

### Item 3: F2, no stall on a swapped file

**Code (codemap.py):**
- `_system1` (:84) imports `.claude/hooks/system1-context.py` by path once and writes no bytecode. filepacks hands over its own import (filepacks.py:172).
- Each reader opens with `open_regular`/`read_regular`, that is, O_NONBLOCK, then fstat, regular files only:
  - `language` (:105; the open is at :111);
  - `_load_pack` (:896; the pack itself is opened with O_NOFOLLOW);
  - `lookup` (:910, the read at :930);
  - `edit_context` (:953, at :961);
  - `file_entry` (:987, at :1009).
- Working files are followed through a link, as before.
- In tests/test_codemap.py:
  - TOOLING gains the System-1 hook: the fixture needs it.
  - Two mutant anchors moved to the new read lines (`never-stale`, `file-entry-never-stale`). The mutation is the same, `stale = False`.
  - No check changed.

**Tests:**
- `test_no_reader_waits_on_a_fifo[5]` (test_codemap.py:877). [V]
  - Tools-free: the pack comes from the real `build_one` with no graph installed.
  - Each reader runs in a child process with a 10 s bound.
  - Five mutants, each reader's plain pre-F2 open, are all killed by "codemap's <reader> stalled on a FIFO past 10 s" (10.0 s each).
- Ported check `fifo-working-file` (test_filepacks.py:771) with the verifier's 15 s stall bound. [V]
  - `run()` (:220) now kills the process group and fails as "the hook stalled past N s".
  - Mutant `fifo-working-file-read` is killed by "a FIFO working file". With the readers fixed, the mutant no longer stalls; it fails on content instead (the code part shows with STALE rather than P2 only).
- Race evidence: the verifier's `probe_fifo.py` race, N=40 per target, on the same machine. [V]

| Swapped target | Round 2 | PIN |
|---|---|---|
| Working file | 0 of 40 stalled past 5 s | 10 of 40 |
| Code pack | 0 of 40 stalled past 5 s | 10 of 40 |

### Item 4: F3, a linear parse

**Code (filepacks.py):**
- `_Words` (:212) splits each command line into words once. `after()` bisects to the first word and reads at most WORDS_MAX=64.
- Each word is dequoted once. `repo_rel` runs once per (word, directory) (:435).
- A command line gives at most FILES_MAX=64 paths.

**Timings through the real wrapper** (`sh -c REG_PRE`, then hook_context.py, then `filepacks.py hook`). The command is the verifier's: `echo time cat … docs/INCIDENT-LOG.md`. Both versions ran on 1,707-pack builds at the PIN. [V]

| Pairs | Round 2 | PIN, same machine |
|---|---|---|
| 250 (2,275 B) | 179 ms, injected | 612 ms |
| 1,000 (9,025 B) | 207 ms, injected | 8,293 ms |
| 3,000 (27,025 B) | 336 ms, injected | 55,055 ms (the wrapper's 55 s cap; nothing injected) |

- **In process, 3,000 pairs:** 0.21 s; the uncapped variant takes 9.59 s. [V]
- **Check `linear-parse`** (:969): 3,000 pairs through the wrapper under 3 s, and the file is still read. Mutant `no-word-cap` is killed: "the parse is not linear". [V]

### Item 5: F4 and F5, the right file

**Code (filepacks.py):**
- `_frames` (:284) finds, in one pass, each subshell, `$(`, backtick and nested script, with its opener and closer.
- `bash_paths` (:380) keeps a frame stack:
  - A frame restores the directory and the pushd stack when it closes.
  - An `eval` script shares its directory with the caller.
  - `pushd` and `popd` are followed.
- `_grep_files` (:345) takes grep's, egrep's and rg's pattern out of the files. A `-f` file counts as read.
- `_shell` (:268) blanks each `ssh` and `pc.sh` word (same length) and re-derives the code, so the quoted words and heredocs they hand on are data. A remote simple command's extent is skipped, frames inside it included.

**Oracle:** the verifier's 85 strace cases (parser.py), run against round 2, give `Counter({'right': 60, 'miss': 25}) cases 85`. The verifier measured 50 right, 28 miss and 7 wrong at the PIN. [V] The 25 misses are F5's by-design list, plus `cd -` and variable cd's.

**Checks, each with its mutants, all killed** [V]:
- `cd-scope`: the four subshell and substitution shapes, a backtick, and `true && (cd scripts && cat alpha.py) && cat README.md`. Mutant: cd-scope-leaks.
- `pushd-popd`. Mutants: no-pushd, no-popd.
- `grep-pattern`: grep, `-e`, `egrep -n`, `rg -g`, `--regexp=`, `-m 1`, and `-f`. Mutants: grep-pattern-as-file, grep-f-file-missed.
- `nested-script`: `bash -c`, `sh -c`, two files, `eval`; a child shell's cd stays inside; an eval's cd is kept. Mutants: no-quote-strip, bash-c-cd-leaks, eval-scoped.
- `remote`: ssh single and double quoted, pc.sh, `bash pc.sh`, an ssh heredoc, `ssh h time cat`, `ssh h bash -c`; the control is a local read after a remote command. Mutants: remote-read-locally, remote-extent-ignored.

### Item 6: F14, the verifier's 17 checks

- All 17 are added under the verifier's names, each with the verifier's mutant name, anchored on this file's text. All 17 are killed. [V]
- The checks: fifo-working-file, code-pack-parent-link, pack-path-field, pack-schema, root-untracked-suffix, window-max-two, cd-variable-dotdot, tilde, replace-all, offset-zero, log-rotation, long-subject, age-prune, reset-no-state, event-check, dot-slash, nul-newline.
- All 25 round-1 checks are kept.
- Two round-1 anchors moved (`no-cd`, `corrupt-code-pack-ignored`). I re-anchored them; the mutation is the same. [V]

### Item 7: F12 and F6, the claims match the code

**filepacks.py docstring, the boundary paragraph:**
- Refused: a pack that is itself a link gives nothing, logged `link`; a code pack whose directory resolves outside .jev/codemap, logged `unreadable`; a pack whose directory resolves outside <state>/filepacks, logged `link`.
- Followed: a directory link inside them, a linked .jev/codemap and a linked <state>/filepacks.

**"Creates nothing" now says what a call writes:**
- A non-JSON payload logs one line, and creates <state> when it is missing.
- The System-1 bytecode is cached under <state>/pycache.
- codemap's bytecode goes to scripts/__pycache__, which git ignores.

**Two comments made exact:**
- filepacks.py: the hook's "nothing decided or created" now reads "no log line, no marker".
- codemap.py: the `_load_pack` comment now reads "the pack itself: no link, no FIFO".

### Item 8: the registration, as a patch

**The patch** is in `git diff` format against 39d9f82:
- `.claude/settings.json`, +17 lines, two groups, each last in its list:
  - PreToolUse, matcher `Read|Edit|Write|Bash`, with the REG_PRE command.
  - SessionStart, no matcher, with REG_RESET.
  - Both strings are byte-equal to test_filepacks' REG_PRE and REG_RESET (checked).
- `scripts/install_session_hooks.py`:
  - `our_hooks`: `filepacks` goes last in PreToolUse and `filepacks_reset` last in SessionStart.
  - `merged()`: adds `filepacks_marker`.
  - Docstring: a filepacks paragraph and the merge rule.
  - The count: "nine" and "installed 9". See DISCREPANCIES 1.
- `tests/test_session_hooks.py`:
  - The builder's seven edits.
  - The verifier's eighth: `_fake_repo` writes a `scripts/filepacks.py` stub that prints its cwd.
  - The count edit and one new test. See DISCREPANCIES 1 and 2.

**Proof.** Setup: a clean worktree at 39d9f82; the four round-2 files copied in; `git apply` of the post-commit patch, then of the registration patch; the patched hook is fce110fe82d8b183. The worktree's diff equals K2-registration.patch byte for byte. [V] Final bytes:
```
2 files set=2415789b9582
pytest-exit: 0
pytest-summary: 137 passed in 67.29s (0:01:07)
```
- **Earlier run:** before the test_filepacks fix, the same run gave `137 passed in 71.48s`.
- **Count:** 137 is the verifier's 136 plus the new older-spelling test.
- **Manifest:** `python3 scripts/vendored_manifest.py --check` FAILS on the `.claude/ (kit-adapted)` row, rc 1. The committed value is `214664b3…` and the generated one `cab4c825…`. The clean PIN worktree gives rc 0. This is expected until the coordinator regenerates the manifest at landing. [V]
- **Negative controls, in the proof worktree:** [V]
  - With the marker removed, the new test fails with "an older filepacks spelling stayed".
  - With the eighth edit removed, `test_wrapped_commands_name_their_own_event` fails with a JSONDecodeError (the verifier's F7).
  - Restored, both pass.

### Item 9: gates

The gate ran in a clean detached worktree at 39d9f82 with the four round-2 files. `--basetemp` was a pytest argument, under my scratch directory, outside any work tree.

| Run | Start | Bytes | Result |
|---|---|---|---|
| 1 | 08:52Z | earlier test_filepacks, 51c4c584… | `pytest-exit: 1` / `pytest-summary: 1 failed, 325 passed in 507.56s (0:08:27)` |
| 2 | 09:02Z | final | `3 files set=804c19143d13` / `pytest-exit: 0` / `pytest-summary: 326 passed in 503.76s (0:08:23)` |
| 3 | 09:11Z | final | `3 files set=804c19143d13` / `pytest-exit: 0` / `pytest-summary: 326 passed in 496.07s (0:08:16)` |

**Run 1's failure:** `test_untracked_since_build_with_the_real_code_map_refresh[no-blob-check]` raised FileExistsError on its `home` directory.
- Cause: `graft build` spawns a detached `graft _update-check` child when `$HOME/.graft/update-check.json` is stale.
- The repo sets `tmp_path_retention_policy = "failed"`, so the next test reused the deleted directory's name, and the child then wrote into it.
- Fix: the test writes a fresh update-check answer into graft's private HOME, so no child is spawned. After the fix, no `_update-check` process is left. [V]

### Mutation summary (final bytes, control first, AF-AP-223) [V]

- **Control:** `70 passed, 115 deselected in 187.10s (0:03:07)`. That is 50 filepacks checks, 10 codemap lookup checks, 5 refresh checks and 5 FIFO reader checks.
- **Mutants:** `102 passed, 83 deselected in 265.04s (0:04:25)`, rc 0. Each mutant test asserts its own named failure.

| Mutants | Killed |
|---|---|
| filepacks (40 kept from round 1, 30 new) | 70 of 70 |
| Hook without the patch | 1 of 1 |
| codemap lookup | 15 of 15 |
| Refresh | 6 of 6 |
| FIFO readers | 5 of 5 |

- **Also in the 102:** the renamed-lock control and 4 framework tests (every check has a mutant; every mutant compiles and has a check).
- **In the registration proof:** the merged-marker mutant, 1 of 1.

## NOT done (first-class)

1. **Not registered.** The hook is registered nowhere, by rule.
   - The live `.jev/filepacks` is still round 1's build: 7db59b9, from 05:48:54Z, with no BLOBS.txt. I never wrote it.
   - With round-2 code, every code part is left out (P2 lines only) until a build writes BLOBS.txt. That build is the first post-commit build with the patch, or one manual `filepacks.py build`.
2. **The vendored manifest is not regenerated.** That is the coordinator's step at landing.
3. **The round-1 report of record is unchanged.** `tasks/briefs/jev-trim/K2-FILE-PACKS-report.md:179-180` still says "a pack reached through a link gives nothing" and "creates nothing". The file is outside this round's boundary.
4. **Parser limits kept** (named in the docstring):
   - A cd in a pipeline is followed, though it runs in a subshell.
   - A heredoc fed to a shell under ssh (`ssh h bash -s <<EOF`) is read locally, so a wrong file is possible.
   - A `case` pattern's `)` inside a subshell closes the subshell early.
   - A function body's cd is followed where the function is defined.
   - `cd -` is unknown.
   - F5's by-design misses remain: xargs, find -exec, globs, variables, `<` redirects, nice, stdbuf, command, `env -i`, `sudo -u`, `timeout -k`.
5. **The callers sample, unmeasured.** A code pack's callers sample can name an untracked caller's file and function, because GitNexus indexes working-tree files. F1's check covers the file's own text only.
6. **F20 docs** (D105-DESIGN §10.3, the LS-AUDIT S3 row): not updated; not my files.
7. **Not re-run:** the replay on round-2 code; the parse changes shift which files count. Also F13 (stale @sha7 after push_clean).
8. **Venue:** the patched-hook test needs flock, nice and ionice (util-linux), and ran only in this container, not on CI. The real-refresh test skips where graft is absent.
9. **A test name.** `test_fresh_install_registers_the_eight_hooks` keeps its name, though its count is now 9.

## DISCREPANCIES

1. **DEVIATION: the count.** The patch changes the installer's "installed 8" to "installed 9", and "eight" to "nine" in the installer's and the test's docstrings. It also changes the test's `"installed 8"` to `"installed 9"`. That is one test edit more than "the builder's seven plus the verifier's eighth".
   - Why: the number counts hook scripts. LS-B9 round 4 bumped it from 7 to 8 for the catalog (VERIFY-LS-B9 R4-F9), and filepacks.py is a ninth.
   - The builder's round-1 list left this open ("check how the installer counts before changing it").
2. **DEVIATION: a new test.** I added `test_an_older_filepacks_spelling_is_replaced_on_install`. Without it, no test fails when the merged marker is missing. Its mutant is killed.
3. **DEVIATION: the patch-applied F1 test's commits.** In that test, the untracking commit runs with hooks off, and the patched hook runs on a later docs-only commit.
   - Why: a commit that changes scripts/gamma.py makes the hook launch the graph re-index and the code-map refresh. This container has code-review-graph and codebase-memory at fixed fallback paths, which the hook finds without PATH. Those jobs would outlive the test.
   - What it proves: the patched hook's build reaches HEAD, and that TRACKED.txt and BLOBS.txt leave the untracked file out.
4. **DEVIATION (design): the quote strip.** "Strip the unmatched closing quote" is built as a word boundary at the closer's offset, which the frame scan finds. It is not a string strip. The effect is the same: `bash -c 'cat a b'` gives both a and b.
5. **DEVIATION (scope): two additions inside F4/F5's "the right file".**
   - A cd inside a child shell's script (`bash -c`) stays inside it.
   - A grep `-f` pattern file counts as read.
6. **The premise block** in §1 is a reproduction at 09:30Z in a clean PIN worktree. The round-start run matched, but I saved only its commands to a file. Its file hashes are in this session's first output, at 07:58:23Z.
7. **The set ids did not change** (804c19143d13, 2415789b9582): `pc_suite.sh set-id` names the file set, not its bytes. I compared the gate's bytes with `cmp`.
8. **Behavior change beyond F1's letter.** A code pack built from uncommitted bytes of a TRACKED file now shows no code part until its blob matches the build's commit. Examples: a manual `codemap.py build` during an edit, or a refresh that ran while edits were pending. The brief's rule demands this; the cost is missing code parts in those windows. [I]
9. **codemap's `_load_pack` now refuses a pack file that is itself a symbolic link** (O_NOFOLLOW), for the CLI too. Before, it followed one. No code writes linked packs. [I]
10. **codemap's readers now depend on the System-1 hook importing.** A missing or broken hook raises (loud), including in the builder's `language()` for extensionless files.
11. **GitNexus `detect-changes` reads MEDIUM:** 4 files, 57 symbols, 4 flows. Before my edits, `impact` read MEDIUM for `language` (10 callers in codemap's builder) and LOW for the other symbols; the UNKNOWN reads were name collisions or unresolved callers, which a text search confirmed.
    - The flows are Build_one→_ext, Main→In_scope, Main→_ext and File_entry→_ext.
    - `reads`, `in_scope`, `_sha256_file` and `pack_path` are listed only because the index's spans predate the 24-line insertion above them. The diff's hunks name only `_system1` and the five readers. [V]
12. **Gate run 1 failed** (§3, item 9) on my own new test. It is fixed, and two clean runs followed.

## Self-attack: the three likeliest ways this is wrong

1. **The blob check lets text through that no commit holds.** Ruled out:
   - BLOBS.txt comes only from `git ls-tree` at the build's commit, so a match means the pack describes a blob committed at that commit.
   - The exact-path lookup is killed by `blobs-suffix-match`.
   - BLOBS.txt is held equal to git's own ls-tree output.
   - The real-refresh control shows the canary reaching the model when the check is removed, so the test is not vacuous.
   - Residual: the callers sample (NOT done 5).
   > **Note (2026-09-29 18:5xZ, K2 round 3): falsified** by VERIFY-K2 round 2. B2: a match proves only that the
   > pack's blob was committed; its symbols come from a graph's index, which can hold other bytes (graft stale). B1:
   > the callers sample named above put an untracked file's name and path in front of the model. The repair:
   > `tasks/briefs/jev-trim/K2-R3-report.md`.
2. **The frame scan mis-pairs frames and scopes a cd wrongly, so a wrong file is injected.** Evidence against:
   - The verifier's 85-case strace oracle gives 0 wrong.
   - The checks cover the seven wrong shapes and the nested and remote forms.
   - The known mis-pairs are documented (NOT done 4).
   - Not done: fuzzing against strace beyond those 85 cases.
3. **The F3 bound is flaky or weak.**
   - Real side: 336 ms measured against a 3 s bound, a 9× margin.
   - Mutant side: 9.59 s in process against the 3 s bound, about 3×. A machine twice as fast would still take about 4.8 s. This is the thinner margin.
   - The FIFO bounds are 10 s. The real readers return in about 0.1 s, and the mutants hit exactly 10.0 s.

## Hygiene

- **Writes in the shared repo:** four `git worktree add` (with hooks off) and four `git worktree remove`: wt-reg, wt-gate, wt-pin and wt-regproof. All are removed; `git worktree list` shows none of mine.
- **Files written in the shared tree:** the four in §2 and the new patch. I never touched `.claude/`, `scripts/install_session_hooks.py`, `tests/test_session_hooks.py`, `scripts/hooks/post-commit`, `/home/user/.claude/settings.json` or the live `.jev/`. I never ran the installer.
- **Processes:** none of mine is running; I checked for filepacks, `_update-check`, `flock 7`, pytest and codemap refresh.
- **Transcripts:** none read this round. I read only repo files and the verifier's probe directory.
- **Kept in scratch:** logs and probes under `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/k2-lane-353/r2/`:
  - gates: gate-1.txt, gate-2.txt, gate-3.txt;
  - mutation run: mut-control.txt, mut-run.txt;
  - registration proof: regproof-1.txt, regproof-2.txt;
  - probes and their outputs: parser_r2.txt, detect.json, wrap_time.py, probe_fifo_r2.py, quad_r2.py;
  - a copy of the patch.