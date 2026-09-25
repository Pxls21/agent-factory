# S1-L1-R1 report: one repair of the situation-to-skill hook

Lane: S1-L1-R1 build (sandbox, Opus 5.5). Brief: `tasks/briefs/system1/S1-L1-R1-brief.md`. Report started 17:4xZ;
finished 19:1xZ 2026-09-25. Status: DONE, REVIEW-PENDING (the coordinator grades it and applies the skill patch of
section 7). Outcome: every contract item built and tested; 8 of 8 mutants killed by failed tests; the four rows that need a
skill line break are whole only once section 7 is applied; F5 does not meet "drops most of the 54 weak" (19 of 54).

DEVIATION (loud, small): the brief's scratch path `scratchpad/r1/` is an existing 554-byte text file from 2026-09-03 (another
lane's pytest output), not a directory. I did not touch it. My scratch is `scratchpad/s1l1r1/`, same rules (under 200 MB,
deleted as I go).

## 0. Premise re-measurement (verified, 17:4xZ)

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf
03ca747 S1-L1-R1 brief (task #277): ...          (the brief's commit on top of the PIN f259652)
$ git diff --stat 6195b77 origin/claude/soundbox-kit-migration-iz1jwf -- .claude/hooks tests/test_system1_context.py scripts/install_session_hooks.py tests/test_session_hooks.py
(empty)
$ sha256 (first 16) at the PIN | at origin | in the worktree
a3e37aba8adbc014 | a3e37aba8adbc014 | a3e37aba8adbc014  .claude/hooks/system1-context.py
eef9252d0c0c2b9f | eef9252d0c0c2b9f | eef9252d0c0c2b9f  .claude/hooks/system1-situations.json
2bd7568e12822e32 | 2bd7568e12822e32 | 2bd7568e12822e32  tests/test_system1_context.py
a6632b8003ccffe3 | a6632b8003ccffe3 | a6632b8003ccffe3  scripts/install_session_hooks.py
06490455c7163016 | 06490455c7163016 | 06490455c7163016  tests/test_session_hooks.py
$ bash scripts/test_summary.sh tests/test_system1_context.py tests/test_session_start_hook.py tests/test_session_hooks.py tests/test_hooks_worktree.py
pytest-summary: 124 passed in 13.57s
4 files set=2dc71b948b8b      (pc_suite.sh's set_id formula, computed inline: no bridge call)
$ df -h / | awk 'NR==2{print $4}'
1.8G
```

The coordinator's premise log (`scratchpad/r1-premise.log`, 17:37Z) holds the reproductions' rc lines and the hollow
mutate.py run (8 of 8 "KILLED" on "2 passed, 1 error"); they match the brief's block. Verdict: the premise holds; no
mismatch. Observed, not mine: `.claude/hooks/edit-snapshot.py` is modified in the tree (a new AF-AP-223 screen for a
mutation verdict read from the exit code alone); it is outside my boundary and I leave it alone.

## 1. Plan and the constraints the oracle sets (written 18:1xZ, before any code)

The verifier's scripts bind the new code in four ways, measured by reading them:
- `mutate.py` applies each mutant as a literal source replacement and asserts the anchor occurs exactly once; I may not
  edit the mutants. So all 8 anchor strings stay verbatim and unique in the new hook, and each mutant must still change
  behavior (m8 in particular: the new per-row error handling must not catch a bare LookupError).
- `replay.py` imports `plan_tool`, `plan_prompt`, `load_table`, `parse_skill`, `resolve`, `line_key`, `tokens`,
  `command_positions` and `CMD_POS`, and its V1 variant asserts that `CMD_POS.replace("timeout\s+\S+)\s)", ...)`
  changed the string. The names and that substring stay.
- `rows_static.py` judges entries with the hook's own `ENTRY_START_RX`; I leave that regex unchanged (widening it would
  weaken the oracle).
- `rows_dyn.py` asserts its fixture set equals the table's row set. Contract item 1 adds rows (the hook-registration
  subsection), so the unmodified script cannot pass its first assert on the new table. I run it unmodified and report
  that, and I also run it on the new table minus the new rows (labelled as such); my own tests cover the new rows.
- `h.check` and the test file's `blocks()` reject a block with no body line. F4's label-and-pointer block has none, so
  `prompt_dyn.py` will flag that one prompt by design.

Skill entries that cannot fit one 2,048-byte call whole need a line break in the skill (outside my boundary): the ops
scripts paragraph (env-tool-quirks 15-29, 2,330 B: rows ops-script and anchor-edit), the Ouroboros stdio quirks
(ouroboros-stdio 18-42, 2,801 B), and build-loop item 5 (331-341, 2,028 B before the label: the stamp row). The table is
written for the patched skills with selectors that also resolve on today's text; the patch goes in this report.

Order of work: (1) fix the harness copy and run it on the PIN; (2) tests first, red on the PIN; (3) the hook and table in
scratch, green there, 8 of 8 killed; (4) F5 and F6 measurements; (5) move into place, full gate, the reproductions;
(6) F19; (7) this report.

## 2. The mutation harness, fixed in my copy first (verified, 18:1xZ)

My copy: `scratchpad/s1l1r1/oracle/mutate.py`. The diff against the verifier's original changes only the classification:
an unmutated control run must pass first (else exit 2, no mutant runs); KILLED needs at least one FAILED test; a run whose
non-passes are all errors, or that pytest did not complete, is INVALID; a clean pass is SURVIVED. The 8 mutant
definitions are byte-identical. Hashes of all 14 originals were saved before any run (`scratchpad/s1l1r1/oracle-originals.sha`).

On the PIN (the live tree), `/root/venv-agent-factory/bin/python mutate.py`:
```
--- without bt/ (the case the old harness scored as 8 of 8 KILLED):
CONTROL FAILED on the unmutated hook: rc 1 | 2 passed, 1 error in 0.11s -> no mutant runs (a harness error is not a kill)
rc=2
--- with bt/:
CONTROL  unmutated hook passes                                         91 passed in 10.70s
SURVIVED m1 window lock removed (no flock)                                      91 passed in 10.96s []
SURVIVED m2 budget counts characters, not bytes                                 91 passed in 11.15s []
SURVIVED m3 telemetry logs the Write/Edit path                                  91 passed in 11.20s []
SURVIVED m4 telemetry logs the prompt's words (lower-cased)                     91 passed in 10.74s []
SURVIVED m5 marker stores the prompt's words                                    91 passed in 10.60s []
KILLED  m6 continuation lines dropped (a single-string selector takes one line) 1 failed, 79 passed in 6.22s ['test_the_tool_budget_cuts_at_a_line_boundary_and_keeps_the_pointer']
SURVIVED m7 the 7-day prune removed                                             91 passed in 10.97s []
SURVIVED m8 unresolved rows raise instead of skip                               91 passed in 10.57s []
hook restored: True
```
This reproduces the brief's premise (7 survive, m6 killed) with an honest harness.

## 3. F5, the one-word-lead rule: two families measured before choosing (verified, 18:2xZ)

Instrument: `scratchpad/s1l1r1/tools/prompt_split.py` (mine), counts only. The human prompts of this session's main
transcript (217; the same 217 at the verifier's cut 16:47:26Z and now), a fresh window per prompt, `plan_prompt` of each
hook, and the verifier's proxies: lead = prompt words in the best section's heading or skill name; cover = share of the
prompt's words in the injected text; strong = lead >= 2 and cover >= .20; weak = lead 1 and cover < .20. Calibration: on
the PIN it reproduces the verifier's split exactly (148 injected: strong 23, middle 71, weak 54).

| rule (new hook; F4 on) | injected | strong | middle | weak | PIN's 23 strong, same best section | PIN's 54 weak: nothing / still weak |
|---|---|---|---|---|---|---|
| PIN hook | 148 | 23 | 71 | 54 | - | - |
| one-word lead needs 12 (no F5) | 149 | 23 | 71 | 55 | 23 | 0 / 54 |
| needs 14 | 130 | 23 | 65 | 42 | 23 | 14 / 40 |
| needs 16 | 124 | 23 | 61 | 40 | 23 | 15 / 39 |
| **needs 18 (chosen)** | **117** | **24** | **57** | **36** | **23** | **19 / 35** |
| needs 20 | 111 | 24 | 52 | 35 | 23 | 20 / 34 |
| needs 24 | 103 | 23 | 48 | 32 | 23 | 23 / 31 |
| a second lead word | 79 | 31 | 48 | 0 | 23 | 36 / 0 |

The answer to the brief's question, measured: **no rule in either family keeps the good one-word leads and drops most of
the 54 weak ones.** The best scores of weak and middle one-word-lead matches overlap at every threshold (below 18: 19 weak,
14 middle; below 24: 23 weak, 25 middle), because the score counts body words over the whole section while the proxy's
cover counts only the injected excerpt. The second-lead-word rule leaves no weak match (36 inject nothing, 18 move to a
section with a two-word lead) but also drops plainly relevant matches: "the resume after compaction protocol, fetch origin
and compare the three clocks" (a fixture, not a transcript prompt) loses both session-continuity sections, and the F4
reproduction's own prompt ("launch the pc lane ...", best section scored 18.79 on the one lead word "lane") injects
nothing, so `f4_prompt_pointer.py` could not exit 0. I chose 18 = 1.5 x MIN_PROMPT_SCORE: the most weak matches dropped
(19) of any rule that keeps that acceptance prompt, all 23 strong kept with the same best section, 21 % fewer prompt
injections (the verifier's F23 context cost), and the verifier's F5 example (systemctl, 12.88 on "unit") no longer
injects. DISCREPANCY: "drops most of its 54 weak ones" is NOT met (19 of 54); the data says a lead-count or score rule
cannot meet it without dropping good matches. A cover-aware rule (score the excerpt, not the section) is the candidate
for that, NOT built.

## 4. Tests first: red on the PIN, green on the candidate, and 8 of 8 mutants killed (verified, 18:4xZ)

Staging (my scratch; the tree untouched until section 6): `stage-pin` = the PIN hook and table + my new test file;
`stage-new` = my hook and table + the same test file, today's skills; `stage-patched` = the same with the skill patch
of section 5 applied to the staged skill copies. `/root/venv-agent-factory/bin/python -m pytest -q` in each:

```
stage-pin      31 failed, 92 passed in 43.67s      (123: the PIN table has 38 rows, so 4 fewer parametrized cases)
stage-new      127 passed in 18.80s
stage-patched  127 passed in 19.75s                (the four pending-break runs of the whole-entry test are then whole)
```

The 31 PIN failures, each for its stated reason (one-line reasons from `--tb=line`): the 2 new rows absent; 4 delivery
cases "not whole entries" (push, push-delegate-work, test-edit, test-edit-increment: the line-level cut); the static
whole-entry set (17 runs vs the 4 pending); the qualifier test; the first push brings `push` first; F4 (pointer absent);
F5 (the systemctl prompt injects "Repair briefs"); F12 (a dangling `system1-off` injects); F9 (`...json.<pid>.tmp` left);
F8 (a call injects while another holds the lock); F16 (one bad regex silences `commit`); F17 (`TimeoutExpired` on a
FIFO skill; the test unblocks the FIFO after, and no process was left: `ps` count 0); F1 x5 (`pgrep` not injected); F6
x9 (data fires push, pc-call, pgrep; `pc.sh '…'`, `bash -c '…'`, `ssh "…"` do not fire their first command); F7
(`2623 ms < 100` false). EXCEPTION, flagged: `test_the_budget_counts_bytes_not_characters` fails on the PIN with a
`ValueError` from the changed `compose` signature (units, not lines), not for the stated reason; the PIN counts bytes
correctly, so that test's red evidence is mutant m2 below. The mutant-killing tests (canary, prune, unresolved skip,
burst) pass on the PIN, as they must: the PIN is correct there; their red evidence is the mutants.

The fixed harness (section 2) on the candidate, `repo_m` = `setup_copy.sh`'s copy with my hook, table and test file
overlaid (the oracle scripts untouched):
```
CONTROL  unmutated hook passes                                         127 passed in 20.89s
KILLED  m1 window lock removed (no flock)                                      1 failed, 101 passed in 18.30s ['test_a_held_lock_injects_nothing_and_logs_why']
KILLED  m2 budget counts characters, not bytes                                 1 failed, 88 passed in 11.64s ['test_the_budget_counts_bytes_not_characters']
KILLED  m3 telemetry logs the Write/Edit path                                  1 failed, 96 passed in 14.17s ['test_no_input_text_reaches_any_state_file']
KILLED  m4 telemetry logs the prompt's words (lower-cased)                     1 failed, 96 passed in 13.79s ['test_no_input_text_reaches_any_state_file']
KILLED  m5 marker stores the prompt's words                                    1 failed, 96 passed in 13.64s ['test_no_input_text_reaches_any_state_file']
KILLED  m6 continuation lines dropped (a single-string selector takes one line) 1 failed, 4 passed in 0.43s ['test_a_row_delivers_its_whole_entries_in_one_window[brief]']
KILLED  m7 the 7-day prune removed                                             1 failed, 86 passed in 10.97s ['test_the_reset_prunes_markers_idle_for_seven_days']
KILLED  m8 unresolved rows raise instead of skip                               1 failed, 103 passed in 18.40s ['test_an_unresolved_row_is_skipped_through_the_registered_command']
hook restored: True
```
Why each died (each mutant applied alone, only its killing test, `--tb=line`): m1 the call injects while the lock is
held; m2 the unit over by bytes is delivered; m3 and m4 the canary is in `system1.jsonl`; m5 the canary is in the marker
`s1test-session-0001.main.json`; m6 the `brief` row is not whole entries; m7 the 8-day-old files stay; m8 nothing is
injected (the LookupError reaches the top). Each is the reason the test names.

## 5. The replay before and after, F2's parts and F6's nested commands (verified, 18:4xZ; counts only)

The verifier's `replay.py` (my unmodified copy), cut at 2026-09-25T18:40:00Z so both runs read the same 16,983 calls;
"before" = `setup_copy.sh`'s copy (the PIN), "after" = my hook and table overlaid on that copy. Its V1-V3 variants are
the verifier's what-ifs layered on each V0; on the new V0 they add almost nothing because V0 already does their masking.
```
before  calls: {'Bash': 15761, 'Write': 559, 'Edit': 663} | total 16983
before  V0: calls that received an injection: {'Bash': 1351, 'Write': 142, 'Edit': 124} total 1617 | injected bytes 2067163
before  V1: calls that received an injection: {'Bash': 1350, 'Write': 142, 'Edit': 124} total 1616 | injected bytes 2067164
before  V2: calls that received an injection: {'Bash': 1298, 'Write': 142, 'Edit': 124} total 1564 | injected bytes 1977773
before  V3: calls that received an injection: {'Write': 142, 'Edit': 124, 'Bash': 1278} total 1544 | injected bytes 1961896
before  V0 variant B (+ resume resets) bytes: 2126804
before  bytes per injected call: median 1275 max 2046
before  bytes per window (A, 131 windows): median 16740, p90(index) 20738, max 25680, windows with none 2
before  Write/Edit/Bash calls per window: median 131 max 310
after   calls: {'Bash': 15761, 'Write': 559, 'Edit': 663} | total 16983
after   V0: calls that received an injection: {'Write': 154, 'Edit': 142, 'Bash': 1306} total 1602 | injected bytes 2183994
after   V1: calls that received an injection: {'Write': 154, 'Edit': 142, 'Bash': 1306} total 1602 | injected bytes 2183994
after   V2: calls that received an injection: {'Write': 154, 'Edit': 142, 'Bash': 1306} total 1602 | injected bytes 2183994
after   V3: calls that received an injection: {'Write': 154, 'Edit': 142, 'Bash': 1303} total 1599 | injected bytes 2179024
after   V0 variant B (+ resume resets) bytes: 2246140
after   bytes per injected call: median 1410.0 max 2042
after   bytes per window (A, 131 windows): median 16966, p90(index) 23071, max 29367, windows with none 2
after   Write/Edit/Bash calls per window: median 131 max 310
```

Per row, V0 (matched / injected / cut / skipped duplicate / skipped budget / skipped unresolved), before | after:
```
 pc-sqlite 224 50 0 174 0 0| pc-sqlite 28 8 0 20 0 0
 pc-podman 132 29 0 103 0 0| pc-podman 83 23 0 60 0 0
 pc-call 2293 118 6 2169 6 0| pc-call 2260 116 4 2143 1 0
 pc-lane 593 72 0 519 2 0| pc-lane 367 63 0 303 1 0
 pc-suite 371 67 0 304 0 0| pc-suite 258 22 0 236 0 0
 ouroboros 63 6 1 57 0 0| ouroboros 54 6 3 48 0 0
 push 919 128 4 790 1 0| push-delegate-work 855 124 0 728 3 0
 push-delegate-work 919 226 121 688 5 0| push 855 187 102 541 127 0
 stamp 1780 103 0 1670 7 0| hook-installer 3 3 0 0 0 0
 commit 1388 126 0 1249 13 0| stamp 1780 104 0 1675 1 0
 commit-increment 1388 123 8 1248 17 0| commit 1346 126 0 1217 3 0
 proof-regen 262 49 0 208 5 0| commit-increment 1346 118 0 1203 25 0
 vendored-manifest-write 79 34 0 45 0 0| proof-regen 120 40 0 80 0 0
 test-vendored-manifest 58 23 1 35 0 0| vendored-manifest-write 54 27 0 27 0 0
 test-proof-status 45 18 0 27 0 0| test-vendored-manifest 28 11 0 13 4 0
 test-gate 1173 76 0 1082 15 0| test-proof-status 35 15 0 20 0 0
 pasted-count 1124 43 0 1050 31 0| test-gate 762 38 0 721 3 0
 anchor-edit 610 75 11 533 2 0| pasted-count 1124 58 0 1039 27 0
 ops-script 507 98 12 379 30 0| anchor-edit 601 63 0 526 12 0
 background 569 100 0 457 12 0| ops-script 345 72 0 249 24 0
 pgrep 576 103 11 469 4 0| background 439 93 0 338 8 0
 gitnexus 214 65 0 143 6 0| pgrep 555 85 0 458 12 0
 codebase-memory 29 7 0 19 3 0| gitnexus 169 61 0 103 5 0
 code-review-graph 20 7 0 10 3 0| codebase-memory 17 5 0 12 0 0
 graft 86 39 6 43 4 0| code-review-graph 4 3 0 1 0 0
 lane-context 93 33 7 52 8 0| graft 29 18 0 11 0 0
 brief 206 63 13 143 0 0| lane-context 40 15 0 23 2 0
 brief-contract 206 51 12 104 51 0| brief-registers-hook 16 6 0 10 0 0
 research-prompt 1 1 0 0 0 0| brief 206 87 50 102 17 0
 live-state 10 3 0 7 0 0| brief-contract 206 50 13 100 56 0
 claude-md-gitnexus-block 1 1 0 0 0 0| research-prompt 1 1 0 0 0 0
 dormant-claim 2 2 0 0 0 0| live-state 10 3 0 7 0 0
 test-edit 191 49 0 142 0 0| claude-md-gitnexus-block 1 1 0 0 0 0
 test-edit-increment 191 33 20 157 1 0| dormant-claim 2 2 0 0 0 0
 gate-edit 66 20 0 46 0 0| test-edit 191 80 43 110 1 0
 gate-edit-tactics 66 10 0 56 0 0| test-edit-increment 191 10 0 148 33 0
 code-edit 384 61 1 315 8 0| gate-edit 66 20 0 46 0 0
 code-edit-guidelines 384 71 17 294 19 0| gate-edit-tactics 66 10 0 56 0 0
| code-edit 384 52 0 289 43 0
| code-edit-guidelines 384 78 23 297 9 0
```

Windows where a row injected but some of its lines never arrived before the window closed:
```
before  windows where a row was injected but some of its lines never arrived before the window closed: 38 | by row: {'push-delegate-work': 19, 'code-edit-guidelines': 6, 'brief-contract': 5, 'graft': 2, 'ops-script': 1, 'anchor-edit': 1, 'lane-context': 1, 'brief': 1, 'code-edit': 1, 'test-vendored-manifest': 1}
after   windows where a row was injected but some of its lines never arrived before the window closed: 54 | by row: {'push': 17, 'brief': 13, 'test-edit': 12, 'code-edit-guidelines': 6, 'brief-contract': 6}
```

Reading it: injected calls 1,617 -> 1,602 and bytes 2,067,163 -> 2,183,994 (+5.7 %): whole entries carry more text per
row (push now 40-49 + 50 + 59, push-delegate-work 533-547, brief's 0l whole, test-edit two whole entries, the pasted-count
entry whole for pc-suite, test-gate and pasted-count). pc-suite injects less (67 -> 22) because its entry is now the
same entry test-gate and pasted-count deliver: the lines arrive once, under whichever row fires first.

**F2's parts, per whole entry** (`tools/parts_nested.py`, mine, the same cut and windows; the new hook):
```
  push                       matched in 124 windows | arrived: entry 1: 102, entry 2: 102, entry 3: 85
  test-vendored-manifest     matched in  15 windows | arrived: entry 1: 11
  anchor-edit                matched in  64 windows | arrived: entry 1: 63
  ops-script                 matched in  77 windows | arrived: entry 1: 72
  gitnexus                   matched in  63 windows | arrived: entry 1: 61, entry 2: 61
  brief                      matched in  51 windows | arrived: entry 1: 50, entry 2: 50, entry 3: 37
  brief-contract             matched in  51 windows | arrived: entry 1: 43, entry 2: 43, entry 3: 43, entry 4: 37
  test-edit                  matched in  49 windows | arrived: entry 1: 49, entry 2: 37
  code-edit                  matched in  61 windows | arrived: entry 1: 52
  code-edit-guidelines       matched in  61 windows | arrived: entry 1: 61, entry 2: 55
  rows whose every entry arrived in every window they matched: 30
  'Push the REVIEWED SHA ... never HEAD': windows with a push-row match 124; the line arrived: PIN 105, new 124
```
The verifier's headline (the REVIEWED-SHA line missing in 19 windows) is gone: 124 of 124. The cost moved to `push`'s
later entries: its third entry (`--lanes-live` counts tracked dirt only) arrived in 85 of 124 windows, because a window
often has only one or two push-shaped calls and push-delegate-work now goes first. brief's third entry (rule 3, the brief
is a hypothesis) arrived in 37 of 51, test-edit's second (execution guards) in 37 of 49. These are whole entries waiting
for a call that never came, never a cut inside an entry.

**F6, the detector level** (the 38 PIN rows' command detectors on both sides, so only the scan differs; a (call, row)
pair counts once, classed by where its matching command word sits):
```
PIN : 18,592 matches = 15,791 plain code + 234 inside a quote or heredoc a shell reads ("nested") + 2,567 data only
new : 16,122 matches = 15,856 plain code + 266 nested; 184 of them are new (152 plain, 32 nested)
```
- The 2,567 data-only matches (13.8 %) are the false positives F6 names; none survives.
- Nested commands kept: all 234 (the builder's D11 counted 328 with its own masking; same class, a different count), plus
  32 first commands of a shell-read quote (`pc.sh 'pgrep …'`, `bash -c 'git push …'`) that no scan found before.
- The 152 new plain matches: 25 are F1 (a rerun with the loop keywords stripped leaves 127); the rest are commands the
  old scan swallowed. Shape-only inspection (letters as `a`, no text printed) shows the main one: `R=$(timeout 120 bash
  scripts/pc.sh …)`. The old assignment pattern `NAME=\S*\s+` took `R=$(timeout ` as one assignment, so the command inside
  the substitution never got a position (reproduced on a synthetic command: PIN positions `['120']`, new `['r=$(timeout',
  'timeout', 'pc.sh', ...]`). F7's word class `[^\s;&|()\`]` ends a value at `(` or a separator, which fixes it; 21 more
  were a separator swallowed by the old `\S*`. This is a PIN false-negative class the verifier did not list; I report it,
  and it is fixed by the F7 change, not by extra code.

**F6, what the new scan loses, checked with a second instrument** (`tools/lost2.py`, `tools/lost3.py`, mine; the verifier's
own masking, `mask_heredocs` + `mask_quotes` extracted from `replay.py` with `ast` and not run, is the second
instrument). Of the PIN's 18,592 (call, row) matches, the final hook loses 2,648:
- 2,535: data by my lexer AND by the verifier's masking (the false positives F6 names).
- 30: data by my lexer, code by the verifier's masking. Shape-only inspection (letters as `a`): grep or echo text in
  double quotes that holds `$(…)` or `\|`; the verifier's quick mask ends the quote at the inner `"`, the shell does
  not. Data; mine is right on these.
- 75: the command word is code, but the PIN reached it only from a separator inside a quote or a comment
  (`grep -E "^A=\|B=" scripts/pc_suite.sh` fired pc-suite on grep's file argument). PIN false positives.
- 7: the PIN reached the word from the newline of a line continuation (`\` + newline), which the shell does not treat
  as a new command: the word is an argument of the line above. Where that line is a wrapper word followed by `--` (the
  shape shows one), the command after it is a real miss of the prefix rules, which the PIN caught only by accident.
- 1: a path argument of a `$(…)` call, reached by the old `\S*` through the `$(`. A PIN false positive.

**A defect of my own first version, found by this check and fixed before the final runs (flagged):** the first lexer
masked `\` + newline as an escaped character, so a command after a continuation lost its position (`cd /x && \` +
newline + `bash scripts/pc.sh 'uptime'` gave no `pc.sh`; `python3 \` + newline + `scripts/proof-runner …` gave no
`proof-runner`). The continuation now reads as a space (`continuation`, `system1-context.py:191-199`), with two regression cases in the F6
test. That first version was LIVE from 18:51:14Z to 19:05:39Z (both hook swaps below), so for 14 minutes such
continuation commands drew no row in every session here. The 17 earlier lexer probe cases are unchanged by the fix.

## 6. Into place, the final gate and the reproductions (verified, 19:1xZ)

Every move was one `mv` from my scratch on the same filesystem (`/dev/vda`, device 65024), after `py_compile` or
`json.load` and the staged tests; each previous version is kept in `scratchpad/s1l1r1/prev/`:
- 18:51:14Z hook + table (the PIN versions kept as `prev/system1-context.py`, `prev/system1-situations.json`);
  18:51:42Z the two test files and the installer (PIN versions kept beside them).
- 18:54:24Z hook + test file: timeout and other error records now carry `window` (kept: `prev/system1-context.r1-first.py`).
  Reason: `conc_dyn.py`'s summary selects the held-lock records by window and crashed on none; a record that cannot be
  tied to its window is a telemetry gap, so this is a fix, not a fit to the script.
- 19:05:39Z hook + test file: the continuation fix above (kept: `prev/system1-context.r1-second.py`).
- After each move the live telemetry showed clean records (no `error`, 2-11 ms); no live call broke, nothing was
  restored. `python3 scripts/install_session_hooks.py --check` (read-only): `session hooks: present in
  /home/user/.claude/settings.json`, rc 0; that call fired the new `hook-installer` row live (1 entry, 1,360 bytes).
- Side effect: my first `py_compile` at 18:51:14Z refreshed the gitignored `.claude/hooks/__pycache__/system1-context.cpython-311.pyc`
  (the directory already held other hooks' caches; later compiles ran in scratch).

The gate, final tree, twice (`bash scripts/test_summary.sh` on the brief's four files):
```
pytest-exit: 0
pytest-summary: 164 passed in 23.31s
pytest-exit: 0
pytest-summary: 164 passed in 22.89s
4 files set=2dc71b948b8b
pyflakes (the four .py files I changed): rc 0
LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]': 0 for each of the five boundary files and this report
```
(124 at the PIN: 91 in tests/test_system1_context.py + 33 in the other three. Now 129 + 35.)

The verifier's reproductions, my unmodified copies after `bash setup_copy.sh` (the copy = the live tree, checked by cmp):
```
f1_while_pgrep.py: pgrep row on `while pgrep …`: injected | matched: ['pgrep']
rows_static.py: 4 row runs start or end inside an entry
f4_prompt_pointer.py: best: pc-bridge-lanes § Launching, re-attaching and sizing PC lanes | its pointer in additionalContext: True | skipped: []
conc_dyn.py: stray tmp files: []
hostile.py:      the next call in that window injects: False | error: json.decoder.JSONDecodeError
ks_secrets.py: injections that happened (so the canaries rode through real work): [2, 1, 1, 2, 0, 2, 0, 0]
window_dyn.py: A.main marker idle 8 days, after another session's startup: exists = False | A.main injects again: True
rows_dyn.py: AssertionError: {'hook-installer', 'brief-registers-hook'}
prompt_dyn.py: problems: [(24, 'oracle', 'empty body or a gap mark at an edge')]
```
- `f1_while_pgrep.py`, `f4_prompt_pointer.py`: rc 0.
- `rows_static.py`: rc 1 on today's skills with exactly the 4 runs that wait for the skill patch (section 7); with the
  patch applied to the copy's skills: `0 row runs start or end inside an entry`, rc 0.
- `conc_dyn.py`: rc 0. With the external holder both trials read `(0, 0, 0)` (PIN: `(83, 17, 11)` and `(59, 40, 38)`);
  `errors: Counter({'WindowLockTimeout': 32})`; free lock `(77, 0, 0)` x4; no stray temp file. My own rc-gated tests:
  `test_a_held_lock_injects_nothing_and_logs_why`, `test_a_parallel_burst_on_one_window_never_repeats_or_loses_a_line`.
- `hostile.py`: rc 0, every input rc 0 and 0 bytes of stderr. 3 lines print BAD, by F16's design: "missing skill dir",
  "SKILL.md is a directory" and "a row regex that does not compile" now skip that row only and the other rows inject
  (1,171 / 1,171 / 1,747 bytes); the script's expectation encodes the old whole-call failure. The full-disk case leaves
  no `.tmp` now (F9). Error names are module-qualified (`json.decoder.JSONDecodeError`).
- `ks_secrets.py`: rc 0; canary hits NONE; a dangling `system1-off` now switches it off (PreToolUse and prompt 0 bytes,
  F12); the exception record's keys gain `window`.
- `window_dyn.py`: rc 0, output byte-identical to the PIN run.
- `rows_dyn.py`: rc 1 at its first line, `AssertionError: {'hook-installer', 'brief-registers-hook'}`: its fixture set
  pins the 38 PIN rows and contract item 1 adds two. The same unmodified script on the new table minus those two rows:
  rc 0, `rows checked: 38 | total calls: 95`, `problems: 2`, both `('brief', 'brief', 'out of order')` /
  `('brief-contract', 'brief', 'out of order')` = the verifier's F3 (INFO, row priority by design). PIN run: 3 problems,
  the third being F1 (`pgrep` did not match its fixture). The two new rows are covered by my tests (fixtures, delivery,
  near miss) and fired live.
- `prompt_dyn.py` (not on the must-hold list): 1 problem, prompt 24 "empty body": F4's label-and-pointer block, which the
  verifier's `check` rejects by construction. PIN: 0 problems, because the PIN dropped that pointer silently.
- `mutate.py` (my fixed copy), final tree: CONTROL 129 passed; m1-m8 all KILLED by FAILED tests (the same eight killing
  tests as section 4).
- `latency.py` (informational), hook-internal medians new vs PIN: no match 2.4 vs 3.1 ms, git commit 6.1 vs 6.5, code
  edit 5.6 vs 4.6, prompt warm 11.3 vs 9.7, cold 38.9 vs 34.4; wall medians within noise on a shared box.
- The in-process F7 case (`test_the_command_scan_is_linear`, best of 3): the 198 KB data heredoc runs `plan_tool` in
  about 32 ms (the PIN's scan of 40 KB of `;` took 2,623-2,747 ms).

## 7. The proposed skill patch (for the coordinator to apply; I edited no skill file) (19:1xZ)

Three line breaks, no word changed. Each makes an entry edge where a row needs one, so that every row is whole entries
and every entry fits one call. Checked: `git apply --check` rc 0 on the tree at 19:0xZ (no skill changed since the PIN);
with it applied to copies, `rows_static.py` exits 0 and the final test file passes there, `129 passed in 22.20s`, with
its PENDING_BREAKS set empty.

- P1, env-tool-quirks `## The ops scripts`: `**\`scripts/anchor_edit.py\`` starts its own line. Rows `ops-script` (then whole:
  15-27, about 1.4 KB) and `anchor-edit` (then whole: the anchor_edit.py entry). Today the paragraph 15-29 is one entry of
  2,330 bytes, larger than a call.
- P2, ouroboros-stdio: `**Resume uses the EXACT documented` starts its own line. Row `ouroboros` (then its second
  entry, 18-32, 1,698 bytes, is whole; today the quirks paragraph 18-42 is one entry of 2,801 bytes).
- P3, build-loop `### The operative core`: a blank line before the count-and-stamp paragraph of item 5. Row `stamp`
  (today item 5, 331-341, is 2,028 bytes before the label and cannot go whole).

Until the patch is in, those four rows deliver what they deliver today (a part of the entry), `rows_static.py` reports
4 runs, and `tests/test_system1_context.py` allows exactly those 4 (PENDING_BREAKS); once a break is in, the test demands
that run be whole, and PENDING_BREAKS can then be deleted. Apply with `git apply` on this text:

```diff
diff -ru a/.claude/skills/build-loop/SKILL.md b/.claude/skills/build-loop/SKILL.md
--- a/.claude/skills/build-loop/SKILL.md	2026-09-25 18:25:44.451918981 +0000
+++ b/.claude/skills/build-loop/SKILL.md	2026-09-25 18:25:44.465906690 +0000
@@ -338,6 +338,7 @@
    status lines open with the OUTCOME: `Verified live:` ≠ `DONE:` ≠ `NOT built.` (stated
    first-class). Ledger denominators are FOUR-WAY (execution / conformance-checked decision /
    blocked-on-external-input / blocked-on-capability) — never a flat count over the twelve proofs.
+
    Test counts in reports and commit messages are PASTED from `scripts/test_summary.sh` output verbatim, never typed (AF-AP-37: '217 tests green' was a collection total). Timestamps are the same rule — pasted from `date -u` or the commit clock (2026-09-07: the day's ledger stamps drifted 2.8 h ahead); a ten-minute bucket comes from the clock too, `date -u +'%H:%M' | sed 's/[0-9]$/xZ/'`, never rounded up to the bucket an event is expected in (three ahead-of-clock stamps on 2026-09-25; the future-stamp gate blocked the one that reached a commit); a fourth at 04:5xZ, typed in the same call that ran `date`). **A stamp is SUBSTITUTED, never typed:** `export STAMP=$(date -u +'%H:%M' | sed 's/[0-9]$/xZ/')` and the text uses `$STAMP` (or `os.environ['STAMP']`) in the same command. **The Write tool cannot substitute:** a file written through Write takes its stamp from a `date -u` run just before it, pasted from that output, or is written through a Bash heredoc that expands `$STAMP` (the P1-R1 brief's premise heading, typed 09:2xZ at 09:18Z, the fifth; the future-stamp gate blocked the commit).
 
 ### Behavioral guidelines (Andrej Karpathy skills)
diff -ru a/.claude/skills/env-tool-quirks/SKILL.md b/.claude/skills/env-tool-quirks/SKILL.md
--- a/.claude/skills/env-tool-quirks/SKILL.md	2026-09-25 18:25:44.439779097 +0000
+++ b/.claude/skills/env-tool-quirks/SKILL.md	2026-09-25 18:25:44.465474896 +0000
@@ -24,7 +24,8 @@
 gate venue when the bridge is up; `spikes/` stays sandbox-only)** · `scripts/why.sh <file> [fn]`
 (on-demand chronology from primary sources) · `scripts/replay_transcript_edits.py` (recover a
 dead delegate's edits from its transcript) · `scripts/lint_delta.py` (the pre-commit pyflakes
-DELTA gate: new hits only; `--base HEAD` reads tracked files only, so a lane's NEW files are linted by `pyflakes` directly until staged, JT1 DISC-1 2026-09-24) · `scripts/verify-planning-repo.sh` (the planning docs' own check) · **`scripts/anchor_edit.py` (ledger-plane
+DELTA gate: new hits only; `--base HEAD` reads tracked files only, so a lane's NEW files are linted by `pyflakes` directly until staged, JT1 DISC-1 2026-09-24) · `scripts/verify-planning-repo.sh` (the planning docs' own check) ·
+**`scripts/anchor_edit.py` (ledger-plane
 edits: every anchor validated unique BEFORE any write, all-or-nothing, rc 2 with the file untouched on a miss; `--replace OLD NEW` /
 `--insert-after|--insert-before PREFIX TEXT`, `@file` values; it never commits — a mutation and a commit never share a call, bit twice 2026-09-08; a VALUE that begins with `@` is ALWAYS read as a file path — there is no escape — so a placeholder never starts with `@`, bit 2026-09-22 on an `@@FULL@@` placeholder; an `@file` OLD value carries the file's trailing newline, so an OLD anchor ends at a line boundary or is written without one — a mid-line OLD is refused with nothing written, bit 2026-09-22; an `@file` TEXT for `--insert-after|--insert-before` is split on newlines, so a file that ends in a newline inserts one EXTRA blank line: write it with `printf '%s'`, bit twice 2026-09-24, a wiki block and the D-070 row)**.
 
diff -ru a/.claude/skills/ouroboros-stdio/SKILL.md b/.claude/skills/ouroboros-stdio/SKILL.md
--- a/.claude/skills/ouroboros-stdio/SKILL.md	2026-09-25 18:25:44.445782978 +0000
+++ b/.claude/skills/ouroboros-stdio/SKILL.md	2026-09-25 18:25:44.465624411 +0000
@@ -29,7 +29,8 @@
 dangerous input"; paraphrase) — scrub before submitting · nothing is retained between partial
 submissions — resubmit every lane · `ouroboros_generate_seed` returns YAML and writes NO file —
 transcribe to `seeds/` immediately and run the seed's own `verify_command`s (a red first pass is
-the gate working: ours caught a missing per-proof section). **Resume uses the EXACT documented
+the gate working: ours caught a missing per-proof section).
+**Resume uses the EXACT documented
 arg shape** `{session_id, last_question, answer, ambiguity_score}` (the server also writes its artifact store into the PROJECT cwd, `.ouroboros/artifacts/artifacts.db` + WAL, on every interview call — gitignored since 2026-09-22, never committed) — a bare `{session_id,
 answer}` resume and the `ouroboros_session_status` tool both report "No events found" even when
 the session file exists under `~/.ouroboros/data/` (status reads a different store). Interview
```

Not proposed, and why: (a) a break before `**PC gate on EXACTLY the pushed commit` in env-tool-quirks line 76 (the brief
names pc-suite as needing a break): with the whole 74-79 entry, pc-suite is already whole today and stays whole after
such a break, so nothing requires it; it would only let pc-suite be narrowed to the PC gate text. (b) The verifier's D9,
pc-bridge-lanes lines 19 and 23 (4.7 and 4.8 KB single lines): no contract item needs them now, because F4 is fixed in
code (the label and pointer go when no line fits); breaking them would let the `pc-lane` row carry the launch recipe and
allow a systemctl row, a follow-up.

## 8. The contract, item by item (19:1xZ)

1. **F2 whole entries — DONE, 4 rows wait for the skill patch (verified).** Table rewritten (`tools/make_table.py` lists
   every change); push + its CTX1 qualifier (48-49) + the lanes-live entry; push-delegate-work 533-547, now before push;
   test-edit and gate-edit-tactics carry the NaN rule; a call takes or leaves an entry whole (`entry_units`, `compose`,
   `entry_units`/`compose` at `system1-context.py:424-492`); per-entry arrival on the replay in section 5; rows `brief-registers-hook` (a brief
   naming `.claude/settings.json` or `install_session_hooks.py`) and `hook-installer` (a command running the installer).
   `rows_static.py`: 4 runs today, 0 with the patch of section 7.
2. **F10 — DONE (verified).** 8 of 8 mutants KILLED by FAILED tests, each for its reason; the named tests exist (burst,
   held lock, multi-byte boundary, lower-case canary in Write/Edit paths and text, command and prompt across every state
   file, 7-day prune, unresolved skip through the registered command).
3. **F8 — DONE (verified).** A held lock raises `WindowLockTimeout`: nothing injected, nothing written, the type and the
   window logged; docstring rewritten (`WindowLock`, `system1-context.py:735-739`); `conc_dyn.py` held trials `(0, 0, 0)`.
4. **F4 — DONE (verified).** Label and pointer when no line fits, once per window (`compose`, `pointer_only`);
   `f4_prompt_pointer.py` rc 0.
5. **F5 — DONE, target NOT met (verified, DISCREPANCY).** A one-word lead needs 18 (`ONE_LEAD_MIN_SCORE`, `system1-context.py:57`, `:623`); 23 of 23
   strong kept, 19 of 54 weak dropped; the measurement says no lead-count or score rule drops most weak matches without
   dropping good ones (section 3).
6. **F6 — DONE (verified).** `shell_code` (`system1-context.py:149-333`): quotes, heredoc bodies and comments are data unless
   a shell reads them; replay per row before/after and nested commands kept (234 of 234, plus 32) in section 5.
7. **F1 — DONE (verified).** `while|until|if|elif`, `!`, `{` in `CMD_POS`; `f1_while_pgrep.py` rc 0; 5 shapes tested.
8. **F7 — DONE (verified).** Separator-bounded word class and a bulk code scan; the 198 KB data heredoc about 32 ms in
   process, every tested shape under 100 ms; PIN 2,623 ms on 40 KB.
9. **Small fixes — DONE (verified).** F9 (temp file removed on a failed write, `write_json_atomic`, `system1-context.py:695-717`), F12 (`os.path.lexists`, `system1-context.py:813`),
   F16 (per-row skip for a pattern that does not compile or a skill file that fails, logged as `re.error` /
   `FileNotFoundError`), F17 (skill and table reads open non-blocking and refuse a non-regular file, `open_regular`
   `follow=True`), F19 (installer merges hook by hook; `--remove` takes our exact commands only; `_without`, `install_session_hooks.py:71-102`).

## 9. Files (19:1xZ)

MODIFIED (all within the boundary; each PIN version kept in `scratchpad/s1l1r1/prev/`):
- `.claude/hooks/system1-context.py` (live; final sha256 prefix 59fdc31a67931af4)
- `.claude/hooks/system1-situations.json` (live; 9bc5bb4862b28d01)
- `tests/test_system1_context.py` (66cc62ea218b6312)
- `scripts/install_session_hooks.py` (F19 only)
- `tests/test_session_hooks.py` (F19 only: two tests)
CREATED: this report. No new file under `.claude/`: the two changed files move the vendored manifest's `.claude/` row
(regenerate at commit), and so will the skill patch when applied. Not mine, seen changing in the tree while I worked:
`.claude/hooks/edit-snapshot.py` (AF-AP-223 screen, since committed), other lanes' files; none touched.

## 10. NOT done (first-class)

- The skill patch is NOT applied (skills are outside my boundary): until the coordinator applies section 7, rows
  ops-script, anchor-edit, ouroboros and stamp deliver part of an entry, as they did before, and `rows_static.py` reports 4.
- F5's weak-match target is NOT met (19 of 54). A cover-aware rule (score the excerpt that would go, not the whole
  section) is the candidate; NOT built.
- The prompt path is still NOT verified live: no UserPromptSubmit record reached this container's log since the change.
- The registry and bug-echo step of the build loop is NOT done (`docs/INCIDENT-LOG.md` is outside my boundary). Classes
  found, for the coordinator: (a) a regex value `\S*` that runs through `$(` hides the command inside `NAME=$(cmd …)`
  (PIN false negatives, 127 matches); (b) a shell scan that treats `\` + newline as an escape (my own first version) or
  as a new line (the PIN) mis-places command positions; (c) a mutation harness that scores exit codes (the AF-AP-223 the
  coordinator already screens).
- The verifier's D9 lines and the optional pc-suite narrowing (section 7) are NOT proposed as patches.
- F24 and F25 (UNVERIFIED in the verify report) and F18 are not in this brief and are untouched.

## 11. Deviations and discrepancies (loud)

- D-R1. Scratch: `scratchpad/r1` is someone's file; I used `scratchpad/s1l1r1/` (31 MB at its largest, 860 KB after the cleanup: the previous file versions,
  the candidates, my tools and outputs, the fixed harness copy and the patch).
- D-R2. `rows_dyn.py` cannot pass unmodified: its first line asserts the PIN's 38 rows, and item 1 adds two. Run as is
  (rc 1 at that assert) and on the new table minus the two rows (rc 0, only F3).
- D-R3. `rows_static.py` exits 0 only with the skill patch; the test file encodes the 4 pending runs (PENDING_BREAKS).
- D-R4. F5: "drops most of its 54 weak ones" not met (section 3).
- D-R5. `hostile.py` prints 3 BAD lines by F16's design; `prompt_dyn.py` flags prompt 24 by F4's design.
- D-R6. `test_the_budget_counts_bytes_not_characters` fails on the PIN by signature (`ValueError`), not by its reason; its
  red evidence is m2.
- D-R7. F19 went a step past `--remove`: the install also merges hook by hook now, so a foreign hook in one of our groups
  survives an install too. The install still replaces any hook naming `<repo>/.claude/hooks/` (it must, to replace an
  older spelling of ours), so an owner's own hook in that directory survives `--remove` but not the next session start.
- D-R8. Side effects of F16 and F8 in the telemetry: error types are module-qualified (`json.decoder.JSONDecodeError`,
  `re.error`), and error records carry `window` when known (the verifier's key-set table in its section 6 changes).
- D-R9. Behaviour beyond the named findings: the first word inside a quote or heredoc a shell reads is now a command
  (32 new nested matches), and commands inside `NAME=$(…)` are now seen (127 new plain matches; section 5).
- D-R10. The replay's cost side: bytes +5.7 %; windows where a row's lines never all arrived 38 -> 54 (push 17, brief 13,
  test-edit 12, code-edit-guidelines 6, brief-contract 6), each a whole entry waiting for a call that never came.
- D-R11. The hook was swapped live three times (18:51:14Z, 18:54:24Z, 19:05:39Z) in a shared container; the first two
  versions missed commands after a line continuation (section 5).
- D-R12. A line already delivered in a window is never repeated (the builder's D3), so an entry whose other lines arrived
  earlier goes as its remainder: seen live at 18:51:55Z (test-gate delivered line 75 alone, the PIN having delivered 74
  and 76-79 in this window before the swap).

## 12. Self-attack: the three likeliest ways this is wrong

1. **The shell lexer is wrong on a shape the replay does not hold.** Shell grammar is large: `bash <<< "cmd"` is read as
   data, a `case x in a)` inside `$(` closes the substitution early, `$((1<<3))` followed by a newline would open a
   heredoc. Ruled out as far as two instruments reach: on the 16,983 real calls, of 2,648 lost matches, 2,535 are data by
   the verifier's own masking too, 30 disagree where the shape shows the verifier's mask is naive, 75 + 1 are PIN false
   positives, and 7 follow a line continuation. NOT ruled out: shapes absent from this transcript.
2. **Whole entries cost more context and deliver later entries less often.** Not a defect of the code; measured and
   reported (D-R10, the per-entry table). The coordinator may prefer the old line-cut for some rows; the budget and the
   row order are the levers.
3. **The F5 threshold is tuned near one acceptance prompt.** 18 sits 0.79 under the F4 reproduction's best score (18.79),
   so a skill edit can turn `f4_prompt_pointer.py` red without any code change. My committed F4 test uses a four-word
   lead (52.66) and does not depend on that margin; the reproduction script does.

## 13. Evidence tiers

- **Verified** (run here, output pasted above): the premise; the harness fix and its negative control; red on the PIN
  and green on the candidate; 8 of 8 kills with their reasons; the F5 table; the replay before and after; the per-entry
  arrival; the nested and lost counts with the second instrument; every reproduction after the move; the gate twice
  (164 passed, set 2dc71b948b8b); pyflakes rc 0; the separator counts; `git apply --check` of the patch; the patched-skill
  runs (`rows_static.py` 0, 129 passed); the live telemetry after each swap (78 records since 18:51:14Z, no error, median
  3.1 ms, max 14.4 ms); `report_lint.py`: `report_lint: 8 refs — OK 8, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.
- **Inferred**: that the 7 continuation losses are mostly arguments (shell grammar; shapes only, no text read); that the
  30 two-instrument disagreements are the verifier's naive quote masking (shapes only); that the prompt path behaves live
  as in the replay (no live prompt record since the change).
- **Assumed**: that the coordinator applies the section 7 patch at commit, and regenerates the vendored manifest.
