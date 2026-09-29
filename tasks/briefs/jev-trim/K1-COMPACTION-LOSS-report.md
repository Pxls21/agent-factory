> Coordinator note (2026-09-29 03:1xZ): the report of record, extracted by `scripts/stack.py harvest` (the lane's report-file write is refused for subagents). Served model: claude-opus-5-5 on every assistant record of this lane (876 across its three rounds), 0 refusal stops; `report_lint` 0 refs. An independent verify follows (VERIFY-K1).

> Coordinator note (2026-09-29 04:2xZ): superseded in part by VERIFY-K1 (`tasks/briefs/jev-trim/VERIFY-K1-report.md`). The numbers reproduce exactly, but the R-C shapes counted writes as re-fetches (F2) and missed this session's main re-fetch forms, Bash views of known files and repeated `git log` or `git show` (F3); corrected, the first 20 requests after a compaction carry +2.5 to +3.3 re-fetch calls per boundary, not +0.49, and the missed-path share is 1.3% to 2.0%, not 1% to 4% (F9). K1 round 2 (`tasks/briefs/jev-trim/K1-R2-brief.md`) re-measures.

# K1-COMPACTION-LOSS report (T0-REPLAY round 3; task #352, D-106)

Written 2026-09-29, last `date -u` 03:13:29Z. Contract: `tasks/briefs/jev-trim/K1-COMPACTION-LOSS-brief.md`. I measure; there is no recommendation.

## Answer first

- **Premise:** re-run, every line matched. No CONTRACT-INVALID.
- **Build:**
  - A new module, `scripts/jev_trim/compaction.py`, imports `replay.py` and `jev_pipes` and changes neither.
  - A new test file, `tests/test_jev_trim_compaction.py`, holds 16 tests and 15 mutants; every mutant is killed at its named assertion.
  - The outputs are 19 files under `docs/research/findings/jev-trim/compaction-2026-09-29/`, all written by the tool.
- **Pins:** main at 788,725,407 bytes (139 boundaries) and 16 subagent files (21 boundaries). A whole-file build fits in memory (peak RSS 1.34 GB), so no segment-by-segment processing was needed.
- **R-C on main, 1M-window class (121 boundaries):**
  - A compaction removes 657,623 modeled tokens on average and keeps 58,273 (postTokens 24,349).
  - The next 20 requests use 86.0 distinctive removed tokens that the kept start lacks. The next 100 use 301.2, and the rest of the segment 411.3.
  - Re-fetch calls per 100 requests:

    | window | after a real boundary | control base rate (27 points) |
    |---|---|---|
    | N = 20 | 26.4 | 23.9 |
    | N = 100 | 21.9 | 25.6 |
    | rest | 21.6 | 25.0 |

  - The mix differs after a boundary: more Reads of known files and ledger reads, fewer identical re-runs.
  - Of the missed paths, 1% to 4% name a file the pre segment read or edited.
- **R-C, subagents pooled (21 boundaries):**
  - Re-fetch calls per 100 requests run 34.8, 30.4 and 27.4 against a base rate of 22.1, 14.9 and 14.9.
  - The excess is mostly transcript searches and Reads of known files.
  - The control here is only 7 points.
- **R-B:** my rates reproduce the coordinator's probe bin for bin. On main, tool errors run 1.45% to 2.11% of calls per bin from 100k to 800k. Inside segments, from the first third to the last, errors fall (1.89% to 1.58%), while re-runs with no edit between rise (0.23% to 1.39% of Bash calls).
- **Cost model (a model, labeled so):**
  - At X = 785k it reproduces the observed compaction count: 119 against 121 on main, and exact on all 16 subagent files.
  - On main, compactions go from 119 to 427 as X falls from 785k to 300k.
  - Mean fill goes from 453,578 to 205,288, and cache-read tokens from 9.24 billion to 4.10 billion.
- **Rounds 1 and 2:** re-run and checked with `sha256sum -c`: 8 of 8 and 11 of 11 OK.
- **Python versions:** all 19 outputs of this round are byte-identical on Python 3.11.15 and 3.12.3.

## NOT done (first-class)

1. No recommendation, by rule.
2. No git writes. Untracked: `scripts/jev_trim/compaction.py`, `tests/test_jev_trim_compaction.py`, `docs/research/findings/jev-trim/compaction-2026-09-29/`.
3. Each subagent file's own R-C, R-B and cost-model tables are in SUMMARY.md only. This report carries the pooled subagent tables and a per-file compaction count.
4. The 200k-window class (18 main boundaries) has no control point: its segments are too short.
5. `replay.py` is unchanged. It drops the items a segment's last request produced (D2). I did not change it; the question is under D2.
6. The per-model R-B table is in the JSON (`quality.by_model`) only, not in SUMMARY.md.
7. No PC gate (no PC bridge). All gates ran in the sandbox.
8. I did not identify which of the 16 subagent files is this lane's own transcript. This lane was compacted once, so one of them is likely mine. It was pinned at my start like the others.

## Deviations (flagged)

- **DEV-1: the P1 miss is a set; `accounting.miss` checks it on the full texts once per boundary.**
  - The miss is computed as a set over the tokens `accounting.tokens` gave each item.
  - Once per boundary, at the widest window, `accounting.miss` runs on the two full joined texts, and its count must equal the set's size, else the run stops.
  - It passed at all 160 boundaries.
  - My first version called `accounting.miss` on texts cut down to the used tokens. The guard caught it at a88c: 344 counted against 345 in the set. The cause is D1.
- **DEV-2: the control's P1 miss is 0 by construction.** The brief says "kept = everything still in context". So the control measures only the base rate of reuse and re-fetches, and the miss "excess" equals the real miss.
- **DEV-3: two extra shapes.** Besides the brief's call shapes I count `identical_other_call` (the same non-Read, non-Bash, non-edit call as in the pre segment) and report it separately.
- **DEV-4: the premise's pytest line used another basetemp.** The brief's `rm -rf /tmp/k1-premise-bt` was replaced by a fresh basetemp under the scratchpad. My first choice of path failed (D15). The re-run printed `110 passed`, as expected.

## Premise re-run (item 1): 02:12 to 02:13Z

```
PIN-is-an-ancestor-of-HEAD
T0-REPLAY round 2 landed (task #346): the replay tool's round-2 grid, its tests and outputs; a record under D-106
73a16e72ed933db5  scripts/jev_trim/replay.py
d17f19c859ed3727  tests/test_jev_trim_replay.py
a9bea1dbbd9c112a  tasks/briefs/jev-trim/k1_authoring_probe.py
ls: cannot access 'scripts/jev_trim/compaction.py': No such file or directory
ls: cannot access 'tests/test_jev_trim_compaction.py': No such file or directory
ls: cannot access 'docs/research/findings/jev-trim/compaction-2026-09-29': No such file or
138
251:### 10.2 Where to compact (task #352)
261:- **R-B, our own quality curve** (the replay tool; count
265:- **R-C, the loss at each compaction** (the replay tool)
2 files set=5365c5f240ce
110 passed
```

HEAD was the commit "I59-F landed with the owner's S0-05 re-capture (tasks #335, #344): S0-01 to S0-05 re-minted; the twelve wait for one signature" at the premise, and the commit "Retro of the CI fix: task #356 registered (a gate under CI's Python); live-state names origin 975523a" now (coordinator commits; coordinator note: local ids the push rewrites, replaced by their subjects). `tests/test_jev_trim_replay.py` later changed by the coordinator's per-interpreter pin, now committed (sha256 841351f042ae62d4). As the coordinator's note said, that is not a CONTRACT-INVALID.

## Files

| path | action | lines | sha256 |
|---|---|---|---|
| scripts/jev_trim/compaction.py | CREATE | 883 | 95e160625dd2cd1067dd853af023367a9ab1c99bda0f85c1101abb4ccd617a95 |
| tests/test_jev_trim_compaction.py | CREATE | 525 | fff6fb719740142e71bb3f65095b0ccaecc04b57e6f01751945261634d18649a |
| scripts/jev_trim/replay.py | read, imported, unchanged | — | 73a16e72ed933db5 (as the premise) |

Outputs in `docs/research/findings/jev-trim/compaction-2026-09-29/` (19 files, 1.2 MB, all written by compaction.py):

| file | lines | sha256 |
|---|---|---|
| SUMMARY.md | 1285 | a77e0c3ff1261bde8fd67f17d75d1d7b5ebfb447ba86503ebbd8c36ba67e64bd |
| pins.json | 141 | bff43daab618cc472620e174b7bedc3ab6b3672a6a56bf31b9c994f2a47d348c |
| run-main.json | 31544 | f18702146dd75902f56f568a216bdc4c0968fd364f161182f821776a561f5ded |
| run-sub-a3977da56fa688986.json | 1308 | ade2290ad64d4e89998cb3421bfae283241945a0e79781faa6d13ae3b8fad481 |
| run-sub-a4920ba3ae772b9d0.json | 1825 | 52e9610d3c9759463f0a8b53e9e3fdfee15bca8da71ca5dc26e8eb9a844c3d72 |
| run-sub-a4c0c331a18908947.json | 975 | a316b478aa33fdd216bdbfba02dd674d414762a2acfb330d7f1b79c615a837f0 |
| run-sub-a4f24691b2f13e97e.json | 1327 | c37fa428a4930fe50ce4f1824b3134b04b423dfb9d510b8c1c6ddd0690b73a00 |
| run-sub-a58226189b58bf46f.json | 998 | b0f9446ec4f05f6b1f73e8a3941d28dfb76808f669ef924adda60efdab3c61a3 |
| run-sub-a60226a535b771d07.json | 1004 | ebc288468d7666d48745fdba44946d7e44f5b6033fb066f13e7450f2acd34fa9 |
| run-sub-a88c7c57f2fa2a96b.json | 1679 | a4693c4c90a066f70ac3842ba7bd8fd72d7bfa5303978d95e21d3cbb5940384e |
| run-sub-a90d7cc077452b42d.json | 1296 | a722b89c7274fb679d8d4ac9ac95f9a4d99db7feff297a45469f008d7fc8de85 |
| run-sub-aa842df27d05dd80d.json | 995 | 7a0520dcba5231c190ec95213414fd1bd9ac6603bd6a2bcfca4bcfddc2d8133f |
| run-sub-aad0e50d8019b70bb.json | 987 | 931af5112a92d0a66f2b8e7b573cd62db028b11cec4f1bb084d86fb607a80c89 |
| run-sub-ab1c8cf107bc6ad72.json | 980 | bafa40413ac593c6c9581b4fbdf4c35d6b2c31dc9abbadef722524de4817f194 |
| run-sub-ac753871198ee8cfd.json | 1477 | 203f69155b857dc65095ded43f7f4513e5382da2b052ff0356c99ec98aaafd8c |
| run-sub-ac9c149483559ffec.json | 985 | fab960ab66be3530f45f6ec785939435c856f5c011dc30ac9560b4c5358ca29c |
| run-sub-acc9cf211b3e34071.json | 979 | 12b87aed2651c68b562e8ae0e680ca570c79d421ae7d623d70adc609966a0534 |
| run-sub-ae66dca0f21a920b6.json | 977 | bbe7cf0a43a7abdd2f100c28448f22610e6bdd1a528a785d40fbcbbf9f7ac00d |
| run-sub-af25a8ffadcb62c75.json | 985 | bf1bf77a56f9f462a05827a780343acc58afd2214add2525a0d0ac09a96a37e2 |

**CLI:** `compaction.py select --transcript MAIN --subagents DIR --sizes SIZES.json --out DIR`; `run --transcript FILE --pin BYTES --label NAME --out DIR [--sidechain]`; `summary --out DIR [--stamp]`. `--sizes` is my start measurement (02:15:09Z, in the scratchpad at `k1r3/pins.json`).

**Timing:** main took 159 to 162 s per run; each subagent file 1 to 4 s.

## Gates (item 7): final code, 03:11:07Z to 03:12:16Z, basetemps under the scratchpad

```
1 files set=7f396804fe23
pytest-summary: 31 passed in 2.53s
pytest-summary: 31 passed in 2.49s
1 files set=1bb7608ed22a
pytest-summary: 68 passed in 7.84s
pytest-summary: 68 passed in 7.86s
1 files set=17f6a5adc0c9
pytest-summary: 42 passed in 23.56s
pytest-summary: 42 passed in 23.78s
```

The three files together: `3 files set=74199ac6b13a`. The replay test ran on sha256 841351f042ae62d4, the coordinator's edited version.

Also run:
- `tests/test_jev_trim_compaction.py` on Python 3.12.3 (the scratchpad's `v312` venv): `31 passed in 3.03s`.
- pyflakes: clean on both new files.
- Separator bytes: 0 in both files and in SUMMARY.md.

`ap_screen` tells:
- **compaction.py, AF-AP-40, one hit:** the summary reads `pins.json` only if present. Its absence is printed as `## Pins: NO pins.json in this directory`, not skipped.
- **Test file, AP-66, four hits:** the `accounting.miss` patch is restored in `finally`. Two are rewrites of local fixture objects' `lines` (a harmless no-op).
- **Test file, AF-AP-80, three hits:** two check the summary's output text; one is the data control that the fixture holds the secret.

**Rounds 1 and 2 byte-identical** (re-run with the committed tool on Python 3.11, then `sha256sum -c`):
- round 1, 8 of 8 OK (02:46 to 02:48Z);
- round 2, 11 of 11 OK (02:48 to 03:03Z).

**3.11 against 3.12 (the coordinator's note).** compaction.py totals floats with `math.fsum` (exactly rounded on both), and `statistics.fmean` is fsum-based. All 19 outputs, re-run under Python 3.12.3, are byte-identical to the 3.11.15 outputs (19 of 19 OK). A re-run of main and of a88c on 3.11 also wrote identical bytes (determinism).

## Mutants: 15, all killed

Each one fails its check with AssertionError at the named line of `tests/test_jev_trim_compaction.py`.

| item | mutant | killed at |
|---|---|---|
| 3 | kept-start-ignored (`opening = []`) | 109: the kept token must be reused, not missed |
| 3 | window-one-request-long (`pos + n + 1`) | 111: a token used at post request 20 is outside N = 20 |
| 3 | read-shape-takes-any-read | 125: the shape counts |
| 3 | miss-check-dropped | 150: the guard must fire on a disagreeing count |
| 4 | pseudo-gap-ignored | 175: only the 250-request segment gets a pseudo-boundary |
| 4 | control-kept-is-empty | 177: the control misses nothing |
| 5 | reread-ignores-edits | 214 |
| 5 | rerun-ignores-edits | 215 |
| 5 | gate-marker-anywhere (no line-start rule) | 217: a Read of the hook text is not a refusal |
| 5 | error-gate-without-an-error | 217 |
| 6 | compaction-resets-to-zero | 231 |
| 6 | compaction-at-X-not-past-it (`>=`) | 234 |
| 6 | small-window-segments-included | 252 |
| 2 | pin-keeps-a-cut-record | 268 |
| 2 | select-by-text-match | 297: a text mention is not a boundary |

**Red-green:** the tests ran green on the built code. The red side is this table. Two tests failed on their first run, both real findings:
- my own wrong assertion (a dict keyed by tool_use id holds the result, not the call), fixed in the test;
- a real defect: the pooled summary vanished when the subagent runs held no boundary. Fixed in compaction.py and covered by `test_the_summary_pools_the_subagent_runs`.

## Pins (item 2): measured at my start, 02:15:09Z

All sizes end on a newline and hold no cut record. `select` re-counted the boundaries as parsed records within these pins at 03:04Z. No other subagent file held a boundary at 03:04Z.

| file | pin (bytes) | compact_boundary records |
|---|---|---|
| bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl (main) | 788,725,407 | 139 |
| agent-a3977da56fa688986.jsonl | 6,563,519 | 1 |
| agent-a4920ba3ae772b9d0.jsonl | 12,926,645 | 3 |
| agent-a4c0c331a18908947.jsonl | 5,021,742 | 1 |
| agent-a4f24691b2f13e97e.jsonl | 5,372,930 | 1 |
| agent-a58226189b58bf46f.jsonl | 6,874,791 | 1 |
| agent-a60226a535b771d07.jsonl | 5,746,951 | 1 |
| agent-a88c7c57f2fa2a96b.jsonl | 14,223,996 | 3 |
| agent-a90d7cc077452b42d.jsonl | 5,722,161 | 1 |
| agent-aa842df27d05dd80d.jsonl | 5,739,552 | 1 |
| agent-aad0e50d8019b70bb.jsonl | 4,660,437 | 1 |
| agent-ab1c8cf107bc6ad72.jsonl | 4,544,022 | 1 |
| agent-ac753871198ee8cfd.jsonl | 9,748,808 | 2 |
| agent-ac9c149483559ffec.jsonl | 5,663,224 | 1 |
| agent-acc9cf211b3e34071.jsonl | 5,654,864 | 1 |
| agent-ae66dca0f21a920b6.jsonl | 3,861,913 | 1 |
| agent-af25a8ffadcb62c75.jsonl | 6,606,908 | 1 |

- **Main:**
  - 21,118 requests in 140 segments; all 139 boundaries measured, none skipped.
  - Requests by model: claude-opus-5-5 11,758; claude-fable-5-1 5,908; claude-opus-4-8 2,771; claude-opus-4-6 532; claude-fable-5 149.
  - Every compaction was `auto`; preTokens range from 144,106 to 802,058.
- **Memory:** whole-file build of main, peak RSS 1.34 GB (15 GB machine).

## R-C and the control (items 3, 4)

**Definitions:**
- **Class:** a boundary whose pre segment's last context is under 400,000 is `200k_window` (on main, 18 boundaries on 09-03 and 09-04 at about 142k); otherwise `1M_window`.
- **Excess:** the real mean minus the control mean.
- **Control points:** the middle request of every segment of 200 or more requests.

### main, `1M_window` (121 boundaries; 27 control points)

- **Removed per boundary, modeled mean:** 657,623 tokens; the last context before is 777,890 (exact).
  - By kind (mean): task_reminder 158,620; other_attachment 142,510; thinking 129,986; tool_input 106,253; tool_result 89,024; other_user_text 16,606; assistant_text 8,832; typed_user_text 3,898; hook_context 1,893.
- **Kept start, modeled mean:** 58,273; the first context after is 119,382 (exact); postTokens 24,349.
- **Post segments:** a median of 150 requests.

| N | window requests | missed (mean) | missed paths (mean) | missed paths read / edited / neither before (sum) | reused (mean) | re-fetch calls / tokens / requests (mean) | control: requests, reused, calls, tokens, requests (mean) | excess calls / tokens | re-fetch calls per 100 requests, real / control |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 20.0 | 86.0 | 12.3 | 15 / 15 / 1,457 | 240.1 | 5.27 / 9,508 / 5.11 | 20.0, 316.9, 4.78, 5,137, 4.74 | +0.49 / +4,371 | 26.4 / 23.9 |
| 100 | 97.1 | 301.2 | 37.7 | 33 / 29 / 4,501 | 713.8 | 21.26 / 29,627 / 20.88 | 100.0, 739.0, 25.59, 29,596, 25.48 | −4.34 / +32 | 21.9 / 25.6 |
| rest | 167.2 | 411.3 | 50.6 | 38 / 42 / 6,042 | 927.4 | 36.07 / 46,286 / 35.55 | 142.7, 863.9, 35.63, 39,966, 35.48 | +0.44 / +6,320 | 21.6 / 25.0 |

The missed excess equals the missed column: the control misses nothing by construction (DEV-2).

Re-fetch shapes, calls per boundary against per control point:

| shape | N = 20 | N = 100 | rest |
|---|---|---|---|
| read_known_path | 0.31 / 0.11 | 0.63 / 0.37 | 0.72 / 0.41 |
| rerun_command | 0.01 / 0.30 | 0.15 / 1.15 | 0.25 / 1.56 |
| identical_other_call | 0.09 / 0.19 | 0.49 / 0.33 | 0.60 / 0.33 |
| search_transcript | 1.89 / 2.07 | 7.21 / 10.96 | 14.31 / 15.85 |
| search_ledger | 2.51 / 1.63 | 10.53 / 9.96 | 16.58 / 13.44 |
| search_live_state | 0.46 / 0.48 | 2.25 / 2.81 | 3.62 / 4.04 |

Of the read_known_path calls in `rest`, 37 were Reads of a file the kept start had re-injected.

### main, `200k_window` (18 boundaries; no control point)

- **Removed, modeled mean:** 109,169; the last context before is 142,069.
- **Kept start, modeled mean:** 28,042; the first context after is 83,659; postTokens 18,948.
- **Post segments:** a median of 29.5 requests.

| N | window requests | missed (mean) | missed paths (mean) | read / edited / neither (sum) | reused (mean) | re-fetch calls / tokens / requests (mean) |
|---|---|---|---|---|---|---|
| 20 | 18.7 | 54.8 | 7.8 | 23 / 0 / 118 | 197.9 | 4.72 / 4,508 / 3.89 |
| 100 | 34.1 | 79.9 | 9.9 | 24 / 0 / 154 | 276.9 | 8.22 / 7,245 / 7.33 |
| rest | 39.7 | 83.9 | 10.1 | 24 / 0 / 157 | 285.7 | 8.89 / 8,024 / 8.00 |

Its calls per boundary at `rest`: read_known_path 2.89, rerun_command 1.06, search_ledger 4.39. 30 of the known-path Reads hit a re-injected file.

### Subagents pooled (16 files, 21 boundaries, all `1M_window`; 7 control points)

- **Removed, modeled mean:** 555,878; the last context before is 778,367.
- **Kept start, modeled mean:** 43,985; the first context after is 85,432; postTokens 16,650.
- **Post segments:** a median of 96 requests.

| N | window requests | missed (mean) | missed paths (mean) | read / edited / neither (sum) | reused (mean) | re-fetch calls / tokens / requests (mean) | control: requests, reused, calls, tokens, requests | excess calls / tokens | per 100 requests, real / control |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 16.1 | 38.3 | 6.9 | 4 / 5 / 136 | 111.9 | 5.62 / 13,843 / 5.57 | 20.0, 360.1, 4.43, 8,969, 4.43 | +1.19 / +4,874 | 34.8 / 22.1 |
| 100 | 68.9 | 185.2 | 26.1 | 12 / 17 / 520 | 415.1 | 20.95 / 36,767 / 20.10 | 100.0, 781.4, 14.86, 29,338, 14.29 | +6.10 / +7,430 | 30.4 / 14.9 |
| rest | 108.8 | 303.3 | 35.0 | 12 / 24 / 700 | 591.1 | 29.86 / 49,315 / 28.76 | 115.3, 798.4, 17.14, 32,391, 16.57 | +12.71 / +16,923 | 27.4 / 14.9 |

Shapes at `rest`, per boundary against per point: search_transcript 26.48 / 14.71; read_known_path 2.81 / 1.86; search_ledger 0.38 / 0.43; the others 0.1 or less.

Boundaries, control points and requests per file:

| file | boundaries | control points | requests |
|---|---|---|---|
| a3977 | 1 | 1 | 369 |
| a4920 | 3 | 2 | 714 |
| a4c0c | 1 | 0 | 159 |
| a4f24 | 1 | 1 | 285 |
| a5822 | 1 | 0 | 342 |
| a6022 | 1 | 0 | 237 |
| a88c7 | 3 | 1 | 723 |
| a90d7 | 1 | 1 | 296 |
| aa842 | 1 | 0 | 198 |
| aad0e | 1 | 0 | 179 |
| ab1c8 | 1 | 0 | 193 |
| ac753 | 2 | 1 | 425 |
| ac9c1 | 1 | 0 | 210 |
| acc9c | 1 | 0 | 223 |
| ae66d | 1 | 0 | 197 |
| af25a | 1 | 0 | 239 |

## R-B, the quality curve (item 5)

Rates are per call, attributed to the request that made the call. Re-reads are a share of Reads, re-runs of Bash calls, failed edits of edit calls.

### main, per 100k of fill

| bin | requests | calls | tool errors | failed edits | re-reads | re-runs | refusals (sum) |
|---|---|---|---|---|---|---|---|
| 0-100k | 84 | 150 | 1 (0.67%) | 0/0 | 1/39 | 0/106 | 0 |
| 100-200k | 2,146 | 2,617 | 43 (1.64%) | 3/200 | 1/180 | 16/1,976 (0.81%) | 6 |
| 200-300k | 2,994 | 3,565 | 72 (2.02%) | 1/168 | 1/87 | 5/2,735 (0.18%) | 11 |
| 300-400k | 3,133 | 3,460 | 62 (1.79%) | 0/206 | 0/80 | 10/2,733 (0.37%) | 9 |
| 400-500k | 3,360 | 3,603 | 76 (2.11%) | 5/232 | 4/59 | 20/2,887 (0.69%) | 19 |
| 500-600k | 3,337 | 3,462 | 54 (1.56%) | 2/195 | 0/44 | 23/2,748 (0.84%) | 19 |
| 600-700k | 3,242 | 3,317 | 48 (1.45%) | 2/173 | 0/52 | 36/2,584 (1.39%) | 17 |
| 700-800k | 2,822 | 3,018 | 51 (1.69%) | 0/135 | 2/40 | 28/2,299 (1.22%) | 22 |

Refusals by gate on main over all bins: stale_ids 24, commit_blocked_other 30, future_stamp 15, ci_gate 9, lint_delta 7, never_a_gate 6, push_blocked 6, quirk_guard 3, search_intercept 3.

### main, per segment third

| third | mean fill | calls | tool errors | failed edits | re-reads | re-runs | refusals |
|---|---|---|---|---|---|---|---|
| first | 256,046 | 8,417 | 1.89% | 3/440 | 2/303 | 15/6,607 (0.23%) | 21 |
| middle | 466,058 | 7,424 | 1.78% | 7/489 | 5/147 | 45/5,842 (0.77%) | 37 |
| last | 664,716 | 7,351 | 1.58% | 3/380 | 2/131 | 78/5,619 (1.39%) | 45 |

**The probe's floor, reproduced.** The coordinator's probe, run on main at 789,421,832 bytes (0.7 MB past my pin), prints 0.7, 1.6, 2.0, 1.8, 2.1, 1.6, 1.4 and 1.7 error % per bin. Mine are 0.67, 1.64, 2.02, 1.79, 2.11, 1.56, 1.45 and 1.69. Requests, calls, edit-error % and re-read % are equal per bin, except in the 500-700k bins, which the growth past my pin fills.

**Tool errors per model and bin on main** (bins of 300 calls or more; in the JSON):
- claude-opus-5-5: 1.23% to 2.43%.
- claude-fable-5-1: 1.22% to 1.91%.
- claude-opus-4-8: 0.91% to 3.33%.

### Subagents pooled, per 100k of fill

| bin | requests | calls | tool errors | failed edits | re-reads | re-runs | refusals |
|---|---|---|---|---|---|---|---|
| 0-100k | 130 | 148 | 0.00% | 0/2 | 0/40 | 0/101 | 0 |
| 100-200k | 810 | 850 | 0.82% | 0/26 | 0/85 | 0/722 | 1 |
| 200-300k | 834 | 876 | 1.71% | 2/99 | 0/48 | 1/712 | 1 |
| 300-400k | 780 | 843 | 2.25% | 0/155 | 0/36 | 2/634 | 2 |
| 400-500k | 675 | 738 | 2.03% | 1/131 | 1/19 | 0/581 | 0 |
| 500-600k | 590 | 615 | 2.44% | 3/75 | 0/28 | 0/501 | 0 |
| 600-700k | 588 | 621 | 1.29% | 1/84 | 0/28 | 2/498 | 2 |
| 700-800k | 582 | 609 | 1.15% | 0/77 | 0/24 | 0/500 | 0 |

Subagent thirds:

| third | mean fill | tool errors | failed edits | re-runs |
|---|---|---|---|---|
| first | 215,074 | 1.27% | 1/188 | 1/1,412 |
| middle | 416,502 | 1.98% | 0/246 | 0/1,438 |
| last | 608,122 | 1.63% | 6/215 | 4/1,398 |

**Markers** (gate: fixed string; the rule):

| gate | marker | rule |
|---|---|---|
| future_stamp | `COMMIT BLOCKED by the future-stamp gate` | at a line start |
| lint_delta | `COMMIT BLOCKED by lint_delta` | at a line start |
| mutant_anchor | `COMMIT BLOCKED by mutant_anchor_precommit` | at a line start |
| mirror | `COMMIT BLOCKED by the MIRROR gate` | at a line start |
| never_a_gate | `COMMIT BLOCKED by the never-a-gate screen` | at a line start |
| push_in_flight | `COMMIT BLOCKED: a push is in flight` | at a line start |
| commit_blocked_other | `COMMIT BLOCKED` | at a line start |
| push_blocked | `PUSH BLOCKED` | at a line start |
| stale_ids | `REFUSED by stale_ids` | at a line start |
| ci_gate | `REFUSED by ci-gate` | at a line start |
| search_intercept | `SEARCH INTERCEPT (search-intercept.py)` | inside a result with is_error |
| quirk_guard | `QUIRK GUARD (search-intercept.py` | inside a result with is_error |

The strings come from `scripts/hooks/*`, `scripts/push_clean.sh`, `scripts/ci_gate.py` and `.claude/hooks/search-intercept.py`.

**Re-fetch search markers** (a call's input holding every string of a group):
- search_transcript: `.claude/projects/`; `/tasks/` and `.output` together; `chat_tail.py`; `session_export.py`; `transcript_export.py`; `hiccup_scan.py`; `replay_transcript_edits.py`.
- search_ledger: `BUILD-TASKLIST.md`.
- search_live_state: `live-state.md`.

## The cost model (item 6): a MODEL, not a measurement

**Main.**
- Included: 122 segments. The 18 segments that end in a 200k-window compaction are left out.
- The kept start K is 119,625, the mean first context of 121 segments.
- The stream is 20,585 growth steps, 11 of them negative.
- Units are in the base input price: read 0.05, write 2.0.

| X | modeled compactions | mean fill | cache-read tokens (units) | cache-write tokens (units) | summarizer reads |
|---|---|---|---|---|---|
| 300,000 | 427 | 205,288 | 4,100,747,389 (205,037,369) | 125,902,060 (251,804,120) | 125,139,994 |
| 400,000 | 278 | 256,417 | 5,169,179,159 (258,458,958) | 110,014,563 (220,029,126) | 109,046,580 |
| 500,000 | 206 | 305,770 | 6,192,762,386 (309,638,119) | 102,412,440 (204,824,880) | 101,491,232 |
| 600,000 | 164 | 355,983 | 7,230,448,795 (361,522,440) | 98,409,562 (196,819,123) | 97,370,356 |
| 700,000 | 136 | 406,302 | 8,269,623,513 (413,481,176) | 95,112,346 (190,224,692) | 94,119,653 |
| 785,000 | 119 (observed 121) | 453,578 | 9,244,750,496 (462,237,525) | 93,190,429 (186,380,858) | 92,329,348 |

**Modeled loss on main** = the compactions times the per-boundary means of the 1M class. Each cell is missed tokens / re-fetch calls / re-fetch tokens.

| X | raw, N = 20 | raw, N = 100 | raw, rest | excess, N = 20 | excess, N = 100 | excess, rest |
|---|---|---|---|---|---|---|
| 300k | 36,701 / 2,252 / 4,060,103 | 128,619 / 9,076 / 12,650,834 | 175,610 / 15,404 / 19,764,221 | 36,701 / 211 / 1,866,457 | 128,619 / −1,852 / 13,550 | 175,610 / 190 / 2,698,565 |
| 400k | 23,894 / 1,466 / 2,643,346 | 83,738 / 5,909 / 8,236,374 | 114,332 / 10,029 / 12,867,572 | 23,894 / 138 / 1,215,164 | 83,738 / −1,206 / 8,822 | 114,332 / 124 / 1,756,911 |
| 500k | 17,706 / 1,086 / 1,958,738 | 62,050 / 4,379 / 6,103,212 | 84,720 / 7,431 / 9,534,964 | 17,706 / 102 / 900,445 | 62,050 / −893 / 6,537 | 84,720 / 92 / 1,301,884 |
| 600k | 14,096 / 865 / 1,559,384 | 49,399 / 3,486 / 4,858,868 | 67,447 / 5,916 / 7,590,942 | 14,096 / 81 / 716,860 | 49,399 / −711 / 5,204 | 67,447 / 73 / 1,036,451 |
| 700k | 11,689 / 717 / 1,293,148 | 40,965 / 2,891 / 4,029,305 | 55,932 / 4,906 / 6,294,928 | 11,689 / 67 / 594,469 | 40,965 / −590 / 4,316 | 55,932 / 60 / 859,496 |
| 785k | 10,228 / 628 / 1,131,504 | 35,845 / 2,530 / 3,525,642 | 48,940 / 4,293 / 5,508,062 | 10,228 / 59 / 520,160 | 35,845 / −516 / 3,776 | 48,940 / 53 / 752,059 |

**Subagent files: modeled compactions** at X = 300k / 400k / 500k / 600k / 700k / 785k. At 785k every file equals its observed count.

| file | 300k | 400k | 500k | 600k | 700k | 785k |
|---|---|---|---|---|---|---|
| a88c | 11 | 8 | 6 | 5 | 4 | 3 |
| a4920 | 9 | 6 | 4 | 4 | 3 | 3 |
| ac753 | 6 | 4 | 3 | 2 | 2 | 2 |
| a3977 | 4 | 3 | 2 | 1 | 1 | 1 |
| a5822 | 4 | 3 | 2 | 2 | 1 | 1 |
| a6022 | 4 | 3 | 2 | 1 | 1 | 1 |
| a90d7 | 4 | 3 | 2 | 1 | 1 | 1 |
| aa842 | 4 | 3 | 2 | 1 | 1 | 1 |
| ac9c1 | 4 | 2 | 2 | 1 | 1 | 1 |
| acc9c | 4 | 3 | 2 | 1 | 1 | 1 |
| af25a | 5 | 3 | 2 | 2 | 1 | 1 |
| a4c0c | 3 | 2 | 1 | 1 | 1 | 1 |
| a4f24 | 3 | 2 | 1 | 1 | 1 | 1 |
| aad0e | 3 | 2 | 1 | 1 | 1 | 1 |
| ab1c8 | 3 | 2 | 1 | 1 | 1 | 1 |
| ae66d | 3 | 2 | 1 | 1 | 1 | 1 |

Each file's full table is in SUMMARY.md.

**Assumptions** (also in SUMMARY.md and the module's `MODEL_ASSUMPTIONS`):
- The work (the growth per request) is the same at every X.
- The early 200k-window segments are left out.
- The step across an observed compaction is taken as 0.
- The fill returns to K after a modeled compaction, whatever X is.
- The request after a compaction writes all of K (the cached system prompt is not credited).
- Other requests read the previous fill and write their growth.
- The summarizer's read is its own column, not added to the reads.
- The loss per compaction is the per-boundary mean measured at about 785k, the same at every X; `rest` keeps the observed segment length.

## DISCREPANCIES

- **D1: the restricted-text shortcut is not exact.** Python's `\b` treats a non-ASCII letter as a word character. So a path's inner identifier matches when the path stands alone but not in the full text (for example, a path followed by "é"). My first shortcut differed by 1 token at a88c boundary 1 (344 against 345). Fixed by DEV-1; the test `test_the_miss_set_is_accounting_miss_on_the_full_texts` records the case.
- **D2: the last request's output is missing from `rest`.** `replay.build` drops the items a segment's last request produced (stat `items_after_their_segments_last_request`). So `rest` never holds that request's tool inputs and assistant text: one request per segment. One subagent (ae66) has a single post request and shows used 0.
  - Question to the coordinator: should `replay.py` gain an option to keep those items? I did not change it. It is not unavoidable for this round.
- **D3: the control is small and biased.**
  - Main: 27 points, all in 1M segments of 200+ requests; the 200k class has none.
  - Subagents: 7 points.
  - `rest` compares 167.2 against 142.7 requests on main, so the per-100-request rates are the fair comparison.
- **D4: what the P1 miss measures here.** It counts removed distinctive tokens that the next N requests used and that neither the kept start nor the system prompt held. That includes tokens the session met again through new work. It measures reuse of removed content, not proven need.
- **D5: most missed paths name no file the pre segment read or edited.** Main, 1M class: 1,457 of 1,487 at N = 20, and 6,042 of 6,122 at `rest`. Their sources are Bash output, greps, reports and injections, which the Read/Edit test does not see.
- **D6: shape labels depend on the lane's work.** A lane whose work is reading transcripts (the verifiers, this lane) makes `search_transcript` calls as normal work. The coordinator reads the ledger and the live-state routinely. The control's base rate is the correction, but its sample is small.
- **D7: the kept start is modeled above postTokens.** The modeled kept start (58,273 on main) exceeds postTokens (24,349). The same pattern appeared in round 2's D2: 2.90 characters per token against the harness's own count.
- **D8: main mixes models and windows.** Five model families and two windows (18 boundaries at about 142k, 121 at about 778k). R-B per model is in the JSON; the cost model leaves out the 200k segments.
- **D9: refusal counts include hook tests.** The line-start rule keeps greps and Reads of hook sources out, but a hook test that prints the marker at a line start counts as a refusal. The markers come from today's hooks; earlier or renamed gates are not listed.
- **D10: Bash edits are not seen.** An "edit" is an Edit, Write, MultiEdit or NotebookEdit call, failed or not, as in the probe. A Bash command that changes a file is not seen, so "no edit between" may hold a Bash change.
- **D11: removed task reminders.** On main, task-reminder copies make up 158,620 modeled tokens of the average removed context (every copy stays until the compaction). They are modeled at 2.90 characters per token.
- **D12: the replay test file changed after the premise** (the coordinator's per-interpreter pin, committed in the CI fix). My final gates ran on sha256 841351f042ae62d4.
- **D13: a stale scratch file broke my first premise attempt.** The scratch path `k1` is an unrelated 10-byte file from 2026-09-03. My first premise basetemp under it failed (`8 passed, 102 errors`, NotADirectoryError). The re-run under `k1r3/` gave `110 passed`. I did not touch that file.
- **D14: a stray file, created and removed.** A failed `/usr/bin/time` wrapper (the binary is not installed) redirected stderr to `/home/user/tmp_k1_time.txt`. It held 61 bytes, the shell's error line only. I removed it by its literal path.
- **D15: the test file reuses round 1's fixture builders.** It imports `Tx`, `step`, `call` and `TOKENS_1000` from `tests/test_jev_trim_replay.py`, read-only. A change there can break these tests.

## Self-attack: the most likely ways this is wrong

1. **The miss could be wrong.**
   - Ruled out for the definition: at every one of the 160 boundaries, `accounting.miss` on the full texts equals the set, or the run would have stopped.
   - The fixture tests assert each planted token's fate differentially.
   - Residual: the P1 token classes (identifiers of 6+ characters, paths, 3+ digit numbers, hex) count incidental tokens. The miss measures reuse, not need (D4).
2. **The control could be unfair** (D3, D6). Not ruled out. It is reported as it is, with per-100-request rates and the shapes side by side.
3. **The re-fetch shapes could be mislabeled.** Each shape is tested (one call each, plus a Read of a new file that must not count), with the mutant read-shape-takes-any-read. Residual: the markers are fixed strings, and a call holding two markers takes the first shape in the order.
4. **R-B could mis-attribute calls.** Ruled out by reproducing the coordinator's independent probe bin for bin; 0 calls were without a request on main.
5. **The cost model could be off.** It is labeled a model with every assumption listed. It is calibrated at 785k (119 against 121 on main, exact on the 16 subagent files). Residual: the loss per compaction is taken as constant across X.

## Evidence tiers

- **Verified** (run and checked this session): the premise; the gates (twice each); the 15 mutants and their lines; the pins and boundary counts (parsed records); every number above, read from the JSON that compaction.py wrote; the probe match; rounds 1 and 2 byte-identical; determinism; 3.11 against 3.12 byte identity; peak RSS.
- **Inferred:**
  - that one subagent file is this lane's own;
  - that the missed paths come mainly from Bash, greps, reports and injections (D5);
  - that postTokens leaves some kept-start injections uncounted (D7).
- **Assumed:**
  - every cost-model assumption (listed);
  - 2.90 characters per token for user-side items;
  - the cache ratios 0.05 and 2.0 (UNSURE parameters, as in rounds 1 and 2).
