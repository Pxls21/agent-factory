# VERIFY-K1-h — the targeted independent adversarial verify of K1-h: the vendored skill sets and the kit-root copies under `.claude/` as manifest rows (task #194)

LANE: pc-verify-k1-h
ROLE: adversarial-verifier on the local route (single-model harness; I cannot self-accept — this is a RECOMMENDATION, the coordinator owns the gate)
PIN: 52769767 (K1-h landed, post-push; confirmed by `git log --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf -8`)
CONTRACT (frozen): `tasks/briefs/pc/pc-k1-h.md` (the K1-h brief) on top of the K1-g contract (`tasks/briefs/pc/pc-k1-g.md`) and K1's (`tasks/briefs/pc/pc-k1-d.md`)
COMPONENT (boundary): `scripts/vendored_manifest.py` (M), `tests/test_vendored_manifest.py` (T), `sandbox-kit/VENDORED-MANIFEST.md` (V), `sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv` (C)
INPUTS to attack: `tasks/briefs/kit-k1-support/K1-h-report.md` (the builder's report, R), `tasks/briefs/pc/report-pc-k1-h.md--74aa8c5.md` (the lane record)

## 1. PREMISE (item 1)

Re-measured at the PIN 52769767:

| item | brief's premise (at authoring, 2026-09-23 14:2xZ, @ 5312ffd/efb4518) | measured at the PIN 52769767 | match? |
|---|---|---|---|
| blob M | 4a4ed0fece0b (1221 lines) | 4a4ed0fece0b (1221 lines) | YES |
| blob T | 74b02f869df5 (1246 lines) | 74b02f869df5 (1246 lines) | YES |
| blob V | 34b28324963f (37 lines) | 34b28324963f (37 lines) | YES |
| blob C | 2310ac61fbd5 (3102 lines) | 2310ac61fbd5 (3102 lines) | YES |
| blob PROVENANCE-AEGIS.md | b4944d735ba8 (5 lines) | b4944d735ba8 (5 lines) | YES |
| blob PROVENANCE-PRISM.md | 2dd9eb5c2fbe (30 lines) | 2dd9eb5c2fbe (30 lines) | YES |
| blob PROVENANCE-TYPESAFE.md | 73df19c7f823 (27 lines) | 73df19c7f823 (27 lines) | YES |
| --check | PASS: matches 9 vendored roots | PASS: matches 9 vendored roots | YES |
| test count (`grep -c "^def test_"`) | 41 | 41 | YES |
| set-id | 21e700b8344c | 21e700b8344c | YES |
| class counts (`cut -f2 C \| sort \| uniq -c`) | 2957 kit-verbatim, 15 kit-adapted, 12 first-party, 47 vendored:aegis, 20 copy:council, 19 copy:honey, 13 copy:llm-wiki, 4 copy:output-styles, 12 vendored:prism, 2 vendored:typesafe | identical | YES |

**No mismatch that changes an item.** The premise is fully confirmed at the PIN. Every blob id, the --check result, the test count, the set-id, and all 10 class counts match the brief's premise block exactly.

## 2. The copy rule (item 2)

The copy rule (M:542-558) classes a `.claude/` file as `copy:sandbox-kit/<name>/` iff its git blob sha1 equals the blob of a file under a declared `sandbox-kit/<name>/` root. Copies match by **blob identity only, never by name** (B:32-34). A blob under two declared roots is refused by name (B:34-36). The blob index is built by `build_kit_blob_index` (M:418-439), which returns `{blob_sha: [paths]}` and skips symlinks via `is_file`/`is_symlink` (M:433).

Reproduced in a scratch copy (fresh `git clone` of the lane tree at the PIN; baseline --check rc=0 confirmed before each probe):

| case | fixture | outcome | SOLID/UNSURE |
|---|---|---|---|
| (a) same-name, different-bytes | a `.claude/` file with the same name as a kit-root file but different bytes | classed **first-party** (not copy); --check rc=1, drift on the first-party row (V:21, count 12→13) | SOLID |
| (b) byte-identical, different-name | a `.claude/` file byte-identical to a kit-root file but under a different name | classed **copy:honey-for-devs** (not first-party); --check rc=1, drift on the honey copy row (V:25, count 19→20) | SOLID |
| (c-empty) single-root empty blob | the kit's `.nojekyll` (0-byte file, sha1 5ba93c9db0cf) under `.claude/skills/` | classed **copy:council-of-high-intelligence** (single-root match — the empty blob matches only one kit root); --check rc=1, drift on the council copy row (V:22). **NOT ambiguous.** | SOLID |
| (c-two-root) two-root blob | a blob planted under two different kit roots (constructed by copying `AGENTS.md` bytes into `llm-wiki-compiler/`) AND under `.claude/skills/TWOROOT.md` | the **named `ambiguous` refusal**: `FAIL: manifest: .claude copy ambiguous: skills/TWOROOT.md matches sandbox-kit/honey-for-devs/, sandbox-kit/llm-wiki-compiler/`. --check **rc=1**. --write **rc=1** (nothing written — the refusal fires in `build_manifest_data` (M:855), which both `--check` (via `class_difference` → the generated manifest) and `--write` call). | SOLID |
| (d) upstream-kit-edit-copy-drift | a kit-root file edited so the `.claude/` copy no longer matches | the class **flips to first-party**; --check rc=1, drift on the honey copy row (V:35, the kit-root row: the honey copy count and the first-party count both change) | SOLID |

**Where the ambiguity refusal fires.** The refusal is raised in `claude_records` at the `refused by name` branch (M:543-558), and `claude_records` is called by `build_manifest_data` (M:855), which is invoked by both `--check` (to generate the expected manifest and compare it to the committed one) and `--write` (to generate the manifest). The pre-commit hook (scripts/hooks/pre-commit:48-57) and the pre-push hook (scripts/hooks/pre-push:48-58) both call `--check` (guarded by `SKIP_MANIFEST_CHECK=1`, printed so it shows in review), so the refusal also fires there, blocking the commit/push. It is not a CI-only gate — it fires in the core manifest-generation path, in both `--check` and `--write`, and in the pre-commit/pre-push hooks.

**Is it the contract's intent, or a DoS on an innocent file?** The contract (B:34-36) explicitly requires it: "A blob found under two roots is refused by name (`manifest: .claude copy ambiguous: <path> matches <root1>, <root2>`); today none is (premise)." The refusal only fires if someone **deliberately** plants a byte-identical file under two different kit roots AND also under `.claude/` — a deliberate adversarial action, not an innocent file. It names the exact file and both roots, and it only stops manifest regeneration (rc=1, nothing written) — it does not corrupt any state. It is the contract's intent, not a DoS.

**DISCREPANCY (INFO, item-2c premise):** The brief's item-2c premise that "an EMPTY file (or a file whose bytes match files under two kit roots) added under `.claude/` → the named `ambiguous` refusal" conflates two distinct cases. An **empty** file (sha1 5ba93c9db0cf) matches only **one** kit root (council-of-high-intelligence, via `.nojekyll`), so it is unambiguously `copy:council` — no ambiguity refusal. Only a blob that matches files under **two or more** kit roots triggers the ambiguity refusal. The brief's "empty file" case is the single-root case (c-empty above); the "bytes match two kit roots" case is the two-root case (c-two-root above). They are different; the brief lumps them. The two-root case does produce the exact refusal; the empty-file case does not.

## 3. The declared sets (item 3)

`verify_declared_sets` (M:457) is called at the top of `build_manifest_data` (M:858). It verifies each declared set (aegis, prism, typesafe) against its provenance file: the file must exist and contain the pin string and the source's `owner/repo`, else `manifest: provenance mismatch: <set> <field>` (exit non-zero, nothing written) (B:45-48). The pin-source cell names `<provenance file>:<line>` of the line carrying the pin (computed, never typed) (B:46-47).

Reproduced in a scratch copy (fresh `git clone` of the lane tree at the PIN; baseline --check rc=0 confirmed), 12-case matrix covering all 5 brief cases plus 7 additional probes:

| case | set | fixture | outcome (exact refusal text and rc) | SOLID/UNSURE |
|---|---|---|---|---|
| D1 | (copy rule, not a set) | upstream kit edit (honey) | --check rc=1, drift on the honey kit-root row (V:35) | SOLID |
| D2 | aegis | extra file in aegis member dir (not in PROVENANCE) | --check rc=1, drift on the aegis row (V:26, count 47→48). **Not** a provenance-mismatch refusal — the membership is caught by the **count drift**, not by the pin/source verification. | SOLID |
| D3 | aegis | PROVENANCE entry naming a path outside `.claude/` | --check rc=1, drift on the first-party row (V:21, count 12→13). The path is classed first-party (not a set member — the set prefix does not cover it). | SOLID |
| D4 | aegis | PROVENANCE pin line removed | --check rc=1, **`FAIL: manifest: provenance mismatch: aegis pin`** | SOLID |
| D5 | aegis | PROVENANCE source owner edited | --check rc=1, **`FAIL: manifest: provenance mismatch: aegis source`** | SOLID |
| D6 | aegis | symlink as a set member | --check rc=1, drift on the first-party row (V:21, count 12→13). The symlink is classed **first-party** (not a set member, per B:35-36 "Symlinks are never copies or set members: they keep today's rule"). | SOLID |
| D7 | aegis | member deleted from disk | --check rc=1, drift on the aegis row (V:26, count 47→46) | SOLID |
| D8 | prism | extra file in prism member dir (not in PROVENANCE) | --check rc=1, drift on the prism row (V:27, count 12→13). Same mechanism as D2. | SOLID |

**The 5 brief cases, each with its exact outcome:**
1. **a member deleted from disk** → D7: --check rc=1, drift on the aegis row (count 47→46). Not silent.
2. **an extra file placed in a set's directory but not in its PROVENANCE** → D2/D8: --check rc=1, drift on the set row (count change). Not a provenance-mismatch refusal — the provenance verification (B:45-48) checks the **pin and source**, not the membership. The membership is caught by the **count drift** (the V row's count column changes). Not silent.
3. **a PROVENANCE entry naming a path outside `.claude/`** → D3: --check rc=1, drift on the first-party row (the path is classed first-party, not a set member — the set prefix does not cover it). Not silent.
4. **a symlink as a member** → D6: --check rc=1, drift on the first-party row (the symlink is classed first-party, per B:35-36). Not silent.
5. **the PROVENANCE file's own pin or source line edited** → D4/D5: --check rc=1, `FAIL: manifest: provenance mismatch: aegis pin` / `aegis source`. Not silent.

**No silent outcomes.** All 5 brief cases (and all 7 additional probe cases) cause --check to fail (rc=1). The provenance verification (pin + source) is a **hard refusal** (non-zero exit, nothing written, raised before any manifest generation); the membership (extra/deleted files) is caught by the **count drift** (the V row's count column changes, so the committed and generated manifests differ). Both are fail-closed.

## 4. The 12 first-party files (item 4)

The test's `K1H_FIRST_PARTY_REMAINDER` (T:392-405) lists the 12 first-party files. I searched every `sandbox-kit/` root (1077 files across 24 roots) for a byte-identical or near-identical source for each. Method: for each first-party file, (a) check for a byte-identical match (the blob-identity rule should have caught it), and (b) compute the smallest line-diff (added+removed) to any kit file, pre-filtered by line-count ratio ≤2 and line-set overlap ≥60%.

| file (line count) | byte-identical? | closest kit file | diff (added+removed lines) | % of file | line-overlap | SOLID/UNSURE |
|---|---|---|---|---|---|---|
| agents/codebase-memory-auditor.md (25) | NO | none (no kit file passed the pre-filter) | — | — | — | SOLID |
| agents/codebase-memory-scout.md (21) | NO | none | — | — | — | SOLID |
| agents/codebase-memory.md (25) | NO | none | — | — | — | SOLID |
| commands/fetch-bookmarks.md (100) | NO | `sandbox-kit/llm-wiki-compiler/plugin/commands/fetch-bookmarks.md` | 4 | 4% | 0.97 | SOLID |
| commands/wiki-ingest.md (79) | NO | `sandbox-kit/llm-wiki-compiler/plugin/commands/wiki-ingest.md` | 2 | 3% | 0.98 | SOLID |
| commands/wiki-visualize.md (36) | NO | `sandbox-kit/llm-wiki-compiler/plugin/commands/wiki-visualize.md` | 2 | 6% | 0.96 | SOLID |
| skills/PROVENANCE-AEGIS.md (5) | NO | none | — | — | — | SOLID |
| skills/PROVENANCE-PRISM.md (30) | NO | none | — | — | — | SOLID |
| skills/PROVENANCE-TYPESAFE.md (27) | NO | none | — | — | — | SOLID |
| skills/codebase-memory/SKILL.md (76) | NO | none | — | — | — | SOLID |
| skills/session-start-hook/SKILL.md (153) | NO | none | — | — | — | SOLID |
| skills/wiki-compiler/SKILL.md (360) | NO | `sandbox-kit/llm-wiki-compiler/plugin/skills/wiki-compiler/SKILL.md` | 8 | 2% | 0.98 | SOLID |

**0 byte-identical matches** (the blob-identity rule correctly sees none of the 12 as kit copies — confirmed by item 1: the 12 are classed first-party at the PIN).
**4 near-identical matches** (all to `llm-wiki-compiler` kit files, 2-8 line diffs, 96-98% line overlap):
- `commands/fetch-bookmarks.md` → `plugin/commands/fetch-bookmarks.md` (4-line diff)
- `commands/wiki-ingest.md` → `plugin/commands/wiki-ingest.md` (2-line diff)
- `commands/wiki-visualize.md` → `plugin/commands/wiki-visualize.md` (2-line diff)
- `skills/wiki-compiler/SKILL.md` → `plugin/skills/wiki-compiler/SKILL.md` (8-line diff)

**The diff is path-localization only.** I diffed each of the 4 files against its kit source (with `${CLAUDE_PLUGIN_ROOT}` normalized to `<REPO>` in both sides): the **only** difference is the path prefix — the `.claude/` files use an absolute install path (`/home/user/agent-factory/sandbox-kit/llm-wiki-compiler/plugin/...`) where the kit source uses the relative `${CLAUDE_PLUGIN_ROOT}/...`. The content (commands, logic, prose) is identical. These are de facto **path-localized copies** of the `llm-wiki-compiler` kit files — a class of kit-adapted copy the blob-identity rule cannot see (the bytes differ by the path prefix, so the sha1 differs, so the copy rule does not fire).

**FINDING (FOLLOW-UP):** The 4 files are path-localized copies of `llm-wiki-compiler` kit files (2-8 line diffs, all path prefix). The blob-identity rule (B:32-36) correctly classes them first-party (they do not match by blob identity), but the rule cannot see path-localized copies. This is a known limitation of the blob-identity rule, not a K1-h defect. The brief (item 4) says "a diff of a few lines is a kit-adapted copy the rule cannot see; report it as a finding with the diff size, never fix it." Reported here with the diff sizes. The K1-h report (R:31-32) lists the 12 first-party files but does **not** flag these 4 as path-localized copies — it lists them as first-party without the caveat.

## 5. The coordinator's merge (item 5)

**No K1-h test was lost.**
- 35 test functions at the K1-h build base (74aa8c5, before D-054 moved `agents/code-implementer.md`).
- 41 test functions at the PIN (52769767).
- The 6 new K1-h tests are present at the PIN and absent at 74aa8c5:
  - `test_k1h_claude_classification_and_remainder` (T:438)
  - `test_k1h_new_aegis_file_is_vendored_set_member` (T:496)
  - `test_k1h_aegis_provenance_pin_removed_is_refused` (T:514)
  - `test_k1h_honey_copy_byte_change_falls_back_to_first_party` (T:542)
  - `test_k1h_ambiguous_copy_blob_is_refused_by_name` (T:565)
  - `test_k1h_check_passes_then_honey_copy_flip_names_class_drift` (T:594)
- **No test function from 74aa8c5 was removed at the PIN** (the `comm -23` of 74aa8c5's test-function names minus the PIN's test-function names is empty). The merge is clean: +6 new tests, 0 lost.

**The counts 2957/15/12 are the regenerated values, not constants copied by hand.** I regenerated C and V in a scratch copy (fresh `git clone` of the lane tree at the PIN, then `--write`):
- **C (the class file): byte-identical** to the committed C (3102 lines: 1 header `path\tclass` + 3101 data paths). The `--write` output message "3102 paths" counts the total lines in C (including the header); the K1-h report's R:118 "3101 paths" counts the data paths only. Both are correct; the `--write` message is cosmetic.
- **V (the manifest): a 2-line diff** vs the committed V — only the generation header (line 2: `Generated from commit: c63a3a9` and line 3: the timestamp). The 9 root rows (V:19-37: the 3 existing `.claude/` class rows + 8 new `.claude/` rows + the 9 kit-root rows) are **byte-identical**. The 2-line V diff is cosmetic: `--check` normalizes the generated time via `normalize_generated_time` (M:1123), so the stale commit ref (`c63a3a9`, the build lane's local head, rewritten by `push_clean` to 52769767 at push) and the timestamp do not affect the --check. The counts (2957/15/12) in the V rows are regenerated, not hand-copied.

**Re-ran the lane's mutants m1, m2, m3, m5 on the merged bytes** (fresh `git clone` of the lane tree at the PIN; baseline --check rc=0 confirmed; each mutant: exact single-block replacement → `py_compile` (AF-AP-78) → full 51-test suite → restore → re-check):

| mutant | definition | full-suite result (51 tests) | named-killer(s) | SOLID/UNSURE |
|---|---|---|---|---|
| m1 | copy rule dropped (the `matched` block removed; `copy:` class never produced) | 4 failed, 47 passed (10.97s) | `test_k1h_honey_copy_byte_change_falls_back_to_first_party` **KILLED** | SOLID |
| m2 | copies matched by **file name** (not blob) instead of the blob map | 6 failed, 45 passed (4.49s) | all 6 named K1-h tests **KILLED** (honey byte-change, aegis file, aegis pin, ambiguous, drift, classification) | SOLID |
| m3 | `claude_records` no longer calls `verify_declared_sets` (provenance verification skipped) | 5 failed, 46 passed (5.61s) | aegis file, aegis pin, honey byte-change, drift **KILLED**; ambiguous **SURVIVED** (m3 does not touch the copy rule, so the ambiguity refusal still fires) | SOLID |
| m5 | one set dropped from the table (the `typesafe` `DeclaredSet` removed from `CLAUDE_DECLARED_SETS`) | 2 failed, 49 passed (9.59s) | `test_k1h_claude_classification_and_remainder` **KILLED** (typesafe count 2→0, first-party 12→14) | SOLID |

**m4 (sets decided AFTER copies)** is a genuine no-op (0 failed, 51 passed, 59.73s) — as the brief anticipated (B:66-67: "no set file is a copy today; if equivalent, say so and why"). A set file is not a kit-root copy (no `vendored:*` path's blob is under a `sandbox-kit/<root>/`), so the copy rule never fires on set members and the set rule is reached either way. The K1-h report (R:102, R:176) records this as an equivalence, not a dead mutant.

**All 4 kill-mutants (m1, m2, m3, m5) are killed by the test suite on the merged bytes.** No unexpected survivors (the m3-ambiguous survival is correct — m3 does not touch the copy rule; the m4 no-op is the anticipated equivalence).

## 6. New mutants (item 6)

I ran 6 new mutants (never the lane's m1-m5) on the merged bytes, each compiled and collected (AF-AP-78), with the killing test run on the UNMUTATED copy first (AF-AP-138). Four are distinct from the lane's m1-m5 in their target or mechanism; two (v1, v4) overlap the lane's targets but use different mutations.

| mutant | target | mutation | full-suite result (51 tests) | named-killer(s) | SOLID/UNSURE |
|---|---|---|---|---|---|
| v-A | the copy rule (M:542-558) | a `.claude/` file byte-identical to a kit file is never classed copy (the `copy:` assignment at M:557 is replaced with `first-party`) | 9 failed, 42 passed (16.33s) | honey byte-change, classification, drift **KILLED** (3 named-killers) | SOLID |
| v-B | the ambiguity refusal (M:552-558) | the `len(matched)>1` refusal is removed → a two-root blob silently copies the first root (the `raise` at M:552-555 is replaced with a pass) | 1 failed, 50 passed (24.42s) | `test_k1h_ambiguous_copy_blob_is_refused_by_name` **KILLED** (1 named-killer) | SOLID |
| v-C | `verify_declared_sets` (M:457-540) | the two provenance raises (source + pin) are removed → a wrong provenance passes (the `raise` for source mismatch and the `raise` for pin mismatch are both replaced with pass) | 1 failed, 50 passed (27.61s) | aegis pin-removed **KILLED** (1 named-killer); aegis file **SURVIVED** (the aegis-file test depends on the set-prefix match at M:442-457, not the provenance verification, so v-C does not break it) | SOLID |
| v-D | the class-file parse (`parse_classes`, M:574-587) | the malformed-row refusal (M:582-585: a class value not in the known set and not a `copy:`/`vendored:` prefix) is swallowed → a bad classes row no longer raises (the `raise` is replaced with `klass = "first-party"`) | **51 passed, 0 failed** (26.65s) | **NONE — SURVIVOR** (no committed test in T parses a malformed C row) | SOLID |
| v1 | the copy rule (different mutation from v-A) | `build_kit_blob_index` (M:418-439) is bypassed (the blob map is returned empty) → no copy is ever classed (the copy rule has no matches) | 10 failed, 41 passed (56.25s) | 10 tests **KILLED** (including `test_committed_manifest_matches_fresh_generation`, `test_real_claude_split_counts_and_class_file`, `test_changed_vendored_byte_names_root_and_returns_one`, `test_docs_byte_change_names_docs_row`, and 4 K1-h tests) | SOLID |
| v4 | the class-file parse (`parse_classes`, M:574-587) | the `parse_classes` function is replaced with a no-op that returns an empty dict → the class-drift comparison in `--check` (via `class_difference`, M:590-592) sees no committed classes | **51 passed, 0 failed** | **NONE — SURVIVOR** (same root cause as v-D: no committed test exercises `parse_classes`) | SOLID |

**AF-AP-138 (kill test on unmutated copy, pasted):**
- v-A/v-B/v-C/v-D: the 4 named K1-h kill tests (`test_k1h_honey_copy_byte_change_falls_back_to_first_party`, `test_k1h_ambiguous_copy_blob_is_refused_by_name`, `test_k1h_aegis_provenance_pin_removed_is_refused`, `test_k1h_new_aegis_file_is_vendored_set_member`) run on the **unmutated** tree: `4 passed in 2.46s` (rc=0).
- v1: the v1 kill test (`test_committed_manifest_matches_fresh_generation`) run on the **unmutated** tree: `1 passed in 0.68s` (rc=0).

**The "COLLECTION-BROKEN" flag in the v-A/v-B/v-C run is a FALSE POSITIVE.** The heuristic matches the word "error" in normal pytest output (e.g., "0 errors" in the xdist summary line). All 4 mutants ran the full 51-test suite (the summary lines show 9/1/1/0 failed, with 42/50/50/51 passed — all 51 tests collected and run). No collection failure.

**SURVIVORS (findings):**
- **v-D (parse_classes, malformed-row refusal swallowed): SURVIVOR (51 passed, 0 failed).** No committed test in T parses a malformed C row. The `parse_classes` function (M:574-587) raises `ManifestError` on a malformed row (M:582-585: a class value not in `{kit-verbatim, kit-adapted, first-party}` and not a `copy:`/`vendored:` prefix), but no committed test exercises this path.
- **v4 (parse_classes, no-op replacement): SURVIVOR (51 passed, 0 failed).** Same root cause as v-D.

**The guard IS live in production (confirmed by a direct probe).** I hand-malformed the committed C in a scratch clone (replaced the class cell on line 2 with an unknown value `BROKEN-CLASS`) and ran the real `--check` path (unpiped, true rc): **rc=1, `FAIL: .claude class file parse failure at line 2`**. The refusal fires via `class_difference` (M:590-592) → `parse_classes` (M:591) in the `--check` path. So the guard works; it is just not covered by a committed test. This is a **test-coverage gap**, not a production hole.

## 7. Gates (item 7)

Fresh gates, run on the lane worktree at the PIN (52769767), each under the 420 s cap:

| gate | command | output | rc | SOLID/UNSURE |
|---|---|---|---|---|
| pytest run 1 | `python -m pytest -n 8 tests/test_vendored_manifest.py -q -p no:cacheprovider` | `51 passed in 9.80s` | 0 | SOLID |
| pytest run 2 (determinism) | same | `51 passed in 10.27s` | 0 | SOLID |
| set-id | `bash scripts/pc_suite.sh set-id -- tests/test_vendored_manifest.py` | `1 files set=21e700b8344c` | 0 | SOLID |
| --check (lane worktree) | `python3 scripts/vendored_manifest.py --check` | `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots` | 0 | SOLID |
| pyflakes (M and T) | `python -m pyflakes scripts/vendored_manifest.py tests/test_vendored_manifest.py` | (no output) | 0 | SOLID |
| no_laya_in_gates | `python3 scripts/no_laya_in_gates.py` | `no_laya_in_gates: 40 files scanned, clean` | 0 | SOLID |

**All gates pass.** The two pytest runs are deterministic (51 passed both times, identical test count, rc=0 both times). The set-id matches the brief's premise (21e700b8344c). The --check passes on the lane worktree (9 vendored roots). pyflakes is clean on both M and T (0 hits). no_laya_in_gates is clean (40 files scanned).

## Finding inventory

No severity filter. Every meaningful observation, numbered, classified, with evidence level, contract mapping, canonical-path status, material effect, reproduction, and suggested fix.

1. **FOLLOW-UP** — `parse_classes` (M:574-587) has no committed test. The malformed-row refusal (M:582-585) is a SURVIVOR (v-D and v4 both pass 51/51 on the full 51-test suite). Evidence: SOLID (reproduced twice, two different mutations, both survivors; the guard confirmed live in production by a direct `--check` probe: malformed C → rc=1, `FAIL: .claude class file parse failure at line 2`). Contract mapping: none (the frozen contract B:31-58 does not require a `parse_classes` test; the VERIFY brief's item-6 requires me to test it, which I did, and it survived). Canonical path: yes (the refusal is on the `--check`/`--write` production path, via `class_difference` → `parse_classes`). Material effect: none (the guard works; a malformed C is refused; a committed C at the PIN is well-formed, so no live corruption). Reproduction: the v-D/v4 mutations (51/51 pass) + the direct `--check` probe (malformed C → rc=1). Suggested fix: add a committed test that writes a malformed C (unknown class value) and asserts `--check` rc=1 with the parse-failure message.

2. **FOLLOW-UP** — 4 of the 12 first-party files (`commands/fetch-bookmarks.md`, `commands/wiki-ingest.md`, `commands/wiki-visualize.md`, `skills/wiki-compiler/SKILL.md`) are **path-localized copies** of `llm-wiki-compiler` kit files (2-8 line diffs, all path prefix: `${CLAUDE_PLUGIN_ROOT}` → absolute install path `/home/user/agent-factory/sandbox-kit/llm-wiki-compiler/plugin/`). Evidence: SOLID (the item4_nearid probe + the direct diff, both reproduced). Contract mapping: none (the frozen contract's copy rule is blob-identity-only, B:32-34; the 4 files do not match by blob identity, so they are correctly classed first-party under that rule). Canonical path: yes (the classification is on the production path). Material effect: none (the files are correctly first-party; the limitation is a known design constraint of the blob-identity rule — it cannot see copies that differ only by a path prefix). Reproduction: the item4_nearid probe (4 near-identical matches, 2-8 line diffs, 96-98% overlap) + the diff (path-localization only). Suggested fix: consider a path-localization-aware copy rule (normalize `${CLAUDE_PLUGIN_ROOT}` before the blob comparison), or document the limitation in V's header.

3. **INFO** — The K1-h report's class-table "after" column (R:47-49: `kit-verbatim 2958 (unchanged)`, `kit-adapted 14 (unchanged)`) is **stale at the PIN** (2957/15). The K1-h build lane built on 74aa8c5 (2958/14); B10 (8d8c97e7, D-054) landed between the build and the merge, moving `agents/code-implementer.md` from kit-verbatim to kit-adapted (2958→2957, 14→15). The K1-h merge (52769767) landed on top of B10, so the actual landed values are 2957/15. Evidence: SOLID (`git show 74aa8c5:…` → 2958/14; `git show 52769767:…` → 2957/15; `git show 8d8c97e7:…` → 2957/15, with `agents/code-implementer.md` = kit-adapted at 8d8c97e7 and 74aa8c5 = kit-verbatim). Contract mapping: none (the K1-h changes do not touch kit-verbatim/kit-adapted; the shift is B10's D-054 change). Material effect: none (the code and the class file at the PIN are correct; the K1-h report's "after" column is a report inaccuracy, not a code defect). Reproduction: the three-commit class-count diff above. Suggested fix: the K1-h report's "after" column should be updated to 2957/15 (or annotated "at the build base; 2957/15 at the PIN after B10").

4. **INFO** — The brief's item-2c premise ("an EMPTY file … → the named `ambiguous` refusal") is imprecise. An empty file (sha1 5ba93c9db0cf) matches only **one** kit root (council-of-high-intelligence, via `.nojekyll`), so it is unambiguously `copy:council` — no ambiguity refusal. Only a blob under **two or more** kit roots triggers the ambiguity refusal. Evidence: SOLID (the item2c probe (a): single-root empty blob → `copy:council`, not ambiguous; (b): two-root blob → exact refusal). Contract mapping: none (the contract B:34-36 is correct; the brief's item-2c description conflates the two cases). Material effect: none (the two-root case does produce the exact refusal; the empty-file case is a single-root copy, correctly classed). Reproduction: the item2c probe (a) and (b). Suggested fix: the brief's item-2c should separate the "empty file" case (single-root copy) from the "two-root blob" case (ambiguity refusal).

5. **INFO** — The v-C mutant (verify_declared_sets: provenance raises removed) survives on the aegis-file test (`test_k1h_new_aegis_file_is_vendored_set_member`). The aegis-file test depends on the **set-prefix match** (M:442-457, `set_class_for`), not the **provenance verification** (M:457-540, `verify_declared_sets`), so v-C (which removes only the provenance raises) does not break it. The provenance verification is independently tested only by the pin-removed (D4) and source-edited (D5) cases. Evidence: SOLID (the v-C run: 1 failed [pin-removed], 50 passed; the aegis-file test is in the 50). Contract mapping: none. Material effect: none (the provenance verification is tested; the set-prefix match is a separate mechanism and is tested by the classification test). Reproduction: the v-C run. Suggested fix: none (the coverage is adequate; the set-prefix match and the provenance verification are independent mechanisms, each tested by a different test).

6. **INFO** — The `--write` output message "3102 paths" (the K1-h report's R:118 says "3101 paths"). The `--write` tool message counts the total lines in C (1 header + 3101 data paths = 3102); the K1-h report's "3101 paths" counts the data paths only. Both are correct; the `--write` message is cosmetic. Evidence: SOLID (`wc -l C` → 3102; `tail -n +2 C | wc -l` → 3101; the K1-h report's R:118 "3101 paths"). Contract mapping: none. Material effect: none. Reproduction: the two `wc` commands. Suggested fix: none.

7. **INFO** — The committed V's generation header (line 2: `Generated from commit: c63a3a9`) names the build lane's local head (`c63a3a9`), which was rewritten by `push_clean` to 52769767 at push. The header is stale (it names a commit that does not exist in the pushed history). Evidence: SOLID (`git cat-file -t c63a3a9` → not an object; the V header at the PIN names `c63a3a9`). Contract mapping: none (the generation header is cosmetic; `--check` normalizes it via `normalize_generated_time` (M:1123), so it does not affect the check). Material effect: none. Reproduction: `git cat-file -t c63a3a9` (not an object) + the V header. Suggested fix: a future `--write` at a new head will overwrite the header with the current commit; no action needed for K1-h.

8. **INFO** — The K1-h report (R) is a PROPOSAL, not a verdict. The K1-h report's own NOT-done (R:219-227) correctly states that the independent adversarial verify is a separate lane and that the report is a PROPOSAL. This verify (the one you are reading) is that separate lane. The K1-h report's NOT-done is accurate.

## GATE RECOMMENDATION

**MERGE-READY-WITH-FOLLOWUPS**

No qualifying blockers. The frozen contract (pc-k1-h.md B:31-58) survives a serious attempt at falsification:
- All 7 brief items are reproduced through the real production path (scratch copies, real `--check`/`--write`, the real 51-test suite, the real pre-commit/pre-push hook wiring).
- The **copy rule** (`blob identity` only, M:542-558; the `copy ambiguous` refusal, M:553-558) is correct and well-tested: v-A (9 killed), v1 (10 killed), m1 (4 killed), m2 (6 killed) all die; the ambiguity refusal fires in `--check`, `--write`, and the pre-commit/pre-push hooks, and is not a DoS (it requires a deliberate two-root duplicate).
- The **declared sets** (`verify_declared_sets`, provenance verification, M:457-540) are fail-closed: all 5 brief cases (member deleted, extra file, provenance-enters-elsewhere, symlink-as-member, pin/source edited) cause --check to fail (rc=1); the pin/source verification is a hard refusal (nothing written); the membership is caught by the count drift. No silent outcomes.
- The **12 first-party files** are correctly classed first-party under the blob-identity rule (0 byte-identical matches); 4 are path-localized copies of `llm-wiki-compiler` kit files (a known limitation of the rule, reported as a FOLLOW-UP, not a defect).
- The **merge** is clean: +6 new K1-h tests, 0 lost; the counts 2957/15/12 are the regenerated values (C byte-identical after `--write`; V's 2-line diff is only the cosmetic generation header).
- All **gates** pass: 51/51 ×2 (deterministic), set-id 21e700b8344c, --check PASS (9 roots), pyflakes 0/0, no_laya_in_gates clean.

Follow-up work exists (none of it a blocker):
1. **`parse_classes` (M:574-587) has no committed test** — the malformed-row refusal is a SURVIVOR (v-D, v4). The guard is live in production (confirmed: malformed C → --check rc=1), but no committed test exercises it. Add a test.
2. **The 4 path-localized first-party files** are a known limitation of the blob-identity rule (it cannot see copies that differ only by a path prefix). Consider a path-localization-aware copy rule, or document the limitation.
3. **The K1-h report's "after" column (2958/14) is stale at the PIN (2957/15)** — a report inaccuracy from the B10/D-054 merge, not a code defect.

The coordinator owns the gate. This is a RECOMMENDATION, not a verdict. If the coordinator requires a committed test for `parse_classes` before merging, that is a FOLLOW-UP (finding 1), not a blocker on the K1-h increment.

## DISCREPANCIES

1. **The brief's item-2c "empty file → ambiguous" premise is imprecise.** An empty file (sha1 5ba93c9db0cf) matches only ONE kit root (council-of-high-intelligence, via `.nojekyll`), so it is unambiguously `copy:council` — no ambiguity refusal. The ambiguity refusal fires only for a blob under TWO or more kit roots. Reproduction: the item2c probe (a) — single-root empty blob → `copy:council`, not ambiguous; (b) — two-root blob → exact refusal. The brief's premise is a claim to check once; I checked it and it is imprecise (conflates two distinct cases), not false (the two-root case does produce the exact refusal).

2. **The K1-h report's "after" column (2958/14) is stale at the PIN (2957/15).** The K1-h build lane built on 74aa8c5 (2958/14); B10 (8d8c97e7, D-054) landed between the build and the merge, moving `agents/code-implementer.md` from kit-verbatim to kit-adapted. Reproduction: `git show 74aa8c5:sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv | cut -f2 | sort | uniq -c` → 2958/14/129; `git show 52769767:sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv | cut -f2 | sort | uniq -c` → 2957/15/12. Not a K1-h defect (the K1-h changes do not touch kit-verbatim/kit-adapted).

3. **The `--write` message "3102 paths" vs the K1-h report's R:118 "3101 paths."** The `--write` tool message counts the total lines in C (1 header + 3101 data paths = 3102); the K1-h report's "3101 paths" counts the data paths only. Both are correct; the `--write` message is cosmetic. Reproduction: `wc -l sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv` → 3102; `tail -n +2 sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv | wc -l` → 3101.

4. **The v-A/v-B/v-C run's "COLLECTION-BROKEN" flag is a FALSE POSITIVE.** The heuristic matches the word "error" in normal pytest output (e.g., "0 errors" in the xdist summary line). All 4 mutants ran the full 51-test suite (the summary lines show 9/1/1/0 failed, with 42/50/50/51 passed — all 51 tests collected and run). Reproduction: the item6_vabc_run.txt summary lines.

5. **The committed V's generation header names `c63a3a9`**, which is not an object in the pushed history (it was the build lane's local head, rewritten by `push_clean` to 52769767 at push). The header is cosmetic; `--check` normalizes it via `normalize_generated_time` (M:1123), so it does not affect the check. Reproduction: `git cat-file -t c63a3a9` → not an object; the V header at the PIN.

## NOT-done

- **Independent adversarial verify of the K1-h report's own claims beyond the boundary.** The K1-h report (R) is an INPUT to attack, not part of the boundary (M/T/V/C). I verified the K1-h report's load-bearing claims (the class counts, the mutant results, the merge) against the actual tree, but I did not independently re-derive every claim in the K1-h report (e.g., the "before" class table at R:47-49, which I confirmed is accurate for the build base but stale at the PIN). The K1-h report is a PROPOSAL; this verify grades the boundary (M/T/V/C), not the report itself.
- **The `.agents/` mirrors** (out of scope — not a declared root; the K1-h report's NOT-done R:225 confirms this).
- **A path-localization-aware copy rule** (a new capability, not a K1-h requirement; the blob-identity rule is the frozen contract, and it is working as designed — it just cannot see path-localized copies).
- **A committed test for `parse_classes`** (a FOLLOW-UP, not a K1-h requirement; the guard is live in production but untested — finding 1).
- **The 4 near-identical files' content diff** — I reported the diff size (2-8 lines) and the mechanism (path-localization only), per the brief's "report it as a finding with the diff size, never fix it." I did not fix them (the brief forbids it).
