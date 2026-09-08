# VERIFY-CK12 — adversarial grade of lane A5j (S0-01 checker round 12: the class, not the instance)

You are an Opus-5 `adversarial-verifier`. Repo /home/user/agent-factory, branch claude/soundbox-kit-migration-iz1jwf.
**PIN: `dc9f5969182fe9dda5b9eadb98c9bfc85edf773f`** (checkpoint 8x — the lane's three files + its report + the coordinator's pack; parent = the
tree before the lane, whose checker files are checkpoint 8t = `73efb9f`). Grade the bytes of `git archive dc9f5969182fe9dda5b9eadb98c9bfc85edf773f` from a
copy under the session scratchpad /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ (`vck12/`).
Read-only git on the shared tree (other lanes may hold it — never stash/checkout/restore/reset/add/commit/push); every
mutant on scratch copies; every pytest run with an explicit `--basetemp` under your scratch dir (the shared
`/tmp/pytest-of-root` races between verifiers — VERIFY-B5h F15); kill only what you start, PID-targeted; never
background a run and stop; no outward actions.

**The ONE bridge action you MAY take (owner ruling 2026-09-07 — the carve-out to "delegates take no outward actions"):**
a pytest-only PC gate through `scripts/pc_suite.sh launch -n 8 -- <files>` then `scripts/pc_suite.sh wait <RUN_ID>`
(+ `log`), run from a CLEAN detached worktree of the PIN (`WT=$(mktemp -d) && git worktree add -q --detach $WT dc9f5969182fe9dda5b9eadb98c9bfc85edf773f &&
cp .pc-bridge.env $WT/ && cd $WT`; remove the worktree after). The PC exports `S0_01_VENUE=pc` and the PC corpus for you.
Nothing else on the bridge: no `scripts/pc.sh`, no lane dispatch, no server touch, no file writes on the PC.

**Inputs (read in this order):** the lane brief `tasks/briefs/s0-01-a5j-checker-the-class-not-the-instance.md` (the
contract: 11 items) · the verdict it answers `tasks/briefs/s0-01-a5j-support/verify-CK11.md` (F1-F20, every finding
with its red test) · the lane's report `tasks/briefs/s0-01-a5j-support/A5j-report.md` (grade it as a claim set) · **the
context pack `tasks/briefs/s0-01-a5j-support/pack-checker-a5j.md`** (graft skeletons + line ranges, the whole-file
registry screen, GitNexus/crg/ripwire answers for every symbol the lane touched — start here; run the instruments
yourself for anything it does not answer: `scripts/lane_context.sh -s SYM FILE`, `graft ask`, `node .gitnexus/run.cjs
impact SYM --direction upstream --repo .`, `/root/venv-crg/bin/code-review-graph query callers_of|tests_for`,
`scripts/ripwire_review.sh callers|test-gate`; the CLI on every venue, never MCP) · the production class sweep
`tasks/briefs/s0-01-sweep-support/SWEEP-prod.md` (55 rows; its checker rows are #2, #3, #4, #5, #8, #9, #17-#22, #29,
#30, #37, #38, #46-#51) · the registry `docs/INCIDENT-LOG.md` (AF-AP-1..61) · `.claude/skills/anti-hollow-green/SKILL.md`.
The declared corpus: `S0_01_VENUE=sandbox S0_01_REAL_LEG_DIR=/root/s0-01-realleg/golden` (`bash scripts/realleg_sync.sh
check` first; if absent, `pull`); the checker's real-leg tests FAIL by design when it is missing.

## Item 0 — the mechanical gates, pasted (the coordinator ran both; you re-run and DISAGREE if you can)
`python3 scripts/report_lint.py tasks/briefs/s0-01-a5j-support/A5j-report.md --rev dc9f5969182fe9dda5b9eadb98c9bfc85edf773f --map C=proofs/S0-01/check_acp_conformance.py
--map T=tests/test_s0_01_check_acp_conformance.py --map N=proofs/S0-01/negative_contract.py` — MISS must be 0; classify
every NEAR; a wrong reference the lane claims was grep-derived is a finding (AF-AP-37, fourth round in this component).
`python3 scripts/ap_screen.py proofs/S0-01/check_acp_conformance.py proofs/S0-01/negative_contract.py` and `--tests
tests/test_s0_01_check_acp_conformance.py`: every hit classified by RUNNING it — defect / reviewed-safe with the guard
named / documented limit. The lane's own classifications are claims: check each.

## Items (grade each against the brief's contract, reproduce every load-bearing claim, red-before on the TRUE parent 73efb9f for every new test — full file, never `-x`)
1. **CK11 F1-F20 closure table** — one row per finding: closed by what (file:line on the PIN), what you reproduced (the
   red-before on the parent for each new test with its failing line; the green on the PIN), verdict.
2. **The read CLASS (F8 → an AST self-scan over the checker + callees).** Attack the scan: plant in a scratch copy each of
   `pathlib.Path.open`, `io.open`, `os.open`, `json.load(open(...))`, `gzip.open`, `Path.read_bytes`, `readlink`,
   `os.stat`-then-read, a read inside a lambda / module scope / class body (the B5h lesson: an inclusion walk over
   FunctionDefs is blind to those), a read in `check_initialize.py` and in `negative_contract.py` — which does the scan
   flag, which does it miss? Then RUN the class: for EVERY path the checker reads (enumerate them from the scan itself),
   plant a FIFO and a directory and run the checker entry point (`proofs/S0-01/check_acp_conformance.py <root>` and the
   spec's negative leg `check_initialize.py request <negdir>`) with `--timeout-s 30`: elapsed, rc, reason. A hang to the
   cap is a defect; a named refusal in < 5 s of the read is the contract. SWEEP-prod #8 found four hangs in
   `negative_contract.py` (:58, :96, :159, :204) and #7 one in `tools/acp_probe.py:156` — state which are closed on the PIN.
3. **The presence-gated CLASS (F15 → no `exists()`-guarded check; AF-AP-40 screen + AST pin).** Attack: `os.path.exists`,
   `Path.exists`, `is_file`, `is_dir`, `try/except FileNotFoundError` with a default, `glob` presence, `os.access` — plant
   each guarding a read in a scratch copy; which does the pin catch? Then the exemplar: delete `fixtures/acp-schema-v1.json`
   from a passing bundle → the PIN must FAIL with a named reason (the parent printed the byte-identical PASS line — reproduce
   that too). SWEEP-prod #3d: the 2-line permissive schema substitution → still PASS byte-identical on the PIN? (it is
   unpinned by design today — state it as the OPEN class #4 for the next round, not as this lane's blocker, unless the
   brief asked for it).
4. **B1 as a property (F3/F4/F5).** `assert not ok` before the xfail branch; whole-reason equality; the strict xfail must
   XPASS-FAIL on a repaired capture (build one); mutants XFAIL-SUBSTRING, XFAIL-TAIL-COLLISION (a `probe_error` whose tail
   equals a known reason's tail) must die; the committed B1 test exists and is red on the parent.
5. **The declared corpus (F1/F16/F13/F17/F18/F19).** `S0_01_VENUE` ∈ {sandbox, pc, ci}: run a typo, wrong case, trailing
   space, empty, unset (= sandbox); `S0_01_REAL_LEG_DIR` tracking (mutant CORPUS-UUID-LITERAL); the sidecar verification:
   corrupt ONE corpus file → the suite FAILS with the file named (never skips); delete the sidecar → named failure; CI
   (`S0_01_VENUE=ci`) → the real-leg tests SKIP with the declared reason and nothing else changes. Run the real-leg set
   twice on the declared corpus and paste both summary lines.
6. **The alarm-in-try killer, the dead-branch pin, F6/F7/F14/F20, the one skip helper** — each reproduced (the pin must
   PARSE the cited `C:a-b` range and fail when the range no longer holds the `raise Failure`; move the raise and show it).
7. **The PC gate (the carve-out):** from a clean detached worktree of the PIN, `scripts/pc_suite.sh launch -n 8 --
   tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_negative_contract.py tests/test_s0_01_check_initialize.py`
   (adjust to the files that exist) → `wait` → paste the PC summary line next to your sandbox line (they should agree
   modulo the venue's skips: state the difference and why).
8. **The class status table over SWEEP-prod's checker rows** (#2 symlinked walk roots, #3/#4 unpinned fixtures, #5 the
   F17 `pinned_present` consumer = the AF-AP-59 addendum class, #17/#18/#19/#20/#21 redundant guards and dead arms, #29/#30
   wrong-reason deferrals, #37 `int(se.code or 0)` + exit-code-only grading, #38 documented, #46-#51 safe): for each,
   OPEN / CLOSED-BY-A5j / N-A on the PIN, with the run. This table is the next round's brief, not this lane's blocker
   list — grade the lane against ITS brief; report the rest as carry-forward with evidence.
9. **The real-corpus end-to-end truth (SWEEP-prod #1).** Run `check_acp_conformance.py` over a bundle whose golden/ is the
   declared real corpus (`/root/s0-01-realleg/golden`, with the repo's fixtures) and paste the exact first failure — the
   allowlist rejects producer names / requires names never produced. Not this lane's blocker; the number the next brief
   needs (which names, which direction).
10. **Discipline.** Every file:line in YOUR report by `sed -n` on the PIN's bytes; run `report_lint.py` on your own report
    at `--rev dc9f5969182fe9dda5b9eadb98c9bfc85edf773f` and paste the summary; every mutant on a scratch copy with `git status --porcelain` on the scope
    files asserted empty after each; ≥ 25 mutants (the lane's + yours), `ran` = executed, killers named from the run.
11. **The design.** Is an AST self-scan written as an inclusion walk the right shape, or a subtraction (every read Call
    in the module minus the allowed helper)? Is `_require_file` (S_ISREG + named refusal) the right primitive for the
    checker, `check_initialize.py` and `negative_contract.py` alike — one helper in `pins.py`, or three copies? Where would
    you still change it? Keep it to what you measured.

## Report
Save to the session scratchpad `wf-results-r5/VERIFY-CK12.md` (draft after each item; return it whole). Findings: ALL of
them, no severity filtering, each with file:line on the PIN, expected vs observed, the failing input, the minimal fix
and the exact red test; SOLID/UNSURE on every claim; what you reproduced vs reviewed statically vs deliberately skipped
(with the reason); shared-tree hygiene line; the process census. Verdict: MERGE-READY or NOT-READY with the blocking set
named — and if NOT-READY, the cheapest path to MERGE-READY in one paragraph.
