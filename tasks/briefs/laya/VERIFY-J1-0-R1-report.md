# VERIFY-J1-0-R1 — targeted re-verify of the ONE focused repair (B1 + B2) on the never-a-gate screen

Lane: VERIFY-J1-0-R1 (sandbox, Opus `adversarial-verifier`). PIN 07ff690 (the J1-0-R1 landing). Tree at the run: origin 3893d72.
Frozen contract: `tasks/briefs/laya/J1-0-brief.md` items 1-6 · `tasks/briefs/laya/VERIFY-J1-0-report.md` §B1 + §B2 + its
production-path cases · `tasks/briefs/laya/J1-0-R1-brief.md` §The repair. The builder's report `tasks/briefs/laya/J1-0-R1-report.md`
was treated as claims to attack, never as evidence. Issue #24's rows are not re-litigated; every NEW observation is graded by the predicate.

**GATE RECOMMENDATION: MERGE-READY-WITH-FOLLOWUPS** — B1 and B2 are closed through a real `git commit` over the real hook; no finding
meets the complete blocking predicate. One **CONTRACT-DEFECT (R3)** is returned for an explicit contract amendment: a listed gate file
replaced by a SYMLINK is screened as its link text and the commit lands "clean". It is pre-existing (the 3bd4fbb screen passes it
too), so it does not hold this repair. Every line below was re-run after the worker restart; nothing here rests on an unreproduced claim.

## 0. Venue, restart, isolation

- The first run was killed by a worker restart before the report landed. The scratch tree `/tmp/vj10r1/` survived; I re-checked it
  (PIN copy, pristine screens and hook copy all sha-identical) and then RE-RAN every item into logs `/tmp/vj10r1/evidence/s1…s7`.
  The pasted lines below come from those post-restart runs. `/tmp/vj10r1` was removed at the end, as the brief requires; the logs,
  the section scripts, the mutator and the fix3 file are kept in the session scratchpad (`vj10r1-evidence/`, ephemeral).
  The pasted lines in this report are the durable record.
- PREMISE re-verified at the PIN: screen `ec9e510e09a47182`, tests `cd374f2a9dfe4674`, allowlist `205ee269eeddc19b`, hook
  `38f65ceed07eacfe`; `git diff --stat 07ff690` over the four files prints nothing; `git log 07ff690..HEAD` over them is empty.
- **SIDE EFFECT, DISCLOSED AND RESTORED.** My first run's fixture step ran `chmod 755 /tmp /tmp/vj10r1` to make the fixture
  path traversable for `nobody`. That stripped the sandbox's `/tmp` from `1777` to `755` from about 18:14Z (the fixture
  mtimes) until 2026-09-22T20:15Z, when I found it at the end of this run and ran `chmod 1777 /tmp`. Verified after: `1777 drwxrwxrwt root /tmp`,
  and `nobody` can create a file in `/tmp` again. In that window a NON-root process could not create files in `/tmp`
  (root was unaffected). Any other lane's non-root failure in that window should be re-checked against this.
- The shared tree was READ-ONLY. Every mutant ran on a `git archive 07ff690` copy or a throwaway repo, restored from a held pristine
  copy with the sha re-checked after each row. The only file this lane writes in the repo is this report.
- The production-path stand-in (`/tmp/vj10r1/repo`, rebuilt fresh after the restart): exactly the 33 listed files + the screen + the
  allowlist (35 tracked files), local `user.*`, `commit.gpgsign=false`, and `core.hooksPath` pointing at a directory holding ONLY a copy
  of the real pre-commit hook (sha `38f65ceed07eacfe`). post-commit was left out on purpose: it starts background graft/GitNexus
  builds. The hook's other gates ran for real: `lint_delta` (a listed file, so present) printed its line on every commit; the
  anchor, manifest, skill, mirror and lane-skill gates no-op because their inputs are absent or unstaged, as in VERIFY-J1-0.
- Instruments: the real script, the real hook, real `git commit`, pytest (venv python), `su nobody`, `scripts/ap_screen.py`,
  `scripts/report_lint.py`, the pack's graft skeleton + GitNexus/crg/ripwire caller rows (`_glob_structural_staged`, `_exists_staged` and `_read_staged`
  each have ONE caller, `main`; `_parse_allowlist` has two, `_load_allowlist` and `main`; crg `tests_for` = 0 for all four — the tests
  reach them only through a subprocess), and a literal sweep for invocations.

## A. Item 1 — the landing gates, reproduced at the PIN (`/tmp/vj10r1/evidence/s1_gates.log`)

| Gate | Result (pasted) |
|---|---|
| suite run 1 | `14 passed in 1.78s`, rc=0 |
| suite run 2 | `14 passed in 0.77s`, rc=0 — the counts agree; the timings are not evidence on a shared box |
| pyflakes | no output, rc=0 |
| live screen, worktree mode (real repo) | `no_laya_in_gates: 33 files scanned, clean`, rc=0 |
| live screen, `--staged` (real repo index) | `no_laya_in_gates: 33 files scanned, clean`, rc=0 — equals the allowlist's 33 entries; 18 structural index entries |
| RED: the 3bd4fbb screen (`5b5f6bbdb82c5a32`) under the PIN tests | `5 failed, 9 passed`, rc=1 — the five names below |
| nine frozen tests of VERIFY-J1-0, by name (`-v`) | all PASSED: `test_live_tree_clean`, `test_planted_violation_in_real_gate_path`, `test_planted_violation_stripped_is_clean`, `test_unlisted_structural_match`, `test_identifier_boundary`, `test_import_check`, `test_no_bypass`, `test_staged_mode`, `test_precommit_wired` |
| seed AC 6 | `WIRED`, rc=0 |
| hook + allowlist bytes | `scripts/hooks/pre-commit` 98a604a=`38f65ceed07eacfe` 07ff690=`38f65ceed07eacfe`; `scripts/gate_files.txt` `205ee269eeddc19b` both |

RED by NAME (the 3bd4fbb screen, the PIN tests), each with the stderr the old screen printed (`s7_redaudit.log`):
- `tests/test_no_laya_in_gates.py:224` `test_staged_renamed_gate_file_is_missing_not_clean` — `assert 0 == 4`, stderr `1 files scanned, clean`
- `tests/test_no_laya_in_gates.py:251` `test_staged_deleted_gate_file_is_missing` — `assert 0 == 4`, same stderr
- `tests/test_no_laya_in_gates.py:272` `test_staged_allowlist_is_read_from_index` — `assert 0 == 3`, same stderr
- `tests/test_no_laya_in_gates.py:298` `test_staged_allowlist_absent_from_index_refused` — `assert 0 == 64`, same stderr
- `tests/test_no_laya_in_gates.py:327` `test_scanned_count_equals_listed_count` — `assert 0 != 0`, same stderr

## B. The production path — real `git commit` over the real hook (`s2_prodpath.log`, `s4_probes.log`, `s4b_fix3.log`)

Base = a fresh stand-in plus one clean commit of a non-gate file (`33 files scanned, clean`, commit rc=0). Each case resets to the base.

| Case | Setup | Screen + hook output | commit rc | HEAD |
|---|---|---|---|---|
| F (B1) | `git mv scripts/report_lint.py scripts/report_lint_v2.py`, `laya` planted in the new name, allowlist unchanged | `gate-file-missing: scripts/report_lint.py` → `COMMIT BLOCKED by the never-a-gate screen (rc=4)` | 1 | unchanged |
| F-deleted-a | `git rm --cached scripts/report_lint.py`, violation on disk | `gate-file-missing: scripts/report_lint.py` → BLOCKED (rc=4) | 1 | unchanged |
| F-deleted-b | `git rm scripts/report_lint.py` | `gate-file-missing: scripts/report_lint.py` → BLOCKED (rc=4) | 1 | unchanged |
| H (B2) | `laya` STAGED into report_lint.py; its allowlist line dropped in the WORKTREE only | the violation line (block 1) → BLOCKED (rc=3) | 1 | unchanged |
| H-staged-twin | the allowlist edit STAGED with the violating file | `no_laya_in_gates: 32 files scanned, clean`; the next unrelated commit also `32 files scanned, clean` | 0 | moved (R4) |
| absent allowlist | `git rm --cached scripts/gate_files.txt` | `gate-file-missing: scripts/gate_files.txt` → BLOCKED (rc=64) | 1 | unchanged |
| m9-a | new unlisted `proofs/S0-99/check_x.py` staged, then deleted from the worktree | `gate-file-unlisted: proofs/S0-99/check_x.py` → BLOCKED (rc=4) | 1 | unchanged |
| m9-b | the same file UNTRACKED in the worktree, never staged; an unrelated commit | `33 files scanned, clean` (worktree mode on the same tree: rc 4) | 0 | moved — F15 closed |
| I | `SKIP_LINT_DELTA SKIP_ANCHOR_CHECK SKIP_MANIFEST_CHECK SKIP_MIRROR_CHECK SKIP_LAYA_GATE_CHECK SKIP_ALL NO_VERIFY` all =1, `laya` staged | the violation line → BLOCKED (rc=3) | 1 | unchanged |
| I, `--no-verify` | the flag, not a variable | hook not run (F16, out of boundary, unchanged) | 0 | moved |
| cwd | the m9-a index, `git commit` run from `scripts/` | `gate-file-unlisted: proofs/S0-99/check_x.py` → BLOCKED (rc=4) | 1 | unchanged |
| positive control | a harmless staged edit to report_lint.py | `33 files scanned, clean` | 0 | moved |
| symlink (R3) | report_lint.py `git mv`'d to `scripts/report_lint_impl.py` + `laya`; `scripts/report_lint.py` re-added as a symlink to it (mode 120000) | `33 files scanned, clean`; git prints `mode change 100755 => 120000` | 0 | **moved — the violation lands** |
| symlink, scratch fix3 | the same state, fix3 screen | `gate-file-not-regular: scripts/report_lint.py` → BLOCKED (rc=4) | 1 | unchanged |
| m9 mutant | m9-a's index, the m9 screen | `33 files scanned, clean` | 0 | moved — m9 lets the unlisted checker land |
| m10 mutant | an unlisted checker staged, the m10 screen | `33 files scanned, clean` | 0 | moved — m10 lets it land |

Block 1 — the violation lines the hook printed (pasted; each alone on its line; the path is the stand-in's copy, line 145 is the planted line):
```
scripts/report_lint.py:145:laya
COMMIT BLOCKED by the never-a-gate screen (rc=3)
```

## C. Mutant table (`s3_mutants.log`; the 14 tests; restore sha `ec9e510e09a47182` after every row)

| Mutant | Mutation | Suite | Killed by |
|---|---|---|---|
| m6 (builder) | staged mode skips the existence control (`if False:` in place of `_exists_staged`) | `2 failed, 12 passed` | `test_staged_renamed_gate_file_is_missing_not_clean`, `test_staged_deleted_gate_file_is_missing` — confirmed |
| m7 (builder) | `if content is None: continue` restored | `14 passed` — SURVIVES | nothing; NOT equivalent — two worktree-mode cases reach the line (R6) |
| m8 (builder) | staged mode reads the WORKTREE allowlist | `2 failed, 12 passed` | `test_staged_allowlist_is_read_from_index`, `test_staged_allowlist_absent_from_index_refused` — confirmed |
| m9 (builder) | staged mode walks the worktree (`_glob_structural(root)`) | `14 passed` — SURVIVES | nothing; NOT equivalent — case m9-a discriminates, and through the real hook the mutant lands the commit (R5) |
| m10 (mine) | `git ls-files` forced to fail (the swallowed error) | `14 passed` — SURVIVES | nothing; through the real hook the unlisted checker lands (R7) |
| m11 (mine) | `main` returns 4 on every path | `12 failed, 2 passed` | survivors: `test_precommit_wired`, `test_scanned_count_equals_listed_count` (R11) |
| m12 (mine) | `main` returns 0 on every path | `12 failed, 2 passed` | survivors: `test_precommit_wired`, `test_planted_violation_stripped_is_clean` |
| m6+m7 (mine) | both controls removed | `3 failed, 11 passed` | adds `test_scanned_count_equals_listed_count` — its only kill is the conjunction |
| fix3 (mine, discriminator) | staged mode refuses a listed index entry whose mode is not 100644/100755 (7 added lines, scratch only) | `14 passed` | — flips the symlink case to rc 4; the live index still reads `33 files scanned, clean` |

m7 worktree-mode reaching cases (`s4_probes.log`, real script, `--root` fixtures, the 000 case as `nobody`):

| Fixture | PIN | m7 |
|---|---|---|
| listed entry is a DIRECTORY | `gate-file-unreadable: scripts/hooks/pre-commit`, rc 4 | `0 files scanned, clean`, rc 0 |
| listed entry mode 000 (as `nobody`) | `gate-file-unreadable: scripts/hooks/pre-commit`, rc 4 | `0 files scanned, clean`, rc 0 |
| positive control, the same file at 644 (as `nobody`) | rc 3 | rc 3 |

## D. Finding inventory (discovery exhaustive inside the repair's scope)

**R1 — INFO (verified). B1 is closed.** SOLID; real path YES. The existence control now runs in both modes:
`scripts/no_laya_in_gates.py:255-262` (`completeness_errors` grows for a missing entry), index-backed through
`scripts/no_laya_in_gates.py:182-188` (`_exists_staged` runs `git cat-file -e`). Cases F, F-deleted-a, F-deleted-b block with rc 4.

**R2 — INFO (verified). B2 is closed.** SOLID; real path YES. In `--staged` the list comes from the index:
`scripts/no_laya_in_gates.py:224-229` (`allowlist_content` from `_read_staged`). Case H blocks with rc 3; the absent-allowlist
shape blocks with rc 64.

**R3 — CONTRACT-DEFECT (returned for amendment; NOT a blocker of this repair). A listed gate file replaced by a symlink passes as clean.**
SOLID; real path YES. Mechanism: the staged read is `git show :<path>` (`scripts/no_laya_in_gates.py:97-106`, `_read_staged`), and
for an index entry of mode 120000 git returns the LINK TEXT. The stand-in commit replaced `scripts/report_lint.py` by a symlink to
an unlisted, non-structural `scripts/report_lint_impl.py` carrying `laya`: the hook printed `33 files scanned, clean` and the
commit LANDED (`mode change 100755 => 120000`). Worktree mode on the identical tree reports the violation (rc 3), because
`scripts/no_laya_in_gates.py:113` (`read_text`) follows the link. The 3bd4fbb screen also passes the state (rc 0), so the defect dates
from 98a604a; the repair neither introduced it nor was asked to close it. Discriminator: the scratch fix3 (refuse index modes
other than 100644/100755 with `gate-file-not-regular`) blocks the commit (rc 4) and keeps `14 passed` and the live
`33 files scanned, clean`. Why CONTRACT-DEFECT and not BLOCKER: frozen item 6 names the mechanism literally
(`tasks/briefs/laya/J1-0-brief.md:15`, `cannot be dodged by an unstaged edit` — this dodge is STAGED), so predicate column 1 fails. Why not a plain FOLLOW-UP: the screen's
own two modes disagree on one tree and the production mode is the wrong one. Its "clean" line is the evidence KC-J1 keys on
(`docs/research/COUNCIL-VERDICT-JEV-LAYA-v1.md:45`, an `absorbing barrier` that fires only when the screen REPORTS vocabulary), so
the false clean silences the kill criterion. Fix shape (for the amendment): fix3, plus a worktree-mode `is_symlink()` refusal. The
same rule covers the gitlink of R16. I did NOT repair it.

**R4 — FOLLOW-UP (contract gap). The staged allowlist twin lands a violation.** SOLID; real path YES. One staged commit that drops
`scripts/report_lint.py` from `scripts/gate_files.txt` AND plants `laya` in it prints `32 files scanned, clean`, commits, and every
later commit screens 32 silently. Conformant: frozen item 1
(`tasks/briefs/laya/J1-0-brief.md:10`, `Scanned set = the explicit committed allowlist`) makes the committed list the scanned set, and item 6 excludes only UNSTAGED dodges. The allowlist is itself
neither listed nor structural, and the 15 non-structural entries have no other backstop (VERIFY-J1-0 §B2 blast radius). Fix shape:
screen `scripts/gate_files.txt` too, or refuse a staged allowlist that drops an entry of HEAD's list unless the same commit removes
that file.

**R5 — FOLLOW-UP. m9 survives the suite but is NOT behaviourally equivalent; the index walk is untested.** SOLID; real path YES.
Case m9-a (staged, absent from the worktree) → PIN rc 4 blocked; the m9 mutant → `33 files scanned, clean` and the commit lands.
The builder's label at `tasks/briefs/laya/J1-0-R1-report.md:59` (`EQUIVALENT-FOR-THE-FROZEN-TESTS`) is literally right, but the
behaviour differs on a two-command case. The walk under test: `scripts/no_laya_in_gates.py:245-248` (`structural_matches` by mode) and
`scripts/no_laya_in_gates.py:162` (`_glob_structural_staged`). Case m9-b turns the builder's code-inspection claim at
`tasks/briefs/laya/J1-0-R1-report.md:105` (`_glob_structural_staged()` closes F15) into a run: an untracked checker no longer blocks
(rc 0, the commit lands), so VERIFY-J1-0's F15 (`tasks/briefs/laya/VERIFY-J1-0-report.md:206`, `UNTRACKED structural file`) is closed.
Fix: add m9-a as a test.

**R6 — FOLLOW-UP (plus a report correction). m7 is NOT equivalent: the unreadable line is reachable in worktree mode, where it
closes F3 and F4.** SOLID; real path NO (worktree mode is not the hook's mode).
`scripts/no_laya_in_gates.py:278-280` (`gate-file-unreadable`, return 4) fires for a listed directory and for a mode-000 file read as `nobody`; m7 turns both into
`0 files scanned, clean`, rc 0 (§C). So VERIFY-J1-0's F3 (`tasks/briefs/laya/VERIFY-J1-0-report.md:109`, `An unreadable listed file`)
and F4 (`tasks/briefs/laya/VERIFY-J1-0-report.md:118`, `listed path that is a directory`) are closed by this repair, unclaimed and
unpinned. The builder's claim is wrong as stated: `tasks/briefs/laya/J1-0-R1-report.md:109` (`m7 SURVIVES` … "structurally unreachable")
and the row at `tasks/briefs/laya/J1-0-R1-report.md:57` (`EQUIVALENT`), repeated in the ledger at `todo/BUILD-TASKLIST.md:159`
(`GATED-PENDING-RE-VERIFY`). In STAGED mode I found no reaching case. Four classes stop at `gate-file-missing` first: a missing index
entry, a missing blob object (`cat-file -e` rc 1), an unmerged entry, a directory entry. That absence is UNSURE by nature (a bounded
hunt). Fix: one worktree-mode test (a listed directory → rc 4 `gate-file-unreadable`), and correct the wording in the report and the ledger.

**R7 — FOLLOW-UP (UNSURE on reachability). A failed index enumeration becomes an empty structural set.** Real path: the forced mutant YES, a natural trigger NO.
`scripts/no_laya_in_gates.py:177-178` (`except subprocess.CalledProcessError:` then `pass`) turns a `git ls-files` failure into "no
structural files". That is the fail-open-by-omission class of AF-AP-40 (`docs/INCIDENT-LOG.md:337`, `presence-gated check`), a new
instance the repair itself added. m10 forces the failure: the suite stays `14 passed` and the real hook lands an unlisted checker. I
found NO reachable trigger at the PIN. Hunted: a worktree `proofs` symlink (`ls-files` rc 0, walk intact); a missing `GIT_INDEX_FILE`
and a cwd outside any repo (both stop at the allowlist read, rc 64); the pathspecs are literals. Fix shape: a named exit 4, like the
unreadable branch — a failed walk prints `gate-file-walk-failed: <git stderr>` and returns 4; add a test that forces the failure.

**R8 — FOLLOW-UP. The staged walk depends on the cwd; the hook's cwd makes it correct.** SOLID; real path NO. Git pathspecs are
cwd-relative, while `:<path>` object names are root-relative. From `scripts/` the three pathspecs enumerate 0 entries (19 from the
top), and a by-hand `--staged` run from there passes an unlisted staged checker (rc 0). In production git runs pre-commit at the
work-tree top: a real `git commit` from `scripts/` was BLOCKED rc 4 (the cwd row of §B). `man githooks` is not installed here, so the
primary source is that measurement on git 2.43.0. The root flag does not help in staged mode:
`scripts/no_laya_in_gates.py:212-215` (`Path.cwd()` default) sets `root`, which the staged branches never read. Fix: `:(top)` pathspec magic, or run git with `cwd=` the
`git rev-parse --show-toplevel` result.

**R9 — INFO. Mode discrepancy: git's `*` crosses `/`.** SOLID; real path NO (the script on the stand-in index). With `scripts/hooks/sub/x.sh` and
`proofs/S0-98/nested/check_y.py` staged, `--staged` exits 4 on both paths, while worktree mode stays clean. The worktree walk is one
level deep (`scripts/no_laya_in_gates.py:156`, `sub.glob("check_*.py")`). The production mode errs STRICT (fail-closed). No nested
path exists today (18 structural index entries, all one level).

**R10 — FOLLOW-UP. `core.quotePath` makes a non-ASCII structural path unlistable.** SOLID; real path: the script on the stand-in index.
`git ls-files` C-quotes the name, so `gate-file-unlisted: "proofs/S0-\303\251/check_x.py"` rc 4 appears even when the path IS
listed. With `core.quotePath=false` injected (`GIT_CONFIG_COUNT`) the same index reads `34 files scanned, clean`, rc 0. Fail-closed;
the live allowlist has 0 non-ASCII entries. Fix: `git -c core.quotePath=false ls-files`, or `-z`.

**R11 — FOLLOW-UP (the closest call). `test_scanned_count_equals_listed_count` never reads the count.** SOLID; real path NO.
`tests/test_no_laya_in_gates.py:327` (`test_scanned_count_equals_listed_count`) asserts only
`returncode != 0` (`tests/test_no_laya_in_gates.py:343`). It survives m11 (a screen that exits 4 on every path) and each of m6 and m7 alone; only
m6+m7 kills it. The repair spec names it "the success line's N == the list's length" (`tasks/briefs/laya/J1-0-R1-brief.md:14`,
`test_scanned_count_equals_listed_count`). The production invariant itself holds by construction, not by the test: past the
controls every entry either counts (`scripts/no_laya_in_gates.py:281`, `scanned += 1`) or returns 4
(`scripts/no_laya_in_gates.py:278-280`, `gate-file-unreadable`), and the success line prints the count
(`scripts/no_laya_in_gates.py:291`, `files scanned, clean`). Measured: 33 == 33 on the live index. A duplicate list line counts
twice (34 printed for 33 distinct files), so N is entries, not distinct files. Fix: in a well-formed staged repo, assert rc 0 and the
exact `2 files scanned, clean`.

**R12 — INFO. The suite is not a mirror; the positive staged control is a FROZEN test.** SOLID; real path n/a (the suite). The five new tests assert failure
codes only. The positive staged path — index clean, worktree dirty → rc 0 — is pinned by
`tests/test_no_laya_in_gates.py:136` (`test_staged_mode`), which m11 kills. m11 and m12 each kill 12 of 14.

**R13 — FOLLOW-UP. `_init_repo` inherits the global git config (a hidden input).** SOLID; real path n/a (the suite). `tests/test_no_laya_in_gates.py:202`
(`_init_repo`) commits with `check=True`. It neutralises the sandbox's global `commit.gpgsign=true` with
`tests/test_no_laya_in_gates.py:214` (`--no-gpg-sign`) and sets identity through
`tests/test_no_laya_in_gates.py:192` (`_git_env`), but it does not neutralise `core.hooksPath`. Under `GIT_CONFIG_GLOBAL` with a blocking hooksPath, six tests fail (all
five new ones and the frozen `test_staged_mode`; `6 failed, 8 passed`). Today hooksPath is repo-local (`scripts/hooks`), so the
suite is green. Fix: `git -c core.hooksPath=/dev/null` on the init and commit calls.

**R14 — FOLLOW-UP (a doc the diff falsified).** SOLID; real path n/a (a docstring). The module docstring still reads
`scripts/no_laya_in_gates.py:7` (`gate-file-unlisted or gate-file-missing`) for exit 4. The repair added a third exit-4 message at
`scripts/no_laya_in_gates.py:279` (`gate-file-unreadable`). Fix: one line in the same file.

**R15 — INFO. The new staged rc-64 line reuses the exit-4 prefix.** SOLID; real path YES (the absent-allowlist commit).
`scripts/no_laya_in_gates.py:227` prints `gate-file-missing` for the absent allowlist and returns 64. That is VERIFY-J1-0's F12
(`tasks/briefs/laya/VERIFY-J1-0-report.md:188`, `exit-4 message prefix`), extended to the new staged branch.

**R16 — INFO. A listed gitlink is counted as scanned.** SOLID; real path NO (the script on the stand-in index). A 160000 entry whose commit exists passes `cat-file -e`, and
`git show :subrepo` prints the commit, which is then screened (34 printed, rc 0). Contrived; R3's fix shape covers it.

**R17 — INFO. Strict decoding of staged content (pre-existing; one new site).** SOLID; real path NO (the script; the hook would block on rc 1). `_read_staged`
(`scripts/no_laya_in_gates.py:101`, `["git", "show", ":%s" % path]` with `text=True`) raises an uncaught `UnicodeDecodeError` on
invalid UTF-8 → rc 1 traceback. Fail-closed: the hook blocks. Worktree mode reads the same bytes with `errors="replace"` and reports
rc 3. The repair's allowlist read has the same exposure (rc 1). The live staged run crashes (rc 1) only with `LC_ALL=C` and both
PEP 538 coercion and UTF-8 mode switched off; plain `LC_ALL=C` is coerced and clean. Fix: `errors="replace"`, or read bytes.

**R18 — INFO. Flag combinations are coherent and unreachable from production.** SOLID; real path NO (unreachable by construction). The hook passes only `--staged`:
`scripts/hooks/pre-commit:113` (`--staged`). `--staged --list <file>` scans the on-disk list against the index walk (18 unlisted
lines, rc 4). `--staged --root <tree>` ignores the root and reads the cwd's index (rc 3 on the stand-in's staged violation). This
supersedes VERIFY-J1-0's F21 (`tasks/briefs/laya/VERIFY-J1-0-report.md:264`, `reads the wrong index`): staged mode now reads one
index for all three inputs.

**R19 — INFO. Case I holds after the repair; `--no-verify` still bypasses.** SOLID; real path YES. Every `SKIP_*` variable and
`NO_VERIFY` set → still `COMMIT BLOCKED by the never-a-gate screen` (`scripts/hooks/pre-commit:116`). The flag `--no-verify`
lands the commit: VERIFY-J1-0's F16 (`tasks/briefs/laya/VERIFY-J1-0-report.md:213`, `--no-verify`), out of this boundary.

**R20 — INFO. An unmerged gate file reads as missing, but git refuses first.** SOLID; real path YES (git refused before the hook). During a conflicted merge the screen prints
`gate-file-missing: scripts/report_lint.py` (rc 4). `git commit` stops with `fatal: Exiting because of an unresolved conflict.`
(rc 128) before any hook runs. No production effect.

**R21 — INFO + bug-echo action. The AP screen does not see the repair's new AF-AP-40 site.** SOLID; real path n/a (a screen run).
`python3 scripts/ap_screen.py scripts/no_laya_in_gates.py` returns the same seven known-noisy guards as 3bd4fbb
(`scripts/no_laya_in_gates.py:141-157`, `is_dir()` / `is_file()`, issue #24 row 10). It misses R7's genuine site at
`scripts/no_laya_in_gates.py:177` (`CalledProcessError`). The builder declined the signature as out of boundary
(`tasks/briefs/laya/J1-0-R1-report.md:117`, `AP_SCREEN`). VERIFY-J1-0's F17 action
(`tasks/briefs/laya/VERIFY-J1-0-report.md:224`, `missed the real one`) is still open, now with two shapes: `except …: pass` around an enumeration, and a `continue` in a scan loop.

**R22 — INFO. The boundary is respected; one production consumer.** SOLID; real path n/a (git and a literal sweep). The production delta is confined to
`scripts/no_laya_in_gates.py`; the hook and the allowlist are byte-identical to 98a604a. The landing commit also carries the report
and one ledger line (coordinator plane). A literal sweep of `scripts/ .github/ harness-ports/ proofs/ tests/` finds one invocation,
`scripts/hooks/pre-commit:113` (`no_laya_in_gates.py`). No CI step runs the screen, and no other test touches it.

**R23 — INFO. Evidence audit of the builder's report: it reproduces, with four exceptions.** SOLID; real path n/a (an audit). Reproduced: the hunk
inventory against `git diff 3bd4fbb 07ff690`, every hunk line, both shas, RED `5 failed, 9 passed` with the five names and the
stderr of each row, GREEN twice, m6 and m8 with their named kills, the live count 33 in both modes, the AP screen line, and the
`_read_staged` callers (`tasks/briefs/laya/J1-0-R1-report.md:36`, `_read_staged`). The exceptions:
(1) the PIN line counts are each one high — `tasks/briefs/laya/J1-0-R1-report.md:9` (`248 -> 296`) and
`tasks/briefs/laya/J1-0-R1-report.md:10` (`188 -> 346`) against `wc -l` 247 and 187; the ledger repeats both;
(2) m7 (R6); (3) the brief demanded a pasted lint line (`tasks/briefs/laya/J1-0-R1-brief.md:21`, `report_lint --min-refs 10`) and the
report has none — I ran it: `19 refs — OK 19, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0`; (4) code intel was grep, not `graft ask`.

Counts: 23 observations — **22 SOLID, 1 UNSURE (R7's reachability)**. Classes: 1 CONTRACT-DEFECT, 9 FOLLOW-UP (R4 R5 R6 R7 R8 R10
R11 R13 R14), 13 INFO. BLOCKER: none.

## E. Item 8 — test realism and mirror check (summary of R11-R13)

- Hidden inputs: identity is set per test and gpg signing is disabled per commit; `core.hooksPath` is not neutralised (R13).
- Mirror: a blanket `exit 4` keeps 2 tests green, one of them the count test (R11). A blanket `exit 0` keeps 2 green.
- Assertions are on exit codes and stderr names, never on prose, except the count test, which asserts nothing about the count.

## F. The blocking predicate, applied per finding

| # | 1 contract-mapped | 2 canonical repro | 3 material | 4 discriminator | 5 in boundary | Disposition |
|---|---|---|---|---|---|---|
| R3 | no — item 6's mechanism implemented literally | yes — the real commit lands | yes — a false clean on KC-J1's evidence | yes — fix3: rc 4, 14/14 | the fix yes; the rule is new | **CONTRACT-DEFECT** — returned for amendment |
| R4 | no — item 1 makes the committed list the set | yes | yes | yes | yes | FOLLOW-UP (contract gap) |
| R5 | no — no frozen test pins the walk | yes (m9 lands a commit) | test strength only | yes — m9-a | yes | FOLLOW-UP |
| R6 | no — worktree mode is not the production mode | no | test strength + a wrong claim | yes — 2 fixtures | yes | FOLLOW-UP |
| R7 | partial — AF-AP-40's class | **no** — no reachable trigger found | yes (forced) | m10 only | yes | FOLLOW-UP |
| R8 | no | **no** — the hook runs at the top | none in production | yes | yes | FOLLOW-UP |
| R10 | no | script on the stand-in only | fail-closed | yes | yes | FOLLOW-UP |
| R11 | **yes** — the repair spec names the assertion | **no** — the production invariant holds | test strength only | yes — m11 | yes | FOLLOW-UP |
| R13 | no | no — the environment only | test fragility | yes | yes | FOLLOW-UP |
| R14 | no | n/a | none — documentation | yes | yes | FOLLOW-UP |
| R1 R2 R9 R12 R15-R23 | — | — | none, or verified-working | — | — | INFO |

**GATE RECOMMENDATION: MERGE-READY-WITH-FOLLOWUPS.** Blocking findings: none. B1 and B2 are closed through the real hook with both
discriminators (rc 4 on case F and its deleted forms; rc 3 on case H). The nine frozen tests stay green by name. **R3 is a
CONTRACT-DEFECT returned to the coordinator**: a symlinked gate file commits under "clean", pre-existing since 98a604a. The frozen
text needs an amendment (refuse non-regular index modes) before KC-J1's evidence can be trusted against that shape; it is not a
reason to keep this builder in a repair loop. The follow-ups R4-R8, R10, R11, R13 and R14 belong in issue #24 or a new row. Every
claim here was reproduced after the restart; the recommendation depends on nothing unreproduced.

## G. Deliberately not done

- No repair of anything (R3 included), no commit, no push, no bridge call, no outward action. No file written in the tree but this
  report. Never touched: `src/agent_factory/decisions/`, `scripts/laya_probe.py`, `tests/test_laya_probe_report.py`,
  `tests/fixtures/decisions/probe/`. Commit b67a813 now tracks the J0-a files; they are outside the scanned set and the patterns.
- No recursive check of pytest, `scripts/ap_screen.py`, `scripts/report_lint.py` or the hook's other gates: none changed in this
  repair, and no readiness claim depends on them.
- No wider suite: the literal sweep shows the screen has one consumer (the hook) and one test file.
- No timing claims: the box is shared; the timings printed by pytest are copied only as part of the pasted count lines.

## H. Item 9 — lint and screen, pasted (`s6_lint.log`)

```
$ python3 scripts/report_lint.py --min-refs 10 tasks/briefs/laya/J1-0-R1-report.md
report_lint: 19 refs — OK 19, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
$ python3 scripts/ap_screen.py --tests scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py
--- TEST_SCREEN over 2 path(s): 0 hits over 2 files ---
$ python3 scripts/ap_screen.py scripts/no_laya_in_gates.py
--- AP_SCREEN over 1 path(s): 7 hits over 1 files ---
AF-AP-40: 7
```

This report, final lint (three rounds: round 1 found six MISS rows from line-wrapped references; no reference number was changed):
```
$ python3 scripts/report_lint.py --min-refs 12 tasks/briefs/laya/VERIFY-J1-0-R1-report.md
report_lint: 57 refs — OK 56, NEAR 0, MISS 0, UNCHECKABLE 1, UNRESOLVED 0 (worktree)
```
The one UNCHECKABLE row is Block 1's verbatim hook paste.
