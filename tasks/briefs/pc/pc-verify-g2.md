# PC continuation — VERIFY-G2 (the adversarial grade of S0-08 gVisor containment round 2)

PIN: 887f021

Role: adversarial-verifier. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

## CONTINUATION (read second)
This lane CONTINUES the sandbox VERIFY-G2 lane, which the sandbox's model quota stopped on 2026-09-08 at ~05:18Z while it was
building its mutant driver ("Now the mutant campaign. Building the driver."). Nothing of its work survives; start the grade
from item 0.

**The brief governs**: `tasks/briefs/s0-08-support/VERIFY-G2-brief.md` — READ IT WHOLE and follow it item by item (0-15). Your
worktree IS `git archive 887f021` plus ONE shipped file, VERIFY-G1's report at `tasks/briefs/s0-08-support/VERIFY-G1-report.md`
(the brief cites it at a sandbox scratchpad path). Save your report at `tasks/briefs/s0-08-support/VERIFY-G2-report.md` inside
your tree, draft after EACH item (the incremental rule), and return it whole as your final message.

Venue notes specific to this grade:
- The brief's "ONE bridge action" (the pytest-only PC gate through `pc_suite.sh`) is moot — you are on the PC: run
  `tests/test_s0_08_containment.py` directly with the venue exports as uid 1000 (`kernel.dmesg_restrict=1` here; the amended
  tests derive their expectation from the running user — item 15). The coordinator's own run on these bytes read
  `197 passed in 6.41s` over the five-file set.
- gVisor cells: `/usr/local/bin/runsc --rootless do` on scratch dirs is allowed, as uid 1000 only. The brief's
  `setpriv --reuid=65534` non-root cell and any root cell need root and are NOT run here — state each as NOT run and grade
  the same claims from the lane's pasted evidence plus your own uid-1000 cell.
- NEVER `proofs/S0-08/tools/pc/run_containment.sh`, never podman, never a container start of any kind on this host.
- The pinned hermes-agent checkout for item 1 (the s6-overlay chain, `Dockerfile:68`) is at `/home/rocco/s0-01-pinned/hermes-agent`
  (READ-ONLY); fetching the s6-overlay release tarball is a read of a public artefact and allowed if this host can reach it —
  say whether it could.
