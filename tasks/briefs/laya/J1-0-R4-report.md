# J1-0-R4 — report (task #172; the ONE focused repair of VERIFY-J1-0-R23-STAMP (B): F-B1, F-B2)

Lane j1-0-r4 · sandbox · agent `code-implementer` (claude-opus-5-5) · shared tree, no worktree · brief
`tasks/briefs/laya/J1-0-R4-brief.md` (AMENDMENT 3, R4-1..R4-6) on AMENDMENT 2 (`tasks/briefs/laya/J1-0-R3-brief.md`).
Report = DATA. Evidence tiers: **verified** (run and pasted here), **inferred**, **assumed**.

**TL;DR — BUILT and gated; NOT landed, and NOT left in the shared tree (D1, D6).**
- [x] R4-1..R4-6 built; every item has a test.
- [x] Tests: `92 passed` twice (the PIN file had 33).
  - RED at the PIN, 88 of the 92 tests: `53 failed, 35 passed`; the 35 = 32 old tests + 3 controls.
  - The last 4 tests were each run red against the screen they guard (§ RED).
- [x] Every F-B1 member trigger, and BH-2 and YH-4, moved from CLEAN to CAUGHT at its exact line.
- [x] Mutants: 25 run, 24 killed. 1 survivor, m24: the verifier's F-B6 m10 class, carried over from R3's code and left to issue #37.
- [x] Bash's own parser vs the scanner: 0 disagreements over 1804 live line positions (the PIN screen: 240).
- [ ] **D1 — BIT FOR REAL: the new screen blocked one coordinator commit.**
  - What happened: the finished screen was in the shared tree 11:05:57Z-11:09:24Z for the final gates. At 11:07:52Z it refused the ledger-plane `safe_commit.sh` (the index's list does not name the hook).
  - What I did: restored the PIN screen, then parked all three final files in the session scratchpad. The tree's boundary files equal the PIN, and both modes read clean.
  - **Landing = ONE command block (§ LANDING).**

## PREMISE — re-measured (2026-09-23 10:02Z, before any edit)

```
$ date -u; git rev-parse --short HEAD; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
Wed Sep 23 10:02:33 UTC 2026
3846636
3846636
$ git log --oneline 792fdbb..origin/claude/soundbox-kit-migration-iz1jwf ; git diff --name-only 792fdbb origin/...
3846636 Wiki live-state 09:4xZ: ...
wiki/topics/live-state.md
$ boundary blobs: <792fdbb blob> <worktree blob> <lines> <path>
18c3939889cf 18c3939889cf 653 scripts/no_laya_in_gates.py
55a9a43af463 55a9a43af463 655 tests/test_no_laya_in_gates.py
0d8edcdc9e92 0d8edcdc9e92 50 scripts/gate_files.txt
$ git diff --quiet 792fdbb -- <the three boundary files>; echo rc
diff-quiet rc=0
$ git diff --cached --stat        # the shared index
(empty: the index equals HEAD; its scripts/gate_files.txt names no edit-snapshot hook)
$ python3 scripts/no_laya_in_gates.py            (x3, bash `time`)
no_laya_in_gates: 39 files scanned, clean   wall=0.289 s / 0.291 s / 0.275 s   rc=0
$ python3 scripts/no_laya_in_gates.py --staged   (x3)
no_laya_in_gates: 39 files scanned, clean   wall=0.759 s / 0.740 s / 0.731 s   rc=0
$ /root/venv-agent-factory/bin/python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/j10r4/bt0
33 passed in 2.38s
$ bash scripts/pc_suite.sh set-id -- tests/test_no_laya_in_gates.py
1 files set=e3695f80792b
```
The premise holds. The boundary files equal the PIN 792fdbb, and the one commit after it changes only the wiki. HEAD
then moved during the lane (bf6d406, acc5a38, 2cd7860). The boundary files stayed at the PIN in every one.

Dynamic-load census: an AST walk over every listed Python gate plus `.claude/hooks/edit-snapshot.py`, at 792fdbb and in the
worktree. Both give the same result, and the hook itself holds no load. The seven syntactic sites are below, as a scratch
script printed them from the final resolver over the live files (`sites: 7`; verified).

| site | loader | resolves to |
|---|---|---|
| scripts/ap_screen.py:26 | `spec_from_file_location` | .claude/hooks/edit-snapshot.py (listed) |
| scripts/lint_delta.py:106 | `spec_from_file_location` | <runtime root>/.claude/hooks/edit-snapshot.py (ALLOWED_DYNAMIC_LOADS x1) |
| scripts/proof-runner:39 | `SourceFileLoader` | <runtime root>/scripts/validate-ledger (ALLOWED_DYNAMIC_LOADS x1) + scripts/validate-ledger (listed) |
| scripts/ledger-gen:17 | `SourceFileLoader` | <runtime root>/scripts/validate-ledger (ALLOWED_DYNAMIC_LOADS x1) + scripts/validate-ledger (listed) |
| proofs/S0-02/check_buzz_authz.py:80 | `spec_from_file_location` | proofs/S0-01/check_acp_conformance.py (listed) + proofs/S0-01/tools/nostr_verify.py (listed) |
| proofs/S0-03/check_omniroute_roundtrip.py:114 | `spec_from_file_location` | proofs/S0-01/check_acp_conformance.py (listed) |
| proofs/S0-05/check_egress.py:122 | `spec_from_file_location` | proofs/S0-01/pins.py (listed) |

- `scripts/ap_screen.py:26` builds its target from `ROOT = Path(__file__).resolve().parents[1]` (`scripts/ap_screen.py:22`).
- `scripts/lint_delta.py:106` loads `hook`, built at `scripts/lint_delta.py:103` from `REPO`; `REPO` is `git rev-parse --show-toplevel` (`scripts/lint_delta.py:35`).
- `proofs/S0-02/check_buzz_authz.py:79-80` is the `_load_by_path` wrapper; its parameter resolves through the wrapper's two direct calls.

## LANDING (for the coordinator; the final files are parked, sha256-verified)

```
SP=/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/j10r4-final
(cd $SP && sha256sum -c SHA256SUMS) \
  && cp $SP/no_laya_in_gates.py scripts/no_laya_in_gates.py && cp $SP/gate_files.txt scripts/gate_files.txt \
  && cp $SP/test_no_laya_in_gates.py tests/test_no_laya_in_gates.py \
  && bash scripts/safe_commit.sh -m "<msg>" scripts/no_laya_in_gates.py scripts/gate_files.txt tests/test_no_laya_in_gates.py tasks/briefs/laya/J1-0-R4-report.md
```
- sha256[:16]: `no_laya_in_gates.py` ab33c767c65c6f56 · `test_no_laya_in_gates.py` 5c6218f1bfab20bd · `gate_files.txt` abb01939f762fb62.
- The three files must enter the index in ONE commit (or the list first). The hook then runs the new screen against an index
  whose list names the hook, and it reads clean (proved: the throwaway-repo gate below).
- Between the `cp` and the commit, any commit of other paths is refused (D1). Keep the block atomic.

## DISCREPANCIES (first-class)

- **D1 — the contract's "live tree clean in both modes" and R4-4 + R4-5 cannot all hold until the new list is in the index.
  It bit a real commit (verified).**
  - Mechanism: the hook runs the WORKTREE screen with `--staged` (`scripts/hooks/pre-commit:127`), and `--staged` reads the
    allowlist from the INDEX (AMENDMENT 2: the index is authoritative). The index carried HEAD's list, which does not name the
    hook. Any correct R4-4 then refuses the two hook loads. I may not `git add`, so I cannot make the index agree.
  - Reproduced after the incident: `python3 <final screen> --staged` on the shared index →
    `gate-file-import-unlisted: scripts/ap_screen.py:26 loads .claude/hooks/edit-snapshot.py` and
    `gate-file-import-unlisted: scripts/lint_delta.py:106 loads .claude/hooks/edit-snapshot.py`, rc=4.
  - Incident timeline (the session transcript, `/root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl`, and `git reflog`):

    | time (Z) | event |
    |---|---|
    | 11:05:57 | I install the three final files for the final gates. All development before this ran in scratch copies. |
    | 11:07:49 | the coordinator runs `safe_commit.sh` on `docs/INCIDENT-LOG.md CLAUDE.md todo/BUILD-TASKLIST.md wiki/topics/live-state.md` |
    | 11:07:52 | its output: the two lines above, then `COMMIT BLOCKED by the never-a-gate screen (rc=4)` |
    | 11:08:39 | the coordinator unstages and reads the hook |
    | 11:09:14 | the coordinator commits from a separate worktree, through a copied hooks directory |
    | 11:09:26 | the coordinator moves the branch with `git update-ref` (reflog: an entry with no message at 2cd7860) |
    | 11:09:24 | I restore the PIN screen (atomic rename) |
    | 11:13:06 | all three boundary files are back at the PIN; the final files are parked (§ LANDING) |

  - Cause, on my side: the dispatch rule was "never leave the screen refusing the live tree longer than a test run". My final
    gates held the new screen in the tree for 3.5 minutes (pytest twice, the hook gate, timings). That was longer than a test run.
- **D2 — `eval` added to R4-4's list (a flagged addition).**
  - R4-4 names `exec`/`compile` of a file's text. `eval(open(p).read())` and `eval("__import__('x')")` load code the same way, so both are refused too.
  - Inline text given to `exec`/`eval`/`compile` counts as part of the gate only while it imports and loads nothing (`_inert`).
    Otherwise the load is refused: a string hides the edge from AMENDMENT 2's import rule.
  - No live gate calls `exec`, `eval` or `compile` as builtins (census).
- **D3 — how the count is checked.** R4-4 says an exception "is checked for how many times it occurs".
  - At runtime the screen refuses MORE than the count: every load that uses the entry is refused.
  - `test_allowed_dynamic_loads_match_the_live_tree_exactly` refuses FEWER on the live tree, so a stale entry cannot wait for a new load.
  - A zero-use entry has no line to name, so it is a test failure, not a runtime line.
- **D4 — refusals that are safe but may be false (fail-closed; no live instance of any of them):**
  - a literal that is not normalized (`./a`, `a/`, `a/../b`) under `.parent`, `with_name` or `dirname`: pathlib and `os.path` disagree there, so the resolver says it cannot tell;
  - `$[ … ]` arithmetic: its `<<` reads as a heredoc, which ends in an R4-1 refusal;
  - a heredoc opened inside backquotes whose body lies outside them;
  - a workflow step with `shell: python`: its `run:` text is scanned as bash.
- **D5 — R4-3 covers more than the brief names.** R4-3 names `.github/workflows/*.yml`. The parser runs for every listed `.yml`/`.yaml` (today: the same two files).
- **D6 — the deliverable is parked, not in the tree.** The tree's three boundary files equal the PIN (see D1). The three final
  files are in the session scratchpad; § LANDING gives the commands and shas. The gates below ran on these exact files
  while they were installed (11:05:57-11:09:24Z), and in scratch copies before that.
- **D7 — the lint root.** `report_lint` ran against a scratch root: `git archive HEAD` plus the three parked files. The tree
  holds the PIN versions, so `--root .` would check this report's line numbers against the wrong screen.

## Per contract line (final-file lines; tests in `tests/test_no_laya_in_gates.py` at the final version)

**R4-1 — a scan never ends open, silently.**
- The code:
  - `_Open` (`scripts/no_laya_in_gates.py:111`) carries the line and what is open. Each construct raises it at the end of its text:
    `def commands` (`scripts/no_laya_in_gates.py:176-295`), `def arith`, `def brace`, `def dq`, `def squote`, `def ansi`,
    `def backtick`, and `def read_bodies` (`scripts/no_laya_in_gates.py:433`) for a pending heredoc.
  - `_command_segments` (`scripts/no_laya_in_gates.py:455`) turns it into `(line, what)`.
  - `_source_errors` (`scripts/no_laya_in_gates.py:499`) prints `gate-file-unparseable: <path>:<line>: <what>` (exit 4). Both modes.
- The texts: `quote " open`, `quote ' open`, `quote $' open`, `heredoc <<EOF pending`, `$( unclosed`, `${ unclosed`, `$(( unclosed`, `` ` unclosed``.
- Tests:
  - `test_scan_ending_inside_a_construct_fails_closed` (8 shapes, `tests/test_no_laya_in_gates.py:791`);
  - `test_scan_ending_inside_a_construct_fails_closed_staged` (`tests/test_no_laya_in_gates.py:799`);
  - `test_workflow_run_ending_inside_a_construct_names_its_yaml_line` (`tests/test_no_laya_in_gates.py:819`).

**R4-2 — the shell scan models bash.**
- `_ShellScan` (`scripts/no_laya_in_gates.py:147`) scans the whole text through one position. It handles:
  - `$( )` nested inside `"…"`: `def dq` → `def dollar` → `commands(")")`;
  - `$'…'` with `\'`: `def ansi` (`scripts/no_laya_in_gates.py:384`);
  - heredoc words by bash's word rules: `def heredoc` (`scripts/no_laya_in_gates.py:414`) + `_unquote` (`scripts/no_laya_in_gates.py:126`);
  - `<<` as a shift in `$(( ))` and `(( ))`: `def arith` (`scripts/no_laya_in_gates.py:332`), which falls back to a subshell for `$( (a) … )`;
  - `${…}` with quotes: `def brace` (`scripts/no_laya_in_gates.py:356`). A bare `{` does not nest, as measured in bash 5.2;
  - `{`/`}` split only as whole words, and `#` starts a comment only at the start of a word: both in `def commands`;
  - `case` patterns inside `$( )`, backquotes, `<( )`, line continuations, and unquoted heredoc bodies (their `$( )` and backquotes run).
- Heredoc bodies and single-quoted text are data.
- Tests:
  - `test_shell_member_trigger_is_caught` (12 shapes, `tests/test_no_laya_in_gates.py:722`);
  - `test_nested_quote_heredoc_text_does_not_blind_the_scan` (the verifier's test 1, `tests/test_no_laya_in_gates.py:753`);
  - `test_heredoc_bodies_are_data_but_their_expansions_run` (`tests/test_no_laya_in_gates.py:765`);
  - `test_real_pc_lane_is_scanned_to_its_end` (BH-2 on the real file, `tests/test_no_laya_in_gates.py:828`);
  - `test_live_tree_clean`.

**R4-3 — workflows are parsed.**
- `_workflow_runs` (`scripts/no_laya_in_gates.py:470`) uses `yaml.compose_all` with `SafeLoader`. It collects every scalar
  `run:` value and follows aliases.
  - A literal block (`|`) maps each value line to its YAML line (`start_mark.line + 2 + k`); any other style maps to the line the value starts on.
  - A parse error gives `gate-file-unparseable: <path>`.
  - A missing PyYAML fails closed and prints its reason.
- Measured interpreters: `python3` has PyYAML 6.0.1 and the hook's `$PY` has 6.0.3.
- Tests:
  - `test_workflow_member_trigger_is_caught` (S39, S40, X3; `tests/test_no_laya_in_gates.py:743`);
  - `test_real_workflow_step_that_sources_is_refused` (YH-3, YH-4 on the real `stage0-ci.yml`, `tests/test_no_laya_in_gates.py:858`);
  - `test_unparseable_workflow_refused` (`tests/test_no_laya_in_gates.py:811`);
  - the existing `test_yaml_parentheses_do_not_split_but_run_sources_are_refused` (`tests/test_no_laya_in_gates.py:494`).

**R4-4 — a dynamic in-process load is an include edge.**
- The code:
  - `_LOADERS` (`scripts/no_laya_in_gates.py:684`): `spec_from_file_location`, `SourceFileLoader`, `run_path`, `import_module`,
    `__import__`, and `exec`/`eval`/`compile` as builtins only (D2).
  - `_Resolver` (`scripts/no_laya_in_gates.py:760`) follows:
    - literals, `Path(__file__)` chains, and pathlib/`os.path` calls. A helper call counts only when the file's imports prove it is pathlib, `os.path`, `io`, `codecs` or a builtin: `def dotted`;
    - module and function bindings. `global`, `nonlocal`, star imports, `for`/`with`/walrus targets and match captures make a name unknown;
    - a parameter, through the arguments of the function's direct calls in the file: `def param_values`, `scripts/no_laya_in_gates.py:905`. A method, lambda, decorated function or escaping function is unknown.
  - `_load_errors` (`scripts/no_laya_in_gates.py:1078`) prints `gate-file-import-unlisted: <path>:<line> loads <target>` or `gate-file-import-unresolved: <path>:<line>`.
  - A module name is closed exactly like a static import, through `_module_candidates` (`scripts/no_laya_in_gates.py:1070`). That helper was extracted from `_import_errors` with no change in behaviour: the 32 old tests stay green.
- The exception set is `ALLOWED_DYNAMIC_LOADS` (`scripts/no_laya_in_gates.py:699`): (gate, the listed target, count).
  - A load matches an entry only as an unknown base joined to exactly that literal target, so an entry cannot be re-pointed (F-B5's class).
  - There are 3 entries: `scripts/lint_delta.py`, `scripts/proof-runner`, `scripts/ledger-gen`, each x1.
- Tests:
  - the verifier's test 4 as `test_dynamic_import_of_an_unlisted_file_is_refused` (`tests/test_no_laya_in_gates.py:873`);
  - listed/unlisted/clean: `test_dynamic_load_is_closed_over_the_list` (`tests/test_no_laya_in_gates.py:891`);
  - unresolvable: `test_dynamic_load_that_cannot_be_resolved_is_refused`;
  - `test_every_loader_kind_is_an_include_edge` (7 kinds, `tests/test_no_laya_in_gates.py:927`);
  - `test_loads_that_bring_no_repo_code_pass`;
  - `test_loader_parameter_is_resolved_at_its_calls` (`tests/test_no_laya_in_gates.py:943`);
  - `test_allowed_dynamic_load_is_bounded_and_keyed_by_target` (`tests/test_no_laya_in_gates.py:967`);
  - ES: `test_edit_snapshot_hook_load_is_an_include_edge`, which copies the real hook and exits 3 on its line (`tests/test_no_laya_in_gates.py:989`);
  - `test_allowed_dynamic_loads_match_the_live_tree_exactly` (`tests/test_no_laya_in_gates.py:1008`);
  - the three first-draft fail-opens: `test_rebinding_a_load_target_is_refused` (`tests/test_no_laya_in_gates.py:1051`), `test_inline_code_that_loads_is_refused` (`tests/test_no_laya_in_gates.py:1070`) and `test_path_modelling_edges_are_refused` (`tests/test_no_laya_in_gates.py:1090`);
  - the lock `test_closed_sets_locked` (`tests/test_no_laya_in_gates.py:652`, `ALLOWED_DYNAMIC_LOADS ==`).

**R4-5 — the hook is listed.** `.claude/hooks/edit-snapshot.py` is on `scripts/gate_files.txt:53`, with its comment on `scripts/gate_files.txt:51-53` (`AMENDMENT 3`).
- Nothing under `.claude/` was modified.
- Tests: the verifier's test 5 as `test_real_tree_lists_the_dynamically_loaded_helper` (`tests/test_no_laya_in_gates.py:885`), and `test_live_tree_clean_staged` (`tests/test_no_laya_in_gates.py:1018`).

**R4-6 — the limits paragraph is corrected** (`scripts/no_laya_in_gates.py:12-36`, which names `ALLOWED_DYNAMIC_LOADS`).
- Dynamic loads are now a followed edge. EXEC edges stay the one declared limit, with the count re-measured (§ R4-6 below).
- The paragraph also lists what is NOT followed.

## Member-trigger table (the PIN screen vs the final screen; each fixture's edge proved by bash itself; verified)

| shape | edge real? | PIN (792fdbb) | final |
|---|---|---|---|
| S12 | bash runs the helper: True | rc=0 CLEAN | rc=4 gate-file-sources: scripts/g.sh:3: scripts/helper.sh |
| S17 | bash runs the helper: True | rc=0 CLEAN | rc=4 gate-file-sources: scripts/g.sh:5: scripts/helper.sh |
| S18 | bash runs the helper: True | rc=0 CLEAN | rc=4 gate-file-sources: scripts/g.sh:5: scripts/helper.sh |
| S24 | bash runs the helper: True | rc=0 CLEAN | rc=4 gate-file-sources: scripts/g.sh:3: scripts/helper.sh |
| S26 | bash runs the helper: True | rc=0 CLEAN | rc=4 gate-file-sources: scripts/g.sh:3: scripts/helper.sh |
| S34 | bash runs the helper: True | rc=0 CLEAN | rc=4 gate-file-sources: scripts/g.sh:2: scripts/helper.sh |
| S35 | bash runs the helper: True | rc=0 CLEAN | rc=4 gate-file-sources: scripts/g.sh:3: scripts/helper.sh |
| S36 | bash runs the helper: True | rc=0 CLEAN | rc=4 gate-file-sources: scripts/g.sh:2: scripts/helper.sh |
| S39 | the step's shell runs the helper: True | rc=0 CLEAN | rc=4 gate-file-sources: .github/workflows/w.yml:6: scripts/helper.sh |
| S40 | the step's shell runs the helper: True | rc=0 CLEAN | rc=4 gate-file-sources: .github/workflows/w.yml:8: scripts/helper.sh |
| X3 | the step's shell runs the helper: True | rc=0 CLEAN | rc=4 gate-file-sources: .github/workflows/w.yml:4: scripts/helper.sh |
| BH-2 | real `scripts/pc_lane.sh` + one line (the throwaway copy's line four hundred one) | rc=0 CLEAN | rc=4 gate-file-sources naming that inserted line: scripts/helper.sh |
| YH-3 | real `stage0-ci.yml`, run: line 48 | rc=4 gate-file-sources: .github/workflows/stage0-ci.yml:48: scripts/helper.sh | the same |
| YH-4 | the same + one apostrophe | rc=0 CLEAN | rc=4 gate-file-sources: .github/workflows/stage0-ci.yml:48: scripts/helper.sh |

## RED at the PIN, GREEN after

- RED: the final test file against the PIN screen and list, in a scratch copy of 792fdbb:
  ```
  $ /root/venv-agent-factory/bin/python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/j10r4/btred/bt2
  53 failed, 35 passed in 6.31s        (before the last 4 tests were added: the 2 modelling-edge tests and 2 member shapes)
  ```
  Each of the 4 later tests was also run red on the screen it guards against:
  - backtick-source: red at the PIN;
  - procsub-source: a control (the PIN caught it);
  - the 2 modelling-edge tests: red on the first-draft screen (`2 failed, 90 deselected`).
- All 53 failures were read (`--tb=line`). Each fails on the screen's result (`assert r.returncode == 4`, the exact error lines,
  or the missing `ALLOWED_DYNAMIC_LOADS`). None fails on a de-vacuous check.
- The 35 = 32 untouched old tests + 3 controls that are green at the PIN by design: YH-3,
  `test_loads_that_bring_no_repo_code_pass` and `test_live_tree_clean_staged`.
- GREEN: see § GATES (`92 passed` twice).

## Independent instrument: bash's parser vs the scanner (verified)

`/tmp/j10r4/oracle.py` inserts one probe line after every line N:
- `fi` for `bash -n`: a syntax error iff bash parses that line as code, including inside `$( )`;
- `. __probe__` for `_source_errors`: reported iff the scanner reads that line as a command.

Positions right after a `\` continuation are skipped: the probe becomes an argument there, and bash's error then comes
from the next line's orphaned `&&`/`|`. All 23 raw mismatches of the first run were of that kind.
```
final screen, every listed non-Python gate file (shell texts + each workflow run: value):  TOTAL probes=1804 mismatches=0 skipped-after-continuation=44
PIN screen, the same shell files:  PIN: scripts/pc_lane.sh probes= 611 mismatches=240 · PIN: TOTAL probes=1762 mismatches=240
adversarial corpus 1 (20 files: nested quotes in $( ), $'…', heredoc words, arithmetic, case in $( ), braces, comments,
  backquotes, <( ), here-strings, continuations, arrays):  TOTAL probes=120 mismatches=0
adversarial corpus 2 (16 files: a heredoc in a same-line $( ), comments in $( ), ')' quoted/escaped, $(<f), 2<<EOF, cat<<EOF,
  <<$X, nested case in $( ), $((cd /; ls) | wc), quoted delimiter words, tab-only <<- ends):  probes=100 mismatches=0
c11 (an extglob case pattern) with `bash -O extglob -n`:  probes=5 mismatches=0
the 36 corpus files unprobed:  0 error lines of any kind (no false gate-file-unparseable)
```

## Adversarial R4-4 shapes (`/tmp/j10r4/evade.py`, one tree per shape; verified)

- 37 shapes, all refused except 3 positive controls.
- Three rounds found SIX real fail-opens in my own first drafts. All are fixed and pinned by committed tests:
  - `global-rebind`: a function's `global T` rebinds the module's `T`. It pulled in the siblings `nonlocal`, a decorated wrapper, a star import, and a shadowed `Path`/`open`/`str`;
  - an inline `exec`/`eval` whose text imports or loads;
  - `relative-parent`: `HERE / Path("a/b").parent` was modelled as the repo's `a`;
  - `annotation`: a load inside an argument annotation, which runs at def time.
```
refused: assigned-alias · keyword-location · starred-args · climb-out · rebound-const · global-rebind · nonlocal-rebind ·
decorated-wrapper · star-import · shadowed-Path · shadowed-open · shadowed-str · fstring-module · relative-dunder ·
exec-compile-open · exec-with-file · run_path-keyword · from-import-run_path · module-alias · builtins-exec · ifexp ·
loop-var · lambda-wrapper · method-wrapper · absolute-literal · missing-file · exec-inline-import · exec-inline-loader ·
eval-inline-dunder · eval-file · exec-inline-const · relative-parent-trick · annotation-load · dotslash-parent (D4)
PASSED(rc=0): ok-exec-inert · ok-listed-ospath · ok-listed-with_name
the first-draft screen (sha 61d965d3d27d40d1) on the last three: relative-parent-trick PASSED · annotation-load PASSED · dotslash-parent PASSED
```

## Mutants (scratch `/tmp/j10r4/mut`; exact-once anchors; each compiled and collected `92 tests collected`; restored by copy)

- Restore verified by sha: screen ab33c767c65c6f56, list abb01939f762fb62.
- m1-m8 are the brief's mutants. m9-m22 defend the new mechanisms.

| id | mutant | result | killed by |
|---|---|---|---|
| m1 | drop R4-1's end-state check | 10 failed, 82 passed | the 8 `test_scan_ending_inside_a_construct_fails_closed` shapes, its `_staged` twin, `test_workflow_run_ending_inside_a_construct_names_its_yaml_line` |
| m2 | no `$( )` inside `"…"` (the nested-quote model) | 7 failed, 85 passed | `test_live_tree_clean`, S35, case-in-cmdsub, backtick-source, `test_nested_quote_heredoc_text_does_not_blind_the_scan`, `test_real_pc_lane_is_scanned_to_its_end`, `test_live_tree_clean_staged` |
| m3 | heredoc delimiter as `[A-Za-z0-9_]` (quotes allowed, the PIN regex) | 2 failed, 90 passed | S17, S18 |
| m4 | `<<` in arithmetic read as a heredoc | 4 failed, 88 passed | `test_live_tree_clean` (the live shift at `harness-ports/bin/pc-lane.sh:471`, `LANE_CAPACITY_BACKOFF`), S26, arith-command, `test_live_tree_clean_staged` |
| m5 | a workflow scanned as one shell text again | 7 failed, 85 passed | `test_yaml_parentheses_do_not_split_but_run_sources_are_refused`, S39, S40, X3, `test_unparseable_workflow_refused`, YH-3, YH-4 |
| m6 | drop R4-4's rule | 24 failed, 68 passed | every R4-4 refusal test: `test_dynamic_import_of_an_unlisted_file_is_refused`, `test_dynamic_load_is_closed_over_the_list`, `test_dynamic_load_that_cannot_be_resolved_is_refused`, the 7 `test_every_loader_kind_is_an_include_edge` kinds, `test_loader_parameter_is_resolved_at_its_calls`, `test_allowed_dynamic_load_is_bounded_and_keyed_by_target`, `test_edit_snapshot_hook_load_is_an_include_edge`, the 5 rebinding shapes, the 4 inline-code shapes, the 2 modelling edges |
| m7a | exception keyed by (file, target) text, no count | 1 failed, 91 passed | `test_allowed_dynamic_load_is_bounded_and_keyed_by_target` |
| m7b | exception keyed by the file alone (any target) | 1 failed, 91 passed | `test_allowed_dynamic_load_is_bounded_and_keyed_by_target` |
| m8 | unlist the edit-snapshot hook | 3 failed, 89 passed | `test_live_tree_clean`, `test_real_tree_lists_the_dynamically_loaded_helper`, `test_live_tree_clean_staged` |
| m9 | `global`/`nonlocal` bind only locally | 2 failed, 90 passed | rebinding[global-rebind], rebinding[nonlocal-rebind] |
| m10 | a name `Path` is pathlib whatever binds it | 1 failed, 91 passed | rebinding[shadowed-Path] |
| m11 | inline exec/eval text always inert | 4 failed, 88 passed | the 4 `test_inline_code_that_loads_is_refused` shapes |
| m12 | no case tracking | 1 failed, 91 passed | case-in-cmdsub |
| m13 | `{`/`}` split everywhere | 1 failed, 91 passed | S34 |
| m14 | `${ }` blind to quotes | 4 failed, 88 passed | `test_live_tree_clean`, S24, `test_real_pc_lane_is_scanned_to_its_end`, `test_live_tree_clean_staged` |
| m15 | `$'…'` read as `'…'` | 2 failed, 90 passed | S12, fails_closed[ansi] |
| m16 | unquoted heredoc bodies never expanded | 1 failed, 91 passed | `test_heredoc_bodies_are_data_but_their_expansions_run` |
| m17 | literal `run:` blocks mapped to the key's line | 1 failed, 91 passed | `test_workflow_run_ending_inside_a_construct_names_its_yaml_line` |
| m18 | parameters never resolved at their calls | 3 failed, 89 passed | `test_live_tree_clean` (the live S0-02 wrapper), `test_loader_parameter_is_resolved_at_its_calls`, `test_live_tree_clean_staged` |
| m19 | backquoted text not scanned | 1 failed, 91 passed | backtick-source |
| m20 | `<( )` text not scanned | 1 failed, 91 passed | procsub-source |
| m21 | annotations not walked | 1 failed, 91 passed | modelling_edges[annotation] |
| m22 | `.parent` makes a relative literal root-anchored (the first draft) | 1 failed, 91 passed | modelling_edges[relative-parent] |
| m23 | no `${ }` handling at all (the verifier's F-B6 m11 class) | 1 failed, 91 passed | fails_closed[param] |
| m24 | `(`/`)` no longer split commands (the verifier's F-B6 m10 class) | 92 passed | **SURVIVED**: `( . x )` then reads as one word, and no test pins the subshell shape. F-B6, issue #37: reported, not fixed |

AF-AP-138: the 58 distinct killing tests of m1-m22, each run by node id on the UNMUTATED final tree (screen
ab33c767c65c6f56): `58 passed in 5.07s`. m23's killer, fails_closed[param], is among them. Survivor: m24 (above).

## GATES (the three final files installed in the shared tree, 11:05:57-11:09:24Z; pasted)

```
$ /root/venv-agent-factory/bin/python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/j10r4/bt1
92 passed in 7.61s
$ ... --basetemp=/tmp/j10r4/bt2
92 passed in 7.43s
$ bash scripts/pc_suite.sh set-id -- tests/test_no_laya_in_gates.py
1 files set=e3695f80792b
$ python3 scripts/no_laya_in_gates.py            (x3)
no_laya_in_gates: 40 files scanned, clean   wall=0.448 s / 0.462 s / 0.421 s   rc=0
$ python3 scripts/no_laya_in_gates.py --staged   (x3; the shared index still held HEAD's list: D1)
gate-file-import-unlisted: scripts/ap_screen.py:26 loads .claude/hooks/edit-snapshot.py
gate-file-import-unlisted: scripts/lint_delta.py:106 loads .claude/hooks/edit-snapshot.py
wall=0.850 s / 0.824 s / 0.768 s   rc=4
$ /root/venv-agent-factory/bin/python -m pyflakes scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py
pyflakes rc=0
$ python3 scripts/ap_screen.py scripts/no_laya_in_gates.py          (PIN baseline: the same 7 at lines 463-479)
--- AP_SCREEN over 1 path(s): 7 hits over 1 files ---   AF-AP-40: 7   (lines 1229-1245, `_glob_structural`, unchanged code: 0 new)
$ python3 scripts/ap_screen.py --tests tests/test_no_laya_in_gates.py
--- TEST_SCREEN over 1 path(s): 0 hits over 1 files ---
```
Timing. The screen runs on every commit.
- Like for like, worktree mode: same inputs, back to back, the PIN screen via `--root . --list`:
  PIN 0.297/0.323/0.299/0.310/0.298 s; final 0.396/0.397/0.394/0.405/0.398 s. **About +0.10 s (+33 %).**
- `--staged`, one index holding the new list (the throwaway repo): final 0.650/0.728/0.640 s; PIN 0.639/0.575/0.558 s. **About +0.08 s.**
- Profiling removed two costs: a second `ast.walk` per Python gate, and a resolver built for every file that uses `re.compile`.

The real pre-commit hook in a THROWAWAY repository. `/tmp/j10r4/hookgate.sh`: `git archive HEAD` (a subset) plus the three
final files, `git init`, `core.hooksPath` = the repo's `scripts/hooks`. Pasted:
```
base: 713eef3 (892 files; hooks not yet active)
identical to the lane's working file: scripts/no_laya_in_gates.py
identical to the lane's working file: scripts/gate_files.txt
=== clean commit
    lint_delta (index vs HEAD): 0 .py changed, 0 NEW pyflakes hit(s), 0 removed
    no_laya_in_gates: 40 files scanned, clean
    commit rc=0; HEAD 713eef3 -> e10484c
=== BH-2
    gate-file-sources: scripts/pc_lane.sh:<the throwaway copy's line four hundred one, the inserted line>: scripts/h.sh
    COMMIT BLOCKED by the never-a-gate screen (rc=4)
    commit rc=1; HEAD 713eef3 -> 713eef3
=== YH-4
    gate-file-sources: .github/workflows/stage0-ci.yml:48: scripts/h.sh
    COMMIT BLOCKED by the never-a-gate screen (rc=4)
    commit rc=1; HEAD 713eef3 -> 713eef3
ES line: 478
=== ES
    laya EDIT-SNAPSHOT RAN in pid 4429
    .claude/hooks/edit-snapshot.py:478:laya
    COMMIT BLOCKED by the never-a-gate screen (rc=3)
    commit rc=1; HEAD 713eef3 -> 713eef3
```
In ES, `lint_delta` ran the planted line in its own process (the pid line). Then the screen, with the hook listed, named that line.

The clean commit runs the new screen with `--staged` against an index whose list names the hook: `40 files scanned, clean`.
That is the state the § LANDING commit produces.

## R4-6 — the exec-edge count re-measured (F-B11), two instruments (verified)

- **Scanner instrument** (`/tmp/j10r4/exec_edges.py`): the commands each gate's own shell runs, taken from the screen's own
  `_command_segments`, over shell texts and workflow `run:` values. A command counts when its command word is an interpreter
  (`bash`, `sh`, `python`, `python3`, `$PY`, `node`) or a path, and it names a TRACKED file once a leading `$VAR/` is removed.
  ```
  literal exec edges: 17; distinct targets: 15; unlisted: 9
  unlisted targets: harness-ports/bin/hermes-session-export.py, harness-ports/bin/sync-lane-skills.sh, harness-ports/bin/sync-skills.sh, harness-ports/tests/run-all.sh, harness-ports/tests/test_context_mirrors.sh, scripts/fubuki_pin_sync.sh, scripts/no_laya_in_gates.py, scripts/pc_bridge_exec.py, scripts/transcript_export.py
  ```
- **Loose text grep** (`grep -noE '(bash|sh|python3?|"\$PY"|\$PY|node)[[:space:]]+"?(\$\{?VAR\}?/)*path'`, each match kept
  when it names a tracked file):
  ```
  grep instrument: 30 edges (text occurrences), 22 distinct targets, 13 unlisted
  unlisted: harness-ports/bin/hermes-session-export.py, harness-ports/bin/qwen-server.sh, harness-ports/bin/sync-lane-skills.sh, harness-ports/bin/sync-skills.sh, harness-ports/tests/run-all.sh, harness-ports/tests/test_context_mirrors.sh, scripts/fubuki_pin_sync.sh, scripts/lane_context.sh, scripts/no_laya_in_gates.py, scripts/pc_bridge_exec.py, scripts/realleg_sync.sh, scripts/ripwire_review.sh, scripts/transcript_export.py
  ```
- The grep's 13 = R3's twelve plus the screen itself. So R3's "26 … 12" was a loose-grep figure on an older tree.
- The four targets only the grep finds occur only in:
  - comments: `scripts/test_summary.sh:13` and `scripts/pc_suite.sh:32` (`realleg_sync.sh`), `harness-ports/bin/pc-lane.sh:195` (`lane_context.sh`), `harness-ports/bin/pc-lane.sh:407` (`qwen-server.sh`);
  - a printf string: `harness-ports/bin/pc-lane.sh:245` (`lane_context.sh`);
  - a command sent to the PC in a `bridge "…"` string: `scripts/pc_lane.sh:313` (`EFF_OUT`, `qwen-server.sh`).
- The docstring states both measurements with their definitions.

## Issue #37 findings this change closes incidentally (the PIN screen vs the final screen, one tree per shape; verified)

```
S09 backslash-newline between source and target  PIN rc=4 gate-file-sources: scripts/g.sh:2: \       NEW rc=4 … scripts/g.sh:2: scripts/h.sh
S10 backslash-newline inside the word            PIN rc=0 clean                                    NEW rc=4 gate-file-sources: scripts/g.sh:2: scripts/h.sh
S04 source <(cat x)                              PIN rc=4 … scripts/g.sh:2: <                      NEW rc=4 … scripts/g.sh:2: <(cat scripts/h.sh)
S02 builtin source / S29 FOO=1 . x / S22 eval / X1 redirection prefix: PIN clean, NEW clean (NOT closed)
```
- **F-B9 (cosmetic targets):** closed. S09 now names `scripts/h.sh`, not `\`; S04 names `<(cat …)`, not `<`.
- **F-B3:** only the S10 member is closed (a line continuation inside the command word). The rest stay open: S02, S03, S08, S20, S22, S28-S33, X1, X2, S4.
- **F-B7 (INFO):** closed. `scripts/pc_lane.sh` lines 386 and 397 are scanned now: the oracle agrees with bash at every one of the file's 611 positions.
- **F-B11 (UNVERIFIED count):** closed by R4-6.
- **F-B6 (test gaps):** partly.
  - Closed: the verifier's m11 class (`${…}` handling) now dies in this code (m23, m14), and so does a `}` inside a word (m13).
  - Still open: the verifier's m10 class survives as m24 (`( . x )`). So do its m3 (`_LEADING_KEYWORD_RE`), m14 (the
    `<<-` tab strip) and m15 (stdlib-first), and the vacuous comment fixture (the PIN file's line 464, unchanged).
    No test for them was added: #37 owns them.
- **Not touched:** F-A2, F-B4, F-B5 (`ALLOWED_SOURCES` is unchanged), F-B8, F-B10, F-C1, F-C2, and the other INFO rows.

## Self-attack — the three most likely ways this change is wrong

1. **The lexer is wrong on a shape the tests never saw, and a silent desync reopens F-B1.**
   - Ruled out on the live tree: 0 mismatches against bash's own parser at 1804 line positions.
   - Ruled out on two adversarial corpora: 0 of 220.
   - Ruled out at the end: any text the scanner cannot finish fails closed (R4-1).
   - Residual: a desync that re-syncs before the end, on a shape outside every corpus. Its known exotic triggers refuse instead (D4).
2. **The resolver accepts a load whose runtime target is unlisted (a fail-open).** Three rounds of evasion shapes found six first-draft holes:
   global, nonlocal, decorator, star import, shadowed helpers, inline exec/eval, relative `.parent`, annotations.
   - Each hole was fixed, pinned by a committed test, and killed by a mutant.
   - Residual, declared in the docstring: `getattr`/`globals()` indirection, a name rebound by exec'd text, loader classes
     outside the list, and a wrapper called from ANOTHER module.
3. **The exception set is broader than the three live loads it covers.**
   - Ruled out:
     - m7a/m7b are killed (the count, and the target key);
     - a re-pointed tail is refused (a test);
     - `test_allowed_dynamic_loads_match_the_live_tree_exactly` pins each entry at exactly x1 on the live files.
   - Residual: each entry trusts that the unknown base is the repo root, by review. The `--root` argument (proof-runner,
     ledger-gen) and `git rev-parse --show-toplevel` (lint_delta) are that base today.

## Side effects outside the boundary, and their cleanup (verified)

- The throwaway repo's `core.hooksPath` pointed at the whole hooks directory, so its clean commit also ran `post-commit`
  (the verifier used a copy of `pre-commit` alone). That started the background reindexers for `/tmp/j10r4/hook`:
  - codebase-memory indexed a project `tmp-j10r4-hook`. I deleted it (`{"project":"tmp-j10r4-hook","status":"deleted"}`). Other lanes' entries (`tmp-vj10-repo`, …) were left alone.
  - graft wrote its index inside the throwaway (deleted with it). It overwrote `/tmp/graft-build.log` and held `/tmp/graft-build.lock` for a few seconds, so a main-repo graft rebuild in that window would have skipped.
  - GitNexus did not register the throwaway (the registry holds only `agent-factory`).
- No git write in the shared repo: no `add`, `commit`, `stash`, `checkout` or `restore`.
- The boundary files were replaced only by atomic `cp` + `mv`, from sha-verified scratch copies and `git show 792fdbb:<path>`.
- `/tmp/j10r4` is removed (verified: `ls` finds nothing). The parked final files stay in the session scratchpad for § LANDING.
- The scratch instruments went with it: `oracle.py`, `evade.py`, `mutants.py`, `hookgate.sh`, `exec_edges.py`. Each was
  written by one heredoc in this lane's Bash calls, so the transcript holds its full text for a verifier to re-run.

## NOT done

- **The change is not landed, and not left in the tree (D1, D6).** § LANDING is one block.
- The seed's AC-5 `verify_command` was not run separately (the same test file ran twice above).
- The PC side was not run (no bridge use in this lane). The hook's `$PY` on the PC is the AF_VENV python (VERIFY-J1-0-R23-STAMP (A) ENV FACTS). Its PyYAML version there is NOT measured. If it is missing, every workflow gate fails closed with a printed reason.
- Not closed (declared, issue #37): F-B3's other spellings, F-B4, F-B5 (`ALLOWED_SOURCES` is still keyed by target text), F-B6's remaining survivors (m24 here, the verifier's m3/m14/m15), F-A2, F-C1, F-C2.
- No bug-echo or registry row: the coordinator's step. Candidates:
  - D1 (a gate whose `--staged` reads the index while the worktree copy of the gate is what runs: a lane that changes the gate and its list together cannot keep a shared tree committable);
  - the six resolver fail-opens (Python's own binding rules re-pointing a statically resolved target).

## report_lint (against a scratch root = `git archive HEAD` + the three parked files; D7)

Run at 11:17:32Z and 11:18:39Z (`date -u`), one fix round of the three allowed. Round 1 read: 72 refs — OK 49, NEAR 2, MISS 6. Its fixes:
- the census became a table carrying each site's loader token;
- a throwaway copy's line number is written in words;
- one token copied from each cited line.
```
$ python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/J1-0-R4-report.md --root /tmp/j10r4/lintroot
report_lint: 70 refs — OK 66, NEAR 0, MISS 0, UNCHECKABLE 4, UNRESOLVED 0 (worktree)
```
`/tmp/j10r4/lintroot` is removed with the rest of the scratch. After § LANDING the same command with `--root .` checks the
report against the committed files.
