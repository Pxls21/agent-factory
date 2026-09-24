**DONE: K170 build complete, all gates green, report landed.** The lock/SBOM/provenance parsers in `scripts/vendored_manifest.py` now fail closed (D-1 PyYAML safe loader + dup-key refusal, D-2 every refusal a `ManifestError`, D-3 no behaviour change on the real files — both digests hold).

**Files (lane tree `pc-k170.md--9e6821b/tree` at 9e6821b):**
- `M scripts/vendored_manifest.py` (+158/−56): `:29` `import yaml` · `:265` `_LINE_SEPARATORS` (chr-built) · `:268` new `_refuse_line_separators` (R1, newline-counted) · `:281` new `load_manifest_yaml` (D-1/D-2, raw-bytes read, dup-key constructor, YAML-mark line) · `:323` new `_clean_str` (R5) · `:730` `parse_provenance` (R8 refuse) · `:837` `parse_lock` (R3–R6) · `:878` `parse_sbom` (R7); `:915`/`:1255` unchanged
- `?? tests/test_vendored_manifest_parse.py` (24 tests; fresh module load per test)
- `?? tasks/briefs/kit-k1-support/K170-report.md` (the full report; a previous attempt's copy had landed OUTSIDE the boundary at the lane's parent dir — removed)
- Draft synced: `/home/rocco/agent-factory/.lanes/pc-k170.md--9e6821b/report-draft.md` (270 lines)

**Premise:** re-measured at the PIN — all four blobs match, the shapes/repro/drift outputs reproduce verbatim (item 1 of the report).

**Red (PIN code, final test file):** `20 failed, 4 passed in 0.67s` — the 4 green are the regression rows (`test_R0_real_files_unchanged`, `test_L7_lock_pin_read_as_scalar_is_a_regression_row`, `test_S5_sbom_yaml_round_trip_is_a_regression_row`, `test_X4b_lock_top_level_scalar_is_ignored_regression_row`).
**Green (changed code):** `24 passed` (0.69s / 0.67s, two runs).

**Outermost control:** at PIN `--check rc=0` (hollow green, `check_pin_diff rc=1`); after change: `FAIL: selected_core.agent-client-protocol: the value 0 is not a non-empty whitespace-free string`, `--check rc=1`, `check_pin_diff rc=1` unchanged.

**Mutations (9):** m1→`test_L4`, m2→`test_L7b`+`test_S6`, m3→`test_L5`, m4→`test_S2`, m5→`test_X1`+`test_X2`, m6→`test_P1`, m7→`test_S3`, m9→`test_R0` all killed (1 failed / 23 passed each); **m8 (SafeLoader→Loader, dup constructor kept): nothing turns red — the safe loader is unpinned by the test set**, as the brief anticipated.

**Gates:** consumer set `257 passed` (22.55s / 29.82s, set id `10334866f935` = brief's); `--check` PASS, `check_pin_diff` PASS; ap_screen: AF-AP-132 ×3 at new lines `:482/:557/:655` (the three out-of-boundary sites; in-boundary `:653/:759/:798` gone), AF-AP-25 ×0; pyflakes clean (rc=0); report_lint rc=0 (26 refs, OK 24, MISS 0, FLOOR met; 2 UNCHECKABLE reported, 3-round bound hit).

**DISCREPANCIES (4, all in report §9):**
- **L7 premise false:** PyYAML 6 (YAML 1.1) reads `1e10` as a STRING, not a float — L7 is green at the PIN (regression row); the real R5 non-string row is L7b/S6 (`12345` → int).
- **X4 premise has two forms:** the brief's literal mid-file `selected_core: [a, b]` is a `ParserError` (R2 class, line 46); the test exercises the appended fresh section, which is valid YAML and hits the R3 refusal.
- **Drift message:** the brief's predicted `FAIL: pin disagreement for …` is unreachable — 40 zeros parse as the int `0`, so R5 refuses first (the `FAIL: …` + rc=1 the brief requires is met; the `…agent-client-protocol…` key is in the message).
- **PyYAML 6.0.1 (brief authoring) vs 6.0.3 (this box):** no measured difference.

**NOT-done:** drift control is the script (not a pytest test — duplicating it under the 420 s cap adds failure modes; re-runnable with one line, `../scratch/k170-drift.sh`); safe loader unpinned by test (m8); `tests/test_vendored_manifest.py` untouched (no change needed); report_lint's 2 UNCHECKABLE refs reported, not chased. No gate verdict — a verify lane follows.
