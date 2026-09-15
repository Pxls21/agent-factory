# PC lane — A5n (S0-01 checker round 16: the narrowed claim, labelled asserts, the literal denominator with a self-test, the per-row timeout)

PIN: c41aab6

Role: code-implementer. Route: the CLOUD build route (`HERMES_MODEL=agentfactory-build`, `HERMES_REASONING=ultra`) — the local slot runs
VERIFY-GOV1. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first.

**The brief governs**: `tasks/briefs/s0-01-a5n-checker-round-16-narrowed-claim-labelled-asserts-literal-denominator.md` — READ IT WHOLE and
build items 1-5 in order. Your worktree IS `git archive <PIN>` plus the lane patch (the brief, this file). Save your report at
`tasks/briefs/s0-01-a5m-support/A5n-report.md`, draft after EACH item, return it whole as your final message.

Venue notes:
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden` (read-only —
  copy a leg into your scratch for any hostile edit); an absolute, SHORT `--basetemp` under your lane's scratch dir.
- Hermes's `terminal` tool caps ONE call at 420 s: the checker file ONLY with `-n 8` (~2.5 min); the 13-file set with `-n 8` (~4 min), one run
  per call; the 19-row driver ~6 min — run it in TWO halves if a single run would exceed the cap (`D` accepts a row range, or split by
  `--rows`), never one call over the cap.
- Other lanes run on this host in their own trees (QM0-b, N5m, VERIFY-QM1, VERIFY-GOV1): never touch their files, the `qwen-builder` unit,
  or any server.
