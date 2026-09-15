# PC lane — QM0 (qwen-server.sh: the six matrix knobs, the side-effect-free `guard` that tells local from cloud lanes, the guard before every persistent write — AF-AP-79)

PIN: PIN-PLACEHOLDER

Role: code-implementer. Route: the CLOUD build route (`HERMES_MODEL=agentfactory-build`, `HERMES_REASONING=ultra`). Venue:
`tasks/briefs/pc/VENUE-MAP.md` — read it first.

**The brief governs**: `tasks/briefs/qwen-server-qm0-cell-knobs-and-guard-before-write.md` — READ IT WHOLE and build items 1-7 in order.
Your worktree IS `git archive <PIN>` plus the lane patch (the brief, this file); the pack `tasks/briefs/qwen-matrix-support/QM1-pack.md`
and lane QM1's report (`tasks/briefs/qwen-matrix-support/QM1-report.md` — its Premise audit and Blocker sections are the measured facts you
build against) are IN the archive. Save your report at `tasks/briefs/qwen-matrix-support/QM0-report.md` inside your tree, draft after EACH
item, and return it whole as your final message.

Venue notes:
- The model server at `127.0.0.1:8080` is LIVE under a verify lane: read-only endpoints only; NEVER `install`/`restart`/`stop` the real
  `qwen-builder` unit, never touch the real `~/agent-factory/.lanes/`; every install/guard test runs against a fake `QWEN_LANES_DIR`, a fake
  `systemctl`/`systemd-analyze` on PATH and the harness's fake binary/HF tree (`harness-ports/tests/test_qwen_server.sh` shows how).
- Hermes's `terminal` tool caps ONE call at 420 s: `run-all.sh` (~2 min) in one foreground call.
- `/proc/<pid>/environ` of your own child processes is readable; use real `sleep` children for the guard tests and kill them by pid.
