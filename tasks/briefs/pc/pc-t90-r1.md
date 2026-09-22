# PC lane — T90-R1 (the ONE focused repair of the owner audit's three T90 blockers on the dispatcher — a stale pidfile read as RESUME, the self-copy failing OPEN, whitespace-only premise lines counted as evidence — plus the two findings at the T91 landing: the combo-window relabel the audit accepted and the re-attach window)

PIN: 9ca3279

Role: code-implementer. Route: the LOCAL build route (`agentfactory-build-local`, the vLLM server default effort; the route is
HYBRID in practice — the cloud step serves a turn when the local step refuses with the chat-template 400 — say so in the report
header, claim nothing about which model produced the code). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first. Honey mode:
ultra, Lever-2: the report is DATA (files:lines, verbatim counts, pasted assertions, NOT-done). Keep your context small: bounded
terminal output (`| tail -n 40`), the report drafted after each item, never a whole-file read where `sed -n` of a range answers.
Code intel first: the pack `tasks/briefs/pc-t90-support/T90-R1-pack.md` is attached — read it before D.

AUTHORIZATION: defensive work on the owner's own lane tooling. Every reproduction runs through the test harness's fake `bridge`
(T:40; `PC_AF_REPO=/fake PC_LANE_SKIP_ADMIT=1 LANE_SET_SERVER_EFFORT=0 POLL_SECONDS=0 MAX_POLLS=1`) or against a brief whose
lane id exists nowhere — NEVER against a real brief under `tasks/briefs/pc/` (2026-09-22 12:5xZ: a coordinator reproduction of N2
named a live brief, the original bytes kept running, found the live lane and re-attached as a second poller — benign, killed by
pid; the incident-log entry of that time). No server, credential, lane directory or OmniRoute state is touched. The dispatcher
sources `.pc-bridge.env` itself (D:96): a reproduction that reaches the bridge is a reproduction that went wrong.

## THE CONTRACT (D-031: ONE focused repair — component T90 (the dispatcher's premise gate + launch path) · contract revision =
the owner audit's T90-N1/N2/N3 rows + T91-N1 (accepted) recorded in `todo/BUILD-TASKLIST.md` ("AUDIT RECEIVED 2026-09-22
09:5xZ") + the coordinator's G1 at the T91 landing ("T91 LANDED 2026-09-22 12:5xZ") · production digest D `a5a48539e40313b4` at
the PIN). OUT of scope: the PC-side runner `harness-ports/bin/pc-lane.sh` (read-only), T92 (a durable per-request correlation
id), D-039's routes, every other file.

Boundary (edit ONLY these):
- D `scripts/pc_lane.sh`
- T `harness-ports/tests/test_pc_lane_dispatcher.sh`
- R `tasks/briefs/pc-t90-support/T90-R1-report.md` — this lane's report
Read-only: `harness-ports/bin/pc-lane.sh` (the PC runner: `lane.pid` is written by it; its liveness census at :122),
`harness-ports/tests/test_pc_lane.sh` (must stay `59 passed`), the T91 report `tasks/briefs/pc-t91-support/T91-report.md`.

## PREMISE — MEASURED at authoring (2026-09-22 12:5xZ, the sandbox clone; the PC clone ff-synced to 5b37468 = the PIN + one transcripts commit); re-measure as item 1

```
date 2026-09-22T12:46:16Z; PIN 9ca3279 (the T91 harvest commit on origin; the PC clone at 5b37468 = 9ca3279 + a transcripts commit)
scripts/pc_lane.sh sha256[:16]=a5a48539e40313b4 lines=524
harness-ports/tests/test_pc_lane_dispatcher.sh sha256[:16]=2c0b622fa89a88f7 lines=200
harness-ports/bin/pc-lane.sh sha256[:16]=0e000f53ef6d3899 lines=512
--- anchors (grep -n at the PIN)
52:  _self="$(mktemp "${TMPDIR:-/tmp}/pc_lane.sh.XXXXXX")" && cp "$0" "$_self" && PC_LANE_SELF_COPY="$_self" PC_LANE_ORIG="$0" exec bash "$_
54:trap 'rm -f "$PC_LANE_SELF_COPY"' EXIT
169:_premise_block_ok() {
175:             if (length($0) > 0) n++ }
186:_premise_state="$(bridge "test -f $PC_AF_REPO/.lanes/$LANE_ID/lane.pid && echo RESUME || echo FIRST" 2>/dev/null || true)"
187:if [ "$_premise_state" = "RESUME" ]; then
317:LAUNCH_AT="$(date -u +%FT%TZ)"
320:MIX_CAVEAT="$(date -u -d "$LAUNCH_AT + 60 seconds" +%FT%TZ 2>/dev/null || printf '%s' "$LAUNCH_AT")"
415:  MIX_FROM="$(date -u -d "$LAUNCH_AT - 60 seconds" +%FT%TZ 2>/dev/null || printf '%s' "$LAUNCH_AT")"
481:    echo "pc_lane: provider-mix $MIX_COMBO $MIX_FROM..$MIX_TO: $MIX_COUNTS | tags: ${MIX_TAGS:-none}" >&2
483:      echo "pc_lane: provider-mix is per COMBO — $MIX_OTHER other conversation(s) shared it; the lane's own share is the tag(s) starti
--- N1 by reading: the RESUME probe tests FILE PRESENCE
_premise_state="$(bridge "test -f $PC_AF_REPO/.lanes/$LANE_ID/lane.pid && echo RESUME || echo FIRST" 2>/dev/null || true)"
--- N2 reproduced: the self-copy with an unavailable TMPDIR
mktemp: failed to create file via template '/nonexistent/pc_lane.sh.XXXXXX': No such file or directory
pc_lane: lane=pc-k1-g.md--46186d6 harness=hermes role=code-implementer pin=46186d6
pc_lane: premise gate skipped — a resume of pc-k1-g.md--46186d6
17512 /home/rocco/agent-factory/.lanes/pc-k1-g.md--46186d6/brief.md
pc_lane: local route — qwen-builder llama-server not running (vLLM is the local server since D-032); server-effort restart skipped, lane runs at the vLLM server default
launched
pc_lane: polling every 15s (max 60 min)…
scripts/pc_lane.sh: line 1: PC_LANE_SELF_COPY: unbound variable
Terminated
rc=143
--- N3 reproduced: whitespace-only lines satisfy the premise block
whitespace-only rc=0
real rc=0
empty rc=1
--- G1 by reading: LAUNCH_AT unconditional
LAUNCH_AT="$(date -u +%FT%TZ)"
--- suites at the PIN
pc_lane dispatcher: 24 passed, 0 failed
59 passed, 0 failed
The audit's T90-N1 (by reading): `test -f lane.pid` is file PRESENCE — a dead lane's pidfile answers RESUME and the gate is
   skipped, so a legacy brief ships (AF-AP-105's class). The committed T only injects the RESUME token, never a stale pidfile.
The audit's T90-N2 (reproduced above): mktemp fails → the `if` has no failure branch → the ORIGINAL file keeps running (the
   lazily-read hazard the copy exists to prevent) → `PC_LANE_SELF_COPY: unbound variable` at the trap.
The audit's T90-N3 (reproduced above): two whitespace-only lines satisfy `length($0) > 0` twice → rc 0 (AF-AP-64's class).
The audit's T91-N1 (accepted by the coordinator): the harvest line is a COMBO-WINDOW aggregate, not the lane's mix; the landed
   T91 still prints "the lane's own share is the tag(s) starting at launch" (D:483) — an attribution claim with no lane key.
The coordinator's G1 (T91 landing): D:317 `LAUNCH_AT="$(date -u +%FT%TZ)"` is the POLLER's start — on a re-attach the mix
   window starts at the re-attach, not the lane's launch (every harvest today was a re-attach).
```

## ITEMS

1. **Re-measure the premise** at the PIN (`git rev-parse HEAD`, the three digests + line counts, the anchor lines by `grep -n`,
   the two suites) and paste it under `## PREMISE — RE-MEASURED` in R. A mismatch = STOP and report `CONTRACT-INVALID`.

2. **N1 — the RESUME exemption is bound to LIVENESS and to THIS lane (D, T).** The ONE bridge probe at D:186 becomes: the pidfile
   exists AND its pid is alive (`kill -0`) AND that pid belongs to this lane (its `/proc/<pid>/cwd` resolves under
   `.lanes/<lane-id>/` or its `/proc/<pid>/cmdline` names the lane dir) → `RESUME <launch-epoch>` where the epoch is the pidfile's
   mtime (`stat -c %Y`); anything else → `FIRST` — a dead pid, a live pid of another lane, an unreadable pidfile, a bridge error.
   FIRST → the premise gate applies (rc 64 on a brief without a MEASURED block, BEFORE any ship write — AF-AP-79 stays true).
   The probe is ONE command string the test pins (the fake `bridge` asserts it contains `kill -0` and the lane id). Red-first
   tests, each named and each ASSERTING NO SHIP WRITE (the fake bridge records every write-shaped command; the count stays 0
   on a refusal): (a) a stale pidfile → the fake bridge answers FIRST-shaped → a premise-less brief refused rc 64 with the
   existing message; (b) a live pid of another lane → FIRST → refused; (c) a live pid bound to the lane → `RESUME <epoch>` → the
   gate skipped, the poll proceeds; (d) a bridge error → FIRST → refused. The pre-change control: (a) passes today (the token
   injection) — rewrite T's existing RESUME test to inject the NEW answer shape and add the stale-pidfile case as a real fixture
   of the probe's semantics (the fake bridge evaluates `test -f` / `kill -0` against a temp lane dir + a real short-lived
   process the test owns and reaps).

3. **N2 — the self-copy fails CLOSED (D, T).** D:51-53 becomes: mktemp and cp succeed → exec the copy; either fails → one stderr
   line `pc_lane: refusing to run from the lazily-read original — private copy failed (mktemp/cp): <reason>` and `exit 64`,
   BEFORE `set -u`, before any bridge call, before any env file is sourced. Red-first tests: `TMPDIR=/nonexistent` with a brief
   whose lane id exists nowhere and `PC_AF_REPO=/fake` → rc 64 with the exact text, ZERO bridge calls (the fake bridge counts),
   no `PC_LANE_SELF_COPY` message; the control: a writable TMPDIR → the run proceeds past the copy (assert the usual next refusal
   — the missing-brief text — and that `PC_LANE_SELF_COPY` is set in the child, e.g. via a `PC_LANE_DEBUG_ENV=1` echo the test
   enables). Also: `trap` must never reference an unset name — define `PC_LANE_SELF_COPY` before the trap or guard it.

4. **N3 — a premise line counts only when it holds a non-space character (D, T).** `_premise_block_ok` (D:169-180): the counter
   line becomes `if ($0 ~ /[^[:space:]]/) n++`. Red-first tests (unit-level, sourcing the function as the test file already does
   or via a `PC_LANE_PREMISE_CHECK_ONLY=1` seam): a block of two whitespace-only lines → rc 1; one real + one whitespace line
   → rc 1; two real lines → rc 0; the empty block → rc 1; and the dispatcher-level control: the whitespace-only brief is REFUSED
   rc 64 with NO ship write.

5. **N4 — the harvest line is labelled as what it is (D, T) — the audit's T91-N1.** D:481-484: the line reads
   `pc_lane: combo-window provider mix (per-lane provenance UNVERIFIED) <combo> <from>..<to>: <counts> | tags: <tags>`; the
   caveat line becomes `pc_lane: the mix is a COMBO-WINDOW aggregate — N conversation tag(s) shared it; per-lane execution
   provenance is UNVERIFIED (no lane key in call_logs; T92)`; the sentence "the lane's own share is the tag(s) starting at
   launch" is DELETED (grep -c of it in D → 0, pasted). T's existing T91 expectations updated to the exact new strings; one
   negative test asserts the old attribution sentence is absent from the harvest output.

6. **N5 — the mix window is keyed to the LANE's launch, never the poller's (D, T) — the coordinator's G1.** On `RESUME <epoch>`
   (item 2) `LAUNCH_AT` is that epoch rendered `%FT%TZ` (UTC) and `MIX_CAVEAT` = epoch + 60 s; on FIRST the current `date -u`
   stays. Red-first tests: the RESUME poll test's fake bridge answers `RESUME 1790000000` and the captured SQL's `timestamp >=`
   bound equals `2026-09-21T09:32:20Z` (= 1790000000 − 60 s); the FIRST path's bound is within 5 s of now − 60 s.

7. **Mutation table (AF-AP-78: every mutant passes `bash -n` and the suite collects; an INVALID row is stated, never counted).**
   At least SIX rows in scratch copies, each with the killing test's name: `kill -0` dropped from the probe; the lane binding
   dropped; the fail-closed `exit 64` dropped (the original runs on); `[^[:space:]]` reverted to `length($0) > 0`; the attribution
   sentence restored; the RESUME epoch ignored (LAUNCH_AT stays `date -u`).

8. **Gates (each call under the 420 s cap; paste every line verbatim):** `bash -n D T` rc 0; `bash T` ×2 (counts agreeing;
   > 24 now — state the new count); `bash harness-ports/tests/test_pc_lane.sh` ×2 (`59 passed, 0 failed` unchanged);
   `bash harness-ports/tests/run-all.sh` (`ALL SUITES PASSED`); `git diff --check` rc 0; `python3 scripts/ap_screen.py D T`
   (paste the hits; say why each is not a finding); `python3 scripts/report_lint.py --min-refs 15 R` (bounded: three rounds,
   then paste the final line). File identity before/after for D and T (sha256 first 16 + line counts).

9. **Report R** sections, in order: header (route caveat), PREMISE — RE-MEASURED, ITEMS 2-6 (files:lines changed; each red-first
   test with its red output and its green output pasted; the NO-SHIP-WRITE assertion named per control), MUTATION TABLE, GATES,
   DISCREPANCIES, NOT-DONE (T92, D-039, the PC runner). No commit, no push (the shim refuses them anyway); the patch is
   harvested by the dispatcher — and note: the dispatcher that harvests YOU is the PIN's own bytes (a private copy), so nothing
   you change here affects this lane's harvest.
