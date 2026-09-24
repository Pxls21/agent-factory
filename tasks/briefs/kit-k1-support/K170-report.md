# K170 report — the lock and SBOM parsers fail closed (task #170; PIN 9e6821b)

## 1. Premise, re-measured

All commands echoed and pasted from `../scratch/premise-{1,2,3}.txt`, run from the lane tree at
9e6821b252717c15cd1381fcead0c64abc50986f (clean at the start: `git status --porcelain | wc -l` = 0).

Blob identities match the brief's premise block:

| file | brief | re-measured |
|---|---|---|
| scripts/vendored_manifest.py | 4a4ed0fece0b | 4a4ed0fece0b (match) |
| upstream.lock.yaml | 514b0f96f8a2 | 514b0f96f8a2 (match) |
| SBOM.yaml | b68cb55da3b3 | b68cb55da3b3 (match) |
| sandbox-kit/VENDORED-FROM.md | 98feae9d4d8b | 98feae9d4d8b (match) |

`git log -4` on the four files: 20da8620, 52769767, 9c991a2e, 879ee98f (matches the brief).

Premise block output, re-measured (verbatim, from the scratch transcripts):

- lock line-parser branches: `{'blank/comment': 17, 'component': 27, 'pin-field': 51, 'section': 8, 'skipped': 90}`; skipped per section: `(top level) 1, advisory_models 13, advisory_tooling 14, development_and_reference 6, lane_runtime 7, local_model_server 9, not_selected_as_stock_runtimes 8, selected_core 18, selected_later_planes 14`
- `parse_lock: 24 entries, digest f3b81f34ac1966c3; yaml extraction equal: True`
- lock components without repository: `['advisory_models.laya-typed-decisions', 'local_model_server.qwen38-27b-rtx3090', 'lane_runtime.hermes-agent-lane-runtime']`
- lock components with a repository and no pin key: `[]`
- lock components with two pin keys: `['advisory_tooling.ripwire:commit+binary_sha256+asset_sha256']` (all three, the precedence case)
- lock repositories pinned twice: `[]`
- lock pin/repository value types: `{'str': 51}`
- `parse_sbom: 22 entries, digest 734a79b525e59e2f; yaml extraction equal: True; components 22; keys ['commit', 'license', 'name', 'repository', 'role']`
- duplicate keys at any depth: none in either file
- provenance: header line 9, 9 rows, walk stops at line 20 (`''`), roots 9
- repro rows L0–L9, S0–S5, P0–P1: every "Today (premise)" value reproduces verbatim (full paste in `../scratch/premise-2.txt`; highlights: L1/L2/L3 23 entries with hermes re-labelled `selected_core.agent-client-protocol`; L4 24 with hermes = 40 zeros; L5 24 with `selected_core.hermes-agent-copy`; L6 23 with hermes dropped; L7 pin reads `'1e10'`; L8 pin reads `'527da60844d4dced37879ea50259675371abe10e  # note'`; L9 `ManifestError: upstream lock parse failure at line 163`; S1 21 with hermes named `agent-client-protocol`; S2 22 last-wins; S3 21 dropped; S4 21 dropped; S5 22 = real map (regression row, green at PIN); P0 9 roots; P1 2 of 9 roots)
- `LC_ALL=C grep -c` of U+2028/U+2029/U+0085/CRLF bytes on all three files: `0 0 0` (rc=1, as the brief notes)
- `grep -n '^  hermes-agent:$\|^  agent-client-protocol:$\|^selected_later_planes:$' upstream.lock.yaml` → lines 5, 10, 45
- PyYAML present in the CI workflow (`.github/workflows/stage0-ci.yml:40,64,84,103`) and in the host interpreter: `/usr/bin/python3` 6.0.3 (brief's authoring environment: `/usr/local/bin/python3` 6.0.1 — same major; see DISCREPANCIES)
- `python3 scripts/vendored_manifest.py --check` → `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots` (rc 0)
- `python3 proofs/S0-12/check_pin_diff.py . | tail -2` → `PASS`
- drift control AT THE PIN: `k170-drift.sh ../scratch/drift` → `mutated: a trailing space on the agent-client-protocol line; its commit drifted to 40 zeros` / `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots` / `vendored_manifest --check rc=0` / `sbom-pin-drift: pin differs from upstream.lock.yaml for agent-client-protocol` / `check_pin_diff rc=1` — the hollow green the brief describes, at the real entry point, reproduced.
- consumer set: `257 tests collected in 0.44s`; `bash scripts/pc_suite.sh set-id -- <the five files>` → `5 files set=10334866f935` (matches the brief)
- ap_screen at the PIN: AF-AP-132 ×6 at 402, 477, 575, 653, 759, 798; AF-AP-25 ×2 at 759, 798 (the two in-boundary sites)

**Premise: VERIFIED. No boundary mismatch; the lane proceeds.**

## YAML behavior measured (pre-parse vs parse-time)

`yaml.safe_load` on the mutations (PyYAML 6.0.3, venv 3.11.14):
- L3 (3-space indent) → `ParserError` at problem line 10 (the `hermes-agent` line; the context mark is line 5). R2 uses the problem mark → line 10.
- X1 (U+2028 inside the hermes commit value) → a `ScannerError` at the YAML-own line 14; but R1's pre-parse scan finds the U+2028 at newline-count line 12 FIRST, with the R1 message. (Two different numbering models by design: R1 = newline count, R2 = YAML mark.)
- X2 (CRLF) → `safe_load` returns OK (no error at all). Only R1's pre-parse scan (carriage return at line 1) rejects it.
- X4 (a section written as a flow list) → a `ParserError` at line 46; X4b (a section written as a scalar) → a `ScannerError` at line 46. R2 reports the line; the R3 section-is-not-a-mapping refusal fires after load.
- X3 (an SBOM item with no repository) → `safe_load` OK (it is valid YAML). Only R7's item validation (missing repository) rejects it.
- A duplicate key at depth 2 → my `SafeLoader` subclass's mapping constructor raises before the loader would otherwise silently keep the last value; the message carries the SECOND key's `start_mark.line + 1`. (Both `safe_load` and the full `yaml.Loader` silently keep the last value on a dup — measured — so the refusal is purely my constructor.)
- The real files contain none of U+0085 / U+2028 / U+2029 / CRLF (R0 control; also the `LC_ALL=C grep -c` = 0 0 0).

This is why R1 must be a pre-parse newline-count scan with its own message, and R2 the post-load YAML-mark line: they answer different questions (which line holds a break both YAML and `str.splitlines()` would split, vs where the YAML engine choked).

## 2. What changed

**`scripts/vendored_manifest.py`** (the only modified file; +158/−56 vs the PIN):

- `:29-30` — `import yaml` (D-1).
- `:265` — `_LINE_SEPARATORS = (chr(0x0085), chr(0x2028), chr(0x2029), chr(0x000D))` (R1; built with `chr()`, no typed escape).
- `:268-276` — NEW `_refuse_line_separators(text, path)`: refuses the first hit of any separator, message `{path}: line {n} holds {separator!r}`, line counted by newline characters (R1, AF-AP-132).
- `:281-321` — NEW `load_manifest_yaml(path, label)`: the single loader helper (D-1/D-2). Reads RAW bytes (`read_bytes().decode("utf-8")` — `Path.read_text` would translate CRLF and hide the carriage return), runs the R1 scan, then `yaml.load` through a per-call `SafeLoader` subclass whose mapping constructor refuses a duplicate key at any depth (message `{label} duplicate key {key!r} at line {n} ({path})`, the SECOND key's line). A `yaml.YAMLError` becomes `{label} parse failure at line {n} ({path})` from the problem mark. Never a raw `YAMLError`, never a traceback.
- `:323-329` — NEW `_clean_str(value, where)`: R5 — refuses a value that is not a non-empty whitespace-free string (YAML reads a long digit run as an int, `0000…` as `0`, an empty value as None) with `{where}: the value {v!r} is not a non-empty whitespace-free string`.
- `:730` — `parse_provenance`: now reads raw bytes, runs the R1 scan, numbers by `text.split("\n")` (the in-boundary AF-AP-132 site at the PIN's `:653` removed); the table walk REFUSES a non-blank line that does not start with `|`, naming its line (`provenance table parse failure at line {n}: expected a row`), and stops only at the first blank line (R8).
- `:837-876` — `parse_lock`: the line regex is gone. D-1 load; R3 — a top-level scalar is ignored (it carries no pin), any other non-mapping top-level value is refused by its section key, a non-mapping component value is refused by `section.component`; R4 — a component with `repository` must carry a pin (message `{where} has a repository but no pin (commit, binary_sha256, asset_sha256)`); R5 via `_clean_str`; R6 — a repository pinned twice is refused naming both `section.component` keys. Pin precedence `commit` → `binary_sha256` → `asset_sha256` unchanged.
- `:878-913` — `parse_sbom`: D-1 load; R7 — the top level is a mapping whose `components` value is a list; each item is a mapping with non-empty string `name` and `repository` and a pin (`commit` → `digest`); a missing name / missing repository / missing pin / non-mapping item is refused naming the item's name (or its 1-based position when it has none); a repository named twice is refused naming both names (message `SBOM: repository {key} is named by both {first} and {second}`).
- `:915` `validate_pin_agreement` and `:1255` `main` are UNCHANGED (byte-identical to the PIN — the `FAIL:` print and exit-1 behaviour the brief's D-2 relies on already exist there; the new `ManifestError`s from the three parsers flow into it).

**`tests/test_vendored_manifest_parse.py`** (NEW, 451 lines, 24 tests): one test per brief row, plus the dedicated non-string-pin rows L7b/S6 and X4b/X5. The module under test is loaded fresh under a unique name per test so every test re-reads the file on disk.

**Boundary check**: the brief names `parse_lock`, `parse_sbom`, the `parse_provenance` table walk, one new private loader helper, and `import yaml`. Implemented: those, plus `_refuse_line_separators` (a second private helper; see BOUNDARY DEVIATIONS) and the R1 raw-bytes read inside `parse_provenance`. Nothing else in the file touched.

## 3. Red run (the new test file on the PIN's code)

Run in a fresh `git clone --shared` at 9e6821b with the test file overlaid (the lane tree holds the fixed script; the red run must use the PIN's):

```
$ PYTHONPATH=$PWD/src /home/rocco/venv-agent-factory/bin/python -m pytest -n 8 -q -p no:cacheprovider tests/test_vendored_manifest_parse.py
20 failed, 4 passed in 0.61s
```

Per failing test, the exact first E-line (from `../scratch/redrun-final.txt`):

| test | red failure (verbatim first E-line) | brief row "Today" |
|---|---|---|
| test_L1_lock_trailing_space_on_component_line | `E AssertionError: the real map (24 entries) is required` | 23 entries, hermes re-labelled |
| test_L2_lock_trailing_comment_on_component_line | `E AssertionError: assert {'github.com/…` (map mismatch) | as L1 |
| test_L3_lock_three_space_indent | `E Failed: DID NOT RAISE ManifestError` | 23 entries (old: no raise) |
| test_L4_lock_duplicate_component | `E Failed: DID NOT RAISE ManifestError` | 24; hermes = 40 zeros |
| test_L5_lock_repository_pinned_twice | `E Failed: DID NOT RAISE ManifestError` | 24; last wins |
| test_L6_lock_pin_key_typo | `E Failed: DID NOT RAISE ManifestError` | 23; hermes dropped |
| test_L7b_lock_pin_read_as_int_is_refused | `E Failed: DID NOT RAISE ManifestError` | (R5 row; the old parser accepted `12345` as a string) |
| test_L8_lock_pin_with_trailing_comment | `E AssertionError: assert {'github.com/…` (map mismatch) | pin reads `'…  # note'` |
| test_L9_lock_yaml_round_trip | `ManifestError: upstream lock parse failure at line 163` (the old parser's own refusal, uncaught) | exactly the premise's L9 |
| test_S1_sbom_trailing_comment_on_name | `E AssertionError: assert {'github.com/…` (map mismatch) | 21; hermes named `agent-client-protocol` |
| test_S2_sbom_repository_named_twice | `E Failed: DID NOT RAISE ManifestError` | 22; last wins |
| test_S3_sbom_pin_key_typo | `E Failed: DID NOT RAISE ManifestError` | 21; hermes dropped |
| test_S4_sbom_flow_style_item | `E AssertionError: assert {'github.com/…` (map mismatch) | 21; hermes dropped |
| test_S6_sbom_pin_read_as_int_is_refused | `E Failed: DID NOT RAISE ManifestError` | (R5 row) |
| test_P1_provenance_non_row_line_is_refused | `E Failed: DID NOT RAISE ManifestError` | 2 of 9 roots, no error |
| test_X1_lock_line_separator_is_refused | `E Failed: DID NOT RAISE ManifestError` | (measured: a raw YAML error, not a ManifestError) |
| test_X2_lock_crlf_line_endings_are_refused | `E Failed: DID NOT RAISE ManifestError` | (measured: the old parser accepted it) |
| test_X3_sbom_item_without_repository_is_refused | `E Failed: DID NOT RAISE ManifestError` | (measured: the item was dropped) |
| test_X4_lock_section_written_as_a_list_is_refused | `E Failed: DID NOT RAISE ManifestError` | (the R3 refusal is new) |
| test_X5_lock_component_value_as_a_list_is_refused | `E AssertionError: Regex pattern did not match.` (old: the list items were silently skipped, 24 entries) | (the R3 refusal is new) |

**The 4 passed at the PIN are the regression rows (stated in the test file's docstring): `test_R0_real_files_unchanged`, `test_L7_lock_pin_read_as_scalar_is_a_regression_row`, `test_S5_sbom_yaml_round_trip_is_a_regression_row`, `test_X4b_lock_top_level_scalar_is_ignored_regression_row`.**

**L7 is a brief-premise conflict, measured, not a test defect**: the premise (D-1/R5) says "YAML reads `1e10` as a float". Measured on PyYAML 6.0.1 AND 6.0.3: `yaml.safe_load('v: 1e10')` returns the STRING `'1e10'` — PyYAML implements YAML 1.1, whose core resolver does not tag the 1.2 exponent form. The old parser therefore already returned the real map for L7 (24 entries, pin `'1e10'`) — exactly the premise's own L7 row ("24; the pin reads `'1e10'`"). The red run confirms L7 is GREEN at the PIN. The test keeps the L7 row as the contract (pin survives as a string, 24 entries) and adds **L7b** (`commit: 12345`, a real YAML int) as the dedicated R5 non-string-pin row — the class the D-1 text actually meant ("a long run of digits as an int"). Same on the SBOM side: **S6** (an appended item with `commit: 12345`, refused naming `k170-probe`).

**X4 is a brief-premise conflict, measured, in two forms.** The brief's literal mid-file mutation `selected_core: [a, b]` collides with the block mapping already begun at the indent (the section's components) and is a YAML SYNTAX error — measured: `ParserError` at line 46 — refused by the R2 class, not R3. But the R3 list-value refusal the brief names still needs a live exercise: a FRESH top-level section `k170_probe: [a, b]` appended at the file end is VALID YAML (no mapping continuation yet) and is refused by R3 as `upstream lock: section 'k170_probe' is a list, not a mapping`. The test uses that appended form. (The same two forms hold for the scalar case, X4b: mid-file a scalar where a mapping was begun is a YAML error; an appended fresh scalar is valid and IGNORED — the real file's `snapshot_date` already is.)

**P1's row count**: the brief's `k170-repro.py` P1 takes `rows[3]` of the ten `| `-prefixed lines (header + 9 data rows) → data row 3 = file line 13. The test pins `assert len(rows) == 10` and targets file line 13; the refusal names line 13. (An earlier draft of the test used 9 — that draft's P1 failed for that wrong reason; the committed test file has the 10-row pin.)

## 4. Green run (the new test file on the changed code)

```
$ PYTHONPATH=$PWD/src /home/rocco/venv-agent-factory/bin/python -m pytest -n 8 -q -p no:cacheprovider tests/test_vendored_manifest_parse.py
24 passed in 0.69s
24 passed in 0.67s
```
(two runs, this session, after the final docstring fix; both green)

## 5. The outermost control (drift through the real entry point)

`bash ../scratch/k170-drift.sh <dir>` overlays the working copy of `scripts/vendored_manifest.py` on a `--shared` clone of HEAD (0.8 s), puts a trailing space on the lock's `agent-client-protocol:` line and drifts its commit to 40 zeros, then runs both checkers there.

**Before (at the PIN, `../scratch/drift-before`, the hollow green):**
```
mutated: a trailing space on the agent-client-protocol line; its commit drifted to 40 zeros
PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots
vendored_manifest --check rc=0
sbom-pin-drift: pin differs from upstream.lock.yaml for agent-client-protocol
check_pin_diff rc=1
```

**After (with the change, `../scratch/drift-after`):**
```
mutated: a trailing space on the agent-client-protocol line; its commit drifted to 40 zeros
FAIL: selected_core.agent-client-protocol: the value 0 is not a non-empty whitespace-free string
vendored_manifest --check rc=1
sbom-pin-drift: pin differs from upstream.lock.yaml for agent-client-protocol
check_pin_diff rc=1
```

`--check` now refuses (rc=1) and `check_pin_diff` stays rc=1. The hollow green is gone, at the real entry point.

**The message is R5, not the brief's predicted `FAIL: pin disagreement for …agent-client-protocol…` — and the brief's prediction is unreachable by construction.** The drift value is 40 zeros: PyYAML's YAML-1.1 core resolver reads an all-digit plain scalar as an int, and `0000…0` is `0` (measured: `yaml.safe_load('v: 0000000000000000000000000000000000000000') == {'v': 0}`; `1111…` → big int; `aaaaaaaa…` and the real 40-char hex pins stay strings because they are not all-digit). R5 therefore refuses the value in `parse_lock` BEFORE `validate_pin_agreement` can ever compare it. D-2 says a parse failure is a `ManifestError`, and `main` already prints `FAIL: …` and exits 1 for one (the code path is unchanged). The pin-disagreement message is only reachable for a pin that is a valid non-empty string AND different from the SBOM's (e.g. a 40-char hex drift). The brief's actually-required outcome — "must print `FAIL: …` and exit 1" — is met; the `…agent-client-protocol…` substring is in the component key. See DISCREPANCIES D-3.

**pytest wrapping (the brief's "if you can"): not done — see NOT-done.** The brief's own script runs `python3` (the HOST interpreter) inside the clone and needs a git revision for `--check`; a pytest test re-running it would be a second, slower copy of the same control with its own failure modes under the 420 s cap. The two script runs above ARE the control; they are fast (0.8 s clone, <1 s each) and deterministic, and the verifier re-runs them with one line. The script stays in `../scratch/k170-drift.sh` with its usage line.

## 6. Mutation audit (scratch copies only, never the lane tree's file)

Method: `../scratch/k170-mutations.py` — per mutant, a scratch dir with the script (one exact string replacement, count asserted == 1), a copy of the committed test file and the three real inputs; `py_compile` first (a mutant that does not compile or collect is INVALID, AF-AP-78, never a kill); then the full test file run against the mutant. Nine mutants:

| mutant | edit (scratch) | killed by | evidence (this run) |
|---|---|---|---|
| m1 | the duplicate-key refusal removed (the mapping constructor just calls `construct_mapping`) | test_L4_lock_duplicate_component | `1 failed, 23 passed in 0.44s`; failed: `test_L4_lock_duplicate_component` |
| m2 | `_clean_str` body removed (returns the value as-is) | test_L7b_lock_pin_read_as_int_is_refused, test_S6_sbom_pin_read_as_int_is_refused | `2 failed, 22 passed in 0.44s`; failed: `test_L7b_lock_pin_read_as_int_is_refused`, `test_S6_sbom_pin_read_as_int_is_refused` (L1/L2/L8 stay green: their mutations are whitespace/comment, which a string pin still carries) |
| m3 | the lock repository-twice refusal removed | test_L5_lock_repository_pinned_twice | `1 failed, 23 passed in 0.43s`; failed: `test_L5_lock_repository_pinned_twice` |
| m4 | the SBOM repository-twice refusal removed | test_S2_sbom_repository_named_twice | `1 failed, 23 passed in 0.44s`; failed: `test_S2_sbom_repository_named_twice` |
| m5 | the R1 separator/CRLF scan removed from BOTH call sites (the loader and the provenance walk) | test_X1_lock_line_separator_is_refused, test_X2_lock_crlf_line_endings_are_refused | `2 failed, 22 passed in 0.45s`; failed: `test_X1_lock_line_separator_is_refused`, `test_X2_lock_crlf_line_endings_are_refused` |
| m6 | the provenance non-row refusal removed (`raise` → `break`) | test_P1_provenance_non_row_line_is_refused | `1 failed, 23 passed in 0.44s`; failed: `test_P1_provenance_non_row_line_is_refused` |
| m7 | the SBOM missing-pin refusal removed | test_S3_sbom_pin_key_typo | `1 failed, 23 passed in 0.45s`; failed: `test_S3_sbom_pin_key_typo` |
| m8 | the safe loader swapped for the full `yaml.Loader`, two ways measured | **m8b (the clean one: base class `SafeLoader`→`Loader` only, the duplicate-key constructor KEPT) → 24 passed. NOTHING TURNS RED: the safe loader is unpinned by the test set**, stated as the brief asks — every real-file and mutation row parses identically under the full loader, because the difference (constructing Python objects for non-core tags like `!!python/object`) cannot be expressed in a manifest file. The safe loader is pinned by the source (`yaml.SafeLoader` in `load_manifest_yaml`), not by a test. **m8-raw (swapping `Loader=loader` for `Loader=yaml.Loader`, which also drops my duplicate-key constructor) → `1 failed, 23 passed`; failed: `test_L4_lock_duplicate_component` — but that is m1's kill (the dup constructor is gone), not the base class's.** Measured: both `yaml.safe_load` and `yaml.load(Loader=yaml.Loader)` silently keep the LAST value on a duplicate key (no raise), so the dup refusal is purely my constructor and orthogonal to safe-vs-full. |
| m9 | the lock pin precedence reversed (`asset_sha256`, `binary_sha256`, `commit`) | test_R0_real_files_unchanged | `1 failed, 23 passed in 0.43s`; failed: `test_R0_real_files_unchanged` (the D-3 digest of the real map changes: `ripwire` carries all three pin keys and its chosen pin is `commit`) |

All nine mutants were run; m8 (clean form) is the only survivor, and it is reported as such per the brief's instruction.

## 7. Gates

**1. The new test file** (run twice this session; both green):
```
$ PYTHONPATH=$PWD/src /home/rocco/venv-agent-factory/bin/python -m pytest -n 8 -q -p no:cacheprovider tests/test_vendored_manifest_parse.py
24 passed in 0.58s
24 passed in 0.82s
```

**2. The consumer set, unchanged** (the five brief-named files; run twice this session; both runs under the 420 s cap):
```
$ PYTHONPATH=$PWD/src /home/rocco/venv-agent-factory/bin/python -m pytest -n 8 -q -p no:cacheprovider tests/test_vendored_manifest.py tests/test_s0_12_license_sbom.py tests/test_laya_pin.py tests/test_upstream_lock_lane_runtime.py tests/test_edit_snapshot_ap_screen.py
257 passed in 22.55s
257 passed in 29.82s
$ bash scripts/pc_suite.sh set-id -- <the five files>
5 files set=10334866f935
```
The set id matches the brief's (`10334866f935`) — the five files are byte-identical to the PIN (I modified none of them; the `test_edit_snapshot_ap_screen.py` AF-AP-25/AF-AP-132 tests fire on their own inline snippets, not on the file on disk).

**3. The two checkers on the lane tree (the real, unchanged files):**
```
$ python3 scripts/vendored_manifest.py --check
PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots
$ python3 proofs/S0-12/check_pin_diff.py . | tail -1
PASS
```

**4. `python3 scripts/ap_screen.py scripts/vendored_manifest.py`** (the new line numbers):
```
$ python3 scripts/ap_screen.py scripts/vendored_manifest.py 2>&1 | awk '/^[A-Z]/{show=($1=="AF-AP-132:"||$1=="AF-AP-25:")} show'
AF-AP-132: 3
    scripts/vendored_manifest.py:482: lines = data.decode("utf-8").splitlines()
    scripts/vendored_manifest.py:557: for line_number, line in enumerate(text.splitlines(), start=1):
    scripts/vendored_manifest.py:655: lines = text.splitlines()
AF-AP-25: 0
```
The three AF-AP-132 hits are exactly the three OUT-OF-BOUNDARY sites the brief names, at their new line numbers: `:482` (was `:402`), `:557` (was `:477`), `:655` (was `:575`) — a +80 shift (the 2-line import block plus the ~78-line helper block, both above them). The in-boundary sites `:653` (provenance), `:759` (parse_lock) and `:798` (parse_sbom) are GONE: the provenance walk now counts by newline characters and the two line loops are replaced by the YAML-mark line. **No AF-AP-25 hits** (the two at `:759`/`:798` are gone with the line loops). No new hit in the changed hunks: the screen does not fire on the `text.split("\n")` line in `parse_provenance` (the ap_screen test file's `test_no_fire_on_the_newline_split` is the non-firing case, and the run above confirms it).

**5. Pyflakes:**
```
$ /home/rocco/venv-agent-factory/bin/python -m pyflakes scripts/vendored_manifest.py tests/test_vendored_manifest_parse.py
(no output, rc=0)
```

**6. Report lint:** run at the end of the report (item 12); the final summary line is pasted in DISCREPANCIES.

## 8. Line anchors (machine-checkable; one `file:NN` with its on-line content per row)

- scripts/vendored_manifest.py:29 — `import yaml` (D-1; the import block is the only other change at the top of the file)
- scripts/vendored_manifest.py:265 — `_LINE_SEPARATORS = (chr(0x0085), chr(0x2028), chr(0x2029), chr(0x000D))` (R1; no typed escape in source)
- scripts/vendored_manifest.py:268 — `def _refuse_line_separators(text: str, path: Path) -> None:` (the R1 scan, shared by loader and provenance walk)
- scripts/vendored_manifest.py:281 — `def load_manifest_yaml(path: Path, label: str) -> object:` (the single fail-closed loader, D-1/D-2)
- scripts/vendored_manifest.py:323 — `def _clean_str(value: object, where: str) -> str:` (R5)
- scripts/vendored_manifest.py:730 — `def parse_provenance(path: Path) -> tuple[set[str], dict[str, int]]:` (R8; the raw-bytes read and the newline-count walk live inside it)
- scripts/vendored_manifest.py:837 — `def parse_lock(path: Path) -> dict[str, tuple[str, str]]:` (R3–R6)
- scripts/vendored_manifest.py:878 — `def parse_sbom(path: Path) -> dict[str, tuple[str, str]]:` (R7)
- scripts/vendored_manifest.py:915 — `def validate_pin_agreement(root: Path) -> None:` (unchanged; the D-2 `FAIL:` print and exit 1 already live in `main` below it)
- scripts/vendored_manifest.py:1255 — `def main(argv: list[str] | None = None) -> int:` (unchanged; prints `FAIL: {error}` and returns 1)
- scripts/vendored_manifest.py:482 — `lines = data.decode("utf-8").splitlines()` (OUT-of-boundary AF-AP-132 site; `:402` at the PIN)
- scripts/vendored_manifest.py:557 — `for line_number, line in enumerate(text.splitlines(), start=1):` (OUT-of-boundary AF-AP-132 site; `:477` at the PIN; the `splitlines` call is the flagged token)
- scripts/vendored_manifest.py:655 — `lines = text.splitlines()` (OUT-of-boundary AF-AP-132 site; `:575` at the PIN; the `splitlines` call is the flagged token)
- upstream.lock.yaml:5 — `  agent-client-protocol:` (the drift target component, line 5)
- upstream.lock.yaml:10 — `  hermes-agent:` (the component the premise's L1–L9 mutations touch, line 10)
- upstream.lock.yaml:45 — `selected_later_planes:` (the section the L4/L5 mutations append into, line 45)
- SBOM.yaml:25 — `  - name: hermes-agent` (the SBOM's hermes item, line 25; the S1–S4 mutation target)
- .github/workflows/stage0-ci.yml:40 — `run: python -m pip install pyflakes pytest "jsonschema==4.25.1" "rfc3339-validator==0.1.4" "PyYAML>=6.0"` (PyYAML in every CI job, the D-1 premise)
- proofs/S0-12/check_pin_diff.py:64 — `print(f"sbom-pin-drift: pin differs from upstream.lock.yaml for {name}")` (the drift line the control's `check_pin_diff rc=1` carries; `:33` and `:34` are its `yaml.safe_load` of the SBOM and lock — the D-1 premise)
- tests/test_edit_snapshot_ap_screen.py:560 — `def test_fires_on_the_parse_sbom_loop(self):` (the AF-AP-25 row that fires on the old `parse_sbom` loop, from an inline snippet)
- tests/test_edit_snapshot_ap_screen.py:617 — `def test_fires_on_the_parse_lock_loop(self):` (the AF-AP-25 row for `parse_lock`, cited at the K215 PIN line 759)
- tests/test_vendored_manifest.py:1040 — `lambda text: text.replace("    validate_pin_agreement(root)\n", "    pass"),` (the consumer test file's mutation of the call; the file is byte-identical to the PIN — I did not touch it)
- tests/test_vendored_manifest.py:1178 — `# calling validate_pin_agreement() directly would survive the` (the consumer test's comment; same file, unchanged)

## 9. DISCREPANCIES

- **D-1 (brief premise, L7): "YAML reads `1e10` as a float" is false for PyYAML 6.** Measured on 6.0.1 (the brief's authoring interpreter) and 6.0.3 (the venv): `yaml.safe_load('v: 1e10')` → `{'v': '1e10'}` (string). PyYAML implements YAML 1.1, whose core resolver does not tag the 1.2 exponent form. The premise's own L7 row ("24; the pin reads `'1e10'`") already shows the string; the red run confirms L7 is GREEN at the PIN (a regression row). The dedicated non-string-pin refusal is exercised by L7b (`commit: 12345`, a real YAML int) and S6.
- **D-2 (brief premise, X4): the literal mutation `selected_core: [a, b]` is a YAML syntax error (R2), not the R3 refusal the brief names.** Measured: mid-file, a flow list where a block mapping was already begun (the section's components at the indent) is a `ParserError` at line 46 — R2's class. The R3 list-value refusal is exercised on a FRESH appended section `k170_probe: [a, b]` (valid YAML; refused naming the section). The appended form is a deviation from the brief's literal, and it is the only form that exercises R3 rather than R2.
- **D-3 (outermost control, the drift message): the brief's predicted `FAIL: pin disagreement for …agent-client-protocol…` is unreachable.** The drift value (40 zeros) is read by YAML as the int `0`, so R5 refuses it in `parse_lock` before `validate_pin_agreement` can compare: the actual message is `FAIL: selected_core.agent-client-protocol: the value 0 is not a non-empty whitespace-free string` (rc=1; `check_pin_diff` rc=1 unchanged). The brief's required outcome — "must print `FAIL: …` and exit 1" — is met, and the `…agent-client-protocol…` substring is in the component key. A `pin disagreement` message would require a drifted pin that is a valid non-empty string (e.g. 40 hex chars) AND different from the SBOM's. The D-3 rule (no behaviour change on the real files) is unaffected: both digests hold (the R0 test).
- **PyYAML version**: the brief's authoring environment ran `/usr/local/bin/python3` with 6.0.1; this lane's host `/usr/bin/python3` and the venv interpreter both run 6.0.3. Every premise measurement reproduced on 6.0.3; no 6.0.1/6.0.3 difference observed in any measured row.
- **Report lint (item 6 / 12, final summary line)**: `report_lint: 26 refs — OK 24, NEAR 0, MISS 0, UNCHECKABLE 2, UNRESOLVED 0 (worktree)`; `FLOOR — OK 24 >= --min-refs 10: the floor is met`; lint rc=0. Rounds: 1 — OK 22, MISS 1 (the `SBOM.yaml:19` anchor named the `agent-client-protocol` item; the hermes item is line 25 — corrected), UNCHECKABLE 2; 2 — OK 23, MISS 0, UNCHECKABLE 2; 3 — the two UNCHECKABLE lines carry a bare backticked token that the lint's claim-token extractors do not recognise (they sit in the ap_screen PASTE block, whose lines are verbatim tool output; the same refs are OK-checked in item 8's anchor lines) — final state as above, no further rounds (bounded at three), the two UNCHECKABLE refs are REPORTED.

## 10. BOUNDARY DEVIATIONS

- `_refuse_line_separators` is a second private helper beyond the brief's "one new private loader helper". It is the R1 scan the brief's R1 itself mandates ("each of the three files … is refused if it holds …"), and it is shared by the loader (lock, SBOM) and the provenance walk so one scan answers the question. It is private, file-local, and does no I/O.
- The R1 raw-bytes read inside `parse_provenance` (`read_bytes().decode("utf-8")` + the scan + `split("\n")`) goes beyond "the table walk" as a strict reading; R1's own text ("each of the three files (the lock, the SBOM and the provenance file) is refused if it holds …") requires the provenance file to be scanned, and the raw-bytes read is what makes the CRLF refusal actually work (`Path.read_text` would translate the carriage return away). Both are R1, not scope.
- The report itself: the brief names the path `tasks/briefs/kit-k1-support/K170-report.md`; it is written at that path IN THE LANE TREE (a new untracked file beside the two boundary files). A transient copy that a previous attempt of this lane left at the lane's parent dir (outside the boundary) was removed.

## 11. NOT-done

- **The drift control is a script, not a pytest test** (the brief's "if you can" was not satisfiable without duplicating the script's failure modes; the two runs in item 5 are the control and are re-runnable with one line; the script is `../scratch/k170-drift.sh`).
- **The safe loader is unpinned by a test** (mutation m8, clean form, survives — the brief's own instruction: "If nothing does, say so").
- **`tests/test_vendored_manifest.py`** (the old test file) was not modified (boundary: read-only). Its `validate_pin_agreement` mutation test (line 1040) and comment (line 1178) exercise the unchanged call path; no change to that file was needed.
- **No GATE RECOMMENDATION** (builder role; an independent verify follows — rule 0f).

## 12. Self-attack

The three most likely ways this change is wrong, and how each was ruled out:

1. **A real lock or SBOM the line parser accepted is now refused** (a false positive breaking `--check` or a hook). Ruled out by gate 3: `--check` prints PASS and `check_pin_diff` prints PASS on the lane tree's real files; R0 re-asserts the two D-3 digests and the 9 roots. The only new refusals fire on shapes the real files do not hold (no duplicate key, no separator, no non-mapping section, no repository-twice — all measured at the PIN in item 1).
2. **The R1 line number disagrees with an editor's for a file that mixes separators.** The scan counts newline characters only (never `splitlines()`), so a U+2028 inside a line reports that line's number, not the next line's (test_X1: line 12, the hermes commit line, not line 13). A file holding two different separator characters is refused at the first hit in the scan's character order (U+0085, U+2028, U+2029, CR — by severity, not position): the message names the character, so the reader finds the rest. That is a documented choice, not a defect.
3. **A duplicate key at depth >2 (a nested mapping the constructor might not visit) is missed.** The constructor is registered for `DEFAULT_MAPPING_TAG`, which the safe loader uses for EVERY mapping node at every depth (construction is bottom-up, so every nested mapping passes through it), so a duplicate at any depth is refused. The test set has L4 (depth 2: a component inside a section); a depth-3 duplicate is the same code path. The real files hold no duplicate at any depth (measured in item 1), so the depth-3 case is not exercised by a real-file mutation — it is the same constructor call.
