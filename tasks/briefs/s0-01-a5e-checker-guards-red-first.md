# BRIEF — S0-01 lane A5e: the 21 untested checker guards get their killing tests (red first), the record/receipt/startup rules land, the suite stops writing 4.7 GB
PIN: (set at dispatch)

Follow-up to lane A5d (`tasks/briefs/s0-01-a5e-support/A5d-report.md`), which landed 16 checker rules (F10-F13, F15-F21, F28, F30-F32) with a
green PC gate and reported the rest NOT done. The parent brief `tasks/briefs/s0-01-a5d-checker-guards-tested.md` and the verifier's report
`tasks/briefs/s0-01-a5d-support/verify-CK7.md` remain the contract; this brief is the ordered remainder. Same role, honey, boundary and
standing rules as the parent (build lane; touch ONLY `proofs/S0-01/check_acp_conformance.py`, `tests/test_s0_01_check_acp_conformance.py`,
`tests/test_s0_01_audit_cp5_controls.py` only if a control's exact reason changes; `pins.py`, `pc_post.sh`, the scan test and
`negative_contract.py` are READ-ONLY; no commits; no subagents; no outward actions).

FIRST ACTION (halt loud on mismatch): `git rev-parse HEAD` equals the PIN; the checker at HEAD has 257 `raise Failure` sites (A5d's count);
the lane suite on the PC (`bash scripts/pc_suite.sh launch -n 8 -- tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_audit_cp5_controls.py tests/test_s0_01_pc_post_scan.py`,
then `wait`) → `202 passed, 46 skipped`; in the sandbox `python3 -m pytest tests/test_s0_01_check_acp_conformance.py -q -p no:cacheprovider -k real_leg --basetemp=<scratch>` → `41 passed, 5 skipped`.

## Work, in this order — each item is a test that goes RED before the fix or the guard, and every red is pasted
1. **The 21 killing tests (VERIFY-CK7 F1-F9; the acceptance bar).** Rebuild the verifier's combined 24-guard mutant (`if False and …`
   per guard) on a scratch copy; for each of the 21 unkilled guards write ONE named test that builds the verifier's hostile bundle
   (the report gives the attack and the exact `failure_reason` it observed) and asserts the EXACT reason; prove each test red on the
   guard-disabled copy and green on the shipped checker; paste the per-guard table (guard → test → red text on the mutant). Run the
   combined mutant once more at the end: the bar is `24/24 guards each killed by a named test`.
2. **F22-F26 (records / receipts / startup).** Upstream POST records accept ONLY the pinned body keys (extra key → Failure naming it);
   message roles pinned from the real corpus shape (name the sample leg); GET records' `authorization_fingerprint` == the pinned
   fingerprint; the startup line matched EXACTLY against the pinned token set (unknown token → Failure); `mention_pubkeys` == the
   expected set exactly (extras and empty → Failure). Each with its red test through `check_bundle`.
3. **F30 (after-scan duplicates), F14 (rid `tee_pid`/`agent_child_pid` in the owned set on EVERY leg — A5d relaxed it to buzz-only).**
4. **F36-F38 (A28).** Replace the 13 remaining substring reason assertions with exact full-line equality (grep `in out`/`startswith`
   /`or ` over the reason assertions and paste the count: it must be 0); the sequence-guard test omits a real (check, leg) invocation
   at the dispatcher and asserts the exact `first missing:` pair.
5. **F39-F41.** `_run_check` counts assertions per check (`_asserted()`), a check that asserts nothing is a Failure `<check>:<leg>: check
   asserted nothing`; the six dead presence gates are deleted or converted to hard requirements with their own reason + test.
6. **F34/F35.** `_TEE_STATUS_KEYS` → `pins.PINNED_TEE_STATUS_KEYS`; a test that RUNS the committed `frame_tee.py` once and binds its
   emitted key set to the pin; `check_tee_status` gets a real-leg test that skips with the exact reason
   `real leg predates tee-status.json (v2.2 capture)`.
7. **F43 (disk).** A5d found that hardlink overlays break because tests WRITE IN PLACE (truncating the shared inode). The fix is a
   mutation discipline, not copytree: the bundle fixture builds ONE pristine bundle per session; each test gets a `cp -al` hardlink
   copy and every mutation goes through ONE helper `_rewrite(path, data)` that does `os.unlink(path)` (or `path.unlink()`) BEFORE
   writing, so the write lands in a new inode and the pristine copy is untouched (append-mode writes and `open(path, "w")` on a
   hardlinked file are FORBIDDEN in the test file — add a test that scans the test source for `open(` on bundle paths outside the
   helper). Measure `du -sh` of a run's `--basetemp` before and after; the bar is < 1 GB per serial run; paste both.

## Gate (paste verbatim into the report)
pyflakes on the three files (rc 0); the PC lane suite TWICE with `-n 8` (pasted `pytest-summary:` lines); the sandbox real-leg subset
once; the combined-mutant run (the `24/24` line). Report fields as the parent brief: the per-guard table, the hostile-bundle table,
mutants killed/total, not_done → reason (an empty not_done beside an unmet item reopens the lane), files, summaries, discrepancies,
adjacent defects. Venue substitutions for a sandbox dispatch are in the delta file named at dispatch.
