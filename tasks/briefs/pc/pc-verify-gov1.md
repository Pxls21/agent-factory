# PC lane — VERIFY-GOV1 (adversarial verification of the first production increment: the Stage 3 governance core as LANDED)

PIN: 78f400d

Role: adversarial-verifier. Route: the LOCAL verify route (`agentfactory-verify-local`, xhigh — the server already runs at xhigh, no restart).
Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first.

**The brief governs**: `tasks/briefs/stage3-verify-gov1-governance-core.md` — READ IT WHOLE and work items V1-V12 in order. Your worktree IS
`git archive <PIN>` plus the lane patch (the brief, this file). Save your report at
`tasks/briefs/stage3-governance-support/VERIFY-GOV1-report.md`, draft after EACH item, return it whole as your final message.

Venue notes:
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; an absolute `--basetemp` under your lane's scratch dir; never `pip install` into the shared venv.
- Export `FUBUKI_OS_ROOT=/home/rocco/fubuki-pin/fubuki-os FUBUKI_OTHER_ROOT=/home/rocco/fubuki-pin/fubuki-os-other` for every pytest call
  (`bash scripts/fubuki_pin_sync.sh /home/rocco/fubuki-pin` re-verifies both, idempotent). A DIRTY copy for V10 goes under your scratch, never the
  provisioned checkout.
- Hermes's `terminal` tool caps ONE call at 420 s; the six suites run in ~2 s, the driver in ~40 s — nothing here needs more.
- Another lane (A5m) runs on this host in its own tree; never touch its files, the `qwen-builder` unit, or any server.
