# BRIEF — S0-01 lane A5g: the checker's A21d non-final arms follow the tee's contract, every startup value is pinned, `_PINS_PENDING` retires, the exact-reason debt (F36/F37), the A25 omission test (F38), the dead presence gates (F40/F41), the real-leg tee-status test (F35), and VERIFY-CK8's F1-F22
PIN: (set at dispatch)

Build lane (sandbox Opus 4.6 `code-implementer`, or the PC Hermes lane if Kimi K3 has cooled down — the dispatcher says which). honey:
ultra. Your output is a PROPOSAL graded by VERIFY-CK9; never self-accept. THE CHECKER SUITE IS HEAVY: ~13 min serial in the sandbox,
~90 s on the PC with 8 workers. Sandbox runs are `-k` subsets only; every full lane suite runs on the PC:
`bash scripts/pc_suite.sh launch -n 8 -- tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_audit_cp5_controls.py tests/test_s0_01_pc_post_scan.py`
then `bash scripts/pc_suite.sh wait <RUN_ID>` (the id `launch` prints; your uncommitted edits travel as the patch — that is the point;
the pushed HEAD equals your PIN so no `PC_SUITE_BASE` is needed). Long runs in ONE foreground call. Scratch under
…/scratchpad/la5g/; report to …/scratchpad/wf-results-r5/A5g.md (draft A5g-draft.md as you go). `df -h /` before the first batch.

FIRST ACTION (halt loud on mismatch): `git rev-parse HEAD` equals the PIN; `git status --porcelain --untracked-files=no` shows only the
files the dispatcher lists (if any); the lane suite on the PC at the PIN → paste the counts (`233 passed, 46 skipped` is the PC shape:
the 46 real-leg tests skip there with exact reasons, their corpus lives in the sandbox).

Read, in this order: this brief; `tasks/briefs/s0-01-a5e-support/A5f-report.md` and `A5e-report.md` (what landed);
`tasks/briefs/s0-01-a5d-support/verify-CK7.md` §F35-F42 (the remaining findings, with `C:`/`T:` line refs at the CK7 PIN — re-derive at
yours); VERIFY-CK8's verdict (path set at dispatch — its A21d rejection table and its own findings, ruled on in R8 below);
`tasks/briefs/s0-01-b5d-support/B5d-report.md` §"R2 invariant list for the checker lane" and `tasks/briefs/s0-01-b5d-tee-drain-to-eof.md`
R2/R3 (the tee's status contract the checker must accept); the landed `proofs/S0-01/tools/frame_tee.py` docstring.

## Rulings (binding)
R1 — A21d non-final arms (`check_tee_status`, ~:1325). BOTH arms keep: the exact key set (`pins.PINNED_TEE_STATUS_KEYS`), `final` a
strict bool, `updated_utc` format, `updated_seq == recorded_c2a + recorded_a2c` (exact, every snapshot). FINAL (`final is True`): today's
exact arms unchanged — `drained` true, `write_errors == []`, `forwarded == recorded` both directions, `recorded == timeline count` both
directions, `updated_seq == timeline last seq`, `stdin_reader_done` true, the A21b exit rule. RUNNING (`final is False`, the snapshot
buzz-acp's SIGTERM/SIGKILL leaves behind): `timeline_last_seq - updated_seq ∈ {0, 1}`; per direction `timeline_<dir> - recorded_<dir> ∈
{0, 1}` and the two deficits sum to `timeline_last_seq - updated_seq` (the trailing frame has one direction); per direction
`recorded_<dir> - forwarded_<dir> ∈ {0, 1}`; `drained` and `stdin_reader_done` any bool; `write_errors` EXACTLY `[]` or EXACTLY
`["terminated: SIGTERM"]` (any other content → Failure naming the entry); `agent_returncode` and `exit_code` null (as today). Every new
reason carries the arm, e.g. `{leg}: tee-status.json running snapshot updated_seq {x} trails timeline last seq {y} by more than one`.
Red tests per bound (each red on the PIN's checker or on the mutant, green after): diff 1 passes / diff 2 fails; forwarded deficit 1
passes / 2 fails; `["terminated: SIGTERM"]` running passes, `["terminated: SIGKILL"]` fails naming it, the SIGTERM entry on a FINAL
status fails; `drained` false running passes / final fails; the seq-sum invariant violated fails; a deficit whose direction sum does not
match fails. Mutants: FINAL-RELAXED (final accepts diff 1), RUN-DIFF2, RUN-ANYERR, RUN-NOSUM, RUN-FWD2, RUN-DEFICIT-SUM — each killed by a
NAMED test. Then the tee's `test_sigterm_status_satisfies_check_tee_status` (`tests/test_s0_01_frame_tee.py` ~:1969-2026) is a HOLLOW
xfail: it imports `proofs.S0_01.check_acp_conformance` (no such package — `proofs/S0-01` is a directory, not a module) and calls
`check_tee_status(str(framedir))` with one argument (the real signature is `(leg_dir, leg, entries)`), so it xfails on ModuleNotFoundError
today and would never turn red. Rewrite it: load the checker the way `tests/test_s0_01_check_acp_conformance.py` does, call the real
signature with the parsed timeline entries, drop the xfail; it must FAIL on the PIN's checker with the exact `drained is not true`
reason and PASS on yours (paste both).
R2 — F42: `_PINS_PENDING` retires; consume `pins.PINNED_STARTUP_MCP_CMD`, `PINNED_STARTUP_PERMISSION_MODE`, `PINNED_STARTUP_RESPOND_TO`,
`PINNED_STARTUP_RESPOND_TO_TWO_USERS` (all landed in pins.py — read them, do not edit pins.py); one wrong-value hostile bundle per key →
the exact Failure naming the key and both values.
R3 — F36/F37 exact-reason debt: every reason assertion in `tests/test_s0_01_check_acp_conformance.py` becomes equality against the
checker's actual line; the three `ok or <substring>` real-leg tests (`tee_sha256 mismatch`, `manifest timestamps`, `_KNOWN_SKIP_REASONS`)
split into the corpus assertion (the exact PASS line) and a hostile-bundle assertion (the exact Failure). Paste `grep -c` of `in out` /
`in result` / `startswith(` / ` or ` before and after (target 0; list every survivor with why).
R4 — F38: the A25 sequence test mutates by OMISSION at the dispatcher (delete `check_env` for run-2, not a rename) and asserts exactly
`failure_reason: golden: check sequence mismatch - first missing: check_env:run-2`; F39 is an ACCEPTED risk by coordinator ruling (a
check that returns without asserting still counts as executed — the mutation audit is the guard): state it in `_run_check`'s docstring,
build no counter.
R5 — F40/F41 dead presence gates (CK7: `C:878-879`, `C:890`, `C:898`, `C:1327`, `C:1340`, `C:1367`, `C:1373`): for each, prove the
earlier check on the same path makes it unreachable — a delete-mutant survives the whole suite AND a raise-instrument in the gate never
fires across the suite + the corpus — then delete it; where a gate IS reachable, keep it and add the killing test with its exact reason.
`check_two_users`' AF-AP-40 branch: the live-path reason (`two-users: mentions/ absent`) is the tested one.
R6 — F35: a real-leg test for `check_tee_status` over every corpus leg, skipping with the exact reason
`tee-status.json absent in <leg> (corpus predates the tee status)` until the PC re-capture lands, plus a hostile-bundle variant that never
skips; report which legs skip today.
R7 — F43 follow-through: keep the hardlink fixture + `_rewrite` + the source-scan test; run the lane suite ONCE serially on the PC
(`-n 0`, the run A5f skipped) and paste `du -sh` of its basetemp; VERIFY-CK8's contamination findings (if any) fixed at the class.
R8 — VERIFY-CK8 (`tasks/briefs/s0-01-a5g-support/verify-CK8.md`; ids are R8-CK-Fn there; its item-4 table is R1's rejection list —
rows 1-6 must each PASS on your relaxed checker for a running snapshot and each still FAIL on a final status where the arm applies):
- F1 (BLOCKING): `test_ck8_owned_set_empty` / `test_ck8_owned_missing_buzz_pid` with the exact reasons `shutdown: owned-pids.json owned
  is empty or not a list` / `shutdown: owned-pids.json does not contain buzz-acp.pid <pid>`; the delete-mutants of both guards die.
- F2 (BLOCKING): `test_ck8_fifo_in_evidence_tree` (exact reason, completes in < 5 s); the non-regular walk covers EVERY directory the
  checker reads — golden AND `--fixtures-dir` (`test_ck8_fifo_in_fixtures_dir_rejected`: an exact reason, never a timeout); the
  wall-clock cap moves INTO `check_bundle(…, timeout_s=…)` so in-process consumers get it (`test_ck8_check_bundle_timeout`: a patched
  slow check → exact `checker timed out after 1s`); `--timeout-s` non-int → rc 64 with a test; exit 70 documented in the module
  docstring; the default cap becomes 90 s so it always fires before the runner's `timeout_s: 120` (spec.json untouched; say so in the docstring).
- F3 (BLOCKING): parametrise over LEGS × {`tee_pid`, `agent_child_pid`} — 10 exact-reason cases; the per-leg skip mutants and the
  `rid_agent` arm mutant die.
- F4 (BLOCKING): restore the two A20a structural attacks with a FULL owned set (`no tee process parented by buzz-acp`, `no agent process
  parented by a tee process`) — the three assertions the parent commit `2877327` had; both disable-mutants die.
- F5 (BLOCKING): the F43 source scan covers `open(...)` / `Path.open(...)` with a mode containing `w`/`a`/`+`, `json.dump`,
  `shutil.copy*`/`copyfile`, `os.replace`/`os.rename` onto a bundle path, over ALL module-level functions (helpers included); it self-tests
  with a deliberately violating source string (the three CK8 mutants); `_write_process_scan` (~T:317-343) unlinks before writing; the
  docstring says exactly what the scan catches.
- F6: the required startup set is the full 21 keys (every corpus leg has 21); every value except `pubkey` (64-hex format check only) is
  pinned — the constants are LANDED in pins.py (`PINNED_STARTUP_SUBSCRIBE`, `_CONTEXT_LIMIT`, `_MAX_TURNS_PER_SESSION`, `_HEARTBEAT`,
  `_MEH`, `_MEMORY`, `_PRESENCE`, `_TYPING`, `_MODEL`, plus the four from R2); a parenthesised value that contains `=` is rejected
  (`run-1: startup-line parenthesised value carries key=value tokens: model`); `missing keys` gets its exact-reason test; one
  wrong-value bundle per pinned key (exact reason naming the key and both values).
- F7: GET records' `authorization_fingerprint` is pinned to `is None` (the real producer records null on GET); the synthetic fixture's
  GET record becomes null; `test_ck8_get_fingerprint_non_null_rejected` (exact reason).
- F8: two per-shape POST body key sets keyed on `body.get("stream") is True` (stream: exactly `{max_tokens, messages, model, stream,
  stream_options, tools}`; non-stream: exactly `{messages, model, response_format, temperature}` — confirm against the real corpus),
  and the role SEQUENCE per shape pinned from the corpus; CK8's accepted bundles c02/c03 must now fail with exact reasons.
- F9: `test_ck8_teardown_scan_duplicate_pid` (exact reason).
- F10: F34's test RUNS the committed tee (subprocess, two frames on stdin, SIGTERM) and asserts `tuple(emitted keys) ==
  PINNED_TEE_STATUS_KEYS` (order bound); the AST test stays as the second instrument; both docstrings say what each does.
- F11 → R1. F12 → R2 (`test_ck8_startup_values_come_from_pins`: monkeypatch one pin, assert the reason quotes the patched value).
- F13/F14: the producer `pc_post.sh` and its tests are the COORDINATOR's — report only. F15/F16: every `file:line` in your report
  re-derived at your final tree; every count pasted from a command whose output you show. F17: `_write_tee_status`'s docstring says the
  values are hand-authored and only the key set is bound. F18: the parallel legs run on the PC (your gate). F20 → R3. F22 → F2.

## Boundary (touch ONLY): `proofs/S0-01/check_acp_conformance.py`, `tests/test_s0_01_check_acp_conformance.py`,
`tests/test_s0_01_audit_cp5_controls.py` (only if a control's exact reason changes — say which), and the ONE test
`test_sigterm_status_satisfies_check_tee_status` in `tests/test_s0_01_frame_tee.py`. READ-ONLY: `proofs/S0-01/pins.py`,
`proofs/S0-01/tools/frame_tee.py`, everything else. No commits, no git state changes, no subagents, no outward actions; one mutant copy
at a time; tests write only under tmp_path.

## Gate (paste verbatim)
pyflakes rc 0 on every touched file; the lane suite on the PC TWICE with `-n 8` and ONCE serial (`-n 0`), each with its own basetemp +
`du -sh`; the combined 24-guard mutant still 24/24 (re-run it); the R1 mutant set; the R3 greps before/after; the tee test's red/green
pair. Report fields: done (finding → test → red before / green after), the hostile-bundle table (A21d arms, the four pins, F36/F37 splits),
mutants killed/total, not_done → reason (an empty not_done beside an unmet item reopens the lane), files, summaries, temp footprint,
discrepancies, adjacent defects (report only). Authorization context: defensive verification tooling on the owner's own system; the
checker grades the owner's own ACP evidence; no credentials are involved.
