# VERIFY-T94 — the targeted independent adversarial verify of T94: a failed lane session never becomes a report (task #200), a relaunched lane never inherits a dead loop's FAILED (task #167), and the coordinator's amendment to the poll probe (AF-AP-162)

PIN: 4a38190 (the origin head: "transcripts: scrubbed sandbox chat digests"; the T94 landing itself is 1a94bbb, and R, D, T1 and T2 are
byte-identical there and at the PIN — premise below). Confirm with `git log --format='%h %s' -3 4a38190`.
LANE: pc-verify-t94
ROLE: adversarial-verifier. Route: the CLOUD verify route (`HERMES_MODEL=agentfactory-verify`, reasoning xhigh; OmniRoute's priority chain
starts at codex/gpt-5.6-terra-xhigh, a different model from T94's builder, codex/gpt-5.6-sol-ultra). Claim nothing about which model
wrote which turn; the harvest measures the provider mix. Venue: `tasks/briefs/pc/VENUE-MAP.md`, read it FIRST. Honey full: line-bounded
findings, evidence anchors, SOLID/UNSURE per observation.

The contract-gate predicate (D-031): a finding BLOCKS only if it is contract-mapped (the contract below), reproduced through the real code
(R run with a fake Hermes the way `harness-ports/tests/test_pc_lane.sh` runs it; D run with a fake bridge function the way
`harness-ports/tests/test_pc_lane_dispatcher.sh` runs it; the poll probe executed by `bash`), materially effective (a failed session's
last output harvested as a report; a live lane read as FAILED, READY or GONE; a finished lane never harvested; this dispatch's own FAILED
ignored; a relaunched lane ended by a dead loop's FAILED; evidence deleted), with a concrete discriminator (the input state, the expected
and the observed outcome), and inside the boundary (R, D, T1, T2 below). Everything else is a follow-up. Emit ONE GATE RECOMMENDATION:
`MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`; the coordinator owns the gate.

AUTHORIZATION: defensive review of the owner's own lane dispatcher and runner. Every token, key or report text you write is a FAKE string.

WHY THIS LANE EXISTS: T94 was built by a PC cloud build lane (all its gates green). The coordinator's pre-commit read found a BLOCKER in
the lane's rewrite of the poll probe (a doubled escape that ran the PC lookups in the sandbox, and an inverted FAILED predicate; T2 was
green because its fake bridge never ran the probe) and repaired it at the landing, with six tests that now execute the probe. Rule 0f:
neither the builder's gates nor the coordinator's re-run is independent verification, and the amendment is coordinator code nobody else
has read. Your job is NEW shapes, never the builder's or the coordinator's own cases.

COMPONENT (the boundary): `harness-ports/bin/pc-lane.sh` (R: the stale-FAILED rename block after the state guard; the runtime-verdict
block `usage_verdict` before the refusal screen), `scripts/pc_lane.sh` (D: the poll probe `probe="$(bridge …)"`; the harvest defense
`USAGE_VERDICT`), `harness-ports/tests/test_pc_lane.sh` (T1), `harness-ports/tests/test_pc_lane_dispatcher.sh` (T2, including the
executed-probe bridge `EXEC_BRIDGE_FN` and its six `EXECUTED probe:` tests).
CONTRACT (frozen): `tasks/briefs/pc-t90-support/T94-brief.md` items 2-6, plus the COORDINATOR AMENDMENT in the landing commit body
(`git log --format=%B -1 1a94bbb`): the poll probe is the pre-T94 line except its FAILED predicate `test -f F && test ! F -ot B && echo
FAILED`, and the lane's brief-mtime binding is kept. INPUTS TO ATTACK, not truths: the lane's report `tasks/briefs/pc-t90-support/T94-report.md`
(its sections 1-8, the mutant table m1-m6), the landing commit body (the mutants Ma-Me), `docs/INCIDENT-LOG.md`'s 2026-09-23 18:4xZ entry.
KNOWN, never blocking here: K1 issue #54 (the server-effort probe and the premise probe are not executed against a disjoint fake root;
the AP_SCREEN signature for a doubled escape); K2 T1's quota-window check message carries a backticked phrase inside double quotes
(`harness-ports/tests/test_pc_lane.sh:292`, since 5a19c7f), so every T1 run executes `reset after 5m` as a command and prints the
reset(1) usage text on stderr — pre-existing, report only if it changes a verdict.

## Items (report EVERY observation; no severity filter; SOLID/UNSURE per observation)

1. PREMISE. Re-measure the block below in your worktree (blob ids, line map, the two counts). A mismatch is CONTRACT-INVALID for the
   affected items; say which.
2. R — THE RUNTIME'S VERDICT, NEW SHAPES (never T1's cases (a)-(e)). Run R with a fake Hermes that writes the `usage.json` you choose. At
   least: `"failed": "true"` (a string), `1`, `null`, `"completed": 0`; both flags absent with other keys present; a JSON array; a JSON
   scalar; a UTF-8 BOM; trailing garbage after the object; an unreadable file (mode 000); a directory named `usage.json`. For the failed
   output: NUL bytes, invalid UTF-8, CRLF line ends, a first line that is itself `DRAFT REPORT — the Hermes session FAILED …` (a forged
   header), an `API call failed …` line placed after byte 200. For the draft: whitespace-only, and a draft that is a symlink. For each:
   the outcome (report.md content, FAILED, rc) and whether it matches the contract. Then: does `report.failed-output.md` survive every
   later step of R (the transcript export, the patch build, the exit trap)? And what happens to a `report.failed-output.md` left by an
   EARLIER loop of the same lane (R copies with `cp -f`): is earlier evidence lost, and does the contract ("never deleted") cover it?
3. R — STALENESS AND THE RETRY FAMILIES. QUESTIONS (measure; do not assume): R never removes `$LANE_DIR/usage.json` at an attempt's
   start (`grep -n usage.json harness-ports/bin/pc-lane.sh`). If an attempt's Hermes dies before it writes `usage.json`, does R read the
   PREVIOUS attempt's or the previous loop's file? Build both directions with a fake Hermes: a stale `failed: true` beside a fresh good
   report, and a stale `completed: true` beside a fresh failed output. Does the harvest side (D reads `usage.json` too) have the same
   exposure? Then the families: a failed session whose last output also matches `CAPACITY_RX`, `QUOTA_RX` or `PERSIST_RX` (the retries
   still run first? which verdict wins at the end?); the safety family (still terminal before the new block?).
4. R — THE STALE-FAILED RENAME. With T1's fake-repo pattern (never a real lane directory): FAILED as a directory, a symlink (to a file
   outside the lane directory, and dangling), a FIFO, an unreadable file; `FAILED.stale-<ts>` already present (the `.$$` suffix); the
   `mv` failing (a read-only lane directory: R must die with its named message and run nothing); confirm by a real run that a replayed
   launch while the lane loop is alive exits at the state guard BEFORE the rename (build a live loop holding the pidfile, with a FAILED
   it has just written, then replay the launch).
5. D — THE HARVEST DEFENSE. With T2's fake bridge: `usage.json` absent, corrupt base64, a JSON array, a string, `failed: "true"`; the
   report's first line an exact, a truncated and a Unicode-lookalike `DRAFT REPORT — the Hermes session FAILED` header. Which of these
   are fail-open (the failed output harvested as `report-<lane>.md`)? Is anything the harvest normally does after the report fetch (the
   usage line, the provider mix, the patch fetch, the transcript) skipped by the early exit 70 that the coordinator needs for a failed
   lane (for example the lane patch with the partial work)?
6. THE COORDINATOR AMENDMENT (the poll probe). Execute the probe (render it with an echoing bridge, then run it with `bash` against a fake
   lane directory under `../scratch/fakelanes/`, NEVER the clone's `.lanes/`). New states, at least: FAILED and brief.md with EQUAL
   mtimes (`touch -r`); FAILED newer than the brief by less than one second; brief.md missing (the ship failed: does the predicate fail
   closed or open?); FAILED a directory; `lane.pid` empty, holding garbage, or holding the pid of a live process that is not the lane;
   `report.md` present but zero bytes with a live loop (the live VERIFY-K1-h state at 18:52Z) and with the loop gone; a report whose first
   line is `API call failed …` with the loop alive and with it gone; a launch.log exactly five minutes old. Then attack the HARNESS: can
   you write a probe mutant that expands a lookup in the sandbox (or inverts a branch) and still passes all six `EXECUTED probe:` tests?
   A surviving mutant is a finding against the tests (name the missing state).
7. MUTANTS (each on a scratch copy under `../scratch/mut/`, never in your tree). Re-run the lane's m1-m6 (T94-report.md section 6) and
   the coordinator's Ma-Me (the landing commit body) on the final bytes, and add at least four of your own, for example: the rename moved
   BEFORE the state guard; D's header check shortened to `DRAFT REPORT`; R reading only `failed`; the probe's FAILED-UNRETRIED branch
   escaped twice; `cp -f` of the failed output replaced by `mv`. Each must red a named test for the stated reason (paste the killer line);
   a survivor is a finding (name the missing test).
8. THE SIBLING SWEEP. Confirm or extend issue #54's list by static reading: every bridge string in `scripts/pc_lane.sh` that carries a
   remote-side expansion (a `\$` inside `bridge "…"`), and for each, whether any test runs it; every other place in `scripts/` or
   `harness-ports/bin/` that builds a shell program as a string for another shell (`bash -c`, `ssh`, `podman exec`, `systemd-run`, a
   heredoc shipped over the bridge); any doubled escape (`\\$(`, `\\\"`) inside a double-quoted argument anywhere in those trees.
9. THIS HOST'S SHELL. T2's executed-probe tests use whichever `bash` runs them: run T2 here and paste the six `EXECUTED probe:` lines
   (the PC's bash is the second instrument; the coordinator's run was in the sandbox). Paste `bash --version | head -1`.
10. GATES (each under the 420 s cap). `bash -n harness-ports/bin/pc-lane.sh`, `bash -n scripts/pc_lane.sh`; T1 twice and T2 twice with
   identical counts (`67 passed, 0 failed`, `pc_lane dispatcher: 48 passed, 0 failed`); `bash harness-ports/tests/run-all.sh` once
   (paste its summary lines; a failure that happens only on this host is reported with its first failing line, for example the
   qwen-matrix SECOND_SIGINT line the builder saw here).

RUNNING THE CODE ON THIS HOST (read twice). T2 runs `scripts/pc_lane.sh` with a fake bridge function (`PC_LANE_BRIDGE_FN`) and fake
`PC_BRIDGE_URL`/`PC_BRIDGE_TOKEN` values: that is the only way you run D. You run R only through T1's harness or your own scratch copies
with a fake Hermes and a fake repository root under `../scratch/`. Never run either script against the clone `/home/rocco/agent-factory`
or any real lane id: R renames and writes files in its lane directory, and five real lanes live under the clone's `.lanes/`. Never create,
rename or delete anything under the clone's `.lanes/` outside your own lane directory. Never signal a process you did not start.

Boundary: READ-ONLY on every repository file. CREATE only `tasks/briefs/pc-t90-support/VERIFY-T94-report.md` in your tree (write it
incrementally from the start) and scratch files under `../scratch/`. Never fix anything. Take no outward-facing action.

## PREMISE — MEASURED at authoring (2026-09-23 18:50Z, /home/user/agent-factory@4a38190)
```
$ date -u +%Y-%m-%dT%H:%MZ; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf; git log --format="%h %s" -4 origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-100
2026-09-23T18:50Z
4a38190
4a38190 transcripts: scrubbed sandbox chat digests (2026-09-23)
4f56130 ledger plane 18:4xZ: T94 LANDED (GATED-PENDING-VERIFY) with the coordinator amendment to the
1a94bbb T94 LANDED (tasks #200 + #167) with a coordinator amendment: the runtime's verdict decides f
9669235 transcripts: scrubbed sandbox chat digests (2026-09-23)
$ git diff --stat 1a94bbb 4a38190 -- harness-ports scripts/pc_lane.sh | wc -l   (0 = the T94 landing 1a94bbb and the PIN carry identical R, D, T1, T2)
0
$ for f in R D T1 T2; do echo "$(git rev-parse 4a38190:$f | cut -c1-12) $(git show 4a38190:$f | wc -l) $f"; done
623c5e7fc8c4 581 harness-ports/bin/pc-lane.sh
cbb361842e3e 627 scripts/pc_lane.sh
c4c64d64665a 736 harness-ports/tests/test_pc_lane.sh
700df251e54b 556 harness-ports/tests/test_pc_lane_dispatcher.sh
$ git rev-parse feb26d7:<R D T1 T2> | cut -c1-12   (the lane PIN: the bytes before T94)
183f337eff91 harness-ports/bin/pc-lane.sh
6d6024139163 scripts/pc_lane.sh
67ed1e0c3c56 harness-ports/tests/test_pc_lane.sh
948c19ac580c harness-ports/tests/test_pc_lane_dispatcher.sh
$ grep -n "a dead loop.s FAILED is not this loop.s verdict\|^if \[ -e \"\$LANE_DIR/FAILED\" \]\|^usage_verdict=\|^if \[ \"\${usage_verdict%% \*}\" = failed \]\|^elif grep -Eq \"\$CAPACITY_RX\|^# --- state guard" harness-ports/bin/pc-lane.sh
101:# --- state guard (replay safety) --------------------------------------------
129:# --- a dead loop's FAILED is not this loop's verdict (AF-AP-140, task #167) ------------------------------------------------
135:if [ -e "$LANE_DIR/FAILED" ]; then
518:usage_verdict=""
529:if [ "${usage_verdict%% *}" = failed ]; then
548:elif grep -Eq "$CAPACITY_RX|$QUOTA_RX|$PERSIST_RX|^API call failed" "$REPORT" 2>/dev/null; then
$ grep -n "^  probe=\"\$(bridge \|^  USAGE_VERDICT=\|DRAFT REPORT — the Hermes session FAILED\"\*\|^REMOTE_BRIEF=\|^bridge \"\$LAUNCH\"\|EFF_STATE=\"\$(bridge \|_premise_state=\"\$(printf" scripts/pc_lane.sh | cut -c1-120
211:_premise_state="$(printf '%s' "$_PREMISE_LANE_DIR" | base64 -w0 | { IFS= read -r _premise_lane_b64; bridge "d=\$(pri
250:REMOTE_BRIEF="$PC_AF_REPO/.lanes/$LANE_ID/brief.md"
292:  EFF_STATE="$(bridge "export XDG_RUNTIME_DIR=/run/user/\$(id -u); MP=\$(systemctl --user show -p MainPID --value qw
361:bridge "$LAUNCH" || die "launch call failed (it may still have started — polling anyway)"
391:  probe="$(bridge "test -f $PC_AF_REPO/.lanes/$LANE_ID/FAILED && test ! $PC_AF_REPO/.lanes/$LANE_ID/FAILED -ot $REMO
446:  USAGE_VERDICT="$(printf '%s' "$USAGE_B64" | base64 -d 2>/dev/null | python3 -c 'import json, sys
451:  if [ "$USAGE_VERDICT" = failed ] && [[ "$REPORT_FIRST_LINE" != "DRAFT REPORT — the Hermes session FAILED"* ]]; t
$ bash harness-ports/tests/test_pc_lane.sh 2>/dev/null | tail -1; bash harness-ports/tests/test_pc_lane_dispatcher.sh 2>/dev/null | tail -1   (T1 prints the reset(1) usage text on stderr: a pre-existing backtick, known item K2 below)
67 passed, 0 failed
pc_lane dispatcher: 48 passed, 0 failed
$ grep -n "EXECUTED probe:" harness-ports/tests/test_pc_lane_dispatcher.sh | cut -c1-110
459:check "EXECUTED probe: a stale FAILED (older than this dispatch's brief) with a live loop polls RUNNING; t
464:check "EXECUTED probe: this dispatch's own FAILED (not older than the brief) ends the poll with LANE FAILE
469:check "EXECUTED probe: report.md present while the lane loop is alive polls RUNNING, never READY (the pid 
475:check "EXECUTED probe: report.md present with the lane loop gone polls READY" $? \
480:check "EXECUTED probe: no pidfile yet and a fresh launch.log (the launch window) polls RUNNING (the find r
485:check "EXECUTED probe: no pidfile, no report and a stale launch.log polls GONE" $? \
$ grep -n "died un-retried on .reset after 5m." harness-ports/tests/test_pc_lane.sh | cut -c1-80; git log --format="%h %ad" --date=short -1 -S"died un-retried on" -- harness-ports/tests/test_pc_lane.sh
292:  "2026-09-08 22:2xZ: O3, D5n and B5k died un-retried on `reset after 5m` �
5a19c7f 2026-09-14
$ (render the poll probe through an echoing bridge: PC_AF_REPO=/fake LANE_ID=L; eval the probe line; bash -n on the rendered string)
bash -n rc=0
kill -0 $(cat /fake/.lanes/L/lane.pid
[ -n "$(find /fake/.lanes/L/launch.log -mmin -5 2>/dev/null)" ]
$ (the live probe, 18:52Z: the amended probe rendered for pc-verify-k1-h.md--5276976 and run by the PC bash over the bridge)
RUNNING
probe-rc=0
$ grep -n 'usage.json\|usage-file' harness-ports/bin/pc-lane.sh | cut -c1-60   (no rm of usage.json at an attempt's start: item 3's question)
418:  # the served model is whatever the chain reached — the lane
464:      --usage-file "$LANE_DIR/usage.json" > "$REPORT" 2> "$LOG
508:# No user query found in messages.` and wrote usage.json wi
512:# text screens: a Hermes session whose usage.json says "fail
516:# Never retried here: the same context fails the same way. us
526:print(("failed" if bad else "ok") + " \"failed\": " + flag("f
527:    || { usage_verdict=""; echo "pc-lane: WARNING usage-verdi
534:    { echo "DRAFT REPORT — the Hermes session FAILED (usage.j
537:    echo "pc-lane: the Hermes session FAILED (usage.json $usag
539:    { echo "failed-session: the Hermes runtime reported this s
541:    echo "pc-lane: FAILED — the Hermes session failed (usage.j
561:if [ "$HARNESS" = "hermes" ] && [ -s "$LANE_DIR/usage.json" ]; then
562:  SID="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('session_id',''))" "$LANE_DIR/usage.json" 2>/dev/null
568:      && { printf '\n---\nprofile: %s\n\nusage.json:\n\n```json\n' "${LANE_PROFILE:-unknown}" >> "$TREE/transcripts/pc/$LANE_ID.md"; cat
```
