# PC lane — VERIFY-B5j (the adversarial grade of S0-01 frame tee round 15, checkpoint 9b)

PIN: 01499e7

Role: adversarial-verifier. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-01-b5j-support/VERIFY-B5j-brief.md` — READ IT WHOLE and follow it item by item (0-13).
Your worktree IS `git archive 01499e7`: the lane's two files at their final bytes, its report, VERIFY-B5i's report (the round's
contract) and the lane brief are all in the tree at the paths the brief names. Save your report at
`tasks/briefs/s0-01-b5j-support/VERIFY-B5j-report.md` inside your tree, draft after EACH item (the incremental rule), and return it
whole as your final message.

Venue notes specific to this grade:
- Run the tee suite directly with the venue exports (`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`);
  the coordinator's own runs on these bytes: sandbox `lane_gate.sh` two runs (pasted in the checkpoint commit) and the PC
  `116 passed in 44.05s` (8 workers, 20260908T123710Z-298cb55). Agree or disagree by your own run.
- Every hang probe standalone under `timeout` with a PID-scoped watchdog, never through pytest.
- `stress`-like load for item 7 means a few busy loops you start and kill by pid — never more than half the cores, never the
  owner's processes.
- `/proc/<pid>/exe` of another user's process for item 5: read only; pick a system daemon, never the owner's Hermes sessions.
