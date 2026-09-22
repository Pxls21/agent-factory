# PC lane — B9 (issue #17 / D-036: the S0-02 replay leg's per-delivery DELTA model in the runner, the masked log into BOTH sub-legs, and the exact runner→checker replay test)

PIN: 71463f3

Role: code-implementer. Route: the LOCAL build route (`agentfactory-build-local`, the vLLM server default effort; the route
is HYBRID in practice — the cloud step serves a turn when the local step refuses with the chat-template 400 — say so in the
report header, claim nothing about which model produced this report). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first.
Honey mode: ultra Lever-2 — the report is DATA: files:lines, verbatim test counts, discrepancies, NOT-done. Keep your context
small: bounded terminal output (`| tail -n 40`), the report drafted after each item, never a whole-file read where `sed -n`
of a range answers.

AUTHORIZATION: defensive repair of the owner's own S0-02 tooling. Every run uses a scratch tree + labelled launcher/post
doubles under the lane's own directory; NO live capture, no real launcher, relay, harness server, container or host secret
file is touched (the relay URL in every test is closed loopback). The runner's `main` is NEVER executed against the live
harness by this lane (B8's rule stands: the runner never past its preflight on the PC). No commit, no push — the coordinator
harvests the worktree.

## THE CONTRACT

Issue #17 (owner audit B7-01, CORE-BLOCKING; `https://github.com/Pxls21/agent-factory/issues/17`) and D-036 (owner 2026-09-22
10:4xZ, `todo/BUILD-TASKLIST.md` line 110): the S0-02 replay oracle = relay-level dedup under the full contract — identical
event id · the `duplicate:` receipt bound to the second delivery · ONE continuous buzz-acp process · ONE prompt in total ·
ZERO prompts in the second delta · the synthetic Buzz-ACP replay guard kept as defense-in-depth. The repair contract, verbatim
from the issue (the per-delivery DELTA model):

1. Keep one continuous live process across both deliveries.
2. After the first terminal observation, record the timeline boundary (byte offset or exact line/sequence count).
3. Submit the identical event a second time without stopping the process.
4. After the duplicate receipt and the observation window, stop the process and take the final full timeline.
5. Prove the final timeline has the first snapshot as an exact prefix (refuse otherwise).
6. Write only the post-boundary delta as the second delivery's timeline.
7. Grade: first prompts = 1, second-delta prompts = 0 (the checker's existing rule then holds).

Required test (the issue's words): "a producer→consumer integration test that runs the exact replay portion of
`run_s0_02_legs.sh` (the sourced functions, a stub launcher for the ACP process is acceptable ONLY for the process, never for
the timeline shape) and then invokes the exact checker on its output. A hand-built synthetic second-delivery bundle is not
sufficient."

THE CONSUMER IS THE FIXED POINT. `proofs/S0-02/check_buzz_authz.py` (C) is READ-ONLY for this lane: `_check_replay`
(C:561-624) requires the leg root to hold EXACTLY the two sub-leg directories (C:569-574), each sub-leg to hold exactly the six
plain files INCLUDING `buzzacp.log` (`_LEG_FILES_PLAIN` C:143-149 through `_leg_closure` at C:585), the same event id in both
(C:611-615), exactly 1 prompt in `first` (C:616-620) and 0 in `second` (C:621-624); the observables are scanned on the SECOND
sub-leg's `buzzacp.log` only (C:609-610 → `_observe_all` C:368-408, the DEBUG canary + the duplicate-drop text). The committed
bundles `proofs/S0-02/fixtures/evidence-pass/legs/neg-replayed/{first,second}/` are the consumer's shape (six files each;
`first/timeline.jsonl` 7 lines / 1 prompt, `second/timeline.jsonl` 2 lines / 0 prompts — a DELTA-shaped second).

TWO producer/consumer mismatches exist at the PIN, both in the runner's replay case, both to be REPRODUCED red first (item 5
case C) and then repaired (items 2-3):
- M-A (issue #17): `collect_leg "$out/second"` (R:196 → R:91-95) copies the CUMULATIVE live timeline — the second snapshot
  still carries the first prompt → C:621-624 refuses every real capture.
- M-B (found at authoring, measured below): `collect_masked "$out"` (R:246 with `out=$DEST/neg-replayed`, R:99-117) writes
  `neg-replayed/buzzacp.log` at the LEG ROOT and nothing into the sub-legs → C:569-574 refuses the root (`expected exactly the
  sub-leg directories`) and both sub-leg closures lack `buzzacp.log`. Not in B8's scope (issue #15 rows + D1/D2/D3), not in
  issue #17's text — it is the same replay-leg contract, so it belongs to this ONE focused repair (D-031: one repair keyed by
  component S0-02-runner + contract revision = issue #17 + D-036 + this brief, production digest below).

Files: R `proofs/S0-02/tools/pc/run_s0_02_legs.sh` (WRITE), T2 `tests/test_s0_02_buzz_authz.py` (WRITE — new tests + the
adapted pin test; every B8 test at T2:2135-2414 stays green untouched), C `proofs/S0-02/check_buzz_authz.py` (READ-ONLY), D
`proofs/S0-02/tools/pc/deliver_event.py` (READ-ONLY), PP `proofs/S0-01/tools/pc/pc_post.sh` (READ-ONLY, the masked-log producer
:107), the committed fixture bundles (READ-ONLY). Report: `tasks/briefs/s0-02-support/B9-report.md` (WRITE). Nothing else.

## PREMISE — MEASURED at authoring (2026-09-22T13:49:56Z, the sandbox clone at the PIN = origin head; the PC clone ff-synced to the same head); re-measure as item 1

```
PIN 71463f3 (origin head); date 2026-09-22T13:49:56Z
proofs/S0-02/tools/pc/run_s0_02_legs.sh sha256[:16]=2f301973ee198a35 lines=253 last-commit=b3eba6a
proofs/S0-02/check_buzz_authz.py sha256[:16]=6bc4729839495148 lines=762 last-commit=91e33f2
tests/test_s0_02_buzz_authz.py sha256[:16]=3f341399d0cb4f1d lines=2437 last-commit=b3eba6a
proofs/S0-01/tools/pc/pc_post.sh sha256[:16]=92bf9609f54652d3 lines=155 last-commit=77f46a2
set id: 1 files set=a5de0beef100
--- R anchors (grep -n)
34:TURN_WAIT_S=${S0_02_TURN_WAIT_S:-100}
35:POLL_S=5
39:say() { echo; echo "===== [S0-02] $* ====="; }
41:launch_leg() {
50:    [ -f "$FD/launch.ready" ] && return 0
52:      echo "launch died before ready:" >&2; tail -20 "$MARKERS/s0-02.launch.log" >&2; return 4
56:  echo "launch never became ready" >&2; tail -20 "$MARKERS/s0-02.launch.log" >&2; return 4
60:stop_leg() {
62:  [ -f "$pidfile" ] || { echo "no pidfile — nothing of ours to stop"; return 0; }
64:  [ -n "$pid" ] && [ -d "/proc/$pid" ] || { echo "pid $pid already gone"; return 0; }
68:    *) echo "REFUSING to kill pid $pid: /proc exe is '$exe', not our buzz-acp" >&2; return 5 ;;
70:  for _ in $(seq 1 12); do [ -d "/proc/$pid" ] || return 0; sleep 1; done
71:  echo "pid $pid did not exit after SIGTERM" >&2; return 5
76:wait_turn_window() {
82:    [ "$n" -ge "$want" ] && [ "$want" -gt 0 ] && return 0
83:    [ -f "$FD/buzz-acp.exit" ] && { echo "buzz-acp exited during the turn window" >&2; return 6; }
86:  return 0
91:collect_leg() {
94:  cp "$FD/timeline.jsonl" "$out/timeline.jsonl"
99:collect_masked() {
107:    return 9
110:  cp "$FD/buzzacp.log" "$out/buzzacp.log"
113:    rm -f "$out/buzzacp.log"; return 7
119:post_leg() {
127:    return 9
132:deliver() {  # deliver <fixture> <leg-dir> <role> [extra deliver_event.py args...]
139:role_for() {
144:main() {
182:    neg-replayed)
186:      wait_turn_window 1
187:      collect_leg "$out/first"
192:      sleep 1
194:      deliver neg-replayed "$out/second" "$(role_for neg-replayed)" \
195:        --reuse "$out/first/delivered-event.json" \
197:      wait_turn_window 0
198:      collect_leg "$out/second"
205:        --reuse "$out/.probe/delivered-event.json" --flip-signature
207:      wait_turn_window 0
208:      collect_leg "$out"
227:      wait_turn_window 0
228:      collect_leg "$out"
232:      wait_turn_window 1
233:      collect_leg "$out"
237:      wait_turn_window 0
238:      collect_leg "$out"
243:  collect_masked "$out"
--- R return codes in use
      1 exit 3;      6 return 0;      2 return 4;      2 return 5;      1 return 6;      1 return 7;      2 return 9;
--- C anchors (READ-ONLY; grep -n)
136:REPLAY_SUBLEGS = ("first", "second")
143:_LEG_FILES_PLAIN = frozenset({
155:def _leg_closure(leg_dir: Path, leg: str, expected: frozenset):
178:def _prompt_frames(entries, leg):
368:def _observe_all(leg_dir: Path, leg: str, delivery: dict, fixture_name: str) -> frozenset:
451:def _turns(leg_dir: Path, leg: str):
490:            raise Failure(f"{leg}: {len(news)} session/new frame(s), expected exactly 1")
561:def _check_replay(root: Path, identities: dict, anchors: "Anchors"):
569:    if {p.name for p in leg_dir.iterdir()} != set(REPLAY_SUBLEGS):
571:            f"neg-replayed: expected exactly the sub-leg directories "
572:            f"{sorted(REPLAY_SUBLEGS)}, got "
578:    for sub in REPLAY_SUBLEGS:
610:            key = (_observe_all(sub_dir, leg, delivery, fixture_name), delivery)
613:            "neg-replayed: the two deliveries carry different event ids "
618:            f"neg-replayed/first: {turns[0]} ACP turn(s), expected exactly 1 — a replay "
623:            f"neg-replayed/second: {turns[1]} ACP turn(s), expected 0 — the duplicate "
640:            d / sub / "timeline.jsonl" for sub in REPLAY_SUBLEGS
--- T2 anchors (grep -n)
30:FIXTURES = PROOF / "fixtures"
31:PASS_BUNDLE = FIXTURES / "evidence-pass"
35:RUNNER = PROOF / "tools" / "pc" / "run_s0_02_legs.sh"
63:def _bundle(tmp_path: Path, src: Path = PASS_BUNDLE) -> Path:
76:def _expect_failure(bundle_root: Path, needle: str, legs: str = "legs"):
83:def _leg(bundle_root: Path, name: str) -> Path:
1062:def test_replay_second_delivery_with_a_turn_fails(tmp_path):
1070:def test_replay_first_delivery_without_a_turn_fails(tmp_path):
1078:def test_replay_with_two_different_event_ids_fails(tmp_path):
1094:def test_replay_second_subleg_uses_only_the_wider_replay_tolerance(tmp_path):
1406:def test_replay_subleg_replaced_by_a_symlink_is_refused(tmp_path):
1428:def test_replay_leg_must_carry_exactly_the_two_subleg_directories(tmp_path):
1695:def test_pc_runner_replay_window_and_nip98_guard_are_pinned():
2012:def _b8_function_source(source: Path, name: str) -> str:
2028:def _b8_shell_function(
2047:def _b8_runner_env(tmp_path: Path, launcher: Path | None = None) -> dict[str, str]:
2065:def _b8_write_launcher(path: Path, *, ready: bool) -> None:
2082:def _b8_preflight_tree(
2340:def _b8_load_deliver(source: Path):
--- committed replay sub-legs (evidence-pass; the consumer's shape)
first: files=buzzacp.log delivered-event.json delivery.json fixture.json t0.json timeline.jsonl  timeline=7 lines/1701 bytes prompts=1
second: files=buzzacp.log delivered-event.json delivery.json fixture.json t0.json timeline.jsonl  timeline=2 lines/476 bytes prompts=0
evidence-pass second/buzzacp.log: DEBUG-canary lines=2 duplicate-observable lines=1
--- M-B measured: where the runner writes the masked log for the replay leg
  collect_masked "$out"
done

say "captured into $DEST"
```

## ITEMS (in order; the report drafted after each)

1. **Re-measure the premise** at the PIN in your worktree (the same commands; paste). Any sha or anchor that differs →
   STOP, write the discrepancy into the report as the first section, finish nothing else.

2. **R — the per-delivery DELTA model** in the `neg-replayed)` case (R:182-197 at the PIN), issue #17 steps 1-7:
   - after `wait_turn_window 1`: take the FIRST snapshot into `$out/first/timeline.jsonl` cut at its LAST NEWLINE (a partial
     trailing line, if the live writer is mid-line, never enters the first snapshot); record `first_bytes` = the snapshot's
     byte length in a runner-local variable (NO new bundle leaf — the closure sets at C:143-149 are the consumer's contract);
   - the second delivery unchanged (`sleep 1`, the NIP-98 comment, `--reuse … --t0 "$local_first_t0"`);
   - `wait_turn_window 0` unchanged (the observation window); then read the FINAL live timeline and PROVE the first snapshot
     is an exact byte prefix of it (`cmp -n "$first_bytes" "$out/first/timeline.jsonl" "$FD/timeline.jsonl"`); on a mismatch
     print `S0-02: neg-replayed final timeline does not extend the first snapshot (prefix mismatch)` to stderr, write NO
     second timeline, and return a NEW named code not already in use (the codes in use are pasted above; pick one and pin it);
   - write ONLY the post-boundary bytes as `$out/second/timeline.jsonl` (`tail -c +$((first_bytes + 1))`); an EMPTY delta is a
     VALID runner output (the relay dropped the duplicate; buzz-acp saw nothing) — item 5 case B grades what the checker does
     with it, the runner never fabricates lines.
   Put the two steps in two small functions (`snapshot_timeline <out>` → prints first_bytes; `delta_timeline <out>
   <first_bytes>`), each extractable by `_b8_function_source` (T2:2012) so the tests source EXACTLY the production bytes.
   `collect_leg` (R:91-95) stays the plain copy for every other leg.

3. **R — the masked log into BOTH sub-legs** (M-B): for the replay leg `collect_masked` writes the SAME masked log into
   `$out/first/buzzacp.log` AND `$out/second/buzzacp.log` (byte-identical — ONE continuous process produces ONE masked log;
   a boundary split is impossible because masking happens only after exit, PP:107) and NOTHING at the leg root; the 64-hex
   refusal (R:111-113) applies to each copy; every other leg keeps the single copy. State in the report that the checker scans
   only the second sub-leg's log for observables (C:609-610) and that the first sub-leg's copy exists for the closure
   (C:143-149) — a reader must not mistake the duplicate copy for a second observation.

4. **T2 — the adapted source pin** `test_pc_runner_replay_window_and_nip98_guard_are_pinned` (T2:1695-1715): keep its four
   replay asserts; add pins for the prefix proof (`cmp -n`), the delta write (`tail -c +`), and the two sub-leg log copies —
   EACH new pin paired with a behavioral control in items 5-6 (AF-AP-80: a source-text pin alone is a mirror, the verifier
   refuses it).

5. **T2 — THE producer→consumer integration test** (issue #17's required test), built on the B8 harness (`_b8_function_source`
   T2:2012, `_b8_shell_function` T2:2028, `_b8_runner_env` T2:2047, `_b8_write_launcher` T2:2065): the sourced replay functions
   run with
   - a fake LAUNCHER only for the PROCESS (writes `launch.ready`; when the test's stop/post step runs, writes `buzz-acp.exit` and
     the masked `buzzacp.log` = a copy of the committed evidence-pass `second/buzzacp.log`, which carries the DEBUG canary and
     the duplicate-drop observable — counts pasted above);
   - `deliver` replaced by a shell function that (a) copies the committed evidence-pass sub-leg files `fixture.json`,
     `delivered-event.json`, `delivery.json`, `t0.json` into the target sub-leg dir (the real producer shapes at the PIN) and
     (b) APPENDS to the live `$FD/timeline.jsonl` exactly what the live process would write: the 7 lines of evidence-pass
     `first/timeline.jsonl` for the first delivery; for the second delivery the 2 lines of evidence-pass `second/timeline.jsonl`
     (case A) or NOTHING (case B, the empty delta);
   - `stop_leg` against no pidfile (R:63 "no pidfile — nothing of ours to stop"), `post_leg`'s `pc_post.sh` replaced by the fake's
     exit+log write (never the real PP);
   then the runner-produced `neg-replayed` leg replaces the one inside a full copy of the evidence-pass bundle (`_bundle` T2:63)
   and the REAL checker runs on it (`check_bundle` with the bundle's anchors, exactly as the existing replay tests at
   T2:1062-1110 do): case A → the PASS line (paste it); case B → whatever the checker says: if it REFUSES an empty second
   timeline, report the exact failure text as a FINDING (C is out of boundary; the live relay-dropped duplicate may produce
   exactly this) — never adapt the runner to fake lines; case C, the REPRODUCTION: the same harness over the PIN's runner bytes
   (`git show 71463f3:proofs/S0-02/tools/pc/run_s0_02_legs.sh` into a scratch file) → the checker refuses — paste the exact
   text(s) it produces (expected: C:570's `expected exactly the sub-leg directories` first, and with M-B alone repaired,
   C:623's `neg-replayed/second: 1 ACP turn(s), expected 0`) — this is the red-first proof of issue #17 and of M-B.

6. **T2 — the prefix-proof and boundary controls** through the sourced functions: (a) a final live timeline that is NOT an
   extension of the first snapshot (the fake rewrites one byte inside the first region before the final read) → the named
   code, the exact stderr text, and NO `second/timeline.jsonl`; (b) a live file ending MID-LINE at snapshot time → the first
   snapshot ends with a newline, and `first + delta == final` byte-for-byte (assert the concatenation); (c) the empty-delta
   case writes a zero-byte `second/timeline.jsonl` (exists, size 0).

7. **Mutants** — each run in place with a scratch-copy restore (never git-restore/stash), the killing test NAMED in the report,
   a survivor is a report row never a silent skip: m1 `second` gets the cumulative copy (the PIN's behavior) → item 5 case A
   red at C:621-624; m2 the `cmp -n` prefix proof removed → item 6a red; m3 `tail -c +$first_bytes` (off by one) → item 6b red;
   m4 the masked log at the root only (the PIN's behavior) → item 5 red at C:569-574; m5 the log into `first` only → red at the
   second sub-leg's closure (paste the text); m6 the first snapshot not cut at the last newline → item 6b red; m7
   `wait_turn_window 0` removed before the final read → with `S0_02_TURN_WAIT_S` small and a fake that appends its
   second-delivery prompt line after a short delay, case A goes red at C:621-624 ONLY when the window is honored — if m7 is
   EQUIVALENT under the harness, say so and why (a declared equivalence is a report row).

8. **Gates** (paste verbatim, never typed): `bash -n` on R; `python -m pytest -n 8 tests/test_s0_02_buzz_authz.py` TWICE on the
   PC under the 420 s tool cap (the two summaries must agree; the set id `1 files set=a5de0beef100` beside each count);
   `python3 scripts/report_lint.py --min-refs 12 tasks/briefs/s0-02-support/B9-report.md` (apply its `fix:` hints for at most
   three rounds, then paste and finish); `python3 scripts/ap_screen.py` on `git diff` (paste; explain every hit or fix it);
   `git diff --check`. `shellcheck` on R if present (advisory, paste). The B8 tests (T2:2135-2414) untouched and green.

9. **Report** `tasks/briefs/s0-02-support/B9-report.md`: one section per item with file:line refs, the verbatim outputs, the
   mutant table (id · mutation · killing test · result), NOT-done (the live capture is the coordinator's after VERIFY-B9; the
   checker's empty-delta behavior if it refused), the RETRO (one lesson or "retro: nothing to bake").

## RULES THAT SURVIVE EVERYTHING

- CODE INTEL FIRST: `scripts/lane_context.sh` / `graft ask` before reading whole files; the pack is attached to your prompt.
- Every count and timestamp is PASTED from a command; a test runs twice, bitwise; a red first pass is the gate working.
- No stubs of the timeline SHAPE, no fake green: the fake replaces ONLY the process (launcher/post) and the deliver CLI's side
  effects, with the committed producer shapes; the checker is the real checker.
- The boundary is R + T2 + the report. A needed change outside it (C, D, PP, fixtures) is a FINDING in the report, not an edit.
- No commit, no push, no outward action; the coordinator harvests and grades; VERIFY-B9 (independent, targeted) follows.
