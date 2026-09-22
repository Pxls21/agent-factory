# VERIFY-T90 — independent adversarial verify of T91 + T90-R1 (PIN c49880c)

- Lane: `pc-verify-t90.md--c49880c` · role: adversarial-verifier · route: `agentfactory-verify-local`. The lane route is local vLLM default effort and hybrid in practice; a cloud step may serve a turn after a local chat-template refusal. This report makes no claim about its producing model.
- Venue: `tasks/briefs/pc/VENUE-MAP.md` read first. All dispatcher reproductions used isolated scratch repos and fake bridge functions only. No real brief, live lane id, bridge call, OmniRoute write, commit, or push was used.
- Frozen contract: `tasks/briefs/pc/pc-t91-provider-mix-safety-family.md` (T91) and `tasks/briefs/pc/pc-t90-r1.md` (T90-R1 N1–N5). R0 `tasks/briefs/pc-t91-support/T91-report.md` and R1 `tasks/briefs/pc-t90-support/T90-R1-report.md` were claims, not the oracle.

## 1. Premise re-measure

At `2026-09-22T14:21:05Z`, `git rev-parse HEAD` was `c49880c5bb3c6c60335c8386d84da6ad76651d06`; tree clean at start.

```
scripts/pc_lane.sh sha256[:16]=309d5cabe68ab150 lines=555 last-commit=c49880c
harness-ports/tests/test_pc_lane_dispatcher.sh sha256[:16]=186601fb81b0a167 lines=303 last-commit=c49880c
harness-ports/bin/pc-lane.sh sha256[:16]=0e000f53ef6d3899 lines=512 last-commit=9ca3279
harness-ports/tests/test_pc_lane.sh sha256[:16]=83bf3932ce70259d lines=619 last-commit=9ca3279
tasks/briefs/pc-t91-support/T91-report.md sha256[:16]=331a1c0de0ffb68c lines=139 last-commit=9ca3279
tasks/briefs/pc-t90-support/T90-R1-report.md sha256[:16]=ae4cadd1db084227 lines=165 last-commit=c49880c
```

All identities equal the brief premise. Anchor spot check: D `scripts/pc_lane.sh@c49880c:52-74` `PC_LANE_SELF_COPY` private copy/trap, `:189-217` premise and RESUME probe, `:343-351` launch epoch, `:432-515` mix; B `harness-ports/bin/pc-lane.sh@9ca3279:304` `SAFETY_RX`, `:442-451` safety classifier. No premise mismatch.

## 2. N1 — RESUME probe

### Reproduced production probe

D `scripts/pc_lane.sh@c49880c:205` `_premise_state` ships exactly one remote command:

```sh
d=$_PREMISE_LANE_DIR; p=$(cat "$d/lane.pid" 2>/dev/null) || { echo FIRST; exit 0; }; case "$p" in ''|*[!0-9]*) echo FIRST; exit 0;; esac; kill -0 "$p" 2>/dev/null || { echo FIRST; exit 0; }; c=$(readlink -f "/proc/$p/cwd" 2>/dev/null || true); n=$(tr '\0' ' ' < "/proc/$p/cmdline" 2>/dev/null || true); case "$c" in "$d"|"$d"/*) b=1;; *) case "$n" in *"$d"*) b=1;; *) b=0;; esac;; esac; [ "$b" = 1 ] || { echo FIRST; exit 0; }; e=$(stat -c %Y "$d/lane.pid" 2>/dev/null) || { echo FIRST; exit 0; }; case "$e" in ''|*[!0-9]*) echo FIRST;; *) echo "RESUME $e";; esac
```

D `:206-217` accepts only `RESUME <digits>` and otherwise applies `_premise_block_ok` before the first ship call. The fake bridge ran the quoted probe locally in a scratch repo. A bad-premise FIRST deterministically returned `rc=64`, one probe, zero `mkdir -p` ship writes and zero launch writes.

| Shape | Result through D | Consequence |
|---|---|---|
| absent pidfile | FIRST, `rc=64`, ship=0 | premise gate applied |
| stale/dead pid, leading/trailing whitespace, `0`, `1`, NBSP, empty, metacharacter pid text | FIRST, `rc=64`, ship=0 each | premise gate applied |
| normal live pid whose cwd is this lane | RESUME, `rc=75`, ship=1, launch=1 | gate skipped; timeout only because fake poll had `MAX_POLLS=0` |
| pidfile mtime `2027-01-01` | RESUME, `rc=75`, ship=1, launch=1 | gate skipped; future epoch accepted |
| pidfile mtime `0` | RESUME, `rc=75`, ship=1, launch=1 | gate skipped; epoch zero accepted |
| bridge returns `RESUME`, `RESUME +`, or `RESUME +1790000000` | FIRST, `rc=64`, ship=0 | malformed/no/leading-plus epoch rejected |
| pid cwd is `/tmp`, argv contains this lane directory | RESUME, `rc=75`, ship=1, launch=1 | cmdline substring alone bypasses gate |
| sibling whose id is a prefix of this id | FIRST in the constructed case | cwd and argv did not contain this lane's complete directory string |
| sibling whose id is this id plus one byte | RESUME, `rc=75`, ship=1, launch=1 | **F1 below**: substring binding accepts a sibling suffix id |

The suffix reproduction used this lane path `/.../.lanes/b.md--aabbccdd` and a live process with cwd/argv `/.../.lanes/b.md--aabbccddX`; the real command's `*"$d"*` match returned RESUME. Its bad brief therefore shipped and launched. This is exact D production behavior, not a surrogate.

The cmdline-only reproduction likewise used a live `bash -c 'while :; do sleep 60; done' <this-lane-dir>` process with cwd `/.../scratch/v90` (outside every lane) and the target directory only as the `$0`/prompt-style argument. It returned RESUME and shipped. This is a direct reproduction of the T91 pgrep lesson’s false-binding class, not merely a process legitimately launched with a lane path.

Lane ID quoting: D `:146` derives `LANE_ID` by `tr -c 'A-Za-z0-9_.-' '-'`; a `$`, quote and space filename became `i---quote-space.md--aabbccdd`. The recorded probe contained no non-printable or injected metacharacter and the sentinel survived. The specified shell-metachar injection does not reproduce because the lane id is normalized before interpolation.

## 3. N2 — private self-copy

D `scripts/pc_lane.sh@c49880c:52-71` is fail-closed for `mktemp` and `cp`: all following scratch runs made zero bridge calls and returned `64` with the private-copy refusal line.

```
TMPDIR file:       rc=64 ... Not a directory
unwritable TMPDIR: rc=64 ... Permission denied
fake cp exit 23:   rc=64 ... fake cp failure
```

**F2 — FOLLOW-UP: missing `bash` returns an unexpected code but does not run the original.** With `mktemp` and `cp` available but `bash` removed from PATH, D reaches `exec bash "$_self"` at `:67`; the shell prints `exec: bash: not found` and terminates `rc=127`. The lines `:68-71` are unreachable after a failed `exec`, so the standard private-copy `rc=64` message does not occur. The run makes zero bridge calls and does not continue in the original, so it is fail-closed in the security sense. T90-R1 does not explicitly freeze rc 64 for a missing interpreter after copy success. Suggested fix: preflight `bash` or explicitly translate exec failure to 64 if a uniform private-copy error contract is required.

**F3 — BLOCKER: caller-controlled `PC_LANE_SELF_COPY` bypasses copy protection and its EXIT trap deletes that caller path.** D `:52-53` trusts any non-empty caller value. With `PC_LANE_SELF_COPY=/scratch/caller-sentinel`, D executes the original lazily-read file, reaches the bad-premise refusal (`rc=64`, bridge probe=1), then `:74` removes the pre-existing sentinel. The sentinel was absent afterward. With a nonexistent caller path, D also runs the original path and only happens to leave no file. This is reachable production behavior, material to the copy’s purpose and a caller-controlled deletion. It maps to N2’s private-copy fail-closed invariant and is inside D.

## 4. N3 — premise grammar hostile inputs

D `scripts/pc_lane.sh@c49880c:189-198` `_premise_block_ok` results, each through D under fake bridge with rc/ship captured:

| Input | Result |
|---|---|
| two `\t\r` lines | `rc=64`, ship=0 |
| two NBSP (`c2 a0`) lines | `rc=75`, ship=1, launch=1 |
| two zero-width-space (`e2 80 8b`) lines | `rc=75`, ship=1, launch=1 |
| four-backtick fences | `rc=64`, ship=0 |
| `## MEASURED PREMISE` | `rc=64`, ship=0 |
| depth-7 heading | `rc=64`, ship=0 |
| valid-looking premise inside an outer fenced block | `rc=75`, ship=1, launch=1 |
| proper control | `rc=75`, ship=1, launch=1 |

**F4 — FOLLOW-UP: NBSP, ZWSP and code-fenced metadata satisfy the syntactic gate.** GNU awk’s POSIX `[[:space:]]` in this environment does not classify NBSP/ZWS as space; the parser also has no Markdown fence state. The frozen contract explicitly says “non-space character,” and NBSP/ZWS are non-space code points. This is therefore not a contract blocker. The code-fence case is a parser limitation but T90 froze an intentionally simple heading/fence grammar, so it is FOLLOW-UP unless the coordinator strengthens the formal premise language.

## 5. N4/N5 — provider mix and time window

D `scripts/pc_lane.sh@c49880c:446-515` computes `MIX_FROM = LAUNCH_AT - 60 seconds`, escapes single quotes in the combo with `sed "s/'/''/g"`, base64-ships a read-only SQL script, and labels output `combo-window provider mix (per-lane provenance UNVERIFIED)`.

The T harness already captures SQL and the focused dispatcher gate passed `32 passed, 0 failed`. Independent controlled harvest runs used the real D and fake bridge. A resume response `RESUME 1790000000` rendered the output window start `2026-09-21T14:12:20Z`, matching epoch minus 60 s. FIRST uses D’s current UTC time minus 60 s by construction/test at `harness-ports/tests/test_pc_lane_dispatcher.sh:288-297`.

- Two tags emitted the aggregate caveat exactly: `pc_lane: the mix is a COMBO-WINDOW aggregate — 1 conversation tag(s) shared it; per-lane execution provenance is UNVERIFIED (no lane key in call_logs; T92)`.
- Zero rows emitted `pc_lane: provider-mix: no call_logs rows in the window (db=/home/rocco/.omniroute-migrated/storage.sqlite)` and kept `rc=0`.
- A combo `agentfactory-verify-local'quoted` was printed as supplied and the source’s SQL literal escape (`''`) is present. The T hostile-combo control captures and asserts the exact escaped predicate at `T:253-264` `run_poll`.
- A tag containing `|` remained in one line. A tag containing an embedded newline corrupts the tab-row parser: D printed `tags: conv_a(-,n=)`, losing the injected following fields. It did not emit an additional log line in this controlled run. Tags come from the internal call log, not an externally untrusted lane input; no frozen criterion requires robust hostile tag rendering. FOLLOW-UP only.

Re-attach intent: on a normal active resume, `LAUNCH_AT` is the lane pidfile mtime, so harvest reads from original launch. On the common finished-lane/poller-timeout re-attach path, `harness-ports/bin/pc-lane.sh@9ca3279:110-112` removes `lane.pid` in its EXIT trap. D sees FIRST and assigns re-attach time at `scripts/pc_lane.sh:343-347`; its harvest can therefore say `no call_logs rows in the window`, even if the finished original lane made calls. This fails neither N5’s stated live-RESUME policy nor the label’s explicit UNVERIFIED scope. It does not meet the current blocker predicate; per durable lane/request attribution remains T92 NOT built.

## 6. T91 safety-block family

B source matcher: `SAFETY_RX="^(⚠️[[:space:]]*)?The model provider's safety filter blocked"` at `harness-ports/bin/pc-lane.sh:304`. B `:442-451` selects only the first non-empty line, writes `FAILED` prefixed `safety-filter: `, removes `report.md`, promotes a nonempty B-owned incremental draft to `report.partial.md`, then exits `70`.

Independent isolated B runs:

| First non-empty report line | Result |
|---|---|
| exact provider family | `rc=70`, FAILED=yes, report=no |
| BOM + provider family | `rc=0`, normal report |
| ZWSP + provider family | `rc=0`, normal report |
| `# ` + provider family | `rc=0`, normal report |
| ordinary line, family on second line | `rc=0`, normal report |
| a real report quoting family mid-line | `rc=0`, normal report |
| family with no draft | `rc=70`, no partial |
| family with B-owned nonempty draft | production suite proves partial header/payload; exact B control `TB:374-380` `BRIEF15b` passes |

**F5 — FOLLOW-UP: BOM/ZWS/Markdown-prefixed provider refusal reaches report.md.** The matcher has a deliberately strict first-character anchor. These transport/rendering prefixes are not in T91’s specified safety family. No evidence shows Hermes emits them; this is a real hardening gap but not frozen-contract contradiction.

T91’s poller arm is reproduced by its focused dispatcher test at `test_pc_lane_dispatcher.sh:235-247`: a safety `FAILED` returns `70`, prints terminal safety guidance, fetches only `report-$LANE_ID.partial.md`, and no normal report. Empty draft results in no `report.partial.md`, as B’s `[ -s "$LANE_REPORT_DRAFT" ]` requires.

## 7. Mutations

Every listed scratch D passed `bash -n` before the copied dispatcher suite. The copied suite runs the real test harness logic but substitutes only its D pathname.

| Mutant | Result / killing test |
|---|---|
| drop `kill -0` | KILLED: `27 passed, 5 failed`; includes stale pid refusal |
| drop lane binding | KILLED: `31 passed, 1 failed`; foreign live pid refusal |
| copy-failure `exit 64` → `exit 0` | KILLED: `31 passed, 1 failed`; private-copy refusal |
| non-space regex → `length($0)>0` | KILLED: `30 passed, 2 failed`; whitespace and mixed premise controls |
| restore old attribution claim | KILLED: `31 passed, 1 failed`; RESUME aggregate/old-sentence assertion |
| ignore RESUME epoch | KILLED: `31 passed, 1 failed`; RESUME lower SQL bound |
| cmdline-only binding | KILLED: `31 passed, 1 failed`, but by the current bound-live control (not a false-positive control) |
| mtime → ctime | SURVIVED: `32 passed, 0 failed` — **F6 FOLLOW-UP**; no discriminator asserts mtime distinct from ctime |
| copy-failure `exit 64` → `exit 0` (v3) | KILLED: `31 passed, 1 failed` |
| remove `UNVERIFIED` from mix label | KILLED: `31 passed, 1 failed`; READY one-tag exact label |
| drop `-60` | KILLED: `30 passed, 2 failed`; RESUME and FIRST lower bounds |

Hollow-green rate: `1/11` valid mutants survived (ctime mutation). The contract’s specified mtime identity is not fully defended by the existing suite. This alone is a FOLLOW-UP because current production observed behavior still calls `stat -c %Y`; it becomes a blocker only if a repair changes it without a discriminator.

## 8. Reports evidence and red-first claims

R1 lint at current PIN, `python3 scripts/report_lint.py --min-refs 8 tasks/briefs/pc-t90-support/T90-R1-report.md`, reproduced as `report_lint: 5 refs — OK 5, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)` followed by `FLOOR — OK 5 < --min-refs 8`; it exits `1`. R0 likewise has 0 recognized current-worktree refs and fails the requested floor. This exactly confirms the coordinator observation: R1's authoring lane used a then-current lint interpretation that counted 18 refs; the current overlay recognizes 5. The report itself cites a mix of historical `D@PIN` and current references, and the mismatch does not falsify execution evidence, but **F7 FOLLOW-UP**: R0/R1 do not meet the current verifier’s required evidence-floor configuration.

Two R1 red-first claims were re-derived against parent D `9ca3279:scripts/pc_lane.sh` in scratch:

1. Parent copy logic with `TMPDIR=/nonexistent`: `mktemp: failed ... No such file or directory`; then original D continued past premise handling, whereas current D returns its explicit copy refusal `rc=64` before bridge.
2. Parent premise counter `length($0) > 0`: two whitespace lines cause `_premise_block_ok` to accept; current `[^[:space:]]` makes the dispatcher’s whitespace control return `64` before ship.

The original R1 epoch discrepancy is confirmed: `date -u -d @1790000000` is `2026-09-21T14:13:20Z`; lower bound is `2026-09-21T14:12:20Z`, correctly used in current D/T.

## 9. Screens and gates

Fresh focused gates:

```
pc_lane dispatcher: 32 passed, 0 failed
59 passed, 0 failed
```

`bash -n scripts/pc_lane.sh harness-ports/bin/pc-lane.sh harness-ports/tests/test_pc_lane_dispatcher.sh harness-ports/tests/test_pc_lane.sh`: rc `0`.

`python3 scripts/ap_screen.py --tests scripts/pc_lane.sh harness-ports/tests/test_pc_lane_dispatcher.sh harness-ports/bin/pc-lane.sh harness-ports/tests/test_pc_lane.sh` output:

```
--- TEST_SCREEN over 4 path(s): 4 hits over 4 files ---
AF-AP-87: 3
    scripts/pc_lane.sh:378: probe="$(bridge "test -f $PC_AF_REPO/.lanes/$LANE_ID/FAILED ...
    scripts/pc_lane.sh:378: probe="$(bridge "test -f $PC_AF_REPO/.lanes/$LANE_ID/FAILED ...
    harness-ports/tests/test_pc_lane.sh:437: "$([ -n "$GC16" ] && ! kill -0 "$GC16" ...
AF-AP-59: 1
    scripts/pc_lane.sh:370: # The no-pidfile fallback is bounded to the LAUNCH WINDOW ...
```

AF-AP-87 twice and AF-AP-59 at D `:370/:378` are the pre-existing T90 screen hits named in the premise. The test helper is the additional known AP-87 test-only hit. They are outside T90-R1 hunks; no current finding depends on them.

## Finding inventory

1. **F1 BLOCKER — SOLID.** Contract mapping: N1 “bound to THIS lane.” Canonical path: real D probe evaluated on real scratch live processes. Material: both a sibling suffix id and a non-lane process whose argument merely names this lane bypass the premise gate and ship a bad-premise brief. Discriminator: `n1-real.sh` B suffix and `n1-prompt.sh`, each `rc=75 ship=1` vs expected FIRST/`64 ship=0`. Ownership: D current component. Suggested fix: structural cwd containment plus an argv token/path-boundary rule that cannot accept arbitrary prompt arguments; add suffix/prefix/prompt false-binding negative controls.
2. **F2 FOLLOW-UP — SOLID.** A missing `bash` after successful copying returns 127 rather than the standard 64, but does not execute the original or make bridge calls. Suggested fix: normalize exec failure if a single error contract is needed.
3. **F3 BLOCKER — SOLID.** Contract mapping: N2 private copy runs only copied bytes and is fail-closed. Canonical path: real D with caller-provided `PC_LANE_SELF_COPY`. Material: original code executes and caller’s sentinel is deleted by EXIT trap. Discriminator: `n2.sh caller_self_copy_sentinel`, `rc=64 bridge=1 sentinel_exists=NO`. Ownership: D. Suggested fix: unset/reject externally supplied self-copy state before the guard; use an internal readonly variable; trap only the process-created copy.
4. **F4 FOLLOW-UP — SOLID.** NBSP/ZWS and a code-fenced fake premise pass the simple parser. Mapping: no contradiction of frozen “non-space” wording. Suggested fix: specify a Unicode/Markdown premise grammar if desired.
5. **F5 FOLLOW-UP — SOLID.** BOM/ZWS/heading-prefixed safety text is not classified. Mapping: outside frozen exact family. Suggested fix: normalize known transport prefixes before first-line comparison, with a quoted-report negative control.
6. **F6 FOLLOW-UP — SOLID.** ctime mutant survives the dispatcher suite. Mapping: N5 says mtime; current code meets it, but the test does not distinguish. Suggested fix: force diverging ctime/mtime evidence or check source’s `stat -c %Y` by a deterministic contract test.
7. **F7 FOLLOW-UP — SOLID.** The author reports fail the current `report_lint --min-refs 8` floor (R1 5 refs; R0 0) despite historical lane outputs saying 18/0. Mapping: report-quality tooling rather than T90/T91 production behavior. Suggested fix: coordinator re-lints/pins reports against their claimed revision or updates revision-qualified anchors.

## Gate recommendation

**NOT-READY.** F1 and F3 each satisfy all five blockers: frozen-contract mapping, current exact production path reproduction, material effect, deterministic discriminator, and D-boundary ownership. No final gate verdict is claimed; the coordinator owns it.

## DISCREPANCIES / NOT-DONE

- The brief instructed a fake-bridge N1 battery. My first harness recorder returned FIRST without executing D’s quoted probe and therefore could not test the declared shapes. I discarded that result and used a second isolated fake bridge that executes only the captured D probe in a scratch repo; its results are above.
- The brief says future/zero epoch should be classified FIRST or RESUME. The dedicated exact-lane probe measured RESUME for both (`rc=75`, ship=1, launch=1), so D accepts future and zero pidfile mtimes; no frozen criterion currently rejects either.
- The full `ap_screen --tests` output is pasted in section 9; no further pre-existing result is inferred.
- No repair was made. T92 durable request/lane correlation, exact lane attribution after a finished re-attach, robust external-prefix safety handling, Unicode/Markdown premise parsing, and ctime-vs-mtime mutation defense remain NOT built.
- Scratch artifacts only: `/home/rocco/agent-factory/.lanes/pc-verify-t90.md--c49880c/scratch/v90/`. Production tree was not edited. The only worktree change is this report.
