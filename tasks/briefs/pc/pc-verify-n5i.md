# PC continuation — VERIFY-N5i (the adversarial grade of S0-01 ACP probe round 12, checkpoint 9a)

PIN: 628da83

Role: adversarial-verifier. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

## CONTINUATION (read second)
This lane CONTINUES the sandbox VERIFY-N5i lane, which the sandbox's model quota stopped on 2026-09-08 at ~05:18Z while it was
still reading ("Now the test file's key sections — the AST self-scan first."). Nothing of its work survives; start the grade
from item 0.

**The brief governs**: `tasks/briefs/s0-01-n5i-support/VERIFY-N5i-brief.md` — READ IT WHOLE and follow it item by item (0-11).
Your worktree IS `git archive 628da83` plus ONE shipped file, VERIFY-N5h's report at
`tasks/briefs/s0-01-n5i-support/VERIFY-N5h-report.md` (the brief cites it at a sandbox scratchpad path). Save your report at
`tasks/briefs/s0-01-n5i-support/VERIFY-N5i-report.md` inside your tree, draft after EACH item, and return it whole as your final
message.

Venue notes specific to this grade:
- The brief's "ONE bridge action" (the pytest-only PC gate through `pc_suite.sh`) is moot — you are on the PC: run the three
  test files directly with the venue exports (`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`; the
  checker's real-leg tests need that corpus). The coordinator's own run on these bytes with the whole checker added read
  `568 passed, 9 xfailed in 143.10s (0:02:23)` — the 9 xfails are the corpus's known-stale `probe_sha256 mismatch`.
- The pinned sources for item 4 (can the agent leave a child holding its stderr?) are `/home/rocco/s0-01-pinned/acp` (buzz-acp)
  and `/home/rocco/s0-01-pinned/hermes-agent` (READ-ONLY). You never launch the real agent or Hermes here.
- Every FIFO/hang probe under `timeout` and standalone, never through pytest; the probe's real leg is NOT run here.
