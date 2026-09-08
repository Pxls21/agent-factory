# VERIFY-D5m — adversarial grade of lane D5m (S0-01 scripted backend round 16: the `--pidfile` guard before the bind, the `!= MARKER` ban scoped by glob with the scope asserted, failure-aware readiness waits, the per-request record slot refused, a true cost sentence)

You are an adversarial-verifier (the PC Hermes verify lane; the venue map `tasks/briefs/pc/VENUE-MAP.md` applies). Repo
agent-factory, branch claude/soundbox-kit-migration-iz1jwf. **PIN: `246bec7` plus the lane patch pc-lane.sh applied on it** —
the SAME tree shape lane D5m ran in: the PIN carries the checker, probe and tee rounds; the patch carries lane P5b's still-unlanded
files (`proofs/S0-01/pins.py`, the PC tools, `tests/conftest.py` with the shared `synthetic_leg` fixture — CONTEXT, never yours
to grade beyond what the backend test consumes) and D5m's FINAL bytes: `proofs/S0-01/tools/scripted_backend.py` (894 lines, sha
`1968c156…`), `tests/test_s0_01_scripted_backend.py` (2361, `02b4cd9a…`), `tests/red/test_s0_01_backend_credential_screen.py`
(1278, `71aafdb7…`), the lane's report `tasks/briefs/s0-01-d5m-support/D5m-report.md` and VERIFY-D5l's report. Grade the bytes
of your worktree from a scratch copy under your lane's scratch dir (`git status --porcelain` lists the patch's files — stamp their
sha256 in your identity table so the coordinator can match them to the checkpoint that lands them); every mutant on scratch
copies; every pytest run with an explicit `--basetemp` and the venue exports (`S0_01_VENUE=pc
S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`); every FIFO/hang probe standalone under `timeout` with a PID-scoped
watchdog, never through pytest; kill only what you start, by pid; never background a run and stop; no outward actions; never read,
print or commit a credential. Authorization: the owner's own scripted model backend under test on the owner's system.

**Inputs (read in this order):** VERIFY-D5l's report `tasks/briefs/s0-01-d5m-support/VERIFY-D5l-report.md` (the round's
contract: F1-F4 blocking, F5-F9, its mutant table) · the lane brief
`tasks/briefs/s0-01-d5m-backend-the-startup-class-closed-the-ban-scoped-by-glob.md` (the pinned design, items 1-10) · the lane's
report `D5m-report.md` (FILE IDENTITY, the red-before/green-after pairs, the cost table, the 19-spelling walker table, 33 mutant
rows, the 18-class enumeration, DISCREPANCIES 1-8, NOT DONE 1-7) · `docs/INCIDENT-LOG.md` (AF-AP-37, AF-AP-40, AF-AP-59,
AF-AP-60, AF-AP-61, AF-AP-65).

## Item 0 — the mechanical gates, pasted
`python3 scripts/report_lint.py tasks/briefs/s0-01-d5m-support/D5m-report.md --map backend=proofs/S0-01/tools/scripted_backend.py --map main=tests/test_s0_01_scripted_backend.py --map red=tests/red/test_s0_01_backend_credential_screen.py`
(the coordinator read `63 refs — OK 52, NEAR 0, MISS 0, UNCHECKABLE 11`); `ap_screen.py --s0-01` (66 production hits over 11
files — classify the BACKEND's share by RUN; the lane's report has a table with "the 0 de-vacuoused" — agree or disagree);
`--tests`; pyflakes; the FILE IDENTITY table; the two test files run directly: the lane's own `548 passed` ×2 on this tree shape,
the coordinator's PC run of the same shape (pasted in the dispatch note) — agree or disagree by your own run. State first-class
that the three-file archive gate WITHOUT P5b's files is red for exactly ONE reason (`fixture 'synthetic_leg' not found` /
`pins.PINNED_LEG_FILES`): the backend test now depends on P5b's `tests/conftest.py` and `pins.py` — is that dependency the right
shape (one shared fixture) or a coupling that lets a P5b change break the backend suite silently?

## Items
1. **F2 — the `--pidfile` guard BEFORE the bind (`backend`, the moved block).** Reproduce the lane's four live probes (FIFO 0.09 s,
   directory, dangling symlink, symlink-to-regular starts) standalone under `timeout`; prove the port is unbound on refusal by a
   method that DISCRIMINATES order (the lane says its own `ConnectionRefusedError` check does not — DISCREPANCY 2 — and added an
   occupied-port test: attack that test); the residual the lane declared (a backend that fails to bind leaves a pidfile behind —
   DISCREPANCY 6): does the S0-04 runner really handle it (`run_s0_04_legs.sh`, `pc_backend_restart.sh` — by READ of both)?
   NOT DONE 6: the guard is check-then-use — construct the race (replace the path between the stat and the write) and measure the
   window; is `os.open(O_NONBLOCK|O_NOFOLLOW)` the fix and what would it change?
2. **F1 — the ban's scope is the glob (`red:1213-1216`, the scope pin).** Attack the scope pin: a test file named outside the
   glob (`test_s0_01x_*.py`, `test_s001_*.py`, a subdirectory beyond `red/`), a file the glob matches but the walker cannot parse
   (a syntax error — skipped silently or red?), a symlinked test file; the lane's third-file plant reproduced on YOUR scratch copy.
3. **F5 — the walker's reach (the 19-spelling table, `red:1185`, `:1198-1203`, `:1236-1243`).** Reproduce the table by RUN (11
   caught / 8 not); attack the six declared evasions with a seventh and eighth spelling the table does not list (`MARKER in
   (x,)` negated by `assert len(...)`, a chained compare `a != MARKER != b`, `assert (x != MARKER) is True`, a match statement,
   an `if x == MARKER: raise` — the AF-AP-65 shape); does the docstring's OUT OF SCOPE block name every evasion you find, or is a
   new one a finding?
4. **F4 — `_wait_ready` (`main:113` and the four fixtures, `red`).** The fake-process unit test: attack the helper with a process
   that exits 0 before listening, one that listens and then dies, one that prints nothing (the message must still carry rc); the
   R9A mutant re-run (< 2 s with the backend's own line); DISCREPANCY 4: draining only an exited child — a child that exited but
   whose pipe holds > 64 KB (does the drain block?); the `stdout=PIPE` of a LIVE child — never read (a full pipe stalls the
   backend?): measure with a chatty backend.
5. **F7 — the per-request record slot (`backend:536` region).** The FIFO at `000001.json` → one 500 naming the reason, the next
   request 200 into the next slot: attack with a directory slot, a symlink slot pointing to a FIFO, a slot that becomes a FIFO
   between the check and the write (the same check-then-use class as item 1 — is it?), a FIFO at `000002.json` after a 500 at
   `000001.json` (does the counter advance past a refused slot, and is that the right semantics?).
6. **F3 — the cost sentence (`backend:77-84`) and every number in it.** Re-measure on the PC with `cost_probe.py`
   (`tasks/briefs/s0-01-d5j-support/cost_probe.py`, min of 5, one window): the lane's PC cells `bound-body 1.523 s`, `ordinary
   0.563 s`, harness 0.99-1.00x; the sentence's numbers must be in the table with the venue named — a number in the sentence
   not in any pasted table is AF-AP-37 (paste your table with load before/after).
7. **The record fidelity + extras + startup guards held from D5l (mutants 24-33).** Re-run on scratch copies: the three
   record-fidelity mutants, the three extras drifts, the six startup-guard mutants (SISREG-DELETED/TAUTOLOGY, RECDIR-DANGLING,
   TOKEN-MSG/RC-DRIFT/GUARD-ORDER), UQ-REPLACE-BOTH — killers pasted.
8. **F6 — the 18-class enumeration (the report's table with counts and methods).** Re-derive three rows by RUN (the `[-1]`
   population 93 vs D5l's 82 — DISCREPANCY 7; the 14 poll loops; the presence-gated forms) and SWEEP row 11.4's measurement
   (`_free_port()` TOCTOU — a documented limit: is the measurement right, and would `EADDRINUSE` retry in the fixture close it
   cheaply?); every `if <field> == <literal>:` without a raising other arm listed (AF-AP-65).
9. **The 33 mutants** reconstructed on YOUR scratch copies (never the lane's `probes/` driver): killed / survives with the killer
   line and the env stated; mutants ≥ 40 with your own additions (a `--pidfile` path that is a socket; `record slot` refusal
   message drift by one character; the readiness helper's deadline 0).
10. **Discipline** — file:line by `sed -n` on the tree; `report_lint.py` on your own report; the process census by pid (the
    lane's census read `/proc/<pid>/cmdline` directly — no `pgrep`).
11. **The design.** Is a glob-scoped AST walk the right home for a test-hygiene ban (vs the registry screen `scripts/ap_screen.py`,
    which the brief assigned AF-AP-61b to the coordinator — NOT DONE 4)? The check-then-use residual on both startup paths and the
    record slot: one structural fix or three? What must the round after this one do to make the backend MERGE-READY, and which
    items are the coordinator's (the P5b coupling, AF-AP-61b, the joint landing with P5b and A5k)?

## Report
Write it to `tasks/briefs/s0-01-d5m-support/VERIFY-D5m-report.md` inside your tree, draft after EACH item, and return it whole as
your final message. Findings: ALL, no severity filtering, each with file:line, expected vs observed, the failing input, the
minimal fix, the exact red test, SOLID/UNSURE; reproduced vs reviewed vs skipped; verdict MERGE-READY or NOT-READY with the
blocking set and the cheapest path; the items that are the coordinator's named as such.
