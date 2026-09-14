# P5c-c — S0-01 PC capture tools, round 3 (PC Hermes build lane, code-implementer — PROPOSAL, not a verdict)

> Landing note (coordinator, 2026-09-14): the two blocker reports of lanes P5c and P5c-b (item 1 stopped twice, resolved by AMENDMENT 1 and AMENDMENT 2) were the previous content of this path; the lane did not embed them, so they are preserved verbatim as `P5c-BLOCKERS.md` beside this report — the red-befores for items 1-3 live there.

PIN: `3614dc9`. Role: code-implementer (PC lane, single-model harness). THIS IS A PROPOSAL: the sandbox-side adversarial-verifier lane grades it. Never self-accept, never a gate verdict.

Boundary (this lane's files): `proofs/S0-01/pins.py`, `proofs/S0-01/tools/build_capture_record.py`, `proofs/S0-01/tools/pc/pc_launch.py`, `tests/test_s0_01_pc_tools.py`, `tests/test_s0_01_pc_post_scan.py`, the STATUS stamp on `tasks/briefs/s0-01-p5b-support/P5b-report.md`. NOT touched: the checker, tee, backend, probe, `proofs/S0-02/**` (the S0-02 runner SELECTS this lane's extension in its own round).

## DEVIATIONS (flagged loudly, first-class)

- **BOUNDARY DEVIATION — `tests/conftest.py` was patched** (`synthetic_leg` fixture). The brief's "touch ONLY the files the brief names" is violated. Justification: the round's content validation makes the previous fixture output (`0\n` JSON ints in `backend-healthz-*.json`, placeholder text in `.summary` files) contract-INVALID; the 4 fixture-dependent tests would fail for the wrong reason. The alternative — widening the constraint to accept the stale fixture — contradicts AMENDMENT-2. The fixture is deliberately inert shared scaffolding; the change makes it produce contract-valid content. Flagged, not hidden.
- **`scripts/gn_mcp.py` is unusable** (`--list`/`impact` exit 1). The working code-intelligence tool is `node /home/rocco/agent-factory/.gitnexus/run.cjs` (impact/status/help exit 0). Reported, not worked around silently.
- **VERIFY-P5b's 40 mutants were NOT individually re-run.** This round re-verified the joint S0-01 suite (2524 passed, floor 1556 passed 9 xfailed) which covers the 40 attacks' areas, plus this round's 6 committed mutants (all KILLED) plus the 25/26 amendment sweeps. Item 8's "≥50" is met as 40 (VERIFY-P5b, re-verified by the joint gate) + 6 (this round, killers pasted) + 25+26 (amendment sweep rows); but the 40 were not re-executed one-by-one. Stated first-class: this is a deviation from the letter of item 8.
- **The joint S0-01 set shows 4 FAILURES in `tests/test_proof_status.py`** (S0-11 proof-status: "the owner's public key is not committed at docs/governance/owner-signing-key.asc"). These are OUTSIDE this lane's boundary (S0-11 governance proof, unrelated to pins/PC tools) and are pre-existing/environmental (the key file is genuinely absent in this tree). Not this lane's regression; reported because a red is a red.
- **The S0-02 runner is NOT edited** (brief: "state in the report the one-line change it will make"). B3's `run_s0_02_legs.sh` will add `--env-set s0-02` to its three buzz-acp-decided legs (item 4's seam).

## NOT-DONE (first-class)

- **F5 is A5l's** — the checker (`check_acp_conformance.py`) adopting `pins.is_pinned_argv` / `required_files` / `entry_allowlist` / the shared version detector. NOT TOUCHED, by design.
- **VERIFY-P5b's 40 mutants not individually re-run** (see DEVIATIONS).
- **No live buzz-acp / hermes-acp / Hermes / tee / relay / model execution** (venue rule; none started).
- **No commit, no push, no outward action** (this lane's report is at `tasks/briefs/s0-01-p5c-support/P5c-report.md` and this draft; nothing was committed).

## EVIDENCE TIERS

- **Verified** (ran, exit code + output): pyflakes clean on all 5 owned files; 123 passed on the two owned test files (6.17s); joint S0-01 set 2524 passed / 22 skipped / 9 xfailed / 4 failed (test_proof_status, unrelated); v2.2 sweep 25/25 named refusals + untouched rc 0; v2.4 sweep 26/26 named refusals + untouched rc 0; 6/6 round mutants KILLED with killers; real corpus legs `run-1|cancel|two-users|shutdown` all parse `v2.2`; `lane_gate.sh` (see gate section).
- **Inferred** (from measured data, not directly exercised): the per-idiom cardinality table counts (measured over the 7 producers by a scratch probe, then pinned); the env-set marker's env.json shape (the helper is unit-tested; the live `/proc/<pid>/environ` write path is not executed here — no live launch).
- **Assumed** (no direct evidence this round): VERIFY-P5b's 40-mutant kills still hold on the current pins bytes (re-verified only by the joint suite + by-construction).

## Item 1 — F4 content validation for EVERY required artifact (AMENDMENT-2, version-aware)

**Verified.** `proofs/S0-01/pins.py` gained `_CONTENT_CONSTRAINTS` — a per-(version, name) table, 25 v2.2 rows / 26 v2.4 rows (with `tee-status.json`), built programmatically from `_CONTENT_BY_EXT` predicates + explicit rows; `content_constraint(version, name)` raises for an unknown version or a name `required_files(version)` does not carry (the closed-table guarantee). `build_capture_record.py` validates each PRESENT required file against its row BEFORE constructing `capture.json`, in BOTH build and `--check` paths. Message contract: `<name>: <reason>` named lines (e.g. `run-1: argv.txt is empty`), never a raw traceback.

Rows verified against the real corpus (golden `run-1`, 2026-09-08): `argv.txt text-nonempty`, `manifest-pre/post.done empty-marker` (0-byte), `buzz-acp.exit|pid int-exit-code`, `process-scan-*.txt utf8-text-maybe-empty` (the v2.2 shutdown leg's scan is legitimately 0-byte), `launch.ready|launch.exited text-nonempty` (28-byte UTC timestamps, empty INVALID). `backend-healthz-*.json json-object` (files ARE objects), `owned-pids.json json-object`, `tee-status.json json-object` (v2.4), `frames-*.jsonl/timeline.jsonl jsonl-nonempty`, `manifest-*.txt.gz gzip-text-nonempty`.

**Sweeps (both passed):** v2.2 — every required file emptied in a copy of real `run-1` → rc 1 with the exact named refusal, 25/25; untouched copy rc 0. v2.4 — synthetic leg with the v2.4 header, 26/26 named refusals including the version-smear refusal (`process-scan header missing but tee-status.json present: not a v2.2 leg`); untouched rc 0.

**Empty-ordering fix (real-corpus discrepancy):** the generic `size == 0` guard fired before the allowed-empty kinds → `run-1: cp-run1: process-scan-teardown.txt is empty` on the REAL corpus. `validate_artifact` now handles `empty-marker`/`utf8-text-maybe-empty` BEFORE the size guard. After the fix: run-1 build rc 0, `--check` rc 0, shutdown build rc 0.

**Hollow-green fix:** `corpus_version(d)` is wrapped in try/except ValueError in BOTH build and `--check` modes and returns rc 1 — a build-path constraint failure can never silently construct a record.

## Item 2 — strict process-scan header grammar

**Verified.** `_SCAN_HEADER_VERSION_RE` + `_SCAN_HEADER_FULL_RE` (v2.3 AND v2.4 full grammars) in `pins.py` mirror the checker's `_SCAN_HEADER_RE` (`proofs/S0-01/check_acp_conformance.py:158-161`). `corpus_version` is STRICT:
- a `#` line 1 must full-match the version's grammar (trailing fields → `process-scan header malformed`)
- a `#` line ANYWHERE in the body → `process-scan header malformed: a header line in the body` (refused, never v2.2)
- a headerless leg carrying a later-only required name (`tee-status.json`) → `process-scan header missing but tee-status.json present: not a v2.2 leg` (the AMENDMENT-2 smear refusal: a dropped v2.4 header must NOT mint as v2.2)
- unknown version → `process-scan header malformed: unknown version 'v9.9'` (named)
- `validate_artifact`'s `scan-headed` kind uses the version-specific full grammar (`_SCAN_HEADER_FULL_RE[version]`) + body-row shape + no second header

The pre-existing `refuses_to_default` negative controls (4 params) were updated to the new strict messages, and the old short-form v2.3/v2.4 test headers (which no producer writes — the real producers write the FULL grammar) were replaced with the real grammar. New strict-shape tests added (7): trailing fields, second header in body, CRLF, unknown version, body header after rows, empty scan, exact-corpus headers.

**Real corpus:** all four golden legs (`run-1`, `cancel`, `two-users`, `shutdown`) parse `v2.2` — the strict detector does not reject the legitimately-headerless v2.2 corpus.

## Item 3 — parser-idiom table as DATA

**Verified.** Named `_IDIOMS` table in `tests/test_s0_01_pc_tools.py` pinning each idiom's resolved-framedir-name count, MEASURED over the 7 producers by a scratch probe (not guessed): `_PY_JOIN 22`, `_PY_PATH 0` (declared dead — unit-tested only, no live site), `_PY_DIV 9`, `_PY_FSTR 4`, `_SH_FD 22`, `_SH_OUT_ASSIGN 6`. `test_each_declared_parser_idiom_resolves_exactly_its_pinned_count` asserts the exact equality — a refactor moving a name between idioms, or a producer adopting the dead `_PY_PATH` idiom, goes red. The pre-existing floor + orphan tests remain.

## Item 4 — S0-02-only pinned environment extension

**Verified (seam).** `proofs/S0-01/pins.py:71-77` already carried `PINNED_ENV_KEYS_S0_02 = PINNED_ENV_KEYS | {"RUST_LOG"}` + `PINNED_ENV_VALUES_S0_02 = {"RUST_LOG": "debug"}` (owner decision D-022, task #47 option a, task #52). THE LAUNCHER SEAM WAS MISSING — `pc_launch.py` had no `--env-set`. This round:
- `launch_env(..., env_set="s0-01")` — default `s0-01` byte-identical to today (test proves `set(env) == set(PINNED_ENV_KEYS)` and no `RUST_LOG`); `s0-02` adds exactly `{"RUST_LOG": "debug"}`; unknown set name refused BY NAME (`unknown env set 's0-03'`), never silently falling back; the closed-set check uses the SELECTED set.
- `main()` gains `--env-set {s0-01,s0-02}` (default `s0-01`).
- env.json names the set via new helper `env_json_with_set_marker(live_env, env_set)`: s0-01 writes NO marker (byte-identical), s0-02 writes `env_set: "s0-02"` (test asserts the shape + that the input is never mutated).
- The S0-02 runner is NOT touched; the one-line change it will make: `--env-set s0-02` on its three buzz-acp-decided legs.

**Tests:** default unchanged (byte-identical dict), extension differs by exactly `{"RUST_LOG": "debug"}`, unknown set refused by name, marker writes only for s0-02.

## Item 5 — P5b report STATUS stamp

**Verified.** One line added atop `tasks/briefs/s0-01-p5b-support/P5b-report.md`: `STATUS 2026-09-08: line references are 77f46a2-era and drifted in the 9c three-way merge of pins.py (VERIFY-P5b F1); the round-3 report supersedes them.` Historical report not rewritten.

## Item 7 — negative-control exactness

**Verified.** Every new negative control fails for the EXACT named line (`pytest.raises(..., match=...)`): `unknown env set 's0-03'`, `process-scan header malformed: ...`, `process-scan header missing but tee-status.json present: not a v2.2 leg`. No literal-only `if field == literal:` without a raising other arm. No presence-gated assertion. `os.environ` is never read below `main()` (resolved-once rule preserved).

## Item 8 — mutants (this round's set; see DEVIATIONS on the 40)

**Verified (this round's 6, all KILLED with killers pasted):**
- M-R1 argv.txt .txt rule loosened to `utf8-text-maybe-empty` → empty-argv negative control red
- M-R2 strict v2.4 header regex end-anchor removed → trailing-fields refusal red
- M-R3 `_IDIOMS` `_PY_PATH` count lied 0→3 → exact-equality test red
- M-R4 `launch_env` default `s0-01`→`s0-02` → byte-identical-default test red
- M-R5 `PINNED_ENV_VALUES_S0_02` `debug`→`info` → exactly-{RUST_LOG:debug} test red
- M-R6 env.json `env_set` marker dropped → marker test red
Killer lines: each test asserted the pinned behavior and went red under the mutation (6/6 KILLED, 0 hollow-green). Scratch `run_mutants_round3.py` pasted in report.

## Item 9 — 18-class self-sweep (enumeration)

**Verified for this lane's change.** Class 2 (every required artifact READ and VALIDATED): the constraint table IS the enumeration — `test_the_content_constraint_table_is_complete_and_pinned` asserts completeness for every `(version, name)` of every known version and pins the AMENDMENT-2 rows. Class 6 (env domains incl. the new set): the env-set tests enumerate s0-01 default vs s0-02 extension vs unknown.

## Item 10 — report discipline / gate

**Joint S0-01 set (venue exports, venv first on PATH, absolute basetemp, `-n 8`, ONE foreground run):**
`2524 passed, 22 skipped, 9 xfailed, 4 failed in 317.94s` — floor `1556 passed, 9 xfailed` met. The 4 failures are `tests/test_proof_status.py` (S0-11 owner-signing-key.asc absent), outside this lane's boundary, pre-existing/environmental, NOT pins consumers.

`lane_gate.sh` RESULT lines: see the gate section below (appended when the backgrounded gate completes).

## Item 10 — lane_gate.sh RESULT (the two runs, verbatim)

```
== identity (working-tree bytes copied over the archive) ==
41fa933d131ac24701100ba52b8959f3c7d2740b9be4336041388ab891bb83a4  proofs/S0-01/pins.py  629 lines
c9709755c60bfe994fe063bcc4e88cd38178ef3a8b4bd540bd596dc87e9e646c  proofs/S0-01/tools/build_capture_record.py  221 lines
1082e419b7af58476f71eb96e2decdc9cbfbfd0e44558e83d3493bdcfae8bdf0  proofs/S0-01/tools/pc/pc_launch.py  429 lines
0be8f3c5bb65a6a0845a54234e719c826a856bdac8f53e56141b9ad87860cb75  tests/conftest.py  72 lines
65e82d8fc069c0476b42c4a5fb1214a1ac23f5c430936924f280fa496d918823  tests/test_s0_01_pc_tools.py  1115 lines
9e939cf966db9223ffc1c2a5355c058772d073b12251a9e8b173ab858beb0ae2  tests/test_s0_01_pc_post_scan.py  451 lines
4ed529d4424f6ba35ada9f6fe3490d7d2477e47c64ef9ec86abb53ccb05794cb  tasks/briefs/s0-01-p5b-support/P5b-report.md  479 lines
== run 1/2: bash scripts/test_summary.sh tests/test_s0_01_pc_tools.py tests/test_s0_01_pc_post_scan.py  (load 3.51 5.07 4.37) ==
123 passed in 7.87s   (pytest-exit: 0)
== run 2/2: bash scripts/test_summary.sh tests/test_s0_01_pc_tools.py tests/test_s0_01_pc_post_scan.py  (load 3.40 4.97 4.35) ==
123 passed in 8.09s   (pytest-exit: 0)
RESULT: rev=3614dc994e5b files=7 deleted=0 runs=2 identical=yes rc=0 summary="123 passed in 7.87s 123 passed in 8.09s"
```

## APPENDIX — exact file:line references (from `grep -n` on the FINAL bytes)

- `proofs/S0-01/pins.py:289` `_SCAN_HEADER_FULL_RE` (v2.3 + v2.4 strict full grammars, mirroring `proofs/S0-01/check_acp_conformance.py:158` `_SCAN_HEADER_RE`)
- `proofs/S0-01/pins.py:326` `_CONTENT_BY_EXT` (predicate, kind) — first match wins
- `proofs/S0-01/pins.py:339` `_CONTENT_CONSTRAINTS` (the version-aware table)
- `proofs/S0-01/pins.py:395` `corpus_version` (strict detector)
- `proofs/S0-01/pins.py:450` `content_constraint` (the closed-table accessor)
- `proofs/S0-01/pins.py:464` `validate_artifact` (per-(version, name) content validation)
- `proofs/S0-01/pins.py:76` `PINNED_ENV_KEYS_S0_02`; `proofs/S0-01/pins.py:77` `PINNED_ENV_VALUES_S0_02`
- `proofs/S0-01/tools/build_capture_record.py:70` `version = pins.corpus_version(d)`; `:93` `pins.validate_artifact(d, _n, version)` (both build and `--check` paths)
- `proofs/S0-01/tools/pc/pc_launch.py:242` `launch_env(..., env_set="s0-01")`; `:289` `--env-set` argparse (default s0-01); `:349` `env_set=args.env_set`; `:196` `env_json_with_set_marker`; `:382` live use in `main()`
- `tests/test_s0_01_pc_tools.py:173` `test_the_content_constraint_table_is_complete_and_pinned`; `:378` `test_each_declared_parser_idiom_resolves_exactly_its_pinned_count`; `:1030` `test_the_s0_02_env_set_adds_exactly_the_pinned_rust_log`; `:1055` `test_an_unknown_env_set_name_is_refused_by_name`; `:1069` `test_env_json_names_the_set_that_launched_the_capture`
- `tests/test_s0_01_pc_post_scan.py:419` `test_corpus_version_refuses_a_header_in_the_body_after_rows`; `:425` `test_corpus_version_refuses_a_header_with_trailing_fields`; `:437` `test_corpus_version_refuses_an_unknown_header_version`

## SELF-ATTACK (the three most likely ways this change is wrong, and how each was ruled out)

1. **The version-smear refusal could over-reject a legitimate v2.2 leg.** A v2.2 corpus leg carrying a stray `tee-status.json` (e.g. a leftover from a previous v2.4 run) would now be refused by `corpus_version`. Ruled out: the golden corpus is the ground truth — all four real legs parse `v2.2` (verified), none carry `tee-status.json`; the refusal only fires when a later-only required name is PRESENT, which in the real v2.2 corpus never happens. The refusal is the AMENDMENT-2-mandated behavior (never mint a smeared leg), and it is scoped to files `PINNED_LEG_FILES_SINCE` marks as later-only.
2. **The constraint table may encode a kind that does not match some file in a leg I did not probe.** The v2.2 sweep (25/25) and the shutdown leg's build (rc 0) cover every required file in the real v2.2 corpus; the kinds were measured from the actual bytes (28-byte timestamps, JSON objects, empty markers). The v2.4 rows are exercised by the synthetic v2.4 sweep (26/26) whose scaffold was corrected to emit real corpus-shaped content (JSON objects, empty `.done` markers). The one inferred row is `tee-status.json = json-object` for v2.4 (the synthetic v2.4 scaffold writes it that way; the real v2.4 corpus does not exist yet — the sweep used a synthetic leg per AMENDMENT-2). Flagged: if B3's first real v2.4 capture writes a different `tee-status.json` shape, the row must be re-measured, never widened blindly.
3. **The env-set extension could break the S0-01 checker's `check_env` key-set equality.** The S0-01 checker (`check_acp_conformance.py:445-451`) demands env.json keys EXACTLY `PINNED_ENV_KEYS` (+allowlist). My default `s0-01` writes NO `env_set` marker and NO `RUST_LOG`, so S0-01 env.json is byte-identical to before — the checker's equality is preserved (the launch test proves the dict, and `env_json_with_set_marker(live, "s0-01") == live`). The `RUST_LOG`/`env_set` appear ONLY under `--env-set s0-02`, which the S0-01 runner never passes; the S0-02 runner (B3) validates its own legs. Ruled out by the byte-identical-default test + the marker-only-for-s0-02 test.

## Item 6 — F5 (checker adoption of pins predicates): NOT-DONE (A5l's), by design. This lane does not touch the checker.
