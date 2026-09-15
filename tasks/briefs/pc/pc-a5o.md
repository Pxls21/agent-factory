# PC lane — A5o (S0-01 checker round 17: close VERIFY-A5n's two BLOCKERs)

PIN: 99ecb36

Role: code-implementer. Route: the CLOUD build route (`HERMES_MODEL=agentfactory-build`,
`HERMES_REASONING=ultra`). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first.

**The brief governs**: `tasks/briefs/s0-01-a5o-support/A5o-brief.md` — READ IT WHOLE (and the
VERIFY-A5n report it names, `tasks/briefs/s0-01-a5m-support/VERIFY-A5n-report.md`) and build items 1-2
in order. Your worktree IS `git archive <PIN>` plus the lane patch (the two briefs). Save your report
at `tasks/briefs/s0-01-a5o-support/A5o-report.md`, draft after EACH item, return it whole as your final
message.

Venue notes:
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; `S0_01_VENUE=pc
  S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden` exported before every gate run; an
  absolute, SHORT `--basetemp` and an absolute short `A5M_MUTANT_DIR` under your lane's `../scratch`
  (a RELATIVE mutant dir re-interprets `--basetemp` and turns TABLE_ROWS INVALID — VERIFY-A5n
  discrepancy).
- Hermes's `terminal` tool caps ONE call at 420 s. The checker file runs ~15 min SERIAL, so the pytest
  gate MUST be `scripts/pc_suite.sh launch -n 8 -- tests/test_s0_01_check_acp_conformance.py` then
  `wait <RUN_ID>` (xdist ~2-3 min, fits) — NEVER `lane_gate.sh -n` (its `-n` is RUNS, the bug
  VERIFY-A5n's Finding 3 caught). The mutant driver's own rows each run under `ROW_TIMEOUT_S`; run the
  driver detached if the full sweep would exceed the cap and read its log.
- The production checker `proofs/S0-01/check_acp_conformance.py` (C) MUST be BYTE-IDENTICAL to the PIN
  (`git diff --quiet c728be5 -- C` = rc 0) — a change to C is a finding, not a fix. Your fix is in the
  meta-test T and the A5o driver.
- Other lanes run on this host in their own trees (VERIFY-QM1-d on the local model): never touch their
  files, the `qwen-builder` unit, or any server.
- Attack through SCRATCH COPIES only — never git-restore/stash/checkout the shared tree. CODE INTEL
  FIRST: `graft ask` / `ripwire` on T before grep; attach the pack. The lint's `fix:` hints apply for
  at most three rounds, then paste and finish.
