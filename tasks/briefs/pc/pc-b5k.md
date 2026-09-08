# PC lane — B5k (S0-01 frame tee round 16)

PIN: 5e4f816

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-01-b5k-tee-sentences-not-lines-aliases-not-names-every-census-spelling.md` — READ IT
WHOLE and build it item by item (1-5). Your worktree IS `git archive 5e4f816` plus this brief (shipped as the lane patch): the
tee's two files at their checkpoint-9b bytes, VERIFY-B5j's report (the round's contract) at
`tasks/briefs/s0-01-b5j-support/VERIFY-B5j-report.md`, VERIFY-B5i's report and the B5j report beside it. Write your report at
`tasks/briefs/s0-01-b5k-support/B5k-report.md` inside your tree, draft after EACH item (the incremental rule), and return it
whole as your final message.

Venue notes:
- Run the tee suite directly with the venue exports (`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`),
  twice on the FINAL bytes, counts pasted verbatim; every FIFO/hang probe standalone under `timeout` with a PID-scoped watchdog.
- The verify lanes CK13/P5b/D5m/N5i/M2/G2 share this box: state the load before long runs; never touch another lane's dir.
