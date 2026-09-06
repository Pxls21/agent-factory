# BRIEF — S0-01 lane A5f: the checker's remaining VERIFY-CK7 items — record/receipt/startup pins, exact reasons, the assertion counter, the dead gates, the tee-status pin, the 4.7 GB fixture
PIN: (set at dispatch)

You are the BUILD lane (Hermes on the PC, model ollama-cloud/kimi-k3, role code-implementer). honey: ultra. `.hermes.md` carries the
project rules; your output is a PROPOSAL graded by the sandbox adversarial verifier. Interpreter: `$HOME/venv-agent-factory/bin/python`
(pytest-xdist installed). Write `report-draft.md` as you go. Long runs in ONE foreground call.

Read, in this order (all in the tree at your PIN): `tasks/briefs/s0-01-a5e-checker-guards-red-first.md` (the ordered list — item 1 is
DONE by lane A5e: 21 killing tests, the combined 24-guard mutant 24/24; you do items 2-7), `tasks/briefs/s0-01-a5e-support/A5e-report.md`
and `A5d-report.md` (what landed), `tasks/briefs/s0-01-a5d-checker-guards-tested.md` (the parent rulings) and
`tasks/briefs/s0-01-a5d-support/verify-CK7.md` (the verifier's findings F22-F26, F14, F30, F34-F41, F43 with their hostile bundles and
exact reasons). The rulings in the parent brief are binding; the A5e brief's item 7 (F43) states the hardlink discipline: ONE pristine
bundle per session, `cp -al` copies per test, every mutation through ONE helper that UNLINKS before writing (in-place writes on a
hardlinked file corrupt the pristine copy — that is why A5d's attempt broke), a source-scan test that forbids `open(<bundle path>, "w")`
outside the helper; target < 1 GB of temp per serial run, paste `du -sh` before/after.

FIRST ACTION (halt loud on mismatch): `git rev-parse HEAD` equals the PIN; `git log --oneline -8` contains subjects starting
`S0-01 WIP checkpoint 8c:` and `8a:`; tree clean; the lane suite with xdist:
`$HOME/venv-agent-factory/bin/python -m pytest tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_audit_cp5_controls.py tests/test_s0_01_pc_post_scan.py -q -p no:cacheprovider -n 8 --basetemp=<scratch>/tmp`
→ `223 passed, 46 skipped` (the 46 are the real-leg tests; their corpus lives in the sandbox and they skip here with exact reasons).

Work items 2-7 IN ORDER, each red-first with the exact reason pasted; stop cleanly with an honest not_done if the budget runs out.
Boundary (touch ONLY): `proofs/S0-01/check_acp_conformance.py`, `tests/test_s0_01_check_acp_conformance.py`,
`tests/test_s0_01_audit_cp5_controls.py` (only if a control's exact reason changes — say which). READ-ONLY: `proofs/S0-01/pins.py`
(the F42 hunk goes in the report: `PINNED_STARTUP_MCP_CMD = ""`, `PINNED_STARTUP_PERMISSION_MODE = "bypassPermissions"` — consume them
from a local `_PINS_PENDING` dict with a TODO naming this ruling), `proofs/S0-01/tools/pc/pc_post.sh`, `tests/test_s0_01_pc_post_scan.py`,
`proofs/S0-01/negative_contract.py`, `proofs/S0-01/tools/frame_tee.py` (for F34: RUN the committed tee once in a test and bind its emitted
key set to `pins.PINNED_TEE_STATUS_KEYS`; `_TEE_STATUS_KEYS` in the checker is replaced by the pin).

Gate (paste verbatim): pyflakes rc 0 on the three files; the lane suite TWICE with `-n 8` and ONCE serially (`-n 0`), each with its own
`--basetemp`, deleted afterwards, plus `du -sh` of the serial run's basetemp; the combined 24-guard mutant still 24/24 (re-run it —
your checker edits must not un-gate a guard); `grep -c` of `in out`/`startswith(`/` or ` over reason assertions (target 0). Report
fields: done (finding → test → red before / green after), the hostile-bundle table (F22-F32 → exact Failure reason), mutants killed/total,
not_done → reason (an empty not_done beside an unmet item reopens the lane), files, summaries, temp footprint, pyflakes, discrepancies,
adjacent defects (report only), the pins hunk. Standing rules: no subagents; no outward-facing actions; never `git stash`/reset the
worktree; tests write only under tmp_path. Authorization context: defensive verification tooling on the owner's own system; the checker
grades the owner's own ACP evidence; no credentials are involved.
