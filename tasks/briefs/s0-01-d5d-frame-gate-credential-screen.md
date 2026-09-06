# BRIEF — S0-01 lane D5d: the scripted backend's credential screen closes the four VERIFY-D5c blockers (red tests are committed)
PIN: (set at dispatch — scripts/pc_lane.sh refuses to run without a full SHA here)

You are the BUILD lane (Hermes on the PC, role code-implementer). honey: ultra. `.hermes.md` carries the project
rules. Your output is a PROPOSAL graded by the sandbox adversarial verifier; never self-accept. CONTEXT BUDGET: this
brief, the verify report, the red-test file and your two files fit one context — load no skills. Write
`report-draft.md` in your lane dir as you go (AF-AP-16).

FIRST ACTION (halt loud on any mismatch): `git rev-parse HEAD` equals the PIN; `git log --oneline -1` subject starts
`S0-01 WIP checkpoint 7:`; tree clean; `$HOME/venv-agent-factory/bin/python -m pytest tests/red/test_s0_01_backend_credential_screen.py -q -p no:cacheprovider`
→ `11 passed, 10 xfailed` (the ten xfails ARE the defects; if any XPASSes or errors, STOP and report).

## What this lane is for
VERIFY-D5c (`tasks/briefs/s0-01-d5d-support/verify-D5c.md`) confirmed the allow-list framing gate: 36/36 replayed vectors
closed, 192/192 domain cells match an independently derived oracle, http.server's own 501 path proven safe. It returned
NOT-READY on the CREDENTIAL SCREEN and on test/report hygiene. The verifier's red tests are already committed in
`tests/red/test_s0_01_backend_credential_screen.py` with STRICT xfail markers (R7-D5c-F1, F2, F6, F7) plus three
guard tests (F3, F4, F5) that kill its surviving mutants M48/M41/M20. Make the xfails green by fixing the BACKEND and
removing their markers — never by editing an assertion (the markers are the only edit allowed in that file).

## Coordinator rulings (binding)
- F1 (BLOCKING): the raw request body reaches the ONE record boundary on EVERY recording path — `_read_body` returns the
  raw bytes and every `state.record(...)` call passes `raw_body=` (the GET site and the POST success site today do not).
  A token split by any whitespace inside a valid JSON body is a 400 + the marker record; the record bytes carry no
  token under literal / unquote / whitespace-stripped / both normalizations.
- F2 (BLOCKING): the Expect arm tests PRESENCE — `self.headers.get_all("Expect") is not None` — any value, including
  empty, → 417 + close, exactly one response, no record.
- F6: obs-fold (RFC 9112 §5.2) is a framing defect: any header VALUE containing `\r` or `\n` → 400 + close before
  any route (the arm belongs in `_framing_gate`, step 1, next to `headers.defects`).
- F7: the screen's `unquote` runs to a FIXED POINT, bounded (≤ 3 passes); a value that still changes after the bound
  is treated as carrying the secret (fail closed). Apply the same to the path, header names, header values, both body
  forms. Add a test for `%2525…` (triple) → 400.
- F8/F9 (hygiene, in tests/test_s0_01_scripted_backend.py): every test self-contained (the one at :174 issues its own
  POST); every status assertion is an exact status-line equality and every record-count assertion is
  `== count_before + k` — the verifier lists the exact lines (18 `>` counts, 13 substring status checks).
- F10/F11 (docstring): state the raw-body screen truthfully once F1 is fixed; the Expect rule; leading-OWS
  `Content-Length:  5` is parser-stripped and SERVED on POST (not a defect), trailing OWS is rejected (stricter than
  RFC 9110 §5.5, fail-closed); the collapse of duplicate non-framing headers loses the dropped values (say so; drop the
  "combed when needed" sentence); arm 6 (501) is unreachable inside do_GET/do_POST and is delivered by http.server.
- F12: delete the dead 501 arm from `_framing_gate` and cite the http.server proof in the docstring — OR move the check
  into an overridden `handle_one_request`; either way the negative control must red on deletion of the live code.
- F13/F14: rename `test_negative_control_post_cl_overmax_gate_arm` to what it proves and add the ordering assertion
  `CL > MAX + Expect: 100-continue → 400`; the defects and expect negative controls send a forged tail and assert the
  record delta AND `Connection: close`.
- F15: the handler-timeout test bounds by `Handler.timeout` read from the module (×0.5 … ×2.5), never a hand-copied window.
- F17 (advisory, do it if cheap): served and leak responses may send `Connection: close` so clients need no 5 s recv
  timeout — only if every domain cell and the OmniRoute-facing behaviour stay identical (the verifier's half-close control
  showed identical verdicts); otherwise report and skip.

## Deliverables (boundary — touch ONLY these paths)
1. MODIFY `proofs/S0-01/tools/scripted_backend.py` — the rulings above; docstring per F10/F11/F12.
2. MODIFY `tests/test_s0_01_scripted_backend.py` — F8/F9/F13/F14/F15 + the triple-encoding test.
3. MODIFY `tests/red/test_s0_01_backend_credential_screen.py` — ONLY remove the `xfail` markers that now XPASS.

## Acceptance bar (the verifier's set is the bar)
Red file: `21 passed` (no xfail left, no skip). The verifier's non-equivalent survivors M18 (order), M20, M29, M41, M48
each killed by a named test (`tasks/briefs/s0-01-d5d-support/verify-D5c.md` §5 lists them; rebuild each mutant on a
scratch copy — `cp -al` hardlink copies are fine — and paste killed/total for the full 54 + the double M55).

## Gate (paste verbatim into the report AND the commit body)
- `$HOME/venv-agent-factory/bin/python -m pyflakes proofs/S0-01/tools/scripted_backend.py tests/test_s0_01_scripted_backend.py tests/red/test_s0_01_backend_credential_screen.py`
- `bash scripts/test_summary.sh tests/test_s0_01_scripted_backend.py tests/red/test_s0_01_backend_credential_screen.py tests/test_stage0_ci_workflow.py` TWICE (use the venv python:
  `SUITE_PY`-style — run `$HOME/venv-agent-factory/bin/python -m pytest … -q -p no:cacheprovider` if the wrapper picks the wrong interpreter; paste both summary lines).
- Report fields: done (finding → test → the red observed before the fix / on revert), mutants killed/total + survivors,
  not_done (→ reason), files, summaries, pyflakes, discrepancies, adjacent defects (report only).

Standing rules: no subagents; no outward-facing actions; long runs in ONE foreground call; never `git stash`/reset the
worktree; tests write only under tmp_path; the token in tests is a dummy — never print/persist a real credential.
Authorization context: the owner's own deterministic test upstream behind the owner's OmniRoute.
