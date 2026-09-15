# Lane A5m — S0-01 checker round 15: the ONE-predicate pin made EXCLUSIVE (not a presence check), the mutant driver made VALID (a mutant must compile and collect; INVALID is a verdict), VERIFY-CK14's two findings closed with red rows (build lane: PC Hermes `code-implementer` on the CLOUD build route; sandbox fallback `code-implementer`)

PIN: `1231624` (the checker, its test and `pins.py` are byte-identical to the landing b6483df: `proofs/S0-01/check_acp_conformance.py`
1907 lines sha `0ea35504…`, `tests/test_s0_01_check_acp_conformance.py` 5615 lines sha `bf7c5411…`, `proofs/S0-01/pins.py` 629
lines sha `41fa933d…` — re-derive all three with `sha256sum` + `wc -l` at the PIN and paste them as your FILE IDENTITY block; the
PIN is newer than the landing only for tooling: `scripts/pc_suite.sh set-id` exists from 753b1a5 on).

**Authorization + provenance.** The findings are VERIFY-CK14's (`tasks/briefs/s0-01-a5l-support/VERIFY-CK14-report.md`, in your
tree): F1 BLOCKER (the ONE-predicate pin is a PRESENCE check — a second local predicate consulted before the shared call
survives, measured: `7 passed, 425 deselected` with `_is_pinned_process_alt` in the tree) and F2 EVIDENCE DEFECT (A5l's driver row
TABLE_ROWS "killed" through a `SyntaxError`, rc 2 — AF-AP-78). Both premises were MEASURED by the verifier on the landed bytes; take
them as settled and build. The corpus fact in its DISCREPANCIES (no `run-2` leg in the real corpus while `pins.LEGS` requires it) is
the coordinator's (VB-F12's re-capture) — do NOT chase it; your real-leg tests must keep passing on the 5-leg corpus exactly as today.
The code-intel pack `tasks/briefs/s0-01-a5m-support/A5m-pack.md` (skeletons, the graft ask, GitNexus impact, crg, ripwire, the
registry screen over C/T/P) is in your tree — START FROM IT (CODE INTEL FIRST). Boundary: `proofs/S0-01/check_acp_conformance.py`
(C), `tests/test_s0_01_check_acp_conformance.py` (T), `tasks/briefs/s0-01-a5m-support/mutants.sh` (D, new — copy A5l's driver and
extend it), `tasks/briefs/s0-01-a5m-support/A5m-report.md`. `pins.py` (P) is READ-ONLY; if a change there looks necessary, stop
and report (the ONE list is the producer's).

## Items (build in order; every item = code + a deterministic LLM-free test + a pasted line)

1. **F1 — the EXCLUSIVITY pin (T; C unchanged unless the pin forces a shape change).** Replace the presence assertion in
   `test_ck13_checker_has_no_private_pinned_process_predicate` (T:2909-2924) with an EXACT-SHAPE pin on `_pinned_process_count`
   (C:1195-1197): its body is ONE `Return` of `sum(<GeneratorExp>)` whose single `comprehension` has EXACTLY one `ifs` entry, a
   `Call` whose func unparses to `pins.is_pinned_argv` and whose only argument unparses to `cmd.split()`; no other statements,
   no other Call nodes, no `BoolOp`/`Compare` anywhere in the function. Then a MODULE-WIDE lock: walk every `FunctionDef` in C —
   `is_pinned_argv` is referenced in exactly one function (the classifier), and no function other than the classifier contains a
   `Compare`/`BoolOp`/`in`-membership whose operands unparse to any of `PINNED_TEE_PATH`, `PINNED_AGENT_REALPATH`,
   `PINNED_BUZZ_ACP_EXE_REALPATH`, `argv`, `cmd.split()`; a helper whose NAME matches `_is_pinned_process*`/`*pinned_argv*` outside
   `pins.` is refused by name. State the enumeration in the test's docstring (which shapes are forbidden and why — the CK14 scratch
   mutant, the prefilter form, the conjunction form). Prove: the driver rows in item 3 kill it.
2. **F2 — the driver made VALID (D).** Copy `tasks/briefs/s0-01-a5l-support/mutants.sh` to `tasks/briefs/s0-01-a5m-support/mutants.sh`
   and change the verdict logic: after every row's `sed`, `python -m py_compile` EACH mutated file and run a collect-only pass
   (`pytest --collect-only -q -k "<test>"` must collect ≥ 1 test); a failure there prints `INVALID <row> <reason>` and increments
   `invalid`; a kill prints the pytest failure line pasted from the output (`FAILED …::<test> - <Exception>: …`), never a bare rc;
   the summary line becomes `EXPECTED=<n> KILLED=<k> SURVIVED=<s> INVALID=<i> CONTROL=<c>` and your report gates on `INVALID=0`
   AND `SURVIVED=0`. Keep A5l's thirteen rows and re-run them under the new logic — every one must still be a REAL kill (a pasted
   assertion line); if any of the thirteen turns out INVALID or hollow, say so in DISCREPANCIES (that is a finding, not a failure of
   this lane). Rewrite the TABLE_ROWS row: mutate C's `_SCAN_HEADER_RE` (find it in the pack) so a header whose key is `rows=` in
   place of `table_rows=` is ACCEPTED — the exact `sed` is yours to derive from the regex text; the kill must be
   `test_v24_table_rows_key_cannot_be_replaced_by_rows` (T:2516-2524) failing with `DID NOT RAISE` (paste it). A row whose sed does
   not change the file is INVALID too (assert the file's sha changed).
3. **The F1 rows (D).** Add these VALID rows (each must compile; each must be killed by item 1's test with a pasted assertion
   line): (a) the CK14 scratch mutant — define `_is_pinned_process_alt(argv)` in C and use it BEFORE the shared call inside the
   classifier (`_is_pinned_process_alt(cmd.split()) or pins.is_pinned_argv(cmd.split())`); (b) the conjunction form
   (`pins.is_pinned_argv(cmd.split()) and cmd.startswith("/")`); (c) a module-level helper named `_pinned_argv_local` that wraps
   the shared call and is used by the classifier; (d) a second function elsewhere in C that compares against `PINNED_TEE_PATH`
   (dead code, never called) — killed by the module-wide lock. Plus ≥ 2 rows of your own on item 1's shape (say what each attacks).
4. **Gates on the PC (Hermes's `terminal` tool caps ONE call at 420 s — size every call under it).** The checker file serial is
   ~680 s (VERIFY-CK14 measured `419 passed, 13 xfailed in 679.70s`) — NEVER serial: run
   `python -m pytest tests/test_s0_01_check_acp_conformance.py -n 8 -q -p no:cacheprovider --basetemp=<your scratch>` in ONE
   foreground call, TWICE, and paste both summaries; the four-file set (`tests/test_s0_01_check_acp_conformance.py
   tests/test_s0_01_pc_tools.py tests/test_s0_01_pc_post_scan.py tests/test_s0_01_acp_probe.py`) `-n 8` ONCE, pasted; the 13-file
   joint glob `tests/test_s0_01_*.py -n 8` ONCE in ONE foreground call (~204 s measured), pasted — beside EVERY count paste the set
   id from `bash scripts/pc_suite.sh set-id -- <the same files>` (no bridge needed; a count without its set id is not evidence).
   The landing floors: the checker file `419 passed, 13 xfailed` (+ your new tests), the 13-file glob `1341 passed, 13 xfailed`
   (13 files, `set=` printed by set-id at the PIN — paste yours and state the delta in tests). pyflakes rc 0 on C and T. NEVER
   background a gate (the lost-log lesson: VERIFY-CK14 backgrounded its joint run and could claim no count).
5. **Report** at `tasks/briefs/s0-01-a5m-support/A5m-report.md`: the FILE IDENTITY block (before and after), per item the pasted
   evidence line, the driver's full output + summary line, the gate lines with set ids, DISCREPANCIES (anything in the brief that
   disagreed with the tree), NOT-done. Lint LAST: `python3 scripts/report_lint.py --map C=proofs/S0-01/check_acp_conformance.py
   --map T=tests/test_s0_01_check_acp_conformance.py --map P=proofs/S0-01/pins.py --min-refs 12 <report>` — apply the lint's own
   `fix:` hint for at most THREE rounds, then paste the final line and finish (AF-AP-76: a mechanical bar is bounded).
6. **Discipline.** `file:line` by `sed -n` at the PIN; kill only what you start, by pid; scratch copies only under your lane's
   scratch dir; the real corpus is READ-ONLY (copy a leg per probe); never touch VERIFY-N5k's lane tree or the `qwen-builder` unit;
   no git writes inside the lane (the coordinator lands your bytes from the tree diff).
