# PC lane — QM1-d (close VERIFY-QM1-c's two findings on the L1 matrix runner)

PIN: c728be5

Role: code-implementer. Route: the CLOUD build route (`HERMES_MODEL=agentfactory-build`,
`HERMES_REASONING=ultra`). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first.

**The brief governs**: `tasks/briefs/qwen-matrix-support/qm1d-two-findings.md` — READ IT WHOLE (and the
VERIFY-QM1-c report it names) and build items 1-2 in order. Your worktree IS `git archive <PIN>` plus
the lane patch (the two briefs, this file). Save your report at
`tasks/briefs/qwen-matrix-support/QM1d-report.md`, draft after EACH item, return it whole as your final
message.

Venue notes:
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH. All effects are FAKES: fake QWEN_HOME /
  QWEN_LANES_DIR / proc / curl / systemctl. Never touch the real `qwen-builder` unit, the running
  servers, or any live lane's files (N5n, VERIFY-A5n on this host).
- Hermes's `terminal` tool caps ONE call at 420 s: `run-all.sh` is ~2 min (fits); the focused suites
  are seconds. One heavy call at a time; run `run-all.sh` with the NORMAL environment, not a lane TMPDIR.
- The corpus at `~/qwen-builder/corpus/` is a coordinator input — read nothing there.
- Attack through SCRATCH COPIES only — never git-restore/stash/checkout the shared tree. CODE INTEL
  FIRST: `graft ask` / `ripwire` on M and R before editing; attach the pack.
