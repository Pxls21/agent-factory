# Lane M3 — S0-06 round 3: exact regular-file manifests with every declared leaf graded, the C6 truth, the raw URL bound to the run's origin, the query text out of the telemetry path

**PIN: `038bc9b`** (the current branch head; the S0-06 files are cb91edf's round-2 bytes, unchanged since). Role: code-implementer
(the PC Hermes build lane; the venue map `tasks/briefs/pc/VENUE-MAP.md` applies). Repo agent-factory, branch
claude/soundbox-kit-migration-iz1jwf. Boundary (yours, disjoint from every other lane): `proofs/S0-06/check_four_scope.py`,
`proofs/S0-06/adapter/factory_memory.py`, `proofs/S0-06/tools/pc/start_ai_memory.sh`, `proofs/S0-06/tools/pc/collect_leg.sh`,
`proofs/S0-06/tools/pc/run_s0_06_legs.sh`, `proofs/S0-06/fixtures/**`, `tests/test_s0_06_four_scope.py`, your report
`tasks/briefs/s0-06-support/M3-report.md`. Nothing else. No live ai-memory run, build, clone or start (the venue rule); no outward
actions; kill only what you start, by pid; never background a run and stop.

**Inputs (read in this order):** VERIFY-M2's report `tasks/briefs/s0-06-support/VERIFY-M2-report.md` (the round's contract: F-27,
F-28, F-29, F-25, the C-matrix, §9 the cheapest path) · the M2 lane report `tasks/briefs/s0-06-support/M2-report.md` (its C-matrix
claim at :51 is the one you correct) · the M2 brief
`tasks/briefs/s0-06-m2-four-scope-the-leak-agent-seeded-the-oracles-scoped-the-shapes-named.md` (items 1-13, still binding) ·
`docs/INCIDENT-LOG.md` (AF-AP-40, AF-AP-59, AF-AP-63, AF-AP-65, AF-AP-68).

## Design (pinned — build it, do not redesign it; line numbers are `038bc9b`'s = cb91edf's for these files)
1. **F-27 — the manifest is EXACT and every declared leaf is GRADED.** `_check_expected_files` (`check_four_scope.py:490-501`) compares
   each leg's COMPLETE relative-file set (a recursive walk, `lstat`) to `EXPECTED_FILES` (`:116`): a missing declared leaf, an extra
   leaf, a declared name that is a directory or a symlink or any non-regular file → rc 1 with one named line per defect
   (`leg: expected evidence file <name> missing` / `… is not a regular file` / `leg: unexpected evidence file <name>`); the root is
   closed the same way (an unexpected root file is a named failure; `PROVENANCE.md` is either declared or refused — declare it).
   The six never-read names are GRADED, never dropped (an emitted-but-unread evidence file is a silent hollow green — CLAUDE.md
   build-loop rule 1; REJECTED alternative: removing them from the collector, which discards the reason-carrying telemetry the
   observability rule demands): `precedence/events-1.jsonl` and `events-2.jsonl` → the adapter's search events for exactly the four
   scopes, every event in the leg's allowlist, no `http_request` outside the leg's recorded instance (the same discipline as the
   denied leg's F-8 allowlist); `write-scope/events-write.jsonl` and `events-retry.jsonl` → the write event set (one authorized
   write, the retry's idempotent no-op, no second write of the same key); `leak/events.jsonl` → the two agents' search events with
   no cross-scope read; `write-scope/record.json` → equals the written page re-derived (path, idempotency key, type). Each file's
   grade is a function with a red test.
2. **Fixtures regenerated from the COLLECTOR's shape.** Every committed bundle (`evidence-*`) carries the full 48-leaf producer shape
   (VERIFY-M2 measured 48 from a loopback `collect_leg.sh` run); the two negative bundles stay negative for their OWN reason and for
   nothing else — a negative fixture that also lacks six files proves the wrong thing. State the generator (a checked-in script or the
   collector itself) and the drift test (a fresh build equals the committed bytes).
3. **F-28 — the C6 truth.** The M2 report's C-matrix row C6 (`factory_memory.py:160` `row[f]` → `row.get(f)`) is EQUIVALENT behind the
   row validation at `:154-159`: correct the row in YOUR report's inherited matrix as an equivalent survivor with the reason, and add
   the COMPOUND mutant C6′ (the validation guard deleted AND `row.get`) with its exact red test
   (`test_a_malformed_table_row_can_never_authorize_a_null_tuple` or a sharper one) — the killer line pasted. Never claim a kill you
   did not reproduce.
4. **F-29 — the raw instrument bound to the run's origin.** `start_ai_memory.sh` records a non-secret `origin` (`scheme://host:port`)
   in `substrate.json` beside the existing observation fields; `_require_raw_url` (`check_four_scope.py:259-263`) requires the raw
   URL's scheme + netloc to EQUAL that origin and the route + project to be the exact expected ones; a foreign host, a foreign port,
   a right-named foreign endpoint → rc 1 with a named line. The provenance-only design of the digest (`:306`) stays described as such.
5. **F-25 — the query text leaves the telemetry path.** `factory_memory.py:296-309`: the `http_request` event carries a route-only
   path and a deterministic query digest (sha256 of the query, first 16 hex), never the query text; the documentation test at
   `tests/test_s0_06_four_scope.py:1791-1798` becomes a scrubber test (a query with a canary token → the token appears in NO emitted
   event). Every other emitted field unchanged (byte-invisible to the checker's existing grades — prove it by the unchanged fixtures'
   pass).
6. **Every negative control fails for the EXACT expected reason** (the named line asserted, never `rc != 0` alone; AF-AP-63); every
   `if <field> == <literal>:` has a raising other arm (AF-AP-65); no `pkill`/`pgrep -f`/name kill anywhere (AF-AP-34/59).
7. **Mutants:** VERIFY-M2's V1-V20, H1-H11, L1-L5, the six malformed loopback bodies, C1-C10 with C6 corrected and C6′ added, plus
   F-27's four hostile shapes (absent, malformed, directory, symlink) under EVERY previously unopened name, an unexpected root file,
   F-29's foreign host / foreign port, F-25's canary — every one killed with its killer line pasted; by-construction survivors named.
8. **18-class self-sweep as an ENUMERATION** (counts + method per class; class 11 world-enumeration now CLOSED by the exact manifest —
   show the walk; class 18 malformed-row with the honest C6 row).
9. **Report discipline:** FILE IDENTITY of the FINAL bytes; every `file:line` from `grep -n` on the FINAL bytes and
   `python3 scripts/report_lint.py <report> --map C=proofs/S0-06/check_four_scope.py --map A=proofs/S0-06/adapter/factory_memory.py
   --map T=tests/test_s0_06_four_scope.py --map S=proofs/S0-06/tools/pc/start_ai_memory.sh --map L=proofs/S0-06/tools/pc/collect_leg.sh
   --map R=proofs/S0-06/tools/pc/run_s0_06_legs.sh` pasted with MISS 0; the direct venue suite pasted
   (`S0_06`-free — this suite needs no real-leg exports; an absolute `--basetemp`); the two `lane_gate.sh` RESULT lines
   (`scripts/lane_gate.sh -r 038bc9b -f "<your files>" -t "tests/test_s0_06_four_scope.py" -n 2`); `ap_screen.py` prod + `--tests`
   classified by run; NOT-done first-class (the live ai-memory leg — the coordinator's after this round's verify; D-2 / ADR 0003 —
   the owner's).

## Report
Write it to `tasks/briefs/s0-06-support/M3-report.md` inside your tree, draft after EACH item, and return it whole as your final
message: the DONE table (item → file:line → the red test → its killer line), the mutant table, the discrepancies, the self-attack,
the evidence tiers (verified / inferred / assumed), NOT-done first.
