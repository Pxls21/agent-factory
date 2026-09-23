# C1 Report -- scripts/verify_command.py (D-052, task #147)

## Premise re-measured

All measurements match the brief (2026-09-23):
- Canny clone: f2c5e53 `chore(release): 0.3.0 (#21)`
- `wc -l`: 250 src/checks.ts, 266 test/checks.test.ts
- `sha256sum` prefixes: 1d3f36a1063542ee, d5297358e03e58cc, 0ba25891a959268c
- LICENSE line 3: `Copyright (c) 2026 Kal`
- VERIFY alternatives: line 9=33 (pytest..nox), line 10=20 (tsc..webpack), line 11=25 (eslint..shellcheck), total=78
- Test tables: isVerify rows lines 49-75 (27), checks lines 80-92 (11), hides 93-108 (14), keeps 109-123 (13), override 133-136, pipefail config 238-242
- Target files do not exist
- No symbol clash: only `tests/test_laya_probe_report.py` mentions "verify_command" in a docstring

## What was built

**V:50-76** -- `VERIFY`: three compiled patterns, 78 alternatives verbatim from checks.ts:8-12, all `re.ASCII`.

**V:79-88** -- `_PRINTS_OR_INSPECTS`, `_ASKS_ONLY`, `_NEGATED`: the three deny-list patterns (checks.ts:35-42).

**V:91-97** -- `_not_a_check`: combines `_PRINTS_OR_INSPECTS`, `_ASKS_ONLY`, `_NEGATED` (checks.ts:44-45).

**V:100-108** -- `_compile_patterns(patterns)`: compiles user patterns, raises `ValueError` on invalid (our deviation from Canny's `safeRegex`).

**V:111-120** -- `executed`: strips quoted strings via `re.sub` then `#` comments (checks.ts:48-50).

**V:123-176** -- `is_verify(command, patterns=None)`: the classifier (checks.ts:58-80). Pipefail detection walks all `set` statements and takes the last. Splits on `;`/`\n` for the last segment, then on `&&`. Each part is rejected on `||`, bare `|` (unless pipefail), lone `&`, then the pipe-feeder is checked against `_not_a_check` and the pattern list.

**V:179-199** -- `with_pipefail(command, patterns=None)`: prepends `set -o pipefail &&` if it would make the command count, only when the pipe feeds `tail` (checks.ts:88-93).

**V:202-273** -- `_cli()` + `__main__` entry point: `--pattern`, `--with-pipefail`, `--` separator, exit codes 0/1/2.

**V:1-42** -- module docstring: regex-semantics choice (re.ASCII; NBSP pinned by test), deviation notice (ValueError), full MIT notice (Copyright (c) 2026 Kal), source + port line.

**T:40-101** -- `test_is_verify_27_rows`: 27-row parametrized table from checks.test.ts:49-75.

**T:107-167** -- product tables: `CHECKS` 11 items (T:107-119), `HIDES` 14 forms (T:121-136), `KEEPS` 13 forms (T:138-154), `test_hides_exit_status` and `test_keeps_exit_status` (T:159-167).

**T:174-190** -- `test_override_replaces_defaults` and `test_pipefail_with_config` from checks.test.ts:133-136 and :238-242.

**T:195-302** -- our additions: `test_leading_spaces_do_not_count` (T:195), `test_nbsp_before_help_does_not_trigger_asks_only` (T:215), `test_with_pipefail_returns_none_for_head` and `test_with_pipefail_returns_none_when_already_counts` (T:221-228), `test_invalid_pattern_raises_value_error` (T:230), `test_cli_counts` through `test_cli_with_pipefail_no_effect` (T:235-302).

273 lines in V, 283 lines in T at the lane's hand-back (302 after the coordinator's landing touch added two rows; VERIFY-C1 F7). Standard library only; no imports from `src/` or `sandbox-kit/`.

## RED then GREEN

**RED** (stub returning `False`/`None` for everything): 23 failed, 20 passed in 0.27s. The 20 passes are all False-expected rows from the 27-row table, False-expected product-table entries, and negative-control additions (leading spaces, head, already-counts, invalid-pattern).

**GREEN run 1**: 43 passed in 0.27s.
**GREEN run 2**: 43 passed in 0.27s (deterministic).

## Mutant table

| ID | Mutation | Compiles | Collected | Killed by | Notes |
|----|----------|----------|-----------|-----------|-------|
| M1 | Quoted-string `re.sub` dropped from `executed` (V:117) | yes | 43 | **SURVIVED** | Not equivalent: `true "pytest"` returns True under M1 vs False in original. All 27-row cases with quoted strings (`git commit -m "..."`) are masked by `_PRINTS_OR_INSPECTS` (`git` in the deny list). |
| M2 | Comment `re.sub` dropped from `executed` (V:119) | yes | 43 | `test_is_verify_27_rows[comment_hides]` | 1 failed, 42 passed |
| M3 | `pipefail` always False, `re.finditer` loop removed (V:138-142) | yes | 43 | `test_is_verify_27_rows[piped_with_pipefail]` | 6 failed, 37 passed |
| M4 | `pipefail` from FIRST `m.group(1)` instead of last (V:142 + break) | yes | 43 | `test_is_verify_27_rows[pipefail_off_then_on_off]` | 2 failed, 41 passed |
| M5 | `"||" in part` check dropped (V:157-158) | yes | 43 | **SURVIVED** | Not equivalent: `set -o pipefail; pnpm test || true` returns True under M5 vs False in original. Without `pipefail`, `||` is caught by the `"|" in part` check (V:159). No test combines `||` with pipefail on. |
| M6 | Lone-`&` `re.search` dropped (V:163-164) | yes | 43 | `test_is_verify_27_rows[backgrounded]` | 2 failed, 41 passed |
| M7 | `_NEGATED` dropped from `_not_a_check` (V:96) | yes | 43 | `test_is_verify_27_rows[negated]` | 1 failed, 42 passed |
| M8 | `_ASKS_ONLY` dropped from `_not_a_check` (V:95) | yes | 43 | `test_is_verify_27_rows[tsc_version]` | 2 failed, 41 passed |
| M9 | `\s*` dropped from `_PRINTS_OR_INSPECTS` (V:80) | yes | 43 | **EQUIVALENT** | the caller strips first: `check` gets `.strip()` at V:166, so leading whitespace never reaches the pattern. |
| M10 | `with_pipefail` tail-only `re.search` dropped (V:197) | yes | 43 | `test_with_pipefail_returns_none_for_head` | 1 failed, 42 passed |
| M11 | `user_re` `any()` also checks `VERIFY` (V:169-174) | yes | 43 | `test_override_replaces_defaults` | 1 failed, 42 passed |

**Summary**: 11 mutants. 8 killed, 1 equivalent, 2 survived (not equivalent).

## Gates

**pytest (run 1)**:
```
43 passed in 0.27s
```

**pytest (run 2)**:
```
43 passed in 0.27s
```

**pyflakes**:
```
(clean -- no output)
```

**ap_screen (module)**:
```
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---
```

**ap_screen (tests)**:
```
--- TEST_SCREEN over 1 path(s): 0 hits over 1 files ---
```

**no_laya_in_gates**:
```
no_laya_in_gates: 38 files scanned, clean
```

**report_lint**: the lane's run read `39 refs -- OK 37, NEAR 1, MISS 1` (the M9 row's two refs); the coordinator reworded that row at landing; the re-run, pasted by VERIFY-C1 (F7) and again by the coordinator on 2026-09-23, is unchanged: `39 refs — OK 37, NEAR 1, MISS 1, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.

## DISCREPANCIES

1. **`safeRegex` replaced by `ValueError`** (contract item 3, deliberate). Canny silently converts an invalid configured pattern to "never matches" (checks.ts:16-27). Our port raises `ValueError` naming the bad pattern. Stated in the module docstring (V:14-16) and tested (T:230-232).

2. **`re.ASCII` instead of Unicode-aware `\s`** (contract item 2, deliberate). JS `\s` without the `u` flag matches Unicode spaces (NBSP, U+2028); Python `\s` under `re.ASCII` does not. Since bash does not word-split on NBSP, the ASCII behavior is correct. Stated in the module docstring (V:7-12), pinned by test (T:215-220).

3. **No `Config` type.** Canny passes a `Config` object with a `.verify` field; our port uses `patterns: Optional[List[str]]` directly. This is a surface-level simplification with identical behavior.

4. **No `safeRegex` caching.** Canny memoizes compiled regexes in a `Map`; our port compiles on each call. Acceptable for the classifier's use case (called once per command).

## NOT-done

1. **M1 and M5 survived mutation testing.** Neither is equivalent. M1 needs a test case where a check name appears inside quotes AND the first word is NOT in PRINTS_OR_INSPECTS (e.g. `true "pytest"` -> False). M5 needs a case combining `||` with pipefail on (e.g. `set -o pipefail; pnpm test || true` -> False). Both gaps exist in Canny's own test suite too. C2 or a follow-up should add these rows.

2. **C2 consumption.** This module is ready for C2 (task #148) to import `is_verify` and `with_pipefail` for the lane done-gate. C2 is a separate lane.

## Coordinator touch at landing (2026-09-23)

1. **The tests found the script through the working directory.** `SCRIPT` and every CLI subprocess used the relative path
   `scripts/verify_command.py`, so the suite failed to collect when pytest ran outside the repository root (run from `/tmp`:
   `1 error in 0.11s`, `FileNotFoundError`). The path is now resolved from the test file (`pathlib.Path(__file__)`).
2. **M1 and M5 now die.** Two rows added under "Our additions": `set -o pipefail; pnpm test || true` is not a check (kills
   M5: without pipefail the pipe rule already refuses `||`, so only a pipefail command reaches the `||` rule), and
   `python -c "import pytest"` / `true 'npm test'` are not checks (kills M1: quote removal matters only when the first word
   is not a print or inspect command). Each mutant, applied to a scratch copy: `1 failed, 44 passed`, the failure being the
   new test named for it.
3. **The report's test line numbers** were remapped to the edited file; the M9 row was reworded for the lint (its remaining
   MISS is the lint pairing that row's words with its second reference; the cited line is right). Three lint rounds, then stopped.

Gates after the touch: `45 passed in 0.28s` and `45 passed in 0.25s` from the repository root; `45 passed in 0.25s` from
`/tmp`; pyflakes clean.
