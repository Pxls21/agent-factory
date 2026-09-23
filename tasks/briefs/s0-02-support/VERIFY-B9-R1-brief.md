# VERIFY-B9-R1 — the targeted adversarial verify of B9-R1 (S0-02's replay leg under D-036) (task #174)

PIN: 56a8f50 (origin; the post-push SHA of the local landing commit fa29865, "B9-R1 landed (task #168) …").
COMPONENT:
- `proofs/S0-02/check_buzz_authz.py` (C): `_read_receipt`, `_load_timeline`, `_check_one_process`, `_check_replay`,
  `_check_duplicate_receipt`, the ALL_OBSERVABLES change, the PASS line.
- `proofs/S0-02/oracle/denial_table.py` (O): the `neg-replayed` row and the module docstring.
- `proofs/S0-02/tools/build_fixtures.py` (B): the replay leg's construction.
- The regenerated replay-leg bundle files under `proofs/S0-02/fixtures/` (nine files) and `proofs/S0-02/fixtures/PROVENANCE.md`.
- `tests/test_s0_02_buzz_authz.py` (T2).

INPUTS TO ATTACK, not truths: the builder's report `tasks/briefs/s0-02-support/B9-R1-report.md` and its corrections to
`tasks/briefs/s0-02-support/B9-report.md`.

CONTRACT (frozen):
- `tasks/briefs/s0-02-support/B9-R1-brief.md` R1-R9 (the one focused repair of VERIFY-B9, D-031);
- `docs/08_DECISION_LOG.md` D-036, verbatim: "the second delivery carries an IDENTICAL event id; its receipt is the relay's
  `duplicate:` refusal, BOUND to that delivery; ONE continuous buzz-acp process spans both deliveries; ONE prompt in total; ZERO
  prompts in the second delivery's delta; the synthetic Buzz-ACP replay guard stays as defense-in-depth, never the live oracle";
- `tasks/briefs/pc/pc-b9.md` (the frozen B9 contract).

The coordinator accepted the builder's deviations D1-D7 (in its report). Attack whether each is SAFE, not whether it matches the
brief's words.

ROLE: adversarial-verifier (sandbox, the D-054 pin). READ-ONLY on the tree: mutate scratch copies only (`/tmp/vb9r1/`). No live relay,
launcher, harness server or host secret. Every probe uses the labelled doubles, the committed bundles or copies of them, and a closed
loopback URL. No bridge or PC use.

BOUNDARY: CREATE `tasks/briefs/s0-02-support/VERIFY-B9-R1-report.md` (write it incrementally from the start); nothing else. Other
sandbox agents work in this tree on disjoint files. Never touch, run or revert them:
- `proofs/S0-05/`, `tests/test_s0_05_egress.py`, `tasks/briefs/s0-05-support/`;
- `scripts/no_laya_in_gates.py`, `tests/test_no_laya_in_gates.py`, `scripts/gate_files.txt`, `tasks/briefs/laya/`;
- `tasks/briefs/ci/`, `tasks/briefs/continuity/`, `tasks/briefs/hermes-repin/`.

Never run `git stash`, `git checkout -- …`, `git restore`, `git add`, `git commit` or `git push`. No outward-facing action. Do NOT
spawn subagents. Every pytest `--basetemp` lives under `/tmp/vb9r1/` and is removed after each run (the sandbox has about 1.6 GB
free).

CODE INTEL FIRST: `graft ask` before any grep for code questions. The pack: `scripts/lane_context.sh -q 'how does the S0-02 checker
grade the replay leg' -s _check_replay -s _check_duplicate_receipt -s _check_one_process -s _load_timeline -o /tmp/vb9r1/pack.md
proofs/S0-02/check_buzz_authz.py proofs/S0-02/oracle/denial_table.py proofs/S0-02/tools/build_fixtures.py`.

## Items (report EVERY observation; no severity filter; rank downstream)

1. PREMISE. Re-measure the block below on the PIN (blob ids, the run twice with its set id, the two CLI outputs, the relay source
   line). A mismatch that changes an item is CONTRACT-INVALID for that item; say which.
2. D-036 clause 2, the relay receipt (`_check_duplicate_receipt`). Attack with NEW shapes through the real CLI on copies of the PASS
   bundle, never the builder's cases. Each case either fails by its named refusal or passes; say which, and whether a pass is
   correct:
   - the message `duplicate: reaction already exists` (a suffixed relay text);
   - `duplicate:` plus trailing whitespace;
   - `accepted` as the string `"true"`, or as `1`;
   - `http_status` 200 as `200.0` or `"200"`;
   - `event_id_echoed` false;
   - the receipt's `event_id` equal to the first id but in uppercase hex;
   - a receipt valid in every field, with a SECOND denial observable in the second sub-leg's `buzzacp.log` (one that is not the
     drop line);
   - the drop line present alongside a valid receipt: does the PASS line say `present`?
   - a FORWARDED duplicate: accepted true, an empty message, the drop line present. D-036 must refuse it.
3. D-036 clause 3, one process (`_check_one_process`). New shapes:
   - a second delta whose seq continues but which carries a `session/new` and a prompt: does it fail on the turn count, and with
     which text?
   - a seq gap of two;
   - seq values as strings or floats;
   - a first snapshot that is empty. Is `first[-1]` reachable, and does it traceback? Say which earlier check guards it.
   - two identical logs that each carry the `buzz-acp starting:` banner twice;
   - the banner text quoted inside another log line (a false count: a real risk or not?);
   - a CRLF log;
   - the logs differing only in a trailing newline.
4. D-036 clauses 1, 4 and 5 and the turn counts. For each clause:
   - name the test that pins it and the mutant that kills that test (run it; AF-AP-138: the killer passes on the unmutated copy
     first);
   - is there a clause whose only guard is the builder's own case?
5. R8, the torn line (`_load_timeline`, AF-AP-144). The torn line placed in the FIRST sub-leg, in the second sub-leg, and in a
   non-replay leg. And the two siblings B9-R1 reported (a JSON value that is not an object; a non-UTF-8 `buzzacp.log`): confirm they
   are the only parse escapes left in C, with a sweep of every `json.loads`, `.decode(` and `read_text(` in C, and list any other.
6. R7, the regenerated bundle.
   - Run `build_fixtures.py` twice into scratch roots: byte-identical?
   - Diff every non-replay leg's bytes against the pre-B9-R1 commit (the parent of 56a8f50): unchanged?
   - Does PROVENANCE.md label the replay leg synthetic, in words a reader cannot miss?
7. R6, the integration harness. Does it drive D's REAL `_normalise` over a relay-shaped 200 body? A scratch mutant of `_normalise`
   (the message field dropped, `accepted` coerced) must turn the integration test red: run it.
8. The oracle row (O). Is the `ingest.rs:3196` pin re-read by a test from the pinned buzz source (the `S0_02_BUZZ_SRC` tests)? A
   scratch copy of the row with a wrong line number or a wrong `src_pattern`: red, and by which test? Is `defense_in_depth` read by
   anything besides `ALL_OBSERVABLES` and the receipt check?
9. The deviations.
   - D1: can a bundle with a BAD replay receipt pass the distinctness gate and then fail with the receipt text? Is there any bundle
     for which the receipt check never runs (an early return, a skipped leg)?
   - D3: does any consumer besides the two updated test pins read the PASS line (spec.json, proof-runner, ledger)?
   - D6: the top-level `fixtures/neg-replayed.json`, copied by the builder: identical to the bundles' row?
10. MUTANTS (new ones, never the builder's 26 rows). Each compiles (`py_compile`) and collects (AF-AP-78), and its killer is run on
    the unmutated copy first (AF-AP-138). At least these:
    - M1 `status != 200` → `status >= 400`;
    - M2 `delivery["accepted"] is not True` → `not delivery["accepted"]`;
    - M3 the `extra` observable refusal removed;
    - M4 the banner count `!= 1` → `< 1`;
    - M5 the log-equality check removed;
    - M6 `seq != prev + 1` → `seq <= prev`;
    - M7 the `initialize` check removed.

    Add any that items 2-9 suggest. One row each: mutant · compiles · collected · killed-by / SURVIVED / EQUIVALENT with the
    reason.
11. Gates (paste each command with its output):
    - T2 TWICE with identical counts: `bash scripts/test_summary.sh tests/test_s0_02_buzz_authz.py --basetemp /tmp/vb9r1/bt`, with
      `rm -rf` between;
    - the CLI on the PASS and the blanket bundles;
    - `python3 scripts/validate-ledger integrity --root .`;
    - report lint on the BUILDER's report with its brief's maps.

## Output

`tasks/briefs/s0-02-support/VERIFY-B9-R1-report.md` holds:
- every observation with file:line, SOLID/UNSURE and its reproduction;
- the mutant table;
- the GATE RECOMMENDATION (`MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`), with the blocking
  predicate applied per finding: contract-mapped to R1-R9 or D-036, reproduced through the real path, materially effective, a
  concrete discriminator, in-boundary.

Issue #38 already holds F-3, F-4, F-8, F-9 and the two parse siblings: do not re-file those. Only a changed verdict on one of them
is news.

Lint your own report:
`python3 scripts/report_lint.py --min-refs 15 --map C=proofs/S0-02/check_buzz_authz.py --map O=proofs/S0-02/oracle/denial_table.py
--map B=proofs/S0-02/tools/build_fixtures.py --map T2=tests/test_s0_02_buzz_authz.py tasks/briefs/s0-02-support/VERIFY-B9-R1-report.md
--root .`. Apply its `fix:` hints for at most three rounds, then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23 10:2xZ, sandbox; the S0-02 files at the PIN equal HEAD)

The coordinator's re-run at landing is the count floor (set a5de0beef100). The two CLI outputs and the relay source line were read
this session. Every S0-02 file at the PIN is byte-identical to the working tree.

````
$ for f in …; do echo "$(git rev-parse --short=12 56a8f50:$f) $(git show 56a8f50:$f | wc -l) $f"; done
7b875de37dce 936 proofs/S0-02/check_buzz_authz.py
c8c7ac11e2ba 314 proofs/S0-02/oracle/denial_table.py
2d74933a169d 559 proofs/S0-02/tools/build_fixtures.py
044b32b5880b 3416 tests/test_s0_02_buzz_authz.py
81ef691a387c 78 proofs/S0-02/fixtures/PROVENANCE.md
c2178e7cfd60 574 tasks/briefs/s0-02-support/B9-R1-report.md
$ git diff --quiet 56a8f50 HEAD -- proofs/S0-02 tests/test_s0_02_buzz_authz.py; echo rc=$?
rc=0

$ grep -n "^def _check_one_process\|^def _check_duplicate_receipt\|^def _load_timeline\|^def _check_replay\|^def _read_receipt\|^PROCESS_START_BANNER" proofs/S0-02/check_buzz_authz.py
139:PROCESS_START_BANNER = "buzz-acp starting:"
304:def _read_receipt(leg_dir: Path, leg: str) -> dict:
471:def _load_timeline(leg_dir: Path, leg: str):
597:def _check_one_process(leg_dir: Path, first: list, second: list):
653:def _check_replay(root: Path, identities: dict, anchors: "Anchors"):
738:def _check_duplicate_receipt(found: frozenset, delivery: dict, first_id: str) -> bool:

$ (the coordinator's gate at landing, 10:14-10:19Z, on these bytes)
pytest-summary: 206 passed in 122.49s (0:02:02)
pytest-summary: 206 passed in 121.87s (0:02:01)
1 files set=a5de0beef100

$ python3 proofs/S0-02/check_buzz_authz.py --synthetic-root proofs/S0-02/fixtures/evidence-blanket proofs/S0-02/fixtures/evidence-blanket/legs; echo rc=$?
failure_reason: blanket-rejection: reasons ['delivery::restricted: not a channel member'] not distinct — 6 negative legs collapsed to 1 observable(s)
rc=1
$ python3 proofs/S0-02/check_buzz_authz.py --synthetic-root proofs/S0-02/fixtures/evidence-pass proofs/S0-02/fixtures/evidence-pass/legs; echo rc=$?
PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, 6 distinct reasons; replay refused by the relay's duplicate: receipt (buzz-acp drop line absent, defense-in-depth only); +1 revocation leg (assertion 2); removal evidence: coordinator-supplied receipt (unauthenticated; ordering and fields verified; not an end-to-end revocation proof)
rc=0

$ (the pinned relay source, S0_02_BUZZ_SRC default /home/user/nerdherderdani/buzz at 1c8321cd0 = upstream.lock.yaml's buzz pin)
$ sed -n 3192,3197p crates/buzz-relay/src/handlers/ingest.rs
    if !was_inserted {
        return Ok(IngestResult {
            event_id: event_id_hex,
            accepted: true,
            message: "duplicate:".into(),
        });
$ sed -n 2387p crates/buzz-acp/src/relay.rs
                            debug!("dropping duplicate event for channel {channel_id}");
````
