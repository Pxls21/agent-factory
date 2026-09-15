# GOV1 implementation report

> **COORDINATOR AMENDMENT at landing (2026-09-15 15:0xZ) — a hidden test input, fixed before the landing (AF-AP-81).**
> The sandbox static-copy gate, run bare on the PIN, read `12 failed, 17 passed` twice (`ModuleNotFoundError: No module
> named 'fubuki_os'` / `'lint'`): the packet and bounds tests reached the pinned upstream only through the lane shell's
> PYTHONPATH, so the `29 passed` above was green on an undeclared input. Fix: `verify_pinned_fubuki` inserts BOTH upstream
> import roots once — the loop `for entry in (str(root), str(root / "src"))` at `src/agent_factory/governance/pin.py:77-79`
> (`lint/persona_lint.py` lives beside `src/`, not inside it); the packet and bounds suites pin through the production
> function — the autouse fixture `pinned_fubuki` at `tests/test_governance_packet.py:33-42`,
> and the same fixture `pinned_fubuki` at `tests/test_governance_bounds.py:18-23`;
> the behavioral test `test_pinned_upstream_modules_resolve_from_the_pinned_checkout` at `tests/test_governance_pin.py:47-61`
> imports both modules and locates their files under the pinned root; the driver's
> PYTHONPATH is stripped to the repo's `src` (an ambient upstream path had masked the root-insertion mutant, now the row
> `pin-skips-root-insert` at `tasks/briefs/stage3-governance-support/mutants.sh:115-117`). Sandbox, bare, after the fix:
> `RESULT: rev=9376760edfda files=28 deleted=0 runs=2 tests=fbbd35151dcc identical=yes rc=0 summary="30 passed in 0.34s 30 passed in 0.33s"`,
> `EXPECTED=12 KILLED=12 SURVIVED=0 INVALID=0 CONTROL=1`, `tests/test_sentrux_review.py` `8 passed` before and after the pyproject.
> The 27-row FILE IDENTITY table below was verified byte-for-byte against the applied patch (27/27) before these edits.
> The DISCREPANCY (no review field in the pinned upstream) stands and is GOV2's first item: the reviewed bit comes from a
> first-party review record keyed by the governance hash, never from a fubuki field. `scripts/fubuki_pin_sync.sh` now
> provisions the declared inputs on every venue.

STATUS: PROPOSAL. The production code and deterministic tests are built and self-validated. This build lane cannot independently accept its own work. A separate sandbox adversarial-verifier must grade it.

## NOT done

- The projection is NOT wired into a Hermes session. Buzz/ACP/Hermes spine work still must bind `session.governance_hash` after S0-01/S0-03.
- `load_packet` has no success path against pinned fubuki-os because that upstream packet has no review/status field. It fails closed with `fubuki-packet-unreviewed`. No reviewed bit was fabricated.
- The audit sink is a local JSONL file. It does not send to OpenObserve.
- This lane did not commit, push, mint a proof, edit the ledger, or issue a gate verdict.

## Grounding and premise

VERIFIED

- PIN: `9376760edfda16a686a7749dbd9a8d7889dd5103`.
- The one permitted clone produced fubuki-os HEAD `7375e56d6a5dc857bfd43ceccbc09bbc817d575a`, matching `upstream.lock.yaml`.
- The S0-07 checker printed `PASS`, rc 0. Its corrected rule `_correct_lint_exit` gives violations priority over review findings (`C:27-34`). The upstream bug is reproduced by `upstream_rc` in the ordered lint call (`C:62-73`).
- Fubuki compiles through `compile_packet` at pinned `src/fubuki_os/compiler/compiler.py:32-134`; canonicalization is `canonical_json` at pinned `src/fubuki_os/release/hashing.py:39-52`; `hash_obj` at pinned line 57 hashes canonical bytes but returns a `sha256:`-prefixed value.
- Fubuki's `check_bound_decision_join` demonstrates `BoundDecision` values without payload (`C:79-132`). Pinned `evaluate_records` is at `src/fubuki_os/memory/bounds.py:91-98`; `BoundDecision` fields are at `src/fubuki_os/memory/models.py:69-93`.

DISCREPANCY

- Pinned `Manifest`, `ValidatedPackage`, `CompileRequest`, and compiled packet expose no review, approval, or certification field. A live validated-package probe printed `HAS_REVIEW_STATUS []`. The brief explicitly says absence means NOT reviewed, so `load_packet` refuses readiness. A positive readiness fixture would contradict the measured upstream contract.

## Implementation by item

1. Pin boundary

- `verify_pinned_fubuki` reads the lock, requires `src/fubuki_os`, compares exact HEAD, refuses a dirty tree, and inserts pinned `src` once (`src/agent_factory/governance/pin.py:57-76`).
- Negative controls call `test_other_commit_refuses_by_name`, `test_dirty_checkout_refuses_by_name`, `test_missing_source_refuses_before_git`, and `test_invalid_lock_refuses` (`tests/test_governance_pin.py:44-66`).

2. Packet boundary

- `lint_sources` calls pinned `persona_lint`, orders the fixture as review then violations, and applies `_correct_lint_exit` with violation-first status (`P:27-34`, `P:59-78`).
- `compile_canonical` calls Fubuki loader, validator, compiler, and `canonical_json` (`P:108-124`).
- `governance_hash` is exact, unprefixed `sha256(canonical_bytes)` because the session invariant names that representation (`P:127-131`).
- `test_lint_exit_semantics`, `test_compile_is_canonical_and_hash_is_exact_sha256`, and `test_each_source_byte_changes_hash` cover determinism, key-order invariance, exact independent hashlib comparison, and one-byte mutation of every declared source (`tests/test_governance_packet.py:44-88`).
- Enumerated source sweep: `compile-request.json`, `core/doctrine.md`, `core/persona.md`, `examples/gold.jsonl`, `modes/strategy.md`.

3. Immutable projection

- `project` verifies packet identity and review, projects `resident_kernel`, `mode_manifest`, package/core identity, mode/register, hard constraints, and output contract (`J:33-57`).
- It deliberately excludes state, bounded context, examples, memory cutoff, source pointers, and adapter notes. Nested dictionaries become `MappingProxyType`; lists become tuples (`J:25-30`).
- `write_projection` uses `O_CREAT|O_EXCL|O_NOFOLLOW|O_NONBLOCK`; `read_projection` accepts only a regular file and checks both envelope and expected governance hash (`J:86-152`).
- Tests cover deep immutability, round trip, one-byte tampering, wrong hash, existing file, symlink flags, FIFO refusal, and mutated packet identity (`tests/test_governance_projection.py:40-128`).

4. BoundDecision join

- `bound_records` calls pinned `evaluate_records`, joins only by `record_id`, returns original source object identities, refuses missing/duplicate decisions, retains reasons/rule, and emits one event per decision (`B:34-111`).
- A planted decision `payload` cannot enter output (`tests/test_governance_bounds.py:54-68`). `test_bound_join_refuses_decision_without_source` rejects a foreign id (`tests/test_governance_bounds.py:71-83`).

5. Audit envelope seed

- Frozen `Event` requires non-empty `reason` and all common identity fields. `JsonlSink` uses append, no-follow, nonblocking open and rejects non-regular sinks (`src/agent_factory/audit/events.py:24-88`).
- Round-trip, required-reason, symlink, and bounded FIFO controls are in `tests/test_audit_events.py:25-60`.

6. Mutation driver

- Driver performs `py_compile`, collect-only, and a real green control before mutants.
- Final output:
  `EXPECTED=11 KILLED=11 SURVIVED=0 INVALID=0 CONTROL=1`
- It kills the nine required rows plus two security rows: projection symlink-follow and audit symlink-follow.

7. Mechanical gates

- Focused set: `5 files set=fbbd35151dcc`.
- Run 1: `pytest-summary: 29 passed in 0.86s`; `pytest-exit: 0`.
- Run 2: `pytest-summary: 29 passed in 1.08s`; `pytest-exit: 0`.
- Archive gate: `RESULT: rev=9376760edfda files=27 deleted=0 runs=2 tests=fbbd35151dcc identical=yes rc=0 summary="29 passed in 0.47s 29 passed in 0.42s"`.
- `python -m pyflakes ...`: `PYFLAKES_RC=0`.
- Shell syntax: `BASH_N_RC=0`.
- Repo-root import resolves `src/agent_factory/governance/__init__.py`.
- Throwaway editable venv import: `EDITABLE_IMPORT_RC=0`.
- Existing test set: `1 files set=1df3420b4c03`.
- Before: `pytest-summary: 4 passed, 4 skipped in 0.19s`; after: `pytest-summary: 4 passed, 4 skipped in 0.09s`. Counts match. Skips state that the pinned sentrux binary is absent in this venue.
- `git diff --check`: rc 0 at `2026-09-15T14:26:16Z`.
- Report lint: `report_lint: 19 refs — OK 19, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.
- GitNexus after reindex: `Changes: 30 files, 135 symbols`, `Affected processes: 3`, `Risk level: medium`; affected flows are the three new `load_packet` paths.

## Test-history findings

- Initial focused run: `1 failed, 28 passed in 2.90s`. Linux refused nonblocking FIFO open with `audit-sink-open-refused: [Errno 6] No such device or address`, before the post-open regular-file check. The final test allows either exact fail-closed branch and remains bounded.
- Initial mutation run falsely showed all mutants surviving because pytest put the repository root ahead of mutant `PYTHONPATH`. The driver now copies each focused test into its scratch mutant root and uses importlib mode. This is the fixed anti-pattern: a mutation gate must prove which implementation it imported.
- Initial throwaway import failed with `ModuleNotFoundError: No module named 'yaml'`. `PyYAML>=6.0` is now declared in `pyproject.toml`; the throwaway proof installed that declared dependency and imported from outside the repository.

## Anti-pattern screen classification

- `AF-AP-40` hits are RUN-class path type checks that enforce source and special-file boundaries, not reachability claims.
- `AP-32` hits are RUN-class digest computation and independent digest assertions required by the governance-hash contract.
- `AP-1` hits are TEST-only reads of the two explicit test-shim inputs. No library code reads `os.environ`.
- Driver hash hits are mutation strings, not production hashing shortcuts.

## FILE IDENTITY

- `0f13ca663326296691a51c2d7362ef9ebaa48b5b6da5c31fb1d6a9725442aa91`  `pyproject.toml`  15 lines
- `18f0fd6e7d7a39f0bd7ce70a1e7d20ac48005902914771f4817d298bf1cd26a9`  `src/agent_factory/__init__.py`  1 line
- `ed2f6d1837dcd0ffc25bc3bc0aa85fa9fc831dee5742977f55c80772a5014c44`  `src/agent_factory/governance/__init__.py`  25 lines
- `9c897b8cc0e1d6de410764ef3efb55b7e3e48cf4456c7d51c7b2cf1ffae69219`  `src/agent_factory/governance/pin.py`  76 lines
- `6a27e2b7ddb1e9cbbc29c2299eb49f76f88f5347ebcd90492f0499e1d1bf8278`  `src/agent_factory/governance/packet.py`  154 lines
- `bad2491b90297df4d1a39b9282dbead283783e5bf3db7b0cffbff5819d5f62bf`  `src/agent_factory/governance/projection.py`  152 lines
- `aca388e7e8046dfc7da4e740103e31dcd1779e3052658200cfda40328462a0d9`  `src/agent_factory/governance/bounds.py`  111 lines
- `6cb3f6878657a95eebed2b637c799973ebc5ddf016caab28046f9fc7ee9a2124`  `src/agent_factory/audit/__init__.py`  5 lines
- `52215d4cd97158cac77e2f4a7e251337f7fe59ba59cf6170924ae58c0dea3339`  `src/agent_factory/audit/events.py`  88 lines
- `c8aba4068ea90bd0d64f689cb9616e0dc218563ad0b379e2cd8fdc90d0080ecd`  `tests/test_governance_packet.py`  98 lines
- `54187dbb663d6882b820780af5c78c123110e6c1964ea9c452fb9df03861e2d1`  `tests/test_governance_projection.py`  128 lines
- `42143677baec68f91076d6159e73ec6b4c7dbad72a91ccae85e97817d0f68314`  `tests/test_governance_bounds.py`  89 lines
- `a7d934c4210505bcd0e6f8687e083d4e792903fd64b7413ea32dd66e10d20f50`  `tests/test_governance_pin.py`  66 lines
- `4edaa61df009bdcb4e1e8e4af4785911b31a5bc18750999c77120fc3c8bd0693`  `tests/test_audit_events.py`  60 lines
- `41c9f100fbf1856186d75d7394593337707129e22d9d611b01a4900a0b5d17f2`  `tasks/briefs/stage3-governance-support/mutants.sh`  115 lines
- Fixture identities: `clean.txt` `793cf00d...` 1; `review-only.txt` `2d8dddda...` 1; `violation.txt` `b848ed5f...` 1; `ordered-review-then-violation.txt` `15c6130b...` 2; `compile-request.json` `5a10d66e...` 14; `persona.package.json` `2b1dff17...` 49; `core/persona.md` `36996eeb...` 3; `core/doctrine.md` `23fa46e0...` 3; `modes/strategy.md` `1c8246c5...` 3; `examples/gold.jsonl` `62e46b80...` 1.
- Edited setup identities: `scripts/setup.sh` `ed26115a...` 360 lines; `harness-ports/bin/pc-setup.sh` `777533e7...` 128 lines.

## Self-attack

1. Wrong upstream code might load. Ruled out by exact lock/HEAD comparison, dirty-tree refusal, missing-source refusal, one-time path insertion, and a clean alternate-commit negative control.
2. A green could survive while hashing or joins use the wrong substrate. Ruled out by independent hashlib comparison, full source mutation sweep, source-object identity assertion, planted decision payload, foreign-id refusal, and killed focused mutants.
3. File boundaries might block or follow attacker-controlled paths. Ruled out by nonblocking FIFO tests, no-follow flag observation, unchanged symlink targets, regular-file checks, and two dedicated symlink-follow mutants.

## Evidence tiers

- VERIFIED: all command results and source contracts quoted above were measured in this lane.
- INFERRED: none used for acceptance claims.
- ASSUMED: sandbox adversarial verification will use the same pinned fubuki-os commit and declared test inputs.

## Handoff

- Rejected alternative: inventing `reviewed=True` from package validation. That would create a hollow readiness green because integrity validation is not human review.
- Ordering rationale: verify pin before import; lint before compile; canonicalize before hash; check review before projection; bounds before any packet memory context; audit each decision at the join.
- Proposal requires separate `contract-gate` and adversarial-verifier grading. No self-acceptance.
