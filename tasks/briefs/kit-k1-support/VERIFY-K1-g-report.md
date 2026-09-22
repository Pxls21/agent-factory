VERIFY-K1-g REPORT — targeted adversarial verify of K1-g at PIN fe2284d

Recommendation only: MERGE-READY-WITH-FOLLOWUPS.
Coordinator owns the final gate verdict. This recommendation depends on accepting the repo's existing `SOURCE_DATE_EPOCH` + `normalize_generated_time` determinism contract for generated manifests; raw unpinned `--write` differs only on the generated timestamp line and is listed as F-01.

Scope and identity

- Lane tree: /home/rocco/agent-factory/.lanes/pc-verify-k1-g.md--fe2284d/tree
- PIN: fe2284d32dac52765b5d180dcfdc9e30115d4d90.
- Worktree status at close: 0 status lines before this report was written.
- Four pinned file SHA-256 values remeasured:
  - scripts/vendored_manifest.py = 023525eef8db1fdce4e8f06aa757447e3df5fe5631885c51985e3b608bd7af91; 957 lines.
  - tests/test_vendored_manifest.py = fe6165d53d164edf53670d9f6d1ae0a4615c9d749f99a704acf0e458a27ec372; 1,007 lines.
  - sandbox-kit/VENDORED-MANIFEST.md = f4eaa0410fd12501d1fbbfafce546459da83b27b32b64ce91b52ac0ac2cd615e; 30 lines.
  - sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv = 750c5532f248aec91193d82f83da31e5de6de8020fb1bdf10512a5cd37fcbfb1; 3,054 lines.
- `git diff --stat fe2284d HEAD -- scripts/vendored_manifest.py tests/test_vendored_manifest.py sandbox-kit/VENDORED-MANIFEST.md sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv` printed nothing.
- `python3 scripts/vendored_manifest.py --check` at the PIN: `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots`.

Anchor map for this report

- The closed root table is `SANDBOX_KIT_ENTRIES` at M:118; `validate_sandbox_kit_entries` is at M:284; `walk_tree` is at M:186.
- The F2 classifier is `claude_records` at M:346; digest comparison uses `git_blob_sha1(data)` at M:395; class serialization/parsing is `render_classes` at M:410 and `parse_classes` at M:416; drift naming is `class_difference` at M:429.
- Full generation flows through `build_manifest_data` at M:694, `render` at M:805, `normalize_generated_time` at M:859, and `main` at M:889.
- The timestamp determinism tests are `test_two_write_runs_are_byte_identical` at T:197 and `test_generation_time_is_only_normalized_drift_line` at T:212.
- The class-file monkeypatch that AP-66 flagged is `setattr` at T:469; it materializes the fixture-local mutated script with `write_text(mutated, encoding="utf-8")` at T:481.
- Manifest evidence rows include `.claude/ (kit-verbatim)` at V:19, `.claude/ (kit-adapted)` at V:20, `.claude/ (first-party)` at V:21, `sandbox-kit/docs/` at V:29, and `sandbox-kit/ (kit-portable files)` at V:30.
- Provenance evidence includes `docs/` at P:18 and `portable top-level files` at P:19.
- The committed class file begins with `path` at C:1 and `agents/adversarial-verifier.md` at C:2.

Gate commands

1. `python3 scripts/vendored_manifest.py --check`

Output:
PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots

2. `python -m pytest tests/test_vendored_manifest.py -q -p no:cacheprovider --basetemp=/home/rocco/tmp-vk1g/bt` twice, removing basetemp between runs.

Run 1 output:
.............................................                            [100%]
Running teardown with pytest sessionfinish...
45 passed in 48.44s
RC=0
2503	/home/rocco/tmp-vk1g/bt

Run 2 output:
.............................................                            [100%]
Running teardown with pytest sessionfinish...
45 passed in 49.38s
RC=0
2503	/home/rocco/tmp-vk1g/bt
bt_absent=yes

3. `python -m pytest tests/test_vendored_manifest.py --collect-only -q -p no:cacheprovider`

Output summary: 45 tests collected in 0.02s. This is 35 named `def test_` functions plus 10 parametrized mutant rows.

4. `python3 scripts/report_lint.py tasks/briefs/kit-k1-support/K1-g-report.md --root . --map M=scripts/vendored_manifest.py --map T=tests/test_vendored_manifest.py --map V=sandbox-kit/VENDORED-MANIFEST.md --map P=sandbox-kit/VENDORED-FROM.md --map C=sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv --min-refs 20`

Output summary:
report_lint: 68 refs — OK 42, NEAR 1, MISS 23, UNCHECKABLE 2, UNRESOLVED 0 (worktree)

This is the GR lint state at the PIN after bounded lint. It meets the floor but still has known bounded misses; classified as INFO because the evidence remains interpretable.

Item 1 — F1 closure over top-level sandbox-kit entries

Remeasured production source:
- `SANDBOX_KIT_ENTRIES` is the closed table at M:118.
- `validate_sandbox_kit_entries` refuses missing, symlinked declared roots, and unknown top-level entries at M:284.
- The manifest renders `sandbox-kit/docs/` and `sandbox-kit/ (kit-portable files)` rows at V:29-30; provenance rows are P:18-19.

New-shape probes through `python3 scripts/vendored_manifest.py --root <fixture> --check|--write`:

- New top-level file: rc 1, `FAIL: undeclared entry under sandbox-kit/: stray-file.txt`.
- New top-level dir: rc 1, `FAIL: undeclared entry under sandbox-kit/: straydir`.
- Declared root symlink to an inside target: rc 1, `FAIL: declared root is a symlink: .../sandbox-kit/aleph -> docs`.
- Declared root symlink outside: rc 1, `FAIL: declared root is a symlink: .../sandbox-kit/aleph -> ../aleph-real`.
- Declared root dangling symlink: rc 1, `FAIL: declared root is a symlink: .../sandbox-kit/aleph -> ../gone-target`.
- Declared root regular file: rc 1, `FAIL: vendored root missing or not a directory: .../sandbox-kit/aleph`.
- Declared root empty dir: rc 1, `FAIL: vendored manifest drift: line 29`, changing the docs row from 1 file to 0.
- Case variant and trailing-dot/space names: rc 1. `NewTool` and `aleph.` / `aleph ` are treated as undeclared literal names.
- Nested `.git` inside a declared root: #19 says nested `.git` is out of scope. Measured behavior: `--write` rc 0, nested `.git` itself is excluded, but the non-`.git` `subproj/a.txt` changes the `sandbox-kit/aleph/` row from 158 to 159 files; after `--write`, `--check` rc 0.

Assessment: F1 closure held. No blocker.

Item 2 — F2 `.claude/` split

Independent reproduction, not using the script's classifier:
- My own `os.walk` of `.claude/` + own git-blob-sha1 comparison against sandbox-kit/dot-claude.aeb3082.index.tsv produced: kit-verbatim 2958, kit-adapted 14, first-party 81.
- Committed sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv produced the same counts: kit-verbatim 2958, kit-adapted 14, first-party 81.
- Kit-only paths in index absent here: 19.
- Path-by-path mismatch between my walk and committed class file: 0.
- Total `.claude/` paths in my walk: 3053.

New-shape probes through the real tool:

- First-party file bytes changed to equal a kit file: rc 1, row drift on `.claude/ (first-party)`; the first-party digest changed while count stayed 81.
- Kit-adapted file re-verbatimized from the pinned upstream blob: rc 1, `.claude class drift: agents/adversarial-verifier.md: committed=kit-adapted generated=kit-verbatim`; kit-verbatim count changed 2958 -> 2959.
- Path present in index but absent on disk: rc 1, kit-only count changed 19 -> 20, and `.claude class drift: agents/adversarial-verifier.md: committed=kit-adapted generated=<missing>`.
- Path on disk absent from index: rc 1, first-party count changed 81 -> 82, and `.claude class drift: NEW_FIRST_PARTY.md: committed=<missing> generated=first-party`.
- Class-file row edited by hand: rc 1, `.claude class drift: agents/codebase-memory-auditor.md: committed=kit-verbatim generated=first-party`.
- Class file deleted: rc 1, `FAIL: declared sandbox-kit entry missing: VENDORED-CLAUDE-CLASSES.tsv`.
- Class file duplicated path row: rc 1, `FAIL: .claude class drift: byte length differs`.
- CRLF class file: rc 0, `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots`; see F-02.

Assessment: F2 semantic split held. The CRLF behavior is a follow-up, not a blocker.

Item 3 — F3 root type

Remeasured source:
- `walk_tree` refuses a declared root symlink before digest work at M:186.
- `validate_sandbox_kit_entries` also refuses symlinked top-level declared roots at M:284.
- The manifest states root type `dir` in the header at V:9, and `Tree SHA-256` row digests include the root-type domain.

New-shape probes:

- Declared root symlink to real dir inside sandbox-kit: rc 1, `declared root is a symlink: .../sandbox-kit/aleph -> ../sandbox-kit/docs`.
- Declared root symlink to real dir outside sandbox-kit: rc 1, `declared root is a symlink: .../sandbox-kit/aleph -> ../aleph-real`.
- Declared root dangling symlink: rc 1, `declared root is a symlink: .../sandbox-kit/aleph -> ../nowhere`.
- Declared root regular file: rc 1, `vendored root missing or not a directory: .../sandbox-kit/aleph`.
- FIFO at declared root path, under a 60 second subprocess timeout: rc 1, `vendored root missing or not a directory: .../sandbox-kit/aleph`; no hang.
- Changed root type for docs -> symlink: rc 1, `declared root is a symlink: .../sandbox-kit/docs -> ../docs-real`.

Assessment: F3 held. No blocker.

Item 4 — generated manifest

Remeasured source:
- `render` emits a live timestamp with `generated_at_utc()` at M:805.
- `normalize_generated_time` blanks both timestamp and generating commit before drift comparison at M:859.
- `main` handles `--write` and `--check` at M:889; the drift comparison loop begins with `for attempt in range(2)` at M:919 and compares committed vs generated data.
- The tests pin the deterministic-write contract with `SOURCE_DATE_EPOCH` in `test_two_write_runs_are_byte_identical` at T:197 and prove timestamp-only drift is normalized in `test_generation_time_is_only_normalized_drift_line` at T:212.

Probes:

- `SOURCE_DATE_EPOCH=1700000000` pinned `--write` twice: manifest sha256 identical `6676109be410178da7e8fbaf8b9ac3dc7103e3ca5637475755d24f3f539a5c8d`; classes file byte-identical; rc 0 both times.
- Raw unpinned `--write` twice: 30 vs 30 lines; only line 5 differed:
  - raw#1 L5: `Generated at (UTC): 2026-09-22T19:01:03.297803Z`
  - raw#2 L5: `Generated at (UTC): 2026-09-22T19:01:05.202585Z`
  See F-01.
- `--check` on the committed manifest, which names parent commit 8597250, at later HEAD fe2284d: rc 0, `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots`.
- Whitespace-only manifest edit, trailing blank line: rc 1, `vendored manifest drift: line 31: committed=''; generated='<missing>'`.
- Data row reorder: rc 1, drift at line 19.
- Header edit: rc 1, drift at line 2.
- Untracked file in `sandbox-kit/aleph/`, no commit: rc 1, aleph row changed from 158 -> 159 files. This proves `--check` is filesystem-live for vendored bytes; git is used only to capture the generating revision and detect HEAD changing during the run.

Assessment: generated-manifest drift checks held. Raw default write byte identity is a contract wording ambiguity / follow-up, not a K1-g blocker under the repo's existing `SOURCE_DATE_EPOCH` + normalized-check contract.

Item 5 — mutants

Mutants were run in scratch copies only. Current-tree tests also include the registered mutant killers in `MUTANTS` at T:744 and exercise them with `test_required_mutants_are_killed` at T:860.

Production-path scratch probes:

- Drop unknown-entry refusal: with undeclared `sandbox-kit/newtool`, mutant rc 0, `PASS`. Correct implementation rejects it. Named killer in the suite: `test_undeclared_sandbox_kit_entry_is_named`.
- Drop missing-declared-entry refusal: with `sandbox-kit/docs/` removed, exact suite-style mutant still rc 1 through row drift on `sandbox-kit/docs/` changing from 1 file to 0. This is redundant detection, not a hollow green.
- Drop root-symlink refusal in both `walk_tree` and top-level sandbox-kit validation: declared root symlink mutant rc 0, `PASS`. Correct implementation rejects it. Named killer: `test_declared_root_symlink_target_outside_sandbox_kit_is_refused_by_name`.
- Drop class-file comparison / drift naming: hand-edited class file mutant rc 0, `PASS`. Correct implementation rejects and names the path. Named killer: `test_claude_class_drift_names_changed_path`.
- Compare index by path only / ignore digest: changed indexed verbatim file was written as `kit-verbatim` by the mutant and self-check passed. Correct implementation classifies changed bytes as adapted. The committed suite's closest registered mutant is `blob-sha-without-git-header`, which rc 1 on unchanged fixture and is killed by `test_real_claude_split_counts_and_class_file`.
- Accept a relative root: no absolute-root guard exists to mutate; `main` resolves `args.root` with `Path.resolve()` before mode handling. This is a brief discrepancy, not a blocker.

Assessment: mutation audit supports the guards. No current-code blocker.

Item 6 — disk discipline

- Full suite ran twice with `--basetemp=/home/rocco/tmp-vk1g/bt` and the basetemp removed between runs.
- Each run's basetemp: 2503 MB.
- Threshold in brief: finding if a single run exceeds 3 GB or cannot run twice. This did not happen.
- `/home` free after scratch probes: 415G.
- Scratch `/home/rocco/tmp-vk1g` grew to about 1970 MB because probe fixtures remain for evidence; pytest basetemp was removed.

Assessment: disk discipline held. No blocker.

Item 7 — report anchors

- GR lint at the PIN: `report_lint: 68 refs — OK 42, NEAR 1, MISS 23, UNCHECKABLE 2, UNRESOLVED 0 (worktree)` with `--min-refs 20`.
- This verifier report is linted separately with `--min-refs 10`; see close line below.

Assessment: GR remains mechanically interpretable despite bounded misses. No blocker.

Item 8 — AP screen

Command:
`python3 scripts/ap_screen.py --tests scripts/vendored_manifest.py tests/test_vendored_manifest.py`

Output:
--- TEST_SCREEN over 2 path(s): 3 hits over 2 files ---
AF-AP-57: 2
    VM path scripts/vendored_manifest.py line 554 contains `if row_count == 0:`
    VM path scripts/vendored_manifest.py line 932 contains `if attempt == 0:`
AP-66: 1
    T path tests/test_vendored_manifest.py line 469 contains `setattr(`

Classification:
- AP-66 at T:469 is benign test scaffolding: the line is the literal `setattr(` call. It mutates the loaded module's `VENDORED_ROOTS`, then materializes that in-memory tuple into a fixture-local script at T:481 before running the production CLI path. It is not a production class instance and does not affect the lane tree.
- AF-AP-57 hits are bounded-control/test-screen hits: `row_count == 0` is an index parser validation path, and `attempt == 0` is the one retry when HEAD changes during `--check`. No blocker.

Finding inventory

F-01 FOLLOW-UP — raw unpinned `--write` is not byte-identical.
- Evidence level: reproduced through production `--write`.
- Contract mapping: ambiguous. The verify brief says to run `--write` twice and prove byte-identical output; the repository's own tests define determinism under `SOURCE_DATE_EPOCH` and `--check` normalizes generation metadata.
- Canonical path: yes, `python3 scripts/vendored_manifest.py --root <fixture> --write`.
- Material effect: raw output bytes differ on line 5 only, the timestamp line. Vendored rows and class file remain stable when `SOURCE_DATE_EPOCH` is pinned.
- Concrete discriminator: raw two-write probe showed line 5 changed; pinned SDE probe was byte-identical.
- Task ownership: in boundary, but changing it would be a design choice about whether the timestamp belongs in the committed artifact.
- Suggested fix: either state `SOURCE_DATE_EPOCH` explicitly in the verify contract, or remove/live-normalize the timestamp on `--write` if raw byte identity is required.
- Blocking predicate: not complete because the frozen K1-g behavior in tests is SDE-pinned/normalized determinism, not raw timestamp-free output.

F-02 FOLLOW-UP — CRLF line endings in `VENDORED-CLAUDE-CLASSES.tsv` are accepted.
- Evidence level: reproduced through production `--check`.
- Contract mapping: item 2 asked for a CRLF vs LF probe; no frozen criterion says line-ending normalization must fail.
- Canonical path: yes, class file bytes rewritten to CRLF then `--check` returned rc 0.
- Material effect: semantic class rows are unchanged; raw evidence bytes differ.
- Concrete discriminator: CRLF probe rc 0.
- Task ownership: in boundary if the project wants byte-exact class-file evidence.
- Suggested fix: if desired, read class files as bytes or reject CRLF explicitly before `parse_classes`.
- Blocking predicate: not complete; no material semantic class drift and no predeclared byte-exact line-ending requirement.

F-03 INFO — duplicated class-file rows fail, but the error is generic.
- Evidence level: reproduced.
- Contract mapping: item 2 duplicate path probe.
- Canonical path: yes.
- Material effect: no pass-through; `--check` rc 1 with `.claude class drift: byte length differs`.
- Suggested fix: optional duplicate-path detection in `parse_classes` for a more actionable error.
- Blocking predicate: not complete; the production path fails closed.

F-04 INFO — exact suite mutant for missing-declared-entry still fails through row drift.
- Evidence level: reproduced with exact suite-style mutant.
- Contract mapping: item 5 mutant.
- Canonical path: yes.
- Material effect: no hollow green; the mutated implementation still rejects missing docs via changed manifest row.
- Suggested fix: none required. This is redundant coverage.
- Blocking predicate: not complete; no defect in current code.

F-05 INFO — GR report and K1-report SHA values disagree by hash kind / regeneration context.
- Evidence level: reproduced from files.
- Contract mapping: report/evidence audit.
- Canonical path: yes; actual file SHA-256 of `sandbox-kit/VENDORED-MANIFEST.md` is f4eaa0410fd12501..., while K1-report line 81 lists 1c4e0abe..., apparently from the post-edit regenerated working copy. The brief's PIN identity is correct for fe2284d.
- Material effect: report-accuracy issue only; the pinned file identity and `--check` output are directly remeasured here.
- Suggested fix: future reports should label git blob hash vs file SHA-256 and distinguish committed artifact from regenerated scratch artifact.
- Blocking predicate: not complete; the required evidence was independently rederived.

F-06 INFO — AP-66 at T:469 (`setattr(`) is benign test scaffolding.
- Evidence level: reviewed primary source and AP-screen output.
- Contract mapping: item 8.
- Canonical path: test-only.
- Material effect: none in production; fixture-local script only.
- Suggested fix: none.
- Blocking predicate: not complete.

Deliberately skipped

- Issue #19 nested `.git` expansion remains out of scope. I measured nested `.git` behavior only as requested.
- No outward-facing actions, no commits, no pushes, no production-server operations.
- I did not verify unrelated vendored components beyond the K1-g manifest/classification boundary.

Close gates for this report

- `python3 scripts/report_lint.py tasks/briefs/kit-k1-support/VERIFY-K1-g-report.md --root . --map M=scripts/vendored_manifest.py --map T=tests/test_vendored_manifest.py --map V=sandbox-kit/VENDORED-MANIFEST.md --map P=sandbox-kit/VENDORED-FROM.md --map C=sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv --min-refs 10`: `report_lint: 43 refs — OK 41, NEAR 1, MISS 0, UNCHECKABLE 1, UNRESOLVED 0 (worktree)`.

Gate recommendation

MERGE-READY-WITH-FOLLOWUPS — recommendation only, no final verdict. No finding satisfied the full blocking predicate. Follow-ups are F-01 raw `--write` wording/default determinism, F-02 CRLF class-file byte normalization, F-03 optional duplicate-row naming, and F-05 report hash-kind clarity.
