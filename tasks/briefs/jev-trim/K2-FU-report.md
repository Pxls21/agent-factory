# K2-FU: the builder's report of record (task #420, D-120)

> **Coordinator note (2026-09-30 20:4xZ).** The K2-FU lane (task #420, a sandbox code-implementer on Opus 5.5) came home
> at 20:4xZ. Its final message is saved verbatim below. Harvest run s-20260930T204506Z-48a93c: 373 assistant records,
> every one claude-opus-5-5; 0 refusal stops; 1 tool error; one compaction. The lane made no SubagentHandback call, so
> the harvest's hand-back step failed and took the report from its final message (sha256 prefix 534abc53d860,
> report_lint OK, no local ids). The harness marked the message as instruction-shaped (a settings-json pattern): it
> names the registration patch's `.claude/settings.json`, and nothing in it was acted on.
>
> **The coordinator's gate: MERGE-READY-WITH-FOLLOWUPS, GATED-PENDING-VERIFY until the verifier's narrow re-check.**
> The patch (sha256 prefix 5cc5e6b56b78) applies at HEAD, whose four files equal the PIN's, and after `git apply` the
> four files match the table below (line counts and sha256 prefixes). The review:
> - C1, F4's builder finding (history only, and only from a manual run with a foreign `GIT_DIR`): F9's class, not the
>   tree class. It goes to the verifier's re-check and to the owner's registration question: removing `GIT_ENV` in the
>   builders' git calls (`_log` at `scripts/filepacks.py:959`, and the other rows of the call-site table) is the same
>   small change as `_rev`'s.
> - C2, `lookup --json` prints the label before the JSON document (`_label`, `scripts/codemap.py:1116`, then the print
>   at :1217). Nothing parses that output (the only reference is the usage line), so it is a follow-up: with `--json`
>   the label belongs inside the document.
> - C3, `recover` (`scripts/filepacks.py:831`) runs with `filepacks-off` set, as the reset did at the PIN: only the
>   hook path checks the switch (:889), and no build does. The switch stops injection, not builds; the owner's
>   registration question says so.
> - C4, `demo` prints "--- the entry L2b would inject" (`scripts/codemap.py:1234`) under a label that says the text is
>   not HEAD's committed code: a wording follow-up.
> - C5, `_ast_symbols` now returns None on a failed parse: its one production caller (`build_one`) maps it to `[]` and
>   records `parsed`, and the mutation anchors in both test files are unchanged lines. `build()`'s failed entry
>   `(rel, "failed", None)` is handled by both consumers: the refresh line counts it, and the build CLI's `if pack:`
>   skips its None.
> - C6, one change at landing: the sentence in `tests/test_filepacks.py`'s docstring (the lane's NOT-done item 3) now
>   matches F9's.

## The lane's final message (verbatim)

**K2-FU (task #420) report. Patch done and gated. One finding for you first (F4).**

The patch is `/home/user/agent-factory/tasks/briefs/jev-trim/K2-FU.patch`: 777 lines, sha256 `5cc5e6b56b782e4cc3d41e8cce4258228710e1dbf51811dd72cc22537e9c5624`. `git apply --check` exits 0 at the PIN (59ad820) and on the shared tree's working copy. There are no commits, no hooks registered, and all worktrees are removed.

## F4 finding first: one builder site does not fail closed for history (not changed, as the brief says)
Suppose `filepacks.py build` inherits a `GIT_DIR` that names another repository whose HEAD has this HEAD's tree. The hook then shows that repository's history. Measured (`p/f4b.py`): `commit 1099fb9 2026-01-01: foreign subject fhf3a6f00105` and the head line `@1099fb9`, while this repo's HEAD is `10aed24`.
- Tree bytes still fail closed.
- Only the commit lines and `@commit` leak. This is the same class as F9's same-tree ref move.
- How it could happen: git exports `GIT_DIR` to hooks only in a linked worktree, and there it names that worktree's own gitdir. So the path is a manual run with `GIT_DIR` set.

## Premise
13 commands. Expected and actual output are byte-identical (sha256 `f867dbc787f744d8` both, run 19:32Z). The PIN baseline was `pytest-summary: 175 passed in 160.86s (0:02:40)`.

## Contract items (verified: run or measured)
1. **Premise:** as above.
2. **F1:** new check `registry-committed`. It uses the real `codemap.py build`, then the file-pack build, then the hook.
   - The canary is absent on an Edit placed on its line.
   - The control shows `registry rows here 1: AF-AP-175 :18 ref = "HEAD"  # the committed hit — `.
   - The verifier's mutant `registry-from-working-text-fullfp` is KILLED: `E AssertionError: an uncommitted line reached the model through a registry row: 'codemap scripts/alpha.py:6 — function helper L5-6 …`.
3. **F2:** `head-unresolved` gains two cases with a failing git: a record with no tree and no id, and a marker. Mutant `current-none-equals-none` is KILLED: `E AssertionError: a record with no tree and a git that fails showed a pack: 'filepack docs/NOTE.md @f7a303a: …`.
4. **F3:** new check `cli-label`.
   - The label line is `codemap: NOT HEAD's committed code (tree): no file-pack build of HEAD's tree`. The same shape covers `(blob)` and `(symbols)`.
   - Without `scripts/filepacks.py` the line is `codemap: NOT CHECKED against HEAD's committed code: …`. `tests/test_codemap.py`'s demo check now expects that line.
   - After `--mixed` and `--hard` resets, both CLIs print the label first and the rest unchanged. The control at HEAD's tree prints no label.
   - The usage line (old :30) now reads "the code map's entry for a recorded Edit payload".
   - At the PIN the check fails: `…printed a pack of another tree without the label`.
5. **F4:** `_rev` now runs git with `GIT_DIR`, `GIT_WORK_TREE`, `GIT_COMMON_DIR` and `GIT_INDEX_FILE` removed, from `cwd=root`.
   - The PIN reader with `GIT_DIR` set to a clone showed 302 bytes including the canary. Mine shows 0 bytes, skipped as `tree`.
   - New check `foreign-git-dir`. Its leak control uses a git shim that reads the clone, and the canary shows.
   - At the PIN the check fails: `a foreign GIT_DIR's HEAD decided what shows`.
   - In a linked worktree, the stripped `_rev` resolves the worktree's own tree in all four environment cases (`p/f4wt.py`).
6. **F5:** I kept `_ast_starts` and made it catch `RecursionError` and `MemoryError` in both the parse and the walk. I did not drop it: `_moved` uses it, and `test_codemap`'s record-that-lies check asserts the stale mark it produces. `build()` now has a per-file guard: a failing file becomes `failed` with its reason on stderr.
   - Depths measured on Python 3.11, 3.12 and 3.13: a 1,500-deep chain parses, and the PIN's walk raises RecursionError. A 20,000-deep chain raises MemoryError in the parse. Each takes 5 ms or less.
   - New check `deep-chain`: exit code 0; alpha.py has its 5 symbols; both chains keep their packs; the long-name file is `failed` with an OSError.
   - Timing: the check takes 0.23 s. The four-file build takes 0.08 s wall; alpha alone takes 0.06 to 0.07 s.
   - At the PIN: `one bad file ended the code-map build: rc 1 …line 628, in _ast_starts`.
7. **F6:** new check `no-symbols-lines`. The texts are:
   - `no symbols: the committed blob does not parse`
   - `no symbols for shell`
   - `no symbols: the committed blob defines no function or class`
   - on an Edit, `module level (…)` with the same reason.
   - At the PIN: `'codemap scripts/broken.py — 0 symbols, 0 at top level …`.
8. **F9:** only that sentence changed. It now reads: "Every byte shown, the readers' own words aside, is committed text of HEAD's tree or the build's commit history (P2's commit lines, a brief's last commit and date, the head line's `@commit`), and after a same-tree ref move that history can hold commits HEAD's history lacks".
9. **F15:** new `recover()`, called from `reset`.
   - When the record is a marker and the lock is free, it starts one build: in the background, niced, in its own session, with the git variables removed. Its record says `rebuild: started` with the pid.
   - When the lock is held, the record says `busy` and no build process exists.
   - New check `recover`. At the PIN: `a crashed build's marker was not rebuilt at SessionStart`.
   - Both K2 patches are unchanged. This runs on the reset path the registration already calls.

## F4 call-site table (other sites unchanged, as the brief says)
| Site | Can an inherited GIT_* reach it? | What a foreign GIT_DIR does | Fail closed? |
|---|---|---|---|
| filepacks `_build` rev-parse HEAD / sha^{tree}, `ls-tree`, `_blobs` cat-file | yes | the build describes the foreign HEAD; the reader shows 0 bytes (`tree`) (measured) | yes |
| filepacks `_log` (and the `@commit` taken from the build's sha) | yes | same tree: foreign commit lines are shown (measured) | **no, history only** |
| codemap `_head`, `_committed` | yes | a pack of the foreign blob; the reader skips it as `blob`, or `tree` if both builds are foreign (measured) | yes |
| codemap `all_code_files` (`build --all`) | yes | lists the foreign index; its packs then go through the rows above (measured) | yes |
| filepacks `recover` (starts a build) | no | the variables are removed before the build starts | n/a |
| filepacks `replay` | yes | the hook it runs strips them in `_rev` | yes |

`GIT_COMMON_DIR`, `GIT_WORK_TREE` or `GIT_INDEX_FILE` alone changed nothing at the PIN reader or at any builder site (measured). That is why the test covers `GIT_DIR` only. A garbage `GIT_DIR` makes the builders fail or drop packs, which is closed (inferred from the code, not run).

## F15 measured bound
REG_RESET run through `sh`, n=20:

| State | Wall time (median / p95 / max) | Hook's own time (median / max) |
|---|---|---|
| no marker | 53 / 65 / 72 ms | 5 / 11 ms |
| marker, lock free (build started) | 60 / 72 / 78 ms | 8 / 10 ms |
| marker, lock held (busy) | 53 / 66 / 77 ms | 5 / 6 ms |

With a build slowed by a git shim, the reset returned in 54 ms and the build ran 18.2 s more. So the session start waits for the start of the build, never for the build.

## Files
| File | Lines | sha256 now | sha256 at PIN |
|---|---|---|---|
| `scripts/filepacks.py` | 1307 | `b4280c0da1ebb54f` | `be82ab16c83a1402` |
| `scripts/codemap.py` | 1241 | `6f61344589bfc3e7` | `15f41cb1400f34f2` |
| `tests/test_filepacks.py` | 2481 | `b3ef201508b996a6` | `0ae34b5c13aaa7d6` |
| `tests/test_codemap.py` | 1053 | `b0cde454ba6588f5` | `08e48d868a92cedb` |

Total: 487 insertions, 33 deletions. pyflakes exits 0 on all four. The AP screen shows one new tell: AP-1 at `codemap.py:1212`, an environment read done once at CLI start. The PIN's `filepacks.py:1280` has the same tell.

## Gates (pasted)
- `tests/test_filepacks.py` (`1 files set=db64e610236b`), two runs: `pytest-summary: 194 passed in 186.92s (0:03:06)` and `pytest-summary: 194 passed in 190.20s (0:03:10)`.
- `tests/test_codemap.py tests/test_system1_context.py` (`2 files set=395f8af3a0ce`): `pytest-summary: 204 passed in 296.02s (0:04:56)`.
- Tree with both K2 patches (PIN + my patch + both K2 patches):
  - `tests/test_session_hooks.py tests/test_search_intercept.py` (`2 files set=2415789b9582`): `pytest-summary: 144 passed in 53.66s`.
  - `tests/test_vendored_manifest.py -k test_committed_manifest_matches_fresh_generation` (`1 files set=21e700b8344c`): `pytest-summary: 1 failed, 56 deselected in 1.25s`. The `.claude/ (kit-adapted)` row drifts, as the brief expected: `f0acf40e…` committed, `1b63d45d…` generated. The cause is the registration patch's `.claude/settings.json`: on PIN plus my patch alone, `pytest-summary: 1 passed, 56 deselected in 1.63s`. The coordinator regenerates at landing.
- `stack.py gate` plan: only `tests/test_codemap.py` and `tests/test_filepacks.py` name the changed files, and both ran above.

## Mutants
The driver (`mut/drv.py`) works in a fresh copy per mutant, with bytecode off:
- The control ran first: `7 passed`.
- 13 mutants run; the brief's required eight are among them. All 13 are KILLED, each with its named `E AssertionError` line.
- For every mutant, the fixture's copy of the file was confirmed to be the mutant.
- Result line: `EXPECTED=13 GRADED=13 KILLED=13 SURVIVED=0 INVALID=0`, `VERDICT: PASS`, exit code 0.
- Self-test with 1 row: `VERDICT: FAIL`, exit code 1.

Red-green at the PIN: five of the new checks fail with their named messages. `registry-committed` and `head-unresolved` pass at the PIN, because F1 and F2 were missing tests, not code defects; the verifier's two mutants are their failing side.

## NOT done
- No builder git call site was changed (the F4 finding above).
- The CLI label checks only the three conditions the brief names. It does not check the registry-screen condition (`_screened`).
- `tests/test_filepacks.py:34` still has the old false sentence ("every byte shown is committed text of HEAD's tree"). I left it; F9 named only `filepacks.py`.
- The vendored manifest is not regenerated.
- The two K2 patches are unchanged.
- Two sessions starting at once could each start a build. The builds run one after the other on the build's lock (inferred from the code; no test covers it).

## DISCREPANCIES
- `demo` still prints "--- the entry L2b would inject ---" under the label. The brief said the rest prints as today.
- `lookup --json` output is no longer one JSON document when a label is printed.
- Packs built before this change have no `parsed` field, so they say only "no symbols" until the next code-map build.
- Recovery runs even with `filepacks-off` set. The reset already ran with the switch set at the PIN.
- `stack.py gate` wrote its run record to the shared `.jev/stacks/` (run `s-20260930T202337Z-c8b472`). This is a side effect of the brief's own command, not a git write.
- Mistakes of mine:
  - One top-level `cd /home/user/agent-factory` at about 19:54Z. It was already the primary directory, so nothing moved.
  - I first read two exit codes from `tail` in a pipe. I re-ran both with the real exit code.
  - The first PIN red-green run errored at setup because its basetemp parent did not exist. It read as 1 error, not as a kill; I fixed it and re-ran.

## Self-attack: how could a pack or a CLI still show a byte HEAD's tree does not hold, without saying so?
1. **A builder with a foreign same-tree `GIT_DIR`:** foreign history is shown (measured, open).
2. **A same-tree ref move:** the build's history is shown. This is the F9 residual, now documented in the docstring.
3. **The CLIs:** they can print registry rows whose message came from an uncommitted screen edit, unlabeled. There is also a tiny race: if a pack appears between `_cli_pack`'s read and `lookup`'s own read, its text prints unlabeled.

The three most likely ways my change is wrong, and how each was ruled out:
- **F15 starts a build beside a live one.** The lock probe plus the build's own blocking lock serialize builds. The busy test finds no build process, and the ignore-the-lock mutant is killed.
- **F4 breaks a worktree or the no-repository case.** The linked-worktree probe resolved the worktree's own tree in all four cases, and all `head-unresolved` cases pass.
- **F5's guard hides errors.** Each failure is named on stderr and marked `failed`. Interrupts still pass through. The guard-removed mutant is killed.

Logs and probes are in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/k2fu/`:
- `logs/`: the six gate logs
- `mut/`: `final.log`, `selftest.log`, `pin.log`, `drv.py`, `pin.py`
- `p/`: `f1.py`, `f4.py`, `f4b.py`, `f4wt.py`, `f15.py`, `f5t.py`

Cleanup: no processes of mine remain, and `/tmp/k2fu` is deleted.
