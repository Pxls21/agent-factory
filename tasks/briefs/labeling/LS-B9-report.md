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
