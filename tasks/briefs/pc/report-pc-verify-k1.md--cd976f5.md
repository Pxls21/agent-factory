NOT-READY — recommendation for `cd976f5`; no repair, commit, or push.

Report: `tasks/briefs/kit-k1-support/VERIFY-K1-report.md`
Draft mirror: `/home/rocco/agent-factory/.lanes/pc-verify-k1.md--cd976f5/report-draft.md`
Report SHA-256: `77056d12cb9537dc9d9ac294bfc1287871a9cf4be7abda8ebded5010026d6ca1`

BLOCKERS

F1 — undeclared vendored trees are invisible.
- `sandbox-kit/docs/` is listed as portable vendored content in `sandbox-kit/VENDORED-FROM.md:17` but is outside the eight roots in `scripts/vendored_manifest.py:36-93`.
- In a copy-fixture-shaped repo, adding `sandbox-kit/docs/`, then mutating its bytes, left real `--check` at rc 0.
- A newly created `sandbox-kit/newtool/file.txt` also left `--check` at rc 0.
- This defeats mechanical review of every vendored tree.

F2 — the whole `.claude/` provenance row is false for a mixed tree.
- Manifest row `sandbox-kit/VENDORED-MANIFEST.md:15` claims the complete `.claude/` tree is `pxls21/sandbox-kit:dot-claude/ @ aeb3082`.
- Provenance records adaptations; history after the kit import added 24 agents, 12 commands, 4 output styles, and 44 skills. A current `.claude` skill was last changed at `5802919`.
- The manifest needs actual vendored subtrees or an explicit first-party split. Its whole-tree source/pin claim cannot remain.

F3 — declared-root type is not bound.
- Replacing declared `sandbox-kit/aleph/` with a symlink to an identical, in-repo moved directory returned real `--check` rc 0.
- `walk_tree` follows a declared-root symlink via `root.is_dir()` / `os.walk`, then records only children (`scripts/vendored_manifest.py:129-156`).
- This violates the owner’s required path/type binding. Reject root symlinks or include root type and target in the manifest/digest; add this exact regression case.

F4 — committed K1 report evidence is stale and contradicts K1-e.
- `tasks/briefs/kit-k1-support/K1-report.md:20,38,76-78,92` claims `4d45f19`, obsolete file hashes/line counts, and says generating-commit drift fails at line 4.
- The K1 files do not exist at `4d45f19`; current PIN is `cd976f5`.
- `tests/test_vendored_manifest.py:180-207` asserts the opposite K1-e behavior: later HEAD passes, while a changed vendored byte fails on a row, not the header.
- Rewrite the K1 report against `cd976f5`.

FOLLOW-UPS

- Root-specific lock/SBOM agreement is currently vacuous: 24 lock entries, 22 SBOM entries, 22 shared entries, but none of the eight manifest sources occur in the lock.
- FIFO, socket, empty directory, and nested `.git` content are silently omitted. Unreadable and non-UTF8 names fail closed but emit raw exceptions.
- REUSE `LICENSES/` directories are reported `none found`; a LICENSE symlink is reported as `unknown`.
- `--write` is non-atomic. A permission-denied write preserved the old artifact; a truncated artifact failed `--check` closed.
- Generating-commit header is informational by design: a forged header with correct rows passes. Do not treat it as a pin.

VERIFIED GATES

- `python3 scripts/vendored_manifest.py --root . --check`
  - rc 0: `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 8 vendored roots`
- pytest, independent runs:
  - `22 passed in 12.13s`
  - `22 passed in 11.98s`
  - final: `22 passed in 12.63s`
- `/home/rocco/venv-agent-factory/bin/python -m pyflakes M T`
  - rc 0
- `git diff --check`
  - rc 0
- Mutation audit:
  - 11 scratch-only mutants compiled and collected 22 tests each.
  - 9 were killed.
  - `followlinks=True` and broad `Generated...` normalization were equivalent under the current control flow/format.
  - Existing mutations do not cover all-tree coverage, `.claude` segmentation, or declared-root type substitution; F1–F3 were independently reproduced through real `--check`.

REPORT LINT

- Three bounded hint-driven runs completed.
- Last executed run: `37 refs — OK 35, MISS 2, UNCHECKABLE 0, UNRESOLVED 0`; rc 1.
- Both final hints were applied afterward. I did not run a fourth lint pass because AF-AP-76 caps it at three rounds.

NOT-DONE

- No source repair applied.
- No commit or push.
- Unrelated untracked `downloaded_files/dashboard.lock` was present and untouched.
- `detect-changes` reported `No changes detected`; its clone index does not map the untracked report.

GATE RECOMMENDATION: NOT-READY — F1, F2, F3, and F4 meet the full blocking predicate.
