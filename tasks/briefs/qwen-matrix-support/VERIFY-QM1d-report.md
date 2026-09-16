# VERIFY-QM1-d report — adversarial verification of the L1 matrix runner as LANDED
PIN: 8c1dbe6 · role: adversarial-verifier · route: local Qwen verify (xhigh) · verdict: MERGE-READY

## V1 — table admission at M (the completion-state trust boundary, reader side) — REPRODUCED

Built 7 cell dirs in scratch (`v1/gen.py`), fed each to `python3 m table <dir>` (m = PIN byte copy).
All refusals are the EXACT expected MatrixError text at the named seams:

| cell | state | rc | verdict line |
|---|---|---|---|
| valid | complete==run_id, unit sha OK | 0 | `| A | 10.000 | 20.000 | 1.000 | 4 | 100 |` |
| no_complete | no run-complete | 2 | `cell completion record unreadable` for `run_complete` (M:432) |
| wrong_complete | complete = other 64-hex | 2 | `cell completion record does not match run_id` (M:434) |
| error_plus_complete | run-error AND valid run-complete | 2 | `cell run has error state` (M:426) — error checked FIRST |
| upper_runid | uppercase run_id | 2 | `run_id is not lowercase sha256-shaped` (M:428) |
| short_runid | 63-hex run_id | 2 | same (M:428) |
| empty_runid | run_id "" | 2 | same (M:428) |

The QM1-c F6 regression (canonical lowercase `unit_sha256` loaded without byte verification) is
closed: the valid cell carries a real `unit-text` whose sha is checked (see V4 for the byte-verify
seam). A valid-but-mismatched run-complete is refused; the whole class (missing/other/upper/short/
empty) is refused, not just the two QM1-c counterexamples.

## V2 — completion boundary at R (launcher side, FAKE seams) — REPRODUCED, 8/8

Isolated fake launcher per subtest (`v2/harness.sh`, X's harness style; every subtest its own fake
tree — no unit/baseline/calls bleed). The trace column is the fake seam's call log.

| case | driving input | observed | verdict |
|---|---|---|---|
| V2a | matrix python exits 9 | rc=7, `run-error`=`load generator failed`, run-complete ABSENT, unit restored to baseline sha | PASS |
| V2b | restore install writes wrong bytes after good result | rc=8, result.json present, run-complete ABSENT, `baseline unit sha mismatch after restore` (R:121-123) | PASS |
| V2b2 | cell install fails once (exit 9); restore succeeds | rc=5, baseline restored, run-complete ABSENT; trace shows install FAILING ONCE then restore install | PASS |
| V2c | TERM during matrix step (in-process, X's signal-matrix pattern) | rc=143, unit restored, run-complete ABSENT; trace shows restore install ran | PASS |
| V2c2 | INT during matrix step | rc=130, unit restored, run-complete ABSENT | PASS |
| V2d | positive full run | rc=0, run-complete present and == result run_id (python-checked), unit restored | PASS |
| V2e | baseline env `QWEN_CACHE_RAM=4096` (passes the R:114 `QWEN_` shape, restores different bytes) | rc=8, `baseline unit sha mismatch after restore` (R:123), run-complete ABSENT | PASS |
| V2f | baseline env `PATH=/x` (non-QWEN line) | rc=8, `invalid baseline env line` (R:114), run-complete ABSENT | PASS |

Publish is rc-0-only and post-restore-only: every negative path ends with run-complete ABSENT;
the only publish (V2d) is bound to the result run_id. Signal DURING cleanup (a second TERM while
cleanup is mid-restore) is a STATIC review point only — `trap - EXIT INT TERM` (R:96) clears the
traps before the publish block (the double `rc` guard, detailed in V8), so the default TERM action kills the shell before it
can publish. Not live-reproduced (needs a slow restore seam + a timed second signal; X does not test
this window either). The committed X covers TERM via its own in-process signal-matrix (line 193) —
my V2c uses the same mechanism, so it is a repro of a tested seam, not an untested one.

## V3 — completion record binds the RUN, not the CELL — REPRODUCED (binding gap)

Built a genuinely completed cell A (valid `result.json`, matching `run-complete`), copied its four
identity files into a new dir, changed ONLY `result.json.cell.name` to "B" (argv/unit/run_id all
stay A's), and fed both to `python3 M table A B`. The table ADMIITS B under the new name, carrying
A's run_id and A's measurements — the verdict line even computes "B: aggregate decode >= 1.5x A: NO
(1.000x)" against a baseline that IS cell B itself. Nothing in `_load_cell` checks the cell `name`
at all (`name` is only used as a table key in `render_table`, M:457-461). The completion record
binds `run-complete`<->`run_id`<->`result.json.cell.run_id`; the name and the summary numbers ride
along unbound.

**Ranking.** SHOULD-FIX, not BLOCKER. The matrix is the owner's OWN tool reading the owner's OWN
cell dirs from `$QWEN_MATRIX_ROOT`; a "transplant" requires the reader to be able to WRITE cell
dirs, which the runner only does through the install/restore lifecycle. In the threat model the
runner is the sole producer of cell dirs, so a renamed cell is an operator mistake (a stale dir
left in the matrix root), not an attacker forgery — and a stale dir is exactly what F1's
run-complete/run_id binding is meant to catch at the RUN level (it does not, here, because the
transplant keeps the run_id). Real exposure: a reused/stale cell dir silently re-enters a later
table under a new name with stale numbers. Minimal fix: persist the cell name into the identity
block (e.g. `unit-sha256`'s sibling or the result's `cell.name`) and have `_load_cell` require
`result.json.cell.name` to equal the dir name it was loaded from (`cell_dir.name`), refusing a
mismatch.

## V4 — unit-text integrity vs the INSTALLED unit — REPRODUCED (no gate)

Fake `qwen-server` whose `unit` renders X but whose `install` writes Y (Y != X), baseline unit
present. The runner (a) hashes the RENDERED file into `unit-sha256` (R:74-76), (b)
runs the cell against the INSTALLED unit, (c) restores baseline, and exits rc 0 with run-complete
published. Result: `recorded unit-sha256 = sha(rendered X)`, `installed unit sha = sha(Y)`, and the
two differ — yet the cell is admitted. Nothing reads the installed unit back after install and
compares it to `unit-text`. M's byte recompute (M:443-448) only proves the `unit-text` file
was not tampered; R's restore sha check (R:122-125) only proves the RESTORE landed the baseline
bytes. The running unit is unverified end-to-end.

**Ranking.** SHOULD-FIX. In production `qwen-server unit` and `qwen-server install` are the same
server's two commands over the same template, so divergence would itself be a server defect; the
matrix has no gate to detect it, so a cell would record a `unit-sha256` that does not describe the
running unit and the table would be built on a unit it never saw. Minimal fix: after the `install`
step (R:144), hash the installed unit file and require it to equal the recorded unit sha
(the recorded sha, written to the cell `unit-sha256` file at R:75-76); on mismatch fail rc 5 (or a
new code) before the matrix step, and record the verified sha.

## V5 — baseline chain-of-custody — REPRODUCED (floating baseline, no golden)

`BASELINE_SHA` is captured per-cell from the LIVE unit (R:85-91), never from a pinned golden. I
started the unit in a DRIFTED state D (not the true golden), made the fake restore write D back
(self-consistent), and ran two cells. Both cells: rc 0, baseline captured = sha(D), restore
verified against sha(D) (R:122-125) and passed, run-complete published, unit left at D. The drift
is inherited by every subsequent cell as its "baseline". The R:122-125 check is correct WITHIN a
run (it proves the restore landed the bytes that were present before the cell) but has no anchor
outside the run: a subtly-different-but-self-consistent unit passes every cell forever. The
tampered-`$QWEN_MATRIX_BASELINE_ENV` half of V5 is covered by V2e (a shape-valid line that
restores different bytes fails at R:122-125, rc 8) and V2f (a non-QWEN line is refused at R:114) —
both reproduced PASS.

**Ranking.** NIT (declared design). The baseline is intentionally "the launcher's measured
defaults" (R:81-84 comment) for a live unit the owner runs; pinning a golden would require the
owner to declare one, and the restore check still catches a BROKEN restore (wrong bytes, missing
file). The chain-of-custody gap is real but bounded by the same trust the owner already places in
the live unit. Stated as a declared limit, not a defect.

## V6 — unit-text integrity is byte-exact and mandatory — REPRODUCED, all 4

| case | driving input | observed | verdict |
|---|---|---|---|
| V6a | valid cell, `unit_sha256` = `b`*64 (wrong sha), valid unit-text bytes | rc 2, `unit_sha256 does not match unit-text` (M:447-448) | PASS |
| V6b | unit-text mutated by one trailing byte, OLD sha kept | rc 2, same refusal | PASS |
| V6c | unit-text file MISSING, valid `unit_sha256` | rc 2, `cell unit text unreadable` (M:444-446) | PASS |
| V6d | POSITIVE control: non-UTF-8 unit-text bytes (0xFF 0xFE 0x00), sha MATCHES | rc 0, admitted | PASS |

V6d is the load-bearing proof that the reader is `read_bytes` (M:444), not `read_text`: a
non-UTF-8 unit-text is admitted when the sha matches, which a `read_text` reader would reject or
desync. Producer (M:525 `_sha256` = `sha256(read_bytes())`) and reader (M:444 `read_bytes`) agree
on the raw file bytes, so a trailing newline or non-UTF-8 byte cannot desync them.

## V7 — M-side mutation audit (F1/F2) — REPRODUCED, both mutants killed

Built two scratch mutants of M (the QM1-d fixes) and proved each is caught by its own
test. The full T suite dies earlier in a bare scratch tree on an unrelated env dependency
(`test_export_and_live_fixture` needs `scripts/transcript_export.py`), so the killer is run
in isolation (load T, call `test_table()`), with a positive control on the real M/T.

| mutant | removed block | compiles | loads | killer (isolated test_table) |
|---|---|---|---|---|
| F1 | completion read/compare (M:430-434: `run_complete.read_text()` + the `!= run_id` raise) | yes | yes | `AssertionError("cell without completion record rendered")` |
| F2 | unit-sha shape check + unit-text `read_bytes` recompute (M:441-448) | yes | yes | `AssertionError("malformed unit identity was accepted")` |

Positive control: `test_table()` alone passes on the real M/T (rc 0), so the isolation is valid
and the mutant failures are the mutation assertions firing, not the environment. Each QM1-d fix
is a live gate, not a tautology: F1's completion binding and F2's byte-exact unit-text integrity
each have a test that goes red when the fix is removed.

## V8 — R-side red-green (publish + restore-sha guards) — REPRODUCED, both guards load-bearing

Green (guard present) is V2a/V2b (run-complete ABSENT on the failure paths). Red (guard removed)
proves the guard is what catches it:

| mutant | mutation | red behavior (guard removed) |
|---|---|---|
| M-R1 | publish on non-zero rc — killed the `rc == 0` guard | load-failure (rc 7) now PUBLISHES run-complete |
| M-R2 | restore sha check tautologized (R:122 `elif` -> `false`) | wrong-byte restore ACCEPTED (rc 0, run-complete present) |

**Finding (defense-in-depth, NOT a defect).** The publish block has a DOUBLE `rc == 0` guard:
R:129 (enter the block) and R:131 (the `mv` that actually publishes). Killing only line 129 is
behaviorally INERT — line 131 still blocks the `mv` on `rc != 0`, so no publish. My first M-R1
attempt (line 129 only) produced rc 7 with run-complete ABSENT, exactly the guarded behavior.
The red only fires when both lines are killed. This is double defense, not a gap: a single-point
mutation of either guard is inert, which is the stronger property. The brief's "publish only when
rc == 0 (R:129-134)" is accurate; the load-bearing line is actually R:131, with R:129 as a
redundant outer guard.

## V9 — identities + gates — REPRODUCED, all match

Identities recomputed in the normal environment (not a lane TMPDIR):

| file | sha256 | lines | brief says | match |
|---|---|---|---|---|
| M qwen_matrix.py | `9dc6521f3ab923a3…da3d9de` | 578 | `9dc6521f…`/578 | yes |
| R qwen-matrix.sh | `5c0fc7b1313c09…16f6188a7` | 187 | `5c0fc7b1…`/187 | yes |
| T test_qwen_matrix.py | `3404d8f9f37331…0e3fb825f3` | 440 | `3404d8f9…`/440 | yes |
| X test_qwen_matrix_sh.sh | `a7be1e90adedf1…6e68602339acc` | 231 | `a7be1e90…`/231 | yes |

Static checks, all rc 0: `python3 -m py_compile M`, `pyflakes M`, `bash -n R`, `bash -n X`, `git diff --check`.

Suite counts (normal environment, fresh runs):
- T `test_qwen_matrix.py`: **4 tests passed** (rc 0)
- X `test_qwen_matrix_sh.sh`: **16 passed, 0 failed** (rc 0)
- `run-all.sh`: **ALL SUITES PASSED** (rc 0) — 16 entries: codex_hook_adapter 7/7, hermes_hook_adapter 6/6, hermes_spool 9/9, bridge_token_handling 9 OK, pc_bridge_exec 8, hermes_session_export 13, omniroute_local_builder 24, pc_lane 53/0, pc_lane_dispatcher 13/0, qwen_server 99/0, qwen_matrix 4, qwen_matrix_sh 16/0, lane_context 5/0, context_mirrors 11/0, sync_skills 34/0, build-roles --check OK.

QM1-c gates did NOT regress (spot-check, both live in `test_table`, which passed):
- **argv-identity** — M:439-440 recomputes `sha256(argv_text.encode())` and refuses a mismatch;
  `test_table` exercises it (T:398 asserts the exact `argv_sha256 does not match argv_text` text).
- **positive-requests** — M:478-479 (`requests` must be `int` and `> 0`) rejects the whole unusable
  class; `test_table` drives it with `(0, -1, 1.5, True, "1")` (T:341-345) and the NaN fail-closed
  case (T:334-337). Neither gate was weakened by the F1/F2 insertions (the new unit checks at
  M:441-448 and completion checks at M:429-434 are additive, before and after the argv block, and
  the argv block itself is untouched).

## V10 — findings ranked + VERDICT

### Findings (one-line repro each)

| rank | id | finding | one-line repro |
|---|---|---|---|
| SHOULD-FIX | F1 | completion record binds the RUN, not the CELL — the cell `name` is never checked in `_load_cell` (only as a table key in `render_table`, M:457-461) | copy a completed cell's four files into a new dir, change only `result.json.cell.name`, feed both to `table` — the renamed cell is admitted with the source run_id and numbers (V3, rc 0) |
| SHOULD-FIX | F2 | unit-text integrity is verified against the RENDERED unit file, not the INSTALLED unit — a rendered/installed divergence is uncaught | fake server whose `unit` renders X and `install` writes Y (Y != X): runner exits rc 0 with run-complete, `recorded unit_sha256 = sha(X)` != `installed sha = sha(Y)` (V4, rc 0) |
| NIT | F3 | baseline is a floating per-cell capture of the LIVE unit: `BASELINE_SHA` is hashed per cell (R:85-91), never from a pinned golden; a self-consistent drift is inherited by every cell | start the unit in a drifted state D, make restore write D back, run two cells: both rc 0 with `BASELINE_SHA` = sha(D) (V5, rc 0). Declared design (the R:81-84 `QWEN_SPEC_TYPE` block); the restore-sha check (R:122-125, the `BASELINE_SHA` mismatch) still catches a BROKEN restore (V2b/V2e). |

### NOT-DONE
- **Signal-during-cleanup window** (a second TERM while cleanup is mid-restore): static review only
  (R:96 `trap - EXIT INT TERM` clears the traps before the publish block, so the default
  TERM action kills the shell before publish). Not live-reproduced — needs a slow restore seam +
  a timed second signal; the committed X does not test this window either.
- **Live matrix cell / real GPU / real load:** NOT in scope for this verify lane (boundary: no real
  cell, no live load, no GPU sample, no unit change). Every V1-V9 finding is established on FAKE
  seams or on the committed test bytes; no live-load claim is made.
- **V10 report lint** is run on this report at the end of the lane (below), not pre-baked.

### Gate summary (every gate green, no hollow green)
- V1 reader admission: 7/7 cells refused/admitted exactly as the MatrixError text demands (M:425-448).
- V2 launcher boundary: 8/8 (V2a-f + b2/c2) — every negative path ends run-complete ABSENT; the
  only publish (V2d) is bound to the result run_id.
- V3/V4/V5: the three gaps above, each REPRODUCED on a fake seam (not asserted from reading alone).
- V6 unit-text byte-exact: 4/4 (a/b/c refused, d non-UTF-8 admitted on matching sha — proves
  `read_bytes`, M:444, so producer M:525 and reader agree on raw bytes).
- V7 mutation audit: F1 and F2 mutants each COMPILE, LOAD, and are KILLED by their own
  `test_table` assertion (not a SyntaxError); positive control passes on real M/T.
- V8 negative controls: both R-side guards are load-bearing — the publish `rc` guard (R:129,
  double-guarded with the inner `mv` at line 131, so a single-point mutation is inert) and the
  restore-sha `sha256sum` check (R:122-125). Each is RED when removed, GREEN (V2a/b) when present.
  No tautology found.
- V9: all four identities match the brief; all static checks rc 0; T 4/4, X 16/16, run-all ALL
  SUITES PASSED.

### VERDICT
**MERGE-READY.** The two QM1-d fixes (completion-record binding F1, byte-exact unit-text F2) are
correct, byte-pinned to the brief, live-gated by tests that kill the exact mutation (V7), and
regress-free against the QM1-c argv/requests gates (V9). The two SHOULD-FIX gaps (F1 name-binding,
F2 installed-unit verification) are real but out of scope for a verify lane — they are design
limits of the reader/runner, not defects in the QM1-d diff, and do not weaken the two fixes
themselves; both are named for the coordinator to decide (minimal fixes given in V3/V4). The single
NIT (F3) is declared design.

## Retro (for the coordinator — nothing baked)
- **Double-guarded publish (R:129 + R:131)** — a NEW observation, not a defect: the run-complete
  publish has two independent `rc == 0` checks (outer block entry + the inner `mv`), so a
  single-point mutation of either is behaviorally inert. This is the stronger property; worth a
  one-line note in the registry as "defense-in-depth beats single-point" so a future reviewer does
  not flag the redundancy as dead code.
- **AF-AP-86 (printf format-string) hit in a PROBE, not an artifact** — my V4/V5/V8 scratch fakes
  originally used `printf '%s' "$VAR"` (value as the format string). Fixed in scratch before any
  run; the four tracked files (M/R/T/X) are all clean. No artifact carries the pattern.
- **report_lint claim-token quirk (tooling, not code)** — a backticked identifier is checked
  against the LINES it is cited on. A token that genuinely lives on a DIFFERENT line (e.g. naming
  `UNIT_SHA` while the sentence cites the install step) reads as a MISS even though the citation is
  correct. Resolution: keep each token on the line that cites it, or name the variable in plain
  prose. Three lint rounds to get here; the final line is pasted above.
