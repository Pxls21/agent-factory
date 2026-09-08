# PC lane — VERIFY-M2 (the adversarial grade of S0-06 four-scope round 2)

PIN: cb91edf

Role: adversarial-verifier. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-06-support/VERIFY-M2-brief.md` — READ IT WHOLE and follow it item by item (0-13).
Your worktree IS `git archive cb91edf`: the round's 55 files at their final bytes, the lane's report, VERIFY-M1's report (the
round's contract) and the lane brief are all in the tree at the paths the brief names. Save your report at
`tasks/briefs/s0-06-support/VERIFY-M2-report.md` inside your tree, draft after EACH item (the incremental rule), and return it
whole as your final message.

Venue notes specific to this grade:
- Run the four test files the lane brief names directly (`tests/test_s0_06_four_scope.py tests/test_spec_probe_schemas.py
  tests/test_validate_ledger.py tests/test_proof_runner.py`) with the venue exports; the coordinator's runs on these bytes:
  sandbox `236 passed` ×2 (lane_gate), PC `236 passed in 7.84s` (8 workers). Agree or disagree by your own run.
- There is NO ai-memory checkout or binary on this host for you: the adapter's tests use loopback recording servers you start
  and kill by pid. Never clone, build or start ai-memory; the live PC leg is not this grade's.
- Every FIFO/hang probe standalone under `timeout` with a PID-scoped watchdog, never through pytest.
