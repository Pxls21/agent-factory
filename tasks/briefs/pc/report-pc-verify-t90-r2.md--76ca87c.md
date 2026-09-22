NOT-READY recommendation.

Report written to:

/home/rocco/agent-factory/.lanes/pc-verify-t90-r2.md--76ca87c/tree/tasks/briefs/pc-t90-support/VERIFY-T90-R2-report.md

VERIFY-T90-R2 — targeted independent adversarial verification

STATUS

NOT-READY recommendation. The frozen R-F1 contract is still violated on the production dispatcher path when PC_AF_REPO has its normal literal `$HOME/agent-factory` value.

The structural PID binding works when given an absolute lane directory. The F3 self-copy repair holds.

IDENTITY

PIN: 76ca87c848308cebd695e26810003cb880b86620

Boundary:
  scripts/pc_lane.sh
  harness-ports/tests/test_pc_lane_dispatcher.sh

Dispatcher:
  561 lines
  sha256[:16]: ef6b64a1d8fcfc99
  mode: 100755

Test file:
  417 lines
  sha256[:16]: f74d7e0a3419dcb7
  29 check sites
  37 runtime checks

REPRODUCTION SUMMARY

  Landing dispatcher gate:
    pc_lane dispatcher: 37 passed, 0 failed
    Repeated twice, rc 0 both times.

  Syntax:
    bash -n scripts/pc_lane.sh
    bash -n harness-ports/tests/test_pc_lane_dispatcher.sh
    FINAL_SYNTAX_OK

  Full suite:
    ALL SUITES PASSED
    rc=0
    elapsed=1m13.624s

  AP screen:
    3 known hits
    AF-AP-87: 2 at scripts/pc_lane.sh:384
    AF-AP-59: 1 at scripts/pc_lane.sh:376
    No repair-added hit.

  Own report lint:
    report_lint: 16 refs — OK 15, NEAR 0, MISS 0,
    UNCHECKABLE 1, UNRESOLVED 0 (worktree)

LANDING CONTROLS

  [PASS] inherited PC_LANE_SELF_COPY does not skip the
  private copy or delete the caller sentinel

    rc=64
    private_copy=/tmp/tmp.WEyVrE2aRC/copy-inherited/pc_lane.sh.YayNOG
    private_copy_exists=no
    sentinel_exists=yes
    bridge_calls=1

  [PASS] EXIT trap removes only its own private-copy path

    reason=mutant-other-path-deleted
    rc=64
    private_copy=/tmp/tmp.WEyVrE2aRC/copy-inherited/pc_lane.sh.oX81jv
    private_copy_exists=no
    other_path_exists=no

  [PASS] sibling suffix ID is FIRST and refused with no ship

    state=FIRST
    rc=64
    no_ship_writes=0

  [PASS] argv mention alone is FIRST and refused with no ship

    state=FIRST
    rc=64
    no_ship_writes=0

  [PASS] argv token equal to the lane directory is RESUME

    state=RESUME 1790000000
    rc=75
    ship_writes=1

RED CONTROL

PIN test file against the pre-repair dispatcher from 435b057:

  RC_RED=1
  pc_lane dispatcher: 29 passed, 8 failed

Named failures:

  [FAIL] inherited PC_LANE_SELF_COPY control

    rc=64
    private_copy=/tmp/tmp.fL8yt77dvZ/caller-self-copy-sentinel
    private_copy_exists=no
    sentinel_exists=no
    bridge_calls=1

  [FAIL] EXIT trap ownership control

    reason=no
    rc=64
    private_copy=/tmp/tmp.fL8yt77dvZ/copy-inherited/pc_lane.sh.EAY1du
    private_copy_exists=no
    other_path_exists=yes

  [FAIL] sibling suffix control

    state=RESUME 1790108323
    rc=75
    no_ship_writes=1

  [FAIL] argv mention control

    state=RESUME 1790108323
    rc=75
    no_ship_writes=1

  [FAIL] exact-token positive control

    state=FIRST
    rc=64
    ship_writes=0

Additional harness-shape failures:
  stale PID file
  live PID from another lane
  bridge error

Discrepancy:

The brief and builder report claim 33 passed / 4 failed and say the exact-token positive control passes on the old dispatcher. The literal required pairing produced 29 passed / 8 failed.

The old dispatcher interpolates the spaced lane path into unquoted `d=<path with space>` before fake-bridge evaluation. The exact-token positive therefore returns FIRST.

F1 PROBE SHAPES

  (a) sibling suffix
      FIRST

  (b) argv mention only
      FIRST

  (c) exact lane token
      RESUME 1790111734

  (d) exact brief token
      RESUME 1790111734

  (e) cwd inside lane
      RESUME 1790111734

  (f1) spaced exact token
      RESUME 1790111734

  (f2) spaced sibling
      FIRST

  (g) deleted cwd
      FIRST

      readlink:
      /home/rocco/tmp-vt90r2/lanes2/vdel.md--deadbeef (deleted)

      A live lane can reach this only if its cwd is removed while
      the process remains alive. This is abnormal and destructive,
      not the normal re-attach path.

  (h) stale PID
      FIRST

  (i) other-user PID 1
      owner=root
      kill -0 rc=1
      FIRST

Mutants:

  m1 on sibling suffix:
    RESUME 1790111862

  m1 on argv mention:
    RESUME 1790111862

  m5 on spaced exact token:
    FIRST

F1 THROUGH DISPATCHER FAKE BRIDGE

Bad-premise brief:

  Exact brief token:
    state=RESUME 1790111963
    rc=75
    ship_writes=1

  Spaced exact token:
    state=RESUME 1790111963
    rc=75
    ship_writes=1

  Deleted cwd:
    state=FIRST
    rc=64
    ship_writes=0

Here rc 75 is the deliberate MAX_POLLS=0 post-launch result. It proves the RESUME path shipped. FIRST returned rc 64 before any bridge write.

F3 SELF-COPY SHAPES

  Inherited PC_LANE_SELF_COPY only:

    rc=64
    sentinel=EXISTS
    copy=/home/rocco/tmp-vt90r2/f3/tmp/pc_lane.sh.aZVmyU
    copy_exists=no

  Inherited PC_LANE_SELF_COPY and PC_LANE_ORIG:

    rc=64
    sentinel=EXISTS
    copy=/home/rocco/tmp-vt90r2/f3/tmp/pc_lane.sh.cI8Uj6
    copy_exists=no

  Normal invocation:

    rc=64
    copy_debug_lines=1
    copy=/home/rocco/tmp-vt90r2/f3/tmp/pc_lane.sh.VGMUTE
    copy_exists=no

  TMPDIR=/nonexistent:

    rc=64
    private_active_lines=0
    bridge_calls=0

    Reason:
    private copy failed (mktemp/cp): No such file or directory

  Caller-owned file equals $0:

    rc=64
    attacker_file_after=GONE
    private_debug_path=/home/rocco/tmp-vt90r2/f3/attacker-own.sh

This is not a bypass of another principal’s bytes. The caller executes its own file with its own environment. The trap removes that process’s `$0`, as R-F3 specifies.

  Space-bearing caller sentinel:

    rc=64
    sentinel=EXISTS
    copy=/home/rocco/tmp-vt90r2/f3\ space/tmp/pc_lane.sh.OZPWlw
    copy_exists=no

Mutants:

  m3:
    rc=1
    Killing test:
    inherited PC_LANE_SELF_COPY does not skip the private copy
    or delete the caller sentinel

  m4:
    rc=1
    Killing test:
    the EXIT trap removes only its own private-copy path

BLAST RADIUS

ROOT and copy pass:

  scripts/pc_lane.sh:57 unsets:
    PC_LANE_SELF_COPY PC_LANE_ORIG

  scripts/pc_lane.sh:71 execs with:
    PC_LANE_SELF_COPY="$_self" PC_LANE_ORIG="$0"

  scripts/pc_lane.sh:119 derives ROOT from PC_LANE_ORIG.

Relative invocation result:

  relative-invocation rc=64
  self_copy_exists=no

  TRACE_ROOT
    pass_self=/home/rocco/tmp-vt90r2/root/tmp/pc_lane.sh.e21bjN
    orig=scripts/pc_lane.sh
    root=/home/rocco/tmp-vt90r2/root

ROOT is correct. The first pass does not reach ROOT. The copy pass resolves the relative original from the inherited original cwd. The AF-AP-113 `//scripts/pc_bridge_exec.py` failure was not reintroduced.

Dispatcher cwd sweep:

  grep -n '^cd \|cd "' scripts/pc_lane.sh

Only line 119 appeared, inside the ROOT command-substitution subshell. The main dispatcher does not change cwd after trap installation.

Special paths through the fake bridge:

  Quote-bearing repository:
    state=RESUME 1790112350
    rc=75
    ship=1

  Dollar-bearing repository:
    state=RESUME 1790112351
    rc=75
    ship=1

Mode:

  435b057^: 100755
  435b057:  100755
  76ca87c:  100755

The brief’s transient 100644 patch-mode premise does not reproduce from committed Git state. The landed file is executable.

F1 PRODUCTION-PATH DEFECT

The proposed NUL-free read / pipefail explanation is false:

  parent-context state=RESUME\ 1790093003
  diagnostics=read_rc=1 b_len=80

`read` returns 1 because base64 emits no newline. The brace group’s last command is `bridge`, so the pipeline’s status is the bridge status. The command substitution captures RESUME under `set -uo pipefail`.

Exact coordinator launch shape under setsid, nohup, and stdin `/dev/null`:

  Absolute PC_AF_REPO:

    rc=75
    captured_state=RESUME 1790111575
    trace=TRACE_PREMISE_STATE=RESUME 1790111575
    ship_writes=1

  Default-shaped literal PC_AF_REPO='$HOME/tmp-vt90r2/item6/repo':

    rc=64
    captured_state=FIRST
    trace=TRACE_PREMISE_STATE=FIRST
    ship_writes=0

ROOT CAUSE

At scripts/pc_lane.sh:142, PC_AF_REPO defaults to the literal string:

  $HOME/agent-factory

This is intentional for later PC-side expansion.

At scripts/pc_lane.sh:210-211, the dispatcher forms `_PREMISE_LANE_DIR` from that literal value, then base64-encodes it before sending it through the bridge.

The PC bridge executes commands with:

  subprocess.run(["bash", "-lc", cmd], ...)

After the remote shell runs:

  d=$(printf ... | base64 -d)

the decoded `$HOME` is data. The shell does not parse it again as variable syntax.

The probe therefore looks for:

  $HOME/agent-factory/.lanes/<lane>/lane.pid

as a relative literal path. It emits FIRST, re-ships the brief, and reaches the PC duplicate-start guard.

`2>/dev/null` hides the failed PID-file read but is not causal.

MINIMAL FIX SHAPE

Normalize decoded `d` on the remote side before PID-file access:

  case "$d" in
    '$HOME'/*) d="$HOME/${d#'$HOME'/}";;
  esac

Scratch result after this single repair:

  remote-fix-shape rc=75
  state=RESUME 1790113126
  ship_writes=1

This preserves the dispatcher’s existing literal PC_AF_REPO convention. Expanding the default locally would bind it to the sandbox home and is not the correct repair.

PROVIDER-MIX OBSERVATION

Read-only SQLite, last three hours, direct raw-ID calls only:

  direct_raw_rows_last_3h=348
  direct_raw_rows_empty_or_null_combo=348
  direct_raw_rows_matching_raw_id_combo=0

Context:

  agentfactory-build-local, combo execution key set:
    1224 rows

  agentfactory-verify-local, combo execution key set:
    930 rows

  NULL combo, no combo execution key:
    348 rows

scripts/pc_lane.sh:438 sets:

  MIX_COMBO="${HERMES_MODEL:-}"

For a strict raw-ID lane, direct rows have no combo name. The filter `combo_name = 'qwen-local/qwen3.8-27b-local'` therefore matches zero by construction.

This is a follow-up for the next dispatcher lane, not part of the R-F1/R-F3 repair.

FINDING INVENTORY

F1 — BLOCKER

Normal default PC_AF_REPO is decoded into an unexpanded literal `$HOME/...`, so a real re-attach is classified FIRST.

  Evidence:
    SOLID

  Contract mapping:
    R-F1 requires a real resumed lane, including cwd inside the
    lane directory, to return RESUME.

  Canonical path:
    YES. Exact dispatcher payload under the coordinator’s launch
    shape. It matches the recorded first live use.

  Material effect:
    YES. The dispatcher re-ships a live lane’s bad-premise brief
    and reaches duplicate-start refusal instead of re-attaching.

  Discriminator:
    Absolute directory:
      RESUME, rc 75, ship 1

    Default literal $HOME directory:
      FIRST, rc 64, ship 0

    Remote normalization:
      RESUME, rc 75, ship 1

  Ownership:
    YES. The fix belongs in scripts/pc_lane.sh.

  Suggested fix:
    Normalize decoded `d` before PID-file access. Add a test using
    the real symbolic default `$HOME/...`, not only absolute temp
    directories.

  Bug-echo class:
    Representation-boundary expansion loss. A value stored as shell
    syntax for later expansion was encoded and decoded as inert data.

F2 — INFO

A caller-owned script whose `$0` equals PC_LANE_SELF_COPY passes the guard and deletes itself.

  Evidence:
    SOLID

  Contract mapping:
    R-F3 explicitly keys identity and removal to `$0`.

  Material effect:
    The caller deletes its own launched file. No trust boundary is crossed.

  Suggested fix:
    None for this contract.

F3 — INFO

A process whose cwd was deleted returns FIRST.

  Evidence:
    SOLID

  Contract mapping:
    No contract requires re-attachment after destructive cwd removal.

  Suggested fix:
    None in this increment.

F4 — UNVERIFIED EVIDENCE CLAIM

The builder’s RED count and positive-control result do not reproduce.

  Evidence:
    SOLID mismatch

  Reproduction:
    435b057 dispatcher plus PIN test file:
    29 passed, 8 failed

  Material effect:
    The builder’s 33/4 RED evidence is false, but this does not by
    itself falsify the repaired production output.

  Suggested fix:
    Correct the builder report or retain this discrepancy beside it.
    Do not rely on the 33/4 count.

F5 — FOLLOW-UP

The raw-ID provider-mix query matches zero direct rows.

  Evidence:
    SOLID, read-only SQLite

  Contract mapping:
    None for R-F1/R-F3

  Material effect:
    Post-harvest provenance reports no rows despite real raw-ID calls.

  Suggested fix:
    Distinguish raw-ID direct rows from combo-name rows in the next
    dispatcher increment.

PREDICATE TABLE

  F1 default `$HOME` decode:
    Contract mapped:       YES
    Exact production path: YES
    Material effect:       YES
    Discriminator:         YES
    In boundary:           YES
    Disposition:           BLOCKER

  F2 caller-owned `$0`:
    Contract contradiction: NO
    Exact path:             YES
    Cross-boundary effect:  NO
    Disposition:            INFO

  F3 deleted cwd:
    Required RESUME: NO
    Exact path:      YES
    Disposition:     INFO

  F4 RED evidence mismatch:
    Production blocker: NO
    Evidence mismatch:  YES
    Disposition:        UNVERIFIED EVIDENCE CLAIM

  F5 raw-ID mix query:
    R-F1/R-F3 mapping: NO
    Exact path:        YES
    Disposition:       FOLLOW-UP

DISCREPANCIES / DELIBERATE SKIPS

  - Attempt 1 ended on HTTP 503 before producing a draft.
  - The literal RED command produced 29/8, not 33/4.
  - The NUL-free read / pipefail theory did not reproduce.
  - The committed dispatcher mode is 100755 before and after the repair.
  - F2/F4/F5/F6/F7 from VERIFY-T90 were not re-litigated. They remain issue #20.
  - Every mutant and extra dispatcher ran under $HOME/tmp-vt90r2/.
  - No protected real resource was mutated.
  - All scratch processes started by this verification were stopped by PID.
  - The lane tree contains only the requested untracked report.

GATE RECOMMENDATION: NOT-READY

F1 satisfies all five blocking predicates. The normal production default makes the repaired probe inspect an unexpanded literal `$HOME/...` path, so a real live lane is still classified FIRST.

This is a recommendation, not a final gate verdict. The coordinator owns the decision.
