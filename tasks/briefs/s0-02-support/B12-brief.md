# B12 — S0-02's bad-signature leg delivers ONE corrupted event, and the bundle grades the revoked leg's relay text (task #196)

PIN: c19736d (the origin commit of B11's landing; the boundary is byte-identical at the origin head 0dfd28e; blob ids in the premise
block; re-measure them first).
LANE: s0-02-b12 (sandbox; agent `code-implementer`, in the SHARED tree, no worktree isolation). Honey `ultra` Lever-2: your report is
DATA: files:lines, pasted counts, discrepancies, NOT-done. Do NOT spawn subagents.

WHY THIS LANE EXISTS (AF-AP-156; incident 2026-09-23 14:5xZ). The first live S0-02 capture (seven owner-free legs, PC, 14:37:08Z to
14:50:16Z, rc 0, runner head fa4532e) failed the committed checker on one leg:
`failure_reason: neg-bad-signature: 1 ACP session/prompt turn(s), expected 0`. The relay rejected the flipped event for the right
reason (`400 {"error":"invalid: invalid schnorr signature"}`). The prompt is the runner's own: `deliver_event.py` can flip a signature
only on a `--reuse` event, so the runner's `neg-bad-signature)` branch first POSTs a valid `pos-allowed` event (`$out/.probe`) into the
SAME buzz-acp process, then reuses it with one byte flipped, and `collect_leg` copies the whole timeline. The checker is right; the
producer is wrong. Every other live leg matched its contract (the per-leg table is in the premise block).

REJECTED ALTERNATIVE (do not build it): teach the checker to count only the prompts after the flipped delivery. A real acceptance of a
bad signature could then hide behind a setup turn, and the checker would be fitted to a defective producer.

BOUNDARY (exact): MODIFY `proofs/S0-02/tools/pc/deliver_event.py` (D), `proofs/S0-02/tools/pc/run_s0_02_legs.sh` (R),
`proofs/S0-02/check_buzz_authz.py` (C, for item 5 only), `tests/test_s0_02_buzz_authz.py` (T2); CREATE one regression-input file or directory under `proofs/S0-02/fixtures/` (name it in the
report; at most 1 MB added) and `tasks/briefs/s0-02-support/B12-report.md` (write it incrementally from the start). READ-ONLY:
`proofs/S0-02/spec.json`, `proofs/S0-02/oracle/`, every other fixture,
`proofs/S0-02/tools/build_fixtures.py`, everything under `proofs/S0-01/`. The live seven-leg bundle is at
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/s002c1/legs7.tar.gz` (and its extracted tree `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/s002c1/legs/`) (sha256 aa4dde4b76386f79d174c3f90414ae56d5fa56f5c00c4c9aa1c188e0f6f63475 for the tarball; read it, never edit it).

## The contract

1. **Premise first.** Re-measure the premise block. On a mismatch in the boundary, stop CONTRACT-INVALID and report what differs.
2. **D — sign and corrupt in one call.** `--flip-signature` without `--reuse` signs the fixture's template exactly as the unflipped
   path does, flips byte `SIG_FLIP_BYTE_INDEX`, keeps the existing refusal of an event that still verifies, and POSTs only the
   corrupted event: exactly ONE HTTP request per invocation, and the valid event never leaves the process. `--reuse` together with
   `--flip-signature` is refused before any request, with a named message (grep the tree first and paste that no caller still passes
   both; the replay leg passes `--reuse` alone). The receipt, `delivered-event.json`, `t0.json` and `fixture.json` keep their shapes.
3. **R — one delivery.** The `neg-bad-signature)` branch makes exactly one `deliver` call (`neg-bad-signature`, its own role,
   `--flip-signature`), then `wait_turn_window 0` and `collect_leg "$out"`. No `.probe`, no reuse, no nested directory.
4. **T2 — tests (normal, failure, boundary).**
   a. The old `.probe` pin (`removed_nested == {".probe"}`) becomes a pin that the branch creates no nested directory and calls
      `deliver` once, paired with a behavioral control (AF-AP-80): the branch run against the test harness's fake `deliver` records
      exactly one call with `--flip-signature` and no `--reuse`.
   b. D's new path against an owned loopback listener (the B6 pattern in T2): exactly one request reaches the listener; the posted
      event fails verification; flipping the byte back makes it verify; its content, kind and tags equal the fixture template.
   c. The refusal of `--reuse` with `--flip-signature`: the exact rc and message, and zero connections to the listener.
   d. The regression (AF-AP-36; AF-AP-42's fix): the committed checker C, run on a bundle whose bad-signature timeline carries the
      live probe turn, fails with exactly `neg-bad-signature: 1 ACP session/prompt turn(s), expected 0`. The input carries REAL
      producer bytes copied from the live leg, never hand-written lines; choose the smallest real input that reproduces the exact
      reason (the live leg's `timeline.jsonl` is 926,754 bytes; a subset of its lines is fine if the reason still reproduces), and
      state in the report why that input is sufficient.
5. **C — the bundle grades the revoked leg's relay text (A1, B11's report section 8).** Today `_check_bundle_uncapped` excludes
   revoked from the distinctness keys and skips it in the named-observable loop, and `_observe_all` needs only SOME known observable,
   so a revoked receipt that carries another class's text (B11's reproduction: the stale text) PASSes, at B11's PIN and after it.
   The bundle must refuse that with a named failure, as the `--denial revoked` mode already does (`_observed_row`); the pass bundle's
   PASS line, the blanket leg's reason and every `--denial` output stay byte-identical. Write B11's reproduction as a test first
   (red at the PIN, green after; paste both).
6. **Mutants (each on a scratch copy; never in the shared tree).** m1 the branch sends the probe again (the old two-call shape);
   m2 D POSTs the valid event before flipping; m3 D drops the still-verifies refusal and the flip is neutralized; m4 D accepts
   `--reuse` with `--flip-signature`; m5 on a scratch copy of C, the rejected alternative (count only the prompts after the flipped
   delivery); m6 on C, the revoked grading removed (the A1 test must red). Each must red a named test for the stated reason; paste
   the table.
7. **Gates.** T2 twice with identical counts, with its set id (`bash scripts/pc_suite.sh set-id -- tests/test_s0_02_buzz_authz.py`);
   `python3 scripts/lint_delta.py --base <PIN>` (a bare call exits 2); `bash -n` on R. NOT in this lane: any PC run. The coordinator re-captures all eight legs after
   the landing.

## Done when

- `git status --short` shows only boundary paths (and the other lanes' files, which you name and do not touch).
- The report pastes: the premise re-measurement, the grep for `--reuse … --flip-signature` callers, the regression input's name,
  size and why it suffices, the mutant table, both T2 runs and the set id, and anything NOT done.

## PREMISE — MEASURED at authoring (2026-09-23 15:28Z, /home/user/agent-factory@0dfd28e, the boundary at c19736d)

```
$ date -u +%Y-%m-%dT%H:%MZ
2026-09-23T15:28Z
$ git log --format="%h %s" -1 c19736d | cut -c1-100
c19736d B11 landed (task #191; GATED-PENDING-VERIFY, batched into VERIFY-S0-02): S0-02's four seed n
$ for f in <boundary>; do echo "$(git rev-parse c19736d:$f) $f"; done
334fd28eadaf93f32a2ac9c39fc83a1e6bc1411c proofs/S0-02/tools/pc/deliver_event.py
0394b68db1e928da6b04d9a6a63aa43a277f0a46 proofs/S0-02/tools/pc/run_s0_02_legs.sh
612c6143ec5314ecd52c04c4c05c19e451fce0b2 proofs/S0-02/check_buzz_authz.py
5e11a6fbf8f392009dca1bca07c4b117376f8878 tests/test_s0_02_buzz_authz.py
$ grep -n "\.probe\|flip-signature" proofs/S0-02/tools/pc/run_s0_02_legs.sh
257:      deliver pos-allowed "$out/.probe" "$(role_for pos-allowed)"
259:        --reuse "$out/.probe/delivered-event.json" --flip-signature
260:      rm -rf "$out/.probe"
$ grep -n "flip_signature\|SIG_FLIP_BYTE_INDEX\|args.reuse" proofs/S0-02/tools/pc/deliver_event.py
55:SIG_FLIP_BYTE_INDEX = -1
196:    if args.reuse:
197:        event = json.loads(Path(args.reuse).read_text())
198:        if args.flip_signature:
200:            sig[SIG_FLIP_BYTE_INDEX] ^= 0x01
$ grep -n "\.probe" tests/test_s0_02_buzz_authz.py
2084:    assert removed_nested == {".probe"}
$ grep -n "DISTINCT_FIXTURES\|def _check_bundle_uncapped\|def _observe_all\|def _observed_row\|if fixture_name != \"revoked\"\|revoked" proofs/S0-02/check_buzz_authz.py | head -30
395:def _observe_all(leg_dir: Path, leg: str, delivery: dict, fixture_name: str) -> frozenset:
506:        _LEG_FILES_REVOKED if fixture_name == "revoked" else _LEG_FILES_PLAIN,
555:    if fixture_name == "revoked":
596:    if fixture_name == "revoked":
848:def _check_bundle_uncapped(root: Path, anchors: "Anchors") -> str:
868:    distinct_legs = list(oracle.DISTINCT_FIXTURES)
883:        if fixture_name == "revoked":
921:def _observed_row(leg: str, found: frozenset, removal_receipt: bool) -> dict:
937:        rows = [r for r in rows if (r["fixture"] == "revoked") == removal_receipt]
958:        if fixture_name != "revoked":
$ grep -rn --include='*.sh' --include='*.py' -e '--reuse' -e '--flip-signature' proofs/ scripts/ | cut -c1-140   (15:3xZ)
proofs/S0-02/tools/pc/run_s0_02_legs.sh:239:        --reuse "$out/first/delivered-event.json" \
proofs/S0-02/tools/pc/run_s0_02_legs.sh:259:        --reuse "$out/.probe/delivered-event.json" --flip-signature
proofs/S0-02/tools/pc/deliver_event.py:5:                     --relay-http <http://127.0.0.1:PORT> --t0 <epoch> [--reuse <event.json>]
proofs/S0-02/tools/pc/deliver_event.py:26:created_at offset) and the role key supplies the signature. `--reuse` posts a
proofs/S0-02/tools/pc/deliver_event.py:185:    ap.add_argument("--reuse", help="post this already-signed event verbatim")
proofs/S0-02/tools/pc/deliver_event.py:186:    ap.add_argument("--flip-signature", action="store_true",
$ for i in 1 2; do python -m pytest -q -p no:cacheprovider --basetemp /tmp/b11g/bt$i tests/test_s0_02_buzz_authz.py | tail -1; done   (15:1xZ, the same bytes as c19736d)
246 passed, 24 skipped in 143.50s (0:02:23)
246 passed, 24 skipped in 144.72s (0:02:24)
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_02_buzz_authz.py
1 files set=a5de0beef100
$ sha256sum <scratchpad>/s002c1/legs7.tar.gz
aa4dde4b76386f79d174c3f90414ae56d5fa56f5c00c4c9aa1c188e0f6f63475
$ (per live leg: session/prompt lines in timeline.jsonl; the relay receipt)
pos-allowed prompts=1 accepted=True http=200
neg-unauthorized prompts=0 accepted=False http=400 restricted: not a channel member
neg-bad-signature prompts=1 accepted=False http=400 invalid: invalid schnorr signature
neg-replayed/first prompts=1 accepted=True http=200
neg-replayed/second prompts=0 accepted=True http=200 duplicate:
neg-stale prompts=0 accepted=False http=400 invalid: event timestamp too far from server time
neg-self-authored prompts=0 accepted=True http=200
neg-not-allowlisted prompts=0 accepted=True http=200
$ python3 proofs/S0-02/check_buzz_authz.py proofs/S0-02/evidence; echo rc=$?   (15:3xZ; a scratch copy = git archive c19736d of proofs/S0-02
  and proofs/S0-01 without its evidence, plus the seven live legs as proofs/S0-02/evidence; C's blob 612c6143, the PIN's)
failure_reason: neg-bad-signature: 1 ACP session/prompt turn(s), expected 0
rc=1
$ python3 <scratchpad>/a1_repro.py   (15:3xZ; C, the oracle and fixtures/evidence-pass byte-identical to c19736d; the bundle mode
  on a copy of evidence-pass whose legs/revoked/delivery.json message is set to the neg-stale row's observable, as T2's
  test_revoked_denial_is_read_from_the_observation does)
unmutated: PASS -> PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, 6 distinct reasons; replay refused b
revoked carries neg-stale text: PASS -> PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, 6 distinct reasons; replay refused b
```
