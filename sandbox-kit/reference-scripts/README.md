# reference-scripts — worked examples, NOT wired into this repo

These are the trading-system repo's live workflow scripts, kept as worked examples of the
patterns CLAUDE.md's protocols talk about (lane gates, lint deltas, mutation runs, clean pushes,
per-symbol history). They reference that repo's paths (`/root/venv-trading`, `vectorbtpro-new`,
`trading/…`) and will NOT run here as-is — adapt one into `scripts/` when this project grows the
corresponding need.

| Script | Pattern it demonstrates |
|---|---|
| `setup-trading-system.sh` | The full SessionStart toolchain rebuild this repo's `scripts/setup.sh` was derived from. |
| `lane_gate.sh` | Tiered test-lane gate (fast lane vs full lane) with an isolated worktree. |
| `lint_delta.py` | "New lint hits vs HEAD" delta — lint the change, not the legacy. |
| `mutation_run.py` / `mutant_anchor_precommit.py` | Mutation-testing run + pre-commit anchor check. |
| `push_clean.sh` | Verified-clean push ritual. |
| `why.sh` | Per-symbol `git log -L` chronology ("why is this function the way it is"). |
