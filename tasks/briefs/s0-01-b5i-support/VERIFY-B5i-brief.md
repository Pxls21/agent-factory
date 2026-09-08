# VERIFY-B5i — adversarial grade of lane B5i (S0-01 frame tee round 14: one sentence joined to the source by EQUALITY, an honest census, a structural hang pin, the identity at the right stage)

You are an Opus-5 `adversarial-verifier`. Repo /home/user/agent-factory, branch claude/soundbox-kit-migration-iz1jwf.
**PIN: `75998e7`** (the checkpoint carrying the lane's two files + its report; parent for the scope files =
checkpoint 8v = `63b582c`). Grade the bytes of `git archive <PIN>` from a copy under the session scratchpad
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ (`vb14/`). Read-only git on the shared tree;
every mutant on scratch copies; every pytest run with an explicit `--basetemp` under your scratch dir (VERIFY-B5h F15);
kill only what you start, PID-targeted; never background a run and stop; no outward actions.

**The ONE bridge action you MAY take (owner ruling 2026-09-07):** a pytest-only PC gate through `scripts/pc_suite.sh
launch -n 8 -- tests/test_s0_01_frame_tee.py` then `wait <RUN_ID>`, from a CLEAN detached worktree of the PIN. Nothing
else on the bridge. (F2/F3 of the previous round are precisely the findings an 8-worker venue sharpens — run it.)

**Inputs (read in this order):** the lane brief `tasks/briefs/s0-01-b5i-tee-sandbox-fallback.md` (the contract: 9 items +
the mutant list + the gates; the PC-lane original `s0-01-b5i-tee-one-sentence-joined-by-equality-honest-census-structural-hang-pin.md`
is the same design) · the verdict it answers `tasks/briefs/s0-01-b5i-support/verify-B5h.md` (F1-F16 with their red tests
and the deadlock's wchan/fd table) · the lane's report `tasks/briefs/s0-01-b5i-support/B5i-report.md` · the context pack
`tasks/briefs/s0-01-b5i-support/pack-tee-b5i.md` · the sweeps `SWEEP-prod.md` (#11, #13, #14, #15, #24) and `SWEEP-tests.md`
(the tee rows 1.1, 1.2, 1.3, 1.6, 1.7, 1.8, 1.11, 7.1, 9.4, 9.5, 10.5, 11.2, 11.3, 12.1, 14.1, 14.2 — the lane's item 9 must
have found and fixed 1.1/1.2 (the collector defaulting on absent artifacts: 7 tests green on nothing), 1.3, 10.5 (the eight
undeclared /dev/full skips), 12.1 (the pin blind to the signal's identity), 14.1) · `docs/INCIDENT-LOG.md` (AF-AP-55/58/59)
· the vendored oracle `proofs/S0-01/vendor/buzz-acp/acp.rs` (sha256 `44e82861…` — never edited; verify the sha first).

## Item 0 — the mechanical gates, pasted
`python3 scripts/report_lint.py tasks/briefs/s0-01-b5i-support/B5i-report.md --rev <PIN> --map tee=proofs/S0-01/tools/frame_tee.py
--map test=tests/test_s0_01_frame_tee.py` — MISS 0 or a finding (fourth round of this class in the tee); `ap_screen.py`
on the tee and `--tests` on the test file — the AF-AP-59 row must produce ZERO hits on the test file (the lane's own pin
test asserts the same — confirm it reads the registry row, not a copy), every other hit classified by running it.

## Items (grade against the brief; red-before on the TRUE parent 63b582c for every new test; full file, never -x)
1. **B5h F1-F16 closure table** — one row per finding, closed by what, the red-before reproduced, the green, verdict.
2. **One sentence, joined by EQUALITY (F1/F5/F12/F13).** Attack: FALSECONST-ORDER (the reversed clause at every site);
   SITECOUNT-DUP; SEVENTH-SITE (a false sentence beside the true one); CITE-421 ×3; DOCSTRING-ORDER/-WRONGEVENT/-HYBRID;
   CONST-ORDER/-WRONGEVENT; COMMENT-TERM; TESTDOC-TERM; the union — EVERY one must die (paste the assertion line per
   mutant). Then attack the join itself: change `from_secs(5)` → the test must derive `secs` from the source, so mutate a
   scratch copy of acp.rs (the sha premise must fire FIRST — verify it does) and, separately, the expected-clause
   builder (does the test build `expected` from the derived facts, or from a second hand-written string? A second string
   = a mirror, F1 relocated again). Confirm the five reference sites carry NO shutdown prose of their own.
3. **The census helper's branch (F4).** Sites 1-2 assert `"live"`, site 3 `"gone"` with the a2c-EOF argument in the
   docstring; `range(3000)` restored; GRANDCHILD-UNKILLED at sites 1-2 dies, site 3 declared; the DONE row says "by
   construction" in those words. Measure the suite cost against the parent (the +16 s must be gone).
4. **The kill and the identity read (F6).** ProcessLookupError → gone; PermissionError → named failure, no kill;
   live-foreign → refuses; the unit test with the monkeypatched read covers all four; PROCESSLOOKUP-UNGUARDED dies.
5. **The AST kill pin as a subtraction (F3b/F11).** KILL-MODULE-LEVEL and KILL-LAMBDA die; class-body and comprehension
   scope too (write them); `_KILL_SITES` gone; CENSUS-PKILL-DQ and CENSUS-PGREP-A die on the registry row (the lane must
   not have patched the hook — `git diff <PIN>^ <PIN> -- .claude/hooks/` is empty).
6. **The hang class (F9).** `test_no_unbounded_tee_pipe_reads` exists and was RED on the parent (reproduce: it must flag
   test:2607/:2209/:1785/:459/:515 on 63b582c); every flagged site now bounded; site 3 closes stdin after the last write;
   the committed hang probe (agent consumes the handshake, closes a2c, exits; the test holds stdin) is RED on the parent
   as a timeout and GREEN on the PIN — reproduce BOTH, with the wchan/fd table on the parent if you can; HANG-REINTRODUCED
   dies; PIPEREAD-UNBOUNDED dies. Then try to build a NEW deadlock shape the pin does not cover (stderr, a fixture-level
   read, `communicate()` with a timeout that is too long to matter) and report it.
7. **The identity re-sampled at the first a2c byte (SWEEP-prod #11).** The two-stage agent (bash `exec` python) records
   the python interpreter 20/20 on the PIN (paste 20 trials) vs the parent's 18/20 bash; IDENTITY-EARLY-ONLY dies; the
   readlink guarded for the target exiting between spawn and read (plant an agent that exits immediately — no crash, the
   recorded reason).
8. **`S0_01_AGENT` validated (SWEEP-prod #13).** Empty → rc 64 named, no traceback; non-executable / FIFO / directory /
   absent → rc 64 named; the parent's PermissionError + rc 1 reproduced as the red-before.
9. **The self-sweep (item 9) against the tests sweep.** For each tee row of SWEEP-tests: found, fixed, proved? 1.1/1.2:
   the sweep's R19 mutant (the tee unlinks its four evidence files before `os._exit`) must now fail EVERY test that
   consumed those artifacts — re-run it and paste; 10.5: the /dev/full declaration test exists and the repointed
   predicate (R18) FAILS it, no skips; 12.1: the pin names the signal; 14.1: the token pin gone (item 2). A DEFECT row the
   sweep found and the lane's table lacks = a blocker.
10. **The PC gate (the carve-out)** from a clean detached worktree; paste beside the sandbox line; agree.
11. **Mutants ≥ 45** (the lane ran 43; add yours) (the brief's 30 + yours); every survivor classed; `ran` = executed; killers from the run.
12. **Discipline** — file:line by `sed -n` on the PIN; `report_lint.py` on your own report; the process census (zero
    orphaned `time.sleep` grandchildren; every tee you started gone).
13. **The design.** Is "one sentence in the repo" now enforced structurally (a test that fails when a SECOND shutdown
    sentence appears anywhere in the two files), or only by the five reference sites' wording? Is the bounded-reader
    helper the right primitive for every tee read, or should the fixture own the reads? Keep it to what you measured.

## Additions from the lane's own report (read `B5i-report.md` DISCREPANCIES 1-8 and SELF-ATTACK 1-3 first)
14. **The sixth site.** The lane's structural pin flagged `:407` on the PIN as a sixth unbounded read the verdict missed. Reproduce
    the RED on 63b582c (six sites), then ask: does the pin's AST walk cover EVERY read shape (`readline`, `read`, `readlines`,
    `communicate`, iteration `for line in proc.stdout`, `select`-less `os.read` on `fileno()`)? Write the shape it misses and report it.
15. **The re-sample's cost and race.** The lane measured a 2.9× regression in its first build and fixed it with a path short-circuit
    (`tee:289`); re-measure PIN-vs-parent on 15×3 reps (paste); then attack the short-circuit: a two-stage agent whose second stage
    is the SAME realpath as the first (bash exec bash) — is the record still right, and is the 1/20 race (agent answers and exits at
    once) really loud (the stderr marker) — force it with an agent that writes one a2c byte and `os._exit`s immediately, 20 trials.
16. **The corpus `tee_sha256` discrepancy (report DISCREPANCY 8).** The real-leg corpus records a tee sha that matches no recent tee.
    Establish from `tests/test_s0_01_check_acp_conformance.py` (the `_CORPUS_VERSION` strict xfails) whether this is a DECLARED
    v2.2-era limit or a live defect the mint will hit; say which, with the line.
17. **`S0_01_AGENT` validation vs the launcher.** The tee now exits 64 on an empty/non-executable agent. Find every producer of
    `S0_01_AGENT` in `proofs/S0-01/tools/pc/` and the tests (grep is legal here — a literal env name) and confirm none passes a
    shell string or a relative path that the new `os.access(X_OK)`-style check would reject on the PC (a Python script without the
    executable bit, invoked as `python3 script.py`, is the shape to test).

## Report
Save to the session scratchpad `wf-results-r5/VERIFY-B5i.md` (draft after each item; return it whole). Findings: ALL, no
severity filtering, each with file:line on the PIN, expected vs observed, the failing input, the minimal fix, the exact
red test, SOLID/UNSURE; reproduced vs reviewed vs skipped; shared-tree hygiene; verdict MERGE-READY or NOT-READY with the
blocking set — and the cheapest path to MERGE-READY.
