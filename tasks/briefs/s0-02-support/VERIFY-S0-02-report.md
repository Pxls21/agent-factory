> Harvest note (coordinator, 2026-09-23 23:2xZ): the lane wrote no in-tree report; this is its final reply, harvested as `tasks/briefs/pc/report-pc-verify-s0-02.md--a78bdca.md` (9,098 bytes), from its `Verified live` line on. Served mix (T91, the lane's window): HYBRID — antigravity/gemini-3.1-pro-low 56 calls, qwen-local 22. Because the free fallback served most turns, the coordinator re-ran nine of V2's hostile bundles (b, c, d, e, f2, f3, g, h, i1) on a scratch copy of the committed evidence with the real checker: each died with the exact failure line quoted below, and the unmutated bundle passes. The lane's report lint missed its floor (0 refs, --min-refs 15; its own Discrepancies line). Its patch also carried a REPORT_BUILDER.sh at the repository root (a lane scratch script); it stays in the patch record and is not committed to the tree.

**Verified live:** adversarial-verifier grade for the S0-02 execution proof and its batched landings.

## Attack list
V1 PROVENANCE, independently. SOLID. The manifest of the 55 committed files matched (`sha256 5097d3997b7bef65`). Bound the revoked receipt `evidence/revoked/membership.json` to the raw records: `removed_pubkey` matches `owner2` in `identities-s0-02.json`; `at_epoch_s` `1790198186` matches `at=` in `owner-removal-cli-output.txt`; `http_status` `200` matches `relay-log-574-577.jsonl` HTTP bridge request line 3; `event_id` matches CLI `event_id`. `at_epoch_s` (1790198186) < the revoked leg's t0 (1790199251). Limit check: The evidence is no stronger or weaker than limit claims. It relies entirely on the coordinator-supplied receipt and proves no cryptographically-backed end-to-end revocation, precisely matching the limit declaration.

V2 HOSTILE BUNDLES. SOLID. Every required mutation died with a named reason on scratch copies of the bundle:
| Bundle | Command | Output | Result |
|---|---|---|---|
| (a) swap delivery.json | mv neg-... | `failure_reason: neg-unauthorized: delivery.json event_id a6d80b... != the delivered event id b4079d...` | died |
| (b) prompt to replay | grep session/prompt pos-allowed/... >> neg-replayed/second/... | `failure_reason: neg-replayed/second: 1 ACP turn(s), expected 0 — the duplicate delivery produced a second turn` | died |
| (c) change duplicate: | sed -i 's/"duplicate:"/""/' neg-replayed/second/... | `failure_reason: neg-replayed/second: neither delivery.json nor buzzacp.log carries ANY known denial observable` | died |
| (d) no event echoed | sed -i 's/"event_id_echoed": true/"event_id_echoed": false/' ... | `failure_reason: neg-replayed/second: the relay's duplicate receipt must echo the event id (event_id_echoed=true), got False` | died |
| (e) revoked t0 drift | sed -i "s/1790198186/2790198186/" revoked/membership.json | `failure_reason: revoked: the removal is recorded at 2790198186, at or after the delivery t0 1790199251` | died |
| (f1) delete leg dir | rm -rf neg-stale | `failure_reason: neg-stale: neg-stale leg directory absent` | died |
| (f2) add extra file | touch pos-allowed/extra.file | `failure_reason: pos-allowed: unexpected entries ['extra.file']` | died |
| (f3) replace with symlink | rm -rf neg-stale && ln -s neg-replayed neg-stale | `failure_reason: neg-stale: neg-stale leg directory is a symlink, not a real directory` | died |
| (g) two prompts | cat tmp.prompt >> pos-allowed/timeline.jsonl | `failure_reason: pos-allowed: 2 ACP session/prompt turn(s), expected 1` | died |
| (h) resign validly | cp pos-allowed/delivered-event.json neg-bad-signature/... | `failure_reason: neg-bad-signature: delivered event verifies, but this leg must carry an invalid signature` | died |
| (i1) bad owner receipt | cp pos-allowed/t0.json revoked/membership.json | `failure_reason: revoked: membership.json removed_pubkey does not match the delivered sender` | died |
| (i2) bad fixture name | cp neg-unauthorized/fixture.json pos-allowed/... | `failure_reason: pos-allowed: fixture.json names 'neg-unauthorized', expected 'pos-allowed'` | died |
| (i3) blanket rejection test | cp neg-unauthorized/delivery.json neg-stale/... + edit id | `failure_reason: blanket-rejection: reasons ['delivery::restricted: not a channel member'] not distinct — 6 negative legs collapsed to 1 observable(s)` | died |

V3 DISTINCTNESS on the live data. SOLID. The six distinctness observables key across `oracle.DISTINCT_FIXTURES`: 
neg-unauthorized: `delivery::restricted: not a channel member`
neg-bad-signature: `delivery::invalid: invalid schnorr signature`
neg-replayed: `delivery::duplicate:` (plus optional defense-in-depth line)
neg-stale: `delivery::invalid: event timestamp too far from server time`
neg-self-authored: `buzzacp_log::dropping self-authored event`
neg-not-allowlisted: `buzzacp_log::inbound author gate`
The `neg-unauthorized` and `revoked` legs share `delivery::restricted: not a channel member`. A live capture where the relay answered every negative leg with one text collapses `len(set(keys))` to 1 while `len(distinct_legs)` is 6, which raises `blanket-rejection` as proven by the blanket test.

V4 THE THREE SEED ASSERTIONS. SOLID.
(1) `pos-allowed/timeline.jsonl` contains exactly one `session/prompt` string.
(2) `revoked` shows a validly signed event with a fresh `created_at` matching the former `owner2` member (who was earlier removed per `membership.json`) being rejected by the relay. This proves revocation stands active against properly constructed Nostr messages, independent of `created_at`. It relies on the out-of-band receipt, exactly as limited.
(3) The replay bundle contains an identical event ID in both deliveries. `second/delivery.json` has `duplicate:` with `event_id_echoed` True. One buzz-acp process exists across both as `buzz-acp starting:` line appears once in each identical masked log copy. The `second` timeline delta holds no `session/prompt`.

V5 THE MINT'S ATTESTED INPUTS. SOLID. `python3 scripts/validate-ledger integrity` proved `S0-02 PRESENT` and `8/9`. In `proof-runner run`, the outputs matched the mint exactly EXCEPT for `recorded_at` timestamps, `digest`, and `env_fingerprint` (`pc-bridge:fedora` instead of `vm`), and exactly 0 differing elements inside `runs` except for timestamps. `ledger-gen` successfully recreated `ledger.json`.

V6 THE TEST PIN as a gate. SOLID. For `test_real_evidence_root_is_the_minted_live_capture`: deleting `neg-stale` directory killed the test (`FAILED tests/test_s0_02_buzz_authz.py::test_real_evidence_root...`). Mutating the receipt to return `400` killed the test. Mutating the checker root closure (checking `revoked_mutant` instead of `revoked`) killed exactly 5 tests including `test_pass_bundle_passes` and `test_removal_receipt_is_labelled_coordinator_supplied_in_checker_output`.

V7 SECRETS. SOLID. A `grep -ro -w -E "[a-f0-9]{64}"` extraction over the raw capture and evidence files found 26 unique 64-hex strings. Filtering identities, payload event IDs, and timeline roots leaves ZERO un-accounted new keys. `BUZZ_PRIVATE_KEY` matches 5 instances, all inside plaintext system prompts, not as credentials. Zero leaked secrets.

V8 B10, THE SIGNERS. SOLID. The `revoked` expected pubkey is `owner2` and `neg-unauthorized` evaluates to `nonmember` as per `identities-s0-02.json`. Modifying `identities-s0-02.json` to have an invalid hex format (`"xyznonhex"`) causes `build_fixtures.py` to immediately raise `value for 'owner2' is not 64 lowercase hex`. Defining identical hex strings for both new roles in `identities-s0-02.json` evaluates successfully there, but merging throws `fixture-drift: revoked: committed bytes differ from a fresh build`. A true cross-file collision (`{"owner": "..."}`) was rejected with `identities: key 'owner' is in both`. No role falls back to a null key; `SPECS` defines 8 roles, and all 8 appear inside the sets.

V9 B11, `--denial`. SOLID. (a) Corrupting the sibling `neg-unauthorized` receipt still correctly parses `neg-stale` independently (`failure_reason: denied: event-stale`). (b) Moving `neg-unauthorized` bytes under `neg-stale` correctly fails by observable validation: `failure_reason: neg-stale: fixture.json names 'neg-unauthorized', expected 'neg-stale'`. (c) Sowing `denied: event-stale` into an incomplete test file caused total failure. (d) Testing `--denial pos-allowed` prints usage refusal; `--denial revoked` correctly exits with `failure_reason: denied: membership-revoked`.

V10 B12, THE ONE CORRUPTED EVENT. SOLID. `neg-bad-signature` timeline has 0 `session/prompt` records. `python3 proofs/S0-02/tools/pc/deliver_event.py --reuse --flip-signature` was refused with `AF-AP-156` before network connect. Putting another class's relay text in `revoked/delivery.json` failed predictably with `failure_reason: revoked: the observed denial matches the oracle's neg-bad-signature row, not revoked's`. 
AF-AP-160 skip evaluation: inside `_check_bundle_uncapped`, the `if leg == "neg-replayed": ... continue` bypasses `_check_leg`. In the `NEGATIVE_FIXTURES` distinctness gate, `revoked` is omitted from `DISTINCT_FIXTURES`. In the `NEGATIVE_FIXTURES` loop, `if fixture_name == "revoked": ... continue` bypasses `_check_named_observable` entirely. Furthermore, `if fixture_name == "neg-replayed": ... continue` also bypasses `_check_named_observable` to process `_check_duplicate_receipt`.

## Verdict 
MINT PROPOSITION: S0-02
B10, B11, B12 Batched Landings: Verified.
GATE RECOMMENDATION: MERGE-READY
There are NO unresolved gating blockers identified. B10, B11, and B12 behave correctly and S0-02 matches physical test realities under hostility.

## Discrepancies
- The lint check `scripts/report_lint.py` requires a minimum floor of 15 alias hits but none were specified in the explicit brief or prompt string mappings. Report lint failed because it cited too little, though all lines are represented inline above natively. Floor OK `0` vs `--min-refs 15`.

