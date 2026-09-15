# PC lane — QM0-b (qwen-server.sh restart-when-idle: the deferred restart that fires only when the local server's work is done; the dispatcher queues local lanes behind it)

PIN: QM0-LANDING-PLACEHOLDER

Role: code-implementer. Route: the CLOUD build route (`HERMES_MODEL=agentfactory-build`, `HERMES_REASONING=ultra`) unless the local slot is
free and at `medium` at dispatch. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first.

**The brief governs**: `tasks/briefs/qwen-server-qm0b-restart-when-idle.md` — READ IT WHOLE and build items 1-7 in order. Your worktree IS
`git archive <PIN>` (QM0's landing: the knobs + `guard` are IN the archive) plus the lane patch (the brief, this file). Save your report at
`tasks/briefs/qwen-matrix-support/QM0b-report.md`, draft after EACH item, return it whole as your final message.

Venue notes:
- The model server at `127.0.0.1:8080` is LIVE: `/metrics`, `/props`, `/health` are read-only and allowed (keyed; never print the key);
  NEVER `restart-when-idle`/`install`/`restart` the real unit, never touch the real `~/agent-factory/.lanes/` or `~/qwen-builder/pending/`
  — every test runs under a fake `QWEN_HOME`, fake `QWEN_LANES_DIR`, fake `systemctl` on PATH (QM0's harness shows how).
- Hermes's `terminal` tool caps ONE call at 420 s: `run-all.sh` (~2 min) in one foreground call; `--poll 1 --max-wait 3` in tests.
