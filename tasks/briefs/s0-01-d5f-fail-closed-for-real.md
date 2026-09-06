# BRIEF — S0-01 lane D5f: the credential screen's fail-closed decision is a boolean the consumer cannot misread, the test oracle proves itself non-tautological, every new path has a killing test (VERIFY-D5e, round 8b)
PIN: (set at dispatch)

Build lane (sandbox Opus 4.6 code-implementer — the Kimi lane that wrote D5e produced a fail-OPEN "fail-closed" branch and a
tautological oracle; this security-critical repair runs where the coordinator can gate it). honey: ultra. Your output is a PROPOSAL
graded by the round-9 verifier. Read in order: this brief; `tasks/briefs/s0-01-d5f-support/verify-D5e.md` (the verdict — every finding
below refers to it); `tasks/briefs/s0-01-d5e-credential-screen-closure.md` (the D5e rulings, still binding where not overridden).

FIRST ACTION (halt loud): `git rev-parse HEAD` equals the PIN; the red file `bash scripts/test_summary.sh tests/red/test_s0_01_backend_credential_screen.py`
→ `49 passed`; then REPRODUCE R8b-D5e-F1 before touching code — `GET /v1/models` with `X-Trace: s0-01-upstream-tok%20en-0123456789abcdef-%25252541`
→ today `HTTP/1.1 200 OK` and the header recorded verbatim (the token recovered by one `unquote` + whitespace strip); the control
without the suffix → 400 + redacted. Paste both. Reproduce the oracle tautology: replace `_absent_under_all_normalizations` with
`return True` on a scratch copy and run the red file → identical `49 passed`. Paste it.

## Rulings (binding)
1. F1/F3 (BLOCKING, the root cause): a fail-closed DECISION is a distinct boolean (or an exception), never a data value the consumer
   interprets by membership. `_normal_forms(s)` returns `(forms, saturated)`; `_carries_secret` returns True if the token is in any
   form, else `not saturated` (bound exceeded ⇒ True). The verifier's minimal fix in F1 is the reference. Keep `seen` — never discard
   forms already found. D5d's F12 accepted risk (junk like `%25252540` blanks a record) is RESTORED and documented as such.
2. F2 (BLOCKING): the red-file oracle must (a) be strictly wider than the implementation — depth ≥ 6 over {unquote, unquote_plus,
   strip_ws, lower} plus a zero-width/format-character strip (U+200B, U+FEFF, U+00AD, U+2060) — and (b) PROVE it is not a tautology
   with ORACLE SELF-TESTS: a test that feeds the oracle known-bad record texts (the F1 junk-suffix vector, a depth-5 nesting, an
   uppercased token, a ZWSP-split token, a raw TAB split) and asserts it returns False (detects), and known-good texts (the marker
   record, a normal user agent, `%25252540` alone) and asserts True; plus at least one backend test whose redness depends ONLY on the
   oracle (mutate the oracle to `return True` on a scratch copy → that test must fail; paste the run).
3. New red tests, each proven red on the PIN before your fix: `test_credential_split_with_trailing_nested_escape_returns_400` (the
   five separators × three sinks × the `%25252541` suffix); `test_credential_depth5_percent_nesting_returns_400` (`%25252520`,
   `%2525252520`, `%25252B`, `%2+B` in header value / header NAME / query / path / JSON value / JSON key — all 400 + redacted);
   F8 `sink="json_list_element"` for the whitespace-split family (kills MC9); F12 `test_json_depth_ignores_brackets_inside_strings`
   and `test_json_depth_handles_escaped_quote` (kill MG4/MG5); F14 an uppercased token in a header value → 400 (add `str.lower` to the
   closure ops — cheap; the token is lowercase by construction); F15 zero-width separators (ZWSP/BOM/soft hyphen, raw and JSON `​`)
   → 400 (add a format-character strip to the closure ops; state the exact set in the docstring).
4. Hygiene and truth: F4 the module/function docstrings say exactly what the code does (operators, depth, the closure direction, the
   restored accepted risk); F5 `_error()` sends `Connection: close` (every rejection closes — make `:39` true or delete the sentence);
   F6 the duplicated red-file sentence; F9 rename the quad test to what it proves (depth 4) and add the real bound-exceeded test;
   F10 `_json_safe` becomes iterative (or a test binds `MAX_JSON_DEPTH` far below its recursion limit); F11 delete the dead
   `except RecursionError` arm or make it reachable, and fix the depth-1000 test's docstring; F13 the red file's `MAX_JSON_DEPTH`
   read falls back with `pytest.fail("MAX_JSON_DEPTH missing from the backend")` instead of an AttributeError at import; F17
   `math.isfinite(handler_timeout)`; F18 the "Not recorded" enumeration lists the JSON-depth and short-body classes; F19 the
   `/tmp/unused-timeout-test` path becomes a tmp_path.
5. Mutants (build each on a scratch copy; paste killed/total with the killing test): MC5 (`return frozenset(seen)`), MC5b
   (`frozenset({s})`), MC2 (depth 6), MC9 (list branch), MG4, MG5, the oracle-tautology mutant (`return True` in the oracle — must
   be killed by the self-tests), a no-op control, plus the round-8b kills re-run (M18, M20, M29, M48, M55, M58, M59, M60, M61, M62,
   MC1, MC3, MC4, MC6, MF3, MG1, MG2, MG3, MG6 — all still killed). Every non-equivalent survivor named.

## Boundary (touch ONLY): `proofs/S0-01/tools/scripted_backend.py`, `tests/test_s0_01_scripted_backend.py`,
`tests/red/test_s0_01_backend_credential_screen.py`. Edit the shared tree /home/user/agent-factory in place — no commits, no git state
changes, no other paths, no subagents, no outward actions; one mutant copy at a time under …/scratchpad/ld5f/ with `--basetemp` per run;
4 shared cores — no xdist; long runs in ONE foreground call.

## Gate (paste verbatim): pyflakes rc 0 on the three files; `bash scripts/test_summary.sh tests/test_s0_01_scripted_backend.py tests/red/test_s0_01_backend_credential_screen.py tests/test_stage0_ci_workflow.py`
TWICE; the red file once standalone; the oracle-tautology run (red); the F1 reproduction before/after. Report to
…/scratchpad/wf-results-r5/D5f.md (draft D5f-draft.md as you go): done (finding → test → red before / green after), the mutant table,
not_done → reason (an empty not_done beside an unmet item reopens the lane), files, summaries, discrepancies, adjacent defects.
Authorization context: the owner's own deterministic test upstream behind the owner's OmniRoute; the token in tests is a dummy.
