# PC lane — VERIFY-S0-02 (adversarial verification of the S0-02 mint: the live eight-leg capture)

PIN: a78bdca

Role: adversarial-verifier. Route: the LOCAL Qwen verify route (`agentfactory-verify-local`, xhigh; the pc_lane.sh
default for adversarial-verifier; do NOT set HERMES_MODEL). Venue: `tasks/briefs/pc/VENUE-MAP.md`. Read it first.
Report: write a draft after EACH item to `tasks/briefs/s0-02-support/VERIFY-S0-02-report.md`, and return it whole as
your final message. You VERIFY; you never fix. Every finding is bounded by file:line, reproduced through the real path,
and graded by the blocking predicate: contract-mapped, reproduced canonically, materially effective, a concrete
discriminator, in-boundary. Emit a GATE RECOMMENDATION (MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY /
CONTRACT-INVALID), never a verdict. The coordinator decides. Under D-034, a non-blocking finding becomes a
`verify-followup` issue.

Authorization: this is defensive verification of the owner's own system. The negative legs (unauthorized sender, bad
signature, replay, stale event, revoked member) are authorization fixtures on an isolated test relay.

## What is under verification (read WHOLE, in this order)
1. The mint commit (its message is the reasoning record) and the ledger's **S0-02 MINTED** note in
   `todo/BUILD-TASKLIST.md`.
2. The FROZEN CONTRACT: `seeds/seed-stage0-v1.yaml`, the S0-02 block (three assertions plus the four-distinct-reasons
   rule), `proofs/S0-02/spec.json` (the legs and `limits`), the checker `proofs/S0-02/check_buzz_authz.py`, the oracle
   `proofs/S0-02/oracle/denial_table.py`, and the runner `proofs/S0-02/tools/pc/run_s0_02_legs.sh`.
3. The MINTED artifact `proofs/S0-02/result.json`, `proofs/ledger.json` (S0-02 PRESENT), the evidence root
   `proofs/S0-02/evidence/` (8 legs; the replay leg has `first/` and `second/`), `proofs/S0-02/fixtures/PROVENANCE.md`
   (the production-evidence section), and the raw capture records under
   `tasks/briefs/s0-02-support/live-capture-2026-09-23/`.
4. THREE LANDINGS BATCHED INTO THIS VERIFY (each GATED-PENDING-VERIFY until it lands): B10 `8d8c97e` (the fixture
   signers follow D-037/D-038: revoked signs as owner2, neg-unauthorized binds to nonmember; the identity merge
   refuses a collision or a non-hex key), B11 `c19736d` (`--denial <fixture>`: the four seed negative legs graded one
   at a time, the F16 floor, AF-AP-158), B12 `321bcee` (the bad-signature leg delivers ONE corrupted event; the
   revoked leg graded through `_observed_row`, A1; AF-AP-160). Read each commit message (the reasoning record) and
   its lane report `tasks/briefs/s0-02-support/B1{0,1,2}-report.md`. B10's D3/D4 follow-ups are already filed
   (issue #45): confirm them, do not re-file them.

## Attack list (each item: what you did, the exact command, the exact output, SOLID/UNSURE)
V1 PROVENANCE, independently. Recompute a sha256 manifest of the 55 committed evidence files. Bind the revoked
   receipt (`evidence/revoked/membership.json`) to the raw records, field by field:
   - `removed_pubkey` = owner2 in `proofs/S0-02/fixtures/identities-s0-02.json`;
   - `at_epoch_s` = the CLI's `at=` in `owner-removal-cli-output.txt`;
   - `http_status` = the relay's `HTTP bridge request` line right after the ingest line in `relay-log-574-577.jsonl`;
   - the event id = the one in the CLI JSON and in `relay-log-removal-lines.jsonl`;
   - `at_epoch_s` < the revoked leg's `t0.json`.
   Then state plainly what the receipt does NOT prove: `spec.json` `limits` says unauthenticated and not end-to-end.
   Is anything in the evidence stronger than the limit claims, or weaker?
V2 HOSTILE BUNDLES from the REAL evidence (the pre-mint gate, AF-AP-36). Build each on a SCRATCH COPY of the root.
   Each must fail with a NAMED reason; a survivor is a finding:
   (a) swap two negative legs' `delivery.json`;
   (b) append a second `session/prompt` record to `neg-replayed/second/timeline.jsonl`;
   (c) change the second replay receipt's `message` from `duplicate:` to `""`;
   (d) change the second replay delivery's event id so it no longer echoes the first;
   (e) move the revoked receipt's `at_epoch_s` after the leg's t0;
   (f) delete one leg directory; add one extra file inside a leg; replace a leg directory with a symlink;
   (g) make `pos-allowed` carry two prompts;
   (h) re-sign `neg-bad-signature`'s event validly (the B12 shape);
   (i) at least three shapes of your own.
   Paste the checker line for each.
V3 DISTINCTNESS on the live data. List the six negative legs' observables, as the checker keys them, from the evidence
   files. Confirm that neg-unauthorized and revoked share one key by design and that the receipt alone separates
   them. Answer: could a live capture in which the relay answered every negative leg with one text still pass? Use
   the synthetic blanket bundle's spec leg as the reference.
V4 THE THREE SEED ASSERTIONS against the evidence:
   (1) exactly one ACP session/turn for `pos-allowed`: count them in its timeline;
   (2) revocation "independent of NIP-OA created_at": does the revoked leg's event, or any leg, show that a valid
       signature and a fresh created_at do NOT survive the removal? Say precisely what is and is not demonstrated;
   (3) duplicate delivery: identical event ids, the `duplicate:` receipt, ONE buzz-acp process (count the
       `buzz-acp starting:` lines in the masked logs), zero prompts in the second delta.
   Answer each as the seed's WORDS demand, citing lines.
V5 THE MINT's attested inputs (AF-AP-56). Run `python3 scripts/validate-ledger integrity --root .` and expect S0-02
   PRESENT. Re-run `python3 scripts/proof-runner run --proof S0-02 --venue pc-bridge --root <a scratch copy of the
   tree>`, then diff the new `result.json` against the committed one and name every differing key and why. Show that
   `python3 scripts/ledger-gen --root <copy>` reproduces `proofs/ledger.json`.
V6 THE TEST PIN as a gate: `tests/test_s0_02_buzz_authz.py::test_real_evidence_root_is_the_minted_live_capture`. On a
   SCRATCH COPY of the repo, delete one leg, then separately corrupt the receipt: the test must fail each time. Then
   mutate the CHECKER on the copy (e.g. skip the revoked-leg receipt check) and name which tests kill it. A survivor
   is a finding.
V7 SECRETS. Scan the committed evidence and the raw records for key material: `BUZZ_PRIVATE_KEY`, `nsec1`, and any
   64-hex token that is not a known public key (the identities files), an event id present in the evidence, or a
   sha256 you can name. Report the census; never print a suspected secret, only its file and line.
V8 B10, THE SIGNERS. From the committed fixtures and `proofs/S0-02/fixtures/identities-s0-02.json`, show that the
   revoked event is signed by owner2 and neg-unauthorized by nonmember, and that the live evidence carries the same
   signers. On a scratch copy, feed `build_fixtures.py` a colliding key and a non-hex key: each must be refused by
   name. Does any role still fall back to a null key (D4)? Is that reachable from the eight specs?
V9 B11, `--denial`. On scratch copies of the real root: (a) damage a SIBLING leg (delete it, corrupt its receipt)
   and show `--denial <fixture>` still grades its own leg unchanged; (b) move one denial leg's contents into another
   leg's directory and show the printed reason follows the OBSERVED evidence, never the argument; (c) plant evidence
   bytes that quote `denied: event-stale` inside a failing leg and show that `scripts/proof-runner` does not read the
   leg as proven (AF-AP-158); (d) `--denial pos-allowed` and `--denial revoked` behave as the contract says.
V10 B12, THE ONE CORRUPTED EVENT. Count the `session/prompt` records in `neg-bad-signature`'s timeline (the contract
   is zero). Run the checker on `proofs/S0-02/fixtures/regression-neg-bad-signature-live-probe-prompt.jsonl` as B12's
   tests do. Show that `deliver_event.py --reuse --flip-signature` is refused before any file, key or network
   action; point that run at an address nothing listens on, or at a listener you own (the tests' pattern), never at
   the relay on :3999, so a broken refusal cannot deliver. On a scratch copy, give the revoked receipt another class's relay text: it must fail through
   `_observed_row` (A1). AF-AP-160 says a leg exempted from one gate is exempted from all: list every `continue`
   or skip in the checker's bundle loop and say which gates each one bypasses.
V11 Anything else you find. Discovery is exhaustive; disposition is disciplined.

## Boundary
READ-ONLY on the tree. Attack through SCRATCH COPIES only (`../scratch`). Never git restore, stash or checkout the
shared tree. Never `git add`, commit or push. No relay deliveries, no captures, no membership writes. Never touch
`/home/rocco/s0-01-pinned`, the relay, any unit, the model server, or another lane's tree.

## Gate mechanics (each call under Hermes's 420 s terminal cap)
- `mkdir -p ../scratch/bt`; use an absolute SHORT `--basetemp`. pytest on this host:
  `python -m pytest -n 8 -q -p no:cacheprovider --basetemp ../scratch/bt <files>` DIRECTLY (xdist is installed;
  `scripts/pc_suite.sh` is the SANDBOX's launcher and cannot run here).
- CODE INTEL FIRST: `graft skeleton` / `graft ask` before any whole-file read; the checker and the test file are
  long, so read them by range. `report_lint` gates on a FLOOR (`--min-refs 15`). Apply its `fix:` hints for at most
  THREE rounds, then paste the lint summary as plain text and finish.

## Report shape (DATA)
Per item: command, exact output, SOLID/UNSURE, blocking? (answer each clause of the predicate), the file:line.
Then: the hostile-bundle table (V2), the mutant table (V6), one verdict line per batched landing (B10, B11, B12,
the mint), DISCREPANCIES, NOT-done, GATE RECOMMENDATION.
Never a fix, never a verdict.

## PREMISE — MEASURED at authoring (2026-09-23 22:0xZ, /home/user/agent-factory@a78bdca; generated by `scripts/premise_block.sh`)
```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf
a78bdca transcripts: scrubbed sandbox chat digests (2026-09-23)
$ git log --format='%h %s' -3 origin/claude/soundbox-kit-migration-iz1jwf -- proofs/S0-02
6bd8582 S0-02 MINTED: the live eight-leg capture (clone e8db82c2, rc 0) passes the frozen checker; ledger S0-02 PRESENT (execution proofs 8/9) — VERIFY-S0-02 next
321bcee S0-02 B12 (task #196): the bad-signature leg delivers ONE corrupted event; the bundle grades revoked's relay text (A1); AF-AP-160 registered
c19736d B11 landed (task #191; GATED-PENDING-VERIFY, batched into VERIFY-S0-02): S0-02's four seed negative legs as `--denial <fixture>` checker legs, so the spec meets the F16 floor (registry 4)
$ find proofs/S0-02/evidence -type f | wc -l
55
$ (cd proofs/S0-02/evidence && find . -type f | LC_ALL=C sort | xargs sha256sum) | sha256sum | cut -c1-16
5097d3997b7bef65
$ python3 proofs/S0-02/check_buzz_authz.py proofs/S0-02/evidence
PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, 6 distinct reasons; replay refused by the relay's duplicate: receipt (buzz-acp drop line absent, defense-in-depth only); +1 revocation leg (assertion 2); removal evidence: coordinator-supplied receipt (unauthenticated; ordering and fields verified; not an end-to-end revocation proof)
$ for f in neg-unauthorized neg-bad-signature neg-replayed neg-stale; do python3 proofs/S0-02/check_buzz_authz.py --denial $f proofs/S0-02/evidence; done
failure_reason: denied: sender-not-in-allowlist
failure_reason: denied: signature-invalid
failure_reason: denied: event-replayed
failure_reason: denied: event-stale
[rc=1]
$ python3 scripts/validate-ledger integrity --root . | grep -E 'S0-02|execution_proof'
S0-02 PRESENT
execution_proof numerator=8 denominator=9
$ python3 -c "import json; r=json.load(open('proofs/S0-02/result.json')); print(r['env_fingerprint'], [(x['leg'], x['exit_code']) for x in r['runs']])"
pc-bridge:vm [('positive', 0), ('negative', 1), ('negative', 1), ('negative', 1), ('negative', 1), ('negative', 1)]
$ cat proofs/S0-02/evidence/revoked/membership.json
{"removed": true, "removed_pubkey": "82f440d16985a59efd88ffcbbf186fe27ecde5db2a39773f50c354a08e8cd2b2", "channel": "73701f66-6e12-42ff-b561-7d36db1ad91b", "at_epoch_s": 1790198186, "http_status": 200}
$ cat tasks/briefs/s0-02-support/live-capture-2026-09-23/owner-removal-cli-output.txt
{"accepted":true,"event_id":"03fd24c31cf11abf93ae96ac17ca1f17111457871fe0666093bda958590e8dc1","message":""}
rc=0 at=1790198186
$ grep -n -E 'def test_real_evidence_root_is_the_minted_live_capture|def _check_bundle_uncapped|def _check_denial_uncapped|def check_bundle|^_LEG_FILES_PLAIN = |^REPLAY_SUBLEGS = ' tests/test_s0_02_buzz_authz.py proofs/S0-02/check_buzz_authz.py
tests/test_s0_02_buzz_authz.py:1003:def test_real_evidence_root_is_the_minted_live_capture():
proofs/S0-02/check_buzz_authz.py:149:REPLAY_SUBLEGS = ("first", "second")
proofs/S0-02/check_buzz_authz.py:156:_LEG_FILES_PLAIN = frozenset({
proofs/S0-02/check_buzz_authz.py:848:def _check_bundle_uncapped(root: Path, anchors: "Anchors") -> str:
proofs/S0-02/check_buzz_authz.py:926:def check_bundle(root: Path, anchors: "Anchors | None" = None) -> str:
proofs/S0-02/check_buzz_authz.py:954:def _check_denial_uncapped(root: Path, fixture_name: str, anchors: "Anchors") -> str:
$ python3 -m pytest -q -p no:cacheprovider tests/test_s0_02_buzz_authz.py -k minted_live_capture 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*//'
1 passed, 277 deselected
$ python3 -m pytest -q -p no:cacheprovider --co tests/test_s0_02_buzz_authz.py 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*//'
278 tests collected
$ python3 proofs/S0-02/tools/build_fixtures.py --check
fixture-drift: none (8 fixtures match a fresh build)
$ for c in 8d8c97e c19736d 321bcee 6bd8582; do git merge-base --is-ancestor $c HEAD && echo "$c ancestor of HEAD"; git log -1 --format="%h %s" $c | cut -c1-110; done
8d8c97e ancestor of HEAD
8d8c97e B10 landed (task #190; GATED-PENDING-VERIFY): the S0-02 fixture signers follow D-037 and D-038 before 
c19736d ancestor of HEAD
c19736d B11 landed (task #191; GATED-PENDING-VERIFY, batched into VERIFY-S0-02): S0-02's four seed negative le
321bcee ancestor of HEAD
321bcee S0-02 B12 (task #196): the bad-signature leg delivers ONE corrupted event; the bundle grades revoked's
6bd8582 ancestor of HEAD
6bd8582 S0-02 MINTED: the live eight-leg capture (clone e8db82c2, rc 0) passes the frozen checker; ledger S0-0
```
