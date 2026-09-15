# VERIFY-N5m — adversarial verification of S0-01 probe round 16 (lane N5m) as LANDED

**Authorization.** This is defensive verification of the owner's own S0-01 ACP-conformance probe. The
fd-census / close_fds / symlink-refusal work is a security boundary on the owner's system. Attack the
TESTS and the DRIVER, not to weaken them — to prove they cannot pass a broken probe.

**Single-model rule:** you run on the cloud verify route grading a cloud-built lane. Report FINDINGS
only, ranked, with a repro for each. NO merge verdict. Report everything; do not severity-filter.

**Ground (LANDED at the PIN):** N5m = probe round 16 closed the four VERIFY-N5l findings at the
TEST/DRIVER layer with `proofs/S0-01/tools/acp_probe.py` UNCHANGED (`git diff --quiet <PIN> --
proofs/S0-01/tools/acp_probe.py` = rc 0). The four fixes:
- **F1 the general fd census.** `_CENSUS_AGENT` (tests/test_s0_01_acp_probe.py ~3873-3902) enumerates
  every `/proc/self/fd` entry, resolves each `readlink`, and computes `CENSUS` = the count of fds NOT
  in the expected set `{0,1,2,output-fd}`. `test_probe_census_agent_sees_only_stdio_and_its_output_fd`
  (~3905-3931) requires the exact fd set `{0,1,2,3}`, pipe/tty stdio targets, and `CENSUS=0`. The driver
  (`tasks/briefs/s0-01-n5l-support/mutants.sh`) keeps `FD_LEAK_TRIPLE` and adds `FD_LEAK_PIPE`.
- **F2 the scoped AST walk.** `_agent_popen_close_fds_value` (~3591-3630) traverses production `main`
  pruning nested `FunctionDef`/`AsyncFunctionDef`/`Lambda` scopes; the new control (~3654-3680) accepts
  one nested-helper launch + one guarded main launch and rejects two main launches.
- **F3 the literal denominator + self-test.** `mutants.sh` has a literal `EXPECTED=11` (driver:7) and a
  `--self-test` (driver:18-52) that deletes a row in a scratch copy and requires the driver to report the
  mismatch (`KILLED=10 != 11` → inner rc 1 → wrapper rc 0).
- **F4 the fixture cleanup.** `_short_unix_socket_path` is a context manager whose `finally` removes the
  created leaf and its `/tmp/n5l-sock-*` directory; both callers keep their allocated-path body inside it.

**Coordinator gates already reproduced (do not just re-cite — attack past them):** static-copy
`126 passed` ×2 (identical=yes, tests=a5097bab1417); driver `EXPECTED=11 KILLED=11 SURVIVED=0 INVALID=0
CONTROL=1`; self-test wrapper rc 0; report_lint 20/OK-19 (maps probe=/test=/driver=); AP-screen delta on
the changed test = 0.

**Boundary.** `proofs/S0-01/tools/acp_probe.py` (P, read-only — touch ONLY to build a hostile scratch
copy, never the tracked file), `tests/test_s0_01_acp_probe.py` (T), `tasks/briefs/s0-01-n5l-support/mutants.sh`
(D), your report `tasks/briefs/s0-01-n5l-support/VERIFY-N5m-report.md`. Nothing else tracked. The class list
of the S0-01 sweeps (AF-AP-78/80/81/82/84/85/87) is your preflight.

## Items (V1-V9; every claim gets an independent repro through a scratch copy — never git-restore/stash the tree)

1. **V1 attack the census generality (F1).** Build a hostile scratch copy of production `main` that inherits a
   NON-framedir fd the census could miss: a high fd number, an `O_PATH` fd, a directory fd, an `eventfd`, a
   second inherited pipe on a non-adjacent number. Run `_CENSUS_AGENT` through the copy. Does `CENSUS` count
   it (expected) or miss it? If any inherited non-stdio fd yields `CENSUS=0`, that is a BLOCKER (the census is
   not general). Confirm the test asserts the EXACT set `{0,1,2,3}`, not a subset or a floor.
2. **V2 attack the AST scope (F2).** Can a SECOND real agent launch escape `_agent_popen_close_fds_value`?
   Try: a launch inside an `if`/`try`/`with`/`for` at main level (must be DETECTED); a launch inside a nested
   `def` that main actually CALLS (is it correctly pruned as "not a direct main launch" or does that hide a
   real second launch?); a launch via a bound method / `functools.partial` / a subprocess alias
   (`sp.Popen`, `from subprocess import Popen as P`). State which forms the walk sees and which it does not,
   and whether any blind spot hides a real close_fds-bypassing launch.
3. **V3 attack the denominator (F3).** Is `EXPECTED=11` truly a literal independent of the observed rows, or
   is it derived anywhere? Mutate the driver: lower `EXPECTED` to 10 — does `--self-test` catch it (it must)?
   Add a row without bumping EXPECTED — INVALID or SURVIVED? Confirm the self-test's own scratch copy cannot
   be satisfied by a weakened literal (a scratch `EXPECTED=10` mutant: inner rc 0 but outer self-test rc 1).
4. **V4 attack the fixture cleanup (F4).** Does the context manager remove its dir on EVERY exit — a raised
   exception mid-body, an early `return`, a `KeyboardInterrupt`? Force each and glob `/tmp/n5l-sock-*`
   before/after. Are BOTH callers inside the `with`? A caller that allocates the path outside the manager
   leaks — find one if it exists.
5. **V5 the driver is valid (AF-AP-78).** Every mutant row compiles and collects before the test runs;
   INVALID is gated; no row "kills" through a SyntaxError. Re-run the driver and the self-test; paste both.
6. **V6 identities.** Recompute the sha256 + line count of P, T, D against the PIN. P must be byte-identical
   to round 15. Paste `git diff --quiet <PIN> -- proofs/S0-01/tools/acp_probe.py; echo rc=$?`.
7. **V7 the gates.** Re-run the probe set (`S0_01_VENUE=pc` `-n 8` set of the 13 files if time allows, else the
   single probe file) and paste the exact `pytest-summary` + set id. Re-run the driver + self-test.
8. **V8 the AP screen.** `python3 scripts/ap_screen.py --s0-01 tests/test_s0_01_acp_probe.py`; classify every
   hit as pre-existing or new. Any NEW class is a finding.
9. **V9 report.** Rank findings BLOCKER/SHOULD-FIX/NIT with a one-line repro each; NOT-DONE list; report_lint
   with the probe=/test=/driver= maps; end with the file identities. No verdict (single-model rule).

Retro: bake nothing yourself; name any new class for the coordinator to register.
