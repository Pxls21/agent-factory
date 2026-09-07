# Lane D5h — S0-01 scripted backend, round 11: fail CLOSED on invalid UTF-8, strip control characters, pin the oracle's ops, prove `_json_safe` (sandbox Opus 4.6 `code-implementer`)

**PIN:** the HEAD this brief is committed in. **Verdict graded:** `tasks/briefs/s0-01-d5h-support/verify-D5g.md`
(VERIFY-D5g, round 10 — NOT-READY on F1/F2/F3; F4-F15 non-blocking; read it whole first, it carries the repro lines).
**Scope (exactly three files, all in `.lanes-live`):** `proofs/S0-01/tools/scripted_backend.py` ·
`tests/test_s0_01_scripted_backend.py` · `tests/red/test_s0_01_backend_credential_screen.py` — plus your report
`tasks/briefs/s0-01-d5h-support/D5h-report.md`. Touch nothing else; other lanes hold uncommitted edits in this tree —
never `git stash/checkout/restore/reset`; mutants run on scratchpad COPIES only (tactic 3a). No commits, no pushes,
no outward actions. Bytes and code points below are written as `0xNN` and `U+NNNN` — build them in code
(`bytes([0xE2, 0x80, 0x80])`, `"\N{...}"` / `chr(0x80)`), never paste raw bytes into a source file.

## Design (pinned by the coordinator — build it, do not redesign it)
1. **F1 — invalid UTF-8 is a fail-CLOSED signal, not an identity op.** Before the closure runs, every screened string
   (header names/values, path, query, raw body, every parsed-JSON string leaf) is prechecked: if its latin-1
   re-encoding holds any byte >= 0x80 that is not part of a well-formed UTF-8 sequence (`x.encode("latin-1")`
   succeeds and the resulting bytes fail a strict `.decode("utf-8")` = invalid; a string that cannot latin-1-encode is
   not a byte view and passes the precheck), the request is rejected exactly like a found credential: 400 +
   `{"credential_in_unexpected_location": true}` + the record blanked to MARKER + `Connection: close`. Rationale
   (write it in the docstring): this fixture serves ONE pinned client through OmniRoute; invalid UTF-8 in any screened
   field has no legitimate producer here, and a strict decoder's failure was the only thing hiding a real Unicode
   separator (VERIFY-D5g F1: bytes 0xE2 0x80 0x80 -> 400, bytes 0xE2 0x80 0x80 0x80 -> 200 verbatim).
   `utf8_redecode` stays strict for valid input. The precheck is a SEPARATE function with a SEPARATE name
   (`_has_invalid_utf8_bytes`), called from `_carries_secret`, so a mutant that deletes the call is a one-line mutant
   with a named killer.
2. **F13 — control characters join the equivalence class.** New op `strip_ctl` = remove every code point in
   U+0000-U+0008, U+000B, U+000C, U+000E-U+001F, U+007F-U+009F (keep TAB/LF/CR — `strip_ws` already covers them) in
   the closure AND the oracle. This closes the JSON twin of F1: the JSON escape for U+0080 decodes to a C1 control,
   which now strips to the bare token -> 400; the JSON escapes for U+00C0 U+00A0 decode to two code points whose
   latin-1 view is bytes 0xC0 0xA0 (overlong, invalid UTF-8) -> the precheck fails closed.
3. **Oracle stays STRICTLY wider (F3):** the oracle gains `strip_ctl` and a `utf8_redecode_lenient` op
   (`encode("latin-1").decode("utf-8", errors="ignore")`, `except UnicodeEncodeError: return x`) — the oracle must
   recover the token through junk bytes even when the implementation regresses. Every oracle op gets a NAMED self-test
   vector in `test_oracle_known_vectors` that is red when that op alone is dropped: add `raw_utf8_mojibake` (strict
   op; the verifier's vector — the latin-1 view of bytes 0xE2 0x80 0x8B between the token halves),
   `raw_utf8_mojibake_junk` (lenient op; the latin-1 view of bytes 0xE2 0x80 0x8B 0x80), `c1_control_split`
   (strip_ctl; U+0085), `del_split` (U+007F). Update the oracle docstring to list ALL ops + the JSON seeding (F7).
4. **F2 — prove `_json_safe` directly.** Lift it to module scope (`_json_safe(obj)`), keep `State.record` calling it;
   replace `test_json_safe_does_not_mutate_request_body` with the verifier's direct test (deepcopy-before,
   `body == before`, `out is not body`, coercion of the nested NaN) and delete the round-trip duplicate. Mutant
   `M_JSONSAFE_INPLACE` (the parent's in-place walk) must die on the new test — paste the red line.
5. **F4** — add `test_unquote_op_is_required_for_the_bound` (`X-Trace: %252520%252B` -> 400 + MARKER); mutant
   `M_UQ_DEL` must die on it. **F5** — add `test_raw_non_ascii_header_name_rejected_by_gate_no_record` (400,
   `Connection: close`, record delta 0) and state the REAL mechanism (the `email` parser's
   `MissingHeaderBodySeparatorDefect` -> `_framing_gate` arm 1, before `state.record`). **F6** — end the comment at
   "on every interpreter." **F11** — one clause on `_carries_secret`'s docstring pointing at the accepted risk in
   `_normal_forms` (`%25252540` served / `%25252541` blanked). **F14** — no change. **F15** — the O2 note says
   "for a token containing no `+`".
6. **Red tests for F1 (both twins) exactly as the verifier wrote them:**
   `test_credential_invalid_utf8_separator_in_header_returns_400` over `enquad_plus_junk` (0xE2 0x80 0x80 0x80),
   `nbsp_plus_junk` (0xC2 0xA0 0x80), `overlong_space` (0xC0 0xA0), `lone_continuation` (0x80); the JSON-body twin
   over the JSON escapes for U+0080, for U+00C0 U+00A0, and for U+00E2 U+0080 U+0080 U+0080; and for F13 U+007F
   and U+0001 in a header value and in a JSON body. RED-BEFORE is mandatory for every new behaviour test: run them
   against the PIN's implementation (parent impl + your tests, as the verifier did) and paste the failing lines; a
   test that was already green is a CONTROL and is labelled so, with the mutant it kills.

## Mutants (restore from a pristine copy; `git status --porcelain` clean after each; paste the table)
The verifier's 33-mutant set + no-op control, re-run on the final tree (its runner lives under the session scratchpad
`vd10/` if present — reuse it; otherwise rebuild the same set from the verdict's table), PLUS: `M_UTF8_PRECHECK_DEL`
(delete the precheck call), `M_UTF8_PRECHECK_INV` (invert it), `M_CTL_DEL` (drop `strip_ctl` from the impl), `O_CTL`
(drop it from the oracle), `O_UTF8_LENIENT` (drop the lenient op from the oracle), `M_JSONSAFE_INPLACE`, `M_UQ_DEL`.
Every mutant KILLED by a NAMED test, or proven equivalent with a differential (state the vector count); `O2_UQ` may
stay "equivalent for this token" with the F15 wording.

## Report discipline (F8/F9/F10/F12 — the previous report failed all four)
PIN sha that EXISTS (`git cat-file -e <sha>` pasted); every Done row cites `file:line` against the FINAL tree;
red-before/green-after column with the verbatim failing line or the word CONTROL + killer; cost table with BOTH
columns (ordinary and fail-closed at 1 KB / 10 KB / 100 KB / 1000 KB) and the load average; the sink x separator
matrix re-run (7 sinks x the 4 invalid-UTF-8 separators + U+007F + U+0001), every cell `400/MARKER/yes/yes`.

## Gates (paste verbatim)
`bash scripts/test_summary.sh tests/test_s0_01_scripted_backend.py tests/red/test_s0_01_backend_credential_screen.py`
twice · red file standalone · `python3 -m pyflakes` on the three files · `python3 scripts/lint_delta.py --base
origin/claude/soundbox-kit-migration-iz1jwf` clean on your files · the live normal-traffic + streaming control after
the redactions (the verifier's R10-D shape). PC leg: NOT run here (coordinator's).
