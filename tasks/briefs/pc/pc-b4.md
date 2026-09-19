# PC lane — B4 (S0-02 round 4: close VERIFY-B3's four BLOCKERs)

PIN: 798ce74

Role: code-implementer. Route: the LOCAL Qwen build route (`agentfactory-build-local`, medium —
the pc_lane.sh default for code-implementer; do NOT set HERMES_MODEL). Venue:
`tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path.

**The brief governs**: `tasks/briefs/pc/report-pc-verify-b3.md--c6c384a.md` (the full VERIFY-B3
report, PIN c6c384a) — READ IT WHOLE. Close its four BLOCKERs (B3-00, B3-01, B3-02, B3-03) with the
EXACT red controls it names. B3-04 is a FOLLOW-UP outside your scope (the coordinator's S0-11
re-sign) — do NOT touch it. Your worktree IS `git archive 798ce74` plus the lane patch (this brief).
Save your report at `tasks/briefs/s0-02-support/B4-report.md`, draft after EACH item (the incremental
rule), and return it whole as your final message.

The four blockers and their FROZEN red discriminators (make each named mutant die; a fix with no
red control is NOT done):

1. **B3-01 — the closure table-drift test does not parse the runner's writes.** Four runner
   output-write forms each leave `test_closure_table_covers_all_producer_and_runner_writes`
   (`T:1373-1383`) green: `RUNNER-TEE-UNSEEN` (`tee "$out/x-tee"`), `RUNNER-HEREDOC-UNSEEN`
   (`cat > "$out/x-heredoc"`), `RUNNER-PYTHON-UNSEEN` (`python3 -c ...Path(...).write_text`),
   `RUNNER-MV-UNSEEN` (`mv` into `$out/x-mv`). Fix: a deliberately BOUNDED parser/allowlist over
   every output-write form the runner permits, OR a structural runner-output contract that
   enumerates all final outputs and is exercised by an actual fake-output run. Red control: each
   of the four mutations above must make the table-drift test FAIL. (This is the AF-AP-96 class —
   a source parser as a closure oracle is inherently incomplete; the durable execute-and-diff-STATE
   rewrite is already filed as issue #5. Your job is the BOUNDED parser that kills the four named
   forms, with the domain stated — not an unbounded shell-dataflow engine.)

2. **B3-02 — the tolerance/runner-gap relations are untested.** `TOLERANCE-9000` (change the
   RELAY_DRIFT_WINDOW constant `C:127` 150→9000) and `RUNNER-GAP-151` (change the runner default
   replay wait `R:34` 100→151) both leave all tests green. Fix: add the two literal relationship
   assertions — `REPLAY_CLOCK_TOLERANCE_S + LEG_CLOCK_TOLERANCE_S < RELAY_DRIFT_WINDOW_S` and the
   runner-gap `<= REPLAY_CLOCK_TOLERANCE_S` — plus their mutation tests. Red controls: TOLERANCE-9000
   and RUNNER-GAP-151 must each red.

3. **B3-03 — the checker's fallback removal-label is unbound.** `LABEL-FALLBACK-DROPPED` (alter the
   fallback-only occurrence at `C:717-720`) survives (`2 passed`). Fix: REMOVE the unreachable
   fallback, OR test its exact full sentence. Red control: LABEL-FALLBACK-DROPPED must fail.

4. **B3-00 — the B3 report discipline items 7-9 were omitted while claimed.** Produce a GROUNDED
   B4 report: the required top-of-report stamp in `tasks/briefs/s0-02-support/VERIFY-B2-report.md`,
   B4's final-byte identity table, machine-checkable `file:line` anchors, `report_lint` output above
   its floor, the `ap_screen` paste, the pack, and a NAMED mutant/killer inventory with real killer
   lines (the four B3-01 forms + TOLERANCE-9000 + RUNNER-GAP-151 + LABEL-FALLBACK-DROPPED, each with
   its killer test). A report that cites nothing lints clean by construction — cite real anchors.

## Boundary (touch ONLY these)
- `proofs/S0-02/check_buzz_authz.py` (the checker — B3-02/B3-03 assertions)
- `proofs/S0-02/tools/pc/run_s0_02_legs.sh` / `deliver_event.py` (READ for the closure table; do not
  change the runner's real output set to game the test — fix the TEST/oracle)
- `proofs/S0-02/spec.json`, `proofs/S0-02/fixtures/**`
- `tests/test_s0_02_buzz_authz.py` (the meta-tests + the four new red controls + the two relations)
- `tasks/briefs/s0-02-support/B4-report.md` (your report), `VERIFY-B2-report.md` (the stamp)

`proofs/schemas/**` is OFF LIMITS (it is an attested input of five minted results; B3 already added
`limits`). `proofs/S0-01/*` is read-only. Report adjacent defects, never fix them.

## Gate (a script, not a paragraph)
- Venue exports before every gate run: `S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`,
  `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`,
  `/home/rocco/venv-agent-factory/bin` FIRST on PATH; an absolute SHORT `--basetemp` under your
  lane's scratch.
- The pytest gate is `scripts/pc_suite.sh launch -n 8 -- tests/test_s0_02_buzz_authz.py` then
  `wait <RUN_ID>` (fits under Hermes's 420 s terminal cap; the serial run does not). Paste the
  `pytest-summary:` + `pytest-set:` lines verbatim. Then run each named mutant on a SCRATCH copy
  (never git-restore/stash the shared tree) and paste its kill line.
- `report_lint` gates on a FLOOR, not `MISS 0`; apply its `fix:` hints for at most THREE rounds,
  then paste and finish. CODE INTEL FIRST: `graft ask` / `ripwire` before grep; the pack is built
  at launch.
- No relay delivery, no live leg, no membership write — those are the coordinator's live capture.
  `deliver_event.py` and the runner are read/`bash -n`/pyflakes-checked/unit-tested in-process only.

Under D-034 these are test-strength/report-discipline findings on a checker whose CORE authz
capability the verifier reproduced SOLID; the owner directed this build round. Close the four named
red controls, prove them, STOP — do not widen scope beyond the boundary.
