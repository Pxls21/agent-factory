# evidence-pass / evidence-blanket — SYNTHETIC bundle provenance

Both committed bundles are SYNTHETIC evidence: every leg is built by
`proofs/S0-02/tools/build_fixtures.py` from the committed fixtures and the
deterministic bundle constants. No live relay, no live buzz-acp, and no real
membership write were involved; the delivery receipts are built through the
REAL producer normaliser (`tools/pc/deliver_event.py:_normalise`).

What the bundles prove: the checker's gate logic (closure/containment,
distinctness, receipt shape, freshness, replay, removal-field ordering) over
deterministic inputs, so a mutation of the checker can be graded by a red run
before any live capture. What they do NOT prove: an end-to-end live run of the
Buzz relay + buzz-acp path — that is the production evidence root
(`proofs/S0-02/evidence`, the coordinator's live legs).

The replay leg (`legs/neg-replayed/`, rebuilt by B9-R1 on 2026-09-23 to D-036's
shape) models relay-level dedup with ONE continuous buzz-acp process. The first
sub-leg carries the whole first turn (seven records, one `session/prompt`). The
second sub-leg's receipt is the pinned relay's answer to an event id it already
stored, `{"accepted": true, "message": "duplicate:"}` with HTTP 200 and the first
delivery's id echoed (`crates/buzz-relay/src/handlers/ingest.rs:3192-3197`),
built through `_normalise`. Its timeline DELTA is empty: zero prompts and no
restart. Both sub-legs carry the same one-process masked log, with one
`buzz-acp starting:` line. buzz-acp's own drop line (`relay.rs:2387`) is absent,
because the relay never dispatched the duplicate; the checker records that line
when present and never requires it. In the blanket bundle the replay leg has the
same one-process shape, but its second receipt shows the shared relay text, so
all six negative legs collapse to one observable. This shape is inferred from the
pinned relay source; no live capture has shown it yet.

Revoked-leg removal evidence is a coordinator-supplied receipt
(unauthenticated; ordering and fields verified; not an end-to-end revocation proof).
The pinned relay exposes no membership READ route
(`crates/buzz-relay/src/api/mod.rs` — `check_relay_membership` /
`enforce_relay_membership` are internal enforcement only), so no independent
post-removal observation exists to capture.
## Host-local fixture identities (2026-09-22, D-037 / D-038)

The PC runner signs each delivered leg with the role key named by the fixture's
`signer.role`, read from `/home/rocco/s0-01-pinned/.secrets/<role>.env`
(`BUZZ_PRIVATE_KEY=<64 hex>`, mode 0600); `<role>.pub` holds the x-only public
key. The secrets are never committed or printed; only the public halves are
recorded here.

- `owner` `2267fe91571e5c9166ddf1a80176e988bdd00b9023edcc33375e1be85928000c`,
  `agent` `ff4d48deaa326bcae60687e64cca48dd7f70099933fbda0ae40d2561485f4ce1`,
  `user2` `fec645734c4bdd1a6867ab061b0a7aca7f8128d98ace364707814043b090ea22`
  (generated 2026-09-04/05; `user2` is a channel MEMBER that buzz-acp does not
  allowlist — the `neg-not-allowlisted` leg).
- `owner2` `82f440d16985a59efd88ffcbbf186fe27ecde5db2a39773f50c354a08e8cd2b2`
  (generated 2026-09-22T11:12Z): the SECOND fixture owner D-037 requires, so the
  `revoked` leg removes a non-last owner. Added to channel
  `73701f66-6e12-42ff-b561-7d36db1ad91b` on the isolated harness relay
  (`127.0.0.1:3999`) by the fixture owner with the pinned CLI
  (`buzz channels add-member --channel <id> --pubkey <owner2> --role owner`):
  receipt `{"accepted":true,"event_id":"2650c8cc0651996a845a702e16978ae8a77c8bfcebe6a6bf58ffe3c2b4f135e6","message":""}`.
  B10 (2026-09-23, task #190) moved the `revoked` fixture's `signer.role` /
  `expected_pubkey` from `owner` to `owner2`; the builder reads the key from
  `identities-s0-02.json`. When a prior capture removed `owner2`, the
  coordinator re-adds it by hand before the next one with the same command
  (idempotent); the PC runner makes no membership write.
- `nonmember` `f5aa4962136f829d80cd01966d437eba54d8f1ca97b7d2073d3c5560367dd816`
  (generated 2026-09-22T11:12Z, D-038): the `neg-unauthorized` leg's signer;
  ABSENT from the channel's member listing (0 matches, measured after the
  owner2 add). B10 (2026-09-23, task #190) set the `neg-unauthorized`
  fixture's `expected_pubkey` (`null` before) to this value, read from
  `identities-s0-02.json`.

Generation: a 256-bit scalar from Python `secrets` reduced into the curve order,
the public key derived by the repo signer's own `_point_mul(d, G)` x-only rule
(`proofs/S0-01/tools/nostr_verify.py`, the routine `sign_event` uses); the
derivation was validated against the existing `owner.pub` before any key was
written. No `.key.raw` file exists for the two new identities: that file was a
keygen tool's text output and nothing consumes it.

Correction to the note above: the relay's REST API still exposes no membership
read route, but the pinned CLI's `buzz channels members --channel <id>` lists the
membership through the relay's query surface (measured 2026-09-22: four rows
after the add — `owner`, `owner2` as owners; `agent`, `user2` as members), so a
post-removal membership listing IS an independent observation a future revoked
leg can capture.
