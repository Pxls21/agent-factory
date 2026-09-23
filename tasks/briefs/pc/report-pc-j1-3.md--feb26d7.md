PROPOSAL COMPLETE; sandbox-side adversarial verification is NOT done.

J1-3 report: scripts/decide-harvest
Task #120, PC continuation, code-implementer

STATUS

The real run produced 207 rows, but every question type is below KC-J7’s 200-label floor. Stop at the ledger.

Evidence tiers:
- VERIFIED: file bytes and modes, subprocess tests, mutation REDs, gate output, and pinned-corpus harvest output from this session.
- INFERRED: whether each refused corpus shape is legitimate prose outside the frozen grammar.
- ASSUMED: none.

1. PREMISE RE-MEASURE

    2026-09-23T16:26Z
    origin: 0e60603
    HEAD:   0e60603

The boundary was absent before this increment:

    scripts/decide-harvest: absent
    tests/test_decide_harvest.py: absent
    tests/fixtures/decisions/sources: absent

Decision package identities matched the premise:

    377ccd53da0c  24 lines   src/agent_factory/decisions/__init__.py
    607b65b613e2  78 lines   src/agent_factory/decisions/canonical.py
    bf04415d72c1  395 lines  src/agent_factory/decisions/volatile.py
    71fc398a5340  616 lines  src/agent_factory/decisions/ledger.py

No CONTRACT-INVALID stop.

2. DISCREPANCIES

D-1: Predecessor discrepancy resolved by AMENDMENT A1.

src/agent_factory/decisions/volatile.py:142-148 strips a --<7..40 hex> suffix only at the end of a value. The harvester therefore removes the leading report- and final .md, but does not parse or remove the PIN. J1-1 remains the only PIN normalizer.

Implementation: scripts/decide-harvest:331-340.

The two-PIN fixture proves:
- Both source paths normalize to the same state lane.
- The normalized lane contains no run of seven or more hexadecimal characters.
- The source_ref paths remain distinct.

Test: tests/test_decide_harvest.py:359-379.

The real corpus’s PC finding table lacks a declared title column and is refused before yielding a PC finding row. The real run therefore contains zero PC v1.finding_class rows. This does not weaken the fixture proof.

D-2: Relative LANE_GATE_DIR wrapper defect.

One lane-gate invocation returned rc 0 and a valid RESULT line but also printed:

    /tmp/lane_gate...: No such file or directory

The relative log path was resolved after the script changed directory. Two reruns with an absolute LANE_GATE_DIR produced clean RESULT lines. No project file was changed for this tooling defect.

D-3: Code-intelligence blind spots.

GitNexus’s clone index is 839 commits stale and cannot resolve the new untracked script. Its final detect_changes result reports one changed file but zero changed symbols.

Ripwire also cannot resolve scripts/decide-harvest as a symbol. Its independent exercises query maps 39 test symbols to 25 decision-package symbols.

Subprocess tests and the archived-PIN lane gates are the load-bearing evidence.

D-4: Final context-pack screen.

scripts/lane_context.sh reports AP-32 at scripts/decide-harvest:193. The flagged hashlib.sha256 call produces the source digest required by the ledger source-ref contract.

RUN classification: intentional cryptographic identity, not an insecure password hash or hardcoded digest.

The test-file screen has zero hits.

D-5: Bounded report lint.

Final result:

    report_lint: 60 refs — OK 11, NEAR 0, MISS 3, UNCHECKABLE 46, UNRESOLVED 0 (worktree)

The three MISS rows cite one source file at several exact refusal lines or a range whose first line shares no prose token with the report. The floor passes:

    OK 11 >= --min-refs 10

Stopped under the bounded rule.

3. IMPLEMENTATION AND STRICT GRAMMARS

Code locations:

- CLI, git-root validation, source admission, and output/source conflict guard:
  scripts/decide-harvest:65-196 and 760-849
- Closed source-kind table:
  scripts/decide-harvest:120-137
- Incident-registry grammar:
  scripts/decide-harvest:199-328
- Verify-finding grammar, A1 lane derivation, and path extraction:
  scripts/decide-harvest:331-480
- Lane-drift and bug-echo grammar:
  scripts/decide-harvest:483-579
- Transcript dispatch/result grammar:
  scripts/decide-harvest:582-738
- make_row and append ownership:
  scripts/decide-harvest:797-839

Every accepted record passes through make_row. Every ledger write passes through append.

Closed refusal reasons:

    bad-utf8
    unterminated-heading
    no-registry-row
    bad-title
    bad-table-row
    no-title-column
    bad-finding-id
    bad-class
    no-class-slug
    bad-rating
    bad-json
    bad-payload
    n-mismatch
    no-result
    unknown-role
    unknown-sev
    bad-kind
    state:<DecisionStateError reason>

Admission errors are exact and happen before writes:

    harvest-source-unknown          rc 5
    harvest-source-uncommitted      rc 4
    harvest-output-source-conflict  rc 4
    usage/root errors               rc 64

Malformed records emit harvest-source-unparseable, preserve valid records from the same source, and return rc 3.

4. FIXTURE AND RED-GREEN EVIDENCE

Hand-computed fixture: 10 rows.

    ap.violates_row=3
    b1.finding_kind=1
    b1.finding_sev=1
    b2.hit_role=1
    d1.bug_echo_scores=1
    v1.finding_class=2
    wf.drift=1

Other fixture counts:

    sources read:       4
    no-record sources:  0
    refusals:           0
    duplicates:         0

test_fixture_harvest_exact_rows_and_provenance asserts the exact stdout and one replayed provenance row per type at tests/test_decide_harvest.py:101-133.

The final suite covers:
- Exact fixture output and provenance.
- Re-landing identity.
- Duplicate reruns.
- Six required malformed records.
- Whole-source admission before any write.
- All seven question slots, including zero counts.
- Redaction through make_row.
- Committed HEAD bytes after an admission-time worktree swap.
- A1 two-PIN normalization.
- Canonical source-path suffixes.
- Transcript payload field types.
- Bug-economics blast vocabulary.
- Scout and reviewer n validation.
- Strict report suffix admission.
- Strict drift delimiters.
- Finding ID and class-table validation.
- Missing tool IDs.
- Output/source conflicts.
- append-only writing.
- Usage errors.
- Exact decision-state and unknown-source negative controls.

Final GREEN, same set 87e28761f102:

    33 passed in 8.32s
    33 passed in 8.77s

RED controls used scratch copies only:

- Dirty source:
  Removed the worktree/HEAD byte comparison.
  Expected rc 4/uncommitted; mutation reached record parsing.

- Committed source bytes:
  Re-read worktree bytes after admission.
  test_source_bytes_come_from_head_after_admission failed with probe rc 99 instead of 0.

- Reviewer count:
  Disabled reviewer n validation.
  Expected rc 3; mutation returned 0.

- A1 lane:
  Omitted removal of the final .md.
  State retained --1234abc.md.

- Strict drift:
  Accepted text after the bold anchor without the required delimiter.
  An unexpected wf.drift row appeared.

- Finding ID:
  Disabled the ID regex.
  Expected rc 3; mutation returned 0.

- Dispatch ID:
  Ignored a missing tool-use ID.
  no-result replaced the required bad-payload reason.

- Output conflict:
  Disabled the committed-output guard.
  Expected rc 4; mutation returned 3.

- Invalid disposition:
  Exact decision-state-bad-enum control fired.

- Unknown source:
  Exact rc 5 and exact stderr control fired.

5. MUTATION RESULTS

    m1  Suppress unparseable stderr
        Killer: malformed-record parameter set
        RED: exact stderr match failed

    m2  Admit without worktree/HEAD byte comparison
        Killer: admission test
        RED: rc/error mismatch

    m3  Add an undeclared question type to stdout
        Killer: exact fixture stdout test
        RED: stdout assertion failed

    m4  Remove duplicate stderr
        Killer: duplicate-rerun test
        RED: expected 10 duplicate lines, got 0

    m5  Replace admitted HEAD bytes with a later worktree read
        Killer: HEAD-after-admission test
        RED: probe rc 99 instead of 0

    m6  Disable reviewer n equality
        Killer: reviewer mismatch test
        RED: expected rc 3, got 0

    m7  Synthesize row_title="unknown"
        Killer: missing-registry malformed test
        RED: expected rc 3, got 0

    m8  Replace append with direct open().write()
        Killer: append-only AST test
        RED: expected one append call, got 0

    m9  Omit final .md removal
        Killer: A1 two-PIN test
        RED: lane retained the PIN suffix

Mutants killed: 9/9.

Hollow-green rate: 0/9 = 0%.

6. GATES

New suite:

    set: 87e28761f102
    33 passed in 8.32s
    33 passed in 8.77s

Seed AC 4 count:

    pytest-summary: 33 passed in 27.07s

Unchanged J1 suites:

    set: 70db5efe1e9b
    239 passed, 1 skipped in 21.71s
    pytest-summary: 239 passed, 1 skipped in 55.24s

Skip:

    tests/test_decisions_ledger.py:707
    test_short_write_real_tmpfs: not root, cannot mount tmpfs

Static and boundary checks:

    python -m pyflakes scripts/decide-harvest tests/test_decide_harvest.py
    rc 0, no output

    no_laya_in_gates: 40 files scanned, clean

    TEST_SCREEN over 2 paths: 0 hits over 2 files

    git diff --check
    rc 0, no output

Archived-PIN gate, two independent runs:

    RESULT: rev=feb26d7c930d files=8 deleted=0 runs=1 tests=87e28761f102 identical=yes rc=0 summary="33 passed in 31.52s"

    RESULT: rev=feb26d7c930d files=8 deleted=0 runs=1 tests=87e28761f102 identical=yes rc=0 summary="33 passed in 20.83s"

7. REAL RUN: KC-J7 MEASUREMENT

Private-clone SHA:

    feb26d7c930d059fbe5c364273163f571a63d31b

First run exit: 3.

Exact stdout:

    harvest: 207 rows, per question type: ap.violates_row=108, b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, d1.bug_echo_scores=0, v1.finding_class=97, wf.drift=2
    negatives: 0 (hand-labeled in J2)
    sources: 235 read (incident_log=1, lane_report=141, transcript_jsonl=0, verify_report=93), 224 with no records; refused: 39 records; skipped: 0 duplicates

The second fresh-output run returned the same rc 3, stdout, and 39 stderr lines.

    cmp ../scratch/j13/real.jsonl ../scratch/j13/real2.jsonl
    rc 0

The private clone was removed.

Every question type is below 200. KC-J7 stops at the ledger.

The committed corpus has:
- No transcript JSONL.
- No hive returns.
- No bug-echo rating table accepted by the grammar.

Exact refusal output:

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

Classification:

- bad-class, 3 records:
  Legitimate compound spellings such as FOLLOW-UP / UNVERIFIED and bold CONTRACT-DEFECT lie outside the frozen grammar. The grammar was intentionally not widened.

- bad-title, 9 records:
  These anchors insert parenthetical qualifiers between CLASS and the required separator. They are legitimate report prose but malformed under the frozen record grammar. The grammar was not widened.

- no-title-column, 27 records:
  Both tables place class in column two but have no header beginning with finding or equal to what. The frozen grammar correctly refuses each row.

Duplicate same-output control:

- First run: rc 3 because 39 malformed records remain.
- Second run: rc 3 for the same reason.
- Second stdout: harvest: 0 rows.
- Duplicate count: 207.
- Refusal count: 39.
- Ledger bytes remained unchanged.

8. FILE IDENTITY

    befe924d3656  scripts/decide-harvest
                  849 lines, mode 755

    ebee1158ce7f  tests/test_decide_harvest.py
                  581 lines

    8ad8a1734113  tests/fixtures/decisions/sources/docs/INCIDENT-LOG.md
                  18 lines

    d8229b8ef80d  tests/fixtures/decisions/sources/tasks/briefs/x/VERIFY-X-report.md
                  8 lines

    f006b55cca8c  tests/fixtures/decisions/sources/tasks/briefs/x/X-report.md
                  10 lines

    a185177a8006  tests/fixtures/decisions/sources/transcripts/x/t.jsonl
                  4 lines

    fea8a8f62686  tests/fixtures/decisions/sources/src/existing.py
                  2 lines

Only boundary files changed. src/agent_factory/decisions/* and gate files remain unchanged.

Current worktree status:

    AM tasks/briefs/laya/J1-3-report.md
    ?? scripts/decide-harvest
    ?? tests/fixtures/decisions/sources/
    ?? tests/test_decide_harvest.py

The staged report is the predecessor patch; its worktree version contains this completed report. No git-writing command was run.

The report draft is synchronized byte-for-byte at:

    /home/rocco/agent-factory/.lanes/pc-j1-3.md--feb26d7/report-draft.md

9. SELF-ATTACK

1. The harvester could read mutable worktree bytes after admission.

Ruled out by admission equality plus a controlled post-admission worktree swap. Harvested rows retain the original HEAD digest. Mutant m5 fails with rc 99.

2. Broad Markdown patterns could mint records from prose that merely resembles a record.

Ruled out by root-anchored source classification, exact anchors, closed IDs/classes/ratings, required headings and delimiters, and explicit real-run refusals rather than grammar widening.

3. A PC report PIN could leak into normalized decision state.

Ruled out by A1’s final .md removal before normalization. Two paths with different PINs yield the same state.lane and no seven-character hexadecimal run.

10. NOT DONE / KNOWN LIMITS

- NOT independently accepted. This build-lane output remains a proposal for the sandbox adversarial-verifier lane.
- NOT production-runnable or minted as data. The real JSONL remains scratch evidence and is not committed.
- b1.finding_kind.state.kind duplicates its answer. J1-1 follow-up only.
- v1.finding_class.state.disposition derives from its answer. J1-1 follow-up only.
- b2.hit_role.state.snippet remains empty unless the scout supplies note.
- Incident rows model the report action, action_kind=report and target docs/INCIDENT-LOG.md, rather than the hawk’s original triggering action.
- The pinned corpus has no transcript JSONL, so the real run cannot exercise hive returns. Fixture subprocess tests exercise the real script and decision pipeline.
- One existing ledger test skips because this non-root host cannot mount tmpfs. No sudo was requested.
- The private clone was removed.
- No harvester or pytest process was left running.

Reasoning record for coordinator commit:

Rejected widening the source grammars to increase label yield because strict refusal is the contract. Source admission completes before row construction. Committed HEAD blobs are captured once and parsed after admission. make_row followed by append is the only accepted write path.

Retro: no new general anti-pattern beyond the reported relative LANE_GATE_DIR discrepancy. Nothing to bake in this lane.
