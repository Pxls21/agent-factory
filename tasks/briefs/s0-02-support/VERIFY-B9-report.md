# VERIFY-B9 report — independent adversarial verify of B9 (S0-02 replay leg as a per-delivery DELTA; issue #17, D-036; task #146)

Lane: verify-b9 (sandbox, Opus 5.5, shared tree, no worktree). PIN bee499f; origin head b03b090 (S0-02 files byte-identical, re-measured).
Only write: this report. Scratch work lived under `/tmp/vb9/` (probes, mutation driver, one scratch tree per mutant), all removed at the end.

**GATE RECOMMENDATION: NOT-READY.** Two findings meet the full blocking predicate: B-1 (the observation window has no behavioral test,
and the report's m7 "EQUIVALENT" is false) and B-2 (item 6b does not assert the newline cut, and the report's m6 "KILLED" is false).
Both are fully reproduced here. Both sit in T2 + the report only (R needs no change for them). One focused repair.
Separately, and before the fresh eight-leg capture, the coordinator must route F-1: the checker grades the replay leg by the alternative
D-036 rejected, and it REFUSES the live shape D-036 predicts. That shape is inferred from pinned upstream source, not a live capture.

## PREMISE — RE-MEASURED

Every premise value in the brief reproduces. No mismatch → no CONTRACT-INVALID stop. The working tree's S0-02 files equal HEAD b03b090,
and HEAD equals the PIN bee499f and the landing 221e68b on every S0-02 path (the bee499f..b03b090 delta is five docs/brief files).

````
$ date -u; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
2026-09-23 07:36Z
b03b090
$ git diff --stat 221e68b origin/... -- proofs/S0-02 tests/test_s0_02_buzz_authz.py proofs/S0-01/tools/pc/pc_post.sh | wc -l
0
$ git diff --stat bee499f origin/... -- (same paths) | wc -l
0
$ git diff --name-only bee499f origin/...
CLAUDE.md
docs/INCIDENT-LOG.md
tasks/briefs/s0-02-support/VERIFY-B9-brief.md
todo/BUILD-TASKLIST.md
wiki/topics/live-state.md
$ git status --short -- proofs/S0-02 tests/test_s0_02_buzz_authz.py proofs/S0-01/tools/pc/pc_post.sh
(empty = clean)
$ sha256[:16] lines path last-commit
93bf0cf987f9d4a0 319 proofs/S0-02/tools/pc/run_s0_02_legs.sh last=221e68b
6bc4729839495148 762 proofs/S0-02/check_buzz_authz.py last=91e33f2
f35cd9542e07ec53 2979 tests/test_s0_02_buzz_authz.py last=221e68b
9fdf8f3a87fa96b3 234 proofs/S0-02/tools/pc/deliver_event.py last=b3eba6a
92bf9609f54652d3 155 proofs/S0-01/tools/pc/pc_post.sh last=77f46a2
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_02_buzz_authz.py
1 files set=a5de0beef100
$ method/seq per line of the committed PASS fixture replay leg
first: [(1, 'c2a', 'initialize'), (2, 'a2c', 'result'), (3, 'c2a', 'session/new'), (4, 'a2c', 'result'), (5, 'c2a', 'session/prompt'), (6, 'a2c', 'session/update'), (7, 'a2c', 'result')]
second: [(1, 'c2a', 'initialize'), (2, 'a2c', 'result')]
$ grep -n 'initialize\|continuous\|seq' proofs/S0-02/check_buzz_authz.py | wc -l
0
$ git log -1 --format='%h %ad' --date=short -- $F/second/timeline.jsonl
088efef 2026-09-08
$ mkdir -p /tmp/vb9/bt && bash scripts/test_summary.sh tests/test_s0_02_buzz_authz.py --basetemp /tmp/vb9/bt; rm -rf /tmp/vb9/bt   (07:37:07Z → 07:38:34Z)
pytest-exit: 0
pytest-summary: 175 passed in 87.09s (0:01:27)        [1 files set=a5de0beef100]
````
The brief's anchor greps reproduce unchanged (R, C, T2 anchors; B9-report.md m-table rows at :46-:52, m7 = "EQUIVALENT under this
zero-latency fake"). The re-read lines, each with its text:
- R:39 `S0_02_REPLAY_PREFIX_MISMATCH=8`; R:111 `snapshot_timeline() {`; R:120 `head -c "$first_bytes" "$FD/timeline.jsonl"`.
- R:128 `delta_timeline() {`; R:130 `cmp -n "$first_bytes" "$out/first/timeline.jsonl" "$FD/timeline.jsonl"`.
- R:132 `return "$S0_02_REPLAY_PREFIX_MISMATCH"`; R:135 `tail -c +$((first_bytes + 1))`; R:223 `neg-replayed)`.
- R:231 `first_bytes=$(snapshot_timeline "$out")`; R:252 `delta_timeline "$out" "$first_bytes"`.
- R:305 `collect_masked "$out/first"`; R:306 `collect_masked "$out/second"`; R:308 `collect_masked "$out"`.
- `wait_turn_window`: R:86 `[ "$n" -ge "$want" ] && [ "$want" -gt 0 ] && return 0`, R:87 `buzz-acp exited during the turn window`
  (return 6), R:88 `sleep "$POLL_S"`. The replay case: R:226 `deliver pos-allowed "$out/first"`, R:227 `wait_turn_window 1`, then
  R:231 `snapshot_timeline`.
- C:143 `_LEG_FILES_PLAIN = frozenset({`; C:155 `def _leg_closure`; C:561 `def _check_replay`; C:571 `expected exactly the sub-leg directories`.
- T2:2192 and T2:2559 set `"S0_02_TURN_WAIT_S": "0"`; T2:1771 pins the `S0_02_TURN_WAIT_S` default.

## ITEMS

Method for items 2-7: a scratch probe module (`/tmp/vb9/probes/test_vb9*.py`, deleted at the end, never in the repo) imports T2's own
helpers read-only by path (`_b9_env`, `_b9_tree`, `_bundle`, `_b9_check`, `_run_checker`). It drives the REAL sourced runner `main` for
`neg-replayed` and the REAL checker. Like T2's `_B9_DRIVER` (T2:2615), the fakes replace only the process (`launch_leg`, `post_leg`) and
the deliver CLI's side effects (copies of the committed sub-leg files + appended timeline bytes). The real `stop_leg` runs, wrapped only
by a trace line. A `sleep` shell function records each call and appends "late" bytes on its first call after they are armed, so the
timing is deterministic with no race. `POLL_S` is set to 0.01 after sourcing, for speed only. Probe runs: `11 passed in 26.31s`,
`22 passed in 5.62s`, `3 passed in 8.95s`. Every verdict below is the real checker's text, pasted from `/tmp/vb9/results/*.json`.

### Item 2 — D-036 clause by clause (+ H1)

| D-036 clause | Checker line that enforces it | Test that goes red when the enforcement is removed | SOLID/UNSURE |
|---|---|---|---|
| 1 identical event id | C:611-615 `if ids[0] != ids[1]:` | NONE. Mutant cm1 removes it and the whole T2 stays green. T2:1078 `test_replay_with_two_different_event_ids_fails` swaps in the neg-stale event, which fails first at C:230-231 `delivered content does not match the fixture's` and never reaches C:611. A same-content event with a new id does reach it (probe `clause1`): `neg-replayed: the two deliveries carry different event ids (226e96aeff61 vs 0606b1e95f8a) — this is not a replay` | SOLID |
| 2 the `duplicate:` receipt bound to the second delivery | NONE. C:599-605 call `_check_delivery(` with `expected_accepted=True`, which binds the receipt's id (C:314 `delivery["event_id"] != delivered["id"]`) and demands accepted/200/echoed. No line reads `message` for `duplicate:` (zero occurrences in C). The committed PASS fixture's second receipt is `"message": ""` | none possible (nothing to remove) | SOLID |
| 3 ONE continuous buzz-acp process | NONE (H1). Zero occurrences of `initialize`, `continuous` or `seq` in C | none possible | SOLID |
| 4 ONE prompt in total | C:616 `if turns[0] != 1:` with C:621 `if turns[1] != 0:`. The runner makes first + delta = final byte for byte: R:130 `cmp -n "$first_bytes"` + R:135 `tail -c +$((first_bytes + 1))` | T2:1070 `test_replay_first_delivery_without_a_turn_fails` (cm2), and T2:1062 `test_replay_second_delivery_with_a_turn_fails` + 2 more (cm3) | SOLID |
| 5 ZERO prompts in the second delta | C:621 `if turns[1] != 0:` | T2:1062 `test_replay_second_delivery_with_a_turn_fails` (cm3) | SOLID |
| (6) synthetic Buzz-ACP replay guard as defense-in-depth | C:609-610 `_observe_all(sub_dir, leg, delivery, fixture_name)` + C:711 `_check_named_observable(leg, fixture_name, found, delivery)` REQUIRE `dropping duplicate event for channel` (relay.rs:2387) in the second sub-leg's log. The oracle row is at `proofs/S0-02/oracle/denial_table.py:133` (`"observable": "dropping duplicate event for channel"`) | T2:847 `test_removing_a_legs_observable_fails_that_leg` [neg-replayed] + 3 more (cm4) | SOLID |

H1 — REPRODUCED. Two bundles with a two-process second sub-leg, both through the real checker:
- h1a (runner-produced): the second delivery appends a restarted process's frames. The real runner writes them as the delta, and
  the checker passes it:
  ```
  second: [[1, "c2a", "initialize"], [2, "a2c", "result"], [3, "c2a", "session/new"], [4, "a2c", "result"]]
  verdict: PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, 6 distinct reasons; +1 revocation leg (assertion 2); removal evidence: ...
  ```
- h1b (the committed PASS fixture): the second sub-leg restarts at seq 1 with `initialize`, and its line 1 is the first sub-leg's line 1
  verbatim (`first_line1_t_utc` = `second_line1_t_utc` = `2026-09-07T16:53:20.100000Z`). The two sub-leg logs differ
  (`logs_byte_equal: false`), so the log channel is two-process shaped too. Verdict: PASS.
- B9's own case A (T2:2657 `test_replay_integration_runner_producer_into_real_checker`) appends exactly this shape and asserts PASS.

Clause 2 — no binding, and the D-036 live shape is REFUSED:
- The verdict does not depend on the second receipt's text. Case-B runs (empty delta) with second receipts `"duplicate:"`, `""` and
  `"accepted as a NEW event (no dedup)"`: all three `PASS`.
- The live shape D-036 predicts, from the pinned upstream (`/home/user/nerdherderdani/buzz` @ `1c8321cd`):
  - The relay's duplicate branch returns `accepted: true, message: "duplicate:"` (buzz-relay `handlers/ingest.rs`, lines 3192-3197)
    BEFORE `dispatch_persistent_event` (line 3258). The HTTP bridge returns it with 200 (`api/bridge.rs`, lines 963-967).
  - So buzz-acp never receives the duplicate, and its relay.rs:2387 line cannot fire for it. That line fires only when buzz-acp itself
    receives an id it has seen (buzz-acp `relay.rs`, lines 2344/2387; `record_event` at 1258-1262).
  - Probe `clause2_live` builds that shape. The second receipt is D's real `_normalise(200, <that body>, id)` =
    `{"accepted": true, "event_id": "226e96ae…", "event_id_echoed": true, "http_status": 200, "message": "duplicate:"}`. The masked log is
    the committed first log (startup + DEBUG canary, no :2387 line). The delta is empty (`second_size: 0`). The runner exits 0. The real checker:
  ```
  FAIL: neg-replayed/second: neither delivery.json nor buzzacp.log carries ANY known denial observable — the leg produced no turn and no named reason
  ```
  So C grades the replay leg by the REJECTED alternative of D-036 (`docs/08_DECISION_LOG.md:47` "a Buzz-ACP-level dedup as the
  oracle"). It needs the synthetic guard's line and ignores the relay's `duplicate:` receipt. B9's case A and case B pass only because
  T2:2627's `post_leg` copies the synthetic `"B9_SECOND_LOG"` (T2:2569), which carries the :2387 line. The live shape is inferred from
  primary source (UNVERIFIED live). The checker's verdict on it is SOLID (reproduced).

### Item 3 — H2, the boundary's position

REPRODUCED. `wait_turn_window 1` (R:227) returns at the first loop pass whose `grep -c '"method":"session/prompt"'` (R:85) counts a
line. That is the REQUEST line. `first_bytes=$(snapshot_timeline "$out")` (R:231) follows at once. Probe h2a (`S0_02_TURN_WAIT_S=2`): the
first delivery writes lines 1-5 (through the prompt request) and its turn's `session/update` + `result` arrive on the next `sleep` call:
```
trace:  launch | deliver FIRST | sleep 1 | late-append | deliver SECOND | sleep 0.01 … | stop | post
first:  [[1,"c2a","initialize"],[2,"a2c","result"],[3,"c2a","session/new"],[4,"a2c","result"],[5,"c2a","session/prompt"]]
second: [[6,"a2c","session/update"],[7,"a2c","result"]]
verdict: PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, …
```
- The first turn's terminal frames land in the SECOND delivery's delta. The checker's grade does NOT change:
  C:178 `def _prompt_frames` counts only c2a prompt frames. The evidence misattributes the first turn's terminal observation to the duplicate, and the first
  sub-leg holds none. Control h2b (the whole turn written at once): first = 7 lines, second = `[]`, PASS.
- Against the issue's wording: issue #17 step 2 says record the boundary "after the first terminal observation". The landed code records
  it after the first observed prompt REQUEST. The frozen B9 brief told the builder to do exactly this
  (`tasks/briefs/pc/pc-b9.md:175` "after `wait_turn_window 1`: take the FIRST snapshot"), so the contract is internally inconsistent.
  Live frequency: R:35 `POLL_S=5` against a turn's latency. The first poll that sees the prompt comes 0-5 s after it is written, so
  any turn slower than that offset puts its update/result in the delta.
- h2c, the grade DOES change (fail-closed): `wait_turn_window`'s `grep -c` (R:85) counts a torn trailing line that holds the prompt
  method, while R:119 `p=d.rfind(b"\n")` cuts that line out of the snapshot. First delivery = lines 1-4 + the prompt line without its
  newline, and the rest arrives on the next `sleep`:
  ```
  first:  [[1,"c2a","initialize"],[2,"a2c","result"],[3,"c2a","session/new"],[4,"a2c","result"]]
  second: [[5,"c2a","session/prompt"],[6,"a2c","session/update"],[7,"a2c","result"]]
  verdict: FAIL: neg-replayed/first: 0 ACP turn(s), expected exactly 1 — a replay leg proves nothing unless the first delivery produced a turn
  ```
  Realism is LOW. The tee writes each line with one `write` + `flush` (`proofs/S0-01/tools/frame_tee.py:369-370`), in a file opened
  `"ab"` (`frame_tee.py:337`). A torn line is visible for microseconds, and the snapshot reads tens of ms after the count. A boundary
  taken after the prompt's terminal `result` would remove both effects.

### Item 4 — m7's "equivalence"

NOT EQUIVALENT. The builder's measurement ran where the feature is dead. Probe m7 (`S0_02_TURN_WAIT_S=2`): the whole first turn is
written at once. The second delivery arms a late second-turn prompt (seq 8: the relay did NOT drop the duplicate and buzz-acp ran
it), which lands on the first `sleep` call inside the observation window:
```
landed (wait_turn_window 0 kept):   second [[8,"c2a","session/prompt"]]  → FAIL: neg-replayed/second: 1 ACP turn(s), expected 0 — the duplicate delivery produced a second turn
m7  (that line deleted):            second []                              → PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, …   (HOLLOW GREEN)
M13 (→ wait_turn_window 1):         second []                              → PASS (HOLLOW GREEN: n=1 from the first turn returns at once)
report's override (wait_turn_window() { :; }): second []                 → PASS (HOLLOW GREEN)
```
- Every committed runner test sets `"S0_02_TURN_WAIT_S": "0"` (T2:2192, T2:2559). Probe `item7_loop`: at 0 the ONLY `sleep` in a full
  `main` run is R:236 `sleep 1` (`turn_wait0_sleeps: ["sleep 1"]`), against `turn_wait2_sleep_count: 139` at 2 s. So no committed
  test ever enters `wait_turn_window`'s loop. The whole-T2 runs of m7 and M13 both SURVIVE (mutation table).
- The frozen contract's m7 row (`tasks/briefs/pc/pc-b9.md:235-237`) named the configuration: `S0_02_TURN_WAIT_S` small and a fake
  whose second-delivery prompt comes after a short delay, "case A goes red … ONLY when the window is honored". The builder measured at
  0 instead (T2:2966 `test_replay_mutant_wait_removed_case_a_still_passes`; `tasks/briefs/s0-02-support/B9-report.md:52` "EQUIVALENT").

### Item 5 — the snapshot/delta domain (R:111-135, `snapshot_timeline` / `delta_timeline`)

The REAL sourced functions, with R:18 `set -euo pipefail` active. Every script line reads `shopt_inherit_errexit=off opts=ehuBc`.
Pasted from `/tmp/vb9/results/domain_*.json`:

| live timeline at snapshot → final | call site `first_bytes=$(…)` | `first/timeline.jsonl` | `delta_timeline` rc / stderr | `second/timeline.jsonl` |
|---|---|---|---|---|
| ABSENT → 7 lines appear | continues; `first_bytes=[]`; stderr `FileNotFoundError …` + `head: invalid number of bytes: ''` | created, 0 bytes | rc 8; `cmp: invalid --bytes value ''` + `S0-02: neg-replayed final timeline does not extend the first snapshot (prefix mismatch)` | ABSENT |
| empty (0 B) → 7 lines | `[0]` | 0 B | rc 0 | 1565 B (whole final) |
| no newline at all → line completed | `[0]` | 0 B | rc 0 | 44 B |
| 7 lines → truncated to 3 lines (shorter) | `[1565]` | 1565 B | rc 8; `cmp: EOF on … after byte 626, line 3` + the prefix-mismatch text | ABSENT |
| 7 lines → same length, byte 101 rewritten | `[1565]` | 1565 B | rc 8; the prefix-mismatch text (cmp's `differ: char 101, line 1` goes to STDOUT) | ABSENT |
| 5 lines → 2 appended, a byte rewritten AFTER the boundary | `[1116]` | 1116 B | rc 0 (by design: the delta region is not proven) | 449 B |
| 5 lines → NEW inode repeating the prefix + 2 lines (`inode_before=2926383`, `inode_after=2926391`) | `[1116]` | 1116 B | rc 0: the proof is content-based, not identity-based | 449 B |
| 5 lines → NEW inode with other content | `[1116]` | 1116 B | rc 8; `cmp: EOF … after byte 434, line 2` + the text | ABSENT |
| CRLF lines + a partial line | `[1572]` (cut after the last `\n`; first ends `\r\n`) | 1572 B | rc 0 | 15 B; the real checker grades a CRLF first sub-leg PASS |
| 7 lines + one 4 MiB line without newline → newline appended | `[1565]` | 1565 B | rc 0 | 4194396 B |
| 7 lines + the 4 MiB line WITH newline | `[4195961]` | 4195961 B | rc 0 | 0 B |
| `$out/first` is a regular FILE (mkdir fails) | continues; `first_bytes=[1565]`; stderr `mkdir: cannot create directory … File exists` + `line 120: …/first/timeline.jsonl: Not a directory` | ABSENT | rc 8; `cmp: …/first/timeline.jsonl: Not a directory` + the prefix-mismatch text | ABSENT |
| `$FD/timeline.jsonl` is a DIRECTORY (python fails) | continues; `first_bytes=[]`; `IsADirectoryError …` | created, 0 B | rc 8; `cmp: invalid --bytes value ''` + the text | ABSENT |
| `delta_timeline "$out" ""` (empty `first_bytes` at the call) | — | 1565 B | rc 8; `cmp: invalid --bytes value ''` + the text | ABSENT |

What `set -euo pipefail` catches, measured (`domain_errexit`):
- `x=$(echo partial; false)` → the script exits 1 (the substitution's LAST status is checked).
- `x=$(false; echo last-ok)` → `REACHED x=last-ok`, rc 0.
- Bash clears `-e` inside a command substitution (`inherit_errexit` is off). So NO failure inside `snapshot_timeline` can stop the
  runner: not R:113 `mkdir -p "$out/first"`, R:114 `size=$(wc -c < "$FD/timeline.jsonl")`, R:119 `p=d.rfind(b"\n")` (python) or
  R:120 `head -c "$first_bytes"`. Only R:121 `printf '%s' "$first_bytes"` decides the status, and it succeeds.

Consequences:
- Every internal failure becomes the SAME named rc 8 "prefix mismatch" in `delta_timeline`. The runner fails closed, but the failure
  is misnamed. The absent case is reachable: `wait_turn_window 1` ends with R:90 `return 0` on TIMEOUT, even with no prompt and no
  timeline file.
- R:114 `size=$(wc -c < "$FD/timeline.jsonl")` is computed and never used (dead variable).
- The "new inode repeating the prefix" row is accepted. A real relaunch cannot produce it: the launcher wipes the frame dir
  (`proofs/S0-01/tools/pc/pc_launch.py:308` `shutil.rmtree(FD, ignore_errors=True)`), and new content fails the proof (row 8). A second
  tee appending to the SAME file (`frame_tee.py:337` opens it `"ab"`) keeps the prefix and puts a fresh `initialize` in the delta:
  that is H1's shape.

### Item 6 — the collection (R:297-308, `if [ "$leg" = "neg-replayed" ]`)

- One log into both sub-legs. Case-A run → `equal: true, size: 487`, leg root = `["first", "second"]` (`coll_identical`). Both copies
  are R:151 `cp "$FD/buzzacp.log" "$out/buzzacp.log"` of one file. PP:107 `mask "$FD/buzzacp.raw.log" > "$FD/buzzacp.log"` writes it
  in place, in the foreground of `post_leg` (R:170 `bash "$REPO/proofs/S0-01/tools/pc/pc_post.sh"`). So the copies are byte-identical
  unless the file changes between R:305 `collect_masked "$out/first"` and R:306 `collect_masked "$out/second"`.
- The 64-hex refusal on the SECOND copy after the first succeeded (`coll_hex_second`; a wrapper appends a 64-hex line to
  `$FD/buzzacp.log` after the real first copy): main rc 7, stderr `REFUSING to keep …/neg-replayed/second/buzzacp.log: unmasked 64-hex
  present`. The partial leg left behind is `first` = 6 files, `second` = 5 files (no `buzzacp.log`). Real checker:
  `neg-replayed/second: missing ['buzzacp.log']`.
- On the FIRST copy (`coll_hex_first`): rc 7, the second copy never runs, both sub-legs lack the log. Checker:
  `neg-replayed/first: missing ['buzzacp.log']`.
- Every failure path is refused by the closure: C:143 `_LEG_FILES_PLAIN` via C:582 `_leg_closure(sub_dir, leg, _LEG_FILES_PLAIN)`,
  and the root closure at C:571 `expected exactly the sub-leg directories`:

  | abort | rc | trace (functions reached) | leftover | real checker |
  |---|---|---|---|---|
  | prefix mismatch (a prefix byte rewritten before the final read) | 8 | `launch · deliver FIRST · sleep 1 · deliver SECOND` — NO `stop`, NO `post` | first 5 files, second 4 (no timeline) | `neg-replayed/first: missing ['buzzacp.log']` |
  | buzz-acp exit marker during the observation window (window 2 s) | 6 | same — NO `stop` | same | same |
  | the REAL `post_leg` with no exit marker | 9 | `… · stop · post` | both sub-legs 5 files | same |
  | 64-hex on the second copy | 7 | `… · stop · post · collect first · collect second` | first 6, second 5 | `neg-replayed/second: missing ['buzzacp.log']` |

  The checker never names the runner's cause: every partial leg reads as a closure miss.
- On rc 8 (B9's NEW abort path) and rc 6, `set -e` exits `main` before R:295 `stop_leg` and `post_leg`. R has no `trap`.
  On rc 8 the buzz-acp that R:50 `setsid /usr/bin/python3 "$LAUNCHER"` started keeps running. rc 6 fires only after its exit
  marker exists. Either way every later leg is skipped: R:249's comment `set -e then aborts the leg` understates it, because it aborts the run.
- With the window at 0 (the committed tests' setting), an exit marker written during the "window" is NOT seen (`exit_window0`: rc 0,
  PASS). R:87's guard (`buzz-acp exited during the turn window`) only runs inside the loop, which no committed test enters.

### Item 7 — the integration test (T2:2657, T2:2692, T2:2707: `def test_replay_integration_*`)

- Sourced: the ENTIRE runner (T2:2620 `source "$B9_R"`). Real `main`, `stop_leg` (no-pidfile path, asserted at T2:2667 `no pidfile`),
  `wait_turn_window`, `snapshot_timeline`, `delta_timeline`, `collect_masked`, and `role_for` (real python over the scratch fixtures).
- Stubbed:
  - T2:2621 `launch_leg() { touch "$FD/launch.ready"; }`.
  - T2:2627 `post_leg() { touch "$FD/buzz-acp.exit"; cp "$B9_SECOND_LOG" "$FD/buzzacp.log"; }`, which copies the COMMITTED synthetic
    second log as "the masked log".
  - T2:2628 `deliver() {`, which copies the committed synthetic sub-leg `fixture.json`, `delivered-event.json`, `delivery.json` and
    `t0.json`, and appends committed timeline lines re-serialised no-space.
- Hand-built parts of the second-delivery bundle:
  - Every non-timeline file of the second sub-leg is a verbatim copy of the synthetic fixture (088efef, 2026-09-08). That includes a
    receipt with `"message": ""` (the pinned relay writes `"duplicate:"`) and a log with the synthetic :2387 line (relay-level dedup
    cannot produce it).
  - The case-A timeline bytes are the synthetic second timeline, a two-process shape (H1).
  - Only the split into snapshot and delta is real runner output. Case B (empty delta) is the only D-036-realistic timeline shape, and
    it passes only with the synthetic log (item 2, `clause2_live`).
- `wait_turn_window` runs but never loops (window 0, item 4). Neither R:86's prompt-count `return 0` nor R:87's `buzz-acp exited during the turn window` return 6
  is exercised. `collect_masked`'s wait loop (R:142 `while [ "$SECONDS" -lt "$deadline" ]; do`) is never entered either; only its
  postcondition R:147 `S0-02: post step incomplete` is.
- Verdict against the issue's words: the sourced functions ARE the exact replay portion, and the fake is ONLY the process + the deliver
  side effects. But the second delivery's receipt, log and case-A timeline are copies of a hand-built synthetic bundle whose shape
  contradicts D-036 clauses 2 and 3.
  The issue calls a "hand-built synthetic second-delivery bundle" not sufficient (`tasks/briefs/pc/pc-b9.md:36`). This test meets that clause for the timeline SPLIT only, not for the second delivery's evidence. The
  frozen brief (item 5) prescribed these copies, so the builder complied.

## MUTATION TABLE

Venue:
- One scratch tree per mutant under `/tmp/vb9/mt-<id>`, extracted from `git archive HEAD proofs/S0-01 proofs/S0-02 proofs/schemas
  tests/test_s0_02_buzz_authz.py tests/conftest.py pyproject.toml`.
- A fresh `git init` borrows the real repo's objects read-only (alternates), so T2's `git show 71463f3:…` resolves. Check: the scratch
  `git show` gives the PIN runner digest `2f301973ee198a35`.
- Each tree runs the WHOLE T2 (`python3 -m pytest tests/test_s0_02_buzz_authz.py -q -rfE -p no:cacheprovider --basetemp
  /tmp/vb9/bt-<id>`) with `test_summary.sh`'s environment, then is deleted with its basetemp.
- Every mutation is an exact-string replacement asserted to match ONCE (`mutate.py check`: 24/24 OK).
- The first archive lacked `proofs/schemas`, so the baseline read `1 failed` (`test_spec_validates_against_the_repo_schema`, a venue
  artifact). The archive was rebuilt and every mutant re-run from it.

AF-AP-138: the unmutated baseline in the SAME venue reads `175 passed in 95.00s (0:01:34)` (R digest `93bf0cf987f9d4a0` = the real R).
Every killer in the legend also passes on the unmutated REAL tree (`19 passed in 18.84s`, each listed `PASSED`). AF-AP-78: every mutant
compiles (`bash -n` rc 0 for R, `py_compile` rc 0 for C) and collects all 175 items (failed + passed = 175 in every row).

Killer legend (T2):
- K-pin = `test_pc_runner_replay_window_and_nip98_guard_are_pinned` (T2:1724)
- K-mirror = `test_leg_file_table_matches_the_runner_writes` (T2:1567)
- K-A = `test_replay_integration_runner_producer_into_real_checker` (T2:2657)
- K-B = `test_replay_integration_empty_delta_second_timeline_passes` (T2:2692)
- K-C = `test_replay_integration_pin_runner_reproduces_the_failure` (T2:2707)
- K-6a = `test_replay_prefix_proof_refuses_a_non_extension` (T2:2799)
- K-6b = `test_replay_mid_line_snapshot_first_plus_delta_equals_final` (T2:2811)
- K-6c = `test_replay_empty_delta_writes_zero_byte_second` (T2:2822)
- K-m1t = `test_replay_mutant_cumulative_second_is_rejected` (T2:2834)
- K-m2t = `test_replay_mutant_no_prefix_proof_still_writes_second` (T2:2854)
- K-m5t = `test_replay_mutant_masked_log_first_only_fails_second_closure` (T2:2926)
- K-m7t = `test_replay_mutant_wait_removed_case_a_still_passes` (T2:2966)
- K-1062 = `test_replay_second_delivery_with_a_turn_fails` (T2:1062)
- K-1070 = `test_replay_first_delivery_without_a_turn_fails` (T2:1070)
- K-762 = `test_blanket_bundle_is_a_blanket_rejection` (T2:762)
- K-768 = `test_spec_negative_leg_reason_is_the_exact_observed_line` (T2:768)
- K-847 = `test_removing_a_legs_observable_fails_that_leg` [neg-replayed] (T2:847)
- K-863 = `test_swapping_a_legs_observable_for_another_legs_fails` [neg-replayed] (T2:863)
- K-1110 = `test_delivery_receipt_for_a_different_event_id_fails` (T2:1110)

Tests named by the report that are not killers of the R-level mutant:
- `test_replay_mutant_off_by_one_delta_breaks_concatenation` (T2:2882)
- `test_replay_mutant_root_only_masked_log_is_rejected` (T2:2906)
- `test_replay_mutant_snapshot_not_cut_at_newline` (T2:2942)

These tests override the production function (or run the PIN bytes) and assert what the override does, so they stay GREEN with the
mutant in R.

| id | mutation (R unless marked C) | compiles | collected | whole-T2 result | ACTUAL killer(s) | the report's killer (B9-report rows m1-m7) | verdict |
|---|---|---|---|---|---|---|---|
| baseline | none | 0 | 175 | `175 passed in 95.00s (0:01:34)` | — | — | clean venue |
| m1 | R:135 `tail -c +$((first_bytes + 1))` → `cp "$FD/timeline.jsonl" "$out/second/timeline.jsonl"` (cumulative second) | 0 | 175 | `6 failed, 169 passed in 94.17s` | K-pin · K-A · K-B · K-6b · K-6c · K-m7t | K-m1t — GREEN (it overrides `delta_timeline`) | KILLED; killer misattributed |
| m2 | R:130-133 `if ! cmp -n "$first_bytes"` … `fi` removed | 0 | 175 | `3 failed, 172 passed in 94.28s` | K-pin · K-6a · K-m2t | K-m2t + 6a | KILLED; report correct |
| m2b | R:130 `if ! cmp -n "$first_bytes"` → `if false && ! cmp -n "$first_bytes"` (pinned text kept) | 0 | 175 | `3 failed, 172 passed in 95.20s` | K-mirror · K-6a · K-m2t | — | KILLED behaviorally (6a) |
| m3 | R:135 `tail -c +$((first_bytes + 1))` → `tail -c +$first_bytes` | 0 | 175 | `6 failed, 169 passed in 96.38s` | K-pin · K-A · K-B · K-6b · K-6c · K-m7t | off-by-one test — GREEN | KILLED; misattributed |
| m4 | R:305-306 `collect_masked "$out/first"` + `collect_masked "$out/second"` → `collect_masked "$out"` (the PIN) | 0 | 175 | `6 failed, 169 passed in 94.88s` | K-pin · K-A · K-B · K-m1t · K-m5t · K-m7t | root-only test — GREEN (PIN bytes) | KILLED; misattributed |
| m5 (= my "`collect_masked "$out/second"` dropped") | R:306 `collect_masked "$out/second"` removed | 0 | 175 | `5 failed, 170 passed in 95.17s` | K-pin · K-A · K-B · K-m1t · K-m7t | K-m5t — GREEN (override) | KILLED; misattributed |
| m6 | R:119 `p=d.rfind(b"\n"); print(p+1 if p>=0 else 0)` → `print(len(d))` | 0 | 175 | `175 passed in 95.76s (0:01:35)` | NONE | snapshot-override test (never runs R's cut) | **SURVIVED** (B-2) |
| m7 | R:241 `wait_turn_window 0` removed | 0 | 175 | `175 passed in 97.78s (0:01:37)` | NONE | "EQUIVALENT" (K-m7t, window 0) | **SURVIVED, NOT equivalent** (B-1) |
| M8 | R:252 `delta_timeline "$out" "$first_bytes"` → `delta_timeline "$out" ""` | 0 | 175 | `4 failed, 171 passed in 95.10s` | K-A · K-B · K-m5t · K-m7t | — | KILLED |
| M9 | R:130 `cmp -n "$first_bytes"` → plain `cmp` | 0 | 175 | `5 failed, 170 passed in 97.27s` | K-pin · K-A · K-6b · K-m5t · K-m7t (K-B stays green: an empty delta compares equal) | — | KILLED |
| M10 | R:120 `head -c "$first_bytes"` → `head -n "$first_bytes"` | 0 | 175 | `1 failed, 174 passed in 99.30s` | K-6b | — | KILLED (only by 6b) |
| M11 | R:231 `first_bytes=$(snapshot_timeline "$out")` moved below R:240 `--t0 "$local_first_t0"` | 0 | 175 | `175 passed in 135.71s (0:02:15)` | NONE | — | **SURVIVED** (F-5): landed FAIL vs mutant PASS in probe m11 |
| M12b | R:305 `collect_masked "$out/first"` removed | 0 | 175 | `6 failed, 169 passed in 134.88s` | K-pin · K-A · K-B · K-m1t · K-m5t · K-m7t | — | KILLED |
| M13 | R:241 `wait_turn_window 0` → `wait_turn_window 1` | 0 | 175 | `175 passed in 134.77s (0:02:14)` | NONE | — | **SURVIVED** (B-1): PASS where landed FAILs (probe m7) |
| M14 | R:227 `wait_turn_window 1` removed | 0 | 175 | `175 passed in 136.63s (0:02:16)` | NONE | — | SURVIVED, fail-closed (F-12): landed PASS vs mutant `FAIL: neg-replayed/first: 0 ACP turn(s) …` (probe `m14_disc`) |
| M15 | R:121 `printf '%s' "$first_bytes"` → `printf '%s' "$size"` | 0 | 175 | `1 failed, 174 passed in 91.42s` | K-6b | — | KILLED |
| M16 | R:119 `p=d.rfind(b"\n")` → `p=d.find(b"\n")` | 0 | 175 | `5 failed, 170 passed in 89.62s` | K-A · K-B · K-6c · K-m1t · K-m7t | — | KILLED |
| M18 | R:132 `return "$S0_02_REPLAY_PREFIX_MISMATCH"` → `return 0` | 0 | 175 | `3 failed, 172 passed in 91.66s` | K-pin · K-6a · K-m2t | — | KILLED (6a behavioral) |
| cm1 (C) | C:611-615 `if ids[0] != ids[1]:` block removed | 0 | 175 | `175 passed in 91.51s (0:01:31)` | NONE | — | **SURVIVED** (F-6) |
| cm2 (C) | C:616-620 `if turns[0] != 1:` block removed | 0 | 175 | `1 failed, 174 passed in 96.94s` | K-1070 | — | KILLED |
| cm3 (C) | C:621-625 `if turns[1] != 0:` block removed | 0 | 175 | `3 failed, 172 passed in 96.81s` | K-1062 · K-C · K-m1t | — | KILLED |
| cm4 (C) | C:610 `_observe_all(sub_dir, leg, delivery, fixture_name)` → `frozenset({oracle.observable_key("neg-replayed")})` | 0 | 175 | `4 failed, 171 passed in 95.02s` | K-762 · K-768 · K-847 · K-863 | — | KILLED |
| cm5 (C) | C:314-318 `delivery["event_id"] != delivered["id"]` block removed | 0 | 175 | `1 failed, 174 passed in 98.11s` | K-1110 | — | KILLED |

Tally: 23 mutants (18 R + 5 C) + 1 baseline. KILLED 17. SURVIVED 6: m6, m7, M11, M13, M14 (R) and cm1 (C).
- Of the survivors, 3 produce hollow greens (m7, M13, M11: the landed code refuses, the mutant PASSes). 2 fail closed (m6: checker
  crash; M14: false refusal). 1 is a checker-test gap (cm1).
- Of the report's 7 rows: 1 is fully accurate (m2). 4 have a true outcome but a wrong killer (m1, m3, m4, m5 are KILLED, by other
  tests than the ones named). 2 are false: m6's KILLED and m7's EQUIVALENT.
- B9's new source pins (T2:1741-1761, from `cmp -n "$first_bytes"` on) all have behavioral pairings: the text-preserving m2b is killed
  by 6a, and m4/m5/M12b by case A. AF-AP-80 holds for them.

## FINDINGS

Predicate columns: C1 contract-mapped · C2 canonical reproduction · C3 material effect · C4 concrete discriminator · C5 inside B9's
boundary (R, T2, the report). A finding blocks only if all five hold.

**B-1 · BLOCKER · SOLID — the observation window has no behavioral test; the report's m7 "EQUIVALENT" is false.**
- What: R:241 `wait_turn_window 0` is the only mechanism that lets a LATE duplicate turn reach the second delta.
  - Deleting it (m7) or turning it into `wait_turn_window 1` (M13) leaves the whole T2 green (`175 passed in 97.78s (0:01:37)`,
    `175 passed in 134.77s (0:02:14)`).
  - With the window live (probe m7, window 2 s, a second-turn prompt that lands inside the window), the landed runner yields
    `FAIL: neg-replayed/second: 1 ACP turn(s), expected 0 — the duplicate delivery produced a second turn`, and both mutants (and the
    report's own `wait_turn_window() { :; }` override) yield `PASS`. That is a hollow green.
- C1 YES: `tasks/briefs/pc/pc-b9.md:235-237` names the configuration: `S0_02_TURN_WAIT_S` small and a delayed second prompt, where
  "case A goes red … ONLY when the window is honored". The builder measured at window 0 (`"S0_02_TURN_WAIT_S": "0"` at T2:2559; row
  `tasks/briefs/s0-02-support/B9-report.md:52` "EQUIVALENT"), a configuration in which the mutated feature is dead. Issue #17 step 4
  ("after the duplicate receipt and the observation window") maps too.
- C2 YES: the real sourced `main` and the real checker. The fakes replace only the process and the deliver side effects, the same
  seam as T2's `_B9_DRIVER`. The survivor count comes from the real gate (the whole T2).
- C3 YES: the required m7 evidence row is false. The gate also cannot detect a regression that mints a PASS for a replay whose
  duplicate DID produce a turn.
- C4 YES: a deterministic probe (the late prompt is appended by the first `sleep` inside the window, no race) plus two whole-T2
  survivor runs.
- C5 YES: T2 + the report. R needs no change.
- Fix (one test + one row): add a sourced-`main` replay case with `S0_02_TURN_WAIT_S` ≥ 2, `POLL_S` overridden small after sourcing,
  and a second-delivery prompt that appears inside the window. Assert C:621's exact text (`if turns[1] != 0:`). Show it red under m7
  and M13, then replace the m7 row.

**B-2 · BLOCKER · SOLID — item 6b does not assert the newline cut; m6 survives; the report's m6 "KILLED" is false.**
- What: with R:119's cut `p=d.rfind(b"\n")` replaced by `print(len(d))` (the snapshot NOT cut at the last newline) the whole T2 stays green
  (`175 passed in 95.76s (0:01:35)`).
  - T2:2811 `test_replay_mid_line_snapshot_first_plus_delta_equals_final` asserts only T2:2819 `concat_ok=yes`, which holds for ANY
    split point.
  - The report's killer (`test_replay_mutant_snapshot_not_cut_at_newline`, T2:2942) overrides `snapshot_timeline` itself and never
    runs R's cut.
- C1 YES: `tasks/briefs/pc/pc-b9.md:234` says "m6 the first snapshot not cut at the last newline → item 6b red". Item 6b itself
  (`tasks/briefs/pc/pc-b9.md:226-227`) says the first snapshot "ends with a newline", and `first + delta == final`.
- C2 YES: an R-level mutant against the whole T2. The consequence is shown through the real `main` and the real checker.
- C3 YES: the required m6 row is false. The regression's live effect (probe `m6_disc`): a mid-line snapshot writes a first sub-leg
  that does not end in `\n` (1605 B), and the real checker CRASHES `JSONDecodeError: Unterminated string starting at: line 1 column 39
  (char 38)`. The landed code writes 1565 B and PASSes. The failure is closed, but a valid capture is lost, and nothing in T2 notices.
- C4 YES: the whole-T2 survivor run plus `m6_disc`.
- C5 YES: T2's 6b + the report.
- Fix: 6b also asserts that the first snapshot ends with `\n` and that its length equals the byte count of the complete lines. Show it
  red under R-level m6, and re-measure every m-row against R itself (F-10).

**F-1 · FOLLOW-UP (escalate BEFORE the live capture) · SOLID on the checker, live shape UNVERIFIED — C and the oracle do not implement D-036 clause 2.**
- The problem: the checker grades the replay leg with the synthetic guard, which D-036 rejected as the live oracle. No line binds the
  relay's `duplicate:` receipt (item 2). The oracle row still names it:
  `proofs/S0-02/oracle/denial_table.py:133` `"observable": "dropping duplicate event for channel"`.
- Reproduced verdicts (real checker, D's real `_normalise`, the real runner `main`):
  - The receipt text never changes the verdict: `"duplicate:"`, `""` and a no-dedup text all PASS.
  - The D-036-predicted live shape (a `duplicate:` receipt, no :2387 line, an empty delta) is refused: `neither delivery.json nor
    buzzacp.log carries ANY known denial observable`.
- Consequence: the fresh eight-leg capture's replay leg is predicted to FAIL on exactly that text.
- C5 fails for B9 (`tasks/briefs/pc/pc-b9.md:39` "THE CONSUMER IS THE FIXED POINT"; C, the oracle and the fixtures are read-only).
  So this is not a B9 blocker. The coordinator routes it (D-034); it may warrant an explicit contract amendment.
- Fix: bind `message` starting `duplicate:` + accepted + 200 + the echoed first id to the second receipt,
  next to the C:599-605 `_check_delivery(` call. Make the :2387 line optional defense-in-depth. Regenerate the committed PASS fixture to D-036's shape, and
  keep the six-key distinctness gate (C:697-702 `len(set(keys)) != len(distinct_legs)`).

**F-2 · FOLLOW-UP · SOLID — H1: D-036 clause 3 (ONE continuous process) is unchecked.**
- h1a, h1b and B9's case A all PASS with a delta that restarts at seq 1 with `initialize`. The committed PASS fixture also carries two
  different logs.
- Owner: C (read-only for B9) or R (a new refusal). Route per D-034.
- Fix candidates: the second delta may not contain `initialize`; its first `seq` continues the first snapshot; the sub-leg logs must be
  byte-identical.

**F-3 · FOLLOW-UP (contract question) · SOLID — H2: the boundary follows the first prompt REQUEST, not the terminal observation.**
- Issue #17 step 2 vs the frozen `tasks/briefs/pc/pc-b9.md:175` (`wait_turn_window 1` then snapshot). The landed code follows the brief.
- Grade unchanged in the usual shape (h2a). A torn prompt line makes it a false refusal (h2c, low realism).
- It interacts with F-1: an "empty delta" rule for relay dedup would falsely refuse whenever a turn outlasts the poll offset
  (R:35 `POLL_S=5`).
- Fix: snapshot after the a2c `result` whose id matches the counted prompt.

**F-4 · FOLLOW-UP · SOLID — the final timeline is read while buzz-acp still runs, and the delta is not cut at a newline.**
- R:252 `delta_timeline "$out" "$first_bytes"` runs before R:295 `stop_leg`. Issue #17 step 4 says stop, THEN take the final timeline.
- A frame mid-write at that read ends the second timeline torn (probe `torn_final`: 40 B, no `\n`), and the real checker CRASHES
  (`JSONDecodeError`). Via the CLI that is rc 1 with an EMPTY stdout (F-13).
- Realism LOW (one `write` + `flush` per line). The frozen brief's item 2 does not order stop-then-read, so this is contract-internal.
- Fix: take the final timeline after `stop_leg`, or cut the delta at its last newline and refuse a torn tail by name.

**F-5 · FOLLOW-UP · SOLID — M11 survives: nothing pins the snapshot before the second delivery (issue #17 steps 2-3).**
- Probe m11 (the first delivery opened a session but produced no prompt; the second produced the turn): landed
  `FAIL: neg-replayed/first: 0 ACP turn(s), expected exactly 1 …` vs M11 `PASS`, a hollow green. Case A cannot see M11.
- Not among the frozen m-rows and no frozen criterion names it, so C1 fails. It is cheap to close in B-1's repair round.

**F-6 · FOLLOW-UP · SOLID — clause 1 (C:611 `if ids[0] != ids[1]:`) has no discriminating test; cm1 survives.**
- T2:1078 `test_replay_with_two_different_event_ids_fails` fails first at C:230-231 `delivered content does not match the fixture's`
  and accepts that text.
- Fix: a same-content event with a new id, signed by the bundle's labelled `pass` owner key (probe `clause1`).
- A checker test outside B9's diff.

**F-7 · FOLLOW-UP · SOLID — the integration test's second-delivery evidence is synthetic (item 7).**
- T2:2627 `post_leg()` copies the synthetic log, and T2:2628 `deliver() {` copies the synthetic receipt/event/t0 and the two-process
  case-A timeline. The frozen brief prescribed this.
- After F-1/F-2, rebuild the second delivery from D's real `_normalise` output on the pinned relay's duplicate response, with a
  one-process log/timeline.

**F-8 · FOLLOW-UP · SOLID — failures inside `snapshot_timeline` are masked, and every one surfaces as a misnamed rc 8.**
- Cause (item 5): bash clears `-e` in command substitutions, so only R:121 `printf '%s' "$first_bytes"` decides the status.
- The absent timeline is reachable: `wait_turn_window 1` returns 0 at timeout (R:90 `return 0`).
- Fix: validate `first_bytes` (a digit string) and the snapshot file inside the function, with its own named code. Or
  `shopt -s inherit_errexit`.

**F-9 · FOLLOW-UP · SOLID — no trap: the new rc 8 abort orphans the launched buzz-acp.**
- Trace: no `stop`. R:50 `setsid` keeps the process running and every later leg is skipped. R:249 says `set -e then aborts the leg`.
- rc 6 also skips `stop_leg` and `post_leg`, but it fires only after buzz-acp's own exit marker exists.
- Pre-existing class (every `set -e` abort in the leg loop). B9 adds one more path.
- Fix: an EXIT/ERR trap that calls the pidfile-owned `stop_leg` (AF-AP-34-safe).

**F-10 · FOLLOW-UP · SOLID — the report's named killers for m1, m3, m4, m5 are wrong.**
- The named tests override the function or run the PIN bytes, so they stay GREEN under the R-level mutant (mutation table). The KILLED
  outcomes are true; the attribution is not.
- Row `tasks/briefs/s0-02-support/B9-report.md:46` "KILLED".

**F-11 · FOLLOW-UP · SOLID — `tasks/briefs/s0-02-support/B9-report.md:35` ("C accepts the valid empty delta; no checker change is needed") is too strong.**
- It holds only with the synthetic log that carries the :2387 line. With the relay-dedup shape, C refuses (F-1).

**F-12 · FOLLOW-UP · SOLID — M14 (R:227 `wait_turn_window 1` removed) survives the whole T2.**
- The consequence fails closed (probe `m14_disc`: landed PASS vs mutant `FAIL: neg-replayed/first: 0 ACP turn(s) …`). A slow-first-turn
  integration case would kill it.

**F-13 · FOLLOW-UP (outside B9) · SOLID — a torn timeline line crashes the checker instead of naming a failure.**
- C:97 `_load_timeline_raw = s0_01._load_timeline_raw` reuses S0-01's `_reject_nan`, which lets `json.decoder.JSONDecodeError` escape.
- The CLI (`python3 proofs/S0-02/check_buzz_authz.py --synthetic-root … …/legs` on a bundle whose first replay timeline ends in a torn
  line) exits `checker rc=1` with an EMPTY stdout and a traceback. That breaks C:6's contract (`failure_reason: <reason>`).
- Route to the S0-01/C owner.

INFO (no action required by B9):
- I-1: R:114 `size=$(wc -c < "$FD/timeline.jsonl")` is dead.
- I-2: R:124's comment `delta_timeline <first_bytes>` omits the `<out>` argument.
- I-3: R:224-225's comment "The first delivery must produce a turn" ("so it is checked before the second is sent")
  is not true in code: `wait_turn_window 1` returns 0 at timeout (R:90 `return 0`). The text predates B9.
- I-4: T2's env `"POLL_S": "0.05"` (T2:2560) and `"FD": str(frame)` (T2:2561) are overwritten when R is sourced (R:35 `POLL_S=5`,
  R:33 `FD=$MARKERS/v2-$HOST_LEG`). Harmless only because the window is 0.
- I-5: the prefix proof is content-based (item 5, the new-inode row).
- I-6: cmp's `differ: char 101, line 1` goes to stdout, not stderr.
- I-7: CRLF, a 4 MiB line, empty and no-newline timelines are all handled.
- I-8: at window 0 an exit marker is not seen (`exit_window0`), which B-1's repair covers.
- I-9: T2's test screen shows 11 hits, all older than B9 (blame 91e33f28, f737de55, 088efef2), and none in B9's hunks (GATES).
- I-10: B9's new pins have behavioral pairings (m2b, m4, m5, M12b).
- I-11: PP:104 masks only lowercase hex (`s#[a-f0-9]{64}#<HEX>#g`), while R:152 refuses `[0-9a-fA-F]{64}`. An uppercase 64-hex in the
  raw log therefore aborts at the first copy with rc 7. That is stricter than the mask, and it predates B9.
- I-12: the set id `a5de0beef100` DOES reproduce (`bash scripts/pc_suite.sh set-id`). `tasks/briefs/s0-02-support/B9-report.md:15`
  ("DISCREPANCY: the brief's set id `a5de0beef100` did not reproduce") looked in the wrong script; the ledger already noted this.

## GATES

````
$ mkdir -p /tmp/vb9/bt && bash scripts/test_summary.sh tests/test_s0_02_buzz_authz.py --basetemp /tmp/vb9/bt; rm -rf /tmp/vb9/bt
run1 start 2026-09-23T08:09:59Z
pytest-exit: 0
pytest-summary: 175 passed in 88.04s (0:01:28)        [1 files set=a5de0beef100]
run2 start 2026-09-23T08:11:27Z
pytest-exit: 0
pytest-summary: 175 passed in 88.62s (0:01:28)        [1 files set=a5de0beef100]
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_02_buzz_authz.py
1 files set=a5de0beef100
$ bash -n proofs/S0-02/tools/pc/run_s0_02_legs.sh
rc=0
$ /root/venv-agent-factory/bin/python -m pyflakes tests/test_s0_02_buzz_authz.py
rc=0
$ python3 scripts/ap_screen.py proofs/S0-02/tools/pc/run_s0_02_legs.sh
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---
$ python3 scripts/ap_screen.py --tests tests/test_s0_02_buzz_authz.py
--- TEST_SCREEN over 1 path(s): 11 hits over 1 files ---
AF-AP-80: 7
    tests/test_s0_02_buzz_authz.py:720: assert "removal_line = removal_note\n" in source
    tests/test_s0_02_buzz_authz.py:721: assert "removal_line = removal_note or" not in source
    tests/test_s0_02_buzz_authz.py:1038: assert checker.DEBUG_LEVEL_CANARY not in real_log.read_text()
    tests/test_s0_02_buzz_authz.py:1641: assert "_load_timeline_raw = s0_01._load_timeline_raw" in src
    tests/test_s0_02_buzz_authz.py:1642: assert "_require_file = s0_01._require_file" in src
    tests/test_s0_02_buzz_authz.py:1674: assert "_load_timeline_raw(leg_dir, leg)" in src
    tests/test_s0_02_buzz_authz.py:1697: assert "os.environ" not in src and "getenv" not in src
AF-AP-34: 4
    tests/test_s0_02_buzz_authz.py:1705: """AF-AP-34: no pkill/killall/name match anywhere in the PC runner."""
    tests/test_s0_02_buzz_authz.py:1705: """AF-AP-34: no pkill/killall/name match anywhere in the PC runner."""
    tests/test_s0_02_buzz_authz.py:1709: for word in ("pkill", "killall", "pgrep"):
    tests/test_s0_02_buzz_authz.py:1709: for word in ("pkill", "killall", "pgrep"):
$ git blame (first commit of each hit line): 720/721 91e33f28 · 1038 f737de55 · 1641/1642/1674/1697/1705/1709 088efef2 — all before 221e68b
$ python3 -m pytest <the 19 legend killers> -q -rA   (unmutated real tree)
19 passed in 18.84s
$ which shellcheck
(none; rc=1)
````

## FOLLOW-UPS FOR D-034

1. F-1 (before the fresh eight-leg capture): bring C, the oracle row and the committed PASS fixture to D-036. The live observable
   becomes the relay's `duplicate:` receipt, bound to the second delivery; the :2387 line becomes optional. Today C refuses the
   predicted live shape.
2. F-2 (H1): decide where "ONE continuous process" is proven: seq continuity, no `initialize` in the delta, byte-identical sub-leg logs;
   in C or in R.
3. F-3 (H2) and F-4: resolve the contract-internal inconsistencies between issue #17 steps 2 and 4 and `tasks/briefs/pc/pc-b9.md`
   item 2 (boundary after the terminal `result`; stop before the final read). Decide F-3 together with F-1, because an "empty delta"
   expectation needs the terminal boundary.
4. F-6: a discriminating clause-1 test (same content, new id).
5. F-9: an EXIT/ERR trap that stops the owned buzz-acp on every abort.
6. F-13: S0-01's `_reject_nan` should turn `JSONDecodeError` into a named `Failure` (C:6's exit contract).
7. F-5, F-12: two more integration cases (first delivery without a turn; a slow first turn). They can ride B-1's repair round.

## NOT-DONE

- No live capture, PC, bridge, relay, real launcher, real `pc_post.sh` or host secret (the brief's rule). F-1's live shape is inferred
  from the pinned upstream source at `/home/user/nerdherderdani/buzz` (`1c8321cd`), not observed.
- The PC-venue suite was not run. The sandbox runs the whole file (175) because the declared inputs are present here.
- shellcheck is not installed here (`which shellcheck` → none).
- No repair was attempted (verify lane: the only write is this report). The tests proposed in B-1, B-2, F-5, F-6 and F-12 are not
  written.
- No thermo-nuclear full-stack pass (not in this brief).
- The probes, the mutation driver and the scratch trees lived in `/tmp/vb9/` and were deleted. Their outputs are pasted here by value.
- Report lint (`--min-refs 15`, maps R/C/T2/PP): its `fix:` hints were applied for three rounds, then stopped:
  round 1 `report_lint: 204 refs — OK 187, NEAR 1, MISS 9, UNCHECKABLE 7, UNRESOLVED 0 (worktree)`;
  round 2 `report_lint: 203 refs — OK 196, NEAR 0, MISS 0, UNCHECKABLE 7, UNRESOLVED 0 (worktree)`;
  round 3 `report_lint: 203 refs — OK 203, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)` (rc 0).

## GATE RECOMMENDATION

**NOT-READY.**
- Blockers: B-1 (the observation window is untested; m7 "EQUIVALENT" is false) and B-2 (6b does not assert the newline cut; m6
  "KILLED" is false). Both meet all five predicate conditions and are fully reproduced in the sandbox (whole-T2 survivor runs + the
  real-runner/real-checker discriminators).
- The repair is ONE focused round in T2 + the report. R can stay as landed (`93bf0cf987f9d4a0`) for the blockers. The round: a live-window replay test
  that kills m7/M13, a newline assertion in 6b that kills m6, and the m-table re-measured against R.
- Everything else is a FOLLOW-UP. F-1 must be routed BEFORE the fresh eight-leg capture. That recommendation depends on a live shape
  inferred from pinned upstream source and NOT reproduced live. The two blockers do not depend on it.
