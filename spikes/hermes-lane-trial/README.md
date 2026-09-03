# Spike: hermes-lane-trial — the PC BUILD lane round trip (owner ruling 2026-09-03)

**Proves:** a brief shipped from the sandbox (`scripts/pc_lane.sh <brief> hermes code-implementer`) runs
on the owner's Hermes CLI (profile `agentfactory`, route `codex/gpt-5.6-sol-ultra` through OmniRoute,
reasoning ultra) with the repo skills, hooks and MCP servers, executes repository checks on the PC
(quartet present, venv ok, `pytest tests/` 9 passed), writes bounded artifacts, and returns a DATA report
that the sandbox fetches. Six runs; each earlier run's failure was a real defect in OUR tooling, fixed
with a test (see `result.json` → `runs_before_this_one` and `docs/INCIDENT-LOG.md`). The model itself
verified its premises and stopped correctly every time it should have.

**Does NOT prove:** any Stage 0 proof logic (none ran); that the lane works in the PINNED WORKTREE — its
shell ran in the main clone (HEAD happened to equal the pin), so the patch fetch was empty. That is the
open defect before the first real increment rides a lane.

Result: `result.json`. Pinned commit: `a9847b47e8eff21024f5ac610730c6795bb61459`. Date: 2026-09-03.
