> Coordinator note (2026-09-29 07:4xZ): the report of record, extracted by `scripts/stack.py harvest` (run s-20260929T074108Z-b71211). Served model: claude-opus-5-5 on all 298 assistant records, 0 refusal stops, 2 tool-error clusters. `report_lint`: 3 refs, 1 OK, 1 MISS (`scripts/codemap.py:629` is `build_one`, cited with its module prefix), 1 UNCHECKABLE. Local ids: none cited. The coordinator's disposition: MERGE-READY-WITH-FOLLOWUPS accepted with its condition; the hook stays unregistered until K2 round 2 (one focused repair, D-031) adds F1's defence in depth and delivers the registration as a patch; the owner decides on the cost (about 0.12 s per call, about 36.5 KB and 30 score lines per window).

# VERIFY-K2 report (task #353, D-106)

Lane: sandbox `adversarial-verifier`, served model claude-opus-5-5 (this session). No subagent, no PC bridge, no outward action. Clock at hand-back: 07:3xZ (read `Tue Sep 29 07:36:44 UTC 2026`). PIN: origin d812c9b ("K2 landed (task #353; GATED-PENDING-VERIFY)…"). K2's five files and every dependency (system1 hook, wrapper, post-commit hook, installer, settings, session-hook and search-intercept tests) are byte-identical from the PIN to the current local HEAD (the coordinator's transcript-digest commit after "VERIFY-K1 round 2 home"). So every result here applies to the current tree.

## Gate recommendation

**MERGE-READY-WITH-FOLLOWUPS, on one condition: the post-commit patch lands before the registration or with it.** Without the patch, F1 meets all five blocking conditions and the recommendation is NOT-READY. That is the PIN's post-commit hook as it stands: it runs no file-pack build. One thing I did not reproduce: a stale `TRACKED.txt` arising inside the patched pipeline, from a failed or stalled build.

## Summary

- **Premise:** identical, byte for byte.
- **Gates:** they reproduce. 255 passed; with the patch applied, 223 passed and 7 declared skips.
- **Packs:** correct. 35 files against my own oracle, 0 differences.
- **Entries:** correct.
  - The symbol matched the AST 60 of 60 times.
  - Budget cuts were right 80 of 80 times, and the STALE mark 18 of 18.
  - Window keys and resets behave as designed.
- **Patch:** it never blocks or fails a commit, and it runs one build at a time.
- **Boundary:** it held for every shape I built but one. In F1, an untracked file's text reaches the model when `TRACKED.txt` is older than the commit that untracked the file.
- **Stalls:** two paths reach the wrapper's 55 s cap: the AF-AP-70 FIFO race, and a new quadratic Bash parse. No recorded input comes near either.
- **Registration:** the text matches `REG_PRE`/`REG_RESET`, but its list of forced test edits misses one.
- **Mutation:**
  - The builder's 55 mutants are all killed.
  - Of my 31, 21 survive the builder's 25 checks. My new checks kill 17 of those, and 4 are equivalent.

## 1. Premise (item 1)

I ran `bash scripts/premise_block.sh` on the brief's six commands in a clean detached worktree at d812c9b, then diffed against the brief's block: `PREMISE-IDENTICAL`. In the main tree:
- `filepacks` appears 0 times in the repo settings, the installer and `/home/user/.claude/settings.json`.
- The live `.jev` holds no `filepacks.jsonl` and no `filepacks-seen`, so the hook has never run live.

## 2. Finding inventory (no severity filter)

**F1: an untracked file's text reaches the model when `TRACKED.txt` is older than the untracking commit.** BLOCKER if the registration lands without the patch; otherwise FOLLOW-UP.
- **Evidence (reproduced).** Run on a fixture repo, using the real wrapper, `REG_PRE`, and the real `codemap.py refresh --commit … --lock-dir … --graphs graft -- scripts/gamma.py` exactly as the post-commit hook calls it, after `graft build`:
  1. A file-pack build: `TRACKED.txt` lists `scripts/gamma.py`.
  2. `git rm --cached scripts/gamma.py` and a commit. The file stays on disk; no file-pack build runs after the commit.
  3. Canary text is written into the now-untracked file: a function name and a default argument.
  4. The L2a refresh prints `1 built`; the code pack now holds the canary.
  5. Through the wrapper the canary reaches the model's context on Edit (574 B), Read (453 B) and `cat` (453 B).
  - Control: one `filepacks.py build` at HEAD drops the file from `TRACKED.txt`, and the same three calls inject 0 bytes.
- **Mechanism.**
  - The boundary is `TRACKED.txt` from the last build (`scripts/filepacks.py:256-257`).
  - `_code_part` then shows the code-map pack (`filepacks.py:331-374`).
  - `codemap.build_one` builds from the working copy whenever the path is a file, tracked or not (`scripts/codemap.py:629`ff).
  - The L2a refresh passes every path the commit changed, deletions included (`scripts/hooks/post-commit:146-172`, then `codemap.py:1010`).
- **When `TRACKED.txt` is behind:**
  - (a) At the PIN. The post-commit hook has no build step, so registering without the patch freezes `TRACKED.txt` at its last manual build (7db59b9 in the live `.jev`).
  - (b) With the patch, after a build that fails or stalls. Its failure is only a line in `$T/filepacks-build.log`.
  - (c) On a venue where no graph is launched, so the refresh does not wait.
  - With the patch applied and healthy in the sandbox, the build (about 3 s) finishes long before the code-map refresh, which waits for the graph re-index. Only this timing closes the window; nothing checks it.
- **Contract mapping:** K2 brief item 4 ("an untracked file … gives nothing"); the VERIFY brief's report rule that such a hole is core-blocking.
- **Material effect:** untracked text in front of the model.
- **Reproduction:** `probe_p6.py` (setup in §6).
- **Fix:**
  - Land the patch first.
  - As defence in depth, show the code part only when the code pack's `blob` equals the file's blob at `BUILD.json`'s commit (the build can record blob ids from its `ls-tree`); otherwise show only the P2 lines. This closes F1 even when a build fails.

**F2: AF-AP-70 reproduced (the builder's NOT done 4).** FOLLOW-UP.
- **Stall rate.** I swapped each target between a regular file and a FIFO (hard-link renames) while the hook ran. Working file: 11 of 40 direct hook calls stalled past 5 s. Code pack: 10 of 40.
- **Window** (`strace -tt` on the real process, which inflates both): check to reopen 1.083 ms for the working file, 4.509 ms for the code pack.
- **Through the real wrapper:** one stall took 55.2 s, rc 0, nothing injected, and the stderr names the timeout. A sibling call in the same window took 0.61 s, injected nothing and logged `WindowLockTimeout`.
- A FIFO planted before the call is refused.
- **Contract mapping:** no frozen hang criterion. It needs a process that swaps a FIFO in within about 1 ms.
- **Fix:** open files with System-1's `open_regular` (O_NONBLOCK, then fstat) in codemap's `_load_pack`, `lookup`, `file_entry`, `edit_context` and `language`. That code is outside K2's additive boundary.

**F3: a quadratic Bash parse (new).** FOLLOW-UP.
- **Mechanism:** `_args` (`filepacks.py:160-181`) scans from each reader or `cd` word to the next separator and runs `shlex.split` on every word. System-1's prefix keywords (`time`, `do`, `sudo`, `env` …) create many command positions inside one simple command.
- **In process,** for 250, 500, 1,000 and 2,000 `time cat` pairs: 464, 2,028, 9,235 and 31,208 ms. System-1's own parse takes 1.4 to 10 ms.
- **Through the wrapper:**
  - 1,000 pairs (9,025 B) took 7,958 ms.
  - 3,000 pairs (27 KB) hit the cap at 55,127 ms.
  - The System-1 hook took 117 and 125 ms on the same commands.
  - 800 `do cd .` (6.4 KB) took 4,585 ms.
- **No recorded command comes close.** Over 46,969 recorded Bash commands in 336 transcripts: p50 0.24, p95 0.80, p99 1.48, max 16.7 ms; the largest command was 73,509 B.
- **Fix:** collect each simple command's words in one pass, or cap the words scanned per position.

**F4: wrong-file injections from the Bash parser.** FOLLOW-UP.
- **Oracle:** 85 crafted commands run in a scratch tree, with `strace -f -y` recording what each really opened. Result: 50 right, 28 miss, 7 wrong file.
- **The seven wrong files:**
  - A `cd` inside `( … )` (2 shapes) or `$( … )` (2 shapes) leaks into later commands. Each injected the real `deploy/README.md` pack while the command read `README.md`.
  - `pushd` is not followed.
  - A grep pattern that names a tracked path counts as touched (`grep scripts/b.py scripts/a.py`, `grep -e …`). By the contract's words this conforms.
- **Frequency** over 18,295 recorded main-loop Bash calls, against a scoped-`cd` model:
  - The two models disagree on a tracked file in 26 calls: 5 would inject a file the command never reads, 21 miss one.
  - `pushd` appears 0 times.
  - A grep-family pattern naming a tracked path appears in 33 calls.
  - 158 same-name pairs (`X` and `<dir>/X`, both tracked) exist; 13 have packs on both sides.
- **Fix:**
  - Scope a `cd` to its group.
  - Follow `pushd`/`popd`.
  - Treat the grep pattern as a pattern, not a file.

**F5: parser misses, one of them a defect in the System-1 integration.** FOLLOW-UP.
- **The defect:**
  - `bash -c 'cat scripts/a.py'` and `sh -c "cat scripts/b.py"` give nothing; `bash -c 'cat a b'` gives only `a`.
  - Cause: System-1's code text keeps the nested shell's closing quote (`bash -c ;cat scripts/a.py scripts/b.py'`). The last word carries the quote, `shlex.split` raises, and the word is dropped.
  - The same shape makes `ssh pc '…'` and `scripts/pc.sh '…'` inject the local tree's pack for a file read on the PC (every word but the last).
- **Misses by design or by the prefix list:**
  - `< file` input redirects, `xargs`, `find -exec`, `git show REV:path`.
  - Globs, braces, variables, `for … cat $f`, `\cat`.
  - `nice`, `stdbuf`, `command`, `timeout -k 3 5`, `sudo -u root`, `env -i`.
  - `cd -`, `cd "$PWD/x"`, the argument after `<( … )`, and `..` arguments.
  - Python's `open()`.
- **Fix:** strip an unmatched trailing quote before `shlex.split`.

**F6: the report's "a pack reached through a link gives nothing" is too broad.** INFO.
- **Followed:**
  - A directory link that stays inside the pack directory (545 B injected).
  - A linked `.jev/codemap` root (1,094 B).
  - A linked `<state>/filepacks` (545 B).
- **Refused:**
  - A linked pack file.
  - A code pack's parent linked out (nothing, logged `unreadable`).
  - A P2 pack's parent linked out of the pack directory.
- The state directory is trusted, so no untracked text passes.

**F7: the list of test edits the registration forces is incomplete.** FOLLOW-UP; a landing step.
- I applied the report's two JSON entries and its installer snippet, taken verbatim from the report file, in a clone.
- **Before any edit:** `tests/test_session_hooks.py` (`1 files set=7d112c4ffb8c`): `pytest-exit: 1` / `pytest-summary: 6 failed, 26 passed in 4.02s`.
- **After the builder's 7 listed edits:** `pytest-summary: 1 failed, 31 passed in 4.11s`. The remaining failure is `test_wrapped_commands_name_their_own_event`, a `JSONDecodeError`: `_fake_repo` has no `scripts/filepacks.py`, so the new guard exits 0 and prints nothing.
- **Knock-on in a worktree:**
  - This also fails `tests/test_search_intercept.py::test_the_pair_passes_where_graft_or_rg_is_absent[no-graft]` and `[no-graft-no-rg]`, which run the session-hook tests nested.
  - Result: `1 files set=f1f58be04e7c`, `pytest-summary: 2 failed, 102 passed in 66.04s (0:01:06)`.
  - The clean PIN worktree gives `pytest-summary: 104 passed in 64.61s (0:01:04)`.
- **With an 8th edit** (`_fake_repo` writes a `scripts/filepacks.py` stub that prints its cwd), in a worktree with the registration: `2 files set=2415789b9582` / `pytest-exit: 0` / `pytest-summary: 136 passed in 70.32s (0:01:10)`.
- **Vendored manifest:** `vendored_manifest.py --check` fails on the `.claude/` row with the registration (rc 1) and passes on the clean PIN (rc 0). Regeneration is needed, as the report says.
- `test_system1_context.py` and `test_jev_context.py` pass with the registration.
- **The texts themselves:**
  - The report's PreToolUse entry equals `REG_PRE`, and its SessionStart entry equals `REG_RESET`, exactly.
  - Neither carries a `timeout` key.
  - The reset has no matcher, so it also runs on `clear`.

**F8: the per-window context cost is about a third higher than reported.** INFO / FOLLOW-UP.
- Each injection carries exactly 297 B of wrapper stamp and score-request line (measured on 74 injections).
- At the replay's median of 30 injections, that adds 8,910 B to the 27,591 entry bytes.
- The model also owes one `S1-RATE` line per injection. 73 of my 292 sampled calls injected.

**F9: latency on every Read, Edit, Write and Bash call.** INFO.
- **My sample:** 114 main-loop calls past the builder's byte cap, plus 178 calls from 40 seeded-random subagent transcripts. Each went through `sh -c <REG_PRE>` and through System-1's registered command, in alternating order.
- **Results:**
  - File packs: p50 119.0, p95 144.1, max 185.1 ms.
  - System-1: p50 105.7, p95 134.0, max 187.0 ms.
  - Paired difference: +12.2 / +36.0 / +63.6 ms.
- **Floors:** `python3 -c pass` 20.4 ms; the wrapper around `true` 45.8 ms; the guards alone 2.4 ms.
- Read had no PreToolUse hook before; it now pays about 119 ms per call.
- **In-process entry,** from the replay at the cap with the live root: p50 0.290, p95 0.947, max 5.233 ms over 5,438 entries. This meets the aim of p95 under 5 ms.
- **Parallel calls:** 8 and 16 parallel Reads in one window all injected, with no lock timeout.

**F10: other stall bounds, through the wrapper.** INFO.

| Input | Time |
|---|---|
| 50 MB P2 pack | 1,009 ms |
| 41 MB code pack | 1,735 ms |
| 65 MB `TRACKED.txt` | 304 ms |
| 20,000 `cd` in one command | 586 ms |
| 1 MB heredoc, then a reader | 326 ms |
| 5,000 files in one `wc -l` | 657 ms |
| 100,000 commands, then a reader | 534 ms |
| `TRACKED.txt` as a FIFO | 0.11 s (refused) |

- **Hostile Read `offset`/`limit`** (NaN, ±Infinity, negative, 0, booleans, strings, 1e308, 10^30): rc 0 in 116 to 151 ms. Each gives a file entry, a past-the-end entry or a range entry; no crash, no hang.

**F11: packs depend on the build's root path.** INFO.
- An absolute mention counts only when it names the root the build ran in.
- At the PIN, the live root gives 1,696 packs and a worktree root gives 1,685.
- A clone at another path, such as the PC's, builds different packs at the same commit.

**F12: the "creates nothing" claim is too broad.** INFO.
- A malformed payload with no state directory creates the directory and writes one log record.
- Any call writes System-1's bytecode under `<state>/pycache` once.
- The hook's import of codemap writes `scripts/__pycache__/codemap.cpython-311.pyc`, which git ignores.

**F13: pack `@sha7` ids can go stale.** UNVERIFIED (static only). `push_clean` rewrites unpushed commits without running post-commit. Until the next build, the `@sha7` in pack heads and commit lines can name commits that no longer exist (the builder's self-attack 3).

**F14: test gaps found by mutation.** FOLLOW-UP.
- **The builder's mutants,** with their controls in the same run: `2 files set=bd8d7c79afbe` / `pytest-exit: 0` / `pytest-summary: ================ 104 passed, 10 deselected in 356.16s (0:05:56) ================`.
  - By collected id: 40 file-pack mutants and 15 code-map mutants, all killed with their named failures.
  - Controls: 25 + 10 + 5 checks pass on the real code (plus 6 L2a refresh mutants and 1 lock control).
- **My 31 mutants.** My driver's control ran first: all 25 builder checks and my 18 new checks pass on the real code.
  - **Killed by the builder's checks (10):** write-not-a-target, edit-dup-by-file, edit-no-file-key, compact-forgets-session, abs-prefix-ignored, redirect-target-counted, budget-no-newline-cost, headline-shown-always, brief-names-itself, p2-before-code.
  - **Killed only by my new checks (17):**
    - fifo-working-file-read ("the hook stalled past 15 s").
    - code-pack-parent-link-followed.
    - path-field-unchecked.
    - schema-unchecked.
    - tracked-suffix-match: an untracked root `alpha.py` matched `scripts/alpha.py`'s tail.
    - window-count-not-incremented: a window at 63 files took two more in one call.
    - no-event-check: a PostToolUse payload injected.
    - reset-without-state-check.
    - no-age-prune.
    - replace-all-ignored.
    - offset-zero-not-clamped: a Read at offset 0 lost its whole entry.
    - dot-slash-ignored.
    - log-no-rotation.
    - commit-subject-uncut.
    - cd-variable-followed.
    - tilde-not-expanded.
    - no-nul-newline-guard.
  - **Equivalent (4):**
    - build-file-kept: no tracked root file named BUILD exists.
    - clean-keeps-links: the rename replaces a link anyway.
    - cd-dash-followed: both versions resolve to a miss.
    - commit-dedupe-dropped: `--name-only` lists a path once per commit.
- **Fix:** add the new checks. Start with the boundary and hang guards: the FIFO working file, the code pack's parent link, the path field, the schema, and the exact-line `TRACKED` match.

**F15: the packs are right.** INFO (positive).
- **Oracle:**
  - A per-file substring search with an explicit boundary rule.
  - Sources read with `git show` at the PIN.
  - A brief's last commit from `git log -1 -- <brief>`.
  - Commits from `git log -- <file>`, within the last 400.
- **Sample:** 35 files: 12 often named, 8 random with packs, 4 random without, 11 named only by absolute path.
- **Result:** counts and every mention field identical; 0 differences.

**F16: the entries are right.** INFO (positive).
- **80 recorded payloads on real files:**
  - Placed Edits named the AST's enclosing symbol 6 of 6 times. The other 31 recorded Edits no longer match the file and fall back to the file entry, as designed.
  - Ranges 24 of 24; whole-file entries 15 of 15.
  - The code text equalled codemap's own reader 45 of 45 times.
  - Every cut fell on a line boundary within 1,200 bytes and kept every line that fit, 80 of 80.
- **Synthetic Edits** (one unique line inside a definition, 20 files): 54 of 54.
- **STALE:** on 18 changed copies, all carry the mark as their second line, and tight budgets never drop it.
- **Window walk on `scripts/stack.py` through the wrapper:**
  - The first Edit injects the code part and the P2 lines; the same Edit again injects nothing.
  - An Edit of another symbol injects its code part only.
  - A later Read and a later `cat` of the file inject nothing.
  - A subagent is its own window.
  - Compact removes 1 marker; resume and clear remove 2; startup removes 0.

**F17: the patch works.** INFO (positive).
- **Apply:** `git apply --check` and `git apply` succeed in a `git clone --shared` at the PIN. The patched hook's sha256 prefix is fce110fe82d8b183, the builder's.
- **Setup:** only the patched post-commit on `core.hooksPath`, `AF_POST_COMMIT_TMP` in my scratch, docs-only commits.
- **Commit timings:**

| Scenario | Commit time | What the build did |
|---|---|---|
| Normal | 130 ms | Build 3,074 ms; `BUILD.json` = HEAD |
| Burst of 5 | 128 to 143 ms each | At most 1 running build in 400 samples; final `BUILD.json` = HEAD |
| Build lock held | 147 ms | No build until the lock was released, then one |
| Broken builder (SyntaxError) | 132 ms | Failed in the background |
| Builder hanging 15 s | 139 ms and 128 ms (two commits) | One running, one waiting on the lock, then both in turn |
| No `python3` on `PATH` | 127 ms | Log: `ionice: failed to execute python3` |

- **Side effects:** the wiki-stale marker went to the clone's own `.git`.
- **Screens:** `no_laya_in_gates: 41 files scanned, clean`; `--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---`.
- **Tests that name the hook,** patch applied: `5 files set=61956722b30e` / `pytest-exit: 0` / `pytest-summary: 223 passed, 7 skipped in 466.66s (0:07:46)`. The 7 are the declared slopo-model skips.
- The `$T` logs have no rotation, like the other post-commit logs.

**F18: gates and replay reproduce.** INFO (positive).
- **Gate** in a clean worktree at the PIN: `3 files set=804c19143d13` / `pytest-exit: 0` / `pytest-summary: 255 passed in 440.24s (0:07:20)`.
- **Replay** at the premise's cap, live root, packs at the PIN:
  - Calls and injections are identical in all 141 windows.
  - Injections per window: median 30, p90 52, max 66 (identical to the builder's).
  - Bytes per window: median 27,591, p90 49,885, max 65,512. Per-window deltas run from −1,794 to +2,379, from the newer commit's packs.
- **Builds of 9,949 tracked files:**
  - Live root: 3,028 and 2,713 ms (1,696 packs).
  - Worktree root: 3,480 and 2,556 ms (1,685 packs).
- On real data, 231 code packs name no untracked file.

**F19: an environment artifact, not K2.** INFO. In a `git clone --shared`, `tests/test_search_intercept.py` fails 3 tests with or without the registration (`3 failed, 101 passed` without it). In a worktree it passes. This hid F7's second consequence in the clone.

**F20: docs that go stale at registration.** INFO. `docs/research/findings/jev-trim/D105-DESIGN-v1.md` §10.3 ("Not built: L2b") and the LS-AUDIT S3 row.

**Boundary shapes tried (item 2), with results:**
- P1, a directory link inside the pack dir: followed.
- P2, the code pack's parent linked out: nothing (`unreadable`).
- P2b, `.jev/codemap` linked out: followed.
- P3, `<state>/filepacks` linked out: followed.
- P4a, an untracked file with planted packs: nothing.
- P4b, `TRACKED.txt` edited to list it: injected. `TRACKED.txt` is the trusted boundary.
- P4c to P4f, `TRACKED.txt` as a link, a FIFO, a directory, or empty: nothing.
- P5, a pack whose `path` field names another file, and schema 2: nothing (`corrupt`).
- P6: F1.
- P7, a tracked file replaced by a link to an outside file: P2 lines only; canary absent.
- P8, a code file's parent directory linked outside: code part with its STALE mark; canary absent.
  - Linking `scripts/` itself moved the hook's own `ROOT` through `Path(__file__).resolve()`, so that variant is inconclusive.
- P9, `pushd <other tree> && cat scripts/alpha.py`: the wrong file's pack is injected; canary absent.
- Bash via `cd`, `~`, `$HOME`, globs and variables: misses only; no untracked text.

## 3. Blocking predicate

- **F1:**
  - (1) contract: yes.
  - (2) canonical path: yes at the PIN, whose post-commit hook has no build step; not reproduced inside the patched pipeline.
  - (3) material: yes.
  - (4) discriminator: yes (`probe_p6.py`, with its control).
  - (5) ownership: yes (K2's boundary, K2's patch).
  - Result: blocking for a registration without the patch; FOLLOW-UP once the patch lands.
- **F2, F3:** fail (1) and (2). There is no frozen hang criterion, and each needs an adversarial swap or a crafted command.
- **F4, F5:** fail (1) and (3). The contract names the System-1 parser, and the effects are rare misleads or misses.
- **F7:** a landing step outside the landed code.
- **F14:** test gaps, not a production defect.
- **All others:** INFO.

## 4. What must hold before registration

1. The post-commit patch lands before the registration or with it. One post-commit build must have run, so that `BUILD.json`'s commit equals HEAD, before any session loads the hook (F1).
2. Recommended with it: show the code part only when the code pack's `blob` equals the file's blob at `BUILD.json`'s commit; otherwise show the P2 lines only. This keeps F1 closed when a build fails.
3. In `tests/test_session_hooks.py`: the builder's 7 edits, plus `_fake_repo` writing a `scripts/filepacks.py` stub (F7). Then regenerate the vendored manifest. Then gate the session-hook and search-intercept tests in a worktree (136 passed here).
4. Accept the real cost, which is an owner or coordinator decision:
   - About 119 ms on every Read, Edit, Write and Bash call.
   - About 36.5 KB per window at the median (27.6 KB of entries plus 8.9 KB of stamps).
   - About 30 `S1-RATE` lines per window (F8, F9).
5. Update the docs that say L2b is not built in the landing commit (F20).

## 5. What I reproduced, reviewed statically, or skipped

- **Reproduced:** everything in §2 except F13.
- **Static only:**
  - F13.
  - The harness's 60 s default hook timeout (taken from the wrapper's comment).
  - Claude Code's matcher anchoring (not examined).
- **Skipped:**
  - The builder's 51-file ripwire union: beyond the gate rule.
  - Any PC run: no bridge, by rule.
  - The whole `test_vendored_manifest.py`: a disk risk (env-tool-quirks); I used `--check` instead.

## 6. Files, re-run, hygiene

- **Code under test:**
  - `/home/user/agent-factory/scripts/filepacks.py`: `_args` at :160, `tracked` at :256, `_code_part` at :331.
  - `/home/user/agent-factory/scripts/codemap.py`: `build_one` at :629, `_load_pack` at :865, `file_entry` at :951.
  - `/home/user/agent-factory/tests/test_filepacks.py`
  - `/home/user/agent-factory/tasks/briefs/jev-trim/K2-post-commit.patch`
- **My probes and logs** are in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2/`:
  - Probes: `probe_p6.py`, `probe_boundary.py`, `probe_fifo.py`, `probe_stall.py`, `probe_time.py`, `quad.py`, `realparse.py`, `parser.py`, `cdscope.py`, `oracle.py`, `entry_check.py`, `entry_check2.py`, `window.py`, `lat.py`, `par.py`, `patchtest.sh`, `mutdrv.py` (reads `VK2_S`).
  - Transcript readers: `sample.py` and `tu.py`.
  - Logs: `logs/`.
  - Pack states: `state` (worktree root) and `state-live` (live root), both built at d812c9b.
- **To re-run:**
  ```
  S=<that dir>
  git -c core.hooksPath=/dev/null worktree add -q --detach $S/wt d812c9b
  mkdir -p $S/wt/.jev $S/bt && cp -a /home/user/agent-factory/.jev/codemap $S/wt/.jev/
  (cd $S/wt && AF_FILEPACKS_STATE=$S/state python3 scripts/filepacks.py build)
  python3 $S/probe_p6.py $S
  ```
  - `sample.py` writes recorded tool inputs to a file; delete it after use.
- **Hygiene:**
  - Every write in the shared repo:
    - One `git fetch` at the start, to confirm the PIN on origin.
    - `git worktree add` and `git worktree remove` for my two scratch worktrees.
  - The live `.jev` was read only (`cp -a` of `.jev/codemap`).
  - Both worktrees and the clone are removed, and the payload file with recorded inputs is deleted.
  - No process of mine is running, and `git status` in the shared tree is clean.
  - From transcripts I accessed only `tool_use` blocks and compaction boundaries, and printed only counts, bytes and timings.
  - One self-inflicted incident: a `pkill -f` in a probe matched my own Bash command line (rc 144, the env-tool-quirks rule). I stopped the orphaned probe by process group; nothing outside my scratch was affected.