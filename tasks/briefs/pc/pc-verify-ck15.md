# PC lane — VERIFY-CK15 (adversarial verification of S0-01 checker round 15 as LANDED: the exact-shape exclusivity lock, the inventories, the valid driver)

PIN: A5M-LANDING-PLACEHOLDER

Role: adversarial-verifier. Route: the LOCAL verify route (`agentfactory-verify-local`, xhigh — a verdict is allowed: the builder ran on the
cloud model) when the local slot is free; otherwise the CLOUD verify route (`HERMES_MODEL=agentfactory-verify`, `HERMES_REASONING=ultra`;
the single-model rule: findings, no verdict). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first.

**The brief governs**: `tasks/briefs/s0-01-verify-ck15-checker-round-15.md` — READ IT WHOLE and work items V1-V9 in order. Your worktree IS
`git archive <PIN>` plus the lane patch (the brief, this file). Save your report at `tasks/briefs/s0-01-a5m-support/VERIFY-CK15-report.md`,
draft after EACH item, return it whole as your final message.

Venue notes:
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden` (read-only —
  copy a leg into your scratch for any hostile edit); an absolute, SHORT `--basetemp` under your lane's scratch dir.
- Hermes's `terminal` tool caps ONE call at 420 s: the checker file is ~4.5 min SERIAL — run it ONLY with `-n 8` (~1 min) or as two halves
  (`-k` splits); the 13-file set with `-n 8` (~4 min), one such run per call.
- Other lanes run on this host in their own trees: never touch their files, the `qwen-builder` unit, or any server.
