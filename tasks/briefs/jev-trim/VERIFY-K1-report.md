> Coordinator note (2026-09-29 04:2xZ): the report of record, extracted by `scripts/stack.py harvest` (run s-20260929T042044Z-22db0b). Served model: claude-opus-5-5 on all 262 assistant records, 0 refusal stops, 1 tool-error cluster. `report_lint`: 1 ref, 1 MISS: the cite of the ledger's K1 landing line quotes its words with an ellipsis (the line is the entry headed "K1 HOME AND LANDED (TASK #352; GATED-PENDING-VERIFY)"), so the lint's token match fails; the line is right. Local ids: none cited. The coordinator's disposition: MERGE-READY-WITH-FOLLOWUPS accepted; F2 and F3 (with F5, F7, F9 and F11's gap) go to one focused repair, K1 round 2, as a contract amendment (`tasks/briefs/jev-trim/K1-R2-brief.md`); F8 closes task #357 as immaterial; F10's stale places are marked.

# VERIFY-K1 report (task #352, D-106): K1's compaction-loss numbers

Written 2026-09-29, last `date -u` 04:08:37Z. Role: sandbox adversarial verifier, served as claude-opus-5-5. No subagents, no git writes, no PC bridge, no model or network call. Scratch lived only under `/tmp/vk1/` and is removed.

## Answer first

- **Gate: MERGE-READY-WITH-FOLLOWUPS against the frozen K1 contract, with one CONTRACT-DEFECT (F3) returned to you.**
  - No finding meets the whole blocking predicate of D-031 with D-034's good-state stop.
  - F3's missed-shape counts come from my own reader. That reader reproduces compaction.py's contracted shapes with 0 differences.
  - F3's blind spot also shows through the production path, as a red test.
- **§10.6's reading ("a compaction costs this session little re-fetching") does NOT stand.** Its numbers undercount the compaction's re-fetch cost, for two reasons:
  - **F2, writes counted as searches.** K1's `search_*` shapes count ledger edits, commits and live-state edits as re-fetches, which inflates both sides of the comparison.
  - **F3, missed shapes.** K1's contracted shapes cannot see how this session mostly re-fetches: Bash views of files it knew before the boundary, repeated `git log/show`, and genuine ledger and live-state reads.
  - Corrected, the first 20 requests after a compaction carry +12.6 to +16.5 re-fetch calls per 100 requests over four controls. That is about +2.5 to +3.3 calls and +7k tokens per boundary, five to seven times K1's +0.49 calls.
  - The 95% bootstrap intervals all exclude 0.
  - Over 100 requests the corrected excess is positive (+1.5 to +3.7 per 100 strict, +4.8 to +9.2 loose), not the quoted −3.7.
- **What I reproduced exactly:**
  - All headline numbers, with an independent reader: 9,909 fields on main and 3,315 on the 16 subagent files, 0 differences.
  - All 19 outputs, byte-identical under Python 3.11.15 and 3.12.3.
  - All gates, twice each.
  - The coordinator's probe, at the pin.
  - All 15 named mutants, as FAILED tests.
- **The cost model** reproduces exactly, but its calibration has little power and its constant-growth assumption fails in the data. A position-aware variant, equally calibrated, gives 247 compactions at 500k instead of 206.

## Premise re-run (03:22:15Z): every line matched

```
PIN-is-an-ancestor-of-HEAD
95e160625dd2cd10  scripts/jev_trim/compaction.py
fff6fb719740142e  tests/test_jev_trim_compaction.py
a77e0c3ff1261bde  docs/research/findings/jev-trim/compaction-2026-09-29/SUMMARY.md
bff43daab618cc47  docs/research/findings/jev-trim/compaction-2026-09-29/pins.json
19
341:### 10.6 K1: what our own compactions cost (2026-09-29)
3 files set=74199ac6b13a
141 passed
ls: cannot access '/tmp/vk1': No such file or directory
```

- **HEAD moved during the run.** It was the commit "K1 landed (task #352; GATED-PENDING-VERIFY)…" at the premise and is "transcripts: scrubbed sandbox chat digests (2026-09-29)" now. Your push rewrote the local ids in between.
- **The files under test did not move.** At 04:03Z the four hashes were unchanged, and so were `tests/test_jev_trim_replay.py` (841351f042ae62d4) and `replay.py` (73a16e72ed933db5).
- **One scratch location outside `/tmp/vk1`.** The literal premise line uses `/tmp/vk1-premise-bt`; I removed it.

## Gates

Python 3.11.15, 03:49:57Z to 03:51:08Z. `--basetemp` was a pytest argument under `/tmp/vk1/bt`, `PYTHONDONTWRITEBYTECODE=1` was set, and `PYTEST_ADDOPTS` was unset.

```
1 files set=7f396804fe23
pytest-summary: 31 passed in 2.58s
pytest-summary: 31 passed in 2.70s
1 files set=1bb7608ed22a
pytest-summary: 68 passed in 7.55s
pytest-summary: 68 passed in 7.38s
1 files set=17f6a5adc0c9
pytest-summary: 42 passed in 24.75s
pytest-summary: 42 passed in 24.20s
3 files set=74199ac6b13a
```

Python 3.12.3, my own venv (built offline from the uv cache), through the same script with the venv first on PATH:

```
1 files set=7f396804fe23
pytest-summary: 31 passed in 2.72s
1 files set=1bb7608ed22a
pytest-summary: 68 passed in 8.31s
1 files set=17f6a5adc0c9
pytest-summary: 42 passed in 24.93s
```

## Item 1: the headline numbers, from my own reader

**The reader.**
- It streams the records, keeps two segments in memory at a time, and never reads a thinking block's text.
- It is written from the contract and from `replay.py`'s docstring. It does not import `compaction.py` or `replay.py`.
- Its only repo import is `accounting.tokens`, the contract's own token classes.
- Peak memory 122 MB, against the builder's 1.34 GB.

**Main, within its pin of 788,725,407 bytes.**
- **Boundaries:** 139 `compact_boundary` records, all `auto`, preTokens from 144,106 to 802,058. Of them, 121 are 1M-class and 18 are 200k-class. There are 140 segments and 21,118 requests.
- **Per-boundary comparison with `run-main.json`:** 9,909 fields, 0 differences. The fields cover:
  - the pre segment: requests, last context, modeled tokens, files read and edited, commands, distinct tokens;
  - the kept start per boundary: items, modeled tokens, first context, postTokens, re-injected files, distinct tokens;
  - every window: requests, used, reused, missed, missed paths and read/edited-before, each shape's calls, total calls, re-fetch requests, re-injected reads;
  - the 27 control points, and the R-B bins and thirds.
- **Re-fetch calls per 100 requests after 1M-class boundaries:**

  | window | re-fetch calls / requests | per 100 requests | control |
  |---|---|---|---|
  | N = 20 | 638 / 2,419 | 26.4 | 23.9 |
  | N = 100 | 2,572 / 11,750 | 21.9 | 25.6 |
  | rest | 4,365 / 20,233 | 21.6 | 25.0 |

- **R-B tool errors per 100k of fill:** 1/150 (0.67%), 43/2,617 (1.64%), 72/3,565 (2.02%), 62/3,460 (1.79%), 76/3,603 (2.11%), 54/3,462 (1.56%), 48/3,317 (1.45%), 51/3,018 (1.69%).
- **R-B by segment third:** errors 1.89%, 1.78%, 1.58%; re-runs 15/6,607, 45/5,842, 78/5,619.
- **The coordinator's `k1_authoring_probe.py`:** I fed it exactly the pinned prefix through a FIFO. It gives the same requests, calls, error % (0.7, 1.6, 2.0, 1.8, 2.1, 1.6, 1.4, 1.7), edits and reads in every bin. Three instruments agree on R-B.
- **Spot checks of the report:** 37 re-injected Reads at `rest`; 86.0, 301.2 and 411.3 missed tokens per boundary; 657,623 removed and 58,273 kept per boundary. All match.

**The 16 pinned subagent files.** 3,315 fields, 0 differences.

## Item 2: the control

I built three more controls beside the builder's. Each uses K1's own history rule: "known" means seen in the pre segment.
- **C1:** the builder's control, the middle of every segment of 200 or more requests.
- **C3:** request 100 of those same segments.
- **C2:** paired to each boundary, the last 100 requests of its pre segment. The window's final outputs are counted.
- **C5:** sliding, every 20 requests from request 100.

The intervals are 95% bootstrap, with C5 resampled by segment.

| window, K1's shapes | real | C1 (27) | C3 (27) | C2 (26) | C5 (386 at N=20, 129 at N=100) |
|---|---|---|---|---|---|
| N = 20 | 26.4 | 23.9: +2.5 [−2.4, 7.7] | 24.3: +2.1 [−3.4, 7.6] | 25.8: +0.6 [−5.7, 6.5] | 22.5: +3.9 [0.0, 7.8] |
| N = 100 | 21.9 | 25.6: −3.7 [−7.3, −0.4] | 24.6: −2.7 [−5.9, 0.5] | 25.6: −3.7 [−7.1, −0.5] | 23.1: −1.2 [−3.7, 1.6] |
| requests 20–99 only | 20.7 | 26.0: −5.3 | 24.7: −4.0 | 25.6: −4.9 | 23.3: −2.6 |

**Mean fill at the windows:**

| window | real | C1 | C3 | C2 | C5 |
|---|---|---|---|---|---|
| N = 20 | 185,641 | 487,780 | 413,110 | 588,172 | 602,588 |

- **A fill-matched control is impossible on the 1M class.** Every fill below about 250k sits right after a real boundary.
- **A matched-history variant changes little.** In it, "known" means seen in the last 100 requests before the point, on 104 boundaries. The builder shapes barely move, and the missed-shape excess falls by only 2 to 3 per 100.
- **Answer to the brief's question.** Within K1's contracted shapes, "no excess after the first 20 requests" is robust to the control: all four agree. The N=20 excess cannot be told from 0 under three of the four. The weak point is the shape set, not the control (F2, F3).

## Item 3: re-fetches the shapes miss, and writes the shapes wrongly count

**How I classified direction.**
- Every matched call is classed as a read, a write (an edit tool; an anchor edit; `sed -i`, `tee`, `cp`/`mv`; a redirect into a file other than `/dev/null`), a commit (`safe_commit.sh`, `push_clean.sh`, `git commit/add/push`), a script, or other.
- Bash is parsed with shlex, and heredoc bodies are excluded.
- I checked the classifier on 13 synthetic commands, 13 of 13 correct.
- Heredoc scripts count as non-writes, so the write shares below are lower bounds.

**The strict missed shapes** are counted only on calls K1 matches with no shape, writes excluded:
- a Bash `cat`/`sed`/`head`/`tail`/`nl`/`less`/`awk` view of a file the pre segment Read, edited or viewed;
- a Read of a Bash-viewed file;
- a `git log/show/diff/blame` with the same non-flag arguments as one before;
- a Read of a known path spelled another way.

**The loose set** adds greps (the Grep tool, `grep`/`rg`, `graft ask`) for a token seen before, and any `git log/show/diff`.

Main, 1M class, matched 100-request history, 104 boundaries. Cells show the control's rate per 100, then the excess and its interval. For N=20 and N=100 the second line gives the excess in calls and tokens per boundary.

| shape set | window | real | C1 | C3 | C2 | C5 |
|---|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 21.5 | 15.9: +5.6 [0.9, 10.0] | 17.2: +4.3 [−0.1, 9.0] | 15.4: +6.1 [0.7, 11.2] | 14.4: +7.1 [3.6, 10.5] |
| K1's shapes, writes out | 100 | 15.2 | 16.1: −0.9 | 16.6: −1.4 | 15.8: −0.6 | 14.9: +0.3 |
| strict missed shapes | 20 | 14.8 | 7.0: +7.8 [4.7, 10.9] | 6.5: +8.3 [5.5, 11.2] | 4.4: +10.4 [7.3, 13.4] | 5.6: +9.2 [6.9, 11.6] |
| strict missed shapes | 20–99 | 6.5 | 4.6: +2.0 [0.6, 3.4] | 5.0: +1.5 [0.1, 3.0] | 4.5: +2.1 [0.8, 3.5] | 4.6: +2.0 [0.8, 3.2] |
| K1's + strict, writes out | 20 | 36.3 | 23.0: +13.4 [8.2, 18.4] | 23.7: +12.6 | 19.8: +16.5 [11.3, 21.9] | 20.0: +16.3 [12.5, 20.0] |
| | | | +2.67 calls, +7,161 tok | +2.52, +7,177 | +3.30, +7,124 | +3.26, +7,365 |
| K1's + strict, writes out | 20–99 | 20.1 | 20.8: −0.6 | 21.5: −1.3 | 20.3: −0.2 | 19.6: +0.5 |
| K1's + strict, writes out | 100 | 23.4 | 21.2: +2.2 | 21.9: +1.5 | 20.2: +3.2 [0.1, 6.2] | 19.7: +3.7 [1.1, 6.4] |
| | | | +2.18 calls, +6,842 tok | +1.49, +7,841 | +3.15, +7,594 | +3.62, +8,748 |
| K1's + loose, writes out | 20 | 50.5 | 33.0: +17.5 | 34.6: +15.9 | 27.3: +23.2 | 29.9: +20.6 |
| K1's + loose, writes out | 100 | 36.1 | 29.1: +7.0 | 31.3: +4.8 | 26.9: +9.2 | 28.3: +7.8 |
| | | | +6.80 calls, +12,277 tok | +4.70, +12,685 | +8.97, +13,963 | +7.65, +13,395 |

**The excess is broad, not driven by outliers.**
- 95 of 104 boundaries (91%) carry a strict re-fetch in the first 20 requests, against 62% of C5 windows.
- The top five boundaries hold 48 of the 308 strict calls.

**By label, first 20 requests, per 100 requests (after a boundary against C5):**

| label | after a boundary | C5 |
|---|---|---|
| Bash view of a known file | 10.97 | 3.87 |
| `git log/show` with repeated arguments | 4.67 | 1.92 |
| any `git log/show/diff` | 9.33 | 3.95 |
| grep for a known token | 12.31 | 9.49 |

**K1's `search_*` shapes, split into reads and writes, per 100 requests, N=20 (after a boundary; C1; C5):**

| shape | reads after | reads C1 | reads C5 | writes after | writes C1 | writes C5 |
|---|---|---|---|---|---|---|
| ledger | 8.02 | 0.74 | 1.90 | 3.64 | 3.70 | 4.24 |
| live-state | 1.78 | 0.19 | 0.19 | 0.41 | 0.74 | 0.84 |
| transcript | 6.28 | 6.11 | 5.92 | 1.20 | 3.33 | 2.53 |

At N=100, writes are 578 of the 1,274 `search_ledger` matches after boundaries and 122 of 269 at C1.

**Canonical-path discriminator.** I ran a scratch copy of `compaction.py` in which `_shape` returns no search shape for a write-direction call, over main at the pin, with the builder's own 27-point control:

| window | committed: calls per boundary (per 100) | discriminator: calls per boundary (per 100) | excess, committed → discriminator |
|---|---|---|---|
| N = 20 | 5.27 vs 4.78 (26.4 vs 23.9) | 4.22 vs 3.22 (21.1 vs 16.1) | +0.49 → +1.00 calls |
| N = 100 | 21.26 vs 25.59 | 14.51 vs 16.56 | −4.34 → −2.04 |
| rest | 36.07 vs 35.63 | 24.10 vs 23.44 | +0.44 → +0.65 |

About a third of the counted "re-fetches" are writes.

**Subagents, pooled (21 boundaries).**
- K1's shapes with writes out, N=100: 22.3 per 100 against 8.1 to 11.4; the excess is +10.8 to +14.1, with intervals clear of 0.
- K1's shapes plus the strict set, N=100: +14.8 to +18.8 per 100, about +10 to +13 calls and +19k to +23k tokens per boundary.
- §10.6's "subagents lose more" stands and is understated.

## Item 4: the miss (main, 1M class)

**Classes of the missed tokens:**

| window | total | identifiers | paths | numbers | hex | lowercase alphabetic words | numbers of up to 4 digits |
|---|---|---|---|---|---|---|---|
| N = 20 | 10,400 | 72.6% | 14.3% | 12.1% | 1.0% | 47.4% | 11.1% |
| N = 100 | 36,447 | 73.3% | 12.5% | 13.0% | 1.1% | 46.6% | 12.0% |
| rest | 49,763 | 73.1% | 12.3% | 13.5% | 1.1% | 46.3% | 12.5% |

The lowercase alphabetic words are English prose words; they sit inside the identifier class.

**How much looks incidental** (a second pass counted, for each missed token, how many of the 140 segments hold it; `rest` window):
- 56.2% of the missed tokens appear in half or more of all segments.
- 73.3% appear in a quarter or more.
- Only 1.9% appear in two segments or fewer.

**Missed paths.** Only 2.0% (N=20), 1.4% (N=100) and 1.3% (rest) name a file the pre segment read or edited. The report says "1% to 4%".

**Does the miss predict the re-fetches? No.**
- Spearman between missed tokens and re-fetch calls per boundary: +0.12 (N=20), +0.17 (N=100), +0.44 (rest).
- Per request at `rest` it is −0.02, so the `rest` value is a window-length effect.
- Spearman between missed paths and `read_known_path`: +0.04, −0.26, −0.26.

The P1 miss here counts shared vocabulary, not loss.

## Item 5: the cost model

**Reproduction.** My own re-implementation matches every row: 427, 278, 206, 164, 136 and 119 compactions, with the same mean fills and cache reads. K = 119,624.9 from 121 segment starts, 122 included segments, 20,585 steps (11 negative), and all 16 subagent files match.

**Not tuned, but a weak calibration.**
- 785k comes from the K1 brief's `COST_POINTS`, and K is measured, so nothing is tuned to the answer.
- The count is nearly an identity: total growth / (785,000 − K) = 80,160,616 / 665,375 = 120.47.
- **X sweep:**

  | X | 740k | 750k | 760k | 770k | 775k | 780k | 785k | 790k | 800k | 830k |
  |---|---|---|---|---|---|---|---|---|---|---|
  | compactions | 128 | 125 | 124 | 121 | 120 | 120 | 119 | 118 | 116 | 112 |

- **K sweep at 785k:**

  | K | 100k | 110k | 119.6k | 130k | 140k |
  |---|---|---|---|---|---|
  | compactions | 115 | 117 | 119 | 120 | 123 |

- The observed compaction points have a mean of 777,890 and a median of 780,667.
- Each subagent file matches its observed count at every X from 740k to 785k, so the "exact on 16 files" agreement cannot discriminate.

**Constant growth per request fails in the data.**
- By position since the segment start: 6,202 tokens per request in requests 0–19 (median 2,612), 4,310 in 20–99 (median 1,891), 2,830 after (median 1,509).
- By fill bin: 6,179 at 100–200k and 3,214 to 4,072 above 200k.

**A position-aware variant.** It scales each step by the mean growth of its modeled position over that of its observed position, and it is equally calibrated (122 against 121 at 785k).

| X | 300k | 400k | 500k | 600k | 700k | 785k |
|---|---|---|---|---|---|---|
| compactions, position-aware (flat) | 589 (427) | 354 (278) | 247 (206) | 187 (164) | 146 (136) | 122 (119) |
| cache reads, position-aware (flat) | 4.15B (4.10B) | 5.30B (5.17B) | 6.46B (6.19B) | 7.62B (7.23B) | 8.84B (8.27B) | 9.84B (9.24B) |

The 500k-to-785k cache-read ratio is 0.66, against 0.67 flat, so "a third lower" holds.

**Calibration against the session's actual usage records** (20,586 included requests):

| measure | actual | flat model at 785k |
|---|---|---|
| cache reads | 9,552,612,747 | 9,244,750,496 (−3.2%) |
| cache writes | 124,444,652 | 93,190,429 (−25%) |
| mean context | 470,094 | 453,578 (−3.5%) |

**K against the pre fill.** The slope is 0.26 with r = 0.25 over 121 boundaries (pre fill 611k to 796k). The stated assumption that K does not depend on X is untested below 611k.

## Item 6: mutation

**The builder's 15 mutants.** Each was applied verbatim from the test file's own `MUTANTS` table to a scratch copy, then the normal tests ran (`test_mutant_is_killed` deselected). All 15 are FAILED tests, each at its named check's test or more:

| mutant | FAILED test |
|---|---|
| kept-start-ignored | rc_counts_a_missed_token…, rc_counts_each_refetch_shape… |
| window-one-request-long | rc_counts_a_missed_token… |
| read-shape-takes-any-read | rc_counts_each_refetch_shape… |
| miss-check-dropped | the_run_stops_when_accounting_miss_disagrees |
| pseudo-gap-ignored | the_control_takes_the_middle…, the_summary_pools… |
| control-kept-is-empty | the_control_takes_the_middle… |
| reread-ignores-edits | quality_signals_per_bin_and_third |
| rerun-ignores-edits | quality_signals_per_bin_and_third |
| gate-marker-anywhere | quality_signals_per_bin_and_third, the_summary_pools… |
| error-gate-without-an-error | quality_signals_per_bin_and_third, the_summary_pools… |
| compaction-at-X-not-past-it | the_simulation…, the_cost_model… |
| compaction-resets-to-zero | the_simulation…, the_cost_model… |
| small-window-segments-included | the_cost_model… |
| pin-keeps-a-cut-record | a_pin_stops_at_a_record_boundary |
| select-by-text-match | select_takes_parsed_boundaries… |

**22 new mutants, one per clause no row covers.** For each survivor I ran a live differential: the mutated `compaction.py` over three multi-boundary subagent files (and, for N09, N10 and N15, over main), with its JSON compared section by section against the committed JSON.

| id | clause | result |
|---|---|---|
| N01 | drop the `/tasks/`+`.output` marker group | survives; changes rc and cost model (a4920, ac753) |
| N02 | a marker group matches on any string, not all | survives; rc (all 3) |
| N03 | drop `_names_file`'s suffix clause | survives; rc (a88c) |
| N04 | read-before loses its edited-first exclusion | survives; rc (a88c, a4920) |
| N05 | reused ignores history | survives; rc (all 3) |
| N06 | miss ignores history | survives the tests; the runtime guard stops the run (345 vs 365) |
| N07 | look kinds without assistant text | survives; rc and cost model (all 3) |
| N08 | the control's pre facts include the split request's output | KILLED |
| N09 | R-B keeps its re-read/re-run state across a boundary | survives; R-B bins and thirds on main |
| N10 | R-B keeps `<synthetic>` records | survives; R-B requests, bins and thirds on main (50 synthetic records) |
| N11 | the last usage record defines the fill | survives; equivalent on 3 files; main not run |
| N12 | the re-read key ignores offset and limit | survives; R-B (all 3) |
| N13 | R-B reads both threads | survives; equivalent (no other-thread record) |
| N14 | no zero step across an observed compaction | survives; cost model (all 3) |
| N15 | a negative step writes | survives; cost-model rows on main |
| N16 | the excess is real plus control | survives; cost-model loss (all 3) |
| N17 | thirds reversed | KILLED |
| N18 | the re-injected count takes any known read | survives; rc and control (a88c, ac753) |
| N19 | rerun matching without whitespace folding | KILLED |
| N20 | the control class is always 1M | survives; equivalent |
| N21 | postTokens ignored | survives; rc (all 3) |
| N22 | K from all included segments | survives; cost model (all 3 subagent files) |

Totals: 3 killed, 19 survive. Of the survivors, 15 move real outputs, N06 is caught only at run time by the guard, and 3 are equivalent on the pinned data.

## Item 7: Python 3.11 and 3.12

`compaction.py` itself re-ran into scratch: `select` with the builder's measured sizes, 17 `run`s, and `summary --stamp 2026-09-29T03:07:18Z`.
- Under 3.11.15 and under 3.12.3, 19 of 19 files are byte-identical to the committed outputs and to each other.
- `select` found 0 subagent files that hold a boundary now but were not pinned.

## Finding inventory (no severity filter)

**F1. INFO: reproduction exact.**
- **Evidence:** VERIFIED (items 1 and 7, the gates, the probe).
- **Contract mapping and path:** all items; the canonical path.
- **Material effect:** none.

**F2. FOLLOW-UP: the `search_*` shapes count writes as re-fetches.**
- **Status:** it meets all five D-031 conditions but is not core-blocking under D-034, since the sign of K1's conclusion holds within its own shapes. I recommend folding it into F3's repair.
- **Evidence:** VERIFIED.
- **Contract mapping:** K1 brief item 3, "a search of the transcript, the ledger or the live-state". Design §10.2 says "the ledger searched". An edit or a commit is not a search.
- **Canonical path:** `_shape` marks any call whose input names the file.
- **Material effect:** about a third of all counted re-fetch calls on main are writes. The committed report's "ledger reads" are 45% writes. The N=20 comparison moves from 26.4 vs 23.9 to 21.1 vs 16.1, and the N=100 excess from −4.34 to −2.04 calls.
- **Reproduction:** red test R1 below. It fails on the committed module with `assert (4, 1) == (1, 0)` and passes on the discriminator copy. The live differential is in item 3.
- **Suggested fix:** classify each search-shape call's direction; count reads only; report writes separately.

**F3. CONTRACT-DEFECT: the contracted re-fetch shapes cannot see this session's dominant re-fetch forms.**
- **Evidence:** VERIFIED. The missed-shape counts come from my reader, which matches `compaction.py` exactly on the contracted shapes.
- **Contract mapping:** K1 brief item 3's shape list (a Read, an identical command, a search), which the builder implemented faithfully.
- **Canonical path:** red test R2 below. A file Read before the boundary, then `sed -n` viewed and `git log` repeated after it, counts `0 == 2`.
- **Material effect:**
  - The R-C evidence understates a compaction's cost five to seven times in the first 20 requests (item 3).
  - It reverses the sign over 100 requests.
  - It contradicts §10.6's stated reason: ledger reads rise 4 to 10 times and live-state reads 9 times, against the controls.
  - R-C is also §10.3's planned score for packs and Jev (K6). A score blind to Bash re-views would mis-score the preventable re-fetches.
- **Amendment to consider:** add the strict shapes (and consider the loose ones); exclude writes; report the requests-20–99 window; add a sliding or paired control; then re-measure.

**F4. INFO: the control question.**
- **Evidence:** VERIFIED.
- **Answer:** robust across C1, C2, C3 and C5 within K1's shapes (item 2).
- **Material effect:** none by itself.

**F5. FOLLOW-UP: the cost model.**
- **Evidence:** VERIFIED; the price ratios are ASSUMED as K1's.
- **What is off:** a calibration with little power, constant growth refuted, compactions at low X undercounted by 20% to 38% (position-aware), cache writes 25% low at 785k.
- **Contract mapping:** K1 item 6 asks to "state every assumption", and it does. So this is not a contract violation.
- **Suggested fix:** model growth by position since the last compaction; calibrate on the actual cache reads and writes, not the count.

**F6. INFO (for the design): the P1 miss is mostly shared vocabulary and does not predict re-fetching (item 4).**
- **Evidence:** VERIFIED.
- **Material effect:** §10.6's "modeled missed tokens grow with the count" is not a loss measure.

**F7. FOLLOW-UP: 19 of 22 new mutants survive; 15 change real outputs (item 6).**
- **Evidence:** VERIFIED.
- **Contract mapping:** K1's item-level "named mutant per item" is met.
- **Suggested fix:** add fixture cases for each surviving clause:
  - a `prompt_snapshot` in the R-C fixture;
  - a `/tasks/…output` call;
  - a relative path token;
  - a path both read and edited;
  - a boundary and a synthetic record in the R-B fixture;
  - a negative step;
  - assertions on the excess, on postTokens and on K.

**F8. INFO: D2's pre side is immaterial.**
- **Evidence:** VERIFIED.
- **Measurement:** 138 tail calls over 121 boundaries. Holding them leaves the re-fetch counts unchanged (638, 2,572, 4,365) and raises the miss by about 2%. The post segment's own tail adds 137 calls (0.6%) to `rest`.

**F9. INFO: one report number is imprecise.** "1% to 4%" of missed paths should read 1.3% to 2.0% on main's 1M class.

**F10. INFO: stale context.** Three places quote the numbers and the reading that F2 and F3 correct:
- `docs/research/findings/jev-trim/D105-DESIGN-v1.md` §10.6, lines 349–368;
- `todo/BUILD-TASKLIST.md:1746`, the K1 landing entry ("no higher than the control after that … moving the point down is cheap");
- `tasks/briefs/jev-trim/K1-COMPACTION-LOSS-report.md` line 26.

Update them after you act on F2 and F3.

**F11. INFO: hostile inputs are handled.**
- **Evidence:** VERIFIED.
- **Measurement:** NaN, Infinity and float usage values are refused as malformed (3). A NaN `postTokens` becomes `null`. Garbage lines and a truncated tail are unparseable (2). No NaN or Infinity reaches the JSON or SUMMARY.md.
- **One gap:** a `--pin` beyond the file size is not flagged.

**F12. INFO: the kept start's modeled 58,273 against postTokens 24,349 (D7) was not re-derived further.**

## §10.6: does its reading stand?

**No, not as written.**
1. **"26.4 against 23.9 in the first 20 requests":** with writes out and the missed shapes in, the rate is 36.3 against 19.8 to 23.7 per 100. That is +2.5 to +3.3 calls and about +7k tokens per boundary.
2. **"None above the control after that (21.9 against 25.6 over 100)":** the negative gap is the writes. Over 100 requests the corrected excess is +1.5 to +3.7 per 100 (strict) or +4.8 to +9.2 (loose). In requests 20–99 alone it is about 0 under the strict set and +1.9 to +5.6 under the loose set.
3. **"Because the ledger, the live-state block and the start hook restore its state":** the session re-reads the ledger 4 to 10 times and live-state about 9 times its normal rate, and re-views known files through Bash 2.8 times.
4. **What this verify does not refute (INFERRED, a back-of-envelope at K1's price ratios):** in tokens the extra re-fetching is about 7k to 17k per compaction.
   - At 500k, the 87 to 125 extra compactions add about 0.6M to 2.2M re-fetched tokens against a modeled cache-read cut of 3.05B to 3.38B.
   - Even re-read on every later request, that is under a tenth of the saving.
   - So "moving the point down is cheap in cache terms" may survive. But its stated basis is false, and the count at 500k is more likely about 247 than 206.
   - Re-derive the choice from the corrected counts.

## Red tests and discriminator (the scratch copies are removed; the code is here)

Fixture builders `Tx`, `call` and `step` come from `tests/test_jev_trim_replay.py`. The modules come from the repo's `scripts/`.

```python
def _tool(tx, context, name, body="ok", **tool_input):
    tid = tx.tool_id(); tx.request(context, [call(tid, name, **tool_input)], output=10, thinking=0); tx.results((tid, body))

def test_a_write_is_not_a_search(tmp_path):                 # R1 (F2): committed -> (4, 1)
    tx = Tx(); tx.user("go"); _tool(tx, 10000, "Read", "a", file_path="/w/lib/a.py")
    for j in range(3): step(tx, 11000 + j)
    tx.boundary(summary="a summary", post_tokens=500)
    _tool(tx, 20000, "Edit", "ok", file_path="/w/todo/BUILD-TASKLIST.md", old_string="a", new_string="b")
    step(tx, 20100, command="bash scripts/safe_commit.sh -m m todo/BUILD-TASKLIST.md")
    step(tx, 20200, command="python3 scripts/anchor_edit.py todo/BUILD-TASKLIST.md --insert-after A B")
    _tool(tx, 20300, "Edit", "ok", file_path="/w/wiki/topics/live-state.md", old_string="a", new_string="b")
    step(tx, 20400, command="grep -n TASK todo/BUILD-TASKLIST.md")        # the only search
    for j in range(4): step(tx, 21000 + j)
    path, size = tx.write(tmp_path / "t.jsonl")
    (row,) = compaction.compaction_loss(replay.build(path, size))["boundaries"]
    w = row["windows"]["20"]["refetch"]
    assert (w["search_ledger"]["calls"], w["search_live_state"]["calls"]) == (1, 0)

def test_a_bash_view_of_a_file_read_before_is_a_refetch(tmp_path):   # R2 (F3, the amendment): committed -> 0
    tx = Tx(); tx.user("go"); _tool(tx, 10000, "Read", "body", file_path="/w/lib/core.py")
    step(tx, 10500, command="git log --oneline -5")
    for j in range(3): step(tx, 11000 + j)
    tx.boundary(summary="a summary", post_tokens=500)
    step(tx, 20000, command="sed -n '1,40p' /w/lib/core.py"); step(tx, 20100, command="git log --oneline -3")
    for j in range(4): step(tx, 21000 + j)
    path, size = tx.write(tmp_path / "t.jsonl")
    (row,) = compaction.compaction_loss(replay.build(path, size))["boundaries"]
    assert row["windows"]["20"]["refetch_total"]["calls"] == 2
```

Run it with `python3 -m pytest -q -p no:cacheprovider --basetemp=<scratch> <file>`. On the committed module the result is `2 failed`. The discriminator, for the item 3 live differential, is one guard at the top of `_shape`'s marker loop: if the call is an edit tool, or a Bash write or commit by the direction rules in item 3, return None.

## Reproduced, reviewed statically, skipped

**Reproduced (run this session):** everything above.

**Reviewed statically:** `compaction.py`, the test file, `replay.py`'s timeline semantics, `jev_pipes` and the probe.

**Skipped, with reasons:**
- Rounds 1 and 2 byte identity: not in this brief; their tests pass.
- The per-model R-B table: in the JSON only.
- By-kind removed tokens: only the totals were compared.
- N11 on main: equivalent on three files.
- The builder's timing and RSS claims.
- Any PC run: the brief's boundary.

**Inferred, not measured:**
- the §10.6 token arithmetic;
- that the post-boundary excess is caused by the compaction (a control comparison, not an intervention);
- the direction classifier's accuracy on real commands (checked on synthetic cases only).

## Cleanup and boundary

- `/tmp/vk1` (22 MB) and `/tmp/vk1-premise-bt` are removed, and no process of mine remains.
- I wrote no bytecode into the repo: nothing in its `__pycache__` directories is newer than my first scratch file.
- The tracked tree holds none of my changes. The untracked `tasks/briefs/jev-trim/K2-FILE-PACKS-brief.md` and `k2_authoring_probe.py` are not mine.
- I wrote an `S1-RATE` line for each of the 18 `[S1 …]` injections at the time it arrived.
