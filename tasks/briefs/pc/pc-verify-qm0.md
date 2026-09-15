# PC lane — VERIFY-QM0 (adversarial verification of the qwen-server matrix knobs + the pre-write lane guard as LANDED)

PIN: efde78d

Role: adversarial-verifier. Route: the CLOUD verify route (`HERMES_MODEL=agentfactory-verify`, `HERMES_REASONING=ultra`) — the local slot runs
VERIFY-GOV1 on the very unit you are grading: NEVER a real lifecycle command. The SINGLE-MODEL RULE applies (findings, no verdict).
Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first.

**The brief governs**: `tasks/briefs/qwen-server-verify-qm0-knobs-and-guard.md` — READ IT WHOLE and work items V1-V9 in order. Your worktree IS
`git archive <PIN>` plus the lane patch (the brief, this file). Save your report at `tasks/briefs/qwen-matrix-support/VERIFY-QM0-report.md`,
draft after EACH item, return it whole as your final message.

Venue notes:
- Every lifecycle probe (`install`/`start`/`stop`/`restart`/`uninstall`) runs ONLY with the fake seams T uses (a scratch `QWEN_LANES_DIR`, a scratch
  unit path, a fake `systemctl` on PATH, a scratch `XDG_RUNTIME_DIR`); read T:223-248 and T:304-347 for the exact seams before any probe.
  `guard` alone may read the real `~/agent-factory/.lanes/` (read-only; expect rc 7 while VERIFY-GOV1 is alive).
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; ShellCheck is absent on this host (say so, do not install).
- Hermes's `terminal` tool caps ONE call at 420 s: T runs in ~1 min; `run-all.sh` in ~2 min — one per call.
- Other lanes run on this host in their own trees (QM0-b and QM1-b on qwen-server work, VERIFY-N5l, VERIFY-GOV1): never touch their files, the
  `qwen-builder` unit, or any server.
