# PC lane — VERIFY-M3 (the adversarial grade of S0-06 four-scope round 3)

PIN: e776dd0

Role: adversarial-verifier. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-06-support/VERIFY-M3-brief.md` — READ IT WHOLE and follow it item by item (0-12).
Your worktree IS `git archive e776dd0` plus the lane patch (the brief + this file): the round's 58 files at their final bytes, the
lane's report, VERIFY-M2's report (the round's contract) and the lane brief are all in the tree at the paths the brief names. Save your
report at `tasks/briefs/s0-06-support/VERIFY-M3-report.md` inside your tree, draft after EACH item (the incremental rule), and return it
whole as your final message.

Venue notes specific to this grade:
- Run `tests/test_s0_06_four_scope.py` directly with the venue exports and an absolute `--basetemp` under your lane's scratch dir; the
  coordinator's runs on these bytes: sandbox `214 passed` ×2 (lane_gate), PC `214 passed in 7.41s` (8 workers). Agree or disagree by your
  own run. `/home/rocco/venv-agent-factory/bin` FIRST on PATH.
- There is NO ai-memory checkout or binary on this host for you: the adapter's tests use loopback recording servers you start and kill
  by pid. Never clone, build or start ai-memory; the live PC leg is not this grade's.
- Every FIFO/hang probe standalone under `timeout` with a PID-scoped watchdog, never through pytest; the generator's rmtree probe (item 6)
  only on a scratch directory you created.
- Seven Stage 0 lanes share this host (B3, B5k, D5n, G3, O3, P5c-c, VERIFY-N5j) — never touch their trees, `proofs/`, or `tests/` outside
  your own private copy; every mutant on a scratch copy of your archive.
