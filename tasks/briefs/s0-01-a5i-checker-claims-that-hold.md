# Lane A5i — S0-01 checker, round 11: every self-claim measurable, every guard pinned, the real-leg corpus a declared input (sandbox Opus 4.6 `code-implementer`)

**PIN:** the HEAD this brief is committed in (your work lands in the CHILD commit — state both). **Verdict graded:**
`tasks/briefs/s0-01-a5i-support/verify-CK10.md` (VERIFY-CK10, round 10 on checkpoint 8p — NOT-READY: B1-B6 blocking,
F-R10-03/04/05/10/11/14/15/16/20/21/22/23/24/25 real; 1195 lines; every finding executed, with the exact red test).
**Scope (exactly two files + your report):** `proofs/S0-01/check_acp_conformance.py` (C:) and
`tests/test_s0_01_check_acp_conformance.py` (T:); report `tasks/briefs/s0-01-a5i-support/A5i-report.md`. `pins.py`,
`pc_post.sh`, `pc_suite.sh` and `tests/test_s0_01_pc_post_scan.py` are READ-ONLY (the coordinator owns the last two).
Another lane may hold uncommitted tee edits — never `git stash/checkout/restore/reset/add/commit/push`; mutants on
scratchpad COPIES (the verifier's trees under the session scratchpad `ck10/` — reuse `wk3`/`wk6`/`mat`/`wk2`); the
checker suite hashes and SPAWNS the tee, so run every gate from a `git archive <PIN>` copy plus your two files, never
from the shared tree while a tee lane is live. Every number and `file:line` in the report is PASTED from a tool run on
the FINAL tree (F-R10-17/18: the previous table predated its own last insertion).

## Design (pinned by the coordinator — build it, do not redesign it)
1. **B1 — the real-leg xfail is what it says it is.** Anchor the match on the reason's last segment
   (`result.rsplit(": ", 1)[-1] in _KNOWN_XFAIL_REASONS`), make it STRICT for real (`request.node.add_marker(
   pytest.mark.xfail(strict=True, reason=…))` before running the check, so a repaired capture turns the xfail into a
   FAILURE by design) and rewrite T:2780-2781 to describe that mechanism. Reproduce the verifier's three states on a
   scratch copy of the corpus (stale sha → xfailed; repaired sha → FAILED "unexpectedly passing"; unrelated failure →
   FAILED with the full reason) and paste all three.
2. **B2 — the F43 self-test asserts CATEGORIES, not a count** (the verifier's set-equality over the six families);
   mutants F43-SHUTIL-OFF, F43-OSW-OFF, F43-JSONDUMP-OFF must die; fix the T:3276-3278 docstring. Also widen the scan
   to the four cheap misses the verifier planted: `Path.touch`, `Path.rename`, `p.open(mode="w")` (keyword form),
   `io.open` — and state the remaining misses (os.open+os.write, variable mode, shutil.copytree/move, subprocess cp,
   module-level writes) as the scan's documented limits in its docstring (AF-AP-30: when static scanning is the
   losing game, state the limits honestly rather than grow synonyms forever).
3. **B3 — two more read paths under the walk/S_ISREG rule.** `tee_file = _require_file(HERE / "tools" /
   "frame_tee.py", leg, "tools/frame_tee.py")` at C:416 (a FIFO there must be named in < 1 s, not time out); the A1
   pre-read at C:1697 goes through `_require_file` (a directory named `manifest-post.summary` → the exact
   `is not a regular file` reason like the other 19). Fix the C:1654 comment ("walk EVERY tree") to list what the
   walk covers and what `_require_file` covers. Red tests: the verifier's `test_ck10_fifo_at_tools_frame_tee_is_named`
   (elapsed < 5 s, exact reason) and the directory case.
4. **B4 — one default-cap literal.** `main()` passes `None`/omits so `check_bundle`'s signature default (90) is the
   single source; a test asserts `0 < check_bundle default < spec.json timeout_s (120)` by reading `spec.json`;
   mutant MAIN-DEFAULT-900 becomes N/A (no second literal) and SIG-DEFAULT-900 must die on that test.
5. **B5 — the two-users pin consumed from the pin:** `test_ck10_env_respond_to_two_users_from_pin` (monkeypatch
   `PINNED_STARTUP_RESPOND_TO_TWO_USERS` → exact reason); mutant LITERAL-PINS-2U must die.
6. **F-R10-03/04/05/15 — the cap's domain and its handler hygiene.** `check_bundle` accepts only
   `_is_strict_int(timeout_s) and 0 < timeout_s <= 2**31 - 1` (bool, float, NaN, inf, str, overflow → ValueError);
   the CLI maps the same domain to rc 64 with the usage line (an overflow is a usage error, never "malformed
   evidence"); in `_check_with_timeout` the `alarm()` call moves INSIDE the `try:` so a raising `alarm()` cannot leak
   the handler (red test: `signal.getsignal(SIGALRM)` unchanged after a failing `check_bundle`; this is an AF-AP-58
   sibling — say so in the comment).
7. **F-R10-11 — the producer's invariant in full:** `owned_present + owned_zombies <= owned` (reject the impossible
   header `owned=3 owned_present=3 owned_zombies=3` with the exact reason), and the TEARDOWN scan's `owned_zombies`
   consumed the same way; red tests for both.
8. **F-R10-10 — the six dead-branch comments cite the guard that actually fires** (the verifier's table: C:922-925,
   C:894-895/906-907, `check_prompt_turn` C:747-749 for two of them); add the structural pin the verifier proposes
   (each comment block names its true guard). **F-R10-16 —** the parametrised startup test counts the keys it ran
   (`assert len(ran) == len(checks)`). **F-R10-14/23/24 —** the A25 reorder assertion exact; T:4279 and T:4288 exact;
   `test_ck9_startup_missing_keys_exact` asserts the exact computed list (the whole point of the hoist).
   **F-R10-21 —** the C:2-3 docstring NOTE states current behaviour (refused with 64), not the old symptom.
9. **F-R10-25 — the real-leg corpus is a DECLARED input, never a green-by-skip.** Replace the container-UUID
   `_REAL_LEG_DIR` literal with `os.environ.get("S0_01_REAL_LEG_DIR")`; when it is UNSET, the 51 real-producer tests
   SKIP with the exact reason `S0_01_REAL_LEG_DIR unset (real-leg corpus not declared for this venue)`; when SET, an
   absent or incomplete corpus (fewer than the 5 legs `cancel negative run-1 shutdown two-users`) FAILS loudly, never
   skips; add `test_real_leg_corpus_declared`: if `S0_01_VENUE` is `sandbox` or `pc`, `S0_01_REAL_LEG_DIR` MUST be
   set (FAIL otherwise) — CI (`S0_01_VENUE` unset/`ci`) may skip by declaration. The coordinator wires the env vars
   into `scripts/test_summary.sh`'s callers and `scripts/pc_suite.sh` (read-only for you; note what they must export
   in the report: sandbox `S0_01_REAL_LEG_DIR=<scratchpad>/realleg/golden`, PC the capture dir
   `proofs/S0-01/tools/pc/run_leg.sh` writes — read that script and name the path). Report the skip/xfail counts
   under each configuration (unset; set to the corpus; set to an empty dir).
10. **B6 — report discipline:** red-before rows labelled CONTROL when green on the parent (the verifier measured 17
    of 30 ck9 tests as controls — the mutants they kill are the evidence, say so); the collection block from the
    FINAL bytes; every file:line by `grep -n` on the final tree; the 99-failure run described by its measured cause
    (the tee moving under the run) or not at all.

## Mutants (scratchpad copies; `git status --porcelain` clean on both files after each; paste the table)
The verifier's tables A/B/C/D re-run on the final tree with every survivor KILLED by a NAMED test: F43-SHUTIL-OFF,
F43-OSW-OFF, F43-JSONDUMP-OFF, MAIN-DEFAULT-900 (→ N/A with the duplicate gone; SIG-DEFAULT-900 killed),
LITERAL-PINS-2U; plus new: CAP-BOOL (accept `True`), CAP-NAN, CAP-OVERFLOW-AS-EVIDENCE (map overflow to rc 1),
ALARM-OUTSIDE-TRY (the leak), ZOMBIES-HALF (drop the `+ owned_present` term), ZOMBIES-TEARDOWN-UNREAD,
TEE-FILE-EXISTS-ONLY (revert C:416), PRE-READ-BARE (revert C:1697), XFAIL-SUBSTRING (revert B1),
CORPUS-UUID-LITERAL (revert item 9 — killed by the venue test under `S0_01_VENUE=sandbox` with the var unset). The
24-guard combined mutant once more on the full set (the verifier's re-derived 27-line list is in its report).

## Gates (paste verbatim)
`bash scripts/test_summary.sh tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_audit_cp5_controls.py
tests/test_s0_01_pc_post_scan.py` twice from a `git archive <PIN>` copy + your two files, with
`S0_01_VENUE=sandbox S0_01_REAL_LEG_DIR=<scratchpad>/realleg/golden` exported (collection = passed + skipped + xfailed,
pasted) · once with the var UNSET (the declared skip count pasted) · pyflakes · `python3 scripts/lint_delta.py --base
<PIN>` with each hit ruled by line · the real tee under SIGTERM and clean exit through the checker (`ck10/` has the
harness). PC leg: NOT run here (coordinator's). Report shape: FILE IDENTITY, DONE table, MUTANT table, PROBE table
(the cap domain 16 CLI + 13 in-process values; the 20 directory-named files; the FIFO at tools/), NOT_DONE,
DISCREPANCIES, SELF-ATTACK.
