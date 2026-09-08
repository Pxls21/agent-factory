This is a blocker: the pinned brief requires symlink handling that refuses links escaping the vendored root, but the pinned tree already contains six committed `.claude/skills/*` symlinks that point outside `.claude/` into `.agents/skills/*`.

I am NOT going to stub it or silently weaken that guard.

Verified evidence:

- `tasks/briefs/kit-k1-vendored-manifest-source-commit-license-per-tree.md:32` requires symlinks be recorded by target and refused if they escape the root.
- Existing committed symlinks:
  - `.claude/skills/design-artifact -> ../../.agents/skills/design-artifact`
  - `.claude/skills/html -> ../../.agents/skills/html`
  - `.claude/skills/html-diagram -> ../../.agents/skills/html-diagram`
  - `.claude/skills/html-plan -> ../../.agents/skills/html-plan`
  - `.claude/skills/html-prototype -> ../../.agents/skills/html-prototype`
  - `.claude/skills/html-wireframe -> ../../.agents/skills/html-wireframe`
- `git ls-files -s` shows those six as tracked symlink entries (`120000`).
- The real generator stops before writing the manifest:
  - `FAIL: escaping symlink refused in .../.claude: skills/design-artifact -> ../../.agents/skills/design-artifact`
- Focused tests prove the guard itself works on synthetic escape links, but the real tree cannot satisfy the current brief as written.

Work left in the lane tree:

- Added proposal files:
  - `scripts/vendored_manifest.py`
  - `tests/test_vendored_manifest.py`
- Wrote draft report:
  - `/home/rocco/agent-factory/.lanes/pc-k1.md--be5cf35/report-draft.md`
- Did not create `sandbox-kit/VENDORED-MANIFEST.md` because the real tree fails the required symlink policy.
- Did not edit vendored files or any out-of-scope files.

Real test output:

- `python3 -m py_compile scripts/vendored_manifest.py tests/test_vendored_manifest.py`
  - `py_compile_rc=0`
- `python3 scripts/vendored_manifest.py --root . --write`
  - `FAIL: escaping symlink refused in .../.claude: skills/design-artifact -> ../../.agents/skills/design-artifact`
  - `write_rc=1`
- `/home/rocco/venv-agent-factory/bin/python -m pytest -q tests/test_vendored_manifest.py --basetemp ../scratch/pytest-k1-blocker`
  - `9 failed, 5 passed`
  - Most failures are downstream of the same real-tree blocker.
- Focused non-real-tree checks:
  - `3 passed` for license detection, exclusion handling, and direct escaping-symlink refusal
  - Mutant wrapper assertions still need cleanup once the brief/tree contradiction is resolved.

Decision needed:

1. Treat `.claude/` symlinks into `.agents/skills/` as allowed intra-repo links and update the brief/guard accordingly.
2. Exclude those six symlinks from `.claude/` manifesting by design.
3. Replace the symlinks with real vendored copies in a separate non-K1 change.

🌱 graft saved ~101,106 tokens this turn.
