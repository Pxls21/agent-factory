# K1 — AMENDMENT 2 (coordinator decision 2026-09-22 04:5xZ): the six dangling links were a REPOSITORY DEFECT, now removed; AMENDMENT 1's symlink rule stands; the "six real links pass" test is DELETED

K1-c (PIN 236bec7, report `tasks/briefs/kit-k1-support/K1-report.md`) stopped CONTRACT-INVALID, correctly: AMENDMENT 1 said
"the six real `.claude/skills` links pass" and "dangling links are refused" — jointly unsatisfiable because all six links
DANGLED at that PIN (their `.agents/skills/<name>` targets never existed in this repository; the lane proved it three ways).
The coordinator wrote that premise from memory (AF-AP-73 at the brief level; logged in `docs/INCIDENT-LOG.md` 2026-09-22).
The links were the `npx skills add plannotator/effective-html` installer's layout (`skills-lock.json`), copied by the
2026-09-02 migration without their content. They are REMOVED from the tree at this amendment's landing commit; the doc row in
`sandbox-kit/docs/THIRD-PARTY-AGENT-TOOLS.md` states the gap; restoring the six skills is an owner decision outside K1.

## What changes for K1-d (everything else in the original brief + AMENDMENT 1 stands)

1. The symlink rule is AMENDMENT 1's, unchanged: a symlink under a vendored root is recorded in the tree digest by its TARGET
   STRING; ALLOWED when its resolved target lies inside the REPOSITORY root (`git rev-parse --show-toplevel`, resolved once);
   REFUSED, with the link and its target named, when the resolved target lies outside the repository root or the link dangles.
2. The committed symlink inventory at the PIN is ONE entry — measured at authoring, `git ls-files -s | awk '$1=="120000"{print $4}'`
   with `readlink` and `test -e`, pasted verbatim:
   ```
   sandbox-kit/codebase-memory-mcp/Formula -> pkg/homebrew/Formula [resolves]
   ```
   Re-run the same command on your worktree as item 1 of the premise check; a second entry, or a dangling one, is a premise
   conflict — STOP and report it.
3. Tests, revised: (a) the ONE real link (`sandbox-kit/codebase-memory-mcp/Formula`) passes and appears in the digest by
   target string; (b) a synthetic link to `/etc/hostname` (outside the repository root) is refused by name; (c) a synthetic
   DANGLING link inside a vendored root is refused by name; (d) a synthetic link that crosses vendored roots but stays inside
   the repository (a scratch copy: `.claude/x -> ../.agents/skills/<an existing dir>`) is ALLOWED and digested by target
   string; (e) moving the real link's target outside the repo (a scratch copy) flips it to refused. The AMENDMENT 1 sentence
   "the six real `.claude/skills` links pass" is DELETED — there are no such links.
4. The recovered draft's pyflakes hit (`tests/test_vendored_manifest.py:3:1: 'dataclasses' imported but unused`, K1-c's
   finding) is fixed as part of item 5's green gate; pyflakes rc 0 on both files is a required paste.

## Continuation

Your draft code is in your tree as the lane patch (`scripts/vendored_manifest.py`, `tests/test_vendored_manifest.py` — the
2026-09-08 bytes; K1-c changed nothing in them). Its `9 failed, 5 passed` were downstream of the old vendored-root boundary
rule. Finish items 1-7 of the original brief under AMENDMENT 1's rule and this amendment's tests, write
`sandbox-kit/VENDORED-MANIFEST.md` for real, run `--check` twice, and rebuild the report from the two blocker reports'
verified rows (keep them as its "Blocker (resolved by AMENDMENT 1)" and "Blocker (resolved by AMENDMENT 2)" sections).
