> Coordinator note (2026-09-29 06:0xZ): the report of record, extracted by `scripts/stack.py harvest` (run s-20260929T060432Z-14a6de). Served model: claude-opus-5-5 on all 1,128 assistant records of this lane (its four rounds), 0 refusal stops, 6 tool-error clusters, 2 compactions. `report_lint`: 0 refs. Local ids: none cited (the ids it names, 81ef2a9, aa85f5e and 7db59b9, were origin ids when written; aa85f5e is the retro commit's origin id as the lane read it). The two code files' sha256 prefixes match the report. Landed GATED-PENDING-VERIFY; the VERIFY-K1 verifier is resumed for round 2.

# K1 round 2 (T0-REPLAY round 4, task #352, D-106): report

This is the builder's report. There is no recommendation in it.

## Answer first

- **Status: all 10 items done.** The v2 outputs are in `docs/research/findings/jev-trim/compaction-2026-09-29-r2/`: 19 files, all written by compaction.py. Nothing is committed (no git writes).
- **Gates:** 99 / 68 / 42 passed, twice each, under Python 3.11.15. Once each under 3.12.3.
- **v1 is byte-identical.** The 19 round-1 files regenerate byte-identical under 3.11.15 and under 3.12.3. `select` has to run over a mirror of the subagent directory that leaves out one file: a new subagent compacted at about 04:55Z (DISCREPANCY 17).
- **Main, 1M class: the corrected re-fetch rate after a compaction.** "Corrected" means K1's shapes with writes out, plus the strict set. Per 100 requests:
  - first 20 requests: 38.07, against 17.51 to 18.52 at the controls. The excess is +19.6 to +20.6 per 100, or +3.9 to +4.1 calls and about +9.2k to +9.6k tokens per boundary. Every 95% interval excludes 0.
  - requests 20 to 99: +2.9 to +3.6 per 100. The lower bounds are 0.15 to 0.85.
  - first 100 requests: +6.0 to +7.1 per 100.
- **My excess is larger than VERIFY-K1's** (+2.5 to +3.3 calls per boundary). The reason is mostly that my control rates are lower (DISCREPANCIES 1 to 8).
- **Cost model.** The position-aware variant reproduces VERIFY-K1's rows exactly when unscaled (589 … 122 compactions). Calibrated to the observed 121 at 785k (scale 0.993736), it gives 586 / 353 / 246 / 186 / 146 / 121.

## Deviations (read these first)

1. **`compaction_loss(tl)` with no shape set applies v2.** R1 and R2 call it that way and must pass as they are (item 2). The CLI `--shapes` default is v1, and so is `run()`'s. A golden test and two mutants hold the v1 default.
2. **"A search shape counts reads only"** is implemented as: count read + script + other; exclude write and commit. This follows the brief's "writes and commits are reported beside it" and VERIFY-K1's "writes out" discriminator. Every search-shape call's direction is in the JSON and the summary (read / script / other / write / commit), so the read-only count can be read off directly.
3. **Direction precedence.** A command takes the first of write > commit > read > script > other that any of its simple commands is. The rules are target-agnostic, as written: a read whose output is redirected into a scratch file counts as a write.
4. **C2 eligibility** (the brief did not state it): a boundary whose pre segment has at least 2×PSEUDO_GAP requests, with the point 100 requests before its end. This reproduces VERIFY-K1's 26 C2 points.
5. **C5 counts whole windows only and has no rest window.** This reproduces VERIFY-K1's 386 points at N=20 and 129 at N=100.
6. **C2's "final outputs" (the tail)** are captured by a wrapper around `replay._segments` during `replay.build`. The wrapper calls the original and returns its segments unchanged. replay.py is not modified on disk. The replay tests pass in the same process, and the v1 bytes are identical.
7. **Position convention.** I switched to VERIFY-K1's: a step (request i's context minus request i−1's) takes position i−1. This reproduces its growth means exactly. My first convention gave 6,265 / 4,315 / 2,853.
8. **Calibration.** The committed position-aware rows use one growth scale, 0.993736, found by bisection so that 785k gives the observed 121. The unscaled count sits beside each row.
9. **History rule is K1's**: the whole pre segment, and for a control, the segment before its point. VERIFY-K1's item-3 table used a matched 100-request history on 104 boundaries, so those numbers are not directly comparable.
10. **Labels are exclusive** (first match in order: K1's shapes, then strict, then loose). VERIFY-K1's "any git log/show/diff" row was inclusive.
11. **One planned mutant was replaced.** `v1-counts-directions` crashed with an AttributeError instead of failing an assertion. Its replacements are `v1-schema-is-2` and `v1-params-take-v2-keys`.
12. **The red tests are pasted verbatim.** Their `;` and one-line `for` statements pass pyflakes, but pycodestyle would flag them (E701/E702).
13. **Size.** compaction.py went from 883 to 2,017 lines; the test file from 525 to 1,079. Items 3 to 8 need it (shell parser, labels, three controls, bootstrap, position model, v2 summary). I flag it anyway.

## NOT done

- **No matched-history variant** and **no C3.** Neither is in the brief.
- **The direction classifier was not checked on a labeled sample of real commands.** It was checked on 21 synthetic commands, plus a histogram of program names for the real exclusions. INFERRED accuracy.
- **Intervals only for main (per class) and the pooled subagents.** Single subagent files show rates only.
- **The tail is counted for C2 only.** Real windows, C1 and C5 keep K1's rule (F8 found it immaterial).
- **The stale context places of F10 are untouched.** D105-DESIGN §10.6, the ledger's K1 entry and the round-1 report are outside my boundary.
- **No commit, no push.**

## Premise re-run

**Before any edit (04:26:54Z to 04:27:29Z, HEAD c74e0fb): every line of the brief's PREMISE block matched.** That was item 1.

**Re-run after the edits, at 05:56:08Z.** The lines that moved are exactly this round's edits:

```
3cd69de-is-an-ancestor-of-HEAD
K1 landed (task #352; GATED-PENDING-VERIFY): what a compaction costs this session; the design's section 10.6
e17cc65651796be0  scripts/jev_trim/compaction.py            (was 95e160625dd2cd10: this round)
1908c684664ed7eb  tests/test_jev_trim_compaction.py         (was fff6fb719740142e: this round)
73a16e72ed933db5  scripts/jev_trim/replay.py                (unchanged)
004df9ff8fd1980e  tasks/briefs/jev-trim/VERIFY-K1-report.md (unchanged)
19                                                           (round-1 dir, unchanged)
19                                                           (r2 dir: now exists, this round)
30                                                           (def test_ count, was 17: this round)
423:/438: the two red-test lines                            (unchanged)
3 files set=74199ac6b13a
209 passed                                                   (was 141: this round's tests)
```

HEAD moved from c74e0fb to 7db59b9 during the round. The three commits are:
- aa85f5e "Retro: AF-AP-240 registered …"
- 81ef2a9 "Retro follow-up: live-state names the retro …"
- 7db59b9 "VERIFY-LS-B9 round 4: the report of record …"

`git diff --stat c74e0fb HEAD` over scripts/jev_trim, scripts/jev_pipes, the three test files, the jev-trim findings, the brief and the verify report is empty.

## Files

| file | lines | sha256 (first 16) |
|---|---|---|
| scripts/jev_trim/compaction.py (MODIFIED) | 2,017 | e17cc65651796be0 |
| tests/test_jev_trim_compaction.py (MODIFIED) | 1,079 | 1908c684664ed7eb |
| docs/research/findings/jev-trim/compaction-2026-09-29-r2/SUMMARY.md | 2,299 | 350c23b19a9b924a |
| …/pins.json | | a6c342b427a59abc |
| …/run-main.json (3,903,628 bytes) | | 36865d99ac34b1f8 |
| …/run-sub-a3977da56fa688986.json | | 86a8a5e94a684623 |
| …/run-sub-a4920ba3ae772b9d0.json | | 1d78a26f2a14e729 |
| …/run-sub-a4c0c331a18908947.json | | 80344c9d06372ad0 |
| …/run-sub-a4f24691b2f13e97e.json | | ae9ade60bea6a6b7 |
| …/run-sub-a58226189b58bf46f.json | | 8df095386afa9483 |
| …/run-sub-a60226a535b771d07.json | | b9e1f99307465000 |
| …/run-sub-a88c7c57f2fa2a96b.json | | b9c456d50d19cafb |
| …/run-sub-a90d7cc077452b42d.json | | 7ad89dbf37cc78bd |
| …/run-sub-aa842df27d05dd80d.json | | 46521de0e53da7d8 |
| …/run-sub-aad0e50d8019b70bb.json | | 7672be9e52808db7 |
| …/run-sub-ab1c8cf107bc6ad72.json | | ec51d543ed2bf927 |
| …/run-sub-ac753871198ee8cfd.json | | f0a0509f2434011c |
| …/run-sub-ac9c149483559ffec.json | | 7bba159497895e5e |
| …/run-sub-acc9cf211b3e34071.json | | d6e1b58dbec0d513 |
| …/run-sub-ae66dca0f21a920b6.json | | 68ff19bf7389210f |
| …/run-sub-af25a8ffadcb62c75.json | | 9fa1c28f644c25ee |

- **How the r2 files were written:** 3.11.15, 05:36:25Z to 05:40:07Z: `select` (the round-3 start sizes), 17 `run --shapes v2`, and `summary --stamp 2026-09-29T05:40:02Z` (taken from `date -u` when the summary was written).
- **The other changed paths in the tree are the K2 lane's, not mine:** scripts/codemap.py, tests/test_codemap.py, scripts/filepacks.py, tests/test_filepacks.py, tasks/briefs/jev-trim/K2-post-commit.patch.
- **Hygiene:** none of this round's bytecode is in the repo. No process of mine remains; the only live pytest is K2's (pid 20247).

## Red first (item 2)

On the round-3 module (95e160625dd2cd10), with R1 and R2 appended verbatim (report lines 420 to 447, `diff` confirmed VERBATIM-OK), 04:51:20Z:

```
E       assert (4, 1) == (1, 0)
E       assert 0 == 2
FAILED tests/test_jev_trim_compaction.py::test_a_write_is_not_a_search - asse...
FAILED tests/test_jev_trim_compaction.py::test_a_bash_view_of_a_file_read_before_is_a_refetch
2 failed, 31 deselected in 0.19s
```

On the final module (e17cc65651796be0):

```
2 passed, 97 deselected in 0.26s
```

## Per item: evidence

**Item 3, the shape-set option.** `--shapes {v1,v2}`, default v1. Under v2, the output is schema 2 and params gain `shape_set`, the labels, the program lists, `c5_*`, `bootstrap` and `tail_items`. Under v1, nothing is added.
- **Test:** `test_v1_writes_the_round_one_bytes`. It runs `main()` without `--shapes` on a fixture and checks both files against a golden: run-g.json 360a8c7c…, SUMMARY.md 99f455d6….
- **The golden's source:** I ran the round-3 module itself (scratch copy, 95e1606…) under 3.11.15 and 3.12.3. Both wrote identical hashes.
- **Mutants:** `v1-cli-defaults-to-v2`, `v1-schema-is-2`, `v1-params-take-v2-keys`.

**Item 4, reads apart from writes.**
- **Test:** `test_a_search_counts_reads_and_reports_writes_and_commits`. It holds 21 direction cases and the tool classes, including:
  - a heredoc body that is not parsed;
  - a comment that is dropped;
  - a line continuation;
  - a redirect to `/dev/null` that is a read;
  - a heredoc into a file that is a write.
- **R1's scenario:** the ledger search counts 1 read. Directions are read 1, write 2, commit 1; live-state is write 1. The v1 control counts 4.
- **Mutants:** `v2-search-counts-writes`, `v2-dev-null-is-a-write`, `v2-heredoc-body-parsed`, `v2-comment-parsed`, `v2-commit-scripts-unseen`. Each breaks exactly its own case: comment → the `sed … #` case; commit → safe_commit and push_clean; /dev/null → `grep -c … > /dev/null`; heredoc → `cat <<'EOF'`.
- **On main:** 117 of 638 matched K1 calls at N=20 are excluded (110 write, 7 commit).

**Item 5, the strict and loose shapes.**
- **Test:** `test_the_strict_and_loose_shapes`. Strict: 3 / 1 / 2 / 1 (a / b / c / d). Loose: grep 2, git_any 2. Totals: k1 0, strict 7, refetch 7, loose 4, with_loose 11.
- **Negative controls:** a view of an unknown file, `rg` for a new token, `sed -i` of a known file, and a view redirected into a file. None counts.
- **Mutants:** `v2-view-takes-any-file`, `-git-args-ignored`, `-dot-slash-not-folded`, `-no-suffix-match`, `-bash-views-not-collected`, `-loose-merged-into-refetch-total`, `-grep-takes-any-pattern`, `-writes-reach-the-labels`.
- **R2 passes.**

**Item 6, windows and controls.**
- **Test:** `test_the_windows_and_the_three_controls`.
  - Real windows: 20 → 1, 20-99 → 1 (80 requests), 100 → 2, rest → 3.
  - C1: 0 / 105.
  - C2: boundary 1, position 110, tail_calls 1. With the tail: 20 → 1, 20-99 → 1, 100 → 2, rest → 2. Without it: 100 → 1.
  - C5 positions: (0,100), (0,120) … (0,180), (1,100), (1,120), whole windows only.
- **Test:** `test_the_bootstrap_interval`. It checks against an independent re-computation from `Random(seed)` and nearest rank, a changed seed that differs, a no-spread case (5.0, 5.0), and an empty case (None). The seed is sha256 of the cell's name.
- **Mutants:** `v2-c2-drops-the-tail`, `-c2-at-the-middle`, `-c5-keeps-clipped-windows`, `-c5-from-request-0`, `-window-20-99-from-request-0`, `-bootstrap-seed-ignored`, `-bootstrap-upper-rank-off`.
- **Main's point counts:** C1 27, C2 26, C5 386 at N=20 and 129 at N=100 and 20-99. 792 tail items are kept.

**Item 7, the position-aware cost model.**
- **Test:** `test_the_position_aware_model_on_hand_computed_numbers`, computed by hand: 1 compaction, 25 requests, mean fill 162.4, reads 3630, writes 430, summarizer 250. The flat model differs. Calibration: (1.0, 1, 1) for target 1; for target 2, unscaled 1, scaled 2, scale in (1, 2).
- **Test:** `test_the_position_aware_model_is_calibrated_and_the_usage_read`: steps {0-19: 9}, unscaled 3, calibrated 2, target 2, scale in (0, 1). Actual usage is 12 requests, 7,099,964 reads, 0 writes, mean 591,666.7.
- **Mutants:** `v2-position-never-resets`, `-position-ratio-inverted`, `-calibration-skipped`, `-actual-reads-are-contexts`.
- **The loss rows (`loss_v2`)** take refetch_total and with_loose_total, as the excess per boundary over C1, C2 and C5, times the compactions. This is on both models.

**Item 8, the small ones.**
- **F9.** The v2 summary has a "share of missed paths named before" column. Main, 1M class: 2.02% (N=20), 1.18% (20-99), 1.36% (100), 1.31% (rest).
- **F11.** `run --pin size+1` exits 2 with `PinBeyondFileSize: --pin … is beyond the size of t.jsonl (… bytes)` on stderr and writes no file. Test: `test_a_pin_beyond_the_file_stops_with_a_named_error`. Mutant: `v2-pin-guard-dropped`.
- **F7: the fixture cases added.**
  - in the R-C fixture: a prompt_snapshot (SNAP), a `/tasks/…output` Read plus a half-group `ls …/tasks/`, a relative path token (`lib/core.py`), a path both read and edited, an assistant-text token, THIRD_PATH (read_known_path, not re-injected), and postTokens asserted;
  - in the R-B fixture: a boundary, a `<synthetic>` record, an other-thread record, a request whose later usage record differs, and an offset re-read;
  - in the cost fixtures: a negative step, K from included segments that open at a boundary, the excess asserted (`test_the_excess_is_the_real_mean_minus_the_control`), and a 200k-class C1 point.

**Item 9, byte identity.**
- **3.11.15, final code:** 19 of 19 OK, `sha256sum -c` against the committed files. All 17 runs were regenerated, and `select` ran over the mirror.
- **3.12.3, final code:** 19 of 19 OK, same method.
- **Against the live subagent directory:** 17 of 19 OK. pins.json and SUMMARY.md differ only by `"not_pinned_with_a_boundary_now": ["agent-a038a373e43037a56.jsonl"]` and the line "…: 1." (was 0).
- **v2 across interpreters:** the r2 outputs regenerated under 3.12.3 (the same stamp) are 19 of 19 identical to the committed 3.11 files.
- **The replay tool's rounds 1 and 2:** its tests pass (68 passed, below).

## Gates (item 10)

`--basetemp` was a pytest argument under the session scratchpad. `PYTHONDONTWRITEBYTECODE=1`, `PYTEST_ADDOPTS` unset. Python 3.11.15, 05:51:07Z to 05:52:37Z:

```
1 files set=7f396804fe23
pytest-exit: 0 pytest-summary: 99 passed in 12.90s
pytest-exit: 0 pytest-summary: 99 passed in 12.75s
1 files set=1bb7608ed22a
pytest-exit: 0 pytest-summary: 68 passed in 7.52s
pytest-exit: 0 pytest-summary: 68 passed in 7.24s
1 files set=17f6a5adc0c9
pytest-exit: 0 pytest-summary: 42 passed in 23.63s
pytest-exit: 0 pytest-summary: 42 passed in 23.47s
3 files set=74199ac6b13a
```

Python 3.12.3 (scratch venv first on PATH), once each:

```
1 files set=7f396804fe23
pytest-exit: 0 pytest-summary: 99 passed in 14.18s
1 files set=1bb7608ed22a
pytest-exit: 0 pytest-summary: 68 passed in 8.13s
1 files set=17f6a5adc0c9
pytest-exit: 0 pytest-summary: 42 passed in 23.83s
```

pyflakes on both files: exit 0.

## Mutants: 65, all killed

- **Groups:** round 1's 15; VERIFY-K1's N01 to N22 (22); round 2's 25; v1 guards 3.
- **Test count:** 99 = 34 tests + 65 mutants.
- **Where each dies:** a scratch diagnostic applied every mutant and recorded where it died. All 65 die at the assertion written for them (VERIFIED, `why_killed.py`). None survived, and none died of another exception.
- **N01 to N22:**
  - N01 and N02: the refetch shape map;
  - N03: the REL assertion;
  - N04: the EDIT_PATH read-before assertion;
  - N05: the SNAP reused assertion;
  - N06: the runtime guard inside `compaction_loss`;
  - N07: the TEXT_T assertion;
  - N08: the C1 re-run count;
  - N09 to N13: the 300k-400k bin;
  - N14: the steps count;
  - N15: the negative-step writes;
  - N16: the excess;
  - N17: the thirds;
  - N18: the reinjected count;
  - N19: the b1 re-runs;
  - N20: the C1 class;
  - N21: postTokens;
  - N22: K.
- **Against VERIFY-K1:** it had 3 killed and 19 surviving; now all 22 are killed.

## §10.6 re-answered from the v2 numbers

Rates are per 100 requests. The excess is the real rate minus the control's, with its 95% interval.

### Main, 1M class (121 boundaries)

**refetch_total (K1's shapes with writes out, plus strict)**

| window | real | C1 | C2 | C5 | excess per boundary, calls / tokens (C1, C2, C5) |
|---|---|---|---|---|---|
| first 20 | 38.07 | 18.52: +19.56 [14.75, 24.48] | 17.88: +20.19 [16.13, 24.16] | 17.51: +20.56 [16.93, 24.53] | +3.91 / +9,338; +4.04 / +9,200; +4.11 / +9,585 |
| 20 to 99 | 19.60 | 16.44: +3.17 [0.52, 5.91] | 15.96: +3.64 [0.85, 6.47] | 16.67: +2.93 [0.15, 5.62] | +2.44 / +3,577; +2.81 / +4,875; +2.26 / +4,227 |
| first 100 | 23.40 | 16.85: +6.55 [3.71, 9.24] | 16.35: +7.06 [4.50, 9.50] | 17.38: +6.02 [3.29, 8.67] | +6.36 / +12,915; +6.85 / +14,089; +5.85 / +13,405 |
| rest | 20.26 | 16.35: +3.91 [1.42, 6.34] | 16.35: +3.91 [1.55, 6.21] | none | +6.54 / +13,073; +6.54 / +13,463 |

**Excess of the parts, over C1 / C2 / C5:**
- K1's shapes alone (writes out):
  - N=20: +9.32 / +10.58 / +9.32. All intervals exclude 0.
  - 20 to 99: +0.44 / +0.47 / +0.18. All include 0.
  - 100: +2.27 / +2.54 / +1.75. Only C2's excludes 0.
  - rest: +1.08 / +1.18. Both include 0.
- The strict set alone: N=20 +10.24 / +9.61 / +11.24; 20 to 99 +2.72 / +3.17 / +2.76; 100 +4.28 / +4.52 / +4.27; rest +2.83 / +2.73. All intervals exclude 0.
- The loose set (its own total): N=20 +6.45 [0.25, 12.94] / +14.21 / +6.80; 20 to 99 +8.98 / +10.10 / +7.14; 100 +8.48 / +10.94 / +7.12; rest +7.07 / +8.77.

**The kind, N=20, real against C1 / C2 / C5:**
- Bash view of a known file: 11.95 against 4.44 / 5.00 / 3.60.
- Ledger reads (search_ledger, counted): 8.89 against 2.04 / 1.92 / 2.54. Its writes are 3.43 against 4.81 / 5.00 / 4.61; its commits 0.25 against 1.30 / 2.50 / 1.57.
- Live-state reads: 1.90 against 0.19 / 0.38 / 0.27.
- Transcript searches: 8.72 against 7.04 / 6.73 / 7.78.
- git with repeated arguments: 3.84 against 1.85 / 1.92 / 1.65.
- Read of a known path: 1.53 against 0.56 / 0.77 / 0.19.
- Identical re-run: 0.04 against 1.48 / 0.77 / 1.17.
- Grep for a known token: 21.95 against 17.04 / 9.62 / 16.63.

**The 200k class** has 18 boundaries and no control point of any kind.

### Subagents pooled (16 files, 21 boundaries; control points C1 7, C2 7, C5 85)

**refetch_total**

| window | real | C1 | C2 | C5 | excess per boundary, calls (C1, C2, C5) |
|---|---|---|---|---|---|
| first 20 | 50.44 | 18.57: +31.87 [19.27, 43.61] | 22.86: +27.59 [13.82, 40.39] | 24.65: +25.80 [15.38, 35.88] | +5.14 / +4.45 / +4.16 |
| 20 to 99 | 32.13 | +14.99 | +16.42 | +12.63 (all intervals exclude 0) | +7.91 / +8.66 / +6.66 |
| first 100 | 36.42 | 17.43: +18.99 | 17.14: +19.28 | 19.93: +16.49 | +13.09 / +13.28 / +11.36 (tokens +23,152 / +20,844 / +23,341) |
| rest | 32.34 | +15.61 | +15.20 | none | +16.99 / +16.54 |

**The kind, N=20:** transcript searches 25.37 against 10.00 / 9.29 / 9.06; Bash views of a known file 15.34 against 5.00 / 7.86 / 10.35; Read of a known path 5.60 against 0.00 / 2.86 / 2.29.

### Quality (R-B)

The code is unchanged and the v1 bytes are identical, so round 1's R-B numbers stand.

## Cost-model rows (main; MODEL, not a measurement)

- K = 119,625; 20,585 steps; 11 negative.
- Growth by position: 0-19 6,202 (2,440 steps); 20-99 4,310 (9,474); 100+ 2,830 (8,550).

| X | flat: compactions | mean fill | cache reads | cache writes | position-aware: compactions (unscaled) | mean fill | cache reads | cache writes |
|---|---|---|---|---|---|---|---|---|
| 300,000 | 427 | 205,288 | 4,100,747,389 | 125,902,060 | 586 (589) | 208,577 | 4,122,679,980 | 172,154,988 |
| 400,000 | 278 | 256,417 | 5,169,179,159 | 110,014,563 | 353 (354) | 267,024 | 5,357,952,278 | 139,843,374 |
| 500,000 | 206 | 305,770 | 6,192,762,386 | 102,412,440 | 246 (247) | 322,051 | 6,508,047,128 | 122,503,139 |
| 600,000 | 164 | 355,983 | 7,230,448,795 | 98,409,562 | 186 (187) | 376,812 | 7,646,147,888 | 111,699,825 |
| 700,000 | 136 | 406,302 | 8,269,623,513 | 95,112,346 | 146 (146) | 437,552 | 8,905,523,707 | 102,581,613 |
| 785,000 | 119 | 453,578 | 9,244,750,496 | 93,190,429 | 121 (122) | 488,223 | 9,955,796,034 | 95,387,028 |

**Actual usage** of the 20,586 included requests: cache reads 9,552,612,747; cache writes 124,444,652; mean context 470,094.

**At 785k against the actual:**
- flat: cache reads −3.2%, writes −25.1%, mean fill −3.5%;
- position-aware: cache reads +4.2%, writes −23.3%, mean fill +3.9%.

**Corrected loss** (refetch_total excess × compactions), in calls / tokens:

| X | model | N=20 over C1 | over C2 | over C5 | N=100 over C1 | over C2 | over C5 |
|---|---|---|---|---|---|---|---|
| 500k | flat | 805 / 1.92M | 831 / 1.90M | 847 / 1.97M | 1,311 / 2.66M | 1,412 / 2.90M | 1,205 / 2.76M |
| 500k | position-aware | 962 / 2.30M | 993 / 2.26M | 1,011 / 2.36M | 1,565 / 3.18M | 1,686 / 3.47M | 1,439 / 3.30M |
| 785k | flat | 465 / 1.11M | 480 / 1.09M | 489 / 1.14M | 757 / 1.54M | 816 / 1.68M | 696 / 1.60M |
| 785k | position-aware | 473 / 1.13M | 488 / 1.11M | 497 / 1.16M | 770 / 1.56M | 829 / 1.70M | 708 / 1.62M |

All six X values for both models are in SUMMARY.md.

## DISCREPANCIES (every number that differs from VERIFY-K1's, with why)

1. **K1's shapes writes out, main, N=20, real side.**
   - VERIFY-K1: 21.1 per 100 (511 calls; 4.22 per boundary).
   - Mine: 21.54 (521 calls; 4.31 per boundary).
   - Why: the direction classifiers differ. I exclude 117 of 638 matched calls; the discriminator excluded 127. INFERRED: its code was removed.
2. **The same at C1, N=20.**
   - VERIFY-K1: 16.1 per 100 (87 calls).
   - Mine: 12.22 (66 calls).
   - Why: I exclude 63 of 129 calls (47 write, 16 commit); VERIFY-K1 excluded 42. A histogram of program names only shows each of my 63 exclusions holds a write or a commit by the brief's rules:
     - 26 hold a `safe_commit.sh` or git commit command;
     - 30 hold a file redirect.
   - Of these, 14 to 16 are commit sequences with no write, of the form `export STAMP … ; python3 - <<EOF ; git reset ; bash scripts/safe_commit.sh`.
   - VERIFY-K1's split table implies it kept about 20 C1 ledger calls as neither read nor write. This is the main driver of my larger excess. INFERRED.
3. **K1's shapes writes out, N=100.**
   - VERIFY-K1: 14.51 against 16.56 per boundary (−2.04).
   - Mine: 14.27 against 12.00 per 100 (+2.27; about +2.2 per boundary).
   - Why: the same classifier cause (my C1 excludes 123 more calls).
   - At rest, VERIFY-K1 gave 24.10 against 23.44 per boundary; mine is 12.91 against 11.83 per 100.
4. **Search split, N=20** (after / C1 / C5).

   | shape | VERIFY-K1 reads | my read direction | VERIFY-K1 writes | my writes (+ commits) |
   |---|---|---|---|---|
   | ledger | 8.02 / 0.74 / 1.90 | 8.64 / 1.67 / 2.40 | 3.64 / 3.70 / 4.24 | 3.43 / 4.81 / 4.61 (+0.25 / 1.30 / 1.57) |
   | live-state | 1.78 / 0.19 / 0.19 | 1.90 / 0.19 / 0.25 | 0.41 / 0.74 / 0.84 | 0.37 / 1.11 / 0.92 (+0.04 / 1.11 / 0.78) |
   | transcript | 6.28 / 6.11 / 5.92 | 7.19 / 6.48 / 6.90 | 1.20 / 3.33 / 2.53 | 0.74 / 2.78 / 1.93 (+0 / 0.56 / 0.49) |

   Why: the class definitions and the precedence differ.
5. **Strict and loose, VERIFY-K1's matched-history table vs mine.** Why: the history rule (whole pre segment, 121 boundaries, against 100 matched requests on 104), plus item 2.

   | set, window | VERIFY-K1 (real vs C1 / C2 / C5) | mine |
   |---|---|---|
   | strict, N=20 | 14.8 vs 7.0 / 4.4 / 5.6 | 16.54 vs 6.30 / 6.92 / 5.30 |
   | strict, 20-99 | 6.5 vs 4.6 / 4.5 / 4.6 | 7.21 vs 4.49 / 4.04 / 4.46 |
   | K1's + strict, N=20 | 36.3 vs 23.0 / 19.8 / 20.0 (+13.4 / +16.5 / +16.3) | 38.07 vs 18.52 / 17.88 / 17.51 (+19.56 / +20.19 / +20.56) |
   | per boundary, N=20 | +2.67 / +3.30 / +3.26 calls; +7,161 / +7,124 / +7,365 tokens | +3.91 / +4.04 / +4.11 calls; +9,338 / +9,200 / +9,585 tokens |
   | K1's + strict, 20-99 | 20.1: −0.6 / −0.2 / +0.5 | 19.60: +3.17 / +3.64 / +2.93 |
   | K1's + strict, N=100 | 23.4 vs 21.2 / 20.2 / 19.7 | 23.40 vs 16.85 / 16.35 / 17.38 |
   | K1's + loose / + strict + loose, N=20 | 50.5 vs 33.0 / 27.3 / 29.9 | 62.67 vs 36.67 / 28.27 / 35.31 |
   | K1's + loose / + strict + loose, N=100 | 36.1 vs 29.1 / 26.9 / 28.3 | 46.11 vs 31.07 / 28.12 / 32.96 |

   At N=100 the real rates are equal (23.4); the controls differ.
6. **By label, N=20, against C5.**
   - Bash view of a known file: 10.97 vs 3.87 → mine 11.95 vs 3.60.
   - git log/show with repeated arguments: 4.67 vs 1.92 → git_repeated_args 3.84 vs 1.65. Mine requires the same subcommand, adds diff and blame, and K1's rerun_command takes identical commands first.
   - Any git log/show/diff: 9.33 vs 3.95 (inclusive) → git_any 2.65 vs 1.17. Mine is the remainder only.
   - Grep for a known token: 12.31 vs 9.49 → 21.95 vs 16.63. My "seen before" counts any accounting token of the pattern found in any pre-segment item, which is broader.
7. **Subagents pooled.**
   - K1's shapes writes out, N=100: VERIFY-K1 22.3 vs 8.1 to 11.4 (+10.8 to +14.1); mine 22.74 vs 8.14 / 8.14 / 9.07 (+13.67 to +14.59).
   - K1's + strict, N=100: VERIFY-K1 +14.8 to +18.8, +10 to +13 calls, +19k to +23k tokens per boundary; mine +16.49 to +19.28, +11.36 to +13.28 calls, +20.8k to +23.3k tokens.
   - Why: the classifier and the history rule; VERIFY-K1's range also includes C3.
8. **Headline "+2.5 to +3.3 calls per boundary in the first 20 requests"** is mine at +3.91 to +4.11 (C1 / C2 / C5; no C3). Why: items 2 and 5.
9. **Growth means.** Mine now equal VERIFY-K1's (6,202 / 4,310 / 2,830) under its convention; under my first convention they were 6,265 / 4,315 / 2,853 (deviation 7).
10. **Position-aware rows.**
    - VERIFY-K1: 589 / 354 / 247 / 187 / 146 / 122; reads 4.15B / 5.30B / 6.46B / 7.62B / 8.84B / 9.84B.
    - Mine at scale 1 (scratch diagnostic `diag_unscaled.py`): exactly these. VERIFIED.
    - Committed (calibrated, scale 0.993736): 586 / 353 / 246 / 186 / 146 / 121; reads 4.12B / 5.36B / 6.51B / 7.65B / 8.91B / 9.96B.
    - Why: the brief asks for calibration to the observed 121.
    - The 500k/785k read ratio: 0.654 calibrated, against VERIFY-K1's 0.66.
11. **Position-aware against actual usage** (new; VERIFY-K1 gave the flat model only): reads +4.2%, writes −23.3%, mean fill +3.9%. The flat model matches: −3.2% / −25.1% / −3.5%.
12. **F9 share:** 2.02% / 1.36% / 1.31%, against 2.0 / 1.4 / 1.3 (the same, with more digits).
13. **N01 to N22:** 3 killed → 22 killed.
14. **Point counts** C1 27, C2 26, C5 386 / 129: equal to VERIFY-K1's. None differ.
15. **Gate count** for the compaction file: 31 → 99 (the file grew).
16. **Flat model, actual usage, K, steps, and the miss (86.0 / 301.2 / 411.3):** identical, no discrepancy.
17. **pins.json in r2** lists 1 file not pinned with a boundary now (agent-a038a373e43037a56.jsonl, modified 04:55:26Z, the coordinator's audit lane). VERIFY-K1 found 0 at about 03:50Z. Why: live data changed; the pins list is unchanged.

## Self-attack: the three likeliest ways this is wrong

1. **The direction classifier over-excludes at the controls, which inflates the excess.**
   - For: my C1 base rate is 3.9 per 100 below VERIFY-K1's discriminator.
   - Checked: all 63 C1 exclusions hold a write or a commit by the brief's rules, as written. The per-direction counts are published, so a stricter "read-only" count, or a count with commits in, can be recomputed.
   - NOT ruled out: the precedence and the target-agnostic redirect rule are interpretations. This is the largest open risk to the size of the corrected excess. Its sign at N=20 holds under every reading: K1's + strict at C1 is +19.6, and the strict set alone is +9.6 to +11.2. All intervals exclude 0.
2. **The C2 tail capture (a runtime wrap of `replay._segments`) could change the timeline or leak into other code.**
   - Ruled out:
     - the wrapper returns the original's segments;
     - v1 outputs are byte-identical on real data under both interpreters;
     - the replay tests pass in the same process (68 passed);
     - the wrapper is restored in `finally`;
     - the fixture shows the tail changes only C2's end-reaching windows (2 with the tail, 1 without).
3. **The bootstrap or the calibration could be wrong or non-deterministic across Pythons.**
   - Ruled out:
     - the bootstrap matches an independent re-computation in the test;
     - two v2 runs write identical bytes;
     - a 3.12 regeneration of all 19 r2 files equals the committed 3.11 files byte for byte;
     - the unscaled position-aware rows reproduce VERIFY-K1's rows exactly.

## Evidence tiers

- **VERIFIED:** everything run above. That covers the red run, gates, byte identity, mutants, where each mutant dies, the r2 outputs, the unscaled reproduction and the growth convention.
- **INFERRED:** the causes named for DISCREPANCIES 1 to 8 (VERIFY-K1's classifier code is gone); and that the post-boundary excess is caused by the compaction (a control comparison, not an intervention).
- **ASSUMED:** the price ratios (READ_RATIO 0.05, WRITE_RATIO 2.0, as round 1), and my readings of "reads only" (deviation 2) and of C2 eligibility (deviation 4).

## Scratch

All scratch files are under `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/k1r4/`:
- `regen.sh`, `golden.sh`
- `diag_dirs.py`, `diag_growth.py`, `diag_unscaled.py`
- `why_killed.py`
- the `subs-mirror` symlink directory
- the regeneration directories

Nothing was written outside the boundary. I rated every [S1 …] injection with an S1-RATE line as it arrived.
