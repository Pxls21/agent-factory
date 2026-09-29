> Coordinator note (2026-09-29 01:5xZ): the report of record, extracted by `scripts/stack.py harvest` (the lane's report-file write is refused for subagents). Served model: claude-opus-5-5 on all 672 assistant records, 0 refusal stops; `report_lint` 0 refs. The worker restart of about 01:13Z stopped the lane between tool calls; it was resumed by message. D-106 (the owner, 00:51:42Z) dropped the trimmer for this Claude Code session after this round was dispatched, so these numbers are the record and an input to the compaction work; DEV-1's reading feeds no build.

# T0-REPLAY round 2 report (task #346, D-105)

Written 2026-09-29, final `date -u` 01:55:41Z. Contract: `tasks/briefs/jev-trim/T0-REPLAY-R2-brief.md`. There is no design recommendation.

## Answer first

- **The grid is complete under two readings of "the segment's first user message". The headline depends on which reading applies, so I report both and escalate the choice (DEV-1).**
- **`record`** is round 1's reading and the default, following the brief's "the other protected kinds stay". Only the segment's first user text record is protected.
  - 19 cells hold the median at or under B. All are at B = 200,000 with R1-R6.
  - 17 of them are on main per-request (medians 191,947 to 198,622). 2 are on sub-a88c7c57f2fa2a96b (198,990 and 199,143).
  - No cell holds at B = 100,000 or 131,072, and no cell holds on main between-turn, sub-a4920ba3ae772b9d0 or sub-ac753871198ee8cfd.
- **`group`** protects every item before a segment's first request. This is the reading I built first. Under it, **0 cells hold on any run.**
- **Cache cost of the 17 main rows:**
  - Only one saves cache under the pessimistic bound: L 120,000, A 10, K 3, R1-R6, cooldown:30. Its net is −20.1% at read 0.05 and −36.5% at read 0.1.
  - The other 16 cost +16.2% to +500.6% of the real session under that bound at read 0.05.
  - Under the edit-point model, 10 of the 17 are savings at read 0.05.
- **The pessimistic bound's fixed start changed mid-round.** My first definition produced an impossible value. Both states are reported (DEV-2).
- **The reach guard almost never fires.** Under `record`, 54 to 64 of the 72 reach cells per run never trim. Under `group`, it is 68 to 72 of 72.

## NOT done

1. No design recommendation, by instruction.
2. No git writes. My files are uncommitted:
   - `scripts/jev_trim/replay.py` and `tests/test_jev_trim_replay.py` (modified);
   - `docs/research/findings/jev-trim/replay-2026-09-29/` (new, untracked).
3. The `record` grids ran only with the final fixed start. State A (the audit's definition) exists only for the `group` grids, saved in scratch at `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/t0r2/state-a/`, not in the repo.
4. The subagent files' under-recorded usage (round 1's D6) is not corrected. The subagent results carry it (D3).
5. The live prompt-caching page was not fetched, because network calls are forbidden. The cache ratios remain UNSURE parameters, as in round 1.
6. No PC gate was run, since the PC bridge is off-limits. The gates ran in the sandbox only.
7. The verification and sensitivity scripts are in scratch only (`.../scratchpad/t0r2/*.py`).
8. Nothing was built for round 3 (the coordinator's D-106 message).
9. The round-2 directory holds no cross-check. The brief did not ask for one; round 1's cross-check stands.

## Deviations (flagged)

**DEV-1: ESCALATION. A reversal inside this round: the reading of "the segment's first user message".**
- **State 1 (built first):** protect every item that entered before a segment's first request.
  - Basis: the harness sends that whole group as one user message in the API request.
  - I ran the full grid this way twice (01:05-01:12Z and 01:19-01:25Z).
- **State 2 (the final default):** protect only the first user text record, as round 1 did.
  - Basis: the brief's "The other protected kinds stay (typed text, the segment's first user message, the newest copy of each skill body)". "Stay" means round 1's set, and round 1 protected only the first user text record.
- **Why it matters:**
  - On main, the opening group weighs 68,824 to 84,734 modeled tokens per segment: invoked_skills 28k, CLAUDE.md "instructions" 15k, deferred_tools_record 13-14k, listings, the summary and file re-reads.
  - Under `group`, all of it is floor.
  - Under `record`, R6 takes all of it except the skill bodies and the summary, once older than A.
- **Found by** a scratch sensitivity run, then confirmed on the full grids.
- **What I built:**
  - A `Cell.opening` field (`record` or `group`) and a `--opening` flag (r2 only; default `record`; refused on r1 with exit 2).
  - The full grid under each reading: `run-<label>.json` is `record`; `run-<label>-opening-group.json` is `group`.
  - Tests and mutants for both readings.
- The coordinator chooses the reading. I recommend nothing.

**DEV-2: the pessimistic bound's fixed start changed mid-round.**
- **State A (first build):**
  - Fixed start = first context − the compaction's postTokens (the audit's §3.3). A segment without a compaction borrowed another segment's value.
  - Defect: sub-a88c segment 0 got 72,882, which is more than that segment's whole first context of 67,237.
- **Evidence against state A:**
  - The prompt_snapshot records (system prompt + tools) hardly change within a file: main 173,066 to 179,701 characters; each subagent 117,820 to 118,936.
  - Yet the postTokens-based value varies by up to 10,408 tokens between segments of the same agent (a88c: 72,882, 62,474, 64,043).
  - The audit's own §3.3 notes that the start messages it modeled exceed postTokens.
- **Final state:** fixed start = the lower of (first context − modeled opening items) and (first context − postTokens). The lower value makes the bound rewrite more, so it stays pessimistic. The modeled estimate is the lower one in all 17 segments.
- **Effect:** in the `group` grids, only `cache_pessimistic*` and `composition_at_median` changed. 0 of the 1,440 cells differ in any other field (verified). The best-row nets under both states are in the cache table below.

**DEV-3: main is written as two runs per reading, one per mode (288 cells each).** I split it before timing; the runs took 88 to 167 s each. Together the two files hold the 576-cell grid. The best rows are therefore per mode.

**DEV-4: the reach guard is an exact probe, not archive-then-undo.**
- `ReachProbe` uses four disjoint Fenwick trees and answers in O(log n) before anything is archived.
- An undo would repeat a full pass at every blocked check point: 1,898 main requests × 144 reach cells.
- The probe's semantics equal the greedy pass with no target, by construction and by check (self-attack 2).

## Premise re-run (item 1): about 00:27Z, all matched, no CONTRACT-INVALID

```
PIN-is-an-ancestor-of-HEAD
T0-REPLAY round 1 (task #346, D-105): the replay tool, its tests and outputs; the first rule set misses the budgets
ff35dbb8541818bd  scripts/jev_trim/replay.py
92b29e6d5b364b43  tests/test_jev_trim_replay.py
0
ls: cannot access 'docs/research/findings/jev-trim/replay-2026-09-29': No such file or directory
(the jev_pipes diff printed nothing)
78 passed
2 files set=5365c5f240ce
```

HEAD was the commit "D-105 design corrected by T0 round 1; the T0 round-2 brief (task #346), dispatched" then, and the commit "env-tool-quirks: a re-landed evidence set is the prior mint's file list; the task view names a task from its first body mention" now (the coordinator's commits; coordinator note: local ids the push rewrites, replaced by their subjects). `git status --porcelain` over my lane's paths, both output directories, `scripts/jev_pipes/` and `tests/test_jev_pipes_replay.py` shows only my three paths.

## Files

| path | action | lines | sha256 |
|---|---|---|---|
| scripts/jev_trim/replay.py | MODIFY | 1,799 (round 1: 1,266) | 73a16e72ed933db5c1771dc3bcc10bfca2b1bf2f479767dffeb4ecd86d154216 |
| tests/test_jev_trim_replay.py | MODIFY | 1,357 (round 1: 833) | d17f19c859ed3727c9d59378d2c81e645623c0198d180fa6c189f51af553931f |
| scripts/jev_trim/__init__.py | unchanged | 5 | (round 1's) |

The outputs are all written by replay.py into `docs/research/findings/jev-trim/replay-2026-09-29/`: 11 files, 17M in total.

| file | lines | sha256 |
|---|---|---|
| SUMMARY.md | 6,567 | ae8eaaae78ae62ec425a5946dd9847e42fd5b923c7feaf20354eb62da185ecf4 |
| run-main-between-turn.json | 78,808 | 95ef2a926d840ab0a8d23f853125a146ccdae73bb3f6abc006f041d921db927d |
| run-main-per-request.json | 81,191 | b013f87c38a850aac3e83068beb785d5288aec94506c4d8c97503fe4773f66d4 |
| run-sub-a88c7c57f2fa2a96b.json | 70,450 | 386c9572c6fd7ec604fd793acfd0becbace5cabde0645cbb1c1365d33acf5d12 |
| run-sub-a4920ba3ae772b9d0.json | 68,371 | bb8b01d74e82840a84751d1cb84c71684c15984f1370015d00f3e4ba586145f9 |
| run-sub-ac753871198ee8cfd.json | 69,311 | 6141a1007e353a081c57e2bdd4eccb6c8010c58d23ec2450473b8b18f8879ceb |
| run-main-between-turn-opening-group.json | 76,929 | 5761294eaff40e174944b41cabc14843563f63c5f0316789d67c1424651dcc77 |
| run-main-per-request-opening-group.json | 78,882 | 63f583d4969254b498aada45e0d7fecae8da70725ed802d92480ee346d84449e |
| run-sub-a88c7c57f2fa2a96b-opening-group.json | 68,462 | de4e8c5045130fe141bd45dd347ee0d34acd952993723a7a8c012646e0d79b3c |
| run-sub-a4920ba3ae772b9d0-opening-group.json | 66,282 | 2303aff518638a028b90d49e1c8fe828cd627a0561a76f2d7374eba55fbd24be |
| run-sub-ac753871198ee8cfd-opening-group.json | 67,797 | b6d7847a65975fa9bdf63b806b7866b36f9368faf2e732e8b9d53dc0b928ecc6 |

**Pins:** main 780,424,880 from offset 740,755,248; the three subagent files at 14,082,496, 11,814,169 and 9,235,269; all with `--modes per-request` except main.

**Determinism:** a re-run of the `sub-ac75` grid wrote identical bytes (37fd7e09..., before the final opening change).

**What changed in replay.py, by brief item.** Every round-2 semantic is gated on `Cell.version >= 2` or on an r2-only flag.
- **Item 2:**
  - The r2 grid uses `unit="request"` with K in {3, 10, 30}.
  - Version-2 between-turn check points are stop-hook turn starts (`check_unit = "stop" if v2`).
  - `Item.start`; `protected_kind_of(cell)`.
- **Item 3:** `ENVELOPES`, `_envelope`, `_handback`, `_attachment_handback`, `Index.r5`.
- **Item 4:** `ATTACH_KEY_FIELDS`, `_attach_key`, `Index.r6` / `supersedes6`, the R6 heap.
- **Item 5:** `GUARDS`, `ReachProbe`, the cooldown check (per segment).
- **Item 6:**
  - The trim record's `extra_write_tokens_pessimistic`.
  - `Segment.fixed_start`, `fixed_source`, `fixed_estimates` and `snapshot_chars`.
  - `cache_terms(key=)`.
- **Item 7:** `composition()`.
- **Item 8:**
  - `grid_r2`, `--grid r2`, `--opening`.
  - Schema-2 run fields: `recognition` and `fixed_start`.
  - `write_summary_r2` and `best_rows`.
  - `write_summary` dispatches on the runs' schema and refuses a directory that mixes rounds.

## Gates (item 9): final code, 01:52:44Z to 01:53:49Z, `--basetemp` a pytest argument under the scratchpad

```
1 files set=1bb7608ed22a
pytest-summary: 68 passed in 7.33s
pytest-summary: 68 passed in 8.05s
1 files set=17f6a5adc0c9
pytest-summary: 42 passed in 24.47s
pytest-summary: 42 passed in 24.06s
```

Other checks:
- **pyflakes:** clean on both files.
- **Separator bytes:** 0 in both files and in SUMMARY.md.
- **`ap_screen.py` on replay.py:** 3 hits, the same three round-1 lines (AF-AP-72 twice, AF-AP-40 once).
- **`--tests` screen:** 3 AF-AP-80 hits. Two are round-1 lines. One is new: the round-2 secret test's check that the fixture holds the value. It follows the round-1 pattern: a data check paired with the `_hidden` property check.
- **Red-green:** the new tests ran green first against the built code. The red side is the mutant table below. I did not run the new tests against round 1's code.

## Mutants: 23, all killed

Each one fails its check with AssertionError at the line of `tests/test_jev_trim_replay.py` named here. Round 1's nine are still killed: age-boundary-off-by-one (241), between-turn-fires-inside-a-turn (328), hysteresis-stops-at-B-not-L (310), kept-item-check-dropped (422), protected-set-ignored (367), stub-dropped-with-its-pair (385), supersede-keeps-the-oldest (275), thinking-before-the-current-turn-ignored (296), trim-fires-at-B-not-past-it (309).

| item | mutant | killed at |
|---|---|---|
| 2 window | check-points-follow-the-protection-unit (`check_unit = cell.unit`) | 463: trims only at stop-turn starts |
| 2 window | window-one-request-short (`cur - cell.k + 1`) | 467: `mark[2] - it.req > k` |
| 2 kinds | opening-group-not-protected (`group` drops `item.start`) | 499 |
| 2 kinds | record-reading-protects-the-group (always the group test) | 511 |
| 3 R5 | r5-envelope-anywhere (tag anywhere, not opening) | 541: recognition dict (negative control) |
| 3 R5 | hand-back-protected-as-typed-text | 548: the archived set |
| 4 R6 | r6-key-ignored (`_attach_key` returns the type only) | 582: `{a1, d1}` |
| 4 R6 | skill-body-not-protected | 585 |
| 5 guard | reach-guard-never-blocks | 598: trims `[(7, 3)]` |
| 5 guard | reach-probe-ignores-the-window (`max_gain(entered, ...)`) | 598 |
| 5 guard | cooldown-off-by-one (`<=`) | 613: trims `[2, 5, 8, 11]` |
| 6 cache | pessimistic-bound-uses-the-edit-point | 634: 1,817 |
| 6 cache | fixed-start-takes-the-larger-estimate (`max(candidates)`) | 874 |
| 7 comp. | composition-before-trimming | 654: by-kind after the trim |

## Round 1 stays byte-identical

- **Golden test** `test_round_one_outputs_stay_byte_identical`: round 1's command lines on the rich fixture write run-d.json 234fdcb5f4c1567358e568eebab0b4abcd59c200c588df57ef9bc3ba4da5b1e6 and SUMMARY.md c31ff84313887b019a70097d39f138a5a4cfbd65ce83973a14473131297dd812. The committed round-1 file (aed7d82, ff35dbb8), run from git, writes the same two hashes (verified).
- **Full re-run** of round 1's real commands with the final code (01:50 to 01:52Z), compared with `sha256sum -c` against `replay-2026-09-28/`: 8 of 8 OK. The committed directory is unmodified (0 porcelain lines).

## Per run: rows holding the median at or under B, and the best row per budget

**Criteria**, stated in SUMMARY.md:
- **C1:** the lowest median active context (ties: the lower pessimistic net at read 0.05, then fewer UAA@H).
- **C2:** among rows holding the median at or under B, the lowest pessimistic net at read 0.05.
- **C3:** among rows holding the median at or under B, the fewest UAA@H.

**Columns:**
- **E / P** = net share of the real session's cost under the edit-point model / the pessimistic bound, each shown at read 0.05 / read 0.1. Below zero is a saving.
- **UAA** = use-after-archive (round 1's definition, a lower bound).

### `record` reading (the default)

**main between-turn** (real median 454,522): 0 of 288 hold, so C2 and C3 are empty.

| B | C1 row | median | p90 | >B | trims | E | P | archived | UAA@20 | UAA@H |
|---|---|---|---|---|---|---|---|---|---|---|
| 100,000 | L 75,000 A 10 K 3 R1-R6 none | 234,827 | 337,743 | 1,898 | 114 | −28.9% / −37.3% | 19.0% / −11.5% | 3,881 | 156 | 549 |
| 131,072 | L 98,304 A 10 K 3 R1-R6 none | 234,827 | 337,743 | 1,877 | 112 | −29.0% / −37.4% | 18.6% / −11.7% | 3,881 | 156 | 549 |
| 200,000 | L 150,000 A 10 K 3 R1-R6 none | 236,644 | 337,743 | 1,436 | 79 | −29.7% / −37.5% | 6.8% / −17.8% | 3,881 | 158 | 542 |

**main per-request:** 17 of 288 hold, all at B 200,000 with R1-R6.

| L | A | K | guard | median | p90 | >B | trims | blocked | E | P | archived | UAA@20 | UAA@H |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 120,000 | 10 | 3 | none | 191,947 | 243,333 | 654 | 728 | 0 | −1.9% / −27.8% | 397.0% / 187.5% | 4,154 | 190 | 669 |
| 120,000 | 10 | 3 | cooldown:10 | 192,327 | 249,763 | 751 | 121 | 685 | −35.3% / −45.6% | 16.2% / −17.7% | 4,107 | 193 | 671 |
| 150,000 | 10 | 3 | none | 193,034 | 243,333 | 654 | 734 | 0 | 1.4% / −25.7% | 400.7% / 189.8% | 4,169 | 198 | 662 |
| 150,000 | 10 | 3 | cooldown:10 | 193,711 | 249,872 | 758 | 126 | 691 | −32.2% / −43.5% | 19.2% / −15.8% | 4,118 | 212 | 669 |
| 120,000 | 10 | 10 | none | 193,952 | 247,686 | 702 | 782 | 0 | 18.4% / −16.5% | 436.2% / 209.0% | 4,129 | 198 | 675 |
| 150,000 | 10 | 10 | none | 193,976 | 247,686 | 702 | 784 | 0 | 20.1% / −15.4% | 437.5% / 209.9% | 4,122 | 186 | 651 |
| 150,000 | 10 | 10 | cooldown:10 | 194,084 | 255,121 | 782 | 128 | 713 | −30.4% / −42.5% | 21.9% / −14.2% | 4,059 | 195 | 655 |
| 120,000 | 10 | 10 | cooldown:10 | 194,452 | 253,943 | 786 | 126 | 716 | −32.1% / −43.5% | 21.1% / −14.8% | 4,090 | 210 | 678 |
| 120,000 | 20 | 3 | none | 195,456 | 251,700 | 791 | 839 | 0 | 44.3% / −2.3% | 477.4% / 231.5% | 4,073 | 176 | 600 |
| 150,000 | 20 | 3 | none | 195,466 | 251,700 | 791 | 841 | 0 | 45.6% / −1.5% | 478.6% / 232.3% | 4,073 | 179 | 589 |
| 120,000 | 20 | 3 | cooldown:10 | 195,772 | 259,642 | 835 | 129 | 756 | −26.8% / −40.3% | 24.2% / −12.8% | 4,008 | 171 | 597 |
| 150,000 | 20 | 3 | cooldown:10 | 195,994 | 258,944 | 835 | 131 | 758 | −25.6% / −39.6% | 24.9% / −12.3% | 4,007 | 165 | 583 |
| 150,000 | 20 | 10 | none | 196,328 | 256,303 | 814 | 861 | 0 | 66.3% / 10.0% | 500.6% / 244.5% | 4,029 | 169 | 599 |
| 120,000 | 20 | 10 | none | 196,731 | 256,303 | 814 | 857 | 0 | 65.2% / 9.3% | 498.7% / 243.3% | 4,029 | 163 | 603 |
| 150,000 | 20 | 10 | cooldown:10 | 197,767 | 263,319 | 880 | 134 | 800 | −22.5% / −37.6% | 29.1% / −9.7% | 3,957 | 161 | 585 |
| 120,000 | 20 | 10 | cooldown:10 | 197,962 | 263,644 | 879 | 133 | 797 | −23.5% / −38.2% | 28.8% / −10.0% | 3,988 | 162 | 590 |
| 120,000 | 10 | 3 | cooldown:30 | 198,622 | 271,586 | 921 | 56 | 899 | −37.9% / −46.1% | −20.1% / −36.5% | 3,897 | 189 | 643 |

main per-request best rows:
- **B 100,000, C1:** L 75,000 A 10 K 3 R1-R6 none. Median 172,477, p90 243,333, >B 1,849, trims 1,801. E 55.5% / 1.6%, P 746.0% / 374.3%. Archived 4,186, UAA@20 206, UAA@H 655.
- **B 131,072, C1:** L 98,304, same row otherwise. Median 172,477, >B 1,544, trims 1,561. E 43.0% / −5.0%, P 696.4% / 347.7%. UAA@H 666.
- **B 200,000:**
  - C1 is the first holding row (median 191,947).
  - C2 is the cooldown:30 row (P −20.1% / −36.5%).
  - C3 is L 150,000 A 20 K 3 cooldown:10 (UAA@H 583).
- C2 and C3 are empty at B 100,000 and 131,072.

**sub-a88c7c57f2fa2a96b** (real median 406,837): 2 of 288 hold, both at B 200,000.
- L 120,000 A 10 K 3 R1-R6 none: median 198,990, p90 404,784, >B 349, trims 350. E 36.4% / 6.6%, P 397.3% / 229.4%. Archived 1,074, UAA@20 75, UAA@H 220. This row is C1 and C2.
- L 150,000 A 10 K 3 R1-R6 none: median 199,143, >B 349, trims 351. E 37.2% / 7.2%, P 397.9% / 229.9%. UAA@20 72, UAA@H 219. This row is C3.

Its best rows at the other budgets:
- **B 100,000, C1:** L 75,000 A 10 K 3 R1-R6 none. Median 196,516, >B 645, trims 620. E 67.3% / 24.5%, P 519.5% / 303.7%. UAA@H 216.
- **B 131,072, C1:** L 78,643 (0.6 B). Median 196,516, >B 549, trims 533. E 59.8% / 20.1%, P 494.9% / 288.7%. UAA@H 218.

**sub-a4920ba3ae772b9d0** (real median 406,015): 0 hold. Every C1 row is A 10 K 3 R1-R6 none, median 257,527.

| B | L | >B | trims | E | P | UAA@H |
|---|---|---|---|---|---|---|
| 100,000 | 75,000 | 607 | 567 | 64.2% / 23.2% | 617.7% / 358.4% | 216 |
| 131,072 | 78,643 | 538 | 510 | 56.5% / 18.7% | 597.7% / 346.4% | 219 |
| 200,000 | 120,000 | 415 | 399 | 40.9% / 9.9% | 532.3% / 307.5% | 225 |

**sub-ac753871198ee8cfd** (real median 459,060): 0 hold. Every C1 row is A 10 K 3 R1-R6 none, median 300,500.

| B | L | >B | trims | E | P | UAA@H |
|---|---|---|---|---|---|---|
| 100,000 | 75,000 | 391 | 343 | 73.5% / 23.5% | 688.3% / 372.2% | 133 |
| 131,072 | 98,304 | 345 | 318 | 65.6% / 19.1% | 671.2% / 362.5% | 133 |
| 200,000 | 120,000 | 250 | 231 | 44.1% / 7.6% | 581.2% / 312.2% | 138 |

### `group` reading

0 of 288 hold on every run. Every C1 row is A 10 K 3 R1-R6 none.

| run | C1 median | example C1 row |
|---|---|---|
| main between-turn | 264,184 (B 100,000 and 131,072); 264,386 (B 200,000) | B 100,000: E −25.3% / −33.0%, P 38.8% / 1.6%, UAA@H 504 |
| main per-request | 211,917 | B 100,000: E 61.2% / 8.6%, P 1,016.8% / 524.5%, UAA@H 591 |
| sub-a88c | 228,622 | |
| sub-a492 | 284,166 | |
| sub-ac75 | 333,644 | |

## Composition at the median request after trimming (item 7)

The parts: active = fixed + protected (of which, in the opening group) + outside every rule + a rule may take later + stubs (count) + unattributed. Floor = fixed + protected + outside + stubs. The full grid's composition is in SUMMARY.md and in the JSON.

| run, row | request | active | fixed | protected (opening) | outside | later | stubs (n) | unattributed | floor |
|---|---|---|---|---|---|---|---|---|---|
| record, main between-turn, B 100,000 C1 | 850 | 234,757 | 63,005 | 39,968 (34,212) | 54,880 | 44,745 | 10,000 (250) | 22,158 | 167,854 |
| record, main per-request, B 100,000 C1 | 1103 | 172,454 | 46,544 | 42,846 (36,901) | 28,019 | 8,709 | 6,960 (174) | 39,377 | 124,369 |
| record, main per-request, B 200,000 C1 | 747 | 191,929 | 63,005 | 39,392 (34,212) | 27,752 | 55,730 | 4,160 (104) | 1,889 | 134,309 |
| record, main per-request, B 200,000 C2 (cooldown:30) | 1821 | 198,620 | 47,236 | 41,244 (34,823) | 3,652 | 95,354 | 0 (0) | 11,133 | 92,132 |
| record, main per-request, B 200,000 C3 | 828 | 195,978 | 63,005 | 40,226 (34,212) | 48,725 | 15,843 | 9,840 (246) | 18,338 | 161,797 |
| record, sub-a88c, B 200,000 C1 | 117 | 198,938 | 32,671 | 35,926 (512) | 23,944 | 29,535 | 6,680 (167) | 70,181 | 99,221 |
| record, sub-a492, C1 | 622 | 257,482 | 36,423 | 10,399 (7,541) | 22,813 | 8,375 | 5,600 (140) | 173,871 | 75,235 |
| record, sub-ac75, C1 | 83 | 300,403 | 32,828 | 45,855 (842) | 11,989 | 1,827 | 3,800 (95) | 204,105 | 94,471 |
| group, main between-turn, B 100,000 C1 | 568 | 264,173 | 61,454 | 73,909 (68,824) | 57,180 | 23,425 | 12,480 (312) | 35,724 | 205,023 |
| group, main per-request, C1 | 796 | 211,906 | 63,005 | 83,323 (74,081) | 39,973 | 3,862 | 7,880 (197) | 13,862 | 194,181 |

By kind at those medians:
- **record, main per-request, B 200,000 C1:** tool_input 41,904; other_attachment 30,286; thinking 23,068; tool_result 16,802; other_user_text 6,589; assistant_text 2,552; task_reminder 1,658; typed 16.
- **record, main between-turn, C1:** tool_input 51,232; other_attachment 32,245; thinking 17,572; tool_result 14,998; assistant_text 8,197; other_user_text 7,864; hand-back 5,729; task_reminder 1,740.
- **group, main per-request:** other_attachment 69,916; tool_input 38,019; other_user_text 6,969; assistant_text 4,738; tool_result 2,749; thinking 2,409.
- **"Outside every rule"** on main is mostly small tool inputs, which R4 never takes at 500 tokens or under, plus assistant text.

## R5 and R6 recognition

The counts are identical under both readings (verified: equal `recognition`, `fixed_start` and `timeline` in all five pairs of files).

**R5 on main: 136 items, all larger than a stub.**

| kind:name:route | items | tokens |
|---|---|---|
| other_attachment:queued_command:structure | 71 | 14,926 |
| other_user_text:peer:structure | 16 | 70,970 |
| other_user_text:task-notification:structure | 29 | 16,802 |
| typed_user_text:queued_prompt:envelope | 20 | 119,238 |

**R5 on the subagents:**
- a492: 2 items (queued_command structure 1, 133 tokens; task-notification structure 1, 301 tokens).
- a88c: 1 item (queued_command structure, 135 tokens).
- ac75: 0.

**R5 negative control** (test `check_r5`): none of these is taken:
- an ordinary typed text;
- a typed text that quotes `<agent-message` in the middle;
- a peer message without the hand-back flag.

**R6 attachment types on main.** Columns: items, modeled tokens, in an opening group, keyed, superseded, hand-back or typed.
- invoked_skills 7, 196,620, 7, 0, 0, 0 (skill body, never archived)
- nested_memory 5, 152,457, 0, 5, 0, 0
- queued_command 100, 137,624, 0, 0, 0, 100
- hook_additional_context 193, 124,441, 7, 193, 164, 0
- instructions 8, 121,822, 7, 0, 1, 0
- deferred_tools_record 414, 106,087, 4, 0, 407, 0
- task_reminder 219, 76,347, 0, 0, 212, 0
- edited_text_file 17, 39,894, 0, 17, 5, 0
- deferred_tools_delta 14, 39,543, 7, 0, 7, 0
- file 18, 32,823, 18, 18, 0, 0
- agent_listing_delta 7, 30,757, 7, 0, 0, 0
- total_tokens_reminder 1,788, 30,211, 0, 0, 1,781, 0
- skill_listing 22, 18,540, 0, 0, 17, 0
- mcp_instructions_delta 7, 17,753, 7, 0, 0, 0
- environment 87, 5,005, 7, 0, 80, 0
- silent_turn_reminder 141, 4,668, 0, 0, 134, 0
- dynamic_skill 1, 2,120, 0, 0, 0, 0
- task_status 17, 1,534, 17, 17, 0, 0
- remote_session_change 7, 731, 7, 0, 0, 0
- session_context 7, 659, 7, 0, 0, 0
- compact_file_reference 14, 463, 14, 14, 0, 0
- model 7, 384, 7, 0, 0, 0
- credential_org 4, 50, 4, 0, 0, 0
- date 8, 28, 7, 0, 1, 0
- auto_mode 8, 19, 0, 0, 1, 0
- auto_mode_exit 2, 0
- command_permissions 3, 0

**R6 on the subagents, the largest types** (items, tokens):
- **a88c:** nested_memory 3, 91,451; instructions 4, 61,061; hook_additional_context 65, 41,470; skill_listing 11, 28,169; deferred_tools_delta 8, 21,732; invoked_skills 1, 20,738; file 7, 15,540; total_tokens_reminder 712, 12,030.
- **a492:** nested_memory 5, 152,559; instructions 3, 45,796; skill_listing 9, 28,011; deferred_tools_delta 6, 16,299; total_tokens_reminder 671, 11,338; hook_additional_context 22, 9,621.
- **ac75:** nested_memory 2, 60,697; instructions 3, 45,796; hook_additional_context 71, 18,861; deferred_tools_delta 6, 16,299; skill_listing 5, 14,203; file 4, 10,556.

## Guards under `record`, per run

Each guard has 72 cells per run.

| run | guard | median range | cells that never trim | E at read 0.05 | P at read 0.05 |
|---|---|---|---|---|---|
| main between-turn | none | 234,827 to 334,554 | 0 | −30.0% to 4.6% | 6.5% to 85.1% |
| main between-turn | reach | 352,290 to 454,522 | 64 | −12.5% to 0.0% | −12.2% to 0.0% |
| main between-turn | cooldown:10 | 237,168 to 336,137 | 0 | −31.3% to −6.6% | −11.3% to 29.0% |
| main between-turn | cooldown:30 | 245,436 to 341,020 | 0 | −31.5% to −10.5% | −19.9% to 9.5% |
| main per-request | none | 172,477 to 286,756 | 0 | −1.9% to 348.7% | 397.0% to 1,441.2% |
| main per-request | reach | 236,820 to 454,522 | 60 | −24.3% to 0.0% | −21.6% to 0.0% |
| main per-request | cooldown:10 | 178,492 to 294,353 | 0 | −35.3% to 17.2% | 16.2% to 127.0% |
| main per-request | cooldown:30 | 198,622 to 309,734 | 0 | −37.9% to −6.2% | −20.1% to 28.4% |
| sub-a88c | reach | (not listed) | 58 | | |
| sub-a492 | reach | (not listed) | 54 | | |
| sub-ac75 | reach | (not listed) | 64 | | |

The subagents' other guards follow the main per-request pattern: none costs most, cooldown:30 least.

**R1-R4 vs R1-R6, guard none, lowest median:** main between-turn 309,934 vs 234,827; main per-request 257,063 vs 172,477; a88c 254,781 vs 196,516; a492 294,775 vs 257,527; ac75 337,972 vs 300,500.

## Fixed start per segment (tokens) and the two cache states

Every segment uses the modeled estimate, the lower of the two.

| file, segment | first context | modeled (used) | first − postTokens | snapshot characters |
|---|---|---|---|---|
| main 1 | 131,080 | 60,978 | 91,471 | 173,066 |
| main 2 | 130,278 | 61,454 | 91,576 | 173,066 |
| main 3 | 137,086 | 63,005 | 94,724 | 173,718 |
| main 4 | 131,279 | 46,544 | 91,232 | 179,701 |
| main 5 | 127,359 | 45,687 | 89,969 | 179,701 |
| main 6 | 129,409 | 46,750 | 91,085 | 179,701 |
| main 7 | 128,688 | 47,236 | 91,115 | 179,701 |
| a88c 0 / 1 / 2 / 3 | 67,237 / 106,725 / 78,052 / 80,827 | 32,671 / 44,725 / 40,812 / 42,329 | none / 72,882 / 62,474 / 64,043 | 117,820 to 118,936 |
| a492 0 / 1 / 2 | 68,088 / 71,164 / 71,059 | 33,027 / 39,005 / 36,423 | none / 59,118 / 59,061 | 118,936 |
| ac75 0 / 1 / 2 | 67,734 / 84,231 / 71,509 | 32,828 / 40,434 / 38,619 | none / 63,709 / 58,744 | 118,936 |

**Pessimistic net at read 0.05 / 0.1, state A vs final** (`group` grids, the C1 row at B 100,000):

| run | state A | final |
|---|---|---|
| main between-turn | 24.7% / −6.0% | 38.8% / 1.6% |
| main per-request | 771.9% / 392.3% | 1,016.8% / 524.5% |
| sub-a88c | 535.6% / 316.2% | 613.9% / 364.5% |
| sub-a492 | 642.4% / 375.7% | 709.0% / 416.1% |
| sub-ac75 | 708.4% / 386.5% | 790.6% / 433.1% |

The best-row choices are identical under both states.

## DISCREPANCIES

- **D1 (escalation, DEV-1): the headline depends on the reading of "the segment's first user message".**
  - `record`: 19 holding cells. `group`: 0.
  - A scratch run of the C1 rows (A 10, K 3, R1-R6, none) under both readings gave these medians:
    - main per-request at B 200,000: 211,917 (group) vs 193,034 at L 150,000 and 191,947 at L 120,000 (record);
    - main between-turn at B 200,000: 264,386 vs 236,644;
    - sub-a88c at B 200,000: 228,622 vs 199,143 and 198,990.
- **D2 (DEV-2): the fixed start.**
  - The audit's §3.3 value (first − postTokens, about 90-95k on main) is 28k to 45k above the modeled estimate in every segment.
  - The truth is unmeasured. At 2.90 characters per token the snapshot gives about 60-62k on main; at the audit's value it would be 1.9 characters per token.
  - State A borrowed 72,882 for a88c segment 0, above its first context of 67,237.
- **D3: the subagent model explains only a part of the context.**
  - Calibration, modeled / exact user-side growth: main 0.810; a88c 0.409; a492 0.398; ac75 0.372.
  - At the subagent medians, the unattributed part is 70,181 to 204,105 tokens. No rule can archive it, so it bounds the subagent medians.
  - Inferred cause: round 1's D6, "Output counts in the subagent files are under-recorded" (final usage records for 215 of 595, 35 of 561 and 61 of 335 requests). Not re-measured.
- **D4: the 20 queued agent-message prompts (119,238 tokens) are no longer typed text.** Round 1 protected them as typed text. Version 2 makes them R5's hand-backs (by envelope), as item 3 implies. This changes the protected set relative to round 1.
- **D5: R6 supersedes by type alone where the type has no key field.** This covers deferred_tools_delta, agent_listing_delta, mcp_instructions_delta, skill_listing, deferred_tools_record and total_tokens_reminder.
  - For cumulative delta types, a newer delta does not repeat an older delta's announcements.
  - The brief's literal rule archives the older one. Whether the harness re-sends the full listing is unverified.
  - Keyed types: edited_text_file, file and compact_file_reference by filename; nested_memory by path; task_status by taskId; hook_additional_context by hookName.
- **D6: skill bodies.** Every copy stays protected, as in round 1: no rule targets one, and R6 excepts skill bodies through the protected-kind test. The version-2 floors count every copy; round 1's counted the newest copy only.
- **D7: version-2 between-turn check points are stop-hook turn starts** while the protection unit is the request. This is the brief's "a trim still fires only at a turn start". The test proves that items of the finished turn outside the window are taken.
- **D8: the cooldown counts per segment** and resets at a compaction. The brief does not say.
- **D9: `blocked`** counts check points past B that the guard stopped, whether or not an item was eligible there.
- **D10: the best-row criteria C1-C3 are mine and stated.** C2 and C3 are empty wherever no row holds.
- **D11: attachment sizes use 2.90 characters per token.** Round 1's per-kind fit gives 5.25 for other attachments (round 1 report, line 713). So:
  - R6 savings and the opening group's weight may be overstated;
  - the modeled fixed start may be too low, which is the pessimistic direction.
- **D12: output volume is 17M** (SUMMARY.md 1.3 MB, 6,567 lines), against round 1's 3.5M. This is because the grid runs twice, once per reading.
- **D13: the composition uses the lower middle request by active tokens** (ties by request order).

## Self-attack: the most likely ways this change is wrong

1. **A reading choice drives the headline.** This is not ruled out; it is escalated. Both full grids are delivered and both readings are tested (mutants opening-group-not-protected and record-reading-protects-the-group). The default follows the brief's "stay".
2. **The reach probe could disagree with the greedy pass.** It would then block trims that could reach L, or allow trims that cannot.
   - Oracle test `test_the_reach_probe_equals_a_brute_force_sum`: both readings, 5 rule sets × 3 windows/ages, with items archived along the way. Its control requires more than 500 checks and more than 200 non-zero sums.
   - Real data: 382 main requests and 145 a88c requests, worst difference 0.000000 tokens.
   - Every reach trim that fired (8 cells on main and a88c) landed at or under L.
   - Residual: the oracle and the probe share my reading of the eligibility rules.
3. **Round-1 identity could break through a shared path.** Ruled out: the golden test (hashes from the committed round-1 file run from git), plus the 8-of-8 real re-run with the final code.
4. **The pessimistic fixed start may be wrong in either direction (D2, D11).** Both states are reported with every per-segment estimate and the snapshot's character count. The mutant fixed-start-takes-the-larger-estimate is killed.

## Evidence tiers

- **Verified** (ran and checked this session):
  - premise, gates, mutants, round-1 identity, determinism;
  - every per-run number above (from the JSON written by replay.py);
  - probe exactness on real data; that state A differs only in the fixed-start fields (0 of 1,440 cells);
  - equal recognition, fixed start and timeline across the two readings;
  - the prompt_snapshot character counts.
- **Inferred:**
  - that the subagent gap comes from round 1's D6 under-recording;
  - that postTokens leaves out part of the start messages (from the snapshot constancy and the audit's §3.3 note);
  - that cumulative deltas lose information when superseded.
- **Assumed:**
  - the cache ratios (UNSURE parameters: read 0.05 and 0.1, writes 1.25 and 2.0);
  - the 2.90 characters per token for user-side items;
  - the 40-token stub and the 500-token R4 threshold, carried over from round 1.
