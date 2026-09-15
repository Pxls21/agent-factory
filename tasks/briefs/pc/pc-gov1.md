# PC lane — GOV1 (Stage 3 governance core from S0-07: the first `src/agent_factory` package — lint exit, canonical hash, the immutable projection, the BoundDecision join, the audit envelope seed)

PIN: 9376760

Role: code-implementer. Route: the CLOUD build route (`HERMES_MODEL=agentfactory-build`, `HERMES_REASONING=ultra`) — the local slot's
effort switch waits for QM0's guard; the route changes nothing in the brief. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first.

**The brief governs**: `tasks/briefs/stage3-gov1-governance-core-from-s0-07.md` — READ IT WHOLE and build items 1-9 in order. Your worktree IS
`git archive <PIN>` plus the lane patch (the brief, this file, the pack `tasks/briefs/stage3-governance-support/GOV1-pack.md`). Save your
report at `tasks/briefs/stage3-governance-support/GOV1-report.md`, draft after EACH item, return it whole as your final message. Your driver
goes beside it.

Venue notes:
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; an absolute `--basetemp` under your lane's scratch dir; NEVER `pip install` into that
  shared venv — the editable-install proof runs in a throwaway venv you create under scratch (`python -m venv`).
- The pinned fubuki-os: look under `/home/rocco/s0-01-pinned/` and `/home/rocco/nerdherderdani/` first; else clone into your scratch at
  the lock's commit (the one permitted network action) and paste `git rev-parse HEAD`.
- Three other lanes run on this host in their own trees (A5m, QM0, N5l): never touch their files or the `qwen-builder` unit.
- Hermes's `terminal` tool caps ONE call at 420 s; nothing here needs more.
