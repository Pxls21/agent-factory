# VERIFY-K1-g — the independent targeted adversarial verify of K1-g (the vendored-tree manifest's four VERIFY-K1 blockers) — GATED-PENDING-VERIFY until this lands

PIN: fe2284d (the post-push SHA of the K1-g harvest commit; shas at the PIN: scripts/vendored_manifest.py 023525eef8db1fdc · tests/test_vendored_manifest.py fe6165d53d164edf · sandbox-kit/VENDORED-MANIFEST.md f4eaa0410fd12501 · sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv 750c5532f248aec9)
LANE: pc-verify-k1-g
ROLE: adversarial-verifier — the STRICT local route: `HERMES_MODEL=qwen-local/qwen3.8-27b-local` (D-039(a) + D-042(2); a raw id routes without a combo)
CONTRACT: VERIFY-K1's four blockers as frozen in `tasks/briefs/kit-k1-support/K1-g-report.md` (F1 a CLOSED classification of every top-level `sandbox-kit/` entry; F2 the `.claude/` row split mechanically against the pinned kit index with a committed class file; F3 the declared ROOT TYPE bound — root symlinks refused by name; F4 the K1 report rewritten against the PIN) + the harvest note in `todo/BUILD-TASKLIST.md` ("K1-g LANDED 2026-09-22 15:42Z"). The builder's report (GR) is a CLAIM, never an oracle. Issue #19 is OUT of scope.
DISCIPLINE: attack with NEW shapes, never the builder's own cases; every claim reproduced through the real tool (`python3 scripts/vendored_manifest.py --check | --write`) and the real suite; a finding blocks only under the full predicate (contract-mapped · reproduced through the production path · material · a concrete discriminator · in-boundary); emit a GATE RECOMMENDATION (MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID), never a verdict. NO repair.

## Items
1. F1 closure: enumerate the top-level `sandbox-kit/` entries at the PIN and prove every one is CLASSIFIED (declared root, docs, kit-portable file, or a named refusal). New shapes: a new top-level FILE (not a dir); a top-level symlink to a declared root; a directory that is declared but EMPTY; a name that differs only by case or a trailing dot/space; a nested `.git` inside a declared root (state whether it is in scope — #19 says nested .git is out; just measure what happens).
2. F2 the `.claude/` split: reproduce the three rows' counts from the pinned kit index `sandbox-kit/dot-claude.aeb3082.index.tsv` INDEPENDENTLY (your own walk + digest compare), then attack: a first-party file whose bytes equal a kit-verbatim file (a copy), a kit-adapted file re-verbatimized, a path present in the index but absent on disk, a path on disk absent from the index, a class file row edited by hand (does `--check` name the path?), the class file deleted, the class file with a duplicated path, CRLF vs LF in the class file.
3. F3 root type: a declared root replaced by a symlink to a real directory INSIDE sandbox-kit, OUTSIDE it, dangling; a declared root that is a regular file; a FIFO at a declared root path (do not hang: use a timeout); the root type digest record's exact text and whether a changed root type is named by path.
4. The generated manifest: run `--write` twice from the PIN and prove byte-identical output; `--check` after a whitespace-only edit, a row reorder, a header edit; the manifest's dependence on the working tree vs the index (does `--check` read git or the filesystem? prove it with an untracked file).
5. Mutants (each in a scratch copy, re-run in place with restore, the killing test NAMED): drop the unknown-entry refusal; drop the missing-declared-entry refusal; drop the root-symlink refusal in walk_tree; drop the class-file drift naming; compare the index by path only (ignore digests); accept a relative root. Paste each run.
6. Disk discipline (the coordinator's incident 15:5xZ): the suite copies the real vendored trees per test — measure the basetemp size of ONE run on the PC (`du -sm`), run with an explicit `--basetemp` under `/home/rocco/tmp-vk1g/bt` (NEVER /tmp), and REMOVE it after each run; state the size; if a single run exceeds 3 GB or the suite cannot run twice on the PC's free space, that is a finding (bounded fixtures needed).
7. The report's anchor style (aliases M:/T:/V:/P:/C:) — restate the load-bearing anchors as `path:line` so `scripts/report_lint.py --min-refs 10` grades ≥ 10 refs on YOUR report; note the GR's lint state at the PIN as measured.
8. AP screen: `python3 scripts/ap_screen.py --tests scripts/vendored_manifest.py tests/test_vendored_manifest.py` — the coordinator saw `AP-66 ×1` at tests:469 (a setattr monkeypatch): grade it (benign test scaffolding or a real class instance).

## Gates (paste verbatim)
`python -m pytest tests/test_vendored_manifest.py -q -p no:cacheprovider --basetemp=/home/rocco/tmp-vk1g/bt` twice with the basetemp removed between runs; `python3 scripts/vendored_manifest.py --check`; the mutants; `report_lint --min-refs 10` on your report.

## Report: `tasks/briefs/kit-k1-support/VERIFY-K1-g-report.md` — DATA; items 1-8 each with the pasted reproduction; the finding inventory with the blocking predicate applied per finding; the GATE RECOMMENDATION; DISCREPANCIES / NOT-done.

## PREMISE — MEASURED at authoring (2026-09-22 16:0xZ, sandbox clone @ fe2284d; re-verify at the PIN before editing)
```
$ git diff --stat fe2284d HEAD -- scripts/vendored_manifest.py tests/test_vendored_manifest.py sandbox-kit/VENDORED-MANIFEST.md sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv
(prints nothing — the four files are byte-identical between the PIN and the authoring tree)
$ grep -c 'def test_' tests/test_vendored_manifest.py
35
$ python3 scripts/vendored_manifest.py --check | tail -1
PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots
$ wc -l (the four files)
 957 scripts/vendored_manifest.py; 1007 tests/test_vendored_manifest.py; 30 sandbox-kit/VENDORED-MANIFEST.md; 3054 sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv;
$ python -m pytest tests/test_vendored_manifest.py -q -p no:cacheprovider --basetemp=/tmp/vm-bt | tail -1   (sandbox, 2026-09-22 15:5xZ, basetemp removed after)
45 passed in 56.91s
$ du -sm /tmp/vm-bt   (ONE run's basetemp, before removal)
2728 MB
```
