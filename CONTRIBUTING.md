# Contributing

The project is in Stage 0. Small, evidence-producing pull requests are preferred over broad implementation branches.

## Before opening a pull request

1. Read `AGENTS.md` and the current decision log.
2. Link the work to one Stage 0 or later milestone item.
3. Keep secrets out of commits and logs.
4. Run `./scripts/verify-planning-repo.sh`.
5. State what was tested, what was not tested, and which source pin the work targets.

## Pull-request expectations

- One architectural seam or risk per PR where practical.
- A failing test or reproducible fixture before a behavioral fix.
- Negative tests for fail-closed boundaries.
- An ADR update for changes to engine selection, model egress, memory scope, governance, containment, or trust.
- No vendored upstream source until its update strategy and license obligations are documented.
