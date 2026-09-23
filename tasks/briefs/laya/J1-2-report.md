# J1-2 report: the append-only decision ledger

PIN: f949974
BRIEF: `tasks/briefs/laya/J1-2-brief.md`
BOUNDARY: `src/agent_factory/decisions/ledger.py` (L), `tests/test_decisions_ledger.py` (T)

## PREMISE — verified at f949974

All seven measurements match the brief. HEAD = origin = f949974; decisions module
has `__init__.py`, `canonical.py`, `volatile.py` (no `ledger.py`); J1-1 commit is
01ca7d5; public symbols at the same lines; 14 J1-1 tests pass; all 14 golden
states are fixed points; 39 commits touched `docs/INCIDENT-LOG.md` since
2026-09-22; the breakdown row_id line at line 14.

## FILES

- L:191 `make_row` — builds one complete row: calls `schema_keys` (J1-1), then
  `redact(normalize(question_id, raw_state, root))` for state, `state_digest`
  for the hash, sets `checkpoint_digest` to `"none"` and `calibration_state` to
  `"incumbent"`, computes `row_id` via `_compute_row_id` and `row_digest` via
  `_compute_row_digest`.
- L:70 `_compute_row_id` — amendment J1-A1: identity dict is `{producer,
  question_id, state_digest, source_ref: {kind, path, locator}}`; `source_digest`
  is NOT included.
- L:85 `_compute_row_digest` — `sha256(canonical(row without row_digest))`.
- L:230 `append` — validates the row (L:90 `_validate_row`, steps a-d), then
  replay-verifies the existing file (L:264 `replay`), checks for `decision-row-duplicate`,
  writes with `O_WRONLY|O_APPEND|O_CREAT` + `os.fsync` at L:253 (`os.open`).
- L:90 `_validate_row` — (a) completeness iterates `_ROW_FIELDS` at L:93,
  (b) validity checks `_VALID_KINDS` at L:135, (c) `expected_sd` =
  `_sha256_hex` at L:161, (d) fixed-point via `restate` = `redact` at L:180.
- L:264 `replay` — reads file bytes, splits by `\n`, validates each line
  is parseable JSON that equals `canonical(parsed)` byte for byte, runs
  `_validate_row` per row, checks for in-file duplicates.
- L:60 `_sha256_hex` — the digest primitive (`hashlib.sha256`).
- L:64 `_is_hex64` — validates 64-char lowercase hex strings.
- T:70 `test_import_ac1` — AC 1 import command.
- T:104 `test_replay_byte_identical_x2` — 7 rows from goldens, two ledgers,
  byte-identical, run 4 times.
- T:124 `test_relanding_same_row_id` — variant with same producer/source_ref
  produces the same `row_id`, refused as `decision-row-duplicate`.
- T:165 `test_source_digest_not_in_identity` — J1-A1: two `source_digest` values
  produce one `row_id`; different `locator` or `producer` produces a different one.
- T:222 `test_missing_provenance_each` — each of 5 top-level fields + 4
  `source_ref` sub-fields, both absent and empty, produce
  `decision-row-incomplete: missing <field>`.
- T:278 `test_duplicate_refused_bytes_unchanged` — duplicate row refused, file
  bytes unchanged.
- T:296 `test_tamper_detected` — file-level and in-memory flips in
  `incumbent_answer`, `state.file`, `source_ref.locator`, `source_ref.source_digest`,
  `row_id` produce `decision-row-digest-mismatch`; file unchanged on memory flips.
- T:387 `test_state_not_canonical` — un-normalized state (double whitespace) and
  unredacted secret (containing `sk-abcdef1234567890`), both with consistent
  digests, produce `decision-row-state-not-canonical`.
- T:470 `test_unparseable_lines` — torn last line, non-JSON line, valid JSON not
  canonical (spaces after colons) produce `decision-ledger-unparseable: <path>:<lineno>`.
- T:507 `test_invalid_fields` — another `calibration_state`, another
  `checkpoint_digest`, unknown `kind`, absolute path, `..` path, non-hex digest
  each produce `decision-row-invalid: <field>=<value>`.
- T:562 `test_append_only_prefix` — first 3 rows, then 4 more; first N lines
  byte-identical.
- T:584 `test_corrupt_ledger_not_appended` — tampered file + valid append: replay
  refusal, file unchanged.
- T:609 `test_j1_1_refusals_propagate` — `decision-question-unknown: x.unknown`
  and `decision-state-unknown-key: b1.finding_sev.extra` pass through `make_row`.

## RED-GREEN pairs

RED (13 failed, `ModuleNotFoundError: No module named 'agent_factory.decisions.ledger'`):
```
FAILED tests/test_decisions_ledger.py::test_import_ac1
FAILED tests/test_decisions_ledger.py::test_replay_byte_identical_x2
FAILED tests/test_decisions_ledger.py::test_relanding_same_row_id
FAILED tests/test_decisions_ledger.py::test_source_digest_not_in_identity
FAILED tests/test_decisions_ledger.py::test_missing_provenance_each
FAILED tests/test_decisions_ledger.py::test_duplicate_refused_bytes_unchanged
FAILED tests/test_decisions_ledger.py::test_tamper_detected
FAILED tests/test_decisions_ledger.py::test_state_not_canonical
FAILED tests/test_decisions_ledger.py::test_unparseable_lines
FAILED tests/test_decisions_ledger.py::test_invalid_fields
FAILED tests/test_decisions_ledger.py::test_append_only_prefix
FAILED tests/test_decisions_ledger.py::test_corrupt_ledger_not_appended
FAILED tests/test_decisions_ledger.py::test_j1_1_refusals_propagate
13 failed in 0.17s
```

GREEN (27 passed = 14 J1-1 + 13 J1-2):
```
27 passed in 0.12s
```

## MUTANT TABLE

All mutants compile and collect (AF-AP-78). Scratch-copy restore from `/tmp`, never git-restore.

| # | mutation | failing test | result |
|---|---|---|---|
| m1 | skip one provenance field (`producer` removed from `_ROW_FIELDS`) | `test_missing_provenance_each` | RED (KeyError) |
| m2 | duplicate becomes silent no-op (duplicate check removed from `append`) | `test_duplicate_refused_bytes_unchanged` | RED (DID NOT RAISE) |
| m3 | replay skips digest check (`_validate_row(parsed)` → `pass`) | `test_tamper_detected` | RED (DID NOT RAISE) |
| m4 | `source_digest` back in identity (added to `_compute_row_id`) | `test_source_digest_not_in_identity` | RED (AssertionError: row_ids differ) |
| m5 | fixed-point check dropped (section (d) removed from `_validate_row`) | `test_state_not_canonical` | RED (DID NOT RAISE) |
| m6 | replay drops canonical-line check (byte-for-byte comparison removed) | `test_unparseable_lines` | RED (AssertionError: wrong error path) |
| m7 | `O_TRUNC` instead of `O_APPEND` | `test_append_only_prefix` | RED (prefix changed) |

## GATE RUNS

### Gate run 1 (L + T + J1-1 tests):
```
27 passed in 0.12s
```

### Gate run 2 (bitwise):
```
27 passed in 0.14s
```

### Pyflakes:
```
(no output — clean)
```

### AC 1 (`python3 -c "import agent_factory.decisions as d, agent_factory.decisions.canonical, agent_factory.decisions.ledger; print('OK')"`):
```
OK
```

### AC 2 (`python -m pytest tests/test_decisions_ledger.py -q`):
```
13 passed in 0.13s
```

### AP screen (L):
```
AP-32: 1 (`hashlib.sha256` at L:61 in `_sha256_hex` — intentional digest computation)
```

### AP screen (T):
```
0 hits over 1 files
```

### no_laya_in_gates:
```
no_laya_in_gates: 38 files scanned, clean
```

## DISCREPANCIES

None. All contract lines met.

## NOT-DONE

- No fixture files created under `tests/fixtures/decisions/ledger/` — rows are
  built from J1-1's goldens in the tests as the brief preferred.
- `__init__.py` NOT modified (boundary constraint). J1-2's exports (`make_row`,
  `append`, `replay`) are available via `agent_factory.decisions.ledger` directly.

## DECLARED LIMITS

From the `Declared limits` block at L:13-17, matching the brief's contract item 7 line 1:
1. An unkeyed digest catches accidental or naive mutation, not a forger who
   recomputes every digest.
2. Deleting a whole row is not detected (no hash chain in J1).
3. One writer at a time.

## OUTCOME

GATE: PASS. 27 passed in 0.12s (run 1), 27 passed in 0.14s (run 2). 14 J1-1 tests green, 13 J1-2 tests green. Pyflakes clean. AC 1 OK. AC 2 13 passed. AP screen clean (1 intentional hit). no_laya_in_gates clean. All 7 mutants RED.

Files delivered: `src/agent_factory/decisions/ledger.py` (333 lines), `tests/test_decisions_ledger.py` (634 lines), `tasks/briefs/laya/J1-2-report.md`.
