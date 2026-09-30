# VERIFY-K2-R6: the verifier's report of record, round 6 (task #353)

> **Coordinator note (2026-09-30 22:5xZ).** The VERIFY-K2 verifier, resumed at 21:4xZ for round 6 (a narrow re-check of
> the K2 follow-ups at PIN origin d2e69c6, where CI run #1195 passed), wrote this report from 22:35:47Z. Its hand-back
> call failed at 22:39:15Z ("No such tool available: SubagentHandback"), 48 seconds before the container booted again
> at 22:40:03Z (`/proc/stat` btime). Resumed by message at 22:47:31Z, it re-ran no check and gave the report as its
> final message at 22:49:20Z, with the restart noted. That final text is saved verbatim below. The harvest (run
> s-20260930T225205Z-80bb51) took the failed call's input as the hand-back and read the final text as an epilogue; the
> two differ in wording, and only the final text has the restart lines (task #426's class, noted in the ledger). The
> harvest: 1,411 assistant records over rounds 2 to 6, every one claude-opus-5-5, 0 refusal stops. The text below was
> written by the extractor's own writer (0 tags neutralized; sha256 prefix 505f5add5df8). report_lint over the
> hand-back gave 5 refs: OK 1, MISS 3, UNCHECKABLE 1. The coordinator read the three MISS lines at d2e69c6, and each
> cites the right line: `tests/test_filepacks.py:1436` and `:1190` are the assertions that killed the two survivors,
> and `scripts/codemap.py:820` is the per-file guard; the lint wants a token from the cited line that the quote lacks.
>
> Recommendation: MERGE-READY-WITH-FOLLOWUPS for registering K2 at d2e69c6 with K2-registration.patch and
> K2-post-commit.patch, on one condition: must-hold items 1 to 3 of section 6 hold at landing. **The coordinator's
> gate: MERGE-READY-WITH-FOLLOWUPS.** R6-F1 (the CLI label misses registry rows computed from an uncommitted edit of
> the screen table) is a follow-up for round 5's reason: D-117's condition (b) governs what the hook injects, and the
> hook drops those rows (`_screened`). Until the follow-up lands, the sentence at `scripts/codemap.py:31` is false for
> that case. The follow-ups R6-F1 to R6-F6 and R6-F12 are task #428 (backlog), C1's optional builder strip (R6-F5)
> among them. Registration waits for the owner's yes (D-120). **D-115's round table:**
>
> | Round | Verify | Blocker |
> |---|---|---|
> | 1 | MERGE-READY-WITH-FOLLOWUPS on one condition | F1: a stale index let an untracked file's text through |
> | 2 | NOT-READY | B1: untracked callers through a tracked file's code part |
> | 3 | NOT-READY | R3-1 |
> | 4 | NOT-READY | R4-1, the same class; K2 went to the owner, who chose RE-SCOPE (D-117) |
> | 5 | MERGE-READY-WITH-FOLLOWUPS | none; F1 and F2 are untested clauses, closed by task #420 before registration |
> | 6 | MERGE-READY-WITH-FOLLOWUPS | none; round 5's two survivors are KILLED on the landed bytes; R6-F1 to R6-F6 and R6-F12 are follow-ups (task #428) |

## Round 6 (narrow re-check, d2e69c6)

Written 2026-09-30 from Wed Sep 30 22:35:47 UTC 2026 (`date -u`). Finalized after the container restart, at Wed Sep 30 22:47:40 UTC 2026 (`date -u`). PIN: origin d2e69c6, the K2-FU landing (task #420). Contract revision 5 holds; this round re-checks only the follow-ups.

**Recommendation: MERGE-READY-WITH-FOLLOWUPS** for registering K2 at d2e69c6 with the two patches. I reproduced every result this rests on, except two coordinator steps at landing: the manifest regeneration and the must-hold build run on the live tree.
- No finding meets the whole D-034 predicate. There is no CONTRACT-DEFECT.
- Both of my round-5 survivors are now KILLED on the landed bytes, by the new checks.
- `recover` never started a build beside a live build. One session start took at most 63 ms; 16 starts at once took at most 338 ms each.
- `_rev`'s strip gave the right answer in every shape I tried: a linked worktree, no repository, an unborn branch. A mutant without the strip leaked in five of them.
- C1 is F9's class. It shows history only, and no production path reaches it. It is a follow-up, not a condition for registration.
- At origin 4750728, the K2 files and the registration files are the same as at d2e69c6.
- After the restart I re-ran no check. Every result below comes from my logs, written before the restart. After it I only listed those logs, the worktree list and the shared tree's status, all read-only.

### 1. Premise
- I ran the coordinator's block from the main tree: 7 commands. Expected and actual output are identical (sha256 prefix 0147a6e47588b870 for both).
- I made three worktrees at d2e69c6, with hooks off. All three are removed:
  - `<SR>/wt` for the probes and gates.
  - `<SR>/wtmut` for the mutants.
  - `<SR>/wtboth`: d2e69c6 plus both K2 patches.
- The landed bytes (sha256 prefix, lines):
  - scripts/filepacks.py: b4280c0da1ebb54f, 1307.
  - scripts/codemap.py: 6f61344589bfc3e7, 1241.
  - tests/test_filepacks.py: fc9de23b252fe43e, 2483.
  - tests/test_codemap.py: b0cde454ba6588f5, 1053.
- Both patches are unchanged: K2-registration.patch 1dc53684b8ae5490, K2-post-commit.patch 3fe1a775b7203205.
- At 4750728:
  - `git merge-base --is-ancestor d2e69c6 HEAD` holds.
  - `git diff --stat d2e69c6 HEAD` is empty over these paths: the four files, the two patches, `.claude/settings.json`, `scripts/install_session_hooks.py`, `scripts/hooks/post-commit`, `scripts/hook_context.py` and `.claude/hooks/system1-context.py`.

### 2. My two survivors, on the landed bytes [reproduced]
The driver is `<R6>/mutdrv6.py`, run in wtmut.
- The control ran first, on the full `tests/test_filepacks.py`: "194 passed in 176.57s (0:02:56)", rc 0.
- For every run: bytecode off, `__pycache__` cleared, each anchor found exactly once, each file restored and checked by sha256.

**`registry-from-working-text-fullfp`: KILLED.** "3 failed, 191 passed in 179.05s (0:02:59)". The kill is `[registry-committed]`:

`tests/test_filepacks.py:1436: AssertionError: an uncommitted line reached the model through a registry row: 'codemap scripts/alpha.py:6 — function helper L5-6 · def helper(x) ... registry rows here 1: AF-AP-175 :6 leak = "rw1…'`

The other two failures are not kills. My mutation used up the anchor that the in-test code-map negative controls need: `:1907: AssertionError: INVALID: the anchor occurs 0 times in codemap.py`.

**`current-none-equals-none`: KILLED.** "1 failed, 74 passed in 72.16s (0:01:12)", on the FP_SEL selectors. The kill is `[head-unresolved]`:

`tests/test_filepacks.py:1190: AssertionError: a record with no tree and a git that fails showed a pack: 'filepack docs/NOTE.md @67608b3: ledger 1 · incidents 2 · decisions 1 · commits 1'`

My discriminators, run on the landed bytes:
- `p8disc.py`: a no-tree record plus a failing git gives 0 bytes on the landed code and 907 bytes on the mutant. The control (a working git) gives 0 bytes on both.
- `p8disc_b.py`: no canary on the landed code. The mutant shows "registry rows here 1: AF-AP-175 :6 leak = "rgbc11869039" + "HEAD" — …".

### 3. The new code, attacked with my own shapes [reproduced]
The probes are `p6a` to `p6f` in `<SR>/probes`; the logs are in `<R6>/logs`. Every hook run is the registration's own command (REG_PRE or REG_RESET) run through `sh`, on the fixture from `tests/test_filepacks.py` at d2e69c6.

#### (a) `recover` (F15, scripts/filepacks.py:831): `p6a_recover.py`

| Shape | Result |
|---|---|
| A. Control: a crash after the marker; the lock is free | `rebuild: started` in 49 ms. The build writes a tree. The hook shows 537 bytes |
| B. A real live build holds the lock (`filepacks.py build`, slowed 6 s in its first `git log`). BUILD.json is an older crash's marker | `rebuild: busy` in 49 ms. No second build process; 1 build ran in all |
| B2. A live build is past its own marker (in process, `_clean` slowed 4 s) | `busy` in 54 ms. No other build |
| C. 8 session starts at once, after a crash | 7 `started`, 1 `busy`. 7 builds ran one at a time (their locked sections started 28 to 54 ms apart). Hook wall time min/median/max: 102/141/199 ms |
| C. 16 session starts at once | 9 `started`, 7 `busy`. 9 builds ran one at a time (28 to 83 ms apart). Hook wall time: 116/244/338 ms |
| D1. No state directory | rc 0, no output, no state created, no process |
| D2. The test seam AF_FILEPACKS_STATE names another repository's state, which holds a marker | This repository's build is written there. The other repository's hook then shows 0 bytes (tree) |
| E1. BUILD.json is a symbolic link to a marker | `{}` (no rebuild field), no process. The hook stays dark |
| E2. BUILD.json is a FIFO | `{}` in 63 ms, no hang |
| F. The lock is a symbolic link to a victim file, or a FIFO | `{"error": "OSError"}` in 41 to 53 ms. The seen markers are still removed. The victim is unchanged. No build |
| G. The recover log is a symbolic link or a FIFO | `{"error": "OSError"}`. The victim is unchanged. No build |
| G. The recover log is a HARD link to a victim file | `started`. The victim now holds "filepacks build: 576942d 12 packs (0 written, …": it was truncated and overwritten |
| H. `<state>/filepacks-off` is set, and there is a marker (C3) | `started`, and a tree is written. The hook shows 0 bytes with the switch on and 537 bytes after it is removed |
| I. The root's `.git` is moved away, and there is a marker | Each of 3 session starts spawns one build that fails ("fatal: not a git repository"). The marker stays |
| J. The build is slowed 8 s per `git log` | The reset returns in 58 ms while the build is alive. The build runs 16.2 s more |

**Can it start a build beside a live build?** No. While the lock is held, the lock probe refuses (B, B2). Past that point, the build's own blocking lock makes the builds run one at a time (C).

**Can it hold the session start?** No. Each single start took 41 to 63 ms. The child gets `/dev/null` and the log file, never the hook's pipes (J).

**Can it run where it should not?**
- Under the kill switch: yes, as documented (C3).
- Into another state, through the test seam only.
- In a root that cannot build: one failing process per session start.
- A burst of session starts gives redundant builds (C).
- A hard link at the log path truncates its target (G).
- See R6-F7 to R6-F11.

#### (b) `_rev`'s strip (F4, :564): `p6b_rev.py`
Each row runs twice: once with the landed filepacks.py, once with a mutant whose `_own_env` keeps every variable. A committed canary line in the ledger names scripts/beta.py, and a Read of beta shows it only when the tree check passes.

| Shape | Landed | Mutant |
|---|---|---|
| Linked worktree W (its HEAD moved back; its build is of the old tree), no GIT_* | 0 bytes (tree) | 0 bytes (tree) |
| W, GIT_DIR=<R>/.git (R's HEAD has W's build tree) | 0 bytes | 303 bytes, canary |
| W, GIT_DIR and GIT_WORK_TREE=<R> | 0 bytes | 303 bytes, canary |
| W, GIT_COMMON_DIR=<R>/.git alone | 0 bytes | 0 bytes |
| W, GIT_WORK_TREE=<R> alone | 0 bytes | 0 bytes |
| R (HEAD is its build's tree), GIT_DIR=<W's gitdir> | 303 bytes, canary (right: this is R's HEAD) | 0 bytes (suppressed) |
| No repository (R's files without .git, R's state), no GIT_* | 0 bytes | 0 bytes |
| No repository, GIT_DIR=<R>/.git | 0 bytes | 303 bytes, canary |
| No repository, GIT_CEILING_DIRECTORIES=/ | 0 bytes | 0 bytes |
| Inside an unrelated parent repository | 0 bytes | 0 bytes |
| Inside that parent, GIT_DIR=<R>/.git | 0 bytes | 303 bytes, canary |
| Unborn branch (`git worktree add --orphan`; rev-parse rc 1), no GIT_* | 0 bytes | 0 bytes |
| Unborn branch, GIT_DIR=<R>/.git | 0 bytes | 303 bytes, canary |
| Unborn branch, GIT_INDEX_FILE=<R>/.git/index alone | 0 bytes | 0 bytes |
| R, GIT_OBJECT_DIRECTORY=<empty dir> (not stripped) | 0 bytes | 0 bytes |
| R, GIT_NAMESPACE=ns (not stripped) | 303 bytes | 303 bytes (no effect on `rev-parse HEAD`) |
| R moved back, GIT_OBJECT_DIRECTORY=<a clone's objects> | 0 bytes | 0 bytes |

- The strip decides every case in which a foreign variable could move HEAD.
- In each of those cases it gives the answer of the directory's own repository.
- The variables it keeps either fail closed or change nothing.

#### (c) The per-file guard (F5, scripts/codemap.py:820): `p6c_guard.py`
**c1. A file whose pack can never be written, with an old pack planted.** The file name is 245 characters, so its temporary file name passes NAME_MAX.
- While the old pack is of the file's current blob, the hook shows its code part. That is right: the pack describes HEAD's blob.
- Then a commit changes the file.
  - `codemap.py build`: rc 0, with "failed scripts/nnnn…" on stdout and "OSError: [Errno 36] File name too long" on stderr.
  - The old pack stays (its symbols: ['first']).
  - After the file-pack build, the hook shows no code part for the file (`injected []`).
  - `lookup` prints "codemap: NOT HEAD's committed code (blob): …".
- So a pack that a failure leaves behind is never shown for another blob.

**c2. Git cannot resolve HEAD.** A shim makes `git rev-parse HEAD` fail.
- rc 0, stdout "untracked scripts/alpha.py", stderr empty, and alpha's pack is deleted.
- 59ad820 has the same code (codemap.py:810, then :744). This is older than this increment and fails closed (R6-F12).

**c3. Error classes, in process.**
- MemoryError, RecursionError, OSError and TypeError each cost only their own file: `failed`, and the next file is `built`.
- KeyboardInterrupt, SystemExit and GeneratorExit propagate and end the build.
- So no error class that should end a build now passes silently. One exception: a programming error becomes a per-file `failed`, with its type on stderr and rc 0 (R6-F13).

#### (d) The CLI label (F3): `p6d_label.py`
- **d1. Registry rows from an uncommitted edit of the screen table.** The canary is in the message of the AF-AP-175 row. The screen and the line it hits are committed.
  - The hook (Edit on the hit line) gives 867 bytes, with no canary and no rows line.
  - `lookup` prints no label and shows the canary: `registry rows here 1: AF-AP-175 :18 ref = "HEAD"  # the committed hit — a quoted HEAD passed to git SC77066602cb — …`.
  - `demo` also prints no label and shows the canary.
  - This is R6-F1. The lane named it.
- **d2. Control, after `reset --mixed HEAD~1`.** The hook gives 0 bytes. `lookup` prints "codemap: NOT HEAD's committed code (tree): no file-pack build of HEAD's tree".
- **d3. The read race, in process.** `_load_pack` finds no pack on its first call only.
  - Normal run: the label prints.
  - Race: no label, and the first line is "codemap scripts/alpha.py:24 — function leak_RC00abf7669e L24-25 · def leak_RC00abf7669e(x)". This is R6-F2.
- **d4 (C2).** `lookup --json` under a label exits rc 0, but stdout "does not parse: Expecting value: line 1 column 1 (char 0)".
- **d5 (C4).** `demo` prints the label, then "old_string at: L6-6", "enclosing: helper" and "--- the entry L2b would inject (161 bytes) ---".
- **d6 and d7.** With the kill switch on (d6), and with the working file a symbolic link (d7), the hook shows no code part and the CLIs print the pack with no label. In both cases the pack is HEAD's committed code, so no label is due (R6-F15).

### 4. C1: the builders' foreign GIT_DIR (`p6e_c1.py`) [reproduced]
**My shape.**
- A clone, reset to a NEW ROOT COMMIT that has this repository's tree (made with `commit-tree`). Its subject is "foreign subject fhb840f4f47f".
- The real `filepacks.py build`, run with `GIT_DIR=<clone>/.git`, prints "filepacks build: 7384350 12 packs …".
- BUILD.json records commit 7384350 and tree a6cb754, which is this HEAD's tree.

**What the hook shows.** In this repository, with no GIT_*, it shows 549 bytes, including:
- `filepack docs/NOTE.md @7384350: …`
- `commit 7384350 2026-01-01: foreign subject fhb840f4f47f`

This repository does not hold that commit at all (`cat-file -e` fails).

**Controls.**
- The clone moved to another tree, same build: 0 bytes, skipped `tree`.
- A build with no GIT_*: 538 bytes and no canary.

**Production paths**, measured in a scratch repository:
- In the main worktree, git exports `GIT_INDEX_FILE=.git/index` and `GIT_PREFIX` to a post-commit hook.
- In a linked worktree, git exports `GIT_DIR=<main>/.git/worktrees/w2`, which is that worktree's own gitdir.
- So the post-commit build always names its own repository, and `recover` strips the variables (`_own_env`, :857). Only a manual run with a foreign GIT_DIR reaches C1.

**Grade: FOLLOW-UP, F9's class (history, not tree bytes).**
- Predicate condition 1 fails: no frozen criterion is contradicted. D-117 (b) holds, and item 5 of the K2-FU brief says of these sites "Change none of them".
- Predicate condition 2 fails: no production consumer passes a foreign GIT_DIR, so there is no canonical reproduction.
- It need not block registration.

**My recommendation:** drop GIT_ENV in the builders anyway. It is cheap and matches `_rev`.
- Use `env=_own_env()` in `_git` (filepacks.py:932), and the same in codemap's `_head` (:690), `_committed` (:695) and `all_code_files`.
- Both production paths keep their answer: discovery from `cwd=root` finds the same gitdir that the hook exports.
- The owner can choose to do this with the registration or after it.

### 5. C2 to C4
- **C2 (`lookup --json`): FOLLOW-UP.** Reproduced in d4. Nothing parses this output: only the usage line and the tests name `--json`. Fix: with `--json`, put the check inside the document (for example `"head_check": "tree"`), or print the label to stderr.
- **C3 (`recover` under `filepacks-off`): INFO.** Reproduced in H.
  - The docstring states it: "the reset still runs", and "a reset that starts a build writes <state>/filepacks-recover.log, and the build its packs".
  - The post-commit build ignores the switch too.
  - The switch stops injection, not builds. The owner's registration question should say so.
- **C4 (demo's header): FOLLOW-UP, wording only.** Reproduced in d5. Fix: "--- the code map's entry (N bytes) ---", or say that the hook would not inject the text when a label printed.

### 6. Item 13 at d2e69c6: what must hold before registration
**1. Still must hold: K2-post-commit.patch lands with or before the registration.** It applies at d2e69c6 (`git apply --check`). Without it, the first commit leaves the hook dark.

**2. Still must hold: apply K2-registration.patch, and regenerate the vendored manifest's `.claude/` row at the landing base.**
- Both patches apply at d2e69c6.
- `hook_count(our_hooks)` = 15: ls_req 3, filepacks 2.
- The order is unchanged:
  - SessionStart: session-start.sh, task_sync, catalog [startup|resume|compact], filepacks reset, ls_req.
  - PreToolUse: search-intercept [Grep|Bash], system1-context [Write|Edit|Bash], filepacks [Read|Edit|Write|Bash].
- The patched `.claude/settings.json` holds REG_PRE and REG_RESET exactly.
- The manifest test (`-k test_committed_manifest_matches_fresh_generation`):
  - With both patches: "1 failed, 56 deselected in 1.67s", on line 20 `.claude/ (kit-adapted)` (committed 330a7f27e41…, generated dac17315791…).
  - At d2e69c6 alone: "1 passed, 56 deselected in 2.27s".
  - So the registration patch causes the drift, as in round 5. The committed hash has moved since then, so round 5's pair of hashes is stale.
- F15 depends on this registration: `recover` runs only through `hook --reset`.

**3. Still must hold: at HEAD, run `python3 scripts/codemap.py build --all`, then `python3 scripts/filepacks.py build`.** The live code packs are older than `symbols_from: "ast"` and `parsed`.

Measured at d2e69c6 in my worktree, with a private HOME and PATH=/usr/bin:/bin:
- **codemap:** "codemap build: 235 file(s), 235 built, 4.0 s, 868704 pack bytes", rc 0, 0 stderr lines. All 235 packs have `symbols_from: ast`. `parsed`: True 137, False 0, None 98 (the non-Python files).
- **filepacks:** "filepacks build: d2e69c6 1766 packs (1766 written, 0 removed, 0 failed) of 10076 tracked files in 1607 ms". The tree, 10f914f, equals `HEAD^{tree}`, and the record has an id.

A smoke of the registration's commands, with no AF_* variable and the state at `<wt>/.jev`:
- A Read of scripts/filepacks.py: 1148 bytes in 112 ms. It shows the code part ("58 symbols, 44 at top level"), the registry rows, and "filepack scripts/filepacks.py @d2e69c6: ledger 2 · briefs 25 · commits 6".
- An Edit inside `recover()`: "function recover L831-861 · def recover(state)".
- REG_RESET: 49 ms, no rebuild.
- A crash after the marker, then REG_RESET:
  - After the crash, the hook showed 0 bytes.
  - REG_RESET took 58 ms and returned `rebuild: started`.
  - The build ended 1.4 s later ("… 1766 packs (0 written, 0 removed, 0 failed) … in 1269 ms").
  - The hook then showed 1148 bytes again.

**4. Done:** F1's check and mutant, and F2's case. Both survivors are KILLED (section 2).

**5. Done:** the owner's F3 (the label) and F4 (the strip in `_rev`), per D-120.

**6. Done:** F9's sentence, at filepacks.py:28 and, through C6, in the test docstring. Two items remain for the owner's registration question: the kill switch stops injection but not builds (C3), and C1's optional builder strip.

Nothing new from this round must hold before registration.

### 7. Gates
All counts are pasted. `--basetemp` was under /tmp, outside every work tree, and deleted after each run. PYTHONDONTWRITEBYTECODE=1.
- wt at d2e69c6, `1 files set=db64e610236b`: "pytest-summary: 194 passed in 169.73s (0:02:49)".
- wt, `2 files set=395f8af3a0ce`: "pytest-summary: 204 passed in 278.18s (0:04:38)".
- wtboth, `2 files set=2415789b9582`: "pytest-summary: 144 passed in 45.96s".
- wtboth, `1 files set=21e700b8344c` (`-k` the manifest test): "pytest-summary: 1 failed, 56 deselected in 1.67s". This failure is expected (item 2 of section 6).
- wt, the same test: "pytest-summary: 1 passed, 56 deselected in 2.27s".

### 8. My mutants on the new code [reproduced]
Each ran the full `tests/test_filepacks.py`, after the control in section 2.
- **`recover-always-rebuilds`** (the marker test dropped): KILLED. "1 failed, 193 passed in 154.03s (0:02:34)". The kill is `[reset]`: `:420: AssertionError: a resume did not re-arm the session`.
- **`recover-inherits-pipes`** (the child keeps the hook's stdout and stderr): KILLED. "2 failed, 192 passed in 157.59s (0:02:37)". The kill is `[recover]` at :1626: the reset's stdout was not empty. The second failure is the interaction at :1986.
- **`recover-waits-for-build`** (`p.wait()` before the return): "1 failed, 193 passed in 210.53s (0:03:30)".
  - The only failure is the in-test negative control `[recovery-ignores-the-lock]` at :1986: "Regex pattern did not match … Actual message: 'the hook stalled past 60 s'". My mutant and the in-test mutant together hang on the lock the test holds.
  - `[recover]` and every behavioural check pass.
  - Graded: SURVIVED in substance (R6-F6).

### 9. The lane's claims, spot-checked
- **F15's bound** (the lane measured 54 ms, with the build running 18.2 s more). I measured 58 ms and 16.2 s more (J); on the real tree, 58 ms and 1.4 s. Holds.
- **"Two sessions starting at once could each start a build … one after the other (inferred)".** Now measured: 7 of 8 starts built, and 9 of 16, all one at a time.
- **"git exports GIT_DIR to hooks only in a linked worktree, and there it names that worktree's own gitdir".** Measured; holds.
- **The linked-worktree case, and the three single variables** (GIT_COMMON_DIR, GIT_WORK_TREE and GIT_INDEX_FILE alone change nothing). Hold, per section 3(b).
- **C5** (both consumers handle the failed entry). The build CLI printed "failed scripts/nnnn…" and "2 file(s), 1 built" (c1). Holds. `_ast_symbols` and `_ast_starts` each have one production caller, `build_one`.

### 10. Stale-context sweep
- `tests/test_filepacks.py:34` now carries F9's sentence (C6).
- The only "L2b would inject" left is demo's header (codemap.py:1234, C4).
- codemap.py:31 says that `lookup` and `demo` "print their text as the file-pack hook's code part would". That is false for registry rows from an uncommitted screen (d1). It is part of R6-F1.
- `recover`'s docstring (:836) says "While a build holds the lock, none starts: the marker is that build's." In shape B the marker was an older crash's. The rule holds, but the reason is loose (R6-F14).

### Finding inventory (no severity filter)
**To reproduce:**
1. Re-create the worktree: `git -C /home/user/agent-factory -c core.hooksPath=/dev/null worktree add -q --detach <SR>/wt d2e69c6`.
2. Run `( cd <SR>/probes && python3 <probe> )`.

`<SR>` = /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2rs.
`<R6>` = /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r6 (the driver and the logs).

1. **R6-F1 FOLLOW-UP: the label misses the registry-screen condition.** [V]
   - `lookup` and `demo` print registry rows computed with an uncommitted edit of the screen table, and print no label. The hook drops those rows (`_screened`, filepacks.py:636).
   - In d1 the CLIs showed the canary in the row's message; the hook showed 867 bytes without it.
   - codemap.py:31's claim is false here.
   - Contract: F3 (K2-FU brief item 4) names three checks: tree, blob and symbols. This would be a fourth. This is not the injection path.
   - Material effect: uncommitted text reaches a dev-CLI reader with no mark.
   - Reproduce: `p6d_label.py` (d1).
   - Fix: add `_screened` to `head_check` as `registry`, or drop the rows in the CLIs as the hook does. Correct :31.
2. **R6-F2 FOLLOW-UP: the CLI's read race.** [V, in process]
   - `_cli_pack` reads the pack. When it finds none, `lookup` (:949) and `file_entry` (:1029) read it again, and `_label` sees `pack=None`.
   - So a pack written between the two reads prints with no label. In d3, the undone commit's canary def showed.
   - Canonical path: a code-map write must land inside a window of microseconds. I measured no production trigger.
   - Fix: when `_cli_pack` finds no pack, print lookup's miss text without a second read.
3. **R6-F3 FOLLOW-UP: C2.** [V] `lookup --json` prints the label before the JSON, and stdout does not parse. No consumer reads it. Fix: put the check inside the document, or print the label to stderr.
4. **R6-F4 FOLLOW-UP: C4.** [V] `demo` prints the label, then "--- the entry L2b would inject (161 bytes) ---" (:1234). Fix: name the header by what the text is.
5. **R6-F5 FOLLOW-UP: C1, the builders keep GIT_*.** [V]
   - A manual build with GIT_DIR naming a same-tree repository shows that repository's commit subjects and `@commit`. One of those commits is not in this repository at all.
   - With another tree, the hook shows 0 bytes.
   - F9's class. Contract: K2-FU item 5 said to change none of these sites, and D-117 (b) holds.
   - Canonical path: none. The post-commit hook exports this repository's own gitdir or no GIT_DIR, and `recover` strips.
   - Fix: `env=_own_env()` in `_git` (:932), and in codemap's git calls (`_head` :690, `_committed` :695, `all_code_files`).
6. **R6-F6 FOLLOW-UP: no test holds the recovery's time bound.** [V]
   - The mutant `recover-waits-for-build` passes `[recover]` and every behavioural check. Its one failure is the interaction at :1986.
   - The landed code meets the bound: 58 ms, while the build stayed alive 16.2 s more.
   - Contract: item 9 asked for a bound that is measured and stated. Its Test line names two other cases.
   - Fix: add my shape J as a check. A git shim sleeps in `log`, and the reset must return within a few seconds while the build pid is still alive.
7. **R6-F7 INFO: a burst of session starts after a crash builds more than once.** [V]
   - 8 starts gave 7 builds; 16 starts gave 9. They ran one at a time, never beside each other.
   - Each extra build darkens the hook again for its marker phase: 1.3 to 1.6 s on the real tree.
   - Each spawn opens the recover log with `O_TRUNC` and without `O_APPEND`, so the log keeps only the last build's line.
   - Contract: "start one build, never beside a live build". Each start starts at most one build, and "never beside" holds.
   - Fix (optional): after the spawned build takes the lock, it re-reads BUILD.json and exits if the record is no longer a marker.
8. **R6-F8 INFO: a link or FIFO in the state stops the recovery.** [V]
   - BUILD.json as a symbolic link or a FIFO gives `{}`.
   - The lock or the log as a symbolic link or a FIFO gives `{"error": "OSError"}`. The reset's own record fields are lost, but the seen markers are still removed.
   - No hang (41 to 63 ms), and the victim files are unchanged.
   - The hook stays dark until the next build. The state is trusted (round-5 F10).
9. **R6-F9 INFO: a hard link at the recover log truncates its target.** [V]
   - Afterwards the victim held the build's output line.
   - `open_regular` refuses a symbolic link or a non-regular file, but not a second name of a regular file.
   - Same class as `_write`'s temporary file (`O_TRUNC` before the rename) and the jsonl log (`O_APPEND`).
   - The attack needs write access to the state and, under protected_hardlinks, to the target. So it gains nothing.
   - Fix (optional): open with `O_APPEND` and without `O_TRUNC`, or use `_write`'s rename.
10. **R6-F10 INFO: C3, the kill switch does not stop the recovery build.** [V] This is documented, and the post-commit build ignores the switch too. It belongs in the owner's registration question.
11. **R6-F11 INFO: a root that cannot build spawns one failing build per session start.** [V] With no `.git`, 3 starts gave 3 failing builds ("fatal: not a git repository"), and the marker stayed. In that state the hook shows nothing anyway.
12. **R6-F12 FOLLOW-UP (older than this increment): a code-map build that cannot resolve HEAD deletes packs silently.** [V]
    - rc 0, empty stderr, and alpha's pack is gone (codemap.py:810, then :744). 59ad820 has the same code.
    - It fails closed: the file's code part is missing until a good build.
    - Fix: when `_head` gives None, end the build with rc 1 and touch no pack. Handle a failed `_committed` the same way.
13. **R6-F13 INFO: the per-file guard also catches programming errors.** [V]
    - A TypeError costs its file (`failed`, with the type on stderr), and the build exits 0.
    - Exception classes that are only BaseException propagate.
    - A pack left behind by a failure shows only while its blob is still HEAD's (c1).
    - This is what F5 asked for.
14. **R6-F14 INFO: the reason in `recover`'s docstring is loose.** [V] It says (:836) "the marker is that build's". In shape B the marker was an older crash's. The rule itself holds: no build starts while the lock is held.
15. **R6-F15 INFO: the CLIs print, with no label, packs that the hook withholds for other reasons.** [V] The kill switch (d6) and a symbolic-link working file (d7). The pack is HEAD's committed code in both, so the label's words would be false. No change needed.
16. **R6-F16 INFO: the variables that the strip keeps.** [V]
    - GIT_OBJECT_DIRECTORY: an empty directory gives 0 bytes, and so does a clone's objects after HEAD moved.
    - GIT_NAMESPACE: no effect on `rev-parse HEAD`.
    - GIT_CEILING_DIRECTORIES: it only narrows discovery.
    - Each one fails closed or changes nothing.
17. **R6-F17 INFO: the test seam in `recover`.** [S for the relative path; V for D2]
    - `AF_FILEPACKS_STATE` goes on as `str(state)` to a build that runs with `cwd=ROOT`. A relative value would name another directory in the child.
    - In D2, pointing the seam at another repository's state put this repository's build there, and that repository's reader then showed 0 bytes (tree).
    - Production never sets the seam.
    - Fix (optional): pass `str(Path(state).resolve())`.
18. **R6-F18 INFO: round-5 findings outside task #420.**
    - F7, F8, F10 to F14 and F16 to F18 stand as reported. Nothing in d2e69c6 changes them.
    - F15 is closed by `recover`.
    - F5 is closed (c3).
    - F6 is closed: on the real tree, `parsed` is True 137, False 0, None 98, and the no-symbols check passes.

### What I reproduced, reviewed statically and skipped
- **Reproduced:** items 1 to 6 of the ask; C1 to C4; the both-patches tree and the smoke; the gates; five mutants.
- **Static only:**
  - The relative path in R6-F17.
  - The lane's other 11 mutants. I did not re-run them: the lane reported them, the coordinator reviewed them, and they are outside my ask.
- **Skipped:**
  - Permission shapes, such as a state directory owned by another user or read-only. I run as root, so a mode bit proves nothing.
  - The post-commit hook's per-pick runs during a rebase. That code is unchanged.

### Hygiene
- **S1-RATE lines** this round, each as its own text: s1-73d6efe3, s1-06a4ee0f, s1-c0f622e1, s1-2ea6f511, s1-2fdf3a27, s1-5ceb6807, s1-f71f6463, s1-3c86645d, s1-033e40b6, s1-fafcbc35, s1-87c57da7, s1-37f1faa5.
- **No top-level `cd`.** I used only `( cd … )` subshells, `git -C` and absolute paths.
- **Git:**
  - My only git writes were worktree add and remove, with hooks off (wt, wtmut, wtboth), and `git apply` in wtboth's working tree.
  - The shared tree's `git status --porcelain` is empty. Re-checked after the restart.
- **Processes:**
  - I waited for every build a reset reported: 24 pids, 0 alive at the end. No process of mine is left.
  - I did not touch the Jev relay or the codebase-memory daemon.
- **Files:**
  - I removed `<SR>/pt`, /tmp/vk6m, /tmp/vk6g, /tmp/vk6t, /tmp/vk6s, and a scratch git repository at `<R6>/gitenv`.
  - `grep -c filepacks` is 0 in /home/user/.claude/settings.json, in the repo's .claude/settings.json and in scripts/install_session_hooks.py.
  - I registered no hook, read no secret file and did not touch the live .jev.
- **Restart:**
  - The container restarted at about 22:40Z, after my cleanup (22:34:32Z) and after this report was written (22:35:47Z).
  - The hand-back tool was not available after the restart, so this final message carries the report.
  - After the restart I re-ran no check.

### Gate
**MERGE-READY-WITH-FOLLOWUPS** for registering K2 at d2e69c6 (for these files, the same as origin 4750728), with K2-registration.patch and K2-post-commit.patch.
- Condition: must-hold items 1 to 3 hold at landing.
- Blockers: none.
- Follow-ups: R6-F1 to R6-F6, and R6-F12 (older than this increment).
- I reproduced every result this rests on, except the coordinator's landing steps: the manifest regeneration and the live must-hold build run.
