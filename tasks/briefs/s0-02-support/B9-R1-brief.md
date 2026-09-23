# B9-R1 — the ONE focused repair of VERIFY-B9 (S0-02's replay leg), with D-036's live oracle made the checker's (task #168)

PIN: c269263 (origin head at authoring; every S0-02 file is byte-identical to the B9 landing 221e68b, measured in the premise block).
LANE: s0-02-b9-r1 (sandbox; agent `code-implementer`, in the SHARED tree, no worktree isolation). Venue: the PC's local route is at its
four-lane ceiling and stalling (K1-h's first attempt died on a 120 s stream stall at 07:25Z; the vLLM KV cache read 85 % at 08:12Z), and
the S0-02 test file passes whole in this sandbox through `scripts/test_summary.sh` (premise). Honey `ultra` Lever-2: your report is DATA:
files:lines, pasted counts, discrepancies, NOT-done. Do NOT spawn subagents.

CONTRACT SOURCES (read them whole before you design): `tasks/briefs/pc/pc-b9.md` (the frozen B9 contract: issue #17's seven steps,
D-036's oracle, M-A and M-B) · `docs/08_DECISION_LOG.md` D-036 (verbatim: "the second delivery carries an IDENTICAL event id; its
receipt is the relay's `duplicate:` refusal, BOUND to that delivery; ONE continuous buzz-acp process spans both deliveries; ONE prompt
in total; ZERO prompts in the second delivery's delta; the synthetic Buzz-ACP replay guard stays as defense-in-depth, never the live
oracle" — and it REJECTED "a Buzz-ACP-level dedup as the oracle (that guard is synthetic — the relay is the real dedup point)") ·
`tasks/briefs/s0-02-support/VERIFY-B9-report.md` (§FINDINGS: B-1, B-2, F-1, F-2, F-5, F-6, F-7, F-10, F-11, F-12, F-13, each with its
fix line; §MUTATION TABLE; its probes are described there by value) · `tasks/briefs/s0-02-support/B9-report.md` (the claims you correct).

WHY THIS ROUND IS WIDER THAN THE TWO BLOCKERS (the coordinator's routing, D-031 + D-034): B-1 and B-2 meet the blocking predicate
inside B9's boundary. F-1 and F-2 are outside it (the checker was frozen for B9), but they are core-blocking for the S0-02 proof: the
landed checker keys the replay leg on the synthetic buzz-acp duplicate-drop line (the oracle row at `proofs/S0-02/oracle/denial_table.py:125-134`,
decided_by buzz-acp, relay.rs:2387) — the alternative D-036 rejected — so the live capture's replay leg is REFUSED on D-036's own shape
(VERIFY-B9 reproduced `neither delivery.json nor buzzacp.log carries ANY known denial observable`), and "ONE continuous process" is checked
nowhere. This is the ONE focused repair round for S0-02 at the D-036 contract revision; the runner R stays as landed (digest
93bf0cf987f9d4a0, VERIFY-B9: "R is correct as landed").

BOUNDARY (exact): MODIFY `tests/test_s0_02_buzz_authz.py` (T2), `proofs/S0-02/check_buzz_authz.py` (C), `proofs/S0-02/oracle/denial_table.py`
(the `neg-replayed` row ONLY), `proofs/S0-02/tools/build_fixtures.py` (the replay leg's construction ONLY), the committed bundles under
`proofs/S0-02/fixtures/` that `build_fixtures.py` regenerates (regenerate them by RUNNING it, never by hand), `proofs/S0-02/fixtures/PROVENANCE.md`
(the replay paragraph), `tasks/briefs/s0-02-support/B9-report.md` (corrections only, each marked `Corrected by B9-R1 (2026-09-23): …`);
CREATE `tasks/briefs/s0-02-support/B9-R1-report.md` (write it incrementally from the start). READ-ONLY: `proofs/S0-02/tools/pc/run_s0_02_legs.sh`
(R), `proofs/S0-02/tools/pc/deliver_event.py` (D), `proofs/S0-01/**` (S0-01 is minted and its tooling is ATTESTED — never touch it; F-13 is
fixed in C, not in S0-01's shared loader), `proofs/S0-02/spec.json`, `.github/`, `scripts/`, `.claude/`. A line you cannot meet without
another file is a DISCREPANCY, never a silent edit. Another sandbox agent may run in this tree on disjoint files (`tasks/briefs/hermes-repin/`,
`proofs/S0-05/`, `tests/test_s0_05_egress.py`, `tasks/briefs/s0-05-support/`) and one works in a private worktree under `/tmp/wt-ci166`:
never touch, run or revert them. Never run `git stash`, `git checkout -- …`, `git restore`, `git add`, `git commit` or `git push`. No
outward-facing action; no PC or bridge use; no live relay, launcher, harness server or host secret (every test uses the labelled doubles
and a closed loopback URL, as T2 does today). The sandbox has about 1.9 GB free: every pytest `--basetemp` lives under `/tmp/b9r1/` and is
removed after each run.

CODE INTEL FIRST: `graft ask` before any grep for code questions; `scripts/lane_context.sh -q 'how does the S0-02 checker grade the
replay leg' -s _check_replay -s _check_delivery -s snapshot_timeline -s delta_timeline -o /tmp/b9r1/pack.md
proofs/S0-02/check_buzz_authz.py proofs/S0-02/tools/pc/run_s0_02_legs.sh proofs/S0-02/oracle/denial_table.py proofs/S0-02/tools/build_fixtures.py`.

## The contract (build to it; the HOW is yours)

R1 (B-1). A replay case through the SOURCED `main` with the observation window live: `S0_02_TURN_WAIT_S` ≥ 2, `POLL_S` overridden small
AFTER sourcing (R:35 and R:33 overwrite T2's env today — VERIFY-B9 I-4), and a second-delivery prompt that appears inside the window.
It asserts C:621's exact refusal text. Show it RED under m7 (R:241 `wait_turn_window 0` deleted) and M13 (R:241 → `wait_turn_window 1`),
each through the WHOLE T2 in a scratch copy of R, and GREEN on the landed R. Replace B9's m7 row.

R2 (B-2). Item 6b (T2 `test_replay_mid_line_snapshot_first_plus_delta_equals_final`) also asserts that the first snapshot ends with `\n`
and that its byte length equals the byte count of the timeline's complete lines at the snapshot. Show it RED under R-level m6 (R's cut
`p=d.rfind(b"\n")` replaced by `print(len(d))`) and GREEN on the landed R. Re-measure every m-row m1-m7 against R ITSELF (never a function
override), and correct B9's rows and named killers (F-10).

R3 (F-1, D-036 clause 2). C binds the relay's duplicate receipt to the SECOND delivery, next to C:599's `_check_delivery(` call: the
second receipt has `http_status` 200, `accepted` True (a bool), `event_id_echoed` True, `event_id` equal to the FIRST delivery's id, and
`message` exactly `duplicate:` (the pinned relay, 1c8321cd, `crates/buzz-relay/src/handlers/ingest.rs:3192-3197` returns it BEFORE
dispatch; `crates/buzz-relay/src/api/bridge.rs:963-968` answers it as `{event_id, accepted, message}`; D's `_normalise` turns that into
the receipt — premise). Each violation is its own named refusal (you name them; a test pins each text). The buzz-acp duplicate-drop line
(relay.rs:2387) becomes OPTIONAL defense-in-depth: its presence is recorded, its absence is never a failure, and it never substitutes for
the receipt (a forwarded duplicate — a non-`duplicate:` receipt — fails even when buzz-acp dropped it). The oracle's `neg-replayed` row
names the relay as the decider (`decided_by`, `src`, `line`, `src_pattern` pinned by T2's upstream-source test the same way the other rows
are) and keeps the buzz-acp line as its defense-in-depth field; the six-key distinctness gate (C:697) still holds.

R4 (F-2, D-036 clause 3). C proves ONE continuous buzz-acp process across the two deliveries and refuses a second process by name.
Decide the mechanism from MEASUREMENT of what the real producer writes (the frame tee's timeline records and the masked log, S0-01's
producer, read-only) and state it: for example, the second delta holds no `initialize`, and its first record continues the first
snapshot's sequence. A second delta that restarts with `initialize` + `session/new` (VERIFY-B9's h1a/h1b and B9's own case A) fails.

R5 (F-5, F-6, F-12). T2 gains: the M11 case (the first delivery opened a session but produced no prompt; the second produced the turn →
the landed FAIL `neg-replayed/first: 0 ACP turn(s)`), killing M11; a clause-1 discriminating test (same content, a NEW event id, signed
by the bundle's labelled pass owner key → refused at C:611's text, not earlier at C:231), killing cm1; a slow-first-turn integration case
killing M14 (R:227 `wait_turn_window 1` removed).

R6 (F-7). The integration test's second delivery is built from D's REAL `_normalise` over the pinned relay's duplicate response (200,
`{"event_id": <first id>, "accepted": true, "message": "duplicate:"}`) with a ONE-process log and timeline — never copied from the synthetic
fixture — and it PASSES; the old synthetic shape (the :2387 line with a non-`duplicate:` receipt) FAILS with R3's text.

R7 (the committed PASS bundle). `build_fixtures.py` builds the replay leg in D-036's shape (the second receipt `duplicate:`, one continuous
process, zero prompts in the second delta; the :2387 line optional); the regenerated bundle passes the REAL CLI; `PROVENANCE.md`'s replay
paragraph says what the leg now shows. Every other leg's bytes stay identical (paste the diff stat of the regenerated tree).

R8 (F-13). A torn timeline line is a named `Failure` with the CLI's `failure_reason:` line (C:6's exit contract), through a C-local wrapper
around `_load_timeline_raw` — S0-01's function is untouched.

R9 (F-10, F-11). B9-report.md: the m6/m7 rows, the named killers of m1/m3/m4/m5, and line 35's claim ("no checker change is needed"),
each corrected in place with its `Corrected by B9-R1` note and the measurement that corrects it.

## Tests and mutants

Every contract line has a test that is RED on the PIN bytes (paste the RED run) and GREEN after. The mutation table (scratch copies only;
each mutant compiles — `bash -n` / `py_compile` — and collects, AF-AP-78; run the killer on the UNMUTATED tree first and paste that it
passes, AF-AP-138): m1-m7 and M11, M13, M14 re-measured against R; cm1; and new rows for your code — at least the receipt check removed,
`message ==` loosened to `startswith("duplicate")`, the echoed-id check removed, the first-id binding removed, the continuity check removed,
the :2387 line made required again, the F-13 wrapper removed. One row each: mutant · compiles · collected · killed-by / SURVIVED /
EQUIVALENT with the reason.

## Gates (paste every command with its output)

`mkdir -p /tmp/b9r1/bt && bash scripts/test_summary.sh tests/test_s0_02_buzz_authz.py --basetemp /tmp/b9r1/bt` TWICE, identical counts
(`rm -rf /tmp/b9r1/bt` between; the premise floor is `175 passed`, set a5de0beef100 — your count grows by your tests) · `bash -n` on R (unchanged)
· `/root/venv-agent-factory/bin/python -m pyflakes proofs/S0-02/check_buzz_authz.py proofs/S0-02/oracle/denial_table.py
proofs/S0-02/tools/build_fixtures.py tests/test_s0_02_buzz_authz.py` · `python3 scripts/ap_screen.py proofs/S0-02/check_buzz_authz.py` and
`--tests tests/test_s0_02_buzz_authz.py` (new hits only) · `python3 scripts/no_laya_in_gates.py` · the real CLI over the regenerated PASS
bundle (PASS) and over the old synthetic replay shape (FAIL with R3's text).

## Report (`tasks/briefs/s0-02-support/B9-R1-report.md`)

PREMISE re-measured · per contract line R1-R9: files:lines and the tests that pin it · RED then GREEN (pasted) · the mutant table · the
gates · DISCREPANCIES · NOT-done (the F-rows not in this round — F-3, F-4, F-8, F-9 — stay follow-ups; the live capture is the coordinator's).
Lint floor: `python3 scripts/report_lint.py --min-refs 15 --map R=proofs/S0-02/tools/pc/run_s0_02_legs.sh --map C=proofs/S0-02/check_buzz_authz.py
--map T2=tests/test_s0_02_buzz_authz.py --map O=proofs/S0-02/oracle/denial_table.py tasks/briefs/s0-02-support/B9-R1-report.md --root .`;
apply its `fix:` hints for at most three rounds, then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23 08:33Z, sandbox @ c269263)

````
$ date -u
2026-09-23 08:33Z

$ git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
c269263

$ git diff origin/claude/soundbox-kit-migration-iz1jwf HEAD -- <the eight files> proofs/S0-02/fixtures | wc -l; git status --porcelain -- proofs/S0-02 tests/test_s0_02_buzz_authz.py | wc -l
0
0

$ for f in <the eight files>; do sha256 lines path; done
93bf0cf987f9d4a0 319 proofs/S0-02/tools/pc/run_s0_02_legs.sh
6bc4729839495148 762 proofs/S0-02/check_buzz_authz.py
f35cd9542e07ec53 2979 tests/test_s0_02_buzz_authz.py
9fdf8f3a87fa96b3 234 proofs/S0-02/tools/pc/deliver_event.py
a3c31dbda859a635 288 proofs/S0-02/oracle/denial_table.py
38ae5a69ad28fec9 549 proofs/S0-02/tools/build_fixtures.py
d735e75d42df6099 63 proofs/S0-02/fixtures/PROVENANCE.md
6ff6411a136e2918 80 tasks/briefs/s0-02-support/B9-report.md

$ git log --format="%h %ad %s" --date=format:"%m-%d %H:%M" -3 -- proofs/S0-02 tests/test_s0_02_buzz_authz.py | cut -c1-110
221e68b 09-23 03:53 S0-02 B9 landed (GATED-PENDING-VERIFY): the replay leg's per-delivery delta model, the sec
b3eba6a 09-22 13:18 s0-02: B8 landed - the runner follow-up (D1 the zero-match turn-window count, D2 the maske
bd6af01 09-22 11:15 S0-02 fixture identities (task #102, D-037 + D-038): owner2 added as a second owner of the

$ grep -n (the seams) check_buzz_authz.py
97:_load_timeline_raw = s0_01._load_timeline_raw
231:        raise Failure(f"{leg}: delivered content does not match the fixture's")
298:def _check_delivery(
479:    delivery = _check_delivery(leg_dir, leg, delivered, fixture)
561:def _check_replay(root: Path, identities: dict, anchors: "Anchors"):
599:        delivery = _check_delivery(
611:    if ids[0] != ids[1]:
616:    if turns[0] != 1:
621:    if turns[1] != 0:
697:    if len(set(keys)) != len(distinct_legs):

$ grep -n (the seams) run_s0_02_legs.sh
33:FD=$MARKERS/v2-$HOST_LEG
35:POLL_S=5
80:wait_turn_window() {
111:snapshot_timeline() {
128:delta_timeline() {
227:      wait_turn_window 1
241:      wait_turn_window 0
261:      wait_turn_window 0
281:      wait_turn_window 0
286:      wait_turn_window 1
291:      wait_turn_window 0

$ grep -n (the seams) tests/test_s0_02_buzz_authz.py
41:BUZZ_SRC_DEFAULT = "/home/user/nerdherderdani/buzz"
1078:def test_replay_with_two_different_event_ids_fails(tmp_path):
1771:        r"^TURN_WAIT_S=\$\{S0_02_TURN_WAIT_S:-(\d+)\}$", text, re.MULTILINE
2192:        "S0_02_TURN_WAIT_S": "0",
2358:post_leg() { printf P >> "$B8_ORDER"; }
2559:        "S0_02_TURN_WAIT_S": "0",
2627:post_leg() { touch "$FD/buzz-acp.exit"; cp "$B9_SECOND_LOG" "$FD/buzzacp.log"; }
2783:        '    if cmp -s "$B9_OUT/concat" "$FD/timeline.jsonl"; then echo "concat_ok=yes"; else echo "concat_ok=NO"; fi\n'
2811:def test_replay_mid_line_snapshot_first_plus_delta_equals_final(tmp_path):
2819:    assert "concat_ok=yes" in out, "first (cut at last nl) + delta must equal the final timeline byte-for-byte"
2900:              'if cmp -s "$B9_OUT/concat" "$FD/timeline.jsonl"; then echo "concat_ok=yes"; else echo "concat_ok=NO"; fi\n')
2942:def test_replay_mutant_snapshot_not_cut_at_newline(tmp_path):
2969:    S0_02_TURN_WAIT_S=0, the second delivery is already in the timeline by the

$ sed -n 125,134p proofs/S0-02/oracle/denial_table.py  (the neg-replayed row)
        "fixture": "neg-replayed",
        "reason": "denied: event-replayed",
        "leg": "negative",
        "decided_by": "buzz-acp",
        "src": "crates/buzz-acp/src/relay.rs",
        "line": 2387,
        "src_pattern": 'debug!("dropping duplicate event for channel {channel_id}");',
        "evidence": EV_BUZZACP_LOG,
        "observable": "dropping duplicate event for channel",
        "buzz_acp_observable": "dropping duplicate event for channel",

$ the pinned relay (S0_02_BUZZ_SRC default /home/user/nerdherderdani/buzz)
1c8321cd08feb597f8bcff5195c21148fb3e98ed
--- crates/buzz-relay/src/handlers/ingest.rs:3192-3197
    if !was_inserted {
        return Ok(IngestResult {
            event_id: event_id_hex,
            accepted: true,
            message: "duplicate:".into(),
        });
--- crates/buzz-relay/src/api/bridge.rs:963-968
        Ok(result) => {
            let response = Json(serde_json::json!({
                "event_id": result.event_id,
                "accepted": result.accepted,
                "message": result.message,
            }));

$ docs/08_DECISION_LOG.md D-036 (the rejected alternative, verbatim)
Rejected: keeping the cumulative-file model (the checker can never pass by construction); a Buzz-ACP-level dedup as the oracle (that guard is synthetic — the relay is the real dedup point). Build = B9 (task #101) after B8, then the fresh eight-leg capture. 

$ pytest tests/test_s0_02_buzz_authz.py (sandbox venv)
154 passed, 21 skipped in 85.40s (0:01:25)
(bare pytest leaves S0_01_VENUE unset, so 21 venue-declared tests skip; the gate runs through test_summary.sh:)

$ mkdir -p /tmp/b9r1q && bash scripts/test_summary.sh tests/test_s0_02_buzz_authz.py --basetemp /tmp/b9r1q/bt 2>&1 | tail -2
pytest-exit: 0
pytest-summary: 175 passed in 87.79s (0:01:27)

$ bash scripts/pc_suite.sh set-id -- tests/test_s0_02_buzz_authz.py
1 files set=a5de0beef100
````
