PROPOSAL: T90-R1 implementation complete. Independent sandbox verification is still required.

Report: /home/rocco/agent-factory/.lanes/pc-t90-r1.md--9ca3279/tree/tasks/briefs/pc-t90-support/T90-R1-report.md

T90-R1 IMPLEMENTATION REPORT

Route: agentfactory-build-local, HYBRID in practice because a cloud step may serve a turn when the local step refuses with the chat-template 400. No claim is made about which model produced the code.

PREMISE — RE-MEASURED

Verified at 2026-09-22T12:56:51Z on PIN 9ca327930bbc6dd076754f439428cb3a92d5f9c2.

    a5a48539e40313b4  scripts/pc_lane.sh (524 lines)
    2c0b622fa89a88f7  harness-ports/tests/test_pc_lane_dispatcher.sh (200 lines)
    0e000f53ef6d3899  harness-ports/bin/pc-lane.sh (512 lines)

The anchors matched the brief. The PIN suites returned:

    pc_lane dispatcher: 24 passed, 0 failed
    59 passed, 0 failed

Premise status: VERIFIED. harness-ports/bin/pc-lane.sh:89 defines the lane pidfile. harness-ports/bin/pc-lane.sh:106 checks only pid liveness in its read-only replay guard.

ITEMS 2–6

Red-first suite, with tests changed and production still at the PIN:

    [FAIL] a private-copy failure refuses the original before any bridge call
    [FAIL] a writable TMPDIR execs the private copy with PC_LANE_SELF_COPY set
    [FAIL] a stale pidfile is FIRST and a premise-less brief is refused with no ship write
    [FAIL] a live pid from another lane is FIRST and refused with no ship write
    [FAIL] a live pid bound to this lane returns RESUME with its launch epoch and ships
    [FAIL] a premise-probe bridge error is FIRST and refused with no ship write
    [FAIL] two whitespace-only premise lines are refused with no ship write
    [FAIL] one real and one whitespace premise line are refused with no ship write
    [FAIL] NEGATIVE CONTROL: a READY probe still harvests; one-tag mix has no caveat and the shipped read-only SQL escapes its combo filter
    [FAIL] a RESUME mix is labelled as a combo-window aggregate and starts at lane launch minus 60 seconds
    [FAIL] the old per-lane attribution sentence is absent from the dispatcher
    pc_lane dispatcher: 21 passed, 11 failed

Green after the dispatcher change:

    [PASS] a private-copy failure refuses the original before any bridge call
    [PASS] a writable TMPDIR execs the private copy with PC_LANE_SELF_COPY set
    [PASS] a stale pidfile is FIRST and a premise-less brief is refused with no ship write
    [PASS] a live pid from another lane is FIRST and refused with no ship write
    [PASS] a live pid bound to this lane returns RESUME with its launch epoch and ships
    [PASS] a premise-probe bridge error is FIRST and refused with no ship write
    [PASS] two whitespace-only premise lines are refused with no ship write
    [PASS] one real and one whitespace premise line are refused with no ship write
    [PASS] a RESUME mix is labelled as a combo-window aggregate and starts at lane launch minus 60 seconds
    [PASS] a FIRST mix window starts within five seconds of now minus 60 seconds
    [PASS] the old per-lane attribution sentence is absent from the dispatcher
    pc_lane dispatcher: 32 passed, 0 failed

Item 2 — liveness-bound RESUME

scripts/pc_lane.sh:199-217 sends one bridge probe containing kill -0, the exact lane directory, cwd/cmdline binding, and pidfile stat -c %Y. Only RESUME <epoch> skips the gate.

harness-ports/tests/test_pc_lane_dispatcher.sh:166-203 evaluates stale, foreign-live, bound-live, and bridge-error fixtures. Stale, foreign, and bridge-error controls each assert rc 64 and zero ship writes.

Anti-pattern fixed: stale file presence treated as live state, AF-AP-105.

Item 3 — fail-closed private copy

scripts/pc_lane.sh:52-75 defines PC_LANE_SELF_COPY before the trap. Failed mktemp, cp, or exec refuses with rc 64 before configuration or bridge access.

harness-ports/tests/test_pc_lane_dispatcher.sh:132-148 asserts:

    exactly one stderr line
    zero bridge calls
    no unset-variable or config error
    writable TMPDIR starts the copied child
    PC_LANE_SELF_COPY is set in that child

Anti-pattern fixed: a failed safety copy continued in the unsafe original.

Item 4 — non-space premise evidence

scripts/pc_lane.sh:189-198 counts only lines matching /[^[:space:]]/.

The tests prove that these blocks fail:

    empty
    one real line
    two whitespace-only lines
    one real line plus one whitespace-only line

A two-real-line block passes. Every dispatcher-level refusal asserts no ship write.

Anti-pattern fixed: whitespace accepted as evidence, AF-AP-64.

Item 5 — honest combo-window label

scripts/pc_lane.sh:512-515 now emits:

    pc_lane: combo-window provider mix (per-lane provenance UNVERIFIED) ...

The multi-tag caveat states that the result is a COMBO-WINDOW aggregate and that per-lane provenance is unverified because call_logs has no lane key.

The old attribution sentence occurs zero times in the dispatcher.

Item 6 — lane launch time

scripts/pc_lane.sh:343-351 sets LAUNCH_AT from the validated RESUME epoch. FIRST uses current UTC time.

scripts/pc_lane.sh:446 applies the minus-60-second SQL lower bound.

The RESUME test pins epoch 1790000000 and the measured lower bound 2026-09-21T14:12:20Z. The FIRST test checks that its lower bound is within five seconds of current time minus 60 seconds.

MUTATION TABLE

    drop kill -0
      Validity: bash -n clean; suite collected
      Killer: stale pidfile is FIRST
      Result: KILLED, 27 passed / 5 failed

    drop lane binding
      Validity: bash -n clean; suite collected
      Killer: live pid from another lane is FIRST
      Result: KILLED, 31 passed / 1 failed

    drop fail-closed exit 64
      Validity: bash -n clean; suite collected
      Killer: private-copy failure refuses original
      Result: KILLED, 31 passed / 1 failed

    revert non-space regex to length($0) > 0
      Validity: bash -n clean; suite collected
      Killer: whitespace-only and mixed blocks refused
      Result: KILLED, 30 passed / 2 failed

    restore old attribution sentence
      Validity: bash -n clean; suite collected
      Killer: combo-window label and old-sentence absence
      Result: KILLED, 30 passed / 2 failed

    ignore RESUME epoch
      Validity: bash -n clean; suite collected
      Killer: RESUME lower SQL bound
      Result: KILLED, 31 passed / 1 failed

Hollow-green rate: 0/6 mutants survived.

GATES

    bash-n rc=0
    pc_lane dispatcher: 32 passed, 0 failed
    pc_lane dispatcher: 32 passed, 0 failed
    59 passed, 0 failed
    59 passed, 0 failed

run-all.sh:

    test_pc_bridge_exec.py             test_pc_bridge_exec: 8 checks passed
    test_hermes_session_export.py      test_hermes_session_export: 13 checks passed
    test_omniroute_local_builder.py    test_omniroute_local_builder: 24 checks passed
    test_pc_lane.sh                    59 passed, 0 failed
    test_pc_lane_dispatcher.sh         pc_lane dispatcher: 32 passed, 0 failed
    test_pc_lane_admission.sh          22 passed, 0 failed
    test_qwen_server.sh                qwen-server: 101 passed, 0 failed
    test_qwen_matrix.py                test_qwen_matrix: 4 tests passed
    test_qwen_matrix_sh.sh             qwen-matrix-sh: 16 passed, 0 failed
    test_lane_context.sh               5 passed, 0 failed
    test_context_mirrors.sh            11 passed, 0 failed
    test_sync_skills.sh                34 passed, 0 failed
    build-roles --check                OK: 3 role config layers match their sources

    ALL SUITES PASSED
    diff-check rc=0

Anti-pattern screen:

    --- TEST_SCREEN over 2 path(s): 3 hits over 2 files ---
    AF-AP-87: 2
        scripts/pc_lane.sh:378
        scripts/pc_lane.sh:378
    AF-AP-59: 1
        scripts/pc_lane.sh:370

These are not findings in this increment. Both are pre-existing poll-state patterns outside the changed hunks. The full suite and the 59-test runner suite exercise that code.

Final file identity:

    309d5cabe68ab150  scripts/pc_lane.sh (555 lines)
    186601fb81b0a167  harness-ports/tests/test_pc_lane_dispatcher.sh (303 lines)

Report lint:

    report_lint: 18 refs — OK 18, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)

GitNexus detect-changes returned “No changes detected.” Its index does not map these shell changes, so this means unmapped, not clean.

Ripwire edit-check returned “symbol not found: scripts/pc_lane.sh”. The final lane-context pack completed in lane scratch.

Fixture-process census: ps -C sleep produced no rows after the tests.

Hygiene:

    git status lists only D, T, and R
    git diff --check rc=0
    no commit
    no push

SELF-ATTACK

1. A live foreign pid could be mistaken for this lane.

Ruled out by cwd-or-cmdline binding, the foreign-live fixture, and the lane-binding mutant.

2. A copy failure could continue in the original or hit the unset trap.

Ruled out by exact rc 64, exactly one stderr line, zero bridge calls, no config or unset text, and the dropped-exit mutant.

3. A re-attach could still use poller time or imply per-lane attribution.

Ruled out by the captured SQL bound from epoch 1790000000, the epoch-ignored mutant, exact UNVERIFIED output, and the restored-attribution mutant.

DISCREPANCIES

- The brief says epoch 1790000000 equals 2026-09-21T09:33:20Z and expects lower bound 09:32:20Z. GNU date -u -d @1790000000 returns 2026-09-21T14:13:20Z. The correct lower bound is 2026-09-21T14:12:20Z. The test uses the measured conversion and preserves the contract intent.

- The attached pack was absent from the lane worktree. I read the read-only PC clone copy at /home/rocco/agent-factory/tasks/briefs/pc-t90-support/T90-R1-pack.md.

- The brief’s ap_screen command omitted --tests. The tool rejects a test file without it. The actual run used --tests and its output is recorded above.

- All reproduction used the fake bridge. No real server, credential, lane directory, OmniRoute state, bridge env file, or production tree was touched.

NOT-DONE

- T92 durable per-request correlation id: NOT built.
- D-039 routes: NOT changed.
- harness-ports/bin/pc-lane.sh: NOT changed.
- No commit, push, PR, server action, credential access, or production-tree write.
- The patch remains a proposal until the separate sandbox adversarial-verifier lane grades it.
