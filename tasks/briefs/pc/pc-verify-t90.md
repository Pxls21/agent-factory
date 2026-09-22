# PC lane — VERIFY-T90 (the independent targeted adversarial verify of the dispatcher's two landings T91 + T90-R1 together: the RESUME probe bound to a live lane pid, the fail-closed private copy, the non-space premise counting, the provider-mix harvest line and its combo-window labelling, the safety-block family)

PIN: c49880c

Role: adversarial-verifier. Route: the LOCAL verify route (`agentfactory-verify-local`, the vLLM server default effort; the
route is HYBRID in practice — the cloud step serves a turn when the local step refuses with the chat-template 400 — say so in
the report header, claim nothing about which model produced this report). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it
first. Honey mode: full (line-bounded findings, evidence anchors, SOLID/UNSURE). Keep your context small: bounded terminal
output (`| tail -n 40`), the report drafted after each item, never a whole-file read where `sed -n` of a range answers.

AUTHORIZATION: defensive verification of the owner's own lane dispatcher. EVERY reproduction runs through the test harness's
FAKE bridge (`harness-ports/tests/test_pc_lane_dispatcher.sh:40` and its env `PC_AF_REPO=/fake PC_LANE_SKIP_ADMIT=1
LANE_SET_SERVER_EFFORT=0 POLL_SECONDS=0 MAX_POLLS=1`) or against a lane id that exists NOWHERE — a dispatcher reproduction
NEVER names a real brief or a live lane (incident 2026-09-22 12:5xZ: a reproduction re-attached a LIVE lane). No real bridge
call, no real lane directory, no OmniRoute write, no commit, no push, no repair.

## THE CONTRACT — the frozen contract is the two briefs `tasks/briefs/pc/pc-t91-provider-mix-safety-family.md` (T91: the
MEASURED provider mix pasted into the harvest line from OmniRoute's read-only call log; the model-provider safety-block text
family → a FAILED lane, the draft promoted as PARTIAL, never a report, never a retry) and `tasks/briefs/pc/pc-t90-r1.md`
(T90-R1: N1 a stale pidfile never bypasses the premise gate — RESUME only for a LIVE pid bound to THIS lane, returning the
original launch epoch; N2 the private self-copy fails CLOSED; N3 whitespace-only premise lines count nothing; N4 the mix line
labelled a combo-window aggregate with per-lane provenance UNVERIFIED; N5 the mix window keyed to the lane's ORIGINAL launch),
graded against the landed bytes at the PIN; the lanes' own reports (`tasks/briefs/pc-t91-support/T91-report.md`, `tasks/briefs/pc-t90-support/T90-R1-report.md`) are the CLAIMS under test, never the
oracle. Verify EVERY claim through the real production path (the real `scripts/pc_lane.sh` and `harness-ports/bin/pc-lane.sh`
sourced/executed under the fake bridge), report every observation (no severity filter), then apply the blocking predicate
(contract-mapped · canonically reproduced · materially effective · a concrete discriminator · in-boundary) and return a GATE
RECOMMENDATION (`MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`) — the coordinator owns the gate.

Files (read-only for you; write ONLY the report): D `scripts/pc_lane.sh`, T `harness-ports/tests/test_pc_lane_dispatcher.sh`,
B `harness-ports/bin/pc-lane.sh` (T91's PC side: `SAFETY_RX` and the first-non-empty-line classification), TB
`harness-ports/tests/test_pc_lane.sh`, R0 `tasks/briefs/pc-t91-support/T91-report.md`, R1 `tasks/briefs/pc-t90-support/T90-R1-report.md`. Report: `tasks/briefs/pc-t90-support/VERIFY-T90-report.md`.

## PREMISE — MEASURED at authoring (2026-09-22T14:17:54Z, the sandbox clone at the PIN = origin head after the T90-R1 harvest; the PC clone ff-synced to the same head); re-measure as item 1

```
PIN c49880c (the T90-R1 harvest on origin); date 2026-09-22T14:17:54Z
scripts/pc_lane.sh sha256[:16]=309d5cabe68ab150 lines=555 last-commit=c49880c
harness-ports/tests/test_pc_lane_dispatcher.sh sha256[:16]=186601fb81b0a167 lines=303 last-commit=c49880c
harness-ports/bin/pc-lane.sh sha256[:16]=0e000f53ef6d3899 lines=512 last-commit=9ca3279
harness-ports/tests/test_pc_lane.sh sha256[:16]=83bf3932ce70259d lines=619 last-commit=9ca3279
tasks/briefs/pc-t91-support/T91-report.md sha256[:16]=331a1c0de0ffb68c lines=139 last-commit=9ca3279
tasks/briefs/pc-t90-support/T90-R1-report.md sha256[:16]=ae4cadd1db084227 lines=165 last-commit=c49880c
--- D anchors (grep -n)
52:PC_LANE_SELF_COPY="${PC_LANE_SELF_COPY:-}"
53:if [ -z "$PC_LANE_SELF_COPY" ]; then
65:    exit 64
67:  PC_LANE_SELF_COPY="$_self" PC_LANE_ORIG="$0" exec bash "$_self" "$@"
71:  exit 64
73:[ "${PC_LANE_DEBUG_ENV:-0}" = 1 ] && printf 'pc_lane: private copy active: %s\n' "$PC_LANE_SELF_COPY" >&2
74:trap 'rm -f "${PC_LANE_SELF_COPY:-}"' EXIT
77:die() { echo "pc_lane: $*" >&2; exit 64; }
182:# _premise_block_ok <brief-file>
189:_premise_block_ok() {
195:             if ($0 ~ /[^[:space:]]/) n++ }
205:_premise_state="$(bridge "d=$_PREMISE_LANE_DIR; p=\$(cat \"\$d/lane.pid\" 2>/dev/null) || { echo FIRST; exit 0; }; c
207:  RESUME\ [0-9]*)
208:    _launch_epoch="${_premise_state#RESUME }"
209:    case "$_launch_epoch" in *[!0-9]*) _launch_epoch="";; esac
211:  *) _launch_epoch="";;
213:if [ -n "$_launch_epoch" ]; then
215:elif ! _premise_block_ok "$BRIEF"; then
343:if [ -n "$_launch_epoch" ]; then
344:  LAUNCH_AT="$(date -u -d "@$_launch_epoch" +%FT%TZ 2>/dev/null || true)"
345:  [ -n "$LAUNCH_AT" ] || die "live lane has an invalid launch epoch: $_launch_epoch"
347:  LAUNCH_AT="$(date -u +%FT%TZ)"
384:    *FAILED*)
395:               REMOTE_PARTIAL="$PC_AF_REPO/.lanes/$LANE_ID/report.partial.md"
432:  MIX_COMBO="${HERMES_MODEL:-}"
435:          code-implementer) MIX_COMBO=agentfactory-build-local;;
436:          adversarial-verifier) MIX_COMBO=agentfactory-verify-local;;
437:          researcher|evidence-gatherer) MIX_COMBO=agentfactory-research;;
438:          curator|echo-sweeper|contract-runner) MIX_COMBO=agentfactory-sweep;;
439:          *) MIX_COMBO=agentfactory-build;;
465:  WHERE api_key_name = 'hermes'
493:    MIX_CMD="printf %s '$MIX_B64' | base64 -d > $MIX_REMOTE && sqlite3 -readonly 'file:$MIX_DB?mode=ro' < $MIX_REMOT
512:    echo "pc_lane: combo-window provider mix (per-lane provenance UNVERIFIED) $MIX_COMBO $MIX_FROM..$MIX_TO: $MIX_CO
514:      echo "pc_lane: the mix is a COMBO-WINDOW aggregate — $MIX_OTHER conversation tag(s) shared it; per-lane exec
--- B anchors (grep -n)
177:# applied; a replayed launch on a dirty tree leaves it alone. A patch that does not apply is a FAILED lane
178:# (the reason in FAILED, rc 70, no report.md to grade), never a lane on the wrong bytes.
183:      { echo "lane patch $(sha256sum "$LANE_PATCH_FILE" | cut -c1-12) does not apply on $PIN:"; cat "$LANE_DIR/patch
184:      echo "pc-lane: lane patch failed to apply — FAILED lane (see $LANE_DIR/FAILED)" >&2
185:      exit 70
206:    echo "pc-lane: graft build FAILED (see $LANE_DIR/graft-build.log) — the lane falls back to grep" >&2
275:# stays the FAILED class (retrying it would burn the backoff for nothing).
301:# deterministic, so retrying only replays the refusal. Match only the first non-empty line: a real lane report may q
304:SAFETY_RX="^(⚠️[[:space:]]*)?The model provider's safety filter blocked"
318:# pid or it FAILED out of retries): the draft, not the counter, is the resume signal.
443:if printf '%s\n' "$first_nonempty" | grep -Eq "$SAFETY_RX"; then
444:  { printf 'safety-filter: '; cat "$REPORT"; } > "$LANE_DIR/FAILED"
447:    { echo "PARTIAL REPORT — the model provider's safety filter refused the lane before it wrote its final report;
448:    echo "pc-lane: safety-filter refusal — preserved report-draft.md as report.partial.md" >&2
450:  echo "pc-lane: FAILED — the model provider's safety filter refused the request; reason in $LANE_DIR/FAILED" >&2
451:  exit 70
478:# own Hermes sessions held the route's admission slots). A refusal is a FAILED lane: the line goes to $LANE_DIR/FAIL
479:# report.md is removed so nothing downstream can grade it, and the script exits 70. The poller reads FAILED.
481:  cp "$REPORT" "$LANE_DIR/FAILED"; rm -f "$REPORT"
482:  echo "pc-lane: FAILED — the route or the harness refused every attempt ($attempt); reason in $LANE_DIR/FAILED: $
--- T anchors (test names)
30:check() { if [ "$2" -eq 0 ]; then pass=$((pass+1)); echo "[PASS] $1"; else fail=$((fail+1)); echo "[FAIL] $1"; fi; ec
297:  "rc=$POLL_RC before=$FIRST_BEFORE after=$FIRST_AFTER sql_bound=$FIRST_BOUND epoch=$FIRST_BOUND_EPOCH"
--- suites at the PIN (sandbox)
dispatcher: pc_lane dispatcher: 32 passed, 0 failed
pc-lane: 59 passed, 0 failed
admission: 22 passed, 0 failed
--- R1 mutant table
86:| drop `kill -0` | `bash -n` clean; suite collected | stale pidfile is FIRST | KILLED: 27 passed, 5 failed |
87:| drop lane binding | `bash -n` clean; suite collected | live pid from another lane is FIRST | KILLED: 31 passed, 1 f
88:| drop fail-closed `exit 64` | `bash -n` clean; suite collected | private-copy failure refuses original | KILLED: 31 
89:| revert non-space regex to `length($0) > 0` | `bash -n` clean; suite collected | whitespace-only and mixed blocks re
90:| restore old attribution sentence | `bash -n` clean; suite collected | combo-window label and old-sentence absence |
91:| ignore RESUME epoch | `bash -n` clean; suite collected | RESUME lower SQL bound | KILLED: 31 passed, 1 failed |
--- known screen hits at the PIN (pre-existing, outside T90-R1's hunks): AF-AP-87 x2 pc_lane.sh:378, AF-AP-59 pc_lane.sh:370, AP-44 test helper
--- coordinator observations for you: (a) the report lint on R1 read '18 refs — OK 18' in the lane and '5 refs — OK 5' in the sandbox (scripts/report_lint.py --min-refs 8 R1) — reproduce at the PIN and explain; (b) the T90-R1 brief's epoch conversion was wrong (1790000000 = 2026-09-21T14:13:20Z) — the lane corrected it; (c) the mix line for a lane re-attached AFTER it finished reads 'no call_logs rows in the window' on the T91-era dispatcher (LAUNCH_AT = the re-attach time); T90-R1 keys the window to the pidfile mtime on a RESUME — a dead lane with a stale pidfile is FIRST, so its window is the re-attach time again: state what the harvest line says for the common 'poller timed out, lane finished, re-attach harvests' path and whether that is the contract's intent
```

## ITEMS (in order; the report drafted after each; every run pasted)

1. **Re-measure the premise** at the PIN in your worktree (the same commands; paste). Any sha or anchor that differs → STOP,
   first section = the discrepancy.

2. **N1 — the RESUME probe** through the real D under the fake bridge with NEW shapes (never T's cases as-is): a pidfile
   holding a pid of a live process whose cwd AND cmdline both name ANOTHER lane id that is a PREFIX/SUFFIX of this one
   (`pc-x.md--abc` vs `pc-x.md--abc1`); a live pid bound to this lane whose pidfile mtime is in the FUTURE or 0; a pidfile
   with trailing whitespace/newline variants (`"123\n"`, `" 123"`, `"123 "`); a pidfile naming pid 1; a live pid whose cmdline
   contains this lane id only inside an argument (the `-z` prompt text — the T91 pgrep lesson: other lanes' prompts NAME this
   lane); a bridge that answers `RESUME` with NO epoch; an epoch with a leading `+`. For each: FIRST or RESUME and the exact
   consequence (the premise gate applied? a ship write issued?). The bridge command string itself (D's `_premise_state=`
   line): paste it and attack its quoting — a lane id containing a shell metacharacter (`'`, `$`, space) — is the lane id
   VALIDATED before it is interpolated into a remote shell command? If not, that is a finding (an injection surface on the
   coordinator's own bridge, in-boundary).

3. **N2 — the fail-closed private copy**: `TMPDIR` unwritable, `TMPDIR` a FILE, `mktemp` present but `cp` failing (a
   read-only target), `bash` missing from PATH for the exec, `PC_LANE_SELF_COPY` set by the CALLER to a path that does not
   exist (does D then run from the original? state the exact behavior and whether the trap removes a caller-named path —
   `rm -f "${PC_LANE_SELF_COPY}"` on a path the caller owns is a finding if reachable).

4. **N3 — the premise gate**: a block with two lines that are only `\t`, `\r`, NBSP (`\xc2\xa0`), a zero-width space; a fenced
   block opened with four backticks; a heading with the words in the other order (`MEASURED … PREMISE`); a heading at depth 7;
   the `PREMISE — MEASURED` heading inside a fenced code block (should it count?). Exact rc + stderr each.

5. **N4/N5 — the mix line and window** through the fake bridge with a scripted `sqlite3` double whose OUTPUT you control:
   a window whose rows carry ≥ 2 tags (the aggregate sentence and the count), zero rows (`no call_logs rows`), a tag string
   containing `|` or a newline (does the harvest line stay one line?), the SQL shipped over the bridge: paste it and check the
   combo filter's escaping for a combo name containing `'` (the T90 N2-era `sed` escaping) — never against the real DB.
   Confirm the lower bound = launch epoch − 60 s for a RESUME and = now − 60 s for a FIRST, from the SQL text your double
   receives (paste both).

6. **T91's safety-block family** (B `SAFETY_RX` + the first-non-empty-line classification): the exact text family that
   matches (paste `SAFETY_RX`), a report whose FIRST non-empty line is the safety text preceded by a BOM / a zero-width space /
   a Markdown heading marker; the text on the SECOND line (not first) — classified or not?; a report that legitimately
   QUOTES the safety sentence in its body; the `report.partial.md` promotion (rc 70) — what does D's `*FAILED*` arm fetch
   and where does it land in the sandbox; a lane whose draft is EMPTY at the block (what is promoted?).

7. **Mutants**: re-run R1's six rows from your own scratch copies (each `bash -n` clean and the suite collected first; the
   killing test named) and add v1 the lane-binding check reduced to cmdline-only (cwd dropped), v2 the epoch returned as the
   pidfile's ctime instead of mtime, v3 `exit 64` → `exit 0` on the copy failure, v4 the aggregate sentence kept but the
   `UNVERIFIED` word dropped, v5 the lower bound's `- 60` dropped. A survivor is a row with a reason.

8. **The reports' evidence**: reproduce R0's and R1's lint at the PIN (`scripts/report_lint.py`), and two of R1's eleven
   red-first rows against the PIN's PARENT bytes for D (`git show 9ca3279:scripts/pc_lane.sh` into a scratch file; the first
   failing assertion pasted — AF-AP-114).

9. **Screens**: `python3 scripts/ap_screen.py --tests D T B TB` at the PIN (paste; the three known hits explained or a finding).

10. **GATE RECOMMENDATION** with the blocking predicate applied per finding; followups listed for D-034's verify-followup issue.

## RULES THAT SURVIVE EVERYTHING

- CODE INTEL FIRST: `scripts/lane_context.sh` / `graft ask` before reading whole files; the pack is attached to your prompt.
- Every count is PASTED; every shape is NEW; the production bytes are never edited (scratch copies only; `git status
  --porcelain` clean except the report); no reproduction ever names a real brief or lane id.
- No commit, no push, no outward action; the coordinator harvests and owns the gate.
