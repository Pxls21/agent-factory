# VERIFY-D5l — adversarial grade of lane D5l (S0-01 scripted backend round 15, the PC Hermes lane's output: the `!= MARKER` class banned structurally, the record pinned at every served path, ONE extras literal, FIFO/dangling-symlink startup refusals, honest cost prose)

You are an adversarial-verifier (Opus 5 in the sandbox, or the PC Hermes `adversarial-verifier` role). Repo /home/user/agent-factory,
branch claude/soundbox-kit-migration-iz1jwf. **PIN: `2199747c179c61a051073db853294e9ad072cb70`** (the checkpoint carrying the lane's three scope files + its
report + the PC patch; parent for the scope files = checkpoint 8w = `8695636`; the lane's own PIN was 58741bb — the scope files were
byte-identical there and at 8w's descendants). Grade the bytes of `git archive <PIN>` from a copy under the session scratchpad
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ (`vd15/`). Read-only git on the shared tree; every mutant on
scratch copies; every pytest run with an explicit `--basetemp` under your scratch dir; kill only what you start, PID-targeted; never
background a run and stop; no outward actions.

**The ONE bridge action you MAY take (owner ruling 2026-09-07):** a pytest-only PC gate through `scripts/pc_suite.sh launch -n 8 --
tests/test_s0_01_scripted_backend.py tests/red/test_s0_01_backend_credential_screen.py` then `wait <RUN_ID>`, from a CLEAN detached
worktree of the PIN. Nothing else on the bridge. (The lane itself ran ON the PC — its gate lines are PC lines; the coordinator's
sandbox gate is the second venue. Both are in the checkpoint message.)

**Inputs (read in this order):** the lane brief `tasks/briefs/s0-01-d5l-backend-the-class-closed-structural-ban-record-pinned-one-extras-literal.md`
(the contract: 7 items + the 18-class self-sweep) · the verdict it answers `tasks/briefs/s0-01-d5l-support/verify-D5k.md` (F1-F8 blockers +
the held items, AF-AP-60/61) · the lane's report `tasks/briefs/s0-01-d5l-support/D5l-report.md` (a PC Hermes report: it says
"PROPOSAL only" — grade it exactly as a sandbox report; its `backend:`/`main:`/`red:` aliases map to the three scope files) · the
context pack `tasks/briefs/s0-01-d5l-support/pack-backend-d5l.md` · the PC patch as applied `tasks/briefs/s0-01-d5l-support/patch-d5l.diff`
(the exact bytes the PC lane produced — verify the checkpoint's scope files equal PIN-parent + this patch) · `docs/INCIDENT-LOG.md`
(AF-AP-60, AF-AP-61, AF-AP-37, AF-AP-30) · the sweeps `tasks/briefs/s0-01-sweep-support/SWEEP-prod.md` (backend rows) and
`SWEEP-tests.md` (the backend test rows).

## Item 0 — the mechanical gates, pasted
`python3 scripts/report_lint.py tasks/briefs/s0-01-d5l-support/D5l-report.md --rev <PIN> --map backend=proofs/S0-01/tools/scripted_backend.py
--map main=tests/test_s0_01_scripted_backend.py --map red=tests/red/test_s0_01_backend_credential_screen.py` — MISS 0 or a finding;
`ap_screen.py` on the backend and `--tests` on both test files (the lane claims TEST_SCREEN 0 hits — confirm; every production hit
classified by running it).

## Items (grade against the brief; red-before on the parent 8695636 for every new test; full files, never -x)
1. **D5k F1-F8 closure table** — one row per finding, closed by what, the red-before reproduced, the green, verdict.
2. **The structural `!= MARKER` ban (F1, AF-AP-60/61).** It must be an AST rule (a `Compare` with `NotEq` whose either side is a
   marker constant/name), not a regex over source text; attack it: `assert not (x == MARKER)`, `assert x.__ne__(MARKER)`,
   `assert MARKER != x` (operand order), `assert x != M` where `M = MARKER` (aliasing), a marker inside a tuple `assert (x,) != (MARKER,)`,
   `assert x not in (MARKER,)`. Which forms does the ban catch, which does it document as out of scope? The scratch controls
   BREAK/EVADE/POSITIVE must be REAL runs (paste); the ban must exit non-zero through its own exit code, never `grep -c` (AF-AP-60).
3. **Every served/verbatim path pins the positive record VALUE (F2).** Enumerate the served paths (the backend's routes/branches that
   write a record) and show each has a test asserting the record's content equal to the vector (not `!= MARKER`, not `is not None`);
   the RECORD-HDRVAL-BLANKED mutant dies at each. Write the mutant "the record carries the header NAME but an empty value" and
   "the record carries the previous request's value" — both must die.
4. **ONE extras literal (F3).** `_INVISIBLE_EXTRA` in the impl equals the oracle's; a one-codepoint drift on either side dies (the lane's
   IMPL-/ORACLE-EXTRA-DRIFT); the ten reserved BMP slots and the 4315-member table from D5k are still intact (regenerate the table by
   the documented command and diff).
5. **Startup refusals (F4).** A FIFO at `--token-file` → the named refusal without reading it (prove: the FIFO has no reader — the
   backend must not block; measure elapsed); a dangling symlink `--record-dir` → refusal; then the CLASS: every path the backend
   opens at startup or per request (token file, record dir, the record files it writes, any fixture) — a FIFO/dir/dangling symlink
   at EACH — bounded and named, or a finding (the write side of the read class is what N5h's verdict names for the probe; the same
   question here).
6. **Cost prose (F5).** The docstring's mechanism claim vs the numbers: re-run the dual probe (`tasks/briefs/s0-01-d5j-support/cost_probe.py`,
   both harness styles) on one vector three times and compare with the lane's `http.client 0.731 s vs raw-socket 0.717 s`; the prose
   must state what was measured, not what was assumed (the D5k verdict's "false cost mechanism" was the class).
7. **The dead helper gone (F6); stale `[-1]` over produced records = 0 (F7)** — grep + AST; any `[-1]` over a produced-records list
   without a count delta is a finding.
8. **The 18-class self-sweep** over both test files vs SWEEP-tests' backend rows: found / fixed / proved; a DEFECT row the sweep found
   and the lane's table lacks = a blocker.
9. **The PC carve-out gate**; paste beside the checkpoint's two lines; agree.
10. **Mutants ≥ 30** (the lane's rows + yours); every survivor classed; `ran` = executed; killers from the run.
11. **Discipline** — file:line by `sed -n` on the PIN; `report_lint.py` on your own report; the process census.
12. **The design.** Is the AST ban the right home (a test that scans the test files) or should the registry screen (AP_SCREEN /
    TEST_SCREEN) carry it as a mechanical row so every component gets it? Say which, from what you measured.

## Report
Save to the session scratchpad `wf-results-r5/VERIFY-D5l.md` — draft after EACH item — then return it whole. Findings: ALL, no severity
filtering, each with file:line on the PIN, expected vs observed, the failing input, the minimal fix, the exact red test, SOLID/UNSURE;
reproduced vs reviewed vs skipped; shared-tree hygiene; verdict MERGE-READY or NOT-READY with the blocking set and the cheapest path.
