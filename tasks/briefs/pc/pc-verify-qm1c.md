# PC lane — VERIFY-QM1-c (adversarial verification of the L1 matrix runner as LANDED)

PIN: c728be5

Role: adversarial-verifier. Route: the CLOUD verify route (`HERMES_MODEL=agentfactory-verify`,
`HERMES_REASONING=ultra`) — the SINGLE-MODEL RULE applies (findings only, no verdict). Venue:
`tasks/briefs/pc/VENUE-MAP.md` — read it first.

**The brief governs**: `tasks/briefs/qwen-matrix-support/VERIFY-QM1c-brief.md` — READ IT WHOLE and work
items V1-V9 in order. Your worktree IS `git archive <PIN>` plus the lane patch (the two briefs, this
file). Save your report at `tasks/briefs/qwen-matrix-support/VERIFY-QM1c-report.md`, draft after EACH
item, return it whole as your final message.

Venue notes:
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH. All effects are FAKES: fake QWEN_HOME /
  QWEN_LANES_DIR / proc / curl / systemctl. Never touch the real `qwen-builder` unit, the running
  servers, or any live lane's files (VERIFY-GOV1, the other cloud lanes).
- Hermes's `terminal` tool caps ONE call at 420 s: `run-all.sh` is ~2 min (fits); the focused suites
  are seconds. One heavy call at a time; run `run-all.sh` with the NORMAL environment, not a lane TMPDIR.
- The corpus at `~/qwen-builder/corpus/` is a coordinator input — read nothing there; F6 is about the
  CODE PATH that scrubs a corpus, tested with a synthetic secret-shaped export, not the real corpus.
- Attack through SCRATCH COPIES only — never git-restore/stash/checkout the shared tree. CODE INTEL
  FIRST: `graft ask` / `ripwire` on M and R before grep.
