# Lane B3 — S0-02 round 3: root closure is CONTAINMENT (every expected entry a real directory under the real root, closure inside each leg), the receipt's `accepted` typed at the producer, the key normalised before the empty check, D3 narrowed to the class the scanner proves, the replay tolerance bound to the source-derived window, the removal receipt labelled for what it is (build lane: PC Hermes `code-implementer`; sandbox Opus 4.6 `code-implementer` only if the bridge is down)

PIN: (HEAD at dispatch — the commit carrying this brief; the report header says "PIN: `<sha>`".) Lane B2's landing is `f737de5`
and every S0-02 file is unchanged since. Line numbers below are those bytes'.

**Why:** VERIFY-B2 (`tasks/briefs/s0-02-support/VERIFY-B2-report.md` — READ IT WHOLE FIRST; it is the contract for this round)
graded round 2 NOT-READY with three SOLID defects in the evidence path, each reproduced on scratch copies: **F1** root closure
(`C:567-589`) compares NAMES — `expected_entries = set(LEG_NAMES)` against `root.iterdir()` names — and `_check_leg` reaches the
leg through S0-01's `_require_dir` (`is_dir()`, which follows symlinks); an expected leg directory replaced by a SYMLINK to a
complete copy OUTSIDE the evidence root returned rc 0 and the normal PASS line, and an extra regular file INSIDE a leg is not
rejected at all (closure exists only at the root); the deferral helper `_has_any_timeline` (`C:556-564`) calls `.exists()` before
any containment is established. **F2** the ONE live receipt producer, `deliver_event.py:109-143` (`_normalise`), does
`receipt["accepted"] = bool(blob["accepted"])` — a relay response `{"accepted":"false",…}` is stored as `true`, and the
stored-bundle checker (which rightly rejects non-bool receipts) can no longer see the malformed upstream (registry row
**AF-AP-72**). **F3** `_privkey` (`deliver_event.py:71-79`) checks the UNTRIMMED environment value and only then returns
`key.strip().lower()` — a whitespace-only `BUZZ_PRIVATE_KEY` passes the preflight and reaches signing as an empty key.
**F4 UNSURE** the freshness scanner classifies single lines: `event_time = event.created_at; age = clock.duration_since(event_time);
if age > maximum_age` evades it, so the test's claim "no wall-clock freshness rule on the channel path" is true only for the
direct same-expression class. **F5 UNSURE** the revoked leg's membership-removal receipt is coordinator-authored and
unauthenticated (the checker validates its fields and ordering, nothing else). Also observed: `REPLAY_CLOCK_TOLERANCE_S = 150`
(`C:108`) is a typed allowance with no derivation from the pinned relay constant; the B2 report carried no machine-checkable
`file:line` refs (its own lint `16 OK, 1 NEAR, 7 MISS, 3 UNCHECKABLE`, rc 1). What held and must stay held: the six pinned
production verification sites, the level-aware canary (`C:318-356`), exactly-one-observable per channel, the blanket-rejection
failure, the eight receipt shapes and eight removal attacks killed, the FIFO refusal, the fixture drift check (`none`),
`125 passed` twice on both venues.

**Inputs (read in this order):** VERIFY-B2 whole · the B2 brief and `tasks/briefs/s0-02-support/B2-report.md` ·
`proofs/S0-01/check_acp_conformance.py:198-214` (`_require_file`/`_require_dir` — S0-01's; you do NOT edit them) ·
`proofs/S0-01/pins.py` (`require_regular_file`) · `proofs/S0-02/tools/pc/run_s0_02_legs.sh` (what it writes per leg — the
per-leg file set of item 1 is DERIVED from it; the membership step at `:40-41,171-185`) · the pinned relay's api surface
`<S0_02_BUZZ_SRC>/crates/buzz-relay/src/api/mod.rs:80,152` (`check_relay_membership` / `enforce_relay_membership` are INTERNAL
enforcement, there is no membership READ route — verify by grep and cite) · `docs/INCIDENT-LOG.md` (AF-AP-30, AF-AP-40,
AF-AP-63, AF-AP-65, AF-AP-72) · the pack `scripts/lane_context.sh -q 'what reads a leg directory and what closes the evidence root' -s _check_bundle_uncapped _check_leg _has_any_timeline _check_replay -o pack.md proofs/S0-02/check_buzz_authz.py`
(run it first; attach it).
**Scope (under S0-02 + its test + your report):** `proofs/S0-02/check_buzz_authz.py` · `proofs/S0-02/tools/pc/deliver_event.py`
· `proofs/S0-02/tools/pc/run_s0_02_legs.sh` (only where an item names it) · `proofs/S0-02/tools/build_fixtures.py` and
`proofs/S0-02/fixtures/**` (regenerated ONLY if an item changes a bundle's shape — say so) · `proofs/S0-02/spec.json` (the
limits text of item 5) · `tests/test_s0_02_buzz_authz.py` · `tasks/briefs/s0-02-support/B2-report.md` (ONE stamp line, item 7)
· report `tasks/briefs/s0-02-support/B3-report.md`. NOT yours: `proofs/S0-01/*` (read-only; the RUST_LOG env extension is lane
P5c's, running now), the oracle (`denial_table.py` — unchanged this round), `scripts/validate-ledger`, `proofs/registry.yaml`,
the seed. Shared-tree rules: never `git stash/checkout/restore/reset/add/commit/push`; every gate from a `git archive <PIN> | tar -x`
copy under your lane's scratch dir with your files copied in (`scripts/lane_gate.sh -r <PIN> -f "<your files>" -t "tests/test_s0_02_buzz_authz.py tests/test_spec_probe_schemas.py tests/test_validate_ledger.py tests/test_proof_runner.py" -n 2`,
ONE foreground call, `LANE_GATE_DIR` under your scratch dir); explicit `--basetemp`; kill only your own processes by pid; NEVER
background a run and stop; no outward actions; NO network call to any relay; the runner and `deliver_event.py` are `bash -n`/
pyflakes-checked and READ, never run against a relay (their pure functions are unit-tested in-process); never read, print or
commit a private key (every key in a test is a labelled non-secret throwaway). Venue exports `S0_01_VENUE=pc
S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`. Authorization: the
owner's own relay authorization boundary under test; the forged bundles are defensive fixtures.

## Design (pinned — build it, do not redesign it)
1. **F1 — closure is containment, at the root AND inside every leg.** S0-02 gets its own `_require_real_dir(path, leg, name)`
   (never S0-01's): `os.lstat` → `S_ISDIR` (a symlink → `Failure(f"{leg}: {name} is a symlink")`, absent → the existing "absent"
   text), and `path.resolve()` must have the RESOLVED root as an ancestor (belt after the lstat). The root itself: `lstat` must be a
   directory, not a symlink; `_check_bundle_uncapped` resolves it ONCE and every leg, every replay sub-leg and every file read goes
   through the real-dir guard first. `_has_any_timeline` (`C:556-564`) runs AFTER the root guard and uses `lstat`-based checks,
   never `.exists()` through a symlink. Per-leg closure: a constant table `LEG_FILES` (per leg kind: the exact file names the
   runner writes — derive it from `run_s0_02_legs.sh` and cite the lines; the replay sub-legs and the revoked leg's
   `membership.json` included) and `{p.name for p in leg_dir.iterdir()} == LEG_FILES[kind]` or `Failure(f"{leg}: unexpected
   entries {sorted(extra)}" / "missing …")`. Red tests (RED on the PIN — paste each): the verifier's exact attack (the expected
   leg `legs/neg-stale` replaced by a symlink to a complete outside copy → rc 1, the named reason); a symlinked ROOT; a symlinked
   replay sub-leg; an extra regular file inside a leg; a missing required file named. The committed bundles must still PASS
   unchanged — if `LEG_FILES` disagrees with a committed bundle, the BUNDLE is wrong only if the runner's writes say so; otherwise
   your table is — resolve from the runner, never by widening the table.
2. **F2 — `accepted` is a bool or the receipt says why.** `_normalise`: `accepted` is taken only when `type(blob["accepted"]) is bool`;
   any other type → `accepted: false` and `message: "malformed relay response: accepted is <type name> <repr>"` (the receipt keeps
   its FIVE fields — the checker's shape rule stays exact). Direct in-process tests of `_normalise` for `"false"`, `"true"`, `0`, `1`,
   `1.0`, `True`, `False`, `None`, absent — every outcome exact. `ap_screen.py` over `deliver_event.py`: AF-AP-72 = 0 hits (paste).
   The synthetic builder imports the live normaliser: rebuild the fixtures and prove `fixture-drift: none` (they carry bools, so
   nothing should move — say so from the run).
3. **F3 — normalise, then refuse.** `_privkey`: `key = os.environ.get("BUZZ_PRIVATE_KEY", "").strip().lower()`; empty → the existing
   `SystemExit` text; then the SHAPE: read how `nv`/the signer consumes the key (64 lowercase hex chars, or whatever the
   consumer contract is — cite it) and refuse anything else with `BUZZ_PRIVATE_KEY is not a <shape>` BEFORE any network action.
   Tests: spaces only, `\t\n` only, a valid throwaway with surrounding whitespace (normalised, never printed), a 63-char value.
4. **F4 — D3 stated for the class the scanner proves, with the miss pinned.** The docstrings of
   `test_buzz_acp_has_no_wall_clock_freshness_rule_on_the_channel_event_path` (`T:550-563`) and the B2/B3 reports say: "no
   DIRECT same-line comparison of `created_at` against a clock in the channel-event region; a rule split across statements is
   outside this scanner's class". Pin the limit honestly: a control asserting the verifier's three-statement plant is NOT caught
   (`assert not any(_is_wall_clock_freshness_rule(l) for l in plant.splitlines())`) with a comment naming it a documented limit,
   so the claim can never silently widen. Do not build a Rust dataflow analysis.
5. **F5 — the removal receipt labelled, no signature pretended.** There is no membership READ route on the pinned relay (cite
   `api/mod.rs:80,152` — internal enforcement only), so no independent post-removal observation exists to capture. The checker's
   revoked-leg summary line therefore prints `removal evidence: coordinator-supplied receipt (unauthenticated; ordering and
   fields verified; not an end-to-end revocation proof)`; the same sentence goes into `spec.json`'s limits/provenance text and the
   fixtures' `PROVENANCE.md`. A test pins the sentence in the checker's output for the revoked leg.
6. **The replay tolerance bound, not typed.** Keep 150 s as the runner's replay budget but PIN its joint satisfiability from the
   source-derived window: a test asserts `REPLAY_CLOCK_TOLERANCE_S + LEG_CLOCK_TOLERANCE_S < RELAY_DRIFT_WINDOW_S` where
   `RELAY_DRIFT_WINDOW_S` is the value the existing source scan derives from the pinned relay (cite the scan and the relay line),
   and the runner's replay gap constant (grep it; cite) `<= REPLAY_CLOCK_TOLERANCE_S`. A mutant setting the tolerance to 9000
   must die by the first assertion; one setting the runner's gap above the tolerance by the second.
7. **The B2 report stamped**, one line at its top: `STAMP 2026-09-08 (B3): this report's claims are prose without file:line refs (VERIFY-B2 item 13); B3's report carries them.`
8. **Mutants:** the verifier's three survivors as named killers (`LEG-SYMLINK`, `ACCEPTED-TRUTHINESS`, `KEY-WHITESPACE`) plus
   `ROOT-SYMLINK`, `LEG-EXTRA-FILE`, `RESOLVE-DROPPED` (the ancestor check removed), `LSTAT-TO-ISDIR` (the guard rewritten with
   `is_dir()`), `TYPE-TO-ISINSTANCE-INT`, `TOLERANCE-9000`, `LABEL-DROPPED`; B2's 20 re-run and still dead; every mutant on a
   scratch copy, the killer line pasted.
9. **Report discipline:** FILE IDENTITY of the FINAL bytes; every `file:line` from `grep -n` on the FINAL bytes and
   `python3 scripts/report_lint.py <report> --rev <PIN> --map C=proofs/S0-02/check_buzz_authz.py --map T=tests/test_s0_02_buzz_authz.py --map O=proofs/S0-02/oracle/denial_table.py --map B=proofs/S0-02/tools/build_fixtures.py --map D=proofs/S0-02/tools/pc/deliver_event.py --map R=proofs/S0-02/tools/pc/run_s0_02_legs.sh`
   pasted with MISS 0 — this round's report MUST be machine-checkable, the verifier confirmed round 2's was not; the two gate
   RESULT lines; every red-before pasted beside its green-after; pyflakes + `bash -n`; `ap_screen.py` over the five S0-02
   sources; the pack attached; NOT-done first-class. NOT this lane's: the live eight-leg capture (the RUST_LOG seam = P5c's env
   extension, the role keys, the owner-run membership removal), round 3's ledger-floor bundles, the S0-02 runner's
   `--env-set s0-02` selection (after P5c lands).
