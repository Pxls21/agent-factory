# B12 report — S0-02's bad-signature leg delivers ONE corrupted event; the bundle grades the revoked leg's relay text (task #196)

LANE: s0-02-b12 (sandbox, `code-implementer`, shared tree, no worktree). PIN c19736d. Brief f86d5c6.
STATUS: COMPLETE (2026-09-23T16:12:20Z). Nothing committed or pushed (lane rule); the coordinator commits through `safe_commit.sh`.

## 0. Outcome (read this first)

- **DONE in the sandbox; NOT verified live.** The bad-signature leg now makes ONE delivery: `deliver_event.py --flip-signature`
  signs the fixture template, flips byte `SIG_FLIP_BYTE_INDEX` and POSTs only the corrupted event (one request; the valid event
  never leaves the process). `--reuse` with `--flip-signature` is refused before any file, key or request (rc 1, named text). The
  runner's `neg-bad-signature)` branch is one `deliver … --flip-signature`, `wait_turn_window 0`, `collect_leg "$out"`: no
  `.probe`, no reuse, no nested directory. The live proof is the coordinator's re-capture of all eight legs (no PC use here).
- **A1 closed.** The bundle mode refuses a revoked receipt that carries another class's relay text with the `--denial revoked`
  line (`revoked: the observed denial matches the oracle's neg-stale row, not revoked's`). The pass line, the blanket reason and
  all 14 `--denial` outputs over both committed bundles are byte-identical to the PIN (sha256 dd0e5f85… both).
- **Tests.** T2 twice: `254 passed, 24 skipped` both runs (set a5de0beef100); the same-session PIN baseline is `246 passed, 24
  skipped`. Eight new test items; eight reds at the PIN for their stated reasons (4d is green at the PIN by design; its red is m5).
  Mutants m1-m6: each reds a named test for its stated reason. Regression input: one real record, 20,564 bytes.
- **Gates.** `lint_delta --base c19736d`: 0 new pyflakes hits, rc 0. `bash -n` R: rc 0. The boundary is untouched by the
  coordinator's five commits made during this lane (f86d5c6..be848a1).

## Files changed (working tree vs the PIN; final blobs)

| file | blob | +/- | where |
|------|------|-----|-------|
| proofs/S0-02/tools/pc/deliver_event.py (D) | a2d0f014 | +29 -11 | usage :4-6 · docstring :29-33 · `REUSE_FLIP_REFUSE_TEXT` :83-91 · `--flip-signature` help :200-201 · the refusal :203-204 · the flip, moved out of the reuse branch to after the sign/reuse choice, :222-230 |
| proofs/S0-02/tools/pc/run_s0_02_legs.sh (R) | 448dcece | +5 -5 | the `neg-bad-signature)` branch :254-263 (still 10 lines; the file still 319) |
| proofs/S0-02/check_buzz_authz.py (C) | 9182b042 | +14 -3 | `_check_bundle_uncapped` :883-899 (item 5 only) |
| tests/test_s0_02_buzz_authz.py (T2) | 454f81b9 | +242 -9 | the `.probe` pin :2084-2094 · `_OwnedListener` docstring :2399 and body read :2433-2442 · `_run_deliver_cli` `fixture`/`extra` :2459-2476 · a falsified docstring fixed :3729-3732 · the B12 section :3898-4107 |
| proofs/S0-02/fixtures/regression-neg-bad-signature-live-probe-prompt.jsonl | bf199157 | new, 20,564 B | the regression input (section 4) |
| tasks/briefs/s0-02-support/B12-report.md | — | new | this report |

## 1. Premise re-measurement (2026-09-23T15:32Z, /home/user/agent-factory @ f86d5c6, boundary at c19736d) — ALL MATCH

```
$ date -u +%Y-%m-%dT%H:%MZ
2026-09-23T15:32Z
$ git log --format="%h %s" -1 c19736d | cut -c1-100
c19736d B11 landed (task #191; GATED-PENDING-VERIFY, batched into VERIFY-S0-02): S0-02's four seed n
$ for f in <boundary>; do echo "$(git rev-parse c19736d:$f) $f"; done      (PIN; HEAD f86d5c6 and the working tree: identical)
334fd28eadaf93f32a2ac9c39fc83a1e6bc1411c proofs/S0-02/tools/pc/deliver_event.py
0394b68db1e928da6b04d9a6a63aa43a277f0a46 proofs/S0-02/tools/pc/run_s0_02_legs.sh
612c6143ec5314ecd52c04c4c05c19e451fce0b2 proofs/S0-02/check_buzz_authz.py
5e11a6fbf8f392009dca1bca07c4b117376f8878 tests/test_s0_02_buzz_authz.py
$ grep -n "\.probe\|flip-signature" R
257:      deliver pos-allowed "$out/.probe" "$(role_for pos-allowed)"
259:        --reuse "$out/.probe/delivered-event.json" --flip-signature
260:      rm -rf "$out/.probe"
$ grep -n "flip_signature\|SIG_FLIP_BYTE_INDEX\|args.reuse" D
55:SIG_FLIP_BYTE_INDEX = -1
196:    if args.reuse:
197:        event = json.loads(Path(args.reuse).read_text())
198:        if args.flip_signature:
200:            sig[SIG_FLIP_BYTE_INDEX] ^= 0x01
$ grep -n "\.probe" T2
2084:    assert removed_nested == {".probe"}
$ grep C (the brief's pattern)    395 _observe_all · 848 _check_bundle_uncapped · 868 DISTINCT_FIXTURES · 883 revoked skip · 921 _observed_row · 958 denial-mode revoked
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_02_buzz_authz.py
1 files set=a5de0beef100
$ sha256sum <scratchpad>/s002c1/legs7.tar.gz
aa4dde4b76386f79d174c3f90414ae56d5fa56f5c00c4c9aa1c188e0f6f63475
$ (per live leg: runner-grep prompts / checker c2a prompts; the relay receipt)
pos-allowed grep_prompts=1 c2a_prompts=1 c2a_new=1 accepted=True http=200
neg-unauthorized grep_prompts=0 c2a_prompts=0 c2a_new=0 accepted=False http=400 restricted: not a channel member
neg-bad-signature grep_prompts=1 c2a_prompts=1 c2a_new=1 accepted=False http=400 invalid: invalid schnorr signature
neg-replayed/first grep_prompts=1 c2a_prompts=1 c2a_new=1 accepted=True http=200
neg-replayed/second grep_prompts=0 c2a_prompts=0 c2a_new=0 accepted=True http=200 duplicate:
neg-stale grep_prompts=0 c2a_prompts=0 c2a_new=0 accepted=False http=400 invalid: event timestamp too far from server time
neg-self-authored grep_prompts=0 c2a_prompts=0 c2a_new=0 accepted=True http=200
neg-not-allowlisted grep_prompts=0 c2a_prompts=0 c2a_new=0 accepted=True http=200
$ python3 proofs/S0-02/check_buzz_authz.py proofs/S0-02/evidence; echo rc=$?   (scratch /tmp/b12/pin = git archive c19736d of
  proofs/S0-02 + proofs/S0-01 without its evidence, plus the seven live legs as proofs/S0-02/evidence; C blob 612c6143)
failure_reason: neg-bad-signature: 1 ACP session/prompt turn(s), expected 0
rc=1
$ python3 <scratchpad>/a1_repro.py   (cwd /tmp/b12/pin, the PIN's C and fixtures)
unmutated: PASS -> PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, 6 distinct reasons; replay refused b
revoked carries neg-stale text: PASS -> PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, 6 distinct reasons; replay refused b
revoked carries neg-unauthorized text: PASS -> PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, 6 distinct reasons; replay refused b
```
The T2 baseline (246 passed, 24 skipped x2) is re-run below as the red/green baseline (section 5).

## 2. Caller grep for `--reuse` with `--flip-signature` (before any edit, whole tree, wider than the brief's `proofs/ scripts/`)

Run before any edit, so every line number below is the PIN's (written `path@c19736d:NN`; the tree then equalled the PIN).
```
$ git grep -n -e '--flip-signature' -e 'flip_signature'          (every tracked file)
docs/INCIDENT-LOG.md@f86d5c6:552     `AF-AP-156` row (prose; the row sits at :558 since the coordinator's later commits)
proofs/S0-02/tools/pc/deliver_event.py@c19736d:186   the argparse definition
proofs/S0-02/tools/pc/deliver_event.py@c19736d:198   the reuse-branch flip
proofs/S0-02/tools/pc/run_s0_02_legs.sh@c19736d:259  `--reuse "$out/.probe/delivered-event.json" --flip-signature`   <- the ONE executable caller
tasks/briefs/pc/patch-pc-b9.md--71463f3.diff, tasks/briefs/pc/pc-b9.md:108, transcripts/pc/pc-b9.md--71463f3.md, B12-brief.md   (prose/quotes)
$ git grep -n -e '--reuse' -- '*.sh' '*.py'                        (every tracked shell/python file)
proofs/S0-02/tools/pc/deliver_event.py@c19736d:5,26,185   usage, docstring, argparse
proofs/S0-02/tools/pc/run_s0_02_legs.sh@c19736d:239       `--reuse "$out/first/delivered-event.json"`   (the replay leg: --reuse ALONE)
proofs/S0-02/tools/pc/run_s0_02_legs.sh@c19736d:259       the bad-signature branch (removed by this lane)
tests/test_s0_02_buzz_authz.py@c19736d:1995,3171,3172,3178  the output-write parser and the B9 fake deliver (parses --reuse; never passes --flip-signature)
$ git ls-files --others --exclude-standard | xargs -r grep -ln -e '--flip-signature'   -> nothing (rc 123 = xargs over grep's "no match")
```
After this lane, no caller passes both: the PIN's `--reuse "$out/.probe/delivered-event.json" --flip-signature` (R@c19736d:259) is
gone (section 6 greps again).

## 3. Grounding notes (Phase 1)

- GitNexus `impact main --file proofs/S0-02/tools/pc/deliver_event.py`: LOW, 1 caller (its own `__main__`); R's shell call and T2's
  subprocess calls are invisible to the graph (a subprocess edge), so the caller grep above is the instrument for the flag.
- GitNexus `impact _check_bundle_uncapped`: the S0-02 candidate is `risk: UNKNOWN`, no callers resolved (it is passed BY REFERENCE
  to `_check_with_timeout`). Text search at the PIN: its one caller is `check_bundle`
  (`return _check_with_timeout(90, _check_bundle_uncapped, root, anchors)`, C@c19736d:918); `check_bundle`'s callers are `main`
  (`print(check_bundle(root, anchors))`, C@c19736d:1026) and T2's `_run_checker` (`return checker.check_bundle(`, T2:75).
- graft `ask` found the symbols lexically only ("no structural entries for deliver_event.py").
- The builder (READ-ONLY) loads D and uses ONLY `deliver_event._normalise` (build_fixtures.py:419), which this lane does not touch;
  it keeps its own `SIG_FLIP_BYTE_INDEX = -1` (build_fixtures.py:88).
- LINE-CITATION CONSTRAINT: `run_s0_02_legs.sh:305-306` (the two `collect_masked` sub-leg lines, accurate at the PIN) is cited
  three times:
  - proofs/S0-02/tools/build_fixtures.py:540 — a `run_s0_02_legs.sh` comment in a file that is READ-ONLY for this lane;
  - C:617 — the `_check_one_process` docstring (`PROCESS_START_BANNER` line);
  - T2:1319 — the `masked log` docstring.
  So R's edit keeps the branch at exactly 10 lines (254-263) and every later R line where it was. C's edit sits inside
  `_check_bundle_uncapped` (from C:848 on); every C citation in R and T2 points below 848, so none moves.
- The live timeline (11 records): the probe's `session/new` result alone is 902,155 bytes; the one c2a `session/prompt` is record 7
  (20,563 bytes + newline). The probe's turn lands AFTER the flipped delivery's t0: t0 1790174403 = 14:40:03Z; session/new
  14:40:03.873Z; session/prompt 14:40:07.767Z. So "count only the prompts after the flipped delivery" cannot be done with t0
  (the time filter still counts the probe turn); it needs a turn-order rule ("skip the setup turn"). m5 is built that way
  (section 7), and the time variant is run for the record.
- The synthetic anchors differ from the real ones (evidence-pass/identities.json and evidence-pass/fixtures/neg-bad-signature.json
  both differ from the repo's), so the live leg's other files cannot be graded inside the pass bundle; only the timeline record
  is swapped in.

## 4. The regression input (item 4d)

- NAME: `proofs/S0-02/fixtures/regression-neg-bad-signature-live-probe-prompt.jsonl` — 20,564 bytes (limit 1 MB), sha256
  `239591ed1c15b378688eac94534605d7cc2232dbd197b861a21a08b4c35e87ea`.
- CONTENT: record 7 of the live `legs/neg-bad-signature/timeline.jsonl`, exact bytes plus its newline, read from the tarball after
  `sha256sum -c` on aa4dde4b… (the tarball member = the extracted file, sha256 5ad855ce…). Written by a script that asserts the
  file has 11 records, record 7 is `('c2a', 'session/prompt', 7)`, and it is the ONLY c2a session/prompt record.
- SCREENED before copying (values never printed): six 64-hex strings, all PUBLIC — 3x the probe event id (the flipped event keeps
  that id), 1x the owner pubkey, 2x the agent pubkey (matched by name against identities.json, identities-s0-02.json and the leg's
  delivered events); the one key-named match is the env var NAME `BUZZ_PRIVATE_KEY` in the Buzz CLI help text, with no value; no
  nsec, `sk-`, bearer, password or api-key pattern.
- WHY IT SUFFICES: the checker's turn count (`_prompt_frames`, C:190-203) counts only records with `dir == "c2a"` and
  `frame.method == "session/prompt"`; S0-01's reader (`_load_timeline_raw`) parses each line alone (no seq continuity, no pairing);
  for a zero-turn leg the count is compared before anything else in the timeline is read. The live leg holds exactly ONE such record,
  so every smaller subset has zero prompts (and would not reproduce), and every larger subset has the same count. Measured with the
  PIN's C:
  ```
  (a) the full live bundle:                                   failure_reason: neg-bad-signature: 1 ACP session/prompt turn(s), expected 0   rc=1
  (full) pass bundle + 926754-byte live timeline:             failure_reason: neg-bad-signature: 1 ACP session/prompt turn(s), expected 0   rc=1
  (one) pass bundle + 20564-byte live timeline (this input):  failure_reason: neg-bad-signature: 1 ACP session/prompt turn(s), expected 0   rc=1
  ```
- The test pins the sha256 and the record identity, so a later hand edit of the input reds.

## 5. Red at the PIN (tests written first)

Scratch `/tmp/b12/red` = `git archive c19736d` (proofs, seeds, tests/conftest.py, pyproject.toml) + ONLY my T2 and the regression
input; D, R, C are the PIN blobs (334fd28e, 0394b68d, 612c6143, hash-object checked). 2026-09-23T15:48:17Z:
```
FAILED test_leg_file_table_matches_the_runner_writes                     assert {'.probe'} == set()
FAILED test_pc_runner_bad_signature_leg_makes_one_flipped_delivery       trace: 'pos-allowed …/neg-bad-signature/.probe owner',
                                                                          'neg-bad-signature …/neg-bad-signature owner --reuse …/.probe/delivered-event.json --flip-signature'
FAILED test_cli_flip_signature_posts_one_corrupted_template_event        the --flip-signature path posted an event that verifies
FAILED test_flip_signature_keeps_the_still_verifies_refusal              DID NOT RAISE SystemExit
FAILED test_cli_refuses_reuse_with_flip_signature_before_any_request     (0, b"deliver…", '') == (1, b'', '--f…AF-AP-156)\n')   (rc 0: the PIN posts)
FAILED test_bundle_refuses_a_revoked_receipt_carrying_another_classes_text[neg-bad-signature]   DID NOT RAISE Failure
FAILED test_bundle_refuses_a_revoked_receipt_carrying_another_classes_text[neg-replayed]        DID NOT RAISE Failure
FAILED test_bundle_refuses_a_revoked_receipt_carrying_another_classes_text[neg-stale]           DID NOT RAISE Failure   (B11's A1)
8 failed, 11 passed, 259 deselected in 17.41s
```
Green among the 11 at the PIN, by design: `test_live_bad_signature_probe_turn_fails_the_committed_checker` (4d pins a CORRECT
verdict of the committed checker; its red side is mutant m5), the four B6/B8 CLI tests that use the owned listener (it now also
reads the body), two `_privkey` tests, three torn-timeline CLI tests (the `cli_` pattern selected them) and
`test_revoked_denial_is_read_from_the_observation` (docstring-only change).

## 6. Green after, and the gates

```
$ (the same selection, shared tree, after the D/R/C edits) 2026-09-23T15:51:02Z
19 passed, 259 deselected in 14.45s                                                        rc=0
$ /tmp/b12/outputs.sh (2 bundle-mode + 14 --denial runs over evidence-pass and evidence-blanket, rc+stdout+stderr), PIN C vs new C
dd0e5f856c1536b2064e794f6252063e3435193b6801fe3649fb1106a6dbbe57  /tmp/b12/outputs-pin.txt
dd0e5f856c1536b2064e794f6252063e3435193b6801fe3649fb1106a6dbbe57  /tmp/b12/outputs-after.txt       cmp: BYTE-IDENTICAL
$ (new C, blob 9182b042, over the seven live legs; the PIN C gives the same lines)
bundle:              failure_reason: neg-bad-signature: 1 ACP session/prompt turn(s), expected 0   rc=1
--denial x6:         denied: sender-not-in-allowlist / neg-bad-signature: 1 ACP ... expected 0 / denied: event-replayed /
                     denied: event-stale / denied: self-authored / denied: not-allowlisted          rc=1 each (identical to the PIN C)
$ T2 baseline at the PIN, same session (scratch clone /tmp/b12/base checked out at c19736d; blobs = the PIN's)   2026-09-23T15:52:42Z
246 passed, 24 skipped in 154.95s (0:02:34)                                                rc=0
$ T2 run 1 (shared tree)  2026-09-23T15:55:22Z
254 passed, 24 skipped in 157.68s (0:02:37)                                                rc=0
$ T2 run 2 (shared tree)  2026-09-23T15:58:04Z
254 passed, 24 skipped in 158.93s (0:02:38)                                                rc=0
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_02_buzz_authz.py
1 files set=a5de0beef100
$ python3 scripts/lint_delta.py --base c19736d
lint_delta (worktree vs c19736d): 8 .py changed, 0 NEW pyflakes hit(s), 0 removed           rc=0
  advisory AP-32 on T2 (hashing): verified — the pinned sha256 is the stored file's sha256 (sha256sum 239591ed…)
  advisory AF-AP-159 on tests/test_edit_snapshot_ap_screen.py: NOT this lane's file (committed after the PIN)
  (of the changed .py, mine are C, D and T2; the rest are commits after the PIN or S198A's working-tree edits)
$ python3 scripts/lint_delta.py          (bare)
lint_delta.py: error: one of the arguments --staged --base is required                       rc=2
$ bash -n proofs/S0-02/tools/pc/run_s0_02_legs.sh
rc=0
$ wc -l R (PIN, after): 319, 319; diff of R with lines 254-263 deleted on both sides: identical; R:305-306 still collect_masked first/second
```
Delta 246 -> 254 = the 8 new test items: the runner behavioural control, 4b, the kept refusal, 4c, 4d, and A1 x3 (neg-bad-signature,
neg-replayed, neg-stale texts). The set id is a hash of the path string, so it does not move when the file's contents do.

Caller grep AFTER (section 2's sweep, joined continuation lines): no production caller passes both flags. R:239 is `--reuse` alone
(the replay leg); R:259-260 is `deliver neg-bad-signature "$out" … --flip-signature`. The joined scan's other hits are prose (usage,
docstrings, the refusal text) and T2:4052, the one deliberate call that passes both to prove the refusal.

## 7. Mutant table (driver `/tmp/b12/mutants.py`; each mutant = its own copy of `/tmp/b12/mut-base` = `git archive c19736d`
##    (proofs, seeds, tests/conftest.py, pyproject.toml) + my five working-tree files; each replacement asserted to match exactly once;
##    bytecode off and every `__pycache__` purged per run; the shared tree is never touched) — 2026-09-23T16:04:12Z

Unmutated copy first: `9 passed in 8.67s` (the nine named items).

| id | mutation (file) | named test(s) that red — the assertion | stated reason, met? |
|----|-----------------|------------------------------------------|---------------------|
| m1 | R's branch = the PIN's lines 255-260: a probe `deliver pos-allowed "$out/.probe"`, then `--reuse … --flip-signature`, then `rm -rf "$out/.probe"` | `test_leg_file_table_matches_the_runner_writes`: `assert {'.probe'} == set()` · `test_pc_runner_bad_signature_leg_makes_one_flipped_delivery`: trace = `pos-allowed …/neg-bad-signature/.probe owner` + the reuse call (2 calls) | yes: the old two-call shape, seen in the source AND in the executed branch |
| m2 | D POSTs the valid event before flipping (a `_post` of the unflipped body inserted at the top of the flip block) | `test_cli_flip_signature_posts_one_corrupted_template_event`: `('flipped', 2)` (two requests) · also `test_flip_signature_keeps_the_still_verifies_refusal`: `assert 2 == 1` (its control call made 2) | yes: the valid event left the process |
| m3 | D: flip neutralized (`^= 0x00`) AND the still-verifies refusal deleted | `test_cli_flip_signature_posts_one_corrupted_template_event`: `the --flip-signature path posted an event that verifies` · `test_flip_signature_keeps_the_still_verifies_refusal`: `DID NOT RAISE SystemExit` | yes: a VALID event posted on the bad-signature path |
| m4 | D: the `--reuse` + `--flip-signature` refusal deleted | `test_cli_refuses_reuse_with_flip_signature_before_any_request`: `(0, b"deliver…", '') == (1, b'', '--f…AF-AP-156)\n')` | yes: accepted and posted |
| m5 | C, the REJECTED alternative: in `_check_leg`, for neg-bad-signature, `prompts = prompts[1:]` (count only the prompts after the setup/flipped delivery) | `test_live_bad_signature_probe_turn_fails_the_committed_checker`: `(0, 'PASS: S0…proof)\n', '') == (1, 'failure_…cted 0\n', '')` | yes: the setup turn hid and the bundle PASSED |
| m6 | C: the revoked grading removed (back to a bare `continue`) | `test_bundle_refuses_a_revoked_receipt_carrying_another_classes_text[neg-bad-signature / neg-replayed / neg-stale]`: `DID NOT RAISE Failure` x3 | yes: A1 back |
| m5t | (for the record, NOT a brief mutant) C, the TIME form of the rejected alternative: count only prompts whose `t_utc` >= the leg's t0 | none — 9 passed (SURVIVES) | see below: it cannot realize the rejected alternative |

m5 and m5t over the seven LIVE legs (`/tmp/b12/live-<m>` = the PIN scratch copy + the mutant C):
```
== m5 C over the seven live legs
bundle:  failure_reason: revoked: revoked leg directory absent            rc=1   (the bad-signature leg now PASSES; only revoked's absence stops the bundle)
--denial neg-bad-signature:  failure_reason: denied: signature-invalid      rc=1   <- a PROVEN seed denial on a leg that carries a real ACP turn
== m5t C over the seven live legs
bundle:  failure_reason: neg-bad-signature: 1 ACP session/prompt turn(s), expected 0   rc=1
--denial neg-bad-signature:  failure_reason: neg-bad-signature: 1 ACP session/prompt turn(s), expected 0   rc=1
```
Reading: the turn-order form (m5) is the only filter that hides the live probe turn, and it turns the spec's seed leg into a hollow
green — exactly the brief's reason for rejecting it; T2 kills it. The time form (m5t) survives T2 because it changes no verdict on
any input: the live probe turn lands 4.8 s AFTER the flipped delivery's t0 (section 3), and the regression record (2026-09-23) is
later than the synthetic leg's t0 (1788800000 = 2026-09-07). It is an equivalent mutant on every input this lane has, not a working
version of the rejected alternative.

## 8. DISCREPANCIES and deviations from the brief (each flagged; none changes a contract line)

1. **m5's form.** The brief words m5 as "count only the prompts after the flipped delivery". A t0-based time filter cannot do that
   on the live data (the probe turn lands 4.8 s after the flipped delivery's t0), so m5 is the turn-order filter
   (`prompts = prompts[1:]` for the leg), the only filter that hides the live probe turn. The time form was also run (m5t): it
   survives T2 and changes no verdict on the live legs either (section 7).
2. **4d is green at the PIN.** It pins a CORRECT verdict of the committed checker, so there is no red at the PIN to show; its red
   side is m5 (the bundle then PASSES).
3. **4a's fake `deliver`.** The B9 driver's fake is hardwired to `main … neg-replayed` and does not record argv, so the behavioural
   control has its own small driver (`_B12_DRIVER`, T2:3930) in the B9 pattern: it sources the whole runner in B9's scratch tree
   (`_b9_env`) and fakes only launch/post/deliver; the real `main`, `role_for`, `wait_turn_window`, `collect_leg`, `stop_leg` and
   `collect_masked` run.
4. **Added beyond a-d:** `test_flip_signature_keeps_the_still_verifies_refusal` (item 2's "keeps the existing refusal", executed
   with the verifier forced to accept, paired with an in-process control that posts once). 4b also compares the flipped path with
   the unflipped path through the real CLI (the restored event equals the unflipped event field for field), and A1's test is
   parametrized over the three relay classes whose text differs from revoked's (neg-bad-signature, neg-replayed, neg-stale; B11's
   reproduction is the neg-stale case).
5. **The refusal is stricter than "before any request":** it fires right after argument parsing, before the fixture read, the leg
   directory, the key read and the network (4c asserts no leg directory). It tests `args.reuse is not None`, so an empty
   `--reuse ""` with `--flip-signature` is refused too.
6. **Shared T2 helpers changed:** `_OwnedListener` now also reads the Content-Length body (4b grades the wire bytes);
   `_run_deliver_cli` gained `fixture="pos-allowed"` and `extra=()` (defaults keep every existing caller's argv). The four B6/B8
   CLI tests that use the listener stay green (the red run and both T2 runs).
7. **A falsified comment fixed in T2:** `test_revoked_denial_is_read_from_the_observation`'s docstring said the bundle never reads the
   revoked relay text; after item 5 it does (T2:3729-3732).
8. **The regression input is a single file**, not a directory (the brief allows either).

## 9. Adjacent defects (reported, NOT fixed)

- **AD1 — stale line citations, already wrong at the PIN** (read with `git show c19736d:…`; this lane's edits do not move them:
  C moved only from :883 on, R not at all). A quoted citation is written "C 569-574" (in words) so the linter reads only this
  report's own claims. Where the stale citations sit (current line numbers):
  - R:299 (`NOTHING at the leg root`) cites C 569-574 and C 143-149 for the replay closure.
  - R:302 (`scans only the second sub-leg's log`) cites C 609-610 for that scan.
  - T2:2218 (`both sub-legs`) and T2:3238 (`the leg shape`) cite C 569-574.
  - T2:3286 (`with M-B alone repaired`) and T2:3492 (`replay closure refuses`) cite C 569-574.
  - T2:3287 (`trips the turn count`), T2:3306 (`cumulative second`) and T2:3421 (`refuse at`) cite C 621-624.
  - T2:2387 (`Python exits 1 on a str SystemExit`) cites D 80 and D 85 for the two key-shape refusals.
  What those numbers held at the PIN, and where the cited code was:
  - C@c19736d:569-574 held the revoked ordering check (`if at >= t0:`), not the replay closure.
  - C@c19736d:143-149 held the `PROCESS_START_BANNER` / `LEG_NAMES` block.
  - C@c19736d:677 holds the replay closure (`set(REPLAY_SUBLEGS)`); C@c19736d:168 holds `def _leg_closure`.
  - C@c19736d:609-610 held a `frame_tee.py` docstring line; the scan is C@c19736d:725 (`found = _observe_all(sub_dir`).
  - C@c19736d:621-624 held a docstring and the `initialize` loop; the second-turn check is C@c19736d:736 (`if turns[1] != 0:`).
  - D@c19736d:80 held `def _privkey` and D@c19736d:85 a `nv.sign_event` docstring line.
  - The refusals were D@c19736d:89 and D@c19736d:94 (`raise SystemExit(`); after this lane, D:102 and D:107 (`raise SystemExit(`).
- **AD2 — an empty `--reuse ""` alone is read as absent** (`if args.reuse:` at D:212), so D signs a fresh event instead of refusing
  an empty path. Pre-existing; no caller passes an empty value.
- **AD3 — two copies of the flip index:** `SIG_FLIP_BYTE_INDEX = -1` at D:59 (D@c19736d:55) and again in the READ-ONLY builder,
  proofs/S0-02/tools/build_fixtures.py:88 (`SIG_FLIP_BYTE_INDEX = -1`). No test ties them; 4b uses D's.

## 10. Echo sweep (by hand; the registry file is outside this boundary)

- **AF-AP-156's class** (a negative leg's setup runs the positive path inside the window it observes).
  The registry row: `AF-AP-156` at docs/INCIDENT-LOG.md:558.
  S0-02's runner after B12: every leg makes ONE delivery except `neg-replayed`, which delivers twice by design (D-036: the first
  snapshot and the second delta are graded as separate sub-legs): `deliver pos-allowed` at R:226, `deliver neg-replayed` at R:238. S0-01's negative
  (`pc_negative.py`) runs its probe in its own wiped frame dir (`v2-negative`), not in a shared window. No other instance found.
  NOT read: the PC runners of S0-03, S0-04, S0-05, S0-06 and S0-08.
- **A1's class** (a leg kept out of one gate by design is graded by NO gate: the `continue` that exempted revoked from the
  distinctness keys and the named-observable check also exempted its text from every check). In C after B12, every leg's observable
  meets a grader in both modes: `_check_named_observable` (five legs), `_check_duplicate_receipt` (replay), `_observed_row`
  (revoked). NOT swept: the other proofs' checkers. No `AF-AP-*` row exists for this class; proposed row text (for the
  coordinator): *A LEG EXEMPTED FROM ONE GATE BY DESIGN IS EXEMPTED FROM ALL — a `continue` meant to keep a structurally-separated
  leg out of a cross-leg gate also skips its own observable check. Signature: a `continue` on a named leg inside a grading loop
  with no grader of that leg's observable on the skip path.*

## 11. NOT done

- **NOT run: any PC or live step** (lane rule). The new producer path has not met the real relay; the coordinator re-captures the
  eight legs.
- NOT run: the full tree. Run: T2 twice, the same-session PIN baseline, the selections, the mutants, the output comparisons.
- NOT committed, NOT pushed, NOT published.
- NOT written: registry rows (docs/INCIDENT-LOG.md is outside the boundary). The `/bug-echo` skill was not invoked; the sweep in
  section 10 was by hand and is bounded as stated there.
- NOT fixed: AD1-AD3.
- NOT run: the advisory instruments (sentrux, slopo, ripwire) and a GitNexus reindex; `detect_changes --scope all` was run
  (6 files = my four plus S198A's two, 41 symbols, risk low, 0 affected processes).

## 12. Evidence tiers

- **VERIFIED** (a probe from this session, pasted): the premise (every item); the caller grep before and after; the red run at the
  PIN (8 reds, each reason read); the green selection; T2 twice and the same-session PIN baseline; the 16-output byte identity;
  the live verdicts under the new C; the sufficiency three-way; mutants m1-m6 and m5t, and m5/m5t over the live legs; lint_delta;
  `bash -n`; R's line-count invariance; `detect_changes`; that the coordinator's commits during the lane left the boundary blobs
  at the PIN's.
- **INFERRED** (from code and the live capture, not run): the relay answers the new flipped event with
  `invalid: invalid schnorr signature` (the oracle pins that text to `ingest.rs:2213`, and the live run's flipped event already
  drew it); a re-captured bad-signature leg then passes the committed checker (the synthetic leg of the same shape passes, and the
  live leg's delivery fields already matched its contract).
- **ASSUMED:** none load-bearing. D's changed lines use only the standard library already in use on the PC.

## 13. Self-attack — the three likeliest ways this change is wrong

1. **The new path signs something other than what the unflipped path signs** (another created_at, tag order or key), so the leg
   would differ from a passing event in more than the signature. Ruled out: 4b runs BOTH paths through the real CLI with the same
   fixture, key and t0 and asserts the flipped event with its byte restored verifies and equals the unflipped event field for
   field (id, pubkey, created_at, sig); m3 (flip neutralized) and m2 (valid POST first) both red it.
2. **A valid event can still leave the process** (a request before the flip, or the reuse path). Ruled out: exactly one request per
   invocation, and that request fails verification (4b; m2 reds on `('flipped', 2)`); the combination with `--reuse` is refused at
   argument parsing with zero connections and no leg directory (4c; m4 reds); the runner calls `deliver` once (4a source pin and
   behavioural control; m1 reds both). INFERRED, not executed: an old runner fed to the new D still sends its probe, then its
   second call (the argv 4c refuses) exits 1 and `set -e` stops the run before `collect_leg`, so no leg timeline is written.
3. **Item 5 changes a verdict it should not** (the pass line, the blanket reason, a `--denial` output, the live legs), or picks the
   wrong row where revoked and neg-unauthorized share one text. Ruled out: the 16 outputs are byte-identical (sha dd0e5f85…
   before and after); the live verdicts are identical; T2 is green twice; the shared-text case resolves through the membership
   receipt exactly as `--denial revoked` does (the pass bundle's revoked leg carries `restricted: not a channel member` and passes).

## 14. Done-when check (2026-09-23T16:12:20Z; HEAD be848a1, whose boundary blobs are still the PIN's)

```
$ git status --short
 M proofs/S0-02/check_buzz_authz.py                     <- mine (C)
 M proofs/S0-02/tools/pc/deliver_event.py               <- mine (D)
 M proofs/S0-02/tools/pc/run_s0_02_legs.sh              <- mine (R)
 M scripts/transcript_export.py                         <- S198A (not touched)
 M tests/test_s0_02_buzz_authz.py                       <- mine (T2)
 M tests/test_transcript_export.py                      <- S198A (not touched)
?? proofs/S0-02/fixtures/regression-neg-bad-signature-live-probe-prompt.jsonl   <- mine (the regression input)
?? tasks/briefs/continuity/S198A-report.md             <- S198A (not touched)
?? tasks/briefs/laya/VERIFY-J1-1-R2-report.md          <- the J1-1-R2 verifier (not touched)
?? tasks/briefs/s0-02-support/B12-report.md            <- mine (this report)
$ python3 scripts/report_lint.py --map C=… --map D=… --map R=… --map T2=… --min-refs 5 tasks/briefs/s0-02-support/B12-report.md
report_lint: 56 refs — OK 47, NEAR 0, MISS 0, UNCHECKABLE 9, UNRESOLVED 0 (worktree)            rc=0   (three rounds, the bound)
```
Final blobs (unchanged since both T2 runs and the mutant base): D a2d0f014, R 448dcece, C 9182b042, T2 454f81b9 (the same T2 bytes
the red run used), the regression input bf199157. Scratch trees used (all under /tmp/b12; none in the shared tree): pin, red, base
(a local clone checked out at the PIN, for the same-session baseline), mut-base and m1…m6, m5t, live-after, live-m5, live-m5t,
suff-full, suff-one.
