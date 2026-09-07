# Lane D5l — S0-01 scripted backend, round 15: the CLASS closed, not the instance — a structural ban with a negative control on its own tooling, every "served" test pinning the record, one extras literal, a token file that cannot hang the backend, and a report the linter passes (PC Hermes lane, role `code-implementer`)

PIN: 13c1bd28713a61fdf1106e2872775ce47c1a7fe6
(HEAD at dispatch; the three scope files are byte-identical to checkpoint 8w = 8695636. Your work lands in the CHILD
commit — the report header says "PIN: `13c1bd2`; landing = the coordinator's checkpoint, made after this report".)

**Verdict graded:** `tasks/briefs/s0-01-d5l-support/verify-D5k.md` (VERIFY-D5k, round 14 on 8w — NOT-READY on F1/F2/F3/
F4/F5/F7/F12/F13; real F6/F8/F11; 659 lines; "the code is right, and I could not break it": 41 mutants, 30 000 hostile
vectors, 432 live cells, 26 legitimate values — no leak, no new false positive. Every blocker is a report or
test-strength defect with a one- or two-line fix stated in the verdict; use its code verbatim.)
**Class sweep:** `tasks/briefs/s0-01-sweep-support/SWEEP-prod.md` row #43 (a FIFO at the token path hangs startup) and
row #26 (the `errors="ignore"` decoders are SAFE-BY-DESIGN — do not touch them).
**Context pack:** `tasks/briefs/s0-01-d5l-support/pack-backend-d5l.md` (graft skeletons with line ranges for all three
files, the whole-file registry screen, the symbol map) — read it before the files; it is the map.
**Scope (exactly four files + your report):** `proofs/S0-01/tools/scripted_backend.py` ·
`tests/test_s0_01_scripted_backend.py` · `tests/red/test_s0_01_backend_credential_screen.py` ·
`tasks/briefs/s0-01-d5j-support/cost_probe.py` (the committed harness; edit only if item 5 needs it) · report
`tasks/briefs/s0-01-d5l-support/D5l-report.md` (write it in your worktree so it travels with the patch, AND return it
whole as your final message). Everything else READ-ONLY. You work in a detached worktree at the PIN on the owner's PC:
never push, never open a PR, never touch anything outside the worktree, never stop or restart any server on the PC
(OmniRoute, the Buzz relay, Ollama, Phoenix, OpenObserve, neo4j), never read or print any credential; the backends you
start bind 127.0.0.1 on a free port and are stopped by pid (`Popen.terminate()`), never by name. NEVER background a
run and stop — every gate is one foreground call whose output you paste. Bytes and code points as `0xNN` / `U+NNNN` in
code, never raw. The interpreter is the repo venv `scripts/pc_suite.sh` names as `PC_PY` (Python 3.13, UCD 15.1).

## Why this round exists (read once, then build)
Round 14 fixed instances again. The `!= MARKER` ban was written as a `grep -cP` over test source: an EMPTY stdout on
ANY tool failure reads as "zero hits", so a grep without `-P` (or a renamed file) leaves the guard green over a real
violation (registry **AF-AP-60**); and it bans one SPELLING — `_b = …["body"]; assert _b != MARKER` plus the
record-blanking mutant is `5 passed` (**AF-AP-61**). The test written to close D5j-F6 repeats D5j-F1: it never asserts
the record, so a mutant that blanks every recorded `x-trace` value passes all 537. The extras literal exists in three
unlinked copies; deleting the ten reserved entries from the impl's copy passes all 537. The cost section replaced a
wrong number with a wrong mechanism. Seven `file:line` refs were wrong while the report claimed they were grep-derived.
This round closes each CLASS and proves the closure with the mutant that beat the previous round.

## Design (pinned by the coordinator — build it, do not redesign it)
1. **The `!= MARKER` class banned STRUCTURALLY, with a negative control on its own tooling (D5k-F3 + F4; AF-AP-60/61).**
   Replace `test_no_not_equal_marker_assertions` (`red:1180-1195`) with an AST walk over BOTH test files: every
   `ast.Assert` whose test contains an `ast.Compare` with an `ast.NotEq` operator and a `Name` `MARKER` anywhere in
   the comparison is a violation, whatever the left-hand expression (the verdict's code, verbatim). No subprocess, no
   regex over source. De-vacuous it INSIDE the test: write two scratch modules to `tmp_path` — one with the BREAK form
   (`assert json.loads(x)["body"] != MARKER`) and one with the EVADE form (`_b = …["body"]` / `assert _b != MARKER`) —
   and assert the walker reports exactly 1 and 1 (line numbers included); then assert 0 over the two real files. A
   third scratch module with the POSITIVE form (`assert _b == expected`) must report 0. Rejected: keeping the grep with
   a `returncode in (0, 1)` check — a form ban with a floor is still a form ban. Mutants MARKER-GUARD-BREAK and
   MARKER-GUARD-EVADE (the verdict's) must both FAIL this test; paste both runs.
2. **Every "served" test asserts the POSITIVE recorded value (D5k-F5; the D5j-F1 class made redundant, not
   load-bearing).** `test_pct_dense_junk_that_now_saturates_is_served` (`red:1200-1212`) gains
   `assert json.loads(recs[-1].read_text())["headers"]["x-trace"] == vec` (the verdict's line). Then AUDIT: every test in
   either file whose name contains `served` or `is_served` or `verbatim` or that asserts a `200` after sending a
   credential-shaped value must assert the recorded field `==` what the wire carried (body, header value, query, or
   path — whichever the vector used). List every such test in the report with the assertion line; add the missing
   ones. Mutant RECORD-HDRVAL-BLANKED (`backend:528`, every recorded `x-trace` value → `""`) must FAIL — paste the run
   (it passed 537 on the PIN).
3. **One extras literal (D5k-F6).** In `test_invisible_table_is_the_ucd_15_1_class` add `assert sb._INVISIBLE_EXTRA ==
   extra` next to the local literal; in `test_oracle_table_equals_the_impl_table` add `{ord(c) for c in
   red._INVISIBLE_EXTRA} == sb._INVISIBLE_EXTRA` (adapt to the oracle's actual type — read `red:94-103` first). Mutant
   IMPL-EXTRA-DRIFT (delete `0x2065` and `0xFFF0-0xFFF8` from `backend:146-148`, ranges untouched) must FAIL — it
   passed 537 on the PIN. Rejected: making the impl read the extras at runtime (the class is the pinned table, D5i-F3).
4. **The token file cannot hang the backend (SWEEP-prod #43; the AF-AP-30 read class, backend side).** At the startup
   gate (`backend:766-790`) the `stat()` result is already in hand: refuse with rc 2 and a named message
   (`token file is not a regular file: <path>`) when `not stat.S_ISREG(st.st_mode)` — BEFORE `load_token` reads it.
   Test: a FIFO at the token path with mode 0600 → the backend exits 2 with that message within 5 s (run it as a
   subprocess with `timeout=10`; on the PIN the subprocess HANGS and the test fails by `TimeoutExpired` — that is your
   red-before, paste it). Same class, same gate: a DANGLING SYMLINK at `--record-dir` (D5k-F11) passes both startup
   guards today and dies at the first record; refuse it at startup (`args.record_dir.is_symlink() and not
   args.record_dir.exists()` → rc 2, named). Test both; both red on the PIN.
5. **The cost section tells the truth (D5k-F7).** Replace the "raw-socket probe skips http.client overhead" sentence
   in the backend docstring / cost prose with the measured fact: head-to-head in one window the two harness styles are
   identical (0.378 s each at 1000 KB); the residual against the D5i figure is load, not harness. Re-run
   `cost_probe.py` once on the PC and paste the table with `/proc/loadavg` before and after (no new mechanism claims).
6. **Dead helper (D5k-F8).** Delete `_last_record_text` (`red:80-81`): zero callers, and the only `[-1]` record read
   without a delta. The report's "[-1] audit" line then holds unconditionally.
7. **The registry screen at zero.** `python3 scripts/ap_screen.py --tests tests/test_s0_01_scripted_backend.py
   tests/red/test_s0_01_backend_credential_screen.py` must show NO AF-AP-60 and NO AF-AP-61 hit after item 1 (both
   fire on the PIN at `red:1190` / `red:1191`); paste the tool's output. Classify any other hit by running it.
8. **Report discipline (D5k-F1 / F2 / F12 / F13 — the fourth round of this class; this time it is mechanical).**
   Before returning: `python3 scripts/report_lint.py tasks/briefs/s0-01-d5l-support/D5l-report.md --rev <PIN>
   --map backend=proofs/S0-01/tools/scripted_backend.py --map main=tests/test_s0_01_scripted_backend.py
   --map red=tests/red/test_s0_01_backend_credential_screen.py --map cost_probe=tasks/briefs/s0-01-d5j-support/cost_probe.py`
   — for refs into files you CHANGED use `--rev` of nothing (the worktree) and say which. Paste the summary line;
   MISS must be 0; every NEAR fixed. Every `file:line` from `grep -n` on the FINAL bytes, pasted, never typed. The
   MUTANT table carries EVERY row named below with `ran` = tests EXECUTED and `failed` = the TRUE count, every killer
   NAMED (D5k-F2: 5 not 1, 2 not 1). NOT_DONE lists every brief item or gate you did not run, with the reason — "None"
   is a claim you must be able to defend line by line. DISCREPANCIES: anything the verdict or this brief got wrong.

9. **The 18-class self-sweep over YOUR test file(s) (the owner's mandate: classes, not instances).** Run the class list of
   `tasks/briefs/s0-01-sweep-support/SWEEP-prod.md` § "The classes" (presence-gated checks, reads outside the walk / no
   S_ISREG, stale `[-1]` over produced records, negative acceptance assertions, substring/tail anchors classifying outcomes,
   env-domain fail-opens, lossy decodes on a decision path, broad catches, waits/polls + ordinal gates in fakes (AF-AP-57),
   skips/xfails that cannot fire, world-scoped enumerations (AF-AP-59), signal installs before their try (AF-AP-58),
   `/proc/<pid>/exe` races (AF-AP-55), mirrors of the code under test, two counters over different populations asserted
   equal, provably redundant guards, hardlink-clobbering writes, anything else that is a family) over your test files by AST
   or grep, RUN every instance (a mutant or a planted input), and table them: `class | file:line | verdict (DEFECT / SAFE —
   guard named / DOCUMENTED-LIMIT / EQUIVALENT) | the run | fix | red test`. Fix every DEFECT row in THIS round. An Opus-5
   sweep lane is grading the same files in parallel; its table reaches the verifier — a class you missed and it found is a
   blocker, a class you both found is closed. An empty class is a result: say so.

## Mutants (scratchpad copies under `$TMPDIR`; `git status --porcelain` clean on the scope files after each; paste)
MARKER-GUARD-BREAK · MARKER-GUARD-EVADE (+ BODYSTR-RECORD-BLANKED together, the verdict's `5 passed` reproduction, now
red) · RECORD-HDRVAL-BLANKED · IMPL-EXTRA-DRIFT · TOKEN-FIFO-UNGUARDED (revert item 4 → the FIFO test times out) ·
RECDIR-SYMLINK-UNGUARDED · BODYSTR-RECORD-BLANKED · BODYSTR-RECORD-ONECHAR · O-TABLE-DROP · ORACLE-DRIFT ·
TABLE-DROP-RESERVED · UQ-REPLACE-BOTH (all 5 killers named) · RECORDLESS_400_APIKEY (both killers named) ·
TABLE-DROP-42 / FILLERS / CS / ME / ZLZP · RECORDLESS_400_XTRACE · plus the survivors the verdict classed EQUIVALENT
(ORACLE-EXTRA-DRIFT, CTL_PARTIAL_noC1 predicate form) re-stated with their qualification. ≥ 22 rows.

## Gates (paste verbatim; one foreground call each)
`$PC_PY -m pytest tests/test_s0_01_scripted_backend.py tests/red/test_s0_01_backend_credential_screen.py -q -p
no:cacheprovider` twice from a `git archive <PIN>` copy + your four files (paste both summary lines; they must agree)
· the red file standalone · `pyflakes` on the four files · `python3 scripts/lint_delta.py --base <PIN>` · the
72-code-point × 2-sink sweep on 3.13 (the verdict's; paste `non-conforming cells: 0`) · the impl-vs-oracle strip-domain
differential (`impl − oracle = 0`) · the live controls of the D5k brief item 7 (≥ 50 redactions with the count,
normal + streaming after them, `Connection: close` on every 4xx) · `report_lint.py` and `ap_screen.py` as in items 7-8
· the process census after your runs (`/proc/<pid>/cmdline` per live python, never `ps | grep`). NOT run here: the
sandbox 3.11 leg and the PC `-n 8` gate of record (coordinator's). Report shape: FILE IDENTITY (FINAL bytes, sha256 +
lines, four files), DONE table (item → file:line → the red-before line → the green line), MUTANT table, PROBE tables,
NOT_DONE, DISCREPANCIES, SELF-ATTACK (what a hostile reviewer would still try — and what you ran against it).
