# PC lane — VERIFY-N5l (adversarial verification of S0-01 probe round 15 as LANDED: the ELOOP red, the v3 ports, the census, the scoped close_fds pin, the driver)

PIN: efde78d

Role: adversarial-verifier. Route: the CLOUD verify route (`HERMES_MODEL=agentfactory-verify`, `HERMES_REASONING=ultra`) — the local slot runs
VERIFY-GOV1; the SINGLE-MODEL RULE applies (findings, no verdict). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first.

**The brief governs**: `tasks/briefs/s0-01-verify-n5l-probe-round-15.md` — READ IT WHOLE and work items V1-V9 in order. Your worktree IS
`git archive <PIN>` plus the lane patch (the brief, this file). Save your report at `tasks/briefs/s0-01-n5l-support/VERIFY-N5l-report.md`,
draft after EACH item, return it whole as your final message.

Venue notes:
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden` (read-only —
  copy a leg into your scratch for any hostile edit); an absolute `--basetemp` under your lane's scratch dir (short: AF_UNIX paths).
- Hermes's `terminal` tool caps ONE call at 420 s: the probe file is ~55 s serial; the 13-file set runs ONLY with `-n 8` (~4 min) —
  one such run per call, never two.
- Other lanes run on this host in their own trees (A5m's tree, VERIFY-GOV1 on the local model, QM0-b, QM1-b): never touch their files, the
  `qwen-builder` unit, or any server. Read `~/qwen-builder/…` nothing; the corpus is the only shared input.
