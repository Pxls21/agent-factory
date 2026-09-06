# BRIEF — S0-01 lane N5d: the probe never exits 0 with an unsampled interpreter identity, SR-03 gets a real killer, the fixture agents run under the runner's interpreter by construction
PIN: (set at dispatch)

VERIFY-N5c (`tasks/briefs/s0-01-n5d-support/verify-N5c.md`) returned NOT-READY on lane N5c with four blockers; two are the
coordinator's (F5, F6 — landed with F3 at checkpoint 8a). This lane closes the rest. Same role/honey/standing rules as the round-7
briefs (build lane; no commits; no subagents; no outward actions; long runs in ONE foreground call; tests write only under tmp_path).

FIRST ACTION (halt loud on mismatch): `git rev-parse HEAD` equals the PIN; `bash scripts/test_summary.sh tests/test_s0_01_acp_probe.py tests/test_s0_01_check_initialize.py tests/test_s0_01_spec_runner.py tests/test_s0_01_negative_contract.py tests/test_s0_01_nostr_verify.py`
→ `231 passed` (228 + the coordinator's 3 F3 params); reproduce R7-N5c-F1 with the verifier's shape A (an agent that does
`import sys; sys.exit(0)` without writing to stdout): the probe exits 0 with `agent_interpreter_realpath`/`_sha256` null and
`probe_error` null — paste it. If it does not reproduce, STOP and report.

## Rulings (binding)
- F1 (BLOCKING): the interpreter identity is sampled ONCE, unconditionally, before the read loop can end — at the first a2c byte OR at
  EOF/exit, whichever comes first — and "never sampled" is itself a `probe_error` (`interpreter sample failed: agent exited before its
  first a2c byte`) with exit 1. The `proc.poll() is None` guard goes away: a sample that fails is always loud (the pinned agent's normal
  shape is answer-then-exit, so "child already dead" is not a false positive). Red tests: the verifier's two —
  `test_probe_agent_exits_without_output_is_fail_loud` (shape A → rc 1 + that exact `probe_error`) and
  `test_probe_interpreter_sample_failure_after_child_exit` (readlink patched to sleep 1 s then raise → rc 1 + the exact reason).
  Keep the existing G1-G5 kills green.
- F2 (BLOCKING): `scripts/proof-runner` keeps its per-line rule (it is correct); the tautological
  `test_runner_unmet_when_reason_split_across_lines` is replaced by the verifier's two red tests —
  `test_runner_records_the_observed_line_not_the_expected_reason` (observed line is a superset of the expected reason; the recorded
  `observed_failure_reason` is the OBSERVED line) and `test_runner_unmet_when_expected_reason_is_multiline` (a `\n` in the expected
  reason → `negative-control-unmet: S0-95`, rc != 0). Both must red on the SR-03 mutant (`expected in whole_text`) and green on the runner.
  Fix the false docstring.
- F4/F8 (BLOCKING): every fixture agent in `tests/test_s0_01_acp_probe.py` is written with `#!{sys.executable}` (the pattern
  `tests/test_s0_01_negative_contract.py` already uses) so the producer's `/proc/<pid>/exe` and the test's `sys.executable` expectation
  are the same interpreter BY CONSTRUCTION; delete the `os.path.realpath(sys.executable)`-vs-shebang coincidence. Red test: run the file
  under a PATH whose `python3` is a different interpreter (the verifier's shim: a dir with `python3 -> /usr/bin/python3.13`, or any
  other `python3` on the box) — both `test_probe_interpreter_fields_pinned` and `test_probe_identity_fields_all_pinned` stay green.
- F7: `tests/test_s0_01_check_initialize.py:835` and `:848` assert the exact full line; `:386`/`:395` assert the exact usage line on
  stderr; `tests/test_s0_01_acp_probe.py:576` asserts `== 1`.
- F10: keep `:290` (`agent_argv`, the sole killer of AP-20) and `:291` (`probe_path` presence — now also value-pinned by the
  coordinator's F3); delete only the five genuinely redundant lines (`:292,:293,:294,:296,:298`) and say so.
- F9 closes with F1; F11/F12 are report hygiene: paste the POST-INTEGRATION summary (never the lane's pre-integration count) and
  re-derive every `file:line` on the final tree before writing the report.

## Boundary (touch ONLY): `proofs/S0-01/tools/acp_probe.py`, `tests/test_s0_01_acp_probe.py`, `tests/test_s0_01_check_initialize.py`,
`tests/test_s0_01_spec_runner.py`. READ-ONLY: `scripts/proof-runner` (the rule stands), `proofs/S0-01/negative_contract.py`,
`proofs/S0-01/pins.py`, `tests/test_s0_01_negative_contract.py`, `proofs/S0-01/check_initialize.py` (report a needed change instead).

## Acceptance bar
The verifier's 58-mutant set (`scratchpad/vn5b/mut.py` + specs, or rebuilt from `verify-N5b.md`'s table if the scratch dir is gone)
re-run: 55/55 non-equivalent killed AND SR-03 killed AND AP-32 killed (by the coordinator's F3 test) — paste the table; the PATH-shim
run green; the suite TWICE (pasted `pytest-summary:` lines) + pyflakes rc 0; report fields as the round-7 briefs (done → red before
/ green after, not_done → reason, files, discrepancies, adjacent defects).
