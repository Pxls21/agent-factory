VERIFY-K1 — adversarial verification report

PIN: cd976f5b1171ec035e9540fb33b6f79e09726060
Route: agentfactory-verify-local. The venue says this is HYBRID in practice: a local-model combination may fall through cloud step 2. I did not verify which model produced this report. gpg-free.
Scope: K1-d + K1-e only: `scripts/vendored_manifest.py` (M), `tests/test_vendored_manifest.py` (T), `sandbox-kit/VENDORED-MANIFEST.md` (V), `sandbox-kit/VENDORED-FROM.md` (P), and the lane report evidence. Scratch probes were under `/home/rocco/agent-factory/.lanes/pc-verify-k1.md--cd976f5/scratch`; no production server, credential, or live tree was changed.

PREMISE — SOLID

`git rev-parse HEAD` = `cd976f5b1171ec035e9540fb33b6f79e09726060`; status was clean.

File identity at the PIN:
- M: SHA-256 `6528c8da30e38e551fe34c01be67b4ff707404f9586920e6f9d218a75aa28d0e`; 637 lines.
- T: SHA-256 `e29b4a4fec3ae7ec6fa83b6d7fe1858f60683f2648e2cef600a90630482a1371`; 568 lines.
- V: SHA-256 `ff472fc4d937a81d317c6791b3af63247e6939095ba01e6693cbe7f59e5c7b69`; 22 lines.

`python3 scripts/vendored_manifest.py --root . --check` → rc 0: `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 8 vendored roots` (2026-09-22T10:41:45Z).

`bash scripts/test_summary.sh tests/test_vendored_manifest.py -n 8 --basetemp <lane>/scratch/bt1` → rc 0: `22 passed in 12.13s`.

Repeat at `<lane>/scratch/bt2` → rc 0: `22 passed in 11.98s`.

FINDING INVENTORY

F1 — BLOCKER — SOLID

Contract mapping: owner audit bar requires the manifest to bind every vendored tree so reviewers may mechanically skip vendored trees. `sandbox-kit/docs/` is declared portable vendored content in P:17 (`portable docs`), but it is not a `VENDORED_ROOTS` entry (M:36-93) and its bytes are not under any declared root.

Canonical reproduction: a `copy_fixture`-shaped scratch repo, with current `sandbox-kit/docs/` copied in, passed the real check; after appending a byte to `sandbox-kit/docs/THIRD-PARTY-AGENT-TOOLS.md`, real `--check` still returned rc 0 `PASS...matches 8 vendored roots`. A newly created `sandbox-kit/newtool/file.txt` likewise remained invisible at rc 0.

Material effect: a reviewer relying on V can mechanically skip a changed vendored tree that V never binds.

Concrete discriminator: `python3 <fixture>/scripts/vendored_manifest.py --root <fixture> --check` is rc 0 before and after the undeclared-tree byte mutation; a complete tree inventory must reject it or include its changed digest.

Task ownership: manifest root inventory / declared-root validation in this component. Suggested fix: establish a complete tree classification (vendored / first-party / excluded-by-explicit-policy) and reject undeclared vendored paths, or add the actual vendored docs root. Do not silently classify it as first-party.

F2 — BLOCKER — SOLID

Contract mapping: owner asked for “the vendored PARTS of `.claude/`”; a source/pin claim must describe the tree it digests. V:15 claims whole `.claude/` comes from `pxls21/sandbox-kit:dot-claude/ @ aeb3082`.

Canonical reproduction: P:11 (`Adapted`) itself records adaptations; git history after the kit import `3c0d49e` records 24 `.claude/agents`, 12 commands, 4 output styles, and 44 skills first added. `.claude/skills/orchestration/SKILL.md` was last changed in commit `5802919` on 2026-09-22. The current whole-tree V row still asserts one upstream source/pin.

Material effect: the committed provenance in V is false for the tree whose digest reviewers are asked to trust. This is a hollow-green evidence claim, not a mere hardening gap.

Concrete discriminator: the manifest’s claimed upstream pin remains `aeb3082` after a first-party `.claude` byte change; `--check` merely regenerates a digest and passes after rewrite, never distinguishes upstream-derived versus first-party parts.

Task ownership: root scope/provenance representation in the manifest. Suggested fix: split `.claude/` into the actual vendored subtrees and explicit first-party trees, or remove the false whole-tree source/pin claim. This requires the owner’s `.claude` scoping decision but the current claim cannot be retained.

F3 — BLOCKER — SOLID

Contract mapping: owner audit bar explicitly requires binding path and type (file / symlink / directory).

Canonical reproduction: in a clean copy_fixture-shaped repo, move declared `sandbox-kit/aleph/` to sibling `sandbox-kit/aleph-real/`, replace it with `sandbox-kit/aleph -> aleph-real` symlink, retaining identical content. The real command `python3 scripts/vendored_manifest.py --root <fixture> --check` returned rc 0 `PASS...matches 8 vendored roots`.

Mechanism: M:129-135 calls `root.is_dir()` and `os.walk`. `Path.is_dir()` follows a root symlink; os.walk begins from the resolved directory. The child `path.is_symlink` logic at M:142-156 records only entries below the root, so the root object’s own directory-versus-symlink type and target are absent from the tree digest.

Material effect: type substitution at a declared root changes containment/trust semantics while preserving V’s row and `--check` pass. This directly defeats the stated completion bar.

Concrete discriminator: real `--check`: ordinary directory rc 0; directory→in-repo-symlink-to-identical-moved-tree rc 0. A corrected gate must return rc 1 or bind the root-link target/type in V.

Task ownership: `walk_tree` / record rendering / tests. Suggested fix: reject a declared-root symlink by `root.is_symlink()` before `is_dir`, or render/digest the declared root type and exact target explicitly; add the exact directory→symlink mutant as a regression test.

F4 — BLOCKER — SOLID

Contract mapping: K1-e evidence requires the later-HEAD behavior: generating-commit line informational; row drift still caught. The report is committed in the same increment and its claims are part of the requested evidence.

Canonical reproduction: `tasks/briefs/kit-k1-support/K1-report.md:20` claims PIN `4d45f19`; :76-78 claim M/T/V identities `b5a2...` / 627, `144247...` / 559, and `aa12...`; :38 and :92 say a wrong generating commit returns rc 1 and names line 4. At cd976f5, independently measured identity is M `6528c8...` / 637, T `e29b4a...` / 568, V `ff472f...`; `git show 4d45f19:<each K1 path>` reports those files do not exist. T:180-207 asserts the opposite of the report’s K1-e claim: later HEAD passes, while a changed vendored byte fails without `line 4` / `Generated from commit` in stderr.

Material effect: the committed lane report claims stale behavior that K1-e intentionally changed, and cites a PIN where the asserted files do not exist. It makes required evidence false and uninterpretable.

Concrete discriminator: `git show 4d45f19:scripts/vendored_manifest.py` exits nonzero; `sha256sum` at cd976f5 disagrees with report :76-78; the `test_committed_manifest_passes_check_at_a_later_head` test at T:180-207 contradicts report :38/:92.

Task ownership: current increment’s committed K1 report. Suggested fix: rewrite it against cd976f5, remove false historical assertion or label it pre-K1-e, and rerun report lint on the resulting bytes.

F5 — FOLLOW-UP — SOLID

The lock/SBOM agreement branch that specifically checks a manifest root is vacuous on the real tree. Primary-source parsing: lock entries 24; SBOM entries 22; intersection 22; `manifest roots whose normalized source is in lock = []`. M:435-448 therefore iterates zero real roots. Generic tests show the code branch works when synthetic matching source data exist, but no current V source/pin is bound to lock/SBOM. This does not independently block because V labels unpinned copies explicitly and no frozen bar says all vendor sources must already be lock entries. Fix later by recording immutable sources in upstream.lock/SBOM or accurately retaining the unpinned designation.

F6 — FOLLOW-UP — SOLID

Special files silently evade the tree digest. In a declared root: FIFO rc 0; UNIX socket rc 0; empty directory rc 0; nested `.git/config` creation and byte change each rc 0. The child `path.is_symlink` test at M:142 and `excluded` at M:140/M:151 omit nested `.git`; M:155 only records `path.is_file`; M:142/153 record links. A nested vendored submodule identity can therefore be hidden. Device-node creation was unavailable in the unprivileged venue. Unreadable regular file and non-UTF8 filename fail closed (rc 1) but emit raw exceptions rather than `ManifestError`. This is meaningful but does not meet the frozen bar unless special-file refusal was a stated criterion. Suggested follow-up: explicitly reject special files / nested `.git` under declared roots, or state exclusions in the contract.

F7 — FOLLOW-UP — SOLID

License coverage is intentionally narrow: M:234-253 only accepts top-level `license|copying|notice*`; REUSE `LICENSES/` returns `none found`. A symlink named LICENSE yields `unknown, LICENSE` because the candidate’s tree record has a `symlink:` target-string payload but `license_for` reads the target content separately (M:244-253). Observed supported printed identifiers are MIT, Apache-2.0, AGPL-3.0, CC0-1.0, unknown, and none found. This does not falsify the stated owner bar (license is present as an attestation), so it is a follow-up, not a blocker.

F8 — FOLLOW-UP — SOLID

M:594-603 enters `if args.write` then calls `manifest.write_text` (non-atomic). Chmod-444 target: `--write` rc 1 permission denied, old V remains and `--check` rc 0. A manually truncated V makes `--check` fail closed at line 1. No data corruption was reproduced because the OS rejected before truncation. Suggested future hardening: atomic temp-write + fsync + replace; current failure mode is fail-closed.

F9 — INFO — SOLID

K1-e makes both header lines informational. A forged `Generated from commit: 000...` with correct rows returns real `--check` rc 0. This is consistent with M:555-570. `git log -1 --format=%H -- <eight roots>` gives `5802919c9f4e9f961f119ba34761596db245374f`; it could be a trace signal but cannot replace per-root digest verification. I recommend retaining the “informational” label and not treating the header as a pin.

F10 — INFO — SOLID

Symlink branch behavior reproduced. Existing `symlink:` outside-file/outside-directory links and a relative `..` escape give rc 1 `escaping symlink refused`; dangling inside target gives rc 1 `dangling symlink refused`; an in-repo cross-root `.claude -> .agents` link is accepted into generation and changes its V row; target-string differences change the row. The `relative = path.relative_to(root).as_posix()` entry in `symlink_record` (M:177-202) supports this, but does not cure F3 root-symlink substitution.

AUDIT BAR: BINDINGS

- Path: `V:15-22` renders each `TreeRecord.path`; M:474 assigns `path=item.path`. The V row begins `| `.claude/` |`; paths are bound for rows, but F1 shows coverage is incomplete.
- Type: child file/symlink distinction is encoded by `path.is_symlink` (M:142-156) / `symlink_record` (M:177-202); declared root type is NOT bound (F3).
- Target existence: `resolved.relative_to` and `resolved.exists` (M:188-201) check a contained child-link target; declared root link is NOT checked as a link (F3).
- Source: M:475 assigns `source=item.source`; V source column. Whole `.claude` claim is false (F2).
- Commit/version: M:476 assigns `pin=item.pin`; V pin. The current header commit is explicitly not a verified input (F9).
- License: `license_for` (M:234-253) and `license=license_id` (M:478-480); narrow but displayed.
- Tree digest: `digest.update` (M:205-212), `tree_sha256=digest_records(files)` (M:483), and V final column. It protects walked regular files and child symlink target strings, not declared root type (F3).

MUTATION TABLE

All 11 were scratch-only, compiled (`py_compile` rc 0), and collected exactly 22 cases (`pytest --collect-only` rc 0). The baseline file SHA before and after was identical: `6528c8da30e38e551fe34c01be67b4ff707404f9586920e6f9d218a75aa28d0e`.

| Mutant | Result | Killer / observation |
|---|---|---|
| drop `resolved.exists()` | KILLED | T dangling-symlink test fails |
| `followlinks=True` | EQUIVALENT | full T suite 22/22; child dir links are removed from `dirnames` before descent (M:137-146) |
| digest regular file by path only | KILLED | later-HEAD changed-byte test fails |
| exclude `tests/` | KILLED | real-link target-string test fails on baseline change; direct mutant baseline shows a new tests byte is ignored while correct check fails |
| first license candidate | KILLED | license fixture fails; direct unknown LICENSE + Apache COPYING observes mutant unknown vs correct Apache-2.0 |
| row-count-only check | KILLED | later-HEAD changed-byte test fails; direct mutant baseline accepts byte drift while correct check fails |
| final sort dropped | KILLED | T sorting test fails |
| declared-root validation dropped | KILLED | T provenance-root-missing test fails; direct mutant baseline accepts added provenance row while correct check fails |
| drop `.claude/` root from table | KILLED | mutant `--write` refuses with `roots missing from declared list: .claude/` |
| normalize every `Generated...` header | EQUIVALENT | full T suite 22/22; a row-byte drift still fails on row, not header |
| ignore SOURCE_DATE_EPOCH | KILLED | two-write epoch test fails |

The named suite kills 9/11 non-equivalent mutants. The two survivors are equivalent with the present format/control flow. Mutation evidence does not cover F1/F2/F3: no existing test mutates declared-root type, all-tree coverage, or provenance segmentation. F3 is therefore independently reproduced through real `--check` above.

GATES

- `--check`: rc 0 `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 8 vendored roots`.
- pytest pass 1: 22 passed in 12.13s, rc 0.
- pytest pass 2: 22 passed in 11.98s, rc 0.
- `/home/rocco/venv-agent-factory/bin/python -m pyflakes M T`: rc 0 (2026-09-22T11:51:05Z).
- `python3 scripts/ap_screen.py M`: AP-32 twice at M:114/M:206 (`hashlib.sha256`); AF-AP-40 M:155 (`path.is_file`); AP-1 M:494 (`SOURCE_DATE_EPOCH`).
- `python3 scripts/ap_screen.py T`: AF-AP-70 twice at T:198/T:214 (`path.is_file`); AF-AP-40 T:37 (`source.exists`); AP-32 T:340 (`hashlib.sha256`).
- Report lint: three bounded hint-driven rounds were run. The last executed lint summary, before its final two wording fixes, was `report_lint: 37 refs — OK 35, NEAR 0, MISS 2, UNCHECKABLE 0, UNRESOLVED 0 (at cd976f5)`; rc 1. A fourth run is prohibited by AF-AP-76. The two remaining hints were applied to the current report but not re-run; this is an evidence-format discrepancy, not a source finding.

ITEMS DELIBERATELY SKIPPED

- Device node creation: requires root; venue explicitly disallows it.
- No recursive review of report_lint or test-harness implementation: unchanged machinery and outside change boundary.
- Hook/run-all wiring: explicitly K1-f out of scope.

FOLLOW-UPS FOR D-034

- F5: bind the actual vendor sources to lock/SBOM or preserve explicit unpinned status; root pin loop is presently vacuous.
- F6: decide/reject special files and nested `.git` / submodule identity hiding.
- F7: decide whether REUSE license directories and license symlinks need first-class attribution.
- F8: atomic manifest writes.
- F9: optional roots-last-change trace signal only; no security claim from it.

NOT-DONE

- No repair was applied; all worktree source files remain untouched.
- F1/F2 need a frozen classification/scoping decision before a focused repair.
- F3 needs one focused manifest/test repair under the current contract.
- F4 must be corrected as part of the same repair/handoff because its evidence is false at the graded PIN.

GATE RECOMMENDATION: NOT-READY — F1, F2, F3, and F4 satisfy the complete blocking predicate through current production `--check`/committed evidence. Coordinator owns the final decision.
