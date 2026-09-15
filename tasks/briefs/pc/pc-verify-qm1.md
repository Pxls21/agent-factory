# PC lane — VERIFY-QM1 (adversarial verification of the L1 concurrency-matrix runner as LANDED: the guard-first cell runner, the fail-closed corpus builder, the keyed reads, the overlap and table decisions)

PIN: VQM1-PIN-PLACEHOLDER

Role: adversarial-verifier. Route: the CLOUD verify route (`HERMES_MODEL=agentfactory-verify`, `HERMES_REASONING=ultra`) — the local slot runs
VERIFY-GOV1 on the very unit the runner would restart: NEVER a real cell, load or lifecycle command. The SINGLE-MODEL RULE applies (findings,
no verdict). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first.

**The brief governs**: `tasks/briefs/qwen-matrix-verify-qm1-runner.md` — READ IT WHOLE and work items V1-V9 in order. Your worktree IS
`git archive <PIN>` plus the lane patch (the brief, this file). Save your report at `tasks/briefs/qwen-matrix-support/VERIFY-QM1-report.md`,
draft after EACH item, return it whole as your final message.

Venue notes:
- R's lifecycle paths run ONLY with X's fake seams (a fake `qwen-server.sh`, `systemctl`, `nvidia-smi` on a scratch PATH; read X:1-60 first).
  Live reads allowed, keyed and read-only: `/props`, `/metrics`, one `/tokenize` of a short string (the key file is
  `~/.config/qwen-builder/api-key` — read it into a variable, never echo it). The session exports under `~/qwen-builder/ab/` are read-only.
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; an absolute, short `--basetemp` under your lane's scratch dir.
- Hermes's `terminal` tool caps ONE call at 420 s: T runs in ~1 s, X in ~10 s, `run-all.sh` in ~2 min — one per call.
- Other lanes run on this host in their own trees (QM0-b, N5m, A5n, VERIFY-GOV1): never touch their files, the `qwen-builder` unit, or any server.
