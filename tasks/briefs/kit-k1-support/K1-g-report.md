K1-g BUILD-LANE REPORT

Header

- Route: agentfactory-build-local. HYBRID caveat: the PC route may fall through to a cloud step when the local step refuses; this lane does not claim which model produced the code.
- Status: build proposal only. Independent sandbox adversarial verification has not run. This lane does not issue a gate verdict.
- Scope: F1-F4 only, at PIN `46186d614cf1b02b7023ba100e94ccce1ea62e3e`.

PREMISE — RE-MEASURED

- HEAD: `46186d614cf1b02b7023ba100e94ccce1ea62e3e`.
- Pre-repair `scripts/vendored_manifest.py`: SHA-256 `6528c8da30e38e551fe34c01be67b4ff707404f9586920e6f9d218a75aa28d0e`; 637 lines.
- Pre-repair `tests/test_vendored_manifest.py`: SHA-256 `e29b4a4fec3ae7ec6fa83b6d7fe1858f60683f2648e2cef600a90630482a1371`; 568 lines.
- Pre-repair `sandbox-kit/VENDORED-MANIFEST.md`: SHA-256 `4ef0553cd6dcfb56c96a333631595b49b85516b074c5865de72c9a7fc1636bd2`; 22 lines.
- Pre-repair `sandbox-kit/VENDORED-FROM.md`: SHA-256 `2db7cf5fbee7166eddb261585dca62599eac39079aebc9c990c0cc8cbb242c8a`; 53 lines.
- Input index `sandbox-kit/dot-claude.aeb3082.index.tsv`: SHA-256 `5d266a2bbd7c84d1cf59ffde52eb0c596bb96ab930982dd74778541425ddf02c`; 2,992 lines.
- Pre-repair `tasks/briefs/kit-k1-support/K1-report.md`: SHA-256 `5b6ea7d4aaf3d7baf56fddde19a8a122155f52e0f8ed289cf26944e025072f05`; 100 lines.
- Baseline `--check`: `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 8 vendored roots`; `check rc=0`.
- Baseline suite: `pytest-summary: 22 passed in 16.52s`; `pytest-exit: 0`.
- Set id: `1 files set=21e700b8344c`.
- Anchor lines remeasured: `VENDORED_ROOTS` at `M:44`; `walk_tree` at `M:186`; `parse_provenance` at `M:489`; `validate_declared_roots` at `M:571`; `build_manifest_data` at `M:694`; `render` at `M:805`; `main` at `M:889`.

ITEM 2 — F1 closed classification of every top-level `sandbox-kit/` entry

- Changed `M`: `SANDBOX_KIT_ENTRIES` at `M:118`, `validate_sandbox_kit_entries` at `M:284`, and `kit_portable_records` at `M:303`.
- Changed `P`: added `sandbox-kit/docs/` provenance at `P:18` and `sandbox-kit/ (kit-portable files)` provenance at `P:19`.
- Regenerated `V`: `sandbox-kit/docs/` row at `V:29`; `sandbox-kit/ (kit-portable files)` row at `V:30`.
- Negative/green outputs:
  - Undeclared new entry: `F1 undeclared sandbox-kit entry: rc=1; stderr='FAIL: undeclared entry under sandbox-kit/: newtool'`.
  - Docs byte drift: `F1 docs byte drift: rc=1; stderr="FAIL: vendored manifest drift: line 29: ... | `sandbox-kit/docs/` ..."`.
  - Missing declared entry: `F1 missing declared entry: rc=1; stderr='FAIL: declared sandbox-kit entry missing: README.md'`.
  - Kit-portable byte drift: `F1 kit-portable byte drift: rc=1; stderr="FAIL: vendored manifest drift: line 30: ... | `sandbox-kit/ (kit-portable files)` ..."`.
  - Green: `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots`.

ITEM 3 — F2 `.claude/` row split mechanically against `I`

- Changed `M`: `KIT_INDEX_SHA256` at `M:27`, `load_kit_index` at `M:323`, `claude_records` at `M:346`, `render_classes` at `M:410`, `parse_classes` at `M:416`, `class_difference` at `M:429`, and `build_manifest_data` at `M:694`.
- Changed `V`: kit index header at `V:11`; first-party header at `V:12`; `.claude/ (kit-verbatim)` at `V:19`; `.claude/ (kit-adapted)` at `V:20`; `.claude/ (first-party)` at `V:21`.
- Added `C`: `path	class` header at `C:1`; adapted path examples at `C:2`, `C:41`, `C:42`, `C:43`, `C:44`, `C:50`, `C:82`, `C:302`, `C:453`, `C:587`, `C:596`, `C:730`, `C:1779`, `C:2573`.
- Tests: `test_real_claude_split_counts_and_class_file` at `T:361`; `test_claude_class_drift_names_changed_path` at `T:382`; `test_new_first_party_claude_file_names_manifest_and_class_drift` at `T:397`; `test_kit_index_sha256_mismatch_is_named` at `T:412`; `test_malformed_kit_index_row_names_line` at `T:426`; `test_missing_kit_index_is_named` at `T:440`; `test_real_tree_write_then_check_regenerates_claude_rows` at `T:451`.
- Negative/green outputs:
  - Class flip: `F2 class flip drift: rc=1; stderr="... .claude class drift: agents/code-implementer.md: committed=kit-verbatim generated=kit-adapted"`.
  - New first-party file: `F2 new first-party file: rc=1; stderr="... .claude class drift: first-party-new.md: committed=<missing> generated=first-party"`.
  - Tampered index: `F2 index sha256 mismatch: rc=1; stderr='FAIL: kit index sha256 mismatch'`.
  - Malformed index: `F2 malformed index row: rc=1; stderr='FAIL: kit index parse failure at line 4: expected path<TAB>mode<TAB>git-blob-sha1'`.
  - Green: `WROTE sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv (3053 paths)` and `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots`.

ITEM 4 — F3 declared root type bound

- Changed `M`: `walk_tree` refuses a root symlink at `M:186`; the root type digest record is at `M:196`; `validate_sandbox_kit_entries` refuses top-level root symlinks at `M:292` before unknown-entry reporting.
- Tests: `test_declared_root_symlink_is_refused_by_name` at `T:571`; `test_declared_root_symlink_target_outside_sandbox_kit_is_refused_by_name` at `T:588`; `test_declared_root_dangling_symlink_is_refused_by_type` at `T:601`.
- Negative/green outputs:
  - Plain control: `F3 plain declared-root control: rc=0; stdout='PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots'; stderr=''`.
  - Root symlink: `F3 declared root symlink: rc=1; stderr='FAIL: declared root is a symlink: .../sandbox-kit/aleph -> aleph-real'`.
  - Dangling root symlink: `F3 dangling declared root symlink: rc=1; stderr='FAIL: declared root is a symlink: .../sandbox-kit/aleph -> aleph-missing'`.

ITEM 5 — F4 K1 report rewritten against this PIN

- Rewrote `tasks/briefs/kit-k1-support/K1-report.md` with PIN `46186d6`, kit index SHA-256 `5d266a2bbd7c84d1cf59ffde52eb0c596bb96ab930982dd74778541425ddf02c`, post-repair file identities, K1-e header behavior, current gate outputs, and out-of-scope NOT-DONE.
- `K1-report.md` records bounded report lint output at `tasks/briefs/kit-k1-support/K1-report.md:91`: `report_lint: 66 refs — OK 26, NEAR 3, MISS 25, UNCHECKABLE 12, UNRESOLVED 0 (worktree)`.

THE THREE COUNTS + ADAPTED PATHS

- Counts from `V:19-21`: kit-verbatim 2,958; kit-adapted 14; first-party 81; kit-only 19 from `V:11`.
- Adapted paths from `C`: `agents/adversarial-verifier.md`; `hooks/edit-snapshot.py`; `hooks/graft-first-nag.py`; `hooks/session-start.sh`; `hooks/turn-retro-gate.sh`; `settings.json`; `skills/adversarial-review/SKILL.md`; `skills/anti-hollow-green/SKILL.md`; `skills/build-loop/SKILL.md`; `skills/code-intel-trio/SKILL.md`; `skills/contract-gate/SKILL.md`; `skills/deep-work/SKILL.md`; `skills/orchestration/SKILL.md`; `skills/session-continuity/SKILL.md`.

MUTATION TABLE

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
- Mutant suite output: `11 passed, 34 deselected in 8.35s`.

GATES

- `python3 scripts/vendored_manifest.py --root . --write`: `WROTE sandbox-kit/VENDORED-MANIFEST.md (9 roots)`; `WROTE sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv (3053 paths)`.
- `python3 scripts/vendored_manifest.py --root . --check`: `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots`; `write_rc=0 check_rc=0`.
- `bash scripts/test_summary.sh tests/test_vendored_manifest.py -n 8 --basetemp .../scratch/bt1`: `pytest-summary: 45 passed in 27.02s`; `pytest-exit: 0`.
- Repeat `bt2`: `pytest-summary: 45 passed in 26.09s`; `pytest-exit: 0`.
- Set id beside both counts: `1 files set=21e700b8344c`.
- `/home/rocco/venv-agent-factory/bin/python -m pyflakes scripts/vendored_manifest.py tests/test_vendored_manifest.py`: rc 0.
- `git diff --check`: rc 0.
- `python3 scripts/ap_screen.py scripts/vendored_manifest.py tests/test_vendored_manifest.py`: `AP-32: 6`, `AF-AP-40: 5`, `AP-1: 1`. Classifications are in `K1-report.md`.
- `python3 scripts/report_lint.py tasks/briefs/kit-k1-support/K1-report.md ...`: `report_lint: 66 refs — OK 26, NEAR 3, MISS 25, UNCHECKABLE 12, UNRESOLVED 0 (worktree)` after one bounded hint round.
- `python3 scripts/report_lint.py tasks/briefs/kit-k1-support/K1-g-report.md ... --min-refs 20`: `report_lint: 68 refs — OK 42, NEAR 1, MISS 23, UNCHECKABLE 2, UNRESOLVED 0 (worktree)` after bounded lint.

FILE IDENTITY — POST-REPAIR

- `scripts/vendored_manifest.py`: SHA-256 `023525eef8db1fdce4e8f06aa757447e3df5fe5631885c51985e3b608bd7af91`; 957 lines.
- `tests/test_vendored_manifest.py`: SHA-256 `fe6165d53d164edf53670d9f6d1ae0a4615c9d749f99a704acf0e458a27ec372`; 1,007 lines.
- `sandbox-kit/VENDORED-MANIFEST.md`: SHA-256 `1c4e0abe0cefd80b5d35308e2b71df15bf8320e953eca48f91326e8b2349d2bf`; 30 lines.
- `sandbox-kit/VENDORED-FROM.md`: SHA-256 `552f695e6e6cde893b30e444d0c0ff17f0e93a9135512ef17ba5ad2f4fc7e99c`; 55 lines.
- `sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv`: SHA-256 `750c5532f248aec91193d82f83da31e5de6de8020fb1bdf10512a5cd37fcbfb1`; 3,054 lines.
- `sandbox-kit/dot-claude.aeb3082.index.tsv`: SHA-256 `5d266a2bbd7c84d1cf59ffde52eb0c596bb96ab930982dd74778541425ddf02c`; 2,992 lines.
- `tasks/briefs/kit-k1-support/K1-report.md`: rewritten; see worktree bytes.

DISCREPANCIES

- `tasks/briefs/kit-k1-support/K1-g-pack.md` was absent at this PIN. Replacement pack generated at `/home/rocco/agent-factory/.lanes/pc-k1-g.md--46186d6/scratch/K1-g-post-pack.md`.
- AP screen reported `path.is_file` hits as `AF-AP-40`, not the brief's expected `AF-AP-70` label.
- Test count changed from 22 to 45 because K1-g added F1-F3/F2 coverage and mutation rows.
- Red-first was proven by failing negative controls and mutation kills in scratch, not by a chronological pre-edit test commit. This is a build-lane deviation, reported here.
- `downloaded_files/` is untracked in the lane worktree and was not touched by this repair.
- `report_lint: 68 refs — OK 42, NEAR 1, MISS 23, UNCHECKABLE 2, UNRESOLVED 0 (worktree)` is the final bounded report-lint line for this report.

NOT-DONE

- Independent adversarial verification has not run.
- Issue #19 remains out of scope: lock/SBOM agreement, special files and nested `.git`, REUSE licenses, atomic `--write`, informational header, and hook wiring.
- `.agents/`, `graft/`, and every other file outside the brief remain out of scope.
