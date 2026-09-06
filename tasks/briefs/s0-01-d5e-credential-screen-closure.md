# BRIEF — S0-01 lane D5e: the credential screen tests membership under the CLOSURE of its normalizations, every new code path gets a killing test (VERIFY-D5d, round 8)
PIN: (set at dispatch)

You are the BUILD lane (Hermes on the PC, model ollama-cloud/kimi-k3, role code-implementer). honey: ultra. `.hermes.md` carries the
project rules. Your output is a PROPOSAL graded by the sandbox adversarial verifier; never self-accept. This brief is SELF-CONTAINED:
the verifier's full report is not in the tree at your PIN — every fact you need is below. Write `report-draft.md` in your lane dir as you
go (AF-AP-16). Interpreter: `$HOME/venv-agent-factory/bin/python` (python3.11 + pytest 9 + xdist). Long runs in ONE foreground call.

FIRST ACTION (halt loud on any mismatch): `git rev-parse HEAD` equals the PIN; `git log --oneline -2` shows the PIN on top of a commit
whose subject starts `S0-01 WIP checkpoint 8a:`; tree clean; `$HOME/venv-agent-factory/bin/python -m pytest tests/red/test_s0_01_backend_credential_screen.py -q -p no:cacheprovider`
→ `21 passed`. Then REPRODUCE the leak before touching code (paste the exact response line and the record's header value):
  GET /v1/models with `Authorization: Bearer <TOKEN>` and `X-Trace: s0-01-upstream-tok%20en-0123456789abcdef` (TOKEN =
  `s0-01-upstream-token-0123456789abcdef`, the test dummy) against the backend started as the test fixture starts it → expected
  today: `HTTP/1.1 200 OK` and a record whose `headers["x-trace"]` still carries the split token (recoverable by
  `re.sub(r"\s+", "", unquote(text))`). If it does NOT reproduce, STOP and report.

## The verdict you are closing (VERIFY-D5d, 2026-09-06) — blocking
- R8-D5d-F1 (LEAK): `_carries_secret` (scripted_backend.py ~:151-166) computes `stripped` once from the raw value and then unquotes
  each base; it never re-strips AFTER unquoting, so a token split by an ENCODED whitespace (`%20`, `%09`, `%0A`, `%0d`, `+`) is
  served 200 and recorded — 15/15 across header value, JSON body and path × five separators.
- F2 (the oracle mirrors the bug): `tests/red/test_s0_01_backend_credential_screen.py::_absent_under_all_normalizations` checks
  `(text, unquote(text), stripped, unquote(stripped), unquote(unquote(text)))` and never `strip(unquote(text))` — it calls the
  leaking record clean.
- F3: arm 1b (obs-fold → 400) is tested with CRLF folds only; the mutant `'\r' in v or '\n' in v` → `'\r' in v` SURVIVES and a
  bare-LF fold (`X-Foo: bar\n Content-Length: 5\r\n` + a pipelined POST) then smuggles: 200, two responses, two records.
- F4: the fail-closed branch (`if unquote(v) != v: return True` after the bounded passes) has no test — deleting it survives; a
  QUADRUPLE percent-encoded token is served 200.
- F5: `_iter_json_strings` yields dict KEYS as well as values, but no test covers keys — the mutant that stops yielding keys survives
  and a token split by a TAB inside a JSON KEY (`{"model":"s0-01-pong","messages":[],"s0-01-upstream-tok\ten-…":1}`) is served 200
  and recorded (recoverable by json-decode + whitespace strip).

## Rulings (binding)
1. ROOT CAUSE, not a fifth patch: the screen decides membership under the CLOSURE of its two normalizations. Implement
   `_normal_forms(s)`: breadth-first over the words of {unquote, strip_ws} applied to `s`, deduplicated, bounded at depth 5; if the
   frontier is still producing new forms at the bound → fail closed (`True`). `_carries_secret` returns `True` iff the token occurs in
   ANY normal form. Apply it identically to the path, header names, header values, the serialized body, every parsed JSON string
   (keys AND values) and the raw body. Delete the `range(3)` loop and the `stripped`-once computation.
2. The red-file oracle must be STRICTLY WIDER than the implementation and independent of it: rewrite `_absent_under_all_normalizations`
   to enumerate every word over {unquote, strip_ws, lower, unquote_plus} up to length 4 (a different lattice, more operators, its own
   code — never import the backend's helper) and assert the token absent under all of them.
3. Red tests (each proven red on HEAD before your fix, pasted): `test_credential_encoded_whitespace_split_returns_400` parametrized
   `["%20","%09","%0A","%0d","+"]` × {header value, JSON body value, query string}; `test_credential_whitespace_split_as_json_key_returns_400`
   (the TAB/LF/CR/FF/VT set as keys); `test_credential_quad_percent_encoded_fails_closed`; `test_obs_folded_header_rejected_400`
   extended with `ids=["CL-CRLF","TE-CRLF","CL-LF","TE-LF"]`; `test_duplicate_json_key_hiding_token_returns_400` (F6: the token in the
   wire bytes only — `{"n":"<TOKEN>","n":"safe"}` — must hit the raw-body screen). Every one asserts the exact status line
   `HTTP/1.1 400 Bad Request`, `count_after == count_before + 1`, `body == {"credential_in_unexpected_location": true}`, and the
   widened absence oracle.
4. Non-blocking, ship them (small, exact): F10 — `_read_body` catches `RecursionError` (depth-1000 body → 400 + close, 0 records;
   red test) and `_iter_json_strings` becomes iterative (explicit stack); F11 — records are written with `allow_nan=False` after
   coercing non-finite leaves to the string `"<non-finite>"` (red test: a `NaN`/`Infinity` body → the record parses under
   `parse_constant=raise`); F13 — assert `Handler.timeout` is a positive number before deriving the bounds; F16 — the domain table
   grows five framings (`fold_cl`, `fold_te`, `fold_benign`, `expect_empty`, `expect_bogus`) so the lane's own table covers its gate;
   F9/F15/F17 — the module docstring names `_iter_json_strings` (keys and values), states the closure semantics honestly (the depth
   bound affects false-positive breadth, not detection), says the screen is per item (cross-sink splits are out of contract by design),
   and that a body the parser cannot decode gets 400 + close; F18 — the red file's duplicated docstring sentence. F7: state whether M26
   (`read(0)`) is equivalent (the verifier could not distinguish it) — if you can build a discriminating control (a pipelined second
   request that must not be misframed), add it; otherwise say "equivalent, no distinguishing input found". F12 is an accepted risk:
   document it, do not change it.

## Boundary (touch ONLY): `proofs/S0-01/tools/scripted_backend.py`, `tests/test_s0_01_scripted_backend.py`,
`tests/red/test_s0_01_backend_credential_screen.py`.

## Acceptance bar (the verifier's set is the bar)
Rebuild these mutants on a scratch copy and paste killed/total: M57 (drop the fail-closed branch), M59 (arm 1b sees `\r` only),
M61 (POST-success `raw_body=None`), M62 (walk stops yielding keys), plus M18/M20/M29/M41/M48/M55/M58/M60 from round 8 and a no-op
control — every non-equivalent one killed by a NAMED test. The five separators × three sinks battery: 15/15 → 400 + redacted.

## Gate (paste verbatim into the report AND the commit body)
- pyflakes on the three files (rc 0).
- `$HOME/venv-agent-factory/bin/python -m pytest tests/test_s0_01_scripted_backend.py tests/red/test_s0_01_backend_credential_screen.py tests/test_stage0_ci_workflow.py -q -p no:cacheprovider -n 8`
  TWICE (paste both summary lines; the red file standalone once, no xfail/skip).
- Report fields: done (finding → test → the red observed before the fix), mutants killed/total + survivors named, not_done (→ reason;
  an empty not_done beside an unmet item reopens the lane), files, summaries, pyflakes, discrepancies, adjacent defects (report only).

Standing rules: no subagents; no outward-facing actions; never `git stash`/reset the worktree; tests write only under tmp_path; the
token in tests is a dummy — never print/persist a real credential. Authorization context: the owner's own deterministic test upstream
behind the owner's OmniRoute.
