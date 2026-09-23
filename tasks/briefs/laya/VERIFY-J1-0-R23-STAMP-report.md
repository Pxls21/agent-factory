# VERIFY-J1-0-R23-STAMP — independent adversarial verify (J1-0-R2 · J1-0-R3 · stamp gate)

**Sandbox continuation — lane verify-j1-0-r23-stamp-s (task #140), agent `adversarial-verifier` (claude-opus-5-5), shared
tree, no worktree.** Brief `tasks/briefs/laya/VERIFY-J1-0-R23-STAMP-S-brief.md`; contract `tasks/briefs/pc/pc-verify-j1-0-r23-stamp.md`
under the brief's venue map. The PC lane died on route capacity after part (A); its draft (sha256 856dd688…, 130 lines)
is part (A) below, re-checked here. Report = finding inventory (no severity filter) + ONE gate recommendation per
component. The coordinator owns the gate.

**TL;DR** — (A) J1-0-R2 **MERGE-READY-WITH-FOLLOWUPS** · (B) J1-0-R3 **NOT-READY** (blockers F-B1, F-B2) · (C) future-stamp
gate **MERGE-READY-WITH-FOLLOWUPS** · mutants: 24 run, 17 killed, 7 survived (each proven non-equivalent by a live
differential) · 5 proposed regression tests, each run red at the PIN (scratch only, not committed: my boundary is this file).

- [x] (A) A1 re-run + A2 rows a, b2, c reproduced through the real hook → (A) stands as drafted (two INFO added, F-A2 sharpened)
- [ ] (B) the include-edge scan is blind to 318 of 610 lines of the real `scripts/pc_lane.sh` (F-B1) and misses a live unlisted
      in-process import that the pre-commit hook itself executes (F-B2) — both reproduced through the real hook
- [x] (C) C1-C5 reproduced; no finding meets the predicate; merge/cherry-pick and symlink paths are follow-ups
- [x] D1 — 0 new anti-pattern hits

### Identity and venue (measured, pasted)
- Clock: lane start `Wed Sep 23 08:55:24 UTC 2026`; last identity check `Wed Sep 23 09:27:21 UTC 2026`.
- Boundary blobs (`git rev-parse <rev>:<path>`, 12 chars): equal at 5a00d13 (the PC PIN), c269263 (this PIN), 2ebd486
  (origin at start), c69c07b (HEAD at 09:27Z) and in the worktree. Origin moved to 1978e55; `git diff --stat 2ebd486
  origin -- <boundary + cited code>` is empty.

  | blob | path |
  |---|---|
  | 18c3939889cf | scripts/no_laya_in_gates.py (sha256[:16] a8a1e114d32c1528, 653 lines) |
  | 55a9a43af463 | tests/test_no_laya_in_gates.py |
  | b7b48b8da487 | scripts/gate_files.txt |
  | 7731a91c7d3e | scripts/hooks/pre-commit |
  | 6173ca76b508 | scripts/stamp_check.py |
  | fa2a374363d4 | tests/test_stamp_check.py |
  | 56f4863ca1a8 | tests/test_shell_syntax.py |
  | 1f16b01f1923 / eb20dde7e198 / a6691647faa5 / 6d6024139163 | scripts/lint_delta.py / scripts/ap_screen.py / .claude/hooks/edit-snapshot.py / scripts/pc_lane.sh (cited, unchanged) |

- Every throwaway repo or tree lives under `/tmp/vj10/` and was built by `git archive 2ebd486`, never copied from the
  shared worktree. Four LISTED gate files differ there from the PIN: `.github/workflows/stage0-ci.yml` and
  `scripts/push_clean.sh` (CI-GATE-R1, committed after the PIN) and `proofs/S0-02/check_buzz_authz.py`,
  `proofs/S0-02/oracle/denial_table.py` (another agent's work in flight). Each throwaway repo: `core.hooksPath` → a copy
  of the PIN's `scripts/hooks/pre-commit` only (byte-equal, `cmp`), local identity, `commit.gpgsign=false`.
- Interpreters: the hook's `$PY` resolved to `/root/venv-agent-factory/bin/python` (Python 3.11.15, pyflakes 3.4.0) and
  ran every hook gate (lint_delta, shell syntax, the future-stamp gate, the never-a-gate screen). The `--root` CLI probes
  ran under `python3` = `/usr/local/bin/python3` (Python 3.11.15). Hook gates that never fired in the throwaway repos
  (script or trigger path absent): anchor check, vendored manifest, skill sync, mirror, lane skills. None is counted green.
- A hook-output line that names a line of a MODIFIED throwaway copy of a real file is quoted with that line number in
  words (report_lint would otherwise check it against the tree).

## (A) — from the PC lane's draft (sha256 856dd688…), re-checked in the sandbox

### (A) sandbox re-check (this lane, 2026-09-23 08:59-09:05Z)

| item | instrument | observed (pasted) | SOLID/UNSURE |
|---|---|---|---|
| A1 suites, twice | venv `python -m pytest` on the 3 files, `--basetemp=/tmp/vj10/a1/bt` | `57 passed in 5.16s` then `57 passed in 5.45s`, rc 0 both (set 4e7f72bca20a) | SOLID |
| A1 live screen, both modes | `python3 scripts/no_laya_in_gates.py` and `--staged` | `no_laya_in_gates: 38 files scanned, clean`, rc 0, both modes; allowlist entries 38 | SOLID |
| A1 pyflakes, 2 scripts + 3 tests | venv `python -m pyflakes` (the hook's `$PY`) | rc 0 | SOLID |
| A2 row a — a listed file replaced in the index by a `120000` symlink to an unlisted file carrying the vocabulary; real `git commit` | throwaway `/tmp/vj10/a2` (allowlist shape, 40 files) | commit rc 1; `gate-file-not-regular: scripts/validate-ledger mode=120000`; `COMMIT BLOCKED by the never-a-gate screen (rc=4)`; HEAD unchanged (cf55ef2) | SOLID |
| A2 row b2 — `160000` gitlink whose commit object is present (`git cat-file -e` rc 0) | same repo, `update-index --cacheinfo 160000,<HEAD>` | commit rc 1; `gate-file-not-regular: scripts/validate-ledger mode=160000`; rc=4; HEAD unchanged | SOLID |
| A2 row c — a listed `100644` file made `100755` + a benign edit | same repo | commit rc 0; `no_laya_in_gates: 38 files scanned, clean`; `mode change 100644 => 100755 proofs/S0-12/check_pin_diff.py`; HEAD advanced (f7d0b97) | SOLID |
| (A) mutants (mine; scratch copy, sha restored) | `/tmp/vj10/mutants.py` | ma1 (`120000` accepted as regular) killed by `test_staged_symlinked_gate_file_is_not_regular`; ma3 (on-disk symlink branch dropped) killed by `test_worktree_symlinked_gate_file_is_not_regular`; **ma2 (the on-disk `not-a-regular-file` branch dropped) SURVIVED** | SOLID |
| ma2 live differential | PIN screen vs ma2 screen, `--root`, 8 s timeout | a FIFO at a listed path: PIN `rc=4 gate-file-not-regular: scripts/g.sh not-a-regular-file`, mutant `TIMEOUT after 8 s (hung)`; a directory: PIN the same line, mutant `rc=4 gate-file-unreadable: scripts/g.sh` | SOLID |

Rows a, b2 and c reproduce, so (A) stands as drafted. The branch ma2 removes is `scripts/no_laya_in_gates.py:603-604` (`not-a-regular-file`).
Additions from this re-check:
- **F-A2 sharpened (still FOLLOW-UP):** the untested branch is what keeps an on-disk run from HANGING on a FIFO. Its
  removal passes all 33 screen tests (`33 passed in 2.46s` under ma2). Suggested test: `mkfifo` at a listed path →
  rc 4 `not-a-regular-file`, under a subprocess timeout.
- **F-A4 (INFO, SOLID):** the draft's row a calls `scripts/validate-ledger` "100644, non-executed". `git ls-tree` reads
  `100755` at 5a00d13, c269263 and 2ebd486; the PC throwaway copy probably lost the mode. No effect on the verdict (row a
  reproduces here on the `100755` file).
- **F-A5 (INFO):** the draft labels (A) `MERGE-READY` while listing F-A2 as a real FOLLOW-UP. By the label definitions
  that is `MERGE-READY-WITH-FOLLOWUPS`; my recommendation uses that label (see GATE RECOMMENDATIONS).
- **F-A6 (INFO):** the draft's ENV FACTS say "see DISCREPANCIES", but the lane died before writing that section. The
  discrepancy it names is recorded here: on the PC the hook's `$PY` resolved to the `AF_VENV` python (it has pyflakes), not the
  system `python3` the PC brief predicted. It does not change any (A) result.
- Not re-run here: the draft's rows d (symlink part), e, f and A3 (PC evidence, kept as drafted). The FIFO and directory
  parts of row d were re-observed through the ma2 differential above.

### (A) the PC lane's draft, verbatim (headings demoted two levels; text otherwise unchanged)

PIN 5a00d13 (origin head at authoring). Lane pc-verify-j1-0-r23-stamp, role adversarial-verifier,
strict local route (qwen-local/qwen3.8-27b-local). Report = finding inventory (no severity
filter) + ONE gate recommendation per component. Coordinator owns the gate; I never self-accept.

Attempt 2 of this lane: attempt 1 died on an HTTP 503 (report.attempt1.md is a 110-byte stub,
no finished sections). Worktree was CLEAN at 5a00d13 (no prior lane edits on disk), so this is a
fresh run, not a continuation. All boundary identities re-measured first (match the brief's
PREMISE: a8a1e114d32c1528/653, c911a5bd773e0b2c/655, e3db42b85de898a4/49, f8f587f999ae46a0/133,
a7adc991c1bf0d29/109, f1f463bbae3f3d0f/192, 4ea0979cdfcc166c/103).

ENV FACTS (this host):
- python3 = /usr/bin/python3 → Python 3.13.11. NO pyflakes module in it.
- AF_VENV=/home/rocco/venv-agent-factory (exported). scripts/hooks/pre-commit:13-14 →
  $PY="$AF_VENV/bin/python" = /home/rocco/venv-agent-factory/bin/python, which HAS pyflakes.
  So the hook's $PY is the AF_VENV python, NOT the bare system python3 the brief predicted
  (the brief's premise "on this host that is the system python3" is FALSE — see DISCREPANCIES).
- /root/venv-agent-factory/bin/python is ABSENT.

#### (A) J1-0-R2 — a listed gate file must be a REGULAR file

##### A1 — landing gates at the PIN (reproduced)

| claim | instrument | observed | SOLID/UNSURE |
|---|---|---|---|
| 57 passed, bitwise over 2 runs | pytest 3 files, -p no:cacheprovider | run1 "57 passed in 7.05s"; run2 "57 passed in 7.02s" (counts identical) | SOLID |
| live screen both modes "38 files scanned, clean" rc 0 | `python3 scripts/no_laya_in_gates.py` / `--staged` | both: "no_laya_in_gates: 38 files scanned, clean" rc=0; allowlist (grep -vE '#^\|blank') = 38 entries = scanned | SOLID |
| pyflakes clean on the 2 scripts + 3 tests | AF_VENV python -m pyflakes (the interpreter the hook uses) | rc=0 (clean). Note: bare system python3 has no pyflakes module (rc=1 module-not-found) — not a code defect, just the wrong interpreter | SOLID (with AF_VENV python) |

`scanned` == allowlist entry count (38) confirmed — the count is not inflated by the structural
walk (the walk only checks membership, not the scan count).

##### A2 — AMENDMENT 1 through the REAL hook in a throwaway repo

Template: the 38 allowlisted files copied into a fresh git repo, `core.hooksPath` → a copy of
the PIN's `scripts/hooks/`, git identity set locally, commit.gpgsign=false. The real
`scripts/no_laya_in_gates.py` (the hook's screen) is run inside. All cases below ran through a
real `git commit` (the hook) unless marked "screen only".

| case | shape | observed (hook / screen) | SOLID/UNSURE |
|---|---|---|---|
| a (motivating) | listed `validate-ledger` (100644, non-executed) replaced in INDEX by a 120000 symlink → unlisted `vocab_target.sh` (carries `laya`); `git show :validate-ledger` = "vocab_target.sh" (link text, not content) | commit rc=1; screen line `gate-file-not-regular: scripts/validate-ledger mode=120000`; "COMMIT BLOCKED by the never-a-gate screen (rc=4)"; HEAD unchanged | SOLID |
| b | 160000 gitlink at a listed path, staged by `git add` on a nested repo | `git add` REFUSED the nested repo ("adding files failed" / "does not have a commit checked out"); a subsequent `git commit` then saw the path ABSENT from the index → `gate-file-missing` (rc=4, commit blocked). b4 (a real `git submodule add`) also produced NO 160000 on this host: the file transport is forbidden by git security defaults ("transport 'file' not allowed"), so the submodule never staged. So on this host a real gitlink cannot even be staged by the normal commands | SOLID (refused) / not a clean gitlink repro |
| b2 | 160000 gitlink whose commit object IS in the outer object DB (`update-index --cacheinfo 160000,<HEAD-commit>`; `git cat-file -e :path` rc=0) | commit rc=1; screen line `gate-file-not-regular: scripts/validate-ledger mode=160000` (rc=4); HEAD unchanged | SOLID — the :596 `mode=160000` branch IS reachable |
| b3 | 160000 gitlink whose commit object is NOT in the object DB (`update-index --cacheinfo 160000,<fake sha>`; `git cat-file -e :path` rc=1) | screen rc=4, line `gate-file-missing: scripts/validate-ledger` (NOT `mode=160000`). Proves the :592 existence check runs BEFORE the :596 mode check: an unfetched gitlink is refused via the missing branch | SOLID — confirms the check order |
| c (positive) | well-formed index, 100755 executable gate files (the 3 hooks), a benign staged edit | commit rc=0; "no_laya_in_gates: 38 files scanned, clean"; "[master …] case-c-exec-clean 1 file changed" | SOLID |
| d (on-disk, screen only, no --staged) | symlink at a listed path | screen rc=4 `gate-file-not-regular: scripts/g.sh symlink`, 0.050 s | SOLID |
| d (on-disk) | FIFO at a listed path | screen rc=4 `gate-file-not-regular: scripts/g.sh not-a-regular-file`, 0.047 s — NOT opened, no hang | SOLID |
| d (on-disk) | directory at a listed path | screen rc=4 `gate-file-not-regular: scripts/g.sh not-a-regular-file`, 0.048 s | SOLID |
| e (on-disk) | listed path whose PARENT dir is a symlink to OUTSIDE the repo; final path a regular file | screen rc=0 "1 files scanned, clean" — the final path's lstat is REGULAR (a parent symlink does not make the final path a symlink), so it is read and screened, not refused. The parent symlink CAN point outside the repo and the content it resolves to IS screened | SOLID (mechanism) |
| e-v (on-disk) | listed path whose final component is itself a symlink (chained under a symlinked parent) | screen rc=4 `gate-file-not-regular: p/v.sh symlink` — the FINAL path is what lstat checks, so a symlink terminal component is refused even under a symlinked parent | SOLID |
| f1 | INDEX clean (100755 regular) but WORKTREE replaced by a symlink → vocab file; `--staged` | the SCREEN reads the INDEX (100755) and reports "no_laya_in_gates: 38 files scanned, clean" — it did NOT block. The `git commit` (no `-a`) returned rc=1 only with "no changes added to commit" (nothing was staged). Net: --staged judges the INDEX, a worktree-only symlink is invisible to it | SOLID (index judged) |
| f2b | INDEX = 120000 symlink → clean target; WORKTREE also a symlink → clean target; `--staged` | commit rc=1; screen `gate-file-not-regular: scripts/validate-ledger mode=120000` (rc=4). The INDEX's 120000 is what is judged (the worktree symlink is irrelevant to the decision) | SOLID (index judged) |

**Conclusion for A:** AMENDMENT 1 (a listed gate file must be a REGULAR file) is SOLID through
the real hook. The motivating case (a) is caught exactly as the brief states (rc 4,
`mode=120000`, commit refused, HEAD unchanged). The on-disk branches (symlink / FIFO / dir) all
fire with the correct message; the FIFO is never opened (no hang, ~0.05 s). The `--staged` mode
judges the INDEX (f1: index clean 100755 + worktree symlink → screen clean "38 files scanned,
clean"; the commit rc=1 was "no changes added to commit" because nothing was staged, NOT a gate
block — i.e. the screen itself did not block); f2b: index 120000 → screen blocked. The on-disk
mode judges lstat of the final path. For the `160000` gitlink (b/b2/b3): the code's existence
check (:592) runs BEFORE the mode check (:596) (proven by b3). A gitlink whose commit object is
in the object DB is refused as `mode=160000` (b2); one whose object is not fetched is refused as
`gate-file-missing` (b3). On THIS host a real gitlink cannot even be staged by `git add` or
`git submodule add` (the file transport is forbidden, b), so the only way to get a 160000 into
the index here is `update-index --cacheinfo`. Every gitlink path is refused (rc 4, commit
blocked) — the only difference is which message line names it.

##### A3 — positive staged path (a test that pins a CLEAN exit on a well-formed index w/ 100755)

- `tests/test_no_laya_in_gates.py:400` `test_executable_regular_gate_file_stays_clean` —
  EXACTLY the requested positive control: a file chmod'd to 0755 and staged is asserted
  `mode == "100755"`, then `--staged` must return rc=0 with "2 files scanned, clean".
  SOLID: the suite is NOT failures-only; a clean exit on a well-formed index with an
  executable gate file is pinned.
- `tests/test_no_laya_in_gates.py:136` `test_staged_mode` case 1 also pins rc=0 (staged clean,
  worktree dirty).
- The brief's named test list (`test_staged_symlinked_gate_file_is_not_regular` :357,
  `test_worktree_symlinked_gate_file_is_not_regular` :383, `test_executable_regular_gate_file_stays_clean`
  :400) all exist at those line numbers (A1 grep confirmed). No test names a FIFO, directory or
  gitlink — the on-disk `not-a-regular-file` branch (:604) and the `160000` mode have no NAMED
  test; I exercised them live (A2 d, b2). Whether they are exercised "at all" (A2's open
  question): the not-a-regular-file branch IS exercised by my live d-case; the 160000 branch is
  exercised by my live b2-case. Neither has a committed test — see finding F-A3.

##### (A) findings (inventory, no severity filter)

- **F-A1 (INFO / SOLID)** — For a `160000` gitlink, the `gate-file-missing` branch (:592,
  existence check) runs before the `gate-file-not-regular mode=160000` branch (:596) (proven by
  b3: an unfetched gitlink → `gate-file-missing`; b2: a fetched-object gitlink → `mode=160000`).
  So the not-regular message for a gitlink only fires when the commit object is in the object DB.
  On this host a real gitlink cannot be staged by `git add`/`git submodule add` (file transport
  forbidden), so b2/b3-style `update-index --cacheinfo` is the only local way to make one.
  Effect: cosmetic (message wording for a path that is refused either way); the contract outcome
  (refuse a non-regular listed file, block the commit) is achieved on every gitlink path.
  No blocking-predicate mapping (the contract wants "refuse non-regular"; it is refused).
- **F-A2 (FOLLOW-UP / UNSURE)** — No committed test exercises the on-disk `not-a-regular-file`
  branch (FIFO/directory) or the `160000` mode. The brief flags this (A2's open question). My
  live d- and b2-cases show both branches are reachable and fire correctly, but a reviewer can
  only re-verify them by my live repro, not by the committed suite. Suggested fix: add a
  `test_staged_gitlink_mode_is_not_regular` (update-index --cacheinfo 160000) and a
  `test_worktree_fifo_is_not_regular` (mkfifo) to the committed suite so the branch is
  independently reproducible. Follow-up, not a blocker: the branch is proven reachable and
  the contract outcome (refusal) is already pinned for the 120000 case by
  `test_staged_symlinked_gate_file_is_not_regular`.
- **F-A3 (INFO / SOLID)** — `--staged` judges the INDEX; a worktree-only symlink (index clean)
  passes the screen (f1). This is by design (the screen's contract is index-consistency in
  --staged mode, per J1-0-R1). The on-disk mode would catch the same file if it were later
  committed without the index fix, so there is no durable bypass. Not a defect.

##### (A) predicate table (findings vs the five conjuncts)

| finding | 1 contract-mapped | 2 canonical-path | 3 material effect | 4 discriminator | 5 in-boundary | BLOCKS? |
|---|---|---|---|---|---|---|
| F-A1 gitlink→missing shadows mode=160000 | none (contract wants "refuse non-regular"; achieved) | yes (real git commit) | no (commit blocked either way; only message wording differs) | yes (b vs b2) | yes | NO |
| F-A2 no committed test for 160000/FIFO/dir branch | none (no test is a frozen contract criterion) | n/a | no (the runtime behaviour is correct; the gap is in test coverage) | yes (b2, d live) | yes | NO (follow-up) |
| F-A3 --staged index-vs-worktree | none (by design per J1-0-R1) | yes | no (on-disk catches later) | yes (f1/f2b) | yes | NO |

##### (A) GATE RECOMMENDATION

**MERGE-READY** (no qualifying blockers). AMENDMENT 1 is SOLID through the real hook: the
motivating symlink case, the executable positive control, and the on-disk FIFO/dir/symlink
branches all behave as the brief specifies. The two findings are an INFO (message wording for
an already-blocked gitlink) and a FOLLOW-UP (add committed tests for the 160000/FIFO/dir
branches so they are reviewer-reproducible). Neither satisfies the full blocking predicate.
My recommendation depends on the live A2 b2/d repros I ran this session (no committed test yet
covers those exact branches) — the 120000 case, which IS the motivating case, is covered by
committed test :357.

## (B) J1-0-R3 — the screen follows its in-process include edges (AMENDMENT 2)

Contract read (frozen before dispatch):
- AMENDMENT 2, `tasks/briefs/laya/J1-0-brief.md:17`: "the in-process include edges are closed"; any source or dot command in a listed non-Python gate is `gate-file-sources` unless its (file, target) pair is allowed; "Exec edges stay a declared, measured limit".
- R3 STATUS note, `tasks/briefs/laya/J1-0-R3-brief.md:12`: the scan is "quote-, comment- and heredoc-aware".
- R3 rule 4, `tasks/briefs/laya/J1-0-R3-brief.md:40`: an exec edge is a script the gate "runs it in another process" — the ONLY declared limit.
- R3 rule 2 order, `tasks/briefs/laya/J1-0-R3-brief.md:35`: in `sys.stdlib_module_names` → allowed (stdlib first).
- AF-AP-120, `docs/INCIDENT-LOG.md@2ebd486:466` (`THE LEXICAL GATE SCREEN'S CLOSURE STOPS AT THE FILE`).

Code graded: `_command_segments` `scripts/no_laya_in_gates.py:99-186`, `_source_errors` `scripts/no_laya_in_gates.py:189-208`,
`_import_errors` `scripts/no_laya_in_gates.py:307-361`, `ALLOWED_SOURCES` `scripts/no_laya_in_gates.py:78-81`. Pack:
`scripts/lane_context.sh` (brief's command) → `/tmp/vj10/pack.md`; GitNexus impact LOW for all four symbols; crg `callers_of`:
`_command_segments` ← `_source_errors` ← `main`, `_package_files` ← `_import_errors` ← `main`; crg `tests_for` finds 0 (the tests
run the screen as a subprocess, so the graph cannot see them).

### B1 — the coordinator's shapes (appendix B verbatim, `VJ10_BASE=/tmp/vj10/probe`, run from `/tmp/vj10/pin` = the PIN)
```
[S0 direct token in a listed gate (control)] rc=3 :: scripts/g.sh:2:laya
[S1 sys.path + stdlib-named helper] rc=0 :: no_laya_in_gates: 1 files scanned, clean
[S2 importlib.import_module(helper)] rc=0 :: no_laya_in_gates: 1 files scanned, clean
[S2b static import helper (control)] rc=4 :: gate-file-import-unlisted: scripts/g.py:1 imports helper -> scripts/helper.py
[S3a builtin source] rc=0 :: no_laya_in_gates: 1 files scanned, clean
[S3b command .] rc=0 :: no_laya_in_gates: 1 files scanned, clean
[S4 eval cat] rc=0 :: no_laya_in_gates: 1 files scanned, clean
[S5 yaml run-block continuation] rc=4 :: gate-file-sources: .github/workflows/w.yml:6: scripts/h.sh
[S6 source inside $( )] rc=4 :: gate-file-sources: scripts/g.sh:2: scripts/h.sh
```
All nine lines equal the PC brief's pasted premise (SOLID). Grading, with the runtime observed (the helper reports its
BASHPID/pid and cmdline; in-process = same pid and the gate's cmdline):

| shape | runtime | edge class | graded |
|---|---|---|---|
| S1 | helper ran IN-PROCESS (`harness-ports/bin/secrets.py`) | in-process import | the frozen algorithm allows stdlib names first → a gap in the contract's algorithm, not a builder deviation → F-B4 |
| S2 | IN-PROCESS (`scripts/helper.py`) | in-process dynamic import | NOT an exec edge (rule 4 = another process). The docstring's "same limit" is not in the contract → F-B2 class |
| S3a, S3b | IN-PROCESS (bashpid = gate pid, cmd `bash scripts/g.sh`) | in-process source | AMENDMENT 2's text covers them (they are source/dot commands) → F-B3 |
| S4 | IN-PROCESS (bashpid 3214 = gate pid 3214) | in-process eval of a file's text | **appendix B labels S4 "an exec edge": wrong — eval runs in the gate's own shell**; not literally a source/dot command → F-B3 (contract clarification) |
| S5, S6 | caught | in-process source | contract met |

### B2 — shell and YAML include shapes (the PIN screen `--root`; runtime = the gate run by bash from the tree root)
| # | shape | screen | runtime | class | AMENDMENT 2 text covers? | finding |
|---|---|---|---|---|---|---|
| S01 | control `. scripts/h.sh` | CAUGHT `gate-file-sources: scripts/g.sh:2: scripts/h.sh` | IN-PROCESS | include | yes | — |
| S02 | `builtin source x` | CLEAN | IN-PROCESS | include | yes | F-B3 |
| S03 | `command . x` | CLEAN | IN-PROCESS | include | yes | F-B3 |
| S04 | `source <(cat x)` | CAUGHT (target `<`) | IN-PROCESS | include | yes | — (F-B9 cosmetic) |
| S05 | `exec 3<x; . /dev/fd/3` | CAUGHT (target `/dev/fd/3`) | IN-PROCESS | include | yes | — |
| S06 | `. "$(dirname "$0")/x"` | CAUGHT | IN-PROCESS | include | yes | — |
| S07 | `shopt -s expand_aliases; alias s=source; s x` (one line) | CLEAN | did NOT run (`s: command not found`: bash expands an alias only on a later line) | none | n/a | — |
| S08 | the same on three lines | CLEAN | IN-PROCESS | include | in effect (the text is `s x`) | F-B3 |
| S09 | backslash-newline between `source` and target | CAUGHT (target reported as `\`) | IN-PROCESS | include | yes | — (F-B9) |
| S10 | backslash-newline INSIDE the word (`sou\` / `rce x`) | CLEAN | IN-PROCESS | include | yes | F-B3 |
| S11 | `. $'scripts/h.sh'` | CAUGHT | IN-PROCESS | include | yes | — |
| S12 | `echo $'it\'s'` then `. x` on the next line | CLEAN | IN-PROCESS | include | yes | F-B1 (desync) |
| S13 | `<<-EOF` with a tab-indented delimiter, `. x` after | CAUGHT (line 5) | IN-PROCESS | include | yes | — |
| S14-S16 | `<<'EOF'`, `<<"EOF"`, `<<-'EOF'`: a `. x` in the body + one after | CAUGHT (line 5 only; body not flagged) | IN-PROCESS | include | yes | — |
| S17 | `cat <<END-X` … `END-X`, `. x` after | CLEAN | IN-PROCESS | include | yes | F-B1 (delimiter read as `END`) |
| S18 | `cat <<\EOF` + an apostrophe in the body, `. x` after | CLEAN | IN-PROCESS | include | yes | F-B1 (heredoc not registered) |
| S19 | `f() { . x; }` | CAUGHT | IN-PROCESS | include | yes | — |
| S20 | `trap '. x' EXIT` | CLEAN | IN-PROCESS (at exit) | include | arguable (a dot command in a string the gate's shell runs) | F-B3 |
| S21 | `bash -c '. x'` | CLEAN | OTHER process (`bash -c . scripts/h.sh`) | EXEC | no (declared limit) | — (F-B10) |
| S22 | `eval ". x"` | CLEAN | IN-PROCESS | include | arguable | F-B3 |
| S23 | `y=${x#a}; . x` | CAUGHT (`${…}` masking keeps `#` from reading as a comment) | IN-PROCESS | include | yes | — |
| S24 | `y=${x#"}"}` then `. x` next line | CLEAN | IN-PROCESS | include | yes | F-B1 |
| S25 | `x=$(( 2 # 3 )); . x` | CLEAN (` #` read as a comment) | did NOT run (`bad substitution: no closing ')'`) | none | n/a | — (bash refuses the line) |
| S26 | `z=$(( 1 << n ))` then `. x` next line | CLEAN (`<< n` read as a heredoc) | IN-PROCESS | include | yes | F-B1 |
| S27 | `case x in x) . y ;; esac` | CAUGHT | IN-PROCESS | include | yes | — |
| S28 | `time . x` | CLEAN | IN-PROCESS | include | yes | F-B3 |
| S29 | `FOO=1 . x` | CLEAN | IN-PROCESS | include | yes | F-B3 |
| S30-S32 | `\. x`, `\source x`, `'source' x` | CLEAN | IN-PROCESS | include | yes | F-B3 |
| S33 | `S=source; $S x` | CLEAN | IN-PROCESS | include | arguable | F-B3 |
| S34 | `echo x}#; . x` | CLEAN (`}` splits, `#` then reads as a comment) | IN-PROCESS | include | yes | F-B1 |
| S35 | `m="$(printf '%s' "it's")"` then `. x` | CLEAN (nested quote read as a close) | IN-PROCESS | include | yes | F-B1 (the live `pc_lane.sh` mechanism) |
| S36 | `y=${x:-'{'}; . x` | CLEAN (the `${` scan runs past the line) | IN-PROCESS | include | yes | F-B1 |
| S37 | control `if true; then . x; fi` | CAUGHT | IN-PROCESS | include | yes | — |
| X1, X2 | redirection prefix `2>/dev/null . x`, `< x . /dev/stdin` | CLEAN | IN-PROCESS | include | yes | F-B3 |
| S38 | YAML control: `- run: . scripts/h.sh` | CAUGHT `gate-file-sources: .github/workflows/w.yml:7: scripts/h.sh` | ran in the step's shell (PyYAML value run by bash) | include | yes | — |
| S39 | YAML: an apostrophe in an earlier step NAME | CLEAN | ran in the step's shell | include | yes | F-B1 |
| S40 | YAML: `cat <<EOF` in an earlier `run: \|` block (indented delimiter) | CLEAN (waits for a column-0 `EOF`) | ran in the step's shell | include | yes | F-B1 |
| X3 | YAML flow mapping `- {name: a, run: . scripts/h.sh}` | CLEAN | ran in the step's shell | include | yes | F-B1 |

### B2 on the REAL listed files — where the scanner loses sync today (PIN blobs; re-run on the worktree at 09:2xZ: same)
| listed gate file | lines | lines never scanned (heredoc skip) | multi-line quote spans | desync to EOF |
|---|---|---|---|---|
| scripts/pc_lane.sh | 610 | **318 (lines 293-610)** | 3 | **YES** |
| harness-ports/bin/pc-lane.sh | 530 | 19 (two real `SHIMEOF` heredocs) | 2 (re-sync in 1-2 lines) | no |
| scripts/hooks/post-commit | 65 | 0 | 2 (nested `"$(…)"`, re-sync) | no |
| scripts/pc_suite.sh | 127 | 0 | 1 (a real multi-line string) | no |
| the other 8 shell/YAML gates | — | 0 | 0 | no |

- The trigger is `scripts/pc_lane.sh:292` (`EFF_STATE="$(bridge "export … <<'PY'`). The inner quote of the nested `"$(bridge "…")"` closes the scanner's quote, `_HEREDOC_RE` at `scripts/no_laya_in_gates.py:166` then registers `<<'PY'` (bash sees it as TEXT inside the bridge string), and the skip at `scripts/no_laya_in_gates.py:115-119` (`if heredocs and quote is None`) waits for a line exactly `PY`.
- That line never comes: the remote heredoc ends mid-line at `scripts/pc_lane.sh:308` (`PY")" || die`), so every later line is skipped. `bash -n scripts/pc_lane.sh` rc 0 (bash's parse ends cleanly).
- The scanner has no signal for "ended inside a heredoc or quote": the final flush at `scripts/no_laya_in_gates.py:185-186` (`if raw:`) yields silently.
- Nothing is hidden there TODAY, by two instruments: the scanner on lines 293-610 alone → 0 source hits; a loose token grep over the same span → comments, echo text and `git add -A .` (a path argument) only. So the live verdict is right by luck, not by rule.
- Lines 386 and 397 (the STATUS note's quote-blind false positives) are masked correctly when scanned alone (lines 380-400: 0 hits, 0 lines skipped): the quote handling works there, but on the real file those lines are also inside the blind span (F-B7).

### F-B1 canonical reproduction — the REAL hook, a real `git commit`, the PIN's real files (`/tmp/vj10/bh`, `/tmp/vj10/bh/repo`)
| case | change (throwaway copy) | observed (pasted) |
|---|---|---|
| BH-1 control | `. scripts/h.sh` inserted after line 100 of the real `scripts/pc_lane.sh`; unlisted `scripts/h.sh` = `echo laya` | commit rc=1; `gate-file-sources` names the inserted line (throwaway line 101); `COMMIT BLOCKED by the never-a-gate screen (rc=4)`; HEAD unchanged (051d2f9) |
| BH-2 | the same line inserted after line 400 (inside the blind span) | commit rc=0; `no_laya_in_gates: 38 files scanned, clean`; `[master bf7eea7] bh2` — the committed gate file sources an unlisted helper carrying the vocabulary |
| YH-3 control | a step `- name: Load helper` / `run: . scripts/h.sh` inserted after line 46 of the real `stage0-ci.yml` | commit rc=1; `gate-file-sources` names the inserted run line (throwaway line 48); rc=4 |
| YH-4 | the same step + ONE apostrophe in the existing step name `.github/workflows/stage0-ci.yml@2ebd486:35` (`Install dependencies` → `Install the suite's dependencies`) | commit rc=0; `no_laya_in_gates: 38 files scanned, clean`; `[master 3658f36] yh4`; PyYAML parses it with the new step last in `tests`; the scanner masks lines 35-53 (the quote closes at the `tag's` apostrophe in the line-53 comment) |

### B3 — Python include shapes (the PIN screen `--root`; runtime = `python3 <gate>` from the tree root; helper prints its pid)
| # | shape | screen | runtime | finding |
|---|---|---|---|---|
| P01 | control `import helper` | CAUGHT `gate-file-import-unlisted: scripts/g.py:1 imports helper -> scripts/helper.py` | IN-PROCESS | — |
| P02 | S1: `sys.path.insert(0, 'harness-ports/bin')` + `import secrets` | CLEAN | IN-PROCESS (`harness-ports/bin/secrets.py`) | F-B4 |
| P03 | the same with `import yaml` (an EXTERNAL name) | CLEAN | IN-PROCESS (`harness-ports/bin/yaml.py`) | F-B4 |
| P04 | the same with a non-stdlib name | CAUGHT `gate-file-import-unresolved` | IN-PROCESS | — (fail-closed) |
| P05-P09 | S2 `importlib.import_module`, `__import__`, `exec(open(x).read())`, `runpy.run_path`, `spec_from_file_location` + `exec_module` | CLEAN (all five) | IN-PROCESS (all five) | F-B2 class |
| P10 | import inside a function | CAUGHT | IN-PROCESS | — |
| P11 | `from . import helper` in a dir with no `__init__.py` | CAUGHT (unlisted) | did NOT run (`attempted relative import with no known parent package`) | — (over-approximation) |
| P12 | `from helper import *` | CAUGHT | IN-PROCESS | — |
| P13 | `import a.b.c`, `a/__init__.py` + `a/b.py` only | CAUGHT (both files unlisted) | IN-PROCESS (`a/b.py`) | — |
| P14 | `import a.b.c`, `a/b.py` only (namespace package) | CAUGHT `gate-file-import-unresolved` | IN-PROCESS (`a/b.py`) | — (fail-closed) |
| P15 | a repo `yaml.py` beside the gate | CAUGHT `imports yaml -> scripts/yaml.py` — repo-first CONFIRMED | IN-PROCESS | — |
| P16 | a repo `json.py` beside the gate | CAUGHT | IN-PROCESS (shadows stdlib) | — |
| P17 | a repo `os.py` beside the gate | CAUGHT | did NOT run (`os` is frozen/preloaded) | — (false refusal, F-B8) |
| P18 | a module at depth 2 (`scripts/a/b/deep.py`) | CAUGHT (unlisted) | did NOT run (`No module named 'deep'`) | — (over-approximation) |
| P19 | a module at depth 3 | CAUGHT `gate-file-import-unresolved` | did NOT run | — |
| P20 | `importlib.import_module('agent_factory.decisions')` | VIOLATION rc 3 (`scripts/g.py:2:agent_factory.decisions`) | did NOT run | — (the vocabulary scan reads the string) |

Resolution order, the screen vs `python3 <gate>` (Python: builtin and frozen modules first, then `sys.path` with `sys.path[0]` = the
script's own directory, first hit wins). The screen's order: the importer's directory, its subdirectories to depth 2, then
`scripts/` and `src/`, then stdlib/EXTERNAL (`scripts/no_laya_in_gates.py:349` `sys.stdlib_module_names`) — repo-first, the reverse
of the R3 text order (rule 2 said stdlib first). Where they differ:
- fail-OPEN only (1): a `sys.path` entry the screen does not search, holding a stdlib- or EXTERNAL-named module (P02, P03);
- fail-OPEN only (2): every dynamic load (P05-P09);
- fail-CLOSED over-approximations (refusals Python would not need): subdirectories and `scripts/`/`src/` searched for any gate
  (P18); a repo file shadowing a builtin/frozen module (P17); ambiguity refused where Python takes the first hit; namespace
  packages refused as unresolved (P14); a relative import with no parent package (P11).

### F-B2 — the live in-process dynamic loads from LISTED Python gates (census at 2ebd486; `grep` over every listed Python gate)
| listed gate | site | loads (in-process `exec_module`) | target listed? |
|---|---|---|---|
| scripts/lint_delta.py | `scripts/lint_delta.py:106` `spec_from_file_location("edit_snapshot", hook)` | .claude/hooks/edit-snapshot.py | **NO** |
| scripts/ap_screen.py | `scripts/ap_screen.py:26` `spec_from_file_location("es"` | .claude/hooks/edit-snapshot.py | **NO** |
| scripts/proof-runner | `scripts/proof-runner:39` `SourceFileLoader` | scripts/validate-ledger | yes |
| scripts/ledger-gen | `scripts/ledger-gen:17` `SourceFileLoader` | scripts/validate-ledger | yes |
| proofs/S0-02/check_buzz_authz.py | `proofs/S0-02/check_buzz_authz.py@2ebd486:91-92` `_load_by_path` | S0-01 check_acp_conformance.py, tools/nostr_verify.py | yes, yes |
| proofs/S0-03/check_omniroute_roundtrip.py | `proofs/S0-03/check_omniroute_roundtrip.py:114` `_S0_01_CHECKER` | proofs/S0-01/check_acp_conformance.py | yes |
| proofs/S0-05/check_egress.py | `proofs/S0-05/check_egress.py@2ebd486:122` `_PINS_FILE` | proofs/S0-01/pins.py | yes |

8 sites in 7 listed gates, 6 distinct targets, 1 unlisted (2 sites). `_ap_screen()` runs on EVERY `lint_delta --staged` (`scripts/lint_delta.py:141` `screen = _ap_screen()`), even with 0 .py staged. `scripts/ap_screen.py` gates checkpoints with the AP_SCREEN rows it loads from that file, so the file defines a gate.
Reproduction through the REAL hook (`/tmp/vj10/es`, the allowlist shape + `.claude/hooks/edit-snapshot.py` from 2ebd486; one module-level line added that carries the vocabulary and prints its pid and cmdline):
```
commit_rc=0
lint_delta (index vs HEAD): 0 .py changed, 0 NEW pyflakes hit(s), 0 removed
laya EDIT-SNAPSHOT RAN pid=26069 parent-cmd=/root/venv-agent-factory/bin/python /tmp/vj10/es/repo/script
no_laya_in_gates: 38 files scanned, clean
[master c0c3a52] es1
```
- The docstring line `scripts/no_laya_in_gates.py:22` says "Dynamic imports (importlib, __import__, exec of a file) are the same limit".
- The contract's only declared limit is exec edges, a script the gate "runs it in another process" (`tasks/briefs/laya/J1-0-R3-brief.md:40`).
- Its measured count (26/12) covers shell exec edges only; dynamic loads were never measured.
- `.claude/hooks/edit-snapshot.py` today: 477 lines, 0 hits under the screen's own `_check_line`, static imports stdlib only (ast walk), so listing it keeps the live screen clean.

### B4 — the ALLOWED_SOURCES pairs (`scripts/no_laya_in_gates.py:205` `if (entry, target) in ALLOWED_SOURCES`)
- The claim "neither loads repo code" is not a property the screen can see: it matches TEXT only. The second pair (`scripts/pc_lane.sh:160`, `"$PC_LANE_BRIDGE_FN"`) sources whatever file the environment names. The dispatcher test (`harness-ports/tests/test_pc_lane_dispatcher.sh`) sets it to a temp file the test writes. So the claim is about the runtime environment. The same holds for the first pair (`scripts/pc_lane.sh:120`, `"$ROOT/.pc-bridge.env"`): it names an untracked file whose content the owner pastes.

| case (REAL hook, throwaway `/tmp/vj10/bh/repo`) | observed |
|---|---|
| B4-1 `PC_LANE_BRIDGE_FN=scripts/h.sh` + a second `. "$PC_LANE_BRIDGE_FN"` inserted after line 100 of `pc_lane.sh` (before the blind span) | commit rc=0, `no_laya_in_gates: 38 files scanned, clean` — the allowed TEXT re-used, re-pointed at a tracked helper carrying the vocabulary |
| B4-1b `ROOT=scripts; . "$ROOT/.pc-bridge.env"` + a tracked `scripts/.pc-bridge.env` = `echo laya` | commit rc=0, clean |
| B4-2 `. "$ROOT"/.pc-bridge.env` (quoting variant) | commit rc=1, `gate-file-sources` target `"$ROOT"/.pc-bridge.env`, rc=4 — flagged |
| B4-3 `. $ROOT/.pc-bridge.env` (unquoted) | commit rc=1, target `$ROOT/.pc-bridge.env`, rc=4 — flagged |
| B4-4 the first pair's exact text in another gate (`push_clean.sh`, line 4) | commit rc=1, `gate-file-sources` target `"$ROOT/.pc-bridge.env"`, rc=4 — the pair is (file, target): CONFIRMED |

### B5 — mutants (scratch `/tmp/vj10/mut`; exact-once anchor; each `py_compile`d and collected: `33 tests collected`; restored by copy, sha a8a1e114d32c1528 verified after each)
| id | mutant | result (pasted summary) | killed by |
|---|---|---|---|
| m1 | drop the heredoc skip | `1 failed, 32 passed` | test_source_words_in_strings_comments_heredocs_not_flagged |
| m2 | drop the quote masking | `2 failed, 31 passed` | test_live_tree_clean, test_source_words_in_strings_comments_heredocs_not_flagged |
| m3 | drop `_LEADING_KEYWORD_RE` | `33 passed` | **SURVIVED** |
| m4 | drop the YAML key strip | `1 failed, 32 passed` | test_yaml_parentheses_do_not_split_but_run_sources_are_refused |
| m5 | drop the relative-import branch | `1 failed, 32 passed` | test_relative_import |
| m6 | `IMPORT_SEARCH_DEPTH` 2 → 1 | `1 failed, 32 passed` | test_subdir_import_resolved |
| m7 | drop the ambiguity refusal | `1 failed, 32 passed` | test_ambiguous_import_refused |
| m8 | empty `ALLOWED_SOURCES` | `3 failed, 30 passed`; live screen `rc=4 :: gate-file-sources: scripts/pc_lane.sh:120: "$ROOT/.pc-bridge.env"` | test_allowed_source_pair_passes_only_for_its_file, test_closed_sets_locked, test_live_tree_clean |
| m8 | (second live line) | `gate-file-sources: scripts/pc_lane.sh:160: "$PC_LANE_BRIDGE_FN"` | — |
| m9 | add `builtin` to the keyword set | `33 passed` | **SURVIVED** (an improvement: S02 flips to CAUGHT; no test pins either behaviour) |
| m10 | no `( ) { }` separators in shell | `33 passed` | **SURVIVED** |
| m11 | drop the `${…}` masking | `33 passed` | **SURVIVED** |
| m12 | drop the `#` comment rule | `1 failed, 32 passed` | test_live_tree_clean only (live comment text, e.g. pre-commit line 10 "Found by the first") |
| m13 | drop the backslash escape outside quotes | `1 failed, 32 passed` | test_live_tree_clean only (it moves the line-292 desync; pc_lane.sh line 386 is then read) |
| m14 | drop the `<<-` tab strip | `33 passed` | **SURVIVED** |
| m15 | stdlib/EXTERNAL-first order (the R3 text order) | `33 passed` | **SURVIVED** |
| m16 | `--staged` resolves imports from the worktree | `1 failed, 32 passed` | test_staged_import_closure |
| m17 | ALLOWED_SOURCES keyed by target only | `1 failed, 32 passed` | test_allowed_source_pair_passes_only_for_its_file |
| m18 | python-shebang gates treated as shell | `1 failed, 32 passed` | test_python_shebang_gate_imports_checked |

Live differentials for the survivors (PIN screen vs the mutant screen on one discriminating tree; restored OK after):

| id | discriminating input | PIN | mutant |
|---|---|---|---|
| m3 | `if true; then . scripts/h.sh; fi` | rc=4 gate-file-sources | rc=0 clean |
| m9 | `builtin source scripts/h.sh` | rc=0 clean | rc=4 gate-file-sources |
| m10 | `x=$(. scripts/h.sh; echo ok)` | rc=4 | rc=0 |
| m11 | `A=(1 2); n=${#A[@]}; . scripts/h.sh` | rc=4 | rc=0 |
| m14 | `cat <<-EOF` / tab `EOF` / `. scripts/h.sh` | rc=4 | rc=0 |
| m15 | `import yaml` + a repo `scripts/yaml.py` | rc=4 import-unlisted | rc=0 clean |

AF-AP-138, every killer run on the UNMUTATED tree (sha a8a1e114d32c1528): the twelve killing tests by name → `12 passed, 21 deselected in 1.52s`.
The comment case in `tests/test_no_laya_in_gates.py:464` (`# . scripts/helper.sh would be refused`) is vacuous: a line that starts with `#`
can never match `_SOURCE_RE`, comment rule or not. That is why m12 dies only on live repository text.

### Proposed regression tests — run RED at the PIN (scratch `/tmp/vj10/mut/tests/test_vj10_red.py`; NOT committed: boundary)
`5 failed in 0.24s` at sha a8a1e114d32c1528, each on `assert (0 == 4)` (the screen reads clean) or the missing listing. De-vacuous checks:
- the test-1 gate passes `bash -n` and runs its helper in-process (`HELPER-RAN in 29588 (gate 29588)`);
- the test-3 heredoc ends at `END-X` and the helper runs;
- PyYAML parses the test-2 workflow with its sourcing step intact.
```python
from pathlib import Path
from test_no_laya_in_gates import _make_tree, _run, _err_lines, REPO_ROOT

def test_vj10_nested_quote_heredoc_text_does_not_blind_the_scan(tmp_path):   # F-B1, the live pc_lane.sh:292 shape
    _make_tree(tmp_path, "scripts/g.sh\n", {
        "scripts/g.sh": "#!/bin/bash\nX=\"$(bridge \"python3 - \\\"\\$MP\\\" <<'PY'\nprint(1)\nPY\")\" || true\n. scripts/helper.sh\n",
        "scripts/helper.sh": "echo laya\n"})
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4 and _err_lines(r) == ["gate-file-sources: scripts/g.sh:5: scripts/helper.sh"], r.stderr

def test_vj10_yaml_apostrophe_does_not_blind_the_scan(tmp_path):              # F-B1, the YH-4 shape
    wf = ".github/workflows/w.yml"
    _make_tree(tmp_path, wf + "\n", {
        wf: "jobs:\n  a:\n    steps:\n      - name: Install the suite's dependencies\n        run: echo ok\n      - run: . scripts/helper.sh\n",
        "scripts/helper.sh": "echo laya\n"})
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4 and "gate-file-sources: %s:6: scripts/helper.sh" % wf in r.stderr, r.stderr

def test_vj10_scan_ending_inside_a_heredoc_fails_closed(tmp_path):            # F-B1 tripwire (S17 shape)
    _make_tree(tmp_path, "scripts/g.sh\n", {
        "scripts/g.sh": "#!/bin/bash\ncat <<END-X\nbody\nEND-X\n. scripts/helper.sh\n", "scripts/helper.sh": "echo laya\n"})
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, r.stderr

def test_vj10_dynamic_import_of_an_unlisted_file_is_refused(tmp_path):        # F-B2, code path (P09 shape)
    _make_tree(tmp_path, "proofs/x/check_y.py\n", {
        "proofs/x/check_y.py": "import importlib.util\nspec = importlib.util.spec_from_file_location('h', 'proofs/x/helper.py')\n"
                               "m = importlib.util.module_from_spec(spec)\nspec.loader.exec_module(m)\n",
        "proofs/x/helper.py": "X = 1\n"})
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, r.stderr

def test_vj10_real_tree_lists_the_dynamically_loaded_helper():               # F-B2, listing path
    listed = set((REPO_ROOT / "scripts" / "gate_files.txt").read_text().split())
    assert ".claude/hooks/edit-snapshot.py" in listed
```
Test 4 and test 5 are alternatives for the coordinator's F-B2 decision (close dynamic loads in code, or list the one live target and amend
the contract). Mutant-killer fixtures for F-B6 are the six discriminating inputs in the differential table above.

### (B) finding inventory (no severity filter)
- **F-B1 — BLOCKER (SOLID).** The shell/YAML scan in `_command_segments` loses sync on ordinary text and then goes SILENT to EOF. Evidence:
  - LIVE: 318 of 610 lines of the real `scripts/pc_lane.sh` (293-610) are never scanned for include edges, yet the screen prints `38 files scanned, clean`.
  - Reproduced through the real hook: BH-1 refused vs BH-2 landed; YH-3 refused vs YH-4 landed.
  - Member triggers (each CLEAN through the real screen while the helper ran in-process): S12, S17, S18, S24, S26, S34, S35, S36, S39, S40, X3.

  Causes:
  - no model of quoting inside `$(…)` within double quotes (S35, the live one);
  - `$'…'` escapes (S12);
  - a delimiter word read only as `[A-Za-z0-9_]` and never as `\EOF` (S17, S18);
  - `<<` inside arithmetic (S26);
  - braces split everywhere (S34, S36);
  - YAML read as one shell text instead of per `run:` value (S39, S40, X3);
  - no fail-closed signal when the scan ends inside a quote or heredoc (`scripts/no_laya_in_gates.py:185-186`, `if raw:`).

  Contract: AMENDMENT 2 + the STATUS "heredoc-aware" claim. Canonical: yes. Material: yes. The live gate file is unscreened in its
  tail, and `pc_lane.sh` is actively edited (task #167, the dispatcher fix, targets the poller at line 384, inside the blind
  span). Discriminator: BH-1/BH-2, YH-3/YH-4, proposed tests 1-3. In boundary: yes (`_command_segments` + tests).

  Suggested fix — ONE repair keyed to the scanner:
  - a pending heredoc or an open quote at EOF is a completeness error (exit 4);
  - nested quoting inside `$(…)`, so `pc_lane.sh` line 292 parses and the live tree stays clean;
  - the heredoc delimiter is bash's word (`\EOF`, hyphens);
  - YAML is scanned per `run:` value, or at least with YAML-scalar quoting.

  Acceptance: BH-2 and YH-4 refused; every member CAUGHT or refused fail-closed; tests 1-3 green; the live screen clean.
- **F-B2 — BLOCKER (SOLID; or a coordinator contract amendment).** Two listed gates `exec_module` the UNLISTED `.claude/hooks/edit-snapshot.py`
  in-process, one of them inside the pre-commit hook's own lint gate. The docstring files this under "the same limit" as exec edges without
  contract authority, and without a measurement. Reproduced through the real hook (ES: the vocabulary-carrying line ran in pid 26069 = the
  hook's lint_delta process; the screen read clean; the commit landed).

  Contract: AMENDMENT 2's headline "in-process include edges are closed"; R3 rule 4 limits only edges run "in another process". Material:
  a live unlisted in-process include in a gate the pre-commit hook runs on every commit; the file supplies the AP_SCREEN rows that
  `scripts/ap_screen.py` gates checkpoints with. Discriminator: the ES reproduction; proposed tests 4/5. In boundary:
  `scripts/gate_files.txt` + the docstring (+ the rule, if closed in code).

  Fix: list `.claude/hooks/edit-snapshot.py` (0 hits today, stdlib-only imports). Then EITHER follow literal-path
  `spec_from_file_location`/`SourceFileLoader` loads, OR amend the contract to declare dynamic loads a MEASURED limit (the census above:
  8 sites, 6 targets) and correct the docstring sentence.
- **F-B3 — FOLLOW-UP (SOLID) + a contract question.** Spelling and indirection evasions read CLEAN while the source runs in-process:
  S02, S03, S08, S10, S20, S22, S28-S33, X1, X2 and S4 (`eval "$(cat x)"`). AMENDMENT 2's text literally covers most of them. They are
  not blocking because conjunct 3 fails by itself: no instance exists in the live tree, each needs a deliberate unusual spelling, and the
  declared exec-edge limit already leaves an equivalent door (`bash h.sh`) open to a deliberate evader.

  Cheap partial close: strip assignment words, redirections and `builtin`/`command`/`time`, and unquote the command word before
  matching. Declare the rest (alias, eval, trap, `$VAR` as the command word) with a count. Correct appendix B's "exec edge" label for S4:
  eval is in-process.
- **F-B4 — FOLLOW-UP (SOLID).** A `sys.path` entry outside the searched directories plus a stdlib- or EXTERNAL-named helper passes (P02,
  P03). This is inside the frozen algorithm (stdlib names allowed), so it is an undeclared limit of the contract, not a builder deviation.
  No live instance: the listed checkers insert only their own directory, `tools/`, `oracle/` and the pinned fubuki-os checkout outside
  the repo. Fix: declare the limit, or refuse literal `sys.path.insert/append` arguments outside the searched directories.
- **F-B5 — FOLLOW-UP (SOLID; contract).** The ALLOWED_SOURCES key (file, target text) lets `pc_lane.sh` re-use the allowed text any
  number of times, re-pointed at repo code (B4-1, B4-1b landed). That is within the contract's letter. "Neither loads repo code" is an
  environment claim the screen cannot see. Fix: key by (file, target, occurrence count) or by the exact line text, and word the comment
  as an assumption.
- **F-B6 — FOLLOW-UP (SOLID).** Test gaps: m3, m10, m11, m14 and m15 survive and are non-equivalent; m9 shows the prefix-word behaviour is
  pinned in neither direction. m12 and m13 are killed only by live repository content. The comment fixture at
  `tests/test_no_laya_in_gates.py:464` (`would be refused`) is vacuous. Fix: one fixture per differential row above.
- **F-B7 — INFO (SOLID).** The STATUS note's claim that `pc_lane.sh` lines 386 and 397 are no longer false positives because the scan is
  quote-aware is true when scanned alone. On the real file those lines are unscanned anyway (F-B1).
- **F-B8 — INFO (SOLID).** Import resolution over-approximates in the fail-closed direction (P11, P14, P17, P18): some refusals are
  false. Safe; noted for anyone who hits one.
- **F-B9 — INFO (SOLID).** Cosmetic targets: S09 reports `\`, S04 reports `<`.
- **F-B10 — INFO (SOLID).** S21 `bash -c '. x'` runs in another process: the declared exec limit, consistent with the contract.
- **F-B11 — UNVERIFIED (not re-measured).** The docstring's "26 literal exec edges … 12 unlisted scripts". My census covers dynamic Python
  loads only.

### (B) predicate table
| finding | 1 contract | 2 canonical path | 3 material | 4 discriminator | 5 in boundary | BLOCKS? |
|---|---|---|---|---|---|---|
| F-B1 | yes — AMENDMENT 2 + STATUS "heredoc-aware" | yes — real hook, real `pc_lane.sh` and `stage0-ci.yml` | yes — 318 live lines unscanned; a sourcing commit lands | yes — BH-1/BH-2, YH-3/YH-4, tests 1-3 | yes — `_command_segments` | **YES** |
| F-B2 | yes — "in-process include edges are closed"; limit = another process only | yes — real hook (ES) | yes — live unlisted in-process load inside the pre-commit lint gate | yes — ES, tests 4/5 | yes — list/docstring/rule | **YES** (or amendment) |
| F-B3 | yes (text) / arguable (eval, trap, alias, `$S`) | yes — real screen CLI | no, by itself — no live instance; deliberate spellings; exec door already declared | yes — S-table | yes | no → FOLLOW-UP |
| F-B4 | no — the frozen algorithm allows stdlib names | yes — CLI | no — no live instance | yes — P02/P03 | yes | no → FOLLOW-UP |
| F-B5 | no — the contract keys by (file, target) | yes — real hook | no, by itself — deliberate re-pointing | yes — B4-1 | yes | no → FOLLOW-UP |
| F-B6 | no — no frozen test list | n/a | no — coverage | yes — survivors | yes | no → FOLLOW-UP |
| F-B7-F-B10 | no | — | no | — | — | no (INFO) |
| F-B11 | — | not run | — | — | — | UNVERIFIED |

## (C) The future-stamp gate (8d50443; the CI fixture fix 5f6919b)

Contract read: the ledger note `todo/BUILD-TASKLIST.md@2ebd486:181` (`FUTURE-STAMP GATE LANDED`), the incident entry (5a00d13 line 16),
build-loop rule 2's gate sentence (`.claude/skills/build-loop/SKILL.md`, unchanged 5a00d13..2ebd486), and the module docstring
`scripts/stamp_check.py:11-20` (`LEDGER_PLANE`, the three stamp forms, exit codes 0/1/2). Code: `scripts/stamp_check.py`; the hook block
`scripts/hooks/pre-commit:111-124` (`FUTURE-STAMP GATE`).

### C1 — reproduce
| item | observed (pasted) | SOLID/UNSURE |
|---|---|---|
| `tests/test_stamp_check.py` twice | `20 passed in 1.93s`, `20 passed in 2.21s`, rc 0 (set b5ee558a6385 — the ledger note's set) | SOLID |
| a future stamp through the REAL hook (throwaway `/tmp/vj10/c/repo`; HEAD holds the PIN's four real ledger-plane files) | stamp `2026-09-23 09:47Z` at `date -u` = `2026-09-23T09:17:59Z`: commit rc=1; `stamp_check: todo/BUILD-TASKLIST.md: '2026-09-23 09:47Z' is 29.0 min ahead of the clock 2026-09-23T09:17:59Z — paste stamps from date -u or the commit clock`; `COMMIT BLOCKED by the future-stamp gate (rc=1) — paste the stamp from date -u or the commit clock.`; HEAD unchanged (b8876fd) | SOLID |
| a pasted stamp through the REAL hook | stamp `2026-09-23 09:17Z`: commit rc=0; `stamp_check: 1 new stamp(s) in 1 ledger-plane file(s), none ahead of the clock 2026-09-23T09:18:00Z`; `[master e4b8405] c1b` | SOLID |

### C2 — shapes (REAL hook = `git commit` in `/tmp/vj10/c/repo` through a logging wrapper that prints `GIT_INDEX_FILE` and then execs the unchanged PIN hook; CLI = `python3 scripts/stamp_check.py --staged --now <T>`)
| # | shape | via | observed (pasted) | in scope? |
|---|---|---|---|---|
| C2-1 | `git mv` the ledger to `todo/X.md` + a future stamp | hook | rc=0, commit landed (the new path is outside `LEDGER_PLANE`) | declared out of scope |
| C2-2 | rename INTO the plane (`docs/NOTES.md` holding a future stamp → `wiki/topics/live-state.md`, `R100`) | hook | rc=1; `stamp_check: wiki/topics/live-state.md: '2026-09-23 09:49Z' is 29.1 min ahead …` | checked ✓ |
| C2-3 | a (bypass-committed) future stamp moved from the ledger to the incident log | hook | rc=1; `stamp_check: docs/INCIDENT-LOG.md: '2026-09-23 09:49Z' is 29.8 min ahead …` | checked ✓ (new in the second file) |
| C2-4 | slack, real clock: now+110 s / now+135 s | hook | rc=0 / rc=1 (`'2026-09-23T09:21:30Z' is 2.2 min ahead of the clock 2026-09-23T09:19:15Z`) | ✓ |
| C2-4 | slack, fixed clock 12:00:00Z: +119 s / +120 s / +121 s | CLI | rc=0 / rc=0 / rc=1 (`is 2.0 min ahead`) — inclusive boundary | ✓ |
| C2-5 | `12:3xZ`, `12:34Z`, `T12:34:56Z` at 12:00:00Z; all three at 13:00:00Z | CLI | rc=1 each (`30.0`, `34.0`, `34.9 min ahead`); rc=0 with `3 new stamp(s)` | ✓ |
| C2-6 | lowercase `z` (`14:0xz`, 2 h ahead) | CLI | rc=0, `0 new stamp(s)` | declared forms only |
| C2-7 | `+00:00` offset; ` UTC`; fractional seconds (`14:00:00.000Z`), all 2 h ahead | CLI | rc=0, `0 new stamp(s)` each | declared forms only |
| C2-7d | `T14:0xZ` (T + bucket) | CLI | rc=1 (`120.0 min ahead`) — checked though the docstring lists the bucket form with a space only | ✓ (docstring understates) |
| C2-8 | a future stamp inside a fenced code block | hook | rc=1 (`119.8 min ahead`) — the gate reads all text | by design |
| C2-9 | `2026-02-30`, `24:00Z`, `12:6xZ`, `12:4x:30Z` | CLI | rc=1 each, `names no valid instant` | ✓ |
| C2-9e | 5-digit year typo `20266-09-23 14:00Z` | CLI | rc=0, `0 new stamp(s)` (the look-behind blocks a match) | declared forms only |
| C2-10 | far-future year typo `2062-09-23 08:5xZ` | hook | rc=1 (`18934530.7 min ahead`) | ✓ |
| C2-11 | `git commit -a`, future stamp unstaged | hook | `GIT_INDEX_FILE=/tmp/vj10/c/repo/.git/index.lock`; rc=1 (`29.7 min ahead`) | ✓ |
| C2-12a | partial commit `git commit -m x -- todo/BUILD-TASKLIST.md` (index clean, worktree future) | hook | `GIT_INDEX_FILE=/tmp/vj10/c/repo/.git/next-index-13588.lock`; rc=1 — the gate's `git diff --cached`/`git show :path` read the temp index | ✓ |
| C2-12b | partial commit of `other.txt` while the real index holds a future ledger stamp | hook | `GIT_INDEX_FILE=…/next-index-13723.lock`; rc=0; the ledger stays staged — correct (the stamp is not in this commit) | ✓ |
| C2-13a | `git commit --amend` adding a future stamp | hook | rc=1 (`29.7 min ahead`) | ✓ |
| C2-13b | `--amend` when HEAD already holds the (bypass-committed) future stamp | hook | rc=0 — not re-judged (`scripts/stamp_check.py:90` `if stamp in head`) | by design |
| C2-14a | clean `git merge --no-ff side` (side = a bypass-committed future stamp) | hook | the wrapper logs `WRAP pre-merge-commit ran`, NOT pre-commit; rc=0; the merge commit carries the stamp | outside the gate (F-C1) |
| C2-14b | the same merge with the REAL hooks dir (pre-commit only; the repo ships no `pre-merge-commit`) | hook | rc=0, no gate ran | F-C1 |
| C2-14c/d | a CONFLICTED merge, resolved to side's line, then `git commit --no-edit` | hook | pre-commit ran; rc=1 (`'2026-09-23 10:05Z' is 44.6 min ahead`) | ✓ |
| C2-15 | `git cherry-pick` of the future-stamp commit | hook | no hook ran; rc=0 (`[master 42ffe0a] side-future`) | outside the gate (F-C1) |
| C-x1 | run outside a git repo | CLI | rc=1, `stamp_check: git diff --cached failed: error: unknown option \`cached'` + git's full usage text | fail-closed; exit list omits it (F-C6) |
| C-x2 | the ledger staged as a `120000` symlink to a file holding a future stamp | hook | rc=0, commit landed (a type change `T` is outside `--diff-filter=ACMR`, and the link text holds no stamp) | F-C2 |
| C-x3 | cost on the staged real ledger (771,658 bytes) | CLI | 0.13 s, 0.14 s, 0.13 s wall | ✓ |

Which hook a clean merge runs: `git help hooks` is absent on this minimized host (man pages removed; RelNotes empty). The git 2.43.0
binary's own `merge` option strings read `bypass pre-merge-commit and commit-msg hooks` / `control use of pre-merge-commit and commit-msg
hooks`, and the run above confirms it: pre-merge-commit, not pre-commit.

### C3 — the bypass
- `SKIP_STAMP_CHECK=1` + a future stamp + a vocabulary token planted in a listed gate (`scripts/safe_commit.sh`): commit rc=1;
  `pre-commit: SKIP_STAMP_CHECK set — the future-stamp gate bypassed.`, then the screen's violation line for the planted token
  (the throwaway `safe_commit.sh`, line 24, token `laya`) and `COMMIT BLOCKED by the never-a-gate screen (rc=3)`; HEAD unchanged.
  The bypass skips only its own gate. SOLID.
- `SKIP_STAMP_CHECK=0` also bypasses (the hook tests `-n`, `scripts/hooks/pre-commit:115` `SKIP_STAMP_CHECK`): rc=0, the future stamp landed, line printed (F-C3).
- Who sets it: `git grep` at 2ebd486 (incl. `harness-ports/` and `.claude/`) → only the hook (comment, `-n` test, echo), the assertion in
  `tests/test_stamp_check.py`, and prose (the ledger, the incident log, 2 brief/transcript files). The worktree (untracked included) adds
  nothing. This shell's env: `0` matches; shell init files: none. NOTHING sets it.
- PC lanes' `/proc/<pid>/environ`: **NOT run — the lanes run on the PC; no bridge use in this lane.**

### C4 — the clock
- `timedatectl` exists but cannot operate here: `System has not been booted with systemd as init system (PID 1). Can't operate.` No NTP status.
- OmniRoute's `Date:` on 127.0.0.1:20128: **NOT run — PC only.** Instead: HTTP GETs, headers only, with sub-second local stamps
  (`curl -D - -o /dev/null`; api.github.com answered `200 OK` with no Date line through the proxy):

  | source | Date | server − local |
  |---|---|---|
  | https://www.google.com | 09:21:14 / 09:21:15 | [-0.885, +0.326] / [-0.100, +1.077] s |
  | https://pypi.org/simple/ | 09:21:15 / 09:21:15 | [-0.420, +0.861] / [-0.857, +0.543] s |
  | https://www.cloudflare.com/ | 09:21:16 / 09:21:16 | [-0.432, +1.108] / [-0.761, +0.532] s |

  Intersection: the host clock is within **[-0.100, +0.326] s** of the three servers.
- Skew analysis: the gate compares a stamp with THIS host's clock + 120 s. A host clock AHEAD by `a` lets a stamp up to `a` + 120 s
  ahead of true time through. A host clock BEHIND by more than 120 s refuses a stamp pasted from ANOTHER correct clock (the PC's
  `date -u`, another machine's commit clock). A stamp pasted from this host's own `date -u` is never refused, whatever the skew: the gate
  enforces agreement with the host clock, not truth. Measured skew ≈ 0.3 s, so neither case applies here. PC-sandbox skew: NOT measured (no bridge).

### C5 — the fixture in `tests/test_shell_syntax.py` (scratch copy, sha 4ea0979cdfcc166c restored and verified)
| id | mutant | compiled / collected | result | killed by |
|---|---|---|---|---|
| C5-m1 | drop `stamp_check.py` from the copy list (`tests/test_shell_syntax.py:59` `for name in ("lint_delta.py"`) | ✓ / `4 tests collected` | `1 failed, 3 passed`; `can't open file '…/repo/scripts/stamp_check.py': [Errno 2] No such file or directory`; `COMMIT BLOCKED by the future-stamp gate (rc=2)` — the CI red 5f6919b fixed, reproduced | test_pre_commit_gate_positive_and_negative_controls (positive control) |
| C5-m2 | drop `no_laya_in_gates.py` from the copy list | ✓ / `4 tests collected` | `1 failed, 3 passed`; `can't open file '…/no_laya_in_gates.py'`; `COMMIT BLOCKED by the never-a-gate screen (rc=2)` | same |
| C5-m3 | drop the allowlist write | ✓ / `4 tests collected` | `1 failed, 3 passed`; `gate-file-missing: scripts/gate_files.txt`; `(rc=64)` | same |

- The negative control, run alone under C5-m1 (the mutated `_throwaway_repo`, `bad.sh` only): `rc=1 exact-reason=True missing-script=False
  :: COMMIT BLOCKED: bash -n failed on bad.sh — fix the syntax (unreachable tails count).` It fails for the EXACT reason, not for a
  missing script, because the shell-syntax gate runs before the stamp gate in the hook.
- The killer passes unmutated: `1 passed, 3 deselected in 0.42s`.
- The hook fails CLOSED on a missing gate script (python rc 2 → blocked).

### (C) finding inventory
- **F-C1 — FOLLOW-UP (SOLID).** A clean `git merge` runs `pre-merge-commit` (the repo ships none), and `git cherry-pick` runs no hook.
  A future stamp committed upstream with a bypass, `--no-verify` or a skewed clock lands through them. The same holds for the never-a-gate
  screen and every pre-commit gate, outside these hunks. Fix: a `scripts/hooks/pre-merge-commit` that execs pre-commit (closes clean
  merges); declare cherry-pick/rebase a limit.
- **F-C2 — FOLLOW-UP (SOLID).** A ledger-plane path staged as a symlink (a `T` change) is skipped whole (C-x2). This is (A)'s class in
  the stamp gate. Fix: include `T` in the filter and refuse a non-regular plane entry (reuse (A)'s mode check).
- **F-C3 — INFO.** Any non-empty `SKIP_STAMP_CHECK` bypasses, `=0` included; the documentation shows `=1`. Printed either way.
- **F-C4 — INFO.** Declared-scope confirmations: C2-1, C2-6, C2-7, C2-9e unchecked by declaration; C2-7d checked beyond the docstring's list.
- **F-C5 — INFO.** A future stamp anywhere in the text is refused, fenced code included (C2-8). A legitimately future deadline written as
  a date-prefixed stamp needs the printed bypass (by the contract's wording).
- **F-C6 — INFO.** The git-failure path exits 1 with git's full usage text as the message (C-x1). Fail-closed, but the docstring's exit
  list (`scripts/stamp_check.py:19-20`, `Exit 0 clean; 1 a new stamp`) omits it.
- **F-C7 — INFO.** "HEAD's stamps are never re-judged" is a whole-file substring test (`scripts/stamp_check.py:90`, `stamp in head`): a
  stamp committed once with the bypass can be re-copied freely in the same file (C2-13b). By design.
- **F-C8 — INFO.** Clock measured within 0.3 s; `timedatectl` inoperable here.
- **F-C9 — INFO.** Hook ordering: a stamp refusal exits before the never-a-gate screen runs, so a screen result stays hidden until the
  stamp is fixed.

### (C) predicate table
| finding | 1 contract | 2 canonical path | 3 material | 4 discriminator | 5 in boundary | BLOCKS? |
|---|---|---|---|---|---|---|
| F-C1 | no — the gate is wired into pre-commit (declared scope: staged content at commit time) | yes — real merge/cherry-pick | no, by itself — needs an upstream bypass/`--no-verify`/skew; no merges in this single-branch flow | yes — C2-14a/b, C2-15 | partial — a new hook file | no → FOLLOW-UP |
| F-C2 | no — symlinked plane files not addressed | yes — real hook | no, by itself — a deliberate symlink | yes — C-x2 | yes | no → FOLLOW-UP |
| F-C3-F-C9 | no / declared | yes where run | no | yes | yes | no (INFO) |

## D1 — the anti-pattern screen
- The brief's literal command, `python3 scripts/ap_screen.py --tests scripts/no_laya_in_gates.py scripts/stamp_check.py
  tests/test_no_laya_in_gates.py tests/test_stamp_check.py`: `--- TEST_SCREEN over 4 path(s): 0 hits over 4 files ---`, rc 0
  (`--tests` applies TEST_SCREEN to all four paths).
- The default AP_SCREEN over the two scripts: `--- AP_SCREEN over 2 path(s): 7 hits over 2 files ---`, all `AF-AP-40` in `_glob_structural`
  (`scripts/no_laya_in_gates.py:463-479`, `is_dir()`/`is_file()`), 0 in `scripts/stamp_check.py`.
- At 07ff690: the same seven lines, verbatim, at lines 141-157 (the same instrument over the 07ff690 blob) → all PRE-EXISTING; 0 new.
  `scripts/stamp_check.py` and `tests/test_stamp_check.py` did not exist at 07ff690 (0 hits now); the 07ff690 test file: 0 TEST_SCREEN hits.
- The one new `is_file()` (`scripts/no_laya_in_gates.py:234`, `return (self.root / rel).is_file()`, J1-0-R3's `_Tree.isfile`) is not an
  `if` guard, so AF-AP-40's signature (a presence-gated check) correctly does not match it.
- Instrument note: `scripts/ap_screen.py` changed between 5a00d13 and c269263 (not a boundary file); the runs above used the c269263/2ebd486 version.

## GATE RECOMMENDATIONS (one per component; the coordinator owns the gate)

- **(A) J1-0-R2 — `MERGE-READY-WITH-FOLLOWUPS`.** No qualifying blocker. A1 and A2 rows a, b2, c reproduced here through the real hook.
  Follow-up: F-A2, a committed FIFO/directory test; ma2 shows the untested branch prevents a hang. Depends on the PC draft's rows e
  and f, which were not re-run here.
- **(B) J1-0-R3 — `NOT-READY`: F-B1 and F-B2 meet the complete blocking predicate.** Both were reproduced through the real hook in this
  lane; nothing in this recommendation rests on unreproduced evidence. The ONE focused repair (D-031), keyed to J1-0-R3 + AMENDMENT 2 +
  the screen's digest a8a1e114d32c1528:
  - the scanner fails closed on an unterminated quote or heredoc and models nested `"$(…)"` quoting, heredoc delimiter words, `$'…'` and
    YAML `run:` values, so that BH-2 and YH-4 are refused, every F-B1 member is CAUGHT or refused, and the live screen stays clean;
  - `.claude/hooks/edit-snapshot.py` is listed, and the dynamic-import sentence is either backed by closing the loads or replaced by a
    measured, contract-amended limit;
  - proposed tests 1-5 are committed and green.

  The coordinator decides F-B2's path (code or amendment) and the F-B3 contract question (declare or close the spelling evasions) before
  the repair brief.
- **(C) the future-stamp gate — `MERGE-READY-WITH-FOLLOWUPS`.** C1-C5 reproduced; no finding meets the predicate. Follow-ups: F-C1
  (a pre-merge-commit hook; cherry-pick declared) and F-C2 (a symlinked plane file). C3's PC environment half and C4's OmniRoute `Date:`
  are NOT run (PC only).

## Evidence discipline — what was reproduced, what was read, what was skipped
- Reproduced (this lane, this session):
  - A1; A2 rows a, b2, c;
  - B1 (9 lines); B2 (43 shapes, each with a runtime); the live-tree desync map (PIN + worktree); BH-1/BH-2, YH-3/YH-4, ES, B4-1..4
    through the real hook; B3 (20 shapes, each with a runtime);
  - 24 mutants + 7 live differentials + the AF-AP-138 killer run;
  - 5 proposed tests run red + de-vacuous checks;
  - C1-C5, C-x1..3; D1.
- Read statically (not executed): the resolution-order comparison beyond the P-rows; the census of dynamic loads (grep + reading each
  site; each target path read from the code, not executed).
- Deliberately skipped:
  - the PC draft's rows d (symlink part), e, f and A3 — PC evidence, kept as drafted;
  - the docstring's exec-edge count 26/12 — not re-measured (F-B11);
  - the full-tree suite — not in this contract; the three boundary suites ran;
  - a thermo-nuclear full-stack pass — not in this brief;
  - /bug-echo and registry rows — the coordinator's step. Candidates: F-B1 (a lexical scanner that desyncs and then goes silent: fail-open
    by desync, a sibling of AF-AP-40's fail-open-by-omission) and F-B2 (a closure over import STATEMENTS misses dynamic loads, an
    AF-AP-120 sibling).
- NOT run (venue):
  - C3's `/proc/<lane pid>/environ` and C4's OmniRoute `Date:` — the PC, no bridge use;
  - the PC-to-sandbox clock skew.
- Cleanup: every tree under `/tmp/vj10/` was removed at the end (see the lane's final message). No write outside this report. The only
  git write in the shared repo was one `git fetch -q origin` (remote-tracking ref 2ebd486 → 1978e55; no index, worktree or branch
  change). The throwaway repos' commits never left `/tmp/vj10/`.
- report_lint (after 2 fix rounds of 3; `python3 scripts/report_lint.py --min-refs 15 <this report> --root .`, run `Wed Sep 23 09:38:19 UTC 2026`):
  `report_lint: 47 refs — OK 47, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`, rc 0.
