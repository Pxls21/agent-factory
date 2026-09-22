REVIEW-PENDING — T90-R2 code-implementer proposal; independent sandbox adversarial-verifier has NOT run.

IDENTITY
  pin: 435b057a0af7ba01be130306e5c27d2d9ee3f6d2
  boundary: scripts/pc_lane.sh + harness-ports/tests/test_pc_lane_dispatcher.sh
  component: sandbox dispatcher D
  contract: VERIFY-T90 F1 + F3 only

FILES / LINES CHANGED
  scripts/pc_lane.sh:52-78 — `PC_LANE_SELF_COPY`, `PC_LANE_ORIG`, `trap`
    - trust PC_LANE_SELF_COPY only when `$0` equals it and PC_LANE_ORIG is present
    - unset inherited self-copy/original values before the existing mktemp/cp/exec path
    - EXIT trap removes `$0`, never a mutable environment value
  scripts/pc_lane.sh:203-211 — `_PREMISE_LANE_DIR`, `_premise_state`, `cmdline`
    - bind RESUME by cwd containment or exact NUL-delimited argv token only
    - accepted argv tokens: lane dir or lane dir/brief.md
    - base64-transfer the lane path into the PC-side probe so spaces remain one path
  harness-ports/tests/test_pc_lane_dispatcher.sh:48-66 — `bridge`, `premise_out`, `PC_LANE_TEST_PREMISE_CAPTURE`
    - fake bridge captures evaluated premise state
  harness-ports/tests/test_pc_lane_dispatcher.sh:104-112 — `run_gate`, `GATE_RC`, `PC_LANE_TEST_AF_REPO`
    - every premise test reaches the dispatcher through the fake bridge
  harness-ports/tests/test_pc_lane_dispatcher.sh:114-140 — `run_copy`, `RUN_COPY_DISPATCHER`, `run_inherited_copy`
    - inherited self-copy and trap-ownership controls
  harness-ports/tests/test_pc_lane_dispatcher.sh:164-216 — `CALLER_SENTINEL`, `TRAP_MUTANT`, `TRAP_REASON`
    - private-copy removal and caller-owned-path preservation controls
  harness-ports/tests/test_pc_lane_dispatcher.sh:234-261 — `assert_first_refusal`, `PROBE_STATE`, `PROBE_SLEEPER`
    - pidfile-bound sibling and argv-mention refusal controls
  harness-ports/tests/test_pc_lane_dispatcher.sh:262-302 — `start_probe_process`, `PROBE_SIBLING`, `PROBE_LANE_SPACED`
    - exact-token positive control carries a spaced lane path
  harness-ports/tests/test_pc_lane_dispatcher.sh:304-317 — `LANE_PID`, `PC_LANE_TEST_LANE_PID`, `GATE_RC`
    - existing cwd-bound RESUME control remains green

PREMISE — VERIFIED
  git diff --stat c49880c 435b057 -- scripts/pc_lane.sh harness-ports/tests/test_pc_lane_dispatcher.sh
  output: empty; rc=0

  sha256sum scripts/pc_lane.sh
  309d5cabe68ab150b25e37d41a24cea6743ed24fc169eb547b4ad9c2930791ef  scripts/pc_lane.sh

  grep -cF 'in *\"\$d\"*)' scripts/pc_lane.sh
  1
  grep -c 'check "' harness-ports/tests/test_pc_lane_dispatcher.sh
  24
  wc -l scripts/pc_lane.sh harness-ports/tests/test_pc_lane_dispatcher.sh
    555 scripts/pc_lane.sh
    303 harness-ports/tests/test_pc_lane_dispatcher.sh
    858 total

RED -> GREEN
  RED at PIN, before production repair:
    [FAIL] an inherited PC_LANE_SELF_COPY does not skip the private copy or delete the caller sentinel
             because: rc=64 private_copy=/tmp/tmp.5B2226agrg/caller-self-copy-sentinel private_copy_exists=no sentinel_exists=no bridge_calls=1
    [FAIL] the EXIT trap removes only its own private-copy path
             because: rc=64 private_copy=/tmp/tmp.5B2226agrg/copy-inherited/pc_lane.sh.UlAyPs private_copy_exists=no other_path_exists=yes
    [FAIL] a sibling suffix id is FIRST and refused with no ship write
             because: state=RESUME 1790097243 rc=75 no_ship_writes=1 pid=2570073
    [FAIL] an argv mention alone is FIRST and refused with no ship write
             because: state=RESUME 1790097243 rc=75 no_ship_writes=1 pid=2570135
    [PASS] an argv token equal to the lane dir is RESUME and ships
             because: state=RESUME 1790000000 rc=75 ship_writes=1 pid=2570196
    pc_lane dispatcher: 33 passed, 4 failed

  GREEN after repair, run 1:
    [PASS] an inherited PC_LANE_SELF_COPY does not skip the private copy or delete the caller sentinel
             because: rc=64 private_copy=/tmp/tmp.pJefkw1cM2/copy-inherited/pc_lane.sh.AFq3iy private_copy_exists=no sentinel_exists=yes bridge_calls=1
    [PASS] the EXIT trap removes only its own private-copy path
             because: reason=mutant-other-path-deleted rc=64 private_copy=/tmp/tmp.pJefkw1cM2/copy-inherited/pc_lane.sh.apXUa3 private_copy_exists=no other_path_exists=no
    [PASS] a sibling suffix id is FIRST and refused with no ship write
             because: state=FIRST rc=64 no_ship_writes=0 pid=2695491
    [PASS] an argv mention alone is FIRST and refused with no ship write
             because: state=FIRST rc=64 no_ship_writes=0 pid=2695539
    [PASS] an argv token equal to the lane dir is RESUME and ships
             because: state=RESUME 1790000000 rc=75 ship_writes=1 pid=2695582
    pc_lane dispatcher: 37 passed, 0 failed

  GREEN run 2:
    pc_lane dispatcher: 37 passed, 0 failed

  Normalized deterministic comparison:
    normalized-bitwise-compare=0
  Normalization replaced only mktemp names, fixture pids, current timestamps/epochs, and base64 path payloads.

MUTANTS
  m1 restore substring binding `*"$d"*`: rc=1
    [FAIL] a sibling suffix id is FIRST and refused with no ship write
    [FAIL] an argv mention alone is FIRST and refused with no ship write

  m2 drop argv-token test: rc=1
    [FAIL] an argv token equal to the lane dir is RESUME and ships

  m3 drop `[ "$0" = "$PC_LANE_SELF_COPY" ]`: rc=1
    [FAIL] an inherited PC_LANE_SELF_COPY does not skip the private copy or delete the caller sentinel

  m4 restore variable-owned trap `rm -f "${PC_LANE_SELF_COPY:-}"`: rc=1
    [FAIL] the EXIT trap removes only its own private-copy path

  m5 split cmdline on spaces instead of NUL: rc=1
    [FAIL] an argv token equal to the lane dir is RESUME and ships

  Restore identity after each mutant:
    scripts/pc_lane.sh: OK
    harness-ports/tests/test_pc_lane_dispatcher.sh: OK

GATES
  bash -n scripts/pc_lane.sh
  rc=0

  bash -n harness-ports/tests/test_pc_lane_dispatcher.sh
  rc=0

  bash harness-ports/tests/test_pc_lane_dispatcher.sh
  pc_lane dispatcher: 37 passed, 0 failed

  bash harness-ports/tests/test_pc_lane_dispatcher.sh
  pc_lane dispatcher: 37 passed, 0 failed

  bash harness-ports/tests/run-all.sh
  test_codex_hook_adapter.py         7/7 passed
  test_hermes_hook_adapter.py        6/6 passed
  test_hermes_spool.py               9/9 passed
  test_bridge_token_handling.py      test_bridge_token_handling: 9 checks passed — ALL OK
  test_pc_bridge_exec.py             test_pc_bridge_exec: 8 checks passed
  test_hermes_session_export.py      test_hermes_session_export: 13 checks passed
  test_omniroute_local_builder.py    test_omniroute_local_builder: 24 checks passed
  test_pc_lane.sh                    59 passed, 0 failed
  test_pc_lane_dispatcher.sh         pc_lane dispatcher: 37 passed, 0 failed
  test_pc_lane_admission.sh          22 passed, 0 failed
  test_qwen_server.sh                qwen-server: 101 passed, 0 failed
  test_qwen_matrix.py                test_qwen_matrix: 4 tests passed
  test_qwen_matrix_sh.sh             qwen-matrix-sh: 16 passed, 0 failed
  test_lane_context.sh               5 passed, 0 failed
  test_context_mirrors.sh            11 passed, 0 failed
  test_sync_skills.sh                34 passed, 0 failed
  build-roles --check                OK: 3 role config layers match their sources
  ALL SUITES PASSED
  rc=0

  python3 scripts/ap_screen.py --tests scripts/pc_lane.sh harness-ports/tests/test_pc_lane_dispatcher.sh
  --- TEST_SCREEN over 2 path(s): 3 hits over 2 files ---
  AF-AP-87: 2
      scripts/pc_lane.sh:383 — `probe`
      scripts/pc_lane.sh:383 — `REMOTE_REPORT`
  AF-AP-59: 1
      scripts/pc_lane.sh:375 — `launch.log`
  classification: all three are pre-existing at PIN; outside F1/F3 hunks.

  python3 scripts/ap_screen.py scripts/pc_lane.sh harness-ports/tests/test_pc_lane_dispatcher.sh
  --- AP_SCREEN over 2 path(s): 1 hits over 2 files ---
  AP-44: 1
      harness-ports/tests/test_pc_lane_dispatcher.sh:104 — `run_gate`
  classification: pre-existing run_gate helper, moved by added lines; outside semantic repair.

  git diff --check
  rc=0

  final hashes after mutant restores:
    ef6b64a1d8fcfc993e6ba7202e2b5d5f637156ed4479f6a170d7f61ad7da6065  scripts/pc_lane.sh
    f74d7e0a3419dcb7939ddc3233b5b9e7e2cfcae9846207b99eedbe75eaa7aa5f  harness-ports/tests/test_pc_lane_dispatcher.sh

SELF-ATTACK
  1. Wrong green: exact-token code could silently split on spaces.
     Ruled out: positive token path uses a lane directory containing a space; m5 space-split mutant fails that named test.
  2. Wrong green: inherited PC_LANE_SELF_COPY could still skip the mktemp/cp/exec path.
     Ruled out: sentinel path differs from $0; stderr records `pc_lane.sh.XXXXXX`; m3 kills the named test.
  3. Wrong green: the trap test could prove only one file survived, not ownership.
     Ruled out: positive leg asserts real private copy absent and caller path present; planted trap mutant deletes the caller path; external m4 also kills the named test.

DISCREPANCIES
  - The brief's prescribed `python3 scripts/ap_screen.py scripts/pc_lane.sh --tests testfile` argument order is rejected by argparse (`unrecognized arguments`). Executed equivalent accepted form: `python3 scripts/ap_screen.py --tests scripts/pc_lane.sh harness-ports/tests/test_pc_lane_dispatcher.sh`.
  - `python3 -m pyflakes` is unavailable (`No module named pyflakes`). Both boundary files are Bash; bash -n ran on both.
  - `bash scripts/test_summary.sh harness-ports/tests/test_pc_lane_dispatcher.sh` is inapplicable: the helper invokes pytest and returned `ERROR: not found ... test_pc_lane_dispatcher.sh`, `pytest-exit: 4`. Test counts are therefore pasted from the shell test's own `pc_lane dispatcher: 37 passed, 0 failed` producer.
  - GitNexus `detect-changes` returned `No changes detected` because its clone index does not see this detached lane. Graft/ripwire/CRG report these shell symbols as unmapped/risk UNKNOWN; no low-risk claim made.
  - report_lint: 13 refs — OK 10, NEAR 3, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree). The three NEAR refs are pasted pre-existing anti-pattern-screen rows outside the repair hunks.
  - The EXIT-trap test includes a scratch mutant as its negative control. External m4 independently restores the variable trap in production and kills the same named test.

NOT DONE
  - F2, F4, F5, F6, F7: issue #20; outside this focused repair.
  - harness-ports/bin/pc-lane.sh: untouched and outside boundary.
  - Ledger, wiki, VERIFY-T90 report, and briefs: untouched.
  - No commit, push, PR, comment, or other outward action.
  - Independent sandbox adversarial-verifier: NOT run here; this remains a proposal until that lane grades it.

REASONING RECORD FOR COORDINATOR
  TWO production hunks:
  1. Structural process identity: retain cwd containment and replace substring cmdline matching with exact NUL-delimited argv equality. Reject word splitting because a path with spaces must remain one token. Base64 carries the lane path into the quoted bridge command without shell interpolation.
  2. Self-copy ownership: an ambient variable is not proof of execution identity. Require `$0 == PC_LANE_SELF_COPY` plus PC_LANE_ORIG, clear inherited values before copying, and key cleanup to `$0`.
  Primary sources: live `/proc/<pid>/cwd` and `/proc/<pid>/cmdline` probes; current dispatcher/test bytes at PIN; `scripts/why.sh` history for the self-copy and premise gate.

RETRO
  New general lesson: NUL-safe token tests must include a path with spaces; otherwise a space-splitting mutant can survive. This is an anti-hollow-green instance already covered by the loaded skill's mutation and production-shape fixture rules; no skill edit needed.
