# VERIFY-T243-245-R1 report

Role: adversarial-verifier (sandbox, Opus 5.5), the re-verify after the one repair (D-031). The repair commit:
"push_clean, stale_ids, ap_screen: the one repair (D-031) for VERIFY-T243-245 A-F1, A-F2 and B-F1, with A-F3, A-F5
and B-F2..B-F5 (GATED-PENDING-VERIFY)". Started 2026-09-24 22:26:56Z (`date -u`). Written incrementally.

## 0. Premise re-measure (first action) — HOLDS

```
$ for f in ...; do echo "$(git rev-parse --short=12 HEAD:$f) $(git hash-object $f | cut -c1-12) $f"; done
464c72e88393 464c72e88393 scripts/stale_ids.py
73fafef21fb1 73fafef21fb1 scripts/push_clean.sh
745bf355091e 745bf355091e tests/test_stale_ids.py
d93f80149021 d93f80149021 scripts/ap_screen.py
914421579b49 914421579b49 tests/test_ap_screen.py
$ bash scripts/test_summary.sh tests/test_stale_ids.py tests/test_ap_screen.py   (twice)
pytest-summary: 31 passed in 10.97s
pytest-summary: 31 passed in 13.60s
$ bash scripts/pc_suite.sh set-id -- tests/test_stale_ids.py tests/test_ap_screen.py
2 files set=45d8dbf065f9
```

HEAD at measure: the repair commit (local 9bf084f); the working tree clean.

## 1. Probes

Harness as in the first report (`$SCRATCH/vt243/`): throwaway work repos with a bare origin and a green CI record,
driving the REAL `/home/user/agent-factory/scripts/push_clean.sh` (now blob 73fafef21fb1, calling stale_ids.py
464c72e88393) with cwd in the throwaway repo. Mirrors (`mut1.py`) copy the committed blobs at their repo paths; every
mirror pytest runs under `ulimit -v 3000000` (the new symlink fixture points at /dev/zero; see B-R1-F3).

### R0: the discriminator the repair commit claims (reproduced)

The new test files against the pre-repair scripts (`9bf084f^` blobs of push_clean.sh, stale_ids.py, ap_screen.py) in a
scratch mirror: `11 failed, 20 passed in 10.89s`, the eleven the commit names (the sticky refusal, the two notes, the
five binary shapes, Latin-1, the three B tests). The same mirror at HEAD: `31 passed in 10.56s`.

### R1: the blocking probes on the new blobs (all reproduced, all per contract now)

- A-F1 / P1: run 1 rc 4, the local HEAD is back on the pre-rewrite head, the refusal says `NOT pushed; the branch is
  back on its pre-rewrite commits`; run 2 unchanged: rc 4 again; origin at base.
- A-F1 / P2: two stale notes, one fixed (a commit carrying the trailer): run 2 rc 4 naming only `wiki.md`; run 3
  unchanged rc 4; both fixed: rc 0, and both ids the refusals named (`a78ffd8`, `da58744`) are commits on origin (A.6).
- P7a: a Latin-1 file with no citation: rc 0, no traceback, pushed (the false rc 1 refusal is gone).
- P7b: the failing textconv no longer runs (`--no-textconv`): the citation is found, rc 4 twice, origin at base.
- `aprobes.sticky`: per contract. `aprobes.binary`: per contract.
- A-F2, the six shapes: a NUL byte, `binary`, `-diff`, `core.bigFileThreshold=100`, a lossy textconv, a
  `diff.<driver>.binary` driver: all REFUSED rc 4 with `notes.md:1 cites <old> ... it is <new> on origin`.
- B-F1 (the script directly, `bmut.BPROBES`): rename, look-alike dir, index hit + tree fixed, index clean + tree hit,
  staged then removed: all per contract.

### R2: new attacks on the A repair (all reproduced through the real push_clean.sh unless marked)

| shape | outcome |
|---|---|
| `--lanes-live` (the repaired scripts committed in the throwaway repo; the reset hits the detached worktree HEAD) | run 1 rc 4; `refs/heads/feat` unchanged; one worktree (no leak); run 2 rc 4 with the same new id (b568296); the corrected note pushes, b568296 is on origin, the branch followed origin, the lane edit kept. Per contract |
| a branch other than PUSH_BRANCH checked out (`side`, PUSH_BRANCH=feat) | `side` reset to its pre-rewrite head; the local `feat` untouched; the re-run refuses. Per contract |
| a detached HEAD, PUSH_BRANCH=feat | the detached HEAD reset; `feat` untouched; the re-run refuses. Per contract |
| an unborn branch (`git checkout --orphan`) | rc 128 at `git rev-list --count` (before the rewrite, before the temp file); no leak |
| `refs/original` after a refusal | `refs/original/refs/heads/feat` == HEAD == the pre-rewrite head; `git status` clean; the next run's `filter-branch -f` replaces the backup. No interaction |
| the reflog after a refusal | the reset's entry has an EMPTY message (`update-ref` without `-m`): the reflog does not say why the branch moved back. Cosmetic |
| the exit-3 path (push_clean run from a subdirectory) | rc 3, no temp file leaked (A-F5 closed on this path) |
| **the push fails after a passing check** (a pre-receive hook in the bare origin rejects once) | run 1 rc 1 (`FAKE rejection (once)`), and the branch is LEFT REWRITTEN; run 1's boundary listing printed the PRE-rewrite ids (`d4af412 the fix`). A note written next, citing d4af412, then a plain re-run: **rc 0, no stale_ids line, origin carries d4af412, which does not exist on origin** |
| **SIGINT to the process group during the check** (a wrapper `stale_ids.py` that sleeps 4 s, then execs the real checker; the note citing the old id is already in the range) | the run dies (rc -2), the branch is left rewritten; the temp file is removed (the EXIT trap ran); a plain re-run: **rc 0, origin carries the stale citation** |
| **SIGTERM to the process group during the check** | the same: rc -15, the branch left rewritten, no leak; a plain re-run: **rc 0, origin carries the stale citation** |
| **`update-ref` cannot lock the ref** (the wrapper creates `.git/refs/heads/feat.lock`; the real checker then refuses rc 4) | errexit stops the script at `git update-ref`: **rc 128, the refusal message is never printed**, the branch is left rewritten; the lock removed, a plain re-run: **rc 0, origin carries the stale citation** |
| a commit lands during the check (a wrapper commits `late.txt`, then execs the real checker) | the checker sees 3 commits against 2 recorded, rc 2, refused; the unconditional `git update-ref HEAD "$HEAD_BEFORE"` moves the branch back past the late commit: it is no longer on the branch (reachable only from the reflog), `late.txt` shows as staged-added. `--no-delegates-live` forbids concurrent writers, so this is hypothetical |

Mechanism of the four bold rows (primary source, `scripts/push_clean.sh`): the reset
(`git update-ref HEAD "$HEAD_BEFORE"`) runs only in the stale-id refusal branch. Every other exit after filter-branch
has moved the branch (a failed `git push` under errexit, a signal, an errexit inside the refusal branch itself) leaves
the branch rewritten, exactly A-F1's state: the next run records the rewritten ids as OLD_IDS, rewrites nothing, and
`stale_ids.py` returns 0 before it reads the diff. The wrappers in the signal, lock and concurrent rows simulate the
ENVIRONMENT (a slow check, a stale lock, a concurrent writer); push_clean.sh and the real checker run unmodified.

### R3: `--text` (line numbers, cost), measured on the real checker

push_clean's exact filter-branch invocation (read from the script) run by hand in a throwaway repo, then the real
`stale_ids.py` alone (time, peak RSS of the child via `getrusage`), at the PIN and at the pre-repair blob:
- Line numbers: a citation on line 5 of a modified text file reads `notes.md:5` at the PIN and before the repair
  (unchanged); a citation on line 3 of a binary file (NUL bytes on line 1) reads `bin.dat:3` at the PIN (the
  pre-repair checker never saw it).
- Cost: a 100 MB random binary: PIN 6.65 s, peak 936 MB (pre-repair 0.17 s, 204 MB); 100 MB of zeros with no newline:
  3.52 s, 311 MB (0.15 s, 105 MB); 50 MB of `a` with no newline (text to git either way): 1.25 s, 161 MB both. Memory
  is about nine times the size of a random binary in the range. The largest blob in this repo's whole history is
  7.2 MB (`tasks/briefs/pc/patch-pc-b7.md--c439580.diff`), so this is latent here; a 1 GB binary would need about
  9 GB on this 15 GB sandbox.

### R4: new attacks on the B repair

Through a real `git commit`, a byte-identical pre-commit (ddcf5707a3fc) and the real ap_screen.py (d93f80149021),
unless marked.

| shape | screen output | commit |
|---|---|---|
| B-F1a: the index holds the AF-AP-145 shape, the tree was fixed after staging | `AF-AP-145: 2` (the committed blob) | lands |
| B-F1b: the index clean, the tree holds a hit | silent | lands |
| B-F1c: staged with hits, then removed from the tree | `AF-AP-145: 2` | lands |
| only mode, `git commit -- run.sh` with `other.sh` staged | run.sh only (the temp index) | lands |
| `git commit -a` | the committed file | lands |
| a typechange T (a `.sh` symlink replaced by a script with hits) | `AF-AP-145: 2` (B-F2 closed) | lands |
| a staged symlink `link.sh -> sandbox-kit/v.sh` | silent (the target string) | lands |
| a file named `:odd.sh` | screened | lands |
| a file name with a newline | screened | lands |
| a non-UTF-8 file name (`caf\xe9.sh`), UTF-8 mode and `PYTHONUTF8=0 LC_ALL=C.UTF-8` | screened, the raw byte printed | lands |
| `GIT_LITERAL_PATHSPECS=1` exported for `git commit` | screened (B-F4 closed) | lands |
| 300 staged `.sh` files with hits | 600 hits, 2.88 s wall | lands |
| a conflicted `.sh` (index stages 1-3, status U) run directly | U is outside ACMRT: skipped, the other staged file screened; `git commit` refuses before the hook (`fatal: Exiting because of an unresolved conflict`) | refused by git |
| **a file named `1:run.sh`, with `ok.sh` also staged with hits** | **a traceback: `git show :1:run.sh` reads as STAGE 1 of `run.sh` and fails (128); the loop dies, so `ok.sh`'s hits are not printed either** | lands |
| **a gitlink (mode 160000) named `mod.sh`, with `ok.sh` staged with hits** | **a traceback: `git show :mod.sh` fails (128); `ok.sh`'s hits are not printed** | lands |

The two bold rows are new with the repair: the old tree read screened `1:run.sh` and skipped a gitlink directory
with an OSError, so neither lost the other files' output. The tracked tree holds 0 names with a colon and 0 gitlinks
today.

### R5: mutation check of the new tests (scratch mirrors of the HEAD blobs, one fresh copy per mutant, the 31 committed tests under a 3 GB cap)

| mutant | committed tests (31) | my probes not per contract |
|---|---|---|
| M1 drop the `update-ref` | KILLED 2 failed (the sticky test, the two-notes test) | sticky, rc-2 stickiness |
| M2 drop `--text` | KILLED 4 failed (NUL, `binary`, `-diff`, bigFileThreshold) | binary |
| M3 drop `--no-textconv` | KILLED 1 failed (textconv) | - |
| M4 drop surrogateescape | KILLED 1 failed (Latin-1) | - |
| M5 read the tree, not the blob | KILLED 2 failed (the staged-blob test, the symlink test) | the three B-F1 probes, symlink |
| M6 follow symlinks | KILLED 1 failed (the symlink test) | symlink |
| M7 restore the `*.sh` pathspec | KILLED 1 failed (the pathspec-env test) | `GIT_LITERAL_PATHSPECS` |
| **M8 drop T from the filter** | **SURVIVED 31 passed** | typechange |
| **M9 reset only on rc 4** (`if [ "$src" = 4 ]; then git update-ref ...; fi`) | **SURVIVED 31 passed** | rc-2 stickiness (a blob the diff needs moved aside, run 1 rc 2, the blob restored, run 2 must refuse) |
| M10 the EXIT trap removed | KILLED 1 failed (the leak test) | exit-3 leak |
| M11 `HEAD_BEFORE` read after the rewrite | KILLED 2 failed | sticky, rc-2 stickiness |

The first round's five A-F4 mutants (`--no-ext-diff`, `--no-color`, the 40-character maximum, `STALE_ID_OK` rescuing any
rc, `-U0`) still survive all 31 tests (re-run here); the repair commit defers them to a follow-up issue.

### R6: the leak test under concurrency, and orphan files

`test_the_old_ids_file_never_leaks` asserts `set(Path("/tmp").glob("push-clean-ids.*")) <= before`, a GLOBAL set.
Beside three concurrent loops of the other test_stale_ids tests (separate pytest processes, as xdist workers are),
the leak test failed 6 of 8, 3 of 6 and 5 of 8 runs in three experiments: another run's transient file is alive at its
final glob. CI runs serially (`python -m pytest tests/ -q`), but `scripts/pc_suite.sh`, the default gate venue, runs
`-n $WORKERS`. Not run on the exact consumer (no bridge; xdist is not installed in the sandbox).

26 `/tmp/push-clean-ids.*` files (mtimes 22:43:41-22:43:52Z, 2-4 ids each) appeared during my first concurrency
experiment. Two exact repeats (with the basetemp repos kept for matching) leaked none; the 26 files' ids are not
commits in the real repo or in `/tmp/pytest-of-root`, and that experiment's basetemps were already deleted. Origin
UNVERIFIED; I left the files in place (they may not be mine). A run of the 17 other tests in isolation leaked none.

### R7: the residual triggers against a candidate (a scratch mirror only; nothing written to the repo)

Probes (`r1_residual.py`, True = the stale note never reaches origin): a push that fails after a passing check; SIGINT
during the check; SIGTERM during the check. At the PIN: all three False. A candidate that moves the reset into the EXIT
trap (`PUSHED=0` before the trap; the trap resets `HEAD` to `HEAD_BEFORE` unless `PUSHED=1`; `PUSHED=1` after
`git push`): all three True, the 31 committed tests `31 passed in 8.61s`, and sticky, rc-2 stickiness, the exit-3 leak
and binary probes per contract.

### R8: adjacent consumers, fresh at the current HEAD (cbc35bf)

`bash scripts/test_summary.sh tests/test_stale_ids.py tests/test_ap_screen.py tests/test_ci_gate.py
tests/test_hooks_worktree.py tests/test_shell_syntax.py tests/test_no_laya_in_gates.py
tests/test_edit_snapshot_ap_screen.py` -> `pytest-summary: 466 passed in 32.46s` (7 files set=54d189eb56fb; the commit's
463 predates "edit-snapshot: AF-AP-145's third tell ...", which added hook tests).

## 2. Finding inventory (no severity filter)

Evidence levels: REPRODUCED (a command in this run, through the real script), STATIC (read from primary source).

### Closure of the first round's findings

| first-round finding | status at the PIN | evidence |
|---|---|---|
| A-F1 BLOCKER (a refusal is not sticky) | CLOSED for the refusal exit (rc 4, and rc 1/rc 2) | P1, P2, P7b, sticky, rc-2 stickiness; red on the pre-repair blob |
| A-F2 BLOCKER (binary / diff-reshaping configs) | CLOSED | the six shapes REFUSED; `bin.dat:3` found |
| A-F3 (non-UTF-8 false refusal) | CLOSED | P7a rc 0; the Latin-1 test |
| A-F4 (five surviving mutants) | OPEN, deferred by the commit | R5 |
| A-F5 (temp file leaks) | CLOSED on the exit-3 path and a signal; exit 2 by inspection | R2, `a_no_leak_exit3` |
| B-F1 BLOCKER (tree read) | CLOSED | R1, R4 (three shapes through real commits) |
| B-F2 (typechange) | CLOSED, but untested (M8 survives) | R4, R5 |
| B-F3 (symlink followed) | CLOSED | R4 |
| B-F4 (pathspec env) | CLOSED | R4, M7 killed |
| B-F5 (rename, look-alike untested) | CLOSED (tested now) | the new rename/look-alike test |

### A — the stale-id push check

**R1-A-F1 BLOCKER — A-F1's root cause remains on the exits the reset does not cover: a failed push, a signal, a
failed `update-ref`.**
- Evidence: REPRODUCED (R2 bold rows, R7). Canonical: the real push_clean.sh at the PIN; a real git pre-receive
  rejection on the bare origin; the signal and lock rows use a wrapper that only delays the check or creates the lock.
- Mechanism: `git update-ref HEAD "$HEAD_BEFORE"` runs only inside the stale-id refusal branch. A `git push` that fails
  under errexit, a SIGINT/SIGTERM, or errexit on the reset itself exits with the branch rewritten, which is A-F1's
  state: the next run rewrites nothing, and `stale_ids.py` returns 0 before it reads the diff.
- Material effect: a stale citation reaches origin, rc 0, no warning. The realistic trigger: the push fails after a
  passing check (this sandbox's proxy can cut a transfer; the pre-push hook can block on a VENDORED-MANIFEST drift;
  origin can move), and a note written before the re-run cites an id from that failed run's own boundary listing,
  which prints the PRE-rewrite ids (R2: `d4af412 the fix`). The signal trigger needs an interrupt inside the check's
  window (0.1-2 s); the lock trigger needs a stale ref lock.
- Contract mapping: A.1 with A.6, the same reading as A-F1 (the push that lands delivers the rewrite that replaced the
  cited id). `--lanes-live` does not have it (a failed inner run never moves the branch).
- Discriminator: `r1_residual.push_failure` / `signal_mid_check` / `signal_term`: all red at the PIN, all green on the
  candidate in R7 (31 committed tests green).
- Ownership: `scripts/push_clean.sh` (the trap line and one `PUSHED=1` after `git push`).
- D-031: the first repair closed the trigger I reported (the refusal) but not the root cause. A second repair needs
  the coordinator's explicit authorization; otherwise this is an honest BLOCKED decision for the owner.

**R1-A-F2 FOLLOW-UP — two stickiness gaps in the committed tests.** M9 (reset only on rc 4) survives all 31 tests: no
test re-runs after an rc 1 or rc 2 refusal. The `a_sticky_after_rc2` probe (a blob moved aside for run 1, restored for
run 2) is a ready fixture.

**R1-A-F3 FOLLOW-UP — the leak test is flaky wherever push_clean runs in parallel** (R6: 3-6 of 8 red). A false red,
never a false green; test-only. Fix: key the check to the test's own run (for example, the test's range ids in the
leftover file's content), not a global `/tmp` set difference. Not reproduced on `pc_suite.sh -n 8` itself.

**R1-A-F4 FOLLOW-UP — `--text` costs about 9x a random binary's size in memory** (100 MB: 936 MB peak, 6.65 s). Latent:
the largest blob in the repo's history is 7.2 MB.

**R1-A-F5 FOLLOW-UP — the reset is unconditional.** A commit landing during the check is moved off the branch
(reachable only from the reflog; its file shows as staged). `--no-delegates-live` excludes concurrent writers, so this
is hypothetical. Fix: `git update-ref HEAD "$HEAD_BEFORE" <the rewritten head>` (compare-and-swap).

**R1-A-F6 FOLLOW-UP — a failed reset loses the refusal message.** errexit stops at `git update-ref`: rc 128, not 4, and
no `REFUSED` line (R2 lock row). The candidate in R7 moves the reset into the trap and prints a message on failure.

**R1-A-F7 INFO — the reset's reflog entry has an empty message** (`update-ref` without `-m`).

**R1-A-F8 INFO — held under attack:** `--lanes-live` (the worktree HEAD reset; the branch untouched; the same new id
twice; the correction pushes); a branch other than PUSH_BRANCH; a detached HEAD; an unborn branch (rc 128 before the
rewrite, no leak); `refs/original` equals the restored head and does not interact; the six A-F2 shapes; line labels
under `--text` (text line 5 unchanged, binary line 3 found); the refusal's claim "the next run gives the same ids"
(P2, A1).

**R1-A-F9 UNVERIFIED — 26 orphan `/tmp/push-clean-ids.*` files of unknown origin** (R6).

### B — the staged-shell screen

**R1-B-F1 FOLLOW-UP — one staged entry `git show :<path>` cannot print aborts the whole screen.** A file named
`1:run.sh` (`:1:run.sh` reads as stage 1 of `run.sh`) or a gitlink named `mod.sh` raises CalledProcessError: a
traceback, and the hits of every other staged file (`ok.sh`) are not printed; the commit lands. New with the repair
(the tree read screened `1:run.sh` and skipped a gitlink). Loud, never blocking, and exotic: 0 tracked names with a
colon and 0 gitlinks in the repo. Fix: address stage 0 explicitly (`:0:<path>`) or read the blob ids from
`git ls-files -s -z`, skip mode 160000, and catch per entry.

**R1-B-F2 FOLLOW-UP — the typechange is untested:** M8 (drop T) survives all 31 tests; `b_typechange` is a ready fixture.

**R1-B-F3 FOLLOW-UP — the symlink test's fixture is a memory hazard.** `zero.sh -> /dev/zero`: a regression to
following symlinks reads /dev/zero with no cap (the pre-repair script, M5 and M6 did; under my 3 GB cap they died with
MemoryError). On a 15 GB sandbox or with 8 PC workers, that regression can starve other processes before the test's
60 s timeout. A link to a regular file with AF-AP-145 hits discriminates "followed" by hits, with no hazard.

**R1-B-F4 INFO — held under attack:** B-F1's three shapes through real commits; only mode; `commit -a`; typechange;
a vendored symlink; `:odd.sh`; a newline name; a non-UTF-8 name in UTF-8 and strict locale modes; the pathspec env for
`git commit`; a conflicted `.sh` (U is outside ACMRT; git refuses the commit before the hook); 300 files in 2.88 s.

### C — the AF-AP-200 tell (unchanged)

**R1-C-F1 INFO — C's subject is byte-identical to the first round's PIN:** the AF-AP-200 row and `TestAFAP200` match
`fd6d5d54a3df` and `bc4e48d7d29f`. The hook module changed around it ("edit-snapshot: AF-AP-145's third tell ...",
blob 02d75a470750); `tests/test_edit_snapshot_ap_screen.py` passes (`187 passed`). C-F2 (header parses the tell does
not name; `scripts/jev_echo.py:84`) stays a follow-up.

## 3. Gate recommendations

### A — the stale-id push check: **NOT-READY** on R1-A-F1 (this depends on judging material a failed push followed by a note citing an id from that run's boundary listing; if the coordinator judges that compound trigger immaterial, A is MERGE-READY-WITH-FOLLOWUPS; D-031: a second repair needs explicit coordinator authorization)

| predicate | R1-A-F1 (the branch left rewritten on a non-refusal exit) |
|---|---|
| 1 contract mapping | A.1 with A.6, the reading A-F1 used |
| 2 canonical reproduction | the real push_clean.sh at the PIN; a real pre-receive rejection (R2, R7) |
| 3 material effect | a stale citation reaches origin, rc 0, silent; the trigger is compound (a failed push, then a note citing a pre-rewrite id) |
| 4 concrete discriminator | three residual probes red at the PIN, green on a 3-line candidate (31 committed tests green) |
| 5 task ownership | `scripts/push_clean.sh` |

Follow-ups: R1-A-F2..F6 and A-F4.

### B — the staged-shell screen: **MERGE-READY-WITH-FOLLOWUPS** (B-F1..B-F5 closed; R1-B-F1..F3 are follow-ups)

| predicate | R1-B-F1 (exotic names abort the screen) | R1-B-F3 (the /dev/zero fixture) |
|---|---|---|
| 1 contract mapping | B.1 | none: a test-hygiene hazard |
| 2 canonical reproduction | yes: a real commit through the hook | the committed test against M5/M6 |
| 3 material effect | exotic triggers only (0 in the repo); a loud traceback; the commit lands | only if the guarded regression returns |
| 4 concrete discriminator | yes | yes |
| 5 task ownership | `ap_screen.py` | `tests/test_ap_screen.py` |
| blocks? | no (fails 3: hypothetical input, loud) | no (fails 1 and 3) |

### C — the AF-AP-200 tell: **MERGE-READY-WITH-FOLLOWUPS** (unchanged; follow-up C-F2)

Standing rules kept: no commit, push, PR, comment, GitHub write or bridge call; no git write in the real repo (every
git write ran in throwaway repos under `$SCRATCH/vt243/runs/`, and the only repo reads were `git show`, `git archive`,
`git cat-file`, `git rev-list`, `git ls-files` and `git log`); `scripts/gpu_window.sh` and its tests untouched;
`.jev/intercept-off` neither created nor removed; mutants on scratch copies only, every mirror pytest under
`ulimit -v 3000000`; no process killed except my own probe process groups (by pid); FAKE strings for the trailer and
the refusal reasons.
