# DSV2: the Laya/RWKV training set, version 2, labeled with the answers our own records hold (task #251; D-083)

Role: code-implementer (sandbox, Opus 5.5). PIN: 434b727 (the origin head at authoring). Report:
`tasks/briefs/jev-laya/DSV2-report.md` (write it incrementally from the start). Do NOT spawn subagents. Touch ONLY the
files in the boundary; report adjacent defects, never fix them.

## WHY

The first fine-tune of Laya trained on 1,788 rows labeled by the OpenJev teacher and was rejected on every KC-J3 check.
DATA-INT (`docs/research/findings/laya-ft-data/INTERNAL-LABELS-2026-09-25.md`, read sections 2 to 4 first) measured those
labels against the answers our own records already hold: they are worse than trivial baselines on every question type
(finding class 38/86 against the majority class's 49/86; blocking 72/86 against always-false's 83/86; anti-pattern top-1
17/49 against the lexical order's 26/49). D-083 (`docs/08_DECISION_LOG.md`) retires them: the next set takes its labels
from our recorded answers first. Our records hold 811 findings with the verifier's class that the current harvest does not
read (14 formats, section 3.2), 221 new anti-pattern rows at HEAD, and 457 commit messages that cite AF-AP ids.

## GOAL

A second dataset plus a labels file in the format `train.py` already reads, built deterministically from the committed tree
at one commit, with every label taken from an answer our process recorded, and its provenance kept per row.

## BOUNDARY

- MODIFY `scripts/decide-harvest` and `tests/test_decide_harvest.py`: admit the finding formats DATA-INT section 3.2 names
  (families F1 to F4, F6 to F8 and F11 to F14), each only where the line carries BOTH a finding id and one class word of the
  closed set (`BLOCKER`, `CONTRACT-DEFECT`, `FOLLOW-UP`, `INFO`, `KNOWN`, `UNVERIFIED`). Each family gets a test built from a
  REAL line of a committed report, cited by path and line (AF-AP-42: never an invented shape). Everything decide-harvest
  admits today stays byte-identical: its 369 rows at the PIN are a regression fixture (sha256/16 `c4589e0d77a97d9b`), and
  the only allowed change in them is new rows. Keep its refusal reasons for what stays ambiguous.
- MODIFY `scripts/laya_ft/build_dataset.py` and `tests/test_laya_ft.py`: a version-2 mode (a flag; the default stays
  version 1, and version 1's output stays byte-identical, `d7cd9b49...` at 0b342c7) that:
  - reads every finding decide-harvest admits, from `VERIFY-*-report.md` AND `tasks/briefs/pc/report-pc-verify-*.md`
    (DATA-INT X2), with the whole finding block as the state (define the block's end for the new families and test it);
  - reads the incident entries as version 1 does, and commit messages that cite AF-AP ids (scrubbed with
    `transcript_export.scrub`, the ids masked as `ap_probe` masks them), each against the registry's lexical top 16;
  - keeps J2's held-out samples out by source identity AND by text: no training state may contain a held-out finding's
    text or a held-out entry's text (define the overlap test, and prove it with a planted duplicate);
  - writes, per row, the label's provenance: `verifier-class`, `heading-cite`, `body-cite`, `commit-cite`, or
    `registry-commit` (a commit that adds the row itself).
- CREATE `scripts/laya_ft/recorded_labels.py` and its tests: writes a labels JSONL from the version-2 dataset in the exact
  record shape `scripts/laya_ft/teacher_label.py` writes and `common.join_labels` checks (`key`, `sent_state_sha` equal to
  the row's `state_sha`, `question_sha`, `options`, `target` a distribution over the row's options, `answer`); `model`
  `recorded`, `endpoint` the provenance. The target is one-hot on the recorded answer.
- CREATE the output record under `docs/research/findings/laya-ft-labels/2026-09-25-recorded/`: the dataset manifest, the
  labels file, and a summary (counts by source, question, class and provenance).
- READ: DATA-INT's report and its scratch scripts (`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/data-int/`,
  `goal2a.py` holds the family regexes it counted with; treat them as a starting point, not as proof), `scripts/laya_ft/common.py`,
  `scripts/laya_ft/teacher_label.py`, `docs/research/findings/ap-hawk-probe/ap_probe.py`,
  `docs/research/findings/j2-v1-probe/v1_probe.py`, `docs/research/findings/j2c-fulltext/j2c.py`.

## PINNED DECISIONS (a conflict with the tree is a STOP-and-report)

- **D-1 Labels are recorded answers, never inferred.** A finding's label is the class its report wrote; `v1.blocking` is
  that class in `{BLOCKER, CONTRACT-DEFECT}` (`v1_probe.py:33`); an anti-pattern row is positive when the entry or the
  commit cites it. A row with no recorded answer gets no label (a teacher may label it later; not here).
- **D-2 Evaluation does not move.** J2's samples, scorers and held-out rule stay as they are; the anti-pattern test counts
  HEADING citations (`ap_probe.py:80`). Training rows keep every provenance so a training run can select; report how often
  `heading-cite` and `body-cite` agree on entries that have both (DATA-INT X3).
- **D-3 No rebalancing in the builder.** Report the class mix per question (DATA-INT X4: the rare classes had 0 training
  rows in version 1); the training run decides the weighting.
- **D-4 Determinism.** One commit resolved once; the same commit, code and model give byte-identical output.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report on a mismatch.
2. Per family: admitted count; a precision read of 20 random admitted findings, each checked by a deterministic rule (the
   class word sits on the finding's own anchor line); and a recall check: class-word anchor lines in the reports that no
   family admits, counted and sampled.
3. The version-2 counts: rows by source, question, class and provenance; the held-out exclusions (by identity and by
   text); the heading/body agreement table.
4. Tests run twice: `bash scripts/test_summary.sh tests/test_decide_harvest.py tests/test_laya_ft.py` plus the
   `recorded_labels.py` tests, and `scripts/pc_suite.sh set-id -- <the files>`. The version-1 regression (dataset bytes)
   and the decide-harvest 369-row regression both pass.
5. A CPU smoke of the real training path: `/root/venv-laya-probe/bin/python scripts/laya_ft/train.py --dataset <v2 dir>
   --labels <recorded labels> --out <scratch> --mode head --device cpu --epochs 1 --batch-size 2 --limit 8` exits 0 and
   joins every one of the 8 rows (no stale label, no LabelError). If the CPU venv cannot run it, say why and do not fake it.
6. Mutants on scratch copies, each red on a named test: a family admitted without a class word; a held-out text let
   through; a target that is not one-hot on the recorded answer; version 1's output changed.
7. Gates: pyflakes on every file you write; `python3 scripts/no_laya_in_gates.py`; the separator check on every file you
   write.

## STANDING RULES

No outward-facing action (no push, PR or comment); no network; no PC bridge. Never commit, stash, checkout or reset in
`/home/user/agent-factory` (the coordinator commits). FAKE strings for anything secret-shaped. Long commands in ONE
foreground call. A pytest `--basetemp` parent must exist first.

## PREMISE — MEASURED at authoring (2026-09-25 01:2xZ, the sandbox at 434b727)

```
$ git rev-parse --short=12 HEAD; git rev-parse --short=12 origin/claude/soundbox-kit-migration-iz1jwf
434b727dfd2b
434b727dfd2b
$ python3 scripts/decide-harvest --out <scratch>/rows.jsonl   (its last stderr lines)
negatives: 0 (hand-labeled in J2)
sources: 298 read (incident_log=1, lane_report=165, transcript_jsonl=0, verify_report=132), 276 with no records; refused: 153 records; skipped: 0 duplicates
$ sha256sum <scratch>/rows.jsonl | cut -c1-16; count question_id
c4589e0d77a97d9b
Counter({'v1.finding_class': 213, 'ap.violates_row': 153, 'wf.drift': 3})
$ grep -n "REPORT_RX =" scripts/laya_ft/build_dataset.py
35:REPORT_RX = re.compile(r"/VERIFY-[^/]*-report\.md$")   # j2c.py's report set (and the brief's premise count)
$ /root/venv-laya-probe/bin/python -c "import torch, laya; print(...)"
torch 2.14.0+cpu laya 0.3.5
$ (DATA-INT, reproduced by the coordinator from decide-harvest's truth joined by path and finding id)
finding_class rows 86 (missing truth 0, ambiguous 0)
  OpenJev agrees 38 | majority class [('INFO', 49)] | truth classes {'FOLLOW-UP': 34, 'INFO': 49, 'BLOCKER': 3}
blocking rows 86 | OpenJev correct at 0.5 72 | always-false correct 83 | TP 1 FN 2 FP 12
```

Questions for you, not facts: whether every family's block end can be found without ambiguity; whether commit messages
that cite an AF-AP id in passing (not as the change's subject) should count as positives, and how you would tell them
apart deterministically. Report what you measure; the coordinator decides.

## AMENDMENT 1 (coordinator, 2026-09-25 01:4xZ, after the lane's STOP; D-085)

The STOP was correct (`DSV2-report.md` section 2). These rulings replace the brief where they conflict. Continue from
your premise run and surveys: the PIN is unchanged, so no new premise block is needed.

1. **The boundary grows by one file.** MODIFY `scripts/laya_ft/common.py` (its tests stay in `tests/test_laya_ft.py`).
   Two changes only: `row_identities` learns the kind `commit` with the identity `("commit", <full sha>)`, and any other
   unknown kind still raises (keep a test for it); `check_no_heldout` reads a kind with no held-out sample as an empty
   set. The version-1 dataset at 0b342c7 still loads through `load_dataset`, and every existing test passes unchanged.
2. **Commits: your option 1 with your split.**
   - Admit a commit when it adds a registry row (your rule: the ids on `+|` lines minus the ids on `-|` lines of its
     `docs/INCIDENT-LOG.md` diff; provenance `registry-commit`) or when an AF-AP id sits in its subject line (provenance
     `commit-subject`). A commit that meets both gets `registry-commit`.
   - Body-only citations are NOT admitted in version 2 (your read: 2 of 6 describe an instance). Count them in the
     summary as not admitted. A phrase rule with its own precision read is a later increment.
   - Held-out linkage: a commit whose diff adds an incident entry carries that entry as a second source,
     `{"kind": "incident", "heading": <the masked heading>, "role": "linked"}`, one per entry it adds. The builder leaves
     out a commit linked to a held-out entry; the loader's own gate is the backstop. Test both: a planted commit that adds
     a held-out entry (the gate refuses it) and a clean commit (it loads).
3. **ap negatives (amends D-1; D-085).** In a source that cites at least one registry row, each of its 16 candidates that
   it does not cite gets the recorded answer `false` with provenance `not-cited`. The reason: J2's ap test scores this
   same truth (the cited rows positive, the other candidates negative; `ap_probe.py:80`), so training and evaluation read
   one answer. Positives keep `heading-cite`, `body-cite`, `commit-subject` or `registry-commit`. The summary counts, per
   source kind, the sources whose cited rows all fall outside their top 16 (all 16 of their rows are `not-cited`). Report
   the class balance per question; do not rebalance (D-3).
4. **Class words: your second reading.** One class in the class slot. Two class words inside the slot (joined by `/` or
   `,`, or an alternative in parentheses such as `(UNVERIFIED, FOLLOW-UP)`) are refused as ambiguous. A qualifier after
   the class (`FOLLOW-UP (KNOWN class F-B4)`) or a class word later in the prose does not refuse the line; the label is
   the slot's class. Test one real line of each case.
5. **Block ends: a per-family rule you define and test.** The frame: a block ends at the next anchor line of any family
   (the admitted grammar included), at a markdown heading, or at a horizontal rule. List-item families (F7, F8, and any
   numbered or bulleted anchor) also end at a blank line followed by an unindented line that does not continue the item.
   A heading family (F6) ends at the next heading of the same or a higher level. Every block is capped at 60 lines; a
   capped block carries `"block_end": "cap"` in its source, and the summary counts them. Tests on real lines:
   `VERIFY-N5m-report.md:13` stops before the graft banner; `report-pc-verify-b4.md--95c0bb1.md:127` stops before
   `Retro:`; `VERIFY-J1-2-R1-report.md:82` keeps its whole body.
6. **F14 stays refused.** The 30 rows with no title cell stay out, and
   `test_class_table_without_a_title_column_refuses_each_row` stands unchanged. Count them in NOT-admitted.
7. **F13: your proposal.** Admit a table row only under a header with a finding or title column. Blocking-predicate and
   disposition tables stay out (their cells are the label's own evidence). Dedup by the first occurrence per (report,
   id), as version 1 does (AF-AP-199).
8. **Masking and leak counts (AF-AP-189's class).** Mask every version-2 finding state with `j2c._mask`, as version 1
   does. Measure and report, per source and provenance: finding states that still hold a class word of the closed set;
   finding states that state the blocking outcome in words (for example "non-blocking", "blocks the merge", "blocking
   predicate"); ap states that hold an unmasked AF-AP id or the positive candidate's registry name cell verbatim. Flag
   each such row in its source (`"leak": "<kind>"`) so a training run can select. Leave nothing out on this basis: the
   disposition is task #238's.
9. **Your two version-1 constraints are rules.** New families go beside the decide-harvest helpers that `j2c._blocks`
   calls, never by changing them. The byte clause is version 1's `dataset.jsonl` (`d7cd9b49...`); its `manifest.json`
   code hashes change by construction, and that is accepted.
10. **The build commit is the PIN** 434b727, for the regression fixture and the version-2 record (D-4).

Evidence demands 2 to 7 stand. Demand 4's set adds the `common.py` tests. Demand 5: report how many of the 8 rows joined a
label (an unlabeled row is skipped by `join_labels`; none may be stale). Demand 6 adds a mutant: a commit linked to a
held-out entry let through.
