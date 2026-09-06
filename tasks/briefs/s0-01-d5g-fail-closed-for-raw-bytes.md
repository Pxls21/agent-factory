# BRIEF — S0-01 lane D5g: the closure keeps `seen` and proves it, raw UTF-8 separators are normalised, the depth bound and the accepted risk are pinned from both sides, the oracle reads records the way they are written (VERIFY-D5f, round 9)
PIN: (set at dispatch)

You are the sandbox BUILD lane (Opus 4.6 `code-implementer`). honey: ultra. Your output is a PROPOSAL graded by VERIFY-D5g; never
self-accept. Interpreter `python3` (= `/root/venv-agent-factory/bin/python`). Edit the shared tree IN PLACE — no worktree, no branch, no
commits, no git state changes (never `git stash`/`checkout`/`restore`/`reset`). THE TREE IS DIRTY BY DESIGN: lanes N5g (the probe, its
tests, the spec schema, the regenerated `proofs/S0-*/result.json` + `proofs/ledger.json`) and A5g (the checker, its tests, one tee test)
are live in it — never touch their files. Long runs in ONE foreground call; no xdist; `--basetemp` under …/scratchpad/ld5g/ per run,
deleted after; `df -h /` before the first suite. Report to …/scratchpad/wf-results-r5/D5g.md (draft D5g-draft.md as you go).

FIRST ACTION (halt loud on mismatch): `git rev-parse HEAD` equals the PIN; your three boundary files are clean at HEAD (`git diff --stat
-- <them>` empty); `bash scripts/test_summary.sh tests/test_s0_01_scripted_backend.py tests/red/test_s0_01_backend_credential_screen.py tests/test_stage0_ci_workflow.py`
→ `442 passed`. Then REPRODUCE the two live leaks BEFORE touching code and paste both: (a) mutant V3 on a scratch copy of the backend
(`_normal_forms` returns the LAST frontier layer instead of `seen`): the suite stays `442 passed` while `X-Trace:
s0-01-upstream-tok+en-0123456789abcdef%2520` is served 200 and recorded with the token recoverable; (b) on the UNMUTATED backend, a
header value whose separator is the UTF-8 BYTES of U+200B (`e2 80 8b`) between the two token halves → `HTTP/1.1 200 OK`, the record
holds `tokâ\x80\x8ben` and the token is recoverable by a latin-1→utf-8 re-decode plus the zero-width strip.

## The verdict you are closing — `tasks/briefs/s0-01-d5g-support/verify-D5f.md` (read it whole; the rulings below are binding)
BLOCKING:
- F1 keep `seen`: add `test_credential_plus_split_with_pct2520_suffix_returns_400` exactly as the verdict specifies (the token found at
  an INTERMEDIATE closure layer) — red on V3, green on HEAD. Mutant V3 must die on it.
- F2 raw UTF-8 separators: `http.server` decodes header lines as latin-1, so a UTF-8-encoded U+200B/U+FEFF/U+00AD/U+2060/U+00A0/U+3000
  arrives as two or three latin-1 chars that neither `strip_ws` nor `strip_zwc` touch. Rule: a sixth closure op `utf8_redecode`
  (`x.encode("latin-1").decode("utf-8")`, returning `x` on either Unicode error) in `_normal_forms` AND in the red-file oracle (the
  oracle must stay at least as wide as the implementation); red test `test_credential_raw_utf8_zero_width_in_header_returns_400`
  parametrised over the six separators, the request built as BYTES exactly as the verdict shows — red on HEAD, green after; the same
  vectors in a header NAME and in a raw (non-JSON-escaped) body probed and reported (add the test if any leaks). Mutant UTF8-DEL
  (drop the op) must die. Measure the screen's cost at `MAX_CONTENT_LENGTH` before and after (the verdict measured 0.22 s at 1000 KB
  with five ops) and paste it.
- F3 the accepted-risk example is wrong: `%25252540` SATURATES at depth 5 and is served; `%25252541` is the one that trips the
  fail-closed arm and blanks. Fix both docstrings (`scripted_backend.py` module docstring and `_normal_forms`) to name `%25252541`, and
  pin the bound from BOTH sides (this is also F7): `test_bound_exceeded_blanks_the_record` (`X-Trace: %25252541` → 400 + the marker
  record; red at depth 6 — mutant MC2) and `test_saturating_junk_is_served` (`X-Trace: %252B` → 200 + a served record; red at depth 4 —
  mutant MC1). MC1 and MC2 move in OPPOSITE directions (4 tightens, 6 loosens) — the lane report's "both strengthening" was wrong; say so.
- F5 ruling 2(b): at least one backend test whose redness depends ONLY on the oracle — `test_record_text_carries_no_token_under_any_normalization`:
  a TAB-split request; assert ONLY `_absent_under_all_normalizations(record_text)` (no `== MARKER`). It is meaningful only after F4 is
  fixed (below); prove it: mutant O1 (`return True`) must now fail this backend test too, not only the self-tests.
NON-BLOCKING, ship them:
- F4 the oracle is blind to JSON escaping (`\t`, `​` in the serialised record never match a real TAB/ZWSP): seed the oracle's form
  set with the JSON-unescaped text of every JSON string literal in the record (`json.loads` over `re.findall(r'"(?:[^"\\]|\\.)*"', text)`),
  and add a RECORD-SHAPED known-bad self-test vector (the escaped form) asserting `False`. Mutant ORACLE-JSONBLIND (the seeding removed)
  must die on that self-test.
- F6 the oracle's `+` axis: add `(TOKEN[:mid] + "+" + TOKEN[mid:], False)` and `(TOKEN[:mid] + "%2B" + TOKEN[mid:], False)` to
  `test_oracle_known_vectors`; mutant O3 (drop `unquote_plus` from the oracle) must die; O2 (drop `unquote`) is EQUIVALENT — say so.
- F8 the header-NAME sink: add `"header_name"` to the depth-5 sink parametrisation (24 cases; the verdict measured all four vectors
  400 + REDACTED there — the lane's "parser interaction" reason was false, say so in the docstring).
- F9 the `except RecursionError` arm: DELETE it (the binary choice; `_json_nesting_depth` returns first at 32, CPython's limit is 1000).
- F12 `_json_safe` mutates the caller's object in place: return a new structure (copy on write) and add a test that the request body
  object is unchanged after `_json_safe`.
- F10 hygiene: every `file:line` in your report re-derived at your final tree (the D5f report's were 6-9 lines stale).
- F11 informational: report the cost table (1 KB / 10 KB / 100 KB / 1000 KB) with six ops.

## Boundary (touch ONLY): `proofs/S0-01/tools/scripted_backend.py`, `tests/test_s0_01_scripted_backend.py`,
`tests/red/test_s0_01_backend_credential_screen.py`. READ-ONLY: everything else (the N5g and A5g files above especially). Mutants: copy
your FINAL file to scratch, apply the mutation to the tree file, run, restore from the scratch copy — never from git. Tests write only
under `tmp_path`; the backend under test binds an ephemeral port as the existing fixtures do.

## Acceptance bar
Mutants (paste killed/total with the killing test named): V3, UTF8-DEL, MC1, MC2, O1 (now killed by a BACKEND test too), O3,
ORACLE-JSONBLIND, plus the round-9 kills re-run (V1, V2, V6, V7, MC5, MC9, MG4, MG5, V12-V19, O4-O7) — every non-equivalent one
killed by a NAMED test; O2 stated equivalent. The three-file suite TWICE + the red file standalone (`bash scripts/test_summary.sh …`,
lines pasted); pyflakes rc 0; the two live reproductions before/after; the cost table. Report fields: done (finding → test → red before
/ green after, red output pasted), not_done → reason (an empty not_done beside an unmet item reopens the lane), files (with the final
`sha256sum proofs/S0-01/tools/scripted_backend.py`), summaries, the mutant table, discrepancies (halt and report rather than
improvise), adjacent defects (report only). Standing rules: no subagents; no outward-facing actions; no commits. Authorization context:
the owner's own deterministic test upstream behind the owner's OmniRoute; the token in tests is a dummy.
