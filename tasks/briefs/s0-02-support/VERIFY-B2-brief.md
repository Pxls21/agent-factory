# VERIFY-B2 — adversarial grade of lane B2 (S0-02 round 2: the scan whole, the receipt kept, the removal before the delivery, the replay window, the level-aware canary, producer-shaped receipts, one observable per channel, root closure, the sixth denial leg)

You are an adversarial-verifier (the PC Hermes verify lane; the venue map `tasks/briefs/pc/VENUE-MAP.md` applies). Repo
agent-factory, branch claude/soundbox-kit-migration-iz1jwf. **PIN: `f737de5`** (the S0-02 round-2 checkpoint — lane B2's 57 files at
their FINAL bytes: `proofs/S0-02/check_buzz_authz.py` (661 lines, sha `cbd9bcfd…`), `proofs/S0-02/oracle/denial_table.py` (288,
`a3c31dbd…`), `proofs/S0-02/tools/build_fixtures.py` (546, `fbcc2f7a…`), `proofs/S0-02/tools/pc/deliver_event.py` (202, `a00c3b7b…`),
`proofs/S0-02/tools/pc/run_s0_02_legs.sh` (205, `03dc46c9…`), `proofs/S0-02/spec.json` (24, `b224b522…`),
`tests/test_s0_02_buzz_authz.py` (1412, `055b39d9…`), the regenerated fixture set incl. the new `neg-not-allowlisted` leg in all three
places, the lane's report `tasks/briefs/s0-02-support/B2-report.md` and its transcript `transcripts/pc/pc-b2.md--246bec7.md`).
Grade the bytes of `git archive f737de5` from a scratch copy under your lane's scratch dir; every mutant on scratch copies; every
pytest run with an explicit `--basetemp` and `/home/rocco/venv-agent-factory/bin` FIRST on PATH (the system Python lacks
`rfc3339-validator` — the lane's first gate read `30 failed, 159 passed` for that reason alone; a venue fact, not a product finding);
kill only what you start, by pid; never background a run and stop; no outward actions; no live relay delivery, membership write or
role-key read — the live legs are the coordinator's; never read, print or commit a credential (the identities files hold TEST
identities — cite pubkeys only). Authorization: the owner's own Buzz authorization proof under test on the owner's system.

**Inputs (read in this order):** VERIFY-B1's report `tasks/briefs/s0-02-support/VERIFY-B1-report.md` (the round's contract:
F1-F23, the blocking set, the cheapest path) · the lane brief
`tasks/briefs/s0-02-b2-buzz-authz-the-scan-whole-the-receipt-kept-the-removal-before-the-delivery.md` (12 pinned design items) ·
the lane's report (its NOT-DONE list, the identity table, its 20/20 mutant claim, the 18-class enumeration) · the pinned Buzz source
at `/home/rocco/s0-01-pinned/buzz` (commit `1c8321cd…`; read-only) · `docs/INCIDENT-LOG.md` (AF-AP-34, AF-AP-59, AF-AP-62,
AF-AP-63, AF-AP-65, AF-AP-66, AF-AP-68).

## Item 0 — the mechanical gates, pasted
The coordinator's gates on these bytes: sandbox `RESULT: rev=b0d331cc75e2 files=57 deleted=0 runs=2 identical=yes rc=0
summary="125 passed in 59.70s 125 passed in 53.82s"`, PC `125 passed in 16.71s` (8 workers, 20260908T161930Z-b0d331c). Agree or
disagree by your own run. Then the report-discipline gap the coordinator found: the in-tree report carries the identity table but NO
`file:line` references (the brief's item 12 demanded every reference from `grep -n` on the FINAL bytes with `report_lint … MISS 0`
pasted); the lane's final message carried 15 references and lints `OK 1, MISS 1, UNCHECKABLE 13` on the PIN (the MISS:
`deliver_event.py:109-144` cited for the `HTTP` status claim) — resolve each of the 15 against the PIN yourself and state which
claims have no anchor at all. `ap_screen.py` on the four .py (AP-32 ×3: the specimen/payload sha256 derivations; AP-1 ×1:
`deliver_event.py:74` `os.environ.get("BUZZ_PRIVATE_KEY", "")`) and `--tests` — classify by RUN; pyflakes; the FILE IDENTITY table
against the PIN; the external-command census (VERIFY-B1 F23).

## Items
1. **F1 — the scan is whole and structural (`check_buzz_authz.py`, `test:452-495`).** Reproduce that `#[cfg(test)]` items and comments
   are excluded STRUCTURALLY (not by a prefix cut): plant a verification call inside a `#[cfg(test)] mod` that appears BEFORE
   production code, inside a `/* */` block comment, inside a `//` line comment, inside a string literal, behind a `#[cfg(test)]` on a
   single fn (not a mod), behind `#[cfg(any(test, feature = "x"))]`; an aliased import (`use nostr::Event as E; E::verify`), a method
   call on a trait object, a macro-generated call. Which does the scanner see, which does it miss, and does any miss matter for the
   six pinned production sites? Exact-equality of the site set: add a seventh REAL production site on a scratch copy of the pinned
   source — red? Remove one — red?
2. **F12/F18 — the freshness rule (`test:535-578`, `_is_wall_clock_freshness_rule`).** Attack the predicate: `created_at` compared
   through a helper (`fn age(e) -> u64`), a bound `now` two statements earlier, `saturating_sub` chains, a `Duration` comparison, the
   comparison in the OTHER direction, `9000` vs `900` (the numeric parse), a rule that lives in a `match` arm. Which shapes evade, and is
   the "no wall-clock rule in buzz-acp" claim (D3) still exactly what the test proves?
3. **F14 — receipts in the producer's shape (`check_buzz_authz.py:248-298`, `deliver_event.py:109-144`, `build_fixtures.py`).**
   Attack the five-field shape: `accepted: "true"` (string), `http_status: "200"`, `200.0`, a sixth field, a missing `message`, an echoed
   event id that differs by case, `accepted=false` with `http_status=200`, `accepted=true` with 4xx. Build every fixture bundle fresh
   through `build_fixtures.py` and diff against the committed set (the lane says 8/8 drift-free) — any byte difference is a finding.
   Is `deliver_event._normalise` the ONE producer of the shape (grep every writer of `delivery.json` — the PC runner, the fixture
   builder, any test helper)?
4. **F2/F3 — the receipt survives the wipe and the removal is bound and ordered (`run_s0_02_legs.sh:41,185`,
   `check_buzz_authz.py:454-487`, `test:1340`).** Reproduce the wipe-then-copy on a scratch tree with a fake `$out`; attack the binding:
   `at_epoch_s` as a float, as a bool, `== t0`, one second after t0; `channel` absent from the delivered event's `h` tags; a 3xx and a
   2xx-as-string relay status; a removal recorded for another sender. Is the removal's receipt ITSELF authenticated in any way, or is
   it trusted bytes (state the trust boundary exactly — the verify brief's design question).
5. **F5 — the replay window (`check_buzz_authz.py:108,218-220`, `run_s0_02_legs.sh:148-152`).** The second sub-leg gets 150 s, every
   other leg 120 s: attack with the second sub-leg's `t0.json` carrying its OWN t0 (not the first's), a first delivery that took 149 s,
   a tolerance applied to the wrong sub-leg. Is the 150 s window derived from the pinned relay's constant or typed?
6. **F9/F9b — the level-aware canary.** `DEBUG` on the canary's line: attack with `DEBUG` inside the message text of an INFO line,
   `debug` lowercase, a `TRACE` line, the canary split across two lines; confirm the canary is demanded on exactly the buzz-acp-decided
   rows (which rows are those in the oracle — three now, with `neg-not-allowlisted`) and on NO relay-decided row.
7. **F10/F11 — one observable per channel, root closure (`check_buzz_authz.py:341-379,557-585`, `test:821-857`).** Attack: the named
   observable present in BOTH channels; two observables of different legs in one log; a leg directory with an extra regular file, a
   symlink, a FIFO (standalone under `timeout`, never through pytest), an empty directory, a leg named with a trailing space; the root
   with a `PROVENANCE.md` (allowed?) — enumerate exactly what closure allows and pin it.
8. **The sixth leg `neg-not-allowlisted` (`denial_table.py:248`, `build_fixtures.py:157-160,475-482`, `test:253`).** Is user2's
   observable DISTINCT from `neg-unauthorized` at the evidence level (which line, which channel), and does the distinctness gate count
   six? The blanket-rejection bundle must fail for the exact reason the lane pasted — reproduce. Then the oracle's own claim about
   who decides this leg (relay accepts the member, buzz-acp's author gate drops it): read the pinned source and confirm the deciding
   site by `file:line`.
9. **F17 — D8 stated exactly.** Read `filter.rs` at the PIN's pinned Buzz commit: is `FilterContext.timestamp` reachable from a shipped
   default rule (the lane says no shipped default references it) — confirm by grep over the shipped defaults and state the residual.
10. **The AP-1 hit — `BUZZ_PRIVATE_KEY` from the environment (`deliver_event.py:74`).** An absent or empty key: does the tool fail LOUD
    (named line, non-zero rc) before any network action, or does it sign with an empty key? A key with surrounding whitespace / a
    trailing newline (a `cat`-pasted secret)? Never print the value; test with a throwaway test key you generate on scratch.
11. **Mutants ≥ 30** — the lane's 20 attack rows re-run from YOUR reconstruction (never its driver), VERIFY-B1's 12 survivors named in
    the brief's item 10, plus the attacks above; killer lines pasted; by-construction survivors stated as such.
12. **The 18-class re-scan** on the seven files by RUN; every `if <field> == <literal>:` without a raising other arm listed
    (AF-AP-65); every evidence read through the S0-01 regular-file guard (class 2 — the lane claims all of them; enumerate).
13. **Discipline** — file:line by `sed -n` on the PIN; `report_lint.py` on your own report with `--map C=proofs/S0-02/check_buzz_authz.py
    --map T=tests/test_s0_02_buzz_authz.py --map O=proofs/S0-02/oracle/denial_table.py --map B=proofs/S0-02/tools/build_fixtures.py
    --map D=proofs/S0-02/tools/pc/deliver_event.py --map R=proofs/S0-02/tools/pc/run_s0_02_legs.sh`; the process census by pid.
14. **The design.** Is the synthetic-bundle proof now the PRODUCER's shape end to end (the lane's own "Inferred" tier: the unexecuted
    PC runner produces matching receipt and timing semantics) — what would the live eight-leg capture have to show, and which of the
    three coordinator prerequisites (the RUST_LOG seam, the relay membership write, the role keys) does each leg need? What must round 3
    do to make S0-02 MERGE-READY, and is anything left that is not the coordinator's or the owner's?

## Report
Write it to `tasks/briefs/s0-02-support/VERIFY-B2-report.md` inside your tree, draft after EACH item, and return it whole as your
final message. Findings: ALL, no severity filtering, each with file:line on the PIN, expected vs observed, the failing input, the
minimal fix, the exact red test, SOLID/UNSURE; reproduced vs reviewed vs skipped; verdict MERGE-READY or NOT-READY with the blocking
set and the cheapest path; the items that are the coordinator's or the owner's named as such.
