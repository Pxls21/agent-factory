# PC lane — VERIFY-B2 (the adversarial grade of S0-02 round 2, checkpoint f737de5)

PIN: f737de5

Role: adversarial-verifier. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-02-support/VERIFY-B2-brief.md` — READ IT WHOLE and follow it item by item (0-14).
Your worktree IS `git archive f737de5`: the lane's 57 files at their final bytes, its report, VERIFY-B1's report (the round's
contract) and the lane brief are all in the tree at the paths the brief names. Save your report at
`tasks/briefs/s0-02-support/VERIFY-B2-report.md` inside your tree, draft after EACH item (the incremental rule), and return it
whole as your final message.

Venue notes specific to this grade:
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH for every pytest run (the system Python lacks `rfc3339-validator`); an
  absolute `--basetemp` under your lane's scratch dir.
- The pinned Buzz source is `/home/rocco/s0-01-pinned/buzz` (read-only; never build, never modify); no relay delivery, no
  membership write, no role-key read — the live legs are the coordinator's.
- Every hang probe (a FIFO in a leg directory) standalone under `timeout` with a PID-scoped watchdog, never through pytest.
- The identities files carry TEST identities; cite pubkeys only; generate any key you need on scratch and never print it.
