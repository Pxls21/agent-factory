# O4 — S0-03 round 4 implementation report

PIN: `d84a90a6bb1c73859db5ab9f86814dc572ca6f17`
Lane: O4, PC Hermes `code-implementer`
Measured: `2026-09-17T15:12:06Z`

GATE RECOMMENDATION: MERGE-READY for sandbox-side adversarial verification. This is a build-lane proposal, not a gate verdict.

## NOT done

- No live direct, Hermes, or negative leg ran.
- No request was sent to OmniRoute or any model endpoint.
- No owner key, database, live profile, or bridge secret was read.
- No result artifact was minted and no `EXPIRED` state was changed. The live captures, EXPIRED→result flip, remint, and owner re-sign remain coordinator/owner work.
- FU3 is unchanged by design: `check_roundtrip` grades the exact required execute start, but a second non-exact execute start remains accepted. This is a declared limit for a later contract decision.

## Outcome

VERIFIED in the static-copy gate:

- `Authorization` and `Proxy-Authorization` are credential names regardless of value scheme (`C:167-178`).
- The checker grades each recorded `row_counts` value against the exported rows it consumes (`C:460-477`, wired at `C:863`).
- The collector's lexical SQL query is a superset for RFC3339 offset-bearing rows, while its aware-instant check stays authoritative (`K:121-149`).
- Tests prove the exact name matcher (`test_credential_name_recognises_authorization_header_identity`, `T:147-150`), four hostile header profiles (`test_credential_screen_rejects_authorization_header_by_identity`, `T:449-469`), the provider-level `key_env` exemption (`T:440-447`, `T:502-508`), count mismatch rejection (`test_row_counts_must_match_the_exported_rows_for_each_query`, `T:1177-1186`) and count-positive controls (`test_row_counts_match_the_exported_rows_in_the_passing_bundle`, `T:1199-1205`), and real sqlite rows carrying `+14:00` and `-12:00` offsets (`test_collect_leg_coarse_sql_bound_keeps_offset_rows_for_exact_filter`, `T:1843-1867`).

## Premise reproduction and red-before

VERIFIED at the PIN:

- The name segment set had `AUTH` but not `AUTHORIZATION`. Therefore `Authorization` remained one unmatched segment; Token and opaque values also evaded the independent Bearer/Basic/sk prefix screen.
- The collector emitted `row_counts`, but the checker did not consume them.
- A real sqlite run through the PIN collector dropped two rows whose instants were inside the UTC window: `2026-09-08T14:00:02+14:00` and `2026-09-07T12:00:02-12:00`. The old SQL compared their original text to a UTC-prefix interval before the exact instant filter could act.

RED before was run from `git archive d84a90a` with only the final tests copied over it:

```text
5 failed, 4 passed in 2.35s
RED_BEFORE_RC=1
```

The five failures were exact and expected:

1. A Token-scheme `Authorization` header returned checker rc 0 instead of rc 1.
2. Opaque `Authorization` returned checker rc 0 instead of rc 1.
3. Opaque `Proxy-Authorization` returned checker rc 0 instead of rc 1.
4. `row_counts['hermes'] = 0` over one exported Hermes row returned checker rc 0 instead of rc 1.
5. The collector exported zero Hermes rows and exited 1 for the two in-window offset rows.

An `Authorization` header using the Basic scheme passed its old-tree negative control because the existing value-prefix check already rejected it. The `key_env` and valid-count controls also passed at the PIN. These are mechanism-positive controls, not missing red cases.

## Changes

### Credential header identity

- Added `AUTHORIZATION` to `CREDENTIAL_SEGMENTS` at `C:178`.
- Kept the existing recursive value-prefix check and provider-level `key_env` exemption unchanged.
- Added direct identity assertions in `test_credential_name_recognises_authorization_header_identity` at `T:147-150`.
- Added checker-level `test_credential_screen_rejects_authorization_header_by_identity` hostile profiles for Token, opaque, Basic, and Proxy-Authorization values at `T:449-469`.
- Retained the positive `key_env: OMNIROUTE_API_KEY` profile controls in `test_credential_screen_allows_only_the_provider_key_env_name` at `T:440-447` and `test_conjunct_v_still_accepts_the_key_env_NAME` at `T:502-508`.

### row_counts grading

- Added `check_row_counts` at `C:460-477`. It compares direct and Hermes counts separately to the exact exported list consumed by `_rows_by_leg`, and requires strict integers.
- Wired `check_row_counts` before `check_identity_route` at `C:863-864`.
- Added `test_row_counts_must_match_the_exported_rows_for_each_query` at `T:1177-1186` and `test_row_counts_match_the_exported_rows_in_the_passing_bundle` at `T:1199-1205`.
- Added `test_row_counts_requires_strict_integers` at `T:1189-1197`; booleans, strings, and floats cannot masquerade as integer counts.
- Updated the `add_row` ambiguity mutant to increment its count at `T:1161-1167`, and the `shadow` mutant at `T:1211-1215`. This preserves their intended downstream identity/uniqueness oracle instead of making them accidental count mutants.

### SQL-bound superset

- Widened `sql_start` and `sql_end` from seconds to one full UTC day on each side at `K:121-128`.
- Proof: RFC3339 numeric offsets range through `23:59`. For an exact in-window instant, its local timestamp differs from UTC by less than one day. Therefore its local date-time prefix cannot sort outside the UTC interval widened by one day on each side. The exact `start <= stamp <= end` condition at `K:147-149` still removes rows outside the real window.
- Added `test_collect_leg_coarse_sql_bound_keeps_offset_rows_for_exact_filter` at `T:1843-1867`. Its lexical assertions prove both rows lie outside the old coarse range, then require both to survive collection and appear in `row_counts`.

## Named mutant table

| Mutant | Killer | Observed result |
|---|---|---|
| Remove `AUTHORIZATION` from the segment set | `test_credential_name_recognises_authorization_header_identity` (`T:147-150`) and `test_credential_screen_rejects_authorization_header_by_identity` (`T:449-469`) | Token, opaque, and Proxy-Authorization hostile profiles return rc 0; killed. |
| Skip `check_row_counts` in `check_bundle` | `test_row_counts_must_match_the_exported_rows_for_each_query` (`T:1177-1186`) | Mismatched count returns rc 0; killed. |
| Restore old seconds-wide SQL bound | `test_collect_leg_coarse_sql_bound_keeps_offset_rows_for_exact_filter` (`T:1843-1867`) | Collector exports no Hermes row and exits 1; killed. |
| Over-broadly reject provider `key_env` | `test_credential_screen_allows_only_the_provider_key_env_name` (`T:440-447`) and `test_conjunct_v_still_accepts_the_key_env_NAME` (`T:502-508`) | Passing bundle becomes RED; positive controls kill it. |
| Rewrite the exact instant filter as lexical-only | Existing F-14 test plus `test_collect_leg_coarse_sql_bound_keeps_offset_rows_for_exact_filter` (`T:1843-1867`) | Fractional/offset traps enter or leave the set incorrectly; killed by real sqlite fixtures. |

## Verification

GREEN after:

```text
186 passed in 28.62s
```

Final static-copy gate, two bit-count-identical runs:

```text
RESULT: rev=d84a90a6bb1c files=3 deleted=0 runs=2 tests=89f05701192e identical=yes rc=0 summary="254 passed in 43.50s 254 passed in 42.79s"
```

Static checks:

```text
FINAL_STATIC pyflakes=0 bash_n=0 ap_checker=0 ap_tests=0
```

AP screen detail:

```text
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---
--- TEST_SCREEN over 1 path(s): 6 hits over 1 files ---
AF-AP-34: 3
AF-AP-80: 2
AF-AP-59: 1
```

Classification: all six test-screen hits are pre-existing incident-name references or assertions: `test_pc_tools_never_name_match_processes` (`T:920-921`); `pc_mention.sh` in `RUNNER.read_text()` (`T:1629`); and `current-framedir` in `PC_MENTION.read_text()` (`T:1638`). No O4 hunk matched.

Code-intelligence after edit: GitNexus `detect-changes` saw 3 files, 11 symbols, 4 affected processes, risk `medium`. Its clone index did not resolve the new function accurately. Ripwire independently found one caller for `check_row_counts`: `check_bundle`. Ripwire cannot model the collector's subprocess test edge.

## File identity — final bytes

- `proofs/S0-03/check_omniroute_roundtrip.py` — 894 lines — git blob `b99f18cafbce2fde75c513457e1988aebcf5b0fa` — SHA-256 `5cf11fe493a237ac40565b989b85aef81d5e312813844ccd8d7230688cd2b367`
- `proofs/S0-03/tools/pc/collect_leg.sh` — 186 lines — git blob `b159927241bfce1d3f2842ae36e946d162161914` — SHA-256 `491b4d4e7ef89ffe0c9104a4ab9b527cdb9b0a858b369f68524f0c5609715769`
- `tests/test_s0_03_omniroute.py` — 2021 lines — git blob `d513bdb11bab2be7d6b69a4903aa05619bf6b32d` — SHA-256 `6a33eddca902605d6c17188483b4a0efdbfdd990f984020aa6f7036719f42407`

## Evidence tiers

VERIFIED:

- All source and test claims above were measured from the final bytes.
- The red controls failed against the PIN for the intended mechanisms.
- The final four-file gate passed twice with identical count vectors.
- `git diff --check`, pyflakes, `bash -n`, and both AP screens returned rc 0.

INFERRED:

- The one-day coarse range is a complete lexical superset under the RFC3339 offset domain accepted by Python's aware parser. The real sqlite regression exercises both positive and negative large offsets; it does not enumerate every legal offset.

ASSUMED:

- OmniRoute continues to store RFC3339 timestamp text in `call_logs.timestamp`, as required by the collector/checker contract and existing fixtures.

## Self-attack

1. The header tests might pass by the old value-prefix branch, not by name. Ruled out with Token and opaque values plus direct `is_credential_name` assertions in `test_credential_name_recognises_authorization_header_identity` (`T:147-150`) and hostile checker profiles in `test_credential_screen_rejects_authorization_header_by_identity` (`T:449-469`).
2. The count check might grade a reconstructed set different from the one route identity consumes. Ruled out because `check_row_counts` and `check_identity_route` both call `_rows_by_leg` on the same loaded `bundle["requests"]` object (`C:470-477`, `C:863-864`).
3. Widening SQL might admit false rows. The coarse query may fetch extra rows by design, but the exact `start <= stamp <= end` filter remains at `K:147-149`; existing fractional-precision tests and the new offset regression passed.

## Discrepancies

- Final report lint (required command included `--rev d84a90a`): `report_lint: 41 refs — OK 8, NEAR 0, MISS 33, UNCHECKABLE 0, UNRESOLVED 0 (at d84a90a)`. That mode grades final-byte references against the pre-edit PIN. After the bounded hint pass, the mechanically useful worktree run was `report_lint: 41 refs — OK 38, NEAR 3, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.
- The first lane-gate invocation inherited `/usr/bin/python3` and deterministically returned `33 failed, 217 passed` twice because `rfc3339_validator` was unavailable there. Per `VENUE-MAP`, prepending `/home/rocco/venv-agent-factory/bin` produced the final two-run green. This was an invocation-environment error, not a source failure.
- The brief named `tasks/briefs/s0-03-support/VERIFY-O3-report.md`, but the PIN tree exposed the graded report under its PC-harvest path; the supplied O4 pack and O3 report carried the finding evidence. No design was changed.
- A fresh `lane_context.sh` invocation first failed rc 64 because repeated `-s` flags are required; after correction it wrote over the supplied pack. The supplied pack was restored byte-for-byte (`git hash-object` equals `d84a90a:` blob `0294ccbde15b50df8d7b785a3fa0606a6296e4f0`). No out-of-scope file remains changed.
- Ripwire `exercises` was invoked with symbol/non-test selectors and returned rc 1 with corrective hints. `callers check_row_counts` succeeded and identified `check_bundle`; subprocess coverage is verified by pytest instead.

## Reasoning record

- Rejected alternative: converting every timestamp in SQL was not used because SQLite's schema stores timestamp text and the exact aware-instant Python filter already exists. A bounded coarse superset is smaller and preserves the authoritative filter.
- Ordering rationale: `row_counts` is checked after direct stream/model checks and before identity-route consumption. This preserves the existing first-failure contract for direct evidence while ensuring the exported set is internally self-consistent before route grading.
- Primary source: final checker, collector, and real-sqlite tests cited above; prior-round verifier finding supplied in the O4 pack.
- Disjoint hunks: credential segment + checker count assertion; collector bound; targeted checker/collector tests only.

Retro: no new product defect beyond the three briefed findings. The only workflow wrinkle was the interpreter-path gate invocation; it is recorded above. No skill update was made from this lane.
