# PC lane — VERIFY-A5n (adversarial verification of S0-01 checker round 16 as LANDED)

PIN: c728be5

Role: adversarial-verifier. Route: the CLOUD verify route (`HERMES_MODEL=agentfactory-verify`,
`HERMES_REASONING=ultra`) — the SINGLE-MODEL RULE applies (findings only, no verdict). Venue:
`tasks/briefs/pc/VENUE-MAP.md` — read it first.

**The brief governs**: `tasks/briefs/s0-01-a5m-support/VERIFY-A5n-brief.md` — READ IT WHOLE and work
items V1-V8 in order. Your worktree IS `git archive <PIN>` plus the lane patch (the two briefs, this
file). Save your report at `tasks/briefs/s0-01-a5m-support/VERIFY-A5n-report.md`, draft after EACH
item, return it whole as your final message.

Venue notes:
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; `S0_01_VENUE=pc
  S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden` exported before every `scripts/lane_gate.sh`
  run; an absolute, SHORT `--basetemp` under your lane's `../scratch` (AF_UNIX path length).
- Hermes's `terminal` tool caps ONE call at 420 s: the checker file alone runs ~15 min serial, so the
  gate MUST be `-n 8` xdist (~4 min, fits) — ONE `lane_gate.sh … -n 8` foreground call, never serial.
- The production checker `proofs/S0-01/check_acp_conformance.py` (C) must be BYTE-IDENTICAL to the PIN
  (`git diff --quiet c728be5 -- C` = rc 0) — a change to C is a finding, not a fix.
- Other lanes run on this host in their own trees (VERIFY-GOV1 on the local model, the other cloud
  lanes): never touch their files, the `qwen-builder` unit, or any server.
- Attack through SCRATCH COPIES only — never git-restore/stash/checkout the shared tree. CODE INTEL
  FIRST: `graft ask` / `ripwire` before grep.
