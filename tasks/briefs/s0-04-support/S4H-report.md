NOT built: F1/F2/F3/F6/F7 are outside this lane by design. Independent adversarial verification has not run; this build report is a proposal only.

FILE IDENTITY
- C4 `proofs/S0-04/check_compression.py`: `fa39bb78c7d589cc678af163075393244ec5ab7894e8a9917ac4af5363610981` (408 lines).
- T4 `tests/test_s0_04_compression.py`: `2085b90bdde03c1b605a8e3d61a06f178e122327e9001d04ecd9a7342b7a5404` (1026 lines).
- Final `git status --porcelain`: `M proofs/S0-04/check_compression.py`; `M tests/test_s0_04_compression.py`; generated-only `M proofs/S0-04/result.json`; report `?? tasks/briefs/s0-04-support/S4H-report.md`.

PREMISE — verified on an isolated d92bfcf archive. The current PIN suite was 74 tests, not the brief-stated 69.
- M4 delete C4 argv guard: `74 passed in 1.18s`.
- M5 delete C4 sent-header guard: `74 passed in 1.15s`.
- M15 delete C4 duplicated-config-header guard: `74 passed in 1.08s`.
- M17 delete C4 status-type guard: `74 passed in 1.12s`.
- F5 503 response with compliant compression header: `PASS: S0-04 compression-contract - 3 assertions over 3 legs`; `checker_rc=0`.

ITEM F5 — C4:264-269 (`response`)
- Added local `status`, retained the named non-int failure, then refuses non-2xx with `response-status-not-2xx: <status>` before parsing A2’s header.
- RED first against pre-fix archive plus final tests: `1 failed, 78 passed in 1.28s`; assertion: `assert 0 == 1` for status 503 in `test_response_status_must_be_2xx`.
- Green final focused cases: `5 passed in 0.34s` before the lower/upper-bound additions; final full suite evidence is below.
- Bound de-vacuity mutants: `< 5000` admits 503 and yields `1 failed in 0.23s`, `assert 0 == 1`; inverted predicate rejects 200 and yields `1 failed in 0.14s`, `assert 1 == 0`.
- Final tests pin 200 and 299 PASS, 503 exact failure, lower bound 199 and upper bound 300 failure, plus string `"200"` and boolean `True` exact `response-status-absent` at T4:301-331 (`test_response_status_must_be_2xx`, `test_response_status_requires_an_integer`).

ITEM F4 — C4:250-257 (`request`), C4:265-267 (`status`), C4:326-327 (`hits`)
- M4 killer T4:523-532 (`test_request_argv_is_required`) removes `argv`; final checker emits `failure_reason: off: request-argv-absent`.
  Scratch delete-mutant: `1 failed in 0.15s`; assertion: `assert 0 == 1`.
- M5 killer T4:535-551 (`test_fixture_compression_header_is_pinned_after_request_equivalence`) supplies a private self-consistent fixture and matching request with header `on`; final checker emits `failure_reason: off: sent-compression-header-value: on`.
  The original equivalence premise was false because `--fixtures-dir` permits a self-consistent alternate fixture. C4:252-253 documents this real reachability.
  Scratch delete-mutant: `1 failed in 0.15s`; assertion: `assert 0 == 1`.
- M15 killer T4:425-437 (`test_duplicated_config_header_is_refused`) supplies both header spellings; final checker emits `failure_reason: config: config-header-duplicated: 2 keys`.
  Scratch delete-mutant: `1 failed in 0.15s`; assertion: `assert 0 == 1`.
- M17 killer T4:321-331 (`test_response_status_requires_an_integer`) supplies status string `"200"` and boolean `True`; final checker uses `type(status) is not int` and emits `failure_reason: off: response-status-absent`.
  Scratch delete-mutant: `1 failed in 0.15s`; assertion expected `response-status-absent`, mutant instead exposed `malformed evidence: TypeError: '<=' not supported between instances of 'int' and 'str'`.

MUTATION TABLE
| mutant | final scratch mutation result | killer |
| M4 argv guard deleted | `1 failed in 0.15s`; `assert 0 == 1` | T4:523-532 `test_request_argv_is_required` |
| M5 sent-header guard deleted | `1 failed in 0.15s`; `assert 0 == 1` | T4:535-551 `test_fixture_compression_header_is_pinned_after_request_equivalence` |
| M15 duplicated-config guard deleted | `1 failed in 0.15s`; `assert 0 == 1` | T4:425-437 `test_duplicated_config_header_is_refused` |
| M17 status-type guard deleted | `1 failed in 0.15s`; expected exact reason absent, mutant yields TypeError | T4:321-331 `test_response_status_requires_an_integer` |

ATTESTED INPUTS
- `python3 scripts/proof-runner run --proof S0-04 --venue sandbox --root .` on final bytes: `proof_runner_rc=0`, `result_classification=execution_proof`, `result_run_legs=positive:0,negative:1`. It regenerated only `proofs/S0-04/result.json`, with `env_fingerprint: sandbox:fedora`; do not land this PC-generated artifact.
- `python3 scripts/validate-ledger integrity --root .` on final bytes: `S0-04 PRESENT`; `execution_proof numerator=7 denominator=9`; `validate_ledger_rc=0`.
- `git diff --stat -- proofs/S0-04/result.json proofs/ledger.json` after final proof runner: `proofs/S0-04/result.json | 16 ++++++++--------`; ledger unchanged.

FINAL GATES
- `python -m pytest -n 4 -q -p no:cacheprovider --basetemp ../scratch/bt/final-strict-type-1 tests/test_s0_04_compression.py`: `79 passed in 1.25s`.
- Same final bytes, `final-strict-type-2`: `79 passed in 1.24s`.
- `scripts/test_summary.sh tests/test_s0_04_compression.py` on final bytes: `pytest-summary: 79 passed in 2.86s`.
- Archive gate 1: `RESULT: rev=d92bfcfc8b85 files=2 deleted=0 runs=1 tests=2e5825a9019e identical=yes rc=0 summary="79 passed in 2.88s"`.
- Archive gate 2: `RESULT: rev=d92bfcfc8b85 files=2 deleted=0 runs=1 tests=2e5825a9019e identical=yes rc=0 summary="79 passed in 2.86s"`.
- `python -m pyflakes proofs/S0-04/check_compression.py tests/test_s0_04_compression.py` on final bytes: `pyflakes_strict_type_rc=0`.
- `python3 scripts/ap_screen.py proofs/S0-04/check_compression.py` on final bytes: `--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---`.
- `python3 scripts/ap_screen.py --tests tests/test_s0_04_compression.py` on final bytes: `--- TEST_SCREEN over 1 path(s): 3 hits over 1 files ---`; all three are pre-existing source-string hits at T4:905 in `test_runner_never_kills_by_name`; its `banned` tuple gives AF-AP-34 x2 and AF-AP-59 x1, screen rc 0; no new hit in this hunk.
- `git diff --check` on final bytes: rc 0.
- `python3 scripts/report_lint.py tasks/briefs/s0-04-support/S4H-report.md --root . --map C4=proofs/S0-04/check_compression.py --map T4=tests/test_s0_04_compression.py --min-refs 10`: `report_lint: 15 refs — OK 15, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.

SELF-ATTACK
- Status type mutation could produce an incidental TypeError rather than exercise the type guard. Ruled out: M17 delete-mutant runs to the comparison and the test fails specifically because `response-status-absent` is absent; final emits exact named reason.
- A status bound could be too broad or inverted. Ruled out: 200 and 299 pass, 503/199/300 fail exact reason; a `< 5000` mutant yields `1 failed`, `assert 0 == 1`, and the inverted predicate yields `1 failed`, `assert 1 == 0`.
- M5 could remain redundant. Ruled out: alternate `--fixtures-dir` permits request and fixture to agree on `on`; the real guard is reachable and its delete-mutant passes the hostile bundle, while the final test fails it exact.

DISCREPANCIES
- Brief says T4 had 69 tests; isolated PIN and final suite measured 74 then 79. Counts above are tool output, not hand-derived.
- `gh issue view` was blocked by local deny policy; public issue #7 was read anonymously at GitHub.
- First red-archive creation omitted `mkdir -p` for the destination and tar failed; no source files changed. The retry created the destination and reproduced the expected red.
- Initial bound mutation `< 400` did not admit 503, so it did not test de-vacuity. The corrected `< 5000` mutant admitted 503 and went red as recorded above.
- Proof runner rewrote `proofs/S0-04/result.json` only. Its recorded venue is `sandbox:fedora`, not the PIN’s `sandbox:vm`; it is declared and must be regenerated by the coordinator on the landing sandbox. `proofs/ledger.json` did not change.
- A self-attack found Python’s `bool` is an `int` subclass: a status of `True` initially took the 2xx-bound path. C4 now uses `type(status) is not int`; T4 proves both `"200"` and `True` emit `response-status-absent`.
- GitNexus `impact` before edit found `check_bundle -> main -> check_compression.py` (LOW, 3 nodes) but says index 439 commits stale. Final `detect-changes` reported 3 files, 10 symbols, MEDIUM (the third is the report); the production change remains C4 + T4. The lane pack records code-review-graph unavailable and ripwire’s subprocess blind spot; direct CLI tests and archive gates exercised the real checker process.

NOT-DONE
- F1 config-leg mirror, F3 offline provenance, F6 Hermes-side capture are EAT/document items, not touched.
- F2 no-header live capture and F7 capture-provenance refresh require a PC re-capture, not run.
- No live capture, OmniRoute request, Git write, commit, push, or attestation artifact landing occurred.
- Independent sandbox adversarial verification remains required.

GATE RECOMMENDATION: MERGE-READY-WITH-FOLLOWUPS (proposal only). The deterministic build evidence supports the scoped F4/F5 change. Coordinator must remove/recreate the PC-generated result artifact, regenerate the attestation on the landing sandbox, and send the diff plus this contract evidence to the independent adversarial verifier before any acceptance decision.

retro: status fields from JSON require `type(x) is int`, not `isinstance(x, int)`, when booleans are invalid; the local S0 proof checker is fixed and the sibling proof checkers are outside this lane boundary.

graft saved ~12,217 tokens this turn.
