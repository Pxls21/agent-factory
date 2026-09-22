DONE: K1-g repaired VERIFY-K1 F1-F4 at PIN `46186d6`; deterministic self-validation is green. Independent sandbox adversarial verification has not run, so this remains a build-lane proposal.

NOT-DONE

- Independent adversarial verification has not run. This lane does not issue a gate verdict.
- Issue #19 remains out of scope: lock/SBOM agreement expansion, special files and nested `.git`, REUSE licenses, atomic `--write`, the informational header, pre-commit/run-all wiring, `.agents/`, `graft/`, and every other file.
- `SBOM.yaml` and `upstream.lock.yaml` were read-only inputs and were not changed.
- `tasks/briefs/kit-k1-support/K1-g-pack.md` was named by the brief but absent at this PIN; the post-edit replacement pack is `/home/rocco/agent-factory/.lanes/pc-k1-g.md--46186d6/scratch/K1-g-post-pack.md`.

BLOCKER (resolved by K1-g F1)

- The previous manifest did not bind every top-level `sandbox-kit/` entry. K1-g added the closed `SANDBOX_KIT_ENTRIES` table (`M:118`) and fail-closed checks for undeclared and missing top-level entries (`M:284`). `sandbox-kit/docs/` is now a vendored root (`M:102`, `V:29`), and kit portable top-level files are one digest row (`V:30`). Provenance rows were added at `P:18-19`.

BLOCKER (resolved by K1-g F2)

- The previous single `.claude/` row made the whole tree look kit-vendored. K1-g now classifies `.claude/` mechanically against the committed kit index (`M:323`, `M:346`), writes the class map to `C`, checks drift in `--check` (`M:924`), and renders three rows: kit-verbatim (`V:19`), kit-adapted (`V:20`), and first-party (`V:21`). Counts at this PIN are 2,958 / 14 / 81, kit-only 19 (`V:11`).

BLOCKER (resolved by K1-g F3)

- Declared root type is now bound. `walk_tree` refuses a declared root that is itself a symlink (`M:186`) and includes the root type `dir` as the first digest record (`M:194`). Top-level `sandbox-kit/` declared roots are also refused before unknown-entry reporting masks the type fault (`M:292`).

BLOCKER (resolved by K1-g F4)

- This report is rewritten against PIN `46186d614cf1b02b7023ba100e94ccce1ea62e3e` and committed kit index SHA-256 `5d266a2bbd7c84d1cf59ffde52eb0c596bb96ab930982dd74778541425ddf02c`. K1-e behavior remains: a later HEAD passes, and a changed vendored byte fails on its row, not the header.

PREMISE CHECK

- PIN: `46186d614cf1b02b7023ba100e94ccce1ea62e3e`.
- Pre-repair M/T matched VERIFY-K1's production digest: `scripts/vendored_manifest.py` SHA-256 `6528c8da30e38e551fe34c01be67b4ff707404f9586920e6f9d218a75aa28d0e`, 637 lines; `tests/test_vendored_manifest.py` SHA-256 `e29b4a4fec3ae7ec6fa83b6d7fe1858f60683f2648e2cef600a90630482a1371`, 568 lines.
- Pre-repair baseline: `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 8 vendored roots`; `pytest-summary: 22 passed in 16.52s`.
- Independent `.claude/` probe against `I` reproduced the brief exactly: kit-verbatim 2,958, kit-adapted 14, first-party 81, kit-only 19.

DONE TABLE

- F1 closed `sandbox-kit/` classification: done in `M:118`, `M:284`, `M:303`, `P:18-19`, `V:29-30`.
- F2 `.claude/` mechanical split: done in `M:323`, `M:346`, `M:410`, `M:416`, `M:429`, `M:694`, `M:924`, `C:1`; rendered in `V:11`, `V:19-21`.
- F3 root type binding: done in `M:186`, `M:194`, `M:292`; tests at `T:571`, `T:588`, `T:601`.
- F4 stale K1 report: this file rewritten against `46186d6`, current file identities below, and current gate output.

MANIFEST

- `python3 scripts/vendored_manifest.py --root . --write` output: `WROTE sandbox-kit/VENDORED-MANIFEST.md (9 roots)` and `WROTE sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv (3053 paths)`.
- `python3 scripts/vendored_manifest.py --root . --check` output: `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots`.
- `V` now has 12 manifest rows: three `.claude/` class rows, eight vendored roots including `sandbox-kit/docs/`, and one kit-portable pseudo-root. `len(VENDORED_ROOTS)` stays 9 because `.claude/` remains one declared root and renders into three classified rows.

MUTANTS

- `unsorted-tree-digest` → killed by `test_walk_is_sorted_before_digest` (`T:642`).
- `empty-exclusions` → killed by `test_exclusions_do_not_affect_tree_record` (`T:659`).
- `remove-sbom-agreement` → killed by `test_sbom_pin_disagreement_is_named` (`T:679`).
- `remove-symlink-refusal` → killed by `test_escaping_symlink_is_refused_by_name` (`T:506`).
- `remove-declared-root-symlink-refusal` → killed by `test_declared_root_symlink_target_outside_sandbox_kit_is_refused_by_name` (`T:588`).
- `remove-undeclared-entry-refusal` → killed by `test_undeclared_sandbox_kit_entry_is_named` (`T:293`).
- `remove-missing-entry-refusal` → killed by `test_vendored_root_table_entry_missing_is_named` (`T:339`).
- `blob-sha-without-git-header` → killed by `test_real_claude_split_counts_and_class_file` (`T:361`).
- `remove-kit-index-sha256-check` → killed by `test_kit_index_sha256_mismatch_is_named` (`T:412`).
- `remove-claude-class-comparison` → killed by `test_claude_class_drift_names_changed_path` (`T:382`).
- `drop-docs-root-from-manifest-table` → killed by `test_docs_byte_change_names_docs_row` (`T:305`).

VERIFIED OUTPUT

- `python3 scripts/vendored_manifest.py --root . --write` / `--check`: `WROTE sandbox-kit/VENDORED-MANIFEST.md (9 roots)`; `WROTE sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv (3053 paths)`; `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots`; `write_rc=0 check_rc=0`.
- `bash scripts/test_summary.sh tests/test_vendored_manifest.py -n 8 --basetemp .../scratch/bt1`: `pytest-summary: 45 passed in 27.02s`; `pytest-exit: 0`.
- Repeat `bt2`: `pytest-summary: 45 passed in 26.09s`; `pytest-exit: 0`.
- `bash scripts/pc_suite.sh set-id -- tests/test_vendored_manifest.py`: `1 files set=21e700b8344c`.
- `/home/rocco/venv-agent-factory/bin/python -m pyflakes scripts/vendored_manifest.py tests/test_vendored_manifest.py`: rc 0.
- `node /home/rocco/agent-factory/.gitnexus/run.cjs detect-changes --scope all --repo /home/rocco/agent-factory`: `Changes: 4 files, 1 symbols`; `Affected processes: 0`; `Risk level: low`.

AP SCREEN CLASSIFICATION

- `scripts/vendored_manifest.py:171`, `M:269`, and `T:624` SHA-256 hits are intentional manifest digests.
- `T:133`, `T:388`, `T:389` use an all-zero replacement SHA only inside tests to force manifest drift; not production behavior.
- `M:218`, `M:312`, `M:390` `path.is_file()` hits are walker type checks that refuse symlink roots and digest child symlinks by target string; they do not follow symlinks.
- `T:63`, `T:77` `source.exists()` hits only decide whether optional fixture inputs exist before copying.
- `M:793` `SOURCE_DATE_EPOCH` is an existing deterministic timestamp override, with invalid input tested at `T:238`.

FILE IDENTITY

- `scripts/vendored_manifest.py`: SHA-256 `023525eef8db1fdce4e8f06aa757447e3df5fe5631885c51985e3b608bd7af91`; 957 lines.
- `tests/test_vendored_manifest.py`: SHA-256 `fe6165d53d164edf53670d9f6d1ae0a4615c9d749f99a704acf0e458a27ec372`; 1,007 lines.
- `sandbox-kit/VENDORED-MANIFEST.md`: SHA-256 `1c4e0abe0cefd80b5d35308e2b71df15bf8320e953eca48f91326e8b2349d2bf`; 30 lines.
- `sandbox-kit/VENDORED-FROM.md`: SHA-256 `552f695e6e6cde893b30e444d0c0ff17f0e93a9135512ef17ba5ad2f4fc7e99c`; 55 lines.
- `sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv`: SHA-256 `750c5532f248aec91193d82f83da31e5de6de8020fb1bdf10512a5cd37fcbfb1`; 3,054 lines.
- `sandbox-kit/dot-claude.aeb3082.index.tsv`: SHA-256 `5d266a2bbd7c84d1cf59ffde52eb0c596bb96ab930982dd74778541425ddf02c`; 2,992 lines.

DISCREPANCIES

- The brief named `tasks/briefs/kit-k1-support/K1-g-pack.md`; it was absent at the PIN. Graft and a new lane-context pack were used instead.
- The AP-screen brief note named AF-AP-70 `path.is_file`; this tree's `ap_screen.py` reports those hits as AF-AP-40.
- K1-g changed the test count from 22 to 45 because F1-F3/F2 added red-first and mutation tests.
- `python3 scripts/report_lint.py K ...` after one hint round: `report_lint: 66 refs — OK 26, NEAR 3, MISS 25, UNCHECKABLE 12, UNRESOLVED 0 (worktree)`. Bounded lint misses are reported here instead of chased.

SELF-ATTACK

- Risk: `.claude/` class drift could be hidden by only updating the manifest rows. Control: `C` is regenerated by `--write` and compared by `--check`; class flips and new paths have direct tests (`T:382`, `T:397`).
- Risk: a symlinked declared root could be hidden by an extra undeclared `*-real` directory. Control: type is checked before unknown-entry reporting for declared roots (`M:292`), and an outside-root symlink test covers the same guard without an extra `sandbox-kit/` entry (`T:588`).
- Risk: `sandbox-kit/docs/` could still be unbound. Control: docs is in both `VENDORED_ROOTS` and `SANDBOX_KIT_ENTRIES`; docs byte drift fails on its row (`T:305`) and a mutant dropping that row is killed.

HANDOFF

- Build-lane recommendation only: MERGE-READY-WITH-FOLLOWUPS after independent verifier review. Followups are the out-of-scope issue #19 items and hook wiring.
