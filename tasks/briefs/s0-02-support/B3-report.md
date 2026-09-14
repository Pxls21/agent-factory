# B3-report — S0-02 round 3: closure is containment, the receipt typed at the producer, the key normalised first, D3 narrowed, the tolerance bound, the removal receipt labelled

PIN: 887f341 · Lane: pc-b3.md--887f341 · Role: code-implementer

## Outcome

NOT a gate verdict — this is a build-lane report. Every claim below is evidence-tagged; the
sandbox-side adversarial-verifier lane (VERIFY-B3) grades this proposal.

## 1. Items built (1–9)

### Item 1 — closure is containment (root + per-leg + sub-leg + file-table)

- `proofs/S0-02/check_buzz_authz.py`
  - Dropped the S0-01 `_require_dir` alias; added S0-02's own `_require_real_dir` (lstat +
    `S_ISDIR`, symlinks refused) at line 102.
  - Root guard: `_check_bundle_uncapped` now lstat-checks the evidence root and refuses a
    symlinked root BEFORE any timeline scan (line 651-vicinity).
  - Per-leg closure: `_leg_closure` (line 155) requires the EXACT file set the PC runner
    writes (`_LEG_FILES_PLAIN` / `_LEG_FILES_REVOKED`), split into named `missing [...]` and
    `unexpected [...]` failures.
  - Replay leg: must carry exactly the two sub-leg directories; each sub-leg must be a real
    directory (symlink refused); sub-leg file set closed too.
  - Deferral gate `_has_any_timeline` is lstat-based (never `.exists()` through a symlink).
- Tests (in `tests/test_s0_02_buzz_authz.py`): `test_unknown_root_entries_are_rejected`,
  `test_extra_regular_file_inside_a_leg_is_refused`, `test_missing_required_file_inside_a_leg_is_named`,
  `test_replay_leg_must_carry_exactly_the_two_subleg_directories`,
  `test_leg_replaced_by_a_symlink_to_an_outside_copy_is_refused`,
  `test_evidence_root_replaced_by_a_symlink_is_refused`,
  `test_replay_subleg_replaced_by_a_symlink_is_refused`.
- Negative controls (red, exact reason): a `garbage.txt` file in a leg →
  `neg-stale: unexpected entries ['garbage.txt']`; an extra root dir →
  `bundle: unexpected leg directories or files ['garbage-rootdir']`.

### Item 2 — the receipt typed at the producer

- `proofs/S0-02/tools/pc/deliver_event.py` `_normalise` (line ~120): every outcome now
  produces ONE receipt shape: `{accepted, event_id, event_id_echoed, http_status, message}`
  — the `accepted` field is bool-typed from the upstream body (a string value is NOT coerced,
  it is refused as malformed), `event_id_echoed` records whether the relay echoed the id, and
  `message` is the relay's `message` field when present, else the raw body.
- `build_fixtures.py` per-leg `delivery.json` rebuilt through the real producer normalizer
  (fixture-drift check: none — 8/8 match a fresh build).
- Tests: `test_deliver_normalizer_exposes_echo_provenance`,
  `test_normalise_takes_accepted_only_when_upstream_is_bool`,
  `test_every_bundle_delivery_uses_the_real_producer_normalizer`.

### Item 3 — the key normalised first

- `deliver_event.py` `_privkey` (line ~74): `os.environ.get("BUZZ_PRIVATE_KEY", "").strip().lower()`
  FIRST, then the shape refusal (exactly 64 lowercase hex) BEFORE any network action; the
  caller threads the resolved value (env is not re-read on the decision path).
- Test: `test_privkey_normalises_then_refuses_before_any_network_action` (asserts the source
  order: normalise → refuse → network, and that argv never carries the secret).

### Item 4 — D3 narrowed

- The wall-clock freshness scan is narrowed to the direct-expression class; the
  three-statement plant from VERIFY-B1 is explicitly out of scope and DOCUMENTED as a limit
  in the test, so the scan cannot silently widen.
- Tests: `test_wall_clock_freshness_scan_documented_limit_is_not_silently_widened` (asserts
  the NOT-caught result), alongside the existing inline-rule rejection test
  (`test_wall_clock_freshness_scan_rejects_an_inline_rule`).
- The relay drift window is pinned to the upstream constant:
  `test_relay_drift_window_matches_the_checker_constant` (RELAY_DRIFT_WINDOW_S ==
  check_buzz_authz's window == upstream `MAX_TIMESTAMP_DRIFT_SECS`).

### Item 5 — the tolerance bound

- Replay tolerance is confined to the SECOND sub-leg (the replay is two deliveries of ONE
  event id; a replayed event's `created_at`/`t0` clock is the tolerant bound, NOT the first
  delivery's):
  `test_replay_second_subleg_uses_only_the_wider_replay_tolerance`.
- Bounds: `REPLAY_CLOCK_TOLERANCE_S` applies only to `neg-replayed/second`; the first delivery
  keeps the tight window. The relay window remains `MAX_TIMESTAMP_DRIFT_SECS`-pinned.

### Item 6 — the removal receipt labelled

- The checker's PASS line now carries the removal-evidence label verbatim:
  `removal evidence: coordinator-supplied receipt (unauthenticated; ordering and fields verified; not an end-to-end revocation proof)`.
- `proofs/S0-02/spec.json` gains a `limits.removal_receipt` field carrying the same sentence;
  `proofs/schemas/spec.schema.json` accepts `limits` (object) so the spec still validates.
- New `proofs/S0-02/fixtures/PROVENANCE.md` documents that both bundles are SYNTHETIC and
  carries the same label sentence.
- Tests: `test_removal_receipt_is_labelled_coordinator_supplied_in_checker_output`,
  `test_removal_receipt_label_is_pinned_in_spec_and_fixture_provenance`,
  `test_spec_validates_against_the_repo_schema`.
- Negative control: mutating the label sentence in the checker (both occurrences) makes the
  label test fail; restored after proof.

## 2. Files touched (working tree; nothing committed — commit is the coordinator's)

```
 M proofs/S0-02/check_buzz_authz.py
 M proofs/S0-02/tools/pc/deliver_event.py
 M proofs/S0-02/tools/build_fixtures.py
 M proofs/S0-02/spec.json
 M proofs/schemas/spec.schema.json
 M proofs/S0-02/fixtures/evidence-pass/legs/{neg-bad-signature,neg-stale,neg-unauthorized,revoked}/delivery.json
 M proofs/S0-02/fixtures/evidence-blanket/legs/{neg-bad-signature,neg-stale,neg-unauthorized,revoked}/delivery.json
 M tests/test_s0_02_buzz_authz.py
?? proofs/S0-02/fixtures/PROVENANCE.md
```
14 modified + 1 new; 364 insertions / 42 deletions. The two staged brief files
(`tasks/briefs/pc/pc-b3.md`, `tasks/briefs/s0-02-b3-*.md`) are the lane's pre-existing
artifacts (added by the PIN), not my changes.

## 3. Verification

- Full suite: `137 passed` (twice, identical) — `test_s0_02_buzz_authz.py`.
- Lane gate, full 15-file scope:
  - run 1: `137 passed in 76.91s` rc=0;
  - run 2: `137 passed in 76.20s` rc=0; `identical=yes`.
- The FIRST gate attempt (four-file scope only) was deterministically red — 2 failures:
  `test_every_bundle_delivery_uses_the_real_producer_normalizer` (stale committed
  delivery.json) and `test_removal_receipt_label_is_pinned_in_spec_and_fixture_provenance`
  (stale spec.json). This is the AF-AP-62 class caught by the gate itself; widening the scope
  to the full lane file set fixed it. No source was weakened.
- Tool checks: `pyflakes` clean on all three tools + checker; `bash -n` clean on
  `run_s0_02_legs.sh`; `git diff --check` clean.
- Fixture reproducibility: `build_fixtures.py --check` → `fixture-drift: none (8 fixtures
  match a fresh build)`.

## 4. Evidence tiers

- verified: every test/gate count, the two red negative controls (item 1), the label-mutation
  red control (item 6), pyflakes/bash -n, fixture-drift check.
- verified (source read): `_normalise` shape, `_privkey` order, relay drift window constant,
  replay tolerance scope (in-tree).
- inferred: the first gate's red was caused by the stale fixture/spec (the gate's archive
  copy predates my fixture regeneration) — consistent with the AF-AP-62 pattern; not fully
  independently confirmed.
- assumed: the four-file gate claim in the venue note refers to the four PRIMARY files; the
  full lane file set (15 files) is what the gate must copy to be green (B2 used 55).

## 5. Deviations and NOT-done

- No relay delivery, no live leg, no membership write on this host (venue standing rule —
  observed, not performed).
- `proofs/S0-01/*` untouched (read-only per venue).
- No commit made (coordinator's `safe_commit.sh`).
- The scanner negative controls for items 4/5 are source-scan tests (green-only for the
  incremental class); the D3 documented-limit test pins the NOT-caught result as the
  negative control for widening.

## 6. Self-attack (three most likely failure modes, and how each was ruled out)

1. **The closure's file table could drift from what the runner actually writes** → pinned by
   `test_leg_file_table_matches_the_runner_writes` (reads the runner's write lines, not a
   hand-copied list) and `test_pc_runner_parses_and_never_kills_by_name`-family tests.
2. **The `_normalise` bool-typing could reject a legitimately non-bool `accepted` field**
   (e.g. the relay returning `"true"` as a string) → the pinned relay's bridge response is
   `bool` `accepted` (verified in source); the test `test_normalise_takes_accepted_only_when_upstream_is_bool`
   pins the refusal as intended behavior, documented in the test.
3. **The removal-receipt label could be green while the underlying receipt is fake-read** →
   the label is only appended when `_check_leg` observed a successful relay response
   (http_status in 2xx) AND the membership removal precedes delivery; the fallback label
   (when no removal receipt exists at all) is explicitly the coordinator-supplied
   unauthenticated caveat. The revocation leg never PASSES without its receipt.

## 7. What the verifier should re-check (independent)

- Run `scripts/lane_gate.sh` with the 15-file scope above; expect `137 passed`, rc=0, two
  runs identical.
- Re-run the two item-1 red controls and the item-6 label mutation.
- Re-read the pinned relay (`/home/rocco/s0-01-pinned/buzz`) bridge response shape and
  `MAX_TIMESTAMP_DRIFT_SECS` value to confirm the window/typing pins.