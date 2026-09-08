# PC lane — VERIFY-CK13 (the adversarial grade of S0-01 checker round 13 on the joint checkpoint)

PIN: 77f46a2

Role: adversarial-verifier. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-01-a5k-support/VERIFY-CK13-brief.md` — READ IT WHOLE and follow it item by item (0-11).
Your worktree IS `git archive 77f46a2`: the joint checkpoint's bytes (A5k's checker round, P5b's PC tools, D5m's backend, the
merged pins.py), the lane's report, VERIFY-CK12's report (the round's contract), P5b's report and the lane brief are all in the
tree at the paths the brief names. Save your report at `tasks/briefs/s0-01-a5k-support/VERIFY-CK13-report.md` inside your
tree, draft after EACH item (the incremental rule), and return it whole as your final message.

Venue notes specific to this grade:
- The headline suite (`tests/test_s0_01_check_acp_conformance.py`, ~12 min single-process) runs with the venue exports; run it
  in ONE foreground call if your terminal allows, else as a bounded background process you explicitly await with a durable rc
  file — say which. `pytest -n` is available in the venv (`-n 8` on this box is fine while the other lanes run; state the load).
- The real corpus is `/home/rocco/s0-01-pinned/realleg/golden` (read-only); item 7 decides what the checker's ROOT should be.
- Every FIFO/hang probe standalone under `timeout` with a PID-scoped watchdog, never through pytest.
- You never launch the real agent, buzz-acp or Hermes here; the producer's process rows for item 1 come from a synthetic ps
  table (the tests' shim) and the collected corpus scans.
