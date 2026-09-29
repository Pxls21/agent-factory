# K1 round 2 results (task #352, D-106): the corrected re-fetch shapes, three controls, a position-aware cost model

Written by `scripts/jev_trim/compaction.py summary` at 2026-09-29T05:40:02Z from `run --shapes v2` outputs. Counts, sizes, offsets and names only. No recommendation. The brief is `tasks/briefs/jev-trim/K1-R2-brief.md`; the method is in the module's docstring. A rate is calls per 100 requests, summed over the boundaries or points; an excess is the real rate minus the control's; [a, b] is the excess's 95% bootstrap interval (main only, and the subagents pooled).

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

Subagent files with a boundary now but not in the start measurement: 1.

## Run `main`: bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl pinned at 788,725,407 bytes (main thread)

- Requests 21,118; segments with requests 140; boundaries on the thread 139; skipped boundaries 0; control points: C1 27, C2 26, C5 386; items after a segment's last request kept for C2 792; models {'claude-fable-5': 149, 'claude-fable-5-1': 5908, 'claude-opus-4-6': 532, 'claude-opus-4-8': 2771, 'claude-opus-5-5': 11758}.

### R-C, class `1M_window`: 121 boundaries; control points C1 27, C2 26, C5 386

- Removed per boundary (modeled, mean): 657,623 tokens; last context before (mean) 777,890; kept start per boundary (modeled, mean) 58,273; first context after (mean) 119,382; postTokens (mean) 24,349.

#### Re-fetch calls per 100 requests: the control's rate, then the excess and its 95% bootstrap interval

| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |
|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 21.54 (121; 2,419) | 12.22: +9.32 [+5.42, +13.37] | 10.96: +10.58 [+6.20, +14.75] | 12.22: +9.32 [+6.42, +12.22] |
| K1's shapes, writes out | 20-99 | 12.39 (120; 9,331) | 11.94: +0.44 [-2.15, +2.87] | 11.92: +0.47 [-2.04, +2.92] | 12.21: +0.18 [-2.20, +2.64] |
| K1's shapes, writes out | 100 | 14.27 (121; 11,750) | 12.00: +2.27 [-0.22, +4.66] | 11.73: +2.54 [+0.23, +4.71] | 12.52: +1.75 [-0.77, +3.96] |
| K1's shapes, writes out | rest | 12.91 (121; 20,233) | 11.83: +1.08 [-1.20, +3.15] | 11.73: +1.18 [-1.07, +3.35] | — |
| strict shapes | 20 | 16.54 (121; 2,419) | 6.30: +10.24 [+6.98, +13.59] | 6.92: +9.61 [+6.30, +12.74] | 5.30: +11.24 [+8.97, +13.64] |
| strict shapes | 20-99 | 7.21 (120; 9,331) | 4.49: +2.72 [+1.42, +4.07] | 4.04: +3.17 [+1.83, +4.50] | 4.46: +2.76 [+1.39, +3.96] |
| strict shapes | 100 | 9.13 (121; 11,750) | 4.85: +4.28 [+2.94, +5.62] | 4.62: +4.52 [+3.18, +5.86] | 4.86: +4.27 [+2.95, +5.57] |
| strict shapes | rest | 7.35 (121; 20,233) | 4.51: +2.83 [+1.67, +3.91] | 4.62: +2.73 [+1.53, +3.96] | — |
| K1's + strict (refetch_total) | 20 | 38.07 (121; 2,419) | 18.52: +19.56 [+14.75, +24.48] | 17.88: +20.19 [+16.13, +24.16] | 17.51: +20.56 [+16.93, +24.53] |
| K1's + strict (refetch_total) | 20-99 | 19.60 (120; 9,331) | 16.44: +3.17 [+0.52, +5.91] | 15.96: +3.64 [+0.85, +6.47] | 16.67: +2.93 [+0.15, +5.62] |
| K1's + strict (refetch_total) | 100 | 23.40 (121; 11,750) | 16.85: +6.55 [+3.71, +9.24] | 16.35: +7.06 [+4.50, +9.50] | 17.38: +6.02 [+3.29, +8.67] |
| K1's + strict (refetch_total) | rest | 20.26 (121; 20,233) | 16.35: +3.91 [+1.42, +6.34] | 16.35: +3.91 [+1.55, +6.21] | — |
| loose shapes alone | 20 | 24.60 (121; 2,419) | 18.15: +6.45 [+0.25, +12.94] | 10.38: +14.21 [+8.95, +20.00] | 17.80: +6.80 [+2.40, +11.82] |
| loose shapes alone | 20-99 | 22.22 (120; 9,331) | 13.24: +8.98 [+5.93, +11.87] | 12.12: +10.10 [+7.12, +13.00] | 15.08: +7.14 [+4.31, +10.17] |
| loose shapes alone | 100 | 22.71 (121; 11,750) | 14.22: +8.48 [+5.36, +11.49] | 11.77: +10.94 [+8.19, +13.75] | 15.58: +7.12 [+4.07, +10.05] |
| loose shapes alone | rest | 20.54 (121; 20,233) | 13.47: +7.07 [+4.65, +9.78] | 11.77: +8.77 [+6.22, +11.36] | — |
| K1's + strict + loose | 20 | 62.67 (121; 2,419) | 36.67: +26.00 [+19.16, +33.70] | 28.27: +34.40 [+28.46, +40.78] | 35.31: +27.36 [+22.14, +32.90] |
| K1's + strict + loose | 20-99 | 41.82 (120; 9,331) | 29.68: +12.14 [+8.51, +15.96] | 28.08: +13.74 [+9.76, +17.61] | 31.74: +10.07 [+6.88, +13.55] |
| K1's + strict + loose | 100 | 46.11 (121; 11,750) | 31.07: +15.04 [+11.32, +18.71] | 28.12: +18.00 [+14.49, +21.66] | 32.96: +13.15 [+10.01, +16.45] |
| K1's + strict + loose | rest | 40.80 (121; 20,233) | 29.81: +10.99 [+7.86, +14.24] | 28.12: +12.68 [+9.33, +16.28] | — |

#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)

| shape set | window | real mean requests per boundary | real calls / tokens per boundary | excess over C1: calls / tokens per boundary | over C2 | over C5 |
|---|---|---|---|---|---|---|
| K1's + strict (refetch_total) | 20 | 19.99 | 7.61 / 12,396 | +3.91 / +9,338 | +4.04 / +9,200 | +4.11 / +9,585 |
| K1's + strict (refetch_total) | 20-99 | 77.12 | 15.12 / 15,216 | +2.44 / +3,577 | +2.81 / +4,875 | +2.26 / +4,227 |
| K1's + strict (refetch_total) | 100 | 97.11 | 22.73 / 27,612 | +6.36 / +12,915 | +6.85 / +14,089 | +5.85 / +13,405 |
| K1's + strict (refetch_total) | rest | 167.21 | 33.88 / 36,749 | +6.54 / +13,073 | +6.54 / +13,463 | — |
| K1's + strict + loose | 20 | 19.99 | 12.53 / 17,983 | +5.20 / +12,439 | +6.88 / +13,514 | +5.47 / +12,245 |
| K1's + strict + loose | 20-99 | 77.12 | 32.25 / 30,730 | +9.36 / +12,015 | +10.60 / +14,088 | +7.77 / +11,939 |
| K1's + strict + loose | 100 | 97.11 | 44.78 / 48,713 | +14.60 / +24,474 | +17.47 / +27,607 | +12.77 / +24,329 |
| K1's + strict + loose | rest | 167.21 | 68.22 / 67,908 | +18.37 / +28,966 | +21.21 / +31,565 | — |

#### By shape and label, per 100 requests

| window | label | set | real | C1 | C2 | C5 |
|---|---|---|---|---|---|---|
| 20 | read_known_path | K1 | 1.53 | 0.56 | 0.77 | 0.19 |
| 20 | rerun_command | K1 | 0.04 | 1.48 | 0.77 | 1.17 |
| 20 | identical_other_call | K1 | 0.45 | 0.93 | 0.38 | 0.26 |
| 20 | search_transcript | K1 | 8.72 | 7.04 | 6.73 | 7.78 |
| 20 | search_ledger | K1 | 8.89 | 2.04 | 1.92 | 2.54 |
| 20 | search_live_state | K1 | 1.90 | 0.19 | 0.38 | 0.27 |
| 20 | bash_view_known_file | strict | 11.95 | 4.44 | 5.00 | 3.60 |
| 20 | read_bash_viewed_file | strict | 0.74 | 0.00 | 0.00 | 0.05 |
| 20 | git_repeated_args | strict | 3.84 | 1.85 | 1.92 | 1.65 |
| 20 | read_known_path_respelled | strict | 0.00 | 0.00 | 0.00 | 0.00 |
| 20 | grep_known_token | loose | 21.95 | 17.04 | 9.62 | 16.63 |
| 20 | git_any | loose | 2.65 | 1.11 | 0.77 | 1.17 |
| 20-99 | read_known_path | K1 | 0.42 | 0.32 | 0.38 | 0.15 |
| 20-99 | rerun_command | K1 | 0.18 | 1.06 | 1.59 | 0.88 |
| 20-99 | identical_other_call | K1 | 0.51 | 0.19 | 0.14 | 0.10 |
| 20-99 | search_transcript | K1 | 5.52 | 7.36 | 7.16 | 8.70 |
| 20-99 | search_ledger | K1 | 4.29 | 2.59 | 2.50 | 2.12 |
| 20-99 | search_live_state | K1 | 1.47 | 0.42 | 0.14 | 0.26 |
| 20-99 | bash_view_known_file | strict | 5.28 | 2.45 | 2.12 | 2.47 |
| 20-99 | read_bash_viewed_file | strict | 0.13 | 0.00 | 0.10 | 0.06 |
| 20-99 | git_repeated_args | strict | 1.80 | 2.04 | 1.83 | 1.93 |
| 20-99 | read_known_path_respelled | strict | 0.00 | 0.00 | 0.00 | 0.00 |
| 20-99 | grep_known_token | loose | 20.46 | 12.36 | 11.49 | 14.00 |
| 20-99 | git_any | loose | 1.76 | 0.88 | 0.62 | 1.08 |
| 100 | read_known_path | K1 | 0.65 | 0.37 | 0.46 | 0.14 |
| 100 | rerun_command | K1 | 0.15 | 1.15 | 1.42 | 0.87 |
| 100 | identical_other_call | K1 | 0.50 | 0.33 | 0.19 | 0.14 |
| 100 | search_transcript | K1 | 6.18 | 7.30 | 7.08 | 8.95 |
| 100 | search_ledger | K1 | 5.23 | 2.48 | 2.38 | 2.15 |
| 100 | search_live_state | K1 | 1.56 | 0.37 | 0.19 | 0.28 |
| 100 | bash_view_known_file | strict | 6.66 | 2.85 | 2.69 | 2.94 |
| 100 | read_bash_viewed_file | strict | 0.26 | 0.00 | 0.08 | 0.05 |
| 100 | git_repeated_args | strict | 2.22 | 2.00 | 1.85 | 1.88 |
| 100 | read_known_path_respelled | strict | 0.00 | 0.00 | 0.00 | 0.00 |
| 100 | grep_known_token | loose | 20.77 | 13.30 | 11.12 | 14.43 |
| 100 | git_any | loose | 1.94 | 0.93 | 0.65 | 1.16 |

#### The search shapes by direction, per 100 requests (`counted` = read + script + other)

| window | shape | direction | real | C1 | C2 | C5 |
|---|---|---|---|---|---|---|
| 20 | search_transcript | counted | 8.72 | 7.04 | 6.73 | 7.78 |
| 20 | search_transcript | read | 7.19 | 6.48 | 5.96 | 6.90 |
| 20 | search_transcript | script | 1.36 | 0.37 | 0.19 | 0.43 |
| 20 | search_transcript | other | 0.17 | 0.19 | 0.58 | 0.45 |
| 20 | search_transcript | write | 0.74 | 2.78 | 3.46 | 1.93 |
| 20 | search_transcript | commit | 0.00 | 0.56 | 1.15 | 0.49 |
| 20 | search_ledger | counted | 8.89 | 2.04 | 1.92 | 2.54 |
| 20 | search_ledger | read | 8.64 | 1.67 | 1.92 | 2.40 |
| 20 | search_ledger | script | 0.17 | 0.00 | 0.00 | 0.08 |
| 20 | search_ledger | other | 0.08 | 0.37 | 0.00 | 0.06 |
| 20 | search_ledger | write | 3.43 | 4.81 | 5.00 | 4.61 |
| 20 | search_ledger | commit | 0.25 | 1.30 | 2.50 | 1.57 |
| 20 | search_live_state | counted | 1.90 | 0.19 | 0.38 | 0.27 |
| 20 | search_live_state | read | 1.90 | 0.19 | 0.38 | 0.25 |
| 20 | search_live_state | script | 0.00 | 0.00 | 0.00 | 0.03 |
| 20 | search_live_state | other | 0.00 | 0.00 | 0.00 | 0.00 |
| 20 | search_live_state | write | 0.37 | 1.11 | 1.15 | 0.92 |
| 20 | search_live_state | commit | 0.04 | 1.11 | 1.54 | 0.78 |
| 100 | search_transcript | counted | 6.18 | 7.30 | 7.08 | 8.95 |
| 100 | search_transcript | read | 5.32 | 6.33 | 6.08 | 7.85 |
| 100 | search_transcript | script | 0.66 | 0.52 | 0.42 | 0.55 |
| 100 | search_transcript | other | 0.20 | 0.44 | 0.58 | 0.54 |
| 100 | search_transcript | write | 1.19 | 2.78 | 2.88 | 2.63 |
| 100 | search_transcript | commit | 0.06 | 0.89 | 1.04 | 0.81 |
| 100 | search_ledger | counted | 5.23 | 2.48 | 2.38 | 2.15 |
| 100 | search_ledger | read | 4.98 | 2.30 | 2.27 | 2.08 |
| 100 | search_ledger | script | 0.16 | 0.07 | 0.04 | 0.03 |
| 100 | search_ledger | other | 0.09 | 0.11 | 0.08 | 0.04 |
| 100 | search_ledger | write | 4.76 | 4.89 | 4.69 | 3.95 |
| 100 | search_ledger | commit | 0.85 | 2.59 | 2.65 | 2.16 |
| 100 | search_live_state | counted | 1.56 | 0.37 | 0.19 | 0.28 |
| 100 | search_live_state | read | 1.48 | 0.33 | 0.19 | 0.27 |
| 100 | search_live_state | script | 0.07 | 0.04 | 0.00 | 0.01 |
| 100 | search_live_state | other | 0.01 | 0.00 | 0.00 | 0.00 |
| 100 | search_live_state | write | 0.53 | 1.15 | 1.27 | 1.10 |
| 100 | search_live_state | commit | 0.23 | 1.30 | 1.35 | 1.26 |

#### The miss

| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 121 | 20.0 | 86.0 | 12.3 | 15 / 15 | 2.02% | 240.1 | 27 | 316.9 |
| 20-99 | 121 | 77.1 | 260.6 | 31.6 | 26 / 19 | 1.18% | 630.2 | 27 | 633.9 |
| 100 | 121 | 97.1 | 301.2 | 37.7 | 33 / 29 | 1.36% | 713.8 | 27 | 739.0 |
| rest | 121 | 167.2 | 411.3 | 50.6 | 38 / 42 | 1.31% | 927.4 | 27 | 863.9 |

### R-C, class `200k_window`: 18 boundaries; control points C1 0, C2 0, C5 0

- Removed per boundary (modeled, mean): 109,169 tokens; last context before (mean) 142,069; kept start per boundary (modeled, mean) 28,042; first context after (mean) 83,659; postTokens (mean) 18,948.

#### Re-fetch calls per 100 requests: the control's rate, then the excess and its 95% bootstrap interval

| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |
|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 22.02 (18; 336) | — | — | — |
| K1's shapes, writes out | 20-99 | 7.22 (14; 277) | — | — | — |
| K1's shapes, writes out | 100 | 15.33 (18; 613) | — | — | — |
| K1's shapes, writes out | rest | 13.29 (18; 715) | — | — | — |
| strict shapes | 20 | 7.74 (18; 336) | — | — | — |
| strict shapes | 20-99 | 2.89 (14; 277) | — | — | — |
| strict shapes | 100 | 5.55 (18; 613) | — | — | — |
| strict shapes | rest | 4.76 (18; 715) | — | — | — |
| K1's + strict (refetch_total) | 20 | 29.76 (18; 336) | — | — | — |
| K1's + strict (refetch_total) | 20-99 | 10.11 (14; 277) | — | — | — |
| K1's + strict (refetch_total) | 100 | 20.88 (18; 613) | — | — | — |
| K1's + strict (refetch_total) | rest | 18.04 (18; 715) | — | — | — |
| loose shapes alone | 20 | 10.12 (18; 336) | — | — | — |
| loose shapes alone | 20-99 | 9.03 (14; 277) | — | — | — |
| loose shapes alone | 100 | 9.62 (18; 613) | — | — | — |
| loose shapes alone | rest | 8.81 (18; 715) | — | — | — |
| K1's + strict + loose | 20 | 39.88 (18; 336) | — | — | — |
| K1's + strict + loose | 20-99 | 19.13 (14; 277) | — | — | — |
| K1's + strict + loose | 100 | 30.51 (18; 613) | — | — | — |
| K1's + strict + loose | rest | 26.85 (18; 715) | — | — | — |

#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)

| shape set | window | real mean requests per boundary | real calls / tokens per boundary | excess over C1: calls / tokens per boundary | over C2 | over C5 |
|---|---|---|---|---|---|---|
| K1's + strict (refetch_total) | 20 | 18.67 | 5.56 / 5,092 | — | — | — |
| K1's + strict (refetch_total) | 20-99 | 15.39 | 1.56 / 1,507 | — | — | — |
| K1's + strict (refetch_total) | 100 | 34.06 | 7.11 / 6,599 | — | — | — |
| K1's + strict (refetch_total) | rest | 39.72 | 7.17 / 6,707 | — | — | — |
| K1's + strict + loose | 20 | 18.67 | 7.44 / 5,836 | — | — | — |
| K1's + strict + loose | 20-99 | 15.39 | 2.94 / 2,429 | — | — | — |
| K1's + strict + loose | 100 | 34.06 | 10.39 / 8,266 | — | — | — |
| K1's + strict + loose | rest | 39.72 | 10.67 / 8,499 | — | — | — |

#### By shape and label, per 100 requests

| window | label | set | real | C1 | C2 | C5 |
|---|---|---|---|---|---|---|
| 20 | read_known_path | K1 | 12.20 | — | — | — |
| 20 | rerun_command | K1 | 4.46 | — | — | — |
| 20 | identical_other_call | K1 | 1.49 | — | — | — |
| 20 | search_transcript | K1 | 0.89 | — | — | — |
| 20 | search_ledger | K1 | 2.98 | — | — | — |
| 20 | search_live_state | K1 | 0.00 | — | — | — |
| 20 | bash_view_known_file | strict | 0.60 | — | — | — |
| 20 | read_bash_viewed_file | strict | 1.49 | — | — | — |
| 20 | git_repeated_args | strict | 5.65 | — | — | — |
| 20 | read_known_path_respelled | strict | 0.00 | — | — | — |
| 20 | grep_known_token | loose | 6.55 | — | — | — |
| 20 | git_any | loose | 3.57 | — | — | — |
| 20-99 | read_known_path | K1 | 3.97 | — | — | — |
| 20-99 | rerun_command | K1 | 1.44 | — | — | — |
| 20-99 | identical_other_call | K1 | 0.72 | — | — | — |
| 20-99 | search_transcript | K1 | 0.00 | — | — | — |
| 20-99 | search_ledger | K1 | 1.08 | — | — | — |
| 20-99 | search_live_state | K1 | 0.00 | — | — | — |
| 20-99 | bash_view_known_file | strict | 1.44 | — | — | — |
| 20-99 | read_bash_viewed_file | strict | 0.00 | — | — | — |
| 20-99 | git_repeated_args | strict | 1.44 | — | — | — |
| 20-99 | read_known_path_respelled | strict | 0.00 | — | — | — |
| 20-99 | grep_known_token | loose | 6.86 | — | — | — |
| 20-99 | git_any | loose | 2.17 | — | — | — |
| 100 | read_known_path | K1 | 8.48 | — | — | — |
| 100 | rerun_command | K1 | 3.10 | — | — | — |
| 100 | identical_other_call | K1 | 1.14 | — | — | — |
| 100 | search_transcript | K1 | 0.49 | — | — | — |
| 100 | search_ledger | K1 | 2.12 | — | — | — |
| 100 | search_live_state | K1 | 0.00 | — | — | — |
| 100 | bash_view_known_file | strict | 0.98 | — | — | — |
| 100 | read_bash_viewed_file | strict | 0.82 | — | — | — |
| 100 | git_repeated_args | strict | 3.75 | — | — | — |
| 100 | read_known_path_respelled | strict | 0.00 | — | — | — |
| 100 | grep_known_token | loose | 6.69 | — | — | — |
| 100 | git_any | loose | 2.94 | — | — | — |

#### The search shapes by direction, per 100 requests (`counted` = read + script + other)

| window | shape | direction | real | C1 | C2 | C5 |
|---|---|---|---|---|---|---|
| 20 | search_transcript | counted | 0.89 | — | — | — |
| 20 | search_transcript | read | 0.89 | — | — | — |
| 20 | search_transcript | script | 0.00 | — | — | — |
| 20 | search_transcript | other | 0.00 | — | — | — |
| 20 | search_transcript | write | 0.00 | — | — | — |
| 20 | search_transcript | commit | 0.00 | — | — | — |
| 20 | search_ledger | counted | 2.98 | — | — | — |
| 20 | search_ledger | read | 2.98 | — | — | — |
| 20 | search_ledger | script | 0.00 | — | — | — |
| 20 | search_ledger | other | 0.00 | — | — | — |
| 20 | search_ledger | write | 2.08 | — | — | — |
| 20 | search_ledger | commit | 1.19 | — | — | — |
| 20 | search_live_state | counted | 0.00 | — | — | — |
| 20 | search_live_state | read | 0.00 | — | — | — |
| 20 | search_live_state | script | 0.00 | — | — | — |
| 20 | search_live_state | other | 0.00 | — | — | — |
| 20 | search_live_state | write | 0.00 | — | — | — |
| 20 | search_live_state | commit | 0.00 | — | — | — |
| 100 | search_transcript | counted | 0.49 | — | — | — |
| 100 | search_transcript | read | 0.49 | — | — | — |
| 100 | search_transcript | script | 0.00 | — | — | — |
| 100 | search_transcript | other | 0.00 | — | — | — |
| 100 | search_transcript | write | 0.00 | — | — | — |
| 100 | search_transcript | commit | 0.00 | — | — | — |
| 100 | search_ledger | counted | 2.12 | — | — | — |
| 100 | search_ledger | read | 2.12 | — | — | — |
| 100 | search_ledger | script | 0.00 | — | — | — |
| 100 | search_ledger | other | 0.00 | — | — | — |
| 100 | search_ledger | write | 6.53 | — | — | — |
| 100 | search_ledger | commit | 2.28 | — | — | — |
| 100 | search_live_state | counted | 0.00 | — | — | — |
| 100 | search_live_state | read | 0.00 | — | — | — |
| 100 | search_live_state | script | 0.00 | — | — | — |
| 100 | search_live_state | other | 0.00 | — | — | — |
| 100 | search_live_state | write | 0.00 | — | — | — |
| 100 | search_live_state | commit | 0.00 | — | — | — |

#### The miss

| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 18 | 18.7 | 54.8 | 7.8 | 23 / 0 | 16.31% | 197.9 | 0 | — |
| 20-99 | 18 | 15.4 | 35.8 | 3.1 | 1 / 0 | 1.79% | 132.1 | 0 | — |
| 100 | 18 | 34.1 | 79.9 | 9.9 | 24 / 0 | 13.48% | 276.9 | 0 | — |
| rest | 18 | 39.7 | 83.9 | 10.1 | 24 / 0 | 13.26% | 285.7 | 0 | — |

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

- Growth per request by position since the segment start: 0-19 6,202 (2,440 steps); 20-99 4,310 (9,474 steps); 100+ 2,830 (8,550 steps).
- Actual usage of the 20,586 included requests: cache reads 9,552,612,747, cache writes 124,444,652, mean context 470,094.
- Position-aware calibration: scale 0.993736; compactions at 785,000: 121 (target 121; unscaled 122).

| X | flat: compactions | mean fill | cache reads | cache writes | position-aware: compactions (unscaled) | mean fill | cache reads | cache writes |
|---|---|---|---|---|---|---|---|---|
| 300,000 | 427 | 205,288 | 4,100,747,389 | 125,902,060 | 586 (589) | 208,577 | 4,122,679,980 | 172,154,988 |
| 400,000 | 278 | 256,417 | 5,169,179,159 | 110,014,563 | 353 (354) | 267,024 | 5,357,952,278 | 139,843,374 |
| 500,000 | 206 | 305,770 | 6,192,762,386 | 102,412,440 | 246 (247) | 322,051 | 6,508,047,128 | 122,503,139 |
| 600,000 | 164 | 355,983 | 7,230,448,795 | 98,409,562 | 186 (187) | 376,812 | 7,646,147,888 | 111,699,825 |
| 700,000 | 136 | 406,302 | 8,269,623,513 | 95,112,346 | 146 (146) | 437,552 | 8,905,523,707 | 102,581,613 |
| 785,000 | 119 | 453,578 | 9,244,750,496 | 93,190,429 | 121 (122) | 488,223 | 9,955,796,034 | 95,387,028 |

At 785,000 against the actual usage: flat cache reads -3.2%, writes -25.1%, mean fill -3.5%; position-aware cache reads +4.2%, writes -23.3%, mean fill +3.9%.

The corrected loss (refetch_total, K1's shapes with writes out plus the strict set): the modeled compactions times the excess per boundary; calls / tokens.

| X | model | N=20 over C1 | over C2 | over C5 | N=100 over C1 | over C2 | over C5 |
|---|---|---|---|---|---|---|---|
| 300,000 | flat | 1,669 / 3,987,155 | 1,723 / 3,928,186 | 1,755 / 4,092,752 | 2,717 / 5,514,876 | 2,927 / 6,016,046 | 2,498 / 5,723,807 |
| 400,000 | flat | 1,087 / 2,595,853 | 1,122 / 2,557,461 | 1,143 / 2,664,602 | 1,769 / 3,590,481 | 1,905 / 3,916,770 | 1,626 / 3,726,507 |
| 500,000 | flat | 805 / 1,923,546 | 831 / 1,895,097 | 847 / 1,974,489 | 1,311 / 2,660,572 | 1,412 / 2,902,355 | 1,205 / 2,761,368 |
| 600,000 | flat | 641 / 1,531,366 | 662 / 1,508,718 | 674 / 1,571,924 | 1,044 / 2,118,126 | 1,124 / 2,310,612 | 959 / 2,198,371 |
| 700,000 | flat | 532 / 1,269,914 | 549 / 1,251,132 | 559 / 1,303,546 | 865 / 1,756,494 | 932 / 1,916,118 | 796 / 1,823,039 |
| 785,000 | flat | 465 / 1,111,174 | 480 / 1,094,740 | 489 / 1,140,603 | 757 / 1,536,933 | 816 / 1,676,603 | 696 / 1,595,159 |
| 300,000 | position-aware | 2,291 / 5,471,834 | 2,365 / 5,390,907 | 2,409 / 5,616,751 | 3,729 / 7,568,424 | 4,016 / 8,256,213 | 3,428 / 7,855,154 |
| 400,000 | position-aware | 1,380 / 3,296,173 | 1,425 / 3,247,424 | 1,451 / 3,383,470 | 2,246 / 4,559,136 | 2,419 / 4,973,452 | 2,065 / 4,731,859 |
| 500,000 | position-aware | 962 / 2,297,050 | 993 / 2,263,077 | 1,011 / 2,357,885 | 1,565 / 3,177,188 | 1,686 / 3,465,919 | 1,439 / 3,297,556 |
| 600,000 | position-aware | 727 / 1,736,794 | 751 / 1,711,107 | 764 / 1,782,791 | 1,184 / 2,402,264 | 1,275 / 2,620,573 | 1,088 / 2,493,274 |
| 700,000 | position-aware | 571 / 1,363,290 | 589 / 1,343,127 | 600 / 1,399,395 | 929 / 1,885,648 | 1,001 / 2,057,009 | 854 / 1,957,086 |
| 785,000 | position-aware | 473 / 1,129,850 | 488 / 1,113,140 | 497 / 1,159,773 | 770 / 1,562,763 | 829 / 1,704,781 | 708 / 1,621,969 |

## Run `sub-a3977da56fa688986`: agent-a3977da56fa688986.jsonl pinned at 6,563,519 bytes (sidechain thread)

- Requests 369; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; control points: C1 1, C2 1, C5 8; items after a segment's last request kept for C2 5; models {'claude-opus-5-5': 369}.

### R-C, class `1M_window`: 1 boundaries; control points C1 1, C2 1, C5 8

- Removed per boundary (modeled, mean): 729,970 tokens; last context before (mean) 783,095; kept start per boundary (modeled, mean) 49,852; first context after (mean) 90,872; postTokens (mean) 12,724.

#### Re-fetch calls per 100 requests: the control's rate, then the excess

| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |
|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 0.00 (1; 20) | 0.00: +0.00 | 10.00: -10.00 | 1.25: -1.25 |
| K1's shapes, writes out | 20-99 | 13.75 (1; 80) | 2.50: +11.25 | 0.00: +13.75 | 2.50: +11.25 |
| K1's shapes, writes out | 100 | 11.00 (1; 100) | 2.00: +9.00 | 2.00: +9.00 | 2.00: +9.00 |
| K1's shapes, writes out | rest | 9.03 (1; 144) | 1.77: +7.26 | 2.00: +7.03 | — |
| strict shapes | 20 | 25.00 (1; 20) | 15.00: +10.00 | 25.00: +0.00 | 23.12: +1.88 |
| strict shapes | 20-99 | 20.00 (1; 80) | 18.75: +1.25 | 16.25: +3.75 | 20.00: +0.00 |
| strict shapes | 100 | 21.00 (1; 100) | 18.00: +3.00 | 18.00: +3.00 | 18.50: +2.50 |
| strict shapes | rest | 21.53 (1; 144) | 15.93: +5.60 | 18.00: +3.53 | — |
| K1's + strict (refetch_total) | 20 | 25.00 (1; 20) | 15.00: +10.00 | 35.00: -10.00 | 24.38: +0.62 |
| K1's + strict (refetch_total) | 20-99 | 33.75 (1; 80) | 21.25: +12.50 | 16.25: +17.50 | 22.50: +11.25 |
| K1's + strict (refetch_total) | 100 | 32.00 (1; 100) | 20.00: +12.00 | 20.00: +12.00 | 20.50: +11.50 |
| K1's + strict (refetch_total) | rest | 30.56 (1; 144) | 17.70: +12.86 | 20.00: +10.56 | — |
| loose shapes alone | 20 | 30.00 (1; 20) | 20.00: +10.00 | 10.00: +20.00 | 17.50: +12.50 |
| loose shapes alone | 20-99 | 17.50 (1; 80) | 16.25: +1.25 | 15.00: +2.50 | 16.25: +1.25 |
| loose shapes alone | 100 | 20.00 (1; 100) | 17.00: +3.00 | 14.00: +6.00 | 17.50: +2.50 |
| loose shapes alone | rest | 17.36 (1; 144) | 15.93: +1.43 | 14.00: +3.36 | — |
| K1's + strict + loose | 20 | 55.00 (1; 20) | 35.00: +20.00 | 45.00: +10.00 | 41.88: +13.12 |
| K1's + strict + loose | 20-99 | 51.25 (1; 80) | 37.50: +13.75 | 31.25: +20.00 | 38.75: +12.50 |
| K1's + strict + loose | 100 | 52.00 (1; 100) | 37.00: +15.00 | 34.00: +18.00 | 38.00: +14.00 |
| K1's + strict + loose | rest | 47.92 (1; 144) | 33.63: +14.29 | 34.00: +13.92 | — |

#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)

| shape set | window | real mean requests per boundary | real calls / tokens per boundary | excess over C1: calls / tokens per boundary | over C2 | over C5 |
|---|---|---|---|---|---|---|
| K1's + strict (refetch_total) | 20 | 20.00 | 5.00 / 8,657 | +2.00 / +3,990 | -2.00 / -1,867 | +0.13 / +3,958 |
| K1's + strict (refetch_total) | 20-99 | 80.00 | 27.00 / 29,318 | +10.00 / +9,855 | +14.00 / +15,958 | +9.00 / +8,040 |
| K1's + strict (refetch_total) | 100 | 100.00 | 32.00 / 37,975 | +12.00 / +13,845 | +12.00 / +14,091 | +11.50 / +13,478 |
| K1's + strict (refetch_total) | rest | 144.00 | 44.00 / 51,072 | +18.51 / +20,323 | +15.20 / +16,679 | — |
| K1's + strict + loose | 20 | 20.00 | 11.00 / 15,439 | +4.00 / +8,880 | +2.00 / +2,956 | +2.63 / +8,508 |
| K1's + strict + loose | 20-99 | 80.00 | 41.00 / 43,767 | +11.00 / +15,920 | +16.00 / +22,995 | +10.00 / +14,000 |
| K1's + strict + loose | 100 | 100.00 | 52.00 / 59,205 | +15.00 / +24,799 | +18.00 / +25,951 | +14.00 / +23,093 |
| K1's + strict + loose | rest | 144.00 | 69.00 / 74,706 | +20.58 / +30,495 | +20.04 / +26,820 | — |

#### The miss

| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 20.0 | 23.0 | 10.0 | 0 / 0 | 0.00% | 80.0 | 1 | 588.0 |
| 20-99 | 1 | 80.0 | 221.0 | 43.0 | 0 / 1 | 2.33% | 422.0 | 1 | 600.0 |
| 100 | 1 | 100.0 | 237.0 | 51.0 | 0 / 1 | 1.96% | 456.0 | 1 | 846.0 |
| rest | 1 | 144.0 | 378.0 | 65.0 | 0 / 3 | 4.62% | 717.0 | 1 | 871.0 |

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

- Growth per request by position since the segment start: 0-19 4,556 (40 steps); 20-99 2,315 (160 steps); 100+ 2,559 (167 steps).
- Actual usage of the 369 included requests: cache reads 139,380,585, cache writes 1,095,668, mean context 380,696.
- Position-aware calibration: scale 1.000000; compactions at 785,000: 1 (target 1; unscaled 1).

| X | flat: compactions | mean fill | cache reads | cache writes | position-aware: compactions (unscaled) | mean fill | cache reads | cache writes |
|---|---|---|---|---|---|---|---|---|
| 300,000 | 4 | 194,671 | 70,423,228 | 1,410,389 | 5 (5) | 200,223 | 72,230,727 | 1,651,397 |
| 400,000 | 3 | 240,518 | 87,417,702 | 1,333,333 | 3 (3) | 250,083 | 90,919,697 | 1,360,979 |
| 500,000 | 2 | 288,831 | 105,344,783 | 1,233,798 | 2 (2) | 309,434 | 112,875,506 | 1,305,735 |
| 600,000 | 1 | 348,498 | 127,436,291 | 1,159,655 | 1 (1) | 358,234 | 131,017,498 | 1,170,749 |
| 700,000 | 1 | 357,502 | 130,775,958 | 1,142,286 | 1 (1) | 361,519 | 132,252,211 | 1,148,146 |
| 785,000 | 1 | 381,526 | 139,623,937 | 1,159,201 | 1 (1) | 381,253 | 139,523,829 | 1,158,436 |

At 785,000 against the actual usage: flat cache reads +0.2%, writes +5.8%, mean fill +0.2%; position-aware cache reads +0.1%, writes +5.7%, mean fill +0.1%.

The corrected loss (refetch_total, K1's shapes with writes out plus the strict set): the modeled compactions times the excess per boundary; calls / tokens.

| X | model | N=20 over C1 | over C2 | over C5 | N=100 over C1 | over C2 | over C5 |
|---|---|---|---|---|---|---|---|
| 300,000 | flat | 8 / 15,961 | -8 / -7,469 | 0 / 15,832 | 48 / 55,381 | 48 / 56,364 | 46 / 53,912 |
| 400,000 | flat | 6 / 11,971 | -6 / -5,602 | 0 / 11,874 | 36 / 41,536 | 36 / 42,273 | 34 / 40,434 |
| 500,000 | flat | 4 / 7,980 | -4 / -3,734 | 0 / 7,916 | 24 / 27,691 | 24 / 28,182 | 23 / 26,956 |
| 600,000 | flat | 2 / 3,990 | -2 / -1,867 | 0 / 3,958 | 12 / 13,845 | 12 / 14,091 | 12 / 13,478 |
| 700,000 | flat | 2 / 3,990 | -2 / -1,867 | 0 / 3,958 | 12 / 13,845 | 12 / 14,091 | 12 / 13,478 |
| 785,000 | flat | 2 / 3,990 | -2 / -1,867 | 0 / 3,958 | 12 / 13,845 | 12 / 14,091 | 12 / 13,478 |
| 300,000 | position-aware | 10 / 19,951 | -10 / -9,336 | 1 / 19,790 | 60 / 69,226 | 60 / 70,456 | 58 / 67,390 |
| 400,000 | position-aware | 6 / 11,971 | -6 / -5,602 | 0 / 11,874 | 36 / 41,536 | 36 / 42,273 | 34 / 40,434 |
| 500,000 | position-aware | 4 / 7,980 | -4 / -3,734 | 0 / 7,916 | 24 / 27,691 | 24 / 28,182 | 23 / 26,956 |
| 600,000 | position-aware | 2 / 3,990 | -2 / -1,867 | 0 / 3,958 | 12 / 13,845 | 12 / 14,091 | 12 / 13,478 |
| 700,000 | position-aware | 2 / 3,990 | -2 / -1,867 | 0 / 3,958 | 12 / 13,845 | 12 / 14,091 | 12 / 13,478 |
| 785,000 | position-aware | 2 / 3,990 | -2 / -1,867 | 0 / 3,958 | 12 / 13,845 | 12 / 14,091 | 12 / 13,478 |

## Run `sub-a4920ba3ae772b9d0`: agent-a4920ba3ae772b9d0.jsonl pinned at 12,926,645 bytes (sidechain thread)

- Requests 714; segments with requests 4; boundaries on the thread 3; skipped boundaries 0; control points: C1 2, C2 2, C5 19; items after a segment's last request kept for C2 15; models {'claude-opus-5-5': 714}.

### R-C, class `1M_window`: 3 boundaries; control points C1 2, C2 2, C5 19

- Removed per boundary (modeled, mean): 438,263 tokens; last context before (mean) 780,973; kept start per boundary (modeled, mean) 33,098; first context after (mean) 70,278; postTokens (mean) 11,537.

#### Re-fetch calls per 100 requests: the control's rate, then the excess

| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |
|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 0.00 (3; 42) | 17.50: -17.50 | 5.00: -5.00 | 5.00: -5.00 |
| K1's shapes, writes out | 20-99 | 3.12 (2; 160) | 1.25: +1.88 | 4.38: -1.25 | 3.04: +0.09 |
| K1's shapes, writes out | 100 | 2.48 (3; 202) | 4.50: -2.02 | 4.50: -2.02 | 3.86: -1.38 |
| K1's shapes, writes out | rest | 4.05 (3; 519) | 5.79: -1.75 | 4.50: -0.45 | — |
| strict shapes | 20 | 35.71 (3; 42) | 15.00: +20.71 | 22.50: +13.21 | 17.11: +18.61 |
| strict shapes | 20-99 | 28.75 (2; 160) | 18.75: +10.00 | 15.62: +13.12 | 16.43: +12.32 |
| strict shapes | 100 | 30.20 (3; 202) | 18.00: +12.20 | 17.00: +13.20 | 16.29: +13.91 |
| strict shapes | rest | 21.77 (3; 519) | 14.67: +7.10 | 17.00: +4.77 | — |
| K1's + strict (refetch_total) | 20 | 35.71 (3; 42) | 32.50: +3.21 | 27.50: +8.21 | 22.11: +13.61 |
| K1's + strict (refetch_total) | 20-99 | 31.88 (2; 160) | 20.00: +11.88 | 20.00: +11.88 | 19.46: +12.41 |
| K1's + strict (refetch_total) | 100 | 32.67 (3; 202) | 22.50: +10.17 | 21.50: +11.17 | 20.14: +12.53 |
| K1's + strict (refetch_total) | rest | 25.82 (3; 519) | 20.46: +5.36 | 21.50: +4.32 | — |
| loose shapes alone | 20 | 21.43 (3; 42) | 20.00: +1.43 | 17.50: +3.93 | 18.68: +2.74 |
| loose shapes alone | 20-99 | 27.50 (2; 160) | 13.12: +14.38 | 13.75: +13.75 | 14.46: +13.04 |
| loose shapes alone | 100 | 26.24 (3; 202) | 14.50: +11.74 | 14.50: +11.74 | 15.71: +10.52 |
| loose shapes alone | rest | 20.23 (3; 519) | 13.51: +6.72 | 14.50: +5.73 | — |
| K1's + strict + loose | 20 | 57.14 (3; 42) | 52.50: +4.64 | 45.00: +12.14 | 40.79: +16.35 |
| K1's + strict + loose | 20-99 | 59.38 (2; 160) | 33.12: +26.25 | 33.75: +25.62 | 33.93: +25.45 |
| K1's + strict + loose | 100 | 58.91 (3; 202) | 37.00: +21.91 | 36.00: +22.91 | 35.86: +23.05 |
| K1's + strict + loose | rest | 46.05 (3; 519) | 33.98: +12.07 | 36.00: +10.05 | — |

#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)

| shape set | window | real mean requests per boundary | real calls / tokens per boundary | excess over C1: calls / tokens per boundary | over C2 | over C5 |
|---|---|---|---|---|---|---|
| K1's + strict (refetch_total) | 20 | 14.00 | 5.00 / 7,654 | +0.45 / +2,276 | +1.15 / +3,700 | +1.91 / +3,315 |
| K1's + strict (refetch_total) | 20-99 | 53.33 | 17.00 / 24,774 | +6.33 / +7,268 | +6.33 / +5,481 | +6.62 / +8,712 |
| K1's + strict (refetch_total) | 100 | 67.33 | 22.00 / 32,428 | +6.85 / +9,573 | +7.52 / +9,139 | +8.44 / +12,885 |
| K1's + strict (refetch_total) | rest | 173.00 | 44.67 / 64,883 | +9.27 / +12,020 | +7.47 / +5,045 | — |
| K1's + strict + loose | 20 | 14.00 | 8.00 / 10,199 | +0.65 / +3,580 | +1.70 / +2,731 | +2.29 / +3,906 |
| K1's + strict + loose | 20-99 | 53.33 | 31.67 / 36,995 | +14.00 / +13,667 | +13.67 / +13,201 | +13.57 / +15,289 |
| K1's + strict + loose | 100 | 67.33 | 39.67 / 47,194 | +14.75 / +17,266 | +15.43 / +15,979 | +15.52 / +19,782 |
| K1's + strict + loose | rest | 173.00 | 79.67 / 90,837 | +20.89 / +20,832 | +17.39 / +10,637 | — |

#### The miss

| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 3 | 14.0 | 63.7 | 8.0 | 1 / 0 | 4.17% | 134.0 | 2 | 499.5 |
| 20-99 | 3 | 53.3 | 157.0 | 24.7 | 2 / 1 | 4.05% | 316.3 | 2 | 656.0 |
| 100 | 3 | 67.3 | 206.0 | 30.0 | 2 / 1 | 3.33% | 386.3 | 2 | 754.0 |
| rest | 3 | 173.0 | 443.0 | 49.3 | 2 / 4 | 4.05% | 712.0 | 2 | 786.0 |

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

- Growth per request by position since the segment start: 0-19 4,155 (61 steps); 20-99 2,849 (240 steps); 100+ 2,976 (409 steps).
- Actual usage of the 714 included requests: cache reads 297,431,019, cache writes 10,804,822, mean context 431,705.
- Position-aware calibration: scale 1.002980; compactions at 785,000: 3 (target 3; unscaled 2).

| X | flat: compactions | mean fill | cache reads | cache writes | position-aware: compactions (unscaled) | mean fill | cache reads | cache writes |
|---|---|---|---|---|---|---|---|---|
| 300,000 | 9 | 182,255 | 127,315,270 | 2,814,844 | 9 (9) | 185,452 | 129,443,020 | 2,969,425 |
| 400,000 | 6 | 227,117 | 159,551,706 | 2,609,940 | 6 (6) | 235,318 | 165,349,793 | 2,667,268 |
| 500,000 | 4 | 283,970 | 200,288,656 | 2,466,256 | 5 (5) | 297,516 | 209,857,914 | 2,568,291 |
| 600,000 | 4 | 353,312 | 249,800,321 | 2,464,569 | 4 (4) | 356,575 | 252,078,385 | 2,516,029 |
| 700,000 | 3 | 352,480 | 249,249,901 | 2,421,037 | 3 (3) | 361,040 | 255,336,503 | 2,445,756 |
| 785,000 | 3 | 431,389 | 305,609,577 | 2,402,041 | 3 (2) | 434,910 | 308,109,524 | 2,416,581 |

At 785,000 against the actual usage: flat cache reads +2.7%, writes -77.8%, mean fill -0.1%; position-aware cache reads +3.6%, writes -77.6%, mean fill +0.7%.

The corrected loss (refetch_total, K1's shapes with writes out plus the strict set): the modeled compactions times the excess per boundary; calls / tokens.

| X | model | N=20 over C1 | over C2 | over C5 | N=100 over C1 | over C2 | over C5 |
|---|---|---|---|---|---|---|---|
| 300,000 | flat | 4 / 20,484 | 10 / 33,300 | 17 / 29,836 | 62 / 86,162 | 68 / 82,248 | 76 / 115,961 |
| 400,000 | flat | 3 / 13,656 | 7 / 22,200 | 11 / 19,891 | 41 / 57,441 | 45 / 54,832 | 51 / 77,308 |
| 500,000 | flat | 2 / 9,104 | 5 / 14,800 | 8 / 13,260 | 27 / 38,294 | 30 / 36,555 | 34 / 51,538 |
| 600,000 | flat | 2 / 9,104 | 5 / 14,800 | 8 / 13,260 | 27 / 38,294 | 30 / 36,555 | 34 / 51,538 |
| 700,000 | flat | 1 / 6,828 | 3 / 11,100 | 6 / 9,945 | 20 / 28,720 | 23 / 27,416 | 25 / 38,654 |
| 785,000 | flat | 1 / 6,828 | 3 / 11,100 | 6 / 9,945 | 20 / 28,720 | 23 / 27,416 | 25 / 38,654 |
| 300,000 | position-aware | 4 / 20,484 | 10 / 33,300 | 17 / 29,836 | 62 / 86,162 | 68 / 82,248 | 76 / 115,961 |
| 400,000 | position-aware | 3 / 13,656 | 7 / 22,200 | 11 / 19,891 | 41 / 57,441 | 45 / 54,832 | 51 / 77,308 |
| 500,000 | position-aware | 2 / 11,380 | 6 / 18,500 | 10 / 16,576 | 34 / 47,868 | 38 / 45,694 | 42 / 64,423 |
| 600,000 | position-aware | 2 / 9,104 | 5 / 14,800 | 8 / 13,260 | 27 / 38,294 | 30 / 36,555 | 34 / 51,538 |
| 700,000 | position-aware | 1 / 6,828 | 3 / 11,100 | 6 / 9,945 | 20 / 28,720 | 23 / 27,416 | 25 / 38,654 |
| 785,000 | position-aware | 1 / 6,828 | 3 / 11,100 | 6 / 9,945 | 20 / 28,720 | 23 / 27,416 | 25 / 38,654 |

## Run `sub-a4c0c331a18908947`: agent-a4c0c331a18908947.jsonl pinned at 5,021,742 bytes (sidechain thread)

- Requests 159; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; control points: C1 0, C2 0, C5 2; items after a segment's last request kept for C2 6; models {'claude-opus-5-5': 159}.

### R-C, class `1M_window`: 1 boundaries; control points C1 0, C2 0, C5 2

- Removed per boundary (modeled, mean): 751,874 tokens; last context before (mean) 778,553; kept start per boundary (modeled, mean) 51,427; first context after (mean) 96,172; postTokens (mean) 15,025.

#### Re-fetch calls per 100 requests: the control's rate, then the excess

| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |
|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 66.67 (1; 3) | — | — | 2.50: +64.17 |
| K1's shapes, writes out | 20-99 | — (0; 0) | — | — | — |
| K1's shapes, writes out | 100 | 66.67 (1; 3) | — | — | — |
| K1's shapes, writes out | rest | 66.67 (1; 3) | — | — | — |
| strict shapes | 20 | 0.00 (1; 3) | — | — | 15.00: -15.00 |
| strict shapes | 20-99 | — (0; 0) | — | — | — |
| strict shapes | 100 | 0.00 (1; 3) | — | — | — |
| strict shapes | rest | 0.00 (1; 3) | — | — | — |
| K1's + strict (refetch_total) | 20 | 66.67 (1; 3) | — | — | 17.50: +49.17 |
| K1's + strict (refetch_total) | 20-99 | — (0; 0) | — | — | — |
| K1's + strict (refetch_total) | 100 | 66.67 (1; 3) | — | — | — |
| K1's + strict (refetch_total) | rest | 66.67 (1; 3) | — | — | — |
| loose shapes alone | 20 | 0.00 (1; 3) | — | — | 10.00: -10.00 |
| loose shapes alone | 20-99 | — (0; 0) | — | — | — |
| loose shapes alone | 100 | 0.00 (1; 3) | — | — | — |
| loose shapes alone | rest | 0.00 (1; 3) | — | — | — |
| K1's + strict + loose | 20 | 66.67 (1; 3) | — | — | 27.50: +39.17 |
| K1's + strict + loose | 20-99 | — (0; 0) | — | — | — |
| K1's + strict + loose | 100 | 66.67 (1; 3) | — | — | — |
| K1's + strict + loose | rest | 66.67 (1; 3) | — | — | — |

#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)

| shape set | window | real mean requests per boundary | real calls / tokens per boundary | excess over C1: calls / tokens per boundary | over C2 | over C5 |
|---|---|---|---|---|---|---|
| K1's + strict (refetch_total) | 20 | 3.00 | 2.00 / 1,598 | — | — | +1.47 / +665 |
| K1's + strict (refetch_total) | 100 | 3.00 | 2.00 / 1,598 | — | — | — |
| K1's + strict (refetch_total) | rest | 3.00 | 2.00 / 1,598 | — | — | — |
| K1's + strict + loose | 20 | 3.00 | 2.00 / 1,598 | — | — | +1.17 / +471 |
| K1's + strict + loose | 100 | 3.00 | 2.00 / 1,598 | — | — | — |
| K1's + strict + loose | rest | 3.00 | 2.00 / 1,598 | — | — | — |

#### The miss

| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 3.0 | 6.0 | 0.0 | 0 / 0 | — | 41.0 | 0 | — |
| 20-99 | 1 | 0.0 | 0.0 | 0.0 | 0 / 0 | — | 0.0 | 0 | — |
| 100 | 1 | 3.0 | 6.0 | 0.0 | 0 / 0 | — | 41.0 | 0 | — |
| rest | 1 | 3.0 | 6.0 | 0.0 | 0 / 0 | — | 41.0 | 0 | — |

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

- Growth per request by position since the segment start: 0-19 8,296 (22 steps); 20-99 4,385 (80 steps); 100+ 3,722 (55 steps).
- Actual usage of the 159 included requests: cache reads 68,348,010, cache writes 3,222,543, mean context 450,131.
- Position-aware calibration: scale 1.000000; compactions at 785,000: 1 (target 1; unscaled 1).

| X | flat: compactions | mean fill | cache reads | cache writes | position-aware: compactions (unscaled) | mean fill | cache reads | cache writes |
|---|---|---|---|---|---|---|---|---|
| 300,000 | 3 | 182,444 | 27,914,803 | 1,093,827 | 4 (4) | 205,363 | 31,182,066 | 1,470,587 |
| 400,000 | 2 | 247,251 | 38,294,824 | 1,018,030 | 3 (3) | 268,639 | 41,339,816 | 1,373,815 |
| 500,000 | 1 | 268,719 | 41,819,775 | 906,509 | 1 (1) | 304,402 | 47,409,498 | 990,426 |
| 600,000 | 1 | 302,039 | 47,094,787 | 929,379 | 1 (1) | 333,264 | 51,946,640 | 1,042,256 |
| 700,000 | 1 | 350,601 | 54,820,543 | 924,997 | 1 (1) | 361,076 | 56,424,249 | 986,808 |
| 785,000 | 1 | 447,122 | 70,167,064 | 925,362 | 1 (1) | 447,193 | 70,175,923 | 927,835 |

At 785,000 against the actual usage: flat cache reads +2.7%, writes -71.3%, mean fill -0.7%; position-aware cache reads +2.7%, writes -71.2%, mean fill -0.7%.

The corrected loss (refetch_total, K1's shapes with writes out plus the strict set): the modeled compactions times the excess per boundary; calls / tokens.

| X | model | N=20 over C1 | over C2 | over C5 | N=100 over C1 | over C2 | over C5 |
|---|---|---|---|---|---|---|---|
| 300,000 | flat | — | — | 4 / 1,994 | — | — | — |
| 400,000 | flat | — | — | 3 / 1,329 | — | — | — |
| 500,000 | flat | — | — | 2 / 664 | — | — | — |
| 600,000 | flat | — | — | 2 / 664 | — | — | — |
| 700,000 | flat | — | — | 2 / 664 | — | — | — |
| 785,000 | flat | — | — | 2 / 664 | — | — | — |
| 300,000 | position-aware | — | — | 6 / 2,658 | — | — | — |
| 400,000 | position-aware | — | — | 4 / 1,994 | — | — | — |
| 500,000 | position-aware | — | — | 2 / 664 | — | — | — |
| 600,000 | position-aware | — | — | 2 / 664 | — | — | — |
| 700,000 | position-aware | — | — | 2 / 664 | — | — | — |
| 785,000 | position-aware | — | — | 2 / 664 | — | — | — |

## Run `sub-a4f24691b2f13e97e`: agent-a4f24691b2f13e97e.jsonl pinned at 5,372,930 bytes (sidechain thread)

- Requests 285; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; control points: C1 1, C2 1, C5 5; items after a segment's last request kept for C2 6; models {'claude-opus-4-8': 36, 'claude-opus-5-5': 249}.

### R-C, class `1M_window`: 1 boundaries; control points C1 1, C2 1, C5 5

- Removed per boundary (modeled, mean): 464,395 tokens; last context before (mean) 781,965; kept start per boundary (modeled, mean) 37,498; first context after (mean) 80,241; postTokens (mean) 16,129.

#### Re-fetch calls per 100 requests: the control's rate, then the excess

| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |
|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 40.00 (1; 20) | 0.00: +40.00 | 5.00: +35.00 | 3.00: +37.00 |
| K1's shapes, writes out | 20-99 | 0.00 (1; 48) | 3.75: -3.75 | 3.75: -3.75 | 3.75: -3.75 |
| K1's shapes, writes out | 100 | 11.76 (1; 68) | 3.00: +8.76 | 4.00: +7.76 | 3.00: +8.76 |
| K1's shapes, writes out | rest | 11.76 (1; 68) | 3.67: +8.09 | 4.00: +7.76 | — |
| strict shapes | 20 | 30.00 (1; 20) | 0.00: +30.00 | 0.00: +30.00 | 4.00: +26.00 |
| strict shapes | 20-99 | 16.67 (1; 48) | 6.25: +10.42 | 6.25: +10.42 | 5.00: +11.67 |
| strict shapes | 100 | 20.59 (1; 68) | 5.00: +15.59 | 5.00: +15.59 | 4.00: +16.59 |
| strict shapes | rest | 20.59 (1; 68) | 4.59: +16.00 | 5.00: +15.59 | — |
| K1's + strict (refetch_total) | 20 | 70.00 (1; 20) | 0.00: +70.00 | 5.00: +65.00 | 7.00: +63.00 |
| K1's + strict (refetch_total) | 20-99 | 16.67 (1; 48) | 10.00: +6.67 | 10.00: +6.67 | 8.75: +7.92 |
| K1's + strict (refetch_total) | 100 | 32.35 (1; 68) | 8.00: +24.35 | 9.00: +23.35 | 7.00: +25.35 |
| K1's + strict (refetch_total) | rest | 32.35 (1; 68) | 8.26: +24.10 | 9.00: +23.35 | — |
| loose shapes alone | 20 | 5.00 (1; 20) | 15.00: -10.00 | 15.00: -10.00 | 16.00: -11.00 |
| loose shapes alone | 20-99 | 18.75 (1; 48) | 11.25: +7.50 | 11.25: +7.50 | 13.75: +5.00 |
| loose shapes alone | 100 | 14.71 (1; 68) | 12.00: +2.71 | 12.00: +2.71 | 15.00: -0.29 |
| loose shapes alone | rest | 14.71 (1; 68) | 11.93: +2.78 | 12.00: +2.71 | — |
| K1's + strict + loose | 20 | 75.00 (1; 20) | 15.00: +60.00 | 20.00: +55.00 | 23.00: +52.00 |
| K1's + strict + loose | 20-99 | 35.42 (1; 48) | 21.25: +14.17 | 21.25: +14.17 | 22.50: +12.92 |
| K1's + strict + loose | 100 | 47.06 (1; 68) | 20.00: +27.06 | 21.00: +26.06 | 22.00: +25.06 |
| K1's + strict + loose | rest | 47.06 (1; 68) | 20.18: +26.88 | 21.00: +26.06 | — |

#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)

| shape set | window | real mean requests per boundary | real calls / tokens per boundary | excess over C1: calls / tokens per boundary | over C2 | over C5 |
|---|---|---|---|---|---|---|
| K1's + strict (refetch_total) | 20 | 20.00 | 14.00 / 25,315 | +14.00 / +25,315 | +13.00 / +8,304 | +12.60 / +18,164 |
| K1's + strict (refetch_total) | 20-99 | 48.00 | 8.00 / 5,726 | +3.20 / -15,823 | +3.20 / -10,791 | +3.80 / -15,728 |
| K1's + strict (refetch_total) | 100 | 68.00 | 22.00 / 31,041 | +16.56 / +6,619 | +15.88 / +755 | +17.24 / +6,727 |
| K1's + strict (refetch_total) | rest | 68.00 | 22.00 / 31,041 | +16.39 / +3,256 | +15.88 / +755 | — |
| K1's + strict + loose | 20 | 20.00 | 15.00 / 25,404 | +12.00 / +24,285 | +11.00 / +7,078 | +10.40 / +16,050 |
| K1's + strict + loose | 20-99 | 48.00 | 17.00 / 9,743 | +6.80 / -15,952 | +6.80 / -11,065 | +6.20 / -16,271 |
| K1's + strict + loose | 100 | 68.00 | 32.00 / 35,147 | +18.40 / +5,265 | +17.72 / -897 | +17.04 / +3,753 |
| K1's + strict + loose | rest | 68.00 | 32.00 / 35,147 | +18.28 / +1,812 | +17.72 / -897 | — |

#### The miss

| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 20.0 | 54.0 | 8.0 | 0 / 0 | 0.00% | 156.0 | 1 | 102.0 |
| 20-99 | 1 | 48.0 | 239.0 | 9.0 | 0 / 0 | 0.00% | 476.0 | 1 | 740.0 |
| 100 | 1 | 68.0 | 271.0 | 15.0 | 0 / 0 | 0.00% | 551.0 | 1 | 757.0 |
| rest | 1 | 68.0 | 271.0 | 15.0 | 0 / 0 | 0.00% | 551.0 | 1 | 759.0 |

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

- Growth per request by position since the segment start: 0-19 4,316 (40 steps); 20-99 2,504 (127 steps); 100+ 3,016 (116 steps).
- Actual usage of the 285 included requests: cache reads 104,382,711, cache writes 3,767,722, mean context 379,477.
- Position-aware calibration: scale 1.000000; compactions at 785,000: 1 (target 1; unscaled 1).

| X | flat: compactions | mean fill | cache reads | cache writes | position-aware: compactions (unscaled) | mean fill | cache reads | cache writes |
|---|---|---|---|---|---|---|---|---|
| 300,000 | 3 | 189,872 | 53,010,457 | 1,137,365 | 4 (4) | 216,397 | 60,398,736 | 1,308,553 |
| 400,000 | 2 | 230,400 | 64,587,949 | 1,110,396 | 2 (2) | 237,708 | 66,674,334 | 1,106,702 |
| 500,000 | 1 | 330,611 | 93,227,408 | 1,030,997 | 1 (1) | 334,376 | 94,309,219 | 1,029,256 |
| 600,000 | 1 | 318,952 | 89,903,312 | 1,032,270 | 1 (1) | 318,258 | 89,719,368 | 1,018,340 |
| 700,000 | 1 | 352,892 | 99,575,597 | 1,032,688 | 1 (1) | 355,390 | 100,288,574 | 1,031,680 |
| 785,000 | 1 | 380,966 | 107,586,236 | 1,023,293 | 1 (1) | 380,794 | 107,538,624 | 1,021,843 |

At 785,000 against the actual usage: flat cache reads +3.1%, writes -72.8%, mean fill +0.4%; position-aware cache reads +3.0%, writes -72.9%, mean fill +0.3%.

The corrected loss (refetch_total, K1's shapes with writes out plus the strict set): the modeled compactions times the excess per boundary; calls / tokens.

| X | model | N=20 over C1 | over C2 | over C5 | N=100 over C1 | over C2 | over C5 |
|---|---|---|---|---|---|---|---|
| 300,000 | flat | 42 / 75,946 | 39 / 24,913 | 38 / 54,493 | 50 / 19,857 | 48 / 2,265 | 52 / 20,181 |
| 400,000 | flat | 28 / 50,631 | 26 / 16,608 | 25 / 36,328 | 33 / 13,238 | 32 / 1,510 | 34 / 13,454 |
| 500,000 | flat | 14 / 25,315 | 13 / 8,304 | 13 / 18,164 | 17 / 6,619 | 16 / 755 | 17 / 6,727 |
| 600,000 | flat | 14 / 25,315 | 13 / 8,304 | 13 / 18,164 | 17 / 6,619 | 16 / 755 | 17 / 6,727 |
| 700,000 | flat | 14 / 25,315 | 13 / 8,304 | 13 / 18,164 | 17 / 6,619 | 16 / 755 | 17 / 6,727 |
| 785,000 | flat | 14 / 25,315 | 13 / 8,304 | 13 / 18,164 | 17 / 6,619 | 16 / 755 | 17 / 6,727 |
| 300,000 | position-aware | 56 / 101,262 | 52 / 33,217 | 50 / 72,657 | 66 / 26,476 | 64 / 3,020 | 69 / 26,908 |
| 400,000 | position-aware | 28 / 50,631 | 26 / 16,608 | 25 / 36,328 | 33 / 13,238 | 32 / 1,510 | 34 / 13,454 |
| 500,000 | position-aware | 14 / 25,315 | 13 / 8,304 | 13 / 18,164 | 17 / 6,619 | 16 / 755 | 17 / 6,727 |
| 600,000 | position-aware | 14 / 25,315 | 13 / 8,304 | 13 / 18,164 | 17 / 6,619 | 16 / 755 | 17 / 6,727 |
| 700,000 | position-aware | 14 / 25,315 | 13 / 8,304 | 13 / 18,164 | 17 / 6,619 | 16 / 755 | 17 / 6,727 |
| 785,000 | position-aware | 14 / 25,315 | 13 / 8,304 | 13 / 18,164 | 17 / 6,619 | 16 / 755 | 17 / 6,727 |

## Run `sub-a58226189b58bf46f`: agent-a58226189b58bf46f.jsonl pinned at 6,874,791 bytes (sidechain thread)

- Requests 342; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; control points: C1 0, C2 0, C5 6; items after a segment's last request kept for C2 5; models {'claude-opus-5-5': 342}.

### R-C, class `1M_window`: 1 boundaries; control points C1 0, C2 0, C5 6

- Removed per boundary (modeled, mean): 682,824 tokens; last context before (mean) 781,123; kept start per boundary (modeled, mean) 34,193; first context after (mean) 72,380; postTokens (mean) 13,067.

#### Re-fetch calls per 100 requests: the control's rate, then the excess

| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |
|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 30.00 (1; 20) | — | — | 13.33: +16.67 |
| K1's shapes, writes out | 20-99 | 18.75 (1; 80) | — | — | — |
| K1's shapes, writes out | 100 | 21.00 (1; 100) | — | — | — |
| K1's shapes, writes out | rest | 16.47 (1; 170) | — | — | — |
| strict shapes | 20 | 30.00 (1; 20) | — | — | 20.00: +10.00 |
| strict shapes | 20-99 | 13.75 (1; 80) | — | — | — |
| strict shapes | 100 | 17.00 (1; 100) | — | — | — |
| strict shapes | rest | 18.82 (1; 170) | — | — | — |
| K1's + strict (refetch_total) | 20 | 60.00 (1; 20) | — | — | 33.33: +26.67 |
| K1's + strict (refetch_total) | 20-99 | 32.50 (1; 80) | — | — | — |
| K1's + strict (refetch_total) | 100 | 38.00 (1; 100) | — | — | — |
| K1's + strict (refetch_total) | rest | 35.29 (1; 170) | — | — | — |
| loose shapes alone | 20 | 0.00 (1; 20) | — | — | 15.83: -15.83 |
| loose shapes alone | 20-99 | 18.75 (1; 80) | — | — | — |
| loose shapes alone | 100 | 15.00 (1; 100) | — | — | — |
| loose shapes alone | rest | 15.29 (1; 170) | — | — | — |
| K1's + strict + loose | 20 | 60.00 (1; 20) | — | — | 49.17: +10.83 |
| K1's + strict + loose | 20-99 | 51.25 (1; 80) | — | — | — |
| K1's + strict + loose | 100 | 53.00 (1; 100) | — | — | — |
| K1's + strict + loose | rest | 50.59 (1; 170) | — | — | — |

#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)

| shape set | window | real mean requests per boundary | real calls / tokens per boundary | excess over C1: calls / tokens per boundary | over C2 | over C5 |
|---|---|---|---|---|---|---|
| K1's + strict (refetch_total) | 20 | 20.00 | 12.00 / 27,460 | — | — | +5.33 / +17,162 |
| K1's + strict (refetch_total) | 20-99 | 80.00 | 26.00 / 51,497 | — | — | — |
| K1's + strict (refetch_total) | 100 | 100.00 | 38.00 / 78,957 | — | — | — |
| K1's + strict (refetch_total) | rest | 170.00 | 60.00 / 106,164 | — | — | — |
| K1's + strict + loose | 20 | 20.00 | 12.00 / 27,460 | — | — | +2.17 / +15,228 |
| K1's + strict + loose | 20-99 | 80.00 | 41.00 / 60,246 | — | — | — |
| K1's + strict + loose | 100 | 100.00 | 53.00 / 87,705 | — | — | — |
| K1's + strict + loose | rest | 170.00 | 86.00 / 126,028 | — | — | — |

#### The miss

| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 20.0 | 36.0 | 5.0 | 0 / 0 | 0.00% | 91.0 | 0 | — |
| 20-99 | 1 | 80.0 | 244.0 | 50.0 | 2 / 2 | 8.00% | 515.0 | 0 | — |
| 100 | 1 | 100.0 | 260.0 | 53.0 | 2 / 2 | 7.55% | 535.0 | 0 | — |
| rest | 1 | 170.0 | 437.0 | 58.0 | 2 / 2 | 6.90% | 771.0 | 0 | — |

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

- Growth per request by position since the segment start: 0-19 4,238 (40 steps); 20-99 3,820 (160 steps); 100+ 2,580 (140 steps).
- Actual usage of the 342 included requests: cache reads 126,012,850, cache writes 3,580,780, mean context 378,931.
- Position-aware calibration: scale 1.000000; compactions at 785,000: 1 (target 1; unscaled 1).

| X | flat: compactions | mean fill | cache reads | cache writes | position-aware: compactions (unscaled) | mean fill | cache reads | cache writes |
|---|---|---|---|---|---|---|---|---|
| 300,000 | 4 | 183,467 | 61,285,003 | 1,460,595 | 5 (5) | 186,571 | 62,066,790 | 1,740,361 |
| 400,000 | 3 | 219,391 | 73,663,388 | 1,368,224 | 3 (3) | 250,642 | 84,163,446 | 1,556,290 |
| 500,000 | 2 | 282,819 | 95,400,763 | 1,323,361 | 2 (2) | 268,438 | 90,362,762 | 1,443,079 |
| 600,000 | 2 | 305,422 | 103,102,172 | 1,352,116 | 2 (2) | 333,062 | 112,457,230 | 1,450,038 |
| 700,000 | 1 | 370,521 | 125,434,271 | 1,284,011 | 1 (1) | 385,076 | 130,409,084 | 1,286,949 |
| 785,000 | 1 | 379,597 | 128,537,225 | 1,284,913 | 1 (1) | 379,431 | 128,481,267 | 1,284,264 |

At 785,000 against the actual usage: flat cache reads +2.0%, writes -64.1%, mean fill +0.2%; position-aware cache reads +2.0%, writes -64.1%, mean fill +0.1%.

The corrected loss (refetch_total, K1's shapes with writes out plus the strict set): the modeled compactions times the excess per boundary; calls / tokens.

| X | model | N=20 over C1 | over C2 | over C5 | N=100 over C1 | over C2 | over C5 |
|---|---|---|---|---|---|---|---|
| 300,000 | flat | — | — | 21 / 68,649 | — | — | — |
| 400,000 | flat | — | — | 16 / 51,487 | — | — | — |
| 500,000 | flat | — | — | 11 / 34,325 | — | — | — |
| 600,000 | flat | — | — | 11 / 34,325 | — | — | — |
| 700,000 | flat | — | — | 5 / 17,162 | — | — | — |
| 785,000 | flat | — | — | 5 / 17,162 | — | — | — |
| 300,000 | position-aware | — | — | 27 / 85,812 | — | — | — |
| 400,000 | position-aware | — | — | 16 / 51,487 | — | — | — |
| 500,000 | position-aware | — | — | 11 / 34,325 | — | — | — |
| 600,000 | position-aware | — | — | 11 / 34,325 | — | — | — |
| 700,000 | position-aware | — | — | 5 / 17,162 | — | — | — |
| 785,000 | position-aware | — | — | 5 / 17,162 | — | — | — |

## Run `sub-a60226a535b771d07`: agent-a60226a535b771d07.jsonl pinned at 5,746,951 bytes (sidechain thread)

- Requests 237; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; control points: C1 0, C2 0, C5 2; items after a segment's last request kept for C2 5; models {'claude-opus-5-5': 237}.

### R-C, class `1M_window`: 1 boundaries; control points C1 0, C2 0, C5 2

- Removed per boundary (modeled, mean): 711,058 tokens; last context before (mean) 781,547; kept start per boundary (modeled, mean) 62,077; first context after (mean) 107,823; postTokens (mean) 22,075.

#### Re-fetch calls per 100 requests: the control's rate, then the excess

| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |
|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 55.00 (1; 20) | — | — | 15.00: +40.00 |
| K1's shapes, writes out | 20-99 | 32.88 (1; 73) | — | — | — |
| K1's shapes, writes out | 100 | 37.63 (1; 93) | — | — | — |
| K1's shapes, writes out | rest | 37.63 (1; 93) | — | — | — |
| strict shapes | 20 | 0.00 (1; 20) | — | — | 5.00: -5.00 |
| strict shapes | 20-99 | 1.37 (1; 73) | — | — | — |
| strict shapes | 100 | 1.08 (1; 93) | — | — | — |
| strict shapes | rest | 1.08 (1; 93) | — | — | — |
| K1's + strict (refetch_total) | 20 | 55.00 (1; 20) | — | — | 20.00: +35.00 |
| K1's + strict (refetch_total) | 20-99 | 34.25 (1; 73) | — | — | — |
| K1's + strict (refetch_total) | 100 | 38.71 (1; 93) | — | — | — |
| K1's + strict (refetch_total) | rest | 38.71 (1; 93) | — | — | — |
| loose shapes alone | 20 | 10.00 (1; 20) | — | — | 10.00: +0.00 |
| loose shapes alone | 20-99 | 16.44 (1; 73) | — | — | — |
| loose shapes alone | 100 | 15.05 (1; 93) | — | — | — |
| loose shapes alone | rest | 15.05 (1; 93) | — | — | — |
| K1's + strict + loose | 20 | 65.00 (1; 20) | — | — | 30.00: +35.00 |
| K1's + strict + loose | 20-99 | 50.68 (1; 73) | — | — | — |
| K1's + strict + loose | 100 | 53.76 (1; 93) | — | — | — |
| K1's + strict + loose | rest | 53.76 (1; 93) | — | — | — |

#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)

| shape set | window | real mean requests per boundary | real calls / tokens per boundary | excess over C1: calls / tokens per boundary | over C2 | over C5 |
|---|---|---|---|---|---|---|
| K1's + strict (refetch_total) | 20 | 20.00 | 11.00 / 21,289 | — | — | +7.00 / +14,781 |
| K1's + strict (refetch_total) | 20-99 | 73.00 | 25.00 / 45,970 | — | — | — |
| K1's + strict (refetch_total) | 100 | 93.00 | 36.00 / 67,259 | — | — | — |
| K1's + strict (refetch_total) | rest | 93.00 | 36.00 / 67,259 | — | — | — |
| K1's + strict + loose | 20 | 20.00 | 13.00 / 23,868 | — | — | +7.00 / +15,436 |
| K1's + strict + loose | 20-99 | 73.00 | 37.00 / 52,577 | — | — | — |
| K1's + strict + loose | 100 | 93.00 | 50.00 / 76,445 | — | — | — |
| K1's + strict + loose | rest | 93.00 | 50.00 / 76,445 | — | — | — |

#### The miss

| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 20.0 | 25.0 | 4.0 | 0 / 1 | 25.00% | 88.0 | 0 | — |
| 20-99 | 1 | 73.0 | 190.0 | 30.0 | 3 / 3 | 20.00% | 544.0 | 0 | — |
| 100 | 1 | 93.0 | 199.0 | 31.0 | 3 / 3 | 19.35% | 557.0 | 0 | — |
| rest | 1 | 93.0 | 199.0 | 31.0 | 3 / 3 | 19.35% | 557.0 | 0 | — |

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

- Growth per request by position since the segment start: 0-19 8,160 (40 steps); 20-99 3,349 (152 steps); 100+ 2,448 (43 steps).
- Actual usage of the 237 included requests: cache reads 92,855,387, cache writes 9,492,668, mean context 431,850.
- Position-aware calibration: scale 1.000000; compactions at 785,000: 1 (target 1; unscaled 1).

| X | flat: compactions | mean fill | cache reads | cache writes | position-aware: compactions (unscaled) | mean fill | cache reads | cache writes |
|---|---|---|---|---|---|---|---|---|
| 300,000 | 4 | 190,992 | 43,794,417 | 1,470,646 | 7 (7) | 213,032 | 48,134,194 | 2,354,262 |
| 400,000 | 3 | 261,932 | 60,721,925 | 1,356,017 | 4 (4) | 261,559 | 60,111,339 | 1,878,113 |
| 500,000 | 2 | 269,095 | 62,516,324 | 1,259,227 | 2 (2) | 319,240 | 74,239,220 | 1,420,564 |
| 600,000 | 1 | 355,146 | 83,014,216 | 1,155,474 | 1 (1) | 408,260 | 95,573,389 | 1,184,261 |
| 700,000 | 1 | 382,095 | 89,401,137 | 1,155,415 | 1 (1) | 439,194 | 102,862,377 | 1,226,635 |
| 785,000 | 1 | 425,019 | 99,574,632 | 1,154,812 | 1 (1) | 437,664 | 102,543,449 | 1,182,971 |

At 785,000 against the actual usage: flat cache reads +7.2%, writes -87.8%, mean fill -1.6%; position-aware cache reads +10.4%, writes -87.5%, mean fill +1.3%.

The corrected loss (refetch_total, K1's shapes with writes out plus the strict set): the modeled compactions times the excess per boundary; calls / tokens.

| X | model | N=20 over C1 | over C2 | over C5 | N=100 over C1 | over C2 | over C5 |
|---|---|---|---|---|---|---|---|
| 300,000 | flat | — | — | 28 / 59,125 | — | — | — |
| 400,000 | flat | — | — | 21 / 44,344 | — | — | — |
| 500,000 | flat | — | — | 14 / 29,563 | — | — | — |
| 600,000 | flat | — | — | 7 / 14,781 | — | — | — |
| 700,000 | flat | — | — | 7 / 14,781 | — | — | — |
| 785,000 | flat | — | — | 7 / 14,781 | — | — | — |
| 300,000 | position-aware | — | — | 49 / 103,469 | — | — | — |
| 400,000 | position-aware | — | — | 28 / 59,125 | — | — | — |
| 500,000 | position-aware | — | — | 14 / 29,563 | — | — | — |
| 600,000 | position-aware | — | — | 7 / 14,781 | — | — | — |
| 700,000 | position-aware | — | — | 7 / 14,781 | — | — | — |
| 785,000 | position-aware | — | — | 7 / 14,781 | — | — | — |

## Run `sub-a88c7c57f2fa2a96b`: agent-a88c7c57f2fa2a96b.jsonl pinned at 14,223,996 bytes (sidechain thread)

- Requests 723; segments with requests 4; boundaries on the thread 3; skipped boundaries 0; control points: C1 1, C2 1, C5 14; items after a segment's last request kept for C2 13; models {'claude-opus-5-5': 723}.

### R-C, class `1M_window`: 3 boundaries; control points C1 1, C2 1, C5 14

- Removed per boundary (modeled, mean): 489,853 tokens; last context before (mean) 777,900; kept start per boundary (modeled, mean) 45,912; first context after (mean) 88,535; postTokens (mean) 22,068.

#### Re-fetch calls per 100 requests: the control's rate, then the excess

| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |
|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 30.00 (3; 60) | 25.00: +5.00 | 40.00: -10.00 | 31.43: -1.43 |
| K1's shapes, writes out | 20-99 | 30.42 (3; 240) | 25.00: +5.42 | 18.75: +11.67 | 25.83: +4.58 |
| K1's shapes, writes out | 100 | 30.33 (3; 300) | 25.00: +5.33 | 23.00: +7.33 | 28.00: +2.33 |
| K1's shapes, writes out | rest | 29.90 (3; 572) | 23.77: +6.12 | 23.00: +6.90 | — |
| strict shapes | 20 | 16.67 (3; 60) | 0.00: +16.67 | 0.00: +16.67 | 2.50: +14.17 |
| strict shapes | 20-99 | 10.00 (3; 240) | 0.00: +10.00 | 0.00: +10.00 | 0.00: +10.00 |
| strict shapes | 100 | 11.33 (3; 300) | 0.00: +11.33 | 0.00: +11.33 | 0.67: +10.67 |
| strict shapes | rest | 6.99 (3; 572) | 0.00: +6.99 | 0.00: +6.99 | — |
| K1's + strict (refetch_total) | 20 | 46.67 (3; 60) | 25.00: +21.67 | 40.00: +6.67 | 33.93: +12.74 |
| K1's + strict (refetch_total) | 20-99 | 40.42 (3; 240) | 25.00: +15.42 | 18.75: +21.67 | 25.83: +14.58 |
| K1's + strict (refetch_total) | 100 | 41.67 (3; 300) | 25.00: +16.67 | 23.00: +18.67 | 28.67: +13.00 |
| K1's + strict (refetch_total) | rest | 36.89 (3; 572) | 23.77: +13.12 | 23.00: +13.89 | — |
| loose shapes alone | 20 | 11.67 (3; 60) | 25.00: -13.33 | 10.00: +1.67 | 11.43: +0.24 |
| loose shapes alone | 20-99 | 14.17 (3; 240) | 10.00: +4.17 | 10.00: +4.17 | 10.83: +3.33 |
| loose shapes alone | 100 | 13.67 (3; 300) | 13.00: +0.67 | 10.00: +3.67 | 11.67: +2.00 |
| loose shapes alone | rest | 13.64 (3; 572) | 12.30: +1.34 | 10.00: +3.64 | — |
| K1's + strict + loose | 20 | 58.33 (3; 60) | 50.00: +8.33 | 50.00: +8.33 | 45.36: +12.98 |
| K1's + strict + loose | 20-99 | 54.58 (3; 240) | 35.00: +19.58 | 28.75: +25.83 | 36.67: +17.92 |
| K1's + strict + loose | 100 | 55.33 (3; 300) | 38.00: +17.33 | 33.00: +22.33 | 40.33: +15.00 |
| K1's + strict + loose | rest | 50.52 (3; 572) | 36.07: +14.46 | 33.00: +17.52 | — |

#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)

| shape set | window | real mean requests per boundary | real calls / tokens per boundary | excess over C1: calls / tokens per boundary | over C2 | over C5 |
|---|---|---|---|---|---|---|
| K1's + strict (refetch_total) | 20 | 20.00 | 9.33 / 19,927 | +4.33 / +17,085 | +1.33 / +10,820 | +2.55 / +13,768 |
| K1's + strict (refetch_total) | 20-99 | 80.00 | 32.33 / 43,219 | +12.33 / +20,822 | +17.33 / +24,560 | +11.67 / +20,861 |
| K1's + strict (refetch_total) | 100 | 100.00 | 41.67 / 63,146 | +16.67 / +37,907 | +18.67 / +35,380 | +13.00 / +33,314 |
| K1's + strict (refetch_total) | rest | 190.67 | 70.33 / 92,821 | +25.01 / +43,490 | +26.48 / +39,881 | — |
| K1's + strict + loose | 20 | 20.00 | 11.67 / 22,454 | +1.67 / +16,956 | +1.67 / +12,735 | +2.60 / +14,750 |
| K1's + strict + loose | 20-99 | 80.00 | 43.67 / 51,660 | +15.67 / +26,517 | +20.67 / +26,688 | +14.33 / +24,747 |
| K1's + strict + loose | 100 | 100.00 | 55.33 / 74,114 | +17.33 / +43,474 | +22.33 / +39,423 | +15.00 / +37,681 |
| K1's + strict + loose | rest | 190.67 | 96.33 / 111,652 | +27.57 / +47,349 | +33.41 / +45,509 | — |

#### The miss

| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 3 | 20.0 | 36.3 | 14.0 | 1 / 1 | 4.76% | 100.3 | 1 | 168.0 |
| 20-99 | 3 | 80.0 | 195.3 | 34.0 | 1 / 4 | 4.90% | 443.7 | 1 | 781.0 |
| 100 | 3 | 100.0 | 207.3 | 39.3 | 1 / 4 | 4.24% | 465.7 | 1 | 800.0 |
| rest | 3 | 190.7 | 431.7 | 68.0 | 1 / 5 | 2.94% | 827.0 | 1 | 825.0 |

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

- Growth per request by position since the segment start: 0-19 5,610 (80 steps); 20-99 3,765 (320 steps); 100+ 3,078 (319 steps).
- Actual usage of the 723 included requests: cache reads 294,707,109, cache writes 9,479,128, mean context 420,730.
- Position-aware calibration: scale 1.000000; compactions at 785,000: 3 (target 3; unscaled 3).

| X | flat: compactions | mean fill | cache reads | cache writes | position-aware: compactions (unscaled) | mean fill | cache reads | cache writes |
|---|---|---|---|---|---|---|---|---|
| 300,000 | 11 | 197,138 | 138,988,677 | 3,541,971 | 14 (14) | 203,621 | 142,837,772 | 4,380,087 |
| 400,000 | 8 | 238,098 | 168,781,451 | 3,363,254 | 9 (9) | 255,844 | 181,037,175 | 3,937,733 |
| 500,000 | 6 | 279,733 | 199,026,581 | 3,220,526 | 7 (7) | 310,591 | 220,892,206 | 3,665,381 |
| 600,000 | 5 | 353,510 | 252,509,918 | 3,077,736 | 5 (5) | 341,030 | 243,309,418 | 3,255,279 |
| 700,000 | 4 | 367,948 | 262,990,325 | 3,036,004 | 4 (4) | 402,984 | 288,100,147 | 3,257,581 |
| 785,000 | 3 | 426,207 | 305,174,853 | 2,973,094 | 3 (3) | 435,489 | 311,869,785 | 2,988,661 |

At 785,000 against the actual usage: flat cache reads +3.6%, writes -68.6%, mean fill +1.3%; position-aware cache reads +5.8%, writes -68.5%, mean fill +3.5%.

The corrected loss (refetch_total, K1's shapes with writes out plus the strict set): the modeled compactions times the excess per boundary; calls / tokens.

| X | model | N=20 over C1 | over C2 | over C5 | N=100 over C1 | over C2 | over C5 |
|---|---|---|---|---|---|---|---|
| 300,000 | flat | 48 / 187,933 | 15 / 119,021 | 28 / 151,447 | 183 / 416,973 | 205 / 389,186 | 143 / 366,451 |
| 400,000 | flat | 35 / 136,678 | 11 / 86,561 | 20 / 110,143 | 133 / 303,253 | 149 / 283,044 | 104 / 266,510 |
| 500,000 | flat | 26 / 102,509 | 8 / 64,921 | 15 / 82,607 | 100 / 227,440 | 112 / 212,283 | 78 / 199,882 |
| 600,000 | flat | 22 / 85,424 | 7 / 54,100 | 13 / 68,840 | 83 / 189,533 | 93 / 176,902 | 65 / 166,568 |
| 700,000 | flat | 17 / 68,339 | 5 / 43,280 | 10 / 55,072 | 67 / 151,626 | 75 / 141,522 | 52 / 133,255 |
| 785,000 | flat | 13 / 51,254 | 4 / 32,460 | 8 / 41,304 | 50 / 113,720 | 56 / 106,142 | 39 / 99,941 |
| 300,000 | position-aware | 61 / 239,187 | 19 / 151,481 | 36 / 192,751 | 233 / 530,692 | 261 / 495,327 | 182 / 466,392 |
| 400,000 | position-aware | 39 / 153,763 | 12 / 97,381 | 23 / 123,911 | 150 / 341,159 | 168 / 318,424 | 117 / 299,823 |
| 500,000 | position-aware | 30 / 119,594 | 9 / 75,741 | 18 / 96,375 | 117 / 265,346 | 131 / 247,664 | 91 / 233,196 |
| 600,000 | position-aware | 22 / 85,424 | 7 / 54,100 | 13 / 68,840 | 83 / 189,533 | 93 / 176,902 | 65 / 166,568 |
| 700,000 | position-aware | 17 / 68,339 | 5 / 43,280 | 10 / 55,072 | 67 / 151,626 | 75 / 141,522 | 52 / 133,255 |
| 785,000 | position-aware | 13 / 51,254 | 4 / 32,460 | 8 / 41,304 | 50 / 113,720 | 56 / 106,142 | 39 / 99,941 |

## Run `sub-a90d7cc077452b42d`: agent-a90d7cc077452b42d.jsonl pinned at 5,722,161 bytes (sidechain thread)

- Requests 296; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; control points: C1 1, C2 1, C5 5; items after a segment's last request kept for C2 6; models {'claude-opus-5-5': 296}.

### R-C, class `1M_window`: 1 boundaries; control points C1 1, C2 1, C5 5

- Removed per boundary (modeled, mean): 425,265 tokens; last context before (mean) 780,956; kept start per boundary (modeled, mean) 43,489; first context after (mean) 90,060; postTokens (mean) 20,512.

#### Re-fetch calls per 100 requests: the control's rate, then the excess

| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |
|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 30.00 (1; 20) | 15.00: +15.00 | 15.00: +15.00 | 13.00: +17.00 |
| K1's shapes, writes out | 20-99 | 25.00 (1; 76) | 12.50: +12.50 | 12.50: +12.50 | 12.50: +12.50 |
| K1's shapes, writes out | 100 | 26.04 (1; 96) | 13.00: +13.04 | 13.00: +13.04 | 13.00: +13.04 |
| K1's shapes, writes out | rest | 26.04 (1; 96) | 13.00: +13.04 | 13.00: +13.04 | — |
| strict shapes | 20 | 10.00 (1; 20) | 0.00: +10.00 | 0.00: +10.00 | 1.00: +9.00 |
| strict shapes | 20-99 | 3.95 (1; 76) | 0.00: +3.95 | 0.00: +3.95 | 0.00: +3.95 |
| strict shapes | 100 | 5.21 (1; 96) | 0.00: +5.21 | 0.00: +5.21 | 0.00: +5.21 |
| strict shapes | rest | 5.21 (1; 96) | 0.00: +5.21 | 0.00: +5.21 | — |
| K1's + strict (refetch_total) | 20 | 40.00 (1; 20) | 15.00: +25.00 | 15.00: +25.00 | 14.00: +26.00 |
| K1's + strict (refetch_total) | 20-99 | 28.95 (1; 76) | 12.50: +16.45 | 12.50: +16.45 | 12.50: +16.45 |
| K1's + strict (refetch_total) | 100 | 31.25 (1; 96) | 13.00: +18.25 | 13.00: +18.25 | 13.00: +18.25 |
| K1's + strict (refetch_total) | rest | 31.25 (1; 96) | 13.00: +18.25 | 13.00: +18.25 | — |
| loose shapes alone | 20 | 10.00 (1; 20) | 20.00: -10.00 | 20.00: -10.00 | 13.00: -3.00 |
| loose shapes alone | 20-99 | 11.84 (1; 76) | 12.50: -0.66 | 12.50: -0.66 | 12.50: -0.66 |
| loose shapes alone | 100 | 11.46 (1; 96) | 14.00: -2.54 | 14.00: -2.54 | 14.00: -2.54 |
| loose shapes alone | rest | 11.46 (1; 96) | 14.00: -2.54 | 14.00: -2.54 | — |
| K1's + strict + loose | 20 | 50.00 (1; 20) | 35.00: +15.00 | 35.00: +15.00 | 27.00: +23.00 |
| K1's + strict + loose | 20-99 | 40.79 (1; 76) | 25.00: +15.79 | 25.00: +15.79 | 25.00: +15.79 |
| K1's + strict + loose | 100 | 42.71 (1; 96) | 27.00: +15.71 | 27.00: +15.71 | 27.00: +15.71 |
| K1's + strict + loose | rest | 42.71 (1; 96) | 27.00: +15.71 | 27.00: +15.71 | — |

#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)

| shape set | window | real mean requests per boundary | real calls / tokens per boundary | excess over C1: calls / tokens per boundary | over C2 | over C5 |
|---|---|---|---|---|---|---|
| K1's + strict (refetch_total) | 20 | 20.00 | 8.00 / 15,197 | +5.00 / +13,170 | +5.00 / +13,170 | +5.20 / +11,233 |
| K1's + strict (refetch_total) | 20-99 | 76.00 | 22.00 / 31,811 | +12.50 / +15,431 | +12.50 / +15,431 | +12.50 / +15,431 |
| K1's + strict (refetch_total) | 100 | 96.00 | 30.00 / 47,008 | +17.52 / +28,510 | +17.52 / +28,510 | +17.52 / +28,510 |
| K1's + strict (refetch_total) | rest | 96.00 | 30.00 / 47,008 | +17.52 / +28,510 | +17.52 / +28,510 | — |
| K1's + strict + loose | 20 | 20.00 | 10.00 / 16,821 | +3.00 / +9,715 | +3.00 / +9,715 | +4.60 / +11,177 |
| K1's + strict + loose | 20-99 | 76.00 | 31.00 / 40,756 | +12.00 / +20,697 | +12.00 / +20,697 | +12.00 / +20,697 |
| K1's + strict + loose | 100 | 96.00 | 41.00 / 57,577 | +15.08 / +30,485 | +15.08 / +30,485 | +15.08 / +30,485 |
| K1's + strict + loose | rest | 96.00 | 41.00 / 57,577 | +15.08 / +30,485 | +15.08 / +30,485 | — |

#### The miss

| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 20.0 | 21.0 | 5.0 | 0 / 0 | 0.00% | 115.0 | 1 | 188.0 |
| 20-99 | 1 | 76.0 | 261.0 | 48.0 | 0 / 0 | 0.00% | 594.0 | 1 | 626.0 |
| 100 | 1 | 96.0 | 267.0 | 48.0 | 0 / 0 | 0.00% | 618.0 | 1 | 678.0 |
| rest | 1 | 96.0 | 267.0 | 48.0 | 0 / 0 | 0.00% | 618.0 | 1 | 678.0 |

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

- Growth per request by position since the segment start: 0-19 3,757 (40 steps); 20-99 3,248 (155 steps); 100+ 3,528 (99 steps).
- Actual usage of the 296 included requests: cache reads 102,181,749, cache writes 3,528,123, mean context 357,130.
- Position-aware calibration: scale 1.000000; compactions at 785,000: 1 (target 1; unscaled 1).

| X | flat: compactions | mean fill | cache reads | cache writes | position-aware: compactions (unscaled) | mean fill | cache reads | cache writes |
|---|---|---|---|---|---|---|---|---|
| 300,000 | 4 | 182,349 | 52,560,054 | 1,415,164 | 4 (4) | 187,058 | 53,929,045 | 1,440,121 |
| 400,000 | 3 | 231,923 | 67,327,241 | 1,322,059 | 3 (3) | 233,509 | 67,798,911 | 1,319,744 |
| 500,000 | 2 | 272,897 | 79,513,423 | 1,263,964 | 2 (2) | 273,827 | 79,798,172 | 1,254,550 |
| 600,000 | 1 | 362,278 | 106,051,839 | 1,182,441 | 1 (1) | 362,533 | 106,119,691 | 1,190,012 |
| 700,000 | 1 | 342,397 | 100,194,977 | 1,154,596 | 1 (1) | 341,561 | 99,944,768 | 1,157,414 |
| 785,000 | 1 | 364,866 | 106,819,694 | 1,180,494 | 1 (1) | 364,617 | 106,747,350 | 1,179,266 |

At 785,000 against the actual usage: flat cache reads +4.5%, writes -66.5%, mean fill +2.2%; position-aware cache reads +4.5%, writes -66.6%, mean fill +2.1%.

The corrected loss (refetch_total, K1's shapes with writes out plus the strict set): the modeled compactions times the excess per boundary; calls / tokens.

| X | model | N=20 over C1 | over C2 | over C5 | N=100 over C1 | over C2 | over C5 |
|---|---|---|---|---|---|---|---|
| 300,000 | flat | 20 / 52,680 | 20 / 52,680 | 21 / 44,930 | 70 / 114,040 | 70 / 114,040 | 70 / 114,040 |
| 400,000 | flat | 15 / 39,510 | 15 / 39,510 | 16 / 33,698 | 53 / 85,530 | 53 / 85,530 | 53 / 85,530 |
| 500,000 | flat | 10 / 26,340 | 10 / 26,340 | 10 / 22,465 | 35 / 57,020 | 35 / 57,020 | 35 / 57,020 |
| 600,000 | flat | 5 / 13,170 | 5 / 13,170 | 5 / 11,232 | 18 / 28,510 | 18 / 28,510 | 18 / 28,510 |
| 700,000 | flat | 5 / 13,170 | 5 / 13,170 | 5 / 11,232 | 18 / 28,510 | 18 / 28,510 | 18 / 28,510 |
| 785,000 | flat | 5 / 13,170 | 5 / 13,170 | 5 / 11,232 | 18 / 28,510 | 18 / 28,510 | 18 / 28,510 |
| 300,000 | position-aware | 20 / 52,680 | 20 / 52,680 | 21 / 44,930 | 70 / 114,040 | 70 / 114,040 | 70 / 114,040 |
| 400,000 | position-aware | 15 / 39,510 | 15 / 39,510 | 16 / 33,698 | 53 / 85,530 | 53 / 85,530 | 53 / 85,530 |
| 500,000 | position-aware | 10 / 26,340 | 10 / 26,340 | 10 / 22,465 | 35 / 57,020 | 35 / 57,020 | 35 / 57,020 |
| 600,000 | position-aware | 5 / 13,170 | 5 / 13,170 | 5 / 11,232 | 18 / 28,510 | 18 / 28,510 | 18 / 28,510 |
| 700,000 | position-aware | 5 / 13,170 | 5 / 13,170 | 5 / 11,232 | 18 / 28,510 | 18 / 28,510 | 18 / 28,510 |
| 785,000 | position-aware | 5 / 13,170 | 5 / 13,170 | 5 / 11,232 | 18 / 28,510 | 18 / 28,510 | 18 / 28,510 |

## Run `sub-aa842df27d05dd80d`: agent-aa842df27d05dd80d.jsonl pinned at 5,739,552 bytes (sidechain thread)

- Requests 198; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; control points: C1 0, C2 0, C5 0; items after a segment's last request kept for C2 5; models {'claude-opus-5-5': 198}.

### R-C, class `1M_window`: 1 boundaries; control points C1 0, C2 0, C5 0

- Removed per boundary (modeled, mean): 710,088 tokens; last context before (mean) 742,912; kept start per boundary (modeled, mean) 53,761; first context after (mean) 96,415; postTokens (mean) 16,305.

#### Re-fetch calls per 100 requests: the control's rate, then the excess

| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |
|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 80.00 (1; 20) | — | — | — |
| K1's shapes, writes out | 20-99 | 30.00 (1; 80) | — | — | — |
| K1's shapes, writes out | 100 | 40.00 (1; 100) | — | — | — |
| K1's shapes, writes out | rest | 39.64 (1; 111) | — | — | — |
| strict shapes | 20 | 0.00 (1; 20) | — | — | — |
| strict shapes | 20-99 | 3.75 (1; 80) | — | — | — |
| strict shapes | 100 | 3.00 (1; 100) | — | — | — |
| strict shapes | rest | 4.50 (1; 111) | — | — | — |
| K1's + strict (refetch_total) | 20 | 80.00 (1; 20) | — | — | — |
| K1's + strict (refetch_total) | 20-99 | 33.75 (1; 80) | — | — | — |
| K1's + strict (refetch_total) | 100 | 43.00 (1; 100) | — | — | — |
| K1's + strict (refetch_total) | rest | 44.14 (1; 111) | — | — | — |
| loose shapes alone | 20 | 0.00 (1; 20) | — | — | — |
| loose shapes alone | 20-99 | 20.00 (1; 80) | — | — | — |
| loose shapes alone | 100 | 16.00 (1; 100) | — | — | — |
| loose shapes alone | rest | 14.41 (1; 111) | — | — | — |
| K1's + strict + loose | 20 | 80.00 (1; 20) | — | — | — |
| K1's + strict + loose | 20-99 | 53.75 (1; 80) | — | — | — |
| K1's + strict + loose | 100 | 59.00 (1; 100) | — | — | — |
| K1's + strict + loose | rest | 58.56 (1; 111) | — | — | — |

#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)

| shape set | window | real mean requests per boundary | real calls / tokens per boundary | excess over C1: calls / tokens per boundary | over C2 | over C5 |
|---|---|---|---|---|---|---|
| K1's + strict (refetch_total) | 20 | 20.00 | 16.00 / 32,247 | — | — | — |
| K1's + strict (refetch_total) | 20-99 | 80.00 | 27.00 / 34,195 | — | — | — |
| K1's + strict (refetch_total) | 100 | 100.00 | 43.00 / 66,442 | — | — | — |
| K1's + strict (refetch_total) | rest | 111.00 | 49.00 / 86,569 | — | — | — |
| K1's + strict + loose | 20 | 20.00 | 16.00 / 32,247 | — | — | — |
| K1's + strict + loose | 20-99 | 80.00 | 43.00 / 46,836 | — | — | — |
| K1's + strict + loose | 100 | 100.00 | 59.00 / 79,083 | — | — | — |
| K1's + strict + loose | rest | 111.00 | 65.00 / 99,210 | — | — | — |

#### The miss

| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 20.0 | 14.0 | 2.0 | 0 / 0 | 0.00% | 57.0 | 0 | — |
| 20-99 | 1 | 80.0 | 196.0 | 15.0 | 0 / 1 | 6.67% | 473.0 | 0 | — |
| 100 | 1 | 100.0 | 201.0 | 16.0 | 0 / 1 | 6.25% | 484.0 | 0 | — |
| rest | 1 | 111.0 | 346.0 | 19.0 | 0 / 2 | 10.53% | 750.0 | 0 | — |

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

- Growth per request by position since the segment start: 0-19 5,062 (40 steps); 20-99 4,962 (146 steps); 100+ 3,533 (10 steps).
- Actual usage of the 198 included requests: cache reads 61,286,393, cache writes 2,964,670, mean context 324,502.
- Position-aware calibration: scale 1.000000; compactions at 785,000: 1 (target 1; unscaled 1).

| X | flat: compactions | mean fill | cache reads | cache writes | position-aware: compactions (unscaled) | mean fill | cache reads | cache writes |
|---|---|---|---|---|---|---|---|---|
| 300,000 | 4 | 189,306 | 36,064,546 | 1,418,030 | 4 (4) | 189,569 | 36,098,974 | 1,435,750 |
| 400,000 | 3 | 245,951 | 47,372,510 | 1,325,759 | 3 (3) | 247,250 | 47,611,816 | 1,343,696 |
| 500,000 | 2 | 276,957 | 53,593,307 | 1,244,195 | 2 (2) | 278,149 | 53,812,996 | 1,260,433 |
| 600,000 | 1 | 372,771 | 72,673,889 | 1,134,805 | 1 (1) | 373,618 | 72,846,218 | 1,130,084 |
| 700,000 | 1 | 337,932 | 65,759,094 | 1,151,406 | 1 (1) | 338,125 | 65,801,221 | 1,147,542 |
| 785,000 | 1 | 344,528 | 67,067,123 | 1,149,339 | 1 (1) | 345,088 | 67,164,127 | 1,163,303 |

At 785,000 against the actual usage: flat cache reads +9.4%, writes -61.2%, mean fill +6.2%; position-aware cache reads +9.6%, writes -60.8%, mean fill +6.3%.

The corrected loss (refetch_total, K1's shapes with writes out plus the strict set): the modeled compactions times the excess per boundary; calls / tokens.

| X | model | N=20 over C1 | over C2 | over C5 | N=100 over C1 | over C2 | over C5 |
|---|---|---|---|---|---|---|---|
| 300,000 | flat | — | — | — | — | — | — |
| 400,000 | flat | — | — | — | — | — | — |
| 500,000 | flat | — | — | — | — | — | — |
| 600,000 | flat | — | — | — | — | — | — |
| 700,000 | flat | — | — | — | — | — | — |
| 785,000 | flat | — | — | — | — | — | — |
| 300,000 | position-aware | — | — | — | — | — | — |
| 400,000 | position-aware | — | — | — | — | — | — |
| 500,000 | position-aware | — | — | — | — | — | — |
| 600,000 | position-aware | — | — | — | — | — | — |
| 700,000 | position-aware | — | — | — | — | — | — |
| 785,000 | position-aware | — | — | — | — | — | — |

## Run `sub-aad0e50d8019b70bb`: agent-aad0e50d8019b70bb.jsonl pinned at 4,660,437 bytes (sidechain thread)

- Requests 179; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; control points: C1 0, C2 0, C5 3; items after a segment's last request kept for C2 4; models {'claude-opus-5-5': 179}.

### R-C, class `1M_window`: 1 boundaries; control points C1 0, C2 0, C5 3

- Removed per boundary (modeled, mean): 438,271 tokens; last context before (mean) 781,057; kept start per boundary (modeled, mean) 34,314; first context after (mean) 75,460; postTokens (mean) 13,802.

#### Re-fetch calls per 100 requests: the control's rate, then the excess

| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |
|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 16.67 (1; 6) | — | — | 16.67: +0.00 |
| K1's shapes, writes out | 20-99 | — (0; 0) | — | — | — |
| K1's shapes, writes out | 100 | 16.67 (1; 6) | — | — | — |
| K1's shapes, writes out | rest | 16.67 (1; 6) | — | — | — |
| strict shapes | 20 | 0.00 (1; 6) | — | — | 13.33: -13.33 |
| strict shapes | 20-99 | — (0; 0) | — | — | — |
| strict shapes | 100 | 0.00 (1; 6) | — | — | — |
| strict shapes | rest | 0.00 (1; 6) | — | — | — |
| K1's + strict (refetch_total) | 20 | 16.67 (1; 6) | — | — | 30.00: -13.33 |
| K1's + strict (refetch_total) | 20-99 | — (0; 0) | — | — | — |
| K1's + strict (refetch_total) | 100 | 16.67 (1; 6) | — | — | — |
| K1's + strict (refetch_total) | rest | 16.67 (1; 6) | — | — | — |
| loose shapes alone | 20 | 0.00 (1; 6) | — | — | 18.33: -18.33 |
| loose shapes alone | 20-99 | — (0; 0) | — | — | — |
| loose shapes alone | 100 | 0.00 (1; 6) | — | — | — |
| loose shapes alone | rest | 0.00 (1; 6) | — | — | — |
| K1's + strict + loose | 20 | 16.67 (1; 6) | — | — | 48.33: -31.67 |
| K1's + strict + loose | 20-99 | — (0; 0) | — | — | — |
| K1's + strict + loose | 100 | 16.67 (1; 6) | — | — | — |
| K1's + strict + loose | rest | 16.67 (1; 6) | — | — | — |

#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)

| shape set | window | real mean requests per boundary | real calls / tokens per boundary | excess over C1: calls / tokens per boundary | over C2 | over C5 |
|---|---|---|---|---|---|---|
| K1's + strict (refetch_total) | 20 | 6.00 | 1.00 / 7,041 | — | — | -0.80 / +1,323 |
| K1's + strict (refetch_total) | 100 | 6.00 | 1.00 / 7,041 | — | — | — |
| K1's + strict (refetch_total) | rest | 6.00 | 1.00 / 7,041 | — | — | — |
| K1's + strict + loose | 20 | 6.00 | 1.00 / 7,041 | — | — | -1.90 / +822 |
| K1's + strict + loose | 100 | 6.00 | 1.00 / 7,041 | — | — | — |
| K1's + strict + loose | rest | 6.00 | 1.00 / 7,041 | — | — | — |

#### The miss

| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 6.0 | 114.0 | 10.0 | 0 / 0 | 0.00% | 302.0 | 0 | — |
| 20-99 | 1 | 0.0 | 0.0 | 0.0 | 0 / 0 | — | 0.0 | 0 | — |
| 100 | 1 | 6.0 | 114.0 | 10.0 | 0 / 0 | 0.00% | 302.0 | 0 | — |
| rest | 1 | 6.0 | 114.0 | 10.0 | 0 / 0 | 0.00% | 302.0 | 0 | — |

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

- Growth per request by position since the segment start: 0-19 7,880 (25 steps); 20-99 3,541 (80 steps); 100+ 3,774 (72 steps).
- Actual usage of the 179 included requests: cache reads 80,707,997, cache writes 1,624,515, mean context 459,960.
- Position-aware calibration: scale 1.000000; compactions at 785,000: 1 (target 1; unscaled 1).

| X | flat: compactions | mean fill | cache reads | cache writes | position-aware: compactions (unscaled) | mean fill | cache reads | cache writes |
|---|---|---|---|---|---|---|---|---|
| 300,000 | 3 | 190,662 | 33,169,747 | 958,655 | 3 (3) | 197,530 | 34,200,180 | 1,157,707 |
| 400,000 | 2 | 206,800 | 36,045,375 | 971,913 | 2 (2) | 225,214 | 39,268,194 | 1,045,115 |
| 500,000 | 1 | 291,263 | 51,243,399 | 892,613 | 1 (1) | 305,023 | 53,698,512 | 900,684 |
| 600,000 | 1 | 336,188 | 59,295,807 | 881,843 | 1 (1) | 367,281 | 64,755,223 | 988,007 |
| 700,000 | 1 | 353,384 | 62,357,827 | 897,872 | 1 (1) | 363,225 | 64,077,789 | 939,421 |
| 785,000 | 1 | 454,550 | 80,462,831 | 901,564 | 1 (1) | 454,635 | 80,476,130 | 903,594 |

At 785,000 against the actual usage: flat cache reads -0.3%, writes -44.5%, mean fill -1.2%; position-aware cache reads -0.3%, writes -44.4%, mean fill -1.2%.

The corrected loss (refetch_total, K1's shapes with writes out plus the strict set): the modeled compactions times the excess per boundary; calls / tokens.

| X | model | N=20 over C1 | over C2 | over C5 | N=100 over C1 | over C2 | over C5 |
|---|---|---|---|---|---|---|---|
| 300,000 | flat | — | — | -2 / 3,970 | — | — | — |
| 400,000 | flat | — | — | -2 / 2,647 | — | — | — |
| 500,000 | flat | — | — | -1 / 1,323 | — | — | — |
| 600,000 | flat | — | — | -1 / 1,323 | — | — | — |
| 700,000 | flat | — | — | -1 / 1,323 | — | — | — |
| 785,000 | flat | — | — | -1 / 1,323 | — | — | — |
| 300,000 | position-aware | — | — | -2 / 3,970 | — | — | — |
| 400,000 | position-aware | — | — | -2 / 2,647 | — | — | — |
| 500,000 | position-aware | — | — | -1 / 1,323 | — | — | — |
| 600,000 | position-aware | — | — | -1 / 1,323 | — | — | — |
| 700,000 | position-aware | — | — | -1 / 1,323 | — | — | — |
| 785,000 | position-aware | — | — | -1 / 1,323 | — | — | — |

## Run `sub-ab1c8cf107bc6ad72`: agent-ab1c8cf107bc6ad72.jsonl pinned at 4,544,022 bytes (sidechain thread)

- Requests 193; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; control points: C1 0, C2 0, C5 4; items after a segment's last request kept for C2 4; models {'claude-opus-5-5': 193}.

### R-C, class `1M_window`: 1 boundaries; control points C1 0, C2 0, C5 4

- Removed per boundary (modeled, mean): 668,626 tokens; last context before (mean) 780,682; kept start per boundary (modeled, mean) 49,466; first context after (mean) 88,302; postTokens (mean) 13,214.

#### Re-fetch calls per 100 requests: the control's rate, then the excess

| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |
|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 28.57 (1; 7) | — | — | 26.25: +2.32 |
| K1's shapes, writes out | 20-99 | — (0; 0) | — | — | — |
| K1's shapes, writes out | 100 | 28.57 (1; 7) | — | — | — |
| K1's shapes, writes out | rest | 28.57 (1; 7) | — | — | — |
| strict shapes | 20 | 14.29 (1; 7) | — | — | 25.00: -10.71 |
| strict shapes | 20-99 | — (0; 0) | — | — | — |
| strict shapes | 100 | 14.29 (1; 7) | — | — | — |
| strict shapes | rest | 14.29 (1; 7) | — | — | — |
| K1's + strict (refetch_total) | 20 | 42.86 (1; 7) | — | — | 51.25: -8.39 |
| K1's + strict (refetch_total) | 20-99 | — (0; 0) | — | — | — |
| K1's + strict (refetch_total) | 100 | 42.86 (1; 7) | — | — | — |
| K1's + strict (refetch_total) | rest | 42.86 (1; 7) | — | — | — |
| loose shapes alone | 20 | 42.86 (1; 7) | — | — | 10.00: +32.86 |
| loose shapes alone | 20-99 | — (0; 0) | — | — | — |
| loose shapes alone | 100 | 42.86 (1; 7) | — | — | — |
| loose shapes alone | rest | 42.86 (1; 7) | — | — | — |
| K1's + strict + loose | 20 | 85.71 (1; 7) | — | — | 61.25: +24.46 |
| K1's + strict + loose | 20-99 | — (0; 0) | — | — | — |
| K1's + strict + loose | 100 | 85.71 (1; 7) | — | — | — |
| K1's + strict + loose | rest | 85.71 (1; 7) | — | — | — |

#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)

| shape set | window | real mean requests per boundary | real calls / tokens per boundary | excess over C1: calls / tokens per boundary | over C2 | over C5 |
|---|---|---|---|---|---|---|
| K1's + strict (refetch_total) | 20 | 7.00 | 3.00 / 4,473 | — | — | -0.59 / -1,801 |
| K1's + strict (refetch_total) | 100 | 7.00 | 3.00 / 4,473 | — | — | — |
| K1's + strict (refetch_total) | rest | 7.00 | 3.00 / 4,473 | — | — | — |
| K1's + strict + loose | 20 | 7.00 | 6.00 / 6,186 | — | — | +1.71 / -702 |
| K1's + strict + loose | 100 | 7.00 | 6.00 / 6,186 | — | — | — |
| K1's + strict + loose | rest | 7.00 | 6.00 / 6,186 | — | — | — |

#### The miss

| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 7.0 | 15.0 | 0.0 | 0 / 0 | — | 116.0 | 0 | — |
| 20-99 | 1 | 0.0 | 0.0 | 0.0 | 0 / 0 | — | 0.0 | 0 | — |
| 100 | 1 | 7.0 | 15.0 | 0.0 | 0 / 0 | — | 116.0 | 0 | — |
| rest | 1 | 7.0 | 15.0 | 0.0 | 0 / 0 | — | 116.0 | 0 | — |

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

- Growth per request by position since the segment start: 0-19 6,926 (26 steps); 20-99 3,924 (80 steps); 100+ 2,966 (85 steps).
- Actual usage of the 193 included requests: cache reads 88,712,617, cache writes 857,205, mean context 464,094.
- Position-aware calibration: scale 1.000000; compactions at 785,000: 1 (target 1; unscaled 1).

| X | flat: compactions | mean fill | cache reads | cache writes | position-aware: compactions (unscaled) | mean fill | cache reads | cache writes |
|---|---|---|---|---|---|---|---|---|
| 300,000 | 3 | 189,966 | 35,581,940 | 1,081,514 | 4 (4) | 197,008 | 36,620,587 | 1,401,896 |
| 400,000 | 2 | 241,767 | 45,658,063 | 1,002,989 | 2 (2) | 257,082 | 48,449,693 | 1,167,048 |
| 500,000 | 1 | 268,730 | 50,943,460 | 921,514 | 2 (2) | 293,422 | 55,535,734 | 1,094,750 |
| 600,000 | 1 | 313,974 | 59,678,017 | 918,981 | 1 (1) | 335,179 | 63,692,446 | 997,109 |
| 700,000 | 1 | 396,256 | 75,564,306 | 913,135 | 1 (1) | 405,714 | 77,300,666 | 1,002,197 |
| 785,000 | 1 | 458,854 | 87,636,825 | 922,025 | 1 (1) | 458,909 | 87,646,182 | 923,245 |

At 785,000 against the actual usage: flat cache reads -1.2%, writes +7.6%, mean fill -1.1%; position-aware cache reads -1.2%, writes +7.7%, mean fill -1.1%.

The corrected loss (refetch_total, K1's shapes with writes out plus the strict set): the modeled compactions times the excess per boundary; calls / tokens.

| X | model | N=20 over C1 | over C2 | over C5 | N=100 over C1 | over C2 | over C5 |
|---|---|---|---|---|---|---|---|
| 300,000 | flat | — | — | -2 / -5,404 | — | — | — |
| 400,000 | flat | — | — | -1 / -3,603 | — | — | — |
| 500,000 | flat | — | — | -1 / -1,801 | — | — | — |
| 600,000 | flat | — | — | -1 / -1,801 | — | — | — |
| 700,000 | flat | — | — | -1 / -1,801 | — | — | — |
| 785,000 | flat | — | — | -1 / -1,801 | — | — | — |
| 300,000 | position-aware | — | — | -2 / -7,205 | — | — | — |
| 400,000 | position-aware | — | — | -1 / -3,603 | — | — | — |
| 500,000 | position-aware | — | — | -1 / -3,603 | — | — | — |
| 600,000 | position-aware | — | — | -1 / -1,801 | — | — | — |
| 700,000 | position-aware | — | — | -1 / -1,801 | — | — | — |
| 785,000 | position-aware | — | — | -1 / -1,801 | — | — | — |

## Run `sub-ac753871198ee8cfd`: agent-ac753871198ee8cfd.jsonl pinned at 9,748,808 bytes (sidechain thread)

- Requests 425; segments with requests 3; boundaries on the thread 2; skipped boundaries 0; control points: C1 1, C2 1, C5 9; items after a segment's last request kept for C2 14; models {'claude-opus-5-5': 425}.

### R-C, class `1M_window`: 2 boundaries; control points C1 1, C2 1, C5 9

- Removed per boundary (modeled, mean): 437,042 tokens; last context before (mean) 778,574; kept start per boundary (modeled, mean) 38,343; first context after (mean) 77,870; postTokens (mean) 16,644.

#### Re-fetch calls per 100 requests: the control's rate, then the excess

| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |
|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 37.50 (2; 40) | 5.00: +32.50 | 5.00: +32.50 | 11.11: +26.39 |
| K1's shapes, writes out | 20-99 | 8.24 (2; 85) | 5.00: +3.24 | 6.25: +1.99 | 5.00: +3.24 |
| K1's shapes, writes out | 100 | 17.60 (2; 125) | 5.00: +12.60 | 6.00: +11.60 | 5.00: +12.60 |
| K1's shapes, writes out | rest | 12.07 (2; 232) | 4.81: +7.26 | 6.00: +6.07 | — |
| strict shapes | 20 | 27.50 (2; 40) | 5.00: +22.50 | 5.00: +22.50 | 4.44: +23.06 |
| strict shapes | 20-99 | 5.88 (2; 85) | 6.25: -0.37 | 6.25: -0.37 | 7.50: -1.62 |
| strict shapes | 100 | 12.80 (2; 125) | 6.00: +6.80 | 6.00: +6.80 | 6.00: +6.80 |
| strict shapes | rest | 9.91 (2; 232) | 5.77: +4.14 | 6.00: +3.91 | — |
| K1's + strict (refetch_total) | 20 | 65.00 (2; 40) | 10.00: +55.00 | 10.00: +55.00 | 15.56: +49.44 |
| K1's + strict (refetch_total) | 20-99 | 14.12 (2; 85) | 11.25: +2.87 | 12.50: +1.62 | 12.50: +1.62 |
| K1's + strict (refetch_total) | 100 | 30.40 (2; 125) | 11.00: +19.40 | 12.00: +18.40 | 11.00: +19.40 |
| K1's + strict (refetch_total) | rest | 21.98 (2; 232) | 10.58: +11.41 | 12.00: +9.98 | — |
| loose shapes alone | 20 | 10.00 (2; 40) | 40.00: -30.00 | 30.00: -20.00 | 20.00: -10.00 |
| loose shapes alone | 20-99 | 11.76 (2; 85) | 12.50: -0.74 | 13.75: -1.99 | 12.50: -0.74 |
| loose shapes alone | 100 | 11.20 (2; 125) | 18.00: -6.80 | 17.00: -5.80 | 18.00: -6.80 |
| loose shapes alone | rest | 13.79 (2; 232) | 18.27: -4.48 | 17.00: -3.21 | — |
| K1's + strict + loose | 20 | 75.00 (2; 40) | 50.00: +25.00 | 40.00: +35.00 | 35.56: +39.44 |
| K1's + strict + loose | 20-99 | 25.88 (2; 85) | 23.75: +2.13 | 26.25: -0.37 | 25.00: +0.88 |
| K1's + strict + loose | 100 | 41.60 (2; 125) | 29.00: +12.60 | 29.00: +12.60 | 29.00: +12.60 |
| K1's + strict + loose | rest | 35.78 (2; 232) | 28.85: +6.93 | 29.00: +6.78 | — |

#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)

| shape set | window | real mean requests per boundary | real calls / tokens per boundary | excess over C1: calls / tokens per boundary | over C2 | over C5 |
|---|---|---|---|---|---|---|
| K1's + strict (refetch_total) | 20 | 20.00 | 13.00 / 38,232 | +11.00 / +23,024 | +11.00 / +23,024 | +9.89 / +31,420 |
| K1's + strict (refetch_total) | 20-99 | 42.50 | 6.00 / 5,921 | +1.22 / -555 | +0.69 / -6,530 | +0.69 / -729 |
| K1's + strict (refetch_total) | 100 | 62.50 | 19.00 / 44,153 | +12.12 / +27,030 | +11.50 / +20,000 | +12.12 / +27,030 |
| K1's + strict (refetch_total) | rest | 116.00 | 25.50 / 58,546 | +13.23 / +27,988 | +11.58 / +13,718 | — |
| K1's + strict + loose | 20 | 20.00 | 15.00 / 39,788 | +5.00 / +19,574 | +7.00 / +20,368 | +7.89 / +30,508 |
| K1's + strict + loose | 20-99 | 42.50 | 11.00 / 10,754 | +0.91 / +864 | -0.16 / -5,988 | +0.38 / +689 |
| K1's + strict + loose | 100 | 62.50 | 26.00 / 50,543 | +7.88 / +26,273 | +7.88 / +18,708 | +7.88 / +26,273 |
| K1's + strict + loose | rest | 116.00 | 41.50 / 70,985 | +8.04 / +25,833 | +7.86 / +11,900 | — |

#### The miss

| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 2 | 20.0 | 27.0 | 3.5 | 1 / 1 | 28.57% | 88.0 | 1 | 476.0 |
| 20-99 | 2 | 42.5 | 139.5 | 15.0 | 0 / 0 | 0.00% | 301.5 | 1 | 664.0 |
| 100 | 2 | 62.5 | 159.5 | 18.0 | 1 / 1 | 5.56% | 353.5 | 1 | 881.0 |
| rest | 2 | 116.0 | 272.5 | 28.0 | 1 / 1 | 3.57% | 528.5 | 1 | 884.0 |

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

- Growth per request by position since the segment start: 0-19 5,690 (60 steps); 20-99 3,473 (164 steps); 100+ 3,191 (198 steps).
- Actual usage of the 425 included requests: cache reads 185,317,067, cache writes 3,455,755, mean context 444,173.
- Position-aware calibration: scale 1.000000; compactions at 785,000: 2 (target 2; unscaled 2).

| X | flat: compactions | mean fill | cache reads | cache writes | position-aware: compactions (unscaled) | mean fill | cache reads | cache writes |
|---|---|---|---|---|---|---|---|---|
| 300,000 | 6 | 193,601 | 80,281,372 | 1,998,923 | 7 (7) | 188,261 | 77,663,666 | 2,347,171 |
| 400,000 | 4 | 221,108 | 92,066,203 | 1,904,782 | 5 (5) | 240,487 | 100,054,269 | 2,152,784 |
| 500,000 | 3 | 255,244 | 106,629,323 | 1,849,355 | 3 (3) | 274,445 | 114,746,548 | 1,892,437 |
| 600,000 | 2 | 361,156 | 151,736,670 | 1,754,501 | 2 (2) | 378,914 | 159,261,781 | 1,776,522 |
| 700,000 | 2 | 355,527 | 149,327,420 | 1,771,410 | 2 (2) | 368,789 | 154,963,856 | 1,771,415 |
| 785,000 | 2 | 444,774 | 187,276,935 | 1,751,944 | 2 (2) | 446,098 | 187,825,830 | 1,765,954 |

At 785,000 against the actual usage: flat cache reads +1.1%, writes -49.3%, mean fill +0.1%; position-aware cache reads +1.4%, writes -48.9%, mean fill +0.4%.

The corrected loss (refetch_total, K1's shapes with writes out plus the strict set): the modeled compactions times the excess per boundary; calls / tokens.

| X | model | N=20 over C1 | over C2 | over C5 | N=100 over C1 | over C2 | over C5 |
|---|---|---|---|---|---|---|---|
| 300,000 | flat | 66 / 138,145 | 66 / 138,145 | 59 / 188,523 | 73 / 162,178 | 69 / 119,998 | 73 / 162,178 |
| 400,000 | flat | 44 / 92,096 | 44 / 92,096 | 40 / 125,682 | 48 / 108,119 | 46 / 79,999 | 48 / 108,119 |
| 500,000 | flat | 33 / 69,072 | 33 / 69,072 | 30 / 94,262 | 36 / 81,089 | 34 / 59,999 | 36 / 81,089 |
| 600,000 | flat | 22 / 46,048 | 22 / 46,048 | 20 / 62,841 | 24 / 54,059 | 23 / 39,999 | 24 / 54,059 |
| 700,000 | flat | 22 / 46,048 | 22 / 46,048 | 20 / 62,841 | 24 / 54,059 | 23 / 39,999 | 24 / 54,059 |
| 785,000 | flat | 22 / 46,048 | 22 / 46,048 | 20 / 62,841 | 24 / 54,059 | 23 / 39,999 | 24 / 54,059 |
| 300,000 | position-aware | 77 / 161,169 | 77 / 161,169 | 69 / 219,944 | 85 / 189,208 | 80 / 139,998 | 85 / 189,208 |
| 400,000 | position-aware | 55 / 115,120 | 55 / 115,120 | 49 / 157,102 | 61 / 135,148 | 58 / 99,998 | 61 / 135,148 |
| 500,000 | position-aware | 33 / 69,072 | 33 / 69,072 | 30 / 94,262 | 36 / 81,089 | 34 / 59,999 | 36 / 81,089 |
| 600,000 | position-aware | 22 / 46,048 | 22 / 46,048 | 20 / 62,841 | 24 / 54,059 | 23 / 39,999 | 24 / 54,059 |
| 700,000 | position-aware | 22 / 46,048 | 22 / 46,048 | 20 / 62,841 | 24 / 54,059 | 23 / 39,999 | 24 / 54,059 |
| 785,000 | position-aware | 22 / 46,048 | 22 / 46,048 | 20 / 62,841 | 24 / 54,059 | 23 / 39,999 | 24 / 54,059 |

## Run `sub-ac9c149483559ffec`: agent-ac9c149483559ffec.jsonl pinned at 5,663,224 bytes (sidechain thread)

- Requests 210; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; control points: C1 0, C2 0, C5 2; items after a segment's last request kept for C2 6; models {'claude-opus-5-5': 210}.

### R-C, class `1M_window`: 1 boundaries; control points C1 0, C2 0, C5 2

- Removed per boundary (modeled, mean): 726,933 tokens; last context before (mean) 783,019; kept start per boundary (modeled, mean) 57,847; first context after (mean) 101,421; postTokens (mean) 19,649.

#### Re-fetch calls per 100 requests: the control's rate, then the excess

| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |
|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 30.00 (1; 20) | — | — | 0.00: +30.00 |
| K1's shapes, writes out | 20-99 | 21.43 (1; 42) | — | — | — |
| K1's shapes, writes out | 100 | 24.19 (1; 62) | — | — | — |
| K1's shapes, writes out | rest | 24.19 (1; 62) | — | — | — |
| strict shapes | 20 | 15.00 (1; 20) | — | — | 2.50: +12.50 |
| strict shapes | 20-99 | 19.05 (1; 42) | — | — | — |
| strict shapes | 100 | 17.74 (1; 62) | — | — | — |
| strict shapes | rest | 17.74 (1; 62) | — | — | — |
| K1's + strict (refetch_total) | 20 | 45.00 (1; 20) | — | — | 2.50: +42.50 |
| K1's + strict (refetch_total) | 20-99 | 40.48 (1; 42) | — | — | — |
| K1's + strict (refetch_total) | 100 | 41.94 (1; 62) | — | — | — |
| K1's + strict (refetch_total) | rest | 41.94 (1; 62) | — | — | — |
| loose shapes alone | 20 | 25.00 (1; 20) | — | — | 7.50: +17.50 |
| loose shapes alone | 20-99 | 14.29 (1; 42) | — | — | — |
| loose shapes alone | 100 | 17.74 (1; 62) | — | — | — |
| loose shapes alone | rest | 17.74 (1; 62) | — | — | — |
| K1's + strict + loose | 20 | 70.00 (1; 20) | — | — | 10.00: +60.00 |
| K1's + strict + loose | 20-99 | 54.76 (1; 42) | — | — | — |
| K1's + strict + loose | 100 | 59.68 (1; 62) | — | — | — |
| K1's + strict + loose | rest | 59.68 (1; 62) | — | — | — |

#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)

| shape set | window | real mean requests per boundary | real calls / tokens per boundary | excess over C1: calls / tokens per boundary | over C2 | over C5 |
|---|---|---|---|---|---|---|
| K1's + strict (refetch_total) | 20 | 20.00 | 9.00 / 34,931 | — | — | +8.50 / +34,119 |
| K1's + strict (refetch_total) | 20-99 | 42.00 | 17.00 / 22,970 | — | — | — |
| K1's + strict (refetch_total) | 100 | 62.00 | 26.00 / 57,901 | — | — | — |
| K1's + strict (refetch_total) | rest | 62.00 | 26.00 / 57,901 | — | — | — |
| K1's + strict + loose | 20 | 20.00 | 14.00 / 38,724 | — | — | +12.00 / +36,167 |
| K1's + strict + loose | 20-99 | 42.00 | 23.00 / 28,738 | — | — | — |
| K1's + strict + loose | 100 | 62.00 | 37.00 / 67,461 | — | — | — |
| K1's + strict + loose | rest | 62.00 | 37.00 / 67,461 | — | — | — |

#### The miss

| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 20.0 | 33.0 | 14.0 | 1 / 1 | 14.29% | 99.0 | 0 | — |
| 20-99 | 1 | 42.0 | 205.0 | 31.0 | 2 / 1 | 9.68% | 615.0 | 0 | — |
| 100 | 1 | 62.0 | 220.0 | 37.0 | 2 / 1 | 8.11% | 640.0 | 0 | — |
| rest | 1 | 62.0 | 220.0 | 37.0 | 2 / 1 | 8.11% | 640.0 | 0 | — |

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

- Growth per request by position since the segment start: 0-19 7,104 (40 steps); 20-99 4,170 (121 steps); 100+ 2,713 (47 steps).
- Actual usage of the 210 included requests: cache reads 86,289,663, cache writes 3,004,822, mean context 425,214.
- Position-aware calibration: scale 1.000000; compactions at 785,000: 1 (target 1; unscaled 1).

| X | flat: compactions | mean fill | cache reads | cache writes | position-aware: compactions (unscaled) | mean fill | cache reads | cache writes |
|---|---|---|---|---|---|---|---|---|
| 300,000 | 4 | 189,282 | 38,340,178 | 1,409,111 | 5 (5) | 205,620 | 41,422,132 | 1,758,063 |
| 400,000 | 2 | 264,731 | 54,424,831 | 1,168,726 | 3 (3) | 259,945 | 53,116,521 | 1,471,842 |
| 500,000 | 2 | 271,831 | 55,870,969 | 1,213,510 | 2 (2) | 299,308 | 61,502,177 | 1,352,615 |
| 600,000 | 1 | 338,895 | 70,051,506 | 1,116,517 | 1 (1) | 384,940 | 79,661,861 | 1,175,608 |
| 700,000 | 1 | 363,006 | 75,118,271 | 1,113,018 | 1 (1) | 399,063 | 82,617,505 | 1,185,686 |
| 785,000 | 1 | 414,312 | 85,889,849 | 1,115,714 | 1 (1) | 418,534 | 86,765,420 | 1,126,614 |

At 785,000 against the actual usage: flat cache reads -0.5%, writes -62.9%, mean fill -2.6%; position-aware cache reads +0.6%, writes -62.5%, mean fill -1.6%.

The corrected loss (refetch_total, K1's shapes with writes out plus the strict set): the modeled compactions times the excess per boundary; calls / tokens.

| X | model | N=20 over C1 | over C2 | over C5 | N=100 over C1 | over C2 | over C5 |
|---|---|---|---|---|---|---|---|
| 300,000 | flat | — | — | 34 / 136,477 | — | — | — |
| 400,000 | flat | — | — | 17 / 68,238 | — | — | — |
| 500,000 | flat | — | — | 17 / 68,238 | — | — | — |
| 600,000 | flat | — | — | 8 / 34,119 | — | — | — |
| 700,000 | flat | — | — | 8 / 34,119 | — | — | — |
| 785,000 | flat | — | — | 8 / 34,119 | — | — | — |
| 300,000 | position-aware | — | — | 42 / 170,596 | — | — | — |
| 400,000 | position-aware | — | — | 26 / 102,358 | — | — | — |
| 500,000 | position-aware | — | — | 17 / 68,238 | — | — | — |
| 600,000 | position-aware | — | — | 8 / 34,119 | — | — | — |
| 700,000 | position-aware | — | — | 8 / 34,119 | — | — | — |
| 785,000 | position-aware | — | — | 8 / 34,119 | — | — | — |

## Run `sub-acc9cf211b3e34071`: agent-acc9cf211b3e34071.jsonl pinned at 5,654,864 bytes (sidechain thread)

- Requests 223; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; control points: C1 0, C2 0, C5 1; items after a segment's last request kept for C2 5; models {'claude-opus-5-5': 223}.

### R-C, class `1M_window`: 1 boundaries; control points C1 0, C2 0, C5 1

- Removed per boundary (modeled, mean): 701,128 tokens; last context before (mean) 782,891; kept start per boundary (modeled, mean) 56,130; first context after (mean) 102,046; postTokens (mean) 17,631.

#### Re-fetch calls per 100 requests: the control's rate, then the excess

| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |
|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 50.00 (1; 20) | — | — | 45.00: +5.00 |
| K1's shapes, writes out | 20-99 | 25.00 (1; 64) | — | — | — |
| K1's shapes, writes out | 100 | 30.95 (1; 84) | — | — | — |
| K1's shapes, writes out | rest | 30.95 (1; 84) | — | — | — |
| strict shapes | 20 | 15.00 (1; 20) | — | — | 0.00: +15.00 |
| strict shapes | 20-99 | 12.50 (1; 64) | — | — | — |
| strict shapes | 100 | 13.10 (1; 84) | — | — | — |
| strict shapes | rest | 13.10 (1; 84) | — | — | — |
| K1's + strict (refetch_total) | 20 | 65.00 (1; 20) | — | — | 45.00: +20.00 |
| K1's + strict (refetch_total) | 20-99 | 37.50 (1; 64) | — | — | — |
| K1's + strict (refetch_total) | 100 | 44.05 (1; 84) | — | — | — |
| K1's + strict (refetch_total) | rest | 44.05 (1; 84) | — | — | — |
| loose shapes alone | 20 | 10.00 (1; 20) | — | — | 10.00: +0.00 |
| loose shapes alone | 20-99 | 12.50 (1; 64) | — | — | — |
| loose shapes alone | 100 | 11.90 (1; 84) | — | — | — |
| loose shapes alone | rest | 11.90 (1; 84) | — | — | — |
| K1's + strict + loose | 20 | 75.00 (1; 20) | — | — | 55.00: +20.00 |
| K1's + strict + loose | 20-99 | 50.00 (1; 64) | — | — | — |
| K1's + strict + loose | 100 | 55.95 (1; 84) | — | — | — |
| K1's + strict + loose | rest | 55.95 (1; 84) | — | — | — |

#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)

| shape set | window | real mean requests per boundary | real calls / tokens per boundary | excess over C1: calls / tokens per boundary | over C2 | over C5 |
|---|---|---|---|---|---|---|
| K1's + strict (refetch_total) | 20 | 20.00 | 13.00 / 24,435 | — | — | +4.00 / +3,146 |
| K1's + strict (refetch_total) | 20-99 | 64.00 | 24.00 / 35,115 | — | — | — |
| K1's + strict (refetch_total) | 100 | 84.00 | 37.00 / 59,549 | — | — | — |
| K1's + strict (refetch_total) | rest | 84.00 | 37.00 / 59,549 | — | — | — |
| K1's + strict + loose | 20 | 20.00 | 15.00 / 26,027 | — | — | +4.00 / +2,097 |
| K1's + strict + loose | 20-99 | 64.00 | 32.00 / 40,794 | — | — | — |
| K1's + strict + loose | 100 | 84.00 | 47.00 / 66,822 | — | — | — |
| K1's + strict + loose | rest | 84.00 | 47.00 / 66,822 | — | — | — |

#### The miss

| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 20.0 | 51.0 | 8.0 | 0 / 0 | 0.00% | 161.0 | 0 | — |
| 20-99 | 1 | 64.0 | 240.0 | 20.0 | 0 / 2 | 10.00% | 553.0 | 0 | — |
| 100 | 1 | 84.0 | 268.0 | 24.0 | 0 / 2 | 8.33% | 604.0 | 0 | — |
| rest | 1 | 84.0 | 268.0 | 24.0 | 0 / 2 | 8.33% | 604.0 | 0 | — |

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

- Growth per request by position since the segment start: 0-19 5,496 (40 steps); 20-99 3,358 (143 steps); 100+ 6,075 (38 steps).
- Actual usage of the 223 included requests: cache reads 78,186,736, cache writes 3,812,083, mean context 367,710.
- Position-aware calibration: scale 1.000000; compactions at 785,000: 1 (target 1; unscaled 1).

| X | flat: compactions | mean fill | cache reads | cache writes | position-aware: compactions (unscaled) | mean fill | cache reads | cache writes |
|---|---|---|---|---|---|---|---|---|
| 300,000 | 4 | 196,168 | 42,347,177 | 1,398,207 | 4 (4) | 202,173 | 43,674,967 | 1,409,543 |
| 400,000 | 3 | 246,110 | 53,573,985 | 1,308,573 | 2 (2) | 249,340 | 54,449,076 | 1,153,752 |
| 500,000 | 2 | 297,524 | 65,121,215 | 1,226,714 | 2 (2) | 319,440 | 70,030,403 | 1,204,673 |
| 600,000 | 1 | 362,279 | 79,693,984 | 1,094,141 | 1 (1) | 338,337 | 74,371,401 | 1,077,657 |
| 700,000 | 1 | 350,258 | 76,982,081 | 1,125,456 | 1 (1) | 337,800 | 74,233,111 | 1,096,188 |
| 785,000 | 1 | 365,386 | 80,351,373 | 1,129,717 | 1 (1) | 362,708 | 79,762,810 | 1,121,066 |

At 785,000 against the actual usage: flat cache reads +2.8%, writes -70.4%, mean fill -0.6%; position-aware cache reads +2.0%, writes -70.6%, mean fill -1.4%.

The corrected loss (refetch_total, K1's shapes with writes out plus the strict set): the modeled compactions times the excess per boundary; calls / tokens.

| X | model | N=20 over C1 | over C2 | over C5 | N=100 over C1 | over C2 | over C5 |
|---|---|---|---|---|---|---|---|
| 300,000 | flat | — | — | 16 / 12,584 | — | — | — |
| 400,000 | flat | — | — | 12 / 9,438 | — | — | — |
| 500,000 | flat | — | — | 8 / 6,292 | — | — | — |
| 600,000 | flat | — | — | 4 / 3,146 | — | — | — |
| 700,000 | flat | — | — | 4 / 3,146 | — | — | — |
| 785,000 | flat | — | — | 4 / 3,146 | — | — | — |
| 300,000 | position-aware | — | — | 16 / 12,584 | — | — | — |
| 400,000 | position-aware | — | — | 8 / 6,292 | — | — | — |
| 500,000 | position-aware | — | — | 8 / 6,292 | — | — | — |
| 600,000 | position-aware | — | — | 4 / 3,146 | — | — | — |
| 700,000 | position-aware | — | — | 4 / 3,146 | — | — | — |
| 785,000 | position-aware | — | — | 4 / 3,146 | — | — | — |

## Run `sub-ae66dca0f21a920b6`: agent-ae66dca0f21a920b6.jsonl pinned at 3,861,913 bytes (sidechain thread)

- Requests 197; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; control points: C1 0, C2 0, C5 4; items after a segment's last request kept for C2 7; models {'claude-opus-5-5': 197}.

### R-C, class `1M_window`: 1 boundaries; control points C1 0, C2 0, C5 4

- Removed per boundary (modeled, mean): 546,407 tokens; last context before (mean) 771,483; kept start per boundary (modeled, mean) 40,730; first context after (mean) 81,324; postTokens (mean) 18,188.

#### Re-fetch calls per 100 requests: the control's rate, then the excess

| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |
|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 0.00 (1; 1) | — | — | 10.00: -10.00 |
| K1's shapes, writes out | 20-99 | — (0; 0) | — | — | — |
| K1's shapes, writes out | 100 | 0.00 (1; 1) | — | — | — |
| K1's shapes, writes out | rest | 0.00 (1; 1) | — | — | — |
| strict shapes | 20 | 0.00 (1; 1) | — | — | 18.75: -18.75 |
| strict shapes | 20-99 | — (0; 0) | — | — | — |
| strict shapes | 100 | 0.00 (1; 1) | — | — | — |
| strict shapes | rest | 0.00 (1; 1) | — | — | — |
| K1's + strict (refetch_total) | 20 | 0.00 (1; 1) | — | — | 28.75: -28.75 |
| K1's + strict (refetch_total) | 20-99 | — (0; 0) | — | — | — |
| K1's + strict (refetch_total) | 100 | 0.00 (1; 1) | — | — | — |
| K1's + strict (refetch_total) | rest | 0.00 (1; 1) | — | — | — |
| loose shapes alone | 20 | 0.00 (1; 1) | — | — | 23.75: -23.75 |
| loose shapes alone | 20-99 | — (0; 0) | — | — | — |
| loose shapes alone | 100 | 0.00 (1; 1) | — | — | — |
| loose shapes alone | rest | 0.00 (1; 1) | — | — | — |
| K1's + strict + loose | 20 | 0.00 (1; 1) | — | — | 52.50: -52.50 |
| K1's + strict + loose | 20-99 | — (0; 0) | — | — | — |
| K1's + strict + loose | 100 | 0.00 (1; 1) | — | — | — |
| K1's + strict + loose | rest | 0.00 (1; 1) | — | — | — |

#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)

| shape set | window | real mean requests per boundary | real calls / tokens per boundary | excess over C1: calls / tokens per boundary | over C2 | over C5 |
|---|---|---|---|---|---|---|
| K1's + strict (refetch_total) | 20 | 1.00 | 0.00 / 0 | — | — | -0.29 / -699 |
| K1's + strict (refetch_total) | 100 | 1.00 | 0.00 / 0 | — | — | — |
| K1's + strict (refetch_total) | rest | 1.00 | 0.00 / 0 | — | — | — |
| K1's + strict + loose | 20 | 1.00 | 0.00 / 0 | — | — | -0.53 / -993 |
| K1's + strict + loose | 100 | 1.00 | 0.00 / 0 | — | — | — |
| K1's + strict + loose | rest | 1.00 | 0.00 / 0 | — | — | — |

#### The miss

| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 1.0 | 0.0 | 0.0 | 0 / 0 | — | 0.0 | 0 | — |
| 20-99 | 1 | 0.0 | 0.0 | 0.0 | 0 / 0 | — | 0.0 | 0 | — |
| 100 | 1 | 1.0 | 0.0 | 0.0 | 0 / 0 | — | 0.0 | 0 | — |
| rest | 1 | 1.0 | 0.0 | 0.0 | 0 / 0 | — | 0.0 | 0 | — |

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

- Growth per request by position since the segment start: 0-19 6,510 (20 steps); 20-99 4,057 (80 steps); 100+ 2,625 (95 steps).
- Actual usage of the 197 included requests: cache reads 95,566,232, cache writes 790,874, mean context 489,124.
- Position-aware calibration: scale 1.000000; compactions at 785,000: 1 (target 1; unscaled 1).

| X | flat: compactions | mean fill | cache reads | cache writes | position-aware: compactions (unscaled) | mean fill | cache reads | cache writes |
|---|---|---|---|---|---|---|---|---|
| 300,000 | 3 | 195,568 | 37,517,051 | 1,009,826 | 4 (4) | 193,957 | 36,794,307 | 1,415,206 |
| 400,000 | 2 | 232,699 | 44,906,118 | 935,501 | 2 (2) | 232,792 | 44,717,810 | 1,142,184 |
| 500,000 | 1 | 278,243 | 53,954,283 | 859,503 | 2 (2) | 323,211 | 62,511,186 | 1,161,310 |
| 600,000 | 1 | 313,732 | 60,940,206 | 864,901 | 1 (1) | 348,108 | 67,558,800 | 1,018,581 |
| 700,000 | 1 | 415,048 | 80,901,720 | 862,835 | 1 (1) | 421,089 | 82,012,651 | 941,869 |
| 785,000 | 1 | 499,484 | 97,548,467 | 849,849 | 1 (1) | 499,484 | 97,548,467 | 849,849 |

At 785,000 against the actual usage: flat cache reads +2.1%, writes +7.5%, mean fill +2.1%; position-aware cache reads +2.1%, writes +7.5%, mean fill +2.1%.

The corrected loss (refetch_total, K1's shapes with writes out plus the strict set): the modeled compactions times the excess per boundary; calls / tokens.

| X | model | N=20 over C1 | over C2 | over C5 | N=100 over C1 | over C2 | over C5 |
|---|---|---|---|---|---|---|---|
| 300,000 | flat | — | — | -1 / -2,098 | — | — | — |
| 400,000 | flat | — | — | -1 / -1,399 | — | — | — |
| 500,000 | flat | — | — | -0 / -699 | — | — | — |
| 600,000 | flat | — | — | -0 / -699 | — | — | — |
| 700,000 | flat | — | — | -0 / -699 | — | — | — |
| 785,000 | flat | — | — | -0 / -699 | — | — | — |
| 300,000 | position-aware | — | — | -1 / -2,797 | — | — | — |
| 400,000 | position-aware | — | — | -1 / -1,399 | — | — | — |
| 500,000 | position-aware | — | — | -1 / -1,399 | — | — | — |
| 600,000 | position-aware | — | — | -0 / -699 | — | — | — |
| 700,000 | position-aware | — | — | -0 / -699 | — | — | — |
| 785,000 | position-aware | — | — | -0 / -699 | — | — | — |

## Run `sub-af25a8ffadcb62c75`: agent-af25a8ffadcb62c75.jsonl pinned at 6,606,908 bytes (sidechain thread)

- Requests 239; segments with requests 2; boundaries on the thread 1; skipped boundaries 0; control points: C1 0, C2 0, C5 1; items after a segment's last request kept for C2 7; models {'claude-opus-5-5': 239}.

### R-C, class `1M_window`: 1 boundaries; control points C1 0, C2 0, C5 1

- Removed per boundary (modeled, mean): 458,166 tokens; last context before (mean) 782,657; kept start per boundary (modeled, mean) 39,176; first context after (mean) 79,382; postTokens (mean) 17,218.

#### Re-fetch calls per 100 requests: the control's rate, then the excess

| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |
|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 40.00 (1; 20) | — | — | 15.00: +25.00 |
| K1's shapes, writes out | 20-99 | 21.25 (1; 80) | — | — | — |
| K1's shapes, writes out | 100 | 25.00 (1; 100) | — | — | — |
| K1's shapes, writes out | rest | 24.79 (1; 117) | — | — | — |
| strict shapes | 20 | 0.00 (1; 20) | — | — | 10.00: -10.00 |
| strict shapes | 20-99 | 3.75 (1; 80) | — | — | — |
| strict shapes | 100 | 3.00 (1; 100) | — | — | — |
| strict shapes | rest | 3.42 (1; 117) | — | — | — |
| K1's + strict (refetch_total) | 20 | 40.00 (1; 20) | — | — | 25.00: +15.00 |
| K1's + strict (refetch_total) | 20-99 | 25.00 (1; 80) | — | — | — |
| K1's + strict (refetch_total) | 100 | 28.00 (1; 100) | — | — | — |
| K1's + strict (refetch_total) | rest | 28.21 (1; 117) | — | — | — |
| loose shapes alone | 20 | 10.00 (1; 20) | — | — | 20.00: -10.00 |
| loose shapes alone | 20-99 | 16.25 (1; 80) | — | — | — |
| loose shapes alone | 100 | 15.00 (1; 100) | — | — | — |
| loose shapes alone | rest | 14.53 (1; 117) | — | — | — |
| K1's + strict + loose | 20 | 50.00 (1; 20) | — | — | 45.00: +5.00 |
| K1's + strict + loose | 20-99 | 41.25 (1; 80) | — | — | — |
| K1's + strict + loose | 100 | 43.00 (1; 100) | — | — | — |
| K1's + strict + loose | rest | 42.74 (1; 117) | — | — | — |

#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)

| shape set | window | real mean requests per boundary | real calls / tokens per boundary | excess over C1: calls / tokens per boundary | over C2 | over C5 |
|---|---|---|---|---|---|---|
| K1's + strict (refetch_total) | 20 | 20.00 | 8.00 / 47,177 | — | — | +3.00 / +39,006 |
| K1's + strict (refetch_total) | 20-99 | 80.00 | 20.00 / 17,820 | — | — | — |
| K1's + strict (refetch_total) | 100 | 100.00 | 28.00 / 64,998 | — | — | — |
| K1's + strict (refetch_total) | rest | 117.00 | 33.00 / 69,450 | — | — | — |
| K1's + strict + loose | 20 | 20.00 | 10.00 / 48,359 | — | — | +1.00 / +38,400 |
| K1's + strict + loose | 20-99 | 80.00 | 33.00 / 25,769 | — | — | — |
| K1's + strict + loose | 100 | 100.00 | 43.00 / 74,128 | — | — | — |
| K1's + strict + loose | rest | 117.00 | 50.00 / 80,132 | — | — | — |

#### The miss

| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 1 | 20.0 | 58.0 | 6.0 | 0 / 1 | 16.67% | 165.0 | 0 | — |
| 20-99 | 1 | 80.0 | 240.0 | 17.0 | 1 / 1 | 11.76% | 495.0 | 0 | — |
| 100 | 1 | 100.0 | 273.0 | 20.0 | 1 / 1 | 10.00% | 551.0 | 0 | — |
| rest | 1 | 117.0 | 680.0 | 21.0 | 1 / 1 | 9.52% | 1,073.0 | 0 | — |

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

- Growth per request by position since the segment start: 0-19 7,319 (40 steps); 20-99 4,001 (160 steps); 100+ 5,436 (37 steps).
- Actual usage of the 239 included requests: cache reads 90,521,499, cache writes 3,692,230, mean context 394,202.
- Position-aware calibration: scale 1.000000; compactions at 785,000: 1 (target 1; unscaled 1).

| X | flat: compactions | mean fill | cache reads | cache writes | position-aware: compactions (unscaled) | mean fill | cache reads | cache writes |
|---|---|---|---|---|---|---|---|---|
| 300,000 | 5 | 180,438 | 41,587,633 | 1,537,026 | 6 (6) | 188,702 | 43,242,203 | 1,857,549 |
| 400,000 | 3 | 213,511 | 49,627,488 | 1,401,672 | 3 (3) | 231,691 | 53,983,294 | 1,390,768 |
| 500,000 | 2 | 259,694 | 60,717,147 | 1,349,596 | 2 (2) | 270,864 | 63,426,036 | 1,310,432 |
| 600,000 | 2 | 363,622 | 85,538,086 | 1,367,675 | 2 (2) | 362,130 | 85,133,404 | 1,415,663 |
| 700,000 | 1 | 386,109 | 91,045,142 | 1,234,881 | 1 (1) | 378,002 | 89,114,960 | 1,227,523 |
| 785,000 | 1 | 398,438 | 93,941,971 | 1,284,832 | 1 (1) | 399,307 | 94,146,670 | 1,287,758 |

At 785,000 against the actual usage: flat cache reads +3.8%, writes -65.2%, mean fill +1.1%; position-aware cache reads +4.0%, writes -65.1%, mean fill +1.3%.

The corrected loss (refetch_total, K1's shapes with writes out plus the strict set): the modeled compactions times the excess per boundary; calls / tokens.

| X | model | N=20 over C1 | over C2 | over C5 | N=100 over C1 | over C2 | over C5 |
|---|---|---|---|---|---|---|---|
| 300,000 | flat | — | — | 15 / 195,028 | — | — | — |
| 400,000 | flat | — | — | 9 / 117,016 | — | — | — |
| 500,000 | flat | — | — | 6 / 78,011 | — | — | — |
| 600,000 | flat | — | — | 6 / 78,011 | — | — | — |
| 700,000 | flat | — | — | 3 / 39,006 | — | — | — |
| 785,000 | flat | — | — | 3 / 39,006 | — | — | — |
| 300,000 | position-aware | — | — | 18 / 234,033 | — | — | — |
| 400,000 | position-aware | — | — | 9 / 117,016 | — | — | — |
| 500,000 | position-aware | — | — | 6 / 78,011 | — | — | — |
| 600,000 | position-aware | — | — | 6 / 78,011 | — | — | — |
| 700,000 | position-aware | — | — | 3 / 39,006 | — | — | — |
| 785,000 | position-aware | — | — | 3 / 39,006 | — | — | — |

## Subagent files pooled: 16 files, 21 boundaries; control points C1 7, C2 7, C5 85 (every class)

#### Re-fetch calls per 100 requests: the control's rate, then the excess and its 95% bootstrap interval

| shape set | window | real (boundaries; requests) | C1 | C2 | C5 |
|---|---|---|---|---|---|
| K1's shapes, writes out | 20 | 32.15 (21; 339) | 11.43: +20.72 [+8.55, +32.45] | 12.14: +20.01 [+6.17, +32.43] | 12.88: +19.27 [+8.67, +29.70] |
| K1's shapes, writes out | 20-99 | 19.86 (16; 1,108) | 7.32: +12.53 [+3.79, +20.17] | 7.14: +12.71 [+5.48, +20.12] | 8.33: +11.52 [+1.25, +20.10] |
| K1's shapes, writes out | 100 | 22.74 (21; 1,447) | 8.14: +14.59 [+6.42, +22.14] | 8.14: +14.59 [+6.59, +21.93] | 9.07: +13.67 [+2.06, +22.89] |
| K1's shapes, writes out | rest | 19.61 (21; 2,285) | 8.43: +11.18 [+2.65, +19.92] | 8.14: +11.46 [+3.05, +20.04] | — |
| strict shapes | 20 | 18.29 (21; 339) | 7.14: +11.15 [+1.58, +21.06] | 10.71: +7.57 [-6.52, +20.48] | 11.76: +6.52 [-2.20, +15.52] |
| strict shapes | 20-99 | 12.27 (16; 1,108) | 9.82: +2.45 [-4.98, +10.25] | 8.57: +3.70 [-3.15, +10.57] | 11.17: +1.11 [-6.02, +9.99] |
| strict shapes | 100 | 13.68 (21; 1,447) | 9.29: +4.40 [-3.29, +12.12] | 9.00: +4.68 [-2.51, +12.33] | 10.87: +2.82 [-4.38, +11.51] |
| strict shapes | rest | 12.74 (21; 2,285) | 8.30: +4.43 [-2.50, +11.10] | 9.00: +3.74 [-3.62, +10.54] | — |
| K1's + strict (refetch_total) | 20 | 50.44 (21; 339) | 18.57: +31.87 [+19.27, +43.61] | 22.86: +27.59 [+13.82, +40.39] | 24.65: +25.80 [+15.38, +35.88] |
| K1's + strict (refetch_total) | 20-99 | 32.13 (16; 1,108) | 17.14: +14.99 [+9.81, +20.86] | 15.71: +16.42 [+11.71, +21.15] | 19.50: +12.63 [+7.58, +17.93] |
| K1's + strict (refetch_total) | 100 | 36.42 (21; 1,447) | 17.43: +18.99 [+13.64, +24.49] | 17.14: +19.28 [+13.93, +24.67] | 19.93: +16.49 [+11.58, +22.51] |
| K1's + strict (refetch_total) | rest | 32.34 (21; 2,285) | 16.73: +15.61 [+10.54, +21.75] | 17.14: +15.20 [+9.88, +21.16] | — |
| loose shapes alone | 20 | 12.68 (21; 339) | 22.86: -10.17 [-17.52, -3.33] | 17.14: -4.46 [-10.94, +1.90] | 15.88: -3.20 [-7.70, +1.54] |
| loose shapes alone | 20-99 | 17.15 (16; 1,108) | 12.68: +4.47 [+1.10, +7.86] | 12.86: +4.29 [+1.13, +7.73] | 13.67: +3.48 [+0.26, +7.29] |
| loose shapes alone | 100 | 16.10 (21; 1,447) | 14.71: +1.39 [-1.78, +4.92] | 13.71: +2.39 [-0.80, +5.92] | 15.13: +0.97 [-2.17, +4.41] |
| loose shapes alone | rest | 15.67 (21; 2,285) | 14.13: +1.54 [-0.97, +3.94] | 13.71: +1.95 [-1.02, +4.74] | — |
| K1's + strict + loose | 20 | 63.13 (21; 339) | 41.43: +21.70 [+10.79, +33.77] | 40.00: +23.13 [+12.32, +34.11] | 40.53: +22.60 [+14.66, +30.55] |
| K1's + strict + loose | 20-99 | 49.28 (16; 1,108) | 29.82: +19.46 [+12.37, +26.24] | 28.57: +20.71 [+13.78, +26.70] | 33.17: +16.11 [+10.26, +23.10] |
| K1's + strict + loose | 100 | 52.52 (21; 1,447) | 32.14: +20.38 [+14.25, +26.48] | 30.86: +21.67 [+15.43, +27.41] | 35.07: +17.46 [+13.29, +23.15] |
| K1's + strict + loose | rest | 48.01 (21; 2,285) | 30.86: +17.15 [+12.39, +22.96] | 30.86: +17.15 [+10.83, +22.98] | — |

#### Per boundary: the excess in calls and tokens (the rate's excess times the real window length)

| shape set | window | real mean requests per boundary | real calls / tokens per boundary | excess over C1: calls / tokens per boundary | over C2 | over C5 |
|---|---|---|---|---|---|---|
| K1's + strict (refetch_total) | 20 | 16.14 | 8.14 / 19,477 | +5.14 / +14,853 | +4.45 / +11,962 | +4.16 / +13,195 |
| K1's + strict (refetch_total) | 20-99 | 52.76 | 16.95 / 23,345 | +7.91 / +8,296 | +8.66 / +8,449 | +6.66 / +8,229 |
| K1's + strict (refetch_total) | 100 | 68.90 | 25.10 / 42,822 | +13.09 / +23,152 | +13.28 / +20,844 | +11.36 / +23,341 |
| K1's + strict (refetch_total) | rest | 108.81 | 35.19 / 56,158 | +16.99 / +25,681 | +16.54 / +21,452 | — |
| K1's + strict + loose | 20 | 16.14 | 10.19 / 21,272 | +3.50 / +14,422 | +3.73 / +11,080 | +3.65 / +13,131 |
| K1's + strict + loose | 20-99 | 52.76 | 26.00 / 30,319 | +10.27 / +10,954 | +10.93 / +11,058 | +8.50 / +10,463 |
| K1's + strict + loose | 100 | 68.90 | 36.19 / 51,591 | +14.04 / +25,512 | +14.93 / +22,767 | +12.03 / +24,961 |
| K1's + strict + loose | rest | 108.81 | 52.24 / 68,942 | +18.66 / +28,118 | +18.66 / +23,425 | — |

#### By shape and label, per 100 requests

| window | label | set | real | C1 | C2 | C5 |
|---|---|---|---|---|---|---|
| 20 | read_known_path | K1 | 5.60 | 0.00 | 2.86 | 2.29 |
| 20 | rerun_command | K1 | 0.00 | 0.00 | 0.00 | 0.35 |
| 20 | identical_other_call | K1 | 0.29 | 0.00 | 0.00 | 0.00 |
| 20 | search_transcript | K1 | 25.37 | 10.00 | 9.29 | 9.06 |
| 20 | search_ledger | K1 | 0.88 | 1.43 | 0.00 | 1.00 |
| 20 | search_live_state | K1 | 0.00 | 0.00 | 0.00 | 0.18 |
| 20 | bash_view_known_file | strict | 15.34 | 5.00 | 7.86 | 10.35 |
| 20 | read_bash_viewed_file | strict | 1.77 | 0.71 | 0.71 | 0.24 |
| 20 | git_repeated_args | strict | 1.18 | 1.43 | 2.14 | 1.18 |
| 20 | read_known_path_respelled | strict | 0.00 | 0.00 | 0.00 | 0.00 |
| 20 | grep_known_token | loose | 10.32 | 22.86 | 16.43 | 14.47 |
| 20 | git_any | loose | 2.36 | 0.00 | 0.71 | 1.41 |
| 20-99 | read_known_path | K1 | 2.44 | 1.96 | 1.79 | 1.58 |
| 20-99 | rerun_command | K1 | 0.00 | 0.00 | 0.00 | 0.00 |
| 20-99 | identical_other_call | K1 | 0.09 | 0.00 | 0.00 | 0.00 |
| 20-99 | search_transcript | K1 | 17.33 | 5.18 | 5.18 | 6.17 |
| 20-99 | search_ledger | K1 | 0.00 | 0.00 | 0.00 | 0.50 |
| 20-99 | search_live_state | K1 | 0.00 | 0.18 | 0.18 | 0.08 |
| 20-99 | bash_view_known_file | strict | 11.19 | 9.29 | 8.04 | 10.50 |
| 20-99 | read_bash_viewed_file | strict | 0.27 | 0.18 | 0.36 | 0.25 |
| 20-99 | git_repeated_args | strict | 0.81 | 0.36 | 0.18 | 0.42 |
| 20-99 | read_known_path_respelled | strict | 0.00 | 0.00 | 0.00 | 0.00 |
| 20-99 | grep_known_token | loose | 15.97 | 11.79 | 12.32 | 12.92 |
| 20-99 | git_any | loose | 1.17 | 0.89 | 0.54 | 0.75 |
| 100 | read_known_path | K1 | 3.18 | 1.57 | 2.00 | 1.40 |
| 100 | rerun_command | K1 | 0.00 | 0.00 | 0.00 | 0.07 |
| 100 | identical_other_call | K1 | 0.14 | 0.00 | 0.00 | 0.00 |
| 100 | search_transcript | K1 | 19.21 | 6.14 | 6.00 | 6.93 |
| 100 | search_ledger | K1 | 0.21 | 0.29 | 0.00 | 0.60 |
| 100 | search_live_state | K1 | 0.00 | 0.14 | 0.14 | 0.07 |
| 100 | bash_view_known_file | strict | 12.16 | 8.43 | 8.00 | 10.20 |
| 100 | read_bash_viewed_file | strict | 0.62 | 0.29 | 0.43 | 0.27 |
| 100 | git_repeated_args | strict | 0.90 | 0.57 | 0.57 | 0.40 |
| 100 | read_known_path_respelled | strict | 0.00 | 0.00 | 0.00 | 0.00 |
| 100 | grep_known_token | loose | 14.65 | 14.00 | 13.14 | 14.40 |
| 100 | git_any | loose | 1.45 | 0.71 | 0.57 | 0.73 |

#### The search shapes by direction, per 100 requests (`counted` = read + script + other)

| window | shape | direction | real | C1 | C2 | C5 |
|---|---|---|---|---|---|---|
| 20 | search_transcript | counted | 25.37 | 10.00 | 9.29 | 9.06 |
| 20 | search_transcript | read | 20.35 | 7.14 | 7.14 | 6.94 |
| 20 | search_transcript | script | 5.01 | 2.14 | 0.71 | 1.76 |
| 20 | search_transcript | other | 0.00 | 0.71 | 1.43 | 0.35 |
| 20 | search_transcript | write | 2.65 | 10.00 | 10.00 | 7.35 |
| 20 | search_transcript | commit | 0.00 | 0.00 | 0.00 | 0.00 |
| 20 | search_ledger | counted | 0.88 | 1.43 | 0.00 | 1.00 |
| 20 | search_ledger | read | 0.59 | 0.71 | 0.00 | 0.94 |
| 20 | search_ledger | script | 0.00 | 0.00 | 0.00 | 0.00 |
| 20 | search_ledger | other | 0.29 | 0.71 | 0.00 | 0.06 |
| 20 | search_ledger | write | 0.00 | 0.71 | 0.00 | 0.18 |
| 20 | search_ledger | commit | 0.00 | 0.00 | 0.00 | 0.00 |
| 20 | search_live_state | counted | 0.00 | 0.00 | 0.00 | 0.18 |
| 20 | search_live_state | read | 0.00 | 0.00 | 0.00 | 0.12 |
| 20 | search_live_state | script | 0.00 | 0.00 | 0.00 | 0.06 |
| 20 | search_live_state | other | 0.00 | 0.00 | 0.00 | 0.00 |
| 20 | search_live_state | write | 0.00 | 0.00 | 0.00 | 0.18 |
| 20 | search_live_state | commit | 0.00 | 0.00 | 0.00 | 0.00 |
| 100 | search_transcript | counted | 19.21 | 6.14 | 6.00 | 6.93 |
| 100 | search_transcript | read | 15.69 | 4.71 | 4.71 | 5.80 |
| 100 | search_transcript | script | 3.18 | 0.86 | 0.43 | 0.67 |
| 100 | search_transcript | other | 0.35 | 0.57 | 0.86 | 0.47 |
| 100 | search_transcript | write | 7.60 | 6.57 | 6.29 | 6.80 |
| 100 | search_transcript | commit | 0.00 | 0.00 | 0.00 | 0.00 |
| 100 | search_ledger | counted | 0.21 | 0.29 | 0.00 | 0.60 |
| 100 | search_ledger | read | 0.14 | 0.14 | 0.00 | 0.33 |
| 100 | search_ledger | script | 0.00 | 0.00 | 0.00 | 0.00 |
| 100 | search_ledger | other | 0.07 | 0.14 | 0.00 | 0.27 |
| 100 | search_ledger | write | 0.07 | 0.14 | 0.00 | 0.20 |
| 100 | search_ledger | commit | 0.00 | 0.00 | 0.00 | 0.00 |
| 100 | search_live_state | counted | 0.00 | 0.14 | 0.14 | 0.07 |
| 100 | search_live_state | read | 0.00 | 0.14 | 0.14 | 0.07 |
| 100 | search_live_state | script | 0.00 | 0.00 | 0.00 | 0.00 |
| 100 | search_live_state | other | 0.00 | 0.00 | 0.00 | 0.00 |
| 100 | search_live_state | write | 0.00 | 0.00 | 0.00 | 0.00 |
| 100 | search_live_state | commit | 0.00 | 0.00 | 0.00 | 0.00 |

#### The miss

| window | real boundaries | mean window requests | missed (mean) | missed paths (mean) | read / edited before (sum) | share of missed paths named before | reused (mean) | C1 points | C1 reused (mean) |
|---|---|---|---|---|---|---|---|---|---|
| 20 | 21 | 16.1 | 38.3 | 6.9 | 4 / 5 | 6.21% | 111.9 | 7 | 360.1 |
| 20-99 | 21 | 52.8 | 160.6 | 22.3 | 11 / 16 | 5.76% | 360.5 | 7 | 674.7 |
| 100 | 21 | 68.9 | 185.2 | 26.1 | 12 / 17 | 5.28% | 415.1 | 7 | 781.4 |
| rest | 21 | 108.8 | 303.3 | 35.0 | 12 / 24 | 4.89% | 591.1 | 7 | 798.4 |

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
- Position-aware variant: each observed step is scaled by g(its modeled bucket) / g(its observed bucket), g being the mean growth per request of the included segments' steps by position since the segment start (buckets 0-19, 20-99, 100 and later; a step, request i's context minus request i-1's, takes position i-1, the request whose output it adds: VERIFY-K1's convention; a bucket with no step takes the nearest earlier bucket's mean). The modeled position counts the requests since the stream's start or the last modeled compaction; the step across an observed compaction stays 0.
- Calibration: one scale on every step, found by bisection (CALIBRATION_STEPS halvings, the scale nearest 1) so that the position-aware count at the last X (785k) equals the observed compactions among the included segments; the unscaled count is reported beside it. The flat model is not rescaled.
- Actual usage: the included segments' requests' cache_read_input_tokens, cache_creation_input_tokens and mean context from their first usage records; the session ran at about 785k, so only that X has an actual to compare.
- The corrected loss per compaction: the excess per boundary of K1's shapes (writes out) plus the strict set (refetch_total), and with the loose set (with_loose_total), over each control: (the real rate - the control's rate) x the real mean requests per boundary, times the modeled compactions.

## Markers and rules

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

Searches (R-C re-fetch shapes; v2 counts a search's reads only):

- `search_ledger`: `BUILD-TASKLIST.md`
- `search_live_state`: `live-state.md`
- `search_transcript`: `.claude/projects/`; `/tasks/` and `.output`; `chat_tail.py`; `session_export.py`; `transcript_export.py`; `hiccup_scan.py`; `replay_transcript_edits.py`

- Strict labels: bash_view_known_file, read_bash_viewed_file, git_repeated_args, read_known_path_respelled. Loose labels: grep_known_token, git_any.
- Views: awk, cat, head, less, nl, sed, tail. Greps: egrep, fgrep, grep, rg and `graft ask`. Reads: awk, cat, cmp, cut, diff, du, egrep, fgrep, file, find, grep, head, jq, less, ls, md5sum, more, nl, od, readlink, realpath, rg, sed, sha256sum, sort, stat, strings, tac, tail, tree, uniq, wc, xxd; git blame, cat-file, describe, diff, grep, log, ls-files, merge-base, reflog, rev-parse, shortlog, show, status.
- C5: every 20 requests from request 100; bootstrap replicates 2000.

