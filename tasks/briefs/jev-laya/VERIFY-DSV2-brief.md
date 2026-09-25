# VERIFY-DSV2: attack dataset v2 and its recorded-label record (task #251; orchestration 0f; D-031's one repair)

Role: adversarial-verifier (sandbox, Opus 5.5). PIN: see the premise block. Report: `tasks/briefs/jev-laya/VERIFY-DSV2-report.md`
(write it incrementally from the start). Do NOT spawn subagents. Report EVERY meaningful observation with no severity filter,
then apply the blocking predicate (contract-mapped; reproduced through the real production path; materially effective; a
concrete discriminator; in-boundary) and end with a GATE RECOMMENDATION: MERGE-READY, MERGE-READY-WITH-FOLLOWUPS, NOT-READY or
CONTRACT-INVALID. The coordinator owns the final gate.

## WHY

The builder's own gate is not verification (orchestration 0f). This dataset is the first training set of the System 1 models
(D-083, D-086): Laya and the RWKV student will learn from it, and J2 will measure them. The expensive wrong greens:
1. a J2 held-out row, or its text, inside training: every later evaluation would read too high;
2. an answer written into its own state (a label leak): the model learns the leak;
3. a wrong recorded label: a class misread from a report line, or a `not-cited` row that its source does cite;
4. the shared loader change (`scripts/laya_ft/common.py`; GitNexus rates `check_no_heldout` CRITICAL: 11 upstream symbols,
   among them `train.py` `run`, `teacher_label.py` `main` and `recorded_labels.py` `main`) letting a held-out row through, or
   refusing a valid dataset.

## CONTRACT (frozen)

`tasks/briefs/jev-laya/DSV2-brief.md` with its AMENDMENT 1; D-083 and D-085 in `docs/08_DECISION_LOG.md`. The builder's report is
`tasks/briefs/jev-laya/DSV2-report.md` (sections 7 to 12). It lists 12 deviations: judge each against the contract.

## VENUE (load-bearing)

Work ONLY in a clean detached worktree at the PIN, never in `/home/user/agent-factory`: two other lanes edit files there, and
the SESSION-EXPORT lane's in-progress change to `scripts/transcript_export.py` breaks the record's manifest test by design (the
manifest hashes that file). Create it with `git -C /home/user/agent-factory worktree add --detach <your scratch>/wt <PIN>` (the
only git write you make) and remove it with `git -C /home/user/agent-factory worktree remove --force <your scratch>/wt` at the end.
Mutants go on copies inside your worktree only. Your scratch:
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-dsv2/` (the disk has about 2.5 GB free; keep
under 500 MB, the worktree included).

## ATTACK SURFACES (new shapes; never only the builder's own cases)

1. **Held-out leakage, by identity and by text.** Build new shapes and see whether the builder or the loader's gate catches each:
   a held-out finding restated under another report path or finding id, with small edits (whitespace, one word, the class
   changed); a held-out incident entry's text inside a commit subject or body; a commit that EDITS (does not add) a held-out
   entry; a held-out heading whose text changed after the sample's commit. Measure what the text-overlap rule matches (an exact
   substring, or a normalized one).
2. **Label leaks.** The builder flagged ap-id 126, row-name 33, blocking-words 35 (per question) and class-word 1. Are the flags
   complete? Look for other forms in the states: an AF-AP id range, a lower-case id, `AP-12`, a class word in another case or a
   plural. Count what is unflagged.
3. **Label correctness.** Sample findings from every family and check each recorded class against the report's own line. Check
   that no `not-cited` row is cited by its source (heading, body, commit subject, commit body, or a registry row the commit
   adds). Check that `v1.blocking` is true exactly when the class is `BLOCKER` or `CONTRACT-DEFECT`.
4. **The loader.** Version-1 datasets still load; an unknown source kind still raises; a sampled kind that carries a held-out
   identity is refused. Can any row pass `check_no_heldout` with a held-out identity through the `commit` kind or a variant of
   the linked source (a missing `role`, a heading masked differently)? Read every caller GitNexus lists.
5. **The recorded labels.** One-hot on the recorded answer; `key` and `sent_state_sha` match the rebuilt dataset; `join_labels`
   accepts them; an unlabeled row stays unlabeled; two builds give the same bytes.
6. **Regressions.** decide-harvest's 369 rows at 434b727 (sha256/16 `c4589e0d77a97d9b`) and version 1's dataset bytes
   (`d7cd9b49...` at 0b342c7); the old refusal reasons unchanged for old inputs.
7. **The record.** Rebuild version 2 at the build commit 434b727 with the PIN's code, and compare it byte for byte with the
   committed record (`docs/research/findings/laya-ft-labels/2026-09-25-recorded/`).

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; STOP and report CONTRACT-INVALID on a mismatch that matters.
2. Every finding with file:line, the command and its output, and the blocking predicate applied item by item.
3. A mutation table of NEW mutants (each red or surviving, with the test that catches it or the gap it shows).
4. The test files at the PIN run twice in your worktree with `bash scripts/test_summary.sh tests/test_decide_harvest.py
   tests/test_laya_ft.py tests/test_recorded_labels.py` (paste both summaries; the set id with `scripts/pc_suite.sh set-id --`).
5. NOT-done.

## STANDING RULES

No network; no PC bridge; no outward-facing action. No git writes except your own worktree's add and remove. FAKE strings for
anything secret-shaped. Long commands in ONE foreground call; a pytest `--basetemp` parent must exist first. Check your report
with `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` (0 expected).

## PREMISE — MEASURED at authoring

PIN: the origin head that carries this brief and the DSV2 commit (named in the dispatch). Measured 2026-09-25 03:2xZ in the
sandbox; the coordinator's gate ran in a clean worktree at e6bab18 plus the lane's files only (no other lane's edits).

```
$ sha256sum <file> | cut -c1-16    (the lane's files, as committed)
2912b3799639aee6  scripts/decide-harvest
a7ad1838fce325db  scripts/laya_ft/common.py
f71590b4be1c7108  scripts/laya_ft/build_dataset.py
fc7b222ce71596ab  scripts/laya_ft/recorded_labels.py
a6f3e11486a25b04  tests/test_decide_harvest.py
8e52b288ea722a0e  tests/test_laya_ft.py
6a2cfa6b866d9c37  tests/test_recorded_labels.py
efd3c91306cc967b  docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
0098e52e0dbfc01d  docs/research/findings/laya-ft-labels/2026-09-25-recorded/labels.jsonl
4fdd169cc9a05ec6  docs/research/findings/laya-ft-labels/2026-09-25-recorded/summary.json
$ bash scripts/test_summary.sh tests/test_decide_harvest.py tests/test_laya_ft.py tests/test_recorded_labels.py   (the worktree)
pytest-summary: 143 passed in 427.96s (0:07:07)
$ bash scripts/pc_suite.sh set-id -- tests/test_decide_harvest.py tests/test_laya_ft.py tests/test_recorded_labels.py
3 files set=5d6a3ce56265
$ node .gitnexus/run.cjs impact check_no_heldout --direction upstream --repo .   (selected fields)
"impactedCount": 11, "risk": "CRITICAL", "direct": 3; processes: teacher_label.py main, recorded_labels.py main,
train.py run, build_dataset.py build_v2, build_dataset.py build
$ git show HEAD:tests/test_decide_harvest.py | LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'
7
```

The 7 separator bytes in `tests/test_decide_harvest.py` sit on lines 777-862, which predate the lane (they are the same at
e6bab18); they are not a finding. Questions for you, not facts: does the builder's text-overlap rule match a finding restated
with small edits; are the leak flags complete.
