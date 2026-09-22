# T90 report — the dispatcher's MEASURED-premise gate

**DONE (proposal pending the adversarial-verifier lane).** The T90 premise gate is
implemented in the sandbox dispatcher `scripts/pc_lane.sh` and its test
`harness-ports/tests/test_pc_lane_dispatcher.sh`. A FIRST launch of a lane is refused
(rc 64) when its brief carries no MEASURED premise block; a resume of an already-launched
lane is exempt. Self-validated here: the dispatcher test 19 passed / 0 failed
(deterministic over 3 runs), `run-all.sh` -> `ALL SUITES PASSED`, and the gate-deleted
mutant turns 5 checks red (14 passed / 5 failed) — the gate is load-bearing, not a
tautology. No gate verdict is issued; this is a proposal for the verify lane to grade.

## Item 1 — identity at c2a0df2 (re-measured this session; brief premises reproduced)

| file (at c2a0df2) | sha256 (first 16) | lines | last change | brief said | match |
|---|---|---|---|---|---|
| scripts/pc_lane.sh | d5b895574e357727 | 368 | ea32017 2026-09-17 | same | OK |
| harness-ports/tests/test_pc_lane_dispatcher.sh | 84f89b515fd3dec4 | 74 | 650b33b 2026-09-15 | same | OK |
| harness-ports/tests/run-all.sh | d12c3e49e4f859ca | — | — | same | OK |

Re-measured (paste):
- `sha256sum scripts/pc_lane.sh harness-ports/tests/test_pc_lane_dispatcher.sh harness-ports/tests/run-all.sh | awk '{print substr($1,1,16), $2}'`
  -> `d5b895574e357727 scripts/pc_lane.sh` / `84f89b515fd3dec4 ...test_pc_lane_dispatcher.sh` / `d12c3e49e4f859ca ...run-all.sh`
- `wc -l scripts/pc_lane.sh harness-ports/tests/test_pc_lane_dispatcher.sh` -> `368` / `74`
- `git -C tree log -1 --format=%h -- <file>` -> `ea32017` (dispatcher) / `650b33b` (test)
- fresh c2a0df2 copy of the dispatcher test -> `pc_lane dispatcher: 13 passed, 0 failed`, rc 0 (the pre-change baseline)

**DISCREPANCY (item 1, measured).** The brief's line-number annotations for the
dispatcher's middle band are off by one from the actual bytes; the 172+ region matches.
The decisive evidence is the sha256: the file is byte-identical to what the brief claims
(`d5b895574e357727`), so the drift is hand-typed annotation, not a changed file — the
`bridge()` function (D:128) and the `LANE_PRINT_EFFORT` early-exit (D:149) are where the
bytes actually are. The contract's insertion point is anchored to two stable code
anchors (after the `LANE_PRINT_EFFORT` early-exit, before the headroom block), so the
design is satisfied on the measured truth. Built on the measured map, not the drifted
annotation.

## Item 2 — the gate (new lines, stated in words; the c2a0df2-stable anchors they sit between are pinned)

The gate is a NEW block (31 lines) inserted in the worktree between the
`LANE_PRINT_EFFORT` early-exit (D:149, unchanged) and the `headroom` block header
(D:151, unchanged). Because these are new lines they have no c2a0df2 revision, so their
span is stated in words rather than pinned; the two stable anchors they sit between are
the pinned refs above. Structure, top to bottom:

- header comment `# --- 0a. premise gate ---` (conformed this session; attempt 1 had
  decorated it with `(T90, 2026-09-22)` + dash-fill, which the contract item 2 does not
  specify).
- `_premise_block_ok <brief-file>` -> 0/1: an awk state machine. `s==0` matches the
  heading `^#{1,6} .*premise.*measured` (case-insensitive via `tolower`); `s==1` waits
  for the opening fence (a line that is exactly three backticks); `s==2` counts
  non-empty lines until the closing fence; returns 0 only if that count is >= 2.
- the resume probe, one bridge call: `test -f $PC_AF_REPO/.lanes/$LANE_ID/lane.pid &&
  echo RESUME || echo FIRST`, wrapped in `2>/dev/null || true`. It calls the same
  `bridge()` seam (D:128) the rest of the script uses. Fail closed: a bridge error yields
  empty, which is not `RESUME`, so the gate applies.
- if the probe answered `RESUME`: stderr note `pc_lane: premise gate skipped — a resume
  of <lane-id>`, gate skipped.
- else, if the brief has no measured block: `die` with the exact one-line text from
  contract item 4 (verified byte-for-byte), rc 64.
- No environment escape hatch (scanned the new block, none). No `mkdir -p` bridge call
  precedes the die (the ship block is after the gate) — AF-AP-79, the guard before the
  write.

## Item 3 — tests (new/changed lines stated in words; the stable seam and unchanged checks pinned)

In the worktree test file the fixture (the `brief.md` printf, `T:8` at c2a0df2, the
no-block form) is updated to the WITH-block form (`### premise — measured at authoring
(2026-09-22, c2a0df2)` + a two-line fence), and four new fixture briefs are added right
after it (no-block, empty-fence, one-line-fence, heading-missing-`measured`). The
- the fake-bridge `bridge()` function (T:28, the test-only `case`) gains the arm
  `*'lane.pid && echo RESUME'*) echo "${PC_LANE_TEST_RESUME:-FIRST}"`.
runner is added that takes a brief path plus env overrides and captures the exit code as
`GATE_RC`. Six new checks are appended at the end of the file, each with a negative
control proven on the mutant (item 4). The 9 effort-seam checks (T:16–T:24 at c2a0df2,
the unchanged `run <expected> ... -- <role>` lines) are byte-identical and all still pass
(item 6f); the 4 pre-existing dispatch checks now run on the updated with-block fixture
and still pass.

| new check (stated in words; appended to the test file) | contract item | asserts |
|---|---|---|
| no-block brief on a FIRST launch (probe answers FIRST) | (a) | rc 64 / stderr has `no MEASURED premise block` / the `mkdir -p` ship call is NOT recorded |
| the same no-block brief on a RESUME (PC_LANE_TEST_RESUME=RESUME) | (b) | rc 75 / stderr has `premise gate skipped — a resume of` / the `mkdir -p` ship call IS recorded |
| heading + an EMPTY fenced block | (c) | rc 64 / `no MEASURED premise block` / no `mkdir -p` |
| heading + a ONE-line fenced block | (c) | rc 64 / `no MEASURED premise block` / no `mkdir -p` |
| a `###`-depth lowercase heading + a two-line block | (d)+(e) | rc 75 / `server effort applied` / `mkdir -p` recorded |
| a heading with `premise` but no `measured`, even with a two-line fence | (e) | rc 64 / `no MEASURED premise block` / no `mkdir -p` |

Verbatim counts (each with `date -u`):
- `bash harness-ports/tests/test_pc_lane_dispatcher.sh` -> **19 passed, 0 failed**, rc 0.
  Run 1 `Tue Sep 22 08:38:38 AM UTC 2026`; runs 2 and 3 (determinism) -> 19/0 both,
  `08:38:57` / `08:41:52`.
- `bash harness-ports/tests/run-all.sh` (one foreground call) -> final line **`ALL SUITES
  PASSED`**, rc 0, `Tue Sep 22 08:43:10 AM UTC 2026`. Includes `test_pc_lane.sh` 53/0,
  `test_pc_lane_dispatcher.sh` 19/0, `test_pc_lane_admission.sh` 22/0, `test_qwen_server.sh`
  101/0.

## Item 4 — the mutant (gate deleted)

Scratch copy of the dispatcher with the new gate block deleted; `bash -n` clean; the test
run against that copy (the test resolves the dispatcher by its `scripts/pc_lane.sh`
path, so a self-contained run dir holds the mutant at that path). Result: **`pc_lane
dispatcher: 14 passed, 5 failed`**, rc 1 (`Tue Sep 22 08:41:38`). The 5 FAIL lines:
no-block-on-FIRST / no-block-on-RESUME / empty-fence / one-line-fence / heading-missing-
measured. With the gate gone, a no-block FIRST brief falls through the headroom check
(fail-open, admits) -> the `mkdir -p` ship -> launch (rc 75), so the (a) check is
green-for-the-wrong-reason on the mutant and correctly red. The 9 effort checks, the 4
dispatch checks, and the one positive (d) check still pass on the mutant, which is what
proves the 5 red checks depend on the gate and not on anything else. Worktree restored
(gate present); re-run -> 19/0, rc 0.

## Item 5 — this report + report_lint

Location: `tasks/briefs/pc-t90-support/T90-report.md` (directory created this session).
The c2a0df2-stable references are pinned to `D:`/`T:` lines that exist at the PIN with
their literal identifier backticked; the new-only content is stated in words (no bare
`D:NN`/`T:NN` for a line that has no c2a0df2 revision). The `report_lint.py` summary
with the brief's flags is pasted in DISCREPANCIES.

## Self-attack (three most likely ways this is wrong, each ruled out)

1. **The gate is a tautology (hollow green) that passes without inspecting the brief.**
   Ruled out by the mutant (item 4): deleting the gate turns 5 checks red, including (a)
   which requires the exact refusal (rc 64 + `no MEASURED premise block` + no
   `mkdir -p`). A tautology would stay green.
2. **The awk grammar accepts a block the contract rejects (or rejects a valid one).**
   Ruled out by the fixture matrix: the empty-fence and one-line-fence fixtures and the
   missing-`measured` heading are all refused; the `###` lowercase two-line block is
   accepted. The heading regex is exactly `^#{1,6} .*premise.*measured` (case-insensitive)
   per contract item 1.
3. **The resume exemption is too loose (a non-resume is exempted) or too tight (a real
   resume is refused).** Ruled out by the probe's fail-closed design: only the exact
   string `RESUME` (from the on-PC `test -f .../lane.pid`) exempts; `FIRST`, empty, or a
   bridge error all apply the gate. The (b) check proves a RESUME is skipped and shipped;
   (a) proves a FIRST (probe absent) is refused.

## DISCREPANCIES

- **Item 1 line-number drift** (see Item 1): the brief's middle-band annotations are off
  by one from the byte-identical file; sha256 proves the file is unchanged. Built on the
  measured map.
- **Header decoration** (item 2): attempt 1's gate header carried `(T90, 2026-09-22)` +
  dash-fill; conformed to the contract's exact `# --- 0a. premise gate ---` this session
  (single-line, no behavior change, re-verified 19/0).
- **report_lint** (bounded to 3 rounds per AF-AP-76). Round 1: 19 MISS / 13 UNCHECKABLE
  (root cause: cited worktree line numbers as `D:NN`/`T:NN`, which map to the c2a0df2
  revision where the new lines don't exist; plus claim tokens on prose lines). Round 2:
  corrected the new-only content to words, pinned c2a0df2-stable refs with their literal
  identifier backticked -> 1 MISS / 3 UNCHECKABLE (one test-file ref was aliased to the
  dispatcher). Round 3: that ref corrected -> **`report_lint: 9 refs — OK 6, NEAR 0, MISS 0,
  UNCHECKABLE 3, UNRESOLVED 0 (at c2a0df2)`, rc 0.** The 3 UNCHECKABLE rows are prose lines
  carrying an alias with no claim token (the two stable anchors in Item 2 and the 9-seam
  line in Item 3); the hints are "add a token if the line is right, else correct the
  number" — they are correct lines stated in a summary sentence, so they are reported, not
  chased.

## NOT done

- No gate verdict (this is a build lane; the `adversarial-verifier` lane grades it).
- `harness-ports/bin/pc-lane.sh` (the PC side), the poll/harvest sections, and the four
  briefs named in the contract are untouched — per item 7. The mirror rule (CLAUDE.md /
  AGENTS.md / .hermes.md) is the coordinator's at harvest, not this lane's.
