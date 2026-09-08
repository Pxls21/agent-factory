# PC lane — VERIFY-O2 (the adversarial grade of S0-03 round 2)

PIN: d12fc13

Role: adversarial-verifier. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-03-support/VERIFY-O2-brief.md` — READ IT WHOLE and follow it item by item (0-11).
Your worktree IS `git archive d12fc13`: O2's bytes on top of checkpoint 9c (the joint landing with P5b's launcher seam), the
lane's report, VERIFY-O1's report (the round's contract), P5b's report and the lane brief are all in the tree at the paths
the brief names. Save your report at `tasks/briefs/s0-03-support/VERIFY-O2-report.md` inside your tree, draft after EACH
item (the incremental rule), and return it whole as your final message.

Venue notes specific to this grade:
- NEVER make an OmniRoute or model request, never launch Hermes/buzz-acp/the agent, never read the OmniRoute key: the checker
  and tools are graded through loopback stand-ins you start and kill by pid, the committed bundles, and the S0-01 corpus's
  real `runtime-identity.json` files (`/home/rocco/s0-01-pinned/realleg/golden`, read-only).
- Run the four test files the lane brief names directly with the venue exports; state the load before long runs (the other
  verify lanes share this box).
