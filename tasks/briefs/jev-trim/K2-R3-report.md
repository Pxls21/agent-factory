> **Coordinator note (2026-09-29 20:3xZ).** Landed as GATED-PENDING-VERIFY: the patch
> `tasks/briefs/jev-trim/K2-R3.patch` (sha256 f6f480b3...) applied to the shared tree, gated there twice (the counts
> are in the landing commit). NOT done 1 (uncommitted text in a TRACKED caller or test file) stays the follow-up class
> VERIFY-K2 round 2 rated it; the round-3 verify re-checks it. The hook stays unregistered. The builder's `logs/` and
> `vk/` paths are its sandbox scratch (`scratchpad/k2-lane-353/r3/`), not repo paths; its line refs are to the
> patched files.

# K2 round 3 report (task #353, D-111): B1, B2, B3, the seven checks, the stale documents, the patches

Written 2026-09-29 20:1xZ by the K2 build lane (sandbox, Opus 5.5). PIN origin 99583a2. Brief: `tasks/briefs/jev-trim/K2-R3-brief.md`.

Evidence tiers:
- [V]: I ran it and pasted the output.
- [I]: read from the code, not run.
- [A]: assumed.

The evidence lives in my scratch, `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/k2-lane-353/r3/`: the logs in `logs/`, the probes in `vk/`, and `b3mut.py`. Paths below that start `logs/` or `vk/` are relative to that directory. The worktrees are removed (section 9).

**Answer first.**
- All six contract items are built in a worktree at the PIN and gated there on the final bytes.
- The one deliverable in the shared tree is `tasks/briefs/jev-trim/K2-R3.patch`:
  - 695 lines; sha256 f6f480b38272e0bcd29f224d2aa81b60224a201e670ac11850c130a5f2e61d3b.
  - 5 files; 539 insertions, 17 deletions.
  - It equals `git -C <wt> diff 99583a2` byte for byte.
- One boundary hole stays open, of the class VERIFY-K2 R2 rated FOLLOW-UP. A probe proves it: uncommitted text in a TRACKED caller file still reaches the model (NOT done 1).
- The hook stays unregistered.
- My recommendation: ready for the verify round. This is not a final verdict.

## 1. NOT done

1. **Uncommitted text in a tracked caller or test file reaches the model [V].**
   - The probe `vk/probe_uncommitted_caller.py` runs the healthy pipeline: the real patched hook, and all graphs fresh. Its log is `logs/residual-uncommitted-caller.txt`.
   - It adds an uncommitted function to the tracked `scripts/caller_trk.py`. The Edit then shows: `callers in tracked files (the total is left out): <TRK> scripts/caller_trk.py:4 · <UNCOMMITTED> scripts/caller_trk.py:8`.
   - Why: GitNexus indexes the working bytes of every file. TRACKED.txt vouches for a path, not for its bytes.
   - This satisfies item 1's letter. It also matches D-034's letter as VERIFY-K2 R2 read it (FOLLOW-UP). But it is still text that no commit holds.
   - Fix direction [I]: the builder records, for each caller file, the graph's indexed sha256 beside the committed blob. The reader keeps a caller only where the two match.
   - The same holds for code-review-graph's test names in a tracked test file [I].
2. **The risk line's numbers still count untracked dependants [I].** The line holds numbers only, with no name or path. `_risk_line` (`scripts/codemap.py:816`) prints GitNexus's `impacted` and `direct` counts.
3. **The same-file channel has no committed real-pipeline test.** The planted check `same-file-stale` covers it in the suite. The real-pipeline run is a scratch probe only (`vk/probe_samefile.py`; see DISCREPANCY 2).
4. **Item 3's pre-image assertion has no killer.** The mutant `pre-image-unchecked` survives. It stays equivalent while `UNPATCHED_AT`'s hook is the patch's pre-image, and the unit test and both gates show that it is.
5. **Out of scope (issue #83), untouched:** findings 5, 6, 7, 9, 12 and 15. One side effect: finding 5's mutant `pack-not-handed` is now killed by my check `untracked-callers` ("an untracked test reached the model").
6. **No PC run.** The rules forbid the bridge.
   - Three tests use the real instruments: round 2's real-refresh test and round 3's two.
   - Each skips LOUDLY where graft, gitnexus or code-review-graph is missing.
   - This sandbox has all three, so every gate ran them. No summary line shows a skip.
7. **The builder's stamp-then-read window [I, not probed].**
   - The code map stamps a graph `fresh` when the graph's recorded sha256 equals the bytes it read. It queries the symbols after that.
   - A re-index between the two steps would give another content's symbols under a `fresh` mark.
   - The stamp is `_fresh` (`scripts/codemap.py:287`).
8. **Instrument notes render verbatim [I, not probed].** I did not probe whether any GitNexus error text can name an untracked path. The two places are:
   - an instrument's note, `sec.get("note", "")` (`scripts/codemap.py:819`);
   - an impact error, `g.get("risk_error", "no answer")` (`scripts/codemap.py:823`).
9. **TRACKED.txt is the build's list [A].** Suppose a caller file is untracked with `git rm --cached` after a build. It stays listed until the next build. The patched post-commit hook builds on every commit.
10. **Item 2's alternative was not pursued** (tie the symbols to the blob itself). The stale-graph clause is the brief's primary design. The pack's own sha256 already makes the tie: `fresh` means the graph's recorded sha256 equals the pack's bytes.
11. **Landing work stays with the coordinator:**
    - Apply the patch.
    - Regenerate the vendored manifest when the registration patch lands.
    - Save this report where the K2-R2 notes point (DISCREPANCY 7).

## 2. DISCREPANCIES

Each item is either a deviation from the brief's letter, or a fact the brief did not expect.

1. **Item 1 says "recounted over what is kept, or dropped". The total is always dropped, never recounted.**
   - Why: the pack samples at most three callers, so a recount would not be exact.
   - A symbol's total stands only when all three of these hold:
     - GitNexus is fresh;
     - every entry of `caller_files` is a TRACKED.txt line;
     - the filter removed no sampled caller.
   - The code: `all_kept` (`scripts/filepacks.py:589`) and `len(kept) < len(sample)` (`scripts/filepacks.py:596`).
   - Otherwise count and tests become None, and the code map's reader prints `callers in tracked files (the total is left out): …`. Its branch is `c.get("count") is None` (`scripts/codemap.py:839`).
2. **An extension past item 1's letter: names from the file itself.**
   - A caller or test in `rel` is kept only when the graph that named it is fresh: `keep(x, graph)` (`scripts/filepacks.py:583`).
   - Why: a stale GitNexus graph of `rel` can name functions from bytes that no commit holds. That is B2's class, reached through B1's lists.
   - The scratch probe: the real code shows `none shown` and 0 canary bytes. The mutant `same-file-names-from-stale-graphs` shows `callers in tracked files (the total is left out): leak_<C> scripts/gamma.py:5`. Logs: `logs/samefile-real.txt` and `logs/samefile-mutant.txt`.
3. **Item 2's clause reads the graph named by `symbols_from`, not `instruments.graft.graph` literally.**
   - That is the graph the symbols came from: graft or code-review-graph.
   - A pack that holds symbols but names no source graph is withheld too (check `sourceless-symbols`).
   - The clause: `src is not None` (`scripts/filepacks.py:640`).
4. **`scripts/codemap.py` changed in one reader only** (`_callers_line`, +5/-2). The builder is unchanged. All 197 codemap and System-1 tests pass.
5. **Each 3-file gate run is two foreground calls.** One runs filepacks (set db64e610236b). The other runs codemap and system1 (set 395f8af3a0ce). Together they take about 11 minutes, which is above the 10-minute cap. The union's set id is 804c19143d13.
6. **Gate run 1 failed, and I fixed it.**
   - The run: `pytest-summary: 1 failed, 166 passed in 268.79s (0:04:28)`.
   - The failing test: `test_negative_control_the_same_check_fails_on_a_mutant[no-nul-newline-guard]` (DID NOT RAISE).
   - The cause: I had put a newline and NUL guard inside `Packs.tracked`. It overlapped `repo_rel`'s guard and made round 2's mutant equivalent.
   - The fix: `Packs.tracked` is back to the PIN's bytes. The guard now lives in `_tracked_only`, with its own mutant `tracked-newline-unguarded`. The guard: `listed(f)` (`scripts/filepacks.py:580`).
   - Every run after the fix is on the final bytes. The last write was at 18:59:48Z, and run 2 started at about 19:00:18Z.
7. **The K2-R2-report notes point to `tasks/briefs/jev-trim/K2-R3-report.md`, which does not exist yet.** Save this report there, or change the two pointers.
8. **Some item 2 and item 3 mutants are graded outside the in-file table.**
   - The in-file driver mutates `scripts/filepacks.py` only.
   - The `hook_dir` mutants ran through the scratch driver `b3mut.py`.
   - The "record why" mutant `stale-graph-recorded-as-blob` ran as a scratch one-off.
   - Committed tests kill all of them except `pre-image-unchecked` (NOT done 4).
9. **The planted fixture pack's `tests/test_alpha.py` is now filtered out of the rendering.** The fixture does not track that file. No existing assertion read it.
10. **"The verifier's 60" is its pool of 60 checks.** Its driver `mutdrv3.py` holds 57 mutants (31 + 11 + 15). I ran all 57 against 72 checks: my 62 and its 10.
11. **Live effect, read-only [V].**
    - Of the 233 live code-map packs, the B2 clause would withhold 0.
    - 17 packs have GitNexus not fresh, and 6 would lose their callers totals.
    - 4 sampled callers would be dropped, all in `scripts/jev_relay.py`. That file is tracked at HEAD, but the live TRACKED.txt comes from round 1's 7db59b9 build.
    - The live state also has no BLOBS.txt, so today every code part is withheld anyway (check `blobs-missing`).

## 3. Premise [V]

- I ran `bash scripts/premise_block.sh` from `/home/user/agent-factory` at 18:3xZ.
- The output equals the brief's block: `cmp` finds them identical, and both have sha256 fdaf56047f21d2be.
- So no CONTRACT-INVALID.

## 4. Per item: code and pasted evidence

### Item 1 (B1): no untracked caller or test reaches the model

**Code.** The filter is `_tracked_only` (`scripts/filepacks.py:571`).
- It runs after the blob and graph checks: `_tracked_only(pack, rel, packs, graphs)` (`scripts/filepacks.py:642`).
- It filters the tests: `keep(x, "code-review-graph")` (`scripts/filepacks.py:587`).
- It filters each symbol's callers sample, and drops any total it cannot vouch for (DISCREPANCY 1).
- A path counts only as a whole TRACKED.txt line, with no newline or NUL.
- The code map's reader shows a dropped total's kept callers: `_callers_line` (`scripts/codemap.py:836`).

**Red at the PIN.** The verifier's `probe_callers2.py`, log `logs/red-b1-pin.txt`:
- `Edit in helper: injected 1199 B; tracked name in context True; UNTRACKED name in context True; untracked path True`
- `line: callers 5 (2 in tests): <UNT> scripts/caller_new.py:4 · <TRK> scripts/caller_trk.py:4 · __init__ scripts/alpha.py:10 · +2 more`

**Green on the final bytes.** Log `logs/green-b1-final.txt`:
- `pack blob == HEAD's blob: True; instruments: {... 'code-review-graph': ('ok', 'fresh'), 'gitnexus': ('ok', 'fresh'), 'graft': ('ok', 'fresh')}`
- `Edit in helper: injected 1173 B; tracked name in context True; UNTRACKED name in context False; untracked path False`
- `line: callers in tracked files (the total is left out): <TRK> scripts/caller_trk.py:4 · __init__ scripts/alpha.py:10`
- `line: tests of the file (code-review-graph) 1: tests/test_trk_t.py:6 test_<TRK>`
- `processes left in the fixture and stopped: 0`

**Tests.**
- `check_untracked_callers` (`tests/test_filepacks.py:1020`):
  - The control: a clean pack's total stands.
  - On Edit and Read, the untracked caller and test canaries are absent, and the tracked ones are present.
  - The left-out line is exact.
  - A caller past the sample, named only in `caller_files`, drops the total.
- `check_same_file_stale` (`tests/test_filepacks.py:1053`).
- `check_caller_path_newline` (`tests/test_filepacks.py:1077`).
- `test_untracked_callers_with_the_post_commit_patch` (`tests/test_filepacks.py:1727`), with params `real` and `untracked-callers-kept`. It ports `probe_callers2.py` through the REAL patched hook:
  - Every graph must read fresh.
  - The pack must name the untracked caller. This guards against a vacuous test.
  - The real code shows neither the untracked name nor its paths. The tracked caller and test are present.
  - The mutant shows the untracked name.
  - No post-commit job may outlive its lock.
- The code map's half: `test_negative_control_the_code_map_without_its_left_out_total` (`tests/test_filepacks.py:1442`).

**Named mutants.** All are killed with their exact messages (section 6):
- `untracked-callers-kept` (`tests/test_filepacks.py:1361`)
- `untracked-tests-kept`
- `callers-total-kept`
- `callers-total-always-dropped` (the control's mutant)
- `caller-files-ignored`
- `same-file-names-from-stale-graphs`
- `stale-gitnexus-total-stands`
- `tracked-newline-unguarded` (`tests/test_filepacks.py:1378`)

### Item 2 (B2): a pack's symbols are tied to its blob

**Code.**
- The blob check comes first: `packs.blob(rel)` (`scripts/filepacks.py:636`).
- Then the code part is withheld, with skip `stale-graph`, when two things hold:
  - the pack holds symbols, or names a source;
  - its source graph is not fresh.
- That clause is `src is not None` (`scripts/filepacks.py:640`).
- The record says `code_skip: stale-graph`.

**(a) sg-untracked, red at the PIN.** Probe `probe_f1b.py`, log `logs/red-b2a-pin.txt`:
- `Edit of the untracked file         injected  587 B; canary in the model's context: True`
- `Read of the untracked file         injected  466 B; canary in the model's context: True`
- `cat of the untracked file          injected  466 B; canary in the model's context: True`

**(a) green.** Log `logs/green-b2a-final.txt`:
- `Edit of the untracked file         injected  243 B; canary in the model's context: False`
- `Read of the untracked file         injected  243 B; canary in the model's context: False`
- `cat of the untracked file          injected  243 B; canary in the model's context: False`
- `records: [[('file:scripts/gamma.py', None, 'stale-graph')], [('file:scripts/gamma.py', None, 'stale-graph')], [('file:scripts/gamma.py', None, 'stale-graph')]]`

**(b) sg-tracked, before.** Probe `probe_f1.py`, log `logs/red-b2b-pin.txt`:
- `Read of alpha.py                   injected 1060 B; canary in the model's context: True`
- `line: symbols: helper L5-6 · Box L9-14 · main L17-18 · leak_<CANARY> L24-25`

**(b) after.** Log `logs/green-b2b-final.txt`:
- `Read of alpha.py                   injected  792 B; canary in the model's context: False`
- `Edit in helper                     injected  792 B; canary in the model's context: False`
- `records: [[('file:scripts/alpha.py', None, 'stale-graph')], [('file:scripts/alpha.py', None, 'stale-graph')], []]`

**Tests.**
- `check_stale_symbol_graph` (`tests/test_filepacks.py:1089`). Its control is a stale graft beside a fresh code-review-graph source.
- `check_sourceless_symbols` (`tests/test_filepacks.py:1113`).
- `test_stale_symbol_graph_with_the_real_code_map_refresh` (`tests/test_filepacks.py:1634`) runs both shapes through the REAL refresh:
  - params `untracked` and `tracked`, crossed with `real` and `stale-symbol-graph-shown`;
  - the real code shows 0 canary bytes and records stale-graph;
  - the mutant shows the canary.

**Named mutants.**
- `stale-symbol-graph-shown`, `symbol-graph-always-graft` and `sourceless-symbols-shown`: all killed.
- "Record why" [V, scratch], log `logs/stale-graph-record-mutant.txt`:
  - `control                        check_stale_symbol_graph PASSED`
  - `stale-graph-recorded-as-blob   check_stale_symbol_graph FAILED: [{... 'code_skip': 'blob', ...}]`

### Item 3 (B3): the post-commit patch passes its own tests once it lands

**Code.**
- `UNPATCHED_AT` = origin 99583a26915d2cbd3a228b9a561864fc81b97487 (`tests/test_filepacks.py:1462`).
- `hook_dir` (`tests/test_filepacks.py:1466`):
  - With the patch: it copies the hook. It runs `git apply` only when `git apply -R --check` says the hook does not carry the patch yet.
  - Without the patch: the bytes come from `git show UNPATCHED_AT:scripts/hooks/post-commit`, never from the working copy. Their blob must start with the patch's `index <pre>..` id.
- CI checks out with fetch-depth 0, so the commit is there.

**Red at the PIN, with the post-commit patch applied.** Log `logs/red-b3-pin.txt`:
- `E           AssertionError: error: patch failed: scripts/hooks/post-commit:172`
- `pytest-summary: 3 failed, 126 deselected in 2.83s`

**Green.** `tests/test_filepacks.py` gives 0 failed both without the patch and with it (section 5; set db64e610236b).

**Unit test.** `test_hook_dir_knows_whether_the_hook_carries_the_patch` (`tests/test_filepacks.py:1603`).

**Named mutants.** Driver `b3mut.py`, log `logs/b3-mutants.txt`. The control ran first in both trees.

| Tree | Mutant | Pasted result |
|---|---|---|
| wt | control | `rc 0 \| 4 passed, 163 deselected in 2.52s \| failed: []` |
| wt | hook-dir-applies-twice | `rc 1 \| 1 failed, 3 passed, 163 deselected in 2.65s` |
| wt | unpatched-from-the-working-copy | `rc 1 \| 1 failed, 3 passed, 163 deselected in 2.74s` |
| wt | pre-image-unchecked | `rc 0 \| 4 passed, 163 deselected in 2.77s \| failed: []` |
| wt-both | control | `rc 0 \| 4 passed, 163 deselected in 2.78s \| failed: []` |
| wt-both | hook-dir-applies-twice | `rc 1 \| 3 failed, 1 passed, 163 deselected in 2.09s` |
| wt-both | unpatched-from-the-working-copy | `rc 1 \| 2 failed, 2 passed, 163 deselected in 3.31s` |
| wt-both | pre-image-unchecked | `rc 0 \| 4 passed, 163 deselected in 2.56s \| failed: []` |

### Item 4: the seven checks

**Code.**
- The first check: `check_blobs_missing` (`tests/test_filepacks.py:1128`).
- The last check's assertion: `not FILES_MAX (64)` (`tests/test_filepacks.py:1172`).
- The first mutant: `blob-fail-open` (`tests/test_filepacks.py:1392`).
- The last mutant: `files-max-off` (`tests/test_filepacks.py:1406`).
- The mutants use the verifier's anchors.
- All 50 checks from the PIN are kept, with unchanged bodies. The test diff removes only the CHECKS dict's closing line and the old `hook_dir` body.

**Red at the PIN.** `mutdrv3.py` ran its control first: 60 lines, all `PASS`. Then with `VK_BUILDER_ONLY=1` (log `logs/red-mut7-pin.txt`), each of the seven printed `SURVIVED all 50 checks`:
- `blob-fail-open`
- `grep-long-value-dropped`
- `grep-attached-ignored`
- `frame-close-any`
- `dq-sub-not-opened`
- `grep-double-dash-dropped`
- `files-max-off`

**After, builder checks only.** Log `logs/vmut-seven-builderonly-final.txt`:
- `blob-fail-open                       KILLED by blobs-missing assert: a code part went out with no BLOBS.txt`
- `grep-long-value-dropped              KILLED by grep-long-value assert: a long option's value was taken as the pattern`
- `grep-attached-ignored                KILLED by grep-attached assert: an attached short value swallowed the pattern: []`
- `frame-close-any                      KILLED by script-paren assert: a ) inside a nested script broke the frame scan: []`
- `dq-sub-not-opened                    KILLED by dq-substitution assert: a cd inside a double-quoted $( ) leaked out`
- `grep-double-dash-dropped             KILLED by grep-double-dash assert: grep -- lost its files or read its pattern: []`
- `files-max-off                        KILLED by files-max assert: a command line gave 120 paths, not FILES_MAX (64)`
- `pack-not-handed                      KILLED by untracked-callers assert: an untracked test reached the model`

### Item 5: the stale documents

- The design line now says what is built and what is not:
  - Built: L2b and P2, in `scripts/filepacks.py`. They are not registered, VERIFY-K2 R2 found them NOT-READY, and round 3 repairs them.
  - Not built: P3.
- The line's first words, `Built since`, are at `docs/research/findings/jev-trim/D105-DESIGN-v1.md:281`.
- Two dated blockquote notes read "Note (2026-09-29 18:5xZ, K2 round 3): falsified":
  - under the F1 line: `found untracked text past the blob` (`tasks/briefs/jev-trim/K2-R2-report.md:9`);
  - under self-attack 1: `a match proves only that the` (`tasks/briefs/jev-trim/K2-R2-report.md:313`).
- The round-2 text is unchanged: 7 lines added, 0 removed.

### Item 6: both patches apply and prove out

- Both patches are unchanged:
  - `tasks/briefs/jev-trim/K2-post-commit.patch`: 26 lines, sha256 71ba4c2c0cec81ab.
  - `tasks/briefs/jev-trim/K2-registration.patch`: 224 lines, sha256 3e8b979120d0638a.
- Round 3 touches none of the three files that `LS-B10-registration.patch` changes.
- `wt-both` is the PIN plus `K2-R3.patch` plus both patches.
  - My five files there diff to f6f480b3… again.
  - The patched hook's sha256 is fce110fe82d8b183, the same as in the verifier's wtreg.
- `git apply --cached --check` of `K2-R3.patch` [V]:
  - rc 0 on a pristine index of the PIN.
  - rc 0 on the current shared HEAD 3a3d45a. Its boundary files equal the PIN's: `git diff --stat 99583a2 3a3d45a` over them is empty.
- Both older patches also give rc 0 on 3a3d45a.
- `git diff --check` is clean.

## 5. Gates

How the counts were taken:
- Counts are pasted from `scripts/test_summary.sh`.
- `--basetemp` is an argument, under my scratch and outside every work tree.
- Set ids come from `bash scripts/pc_suite.sh set-id -- <files>`.

| Gate | Tree | Set id | Run A | Run B |
|---|---|---|---|---|
| `tests/test_filepacks.py` | wt | db64e610236b | `167 passed in 247.24s (0:04:07)` | `167 passed in 241.78s (0:04:01)` |
| `tests/test_codemap.py tests/test_system1_context.py` | wt | 395f8af3a0ce | `197 passed in 423.54s (0:07:03)` | `197 passed in 398.87s (0:06:38)` |
| `tests/test_filepacks.py` | wt-fresh (PIN + `git apply K2-R3.patch`) | db64e610236b | `167 passed in 246.00s (0:04:05)` | |
| `tests/test_codemap.py tests/test_system1_context.py` | wt-fresh | 395f8af3a0ce | `197 passed in 375.24s (0:06:15)` | |
| `tests/test_filepacks.py` (B3: 0 failed) | wt-both | db64e610236b | `167 passed in 237.23s (0:03:57)` | `167 passed in 225.49s (0:03:45)` |
| `tests/test_session_hooks.py tests/test_search_intercept.py` | wt-both | 2415789b9582 | `137 passed in 69.67s (0:01:09)` | `137 passed in 61.49s (0:01:01)` |
| `tests/test_vendored_manifest.py -k test_committed_manifest_matches_fresh_generation`, manifest as committed | wt-both | 21e700b8344c | `1 failed, 56 deselected in 2.35s` | `1 failed, 56 deselected in 2.68s` |
| the same, after `vendored_manifest.py --write` | wt-both | 21e700b8344c | `1 passed, 56 deselected in 2.25s` | `1 passed, 56 deselected in 3.44s` |

- Every row reads `pytest-exit: 0`, except the committed-manifest row, which reads `pytest-exit: 1`.
- Before run B, I restored the committed manifest from HEAD in wt-both.
- `python3 scripts/vendored_manifest.py --check`, with the registration patch applied, gave rc 1 both times, as the brief expected:
  `FAIL: vendored manifest drift: line 20: committed='| `.claude/ (kit-adapted)` | … | 17 | 0 | `439569a82576e716cb655b52dee9987dcdef3876800a452b54209c292e8f5583` |'; generated='| `.claude/ (kit-adapted)` | … | 17 | 0 | `35c61973a4aa70c19037ac660001ca98e50d1ee2eda19bf01896c74087d6a172` |'`
- `--write` printed `WROTE sandbox-kit/VENDORED-MANIFEST.md (10 roots)`. After it, `--check` prints `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 10 vendored roots`.
- The row hash is the same without `.claude/hooks/__pycache__`.
- In wt-fresh (no registration patch), `--check` passes with rc 0.
- The combined 3-file set 804c19143d13 is the first two rows together: 167 + 197 = 364 tests per run. It ran twice in wt and once in wt-fresh.

## 6. Mutation

All runs are on the final bytes. Each driver's control ran first, and I checked that the basetemp parent exists before counting a kill (AF-AP-223).

**Own table (rounds 1 to 3).**
- 70 mutants at the PIN, 88 now.
- Control, `-k check_passes`: `pytest-summary: 62 passed, 105 deselected in 43.58s`.
- Mutants, `-k "negative_control or every_"`: `pytest-summary: 91 passed, 76 deselected in 89.40s (0:01:29)`.
- The 91 are the 88 mutants (each killed by its named check, with its exact message), the code-map control, the hook control and the table-completeness test.

**The verifier's `mutdrv3.py` (57 mutants).** Control: 72 of 72 `PASS`. Logs: `logs/vmut-*-final.txt`.
- r1: 27 of 31 killed. The survivors are build-file-kept, clean-keeps-links, cd-dash-followed and commit-dedupe-dropped, the verifier's own equivalents.
- m2: 10 of 11 killed. The survivor is blobs-not-kept, which is equivalent.
- m3: 13 of 15 killed. The survivors are blob-field-optional and blob-kind-any, both INFO in the verifier's report.
- pack-not-handed is now killed.

**New mutants per clause of items 1 to 3.**
- Item 1: 8 in the table, plus the code-map control.
- Item 2: 3 in the table, plus `stale-graph-recorded-as-blob` (scratch).
- Item 3: 3 in `b3mut.py`. 2 are killed, and 1 is equivalent.

## 7. Files

Final bytes in the worktree: lines and sha256.

| File | Lines (PIN → now) | sha256 | Diff |
|---|---|---|---|
| `scripts/filepacks.py` | 1179 → 1219 | 18c8360473ba0b6dc867e1ae0a259e83198c893cabbe7851c1f8624c1c5de62c | +45 -5 |
| `scripts/codemap.py` | 1153 → 1156 | 8be917715cd2a5c9973d495f44f725e6df8322e7cf99d0ff4ecaeb0b8dd92ba3 | +5 -2 |
| `tests/test_filepacks.py` | 1366 → 1836 | 3857536f23325e5d97108814b42fad725f9c1e6858a27608dd7bd6403e563024 | +478 -8 |
| `docs/research/findings/jev-trim/D105-DESIGN-v1.md` | 406 → 408 | 95351f65dca39008ae11dfbd57f1fd34fe4abb2d2e4645a782f73ebb1970408e | +4 -2 |
| `tasks/briefs/jev-trim/K2-R2-report.md` | 330 → 337 | 77e21ff1115a94459b36440b30d65f55804cce3a73c8f73409e6a4275a2ce8b7 | +7 -0 |
| `tests/test_codemap.py` | 943, unchanged | 76e31571e8008a4d… | none |
| `tasks/briefs/jev-trim/K2-R3.patch` (shared tree, untracked) | 695 | f6f480b38272e0bcd29f224d2aa81b60224a201e670ac11850c130a5f2e61d3b | the deliverable |

The AP screen over the three code files, compared with the PIN. All the new hits are in tests and are there by design. None is in production code.
- AF-AP-175, 13 → 16: a test's `git rev-parse HEAD` in a private fixture repo.
  - `at = git(repo, "rev-parse", "HEAD")` (`tests/test_filepacks.py:1654`)
  - `head = git(repo, "rev-parse", "HEAD")` (`tests/test_filepacks.py:1757`)
  - `git(repo, "rev-parse", "HEAD:scripts/alpha.py")` (`tests/test_filepacks.py:1762`)
- AF-AP-40, 7 → 8: the log reader of `wait_post_commit`, which fails closed at its deadline. `if p.exists() else ""` (`tests/test_filepacks.py:1700`).
- AF-AP-115, 2 → 4: `shutil.which` for the test tools.
  - `GITNEXUS = shutil.which("gitnexus")` (`tests/test_filepacks.py:1598`)
  - `CRG = shutil.which("code-review-graph")` (`tests/test_filepacks.py:1600`)

## 8. Self-attack: how could untracked text still reach the model?

**Still open:**
- [V] Uncommitted text in a tracked caller or test file (NOT done 1). This is the one proven channel left.
- [I] The risk line's `impacted` and `direct` counts (NOT done 2). These are numbers only.
- [I, not probed] Three more:
  - instrument error text rendered verbatim (NOT done 8);
  - the builder's stamp-then-read window (NOT done 7);
  - a caller file untracked after the last build (NOT done 9).

**Closed.** Each has a committed test and a killed mutant:
- untracked caller and test names and paths (B1: `untracked-callers`, and the real-hook test);
- a callers total that counts an unseen caller (`callers-total-kept`, `caller-files-ignored`);
- symbols from a stale graph, in both shapes (B2: `stale-symbol-graph`, and the real-refresh test);
- symbols with no source graph (`sourceless-symbols`);
- a stale graph's names from the file itself (`same-file-stale`);
- a caller path that holds a newline (`caller-path-newline`);
- a file untracked since the build (round 2's blob check);
- no BLOBS.txt (`blobs-missing`);
- a reader re-reading the unfiltered pack from disk (`pack-not-handed`, now killed).

**The three most likely ways this change is wrong, and how I ruled each out:**
1. **It hides legitimate callers.**
   - The clean-pack control in `untracked-callers` kills `callers-total-always-dropped`.
   - The real-hook test and green-b1 show the tracked caller and test.
   - On the live code map, 6 of 233 packs would lose a total. All 6 come from the stale TRACKED.txt of round 1's build (DISCREPANCY 11).
2. **The B2 clause blanks the live code map.**
   - A read-only count over the live packs: the clause would withhold 0 of 233.
   - The 197 codemap and System-1 tests pass.
3. **`hook_dir` misdetects the patch.**
   - The unit test rules it out, and so do two killed mutants in both trees.
   - The filepacks file passes twice in each tree.
   - The one survivor, `pre-image-unchecked`, is equivalent (NOT done 4).

## 9. Hygiene

- **Shared tree:**
  - My only git writes there were worktree add and remove, with hooks off.
  - Its only file from me is `tasks/briefs/jev-trim/K2-R3.patch`.
- **Rules kept:** no PC bridge, no outward action, no subagent, no secret file read. I never registered the hook.
- **Never written:** `/home/user/.claude/settings.json`, the shared tree's `.claude/` and `scripts/hooks/`, and the live `.jev/`. I only read the live code map.
- **Reboots:** none voided a run. The VM booted at 14:36:27Z (`uptime -s`), before this round began at 18:1xZ.
- **S1 injections:** none reached me after the resume.
- **Report lint:** `scripts/report_lint.py` ran over this report with `--root` set to the worktree that held the final bytes (before I removed it) and `--min-refs 20`. rc 0:
  `report_lint: 43 refs — OK 42, NEAR 0, MISS 0, UNCHECKABLE 1, UNRESOLVED 0 (worktree)`.
  The one UNCHECKABLE is the pasted PIN error line (`scripts/hooks/post-commit:172` inside pytest's output).
- **Worktrees:** wt, wt-fresh and wt-both are removed with `git worktree remove --force`, hooks off, rc 0 each. None is left in `git worktree list`.
- **Scratch:** the basetemps are deleted.
- **Processes:**
  - No process of mine remains, and no `graft _update-check` child.
  - Each real-instrument test ends by killing its fixture's processes by pid.
  - Every probe log ends with `processes left in the fixture and stopped: 0`.
  - The post-commit jobs running in the shared tree at 20:0xZ are not mine. They belong to the coordinator's commit 3a3d45a ("pc_egress_watch.sh: watch a PC lane's network peers from outside the lane").
