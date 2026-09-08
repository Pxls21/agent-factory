# VERIFY-M2 — adversarial grade of lane M2 (S0-06 four-scope round 2: the leak agent seeded, the oracles scoped to the records, the hostile shapes named, the substrate digest observed and bound to the run, a closed per-leg file manifest)

You are an adversarial-verifier (the PC Hermes verify lane; the venue map `tasks/briefs/pc/VENUE-MAP.md` applies). Repo
agent-factory, branch claude/soundbox-kit-migration-iz1jwf. **PIN: `cb91edf`** — the commit carrying the round's 55 files:
`proofs/S0-06/check_four_scope.py` (549 lines, sha `b02c9d3c…`), `proofs/S0-06/adapter/factory_memory.py` (506, `119fa343…`),
`tests/test_s0_06_four_scope.py` (1798, `440f72ba…`), the three PC scripts under `proofs/S0-06/tools/pc/`, both regenerated
bundles under `proofs/S0-06/fixtures/`, and the lane's report `tasks/briefs/s0-06-support/M2-report.md`. Grade the bytes of
`git archive cb91edf` from a scratch copy under your lane's scratch dir; every mutant on scratch copies; every pytest run with an
explicit `--basetemp`; every loopback server you start is killed by pid; NEVER start, build or clone ai-memory here (the live
leg is NOT this grade's — VENUE-MAP: no ai-memory checkout on this host); no outward actions; never read, print or commit a
credential (the honeytokens are synthetic canaries by design). Authorization: the owner's own memory boundary under test on the
owner's system.

**Inputs (read in this order):** VERIFY-M1's report `tasks/briefs/s0-06-support/VERIFY-M1-report.md` (the round's contract:
F-1..F-25, the V1-V20 / H1-H11 / L1-L5 / G1-G5 / C1-C10 mutant tables, PIN 380877b) · the lane brief
`tasks/briefs/s0-06-m2-four-scope-the-leak-agent-seeded-the-oracles-scoped-the-shapes-named.md` (the pinned design, items
1-13) · the lane's report `M2-report.md` — READ ITS SCOPE SECTION FIRST: the PC session claims ONLY its own V17 edit; the
rest of the 55-file diff is the quota-killed sandbox session's draft, claimed by nobody — you grade it from the bytes · the M1
report `M1-report.md` (its F-17 re-paste) · `docs/INCIDENT-LOG.md` (AF-AP-40, AF-AP-42, AF-AP-63, AF-AP-65, AF-AP-66).

## Item 0 — the mechanical gates, pasted
`python3 scripts/report_lint.py tasks/briefs/s0-06-support/M2-report.md --rev cb91edf --map factory_memory.py=proofs/S0-06/adapter/factory_memory.py --map check_four_scope.py=proofs/S0-06/check_four_scope.py --map seed_scopes.py=proofs/S0-06/tools/pc/seed_scopes.py --map run_s0_06_legs.sh=proofs/S0-06/tools/pc/run_s0_06_legs.sh --map start_ai_memory.sh=proofs/S0-06/tools/pc/start_ai_memory.sh --map collect_leg.sh=proofs/S0-06/tools/pc/collect_leg.sh`
(the coordinator read `8 refs — OK 8, NEAR 0, MISS 0`); `ap_screen.py` over the checker + adapter + seed_scopes (3 hits) and
`--tests` over the test (4 hits) — classify by RUN; pyflakes; `bash -n` ×3; the FILE IDENTITY table against the PIN; the four
test files the lane brief names, run directly: the coordinator read sandbox `236 passed` ×2 and PC `236 passed in 7.84s` — agree
or disagree by your own run.

## Items
1. **F-1..F-25 closure, by RUN, one row each.** Reconstruct VERIFY-M1's mutants on the PIN's bytes yourself (never the lane's
   driver): V1-V20, H1-H11, L1-L5, G1-G5, C1-C10 — killed / survives, the killer line pasted. The lane did NOT re-run H, L and
   G as matrices ("their paths run inside the 170 tests" — an inference); those three families are yours entirely.
2. **The V17 manifest (`check_four_scope.py:116-138`, `:490-502`).** The coordinator found that `EXPECTED_FILES` allows SIX
   names the checker never opens — `precedence/events-1.jsonl`, `events-2.jsonl`, `write-scope/events-retry.jsonl`,
   `events-write.jsonl`, `leak/events.jsonl`, `write-scope/record.json` — and that both golden bundles lack all six. Attack:
   hostile content under an allowed-but-unopened name (is it graded by anything?); a SUBDIRECTORY named like an expected file;
   a symlink named as an expected file that points outside the bundle; a name the collector writes that the manifest lacks
   (reconstruct the collector's write set from `collect_leg.sh` by RUN on a fake adapter, not by reading); a manifest name the
   collector never writes. Decide: is a manifest that names ungraded files a closed manifest, and are fixtures that lack files
   the producer always writes "a shape the producer can emit" (AF-AP-42) or its inverse?
3. **D-3b — the socket-side witness (`_new_connections`, `check_denied`).** How does it count (which instrument, which
   port, which state)? Attack: a foreign process opening a connection to the same port during the denied leg; a witness that
   counts the SAME connection twice; the positive control's floor (why ≥ that number); the vacuity guard
   (`denied_witness_vacuous`) — a bundle whose precedence witness fired exactly once.
4. **F-2/F-3/F-4 — the substrate record as an observation.** A bundle whose per-leg digest equals the startup digest but whose
   `posture_observed` contradicts the posture block; the version from `upstream.lock.yaml` — a lock bumped to 1.40.0 → RED?;
   a lock with a duplicate `ai-memory:` key (F-12); `binary_sha256_observed` — provenance, not a pin: can a bundle from a
   DIFFERENT binary pass by carrying its own consistent digest (say so — is that the accepted design?).
5. **F-5/F-6/F-7 — provenance, content, derivation.** A `raw-<scope>.url` naming the right workspace/project on a different
   host/port; a url for one scope pointing at another scope's page; the merged winner's title/snippet from the wrong scope's
   raw hit; a `page_path` derived from a different key; `kind`/`tier` mutations in the raw listing.
6. **F-8/F-9 — the denied allowlist and the vacuity oracle.** Tokens inside `records[].snippet` vs `records[].title` vs a
   nested field vs a key name; the forbidden half whole-file (a forbidden token in a key NAME); an event stream with
   `scope_tuple_denied` plus a second harmless event (`denied_request` must name it).
7. **F-10/F-11 — shapes and degradation.** The eight shapes + the absent bindings table → rc 1, ONE stdout line, no
   `Traceback` on stderr (paste one); the adapter against a loopback recording server with G1-G5 bodies → `degraded`, exit 3;
   an unexpected exception → exit 70 with ONE stderr line, never 1.
8. **F-12..F-25 — one run each**: shadowed_scopes minus the winner (F-13), an unknown scope name in a bindings row (F-14),
   `allow_nan=False` at BOTH sinks (F-15: NaN and Infinity), the external-command list vs the scripts' actual invocations
   (F-16, by RUN over the three scripts), the token shred + the ONE derivation (F-18, static), `S0_06_SRC` unset → a clone
   under `$RUNDIR/src` (F-19, static), the S_ISREG guard (F-20: dir, FIFO, symlink — the FIFO probe standalone under
   `timeout`), a symlinked evidence root (F-22), the nondet note (F-24), the query text out of the event path (F-25).
9. **The 18-class re-scan** on the checker, adapter, test and the three scripts by RUN; every `if <field> == <literal>:`
   without a raising other arm listed (AF-AP-65); the report's class table agreed or disagreed per row.
10. **The PC runner, static (never run here).** `run_s0_06_legs.sh`, `start_ai_memory.sh`, `collect_leg.sh`: every
    `set -e` exit path before a bundle is graded (the F-1 class), the readiness wait's failure arm, the stop-by-pidfile path,
    the seeding of BOTH agents (F-1) — idempotent on a re-run?
11. **Mutants ≥ 40** (the reconstructions above + your own), pasted with killer lines; by-construction survivors stated as such.
12. **Discipline** — file:line by `sed -n` on the PIN; `report_lint.py` on your own report; the process census by pid.
13. **The design.** Is a per-leg exact manifest the right shape, or should every file under a leg be graded or refused
    (which is it today for the six names)? What must the round after this one do to make S0-06 capture-ready on the PC
    (VERIFY-M1's preconditions, the seeding, the witness), and which items are the owner's (D-2, the ADR 0003 conflict) or the
    coordinator's (D-3's rename, the live leg)?

## Report
Write it to `tasks/briefs/s0-06-support/VERIFY-M2-report.md` inside your tree, draft after EACH item, and return it whole as
your final message. Findings: ALL, no severity filtering, each with file:line on the PIN, expected vs observed, the failing
input, the minimal fix, the exact red test, SOLID/UNSURE; reproduced vs reviewed vs skipped; verdict MERGE-READY or NOT-READY
with the blocking set and the cheapest path; the items that are the owner's or the coordinator's named as such.
