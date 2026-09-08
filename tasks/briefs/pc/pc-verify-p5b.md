# PC lane — VERIFY-P5b (the adversarial grade of S0-01 PC capture tools round 2 on the joint checkpoint)

PIN: 77f46a2

Role: adversarial-verifier. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-01-p5b-support/VERIFY-P5b-brief.md` — READ IT WHOLE and follow it item by item (0-10).
Your worktree IS `git archive 77f46a2`: the joint checkpoint's bytes, the lane's report, VERIFY-P5a's report (the round's
contract), A5k's report and the lane brief are all in the tree at the paths the brief names. Save your report at
`tasks/briefs/s0-01-p5b-support/VERIFY-P5b-report.md` inside your tree, draft after EACH item (the incremental rule), and return
it whole as your final message.

Venue notes specific to this grade:
- NEVER launch buzz-acp, hermes-acp, Hermes or the tee here: the tools are graded through their shims (the tests' ps table),
  their argv/unit surface (`pc_launch.py` as a subprocess with `--help` and refusing argv only), synthetic run dirs for
  `collect_leg.sh`, and the real corpus's COLLECTED files (`/home/rocco/s0-01-pinned/realleg/golden`, read-only).
- Run the test files the brief names directly with the venue exports; every FIFO probe standalone under `timeout`.
- The other verify lanes (CK13, D5m) run on this box at the same time — state the load before long runs.
