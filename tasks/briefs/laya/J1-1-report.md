PC-J1-1 BUILD-LANE REPORT

Header

- Status: build proposal only. Independent sandbox adversarial verification has not run. This lane does not issue a gate verdict.
- PIN: `330803c`. Lane: `pc-j1-1`. Finished at `2026-09-23T02:26:33Z`.
- Scope: only the J1-1 boundary in `tasks/briefs/laya/J1-1-brief.md:5`.

PREMISE — VERIFIED

- The exact contract names `SCHEMAS` as seven closed schemas and exact refusal strings at `B:8-19`.
- The PIN tree had no decisions package; this increment added `state_digest` at `C:70-77` and package exports at `src/agent_factory/decisions/__init__.py:14-21`.
- The build follows the pinned `state_digest` transform order in `L:14-17`: normalize -> redact -> canonical -> sha256.

FILES / LINES

- `src/agent_factory/decisions/__init__.py:14-21` — exports `DecisionStateError`, `normalize`, `redact`, and `state_digest`; SHA-256 `2aec3875f71213e4dc91557013439fdba6174b9a777cc87f6470e8d8b92c10b5`.
- `C:26-77` — `_canon_str`, `canonical`, `_canon`, and `state_digest`; SHA-256 `bc9cb1d03fdb77a47dba18098367c15f1902fc4907cfd2f676e04cce09c879ad`.
- `V:30-59` — `PLACEHOLDERS`, `_BEARER`, `_SK`, `_TOKEN`, `_ENVVAL`, and `_PRIVKEY` implement five fixed redaction classes.
- `V:72-148` — `_Field`, `_strip_pin_suffix`, `_nfc_collapse`, `_path`, and `_normalize_field` implement exact PIN stripping, paths, sorted lists, leading-token command targets, NFC, whitespace, case, and bounds.
- `V:151-224` — `SCHEMAS` contains the seven closed state schemas; incumbent answers remain row provenance, not stable state.
- `V:242-295` — `normalize`, `redact`, and `_redact_str` enforce closed-schema refusals, enums, normalization, and redaction; file SHA-256 `b48899c883c7231f85f0a0db57de60fcbedf2b9238f3cef747d0999c2cd7b1a7`.
- `T:42-50` — `GOLDEN_DIGESTS` holds seven pasted values.
- `T:63-96` — `test_golden_digests_exact` and `test_relanding_stable` prove exact digests x2 and re-landing identity.
- `T:108-185` — `test_secret_redacted_every_class` covers five classes, identical clean-state digests, and secret-byte absence.
- `T:193-283` — `test_unknown_key_refused`, `test_closed_schema_refuses_incumbent_answer_key`, and sibling tests pin closed-schema/path/canonical failures plus leading-token and exact-PIN controls.
- `T:291-340` — `test_normalize_does_not_redact`, `test_redact_does_not_normalize`, and `test_order_is_normalize_then_redact`; test-file SHA-256 `48fdf09e8038a146cd7f7d24643fe33a911f4051f3c66021543264928f553048`.
- `tests/fixtures/decisions/golden/ap.violates_row.json:1-19`.
- `tests/fixtures/decisions/golden/b1.finding_kind.json:1-15`.
- `tests/fixtures/decisions/golden/b1.finding_sev.json:1-15`.
- `tests/fixtures/decisions/golden/b2.hit_role.json:1-15`.
- `tests/fixtures/decisions/golden/d1.bug_echo_scores.json:1-13`.
- `tests/fixtures/decisions/golden/v1.finding_class.json:1-25`.
- `tests/fixtures/decisions/golden/wf.drift.json:1-17`.

GOLDEN DIGESTS — PRODUCED, COMMITTED, ASSERTED EXACTLY

- `b2.hit_role` = `3ced4cd39a61faa5519dd3c491b9019347cfc12d447448bc53fc49118bc6423e`.
- `b1.finding_sev` = `8c42d5dd1e8c349e6e94ab40189e706dcc3ada5e262d44077734ef91c178350d`.
- `b1.finding_kind` = `9e18ed7e5146a2c3762ec1e00ae233351928e06ef07308563e844b07aec16abf`.
- `d1.bug_echo_scores` = `5a8c4ad2659c0e6b5dd2b2638bc2a546adca5e55f7246e073197fa30f5971bb8`.
- `v1.finding_class` = `f41a299c4a38ab305fc612dfc61cedd4481b9e6c6f9d3e1ffe24a229f10ad43e`.
- `ap.violates_row` = `594584bde9869086e1814489784747f00dbee9918e12c3d4f4bdb4f90702deef`.
- `wf.drift` = `a51a56c48e98cca60a95923da2a34a25bfb3609c1b23197588ad32af90cfc06b`.
- Producer repeat: `bitwise-stable (x2): True`; `ALL-RELAND-OK: True`.

RED -> GREEN

- First complete suite: `1 failed, 13 passed`; red test `test_order_is_normalize_then_redact`; root cause: the first discriminator used the `sk` class, which is independent of leading whitespace.
- Corrected negative control: a 32+ token run after `token:` and two spaces. Redact-first leaks it; normalize-first collapses to one space and catches it (`tests/test_decisions_canonical.py:314-340`).
- Final producer-backed count: `pytest-summary: 14 passed in 0.04s`; `pytest-exit: 0`.

MUTATION TABLE — SCRATCH COPIES, COMPILE + COLLECT + RESTORE SHA VERIFIED

- m1 drop normalize -> `2 failed, 12 passed`; named reds `test_relanding_stable`, `test_order_is_normalize_then_redact`; compiled=True, collected=True, restore-sha-ok=True.
- m2 drop redact -> `2 failed, 12 passed`; named reds `test_secret_redacted_every_class`, `test_order_is_normalize_then_redact`; compiled=True, collected=True, restore-sha-ok=True.
- m3 drop NFC -> `1 failed, 13 passed`; named red `test_relanding_stable`; compiled=True, collected=True, restore-sha-ok=True.
- m4 allow floats -> `1 failed, 13 passed`; named red `test_float_refused`; compiled=True, collected=True, restore-sha-ok=True.
- m5 swap order -> `1 failed, 13 passed`; named red `test_order_is_normalize_then_redact`; compiled=True, collected=True, restore-sha-ok=True.
- m6 open schema -> `2 failed, 12 passed`; named reds `test_unknown_key_refused`, `test_closed_schema_refuses_incumbent_answer_key`; compiled=True, collected=True, restore-sha-ok=True.
- Harness line: `ALL-MUTANTS-DEAD: True`.

GATES

- PC gate run 1: `14 passed in 0.02s`; `run1-rc=0`.
- PC gate run 2 after deleting basetemp: `14 passed in 0.02s`; `run2-rc=0`.
- Seed AC 3 verify command with the PC interpreter: `14 passed in 0.02s`; `AC3-rc=0`.
- Pyflakes: `pyflakes-rc=0` (0 hits).
- Compile: `compile-rc=0`.
- `git diff --check`: `diff-check-rc=0`.
- FLAG-form AP screen: `--- TEST_SCREEN over 3 path(s): 0 hits over 3 files ---`; `ap-screen-rc=0`.
- Never-a-gate screen: `no_laya_in_gates: 33 files scanned, clean`; `no-laya-rc=0`.

SELF-ATTACK

- Wrong schema boundary: ruled out by the exact schema map at `src/agent_factory/decisions/volatile.py:151-224`, the unknown-key controls at `tests/test_decisions_canonical.py:193-230`, and m6.
- Stability accidentally depends on redaction or vice versa: ruled out by the separation controls and order discriminator at `tests/test_decisions_canonical.py:291-340`, plus m1, m2 and m5.
- Golden values are self-referential: reduced by pasting the seven produced values into a separate assertion table at `tests/test_decisions_canonical.py:42-50`, committing raw/re-landed fixture pairs, repeating each pipeline twice, and killing m1/m3 against those pairs. Independent verification is still required.

DISCREPANCIES

- Seed AC 1 is RED-until-J1-2 exactly as the brief predicts: `ModuleNotFoundError: No module named 'agent_factory.decisions.ledger'`; `AC1-rc=1`. No `ledger.py` stub was created.
- The venv is not installed editable; AC 1 required `PYTHONPATH=src` to reach the intended J1-2 ledger failure. Without it, the earlier command failed first with `No module named 'agent_factory'`.
- m1 and m2 each kill the designated test plus the order test; m6 kills the two unknown-key controls. The brief's word `only` does not reproduce, but every required mutant compiles, collects and dies for the intended mechanism.
- GitNexus clone index is 654 commits stale and does not contain new J1 symbols; `detect-changes` said `No changes detected.` It is not used as correctness evidence. Ripwire indexed the worktree and reported `state_digest`, `normalize`, `redact`, and the qualified decisions `canonical` as new symbols with zero incompatible callers.
- First `scripts/test_summary.sh` invocation incorrectly used Python and raised `SyntaxError`; the required shell invocation produced the pasted 14-test summary above.
- Production AP screen reported only AP-32 hash-use hits; classification: REQUIRED/RUN, because `state_digest` uses SHA-256 as the contract's identity primitive at `C:70-77`. The mandated FLAG-form screen reported 0 hits.
- Final bounded lint line: `report_lint: 29 refs — OK 17, NEAR 0, MISS 0, UNCHECKABLE 12, UNRESOLVED 0 (worktree)`.

NOT-DONE

- `src/agent_factory/decisions/ledger.py` is J1-2 and is NOT built.
- `scripts/decide-harvest` is J1-3 and is NOT built.
- No hook, script, ledger, task ledger, wiki, commit, push, PR or outward action was performed.
- Independent sandbox adversarial verification has not run; this remains a build proposal.
