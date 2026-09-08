# K1 — AMENDMENT 1 (coordinator decision 2026-09-08 20:2xZ): the symlink rule is bounded by the REPOSITORY root, not the vendored root

The K1 lane stopped with a blocker report (`tasks/briefs/kit-k1-support/K1-report.md`): item 2 says "symlinks recorded by target
and refused if they escape the root", and the pinned tree carries six committed symlinks under `.claude/skills/` that point
OUTSIDE `.claude/` into `.agents/skills/` (`design-artifact`, `html`, `html-diagram`, `html-plan`, `html-prototype`,
`html-wireframe`; `git ls-files -s` mode `120000`). The real generator refused them and stopped before writing the manifest. The
lane was right to stop rather than weaken the guard silently. Those links are the harness-ports sync by design (`docs/HARNESS-PORTS.md`:
`.agents/skills/` is the Codex/Hermes port of the skills; `.claude/skills/` links to it so one copy serves both harnesses).

## Item 2, the symlink sentence revised (the rest of item 2 and every other item stand unchanged)

A symlink under a vendored root is recorded in the tree digest by its TARGET STRING (the `readlink` value, never the target's
content — the content belongs to whichever root owns it, or to no root). It is ALLOWED when its resolved target lies inside the
REPOSITORY root (`git rev-parse --show-toplevel`, resolved once), whether or not that target is inside the same vendored root.
It is REFUSED, with the link and its target named, when the resolved target lies outside the repository root or the link
dangles. The header states the rule in one sentence. Tests: the six real `.claude/skills` links pass and appear in the digest by
target; a synthetic link to `/etc/hostname` and a synthetic dangling link are each refused by name; moving one of the six links'
targets outside the repo (a scratch copy) flips it to refused.

## Continuation

Your draft code is in your tree as the lane patch (`scripts/vendored_manifest.py`, `tests/test_vendored_manifest.py` — the
lane's `9 failed, 5 passed` were downstream of this one rule). Finish items 1-7 of the original brief under the revised rule,
write `sandbox-kit/VENDORED-MANIFEST.md` for real, run `--check` twice, and rebuild the report from the blocker report's
verified rows (keep them as its "Blocker (resolved by AMENDMENT 1)" section).
