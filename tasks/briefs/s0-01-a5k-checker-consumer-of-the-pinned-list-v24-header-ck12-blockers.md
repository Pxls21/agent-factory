# Lane A5k — S0-01 checker, round 13: the consumer side of `pins.PINNED_LEG_FILES` + the v2.4 scan header, VERIFY-CK12's five blockers closed as CLASSES, the thirteen non-blocking findings, the two SWEEP carry-forwards (PC Hermes `code-implementer`; sandbox fallback `code-implementer`)

PIN: 545a9ff87124a5345f51c9aee2c0e98697bc7dc4
(the pushed head; the lane tree ALSO carries lane P5a's nine uncommitted files applied as a patch — `pins.py` with
`PINNED_LEG_FILES`, the v2.4 `pc_post.sh`, `pc_launch.py`, `pc_negative.py`, `build_capture_record.py`, the two PC-tools tests —
verify with `sha256sum proofs/S0-01/pins.py | cut -c1-16` = `974b86f2445d239f` and `proofs/S0-01/tools/pc/pc_post.sh` = `8db8caeaf5e56f28`
BEFORE the first edit; if they differ, STOP and report.)

**Why:** the checker (round 12, checkpoint 8x = dc9f596) is NOT-READY under VERIFY-CK12 — five blockers, thirteen findings, two
SWEEP carry-forwards (`tasks/briefs/s0-01-a5j-support/verify-CK12.md`, read WHOLE first). Independently, lane P5a rebuilt the PC
capture tools around ONE pinned leg-file list and a v2.4 scan header, and the checker is their only consumer: with P5a's
`pc_post.sh` in the tree, `tests/test_s0_01_audit_cp5_controls.py` is 2-of-3 RED (`process-scan-after.txt has no enumeration
header`) — P5a cannot land until the checker adopts v2.4 (`tasks/briefs/s0-01-p5a-support/P5a-report.md` NOT_DONE 2-3, D1-D6). This
round does both, as classes.

**Inputs (read in this order):** `tasks/briefs/s0-01-a5j-support/verify-CK12.md` (whole: Items 0-11, F-CK12-01..18, the carry-forward
list, the "cheapest path" closing paragraph) · the previous brief `tasks/briefs/s0-01-a5j-checker-the-class-not-the-instance.md` +
report `tasks/briefs/s0-01-a5j-support/A5j-report.md` (what round 12 built) · `tasks/briefs/s0-01-p5a-support/P5a-report.md` (DONE 1-7,
D1-D6, NOT_DONE 3 = the five checker sites) · `proofs/S0-01/pins.py` (`PINNED_LEG_FILES`, `PINNED_LEG_FILES_SINCE`, `PINNED_LEG_DIRS`
and their four statuses) · `proofs/S0-01/tools/pc/pc_post.sh:36-47, 87-96` (the v2.4 header and the entry-point rule) ·
`tasks/briefs/s0-01-n5h-support/N5h-report.md` §"Consumer contract" (a lossy a2c line now carries `raw_b64`; `check_timeline`'s
exact key set rejects it with an unnamed `unexpected keys` message) · `tasks/briefs/s0-01-sweep-support/SWEEP-prod.md` rows #1, #2,
#3d, #8, #37, #41 · the real-leg corpus (`S0_01_VENUE=sandbox S0_01_REAL_LEG_DIR=/root/s0-01-realleg/golden` in the sandbox; the PC
pair from `scripts/pc_suite.sh`/`pc_lane.sh`'s env — run `bash scripts/realleg_sync.sh check` first) · `docs/INCIDENT-LOG.md`
(AF-AP-30/40/56/59).
**Scope:** `proofs/S0-01/check_acp_conformance.py` · `proofs/S0-01/negative_contract.py` · `proofs/S0-01/check_initialize.py` (only if
a read-class fix lands there) · `proofs/S0-01/pins.py` (ADD-only: one `require_regular_file` helper; never touch `PINNED_LEG_FILES`) ·
`proofs/S0-01/spec.json` (the `#37` carry-forward, if the spec schema allows `stdout_contains` — check `proofs/schemas/spec.schema.json`
first; if it does not, say so and do the code-side fix only) · tests `tests/test_s0_01_check_acp_conformance.py`,
`tests/test_s0_01_negative_contract.py`, `tests/test_s0_01_check_initialize.py`, `tests/test_s0_01_audit_cp5_controls.py` · report
`tasks/briefs/s0-01-a5k-support/A5k-report.md`. NOT yours: every file of lanes P5a/B5i/D5l/N5h (`tools/pc/*`, `frame_tee.py`,
`scripted_backend.py`, `acp_probe.py`, their tests), `proofs/registry.yaml`, the schemas (attested inputs — AF-AP-56), the corpus.
Lane rules: the lane tree is a detached worktree at the PIN + the P5a patch; commit nothing, push nothing; every gate one FOREGROUND
call; kill only your own pids; never `pkill`/`pgrep -f` (AF-AP-59); no network beyond localhost; never touch the owner's services.

## Design (pinned — build it, do not redesign it)
1. **The v2.4 header + the ONE list (P5a's five sites, as one change).** `check_acp_conformance.py:154-155` parses `v2.4` with
   `table_rows=(\d+)` before `utc=`; `rows` is the BODY count and a clean teardown legitimately reads `rows=0`, so the enumeration
   check at `:1234`/`:1338` reads `table_rows` (`table_rows=0` = "enumeration did not run", named); F17's `body_pinned` at `:1249-1253`
   adopts the ENTRY-POINT rule from `pc_post.sh:36-47` (`argv[0] == PINNED_BUZZ_ACP_EXE_REALPATH` or `argv[1] in (PINNED_TEE_PATH,
   PINNED_AGENT_REALPATH)`) — import the rule as ONE function shared with nothing (the shell producer cannot import Python), and pin the
   two implementations to agree by a test that runs `pc_post.sh`'s embedded Python over a synthetic table and the checker's function over
   the same rows; `_LEG_REQUIRED_FILES`/`_LEG_OPTIONAL_DIRS` (`:1718-1726`) are DELETED and replaced by `pins.PINNED_LEG_FILES`
   (allowlist = `required | optional | PINNED_LEG_DIRS`; required = `required` minus `PINNED_LEG_FILES_SINCE` names for a corpus older
   than their version — the corpus version rule the test file already has); `capture.json` becomes admissible (it is `optional` in the
   list). F20 `agent-stderr.txt` (`:1737`): REQUIRED in the negative leg only (its producer is `acp_probe.py`), never in positive legs —
   the ruling on P5a's D2; write the reason in the code comment. Red-before: `tests/test_s0_01_audit_cp5_controls.py` 2-of-3 red on the
   PIN+patch; green after; the real corpus (v2.2) still yields the same 364/9/1-shaped run as round 12 (paste both).
2. **The read CLASS, for real (F-CK12-02, F-CK12-03, F-CK12-11, F-CK12-12; SWEEP #8).** ONE helper `pins.require_regular_file(path,
   what) -> Path` (S_ISREG via `os.stat`, never `exists()`; raises the caller's failure type with `<what> is not a regular file: <name>`
   — the NAME, never an absolute path); every read in the three checker modules goes through it or through the walk (the four
   `negative_contract.py` sites `:59, :97, :160, :207` included — F-CK12-03's four hangs must become named refusals in < 5 s through the
   `spec.json` negative entry point, reproduced with a FIFO at each). The AST read-scan test (`T:4718-4780`) becomes a GOLDEN-LIST test:
   the scan enumerates every `open`/`io.open`/`os.open`/`gzip.open`/`Path.open`/`read_text`/`read_bytes`/`json.load` site in the three
   modules and asserts the set of (file, function, receiver) EQUALS a committed list, each entry tagged `walk` | `require_regular_file`
   | `stdin` — a new read site fails the test by name; the guard token must name the SAME receiver (never "within 5 lines"); CK12's
   six planted vectors all caught (write them as the test's own mutants: M06 `checked_files = []`, M21 the widened allowlist, the six
   vectors). The `_corpus_file` guard gets its FIFO killer (F-CK12-12).
3. **The presence-gated CLASS, for real (F-CK12-04, F-CK12-05, F-CK12-08, F-CK12-10; SWEEP #3d).** The AP-40 pin flags EVERY shape where
   a false path of an `exists()`/`is_file()`/`is_dir()`/`os.path.exists`/`os.access`/glob-truthiness/`try: … except FileNotFoundError`
   gate can yield a value without raising — explicit `else`, fall-through, ternary (`IfExp`), the `not` form — over the three production
   modules AND the test module (F-CK12-10's `pytest.skip` behind `baseline.exists()`); exemptions keyed by `(file, enclosing function,
   ast.unparse(test))`, never a line number (a prepended comment must not move a verdict — that is a test); CK12's ten planted shapes are
   the pin's own mutants, all ten caught. `_corpus_version()` (`T:2629-2641`) RAISES on a malformed corpus (missing scan header, missing
   `tee-status.json` on a v2.3+ corpus) instead of defaulting to v2.2 — `test_real_leg_corpus_declared` owns the absence semantics; the
   `pytest.fail` guards in `test_real_leg_process_evidence` move above the `add_marker` call.
4. **B1 with an in-gate killer (F-CK12-06, F-CK12-18).** Extract `_grade_negative(ok, result) -> str` (three outputs: pass-is-hard-failure,
   known-stale-xfail, real-failure) and unit-test all three; the triple `negative:` prefix gone.
5. **The dead-branch pin covers every comment and every citation (F-CK12-07).** `re.findall` over `C:a-b`; every one of the six comments
   must cite ≥ 1 range (RED on the PIN: `C:1605` cites none — fix the comment, then the test); M14/M16 die.
6. **The sidecar verification is two-directional (F-CK12-09).** The sidecar's path set equals the corpus walk (both directions, unlisted
   file named, missing declared artifact named with a `pytest.fail`, not a `FileNotFoundError` traceback); a committed tiny drifted
   corpus fixture makes the drift loop's killer real (M08).
7. **F9 stated honestly (F-CK12-13)** — either the monkeypatched `alarm` raises on `0` too so the restore order is observable, or the
   report says "inspection-only" in those words. Your call; say which.
8. **The lossy-line message (N5h's consumer note).** `check_timeline` names the cause: `timeline: lossy a2c line at seq N (raw_b64 kept)`
   — a Failure with the REASON, not `unexpected keys`; the key set otherwise stays exact (the clean-line test from N5h's file is the
   negative control; a lossy entry WITHOUT `raw_b64` is still `unexpected keys`).
9. **The carry-forwards.** SWEEP #37: a bare `raise SystemExit()` inside a check must not mint rc 0 with an empty stdout —
   `return 70 if se.code is None else int(se.code)` at `:1849-1850`, and (schema permitting) `"stdout_contains": "PASS: S0-01"` on the
   positive spec leg; test it through `scripts/proof-runner`'s leg path if the runner honours it, else through the checker's exit.
   SWEEP #2: `golden/` or the fixtures root as a SYMLINK ⇒ named refusal (the walk's S_ISDIR-without-follow rule, `os.lstat`).
   F-CK12-17: `symlink_to` back in `_WRITE_ATTRS`; the two enclosing tests exempted by NAME (`_EXEMPT_FNS`), never by dropping the family.
10. **Report discipline (F-CK12-01, -14, -15, -16) — the fourth round of this class ends here.** Every `file:line` in your report comes
    from `grep -n` run on your FINAL bytes and is checked by `python3 scripts/report_lint.py <report> --map C=proofs/S0-01/check_acp_conformance.py
    --map N=proofs/S0-01/negative_contract.py --map I=proofs/S0-01/check_initialize.py --map T=tests/test_s0_01_check_acp_conformance.py
    --map A=tests/test_s0_01_audit_cp5_controls.py` with MISS 0 and NEAR 0 — paste the summary line; every mutant row states the ENV it
    ran under (`S0_01_VENUE`, `S0_01_REAL_LEG_DIR` set/unset) and is labelled KILL or CONTROL; the headline gate lines are runs on the
    FINAL bytes (`bash scripts/test_summary.sh tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_negative_contract.py
    tests/test_s0_01_check_initialize.py tests/test_s0_01_audit_cp5_controls.py` twice, pasted verbatim, with the load); the PIN header
    names the commit whose bytes the red-befores ran on. `python3 scripts/ap_screen.py --s0-01` before the report: every hit classified
    by RUNNING it. The 18-class self-sweep over your test file (the sweep's class list is §COUNTS PER CLASS in SWEEP-prod.md) as a table.
11. **Mutants ≥ 30**, each RUN on a scratch copy of the lane tree (never the tree itself): CK12's M03/M06/M08/M11/M14/M16/M21/M23 and the
    six read vectors and the ten AP-40 shapes, plus the v2.4 header literal, `table_rows` counted over the body, the entry-point rule
    weakened to substring, a required file dropped from the list, F20 required in a positive leg, the lossy message reverted, SystemExit
    rc 0, the symlinked golden. Killer lines pasted from the run.

## Report
`tasks/briefs/s0-01-a5k-support/A5k-report.md` (append each FINISHED section to `$LANE_REPORT_DRAFT` as you go): PIN + the P5a patch
identity table; FILE IDENTITY (sha256 + lines, FINAL bytes); the gate lines; report_lint's summary; ap_screen classified; the DONE table
(item → file:line → red-before → green); the mutant table with env; the self-sweep; NOT_DONE first-class (what you could not run on this
venue and why); DISCREPANCIES (anything the inputs contradict — e.g. a CK12 finding that does not reproduce on the PIN+patch, with the run);
the three most likely ways this change is wrong.
