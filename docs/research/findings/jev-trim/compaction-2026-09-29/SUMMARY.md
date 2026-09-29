# K1-COMPACTION-LOSS results (task #352, D-106)

Written by `scripts/jev_trim/compaction.py summary` at 2026-09-29T03:07:18Z. Counts, sizes, offsets and names only.
No recommendation. The brief is `tasks/briefs/jev-trim/K1-COMPACTION-LOSS-brief.md`; the method is in the module's docstring.

## Pins

| file | role | measured at the start | pin | compact_boundary records |
|---|---|---|---|---|
| bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl | main | 788,725,407 | 788,725,407 | 139 |
| agent-a3977da56fa688986.jsonl | subagent | 6,563,519 | 6,563,519 | 1 |
| agent-a4920ba3ae772b9d0.jsonl | subagent | 12,926,645 | 12,926,645 | 3 |
| agent-a4c0c331a18908947.jsonl | subagent | 5,021,742 | 5,021,742 | 1 |
| agent-a4f24691b2f13e97e.jsonl | subagent | 5,372,930 | 5,372,930 | 1 |
| agent-a58226189b58bf46f.jsonl | subagent | 6,874,791 | 6,874,791 | 1 |
| agent-a60226a535b771d07.jsonl | subagent | 5,746,951 | 5,746,951 | 1 |
| agent-a88c7c57f2fa2a96b.jsonl | subagent | 14,223,996 | 14,223,996 | 3 |
| agent-a90d7cc077452b42d.jsonl | subagent | 5,722,161 | 5,722,161 | 1 |
| agent-aa842df27d05dd80d.jsonl | subagent | 5,739,552 | 5,739,552 | 1 |
| agent-aad0e50d8019b70bb.jsonl | subagent | 4,660,437 | 4,660,437 | 1 |
| agent-ab1c8cf107bc6ad72.jsonl | subagent | 4,544,022 | 4,544,022 | 1 |
| agent-ac753871198ee8cfd.jsonl | subagent | 9,748,808 | 9,748,808 | 2 |
| agent-ac9c149483559ffec.jsonl | subagent | 5,663,224 | 5,663,224 | 1 |
| agent-acc9cf211b3e34071.jsonl | subagent | 5,654,864 | 5,654,864 | 1 |
| agent-ae66dca0f21a920b6.jsonl | subagent | 3,861,913 | 3,861,913 | 1 |
| agent-af25a8ffadcb62c75.jsonl | subagent | 6,606,908 | 6,606,908 | 1 |

Subagent files with a boundary now but not in the start measurement: 0.

## Run `main`: bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl pinned at 788,725,407 bytes (main thread)

- Requests 21,118; segments with requests 140; boundaries on the thread 139; skipped boundaries 0; models {'claude-fable-5': 149, 'claude-fable-5-1': 5908, 'claude-opus-4-6': 532, 'claude-opus-4-8': 2771, 'claude-opus-5-5': 11758}.

### R-C, class `1M_window`: 121 boundaries, 27 control points

- Removed per boundary (modeled, mean): 657,623 tokens; last context before (mean) 777,890; kept start per boundary (modeled, mean) 58,273; first context after (mean) 119,382; postTokens (mean) 24,349.

| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) | control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) | excess missed | excess re-fetch calls | excess re-fetch tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 121 | 20.0 | 86.0 | 12.3 | 15 / 15 | 240.1 | 5.27 | 9,508.4 | 5.11 | 27 | 316.9 | 4.78 | 5,137.3 | 86.0 | 0.49 | 4,371.1 |
| 100 | 121 | 97.1 | 301.2 | 37.7 | 33 / 29 | 713.8 | 21.26 | 29,627.2 | 20.88 | 27 | 739.0 | 25.59 | 29,595.5 | 301.2 | -4.34 | 31.7 |
| rest | 121 | 167.2 | 411.3 | 50.6 | 38 / 42 | 927.4 | 36.07 | 46,286.2 | 35.55 | 27 | 863.9 | 35.63 | 39,966.4 | 411.3 | 0.44 | 6,319.8 |

| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | control tokens (sum) |
|---|---|---|---|---|---|---|
| 20 | read_known_path | 37 | 146,014 | 34 | 3 | 5,980 |
| 20 | rerun_command | 1 | 433 | 1 | 8 | 2,780 |
| 20 | identical_other_call | 11 | 23,847 | 10 | 5 | 4,340 |
| 20 | search_transcript | 229 | 322,865 | 225 | 56 | 47,139 |
| 20 | search_ledger | 304 | 583,707 | 299 | 44 | 68,099 |
| 20 | search_live_state | 56 | 73,654 | 56 | 13 | 10,371 |
| 100 | read_known_path | 76 | 214,939 | 72 | 10 | 11,149 |
| 100 | rerun_command | 18 | 5,612 | 18 | 31 | 12,572 |
| 100 | identical_other_call | 59 | 53,731 | 58 | 9 | 16,266 |
| 100 | search_transcript | 873 | 943,296 | 858 | 296 | 310,502 |
| 100 | search_ledger | 1274 | 2,068,764 | 1264 | 269 | 369,670 |
| 100 | search_live_state | 272 | 298,555 | 272 | 76 | 78,920 |
| rest | read_known_path | 87 | 225,375 | 83 | 11 | 11,680 |
| rest | rerun_command | 30 | 8,617 | 30 | 42 | 16,334 |
| rest | identical_other_call | 73 | 67,020 | 72 | 9 | 16,266 |
| rest | search_transcript | 1731 | 1,736,581 | 1706 | 428 | 434,564 |
| rest | search_ledger | 2006 | 3,099,205 | 1995 | 363 | 494,568 |
| rest | search_live_state | 438 | 463,836 | 437 | 109 | 105,680 |

### R-C, class `200k_window`: 18 boundaries, 0 control points

- Removed per boundary (modeled, mean): 109,169 tokens; last context before (mean) 142,069; kept start per boundary (modeled, mean) 28,042; first context after (mean) 83,659; postTokens (mean) 18,948.

| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) | control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) | excess missed | excess re-fetch calls | excess re-fetch tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 18 | 18.7 | 54.8 | 7.8 | 23 / 0 | 197.9 | 4.72 | 4,507.8 | 3.89 | 0 | — | — | — | — | — | — |
| 100 | 18 | 34.1 | 79.9 | 9.9 | 24 / 0 | 276.9 | 8.22 | 7,244.9 | 7.33 | 0 | — | — | — | — | — | — |
| rest | 18 | 39.7 | 83.9 | 10.1 | 24 / 0 | 285.7 | 8.89 | 8,024.3 | 8.00 | 0 | — | — | — | — | — | — |

| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | control tokens (sum) |
|---|---|---|---|---|---|---|
| 20 | read_known_path | 41 | 57,086 | 30 | 0 | 0 |
| 20 | rerun_command | 15 | 6,189 | 13 | 0 | 0 |
| 20 | identical_other_call | 5 | 186 | 5 | 0 | 0 |
| 20 | search_transcript | 3 | 374 | 2 | 0 | 0 |
| 20 | search_ledger | 21 | 17,305 | 20 | 0 | 0 |
| 20 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| 100 | read_known_path | 52 | 77,001 | 41 | 0 | 0 |
| 100 | rerun_command | 19 | 7,033 | 17 | 0 | 0 |
| 100 | identical_other_call | 7 | 276 | 7 | 0 | 0 |
| 100 | search_transcript | 3 | 374 | 2 | 0 | 0 |
| 100 | search_ledger | 67 | 45,724 | 65 | 0 | 0 |
| 100 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| rest | read_known_path | 52 | 77,001 | 41 | 0 | 0 |
| rest | rerun_command | 19 | 7,033 | 17 | 0 | 0 |
| rest | identical_other_call | 7 | 276 | 7 | 0 | 0 |
| rest | search_transcript | 3 | 374 | 2 | 0 | 0 |
| rest | search_ledger | 79 | 59,753 | 77 | 0 | 0 |
| rest | search_live_state | 0 | 0 | 0 | 0 | 0 |

### R-B, per 100k of fill

| bin | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0k-100k | 84 | 89,849 | 150 | 1 | 0.67% | 0 / 0 (—) | 1 / 39 (2.56%) | 0 / 106 (0.00%) | 0 | Bash 1 |
| 100k-200k | 2,146 | 152,779 | 2,617 | 43 | 1.64% | 3 / 200 (1.50%) | 1 / 180 (0.56%) | 16 / 1976 (0.81%) | ci_gate 1, commit_blocked_other 1, lint_delta 3, search_intercept 1 | Bash 37, Edit 3, Grep 1 |
| 200k-300k | 2,994 | 250,887 | 3,565 | 72 | 2.02% | 1 / 168 (0.60%) | 1 / 87 (1.15%) | 5 / 2735 (0.18%) | commit_blocked_other 5, lint_delta 1, push_blocked 1, quirk_guard 2, search_intercept 1, stale_ids 1 | Bash 66, mcp__github__actions_run_trigger 3, TaskUpdate 1 |
| 300k-400k | 3,133 | 350,327 | 3,460 | 62 | 1.79% | 0 / 206 (0.00%) | 0 / 80 (0.00%) | 10 / 2733 (0.37%) | ci_gate 2, commit_blocked_other 3, future_stamp 2, lint_delta 1, stale_ids 1 | Bash 55, Glob 2, Read 2 |
| 400k-500k | 3,360 | 449,658 | 3,603 | 76 | 2.11% | 5 / 232 (2.16%) | 4 / 59 (6.78%) | 20 / 2887 (0.69%) | ci_gate 3, commit_blocked_other 10, future_stamp 2, stale_ids 4 | Bash 70, Edit 4, Read 1 |
| 500k-600k | 3,337 | 551,684 | 3,462 | 54 | 1.56% | 2 / 195 (1.03%) | 0 / 44 (0.00%) | 23 / 2748 (0.84%) | ci_gate 1, commit_blocked_other 5, future_stamp 4, never_a_gate 2, stale_ids 7 | Bash 49, Edit 2, TaskStop 1 |
| 600k-700k | 3,242 | 651,005 | 3,317 | 48 | 1.45% | 2 / 173 (1.16%) | 0 / 52 (0.00%) | 36 / 2584 (1.39%) | ci_gate 1, commit_blocked_other 3, future_stamp 5, lint_delta 1, never_a_gate 1, push_blocked 1, stale_ids 5 | Bash 42, Edit 2, Read 1 |
| 700k-800k | 2,822 | 742,435 | 3,018 | 51 | 1.69% | 0 / 135 (0.00%) | 2 / 40 (5.00%) | 28 / 2299 (1.22%) | ci_gate 1, commit_blocked_other 3, future_stamp 2, lint_delta 1, never_a_gate 3, push_blocked 4, quirk_guard 1, search_intercept 1, stale_ids 6 | Bash 46, Monitor 2, Grep 1 |

### R-B, per segment third

| third | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| first | 7,088 | 256,046 | 8,417 | 159 | 1.89% | 3 / 440 (0.68%) | 2 / 303 (0.66%) | 15 / 6607 (0.23%) | ci_gate 3, commit_blocked_other 8, lint_delta 3, push_blocked 1, quirk_guard 2, search_intercept 2, stale_ids 2 | Bash 142, TaskUpdate 3, mcp__github__actions_run_trigger 3 |
| middle | 7,043 | 466,058 | 7,424 | 132 | 1.78% | 7 / 489 (1.43%) | 5 / 147 (3.40%) | 45 / 5842 (0.77%) | ci_gate 4, commit_blocked_other 15, future_stamp 6, never_a_gate 2, stale_ids 10 | Bash 120, Edit 6, Read 1 |
| last | 6,987 | 664,716 | 7,351 | 116 | 1.58% | 3 / 380 (0.79%) | 2 / 131 (1.53%) | 78 / 5619 (1.39%) | ci_gate 2, commit_blocked_other 7, future_stamp 9, lint_delta 4, never_a_gate 4, push_blocked 5, quirk_guard 1, search_intercept 1, stale_ids 12 | Bash 104, Edit 3, Monitor 2 |

### Cost model (MODEL, not a measurement): included segments 122, kept start 119,625, observed compactions among them 121

| X | modeled compactions | requests | mean fill | cache-read tokens | read units | cache-write tokens | write units | summarizer reads | loss N=20: missed / re-fetch calls / tokens (raw) | loss N=100 (raw) | loss rest (raw) | loss N=100 (excess) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 300,000 | 427 | 20,586 | 205,288 | 4,100,747,389 | 205,037,369 | 125,902,060 | 251,804,120 | 125,139,994 | 36,701 / 2,252 / 4,060,103 | 128,619 / 9,076 / 12,650,834 | 175,610 / 15,404 / 19,764,221 | 128,619 / -1,852 / 13,550 |
| 400,000 | 278 | 20,586 | 256,417 | 5,169,179,159 | 258,458,958 | 110,014,563 | 220,029,126 | 109,046,580 | 23,894 / 1,466 / 2,643,346 | 83,738 / 5,909 / 8,236,374 | 114,332 / 10,029 / 12,867,572 | 83,738 / -1,206 / 8,822 |
| 500,000 | 206 | 20,586 | 305,770 | 6,192,762,386 | 309,638,119 | 102,412,440 | 204,824,880 | 101,491,232 | 17,706 / 1,086 / 1,958,738 | 62,050 / 4,379 / 6,103,212 | 84,720 / 7,431 / 9,534,964 | 62,050 / -893 / 6,537 |
| 600,000 | 164 | 20,586 | 355,983 | 7,230,448,795 | 361,522,440 | 98,409,562 | 196,819,123 | 97,370,356 | 14,096 / 865 / 1,559,384 | 49,399 / 3,486 / 4,858,868 | 67,447 / 5,916 / 7,590,942 | 49,399 / -711 / 5,204 |
| 700,000 | 136 | 20,586 | 406,302 | 8,269,623,513 | 413,481,176 | 95,112,346 | 190,224,692 | 94,119,653 | 11,689 / 717 / 1,293,148 | 40,965 / 2,891 / 4,029,305 | 55,932 / 4,906 / 6,294,928 | 40,965 / -590 / 4,316 |
| 785,000 | 119 | 20,586 | 453,578 | 9,244,750,496 | 462,237,525 | 93,190,429 | 186,380,858 | 92,329,348 | 10,228 / 628 / 1,131,504 | 35,845 / 2,530 / 3,525,642 | 48,940 / 4,293 / 5,508,062 | 35,845 / -516 / 3,776 |

## Run `sub-a3977da56fa688986`: agent-a3977da56fa688986.jsonl pinned at 6,563,519 bytes (sidechain thread)

- Requests 369; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; models {'claude-opus-5-5': 369}.

### R-C, class `1M_window`: 1 boundaries, 1 control points

- Removed per boundary (modeled, mean): 729,970 tokens; last context before (mean) 783,095; kept start per boundary (modeled, mean) 49,852; first context after (mean) 90,872; postTokens (mean) 12,724.

| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) | control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) | excess missed | excess re-fetch calls | excess re-fetch tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 20.0 | 23.0 | 10.0 | 0 / 0 | 80.0 | 0.00 | 0.0 | 0.00 | 1 | 588.0 | 1.00 | 13,852.9 | 23.0 | -1.00 | -13,852.9 |
| 100 | 1 | 100.0 | 237.0 | 51.0 | 0 / 1 | 456.0 | 12.00 | 7,515.3 | 12.00 | 1 | 846.0 | 3.00 | 18,028.5 | 237.0 | 9.00 | -10,513.2 |
| rest | 1 | 144.0 | 378.0 | 65.0 | 0 / 3 | 717.0 | 14.00 | 10,076.8 | 14.00 | 1 | 871.0 | 3.00 | 18,028.5 | 378.0 | 11.00 | -7,951.7 |

| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | control tokens (sum) |
|---|---|---|---|---|---|---|
| 20 | read_known_path | 0 | 0 | 0 | 0 | 0 |
| 20 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 20 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 20 | search_transcript | 0 | 0 | 0 | 1 | 13,853 |
| 20 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 20 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| 100 | read_known_path | 0 | 0 | 0 | 1 | 1,392 |
| 100 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 100 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 100 | search_transcript | 12 | 7,515 | 12 | 2 | 16,636 |
| 100 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 100 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| rest | read_known_path | 1 | 508 | 1 | 1 | 1,392 |
| rest | rerun_command | 1 | 2,053 | 1 | 0 | 0 |
| rest | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| rest | search_transcript | 12 | 7,515 | 12 | 2 | 16,636 |
| rest | search_ledger | 0 | 0 | 0 | 0 | 0 |
| rest | search_live_state | 0 | 0 | 0 | 0 | 0 |

### R-B, per 100k of fill

| bin | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0k-100k | 3 | 89,056 | 3 | 0 | 0.00% | 0 / 0 (—) | 0 / 1 (0.00%) | 0 / 2 (0.00%) | 0 | — |
| 100k-200k | 66 | 164,350 | 72 | 0 | 0.00% | 0 / 0 (—) | 0 / 2 (0.00%) | 0 / 70 (0.00%) | 0 | — |
| 200k-300k | 84 | 245,879 | 84 | 1 | 1.19% | 0 / 0 (—) | 0 / 0 (—) | 0 / 80 (0.00%) | search_intercept 1 | Bash 1 |
| 300k-400k | 77 | 344,818 | 80 | 1 | 1.25% | 0 / 12 (0.00%) | 0 / 1 (0.00%) | 1 / 65 (1.54%) | 0 | Bash 1 |
| 400k-500k | 48 | 445,636 | 48 | 1 | 2.08% | 0 / 1 (0.00%) | 0 / 1 (0.00%) | 0 / 44 (0.00%) | 0 | Bash 1 |
| 500k-600k | 16 | 544,125 | 15 | 1 | 6.67% | 0 / 0 (—) | 0 / 1 (0.00%) | 0 / 13 (0.00%) | 0 | Bash 1 |
| 600k-700k | 41 | 651,222 | 48 | 1 | 2.08% | 0 / 17 (0.00%) | 0 / 0 (—) | 0 / 27 (0.00%) | quirk_guard 1 | Bash 1 |
| 700k-800k | 34 | 745,919 | 35 | 0 | 0.00% | 0 / 5 (0.00%) | 0 / 0 (—) | 0 / 30 (0.00%) | 0 | — |

### R-B, per segment third

| third | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| first | 123 | 211,287 | 130 | 1 | 0.77% | 0 / 4 (0.00%) | 0 / 3 (0.00%) | 0 / 119 (0.00%) | search_intercept 1 | Bash 1 |
| middle | 123 | 377,025 | 122 | 2 | 1.64% | 0 / 1 (0.00%) | 0 / 2 (0.00%) | 0 / 115 (0.00%) | 0 | Bash 2 |
| last | 123 | 553,778 | 133 | 2 | 1.50% | 0 / 30 (0.00%) | 0 / 1 (0.00%) | 1 / 97 (1.03%) | quirk_guard 1 | Bash 2 |

### Cost model (MODEL, not a measurement): included segments 2, kept start 90,872, observed compactions among them 1

| X | modeled compactions | requests | mean fill | cache-read tokens | read units | cache-write tokens | write units | summarizer reads | loss N=20: missed / re-fetch calls / tokens (raw) | loss N=100 (raw) | loss rest (raw) | loss N=100 (excess) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 300,000 | 4 | 369 | 194,671 | 70,423,228 | 3,521,161 | 1,410,389 | 2,820,778 | 1,193,459 | 92 / 0 / 0 | 948 / 48 / 30,061 | 1,512 / 56 / 40,307 | 948 / 36 / -42,053 |
| 400,000 | 3 | 369 | 240,518 | 87,417,702 | 4,370,885 | 1,333,333 | 2,666,666 | 1,197,083 | 69 / 0 / 0 | 711 / 36 / 22,546 | 1,134 / 42 / 30,230 | 711 / 27 / -31,540 |
| 500,000 | 2 | 369 | 288,831 | 105,344,783 | 5,267,239 | 1,233,798 | 2,467,596 | 986,531 | 46 / 0 / 0 | 474 / 24 / 15,031 | 756 / 28 / 20,154 | 474 / 18 / -21,026 |
| 600,000 | 1 | 369 | 348,498 | 127,436,291 | 6,371,815 | 1,159,655 | 2,319,310 | 598,698 | 23 / 0 / 0 | 237 / 12 / 7,515 | 378 / 14 / 10,077 | 237 / 9 / -10,513 |
| 700,000 | 1 | 369 | 357,502 | 130,775,958 | 6,538,798 | 1,142,286 | 2,284,572 | 688,716 | 23 / 0 / 0 | 237 / 12 / 7,515 | 378 / 14 / 10,077 | 237 / 9 / -10,513 |
| 785,000 | 1 | 369 | 381,526 | 139,623,937 | 6,981,197 | 1,159,201 | 2,318,402 | 784,988 | 23 / 0 / 0 | 237 / 12 / 7,515 | 378 / 14 / 10,077 | 237 / 9 / -10,513 |

## Run `sub-a4920ba3ae772b9d0`: agent-a4920ba3ae772b9d0.jsonl pinned at 12,926,645 bytes (sidechain thread)

- Requests 714; segments with requests 4; boundaries on the thread 3; skipped boundaries 0; models {'claude-opus-5-5': 714}.

### R-C, class `1M_window`: 3 boundaries, 2 control points

- Removed per boundary (modeled, mean): 438,263 tokens; last context before (mean) 780,973; kept start per boundary (modeled, mean) 33,098; first context after (mean) 70,278; postTokens (mean) 11,537.

| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) | control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) | excess missed | excess re-fetch calls | excess re-fetch tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 3 | 14.0 | 63.7 | 8.0 | 1 / 0 | 134.0 | 0.00 | 0.0 | 0.00 | 2 | 499.5 | 4.00 | 5,657.1 | 63.7 | -4.00 | -5,657.1 |
| 100 | 3 | 67.3 | 206.0 | 30.0 | 2 / 1 | 386.3 | 2.00 | 2,858.7 | 2.00 | 2 | 754.0 | 5.00 | 6,001.5 | 206.0 | -3.00 | -3,142.8 |
| rest | 3 | 173.0 | 443.0 | 49.3 | 2 / 4 | 712.0 | 7.67 | 7,732.1 | 7.67 | 2 | 786.0 | 8.00 | 6,981.1 | 443.0 | -0.33 | 750.9 |

| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | control tokens (sum) |
|---|---|---|---|---|---|---|
| 20 | read_known_path | 0 | 0 | 0 | 0 | 0 |
| 20 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 20 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 20 | search_transcript | 0 | 0 | 0 | 5 | 4,210 |
| 20 | search_ledger | 0 | 0 | 0 | 3 | 7,105 |
| 20 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| 100 | read_known_path | 0 | 0 | 0 | 0 | 0 |
| 100 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 100 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 100 | search_transcript | 5 | 7,734 | 5 | 7 | 4,898 |
| 100 | search_ledger | 1 | 843 | 1 | 3 | 7,105 |
| 100 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| rest | read_known_path | 0 | 0 | 0 | 0 | 0 |
| rest | rerun_command | 0 | 0 | 0 | 0 | 0 |
| rest | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| rest | search_transcript | 18 | 14,591 | 18 | 13 | 6,858 |
| rest | search_ledger | 5 | 8,605 | 5 | 3 | 7,105 |
| rest | search_live_state | 0 | 0 | 0 | 0 | 0 |

### R-B, per 100k of fill

| bin | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0k-100k | 23 | 84,719 | 24 | 0 | 0.00% | 0 / 0 (—) | 0 / 2 (0.00%) | 0 / 22 (0.00%) | 0 | — |
| 100k-200k | 107 | 146,514 | 107 | 0 | 0.00% | 0 / 0 (—) | 0 / 1 (0.00%) | 0 / 102 (0.00%) | 0 | — |
| 200k-300k | 99 | 246,541 | 101 | 1 | 0.99% | 0 / 0 (—) | 0 / 0 (—) | 0 / 101 (0.00%) | 0 | Bash 1 |
| 300k-400k | 109 | 347,612 | 119 | 4 | 3.36% | 0 / 16 (0.00%) | 0 / 1 (0.00%) | 0 / 101 (0.00%) | 0 | Bash 4 |
| 400k-500k | 81 | 446,393 | 85 | 2 | 2.35% | 0 / 10 (0.00%) | 0 / 6 (0.00%) | 0 / 67 (0.00%) | 0 | Bash 2 |
| 500k-600k | 94 | 546,535 | 97 | 2 | 2.06% | 0 / 5 (0.00%) | 0 / 3 (0.00%) | 0 / 89 (0.00%) | 0 | Bash 2 |
| 600k-700k | 99 | 653,628 | 100 | 1 | 1.00% | 0 / 7 (0.00%) | 0 / 1 (0.00%) | 0 / 91 (0.00%) | 0 | Bash 1 |
| 700k-800k | 102 | 745,815 | 101 | 2 | 1.98% | 0 / 3 (0.00%) | 0 / 2 (0.00%) | 0 / 93 (0.00%) | 0 | Bash 2 |

### R-B, per segment third

| third | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| first | 238 | 200,879 | 247 | 1 | 0.40% | 0 / 9 (0.00%) | 0 / 4 (0.00%) | 0 / 230 (0.00%) | 0 | Bash 1 |
| middle | 237 | 416,748 | 245 | 8 | 3.27% | 0 / 18 (0.00%) | 0 / 7 (0.00%) | 0 / 217 (0.00%) | 0 | Bash 8 |
| last | 237 | 681,434 | 241 | 3 | 1.24% | 0 / 14 (0.00%) | 0 / 5 (0.00%) | 0 / 218 (0.00%) | 0 | Bash 3 |

### Cost model (MODEL, not a measurement): included segments 4, kept start 70,278, observed compactions among them 3

| X | modeled compactions | requests | mean fill | cache-read tokens | read units | cache-write tokens | write units | summarizer reads | loss N=20: missed / re-fetch calls / tokens (raw) | loss N=100 (raw) | loss rest (raw) | loss N=100 (excess) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 300,000 | 9 | 714 | 182,255 | 127,315,270 | 6,365,764 | 2,814,844 | 5,629,688 | 2,677,227 | 573 / 0 / 0 | 1,854 / 18 / 25,729 | 3,987 / 69 / 69,589 | 1,854 / -27 / -28,285 |
| 400,000 | 6 | 714 | 227,117 | 159,551,706 | 7,977,585 | 2,609,940 | 5,219,880 | 2,384,161 | 382 / 0 / 0 | 1,236 / 12 / 17,152 | 2,658 / 46 / 46,392 | 1,236 / -18 / -18,857 |
| 500,000 | 4 | 714 | 283,970 | 200,288,656 | 10,014,433 | 2,466,256 | 4,932,512 | 1,971,296 | 255 / 0 / 0 | 824 / 8 / 11,435 | 1,772 / 31 / 30,928 | 824 / -12 / -12,571 |
| 600,000 | 4 | 714 | 353,312 | 249,800,321 | 12,490,016 | 2,464,569 | 4,929,138 | 2,372,421 | 255 / 0 / 0 | 824 / 8 / 11,435 | 1,772 / 31 / 30,928 | 824 / -12 / -12,571 |
| 700,000 | 3 | 714 | 352,480 | 249,249,901 | 12,462,495 | 2,421,037 | 4,842,074 | 2,092,112 | 191 / 0 / 0 | 618 / 6 / 8,576 | 1,329 / 23 / 23,196 | 618 / -9 / -9,428 |
| 785,000 | 3 | 714 | 431,389 | 305,609,577 | 15,280,479 | 2,402,041 | 4,804,082 | 2,331,763 | 191 / 0 / 0 | 618 / 6 / 8,576 | 1,329 / 23 / 23,196 | 618 / -9 / -9,428 |

## Run `sub-a4c0c331a18908947`: agent-a4c0c331a18908947.jsonl pinned at 5,021,742 bytes (sidechain thread)

- Requests 159; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; models {'claude-opus-5-5': 159}.

### R-C, class `1M_window`: 1 boundaries, 0 control points

- Removed per boundary (modeled, mean): 751,874 tokens; last context before (mean) 778,553; kept start per boundary (modeled, mean) 51,427; first context after (mean) 96,172; postTokens (mean) 15,025.

| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) | control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) | excess missed | excess re-fetch calls | excess re-fetch tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 3.0 | 6.0 | 0.0 | 0 / 0 | 41.0 | 2.00 | 1,597.8 | 2.00 | 0 | — | — | — | — | — | — |
| 100 | 1 | 3.0 | 6.0 | 0.0 | 0 / 0 | 41.0 | 2.00 | 1,597.8 | 2.00 | 0 | — | — | — | — | — | — |
| rest | 1 | 3.0 | 6.0 | 0.0 | 0 / 0 | 41.0 | 2.00 | 1,597.8 | 2.00 | 0 | — | — | — | — | — | — |

| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | control tokens (sum) |
|---|---|---|---|---|---|---|
| 20 | read_known_path | 0 | 0 | 0 | 0 | 0 |
| 20 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 20 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 20 | search_transcript | 2 | 1,598 | 2 | 0 | 0 |
| 20 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 20 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| 100 | read_known_path | 0 | 0 | 0 | 0 | 0 |
| 100 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 100 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 100 | search_transcript | 2 | 1,598 | 2 | 0 | 0 |
| 100 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 100 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| rest | read_known_path | 0 | 0 | 0 | 0 | 0 |
| rest | rerun_command | 0 | 0 | 0 | 0 | 0 |
| rest | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| rest | search_transcript | 2 | 1,598 | 2 | 0 | 0 |
| rest | search_ledger | 0 | 0 | 0 | 0 | 0 |
| rest | search_live_state | 0 | 0 | 0 | 0 | 0 |

### R-B, per 100k of fill

| bin | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0k-100k | 3 | 90,907 | 5 | 0 | 0.00% | 0 / 0 (—) | 0 / 1 (0.00%) | 0 / 4 (0.00%) | 0 | — |
| 100k-200k | 11 | 134,858 | 11 | 0 | 0.00% | 0 / 1 (0.00%) | 0 / 2 (0.00%) | 0 / 8 (0.00%) | 0 | — |
| 200k-300k | 34 | 249,041 | 34 | 1 | 2.94% | 0 / 4 (0.00%) | 0 / 0 (—) | 0 / 30 (0.00%) | 0 | Bash 1 |
| 300k-400k | 29 | 345,885 | 28 | 0 | 0.00% | 0 / 3 (0.00%) | 0 / 0 (—) | 0 / 24 (0.00%) | 0 | — |
| 400k-500k | 8 | 444,202 | 9 | 0 | 0.00% | 0 / 1 (0.00%) | 1 / 1 (100.00%) | 0 / 7 (0.00%) | 0 | — |
| 500k-600k | 27 | 555,473 | 27 | 0 | 0.00% | 0 / 4 (0.00%) | 0 / 0 (—) | 0 / 23 (0.00%) | 0 | — |
| 600k-700k | 20 | 637,314 | 19 | 0 | 0.00% | 0 / 1 (0.00%) | 0 / 1 (0.00%) | 0 / 16 (0.00%) | 0 | — |
| 700k-800k | 27 | 741,445 | 27 | 0 | 0.00% | 0 / 3 (0.00%) | 0 / 0 (—) | 0 / 23 (0.00%) | 0 | — |

### R-B, per segment third

| third | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| first | 53 | 229,192 | 56 | 1 | 1.79% | 0 / 7 (0.00%) | 0 / 3 (0.00%) | 0 / 46 (0.00%) | 0 | Bash 1 |
| middle | 53 | 444,447 | 53 | 0 | 0.00% | 0 / 6 (0.00%) | 1 / 1 (100.00%) | 0 / 45 (0.00%) | 0 | — |
| last | 53 | 676,755 | 51 | 0 | 0.00% | 0 / 4 (0.00%) | 0 / 1 (0.00%) | 0 / 44 (0.00%) | 0 | — |

### Cost model (MODEL, not a measurement): included segments 2, kept start 96,172, observed compactions among them 1

| X | modeled compactions | requests | mean fill | cache-read tokens | read units | cache-write tokens | write units | summarizer reads | loss N=20: missed / re-fetch calls / tokens (raw) | loss N=100 (raw) | loss rest (raw) | loss N=100 (excess) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 300,000 | 3 | 159 | 182,444 | 27,914,803 | 1,395,740 | 1,093,827 | 2,187,654 | 887,282 | 18 / 6 / 4,793 | 18 / 6 / 4,793 | 18 / 6 / 4,793 | — |
| 400,000 | 2 | 159 | 247,251 | 38,294,824 | 1,914,741 | 1,018,030 | 2,036,060 | 792,909 | 12 / 4 / 3,196 | 12 / 4 / 3,196 | 12 / 4 / 3,196 | — |
| 500,000 | 1 | 159 | 268,719 | 41,819,775 | 2,090,989 | 906,509 | 1,813,018 | 494,521 | 6 / 2 / 1,598 | 6 / 2 / 1,598 | 6 / 2 / 1,598 | — |
| 600,000 | 1 | 159 | 302,039 | 47,094,787 | 2,354,739 | 929,379 | 1,858,758 | 599,108 | 6 / 2 / 1,598 | 6 / 2 / 1,598 | 6 / 2 / 1,598 | — |
| 700,000 | 1 | 159 | 350,601 | 54,820,543 | 2,741,027 | 924,997 | 1,849,994 | 699,876 | 6 / 2 / 1,598 | 6 / 2 / 1,598 | 6 / 2 / 1,598 | — |
| 785,000 | 1 | 159 | 447,122 | 70,167,064 | 3,508,353 | 925,362 | 1,850,724 | 781,717 | 6 / 2 / 1,598 | 6 / 2 / 1,598 | 6 / 2 / 1,598 | — |

## Run `sub-a4f24691b2f13e97e`: agent-a4f24691b2f13e97e.jsonl pinned at 5,372,930 bytes (sidechain thread)

- Requests 285; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; models {'claude-opus-4-8': 36, 'claude-opus-5-5': 249}.

### R-C, class `1M_window`: 1 boundaries, 1 control points

- Removed per boundary (modeled, mean): 464,395 tokens; last context before (mean) 781,965; kept start per boundary (modeled, mean) 37,498; first context after (mean) 80,241; postTokens (mean) 16,129.

| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) | control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) | excess missed | excess re-fetch calls | excess re-fetch tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 20.0 | 54.0 | 8.0 | 0 / 0 | 156.0 | 8.00 | 15,079.5 | 8.00 | 1 | 102.0 | 0.00 | 0.0 | 54.0 | 8.00 | 15,079.5 |
| 100 | 1 | 68.0 | 271.0 | 15.0 | 0 / 0 | 551.0 | 8.00 | 15,079.5 | 8.00 | 1 | 757.0 | 3.00 | 32,570.8 | 271.0 | 5.00 | -17,491.3 |
| rest | 1 | 68.0 | 271.0 | 15.0 | 0 / 0 | 551.0 | 8.00 | 15,079.5 | 8.00 | 1 | 759.0 | 4.00 | 41,194.5 | 271.0 | 4.00 | -26,115.0 |

| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | control tokens (sum) |
|---|---|---|---|---|---|---|
| 20 | read_known_path | 0 | 0 | 0 | 0 | 0 |
| 20 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 20 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 20 | search_transcript | 8 | 15,080 | 8 | 0 | 0 |
| 20 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 20 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| 100 | read_known_path | 0 | 0 | 0 | 3 | 32,571 |
| 100 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 100 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 100 | search_transcript | 8 | 15,080 | 8 | 0 | 0 |
| 100 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 100 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| rest | read_known_path | 0 | 0 | 0 | 4 | 41,194 |
| rest | rerun_command | 0 | 0 | 0 | 0 | 0 |
| rest | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| rest | search_transcript | 8 | 15,080 | 8 | 0 | 0 |
| rest | search_ledger | 0 | 0 | 0 | 0 | 0 |
| rest | search_live_state | 0 | 0 | 0 | 0 | 0 |

### R-B, per 100k of fill

| bin | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0k-100k | 12 | 83,923 | 13 | 0 | 0.00% | 0 / 0 (—) | 0 / 3 (0.00%) | 0 / 10 (0.00%) | 0 | — |
| 100k-200k | 78 | 159,061 | 76 | 2 | 2.63% | 0 / 1 (0.00%) | 0 / 1 (0.00%) | 0 / 73 (0.00%) | 0 | Bash 2 |
| 200k-300k | 30 | 247,088 | 29 | 0 | 0.00% | 0 / 0 (—) | 0 / 0 (—) | 0 / 28 (0.00%) | 0 | — |
| 300k-400k | 38 | 353,184 | 38 | 1 | 2.63% | 0 / 4 (0.00%) | 0 / 0 (—) | 1 / 34 (2.94%) | 0 | Bash 1 |
| 400k-500k | 46 | 454,751 | 46 | 1 | 2.17% | 0 / 1 (0.00%) | 0 / 1 (0.00%) | 0 / 44 (0.00%) | 0 | Bash 1 |
| 500k-600k | 20 | 559,172 | 19 | 1 | 5.26% | 0 / 0 (—) | 0 / 3 (0.00%) | 0 / 15 (0.00%) | 0 | Bash 1 |
| 600k-700k | 37 | 651,007 | 37 | 1 | 2.70% | 0 / 4 (0.00%) | 0 / 0 (—) | 0 / 33 (0.00%) | 0 | Bash 1 |
| 700k-800k | 24 | 738,097 | 23 | 0 | 0.00% | 0 / 0 (—) | 0 / 3 (0.00%) | 0 / 19 (0.00%) | 0 | — |

### R-B, per segment third

| third | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| first | 96 | 206,858 | 97 | 0 | 0.00% | 0 / 4 (0.00%) | 0 / 4 (0.00%) | 1 / 88 (1.14%) | 0 | — |
| middle | 95 | 378,014 | 92 | 3 | 3.26% | 0 / 2 (0.00%) | 0 / 2 (0.00%) | 0 / 87 (0.00%) | 0 | Bash 3 |
| last | 94 | 557,248 | 92 | 3 | 3.26% | 0 / 4 (0.00%) | 0 / 5 (0.00%) | 0 / 81 (0.00%) | 0 | Bash 3 |

### Cost model (MODEL, not a measurement): included segments 2, kept start 80,241, observed compactions among them 1

| X | modeled compactions | requests | mean fill | cache-read tokens | read units | cache-write tokens | write units | summarizer reads | loss N=20: missed / re-fetch calls / tokens (raw) | loss N=100 (raw) | loss rest (raw) | loss N=100 (excess) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 300,000 | 3 | 285 | 189,872 | 53,010,457 | 2,650,523 | 1,137,365 | 2,274,730 | 869,522 | 162 / 24 / 45,238 | 813 / 24 / 45,238 | 813 / 24 / 45,238 | 813 / 15 / -52,474 |
| 400,000 | 2 | 285 | 230,400 | 64,587,949 | 3,229,398 | 1,110,396 | 2,220,792 | 797,126 | 108 / 16 / 30,159 | 542 / 16 / 30,159 | 542 / 16 / 30,159 | 542 / 10 / -34,983 |
| 500,000 | 1 | 285 | 330,611 | 93,227,408 | 4,661,370 | 1,030,997 | 2,061,994 | 499,326 | 54 / 8 / 15,080 | 271 / 8 / 15,080 | 271 / 8 / 15,080 | 271 / 5 / -17,491 |
| 600,000 | 1 | 285 | 318,952 | 89,903,312 | 4,495,166 | 1,032,270 | 2,064,540 | 597,060 | 54 / 8 / 15,080 | 271 / 8 / 15,080 | 271 / 8 / 15,080 | 271 / 5 / -17,491 |
| 700,000 | 1 | 285 | 352,892 | 99,575,597 | 4,978,780 | 1,032,688 | 2,065,376 | 699,181 | 54 / 8 / 15,080 | 271 / 8 / 15,080 | 271 / 8 / 15,080 | 271 / 5 / -17,491 |
| 785,000 | 1 | 285 | 380,966 | 107,586,236 | 5,379,312 | 1,023,293 | 2,046,586 | 778,426 | 54 / 8 / 15,080 | 271 / 8 / 15,080 | 271 / 8 / 15,080 | 271 / 5 / -17,491 |

## Run `sub-a58226189b58bf46f`: agent-a58226189b58bf46f.jsonl pinned at 6,874,791 bytes (sidechain thread)

- Requests 342; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; models {'claude-opus-5-5': 342}.

### R-C, class `1M_window`: 1 boundaries, 0 control points

- Removed per boundary (modeled, mean): 682,824 tokens; last context before (mean) 781,123; kept start per boundary (modeled, mean) 34,193; first context after (mean) 72,380; postTokens (mean) 13,067.

| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) | control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) | excess missed | excess re-fetch calls | excess re-fetch tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 20.0 | 36.0 | 5.0 | 0 / 0 | 91.0 | 6.00 | 10,610.3 | 6.00 | 0 | — | — | — | — | — | — |
| 100 | 1 | 100.0 | 260.0 | 53.0 | 2 / 2 | 535.0 | 21.00 | 47,044.7 | 20.00 | 0 | — | — | — | — | — | — |
| rest | 1 | 170.0 | 437.0 | 58.0 | 2 / 2 | 771.0 | 28.00 | 61,611.6 | 27.00 | 0 | — | — | — | — | — | — |

| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | control tokens (sum) |
|---|---|---|---|---|---|---|
| 20 | read_known_path | 0 | 0 | 0 | 0 | 0 |
| 20 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 20 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 20 | search_transcript | 6 | 10,610 | 6 | 0 | 0 |
| 20 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 20 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| 100 | read_known_path | 12 | 33,107 | 11 | 0 | 0 |
| 100 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 100 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 100 | search_transcript | 9 | 13,938 | 9 | 0 | 0 |
| 100 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 100 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| rest | read_known_path | 14 | 35,668 | 13 | 0 | 0 |
| rest | rerun_command | 0 | 0 | 0 | 0 | 0 |
| rest | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| rest | search_transcript | 14 | 25,944 | 14 | 0 | 0 |
| rest | search_ledger | 0 | 0 | 0 | 0 | 0 |
| rest | search_live_state | 0 | 0 | 0 | 0 | 0 |

### R-B, per 100k of fill

| bin | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0k-100k | 14 | 88,847 | 18 | 0 | 0.00% | 0 / 2 (0.00%) | 0 / 6 (0.00%) | 0 / 8 (0.00%) | 0 | — |
| 100k-200k | 73 | 158,143 | 74 | 0 | 0.00% | 0 / 1 (0.00%) | 0 / 8 (0.00%) | 0 / 65 (0.00%) | 0 | — |
| 200k-300k | 54 | 239,841 | 55 | 0 | 0.00% | 0 / 0 (—) | 0 / 7 (0.00%) | 0 / 48 (0.00%) | 0 | — |
| 300k-400k | 53 | 349,832 | 66 | 1 | 1.52% | 0 / 25 (0.00%) | 0 / 5 (0.00%) | 0 / 35 (0.00%) | 0 | Bash 1 |
| 400k-500k | 56 | 449,880 | 69 | 2 | 2.90% | 1 / 21 (4.76%) | 0 / 2 (0.00%) | 0 / 45 (0.00%) | 0 | Bash 1, Write 1 |
| 500k-600k | 26 | 554,520 | 32 | 0 | 0.00% | 0 / 10 (0.00%) | 0 / 0 (—) | 0 / 21 (0.00%) | 0 | — |
| 600k-700k | 38 | 653,042 | 40 | 1 | 2.50% | 0 / 1 (0.00%) | 0 / 5 (0.00%) | 0 / 33 (0.00%) | quirk_guard 1 | Bash 1 |
| 700k-800k | 28 | 745,968 | 28 | 1 | 3.57% | 0 / 0 (—) | 0 / 0 (—) | 0 / 28 (0.00%) | 0 | Bash 1 |

### R-B, per segment third

| third | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| first | 115 | 174,408 | 121 | 0 | 0.00% | 0 / 3 (0.00%) | 0 / 13 (0.00%) | 0 / 103 (0.00%) | 0 | — |
| middle | 114 | 391,592 | 142 | 1 | 0.70% | 0 / 45 (0.00%) | 0 / 18 (0.00%) | 0 / 77 (0.00%) | 0 | Bash 1 |
| last | 113 | 574,299 | 119 | 4 | 3.36% | 1 / 12 (8.33%) | 0 / 2 (0.00%) | 0 / 103 (0.00%) | quirk_guard 1 | Bash 3, Write 1 |

### Cost model (MODEL, not a measurement): included segments 2, kept start 72,380, observed compactions among them 1

| X | modeled compactions | requests | mean fill | cache-read tokens | read units | cache-write tokens | write units | summarizer reads | loss N=20: missed / re-fetch calls / tokens (raw) | loss N=100 (raw) | loss rest (raw) | loss N=100 (excess) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 300,000 | 4 | 342 | 183,467 | 61,285,003 | 3,064,250 | 1,460,595 | 2,921,190 | 1,184,351 | 144 / 24 / 42,441 | 1,040 / 84 / 188,179 | 1,748 / 112 / 246,446 | — |
| 400,000 | 3 | 342 | 219,391 | 73,663,388 | 3,683,169 | 1,368,224 | 2,736,448 | 1,167,082 | 108 / 18 / 31,831 | 780 / 63 / 141,134 | 1,311 / 84 / 184,835 | — |
| 500,000 | 2 | 342 | 282,819 | 95,400,763 | 4,770,038 | 1,323,361 | 2,646,722 | 977,630 | 72 / 12 / 21,221 | 520 / 42 / 94,089 | 874 / 56 / 123,223 | — |
| 600,000 | 2 | 342 | 305,422 | 103,102,172 | 5,155,109 | 1,352,116 | 2,704,232 | 1,195,462 | 72 / 12 / 21,221 | 520 / 42 / 94,089 | 874 / 56 / 123,223 | — |
| 700,000 | 1 | 342 | 370,521 | 125,434,271 | 6,271,714 | 1,284,011 | 2,568,022 | 699,102 | 36 / 6 / 10,610 | 260 / 21 / 47,045 | 437 / 28 / 61,612 | — |
| 785,000 | 1 | 342 | 379,597 | 128,537,225 | 6,426,861 | 1,284,913 | 2,569,826 | 784,900 | 36 / 6 / 10,610 | 260 / 21 / 47,045 | 437 / 28 / 61,612 | — |

## Run `sub-a60226a535b771d07`: agent-a60226a535b771d07.jsonl pinned at 5,746,951 bytes (sidechain thread)

- Requests 237; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; models {'claude-opus-5-5': 237}.

### R-C, class `1M_window`: 1 boundaries, 0 control points

- Removed per boundary (modeled, mean): 711,058 tokens; last context before (mean) 781,547; kept start per boundary (modeled, mean) 62,077; first context after (mean) 107,823; postTokens (mean) 22,075.

| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) | control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) | excess missed | excess re-fetch calls | excess re-fetch tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 20.0 | 25.0 | 4.0 | 0 / 1 | 88.0 | 11.00 | 21,288.6 | 11.00 | 0 | — | — | — | — | — | — |
| 100 | 1 | 93.0 | 199.0 | 31.0 | 3 / 3 | 557.0 | 41.00 | 89,158.0 | 41.00 | 0 | — | — | — | — | — | — |
| rest | 1 | 93.0 | 199.0 | 31.0 | 3 / 3 | 557.0 | 41.00 | 89,158.0 | 41.00 | 0 | — | — | — | — | — | — |

| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | control tokens (sum) |
|---|---|---|---|---|---|---|
| 20 | read_known_path | 1 | 13,786 | 1 | 0 | 0 |
| 20 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 20 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 20 | search_transcript | 10 | 7,503 | 10 | 0 | 0 |
| 20 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 20 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| 100 | read_known_path | 4 | 38,846 | 4 | 0 | 0 |
| 100 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 100 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 100 | search_transcript | 37 | 50,312 | 37 | 0 | 0 |
| 100 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 100 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| rest | read_known_path | 4 | 38,846 | 4 | 0 | 0 |
| rest | rerun_command | 0 | 0 | 0 | 0 | 0 |
| rest | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| rest | search_transcript | 37 | 50,312 | 37 | 0 | 0 |
| rest | search_ledger | 0 | 0 | 0 | 0 | 0 |
| rest | search_live_state | 0 | 0 | 0 | 0 | 0 |

### R-B, per 100k of fill

| bin | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0k-100k | 1 | 87,034 | 1 | 0 | 0.00% | 0 / 0 (—) | 0 / 1 (0.00%) | 0 / 0 (—) | 0 | — |
| 100k-200k | 31 | 173,817 | 34 | 3 | 8.82% | 0 / 1 (0.00%) | 0 / 6 (0.00%) | 0 / 27 (0.00%) | search_intercept 1 | Bash 3 |
| 200k-300k | 66 | 243,282 | 66 | 4 | 6.06% | 1 / 6 (16.67%) | 0 / 2 (0.00%) | 1 / 57 (1.75%) | 0 | Bash 3, Write 1 |
| 300k-400k | 28 | 350,811 | 27 | 1 | 3.70% | 0 / 1 (0.00%) | 0 / 3 (0.00%) | 0 / 22 (0.00%) | 0 | Bash 1 |
| 400k-500k | 10 | 476,344 | 26 | 0 | 0.00% | 0 / 24 (0.00%) | 0 / 0 (—) | 0 / 2 (0.00%) | 0 | — |
| 500k-600k | 30 | 553,664 | 40 | 2 | 5.00% | 0 / 16 (0.00%) | 0 / 0 (—) | 0 / 24 (0.00%) | 0 | Bash 2 |
| 600k-700k | 37 | 654,725 | 44 | 2 | 4.55% | 0 / 7 (0.00%) | 0 / 0 (—) | 1 / 37 (2.70%) | 0 | Bash 2 |
| 700k-800k | 34 | 746,932 | 36 | 0 | 0.00% | 0 / 4 (0.00%) | 0 / 0 (—) | 0 / 32 (0.00%) | 0 | — |

### R-B, per segment third

| third | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| first | 79 | 279,610 | 99 | 5 | 5.05% | 0 / 28 (0.00%) | 0 / 9 (0.00%) | 0 / 61 (0.00%) | search_intercept 1 | Bash 5 |
| middle | 79 | 455,848 | 93 | 5 | 5.38% | 0 / 22 (0.00%) | 0 / 0 (—) | 0 / 71 (0.00%) | 0 | Bash 5 |
| last | 79 | 560,093 | 82 | 2 | 2.44% | 1 / 9 (11.11%) | 0 / 3 (0.00%) | 2 / 69 (2.90%) | 0 | Bash 1, Write 1 |

### Cost model (MODEL, not a measurement): included segments 2, kept start 107,823, observed compactions among them 1

| X | modeled compactions | requests | mean fill | cache-read tokens | read units | cache-write tokens | write units | summarizer reads | loss N=20: missed / re-fetch calls / tokens (raw) | loss N=100 (raw) | loss rest (raw) | loss N=100 (excess) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 300,000 | 4 | 237 | 190,992 | 43,794,417 | 2,189,721 | 1,470,646 | 2,941,292 | 1,194,745 | 100 / 44 / 85,154 | 796 / 164 / 356,632 | 796 / 164 / 356,632 | — |
| 400,000 | 3 | 237 | 261,932 | 60,721,925 | 3,036,096 | 1,356,017 | 2,712,034 | 1,188,761 | 75 / 33 / 63,866 | 597 / 123 / 267,474 | 597 / 123 / 267,474 | — |
| 500,000 | 2 | 237 | 269,095 | 62,516,324 | 3,125,816 | 1,259,227 | 2,518,454 | 999,332 | 50 / 22 / 42,577 | 398 / 82 / 178,316 | 398 / 82 / 178,316 | — |
| 600,000 | 1 | 237 | 355,146 | 83,014,216 | 4,150,711 | 1,155,474 | 2,310,948 | 599,839 | 25 / 11 / 21,289 | 199 / 41 / 89,158 | 199 / 41 / 89,158 | — |
| 700,000 | 1 | 237 | 382,095 | 89,401,137 | 4,470,057 | 1,155,415 | 2,310,830 | 699,247 | 25 / 11 / 21,289 | 199 / 41 / 89,158 | 199 / 41 / 89,158 | — |
| 785,000 | 1 | 237 | 425,019 | 99,574,632 | 4,978,732 | 1,154,812 | 2,309,624 | 784,746 | 25 / 11 / 21,289 | 199 / 41 / 89,158 | 199 / 41 / 89,158 | — |

## Run `sub-a88c7c57f2fa2a96b`: agent-a88c7c57f2fa2a96b.jsonl pinned at 14,223,996 bytes (sidechain thread)

- Requests 723; segments with requests 4; boundaries on the thread 3; skipped boundaries 0; models {'claude-opus-5-5': 723}.

### R-C, class `1M_window`: 3 boundaries, 1 control points

- Removed per boundary (modeled, mean): 489,853 tokens; last context before (mean) 777,900; kept start per boundary (modeled, mean) 45,912; first context after (mean) 88,535; postTokens (mean) 22,068.

| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) | control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) | excess missed | excess re-fetch calls | excess re-fetch tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 3 | 20.0 | 36.3 | 14.0 | 1 / 1 | 100.3 | 7.67 | 10,652.3 | 7.67 | 1 | 168.0 | 12.00 | 7,986.1 | 36.3 | -4.33 | 2,666.2 |
| 100 | 3 | 100.0 | 207.3 | 39.3 | 1 / 4 | 465.7 | 49.67 | 61,850.5 | 45.00 | 1 | 800.0 | 50.00 | 61,103.6 | 207.3 | -0.33 | 746.9 |
| rest | 3 | 190.7 | 431.7 | 68.0 | 1 / 5 | 827.0 | 97.33 | 118,274.1 | 91.33 | 1 | 825.0 | 59.00 | 71,895.5 | 431.7 | 38.33 | 46,378.6 |

| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | control tokens (sum) |
|---|---|---|---|---|---|---|
| 20 | read_known_path | 0 | 0 | 0 | 0 | 0 |
| 20 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 20 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 20 | search_transcript | 23 | 31,957 | 23 | 12 | 7,986 |
| 20 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 20 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| 100 | read_known_path | 2 | 9,504 | 2 | 4 | 11,278 |
| 100 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 100 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 100 | search_transcript | 147 | 176,048 | 133 | 46 | 49,825 |
| 100 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 100 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| rest | read_known_path | 7 | 25,757 | 7 | 5 | 16,254 |
| rest | rerun_command | 0 | 0 | 0 | 0 | 0 |
| rest | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| rest | search_transcript | 285 | 329,065 | 267 | 54 | 55,642 |
| rest | search_ledger | 0 | 0 | 0 | 0 | 0 |
| rest | search_live_state | 0 | 0 | 0 | 0 | 0 |

### R-B, per 100k of fill

| bin | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0k-100k | 17 | 85,032 | 18 | 0 | 0.00% | 0 / 0 (—) | 0 / 2 (0.00%) | 0 / 16 (0.00%) | 0 | — |
| 100k-200k | 113 | 153,314 | 117 | 0 | 0.00% | 0 / 0 (—) | 0 / 10 (0.00%) | 0 / 105 (0.00%) | 0 | — |
| 200k-300k | 116 | 250,220 | 127 | 4 | 3.15% | 1 / 23 (4.35%) | 0 / 3 (0.00%) | 0 / 98 (0.00%) | 0 | Bash 3, Edit 1 |
| 300k-400k | 109 | 347,956 | 113 | 1 | 0.88% | 0 / 6 (0.00%) | 0 / 12 (0.00%) | 0 / 93 (0.00%) | search_intercept 1 | Grep 1 |
| 400k-500k | 99 | 456,649 | 110 | 2 | 1.82% | 0 / 24 (0.00%) | 0 / 3 (0.00%) | 0 / 83 (0.00%) | 0 | Bash 2 |
| 500k-600k | 97 | 551,958 | 99 | 1 | 1.01% | 1 / 11 (9.09%) | 0 / 2 (0.00%) | 0 / 85 (0.00%) | 0 | Write 1 |
| 600k-700k | 82 | 649,202 | 82 | 0 | 0.00% | 0 / 6 (0.00%) | 0 / 1 (0.00%) | 0 / 74 (0.00%) | 0 | — |
| 700k-800k | 90 | 738,690 | 90 | 2 | 2.22% | 0 / 4 (0.00%) | 0 / 1 (0.00%) | 0 / 85 (0.00%) | 0 | Bash 2 |

### R-B, per segment third

| third | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| first | 243 | 208,582 | 260 | 4 | 1.54% | 1 / 21 (4.76%) | 0 / 20 (0.00%) | 0 / 213 (0.00%) | search_intercept 1 | Bash 2, Edit 1, Grep 1 |
| middle | 240 | 421,359 | 258 | 2 | 0.78% | 0 / 44 (0.00%) | 0 / 9 (0.00%) | 0 / 204 (0.00%) | 0 | Bash 2 |
| last | 240 | 634,901 | 238 | 4 | 1.68% | 1 / 9 (11.11%) | 0 / 5 (0.00%) | 0 / 222 (0.00%) | 0 | Bash 3, Write 1 |

### Cost model (MODEL, not a measurement): included segments 4, kept start 88,535, observed compactions among them 3

| X | modeled compactions | requests | mean fill | cache-read tokens | read units | cache-write tokens | write units | summarizer reads | loss N=20: missed / re-fetch calls / tokens (raw) | loss N=100 (raw) | loss rest (raw) | loss N=100 (excess) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 300,000 | 11 | 723 | 197,138 | 138,988,677 | 6,949,434 | 3,541,971 | 7,083,942 | 3,247,353 | 400 / 84 / 117,176 | 2,281 / 546 / 680,356 | 4,748 / 1,071 / 1,301,015 | 2,281 / -4 / 8,216 |
| 400,000 | 8 | 723 | 238,098 | 168,781,451 | 8,439,073 | 3,363,254 | 6,726,508 | 3,166,924 | 291 / 61 / 85,219 | 1,659 / 397 / 494,804 | 3,453 / 779 / 946,192 | 1,659 / -3 / 5,976 |
| 500,000 | 6 | 723 | 279,733 | 199,026,581 | 9,951,329 | 3,220,526 | 6,441,051 | 2,979,617 | 218 / 46 / 63,914 | 1,244 / 298 / 371,103 | 2,590 / 584 / 709,644 | 1,244 / -2 / 4,482 |
| 600,000 | 5 | 723 | 353,510 | 252,509,918 | 12,625,496 | 3,077,736 | 6,155,472 | 2,949,158 | 182 / 38 / 53,262 | 1,037 / 248 / 309,253 | 2,158 / 487 / 591,370 | 1,037 / -2 / 3,735 |
| 700,000 | 4 | 723 | 367,948 | 262,990,325 | 13,149,516 | 3,036,004 | 6,072,009 | 2,795,096 | 145 / 31 / 42,609 | 829 / 199 / 247,402 | 1,727 / 389 / 473,096 | 829 / -1 / 2,988 |
| 785,000 | 3 | 723 | 426,207 | 305,174,853 | 15,258,743 | 2,973,094 | 5,946,187 | 2,348,846 | 109 / 23 / 31,957 | 622 / 149 / 185,552 | 1,295 / 292 / 354,822 | 622 / -1 / 2,241 |

## Run `sub-a90d7cc077452b42d`: agent-a90d7cc077452b42d.jsonl pinned at 5,722,161 bytes (sidechain thread)

- Requests 296; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; models {'claude-opus-5-5': 296}.

### R-C, class `1M_window`: 1 boundaries, 1 control points

- Removed per boundary (modeled, mean): 425,265 tokens; last context before (mean) 780,956; kept start per boundary (modeled, mean) 43,489; first context after (mean) 90,060; postTokens (mean) 20,512.

| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) | control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) | excess missed | excess re-fetch calls | excess re-fetch tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 20.0 | 21.0 | 5.0 | 0 / 0 | 115.0 | 8.00 | 11,670.6 | 8.00 | 1 | 188.0 | 9.00 | 14,751.4 | 21.0 | -1.00 | -3,080.8 |
| 100 | 1 | 96.0 | 267.0 | 48.0 | 0 / 0 | 618.0 | 39.00 | 50,450.5 | 39.00 | 1 | 678.0 | 31.00 | 42,265.8 | 267.0 | 8.00 | 8,184.7 |
| rest | 1 | 96.0 | 267.0 | 48.0 | 0 / 0 | 618.0 | 39.00 | 50,450.5 | 39.00 | 1 | 678.0 | 31.00 | 42,265.8 | 267.0 | 8.00 | 8,184.7 |

| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | control tokens (sum) |
|---|---|---|---|---|---|---|
| 20 | read_known_path | 0 | 0 | 0 | 0 | 0 |
| 20 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 20 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 20 | search_transcript | 8 | 11,671 | 8 | 9 | 14,751 |
| 20 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 20 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| 100 | read_known_path | 0 | 0 | 0 | 0 | 0 |
| 100 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 100 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 100 | search_transcript | 39 | 50,450 | 39 | 31 | 42,266 |
| 100 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 100 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| rest | read_known_path | 0 | 0 | 0 | 0 | 0 |
| rest | rerun_command | 0 | 0 | 0 | 0 | 0 |
| rest | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| rest | search_transcript | 39 | 50,450 | 39 | 31 | 42,266 |
| rest | search_ledger | 0 | 0 | 0 | 0 | 0 |
| rest | search_live_state | 0 | 0 | 0 | 0 | 0 |

### R-B, per 100k of fill

| bin | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0k-100k | 10 | 85,440 | 11 | 0 | 0.00% | 0 / 0 (—) | 0 / 5 (0.00%) | 0 / 6 (0.00%) | 0 | — |
| 100k-200k | 69 | 158,040 | 69 | 2 | 2.90% | 0 / 0 (—) | 0 / 3 (0.00%) | 0 / 63 (0.00%) | 0 | Bash 2 |
| 200k-300k | 59 | 244,559 | 59 | 2 | 3.39% | 0 / 4 (0.00%) | 0 / 0 (—) | 0 / 55 (0.00%) | 0 | Bash 2 |
| 300k-400k | 48 | 343,821 | 47 | 1 | 2.13% | 0 / 4 (0.00%) | 0 / 0 (—) | 0 / 42 (0.00%) | 0 | Bash 1 |
| 400k-500k | 34 | 447,846 | 34 | 2 | 5.88% | 0 / 2 (0.00%) | 0 / 0 (—) | 0 / 32 (0.00%) | 0 | Bash 2 |
| 500k-600k | 36 | 545,904 | 36 | 1 | 2.78% | 0 / 1 (0.00%) | 0 / 0 (—) | 0 / 35 (0.00%) | 0 | Bash 1 |
| 600k-700k | 15 | 639,949 | 14 | 0 | 0.00% | 0 / 0 (—) | 0 / 5 (0.00%) | 0 / 7 (0.00%) | 0 | — |
| 700k-800k | 25 | 741,613 | 25 | 0 | 0.00% | 0 / 6 (0.00%) | 0 / 0 (—) | 0 / 19 (0.00%) | 0 | — |

### R-B, per segment third

| third | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| first | 99 | 174,294 | 100 | 2 | 2.00% | 0 / 5 (0.00%) | 0 / 8 (0.00%) | 0 / 84 (0.00%) | 0 | Bash 2 |
| middle | 99 | 362,513 | 99 | 5 | 5.05% | 0 / 6 (0.00%) | 0 / 0 (—) | 0 / 93 (0.00%) | 0 | Bash 5 |
| last | 98 | 536,394 | 96 | 1 | 1.04% | 0 / 6 (0.00%) | 0 / 5 (0.00%) | 0 / 82 (0.00%) | 0 | Bash 1 |

### Cost model (MODEL, not a measurement): included segments 2, kept start 90,060, observed compactions among them 1

| X | modeled compactions | requests | mean fill | cache-read tokens | read units | cache-write tokens | write units | summarizer reads | loss N=20: missed / re-fetch calls / tokens (raw) | loss N=100 (raw) | loss rest (raw) | loss N=100 (excess) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 300,000 | 4 | 296 | 182,349 | 52,560,054 | 2,628,003 | 1,415,164 | 2,830,328 | 1,168,119 | 84 / 32 / 46,682 | 1,068 / 156 / 201,802 | 1,068 / 156 / 201,802 | 1,068 / 32 / 32,739 |
| 400,000 | 3 | 296 | 231,923 | 67,327,241 | 3,366,362 | 1,322,059 | 2,644,118 | 1,174,454 | 63 / 24 / 35,012 | 801 / 117 / 151,352 | 801 / 117 / 151,352 | 801 / 24 / 24,554 |
| 500,000 | 2 | 296 | 272,897 | 79,513,423 | 3,975,671 | 1,263,964 | 2,527,928 | 994,580 | 42 / 16 / 23,341 | 534 / 78 / 100,901 | 534 / 78 / 100,901 | 534 / 16 / 16,369 |
| 600,000 | 1 | 296 | 362,278 | 106,051,839 | 5,302,592 | 1,182,441 | 2,364,882 | 599,936 | 21 / 8 / 11,671 | 267 / 39 / 50,450 | 267 / 39 / 50,450 | 267 / 8 / 8,185 |
| 700,000 | 1 | 296 | 342,397 | 100,194,977 | 5,009,749 | 1,154,596 | 2,309,192 | 696,690 | 21 / 8 / 11,671 | 267 / 39 / 50,450 | 267 / 39 / 50,450 | 267 / 8 / 8,185 |
| 785,000 | 1 | 296 | 364,866 | 106,819,694 | 5,340,985 | 1,180,494 | 2,360,988 | 782,533 | 21 / 8 / 11,671 | 267 / 39 / 50,450 | 267 / 39 / 50,450 | 267 / 8 / 8,185 |

## Run `sub-aa842df27d05dd80d`: agent-aa842df27d05dd80d.jsonl pinned at 5,739,552 bytes (sidechain thread)

- Requests 198; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; models {'claude-opus-5-5': 198}.

### R-C, class `1M_window`: 1 boundaries, 0 control points

- Removed per boundary (modeled, mean): 710,088 tokens; last context before (mean) 742,912; kept start per boundary (modeled, mean) 53,761; first context after (mean) 96,415; postTokens (mean) 16,305.

| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) | control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) | excess missed | excess re-fetch calls | excess re-fetch tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 20.0 | 14.0 | 2.0 | 0 / 0 | 57.0 | 17.00 | 32,568.9 | 17.00 | 0 | — | — | — | — | — | — |
| 100 | 1 | 100.0 | 201.0 | 16.0 | 0 / 1 | 484.0 | 53.00 | 86,437.3 | 53.00 | 0 | — | — | — | — | — | — |
| rest | 1 | 111.0 | 346.0 | 19.0 | 0 / 2 | 750.0 | 59.00 | 104,529.5 | 58.00 | 0 | — | — | — | — | — | — |

| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | control tokens (sum) |
|---|---|---|---|---|---|---|
| 20 | read_known_path | 0 | 0 | 0 | 0 | 0 |
| 20 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 20 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 20 | search_transcript | 17 | 32,569 | 17 | 0 | 0 |
| 20 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 20 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| 100 | read_known_path | 0 | 0 | 0 | 0 | 0 |
| 100 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 100 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 100 | search_transcript | 53 | 86,437 | 53 | 0 | 0 |
| 100 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 100 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| rest | read_known_path | 0 | 0 | 0 | 0 | 0 |
| rest | rerun_command | 0 | 0 | 0 | 0 | 0 |
| rest | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| rest | search_transcript | 59 | 104,530 | 58 | 0 | 0 |
| rest | search_ledger | 0 | 0 | 0 | 0 | 0 |
| rest | search_live_state | 0 | 0 | 0 | 0 | 0 |

### R-B, per 100k of fill

| bin | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0k-100k | 5 | 93,135 | 5 | 0 | 0.00% | 0 / 0 (—) | 0 / 1 (0.00%) | 0 / 4 (0.00%) | 0 | — |
| 100k-200k | 48 | 152,188 | 52 | 0 | 0.00% | 0 / 4 (0.00%) | 0 / 3 (0.00%) | 0 / 45 (0.00%) | 0 | — |
| 200k-300k | 43 | 251,005 | 43 | 1 | 2.33% | 0 / 4 (0.00%) | 0 / 0 (—) | 0 / 39 (0.00%) | 0 | Bash 1 |
| 300k-400k | 52 | 348,758 | 57 | 3 | 5.26% | 0 / 8 (0.00%) | 0 / 0 (—) | 0 / 44 (0.00%) | search_intercept 1 | Bash 2, Grep 1 |
| 400k-500k | 20 | 466,101 | 21 | 0 | 0.00% | 0 / 5 (0.00%) | 0 / 0 (—) | 0 / 16 (0.00%) | 0 | — |
| 500k-600k | 17 | 541,970 | 19 | 1 | 5.26% | 1 / 6 (16.67%) | 0 / 3 (0.00%) | 0 / 10 (0.00%) | 0 | Write 1 |
| 600k-700k | 8 | 673,211 | 8 | 0 | 0.00% | 0 / 1 (0.00%) | 0 / 2 (0.00%) | 0 / 5 (0.00%) | 0 | — |
| 700k-800k | 5 | 726,185 | 5 | 0 | 0.00% | 0 / 2 (0.00%) | 0 / 1 (0.00%) | 0 / 2 (0.00%) | 0 | — |

### R-B, per segment third

| third | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| first | 66 | 171,322 | 72 | 2 | 2.78% | 0 / 5 (0.00%) | 0 / 4 (0.00%) | 0 / 61 (0.00%) | search_intercept 1 | Bash 1, Grep 1 |
| middle | 66 | 334,994 | 70 | 0 | 0.00% | 0 / 13 (0.00%) | 0 / 0 (—) | 0 / 57 (0.00%) | 0 | — |
| last | 66 | 467,191 | 68 | 3 | 4.41% | 1 / 12 (8.33%) | 0 / 6 (0.00%) | 0 / 47 (0.00%) | 0 | Bash 2, Write 1 |

### Cost model (MODEL, not a measurement): included segments 2, kept start 96,415, observed compactions among them 1

| X | modeled compactions | requests | mean fill | cache-read tokens | read units | cache-write tokens | write units | summarizer reads | loss N=20: missed / re-fetch calls / tokens (raw) | loss N=100 (raw) | loss rest (raw) | loss N=100 (excess) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 300,000 | 4 | 198 | 189,306 | 36,064,546 | 1,803,227 | 1,418,030 | 2,836,060 | 1,178,838 | 56 / 68 / 130,276 | 804 / 212 / 345,749 | 1,384 / 236 / 418,118 | — |
| 400,000 | 3 | 198 | 245,951 | 47,372,510 | 2,368,626 | 1,325,759 | 2,651,518 | 1,191,909 | 42 / 51 / 97,707 | 603 / 159 / 259,312 | 1,038 / 177 / 313,588 | — |
| 500,000 | 2 | 198 | 276,957 | 53,593,307 | 2,679,665 | 1,244,195 | 2,488,390 | 996,065 | 28 / 34 / 65,138 | 402 / 106 / 172,875 | 692 / 118 / 209,059 | — |
| 600,000 | 1 | 198 | 372,771 | 72,673,889 | 3,633,694 | 1,134,805 | 2,269,610 | 588,014 | 14 / 17 / 32,569 | 201 / 53 / 86,437 | 346 / 59 / 104,530 | — |
| 700,000 | 1 | 198 | 337,932 | 65,759,094 | 3,287,955 | 1,151,406 | 2,302,812 | 697,774 | 14 / 17 / 32,569 | 201 / 53 / 86,437 | 346 / 59 / 104,530 | — |
| 785,000 | 1 | 198 | 344,528 | 67,067,123 | 3,353,356 | 1,149,339 | 2,298,678 | 784,605 | 14 / 17 / 32,569 | 201 / 53 / 86,437 | 346 / 59 / 104,530 | — |

## Run `sub-aad0e50d8019b70bb`: agent-aad0e50d8019b70bb.jsonl pinned at 4,660,437 bytes (sidechain thread)

- Requests 179; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; models {'claude-opus-5-5': 179}.

### R-C, class `1M_window`: 1 boundaries, 0 control points

- Removed per boundary (modeled, mean): 438,271 tokens; last context before (mean) 781,057; kept start per boundary (modeled, mean) 34,314; first context after (mean) 75,460; postTokens (mean) 13,802.

| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) | control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) | excess missed | excess re-fetch calls | excess re-fetch tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 6.0 | 114.0 | 10.0 | 0 / 0 | 302.0 | 1.00 | 7,040.9 | 1.00 | 0 | — | — | — | — | — | — |
| 100 | 1 | 6.0 | 114.0 | 10.0 | 0 / 0 | 302.0 | 1.00 | 7,040.9 | 1.00 | 0 | — | — | — | — | — | — |
| rest | 1 | 6.0 | 114.0 | 10.0 | 0 / 0 | 302.0 | 1.00 | 7,040.9 | 1.00 | 0 | — | — | — | — | — | — |

| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | control tokens (sum) |
|---|---|---|---|---|---|---|
| 20 | read_known_path | 1 | 7,041 | 1 | 0 | 0 |
| 20 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 20 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 20 | search_transcript | 0 | 0 | 0 | 0 | 0 |
| 20 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 20 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| 100 | read_known_path | 1 | 7,041 | 1 | 0 | 0 |
| 100 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 100 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 100 | search_transcript | 0 | 0 | 0 | 0 | 0 |
| 100 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 100 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| rest | read_known_path | 1 | 7,041 | 1 | 0 | 0 |
| rest | rerun_command | 0 | 0 | 0 | 0 | 0 |
| rest | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| rest | search_transcript | 0 | 0 | 0 | 0 | 0 |
| rest | search_ledger | 0 | 0 | 0 | 0 | 0 |
| rest | search_live_state | 0 | 0 | 0 | 0 | 0 |

### R-B, per 100k of fill

| bin | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0k-100k | 5 | 81,729 | 6 | 0 | 0.00% | 0 / 0 (—) | 0 / 2 (0.00%) | 0 / 4 (0.00%) | 0 | — |
| 100k-200k | 18 | 133,750 | 25 | 0 | 0.00% | 0 / 0 (—) | 0 / 9 (0.00%) | 0 / 15 (0.00%) | 0 | — |
| 200k-300k | 15 | 237,641 | 20 | 0 | 0.00% | 0 / 0 (—) | 0 / 0 (—) | 0 / 20 (0.00%) | 0 | — |
| 300k-400k | 25 | 369,322 | 25 | 1 | 4.00% | 0 / 0 (—) | 0 / 0 (—) | 0 / 25 (0.00%) | 0 | Bash 1 |
| 400k-500k | 40 | 444,520 | 40 | 1 | 2.50% | 0 / 0 (—) | 0 / 0 (—) | 0 / 40 (0.00%) | 0 | Bash 1 |
| 500k-600k | 31 | 535,622 | 30 | 1 | 3.33% | 0 / 0 (—) | 0 / 2 (0.00%) | 0 / 27 (0.00%) | 0 | Bash 1 |
| 600k-700k | 13 | 652,862 | 19 | 0 | 0.00% | 0 / 0 (—) | 0 / 7 (0.00%) | 1 / 12 (8.33%) | 0 | — |
| 700k-800k | 32 | 745,212 | 32 | 0 | 0.00% | 0 / 0 (—) | 0 / 1 (0.00%) | 0 / 31 (0.00%) | 0 | — |

### R-B, per segment third

| third | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| first | 60 | 259,735 | 74 | 1 | 1.35% | 0 / 0 (—) | 0 / 11 (0.00%) | 0 / 63 (0.00%) | 0 | Bash 1 |
| middle | 60 | 457,301 | 60 | 1 | 1.67% | 0 / 0 (—) | 0 / 0 (—) | 0 / 60 (0.00%) | 0 | Bash 1 |
| last | 59 | 666,283 | 63 | 1 | 1.59% | 0 / 0 (—) | 0 / 10 (0.00%) | 1 / 51 (1.96%) | 0 | Bash 1 |

### Cost model (MODEL, not a measurement): included segments 2, kept start 75,460, observed compactions among them 1

| X | modeled compactions | requests | mean fill | cache-read tokens | read units | cache-write tokens | write units | summarizer reads | loss N=20: missed / re-fetch calls / tokens (raw) | loss N=100 (raw) | loss rest (raw) | loss N=100 (excess) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 300,000 | 3 | 179 | 190,662 | 33,169,747 | 1,658,487 | 958,655 | 1,917,310 | 871,747 | 342 / 3 / 21,123 | 342 / 3 / 21,123 | 342 / 3 / 21,123 | — |
| 400,000 | 2 | 179 | 206,800 | 36,045,375 | 1,802,269 | 971,913 | 1,943,826 | 799,132 | 228 / 2 / 14,082 | 228 / 2 / 14,082 | 228 / 2 / 14,082 | — |
| 500,000 | 1 | 179 | 291,263 | 51,243,399 | 2,562,170 | 892,613 | 1,785,226 | 499,570 | 114 / 1 / 7,041 | 114 / 1 / 7,041 | 114 / 1 / 7,041 | — |
| 600,000 | 1 | 179 | 336,188 | 59,295,807 | 2,964,790 | 881,843 | 1,763,686 | 584,776 | 114 / 1 / 7,041 | 114 / 1 / 7,041 | 114 / 1 / 7,041 | — |
| 700,000 | 1 | 179 | 353,384 | 62,357,827 | 3,117,891 | 897,872 | 1,795,744 | 698,677 | 114 / 1 / 7,041 | 114 / 1 / 7,041 | 114 / 1 / 7,041 | — |
| 785,000 | 1 | 179 | 454,550 | 80,462,831 | 4,023,142 | 901,564 | 1,803,128 | 784,495 | 114 / 1 / 7,041 | 114 / 1 / 7,041 | 114 / 1 / 7,041 | — |

## Run `sub-ab1c8cf107bc6ad72`: agent-ab1c8cf107bc6ad72.jsonl pinned at 4,544,022 bytes (sidechain thread)

- Requests 193; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; models {'claude-opus-5-5': 193}.

### R-C, class `1M_window`: 1 boundaries, 0 control points

- Removed per boundary (modeled, mean): 668,626 tokens; last context before (mean) 780,682; kept start per boundary (modeled, mean) 49,466; first context after (mean) 88,302; postTokens (mean) 13,214.

| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) | control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) | excess missed | excess re-fetch calls | excess re-fetch tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 7.0 | 15.0 | 0.0 | 0 / 0 | 116.0 | 2.00 | 4,151.1 | 2.00 | 0 | — | — | — | — | — | — |
| 100 | 1 | 7.0 | 15.0 | 0.0 | 0 / 0 | 116.0 | 2.00 | 4,151.1 | 2.00 | 0 | — | — | — | — | — | — |
| rest | 1 | 7.0 | 15.0 | 0.0 | 0 / 0 | 116.0 | 2.00 | 4,151.1 | 2.00 | 0 | — | — | — | — | — | — |

| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | control tokens (sum) |
|---|---|---|---|---|---|---|
| 20 | read_known_path | 1 | 2,549 | 1 | 0 | 0 |
| 20 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 20 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 20 | search_transcript | 0 | 0 | 0 | 0 | 0 |
| 20 | search_ledger | 1 | 1,602 | 1 | 0 | 0 |
| 20 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| 100 | read_known_path | 1 | 2,549 | 1 | 0 | 0 |
| 100 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 100 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 100 | search_transcript | 0 | 0 | 0 | 0 | 0 |
| 100 | search_ledger | 1 | 1,602 | 1 | 0 | 0 |
| 100 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| rest | read_known_path | 1 | 2,549 | 1 | 0 | 0 |
| rest | rerun_command | 0 | 0 | 0 | 0 | 0 |
| rest | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| rest | search_transcript | 0 | 0 | 0 | 0 | 0 |
| rest | search_ledger | 1 | 1,602 | 1 | 0 | 0 |
| rest | search_live_state | 0 | 0 | 0 | 0 | 0 |

### R-B, per 100k of fill

| bin | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0k-100k | 3 | 85,560 | 3 | 0 | 0.00% | 0 / 0 (—) | 0 / 1 (0.00%) | 0 / 2 (0.00%) | 0 | — |
| 100k-200k | 22 | 155,170 | 23 | 0 | 0.00% | 0 / 1 (0.00%) | 0 / 9 (0.00%) | 0 / 12 (0.00%) | 0 | — |
| 200k-300k | 19 | 250,514 | 21 | 0 | 0.00% | 0 / 0 (—) | 0 / 15 (0.00%) | 0 / 6 (0.00%) | 0 | — |
| 300k-400k | 28 | 349,048 | 28 | 1 | 3.57% | 0 / 1 (0.00%) | 0 / 7 (0.00%) | 0 / 20 (0.00%) | 0 | Read 1 |
| 400k-500k | 25 | 451,146 | 27 | 1 | 3.70% | 0 / 6 (0.00%) | 0 / 0 (—) | 0 / 21 (0.00%) | 0 | Bash 1 |
| 500k-600k | 37 | 547,916 | 37 | 0 | 0.00% | 0 / 2 (0.00%) | 0 / 3 (0.00%) | 0 / 32 (0.00%) | 0 | — |
| 600k-700k | 38 | 639,563 | 38 | 0 | 0.00% | 0 / 4 (0.00%) | 0 / 0 (—) | 0 / 34 (0.00%) | 0 | — |
| 700k-800k | 21 | 738,653 | 32 | 0 | 0.00% | 0 / 20 (0.00%) | 0 / 5 (0.00%) | 0 / 7 (0.00%) | 0 | — |

### R-B, per segment third

| third | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| first | 65 | 253,719 | 69 | 1 | 1.45% | 0 / 2 (0.00%) | 0 / 31 (0.00%) | 0 / 36 (0.00%) | 0 | Read 1 |
| middle | 64 | 487,609 | 66 | 1 | 1.52% | 0 / 8 (0.00%) | 0 / 4 (0.00%) | 0 / 54 (0.00%) | 0 | Bash 1 |
| last | 64 | 654,242 | 74 | 0 | 0.00% | 0 / 24 (0.00%) | 0 / 5 (0.00%) | 0 / 44 (0.00%) | 0 | — |

### Cost model (MODEL, not a measurement): included segments 2, kept start 88,302, observed compactions among them 1

| X | modeled compactions | requests | mean fill | cache-read tokens | read units | cache-write tokens | write units | summarizer reads | loss N=20: missed / re-fetch calls / tokens (raw) | loss N=100 (raw) | loss rest (raw) | loss N=100 (excess) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 300,000 | 3 | 193 | 189,966 | 35,581,940 | 1,779,097 | 1,081,514 | 2,163,028 | 897,713 | 45 / 6 / 12,453 | 45 / 6 / 12,453 | 45 / 6 / 12,453 | — |
| 400,000 | 2 | 193 | 241,767 | 45,658,063 | 2,282,903 | 1,002,989 | 2,005,978 | 795,572 | 30 / 4 / 8,302 | 30 / 4 / 8,302 | 30 / 4 / 8,302 | — |
| 500,000 | 1 | 193 | 268,730 | 50,943,460 | 2,547,173 | 921,514 | 1,843,028 | 499,032 | 15 / 2 / 4,151 | 15 / 2 / 4,151 | 15 / 2 / 4,151 | — |
| 600,000 | 1 | 193 | 313,974 | 59,678,017 | 2,983,901 | 918,981 | 1,837,962 | 598,292 | 15 / 2 / 4,151 | 15 / 2 / 4,151 | 15 / 2 / 4,151 | — |
| 700,000 | 1 | 193 | 396,256 | 75,564,306 | 3,778,215 | 913,135 | 1,826,270 | 693,346 | 15 / 2 / 4,151 | 15 / 2 / 4,151 | 15 / 2 / 4,151 | — |
| 785,000 | 1 | 193 | 458,854 | 87,636,825 | 4,381,841 | 922,025 | 1,844,050 | 784,837 | 15 / 2 / 4,151 | 15 / 2 / 4,151 | 15 / 2 / 4,151 | — |

## Run `sub-ac753871198ee8cfd`: agent-ac753871198ee8cfd.jsonl pinned at 9,748,808 bytes (sidechain thread)

- Requests 425; segments with requests 3; boundaries on the thread 2; skipped boundaries 0; models {'claude-opus-5-5': 425}.

### R-C, class `1M_window`: 2 boundaries, 1 control points

- Removed per boundary (modeled, mean): 437,042 tokens; last context before (mean) 778,574; kept start per boundary (modeled, mean) 38,343; first context after (mean) 77,870; postTokens (mean) 16,644.

| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) | control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) | excess missed | excess re-fetch calls | excess re-fetch tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 2 | 20.0 | 27.0 | 3.5 | 1 / 1 | 88.0 | 7.50 | 29,200.3 | 7.50 | 1 | 476.0 | 1.00 | 14,878.7 | 27.0 | 6.50 | 14,321.6 |
| 100 | 2 | 62.5 | 159.5 | 18.0 | 1 / 1 | 353.5 | 12.50 | 40,251.8 | 12.50 | 1 | 881.0 | 7.00 | 39,393.7 | 159.5 | 5.50 | 858.1 |
| rest | 2 | 116.0 | 272.5 | 28.0 | 1 / 1 | 528.5 | 16.50 | 60,477.8 | 16.50 | 1 | 884.0 | 7.00 | 39,393.7 | 272.5 | 9.50 | 21,084.0 |

| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | control tokens (sum) |
|---|---|---|---|---|---|---|
| 20 | read_known_path | 7 | 51,952 | 7 | 0 | 0 |
| 20 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 20 | identical_other_call | 1 | 20 | 1 | 0 | 0 |
| 20 | search_transcript | 5 | 5,053 | 5 | 1 | 14,879 |
| 20 | search_ledger | 2 | 1,375 | 2 | 0 | 0 |
| 20 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| 100 | read_known_path | 9 | 56,765 | 9 | 3 | 6,530 |
| 100 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 100 | identical_other_call | 2 | 41 | 2 | 0 | 0 |
| 100 | search_transcript | 12 | 22,323 | 12 | 3 | 32,418 |
| 100 | search_ledger | 2 | 1,375 | 2 | 0 | 0 |
| 100 | search_live_state | 0 | 0 | 0 | 1 | 445 |
| rest | read_known_path | 13 | 64,354 | 13 | 3 | 6,530 |
| rest | rerun_command | 0 | 0 | 0 | 0 | 0 |
| rest | identical_other_call | 2 | 41 | 2 | 0 | 0 |
| rest | search_transcript | 15 | 54,741 | 15 | 3 | 32,418 |
| rest | search_ledger | 2 | 1,375 | 2 | 0 | 0 |
| rest | search_live_state | 1 | 445 | 1 | 1 | 445 |

### R-B, per 100k of fill

| bin | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0k-100k | 13 | 85,360 | 16 | 0 | 0.00% | 0 / 0 (—) | 0 / 4 (0.00%) | 0 / 9 (0.00%) | 0 | — |
| 100k-200k | 63 | 159,787 | 64 | 0 | 0.00% | 0 / 0 (—) | 0 / 7 (0.00%) | 0 / 55 (0.00%) | 0 | — |
| 200k-300k | 54 | 245,541 | 63 | 1 | 1.59% | 0 / 29 (0.00%) | 0 / 2 (0.00%) | 0 / 30 (0.00%) | 0 | Bash 1 |
| 300k-400k | 49 | 358,628 | 54 | 3 | 5.56% | 0 / 18 (0.00%) | 0 / 1 (0.00%) | 0 / 34 (0.00%) | 0 | Bash 3 |
| 400k-500k | 66 | 448,983 | 68 | 0 | 0.00% | 0 / 5 (0.00%) | 0 / 2 (0.00%) | 0 / 60 (0.00%) | 0 | — |
| 500k-600k | 57 | 542,980 | 58 | 1 | 1.72% | 1 / 5 (20.00%) | 0 / 4 (0.00%) | 0 / 48 (0.00%) | 0 | Write 1 |
| 600k-700k | 58 | 654,880 | 66 | 0 | 0.00% | 0 / 24 (0.00%) | 0 / 4 (0.00%) | 0 / 38 (0.00%) | 0 | — |
| 700k-800k | 65 | 741,533 | 76 | 1 | 1.32% | 0 / 12 (0.00%) | 0 / 8 (0.00%) | 0 / 55 (0.00%) | 0 | Bash 1 |

### R-B, per segment third

| third | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| first | 143 | 221,630 | 155 | 4 | 2.58% | 0 / 38 (0.00%) | 0 / 13 (0.00%) | 0 / 98 (0.00%) | 0 | Bash 4 |
| middle | 141 | 452,985 | 152 | 0 | 0.00% | 0 / 23 (0.00%) | 0 / 8 (0.00%) | 0 / 120 (0.00%) | 0 | — |
| last | 141 | 661,062 | 158 | 2 | 1.27% | 1 / 32 (3.12%) | 0 / 11 (0.00%) | 0 / 111 (0.00%) | 0 | Bash 1, Write 1 |

### Cost model (MODEL, not a measurement): included segments 3, kept start 77,870, observed compactions among them 2

| X | modeled compactions | requests | mean fill | cache-read tokens | read units | cache-write tokens | write units | summarizer reads | loss N=20: missed / re-fetch calls / tokens (raw) | loss N=100 (raw) | loss rest (raw) | loss N=100 (excess) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 300,000 | 6 | 425 | 193,601 | 80,281,372 | 4,014,069 | 1,998,923 | 3,997,846 | 1,759,665 | 162 / 45 / 175,202 | 957 / 75 / 241,511 | 1,635 / 99 / 362,866 | 957 / 33 / 5,149 |
| 400,000 | 4 | 425 | 221,108 | 92,066,203 | 4,603,310 | 1,904,782 | 3,809,564 | 1,591,293 | 108 / 30 / 116,801 | 638 / 50 / 161,007 | 1,090 / 66 / 241,911 | 638 / 22 / 3,432 |
| 500,000 | 3 | 425 | 255,244 | 106,629,323 | 5,331,466 | 1,849,355 | 3,698,710 | 1,498,212 | 81 / 22 / 87,601 | 478 / 38 / 120,755 | 818 / 50 / 181,433 | 478 / 16 / 2,574 |
| 600,000 | 2 | 425 | 361,156 | 151,736,670 | 7,586,834 | 1,754,501 | 3,509,002 | 1,197,992 | 54 / 15 / 58,401 | 319 / 25 / 80,504 | 545 / 33 / 120,956 | 319 / 11 / 1,716 |
| 700,000 | 2 | 425 | 355,527 | 149,327,420 | 7,466,371 | 1,771,410 | 3,542,820 | 1,399,475 | 54 / 15 / 58,401 | 319 / 25 / 80,504 | 545 / 33 / 120,956 | 319 / 11 / 1,716 |
| 785,000 | 2 | 425 | 444,774 | 187,276,935 | 9,363,847 | 1,751,944 | 3,503,888 | 1,558,082 | 54 / 15 / 58,401 | 319 / 25 / 80,504 | 545 / 33 / 120,956 | 319 / 11 / 1,716 |

## Run `sub-ac9c149483559ffec`: agent-ac9c149483559ffec.jsonl pinned at 5,663,224 bytes (sidechain thread)

- Requests 210; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; models {'claude-opus-5-5': 210}.

### R-C, class `1M_window`: 1 boundaries, 0 control points

- Removed per boundary (modeled, mean): 726,933 tokens; last context before (mean) 783,019; kept start per boundary (modeled, mean) 57,847; first context after (mean) 101,421; postTokens (mean) 19,649.

| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) | control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) | excess missed | excess re-fetch calls | excess re-fetch tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 20.0 | 33.0 | 14.0 | 1 / 1 | 99.0 | 6.00 | 28,851.5 | 6.00 | 0 | — | — | — | — | — | — |
| 100 | 1 | 62.0 | 220.0 | 37.0 | 2 / 1 | 640.0 | 21.00 | 64,194.6 | 20.00 | 0 | — | — | — | — | — | — |
| rest | 1 | 62.0 | 220.0 | 37.0 | 2 / 1 | 640.0 | 21.00 | 64,194.6 | 20.00 | 0 | — | — | — | — | — | — |

| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | control tokens (sum) |
|---|---|---|---|---|---|---|
| 20 | read_known_path | 2 | 9,985 | 2 | 0 | 0 |
| 20 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 20 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 20 | search_transcript | 4 | 18,867 | 4 | 0 | 0 |
| 20 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 20 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| 100 | read_known_path | 6 | 19,121 | 5 | 0 | 0 |
| 100 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 100 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 100 | search_transcript | 15 | 45,074 | 15 | 0 | 0 |
| 100 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 100 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| rest | read_known_path | 6 | 19,121 | 5 | 0 | 0 |
| rest | rerun_command | 0 | 0 | 0 | 0 | 0 |
| rest | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| rest | search_transcript | 15 | 45,074 | 15 | 0 | 0 |
| rest | search_ledger | 0 | 0 | 0 | 0 | 0 |
| rest | search_live_state | 0 | 0 | 0 | 0 | 0 |

### R-B, per 100k of fill

| bin | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0k-100k | 1 | 84,833 | 1 | 0 | 0.00% | 0 / 0 (—) | 0 / 1 (0.00%) | 0 / 0 (—) | 0 | — |
| 100k-200k | 25 | 155,270 | 31 | 0 | 0.00% | 0 / 1 (0.00%) | 0 / 9 (0.00%) | 0 / 21 (0.00%) | 0 | — |
| 200k-300k | 54 | 252,078 | 59 | 0 | 0.00% | 0 / 7 (0.00%) | 0 / 7 (0.00%) | 0 / 45 (0.00%) | 0 | — |
| 300k-400k | 35 | 320,352 | 38 | 0 | 0.00% | 0 / 13 (0.00%) | 0 / 1 (0.00%) | 0 / 22 (0.00%) | 0 | — |
| 400k-500k | 12 | 458,149 | 12 | 0 | 0.00% | 0 / 0 (—) | 0 / 0 (—) | 0 / 12 (0.00%) | 0 | — |
| 500k-600k | 22 | 558,759 | 25 | 2 | 8.00% | 0 / 8 (0.00%) | 0 / 1 (0.00%) | 0 / 15 (0.00%) | 0 | Bash 2 |
| 600k-700k | 30 | 651,928 | 33 | 1 | 3.03% | 0 / 10 (0.00%) | 0 / 0 (—) | 0 / 23 (0.00%) | 0 | Bash 1 |
| 700k-800k | 31 | 746,952 | 31 | 1 | 3.23% | 0 / 1 (0.00%) | 0 / 0 (—) | 0 / 29 (0.00%) | 0 | Bash 1 |

### R-B, per segment third

| third | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| first | 71 | 231,765 | 81 | 0 | 0.00% | 0 / 9 (0.00%) | 0 / 13 (0.00%) | 0 / 58 (0.00%) | 0 | — |
| middle | 70 | 449,312 | 75 | 2 | 2.67% | 0 / 12 (0.00%) | 0 / 5 (0.00%) | 0 / 57 (0.00%) | 0 | Bash 2 |
| last | 69 | 599,822 | 74 | 2 | 2.70% | 0 / 19 (0.00%) | 0 / 1 (0.00%) | 0 / 52 (0.00%) | 0 | Bash 2 |

### Cost model (MODEL, not a measurement): included segments 2, kept start 101,421, observed compactions among them 1

| X | modeled compactions | requests | mean fill | cache-read tokens | read units | cache-write tokens | write units | summarizer reads | loss N=20: missed / re-fetch calls / tokens (raw) | loss N=100 (raw) | loss rest (raw) | loss N=100 (excess) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 300,000 | 4 | 210 | 189,282 | 38,340,178 | 1,917,009 | 1,409,111 | 2,818,222 | 1,190,727 | 132 / 24 / 115,406 | 880 / 84 / 256,778 | 880 / 84 / 256,778 | — |
| 400,000 | 2 | 210 | 264,731 | 54,424,831 | 2,721,242 | 1,168,726 | 2,337,452 | 781,279 | 66 / 12 / 57,703 | 440 / 42 / 128,389 | 440 / 42 / 128,389 | — |
| 500,000 | 2 | 210 | 271,831 | 55,870,969 | 2,793,548 | 1,213,510 | 2,427,020 | 995,126 | 66 / 12 / 57,703 | 440 / 42 / 128,389 | 440 / 42 / 128,389 | — |
| 600,000 | 1 | 210 | 338,895 | 70,051,506 | 3,502,575 | 1,116,517 | 2,233,034 | 597,892 | 33 / 6 / 28,852 | 220 / 21 / 64,195 | 220 / 21 / 64,195 | — |
| 700,000 | 1 | 210 | 363,006 | 75,118,271 | 3,755,914 | 1,113,018 | 2,226,036 | 695,476 | 33 / 6 / 28,852 | 220 / 21 / 64,195 | 220 / 21 / 64,195 | — |
| 785,000 | 1 | 210 | 414,312 | 85,889,849 | 4,294,492 | 1,115,714 | 2,231,428 | 784,279 | 33 / 6 / 28,852 | 220 / 21 / 64,195 | 220 / 21 / 64,195 | — |

## Run `sub-acc9cf211b3e34071`: agent-acc9cf211b3e34071.jsonl pinned at 5,654,864 bytes (sidechain thread)

- Requests 223; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; models {'claude-opus-5-5': 223}.

### R-C, class `1M_window`: 1 boundaries, 0 control points

- Removed per boundary (modeled, mean): 701,128 tokens; last context before (mean) 782,891; kept start per boundary (modeled, mean) 56,130; first context after (mean) 102,046; postTokens (mean) 17,631.

| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) | control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) | excess missed | excess re-fetch calls | excess re-fetch tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 20.0 | 51.0 | 8.0 | 0 / 0 | 161.0 | 11.00 | 20,305.4 | 11.00 | 0 | — | — | — | — | — | — |
| 100 | 1 | 84.0 | 268.0 | 24.0 | 0 / 2 | 604.0 | 29.00 | 55,908.4 | 29.00 | 0 | — | — | — | — | — | — |
| rest | 1 | 84.0 | 268.0 | 24.0 | 0 / 2 | 604.0 | 29.00 | 55,908.4 | 29.00 | 0 | — | — | — | — | — | — |

| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | control tokens (sum) |
|---|---|---|---|---|---|---|
| 20 | read_known_path | 0 | 0 | 0 | 0 | 0 |
| 20 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 20 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 20 | search_transcript | 11 | 20,305 | 11 | 0 | 0 |
| 20 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 20 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| 100 | read_known_path | 0 | 0 | 0 | 0 | 0 |
| 100 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 100 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 100 | search_transcript | 29 | 55,908 | 29 | 0 | 0 |
| 100 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 100 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| rest | read_known_path | 0 | 0 | 0 | 0 | 0 |
| rest | rerun_command | 0 | 0 | 0 | 0 | 0 |
| rest | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| rest | search_transcript | 29 | 55,908 | 29 | 0 | 0 |
| rest | search_ledger | 0 | 0 | 0 | 0 | 0 |
| rest | search_live_state | 0 | 0 | 0 | 0 | 0 |

### R-B, per 100k of fill

| bin | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0k-100k | 2 | 90,176 | 3 | 0 | 0.00% | 0 / 0 (—) | 0 / 2 (0.00%) | 0 / 1 (0.00%) | 0 | — |
| 100k-200k | 42 | 153,195 | 43 | 0 | 0.00% | 0 / 5 (0.00%) | 0 / 1 (0.00%) | 0 / 36 (0.00%) | 0 | — |
| 200k-300k | 55 | 249,621 | 55 | 0 | 0.00% | 0 / 4 (0.00%) | 0 / 0 (—) | 0 / 48 (0.00%) | 0 | — |
| 300k-400k | 41 | 343,211 | 40 | 0 | 0.00% | 0 / 12 (0.00%) | 0 / 0 (—) | 0 / 27 (0.00%) | 0 | — |
| 400k-500k | 35 | 448,946 | 35 | 1 | 2.86% | 0 / 6 (0.00%) | 0 / 0 (—) | 0 / 29 (0.00%) | 0 | Bash 1 |
| 500k-600k | 11 | 522,444 | 10 | 1 | 10.00% | 0 / 2 (0.00%) | 0 / 2 (0.00%) | 0 / 5 (0.00%) | 0 | Bash 1 |
| 600k-700k | 16 | 654,226 | 16 | 0 | 0.00% | 0 / 1 (0.00%) | 0 / 1 (0.00%) | 0 / 14 (0.00%) | 0 | — |
| 700k-800k | 21 | 745,537 | 21 | 0 | 0.00% | 0 / 2 (0.00%) | 0 / 1 (0.00%) | 0 / 18 (0.00%) | 0 | — |

### R-B, per segment third

| third | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| first | 75 | 215,057 | 77 | 0 | 0.00% | 0 / 13 (0.00%) | 0 / 3 (0.00%) | 0 / 60 (0.00%) | 0 | — |
| middle | 74 | 359,366 | 74 | 2 | 2.70% | 0 / 11 (0.00%) | 0 / 0 (—) | 0 / 60 (0.00%) | 0 | Bash 2 |
| last | 74 | 530,769 | 72 | 0 | 0.00% | 0 / 8 (0.00%) | 0 / 4 (0.00%) | 0 / 58 (0.00%) | 0 | — |

### Cost model (MODEL, not a measurement): included segments 2, kept start 102,046, observed compactions among them 1

| X | modeled compactions | requests | mean fill | cache-read tokens | read units | cache-write tokens | write units | summarizer reads | loss N=20: missed / re-fetch calls / tokens (raw) | loss N=100 (raw) | loss rest (raw) | loss N=100 (excess) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 300,000 | 4 | 223 | 196,168 | 42,347,177 | 2,117,359 | 1,398,207 | 2,796,414 | 1,172,120 | 204 / 44 / 81,222 | 1,072 / 116 / 223,634 | 1,072 / 116 / 223,634 | — |
| 400,000 | 3 | 223 | 246,110 | 53,573,985 | 2,678,699 | 1,308,573 | 2,617,146 | 1,182,478 | 153 / 33 / 60,916 | 804 / 87 / 167,725 | 804 / 87 / 167,725 | — |
| 500,000 | 2 | 223 | 297,524 | 65,121,215 | 3,256,061 | 1,226,714 | 2,453,428 | 991,071 | 102 / 22 / 40,611 | 536 / 58 / 111,817 | 536 / 58 / 111,817 | — |
| 600,000 | 1 | 223 | 362,279 | 79,693,984 | 3,984,699 | 1,094,141 | 2,188,282 | 566,731 | 51 / 11 / 20,305 | 268 / 29 / 55,908 | 268 / 29 / 55,908 | — |
| 700,000 | 1 | 223 | 350,258 | 76,982,081 | 3,849,104 | 1,125,456 | 2,250,912 | 699,644 | 51 / 11 / 20,305 | 268 / 29 / 55,908 | 268 / 29 / 55,908 | — |
| 785,000 | 1 | 223 | 365,386 | 80,351,373 | 4,017,569 | 1,129,717 | 2,259,434 | 781,972 | 51 / 11 / 20,305 | 268 / 29 / 55,908 | 268 / 29 / 55,908 | — |

## Run `sub-ae66dca0f21a920b6`: agent-ae66dca0f21a920b6.jsonl pinned at 3,861,913 bytes (sidechain thread)

- Requests 197; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; models {'claude-opus-5-5': 197}.

### R-C, class `1M_window`: 1 boundaries, 0 control points

- Removed per boundary (modeled, mean): 546,407 tokens; last context before (mean) 771,483; kept start per boundary (modeled, mean) 40,730; first context after (mean) 81,324; postTokens (mean) 18,188.

| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) | control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) | excess missed | excess re-fetch calls | excess re-fetch tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 1.0 | 0.0 | 0.0 | 0 / 0 | 0.0 | 0.00 | 0.0 | 0.00 | 0 | — | — | — | — | — | — |
| 100 | 1 | 1.0 | 0.0 | 0.0 | 0 / 0 | 0.0 | 0.00 | 0.0 | 0.00 | 0 | — | — | — | — | — | — |
| rest | 1 | 1.0 | 0.0 | 0.0 | 0 / 0 | 0.0 | 0.00 | 0.0 | 0.00 | 0 | — | — | — | — | — | — |

| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | control tokens (sum) |
|---|---|---|---|---|---|---|
| 20 | read_known_path | 0 | 0 | 0 | 0 | 0 |
| 20 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 20 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 20 | search_transcript | 0 | 0 | 0 | 0 | 0 |
| 20 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 20 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| 100 | read_known_path | 0 | 0 | 0 | 0 | 0 |
| 100 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 100 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 100 | search_transcript | 0 | 0 | 0 | 0 | 0 |
| 100 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 100 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| rest | read_known_path | 0 | 0 | 0 | 0 | 0 |
| rest | rerun_command | 0 | 0 | 0 | 0 | 0 |
| rest | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| rest | search_transcript | 0 | 0 | 0 | 0 | 0 |
| rest | search_ledger | 0 | 0 | 0 | 0 | 0 |
| rest | search_live_state | 0 | 0 | 0 | 0 | 0 |

### R-B, per 100k of fill

| bin | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0k-100k | 7 | 86,085 | 7 | 0 | 0.00% | 0 / 0 (—) | 0 / 1 (0.00%) | 0 / 6 (0.00%) | 0 | — |
| 100k-200k | 15 | 147,489 | 17 | 0 | 0.00% | 0 / 0 (—) | 0 / 8 (0.00%) | 0 / 9 (0.00%) | 0 | — |
| 200k-300k | 10 | 246,760 | 11 | 0 | 0.00% | 0 / 0 (—) | 0 / 11 (0.00%) | 0 / 0 (—) | 0 | — |
| 300k-400k | 21 | 352,782 | 23 | 0 | 0.00% | 0 / 0 (—) | 0 / 2 (0.00%) | 0 / 21 (0.00%) | 0 | — |
| 400k-500k | 42 | 446,322 | 42 | 2 | 4.76% | 0 / 0 (—) | 0 / 0 (—) | 0 / 42 (0.00%) | 0 | Bash 2 |
| 500k-600k | 34 | 554,784 | 34 | 0 | 0.00% | 0 / 0 (—) | 0 / 0 (—) | 0 / 31 (0.00%) | 0 | — |
| 600k-700k | 44 | 651,910 | 44 | 0 | 0.00% | 0 / 0 (—) | 0 / 0 (—) | 0 / 44 (0.00%) | 0 | — |
| 700k-800k | 24 | 723,930 | 24 | 0 | 0.00% | 0 / 0 (—) | 0 / 0 (—) | 0 / 23 (0.00%) | 0 | — |

### R-B, per segment third

| third | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| first | 66 | 278,704 | 72 | 1 | 1.39% | 0 / 0 (—) | 0 / 22 (0.00%) | 0 / 50 (0.00%) | 0 | Bash 1 |
| middle | 65 | 517,395 | 65 | 1 | 1.54% | 0 / 0 (—) | 0 / 0 (—) | 0 / 62 (0.00%) | 0 | Bash 1 |
| last | 65 | 680,784 | 65 | 0 | 0.00% | 0 / 0 (—) | 0 / 0 (—) | 0 / 64 (0.00%) | 0 | — |

### Cost model (MODEL, not a measurement): included segments 2, kept start 81,324, observed compactions among them 1

| X | modeled compactions | requests | mean fill | cache-read tokens | read units | cache-write tokens | write units | summarizer reads | loss N=20: missed / re-fetch calls / tokens (raw) | loss N=100 (raw) | loss rest (raw) | loss N=100 (excess) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 300,000 | 3 | 197 | 195,568 | 37,517,051 | 1,875,853 | 1,009,826 | 2,019,652 | 883,192 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | — |
| 400,000 | 2 | 197 | 232,699 | 44,906,118 | 2,245,306 | 935,501 | 1,871,002 | 792,547 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | — |
| 500,000 | 1 | 197 | 278,243 | 53,954,283 | 2,697,714 | 859,503 | 1,719,006 | 494,509 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | — |
| 600,000 | 1 | 197 | 313,732 | 60,940,206 | 3,047,010 | 864,901 | 1,729,802 | 599,982 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | — |
| 700,000 | 1 | 197 | 415,048 | 80,901,720 | 4,045,086 | 862,835 | 1,725,670 | 699,488 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | — |
| 785,000 | 1 | 197 | 499,484 | 97,548,467 | 4,877,423 | 849,849 | 1,699,698 | 768,525 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | — |

## Run `sub-af25a8ffadcb62c75`: agent-af25a8ffadcb62c75.jsonl pinned at 6,606,908 bytes (sidechain thread)

- Requests 239; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; models {'claude-opus-5-5': 239}.

### R-C, class `1M_window`: 1 boundaries, 0 control points

- Removed per boundary (modeled, mean): 458,166 tokens; last context before (mean) 782,657; kept start per boundary (modeled, mean) 39,176; first context after (mean) 79,382; postTokens (mean) 17,218.

| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) | control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) | excess missed | excess re-fetch calls | excess re-fetch tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 20.0 | 58.0 | 6.0 | 0 / 1 | 165.0 | 8.00 | 47,177.1 | 7.00 | 0 | — | — | — | — | — | — |
| 100 | 1 | 100.0 | 273.0 | 20.0 | 1 / 1 | 551.0 | 31.00 | 68,906.2 | 29.00 | 0 | — | — | — | — | — | — |
| rest | 1 | 117.0 | 680.0 | 21.0 | 1 / 1 | 1,073.0 | 35.00 | 72,834.8 | 33.00 | 0 | — | — | — | — | — | — |

| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | control tokens (sum) |
|---|---|---|---|---|---|---|
| 20 | read_known_path | 7 | 46,022 | 6 | 0 | 0 |
| 20 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 20 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 20 | search_transcript | 1 | 1,155 | 1 | 0 | 0 |
| 20 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 20 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| 100 | read_known_path | 11 | 50,260 | 9 | 0 | 0 |
| 100 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 100 | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| 100 | search_transcript | 20 | 18,647 | 20 | 0 | 0 |
| 100 | search_ledger | 0 | 0 | 0 | 0 | 0 |
| 100 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| rest | read_known_path | 12 | 52,756 | 10 | 0 | 0 |
| rest | rerun_command | 0 | 0 | 0 | 0 | 0 |
| rest | identical_other_call | 0 | 0 | 0 | 0 | 0 |
| rest | search_transcript | 23 | 20,079 | 23 | 0 | 0 |
| rest | search_ledger | 0 | 0 | 0 | 0 | 0 |
| rest | search_live_state | 0 | 0 | 0 | 0 | 0 |

### R-B, per 100k of fill

| bin | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0k-100k | 11 | 80,773 | 14 | 0 | 0.00% | 0 / 0 (—) | 0 / 7 (0.00%) | 0 / 7 (0.00%) | 0 | — |
| 100k-200k | 29 | 159,306 | 35 | 0 | 0.00% | 0 / 11 (0.00%) | 0 / 6 (0.00%) | 0 / 16 (0.00%) | 0 | — |
| 200k-300k | 42 | 257,993 | 49 | 0 | 0.00% | 0 / 18 (0.00%) | 0 / 1 (0.00%) | 0 / 27 (0.00%) | 0 | — |
| 300k-400k | 38 | 358,405 | 60 | 1 | 1.67% | 0 / 32 (0.00%) | 0 / 3 (0.00%) | 0 / 25 (0.00%) | 0 | Bash 1 |
| 400k-500k | 53 | 444,230 | 66 | 0 | 0.00% | 0 / 25 (0.00%) | 0 / 3 (0.00%) | 0 / 37 (0.00%) | 0 | — |
| 500k-600k | 35 | 543,097 | 37 | 1 | 2.70% | 0 / 5 (0.00%) | 0 / 4 (0.00%) | 0 / 28 (0.00%) | 0 | Bash 1 |
| 600k-700k | 12 | 636,005 | 13 | 1 | 7.69% | 1 / 1 (100.00%) | 0 / 1 (0.00%) | 0 / 10 (0.00%) | 0 | Write 1 |
| 700k-800k | 19 | 740,320 | 23 | 0 | 0.00% | 0 / 15 (0.00%) | 0 / 2 (0.00%) | 0 / 6 (0.00%) | 0 | — |

### R-B, per segment third

| third | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| first | 80 | 220,733 | 100 | 0 | 0.00% | 0 / 40 (0.00%) | 0 / 13 (0.00%) | 0 / 42 (0.00%) | 0 | — |
| middle | 80 | 410,174 | 100 | 2 | 2.00% | 0 / 35 (0.00%) | 0 / 6 (0.00%) | 0 / 59 (0.00%) | 0 | Bash 2 |
| last | 79 | 553,692 | 97 | 1 | 1.03% | 1 / 32 (3.12%) | 0 / 8 (0.00%) | 0 / 55 (0.00%) | 0 | Write 1 |

### Cost model (MODEL, not a measurement): included segments 2, kept start 79,382, observed compactions among them 1

| X | modeled compactions | requests | mean fill | cache-read tokens | read units | cache-write tokens | write units | summarizer reads | loss N=20: missed / re-fetch calls / tokens (raw) | loss N=100 (raw) | loss rest (raw) | loss N=100 (excess) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 300,000 | 5 | 239 | 180,438 | 41,587,633 | 2,079,382 | 1,537,026 | 3,074,052 | 1,438,353 | 290 / 40 / 235,886 | 1,365 / 155 / 344,531 | 3,400 / 175 / 364,174 | — |
| 400,000 | 3 | 239 | 213,511 | 49,627,488 | 2,481,374 | 1,401,672 | 2,803,344 | 1,154,842 | 174 / 24 / 141,531 | 819 / 93 / 206,719 | 2,040 / 105 / 218,504 | — |
| 500,000 | 2 | 239 | 259,694 | 60,717,147 | 3,035,857 | 1,349,596 | 2,699,192 | 984,622 | 116 / 16 / 94,354 | 546 / 62 / 137,812 | 1,360 / 70 / 145,670 | — |
| 600,000 | 2 | 239 | 363,622 | 85,538,086 | 4,276,904 | 1,367,675 | 2,735,350 | 1,197,796 | 116 / 16 / 94,354 | 546 / 62 / 137,812 | 1,360 / 70 / 145,670 | — |
| 700,000 | 1 | 239 | 386,109 | 91,045,142 | 4,552,257 | 1,234,881 | 2,469,762 | 661,545 | 58 / 8 / 47,177 | 273 / 31 / 68,906 | 680 / 35 / 72,835 | — |
| 785,000 | 1 | 239 | 398,438 | 93,941,971 | 4,697,098 | 1,284,832 | 2,569,664 | 778,182 | 58 / 8 / 47,177 | 273 / 31 / 68,906 | 680 / 35 / 72,835 | — |

## Subagent files pooled: 16 files, 21 boundaries, 7 control points

### R-C, pooled

| N | real boundaries | mean window requests | missed (mean) | missed paths (mean) | of them read / edited before (sum) | reused (mean) | re-fetch calls (mean) | re-fetch tokens (mean) | re-fetch requests (mean) | control points | control reused (mean) | control re-fetch calls (mean) | control re-fetch tokens (mean) | excess missed | excess re-fetch calls | excess re-fetch tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 21 | 16.1 | 38.3 | 6.9 | 4 / 5 | 111.9 | 5.62 | 13,842.8 | 5.57 | 7 | 360.1 | 4.43 | 8,969.0 | 38.3 | 1.19 | 4,873.8 |
| 100 | 21 | 68.9 | 185.2 | 26.1 | 12 / 17 | 415.1 | 20.95 | 36,767.4 | 20.10 | 7 | 781.4 | 14.86 | 29,337.9 | 185.2 | 6.10 | 7,429.5 |
| rest | 21 | 108.8 | 303.3 | 35.0 | 12 / 24 | 591.1 | 29.86 | 49,314.6 | 28.76 | 7 | 798.4 | 17.14 | 32,391.5 | 303.3 | 12.71 | 16,923.2 |

| N | shape | real calls (sum) | real tokens (sum) | real requests (sum) | control calls (sum) | control tokens (sum) |
|---|---|---|---|---|---|---|
| 20 | read_known_path | 19 | 131,335 | 18 | 0 | 0 |
| 20 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 20 | identical_other_call | 1 | 20 | 1 | 0 | 0 |
| 20 | search_transcript | 95 | 156,367 | 95 | 28 | 55,679 |
| 20 | search_ledger | 3 | 2,977 | 3 | 3 | 7,105 |
| 20 | search_live_state | 0 | 0 | 0 | 0 | 0 |
| 100 | read_known_path | 46 | 217,191 | 42 | 11 | 51,772 |
| 100 | rerun_command | 0 | 0 | 0 | 0 | 0 |
| 100 | identical_other_call | 2 | 41 | 2 | 0 | 0 |
| 100 | search_transcript | 388 | 551,064 | 374 | 89 | 146,044 |
| 100 | search_ledger | 4 | 3,820 | 4 | 3 | 7,105 |
| 100 | search_live_state | 0 | 0 | 0 | 1 | 445 |
| rest | read_known_path | 59 | 246,599 | 55 | 13 | 65,371 |
| rest | rerun_command | 1 | 2,053 | 1 | 0 | 0 |
| rest | identical_other_call | 2 | 41 | 2 | 0 | 0 |
| rest | search_transcript | 556 | 774,887 | 537 | 103 | 153,820 |
| rest | search_ledger | 8 | 11,582 | 8 | 3 | 7,105 |
| rest | search_live_state | 1 | 445 | 1 | 1 | 445 |

### R-B, pooled, per 100k of fill

| bin | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| 0k-100k | 130 | 85,564 | 148 | 0 | 0.00% | 0 / 2 (0.00%) | 0 / 40 (0.00%) | 0 / 101 (0.00%) | 0 | — |
| 100k-200k | 810 | 155,454 | 850 | 7 | 0.82% | 0 / 26 (0.00%) | 0 / 85 (0.00%) | 0 / 722 (0.00%) | search_intercept 1 | Bash 7 |
| 200k-300k | 834 | 247,512 | 876 | 15 | 1.71% | 2 / 99 (2.02%) | 0 / 48 (0.00%) | 1 / 712 (0.14%) | search_intercept 1 | Bash 13, Write 1, Edit 1 |
| 300k-400k | 780 | 348,350 | 843 | 19 | 2.25% | 0 / 155 (0.00%) | 0 / 36 (0.00%) | 2 / 634 (0.32%) | search_intercept 2 | Bash 16, Grep 2, Read 1 |
| 400k-500k | 675 | 450,263 | 738 | 15 | 2.03% | 1 / 131 (0.76%) | 1 / 19 (5.26%) | 0 / 581 (0.00%) | 0 | Bash 14, Write 1 |
| 500k-600k | 590 | 548,191 | 615 | 15 | 2.44% | 3 / 75 (4.00%) | 0 / 28 (0.00%) | 0 / 501 (0.00%) | 0 | Bash 12, Write 3 |
| 600k-700k | 588 | 650,711 | 621 | 8 | 1.29% | 1 / 84 (1.19%) | 0 / 28 (0.00%) | 2 / 498 (0.40%) | quirk_guard 2 | Bash 7, Write 1 |
| 700k-800k | 582 | 742,121 | 609 | 7 | 1.15% | 0 / 77 (0.00%) | 0 / 24 (0.00%) | 0 / 500 (0.00%) | 0 | Bash 7 |

### R-B, pooled, per segment third

| third | requests | mean fill | calls | tool errors | error % | failed edits / edits | re-reads / reads | re-runs / Bash | refusals by gate | errors by tool (top 3) |
|---|---|---|---|---|---|---|---|---|---|---|
| first | 1,672 | 215,074 | 1,810 | 23 | 1.27% | 1 / 188 (0.53%) | 0 / 174 (0.00%) | 1 / 1412 (0.07%) | search_intercept 4 | Bash 19, Grep 2, Edit 1 |
| middle | 1,660 | 416,502 | 1,766 | 35 | 1.98% | 0 / 246 (0.00%) | 1 / 62 (1.61%) | 0 / 1438 (0.00%) | 0 | Bash 35 |
| last | 1,654 | 608,122 | 1,723 | 28 | 1.63% | 6 / 215 (2.79%) | 0 / 72 (0.00%) | 4 / 1398 (0.29%) | quirk_guard 2 | Bash 22, Write 6 |

## The cost model's assumptions

- A model, not a measurement: the session's work (its per-request growth) is taken as the same at every X.
- Included: the segments that do not end in a compaction under CLASS_SPLIT (the early 200k-window segments are left out); their growth steps are replayed in file order as one stream.
- The step across an observed compaction is taken as 0 (the real step is the compaction's drop).
- After a modeled compaction the fill returns to K, the mean first context of the included segments that open at a boundary, whatever X is.
- A compaction is counted when the fill would pass X; the request after it sends K, all of it written to the cache (the system prompt's cached prefix is not credited).
- Every other request reads the previous request's fill from the cache and writes what it adds (a negative step writes nothing); cache reads are priced at READ_RATIO, writes at WRITE_RATIO, of the base input price.
- The summarizer's own call (it reads the whole context once per compaction) is reported as its own column, not added to the reads.
- The loss per compaction is the run's mean per-boundary value (1M_window class) measured at about 785k, the same at every X; `rest` keeps the observed segment length.

## Markers

Hook refusals (R-B), by gate:

- `future_stamp`: `COMMIT BLOCKED by the future-stamp gate` (at a line start)
- `lint_delta`: `COMMIT BLOCKED by lint_delta` (at a line start)
- `mutant_anchor`: `COMMIT BLOCKED by mutant_anchor_precommit` (at a line start)
- `mirror`: `COMMIT BLOCKED by the MIRROR gate` (at a line start)
- `never_a_gate`: `COMMIT BLOCKED by the never-a-gate screen` (at a line start)
- `push_in_flight`: `COMMIT BLOCKED: a push is in flight` (at a line start)
- `commit_blocked_other`: `COMMIT BLOCKED` (at a line start)
- `push_blocked`: `PUSH BLOCKED` (at a line start)
- `stale_ids`: `REFUSED by stale_ids` (at a line start)
- `ci_gate`: `REFUSED by ci-gate` (at a line start)
- `search_intercept`: `SEARCH INTERCEPT (search-intercept.py)` (in an error result)
- `quirk_guard`: `QUIRK GUARD (search-intercept.py` (in an error result)

Searches (R-C re-fetch shapes):

- `search_ledger`: `BUILD-TASKLIST.md`
- `search_live_state`: `live-state.md`
- `search_transcript`: `.claude/projects/`; `/tasks/` and `.output`; `chat_tail.py`; `session_export.py`; `transcript_export.py`; `hiccup_scan.py`; `replay_transcript_edits.py`

