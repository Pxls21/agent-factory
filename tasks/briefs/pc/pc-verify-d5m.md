# PC lane — VERIFY-D5m (the adversarial grade of S0-01 backend round 16, on the lane's own tree shape)

PIN: 246bec7

Role: adversarial-verifier. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-01-d5m-support/VERIFY-D5m-brief.md` — READ IT WHOLE and follow it item by item (0-11).
Your worktree is `git archive 246bec7` PLUS the lane patch pc-lane.sh applied before you started (`git status --porcelain`
lists it): lane P5b's unlanded context files, D5m's FINAL bytes, the lane's report, VERIFY-D5l's report and the brief — the
same tree shape lane D5m gated in (`548 passed` ×2). There is NO pushed checkpoint for this round yet: D5m lands jointly with
P5b and A5k, so your identity table (sha256 of every patched file) is what binds your verdict to the bytes. Save your report
at `tasks/briefs/s0-01-d5m-support/VERIFY-D5m-report.md` inside your tree, draft after EACH item (the incremental rule), and
return it whole as your final message.

Venue notes specific to this grade:
- Run the two test files directly with the venue exports (`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`).
- Every FIFO/hang probe standalone under `timeout` with a PID-scoped watchdog, never through pytest — a deadlocked
  pytest+backend pair is the failure class this round closes.
- `cost_probe.py` for item 6 runs against a backend YOU start on a free loopback port and stop by pid; state the load before
  and after (the other lanes share this box).
