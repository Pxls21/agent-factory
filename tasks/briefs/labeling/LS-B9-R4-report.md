> Coordinator note (2026-09-29 03:2xZ): the report of record, extracted by `scripts/stack.py harvest` (round 4's own harvest, whose new `local_ids` step read "none cited"). Served model: claude-opus-5-5 on every assistant record of this lane (1,454 across its four rounds), 0 refusal stops; `report_lint` 57 refs, all OK. The id `755e900` in its real runs was the local id of the commit "Retro of the CI fix: task #356 registered (a gate under CI's Python); live-state names origin 975523a", which the push since rewrote; `d773575` (NOT done 5) was rewritten by an earlier push. Both appear as evidence of what the step prints, not as citations.

## Round 4 (four fixes, the catalog notes, local ids in a hand-back, the SessionStart catalog)

Written 2026-09-29 from 03:2xZ (clock read at 03:22:35Z; state re-checked at 03:26:35Z) by the original LS-B9 builder, resumed. Brief: `tasks/briefs/labeling/LS-B9-R4-brief.md`, read in full.

- Files changed: the brief's six (`scripts/stack.py`, `scripts/stacks.toml`, `scripts/handback_extract.py`, `tests/test_stack.py`, `scripts/install_session_hooks.py`, `tests/test_session_hooks.py`). No new helper.
- The repo's `.claude/settings.json` is unchanged. Running the installer changed `/home/user/.claude/settings.json` (D1).
- No git write to the project, no PC bridge, no subagent, no outward action.

### TL;DR

- **Done:** items 1 to 7 and 6b, each with a test and a killed mutant. Item 8's gates ran twice each.
- **Red first:** the final tests on round 3's code give `28 failed, 202 passed in 55.54s`.
  - The 28 are exactly the round-4 feature tests.
  - The gap tests (X1, X2, X3, X6) pass on round 3's code, as they should. Each kills its own mutant.
- **Mutation on the final bytes:** `TOTAL=29 KILLED=29 SURVIVED=0 INVALID=0`. This includes the verifier's X1, X2, X3 and X6.
- **Gates:**
  - A: `3 files set=cebb397be3f6`, `296 passed` twice.
  - B: `5 files set=2804489b9d6b`, `482 passed` twice (runs 3 and 4). Runs 1 and 2 had `1 failed`: a cold-cache timeout inside the search-intercept hook, not my code (D7).
  - C (added: two more tests name my files): `2 files set=a9d6e3f9b705`, `190 passed` twice.
  - CI rehearsal (uid 1000, Python 3.12.3, CI's own installs, no instrument on the PATH): `228 passed, 2 skipped`.
- **Wired:** the installer registered the catalog hook in `/home/user/.claude/settings.json`; a second run printed `unchanged`. The installed command prints 2,681 characters (2,704 bytes, 19 lines), exits 0 and writes nothing to stderr.
- **Citations:** checked with `scripts/report_lint.py` on stdin (the harness refuses a subagent's report file): `57 refs — OK 54, NEAR 0, MISS 0, UNCHECKABLE 3`. The three got longer claim tokens: `3 refs — OK 3`.

### NOT done (first-class)

1. **The CLAUDE.md pointer line** is proposed below, not written. It is the coordinator's file.
2. **The repo's `.claude/settings.json` does not register the catalog.**
   - The installer writes only `<repo parent>/.claude/settings.json`, and the brief forbids a hand edit.
   - A session rooted at the repo (not this CCR session) gets no catalog until someone adds the entry.
   - The entry, in the repo file's spelling, as the third SessionStart group:
     `{"matcher": "startup|resume|compact", "hooks": [{"type": "command", "command": "[ -f $CLAUDE_PROJECT_DIR/scripts/stack.py ] || exit 0; python3 $CLAUDE_PROJECT_DIR/scripts/stack.py catalog || echo \"stacks: no catalog (scripts/stack.py catalog exited $?)\"", "timeout": 30}]}`
   - `tests/test_session_hooks.py` does not pin it yet.
3. **No kill-switch file for the catalog hook.** The orchestration skill's hook contract names one; this brief does not. To turn the catalog off today:
   - `install_session_hooks.py --remove` removes all eight hooks, and `scripts/setup.sh` installs them again at the next session start;
   - or edit the file.
4. **I did not see the hook fire live.** No session started, resumed or compacted during my run.
   - I ran the installed command by hand through `sh`; its output is under item 7.
   - ASSUMED: the harness matches `startup|resume|compact` against its SessionStart `source` (the documented values are startup, resume, clear and compact).
   - The live proof is the coordinator's next compaction.
5. **6b checks only the CURRENT local range.** An id that an earlier push already rewrote is neither local nor on origin, so it is not flagged.
   - Example: my round-3 hand-back cites `d773575` twice. That commit is on no origin branch now, and `--local-ids` prints `none cited`.
   - The step does its job at harvest time, before the push.
6. **F-13's class stays open.** With a very long `paths`, each step's `$ argv` head line is long too, so the step status lines still fall out of the print. Only the header up to the counts line is protected (R3-F1, as the brief specified).
7. **Not in this round:** R3-F2 (a setsid child escapes), F-4, F-5, F-6, and the INFO items.
8. **Rounds 1 to 3's mutation sets were not re-run.** Their drivers were in removed scratch dirs. Round 4 ran 29 new mutants.
9. **`harness-ports/tests/run-all.sh` was not run.** It is not in this brief's gates. A test and a plan-mode real run show X3's routing.
10. **The defect classes I found are not registered** in `docs/INCIDENT-LOG.md` (not my file). They are listed under "For the registry".

### DISCREPANCIES

- **D1. `.claude/settings.json`.** The brief's boundary line and `.lanes-live` name the repo's `.claude/settings.json`. But `scripts/install_session_hooks.py` writes `<repo parent>/.claude/settings.json`, which is `/home/user/.claude/settings.json` (its default target since task #214).
  - Running it changed that file: sha256 prefix `21ca48e4d8777127` to `ab456303e3b74530`; mode `644 root` kept.
  - The repo's file is untouched: `git status --porcelain -- .claude/settings.json` prints nothing.
- **D2. R3-F3's rule, refined.** In every transcript I measured, "the first user record after the previous call" is the call's own tool result, a user record right after each call. Taken literally, the fix would change nothing. So the window opens at the first user record that carries text and is neither a tool result nor a compaction summary.
  - Measured in this session's tasks dir: 23 transcripts with two or more calls. After every call, the first such record was one of:
    - the coordinator's message (`"origin": {"kind": "coordinator"}`);
    - a `[handback-send-enforce]` message;
    - a compaction summary (`isCompactSummary`).
  - Among 23,522 tool-result user records, none also held a text block.
  - The verifier's synthetic shape had no tool-result record.
- **D3. Two of issue #80's seven notes are amended,** because this round fixes what they warn about. The other five are verbatim.
  - gate, verbatim: "Read the counts line; `mode=run` refuses more than `max_files` (40); past about 180 paths read `sources.out` (R3-F1)." Now: "Read the counts line; `mode=run` refuses more than `max_files` (40)."
  - harvest, verbatim: "On a resumed lane, check `harvest`'s `report:` line (R3-F3)." Now: "On a resumed lane, check the `report:` line: the report window opens at the resume message, so no earlier round's text is this round's report (R3-F3)."
  - To restore the verbatim text: edit `scripts/stacks.toml` and the `NOTES` table in `tests/test_stack.py`.
- **D4. Where issue #80's text came from.** I took it from the coordinator's scratchpad file `issue-lsb9.md`, the body the issue was filed from at 23:00Z; its `.json` twin is identical. I did not read it from GitHub. ASSUMED equal to the live issue.
- **D5. 6b scans two files.** It reads the hand-back file and also the file the extractor chains (the lane's longer text report, when one was saved). The brief says "in the hand-back". Either file can become the committed report. A path given twice is read once.
- **D6. Added, not asked: a catalog marker in the installer's merge rule.**
  - The rule now names `<repo>/scripts/stack.py catalog` as ours (`scripts/install_session_hooks.py:113` `catalog_marker`, used at `scripts/install_session_hooks.py:117` `catalog_marker`).
  - So a later spelling of the command replaces the old one instead of printing the catalog twice.
  - Tested by `test_an_older_catalog_spelling_is_replaced_on_install`; mutant I3.
  - The installer now prints `installed 8` (was 7), and its docstring says eight hooks.
- **D7. Gate B went red twice, then green twice.**
  - Runs 1 and 2 (02:55Z and 02:57Z) gave `1 failed, 481 passed`. Both failures were `tests/test_search_intercept.py::test_an_answer_searches_what_the_raw_call_searches`: the hook's answer to a Bash `grep -rn` was empty.
  - Following AF-AP-237, I questioned the gate first:
    - For a Bash grep, the hook runs rg with `--hidden` only (`.claude/hooks/search-intercept.py:911` `_GREP_TOOL_SCOPE`), under a 10-second rg budget (`.claude/hooks/search-intercept.py:59` `RG_TIMEOUT_S`).
    - That walk includes `.git`: 27,067 loose objects, 511.71 MiB (`git count-objects -vH`).
    - With a cold cache, the hook's exact rg command ran past 60 s, and my timeout killed it. With a warm cache it took 0.67 s.
    - Run by hand, the hook took 10.1 s and failed open with an empty answer.
    - Once the cache was warm, the test passed alone (7.93 s), and runs 3 and 4 (03:04Z and 03:07Z) gave `482 passed`.
  - My files are not on that path: the test reads `scripts/install_session_hooks.py` only through `line_of("def our_hooks(")`, which still resolves.
  - This is an adjacent defect: reported, not fixed.
- **D8. HEAD moved during the round** through the coordinator's commits and a push. The PIN was 0749fe5; at the end, HEAD is the commit "Retro of the CI fix: task #356 registered ..." and origin is 975523a. No commit touched my six files: HEAD's copies still carry the premise hashes.
- **D9. My first X2 test also pinned the header position** (R3-F1's order), so on round 3's code it went red for the wrong reason. It is position-free now: it passes on round 3's code and kills X2.
- **D10. Gate C is extra.** The gate stack's real run over my six files found two more tests that name them as data: `tests/test_jev_context.py` and `tests/test_system1_context.py`.

### Premise re-run (item 1)

- I ran `bash scripts/premise_block.sh` over the brief's PREMISE commands, in the main tree, from 02:09:44Z to 02:10:42Z.
- `diff` of its output against the brief's block printed `NO DIFFERENCE`, so there was no CONTRACT-INVALID stop.
- What it showed:
  - the six lane files at the premise hashes (`a3a24981247588c7` … `dddd30002144af50`);
  - `git status` clean for the seven paths;
  - `"SessionStart"` counted 1;
  - both set ids matched;
  - the three-file pytest run gave `271 passed`.

### The items: code, test, mutant, real run

**Item 2, R3-F3 (the report window)**
- Code:
  - `scripts/handback_extract.py:69` `opens_round`: a message to the lane carries text, and is never a tool result or a compaction summary.
  - `scripts/handback_extract.py:82` `scan` streams the transcript.
  - `scripts/handback_extract.py:90` `wants_user`: a user record is parsed only between a call and the next message.
  - `scripts/handback_extract.py:116` `in_round`: a long text counts only inside a round.
  - `scripts/handback_extract.py:125` `in_round`: a call closes the round.
- Test: `tests/test_stack.py:2084` `test_handback_extract_never_takes_the_previous_rounds_epilogue`.
  - The verifier's shape, with the call's tool result: round-1 report, call 1, a 4,000-character epilogue, the resume, a short text, a 160-character call 2. It gives no report.
  - The same shape with a compaction before the resume also gives no report.
  - The control, where round 2 writes its own long text, picks that text.
  - F-11's test now also holds the tool result and the resume message.
- Mutants, each killed by `FAILED tests/test_stack.py::test_handback_extract_never_takes_the_previous_rounds_epilogue`:
  - F3a: the window opens at the previous call (round 3's rule);
  - F3b: any user record opens it;
  - F3c: a compaction summary opens it;
  - F3d: a tool result counts as a message.
- Real run on my own transcript (3 calls; round 2's 3,995-character epilogue lies between its call and round 3's resume):
  - round 3's bytes: `report: none longer than the hand-back (the last long text block: 3995 characters, the hand-back: 33227)`
  - round 4: `report: none (no assistant text block of 1000 or more characters in the last round)`
  - the hand-back is the same both times: `handback: found calls=3 chars=33227 bytes=33410 neutralized=0 sha256=620593bc072e`.

**Item 3, R3-F1 (the counts line and the print cap)**
- Code:
  - `scripts/stack.py:1290` `cmd_run` builds the header; the headline lines now come right after the tree line.
  - `scripts/stack.py:1355` `header`: params and outputs come after the headline lines.
- Test: `tests/test_stack.py:2109` `test_the_gates_counts_line_stays_in_the_print_past_a_9562_character_paths_value` (a 10,816-character paths value; line 3 of the print must be the counts line).
- Mutant F1 (params and outputs inserted before the headlines again): `FAILED tests/test_stack.py::test_the_gates_counts_line_stays_in_the_print_past_a_9562_character_paths_value`. Why: line 3 was `params: ...`.
- Real run: `gate paths=scripts/report_lint.py,<177 docs paths> graph=no`, a 9,624-character value with 178 paths. The print is 9,000 characters in 5 lines:
  ```
  stack gate · run s-20260929T031414Z-44217f · exit 0
  tree /home/user/agent-factory · HEAD 755e900cfb60
  sources · run list 24 of union 24: pytest 22 · python3 0 · bash 2 · not run 0
  ...
  … the print is cut at 9,000 characters (the headers alone are over the cap)
  ```

**Item 4, R3-F4 (one test per surviving mutant)**
- X1: the stray kill must be SIGKILL.
  - Test: `tests/test_stack.py:2132` `test_a_stray_that_ignores_sigterm_is_killed_all_the_same`. The leader waits until its child ignores SIGTERM, then exits.
  - Code: `scripts/stack.py:909` `_signal_group`, the stray kill.
  - Mutant X1 (the stray kill sends SIGTERM): `FAILED tests/test_stack.py::test_a_stray_that_ignores_sigterm_is_killed_all_the_same`. Why: `assert [11419] == []`, the child was still alive after 5 s. The test's `finally` killed it.
- X2: the headline cut.
  - Test: `tests/test_stack.py:2151` `test_a_headline_longer_than_headline_max_is_cut_with_an_ellipsis`.
  - Mutant X2 (no cut): `FAILED tests/test_stack.py::test_a_headline_longer_than_headline_max_is_cut_with_an_ellipsis`.
- X3: run-all.sh goes to bash.
  - Test: `tests/test_stack.py:2186` `test_a_gate_on_a_path_only_run_all_names_runs_run_all_with_bash`.
  - Code: `scripts/gate_union.py:87` `HARNESS`: run-all.sh goes to bash.
  - Mutant X3, applied in scratch (that line without `name == "run-all.sh"`): `FAILED tests/test_stack.py::test_a_gate_on_a_path_only_run_all_names_runs_run_all_with_bash`. Why: `exit 1 — required, not ok: sources`, NOTHING TO RUN.
- X6: a refused run runs no shell test.
  - Test: `tests/test_stack.py:2202` `test_a_refused_run_runs_no_shell_test`. Its control lifts the bound, and then the shell test runs.
  - Code: `scripts/stacks.toml:246` `needs`: the shells step waits for sources.
  - Mutant X6 (the shells step without `needs`): `FAILED tests/test_stack.py::test_a_refused_run_runs_no_shell_test`. Why: `[(1, 'ok')]`, the shell test ran.
- Real runs on the main tree:
  - X3: `gate paths=harness-ports/bin/build-roles.py graph=no` printed `sources · run list 2 of union 2: pytest 1 · python3 0 · bash 1 · not run 0`, and union_sh printed `harness-ports/tests/run-all.sh`.
  - X6: `gate paths=scripts/report_lint.py mode=run runs=1 max_files=1 graph=no` exited 1 and printed:
    - `sources · run list 4 of union 4: pytest 3 · python3 0 · bash 1 · not run 0 · REFUSED: mode=run runs at most max_files=1 files; pass max_files=4 to run these 4`
    - `## run · SKIPPED — its prerequisite step sources failed (rc 1)`
    - `## shells · SKIPPED — its prerequisite step sources failed (rc 1)`
  - X2: under item 5.

**Item 5, R3-F5 (control characters in a headline)**
- Code:
  - `scripts/stack.py:98` `CONTROL_RE`: C0, DEL, C1, U+2028 and U+2029, built with `chr()`. The Edit tool had written the two separators as literal bytes, and my byte check caught it.
  - `scripts/stack.py:1353` `CONTROL_RE`: the headline is escaped before the cut, so the header line stays bounded.
- Test: `tests/test_stack.py:2167` `test_a_headlines_control_characters_are_escaped_in_the_header`. It reads the print as bytes, because text mode turns a raw CR into a newline.
- Mutants F5a (no escape) and F5b (C0 only): `FAILED tests/test_stack.py::test_a_headlines_control_characters_are_escaped_in_the_header`, twice.
- Real run: the real runner with an ad-hoc registry holding two headline steps (`--registry` and `--log-dir` under scratch). The header lines, shown as Python repr:
  - `'ctl · COUNTS ok\\rFORGED exit 0\\x1b[2K\\x85\\u2028|'`
  - `long · HHH…`: 508 characters (500, plus the id and the `…`).
  - No raw CR, ESC, NEL or U+2028 is in the header.

**Item 6, the catalog notes**
- Code:
  - `scripts/stack.py:364` `notes`: each stack's notes are checked (1 to 300 characters each, one line, no control character).
  - `scripts/stack.py:1173` `list_lines` prints each note under its stack's line, as `  note: ...`.
  - The notes in the registry:
    - `scripts/stacks.toml:33` `notes` (harvest)
    - `scripts/stacks.toml:112` `notes` (gate)
    - `scripts/stacks.toml:255` `notes` (ctx)
    - `scripts/stacks.toml:459` `notes` (review)
- Tests:
  - `tests/test_stack.py:1057` `test_list_prints_one_line_per_wave1_stack_and_its_notes_under_it`: the NOTES table pins each note under its stack.
  - Four bad-registry cases: note-cr, notes-string, note-empty and note-301.
- Mutants:
  - N1 (notes not printed) and N3 (a note dropped from the registry): `FAILED tests/test_stack.py::test_list_prints_one_line_per_wave1_stack_and_its_notes_under_it`.
  - N2 (the notes check removed): `FAILED tests/test_stack.py::test_a_bad_registry_exits_3_before_anything_runs[note-cr]` and `[notes-string]`.
- Real run: `python3 scripts/stack.py list` exits 0. Its 16 lines are the SessionStart output under item 7, minus the heading and the ratings line.

**Item 6b, local commit ids in a hand-back**
- Code:
  - `scripts/handback_extract.py:153` `local_ids`: the mode `--local-ids FILE...`.
    - It lists each commit id that the files cite and that `git log origin/<current branch>..HEAD` shows as local, with its line and the commit's subject.
    - Exit codes: 0 none cited, 1 some cited, 2 not checked (the reason is on stdout).
  - `scripts/handback_extract.py:141` `git_out`.
  - It uses stale_ids.py's own rules, so it flags exactly what stale_ids would refuse once the push rewrites the range:
    - `scripts/stale_ids.py:23` `HEX = re.compile`: the token rule;
    - `scripts/stale_ids.py:33` `stale_in`: the prefix match.
  - `scripts/stacks.toml:92` `local_ids`: the step. It is advisory and chained like lint_handback, so it is SKIPPED when there is no hand-back.
- Tests:
  - `tests/test_stack.py:2236` `test_local_ids_lists_a_cited_local_commit_with_its_line`: in a repository with a bare origin, the planted local id is listed with its line. The control cites only an origin id and lists none.
  - `tests/test_stack.py:2257` `test_local_ids_says_why_when_it_cannot_check`: a detached HEAD, and a branch that origin does not hold, each exit 2 with the reason.
  - `tests/test_stack.py:2273` `test_harvest_lists_the_local_ids_its_handback_cites`: runs the registry's own handback and local_ids steps. The harvest exits 0 while the step reads `FAILED · rc 1`.
- Mutants:
  - L1 (the range is all of HEAD) and L2 (a full-id match only): `FAILED tests/test_stack.py::test_local_ids_lists_a_cited_local_commit_with_its_line`.
  - L3 (the step required): `FAILED tests/test_stack.py::test_harvest_lists_the_local_ids_its_handback_cites`.
  - L4 ("not checked" read as none): `FAILED tests/test_stack.py::test_local_ids_says_why_when_it_cannot_check`.
- Real runs on the main tree:
  - A file that cites the local commit, rc 1:
    - `local ids: 1 cited — origin/claude/soundbox-kit-migration-iz1jwf..HEAD holds 1 local commit; push_clean.sh rewrites them, so cite each by its subject (or by its origin id after the push)`
    - `/tmp/lsb9r4/hb/cites-now.md:1: 755e900 is local 755e900cfb60 "Retro of the CI fix: task #356 registered (a gate under CI's Python); live-state names origin 975523a" · The landing was 755e900; round 4 builds on it.`
  - My round-3 hand-back, rc 0: `local ids: none cited (origin/claude/soundbox-kit-migration-iz1jwf..HEAD holds 1 local commit)` (see NOT done 5).

**Item 7, the SessionStart wiring**
- Code:
  - `scripts/install_session_hooks.py:69` `catalog`: the group, with matcher `startup|resume|compact` and a 30-second timeout. The command is guarded like LS-B7's: it exits 0 when the repo or stack.py is absent. It ends in `|| echo "stacks: no catalog (scripts/stack.py catalog exited $?)"`, so a python3 that cannot run still leaves one line and exits 0.
  - `scripts/install_session_hooks.py:77` `task_sync`: the catalog group comes after it. LS-B7's hooks are unchanged.
  - `scripts/stack.py:1190` `catalog`: the command. It prints a heading line, `list`'s lines, and one line on ratings that names the rated (content) stacks.
  - `scripts/stack.py:94` `CATALOG_CAP`: 4,000. Past the cap, whole stacks are dropped, with a line that counts them.
  - `scripts/stack.py:1209` `CATALOG_CAP`: the last-resort cut, to 3,999 characters.
  - `scripts/stack.py:1210` `Exception`: any failure becomes ONE line, `stacks: no catalog (<why>)`.
  - `scripts/stack.py:1387` `catalog`: main dispatches it before the registry loads. It exits 0 always.
- Tests in `tests/test_session_hooks.py`:
  - `tests/test_session_hooks.py:117` `test_fresh_install_registers_the_eight_hooks` (SessionStart now holds 3).
  - `tests/test_session_hooks.py:435` `test_the_catalog_hook_is_installed_once_on_start_resume_and_compact`: the matcher, the timeout and the command are pinned; a second install changes nothing.
  - `tests/test_session_hooks.py:451` `test_the_installed_catalog_command_prints_the_catalog_under_4000_characters`: runs the installed command through `sh`.
  - `tests/test_session_hooks.py:465` `test_the_catalog_hook_fails_loud_in_one_line_and_exits_0`. Both cases exit 0:
    - a stack.py that exits 3 leaves `stacks: no catalog (scripts/stack.py catalog exited 3)`;
    - a bad registry leaves `stacks: no catalog (registry: version: must be 1 (found 2))`.
  - `tests/test_session_hooks.py:481` `test_an_older_catalog_spelling_is_replaced_on_install`.
  - LS-B7's tests keep their assertions; their "others" filter now leaves out the catalog.
- Tests in `tests/test_stack.py`:
  - `tests/test_stack.py:2304` `test_catalog_is_a_heading_the_list_and_one_line_on_ratings_under_4000_characters`
  - `tests/test_stack.py:2319` `test_catalog_drops_whole_stacks_to_stay_under_4000_characters` (60 stacks, with a count line)
  - `tests/test_stack.py:2337` `test_catalog_cuts_even_its_ratings_line_to_stay_under_4000_characters` (200 rated stacks; the output is 3,999 characters)
  - `tests/test_stack.py:2355` `test_catalog_that_cannot_be_built_prints_one_line_naming_why_and_exits_0` (a bad registry, no registry, or an argument)
  - `tests/test_stack.py:2366` `test_catalog_turns_an_unexpected_error_into_one_line`
- Mutants (each FAILED line is in the mutation block below):
  - C1: the cap raised to 40,000.
  - C2: only a KeyError caught.
  - C3: only a Refusal caught.
  - C4: the ratings line names every stack.
  - C5: no last-resort cut.
  - C6: an argument is accepted.
  - I1: no matcher.
  - I2: no echo.
  - I3: no catalog marker.
  - I4: no timeout.
  - I5: the group placed before LS-B7's.
- Real run of the installer:
  - First run: `session hooks: installed 8 in /home/user/.claude/settings.json (live from the next tool call)`.
  - Second run: `session hooks: unchanged in /home/user/.claude/settings.json`.
  - `--check`: `session hooks: present in /home/user/.claude/settings.json`.
  - A before-and-after diff of the settings: every hook kept (PostToolUse 1 of 1, PreToolUse 2 of 2, SessionStart 2 of 2, Stop 2 of 2, UserPromptSubmit 2 of 2), one command added to SessionStart, the other keys equal.
- Real run of the installed command, through `sh` from `/home/user` with a `compact` payload: rc 0, no stderr, 2,681 characters, 2,704 bytes, 19 lines:
  ```
  Stacks (scripts/stacks.toml): `python3 scripts/stack.py <label> key=value ...` runs one in one call; `python3 scripts/stack.py explain <label> ...` prints its plan and runs nothing.
  harvest  agent=<agent> [report=<path>]  — a finished lane: its served models and refusal stops, its SubagentHandback message (tags neutralized), the report linted and hashed
    note: On a resumed lane, check the `report:` line: the report window opens at the resume message, so no earlier round's text is this round's report (R3-F3).
    note: `report=` names an existing file to lint and hash; the hand-back itself is saved under the run directory as `handback.md`.
  gate  paths=<paths> [mode=plan|run] [runs=1|2] [graph=yes|no] [max_files=<int>]  — every test that names each path, united with the tests ripwire's call graph links to the change (graph=yes); mode=run runs each file with its own runner: pytest, python3 or bash
    note: `runs=2` re-runs the pytest files only; `setid` covers the pytest files only.
    note: Read the counts line; `mode=run` refuses more than `max_files` (40).
    note: Pass `graph=no` where ripwire is missing and for a deleted path (F-18).
  ctx  files=<paths> [q=<text>] [sym=<symbols>]  — the code-intel pack of files: graft skeletons and ask, GitNexus impact, code-review-graph, ripwire, the AP screen · rated
    note: `ctx` does not show a missing ripwire as unmapped (F-6).
  impact  sym=<symbol>  — the blast radius of one symbol from four instruments in parallel: GitNexus impact, code-review-graph callers and tests, ripwire edit-check · rated
  find  q=<text>  — what the repo already holds on q: graft ask, the owner's rulings, the chat, the AF-AP registry rows · rated
  premise  files=<paths>  — the premise facts of files: tracked or not, sha256, line count, the last commit that touched each
  echo  pattern=<text> [roots=<paths>]  — the bug-echo sweep: the pattern in the six code roots, the incident log's lines, the AP screen over the files hit · rated
  review  [files=<paths>] [mode=check|save|compare]  — a change's review: sentrux architecture health (check, save a baseline, compare with it), and for the files ripwire's test gate, the pyflakes delta and the AP screen · rated
    note: `review mode=save` overwrites the shared sentrux baseline (F-5).
    note: `review`'s sentrux section is advisory; `tool exit N` is the only sign of a failed run.
  ci  [branch=<text>]  — the branch's stage0-ci verdict through scripts/ci_gate.py: 0 passed, 75 not in yet, 1 red
  Ratings, the content stacks only (ctx, impact, find, echo, review): `--rate <run id>=<rel>/<use>` on the next stack call, or `python3 scripts/stack.py rate <run id>=<rel>/<use>`; rel and use are 0 to 3.
  ```

### The CLAUDE.md pointer line I propose (item 7), word for word

Where: in the section `## Environment & Tools (summary)`, after the line that begins "Load `env-tool-quirks` before a background job". It is one line inside an existing section, so the mirror files need no new section.

`**Stacks (D-103):** run a named sequence of instrument calls in one tool call with `python3 scripts/stack.py <label> key=value ...` (the registry is `scripts/stacks.toml`; `explain <label> ...` prints the plan and runs nothing); the SessionStart hook prints the catalog with each stack's notes, and a content stack's run takes a rating with `--rate <run id>=<rel>/<use>`.`

### Gates (item 8)

Pasted from `bash scripts/test_summary.sh`, with `--basetemp` passed as a pytest argument under a private scratch dir, in the main tree (a git work tree).

- **A:** `3 files set=cebb397be3f6` (tests/test_stack.py tests/test_session_hooks.py tests/test_task_sync.py)
  - run 1, 02:52:53Z: `pytest-summary: 296 passed in 60.95s (0:01:00)`
  - run 2, 02:53:55Z: `pytest-summary: 296 passed in 62.45s (0:01:02)`
- **B,** the round-1 set: `5 files set=2804489b9d6b` (tests/test_stack.py tests/test_no_laya_in_gates.py tests/test_s0_01_spec_runner.py tests/test_s0_11_eval_hardening.py tests/test_search_intercept.py)
  - run 1, 02:55:05Z: `pytest-summary: 1 failed, 481 passed in 165.45s (0:02:45)` (D7)
  - run 2, 02:57:50Z: `pytest-summary: 1 failed, 481 passed in 167.80s (0:02:47)` (D7)
  - run 3, 03:04:50Z: `pytest-summary: 482 passed in 144.89s (0:02:24)`
  - run 4, 03:07:15Z: `pytest-summary: 482 passed in 146.81s (0:02:26)`
- **C,** added: `2 files set=a9d6e3f9b705` (tests/test_jev_context.py tests/test_system1_context.py)
  - run 1, 03:09:49Z: `pytest-summary: 190 passed in 59.28s`
  - run 2, 03:10:49Z: `pytest-summary: 190 passed in 59.43s`
- **The CI rehearsal:** a direct pytest run (not test_summary.sh) over `2 files set=341b63444f8c` (tests/test_stack.py tests/test_session_hooks.py).
  - Environment:
    - uid 1000, Python 3.12.3;
    - installed: pyflakes, pytest, jsonschema 4.25.1, rfc3339-validator 0.1.4 and PyYAML, as `.github/workflows/stage0-ci.yml:40` `pyflakes` installs them;
    - a PATH without rg, python, graft, ripwire, sentrux or node;
    - the tree: a `git clone --shared --no-tags` in scratch, owned by uid 1000, with my six files on top.
  - Result at 03:17:58Z: `228 passed, 2 skipped in 53.44s`. The skips are the ripwire and rg skips, as in round 3.
  - A first attempt, before pyflakes was in my venv, gave `2 failed, 226 passed, 2 skipped`. Both failures were lint_files: a gap in my rehearsal venv, since CI installs pyflakes.
  - pyflakes over the two test files, as CI runs it on `tests/`: rc 0.
- **Red first:** the final tests on round 3's code gave `28 failed, 202 passed in 55.54s`.
  - The tree: a scratch repo of HEAD's bytes (its six files at the premise hashes) with the new tests on top.
  - The 28 red tests are the round-4 feature tests:
    - the notes cases and the NOTES table;
    - the two harvest explain pins and the harvest step list;
    - R3-F3, R3-F1 and R3-F5;
    - the three local-ids tests;
    - the six catalog tests;
    - seven session-hook tests.

### Mutation

The rules (AF-AP-223): each mutant is one exact anchor that matches once; the control runs first; a mutant counts as KILLED only on a FAILED line; each file is restored and re-hashed after each mutant; the main tree's hashes are checked at the end.

The driver ran in scratch on a copy of the final bytes:
- `CONTROL rc=0 24 passed in 8.20s`
- `TOTAL=29 KILLED=29 SURVIVED=0 INVALID=0`
- `main-tree hashes unchanged: stack.py c69a819138d2, stacks.toml 6393305a0bf1, handback_extract.py 6607d18007d3, test_stack.py 3036e5784df2, install_session_hooks.py 0cc115498df9, test_session_hooks.py e7c008cc4491, gate_union.py 40b64972b404`

The FAILED lines, in the order F3a, F3b, F3c, F3d, F1, X1, X2, X3, X6, F5a, F5b, N1, N2 (two lines), N3, L1, L2, L3, L4, C1, C2 (two lines), C3, C4, C5, C6, I1, I2, I3, I4, I5 (two lines):
```
tests/test_stack.py::test_handback_extract_never_takes_the_previous_rounds_epilogue
tests/test_stack.py::test_handback_extract_never_takes_the_previous_rounds_epilogue
tests/test_stack.py::test_handback_extract_never_takes_the_previous_rounds_epilogue
tests/test_stack.py::test_handback_extract_never_takes_the_previous_rounds_epilogue
tests/test_stack.py::test_the_gates_counts_line_stays_in_the_print_past_a_9562_character_paths_value
tests/test_stack.py::test_a_stray_that_ignores_sigterm_is_killed_all_the_same
tests/test_stack.py::test_a_headline_longer_than_headline_max_is_cut_with_an_ellipsis
tests/test_stack.py::test_a_gate_on_a_path_only_run_all_names_runs_run_all_with_bash
tests/test_stack.py::test_a_refused_run_runs_no_shell_test
tests/test_stack.py::test_a_headlines_control_characters_are_escaped_in_the_header
tests/test_stack.py::test_a_headlines_control_characters_are_escaped_in_the_header
tests/test_stack.py::test_list_prints_one_line_per_wave1_stack_and_its_notes_under_it
tests/test_stack.py::test_a_bad_registry_exits_3_before_anything_runs[note-cr]
tests/test_stack.py::test_a_bad_registry_exits_3_before_anything_runs[notes-string]
tests/test_stack.py::test_list_prints_one_line_per_wave1_stack_and_its_notes_under_it
tests/test_stack.py::test_local_ids_lists_a_cited_local_commit_with_its_line
tests/test_stack.py::test_local_ids_lists_a_cited_local_commit_with_its_line
tests/test_stack.py::test_harvest_lists_the_local_ids_its_handback_cites
tests/test_stack.py::test_local_ids_says_why_when_it_cannot_check
tests/test_stack.py::test_catalog_drops_whole_stacks_to_stay_under_4000_characters
tests/test_stack.py::test_catalog_that_cannot_be_built_prints_one_line_naming_why_and_exits_0[bad-registry]
tests/test_stack.py::test_catalog_that_cannot_be_built_prints_one_line_naming_why_and_exits_0[no-registry]
tests/test_stack.py::test_catalog_turns_an_unexpected_error_into_one_line
tests/test_stack.py::test_catalog_is_a_heading_the_list_and_one_line_on_ratings_under_4000_characters
tests/test_stack.py::test_catalog_cuts_even_its_ratings_line_to_stay_under_4000_characters
tests/test_stack.py::test_catalog_that_cannot_be_built_prints_one_line_naming_why_and_exits_0[an-argument]
tests/test_session_hooks.py::test_the_catalog_hook_is_installed_once_on_start_resume_and_compact
tests/test_session_hooks.py::test_the_catalog_hook_fails_loud_in_one_line_and_exits_0
tests/test_session_hooks.py::test_an_older_catalog_spelling_is_replaced_on_install
tests/test_session_hooks.py::test_the_catalog_hook_is_installed_once_on_start_resume_and_compact
tests/test_session_hooks.py::test_fresh_install_registers_the_eight_hooks
tests/test_session_hooks.py::test_the_catalog_hook_is_installed_once_on_start_resume_and_compact
```

I read each kill's reason from its one-line traceback, and each is the intended one. Some examples:
- F1: line 3 is `params:`.
- X1: `assert [11419] == []`.
- X6: `[(1, 'ok')]`.
- C1: `assert 15118 < 4000`.
- C5: `assert (5657 == 3999)`.
- I3: `assert (2 == 1)`.

### Self-attack: the three likeliest ways this is wrong

1. **The report window opens at the wrong record, in a shape I did not measure.**
   - Too early: a harness message before the resume would open it, and the old epilogue would come back.
   - Too late: a refused call and a retry with no user text between them would leave that round's text out.
   - Ruled out for the shapes that occur: in all 23 transcripts with two or more calls, the first record after each call is the resume, an enforce message or a compaction summary.
   - Bounded otherwise: "too late" only drops a report candidate. The hand-back itself is still saved and linted.
2. **The catalog hook harms the sessions it runs in.** It fires at every start, resume and compaction of every session rooted at /home/user.
   - Exit 0 on every path, tested: stack.py exits 3; a bad registry; no registry; an argument; an unexpected error; a missing repo or stack.py (`test_every_installed_command_fails_open_when_the_repo_is_absent` now covers 10 commands).
   - Its output stays under 4,000 characters by construction, tested with 60 stacks and with 200 rated stacks.
   - It has a 30-second timeout, and it runs nothing but a registry read.
   - Still open: no kill switch (NOT done 3), and the live firing was not observed (NOT done 4).
3. **The local-ids step misleads.**
   - A false "none cited" after a push is documented (NOT done 5).
   - "Not checked" (a detached HEAD, or no origin branch) reads as FAILED (not required), so the harvest still exits 0. The reason is on its line (tested: exit 2).
   - A false positive needs a hex token of 7 or more characters that is a prefix of a local commit id: the same rule stale_ids.py applies.
   - I also checked the header reorder: no script parses the stack print's header by position (`git grep` over scripts, harness-ports, .claude/hooks and src found none). runs.jsonl is the machine record.

### Evidence tiers

- **VERIFIED** (run here):
  - the premise;
  - red first, on round 3's bytes;
  - 29 of 29 mutants killed, each reason read;
  - gates A, B and C twice each;
  - the diagnosis of B's two red runs, measured: the cold rg ran past 60 s, the warm one took 0.67 s, the hook took 10.1 s by hand, and the test was green once the cache was warm;
  - the CI rehearsal;
  - the real runs above;
  - the installer's idempotency and the settings diff;
  - no commit touched my files during the round;
  - the citations (report_lint, MISS 0).
- **INFERRED:** why the page cache was cold for gate B's runs 1 and 2 (other lanes' I/O and git's growing loose objects evicting it). Not traced.
- **ASSUMED:**
  - the live issue #80 equals the local body file (D4);
  - the harness matches `startup|resume|compact` against its SessionStart source (NOT done 4).

### For the registry (the coordinator's file; bug-echo done)

- **R3-F3's class:** a round boundary taken from a user record without leaving out the call's own tool result and the compaction summary.
  - The bug-echo used the `echo` stack with the pattern `get\("type"\) (==|!=) "user"|isCompactSummary|"tool_result" (in|not in)` over the six code roots. It found no sibling:
    - `scripts/decide-harvest:958` `record`: reads tool results on purpose.
    - `scripts/s1_scores.py:133` `r.get("type") == "user"`: reads tool results on purpose.
    - `scripts/s1_synth.py:240` `isCompactSummary`: already left out.
    - `scripts/chat_tail.py:99` `e.get("type") != "user"`: prints chat and sets no boundary.
- **The adjacent defect (D7):** `.claude/hooks/search-intercept.py` answers a Bash `grep -r` by walking `.git` with rg `--hidden` under a 10-second budget. With a cold cache it fails open with no answer, and its own test goes red.
  - A possible fix: the six VCS globs the Grep scope already has (`.claude/hooks/search-intercept.py:890` `_GREP_TOOL_SCOPE`), or `--glob '!.git'`.
- **Met on contact,** both already in env-tool-quirks:
  - the Edit tool wrote U+2028 and U+2029 as literal bytes;
  - a TOML basic string turned `\n` into a newline in an ad-hoc registry.

### Files (sha256 prefix and line count; all uncommitted in the main tree)

- `c69a819138d21471`  1434  scripts/stack.py
- `6393305a0bf1a585`   529  scripts/stacks.toml
- `6607d18007d36121`   240  scripts/handback_extract.py
- `3036e5784df20d2f`  2374  tests/test_stack.py
- `0cc115498df91147`   182  scripts/install_session_hooks.py
- `e7c008cc44919c31`   490  tests/test_session_hooks.py
- Outside the repo: `/home/user/.claude/settings.json` `ab456303e3b74530`, written by the installer.

### Records and cleanup

- My real runs logged under my scratch dir, never the main tree's `.jev/`.
- Removed at 03:26Z:
  - the scratch dir (the scratch repos, the CI clone, the venv, the logs, the mutation driver);
  - the premise's basetemp `/tmp/lsb9r4-premise-bt`;
  - my ripwire cache `/tmp/ripwire-0/8a`. I proved it mine: a ripwire run in my scratch tree touched it and nothing else.
- Kept: `/tmp/ripwire-0/3a` (02:59). It is not mine.
- No `/tmp/stack-*` directory remains, and no process of mine is left.
- A slow `grep -r` I started over the session scratchpad went to the background after 120 s; I killed it by its pid (2546).
- Disk: 11,021 MB free.
