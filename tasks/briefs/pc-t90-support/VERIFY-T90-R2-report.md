VERIFY-T90-R2 — targeted independent adversarial verification

STATUS
  NOT-READY recommendation. The frozen R-F1 contract is still violated on the production dispatcher path when PC_AF_REPO has its normal literal `$HOME/agent-factory` value. The structural pid binding itself works when given the real absolute lane directory. The F3 self-copy repair holds.

IDENTITY
  PIN: 76ca87c848308cebd695e26810003cb880b86620
  Boundary: `scripts/pc_lane.sh` and `harness-ports/tests/test_pc_lane_dispatcher.sh`
  Frozen contract: `tasks/briefs/pc/pc-t90-r2.md` R-F1 + R-F3; `tasks/briefs/pc-t90-support/VERIFY-T90-report.md` F1 + F3.
  Dispatcher: 561 lines, sha256[:16] ef6b64a1d8fcfc99, mode 100755.
  Test file: 417 lines, sha256[:16] f74d7e0a3419dcb7, 29 check sites / 37 runtime checks.

REPRODUCTION TABLE

| Claim | Instrument | Observed | Evidence |
|---|---|---|---|
| Landing dispatcher gate | `bash harness-ports/tests/test_pc_lane_dispatcher.sh` twice | `pc_lane dispatcher: 37 passed, 0 failed` twice; rc 0 | SOLID |
| Syntax | `bash -n scripts/pc_lane.sh`; `bash -n harness-ports/tests/test_pc_lane_dispatcher.sh` | both rc 0 | SOLID |
| Full harness suite | `bash harness-ports/tests/run-all.sh` | `ALL SUITES PASSED`; rc 0; 1m13.624s | SOLID |
| R-F1 exact structural binding | Production probe body from `scripts/pc_lane.sh:211`, local pidfile-bound sleepers | sibling/mention FIRST; exact lane token, exact brief token, cwd containment, spaced exact token RESUME | SOLID |
| R-F1 dispatcher path under normal default | Scratch dispatcher + fake bridge, exact setsid/nohup/stdin `/dev/null` launch | literal `$HOME/...` -> FIRST, rc 64, ship 0; absolute path -> RESUME, rc 75, ship 1 | SOLID |
| R-F3 inherited env cannot skip copy | PIN dispatcher, bad brief, fake bridge | caller sentinel survives; one new `pc_lane.sh.XXXXXX` copy runs and is removed; rc 64 | SOLID |
| R-F3 trap owns only `$0` | PIN dispatcher plus m4 mutant | production copy removed; m4 killed by named test | SOLID |
| Raw-id mix query | read-only SQLite script | 348 direct raw-id rows; 348 NULL/empty combo; raw-id combo-name matches 0 | SOLID |
| Builder RED claim | PIN test file against `git show 435b057:scripts/pc_lane.sh` | 29 passed / 8 failed, not the reported 33 / 4 | SOLID discrepancy |

LANDING GATES

Run 1:
  pc_lane dispatcher: 37 passed, 0 failed
  RC1=0

Run 2:
  pc_lane dispatcher: 37 passed, 0 failed
  RC2=0

Five named controls from run 2:
  [PASS] an inherited PC_LANE_SELF_COPY does not skip the private copy or delete the caller sentinel
           because: rc=64 private_copy=/tmp/tmp.WEyVrE2aRC/copy-inherited/pc_lane.sh.YayNOG private_copy_exists=no sentinel_exists=yes bridge_calls=1
  [PASS] the EXIT trap removes only its own private-copy path
           because: reason=mutant-other-path-deleted rc=64 private_copy=/tmp/tmp.WEyVrE2aRC/copy-inherited/pc_lane.sh.oX81jv private_copy_exists=no other_path_exists=no
  [PASS] a sibling suffix id is FIRST and refused with no ship write
           because: state=FIRST rc=64 no_ship_writes=0 pid=2837033
  [PASS] an argv mention alone is FIRST and refused with no ship write
           because: state=FIRST rc=64 no_ship_writes=0 pid=2837079
  [PASS] an argv token equal to the lane dir is RESUME and ships
           because: state=RESUME 1790000000 rc=75 ship_writes=1 pid=2837122

Full suite:
  ALL SUITES PASSED
  rc=0
  elapsed=1m13.624s

RED CONTROL

Literal command: PIN test file against a scratch tree whose `scripts/pc_lane.sh` is from 435b057.

  RC_RED=1
  pc_lane dispatcher: 29 passed, 8 failed
  [FAIL] an inherited PC_LANE_SELF_COPY does not skip the private copy or delete the caller sentinel
           because: rc=64 private_copy=/tmp/tmp.fL8yt77dvZ/caller-self-copy-sentinel private_copy_exists=no sentinel_exists=no bridge_calls=1
  [FAIL] the EXIT trap removes only its own private-copy path
           because: reason=no rc=64 private_copy=/tmp/tmp.fL8yt77dvZ/copy-inherited/pc_lane.sh.EAY1du private_copy_exists=no other_path_exists=yes
  [FAIL] a sibling suffix id is FIRST and refused with no ship write
           because: state=RESUME 1790108323 rc=75 no_ship_writes=1 pid=2839262
  [FAIL] an argv mention alone is FIRST and refused with no ship write
           because: state=RESUME 1790108323 rc=75 no_ship_writes=1 pid=2839324
  [FAIL] an argv token equal to the lane dir is RESUME and ships
           because: state=FIRST rc=64 ship_writes=0 pid=2839385
  Additional harness-shape failures: stale pidfile, live pid from another lane, and bridge error.

The exact-token positive does not pass by design on the old dispatcher with the literal required pairing. The old probe interpolates the spaced lane path as unquoted `d=<path with space>` before fake-bridge eval, so it yields FIRST. The builder report's 33/4 RED count is not reproduced.

F1 PROBE-SHAPE TABLE

| Shape | Exact output | Consequence |
|---|---|---|
| (a) sibling suffix | `FIRST` | Correct rejection |
| (b) argv mention only | `FIRST` | Correct rejection |
| (c) exact lane token | `RESUME 1790111734` | Correct acceptance |
| (d) exact brief token | `RESUME 1790111734` | Correct acceptance |
| (e) cwd inside lane | `RESUME 1790111734` | Correct acceptance |
| (f1) spaced exact token | `RESUME 1790111734` | NUL boundary preserved |
| (f2) spaced sibling | `FIRST` | Correct rejection |
| (g) deleted cwd | `FIRST` | Conservative rejection |
| (h) stale pid | `FIRST` | Correct rejection |
| (i) other-user PID 1 | `kill -0 rc=1`; `FIRST` | EPERM fails closed |
| m1 on (a) | `RESUME 1790111862` | Mutation discriminator |
| m1 on (b) | `RESUME 1790111862` | Mutation discriminator |
| m5 on (f1) | `FIRST` | Mutation discriminator |

Deleted cwd observation:
  `readlink /proc/2909030/cwd` -> `/home/rocco/tmp-vt90r2/lanes2/vdel.md--deadbeef (deleted)`.
  A live lane can reach this only if its working directory is removed while the process stays alive. This is abnormal/destructive, not the normal re-attach path.

F1 THROUGH DISPATCHER FAKE BRIDGE

Bad-premise brief, scratch copy only:
  d exact brief token: `state=RESUME 1790111963 rc=75 ship_writes=1`
  f spaced exact token: `state=RESUME 1790111963 rc=75 ship_writes=1`
  g deleted cwd: `state=FIRST rc=64 ship_writes=0`

Here rc 75 is the fake harness's deliberate `MAX_POLLS=0` post-launch marker. It proves the RESUME path shipped. FIRST refuses with rc 64 before any bridge write.

F3 SHAPE TABLE

| Shape | Exact observation | Result |
|---|---|---|
| (a) inherited self-copy sentinel | `rc=64 sentinel=EXISTS copy=.../pc_lane.sh.aZVmyU copy_exists=no` | Correct |
| (b) inherited self-copy + origin | `rc=64 sentinel=EXISTS copy=.../pc_lane.sh.cI8Uj6 copy_exists=no` | Correct |
| (c) normal invocation | `rc=64 copy_debug_lines=1 copy=.../pc_lane.sh.VGMUTE copy_exists=no` | Correct |
| (d) `TMPDIR=/nonexistent` | `rc=64 private_active_lines=0 bridge_calls=0`; named mktemp reason | Fail closed |
| (e) caller file equals `$0` | `rc=64 attacker_file_after=GONE private_debug_path=.../attacker-own.sh` | Declared limit; not bypass |
| space-bearing sentinel | `rc=64 sentinel=EXISTS copy=.../f3\ space/tmp/pc_lane.sh.OZPWlw copy_exists=no` | Correct |
| m3 | rc 1; inherited-self named test fails | Killed |
| m4 | rc 1; EXIT-trap named test fails | Killed |

Shape (e) runs the caller's own file with the caller's own environment. No privilege or byte-identity boundary is crossed. The trap removes that process's own `$0`, exactly as frozen R-F3 states. Classification: INFO, not a blocker.

BLAST RADIUS

ROOT and first/copy pass:
  `scripts/pc_lane.sh:57` unsets `PC_LANE_SELF_COPY PC_LANE_ORIG` as untrusted copy/origin values.
  `scripts/pc_lane.sh:71` execs the private copy with `PC_LANE_SELF_COPY="$_self" PC_LANE_ORIG="$0"`.
  `scripts/pc_lane.sh:119` derives `ROOT` from `PC_LANE_ORIG` on the copy pass.

Relative launch probe:
  `relative-invocation rc=64 self_copy_exists=no`
  `TRACE_ROOT pass_self=/home/rocco/tmp-vt90r2/root/tmp/pc_lane.sh.e21bjN orig=scripts/pc_lane.sh root=/home/rocco/tmp-vt90r2/root`

ROOT is correct. The first pass does not reach ROOT. The copy pass resolves the relative original from the inherited original cwd and obtains the expected root. The AF-AP-113 `//scripts/pc_bridge_exec.py` failure is not reintroduced.

Dispatcher cwd sweep:
  Literal `grep -n '^cd \|cd "' scripts/pc_lane.sh` reports only line 119, the ROOT command-substitution subshell. The dispatcher does not change its main-shell cwd after trap installation.

A scratch-only inserted cwd change proved that a caller-chosen relative `$0` can make the trap miss its original path. That shape is unreachable for production-created copies because `mktemp` returns an absolute path and the dispatcher never changes cwd. Classification: INFO.

Special paths through the dispatcher/fake bridge:
  quote repo: `state=RESUME 1790112350 rc=75 ship=1`
  dollar repo: `state=RESUME 1790112351 rc=75 ship=1`

Mode:
  435b057^: 100755
  435b057:  100755
  76ca87c:  100755

The brief's stated transient 100644 patch mode does not reproduce from committed primary sources. The landed PIN is executable.

F1 PRODUCTION-PATH DEFECT

The NUL-free `read` hypothesis is false:
  `parent-context state=RESUME\ 1790093003 diagnostics=read_rc=1 b_len=80`

`read` returns 1 because base64 emits no newline. But the brace group's last command is `bridge`, so the pipeline status is the bridge status. The command substitution captures RESUME under `set -uo pipefail`. stdin `/dev/null` and private-copy ROOT are not causal.

Exact coordinator launch shape under setsid/nohup/stdin `/dev/null`:
  absolute `PC_AF_REPO`:
    `rc=75 captured_state=RESUME 1790111575 trace=TRACE_PREMISE_STATE=RESUME 1790111575 ship_writes=1`
  literal default-shaped `PC_AF_REPO='$HOME/tmp-vt90r2/item6/repo'`:
    `rc=64 captured_state=FIRST trace=TRACE_PREMISE_STATE=FIRST ship_writes=0`

Root cause:
  `scripts/pc_lane.sh:142` sets `: "${PC_AF_REPO:=\$HOME/agent-factory}"`, storing the literal string `$HOME/agent-factory` for PC-side expansion in bridge commands. `scripts/pc_lane.sh:210-211` constructs `_PREMISE_LANE_DIR` and `_premise_state`, then base64-encodes that literal before the bridge command. The remote bridge uses `subprocess.run(["bash", "-lc", cmd]` (`/home/rocco/agent_shell2.py:31`). After `d=$(... | base64 -d)`, `$HOME` is data and is not reparsed as shell syntax. The probe therefore reads the relative nonexistent path `$HOME/agent-factory/.lanes/.../lane.pid`, emits FIRST, re-ships, and reaches the PC duplicate-start guard. `2>/dev/null` hides the failed read but is not the cause.

Proven minimal fix shape in scratch:
  Normalize decoded `d` before reading the pidfile:
    `case "$d" in '$HOME'/*) d="$HOME/${d#'$HOME'/}";; esac`

Observed after this single repair:
  `remote-fix-shape rc=75 state=RESUME 1790113126 ship_writes=1`

This preserves the dispatcher's existing literal `PC_AF_REPO` convention for every other bridge command. Expanding the default locally would bind it to the sandbox home and is therefore not the right repair.

PROVIDER-MIX OBSERVATION

Read-only SQLite, SQL supplied from `/home/rocco/tmp-vt90r2/rawcombo2.sql`, last three hours:
  direct_raw_rows_last_3h: 348
  direct_raw_rows_empty_or_null_combo: 348
  direct_raw_rows_matching_raw_id_combo: 0

Context rows:
  agentfactory-build-local / combo execution key set: 1224
  agentfactory-verify-local / combo execution key set: 930
  NULL combo / no combo execution key: 348

`scripts/pc_lane.sh:438` sets `MIX_COMBO="${HERMES_MODEL:-}"`. On a strict raw-id lane, the direct rows have no combo name, so the query's `combo_name = 'qwen-local/qwen3.8-27b-local'` matches zero by construction. This is the next dispatcher lane's observation, not a T90-R2 repair request.

FINDING INVENTORY

F1 — BLOCKER — normal default `PC_AF_REPO` is base64-decoded into an unexpanded literal `$HOME/...`, so a real re-attach is classified FIRST.
  Evidence: SOLID, exact production payload executed by fake bridge; exact coordinator process launch shape.
  Contract mapping: R-F1 requires a real resumed lane, including cwd inside `$d`, to return RESUME.
  Canonical path: YES. At `scripts/pc_lane.sh:142`, `PC_AF_REPO:=\$HOME/agent-factory`; at `scripts/pc_lane.sh:210`, `_PREMISE_LANE_DIR="$PC_AF_REPO/.lanes/$LANE_ID"`; at `scripts/pc_lane.sh:211`, `_premise_state` base64-transfers that literal. It matches the recorded first live use.
  Material effect: YES. The dispatcher re-ships a bad-premise brief and reaches duplicate-start refusal rather than entering the re-attach path. The protected premise exemption is therefore broken on the normal default.
  Concrete discriminator: absolute directory -> RESUME/rc75/ship1; default literal `$HOME/...` -> FIRST/rc64/ship0; one-line remote normalization -> RESUME/rc75/ship1.
  Ownership: YES. Fix is in `scripts/pc_lane.sh` within the item-6 target boundary.
  Suggested fix: normalize the decoded remote path as shown above before pidfile access, and add a test whose fake-bridge input uses the real default literal `$HOME/...` rather than only absolute temp paths.
  Bug-echo / anti-pattern class for coordinator: representation-boundary expansion loss. A value deliberately stored as shell syntax for later expansion was base64-transferred and decoded as data; test the normal symbolic default and its resolved consumer path, not only an already-absolute fixture.

F2 — INFO — R-F3 attacker-owned script whose `$0` equals the supplied self-copy path passes the guard and deletes itself.
  Evidence: SOLID.
  Contract mapping: R-F3 explicitly keys identity and removal to process `$0`.
  Canonical path: YES, but only caller-owned bytes/env.
  Material effect: caller deletes its own launched script; no trust boundary crossed.
  Reproduction: F3 shape (e).
  Suggested fix: none for this contract. Document only if caller expectations need clarification.

F3 — INFO — deleted cwd returns FIRST.
  Evidence: SOLID.
  Contract mapping: refusal class is preserved; no contract requires re-attaching after destructive cwd deletion.
  Canonical path: exact probe.
  Material effect: abnormal lane cannot re-attach.
  Reproduction: probe shape (g).
  Suggested fix: none in this increment.

F4 — UNVERIFIED EVIDENCE CLAIM — builder RED count and positive-control status do not reproduce.
  Evidence: SOLID for the mismatch; reason inferred from the old unquoted spaced path in fake-bridge eval.
  Contract mapping: report evidence demand, not production behavior at the repaired PIN.
  Canonical path: literal required red command, scratch copy.
  Material effect: makes the builder's stated 33/4 RED evidence false, but does not itself falsify repaired production output.
  Reproduction: 435b057 dispatcher + PIN test file -> 29/8; exact-token positive is FAIL.
  Suggested fix: correct the builder report or retain this verifier's discrepancy alongside it. Do not use the claimed 33/4 count as evidence.

F5 — FOLLOW-UP — raw-id provider-mix query matches zero direct rows.
  Evidence: SOLID, read-only SQLite.
  Contract mapping: none for R-F1/R-F3; brief item 7 explicitly says observation only.
  Canonical path: `scripts/pc_lane.sh:438` plus live call log.
  Material effect: post-harvest provenance report says no rows despite raw-id calls.
  Reproduction: 348 direct raw-id rows; 348 empty/NULL combo; 0 raw-id combo-name matches.
  Suggested fix: the next dispatcher lane should distinguish raw-id direct rows from combo-name rows.

PREDICATE TABLE

| Finding | Contract-mapped | Exact production path | Material | Discriminator | In boundary | Disposition |
|---|---|---|---|---|---|---|
| F1 default `$HOME` decode | YES | YES | YES | YES | YES | BLOCKER |
| F2 caller-owned `$0` | literal limit, not contradiction | YES | no cross-boundary effect | YES | YES | INFO |
| F3 deleted cwd | no required RESUME | YES | abnormal path only | YES | YES | INFO |
| F4 RED evidence mismatch | evidence requirement only | red scratch path | report evidence false | YES | report artifact | UNVERIFIED evidence claim |
| F5 raw-id mix query | none for R-F1/R-F3 | YES | provenance output | YES | next lane | FOLLOW-UP |

SCREENS / LINT

Builder report lint:
  report_lint: 13 refs — OK 10, NEAR 3, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)

Own report lint:
  report_lint: 16 refs — OK 15, NEAR 0, MISS 0, UNCHECKABLE 1, UNRESOLVED 0 (worktree)
  The one UNCHECKABLE line is the repeated `scripts/pc_lane.sh:438` `MIX_COMBO` observation; the floor passes and MISS is zero.

AP screen:
  --- TEST_SCREEN over 2 path(s): 3 hits over 2 files ---
  AF-AP-87: 2 at `scripts/pc_lane.sh:384` on `probe="$(bridge` and `$REMOTE_REPORT`.
  AF-AP-59: 1 at `scripts/pc_lane.sh:376` on the `launch.log` fallback comment.
  All three are outside the repair hunks `scripts/pc_lane.sh:52-78` (`PC_LANE_SELF_COPY`) and `scripts/pc_lane.sh:203-211` (`_premise_state`); no repair-added hit.

DISCREPANCIES / DELIBERATE SKIPS

  - Attempt-1 draft did not exist; attempt 1 contained only an HTTP 503 refusal. This report restarted item 1 from primary output.
  - The RED command produced 29/8, not the brief/builder 33/4. The positive exact-token control failed on the old dispatcher because its spaced absolute path was interpolated unquoted before fake-bridge eval.
  - The item-6 NUL-free `read` / pipefail theory is false on this host. The production-path defect is the base64-decoded literal `$HOME` path.
  - The committed mode was 100755 before and after 435b057 and remains 100755 at 76ca87c. The transient patch-mode premise cannot be recovered from committed Git state.
  - No second full sweep of F2/F4/F5/F6/F7 from VERIFY-T90. They remain issue #20, per frozen scope.
  - No mutations were pointed at a protected real resource. All mutants and extra dispatchers ran under `$HOME/tmp-vt90r2/`.

GATE RECOMMENDATION: NOT-READY — F1 satisfies all five blocking predicates. The normal production default makes the repaired structural probe inspect an unexpanded literal `$HOME/...` path, so a real live lane is still classified FIRST. This recommendation depends only on reproduced evidence.

No final verdict is issued here. The coordinator owns the gate decision.
