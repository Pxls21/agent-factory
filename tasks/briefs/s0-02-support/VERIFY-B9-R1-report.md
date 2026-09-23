# VERIFY-B9-R1 report — the targeted adversarial verify of B9-R1 (S0-02 replay leg, D-036) (task #174)

Lane: VERIFY-B9-R1, sandbox adversarial-verifier (claude-opus-5-5, D-054). PIN 56a8f50.
Brief: `tasks/briefs/s0-02-support/VERIFY-B9-R1-brief.md`. Report is DATA: claim · instrument · observed · SOLID/UNSURE.
Status: COMPLETE (written incrementally). Gate recommendation: MERGE-READY-WITH-FOLLOWUPS (see the end).

Map: C = `proofs/S0-02/check_buzz_authz.py`, O = `proofs/S0-02/oracle/denial_table.py`,
B = `proofs/S0-02/tools/build_fixtures.py`, T2 = `tests/test_s0_02_buzz_authz.py`.

## Item 1 — PREMISE re-measure

Measured 2026-09-23 10:53-11:00Z (sandbox, HEAD 3d89549; `date -u` read `Wed Sep 23 10:53:50 UTC 2026` at lane start).

````
$ git rev-parse 56a8f50 ; git log -1 --format='%H %P' 56a8f50
56a8f50cc086fddcb09b4240f905860aee8450ca
56a8f50cc086fddcb09b4240f905860aee8450ca 59d8f004ea06da25d2a01c74b9f7da3c8f1d820b
$ for f in …; do echo "$(git rev-parse --short=12 56a8f50:$f) $(git show 56a8f50:$f | wc -l) $f"; done
7b875de37dce 936 proofs/S0-02/check_buzz_authz.py
c8c7ac11e2ba 314 proofs/S0-02/oracle/denial_table.py
2d74933a169d 559 proofs/S0-02/tools/build_fixtures.py
044b32b5880b 3416 tests/test_s0_02_buzz_authz.py
81ef691a387c 78 proofs/S0-02/fixtures/PROVENANCE.md
c2178e7cfd60 574 tasks/briefs/s0-02-support/B9-R1-report.md
$ git diff --quiet 56a8f50 HEAD -- proofs/S0-02 tests/test_s0_02_buzz_authz.py; echo rc=$?
rc=0
$ git diff --quiet HEAD -- proofs/S0-02 tests/test_s0_02_buzz_authz.py; echo worktree_vs_HEAD_rc=$?
worktree_vs_HEAD_rc=0
$ grep -n "^def _check_one_process\|…\|^PROCESS_START_BANNER" proofs/S0-02/check_buzz_authz.py
139:PROCESS_START_BANNER = "buzz-acp starting:"
304:def _read_receipt(leg_dir: Path, leg: str) -> dict:
471:def _load_timeline(leg_dir: Path, leg: str):
597:def _check_one_process(leg_dir: Path, first: list, second: list):
653:def _check_replay(root: Path, identities: dict, anchors: "Anchors"):
738:def _check_duplicate_receipt(found: frozenset, delivery: dict, first_id: str) -> bool:
$ python3 proofs/S0-02/check_buzz_authz.py --synthetic-root proofs/S0-02/fixtures/evidence-blanket proofs/S0-02/fixtures/evidence-blanket/legs; echo rc=$?
failure_reason: blanket-rejection: reasons ['delivery::restricted: not a channel member'] not distinct — 6 negative legs collapsed to 1 observable(s)
rc=1
$ python3 proofs/S0-02/check_buzz_authz.py --synthetic-root proofs/S0-02/fixtures/evidence-pass proofs/S0-02/fixtures/evidence-pass/legs; echo rc=$?
PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, 6 distinct reasons; replay refused by the relay's duplicate: receipt (buzz-acp drop line absent, defense-in-depth only); +1 revocation leg (assertion 2); removal evidence: coordinator-supplied receipt (unauthenticated; ordering and fields verified; not an end-to-end revocation proof)
rc=0
$ (buzz source, /home/user/nerdherderdani/buzz) git rev-parse HEAD ; upstream.lock.yaml buzz commit
1c8321cd08feb597f8bcff5195c21148fb3e98ed
    commit: 1c8321cd08feb597f8bcff5195c21148fb3e98ed
$ sed -n 3192,3197p crates/buzz-relay/src/handlers/ingest.rs ; sed -n 2387p crates/buzz-acp/src/relay.rs
    if !was_inserted {
        return Ok(IngestResult {
            event_id: event_id_hex,
            accepted: true,
            message: "duplicate:".into(),
        });
                            debug!("dropping duplicate event for channel {channel_id}");
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_02_buzz_authz.py
1 files set=a5de0beef100
````

- P1.1 blob ids, line counts, def lines, CLI outputs, relay lines: all equal the brief's premise block. SOLID.
- P1.2 the regenerated bundle files: `git show --stat 56a8f50` lists NINE replay files under `proofs/S0-02/fixtures/`
  (the brief's "nine files" counts the top-level `fixtures/neg-replayed.json`), plus PROVENANCE.md. SOLID.
- P1.3 the T2 run twice: see Item 11 (the same run serves both items).

## Item 2 — D-036 clause 2, the relay receipt (`_check_duplicate_receipt`, C:738)

Instrument: `/tmp/vb9r1/probe.py` (deleted at lane end). Each case copies the committed PASS bundle, changes ONE thing,
and runs the REAL CLI from the repo: `python proofs/S0-02/check_buzz_authz.py --synthetic-root <copy> <copy>/legs`.
Every case below is a NEW shape except the three the brief names literally (`accepted` "true", `event_id_echoed` false,
the forwarded duplicate), which I ran in new variants as well. Pasted output (11:1xZ):

````
[i2a-msg-suffixed-reaction] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: the relay receipt message is 'duplicate: reaction already exists', expected exactly 'duplicate:' — the relay did not refuse the second delivery as a duplicate (a forwarded duplicate fails even when buzz-acp dropped it)
[i2b-msg-trailing-space] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: the relay receipt message is 'duplicate: ', expected exactly 'duplicate:' — …
[i2b-msg-trailing-newline] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: the relay receipt message is 'duplicate:\n', expected exactly 'duplicate:' — …
[i2b-msg-uppercase] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: neither delivery.json nor buzzacp.log carries ANY known denial observable — the leg produced no turn and no named reason
[i2c-accepted-str-true] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: the relay's duplicate receipt must carry accepted=true (a bool), got 'true'
[i2c-accepted-int-1] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: the relay's duplicate receipt must carry accepted=true (a bool), got 1
[i2d-status-float-200.0] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: the relay answers a duplicate with HTTP 200, got http_status 200.0
[i2d-status-str-200] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: the relay answers a duplicate with HTTP 200, got http_status '200'
[i2d-status-201] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: the relay answers a duplicate with HTTP 200, got http_status 201
[i2e-echoed-false] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: the relay's duplicate receipt must echo the event id (event_id_echoed=true), got False
[i2e-echoed-str-true] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: the relay's duplicate receipt must echo the event id (event_id_echoed=true), got 'true'
[i2f-event-id-uppercase] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: the duplicate receipt names event 226E96AEFF61, not the first delivery's 226e96aeff61 — the receipt is not bound to this replay
[i2g-2nd-denial-second-log-only] rc=1 traceback=no
    stdout: failure_reason: neg-replayed: the first and second sub-legs carry different buzzacp.log bytes — two masked logs: a second process, not ONE continuous buzz-acp process (D-036 clause 3)
[i2g-2nd-denial-both-logs-relay-text] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: evidence carries denial observables ['buzzacp_log::invalid: event timestamp too far from server time'] beside the relay's duplicate receipt
[i2g-2nd-denial-both-logs-self-authored] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: evidence carries denial observables ['buzzacp_log::dropping self-authored event'] beside the relay's duplicate receipt
[i2h-drop-line-present-debug] rc=0 traceback=no
    stdout: PASS: S0-02 buzz-authz - … replay refused by the relay's duplicate: receipt (buzz-acp drop line present, defense-in-depth only); …
[i2h-drop-line-other-channel-info-level] rc=0 traceback=no
    stdout: PASS: S0-02 buzz-authz - … replay refused by the relay's duplicate: receipt (buzz-acp drop line present, defense-in-depth only); …
[i2i-forwarded-dup-empty-msg-dropline-plus-delta] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: the relay receipt message is '', expected exactly 'duplicate:' — the relay did not refuse the second delivery as a duplicate (a forwarded duplicate fails even when buzz-acp dropped it)
[i2i-forwarded-dup-empty-msg-no-dropline] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: neither delivery.json nor buzzacp.log carries ANY known denial observable — the leg produced no turn and no named reason
[i2i-forwarded-dup-body-without-message-field] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: neither delivery.json nor buzzacp.log carries ANY known denial observable — the leg produced no turn and no named reason
[i2x-control-unmodified] rc=0 traceback=no
    stdout: PASS: S0-02 buzz-authz - … (buzz-acp drop line absent, defense-in-depth only); …
````
(`…` stands for an unchanged tail: in the message rows, the tail of i2a's full refusal text; in the PASS rows, the tail of the full PASS line in Item 1.)

Per brief case, fails-by-named-refusal or passes, and whether that is correct:
- 2.1 `duplicate: reaction already exists`: REFUSED at C:771 `if delivery["message"] != row["observable"]:` (message). Correct: a kind-9 duplicate is the bare text
  (ingest.rs:3196, the O row's note at O:153 `"The observable is the receipt, BOUND to the second`); the suffixed text is the reaction path (ingest.rs:3080). SOLID.
- 2.2 `duplicate:` plus trailing space / newline: REFUSED at C:771 `if delivery["message"] != row["observable"]:`. Correct: D's `_normalise` keeps the body's message
  verbatim (D:169 `receipt["message"] = blob["message"]`), so the pinned relay cannot produce a padded text. SOLID.
- 2.3 `accepted` "true" / `1`: REFUSED at C:755. Correct (`is not True`). SOLID.
- 2.4 `http_status` 200.0 / "200" (and 201): REFUSED at C:751 `if type(status) is not int or status != 200:`. Correct. SOLID.
- 2.5 `event_id_echoed` false (and "true"): REFUSED at C:760. SOLID.
- 2.6 the first id in uppercase hex: REFUSED at C:765 `if delivery["event_id"] != first_id:` (the first-id binding). Correct: the relay echoes
  `event_id_hex` (ingest.rs:3194) and D stores the echoed value (D:165 `receipt["event_id"] = blob["event_id"]`), so a
  case-folded id is not what the relay said. SOLID.
- 2.7 a valid receipt plus a SECOND denial observable: with the line in BOTH logs, REFUSED at C:781 (the `extra`
  refusal) with the observable named. With the line in the SECOND log only, REFUSED earlier by clause 3's log-equality
  check (C:637 `if logs[0] != logs[1]:`), because `_check_one_process` runs inside `_check_replay`, before the distinctness gate. Both are
  correct refusals; the named text depends on which log carries the line. SOLID.
- 2.8 the drop line beside a valid receipt: PASS line says `present`. SOLID. Observation (see VF-4): the record is a bare
  substring match, so a line from another target, at INFO level, for ANOTHER channel id, also reads `present`.
- 2.9 a FORWARDED duplicate (accepted true, empty message, drop line present), here with a continuing non-prompt delta:
  REFUSED at C:771 `if delivery["message"] != row["observable"]:` with R3's text. D-036 refuses it. SOLID. Without the drop line the same receipt is refused earlier, at
  `_observe_all` (C:422 `raise Failure(`), with the no-observable text; also a refusal, with a different name.

## Item 3 — D-036 clause 3, one process (`_check_one_process`, C:597)

Same instrument as Item 2 (real CLI, bundle copies). Pasted output (11:2xZ); `…PASS…` is the unchanged control PASS
line with `drop line absent`:

````
[i3a-delta-continues-with-session-new-and-prompt] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: 1 ACP turn(s), expected 0 — the duplicate delivery produced a second turn
[i3b-seq-gap-of-two] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: delta record seq 10 does not continue the preceding seq 7 — the frame tee restarted: a second process, not ONE continuous buzz-acp process (D-036 clause 3)
[i3b-seq-gap-of-two-mid-delta] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: delta record seq 11 does not continue the preceding seq 8 — the frame tee restarted: …
[i3c-seq-float] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: delta record seq 8.0 does not continue the preceding seq 7 — the frame tee restarted: …
[i3c-seq-bool] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: delta record seq True does not continue the preceding seq 7 — the frame tee restarted: …
[i3c-prev-str-nonempty-delta] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: delta record seq 8 does not continue the preceding seq '7' — the frame tee restarted: …
[i3c-prev-str-empty-delta] rc=0 traceback=no
    stdout: …PASS…
[i3d-first-snapshot-empty] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/first: 0 ACP turn(s), expected exactly 1 — a replay leg proves nothing unless the first delivery produced a turn
[i3e-both-logs-two-banner-blocks] rc=1 traceback=no
    stdout: failure_reason: neg-replayed: buzzacp.log shows 2 buzz-acp start line(s) ('buzz-acp starting:'), expected exactly 1 — not ONE continuous buzz-acp process (D-036 clause 3)
[i3f-banner-quoted-in-another-line] rc=1 traceback=no
    stdout: failure_reason: neg-replayed: buzzacp.log shows 2 buzz-acp start line(s) ('buzz-acp starting:'), expected exactly 1 — …
[i3f-two-banners-one-line] rc=0 traceback=no
    stdout: …PASS…
[i3f-two-banners-vt-separated] rc=1 traceback=no
    stdout: failure_reason: neg-replayed: buzzacp.log shows 2 buzz-acp start line(s) ('buzz-acp starting:'), expected exactly 1 — …
[i3g-crlf-logs] rc=0 traceback=no
    stdout: …PASS…
[i3h-logs-differ-only-trailing-newline] rc=1 traceback=no
    stdout: failure_reason: neg-replayed: the first and second sub-legs carry different buzzacp.log bytes — two masked logs: a second process, not ONE continuous buzz-acp process (D-036 clause 3)
[i3i-first-snapshot-internal-agent-restart-empty-delta] rc=0 traceback=no
    stdout: …PASS…
[i3i-first-snapshot-internal-agent-restart-continuing-delta] rc=0 traceback=no
    stdout: …PASS…
[i3j-first-snapshot-seq-gap-empty-delta] rc=0 traceback=no
    stdout: …PASS…
[i3k-first-snapshot-two-prompts] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/first: 2 ACP turn(s), expected exactly 1 — a replay leg proves nothing unless the first delivery produced a turn
````

Per brief case:
- 3.1 a continuing delta that carries `session/new` + a prompt (seq 8-10): REFUSED on the TURN COUNT, C:729
  `if turns[1] != 0:`, with the text `neg-replayed/second: 1 ACP turn(s), expected 0 — the duplicate delivery produced`
  `a second turn`. The turn counts run before C:734 `_check_one_process(leg_dir, entries[0], entries[1])` (the builder's
  Design decision 2). SOLID.
- 3.2 a seq gap of two (7 → 10, and 8 → 11 inside the delta): REFUSED at C:626 `if type(prev) is not int or type(seq) is not int or seq !=`. SOLID.
- 3.3 seq as a float (8.0) or a bool (True): REFUSED at C:626 (`type(seq) is not int`; a bool is not `int` by `type`).
  A string seq was the builder's own case, so it is not re-run. New: the FIRST snapshot's last seq as a string ("7")
  is refused only when the delta is non-empty; with the empty delta (D-036's expected live shape) it PASSES, because
  C:623 `prev = first[-1].get("seq")` is never compared. SOLID (observed). See VF-2.
- 3.4 an empty first snapshot: REFUSED at C:724 `if turns[0] != 1:` (`neg-replayed/first: 0 ACP turn(s), expected exactly 1`), no traceback.
  C:623 `first[-1]` is unreachable with an empty list: C:734 `_check_one_process(leg_dir, entries[0], entries[1])` runs only after C:724 `if turns[0] != 1:` required exactly one prompt, and a
  snapshot with a prompt has at least one record. The guard is C:724 `if turns[0] != 1:`. SOLID.
- 3.5 two identical logs, each with the banner twice (a full second startup block): REFUSED at C:645 `if starts != 1:`, `shows 2`. SOLID.
- 3.6 the banner text quoted inside another log line: COUNTED (C:644 `starts = sum(1 for ln in logs[1].splitlines() if banner in ln)` is a substring test over every line), so a genuine
  one-process leg is REFUSED as `shows 2`. Real risk: LOW and fail-closed only. The pinned crate emits the text at one
  site (T2:716 `def test_process_start_banner_is_buzz_acp_s_single_entry_point_line`), and the live legs carry fixture
  texts that do not contain it. The reverse (a false PASS) needs a real second banner to go missing; two banners on
  ONE physical line count as 1 and PASS (`i3f-two-banners-one-line`), which tracing's whole-line writes do not produce.
  INFO. (The `vt-separated` probe was mis-designed: its second banner sat on its own line, so it counts 2 like any
  repeat. It adds nothing beyond the one-line case.)
- 3.7 a CRLF log (both copies): PASS. `bytes.splitlines` splits `\r\n`, so the count stays 1. Correct. SOLID.
- 3.8 the logs differing only in a trailing newline: REFUSED at C:637 `if logs[0] != logs[1]:`. Correct: the runner copies ONE file into both
  sub-legs, so byte identity is the producer's contract. SOLID.
- 3.9 NEW: an agent restart INSIDE the first snapshot (`initialize` seq 1 + its result seq 2 appended after the first
  turn): PASSES with an empty delta, and PASSES with a delta that continues the RESTARTED counter (seq 3). Also a first
  snapshot with an internal seq gap (…6, 100) PASSES. Clause 3's timeline half (C:616-632 `for rec in second:`) inspects only the delta and
  the first snapshot's LAST seq. See VF-2.
- 3.10 NEW: a first snapshot with TWO prompts: REFUSED at C:724 `if turns[0] != 1:` (`2 ACP turn(s)`). The code is right; no T2 test pins
  this direction (Item 4, mutant M16).

## Item 4 — D-036 clauses 1, 4 and 5, and the turn counts

Independent CLI probes in NEW shapes (pasted, 12:1xZ):

````
[i4a-clause1-created_at-minus-30-new-id] rc=1 traceback=no
    stdout: failure_reason: neg-replayed: the two deliveries carry different event ids (226e96aeff61 vs 1a524994673d) — this is not a replay
    (control) same id: True | same sig: True
[i4a-clause1-control-resigned-same-id] rc=0 traceback=no
    stdout: PASS: S0-02 buzz-authz - … (buzz-acp drop line absent, defense-in-depth only); …
[i4b-clause5-prompt-in-the-open-session] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: 1 ACP turn(s), expected 0 — the duplicate delivery produced a second turn
````
(The re-sign control is trivial: S0-01's `sign_event` is deterministic, so the re-signed event is byte-identical.)

Per clause: the guard, the test that pins it, and the mutant that kills that test (whole-T2 rows in Item 10; every
killer passed in the unmutated baseline first, AF-AP-138):
- Clause 1 (IDENTICAL event id): guard C:719 `if ids[0] != ids[1]:`. Pinned by T2:1178 `def test_replay_same_content_new_event_id_fails_on_the_id_check`.
  Mutant cm1 (C:719 `if ids[0] != ids[1]:` → `if False:`, re-run here):
  `1 failed, 205 passed in 130.84s (0:02:10)`, killed by that ONE test only. T2:1127 `def test_replay_with_two_different_event_ids_fails`
  does NOT kill cm1: its OR-assertion also accepts the earlier
  content refusal. So clause 1's ONLY discriminating test is the builder's own case. It is a real discriminator
  (killed cm1; my created_at − 30 probe is refused at the same line), so this is INFO, not a gap. SOLID.
- Clause 4 (ONE prompt in total): guard C:724 `if turns[0] != 1:` plus C:729 `if turns[1] != 0:`. The LOWER bound (0 prompts in the
  first) is pinned: M24 (`turns[0] != 1` → `turns[0] > 1`), `2 failed, 204 passed in 136.07s (0:02:16)`, killed by T2:1119 `def test_replay_first_delivery_without_a_turn_fails`
  and T2:3361 `def test_replay_first_delivery_that_turns_only_after_the_duplicate_fails`. The UPPER bound (2 prompts in the
  first sub-leg) is UNPINNED: M16 (`turns[0] != 1` → `turns[0] < 1`) SURVIVED the whole T2, `206 passed in 123.13s
  (0:02:03)`. The code refuses two prompts today (Item 3 case 3.10, `neg-replayed/first: 2 ACP turn(s), expected
  exactly 1`); no test keeps it that way. This clause half has NO test at all, not even a builder case. The check
  pre-dates B9-R1 (C@c269263:616 `if turns[0] != 1:` per the builder's premise). SOLID. See VF-6.
- Clause 5 (ZERO prompts in the second delta): guard C:729 `if turns[1] != 0:`. M17 (`turns[1] != 0` → `turns[1] > 1`),
  `4 failed, 202 passed in 123.30s (0:02:03)`, killed by T2:1111 `def test_replay_second_delivery_with_a_turn_fails`,
  T2:3341 `def test_replay_observation_window_catches_a_late_second_turn`,
  `test_replay_integration_pin_runner_reproduces_the_failure`, `test_replay_mutant_cumulative_second_is_rejected`.
  My realistic shape (a prompt reusing the open session, no `session/new`) is refused at C:729 `if turns[1] != 0:`. SOLID.
- The turn-count primitive (`_prompt_frames`, C:184, counts c2a `session/prompt` frames) is unchanged by B9-R1 and was
  not mutated here (out of the change class).

## Item 5 — R8, the torn line (`_load_timeline`, C:471; AF-AP-144) and the parse-escape sweep

Torn records in NEW places, through the real CLI (the builder's three cases were: replay-second JSON, replay-second
UTF-8, pos-allowed JSON at the end). Pasted (11:3xZ):

````
[i5a-torn-json-first-subleg] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/first: a timeline record is not valid JSON or UTF-8 — a torn or partial line (Unterminated string starting at: line 1 column 87 (char 86))
[i5a-torn-utf8-first-subleg] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/first: a timeline record is not valid JSON or UTF-8 — a torn or partial line ('utf-8' codec can't decode bytes in position 1731-1732: unexpected end of data)
[i5b-torn-json-second-subleg-empty-delta] rc=1 traceback=no
    stdout: failure_reason: neg-replayed/second: a timeline record is not valid JSON or UTF-8 — a torn or partial line (Unterminated string starting at: line 1 column 87 (char 86))
[i5c-torn-json-nonreplay-neg-stale] rc=1 traceback=no
    stdout: failure_reason: neg-stale: a timeline record is not valid JSON or UTF-8 — a torn or partial line (Unterminated string starting at: line 1 column 87 (char 86))
[i5c-torn-utf8-nonreplay-neg-self-authored] rc=1 traceback=no
    stdout: failure_reason: neg-self-authored: a timeline record is not valid JSON or UTF-8 — a torn or partial line ('utf-8' codec can't decode bytes in position 506-507: unexpected end of data)
[i5c-torn-json-mid-file-pos-allowed] rc=1 traceback=no
    stdout: failure_reason: pos-allowed: a timeline record is not valid JSON or UTF-8 — a torn or partial line (Unterminated string starting at: line 1 column 35 (char 34))
````

- 5.1 torn line in the FIRST sub-leg (JSON and UTF-8): named failure, labelled `neg-replayed/first`. SOLID.
- 5.2 torn line in the SECOND sub-leg (as the whole empty-delta file): named failure. SOLID.
- 5.3 torn line in non-replay legs (neg-stale JSON, neg-self-authored UTF-8) and MID-FILE in pos-allowed: named
  failures with the right leg label. Every leg reaches the wrapper through C:488 `entries = _load_timeline(leg_dir, leg)`.
  R8 holds. SOLID.

The sweep: every `json.loads`, `.decode(` and `read_text(` in C (grep, then each escape reproduced through the CLI):

````
$ grep -n "json\.loads\|\.decode(\|read_text(\|read_bytes(\|json\.load(" proofs/S0-02/check_buzz_authz.py
179:        return json.loads(path.read_text())
400:    log_text = log_path.read_text()
472:    """F-13 (VERIFY-B9): S0-01's reader parses each line with a bare json.loads
536:        _check_masking(log_path.read_text(), leg)
542:        log_text = _require_file(leg_dir / "buzzacp.log", leg, "buzzacp.log").read_text()
634:        _require_file(leg_dir / sub / "buzzacp.log", f"neg-replayed/{sub}", "buzzacp.log").read_bytes()
824:    identities = json.loads(
$ (each escape through the CLI; the last checker frame and the exception)
i5s1-nonobject-record-second | rc 1 | … line 188, in _prompt_frames | AttributeError: 'list' object has no attribute 'get'
i5s2-nonobject-frame-second | rc 1 | … line 191, in _prompt_frames | AttributeError: 'str' object has no attribute 'get'
i5s3-nonutf8-log-replay-both | rc 1 | … line 400, in _observe_all | UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 362: invalid start byte
i5s4-nonutf8-log-pos-allowed | rc 1 | … line 536, in _check_leg | UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 362: invalid start byte
i5s5-nonutf8-json-delivery-pos-allowed | rc 1 | … line 179, in _read_json | UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 162: invalid start byte
i5s6-json-list-delivery-second | rc 1 | … line 397, in _observe_all | AttributeError: 'list' object has no attribute 'get'
i5s7-json-list-t0-pos-allowed | rc 1 | … line 270, in _check_freshness | AttributeError: 'list' object has no attribute 'get'
i5s8-delivered-created_at-string-signed | rc 1 | … line 276, in _check_freshness | TypeError: unsupported operand type(s) for -: 'int' and 'str'
i5s9-anchor-identities-torn | rc 1 | stdout: '' | … line 824, in _check_bundle_uncapped | json.decoder.JSONDecodeError: Unterminated string starting at: line 7 column 11 (char 335)
````
(stdout was empty for every row: no `failure_reason:` line.)

Site by site:
- C:472 `"""F-13 (VERIFY-B9): S0-01's reader parses each line with a` is docstring text. C:634 `_require_file(leg_dir / sub / "buzzacp.log"` reads bytes and decodes nothing: safe. C:542 `log_text = _require_file(leg_dir / "buzzacp.log", leg` is dominated: C:539 `found = _observe_all(leg_dir, leg, delivery, fixture_name)`
  reads the same file first (C:400 `log_text = log_path.read_text()`).
- The two reported siblings reproduce: the non-object record (C:188 `if e.get("dir") != "c2a":`, and its `frame` at C:191) and the non-UTF-8 log
  at C:400 `log_text = log_path.read_text()`. Their verdict does not change (FOLLOW-UP, issue #38).
- NOT the only escapes. Other sites of the same AF-AP-144 class, all tamper-only (every real producer writes ASCII
  `json.dumps` output, and the masked log is UTF-8):
  - C:536 `_check_masking(log_path.read_text(), leg)`: a non-UTF-8 `buzzacp.log` in a TURN leg (pos-allowed) escapes here, not at C:400 `log_text = log_path.read_text()`. Same class as sibling 2,
    second site.
  - C:179 `_read_json` catches only `JSONDecodeError`, so a non-UTF-8 EVIDENCE JSON file (delivery.json here; the same
    reader serves fixture.json, delivered-event.json, t0.json, membership.json) escapes as `UnicodeDecodeError`.
  - C:179 also returns a non-object value. A JSON LIST of the five key names passes the key-set test at C:310 `if set(delivery) != expected_keys:` (`set()` of a
    list of the names equals `expected_keys`), then dies at C:397 `message = str(delivery.get("message", ""))`; a list t0.json dies at C:270 `t0 = t0_blob.get("t0_epoch_s")`.
  - C:276: a validly signed event (the labelled `pass` bundle owner key) whose `created_at` is a string passes the id
    and signature checks, then dies in the freshness arithmetic. Post-parse type confusion, the same exit-contract
    class.
  - C:824 `identities = json.loads(`: `identities.json` has no parse guard at all. It is an ANCHOR (the repo's S0-01 identities, or the synthetic
    root spec.json pins), not evidence. INFO.
- Effect of every escape: exit 1 with no `failure_reason:` line. proof-runner still fails the leg (the positive leg by
  exit code, `scripts/proof-runner:186-190` `expected_exit = leg["expect"]["exit_code"]`; the negative leg by `negative-control-unmet`, `scripts/proof-runner:194-199`),
  so no escape can mint a PASS. The loss is the named reason. See VF-3.

## Item 6 — R7, the regenerated bundle

````
$ (/tmp/vb9r1/build2.py: the repo's build_fixtures.build_bundle into two scratch roots, then sha256 per file)
evidence-pass: files r1=64 r2=64 committed=64; r1==r2 True; r1==committed True
   differing paths vs committed: []
evidence-blanket: files r1=64 r2=64 committed=64; r1==r2 True; r1==committed True
   differing paths vs committed: []
top-level fixtures drifting from a fresh build: [] of 8
$ git diff --stat=200 59d8f00 56a8f50 -- proofs/S0-02/fixtures      (59d8f00 = the parent of 56a8f50)
 proofs/S0-02/fixtures/PROVENANCE.md                                            | 15 +++++++++++++++
 proofs/S0-02/fixtures/evidence-blanket/fixtures/neg-replayed.json              |  9 +++++----
 proofs/S0-02/fixtures/evidence-blanket/legs/neg-replayed/second/fixture.json   |  9 +++++----
 proofs/S0-02/fixtures/evidence-blanket/legs/neg-replayed/second/timeline.jsonl |  2 --
 proofs/S0-02/fixtures/evidence-pass/fixtures/neg-replayed.json                 |  9 +++++----
 proofs/S0-02/fixtures/evidence-pass/legs/neg-replayed/second/buzzacp.log       |  1 -
 proofs/S0-02/fixtures/evidence-pass/legs/neg-replayed/second/delivery.json     |  2 +-
 proofs/S0-02/fixtures/evidence-pass/legs/neg-replayed/second/fixture.json      |  9 +++++----
 proofs/S0-02/fixtures/evidence-pass/legs/neg-replayed/second/timeline.jsonl    |  2 --
 proofs/S0-02/fixtures/neg-replayed.json                                        |  9 +++++----
 10 files changed, 41 insertions(+), 26 deletions(-)
$ git diff --name-only 59d8f00 56a8f50 -- proofs/S0-02/fixtures | grep -v "/legs/neg-replayed/\|neg-replayed.json$"
proofs/S0-02/fixtures/PROVENANCE.md
$ git ls-tree -r --name-only <rev> -- proofs/S0-02/fixtures | wc -l      (59d8f00, then 56a8f50)
137
137
````

- 6.1 two builds into scratch roots are byte-identical (64 files per bundle), and each equals the committed bundle
  byte for byte. The committed bundles ARE the builder's output at the PIN. SOLID.
- 6.2 every non-replay leg's bytes are unchanged against 59d8f00: the only changed paths are replay-leg files, the
  three `neg-replayed.json` fixture copies (the top-level one and one per bundle), and PROVENANCE.md. The file count
  is 137 before and after. SOLID.
- 6.3 PROVENANCE.md labels the replay leg synthetic in words a reader cannot miss: line 1 `# evidence-pass /
  evidence-blanket — SYNTHETIC bundle provenance`; line 3 `Both committed bundles are SYNTHETIC evidence`; the replay
  paragraph (line 16 `The replay leg`) says it "models" relay-level dedup and ends "This shape is inferred from the
  pinned relay source; no live capture has shown it yet." Its factual claims match the bytes: a zero-byte second
  timeline in both bundles, identical first/second logs (`cmp` exit 0), one banner. SOLID.
- 6.4 NEW (test gap, not a code defect): NO T2 test compares the committed bundles with a fresh `build_bundle`. The
  only caller of B:423 `def build_bundle` is B:530 `build_bundle(bundle, FIXTURE_DIR / name)` (the `--bundles` CLI);
  `git grep -n "build_bundle"` finds no test. T2:146 `def test_committed_fixtures_equal_a_fresh_build` runs `--check`,
  which compares the EIGHT top-level fixtures only (B:534-555 `built = build_all()`). So R7's "regenerated by running it, never by hand"
  holds TODAY (6.1, measured) but no gate keeps it true. Mutant M18 (Item 10) proves it: the builder's empty-delta
  line removed, whole T2 green. See VF-1.

## Item 7 — R6, the integration harness

- It drives D's REAL `_normalise` over a relay-shaped 200 body: T2:2878 `def _b9_receipt(event_id: str, message: str) -> str:`
  builds `{"event_id", "accepted": True, "message"}` (the bridge.rs:963-968 shape) and calls
  `builder.deliver_event._normalise(200, raw, event_id)`. `builder` loads D BY PATH from the tree
  (B:49 `DELIVER_EVENT = PROOF_DIR / "tools" / "pc" / "deliver_event.py"`), so a D mutant in the tree reaches the harness.
  Nothing is copied from the synthetic second sub-leg: the log is T2:2797 `B9_ONE_PROCESS_LOG = (`, the receipts come
  from `_b9_receipt`. SOLID (read + the mutants below).
- The scratch mutants of `_normalise` turn the integration tests red:
  - D1 (the message field dropped): both integration PASS cases red (T2:3000 `def test_replay_integration_runner_producer_into_real_checker`,
    T2:3045 `def test_replay_integration_empty_delta_second_timeline_passes`), plus the forwarded-duplicate runner case. SOLID.
  - D2a (`accepted` coerced to an int): both integration PASS cases red. SOLID.
  - D2b (`accepted` coerced by truthiness, the type guard dropped): the integration tests stay GREEN, because the
    pinned relay's body carries a real bool, so `bool(True)` changes nothing. Only T2:2115 `def test_normalise_takes_accepted_only_when_upstream_is_bool` kills it. This is correct
    layering (the unit test owns the malformed-body case), not a harness gap. INFO.

## Item 8 — the oracle row (O)

- The `ingest.rs:3196` pin IS re-read from the pinned buzz source (`_buzz_src()`, env `S0_02_BUZZ_SRC`, sandbox default
  `/home/user/nerdherderdani/buzz`; T2:301 `def test_pinned_tree_is_the_locked_commit` pins its HEAD to
  1c8321cd, measured in Item 1): T2:324 `def test_oracle_row_line_still_carries_its_pattern` (the `[neg-replayed]` case)
  reads `row["src"]` at `row["line"]` and asserts the pattern; T2:356 `def test_replay_row_is_the_relay_duplicate_receipt`
  asserts the exact six-line block ending at `row["line"] + 1` and the bridge's three body lines. SOLID.
- A wrong line number (M20) is red in three tests; a wrong `src_pattern` (M21) in two; a wrong defense-in-depth line
  (M22) in T2:345 `def test_oracle_replay_defense_in_depth_line_is_pinned_too`. Rows in Item 10. SOLID.
- `defense_in_depth` readers (`git grep -n "defense_in_depth" -- '*.py'`): C:384 (ALL_OBSERVABLES), C:778 (the receipt
  check), O:162 `"defense_in_depth": {` (the definition), T2:345-353 `def test_oracle_replay_defense_in_depth_line_is_pinned_too` (the pin test). Nothing else. The builder does not copy it into fixtures
  (B:236-243 `"expected": {` copies mechanism, decided_by, evidence, observable); no fixture copy contains the key (measured). SOLID.
- INFO: T2:332 tests `src_pattern` as a SUBSTRING of the line, so a shorter pattern (for example `'"duplicate:"'`)
  would still pass T2:324 `def test_oracle_row_line_still_carries_its_pattern` and T2:356 `def test_replay_row_is_the_relay_duplicate_receipt`. Not material: T2:356's six-line block equality pins the code shape anyway.

## Item 9 — the deviations

- D1 (receipt graded after the distinctness gate). SAFE.
  - A bad replay receipt passes the gate and then fails with the receipt text: every receipt case in Item 2 did so
    (for example `i2d-status-201`), and `i9a` (400, accepted false, echoed false, message `duplicate:`) printed
    `failure_reason: neg-replayed/second: the relay answers a duplicate with HTTP 200, got http_status 400`.
  - A replay receipt carrying another leg's relay text is refused by the gate instead (`i9b`): `failure_reason:
    blanket-rejection: … 6 negative legs collapsed to 5 observable(s)`. That name is correct: the two legs are
    indistinguishable.
  - No bundle skips the receipt check on the way to PASS. C:866 loops over `oracle.NEGATIVE_FIXTURES`, which holds
    `neg-replayed` third (measured order: `('neg-unauthorized', 'neg-bad-signature', 'neg-replayed', 'neg-stale',
    'neg-self-authored', 'revoked', 'neg-not-allowlisted')`). The PASS return (C:893 `PASS: S0-02 buzz-authz - 1 positive`) is after the loop, so a PASS
    always ran C:877 `replay_dind = _check_duplicate_receipt(found, delivery`. The only skips are earlier refusals. Dynamic check (the repo's checker loaded in-process, the
    function wrapped with a counter, the committed PASS bundle): `_check_duplicate_receipt calls:
    [(['delivery::duplicate:'], 'duplicate:', '226e96aeff61')]`, one call, and the line was the PASS line. SOLID.
- D3 (the PASS line changed). SAFE. Consumers: spec.json's positive leg pins only `"exit_code": 0`; proof-runner judges
  the positive leg by exit code (`scripts/proof-runner:186-190` `expected_exit = leg["expect"]["exit_code"]`) and records only `stdout_sha256` (`scripts/proof-runner:113`);
  the ledger lists S0-02 as `"state": "ABSENT"`, so no minted result binds that hash. The only text pins are T2:752 `def test_pass_bundle_passes`
  and T2:2788 `B9_PASS_LINE = (`. Other `git grep` hits are historical briefs and
  reports. SOLID.
- D6 (the top-level `fixtures/neg-replayed.json` regenerated). SAFE, and NEEDED. Its `expected` block equals both bundle
  copies on every oracle-derived key (decided_by, discrepancy, evidence, observable, mechanism
  `crates/buzz-relay/src/handlers/ingest.rs:3196`). The one differing key is `replay_of_event_id`, which is each copy's
  own `pos-allowed` specimen id (true in all three, measured), because the bundles use bundle identities by design.
  The production anchor is this very file (C:58 `DEFAULT_FIXTURES = HERE / "fixtures"`), and D copies it into each live
  leg (D:190 reads it, D:219 writes it), so a stale copy would have carried the old buzz-acp mechanism into the live capture; T2:146 `def test_committed_fixtures_equal_a_fresh_build` (M20's
  killer) would also have gone red. SOLID.
- D2 (the O docstring), D4, D5, D7: read; each is a statement of fact that the tree bears out (D7's cm1 half re-run
  above: killed by T2:1178 `def test_replay_same_content_new_event_id_fails_on_the_id_check`). m6 (R-level) was NOT re-run: the runner is not in this increment's component list.

## Item 10 — MUTANTS

Venue: ONE scratch tree `/tmp/vb9r1/tree` = `git archive 56a8f50` of proofs/S0-01, proofs/S0-02, proofs/schemas, T2,
tests/conftest.py and pyproject.toml, plus a `git init` whose `objects/info/alternates` borrows the repo's objects
read-only (T2's `git show 71463f3:…` resolves). Driver `/tmp/vb9r1/mut.py`: one exact-string edit per row (the dry
check read `EXPECTED 25 OK 25`: every anchor matches once and compiles; cm1 and M24, added later, each matched once), then `py_compile`, then `--collect-only`, then
the WHOLE T2 through `scripts/test_summary.sh` with a JUnit record, then restore by copy with a sha256 check.
AF-AP-138: the unmutated baseline in this venue read `206 passed in 122.42s (0:02:02)`, JUnit `cases 206 failed []
skipped 0`; every killer below is in that baseline's passed set (`killers_in_baseline_passed: true` on every row).
AF-AP-78: `compiles_rc 0` and `collected 206` on every row. Naming: the ids below are local to this report; my C-level
M11, M13 and M14 are NOT VERIFY-B9's R-level mutants of the same names.

| id | mutation (file:line) | compiles | collected | whole-T2 | verdict / killer |
|---|---|---|---|---|---|
| M1 | C:751 `status != 200` → `status >= 400` | 0 | 206 | `206 passed in 122.76s (0:02:02)` | SURVIVED — no case holds a non-200 status below 400 (the six receipt cases use 400 and True). The code is right; the test does not pin "exactly 200". VF-5 |
| M2 | C:755 `delivery["accepted"] is not True` → `not delivery["accepted"]` | 0 | 206 | `1 failed, 205 passed in 122.00s (0:02:02)` | KILLED by `test_replay_duplicate_receipt_fields_each_have_a_named_refusal[accepted='true']` (only) |
| M3 | C:781-785 the `if extra:` refusal block deleted | 0 | 206 | `1 failed, 205 passed in 128.30s (0:02:08)` | KILLED by `test_replay_other_denial_observables_beside_the_receipt_fail` (only) |
| M4 | C:645 `starts != 1` → `starts < 1` | 0 | 206 | `1 failed, 205 passed in 122.78s (0:02:02)` | KILLED by `test_replay_log_must_show_exactly_one_buzz_acp_start[2]` (only) |
| M5 | C:637-642 `if logs[0] != logs[1]:` the log-equality refusal deleted | 0 | 206 | `1 failed, 205 passed in 126.42s (0:02:06)` | KILLED by `test_replay_two_masked_logs_are_a_second_process` (only) |
| M6 | C:626 `seq != prev + 1` → `seq <= prev` | 0 | 206 | `1 failed, 205 passed in 122.29s (0:02:02)` | KILLED by `test_replay_second_delta_from_a_restarted_process_fails[seq-gap]` (only) |
| M7 | C:616-622 the `initialize` refusal loop deleted | 0 | 206 | `4 failed, 202 passed in 123.56s (0:02:03)` | KILLED by `test_replay_runner_restarted_process_is_refused` and the three `test_replay_second_delta_from_a_restarted_process_fails` cases `[b9-case-A-restart]`, `[h1a-restart-with-session]`, `[initialize-continuing-seq]` |
| M8 | C:765 `delivery["event_id"] != first_id` → `str(delivery["event_id"]).lower() != first_id` | 0 | 206 | `206 passed in 122.44s (0:02:02)` | SURVIVED — no test gives an uppercase echoed id (Item 2 case 2.6 shows the code refuses it). Tamper-only: D stores the relay's lowercase `event_id_hex`. INFO, VF-5 |
| M9 | C:751 `type(status) is not int or ` dropped | 0 | 206 | `206 passed in 125.90s (0:02:05)` | SURVIVED — `http_status=True` still fails (True != 200) and no test uses 200.0. Tamper-only: D's status is urllib's int. INFO, VF-5 |
| M10 | C:760 `delivery["event_id_echoed"] is not True` → `not delivery["event_id_echoed"]` | 0 | 206 | `206 passed in 120.66s (0:02:00)` | SURVIVED — the only echoed case is `False`, which still fails; a truthy non-bool ("true", Item 2 case 2.5) is untested. Tamper-only: D writes a bool. INFO, VF-5 |
| M11 | C:623 `first[-1]` → `first[0]` (continuity anchored on the first record) | 0 | 206 | `5 failed, 201 passed in 123.34s (0:02:03)` | KILLED by `test_replay_continuing_delta_passes`, `test_replay_integration_runner_producer_into_real_checker`, and `[seq-gap]`, `[seq-not-an-int]`, `[seq-restart-without-initialize]` |
| M12 | C:719 clause 3 run BEFORE the id and turn checks (`_check_one_process(…)` inserted above `if ids[0] != ids[1]:`) | 0 | 206 | `3 failed, 203 passed in 124.09s (0:02:04)` | KILLED by `test_replay_second_delivery_with_a_turn_fails`, `test_replay_integration_pin_runner_reproduces_the_failure`, `test_replay_mutant_cumulative_second_is_rejected` (the turn-count texts are pinned) |
| M13 | C:480 `except (json.JSONDecodeError, UnicodeDecodeError)` → `except json.JSONDecodeError` | 0 | 206 | `1 failed, 205 passed in 128.21s (0:02:08)` | KILLED by `test_a_torn_timeline_record_is_a_named_cli_failure[replay-second-utf8]` (only) |
| M14 | C:786 `return dind_key in found` → `return True` (always "present") | 0 | 206 | `5 failed, 201 passed in 122.64s (0:02:02)` | KILLED by `test_pass_bundle_passes`, `test_replay_drop_line_is_recorded_when_present_and_never_required`, both integration PASS cases, `test_replay_slow_first_turn_is_waited_for_before_the_snapshot` |
| M15 | C:780 the drop line counted as an extra (`dind_key` removed from the allowed set) | 0 | 206 | `1 failed, 205 passed in 120.96s (0:02:00)` | KILLED by `test_replay_drop_line_is_recorded_when_present_and_never_required` (only) |
| M16 | C:724 `turns[0] != 1` → `turns[0] < 1` (two prompts in the first sub-leg allowed) | 0 | 206 | `206 passed in 123.13s (0:02:03)` | SURVIVED — no test puts two prompts in the replay's first sub-leg. Code right (Item 3 case 3.10). VF-6 |
| M17 | C:729 `turns[1] != 0` → `turns[1] > 1` | 0 | 206 | `4 failed, 202 passed in 123.30s (0:02:03)` | KILLED by `test_replay_second_delivery_with_a_turn_fails`, `test_replay_observation_window_catches_a_late_second_turn`, `test_replay_integration_pin_runner_reproduces_the_failure`, `test_replay_mutant_cumulative_second_is_rejected` |
| M18 | B:514 `(second_dir / "timeline.jsonl").write_text("")` deleted (the builder emits the restarted `_timeline(False)` delta again) | 0 | 206 | `206 passed in 122.21s (0:02:02)` | SURVIVED — no test regenerates the bundles (Item 6.4). VF-1 |
| M19 | B:468 `"duplicate:"` → `""` (the builder emits the forwarded-duplicate receipt) | 0 | 206 | `206 passed in 125.07s (0:02:05)` | SURVIVED — same cause as M18. VF-1 |
| M20 | O:134 `"line": 3196` → `3195` | 0 | 206 | `3 failed, 203 passed in 123.34s (0:02:03)` | KILLED by `test_oracle_row_line_still_carries_its_pattern[neg-replayed]`, `test_replay_row_is_the_relay_duplicate_receipt`, `test_committed_fixtures_equal_a_fresh_build` (the fixture embeds `mechanism`) |
| M21 | O:135 `src_pattern` → `'message: "duplicate: ".into(),'` | 0 | 206 | `2 failed, 204 passed in 123.13s (0:02:03)` | KILLED by `test_oracle_row_line_still_carries_its_pattern[neg-replayed]`, `test_replay_row_is_the_relay_duplicate_receipt` |
| M22 | O:165 the `defense_in_depth` `"line": 2387` → `2386` | 0 | 206 | `1 failed, 205 passed in 121.45s (0:02:01)` | KILLED by `test_oracle_replay_defense_in_depth_line_is_pinned_too` (only) |
| D1 | D:168 `_normalise`'s message field dropped (`if "message" in blob …` → `if False:`) | 0 | 206 | `6 failed, 200 passed in 122.47s (0:02:02)` | KILLED by both integration PASS cases (T2:3000 `def test_replay_integration_runner_producer_into_real_checker`, T2:3045), `test_replay_runner_forwarded_duplicate_is_refused_on_the_receipt`, `test_replay_slow_first_turn_is_waited_for_before_the_snapshot`, `test_every_bundle_delivery_uses_the_real_producer_normalizer`, `test_deliver_normalizer_exposes_echo_provenance` |
| D2a | D:157 `accepted` coerced to int (`int(blob["accepted"])`) | 0 | 206 | `11 failed, 195 passed in 121.50s (0:02:01)` | KILLED by both integration PASS cases and nine more runner/normaliser tests (C:334 refuses the first receipt's `1`) |
| D2b | D:156-157 the bool type guard dropped, `accepted` coerced by truthiness (`bool(blob["accepted"])`) | 0 | 206 | `1 failed, 205 passed in 122.12s (0:02:02)` | KILLED by T2:2115 `test_normalise_takes_accepted_only_when_upstream_is_bool` only. EQUIVALENT for the integration tests: the relay body's `accepted` is already the bool true |
| cm1 | C:719 `if ids[0] != ids[1]:` → `if False:` (the builder's row, re-run for Item 4) | 0 | 206 | `1 failed, 205 passed in 130.84s (0:02:10)` | KILLED by `test_replay_same_content_new_event_id_fails_on_the_id_check` (only) |
| M24 | C:724 `turns[0] != 1` → `turns[0] > 1` (zero prompts in the first allowed) | 0 | 206 | `2 failed, 204 passed in 136.07s (0:02:16)` | KILLED by `test_replay_first_delivery_that_turns_only_after_the_duplicate_fails`, `test_replay_first_delivery_without_a_turn_fails` |

Tally: 27 rows: 26 new, plus the builder's cm1 re-run for Item 4. Three of the brief's named rows coincide in EFFECT with a builder row but use a different edit (a deleted block, not `if False:`): M3 ~ cr7, M5 ~ ccc, M7 ~ cca. KILLED 20. SURVIVED 7: M1, M8, M9, M10 (receipt strictness, tamper-only
shapes), M16 (clause 4's upper bound), M18, M19 (no bundle drift gate). EQUIVALENT 0 (D2b is killed, but only by the unit
test; it is equivalent for the integration harness, Item 7). Every row: `compiles_rc 0`, `collected 206`,
`killers_in_baseline_passed true`, `restored_sha_ok true`. After the last row the four tree files matched the repo's
sha256 (`a545731d7f87f55a` C, `e5a4906d8520ad36` O, `a01aa2305a2057df` B, `9fdf8f3a87fa96b3` D).


## Item 11 — Gates (pasted)

````
$ export PATH=/root/venv-agent-factory/bin:$PATH; for i in 1 2; do rm -rf /tmp/vb9r1/bt; bash scripts/test_summary.sh tests/test_s0_02_buzz_authz.py --basetemp /tmp/vb9r1/bt; done; rm -rf /tmp/vb9r1/bt
run1 start 2026-09-23T10:57:31Z
pytest-exit: 0
pytest-summary: 206 passed in 120.44s (0:02:00)
run2 start 2026-09-23T10:59:31Z
pytest-exit: 0
pytest-summary: 206 passed in 122.69s (0:02:02)
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_02_buzz_authz.py
1 files set=a5de0beef100
$ (the CLI on the PASS and the blanket bundles: pasted in Item 1; PASS rc=0, blanket rc=1 with spec.json's exact failure_reason)
$ python3 scripts/validate-ledger integrity --root . ; echo "rc=$?"
S0-01 PRESENT
S0-02 ABSENT
S0-03 PRESENT
S0-04 PRESENT
S0-05 ABSENT
S0-06 PRESENT
S0-07 PRESENT
S0-08 PRESENT
S0-09 PRESENT
S0-10 PRESENT
S0-11 PRESENT
S0-12 PRESENT
blocked_credential numerator=0 denominator=1
blocked_host numerator=0 denominator=1
conformance_checked_decision numerator=3 denominator=3
execution_proof numerator=7 denominator=9
rc=0
$ python3 scripts/report_lint.py --min-refs 15 --map R=proofs/S0-02/tools/pc/run_s0_02_legs.sh --map C=proofs/S0-02/check_buzz_authz.py --map T2=tests/test_s0_02_buzz_authz.py --map O=proofs/S0-02/oracle/denial_table.py tasks/briefs/s0-02-support/B9-R1-report.md --root .
report_lint: 150 refs — OK 150, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
rc=0
````

- The gate reproduces the premise floor: 206 twice, set `a5de0beef100`, equal to the coordinator's landing count. SOLID.
- The same count held in the scratch venue (the mutant baseline, Item 10). SOLID.
- validate-ledger: no INVALID; S0-02 is ABSENT (not minted), as the builder's NOT-DONE says. SOLID.
- The builder's report cites 150 refs and every one resolves (OK 150). SOLID.

## FINDING INVENTORY (no severity filter; numbered VF-n so they do not collide with VERIFY-B9's F-n in issue #38)

VF-1 · FOLLOW-UP · no drift gate ties the committed bundles to `build_bundle`.
- Evidence: MEASURED. M18 and M19 (two builder mutants of the replay leg) SURVIVED the whole T2; the only caller of
  B:423 `def build_bundle` is B:530 `build_bundle(bundle, FIXTURE_DIR / name)` (the `--bundles` CLI); the `--check` of T2:146 `def test_committed_fixtures_equal_a_fresh_build` covers the eight top-level fixtures only.
- Contract: R7 ("regenerate them by RUNNING it, never by hand"). It holds TODAY: two scratch builds equal the committed
  64 files per bundle (Item 6.1). Nothing keeps it true.
- Canonical path: n/a (a test-suite property). Material effect: none on today's output. Pre-existing (the gap predates
  B9-R1). Discriminator: M18/M19. Ownership: T2.
- Fix: one T2 test that runs `build_bundle("pass"|"blanket", tmp_path/…)` and asserts byte-equality with the committed
  trees (the build is deterministic, measured).

VF-2 · FOLLOW-UP · clause 3's timeline half never inspects the FIRST snapshot.
- Evidence: REPRODUCED through the CLI. An agent restart inside the first snapshot (`initialize` seq 1 + result seq 2
  after the turn) PASSES with an empty delta and with a delta that continues the restarted counter (seq 3); a first
  snapshot with an internal seq gap, or a string last seq, PASSES with the empty delta (Item 3.3, 3.9).
- Contract: R4 / D-036 clause 3 name ONE continuous buzz-acp PROCESS. That is held by C:645 `if starts != 1:` (one banner) and C:637 `if logs[0] != logs[1]:` (one
  log); an agent (hermes-acp) restart under one buzz-acp is not a buzz-acp restart, and the relay's `duplicate:`
  receipt still proves the refusal. The gap is an inconsistency in the checker's own model (C:600-606 `The mechanism follows what the real producers write` calls a restarted
  agent "a second process", but enforces that only after the boundary).
- Canonical path: needs an agent restart between the first prompt and the snapshot (R snapshots right after
  `wait_turn_window 1`); not observed live. Material effect on the D-036 verdict: none. Ownership: C.
- Fix: in `_check_one_process`, require first + delta to be consecutive from seq 1 with `initialize` only at seq 1 (the
  producer shape the builder measured on all six real timelines).

VF-3 · FOLLOW-UP (append to issue #38, not a re-file) · AF-AP-144 escape sites beyond the two reported siblings.
- Evidence: REPRODUCED through the CLI (Item 5 sweep): C:179 (a non-UTF-8 evidence JSON → `UnicodeDecodeError`; a
  non-object JSON value, including a LIST of the five key names that passes the key-set test at C:310 `if set(delivery) != expected_keys:` and dies at C:397 `message = str(delivery.get("message", ""))`),
  C:270 `t0 = t0_blob.get("t0_epoch_s")` (a list t0.json), C:536 `_check_masking(log_path.read_text(), leg)` (a non-UTF-8 log in a TURN leg), C:276 `age = t0 - delivered["created_at"]` (a validly signed event with a string
  `created_at`), C:824 `identities = json.loads(` (the anchor identities.json; INFO).
- Contract: C:6's exit contract (`failure_reason:` on exit 1); R8 covers the torn TIMELINE line only, and it holds.
- Canonical path: tamper-only (the tee and D write ASCII `json.dumps`; the masked log is UTF-8). Material effect: exit 1
  with no `failure_reason:` line; proof-runner still fails the leg (`scripts/proof-runner:186-190` `expected_exit = leg["expect"]["exit_code"]`, `:194-199`); no
  false PASS. The verdict on the two reported siblings is UNCHANGED.
- Fix: `_read_json` catches `UnicodeDecodeError` and requires a dict; every log read goes through one guarded decode;
  a type guard on `created_at` before the arithmetic.

VF-4 · INFO · the drop line's `present` record is an unbound substring.
- Evidence: REPRODUCED (Item 2.8): an INFO line from another target, for ANOTHER channel id, reads `present`.
- Contract: R3 "its presence is recorded". Material effect: the PASS line can overstate defense-in-depth; the verdict
  cannot change (C:786 `return dind_key in found` feeds only the text). Fix: bind the DEBUG level and the bundle's channel id.

VF-5 · FOLLOW-UP · the receipt predicates' exactness is unpinned.
- Evidence: MEASURED. M1 (`status >= 400`), M8 (case-insensitive id), M9 (status type check dropped), M10 (truthy
  `event_id_echoed`) SURVIVED the whole T2. The code refuses each shape (Item 2.4-2.6: 201, 200.0, "200", an uppercase
  id, "true").
- Contract: R3 "a test pins each text": met. The exactness of each predicate is not a frozen requirement.
- Canonical path: the pinned relay and D cannot write these shapes. Material effect: none today.
- Fix: four more `_RECEIPT_CASES` rows (201, 200.0, an uppercase echoed id, echoed "true").

VF-6 · FOLLOW-UP · clause 4's upper bound has no test.
- Evidence: MEASURED. M16 (`turns[0] != 1` → `< 1`) SURVIVED the whole T2. The code refuses two prompts in the first
  sub-leg (Item 3.10).
- Contract: D-036 clause 4 ("ONE prompt in total"). The check pre-dates B9-R1; B9-R1's R5 asked for VERIFY-B9's R-level
  M11 (zero prompts in the first), cm1 and M14; none puts two prompts in the first. Material effect: none today
  (regression protection only).
- Fix: one test with two prompts in the first sub-leg asserting `neg-replayed/first: 2 ACP turn(s), expected exactly 1`.

VF-7 · UNVERIFIED · the `extra` refusal scans the WHOLE one-process debug log.
- C:780-785 `extra = found - {f"{row['evidence']}::{row['observable']}"` refuses any other ALL_OBSERVABLES text in the replay leg's log, and that log spans BOTH deliveries (the first
  turn included). If a live debug log carries one (a self-authored echo of the agent's own reply, or a relay text
  quoted in a debug line), the live capture is REFUSED.
- Why unverified: no real debug-level buzz-acp log exists in the repo; the S0-01 corpus is INFO-level (`DEBUG=0` in all
  five masked logs, measured). The pinned REQ adds `#p: [agent]` when `require_mention` is on (buzz-acp relay.rs,
  lines 3407-3410), which makes a self-authored echo unlikely.
- Pre-existing strictness: B9's `_check_named_observable` enforced exactly one observable on the same log. Direction:
  fail-closed (never a false PASS). Resolution: the coordinator's live eight-leg capture; if it bites, scope the replay
  leg's extra scan to the delivery channel plus the drop line.

VF-8 · INFO · the first sub-leg's receipt is not required to be a NEW acceptance.
- REPRODUCED (`i9c`): a first receipt reading `duplicate:` PASSES. The builder reported it as INFO; the verdict stands:
  a turn is still required in the first sub-leg, and D-036's clauses bind the SECOND receipt.

VF-9 · INFO · the banner count (C:644 `starts = sum(1 for ln in logs[1].splitlines() if banner in ln)`) is a per-line substring test.
- A quoted banner inflates the count (fail-closed); two banners on one physical line count as one (tamper-only: tracing
  writes whole lines). Item 3.6.

VF-10 · FOLLOW-UP (out of this boundary) · stale runner text.
- R:193-195 and the BLOCKER text R:204-210 still say neg-replayed is decided inside buzz-acp with relay.rs:2387 as its
  only observable. D-036 made the relay the decider. R was READ-ONLY for B9-R1. Fix in the next runner increment:
  drop neg-replayed from both (debug capture is still needed for the other two legs).

VF-11 · INFO · D2b is equivalent for the integration harness.
- A truthiness coercion of `accepted` does not change the relay's bool body; T2:2115 owns that case. Correct layering.

VF-12 · INFO · clause 1's only discriminating test is the builder's own case.
- cm1 is killed by T2:1178 `def test_replay_same_content_new_event_id_fails_on_the_id_check` alone; the OR-assertion of T2:1127 `def test_replay_with_two_different_event_ids_fails` does not discriminate. T2:1178 is a real discriminator, and my
  new-shape probe (created_at − 30) is refused at the same line.

VF-13 · INFO · T2:332 tests `src_pattern` as a substring.
- A shorter pattern would pass; the six-line block equality of T2:356 `def test_replay_row_is_the_relay_duplicate_receipt` pins the code shape anyway.

VF-14 · INFO · refusal NAMES that depend on the shape (all are refusals).
- A second observable in the second log ONLY is refused by clause 3's log equality (C:637 `if logs[0] != logs[1]:`), not by C:781 `if extra:`; an uppercase
  `DUPLICATE:` and a forwarded duplicate WITHOUT the drop line are refused pre-gate at C:422 `raise Failure(` with the no-observable text,
  not R3's text. R6 requires R3's text only for the shape WITH the drop line, and that holds (Item 2.9).

Confirmed SOLID (the claims this recommendation rests on, each reproduced):
- R3: every receipt field has its own named refusal, including new shapes (Item 2).
- R4: the four clause-3 refusals fire on new shapes (Item 3).
- R6: the harness runs D's REAL `_normalise`; D mutants turn it red (Items 7, 10).
- R7: the committed bundles equal the builder's output; no non-replay byte moved (Item 6).
- R8: a torn line is a named failure in every leg and sub-leg tried (Item 5).
- D1, D3 and D6 are SAFE (Item 9).
- The gate count reproduces: 206 twice (Item 11).

Reproduced vs reviewed statically vs skipped:
- Reproduced: every item above, through the real CLI or the whole T2.
- Static only: the buzz-acp source reads behind VF-7 (relay.rs:3407-3410, lib.rs:3257-3258).
- Skipped:
  - VERIFY-B9's R-level mutants (m1-m7 and its M11, M13, M14): the runner is not in this increment's component list.
  - The live capture and any PC/bridge use: forbidden by the brief.
  - Reproducing VF-2 through the sourced runner: the runner is out of the change class; the CLI reproduction stands.

## GATE RECOMMENDATION (a recommendation; the coordinator owns the gate)

`MERGE-READY-WITH-FOLLOWUPS` — no finding meets the whole D-031 blocking predicate. This rests on reproduced evidence,
except VF-7, which needs the live capture: it is UNVERIFIED and fail-closed only.

Blocking predicate, per finding (contract-mapped · canonical reproduction · material effect · discriminator ·
in-boundary):
- VF-1: R7 yes, but it is met today · n/a (test suite) · no · yes (M18, M19) · yes → does not block.
- VF-2: clause 3's buzz-acp continuity is held; the agent-level gap is outside the clause · no (needs a live agent
  restart in a narrow window) · no · yes (the CLI probes) · yes → does not block.
- VF-3: the C:6 exit contract, yes · no (tamper-only) · no (still exit 1, never a PASS) · yes · yes → does not block;
  add to issue #38.
- VF-4, VF-8, VF-9, VF-11 to VF-14: no material effect → INFO.
- VF-5, VF-6: the frozen texts are pinned; exactness is not frozen · the shapes are not producible · no · yes (M1, M8,
  M9, M10, M16) · yes → do not block.
- VF-7: static only, fail-closed → UNVERIFIED; cannot block.
- VF-10: out of boundary (R was read-only) → FOLLOW-UP.

Follow-ups ranked for the coordinator:
- 1. VF-1 (a bundle drift test).
- 2. VF-6 and VF-5 (four receipt cases and one clause-4 case in T2).
- 3. VF-2 (the whole-timeline continuity in C).
- 4. VF-10 (the runner text).
- 5. VF-3 (append the new sites to issue #38).
- 6. VF-7 (watch at the live capture).

## Report lint (three rounds, pasted)

````
$ python3 scripts/report_lint.py --min-refs 15 --map C=proofs/S0-02/check_buzz_authz.py --map O=proofs/S0-02/oracle/denial_table.py --map B=proofs/S0-02/tools/build_fixtures.py --map T2=tests/test_s0_02_buzz_authz.py tasks/briefs/s0-02-support/VERIFY-B9-R1-report.md --root .
round 1: report_lint: 153 refs — OK 72, NEAR 6, MISS 57, UNCHECKABLE 18, UNRESOLVED 0 (worktree)
round 2: report_lint: 153 refs — OK 151, NEAR 1, MISS 0, UNCHECKABLE 1, UNRESOLVED 0 (worktree)
round 3: report_lint: 153 refs — OK 153, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
final (after the naming notes, no further fix round): report_lint: 154 refs — OK 154, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
````
(Rounds 1-2 added a backticked token copied from each cited line; round 3 moved the PASS-return cite one line down, to the PASS text itself (C:893 `PASS: S0-02 buzz-authz - 1 positive`). No cited number was found wrong by the lint.)
