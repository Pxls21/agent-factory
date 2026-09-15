# PC lane — QM1-c (the L1 matrix runner: the six VERIFY-QM1 findings fixed)

PIN: __PIN__

Role: code-implementer. Route: the CLOUD build route (`HERMES_MODEL=agentfactory-build`, `HERMES_REASONING=ultra`) — the local slot runs
VERIFY-GOV1. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first.

**The brief governs**: `tasks/briefs/qwen-matrix-qm1c-runner-six-fixes.md` — READ IT WHOLE (and the VERIFY-QM1 report it names) and build
items 1-6 in order. Your worktree IS `git archive <PIN>` plus the lane patch (the brief, this file). Save your report at
`tasks/briefs/qwen-matrix-support/QM1c-report.md`, draft after EACH item, return it whole as your final message.

Venue notes:
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH. All effects are FAKES: fake QWEN_HOME / QWEN_LANES_DIR / proc / curl / systemctl.
  Never touch the real `qwen-builder` unit, the running servers, or any live lane's files (A5n, VERIFY-GOV1).
- Hermes's `terminal` tool caps ONE call at 420 s: `run-all.sh` is ~2 min (fits); the focused suites are seconds. One heavy call at a time.
- CODE INTEL FIRST: `graft ask` / `ripwire` on M and R before editing; attach the pack. The lint's `fix:` hints apply for at most three
  rounds, then paste and finish.
- The corpus at `~/qwen-builder/corpus/` is a coordinator input — read nothing there; F6 is about the CODE PATH that persists a corpus, tested
  with a synthetic secret-shaped export, not the real corpus.
