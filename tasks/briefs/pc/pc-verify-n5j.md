# PC continuation — VERIFY-N5j (the adversarial grade of S0-01 ACP probe round 13, checkpoint 9d)

PIN: fe2dc3b

Role: adversarial-verifier. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

## CONTINUATION (read second)
This lane is the FIRST run of the grade — nothing precedes it; start at item 0.

**The brief governs**: `tasks/briefs/s0-01-n5j-support/VERIFY-N5j-brief.md` — READ IT WHOLE and follow it item by item (0-11). Your
worktree IS `git archive fe2dc3b` plus the lane patch (the brief + this file); the lane's report `tasks/briefs/s0-01-n5j-support/N5j-report.md`
and VERIFY-N5i's report `tasks/briefs/s0-01-n5i-support/VERIFY-N5i-report.md` are IN the archive. Save your report at
`tasks/briefs/s0-01-n5j-support/VERIFY-N5j-report.md` inside your tree, draft after EACH item (the incremental rule), and return it whole as
your final message.

Venue notes specific to this grade:
- You are on the PC: run the test files directly with the venue exports (`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`;
  the checker's real-leg tests need that corpus). `/home/rocco/venv-agent-factory/bin` FIRST on PATH; an absolute `--basetemp` under your lane's
  scratch dir; the four-file set with `-n 4` or `-n 8` in ONE foreground call (the lane's `595 passed, 9 xfailed in 210.82s`); the serial
  four-file run only if it fits your tool ceiling in one call — otherwise declare it NOT-run, as the lane did.
- The pinned sources for item 4 (what a hostile agent can do to its own interpreter path after exec) are `/home/rocco/s0-01-pinned/acp`
  (buzz-acp) and `/home/rocco/s0-01-pinned/hermes-agent` (READ-ONLY). You never launch the real agent, Hermes, buzz-acp, the relay or a model
  request here; every fixture agent is your own script under `timeout`.
- Every FIFO/hang probe under `timeout` and standalone, never through pytest; the probe's real leg is NOT run here.
- Seven Stage 0 lanes share this host (B3, B5k, D5n, G3, M3, O3, P5c-c) — never touch their trees, `proofs/`, or `tests/test_s0_*` outside your
  own private copy; every mutant on a scratch copy of your archive.
