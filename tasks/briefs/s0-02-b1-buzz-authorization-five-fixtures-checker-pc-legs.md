# Lane B1 — S0-02 Buzz authorization/freshness: five committed fixtures with their reasons in-file, a checker over captured legs, the PC leg runner (sandbox Opus 4.6 `code-implementer`)

PIN: (HEAD at dispatch — the commit carrying this brief; the report header says "PIN: `<sha>`".)

**Why:** S0-02 has nothing built (no `proofs/S0-02/`, no fixtures, ledger ABSENT). The seed (`seeds/seed-stage0-v1.yaml:362-381`) is exact:
three assertions (an allowed fresh signed event ⇒ exactly one ACP session/turn; membership removal or key rotation revokes access
independent of NIP-OA `created_at`; duplicate delivery does not duplicate a completed turn) and FOUR negative fixtures each carrying its
own `expected_failure` block in-file (`denied: sender-not-in-allowlist`, `denied: signature-invalid`, `denied: event-replayed`,
`denied: event-stale`) with the rule "four DISTINCT reasons required; one blanket rejection fails the proof". docs/03 §1 and the findings add
a fifth class (self-authored). The component under test is the REAL pinned buzz-acp (upstream.lock.yaml `buzz` 1c8321cd) fed through the
REAL relay on the PC; the ACP turns are observed by the S0-01 tee.
**Inputs (read in this order):** `tasks/briefs/stage0-parallel-support/material-S0-02.md` (whole; §5.7 lists the S0-01 assets to reuse:
`proofs/S0-01/tools/nostr_verify.py` (sign/verify, `event_id`, `verify_event`), `proofs/S0-01/fixtures/identities.json`,
`proofs/S0-01/fixtures/relay-events-2026-09-05.json` (real signed kind-9 events — the fixture FORMAT), the eight PC relay scripts under
`proofs/S0-01/tools/pc/`) · the pinned buzz-acp source at `/home/user/nerdherderdani/buzz/crates/buzz-acp/src/` (commit 1c8321c, READ-ONLY):
`relay.rs` (`seen_ids: TwoGenDedup` and the drop at :1262 — replay; `last_seen`/`created_at` :1267-1301; membership via NIP-29 group
members :826-870, `membership_dropped_since`; `replay_since`/`startup_watermark` — freshness), `filter.rs`, `scope.rs`, `queue.rs`, `lib.rs`
(find where a signature is verified — buzz_core/nostr — and where a sender's membership is decided; cite file:line) · the S0-01 capture
shape (`proofs/S0-01/evidence/`, `check_acp_conformance.py`'s per-leg reads, the tee's `timeline.jsonl`, the masked `buzzacp.log`) ·
`proofs/S0-07/spec.json` + `proofs/schemas/spec.schema.json` (the spec shape) · `docs/03_INTEGRATION_CONTRACTS.md:5-29`,
`docs/02_COMPONENT_AUDIT.md:36-43` (NIP-OA `created_at` is NOT revocation).
**Scope (all NEW + one test + your report):** `proofs/S0-02/spec.json` · `proofs/S0-02/fixtures/{pos-allowed,neg-unauthorized,neg-bad-signature,
neg-replayed,neg-stale,neg-self-authored}.json` · `proofs/S0-02/check_buzz_authz.py` · `proofs/S0-02/oracle/denial_table.py` ·
`proofs/S0-02/tools/pc/run_s0_02_legs.sh` + `deliver_event.py` (PC-side) · `proofs/S0-02/fixtures/evidence/` (a synthetic PASSING bundle and
a BLANKET-REJECTION bundle for the negative control) · `tests/test_s0_02_buzz_authz.py` · report `tasks/briefs/s0-02-support/B1-report.md`.
Nothing under `proofs/S0-01/` is edited (import its `nostr_verify` by path; reuse, never copy). Shared-tree rules as every lane: never `git
stash/checkout/restore/reset/add/commit/push`; gates from a `git archive <PIN>` copy under
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/b1/ + your files; explicit `--basetemp`; kill only your own
processes by pid; NEVER background a run and stop; no outward actions; NO PC bridge; never read or print credentials (identities.json's
keys are test identities — cite them by pubkey, never print a private key into the report). Interpreter `/root/venv-agent-factory/bin/python`.

## Design (pinned — build it, do not redesign it)
1. **Fixtures = signed Nostr events with the reason IN-FILE.** Each fixture is `{"event": <signed kind-9 event in the relay-events format>,
   "expected": {"turns": 1|0, "failure_reason": "denied: …"|null, "mechanism": "<file:line in buzz-acp that decides it>"}}`. Build them with
   `nostr_verify.py`'s signer from `identities.json`: `pos-allowed` (a member's fresh event — `user2` if the S0-01 relay fixtures show it as a
   member; else the owner); `neg-unauthorized` (a freshly generated key NOT in the group — generate the key in the fixture builder, commit
   only the pubkey + the signed event); `neg-bad-signature` (the pos event with one signature byte flipped — `verify_event` must reject it in
   the builder's self-test); `neg-replayed` (the pos event's exact id delivered a second time — the fixture is the SAME event with
   `expected.turns: 0` and a `replay_of` pointer); `neg-stale` (a member's event with `created_at` older than buzz-acp's freshness window —
   derive the window from the source: `startup_watermark` / `replay_since` — cite it; if the source has NO stale rule, the fixture's
   `expected.failure_reason` is `denied: event-stale` with `mechanism: NOT FOUND in buzz-acp <commit> — DISCREPANCY` and the report says so);
   `neg-self-authored` (the agent's own pubkey as sender). A `build_fixtures.py` regenerates them deterministically (fixed timestamps, fixed
   nonces) and a test asserts the committed fixtures == a fresh build (no drift) and that every negative fixture's event is REJECTED by the
   named mechanism's precondition where checkable offline (`verify_event` False for the bad signature; the sender absent from the members
   set for unauthorized; the id equal to pos for replayed; `created_at` below the window for stale; sender == agent pubkey for self-authored).
2. **The oracle table `oracle/denial_table.py`** maps each `failure_reason` to the OBSERVABLE buzz-acp produces at `RUST_LOG=debug` (the exact
   log line pattern, cited file:line in the pinned source where the line is emitted) OR, where buzz-acp drops SILENTLY (the `seen_ids`
   dedup at relay.rs:1262 emits nothing — check), to `silent-drop` with the alternative evidence the checker must find (the relay's delivery
   receipt for the event id + NO ACP turn in the tee timeline within the leg). Every row is pinned by a test that reads the source
   checkout (`S0_02_BUZZ_SRC`, sandbox default `/home/user/nerdherderdani/buzz`; CI unset ⇒ a DECLARED skip; set-but-absent ⇒ FAIL — the
   S0-01 corpus rule) and asserts the cited line contains the cited pattern. A reason with no distinguishing observable is a DISCREPANCY
   for the owner (the seed's "four DISTINCT reasons" may be unmeetable from logs alone) — say it, do not paper over it.
3. **The checker `check_buzz_authz.py <evidence-root>`** — per leg dir (`evidence/<fixture-name>/`: `timeline.jsonl` from the tee,
   `buzzacp.log` masked, `delivery.json` from the relay POST, `fixture.json` = the fixture used) asserts: the delivered event id == the
   fixture's; positive leg: EXACTLY one ACP session/turn in the timeline (the S0-01 `prompt`/`session/new` frame shapes — reuse the S0-01
   timeline parsing by import, never copy) and the turn's text carries the fixture's nonce; negative legs: ZERO turns AND the oracle's
   observable present (or the silent-drop evidence); the `replayed` leg: the SECOND delivery of the same id produced no second turn while
   the FIRST did (two sub-legs in one dir); `stale`/`unauthorized`/`bad-signature`/`self-authored` each with their DISTINCT observable — the
   checker FAILS with `blanket-rejection: reasons {…} not distinct` when two negative legs share the same observable (the seed's rule as a
   gate). Absent root ⇒ `deferred: S0-02 evidence not captured` exit 2. Reads under the S_ISREG rule. PASS line `PASS: S0-02 buzz-authz -
   1 positive, 5 negative legs, 5 distinct reasons`.
4. **Membership revocation (assertion 2)** — a sixth leg `revoked`: the pos sender removed from the group (the relay's NIP-29 member removal —
   the PC runner does it via the relay REST with the owner identity, then re-delivers a FRESH event with a NEW `created_at`) ⇒ zero turns,
   observable = the membership drop (relay.rs `membership_dropped_since`) — proving revocation is independent of `created_at`. Key rotation
   is the same leg with a new agent key if the relay supports it; else `NOT run: key rotation not exposed by the pinned relay` (say so).
5. **The PC runner `tools/pc/run_s0_02_legs.sh` + `deliver_event.py`** (NOT run here): for each fixture, a fresh S0-01-style leg (reuse
   `pc_launch.py`/the tee/`pc_post.sh` by invocation, not by copy) with `RUST_LOG=debug` for buzz-acp, deliver the fixture's event through
   the relay REST (`deliver_event.py` posts the SIGNED event verbatim with NIP-98 auth from the owner identity — mirror `pc_mention.sh`'s
   route), record `delivery.json` (the relay's response), wait the S0-01 turn window, collect the leg into `evidence/<name>/`; the replayed
   leg delivers twice; the revoked leg removes membership first. `bash -n` clean; every external call listed in the report.
6. **`spec.json`**: positive `check_buzz_authz.py proofs/S0-02/evidence` expect 0; negative `check_buzz_authz.py proofs/S0-02/fixtures/evidence-blanket`
   expect 1 + `failure_reason: blanket-rejection: …` exact (the committed blanket bundle: five negative legs whose observables are identical);
   `required_negative_controls: 4` is satisfied by five. The evidence root does not exist yet: `deferred:` exit 2 shown in the report.
7. **Tests**: the fixture builder determinism + the offline preconditions (item 1); the oracle table vs the source (item 2); the checker over a
   synthetic PASSING bundle (built by the test from the fixtures + S0-01-shaped timelines) and the blanket bundle; every negative leg's
   observable removed one at a time ⇒ the named failure; the second-turn mutant on the replayed leg; a positive leg with two turns ⇒ FAIL;
   the FIFO read; the `deferred:` exit; the S0-01 timeline parser reused (assert it is imported, not duplicated). Preflight the 18 classes.
8. **Report discipline** as every lane: report_lint MISS 0, ap_screen classified, file:line by grep on the FINAL bytes, counts pasted twice
   (`bash scripts/test_summary.sh tests/test_s0_02_buzz_authz.py`), pyflakes + `bash -n`, the process census.

## Mutants (≥ 12): BLANKET-ACCEPTED · TWO-TURNS-ACCEPTED · REPLAY-SECOND-TURN-ACCEPTED · WRONG-EVENT-ID-ACCEPTED · OBSERVABLE-MISSING-ACCEPTED ·
FIXTURE-DRIFT · SIGNATURE-FLIP-UNDETECTED · STALE-WINDOW-UNPINNED · ORACLE-LINE-DRIFT · FIFO-HANG · DEFERRED-AS-PASS · MEMBERSHIP-BY-CREATED_AT.

## Report shape
FILE IDENTITY · DONE (assertion → fixture → observable (file:line) → checker rule → test) · the mutant table · NOT_DONE (the PC legs, the
relay membership operations — the coordinator's; any reason with no observable) · DISCREPANCIES (the 4-vs-5 count; silent drops; a stale
rule absent from the source; NIP-OA facts) · SELF-ATTACK.
