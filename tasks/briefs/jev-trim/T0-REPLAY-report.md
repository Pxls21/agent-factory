<!-- Coordinator note (2026-09-29): the T0-REPLAY lane's hand-back, extracted verbatim from its transcript by `python3 scripts/stack.py harvest agent=af25a8ffadcb62c75` (run s-20260929T002019Z-ffa427; hand-back sha256 fee52ff11b20; 313 assistant records, all claude-opus-5-5, 0 refusal stops). The report of record for T0 (task #346). Two local commit ids were replaced by the commit's subject before the push (stale_ids). -->

# T0-REPLAY: context trimming replayed with plain rules (task #346, D-105)

**DONE, not committed.** This lane makes no git writes, so every file below is untracked. The replay tool, its 36 tests and eight outputs exist. The premise matched on all ten commands. The cross-check matches the audit: 09-26 is equal on all six fields; 09-28 is equal on five, and the sixth (the median) is equal once truncated to the audit's integer. Both gates passed twice on the final code, and all nine named mutants are killed.

**The numbers, briefly:**
- **Active context stays far above every budget.** With K=2 stop-hook turns protected, the policy never reaches L at any B from 100,000 to 200,000. The protected set alone passes B=200,000 in 63.7% of requests and B=250,000 in 40.7%.
- **Median active context** (main, B=200,000, A=20) is 332,932 with all four rules (between-turn), against a real median of 454,522.
- **Cache cost** runs from −2.9% to +190% of the real cost across cells.
- **Use-after-archive** is 6 at 20 and 17 at the horizon for R1 alone; for all four rules (A=10) it is 96–97 at 20 and 367–368 at the horizon, out of about 1,990 scored archived items.

As the brief asked, there is no design recommendation.

Stamps come from `date -u`: my start was 2026-09-28 22:59:41Z; the final outputs were written 2026-09-29 00:04:29Z to 00:06:58Z; the report was assembled at 00:12:43Z.

## 0. Not done

1. **No commit.** The lane rule forbids git writes. The files to commit are listed in §2.
2. **`scripts/report_lint.py` not run.** The harness refused the scratch write of the report text at 00:1xZ: "Subagents should return findings as text, not write report files." I did not route around it. Every file:line reference below was pasted from a `grep -n` of the current tree at 00:1xZ.
3. **Live prompt-caching page not fetched.** The brief's boundary forbids network calls. The cache price ratios are therefore parameters marked UNSURE (see DISCREPANCY D7).
4. **Run (a) covers a window, not the whole file.** It runs from the audit's slice start to my pin: offset 740,755,248 (the compact_boundary at 2026-09-25 21:58:11Z) up to byte 780,424,880. The whole file since 09-02 (20,622 requests in 138 segments at the audit pin) was not replayed.
5. **The 20-block cache lookback miss is not modeled.** The cache model follows the brief's "the tail after the edit point is written again" (see D16).
6. **Thinking in the subagent files is mostly unsized.** Those files record the final usage for only a minority of requests (see D6). R2 savings there are a lower bound.
7. **Archived thinking is never scored for use-after-archive.** Its text is never read, per the brief's safety rule.
8. **No between-turn mode on the subagent files.** The brief asked for per-request mode there.
9. **No Hermes lane measured.** The runs are sandbox subagent transcripts only.
10. **Ignored bytecode left in the tree.** Imports left `scripts/jev_trim/__pycache__/` and `tests/__pycache__/test_jev_trim_replay*.pyc`, both gitignored. I left them rather than remove files beyond my own sources.

## 1. Premise re-run (item 1), from the main tree

All ten PREMISE commands matched the brief's expected output.
- HEAD was b20b9c2 at my start (past the PIN, allowed). `PIN-is-an-ancestor-of-HEAD` was printed.
- The diff-stat line was empty.
- The accounting.py grep printed lines 16, 17, 26, 36, 44, 48. The transcript.py grep printed lines 31, 62, 85, 132.
- `ls: cannot access 'scripts/jev_trim': No such file or directory`.
- The `git grep` count was `0`.
- `main-transcript-present` and `at-least-300-subagent-transcripts` were both printed.
- The audit lines 200-202 were identical.
- The pytest line was `42 passed`. It ran with a private `--basetemp` in my scratchpad instead of /tmp/t0-premise-bt, per the lane rule; that was the only change.

HEAD moved to the commit "Live-state: the two waiting briefs are committed; three commits wai ..." (a local id then) during my run (other sessions' commits). I re-checked at 00:1xZ:
- `git diff --stat 6222e4a HEAD -- scripts/jev_pipes/ tests/test_jev_pipes_replay.py tests/fixtures/jev_pipes/` is still empty.
- e48e954 changed only §2 (the Hermes measurement rows) of D105-DESIGN-v1.md, not §3.1.
- The T0 brief is unchanged.

Pins, each taken as `stat -c %s` at my start:
- Main transcript: 780,424,880 bytes, at 22:59:41Z.
- Subagent files, at 23:01:42Z:
  - agent-a88c7c57f2fa2a96b: 14,082,496 bytes.
  - agent-a4920ba3ae772b9d0: 11,814,169 bytes.
  - agent-ac753871198ee8cfd: 9,235,269 bytes.

The three were chosen as the longest by byte length among the 28 files modified since 2026-09-26. All three are `agentType` code-implementer.

## 2. Files (CREATE only; the reused files are unmodified)

| file | lines | sha256 |
|---|---:|---|
| scripts/jev_trim/__init__.py | 5 | 8fbf15905b67d8b6603de2debf8a21665a0b497aa32b0c2c3c5b19d8059cb91e |
| scripts/jev_trim/replay.py | 1266 | ff35dbb8541818bd1cc8beaea0fed15dc8a104099030cbc510ebc00dcb88e321 |
| tests/test_jev_trim_replay.py | 833 | 92b29e6d5b364b433fa391b0fb30bd289e66a530600aa418214f783349c1365d |
| docs/research/findings/jev-trim/replay-2026-09-28/SUMMARY.md | 853 | cbe370e47a807a72bdc849d00a9b90d14c5ab2d2e697109d8770800fa54490e2 |
| …/crosscheck.json | 311 | a3ab466f86ab44fdd2bb248db3a13435c679c06ee08faaab396d45a295884e5e |
| …/run-main.json | 27438 | ff6b6ded0574eb95984c088a40dbc13c2ba08ca151994a8c5e3a0470ea4fd3a6 |
| …/run-main-thinking-model.json | 27418 | ad3949f456e9cb9ac16b2dc1fb1e2cb9764bb1ca7afb18d7cf7323a4258e466e |
| …/run-main-user-cpt-2.26.json | 27509 | a028c1914758e3ee29f41d55b115b515042e97e9a729a68a7f8a5456e3694891 |
| …/run-sub-a88c7c57f2fa2a96b.json | 32978 | 6c7b3c34ba5d7bd9b52d0cccb3ad47c51971a74598979496a4cf4425273c6dec |
| …/run-sub-a4920ba3ae772b9d0.json | 30835 | a62b46adf2a2857f4832867ae94df3fdcbdabbc25fd5be97669f55ce622d6430 |
| …/run-sub-ac753871198ee8cfd.json | 31355 | a5a05b4e709e8887e1c6e25a1a309862bd3b526e362d48cf937449dbd3278b30 |

- **Every output was written by `replay.py`, never by hand.** All eight outputs were regenerated from the final code.
- **Determinism was verified on real data.** Two full passes of every run wrote byte-identical JSON: `sha256sum -c` printed OK for all seven JSON files, rc 0.
- **Untracked files in the tree** are my eleven, plus `tasks/briefs/i59/VERIFY-I59-F-R5-report.md`, which is NOT mine (it appeared during my run).
- **The other lane's tracked files** (the `.lanes-live` list) are untouched.

Reused modules are read and called, never modified:
- `scripts/jev_pipes/transcript.py:85` (`def iter_records`): the pinned-length streaming; `_blocks`, `result_text` and `rerun_key` are also used.
- `scripts/jev_pipes/accounting.py:36` (`def miss`): together with `tokens`, `percentile` and `LOOKAHEAD`.

## 3. Gates (item 7), each run twice with a private `--basetemp` passed as a pytest argument

Final code (replay.py sha256 ff35dbb8…), 00:07:22Z to 00:07:54Z:
- `tests/test_jev_trim_replay.py`, set id `1 files set=1bb7608ed22a`:
  - run 1: `pytest-exit: 0` / `pytest-summary: 36 passed in 3.22s`
  - run 2: `pytest-exit: 0` / `pytest-summary: 36 passed in 3.00s`
- `tests/test_jev_pipes_replay.py`, set id `1 files set=17f6a5adc0c9`:
  - run 1: `pytest-exit: 0` / `pytest-summary: 42 passed in 24.56s`
  - run 2: `pytest-exit: 0` / `pytest-summary: 42 passed in 24.60s`

An earlier pair of runs, before two print and summary-writer edits, gave the same counts: `36 passed in 3.12s` / `3.06s` and `42 passed in 24.28s` / `23.80s`.

No other test names the new files; `grep -rln jev_trim tests/ harness-ports/tests/` finds only the new test file.

## 4. Mutants (item 6): nine, each killed

**In-file test.** `test_mutant_is_killed` (`tests/test_jev_trim_replay.py:789`, `MUTANTS`) checks three things per mutant. The anchor occurs exactly once in replay.py. The unmutated file passes the check. The mutant raises AssertionError. The `-k mutant` run printed `9 passed, 27 deselected in 0.79s`.

**Whole-file runs.** I also ran the whole test file against each mutant in a scratch copy of the tree, at 00:08:32Z on the final code. The extra failures in each count are `test_mutant_is_killed` parameters, which fail by design when the tree's "original" is the mutant.

| mutant (anchor change) | result | behavior tests red |
|---|---|---|
| age-boundary-off-by-one (`not items[q].req < r - cell.age` → `<=`, at `scripts/jev_trim/replay.py:695`) | 3 failed, 33 passed | test_r3_age_boundary, test_r4_archives_only_large_old_inputs |
| supersede-keeps-the-oldest (`heapq.heappush(heap, older)` → push the newer copy, `scripts/jev_trim/replay.py:654`) | 2 failed, 34 passed | test_r1_archives_superseded_copies_and_keeps_the_newest |
| hysteresis-stops-at-B-not-L (`target = cell.low` → `cell.budget`, `scripts/jev_trim/replay.py:678`) | 4 failed, 32 passed | test_hysteresis_fires_past_b_and_lands_at_or_under_l, test_the_cache_model_on_hand_computed_numbers |
| protected-set-ignored (`protect_from` → `entered`, `scripts/jev_trim/replay.py:659`) | 4 failed, 32 passed | test_the_protected_set_is_never_archived, test_r2_archives_thinking_only_before_the_current_turn |
| kept-item-check-dropped (`kept = frozenset` keeps fixed tokens only, `scripts/jev_trim/replay.py:762`) | 4 failed, 32 passed | test_use_after_archive_is_zero_when_a_kept_item_holds_the_token, test_the_restricted_miss_calls_equal_unrestricted_calls, test_visible_only_variant_counts_an_archived_earlier_copy |
| between-turn-fires-inside-a-turn (`or turn_start` → `or True`) | 2 failed, 34 passed | test_between_turn_never_trims_inside_a_turn |
| trim-fires-at-B-not-past-it (`active > cell.budget` → `>=`) | 4 failed, 32 passed | test_hysteresis_…, test_the_cache_model_… |
| stub-dropped-with-its-pair (`stub = 0.0` for every kind) | 6 failed, 30 passed | test_a_stub_keeps_its_pair, test_hysteresis_…, test_the_cache_model_… |
| thinking-before-the-current-turn-ignored (protect from `cur + 1`) | 4 failed, 32 passed | test_r2_…, test_the_protected_set_… |

**Red-green history.** The tests were written after the code, not test-first. The red evidence is the mutant table. Three of my first test runs went red on my own test mistakes, never on a code defect:
- The cross-check fixture's arithmetic: the median of (200, 300) is 250.0, not 250.5.
- The security fixture was too short for any cell to archive. The de-vacuum control caught it.
- The visible-only expectation: the case was the earlier-history under-count. The test now documents it.

**Other test evidence:**
- **Security** (`tests/test_jev_trim_replay.py:695`). A run-time secret sits in every text field, the thinking field included. Four CLI runs follow: run with three turn units, run with `--thinking-size model`, crosscheck, and summary. No 8-character piece of the secret appears in any output file or print. The controls check that the fixture holds the value, and that archived items exist in the outputs.
- **Thinking never read.** `test_a_thinking_blocks_text_never_enters_the_timeline` plants a token in a thinking field; it reaches no item text, token set or stub. The control plants it in a text block, where it is found.
- **Real outputs.** All 3,311 string values and 146,313 keys in the seven JSON outputs match the name pattern or are my two fixed strings: 0 others.
- **The restricted miss calls.** `test_the_restricted_miss_calls_equal_unrestricted_calls` (`tests/test_jev_trim_replay.py:529`) is an oracle. It rebuilds each archived item's full history and lookahead from the archive map, calls `accounting.miss` directly, and must agree with the restricted, memoized rows (more than 20 items checked).

## 5. Cross-check (b): no policy, at the audit's pin 777,005,680

| day | requests (mine / audit) | median (mine / audit) | nearest-rank median | p90 | max | min | compactions |
|---|---|---|---|---|---|---|---|
| 2026-09-26 | 781 / 781 | 545,883 / 545,883 | 545,883 | 733,680 / 733,680 | 783,173 / 783,173 | 130,278 / 130,278 | 2 / 2 |
| 2026-09-28 | 792 / 792 | 460,505.5 / 460,505 | 460,365 | 714,430 / 714,430 | 783,147 / 783,147 | 127,359 / 127,359 | 3 / 3 |

- **Every field is equal except the 09-28 median.** 792 is an even count. My median is the mean of the two middle values (`statistics.median`), 460,505.5; the audit printed it truncated to an integer. `median_match_after_truncation` is True. The nearest-rank median (460,365) would not match, so the audit's definition is the two-middle mean.
- **The request definition** is the first assistant record with usage per requestId, on the main thread, excluding `<synthetic>` records. It uses the audit's context sum.
- **Verified from the audit's own text:** `docs/research/findings/jev-trim/TRIM-AUDIT-2026-09-28.md:200-202` shows `545,883` and `460,505`.

## 6. What was built (as data)

**The timeline** (`build`) is one streaming pass with `iter_records`.
- **Requests:** the first assistant record with usage per requestId on the chosen thread; the whole context is `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`.
- **Segments** start at compact_boundary records. **Each real segment is simulated from its real start.**
- **Turns** are kept both ways: stop-hook (stop_hook_summary or compact_boundary) and promptId. Turn ids count only turns that hold a request.
- **Items** enter the context of the first request after their record, and carry a kind, a request index, a size, both turns, a segment and the tool_use pairing.
  - Kinds: tool_result and tool_input by tool; assistant_text; thinking (one item per request); typed_user_text; other_user_text; task_reminder; hook_context by hookName; other_attachment by type.
  - hook_success and prompt_snapshot are not items. The snapshot's tokens count as always-visible text.
- **Sizes:**
  - Exact: request contexts, the cache splits by TTL, output_tokens, and the thinking count where the final usage record holds it (see D1).
  - Modeled: user-side content at 2.90 characters per token, per the brief.

**The policy** (`simulate`, `scripts/jev_trim/replay.py:626`) is a pure function of the timeline and one cell.
- **R1:** a task reminder once a newer one exists; a Read result of a file_path read again later; a hook context replaced by a newer one from the same hookName.
- **R2:** thinking.
- **R3:** tool results with age > A.
- **R4:** tool inputs over 500 tokens with age > A.
- **Protected:** the segment's first user message, typed text, skill bodies, and the current turn plus the last K=2 turns.
- **Stubs:** a stub costs 40 tokens and keeps its tool_use_id pairing. Thinking is dropped at cost 0.
- **Hysteresis:** once past B, archive in rule order, oldest first, down to L. Modes are between-turn (the first request of a turn) and per-request.

**The cache model**, per request after a trim, in base-input-price units:
- Reads saved: −0.05 × saved.
- Rewritten tail, per trim: +(write − 0.05) × max(0, tail − real write − real uncached).
- The prefix before the edit point comes from the exact context of the request before that item entered.
- Real writes are priced by their TTL split; extra writes at the run's dominant TTL: 2.0 on main (all 1-hour), 1.25 on the subagents (all 5-minute).

**Use-after-archive** calls `accounting.miss` through an exact memo (`scripts/jev_trim/replay.py:573`, `def miss_memo`).
- The item's text is the original. Its stub is the kept text.
- The history is the tokens of P1's earlier history, of every item active after the trim, of every stub, and of the system-prompt snapshot.
- Horizons: the next 20 tool inputs or assistant texts (20 tool calls for a re-run), and the rest of the segment.
- A visible-only variant drops the earlier-history term.
- **This is a lower bound on need:** a need that leaves no distinctive token or re-run is not seen. Also, a token that re-entered through a later item still counts as a miss, per P1's definition.

**Grid:**
- B ∈ {100,000; 131,072; 150,000; 200,000; 250,000}; L = 0.75 B, plus 0.6 B at 200,000.
- A ∈ {10, 20, 50}; four rule sets; two modes (main) or per-request (subagents).
- A is irrelevant for R1 and R1+R2, so those rows show A = "any".

## 7a. Run (a): main transcript, offset 740,755,248 to pin 780,424,880 (grid 32.0 s)

**Timeline:**
- **Requests:** 1,898 in 7 segments, all `claude-opus-5-5`; 6 synthetic excluded; 9 unparseable lines in the file.
- **Segment starts** (segment, requests, first context): (1, 333, 131,080), (2, 304, 130,278), (3, 344, 137,086), (4, 307, 131,279), (5, 268, 127,359), (6, 247, 129,409), (7, 95, 128,688). Segments 1-6 equal the audit's §3.3 first contexts.
- **Real context:** median 454,522, p90 722,281, max 783,173.
- **Turns:** stop-hook 121 (median 5.0 requests per turn, max 130); promptId 64 (median 15.0, max 142).
- **Items:** 9,277. 47 items after a segment's last request were never sent.

| kind | items | tokens |
|---|---:|---:|
| thinking | 1,542 | 1,144,639 |
| tool_input | 1,910 | 934,770 (Bash 1,628 items, 788,023) |
| tool_result | 1,910 | 813,957 |
| other_attachment | 2,684 | 817,095 |
| other_user_text | 152 | 201,196 |
| hook_context | 193 | 124,441 |
| typed_user_text | 42 | 124,769 |
| assistant_text | 625 | 79,349 |
| task_reminder | 219 | 76,347 |

- **Thinking:** 1,768 blocks, stored text empty in 1,548. 1,547 requests are sized exactly and 1 by the model.
- **Thinking method check.** Over those 1,547 requests the exact count totals 1,152,566, against 1,458,001 for the brief's model (1.265×).
- **Calibration:** 1,891 pairs. The exact user-side residual totals 1,993,742, against 1,614,280 modeled at 2.90.
- **Per-kind fit** (R² 0.931, intercept 102.5), in characters per token: tool results 2.26, hook contexts and task reminders 2.40, user text 2.36, other attachments 5.25.
- **Real session (no trim):** requests over B are 1,898 / 1,893 / 1,871 / 1,730 / 1,600 at the five budgets. Cost is 54,217,480.5 units at read 0.05. Writes: 1-hour 5,285,219, 5-minute 0.
- **Segment start alone over B.** At B=100,000 it passes for 1,898 of 1,898 requests (the audit's R5: 525 of 525 sampled). At B=131,072, 3 of the first 6 segment starts are above.

**Columns in every table below:**
- **median, p90:** the active context per request under the policy.
- **>B:** requests over B.
- **prot>B:** the share of requests whose protected set alone passes B.
- **net units:** extra writes minus reads saved, at read 0.05, with its share of the real cost. **% real @0.1** is the same at read 0.1.
- **UAA@20 / @H (scored):** archived items counted as used after archive, at 20 and at the horizon, out of the scored archived items. **vis** is the visible-only variant.

| B | L | A | rules | mode | median | p90 | >B | prot>B | trims | net units @0.05 (% real) | % real @0.1 | UAA@20 / @H (scored) | vis@20 / @H |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 100,000 | 75,000 | any | R1 | between-turn | 449,283 | 703,725 | 1,898 | 100.0% | 64 | 12,516,198 (+23.1%) | +11.7% | 6 / 17 (322) | 7 / 23 |
| 100,000 | 75,000 | any | R1 | per-request | 449,283 | 703,725 | 1,898 | 100.0% | 80 | 13,459,196 (+24.8%) | +12.6% | 6 / 17 (323) | 7 / 24 |
| 100,000 | 75,000 | any | R1+R2 | between-turn | 400,210 | 566,804 | 1,898 | 100.0% | 100 | 7,339,279 (+13.5%) | +0.6% | 6 / 17 (322) | 7 / 23 |
| 100,000 | 75,000 | any | R1+R2 | per-request | 400,210 | 566,366 | 1,898 | 100.0% | 126 | 9,303,334 (+17.2%) | +2.5% | 6 / 17 (323) | 7 / 24 |
| 100,000 | 75,000 | 10 | R1+R2+R3 | between-turn | 360,915 | 485,616 | 1,898 | 100.0% | 100 | 2,376,836 (+4.4%) | -8.3% | 57 / 245 (1573) | 96 / 350 |
| 100,000 | 75,000 | 10 | R1+R2+R3 | per-request | 360,834 | 485,483 | 1,898 | 100.0% | 160 | 5,433,829 (+10.0%) | -5.3% | 57 / 244 (1575) | 95 / 351 |
| 100,000 | 75,000 | 20 | R1+R2+R3 | between-turn | 361,308 | 486,187 | 1,898 | 100.0% | 101 | 3,325,521 (+6.1%) | -7.4% | 58 / 241 (1550) | 96 / 338 |
| 100,000 | 75,000 | 20 | R1+R2+R3 | per-request | 360,915 | 485,660 | 1,898 | 100.0% | 274 | 15,447,421 (+28.5%) | +4.7% | 57 / 241 (1560) | 91 / 339 |
| 100,000 | 75,000 | 50 | R1+R2+R3 | between-turn | 366,157 | 489,900 | 1,898 | 100.0% | 102 | 9,239,429 (+17.0%) | -1.1% | 44 / 210 (1464) | 62 / 274 |
| 100,000 | 75,000 | 50 | R1+R2+R3 | per-request | 363,035 | 486,953 | 1,898 | 100.0% | 619 | 94,325,048 (+174.0%) | +83.5% | 42 / 213 (1505) | 58 / 282 |
| 100,000 | 75,000 | 10 | R1+R2+R3+R4 | between-turn | 331,889 | 437,578 | 1,898 | 100.0% | 100 | -1,398,929 (-2.6%) | -14.8% | 96 / 368 (1989) | 229 / 650 |
| 100,000 | 75,000 | 10 | R1+R2+R3+R4 | per-request | 331,554 | 437,456 | 1,898 | 100.0% | 170 | 1,984,883 (+3.7%) | -11.4% | 97 / 367 (1991) | 235 / 657 |
| 100,000 | 75,000 | 20 | R1+R2+R3+R4 | between-turn | 332,932 | 438,523 | 1,898 | 100.0% | 101 | -153,950 (-0.3%) | -13.4% | 95 / 353 (1957) | 219 / 611 |
| 100,000 | 75,000 | 20 | R1+R2+R3+R4 | per-request | 331,594 | 437,456 | 1,898 | 100.0% | 305 | 14,549,505 (+26.8%) | +1.1% | 96 / 353 (1969) | 215 / 620 |
| 100,000 | 75,000 | 50 | R1+R2+R3+R4 | between-turn | 346,493 | 444,977 | 1,898 | 100.0% | 102 | 6,651,478 (+12.3%) | -5.8% | 67 / 284 (1821) | 124 / 457 |
| 100,000 | 75,000 | 50 | R1+R2+R3+R4 | per-request | 342,424 | 440,583 | 1,898 | 100.0% | 681 | 103,016,630 (+190.0%) | +89.8% | 63 / 293 (1877) | 124 / 473 |
| 131,072 | 98,304 | any | R1 | between-turn | 449,283 | 703,725 | 1,893 | 99.7% | 64 | 12,516,198 (+23.1%) | +11.7% | 6 / 17 (322) | 7 / 23 |
| 131,072 | 98,304 | any | R1 | per-request | 449,283 | 703,725 | 1,893 | 99.7% | 80 | 13,459,196 (+24.8%) | +12.6% | 6 / 17 (323) | 7 / 24 |
| 131,072 | 98,304 | any | R1+R2 | between-turn | 400,210 | 566,804 | 1,893 | 99.7% | 100 | 7,339,279 (+13.5%) | +0.6% | 6 / 17 (322) | 7 / 23 |
| 131,072 | 98,304 | any | R1+R2 | per-request | 400,210 | 566,366 | 1,893 | 99.7% | 126 | 9,303,334 (+17.2%) | +2.5% | 6 / 17 (323) | 7 / 24 |
| 131,072 | 98,304 | 10 | R1+R2+R3 | between-turn | 360,915 | 485,616 | 1,893 | 99.7% | 100 | 2,376,836 (+4.4%) | -8.3% | 57 / 245 (1573) | 96 / 350 |
| 131,072 | 98,304 | 10 | R1+R2+R3 | per-request | 360,834 | 485,483 | 1,893 | 99.7% | 160 | 5,433,829 (+10.0%) | -5.3% | 57 / 244 (1575) | 95 / 351 |
| 131,072 | 98,304 | 20 | R1+R2+R3 | between-turn | 361,308 | 486,187 | 1,893 | 99.7% | 101 | 3,325,521 (+6.1%) | -7.4% | 58 / 241 (1550) | 96 / 338 |
| 131,072 | 98,304 | 20 | R1+R2+R3 | per-request | 360,915 | 485,660 | 1,893 | 99.7% | 274 | 15,447,421 (+28.5%) | +4.7% | 57 / 241 (1560) | 91 / 339 |
| 131,072 | 98,304 | 50 | R1+R2+R3 | between-turn | 366,157 | 489,900 | 1,893 | 99.7% | 102 | 9,239,429 (+17.0%) | -1.1% | 44 / 210 (1464) | 62 / 274 |
| 131,072 | 98,304 | 50 | R1+R2+R3 | per-request | 363,035 | 486,953 | 1,893 | 99.7% | 619 | 94,325,048 (+174.0%) | +83.5% | 42 / 213 (1505) | 58 / 282 |
| 131,072 | 98,304 | 10 | R1+R2+R3+R4 | between-turn | 331,889 | 437,578 | 1,893 | 99.7% | 100 | -1,398,929 (-2.6%) | -14.8% | 96 / 368 (1989) | 229 / 650 |
| 131,072 | 98,304 | 10 | R1+R2+R3+R4 | per-request | 331,554 | 437,456 | 1,893 | 99.7% | 170 | 1,984,883 (+3.7%) | -11.4% | 97 / 367 (1991) | 235 / 657 |
| 131,072 | 98,304 | 20 | R1+R2+R3+R4 | between-turn | 332,932 | 438,523 | 1,893 | 99.7% | 101 | -153,950 (-0.3%) | -13.4% | 95 / 353 (1957) | 219 / 611 |
| 131,072 | 98,304 | 20 | R1+R2+R3+R4 | per-request | 331,594 | 437,456 | 1,893 | 99.7% | 305 | 14,549,505 (+26.8%) | +1.1% | 96 / 353 (1969) | 215 / 620 |
| 131,072 | 98,304 | 50 | R1+R2+R3+R4 | between-turn | 346,493 | 444,977 | 1,893 | 99.7% | 102 | 6,651,478 (+12.3%) | -5.8% | 67 / 284 (1821) | 124 / 457 |
| 131,072 | 98,304 | 50 | R1+R2+R3+R4 | per-request | 342,424 | 440,583 | 1,893 | 99.7% | 681 | 103,016,630 (+190.0%) | +89.8% | 63 / 293 (1877) | 124 / 473 |
| 150,000 | 112,500 | any | R1 | between-turn | 449,283 | 703,725 | 1,871 | 94.0% | 64 | 12,516,198 (+23.1%) | +11.7% | 6 / 17 (322) | 7 / 23 |
| 150,000 | 112,500 | any | R1 | per-request | 449,283 | 703,725 | 1,871 | 94.0% | 80 | 13,459,196 (+24.8%) | +12.6% | 6 / 17 (323) | 7 / 24 |
| 150,000 | 112,500 | any | R1+R2 | between-turn | 400,210 | 566,804 | 1,871 | 94.0% | 100 | 7,339,279 (+13.5%) | +0.6% | 6 / 17 (322) | 7 / 23 |
| 150,000 | 112,500 | any | R1+R2 | per-request | 400,210 | 566,366 | 1,871 | 94.0% | 126 | 9,303,334 (+17.2%) | +2.5% | 6 / 17 (323) | 7 / 24 |
| 150,000 | 112,500 | 10 | R1+R2+R3 | between-turn | 360,915 | 485,616 | 1,871 | 94.0% | 100 | 2,376,836 (+4.4%) | -8.3% | 57 / 245 (1573) | 96 / 350 |
| 150,000 | 112,500 | 10 | R1+R2+R3 | per-request | 360,834 | 485,483 | 1,871 | 94.0% | 160 | 5,433,829 (+10.0%) | -5.3% | 57 / 244 (1575) | 95 / 351 |
| 150,000 | 112,500 | 20 | R1+R2+R3 | between-turn | 361,308 | 486,187 | 1,871 | 94.0% | 101 | 3,325,521 (+6.1%) | -7.4% | 58 / 241 (1550) | 96 / 338 |
| 150,000 | 112,500 | 20 | R1+R2+R3 | per-request | 360,915 | 485,660 | 1,871 | 94.0% | 274 | 15,447,421 (+28.5%) | +4.7% | 57 / 241 (1560) | 91 / 339 |
| 150,000 | 112,500 | 50 | R1+R2+R3 | between-turn | 366,157 | 489,900 | 1,871 | 94.0% | 102 | 9,239,429 (+17.0%) | -1.1% | 44 / 210 (1464) | 62 / 274 |
| 150,000 | 112,500 | 50 | R1+R2+R3 | per-request | 363,035 | 486,953 | 1,871 | 94.0% | 619 | 94,325,048 (+174.0%) | +83.5% | 42 / 213 (1505) | 58 / 282 |
| 150,000 | 112,500 | 10 | R1+R2+R3+R4 | between-turn | 331,889 | 437,578 | 1,871 | 94.0% | 100 | -1,398,929 (-2.6%) | -14.8% | 96 / 368 (1989) | 229 / 650 |
| 150,000 | 112,500 | 10 | R1+R2+R3+R4 | per-request | 331,554 | 437,456 | 1,871 | 94.0% | 170 | 1,984,883 (+3.7%) | -11.4% | 97 / 367 (1991) | 235 / 657 |
| 150,000 | 112,500 | 20 | R1+R2+R3+R4 | between-turn | 332,932 | 438,523 | 1,871 | 94.0% | 101 | -153,950 (-0.3%) | -13.4% | 95 / 353 (1957) | 219 / 611 |
| 150,000 | 112,500 | 20 | R1+R2+R3+R4 | per-request | 331,594 | 437,456 | 1,871 | 94.0% | 305 | 14,549,505 (+26.8%) | +1.1% | 96 / 353 (1969) | 215 / 620 |
| 150,000 | 112,500 | 50 | R1+R2+R3+R4 | between-turn | 346,493 | 444,977 | 1,871 | 94.0% | 102 | 6,651,478 (+12.3%) | -5.8% | 67 / 284 (1821) | 124 / 457 |
| 150,000 | 112,500 | 50 | R1+R2+R3+R4 | per-request | 342,424 | 440,583 | 1,871 | 94.0% | 681 | 103,016,630 (+190.0%) | +89.8% | 63 / 293 (1877) | 124 / 473 |
| 200,000 | 150,000 | any | R1 | between-turn | 449,283 | 703,725 | 1,730 | 63.7% | 64 | 12,516,198 (+23.1%) | +11.7% | 6 / 17 (322) | 7 / 23 |
| 200,000 | 150,000 | any | R1 | per-request | 449,283 | 703,725 | 1,730 | 63.7% | 80 | 13,459,196 (+24.8%) | +12.6% | 6 / 17 (323) | 7 / 24 |
| 200,000 | 150,000 | any | R1+R2 | between-turn | 400,210 | 566,804 | 1,730 | 63.7% | 100 | 7,339,279 (+13.5%) | +0.6% | 6 / 17 (322) | 7 / 23 |
| 200,000 | 150,000 | any | R1+R2 | per-request | 400,210 | 566,366 | 1,730 | 63.7% | 126 | 9,303,334 (+17.2%) | +2.5% | 6 / 17 (323) | 7 / 24 |
| 200,000 | 150,000 | 10 | R1+R2+R3 | between-turn | 360,915 | 485,616 | 1,730 | 63.7% | 100 | 2,376,836 (+4.4%) | -8.3% | 57 / 245 (1573) | 96 / 350 |
| 200,000 | 150,000 | 10 | R1+R2+R3 | per-request | 360,834 | 485,483 | 1,730 | 63.7% | 160 | 5,433,829 (+10.0%) | -5.3% | 57 / 244 (1575) | 95 / 351 |
| 200,000 | 150,000 | 20 | R1+R2+R3 | between-turn | 361,308 | 486,187 | 1,730 | 63.7% | 101 | 3,325,521 (+6.1%) | -7.4% | 58 / 241 (1550) | 96 / 338 |
| 200,000 | 150,000 | 20 | R1+R2+R3 | per-request | 360,915 | 485,660 | 1,730 | 63.7% | 274 | 15,447,421 (+28.5%) | +4.7% | 57 / 241 (1560) | 91 / 339 |
| 200,000 | 150,000 | 50 | R1+R2+R3 | between-turn | 366,157 | 489,900 | 1,730 | 63.7% | 102 | 9,239,429 (+17.0%) | -1.1% | 44 / 210 (1464) | 62 / 274 |
| 200,000 | 150,000 | 50 | R1+R2+R3 | per-request | 363,035 | 486,953 | 1,730 | 63.7% | 619 | 94,325,048 (+174.0%) | +83.5% | 42 / 213 (1505) | 58 / 282 |
| 200,000 | 150,000 | 10 | R1+R2+R3+R4 | between-turn | 331,889 | 437,578 | 1,730 | 63.7% | 100 | -1,398,929 (-2.6%) | -14.8% | 96 / 368 (1989) | 229 / 650 |
| 200,000 | 150,000 | 10 | R1+R2+R3+R4 | per-request | 331,554 | 437,456 | 1,730 | 63.7% | 170 | 1,984,883 (+3.7%) | -11.4% | 97 / 367 (1991) | 235 / 657 |
| 200,000 | 150,000 | 20 | R1+R2+R3+R4 | between-turn | 332,932 | 438,523 | 1,730 | 63.7% | 101 | -153,950 (-0.3%) | -13.4% | 95 / 353 (1957) | 219 / 611 |
| 200,000 | 150,000 | 20 | R1+R2+R3+R4 | per-request | 331,594 | 437,456 | 1,730 | 63.7% | 305 | 14,549,505 (+26.8%) | +1.1% | 96 / 353 (1969) | 215 / 620 |
| 200,000 | 150,000 | 50 | R1+R2+R3+R4 | between-turn | 346,493 | 444,977 | 1,730 | 63.7% | 102 | 6,651,478 (+12.3%) | -5.8% | 67 / 284 (1821) | 124 / 457 |
| 200,000 | 150,000 | 50 | R1+R2+R3+R4 | per-request | 342,424 | 440,583 | 1,730 | 63.7% | 681 | 103,016,630 (+190.0%) | +89.8% | 63 / 293 (1877) | 124 / 473 |
| 200,000 | 120,000 | any | R1 | between-turn | 449,283 | 703,725 | 1,730 | 63.7% | 64 | 12,516,198 (+23.1%) | +11.7% | 6 / 17 (322) | 7 / 23 |
| 200,000 | 120,000 | any | R1 | per-request | 449,283 | 703,725 | 1,730 | 63.7% | 80 | 13,459,196 (+24.8%) | +12.6% | 6 / 17 (323) | 7 / 24 |
| 200,000 | 120,000 | any | R1+R2 | between-turn | 400,210 | 566,804 | 1,730 | 63.7% | 100 | 7,339,279 (+13.5%) | +0.6% | 6 / 17 (322) | 7 / 23 |
| 200,000 | 120,000 | any | R1+R2 | per-request | 400,210 | 566,366 | 1,730 | 63.7% | 126 | 9,303,334 (+17.2%) | +2.5% | 6 / 17 (323) | 7 / 24 |
| 200,000 | 120,000 | 10 | R1+R2+R3 | between-turn | 360,915 | 485,616 | 1,730 | 63.7% | 100 | 2,376,836 (+4.4%) | -8.3% | 57 / 245 (1573) | 96 / 350 |
| 200,000 | 120,000 | 10 | R1+R2+R3 | per-request | 360,834 | 485,483 | 1,730 | 63.7% | 160 | 5,433,829 (+10.0%) | -5.3% | 57 / 244 (1575) | 95 / 351 |
| 200,000 | 120,000 | 20 | R1+R2+R3 | between-turn | 361,308 | 486,187 | 1,730 | 63.7% | 101 | 3,325,521 (+6.1%) | -7.4% | 58 / 241 (1550) | 96 / 338 |
| 200,000 | 120,000 | 20 | R1+R2+R3 | per-request | 360,915 | 485,660 | 1,730 | 63.7% | 274 | 15,447,421 (+28.5%) | +4.7% | 57 / 241 (1560) | 91 / 339 |
| 200,000 | 120,000 | 50 | R1+R2+R3 | between-turn | 366,157 | 489,900 | 1,730 | 63.7% | 102 | 9,239,429 (+17.0%) | -1.1% | 44 / 210 (1464) | 62 / 274 |
| 200,000 | 120,000 | 50 | R1+R2+R3 | per-request | 363,035 | 486,953 | 1,730 | 63.7% | 619 | 94,325,048 (+174.0%) | +83.5% | 42 / 213 (1505) | 58 / 282 |
| 200,000 | 120,000 | 10 | R1+R2+R3+R4 | between-turn | 331,889 | 437,578 | 1,730 | 63.7% | 100 | -1,398,929 (-2.6%) | -14.8% | 96 / 368 (1989) | 229 / 650 |
| 200,000 | 120,000 | 10 | R1+R2+R3+R4 | per-request | 331,554 | 437,456 | 1,730 | 63.7% | 170 | 1,984,883 (+3.7%) | -11.4% | 97 / 367 (1991) | 235 / 657 |
| 200,000 | 120,000 | 20 | R1+R2+R3+R4 | between-turn | 332,932 | 438,523 | 1,730 | 63.7% | 101 | -153,950 (-0.3%) | -13.4% | 95 / 353 (1957) | 219 / 611 |
| 200,000 | 120,000 | 20 | R1+R2+R3+R4 | per-request | 331,594 | 437,456 | 1,730 | 63.7% | 305 | 14,549,505 (+26.8%) | +1.1% | 96 / 353 (1969) | 215 / 620 |
| 200,000 | 120,000 | 50 | R1+R2+R3+R4 | between-turn | 346,493 | 444,977 | 1,730 | 63.7% | 102 | 6,651,478 (+12.3%) | -5.8% | 67 / 284 (1821) | 124 / 457 |
| 200,000 | 120,000 | 50 | R1+R2+R3+R4 | per-request | 342,424 | 440,583 | 1,730 | 63.7% | 681 | 103,016,630 (+190.0%) | +89.8% | 63 / 293 (1877) | 124 / 473 |
| 250,000 | 187,500 | any | R1 | between-turn | 449,283 | 703,725 | 1,600 | 40.7% | 64 | 12,516,198 (+23.1%) | +11.7% | 6 / 17 (322) | 7 / 23 |
| 250,000 | 187,500 | any | R1 | per-request | 449,283 | 703,725 | 1,600 | 40.7% | 80 | 13,459,196 (+24.8%) | +12.6% | 6 / 17 (323) | 7 / 24 |
| 250,000 | 187,500 | any | R1+R2 | between-turn | 400,210 | 566,804 | 1,597 | 40.7% | 99 | 7,327,450 (+13.5%) | +0.6% | 6 / 17 (322) | 7 / 23 |
| 250,000 | 187,500 | any | R1+R2 | per-request | 400,210 | 566,366 | 1,595 | 40.7% | 126 | 9,311,427 (+17.2%) | +2.5% | 6 / 17 (323) | 7 / 24 |
| 250,000 | 187,500 | 10 | R1+R2+R3 | between-turn | 360,915 | 485,616 | 1,570 | 40.7% | 96 | 2,275,078 (+4.2%) | -8.4% | 57 / 245 (1573) | 97 / 350 |
| 250,000 | 187,500 | 10 | R1+R2+R3 | per-request | 360,834 | 485,483 | 1,563 | 40.7% | 153 | 5,296,286 (+9.8%) | -5.4% | 57 / 244 (1575) | 95 / 350 |
| 250,000 | 187,500 | 20 | R1+R2+R3 | between-turn | 361,308 | 486,187 | 1,575 | 40.7% | 99 | 3,263,169 (+6.0%) | -7.4% | 59 / 241 (1550) | 97 / 338 |
| 250,000 | 187,500 | 20 | R1+R2+R3 | per-request | 360,915 | 485,660 | 1,565 | 40.7% | 261 | 14,862,150 (+27.4%) | +4.1% | 57 / 241 (1560) | 91 / 339 |
| 250,000 | 187,500 | 50 | R1+R2+R3 | between-turn | 366,157 | 489,900 | 1,593 | 40.7% | 101 | 9,131,406 (+16.8%) | -1.2% | 44 / 210 (1464) | 62 / 274 |
| 250,000 | 187,500 | 50 | R1+R2+R3 | per-request | 363,035 | 486,953 | 1,588 | 40.7% | 611 | 93,331,228 (+172.1%) | +82.5% | 41 / 213 (1505) | 57 / 282 |
| 250,000 | 187,500 | 10 | R1+R2+R3+R4 | between-turn | 331,889 | 437,578 | 1,541 | 40.7% | 95 | -1,554,886 (-2.9%) | -14.9% | 96 / 367 (1989) | 230 / 647 |
| 250,000 | 187,500 | 10 | R1+R2+R3+R4 | per-request | 331,554 | 437,456 | 1,529 | 40.7% | 154 | 1,633,980 (+3.0%) | -11.8% | 98 / 367 (1991) | 236 / 657 |
| 250,000 | 187,500 | 20 | R1+R2+R3+R4 | between-turn | 332,932 | 438,523 | 1,546 | 40.7% | 96 | -436,814 (-0.8%) | -13.7% | 96 / 353 (1957) | 220 / 609 |
| 250,000 | 187,500 | 20 | R1+R2+R3+R4 | per-request | 331,594 | 437,456 | 1,529 | 40.7% | 267 | 12,372,272 (+22.8%) | -1.0% | 99 / 354 (1969) | 219 / 620 |
| 250,000 | 187,500 | 50 | R1+R2+R3+R4 | between-turn | 346,493 | 444,977 | 1,588 | 40.7% | 99 | 6,313,258 (+11.6%) | -6.2% | 68 / 284 (1821) | 124 / 458 |
| 250,000 | 187,500 | 50 | R1+R2+R3+R4 | per-request | 342,424 | 440,583 | 1,572 | 40.7% | 666 | 101,217,494 (+186.7%) | +88.0% | 62 / 293 (1877) | 123 / 473 |

### Per-trim stats and use-after-archive breakdown: main, reference cells (B=200,000, L=150,000, A=20, all four rules)

**between-turn:**
- **Trims:** 101, 0 of them at a request that does not start a turn.
- **Per trim:** saved tokens median 6,872.1, p90 52,293.4, max 222,429.5; items median 13; rewritten tail median 48,834, p90 131,416.8. Requests between trims: median 5, min 1.
- **Archived** by rule: R1 322, R2 1,301, R3 1,228, R4 407. 1,957 scored (thinking is never scored).
- **Scored by age:** 0-10: 6; 11-50: 1,045; 51-200: 905; 201+: 1.
- **UAA@20: 95** (R1 6, R3 63, R4 26; ages 11-50: 47, 51-200: 48).
  - By tool: Bash 66, Read 12, Agent 7, Write 6, hook_context 3, mcp__gitnexus__detect_changes 1.
- **UAA@H: 353** (R1 17, R3 245, R4 91; ages 11-50: 150, 51-200: 203).
  - By tool: Bash 285, Read 17, Agent 15, hook_context 14, Write 9, SendMessage 6, one to two each for Edit, WebFetch, mcp__github__* and mcp__gitnexus__detect_changes.
- **Visible-only:** @20 219 (R1 10, R3 121, R4 88); @H 611 (R1 28, R3 390, R4 193).
- **Cache:** real 54,217,480.5; reads saved 12,643,837.5; extra writes 12,489,887.6; net −153,949.9.

**per-request:**
- **Trims:** 305, 205 of them at a request that does not start a turn.
- **Per trim:** saved tokens median 844, p90 17,817.7, max 222,429.5; items median 2; rewritten tail median 38,182.7, p90 85,039. Requests between trims: median 1, min 1.
- **Archived** by rule: R1 323, R2 1,301, R3 1,237, R4 409.
- **UAA:** @20 96 (R1 6, R3 62, R4 28); @H 353 (R1 17, R3 245, R4 91).
- **Visible-only:** @20 215; @H 620.
- **Cache:** reads saved 12,725,123.4; extra writes 27,274,628.2; net +14,549,504.8.

### Sensitivity runs on the main transcript (full grids in SUMMARY.md; these are the reference rows)

- `main-thinking-model`: the brief's thinking method (output minus visible / 3.0) applied everywhere.
- `main-user-cpt-2.26`: user-side content at the fitted tool-result ratio.

| run | rules | mode | median | p90 | >B | prot>B | trims | net units @0.05 (% real) | % real @0.1 | UAA@20 / @H (scored) | vis@20 / @H |
|---|---|---|---|---|---|---|---|---|---|---|---|
| main | R1 | between-turn | 449,283 | 703,725 | 1,730 | 63.7% | 64 | 12,516,198 (+23.1%) | +11.7% | 6 / 17 (322) | 7 / 23 |
| main | R1+R2 | between-turn | 400,210 | 566,804 | 1,730 | 63.7% | 100 | 7,339,279 (+13.5%) | +0.6% | 6 / 17 (322) | 7 / 23 |
| main | R1+R2+R3 | between-turn | 361,308 | 486,187 | 1,730 | 63.7% | 101 | 3,325,521 (+6.1%) | -7.4% | 58 / 241 (1550) | 96 / 338 |
| main | R1+R2+R3+R4 | between-turn | 332,932 | 438,523 | 1,730 | 63.7% | 101 | -153,950 (-0.3%) | -13.4% | 95 / 353 (1957) | 219 / 611 |
| main | R1+R2+R3+R4 | per-request | 331,594 | 437,456 | 1,730 | 63.7% | 305 | 14,549,505 (+26.8%) | +1.1% | 96 / 353 (1969) | 215 / 620 |
| thinking-model | R1 | between-turn | 449,283 | 703,725 | 1,730 | 63.3% | 64 | 12,518,122 (+23.1%) | +11.7% | 6 / 17 (322) | 7 / 23 |
| thinking-model | R1+R2 | between-turn | 387,383 | 532,622 | 1,730 | 63.3% | 100 | 5,205,881 (+9.6%) | -3.1% | 6 / 17 (322) | 7 / 23 |
| thinking-model | R1+R2+R3 | between-turn | 346,728 | 458,915 | 1,730 | 63.3% | 101 | 1,080,646 (+2.0%) | -11.1% | 58 / 241 (1550) | 96 / 338 |
| thinking-model | R1+R2+R3+R4 | between-turn | 327,359 | 431,338 | 1,730 | 63.3% | 101 | -988,277 (-1.8%) | -14.7% | 90 / 332 (1809) | 188 / 541 |
| thinking-model | R1+R2+R3+R4 | per-request | 326,653 | 431,277 | 1,730 | 63.3% | 292 | 12,332,418 (+22.7%) | -1.5% | 91 / 333 (1820) | 185 / 549 |
| user-cpt-2.26 | R1 | between-turn | 448,501 | 696,966 | 1,730 | 69.1% | 64 | 12,173,490 (+22.5%) | +11.1% | 6 / 17 (322) | 7 / 23 |
| user-cpt-2.26 | R1+R2 | between-turn | 399,094 | 562,040 | 1,730 | 69.1% | 100 | 7,006,353 (+12.9%) | +0.0% | 6 / 17 (322) | 7 / 23 |
| user-cpt-2.26 | R1+R2+R3 | between-turn | 347,904 | 458,644 | 1,730 | 69.1% | 101 | 1,411,982 (+2.6%) | -10.7% | 58 / 241 (1596) | 95 / 337 |
| user-cpt-2.26 | R1+R2+R3+R4 | between-turn | 314,879 | 419,064 | 1,726 | 69.1% | 101 | -2,072,665 (-3.8%) | -16.8% | 95 / 353 (2003) | 218 / 610 |
| user-cpt-2.26 | R1+R2+R3+R4 | per-request | 314,110 | 418,839 | 1,725 | 69.1% | 310 | 13,106,719 (+24.2%) | -1.7% | 96 / 353 (2015) | 215 / 620 |

## 7c. Runs (c): three subagent transcripts, per-request mode, `--sidechain`

| file (pin) | requests / segments | real median / p90 / max | turns stop / promptId | thinking sized exact / model | writes 5m (1h) | calibration fit R² | requests over B (100k / 131k / 150k / 200k / 250k) |
|---|---|---|---|---|---|---|---|
| a88c7c57f2fa2a96b (14,082,496; the live SCRUB2-R1 lane) | 718 / 4 | 406,837 / 715,946 / 780,538 | 4 / 26 | 215 / 380 | 9,447,996 (0) | 0.295 | 701 / 673 / 656 / 588 / 529 |
| a4920ba3ae772b9d0 (11,814,169; live at pin) | 680 / 3 | 406,015 / 727,032 / 783,487 | 3 / 14 | 35 / 526 | 7,955,168 (0) | 0.486 | 659 / 620 / 597 / 552 / 491 |
| ac753871198ee8cfd (9,235,269) | 404 / 3 | 459,059.5 / 731,012 / 780,693 | 3 / 8 | 61 / 274 | 3,277,071 (0) | 0.287 | 391 / 386 / 377 / 347 / 316 |

- **Stop-hook turn unit (the spec'd unit): 0 trims in every cell.** That is 72 of 72 cells per file, 216 in all. These files hold no stop_hook_summary records, so each segment is one protected turn.
- **The promptId unit** is the brief's second turn definition; the tables follow.
- **The `request` unit is MY ADDITION (flagged in D5).** It protects the current request and the last K=2 requests: the nearest analog of a Hermes lane's message-window protection.
- **Extra writes are priced at 1.25** (5-minute TTL).

#### a88c7c57f2fa2a96b, turn unit promptId
| B | L | A | rules | median | p90 | >B | prot>B | trims | net units @0.05 (% real) | % real @0.1 | UAA@20 / @H (scored) | vis@20 / @H |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 100,000 | 75,000 | any | R1 | 403,690 | 689,965 | 701 | 94.6% | 10 | 2,080,479 (+7.9%) | +4.2% | 3 / 5 (51) | 3 / 5 |
| 100,000 | 75,000 | any | R1+R2 | 402,773 | 635,089 | 701 | 94.6% | 13 | 1,973,325 (+7.5%) | +2.3% | 3 / 5 (51) | 3 / 5 |
| 100,000 | 75,000 | 10 | R1+R2+R3 | 372,984 | 579,223 | 701 | 94.6% | 18 | 1,574,896 (+6.0%) | -1.0% | 25 / 83 (439) | 61 / 131 |
| 100,000 | 75,000 | 20 | R1+R2+R3 | 372,984 | 579,223 | 701 | 94.6% | 26 | 3,032,264 (+11.5%) | +2.4% | 25 / 79 (439) | 54 / 125 |
| 100,000 | 75,000 | 50 | R1+R2+R3 | 374,778 | 580,633 | 701 | 94.6% | 138 | 31,445,845 (+119.1%) | +69.1% | 20 / 70 (423) | 47 / 111 |
| 100,000 | 75,000 | 10 | R1+R2+R3+R4 | 364,748 | 561,272 | 701 | 94.6% | 18 | 1,217,447 (+4.6%) | -2.3% | 31 / 99 (510) | 79 / 164 |
| 100,000 | 75,000 | 20 | R1+R2+R3+R4 | 364,748 | 561,272 | 701 | 94.6% | 26 | 2,674,814 (+10.1%) | +1.1% | 31 / 95 (510) | 73 / 158 |
| 100,000 | 75,000 | 50 | R1+R2+R3+R4 | 364,748 | 564,311 | 701 | 94.6% | 145 | 32,918,726 (+124.7%) | +72.1% | 25 / 82 (489) | 61 / 131 |
| 131,072 | 98,304 | any | R1 | 403,690 | 689,965 | 673 | 80.4% | 10 | 2,080,479 (+7.9%) | +4.2% | 3 / 5 (51) | 3 / 5 |
| 131,072 | 98,304 | any | R1+R2 | 402,773 | 635,089 | 673 | 80.4% | 13 | 1,973,325 (+7.5%) | +2.3% | 3 / 5 (51) | 3 / 5 |
| 131,072 | 98,304 | 10 | R1+R2+R3 | 372,984 | 579,223 | 673 | 80.4% | 18 | 1,574,896 (+6.0%) | -1.0% | 25 / 83 (439) | 61 / 131 |
| 131,072 | 98,304 | 20 | R1+R2+R3 | 372,984 | 579,223 | 673 | 80.4% | 26 | 3,032,264 (+11.5%) | +2.4% | 25 / 79 (439) | 54 / 125 |
| 131,072 | 98,304 | 50 | R1+R2+R3 | 374,778 | 580,633 | 673 | 80.4% | 138 | 31,445,845 (+119.1%) | +69.1% | 20 / 70 (423) | 47 / 111 |
| 131,072 | 98,304 | 10 | R1+R2+R3+R4 | 364,748 | 561,272 | 673 | 80.4% | 18 | 1,217,447 (+4.6%) | -2.3% | 31 / 99 (510) | 79 / 164 |
| 131,072 | 98,304 | 20 | R1+R2+R3+R4 | 364,748 | 561,272 | 673 | 80.4% | 26 | 2,674,814 (+10.1%) | +1.1% | 31 / 95 (510) | 73 / 158 |
| 131,072 | 98,304 | 50 | R1+R2+R3+R4 | 364,748 | 564,311 | 673 | 80.4% | 145 | 32,918,726 (+124.7%) | +72.1% | 25 / 82 (489) | 61 / 131 |
| 150,000 | 112,500 | any | R1 | 403,690 | 689,965 | 656 | 68.7% | 10 | 2,080,479 (+7.9%) | +4.2% | 3 / 5 (51) | 3 / 5 |
| 150,000 | 112,500 | any | R1+R2 | 402,773 | 635,089 | 656 | 68.7% | 13 | 1,973,325 (+7.5%) | +2.3% | 3 / 5 (51) | 3 / 5 |
| 150,000 | 112,500 | 10 | R1+R2+R3 | 372,984 | 579,223 | 656 | 68.7% | 18 | 1,574,896 (+6.0%) | -1.0% | 25 / 83 (439) | 61 / 131 |
| 150,000 | 112,500 | 20 | R1+R2+R3 | 372,984 | 579,223 | 656 | 68.7% | 26 | 3,032,264 (+11.5%) | +2.4% | 25 / 79 (439) | 54 / 125 |
| 150,000 | 112,500 | 50 | R1+R2+R3 | 374,778 | 580,633 | 656 | 68.7% | 138 | 31,445,845 (+119.1%) | +69.1% | 20 / 70 (423) | 47 / 111 |
| 150,000 | 112,500 | 10 | R1+R2+R3+R4 | 364,748 | 561,272 | 656 | 68.7% | 18 | 1,217,447 (+4.6%) | -2.3% | 31 / 99 (510) | 79 / 164 |
| 150,000 | 112,500 | 20 | R1+R2+R3+R4 | 364,748 | 561,272 | 656 | 68.7% | 26 | 2,674,814 (+10.1%) | +1.1% | 31 / 95 (510) | 73 / 158 |
| 150,000 | 112,500 | 50 | R1+R2+R3+R4 | 364,748 | 564,311 | 656 | 68.7% | 145 | 32,918,726 (+124.7%) | +72.1% | 25 / 82 (489) | 61 / 131 |
| 200,000 | 150,000 | any | R1 | 403,690 | 689,965 | 588 | 41.4% | 10 | 2,080,479 (+7.9%) | +4.2% | 3 / 5 (51) | 3 / 5 |
| 200,000 | 150,000 | any | R1+R2 | 402,773 | 635,089 | 588 | 41.4% | 13 | 1,973,325 (+7.5%) | +2.3% | 3 / 5 (51) | 3 / 5 |
| 200,000 | 150,000 | 10 | R1+R2+R3 | 372,984 | 579,223 | 588 | 41.4% | 18 | 1,574,896 (+6.0%) | -1.0% | 25 / 83 (439) | 61 / 131 |
| 200,000 | 150,000 | 20 | R1+R2+R3 | 372,984 | 579,223 | 588 | 41.4% | 26 | 3,032,264 (+11.5%) | +2.4% | 25 / 79 (439) | 54 / 125 |
| 200,000 | 150,000 | 50 | R1+R2+R3 | 374,778 | 580,633 | 588 | 41.4% | 138 | 31,445,845 (+119.1%) | +69.1% | 20 / 70 (423) | 47 / 111 |
| 200,000 | 150,000 | 10 | R1+R2+R3+R4 | 364,748 | 561,272 | 588 | 41.4% | 18 | 1,217,447 (+4.6%) | -2.3% | 31 / 99 (510) | 79 / 164 |
| 200,000 | 150,000 | 20 | R1+R2+R3+R4 | 364,748 | 561,272 | 588 | 41.4% | 26 | 2,674,814 (+10.1%) | +1.1% | 31 / 95 (510) | 73 / 158 |
| 200,000 | 150,000 | 50 | R1+R2+R3+R4 | 364,748 | 564,311 | 588 | 41.4% | 145 | 32,918,726 (+124.7%) | +72.1% | 25 / 82 (489) | 61 / 131 |
| 200,000 | 120,000 | any | R1 | 403,690 | 689,965 | 588 | 41.4% | 10 | 2,080,479 (+7.9%) | +4.2% | 3 / 5 (51) | 3 / 5 |
| 200,000 | 120,000 | any | R1+R2 | 402,773 | 635,089 | 588 | 41.4% | 13 | 1,973,325 (+7.5%) | +2.3% | 3 / 5 (51) | 3 / 5 |
| 200,000 | 120,000 | 10 | R1+R2+R3 | 372,984 | 579,223 | 588 | 41.4% | 18 | 1,574,896 (+6.0%) | -1.0% | 25 / 83 (439) | 61 / 131 |
| 200,000 | 120,000 | 20 | R1+R2+R3 | 372,984 | 579,223 | 588 | 41.4% | 26 | 3,032,264 (+11.5%) | +2.4% | 25 / 79 (439) | 54 / 125 |
| 200,000 | 120,000 | 50 | R1+R2+R3 | 374,778 | 580,633 | 588 | 41.4% | 138 | 31,445,845 (+119.1%) | +69.1% | 20 / 70 (423) | 47 / 111 |
| 200,000 | 120,000 | 10 | R1+R2+R3+R4 | 364,748 | 561,272 | 588 | 41.4% | 18 | 1,217,447 (+4.6%) | -2.3% | 31 / 99 (510) | 79 / 164 |
| 200,000 | 120,000 | 20 | R1+R2+R3+R4 | 364,748 | 561,272 | 588 | 41.4% | 26 | 2,674,814 (+10.1%) | +1.1% | 31 / 95 (510) | 73 / 158 |
| 200,000 | 120,000 | 50 | R1+R2+R3+R4 | 364,748 | 564,311 | 588 | 41.4% | 145 | 32,918,726 (+124.7%) | +72.1% | 25 / 82 (489) | 61 / 131 |
| 250,000 | 187,500 | any | R1 | 403,690 | 689,965 | 529 | 27.0% | 10 | 2,080,479 (+7.9%) | +4.2% | 3 / 5 (51) | 3 / 5 |
| 250,000 | 187,500 | any | R1+R2 | 402,773 | 635,089 | 529 | 27.0% | 13 | 1,973,325 (+7.5%) | +2.3% | 3 / 5 (51) | 3 / 5 |
| 250,000 | 187,500 | 10 | R1+R2+R3 | 372,984 | 579,223 | 529 | 27.0% | 18 | 1,574,896 (+6.0%) | -1.0% | 25 / 83 (439) | 61 / 131 |
| 250,000 | 187,500 | 20 | R1+R2+R3 | 372,984 | 579,223 | 529 | 27.0% | 26 | 3,032,264 (+11.5%) | +2.4% | 25 / 79 (439) | 54 / 125 |
| 250,000 | 187,500 | 50 | R1+R2+R3 | 374,778 | 580,633 | 529 | 27.0% | 138 | 31,445,845 (+119.1%) | +69.1% | 20 / 70 (423) | 47 / 111 |
| 250,000 | 187,500 | 10 | R1+R2+R3+R4 | 364,748 | 561,272 | 529 | 27.0% | 18 | 1,217,447 (+4.6%) | -2.3% | 31 / 99 (510) | 79 / 164 |
| 250,000 | 187,500 | 20 | R1+R2+R3+R4 | 364,748 | 561,272 | 529 | 27.0% | 26 | 2,674,814 (+10.1%) | +1.1% | 31 / 95 (510) | 73 / 158 |
| 250,000 | 187,500 | 50 | R1+R2+R3+R4 | 364,748 | 564,311 | 529 | 27.0% | 145 | 32,918,726 (+124.7%) | +72.1% | 25 / 82 (489) | 61 / 131 |

#### a88c7c57f2fa2a96b, turn unit request (my addition)
| B | L | A | rules | median | p90 | >B | prot>B | trims | net units @0.05 (% real) | % real @0.1 | UAA@20 / @H (scored) | vis@20 / @H |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 100,000 | 75,000 | any | R1 | 395,165 | 686,593 | 701 | 44.9% | 48 | 2,706,117 (+10.3%) | +5.0% | 3 / 6 (64) | 3 / 7 |
| 100,000 | 75,000 | any | R1+R2 | 336,618 | 621,386 | 701 | 44.9% | 226 | 2,386,499 (+9.0%) | +0.1% | 3 / 6 (64) | 3 / 7 |
| 100,000 | 75,000 | 10 | R1+R2+R3 | 268,211 | 504,957 | 701 | 44.9% | 630 | 19,876,079 (+75.3%) | +35.1% | 57 / 160 (674) | 126 / 270 |
| 100,000 | 75,000 | 20 | R1+R2+R3 | 275,656 | 515,900 | 701 | 44.9% | 608 | 38,141,030 (+144.5%) | +78.5% | 49 / 138 (643) | 95 / 225 |
| 100,000 | 75,000 | 50 | R1+R2+R3 | 296,597 | 551,770 | 701 | 44.9% | 563 | 78,709,699 (+298.2%) | +175.1% | 31 / 95 (550) | 55 / 144 |
| 100,000 | 75,000 | 10 | R1+R2+R3+R4 | 253,325 | 472,579 | 701 | 44.9% | 644 | 19,745,176 (+74.8%) | +33.3% | 70 / 194 (786) | 187 / 355 |
| 100,000 | 75,000 | 20 | R1+R2+R3+R4 | 265,503 | 486,893 | 701 | 44.9% | 621 | 38,970,821 (+147.6%) | +79.2% | 61 / 164 (749) | 128 / 289 |
| 100,000 | 75,000 | 50 | R1+R2+R3+R4 | 293,990 | 531,487 | 701 | 44.9% | 573 | 81,099,799 (+307.3%) | +180.0% | 36 / 109 (636) | 71 / 174 |
| 131,072 | 98,304 | any | R1 | 395,165 | 686,593 | 673 | 1.7% | 48 | 2,706,117 (+10.3%) | +5.0% | 3 / 6 (64) | 3 / 7 |
| 131,072 | 98,304 | any | R1+R2 | 336,618 | 621,386 | 673 | 1.7% | 226 | 2,394,636 (+9.1%) | +0.1% | 3 / 6 (64) | 3 / 7 |
| 131,072 | 98,304 | 10 | R1+R2+R3 | 268,211 | 504,957 | 658 | 1.7% | 604 | 19,172,727 (+72.6%) | +33.4% | 61 / 162 (674) | 129 / 273 |
| 131,072 | 98,304 | 20 | R1+R2+R3 | 275,656 | 515,900 | 670 | 1.7% | 606 | 38,044,462 (+144.1%) | +78.2% | 49 / 138 (643) | 95 / 225 |
| 131,072 | 98,304 | 50 | R1+R2+R3 | 296,597 | 551,770 | 673 | 1.7% | 563 | 78,717,836 (+298.2%) | +175.1% | 31 / 95 (550) | 55 / 144 |
| 131,072 | 98,304 | 10 | R1+R2+R3+R4 | 253,325 | 472,579 | 658 | 1.7% | 618 | 19,041,824 (+72.1%) | +31.7% | 74 / 196 (786) | 190 / 358 |
| 131,072 | 98,304 | 20 | R1+R2+R3+R4 | 265,503 | 486,893 | 670 | 1.7% | 619 | 38,874,253 (+147.3%) | +79.0% | 61 / 164 (749) | 128 / 289 |
| 131,072 | 98,304 | 50 | R1+R2+R3+R4 | 293,990 | 531,487 | 673 | 1.7% | 573 | 81,107,936 (+307.3%) | +180.1% | 36 / 109 (636) | 71 / 174 |
| 150,000 | 112,500 | any | R1 | 395,165 | 686,593 | 651 | 0.6% | 48 | 2,706,117 (+10.3%) | +5.0% | 3 / 6 (64) | 3 / 7 |
| 150,000 | 112,500 | any | R1+R2 | 336,618 | 621,386 | 650 | 0.6% | 221 | 2,350,243 (+8.9%) | +0.0% | 3 / 6 (64) | 3 / 7 |
| 150,000 | 112,500 | 10 | R1+R2+R3 | 268,211 | 504,957 | 619 | 0.6% | 575 | 18,796,242 (+71.2%) | +32.6% | 59 / 163 (674) | 128 / 277 |
| 150,000 | 112,500 | 20 | R1+R2+R3 | 275,656 | 515,900 | 623 | 0.6% | 566 | 36,697,858 (+139.0%) | +75.1% | 49 / 141 (643) | 95 / 232 |
| 150,000 | 112,500 | 50 | R1+R2+R3 | 296,597 | 551,770 | 650 | 0.6% | 558 | 78,673,443 (+298.1%) | +175.0% | 31 / 95 (550) | 55 / 144 |
| 150,000 | 112,500 | 10 | R1+R2+R3+R4 | 253,325 | 472,579 | 619 | 0.6% | 589 | 18,665,339 (+70.7%) | +30.9% | 72 / 197 (786) | 189 / 362 |
| 150,000 | 112,500 | 20 | R1+R2+R3+R4 | 265,503 | 486,893 | 623 | 0.6% | 579 | 37,527,649 (+142.2%) | +75.8% | 61 / 167 (749) | 128 / 296 |
| 150,000 | 112,500 | 50 | R1+R2+R3+R4 | 293,990 | 531,487 | 650 | 0.6% | 568 | 81,063,543 (+307.1%) | +180.0% | 36 / 109 (636) | 71 / 174 |
| 200,000 | 150,000 | any | R1 | 395,165 | 686,593 | 588 | 0.0% | 47 | 2,748,082 (+10.4%) | +5.1% | 3 / 6 (64) | 3 / 7 |
| 200,000 | 150,000 | any | R1+R2 | 336,618 | 621,386 | 568 | 0.0% | 187 | 2,129,484 (+8.1%) | -0.5% | 3 / 6 (64) | 3 / 7 |
| 200,000 | 150,000 | 10 | R1+R2+R3 | 268,211 | 504,957 | 507 | 0.0% | 481 | 16,533,637 (+62.6%) | +27.6% | 49 / 161 (674) | 114 / 275 |
| 200,000 | 150,000 | 20 | R1+R2+R3 | 275,656 | 515,900 | 528 | 0.0% | 484 | 34,278,410 (+129.9%) | +69.7% | 47 / 140 (643) | 98 / 236 |
| 200,000 | 150,000 | 50 | R1+R2+R3 | 296,597 | 551,770 | 561 | 0.0% | 501 | 76,745,203 (+290.8%) | +170.6% | 31 / 95 (550) | 57 / 148 |
| 200,000 | 150,000 | 10 | R1+R2+R3+R4 | 253,325 | 472,579 | 497 | 0.0% | 485 | 16,169,988 (+61.3%) | +25.3% | 63 / 197 (786) | 175 / 362 |
| 200,000 | 150,000 | 20 | R1+R2+R3+R4 | 265,503 | 486,893 | 517 | 0.0% | 488 | 34,783,176 (+131.8%) | +69.6% | 59 / 167 (749) | 131 / 300 |
| 200,000 | 150,000 | 50 | R1+R2+R3+R4 | 293,990 | 531,487 | 561 | 0.0% | 511 | 79,135,302 (+299.8%) | +175.5% | 36 / 109 (636) | 73 / 178 |
| 200,000 | 120,000 | any | R1 | 395,165 | 686,593 | 588 | 0.0% | 47 | 2,748,082 (+10.4%) | +5.1% | 3 / 6 (64) | 3 / 7 |
| 200,000 | 120,000 | any | R1+R2 | 336,618 | 621,386 | 568 | 0.0% | 187 | 2,129,484 (+8.1%) | -0.5% | 3 / 6 (64) | 3 / 7 |
| 200,000 | 120,000 | 10 | R1+R2+R3 | 268,211 | 504,957 | 507 | 0.0% | 481 | 16,533,637 (+62.6%) | +27.6% | 49 / 161 (674) | 114 / 275 |
| 200,000 | 120,000 | 20 | R1+R2+R3 | 275,656 | 515,900 | 528 | 0.0% | 484 | 34,278,410 (+129.9%) | +69.7% | 47 / 140 (643) | 98 / 236 |
| 200,000 | 120,000 | 50 | R1+R2+R3 | 296,597 | 551,770 | 561 | 0.0% | 501 | 76,745,203 (+290.8%) | +170.6% | 31 / 95 (550) | 57 / 148 |
| 200,000 | 120,000 | 10 | R1+R2+R3+R4 | 253,325 | 472,579 | 497 | 0.0% | 485 | 16,169,988 (+61.3%) | +25.3% | 63 / 197 (786) | 175 / 362 |
| 200,000 | 120,000 | 20 | R1+R2+R3+R4 | 265,503 | 486,893 | 517 | 0.0% | 488 | 34,783,176 (+131.8%) | +69.6% | 59 / 167 (749) | 131 / 300 |
| 200,000 | 120,000 | 50 | R1+R2+R3+R4 | 293,990 | 531,487 | 561 | 0.0% | 511 | 79,135,302 (+299.8%) | +175.5% | 36 / 109 (636) | 73 / 178 |
| 250,000 | 187,500 | any | R1 | 395,165 | 686,593 | 527 | 0.0% | 46 | 2,790,974 (+10.6%) | +5.2% | 3 / 6 (64) | 3 / 7 |
| 250,000 | 187,500 | any | R1+R2 | 336,618 | 621,386 | 495 | 0.0% | 154 | 1,999,183 (+7.6%) | -0.6% | 3 / 6 (64) | 3 / 7 |
| 250,000 | 187,500 | 10 | R1+R2+R3 | 268,211 | 504,957 | 414 | 0.0% | 389 | 12,959,521 (+49.1%) | +19.7% | 54 / 158 (674) | 118 / 272 |
| 250,000 | 187,500 | 20 | R1+R2+R3 | 275,656 | 515,900 | 423 | 0.0% | 397 | 27,869,987 (+105.6%) | +55.0% | 42 / 136 (643) | 87 / 232 |
| 250,000 | 187,500 | 50 | R1+R2+R3 | 296,597 | 551,770 | 484 | 0.0% | 438 | 72,450,955 (+274.5%) | +160.7% | 30 / 96 (550) | 53 / 148 |
| 250,000 | 187,500 | 10 | R1+R2+R3+R4 | 253,325 | 472,579 | 373 | 0.0% | 376 | 11,756,878 (+44.5%) | +15.5% | 65 / 191 (786) | 177 / 358 |
| 250,000 | 187,500 | 20 | R1+R2+R3+R4 | 265,503 | 486,893 | 403 | 0.0% | 395 | 27,808,390 (+105.4%) | +53.7% | 54 / 164 (749) | 121 / 300 |
| 250,000 | 187,500 | 50 | R1+R2+R3+R4 | 293,990 | 531,487 | 484 | 0.0% | 448 | 74,837,834 (+283.5%) | +165.7% | 35 / 111 (636) | 69 / 179 |

#### a4920ba3ae772b9d0, turn unit promptId
| B | L | A | rules | median | p90 | >B | prot>B | trims | net units @0.05 (% real) | % real @0.1 | UAA@20 / @H (scored) | vis@20 / @H |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 100,000 | 75,000 | any | R1 | 406,015 | 723,596 | 659 | 93.1% | 2 | 645,620 (+2.7%) | +1.6% | 0 / 0 (10) | 0 / 0 |
| 100,000 | 75,000 | any | R1+R2 | 406,015 | 716,059 | 659 | 93.1% | 3 | 957,506 (+4.0%) | +2.2% | 0 / 0 (10) | 0 / 0 |
| 100,000 | 75,000 | 10 | R1+R2+R3 | 406,015 | 641,441 | 659 | 93.1% | 5 | 309,018 (+1.3%) | -2.0% | 11 / 48 (178) | 18 / 74 |
| 100,000 | 75,000 | 20 | R1+R2+R3 | 406,015 | 641,441 | 659 | 93.1% | 5 | 309,018 (+1.3%) | -2.0% | 11 / 48 (178) | 18 / 74 |
| 100,000 | 75,000 | 50 | R1+R2+R3 | 406,015 | 641,441 | 659 | 93.1% | 8 | 806,778 (+3.4%) | -0.7% | 10 / 47 (178) | 17 / 73 |
| 100,000 | 75,000 | 10 | R1+R2+R3+R4 | 402,855 | 629,113 | 659 | 93.1% | 5 | 115,194 (+0.5%) | -3.0% | 13 / 54 (196) | 22 / 94 |
| 100,000 | 75,000 | 20 | R1+R2+R3+R4 | 402,855 | 629,113 | 659 | 93.1% | 5 | 115,194 (+0.5%) | -3.0% | 13 / 54 (196) | 22 / 94 |
| 100,000 | 75,000 | 50 | R1+R2+R3+R4 | 402,855 | 629,113 | 659 | 93.1% | 10 | 965,738 (+4.1%) | -0.8% | 12 / 53 (196) | 21 / 93 |
| 131,072 | 98,304 | any | R1 | 406,015 | 723,596 | 620 | 85.6% | 2 | 645,620 (+2.7%) | +1.6% | 0 / 0 (10) | 0 / 0 |
| 131,072 | 98,304 | any | R1+R2 | 406,015 | 716,059 | 620 | 85.6% | 3 | 957,506 (+4.0%) | +2.2% | 0 / 0 (10) | 0 / 0 |
| 131,072 | 98,304 | 10 | R1+R2+R3 | 406,015 | 641,441 | 620 | 85.6% | 5 | 309,018 (+1.3%) | -2.0% | 11 / 48 (178) | 18 / 74 |
| 131,072 | 98,304 | 20 | R1+R2+R3 | 406,015 | 641,441 | 620 | 85.6% | 5 | 309,018 (+1.3%) | -2.0% | 11 / 48 (178) | 18 / 74 |
| 131,072 | 98,304 | 50 | R1+R2+R3 | 406,015 | 641,441 | 620 | 85.6% | 8 | 806,778 (+3.4%) | -0.7% | 10 / 47 (178) | 17 / 73 |
| 131,072 | 98,304 | 10 | R1+R2+R3+R4 | 402,855 | 629,113 | 620 | 85.6% | 5 | 115,194 (+0.5%) | -3.0% | 13 / 54 (196) | 22 / 94 |
| 131,072 | 98,304 | 20 | R1+R2+R3+R4 | 402,855 | 629,113 | 620 | 85.6% | 5 | 115,194 (+0.5%) | -3.0% | 13 / 54 (196) | 22 / 94 |
| 131,072 | 98,304 | 50 | R1+R2+R3+R4 | 402,855 | 629,113 | 620 | 85.6% | 10 | 965,738 (+4.1%) | -0.8% | 12 / 53 (196) | 21 / 93 |
| 150,000 | 112,500 | any | R1 | 406,015 | 723,596 | 597 | 81.9% | 2 | 645,620 (+2.7%) | +1.6% | 0 / 0 (10) | 0 / 0 |
| 150,000 | 112,500 | any | R1+R2 | 406,015 | 716,059 | 597 | 81.9% | 3 | 957,506 (+4.0%) | +2.2% | 0 / 0 (10) | 0 / 0 |
| 150,000 | 112,500 | 10 | R1+R2+R3 | 406,015 | 641,441 | 597 | 81.9% | 5 | 309,018 (+1.3%) | -2.0% | 11 / 48 (178) | 18 / 74 |
| 150,000 | 112,500 | 20 | R1+R2+R3 | 406,015 | 641,441 | 597 | 81.9% | 5 | 309,018 (+1.3%) | -2.0% | 11 / 48 (178) | 18 / 74 |
| 150,000 | 112,500 | 50 | R1+R2+R3 | 406,015 | 641,441 | 597 | 81.9% | 8 | 806,778 (+3.4%) | -0.7% | 10 / 47 (178) | 17 / 73 |
| 150,000 | 112,500 | 10 | R1+R2+R3+R4 | 402,855 | 629,113 | 597 | 81.9% | 5 | 115,194 (+0.5%) | -3.0% | 13 / 54 (196) | 22 / 94 |
| 150,000 | 112,500 | 20 | R1+R2+R3+R4 | 402,855 | 629,113 | 597 | 81.9% | 5 | 115,194 (+0.5%) | -3.0% | 13 / 54 (196) | 22 / 94 |
| 150,000 | 112,500 | 50 | R1+R2+R3+R4 | 402,855 | 629,113 | 597 | 81.9% | 10 | 965,738 (+4.1%) | -0.8% | 12 / 53 (196) | 21 / 93 |
| 200,000 | 150,000 | any | R1 | 406,015 | 723,596 | 552 | 53.2% | 2 | 645,620 (+2.7%) | +1.6% | 0 / 0 (10) | 0 / 0 |
| 200,000 | 150,000 | any | R1+R2 | 406,015 | 716,059 | 552 | 53.2% | 3 | 957,506 (+4.0%) | +2.2% | 0 / 0 (10) | 0 / 0 |
| 200,000 | 150,000 | 10 | R1+R2+R3 | 406,015 | 641,441 | 552 | 53.2% | 5 | 309,018 (+1.3%) | -2.0% | 11 / 48 (178) | 18 / 74 |
| 200,000 | 150,000 | 20 | R1+R2+R3 | 406,015 | 641,441 | 552 | 53.2% | 5 | 309,018 (+1.3%) | -2.0% | 11 / 48 (178) | 18 / 74 |
| 200,000 | 150,000 | 50 | R1+R2+R3 | 406,015 | 641,441 | 552 | 53.2% | 8 | 806,778 (+3.4%) | -0.7% | 10 / 47 (178) | 17 / 73 |
| 200,000 | 150,000 | 10 | R1+R2+R3+R4 | 402,855 | 629,113 | 552 | 53.2% | 5 | 115,194 (+0.5%) | -3.0% | 13 / 54 (196) | 22 / 94 |
| 200,000 | 150,000 | 20 | R1+R2+R3+R4 | 402,855 | 629,113 | 552 | 53.2% | 5 | 115,194 (+0.5%) | -3.0% | 13 / 54 (196) | 22 / 94 |
| 200,000 | 150,000 | 50 | R1+R2+R3+R4 | 402,855 | 629,113 | 552 | 53.2% | 10 | 965,738 (+4.1%) | -0.8% | 12 / 53 (196) | 21 / 93 |
| 200,000 | 120,000 | any | R1 | 406,015 | 723,596 | 552 | 53.2% | 2 | 645,620 (+2.7%) | +1.6% | 0 / 0 (10) | 0 / 0 |
| 200,000 | 120,000 | any | R1+R2 | 406,015 | 716,059 | 552 | 53.2% | 3 | 957,506 (+4.0%) | +2.2% | 0 / 0 (10) | 0 / 0 |
| 200,000 | 120,000 | 10 | R1+R2+R3 | 406,015 | 641,441 | 552 | 53.2% | 5 | 309,018 (+1.3%) | -2.0% | 11 / 48 (178) | 18 / 74 |
| 200,000 | 120,000 | 20 | R1+R2+R3 | 406,015 | 641,441 | 552 | 53.2% | 5 | 309,018 (+1.3%) | -2.0% | 11 / 48 (178) | 18 / 74 |
| 200,000 | 120,000 | 50 | R1+R2+R3 | 406,015 | 641,441 | 552 | 53.2% | 8 | 806,778 (+3.4%) | -0.7% | 10 / 47 (178) | 17 / 73 |
| 200,000 | 120,000 | 10 | R1+R2+R3+R4 | 402,855 | 629,113 | 552 | 53.2% | 5 | 115,194 (+0.5%) | -3.0% | 13 / 54 (196) | 22 / 94 |
| 200,000 | 120,000 | 20 | R1+R2+R3+R4 | 402,855 | 629,113 | 552 | 53.2% | 5 | 115,194 (+0.5%) | -3.0% | 13 / 54 (196) | 22 / 94 |
| 200,000 | 120,000 | 50 | R1+R2+R3+R4 | 402,855 | 629,113 | 552 | 53.2% | 10 | 965,738 (+4.1%) | -0.8% | 12 / 53 (196) | 21 / 93 |
| 250,000 | 187,500 | any | R1 | 406,015 | 723,596 | 491 | 30.4% | 2 | 645,620 (+2.7%) | +1.6% | 0 / 0 (10) | 0 / 0 |
| 250,000 | 187,500 | any | R1+R2 | 406,015 | 716,059 | 491 | 30.4% | 3 | 957,506 (+4.0%) | +2.2% | 0 / 0 (10) | 0 / 0 |
| 250,000 | 187,500 | 10 | R1+R2+R3 | 406,015 | 641,441 | 491 | 30.4% | 5 | 309,018 (+1.3%) | -2.0% | 11 / 48 (178) | 18 / 74 |
| 250,000 | 187,500 | 20 | R1+R2+R3 | 406,015 | 641,441 | 491 | 30.4% | 5 | 309,018 (+1.3%) | -2.0% | 11 / 48 (178) | 18 / 74 |
| 250,000 | 187,500 | 50 | R1+R2+R3 | 406,015 | 641,441 | 491 | 30.4% | 8 | 806,778 (+3.4%) | -0.7% | 10 / 47 (178) | 17 / 73 |
| 250,000 | 187,500 | 10 | R1+R2+R3+R4 | 402,855 | 629,113 | 491 | 30.4% | 5 | 115,194 (+0.5%) | -3.0% | 13 / 54 (196) | 22 / 94 |
| 250,000 | 187,500 | 20 | R1+R2+R3+R4 | 402,855 | 629,113 | 491 | 30.4% | 5 | 115,194 (+0.5%) | -3.0% | 13 / 54 (196) | 22 / 94 |
| 250,000 | 187,500 | 50 | R1+R2+R3+R4 | 402,855 | 629,113 | 491 | 30.4% | 10 | 965,738 (+4.1%) | -0.8% | 12 / 53 (196) | 21 / 93 |

#### a4920ba3ae772b9d0, turn unit request (my addition)
| B | L | A | rules | median | p90 | >B | prot>B | trims | net units @0.05 (% real) | % real @0.1 | UAA@20 / @H (scored) | vis@20 / @H |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 100,000 | 75,000 | any | R1 | 403,824 | 719,877 | 659 | 29.3% | 16 | 654,891 (+2.7%) | +1.4% | 0 / 2 (19) | 0 / 2 |
| 100,000 | 75,000 | any | R1+R2 | 401,990 | 696,293 | 659 | 29.3% | 49 | 773,870 (+3.2%) | +1.2% | 0 / 2 (19) | 0 / 2 |
| 100,000 | 75,000 | 10 | R1+R2+R3 | 307,501 | 553,208 | 650 | 29.3% | 562 | 17,056,234 (+71.6%) | +34.4% | 57 / 171 (578) | 108 / 267 |
| 100,000 | 75,000 | 20 | R1+R2+R3 | 310,704 | 556,324 | 659 | 29.3% | 537 | 34,582,748 (+145.2%) | +79.6% | 45 / 147 (555) | 97 / 231 |
| 100,000 | 75,000 | 50 | R1+R2+R3 | 347,725 | 582,628 | 659 | 29.3% | 472 | 77,890,218 (+327.0%) | +191.6% | 25 / 100 (482) | 49 / 164 |
| 100,000 | 75,000 | 10 | R1+R2+R3+R4 | 294,775 | 493,389 | 650 | 29.3% | 597 | 17,564,108 (+73.7%) | +33.4% | 73 / 206 (677) | 172 / 361 |
| 100,000 | 75,000 | 20 | R1+R2+R3+R4 | 305,216 | 503,902 | 659 | 29.3% | 572 | 36,200,404 (+152.0%) | +81.7% | 60 / 174 (647) | 152 / 306 |
| 100,000 | 75,000 | 50 | R1+R2+R3+R4 | 344,101 | 545,954 | 659 | 29.3% | 495 | 81,232,858 (+341.0%) | +198.8% | 31 / 114 (554) | 69 / 201 |
| 131,072 | 98,304 | any | R1 | 403,824 | 719,877 | 620 | 0.7% | 16 | 654,891 (+2.7%) | +1.4% | 0 / 2 (19) | 0 / 2 |
| 131,072 | 98,304 | any | R1+R2 | 401,990 | 696,293 | 620 | 0.7% | 49 | 773,870 (+3.2%) | +1.2% | 0 / 2 (19) | 0 / 2 |
| 131,072 | 98,304 | 10 | R1+R2+R3 | 307,501 | 553,208 | 597 | 0.7% | 521 | 16,120,996 (+67.7%) | +32.1% | 55 / 171 (578) | 107 / 268 |
| 131,072 | 98,304 | 20 | R1+R2+R3 | 310,704 | 556,324 | 611 | 0.7% | 518 | 33,937,180 (+142.5%) | +78.0% | 45 / 147 (555) | 97 / 231 |
| 131,072 | 98,304 | 50 | R1+R2+R3 | 347,725 | 582,628 | 620 | 0.7% | 472 | 77,890,218 (+327.0%) | +191.6% | 25 / 100 (482) | 49 / 164 |
| 131,072 | 98,304 | 10 | R1+R2+R3+R4 | 294,775 | 493,389 | 594 | 0.7% | 553 | 16,559,136 (+69.5%) | +30.9% | 73 / 206 (677) | 173 / 362 |
| 131,072 | 98,304 | 20 | R1+R2+R3+R4 | 305,216 | 503,902 | 611 | 0.7% | 553 | 35,554,268 (+149.3%) | +80.1% | 59 / 173 (647) | 151 / 306 |
| 131,072 | 98,304 | 50 | R1+R2+R3+R4 | 344,101 | 545,954 | 620 | 0.7% | 495 | 81,232,858 (+341.0%) | +198.8% | 31 / 114 (554) | 69 / 201 |
| 150,000 | 112,500 | any | R1 | 403,824 | 719,877 | 597 | 0.0% | 16 | 654,891 (+2.7%) | +1.4% | 0 / 2 (19) | 0 / 2 |
| 150,000 | 112,500 | any | R1+R2 | 401,990 | 696,293 | 597 | 0.0% | 49 | 781,408 (+3.3%) | +1.2% | 0 / 2 (19) | 0 / 2 |
| 150,000 | 112,500 | 10 | R1+R2+R3 | 307,501 | 553,208 | 569 | 0.0% | 501 | 15,595,480 (+65.5%) | +30.8% | 62 / 174 (578) | 114 / 271 |
| 150,000 | 112,500 | 20 | R1+R2+R3 | 310,704 | 556,324 | 579 | 0.0% | 493 | 32,604,173 (+136.9%) | +74.6% | 46 / 147 (555) | 98 / 231 |
| 150,000 | 112,500 | 50 | R1+R2+R3 | 347,725 | 582,628 | 597 | 0.0% | 472 | 77,897,756 (+327.0%) | +191.6% | 25 / 100 (482) | 49 / 164 |
| 150,000 | 112,500 | 10 | R1+R2+R3+R4 | 294,775 | 493,389 | 567 | 0.0% | 533 | 16,018,229 (+67.3%) | +29.6% | 80 / 208 (677) | 182 / 364 |
| 150,000 | 112,500 | 20 | R1+R2+R3+R4 | 305,216 | 503,902 | 577 | 0.0% | 528 | 34,223,219 (+143.7%) | +76.7% | 60 / 173 (647) | 152 / 306 |
| 150,000 | 112,500 | 50 | R1+R2+R3+R4 | 344,101 | 545,954 | 597 | 0.0% | 495 | 81,240,397 (+341.1%) | +198.8% | 31 / 114 (554) | 69 / 201 |
| 200,000 | 150,000 | any | R1 | 403,824 | 719,877 | 552 | 0.0% | 16 | 654,891 (+2.7%) | +1.4% | 0 / 2 (19) | 0 / 2 |
| 200,000 | 150,000 | any | R1+R2 | 401,990 | 696,293 | 552 | 0.0% | 48 | 829,572 (+3.5%) | +1.4% | 0 / 2 (19) | 0 / 2 |
| 200,000 | 150,000 | 10 | R1+R2+R3 | 307,501 | 553,208 | 490 | 0.0% | 433 | 13,433,880 (+56.4%) | +25.5% | 59 / 179 (578) | 118 / 270 |
| 200,000 | 150,000 | 20 | R1+R2+R3 | 310,704 | 556,324 | 502 | 0.0% | 437 | 29,589,905 (+124.2%) | +67.1% | 40 / 151 (555) | 101 / 236 |
| 200,000 | 150,000 | 50 | R1+R2+R3 | 347,725 | 582,628 | 539 | 0.0% | 452 | 75,739,342 (+318.0%) | +186.1% | 22 / 100 (482) | 46 / 164 |
| 200,000 | 150,000 | 10 | R1+R2+R3+R4 | 294,775 | 493,389 | 483 | 0.0% | 459 | 13,588,455 (+57.0%) | +23.7% | 75 / 215 (677) | 187 / 369 |
| 200,000 | 150,000 | 20 | R1+R2+R3+R4 | 305,216 | 503,902 | 501 | 0.0% | 469 | 31,020,017 (+130.2%) | +68.7% | 54 / 179 (647) | 155 / 312 |
| 200,000 | 150,000 | 50 | R1+R2+R3+R4 | 344,101 | 545,954 | 538 | 0.0% | 475 | 79,081,360 (+332.0%) | +193.3% | 28 / 114 (554) | 66 / 201 |
| 200,000 | 120,000 | any | R1 | 403,824 | 719,877 | 552 | 0.0% | 16 | 654,891 (+2.7%) | +1.4% | 0 / 2 (19) | 0 / 2 |
| 200,000 | 120,000 | any | R1+R2 | 401,990 | 696,293 | 552 | 0.0% | 48 | 829,572 (+3.5%) | +1.4% | 0 / 2 (19) | 0 / 2 |
| 200,000 | 120,000 | 10 | R1+R2+R3 | 307,501 | 553,208 | 490 | 0.0% | 433 | 13,433,880 (+56.4%) | +25.5% | 59 / 179 (578) | 118 / 270 |
| 200,000 | 120,000 | 20 | R1+R2+R3 | 310,704 | 556,324 | 502 | 0.0% | 437 | 29,589,905 (+124.2%) | +67.1% | 40 / 151 (555) | 101 / 236 |
| 200,000 | 120,000 | 50 | R1+R2+R3 | 347,725 | 582,628 | 539 | 0.0% | 452 | 75,739,342 (+318.0%) | +186.1% | 22 / 100 (482) | 46 / 164 |
| 200,000 | 120,000 | 10 | R1+R2+R3+R4 | 294,775 | 493,389 | 483 | 0.0% | 459 | 13,588,455 (+57.0%) | +23.7% | 75 / 215 (677) | 187 / 369 |
| 200,000 | 120,000 | 20 | R1+R2+R3+R4 | 305,216 | 503,902 | 501 | 0.0% | 469 | 31,020,017 (+130.2%) | +68.7% | 54 / 179 (647) | 155 / 312 |
| 200,000 | 120,000 | 50 | R1+R2+R3+R4 | 344,101 | 545,954 | 538 | 0.0% | 475 | 79,081,360 (+332.0%) | +193.3% | 28 / 114 (554) | 66 / 201 |
| 250,000 | 187,500 | any | R1 | 403,824 | 719,877 | 491 | 0.0% | 16 | 654,891 (+2.7%) | +1.4% | 0 / 2 (19) | 0 / 2 |
| 250,000 | 187,500 | any | R1+R2 | 401,990 | 696,293 | 491 | 0.0% | 48 | 885,968 (+3.7%) | +1.5% | 0 / 2 (19) | 0 / 2 |
| 250,000 | 187,500 | 10 | R1+R2+R3 | 307,501 | 553,208 | 422 | 0.0% | 368 | 11,295,778 (+47.4%) | +20.6% | 72 / 177 (578) | 134 / 272 |
| 250,000 | 187,500 | 20 | R1+R2+R3 | 310,704 | 556,324 | 432 | 0.0% | 373 | 25,152,642 (+105.6%) | +56.2% | 54 / 155 (555) | 110 / 240 |
| 250,000 | 187,500 | 50 | R1+R2+R3 | 347,725 | 582,628 | 466 | 0.0% | 406 | 69,246,884 (+290.7%) | +169.8% | 28 / 105 (482) | 52 / 170 |
| 250,000 | 187,500 | 10 | R1+R2+R3+R4 | 294,775 | 493,389 | 401 | 0.0% | 380 | 11,434,057 (+48.0%) | +18.7% | 91 / 215 (677) | 195 / 373 |
| 250,000 | 187,500 | 20 | R1+R2+R3+R4 | 305,216 | 503,902 | 406 | 0.0% | 385 | 25,824,318 (+108.4%) | +55.9% | 75 / 188 (647) | 169 / 322 |
| 250,000 | 187,500 | 50 | R1+R2+R3+R4 | 344,101 | 545,954 | 465 | 0.0% | 428 | 72,454,093 (+304.2%) | +176.6% | 36 / 119 (554) | 73 / 207 |

#### ac753871198ee8cfd, turn unit promptId
| B | L | A | rules | median | p90 | >B | prot>B | trims | net units @0.05 (% real) | % real @0.1 | UAA@20 / @H (scored) | vis@20 / @H |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 100,000 | 75,000 | any | R1 | 459,060 | 730,202 | 391 | 97.3% | 1 | -1,985 (-0.0%) | -0.0% | 0 / 0 (3) | 0 / 0 |
| 100,000 | 75,000 | any | R1+R2 | 459,060 | 729,872 | 391 | 97.3% | 1 | -2,794 (-0.0%) | -0.0% | 0 / 0 (3) | 0 / 0 |
| 100,000 | 75,000 | 10 | R1+R2+R3 | 459,060 | 709,286 | 391 | 97.3% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 100,000 | 75,000 | 20 | R1+R2+R3 | 459,060 | 709,286 | 391 | 97.3% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 100,000 | 75,000 | 50 | R1+R2+R3 | 459,060 | 709,286 | 391 | 97.3% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 100,000 | 75,000 | 10 | R1+R2+R3+R4 | 459,060 | 709,286 | 391 | 97.3% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 100,000 | 75,000 | 20 | R1+R2+R3+R4 | 459,060 | 709,286 | 391 | 97.3% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 100,000 | 75,000 | 50 | R1+R2+R3+R4 | 459,060 | 709,286 | 391 | 97.3% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 131,072 | 98,304 | any | R1 | 459,060 | 730,202 | 386 | 93.3% | 1 | -1,985 (-0.0%) | -0.0% | 0 / 0 (3) | 0 / 0 |
| 131,072 | 98,304 | any | R1+R2 | 459,060 | 729,872 | 386 | 93.3% | 1 | -2,794 (-0.0%) | -0.0% | 0 / 0 (3) | 0 / 0 |
| 131,072 | 98,304 | 10 | R1+R2+R3 | 459,060 | 709,286 | 386 | 93.3% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 131,072 | 98,304 | 20 | R1+R2+R3 | 459,060 | 709,286 | 386 | 93.3% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 131,072 | 98,304 | 50 | R1+R2+R3 | 459,060 | 709,286 | 386 | 93.3% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 131,072 | 98,304 | 10 | R1+R2+R3+R4 | 459,060 | 709,286 | 386 | 93.3% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 131,072 | 98,304 | 20 | R1+R2+R3+R4 | 459,060 | 709,286 | 386 | 93.3% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 131,072 | 98,304 | 50 | R1+R2+R3+R4 | 459,060 | 709,286 | 386 | 93.3% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 150,000 | 112,500 | any | R1 | 459,060 | 730,202 | 377 | 86.4% | 1 | -1,985 (-0.0%) | -0.0% | 0 / 0 (3) | 0 / 0 |
| 150,000 | 112,500 | any | R1+R2 | 459,060 | 729,872 | 377 | 86.4% | 1 | -2,794 (-0.0%) | -0.0% | 0 / 0 (3) | 0 / 0 |
| 150,000 | 112,500 | 10 | R1+R2+R3 | 459,060 | 709,286 | 377 | 86.4% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 150,000 | 112,500 | 20 | R1+R2+R3 | 459,060 | 709,286 | 377 | 86.4% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 150,000 | 112,500 | 50 | R1+R2+R3 | 459,060 | 709,286 | 377 | 86.4% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 150,000 | 112,500 | 10 | R1+R2+R3+R4 | 459,060 | 709,286 | 377 | 86.4% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 150,000 | 112,500 | 20 | R1+R2+R3+R4 | 459,060 | 709,286 | 377 | 86.4% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 150,000 | 112,500 | 50 | R1+R2+R3+R4 | 459,060 | 709,286 | 377 | 86.4% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 200,000 | 150,000 | any | R1 | 459,060 | 730,202 | 347 | 74.8% | 1 | -1,985 (-0.0%) | -0.0% | 0 / 0 (3) | 0 / 0 |
| 200,000 | 150,000 | any | R1+R2 | 459,060 | 729,872 | 347 | 74.8% | 1 | -2,794 (-0.0%) | -0.0% | 0 / 0 (3) | 0 / 0 |
| 200,000 | 150,000 | 10 | R1+R2+R3 | 459,060 | 709,286 | 347 | 74.8% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 200,000 | 150,000 | 20 | R1+R2+R3 | 459,060 | 709,286 | 347 | 74.8% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 200,000 | 150,000 | 50 | R1+R2+R3 | 459,060 | 709,286 | 347 | 74.8% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 200,000 | 150,000 | 10 | R1+R2+R3+R4 | 459,060 | 709,286 | 347 | 74.8% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 200,000 | 150,000 | 20 | R1+R2+R3+R4 | 459,060 | 709,286 | 347 | 74.8% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 200,000 | 150,000 | 50 | R1+R2+R3+R4 | 459,060 | 709,286 | 347 | 74.8% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 200,000 | 120,000 | any | R1 | 459,060 | 730,202 | 347 | 74.8% | 1 | -1,985 (-0.0%) | -0.0% | 0 / 0 (3) | 0 / 0 |
| 200,000 | 120,000 | any | R1+R2 | 459,060 | 729,872 | 347 | 74.8% | 1 | -2,794 (-0.0%) | -0.0% | 0 / 0 (3) | 0 / 0 |
| 200,000 | 120,000 | 10 | R1+R2+R3 | 459,060 | 709,286 | 347 | 74.8% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 200,000 | 120,000 | 20 | R1+R2+R3 | 459,060 | 709,286 | 347 | 74.8% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 200,000 | 120,000 | 50 | R1+R2+R3 | 459,060 | 709,286 | 347 | 74.8% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 200,000 | 120,000 | 10 | R1+R2+R3+R4 | 459,060 | 709,286 | 347 | 74.8% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 200,000 | 120,000 | 20 | R1+R2+R3+R4 | 459,060 | 709,286 | 347 | 74.8% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 200,000 | 120,000 | 50 | R1+R2+R3+R4 | 459,060 | 709,286 | 347 | 74.8% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 250,000 | 187,500 | any | R1 | 459,060 | 730,202 | 316 | 65.8% | 1 | -1,985 (-0.0%) | -0.0% | 0 / 0 (3) | 0 / 0 |
| 250,000 | 187,500 | any | R1+R2 | 459,060 | 729,872 | 316 | 65.8% | 1 | -2,794 (-0.0%) | -0.0% | 0 / 0 (3) | 0 / 0 |
| 250,000 | 187,500 | 10 | R1+R2+R3 | 459,060 | 709,286 | 316 | 65.8% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 250,000 | 187,500 | 20 | R1+R2+R3 | 459,060 | 709,286 | 316 | 65.8% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 250,000 | 187,500 | 50 | R1+R2+R3 | 459,060 | 709,286 | 316 | 65.8% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 250,000 | 187,500 | 10 | R1+R2+R3+R4 | 459,060 | 709,286 | 316 | 65.8% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 250,000 | 187,500 | 20 | R1+R2+R3+R4 | 459,060 | 709,286 | 316 | 65.8% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |
| 250,000 | 187,500 | 50 | R1+R2+R3+R4 | 459,060 | 709,286 | 316 | 65.8% | 1 | -113,398 (-0.9%) | -1.0% | 3 / 5 (46) | 3 / 8 |

#### ac753871198ee8cfd, turn unit request (my addition)
| B | L | A | rules | median | p90 | >B | prot>B | trims | net units @0.05 (% real) | % real @0.1 | UAA@20 / @H (scored) | vis@20 / @H |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 100,000 | 75,000 | any | R1 | 446,210 | 701,757 | 391 | 55.9% | 54 | 2,890,562 (+21.9%) | +10.4% | 3 / 9 (77) | 4 / 10 |
| 100,000 | 75,000 | any | R1+R2 | 428,152 | 650,431 | 391 | 55.9% | 94 | 2,604,117 (+19.7%) | +6.6% | 3 / 9 (77) | 4 / 10 |
| 100,000 | 75,000 | 10 | R1+R2+R3 | 371,707 | 556,908 | 391 | 55.9% | 318 | 11,283,025 (+85.4%) | +38.2% | 30 / 87 (374) | 54 / 122 |
| 100,000 | 75,000 | 20 | R1+R2+R3 | 380,618 | 562,133 | 391 | 55.9% | 301 | 21,023,954 (+159.2%) | +80.6% | 24 / 70 (359) | 46 / 99 |
| 100,000 | 75,000 | 50 | R1+R2+R3 | 395,156 | 570,915 | 391 | 55.9% | 271 | 45,088,356 (+341.4%) | +185.3% | 14 / 45 (317) | 20 / 67 |
| 100,000 | 75,000 | 10 | R1+R2+R3+R4 | 337,972 | 462,080 | 391 | 55.9% | 343 | 11,188,191 (+84.7%) | +33.5% | 50 / 123 (455) | 107 / 203 |
| 100,000 | 75,000 | 20 | R1+R2+R3+R4 | 352,989 | 478,587 | 391 | 55.9% | 325 | 22,071,873 (+167.1%) | +81.2% | 37 / 101 (435) | 86 / 166 |
| 100,000 | 75,000 | 50 | R1+R2+R3+R4 | 391,234 | 494,027 | 391 | 55.9% | 295 | 48,645,185 (+368.4%) | +198.1% | 22 / 62 (374) | 39 / 106 |
| 131,072 | 98,304 | any | R1 | 446,210 | 701,757 | 385 | 1.5% | 53 | 2,869,896 (+21.7%) | +10.3% | 2 / 9 (77) | 3 / 10 |
| 131,072 | 98,304 | any | R1+R2 | 428,152 | 650,431 | 385 | 1.5% | 93 | 2,583,451 (+19.6%) | +6.5% | 2 / 9 (77) | 3 / 10 |
| 131,072 | 98,304 | 10 | R1+R2+R3 | 371,707 | 556,908 | 385 | 1.5% | 317 | 11,262,358 (+85.3%) | +38.1% | 29 / 87 (374) | 53 / 122 |
| 131,072 | 98,304 | 20 | R1+R2+R3 | 380,618 | 562,133 | 385 | 1.5% | 300 | 21,003,288 (+159.0%) | +80.5% | 23 / 70 (359) | 45 / 99 |
| 131,072 | 98,304 | 50 | R1+R2+R3 | 395,156 | 570,915 | 385 | 1.5% | 270 | 45,067,690 (+341.3%) | +185.3% | 13 / 45 (317) | 19 / 67 |
| 131,072 | 98,304 | 10 | R1+R2+R3+R4 | 337,972 | 462,080 | 385 | 1.5% | 342 | 11,167,524 (+84.6%) | +33.4% | 49 / 123 (455) | 106 / 203 |
| 131,072 | 98,304 | 20 | R1+R2+R3+R4 | 352,989 | 478,587 | 385 | 1.5% | 324 | 22,051,207 (+167.0%) | +81.2% | 36 / 101 (435) | 85 / 166 |
| 131,072 | 98,304 | 50 | R1+R2+R3+R4 | 391,234 | 494,027 | 385 | 1.5% | 294 | 48,624,519 (+368.2%) | +198.0% | 21 / 62 (374) | 38 / 106 |
| 150,000 | 112,500 | any | R1 | 446,210 | 701,757 | 374 | 0.0% | 53 | 2,881,197 (+21.8%) | +10.4% | 2 / 9 (77) | 3 / 10 |
| 150,000 | 112,500 | any | R1+R2 | 428,152 | 650,431 | 374 | 0.0% | 93 | 2,594,752 (+19.6%) | +6.6% | 2 / 9 (77) | 3 / 10 |
| 150,000 | 112,500 | 10 | R1+R2+R3 | 371,707 | 556,908 | 368 | 0.0% | 312 | 10,992,653 (+83.2%) | +37.0% | 29 / 87 (374) | 53 / 122 |
| 150,000 | 112,500 | 20 | R1+R2+R3 | 380,618 | 562,133 | 374 | 0.0% | 300 | 21,014,589 (+159.1%) | +80.5% | 23 / 70 (359) | 45 / 99 |
| 150,000 | 112,500 | 50 | R1+R2+R3 | 395,156 | 570,915 | 374 | 0.0% | 270 | 45,078,992 (+341.3%) | +185.3% | 13 / 45 (317) | 19 / 67 |
| 150,000 | 112,500 | 10 | R1+R2+R3+R4 | 337,972 | 462,080 | 368 | 0.0% | 337 | 10,897,819 (+82.5%) | +32.2% | 49 / 123 (455) | 106 / 203 |
| 150,000 | 112,500 | 20 | R1+R2+R3+R4 | 352,989 | 478,587 | 374 | 0.0% | 324 | 22,062,508 (+167.1%) | +81.2% | 36 / 101 (435) | 85 / 166 |
| 150,000 | 112,500 | 50 | R1+R2+R3+R4 | 391,234 | 494,027 | 374 | 0.0% | 294 | 48,635,820 (+368.3%) | +198.1% | 21 / 62 (374) | 38 / 106 |
| 200,000 | 150,000 | any | R1 | 446,210 | 701,757 | 341 | 0.0% | 50 | 2,888,897 (+21.9%) | +10.5% | 2 / 9 (77) | 3 / 10 |
| 200,000 | 150,000 | any | R1+R2 | 428,152 | 650,431 | 341 | 0.0% | 90 | 2,602,308 (+19.7%) | +6.7% | 2 / 9 (77) | 3 / 10 |
| 200,000 | 150,000 | 10 | R1+R2+R3 | 371,707 | 556,908 | 300 | 0.0% | 252 | 8,967,497 (+67.9%) | +28.6% | 36 / 90 (374) | 57 / 125 |
| 200,000 | 150,000 | 20 | R1+R2+R3 | 380,618 | 562,133 | 304 | 0.0% | 256 | 18,253,846 (+138.2%) | +68.8% | 22 / 69 (359) | 42 / 100 |
| 200,000 | 150,000 | 50 | R1+R2+R3 | 395,156 | 570,915 | 341 | 0.0% | 267 | 45,086,547 (+341.4%) | +185.4% | 13 / 45 (317) | 19 / 67 |
| 200,000 | 150,000 | 10 | R1+R2+R3+R4 | 337,972 | 462,080 | 288 | 0.0% | 269 | 8,574,571 (+64.9%) | +22.6% | 56 / 126 (455) | 110 / 206 |
| 200,000 | 150,000 | 20 | R1+R2+R3+R4 | 352,989 | 478,587 | 304 | 0.0% | 280 | 19,268,453 (+145.9%) | +69.4% | 35 / 100 (435) | 83 / 167 |
| 200,000 | 150,000 | 50 | R1+R2+R3+R4 | 391,234 | 494,027 | 341 | 0.0% | 291 | 48,643,376 (+368.3%) | +198.2% | 21 / 62 (374) | 38 / 106 |
| 200,000 | 120,000 | any | R1 | 446,210 | 701,757 | 341 | 0.0% | 50 | 2,888,897 (+21.9%) | +10.5% | 2 / 9 (77) | 3 / 10 |
| 200,000 | 120,000 | any | R1+R2 | 428,152 | 650,431 | 341 | 0.0% | 90 | 2,602,308 (+19.7%) | +6.7% | 2 / 9 (77) | 3 / 10 |
| 200,000 | 120,000 | 10 | R1+R2+R3 | 371,707 | 556,908 | 300 | 0.0% | 252 | 8,967,497 (+67.9%) | +28.6% | 36 / 90 (374) | 57 / 125 |
| 200,000 | 120,000 | 20 | R1+R2+R3 | 380,618 | 562,133 | 304 | 0.0% | 256 | 18,253,846 (+138.2%) | +68.8% | 22 / 69 (359) | 42 / 100 |
| 200,000 | 120,000 | 50 | R1+R2+R3 | 395,156 | 570,915 | 341 | 0.0% | 267 | 45,086,547 (+341.4%) | +185.4% | 13 / 45 (317) | 19 / 67 |
| 200,000 | 120,000 | 10 | R1+R2+R3+R4 | 337,972 | 462,080 | 288 | 0.0% | 269 | 8,574,571 (+64.9%) | +22.6% | 56 / 126 (455) | 110 / 206 |
| 200,000 | 120,000 | 20 | R1+R2+R3+R4 | 352,989 | 478,587 | 304 | 0.0% | 280 | 19,268,453 (+145.9%) | +69.4% | 35 / 100 (435) | 83 / 167 |
| 200,000 | 120,000 | 50 | R1+R2+R3+R4 | 391,234 | 494,027 | 341 | 0.0% | 291 | 48,643,376 (+368.3%) | +198.2% | 21 / 62 (374) | 38 / 106 |
| 250,000 | 187,500 | any | R1 | 446,210 | 701,757 | 310 | 0.0% | 46 | 3,020,111 (+22.9%) | +11.1% | 4 / 8 (77) | 5 / 9 |
| 250,000 | 187,500 | any | R1+R2 | 428,152 | 650,431 | 300 | 0.0% | 71 | 2,624,606 (+19.9%) | +6.9% | 5 / 8 (77) | 6 / 9 |
| 250,000 | 187,500 | 10 | R1+R2+R3 | 371,707 | 556,908 | 274 | 0.0% | 231 | 8,295,879 (+62.8%) | +26.1% | 40 / 88 (374) | 67 / 124 |
| 250,000 | 187,500 | 20 | R1+R2+R3 | 380,618 | 562,133 | 279 | 0.0% | 235 | 17,039,582 (+129.0%) | +64.0% | 27 / 69 (359) | 52 / 100 |
| 250,000 | 187,500 | 50 | R1+R2+R3 | 395,156 | 570,915 | 290 | 0.0% | 242 | 44,069,011 (+333.7%) | +181.2% | 16 / 45 (317) | 22 / 67 |
| 250,000 | 187,500 | 10 | R1+R2+R3+R4 | 337,972 | 462,080 | 237 | 0.0% | 220 | 7,216,762 (+54.6%) | +17.3% | 62 / 124 (455) | 127 / 206 |
| 250,000 | 187,500 | 20 | R1+R2+R3+R4 | 352,989 | 478,587 | 240 | 0.0% | 227 | 16,161,558 (+122.4%) | +56.5% | 40 / 99 (435) | 93 / 168 |
| 250,000 | 187,500 | 50 | R1+R2+R3+R4 | 391,234 | 494,027 | 290 | 0.0% | 266 | 47,625,840 (+360.6%) | +193.9% | 24 / 62 (374) | 41 / 106 |

## 8. DISCREPANCIES (the brief against what I found)

- **D1. Thinking size (a deviation from the brief's stated method).** The brief says to size thinking as output_tokens minus the visible characters, "as the audit did".
  - The final usage record carries an exact count, `usage.output_tokens_details.thinking_tokens` (`scripts/jev_trim/replay.py:337`). It is a usage number, not a thinking-block field, so reading it keeps the safety rule.
  - On main, the brief's method totals 1,458,001 against 1,152,566 exact over 1,547 requests (1.265×; median per request 1.405×).
  - The default runs use the exact count where present, following the brief's own rule "exact where the API gives them". The brief's method is run as `main-thinking-model`.
- **D2. Visible output.** At 3.0 characters per token the modeled visible output exceeds the recorded output_tokens in many requests. On main, (output − exact thinking) / visible characters has a median of 0.605 tokens per character (1.65 characters per token). Where the exact count exists, visible blocks take the exact rest, split by characters.
- **D3. User-side 2.90 characters per token.** The per-kind fit on main (R² 0.931) gives 2.26 for tool results, 2.40 for hook contexts and task reminders, 2.36 for user text and 5.25 for other attachments. The brief's 2.90 is kept. The sensitivity run `main-user-cpt-2.26` is reported. Other-attachment sizes (flattened records, an upper bound) enter the protected floor, so the prot>B shares are likely overstated (INFERRED).
- **D4. The thread filter.** Every record of a subagent file has `isSidechain: true`, so the brief's `isSidechain false` filter finds 0 requests there. Subagent runs pass `--sidechain`.
- **D5. Turns in the subagent files.**
  - They hold no stop_hook_summary records, so under stop-hook turns each segment is one protected turn: 0 trims in all 216 stop-unit cells.
  - The promptId unit (26, 14 and 8 turns) is reported.
  - I added a `request` unit (the current request plus the last 2 requests protected). It is not in the brief or the design; it is flagged as a deviation and reported only for the subagent files.
- **D6. Output counts in the subagent files are under-recorded.** Final usage records exist for only part of each file: requests with thinking sized exactly are 215 of 595, 35 of 561 and 61 of 335. Elsewhere the recorded output is the partial first-record count (median 8 tokens per request in ac753871198ee8cfd). Thinking there falls back to the model, which gives about 0. R2 savings in subagent runs are therefore a lower bound, and the calibration fits are weak (R² 0.295, 0.486, 0.287).
- **D7. Cache price ratios.**
  - The brief asked to fetch Anthropic's prompt-caching page, but its boundary forbids network calls. The ratios therefore come from the claude-api skill bundled with Claude Code 2.1.283, `shared/prompt-caching.md`, line 144: "0.05× on Claude Opus 5.5 ($0.20/MTok)", "~0.1×" on other models, and "1.25× for 5-minute TTL, 2× for 1-hour TTL".
  - They are marked UNSURE and are parameters. The 0.1 read column is shown beside the 0.05 one.
  - All 3,700 requests across the four files ran `claude-opus-5-5`.
- **D8. The 09-28 median** is 460,505.5 (mine, the two-middle mean) against 460,505 (the audit's, truncated). All other cross-check fields are equal. The nearest-rank median is 460,365.
- **D9. The audit's "Active span" column** does not match request times. For 09-26 the audit shows 00:12:50Z to 14:24:45Z; mine is 00:13:03Z to 12:26:18Z. It is not a required cross-check field. The audit's span probably counts all records (INFERRED).
- **D10. R4's "large"** is not defined by the brief or the design. I used 500 tokens, as a parameter.
- **D11. Stub cost.** 40 tokens for every archived item except thinking, which is dropped whole at cost 0 (the design's C2). An item no larger than its stub is never archived.
- **D12. The protected set dominates.** With K=2 stop-hook turns, the protected set alone passes B=200,000 in 63.7% of main requests. At every B from 100,000 to 200,000 the policy archives everything eligible without reaching L, so those grid rows differ only in >B and prot>B.
- **D13. Run (a) window.** It covers the audit's slice extended to my pin, not the whole file since 09-02 (see §0).
- **D14. The miss definition's "earlier history"** follows P1: every earlier item in the segment, archived or not. This hides a need when two copies are archived at different trims (the test documents the case). The visible-only variant is reported beside it. On the main reference cells it counts 2.3× at 20 and 1.7× at the horizon.
- **D15. The lookahead is limited to the segment.** P1's was not.
- **D16. The cache model follows the brief** ("the tail after the edit point is written again"). The bundled reference, `shared/prompt-caching.md` lines 244-248, says each breakpoint walks back at most 20 positions. An edit far back may therefore miss the cached prefix entirely unless intermediate breakpoints exist. The net-cost figures are optimistic on this point (NOT modeled).
- **D17. Pin timing.** The subagent pins were taken at 23:01:42Z, two minutes after the main pin at 22:59:41Z.
- **D18. Timeline output.** Brief item 2's per-request item timeline is built in memory. The JSON carries per-segment and per-kind summaries, not per-item rows.

## 9. Self-attack: the three most likely ways this is wrong

1. **The modeled sizes misstate what a trim saves, so the active-context and cache numbers are off.**
   - Checks: thinking is exact for 1,547 of 1,548 main requests. Visible output is the exact per-request rest. At the brief's 2.90 the archivable kinds are under-sized against the per-kind fit (2.26-2.40, R² 0.931), so the savings are conservative. The 2.26 sensitivity moves the reference median from 332,932 to 314,879 (between-turn, all rules, A=20).
   - Residual: the prot>B share uses other-attachment sizes at 2.90 against a fitted 5.25, so it is likely overstated. The subagent R2 savings are a lower bound (D6).
2. **The policy archives protected items or breaks pairs.**
   - Tests: the protected-set test (no archived item in the current or last K turns, and none typed, first-message or skill body), the stub-pair test on the active list, and mutants 1-4, 6, 8 and 9 killed.
   - Real data: 0 between-turn trims at a request that does not start a turn in the reference cell. In the B=100,000, A=10, all-rules, per-request cell, only thinking is ever dropped (1,301 dropped against 1,991 stubbed).
3. **Use-after-archive is wrong through the restriction and the memo.**
   - The oracle test recomputes full, unrestricted `accounting.miss` calls from the archive map and agrees on every scored item.
   - The real-data counts were identical before and after the memo: 97/367 and 235/657 (per-request); 96/368 and 229/650 (between-turn).
   - Residual: the definition's own error in both directions (D14, and a token that re-entered through a later item still counts), so the counts are a lower bound on need only in the sense the brief states.

## 10. Refusals

- **About 00:04Z** (between the 00:03:44Z summary and the 00:04:29Z re-run), a built-in safety check refused `rm -f $OUT/*.json $OUT/SUMMARY.md`: "Permission for this command was denied by a built-in Claude Code safety check, not by the user … What was flagged: Dangerous rm operation detected in `rm -f $OUT/*.json $OUT/SUMMARY.md`. The target '$OUT/*.json' is a shell variable expansion …". I did not re-issue it. No deletion was needed: every output is overwritten in place, and the re-run reproduced identical bytes.
- **At 00:1xZ** the scratch report write was refused (see §0 item 2).
- **No read was refused.**

## 11. Adjacent defect, reported and not fixed (a READ-only module)

`scripts/jev_pipes/accounting.py:28` runs `_PATH.finditer`. The `_PATH` pattern at `scripts/jev_pipes/accounting.py:20` backtracks quadratically on a long run of path characters with no slash. Measured: about 36 ms per call on one 2,900-character run of a single letter; by extrapolation, seconds on a 100 KB unbroken token such as a base64 blob. My test fixtures avoid such runs. The real-transcript build is unaffected: 9.1 s for the whole pass, tokens included.

## 12. Evidence tiers

- **VERIFIED:** the premise; the gate counts; the cross-check fields; the mutant kills; determinism (byte-identical JSON across two full passes, and the fixture test); the output-string scan; the timings; the model names; the usage-shape counts; the thinking exact-versus-model totals; the per-kind fit.
- **INFERRED:** the prot>B overstatement (D3); the audit span's meaning (D9); the lookback risk's direction (D16).
- **ASSUMED (parameters):**
  - The cache ratios (bundled doc, not the live page).
  - R4 large = 500 tokens; the stub head content.
  - hook_success and prompt_snapshot do not enter the context; attachments are sized by flattened strings.
  - The turn unit in each run; the `request` unit.
  - The run (a) window.

## 13. Tree state at 00:12:43Z

- **HEAD:** the commit "Live-state: the two waiting briefs are committed; three commits wai ..." (a local id then).
- **Untracked, mine (11):** the three sources and eight outputs in §2.
- **Untracked, not mine (1):** `tasks/briefs/i59/VERIFY-I59-F-R5-report.md`.
- **The other lane's tracked modifications:** untouched.
- **Reused modules:** no diff since the PIN.
- **No process of mine is left running.**
