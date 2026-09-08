# M2 report — S0-06 round 2

## Outcome

PROPOSAL ONLY — not independently accepted. The sandbox adversarial-verifier lane must grade the final worktree bytes.

NOT DONE (first-class): no pinned ai-memory checkout exists on this host. I did not build or run ai-memory, start an instance, seed scopes, capture PC evidence, mint an artifact, or touch the PC production tree. The ai-memory source derivations in M1 and VERIFY-M1 remain NOT re-verified here. Read contract 5 (Fubuki bounds / budget), the `memory_required` pre-dispatch check, D-2's conflicting ADR decision, and D-3's naming decision remain outside this lane.

## Scope and final byte identity

Verified source edits in this continuation:

- `proofs/S0-06/check_four_scope.py:116-138` adds the closed per-leg `EXPECTED_FILES` manifest and an `unexpected_file` reason.
- `proofs/S0-06/check_four_scope.py:490-502` defines `_check_expected_files`, which rejects every extra per-leg entry before semantic grading; `run` calls `_check_expected_files(root)` at `check_four_scope.py:515-525`.
- `tests/test_s0_06_four_scope.py:1228-1233` defines `test_unexpected_evidence_files_are_refused`, the V17 red/green oracle.
- `tasks/briefs/s0-06-support/VERIFY-M1-report.md` received only its trailing-whitespace correction from the predecessor patch; no semantic assertion was changed by this continuation.

Final SHA-256 identity:

- `check_four_scope.py` — `b02c9d3c05b264af0ef7c2577491079d6b2ffa2c6e0e123a0c3643a6ed40e730`
- `factory_memory.py` — `119fa34368dea98d23ad831998df61f6e0c195efa1deda0ac063c5f58c75e677`
- `test_s0_06_four_scope.py` — `440f72ba6a349748d35cdd79712d3cb257b1016183e7e6f981f68fb477964367`

## Premise audit

Verified against revision `246bec7` and current draft bytes:

- V18 was real before the draft fix. A repaired evidence bundle with hand-edited `confidence: NaN` returned rc 0 and `PASS`; this matches VERIFY-M1's recorded survivor.
- Final parser behavior is `check_four_scope.py:180-185`: `_loads` uses `json.loads(text, parse_constant=_reject_constant)`. The V18 final mutant returned rc 1 exactly: `leg: precedence evidence shape invalid (ValueError: non-RFC-8259 constant NaN)`.
- Final producer behavior is `factory_memory.py:165-192` and `factory_memory.py:462-484`: non-finite ranks are rejected and both JSON result sinks use `allow_nan=False`.
- C10 was real in the predecessor mutation audit: deleting the bindings `S_ISREG` guard caused directory input to raise `IsADirectoryError`, not `ValueError`; current guard is `factory_memory.py:116-139`. The isolated C10 directory mutant fails rc 1 at `test_a_bindings_table_that_is_not_a_regular_file_is_refused[dir]`; final bytes pass all dir/FIFO/symlink cases.
- V17 was the remaining verifier survivor: adding `denied/recall-real.json` to a repaired bundle returned rc 0 and `PASS`. It was a contradiction of the original brief's all-survivors-die requirement, not a harmless acceptance. The new closed manifest now refuses it at the exact named reason below.

Git history was checked with `scripts/why.sh`: `check_four_scope.run` originates at `380877b`; its stated limit was an absent live PC leg and no mint. GitNexus impact / detect-changes could not run because this worktree has no `.gitnexus/run.cjs`; that is an infrastructure limitation, not impact evidence.

## Red → green controls

| control | red evidence | final evidence |
|---|---|---|
| V17 extra sibling | before edit: rc 0, `PASS: S0-06 four-scope - 4/4 assertions…` | `test_unexpected_evidence_files_are_refused` → `1 passed in 0.42s`; exact rc 1 reason: `leg: unexpected evidence file denied/recall-real.json` |
| V18 NaN | pre-draft checker accepted hand-edited NaN, rc 0 | `test_evidence_carrying_a_non_rfc_8259_constant_is_refused` plus C10 three shapes → `4 passed in 0.26s` |
| C10 removed regular-file guard | isolated directory mutant fails rc 1 with `IsADirectoryError` | final dir/FIFO/symlink parameter set is included in the 170-test final suite |

No claim is based on a timestamp or on the last line of multi-line output: all checker-mutant runners required an exact one-line stdout result and exact process rc.

## Mutation evidence

Verified final mutation campaign, all deterministic and LLM-free:

- M01–M28: 28/28 expected outcomes. M01 deferred rc 2; M02–M28 each rc 1 with the named reason. The final artifact is `scratch/m1-mutants-final-fixed.out`; M16 now reports `precedence: raw scopes do not carry four distinct variants`, V17 is separately covered by the new oracle.
- V1–V20: 20/20 return rc 1 with a single named reason. V17 is now `leg: unexpected evidence file denied/recall-real.json`; V18 is the RFC-8259 `NaN` refusal.
- C1–C10 injected gate bugs: 10/10 killed. C1–C9 each ran the full module and returned rc 1; C10's only safe bounded killer was the directory member because deleting `S_ISREG` makes the FIFO test block. The isolated C10 mutant returns rc 1 and names the failed directory test. This is a deliberate bounded mutation method, not a full-suite timeout treated as evidence.

## Final deterministic runs

Verified on final bytes:

- `pytest tests/test_s0_06_four_scope.py -q -p no:randomly` with the pinned S0-01/S0-02 environment: `170 passed in 23.92s`, rc 0.
- Static-copy `scripts/lane_gate.sh -r 246bec7 … -n 2`: `RESULT: rev=246bec7ccc7d files=54 runs=2 identical=yes rc=0 summary="170 passed in 27.17s 170 passed in 26.99s"`.
- `bash -n` on `run_s0_06_legs.sh`, `start_ai_memory.sh`, and `collect_leg.sh`: rc 0.
- Python compile of checker, adapter, and seeder: rc 0.
- `git diff --check 246bec7`: rc 0.
- `ap_screen.py proofs/S0-06 proofs/S0-06/adapter proofs/S0-06/tools/pc`: 3 hits, classified: two `hashlib.sha256` derivations are the explicit write-path contract; the byte-identical recall claim is killed by M14. Test scan: 4 hits, all inverted safeguards or synthetic honeytoken mutations.

The first static-copy gate attempt was red, not discarded: its `-f` list omitted staged fixture additions required by the current checker, so the archive lacked `version_stdout` and yielded `65 failed, 105 passed`. The corrected 54-file gate above copied every staged fixture byte required by the new producer/checker contract and is the only final static-copy evidence.

## 18-class re-scan

Verified/inferred from final source and tests, using the M1 enumeration method:

| class | final result |
|---|---|
| 1 presence gates | named refusal / defer, M01–M28 exercised |
| 2 unsafe reads | S_ISREG guards; C10 plus M04/M05 |
| 3 lossy result reads | checker’s one-line contract exercised by hostile shapes and mutant runners |
| 4 negative acceptance | V and M controls include explicit positive counterparts |
| 5 substring/tail verdicts | exact rc plus one full stdout line in every mutant runner |
| 6 environment domains | documented PC-only limit; no PC execution |
| 7 lossy decodes | empty class, strict UTF-8 only |
| 8 broad catches | named failure/status paths; no `except Exception` except top-level exit-70 net |
| 9 waits/polls | one PC-only readiness loop, not executed |
| 10 skips/xfails | empty class |
| 11 world enumeration | NEW check is a fixed per-leg manifest, not a world scan |
| 12–18 | inherited M1 results; no new instances except V17’s manifest boundary |

## Deviations and discrepancies

- DEVIATION: the original brief asks for every lane/verifier mutant family. I ran M01–M28, V1–V20, and C1–C10. I did not rerun H1–H11, L1–L5, or G1–G5 as a fresh external matrix because their final code paths already run within the 170 deterministic tests and the final gate. This is incomplete relative to the literal brief and must be adversarially re-run by the verifier rather than silently inferred.
- DEVIATION: the full C10 FIFO-deletion suite was intentionally not awaited after it proved blocking behavior. The directory case is the deterministic bounded negative control; FIFO and symlink pass on final bytes in the final 170-test run.
- The PC live leg remains deliberately unrun. VERIFY-M1's PC preconditions, especially D-2, are unresolved.
- The worktree includes predecessor and sibling staged changes. This report claims only the continuation’s V17 checker/test additions and the evidence described above; no commit or push was made.

## Self-attack

1. **Manifest drift:** a real future runner output could add a legitimate file and be refused. Ruled down by deriving all names from `collect_leg.sh` and running the 54-file archive gate; residual risk remains for intentional future runner changes, which must update the manifest and test together.
2. **V17 may be a non-security metadata sibling:** it was still ungraded evidence under a proof bundle. The exact negative control proved the checker accepted it before and refuses it now. Residual risk is only policy choice, not unnoticed acceptance.
3. **Synthetic evidence may hide live-substrate incompatibility:** not ruled out. No real ai-memory process ran here; only static PC-script checks and recording/fixture stand-ins were possible. This is why the result remains a proposal and why no mint occurred.

## Handoff

Sandbox adversarial verification should start from final identities above, independently rerun H1–H11/L1–L5/G1–G5, inspect the V17 manifest against `collect_leg.sh`, and decide D-2 before any PC capture. No acceptance verdict is supplied by this lane.
