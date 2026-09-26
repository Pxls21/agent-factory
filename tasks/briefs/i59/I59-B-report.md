# I59-B: report (task #313), sandbox build lane, Opus 5.5

**Status: DONE in the sandbox, NOT committed (this lane makes no git writes). REVIEW-PENDING: the coordinator lands R and
T with the batch re-mint (#315). S0-05 is NOT re-minted, so `validate-ledger integrity` reads S0-05 INVALID until then.**
Final section written 2026-09-26 09:3xZ. Brief `tasks/briefs/i59/I59-B-brief.md` (PIN 7a050b6; origin head 59229eb
at start). R = `proofs/S0-05/tools/pc/run_s0_05_units.sh`, T = `tests/test_s0_05_egress.py`.

## 0. RESULT

- [x] Item 1 (F-6): limit 8 and the A2'' block say what the census admits (an END state equal to a pure append by the
  same holders, whatever happened between the snapshots), name the three let-throughs and say why containment holds.
  The census code is byte-identical. T's limit-8 docstring agrees. One test pins the named let-throughs.
- [x] Item 2 (F-2): a pid-reuse test (a built first snapshot, with an unbuilt control) kills M1 as a FAILED test.
- [x] Item 3 (F-3): an O_RDWR-only holder test kills M4 as a FAILED test.
- [x] Item 4a: the guard refuses a root inside any git work tree (exit 73, named reason, nothing written), also as root
  on a clone another uid owns. It kills G1 (guard removed) and G2 (a `git rev-parse` guard).
- [x] Item 4b: under sudo, the handback runs on the run's own end, on an `exit` it takes, and on INT, TERM and HUP. It
  follows no link and leaves a hard-linked file as it was. The invoking user deletes the root without sudo. Kills H1,
  H2, H3.
- [x] Item 4c: without sudo the run is as before (a root run keeps root-owned entries and prints no handback line; a
  non-root run with SUDO ids exits 2 as before).
- [x] Item 5: census verdicts, checker, canaries and committed evidence untouched; no re-mint.
- [x] Item 6: one driver in scratch, for the PC (section 5). `control` and `2j-deleted` measured here (plain holders);
  the fork, thread and namespace shapes were NOT run here.
- [!] DEVIATION-1: under sudo, an evidence root that already exists is refused (exit 74). Section 6.
- [!] DISCREPANCY-1: the brief's raw `iptables-save | sha256sum` check cannot hold (a timestamp and live counters).
  Section 7.

## 1. PREMISE (re-measured 2026-09-26 08:3xZ, the sandbox tree, uid 0)

Every line of the brief's premise block matches. Origin head is 59229eb (the brief's PIN 7a050b6); no commit touches
S0-05's files or T since ff7a671 or since 7a050b6.

```
$ git log --oneline ff7a671..HEAD -- proofs/S0-05/ tests/test_s0_05_egress.py | wc -l      -> 0
$ git log --oneline 7a050b6..HEAD -- proofs/S0-05/ tests/test_s0_05_egress.py | wc -l     -> 0
$ (the brief's R grep)   84 EVIDENCE_ROOT  86 egress_ns_capable  227 limit 7  246 limit 8  293 O_WRONLY, os.O_RDWR
                         360 w[:2]  468 mkdir -p  476 cleanup()  497-499 trap  599 scratch=  690 census compare
$ (the brief's T grep)   93 netns_capable  99 NEEDS_NETNS  1705 e3dir  3346 _census_leg  3609/3621 limit 8
                         3615/3684/3744 test_a2pp_*
$ grep -l -E 'run_s0_05_units|s0_05' tests/*.py -> tests/test_edit_snapshot_ap_screen.py tests/test_s0_05_egress.py
$ (as root) a repo owned by uid 65534: git -C <clone>/sub rev-parse --is-inside-work-tree; echo rc=$?
fatal: detected dubious ownership in repository at '<scratch>/premise/clone'
rc=128
$ git config --global --get-all safe.directory | wc -l   -> 0    (system scope: 0)
$ sha256sum R T (HEAD bytes, before any edit)
6c1dee427b5b1d0c4f93a34a5f97535b2e07468f713d279f0b50f8557d1cd5bb  proofs/S0-05/tools/pc/run_s0_05_units.sh
9fccff03cfc23a1abebcd1704166e269442ae89927ee2da2fb9dc555ab84da77  tests/test_s0_05_egress.py
```

Venue facts measured for the design (sandbox): `fs.protected_hardlinks` = 1, `fs.protected_symlinks` = 0; no `.git`
entry at /, /tmp, /home, /home/user or the scratch path's ancestors; bash exits 127 on R's `${1:?usage}`; a failing
command in an EXIT trap leaves the exit status as it was (`exit 3` stays 3, a natural end stays 0); bash runs the EXIT
trap on SIGHUP, SIGPIPE, SIGUSR1 and SIGALRM too (a shell's `$?` then reads 129, 141, 138, 142; Popen reads -1 for
HUP), so a step inside `cleanup` covers those exits; `fchownat(fd, "", uid, gid, AT_EMPTY_PATH)` on an
`O_PATH|O_NOFOLLOW` descriptor changes exactly the pinned inode (a symbolic link's own owner, never its target's),
while `fchown` on such a descriptor fails with EBADF.

## 2. FILES AND LINES TOUCHED (working tree, new-side line numbers)

R: 848 lines (was 737), sha256 b6780a867b67aceb3d85c8d16830a65cc145603c041cb99b9a178a3ac511efd9.
- R:63-74 item 1: `A2'' lets one kind of end state through`, the three named let-throughs, `Containment` and why.
- R:91-127 items 4a and 4b: the guard (`EVIDENCE_REAL`, the `.git` walk, `exit 73`), then sudo mode: `HANDBACK` is set
  only with EUID 0 and SUDO_UID set; malformed SUDO ids `exit 64`; an existing root under sudo `exit 74` (DEVIATION-1).
- R:278-291 item 1: the A2'' block, `The census now tells ONE end state`, `whatever happened between them`.
- R:292-425 the census function `_s0_01_census() {`: UNCHANGED, 134 lines, sha256 3f02ca397d32… (the verifier's
  value, cut by the same markers at HEAD and now; it was R@59229eb:247-380, `_s0_01_census() {`).
- R:515-576 item 4b: `_handback() {` (O_PATH|O_NOFOLLOW per entry, `fchownat` AT_EMPTY_PATH, the `st_nlink != 1` and
  device checks, one summary line on stderr).
- R:577-579 the `cleanup` comment now names the handback; R:592 `[ -z "$HANDBACK" ] || _handback` is its last step.
- R:608-609 `mkdir -p "$EVIDENCE_ROOT"` moved below the traps (it was R@59229eb:468, `mkdir -p "$EVIDENCE_ROOT"`,
  above them) (DEVIATION-2).

T: 4295 lines (was 3762), sha256 cf0ba1cd5f3591242fa34fa0c0692b482a7f7dc56df784bd27f6b5a6d7e90271.
- T:1757-1762 `_secret_free_environ` also drops `SUDO_*` (DEVIATION-3).
- T:3621-3623 the test_a2pp_a_log docstring: `limit 8 (the census admits an end state equal to a pure append`. The
  T:3610 comment `declared limit 8: the unit's own append` agrees and is unchanged.
- T:3765-4295 the I59-B block: helpers (`_census_function` cuts R's census from R's bytes at run time; `CENSUS_CALL`
  calls it as R does; `SHAPER`; `_work_tree`; `_git_free_environ`; `_entries`; `INVOKER`; `NEEDS_ROOT`) and 22 tests:

| test (line) | item | venue | what it proves |
|---|---|---|---|
| `test_i59b_f2_a_pid_reused_with_another_start_time_is_another_holder` (T:3893) | 2 | any uid | first snapshot built: holder pid kept, start 1 tick earlier: `changed`; the unbuilt control: `appended` |
| `test_i59b_f3_a_holder_that_opened_the_file_o_rdwr_only_and_appends_is_appended` (T:3935) | 3 | any uid | fdinfo read here: `[O_RDWR]` only; `appended`, the holder on both sides |
| `test_i59b_f6_limit_8_the_end_states_the_census_lets_through_are_named` (T:3956) | 1 | any uid | truncate-rewrite, restore-byte, restore-mode: `appended` (middle states read back: 0, "X", 0600); keep-mode control: `changed` |
| `test_i59b_an_evidence_root_inside_a_git_work_tree_is_refused_before_anything_is_written` x5 (T:4027) | 4a failure | any uid | below the top, the top, via a symlink, 3 levels not made yet, a `.git` file: exit 73, exact stderr, no entry changes |
| `test_i59b_the_refusal_holds_as_root_on_a_clone_another_user_owns` (T:4053) | 4a boundary | root | git exits 128 `detected dubious ownership` (asserted); R still exits 73; the clone unchanged |
| `test_i59b_an_evidence_root_outside_every_work_tree_runs_as_before_without_sudo` (T:4079) | 4a normal, 4c | netns | via a symlink, into a root that holds a foreign file: runs to its checker; entries root's; no handback line |
| `test_i59b_under_sudo_the_evidence_goes_back_to_the_invoker_and_nothing_outside_changes` (T:4137) | 4b normal + boundary | netns, real leg | own end; hard link left and named; links handed back, targets untouched; outside unchanged; invoker deletes the root |
| `test_i59b_the_handback_runs_on_an_exit_the_runner_takes_itself` x2 (T:4190) | 4b, 4c | netns | `exit 1` (census failed): handed back under sudo; root's without |
| `test_i59b_the_handback_runs_when_a_signal_stops_the_run` x3 (T:4216) | 4b | netns, real leg | INT 130, TERM 143, HUP -1: every entry the invoker's, nothing of the leg left |
| `test_i59b_under_sudo_an_existing_root_or_a_bad_id_is_refused_before_anything_is_written` x5 (T:4248) | DEVIATION-1 | root | exit 74: an empty dir, a dir with a foreign entry, a symlink to one; exit 64: gid "staff", no gid; nothing changes |
| `test_i59b_a_non_root_run_that_carries_sudo_ids_runs_as_before` (T:4283) | 4c | root | uid 65534, with and without SUDO ids, into an existing root: exit 2, the same line, nothing written |

Why the census tests call R's function, not a leg: F-2 needs a first snapshot that a test builds (`compare` reads it on
fd 3 as data, R:800, `census_changed=$(_s0_01_census compare`), and F-3/F-6 need no namespace. They cut the function
from R's bytes at each run, so a mutant of R is what they run (M1, M4 killed). F-2's built snapshot is the REAL `snap`
of the tree with one value moved: relay.log's holder keeps its pid and gets a start time one tick earlier. A real reuse
records that shape (a departed holder, pid P and an earlier start time, then a new process with pid P); `compare` only
compares the first snapshot's pids, it never looks them up. A real reuse is item 6's 2c (the PC).

## 3. GATES (pasted; the final bytes, R b6780a867b67aceb…, T cf0ba1cd5f359124…, hashed before each run)

```
$ bash -n proofs/S0-05/tools/pc/run_s0_05_units.sh                                                  -> rc 0
$ python3 -m pyflakes tests/test_s0_05_egress.py <scratch>/mutate.py <scratch>/item6_driver.py       -> rc 0
$ LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>   -> 0 for R, T, this report, mutate.py, item6_driver.py
$ printf '%s\n' tests/test_s0_05_egress.py | sort | sha256sum | cut -c1-12      (pc_suite.sh's own set_id pipeline)
9f0502080347
$ bash scripts/test_summary.sh --basetemp=/tmp/i59b-bt/f1 tests/test_s0_05_egress.py      (09:17:02Z-09:21:06Z)
pytest-exit: 0
pytest-summary: 297 passed in 243.14s (0:04:03)
$ bash scripts/test_summary.sh --basetemp=/tmp/i59b-bt/f2 tests/test_s0_05_egress.py      (09:21:11Z-09:25:13Z)
pytest-exit: 0
pytest-summary: 297 passed in 241.66s (0:04:01)
$ printf '%s\n' tests/test_edit_snapshot_ap_screen.py tests/test_s0_05_egress.py | sort | sha256sum | cut -c1-12
c05fbc3b558e
$ bash scripts/test_summary.sh --basetemp=/tmp/i59b-bt/f3 tests/test_edit_snapshot_ap_screen.py tests/test_s0_05_egress.py
pytest-exit: 0                                                                             (09:25:22Z-09:29:24Z)
pytest-summary: 494 passed in 241.83s (0:04:01)
```

- The floor was 275 passed (set 9f0502080347); 297 = 275 + the 22 new tests. The two T runs agree.
- An earlier gate trio (08:56Z-09:09Z: 297, 297, 494) ran before the AF-AP-70 fix in `SHAPER` (below); superseded.
- After the final gates: `ip netns list` 0 lines; veth 0; `/etc/netns` and `/run/s0-05-egress` empty; route_localnet
  nonzero 0; nat PREROUTING rules 0; no helper process left.
- iptables, the stable form (comments dropped, counters masked): 0528d077bca3781a… before the gates and after. The raw
  sha256: 4358c3af… before my first run, 2cdd3077… after the final gates (DISCREPANCY-1).
- The non-root venue (CI's shape), `setpriv --reuid=65534 … python3 -m pytest … -k i59b -rs`: `8 passed, 14 skipped,
  275 deselected in 1.68s`; each skip carries its declared reason (NEEDS_NETNS or NEEDS_ROOT).
- `scripts/ap_screen.py` over R and T, whole files: the same 53 hits as HEAD's bytes. One new AF-AP-70 tell (a `stat`
  then an `open` in `SHAPER`, a false positive) was removed by reading the mode through a fresh descriptor.
- `python3 scripts/validate-ledger integrity --root .` (read only): `S0-05 INVALID`, and the one mismatch is
  `attestation-mismatch: S0-05 proofs/S0-05/tools/pc/run_s0_05_units.sh`. Expected: R is attested; #315 re-mints.

## 4. MUTANT KILL TABLE (the final bytes; harness `<scratch>/mutate.py`, mirror `/tmp/i59b-mut`)

The mirror is a `git archive HEAD` of what T needs plus the working-tree R and T. Per mutant: one exact edit of R (its
anchor occurs once), `bash -n` rc 0, every Python heredoc of R parses, the killers collect, the killers run. A kill
needs a named killer FAILED and no error (AF-AP-223); the unmutated pool ran first: `BASELINE (17 ids): rc=0 :: 17
passed in 7.89s`.

| mutant | killed by (FAILED) | run | the failing assertion |
|---|---|---|---|
| M1 holders by pid only (`w[:2]` -> `w[:1]`) | test_i59b_f2 | 1 failed in 0.49s | `census["changed"] == ["relay.log"]`: the reuse read as appended |
| M4 O_RDWR dropped from `holders()` | test_i59b_f3 | 1 failed in 0.43s | `census["appended"] == ["rdwr.log"]`: appended was `{}` |
| G1 the guard removed | the 5 refusal cases + the boundary test | 6 failed in 1.81s | `runner.returncode == 73`: got 1, the run went on |
| G2 a `git rev-parse` guard, its failure read as outside | the boundary test ONLY | 1 failed, 5 passed in 0.52s | `runner.returncode == 73`: got 1 (dubious ownership) |
| H1 the handback removed | HB-1, HB-2 under-sudo, HB-3 INT/TERM/HUP | 5 failed in 7.01s | every entry stayed (0, 0) |
| H2 a handback that follows a symbolic link | HB-1 | 1 failed in 1.86s | `_entries(outside) == untouched` |
| H3 a handback that changes a hard-linked file | HB-1 | 1 failed in 1.89s | `_entries(outside) == untouched` |
| P1 (extra) DEVIATION-1's refusal removed | the 3 existing-root cases | 3 failed in 0.97s | `runner.returncode == 74`: got 1 |
| E1 (extra) sudo mode without the EUID 0 test | the non-root test | 1 failed in 0.18s | exit 74 where the run before said exit 2 |

G2 passing the five ordinary refusal cases shows that the boundary test (a clone another uid owns) is the one that
tells a git-based guard apart. HB-1's boundary assertion is ordered before the ownership checks, so H2 and H3 fail on
"something outside changed", the property they break.

## 5. ITEM 6: THE DRIVER (scratch, never committed)

`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/i59b/item6_driver.py`: 304 lines, sha256
92c85fd9cd560f15dc8e0eddcf6f24dfe8a22034dc8d1e621a71cb545744cbf9, pyflakes clean. It cuts `_s0_01_census` from R at run
time and refuses (exit 2) unless it is 134 lines with sha256 3f02ca397d32… (checked here: a copy of R one byte off is
`REFUSED`, rc 2). Each shape runs over its own scratch tree; holders are its own processes, stopped by pid.

PC commands (as rocco, no sudo, from the PC clone at any commit from ff7a671 on: the census bytes are the same):

```
sha256sum /tmp/i59b-item6.py        # 92c85fd9cd560f15dc8e0eddcf6f24dfe8a22034dc8d1e621a71cb545744cbf9 (the copied driver)
python3 /tmp/i59b-item6.py --runner proofs/S0-05/tools/pc/run_s0_05_units.sh \
    control 2j-deleted 2j-zombie 2j-thread 2j-leader-exits 2i-bind-over-itself 2i-bind-elsewhere; echo rc=$?
unshare -r -p -f --mount-proc python3 /tmp/i59b-item6.py --runner proofs/S0-05/tools/pc/run_s0_05_units.sh \
    control 2c-pid-reuse; echo rc=$?
```

The 2i shapes start their holder under `unshare -r -m` themselves; 2c needs the driver in its own pid namespace (it
sets `ns_last_pid` there, and only there, to make a real pid reuse).

Expected lines (P a pid, S a start time, C the comm, `<w>` the driver's temp dir; the first line reads `:247-380` at a
commit before I59-B lands):

```
census proofs/S0-05/tools/pc/run_s0_05_units.sh:292-425 lines=134 sha256=3f02ca397d32092d39935146ee587cc48f069be63492611f469c474502772501
control census=appended before=[[P, S, 'C']] after=[[P, S, 'C']] contract=appended verdict=right |
2j-deleted census=changed before=[[P, S, 'C']] after=None contract=changed verdict=right | holder's descriptors ['<w>/2j-deleted/base/.markers/relay.log (deleted)']
2j-zombie census=changed before=[[P, S, 'C']] after=None contract=changed verdict=right | holder pid P state Z at compare
2j-thread census=appended before=[[P, S, 'C']] after=[[P, S, 'C']] contract=appended verdict=right | descriptor opened by tid T of pid P; leader state S; tasks ['P', 'T']
2j-leader-exits census=changed before=[[P, S, 'C']] after=None contract=appended verdict=fail-closed | descriptor opened by tid T of pid P; leader state Z; tasks ['P', 'T']
2i-bind-over-itself census=appended before=[[P, S, 'C']] after=[[P, S, 'C']] contract=appended verdict=right | holder's descriptor reads ['<w>/2i-bind-over-itself/base/.markers/relay.log'] from the driver's namespace
2i-bind-elsewhere census=changed before=None after=None contract=appended verdict=fail-closed | holder's descriptor reads ['<w>/2i-bind-elsewhere/elsewhere/relay.log'] from the driver's namespace; <w>/2i-bind-elsewhere/elsewhere/relay.log is absent in the driver's namespace (the bind is the holder's only)
rc=0
census proofs/S0-05/tools/pc/run_s0_05_units.sh:292-425 lines=134 sha256=3f02ca397d32…
control census=appended … verdict=right |
2c-pid-reuse census=changed before=[[P, S1, 'C']] after=[[P, S2, 'C']] contract=changed verdict=right | first pid P start S1; second pid P start S2
rc=0
```

Verdict per shape under the contract, and the tier of each prediction:
- control, 2j-deleted: MEASURED in the sandbox (both `right`; 2j-deleted's holder descriptor read `… (deleted)`).
- 2j-zombie `right` (INFERRED: a zombie has closed its descriptors; T's `leave` holder, reaped only after the census,
  already gives exit.log `changed`).
- 2j-thread `right` (INFERRED: threads share one descriptor table, listed under /proc/<pid>/fd).
- 2j-leader-exits `fail-closed` (INFERRED: the leader drops the table at its own exit, so /proc/<pid>/fd lists
  nothing). `appended` would also be right: the process still holds the file. Neither is a hole.
- 2i-bind-over-itself `right` (INFERRED: the same path string, the same device and inode).
- 2i-bind-elsewhere `fail-closed` (INFERRED from d_path: the descriptor reads the holder's own path, which is not under
  .markers). F-8's class: a holder of the path's inode the census cannot bind to a path of the tree.
- 2c-pid-reuse `right` (INFERRED: R:405's exact `w[:2]` compare, pid and start time; T's F-2 test proves the census
  side).
A `WRONG` line (the census admits what the contract says it must name) or `NOT-PRODUCED` (the shape did not happen,
for example no user namespace) makes rc 1; a setup error prints NOT-PRODUCED with its reason (that branch is untested).

## 6. DEVIATIONS (loud)

- DEVIATION-1 (item 4b, sudo only). The brief says the handback takes "every entry under the evidence root". Over a
  root that already exists, that includes entries this run never wrote: `sudo R /tmp` would hand everyone's /tmp
  entries to the invoking user. So under sudo the root must be a new path: an existing one is refused before anything
  is written (exit 74, named), and malformed SUDO ids are refused (exit 64, like `S0_05_UNIT_USER`). Everything under
  the root at exit is then this run's. The dated root of the E3 recipe (E3-report section 8) is new on each run.
  Tested by T:4248, `an_existing_root_or_a_bad_id_is_refused` (5 cases); P1 killed. The coordinator may drop it; the
  handback's own boundary checks stay either way.
- DEVIATION-2. `mkdir -p "$EVIDENCE_ROOT"` moved from above the traps to below them, so the root is made under the
  EXIT trap and the handback covers it on every exit. Without sudo nothing changes: that window held only variable
  assignments and the trap lines.
- DEVIATION-3. T's `_secret_free_environ` drops `SUDO_*`, so a runner test run by a sudo-launched pytest cannot
  inherit the handback (SUDO_* became an input of R). No existing test used them.
- DEVIATION-4. F-2, F-3, F-6 and the five guard refusal cases carry no skip marker: they need no root, so CI's non-root
  job runs them too (measured as uid 65534 above). A new marker `NEEDS_ROOT` (a true reason) sits beside NEEDS_NETNS.
- DEVIATION-5. F-6 (item 1) also got a behaviour test, beside the docstring edits the brief named: it pins the three
  named let-throughs, as T:3621 does for `The unit's own append to the same file passes too`.
- DEVIATION-6. Item 6's `2j-deleted` ran in the sandbox: a plain holder and an unlink, neither fork, thread nor
  namespace. The six fork, thread and namespace shapes did NOT run here.
- DEVIATION-7. Scratch outside the scratch dir: the mutation mirror `/tmp/i59b-mut` and pytest basetemps under
  `/tmp/i59b-bt` (uid 65534 must traverse the mirror, and `/tmp/claude-0` is 0700). Both deleted at the end.
- DEVIATION-8. The handback also leaves an entry on another filesystem (a mount point under the root, not descended),
  beyond the contract's two named properties. Untested (NOT-done).
- The kill table has two extra mutants (P1, E1) beyond the brief's list.

## 7. DISCREPANCIES

- DISCREPANCY-1. `iptables-save` prints `# Generated by … on <time>` and live chain counters (`:PREROUTING ACCEPT
  [302:48381]`), so `iptables-save | sha256sum` changes every second and cannot equal its earlier value. Before my first
  run: 6 non-comment lines, raw 4358c3af…; at every later check, the same 6 lines (the nat table, 4 policy lines,
  COMMIT) and no rule. I compare `iptables-save | grep -v '^#' | sed -E 's/\[[0-9]+:[0-9]+\]$/[n:n]/' | sha256sum`,
  recorded 08:51Z after my first focused run: equal before and after every gate.
- DISCREPANCY-2. The sandbox exports GIT_CONFIG_COUNT=3 with GIT_CONFIG_KEY_0..2 and GIT_CONFIG_VALUE_0..2;
  `_secret_free_environ()` drops the KEY names (they contain "KEY") and keeps COUNT and the VALUEs, so `git` under that
  environment dies (`error: missing config key GIT_CONFIG_KEY_0`). My guard tests use `_git_free_environ` (no GIT_*,
  HOME set, no system file), which is also what sudo's env_reset leaves a root run.
- DISCREPANCY-3. My premise note first said HUP ends with 129: that is a shell's `$?`. Popen reports -1 (the signal);
  the test expects `-signal.SIGHUP`.
- DISCREPANCY-4. S0-05 reads INVALID in the ledger integrity check (section 3) until #315 re-mints; the brief forbids
  re-minting here.
- DISCREPANCY-5. R's usage exit (`${1:?}`) is 127 in bash, not the 64 R uses for its other usage errors (unchanged).

## 8. NOT-done

- No git writes: nothing committed or pushed. S0-05 not re-minted (INVALID until #315).
- Item 6: 2c, 2i x2, 2j-zombie, 2j-thread and 2j-leader-exits NOT run (the brief keeps them off the sandbox): the PC
  commands and predicted lines are in section 5. The driver's NOT-PRODUCED-on-error branch is untested.
- The handback's other-filesystem branch, its per-entry error branch and its RecursionError branch have no test.
- The census `exit 1` for a CHANGED tree was not run under sudo; it is the same `exit` inside the same EXIT trap as the
  census-failed exit that T:4190 runs, `the_handback_runs_on_an_exit_the_runner_takes_itself`.
- A signal other than INT or TERM that arrives DURING the handback (HUP, QUIT) can stop it part way: `cleanup`
  ignores INT and TERM only (E3-R1's design, kept by item 5). SIGKILL runs no trap (named in R's comment).
- A parent that `mkdir -p` makes ABOVE the root keeps its root owner (the brief: nothing outside the root changes), so
  the invoker can empty such a root but not remove it. The recipe's `/home/rocco/s0-05-evidence` was probably made by
  the 2026-09-23 sudo run and is root-owned (UNVERIFIED: no PC access); if so, one owner command fixes it for good:
  `sudo chown rocco: /home/rocco/s0-05-evidence`.
- No PC or bridge use (the brief).

## 9. SELF-ATTACK (the three likeliest ways this is wrong)

1. The guard misses a work tree. It finds work trees as git's discovery does (a `.git` directory or file in the root or
   above, after resolving links). It cannot see a work tree with no `.git` entry at all (`--git-dir`/`--work-tree`, a
   `core.worktree`, `GIT_DIR` in the environment), and it does not refuse a bare repository. Ruled out for AF-AP-169's
   shape (a clone): 5 path shapes plus the dubious-ownership case tested; G1 and G2 killed. Residual named here.
2. The handback changes something outside the root. Each entry is opened `O_PATH|O_NOFOLLOW` relative to its
   directory's descriptor, and its owner changes on that pinned inode (`fchownat` AT_EMPTY_PATH), so no path is looked
   up twice and no link is followed; a non-directory with more than one link is left. It runs after every namespace
   is destroyed (T's destroy test proves the unit processes die). Tested with a hard link to a root file and links to
   a root file and directory; H2 and H3 killed on "outside changed". Residual: a unit process that left its network
   namespace (its own user namespace) could still race the walk; the pinned-inode design leaves it only the run's own
   inodes to swap.
3. The census tests mirror the code. They run R's own function bytes (a mutant of R is what runs: M1, M4 killed). F-2's
   first snapshot is built, not a real reuse: the unbuilt control proves the moved start time is the one reason, and
   the real reuse is 2c on the PC. F-6 pins end states; each shape's middle state is read back (size 0, byte "X",
   mode 0600), so the shapes did happen.

## 10. EVIDENCE TIERS

- VERIFIED (measured this lane): the premise; the gates; the kill table and each kill's assertion; the guard's
  refusals, including as root on a 65534-owned clone; the handback's owners, the link and hard-link boundary and the
  invoker's delete; the non-root venue run; `control` and `2j-deleted` through the driver and its refusal of a wrong
  census; the stable iptables form; the ledger integrity reading; bash's EXIT trap on HUP, PIPE, USR1 and ALRM; the
  `fchownat` AT_EMPTY_PATH semantics.
- INFERRED: the item-6 predictions for 2c, 2i x2, 2j-zombie, 2j-thread, 2j-leader-exits; that sudo's env_reset passes
  no GIT_* to a root run.
- ASSUMED: unprivileged user namespaces work on the PC (Fedora's default); `/home/rocco` holds no `.git` (if it did,
  the recipe's root would be refused, correctly); the ownership of `/home/rocco/s0-05-evidence`.

## 11. LINE-CHECKED CITATIONS (one ref per line; `scripts/report_lint.py` summary in section 12)

- R:63 opens declared limit 8: `A2'' lets one kind of end state through`.
- R:99 resolves the root: `EVIDENCE_REAL=$(readlink -m -- "$EVIDENCE_ROOT")`.
- R:103 finds a work tree: `if [ -e "$_dir/.git" ] || [ -L "$_dir/.git" ]; then`.
- R:106 is the guard's `exit 73`.
- R:117 enters sudo mode: `if [ "$EUID" -eq 0 ] && [ -n "${SUDO_UID:-}" ]; then`.
- R:124 is DEVIATION-1's `exit 74`.
- R:280 rewords A2'': `The census now tells ONE end state`.
- R:292 opens the unchanged census: `_s0_01_census() {`.
- R:338 keeps O_RDWR in `holders()`: `not in (os.O_WRONLY, os.O_RDWR)`.
- R:405 compares holders by pid and start time: `[w[:2] for w in held]`.
- R:525 opens the handback: `_handback() {`.
- R:531 changes an owner on the pinned inode: `libc.fchownat(fd, b"", uid, gid, 0x1000)`.
- R:540 leaves a hard-linked file: `st.st_nlink != 1`.
- R:550 never follows a link: `os.O_PATH | os.O_NOFOLLOW, dir_fd=sub`.
- R:592 runs it last in cleanup: `[ -z "$HANDBACK" ] || _handback`.
- R:609 makes the root under the traps: `mkdir -p "$EVIDENCE_ROOT"`.
- R@59229eb:468 made it above them: `mkdir -p "$EVIDENCE_ROOT"`.
- T:1762 drops sudo's variables: `not k.startswith("SUDO_")`.
- T:3622 agrees with limit 8: `limit 8 (the census admits an end state equal to a pure append`.
- T:3780 cuts R's census at run time: `def _census_function`.
- T:3893 is `def test_i59b_f2_a_pid_reused_with_another_start_time_is_another_holder`.
- T:3935 is `def test_i59b_f3_a_holder_that_opened_the_file_o_rdwr_only_and_appends_is_appended`.
- T:3956 is `def test_i59b_f6_limit_8_the_end_states_the_census_lets_through_are_named`.
- T:4053 is `def test_i59b_the_refusal_holds_as_root_on_a_clone_another_user_owns`.
- T:4137 is `def test_i59b_under_sudo_the_evidence_goes_back_to_the_invoker_and_nothing_outside_changes`.

## 12. ADJACENT (reported, not fixed; outside items 1-6)

- `_secret_free_environ()` (T:1757) filters variable NAMES: it keeps `GIT_CONFIG_VALUE_*` while dropping their KEYs.
  A secret-valued setting under an innocuous name (a git `http.extraHeader`, for one) would reach the runner's
  environment; and any git call under that environment fails (DISCREPANCY-2). A registry candidate: a filter that drops
  one half of a paired protocol (COUNT/KEY/VALUE).
- Two root-owned dirs from 2026-09-23 13:10Z (`/tmp/e3-5t328okv`, `/tmp/e3-nw8nn6mk`: E3-era runner tests that did not
  reach their teardown) sit in /tmp. Not this lane's; left in place.
- The brief's host check hashed a tool's output that carries a timestamp (DISCREPANCY-1): a registry candidate for
  briefs ("hash the stable form of an instrument's output").
- The E3 recipe (E3-report section 8) does not yet say that under sudo the root must be a new path; its dated path
  already is. The recipe is outside this boundary.

`report_lint: 58 refs — OK 56, NEAR 0, MISS 0, UNCHECKABLE 2, UNRESOLVED 0 (worktree)` (`scripts/report_lint.py <this report> --map R=… --map T=… --min-refs 20`, rc 0; the two
UNCHECKABLE refs are the verbatim expected-output lines of section 5, which carry no claim token by design).
