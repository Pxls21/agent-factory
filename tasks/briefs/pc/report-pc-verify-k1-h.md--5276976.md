`report-draft.md` was never created (the `cat >>` target from earlier turns didn't resolve) — no loss: the finished report is at the brief's canonical path `tasks/briefs/kit-k1-support/VERIFY-K1-h-report.md` (37,708 bytes, lint clean: OK 36 / MISS 0 / UNCHECKABLE 0). `downloaded_files/` is an empty dispatcher artifact, not mine. Scratch `~/tmp-vk1h/` is removed. Lane tree is clean apart from the new report file.

---

# VERIFY-K1-h — final report (adversarial-verifier, lane pc-verify-k1-h)

**GATE RECOMMENDATION: `MERGE-READY-WITH-FOLLOWUPS`** — no qualifying blockers; 3 real follow-ups (none a K1-h defect). The coordinator owns the gate; this is a RECOMMENDATION, not a verdict.

**Report file:** `/home/rocco/agent-factory/.lanes/pc-verify-k1-h.md--5276976/tree/tasks/briefs/kit-k1-support/VERIFY-K1-h-report.md` (235 lines; `report_lint.py --min-refs 15` → **OK 36, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0**).

## What I reproduced (all 7 brief items, real production path, scratch copies only)

- **Item 1 (PREMISE).** Re-measured at PIN 52769767: all 7 blob ids, the `--check` PASS, test count 41, set-id `21e700b8344c`, and all 10 class counts (2957/15/12/47/20/19/13/4/12/2) match the brief's premise block exactly. **No mismatch that changes an item.**
- **Item 2 (copy rule).** 5 cases reproduced in a fresh scratch clone: (a) same-name/diff-bytes → first-party; (b) byte-identical/diff-name → `copy:`; (c-empty) empty blob (sha1 5ba93c9db0cf) → **single-root** `copy:council` (NOT ambiguous); (c-two-root) a blob under two kit roots → **the named `ambiguous` refusal**, rc=1, fires in both `--check` and `--write` (via `build_manifest_data`, M:855) and in the pre-commit/pre-push hooks (both call `--check`). (d) upstream-kit-edit → copy flips to first-party. **The ambiguity refusal is the contract's intent, not a DoS** — it requires a deliberate two-root duplicate.
- **Item 3 (declared sets).** 12-case matrix (all 5 brief cases + 7 extra): every case causes `--check` rc=1. The pin/source verification is a **hard refusal** (`FAIL: manifest: provenance mismatch: aegis pin` / `aegis source`); extra/deleted members are caught by **count drift** (the V row's count changes). **No silent outcomes.**
- **Item 4 (12 first-party files).** Searched all 1077 `sandbox-kit/` files for each. **0 byte-identical matches** (correctly first-party). **4 near-identical** (2-8 line diffs, 96-98% overlap) — all to `llm-wiki-compiler` kit files, the only diff being the path prefix (`${CLAUDE_PLUGIN_ROOT}` → absolute install path). **Path-localized copies the blob-identity rule cannot see.** The K1-h report lists these as first-party without that caveat.
- **Item 5 (merge).** 35 test functions at 74aa8c5 → 41 at the PIN. The 6 new K1-h tests are present; **0 tests lost** (`comm -23` of the name sets is empty). Regenerated C and V in a scratch copy: **C byte-identical** (3102 lines: 1 header + 3101 data paths); V's only diff is the 2-line cosmetic generation header (`c63a3a9`, rewritten by `push_clean` to 52769767; `--check` normalizes it via `normalize_generated_time`, M:1123). The counts 2957/15/12 are **regenerated, not hand-copied**. Re-ran the lane's mutants m1/m2/m3/m5 on the merged bytes: m1 (4 killed), m2 (6 killed), m3 (5 killed; ambiguous survived — m3 doesn't touch the copy rule), m5 (2 killed). **m4 is a genuine no-op** (51/51) — as the brief anticipated (B:66-67: no set file is a kit-root copy).
- **Item 6 (new mutants).** 6 new mutants (v-A, v-B, v-C, v-D, v1, v4; never the lane's m1-m5), each compiled (AF-AP-78) with the killing test run on the UNMUTATED copy first (AF-AP-138). **v-A** (copy rule → first-party): 9 killed. **v-B** (ambiguity refusal removed): 1 killed (the ambiguous test). **v-C** (provenance raises removed): 1 killed (pin-removed); aegis-file **survived** (it depends on the set-prefix match, not the provenance verification). **v-D** (malformed-row refusal swallowed): **SURVIVOR — 51/51 pass**. **v1** (blob index bypassed): 10 killed. **v4** (parse_classes no-op): **SURVIVOR — 51/51 pass**. The `parse_classes` guard **IS live in production** (direct probe: hand-malformed C → `--check` rc=1, `FAIL: .claude class file parse failure at line 2`) — it is just **not covered by a committed test**.
- **Item 7 (gates).** `pytest -n 8` ×2: `51 passed in 9.80s` / `51 passed in 10.27s` (deterministic, rc=0 both). `set-id` → `1 files set=21e700b8344c` (matches the brief's premise). `--check` on the lane worktree → `PASS: matches 9 vendored roots` (rc=0). `pyflakes` on M+T → clean (0 hits). `no_laya_in_gates` → `40 files scanned, clean`.

## Finding inventory (no severity filter; the 8 findings in the report file, summary)

| # | class | finding | blocking? |
|---|---|---|---|
| 1 | **FOLLOW-UP** | `parse_classes` (M:574-587) has **no committed test** — the malformed-row refusal is a **SURVIVOR** (v-D, v4 both pass 51/51). The guard is live in production (confirmed: malformed C → `--check` rc=1), but no committed test exercises it. | No (contract doesn't require a parse_classes test; no material effect — the guard works, a committed C is well-formed) |
| 2 | **FOLLOW-UP** | 4 of the 12 first-party files are **path-localized copies** of `llm-wiki-compiler` kit files (2-8 line diffs, all path prefix). The blob-identity rule cannot see them (a known design constraint, not a K1-h defect). The K1-h report lists them first-party without the caveat. | No |
| 3 | INFO | The K1-h report's "after" class column (2958/14) is **stale at the PIN** (2957/15). B10 (8d8c97e7, D-054) landed between the build base (74aa8c5) and the merge, moving `agents/code-implementer.md` from kit-verbatim → kit-adapted. Report inaccuracy, not a code defect. | No |
| 4 | INFO | The brief's item-2c "empty file → ambiguous" premise **conflates two cases**: an empty file is a single-root copy (not ambiguous); only a two-or-more-root blob is. | No (contract B:34-36 is correct; the brief's description is imprecise) |
| 5 | INFO | v-C survives the aegis-file test (it depends on the set-prefix match, not the provenance verification — independent mechanisms, each tested). | No |
| 6 | INFO | The `--write` message "3102 paths" vs the K1-h report's "3101 paths" — both correct (header vs data rows); cosmetic. | No |
| 7 | INFO | The committed V's generation header names `c63a3a9` (not an object in the pushed history — it was the build lane's local head, rewritten by `push_clean`). Cosmetic; `--check` normalizes it. | No |
| 8 | INFO | The K1-h report is a PROPOSAL, not a verdict; its NOT-done is accurate. | No |

## DISCREPANCIES (the 5 in the report file)

1. **Item-2c "empty file → ambiguous" is imprecise** — an empty file is a single-root copy, not ambiguous. (Not a K1-h defect.)
2. **The K1-h report's "after" column (2958/14) is stale at the PIN (2957/15)** — B10/D-054 moved `agents/code-implementer.md`. (Not a K1-h defect.)
3. **The `--write` "3102 paths" vs R:118 "3101 paths"** — both correct (header vs data). (Cosmetic.)
4. **The v-A/v-B/v-C "COLLECTION-BROKEN" flag is a FALSE POSITIVE** — the heuristic matches "error" in normal pytest output; all 4 mutants ran the full 51-test suite.
5. **The V generation header names `c63a3a9`** (not in the pushed history) — cosmetic; `--check` normalizes it.

## NOT-done (per the report file)

- **Independent re-derivation of every K1-h report claim** beyond the boundary (M/T/V/C) — the report is an INPUT to attack, not part of the boundary; I verified its load-bearing claims (counts, mutants, merge) but did not re-derive the "before" class table line-by-line.
- **The `.agents/` mirrors** (out of scope — not a declared root).
- **A path-localization-aware copy rule** (a new capability, not a K1-h requirement; the blob-identity rule is the frozen contract and works as designed).
- **A committed test for `parse_classes`** (a FOLLOW-UP, finding 1; the guard is live in production but untested).
- **Fixing the 4 path-localized files** (the brief forbids: "report it as a finding with the diff size, never fix it").

**Retro:** nothing to bake. The two survivors (v-D, v4) share one root cause (no committed test for `parse_classes`) — that is the finding, already registered. The item-2c conflation is a brief-description imprecision, not a mechanism I need to re-learn. No new anti-pattern class.

**The gate is the coordinator's.** This is a RECOMMENDATION, not a verdict. The frozen contract (pc-k1-h.md B:31-58) survives a serious attempt at falsification; the follow-ups are real but none is a K1-h blocker.
