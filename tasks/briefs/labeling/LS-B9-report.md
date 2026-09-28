> **COORDINATOR NOTE (2026-09-28 17:5xZ):** the harness refused the lane's report-file write, so this report of record is its hand-back message, extracted by the lane's own `harvest` stack (`python3 scripts/stack.py harvest agent=<the lane>`, run `s-20260928T175722Z-f9ff7f`) and checked byte for byte against a manual extraction (40,600 bytes, sha256 prefix 43e02e6aa903 both ways; no control tag to neutralize). The same run read the lane's served model per assistant record (`claude-opus-5-5 381`, 0 refusal stops, 3 tool errors) and linted this text: `report_lint: 72 refs — OK 64, NEAR 0, MISS 7, UNCHECKABLE 1` (the seven MISS lines cite the right lines in words the linter does not match, for example a paraphrase of an import); not yet re-read by a verifier.

# LS-B9 report: the stack runner and the first eight stacks (task #339, D-103)

Written 2026-09-28 17:5xZ by the sandbox `code-implementer` lane (Opus 5.5). This is the whole report as a message: the harness refused the report-file write ("Subagents should return findings as text"), so `tasks/briefs/labeling/LS-B9-report.md` was NOT written, as the brief allows.

## Outcome

**DONE, not landed.** All eight wave-1 stacks ran for real on this tree; `impact` exits 1 on a symbol GitNexus has not indexed yet (D22). I made no git write; the five files are untracked in the main tree, for you to land:
- `/home/user/agent-factory/scripts/stack.py` (the runner)
- `/home/user/agent-factory/scripts/stacks.toml` (the registry, eight stacks)
- `/home/user/agent-factory/scripts/gate_files.py` (helper)
- `/home/user/agent-factory/scripts/handback_extract.py` (helper)
- `/home/user/agent-factory/tests/test_stack.py`

Evidence:
- **Gate:** passed twice over `5 files set=2804489b9d6b`: `pytest-summary: 391 passed in 128.61s (0:02:08)`, then `pytest-summary: 391 passed in 145.29s (0:02:25)`.
- **Mutation:** `EXPECTED=52 KILLED=52 SURVIVED=0 INVALID=0`. The control run was green first, and every kill is a pasted FAILED line.
- **Real defect found and fixed:** a step's worker thread could die silently. The step then dropped out of the record and out of the exit code, so a run could exit 0 with a required step missing (D14).
- **Design hazard reported, not fixed:** the gate stack's basetemp lies inside the main tree's work tree (D12).

## NOT done (first-class)

- **Not landed:** no commit, no push.
- **Report file not written; report_lint not run:** the harness refused the write, and the lint needs a file. Every `file:line` below was taken from `grep -n` or `sed -n` on the final files this session. One number I first wrote from memory was wrong and is corrected: the import is at `scripts/hiccup_scan.py:49`, not 47.
- **SIGKILL of the runner orphans its live steps:** each step runs in its own session (`start_new_session=True`, per the brief). SIGINT, SIGTERM and SIGHUP are handled: the live groups are killed, and the runner exits 128+N with no record.
- **Not killed:** a step that calls setsid, and a child left behind after its leader exits normally.
- **Saved output is not capped in size;** only the print is. A runaway step can fill the disk.
- **A hardlink** inside the tree to a denied file passes the deny list. realpath cannot see a hardlink, and its name is not denied.
- **Ratings are accepted for any recorded run.** Design §5 limits them to the content stacks (find, ctx, impact, echo). The brief's contract has no such refusal, and enforcing it needs a registry field the schema lacks.
- **Not run as a non-root user** (CI's identity). The out-of-tree deny entries rely on realpath's non-strict mode swallowing EACCES. I read that from CPython's posixpath source; inferred, not run.
- **The repo's other tests were not run under the gate stack's in-tree basetemp** (D12).
- **Outside my boundary, not written:**
  - the env-tool-quirks line for the tag-prefix quirk (D18);
  - a fix of `scripts/ripwire_review.sh` (D17);
  - wave 2, T2, the CLAUDE.md pointer and discovery wiring.

## Premise re-run (`bash scripts/premise_block.sh` over the brief's block)

At the start of the lane (16:37Z) every line matched the brief except `df`: 1585 MB free, against the brief's 1625.

The re-run below is from the end of the lane. It differs only where the lane or the day moved:
- HEAD is c4b87d1. The commits since c9889ee touch briefs, the ledger, the wiki and the incident log; none of my inputs.
- My five files now exist.
- Less disk is free.

No contradiction.

```
Mon Sep 28 17:47:31 UTC 2026
$ python3 -c 'import sys, tomllib; print(sys.version.split()[0], "tomllib ok")'
3.11.15 tomllib ok
$ grep -n -E 'python-version|python -m pytest tests/' .github/workflows/stage0-ci.yml
34:          python-version: '3.12'
46:        run: python -m pytest tests/ -q -rs   # -rs: every skip prints its reason (FU-4, VERIFY-I59-A)
60:          python-version: '3.12'
82:          python-version: '3.12'
101:          python-version: '3.12'
$ command -v graft sentrux ripwire rg node
/opt/node22/bin/graft
/root/.local/bin/sentrux
/root/.local/bin/ripwire
/usr/bin/rg
/opt/node22/bin/node
$ ls -la /root/venv-crg/bin/code-review-graph .gitnexus/run.cjs
-rw-r--r-- 1 root root 19564 Sep 26 09:39 .gitnexus/run.cjs
-rwxr-xr-x 1 root root   230 Sep  2 21:37 /root/venv-crg/bin/code-review-graph
$ sed -n '2,6p' scripts/test_summary.sh
# test_summary.sh — run pytest and print a mechanical summary line.
# Usage: scripts/test_summary.sh [pytest paths...]  (default: tests/)
# Prints:
#   pytest-exit: <exit code>
#   pytest-summary: <last non-empty output line>
$ grep -n 'set-id)' scripts/pc_suite.sh
121:set-id)
$ python3 scripts/hiccup_scan.py --help | head -3
usage: hiccup_scan.py [-h]
                      [--project-dir PROJECT_DIR | --transcript TRANSCRIPT]
                      [--limit-bytes LIMIT_BYTES] [--out OUT] [--jev]
$ python3 scripts/report_lint.py --help | head -3
usage: report_lint.py [-h] [--map MAP] [--rev REV] [--tolerance TOLERANCE]
                      [--root ROOT] [--min-refs MIN_REFS]
                      report
$ python3 scripts/owner_rulings.py --help | head -2
usage: owner_rulings.py [-h] [--log LOG] [--all] [--width WIDTH]
                        words [words ...]
$ python3 scripts/chat_find.py --help | head -2
usage: chat_find.py [-h] [--match {words,error}] [--order {lexical,jev}]
                    [--hits HITS] [--since SINCE] [--until UNTIL]
$ python3 scripts/ci_gate.py --help | head -2
usage: ci_gate.py [-h] --branch BRANCH [--origin-ref ORIGIN_REF] [--root ROOT]
                  [--runs-json RUNS_JSON] [--wait SECONDS]
$ python3 scripts/ap_screen.py --help | head -3
usage: ap_screen.py [-h] [--tests] [--s0-01] [--staged-shell] [--limit LIMIT]
                    [paths ...]

$ grep -n -E '^# *(usage|Usage)|^#   -' scripts/lane_context.sh | head -8
5:#   - graft skeleton of every changed file (symbols + line ranges, ~5% of the tokens of the file)
6:#   - graft ask for the question the brief poses (structural answer: callers / seams / resolution)
7:#   - per symbol: GitNexus impact (blast radius + risk), code-review-graph callers_of + tests_for,
9:#   - ripwire test-gate over the files (the tests to run + the UNTESTED blast radius)
10:#   - the anti-pattern registry screen over the WHOLE files (production → AP_SCREEN, tests → TEST_SCREEN)
$ grep -n -E 'edit-check\)|test-gate\)|callers\)' scripts/ripwire_review.sh | head -4
48:  callers)
60:  test-gate)
67:  edit-check)
$ ls scripts/stack.py scripts/stacks.toml scripts/gate_files.py scripts/handback_extract.py tests/test_stack.py
scripts/gate_files.py
scripts/handback_extract.py
scripts/stack.py
scripts/stacks.toml
tests/test_stack.py
$ git check-ignore -v .jev/stacks/runs.jsonl
.gitignore:68:.jev/	.jev/stacks/runs.jsonl
$ git rev-parse --git-common-dir
.git
$ git -C /home/user/i59-landing rev-parse --git-common-dir
/home/user/agent-factory/.git
$ grep -c '' scripts/gate_files.txt
54
$ df -m / | tail -1
/dev/vda          258020 36602      1337  97% /
```

## Files (CREATE only; nothing else modified)

Identity, from the `premise` stack's own run on the five files (run `s-20260928T174950Z-d2d758`):

```
e7461df4401526c94dd0a898df20ab7faecb993c39a4257a598671c9a29df072  scripts/stack.py
9204d83d79cbd7ead31b6f50508b5101150ea230e6a54f628359c9534d5f910b  scripts/stacks.toml
b732d35f2c6490454af25a3f51e6aa7f1f58a0e4d9435f53cfc9ed9db6a36af6  scripts/gate_files.py
4033ae62a3d2954521c3b86aa8c1d9e2dcb82b45a1837e57d5ab2bbe74c67467  scripts/handback_extract.py
7e8f14708946abd5612133cea1872429be8f6bb0ac91747ed856c80ee77ac125  tests/test_stack.py
  1166 scripts/stack.py
   346 scripts/stacks.toml
   130 scripts/gate_files.py
    97 scripts/handback_extract.py
   988 tests/test_stack.py
  2727 total
```

`git status` footprint: exactly these five `??` files. The real runs wrote only `.jev/stacks/` (872K: `runs.jsonl` and 22 run dirs; gitignored by `.gitignore:68`). The scratch dir `ls-b9/` is deleted.

## Interface table (each form verified before its step was written)

**harvest**
- **models:** `python3 scripts/hiccup_scan.py --transcript T --out F`.
  - `--help` lists `--transcript` and `--out`. A run on the 2.0 MB transcript printed one stats line, rc 0.
  - It imports `transcript_export.scrub` (`scripts/hiccup_scan.py:49`), the file SCRUB2-R1 edits. My code does not import it.
- **handback:** `python3 scripts/handback_extract.py --transcript T --out F` (new; tests below).
- **agent_row:** `grep -F "| AGENT |" F`, ok_rc 0,1. The agents table puts the id first (`refusal stops` header at `scripts/hiccup_scan.py:476`; each row starts with `_plain(aid)`).
- **lint / lint_handback:** `python3 scripts/report_lint.py --root TREE REPORT`. `--help` lists `--root` and positional `report`. rc 1 on a MISS; a missing file raises `FileNotFoundError`, rc 1.
- **sha:** `sha256sum -- REPORT`.

**gate**
- **tests / why:** `python3 scripts/gate_files.py [--why] PATH...` (new).
- **setid:** `bash scripts/pc_suite.sh set-id -- FILES` (`set_id()` at `scripts/pc_suite.sh:46`).
  - With `env -i PATH=/usr/bin:/bin HOME=/nonexistent` it printed `1 files set=e3695f80792b`, rc 0.
  - It needs no bridge env: only `scripts/pc.sh` sources `.pc-bridge.env`, and the set-id arm never calls `bridge()`.
- **run:** `bash scripts/test_summary.sh --basetemp=RUN/bt FILES`. The script hands every argument to pytest (`paths=` at `scripts/test_summary.sh:20`). Real run below.
- **clean:** `rm -rf -- RUN/bt`.

**ctx**
- **pack:** `bash scripts/lane_context.sh [-q Q] [-s SYM]... FILES`. The option loop takes `-q`, `-s` and `-o`. With `-o` the script writes the pack to that file and prints only `pack written to` (`scripts/lane_context.sh:98`), hence D2.

**impact**
- **gitnexus:** `node .gitnexus/run.cjs impact SYM --direction upstream --repo .`
  - On `build_page`: JSON with `impactedCount`, rc 0; stdin from /dev/null works.
  - `.gitnexus/` is excluded only via `.git/info/exclude`, so CI has no `run.cjs`. There the step reads `unmapped — .gitnexus/run.cjs unavailable`.
- **crg_callers / crg_tests:** `code-review-graph query callers_of SYM` / `tests_for SYM`. `query --help`. With no graph it exits 1 at once ("No graph found") and leaves an empty `.code-review-graph/` (D16).
- **ripwire:** `bash scripts/ripwire_review.sh edit-check SYM`.
  - About 32 s cold, about 1 s warm.
  - It prints one line of about 7,000 characters, with the `edit-check` element last. Hence the head-and-tail cap.
  - With its binary missing it exits 0 (D17).

**find**
- **graft:** `graft ask Q`. `graft ask --help` shows `<query> [dir]`. It refreshes its index first and writes under `graft/`, which is gitignored (D16).
- **rulings:** `python3 scripts/owner_rulings.py WORD...`, ok_rc 0,1. Any word, case-insensitive substring; 0 with matches, 1 with none.
- **chat:** `python3 scripts/chat_find.py Q --hits 5 --order lexical --no-jev-log`. About 31 s over every transcript. `default="lexical"` at `scripts/chat_find.py:469`; the Jev log is written only under `--order jev` (D4).
- **registry:** `git grep -n -i -e '^| AF-AP-' --and ( -e W ... ) -- docs/INCIDENT-LOG.md`, ok_rc 0,1. By hand: rows with rc 0, rc 1 on none. The parentheses are their own argv elements.

**premise**
- **tracked, sha, lines:** `git ls-files --error-unmatch -- F...`, `sha256sum -- F...`, `wc -l -- F...`, ok_rc 0,1. rc 1 here is a measured fact (untracked or absent), shown in the section.
- **last:** `git log -1 '--format=%h %ci %s' -- F`, foreach. The format is one argv element.

**echo**
- **code / files:** `rg -n --no-heading --sort path -e P -- ROOTS...` / `rg -l --sort path -e P -- ROOTS...`, ok_rc 0,1.
  - rg 14.1.0 exits 0 on a hit, 1 on none, 2 on a missing root.
  - The six default roots exist and are tracked. `--sort path` is D3.
- **registry:** `git grep -n -i -E -e P -- docs/INCIDENT-LOG.md`, ok_rc 0,1.
- **ap:** `python3 scripts/ap_screen.py FILE...`. Advisory: every path exits 0.

**ci**
- **verdict:** `python3 scripts/ci_gate.py --branch B`, ok_rc 0,75. `--help` and the docstring: 0 allow, 1 red, 2 cannot decide, 75 wait. It makes an unauthenticated GET, with no token and no env file.

## Where the runner's rules sit (`scripts/stack.py`)

| Rule | Location |
|---|---|
| Deny list | `deny_rule` (`scripts/stack.py:360`) |
| Path checks | `check_path` (`scripts/stack.py:379`) |
| Process-group kill | `kill_groups` (`scripts/stack.py:849`) |
| Each step in its own session | `start_new_session` (`scripts/stack.py:745`) |
| Unmapped rule | `resolve_program` (`scripts/stack.py:656`); interpreters matched by `INTERPRETER_RE` (`scripts/stack.py:68`) |
| Chained input | `chain_input` (`scripts/stack.py:678`) |
| Per-step run and thread guard | `run_step` (`scripts/stack.py:696`) |
| Print cap | `assemble` (`scripts/stack.py:893`) and `cap_lines` (`scripts/stack.py:872`) |
| One-write flock append | `append_line` (`scripts/stack.py:947`) |
| Main tree from the common dir | `_main` (`scripts/stack.py:483`) |

1,166 lines, 68 definitions. About a quarter is registry validation, each refusal named (exit 3).

## Tests (`tests/test_stack.py`)

The runner's rules run on temporary registries of tiny real programs: `sys.executable` on small scripts in a temporary git tree. Each test's docstring names its killing mutant.

**The brief's cases**
- **No shell:** `test_no_shell_a_text_value_reaches_the_program_as_one_literal_element` (`tests/test_stack.py:124`).
- **Option injection, exit 2:** `test_a_value_that_begins_with_a_dash_is_refused_before_any_step` (`tests/test_stack.py:139`).
- **Deny list:** each entry by name and via symlink, as `path` and as `paths`; exit 2, no marker, no log. `test_the_deny_list_refuses_each_entry_before_any_step_runs` (`tests/test_stack.py:166`).
- **Outside the tree** (`..`, absolute, symlinked file, symlinked dir): `test_a_path_outside_the_tree_is_refused` (`tests/test_stack.py:187`). Positive control: `test_a_path_value_inside_the_tree_reaches_the_program_tree_relative` (`tests/test_stack.py:202`).
- **Process-group kill:** one grandchild ignores SIGTERM, one records it; all three pids dead; SIGKILL 3 s later. `test_a_step_past_its_timeout_loses_its_whole_process_group` (`tests/test_stack.py:246`).
- **Unmapped,** four forms (program, `[tools]` entry, interpreter script, relative path); exit 1 only when required. `test_a_missing_instrument_prints_unmapped_and_fails_the_run_only_when_required` (`tests/test_stack.py:276`).
- **Chained step SKIPPED** (source failed, silent, unmapped, a line outside the tree, a line with a NUL): `test_a_chained_step_is_skipped_when_its_source_failed_or_printed_nothing` (`tests/test_stack.py:299`). Positive control: `test_a_chained_step_receives_its_sources_non_empty_lines_as_paths` (`tests/test_stack.py:313`).
- **Parallel groups under 1.8 s, groups in order:** `test_one_groups_steps_run_in_parallel_and_the_groups_in_order` (`tests/test_stack.py:329`).
- **when / repeat / foreach:**
  - `test_when_selects_a_step_by_its_parameters` (`tests/test_stack.py:347`)
  - `test_repeat_runs_a_step_n_times_with_numbered_sections` (`tests/test_stack.py:368`)
  - `test_foreach_runs_a_step_once_per_element_with_each` (`tests/test_stack.py:387`)
- **9,000-character cap:** `test_the_whole_print_is_capped_at_9000_characters_cut_from_the_largest_section` (`tests/test_stack.py:404`). Head plus tail per section: `test_a_section_over_cap_lines_keeps_its_first_and_last_lines` (`tests/test_stack.py:422`).
- **Worktree logs to the main tree:** `test_a_run_from_a_worktree_logs_to_the_main_tree` (`tests/test_stack.py:646`). Tree must be a toplevel: `test_the_tree_must_be_a_git_toplevel` (`tests/test_stack.py:214`).
- **Records, ratings and refusals:**
  - Record fields: `test_the_run_record_holds_every_field_and_each_output_is_saved_whole` (`tests/test_stack.py:437`).
  - `--rate` and `rate`: `test_ratings_ride_on_a_run_and_on_rate_and_must_name_a_recorded_run` (`tests/test_stack.py:459`).
  - Exit 2 for an unknown, missing, repeated, `=`-less or derived key: `test_a_bad_key_is_refused_with_exit_2_naming_the_known_keys` (`tests/test_stack.py:489`).
  - Exit 3 for a bad version, `outward = true` and ten authoring errors: `test_a_bad_registry_exits_3_before_anything_runs` (`tests/test_stack.py:525`).

**Beyond the brief's list**
- Explain runs nothing: `test_explain_runs_nothing_and_writes_no_record` (`tests/test_stack.py:537`).
- Thread defect fails the step loudly: `test_a_defect_inside_a_step_thread_fails_the_step_loudly` (`tests/test_stack.py:550`).
- A signal to the runner kills its live steps: `test_a_signal_to_the_runner_kills_its_live_steps_and_writes_no_record` (`tests/test_stack.py:578`).
- Every type's shape: `test_every_type_refuses_a_value_outside_its_shape_before_any_step` (`tests/test_stack.py:610`).
- Exactly one transcript: `test_the_transcript_of_an_agent_must_match_exactly_once` (`tests/test_stack.py:627`).

**Wave-1 registry**
- `test_list_prints_one_line_per_wave1_stack` (`tests/test_stack.py:669`).
- Explain pinned for each stack, nine cases: `test_explain_of_each_wave1_stack_is_pinned` (`tests/test_stack.py:787`). Each argv was checked against the interface table first, so the pin is change detection, not an oracle.
- `premise` on this tree against hashlib and byte counts: `test_premise_runs_on_this_tree` (`tests/test_stack.py:804`).
- `gate` plan mode on this tree: each listed test is read for the path, and the set id is compared with pc_suite.sh's own. `test_gate_plan_runs_on_this_tree` (`tests/test_stack.py:820`).
- `harvest` over a built transcript with thinking, attachment and user-record decoys: `test_harvest_on_a_built_subagent_transcript` (`tests/test_stack.py:879`).
- Extractor: `test_handback_extract_writes_the_last_calls_message_with_its_tags_neutralized` (`tests/test_stack.py:898`) and `test_handback_extract_absent_exits_1_and_writes_nothing` (`tests/test_stack.py:915`).
- gate_files on a synthetic root: `test_gate_files_lists_every_test_that_names_a_path` (`tests/test_stack.py:948`) and `test_gate_files_why_names_code_and_comment_mentions_and_self` (`tests/test_stack.py:959`).
- `echo` twice on this tree, same saved search: `test_echo_runs_on_this_tree_and_its_output_is_reproducible` (`tests/test_stack.py:975`). Skips without rg.

### Mutation (AF-AP-223): the scratch driver's output, verbatim

How the driver works:
- It copies the five files to scratch and runs the unmutated CONTROL first, which must collect and pass.
- Each mutant is one exact text replacement; an anchor that does not match exactly once is INVALID.
- It py_compiles the mutant and runs its named test with `PYTHONDONTWRITEBYTECODE=1`.
- KILLED counts only on a `FAILED tests/test_stack.py::<name>` line. EXPECTED is a literal, and the production sha256 is compared before and after.

The first full pass left M5a SURVIVED (SIGTERM to the leader only). The single grandchild ignored SIGTERM, so a group TERM and a leader TERM looked the same. The test gained a grandchild that records SIGTERM. Final pass:

```
CONTROL rc=0 49 passed, 58 deselected in 15.71s
KILLED   M1-shell                       FAILED tests/test_stack.py::test_no_shell_a_text_value_reaches_the_program_as_one_literal_element
KILLED   M2-text-dash                   FAILED tests/test_stack.py::test_a_value_that_begins_with_a_dash_is_refused_before_any_step[q=-rf]
KILLED   M2b-path-dash                  FAILED tests/test_stack.py::test_a_value_that_begins_with_a_dash_is_refused_before_any_step[p=-x]
KILLED   M3a-deny-env                   FAILED tests/test_stack.py::test_the_deny_list_refuses_each_entry_before_any_step_runs[dot-env-path]
KILLED   M3b-deny-git                   FAILED tests/test_stack.py::test_the_deny_list_refuses_each_entry_before_any_step_runs[git-dir-path]
KILLED   M3c-deny-dirs                  FAILED tests/test_stack.py::test_the_deny_list_refuses_each_entry_before_any_step_runs[codiv-path]
KILLED   M3d-deny-qwen                  FAILED tests/test_stack.py::test_the_deny_list_refuses_each_entry_before_any_step_runs[qwen-config-path]
KILLED   M3e-deny-lexical-only          FAILED tests/test_stack.py::test_the_deny_list_refuses_each_entry_before_any_step_runs[symlink-to-env-path]
KILLED   M3f-deny-pc-bridge-name        FAILED tests/test_stack.py::test_the_deny_list_refuses_each_entry_before_any_step_runs[pc-bridge-env-path]
KILLED   M4-containment-lexical-only    FAILED tests/test_stack.py::test_a_path_outside_the_tree_is_refused[symlink-file]
KILLED   M4b-realpath-substituted       FAILED tests/test_stack.py::test_a_path_value_inside_the_tree_reaches_the_program_tree_relative
KILLED   M5a-leader-only                FAILED tests/test_stack.py::test_a_step_past_its_timeout_loses_its_whole_process_group
KILLED   M5b-no-sigkill                 FAILED tests/test_stack.py::test_a_step_past_its_timeout_loses_its_whole_process_group
KILLED   M5c-no-grace                   FAILED tests/test_stack.py::test_a_step_past_its_timeout_loses_its_whole_process_group
KILLED   M6-unmapped-ok                 FAILED tests/test_stack.py::test_a_missing_instrument_prints_unmapped_and_fails_the_run_only_when_required[program-required]
KILLED   M6b-no-script-check            FAILED tests/test_stack.py::test_a_missing_instrument_prints_unmapped_and_fails_the_run_only_when_required[interpreter-script-optional]
KILLED   M7a-chain-ignores-status       FAILED tests/test_stack.py::test_a_chained_step_is_skipped_when_its_source_failed_or_printed_nothing[failed]
KILLED   M7b-chain-empty-runs           FAILED tests/test_stack.py::test_a_chained_step_is_skipped_when_its_source_failed_or_printed_nothing[silent]
KILLED   M7c-chain-lines-unchecked      FAILED tests/test_stack.py::test_a_chained_step_is_skipped_when_its_source_failed_or_printed_nothing[line-refused]
KILLED   M7d-chain-blank-lines-kept     FAILED tests/test_stack.py::test_a_chained_step_receives_its_sources_non_empty_lines_as_paths
KILLED   M8a-sequential                 FAILED tests/test_stack.py::test_one_groups_steps_run_in_parallel_and_the_groups_in_order
KILLED   M8b-groups-descending          FAILED tests/test_stack.py::test_one_groups_steps_run_in_parallel_and_the_groups_in_order
KILLED   M9a-when-ignored               FAILED tests/test_stack.py::test_when_selects_a_step_by_its_parameters - Asse...
KILLED   M9b-repeat-ignored             FAILED tests/test_stack.py::test_repeat_runs_a_step_n_times_with_numbered_sections
KILLED   M9c-each-first-only            FAILED tests/test_stack.py::test_foreach_runs_a_step_once_per_element_with_each
KILLED   M10-no-print-cap               FAILED tests/test_stack.py::test_the_whole_print_is_capped_at_9000_characters_cut_from_the_largest_section
KILLED   M10b-head-only-cap             FAILED tests/test_stack.py::test_a_section_over_cap_lines_keeps_its_first_and_last_lines
KILLED   M11-main-is-tree               FAILED tests/test_stack.py::test_a_run_from_a_worktree_logs_to_the_main_tree
KILLED   M11b-no-toplevel-check         FAILED tests/test_stack.py::test_the_tree_must_be_a_git_toplevel - AssertionE...
KILLED   M12-sha-over-stdout            FAILED tests/test_stack.py::test_the_run_record_holds_every_field_and_each_output_is_saved_whole
KILLED   M13-ratings-unchecked          FAILED tests/test_stack.py::test_ratings_ride_on_a_run_and_on_rate_and_must_name_a_recorded_run
KILLED   M14-repeated-key-overwrites    FAILED tests/test_stack.py::test_a_bad_key_is_refused_with_exit_2_naming_the_known_keys[repeated]
KILLED   M15a-no-version-check          FAILED tests/test_stack.py::test_a_bad_registry_exits_3_before_anything_runs[version-2]
KILLED   M15b-no-outward-check          FAILED tests/test_stack.py::test_a_bad_registry_exits_3_before_anything_runs[outward-true]
KILLED   M16-explain-runs               FAILED tests/test_stack.py::test_explain_runs_nothing_and_writes_no_record - ...
KILLED   M17-no-signal-handler          FAILED tests/test_stack.py::test_a_signal_to_the_runner_kills_its_live_steps_and_writes_no_record
KILLED   M18-transcript-first-of-many   FAILED tests/test_stack.py::test_the_transcript_of_an_agent_must_match_exactly_once[two]
KILLED   M19-match-not-fullmatch        FAILED tests/test_stack.py::test_every_type_refuses_a_value_outside_its_shape_before_any_step[agent-long]
KILLED   M20-nul-accepted               FAILED tests/test_stack.py::test_a_chained_step_is_skipped_when_its_source_failed_or_printed_nothing[line-nul]
KILLED   M21-thread-guard-removed       FAILED tests/test_stack.py::test_a_defect_inside_a_step_thread_fails_the_step_loudly
KILLED   MG1-no-harness-ports           FAILED tests/test_stack.py::test_gate_files_lists_every_test_that_names_a_path
KILLED   MG2-pycache-walked             FAILED tests/test_stack.py::test_gate_files_lists_every_test_that_names_a_path
KILLED   MG3-binary-read                FAILED tests/test_stack.py::test_gate_files_lists_every_test_that_names_a_path
KILLED   MG4-no-recursion               FAILED tests/test_stack.py::test_gate_files_lists_every_test_that_names_a_path
KILLED   MG5-no-self                    FAILED tests/test_stack.py::test_gate_files_lists_every_test_that_names_a_path
KILLED   MG6-any-name-under-tests       FAILED tests/test_stack.py::test_gate_files_lists_every_test_that_names_a_path
KILLED   MG7-all-code                   FAILED tests/test_stack.py::test_gate_files_why_names_code_and_comment_mentions_and_self
KILLED   MG8-docstrings-are-code        FAILED tests/test_stack.py::test_gate_files_why_names_code_and_comment_mentions_and_self
KILLED   MH1-first-call                 FAILED tests/test_stack.py::test_handback_extract_writes_the_last_calls_message_with_its_tags_neutralized
KILLED   MH2-no-neutralize              FAILED tests/test_stack.py::test_handback_extract_writes_the_last_calls_message_with_its_tags_neutralized
KILLED   MH3-prints-message             FAILED tests/test_stack.py::test_handback_extract_writes_the_last_calls_message_with_its_tags_neutralized
KILLED   MH4-any-record-type            FAILED tests/test_stack.py::test_handback_extract_writes_the_last_calls_message_with_its_tags_neutralized
PRODUCTION FILES UNCHANGED: True
EXPECTED=52 KILLED=52 SURVIVED=0 INVALID=0
```

The driver's negative control is its earlier pass: with M5a surviving, it printed `EXPECTED=48 KILLED=47 SURVIVED=1 INVALID=0` and exited 1. The driver was scratch and is deleted with the scratch dir; the design above is enough to rebuild it.

## Gates

`bash scripts/test_summary.sh` twice, each with a private `--basetemp` under scratch, over five files:
- `tests/test_stack.py`
- `tests/test_no_laya_in_gates.py` (KC-J1; my files match none of its walked shapes)
- the three tests that enumerate `scripts/`: `tests/test_s0_01_spec_runner.py` and `tests/test_s0_11_eval_hardening.py` copy the whole directory, and `tests/test_search_intercept.py` searches it.

```
5 files set=2804489b9d6b
run 1: pytest-exit: 0
       pytest-summary: 391 passed in 128.61s (0:02:08)
run 2: pytest-exit: 0
       pytest-summary: 391 passed in 145.29s (0:02:25)
```

**CI rehearsal:** Python 3.12, CI's version, in a scratch venv. The PATH held none of rg, graft, node, ripwire or code-review-graph. Run through `scripts/test_summary.sh`:

```
1 files set=2ac01abb1067
PATH=<scratch>/cibin: 3.12.3 True instruments on PATH: []
SKIPPED [1] tests/test_stack.py:974: rg (ripgrep) is not installed: the echo stack's code search needs it (CI has none)
pytest-exit: 0
pytest-summary: 106 passed, 1 skipped in 28.54s
```

**pyflakes and the U+2028/U+2029 check:**

```
pyflakes rc=0
separators scripts/stack.py: 0
separators scripts/stacks.toml: 0
separators scripts/gate_files.py: 0
separators scripts/handback_extract.py: 0
separators tests/test_stack.py: 0
```

## The eight stacks, real runs on this tree (default log dir `.jev/stacks/`)

Wall time, by a wrapper's clock around each call:

```
harvest rc=0 wall_s=.343659160
gate-plan rc=0 wall_s=.324932591
gate-run rc=0 wall_s=55.070148115
ctx rc=0 wall_s=9.277371282
impact rc=0 wall_s=3.819929955
impact-new rc=1 wall_s=2.397859640
find rc=0 wall_s=30.280333808
premise rc=0 wall_s=1.254746999
echo rc=0 wall_s=.581832034
ci rc=0 wall_s=2.203264059
```

The calls, in order:
- `harvest agent=a2f621e1d36efd61d`
- `gate paths=scripts/owner_rulings.py`, then again with `mode=run` (runs=2)
- `ctx files=scripts/hiccup_scan.py sym=build_page "q=who writes the hiccup page"`
- `impact sym=build_page`
- `impact sym=derive_words` (a new symbol)
- `find "q=how does a stack runner kill a step's process group on timeout"`
- `premise` on the five files
- `echo pattern=start_new_session`
- `ci` (default branch)

Header and section lines of each print (full prints are in `.jev/stacks/<run>/`; the harvest lines carry counts only):

```
=== harvest
stack harvest · run s-20260928T174808Z-3aca79 · exit 0
not selected: lint (when report=*), sha (when report=*)
## models · ok · rc 0 · 0.17 s
hiccup_scan: files=1 bytes=2003594 lines=436 unparsable=0 assistant_usage_model=215 tool_use=83 tool_result=83 errors=0 clusters=0 uncovered=0 task_reminder=0 silent_turn
## handback · ok · rc 0 · 0.07 s
handback: found calls=1 bytes=41506 neutralized=1 sha256=0579d69a8ad6 out=/home/user/agent-factory/.jev/stacks/s-20260928T174808Z-3aca79/handback.md
## agent_row · ok · rc 0 · 0.00 s
## lint_handback · ok · rc 0 · 0.07 s
report_lint: 3 refs — OK 2, NEAR 0, MISS 0, UNCHECKABLE 1, UNRESOLVED 0 (worktree)
=== gate-run
stack gate · run s-20260928T174809Z-8ae2e3 · exit 0
## tests · ok · rc 0 · 0.17 s
## why · ok · rc 0 · 0.22 s
## setid · ok · rc 0 · 0.03 s
2 files set=10cb8e3e25e5
## run[1/2] · ok · rc 0 · 26.60 s
pytest-summary: 111 passed in 26.27s
## run[2/2] · ok · rc 0 · 28.09 s
pytest-summary: 111 passed in 27.68s
## clean · ok · rc 0 · 0.00 s
=== ctx
stack ctx · run s-20260928T174904Z-619829 · exit 0
## pack · ok · rc 0 · 9.14 s
## scripts/hiccup_scan.py
## graft ask — who writes the hiccup page
## symbol build_page
  "impactedCount": 3,
  "risk": "LOW",
## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
=== impact
stack impact · run s-20260928T174913Z-b063a5 · exit 0
print capped at 9,000 characters: shortened ripwire
## gitnexus · ok · rc 0 · 3.69 s
  "impactedCount": 3,
  "risk": "LOW",
## crg_callers · ok · rc 0 · 0.47 s
## crg_tests · ok · rc 0 · 0.62 s
## ripwire · ok · rc 0 · 1.13 s
=== impact-new
stack impact · run s-20260928T174917Z-ba4522 · exit 1 — required, not ok: gitnexus
## gitnexus · FAILED · rc 1 · 2.28 s
  "error": "Target 'derive_words' not found",
  "impactedCount": 0,
  "risk": "UNKNOWN"
## crg_callers · ok · rc 0 · 0.67 s
## crg_tests · ok · rc 0 · 0.53 s
## ripwire · ok · rc 0 · 1.33 s
=== find
stack find · run s-20260928T174919Z-6f2bb6 · exit 0
print capped at 9,000 characters: shortened rulings, registry
## graft · ok · rc 0 · 2.76 s
## rulings · ok · rc 0 · 0.07 s
## chat · ok · rc 0 · 30.17 s
## registry · ok · rc 0 · 0.12 s
=== premise
stack premise · run s-20260928T174950Z-d2d758 · exit 0
## tracked · ok · rc 1 · 0.01 s
## sha · ok · rc 0 · 0.01 s
## lines · ok · rc 0 · 0.00 s
## last[1/5] · ok · rc 0 · 0.22 s
## last[2/5] · ok · rc 0 · 0.21 s
## last[3/5] · ok · rc 0 · 0.22 s
## last[4/5] · ok · rc 0 · 0.22 s
## last[5/5] · ok · rc 0 · 0.27 s
=== echo
stack echo · run s-20260928T174951Z-7742a0 · exit 0
## code · ok · rc 0 · 0.12 s
## files · ok · rc 0 · 0.07 s
## registry · ok · rc 1 · 0.02 s
## ap · ok · rc 0 · 0.32 s
```

**Harvest of `a2f621e1d36efd61d`:**
- 215 assistant records, all `claude-opus-5-5 215`: 82 turns, 0 errors, 0 refusal stops.
- The extracted file (41,506 bytes, 1 tag neutralized) has sha256 `0579d69a8ad603ba7af3d27b777c78bfaae913f6edd100c9a2ac84b65bbdd4f5`.
- In the impact run, the head-and-tail cut kept ripwire's `edit-check` element (verified on an earlier run's print).

Two full prints:

```
stack gate · run s-20260928T174808Z-9fe793 · exit 0
tree /home/user/agent-factory · HEAD c4b87d156824
params: paths=scripts/owner_rulings.py mode=plan runs=2
outputs: /home/user/agent-factory/.jev/stacks/s-20260928T174808Z-9fe793/ (<step>.out each) · record: /home/user/agent-factory/.jev/stacks/runs.jsonl
not selected: run (when mode=run), clean (when mode=run)

## tests · ok · rc 0 · 0.17 s
$ python3 scripts/gate_files.py scripts/owner_rulings.py
tests/test_owner_rulings.py
tests/test_stack.py

## why · ok · rc 0 · 0.16 s
$ python3 scripts/gate_files.py --why scripts/owner_rulings.py
tests/test_owner_rulings.py  comment:1
tests/test_stack.py  code:747

## setid · ok · rc 0 · 0.03 s
$ bash scripts/pc_suite.sh set-id -- tests/test_owner_rulings.py tests/test_stack.py
2 files set=10cb8e3e25e5
```

```
stack ci · run s-20260928T174951Z-ae16c6 · exit 0
tree /home/user/agent-factory · HEAD c4b87d156824
params: branch=claude/soundbox-kit-migration-iz1jwf
outputs: /home/user/agent-factory/.jev/stacks/s-20260928T174951Z-ae16c6/ (<step>.out each) · record: /home/user/agent-factory/.jev/stacks/runs.jsonl

## verdict · ok · rc 75 · 2.08 s
$ python3 scripts/ci_gate.py --branch claude/soundbox-kit-migration-iz1jwf
--- stderr ---
WAIT by ci-gate: run #1116 (c4b87d1) is in_progress — https://github.com/Pxls21/agent-factory/actions/runs/36459226182
Wait for the verdict: python3 scripts/ci_gate.py --branch claude/soundbox-kit-migration-iz1jwf --wait 1800
or push without waiting: CI_WAIT_SKIP=<reason>
```

## DISCREPANCIES

**Deviations from the brief's plan**
- **D1. `ci.branch` is `text`, not `word`** (`[stacks.ci.params.branch]`, `scripts/stacks.toml:336`).
  - `word` refuses `/`, so the current branch `claude/soundbox-kit-migration-iz1jwf` would be refused.
  - Its `default = "{branch}"` (`scripts/stacks.toml:338`): a default may name the built-ins tree, main, head and branch. It is resolved, then validated, at run time.
- **D2. `ctx` runs lane_context.sh without `-o`.** With `-o` it writes the file and prints one line (`if [ -n "$OUT" ]` at `scripts/lane_context.sh:91`), so the pack would never be printed. Without `-o`, the pack is the step's own saved output and its print (`id = "pack"`, `scripts/stacks.toml:152`).
- **D3. The echo rg steps add `--sort path`** (`id = "code"`, `scripts/stacks.toml:298`).
  - rg prints in completion order, and design §4.2 says every stack is reproducible.
  - The resulting order is the roots as given, each walked in path order (not one global sort). Two runs gave the same sha256.
- **D4. `find.chat` pins `--order lexical --no-jev-log`** (`id = "chat"`, `scripts/stacks.toml:226`). Both are today's defaults; pinned, "no model in a stack" no longer rests on a default.
- **D5. `split_from` derives words** (`SPLIT_STOP`, `scripts/stack.py:75`).
  - It keeps word-shaped tokens of 3 or more characters, minus a stop set and duplicates, in first-seen order.
  - owner_rulings.py matches any word as a substring, so "the" or "how" would hit nearly every owner row.
  - A value given for a derived key is refused (exit 2).
- **D6. A section over its cap keeps head and tail** (`def cap_lines`, `scripts/stack.py:872`); the print cap cuts the middle of the largest sections. The brief does not say which lines. test_summary.sh's verdict and ripwire's element both come last.
- **D7. `[tools]` code-review-graph lists `~/venv-crg/...` first** (`code-review-graph`, `scripts/stacks.toml:15`), for the PC.
- **D8. The deny list adds `$HOME` forms of the three `/root` entries** (`DENY_DIRS`, `scripts/stack.py:83`).
- **D9. Record entries carry `n`** (1-based) for each call of a repeat or foreach step.
- **D10. premise's tracked, sha and lines take ok_rc 0,1:** rc 1 there is a measured fact.
- **D11. `echo.ap` is `required = false`** (`id = "ap"`, `scripts/stacks.toml:322`). A pattern found nowhere SKIPS `ap`, and that good outcome must not exit 1.

**Findings for you**
- **D12. The gate stack's basetemp `{run}/bt` lies inside the main work tree** (`.jev/stacks/<run>/bt`). A test that needs tmp_path outside any git repo sees agent-factory there.
  - Measured: the first real gate run read 1 failed, 110 passed, twice. The failure was my own test's plain-directory case, which got "not a toplevel".
  - Fixed in the test with `GIT_CEILING_DIRECTORIES` in its `run()`: red before, green after, inside and outside the repo.
  - Not measured for the repo's other tests. Candidates: `tests/test_proof_status.py:387` and `:402`, which expect "is not a git repository", and `tests/test_fubuki_pin_sync.py:129`.
  - Options: a `{tmp}` built-in (not in the brief), or a step env field (not in the schema).
- **D13. harvest's lint is two steps with distinct ids:** `lint` when report is set, `lint_handback` when it is not.
- **D14. Runner behavior beyond the brief:**
  - The runner's own INT, TERM and HUP kill its live step groups.
  - A defect inside a step's thread fails that step loudly (`except BaseException`, `scripts/stack.py:720`). Found by the NUL mutant: realpath raised `ValueError` in a worker thread, the thread died, and the step vanished from the record and from the exit code.
- **D15. A step whose `when` does not match is left out of the record.** Counted as skipped, it would make every plan-mode gate exit 1. The print lists it under `not selected:`.
- **D16. Instruments keep their own gitignored caches during real runs:** graft refreshes `graft/` (four files in the probe), Python writes `__pycache__`, and code-review-graph leaves an empty `.code-review-graph/` where no graph exists. The stack itself writes only `.jev/stacks/`. One transient write of mine: a pytest basetemp probe at `.jev/stacks/probe-bt`, removed.
- **D17. `scripts/ripwire_review.sh` exits 0 when its binary is missing** (`exit 0` after its `missing` line, `scripts/ripwire_review.sh:36`). The `impact` ripwire section then reads `ok · rc 0` (measured with `RIPWIRE_BIN=/nonexistent/ripwire`). Visible, but the status says ok. Not fixed: outside my boundary.
- **D18. A Write-tool quirk.** A tag-shaped string in my Write input, carrying the harness's tag-namespace prefix, landed in the file without the prefix; the first test run failed on it. The fixture now builds the prefix in code (`NS`, `tests/test_stack.py:865`). It belongs in env-tool-quirks, beside the separator quirk; not written.
- **D19. `rate` accepts a rating of any recorded run** (see NOT done).
- **D20. The worktree test does not pass `--log-dir`:** its subject is the default log dir. Its main tree is a temporary repo, and it asserts the worktree's `.jev/` stays absent.
- **D21. handback_extract.py exits 0 found, 1 absent (no file written), 2 usage or I/O.** On a lane with no handback, harvest shows two failed sections for one cause.
- **D22. `impact` exits 1 on a symbol GitNexus has not indexed yet.** GitNexus answers "Target … not found" with rc 1, while code-review-graph answers `not_found` with rc 0.

## Self-attack: the three likeliest ways this is wrong

1. **The gate stack's green can differ from a plain pytest run, because of D12.**
   - Ruled out for `tests/test_stack.py` only: a real gate run went red on it, and the fix is green in and out of the tree.
   - Not ruled out for the repo's other tests.
2. **The deny list can be walked around.**
   - Ruled out by tests:
     - each entry, by name and via a symlink, as `path` and within `paths`;
     - symlinked files and directories out of the tree, `..`, and absolute paths;
     - chained lines, which are validated as paths.
   - The lexical-only and realpath-substitution mutants both die.
   - Not ruled out: hardlinks.
3. **A step can outlive its runner.**
   - Ruled out: the timeout group kill (two grandchildren, three mutants) and INT, TERM and HUP to the runner (M17).
   - Not ruled out: a SIGKILL of the runner, a step that calls setsid, and a leftover child after a normal exit.

## Evidence tiers

- **Verified:**
  - the premise re-run and every interface form above;
  - `tests/test_stack.py` on Python 3.11 and 3.12;
  - both gate runs and the mutation pass with its control;
  - the real runs of the eight stacks;
  - pyflakes and the separator check.
- **Inferred:**
  - CI as non-root (realpath non-strict, from CPython's source);
  - the repo's other tests under the in-tree basetemp;
  - the ripwire step on CI, where the wrapper would print `missing` with rc 0.
- **Assumed:** nothing named.

<!-- Coordinator note (2026-09-28): the round-2 section below is the lane's hand-back, extracted verbatim from its transcript by `python3 scripts/stack.py harvest agent=ac753871198ee8cfd` (run s-20260928T194356Z-03aebd; handback sha256 e652a7022cde; 827 assistant records, all claude-opus-5-5, 0 refusal stops). The harness refused the lane's own write of this file. -->

## Round 2 (ripwire and sentrux active; the round-1 findings)

LS-B9 round 2: task #339, D-103 and D-104. Written 2026-09-28 at 19:3xZ (`date -u` read 19:33:41Z). HEAD was 9d6799845f8f. Other lanes committed during the round; my files are untracked, and no commit touched them.

**The report file was not written.** The harness forbids a subagent to write a report file: round 1's write of this file was refused, and this session's standing note repeats the rule. This hand-back is therefore the whole round-2 section, full text. Save it with `harvest`, as in round 1.

### TL;DR
- **DONE, not landed.** All seven items are built. Each has a test, a killed mutant and a real run on this tree.
- ripwire now runs in `gate` (a new `graph` step) and in the new `review` stack. sentrux runs in `review`.
- A missing binary now reads `unmapped — <tool> unavailable` on every ripwire and sentrux step, never ok.
- Gates: `147 passed` twice (`1 files set=2ac01abb1067`) and `431 passed` twice (`5 files set=2804489b9d6b`).
- CI rehearsal (Python 3.12, no instrument on the PATH): `145 passed, 2 skipped`.
- Mutation: 100 of 100 killed (r1 52/52, r2 48/48). Each control ran green first, and the production files are unchanged.
- Three deviations change the brief's wording (details under Deviations):
  - ripwire gets one comma-joined argument through a new `{paths,}` placeholder.
  - The run list holds pytest test files only.
  - A new helper, scripts/lint_files.py, replaces lint_delta.py in `review`.
- **The main new risk:** with graph=yes, ripwire links about a hundred test files to any change that touches `main`-named functions. It linked 105 to my own files. Read the plan before `mode=run`.

### NOT done (read first)
1. **The ripwire-linked tests for my own files were not run.**
   - `gate` lists 102 pytest files for my seven files: ripwire linked 105 (D24).
   - Only the two required gate sets ran.
   - The list includes tests/test_vendored_manifest.py. By env-tool-quirks, a whole-file run of it copies about 3.4 GB.
2. **Shell tests are listed, not run.** The run step gives pytest test files only. A shell test that names a changed path (harness-ports/tests/*.sh) appears in `sources` with "not run" and must be run by hand. No stack runs shell tests.
3. **Wrapper defects stay open for task #345** (not my files): the multi-file test-gate, lane_context.sh's blank ripwire sections, and sentrux's single shared baseline (D26, D27).
4. **`review mode=compare` with no saved baseline reads `ok`.** The wrapper prints "no baseline" and exits 0. The step is advisory. It is not a missing instrument, so `unmapped_if` does not cover it.
5. **A SIGKILL of the runner leaves its `{tmp}` dir**, and its steps keep running. SIGINT, SIGTERM and SIGHUP remove the dir.
6. **The CI rehearsal is only close to CI.**
   - As root, `/root/.local/bin` is always reachable, so the rehearsal points RIPWIRE_BIN and SENTRUX_BIN at missing paths.
   - On real CI (non-root) the wrappers' own search fails instead. This is assumed, not run.
   - The rehearsal's code-review-graph steps ran ok through the absolute `[tools]` path /root/venv-crg/bin/code-review-graph. On CI they would read unmapped (assumed).
7. **Some mutants named in docstrings were never run.** The driver runs one test node per mutant, so these are inferred to fail, not measured:
   - the harvest test's run-dir mutant;
   - the two mutants of the sandbox-only ripwire gate test (the copy's ripwire would index the copy);
   - the join test's "each element its own argument";
   - the bad-registry "unset list" case;
   - the report test's no-hand-back clause.
8. **The round-1 section's line citations are stale.** Its citations into scripts/stack.py and tests/test_stack.py no longer match; both files grew.
9. **`.lanes-live` does not list my two new helpers**, scripts/gate_union.py and scripts/lint_files.py. Add them before landing. I may not edit that file.

### The items

**Item 1. `gate` uses ripwire.**
- **Steps.** `graph` (`id = "graph"`, `scripts/stacks.toml:127`), `union` (`id = "union"`, `scripts/stacks.toml:142`) and `sources` (`id = "sources"`, `scripts/stacks.toml:149`). A new parameter `graph` takes yes or no; the default is yes.
- **The union.** A new helper, scripts/gate_union.py, unites gate_files' list with ripwire's `<t>` rows.
  - `def ripwire_tests` (`scripts/gate_union.py:42`) reads only the rows inside the one `<test-gate>` element, never the XML comment.
  - Two elements, or an attribute given twice, is refused rather than read last-wins (AF-AP-41).
  - A row whose file is gone is left out and named.
  - With no element (ripwire unmapped or failed), the union is gate_files' list, and both outputs say so.
- **The run list** holds the union's pytest test files (`TEST_FILE_RE`, `scripts/gate_union.py:36`).
- **The print shows each test's source.** `sources` prints gate_files, ripwire or both for each test, and names each file left out.
- **ripwire's output format**, verified on this tree (run s-20260928T193032Z-1e48ac). The saved file is 2,966 bytes: an XML comment of about 2 KB, then this element:
```
<test-gate changed="2" impacted="6" tests="2" untested="0" shown_tests="2" tests_capped="0" shown_untested="0" untested_capped="0" script_gates_unmodelled="12" script_gates_registered="0" script_gates_mapped="0" script_gates_unresolved_dynamic="0" ccx_bar="15" graph_ambiguous="787" graph_unresolved="926" counts_floor="1" total="0" has_more="0" next_offset="0" offset="0" limit="20" at="9d6799845+dirty" root="/home/user/agent-factory" next="python3 /home/user/agent-factory/tests/test_governance_bounds.py"><t p="tests/test_governance_bounds.py" run="python3 /home/user/agent-factory/tests/test_governance_bounds.py"/><t p="tests/test_governance_pin_enforcement.py" run="python3 /home/user/agent-factory/tests/test_governance_pin_enforcement.py"/></test-gate>
```
- **ripwire's exit codes and limits:** it exits 4 when either list is non-empty, 1 on a path it cannot match (a deleted file), and 0 otherwise. `--limit` caps the `<u>` rows only.
- **Tests:**
  - `test_gate_union_unites_gate_files_and_ripwires_rows` (`tests/test_stack.py:1311`)
  - `test_gate_union_refuses_an_ambiguous_ripwire_output` (`tests/test_stack.py:1348`)
  - `test_gate_union_without_an_answer_from_ripwire_says_so` (`tests/test_stack.py:1359`)
  - `test_gate_plan_runs_on_this_tree` (`tests/test_stack.py:1012`): graph=no, runs on CI.
  - `test_gate_with_the_graph_unites_gate_files_and_ripwires_tests_on_this_tree` (`tests/test_stack.py:1465`): real ripwire; skips where ripwire is absent.
- **Mutants killed:** R6 and R7 (by the explain pin), R8, R9, R10, R11a, R11b, R12, R13, R14, R14b and R14c.
- **Real run:** plan mode, graph=yes. Wall 1.26 s, exit 0.
```
params: paths=src/agent_factory/governance/bounds.py,scripts/gate_union.py mode=plan runs=2 graph=yes
## graph · ok · rc 4 · 0.91 s
## union · ok · rc 0 · 0.20 s
tests/test_governance_bounds.py
tests/test_governance_pin_enforcement.py
tests/test_stack.py
## sources · ok · rc 0 · 0.20 s
tests/test_governance_bounds.py  ripwire
tests/test_governance_pin_enforcement.py  ripwire
tests/test_stack.py  gate_files
gate_files 1 · ripwire 2 · union 3 · run list 3 · ripwire untested blast radius: 0 symbols (0 shown)
## setid · ok · rc 0 · 0.03 s
3 files set=178726f8fd94
```
  The two governance tests import bounds.py but never name its path, so only ripwire finds them.
- **Real run over my own seven files** (run s-20260928T193218Z-854ab8, wall 1.39 s, exit 0):
  - `gate_files 1 · ripwire 105 · union 106 · run list 102 · ripwire untested blast radius: 620 symbols (20 shown) · 4 union file(s) are not pytest test files (test_*.py, *_test.py), left out of the run list; run a test among them by hand: tests/fixtures/jev_pipes/capture_shapes.py tests/fixtures/jev_pipes/make_fixture.py tests/fixtures/jev_pipes/make_pass_fixture.py tests/fixtures/jev_pipes/record_answers.py`
  - `102 files set=5478a1537ddd`

**Item 2. The `review` stack.**
- **The stack:** `[stacks.review]` (`scripts/stacks.toml:376`), with `rated = true`. Parameters: `files` (paths) and `mode` (check, save or compare; the default is check). Use `review mode=save` before a build lane and `review mode=compare files=...` after it.
- **`sentrux`** (`id = "sentrux"`, `scripts/stacks.toml:393`) runs `bash scripts/sentrux_review.sh {mode}`.
  - It is advisory (`required = false`), with `unmapped_if` set and `tool = "sentrux"`.
  - The wrapper takes no file list. It scans its own copy of proofs/, scripts/, tests/, harness-ports/, spikes/ and src/ in `.sentrux-runtime/tree` (about 66 MB) and keeps the baseline there.
- **`ripwire`** (`id = "ripwire"`, `scripts/stacks.toml:403`) runs `bash scripts/ripwire_review.sh test-gate {files,}`. It takes ok_rc 0 and 4, has `unmapped_if` set and `tool = "ripwire"`, and runs when files is set.
- **`lint`** (`id = "lint"`, `scripts/stacks.toml:416`) runs `python3 scripts/lint_files.py {files*}`. **DEVIATION:**
  - lint_delta.py takes no file list: only `--staged` or `--base REV`, over git's changed tracked .py files (verified from its argparse).
  - In this shared tree it would lint other lanes' files, and it never sees an untracked file.
  - The new helper scripts/lint_files.py imports lint_delta's own `_flakes` rule (`def load_lint_delta`, `scripts/lint_files.py:25`), so the two cannot drift.
  - It reads HEAD once per run (`def resolve_head`, `scripts/lint_files.py:32`; AF-AP-175).
  - A hit is NEW when the file's HEAD version lacks it. Every hit in an untracked file counts as new.
  - It skips a path that is not a .py file, is absent, or lies outside the root (`"outside the root"`, `scripts/lint_files.py:60`).
  - It exits 1 when there is a NEW hit.
- **`ap`** runs `python3 scripts/ap_screen.py {files*}`.
- **Tests:**
  - the explain pins `review-compare` and `review-save` in `test_explain_of_each_wave1_stack_is_pinned` (`tests/test_stack.py:979`)
  - `test_the_real_ripwire_and_sentrux_steps_read_unmapped_when_their_binaries_are_missing` (`tests/test_stack.py:1430`)
  - `test_lint_files_counts_only_the_hits_a_file_adds` (`tests/test_stack.py:1380`)
- **Mutants killed:** R31, R32, R35, R36 and R37.
- **Real runs, save then compare.** A shared baseline from 2026-09-07 already exists in `.sentrux-runtime/`, and a default `save` would overwrite it. Both runs therefore set `SENTRUX_RUNTIME_DIR` to a scratch dir, the wrapper's own override. The shared baseline's mtime is unchanged (2026-09-07 22:57:01Z).
```
review mode=save                                   (wall 5.43 s, exit 0)
## sentrux · ok · rc 0 · 5.32 s
Baseline saved to <scratch>/sentrux-rt/tree/.sentrux/baseline.json
Quality: 7141
sentrux save: tool exit 0 (advisory — never a gate; --strict passes it through)

review mode=compare files=scripts/gate_union.py,scripts/lint_files.py,scripts/stack.py   (wall 5.38 s, exit 0)
## sentrux · ok · rc 0 · 5.28 s
Quality:      7141 -> 7141
Coupling:     0.28 → 0.28
Cycles:       0 → 0
God files:    0 → 0
✓ No degradation detected
## ripwire · ok · rc 4 · 0.99 s
## lint · ok · rc 0 · 0.31 s
lint_files (worktree vs HEAD 9d6799845f8f, the given files): 3 .py linted, 0 NEW pyflakes hit(s), 0 removed
## ap · ok · rc 0 · 0.32 s
--- AP_SCREEN over 3 path(s): 9 hits over 3 files ---
```
- **The 9 AP-screen hits on my files, classified:**
  - AF-AP-175 (4 hits): reviewed-safe. lint_files reads HEAD once; stack.py's `_head` and `_branch` go through Env's per-run cache.
  - AP-32: reviewed-safe. The hash is over exactly the bytes written.
  - AF-AP-72: reviewed-safe. `int()` reads a value already validated as digits.
  - AF-AP-43: not applicable. The timestamp measures a duration and makes no ordering claim.
  - AF-AP-115 (2 hits): a documented limit. The runner resolves programs on the caller's PATH, as any shell does. No stack verifies a signature.

**Item 3. A missing instrument never reads ok.**
- **Two new step fields.** `unmapped_if` (`self.unmapped_if`, `scripts/stack.py:253`) and `tool`, an addition: each such step's program is `bash`, so `tool` names the instrument.
- **The rule** (`step.unmapped_if`, `scripts/stack.py:841`): when a step ends ok or failed and its stdout or stderr holds the `unmapped_if` text, its status becomes `unmapped — <tool> unavailable`.
  - The record keeps the wrapper's exit code.
  - The wrapper's line still prints: an unmapped step with an exit code keeps its body (`quiet = r.status`, `scripts/stack.py:1230`).
  - A required unmapped step fails the run.
- **Where it is set:** on all four ripwire and sentrux steps: gate.graph, impact.ripwire, review.ripwire and review.sentrux. A static test checks that set against each wrapper's own missing-binary line, read from the wrapper's source.
- **Tests:**
  - `test_unmapped_if_turns_a_wrappers_missing_line_into_unmapped` (`tests/test_stack.py:334`): four cases.
  - `test_every_ripwire_and_sentrux_step_reads_unmapped_on_its_wrappers_missing_line` (`tests/test_stack.py:1410`)
  - `test_the_real_ripwire_and_sentrux_steps_read_unmapped_when_their_binaries_are_missing` (`tests/test_stack.py:1430`): RIPWIRE_BIN and SENTRUX_BIN point at missing paths; runs on CI.
- **Mutants killed:** R2, R3, R4, R5, R32, R33 and R34.
- **Real run:** `RIPWIRE_BIN=/nonexistent/ripwire python3 scripts/stack.py impact sym=build_page`. Wall 6.73 s, exit 1.
```
stack impact · run s-20260928T193025Z-d34d91 · exit 1 — required, not ok: ripwire
## gitnexus · ok · rc 0 · 6.60 s
## crg_callers · ok · rc 0 · 0.50 s
## crg_tests · ok · rc 0 · 0.61 s
## ripwire · unmapped — ripwire unavailable
$ bash scripts/ripwire_review.sh edit-check build_page
ripwire_review: /nonexistent/ripwire missing — run scripts/setup.sh (pinned install)
```
  In round 1 this section read `ok · rc 0` (D17).

**Item 4. D12: the `{tmp}` built-in.**
- **What it is:** `/tmp/stack-<run id>` (`TMP_BASE`, `scripts/stack.py:65`), mode 0700.
- **Creation:** `def make_tmp` (`scripts/stack.py:1141`) creates it and refuses with exit 3 when git finds a work tree there. **Deviation:** it is created only when a selected step names `{tmp}` (see Deviations).
  - It is created inside `def setup()` (`scripts/stack.py:1186`).
  - setup runs under the runner's signal handlers (`def run(self, plan, setup=None)`, `scripts/stack.py:861`).
- **Removal:** a `finally` removes it (`def remove_tmp`, `scripts/stack.py:1153`) on success, failure and SIGINT, SIGTERM or SIGHUP. The header then says `tmp <dir> · removed after the run`.
- **The gate's run step** now passes `"--basetemp={tmp}/bt"` (`scripts/stacks.toml:166`). Round 1's `clean` step is gone; it existed only to remove the in-tree basetemp.
- **The red-then-green proof:** `test_the_gates_run_step_gives_pytest_a_basetemp_outside_every_work_tree` (`tests/test_stack.py:1499`).
  - It runs the real registry's gate stack in a temporary repository. That repository holds the gate's real scripts, copied byte for byte, and one test that needs its tmp_path outside every git work tree.
  - The log dir lies inside the tree, as the default `.jev/stacks/` does.
  - With the registry as it stands: green.
  - With round 1's `--basetemp={run}/bt`: **red**; the inner test fails with "lies inside the work tree".
- **Other tests:**
  - `test_tmp_is_a_private_dir_outside_every_work_tree_removed_after_the_run` (`tests/test_stack.py:1547`): a success case and a failure case.
  - `test_a_signal_to_the_runner_removes_its_tmp` (`tests/test_stack.py:1569`)
  - `test_a_tmp_inside_a_git_work_tree_is_refused` (`tests/test_stack.py:1595`)
  - the record test: no dir and no header line unless a step names `{tmp}`.
- **Mutants killed:** R15, R16, R16b, R17, R18 and R18b.
- **Real run:** gate A under Gates (`gate paths=scripts/lint_files.py mode=run graph=no`, wall 76.67 s). The header printed `tmp /tmp/stack-s-20260928T192114Z-7f1a30 · removed after the run`, and afterwards no `/tmp/stack-*` dir existed.

**Item 5. D19: only rated stacks take ratings.**
- **Where:** `self.rated` (`scripts/stack.py:326`). The check sits in `def check_ratings` (`scripts/stack.py:1044`), at `stack.rated` (`scripts/stack.py:1069`).
- **Which stacks:** ctx, echo, find, impact and review are rated. `list` ends their lines with ` · rated`.
- **The rule as built:** a rating of an unrated stack's run is refused with exit 2, by `rate` and by `--rate`. A run refused over its `--rate` never starts. A rating of a rated stack's run may ride on any run: the rated run decides. **Flagged:** this is my reading of "refuse any other run".
- **Test:** `test_only_a_rated_stack_takes_ratings` (`tests/test_stack.py:616`). **Mutant killed:** R19.
- **Real run.** No rating was written; the log holds 0 rating lines.
```
$ python3 scripts/stack.py rate s-20260928T193032Z-1e48ac=2/2
stack: rating: run s-20260928T193032Z-1e48ac is a gate run, and only a rated stack takes ratings (ctx, echo, find, impact, review)
rate rc=2
$ python3 scripts/stack.py premise files=scripts/gate_union.py --rate s-20260928T193045Z-207a66=1/1
stack: rating: run s-20260928T193045Z-207a66 is a harvest run, and only a rated stack takes ratings (ctx, echo, find, impact, review)
--rate rc=2
```

**Item 6. The cap on saved output.**
- **Size:** `SAVE_CAP_MB` is 20 by default (`scripts/stack.py:63`). A step can set its own `save_cap_mb`, from 1 to 1024 (`scripts/stack.py:261`).
- **The kill.** Every `POLL_S` (0.1 s, `scripts/stack.py:64`), the runner compares a running step's saved size with its cap (`os.fstat`, `scripts/stack.py:821`).
  - Past the cap, the step's process group is killed.
  - The step FAILS, with the note "killed: its saved output passed the N MB cap".
  - **DEVIATION (an addition):** the brief said "truncate". Without the kill, a runaway writer fills the disk until its timeout.
- **The truncation.** `def save` (`scripts/stack.py:847`) cuts the saved output at the cap and ends it with the line `… saved output truncated at N MB (save_cap_mb N); the rest was not saved`. The record then says `truncated: true` (`r.truncated`, `scripts/stack.py:1207`).
  - A step whose saved form passes the cap only when it is written (stdout, then the stderr header, then stderr) stays ok and is truncated.
- **Chains:** a truncated source feeds no chain (`r.truncated`, `scripts/stack.py:733`); its consumer is SKIPPED.
- **Test:** `test_a_steps_saved_output_is_capped_and_a_truncated_source_feeds_no_chain` (`tests/test_stack.py:539`). **Mutants killed:** R20, R21, R22 and R23.
- **Real run on this tree.** No step of the real registry writes 20 MB, so this run used `--tree` on this tree with a scratch registry: save_cap_mb 1, and one step that writes 3 MB then sleeps 30 s. Wall 0.29 s.
```
stack capdemo · run s-20260928T193323Z-21b136 · exit 1 — required, not ok: flood
## flood · FAILED · rc -15 · 0.15 s — killed: its saved output passed the 1 MB cap
… saved output truncated at 1 MB (save_cap_mb 1); the rest was not saved
{'status': 'failed', 'rc': -15, 'bytes': 1048652, 'truncated': True, 'secs': 0.152}
```

**Item 7. `harvest`.**
- **(a) The lint is advisory.** `lint` and `lint_handback` are `required = false` (`scripts/stacks.toml:63` and `scripts/stacks.toml:73`).
  - Test: `test_harvest_prints_a_failing_lint_and_still_exits_0` (`tests/test_stack.py:1134`). A report with a MISS still harvests with exit 0, and the MISS row still prints.
  - Mutant killed: R24.
- **(b) The extractor also finds a lane's full report.**
  - `def scan` (`scripts/handback_extract.py:51`) reads only `text` blocks and SubagentHandback calls. It never reads a thinking block.
  - The report is the last text block of `LONG` (1,000) characters or more **written before the last hand-back call** (`long_at_call`, `scripts/handback_extract.py:86`). It is saved as REPORT when it is longer than the hand-back, and the status line says which of the two is longer.
  - **Why "before the last call":** in the scrubber repair's transcript, the report is line 2495 (63,540 characters), the call is line 2496, and a 2,910-character epilogue follows at line 2499. "The last long text block" picked the epilogue.
  - **DEVIATION:** stdout is now one line, the path of the longer file (`print(target)`, `scripts/handback_extract.py:140`). The status lines moved to stderr. This lets the stack chain the path, so `lint_handback` lints the longer file.
  - Tests: `test_handback_extract_saves_the_lanes_longer_text_report` (`tests/test_stack.py:1194`); `test_handback_extract_writes_a_report_only_when_it_is_longer` (`tests/test_stack.py:1220`: four cases, including the 999/1000 bound); `test_harvest_saves_and_lints_a_lanes_longer_text_report` (`tests/test_stack.py:1116`).
  - Mutants killed: R25, R25b, R26, R27, R27b, R28 and R41.
- **(c) D21: no hand-back skips the lint.** `lint_handback` chains the extractor's stdout (`"{@handback*}"`).
  - With no hand-back, the extractor prints nothing and exits 1.
  - The handback step then FAILS, so the run exits 1.
  - The lint is SKIPPED, not failed.
  - Test: `test_harvest_with_no_handback_skips_the_lint` (`tests/test_stack.py:1147`). Mutants killed: R29 and R30.
- **Real run:** `harvest agent=a88c7c57f2fa2a96b`, the scrubber repair. Wall 1.66 s, exit 0.
```
## handback · ok · rc 0 · 1.32 s
/home/user/agent-factory/.jev/stacks/s-20260928T193045Z-207a66/report.md
--- stderr ---
handback: found calls=2 chars=3568 bytes=3568 neutralized=0 sha256=34835ad37c4d out=.../handback.md
report: saved chars=63540 bytes=63552 neutralized=0 sha256=e692c1c6f80c out=.../report.md (the longer: 63540 characters against the hand-back's 3568)
## lint_handback · ok · rc 0 · 0.10 s
$ python3 scripts/report_lint.py --root /home/user/agent-factory /home/user/agent-factory/.jev/stacks/s-20260928T193045Z-207a66/report.md
report_lint: 1 refs — OK 1, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
```

### The round-1 findings now
- **D12** (the basetemp inside the work tree): fixed by item 4.
- **D17** (ripwire reads ok when its binary is missing): fixed in the stacks by item 3. The wrapper itself still exits 0; that is task #345.
- **D19** (any recorded run takes a rating): fixed by item 5.
- **D21** (no hand-back fails the lint): fixed by item 7c.
- **The NOT-done output cap:** built as item 6.
- **D22** (`impact` exits 1 on a symbol GitNexus has not indexed): unchanged. Today `build_page` resolved, and gitnexus read ok.

### Gates
Counts are pasted from scripts/test_summary.sh; set ids come from scripts/pc_suite.sh set-id. Each gate had a private basetemp outside every git work tree (`git rev-parse` there says "not a git repository").

**Gate A: tests/test_stack.py.** It ran through my own gate stack: `gate paths=scripts/lint_files.py mode=run graph=no`, run s-20260928T192114Z-7f1a30, wall 76.67 s.
```
## setid · ok · rc 0 · 0.03 s
1 files set=2ac01abb1067
## run[1/2] · ok · rc 0 · 38.08 s
$ bash scripts/test_summary.sh --basetemp=/tmp/stack-s-20260928T192114Z-7f1a30/bt tests/test_stack.py
pytest-exit: 0
pytest-summary: 147 passed in 37.73s
## run[2/2] · ok · rc 0 · 38.04 s
pytest-exit: 0
pytest-summary: 147 passed in 37.74s
```

**Gate B: round 1's five files.** tests/test_stack.py, tests/test_no_laya_in_gates.py, tests/test_s0_01_spec_runner.py, tests/test_s0_11_eval_hardening.py and tests/test_search_intercept.py, run as `bash scripts/test_summary.sh --basetemp=<scratch>/gb/btN ...`:
```
5 files set=2804489b9d6b
run 1: pytest-exit: 0
       pytest-summary: 431 passed in 140.77s (0:02:20)
run 2: pytest-exit: 0
       pytest-summary: 431 passed in 152.17s (0:02:32)
```
- The sandbox-only ripwire test ran green in both gates, since ripwire is installed here.
- Round 1 counted 391 for the same five files. tests/test_stack.py grew from 107 tests to 147: 40 new cases, and six changed tests.

### CI rehearsal
- **The environment:**
  - Python 3.12.3 in a scratch uv venv, installed with CI's own line: `pyflakes pytest "jsonschema==4.25.1" "rfc3339-validator==0.1.4" "PyYAML>=6.0"`.
  - PATH is a scratch dir that links /usr/bin's programs except rg and python. It adds `python3` and `python` wrapper scripts that run the venv. The check printed `instruments on PATH: []`.
  - The command ran under `env -i HOME=<scratch> ... RIPWIRE_BIN=/nonexistent-ci/ripwire SENTRUX_BIN=/nonexistent-ci/sentrux`.
```
1 files set=2ac01abb1067
SKIPPED [1] tests/test_stack.py:1464: ripwire is not installed: gate's graph step needs it (CI has none; the missing case is tested with RIPWIRE_BIN pointed away)
SKIPPED [1] tests/test_stack.py:1610: rg (ripgrep) is not installed: the echo stack's code search needs it (CI has none)
pytest-exit: 0
pytest-summary: 145 passed, 2 skipped in 37.83s
```
- **The real stacks in the same environment:** every ripwire and sentrux step reads unmapped, never ok.
```
== review files=scripts/gate_union.py,scripts/lint_files.py -> rc=1
stack review · run s-20260928T192923Z-a78c52 · exit 1 — required, not ok: ripwire
## sentrux · unmapped — sentrux unavailable (not required)
## ripwire · unmapped — ripwire unavailable
## lint · ok · rc 0 · 0.14 s
## ap · ok · rc 0 · 0.10 s
== gate paths=scripts/report_lint.py -> rc=1
stack gate · run s-20260928T192923Z-9f72c8 · exit 1 — required, not ok: graph
## graph · unmapped — ripwire unavailable
== impact sym=build_page -> rc=1
stack impact · run s-20260928T192924Z-f769ef · exit 1 — required, not ok: gitnexus, ripwire
## gitnexus · unmapped — node unavailable
## ripwire · unmapped — ripwire unavailable
```
- **Note (D32):** with its default graph=yes, `gate` exits 1 wherever ripwire is missing, because the `graph` step is required and reads unmapped. Pass graph=no there. Pass it too for a deleted path: ripwire exits 1 on a path it cannot match.

### Mutation (AF-AP-223)
- **How the driver works** (a scratch script, since deleted):
  - It copies the lane's seven files into a scratch dir, with the eight files that the real-tree tests run: lint_delta.py, ap_screen.py, report_lint.py, pc_suite.sh, test_summary.sh, both wrappers and .claude/hooks/edit-snapshot.py. It adds hiccup_families.tsv.
  - It makes the copy a git repository of its own, so tests that run "this tree" run on the copy.
  - hiccup_scan.py and transcript_export.py are symlinked, never copied. My code imports neither.
  - Each mutant is one exact text replacement. Its anchor must match once; all 100 did.
  - Each mutant is py_compiled, then run with PYTHONDONTWRITEBYTECODE=1 on its one test node.
  - A kill counts only on a `FAILED tests/test_stack.py::<node>` line. The unmutated control runs first and must pass.
- **The driver's own negative controls both fired:**
  - The first r1 pass printed `SET=r1 EXPECTED=52 KILLED=51 SURVIVED=1 INVALID=0` (driver rc 1). MH4 survived because round 2's byte pre-filter now skips the user-record decoy before its record type is checked. I fixed the decoy, not the code (D28).
  - The first r2 pass stopped at `the unmutated control is not green: no mutant verdict counts`: the copy lacked hiccup_families.tsv (D29).
- **Final passes, summary lines verbatim:**
```
CONTROL rc=0 40 passed in 13.58s (40 nodes)
PRODUCTION FILES UNCHANGED: True
SET=r1 EXPECTED=52 KILLED=52 SURVIVED=0 INVALID=0
CONTROL rc=0 31 passed in 7.19s (31 nodes)
PRODUCTION FILES UNCHANGED: True
SET=r2 EXPECTED=48 KILLED=48 SURVIVED=0 INVALID=0
```
- **The round-2 mutants and the node each failed.** These are the kill lines of the 19:12Z pass, which ran R1 to R41 against the same nodes. R14c's line is from the final pass, whose KILLED=48 covers them all.
```
KILLED   R1-join-spaces                           FAILED tests/test_stack.py::test_a_join_placeholder_passes_a_list_as_one_comma_joined_element
KILLED   R2-unmapped-if-ignored                   FAILED tests/test_stack.py::test_unmapped_if_turns_a_wrappers_missing_line_into_unmapped[required-out]
KILLED   R3-unmapped-if-stdout-only               FAILED tests/test_stack.py::test_unmapped_if_turns_a_wrappers_missing_line_into_unmapped[required-err]
KILLED   R4-unmapped-body-hidden                  FAILED tests/test_stack.py::test_unmapped_if_turns_a_wrappers_missing_line_into_unmapped[optional-out]
KILLED   R5-tool-name-dropped                     FAILED tests/test_stack.py::test_unmapped_if_turns_a_wrappers_missing_line_into_unmapped[optional-err]
KILLED   R6-union-told-graph-no                   FAILED tests/test_stack.py::test_explain_of_each_wave1_stack_is_pinned[gate]
KILLED   R7-graph-paths-spliced                   FAILED tests/test_stack.py::test_explain_of_each_wave1_stack_is_pinned[gate]
KILLED   R8-union-ignores-ripwire                 FAILED tests/test_stack.py::test_gate_union_unites_gate_files_and_ripwires_rows
KILLED   R9-union-reads-the-comment               FAILED tests/test_stack.py::test_gate_union_unites_gate_files_and_ripwires_rows
KILLED   R10-union-keeps-gone-rows                FAILED tests/test_stack.py::test_gate_union_unites_gate_files_and_ripwires_rows
KILLED   R11a-two-elements-last-wins              FAILED tests/test_stack.py::test_gate_union_refuses_an_ambiguous_ripwire_output[two-elements]
KILLED   R11b-repeated-attribute-last-wins        FAILED tests/test_stack.py::test_gate_union_refuses_an_ambiguous_ripwire_output[repeated-attribute]
KILLED   R12-why-sources-cut                      FAILED tests/test_stack.py::test_gate_union_unites_gate_files_and_ripwires_rows
KILLED   R13-no-answer-silent                     FAILED tests/test_stack.py::test_gate_union_without_an_answer_from_ripwire_says_so
KILLED   R14-capped-silent                        FAILED tests/test_stack.py::test_gate_union_unites_gate_files_and_ripwires_rows
KILLED   R14b-shell-test-in-run-list              FAILED tests/test_stack.py::test_gate_union_unites_gate_files_and_ripwires_rows
KILLED   R14c-any-py-file-in-run-list             FAILED tests/test_stack.py::test_gate_union_unites_gate_files_and_ripwires_rows
KILLED   R15-basetemp-in-run-dir                  FAILED tests/test_stack.py::test_the_gates_run_step_gives_pytest_a_basetemp_outside_every_work_tree[registry]
KILLED   R16-tmp-removed-only-when-ok             FAILED tests/test_stack.py::test_tmp_is_a_private_dir_outside_every_work_tree_removed_after_the_run[failure]
KILLED   R16b-tmp-removal-not-in-finally          FAILED tests/test_stack.py::test_a_signal_to_the_runner_removes_its_tmp - Ass...
KILLED   R17-tmp-made-for-every-run               FAILED tests/test_stack.py::test_the_run_record_holds_every_field_and_each_output_is_saved_whole
KILLED   R18-tmp-git-check-removed                FAILED tests/test_stack.py::test_a_tmp_inside_a_git_work_tree_is_refused - As...
KILLED   R18b-tmp-default-mode                    FAILED tests/test_stack.py::test_tmp_is_a_private_dir_outside_every_work_tree_removed_after_the_run[success]
KILLED   R19-rated-unchecked                      FAILED tests/test_stack.py::test_only_a_rated_stack_takes_ratings - Assertion...
KILLED   R20-no-size-check-while-running          FAILED tests/test_stack.py::test_a_steps_saved_output_is_capped_and_a_truncated_source_feeds_no_chain
KILLED   R21-no-truncation-at-save                FAILED tests/test_stack.py::test_a_steps_saved_output_is_capped_and_a_truncated_source_feeds_no_chain
KILLED   R22-truncated-not-recorded               FAILED tests/test_stack.py::test_a_steps_saved_output_is_capped_and_a_truncated_source_feeds_no_chain
KILLED   R23-truncated-source-feeds-chain         FAILED tests/test_stack.py::test_a_steps_saved_output_is_capped_and_a_truncated_source_feeds_no_chain
KILLED   R24-harvest-lint-required                FAILED tests/test_stack.py::test_harvest_prints_a_failing_lint_and_still_exits_0
KILLED   R25-report-last-long-overall             FAILED tests/test_stack.py::test_handback_extract_saves_the_lanes_longer_text_report
KILLED   R25b-report-first-long                   FAILED tests/test_stack.py::test_handback_extract_saves_the_lanes_longer_text_report
KILLED   R26-thinking-read-as-text                FAILED tests/test_stack.py::test_handback_extract_saves_the_lanes_longer_text_report
KILLED   R27-report-when-not-longer               FAILED tests/test_stack.py::test_handback_extract_writes_a_report_only_when_it_is_longer[shorter]
KILLED   R27b-long-bound-moved                    FAILED tests/test_stack.py::test_handback_extract_writes_a_report_only_when_it_is_longer[1000]
KILLED   R28-lint-target-stays-handback           FAILED tests/test_stack.py::test_handback_extract_saves_the_lanes_longer_text_report
KILLED   R29-lint-reads-a-missing-handback        FAILED tests/test_stack.py::test_harvest_with_no_handback_skips_the_lint - As...
KILLED   R30-absent-path-printed                  FAILED tests/test_stack.py::test_handback_extract_absent_exits_1_and_writes_nothing
KILLED   R31-sentrux-required                     FAILED tests/test_stack.py::test_the_real_ripwire_and_sentrux_steps_read_unmapped_when_their_binaries_are_missing
KILLED   R32-review-ripwire-unmapped-if-deleted   FAILED tests/test_stack.py::test_the_real_ripwire_and_sentrux_steps_read_unmapped_when_their_binaries_are_missing
KILLED   R33-gate-graph-unmapped-if-deleted       FAILED tests/test_stack.py::test_the_real_ripwire_and_sentrux_steps_read_unmapped_when_their_binaries_are_missing
KILLED   R34-impact-ripwire-unmapped-if-deleted   FAILED tests/test_stack.py::test_every_ripwire_and_sentrux_step_reads_unmapped_on_its_wrappers_missing_line
KILLED   R35-lint-files-head-not-subtracted       FAILED tests/test_stack.py::test_lint_files_counts_only_the_hits_a_file_adds
KILLED   R36-lint-files-untracked-vs-itself       FAILED tests/test_stack.py::test_lint_files_counts_only_the_hits_a_file_adds
KILLED   R37-lint-files-exit-0                    FAILED tests/test_stack.py::test_lint_files_counts_only_the_hits_a_file_adds
KILLED   R38-run-dir-branch-removed               FAILED tests/test_stack.py::test_a_chained_line_may_name_a_file_in_this_runs_own_dir
KILLED   R39-run-dir-lexical-only                 FAILED tests/test_stack.py::test_a_chained_step_is_skipped_when_its_source_failed_or_printed_nothing[run-dir-symlink]
KILLED   R40-join-of-a-scalar-allowed             FAILED tests/test_stack.py::test_a_bad_registry_exits_3_before_anything_runs[join-of-a-scalar]
KILLED   R41-harvest-report-out-dropped           FAILED tests/test_stack.py::test_harvest_saves_and_lints_a_lanes_longer_text_report
```
- **The round-1 mutants** (M1 to M21, MG1 to MG8, MH1 to MH4) ran on the round-2 code. Their anchors were updated where the code moved: M7c, M16, MH1, MH2 and MH3. Each failed the node listed in the round-1 section. MH4 failed its node once the decoy was fixed.

### Deviations (loud)
1. **ripwire gets one comma-joined argument through a new `{paths,}` placeholder** (`PH_BODY_RE`, `scripts/stack.py:75`; the join is `values.get(name[:-1], [])`, `scripts/stack.py:633`). The brief wrote `{paths*}`.
   - The wrapper passes one `--test-gate=` flag per argument (`--test-gate="$f"`, `scripts/ripwire_review.sh:64`), and ripwire 0.4.0 keeps only the last flag: measured changed="1", equal to the last file's output alone.
   - `--test-gate=F1,F2` is ripwire's documented multi-file form: measured changed="2".
   - No list element can hold a comma, because every list value is split on commas.
2. **`ok_rc = [0, 4]` on both test-gate steps**: ripwire exits 4 whenever a list is non-empty.
3. **The run list holds the union's pytest test files only** (test_*.py and *_test.py, pytest's default python_files; pyproject.toml sets none). The brief said "the union".
   - A shell test on pytest's command line stops pytest before any test runs: measured, `ERROR: not found`, exit 4.
   - pytest imports any .py file named on its command line, and ripwire links fixture modules (D25).
   - Every file left out is named on stderr and in `sources`.
4. **`review.lint` runs the new scripts/lint_files.py, not lint_delta.py** (item 2).
5. **A new step field, `tool`, beside `unmapped_if`.** It names the instrument in the unmapped status.
6. **handback_extract.py's stdout changed** to one path line, with the status on stderr (item 7b). The report rule is "before the last hand-back call".
7. **`{tmp}` exists only in runs whose selected steps name it**, and it is created in the runner's setup, under its signal handlers.
8. **The save cap also kills a live step** that passes its cap (item 6).
9. **The gate's `clean` step is removed**, and the `union` and `sources` steps are added.
10. **A chained line may name a file in this run's own dir** in its absolute form (`run_dir`, `scripts/stack.py:431`). A symlink out of that dir is refused. harvest's chain needs this whenever the run dir lies outside the tree: with `--log-dir`, or from a worktree.
11. **The rating refusal keys on the rated run's stack** (item 5, flagged).
12. **The real `review` runs used `SENTRUX_RUNTIME_DIR` in scratch**, not the shared baseline (item 2).
13. **Two new helper files:** scripts/gate_union.py (item 1) and scripts/lint_files.py (item 2).
14. **The test transcript's user-record decoy now carries `"role": "assistant"`**, so that the record-type check carries weight again (D28).

### New findings
- **D23. The gate's run list held shell tests (a round-1 defect).**
  - gate_files lists every file under harness-ports/tests/ by design (MG1).
  - `pytest harness-ports/tests/test_pc_lane.sh tests/test_report_lint.py` exited 4 (`ERROR: not found`) and ran no test at all.
  - Fixed by the run-list rule (deviation 3).
- **D24. ripwire's test list is wide on common names.**
  - Measured: seven changed files gave impacted=3032, tests=105 and graph_ambiguous=787.
  - Two sampled linked tests, tests/test_slopo.py and tests/test_vendored_manifest.py, name none of my files (grep count 0 each).
  - Nine of the 20 shown untested rows are `main`.
  - The cause is inferred: name resolution through `main`.
  - The risk: `gate mode=run` with graph=yes on such a change runs about a hundred files. There is no guard; NOT done.
- **D25. ripwire links fixture modules as tests** (tests/fixtures/jev_pipes/*.py: four in my own gate). pytest would import them as tests. The run-list rule leaves them out and names them.
- **D26. For task #345:**
  - (a) The wrapper's one flag per file, deviation 1 (`--test-gate="$f"`, `scripts/ripwire_review.sh:64`).
  - (b) lane_context.sh's test-gate section also passes the files as separate arguments (`"${FILES[@]}"`, `scripts/lane_context.sh:89`), so ctx's pack gates the last file only.
  - (c) lane_context.sh keeps only ripwire's XML rows (`ripwire callers`, `scripts/lane_context.sh:85`, and the test-gate section). A missing binary therefore leaves blank sections, and ctx cannot show unmapped.
  - (d) Both wrappers exit 0 when their binary is missing (`(pinned install)`, `scripts/ripwire_review.sh:36`).
- **D27. sentrux keeps one baseline for all lanes** (`.sentrux-runtime/baseline.json`).
  - Two lanes that save and compare at the same time collide.
  - `compare` with no baseline prints `no baseline` and exits 0 (`no baseline`, `scripts/sentrux_review.sh:37`), and the step reads ok.
- **D28. My own byte pre-filter changed what a test decoy tests.** round 2's extractor skips a line without the bytes `"assistant"` before json.loads. The user-record decoy was skipped there, so the record-type check had nothing to stop, and MH4 survived. Found by the mutation run; fixed in the test.
- **D29. hiccup_scan.py needs scripts/hiccup_families.tsv beside it.** A copy of the tree without it fails with rc 2. This is a harvest dependency, not my file.
- **D30. Side effects of my runs.**
  - My 18:3xZ smoke run of `review mode=check`, earlier in this round, rewrote `.sentrux-runtime/tree` (66 MB, gitignored) and `.sentrux-runtime/last-check.txt`. The shared baseline stayed as it was.
  - The real runs wrote their records under `.jev/stacks/` (gitignored), as designed.
- **D31. `/usr/bin/time` is absent here.** I took wall times from `date +%s.%N` instead. This belongs in env-tool-quirks; not written, as the file is outside my boundary.
- **D32. `gate` exits 1 wherever ripwire is missing** (its `graph` step is required). CI, or a PC without ripwire, must pass graph=no.

### Self-attack: the three likeliest ways this is wrong
1. **`unmapped_if` could turn a real answer into unmapped**, if a real output quoted the wrappers' sentence.
   - Ruled out: the text is the fixed tail of the wrappers' own missing-binary line.
   - In today's five real ripwire outputs it occurs only in the missing-binary run: counts 0, 0, 0 and 0 in the three `graph.out` files and review's `ripwire.out`, and 1 in the impact run with the binary missing.
   - A real ripwire answer is XML over code symbols and paths.
2. **The run-list rule could drop a real test.**
   - Ruled out for pytest files: the rule is pytest's own default python_files, and pyproject.toml sets none (checked).
   - Every file left out is named on stderr and in `sources`, never dropped silently.
   - Residual: a shell test named by a change is not run (NOT done 2). A future python_files setting would make the rule drift, and nothing guards that.
3. **`{tmp}` could leak, or remove the wrong dir.**
   - Ruled out:
     - `os.mkdir` fails when the path exists, so no existing dir is adopted.
     - `made` holds only the dir this run created.
     - `rmtree` does not follow symlinks.
     - The git check fails closed: exit 3, and the dir is removed.
   - Residuals: a SIGKILL leaves the dir (NOT done 5). A signal in the instant between the mkdir and its record in `made` would leave it too; not tested.

### Evidence tiers
- **Verified (measured and pasted):**
  - the gates, the CI rehearsal, the mutation passes and the real runs;
  - ripwire's output format and exit codes;
  - pytest's exit 4 on a shell test;
  - the wrapper's single-flag gap;
  - the line positions in the scrubber-repair transcript.
- **Inferred:**
  - that ripwire's width comes from name resolution through `main` (from the element's counts and rows; ripwire prints no reason per test);
  - that the docstring mutants in NOT done 7 fail their tests.
- **Assumed:** that on real CI, as a non-root user, the wrappers print "missing" without RIPWIRE_BIN or SENTRUX_BIN, and that code-review-graph reads unmapped there.

### Files (untracked; no git write; first 12 hex of sha256; lines)
- scripts/stack.py: 84d738b33112, 1293 lines. Modified.
- scripts/stacks.toml: 0b4eef56349b, 447 lines. Modified.
- scripts/handback_extract.py: 115416a0624b, 145 lines. Modified.
- scripts/gate_files.py: b732d35f2c64, 130 lines. Unchanged since round 1.
- scripts/gate_union.py: ed9de9247b58, 117 lines. **New.**
- scripts/lint_files.py: 546400ab9781, 89 lines. **New.**
- tests/test_stack.py: da6f1fb42b39, 1624 lines. Modified: 147 tests, 40 of them new.
- tasks/briefs/labeling/LS-B9-report.md: unchanged; see the note at the top.

pyflakes exits 0 on the six .py files, and the U+2028/U+2029 count is 0 in all seven files. The last edit was at 19:16:42Z; every gate and both final mutation passes ran after it.

### Records and cleanup
- **Records in `.jev/stacks/`:**
  - s-20260928T191451Z-890292: gate plan over my files, before the final run-list rule.
  - s-20260928T192114Z-7f1a30: gate A.
  - s-20260928T192946Z-fa3e27: review save.
  - s-20260928T192951Z-7e9f5f: review compare.
  - s-20260928T193025Z-d34d91: impact.
  - s-20260928T193032Z-1e48ac: small gate plan.
  - s-20260928T193045Z-207a66: harvest.
  - s-20260928T193218Z-854ab8: final gate plan over my files.
- **Scratch deleted:** ls-b9r2/ (84 MB: the CI venv, the mutation copy and driver, the logs, the scratch sentrux runtime), and the two ripwire samples rw-tg.txt and rw-tg2.txt from earlier in this round.
- **No `/tmp/stack-*` dir is left.** Disk at the end: 12,165 MB free.
- **No git write, no PC bridge, no subagent, no outward action.** I read no secret source. hiccup_scan.py, run by `harvest`, imports only transcript_export's rule scrubber (`scrub`); its value gate, which reads the secret files, runs only in export().

<!-- Coordinator note (2026-09-28): the round-3 section below is the lane's hand-back, extracted verbatim from its transcript by `python3 scripts/stack.py harvest agent=ac753871198ee8cfd` (run s-20260928T213749Z-778fe2; hand-back sha256 620593bc072e; 1065 assistant records, all claude-opus-5-5, 0 refusal stops). The harness refused the lane's own write of this file. -->

## Round 3 (the gate runs every test with its own runner)

LS-B9 round 3: task #339, D-103, D-104. Written 2026-09-28 at 21:3xZ (`date -u` read 21:32:45Z). Brief: `tasks/briefs/labeling/LS-B9-R3-brief.md`, read in full.
- **No new helper.** All changes sit in five of my seven files: stack.py, stacks.toml, gate_union.py, handback_extract.py and test_stack.py. gate_files.py and lint_files.py are unchanged.
- **No git write, no PC bridge, no subagent, no outward action.** I read no secret source and no thinking block.
- **The report file was not written:** the harness refuses a subagent's report-file writes. This hand-back is the whole round-3 section.

### TL;DR
- **F-1 is fixed.** Every union file now runs with its own runner, one process per file, as run-all.sh runs them:
  - pytest for `test_*.py` outside harness-ports/tests/;
  - `python3` for `harness-ports/tests/test_*.py`;
  - `bash` for `harness-ports/tests/test_*.sh`;
  - every other file is named "not run" with its reason.
  - A nonzero exit from any runner fails the run.
- **All three verifier reproductions now come out right:**
  - The `pc_bridge_exec.py` break: `exit 1 — required, not ok: scripts` (round 2: exit 0, `49 passed`).
  - The `lane-done-gate.py` break: `exit 1` (round 2: exit 0, `8 passed`).
  - `omniroute_local_builder.py`: the script's own `24 checks passed`, exit 0 (round 2: pytest rc 3, no tests ran).
- **F-2, F-3, F-7, F-8, F-11 and F-14 are built, each with a test and a killed mutant.** Except the F-14 tests, whose code was already right, every new test fails on round 2's bytes.
- **Gates:**
  - tests/test_stack.py: `177 passed` twice (`1 files set=2ac01abb1067`).
  - The round-1 five files: `461 passed` twice (`5 files set=2804489b9d6b`).
  - run-all.sh: `ALL SUITES PASSED`.
  - Non-root CI rehearsal (uid 1000, Python 3.12, no instrument on the PATH): `175 passed, 2 skipped`.
- **Mutation: 129 of 129 killed** (r1 52, r2 48, r3 29), each set after a green control. r3 holds the verifier's V1, V2, V3, V4, V5, V9 and V12.

### NOT done (read first)
1. **A wide change is not run whole, by design (F-2).** `gate … mode=run` refuses a run list over `max_files` (default 40). On this tree `scripts/stack.py` alone plans 100 files and is refused. Nothing runs until you pass `max_files=100`.
2. **Scripts and shell tests run once per gate; pytest runs `runs` times** (default 2). I read "one run per file" as one process per file, once. Flagged.
3. **The other findings are untouched,** as the brief says: F-4, F-5, F-6, F-9, F-10, F-12, F-13 and F-15 to F-19. The wrappers and lane_context.sh belong to task #345.
4. **Mutants named in docstrings but not driven:**
  - "needs checked before an empty input": not expressible as one text replacement. The order is written and commented in `run_step`.
  - A few mutants are driven on one sibling test node only: the foreach test's refused-line half (M7c holds the shared `chain_input` check), the `[foreach-later-step]` registry case, and the unit `[nothing-names-it]` case.
5. **The report of record has an uncommitted edit in the tree:** the coordinator appended my round-2 section at 19:44Z. I did not touch the file.

### DISCREPANCIES and deviations (loud)
1. **Four new runner features, added in stack.py for item 1.** The brief named no mechanism; these are my design:
  - `foreach = "@<step>"`: one call per stdout line of an earlier step, as `{each}`.
  - `empty_ok`: an empty chained input means nothing to do, listed as not selected, never a failure.
  - `needs`: run only after the named earlier steps ended ok.
  - `headline`: a step's first stdout line goes into the header.
2. **A gate whose pytest list is empty no longer fails for that reason.** Round 2's `setid` was skipped on an empty list, and the gate failed. Now an empty list for one runner means nothing to do. An empty run list across all three runners still fails the gate: `sources` prints NOTHING TO RUN and exits 1.
3. **gate_union.py's notes moved.** Round 2 printed them on stderr in list mode too. Now they print only in `--why` (the `sources` step). The per-runner list steps print file paths only.
4. **The cap kill's exit code changed from -15 to -9 (F-7).** I updated round 2's cap test to match.
5. **Every `gate mode=run` creates `{tmp}`**, even when the pytest step then has nothing to do, because a selected step names it. It is removed after the run.
6. **HEAD moved during the round:** 0d06ae7 (the premise), then 06f9c82, b294c53 and d773575. All are coordinator commits, and none touches my files.
7. **GitNexus rates `kill_groups` HIGH risk:** 5 impacted symbols (execute, run, run_step, cmd_run, main), all in stack.py. The timeout, signal and cap tests cover every caller. `invocations` is HIGH too: one caller, build_plan.
8. **The round-2 hand-back's file:line citations are stale.** `harvest` on this lane's transcript lints them MISS 53. Round 3 grew the files; the lint is advisory, and the harvest exits 0.

### Premise re-run
`bash scripts/premise_block.sh` over the brief's block, run from the main tree with `PYTHONDONTWRITEBYTECODE=1`, diffed against the block:
```
48c48
< no tests collected in 0.04s
---
> no tests collected in 0.03s
```
Only a pytest timing moved. All seven lane-file hashes match (`84d738b331127be0` … `da6f1fb42b393a94`), so there is no CONTRACT-INVALID stop.

### The items

**Item 1. F-1: every file runs with its own runner, or is named "not run" and why.**
- **The classification** is in gate_union.py, `def runner_of` (`scripts/gate_union.py:78`):
  - `test_*.py` directly under harness-ports/tests/: `python3`, as run-all.sh runs them (`python3 "$HERE/$t"`, `harness-ports/tests/run-all.sh:16`).
  - `test_*.sh` there, and run-all.sh itself: `bash`.
  - Any other file under harness-ports/tests/: "not a harness test".
  - `test_*.py` or `*_test.py` anywhere else: pytest.
  - Every other file: "not a test file (pytest collects test_*.py and *_test.py; it would import this one and run nothing)".
  - The other names it uses: `RUNNERS` (`scripts/gate_union.py:50`) and `HARNESS` (`scripts/gate_union.py:51`).
- **The registry.** New list steps `id = "union_py"` (`scripts/stacks.toml:168`) and `id = "union_sh"` (`scripts/stacks.toml:176`) sit beside `union`, the pytest list. Two new run steps use them:
  - `id = "scripts"` (`scripts/stacks.toml:205`), with `foreach = "@union_py"` (`scripts/stacks.toml:209`), runs `python3 <tree>/<file>`.
  - `id = "shells"` (`scripts/stacks.toml:215`), with `foreach = "@union_sh"` (`scripts/stacks.toml:219`), runs `bash <tree>/<file>`.
  - Both use one process per file, as run-all.sh does. They are required, `needs = ["sources"]`, and `empty_ok = true`. Groups 4, 5 and 6 run in order: pytest, then python3, then bash.
- **How the runner makes the per-line calls.** The placeholder `EACH_LINE` (`scripts/stack.py:92`) marks a call whose line is not yet known. `step.foreach_chain` (`scripts/stack.py:815`) expands it at run time, one call per checked line. Each line passes the same path checks as a chained input, in `def chain_input` (`scripts/stack.py:774`).
- **Test (the brief's three faces, plus a shell face):** `test_gate_runs_each_harness_test_with_its_own_runner` (`tests/test_stack.py:1876`). It runs through the real registry in a temporary tree with the gate's real scripts copied in, as the basetemp test does.
  - guarded-script: a script whose check sits under `__main__` fails → the gate exits 1.
  - module-exit: a script ending in `sys.exit(0)` no longer stops the pytest test beside it: `pytest-summary: 1 passed`, exit 0.
  - counting-check: a `check()` that counts a failure and never raises → exit 1, decided by the script's own exit code.
  - shell-test: a failing `.sh` → exit 1.
  - Unit test: `test_gate_union_gives_each_file_its_runner_or_says_why_not` (`tests/test_stack.py:1565`). Plan test on this tree: `test_gate_plan_runs_on_this_tree` (`tests/test_stack.py:1218`).
- **Red first on round 2's bytes.** A scratch repo held round 2's exact lane files (premise hashes) and the round-3 test file:
```
FAILED tests/test_stack.py::test_gate_runs_each_harness_test_with_its_own_runner[counting-check]
FAILED tests/test_stack.py::test_gate_runs_each_harness_test_with_its_own_runner[guarded-script]
FAILED tests/test_stack.py::test_gate_runs_each_harness_test_with_its_own_runner[module-exit]
FAILED tests/test_stack.py::test_gate_runs_each_harness_test_with_its_own_runner[shell-test]
```
- **Mutants killed:**
  - T1 (harness scripts back to pytest): `FAILED …[guarded-script]`.
  - T2 (shell tests not run): `FAILED …[shell-test]`.
  - T3 (the scripts step not required): `FAILED …[counting-check]`.
  - T4 (one call for the first line only) and T5 (`{each}` bound to the first line): `FAILED …test_foreach_over_an_earlier_steps_lines_makes_one_call_per_line`.
  - V12 (every harness-ports/tests/ file out of the run list, which survived every round-2 test): `FAILED …[guarded-script]`.
  - R14c (a fixture module given to pytest): `FAILED …test_gate_union_gives_each_file_its_runner_or_says_why_not`.
- **Real run on this tree:** `gate paths=scripts/pc_bridge_exec.py mode=run runs=1`, graph=yes. Wall 13.5 s, exit 0; `git status` unchanged.
```
sources · run list 3 of union 3: pytest 1 · python3 2 · bash 0 · not run 0
not selected: shells (its input step union_sh printed nothing)
## run · ok · rc 0 · 8.77 s
pytest-summary: 49 passed in 8.43s
## scripts[1/2] · ok · rc 0 · 0.03 s
test_bridge_token_handling: 9 checks passed — ALL OK
## scripts[2/2] · ok · rc 0 · 2.71 s
test_pc_bridge_exec: 8 checks passed
```

**Item 2. F-3: the header carries the counts.**
- **The step:** `sources` (`id = "sources"`, `scripts/stacks.toml:151`) is `headline = true` (`scripts/stacks.toml:157`). gate_union's `--why` now prints `run list %d of union %d: pytest a · python3 b · bash c · not run d` as its first line (`run list %d of union %d`, `scripts/gate_union.py:140`).
- **The runner** copies a headline step's first stdout line into the header (`step.headline`, `scripts/stack.py:1308`), cut at `HEADLINE_MAX` (`scripts/stack.py:93`). The print cap never cuts header lines.
- **Tests:**
  - `test_a_headline_steps_first_line_is_in_the_header_the_print_cap_never_cuts` (`tests/test_stack.py:707`): a 30,000-character headline step and a capped print; the line survives.
  - Every face test also checks the counts line in the header.
- **Mutants killed:**
  - H1 (headline ignored) and H2 (last line taken): `FAILED …test_a_headline_steps_first_line_is_in_the_header_the_print_cap_never_cuts`.
  - H3 (`headline = true` removed from sources): `FAILED …test_gate_runs_each_harness_test_with_its_own_runner[module-exit]`.
- **Real run:** in F-2's refused run below, the print cap cut the `sources` section, including the manifest's not-run row. The header still read `… · not run 5`.

**Item 3. F-2: the width bound and the heavy file.**
- **The bound:** a new parameter `[stacks.gate.params.max_files]` (`scripts/stacks.toml:113`), int, default 40 (`MAX_FILES`, `scripts/gate_union.py:52`).
  - In mode=run, `sources` exits 1 when the run list is wider (`refused = n == 0`, `scripts/gate_union.py:142`). It names the count: `REFUSED: mode=run runs at most max_files=40 files; pass max_files=N to run these N`.
  - The three run steps then skip, because of `needs`. Plan mode says the same thing without refusing.
- **The heavy file:** tests/test_vendored_manifest.py sits in `HEAVY` (`scripts/gate_union.py:53`). It is named "not run: a whole-file run copies about 3.4 GB of vendored trees; run its one relevant test: python3 -m pytest tests/test_vendored_manifest.py -k test_committed_manifest_matches_fresh_generation --basetemp=<a private dir outside every work tree>". The test id exists at line 187 of that file.
- **An empty run list** fails `sources` (NOTHING TO RUN). The run steps then have nothing to do (`runner.idle`, `scripts/stack.py:1310`) and add no further failures.
- **Tests:**
  - `test_gate_union_refuses_a_run_list_wider_than_max_files` (`tests/test_stack.py:1610`): run-over, plan-over, and run exactly at the bound.
  - `test_gate_run_refuses_a_run_list_wider_than_max_files` (`tests/test_stack.py:1901`): through the real registry; `max_files=1` runs nothing, `max_files=2` runs.
  - `test_gate_union_fails_when_nothing_runs` (`tests/test_stack.py:1628`) and `test_gate_with_nothing_to_run_fails_and_runs_nothing` (`tests/test_stack.py:1918`).
- **Mutants killed:**
  - W1 (no bound): `FAILED …[run-over]`. W2 (the bound checked with `>=`): `FAILED …[run-at-bound]`.
  - W3 (the run step without `needs`): `FAILED …test_gate_run_refuses_a_run_list_wider_than_max_files`.
  - W4 (`needs` ignored): `FAILED …test_needs_runs_a_step_only_after_its_prerequisite_ended_ok`.
  - W5 (the manifest file run whole): `FAILED …test_gate_union_gives_each_file_its_runner_or_says_why_not`.
  - W6 (nothing to run exits 0): `FAILED …test_gate_with_nothing_to_run_fails_and_runs_nothing`.
- **Real run on this tree:** `gate paths=scripts/stack.py mode=run`, graph=yes. Wall 1.34 s, exit 1, nothing ran.
```
stack gate · run s-20260928T211130Z-cd0f73 · exit 1 — required, not ok: run, scripts, sources
sources · run list 100 of union 105: pytest 91 · python3 9 · bash 0 · not run 5 · REFUSED: mode=run runs at most max_files=40 files; pass max_files=100 to run these 100
## run[1/2] · SKIPPED — its prerequisite step sources failed (rc 1)
## scripts · SKIPPED — its prerequisite step sources failed (rc 1)
```
  The five not-run rows, from `sources.out`: four `tests/fixtures/jev_pipes/*.py` fixture modules, and `tests/test_vendored_manifest.py  ripwire · not run: a whole-file run copies about 3.4 GB …`.

**Item 4. F-7: a cap breach gets SIGKILL at once.**
- **Where:** `kill_groups([proc], grace=None)` (`grace=None`, `scripts/stack.py:887`). `def kill_groups` (`scripts/stack.py:992`) sends SIGKILL only in that case, with no SIGTERM first. The timeout path keeps SIGTERM and a 3 s grace.
- **Test:** `test_a_step_past_its_save_cap_gets_sigkill_at_once` (`tests/test_stack.py:599`). A writer that notes any SIGTERM and writes on, 25 MB a second, stopped by itself at 40 MB:
  - it ends with rc -9;
  - its SIGTERM marker file is absent;
  - it wrote under 16 MB.
- **Red on round 2's bytes:** `AssertionError: assert ('failed', 0, True) == ('failed', -9, True)`.
- **Mutant killed:** K1 (round 2's grace at the cap): `FAILED …test_a_step_past_its_save_cap_gets_sigkill_at_once`.
- **Real run on this tree** (a scratch registry, `--tree` this tree; the step ignores SIGTERM). Wall 0.23 s.
```
## flood · FAILED · rc -9 · 0.10 s — killed: its saved output passed the 1 MB cap
… saved output truncated at 1 MB (save_cap_mb 1); the rest was not saved
{'status': 'failed', 'rc': -9, 'bytes': 1048652, 'truncated': True, 'secs': 0.102}
```
  The writer's SIGTERM marker, `got_term`, does not exist.

**Item 5. F-8: when a leader exits, its group is killed.**
- **Where:** after the leader exits normally, if its process group is still alive (`_group_alive`, `scripts/stack.py:892`), the runner sends it SIGKILL.
- **What the print and record show:** the result's status line adds `killed what it left running` (`scripts/stack.py:1083`), and the record gets `strays_killed` (`scripts/stack.py:1291`).
- **Test:** `test_a_step_whose_leader_exits_loses_what_it_left_running` (`tests/test_stack.py:622`). The leader exits at once and leaves a child writing; the child is dead after the run.
- **Mutant killed:** S1 (no kill after the leader exits): `FAILED …test_a_step_whose_leader_exits_loses_what_it_left_running`.
- **Real run on this tree** (scratch registry). Wall 0.16 s.
```
## leave · ok · rc 0 · 0.06 s · killed what it left running
child 13029 dead
{'status': 'ok', 'rc': 0, 'bytes': 8192, 'strays_killed': True}
```

**Item 6. F-11: the report search is bounded by the previous call.**
- **Where:** the extractor now resets its search at each well-formed hand-back call (`last_long = None`, `scripts/handback_extract.py:88`). The report is the last long text after the previous call and before the last one. The no-report line now says `in the last round` (`scripts/handback_extract.py:130`).
- **Test:** `test_handback_extract_takes_the_report_only_from_the_last_round` (`tests/test_stack.py:1425`). A round-1 text before the first call is not the report; a long text between the two calls is.
- **Mutant killed:** B1 (the search not bounded): `FAILED …test_handback_extract_takes_the_report_only_from_the_last_round`.
- **Real runs on this tree:**
  - `harvest agent=a88c7c57f2fa2a96b` (wall 0.45 s, exit 0) still finds the scrubber repair's report, which lies between the two calls: `report: saved chars=63540 … (the longer: 63540 characters against the hand-back's 3568)`, then `report_lint: 1 refs — OK 1`.
  - `harvest agent=ac753871198ee8cfd`, this lane (wall 0.38 s, exit 0): `report: none longer than the hand-back (the last long text block: 2643 characters, the hand-back: 43948)`.

**Item 7. F-14: one test for each verifier mutant.**
- **V1, the flock:** `test_the_record_waits_for_the_log_lock` (`tests/test_stack.py:770`). The test holds `<log>/.lock`; the run's step ends and its record waits. V1 (flock removed): `FAILED tests/test_stack.py::test_the_record_waits_for_the_log_lock`.
- **V2, SIGINT and SIGHUP:** the signal test is parametrized over INT, TERM and HUP (`tests/test_stack.py:941`).
  - V2 (handlers for SIGTERM only): `FAILED …[INT]`; V2b, the same mutant: `FAILED …[HUP]`. M17 still fails `[TERM]`.
- **V3, a `\r` in text:** the case `text-cr` in `test_every_type_refuses_a_value_outside_its_shape_before_any_step` (`tests/test_stack.py:973`). V3: `FAILED …[text-cr]`.
- **V4, the timeout bound:** the case `timeout-3601` in `test_a_bad_registry_exits_3_before_anything_runs` (`tests/test_stack.py:887`). V4 (bound 1..999999): `FAILED …[timeout-3601]`.
- **V5, the label regex:** the case `label-uppercase` in the same test. V5 (`.+`): `FAILED …[label-uppercase]`.
- **V9, the cap boundary:** `test_the_print_cap_holds_at_exactly_9000_characters` (`tests/test_stack.py:530`). A print of exactly 9,000 characters goes out whole; one of 9,001 is cut. V9 (checked at 9,100): `FAILED …test_the_print_cap_holds_at_exactly_9000_characters`.
- **Also: the registry checks of the new fields.** `needs-later-step`, `foreach-later-step`, `empty-ok-unchained` and `needs-not-a-list`. Q1: `FAILED …[needs-later-step]`; Q2: `FAILED …[empty-ok-unchained]`.
- **As the verifier said, the code was right in each.** These tests pass on round 2's bytes; the mutants prove them.

### The verifier's reproductions, re-run
They ran in a scratch copy: `git archive HEAD` (b294c53) with my seven files on top, as its own git repository (281 MB). The breaks were made there only and restored after (`git status` 0 lines).
1. **The `pc_bridge_exec.py` break** (non-JSON reply `"rc": 3` → `"rc": 0`, line 53):
  - control: `test_pc_bridge_exec: 8 checks passed`, rc 0;
  - broken, run-all.sh's form: `AssertionError: (0, '')`, rc 1;
  - `gate paths=scripts/pc_bridge_exec.py mode=run runs=1` (graph=yes), wall 16.41 s:
```
stack gate · run s-20260928T210936Z-c36c4e · exit 1 — required, not ok: scripts
sources · run list 3 of union 3: pytest 1 · python3 2 · bash 0 · not run 0
## run · ok · rc 0 · 7.89 s
pytest-summary: 49 passed in 7.50s
## scripts[1/2] · ok · rc 0 · 0.07 s
## scripts[2/2] · FAILED · rc 1 · 2.22 s
AssertionError: (0, '')
```
2. **The `lane-done-gate.py` break** (`passing = counts and exit_code == 0` → `exit_code in (0, 1)`):
  - control: `lane done gate: 19 passed, 0 failed`;
  - broken: `18 passed, 1 failed`, rc 1;
  - `gate paths=harness-ports/bin/lane-done-gate.py mode=run runs=1` (graph=yes), wall 12.91 s:
```
stack gate · run s-20260928T211014Z-e0a097 · exit 1 — required, not ok: scripts
sources · run list 2 of union 2: pytest 0 · python3 1 · bash 1 · not run 0
not selected: setid (its input step union printed nothing), run (its input step union printed nothing)
## scripts[1/1] · FAILED · rc 1 · 3.21 s
lane done gate: 18 passed, 1 failed
## shells[1/1] · ok · rc 0 · 8.12 s
```
3. **`gate paths=harness-ports/bin/omniroute_local_builder.py mode=run graph=no`**, no edit (wall 0.95 s, exit 0):
```
sources · run list 1 of union 1: pytest 0 · python3 1 · bash 0 · not run 0
## scripts[1/1] · ok · rc 0 · 0.17 s
test_omniroute_local_builder: 24 checks passed
```

### Red first on round 2's bytes
- **The setup:** a scratch repo of round 2's exact lane files, with the round-3 test file. The result: `35 failed, 142 passed in 54.64s`.
- **Failing for the missing behavior:**
  - F-1: the four faces;
  - F-2: `test_gate_union_refuses_a_run_list_wider_than_max_files` ×3, `test_gate_run_refuses_a_run_list_wider_than_max_files`, `test_gate_union_fails_when_nothing_runs` ×2, `test_gate_with_nothing_to_run_fails_and_runs_nothing`, `test_gate_union_gives_each_file_its_runner_or_says_why_not`;
  - F-7: `test_a_step_past_its_save_cap_gets_sigkill_at_once` and the cap test (rc -15, not -9);
  - F-8: `test_a_step_whose_leader_exits_loses_what_it_left_running`;
  - F-11: `test_handback_extract_takes_the_report_only_from_the_last_round`;
  - the new runner fields' tests, and the four new registry cases.
- **Failing for other reasons:**
  - My own wording changes: the new registry (list, explain, plan) and the new no-report line.
  - Artifacts of the small copy: the premise, echo and sandbox-ripwire tests need files the copy lacks.

### Gates
Counts are pasted from scripts/test_summary.sh; set ids come from `scripts/pc_suite.sh set-id`. Each gate had a private basetemp outside every work tree.

**Gate A: tests/test_stack.py.** It ran through my own `gate paths=scripts/lint_files.py mode=run graph=no` (run s-20260928T212018Z-77654b, wall 96.68 s, `tmp /tmp/stack-… · removed after the run`):
```
sources · run list 1 of union 1: pytest 1 · python3 0 · bash 0 · not run 0
1 files set=2ac01abb1067
## run[1/2] · ok · rc 0 · 48.56 s
pytest-exit: 0
pytest-summary: 177 passed in 48.26s
## run[2/2] · ok · rc 0 · 47.47 s
pytest-exit: 0
pytest-summary: 177 passed in 47.11s
```

**Gate B: round 1's five files.** tests/test_stack.py, tests/test_no_laya_in_gates.py, tests/test_s0_01_spec_runner.py, tests/test_s0_11_eval_hardening.py and tests/test_search_intercept.py:
```
5 files set=2804489b9d6b
run 1: pytest-exit: 0
       pytest-summary: 461 passed in 154.13s (0:02:34)
run 2: pytest-exit: 0
       pytest-summary: 461 passed in 151.01s (0:02:31)
```

**`bash harness-ports/tests/run-all.sh`**, once, in the main tree: wall 110.29 s, rc 0, `ALL SUITES PASSED`.
- **Every suite:** 7/7, 6/6, 9/9, `19 passed, 0 failed`, 9 checks, 8 checks, 15 checks, 24 checks, 30, 67, 51, 22, 101, 4, 19, 5, 11, 34, and build-roles OK.
- **The tree's `git status` changed during the run.** The coordinator committed d773575 at 21:28:09Z and edited wiki/topics/live-state.md at 21:28:34Z. The run itself wrote nothing into the tree.

### CI rehearsal (non-root, as the brief asks)
- **The environment:**
  - uid 1000 (`ubuntu`) through `setpriv`;
  - Python 3.12.3 in a uv venv, with CI's install line (`pyflakes pytest "jsonschema==4.25.1" "rfc3339-validator==0.1.4" "PyYAML>=6.0"`);
  - a PATH with no rg, graft, node, ripwire, sentrux or code-review-graph;
  - `/root` unreadable (`ripwire under /root visible: False`), so RIPWIRE_BIN and SENTRUX_BIN were NOT set;
  - git trusting the repo through `GIT_CONFIG_*`;
  - run in the scratch archive copy, whose seven lane files were byte-identical to the main tree's (checked).
```
1 files set=2ac01abb1067
SKIPPED [1] tests/test_stack.py:1758: ripwire is not installed: gate's graph step needs it (CI has none; the missing case is tested with RIPWIRE_BIN pointed away)
SKIPPED [1] tests/test_stack.py:2007: rg (ripgrep) is not installed: the echo stack's code search needs it (CI has none)
pytest-exit: 0
pytest-summary: 175 passed, 2 skipped in 52.40s
```
  (report_lint reads the two pasted skip lines as MISS; the verifier found the same false positive in round 2.)
- **The real stacks in the same environment**, from their records:
```
review rc 1 · sentrux=unmapped, ripwire=unmapped, lint=ok, ap=ok
gate rc 1 · tests=ok, why=ok, graph=unmapped, sources=ok, union=ok, union_py=ok, union_sh=ok, setid=ok
impact rc 1 · gitnexus=unmapped, crg_callers=unmapped, crg_tests=unmapped, ripwire=unmapped
gate rc 0 · … run=ok, scripts[1]=ok, scripts[2]=ok     (paths=scripts/pc_bridge_exec.py mode=run runs=1 graph=no)
```
  Each wrapper printed `…/root/.local/bin/<tool> missing — run scripts/setup.sh (pinned install)`.

### Mutation (AF-AP-223)
- **The driver** (scratch, since deleted) is round 2's design.
  - It copies the lane's seven files and the scripts the real-tree tests run, and makes the copy a git repository of its own.
  - hiccup_scan.py and transcript_export.py are symlinked, never copied.
  - Each anchor must match exactly once: 129 of 129 did.
  - Each mutant is py_compiled, then run with `PYTHONDONTWRITEBYTECODE=1` on its one node. A kill counts only on a `FAILED tests/test_stack.py::<node>` line.
  - Round-3 anchor moves in r1 and r2: M5a, M7b, M7d, M17 (now node `[TERM]`), R6, R12, R14b, R14c and R23.
- **Final summary lines, verbatim:**
```
CONTROL rc=0 40 passed in 14.31s (40 nodes)
PRODUCTION FILES UNCHANGED: True
SET=r1 EXPECTED=52 KILLED=52 SURVIVED=0 INVALID=0
CONTROL rc=0 31 passed in 7.51s (31 nodes)
PRODUCTION FILES UNCHANGED: True
SET=r2 EXPECTED=48 KILLED=48 SURVIVED=0 INVALID=0
CONTROL rc=0 26 passed in 10.61s (26 nodes)
PRODUCTION FILES UNCHANGED: True
SET=r3 EXPECTED=29 KILLED=29 SURVIVED=0 INVALID=0
```
- **The r3 kill lines.** These are from the 21:15Z pass, which ran the first 28 mutants against the same nodes. V12's line is from the final pass.
```
KILLED   T1-harness-scripts-to-pytest             FAILED tests/test_stack.py::test_gate_runs_each_harness_test_with_its_own_runner[guarded-script]
KILLED   T2-harness-shell-tests-not-run           FAILED tests/test_stack.py::test_gate_runs_each_harness_test_with_its_own_runner[shell-test]
KILLED   T3-scripts-step-not-required             FAILED tests/test_stack.py::test_gate_runs_each_harness_test_with_its_own_runner[counting-check]
KILLED   T4-one-call-for-the-first-line-only      FAILED tests/test_stack.py::test_foreach_over_an_earlier_steps_lines_makes_one_call_per_line
KILLED   T5-each-bound-to-the-first-line          FAILED tests/test_stack.py::test_foreach_over_an_earlier_steps_lines_makes_one_call_per_line
KILLED   W1-no-width-bound                        FAILED tests/test_stack.py::test_gate_union_refuses_a_run_list_wider_than_max_files[run-over]
KILLED   W2-bound-checked-with-ge                 FAILED tests/test_stack.py::test_gate_union_refuses_a_run_list_wider_than_max_files[run-at-bound]
KILLED   W3-run-step-without-needs                FAILED tests/test_stack.py::test_gate_run_refuses_a_run_list_wider_than_max_files
KILLED   W4-needs-ignored                         FAILED tests/test_stack.py::test_needs_runs_a_step_only_after_its_prerequisite_ended_ok
KILLED   W5-heavy-file-run-whole                  FAILED tests/test_stack.py::test_gate_union_gives_each_file_its_runner_or_says_why_not
KILLED   W6-nothing-to-run-exits-0                FAILED tests/test_stack.py::test_gate_with_nothing_to_run_fails_and_runs_nothing
KILLED   H1-headline-ignored                      FAILED tests/test_stack.py::test_a_headline_steps_first_line_is_in_the_header_the_print_cap_never_cuts
KILLED   H2-headline-last-line                    FAILED tests/test_stack.py::test_a_headline_steps_first_line_is_in_the_header_the_print_cap_never_cuts
KILLED   H3-sources-not-a-headline                FAILED tests/test_stack.py::test_gate_runs_each_harness_test_with_its_own_runner[module-exit]
KILLED   K1-grace-at-the-cap                      FAILED tests/test_stack.py::test_a_step_past_its_save_cap_gets_sigkill_at_once
KILLED   S1-strays-left-running                   FAILED tests/test_stack.py::test_a_step_whose_leader_exits_loses_what_it_left_running
KILLED   B1-report-search-not-bounded             FAILED tests/test_stack.py::test_handback_extract_takes_the_report_only_from_the_last_round
KILLED   E1-empty-ok-ignored                      FAILED tests/test_stack.py::test_an_empty_chained_input_is_nothing_to_do_only_with_empty_ok[empty-ok]
KILLED   E2-empty-is-idle-without-empty-ok        FAILED tests/test_stack.py::test_an_empty_chained_input_is_nothing_to_do_only_with_empty_ok[not-empty-ok]
KILLED   V1-flock-removed                         FAILED tests/test_stack.py::test_the_record_waits_for_the_log_lock - Assertio...
KILLED   V2-handlers-for-sigterm-only             FAILED tests/test_stack.py::test_a_signal_to_the_runner_kills_its_live_steps_and_writes_no_record[INT]
KILLED   V2b-handlers-for-sigterm-only            FAILED tests/test_stack.py::test_a_signal_to_the_runner_kills_its_live_steps_and_writes_no_record[HUP]
KILLED   V3-text-accepts-cr                       FAILED tests/test_stack.py::test_every_type_refuses_a_value_outside_its_shape_before_any_step[text-cr]
KILLED   V4-timeout-bound-widened                 FAILED tests/test_stack.py::test_a_bad_registry_exits_3_before_anything_runs[timeout-3601]
KILLED   V5-label-regex-anything                  FAILED tests/test_stack.py::test_a_bad_registry_exits_3_before_anything_runs[label-uppercase]
KILLED   V9-cap-checked-higher                    FAILED tests/test_stack.py::test_the_print_cap_holds_at_exactly_9000_characters
KILLED   Q1-needs-source-unchecked                FAILED tests/test_stack.py::test_a_bad_registry_exits_3_before_anything_runs[needs-later-step]
KILLED   Q2-empty-ok-unchained-allowed            FAILED tests/test_stack.py::test_a_bad_registry_exits_3_before_anything_runs[empty-ok-unchained]
KILLED   V12-harness-files-out-of-the-run-list    FAILED tests/test_stack.py::test_gate_runs_each_harness_test_with_its_own_runner[guarded-script]
```

### Self-attack: the three likeliest ways this is wrong
1. **A harness test could need run-all.sh's own context:** its cwd, its absolute path, or something run-all.sh sets.
  - Ruled out: run-all.sh does `cd "$ROOT"` and calls each file by its absolute path (`python3 "$HERE/$t"`). The gate runs from the tree root with `python3 <tree>/<file>`, and run-all.sh sets no variable.
  - Measured: all nine .py and all ten .sh files pass under run-all.sh. The real runs on this tree, and both breaks, gave the same results under the gate.
2. **The runner rules could send a file to the wrong runner.**
  - Ruled out by an independent oracle in the tests: `runner_expected`, run-all.sh's mapping restated. The plan test on this tree checks all three lists against it.
  - Every unrunnable file is named, never dropped.
  - Residual: a harness `.py` that is not a `test_*` script, or a `.sh` test outside harness-ports/tests/, is "not run" by design. None exists today.
3. **The at-once kills could hit the wrong processes.**
  - The stray kill fires only after the leader has exited and been reaped. It targets that step's own process group, created by `start_new_session`.
  - The cap kill targets the same group, as the timeout path always has.
  - Residual: a pid reused inside the instant between reap and `killpg` would need a new process that is also a group leader with that id. The same residual exists in round 1's timeout path.

### Evidence tiers
- **Verified (measured and pasted):**
  - the premise;
  - the red run on round 2's bytes;
  - the three reproductions;
  - the real runs on this tree;
  - gates A and B, run-all.sh, and the non-root CI rehearsal;
  - 129 of 129 mutants;
  - the stray child dead after the run;
  - the SIGTERM marker absent after the cap kill.
- **Inferred:** that the docstring mutants in NOT done 4 would fail their tests.
- **Assumed:** nothing new. Round 2's "on CI the wrappers print missing" is now measured as non-root.

### Files (untracked; first 12 hex of sha256; lines)
- scripts/stack.py: a3a249812475, 1381 lines. Modified.
- scripts/stacks.toml: e44d0f5d94d5, 499 lines. Modified.
- scripts/gate_union.py: 40b64972b404, 166 lines. Modified.
- scripts/handback_extract.py: 382646e57335, 151 lines. Modified.
- tests/test_stack.py: 96c44e0a388c, 2021 lines. Modified: 72 test functions.
- scripts/gate_files.py (b732d35f2c64) and scripts/lint_files.py (546400ab9781): unchanged.

pyflakes exits 0 on the six .py files, and the U+2028/U+2029 count is 0 in all seven files. The last edit was at 21:06:23Z; the red run, the mutation, the gates, run-all.sh and the rehearsal all ran after it.

### Records and cleanup
- **Records in `.jev/stacks/`** (gitignored):
  - s-20260928T211109Z-c32b0b: F-1.
  - s-20260928T211130Z-cd0f73: F-2.
  - s-20260928T212018Z-77654b: gate A.
  - s-20260928T211227Z-bc899d and s-20260928T211227Z-553a2c: the two harvests.
- **Scratch deleted:** /tmp/lsb9r3/ (270 MB: the archive copy, the red copy, the driver, the venv, the logs).
- **Ripwire caches:** I removed the two my scratch runs created (`/tmp/ripwire-0/0c`, born 21:08:32Z in the red run; `e5`, born 21:10:15Z in the scratch gate runs). The main tree's `66` and the older dirs stay.
- **Left over:** no `/tmp/stack-*` dir and no round-2 scratch. Disk: 11,533 MB free.
