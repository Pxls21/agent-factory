# S1-VIEW-GUARDS (task #460): build report, relaunch

Stamped 2026-10-02 05:2xZ. HEAD at finish: the coordinator's local commit "Task #454: the deployed SGLang arm measured (report section K7)"; the coordinator kept committing during the run. (The coordinator replaced the lane's two local commit ids, here and in section 1, before the push: the push rewrites local ids.) PIN: `2979159415b0629ae4d564e5e62ca912aa01a9a8`. Boundary: `scripts/s1_train/view.py` and `tests/test_s1_train_view.py` only. Both are uncommitted. No other path was touched.

Tiers: **[V]** measured in this run. **[I]** inferred from code I read. **[A]** assumed.

## Summary

- **view.py:** D-8 to D-11 are built. I kept every code line of the predecessor's diff. I changed one docstring paragraph. **[V]**
- **Tests:** the D-12 fixture items and tests are built. Run twice: `pytest-summary: 92 passed in 9.18s` and `pytest-summary: 92 passed in 9.21s`. **[V]**
- **Mutants:** 35 of 36 are killed. N19 survived; it is equivalent (shown below). None was INVALID. **[V]**
- **Old fixture:** on the PIN's own fixture, `view.jsonl` is byte-equal to the PIN's (sha256 `fe15dfc84d409d72`, 9 rows). **[V]**
- **DEVIATION (loud):** every `--out` in the test file now lies outside any git work tree.
  - Why: D-10 refuses an `--out` inside a work tree, and `scripts/pc_suite.sh` puts its basetemp inside the PC clone (`$PC_AF_REPO/.suite/<id>/tmp`).
  - Before the change, with such a basetemp: `pytest-summary: 26 passed, 66 errors in 2.94s`. After: `pytest-summary: 92 passed in 9.07s`.
  - The change touches 39 lines of the PIN's tests mechanically. See section 9.
- **NOT done:** the real run (the coordinator's), any PC suite run (no bridge), the commit.

## 1. Premise (demand 1)

**At relaunch, 04:0xZ [V]** (HEAD was the commit "Task #454: the SGL-SMOKE lane brief", origin `e8e4e5d8`). Every line matched the brief except the diff-stat line, as the coordinator expected:
- The PIN is an ancestor of HEAD.
- The diff-stat printed the predecessor's two lines; the diff's sha256 prefix was `a614d36d8ffac68e`.
- The log line was `92d74958 Task #444 landed …`.
- sha256: `__init__` `e3b0c44298fc1c14`, `render` `901c086a6a90f90a`. The PIN blobs: view `16f1905ce72aee78`, test `439c3fc55d0d5c3f`.
- wc: 125, 357 and 888 on the PIN blobs.
- set-id: `1 files set=470c76f8303f`.
- The PIN copy's tests: `pytest-summary: 61 passed`.
- The grep lines matched on the PIN blob.
- The verify report's sha256 was `85fdf2dbfb50`.

**At finish, 05:2xZ [V]:**

```
PIN-is-an-ancestor-of-HEAD
 scripts/s1_train/view.py    | 164 ++++++++---
 tests/test_s1_train_view.py | 664 +++++++++++++++++++++++++++++++++++++-------
 2 files changed, 686 insertions(+), 142 deletions(-)
92d74958 Task #444 landed (GATED-PENDING-VERIFY): … (unchanged: the work is uncommitted)
e3b0c44298fc1c14 scripts/s1_train/__init__.py
901c086a6a90f90a scripts/s1_train/render.py
9ca2bece43af9a9f scripts/s1_train/view.py        (PIN blob still 16f1905ce72aee78)
668e4b46b7e241da tests/test_s1_train_view.py     (PIN blob still 439c3fc55d0d5c3f)
125 / 429 / 1360 lines (PIN blobs: 357, 888)
1 files set=470c76f8303f
85fdf2dbfb50 (verify report)
```

**Read set [V]:** no code file in the brief's READ list changed since the PIN. The only additions are the brief and the verify report themselves, both added by `936ee2ed`.

## 2. Review of the predecessor's view.py diff against D-8 to D-11

I read every hunk of `git diff -U0 PIN -- view.py` (33 hunks). I kept every code line. I fixed one docstring paragraph. **[V]**

| Hunk | Decision | Check against the brief |
|---|---|---|
| Docstring :20, "the LAST tool call" | KEEP | Matches `before[-1]` (:290) and F25. |
| Docstring :23-31, the guards paragraph | **FIXED (wording only)** | It called all three shapes "record orders", but the third is an exporter cut. It also spoke of "a found id" meeting a guard, but a guarded id is never counted found. I rewrote it in D-8's terms: an id with one carrier, the three guards in order, counted once under the first, the two refusals first. The old wording is not quoted here. |
| Docstring :35-41 (D-11, D-9) and usage :44-45 (D-10) | KEEP | Accurate. |
| `VERSION = "s1-view-v2"` :67; `GUARDS` :69 | KEEP | D-8. |
| read_build: `RecursionError` added at :110, :118, :125, :154 | KEEP | D-9. Each catch has its own killing test (section 6). |
| read_manifest: `RecursionError` added at :168 | KEEP | D-9. |
| read_manifest D-11 block :175-187 | KEEP | `realpath(join(root, output))`. A NUL raises `ValueError`, caught at :179. Outside the export directory (and `path == root`) is refused at :181. Two outputs on one file are refused at :184. Each reason names the entry's `src`. |
| stream_events(path, entry) :191 | KEEP | It reads the resolved path. The `src` check is at :218 (D-11). `RecursionError` is caught at :224 (D-9). |
| facts_of: `hooks`, `results`, the guard chain :259-285 | KEEP | Checked against D-8 in the next list. |
| view(): resolved paths; try around render and facts_of :307-311 | KEEP | `R.UnknownPair` is a `ValueError` subclass (render.py:49); the D9-render-value mutant proves that is the only catch that holds it. |
| view(): five-key `not_found` :322; drop :340-342; stdout :368-372 | KEEP | D-8. The source refusal (:334) and the D-3 refusal (:336) come first; mutant X1 pins that order. |
| check_out :376-393 | KEEP | The link rule (:381) runs before anything else. The git walk (:383-389) runs from `realpath(out)` up to `/`. `ValueError` is caught at :392. |
| write :396-408 | KEEP | `check_out` runs again at :397. `makedirs` moved inside the `try`. `OSError` becomes Refused (D-9). |
| main `--out` help :415 | KEEP | |

**D-8 checked line by line [V]:**
- **same_call_hook_in_state (:278):** `call_id is not None`. Some `k < j` (before index s) is a hook event whose text is a JSON dict and which renders, with `toolUseID == call_id` and `hookEvent == event`.
  - "Renders" is coded as `ends[k] > starts[k]`. That equals `block(event) != ""`, because render's `starts` are cumulative block lengths, one per event (render.py:117-125).
- **own_result_in_state (:280):** `event == "PreToolUse"`, `kind != "tool_result"`, and a `tool_result` with `call_id == call_id` at some `k < j`.
- **carrier_truncated (:282):** `events[i]["truncated"] is not None`.

## 3. Files and lines (final)

- **`/home/user/agent-factory/scripts/s1_train/view.py`:** 429 lines, sha256 `9ca2bece43af9a9f`, numstat `118 46` against the PIN. My only edit is the docstring paragraph at :23-31; the rest is the predecessor's diff. The key lines are cited in section 2.
- **`/home/user/agent-factory/tests/test_s1_train_view.py`:** 1360 lines, sha256 `668e4b46b7e241da`, numstat `568 96`.

Key lines in the test file:

| Lines | What |
|---|---|
| :1-22 | Docstring with a task #460 paragraph |
| :54-57 | `SID2`, `GUARD` |
| :70-77 | The new ids and `DROPPED` |
| :84 | `LONG2` (4,549 characters) |
| :100 | `CAND` |
| :226 | `capped` |
| :235 | `EXPORT_CAP`, `EXPORT_HEAD`, `EXPORT_TAIL` |
| :238 | `cut_injection` |
| :296 | `run_blocks` (F16) |
| :387 | `build_guard` |
| :570-578 | `OUT_ROOT`, `_out` |
| :595 | `_out_root` fixture |
| :608 | `world` |
| :735, :754, :765 | The found, absent-id and summary tests (updated) |
| :878 | The F16 run test |
| :895-944 | The D-8 tests |
| :1103 | The build race test |
| :1174 | `test_write_checks_the_out_again` |
| :1195-1279 | The D-9 tests |
| :1281-1310 | The D-10 tests |
| :1313-1360 | The D-11 tests |

## 4. The GUARD fixture (D-12, demand 2)

A second session, 58 raw records. They follow `tests/test_session_export.py`'s builders. The real exporter CLI exports them (`init-key` FAKE key, a fixture repo, `--known-values key-only`). `build_s1.write_split` writes the frozen build. **[V]**

| Seq | Item | Outcome |
|---|---|---|
| 0, 1 | A run at the file's first event (ID_FIRST) | found, state 0 (kills N31) |
| 2 | An owner text with exactly two LFs | rendered with one LF (kills N1) |
| 3 to 5 | O8: a rendered UserPromptSubmit hook, a notification, the stamp | dropped, same_call |
| 7 to 13 | O5: a run split by a notification (11) | O5A found (state 9); O5B dropped, same_call |
| 14 to 21 | O7: another call's result (19) splits call 02's run | O7B dropped, same_call |
| 22 to 25 | O6: the call's own result before its PreToolUse run | dropped, own_result |
| 26 to 29 | G12: guards 1 and 2 both hold | counted under same_call (the order) |
| 30 to 33 | A denial with its call's PreToolUse hooks before it | found, state 31, step 30 |
| 34 to 37 | A candidate over 4,000 characters | found; block capped, candidate whole (kills N39) |
| 38 to 41 | CR LF and LF LF in a chunk | found; `candidate_vs_chunk` equal (kills N26) |
| 43, 44 | A hook whose call is not in the file | found; step_found false (kills N53) |
| 45 to 50 | One call id twice | found; step 47, the LAST call (F25; kills N10) |
| 53 | q3b: a carrier the exporter cut | dropped, carrier_truncated |
| 56 | G23: guards 2 and 3 both hold | counted under own_result |

Ids out of state order: ID_FIRST `s1-0000e009` comes first in GUARD by state and last by id, which kills N14 and N15.

**q3b came from the real exporter.** The stamped text is under 9,500 characters, so the stamp shape is valid. Control characters (`chr(1)`) escape to 6 characters each in canonical JSON, which pushes the attachment past the 32,768-character cap. `test_the_exporter_cut_each_cut_carrier_and_its_json_still_parses` asserts three things: `truncated == {kept_head 24576, kept_tail 8192, dropped}`, the exact kept text, and that the middle is gone.

**Negative control [V]:** on the scratch copy I set the exporter's `HEAD` from 24576 to 24571. Result: `3 failed, 89 passed`, with the cut test failing on `{'kept_head': 24571} != {'kept_head': 24576}`. The exporter was restored and its sha256 checked.

## 5. Pasted counts (demands 8 and 9)

```
pytest-summary: 92 passed in 9.18s          (run 1, --basetemp <scratch>/bt)
pytest-summary: 92 passed in 9.21s          (run 2)
1 files set=470c76f8303f                    (bash scripts/pc_suite.sh set-id -- tests/test_s1_train_view.py)
pytest-summary: 92 passed in 9.07s          (basetemp inside a git work tree, the PC suite's layout; after _out)
pytest-summary: 26 passed, 66 errors in 2.94s   (the same, before _out)
pytest-summary: 92 errors in 2.92s          (control: TMPDIR inside git; _out_root's precondition fires, naming its root)
pyflakes rc=0 (both files)
separator check: printed 0 (grep rc 1), both files
```

## 6. Mutant table (demand 7)

- **Where and when:** scratch copy `<W>/mut` (the PIN tree plus the final two files). The harness checks that the copy equals the working tree before it starts. Runs: 05:16Z to 05:23Z on the final files.
- **Setup:** `COLUMNS=1000`; baseline `92 passed` first in each batch.
- **Scoring:** a kill needs a FAILED test. An error-only run, or a run that lost tests, is INVALID (AF-AP-223). I fixed my harness to this rule before the final runs; the earlier saved runs had no error lines.
- **Totals:** batch 1, `KILLED 18 SURVIVED 1 INVALID 0`; batch 2, `KILLED 17 SURVIVED 0 INVALID 0`. `TREE RESTORED: True` after both.

| Mutant | Edit | Verdict | Test that failed |
|---|---|---|---|
| N1 | render `\n{2,}` to `\n{3,}` | KILLED | render, found, absent, summary |
| N10 | `before[-1]` to `before[0]` (step from the first call) | KILLED | found |
| N14 | sort by (src, id) | KILLED | found |
| N15 | no sort | KILLED | found |
| N19 | `lexists(out)` to `exists(out)` | **SURVIVED: equivalent** | none (see below) |
| N20 | `check_out` in `write` removed | KILLED | write_checks_the_out_again |
| N26 | chunk without the newline rule | KILLED | summary |
| N31 | `while j > 1` | KILLED | found, summary |
| N33 | `isinstance(seq, int)` | KILLED | schema[seq_bool] |
| N39 | `R.body` on the candidate | KILLED | found |
| N49 | no walk for a tool_result carrier | KILLED | absent, ambiguous, guard_item, found, summary |
| N53 | step_found always true | KILLED | summary |
| G1-off | same_call off | KILLED | dropped_row, absent, ambiguous, guard_item, found, **F16 run test**, summary |
| G2-off | own_result off | KILLED | dropped_row, absent, ambiguous, guard_item, found, summary |
| G3-off | truncated off | KILLED | same 6 |
| ORD-213 / ORD-132 / ORD-321 | guard order swapped | KILLED (each) | absent, ambiguous, guard_item, summary |
| X1 | guards before D-3's refusal | KILLED | dropped_id_seen_before_its_state_ends |
| D9-build-summary | RecursionError out | KILLED | nested[build_summary] |
| D9-build-split | RecursionError out (load_dataset) | KILLED | nested[build_dataset] |
| D9-build-manifest | RecursionError out (second parse) | KILLED | split_manifest_swapped_for_a_nested_one |
| D9-build-labels | RecursionError out | KILLED | nested[build_labels] |
| D9-export-manifest | RecursionError out | KILLED | nested[export_manifest] |
| D9-output-path | ValueError out (NUL) | KILLED | manifest_output_with_a_nul |
| D9-export-line | RecursionError out | KILLED | nested[export_line] |
| D9-render-recursion | RecursionError out | KILLED | hook_text_nested (Q7a) |
| D9-render-type | TypeError out | KILLED | role_is_a_list (Q7b) |
| D9-render-value | ValueError out (UnknownPair) | KILLED | unknown_role_and_kind |
| D9-write | OSError out | KILLED | out_that_cannot_be_made (Q7d) |
| D9-check-out-value | ValueError out (NUL) | KILLED | out_with_a_nul |
| D10-link-off | link rule off | KILLED | symlink[link, link-slash, link-dot, dangling], write_checks_the_out_again |
| D10-git-off | git rule off | KILLED | git[a_work_tree, a_new_path_below, a_git_file, through_a_link], write_checks_the_out_again |
| D11-outside-off | outside check off | KILLED | outside[dotdot, absolute, symlink] |
| D11-one-file-off | one-file check off | KILLED | one_file[another_spelling, symlink] |
| D11-src-off | src check off | KILLED | src_is_not_its_entrys |

**Why N19 is equivalent [V]:** a probe called `check_out` from the real file and from the mutant on 17 `--out` forms: new, empty, full, file, link, `link/`, `link/.`, dangling, `dangling/`, `dangling/x`, loop, `loop/`, `loop/x`, `file/x`, `new/a/b`, `empty/../link` and `full/../dangling`. The result: `forms 17, outcomes equal 17`. The reason: `exists` and `lexists` differ only on a symbolic link, and `islink(abspath(out))` refuses every link before line :390 runs.

**D9-build-manifest, both readings (rule 5) [V]:**
- First reading, and why it was wrong: I first took this catch as unreachable. The mutant survived (batch 2, 04:3xZ), so I re-read read_build. It parses its own `raw` bytes, which it read before `load_dataset` reads the files again, so a writer between the two reads reaches the catch.
- Change made: I added the monkeypatch race test, and the mutant is now killed.

## 7. Evidence demands

| # | Status |
|---|---|
| 1 | Done (section 1). |
| 2 | Done. Real producers. q3b was made by the exporter's own cut, with a control (section 4). |
| 3 | Done. `view.jsonl` is byte-equal to the PIN's on the PIN fixture (`fe15dfc84d409d72`, 9 rows). The summary differs only in `version`, the three new zero `not_found` keys, and view.py's code digest. The new items are found or dropped as D-8 says. Counts in GUARD: same_call 4, own_result 2, truncated 1. Stdout: `s1-view: 24 build ids, 16 found, 1 not in the export, 0 ambiguous, 7 dropped by the guards; 3 files, 106 events, …`. |
| 4 | Done. Every refusal test asserts exit 2, the reason, empty stdout and nothing written (`_refused`). Two exceptions run in-process and assert the exact `Refused` text: the race test and `test_write_checks_the_out_again`. main's single `except Refused: return 2` turns every Refused into exit 2, which the CLI refusal tests exercise. |
| 5 | Done. The marker, FAKE key and own-id tests pass. `test_a_dropped_row_reaches_no_output` checks every dropped id and its text (for a cut carrier, the HEAD and TAIL parts it kept): each is present in the stream and absent from `view.jsonl`, `summary.json`, stdout and stderr. |
| 6 | Done. `test_two_runs_give_byte_identical_outputs`, plus pin_compare: each view.py run twice gave identical output. |
| 7 | Done (section 6). |
| 8 | Done (section 5). The file runs in about 9 s. |
| 9 | Done. The AP tells are answered in the next table. |
| 10 | NOT run here (the coordinator's). |

**AP screen tells (7) [V]:**

| Tell | Answer |
|---|---|
| AP-32, view.py:90 `sha256_text` | It hashes the text's UTF-8. The stored digests it feeds (`candidate_sha256`, `streams.sha256`) are made only by this function. The test's oracles hash the same form (test :750, :777). |
| AP-32, view.py:200 | The file's bytes against `output_sha256`, which the exporter writes over the same bytes. Every world run matches, and the sha-mismatch test refuses. |
| AP-32, test:83 | Derives a marker; never compared with stored data. |
| AP-32, test:511 `_sha` | File bytes. The same form as the build's `files` digests and the export's `output_sha256`. |
| AP-32, test:750 and test:777 | Oracles in the code's own form (UTF-8 of the expected text). |
| AP-51, view.py:47 | A byte-identity claim. No dataclass or `asdict` is involved; the rows are fixed-key dicts (`ROW_KEYS` is asserted). The two-run test and pin_compare measure it. |

## 8. Self-attack: the three likeliest ways this is wrong

1. **D-10's git rule refuses an `--out` the coordinator means to use [I].**
   - It refuses any path under a `.git`, gitignored folders included.
   - Two places are hit: `scripts/pc_suite.sh`'s basetemp (`$PC_AF_REPO/.suite/<id>/tmp`), and `.jev/…` under the repo. `build_s1.py`'s docstring suggests `.jev/…` as "outside git" for its own output.
   - Ruled out for the tests: `_out`, plus the git-venue run (92 passed; 26/66 before).
   - **Not ruled out for demand 10:** the real run needs an `--out` outside every work tree, or it exits 2. The rule is the brief's (D-10), so the code follows it.
2. **My guards differ from the verifier's counts-only measure [V for the fixture, I beyond it].**
   - "Renders" is proven from render.py (section 2). D-8 is copied literally, including `None == None` (see section 10).
   - The real run's three zero counts can confirm agreement only on shapes today's export holds.
3. **The fixture is tied to the exporter it was written against [V].**
   - q3b depends on CAP/HEAD/TAIL, which the test restates.
   - If the exporter changes, `cut_injection`'s asserts error at setup, or the cut test fails (the control shows `kept_head` 24571 vs 24576). Neither turns into a silent green.
   - `_out` assumes the system temp dir lies outside git. The fixture asserts it (control: 92 errors naming the root).

Also weighed: the race test simulates the writer with a monkeypatch; it does not run a real concurrent writer. The mutant shows the catch it covers is load-bearing.

## 9. Deviations (loud)

1. **The `_out` change (not in the brief).**
   - Every `--out` now comes from `_out(tmp_path)`, under a module root made by `tempfile.mkdtemp` (`_out_root`, :595). The fixture asserts the root lies outside git and removes it afterwards; 0 roots were left in `/tmp`.
   - Lines touched: the 39 PIN lines with `tmp_path / "out"`, the world fixture's `--out`, and `full` in `test_write_checks_the_out_again`.
   - The "no host path" check at :796-798 now also covers the `--out` root. Before the move it held through `world.base`, which then contained the `--out`.
   - No other assertion changed.
2. **The mutant set goes beyond the brief's list.** I added X1 and D9-render-value. The 12 D-9 catches are my own enumeration.
3. **Venue assumptions:**
   - Q7d uses `/proc/zq-s1-view-<pid>`, which assumes Linux `/proc` and no `.git` at `/` or `/proc`.
   - The NUL `--out` test calls `V.main` in-process, because argv cannot carry a NUL.
4. **A disclosure, not a code change:** I ran `python3 scripts/stack.py gate … mode=plan` once. It writes its run record under `.jev/stacks/`. I read only its stdout.

## 10. Discrepancies and adjacent observations (not fixed)

- **The PC suite's basetemp** lies inside the PC clone (`scripts/pc_suite.sh:59`, `:86`). Any CLI with D-10's rule is refused there. This file no longer depends on it; a future test could.
- **The real run's `--out`** must be outside every work tree (section 8, item 1).
- **own_result_in_state with a null call id:** `c == call_id` matches a `tool_result` whose `call_id` is null. This is literal D-8; I flag it, not fix it.
- **A non-str `state.chunk`:** a build row whose `state.chunk` is not a str would raise AttributeError in `R.newlines` and exit 1 [I]. That is not one of D-9's three classes.
- **A link in a parent of `--out`:** a symbolic link in a parent component is followed. D-10 covers the `--out` itself; the git rule checks the resolved path.
- **F23 (out of scope):** an OSError between the two `os.replace` calls leaves `view.jsonl` without `summary.json`. This is unchanged.
- **Under a dangling link, a loop or a file:** an `--out` there passes `check_out`, then `write` exits 2 with `[Errno 2]`, `[Errno 40]` or `[Errno 20]`, and nothing is written [V, earlier probe].
- **My own harness had AF-AP-223's flaw:** it scored ERROR as a kill until 04:5xZ. I fixed it before the final table.
- **The gate union:** ripwire's union lists 46 test files. Nothing else imports or runs view.py (grep over scripts, src, proofs, tests, harness-ports and the hooks), so I ran only its own file.

## 11. NOT done

- **The real run (demand 10):** the coordinator's job. Expected: `view.jsonl` byte-equal to task #444's, three zero guard counts, the same 19 counts. It needs an `--out` outside git.
- **A PC suite run:** no bridge under the standing rules. Only the set-id was printed.
- **Commit and push:** the coordinator's.
- **The other 45 files in the gate union:** not run (reason in section 10).
- **`report_lint`:** not run.
- **The served model of this lane:** not measured; that is the coordinator's harvest.

Scratch evidence is in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/g460-jgyA1S/`:
- the mutant harness: `mutants.py`
- the mutant logs: `final-mut-1.log`, `final-mut-2.log`
- the scripts: `pin_compare.py`, `n19_probe.py`, `cut_control.py`
- the run logs: `gate-1.log`, `gate-2.log`, `gitvenue.log`, `tmpdir-control.log`