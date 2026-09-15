# PC lane — VERIFY-QM1-d (adversarial verification of the L1 matrix runner as LANDED)

PIN: 8c1dbe6

Role: adversarial-verifier. Route: the LOCAL Qwen verify route (`HERMES_MODEL=agentfactory-verify-local`,
effort xhigh) grading a lane built on the CLOUD route (a DIFFERENT model) — the single-model rule does
NOT apply: end with a FULL MERGE-READY / NOT-READY verdict. Venue: `tasks/briefs/pc/VENUE-MAP.md` —
read it first.

**The brief governs**: `tasks/briefs/qwen-matrix-support/VERIFY-QM1d-brief.md` — READ IT WHOLE (and the
QM1-d report `tasks/briefs/qwen-matrix-support/QM1d-report.md` it grades) and work items V1-V10 in
order. Your worktree IS `git archive <PIN>` plus the lane patch (the two briefs). The QM1-d code is
already in the PIN (M/R/T/X at their final QM1-d bytes). Save your report at
`tasks/briefs/qwen-matrix-support/VERIFY-QM1d-report.md`, draft after EACH item, return it whole as
your final message.

Venue notes:
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH. All effects are FAKES: fake QWEN_HOME /
  QWEN_LANES_DIR / proc / curl / systemctl. Never touch the real `qwen-builder` unit, the running
  servers, or any live lane's files.
- Hermes's `terminal` tool caps ONE call at 420 s: `run-all.sh` is ~2 min (fits); the focused suites
  are seconds. One heavy call at a time; run `run-all.sh` with the NORMAL environment, not a lane TMPDIR.
- The corpus at `~/qwen-builder/corpus/` is a coordinator input — read nothing there.
- The production runner M/launcher R must be BYTE-IDENTICAL to the PIN — copy into `../scratch` for
  every hostile edit; a change to a tracked file is a finding, not a fix.
- Attack through SCRATCH COPIES only — never git-restore/stash/checkout the shared tree. CODE INTEL
  FIRST: `graft ask` / `ripwire` on M and R before grep; attach the pack.
