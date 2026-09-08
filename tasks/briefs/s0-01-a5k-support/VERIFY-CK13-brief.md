# VERIFY-CK13 — adversarial grade of lane A5k (S0-01 checker round 13: the consumer of the pinned list, the v2.4 header, the CK12 blocker classes) on the JOINT checkpoint

You are an adversarial-verifier (the PC Hermes verify lane; the venue map `tasks/briefs/pc/VENUE-MAP.md` applies). Repo
agent-factory, branch claude/soundbox-kit-migration-iz1jwf. **PIN: `77f46a2`** — the JOINT checkpoint that lands three lanes at
once: A5k (this grade), P5b (the PC capture tools round 2 — VERIFY-P5b grades it in parallel) and D5m (the backend round 16 —
VERIFY-D5m). A5k's bytes on the PIN: `proofs/S0-01/check_acp_conformance.py` (1911 lines, sha `25b89431…`),
`proofs/S0-01/check_initialize.py` (222, `304d44d6…`), `proofs/S0-01/negative_contract.py` (222, `b397f6b7…`),
`tests/test_s0_01_check_acp_conformance.py` (5275, `ce62bc62…`), `tests/test_s0_01_check_initialize.py` (863, `6281dab7…`),
`tests/test_s0_01_negative_contract.py` (473, `fe4378fa…`), `tests/test_s0_01_audit_cp5_controls.py` (144, `457430b1…`) and the
lane's report `tasks/briefs/s0-01-a5k-support/A5k-report.md`. **`proofs/S0-01/pins.py` on the PIN is NOT the lane's 251-line
file**: it is the coordinator's three-way merge of P5b's 367-line pins.py (the ONE list as functions) and A5k's
`require_regular_file` helper (381 lines, sha `84a1e5c8…`; one duplicate `import os` from the merge removed). Grade the bytes of
`git archive 77f46a2` from a scratch copy under your lane's scratch dir; every mutant on scratch copies; every pytest run with an
explicit `--basetemp` and the venue exports (`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden
S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`); every FIFO/hang probe standalone under `timeout` with a PID-scoped watchdog, never
through pytest; the ~12-minute headline suite in ONE foreground call or as a bounded background process you explicitly await with a
durable rc file (the lane did the latter — say which you did); kill only what you start, by pid; no outward actions; never read,
print or commit a credential. Authorization: the owner's own ACP conformance checker under test on the owner's system.

**Inputs (read in this order):** VERIFY-CK12's report `tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md` (the round's
contract: F-CK12-01..18, five BLOCKING; its 24 + 27 mutants; "THE CHEAPEST PATH") · the lane brief
`tasks/briefs/s0-01-a5k-checker-consumer-of-the-pinned-list-v24-header-ck12-blockers.md` and its PC continuation
`tasks/briefs/pc/pc-a5k.md` · the lane's report `A5k-report.md` (NOT_DONE, the DONE table with C/T/N/I/A aliases, the 34-row
mutant table, the 18-class sweep of the TEST file, the self-attack) and its predecessor draft `A5k-draft-0631Z.md` · lane P5b's
report `tasks/briefs/s0-01-p5b-support/P5b-report.md` (DECISIONS + DISCREPANCY D6: the two `corpus_version` answers) ·
`docs/INCIDENT-LOG.md` (AF-AP-40, AF-AP-57, AF-AP-59, AF-AP-64, AF-AP-65).

## Item 0 — the mechanical gates, pasted
`python3 scripts/report_lint.py tasks/briefs/s0-01-a5k-support/A5k-report.md --rev 77f46a2 --map C=proofs/S0-01/check_acp_conformance.py --map T=tests/test_s0_01_check_acp_conformance.py --map N=proofs/S0-01/negative_contract.py --map I=proofs/S0-01/check_initialize.py --map A=tests/test_s0_01_audit_cp5_controls.py --map pins.py=proofs/S0-01/pins.py --map negative_contract.py=proofs/S0-01/negative_contract.py --map check_initialize.py=proofs/S0-01/check_initialize.py`
(the coordinator read `52 refs — OK 52` against the lane's tree; the PIN's pins.py is 130 lines longer — `pins.py:16-25`,
`:190-251`, `:196-199` may now be wrong: say which); `ap_screen.py --s0-01` (the coordinator read 66 production / 6 test hits on
the joint tree; the lane read 62 / 8 on its own tree — reconcile by RUN); pyflakes; the FILE IDENTITY table against the PIN; the
headline suite run by you (the lane: `490 passed, 9 xfailed in 701.56s` ×2; the coordinator's joint gates are pasted in the
checkpoint commit `77f46a2`) — agree or disagree by your own run.

## Items
1. **THE COORDINATOR'S FINDING FIRST — the ONE list has two consumers with two predicates.** P5b delivered `pins.required_files`,
   `entry_allowlist`, `corpus_version`, `is_pinned_argv` (`pins.py:265-343` on the PIN) and the producer (`pc_post.sh`) calls
   them; A5k's checker consumes NONE of them (its only `pins.` reads are `require_regular_file`): it carries its own
   `_parse_scan_v24` (`C:1175`), `_is_pinned_process` (`C:1198`) and the test file its own `_corpus_version` fold (`T:2664`).
   Construct rows where the two sides DISAGREE and run both: `/usr/bin/cat <tee>`, `python3 -c "…" <tee>`, `env python3 <tee>`,
   a symlinked interpreter, the tee as argv[2], a v2.4 header without `tee-status.json` (P5b's D6: pins says v2.4 and fails on
   the missing name; the checker's fold says v2.2 and passes — WHICH IS RIGHT, and is the joint tree's answer a silent PASS on a
   leg its own header contradicts?). This is round 14's design item (A5l); your job is the concrete disagreement table.
2. **F-CK12-02/03 — the read class.** The guarded read inventory (`T:5014-5124`) and `require_regular_file` at every negative-entry
   read (`N:37-43`, `I:39-40`): reproduce the FIFO probes standalone at each site; attack the inventory with syntax the lane's six
   mutants did not use — `io.open`, `os.fdopen`, `Path.open` through an alias, `shutil.copyfile`, `subprocess` reading a path,
   a read inside a comprehension / lambda / decorator / `ExitStack.enter_context`, `json.load(p.open())` — does the inventory
   NAME the new site (the lane's pass bar) or stay green?
3. **F-CK12-04/05 — the AP-40 class pin (`T:4939-5011`).** The ten shapes re-run; new ones: a walrus `if (q := p).exists()`,
   `try: … except FileNotFoundError: continue`, `p.stat()` under a caught `OSError`, `os.path.getsize`, `next(p.glob(…), None)`;
   the exemptions keyed by `(file, function, unparsed test)` — a LINE-SHIFT control (insert 20 lines above) must stay green, a
   renamed function must go red; F-CK12-08 (the lane's own new code carrying the shape).
4. **The v2.4 header and the exact entry point (`C:1175-1203`, `:1256-1282`, `:1361-1381`; `A` the audit file).** The
   red-before `2 failed, 1 passed` reproduced on the PIN's parent; the `table_rows` vs `rows` mutant; the substring-weakening
   mutant; a v2.3 header in a v2.4 leg and the reverse; the teardown scan's survivor naming.
5. **The three-way negative grading (`T:3040-3068`), sidecar parity (`T:2785-2803`), the corpus declaration
   (`T:2668-2803`).** A sidecar with an extra path; a corpus of mixed versions; the nine known-stale xfails — can a NEW failure
   with the same reason TEXT hide under an xfail (exact-reason vs exact-cause)?; F-CK12-09/10/12/13 closure by RUN.
6. **The rest of CK12 by RUN:** the alarm restore order (M11), the dead-branch citation pin over all six comments and seven
   citations (F-CK12-07), the lossy-timeline reason (`C:274-281`), bare `SystemExit` → 70 (`C:1903-1904`: also
   `SystemExit("text")`, `SystemExit(None)`, `sys.exit(0)` inside a check, `os._exit`), the symlinked `golden/` root
   (`C:1710-1716`: a symlinked LEG dir inside golden, a symlinked file inside a leg), the F43 write family (`os.link`,
   `os.replace`, `os.rename`, `shutil.move`, `tarfile.extractall` — named or missed?), F-CK12-11/17/18.
7. **The real corpus.** `43 passed, 331 deselected, 9 xfailed` re-run; the lane's NOT_DONE: the checker run directly over
   `/home/rocco/s0-01-pinned/realleg` answered `golden: manifests/ absent` — decide whether the corpus ROOT the checker wants is
   `…/realleg` or `…/realleg/golden` (a venue-map bug, a checker bug, or a corpus layout gap) and what the S0-01 mint would need.
8. **Mutants ≥ 40**: the lane's 34 reconstructed on YOUR scratch copies (never its driver) + the novel shapes above; killers pasted
   with the env stated; the comment-only control.
9. **The 18-class re-scan on the PRODUCTION checker** (the lane swept the TEST file): every `if <field> == <literal>:` without a
   raising other arm (AF-AP-65), the SWEEP-prod checker rows carried forward (CK12 item 8), the presence-gated forms in
   `C`/`N`/`I` by RUN.
10. **Discipline** — file:line by `sed -n` on the PIN; `report_lint.py` on your own report; the process census by pid; the lane's
    two declared deviations (background-awaited headline runs; the replaced draft) weighed.
11. **The design.** What must round 14 (A5l) do: adopt P5b's functions in the checker (one predicate, one version answer), the
    SWEEP carry-forwards (#37 first), the corpus root; what is MERGE-READY today and what blocks the S0-01 re-capture; which
    items are the coordinator's (the joint merge of pins.py, the corpus layout on the PC, VB-F12).

## Report
Write it to `tasks/briefs/s0-01-a5k-support/VERIFY-CK13-report.md` inside your tree, draft after EACH item, and return it whole
as your final message. Findings: ALL, no severity filtering, each with file:line on the PIN, expected vs observed, the failing
input, the minimal fix, the exact red test, SOLID/UNSURE; reproduced vs reviewed vs skipped; verdict MERGE-READY or NOT-READY with
the blocking set and the cheapest path; the items that are the coordinator's or A5l's named as such.
