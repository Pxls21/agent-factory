# VERIFY-S198A — independent adversarial verification

STATUS: COMPLETE. Only fake credential-shaped values were used. No real transcript, state database, or Hermes profile was read.

## 1. Premise and production path

SOLID. At HEAD `750699a`, the measured blobs are S `37d94bd61556`, T `12dbaae6d0da`, P `04326ece5b7a`, P-test `0d7893bf5d2e`, and qwen reader `cd8763d0e3b3`; pre-S198A S at `9801fb5` is `a47e0e5861c9`. `git diff --stat 5415c2a 750699a -- S T harness-ports | wc -l` returned `0`; the contract premise holds. The test set is `2 files set=4e81d5d61609`. The accepted shortest-head grammar is in `_WORD` and `_HEAD` at `S:32` and `S:33`; the changed credential matcher `re.compile` begins at `S:68` with `_NAME`.

SOLID. Reachability through both requested consumers is present: sandbox `export()` calls `scrub()` before its cap at `S:116-123`; P imports S by path in `_scrub()` at `P:26-30`, then applies it before its cap at `P:36-41`. The direct export test builds synthetic JSONL entries in `_entry` at `T:33-34`; P's test creates its synthetic state database in `def _db` at `P-test:21-37`. Ripwire lists P `_body` and qwen `_scrub_messages` as additional callers. GitNexus reports the clone index stale by 832 commits; its exact `scrub` upstream map lists S `export`→`main`, but not the path-import P. This is an advisory mapping limitation, not a contract mismatch.

SOLID. Fresh gates, run twice: `python -m pytest -n 8 -q -p no:cacheprovider --basetemp ../scratch/bt/run1|run2 tests/test_transcript_export.py harness-ports/tests/test_hermes_session_export.py` returned `72 passed in 2.49s` and `72 passed in 3.83s`. The set summary separately returned `72 passed in 6.64s`; P's standalone script returned `15 checks passed`; qwen's reader script returned `4 tests passed`. P contains no pytest collection, so its direct script is required and was run. The relevant existing `CHAINED` and floor controls are at `T:228-252`, `T:276-281` with `LATER_RULES`, and `T:318-345`.

## 2. New chained-shape and extension attacks

SOLID. Independent scratch runner `scratch/verify_s198a.py` exercised 48 fake-only boundary inputs through both S versions. The new S exposed no secret byte that PIN hid: `pin_hid_new_showed=0`. It covered tabs and CRLF, `:=`, `==`, `=>`, decoded JSON quote placement, non-bridge and bridge query strings, three mixed-case heads, base64-tail `_key`, the rare `X-Agent-Token`, non-ASCII flank characters, and non-breaking spaces; all new-survivor rows below are PIN-equivalent pre-existing shapes.

SOLID. X1 three boundaries passed: tab after `Bearer`, a 7-character following token, and `Bearer` glued to a value start. X2 passed two- and three-Bearer chains plus Bearer→bridge. X3 passed `&`, comma/semicolon quote-parenthesis, and link-path head chains. X4 passed `_key`/`-key` prefixes 0, 1, 7, and 8, plus upper-case. No planted value byte survived in the new output for any valid shape.

SOLID. Floor controls: seven ordinary English/code lines retained their exact PIN output (`prose_changed=[]`). Three formerly whole-run secret pieces, including 1 and 5 bytes before an in-run head and a 7-byte in-run value, all remained redacted in new S.

## 3. R-1 boundary finding

FOLLOW-UP F1, SOLID. The declared R-1 residue permits a shortest-form head inside the prior value: at most word, optional one quote, whitespace, and separator. The real consumer leaks the following value when that head has two quote characters (or a mixed/backslash quote) before its separator. This follows from a one-quote-only `_HEAD` class at `S:33` and the stop logic used by `_VALUE` at `S:44-46`. Reproducer, all fake:

```
password=QZ94JQ6XZ94JQ6XZtoken"" = XZ94JQ6XZ94JQ6XZ94
```

PIN and new S both produce:

```
password=<redacted>"" = XZ94JQ6XZ94JQ6XZ94
```

The sandbox CLI writes 18 surviving fake bytes under both versions; the PC P CLI writes the same 18 bytes under both versions. Extra shapes `token'' =`, `token"' =`, and `token\" =` behave identically. This is outside the declared R-1 byte shape, and it is a meaningful exposure. It does not satisfy the contract-gate blocker predicate: it is pre-existing at `9801fb5`, rather than “a secret byte the PIN hid is shown” by S198A; therefore it is a FOLLOW-UP, not an S198A blocker. Suggested fix: future scrubber increment should define and test malformed/multiple quote syntax explicitly, without widening the S198A contract retrospectively.

INFO. `API_KEYé=<fake>` also leaves its value in PIN and new S. `_NAME` only permits ASCII separators/name boundaries. It is pre-existing and outside the accepted S198A changes; record with F1 as a follow-up, not a blocker.

## 4. Independent differential and real CLIs

SOLID. An independent seeded generator (`seed=4815162342`, 50,000 inputs, 124,907 planted fake assignment values, own templates/alphabet) measured: PIN output retained 323,024 planted bytes; new output retained 0; `pin_hid_new_showed=0`. The generator covered assignment names, quotes, `=`, `:`, tab/CRLF spacing, joins, Bearer and bridge-link prefixes. No exception was made for R-1 because generated value alphabet cannot spell a head. The production `def scrub` function itself applies each final pattern at `S:85-88`.

SOLID. Both real production CLIs consumed a three-chain fake fixture. Sandbox exporter: PIN `rc=0`, 17 planted bytes survived; new `rc=0`, 0. PC state-db exporter constructed using P-test’s schema: PIN `rc=0`, 17 survived; new `rc=0`, 0. This confirms the intended fix at both required real sinks, rather than only direct `scrub()` calls.

## 5. Cost and mutants

SOLID. Nine-sample minimum timing of the final changed credential and Bearer patterns at 16k/32k/64k/128k, covering many heads/links/`_key` fragments, name letters without a separator, and alternating quotes, has a largest observed doubling ratio of 2.312. The largest credential series was `credential-many-links`: 32.859/75.963/131.508/219.289 ms, ratios 2.312/1.731/1.667. This is linear within measurement noise; no superlinear evidence appeared.

SOLID. Scratch-only mutations m1–m13 all died. m1 `13 failed`; m2 `7`; m3 `4`; m4 `1`; m5 `2`; m6 `4`; m7 `3`; m8 `1`; m9 `1`; m10 `3`; m11 `1`; m12 `1`; m13 `5`. The report runner added independent X1/X2/X3/X4 boundary tests to kill changed-rule mutations. Existing `CHAINED` tests bind the chain cases at `T:228-233`, `LATER_RULES` binds later-rule cases at `T:276-281`, and `PIN_OUTPUTS` binds negative controls at `T:318-320`. The original m12 performance assertion timed out after 180s on its unanchored head mutant (clear red/hang); the scratch runner instead recorded a fast X4 discriminator (`1 failed, 75 deselected`) so the full mutant table has a deterministic test failure too. No mutation stayed green.

## 6. Finding inventory and recommendation

1. FOLLOW-UP F1 — SOLID; contract mapping: R-1 declaration boundary, but pre-existing at PIN; canonical: both real CLIs; material: malformed multiple-quote assignment exposes the following fake value; discriminator: fixture above; suggested fix: future explicit malformed-quote scrub rule/test. Not a blocker because S198A did not make PIN-hidden bytes visible.

2. FOLLOW-UP F2 — SOLID; contract mapping: none beyond general scrubber posture; canonical direct S only; material: `API_KEYé=` is unredacted in PIN and new; discriminator: fake fixture; suggested fix: explicitly choose/define Unicode identifier boundary policy. Not a blocker: pre-existing, out of S198A contract.

3. INFO I1 — SOLID; GitNexus index is stale and did not map the path-based P import; ripwire/graft did. No production behavior defect.

4. INFO I2 — SOLID; bare system `python3 scripts/lint_delta.py` lacks pyflakes. The project venv command works and returned `0 .py changed, 0 NEW pyflakes hit(s)`. This is a venue interpreter discrepancy, not code evidence.

GATE RECOMMENDATION: MERGE-READY-WITH-FOLLOWUPS. No finding satisfies all five blocking-predicate conditions. The independent 50,000-input differential, X1–X4 attacks, mutations, timing sweep, and both production CLIs find no S198A regression. This is a recommendation only; the coordinator owns the final decision.

## 7. Final hygiene and not done

SOLID. `git diff --check` is clean. `lint_delta --base 750699a --no-ap` reported `0 .py changed, 0 NEW pyflakes hit(s)`; pyflakes passed; S AP screen and T test screen both reported zero hits. GitNexus `detect-changes` returned `No changes detected.` The only tree change is this report. Scratch has only fake fixtures, copies, and results; no raw host transcript/database was read or copied. The report is write-only evidence; the verified production bytes remain S `37d94bd61556`, T `12dbaae6d0da`, and P `04326ece5b7a`.

NOT done: no real-transcript differential, no change to production files, no commit/push, no repair for F1/F2. Deliberately skipped: recursive validation of builder test/report tooling beyond the required mutation and gate evidence; it was outside this increment’s changed production boundary.

DISCREPANCIES: the requested `report-draft.md` did not exist on resume; `report.attempt1.md` only contained a route-503 line, so no completed section was reused. `printf '--- ...'` was rejected by this host Bash because the format began with dashes; this affected only a diagnostic label, not a verification command. `python3` was missing `pyflakes`; `/home/rocco/venv-agent-factory/bin/python` was used for the mandated lint and returned clean. `report_lint` final: `17 refs — OK 17, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.
