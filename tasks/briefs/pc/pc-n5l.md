# PC lane — N5l (S0-01 probe round 15: the final-symlink red, the v3 ports, the real-emitter census, close_fds explicit under a scoped pin)

PIN: 97bb0c0

Role: code-implementer. Route: the CLOUD build route (`HERMES_MODEL=agentfactory-build`, `HERMES_REASONING=ultra`) — the local server
still carries the verify lane's `xhigh` default and the dispatcher cannot switch it to `medium` (D-028) until QM0's route-aware guard lands
(the installer refuses under the two live cloud lanes); the route changes nothing in the brief. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first.

**The brief governs**: `tasks/briefs/s0-01-n5l-probe-the-symlink-red-and-the-v3-ports.md` — READ IT WHOLE and build items 1-8 in order.
Your worktree IS `git archive <PIN>` plus the lane patch (the brief, this file, the pack `tasks/briefs/s0-01-n5l-support/N5l-pack.md`, the
VERIFY-N5k report `tasks/briefs/s0-01-n5j-support/VERIFY-N5k-report.md`); arm B v3's diff `tasks/briefs/s0-01-n5j-support/N5k-xhigh-v3.diff`
and arm A's report `N5k-report.md` are IN the archive. Save your report at `tasks/briefs/s0-01-n5l-support/N5l-report.md` inside your tree,
draft after EACH item, and return it whole as your final message. Your driver goes beside it.

Venue notes:
- Venue exports `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`; the corpus is READ-ONLY (five legs, no `run-2` —
  the coordinator's). `/home/rocco/venv-agent-factory/bin` FIRST on PATH; an absolute `--basetemp` under your lane's scratch dir.
- Hermes's `terminal` tool caps ONE call at 420 s: the probe file serial is ~52 s (fine); the four-file and 13-file sets ONLY with `-n 8`.
- `scripts/pc_suite.sh set-id -- <files>` works without the bridge; paste its line beside every count.
- Two cloud-route lanes (A5m, QM0) run on this host in their own trees: never touch their files.
