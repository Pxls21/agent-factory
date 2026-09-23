# J1-3 report — `scripts/decide-harvest` (task #120, PC continuation, `code-implementer`)

STATUS: PROPOSAL COMPLETE; sandbox-side adversarial verification is NOT done. The real run produced 207 rows, but every question type is below KC-J7's 200-label floor. Stop at the ledger.

EVIDENCE TIERS: VERIFIED = file bytes/modes, subprocess tests, mutation reds, gate output, and pinned-corpus harvest output from this session. INFERRED = whether each refused corpus shape is legitimate prose outside the frozen grammar. ASSUMED = none.

## 1. Premise re-measure (step 1)

```
$ date -u +%Y-%m-%dT%H:%MZ; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf; git rev-parse --short HEAD
2026-09-23T16:26Z
0e60603
0e60603
$ ls scripts/decide-harvest tests/test_decide_harvest.py tests/fixtures/decisions/sources
ls: cannot access 'scripts/decide-harvest': No such file or directory
ls: cannot access 'tests/test_decide_harvest.py': No such file or directory
ls: cannot access 'tests/fixtures/decisions/sources': No such file or directory
$ (origin blob | worktree blob | lines | path)
377ccd53da0c 377ccd53da0c 24 src/agent_factory/decisions/__init__.py
607b65b613e2 607b65b613e2 78 src/agent_factory/decisions/canonical.py
bf04415d72c1 bf04415d72c1 395 src/agent_factory/decisions/volatile.py
71fc398a5340 71fc398a5340 616 src/agent_factory/decisions/ledger.py
```
File identities: MATCH the premise block (all four blob ids and line counts). No CONTRACT-INVALID stop.
Origin moved c6dcd61 -> 0e60603 (6 commits: B12, T94 brief, J1-3 brief, VERIFY-J1-0-R6 brief, two ledger-plane commits); the
decisions package is untouched by them. `docs/INCIDENT-LOG.md` changed (+3/-1) and `tasks/briefs/s0-02-support/B12-report.md` is new,
so the corpus counts at the real run can differ from the premise block by those files.

## DISCREPANCIES (found during the build; each reported, none fixed or self-accepted)

**D-1 — predecessor discrepancy, resolved by AMENDMENT A1.**
The predecessor correctly measured that `_strip_pin_suffix` (`src/agent_factory/decisions/volatile.py:142-148`) strips `--<7..40 hex>` only at the END of the value. AMENDMENT A1 changes the harvester input to the filename without `report-` and without the final `.md`; J1-1 remains the only PIN stripper. The implementation does that at `scripts/decide-harvest:331-340`. The two-pin fixture proves one normalized state lane and two distinct `source_ref.path` values (`tests/test_decide_harvest.py:359-379`). The real corpus's only PC finding table has no declared title column and is refused before it can yield a PC finding row, so the real run contains 0 PC `v1.finding_class` rows; this does not weaken the fixture proof.

**D-2 — one lane-gate invocation exposed a relative `LANE_GATE_DIR` wrapper defect.** The gate itself returned rc 0 and a RESULT line, but its wrapper also printed `/tmp/lane_gate...: No such file or directory` because the relative log path was resolved after the script changed directory. I reran with an absolute `LANE_GATE_DIR`; both final RESULT lines are clean. This is tooling only; no project file was changed.

**D-3 — code-intelligence blind spots.** GitNexus's clone index is 839 commits stale and cannot resolve this new untracked script; its post-edit `detect_changes` reports one changed file but zero changed symbols. Ripwire likewise cannot resolve `scripts/decide-harvest` as a symbol, while its independent `exercises tests/test_decide_harvest.py` maps 39 test symbols to 25 decision-package symbols. The subprocess suite and lane-gate results are the load-bearing evidence.

**D-4 — final context pack screen.** `scripts/lane_context.sh` reports AP-32 at `scripts/decide-harvest:193`, the `hashlib.sha256` digest required by the ledger `source_digest` contract. RUN classification: intentional cryptographic identity, not an insecure password hash or hardcoded digest. The test-file screen has 0 hits.

**D-5 — bounded report lint.** Final line after the report's verbatim stderr expansion: `report_lint: 60 refs — OK 11, NEAR 0, MISS 3, UNCHECKABLE 46, UNRESOLVED 0 (worktree)`. The three MISS rows cite one source file at several exact refusal lines or an exact range whose first line has no report prose token in common; the floor passes (`OK 11 >= --min-refs 10`). I stopped under the bounded rule.

## 2. Implementation and strict grammars

- CLI, git-root validation, admission, output/source conflict guard: `scripts/decide-harvest:65-196`, `scripts/decide-harvest:760-849`.
- Closed source-kind table: `scripts/decide-harvest:120-137`.
- Incident registry and entry grammar: `scripts/decide-harvest:199-328`.
- Verify finding grammar, A1 lane derivation, path extraction: `scripts/decide-harvest:331-480`.
- Lane drift and bug-echo grammar: `scripts/decide-harvest:483-579`.
- Transcript dispatch/result grammar: `scripts/decide-harvest:582-738`.
- Every accepted record passes through `make_row`; every write passes through `append`: `scripts/decide-harvest:797-839`.

Closed refusal reasons implemented: `bad-utf8`, `unterminated-heading`, `no-registry-row`, `bad-title`, `bad-table-row`, `no-title-column`, `bad-finding-id`, `bad-class`, `no-class-slug`, `bad-rating`, `bad-json`, `bad-payload`, `n-mismatch`, `no-result`, `unknown-role`, `unknown-sev`, `bad-kind`, and `state:<DecisionStateError reason>`.

Admission whole-run errors are exact and pre-write: `harvest-source-unknown` rc 5, `harvest-source-uncommitted` rc 4, `harvest-output-source-conflict` rc 4, and usage/root errors rc 64. Record refusals emit `harvest-source-unparseable` and preserve all other accepted rows before exit 3.

## 3. Fixture and RED -> GREEN evidence

Hand-computed fixture: 10 rows: `ap.violates_row=3`, `b1.finding_kind=1`, `b1.finding_sev=1`, `b2.hit_role=1`, `d1.bug_echo_scores=1`, `v1.finding_class=2`, `wf.drift=1`. Four sources, zero no-record sources, zero refusals, zero duplicates. The exact stdout and one replayed provenance row per type are asserted by `test_fixture_harvest_exact_rows_and_provenance` at `tests/test_decide_harvest.py:101-133`.

The final suite covers fixture output, re-landing identity, duplicate re-run, six required malformed records, all-source admission before write, all seven zero slots, redaction, committed HEAD bytes after an admission-time worktree swap, A1 two-PIN normalization, path suffixes, payload field types, blast vocabulary, both scout and reviewer `n`, suffix admission, strict drift delimiter, class-table IDs, missing tool IDs, output/source conflict, append-only writing, usage, and two exact negative controls (`tests/test_decide_harvest.py:101-581`).

RED evidence was produced against scratch copies; no production file was mutated:

| control | mutant | named test | observed RED |
|---|---|---|---|
| dirty source | remove worktree/HEAD byte comparison | `test_admission_untracked_modified_unknown_and_existing_out_untouched` | expected rc 4/uncommitted, got record parse path |
| committed bytes | reread worktree after admission | `test_source_bytes_come_from_head_after_admission` | probe rc 99 vs 0 |
| reviewer count | disable reviewer `n` check | `test_reviewer_n_mismatch_is_refused` | expected rc 3, got 0 |
| A1 lane | omit final `.md` removal | `test_pc_report_lane_pin_is_normalized_only_by_decision_state` | state retained `--1234abc.md` |
| strict drift | accept text after bold anchor without delimiter | `test_boundary_deviation_requires_the_declared_delimiter` | unexpected `wf.drift` row |
| table ID | disable ID regex | `test_class_table_rejects_invalid_finding_id` | expected rc 3, got 0 |
| dispatch ID | ignore missing tool-use id | `test_hive_anchor_with_missing_tool_id_is_refused` | `no-result` replaced exact `bad-payload` |
| output conflict | disable committed-output guard | `test_committed_output_path_is_refused_before_harvest` | expected rc 4, got 3 |
| exact negative | invalid disposition | `test_fixture_negative_control_rejects_mutated_state` | exact `decision-state-bad-enum` |
| exact negative | unknown source | `test_fixture_negative_control_exact_error_for_unknown_source` | exact rc 5 and exact stderr |

Final GREEN, twice, same set `87e28761f102`:
```
33 passed in 8.32s
33 passed in 8.77s
```

## 4. Mutant table (scratch copies only)

| mutant | diff line | killer | observed reason |
|---|---|---|---|
| m1 | replace unparseable stderr print with `pass` | malformed-record parameter set | exact stderr full-match failed (`None is not None`) |
| m2 | admit without comparing worktree bytes | admission test | rc/error mismatch |
| m3 | add an undeclared type to the printed type set | exact fixture stdout test | exit/stdout assertion failed |
| m4 | remove duplicate stderr print | duplicate re-run test | expected 10 duplicate lines, got 0 |
| m5 | replace admitted HEAD bytes with a later worktree read | HEAD-after-admission test | probe rc 99 vs 0 |
| m6 | disable reviewer `n` equality | reviewer mismatch test | expected rc 3, got 0 |
| m7 | synthesize `row_title="unknown"` | missing-registry malformed test | expected rc 3, got 0 |
| m8 | replace `append` with direct `open().write()` | append-only AST test | expected one `append` call, got 0 |
| m9 | omit final `.md` removal | A1 two-PIN test | lane retained PIN suffix |

All 9/9 mutants were killed. Hollow-green rate: 0/9 = 0%.

## 5. Gates

New suite, set `87e28761f102`, direct xdist runs:
```
33 passed in 8.32s
33 passed in 8.77s
```
The seed AC 4 command is the same test file; `scripts/test_summary.sh` pasted:
```
pytest-summary: 33 passed in 27.07s
```

Unchanged J1 suites, set `70db5efe1e9b`:
```
239 passed, 1 skipped in 21.71s
pytest-summary: 239 passed, 1 skipped in 55.24s
SKIPPED [1] tests/test_decisions_ledger.py:707: `pytest.skip`("test_short_write_real_tmpfs: not root, cannot mount tmpfs")
```

Static and boundary screens:
```
python -m pyflakes scripts/decide-harvest tests/test_decide_harvest.py  # rc 0, no output
no_laya_in_gates: 40 files scanned, clean
--- TEST_SCREEN over 2 path(s): 0 hits over 2 files ---
```

Archived PIN gate, two independent one-run invocations, same bytes and count:
```
RESULT: rev=feb26d7c930d files=8 deleted=0 runs=1 tests=87e28761f102 identical=yes rc=0 summary="33 passed in 31.52s"
RESULT: rev=feb26d7c930d files=8 deleted=0 runs=1 tests=87e28761f102 identical=yes rc=0 summary="33 passed in 20.83s"
```

## 6. Real run: KC-J7 measurement

Private clone SHA:
```
feb26d7c930d059fbe5c364273163f571a63d31b
```
First run exit 3; exact stdout:
```
harvest: 207 rows, per question type: ap.violates_row=108, b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, d1.bug_echo_scores=0, v1.finding_class=97, wf.drift=2
negatives: 0 (hand-labeled in J2)
sources: 235 read (incident_log=1, lane_report=141, transcript_jsonl=0, verify_report=93), 224 with no records; refused: 39 records; skipped: 0 duplicates
```
Second fresh-output run returned the same exit 3, stdout, and 39 stderr lines. `cmp ../scratch/j13/real.jsonl ../scratch/j13/real2.jsonl` returned 0. The private clone was removed.

Every type is below 200. KC-J7 therefore stops at the ledger. The committed corpus has no transcript JSONL, no hive returns, and no bug-echo rating table accepted by the grammar.

Refusals, all 39 stderr lines, verbatim:

```
harvest-source-unparseable: tasks/briefs/continuity/VERIFY-AF-AP-127-R1-REPIN-a-R2-report.md:725 (bad-class)
harvest-source-unparseable: tasks/briefs/continuity/VERIFY-AF-AP-127-R1-REPIN-a-R2-report.md:743 (bad-class)
harvest-source-unparseable: tasks/briefs/hermes-repin/VERIFY-REPIN-a-R1-report.md:550 (bad-class)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R4-report.md:749 (bad-title)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R4-report.md:751 (bad-title)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R4-report.md:760 (bad-title)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R4-report.md:762 (bad-title)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R4-report.md:764 (bad-title)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R4-report.md:765 (bad-title)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R5-report.md:466 (bad-title)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R5-report.md:505 (bad-title)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R5-report.md:525 (bad-title)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:209 (no-title-column)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:210 (no-title-column)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:211 (no-title-column)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:212 (no-title-column)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:213 (no-title-column)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:214 (no-title-column)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:215 (no-title-column)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:216 (no-title-column)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:217 (no-title-column)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:218 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:428 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:429 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:430 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:431 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:432 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:433 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:434 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:435 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:436 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:437 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:438 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:439 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:440 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:441 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:442 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:443 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:444 (no-title-column)
```

Classification:
- `bad-class` (3): `tasks/briefs/continuity/VERIFY-AF-AP-127-R1-REPIN-a-R2-report.md:725`, `:743`; `tasks/briefs/hermes-repin/VERIFY-REPIN-a-R1-report.md:550`. These are legitimate compound class spellings (`FOLLOW-UP / UNVERIFIED`, bold `CONTRACT-DEFECT`) outside the frozen grammar. The grammar is intentionally narrower; it was not widened.
- `bad-title` (9): `tasks/briefs/laya/VERIFY-J1-0-R4-report.md:749`, `:751`, `:760`, `:762`, `:764`, `:765`; `tasks/briefs/laya/VERIFY-J1-0-R5-report.md:466`, `:505`, `:525`. These anchors use parenthetical qualifiers between CLASS and the required ` — ` separator. They are legitimate report prose but malformed for the frozen record grammar. The grammar was not widened.
- `no-title-column` (27): `tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:209-218` (10); `tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:428-444` (17). Both tables have class as column two but no header starting with `finding` or equal to `what`; each row is correctly refused under the frozen grammar.

Duplicate same-output control: first and second runs both exited 3 because the 39 malformed records remain; the second run printed `harvest: 0 rows`, `skipped: 207 duplicates`, 207 duplicate stderr lines plus the 39 refusal lines, and left the ledger bytes unchanged by test and implementation contract.

## 7. File identity

```
befe924d3656  scripts/decide-harvest  849 lines  mode 755
ebee1158ce7f  tests/test_decide_harvest.py  581 lines
8ad8a1734113  tests/fixtures/decisions/sources/docs/INCIDENT-LOG.md  18 lines
d8229b8ef80d  tests/fixtures/decisions/sources/tasks/briefs/x/VERIFY-X-report.md  8 lines
f006b55cca8c  tests/fixtures/decisions/sources/tasks/briefs/x/X-report.md  10 lines
a185177a8006  tests/fixtures/decisions/sources/transcripts/x/t.jsonl  4 lines
fea8a8f62686  tests/fixtures/decisions/sources/src/existing.py  2 lines
```
Only boundary files changed. `src/agent_factory/decisions/*` and gate files remain unchanged.

## 8. Self-attack

1. The harvester could accidentally read mutable worktree bytes. Ruled out by admission equality plus the controlled post-admission swap: rows retain the original HEAD digest; m5 fails with rc 99.
2. The broad markdown patterns could mint rows from prose that only resembles a record. Ruled out by root-anchored kind classification, exact anchors, closed IDs/classes/ratings, exact headings/delimiters, and the real-run refusals rather than silent widening.
3. A PC report PIN could leak into normalized state. Ruled out by A1's pre-normalization final `.md` removal and two source paths at different PINs producing the same `state.lane` with no 7+ hex run.

## 9. Known limits / NOT done

- NOT independently accepted. This build-lane output is a proposal for the sandbox adversarial-verifier lane.
- NOT production-runnable or minted as data. The real JSONL stays in scratch and is not committed.
- `b1.finding_kind.state.kind` duplicates its answer; `v1.finding_class.state.disposition` derives from its answer. J1-1 follow-up only.
- `b2.hit_role.state.snippet` is empty unless the scout supplies `note`.
- Incident rows model the report action (`action_kind=report`, target `docs/INCIDENT-LOG.md`), not the hawk's original triggering action.
- No transcript JSONL exists in the pinned committed corpus, so the real run cannot exercise hive returns; fixture subprocess tests exercise the real script and real decision pipeline instead.
- One existing J1 ledger test skips because this non-root host cannot mount tmpfs. No sudo was requested.
- No process was left running; the private clone was removed. Git status contains only the staged predecessor report plus the untracked boundary files for coordinator harvest.

Reasoning record for coordinator commit: rejected widening source grammars to increase label yield because strict refusal is the contract; admission completes for every source before rows; HEAD blobs are captured once and parsed after admission; `make_row` then `append` is the only accepted write path. Retro: no new general anti-pattern beyond the already reported relative `LANE_GATE_DIR` discrepancy; nothing to bake in this lane.
