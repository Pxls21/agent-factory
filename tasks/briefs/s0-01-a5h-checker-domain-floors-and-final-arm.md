# Lane A5h — S0-01 checker, round 10: domain floors, walk-before-read, the FINAL arm pinned, the F43 scan proven, the dead branches settled (sandbox Opus 4.6 `code-implementer`)

**PIN:** the HEAD this brief is committed in. **Verdict graded:** `tasks/briefs/s0-01-a5h-support/verify-CK9.md`
(VERIFY-CK9, round 9 on checkpoint 8m — NOT-READY: R9-CK-F1..F5 blocking, F6..F29 real; read it whole first — it carries
the executed repro for every finding, the 38-shape A21d table, the mutant tables and the exact red tests).
**Scope (exactly two files + your report):** `proofs/S0-01/check_acp_conformance.py` (`C:`) and
`tests/test_s0_01_check_acp_conformance.py` (`T:`); report `tasks/briefs/s0-01-a5h-support/A5h-report.md`. `pins.py`
is READ-ONLY (every value you need is already there). Other lanes hold uncommitted edits in this tree (backend files) —
never `git stash/checkout/restore/reset/add/commit/push`; mutants on scratchpad COPIES only (tactic 3a; the verifier's
harness is under the session scratchpad `vck9/` — reuse `mutate.py`/`driver*.sh`); no outward actions.

## Design (pinned by the coordinator — build it, do not redesign it)
1. **F1 — the cap's domain is `int > 0`.** `--timeout-s` parses to a strict int; `<= 0` (and non-int) exits 64 with
   `usage: --timeout-s must be a positive integer` BEFORE any bundle read; `check_bundle(timeout_s)` raises `ValueError`
   on `<= 0` (never silently uncapped). `None` keeps meaning "no cap" for in-process callers — but see F28: the shared
   test helper `T:499 _check` passes a POSITIVE cap (`timeout_s=60`) by default, so the guard is live in every bundle
   test; one test exercises the 90 s DEFAULT by monkeypatching the alarm (assert `signal.alarm` was called with 90).
   Red tests: CLI `0`/`-1`/`abc` → 64; in-process `0` → ValueError; a FIFO bundle under `--timeout-s 3` → rc 70 in ≤ 4 s.
2. **F2 + F27 — walk before read, and type before name.** The non-regular-entry walk (`C:1629-1645`) runs BEFORE the
   first `read_text` (`C:1613`); `_require_file` (`C:182`) requires `stat.S_ISREG` (a FIFO, a directory, a socket, a
   device → `Failure("<leg>: <name> is not a regular file")`); the per-leg entry allowlist (`C:1674-1677`) checks the
   entry TYPE as well as the name (a directory named `tee-status.json` → the same exact reason). Red tests: `mkfifo
   identities.json` → the exact non-regular reason in ≤ 1 s under the default cap (this is CK8 item-1d's own vector);
   a directory named `tee-status.json`; `_require_file(<FIFO>)` and `(<dir>)` raise.
3. **F3 — the F43 source scan is ONE function.** Extract `_scan_direct_writes(src: str) -> list[str]` at module scope
   in `T:`; the real assertion and the self-test both call it; the self-test asserts the scan finds the planted
   violation AND that emptying `_WRITE_ATTRS` / short-circuiting the loop makes the self-test itself fail. Prove with the
   verifier's two mutants (F43-ATTRS-OFF, F43-SCAN-OFF): both must now die — paste the red lines. Fix the docstring
   (`T:3240-3241`) to say what is actually proven.
4. **F4 — a named killer for `no tee process parented by buzz-acp` (`C:1272-1273`).** The verifier's red test verbatim
   (closure intact so `C:1259` cannot fire first; `assert out == "failure_reason: run-1: no tee process parented by
   buzz-acp"`). Mutant TEEPAR-OFF must die on it.
5. **F5 + F18 + F29 — the FINAL arm pinned exactly, both arms type-strict, both RUNNING upper bounds pinned.** One
   wrong-value bundle per FINAL rule with the exact reason: `forwarded_c2a != recorded_c2a`, `forwarded_a2c !=
   recorded_a2c`, `recorded_c2a != timeline c2a count`, `recorded_a2c != timeline a2c count`, `updated_seq != timeline
   last seq`, `stdin_reader_done is not true when final` (the verifier's shape table gives the exact strings). The FINAL
   arm uses `_is_strict_int` like the RUNNING arm (a float `3.0` is REJECTED on both — red tests for `recorded_c2a`,
   `forwarded_c2a`, `updated_seq` as floats on the final arm). RUNNING upper bounds: `updated_seq` lag 2 and a recorded
   deficit of 2 each get a killer (mutants RUN-DIFF2, RUN-RECDEF2 must die). All six FINAL-RELAXED mutants must die.
6. **F17 — one seq rule, cited.** `check_timeline` forces `seq == 1..N` for every leg before `check_tee_status`, so the
   seq-sum rule (`C:1431-1433`) and the deficit-sum rule (`C:1425-1427`) are the same predicate through the live entry
   point. Keep the deficit-sum rule, delete the seq-sum rule, and put the derivation in a comment citing `C:261-262`.
   (If you find a live-path shape where they differ, STOP and report it instead — that would be a finding.)
7. **F6 — the six derived-dead branches settled.** `C:931`, `C:938`, `C:1532`, `C:1559`, `C:1565`: re-derive each
   against the guard that makes it dead (the verifier names them); DELETE the dead branch with a one-line comment citing
   the earlier guard, or, if your derivation disagrees, keep it and add the killing test. `C:1519` (`init_resp_idx`):
   derive it fully (the verifier left it UNSURE) — same rule. Every deletion is proven by a mutant that would have
   reached it: build the hostile bundle the branch was written for and show the EARLIER guard fires with its exact
   reason.
8. **F7 + F8 + F9 + F10 + F13 + F23 — exact reasons everywhere.** Convert the remaining 16 `in out` fragment
   assertions to exact `==` f-strings built from the test's own values (the technique of `T:1609/1577/1622/1636`); for
   `test_neg_nan_timeline` assert the exact prefix through the line number and `endswith` nothing — assert the
   JSONDecodeError text via `json.JSONDecodeError` raised on the same bytes (compute it, don't type it). `T:2350`
   asserts the exact recorded-deficit reason. `T:2402` comment corrected. `T:2284` becomes `pytest.raises(FileNotFoundError)`
   (singular) or is deleted as vacuous — pick and say why. `test_ck8_f42_wrong_startup_pin` is parametrised over the
   WHOLE `checks` dict (test count follows the pin count; exact reason per key). `_EXPECTED_STARTUP_KEYS` hoisted to
   module scope so the exact `missing keys` list is computable.
9. **F11 + F12 + F20 + F24 + F25 — small rules.** `owned_zombies` (`_SCAN_HEADER_RE` group 8) is validated as a strict
   int `>= 0` and, when `> 0`, the PASS line reports it (the producer's classification stays; the checker just refuses
   garbage) — one red test with `owned_zombies=-1` and one with `abc`. `C:472`/`C:477` read the pinned values from
   `pins.py`, not literals (a test monkeypatches the pin and asserts the reason follows it). Role SEQUENCE tests: a
   reordered `['user','system']` and a duplicated `['system','system','user']` each rejected with the exact reason
   (mutant ROLES-SET must die); if `_POST_ROLES_STREAM == _POST_ROLES_NONSTREAM` is intended, say so in one comment.
   Version strings: `C:1` and `T:1` both v2.2. A25 fallback (`C:1735-1738`): on a pure reorder report the first index
   where executed != expected (`check sequence mismatch - first out of order at #k: got X, expected Y`); red test
   with a reorder.
10. **F19 — the fixture never hardlinks tracked sources.** `T:467-468` copies `proofs/S0-01/tools/` with
    `shutil.copy2` (a real copy), never `os.link`; a test asserts `os.stat(...).st_nlink == 1` for the copied tee and
    that writing the copy leaves the tracked file's sha unchanged.
11. **F21 — the real-leg skips become STRICT xfails keyed on the exact reason.** `T:2764-2777`: replace the
    substring-matched `pytest.skip` with `pytest.xfail(strict=True)` on an EXACT match of the three known-stale
    reasons (`probe_sha256 mismatch`, `agent_interpreter_realpath mismatch`, `spawned_at_utc is later than the first
    frame` — the golden captures predate the current tools; the re-capture retires them). Any other Failure fails.
    After the re-capture these xfails turn into failures by design — say so in the docstring.
12. **F14/F15/F22/F16 — report discipline.** PIN sha that exists (`git cat-file -e`), test counts PASTED from
    `scripts/test_summary.sh`, every Done row with `file:line` on the FINAL tree, every not-done reason true
    (`tests/test_s0_01_pc_post_scan.py` + `tests/test_s0_01_audit_cp5_controls.py` RUN here: 11 passed in 1.71 s), the
    F41 gates carried honestly. Note for the record: the coordinator's ruling R1 stated the parent's expected failure
    as `drained is not true`; the real one-frame SIGTERM status is fully forwarded so the parent rejects on
    `write_errors is not empty` — the test is red on the parent either way (F16, no code change).

## Mutants (scratchpad copies; `git status --porcelain` clean on both files after each; paste the table)
The verifier's 28 + 2 controls (tables A, C, D of the verdict) re-run on the final tree — every survivor now KILLED by
a NAMED test: FINAL-RELAXED-fwdc2a/fwda2c/recc2a/reca2c/seq/stdin, RUN-DIFF2, RUN-RECDEF2, RUN-NOSUM (now deleted —
state N/A with the derivation), ROLES-SET, TEEPAR-OFF, F43-ATTRS-OFF, F43-SCAN-OFF — plus new: CAP-ZERO-ACCEPTED
(drop the positivity floor), WALK-AFTER-READ (move the walk back below the read), REQFILE-EXISTS (drop `S_ISREG`),
ALLOWLIST-NAME-ONLY, ZOMBIES-UNCHECKED, LITERAL-PINS (revert F12), A25-MEMBERSHIP (revert F25), HARDLINK-FIXTURE
(revert F19 — killed by the `st_nlink` test). The A5e 24-guard combined mutant (27 `if` lines at HEAD) re-run once
on the full 3-file suite: all 24 still die.

## Gates (paste verbatim)
`bash scripts/test_summary.sh tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_audit_cp5_controls.py
tests/test_s0_01_pc_post_scan.py` twice (the verifier's 3-file set: 315 passed / 10 skipped baseline — state the
delta and why) · `python3 -m pyflakes` on both files · `python3 scripts/lint_delta.py --base
origin/claude/soundbox-kit-migration-iz1jwf` clean on your files · the real tee under SIGTERM and clean exit through
the rewritten checker (the verifier's `vck9/teerun/run_real_tee.py`) still ACCEPTED · collection count = passed +
skipped/xfailed. PC leg: NOT run here (coordinator's). Report shape: DONE table (finding · change · file:line ·
red-before verbatim or CONTROL+killer · green-after), MUTANT table, PROBE table, NOT_DONE, DISCREPANCIES, SELF-ATTACK.
