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

Revoked-leg removal evidence is a coordinator-supplied receipt
(unauthenticated; ordering and fields verified; not an end-to-end revocation proof).
The pinned relay exposes no membership READ route
(`crates/buzz-relay/src/api/mod.rs` — `check_relay_membership` /
`enforce_relay_membership` are internal enforcement only), so no independent
post-removal observation exists to capture.