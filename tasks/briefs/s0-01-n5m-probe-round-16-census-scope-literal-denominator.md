# Lane N5m — S0-01 probe round 16: VERIFY-N5l's four findings closed — the census over EVERY inherited fd (an exact expected set, the FD_LEAK_PIPE row), the `close_fds` pin scoped to `main`'s launch, the driver's LITERAL denominator with a self-test, the socket fixture's cleanup under failure (build lane: PC Hermes `code-implementer`, the cloud build route; sandbox fallback `code-implementer`)

PIN: `2c7ed47`

**Ground.** Round 15 (lane N5l) LANDED as 8b387d2 and was graded by VERIFY-N5l (`tasks/briefs/s0-01-n5l-support/VERIFY-N5l-report.md`, findings
only, lint 50/50): F1 HIGH the census counts only fds that resolve to the framedir (`tests/test_s0_01_acp_probe.py:3820-3836`,
`_CENSUS_AGENT`) — an inheritable NON-framedir pipe through the same production `Popen` (`proofs/S0-01/tools/acp_probe.py:371-374`) read
`CENSUS=0` (AF-AP-85: a name that claims general fd containment over a subset census); F2 MEDIUM `_agent_popen_close_fds_value`
(`tests/test_s0_01_acp_probe.py:3583-3612`) walks the WHOLE module and goes red on a safe nested helper's own `proc = subprocess.Popen`
(`expected one agent Popen assigned to proc, got 2` — a false red); F3 MEDIUM the driver's `expected=$((killed + survived))`
(`tasks/briefs/s0-01-n5l-support/mutants.sh:138`) reads `EXPECTED=9 KILLED=9 SURVIVED=0 INVALID=0 CONTROL=1` with one row deleted (AF-AP-84);
F4 LOW the short-socket fixture (`tests/test_s0_01_acp_probe.py:3718-3733`) leaks its `/tmp/n5l-sock-*` directory when an assertion fails
after `mkdtemp`. The landed behavior is otherwise SOLID (V1 the ELOOP red through both chains; V3 the pin rejects alias/import-from/`bool(1)`/
`**opts`/absent/comment-only; V4 the ported v3 tests; V5 the driver imports the mutant; V8 every file read routes through `_read_regular`).
The probe test file reads NO corpus (`S0_01_VENUE`/`S0_01_REAL_LEG_DIR` are consumed by the checker and pc-tools suites, not here).
The pack over the lane's files is `tasks/briefs/s0-01-n5l-support/VERIFY-N5l-pack.md` (START FROM IT).

**Boundary.** `proofs/S0-01/tools/acp_probe.py` (P — touch ONLY if an item below needs it; expected: no production change),
`tests/test_s0_01_acp_probe.py` (T), `tasks/briefs/s0-01-n5l-support/mutants.sh` (D), your report
`tasks/briefs/s0-01-n5l-support/N5m-report.md`. Nothing else. The class list of the S0-01 sweeps (AF-AP-78/80/81/82/84/85) is your preflight.

## Items (in order; every item = the change + a deterministic LLM-free test with its negative control + a pasted line)
1. **The census over EVERY inherited fd (F1).** The census agent enumerates `/proc/self/fd`, resolves each entry (`readlink`), and writes the
   FULL inventory (`fd -> target`) plus a one-line `CENSUS=<n>` where n counts every fd that is NOT in the expected set {0, 1, 2, the census
   output file's own fd}. The test asserts `CENSUS=0` AND the exact inventory shape (three stdio entries resolving to pipes/ttys + the output
   file) — a general name now has a general census. Add the driver row `FD_LEAK_PIPE`: an inheritable `os.pipe()` read end created before the
   `Popen` + `close_fds=False` (no framedir involvement) — the census must read `CENSUS=1` with the pipe in the inventory; keep `FD_LEAK_TRIPLE`.
   Rename the test to say what it proves (`…sees_only_stdio_and_its_output_fd…`).
2. **The pin scoped to the launch it guards (F2).** `_agent_popen_close_fds_value` selects the `proc = subprocess.Popen(...)` assignment in
   `main`'s TOP-LEVEL body only (walk `main`'s `body`, not nested `FunctionDef`s); a nested helper with its own literal-True `proc` launch must
   NOT make the pin red (a new test with exactly that scratch shape → the pin stays green), while a second top-level `proc = Popen` in `main`
   still fails with `got 2`. State in the test's docstring the invariant it now pins (one agent launch in `main`).
3. **The literal denominator (F3).** `EXPECTED=11` (the ten rows + `FD_LEAK_PIPE`) as a literal at the top of D; the final gate
   `[[ $killed -eq $EXPECTED && $survived -eq 0 && $invalid -eq 0 && $control -eq 1 ]]`; the summary prints the literal. Self-test: D accepts
   `--self-test`, which copies itself to scratch with one `run_mutant`/row line deleted and asserts that copy exits NON-zero with
   `EXPECTED=11 KILLED=10 …` — paste both outputs (the real run and the self-test) in the report.
4. **The fixture cleanup under failure (F4).** `_short_unix_socket_path` callers wrap the body in `try/finally` (or a pytest fixture with
   teardown) so the `/tmp/n5l-sock-*` directory is removed on ANY exit; the control: a test that forces an assertion failure after allocation
   inside a `pytest.raises(AssertionError)` and then asserts `glob('/tmp/n5l-sock-*')` gained nothing (`find`-based, never `test ! -e` on a
   glob). Remove nothing that predates your lane.
5. **Gates.** The probe file twice (`bash scripts/test_summary.sh tests/test_s0_01_acp_probe.py` → paste both counts + `pc_suite.sh set-id`);
   the driver's full output + the self-test; the 13-file set ONCE with `-n 8` (`1352 passed, 13 xfailed` at 8b387d2, set c62435272c99 — paste
   yours with its set id; +N passed for your new tests, xfails unchanged); pyflakes on P/T rc 0; `bash -n D`; `git diff --check`; the AP screen
   on T (no NEW hit class beyond the pre-existing AF-AP-80 ×4 / AF-AP-57 ×1 — say which of the four AF-AP-80 hits are the inventory pins by
   design); report lint `--map probe=proofs/S0-01/tools/acp_probe.py --map test=tests/test_s0_01_acp_probe.py --map driver=tasks/briefs/s0-01-n5l-support/mutants.sh --min-refs 12`.

**Report.** `tasks/briefs/s0-01-n5l-support/N5m-report.md`: PROPOSAL line first; per item the pasted line and `file:line`; FILE IDENTITY (sha256 +
line count) for P/T/D before and after; the driver's two outputs verbatim; a NOT-done list. No self-acceptance; no edits outside the boundary.
