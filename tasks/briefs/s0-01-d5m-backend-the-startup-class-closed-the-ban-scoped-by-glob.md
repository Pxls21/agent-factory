# Lane D5m — S0-01 scripted backend round 16: every startup and per-request path guarded, the `!= MARKER` ban scoped by glob and honest about its reach, failure-aware readiness waits, a true cost sentence (build lane: PC Hermes `code-implementer` when the slot is free, else sandbox Opus 4.6 `code-implementer`)

PIN: (HEAD at dispatch — the commit carrying this brief; the report header says "PIN: `<sha>`".) The backend's last checkpoint
is 8aa = `2199747` (local; the pushed head carrying the same bytes was `68fb454`): `proofs/S0-01/tools/scripted_backend.py` 819
lines sha `04da144a…`, `tests/test_s0_01_scripted_backend.py` 2177 lines sha `cd51ed65…`, `tests/red/test_s0_01_backend_credential_screen.py`
1234 lines sha `40455da9…`, `proofs/S0-01/tools/cost_probe.py` 128 lines sha `a1b86008…`. **Dispatch order:** this lane starts only
after lane P5b's landing — P5b holds an uncommitted edit in `tests/test_s0_01_scripted_backend.py` (`test_build_capture_record_roundtrip_check`,
the shared `synthetic_leg` fixture); your PIN will carry it. Never revert it.

**Why:** VERIFY-D5l (report `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/wf-results-r5/VERIFY-D5l.md` —
READ IT WHOLE FIRST; it is the contract for this round) graded round 15 NOT-READY with four small blockers, every one reproduced on
the PIN: **F1** the `!= MARKER` ban is an AST walk (good) over TWO hard-coded files — the sweep's R6b evasion is live: the canonical
banned form planted in `tests/test_s0_01_negative_contract.py` → `2 passed`; **F2** `--pidfile` is the third startup path the
backend opens and has no guard: a FIFO there hangs the process forever AFTER the socket is bound (a supervisor waits on a port that
never serves), a directory gives an uncaught traceback (rc 1, no named reason) — the flag is passed by `pc_backend_restart.sh` and
`run_s0_04_legs.sh`; **F3** the cost docstring's number (0.378 s, "~0.4 s on the measured PC") is the ORDINARY vector measured in the
SANDBOX, while the sentence names the bound-exceeding-token vector, which the lane's own PC probe measured at 1.864 s — 4.7× low,
and the parent's "~2 s" sentence was right to 7 %; **F4** the four module-scoped readiness loops are success-only waits (`except
OSError: sleep` with no `proc.poll()` and no post-loop assertion — SWEEP-tests row 9.1): a backend that exits 2 before binding burns
the whole 10 s deadline and fails as `ConnectionRefusedError`, its own reason never surfacing. Also: **F5** the walker catches 6 of 14
spellings and documents none of the 8 it misses; **F6** the self-sweep was a SAMPLE presented as an enumeration; **F7** the
per-request record write blocks forever on a FIFO planted at the predictable next slot; **F8** a stray `UTF8` in a docstring. What
held and must stay held: the record pinned at every served path (three fidelity mutants die), the three extras literals cross-pinned,
the 4315-member table regenerating byte-identically, the two startup guards exactly pinned, `report_lint` MISS 0, 539 ×2 on both venues.

**Inputs (read in this order):** VERIFY-D5l whole · your predecessor's report `tasks/briefs/s0-01-d5l-support/D5l-report.md` and
brief · `tasks/briefs/s0-01-sweep-support/SWEEP-tests.md` rows 4.4, 9.1, 11.4, 18.1 (the backend rows) · `docs/INCIDENT-LOG.md`
(AF-AP-30, AF-AP-37, AF-AP-40, AF-AP-55, AF-AP-60, AF-AP-61) · `scripts/ap_screen.py` (`screen()` accepts non-regex matchers — read
it; the AST-backed screen row is the COORDINATOR's follow-up, not yours) · the pack `scripts/lane_context.sh -q 'where does the
backend open a path at startup or per request' -s main _open_record _fingerprint -o pack.md proofs/S0-01/tools/scripted_backend.py`
(run it first; attach it to your report).
**Scope (exactly these + your report):** `proofs/S0-01/tools/scripted_backend.py` · `tests/test_s0_01_scripted_backend.py` ·
`tests/red/test_s0_01_backend_credential_screen.py` · `proofs/S0-01/tools/cost_probe.py` (only if the F3 re-measurement needs a
column) · report `tasks/briefs/s0-01-d5m-support/D5m-report.md`. NOT yours: `pins.py`, the checker, the probe, the tee, the PC tools,
`.claude/hooks/*`, `scripts/*`. Shared-tree rules: never `git stash/checkout/restore/reset/add/commit/push`; every gate from a
`git archive <PIN> | tar -x` copy under /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/d5m/ with your
files copied in (`scripts/lane_gate.sh -r <PIN> -f "<your files>" -t "tests/test_s0_01_scripted_backend.py
tests/red/test_s0_01_backend_credential_screen.py" -n 2`, ONE foreground call — it runs ~6 min in the sandbox; set `LANE_GATE_DIR`
under your scratch dir); explicit `--basetemp`; every FIFO probe under `timeout 12`; kill only your own processes by pid (never
pkill/pgrep -f); NEVER background a run and stop; no outward actions; NO PC bridge from a sandbox lane (the coordinator runs the PC
gate; a PC lane runs the suite on the PC itself); never read, print or commit a credential. Interpreter `/root/venv-agent-factory/bin/python`.

## Design (pinned — build it, do not redesign it; line numbers are 8aa's)
1. **F1 — the ban's scope is the glob, and the scope is itself asserted.** `red:1213-1216`: `targets = sorted(root.glob("test_s0_01_*.py"))
   + sorted((root / "red").glob("test_s0_01_*.py"))`; `assert marker_not_equal_asserts(p) == []` for every target, the failing
   path named. Plus a scope pin: `assert {p.name for p in targets} >= {p.name for p in root.glob("test_s0_01_*.py")}` so a future
   hard-coded list cannot come back. Red test (scratch): the verifier's plant in a copy of `tests/test_s0_01_negative_contract.py`
   under a scratch tree makes the walk report `('test_s0_01_negative_contract.py', <line>)` — paste it. The glob-scoped walk over
   the 15 real S0-01 test files must return 0 hits (the verifier measured 0 — paste yours).
2. **F2 — `--pidfile` guarded, BEFORE the bind.** Move the pidfile block above `ThreadingHTTPServer(...)` (`backend:806`) so a refusal
   leaves the port unbound; refuse a path that exists and is not a regular file (`stat.S_ISREG` on `lstat` — a dangling symlink is
   refused too, like `--record-dir`) with `scripted_backend: --pidfile is not a regular file: <path>` on stderr and `return 2`; the
   same shape as the token guard. Tests, each with the exact stderr line: a FIFO (RED on the PIN by `TimeoutExpired` — paste), a
   directory (RED on the PIN: rc 1 + traceback — paste), a dangling symlink; a symlink to a regular file still starts (no false
   positive). Prove the port stays unbound on refusal (connect → `ConnectionRefusedError` immediately).
3. **F3 — one true cost sentence.** Re-measure with `cost_probe.py` on YOUR venue (min of 5, both harnesses, one window) and write
   `backend:77-82` as: the vector NAMED (`bound-body`, a 1 MiB body with a bound-exceeding token), the venue NAMED per number (the
   verifier's cells: PC 1.86 s / sandbox 1.03 s for that vector; ordinary 1 MiB body PC 0.72 s / sandbox 0.38 s), and the harness
   note (http.client and a raw socket within 2 %). No number in the sentence that is not in `cost_probe.py`'s table in your report,
   with the venue and the command that produced it (AF-AP-37).
4. **F4 — the readiness waits are failure-aware, ONE helper.** Extract `_wait_ready(proc, port, deadline_s) -> None` used by all four
   fixtures (`main:67-78`, `:265-277`, `:562-574`, `red:43-54`): the loop condition includes `proc.poll() is None`; after the loop,
   `assert ready and proc.poll() is None, f"backend failed to start (rc={proc.poll()}): {stdout}"` reading the backend's captured
   stdout/stderr (the fixture's `stdout=PIPE` is read, never left unread). Unit-test the helper with a fake process that exits 2
   after printing a reason: the failure message carries the reason within 1 s, never `ConnectionRefusedError` after the deadline.
   The verifier's R9A mutant (the backend returns 2 before the bind) must now fail the fixture in < 2 s with the backend's own line.
5. **F5 — the walker's reach stated and widened where cheap.** Extend the predicate to `ast.NotIn`, `ast.IsNot` and
   `ast.UnaryOp(ast.Not, ast.Compare(Eq))` with `MARKER` as an operand; three new two-sided scratch controls (`assert not (x ==
   MARKER)`, `assert x not in (MARKER,)`, `assert x is not MARKER` each report ≥ 1; the positive control stays 0). The docstring at
   `red:1185` names what stays OUT of scope and why (aliasing `M = MARKER`, a helper function, `operator.ne`, an attribute
   `m.MARKER`) — an honest documented limit, never a claim of closure.
6. **F7 — the per-request record path cannot block.** Before `(self.record_dir / f"{n:06d}.json").write_text(...)` (`backend:536`):
   if the slot exists and is not a regular file, respond 500 with a body naming `record slot is not a regular file` and log one
   JSON line with the reason — never block, never skip silently. Red test: `--allow-existing-records` + a FIFO planted at
   `000001.json` → a response within 5 s (RED on the PIN: `TimeoutError` after 6 s — paste), status 500, the next request 200 with
   the next slot written.
7. **F8** — restore `invalid-UTF-8` at `red:1069`.
8. **F6 — the self-sweep is an ENUMERATION.** Every class row carries the COUNT of instances found and the method (AST node type or
   the grep), and either the run that settles the class or "sampled N of M" — never SAFE over a sampled class. The sweep's numbers
   are the floor (77 `[-1]` sites, 14 poll loops, 67 presence-gated forms over these files); SWEEP row 11.4 (`_free_port()` TOCTOU)
   gets a row — either a fix (bind the port once and hand the socket's fd/port to the child, or retry on `EADDRINUSE` in the
   fixture) or a documented limit with the reason.
9. **Mutants:** the verifier's 18 (R6B-THIRD-FILE), 19 (R9A-STARTUP-FAILURE), 20/21 (PIDFILE-FIFO/DIR), 22 (RECFILE-FIFO) must DIE
   with named killers; the lane's previous set (the three record-fidelity mutants, the three extras drifts, the six startup-guard
   mutants, UQ-REPLACE-BOTH) re-run and still dead; paste the killer line per mutant with the env stated.
10. **Report discipline:** FILE IDENTITY of the FINAL bytes; every `file:line` from `grep -n` on the FINAL bytes and
    `python3 scripts/report_lint.py <report> --map backend=proofs/S0-01/tools/scripted_backend.py --map main=tests/test_s0_01_scripted_backend.py
    --map red=tests/red/test_s0_01_backend_credential_screen.py` pasted with MISS 0 (round 15 achieved it — keep it); the two gate
    RESULT lines pasted; every red-before on 8aa pasted beside its green-after; `ap_screen.py` on the backend (the two AF-AP-40 hits
    at `backend:796/800` classified by run) and `--tests` on both test files (0, de-vacuoused against the parent as the verifier did);
    the pack attached; NOT-done first-class. NOT this lane's: the AST-backed TEST_SCREEN row (AF-AP-61b — the coordinator, after
    P5b's edit-snapshot edits land), the checker's consumers.
