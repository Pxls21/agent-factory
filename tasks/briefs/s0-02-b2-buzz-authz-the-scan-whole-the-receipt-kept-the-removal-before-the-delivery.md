# Lane B2 — S0-02 round 2: the verify-site scan over WHOLE files, the membership receipt kept and bound to the relay's response, the removal proven BEFORE the delivery, the replay window inside the tolerance, the canary level-aware and demanded only where it can exist, the bundles in the producer's shape, a member the relay accepts and buzz-acp drops (build lane: PC Hermes `code-implementer` when the slot is free, else sandbox Opus 4.6 `code-implementer`)

PIN: (HEAD at dispatch — the commit carrying this brief; the report header says "PIN: `<sha>`".) Lane B1's landing is `088efef`
(pushed); its 128 files are unchanged at HEAD; the coordinator's `.gitignore` re-include for `proofs/*/evidence/**/*.log`
(VERIFY-B1 F4) lands in the same commit as this brief — verify it with `git check-ignore -v proofs/S0-02/evidence/pos-allowed/buzzacp.log`
(must NOT be ignored) and the coordinator's test `tests/test_lane_gate.py::test_committed_evidence_and_fixture_logs_are_not_gitignored`.

**Why:** VERIFY-B1 (report `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/wf-results-r5/VERIFY-B1.md`
— READ IT WHOLE FIRST; it is the contract for this round) graded lane B1 NOT-READY with five blockers, all reproduced (F2/F5 by
source read of PC-only files): **F1** `_production_verify_sites` cuts each `.rs` at its FIRST `#[cfg(test)]`, which sits at line 397 of
11013 in `lib.rs` (3.6 %) and 736 of 6786 in `relay.rs` (10.8 %) — the whole channel-event path is beyond the cut; a `verify_event`
planted right after the channel EVENT deserialise (`relay.rs:3779`) SURVIVES green; three of the five `known` sites are decorative;
the alias form `use … as v` is missed, a `mod tests` before the marker and a block comment are FALSELY flagged; the report's stated
limit is backwards — the D1/D2 claim is TRUE (the verifier scanned whole files), the GATE is hollow; **F2** `run_s0_02_legs.sh:135`
`rm -rf "$out"` wipes `$DEST/revoked/` one line before `:170` tests for `$out/membership.json` — the operator's receipt is deleted and
the revoked leg can never run; **F3** the revoked block reads only `removed_pubkey` and `removed` — `at_epoch_s` and `channel` are never
read, so a removal recorded AFTER the rejected delivery, a wrong channel, a hand-written receipt that never touched the relay all
PASS; D5's "structural separation" is an unauthenticated operator-typed file; **F4** (the coordinator's, landed); **F5** the replay
leg's second sub-leg reuses the first delivery's `created_at` but records a fresh `t0`, with `wait_turn_window` (up to 100 s) in
between and `LEG_CLOCK_TOLERANCE_S = 120` — a 20 s margin; and a same-second pair is refused by the relay's NIP-98 replay guard
(`crates/buzz-auth/src/nip98_replay.rs`) because the auth event is byte-identical. Non-blocking, same increment: F6/F7 report
corrections, F8 the drift-window substring anchor (`= 900` in `= 9000`), **F9** the DEBUG canary is level-blind (INFO passes) and
**F9b** it is demanded for ALL negative legs — the real S0-01 corpus log has 0 canary lines, so the RUST_LOG seam blocks 6 of 7
legs, not 2; F10 channel confusion undetected; F11 no root closure (extra/garbage leg dirs ignored); F12 the stale branch one-sided
(a t0 in 2286 passes) + off-by-one at 900 + a dead arm; F13 one unguarded read at `:351` + no wall-clock cap (`_check_with_timeout`
exists in S0-01); **F14** the bundles model the S0-01 MENTION receipt (`mention_pubkeys`, no `http_status`), not what
`deliver_event.py` writes, and every relay-decided leg is really HTTP 400 `{"error": msg}` (`bridge.rs:985`) so `event_id` equality
is a tautology there; F15 three oracle prose refs wrong; F17 `created_at` reaches the inbound filter-rule engine (`filter.rs:330`)
so D8's absolute claim is too strong; F18 the freshness gate proves "no constant", the oracle claims "no rule"; F19/F21/F22/F23.
Held: the distinctness gate (the tautology and the reorder both die), the identity binding (11 forgeries caught), the replay leg
(a relay-side dedup correctly rejected), the freshness type-guard incl. NaN, no hang under seven FIFO plants, the signer's fixed aux,
the PC gate 92.

**Inputs (read in this order):** VERIFY-B1 whole · the B1 brief + `tasks/briefs/s0-02-support/B1-report.md` · the pinned buzz
source `/home/user/nerdherderdani/buzz` (1c8321cd, READ-ONLY): `crates/buzz-acp/src/{lib.rs,relay.rs,pool.rs,filter.rs,engram_fetch.rs}`
(the `#[cfg(test)]` positions; `relay.rs:3775-3780`; `filter.rs:37,48,259,330` + `lib.rs:594-606`), `crates/buzz-relay/src/api/bridge.rs:964-985`
+ `api/mod.rs:22` (the 200 and 400 shapes), `crates/buzz-relay/src/handlers/ingest.rs:2224-2245`, `crates/buzz-auth/src/nip98.rs:19-83`
+ `nip98_replay.rs` · S0-01's `_check_with_timeout` (`proofs/S0-01/check_acp_conformance.py`, above `check_bundle`) · the real
corpus `/root/s0-01-realleg/golden/run-1/{buzzacp.log,mentions/owner.receipt.json,timeline.jsonl}` · `docs/INCIDENT-LOG.md`
(AF-AP-40, AF-AP-42, AF-AP-58, AF-AP-62, AF-AP-63, AF-AP-65) · the pack `scripts/lane_context.sh -q 'what does the checker read from
each leg and what does the runner write' -s _observe_all _check_freshness _check_delivery check_bundle -o pack.md
proofs/S0-02/check_buzz_authz.py` (run it first; attach it).
**Scope (under S0-02 + its test + your report):** `proofs/S0-02/check_buzz_authz.py` · `proofs/S0-02/oracle/denial_table.py` ·
`proofs/S0-02/tools/build_fixtures.py` · `proofs/S0-02/tools/pc/{run_s0_02_legs.sh, deliver_event.py}` · `proofs/S0-02/fixtures/**`
(regenerated — every bundle in the producer's shape) · `proofs/S0-02/spec.json` (only if a negative changes) · `tests/test_s0_02_buzz_authz.py`
· report `tasks/briefs/s0-02-support/B2-report.md`. NOT yours: `proofs/S0-01/*` (read-only; the RUST_LOG seam is lane A5l/P5c's),
`.gitignore` (landed), `scripts/validate-ledger` (F16 is a coordinator task), `proofs/registry.yaml`, the seed. Shared-tree rules:
never `git stash/checkout/restore/reset/add/commit/push`; every gate from a `git archive <PIN> | tar -x` copy under
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/b2/ with your files copied in (`scripts/lane_gate.sh -r <PIN>
-f "<your files>" -t "tests/test_s0_02_buzz_authz.py tests/test_spec_probe_schemas.py tests/test_validate_ledger.py
tests/test_proof_runner.py" -n 2`, ONE foreground call, `LANE_GATE_DIR` under your scratch dir); explicit `--basetemp`; kill only your
own processes by pid (never pkill/pgrep -f); NEVER background a run and stop; no outward actions; NO PC bridge; NO network call to
any relay; the runner and `deliver_event.py` are `bash -n`/pyflakes-checked and READ, never run; never read, print or commit a
private key (the SPECIMEN key is a labelled test key derived from a committed seed). Interpreter `/root/venv-agent-factory/bin/python`;
`S0_01_VENUE=sandbox S0_01_REAL_LEG_DIR=/root/s0-01-realleg/golden` (the buzz checkout default applies).

## Design (pinned — build it, do not redesign it; line numbers are `088efef`'s)
1. **F1 — the scan is over WHOLE files, test regions excluded STRUCTURALLY, `known` exact.** Drop the prefix cut. Exclude a test
   region by tracking brace depth from each `#[cfg(test)]` attribute to the end of the item it decorates (a `mod tests { … }` or a
   single `fn`); drop `//` comments AND `/* … */` blocks; match `verify_event(`, `.verify()` and a `use … verify_event as <alias>`
   followed by `<alias>(`. `KNOWN` = the exact six whole-file sites the verifier enumerated (`engram_fetch.rs:122, lib.rs:256,
   lib.rs:1574, lib.rs:6082, pool.rs:3385, pool.rs:3495`) asserted by EQUALITY (added and gone both named); the channel-path claim
   asserted separately: no verify site inside the channel-event region (`relay.rs` from the EVENT deserialise at `:3775` to the end of
   that handler — derive the range by brace depth, cite it). Red tests on a scratch copy of the crate pointed at by `S0_02_BUZZ_SRC`:
   the verifier's channel-path plant after `relay.rs:3779` → the test goes RED; the alias plant → RED; a `mod tests` before the
   marker and a block-comment verify → stay GREEN (no false red). Fix the report's backwards limit statement.
2. **F2 — the receipt survives the wipe.** The membership receipt is read from OUTSIDE `$out` (`S0_02_MEMBERSHIP`, default
   `$DEST/revoked-membership.json`), the `revoked` arm refuses with the documented shape when it is absent, and copies it into `$out`
   AFTER `rm -rf "$out"`; the documented shape gains `http_status` (the relay's actual removal response — F3). The static ordering test
   (the `cp` after the `rm`) RED on `088efef`.
3. **F3 — the removal is bound and ordered.** `at_epoch_s` an int (not bool) and `< t0`; `channel` ∈ the delivered event's `h` tags;
   `http_status` 2xx; the coordinator records the relay's response into the receipt. Three red tests (after-delivery, wrong channel,
   no status) RED on `088efef`.
4. **F5 — the replay pair fits its window.** `sleep 1` before the second `deliver`; the second sub-leg's `t0.json` carries the FIRST
   sub-leg's `t0` (the clock the reused event was signed against) — or the checker measures the second sub-leg's age against the first's
   `t0`; the constant-relation test `LEG_CLOCK_TOLERANCE_S > TURN_WAIT_S + 30` (RED today: 120 vs 130) — resolve by widening the
   tolerance for the replay's second sub-leg ONLY (its freshness is the first's by construction) rather than loosening every leg; the
   NIP-98 same-second guard named in the runner's comment.
5. **F9/F9b — the canary is level-aware and demanded only where it can exist.** A `DEBUG` level token on the canary's line; the
   canary required only for legs whose oracle row's `evidence == EV_BUZZACP_LOG` (replayed, self-authored); relay-decided legs need no
   buzz-acp log evidence. The runner's preflight tripwire (`tests:879-885`) tightened to the `PINNED_ENV_KEYS` block, not the file text.
   Red: the INFO-level canary plant → RED; the real corpus log (0 canaries) as `neg-unauthorized`'s log → still PASS (state why).
6. **F14 — the bundles in the producer's shape, `http_status` graded.** `build_fixtures.py` imports `deliver_event._normalise` and
   builds every `delivery.json` through it (the fixture and the producer cannot drift); `_normalise` records `event_id_echoed: bool`;
   `_check_delivery` requires `http_status == 200` for accepted legs and `400` for relay-decided ones and treats an un-echoed id as a
   named failure on accepted legs; the committed bundles regenerated byte-deterministically. Red: a bundle whose `delivery.json` carries
   `mention_pubkeys`/no `http_status` → RED; the shape test asserting the exact key set.
7. **F10/F11/F12/F13/F8/F15/F18/F19/F21/F22:** wrong-channel observables rejected (`owner["evidence"]`); root closure (exactly the named
   legs; an unknown or garbage leg dir → `bundle: unexpected leg directories`); the stale branch mirrored (the tolerance arm, `<=` at
   the boundary per `ingest.rs:2227`'s strict `>`, the dead 900 arm deleted or reached by a positive-offset fixture and the test
   asserting the distinguishing half of the message); `:351` through `_require_file` + `membership.json` as the seventh FIFO id +
   `_check_with_timeout(90, …)` adopted from S0-01; the drift window parsed as an integer (`= 9000` → RED); the three oracle prose refs
   corrected + a test that lints every `\w+\.rs:\d+` inside `discrepancy`/`note` prose; a second freshness assertion that no line in
   the channel-event region compares `created_at` to a wall clock (the verifier's M-B plant → RED); the nonce on a JSON string
   boundary; positive selection of identity keys; a named failure when `S0_02_BUZZ_SRC` is not a git checkout.
8. **F17 — D8 stated exactly.** `FilterContext.timestamp = event.created_at` (`filter.rs:48`, bound at `:330`, called on the inbound
   path via `lib.rs:594-606`): a configured subscription rule CAN gate on the sender's `created_at`; add the oracle row and a test that
   the shipped `respond_to`/rule config carries no `timestamp` reference; reword D8 to "no default rule does; the capability is
   config-reachable".
9. **The `neg-not-allowlisted` leg (the verifier's item 17 recommendation, the oracle's own unbuilt fixture at `denial_table.py:80-83`).**
   A channel MEMBER (`user2` from `identities.json`) the relay accepts and buzz-acp's author gate drops (`lib.rs:389`, the DEBUG line
   at `lib.rs:550`): fixture, oracle row (evidence = the buzz-acp log), runner arm (role `user2` — `.secrets/user2.env` on the PC,
   state it), checker leg — a genuine buzz-acp decision for the allowlist reason and a sixth distinct observable; the PASS line and
   `LEG_NAMES` grow by one; the seed's wording for signature/freshness (the relay decides at publish) stays a DISCREPANCY for the
   owner, never amended by you.
10. **Mutants:** the verifier's 12 survivors must DIE (the channel-path verify plant, the inline freshness rule, the alias, two
    observables on one leg, a relay text in the buzz-acp log and vice versa, a sixth/garbage leg dir, the far-future t0, `age == 900`,
    the after-delivery removal + the four receipt mutations, the nonce substring, the INFO canary) with the killer line pasted; the
    44 killed re-run; the three false reds gone.
11. **18-class self-sweep as an ENUMERATION** (counts + method; class 2's "every read guarded" true this time; class 5's anchors
    re-graded).
12. **Report discipline:** FILE IDENTITY of the FINAL bytes; every `file:line` from `grep -n` on the FINAL bytes and
    `python3 scripts/report_lint.py <report> --map C=proofs/S0-02/check_buzz_authz.py --map T=tests/test_s0_02_buzz_authz.py --map
    O=proofs/S0-02/oracle/denial_table.py --map B=proofs/S0-02/tools/build_fixtures.py` + a `--map` per buzz file, pasted with MISS 0
    (fix F6's wrong ref: `pc_launch.py:167`, not `:268` — at 088efef); the external-command census (F23); the two `lane_gate.sh`
    RESULT lines; `ap_screen.py` prod + `--tests` classified by run; NOT-done first-class (the PC legs — VERIFY-B1's three
    prerequisites: the RUST_LOG seam A5l/P5c, the relay membership write, the role keys; F16 is the coordinator's validate-ledger task).
