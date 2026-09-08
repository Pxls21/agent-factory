# Lane A5l — S0-01 checker round 14: the ONE list CONSUMED (no private pinned-process predicate, no private version fold), the SystemExit domain closed, the three scanner domains declared and enforced per family, the complete per-version sets pinned, the thirteen survivors killed by name, VB-F12's strict xfail, the mutant driver and the red-befores committed (build lane: PC Hermes `code-implementer`; sandbox Opus 4.6 `code-implementer` only if the bridge is down)

PIN: (HEAD at dispatch — the commit carrying this brief; the report header says "PIN: `<sha>`".) The checker's last checkpoint is
9c = `77f46a2` and its files are unchanged since (VERIFY-CK13's identity table): `proofs/S0-01/check_acp_conformance.py` 1911
lines sha `25b89431…`, `proofs/S0-01/pins.py` 381 lines sha `84a1e5c8…` (the coordinator's merged file), `tests/test_s0_01_check_acp_conformance.py`
5275 lines sha `ce62bc62…`, `tests/test_s0_01_audit_cp5_controls.py` 144 lines sha `457430b1…`, `negative_contract.py` 222 lines
`b397f6b7…`, `check_initialize.py` 222 lines `304d44d6…`. Line numbers below are those bytes'. **Lane P5c-b is editing `pins.py`
RIGHT NOW in its own tree (the per-file constraint table) — you READ `pins.py` and never edit it; the coordinator merges.**

**Why:** VERIFY-CK13 (`tasks/briefs/s0-01-a5k-support/VERIFY-CK13-report.md` — READ IT WHOLE FIRST; it is the contract for this
round) graded round 13 NOT-READY with nine blockers, every one reproduced on the PC from `git archive 77f46a2` copies:
**CK13-02** the checker's private `_is_pinned_process` (`C:1198-1202`) never calls `pins.is_pinned_argv` (`pins.py:331-359`) —
on the same rows `/usr/bin/cat <tee>` and `/tmp/runner <tee>` are pinned for the checker and rejected by the producer
(`pc_post.sh:36-45` calls the shared function); **CK13-03** three corpus-version policies: the test's `_corpus_version` fold
(`T:2664-2702`) downgrades an unknown `# process-scan v9.9` header to v2.2 where `pins.corpus_version` (`pins.py:305-328`)
refuses it, and the checker derives `allowed`/`required` from `PINNED_LEG_FILES` locally at `C:1774-1793` with its own
`_captured_leg_version` (`C:1688-1702`, prefix sniffing, `min()` over legs) instead of `pins.required_files` /
`pins.entry_allowlist` (`pins.py:279-302`); **CK13-04/05/07** the read inventory (`T:5010-5043`) misses `os.fdopen`,
`shutil.copyfile`, a subprocess path consumer; the AP-40 detector (`T:4931-4991`) misses `p.stat()` under a caught `OSError`,
`os.path.getsize`, `next(p.glob(…), None)`; F43 (`T:3537-3700`) misses `os.link`, `shutil.move`, `tar.extractall` — every plant
`1 passed, 382 deselected`; **CK13-06** `SystemExit("text")` escapes the CLI catch (`C:1893-1907`, `int(se.code)`) as an uncaught
`ValueError`; **CK13-08** 13 of 40 expected-kill mutants SURVIVE (32.5 %): the seven scanner plants, `table_rows`→`rows` in the
v2.4 header, `argv.txt` made optional, `teardown.txt` made required, M14 (the citation check reads `matches[:1]`), M16 (a
citationless comment passes), M21 (the read-golden-list test rebinding `expected = actual` survives); **CK13-09** the
representative pin (`T:5122-5124`) protects `timeline.jsonl` only; **CK13-10** A5k's red-before `2 failed, 1 passed` is NOT
reproducible from any archive (its base was an uncommitted P5a patch); **CK13-11** the PC's checker ROOT
`/home/rocco/s0-01-pinned/realleg` lacks `manifests/` — no complete direct-checker bundle exists (the coordinator's, item 9);
**CK13-01** the A5k report's lint at the joint PIN `52 refs — OK 51, MISS 1` (corrected by the coordinator in the commit carrying
this brief — re-run and paste). What held and must stay held: the shared regular-file helper and its FIFO refusal on both guarded
readers (`negative_contract.py:60-74`, `check_initialize.py:39-49`), the alarm restore order, the bidirectional sidecar
(`T:2770-2803`), exact whole-reason negative grading (`T:3028-3051`), the lossy reason, the symlink-root refusal, the six
dead-comment controls, the 27 killed assertions, the headline `374 passed, 9 xfailed` and the four-file `490 passed, 9 xfailed`.

**Inputs (read in this order):** VERIFY-CK13 whole · the A5k brief and `tasks/briefs/s0-01-a5k-support/A5k-report.md` ·
VERIFY-P5b F5 (the same predicate gap seen from the producer's side) · `proofs/S0-01/pins.py:255-359` (the ONE list's functions:
`PINNED_LEG_FILES_SINCE`, `PINNED_SCAN_VERSIONS`, `required_files`, `entry_allowlist`, `corpus_version`, `is_pinned_argv` — their
docstrings are the contract) · `proofs/S0-01/tools/pc/pc_post.sh:36-45` (the producer's call) · `docs/INCIDENT-LOG.md`
(AF-AP-40, AF-AP-42 — the hand-copied predicate row, AF-AP-63, AF-AP-64, AF-AP-65, AF-AP-72) · the pack
`scripts/lane_context.sh -q 'which functions decide a pinned process and a corpus version, and who calls them' -s _is_pinned_process _captured_leg_version _parse_scan_v24 check_process_evidence _check_bundle_uncapped -o pack.md proofs/S0-01/check_acp_conformance.py proofs/S0-01/pins.py`
(run it first; attach it).
**Scope (exactly these + your report):** `proofs/S0-01/check_acp_conformance.py` · `tests/test_s0_01_check_acp_conformance.py` ·
`tests/test_s0_01_audit_cp5_controls.py` · `tasks/briefs/s0-01-a5l-support/{mutants.sh, red-before.patch}` (item 10) · report
`tasks/briefs/s0-01-a5l-support/A5l-report.md`. NOT yours: `pins.py` (P5c-b's; read-only — if a shared function you need is
missing or wrong, STOP and report it as a blocker, never re-implement it locally: that is CK13-02 again), `negative_contract.py`
and `check_initialize.py` (read-only unless an item names a line), the probe (N5j), the tee (B5k), the backend (D5n), the PC
tools (P5c-b), `.claude/hooks/*`, `scripts/*`. Shared-tree rules: never `git stash/checkout/restore/reset/add/commit/push`;
every gate from a `git archive <PIN> | tar -x` copy under your lane's scratch dir with your files copied in
(`scripts/lane_gate.sh -r <PIN> -f "<your files>" -t "tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_audit_cp5_controls.py tests/test_s0_01_negative_contract.py tests/test_s0_01_check_initialize.py" -n 2`,
ONE foreground call with `-n 8` on the PC — about 3 minutes; `LANE_GATE_DIR` under your scratch dir); explicit `--basetemp`;
every FIFO probe standalone under `timeout --foreground 10s`; kill only your own processes by pid; NEVER background a run and
stop; no outward actions; the real corpus `/home/rocco/s0-01-pinned/realleg/golden` is READ-ONLY (copy under your scratch dir
per probe); never read, print or commit a credential. Venue exports `S0_01_VENUE=pc
S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`. Authorization: the owner's own ACP conformance checker under test.

## Design (pinned — build it, do not redesign it)
1. **CK13-02 — ONE predicate.** Delete `_is_pinned_process` (`C:1198-1202`); every site that classified a scan row calls
   `pins.is_pinned_argv(cmd.split())`. Test: the six-row divergence table from VERIFY-CK13 becomes ONE parametrized test that
   runs the checker's classification of a synthetic scan row and the producer's shared function and asserts they are the SAME
   function (identity: `cc.<classifier> is pins.is_pinned_argv`, or the checker module exposes no callable that classifies a
   row other than through `pins.`). AST pin in the test: no function in the checker module compares any name to
   `PINNED_TEE_PATH` / `PINNED_AGENT_REALPATH` / `PINNED_BUZZ_ACP_EXE_REALPATH` outside a `pins.` call (a re-introduced local
   copy is red — that is the AF-AP-42 regression).
2. **CK13-03 — ONE version policy.** `_captured_leg_version` (`C:1688-1702`) calls `pins.corpus_version(golden / leg)` per leg;
   a `ValueError` becomes `Failure(f"{leg}: {exc}")` (never a downgrade); the legs must agree or the failure names the disagreeing
   set; `allowed` / `required` at `C:1774-1793` come from `pins.entry_allowlist()` / `pins.required_files(version)` — the local
   `PINNED_LEG_FILES_SINCE` fold and `_version_before` go (read `pins.py:279-294` first: `required_files` already applies the
   `SINCE` rule; if it does not, STOP and report). The test's `_corpus_version` (`T:2664-2702`) calls `pins.corpus_version` per
   leg with the same agreement rule; an unknown header → `pytest.fail` naming it. Red tests (RED on the PIN — paste): a scratch
   corpus whose `process-scan-after.txt` header reads `# process-scan v9.9 …` → the checker's failure names
   `unrecognised process-scan header version` (today: silently v2.2) and the test fold fails with the same name (today: v2.2).
3. **CK13-06 — the SystemExit domain.** `C:1893-1907`: `None` → 70; `type(code) is int` → that code; anything else (`str`,
   `bool`, an object) → 70 with `failure_reason: check exited with a non-integer status: {code!r}` on stdout. Tests for `None`,
   `0`, `7`, `"text"`, `True` — each the exact rc and line; `os._exit` is out of scope (say so).
4. **CK13-04/05/07 — the three scanner DOMAINS declared as data, enforced per family.** Each scanner gets a family table
   (name → the syntax it recognises) and ONE parametrized self-test that plants each family and asserts the named hit, plus a
   docstring line naming what is OUTSIDE the domain. Add to the read inventory (`T:5010-5043`): `os.fdopen(...)`, `io.open(...)`,
   `Path.open` reached through an alias or an `ExitStack`, `shutil.copy`/`copy2`/`copyfile` (source side), `subprocess.*` calls
   whose argv carries a path expression (as the `consumer` family — named, never silently excluded). Add to the AP-40 detector
   (`T:4931-4991`): `p.stat()` / `os.stat(p)` / `os.path.getsize(p)` / `os.path.isfile(p)` inside a `try` whose handler catches
   `OSError` (or a subclass) without always raising; `next(p.glob(...), None)`; `any(p.glob(...))`. Add to F43 (`T:3537-3646`):
   `os.link`, `os.symlink`, `shutil.move`, `tarfile`/`zipfile` `extractall` and `extract`. The seven CK13 plants are the red
   tests (each `1 passed, 382 deselected` on the PIN — paste).
5. **CK13-09 — the complete per-version sets pinned.** Replace the representative pin (`T:5122-5124`) with literal frozensets in
   the test for `pins.required_files("v2.2")`, `("v2.3")`, `("v2.4")` and `pins.entry_allowlist()` (the test's literal is the
   second, independent copy that makes any status change visible), plus an in-process checker run over a copy of the committed
   golden bundle with each required name removed in turn (parametrized over `required_files("v2.4")`) asserting the checker
   names exactly that file. Mutants `argv.txt`→optional and `teardown.txt`→required must die here.
6. **CK13-08/13 — the thirteen survivors killed by name.** `table_rows`→`rows`: a malformed-key v2.4 header test asserting the
   exact key names the regex requires; M14: the citation check iterates EVERY match (a self-test feeds a comment block with two
   bad citations and asserts both are named); M16: a citationless comment → named; M21: extract the read-golden-list comparison
   into a pure `_read_site_drift(expected, actual)` and self-test it with a planted drift set (a rebinding mutant then dies);
   the seven scanner plants (item 4); the two set mutants (item 5).
7. **VB-F12 — the runtime-identity test is strict.** `test_real_leg_runtime_identity` (`T:2898-2906`) today accepts both
   outcomes. New shape (the same as `T:2965-2973`): on a v2.2 corpus (`_CORPUS_VERSION == "v2.2"`) a STRICT xfail with reason
   `corpus v2.2 predates the final tee: tee_sha256 mismatch` where the failure must equal exactly `f"{leg}: tee_sha256 mismatch"`
   and any other failure hard-fails; on a v2.3+ corpus the check must pass outright. After the coordinator's re-capture the xfail
   arm is dead code and the test passes.
8. **CK13-01 — the A5k report's stale range** is corrected by the coordinator in this brief's commit (`pins.py:196-199` →
   `pins.py:203-206`); re-run `report_lint.py` on it at your PIN and paste `52 refs — OK 52`.
9. **CK13-11 — NOT this lane's**, but STATE it: the report names the two roots (the checker's root `<realleg>` with `golden/` as
   its child; the corpus root `<realleg>/golden` the tests use) with the line that constructs `root/golden` (`C:1709-1719`) and
   says which files the checker root lacks today (`manifests/`). No workaround, no fixture that pretends a parent root exists.
10. **The driver and the red-befores are COMMITTED artifacts.** `tasks/briefs/s0-01-a5l-support/mutants.sh` — the exact mutation
    driver (one mutant per invocation on a fresh `git archive <PIN>` copy, the selection and the expected killer named per row) so
    the verifier re-runs the SAME set, not a class reconstruction; `tasks/briefs/s0-01-a5l-support/red-before.patch` — the planted
    sources / red fixtures of items 2, 4, 5, 6 as a `git diff` against the PIN, so "RED on the PIN" is reproducible by anyone
    (CK13-10 must never recur). Mutants ≥ 40: the 13 survivors, CK13's 27 kills and A5k's classes re-run — every row with the
    killer line pasted; by-construction survivors stated as such.
11. **Report discipline:** FILE IDENTITY of the FINAL bytes; every `file:line` from `grep -n` on the FINAL bytes, written on the
    SAME line as the claim it supports (VERIFY-CK13's own lint read `OK 1, UNCHECKABLE 25` because its refs sat in prose lines the
    linter cannot tokenise — do not repeat that), and
    `python3 scripts/report_lint.py <report> --rev <PIN> --map C=proofs/S0-01/check_acp_conformance.py --map T=tests/test_s0_01_check_acp_conformance.py --map A=tests/test_s0_01_audit_cp5_controls.py --map P=proofs/S0-01/pins.py --map N=proofs/S0-01/negative_contract.py --map I=proofs/S0-01/check_initialize.py`
    pasted with MISS 0 and UNCHECKABLE ≤ 3; the two gate RESULT lines; the headline and the four-file xdist counts (the floor is
    `374 passed, 9 xfailed` / `490 passed, 9 xfailed` — every new test raises it; paste yours); the real-corpus selections with
    the nine xfails EXECUTED (paste the counts); pyflakes; `ap_screen.py` over the three S0-01 checker sources classified by run;
    the pack attached; NOT-done first-class. NOT this lane's: the parent-root bundle (CK13-11), the re-capture (VB-F12's live
    half), `pins.py` (P5c-b), the A5k report beyond the stamp the coordinator applied.
