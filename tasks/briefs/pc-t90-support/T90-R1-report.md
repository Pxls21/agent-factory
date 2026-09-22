# T90-R1 implementation report

Route: `agentfactory-build-local`, HYBRID in practice because a cloud step may serve a turn when the local step refuses with the chat-template 400. No claim is made about which model produced the code.

## PREMISE — RE-MEASURED

Verified at 2026-09-22T12:56:51Z on PIN `9ca327930bbc6dd076754f439428cb3a92d5f9c2`.

```
a5a48539e40313b4  scripts/pc_lane.sh (524 lines)
2c0b622fa89a88f7  harness-ports/tests/test_pc_lane_dispatcher.sh (200 lines)
0e000f53ef6d3899  harness-ports/bin/pc-lane.sh (512 lines)
```

The anchors matched the brief: `PC_LANE_SELF_COPY` at D@PIN:51-54; `_premise_block_ok` at D@PIN:169 and `length($0) > 0` at D@PIN:175; the file-presence RESUME probe at D@PIN:186-190; unconditional `LAUNCH_AT` at D@PIN:317; `MIX_CAVEAT` at D@PIN:320; `MIX_FROM` at D@PIN:415; provider-mix output and the attribution sentence at D@PIN:481-483.

PIN gates:

```
pc_lane dispatcher: 24 passed, 0 failed
59 passed, 0 failed
```

Premise status: VERIFIED. `harness-ports/bin/pc-lane.sh:89` defines `PIDFILE="$LANE_DIR/lane.pid"`; `harness-ports/bin/pc-lane.sh:106` checks `kill -0` only in its read-only replay guard.

## ITEMS 2-6

Red-first suite, with T changed and D still at the PIN:

```
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
```

Green after D:

```
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
```

### Item 2 — liveness-bound RESUME

D:199-217 sends one bridge probe containing `kill -0`, the exact lane directory, cwd/cmdline binding, and pidfile `stat -c %Y`. Only `RESUME <epoch>` skips the gate. T:166-203 evaluates stale, foreign-live, bound-live, and bridge-error fixtures. The stale, foreign, and bridge-error controls each assert rc 64 and `no_ship_writes=0`; T:168-172 also pins one probe containing the lane id. Anti-pattern class fixed: stale file presence treated as live state, AF-AP-105.

### Item 3 — fail-closed private copy

D:52-75 defines `PC_LANE_SELF_COPY` before the trap. A failed mktemp/cp emits exactly one refusal line and rc 64 before config or bridge access. T:132-148 asserts zero bridge calls, one stderr line, no unset-variable/config text, and the writable-TMPDIR child debug line. Anti-pattern class fixed: a safety copy whose setup failure continued in the unsafe original.

### Item 4 — non-space premise evidence

D:189-198 makes `_premise_block_ok` count only `/[^[:space:]]/`. T:205-227 begins at `# Unit-level premise counter controls through the dispatcher gate.` and proves empty, one-real-line, two-whitespace-line, and one-real-plus-whitespace blocks fail; the two-real-line fixture passes. Each dispatcher refusal asserts no ship write. Anti-pattern class fixed: whitespace accepted as evidence, AF-AP-64.

### Item 5 — honest combo-window label

D:512-515 labels output `combo-window provider mix (per-lane provenance UNVERIFIED)`. The multi-tag caveat says per-lane provenance is unverified because call_logs has no lane key. T:269-276 pins the exact caveat and rejects the old sentence. Old attribution sentence count in D: `0`.

### Item 6 — lane launch time

D:343-351 sets `LAUNCH_AT` from the validated RESUME epoch or current UTC time on FIRST. D:446 applies the minus-60-second SQL lower bound. T:269-276 pins RESUME epoch `1790000000` and lower bound `2026-09-21T14:12:20Z`; T:288-297 asserts FIRST within five seconds of now minus 60 seconds.

## MUTATION TABLE

| Mutant | Validity | Killing test | Result |
|---|---|---|---|
| drop `kill -0` | `bash -n` clean; suite collected | stale pidfile is FIRST | KILLED: 27 passed, 5 failed |
| drop lane binding | `bash -n` clean; suite collected | live pid from another lane is FIRST | KILLED: 31 passed, 1 failed |
| drop fail-closed `exit 64` | `bash -n` clean; suite collected | private-copy failure refuses original | KILLED: 31 passed, 1 failed |
| revert non-space regex to `length($0) > 0` | `bash -n` clean; suite collected | whitespace-only and mixed blocks refused | KILLED: 30 passed, 2 failed |
| restore old attribution sentence | `bash -n` clean; suite collected | combo-window label and old-sentence absence | KILLED: 30 passed, 2 failed |
| ignore RESUME epoch | `bash -n` clean; suite collected | RESUME lower SQL bound | KILLED: 31 passed, 1 failed |

Hollow-green rate: `0/6` mutants survived.

## GATES

```
bash-n rc=0
pc_lane dispatcher: 32 passed, 0 failed
pc_lane dispatcher: 32 passed, 0 failed
59 passed, 0 failed
59 passed, 0 failed
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
```

`python3 scripts/ap_screen.py scripts/pc_lane.sh harness-ports/tests/test_pc_lane_dispatcher.sh --tests`:

```
--- TEST_SCREEN over 2 path(s): 3 hits over 2 files ---
AF-AP-87: 2
    scripts/pc_lane.sh:378: probe="$(bridge "test -f $PC_AF_REPO/.lanes/$LANE_ID/FAILED && echo FAILED || (test -s $REMOTE_REPOR
    scripts/pc_lane.sh:378: probe="$(bridge "test -f $PC_AF_REPO/.lanes/$LANE_ID/FAILED && echo FAILED || (test -s $REMOTE_REPOR
AF-AP-59: 1
    scripts/pc_lane.sh:370: # The no-pidfile fallback is bounded to the LAUNCH WINDOW (launch.log younger than 5 min): the old `
```

Classification: not findings in this increment. Both patterns are pre-existing in the poll-state probe, outside changed hunks; `run-all.sh` and the 59-test runner suite exercise that code.

Final file identity:

```
309d5cabe68ab150  scripts/pc_lane.sh (555 lines)
186601fb81b0a167  harness-ports/tests/test_pc_lane_dispatcher.sh (303 lines)
```

GitNexus `detect-changes`: `No changes detected.` The index does not map these shell changes, so this is unmapped, not clean. Ripwire `edit-check` likewise returned `symbol not found: scripts/pc_lane.sh`; the lane-context pack completed and is in lane scratch.

Fixture-process census: `ps -C sleep` produced no rows after the tests. Hygiene: `git status --short` lists only D, T, and R; `git diff --check` is rc 0.

## SELF-ATTACK

1. A live foreign pid could be mistaken for this lane. Ruled out by cwd-or-cmdline binding, the foreign-live fixture, and the lane-binding mutant.
2. A copy failure could continue in the original or hit the unset trap. Ruled out by exact rc 64, exactly one stderr line, zero bridge calls, no config/unset text, and the dropped-exit mutant.
3. A re-attach could still use poller time or imply per-lane attribution. Ruled out by captured SQL bound from epoch 1790000000, the epoch-ignored mutant, exact UNVERIFIED output, and the restored-attribution mutant.

## DISCREPANCIES

- The brief says epoch `1790000000` equals `2026-09-21T09:33:20Z` and expects lower bound `09:32:20Z`. GNU `date -u -d @1790000000` returns `2026-09-21T14:13:20Z`; the correct lower bound is `2026-09-21T14:12:20Z`. The test uses the measured epoch conversion and preserves the contract intent.
- The attached pack was absent from the lane worktree. The read-only PC clone copy at `/home/rocco/agent-factory/tasks/briefs/pc-t90-support/T90-R1-pack.md` was read instead.
- The brief asked `python3 scripts/ap_screen.py D T` without `--tests`; the tool rejects a test file unless `--tests` is supplied. The run used `--tests` and pasted its output.
- The test suite runs against a fake bridge and no real server, credential, lane directory, OmniRoute state, or bridge env file. No live dispatcher reproduction was run, per AUTHORIZATION.
- `report_lint` final line: `report_lint: 18 refs — OK 18, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.

## NOT-DONE

- T92 durable per-request correlation id: NOT built.
- D-039 routes: NOT changed.
- `harness-ports/bin/pc-lane.sh`: NOT changed.
- No commit, push, PR, server action, credential access, or production-tree write.
- The patch remains a proposal until the separate sandbox adversarial-verifier lane grades it.
