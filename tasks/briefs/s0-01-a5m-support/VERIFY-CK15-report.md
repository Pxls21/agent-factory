> **COORDINATOR DISPOSITION (2026-09-15 16:4xZ).** The A5m landing stands. F1 was the brief's claim, wider than the lock: the
> `allowed_compares` inventory is scoped to the classifier's operands by design — the claim is narrowed in checker round 16 (A5n), together
> with F2's labelled asserts, the literal `EXPECTED` + a driver self-test (AF-AP-84) and a per-row timeout (the NOT-done). No verdict
> was expected (single-model rule).

NO VERDICT (single-model rule): findings only. The local verifier route was not established as an independent model, so this report does not admit the landing.

MAP
C = proofs/S0-01/check_acp_conformance.py
T = tests/test_s0_01_check_acp_conformance.py
P = proofs/S0-01/pins.py
D = tasks/briefs/s0-01-a5m-support/mutants.sh
PIN = bf8a5dc

FILE IDENTITY
C sha256 7a13fbffed9fae2cc74be89bd400237a5db25ba0ae477e4e45571a4bfc347bcb; 1906 lines.
T sha256 70914ea3c4785a722e91e2b35057ea93b62f2d3e9effba9000d7edf552acc491; 5707 lines.
P sha256 41fa933d131ac24701100ba52b8959f3c7d2740b9be4336041388ab891bb83a4; 629 lines, byte-identical to PIN.
D sha256 b746a525cfeb539118d4ae5325528dadfb88fb0b583452a0788e6016e5790804; 154 lines.
C/T/D each match PIN. The only staged paths are the lane brief and PC brief; no landed source byte was edited.

FINDINGS
F1 MEDIUM — V2 inventory coverage is narrower than the stated “one legitimate-looking comparison” claim. T:2983-T:2987 only records comparisons whose operands intersect `classifier_operands`, which excludes arbitrary configuration comparisons. Scratch mutation inserted `if env.get("X") == "1": pass` immediately after `def check_env` at C:442. It compiled, collected the named test, and that test stayed green: `compile=0 collect=0 run=0`, `1 passed, 431 deselected`. This does not re-open the process-classifier bypass: comparisons against pinned process operands remain covered. But the `allowed_compares` baseline at T:2972 is not a module-wide comparison inventory. Minimal fix: narrow the stated claim to process-classifier operands, or add a separate exhaustive compare inventory if all comparisons truly must fail closed.

F2 LOW — V7 has a diagnostic gap. Six F1 row types are intentionally killed by one structural test, `test_ck13_checker_has_no_private_pinned_process_predicate` at T:2909. At least the alternate classifier, conjunction, lambda filter, walrus, and one-Return violations collapse to `AssertionError: assert False` or a generic AST-shape failure. The driver proves rejection but not shape-specific diagnostics. Minimal fix: assert labelled failure messages or split the structural contract into named component tests if per-shape diagnosis is required.

V1 SOLID
C:1195-C:1196 is exactly one return: `sum(1 for cmd in commands if pins.is_pinned_argv(cmd.split()))`. C:1274 assigns `body_pinned` from the live consumer `_pinned_process_count`; ripwire independently mapped `check_process_evidence` and `test_ck13_process_evidence_consumes_shared_predicate` at T:3027 as callers.

Fresh scratch mutation runner killed all hostile classifier shapes after compilation and positive collection: CK14 alternate predicate, conjunction, a `pinned_argv` helper, hidden second classifier wired to the sink, lambda-filter predicate, `shlex.split`, `cmd.split(" ")`, `and True`, walrus, and two comprehensions. Each recorded a real failure assertion. Example CK14 alternate: `compile_rc=0`, `collect_rc=0`, `run_rc=1`; killer T:2935, `AssertionError: assert False`.

The fresh full supplied driver was rerun from fresh `git archive bf8a5dc` trees with C/T/P overlays. Its result was exactly: `EXPECTED=19 KILLED=19 SURVIVED=0 INVALID=0 CONTROL=1`. The F1 rows all compiled, collected their selected node, and supplied both `FAILED ...::<test>` plus an `E       ` assertion detail before D:143-D:150 counted them. This closes predecessor F1’s second local predicate use at the live `body_pinned` sink.

V2 SOLID WITH F1 SCOPE LIMIT
T:2972-T:2988 uses handwritten finite expectations, not a list derived from C. The actual pinned-process comparison inventory is calculated independently and checked for equality. The F1 mutation above is the scope boundary: unrelated comparisons are not part of `classifier_operands`, so they survive. Every listed legitimate predicate is present in the running C source: `BUZZ_ACP_AGENT_OWNER` at C:470, the `buzz_found` equality at C:1313, and the tee/agent memberships at C:1317-C:1333. No stale listed process operand was observed.

V3 SOLID
A classifier docstring is forbidden by the exact one-statement shape `assert len(classifier.body) == 1` at T:2918. Scratch insertion of a docstring compiled and made the named test red: `assert 2 == 1` at T:2918. The live no-docstring rule is intentional and enforceable. The F1 mutant runner also killed `and True`, walrus, and two-`for` forms; `int(sum(...))`, `sum((...))`, and `yield` were reviewed as failing the existing AST checks (outer function/argument shape or return requirement), not separately executed.

V4 SOLID
C:1577-C:1581 cites the guard range C:1561-C:1565, which ends at the `raise Failure` line C:1565. T:5634-T:5654 reads cited source ranges and requires a real `raise Failure`, not text in the comment. Scratch change from `C:1561-1565` to `C:1561-1564` produced `1 failed, 431 deselected` with `line 1577 cites C:1561-1564, which contains no guard`. The synthetic citation attack `test_ck13_dead_branch_citation_mutants_die` at T:5657 passed in the direct two-test set; the baseline full xdist runs include `test_ck11_dead_branch_comments_cite_a_real_guard` at T:5689.

V5 SOLID
D:64-D:86 rejects non-unique/no-op edits; D:88-D:100 requires `py_compile`; D:102-D:114 requires at least one collected test. D:133-D:150 only counts a red pytest run with both `FAILED ...::<test>` and an `E       ` detail; error/collection/hang/SystemExit cases fall to INVALID (or need an outer timeout), never KILLED. No explicit timeout command exists in D:116-D:120; a hanging row would block the driver, so a dedicated timeout wrapper remains NOT-done. The fresh 19-row run above has no INVALID rows.

V6 SOLID
C:155-C:158 requires the exact `table_rows=` token in a whole header regex. Scratch replacement of that regex token with `rows=` compiled and produced the requested normal test assertion: `E Failed: DID NOT RAISE Failure` in T:2516-T:2524. Direct parser probes with both `table_rows=4 rows=4` and `xtable_rows=4` failed as `has no enumeration header`, so neither alternate form is accepted. Baseline key-replacement and citation-mutant controls: `2 passed, 430 deselected`.

V7 SOLID WITH F2 DIAGNOSTIC GAP
The six supplied F1 rows share one structural test but are not tautological: the fresh runner killed each from separately altered bytes after compile and selected-node collection. See F2 for the limited diagnostic weakness.

V8 SOLID FOR DECLARATION AND PC CORPUS
Fresh PC runs, with `S0_01_VENUE=pc`, real corpus path, and xdist: run 1 `419 passed, 13 xfailed in 141.14s`; run 2 `419 passed, 13 xfailed in 142.98s`; set id `31306c49985e` (432 collected). The declared empty corpus fails during test collection with `Failed: corpus run-1 directory absent`; it cannot silently skip. Under `S0_01_VENUE=ci` and no corpus, the selected declaration/timeline checks report `5 skipped, 427 deselected`. This is the requested declaration behavior, though it is `ci`, not literally an unset venue: the module defaults an unset value to sandbox at T:2630, where absence is deliberately a failure.

The 13 xfails are v2.2 stale-corpus assertions, not silent pass status: T:3060-T:3072 marks four tee SHA checks strict, T:3129-T:3144 marks four pre-v2.3 process scans strict, T:3232-T:3236 marks the negative stale result, and T:4399-T:4403 handles missing tee status. The full `-rxX` serial diagnostic attempt exceeded the 420 s host tool cap and was not used as count evidence.

V9 SOLID
C/T/D/P identities above were independently rehashed and compared with the PIN. `/home/rocco/venv-agent-factory/bin/python -m pyflakes C T` returned rc 0. AP screen reports 11 existing C hits and four existing T hits; no lane source edit occurred. Final `report_lint`: `19 refs — OK 15, NEAR 3, MISS 0, UNCHECKABLE 1, UNRESOLVED 0 (worktree)`; its sole uncheckable citation is C:1565 at the correct `raise Failure` endpoint.

DISCREPANCIES
- The initial citation mutation used a range where another guard remained, so it stayed green. One corrected scratch mutation ending before C:1565 was red. This is a scratch-probe correction, not a production defect.
- A first table mutation command placed a relative `--basetemp` under the archive tree and errored in fixture setup. A new archive with an existing adjacent base directory reproduced the valid `DID NOT RAISE Failure` red.
- `/usr/bin/python3` lacks pyflakes; the mandated venv invocation passed.
- GitNexus returned `Target '_pinned_process_count' not found`, risk UNKNOWN, against the clone index. Graft/ripwire map the live consumer; no reachability conclusion relies on GitNexus.
- Full serial `-rxX` exceeded the fixed 420 s tool cap. It was stopped by the host; neither its partial output nor builder’s claim substitutes for the two completed xdist runs.

NOT DONE
- D has no per-row timeout. Add an explicit bounded timeout row/runner to make hangs INVALID rather than a host-level stuck gate.
- V3’s `int(sum(...))`, `sum((...))`, and `yield` have static AST coverage only; no separate red probes were retained.
- Required report lint has not yet run. No commit, push, corpus mutation, production proof mint, or outward-facing action occurred.
