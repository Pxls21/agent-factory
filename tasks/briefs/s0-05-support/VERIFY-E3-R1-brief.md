# VERIFY-E3-R1 — the targeted verify of the S0-05 runner's second-signal cleanup and content census (task #185)

PIN: the post-push SHA of the local landing commit "E3-R1 landed (task #175; GATED-PENDING-VERIFY): …"; the dispatch prompt names
it. Read it with `git log --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf -8` and match the subject.
COMPONENT: `proofs/S0-05/tools/pc/run_s0_05_units.sh` (PC, the runner) and `tests/test_s0_05_egress.py` (T). The builder's report
`tasks/briefs/s0-05-support/E3-R1-report.md` is an INPUT TO ATTACK, not a truth. BATCHED (item 10): the coordinator's fix of the
same class in the Qwen matrix runner, `harness-ports/bin/qwen-matrix.sh` (M) and `harness-ports/tests/test_qwen_matrix_sh.sh` (MT),
landed as local 2fd0a7d ("qwen-matrix.sh: a second signal cannot abort the baseline restore (task #176, …)"); the dispatch prompt
names its post-push SHA.
LANE: verify-e3-r1 (sandbox, uid 0: the root-only tests need netns, veth and iptables; agent `adversarial-verifier` on the D-054 pin,
in the SHARED tree, no worktree isolation). Honey `full`: line-bounded findings, evidence anchors, SOLID/UNSURE. Do NOT spawn
subagents.

WHY THIS LANE EXISTS: E3-R1 is GATED-PENDING-VERIFY (rule 0f). Its gates were the builder's own 13 tests, its own 13 mutants and its
own window probe; the coordinator re-ran the suite, which is a second run of the same oracle. The runner removes host state on the
owner's PC (network namespaces, veth pairs, `/etc/netns/<ns>`, D-051's DNAT rule, `route_localnet`) and runs there under the owner's
sudo: a cleanup that can still be cut short leaves that state behind, and a census that passes a changed S0-01 tree lets a leg pass
that should fail.

CONTRACT (frozen): R1-R3 of `tasks/briefs/s0-05-support/E3-R1-brief.md` (A2' is R2's quoted block), graded against VERIFY-E3's F3
and A2 findings in `tasks/briefs/s0-05-support/VERIFY-E3-report.md`. The builder changed the design of R1 on a measurement (its D1:
the one-line ignore alone aborted cleanup in 26 of 60 trials at a 100 µs gap; the ignore in each stop handler too gave 0 of 360) and
added one behaviour beyond A2' (its D2: a census that cannot be taken fails the leg). Attack whether both are TRUE and SOUND, not
whether they match the brief's older words. KNOWN, filed as issue #39: F1, F4-F18, F20, and F19 apart from its limit-2 part.

## Items (report EVERY observation; no severity filter; rank downstream)

1. PREMISE. Re-measure on the PIN: the PC and T blob ids and line counts, the trap lines, the census functions' line map (by grep),
   and one full root run of T with its set id. A mismatch that changes an item is CONTRACT-INVALID for that item; say which.
2. R1 by NEW signal shapes, never the builder's b, c and natural-end cases: a double INT (an operator's double Ctrl-C, pid-directed
   and group-directed); a third signal; INT then TERM with no gap and with a 1 ms gap; a signal while cleanup waits on each of its
   OTHER steps (the unit reap, `ip netns del`, the owner-record removal, the census compare); SIGHUP and SIGQUIT (a closed terminal:
   R1 names INT and TERM only, so say what the runner does and whether the leftover state matters). Every case through the REAL
   runner in its own session, asserting the same leftover set the builder's tests assert.
3. R1, the microsecond window. The builder's handler-only mutant (M1b) has no deterministic killer; its window probe is statistical.
   Try to build a DETERMINISTIC way to open the window (for example: stop bash with SIGSTOP between the two signals, queue both, then
   SIGCONT; or a ptrace/strace-injected delay at the trap dispatch). If one exists, is M1b then killed, and could it be a committed
   test? If none exists, say what you tried and what you measured.
4. R1, the cost of ignoring. Every child cleanup starts inherits the ignore. If one of them hangs (a stuck `ip netns del`, an
   `iptables` that waits on its lock, a unit that ignores TERM), can the operator still stop the run without SIGKILL, and is cleanup's
   time bounded anywhere? Reproduce a hung child through a PATH shim and say what the operator sees and what state is left after
   SIGKILL. A stop that cannot be stopped is a finding even when the contract does not name it.
5. R2, the census, with NEW shapes: a file replaced by a FIFO, a socket or a device node of the same name; a hard-link count change
   (declared not compared: is that declaration true and visible?); an xattr change (the same); a mode-only change; a file changed and
   changed back between snap and compare (never observable: say so); the tree changed WHILE the census walks (a writer running
   during `snap`); `.markers` itself replaced by a symlink between snap and compare; a 3,000-deep directory chain (recursion); a
   500 MB file (time); an entry the census cannot read. For each: named, passed, or failed-closed, and whether that is right.
6. D2, the census that cannot be taken. Does the leg fail with the printed line, before the checker, and does cleanup still run to its
   end? Is there any census failure that still reads as a pass (an exception swallowed, an empty side, a truncated file)?
7. The tests themselves: does a failing test leave host state behind (a netns, a veth, a rule, a changed `route_localnet`) that the
   next test or the next run inherits? Kill one test mid-way (SIGKILL the pytest process during a root test) and measure the leftover,
   then say whether T cleans it at the next start.
8. R3: every comment and declared limit that describes cleanup, the traps, R4 and the census against what the code does (limit 2, the
   new limit 7, the comments above cleanup, the traps and the compare).
9. MUTANTS (new; never the builder's M1-M10): in scratch copies under `/tmp/ve3r1/mut/` only. At least one per contract line, each on a
   line the builder's rows did not touch. Each compiles (`bash -n`, and the census heredoc compiles) and the suite collects
   (AF-AP-78); before you count a kill, run the killing test on the UNMUTATED copy and paste that it passes (AF-AP-138).
10. THE MATRIX RUNNER (task #176, the coordinator's own fix, never self-accepted). M's cleanup began with `trap - EXIT INT TERM`
   (INT/TERM back to the DEFAULT action), so a second signal during cleanup killed bash before the restore and left the owner's
   model-server unit in a matrix cell's configuration. The fix uses E3-R1's two ignores. MT's three new cases send a second TERM
   0.3 s after the first signal (TERM, INT) or after the run's own failure, while cleanup reads a padded baseline env. Attack it
   the same way as R1 (new shapes, never MT's three), through the REAL `harness-ports/bin/qwen-matrix.sh` with MT's fakes: a second
   signal during the GPU sampler's kill and wait, during the restore install itself, during the post-restore sha check; a double
   INT; SIGHUP. Is the 0.3 s delay against a padded env a sound discriminator, or can it pass for the wrong reason (say how you
   would know)? Does the ignore make a hung restore install unstoppable, and what then? Run `harness-ports/tests/run-all.sh` once.
   Report M's findings under their own heading; the gate recommendation covers PC/T and M/MT separately.
11. GATES: T as root twice and as nobody once, each command with its output and the set id (`bash scripts/pc_suite.sh set-id --
   tests/test_s0_05_egress.py`); `bash -n` on PC; the final host census (no netns, no veth, the nat PREROUTING chain empty,
   `/etc/netns` empty, `/run/s0-05-egress` empty, `route_localnet` 0 everywhere) pasted at the end.

## Boundary

CREATE `tasks/briefs/s0-05-support/VERIFY-E3-R1-report.md` (write it incrementally from the start); nothing else in the repository.
M and MT are read and run only; every mutant of them lives under `/tmp/ve3r1/mut/` like the rest.
Every mutant, shim and scratch tree lives under `/tmp/ve3r1/` and is removed at the end, and every namespace, veth, rule and
`route_localnet` change you make is undone before you finish (paste the final census). The sandbox had about 1.4 GB free at
authoring. pytest: `-p no:cacheprovider --basetemp=/tmp/ve3r1/bt<n>` (create the parent first), removed after each run. Other
sandbox agents work in this tree on disjoint files: `src/agent_factory/decisions/`, `tests/test_decisions_*.py`,
`tasks/briefs/laya/`, `tasks/briefs/continuity/`, `tasks/briefs/s0-02-support/`, `proofs/S0-02/`, `scripts/no_laya_in_gates.py`:
never touch, run a writer against, or revert them. Never run `git stash`, `git checkout -- …`, `git restore`, `git add`,
`git commit` or `git push`. No outward-facing action; no PC or bridge use (the live run is the owner's, with sudo).

AUTHORIZATION: this is defensive work on the owner's own system: signalling and hanging the owner's own egress-containment runner in
the sandbox to prove it leaves no network state behind.

CODE INTEL FIRST: `graft ask` before any grep for code questions (graft indexes no definitions under `proofs/S0-05/tools/pc/`: say
"unmapped — graft ask unavailable" and read by line range); the pack:
`scripts/lane_context.sh -q 'how does the S0-05 runner stop, clean up and census S0-01' -s cleanup -s _s0_01_census -o /tmp/ve3r1/pack.md proofs/S0-05/tools/pc/run_s0_05_units.sh tests/test_s0_05_egress.py`.

PREDICATE: a finding blocks only if it is contract-mapped (R1-R3, A2', or D2 as built; for M, the commit 2fd0a7d's stated claims), reproduced through the real runner, materially
effective (host state left after a stop the contract covers, or a changed S0-01 tree that passes, or a stated claim false as stated),
with a concrete discriminator, and in-boundary (PC, T). Everything else is a follow-up. Emit ONE GATE RECOMMENDATION:
`MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`. The coordinator owns the final gate.

Report lint: `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/s0-05-support/VERIFY-E3-R1-report.md --root .` (no `--map`
flags; cite full repo-relative paths); apply its `fix:` hints for at most three rounds, then paste and finish. The report ends with
DISCREPANCIES and NOT-done.

## PREMISE — MEASURED at authoring (2026-09-23 11:38Z, sandbox @ local e0f173e, uid 0, before the push)
```
2026-09-23T11:38:43Z
$ git log -1 --format="%h %s" e0f173e | cut -c1-100
e0f173e E3-R1 landed (task #175; GATED-PENDING-VERIFY): a second signal cannot abort the S0-05 runne
$ git diff --stat e0f173e^ e0f173e
 proofs/S0-05/tools/pc/run_s0_05_units.sh   | 141 ++++++++---
 tasks/briefs/s0-05-support/E3-R1-report.md | 385 +++++++++++++++++++++++++++++
 tests/test_s0_05_egress.py                 | 380 +++++++++++++++++++++++++++-
 3 files changed, 861 insertions(+), 45 deletions(-)
$ blob[:12] lines (at e0f173e)
076f863a54b9   641 proofs/S0-05/tools/pc/run_s0_05_units.sh
8b2f1f042bdf  3367 tests/test_s0_05_egress.py
$ grep -n "trap \|^cleanup()\|_s0_01_census\|census-failed\|census failed" proofs/S0-05/tools/pc/run_s0_05_units.sh
223:_s0_01_census() {  # snap | compare <census file>
382:cleanup() {
383:  trap '' INT TERM
394:# checker runs. (`trap cleanup EXIT INT TERM` ran cleanup on the signal and then CONTINUED, E3.)
400:# `exit` would end the EXIT trap before `cleanup` began (E3-R1 report, section 2). Not covered: a stop
403:trap cleanup EXIT
404:trap 'trap "" INT TERM; exit 130' INT
405:trap 'trap "" INT TERM; exit 143' TERM
407:CENSUS_BEFORE=$(_s0_01_census snap)
594:census_changed=$(_s0_01_census compare "$EVIDENCE_ROOT/s0-01-census.json" 3<<<"$CENSUS_BEFORE") \
632:  echo "=== S0-01's tree census failed (exit $census_failed): the leg FAILS ===" >&2
$ grep -n "^def test_e3r1\|^def _iptables_shim" tests/test_s0_05_egress.py
2415:def _iptables_shim(workdir, action, match="-t nat -A PREROUTING"):
3057:def test_e3r1_r1_b_a_second_signal_while_cleanup_waits_for_a_slow_unit(e3dir, first, second, target):
3099:def test_e3r1_r1_c_a_second_signal_inside_the_relay_reach_removal(e3dir, second, target):
3147:def test_e3r1_r1_a_signal_while_cleanup_reaps_at_the_runs_own_end_changes_nothing(e3dir, target):
3254:def test_e3r1_r2_each_in_place_write_fails_the_leg_by_name(e3dir):
3299:def test_e3r1_r2_a_symbolic_link_is_recorded_by_its_target_never_followed(e3dir):
3339:def test_e3r1_r2_an_unchanged_tree_passes(e3dir):
3358:def test_e3r1_r2_a_census_that_cannot_be_taken_fails_the_leg(e3dir):
$ (the coordinator gate at landing, 11:3xZ) /root/venv-agent-factory/bin/python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e3r1g/bt (as root)
263 passed in 235.74s (0:03:55)
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_05_egress.py
1 files set=9f0502080347
$ host census after the gate: ip netns list | wc -l; veth count; iptables -t nat -S PREROUTING; ls /etc/netns; route_localnet(all)
0
0
-P PREROUTING ACCEPT
0
0
/usr/bin/strace
/usr/bin/gdb
/dev/vda        252G   36G  1.4G  97% /
```
Item 10's component, measured at local 2fd0a7d:
```
2026-09-23T11:51:34Z
$ blob[:12] lines (at 2fd0a7d)
e42d72236c02   195 harness-ports/bin/qwen-matrix.sh
75ca7c341681   263 harness-ports/tests/test_qwen_matrix_sh.sh
$ grep -n "trap " harness-ports/bin/qwen-matrix.sh
96:  trap '' INT TERM
97:  trap - EXIT
143:# EXIT trap before cleanup began (measured on the S0-05 runner, E3-R1 report section 2). Not covered:
145:trap cleanup EXIT
146:trap 'trap "" INT TERM; exit 130' INT
147:trap 'trap "" INT TERM; exit 143' TERM
$ bash harness-ports/tests/test_qwen_matrix_sh.sh | tail -1 (the coordinator, 11:4xZ; and inside run-all.sh: ALL SUITES PASSED)
qwen-matrix-sh: 19 passed, 0 failed
```
The sandbox has `strace` and `gdb` (last two paths above), which item 3 may use. Not measured at authoring, and so written as
questions above: whether a double INT or SIGHUP leaves state, whether a hung child makes the run unstoppable without SIGKILL, and
whether any new mutant survives.
