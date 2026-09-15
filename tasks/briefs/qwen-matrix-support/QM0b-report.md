COORDINATOR DISPOSITION (2026-09-15, landed): ACCEPTED as the deferred restart-when-idle mechanism. Independent sandbox gates reproduced: `harness-ports/tests/run-all.sh` ALL SUITES PASSED; dispatcher 13 passed, 0 failed (this resolves the env-conditioned dispatcher red an earlier detached-worktree probe chased — QM0-b's step-1c rewrite fixed it); three mutants dead. ONE coordinator amendment: the qwen suite read 98 passed, 1 failed in the sandbox where the lane reported 99/0 on the PC; root-caused by diagnostic to the test's `! kill -0 "$P1"` seeing the detached watcher as a ZOMBIE (`/proc/$P1/stat` state = Z; `kill -0` returns 0 for a defunct PID) because the sandbox subshell had not reaped it while the PC's init does. An `is_dead` helper (absent OR state=Z) hardened the one expiry check -> `qwen-server: 99 passed, 0 failed` x2 deterministic. Registered AF-AP-87 (the PID-only-liveness class the lane's own retro flagged). test_qwen_server.sh differs from the report sha by this amendment; the other 5 files match. NEXT: VERIFY-QM0b (findings-only cloud verify); the deferred restart becomes live on the PC after this push + ff-sync.

PROPOSAL COMPLETE — QM0-b implementation is self-validated; independent sandbox adversarial verification is NOT done.

NOT DONE

- No real qwen-builder install, restart, stop, or restart-when-idle command ran. All effects used fake QWEN_HOME, QWEN_LANES_DIR, proc data, curl, systemctl, and systemd-analyze.
- No acceptance verdict, commit, push, or production-file change. This lane cannot independently accept its own proposal.
- The full Python tree suite was not requested or run; the complete harness-port run-all gate ran instead.

VERIFIED

- Premise: the pinned qwen-server had guard/install/status but no deferred command. The live keyed metrics schema exposed `llamacpp:requests_processing 0`; unauthenticated metrics returned HTTP 401. No credential value was printed.
- Deferred state and watcher: `QWEN_PENDING_DIR` and the state helpers are at qwen:58 and qwen:261-387. The command publishes one watcher under an atomic `launch.lock`, replaces the environment snapshot atomically, and retains the watcher when a later request supersedes the snapshot.
- Idle gate: `pending_guard_reason` at qwen:317 requires authenticated processing count zero, no local lane, and no matrix lock. Any unreadable signal returns a blocker. `pending_watcher` at qwen:332 requires two idle observations, rechecks snapshot identity and all gates before `install`, then checks health.
- Terminal evidence: `pending_log` at qwen:307 and `pending_log_for_env` at qwen:312 write env-keyed terminal records. `pending_log_for_env expired` at qwen:339 exits 75 and retains the snapshot. `status_pending` at qwen:261 reports hash, time, watcher liveness, last blocker, and terminal outcome.
- Dispatcher: `server_effort_for_role` at dispatcher:93 preserves role effort mapping. `EFF_STATE` at dispatcher:144 reads live process argv. `EFF_OUT` at dispatcher:157 queues only a mismatch. `EFF_TERM` at dispatcher:166 waits for the exact pending env hash, then `applied` launches while expired/failed block.
- Tests: qwen-test:352-486 covers queueing, singleton replacement, every three-bit idle-mask combination, snapshot replacement during idle, the two-observation barrier, AF-AP-79 byte/systemd preservation, failed unit analysis, and unchanged-unit no-op. dispatcher-test:60-72 covers applied/expired/failed and cloud bypass.
- Red-green: the pinned implementation plus current qwen tests failed exactly at `restart-when-idle queues a detached watcher` with rc 64; summary `qwen-server: 80 passed, 17 failed`. Current focused suites report `qwen-server: 99 passed, 0 failed` and `pc_lane dispatcher: 13 passed, 0 failed`.
- Full harness gate, foreground: `ALL SUITES PASSED`; included qwen-server 99/0, dispatcher 13/0, pc-lane 53/0, and all sibling suites shown by `harness-ports/tests/run-all.sh`.
- Mutation evidence: removing matrix-lock refusal failed exact test `idle gate mask=1 applies iff local=0 busy=0 cell=0`, summary 96/1. Lowering the idle barrier from 2 to 1 failed exact snapshot-replacement test, summary 98/1. Ignoring dispatcher expiry failed exact `expired deferred restart blocks lane launch with reason`, summary 12/1.
- Static/screens: `git diff --check` and Bash syntax checks returned 0. AP screen: 0 production hits; dispatcher test 0. Qwen test has two AF-AP-33 fixture-response hits at lines 330 and 379; both are deterministic fake curl endpoints, not production success paths.
- Code intelligence: GitNexus detect-changes returned `Changes: 8 files, 6 symbols`, `Affected processes: 0`, `Risk level: low`. Ripwire marked `pending_watcher` new with one caller and no incompatible callers; `server_effort_for_role` unchanged. Final pack: qm0b-final-pack:1-85.

INFERRED

- A healthy unit whose rendered argv already contains the target effort needs no restart; dispatcher:qwen already-applied paths rely on argv comparison plus health rather than a service operation.
- Shell script call-graph tools are incomplete here. The final pack says Graft indexed no definitions and the script gate is unmodelled (qm0b-final-pack:5-43,77-85); executable shell suites carry the seam evidence.

ASSUMED

- GNU `flock`, `sha256sum`, `/proc/<pid>/{cmdline,environ}`, systemd user units, and llama.cpp metric names match the target PC. These are existing project dependencies and the brief's stated venue.
- `QWEN_MATRIX_LOCK=$QWEN_HOME/matrix/.cell.lock` remains the matrix-cell activity contract named by the brief.

FILES

- qwen `QWEN_PENDING_DIR` = harness-ports/bin/qwen-server.sh:58
- qwen `status_pending` = harness-ports/bin/qwen-server.sh:261
- qwen `pending_guard_reason` = harness-ports/bin/qwen-server.sh:317
- qwen `pending_watcher` = harness-ports/bin/qwen-server.sh:332
- qwen `restart_when_idle` = harness-ports/bin/qwen-server.sh:387
- qwen dispatcher `restart-when-idle` = harness-ports/bin/qwen-server.sh:468
- qwen test `restart-when-idle queues` = harness-ports/tests/test_qwen_server.sh:410
- qwen test `idle gate mask` = harness-ports/tests/test_qwen_server.sh:443
- qwen test `snapshot replacement` = harness-ports/tests/test_qwen_server.sh:453
- qwen test `AF-AP-79: waiting preserves` = harness-ports/tests/test_qwen_server.sh:469
- dispatcher `server_effort_for_role` = scripts/pc_lane.sh:93
- dispatcher `EFF_STATE` = scripts/pc_lane.sh:144
- dispatcher `EFF_TERM` = scripts/pc_lane.sh:166
- dispatcher test `local mismatch` = harness-ports/tests/test_pc_lane_dispatcher.sh:60
- dispatcher test `expired deferred restart` = harness-ports/tests/test_pc_lane_dispatcher.sh:64
- dispatcher test `failed deferred restart` = harness-ports/tests/test_pc_lane_dispatcher.sh:68
- harness doc `restart-when-idle` = docs/HARNESS-PORTS.md:397
- harness doc `atomically records` = docs/HARNESS-PORTS.md:407
- bridge doc `restart-when-idle` = PC-BRIDGE.md:175
- bridge doc `deferred-restart.log` = PC-BRIDGE.md:178
- Context-only staged lane inputs were not edited: tasks/briefs/pc/pc-qm0b.md and tasks/briefs/qwen-server-qm0b-restart-when-idle.md.

FILE IDENTITY AGAINST PIN efde78d

- harness-ports/bin/qwen-server.sh: 3a663e4faba782bce3047517aeaa904b08022c91b6e826491d24ba05065dff84 -> 55f39757dbaf07aa5452ced4de08a0b13b9e6623f71a1a70e7c4239c2af798c3.
- harness-ports/tests/test_qwen_server.sh: 2b3e51ccbdec77a5ce54b494968a3b3a695f554059c42f4e651871994fa75082 -> 1755ce7b74ed00726905d91437a5e6c8edf918c487ca5326ee0d9f85a0f25c2e.
- scripts/pc_lane.sh: e9bb17e23d34211b6d30656382e66e8bee7b364312b5072a41f1721e7b568374 -> dd9edf38e13edd4985b6231365d0a855bc9ae37c825a554e6a24770c72a64811.
- harness-ports/tests/test_pc_lane_dispatcher.sh: cb3f2bbba8aa74c36b224d9f7ad530b2c4e2d2782adbfb98eb9c2fb68be80458 -> 84f89b515fd3dec46b7081c79aa49cd3888d4046bcd85e3a0adf22c76ca320ef.
- docs/HARNESS-PORTS.md: 60433df0b7766b20c90252ebc2b46147c05f249297cdfa88a0f8cb027de4e1b7 -> aeb494b0ebd8b73b01877895a45347d2dd72169d2469a9a3831bb1a88a4146c1.
- PC-BRIDGE.md: 6bb45bd3bb851424e4ee701f8fc53430fce939ee962de0eb42f1762343d99dd3 -> 7f534920d393c5f6488dd81da400ba5563f0549b90ca1c71ec13fcb6030ec0ca.

SELF-ATTACK

1. Wrong green: one idle sample or a replacement could bypass the stability barrier. Ruled out by exact snapshot-replacement coverage and the barrier-lowering mutant, which failed 98/1.
2. Wrong green: one idle dimension could be omitted. Ruled out by all eight gate masks and the removed-matrix-check mutant, which failed 96/1.
3. Wrong green: dispatcher could launch after expiry/failure or match another request's record. Ruled out by env-sha-filtered polling, applied/expired/failed tests, and the ignored-expiry mutant, which failed 12/1.

DISCREPANCIES

- `scripts/test_summary.sh` only accepts pytest paths in this checkout; both shell-test invocations returned pytest exit 4. Shell counts are pasted from each harness's own deterministic summary and run-all output.
- `python3 -m pyflakes` is unavailable (`No module named pyflakes`) and does not accept shell scripts; shell syntax checks returned 0. `shellcheck` is unavailable.
- A first run-all attempt with TMPDIR inside the lane failed 4 pre-existing path-contract tests because they require `/tmp`; rerunning with the normal environment passed all suites.
- The first final lane-context command passed comma-separated symbols incorrectly and wrote an unmapped pack; the corrected invocation still reports shell scripts unindexed/unmodelled.
- Final report lint: `report_lint: 36 refs — OK 33, NEAR 0, MISS 0, UNCHECKABLE 3, UNRESOLVED 0 (worktree)`.
- No brief deviation.

REASONING RECORD

- Rejected direct restart: it would interrupt active work and bypass install validation.
- Ordering: persist exact target -> publish one watcher -> require two complete idle observations -> reload exact target -> recheck all gates -> validated install -> health -> env-keyed terminal record.
- Primary sources: brief; current consumer scripts; authenticated live metric schema; executable fake-boundary shell harnesses.
- Disjoint hunks: server mechanism/tests, dispatcher mechanism/tests, then current operator docs.

BUGS / RETRO

- Found and fixed: a pending snapshot replacement could inherit the old request's idle count. Class: stale state across identity replacement. The env hash now resets the barrier, and a kill-switch mutant proves the test acts. Coordinator should run bug-echo and register if this class is not already covered.
- Found and fixed: a detached shell watcher can leave a zombie-visible PID after exit, so status/singleton checks must pair liveness with the persisted watcher rc. Class: PID-only liveness. Existing project guidance already says liveness requires more than output; coordinator should classify the echo.
- Retro lesson for anti-hollow-green: mutate numeric/stability thresholds; a green timing test can otherwise survive the exact barrier deletion it claims to guard.

TIMESTAMP

- 2026-09-15T17:27:44Z final measurement checkpoint.
