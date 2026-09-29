> **Coordinator note (2026-09-29 23:0xZ, at harvest).** The resumed round-2 verifier's round-3 hand-back, saved as
> the transcript holds it (agent a5f4b238ed9d44435; served wholly by claude-opus-5-5, 0 refusal stops).
> Recommendation NOT-READY on R3-1. A fourth K2 round is past D-111's third: the owner decides. The follow-ups go
> on issue #83 (D-108 item 2).

## Round 3

Written 2026-09-29 from `Tue Sep 29 22:58:02 UTC 2026` (date -u).

**Recommendation: NOT-READY on one blocker, R3-1.** I reproduced every piece of evidence it rests on through the real patched hook. B1 is closed in the steady state, and B2 and B3 are closed as the brief specifies. But a caller's name from a file's untracked era still reaches the model after that file is committed with other text. When the caller file is outside the code-map refresh paths, the leak persists: no refresh follows its commit. I reproduced that twice. Inside those paths it lasts from the fast file-pack build to the slow refresh (live median wait 92 s), also reproduced twice. D-034: "A boundary hole that puts untracked text in front of the model counts as core-blocking."

Scratch: `S3=/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r3`. Tags: [R] reproduced, [S] static, [I] inferred.

### 1. Premise
- I ran `bash scripts/premise_block.sh` from the main tree at 21:37Z.
- Output is identical to the brief's block: 8 commands, and both texts hash to `cc59ac6a89049266` (`$S3/premise_expected.txt`, `$S3/premise_actual.txt`). No CONTRACT-INVALID.

### 2. Gates at the PIN (my worktree `$S3/wt`, detached at a9e5389)
- `--basetemp` was a pytest argument under `$S3/bt/<name>`, outside every work tree. Each call took under 10 minutes.
- Counts are pasted from `test_summary.sh`. Every run has `pytest-exit: 0`.

| Set | Run | Result |
|---|---|---|
| `1 files set=db64e610236b` (`tests/test_filepacks.py`) | A | `pytest-summary: 167 passed in 246.56s (0:04:06)` |
| same file | B | `pytest-summary: 167 passed in 253.70s (0:04:13)` (the run-B log holds no set line; same single file) |
| `2 files set=395f8af3a0ce` (`tests/test_codemap.py tests/test_system1_context.py`) | once | `pytest-summary: 197 passed in 382.83s (0:06:22)` |

- These match the coordinator's landing counts (167 and 197).

### 3. The scope items

**Item 2: B1 through the real patched hook.**
- **Literal re-run [R].** `$S2/probe_callers2.py` at the PIN (22:42Z, `logs/b1-probe_callers2.txt`):
  - The untracked name and path are absent on Edit and Read. The tracked caller and test are present (the control). No process was left.
  - Edit line: `callers in tracked files (the total is left out): <TRK> scripts/caller_trk.py:4 · __init__ scripts/alpha.py:10`.
- **Successor probe [R].** `probe_r3.py b1-real` gives the same result on Edit, Read and `cat`. The pack itself still names the untracked caller, so the reader's filter is what removes it.
- **Filter-removed control [R].** `b1-nofilter` shows `callers 5 (2 in tests): <UNT> scripts/<CALLER_NEW>:4 …`, so the probe can see a leak.
- **Exact-line match [R].** A mutant that swaps it for a substring match (`r3-listed-substring`) survives all 62 of the builder's checks. My check `n4_listed_substring` kills it: an untracked caller path `beta.py` is the tail of the tracked `scripts/beta.py`.
- **Newline and NUL guard.** The newline guard is load-bearing (builder check `caller-path-newline`). The NUL guard is redundant [S]: TRACKED.txt is split on NUL, so a path holding NUL cannot match.
- **NOT done 9 [R]** (`logs/nd9.txt`): it leaks only while the file-pack build is stalled.
  - Setup: a caller file untracked by commit c2, then given a new function `<U9>`, with c2's build queued behind a held lock.
  - Edit shows `callers 3: <TRK> scripts/caller_trk.py:4 · <U9> scripts/caller_trk.py:8 · __init__ …`. It is gone once the build runs.
  - In the natural order the build (sub-second) finishes before the refresh (16 s or more).
  - This is shape (c) of R3-1.
- **DISCREPANCY 1 [R]:** whenever the filter removes a sampled caller or cannot vouch for one, the total is dropped and never recounted (b1-real, nd1, samefile). Mutant grading is in item 6.
- **DISCREPANCY 2 [R]:** tested through the real refresh (`logs/samefile*.txt`).
  - Real code: `callers in tracked files (the total is left out): none shown`, 0 leak bytes.
  - Builder's mutant `same-file-names-from-stale-graphs`: `<LEAK> scripts/gamma.py:5` shown.
  - code-review-graph records `not-indexed` for the untracked file. So code-review-graph does not index untracked files, and the tests channel carries no untracked-era names.
- **New shape of this item:** R3-1 below.

**Item 3: NOT done 1, re-derived [R]** (`logs/nd1.txt`, real hook, all graphs fresh).
- Edit shows `callers in tracked files (the total is left out): <TRK> scripts/caller_trk.py:4 · <UNC> scripts/caller_trk.py:8`.
- Edit, Read and `cat` show `tests of the file (code-review-graph) 2: … test_<TRK> · tests/test_trk_t.py:10 test_<UNC>`. This confirms the builder's [I] on test names.
- **Grade under D-034: FOLLOW-UP stands.**
  - The files are tracked: in HEAD at the build, and listed in TRACKED.txt. That is the stated boundary.
  - D-034's core-blocking clause names untracked text.
  - The names are in the file's current working bytes, the same bytes a Read of that tracked file returns.
  - Only identifiers and line numbers reach the model.
- Contrast R3-1: its name is in no commit and in no current bytes.
- R3-1's fix (a per-file blob tie) closes NOT done 1 as well.

**Item 4: B2 [R].**
- sg-untracked (`logs/b2-sg-untracked.txt`): 0 canary bytes on Edit, Read and `cat` (231 B each). All three records say `stale-graph`.
- sg-tracked (`logs/b2-sg-tracked.txt`): 0 canary bytes on Read and Edit, both `stale-graph`.
  - Its `cat` leg injected 0 B: the same-window de-dup stopped it, and its record is `[]`. So that leg did not exercise `cat`. sg-untracked's `cat` leg did.
- The builder's parametrized real-refresh test and its mutant control passed inside my gate.
- **The clause:**
  - `r3-clause-not-indexed-passes` lets `not-indexed` pass. It survives the builder's checks and is killed by `n4_not_indexed`.
  - The builder's `sourceless-symbols` check and its table mutants passed in the gate. I wrote no extra mutant for it.
- **NOT done 7, measured [R]:**
  - Window (`logs/nd7-window.txt`, strace, 7 real `codemap.py build` runs), from the stamp's fingerprint read to the skeleton's first index open: min 1039.8, median 1194.9, max 1302.5 ms. Stamp to exec takes 7 to 10 ms; the rest is graft start-up. strace inflates the numbers.
  - Forced interleaving (`probe_nd7.py race`): a graft PATH shim re-indexes a canary inside the window; everything else is production.
  - The pack reads graft `fresh`, its blob equals BLOBS.txt's, and the canary is shown.
    - Tracked shape: on Read (`symbols: … leak_<CANARY> L24-25`).
    - Untracked shape with a stale TRACKED.txt: on Read and on Edit (`def leak_<CANARY>(token="<CANARY>-arg")`).
  - Two leftover graft children were stopped by pid in each race run.
  - Rating: FOLLOW-UP (finding 3).

**Item 5: B3 closed [R].**
- 0 failed without the post-commit patch (`$S3/wt`: 167 passed, twice).
- 0 failed with both patches applied (`$S3/wtboth`: `1 files set=db64e610236b` `pytest-summary: 167 passed in 236.77s (0:03:56)`).
- The negative control reads the hook at the fixed commit `UNPATCHED_AT` 99583a2.
- A mutant that makes the unpatched hook come from the working copy is killed in wtboth: `pytest-summary: 2 failed, 2 passed, 163 deselected in 2.94s`.
  - The two failing tests: `test_negative_control_the_hook_without_the_patch_runs_no_build` (the pre-image assertion fires) and `test_hook_dir_knows_whether_the_hook_carries_the_patch`.
  - I restored the file byte-identical.

**Item 6: mutants.**
- **mutdrv3.py** (my 57 mutants against 72 checks, `logs/mut-*.txt`):
  - Control: 72/72 PASS.
  - r1: 27/31 killed. Survivors: the four round-2 equivalents.
  - m2: 10/11 killed. Survivor: `blobs-not-kept`, equivalent.
  - m3: 13/15 killed. Survivors: `blob-field-optional` and `blob-kind-any`, both INFO in round 2.
  - `pack-not-handed` is now killed by `untracked-callers`.
  - The builder's report states exactly these numbers: **reproduced**.
- **Builder-only regrade:** the seven ported checks plus `pack-not-handed` are all killed by the builder's own checks.
- **`pre-image-unchecked` is NOT equivalent [R]** (`preimage_killer.py`, `logs/preimage-killer.txt`).
  - Set `UNPATCHED_AT` to 283faf0 ("INSTALL1 landed …"). Its hook blob is 2efcc7c, not the pre-image 09b3b0b.
  - The real `hook_dir` refuses it ("the hook at UNPATCHED_AT is not the patch's pre-image 09b3b0b: 2efcc7c"). The mutant accepts it.
- **New mutants** (`mutdrv4.py`, 9, one per clause).
  - On the builder's 62 checks, **8 survive**:

    | Mutant | What it changes |
    |---|---|
    | `r3-listed-substring` | substring match on TRACKED.txt |
    | `r3-tests-by-gitnexus` | tests filtered by GitNexus freshness |
    | `r3-callers-by-crg` | callers filtered by code-review-graph freshness |
    | `r3-keep-rel-any-graph` | same-file names kept if any graph is fresh |
    | `r3-fresh-unless-stale` | `not-indexed` counts as fresh |
    | `r3-clause-not-indexed-passes` | the clause lets `not-indexed` pass |
    | `r3-files-not-list-ok` | a missing `caller_files` vouches for the total |
    | `r3-sample-shrink-ignored` | a shrunk sample keeps the total |

  - Only `r3-tests-rel-unfiltered` is killed (by `same-file-stale`).
  - My four n4 checks all pass on the real code (control 4/4 PASS): `n4_listed_substring`, `n4_tests_graph`, `n4_not_indexed`, `n4_caller_files_missing`. Adding them kills 7 more.
  - `r3-sample-shrink-ignored` survives all 76 checks. It is equivalent on packs the builder writes [S]: the sample's files are a subset of `caller_files` plus rel.

**Item 7: stale documents [R].**
- In a9e5389, `tasks/briefs/jev-trim/K2-R2-report.md` is +7/−0: two dated notes ("Note (2026-09-29 18:5xZ, K2 round 3): falsified …"). The round-2 record is annotated, not rewritten.
- `D105-DESIGN-v1.md` is +4/−2: the "Not built" line is corrected with a dated note.
- `VERIFY-K2-R2-report.md` is unchanged.
- `K2-R3-report.md` exists at the PIN, so the builder's DISCREPANCY 7 is resolved.

**Item 8: the two patches [R].**
- Both apply cleanly at the PIN. The patched hook's sha256 is `fce110fe82d8b183`, the same as round 2.
- `2 files set=2415789b9582` (`tests/test_session_hooks.py tests/test_search_intercept.py`): `pytest-summary: 137 passed in 66.43s (0:01:06)`.
- Manifest:
  - `--check` gives rc 1 before regeneration.
  - `--write`, with `.claude/hooks/__pycache__` moved aside, rewrites the manifest. The CLASSES tsv is unchanged.
  - `--check` then prints `PASS: … matches 10 vendored roots`.
  - The `.claude/` row moves from `1b8b079d3cb8209a…` at the PIN to `065729626735df19…`.
  - `1 files set=21e700b8344c` (`-k test_committed_manifest_matches_fresh_generation`): `pytest-summary: 1 passed, 56 deselected in 2.66s`.
  - The builder's row hashes (439569a8… to 35c61973…) come from an earlier base.
- **Conflict with LS-B10: yes.** Each patch applies alone at the PIN.
  - LS-B10 on top of K2 fails in `.claude/settings.json:44`, `scripts/install_session_hooks.py:1` and `tests/test_session_hooks.py:1`.
  - K2's registration on top of LS-B10 fails in the last two. K2-post-commit.patch applies either way.
  - The count assertions also disagree:
    - K2: installed 9, 12 commands, 13 total, 9 others.
    - LS-B10: installed 13, 13 commands, 14 total.

**Item 9:** section 2. **Item 10:** section 6. **Item 11:** section 5.

### 4. Finding inventory (no severity filter)

**R3-1. BLOCKER. A caller's name from a file's untracked era reaches the model once the file is tracked.** [R, 4 runs in 2 shapes, real patched hook]
- **Mechanism, from primary source:**
  - `_tracked_only` (`scripts/filepacks.py:571`) keeps a caller when its path is a TRACKED.txt line. TRACKED.txt is the build's `ls-tree` path list (`:1000-1001`, `:1078`).
  - It keeps the total when GitNexus is `fresh` and every `caller_files` entry is listed.
  - The pack's GitNexus `fresh` is `_fresh(indexed, sha)` for the callee file rel only (`scripts/codemap.py:452-454`). Nothing records which bytes of a caller file the graph indexed.
  - The file-pack build runs at every commit, so TRACKED.txt lists a newly committed file at once.
  - The callee's pack is rebuilt only by a refresh that reaches it: the hook's `cm_paths` are scripts/, src/, proofs/, spikes/, harness-ports/ and tests/*.py, plus `widen` (`codemap.py:760`).
- **Shape (a), persistent** (`probe_r3.py late-outside`, `logs/late-outside.txt`, `late-outside-2.txt`):
  1. `tools/caller_x.py` is untracked; its `early_<hex>` calls `helper`.
  2. Commit c1 changes `scripts/alpha.py`. The rebuilt pack names `early_<hex>`, which stays hidden while the file is untracked (the control).
  3. I rewrote the file with `later_<hex>` and committed it as c2. The refresh log says `codemap refresh none: no changed path under scripts/, …`.
  4. Result: Edit in `helper` shows `callers 2: <EARLY> tools/<CALLER_X>:6 · __init__ scripts/alpha.py:10`. It shows after every hook job ended, again 30 s later, and after an unrelated in-scope commit c3 (whose refresh built 1 pack, not alpha's). Twice.
  - `early_<hex>` is in no commit and not in the current bytes.
  - Live, read-only: 2 of 234 packs name a caller file outside the refresh paths (both under `docs/`), so the class is populated.
  - The live map holds no instance today. 0 kept names are absent from their file's HEAD bytes; the 109 unmatched kept entries are all `<module>`.
- **Shape (b), a window** (`late-track`, `logs/late-track*.txt`): the same flow with `scripts/caller_x.py`.
  - c2's build finished after 0.31 s and 0.10 s. The refresh was still running at 0.79 s and 0.33 s.
  - Edit shows `callers 2: <EARLY> scripts/<CALLER_X>:4 · __init__ scripts/alpha.py:10`. After the refresh (about 20 s) it shows `<LATER>`. Twice.
  - Live size: `/tmp/codemap-refresh.log` shows 64 refreshes that waited min 0, median 92, p90 279, max 546 s for the graphs. The window is at least that wait.
- **Shape (c):** NOT done 9 with a stalled build (item 2).
- **[S, UNVERIFIED]:** `WIDEN_CAP = 20` (`codemap.py:755`, `:789-791`) leaves callee packs past the cap stale after a refresh. It never bound live: the largest widening was 5 in 64 refreshes.
- **Contract:** brief item 2 (the caller filter; NOT done 9's shape) and item 11 (D-034). It is round 2's B1 content class.
- **Canonical path:** yes.
- **Material effect:** an identifier, and a total that counts it, from bytes no commit holds reaches the model on Edit. In shape (a) it persists until the callee's pack is next rebuilt.
- **Discriminator:** `VK2_WT=<worktree at a9e5389> python3 $S3/probe_r3.py $S3 late-outside` is deterministic: it waits for every hook job to end. The in-run controls hide the name while the file is untracked, and shape (b) shows `<LATER>` after the refresh.
- **Ownership:** `scripts/codemap.py` and `scripts/filepacks.py`, both K2 premise files.
- **Fix:** the builder's own NOT done 1 direction.
  - At build time, record per caller file and per test file the graph's indexed hash and the file's committed blob.
  - The reader keeps a name only when that blob equals BLOBS.txt's blob for the file and the indexed hash matches it.
  - A file untracked at the build gets no blob, so its names never show from that pack.
  - This closes shapes (a) to (c) and NOT done 1.
  - Add committed real-hook tests: shape (a), and shape (b) with the refresh held behind its lock, each with a leak control.

**2. FOLLOW-UP. NOT done 1.** The rating stands (item 3). [R]
- Mapping: D-034 names untracked text; this text is in files the repo tracks.
- Effect: identifiers from tracked working bytes.
- Fix: R3-1's fix closes it.

**3. FOLLOW-UP. NOT done 7, the stamp-then-read race.** [R, forced]
- The window is about 1.0 to 1.3 s.
- Natural content is the model's own uncommitted edit of a tracked file (item 3's class). The untracked shape also needs a stale TRACKED.txt, that is, a stalled build.
- Fix: stamp again after the skeleton read. Mark the graph stale if the fingerprint moved.

**4. FOLLOW-UP. Test gaps in round 3's clauses.** [R] The 8 surviving mutants are listed in item 6. The real code is right on each. Port the four n4 checks from `$S3/mutdrv4.py`.

**5. FOLLOW-UP. `pre-image-unchecked` has a killer.** [R] Add a check that a wrong `UNPATCHED_AT` is refused (item 6).

**6. FOLLOW-UP (coordination). The two registration patches conflict** in three files, and their count assertions disagree (item 8). Rebase whichever lands second, counts included.

**7. INFO.** B1 steady state, B2 and B3 are closed as specified (items 2, 4, 5). [R]

**8. INFO.** DISCREPANCIES 1 and 2 verified. [R]

**9. INFO.** The builder's mutation claims are reproduced exactly. Its own 88-mutant table passed inside my 167-test gates. [R]

**10. INFO.** The manifest row must be re-derived at landing. At the PIN it moves 1b8b079d… to 06572962… (item 8). [R]

**11. INFO.** NOT done 2: the risk line counts untracked dependants, as numbers only (b1-real: `3 impacted within 3 hops`). [R]

**12. INFO.** The NUL guard in `listed` is redundant. [S]

**13. INFO. Live read-only scan** (live HEAD 3f18bc0, 234 packs, no BLOBS.txt).
- The clause withholds 0 packs. 8 packs lose a total.
- 279 sampled callers are dropped:
  - 275 are same-file callers. The cause is a non-fresh GitNexus graph, or a rel missing from the stale TRACKED.txt of round 1's 7db59b9 build; I did not split the two.
  - 4 are cross-file callers in files tracked now but absent from that TRACKED.txt (the builder's 4).
- The builder's "17 not fresh" equals my 5 stale plus 12 not-indexed.
- Today every code part is withheld anyway, because there is no BLOBS.txt.

**14. INFO.** `UNPATCHED_AT` needs full history. CI uses fetch-depth 0, and the shared clone is not shallow. [R]

**15. INFO.** Every fixture pack records `ap_screen` status `error`. I did not investigate; it has no bearing on the probes.

**16. INFO.** NOT done 8 was not probed. It needs a GitNexus error text that names an untracked path, and I found no bounded way to cause one.

### 5. Blocking predicate and recommendation
- R3-1 meets all five conditions:
  1. Contract: items 2 and 11 (D-034).
  2. Canonical path: the real hook, graphs, refresh, build and wrapper at the PIN.
  3. Material effect: untracked-only text in the model's context, persistent in shape (a).
  4. Discriminator: the deterministic probe with in-run controls.
  5. Ownership: K2's two files.
- It is inside the contract, so it is a BLOCKER, not a CONTRACT-DEFECT.
- Findings 2 to 6 fail condition 1 or 3: tracked-file text, a race that needs a stalled build for its untracked shape, test gaps, or coordination.
- **Gate recommendation: `NOT-READY` on R3-1.** It depends on nothing I did not reproduce. The live population count and the WIDEN_CAP path are supporting evidence only.

### 6. What must hold before registration (round 3's bytes)
1. R3-1 is closed by a per-file blob tie for caller and test names, with committed real-hook tests for shapes (a) and (b) and a leak control each.
2. The four n4 checks and a wrong-`UNPATCHED_AT` check are ported.
3. `K2-post-commit.patch` lands with or before the registration.
4. One build at HEAD writes BLOBS.txt before any session loads the hook.
5. The patched installer lands only with the owner's yes: `setup.sh:438` registers hooks at every session start.
6. The manifest is regenerated at the landing base, with ignored output under `.claude/` set aside.
7. Whichever registration patch lands second is rebased, with its counts recomputed.
8. The patched tree passes these gates: `db64e610236b` twice, `395f8af3a0ce`, `2415789b9582` and `21e700b8344c`.
9. The owner accepts the issue-#83 findings (5, 6, 7, 9, 12, 15) as known gaps.
10. Optional: stamp again after the read (finding 3).

### 7. Reproduced, static, skipped
- **Reproduced:** everything tagged [R] above.
- **Static:** the WIDEN_CAP path, the NUL-guard redundancy, and the equivalence of `r3-sample-shrink-ignored`.
- **Skipped:**
  - NOT done 8 (reason in finding 16).
  - A scratch fix for R3-1: it is the builder's job, and the predicate does not need one.
  - The PC: the rules forbid the bridge.
  - The issue-#83 findings: out of scope.

### 8. Files and hygiene
- **Probes:** `$S3/probe_r3.py` (modes b1-real, b1-nofilter, nd1, nd9, late-track, late-outside, samefile, samefile-mut), `$S3/probe_nd7.py`, `$S3/mutdrv4.py`, `$S3/preimage_killer.py`, `$S3/live_scan.py`, `live_scan2.py`, `live_scan2b.py`, `live_scan3.py`.
- **Logs:** `$S3/logs/` (34 files). Notes: `$S3/PROGRESS.md`.
- **Cleanup:**
  - `$S3/wt` and `$S3/wtboth` removed with `worktree remove --force`, hooks off; `wtls` was removed earlier. `git worktree list` shows none under vk2r3.
  - 0 processes have a cwd under `$S3`.
- **Rules held:**
  - No git write in the shared tree. Its 3 untracked paths belong to the LS-B11 and SCRUB2 lanes.
  - The hook is registered nowhere: `grep -c filepacks` gives 0 in all three settings and installer files, rechecked at 22:5xZ.
  - I read no secret file.
  - The live `.jev/codemap` and `/tmp/codemap-refresh.log` were read only.
  - A scan of my 128 round-3 Bash calls finds no top-level `cd` and no `pkill -f`.
- **Slips:**
  - Three PROGRESS.md stamps (22:27Z to 22:31Z) were typed ahead of the clock by up to about 4 minutes. A 22:32Z note corrects them; every later stamp comes from `date -u`.
  - I re-ran the literal `probe_callers2.py` late (22:42Z). The earlier B1 evidence came from its successor, and the two agree.