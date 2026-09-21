# PC lane — VB-F12-T2 (pin the committed S0-01 bundle's behaviour through the REAL proof-runner)

PIN: 38ad46b

Role: code-implementer. Route: the LOCAL Qwen build route (the pc_lane.sh default for code-implementer; do NOT
set HERMES_MODEL). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first. Report: draft after EACH item at
`tasks/briefs/s0-01-vb-f12-support/T2-report.md` (create the directory), return it whole as your final message.

## Context (measured at the PIN by the coordinator — verify, never assume)
Since 2026-09-21 `proofs/S0-01/evidence/golden/` holds the REAL v2.4 capture (five legs + negative). The frozen
checker fails it at ONE check — `check_golden` — because the pinned hermes-acp emits `session_info_update`
asynchronously (AF-AP-107, an OPEN owner decision; `docs/INCIDENT-LOG.md` 2026-09-21 entry item 7). So the real
proof-runner over the committed tree does NOT mint and does NOT defer — it reports a leg exit mismatch. Measured
on a copy of the PIN (`cp -a proofs scripts <copy>/`, then from inside the copy):

    python scripts/proof-runner run --proof S0-01 --venue sandbox --root .
      stdout: (empty)          stderr: leg-exit-mismatch: S0-01 positive expected 0 got 1
      rc: 1                    proofs/S0-01/result.json: absent
    python <the negative leg's cmd from proofs/S0-01/spec.json, argv[1:]>     (cwd = the copy)
      stdout line 1: protocol-violation: missing required initialize field
      stdout line 2: observed: error code=-32602 message=Invalid params
      rc: 1

`tests/test_s0_01_spec_runner.py` already has `_copy(tmp_path)` (a copy of proofs/ + scripts/) and
`_strip_v2_evidence(root)` (puts a copy into the DEFERRED v1 shape); its three deferral tests use the stripped copy
and are green (`13 passed in 3.83s` on the PIN, sandbox). Nothing in that file pins the COMMITTED tree's behaviour.

## Task — ONE file: `tests/test_s0_01_spec_runner.py`
1. Rewrite the module docstring (lines 1-12 still say "the committed evidence still v1"): the committed evidence is
   the real v2.4 bundle; the deferral tests strip a COPY (`_strip_v2_evidence`); the two new tests below pin the
   committed tree's real behaviour, which flips when the AF-AP-107 golden decision lands (that round must update
   them — say so in the docstring). Keep the V3 per-line-substring paragraph as it is.
2. Add `test_committed_bundle_runner_reports_leg_exit_mismatch_not_a_result(tmp_path)`: `root = _copy(tmp_path)`
   (NOT stripped), run RUNNER exactly as `test_runner_defers_s0_01_via_real_runner` does; assert rc == 1, assert
   `r.stderr.strip()` EQUALS the measured line above, assert `r.stdout == ""`, assert result.json absent. Time ONE
   run first (`time`), set `timeout` to at least 3x the measured wall time (the checker walks the whole bundle).
3. Add `test_committed_negative_leg_cmd_reports_the_protocol_violation(tmp_path)`: `root = _copy(tmp_path)`, run the
   negative cmd exactly as `test_negative_leg_defers_directly` does; assert rc == 1 and
   `r.stdout.splitlines() == [<line 1>, <line 2>]` (the two measured lines, exact).
4. De-vacuous each new test at write time: change ONE character of its expected string, run it, paste the failing
   assertion line into the report, restore the string, run again green. Both lines pasted = the red/green record.

## Boundary (touch ONLY `tests/test_s0_01_spec_runner.py`)
`proofs/` (the checker, pins, the evidence, spec.json), `scripts/proof-runner` and every other test file stay
BYTE-IDENTICAL to the PIN (`git status --porcelain` after you finish lists exactly the one file). A discrepancy
between the measured lines above and what you observe is a FINDING: paste both, do not "fix" the runner or the
checker, and stop at that item.

## Gate (paste every line verbatim; each call well under Hermes's 420 s terminal cap)
- `export S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`; PATH has
  `/home/rocco/venv-agent-factory/bin` first; `mkdir -p ../scratch/bt`.
- `python -m pytest -q -p no:cacheprovider -rfExXs --tb=short --basetemp ../scratch/bt tests/test_s0_01_spec_runner.py`
  TWICE — the two summary lines must agree (expected shape: `15 passed in Ns`).
- `python -m pyflakes tests/test_s0_01_spec_runner.py` (rc 0), `python3 scripts/ap_screen.py
  tests/test_s0_01_spec_runner.py` (paste its last line), `sha256sum tests/test_s0_01_spec_runner.py` (the FILE
  IDENTITY line of the report).
- CODE INTEL FIRST: `graft skeleton tests/test_s0_01_spec_runner.py` before any whole-file read. `report_lint`
  gates on a FLOOR; apply its `fix:` hints for at most THREE rounds, then paste and finish.

## Report shape (DATA, not prose)
FILE IDENTITY · the measured-vs-observed table for the four runner/negative lines · the de-vacuous red lines + the
green reruns · the two pytest summary lines · pyflakes/ap_screen lines · DISCREPANCIES · NOT-done.
