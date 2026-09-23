DONE (proposal only): J1-1 is implemented and self-validated. Independent sandbox adversarial verification has not run, so this is not a gate verdict.

FILES

- `src/agent_factory/decisions/__init__.py:1-21`
- `src/agent_factory/decisions/canonical.py:26-77`
- `src/agent_factory/decisions/volatile.py:30-295`
- `tests/test_decisions_canonical.py:42-340`
- Seven fixtures under `tests/fixtures/decisions/golden/`
- Full report: `tasks/briefs/laya/J1-1-report.md`

IMPLEMENTED

- Seven exact closed state schemas.
- NFC, whitespace, enum-case, path, list, command-target, PIN-suffix, and length normalization.
- Five secret classes with fixed placeholders.
- Fixed pipeline: normalize → redact → canonical → SHA-256.
- Exact unknown/missing/bad-enum/path/float refusal strings.
- Re-landing stability for absolute paths, path ordering, whitespace, NFD, enum case, and PIN suffixes.
- Incumbent answer fields remain outside stable state.
- No `ledger.py`, harvest script, hook, or gate wiring was added.

GOLDEN DIGESTS

- `b2.hit_role`: `3ced4cd39a61faa5519dd3c491b9019347cfc12d447448bc53fc49118bc6423e`
- `b1.finding_sev`: `8c42d5dd1e8c349e6e94ab40189e706dcc3ada5e262d44077734ef91c178350d`
- `b1.finding_kind`: `9e18ed7e5146a2c3762ec1e00ae233351928e06ef07308563e844b07aec16abf`
- `d1.bug_echo_scores`: `5a8c4ad2659c0e6b5dd2b2638bc2a546adca5e55f7246e073197fa30f5971bb8`
- `v1.finding_class`: `f41a299c4a38ab305fc612dfc61cedd4481b9e6c6f9d3e1ffe24a229f10ad43e`
- `ap.violates_row`: `594584bde9869086e1814489784747f00dbee9918e12c3d4f4bdb4f90702deef`
- `wf.drift`: `a51a56c48e98cca60a95923da2a34a25bfb3609c1b23197588ad32af90cfc06b`

Producer repeat:

- `bitwise-stable (x2): True`
- `ALL-RELAND-OK: True`

RED → GREEN

- Initial complete suite: `1 failed, 13 passed`
- Red test: `test_order_is_normalize_then_redact`
- Cause: the first discriminator used the `sk` class, which does not depend on preceding whitespace.
- Corrected control: a 32+ token after `token:` plus two spaces. Redact-first leaks it; normalize-first collapses the spaces and catches it.
- Final producer count: `pytest-summary: 14 passed in 0.04s`; `pytest-exit: 0`

MUTANTS

All mutants compiled, collected, died, and passed restore-SHA verification:

- m1 drop normalize: `2 failed, 12 passed`; `test_relanding_stable`, order test
- m2 drop redact: `2 failed, 12 passed`; secret test, order test
- m3 drop NFC: `1 failed, 13 passed`; re-landing test
- m4 allow floats: `1 failed, 13 passed`; float-refusal test
- m5 swap order: `1 failed, 13 passed`; order test
- m6 open schema: `2 failed, 12 passed`; both unknown-key controls
- Final line: `ALL-MUTANTS-DEAD: True`

GATES

- PC run 1: `14 passed in 0.02s`; rc 0
- PC run 2 after basetemp removal: `14 passed in 0.02s`; rc 0
- Seed AC 3: `14 passed in 0.02s`; rc 0
- Pyflakes: 0 hits; rc 0
- Python compilation: rc 0
- `git diff --check`: rc 0
- FLAG AP screen: `0 hits over 3 files`; rc 0
- Never-a-gate screen: `no_laya_in_gates: 33 files scanned, clean`; rc 0
- Report lint: `29 refs — OK 17, NEAR 0, MISS 0, UNCHECKABLE 12, UNRESOLVED 0`; rc 0

DISCREPANCIES

- Seed AC 1 remains RED-until-J1-2 as specified: `ModuleNotFoundError: No module named 'agent_factory.decisions.ledger'`; rc 1. No stub was created.
- The PC venv is not editable. AC 1 needs `PYTHONPATH=src` to reach the expected missing-ledger failure; without it, import fails first at `agent_factory`.
- The brief says m1/m2/m6 should kill “only” one named test. Each also kills a second mechanism-specific control. Every required mutant still compiled, collected, and died.
- GitNexus is 654 commits stale and did not map the new files. Ripwire indexed the worktree and found zero incompatible callers for the new public symbols.
- The production AP screen’s AP-32 hash-use matches are REQUIRED/RUN because SHA-256 is the declared identity primitive. The mandated FLAG screen was clean.

SELF-ATTACK

- Wrong schema boundary: ruled out by exact closed-schema controls and m6.
- Transform responsibilities mixed: ruled out by separate normalize/redact tests plus m1, m2, and m5.
- Self-referential goldens: reduced by a separately pasted digest table, raw/re-landed fixture pairs, two pipeline runs, and m1/m3 kills. Independent verification is still required.

NOT DONE

- `ledger.py` remains J1-2.
- `scripts/decide-harvest` remains J1-3.
- No hook, task ledger, wiki, commit, push, PR, or outward action was performed.
- Independent adversarial verification remains pending.

Retro: nothing general to bake; implementation-specific discrepancies are recorded in the report.

Graft saved approximately 106,163 tokens this turn.
