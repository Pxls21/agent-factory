# PC lane — T90 (the dispatcher's PREMISE gate: a first launch refuses a brief with no MEASURED premise block; a resume is exempt)

PIN: c2a0df2

Role: code-implementer. Route: the LOCAL build route (`agentfactory-build-local`, the vLLM server default effort). Venue:
`tasks/briefs/pc/VENUE-MAP.md` — read it first. Honey mode: ultra Lever-2 (the report is DATA: files:lines, verbatim counts, NOT-done).

## WHY (task #90)
Three lane briefs in one window (2026-09-22) carried premises the coordinator wrote from memory — K1-c stopped CONTRACT-INVALID on
one, B7's item-1 exit-3 premise was read not run, VERIFY-A5q's "names only T" was stale — each cost a lane round or a live stop
(`docs/INCIDENT-LOG.md`, the three 2026-09-22 entries). The two newest briefs (`pc-verify-b67.md`, `pc-verify-gov2c.md`) carry a
`## PREMISE — MEASURED at authoring (...)` heading followed by a fenced block that pastes every premise command with its output. This
lane makes that block MECHANICALLY REQUIRED at first launch, in the sandbox dispatcher `scripts/pc_lane.sh`, BEFORE the brief ships
to the PC (the guard runs before the write, AF-AP-79). A resume/re-attach of a lane that is already launched is exempt — a re-attach
never re-measures, and every lane launched before this gate (e.g. `pc-k1-d.md`, `pc-verify-s4h.md`, which carry no block) must stay
re-attachable. There is NO environment escape hatch: a legacy brief on a FIRST launch is amended, not waved through.

## PREMISE — MEASURED at authoring (2026-09-22 06:2xZ, the sandbox clone at c2a0df2); re-measure as item 1
```
sha256 (first 16) at c2a0df2: scripts/pc_lane.sh d5b895574e357727 (368 lines; last change ea32017 2026-09-17)
                               harness-ports/tests/test_pc_lane_dispatcher.sh 84f89b515fd3dec4 (74 lines; last change 650b33b 2026-09-15)
                               harness-ports/tests/run-all.sh d12c3e49e4f859ca
scripts/pc_lane.sh seams: die() :47 (rc 64) · BRIEF/HARNESS/ROLE :102 · brief-exists check :104 · PIN grep :113-115 · LANE_ID :116 ·
  PC_LANE_BRIDGE_FN test hook :125 · bridge() :126-133 (python3 "$ROOT/scripts/pc_bridge_exec.py") · the lane= echo :135 ·
  "# --- 1. ship the brief" header :138 (the effort seam, testable without the PC: server_effort_for_role :140-148, the
  LANE_PRINT_EFFORT early exit :150) · "# --- 0. headroom admission check" :152-171 (the FIRST bridge I/O: free -m/df) ·
  "# --- 1. ship the brief" :172-178 (mkdir -p $PC_AF_REPO/.lanes/$LANE_ID + the brief written on the PC)
harness-ports/tests/test_pc_lane_dispatcher.sh: 74 lines; check() :10; run() :11-15 + the nine effort-seam checks :16-24; the fake bridge
  function via PC_LANE_BRIDGE_FN :26-50 (bridge() :28-49, a case on the command text; `*'mkdir -p '*'.lanes/'*` → shipped; `*'test -f '*'/FAILED'*` → GONE);
  run_dispatch() :51-56 (MAX_POLLS=0, OUT_DIR, PC_AF_REPO=/fake); 4 dispatch checks :58-72. Its fixture brief is
  `printf 'PIN: 0000000\nbrief\n'` (:8) — NO premise block.
2026-09-22T06:27:39Z  bash harness-ports/tests/test_pc_lane_dispatcher.sh → [PASS] 13, [FAIL] 0
grep -c -i '^#\+ .*PREMISE.*MEASURED' : pc-verify-b67.md 1 · pc-verify-gov2c.md 1 · pc-k1-d.md 0 · pc-verify-s4h.md 0
harness-ports/tests/run-all.sh runs test_pc_lane.sh (:21-24), test_pc_lane_dispatcher.sh (:26-29), test_pc_lane_admission.sh (:31-34).
```

## THE CONTRACT
1. **Grammar of a measured premise block** (exactly this; document it in the dispatcher's header comment): a heading line matching
   `^#{1,6} .*PREMISE.*MEASURED` (case-insensitive), followed anywhere later in the file by a fenced block (a line that is exactly
   three backticks opens it, the next such line closes it) containing at least TWO non-empty lines. Nothing else is inspected — the
   gate proves the block EXISTS and is not empty; the coordinator's discipline supplies the content.
2. **Position:** after the `LANE_PRINT_EFFORT` early exit (:150) and BEFORE the headroom block (:152) — so the nine effort-seam unit
   checks stay byte-for-byte untouched, and no bridge write happens before the gate. Add its own header `# --- 0a. premise gate ---`.
3. **The resume exemption, measured on the PC, not assumed:** ONE bridge probe
   `bridge "test -f $PC_AF_REPO/.lanes/$LANE_ID/lane.pid && echo RESUME || echo FIRST"`; `RESUME` → the gate is skipped with the
   stderr note `pc_lane: premise gate skipped — a resume of $LANE_ID`; anything else (`FIRST`, empty, a bridge error) → the gate
   applies (fail closed: an unreachable bridge never exempts).
4. **The refusal:** `die` (rc 64) with EXACTLY this text on one line:
   `brief has no MEASURED premise block — add '## PREMISE — MEASURED at authoring (<date>, <clone>@<pin>)' + a fenced block pasting each premise command with its output (2026-09-22: three stale premises in one window); a resume of an already-launched lane is exempt`
   and NO `mkdir -p` bridge call before it (the ship never happens).
5. **No escape hatch.** No env var, no flag. (Rejected: `PC_LANE_SKIP_PREMISE=1` — the next stale premise would ride it.)
6. **Tests** (in `harness-ports/tests/test_pc_lane_dispatcher.sh`, the existing fake-bridge harness; extend its `bridge()` case with
   `*'lane.pid && echo RESUME'*) echo "${PC_LANE_TEST_RESUME:-FIRST}";;` and add a second fixture brief WITH a block):
   (a) a brief with NO block on a FIRST launch → rc 64, stderr contains `no MEASURED premise block`, and `BRIDGE_CALLS` has NO
   `mkdir -p` line (AF-AP-79 — the guard before the write); (b) the SAME brief with `PC_LANE_TEST_RESUME=RESUME` → the gate is skipped
   (the note in stderr) and the ship call IS recorded; (c) a brief with the heading but an EMPTY fenced block (or a block of one
   line) → rc 64; (d) a brief with the heading + a two-line block → proceeds to the ship (the existing dispatch checks then run on
   THIS fixture); (e) the heading matches case-insensitively and at `###` depth; (f) the effort-seam checks (`run …`, 9) are
   unchanged. Update the existing fixture (:8) to the WITH-block form so the four existing dispatch checks keep their meaning;
   keep the no-block brief for (a)/(b)/(c). Every new check has a NEGATIVE control on a mutated copy of the dispatcher (the gate
   deleted → (a) goes green-for-the-wrong-reason: show it red on the mutant).
7. **Nothing else changes:** not `harness-ports/bin/pc-lane.sh` (the PC side), not the poll/harvest sections, not CLAUDE.md /
   AGENTS.md / .hermes.md (the mirror gate is the coordinator's), not the four briefs named above. The coordinator bakes the rule into
   the orchestration skill at harvest.

## ITEMS
1. PREMISE (first; stop on failure): re-run the identity/grep/test commands above on your worktree and paste them; a different
   dispatcher line map or a different check count → CONTRACT-INVALID, stop.
2. Implement the gate per THE CONTRACT (~30 lines of bash: a function `_premise_block_ok <brief>` returning 0/1, then the probe and
   the die). `bash -n scripts/pc_lane.sh` clean; `shellcheck` if installed (advisory).
3. Tests per item 6; run `bash harness-ports/tests/test_pc_lane_dispatcher.sh` ×2 (paste `[PASS]`/`[FAIL]` counts with `date -u`),
   then `bash harness-ports/tests/run-all.sh` once (paste the last line — `ALL SUITES PASSED` or the failing suite's tail).
4. The mutant: on a scratch copy, delete the gate → (a) must fail (paste its FAIL line); restore, re-run, paste.
5. Report `tasks/briefs/pc-t90-support/T90-report.md` (create the directory): the identity table, the gate's file:line span, the
   test names with counts pasted, the mutant line, NOT-done, `report_lint.py` summary with `--map D=scripts/pc_lane.sh
   --map T=harness-ports/tests/test_pc_lane_dispatcher.sh --rev c2a0df2` — at most three fix rounds (AF-AP-76).

## VENUE NOTES (this host)
- Everything runs locally on this host with bash; no bridge, no server, no other lane's tree; the other lanes (VERIFY-S4H, K1-d,
  VERIFY-B67, VERIFY-GOV2c) and the vLLM `qwen` container are never touched; never `pkill`/`killall` by name.
- The dispatcher self-copies at start (:41-44, `PC_LANE_SELF_COPY`) — the tests pass `env -u PC_LANE_SELF_COPY`; keep that contract.
- A count is PASTED from the run beside `date -u`, never typed; every file:line by `sed -n` on the PIN.

**Authorization:** the owner's own dispatcher and its own test harness; nothing leaves this host.
