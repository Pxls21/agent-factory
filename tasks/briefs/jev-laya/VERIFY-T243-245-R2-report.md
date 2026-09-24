# VERIFY-T243-245-R2 report

Role: adversarial-verifier (sandbox, Opus 5.5), the verify of A's second repair (D-031, authorized by the coordinator
for R1-A-F1). The repair commit: "push_clean: the second repair (D-031) for R1-A-F1, every exit that does not push
puts the branch back; the AF-AP-145 third tell ignores an ignore (GATED-PENDING-VERIFY)". Started 2026-09-24 23:00:00Z
(`date -u`). Written incrementally.

## 0. Premise re-measure (first action) — HOLDS

```
$ for f in ...; do echo "$(git rev-parse --short=12 HEAD:$f) $(git hash-object $f | cut -c1-12) $f"; done
d514e2f0c095 d514e2f0c095 scripts/push_clean.sh
a4810d932d07 a4810d932d07 tests/test_stale_ids.py
386e2fe53b85 386e2fe53b85 .claude/hooks/edit-snapshot.py
471eb916e66f 471eb916e66f tests/test_edit_snapshot_ap_screen.py
464c72e88393 464c72e88393 scripts/stale_ids.py        (unchanged since R1)
d93f80149021 d93f80149021 scripts/ap_screen.py        (unchanged since R1: B's code)
914421579b49 914421579b49 tests/test_ap_screen.py     (unchanged since R1)
$ bash scripts/test_summary.sh tests/test_stale_ids.py   (twice)
pytest-summary: 20 passed in 13.45s
pytest-summary: 20 passed in 13.87s
$ bash scripts/test_summary.sh tests/test_edit_snapshot_ap_screen.py tests/test_ap_screen.py
pytest-summary: 201 passed in 1.46s
$ (the new tests/test_stale_ids.py against the first repair's push_clean.sh, blob 73fafef21fb1, in a scratch mirror)
1 failed, 19 passed in 11.66s   (red: test_a_failed_push_puts_the_branch_back_so_a_note_citing_a_listed_id_is_refused)
```

HEAD at measure: "ledger and wiki 22:5xZ: task #245 closed ..." (local e19256e), on top of the repair commit (local
47a5ff6); the working tree carries only the other verifier's untracked report.

## 1. Probes

Harness as in R1 (`$SCRATCH/vt243/`): throwaway repos with a bare origin and a green CI record, the REAL
`/home/user/agent-factory/scripts/push_clean.sh` (blob d514e2f0c095). Where a timing window must be widened, a `git`
shim on PATH (`r2_shims.py`) sleeps or commits and then execs `/usr/bin/git`; a wrapper `stale_ids.py` only delays the
check or commits, then execs the real checker. push_clean.sh itself runs unmodified in every probe.

### R2-0: step 2, the blocking probes on the second repair — all per contract

`r1_residual.push_failure` (a pre-receive hook rejects once, then a note cites the id the boundary listing printed),
`signal_mid_check` (SIGINT), `signal_term` (SIGTERM): all three per contract. `aprobes.sticky`, `a_sticky_after_rc2`,
`a_no_leak_exit3`, `aprobes.binary`: all per contract.

### R2-1: step 3, attacks on `back()`

| shape | outcome |
|---|---|
| a successful push, then the transcript sync's push is rejected (an export stub, a pre-receive that rejects the second push) | rc 0, `transcript sync: commit/push failed — code push above already succeeded`; origin holds the rewritten head; the local HEAD is the transcript commit on top of it; the reflog has no reset. No misfire |
| `--lanes-live`, a stale note | rc 4 twice; the branch untouched; one worktree; no WARNING |
| `--lanes-live`, a push the origin rejects once, then a note citing the listed id | rc 1, the branch untouched; the re-run refuses naming the listed id; origin at base |
| `--lanes-live`, a clean push | rc 0; the branch followed origin; the lane edit kept |
| TMPDIR with spaces; a relative TMPDIR | rc 4 (the stale note), the branch back on the pre-rewrite head, nothing left in TMPDIR |
| TMPDIR that does not exist; TMPDIR that is a file | rc 1 at `mktemp`, before the trap and the rewrite; the branch untouched |
| a commit landing between the rewrite and `HEAD_AFTER` (a shim commits right after filter-branch): the tree-mismatch path | rc 2, `TREE MISMATCH`, then `push_clean: the rewrite changed the tree; the branch stays on <id>: reconcile by hand`; the late commit stays on the branch |
| a first SIGINT during the check, then SIGINT or SIGTERM while `back()` runs its `update-ref` (a shim sleeps there) | the reset completes: the branch back on the pre-rewrite head (the `trap '' INT TERM` holds, and the shim child inherits the ignore) |
| a ref lock during a refusal (R1-A-F6) | rc 4 (was 128), the REFUSED line and `WARNING: the branch could not be put back ...` both printed; the branch stays rewritten; after the lock goes, a plain re-run pushes the stale note (rc 0) |
| a commit during the check (R1-A-F5) | rc 4 (the mapping fails: 2 before, 3 after), the WARNING, and the late commit stays on the branch (the old-value argument refused the reset) |
| a `.git/config.lock` or a lock on `refs/remotes/origin/feat` at push time | `git push` still exits 0 (only git's own `update_ref failed` line for the tracking ref): `PUSHED=1`, no reset, local == origin |
| exit statuses through the trap | `exit 4` stays 4 and an errexit stays 1 when `back()` ends on a failed command plus `echo` (bash preserves the status) |
| **a signal after filter-branch has moved the ref, before line 123 reads `HEAD_AFTER`** (a shim sleeps right after the real filter-branch returns; SIGINT and SIGTERM) | **the run dies (rc -2 / -15) with the branch LEFT REWRITTEN: `back()` sees `HEAD_AFTER` empty and returns; a plain re-run pushes the stale citation (rc 0, origin carries it)** |
| **a push that origin accepts while `git push` exits 1** (a shim runs the real push, then exits 1: a connection dropped after the remote's acceptance) | **rc 1; origin holds the rewrite, and `back()` puts the local branch back on the pre-rewrite commits (reflog `push_clean: not pushed; back on the pre-rewrite commits`). Every later run: `stale_ids: the range had 2 commits before the rewrite and 0 after; cannot map them`, rc 2, refused, `STALE_ID_OK` cannot override; a corrected note does not help. Way out by hand: `git rebase` onto origin (it drops the already-pushed commits)** |

The natural width of the first bold window, measured with `GIT_TRACE` timestamps (from filter-branch's
`update-ref -m "filter-branch: rewrite"` to the moment filter-branch returns, five runs each): 11.7-14.0 ms on a 10-file
tree; 42.3-261.8 ms on a 9,500-file tree (this repo's size), spent in the backup ref, `rm -rf "$tempdir"` and
`git read-tree -u -m HEAD`. The commit names "a signal in the microseconds between an exit and back's first line"; this
window is different and larger.

A candidate for it (a scratch mirror only): `back()` reads HEAD itself (`HEAD_AFTER=$(git rev-parse --verify -q HEAD)`
before the early-return line). 20 committed tests pass; the window probe, second signal, tree mismatch, concurrent commit
and success probes all pass.

### R2-2: step 4, mutation check (scratch mirrors of the HEAD blobs, one fresh copy per mutant, `ulimit -v 3000000`)

| mutant | committed tests | my probes not per contract (the window probe is red at the PIN, so omitted) |
|---|---|---|
| M1 drop the trap | KILLED 5 failed | push_failure, both signals, sticky, rc-2, exit-3 leak, second signal |
| M2 drop `PUSHED=1` | KILLED 3 failed | success_not_reset |
| **M3 drop the old-value argument** | **SURVIVED 20 passed** | concurrent_commit_kept |
| **M4 drop the tree-equality guard** | **SURVIVED 20 passed** | tree_mismatch_keeps_late_commit |
| M5 the tell counts an empty handler | KILLED 1 failed (`test_no_fire_on_exits_after_an_ignore_that_is_not_a_handler`) | - |
| **M6 drop the ignore in `back()`** | **SURVIVED 20 passed** | second_signal |
| M7 drop the `rm` in `back()` | KILLED 1 failed (the leak test) | exit-3 leak |
| M8 the ids file back in `/tmp` | SURVIVED 20 passed | - (not a defect by itself) |
| **M9 M7 + M8: a real leak into `/tmp`** | **SURVIVED 20 passed** | exit-3 leak |
| M10 `HEAD_AFTER` read before the rewrite | KILLED 4 failed | push_failure, both signals, sticky, rc-2, second signal |

M9 shows the leak test is vacuous against a regression that stops honoring TMPDIR: it checks only its private
directory, which stays empty when the file lands in `/tmp`. The M1, M7 and M9 runs leaked 117 files into `/tmp`
(23:10-23:13Z); I removed exactly those (no push_clean was live). The 26 unverified files from R1 (22:43Z) are untouched.

### R2-3: the leak test under concurrency, and the rest

- The private-TMPDIR leak test beside three concurrent loops of the other stale-id tests: 8 of 8 passed; no new `/tmp`
  files (R1-A-F3 closed).
- The AF-AP-200 row and `TestAFAP200` are byte-identical to the first round's PIN (the hook module changed only in the
  AF-AP-145 tell); `scripts/ap_screen.py` and `tests/test_ap_screen.py` are unchanged since R1. B and C are unchanged.
- `python3 scripts/ap_screen.py scripts/push_clean.sh`: AF-AP-145 0 (the commit's claim holds); AF-AP-175 4 (HEAD is
  resolved at lines 99, 118, 123, 124 and 145; the repair added the `HEAD_AFTER` read).
- Adjacent consumers, fresh: `pytest-summary: 469 passed in 33.95s` (7 files set=54d189eb56fb: the stale-id, ap_screen,
  ci_gate, hooks-worktree, shell-syntax, no-laya and edit-snapshot tests), matching the commit.

## 2. Finding inventory (no severity filter)

### Closure of R1's items for A

| R1 item | status | evidence |
|---|---|---|
| R1-A-F1 BLOCKER (a failed push, SIGINT/SIGTERM in the check, a failed `update-ref`) | CLOSED for the failed push and the signals in the check; the lock case is now loud (R2-A-F3) | R2-0, R2-1 |
| R1-A-F2 (rc-2 stickiness untested) | CLOSED (a committed test; M9 of R1 would die) | the new rc-2 test |
| R1-A-F3 (the leak test flaky in parallel) | CLOSED | R2-3 (8 of 8) |
| R1-A-F5 (an unconditional reset) | CLOSED (old-value argument) | R2-1, but untested (R2-A-F4) |
| R1-A-F6 (a failed reset loses the refusal) | CLOSED (rc 4, REFUSED and a WARNING) | R2-1 |
| R1-A-F4, A-F4 (`--text` memory; five surviving mutants) | OPEN, deferred to the follow-up issue by the commit | - |

### Remaining items (D-031 is spent for A: each is a follow-up or an owner decision)

**R2-A-F1 FOLLOW-UP — a signal after filter-branch moved the ref and before `HEAD_AFTER` is read leaves the branch
rewritten.** REPRODUCED with the window widened by a shim; the natural window is 12 ms (small tree) to 42-262 ms
(9,500 files). `back()` trusts the variable set at line 123 instead of HEAD. Outcome: A-F1's (a later plain run pushes
a stale note). Trigger: an interrupt landing inside that window. Fix: read HEAD inside `back()` (candidate verified,
R2-1).

**R2-A-F2 FOLLOW-UP (or owner decision on the tradeoff) — a push that lands while `git push` reports failure leaves
push_clean stuck.** REPRODUCED (a shim: the real push, then exit 1). `back()` treats it as not pushed and resets the
branch; every later run fails the mapping (rc 2, "cannot map"), `STALE_ID_OK` cannot override, and the refusal text
("Cite each commit ...") does not apply. Fail-closed: no stale note reaches origin. New with this repair (the first
repair left the branch on origin's head). Trigger: a connection dropped after the remote accepted. Fix: after a failed
`git push`, ask origin (`git ls-remote origin refs/heads/$BRANCH`) and treat a match with `HEAD_AFTER` as pushed; or
name the rebase recovery in the rc-2 refusal.

**R2-A-F3 FOLLOW-UP — after a failed reset the WARNING does not name the recovery.** A stale ref lock: rc 4, REFUSED, and
the WARNING, but the branch stays rewritten and a re-run (once the lock is gone) pushes the stale note. The WARNING
could say to run `git update-ref HEAD <HEAD_BEFORE> <HEAD_AFTER>` before running push_clean again. Exotic trigger.

**R2-A-F4 FOLLOW-UP — three of the repair's parts have no committed test:** the old-value argument (M3), the tree guard
(M4), the ignore in `back()` (M6). `r2_probes.concurrent_commit_kept`, `tree_mismatch_keeps_late_commit` and
`second_signal` are ready fixtures.

**R2-A-F5 FOLLOW-UP — the leak test is vacuous against a regression that stops honoring TMPDIR** (M9: a real leak into
`/tmp` survives). Fix: assert the ids file is created under the private TMPDIR (for example, a wrapper checker that
records its `--old` path), not only that the directory is empty afterwards.

**R2-A-F6 INFO — the refusal line says "the branch is back on its pre-rewrite commits" before `back()` runs;** when the
reset then fails, the WARNING follows and contradicts it.

**R2-A-F7 INFO — held under attack:** the three residual probes, sticky, rc-2, exit-3 leak, binary; a successful push
with a failing transcript sync (no misfire); `--lanes-live` refusal, failed push and success; TMPDIR with spaces,
relative, missing, or a file; a second signal during `back()`; the tree-mismatch path; a concurrent commit; config and
tracking-ref locks (git push still succeeds); exit statuses through the trap; the tell (M5 killed).

**R2-A-F8 UNVERIFIED — the 26 orphan `/tmp/push-clean-ids.*` files from R1 (22:43Z)** remain, origin unknown.

## 3. Gate recommendation

### A — the stale-id push check: **MERGE-READY-WITH-FOLLOWUPS**

This rests on classifying R2-A-F1 (an interrupt inside a 12-262 ms window) and R2-A-F2 (a push that lands while git
reports failure; fail-closed, then stuck until a rebase) as follow-ups: D-031 is spent for A, and neither is a normal
flow. If the owner wants R2-A-F2's tradeoff settled before merge, it is an owner decision, not a verify finding.

| predicate | R2-A-F1 (the filter-branch window) | R2-A-F2 (a push that lands while git reports failure) |
|---|---|---|
| 1 contract mapping | A.1 with A.6 (the reading A-F1 used) | none directly: A.5 is kept (it refuses); availability is not a contract item |
| 2 canonical reproduction | the real push_clean.sh; the window widened by a PATH shim; its natural width measured | the real push_clean.sh; the dropped connection simulated by a PATH shim |
| 3 material effect | a stale citation reaches origin, but only on an interrupt inside a sub-second window | no stale push; later pushes refused until a manual rebase |
| 4 concrete discriminator | `r2_probes.window_after_rewrite` (red at the PIN, green on the candidate) | the drop probe in `r2_attack4.py` |
| 5 task ownership | `scripts/push_clean.sh` | `scripts/push_clean.sh` |
| blocks? | no: follow-up (a narrow signal window; D-031 spent) | no: follow-up or owner decision (fail-closed, rare trigger) |

B and C: unchanged since R1 (B MERGE-READY-WITH-FOLLOWUPS, C MERGE-READY-WITH-FOLLOWUPS).

Standing rules kept: no commit, push, PR, comment, GitHub write or bridge call; no git write in the real repo (only
`git show`, `git archive`, `git cat-file`, `git rev-parse`, `git hash-object`, `git log`, `git diff`); gpu_window files
untouched; `.jev/intercept-off` untouched; mutants on scratch copies only, every mirror pytest under
`ulimit -v 3000000`; processes killed only by process-group id of my own probes; FAKE strings throughout.
