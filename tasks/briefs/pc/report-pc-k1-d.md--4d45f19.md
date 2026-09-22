DONE: K1-d built the vendored-tree manifest at PIN `4d45f19`; deterministic self-validation is green. Independent sandbox adversarial verification has not run, so this remains a build-lane proposal.

NOT-DONE

- Independent adversarial verification has not run. This lane does not issue a gate verdict.
- `SBOM.yaml` and `upstream.lock.yaml` were read-only inputs and were not changed.
- The eight manifest sources have no shared source entry with `SBOM.yaml`/`upstream.lock.yaml` at this PIN. Their agreement loop therefore has no intersecting real entry; tests exercise generic `test_sbom_pin_disagreement_is_named` (`T:381`) and `test_manifest_root_matching_lock_must_use_lock_pin` (`T:407`).
- Three roots have no tree-local license file and are reported as `none found`: `.claude/` (`V:15`), `sandbox-kit/output-styles/` (`V:20`), and `sandbox-kit/reference-scripts/` (`V:21`).

BLOCKER (resolved by AMENDMENT 1)

- The 2026-09-08 lane correctly stopped because the original item-2 rule bounded symlinks by each vendored root. AMENDMENT 1 changed containment to the repository root while retaining fail-closed refusal for dangling and outside-repository targets. `symlink_record` enforces repository-root containment (`M:190`) and separately names dangling targets (`M:197`).

BLOCKER (resolved by AMENDMENT 2)

- K1-c correctly stopped because the six `.claude/skills/*` links AMENDMENT 1 said would pass all dangled at PIN `236bec7`. Commit `4d45f19` removed those repository defects. AMENDMENT 2 repinned the inventory to one resolving Formula link and supplied tests (a)-(e).

PREMISE CHECK

- PIN: `4d45f1944c1570bac4b542827f45365a31a78a93`.
- Symlink inventory: exactly `sandbox-kit/codebase-memory-mcp/Formula -> pkg/homebrew/Formula [resolves]`; count 1.
- Staged 2026-09-08 draft identity: `scripts/vendored_manifest.py` 559 lines; `tests/test_vendored_manifest.py` 320 lines.
- Initial pyflakes on those staged draft bytes: the staged draft imported `dataclasses` but did not use it; rc 1; no other hit. The import existed only in the staged predecessor bytes, not the final file.
- Draft real-tree red first: `python3 ../scratch/k1d/draft_vm.py --root . --check` returned rc 1: manifest drift at line 5 because the prior artifact omitted the required generated-at line.
- The resumed artifact also left `datetime` and `GENERATED_AT_PREFIX` orphaned. Two focused regression tests were red before repair: `2 failed in 2.07s`.
- Final behavior: `SOURCE_DATE_EPOCH` is parsed (`M:494`), the header calls `generated_at_utc` (`M:517`), and `normalize_generated_time` changes only that prefixed line (`M:557`). Tests pin byte identity (`T:137`), time-only normalization (`T:150`), and invalid epoch rc 1 (`T:174`).

DONE TABLE

| Item | Implementation | Negative/red control | Killer/assertion |
|---|---|---|---|
| 1 | Frozen `VENDORED_ROOTS` (`M:36`) and `--write`/`--check` flags (`M:579`) | `test_provenance_root_missing_from_declared_list_is_named` (`T:215`) | rc 1 (`T:234`) and the missing root appears in stderr (`T:236`) |
| 2 | `walk_tree` (`M:129`), `symlink_record` (`M:177`), and `build_records` (`M:465`) | Outside `/etc/hostname` (`T:245`), dangling target (`T:260`), cross-root allowed (`T:269`), moved Formula target (`T:310`) | Exact outside name (`T:251`), dangling name (`T:266`), digest changes (`T:285`), moved target name (`T:316`) |
| 3 | `generated_at_utc` (`M:493`), header (`M:517`), time normalization (`M:555`) | `test_invalid_source_date_epoch_is_named` sets `not-unix-seconds` (`T:170`) | Two writes compare equal (`T:137`); invalid input returns 1 (`T:174`) |
| 4 | `validate_pin_agreement` runs from `render` (`M:509`) | SBOM/lock mismatch (`T:381`) and manifest/lock mismatch (`T:407`) | Exact repo (`T:402`), both pins (`T:403`, `T:404`), and lock key (`T:446`) |
| 5 | Fresh-generation gate (`T:119`), changed-byte control (`T:201`), license fixture (`T:320`) | Changed byte returns 1 (`T:210`) and names `.claude/` (`T:212`) | `22 passed` twice via `test_summary.sh` |
| 6 | Named `MUTANTS` table (`T:449`) and parametrized runner (`T:486`) | Mutated module must raise the exact mutant name (`T:502`) | All four named branches reach an assertion (`T:510`, `T:523`, `T:544`, `T:557`) |
| 7 | Eight generated rows from `.claude/` (`V:15`) through honey (`V:22`) | Wrong generating commit returns 1 (`T:196`) | Commit drift names line 4 (`T:197`); gates below |

MANIFEST

- Row count: 8.
- Roots: `.claude/` (`V:15`); `sandbox-kit/aleph/` (`V:16`); `sandbox-kit/codebase-memory-mcp/` (`V:17`); `sandbox-kit/council-of-high-intelligence/` (`V:18`); `sandbox-kit/llm-wiki-compiler/` (`V:19`); `sandbox-kit/output-styles/` (`V:20`); `sandbox-kit/reference-scripts/` (`V:21`); `sandbox-kit/honey-for-devs/` (`V:22`).
- The single symlink is counted in the codebase-memory row: 513 regular files and 1 symlink (`V:17`).
- Two real writes with `SOURCE_DATE_EPOCH=1790068966` produced identical SHA-256: `aa12d2599319c32c1c645309d44d761f7f5d10fcc8c0df7546ce6813ba7ee274`; `cmp_rc=0`.
- Header commit: `4d45f1944c1570bac4b542827f45365a31a78a93` (`V:4`). Header UTC time: `2026-09-22T09:22:46Z` (`V:5`).

MUTANTS

| Mutant | Named killer | Mechanism |
|---|---|---|
| `unsorted-tree-digest` (`T:451`) | `test_walk_is_sorted_before_digest` (`T:456`) | Exact nested-path order asserted via `mutant.walk_tree` (`T:510`). |
| `empty-exclusions` (`T:459`) | `test_exclusions_do_not_affect_tree_record` (`T:464`) | `node_modules/module.js` is added (`T:520`) and output must equal baseline (`T:523`). |
| `remove-sbom-agreement` (`T:467`) | `test_sbom_pin_disagreement_is_named` (`T:469`) | Calls production `mutant.render` (`T:541`) and requires `detected` (`T:544`). |
| `remove-symlink-refusal` (`T:472`) | `test_escaping_symlink_is_refused_by_name` (`T:481`) | Creates `/etc/hostname` link (`T:551`) and requires `detected` (`T:557`). |

VERIFIED OUTPUT

- Two real checks: `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 8 vendored roots`; `check_rcs=0,0`.
- Mechanical summaries: `pytest-summary: 22 passed in 4.64s`; `pytest-summary: 22 passed in 4.22s`; both `pytest-exit: 0`.
- Pyflakes: `pyflakes_rc=0`. Py-compile: rc 0 for both Python files.
- Static-copy gates:
  - `RESULT: rev=4d45f1944c15 files=3 deleted=0 runs=1 tests=21e700b8344c identical=yes rc=0 summary="22 passed in 12.41s"`
  - `RESULT: rev=4d45f1944c15 files=3 deleted=0 runs=1 tests=21e700b8344c identical=yes rc=0 summary="22 passed in 12.07s"`
- Code-intel pack: `lane_context: pack written to ../scratch/k1d/final-pack.md (484 lines)`.
- GitNexus post-batch: `No changes detected.` The clone index cannot see lane-only additions, so this is not evidence of no lane diff.
- Ripwire found `render`, `walk_tree`, and `generated_at_utc` as new symbols with 4, 6, and 1 caller(s); each had `incompatible="0"`; counts are floors.

AP SCREEN CLASSIFICATION

- Production: `4 hits`. `AP-32` maps to required `hashlib.sha256` operations (`M:114`, `M:206`). `AF-AP-40` maps to the regular-file `path.is_file` branch (`M:155`), not a symlink-following claim. `AP-1` maps to reproducible-build `SOURCE_DATE_EPOCH` (`M:494`), resolved inside one CLI render rather than used between co-resident components.
- Tests: `1 hit`. `AP-66` maps to `setattr` (`T:219`), used to materialize a fixture-local declared-root omission; it does not mock the production sink.

FILE IDENTITY

- `scripts/vendored_manifest.py`: SHA-256 `b5a2c05c1342cdaccb38ac3c3e357bb0dc02b5cc0df7cbb2ff61c4342f99f33b`; 627 lines.
- `tests/test_vendored_manifest.py`: SHA-256 `144247852593e12efd00da2e95fc76ba3225762db4c2014183b4a43e6c9d5fd1`; 559 lines.
- `sandbox-kit/VENDORED-MANIFEST.md`: SHA-256 `aa12d2599319c32c1c645309d44d761f7f5d10fcc8c0df7546ce6813ba7ee274`; 22 lines.

DISCREPANCIES

- Original report path `tasks/briefs/kit-support/K1-report.md` does not exist. The continuation assigns `tasks/briefs/kit-k1-support/K1-report.md`; this report follows the continuation.
- The continuation predicted the draft real-tree run could refuse under the old boundary. At this PIN it wrote 8 roots because the six dangling `.claude/skills` links had already been removed and Formula remains inside its vendored root.
- The previous attempt reported a recovered baseline of `8 failed, 6 passed`. The final suite contains 22 passing cases.
- The first two lane-gate invocations used relative `-o` paths. Their side-log writes failed after the script changed cwd. Both gates were rerun with absolute paths; only the two clean RESULT lines above are evidence.
- `scripts/why.sh` cannot produce history for new staged files; it returned `fatal: ambiguous argument ''` because no committed symbol revision exists.
- GitNexus impact for generic `render` was ambiguous and its clone index was 439 commits stale. The lane-local pack and Ripwire mapped the actual new symbols.
- Bounded report lint final run: `report_lint: 99 refs — OK 53, NEAR 3, MISS 36, UNCHECKABLE 7, UNRESOLVED 0 (worktree)`; rc 1. The report exceeds the 10-reference floor. The remaining misses are cross-claim rows where one cited line cannot carry every token; I stopped after the required two hint-driven fix rounds.

SELF-ATTACK

1. Time normalization could hide commit drift. The wrong-commit control returns rc 1 (`T:196`) and names line 4 (`T:197`).
2. Symlink containment could use the vendored root or follow target content. The real-link test asserts target-string digest change (`T:116`); cross-root same-directory target-string change also changes the row (`T:285`); outside and dangling checks name their targets (`T:251`, `T:266`).
3. Mutant kills could be unrelated exceptions. The wrapper accepts only an exact `AssertionError` carrying `mutant_name` (`T:502`), and the SBOM branch invokes `mutant.render` (`T:541`). Independent adversarial mutation remains NOT-DONE.

HANDOFF

- Reasoning record: rejected weakening dangling-link refusal. Repository containment (`M:190`) precedes existence checking (`M:197`) so existing outside and dangling in-repository targets produce distinct failures. Primary inputs were the original brief, Amendments 1 and 2, provenance, SBOM, and lock files.
- Proposal scope is exactly `scripts/vendored_manifest.py`, `tests/test_vendored_manifest.py`, `sandbox-kit/VENDORED-MANIFEST.md`, and this report.
- Retro: the resumed draft's orphaned timestamp mechanism was a real defect fixed in this batch. Existing build-loop rules already cover stale claims and pyflakes; nothing new to bake.
