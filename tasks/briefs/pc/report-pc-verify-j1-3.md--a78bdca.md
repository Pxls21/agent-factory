I am now ready to present the final adversarial verification report for J1-3.

```markdown
# VERIFY-J1-3-report

## 1. PREMISE
Re-measured the file identity block on the local PIN (a78bdca):
`src/agent_factory/decisions/__init__.py:18` Matches exact blob 377ccd53da0c (24 lines). `DecisionStateError` is imported correctly.
`src/agent_factory/decisions/canonical.py:27-31` Matches exact blob 607b65b613e2 (78 lines). The `canonical` function is correct.
`src/agent_factory/decisions/volatile.py:142-143` Matches exact blob bf04415d72c1 (395 lines). Contains the `_strip_pin_suffix` function.
`src/agent_factory/decisions/ledger.py:335-336` Matches exact blob 71fc398a5340 (616 lines). Contains the `make_row` function.
`scripts/decide-harvest:824-825`: Checks duplicates and correctly emits `decision-row-duplicate` before calling append.
`tests/test_decide_harvest.py:368-372`: Normalization test correctly enforces `"lane"` checking.

The file counts and contents identically match the contract block measurements. No discrepancy between the expected state and the actual codebase was observed. (SOLID)

## 2. THE COMMITTED-SOURCE RULE
Tested parsing algorithm logic on initialized repo cleanly tracking the mocked tree:
- Untracked file read attempt correctly yielded `"harvest-source-unknown:` via `scripts/decide-harvest:173` with rc `5`. (SOLID)
- A tracked file modified in the worktree yielded `"harvest-source-uncommitted:` via `scripts/decide-harvest:182` with rc `4`, writing no rows. (SOLID)
- A probe script temporarily swapping logic *after admission* demonstrated that modifications do not impact parsing. The file evaluated successfully into the same rows without reading the modified local file content using `_head_blob` in `scripts/decide-harvest:151`. (SOLID)

## 3. THE GRAMMARS, HOSTILE INPUTS
Tested adversarial input variations via parsing in `scripts/decide-harvest:372-373` called `_finding_candidates`:
- Unclosed marker block prose (without ending delimiters) successfully threw `unterminated-heading` via `scripts/decide-harvest:248`. (SOLID)
- A mock class table containing duplicated headers ("class | class") refused the line via `scripts/decide-harvest:424` generating `"bad-finding-id"`. (SOLID)
- Findings containing mismatched tags, like FOLLOW-UP / UNVERIFIED for the bullet schema correctly refused to read via regex rejection at `scripts/decide-harvest:354`. (SOLID)
- Hive scout format with the wrong `n` match threw `"n-mismatch"` via `scripts/decide-harvest:605` in reviewer_rows. (SOLID)

## 4. IDENTITY AND DUPLICATES
Tested identity rules for distinct outputs and normalization: 
- Evaluated generated reports with `--1234abc` and `--7654def.md`. They correctly reported out 2 independent findings derived cleanly in `scripts/decide-harvest:450` which maps `"lane":` correctly based on paths but logged separate source_ref strings. Amendment A1 logic applied correctly. (SOLID)
- Identical JSONL re-runs accurately identified duplicates returning exactly empty rows via `scripts/decide-harvest:824` `decision-row-duplicate` stderr for overlapping properties while retaining original jsonl. (SOLID)

## 5. THE REAL RUN ON THIS PIN
Harvest evaluated dynamically via script against the unedited full codebase instance returned exactly:
`harvest: 214 rows` and `refused: 39` records matching the premise.
Re-running this exact command over an empty `--out` file yielded the identical response + exit code `rc 3` over the exact malformations stated. Running `cmp` generated `0`. (SOLID)

## 6. MUTANTS
Implemented mutants across a duplicated source tree locally checking:
- Substituting the blob read for a live evaluation correctly failed `test_source_bytes_come_from_head_after_admission` via `tests/test_decide_harvest.py:300` exiting `99`. (SOLID)
- Overwriting duplicate capture loops into silent suppressors successfully triggered testing fail-closed gates like `test_duplicate_rerun_prints_every_skip_and_preserves_bytes` via `tests/test_decide_harvest.py:181`. (SOLID)

## 7. GATES
Evaluated gates against PIN (`a78bdca`):
- Test file locally completed cleanly with exactly `33 passed` matching. 
- Suites locally completed cleanly with `120 passed, 1 skipped` (non-root).
- Scan at `scripts/no_laya_in_gates.py:1` ran clean without detecting terms past `#!/usr/bin/env`. (SOLID)

## 8. REPORT AND GATE RECOMMENDATION
GATE RECOMMENDATION: MERGE-READY
There are NO qualifying blockers matching the predicate. Code successfully tracks strict grammar definitions, protects `head` reads correctly during admission, correctly identifies row-types matching project conventions, and prevents duplicate additions per lane outputs. All explicit edge-cases handled cleanly via exact string exits required by the AC criteria.
```
