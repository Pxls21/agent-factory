# Lane D5k — S0-01 scripted backend, round 14: the record asserted VERBATIM, the oracle's table pinned, the ten reserved slots, an honest cost vector, a report that pastes (sandbox Opus 4.6 `code-implementer`)

**PIN:** the HEAD this brief is committed in (your work lands in the CHILD commit — the report header says "PIN: `<sha>`
(HEAD at dispatch); landing = the coordinator's checkpoint, made after this report" — D5j got this right; keep it).
**Verdict graded:** `tasks/briefs/s0-01-d5k-support/verify-D5j.md` (VERIFY-D5j, round 13 on checkpoint 8u — NOT-READY
on D5j-F1/F2/F3/F4/F5, all mechanical; F6-F17 real; 712 lines; every finding measured with the exact red test — use
its code verbatim; its trees under the session scratchpad `vd13/` (`base`, `work`) and `pin`).
**Scope (exactly three files + your report + the harness):** `proofs/S0-01/tools/scripted_backend.py` ·
`tests/test_s0_01_scripted_backend.py` · `tests/red/test_s0_01_backend_credential_screen.py` ·
`tasks/briefs/s0-01-d5j-support/cost_probe.py` (edit in place — the committed harness) · report
`tasks/briefs/s0-01-d5k-support/D5k-report.md`. Everything else READ-ONLY. Another lane (tee B5h) holds uncommitted
edits in this tree — never `git stash/checkout/restore/reset/add/commit/push`; run every gate from a `git archive
<PIN>` copy + your files; mutants on scratchpad copies only; kill only the backends you start, PID-targeted; NEVER
background a run and stop; no outward actions. Bytes and code points as `0xNN` / `U+NNNN` in code, never raw.

## Design (pinned by the coordinator — build it, do not redesign it)
1. **D5j-F1 — served-not-blanked tests assert the RECORD, never `!= MARKER`.** In `test_top_level_json_string_body_is_
   not_a_byte_view` and its `hello` control assert `json.loads(recs[-1].read_text())["body"] == json.loads(doc)`; then the
   CLASS: `grep -n "!= MARKER"` over both test files → zero hits (every "served" test asserts the recorded value); pin
   it with a text assertion in the red file. Mutant BODYSTR-RECORD-BLANKED (the verifier's, `backend:502`) must die.
2. **D5j-F2 — the oracle's pinned copy carries weight.** Add the oracle vector `ucd15_addition_split`
   (`TOKEN[:mid] + chr(0x0ECE) + TOKEN[mid:]`, expected caught) — RED on 3.11 under O-TABLE-DROP; and the cross-check
   `test_oracle_table_equals_the_impl_table` in the main file (`_parse_oracle_ranges(_ORACLE_INVIS_RANGES) ==
   sb._INVIS_PINNED`) so the two 4 KB literals cannot drift. Design §4 of the verdict (the oracle reading the impl's
   string) is REJECTED — two copies + an equality test keep the oracle's DATA independent of an impl mutation while
   the drift is loud; say so in the cross-check's docstring.
3. **D5j-F15 / design §3 — the ten permanently-reserved BMP slots join the extras.** U+2065 and U+FFF0-U+FFF8 (Cn on
   every interpreter, inside Default_Ignorable runs, rendered as nothing by several engines, never assignable to a
   visible character) → `_INVISIBLE_EXTRA`; regenerate `_INVIS_RANGES` (expected 4315 — paste your count); the
   self-test's expectation is the DEFINITION (categories ∪ extras), so `pinned − live_definition` stays empty on
   15.x and the 42 on 14.0; the plane-14 reserved run U+E0000-E0FFF stays OUT (the D5i-F11 ruling, documented). Red
   tests: the JSON-escape twin over U+2065 and U+FFF0 (RED today: served 200); oracle vectors `reserved_2065_split`,
   `reserved_fff0_split`; mutant TABLE-DROP-RESERVED must die. Design §1 (`pinned ∪ live` in the IMPL) is REJECTED:
   the self-test already makes a newer UCD loud at gate time, and a live union would make the serve-time predicate
   venue-dependent again — the exact defect D5i-F3 named; the module docstring states this choice and its reason.
4. **D5j-F5 — the cost vector is a body.** In `cost_probe.py` the "ordinary" and "inv-utf8-hdr" bodies carry their
   padding INSIDE a JSON string value (`{"model":…,"messages":[{"role":"user","content":"x"*n}]}`), never as trailing
   spaces (U+0020 is Zs — `strip_invis` deleted the whole pad and the column timed a collapsed string); re-run at a
   stated load, paste the four columns, and STATE the residual divergence from the previous verifier's raw-socket 0.63 s
   (the brief's >2× disclosure rule); the module docstring's cost sentence re-measured.
5. **D5j-F6 — the docstring claims only what holds.** `backend:266-269`: "strictly wider in the token-found arm; the
   saturation arm is not monotone: dropping bytes shortens forms and can let a closure saturate that previously
   exceeded the bound — measured 105 of 20 000 percent-dense vectors move from fail-closed to served, the depth-6 oracle
   confirms the token absent in all of them"; commit `test_pct_dense_junk_that_now_saturates_is_served` with one of the
   verifier's 105 vectors (200 + record kept + `_absent_under_all_normalizations(record)` True; RED under
   UQ-REPLACE-BOTH — it blanked).
6. **D5j-F7 — the stale-`[-1]` class closed in the MAIN file too:** `tests/test_s0_01_scripted_backend.py:144, 175,
   202, 212, 296, 446, 459, 487` get the `n0` / `== n0 + 1` delta; mutant RECORDLESS_400_APIKEY (the verifier's) must
   fail `test_credential_headers_dropped_from_records` (paste); `grep -n "\[-1\]"` over both files → every read is
   preceded by a delta or is the helper.
7. **D5j-F4 — the live-control section, pasted:** >= 50 redactions with the COUNT, normal + streaming after them, the
   legitimate-traffic table (+ the three top-level JSON string bodies at 400-verbatim, `"hello"`, the CJK body), the
   12-class `Connection: close` table.
8. **D5j-F3 / F8 / F10 / F11 / F16 / F17 — the report pastes:** every `file:line` by `grep -n` on the committed FINAL
   bytes (7 of 17 were wrong — three systematic bands — the verifier greps ten; three wrong = discipline failed); the
   test-count decomposition from `--collect-only` diffs; the raw `grep -n "byte_view=True"` output ("3 lines / 4
   occurrences"); the depth-pin sentence names `%252B` for `test_saturating_junk_is_served`; the RECORDLESS_400_XTRACE
   row pastes the 12-case line; the `ran` column = tests EXECUTED (passed + failed), uniformly.
9. **D5j-F9 / F12 / F13 / F14 — small hygiene:** delete the duplicate comment at `backend:528` (one comment, at the
   `_stream` site); the mutant table carries BOTH single-decoder reverts (impl and oracle) as qualified equivalents
   next to the both-decoder kills; the CTL_PARTIAL_noC1 row distinguishes the predicate form (equivalent, full 529)
   from the table-subtraction form (killed by the self-test); the generator in the docstring is COMPLETE and runnable
   (paste your regeneration under `/usr/bin/python3.13` → byte-identical to `_INVIS_RANGES`).

## Mutants (scratchpad copies; `git status --porcelain` clean on the scope files after each; `ran` = executed; paste)
BODYSTR-RECORD-BLANKED, O-TABLE-DROP (3.11), TABLE-DROP-RESERVED, RECORDLESS_400_APIKEY (main file), UQ-REPLACE-BOTH
(now also killed by the saturation-flip test — say so), TABLE-DROP-42 / FILLERS / CS / ME / ZLZP (unchanged killers,
re-measured with executed counts), ORACLE-DRIFT (change one range in the oracle's copy → the cross-check dies), plus
ten of the verifier's reproduced rows.

## Gates (paste verbatim)
`bash scripts/test_summary.sh tests/test_s0_01_scripted_backend.py tests/red/test_s0_01_backend_credential_screen.py`
twice from a static copy · red standalone · pyflakes · `python3 scripts/lint_delta.py --base <PIN>` (the tool's output)
· the 7 sinks × {6 invalid-UTF-8 + 8 invisible + 5 percent-encoded + 2 reserved} matrix · the three-interpreter sweep
over the 62 + 10 code points on both sinks · the impl-vs-oracle differential = `[]` and the parent-vs-child detection
differential = 0 regressions · the live controls (item 7) · the process census after your runs. PC leg: NOT run here
(coordinator's). Report shape: FILE IDENTITY (FINAL bytes, four files), DONE table, MUTANT table, PROBE tables,
NOT_DONE, DISCREPANCIES, SELF-ATTACK.
