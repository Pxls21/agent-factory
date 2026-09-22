# J1-1 — canonical.py + volatile.py: normalize → redact → canonical → sha256, the seven closed state schemas, committed golden digests

PIN: 1dcb7d5 (origin head at authoring). LANE: laya-j1-1 (sandbox; agent `code-implementer`). DISPATCH RULE: after the J0-a probe lane finishes (no timing on a contended box) and after VERIFY-J1-0's recommendation is graded.
CONTRACT: `seeds/seed-laya-j1-v1.yaml` AC 1 (`ac_bdaf2f13a1cee8c9`) + AC 3 (`ac_348ab0ae10309609`) · `tasks/laya-j1-breakdown.md` row J1-1 + the pinned decisions "state = a BOUNDED, CLOSED, per-question-type extraction" and "order of transforms: normalize → redact → canonical → sha256" · the verdict's J1 acceptance tests 1 (redaction) and the KC-J6 field list.
BOUNDARY (exact): NEW `src/agent_factory/decisions/__init__.py`, NEW `src/agent_factory/decisions/canonical.py`, NEW `src/agent_factory/decisions/volatile.py`, NEW `tests/test_decisions_canonical.py`, NEW `tests/fixtures/decisions/golden/` (one JSON fixture + one golden digest per question type). NOT `ledger.py` (J1-2), NOT `scripts/decide-harvest` (J1-3), nothing under `scripts/`, no hook. Do NOT commit. `pythonpath = ["src"]` is already set in `pyproject.toml`; the package `src/agent_factory/` exists (governance, audit).

## The contract (exact)
1. **Seven closed schemas** in `volatile.py` (a `SCHEMAS` mapping question_id → the ordered tuple of allowed keys + per-key normalizers), ONE per question type:
   - `b2.hit_role` = {sym, file (repo-relative), snippet (the hit line, whitespace-collapsed)}; options {def, caller, config, test, other}
   - `b1.finding_sev` = {file, kind, msg}; options {H, M, L}
   - `b1.finding_kind` = {file, kind, msg}; options = an open slug closed to ≤ 8 by the harvest (the schema records `options_max: 8`)
   - `d1.bug_echo_scores` = {class_slug, finding_title}; six sub-questions of 5 levels each
   - `v1.finding_class` = {lane (the report's lane id WITHOUT its PIN suffix), finding_id, title, paths (sorted repo-relative list), disposition}; options {SOLID, UNSURE} × {BLOCKING, NON-BLOCKING}
   - `ap.violates_row` = {action_kind ∈ {edit, command, brief, report}, action_target (a repo-relative path, or a command's LEADING TOKEN only), action_excerpt (≤ 400 chars, normalized, redacted), row_id (AF-AP-N), row_title}; options {yes, no}
   - `wf.drift` = {step_id ∈ {verify-seam-first, one-increment-code-test-commit, negative-control, count-pasted, timestamp-pasted, commit-before-dispatch, impact-before-edit, premise-measured, report-lint-floor, boundary-respected}, expected, observed (≤ 400 chars, normalized, redacted), drift_kind ∈ {skipped-step, out-of-boundary, substituted-step, mirror-test, prose-claim}}; options {yes, no}
   An unknown key → `DecisionStateError("decision-state-unknown-key: <question_id>.<key>")`; a missing required key → `decision-state-missing-key: <question_id>.<key>`; an enum value outside its set → `decision-state-bad-enum: <question_id>.<key>=<value>`; an unknown question_id → `decision-question-unknown: <question_id>`. Line numbers, timestamps, absolute paths, run ids, PIN SHAs are NEVER accepted as state keys (they belong to `source_ref.locator`, J1-2's).
2. **normalize(question_id, state)** — the STABILITY mechanism: repo-relativize any absolute path under the repo root (a path outside the root is refused: `decision-state-abs-path: <key>`), NFC-normalize every string, collapse runs of whitespace to one space and strip, sort list-valued keys, lower-case enum values where the schema says so, truncate the bounded excerpts at their limit on a character boundary.
3. **redact(state)** — the SECURITY mechanism ONLY, applied AFTER normalize: replace every match of the secret classes with the fixed placeholder `<redacted:CLASS>`: `sk-[A-Za-z0-9_-]{8,}` (CLASS=sk), bearer tokens (`(?i)bearer\s+[A-Za-z0-9._~+/-]{16,}=*` → bearer), private-key blocks (`-----BEGIN [A-Z ]*PRIVATE KEY-----` through END → privkey), `KEY=…`/`TOKEN=…`/`SECRET=…`/`PASSWORD=…` env assignments (the value part → envval), and the project's bridge token shape (`PC_BRIDGE_TOKEN=…` → envval; a 32+ hex/base64 run after `token` → token). Redaction never contributes to stability and stability never relies on it.
4. **canonical(obj)** — sorted keys, `ensure_ascii=False`, separators `(",", ":")`, NFC, integers/strings/lists/dicts only (a float → `decision-canonical-float: <key>`), `\n`-free; **state_digest = sha256(canonical(redact(normalize(state))))** hex.
5. **Golden digests:** `tests/fixtures/decisions/golden/<question_id>.json` = {question_id, state (the raw input), expected_digest}; one per type, SEVEN files; the digests are produced by the lane's code, committed, and asserted EXACTLY by the test; a re-landed variant fixture per type (line numbers, a PIN suffix, an absolute path under the root, extra whitespace, NFD instead of NFC) must hash to the SAME digest.
6. **The injected-secret test:** for every secret class, a state carrying the secret in an excerpt/msg hashes IDENTICAL to the same state with the secret absent (the placeholder must therefore equal the redaction of the absent form — design this: the fixture's clean form CONTAINS the placeholder), and the secret bytes appear in no output (assert over the canonical bytes and the digest input).

## Tests (each RED before the code exists, GREEN after; paste both)
`test_golden_digests_exact` (7 types ×2 runs bitwise) · `test_relanding_stable` (7 variants) · `test_secret_redacted_every_class` (5 classes) · `test_unknown_key_refused` / `test_missing_key_refused` / `test_bad_enum_refused` / `test_unknown_question_refused` (exact strings) · `test_abs_path_outside_root_refused` · `test_float_refused` · `test_normalize_does_not_redact` (a secret survives normalize alone) · `test_redact_does_not_normalize` (whitespace survives redact alone) · `test_order_is_normalize_then_redact` (a secret split by whitespace is caught only in the right order).
Mutants (scratch-copy restore; paste the failing test per row): m1 drop normalize → only the re-landing test red; m2 drop redact → only the secret test red; m3 drop NFC → the NFD variant red; m4 allow floats → the float test red; m5 swap the order → the split-secret test red; m6 open the schema (accept unknown keys) → the unknown-key test red.

## Gates (paste verbatim)
`mkdir -p /tmp/j11/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/tmp/j11/bt` twice (rm -rf after each); `python -m pyflakes src/agent_factory/decisions/*.py tests/test_decisions_canonical.py`; the seed's AC 1 verify_command (it imports `agent_factory.decisions.ledger` too — that module is J1-2's: state the AC 1 result honestly as RED-until-J1-2 if the import fails, never stub `ledger.py`); AC 3's command; `python3 scripts/ap_screen.py --tests src/agent_factory/decisions/canonical.py src/agent_factory/decisions/volatile.py tests/test_decisions_canonical.py` (the FLAG form); `python3 scripts/no_laya_in_gates.py` (the live screen must stay clean — your files are outside its scanned set by construction; paste the line).

## Report (`tasks/briefs/laya/J1-1-report.md`)
DATA: files:lines; the RED→GREEN pairs; the six mutant rows; the two gate runs; the seven golden digests (pasted); DISCREPANCIES / NOT-done (AC 1's ledger import = J1-2's; say so). `report_lint --min-refs 10` (≤ 3 rounds).

## PREMISE — MEASURED at authoring (2026-09-22T17:22:34Z, sandbox @ 1dcb7d5)
```
$ ls src/agent_factory/ && ls src/agent_factory/decisions 2>&1 | head -2
__init__.py __pycache__ audit governance 
ls: cannot access 'src/agent_factory/decisions': No such file or directory
$ grep -n 'pythonpath' pyproject.toml
15:pythonpath = ["src"]
$ ls tests/fixtures/decisions/
gate_violation probe 
$ python3 scripts/no_laya_in_gates.py; echo rc=$?
rc=0
$ grep -c 'decision-state-unknown-key\|decision-row-incomplete' tasks/laya-j1-breakdown.md
4
```
