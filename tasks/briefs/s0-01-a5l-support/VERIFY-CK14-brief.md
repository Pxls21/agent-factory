# VERIFY-CK14 — adversarial grade of lane A5l (S0-01 checker round 14: the ONE process list consumed through `pins.is_pinned_argv`, both corpus-version consumers strict through `pins.corpus_version`, the ONE file list from `pins.required_files` / `pins.entry_allowlist` pinned as complete sets, the three scanner domains enumerated by declared syntax family, VERIFY-CK13's survivors M14/M16/M21 killed by name, VB-F12's `rows`/`table_rows` kept distinct, the CLI `SystemExit` domain closed)

**PIN: `b6483df`** (the landing of A5l's bytes: `proofs/S0-01/check_acp_conformance.py` 1907 lines sha `0ea35504…`,
`tests/test_s0_01_check_acp_conformance.py` 5615 lines sha `bf7c5411…`; `proofs/S0-01/pins.py` UNCHANGED by the lane — re-derive
all three with `sha256sum` and `wc -l` at the PIN and paste them as your FILE IDENTITY block). Role: adversarial-verifier. Route:
the CLOUD verify route (`HERMES_MODEL=agentfactory-verify`, `HERMES_REASONING=ultra`) while the one local slot holds VERIFY-N5k.
Repo agent-factory, branch claude/soundbox-kit-migration-iz1jwf. Venue: `tasks/briefs/pc/VENUE-MAP.md` applies. Authorization:
the owner's own ACP-conformance checker under test — defensive work on their system.

**You grade; you do not build.** Never edit `proofs/`, `tests/`, `scripts/` in your tree: every mutant and every rig runs on a
SCRATCH COPY under your lane's scratch dir. Your only deliverable is `tasks/briefs/s0-01-a5l-support/VERIFY-CK14-report.md`
(drafted after EACH item — the incremental rule — and returned whole as your final message).

**Inputs (read in this order):**
1. `tasks/briefs/s0-01-a5l-checker-the-one-list-consumed-the-scanner-domains-closed-the-sets-pinned.md` — the round's contract
   (items 1-11 + AMENDMENT 1). NOTE its paths say `proofs/S0-01/tools/check_acp_conformance.py`; the checker lives at
   `proofs/S0-01/check_acp_conformance.py` (the lane found and flagged this; the pack below uses the real path).
2. `tasks/briefs/s0-01-a5l-support/A5l-report.md` — the lane's report (aliases `C:` = the checker, `T:` = its test), its
   `mutants.sh` driver (13 rows + one comment-only control) and `red-before.patch` (a prose RECORD of the pre-fix reds, not an
   applyable patch — grade that choice in item 9).
3. `tasks/briefs/s0-01-a5l-support/A5l-pack.md` — the code-intel pack over the three files at the PIN (skeletons, the graft
   ask, GitNexus impact, crg callers/tests, ripwire callers + test-gate, the registry screen). Start from it.
4. `tasks/briefs/s0-01-a5k-support/VERIFY-CK13-report.md` — the predecessor verdict whose nine blockers this round closes.
5. `docs/INCIDENT-LOG.md` rows AF-AP-40, AF-AP-42, AF-AP-63, AF-AP-64, AF-AP-65, AF-AP-70, AF-AP-72, AF-AP-73, AF-AP-76.

## Item 0 — the mechanical gates, pasted, and the test-count reconciliation
With the venue exports (`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden
S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`), `/home/rocco/venv-agent-factory/bin` FIRST on PATH, a SHORT absolute
`--basetemp` (`mkdir -p` its parent first), ONE foreground call per run and every call under Hermes's 420 s tool cap:
`bash scripts/test_summary.sh tests/test_s0_01_check_acp_conformance.py` TWICE (the lane: `419 passed, 13 xfailed`), then the
four-file xdist run (`tests/test_s0_01_acp_probe.py tests/test_s0_01_negative_contract.py tests/test_s0_01_check_initialize.py
tests/test_s0_01_check_acp_conformance.py -n 4`; the lane: `535 passed, 13 xfailed in 145.18s`). Paste every summary verbatim.
**Reconcile the count (the coordinator's `--collect-only` at landing):** the pre-round bytes (`d23762a`) collect `383 tests`
(307 unique functions); the landed bytes collect `432 tests` (318 unique functions): 13 functions NEW, TWO REMOVED —
`test_ck12_corpus_version_rejects_missing_newer_artifact` and `test_main_maps_bare_system_exit_to_70`. Grade the two
removals: each must be SUPERSEDED by a stricter landed test (the strict `pins.corpus_version` consumers of item 2; the
`SystemExit` domain test `T:2856` of item 7) with the old test's property still pinned — a property that only the removed
test pinned is a finding. (Round 13's `490 passed, 9 xfailed` was a different tree; do not use it as the baseline.)
Then `python3 -m pyflakes` on the three files (rc 0) and `python3 scripts/ap_screen.py proofs/S0-01/check_acp_conformance.py
tests/test_s0_01_check_acp_conformance.py` (the coordinator's screen at landing: 40 hits over 2 files, IDENTICAL to the PIN's
predecessor bytes class by class — paste yours and classify every hit by RUN).

## Items
1. **The ONE process list (`C:1195` `_pinned_process_count` → `pins.is_pinned_argv`; the private `_is_pinned_process` removed;
   the AST test that prohibits a second checker predicate).** Attack the seam: on scratch copies, (a) re-introduce a private
   predicate under a NEW name that the AST prohibition does not spell; (b) import `pins` under an alias and call
   `is_pinned_argv` through it; (c) a wrapper that pre-filters argv before the shared predicate (a `[a for a in argv if …]`);
   (d) a scan row whose argv the producer classifies pinned=False and the checker's path classifies True (VERIFY-P5b's
   `/usr/bin/cat <frame_tee.py>` shape) — the two must agree BY RUN through the real functions. Which test reds each, by
   what line.
2. **Strict versions (`C:1683` `_captured_leg_version`, `T:2676` `_corpus_version`, both → `pins.corpus_version`).** A leg whose
   `process-scan-after.txt` header says `v9.9`; a leg with NO header; a bundle whose legs carry MIXED versions; a v2.3 corpus
   folded as v2.2 — each must fail BY LEG NAME (exact text pasted). Then the VB-F12 xfail at `T:2968`: it may xfail ONLY the
   exact tee-checksum mismatch — plant a DIFFERENT mismatch (the probe sha, the hermes-acp path) in a scratch copy of a golden
   leg and show the test FAILS (not xfails).
3. **The ONE file list (`C:1774-1775` `pins.entry_allowlist()` / `pins.required_files(version)`; `T:5368` the complete-set
   test).** Flip `argv.txt` to optional and `teardown.txt` to required in a scratch `pins.py` and show the equality test reds
   both ways (the lane's ARGV_OPTIONAL / TEARDOWN_REQUIRED rows); then a THIRD flip the lane did not run (a v2.3-only file).
   Confirm the checker never carries a literal file name outside `pins` (grep for every `.txt`/`.json`/`.jsonl` literal in the
   checker; each hit is either derived from `pins` or a finding).
4. **The scanner domains (`T:3636` `_scan_direct_writes`, `T:5001` `_presence_gate_hits`, `T:5186` `_enumerate_read_sites`).**
   Each declares its syntax families and exclusions. Plant, in scratch copies of the CHECKER, one write/read/presence shape per
   family the scanner does NOT declare: `os.open`+`os.write`, `Path.write_bytes`, `tempfile.NamedTemporaryFile`, a local alias
   (`o = open; o(p)`), `functools.partial(open, p)`, a `shutil.copy2` (not `copyfile`), `os.path.exists`, `Path.exists`,
   `os.access`, `with (p).open()`, `subprocess.run(..., stdout=fh)`. For each: does the scanner see it (red) or slip it (a
   documented exclusion — check that the exclusion is DECLARED in the scanner's docstring/test, else a finding)? Then the
   decisive question: does any EXCLUDED form occur in the checker's own production code today? A live occurrence of an excluded
   form is a hole, not a limit.
5. **The dead-branch validator (`T:5525`) and `_read_site_drift` (`T:5280`).** Re-run M14, M16, M21 through `mutants.sh` on
   scratch copies (paste the KILLED lines); then three of your own: a citation to a REAL line that is not the guard (a non-guard
   citation the validator must name), a citation with a different formatting (`L123`, `line 123`), a comment block with two
   citations of which one is wrong.
6. **VB-F12 `rows` / `table_rows` (`C:1172`; `T:2516`).** Re-run the key-replacement control; then a v2.4 scan with `rows` only,
   with `table_rows` only, with both but mismatched counts — each outcome exact.
7. **The CLI `SystemExit` domain (`C:1894-1899`; `T:2856`).** Beyond the lane's None/0/7/text: `SystemExit(True)`,
   `SystemExit(False)` (bool is an int subclass), `SystemExit(-1)`, `SystemExit(256)`, `SystemExit("7")` (an int-valued
   string). State the observed exit for each and whether the mapping's DOMAIN is closed or has a hole.
8. **Mutants.** Re-run the lane's 13 rows + the control through `tasks/briefs/s0-01-a5l-support/mutants.sh` on scratch copies
   (its `A5L_MUTANT_DIR`/`PIN` env; paste `EXPECTED=13 KILLED=… SURVIVED=… CONTROL=1`), then ≥ 8 rows of your own from items
   1-7 (each on a fresh copy; killer line pasted; survivors by construction stated as such).
9. **The report's discipline.** `python3 scripts/report_lint.py tasks/briefs/s0-01-a5l-support/A5l-report.md --root <tree>
   --map C=proofs/S0-01/check_acp_conformance.py --map T=tests/test_s0_01_check_acp_conformance.py` (the lane and the
   coordinator: `17 refs — OK 17`; reproduce). Grade `red-before.patch`: the brief asked for the red-before PATCH beside the
   driver; the lane delivered a prose record of the pre-fix reds — is each red REPRODUCIBLE from the record on the pre-round
   bytes (`git show d23762a:…`)? Reproduce two; a red that cannot be reproduced is a finding.
10. **The joint set once.** `tests/test_s0_01_*.py -n 8` on the PIN (the last floor before this round: `1556 passed, 9 xfailed`;
    expect the xfails at 13 and the passed count changed by this round's test-count delta — state the arithmetic). ONE call if it
    fits the 420 s cap (it did at 200 s on 8 workers); otherwise two halves.
11. **Discipline.** `file:line` by `sed -n` at the PIN; kill only what you start, by pid; scratch copies only; the real corpus
    READ-ONLY (copy a leg first). **Bounded gates (AF-AP-76): `report_lint.py` on your own report LAST with the three maps
    (`C`, `T`, `P=proofs/S0-01/pins.py`) and `--min-refs 20`; its `fix:` hints for at most THREE rounds, then paste the final line
    and finish.** **Bounded premises: a premise that does not reproduce gets at most THREE experiments, then one DISCREPANCIES
    line.** Every gate call under the 420 s tool cap (`-n 1` twice rather than `-n 2` once).

## Report
`tasks/briefs/s0-01-a5l-support/VERIFY-CK14-report.md`: VERDICT first (MERGE-READY / NOT-READY on the landed bytes at the
PIN, blocking findings named F1…), the FILE IDENTITY block, the item table (item → what was attacked → pasted evidence line →
finding or HELD), the mutant table (every row: mutant, killer test or SURVIVED, pasted line), the test-count reconciliation of
item 0 as a table, the scanner-domain matrix of item 4, NOT-done first-class, the lint summary line last. Numbers pasted, never
typed. Report EVERYTHING found — no severity filtering (the main loop ranks).
