# B9-R1 report — the ONE focused repair of VERIFY-B9 (S0-02 replay leg), D-036's live oracle in the checker (task #168)

Lane: s0-02-b9-r1 (sandbox, `code-implementer`, SHARED tree, no worktree). PIN c269263; origin head 2ebd486 (S0-02 files
byte-identical, re-measured below). No commit, no push; the coordinator harvests.

**STATUS: DONE (tests green), GATED-PENDING-VERIFY.** All nine contract lines are built. The gate reads `206 passed` twice
(set `a5de0beef100`; the premise floor was `175 passed`). The mutation table kills 26 of 26 mutants. Every one compiles
and collects 206 tests, and every killer passed on the unmutated tree first. This lane does not self-accept. Three
DEVIATIONS are flagged in their own section: the receipt check sits after the distinctness gate, the O docstring changed,
and the PASS line changed.

NOT built / NOT run: no live capture, no PC and no bridge use. The D-036 live shape is inferred from the pinned relay
source; no live run has shown it (details in NOT-DONE).

## PREMISE — RE-MEASURED (2026-09-23 08:55Z, sandbox)

````
$ date -u
Wed Sep 23 08:55:42 UTC 2026
$ git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf ; git rev-parse --short HEAD
2ebd486
2ebd486
$ git diff c269263 HEAD -- <the eight files> proofs/S0-02/fixtures | wc -l
0
$ git status --porcelain -- proofs/S0-02 tests/test_s0_02_buzz_authz.py tasks/briefs/s0-02-support/B9-report.md | wc -l
0
$ git diff --name-only c269263 HEAD
docs/INCIDENT-LOG.md
tasks/briefs/hermes-repin/VERIFY-REPIN-a-report.md
tasks/briefs/laya/VERIFY-J1-0-R23-STAMP-S-brief.md
tasks/briefs/s0-02-support/B9-R1-brief.md
tasks/briefs/s0-05-support/VERIFY-E3-brief.md
todo/BUILD-TASKLIST.md
transcripts/sandbox/chat-2026-09-23.md
wiki/topics/live-state.md
$ sha256[:16] lines path
93bf0cf987f9d4a0 319 proofs/S0-02/tools/pc/run_s0_02_legs.sh
6bc4729839495148 762 proofs/S0-02/check_buzz_authz.py
f35cd9542e07ec53 2979 tests/test_s0_02_buzz_authz.py
9fdf8f3a87fa96b3 234 proofs/S0-02/tools/pc/deliver_event.py
a3c31dbda859a635 288 proofs/S0-02/oracle/denial_table.py
38ae5a69ad28fec9 549 proofs/S0-02/tools/build_fixtures.py
d735e75d42df6099 63 proofs/S0-02/fixtures/PROVENANCE.md
6ff6411a136e2918 80 tasks/briefs/s0-02-support/B9-report.md
$ git -C /home/user/nerdherderdani/buzz rev-parse HEAD
1c8321cd08feb597f8bcff5195c21148fb3e98ed
````

Every brief anchor reproduces at the PIN (C, T2 and O have moved since, so the refs below are pinned to c269263):
- C@c269263:97 `_load_timeline_raw = s0_01._load_timeline_raw`; C@c269263:231 `delivered content does not match the fixture's`.
- C@c269263:298 `def _check_delivery(`; C@c269263:479 `delivery = _check_delivery(leg_dir, leg, delivered, fixture)`.
- C@c269263:561 `def _check_replay`; C@c269263:599 `delivery = _check_delivery(`; C@c269263:611 `if ids[0] != ids[1]:`.
- C@c269263:616 `if turns[0] != 1:`; C@c269263:621 `if turns[1] != 0:`; C@c269263:697 `if len(set(keys)) != len(distinct_legs):`.
- R:33 `FD=$MARKERS/v2-$HOST_LEG`; R:35 `POLL_S=5`; R:227 `wait_turn_window 1`; R:241 `wait_turn_window 0` (R is unchanged).
- T2@c269263:41 `BUZZ_SRC_DEFAULT`; T2@c269263:1078 `def test_replay_with_two_different_event_ids_fails`.
- T2@c269263:2192 and T2@c269263:2559 `"S0_02_TURN_WAIT_S": "0",`; T2@c269263:2627 `cp "$B9_SECOND_LOG" "$FD/buzzacp.log"`.
- T2@c269263:2811 `def test_replay_mid_line_snapshot_first_plus_delta_equals_final`; T2@c269263:2819 `concat_ok=yes`.
- T2@c269263:2942 `def test_replay_mutant_snapshot_not_cut_at_newline`.
- The `neg-replayed` row: O@c269263:128 `"decided_by": "buzz-acp",` and O@c269263:130 `"line": 2387,`.

The pinned relay, read directly (quoted here in words, not as repo refs): in `crates/buzz-relay/src/handlers/ingest.rs`,
lines 3192-3197, the `!was_inserted` branch returns `accepted: true, message: "duplicate:"`. In
`crates/buzz-relay/src/api/bridge.rs`, lines 963-968, the bridge answers `{event_id, accepted, message}`. In
`crates/buzz-acp/src/relay.rs`, line 2387, buzz-acp logs `dropping duplicate event for channel {channel_id}`. No mismatch,
so there is no CONTRACT-INVALID stop.

## PREMISE ADDENDUM — primary-source checks made before building on the brief

- Kind 9 is `KIND_STREAM_MESSAGE` (buzz-core `kind.rs`, line 479). Its ingest path skips the reaction branch (`ingest.rs`
  line 3016, `if kind_u32 == KIND_REACTION {`) and inserts at line 3158. On `!was_inserted` it returns
  `accepted: true, message: "duplicate:"` (lines 3192-3197), BEFORE `dispatch_persistent_event` at line 3258.
- A NEW kind-9 event gets `{event_id, accepted: true, message: ""}` (lines 3270-3274).
- Other kinds answer a suffixed `duplicate: …` text (reactions at line 3080, channels at line 2883). So the exact-match rule
  is right for kind 9.
- The brief's premise (the relay dedups before dispatch) is VERIFIED from pinned source. It is NOT verified live.

## DESIGN DECISIONS (each forced by a measured constraint)

1. **Clause 2 (R3) is graded AFTER the distinctness gate, not next to the first-sub-leg receipt call.** This is a DEVIATION
   from the brief's placement hint.
   - Why: `proofs/S0-02/spec.json` (READ-ONLY) pins the blanket bundle's exact failure,
     `blanket-rejection: reasons ['delivery::restricted: not a channel member'] not distinct — 6 negative legs collapsed to
     1 observable(s)`. For that text, the blanket's replay leg must reach the gate with the shared key, so its second
     receipt shows the shared relay text, not `duplicate:`. A pre-gate `message == "duplicate:"` check would refuse the
     blanket bundle first and break the spec's negative leg.
   - So the replay's second receipt gets a SHAPE-only read before the gate: C:712 `delivery = _read_receipt(sub_dir, leg)`.
     C:304 `def _read_receipt` is extracted from `_check_delivery` and preserves its behavior.
   - The five receipt fields are graded after the gate, as the replay leg's named-observable check:
     C:877 `replay_dind = _check_duplicate_receipt(found, delivery, replay_first_id)`.
   - Side effect: the first-id binding is LIVE. The generic `delivery.event_id == delivered.id` rule no longer binds the
     second receipt, so R3's binding to the FIRST delivery's id is the only one, and its mutant is killable (cr4 below).
2. **Clause 3 (R4) runs AFTER the turn counts.** C:734 `_check_one_process(leg_dir, entries[0], entries[1])` follows
   C:729 `if turns[1] != 0:`. A restarted delta that ALSO carries a turn keeps its existing turn-count text. That keeps
   `test_replay_second_delivery_with_a_turn_fails` and case C's M-A text unchanged.
3. **The drop-line text stays in the observation scan.** C:382 `ALL_OBSERVABLES = tuple(sorted(` gains the row's
   `defense_in_depth` observable.
   - Why: without it, the old synthetic shape (the :2387 line with a `""` receipt) fails early with `neither delivery.json
     nor buzzacp.log carries ANY known denial observable`, not with R3's text, which R6 requires (mutant cd2 proves this).
   - Its presence is RECORDED on the PASS line (C:888 `replay_line = (`). Its absence never fails. It never replaces the
     receipt.

## R4 MECHANISM — decided from measurement of the real producers (S0-01's, read-only)

````
$ (per real timeline in /root/s0-01-realleg/golden) n, seq[0], seq[-1], consecutive, initialize@, session/new@, prompts@
run-1: n=11 seq[0]=1 seq[-1]=11 consecutive=True keys0=['dir', 'frame', 'seq', 't_mono_ns', 't_utc'] initialize@[1] session/new@[3] prompts@[7]
run-2: n=11 seq[0]=1 seq[-1]=11 consecutive=True keys0=['dir', 'frame', 'seq', 't_mono_ns', 't_utc'] initialize@[1] session/new@[3] prompts@[7]
two-users: n=20 seq[0]=1 seq[-1]=20 consecutive=True keys0=['dir', 'frame', 'seq', 't_mono_ns', 't_utc'] initialize@[1] session/new@[3, 12] prompts@[7, 16]
cancel: n=13 seq[0]=1 seq[-1]=13 consecutive=True keys0=['dir', 'frame', 'seq', 't_mono_ns', 't_utc'] initialize@[1] session/new@[3] prompts@[7]
negative: n=2 seq[0]=1 seq[-1]=2 consecutive=True keys0=['dir', 'frame', 'seq', 't_mono_ns', 't_utc'] initialize@[1] session/new@[] prompts@[]
shutdown: n=11 seq[0]=1 seq[-1]=11 consecutive=True keys0=['dir', 'frame', 'seq', 't_mono_ns', 't_utc'] initialize@[1] session/new@[3] prompts@[7]
$ (per real masked log) 'buzz-acp starting:' / 'agent initialized agent=' / 'agent_pool_ready' / 'ACP client connected' counts
run-1 starting=1 initialized=1 pool_ready=1 acp_connected=1
run-2 starting=1 initialized=1 pool_ready=1 acp_connected=1
two-users starting=1 initialized=1 pool_ready=1 acp_connected=1
cancel starting=1 initialized=1 pool_ready=1 acp_connected=1
shutdown starting=1 initialized=1 pool_ready=1 acp_connected=1
$ (the committed evidence-pass replay logs at the PIN)
first: lines=3 starting=1 canary=1 dropline=0 sha=9572e611a918
second: lines=4 starting=1 canary=1 dropline=1 sha=96370a69dbbe
````

Producer facts behind the numbers:
- The tee keeps ONE `seq` counter per process: `proofs/S0-01/tools/frame_tee.py:178` `seq = [0]`.
- Each record takes the next value: `proofs/S0-01/tools/frame_tee.py:363` `seq[0] += 1`.
- One timeline file, appended: `proofs/S0-01/tools/frame_tee.py:337` `tl = open(os.path.join(framedir, "timeline.jsonl"), "ab")`.
- The launcher wipes the frame dir per launch: `proofs/S0-01/tools/pc/pc_launch.py:308` `shutil.rmtree(FD, ignore_errors=True)`.
- It opens a fresh raw log per launch: `proofs/S0-01/tools/pc/pc_launch.py:354` `raw_log = open(raw_log_path, "ab")`.
- It keys its own start line on the banner: `proofs/S0-01/tools/pc/pc_launch.py:401` `"buzz-acp starting:" in ln`.
- buzz-acp emits that banner once, in its entry point (buzz-acp `lib.rs`, line 2454, `tracing::info!("buzz-acp starting: …")`).
- The post step masks the raw log once, after exit: `proofs/S0-01/tools/pc/pc_post.sh:107` `mask "$FD/buzzacp.raw.log"`.
- R copies that one masked log into both sub-legs: R:305 `collect_masked "$out/first"`, R:306 `collect_masked "$out/second"`.

The mechanism is `_check_one_process` (C:597 `def _check_one_process`). It has four named refusals, all ending "a second
process, not ONE continuous buzz-acp process (D-036 clause 3)":
- (a) C:617 `if rec.get("dir") == "c2a"`: the second delta holds no `initialize` frame (a restarted agent opens with one).
- (b) C:626 `if type(prev) is not int`: each delta record's `seq` is an int that continues the preceding one, starting
  from the first snapshot's last `seq`. A restarted tee restarts at 1.
- (c) C:637 `if logs[0] != logs[1]:`: the two sub-legs carry byte-identical `buzzacp.log` (ONE masked log).
- (d) C:645 `if starts != 1:`: that log shows exactly one line with C:139 `PROCESS_START_BANNER = "buzz-acp starting:"`.

A second `session/new` is NOT refused: `two-users` shows one inside ONE process (seq 12). An empty delta passes (a) and (b)
trivially. (c) and (d) still apply; they are the only channel that can see a second process when the delta is empty.

## CONTRACT LINES R1-R9 — where each lives and what pins it

**R1 (B-1) — DONE.**
- Test: T2:3341 `def test_replay_observation_window_catches_a_late_second_turn`. It drives the sourced `main` with
  `S0_02_TURN_WAIT_S=2`.
- `POLL_S` is set after the source: T2:2958 `POLL_S=$B9_POLL_S`.
- The late prompt lands on the window's first poll through the driver's T2:2961 `sleep() {`.
- It asserts the trace (`deliver first`, `deliver second`, `late`) and the delta's bytes.
- It asserts C's exact text from C:729 `if turns[1] != 0:`.
- RED under m7 (`1 failed, 205 passed in 115.78s`) and M13 (`1 failed, 205 passed in 118.18s`), each a scratch copy of R
  through the whole T2. GREEN on the landed R (baseline `206 passed`).
- B9's m7 test T2@c269263:2966 `def test_replay_mutant_wait_removed_case_a_still_passes` asserted the hollow PASS; it is
  removed and this test replaces it.

**R2 (B-2) — DONE.**
- Test: T2:3170 `def test_replay_mid_line_snapshot_first_plus_delta_equals_final` now also asserts the cut:
- T2:3181 `first_last_byte=10`, and the snapshot's size equals the complete lines' byte count.
- `_b9_boundary` (T2:3113 `def _b9_boundary`) prints both.
- RED under R-level m6 (R:119's `p=d.rfind(b"\n")` cut replaced by `print(len(d))`): `1 failed, 205 passed in 123.94s`.
  GREEN on the landed R.
- m1-m7 were re-measured against R itself: see the MUTATION TABLE and R9.

**R3 (F-1, D-036 clause 2) — DONE.**
- C:738 `def _check_duplicate_receipt` has one refusal per field:
  - C:751 `if type(status) is not int or status != 200:`
  - C:755 `if delivery["accepted"] is not True:`
  - C:760 `if delivery["event_id_echoed"] is not True:`
  - C:765 `if delivery["event_id"] != first_id:` (the first-delivery binding)
  - C:771 `if delivery["message"] != row["observable"]:` (exact, taken from the oracle)
  - C:781 `if extra:` (no other denial observable may sit beside the receipt)
- The buzz-acp drop line is optional: C:786 `return dind_key in found` feeds the PASS line's `present|absent`.
- The oracle row now names the relay as the decider:
  - O:132 `"decided_by": "buzz-relay",`
  - O:134 `"line": 3196,`
  - O:135 `"src_pattern": 'message: "duplicate:".into(),'`
  - O:137 `"observable": "duplicate:",`
  - O:162 `"defense_in_depth": {` keeps the buzz-acp line as its defense-in-depth field.
- The six-key gate is unchanged at C:859 `if len(set(keys)) != len(distinct_legs):`.
- Tests:
  - T2:1214 `def test_replay_duplicate_receipt_fields_each_have_a_named_refusal` (6 cases: 400, True, False, 'true', echoed
    False, `duplicate: already processed`).
  - T2:1225 `def test_replay_duplicate_receipt_must_name_the_first_delivery`.
  - T2:1236 `def test_replay_forwarded_duplicate_fails_even_when_buzz_acp_dropped_it`.
  - T2:1250 `def test_replay_drop_line_is_recorded_when_present_and_never_required`.
  - T2:1260 `def test_replay_other_denial_observables_beside_the_receipt_fail`.
  - Upstream pin: T2:345 `def test_oracle_replay_defense_in_depth_line_is_pinned_too`.
  - Upstream pin: T2:356 `def test_replay_row_is_the_relay_duplicate_receipt`.
  - Upstream pin: T2:324 `def test_oracle_row_line_still_carries_its_pattern` (its `neg-replayed` case now pins the new row).

**R4 (F-2, D-036 clause 3) — DONE.**
- The mechanism is above.
- Tests:
  - T2:1296 `def test_replay_second_delta_from_a_restarted_process_fails` (6 cases, including B9's case A and VERIFY-B9's h1a).
  - T2:1305 `def test_replay_continuing_delta_passes` (the positive control: seq 5 continues to 6, 7).
  - T2:1315 `def test_replay_two_masked_logs_are_a_second_process`.
  - T2:1326 `def test_replay_log_must_show_exactly_one_buzz_acp_start` (0 and 2 starts).
  - T2:716 `def test_process_start_banner_is_buzz_acp_s_single_entry_point_line` (one emit site in the whole buzz-acp crate).
  - T2:3407 `def test_replay_runner_restarted_process_is_refused` (through the real runner).

**R5 (F-5, F-6, F-12) — DONE.**
- M11: T2:3361 `def test_replay_first_delivery_that_turns_only_after_the_duplicate_fails`.
  It asserts the text of C:724 `if turns[0] != 1:`. M11 reads `3 failed, 203 passed in 123.48s`.
- cm1: T2:1178 `def test_replay_same_content_new_event_id_fails_on_the_id_check` uses the same content with a NEW id,
  signed by `builder._bundle_privkey("pass", "owner")`. It is refused at C:719 `if ids[0] != ids[1]:`, never earlier.
  cm1 reads `1 failed, 205 passed in 125.99s`.
- M14: T2:3376 `def test_replay_slow_first_turn_is_waited_for_before_the_snapshot`. M14 reads `1 failed, 205 passed in 121.57s`.

**R6 (F-7) — DONE.**
- Harness:
  - Each delivery's receipt is D's REAL `_normalise` over the pinned relay's 200 body: T2:2878 `def _b9_receipt`.
  - The masked log is ONE process's, built in the test: T2:2797 `B9_ONE_PROCESS_LOG = (`.
  - Nothing is copied from the synthetic second sub-leg. The driver is T2:2950 `_B9_DRIVER = r'''`.
- PASS cases:
  - T2:3000 `def test_replay_integration_runner_producer_into_real_checker` (case A: a continuing, NON-empty delta; the first
    turn's terminal frames land after the boundary).
  - T2:3045 `def test_replay_integration_empty_delta_second_timeline_passes` (case B: D-036's empty delta).
- FAIL case: T2:3389 `def test_replay_runner_forwarded_duplicate_is_refused_on_the_receipt` (the old synthetic shape: the
  :2387 line with a `""` receipt; R3's message text).

**R7 — DONE.**
- `proofs/S0-02/tools/build_fixtures.py:468` `message=BLANKET_MESSAGE if blanket else "duplicate:"` sets the second
  receipt. It is built through the real `_normalise`, as before.
- `proofs/S0-02/tools/build_fixtures.py:514` `(second_dir / "timeline.jsonl").write_text("")` writes the empty delta.
- `proofs/S0-02/tools/build_fixtures.py:516` `(leg("neg-replayed") / "first" / "buzzacp.log").read_bytes())` puts the one
  log in both sub-legs.
- `proofs/S0-02/fixtures/PROVENANCE.md:16` `The replay leg` is the new replay paragraph. It is labelled synthetic and says
  that no live capture has shown the shape.
- The regeneration and the CLI verdicts are pasted below.

**R8 (F-13) — DONE.**
- C:471 `def _load_timeline` wraps `_load_timeline_raw` and turns `JSONDecodeError` / `UnicodeDecodeError` into a named
  `Failure`. S0-01's reader is untouched.
- C:488 `entries = _load_timeline(leg_dir, leg)` routes every leg through it.
- Test: T2:1348 `def test_a_torn_timeline_record_is_a_named_cli_failure` runs the CLI, rc 1, one `failure_reason:` line and
  no traceback. It has 3 cases: torn JSON in the replay's second sub-leg, a torn UTF-8 sequence there, and torn JSON in
  `pos-allowed`.
- cw1 (the wrapper removed) reads `3 failed, 203 passed in 122.24s`.

**R9 (F-10, F-11) — DONE.** Each correction is in place, marked `Corrected by B9-R1 (2026-09-23)`, with its measurement:
- `tasks/briefs/s0-02-support/B9-report.md:35` `Corrected by B9-R1` (the "no checker change is needed" claim).
- `tasks/briefs/s0-02-support/B9-report.md:46` `Corrected by B9-R1` (m1's named killer).
- `tasks/briefs/s0-02-support/B9-report.md:48` `Corrected by B9-R1` (m3's named killer).
- `tasks/briefs/s0-02-support/B9-report.md:49` `Corrected by B9-R1` (m4's named killer).
- `tasks/briefs/s0-02-support/B9-report.md:50` `Corrected by B9-R1` (m5's named killer).
- `tasks/briefs/s0-02-support/B9-report.md:51` `Corrected by B9-R1` (m6's false KILLED).
- `tasks/briefs/s0-02-support/B9-report.md:52` `Corrected by B9-R1` (m7's false EQUIVALENT).
- m2's row was correct (re-measured: killed by the source pin, 6a and `test_replay_mutant_no_prefix_proof_still_writes_second`),
  so it is not marked.

## RED ON THE PIN BYTES, THEN GREEN

The RED venue was a scratch tree at c269263 (`git archive` of proofs/S0-01, proofs/S0-02, proofs/schemas, T2, conftest,
pyproject) with ONLY the new T2 copied in. The PIN's C, O, R, D, builder, fixtures and spec were in place:

````
$ sha256sum (in the PIN tree)
6bc4729839495148  proofs/S0-02/check_buzz_authz.py
a3c31dbda859a635  proofs/S0-02/oracle/denial_table.py
bc9df748bf30f20a  tests/test_s0_02_buzz_authz.py
$ S0_01_VENUE=sandbox ... bash scripts/test_summary.sh tests/test_s0_02_buzz_authz.py --basetemp /tmp/b9r1/bt-pin --junitxml ...
pytest-exit: 1
pytest-summary: 35 failed, 171 passed in 120.66s (0:02:00)
FAILED test_oracle_replay_defense_in_depth_line_is_pinned_too :: KeyError: 'defense_in_depth'
FAILED test_replay_row_is_the_relay_duplicate_receipt :: AssertionError: assert ('buzz-acp', ... for channel') == ('buzz-relay'... 'duplicate:')
FAILED test_process_start_banner_is_buzz_acp_s_single_entry_point_line :: AttributeError: module 's0_02_check_buzz_authz' has no attribute 'PROCESS_START_BANNER'
FAILED test_pass_bundle_passes :: AssertionError: PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, 6 distinct reasons; +1 revocation leg ...
FAILED test_replay_duplicate_receipt_fields_each_have_a_named_refusal[http_status=400] :: ... + neg-replayed/second: delivery.json http_statu[s must be 200 ...]
FAILED test_replay_duplicate_receipt_fields_each_have_a_named_refusal[http_status=True] :: ... + neg-replayed/second: delivery.json http_stat[us is not an int]
FAILED test_replay_duplicate_receipt_fields_each_have_a_named_refusal[accepted=False] :: ... + neg-replayed/second: buzz-acp decid[es this leg ...]
FAILED test_replay_duplicate_receipt_fields_each_have_a_named_refusal[accepted='true'] :: ... + neg-replayed/second: delivery.json accepted is not [a bool]
FAILED test_replay_duplicate_receipt_fields_each_have_a_named_refusal[event_id_echoed=False] :: ... + neg-replayed/second: de[livery.json event_id_echoed ...]
FAILED test_replay_duplicate_receipt_fields_each_have_a_named_refusal[message='duplicate: already processed'] :: Failed: DID NOT RAISE Failure
FAILED test_replay_duplicate_receipt_must_name_the_first_delivery :: AssertionError: assert 'neg-replayed... 226e96aeff61' == 'neg-replayed...o this replay'
FAILED test_replay_forwarded_duplicate_fails_even_when_buzz_acp_dropped_it :: Failed: DID NOT RAISE Failure
FAILED test_replay_drop_line_is_recorded_when_present_and_never_required :: AssertionError: PASS: S0-02 buzz-authz - 1 positive, ... (no replay segment)
FAILED test_replay_other_denial_observables_beside_the_receipt_fail :: ... + neg-replayed/sec[ond: evidence carries 2 denial observables ...]
FAILED test_replay_second_delta_from_a_restarted_process_fails[initialize-continuing-seq] :: Failed: DID NOT RAISE Failure
FAILED test_replay_second_delta_from_a_restarted_process_fails[b9-case-A-restart] :: Failed: DID NOT RAISE Failure
FAILED test_replay_second_delta_from_a_restarted_process_fails[h1a-restart-with-session] :: Failed: DID NOT RAISE Failure
FAILED test_replay_second_delta_from_a_restarted_process_fails[seq-restart-without-initialize] :: Failed: DID NOT RAISE Failure
FAILED test_replay_second_delta_from_a_restarted_process_fails[seq-gap] :: Failed: DID NOT RAISE Failure
FAILED test_replay_second_delta_from_a_restarted_process_fails[seq-not-an-int] :: Failed: DID NOT RAISE Failure
FAILED test_replay_two_masked_logs_are_a_second_process :: Failed: DID NOT RAISE Failure
FAILED test_replay_log_must_show_exactly_one_buzz_acp_start[0] :: AttributeError: ... no attribute 'PROCESS_START_BANNER'
FAILED test_replay_log_must_show_exactly_one_buzz_acp_start[2] :: AttributeError: ... no attribute 'PROCESS_START_BANNER'
FAILED test_a_torn_timeline_record_is_a_named_cli_failure[replay-second-json] :: AssertionError: Traceback (most recent call last): ...
FAILED test_a_torn_timeline_record_is_a_named_cli_failure[replay-second-utf8] :: AssertionError: Traceback (most recent call last): ...
FAILED test_a_torn_timeline_record_is_a_named_cli_failure[pos-allowed-json] :: AssertionError: Traceback (most recent call last): ...
FAILED test_replay_integration_runner_producer_into_real_checker :: Failure: neg-replayed/second: neither delivery.json nor buzzacp.log carries ANY known denial observable — the leg produced no turn and no named reason
FAILED test_replay_integration_empty_delta_second_timeline_passes :: Failure: neg-replayed/second: neither delivery.json nor buzzacp.log carries ANY known denial observable — ...
FAILED test_replay_integration_pin_runner_reproduces_the_failure :: AssertionError: neg-replayed/second: neither delivery.json nor buzzacp.log carries ANY known denial observable ...
FAILED test_replay_mutant_cumulative_second_is_rejected :: AssertionError: neg-replayed/second: neither delivery.json nor buzzacp.log carries ANY known denial observable ...
FAILED test_replay_observation_window_catches_a_late_second_turn :: ... + neg-replayed/second: neither deliver[y.json nor buzzacp.log ...]
FAILED test_replay_first_delivery_that_turns_only_after_the_duplicate_fails :: ... + neg-r[eplayed/second: neither delivery.json ...]
FAILED test_replay_slow_first_turn_is_waited_for_before_the_snapshot :: assert 'neg-replayed... named reason' == 'PASS: S0-02 ...cation proof)'
FAILED test_replay_runner_forwarded_duplicate_is_refused_on_the_receipt :: assert 'PASS: S0-02 ...cation proof)' == 'neg-replayed...p dropped it)'
FAILED test_replay_runner_restarted_process_is_refused :: assert 'neg-replayed... named reason' == 'neg-replayed...036 clause 3)'
````
(Bracketed tails are the ends of lines pytest had truncated; nothing else is edited.)

How to read the PIN run:
- R3, R4, R6, R7 and R8 are RED for the exact missing mechanism.
- The runner cases that stay inside one process (R1, M11, M14, the integration cases) are RED on the PIN for F-1's reason:
  the PIN checker refuses D-036's receipt with `neither delivery.json nor buzzacp.log carries ANY known denial observable`.
- GREEN on the PIN, as expected, because the PIN's production code already did the right thing and only the test was
  missing. Their red proof is the named mutant:
  - `test_replay_mid_line_snapshot_first_plus_delta_equals_final` (R2): R's cut was right; killed by m6.
  - `test_replay_same_content_new_event_id_fails_on_the_id_check` (R5, cm1): the id check existed but no test
    discriminated it; killed by cm1.
  - The positive control `test_replay_continuing_delta_passes`.

GREEN (this tree, the brief's gate, twice): see GATES.

## MUTATION TABLE

Venue:
- One scratch tree per row under `/tmp/b9r1/mt-<id>` (proofs/S0-01, proofs/S0-02, proofs/schemas, T2, conftest and
  pyproject taken from the WORKING tree).
- A fresh `git init` borrows the repo's objects read-only, so T2's `git show 71463f3:…` resolves.
- Each row applies ONE exact-string mutation (the anchor must match once: `EXPECTED=26 OK=26` in the dry check; a broken
  anchor is refused by the driver's self-test).
- Each row is then compiled (`bash -n` / `py_compile`), collected (`--collect-only`), and run through the WHOLE T2 via
  `scripts/test_summary.sh` with a JUnit XML. Afterwards its tree and basetemp are deleted.
- R-level rows mutate a scratch copy of R ITSELF, never a function override.

AF-AP-138: the unmutated baseline in the same venue reads `206 passed in 128.45s (0:02:08)` (collected 206, failed []).
Every killer below is in that baseline's passed set (`killers_in_baseline_passed=True` for all 26 rows).
AF-AP-78: every row has `compiles` rc 0 and `collected` 206.

| id | mutation | compiles | collected | whole-T2 result | killed-by |
|---|---|---|---|---|---|
| m1 | R:135 `tail -c +$((first_bytes + 1))` delta → `cp "$FD/timeline.jsonl"` (cumulative second) | 0 | 206 | `9 failed, 197 passed in 126.80s` | KILLED: the source pin, 6b, 6c, cases A and B, R1, R6-neg, the restart runner case, M14's test |
| m2 | R:130-133 `if ! cmp -n "$first_bytes"` prefix proof removed | 0 | 206 | `3 failed, 203 passed in 128.39s` | KILLED: the source pin, 6a, `test_replay_mutant_no_prefix_proof_still_writes_second` |
| m3 | R:135 `tail -c +$((first_bytes + 1))` → `tail -c +$first_bytes` | 0 | 206 | `10 failed, 196 passed in 118.05s` | KILLED: the source pin, 6b, 6c, cases A and B, R1, M11's test, M14's test, R6-neg, the restart runner case |
| m4 | R:305-306 `collect_masked "$out/first"` pair → `collect_masked "$out"` (root only) | 0 | 206 | `10 failed, 196 passed in 117.99s` | KILLED: the source pin, cases A and B, the m1 and m5 override tests, R1, M11's test, M14's test, R6-neg, the restart runner case |
| m5 | R:306 `collect_masked "$out/second"` removed | 0 | 206 | `9 failed, 197 passed in 119.14s` | KILLED: the source pin, cases A and B, the m1 override test, R1, M11's test, M14's test, R6-neg, the restart runner case |
| m6 | R:119 `p=d.rfind(b"\n"); print(p+1 if p>=0 else 0)` → `print(len(d))` | 0 | 206 | `1 failed, 205 passed in 123.94s` | KILLED: `test_replay_mid_line_snapshot_first_plus_delta_equals_final` (VERIFY-B9: SURVIVED) |
| m7 | R:241 `wait_turn_window 0` deleted | 0 | 206 | `1 failed, 205 passed in 115.78s` | KILLED: `test_replay_observation_window_catches_a_late_second_turn` (VERIFY-B9: SURVIVED) |
| M11 | R:231 `first_bytes=$(snapshot_timeline "$out")` moved below the `--t0 "$local_first_t0"` line | 0 | 206 | `3 failed, 203 passed in 123.48s` | KILLED: M11's test, case A, the restart runner case (VERIFY-B9: SURVIVED) |
| M13 | R:241 `wait_turn_window 0` → `wait_turn_window 1` | 0 | 206 | `1 failed, 205 passed in 118.18s` | KILLED: `test_replay_observation_window_catches_a_late_second_turn` (VERIFY-B9: SURVIVED) |
| M14 | R:227 `wait_turn_window 1` removed | 0 | 206 | `1 failed, 205 passed in 121.57s` | KILLED: `test_replay_slow_first_turn_is_waited_for_before_the_snapshot` (VERIFY-B9: SURVIVED) |
| cm1 | C:719 `if ids[0] != ids[1]:` → `if False:` | 0 | 206 | `1 failed, 205 passed in 125.99s` | KILLED: `test_replay_same_content_new_event_id_fails_on_the_id_check` (VERIFY-B9: SURVIVED) |
| cr1 | the receipt check removed: C:877 `replay_dind = _check_duplicate_receipt(found, delivery, replay_first_id)` → `replay_dind = False` | 0 | 206 | `11 failed, 195 passed in 167.78s` | KILLED: all six field cases, the first-id test, the forwarded-duplicate test (checker and runner), the drop-line-recorded test, the extras test |
| cr2 | C:771 `if delivery["message"] != row["observable"]:` loosened to `startswith("duplicate")` | 0 | 206 | `1 failed, 205 passed in 168.48s` | KILLED: the `message='duplicate: already processed'` field case |
| cr3 | C:760 `if delivery["event_id_echoed"] is not True:` → `if False:` (echoed-id check removed) | 0 | 206 | `1 failed, 205 passed in 166.65s` | KILLED: the `event_id_echoed=False` field case |
| cr4 | C:765 `if delivery["event_id"] != first_id:` → `if False:` (first-id binding removed) | 0 | 206 | `1 failed, 205 passed in 152.07s` | KILLED: `test_replay_duplicate_receipt_must_name_the_first_delivery` |
| cr5 | C:751 `if type(status) is not int or status != 200:` → `if False:` | 0 | 206 | `2 failed, 204 passed in 156.77s` | KILLED: the `http_status=400` and `http_status=True` cases |
| cr6 | C:755 `if delivery["accepted"] is not True:` → `if False:` | 0 | 206 | `2 failed, 204 passed in 157.07s` | KILLED: the `accepted=False` and `accepted='true'` cases |
| cr7 | C:781 `if extra:` (beside the receipt) → `if False:` | 0 | 206 | `1 failed, 205 passed in 123.58s` | KILLED: `test_replay_other_denial_observables_beside_the_receipt_fail` |
| cc1 | the continuity check removed: C:734 `_check_one_process(leg_dir, entries[0], entries[1])` deleted | 0 | 206 | `10 failed, 196 passed in 128.26s` | KILLED: all six restart cases, the two-logs test, both start-count cases, the restart runner case |
| cca | C:617 `if rec.get("dir") == "c2a"` (the initialize check) → `if False:` | 0 | 206 | `4 failed, 202 passed in 124.53s` | KILLED: three restart cases with `initialize`, the restart runner case |
| ccb | C:626 `if type(prev) is not int` (seq continuity) → `if False:` | 0 | 206 | `3 failed, 203 passed in 127.96s` | KILLED: seq-gap, seq-not-an-int, seq-restart-without-initialize |
| ccc | C:637 `if logs[0] != logs[1]:` → `if False:` | 0 | 206 | `1 failed, 205 passed in 128.02s` | KILLED: `test_replay_two_masked_logs_are_a_second_process` |
| ccd | C:645 `if starts != 1:` → `if False:` | 0 | 206 | `2 failed, 204 passed in 127.17s` | KILLED: both start-count cases (0 and 2) |
| cd1 | the :2387 line made required again: C:786 `return dind_key in found` → raise when absent | 0 | 206 | `13 failed, 193 passed in 124.35s` | KILLED: 13 tests, `test_pass_bundle_passes` and cases A and B among them (each needs a PASS without the drop line; the rest fail on the replay refusal firing before their own leg's text; full list in the APPENDIX) |
| cd2 | the drop line dropped from C:382 `ALL_OBSERVABLES = tuple(sorted(` (presence no longer recorded) | 0 | 206 | `3 failed, 203 passed in 120.88s` | KILLED: the drop-line-recorded test, the forwarded-duplicate test (checker and runner) |
| cw1 | the F-13 wrapper removed: C:488 `entries = _load_timeline(leg_dir, leg)` → `_load_timeline_raw` | 0 | 206 | `3 failed, 203 passed in 122.24s` | KILLED: all three torn-record CLI cases |

Tally: `EXPECTED=26 KILLED=26`, 0 SURVIVED, 0 EQUIVALENT (10 R-level, 16 C-level). Every full killer list is pasted
by value in the APPENDIX at the end.

## R7 — the regenerated committed bundles (run, never hand-edited)

````
$ python3 proofs/S0-02/tools/build_fixtures.py --write
wrote 8 fixtures to /home/user/agent-factory/proofs/S0-02/fixtures
$ python3 proofs/S0-02/tools/build_fixtures.py --bundles
wrote synthetic bundle /home/user/agent-factory/proofs/S0-02/fixtures/evidence-pass
wrote synthetic bundle /home/user/agent-factory/proofs/S0-02/fixtures/evidence-blanket
$ python3 proofs/S0-02/tools/build_fixtures.py --check
fixture-drift: none (8 fixtures match a fresh build)
$ git diff --stat -- proofs/S0-02/fixtures
 .../S0-02/fixtures/evidence-blanket/fixtures/neg-replayed.json   | 9 +++++----
 .../evidence-blanket/legs/neg-replayed/second/fixture.json       | 9 +++++----
 .../evidence-blanket/legs/neg-replayed/second/timeline.jsonl     | 2 --
 proofs/S0-02/fixtures/evidence-pass/fixtures/neg-replayed.json   | 9 +++++----
 .../fixtures/evidence-pass/legs/neg-replayed/second/buzzacp.log  | 1 -
 .../evidence-pass/legs/neg-replayed/second/delivery.json         | 2 +-
 .../fixtures/evidence-pass/legs/neg-replayed/second/fixture.json | 9 +++++----
 .../evidence-pass/legs/neg-replayed/second/timeline.jsonl        | 2 --
 proofs/S0-02/fixtures/neg-replayed.json                          | 9 +++++----
 9 files changed, 26 insertions(+), 26 deletions(-)
````
(The stat was taken before the PROVENANCE.md paragraph was added; that file is the tenth changed under `fixtures/`.)

- All nine changed files are replay-leg files. Every other leg's bytes are identical: none appears in the stat.
- `proofs/S0-02/fixtures/neg-replayed.json` (the top-level fixture, `--write`) changes because
  `proofs/S0-02/tools/build_fixtures.py:239` `"mechanism": f"{row['src']}:{row['line']}",` copies the oracle row into
  `expected`.
- The blanket bundle's replay leg changes too. Its second timeline was `_timeline(False)` (`initialize` at seq 1, a
  restart), which R4 now refuses before the gate.

## GATES (pasted)

````
$ mkdir -p /tmp/b9r1/bt && bash scripts/test_summary.sh tests/test_s0_02_buzz_authz.py --basetemp /tmp/b9r1/bt   (x2, rm -rf /tmp/b9r1/bt between; the FINAL tree)
run1 start 2026-09-23T10:07:55Z
pytest-exit: 0
pytest-summary: 206 passed in 124.25s (0:02:04)
run2 start 2026-09-23T10:10:00Z
pytest-exit: 0
pytest-summary: 206 passed in 124.12s (0:02:04)
(an earlier pair, before the last two edits — a comment-only fix in C, `pc_launch.py:400` to `:401`, and the new PROVENANCE
paragraph — read `206 passed in 121.68s (0:02:01)` and `206 passed in 121.81s (0:02:01)`; the mutation table ran on
that earlier tree, which differs from the final one only by those two non-executable edits)
$ python3 proofs/S0-02/tools/build_fixtures.py --check   (final tree)
fixture-drift: none (8 fixtures match a fresh build)
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_02_buzz_authz.py
1 files set=a5de0beef100
$ bash -n proofs/S0-02/tools/pc/run_s0_02_legs.sh
rc=0
$ sha256sum (R, D, spec unchanged) ; git status --porcelain -- proofs/S0-02/tools/pc proofs/S0-02/spec.json proofs/S0-01 .github scripts .claude
93bf0cf987f9d4a0  proofs/S0-02/tools/pc/run_s0_02_legs.sh
9fdf8f3a87fa96b3  proofs/S0-02/tools/pc/deliver_event.py
7cc99c9599727ae3  proofs/S0-02/spec.json
(empty status: every read-only path untouched)
$ /root/venv-agent-factory/bin/python -m pyflakes proofs/S0-02/check_buzz_authz.py proofs/S0-02/oracle/denial_table.py proofs/S0-02/tools/build_fixtures.py tests/test_s0_02_buzz_authz.py
rc=0
$ python3 scripts/ap_screen.py proofs/S0-02/check_buzz_authz.py
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---
$ python3 scripts/ap_screen.py --tests tests/test_s0_02_buzz_authz.py
--- TEST_SCREEN over 1 path(s): 11 hits over 1 files ---
AF-AP-80: 7   (lines 769, 770, 1087, 1915, 1916, 1948, 1971)
AF-AP-34: 4   (lines 1979 x2, 1983 x2)
$ git blame (first commit of each hit line): 769/770 91e33f28 · 1087 f737de55 · 1915/1916/1948/1971/1979/1983 088efef2
(all pre-existing, the same 11 VERIFY-B9 I-9 listed at their old lines; 0 new hits. One new hit appeared during the
build, on a `"…" not in log` assertion; it was replaced by an exact equality on the produced log.)
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 39 files scanned, clean
$ git diff --check -- proofs/S0-02 tests/test_s0_02_buzz_authz.py
rc=0
$ python3 proofs/S0-02/check_buzz_authz.py --synthetic-root proofs/S0-02/fixtures/evidence-pass proofs/S0-02/fixtures/evidence-pass/legs
PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, 6 distinct reasons; replay refused by the relay's duplicate: receipt (buzz-acp drop line absent, defense-in-depth only); +1 revocation leg (assertion 2); removal evidence: coordinator-supplied receipt (unauthenticated; ordering and fields verified; not an end-to-end revocation proof)
rc=0
$ python3 proofs/S0-02/check_buzz_authz.py --synthetic-root proofs/S0-02/fixtures/evidence-blanket proofs/S0-02/fixtures/evidence-blanket/legs   (spec.json's negative leg)
failure_reason: blanket-rejection: reasons ['delivery::restricted: not a channel member'] not distinct — 6 negative legs collapsed to 1 observable(s)
rc=1
$ CLI over the old synthetic replay shape, two forms:
--- (1) the PIN's committed replay evidence files (timeline, log, delivery, event, t0 from c269263; fixture.json kept current):
failure_reason: neg-replayed/second: the delta holds an ACP initialize frame (seq 1) — the agent restarted: a second process, not ONE continuous buzz-acp process (D-036 clause 3)
rc=1
--- (2) one process + the :2387 line + a non-duplicate: receipt (the brief's definition of the old shape):
failure_reason: neg-replayed/second: the relay receipt message is '', expected exactly 'duplicate:' — the relay did not refuse the second delivery as a duplicate (a forwarded duplicate fails even when buzz-acp dropped it)
rc=1
````

## DISCREPANCIES AND DEVIATIONS (flagged loudly)

1. **DEVIATION — where clause 2 is graded.** The brief put R3 "next to C@c269263:599 `delivery = _check_delivery(`". The
   receipt is graded after the distinctness gate instead, because read-only `spec.json` pins the blanket bundle's exact
   `blanket-rejection:` text (Design decision 1). Every R3 behavior the brief lists holds and is tested; only the
   position moved.
2. **DEVIATION — the O module docstring.** The brief scopes O to "the `neg-replayed` row ONLY". The docstring's claim
   "buzz-acp decides REPLAY" became false with the row change. My standing contract is to fix a comment my change
   falsifies, so the docstring was corrected: `proofs/S0-02/oracle/denial_table.py:20` `Since D-036 the relay also`. No
   other O row changed. Revert it if the coordinator holds the brief's scope literally.
3. **DEVIATION — the PASS line changed.** A replay segment was added before `+1 revocation leg` to RECORD the drop line
   (R3 "its presence is recorded"). The prefix up to `6 distinct reasons;` is unchanged, and the line still ends with the
   removal note. Two T2 pins were updated: `test_pass_bundle_passes` and `B9_PASS_LINE`. spec.json pins only the
   positive leg's exit code.
4. **DISCREPANCY — "the old synthetic replay shape".** The LITERAL PIN evidence (a restart at seq 1, two different logs, a
   `""` receipt, the :2387 line) is refused FIRST by clause 3, with the initialize text in form (1) above. R3's text
   appears when the timeline and log are one-process. That is the brief's own parenthetical ("the :2387 line with a
   non-`duplicate:` receipt"): form (2) above, and T2:3389 `def test_replay_runner_forwarded_duplicate_is_refused_on_the_receipt`.
5. **DISCREPANCY — PROVENANCE.md had no replay paragraph at the PIN** (only a mention in its gate-logic list). R7's
   paragraph is NEW: `proofs/S0-02/fixtures/PROVENANCE.md:16` `The replay leg`.
6. **CONSEQUENCE — the top-level fixture changed.** `proofs/S0-02/fixtures/neg-replayed.json` is regenerated by the same
   builder (`--write`), because it embeds the oracle row. It is under `proofs/S0-02/fixtures/`, and the brief's boundary
   names "the committed bundles … that `build_fixtures.py` regenerates". I read the boundary as covering it; flagged in
   case the coordinator reads "bundles" narrowly.
7. **"RED on the PIN bytes" for R2 and R5-cm1.** These tests are GREEN on the PIN, because the PIN's production code was
   already right and only a discriminating test was missing. Their red proof is the named mutant (m6, cm1): killed, whole
   T2, pasted above.
8. **The m7/M13 kill needs `POLL_S` set after the source.** VERIFY-B9 I-4 (R:35 `POLL_S=5` and R:33 `FD=$MARKERS/v2-$HOST_LEG`
   overwrite the caller's env) is honored in the driver (T2:2958 `POLL_S=$B9_POLL_S`). The old `"POLL_S": "0.05"` env
   entry, which never took effect, was removed from `_b9_env`.
9. **Two T2 tests that VERIFY-B9 graded were re-pointed.** `test_replay_integration_pin_runner_reproduces_the_failure` and
   `test_replay_mutant_cumulative_second_is_rejected` now run on D-036-shaped evidence through the new harness. Their
   asserted texts (the closure text below, and C@c269263:621 `if turns[1] != 0:`) are unchanged. The m2/m3 override
   tests now append `B9_DELTA` (T2:2805 `B9_DELTA = "".join(`), because the regenerated second timeline is empty.
   The closure text they keep asserting is C@c269263:569 `if {p.name for p in leg_dir.iterdir()} != set(REPLAY_SUBLEGS):`.

## NOT-DONE (first-class)

- **No live capture, no PC, no bridge, no relay, no real launcher, no real `pc_post.sh`, no host secret.** Every runner
  test uses labelled doubles and the closed URL `http://127.0.0.1:1`. The D-036 live shape (the relay answers `duplicate:`
  BEFORE dispatch, so buzz-acp never sees the duplicate) is INFERRED from pinned source (`ingest.rs` lines 3192-3197 and
  3258, commit `1c8321cd`). It is NOT observed. The fresh eight-leg capture is the coordinator's.
- **F-3** (the boundary follows the first prompt REQUEST, not the terminal result), **F-4** (the final timeline is read
  while buzz-acp still runs, and the delta is not cut at a newline), **F-8** (failures inside `snapshot_timeline` surface
  as a misnamed rc 8) and **F-9** (no EXIT/ERR trap, so an rc-8 abort orphans buzz-acp): NOT in this round. They stay
  follow-ups; R is unchanged by brief.
- **Case A now passes WITH a non-empty delta.** Under F-3 a slow turn's terminal frames land in the delta. R4 accepts that
  (seq continues), so an "empty delta" rule is NOT imposed. This is consistent with deferring F-3.
- The PC-venue suite was not run; the sandbox runs the whole file (206) because the declared inputs are present here.
  shellcheck is not installed here (VERIFY-B9 measured `which shellcheck` → none).
- `/bug-echo` and the anti-pattern registry entry for F-13's class (a reused parser that raises a non-`Failure` exception
  past a CLI exit contract) are NOT done. `docs/INCIDENT-LOG.md` is outside this lane's boundary. The coordinator owns the
  echo.
- **Sibling seen, not fixed (adjacent, same class):**
  - C:184 `def _prompt_frames` calls `.get` on every timeline record and on its `frame`. A valid-JSON record that is not
    an object (a bare number or a list) still raises AttributeError, a traceback past the exit contract.
  - `_observe_all` reads `buzzacp.log` with `read_text()`, so a non-UTF-8 log still raises UnicodeDecodeError.
  - The real producer (the tee, `json.dumps(entry)`; the mask) cannot write either shape; only tampering can. REPORTED,
    not fixed.
- The first delivery's receipt is not required to be a NEW acceptance (message `""`). The brief does not ask for it, and
  the fresh per-leg launch plus clause 4 make it low-risk. INFO only.

## SELF-ATTACK — the three most likely ways this change is wrong

1. **The blanket bundle stops reaching the distinctness gate, so spec.json's negative leg breaks.** Ruled out: the CLI over
   the regenerated blanket bundle prints spec.json's exact `failure_reason` (pasted), and
   T2:817 `def test_spec_negative_leg_reason_is_the_exact_observed_line` is green in both gate runs.
2. **The continuity check refuses a legitimate one-process capture** (a second `session/new`, a turn's late frames).
   Ruled out: the rule came from six real timelines. `two-users` has a second `session/new` inside ONE process, and the
   rule does not refuse `session/new`. The late-frames shape passes in T2:1305 `def test_replay_continuing_delta_passes`
   and in case A through the real runner. Residual risk: a live timeline with a tee write error has a real seq gap (the
   tee's `_record_write_error` skips a line after `seq` was taken). That refuses as "a second process": fail-closed, with
   a slightly misnamed cause.
3. **The receipt check is a mirror of the fixture I also built.** Ruled out:
   - The bundle's `duplicate:` is a builder literal tied to the relay's source (`ingest.rs` line 3196), not taken from the
     oracle.
   - The oracle row is pinned to that upstream line by T2:356 `def test_replay_row_is_the_relay_duplicate_receipt` (a
     six-line block match) and T2:324 `def test_oracle_row_line_still_carries_its_pattern`.
   - The runner cases build their receipts with D's REAL `_normalise` over the relay's response body, not from any fixture.
   - Each field's check is killed by its own mutant (cr2-cr6).

## RETRO

- Lesson (for anti-hollow-green, the coordinator's to bake): a new named check that must sit before a cross-leg gate can
  collide with a PINNED negative-control text further down the pipeline. Here, spec.json's exact blanket-rejection
  reason. Before placing a per-leg check, run the pinned negative leg's CLI once; a red there is a placement bug, not a
  proof failure.
- Lint (`python3 scripts/report_lint.py --min-refs 15 --map R=… --map C=… --map T2=… --map O=… B9-R1-report.md --root .`),
  two rounds of `fix:` hints:
  round 1 `report_lint: 151 refs — OK 144, NEAR 1, MISS 6, UNCHECKABLE 0, UNRESOLVED 0 (worktree)` (the NEAR was a real
  off-by-one, `pc_launch.py:400` for `:401`, also in C's comment, both fixed);
  round 2 `report_lint: 150 refs — OK 150, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)` (rc 0).


## APPENDIX — every killer, by value (from the driver's JUnit XML; the scratch files are deleted)

````
m1 (9): test_pc_runner_replay_window_and_nip98_guard_are_pinned, test_replay_empty_delta_writes_zero_byte_second, test_replay_integration_empty_delta_second_timeline_passes, test_replay_integration_runner_producer_into_real_checker, test_replay_mid_line_snapshot_first_plus_delta_equals_final, test_replay_observation_window_catches_a_late_second_turn, test_replay_runner_forwarded_duplicate_is_refused_on_the_receipt, test_replay_runner_restarted_process_is_refused, test_replay_slow_first_turn_is_waited_for_before_the_snapshot
m2 (3): test_pc_runner_replay_window_and_nip98_guard_are_pinned, test_replay_mutant_no_prefix_proof_still_writes_second, test_replay_prefix_proof_refuses_a_non_extension
m3 (10): test_pc_runner_replay_window_and_nip98_guard_are_pinned, test_replay_empty_delta_writes_zero_byte_second, test_replay_first_delivery_that_turns_only_after_the_duplicate_fails, test_replay_integration_empty_delta_second_timeline_passes, test_replay_integration_runner_producer_into_real_checker, test_replay_mid_line_snapshot_first_plus_delta_equals_final, test_replay_observation_window_catches_a_late_second_turn, test_replay_runner_forwarded_duplicate_is_refused_on_the_receipt, test_replay_runner_restarted_process_is_refused, test_replay_slow_first_turn_is_waited_for_before_the_snapshot
m4 (10): test_pc_runner_replay_window_and_nip98_guard_are_pinned, test_replay_first_delivery_that_turns_only_after_the_duplicate_fails, test_replay_integration_empty_delta_second_timeline_passes, test_replay_integration_runner_producer_into_real_checker, test_replay_mutant_cumulative_second_is_rejected, test_replay_mutant_masked_log_first_only_fails_second_closure, test_replay_observation_window_catches_a_late_second_turn, test_replay_runner_forwarded_duplicate_is_refused_on_the_receipt, test_replay_runner_restarted_process_is_refused, test_replay_slow_first_turn_is_waited_for_before_the_snapshot
m5 (9): test_pc_runner_replay_window_and_nip98_guard_are_pinned, test_replay_first_delivery_that_turns_only_after_the_duplicate_fails, test_replay_integration_empty_delta_second_timeline_passes, test_replay_integration_runner_producer_into_real_checker, test_replay_mutant_cumulative_second_is_rejected, test_replay_observation_window_catches_a_late_second_turn, test_replay_runner_forwarded_duplicate_is_refused_on_the_receipt, test_replay_runner_restarted_process_is_refused, test_replay_slow_first_turn_is_waited_for_before_the_snapshot
m6 (1): test_replay_mid_line_snapshot_first_plus_delta_equals_final
m7 (1): test_replay_observation_window_catches_a_late_second_turn
M11 (3): test_replay_first_delivery_that_turns_only_after_the_duplicate_fails, test_replay_integration_runner_producer_into_real_checker, test_replay_runner_restarted_process_is_refused
M13 (1): test_replay_observation_window_catches_a_late_second_turn
M14 (1): test_replay_slow_first_turn_is_waited_for_before_the_snapshot
cm1 (1): test_replay_same_content_new_event_id_fails_on_the_id_check
cr1 (11): test_replay_drop_line_is_recorded_when_present_and_never_required, test_replay_duplicate_receipt_fields_each_have_a_named_refusal[accepted='true'], test_replay_duplicate_receipt_fields_each_have_a_named_refusal[accepted=False], test_replay_duplicate_receipt_fields_each_have_a_named_refusal[event_id_echoed=False], test_replay_duplicate_receipt_fields_each_have_a_named_refusal[http_status=400], test_replay_duplicate_receipt_fields_each_have_a_named_refusal[http_status=True], test_replay_duplicate_receipt_fields_each_have_a_named_refusal[message='duplicate: already processed'], test_replay_duplicate_receipt_must_name_the_first_delivery, test_replay_forwarded_duplicate_fails_even_when_buzz_acp_dropped_it, test_replay_other_denial_observables_beside_the_receipt_fail, test_replay_runner_forwarded_duplicate_is_refused_on_the_receipt
cr2 (1): test_replay_duplicate_receipt_fields_each_have_a_named_refusal[message='duplicate: already processed']
cr3 (1): test_replay_duplicate_receipt_fields_each_have_a_named_refusal[event_id_echoed=False]
cr4 (1): test_replay_duplicate_receipt_must_name_the_first_delivery
cr5 (2): test_replay_duplicate_receipt_fields_each_have_a_named_refusal[http_status=400], test_replay_duplicate_receipt_fields_each_have_a_named_refusal[http_status=True]
cr6 (2): test_replay_duplicate_receipt_fields_each_have_a_named_refusal[accepted='true'], test_replay_duplicate_receipt_fields_each_have_a_named_refusal[accepted=False]
cr7 (1): test_replay_other_denial_observables_beside_the_receipt_fail
cc1 (10): test_replay_log_must_show_exactly_one_buzz_acp_start[0], test_replay_log_must_show_exactly_one_buzz_acp_start[2], test_replay_runner_restarted_process_is_refused, test_replay_second_delta_from_a_restarted_process_fails[b9-case-A-restart], test_replay_second_delta_from_a_restarted_process_fails[h1a-restart-with-session], test_replay_second_delta_from_a_restarted_process_fails[initialize-continuing-seq], test_replay_second_delta_from_a_restarted_process_fails[seq-gap], test_replay_second_delta_from_a_restarted_process_fails[seq-not-an-int], test_replay_second_delta_from_a_restarted_process_fails[seq-restart-without-initialize], test_replay_two_masked_logs_are_a_second_process
cca (4): test_replay_runner_restarted_process_is_refused, test_replay_second_delta_from_a_restarted_process_fails[b9-case-A-restart], test_replay_second_delta_from_a_restarted_process_fails[h1a-restart-with-session], test_replay_second_delta_from_a_restarted_process_fails[initialize-continuing-seq]
ccb (3): test_replay_second_delta_from_a_restarted_process_fails[seq-gap], test_replay_second_delta_from_a_restarted_process_fails[seq-not-an-int], test_replay_second_delta_from_a_restarted_process_fails[seq-restart-without-initialize]
ccc (1): test_replay_two_masked_logs_are_a_second_process
ccd (2): test_replay_log_must_show_exactly_one_buzz_acp_start[0], test_replay_log_must_show_exactly_one_buzz_acp_start[2]
cd1 (13): test_a_buzz_acp_leg_showing_only_a_relay_reason_fails_the_named_check, test_a_leg_with_two_denial_observables_is_not_counted_as_a_distinct_reason, test_pass_bundle_passes, test_relay_decided_leg_needs_no_debug_canary, test_removal_receipt_is_labelled_coordinator_supplied_in_checker_output, test_removal_summary_uses_only_the_revoked_leg_note, test_replay_continuing_delta_passes, test_replay_drop_line_is_recorded_when_present_and_never_required, test_replay_integration_empty_delta_second_timeline_passes, test_replay_integration_runner_producer_into_real_checker, test_replay_second_subleg_uses_only_the_wider_replay_tolerance, test_replay_slow_first_turn_is_waited_for_before_the_snapshot, test_wrong_channel_observables_are_rejected
cd2 (3): test_replay_drop_line_is_recorded_when_present_and_never_required, test_replay_forwarded_duplicate_fails_even_when_buzz_acp_dropped_it, test_replay_runner_forwarded_duplicate_is_refused_on_the_receipt
cw1 (3): test_a_torn_timeline_record_is_a_named_cli_failure[pos-allowed-json], test_a_torn_timeline_record_is_a_named_cli_failure[replay-second-json], test_a_torn_timeline_record_is_a_named_cli_failure[replay-second-utf8]
````
