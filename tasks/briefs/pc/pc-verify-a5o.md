# PC lane — VERIFY-A5o (adversarial verification of S0-01 checker round 17 as LANDED)

PIN: 45e7bf6

Role: adversarial-verifier. Route: the CLOUD verify route (`HERMES_MODEL=agentfactory-verify`,
`HERMES_REASONING=ultra`) — the SINGLE-MODEL RULE applies (findings only, no verdict). Venue:
`tasks/briefs/pc/VENUE-MAP.md` — read it first.

**The brief governs**: `tasks/briefs/s0-01-a5o-support/VERIFY-A5o-brief.md` — READ IT WHOLE (and the
A5o report `tasks/briefs/s0-01-a5o-support/A5o-report.md` it grades) and work items V1-V8 in order.
Your worktree IS `git archive <PIN>` plus the lane patch (the two briefs). The A5o code (T + the driver
D) is already in the PIN. Save your report at `tasks/briefs/s0-01-a5o-support/VERIFY-A5o-report.md`,
draft after EACH item, return it whole as your final message.

Venue notes:
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; `S0_01_VENUE=pc
  S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden` exported before every gate run; an
  absolute, SHORT `--basetemp` and (for the driver) an absolute short `A5M_MUTANT_DIR` under your
  lane's `../scratch` (a RELATIVE mutant dir turns TABLE_ROWS INVALID — a known discrepancy).
- Hermes's `terminal` tool caps ONE call at 420 s. The checker file runs ~15 min SERIAL, so the outer
  gate MUST be `scripts/pc_suite.sh launch -n 8 -- tests/test_s0_01_check_acp_conformance.py` then
  `wait <RUN_ID>` (xdist ~2-3 min) — the owner carve-out permits a VERIFY lane to run pytest-only
  gates through pc_suite.sh launch|wait; NO other bridge use, no lane dispatch, no server touch. The
  driver's rows each run under `ROW_TIMEOUT_S`; run a long sweep detached and read its log.
- The production checker C (`proofs/S0-01/check_acp_conformance.py`) must be BYTE-IDENTICAL to the PIN
  (`git diff --quiet c728be5 -- C` = rc 0) — a change to C is a finding, not a fix.
- Other lanes run on this host in their own trees: never touch their files, the `qwen-builder` unit,
  or any server.
- Attack through SCRATCH COPIES only — never git-restore/stash/checkout the shared tree. CODE INTEL
  FIRST: `graft ask` / `ripwire` on T before grep; attach the pack.
