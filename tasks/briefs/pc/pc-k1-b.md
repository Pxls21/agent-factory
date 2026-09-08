# PC lane — K1-b (the vendored manifest, CONTINUED after the symlink blocker: intra-repository links allowed by target, escaping or dangling links refused)

PIN: be5cf35

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

## CONTINUATION (read second)
This lane CONTINUES lane K1, which stopped correctly with a blocker: the brief's symlink rule ("refused if they escape the root")
refused the six committed `.claude/skills/*` links into `.agents/skills/*` (the harness-ports sync by design). The coordinator
resolved it as **AMENDMENT 1** — `tasks/briefs/kit-k1-support/K1-AMENDMENT-1.md` — READ IT FIRST: a link is recorded by its
target string and allowed when its resolved target lies inside the REPOSITORY root; a link escaping the repository or dangling is
refused by name. Your predecessor's draft is ALREADY APPLIED on your worktree as the lane patch (`scripts/vendored_manifest.py`
559 lines, `tests/test_vendored_manifest.py` 320 lines — its `9 failed, 5 passed` were downstream of the one rule); treat it as a
draft: verify its premises, finish items 1-7 of the original brief under the revised rule, write `sandbox-kit/VENDORED-MANIFEST.md`
for real, run `--check` twice, and rebuild the report on the blocker report (`tasks/briefs/kit-k1-support/K1-report.md`, keep it as
the "Blocker (resolved by AMENDMENT 1)" section).

**The original brief governs**: `tasks/briefs/kit-k1-vendored-manifest-source-commit-license-per-tree.md` — READ IT WHOLE. Save
your report at `tasks/briefs/kit-k1-support/K1-report.md` inside your tree, draft after EACH item (the incremental rule), and
return it whole as your final message.

Venue notes specific to this build:
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH (pyflakes from that venv); an absolute `--basetemp` under your lane's scratch
  dir; the tests run in seconds — paste them twice (bitwise-identical manifests on two `--write` runs is item 7's gate).
- The vendored roots are read-only inputs; `SBOM.yaml` and `upstream.lock.yaml` are never edited (a disagreement is reported, not
  fixed). No live service, no network.
- Seven Stage 0 lanes share this host (P5c-b, D5n, O3, N5j, B5k, M3, G3): never touch `proofs/`, `tests/test_s0_*`, or their trees.
