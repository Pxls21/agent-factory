# VERIFY-N5l — adversarial verification of S0-01 probe round 15 as LANDED (8b387d2, in the PIN): the ELOOP behavioral red, the v3 read-primitive ports, the real-emitter fd census, the scoped `close_fds` pin, the compile-and-collect driver — graded against VERIFY-N5k's three findings and the probe's CONTRACT, never against the builder's own cases (verify lane: PC Hermes `adversarial-verifier` on the CLOUD verify route — the SINGLE-MODEL RULE applies: the builder ran on the same cloud model, so you return FINDINGS, no gate verdict; sandbox fallback Opus 5 `adversarial-verifier`)

PIN: `efde78d`

**What you grade.** `proofs/S0-01/tools/acp_probe.py` (P, 678 lines) and `tests/test_s0_01_acp_probe.py` (T, 3868 lines) at the PIN, the
driver `tasks/briefs/s0-01-n5l-support/mutants.sh` (D, 141 lines), the builder's report `tasks/briefs/s0-01-n5l-support/N5l-report.md`
(its own lint: `33 refs — OK 30, NEAR 3`), the pack `tasks/briefs/s0-01-n5l-support/VERIFY-N5l-pack.md` (START FROM IT), and the
predecessor verdict `tasks/briefs/s0-01-n5j-support/VERIFY-N5k-report.md` (F1 the `O_NOFOLLOW` drop survived `113 passed`; F2 no real-emitter
census; F3 a comment-defeatable `close_fds` substring — the three findings this round claims to close). The corpus is a DECLARED input:
`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden` (read-only; the coordinator's sandbox reads the same five legs,
142 files). Counts carry their set id (`scripts/pc_suite.sh set-id -- <files>`): the coordinator's bare gate read
`RESULT: rev=97bb0c01f8e0 files=4 deleted=0 runs=2 tests=a5097bab1417 identical=yes rc=0 summary="124 passed in 48.59s 124 passed in 47.73s"`
and the driver `EXPECTED=10 KILLED=10 SURVIVED=0 INVALID=0 CONTROL=1`; the lane's 13-file set `1352 passed, 13 xfailed` (c62435272c99).

## Items (every item = a reproduced probe with its exact command, output and file:line)
- **V1 — F1 closed BEHAVIORALLY, not by inventory.** Reproduce the landed refusal: a final-component symlink to a regular file under
  `_read_regular` → `errno.ELOOP`, no content returned; the real fixture-loader chain (a `neg-malformed-initialize.json` symlink) → exit 64
  with the exact stderr the test pins (`T:3672-3702`). Then the AF-AP-80 lens: drop `O_NOFOLLOW` in a scratch copy and run the WHOLE file
  — which tests go red (name them)? If only the direct primitive test does, say whether the caller-chain test also reads through the mutated
  primitive (it must) and prove it with the mutant. A red that depends on `errno == ELOOP` alone: what does a `os.open` without `O_NOFOLLOW`
  return on a final symlink (it follows) — is there any platform/mount where the landed test passes vacuously?
- **V2 — the census is the REAL emitter.** `test_probe_census_agent_sees_no_framedir_fd_on_final_bytes` (`T:3852-3867`) launches the census
  agent through `_run_probe` → the production `Popen` at `P:371-374`. Attack: does `_run_probe` in the TEST reach the same `Popen` call the
  PRODUCTION `main` reaches (trace both paths by line); can the census agent see a fd that is open in the parent but closed by
  `close_fds=True` — i.e. is `CENSUS=0` proving the property or proving `close_fds` alone? Add a scratch mutant that leaks a DIFFERENT fd
  (a pipe, not the framedir) and check the census counts it; if it does not, the census is narrower than its name.
- **V3 — the scoped AST pin.** `_agent_popen_close_fds_value` (`T:3583-3612`): selects a `subprocess.Popen` assigned to `proc`, refuses
  `**kwargs`, requires exactly one literal-boolean `close_fds`. Attack the selector: a second `Popen` not assigned to `proc` (a helper that
  launches the agent through an alias `run = subprocess.Popen; proc = run(...)`); `subprocess.Popen` imported as `from subprocess import
  Popen`; `close_fds=bool(1)`; the keyword supplied via a dict `**opts` (refused — good — but does the REFUSAL make the test red or silently
  pass?); a `proc = ...` assignment inside a nested function. For each: does the pin go red, and is that the right outcome?
- **V4 — the ported v3 tests.** Regular bytes (`T:3705-3711`), the named refusals FIFO/directory/devzero/AF_UNIX (`T:3737-3768`), no fd on
  refusal (`T:3771-3787`): reproduce; then check the refusal MESSAGES are asserted exactly (`str(caught.value) == expected`) and that the
  expected strings are not derived from the code under test (a mirror, AF-AP-80's sibling). The AF_UNIX shape: the short-path helper
  `_short_unix_socket_path` (`T:257-258`) and its negative control (`T:3718-3734`, the long-path refusal) — AF-AP-82: does the negative
  control reproduce the SAME failure class the lane hit (`OSError: AF_UNIX path too long`) and does cleanup leave `/tmp/n5l-sock-*` empty
  after a failed test? Run the shape test twice and list `/tmp/n5l-sock-*` after.
- **V5 — the driver's validity (AF-AP-78).** `D:81-94` compile + collect-only per row, INVALID gated (`D:96-100`), the FIFO row under
  `timeout 15s` (`D:102-110`). Prove the driver imports the MUTANT: add a probe row whose edit raises at import and confirm it is reported
  through THAT error; confirm the docstring control SURVIVES; then rerun the ten rows (`EXPECTED=10 …`); paste every line. The
  `READ_NONBLOCK_DROP` row is killed by a TIMEOUT (rc 124) — is a hang the intended red, or would a bounded refusal be the honest oracle?
  State what the landed primitive does on a FIFO with no writer (nonblocking → the named refusal) and whether the timeout kill masks a
  different failure.
- **V6 — the census + census agent as PRODUCTION-shaped evidence.** The agent writes `CENSUS=<n>\n` after resolving `/proc/self/fd` — which
  fds does it EXCLUDE (stdio, the census file itself, the pipe to the parent)? Enumerate them from the code; a mutant that leaks a fd the
  agent excludes is invisible — name that blind spot as a declared limit or a finding.
- **V7 — the real-leg suite under the declared corpus.** Run the probe test file with the PC corpus (`S0_01_VENUE=pc …`): paste the count
  and its set id; then with `S0_01_REAL_LEG_DIR` pointed at an EMPTY directory: the real-producer tests must FAIL (not skip) — paste
  `N failed`; then unset `S0_01_VENUE` (CI's declaration): the real-producer tests SKIP by declaration — paste `N skipped`.
- **V8 — the blast radius the lane could not map.** GitNexus reported `risk: UNKNOWN` for `_read_regular`'s callers; the pack maps
  `_sha256_file`, `_write_evidence`, module hashing and `main`. Enumerate EVERY read of a file in P that does NOT go through
  `_read_regular` (grep `open(`, `read_bytes`, `read_text`, `os.open`) and say for each whether a final symlink there is a hazard the
  contract cares about (evidence files, fixtures, the framedir leaves).
- **V9 — the report.** Re-verify the FILE IDENTITY (FINAL) table against the PIN (the coordinator read 3/3); `report_lint.py` with the map
  `--map test=tests/test_s0_01_acp_probe.py --map probe=proofs/S0-01/tools/acp_probe.py --map driver=tasks/briefs/s0-01-n5l-support/mutants.sh
  --min-refs 12`; grade every VERIFIED claim you can reproduce in ≤ 5 min; UNSURE for the rest, never false. The "DISCREPANCIES" section
  says the pin is STRICTER than the brief's "absent or True" — is any legitimate launch shape in P now impossible (a `Popen` without the
  keyword)? State it.

**Output.** `tasks/briefs/s0-01-n5l-support/VERIFY-N5l-report.md`: FINDINGS first, ranked by severity with the fix shape (no verdict line —
the single-model rule; write `NO VERDICT (single-model rule): findings only` as line 1), then per item SOLID/UNSURE with the command, the
output and `file:line` (`P=`, `T=`, `D=`; declare the map at the top); a NOT-done list. Report lint with your map, `--min-refs 15`, the
bounded rule (three rounds, then paste and finish). No self-acceptance language; no edits to the landed bytes (scratch mutants only).
