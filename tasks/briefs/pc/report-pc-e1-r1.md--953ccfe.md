Mechanically gated: the S0-05 checker now rejects every mechanism except exact `veth-iptables` before gate-state or canary evaluation. This is a proposal until the sandbox adversarial-verifier grades it.

NOT DONE

- The root-only motivating-instance test was not executed on this uid-1000 PC.
- The sandbox must run that test against both the PIN checker and repaired checker.
- VERIFY-E1 F2-F24, live production-unit legs, proof regeneration, and minting remain out of scope.
- No commit, stage, push, proof-runner invocation, or outward-facing action occurred.

FILES

- `proofs/S0-05/check_egress.py:78-81,326-340`
  - Added `MECHANISM = "veth-iptables"`.
  - Added exact-equality validation immediately after `read_gate`.
  - Invalid mechanisms fail with `total-isolation: <unit> mechanism=<value>`.
  - The mechanism check precedes `gate-disabled` and all PHASE 2 checks.

- `proofs/S0-05/spec.json:33-40`
  - Re-pinned bare-unshare to `total-isolation: curl mechanism=netns-no-veth`.

- `tests/test_s0_05_egress.py:138-176,637-650,754-862`
  - Renamed the bare-unshare test and pinned the class reason.
  - Added wrong, empty, list, and trailing-space mechanism controls.
  - Added the mechanism-before-gate ORDER control.
  - Added the root-only live topology test using the real library, collector, and checker.
  - The live test uses an internal addressed veth pair, an in-namespace loopback listener, PID-scoped cleanup, namespace destroy-by-name, and a final namespace census.

- `tasks/briefs/s0-05-support/E1-R1-report.md`
  - Full evidence report.

PREMISE

Verified at PIN `953ccfe`:

- C SHA first 16: `59b884c6e60fa784`
- T SHA first 16: `6c96693ad4063c35`
- S SHA first 16: `0751bf678f50349e`
- `git log --oneline 24e80e6..953ccfe -- proofs/S0-05 tests/test_s0_05_egress.py` was empty.
- The seed says bare unshare is total-block and not acceptable evidence.
- `netns_lib.sh` emits `veth-iptables` or `netns-no-veth`.
- `run_canaries.sh` records that observed value.
- The PIN checker required the `mechanism` key but did not assert its value.

HOLLOW GREEN REPRODUCTION

A copy of `evidence-mechanism-sandbox` with only `mechanism=netns-no-veth` produced:

    PASS: S0-05 no-direct-egress - 1 units, 11 canaries failed as required, positive controls 1/1
    rc=0
    Tue Sep 22 07:26:34 AM UTC 2026

RED-FIRST

Before the checker change:

    6 failed, 98 deselected in 0.50s
    PYTEST_RC=1
    Tue Sep 22 08:08:06 AM UTC 2026

Failures covered:

- Bare-unshare still emitted `positive-control-failed`.
- Four mechanism mutations returned rc 0 PASS.
- Wrong mechanism plus disabled gate emitted `egress-permitted: gate-disabled`.

After the checker change:

    6 passed, 98 deselected in 0.24s
    PYTEST_RC=0
    Tue Sep 22 08:11:00 AM UTC 2026

Spec-leg targeted run:

    2 passed, 102 deselected in 0.22s
    PYTEST_RC=0
    Tue Sep 22 08:12:11 AM UTC 2026

LIVE TEST STATUS

The new live test skipped as required on this host:

    SKIPPED: network-namespace legs need root + iproute2 + iptables
    1 skipped, 103 deselected in 0.11s
    PYTEST_RC=0
    Tue Sep 22 08:15:09 AM UTC 2026

Evidence tier: structurally checked, not empirically executed here. Sandbox execution is mandatory before acceptance.

MUTANTS

All mutations were applied to `/tmp/e1r1/mutant/repo`, compile-checked, and killed:

- M1 guard deleted:
  - `6 failed, 98 deselected in 0.36s`

- M2 allow-list widened to include `netns-no-veth`:
  - `2 failed, 3 passed, 99 deselected in 0.28s`

- M3 guard moved after positive control:
  - `2 failed, 102 deselected in 0.19s`
  - Bare-unshare regressed to `positive-control-failed`.
  - ORDER regressed to `gate-disabled`.

- M4 reason renamed:
  - `6 failed, 98 deselected in 0.50s`
  - Bare-unshare, fixture mutations, and spec-leg consumer killed it.

- M5 `!=` changed to `is not`:
  - `2 failed, 4 passed, 98 deselected in 0.32s`
  - Both positive bundles were falsely rejected.
  - This mutant did not survive.

Scratch checker SHA before and after:

    5b766582a9a03f916201102d8b1f46dec4ce9bb294981bf17cb33be1eaaed0e6

FINAL GATES

Set: `tests/test_s0_05_egress.py`

Collection:

    104 tests collected in 0.05s

Run 1:

    99 passed, 5 skipped in 2.81s
    PYTEST_RC=0
    Tue Sep 22 08:19:17 AM UTC 2026

Run 2:

    99 passed, 5 skipped in 2.76s
    PYTEST_RC=0
    Tue Sep 22 08:19:39 AM UTC 2026

Mechanical count from `scripts/test_summary.sh`:

    pytest-exit: 0
    pytest-summary: 99 passed, 5 skipped in 2.73s
    TEST_SUMMARY_RC=0

Other gates:

    PY_COMPILE_RC=0
    PYFLAKES_RC=0
    DIFF_CHECK_RC=0

Screens:

    python3 scripts/ap_screen.py proofs/S0-05
    AP-32: 1

    python3 scripts/ap_screen.py proofs/S0-05 proofs/S0-05/canaries
    AF-AP-72: 2
    AP-32: 1

    python3 scripts/ap_screen.py --tests tests/test_s0_05_egress.py
    0 hits

All screen hits are pre-existing. No new hit was introduced.

FINAL IDENTITIES

- C: `5b766582a9a03f91`, 375 lines
- T: `7545714460183c94`, 873 lines
- S: `ed6edbd1c408ad83`, 43 lines
- L unchanged: `1b2bd911d54262d3`, 209 lines
- R unchanged: `6f7298077aa39819`, 131 lines
- Report: `1018a0816cc2d2d232048cd45177c681debd36af1e74e5d0b41452bcd56b2b54`, 215 lines

Untouched-boundary check returned rc 0 for:

- `netns_lib.sh`
- `run_canaries.sh`
- fixtures and provenance
- PC runner
- schemas
- `CLAUDE.md`

SELF-ATTACK

1. The root-only topology might not reproduce F1 exactly. This is not empirically ruled out here. Sandbox execution remains mandatory.
2. The mechanism verdict might occur too late. The combined wrong-mechanism plus disabled-gate control and M3 rule this out.
3. Unknown or padded mechanism values might pass. Empty, list, trailing-space, and wrong-value controls plus M2 rule this out.

DISCREPANCIES

- `VERIFY-E1-report.md` is absent at PIN `953ccfe`; it exists in later commit `df04e61`. I read that immutable object to recover the exact F1 topology.
- The PC baseline was `94 passed, 4 skipped`, not the sandbox’s `98 passed`.
- `pc_suite.sh set-id` is a sandbox bridge command and was not run here. The equivalent one-file set digest is `9f0502080347`.
- The brief expected three AP-screen hits from `ap_screen.py proofs/S0-05`; that exact command prints one. Including `proofs/S0-05/canaries` reproduces all three.
- M5 was killed rather than surviving.
- Final bounded `report_lint.py` result:
  - `19 refs — OK 13, NEAR 0, MISS 6, UNCHECKABLE 0, UNRESOLVED 0`
  - The six misses are new working-tree-only T ranges checked against the required PIN revision.
  - The minimum reference floor of 12 passed.
  - Stopped after two rounds per AF-AP-76.

HYGIENE

- `ip netns list`: no output, rc 0.
- Listener census: none found, rc 1.
- No namespace was created on this PC.
- Only C, S, T, and the requested report are modified.
- GitNexus `detect-changes`: 3 code files, 7 symbols, risk medium, 2 affected processes.
- Full report:
  `/home/rocco/agent-factory/.lanes/pc-e1-r1.md--953ccfe/tree/tasks/briefs/s0-05-support/E1-R1-report.md`

Retro: no new general lesson to bake. The lane-context CLI argument-shape quirk is recorded in the report.

graft saved approximately 4,102 tokens this turn.
