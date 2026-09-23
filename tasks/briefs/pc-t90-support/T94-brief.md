# T94 — a failed lane session never becomes a report (AF-AP-67, sixth family; task #200) + a relaunched lane never inherits a dead loop's FAILED (AF-AP-140; task #167)

PIN: c6dcd61 (the origin head; the four boundary files are byte-identical there and at the local head; blob ids in the premise block;
re-measure them first).
LANE: t94 (sandbox; agent `code-implementer`, in the SHARED tree, no worktree isolation). Honey `ultra` Lever-2: your report is DATA:
files:lines, pasted counts, discrepancies, NOT-done. Do NOT spawn subagents.

WHY THIS LANE EXISTS. On 2026-09-23 at 15:33Z the PC verify lane VERIFY-T92-T90R3-PCJ1 wrote its 55,048-byte report into its lane
directory; then its final turn failed. Hermes printed `HTTP 400: [400]: No user query found in messages.` as its last output and wrote
`usage.json` with `"completed": false, "failed": true`. The runner (`harness-ports/bin/pc-lane.sh`) wrote that one line to `report.md`,
because its failure screen is a list of known texts (`CAPACITY_RX`, `QUOTA_RX`, `SAFETY_RX`, `PERSIST_RX`, `^API call failed`) and this
text matches none of them. The sandbox poller (`scripts/pc_lane.sh`) then printed `pc_lane: report ->` for a 50-byte error line. The
coordinator recovered the real report by hand. This is AF-AP-67's sixth family (`docs/INCIDENT-LOG.md`, the incident entry of
2026-09-23 15:3xZ), and the first one where the runtime had ALREADY said the session failed. Separately, AF-AP-140 (task #167): a
relaunched lane loop inherits the FAILED marker its dead predecessor wrote, and the poller reports `LANE FAILED` at once while the new
loop runs, because it tests FAILED before liveness (`scripts/pc_lane.sh:384`). Both are "the harvest reads the wrong verdict", in the
same two files.

REJECTED ALTERNATIVE (do not build it): add `^HTTP [0-9]{3}: ` to the text denylist. The seventh family would pass the same way; the
runtime's own verdict is the structural signal.

BOUNDARY (exact): MODIFY `harness-ports/bin/pc-lane.sh` (R, the PC-side runner), `scripts/pc_lane.sh` (D, the sandbox dispatcher and
poller), `harness-ports/tests/test_pc_lane.sh` (T1), `harness-ports/tests/test_pc_lane_dispatcher.sh` (T2); CREATE
`tasks/briefs/pc-t90-support/T94-report.md` (write it incrementally from the start). READ-ONLY: everything else. R and D are listed gate
files (`scripts/gate_files.txt`): the never-a-gate screen runs over them when the coordinator commits, so add no source or load of an
unlisted file.

## The contract

1. **Premise first.** Re-measure the premise block. On a boundary mismatch, stop CONTRACT-INVALID and report what differs.
2. **R — the runtime's verdict decides first.** After the attempt loop ends (the retry families keep their current behavior: the
   capacity and session-storage retries still happen, the safety family is still terminal), and before the refusal block (R:496): when
   the harness is Hermes and `$LANE_DIR/usage.json` parses and says `"failed": true` or `"completed": false`, the harness's last output is
   NOT a report, whatever its text. Keep it as evidence in `$LANE_DIR/report.failed-output.md` (never deleted). If the incremental draft
   is non-empty, promote it into `report.md` the way the existing empty-report path does (R:501-505), with a header that says the
   session FAILED and pastes the two flags and the first 200 bytes of the failed output. With no draft: write `FAILED` (the flags and the
   output as the reason), remove `report.md`, exit 70. A failed session is NOT retried by this rule (a deterministic failure retried is
   time and tokens for nothing); widening the retry families is out of scope. When `usage.json` is absent or does not parse, behavior is
   unchanged and ONE named warning line goes to stderr (never silent).
3. **D — defense in depth for runners that predate R's fix.** When the poller brings a report home and the usage metadata it already
   fetches (`USAGE_B64`, D:437) says the session failed, and the report is not a promoted draft (its first line is not the runner's `DRAFT REPORT` header):
   print a named `LANE FAILED` line that says `report.md` holds the session's last output, keep the fetched file under a name that is not
   `report-<lane>.md`, and exit 70.
4. **AF-AP-140 — a relaunched loop never inherits a dead loop's FAILED.** A `FAILED` marker is terminal only for the loop that wrote it.
   Decide where the fix lives (R at loop start, D in the probe order, or both) and state why in the report. A stale marker is kept
   (renamed, for example `FAILED.stale-<utc>`), never deleted. The failed-session and refusal paths above still end a live lane.
5. **Tests (T1, T2; normal, failure, boundary).** At least: (a) a fake Hermes that prints the 400 line and writes `usage.json` with
   `failed: true`, with a draft: `report.md` is the promoted draft with the failed-session header and `report.failed-output.md` holds the
   line; (b) the same without a draft: `FAILED`, no `report.md`, rc 70; (c) `failed: true` with a last output that LOOKS like a finished
   report (`## GATE RECOMMENDATION` … `MERGE-READY`): still not a report (the behavioral control for the flag, AF-AP-80); (d) the
   positive control: `failed: false, completed: true` leaves `report.md` byte-identical to the output; (e) `usage.json` absent, and
   `usage.json` not JSON: behavior unchanged plus the warning line; (f) the poller: a pre-fix runner's `report.md` with a failed
   `usage.json` gives the `LANE FAILED` line and rc 70; (g) AF-AP-140: a stale `FAILED` and a live new loop poll as RUNNING, and the stale
   marker survives under its new name. Every existing test stays green.
6. **Mutants (each on a scratch copy; never in the shared tree).** At least: m1 R's flag check removed; m2 R reads `failed` but not
   `completed`; m3 R deletes the failed output instead of keeping it; m4 R promotes the draft without the failed-session header; m5 D's
   defense removed; m6 the AF-AP-140 fix reverted. Each must red a named test for the stated reason; paste the table.
7. **Gates.** T1 and T2 twice each with identical counts (the baselines: `60 passed, 0 failed` and `pc_lane dispatcher: 39 passed,
   0 failed`); `bash -n` on R and D; `bash harness-ports/tests/run-all.sh` once, pasted. NOT in this lane: any PC run or bridge call
   (the tests use their fake harnesses and fake bridge).

Standing rules: touch ONLY the boundary files; report adjacent defects, never fix them. Never run git add, commit, stash, checkout,
restore, reset or clean. Other lanes are live in the tree (S198A on `scripts/transcript_export.py` and `tests/test_transcript_export.py`;
B12 on `proofs/S0-02/` and `tests/test_s0_02_buzz_authz.py`; a verifier writing `tasks/briefs/laya/VERIFY-J1-1-R2-report.md`): never touch
their files. Two PC lanes run from private copies of D and R; your edits do not reach them, and you never touch the PC. Take no
outward-facing action. Fake strings only. Paste every count and timestamp from command output. A deviation from any contract line is
STOP-and-report, never a self-accepted change.

## PREMISE — MEASURED at authoring (2026-09-23 15:5xZ, /home/user/agent-factory, worktree == origin c6dcd61 for all four files)
```
$ date -u +%Y-%m-%dT%H:%MZ; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
2026-09-23T15:55Z
c6dcd61
$ for f in <boundary>; do echo "$(git rev-parse origin/...:$f | cut -c1-12) $(wc -l < $f) $f"; done   (worktree == origin for all four)
183f337eff91 529 harness-ports/bin/pc-lane.sh
6d6024139163 609 scripts/pc_lane.sh
67ed1e0c3c56 641 harness-ports/tests/test_pc_lane.sh
948c19ac580c 452 harness-ports/tests/test_pc_lane_dispatcher.sh
$ grep -n 'SAFETY_RX=\|PERSIST_RX=\|CAPACITY_RX=\|QUOTA_RX=\|--usage-file\|^if grep -Eq "$CAPACITY_RX|$QUOTA_RX\|DRAFT REPORT\|^if \[ "$HARNESS" = "hermes" \] && \[ -s' harness-ports/bin/pc-lane.sh
269:CAPACITY_RX='^API call failed after [0-9]+ retries: '
270:QUOTA_RX='exhausted their quota'
304:SAFETY_RX="^(⚠️[[:space:]]*)?The model provider's safety filter blocked"
305:PERSIST_RX='^(⚠️ )?No reply: '
450:      --usage-file "$LANE_DIR/usage.json" > "$REPORT" 2> "$LOG" &
496:if grep -Eq "$CAPACITY_RX|$QUOTA_RX|$PERSIST_RX|^API call failed" "$REPORT" 2>/dev/null; then
503:  { echo "DRAFT REPORT — the lane ended (harness rc=$rc) before writing its final report; this is the incremental draft it kept. Grade it as PAR
509:if [ "$HARNESS" = "hermes" ] && [ -s "$LANE_DIR/usage.json" ]; then
$ grep -n 'probe="$(bridge "test -f\|\*FAILED-UNRETRIED\*)\|    \*FAILED\*)\|\*READY\*)\|report -> ' scripts/pc_lane.sh
384:  probe="$(bridge "test -f $PC_AF_REPO/.lanes/$LANE_ID/FAILED && echo FAILED || (test -s $REMOTE_REPORT && grep -Eq '^API call failed|^(⚠️ )?N
386:    *FAILED-UNRETRIED*) echo "pc_lane: LANE FAILED — the harness died on an API failure the PC side did not retry (the line stands as report.md;
390:    *FAILED*)
413:    *READY*)   done_flag=1; break;;
433:  echo "pc_lane: report -> $LOCAL_REPORT" >&2
$ bash harness-ports/tests/test_pc_lane.sh | tail -1; bash harness-ports/tests/test_pc_lane_dispatcher.sh | tail -1
60 passed, 0 failed
pc_lane dispatcher: 39 passed, 0 failed
$ grep -c 'pc-lane.sh\|pc_lane.sh' scripts/gate_files.txt
2
$ bash scripts/pc.sh 'grep -E "completed|failed|api_calls" /home/rocco/agent-factory/.lanes/pc-verify-t92-t90r3-pcj1.md--433d15e/usage.json'   (15:5xZ)
  "api_calls": 153,
  "completed": false,
  "failed": true,
$ od -c <scratchpad>/evidence/report-pc-verify-t92-t90r3-pcj1.md--433d15e.md | head -3   (the harvested 50-byte report, 15:3xZ)
0000000   H   T   T   P       4   0   0   :       [   4   0   0   ]   :
0000020       N   o       u   s   e   r       q   u   e   r   y       f
0000040   o   u   n   d       i   n       m   e   s   s   a   g   e   s
```
