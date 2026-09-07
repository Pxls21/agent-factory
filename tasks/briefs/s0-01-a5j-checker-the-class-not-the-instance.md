# Lane A5j — S0-01 checker, round 12: the CLASS, not the instance — every read structurally under the walk rule, no presence-gated check, an xfail that can fail, a venue that cannot go quiet, a corpus whose content is verified (sandbox Opus 4.6 `code-implementer`)

**PIN:** the HEAD this brief is committed in (your work lands in the CHILD commit — the report header says "PIN: `<sha>`
(HEAD at dispatch); landing = the coordinator's checkpoint, made after this report").
**Verdict graded:** `tasks/briefs/s0-01-a5j-support/verify-CK11.md` (VERIFY-CK11, round 11 on checkpoint 8t — NOT-READY:
F1/F3/F4/F5/F8/F12/F15/F16 blocking; F2/F6/F7/F9/F10/F11/F13/F14/F17/F18/F19/F20 real; 1318 lines; every finding
executed, six fixes verified — use its code verbatim; its trees under the session scratchpad `ck11/` — `pin`, `mut`,
`comb`, `fix`, `corp`, `corp2`, `ap40`, `readmap.py`).
**Scope (four files + your report):** `proofs/S0-01/check_acp_conformance.py` (C:), `tests/test_s0_01_check_acp_conformance.py`
(T:), **`proofs/S0-01/negative_contract.py`** (widened this round for F8 — the two-line guard and nothing else unless the
class scan names more), `tests/test_s0_01_negative_contract.py` (only if a unit-level test belongs there); report
`tasks/briefs/s0-01-a5j-support/A5j-report.md`. READ-ONLY: `pins.py`, `check_initialize.py` (scan it, do not edit it —
report any hit as a finding), `pc_post.sh`, the three gate scripts, `tests/test_s0_01_pc_post_scan.py`,
`.github/workflows/stage0-ci.yml` (the coordinator adds `S0_01_VENUE: ci` there in the dispatch commit), everything else.
Never `git stash/checkout/restore/reset/add/commit/push`; every gate from a `git archive <PIN>` copy + your files (the
suite hashes and spawns the tee); mutants on scratchpad copies only; kill only what you start, PID-targeted; NEVER
background a run and stop; no outward actions. The declared corpus is `/root/s0-01-realleg/golden` with its sidecar
`/root/s0-01-realleg/golden.pc.sha256` (run `bash scripts/realleg_sync.sh check` first and paste it).

## Design (pinned by the coordinator — build it, do not redesign it)
1. **B1 as a PROPERTY, not an API call (F3/F4/F5).** `test_real_leg_negative`: run the check; `assert not ok, "check_negative
   PASSES on the real negative leg — the known-stale reasons no longer reproduce; retire them (B1)"` (the verifier's
   text); THEN the xfail branch only when the reason is known-stale — `_KNOWN_XFAIL_REASONS` holds the WHOLE reasons
   (`"negative: negative: probe_sha256 mismatch"` …) and `_is_known_stale(result)` is EQUALITY; drop the inert
   `strict=` / `raises=`; add `test_ck11_known_stale_is_the_whole_reason_not_a_tail` (the verifier's). Reproduce and
   paste the three states (stale → xfailed; repaired sha → FAILED with the retire message; unrelated failure → FAILED
   with the full reason) AND the tail-collision attack (`probe_error = "probe_sha256 mismatch"` → FAILED, never xfail).
   Mutants XFAIL-SUBSTRING and TAIL-COLLISION-ACCEPT (last-segment anchor) must die.
2. **F8 — the read CLASS closed structurally, not one file at a time.** (a) `negative_contract.py:178`: after the
   `exists()` check, `if not stat.S_ISREG(probe_file.lstat().st_mode): raise NegativeFailure("tools/acp_probe.py is not
   a regular file")`; checker-level red tests `test_ck11_fifo_at_tools_acp_probe_is_named` (elapsed < 5 s, the exact
   reason `failure_reason: negative: negative: tools/acp_probe.py is not a regular file`, `nc.HERE` monkeypatched to the
   bundle like `cc.HERE`) and the directory case. (b) The AST self-scan `test_ck11_every_read_is_under_the_walk_or_
   require_file` over the checker AND its callees (`negative_contract.py`, `check_initialize.py`): every `open(` /
   `.read_text(` / `.read_bytes(` / `json.load(` receiver either resolves under a walked root (`golden/`, `_fixtures()`,
   a leg dir) or is wrapped in `_require_file(...)` / preceded in the same function by an `S_ISREG` check on the same
   receiver; anything else FAILS naming `file:line`. The verifier's `ck11/readmap.py` is the starting point (40 sites
   in the checker). Mutants PROBE-EXISTS-ONLY (revert 2a) and READ-SCAN-OFF must die; the scan must be RED on the PIN
   before 2a (paste).
3. **F15 — no presence-gated check anywhere in the proof (AF-AP-40).** `C:1704` → `schema = ci.load_schema(
   _require_file(schema_path, "golden", "fixtures/acp-schema-v1.json"))`; red test `test_ck11_absent_acp_schema_is_a_
   failure` (`(1, "failure_reason: golden: fixtures/acp-schema-v1.json absent")`, the verifier's; baseline PASS line
   unchanged). Then the CLASS: import `AP_SCREEN` from `.claude/hooks/edit-snapshot.py` and assert the AF-AP-40 row has
   zero hits over the checker + callees, plus an AST pin — no `if <p>.exists()/.is_file()` whose false branch yields a
   default instead of a `raise` (the two safe presence gates the verifier named FAIL on absence; list any reviewed
   exception with its reason). Mutant SCHEMA-EXISTS-ONLY must die.
4. **F1 — the corpus path tracks the environment:** `test_ck11_real_leg_dir_is_resolved_from_the_environment` (the
   verifier's, green in both configurations on the PIN, red on CORPUS-UUID-LITERAL in both).
5. **F16 / F13 / F18 / F17 — the venue cannot go quiet.** Resolve BOTH `S0_01_VENUE` and `S0_01_REAL_LEG_DIR` once at
   module scope (one resolution point, documented — F18); the venue's domain is EXACTLY {`ci`, `sandbox`, `pc`} and
   an UNSET venue means `sandbox` (declare-or-fail is the default; CI declares `ci` explicitly — the coordinator's
   workflow edit); any other value (typo, case, whitespace — no normalisation) → the declaration test FAILS with
   `S0_01_VENUE=<v> is not a known venue` (parametrised red test over `sanbox`, `SANDBOX`, `sandbox `, `prod`, `0`);
   a corpus path that is a regular file → `is not a directory` (F17). Mutant VENUE-LOOSE (revert the domain) must
   die. Paste the four configurations again (unset-now-sandbox → FAIL without the corpus / RUN with it; `ci` → the
   declared skip count; empty dir → FAIL; hostile values → FAIL).
6. **F19 — the corpus CONTENT is verified at gate time.** The declaration test reads the sidecar
   `_REAL_LEG_DIR.parent / "golden.pc.sha256"` (absent → FAIL "run scripts/realleg_sync.sh pull") and checks every
   sha (the verifier's loop); red test: flip one byte in a scratch copy of the corpus → `corpus drift at ./<leg>/<file>`;
   mutant SIDECAR-UNCHECKED must die. (The coordinator's `realleg_sync.sh pc-build` now writes the same sidecar beside
   the PC tree, so the PC venue runs the identical assertion.)
7. **F2 / F9 / F10 — the cap's handler.** Add the verifier's `test_ck11_alarm_inside_try_cannot_leak_the_handler`
   (monkeypatched `alarm` raising → handler unchanged; ALARM-OUTSIDE-TRY must die); rename the existing
   `test_ck10_sigalrm_handler_restored_after_a_bad_cap` to what it proves (a rejected cap installs no handler); the
   `finally` restores the handler BEFORE `alarm(0)` with the comment stating why (F9); the C:2-3 NOTE states the whole
   refused domain (F10).
8. **F11 — the dead-branch pin bites.** Parse the cited `C:a-b` out of each of the SIX comments and assert the range
   holds a `raise Failure` inside the named function (RED on the PIN: the two `C:747-749` citations → fix them to
   `C:742-743`); cover all six (drop the `== 4` literal); DEADCOMMENT-WRONG-LINE must die.
9. **F6 / F7 / F14 / F20 — small structural holes.** Inline the scan call in the F43 real-source assertion
   (F43-SCAN-OFF dies); add `"truncate"` to `_OS_WRITERS` and a `gzip.open` branch, and name `os.fdopen` +
   `tempfile.NamedTemporaryFile` in the documented limits (F7; two planted vectors caught, two documented); delete the
   dead `tee.write_text("placeholder")` at T:4542 and its `_EXEMPT_FNS` entry (F14); the startup wrong-value dict is
   checked against `cc._EXPECTED_STARTUP_KEYS` with the two format-only keys named (STARTUP-CHECKS-TRIM dies — F20).
10. **Design §7 — one place to get wrong:** the 17 copies of the per-leg skip guard collapse into ONE helper /
    fixture (`_real_leg(leg)`) that implements the declaration semantics; the per-test bodies call it.
11. **F12 — report discipline, third time:** every `file:line` by `grep -n` on the FINAL bytes (17 of 35 were wrong —
    two were parent-tree numbers; the verifier greps twenty, three wrong = failed); every red-before row labelled
    genuine-red or CONTROL + the mutant that is its evidence (B2/B4 rows were mislabelled); the 17-value CLI cap probe
    PASTED with rc + stderr per value; the tee through the checker (SIGTERM + clean exit) RUN and pasted; NOT_DONE
    honest — "None" is a claim like any other.

## Mutants (scratchpad copies; `git status --porcelain` clean on your files after each; `ran` = executed; paste)
XFAIL-SUBSTRING, TAIL-COLLISION-ACCEPT, CORPUS-UUID-LITERAL (under `S0_01_VENUE=sandbox`, var unset — it must die in
THIS container now), VENUE-LOOSE, SIDECAR-UNCHECKED, SCHEMA-EXISTS-ONLY, PROBE-EXISTS-ONLY, READ-SCAN-OFF,
ALARM-OUTSIDE-TRY, DEADCOMMENT-WRONG-LINE, F43-SCAN-OFF, STARTUP-CHECKS-TRIM, plus ten of the verifier's reproduced rows
and the 27-line combined guard mutant once (its 32 killers).

## Gates (paste verbatim)
`bash scripts/test_summary.sh tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_audit_cp5_controls.py
tests/test_s0_01_pc_post_scan.py` twice from a static copy of the PIN + your files with NO explicit exports (the script's
defaults) · `S0_01_VENUE=ci` once (the declared skips) · `tests/test_s0_01_negative_contract.py` if touched · pyflakes ·
`python3 scripts/lint_delta.py --base <PIN>` (the tool's output) · the FIFO and directory at `tools/acp_probe.py` and at
`tools/frame_tee.py` (< 5 s, exact reasons) · the 17 CLI cap values · the tee through the checker · the process census.
PC leg: NOT run here (coordinator's). Report shape: FILE IDENTITY (FINAL bytes), DONE table (finding · change ·
file:line by grep · red-before verbatim or CONTROL + killer · green-after), MUTANT table, PROBE tables, NOT_DONE,
DISCREPANCIES, SELF-ATTACK.
