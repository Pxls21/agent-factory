# VERIFY-DSV2 report: dataset v2 and its recorded-label record (task #251; orchestration 0f; D-031's one repair)

Role: adversarial-verifier (sandbox, Opus 5.5). Brief: `tasks/briefs/jev-laya/VERIFY-DSV2-brief.md`. PIN: da2ba1b (origin head
of `claude/soundbox-kit-migration-iz1jwf`; it carries the DSV2 commit 71e540f and the brief). STATUS: COMPLETE 2026-09-25 04:2xZ (started
03:27Z; resumed 03:49Z after a container restart). GATE RECOMMENDATION: NOT-READY on V-6 (section 7).

Venue: a clean detached worktree at the PIN,
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-dsv2/wt` (`$W` below; `$V` = its parent,
the scratch). Mutants run on copies inside `$W` only. No network, no bridge, no git write except the worktree add/remove.

## 1. Premise (evidence demand 1)

Measured 2026-09-25 03:27Z in `$W` (HEAD `da2ba1b220605e3ae9108736c3ff5e6ba244a854`, equal to the fetched origin head).

| Premise line | Brief | Measured | Match |
|---|---|---|---|
| `scripts/decide-harvest` | `2912b3799639aee6` | `2912b3799639aee6` | yes |
| `scripts/laya_ft/common.py` | `a7ad1838fce325db` | `a7ad1838fce325db` | yes |
| `scripts/laya_ft/build_dataset.py` | `f71590b4be1c7108` | `f71590b4be1c7108` | yes |
| `scripts/laya_ft/recorded_labels.py` | `fc7b222ce71596ab` | `fc7b222ce71596ab` | yes |
| `tests/test_decide_harvest.py` | `a6f3e11486a25b04` | `a6f3e11486a25b04` | yes |
| `tests/test_laya_ft.py` | `8e52b288ea722a0e` | `8e52b288ea722a0e` | yes |
| `tests/test_recorded_labels.py` | `6a2cfa6b866d9c37` | `6a2cfa6b866d9c37` | yes |
| record `dataset-manifest.json` | `efd3c91306cc967b` | `efd3c91306cc967b` | yes |
| record `labels.jsonl` | `0098e52e0dbfc01d` | `0098e52e0dbfc01d` | yes |
| record `summary.json` | `4fdd169cc9a05ec6` | `4fdd169cc9a05ec6` | yes |
| set id | `3 files set=5d6a3ce56265` | `3 files set=5d6a3ce56265` | yes |
| separator bytes in `tests/test_decide_harvest.py` at HEAD / at e6bab18 | 7 (pre-existing) | 7 / 7 | yes |

The premise holds (the test run and the GitNexus impact line are re-measured in later sections).

## 2. Findings (inventory; no severity filter)

Resumed 03:49Z after a container restart at about 03:4xZ: the worktree (clean, da2ba1b), the scratch (`$V/v2/` rebuild,
`$V/labels.jsonl`, `$V/probes/*.py`, both test-run logs) survived; nothing was re-run whose result was already on disk.
Every probe below reads the PIN's code in `$W` and the sources at the build commit 434b727 through `git show`; the probe
scripts are in `$V/probes/` (rc 0 each). "Reproduced" = run by me in this session; "static" = read only.

**V-1 INFO: the record rebuilds byte for byte (attack 7). Reproduced.**
`HF_HUB_OFFLINE=1 /root/venv-laya-probe/bin/python scripts/laya_ft/build_dataset.py --version 2 --commit 434b727 --out $V/v2`
rc 0, 46.5 s: `dataset.jsonl` `f1b92d6fa79c2f145052fec9f301f1e719987ae5f7d14e19f663eb67426b5c48` (12,795,031 B, the builder's
number), `manifest.json` `cmp`-identical to the record's `dataset-manifest.json` (`efd3c913...`). Then
`python3 scripts/laya_ft/recorded_labels.py --dataset $V/v2 --out $V/labels.jsonl --summary $V/labels-summary.json`
rc 0 (`"conflicts": 0, "labeled": 5301, "rows": 6196, "unlabeled": {"ap.violates_row|commit": 15, "ap.violates_row|incident": 880}`):
`labels.jsonl` and `summary.json` `cmp`-identical to the record (`0098e52e...`, `4fdd169c...`). A second labels run gives
identical labels; its summary differs only in `"file": "labels2.jsonl"` (the output name I chose; `scripts/laya_ft/recorded_labels.py:100`
writes `out.name`). Mechanism: the manifest hashes the code of `$W` (the PIN), so the record pins the DSV2 code.

**V-2 INFO: held-out identity and commit linkage are complete at the build commit (attack 1). Reproduced with parsers
independent of the builder's.**
- The 100 AP headings: all 100 found at 434b727 (`linkage.py`).
- Commits that ADD a held-out entry: an independent parse (every `+` anchor line of `git log -p -U0 -- docs/INCIDENT-LOG.md`,
  its first 70 masked characters at `difflib` ratio >= 0.8 against every held-out heading; `linkage3.py`) finds 105 commits;
  every commit the builder links is among them (`builder-linked commits not found here: 0`). The 6 pairs it did not link are
  look-alikes of OTHER entries, read one by one: d83ff6eabb adds `2026-09-15 11:4xZ — VERIFY-CK14 home (the cloud verify
  route, ...` (not the held-out `16:0xZ — VERIFY-QM0 home ...`), 838c1882d0 adds CK15 and QM1-b, 7537910a54 adds `12:2xZ — lane
  QM1`, 5b3edb81bb and 5447ce520a add cycle 7 and cycle 6 (each linked to its own heading).
- Older versions of a held-out heading: no heading any commit ever added is near (ratio >= 0.6) but unequal to a held-out
  heading (`linkage2.py`: 0). Held-out headings by number of linking commits: `[(1, 93), (2, 6), (6, 1)]`.
- Commits that EDIT a held-out entry (not the anchor line): `git log -L <start>,<end>:docs/INCIDENT-LOG.md 434b727` over each
  of the 100 entries' lines (`edits.py`, 98 s) finds 106 commits; 2 are not linked (d9c440ecec, 98572ac3f5, body-line edits),
  and neither reaches v2 (`admitted_rows=0` each). The contract holds out adding commits only (D-085 (3)); at the build
  commit no editing commit is admitted either.

**V-3 FOLLOW-UP: the text-overlap rule is an exact substring after one normal form; a one-word edit inside a held-out title,
or an AP heading restated without its timestamp, evades it. At the build commit it misses nothing: no training state shares
more than 9% of any held-out text's word 5-grams. Reproduced.**
The rule (`scripts/laya_ft/build_dataset.py:152-170`, `overlap_norm` and `Overlap.hit`): class words and AF-AP ids masked,
scrubbed, lower case, whitespace collapsed, then `t in s`; held-out texts under 40 normalized characters are not used (4:
`declared r4-4 limits, measured:`, `mutation test gaps`, `three new mutants survive (test gaps).`, `undeclared python load
spellings.`; each appears in 0 training states, measured). Positive control (`neardup.py` logic): a J2c held-out state that is a
table row's title cell, with one word changed, has a 5-gram share of 0.762 and `overlap_norm(h) in overlap_norm(planted)` is `False`. Measurement: 300
held-out texts (100 J2c blocks, 100 J2 v1 titles, 100 AP headings) against the 1,316 distinct training texts of the rebuilt
v2 (finding states and ap queries), both directions (the held-out text's share inside the state, and the state's share
inside the held-out text): the highest score is 0.09 (an AP heading against an unrelated commit subject), and only 15 pairs
share any 5-gram at all. So small-edit restatements do not exist in this corpus today.
New shapes against the production rule (`Overlap` built by `heldout_texts` from the committed samples; each shape derived
from a real held-out text): EXCLUDED are a whole block under another path, the block re-wrapped, with its class word
changed, with its bold markers removed, with its finding id changed, its first line alone, the AP heading inside a commit
subject with the ids unmasked, the AP heading lower-cased inside a body; a one-word edit outside the title is also
excluded, because the J2 v1 title is a held-out text of its own and still sits inside the block. They PASS in two shapes,
measured over every held-out text: a one-word edit inside the title portion (96 of the 96 blocks that contain their title
pass), and an AP heading restated without its log timestamp (100 of 100 pass: the held-out text begins `2026-09-24 12:4xZ
— ...`, and a commit subject that restates an incident rarely carries that stamp). At the build commit neither shape occurs
(the 5-gram measurement above, and the adding commits are held out by identity, V-2). The rule is the one the builder
defined (the brief lets it define the overlap test), proven with planted duplicates; a later, larger set (D-086's session
streams) should add a fuzzy rule. Suggested fix: test the AP heading without its stamp as well, and add a word-5-gram share
test (for example >= 0.5 in either direction) beside the containment test, counting its hits.

**V-4 FOLLOW-UP: one `not-cited` label whose source does cite the row, in the shorthand `AF-AP-90/91`. Reproduced.**
Commit b69522e1fe (`bridge: register AF-AP-92 ...`) adds AF-AP-92 (`registry-commit`, true) and says in its body
`not an edit-snapshot AP_SCREEN code-hunk row (like AF-AP-90/91)`. The builder's id rule, `\bAF-AP-(\d+)\b`
(`AP_ID` at `docs/research/findings/ap-hawk-probe/ap_probe.py:30`, used as `C.AP.AP_ID.findall(msg)` at `scripts/laya_ft/build_dataset.py:363` and `:368`), reads AF-AP-90 (a body-only
citation: no label, builder rule 7) but not 91, so the candidate AF-AP-91 gets `false` / `not-cited`
(item `ap-419a51ffa4edffee5e28`). By the contract's own words (AMENDMENT 1 item 3, "each of its 16 candidates that it does
not cite") the provenance is false; by the builder's rule 7 the row should be unlabeled, like AF-AP-90. Scale
(`shorthand.py`): 18 distinct shorthand strings in admitted sources (`AF-AP-1..4`, `AF-AP-10..15`, `AF-AP-24/25/26`, ...);
every other shorthand-only id is a `registry-commit` positive of the same commit (3b5e3a2f0e: 98, 99) or outside the
source's top 16. So 1 of 3,423 `not-cited` labels. The same id rule is J2's own truth (`ap_probe.py:80`), which is D-085's
reason for this label, so training and evaluation still read one answer. Suggested fix: expand `AF-AP-a/b`, `a..b` and
`a, b` before the id rule in both the builder and a later J2 revision, or count such rows as unlabeled.

**V-5 INFO: every ap label recomputes identically from the raw sources. Reproduced.** `aplabels.py` re-derives all 4,544 ap
labels with its own parser (the registry from `^\|\s*AF-AP-(\d+)\s*\|` at 434b727; entries from the anchor to the next
blank line, anchor or heading, the heading between the first two `**`; commits from `git log --format=%H%x00%B%x01`; registry
adds as `+|` ids minus `-|` ids of `git log -p -U0`): `ap rows checked: 4544 | disagreements: 0`, merged sources included.
So `heading-cite`, `body-cite`, `registry-commit`, `commit-subject` and `not-cited` follow the stated rules exactly, and no
`not-cited` row is cited by its heading, body, commit subject, commit body (`AF-AP-n` form) or a row the commit adds. No
incident entry continues past the builder's entry end before the next anchor (`entry_tail.py`: 0), so no citation hides
there.

**V-6 BLOCKER (the predicate is applied in section 5): the leak flags miss the blocking predicate stated in words. 93
finding states per v1 question carry a predicate walk and no flag (61 of them state a predicate result outright); 89 of
the 93 are new-family findings. Reproduced.**
AMENDMENT 1 item 8 asks the builder to measure and flag "finding states that state the blocking outcome in words (for
example "non-blocking", "blocks the merge", "blocking predicate")". The builder's rule (`scripts/laya_ft/build_dataset.py:145-147`,
`blocking-words`) flags 35 rows per question. `blockwords.py` on the rebuilt v2 (826 `v1.blocking` rows, base rate
`{'false': 749, 'true': 77}`):

| Form in the state (masked, as the model reads it) | Rows | Unflagged | Answers of the unflagged |
|---|---|---|---|
| predicate walk: `contract mapping`, `canonical:`, `material:`, `discriminator:`, `task ownership`, `in-boundary:` | 114 | 93 | false 58, true 35 |
| `blocks` / `blocked` (a verb, any object) | 34 | 32 | false 28, true 4 |
| `not a [CLASS]` / `is a [CLASS]` / `as a [CLASS]` | 29 | 12 | false 8, true 4 |
| `defence-in-depth` / `optional hardening` / `hypothetical` | 14 | 12 | false 11, true 1 |
| `no material effect` / `not material` | 7 | 6 | false 6 |
| `hollow green` | 6 | 5 | false 3, true 2 |
| `No [CLASS]` (a report summary line) | 1 | 1 | false 1 |
| any of the forms above, or `does not block` (any object), `must fix` | 143 unflagged in all | | false 105, true 38 |

The predicate walk is the verifier's own evaluation of the blocking predicate, in the finding's block:
`Canonical: yes. Material: yes.` (`tasks/briefs/laya/VERIFY-J1-0-R23-STAMP-report.md@434b727:477`, F-B1, a BLOCKER),
`Predicate: not contract-mapped` (`tasks/briefs/laya/VERIFY-J1-2-report.md@434b727:218`, F8, FOLLOW-UP),
`Contract mapping: none (the frozen contract B:31-58 does not require ...)` (F8 item 1 on `parse_classes`, FOLLOW-UP, anchored at `tasks/briefs/kit-k1-support/VERIFY-K1-h-report.md@434b727:181`), `- Contract mapping: none in frozen B8 criteria` (`tasks/briefs/s0-02-support/VERIFY-B8-report.md@434b727:48`,
F-02, INFO), `Not material: a 1-chunk batch is a per-chunk call` (`tasks/briefs/jev-laya/VERIFY-JT1-report.md@434b727:128`,
F-7, INFO). A seeded read of 12 of the 93 (`random.Random(7)`) found the predicate's evaluation in every one. A stricter
count, only an explicit result (`not contract-mapped`, `contract mapping: none|yes|no`, `canonical: yes|no|n/a`,
`material: yes|no|none`, `not material`, `no material effect`, `Predicate:`), still leaves 61 rows per question unflagged
(false 46, true 15; 59 of them new-family findings), against the 36 rows per question the builder flags in total. 35 of
the 93 unflagged rows are `true` (38%, against the 9.3% base rate). By family: grammar 4, new families 89 (F3 28, F8 26, F2 13, F6 12, F7 5,
F4 2, F1 2, F11 1). The amendment's item 7 keeps predicate TABLES out because "their cells are the label's own evidence";
the same evidence in a paragraph is kept (correct: item 8 says leave nothing out) but not flagged, so the summary's
`blocking-words 35` understates what a training run must select against by a factor of about 3.6 (at least 128 rows).
Suggested fix: add the predicate-walk forms (and `does not/doesn't block`, `not material`) to `blocking-words`, rebuild the
record, and state the rule's vocabulary in the summary.

**V-7 INFO: other unflagged label forms, measured (attack 2).**
- Class words (the closed set, any case, with a suffix): 2 rows per v1 question, both flagged (`class-word` covers plurals
  and case). `FOLLOW UP` with a space: 3 rows per question, 2 unflagged (not in the closed set's spelling).
- AF-AP ids in ap states: 126 rows hold `AF-AP-\d` in the CHUNK (the candidate row's own registry text), all flagged
  `ap-id`, none in the query (the builder's claim holds). Lower-case forms (`af-ap-`) and forms with a non-ASCII hyphen or a space between `AF`, `AP` and the number: 0 rows.
  The mask's remainder in a shorthand, `AF-AP-?/17` (from `AF-AP-16/17`), `AF-AP-?..15`: 191 query rows, 180 unflagged; the
  number is not linked to any candidate (the chunk holds no id of its own: `docs/research/findings/ap-hawk-probe/ap_probe.py:51` keeps `cells[1:3]`), so it is no
  label; the one real effect is V-4. Bare `AP-24`, `AP-1/AP-3`, `AP-32`, `AP-43`: 64 query rows (8 contexts, 4 sources), all
  the SOURCE repo's inherited registry (`(AP-24) straight from the source repo`), not this registry's ids.
- Row names: `row-name` flags 33 rows (a positive row's name, >= 12 normalized characters, verbatim in the query). Partial
  names and paraphrases are not measured by any rule; not counted here.

**V-8 INFO: finding labels match their report lines (attack 3). Reproduced.**
- `fclass.py`: 838 finding sources (grammar 112: the builder's 212 first occurrences minus the 100 held out; F1 66, F2 143, F3 250, F4 52,
  F6 84, F7 22, F8 77, F11 7, F12 1, F13 24). `v1.blocking` is `true` exactly for BLOCKER and CONTRACT-DEFECT: 0 mismatches in
  838. An independent locator (the first line with the id in its first 60 characters, then the first closed-set word after
  it) disagrees 13 times; I read all 13: each is my locator's artifact (a summary line such as
  `tasks/briefs/laya/VERIFY-J1-3-R2-report.md@434b727:8` `GATE RECOMMENDATION: NOT-READY (blockers F-01, ...; CONTRACT-DEFECT F-05 ...)`, a
  mutation-table row quoting a fixture `- **F-13 BLOCKER — minted from mid-line**` at `:172`, a section heading `## 4. ...`),
  and the admitted anchor carries the recorded class in its slot (for example the F-13 FOLLOW-UP anchor on `bad-utf8` at
  `tasks/briefs/laya/VERIFY-J1-3-R2-report.md@434b727:532`). 18 ids my locator cannot place (F8 `1. FOLLOW-UP F1 —`, F11 `- **INFO-2 (R1).**`): read, each
  right.
- A seeded read (`random.Random(4242)`, 3 per family, 30 lines, printed with the anchor text): 30 of 30 carry the recorded
  class in the slot, for example `tasks/briefs/s0-05-support/VERIFY-S0-05-report.md@434b727:332` `F-2 (FOLLOW-UP, SOLID)`,
  `tasks/briefs/pc/report-pc-verify-gov2e.md--949aa85.md@434b727:188` `INFO/DISCREPANCY` (DISCREPANCY is not a class word, so not
  ambiguous), `tasks/briefs/pc-t90-support/VERIFY-T94-report.md@434b727:77` `UNVERIFIED`.
- Reclassification shapes in the 726 admitted family anchors (an arrow or `to` between class words, a struck-through class,
  `downgraded`/`reclassified`): 0 (`was`/`now` occur 13 times, all prose).
- One restated id takes a new class by design: `tasks/briefs/jev-laya/VERIFY-JT2-R1-report.md@434b727:574` `F-20 INFO (R)`, while the brief it
  verifies names F-20 a BLOCKER (line 36). The label is the class this report wrote for its own re-check of F-20 (D-1).

**V-9 FOLLOW-UP: some family blocks run past their finding (block ends, AMENDMENT 1 item 5). Reproduced.**
Of the 726 admitted family blocks (F13 excluded), 11 hold, after their anchor, another line in anchor position with a class
word; 7 of these carry a different class than the block's label. Read:
- A tight list: `tasks/briefs/jev-laya/VERIFY-JT2-R1-report.md@434b727:807` (`- **R2-e INFO (R).**`) ends at line 810 and takes the
  sibling item `- Unchanged, FOLLOW-UP to the issue as the coordinator states: F-06, F-12, F-18, F-21 ...` (lines 809-810): the
  list-item end rule fires only after a blank line (`lines[later - 1]` at `scripts/decide-harvest:515-519`), and this list has none.
- A bold-paragraph finding followed by a plain list: F-13 (FOLLOW-UP, `a torn timeline line crashes the checker`,
  `tasks/briefs/s0-02-support/VERIFY-B9-report.md@434b727:463`) runs 23 lines to the next heading and takes the whole `INFO (no action
  required by B9):` list (I-1 to I-11); F3 is not a list family, so no list rule applies.
- A report summary inside the last finding: `tasks/briefs/ci/VERIFY-CI-GATE-R1-report.md@434b727:767` (VR-19, INFO) takes line 770
  `CONTRACT-DEFECT: none returned. ...`; `tasks/briefs/ci/VERIFY-CI-GATE-report.md@434b727:595` (F23, UNVERIFIED) takes line 597.
Each follows the amendment's frame as written (a plain sibling item, a list title and a summary line are not anchors). The
effect is a few states that hold another finding's text under this finding's label. Blocks over 20 lines: 23 (printed by an
in-session probe, not saved); most are long BLOCKER bodies. Suggested fix: end a list-item block at an unindented
sibling item even without a blank line, and a bold-paragraph block at a `<CLASS> ...:` list title.

**V-10 INFO: no grammar block (version 1's cut, kept in version 2) contains an admitted family anchor (0 of all grammar
bullet blocks at 434b727).** So no family finding's text sits inside a held-out J2c state or another grammar state.

**V-11 INFO: the loader (attack 4). Reproduced through the real `C.load_dataset` (`loader.py`, one-row datasets).**

| Row | Result |
|---|---|
| a commit source alone | loaded |
| a commit + a linked held-out heading (`role` linked / missing / `primary`) | `HeldOutLeak` each |
| a commit + a linked held-out heading with one trailing space | loaded |
| a commit + a linked held-out heading masked `AF-AP-#` instead of `AF-AP-?` | loaded |
| a v2 `verify_finding` with a held-out `path#id` | `HeldOutLeak` |
| the same finding id under a PC report path | loaded |
| an `incident` source with a held-out heading | `HeldOutLeak` |
| kind `tweet` / `Commit` / missing | `DatasetError: ... unknown source kind 'tweet'` / `'Commit'` / `None` |
| a commit source without its sha / with a list sha | `KeyError: 'commit'` / `TypeError: unhashable type: 'list'` |
| no sources | `DatasetError: ... no source identity` |
| a v1 state equal to a held-out J2c text, with a commit source | `HeldOutLeak ... the text of a held-out J2c` |

The loader is an exact-identity backstop, as designed (D-085 (3)): a linked heading written with another mask or another
spacing, or a restated finding under another path, passes it, and only the builder's own rules stop those. The builder
writes the mask J2 wrote (`MASK_ID = "AF-AP-?"`, `scripts/laya_ft/build_dataset.py:42`; `ap_probe.py:82`) and linked all 100 headings
(V-2), so no such row exists at the build commit. The two exceptions that are not `DatasetError` reach `train.py`'s
handler (`C.DatasetError` and its siblings at `scripts/laya_ft/train.py:377`) as a traceback and rc 1, not a refusal and rc 64; the same holds before DSV2 for a
`verify_finding` without `path` or an `incident` without `heading` (`scripts/laya_ft/common.py:183`, `:185`), so it is not a regression.
Callers (GitNexus `impact check_no_heldout --direction upstream`, run 03:4xZ: `impactedCount 11, risk CRITICAL`): `build`,
`build_v2`, `load_dataset` (depth 1); `build_dataset.py main`, `recorded_labels.py main`, `teacher_label.py main`,
`train.py run` (depth 2); the three module entry points and `train.py main` (depth 3). Read: none of them reads `sources`
beyond the loader (`C.load_dataset(args.dataset)` at `scripts/laya_ft/train.py:252`, `scripts/laya_ft/teacher_label.py:204`, `scripts/laya_ft/recorded_labels.py:81`); `evaluate.py` reads no `sources`.
`train.py`, `teacher_label.py`, `evaluate.py`, `j2c.py`, `v1_probe.py`, `ap_probe.py` and `transcript_export.py` are
unchanged between 434b727 and the PIN (`git diff --stat`, empty).

**V-12 INFO: the J1-0-R6 PC report is a summary, not a twin.** One PC report shares a held-out report's lane,
`tasks/briefs/pc/report-pc-verify-j1-0-r6.md--c6dcd61.md`; it holds the lane's closing summary and no finding text of the
held-out `VERIFY-J1-0-R6-report.md#F-4`. The only byte-identical pair of the two sets is O2 (no held-out finding).

**V-13 INFO: the regressions hold (attack 6). Reproduced.**
- decide-harvest at 434b727, in process (`regress.py`: the test's own replica, which the PIN script pins to the CLI by its
  sha): the PIN script gives `369 c4589e0d77a97d9b` with refusals `no-title-column 78, bad-title 66, bad-finding-id 6,
  bad-class 3`; the PIN's script gives `1113 4d139bab00d0991c` (the builder's CLI number) with `no-title-column 78,
  ambiguous-class 6, bad-finding-id 6, bad-class 3`. The old rows are an ordered subsequence, byte for byte (`True`). Old
  refusals whose outcome changed: `bad-title -> admitted` 66 and nothing else; new refusals on lines the PIN script did not
  refuse: `ambiguous-class` 6. So every old input keeps its old refusal reason unless a family admits it.
- Version 1 at 0b342c7 through the real builder CLI with the PIN's code: rc 0, 9.5 s,
  `d7cd9b49abac267bb9b5290641ea353180a9a61047ce6c590809520b085cea1c`, 1,788 rows (ap 1,616, v1 86 + 86); it loads through
  `load_dataset` at the PIN (1,788 rows). Its manifest differs from the committed `2026-09-24-openjev/dataset-manifest.json` in
  `code` (decide-harvest, build_dataset.py, common.py; accepted by AMENDMENT 1 item 9), `commit` (that manifest was built at
  eb256f49 with the same bytes) and `sources.repeated_finding_ids` (added by f1679db, before DSV2). None of it is DSV2's.

**V-14 INFO: the recorded labels (attack 5). Reproduced.** `records.py` over the rebuilt v2 and labels (both identical to the
record): 6,196 rows, 5,301 records (`torn 0, duplicates 0`), 0 problems. Every target is one-hot on the one answer its
non-linked sources record; `key`, `item_id`, `question_id`, `sent_state_sha`, `question_sha` and `options` equal the row's;
`model` is `recorded`; `endpoint` is the union of the sources' provenances; the answer shape (`choice` + `probabilities`, or
`noul`) reads back; `ts` is the manifest's `commit_time` 1790299156. The 895 rows with no recorded answer have no record.
`join_labels` joins all 5,301 with no stale label. Endpoints: verifier-class 1,652, not-cited 3,423, registry-commit 88,
body-cite 64, commit-subject 62, heading-cite+body-cite 8, heading-cite 4 (the builder's table).

**V-15 INFO: D-2's agreement table recomputes; one summary count is off by one against the amendment's own words.** My parse
(`agree.py`): 110 kept entries, 6 cite in both heading and body: 4 the same set, 1 heading inside body, 1 other (the
manifest's numbers). Sources whose 16 rows are all `not-cited`: incident 6 (the manifest's 6); commit 51 against the
manifest's 52. The extra one is 03baf648e1: 15 `not-cited` rows and 1 unlabeled body-cite row (AF-AP-188). The builder
counts a commit whose LABELED cited rows all fall outside the 16 (`commits_all_cited_outside_16`, `scripts/laya_ft/build_dataset.py:385`); the amendment's
parenthesis reads "(all 16 of their rows are not-cited)". One source, a summary count.

**V-16 FOLLOW-UP: five rules are pinned only by the record's bytes, and the record test cannot tell a semantic change from
any other code change.** Section 3: M8 (the outside-16 negatives, AMENDMENT 1 item 3), M12 (a horizontal rule ends a block,
item 5), M14 (a verdict line ends a list item), M19 (`v1.blocking` includes CONTRACT-DEFECT, D-1) and M21 (an edited registry
row is not an addition, the builder's own 197-versus-143 trap) each pass every unit test and change the production dataset
and labels at 434b727. `test_version_2_record_rebuilds_byte_identically_at_the_pin` compares the whole manifest first,
`code` hashes included (`RECORD / "dataset-manifest.json"` at `tests/test_laya_ft.py:1335`), so it is red for ANY byte change to a CODE file, an equivalent
mutant or a comment edit alike; and the builder's adjacent risk 1 prescribes regenerating the record after such a change,
after which a semantic regression would pass every test. The data itself is right today (V-5, V-8). Suggested fix: unit
fixtures for a CONTRACT-DEFECT finding, a commit that edits a registry row, a source whose cited rows all fall outside the
16 (a fixture registry of more than 16 rows), and a horizontal rule and a verdict line after a family anchor.

**V-17 FOLLOW-UP: the F6 heading-level rule is untested and unexercised.** M13 (F6 ends at any heading) passes every test and
leaves the production output unchanged: no F6 anchor at 434b727 has a deeper heading after it (0 of 84), and the pinned case
`J1-2-R1-82` has none inside lines 82-127, although the comment at `tests/test_decide_harvest.py:1336` says `F6: a deeper heading or an indented list does not end it`. The indented-list half is exercised; the deeper-heading half is a claim no line
tests. Suggested fix: a real F6 block with a deeper heading inside, or drop the words.

**V-18 INFO: equivalent or redundant parts at 434b727 (mutants that change nothing).** M4 (the 10 context lines of the
linkage diff), M6 (build_v2's second text net: a state only shrinks after the first net, so the second cannot fire), M9 (the
answer condition of the row-name flag), M10 (the `\bblocking predicate\b` alternative is dead: `j2c._mask` turns `blocking`
into `[CLASS]` before the flag rule reads the state, and `\[CLASS\] predicate` covers it), M27 (the scrub inside
`overlap_norm`). None is a defect; M4 and M27 guard shapes the build commit does not hold.

**V-19 INFO: an id-prefix tell, outside the kinds item 8 names.** Ids whose letter names the class sit on the anchor line in
the state: `I1`, `I-4`, `VE3R1-I2` and the like (9 rows, all INFO), `CD1` (1 row, CONTRACT-DEFECT). Ids that hold the class
word itself (`INFO-2`) are masked to `[CLASS]-2`. `B`-prefixed ids are mixed (BLOCKER 11 of 26; `F-B` in J1-0-R23 is a round
prefix). 10 rows.

**V-20 INFO: hostile report text through the production parser, in process (`_grammar_records`, `_family_findings`,
`v2_findings`).** A 200,000-character id run with and without a digit, 200,000 stars or spaces inside an anchor, 20,000
one-line anchors, 2,000 anchors with 70-line bodies, a 20,000-row F13 table, a header on the last line, CR-only line ends,
and U+2028 inside an anchor (built with `chr(0x2028)`): each returns in under 0.35 s, with no hang and no exception. Two
harmless oddities: a numbered item with a 200,000-digit number is admitted as F8 with that number as its id; CR-only text
is one line (git's line model, AF-AP-132), so a second anchor after a bare CR sits inside the first block.

**V-21 INFO: venue.** The 4-core box ran at load 4.3-7.5 during test run 1 (another lane's four `session_export.py`
processes). A container restart at about 03:4xZ stopped me after both test runs had finished; nothing on disk was lost.

### 2b. The builder's twelve deviations (`DSV2-report.md` section 12), judged against the contract

| # | Deviation | Judgment |
|---|---|---|
| 1 | `_grammar_records` moved out of `_finding_candidates` | Accepted. Not one of the helpers `j2c._blocks` calls (item 9); the AST test pins those, and the 369 rows keep their bytes and order (V-13). |
| 2 | 18 new `ap.violates_row` rows from family titles | Accepted. The grammar already emits them for its own titles; "the only allowed change is new rows" (the brief); pinned by the fixture test's `18`. |
| 3 | new refusal `ambiguous-class`; the `restated` state | Accepted. Item 4 requires the refusal; item 7 requires the first occurrence. |
| 4 | commit provenance per row | Accepted as a reading. Item 2's "a commit that meets both gets registry-commit" is ambiguous for a row cited only in the subject of a registry-adding commit; per row keeps each provenance true. The coordinator may rule. |
| 5 | body-only cited rows of an admitted commit get no label | Accepted (items 2 and 3 leave the case open); V-4 is the one row where a shorthand escapes it. |
| 6 | every registry-adding commit is admitted | Accepted: item 2's letter. |
| 7 | `pc_suite.sh set-id` run | Accepted: a local function, no bridge (I ran it too). |
| 8 | no `dataset.jsonl` in the record | Accepted: the brief's record list names three files; the dataset rebuilds byte for byte (V-1). |
| 9 | the record's `summary.json` is `recorded_labels.py`'s summary | Accepted: it holds the counts the brief asks for. |
| 10 | the `class-word` rule reads plurals | Accepted: stricter than the mask. |
| 11 | F13 states are the title cell only | Accepted: item 7's reason (the other cells are the label's own evidence) and version 1's rule for table rows. |
| 12 | GitNexus rates the `common.py` symbols HIGH | Measured CRITICAL for `check_no_heldout` (11 upstream); the change is the two the amendment names; M1, M2, M3 and M23 are red on the unit tests (section 3); V-11. |

## 3. Mutation table (new mutants)

New mutants only (the builder's a-e, c2, d2 are not repeated). `probes/mutate.py` applies each to one file in `$W` after
checking its anchor is unique, runs the unit sets (`tests/test_laya_ft.py` without the eight Laya-venue tests, plus
`tests/test_recorded_labels.py`: 39 tests; `tests/test_decide_harvest.py`: 90 tests; control, no mutant: `39 passed, 14
deselected in 7.77s` and `90 passed in 23.33s`), restores the file from a pristine copy and re-checks its sha. A mutant that
survives the unit sets is run through the production build at 434b727 (`build_dataset.py --version 2` + `recorded_labels.py`)
and compared with the record by the dataset sha, the labels bytes and the builder summary; the manifest's `code` block is
left out of that compare because it changes under any mutant (V-16). After the audit: `git status --short` 0 lines, and the
four files hash to the premise values.

| Id | Mutant | File | Unit sets | Production output at 434b727 | Caught by |
|---|---|---|---|---|---|
| M1 | `check_no_heldout` reads every kind with `.get` | common.py | red | not run | `test_check_no_heldout_reads_a_kind_no_sample_holds_as_empty` |
| M2 | `row_identities` skips `role: linked` sources | common.py | red | not run | `test_row_identities_know_a_commit_and_still_refuse_an_unknown_kind`, `test_check_no_heldout_...`, `test_a_commit_that_adds_a_heldout_entry_...` |
| M3 | `row_identities` passes an unknown kind | common.py | red | not run | `test_row_identities_know_a_commit_and_still_refuse_an_unknown_kind` |
| M23 | `SAMPLED_KINDS` holds `commit` | common.py | red | not run | `test_check_no_heldout_...`, `test_a_commit_that_adds_...`, four `test_recorded_labels.py` tests |
| M5 | a body-only cited row of an admitted commit becomes `not-cited` | build_dataset.py | red | not run | `test_collect_v2_labels_every_source_with_its_recorded_answer` |
| M26 | a subject citation overrides `registry-commit` | build_dataset.py | red | not run | `test_collect_v2_labels_...` |
| M11 | the slot's `,` joiner dropped | decide-harvest | red | not run | `test_pin_rows_are_the_regression_fixture_and_the_families_only_add_rows` |
| M24 | an F13 row that restates an id is admitted | decide-harvest | red | not run | `test_f13_admits_...`, `test_pin_rows_...` |
| M15 | a conflicting row takes one of its answers | recorded_labels.py | red | not run | `test_a_record_has_the_teacher_records_keys_in_order` and three more |
| M18 | `ts` is the wall clock | recorded_labels.py | red | not run | `test_the_same_dataset_gives_the_same_bytes` |
| M8 | negatives only when a cited row is among the 16 | build_dataset.py | SURVIVES | dataset `61083f6dc471`; labels and summary differ | only the record bytes (V-16) |
| M12 | a horizontal rule does not end a family block | decide-harvest | SURVIVES | dataset `92486ad4b7e3`; labels differ | only the record bytes (V-16) |
| M14 | a verdict line does not end a list item | decide-harvest | SURVIVES | dataset `628ccde4e325`; labels and summary differ | only the record bytes (V-16) |
| M19 | `v1.blocking` true only for BLOCKER | build_dataset.py | SURVIVES | dataset `d8e9329f386e`; labels and summary differ | only the record bytes (V-16) |
| M21 | an edited registry row counts as added | build_dataset.py | SURVIVES | dataset `46960a7b9dac`; counts, held-out, sources, labels and summary differ | only the record bytes (V-16) |
| M13 | F6 ends at any heading | decide-harvest | SURVIVES | identical | nothing: the rule is never exercised (V-17) |
| M4 | commit linkage diff with `-U0` | build_dataset.py | SURVIVES | identical | nothing: equivalent at 434b727 (V-18) |
| M6 | build_v2's second text net off | build_dataset.py | SURVIVES | identical | nothing: redundant (V-18) |
| M9 | the row-name flag without its answer condition | build_dataset.py | SURVIVES | identical | nothing: equivalent at 434b727 (V-18) |
| M10 | `blocking-words` without `blocking predicate` | build_dataset.py | SURVIVES | identical | nothing: a dead alternative (V-18) |
| M27 | `overlap_norm` without the scrub | build_dataset.py | SURVIVES | identical | nothing: equivalent at 434b727 (V-18) |

## 4. Test runs (evidence demand 4)

In `$W` at the PIN, `bash scripts/test_summary.sh tests/test_decide_harvest.py tests/test_laya_ft.py
tests/test_recorded_labels.py`, twice in ONE harness-managed call (started 03:30:26Z; the harness re-invoked me on exit).
Deviation, stated: I did not run it as a plain foreground call, because the 4-core box stood at load 4.3-7.5 from another
lane's four `session_export.py` processes and a foreground call is capped at 600 s; run 1 took 601.11 s, which a foreground
call would have cut.

```
RUN1 start 2026-09-25T03:30:26Z head da2ba1b22060
RUN1 rc 0 end 2026-09-25T03:40:28Z
pytest-summary: 143 passed in 601.11s (0:10:01)
RUN2 start 2026-09-25T03:40:28Z
RUN2 rc 0 end 2026-09-25T03:45:59Z
pytest-summary: 143 passed in 331.12s (0:05:31)
$ bash scripts/pc_suite.sh set-id -- tests/test_decide_harvest.py tests/test_laya_ft.py tests/test_recorded_labels.py
3 files set=5d6a3ce56265
```

`git -C $W status --short` after both runs: 0 lines. The two sandbox-venue byte tests ran in both runs (143 passed, 0
skipped: the Laya venv and model are present).

## 5. Blocking predicate, per finding

INFO findings (V-1, V-2, V-5, V-7, V-8, V-10 to V-15, V-18 to V-21) report verified behaviour or harmless oddities; none
contradicts a frozen criterion with a material effect, so the predicate stops at its first or third condition for each.

**V-6 (leak flags miss the predicate walk): all five conditions hold. BLOCKER.**
1. Contract mapping: AMENDMENT 1 item 8, frozen at 01:4xZ before the build: "Measure and report ... finding states that
   state the blocking outcome in words (for example "non-blocking", "blocks the merge", "blocking predicate") ... Flag each
   such row in its source". `Predicate: not contract-mapped`, `Contract mapping: none`, `Not material`, `Canonical: yes.
   Material: yes.` state the blocking predicate's result, or the conditions that decide it, in words; the amendment's own
   third example flags a state for merely naming the predicate. The unflagged rows contradict "flag each such row".
2. Canonical reproduction: the rows are the production builder's output at 434b727 with the PIN's code
   (`build_dataset.py --version 2`), byte-identical to the dataset the record pins (V-1); their sources carry no `leak`.
3. Material effect: the per-row `leak` fields are the state item 8 asks for (the interface a training run selects on), and
   the reported counts are the evidence it asks for. At least 61 rows per question (the explicit results alone; 93 with
   the whole walk) are missing from both: 1.7 times the 36 rows per question the builder flags in all, and the 93-row class
   is `true` 38% of the time against the 9.3% base, so a run that drops the flagged rows keeps a strong label tell in 11% of
   the finding rows. This is WHY item 2 of the VERIFY brief (the model learns the leak).
4. Concrete discriminator: `probes/blockwords.py` and the strict count (deterministic, rc 0) on the rebuilt dataset. As a
   test: "every `v1.*` state that holds `not contract-mapped` or `contract mapping: none` carries `blocking-words`" is red
   at 434b727 (for example `VERIFY-J1-2-report.md#F8`, `VERIFY-K1-h-report.md#1`).
5. Task ownership: `LEAKS` (`scripts/laya_ft/build_dataset.py:143-148`) and the record are inside the DSV2 boundary.
The one focused repair: extend `blocking-words` with the predicate-walk forms (at least `contract[- ]mapp`, `not
contract-mapped`, `canonical( path)?:`, `material( effect)?:`, `not material`, `no material effect`, `discriminator:`,
`task ownership`, `in[- ]boundary:`, `\bpredicate:`), regenerate the record (the manifest's dataset sha and `summary.json`
change; `labels.jsonl` does not, since labels carry no flags and item ids follow the states), and paste the new counts.
Interpretive dependency, stated: if the coordinator reads item 8 as the explicit outcome words only (not the predicate's
evaluation), condition 1 fails and V-6 is a FOLLOW-UP.

**V-4 (one `not-cited` row cited in shorthand): FOLLOW-UP.** 1 fails: D-085 (1) defines the truth as J2's own
(`ap_probe.py:80`, the id rule `\bAF-AP-(\d+)\b`), under which AF-AP-91 is not cited; the builder applies that definition.
2 holds (the production build, item `ap-419a51ffa4edffee5e28`); 3 is one provenance among 3,423; 4 holds (`shorthand.py`);
5 holds (`build_dataset.py`).

**V-3 (the text rule's blind shapes): FOLLOW-UP.** 1 fails: the brief lets the builder define the overlap test, and "no
training state may contain a held-out text" holds at the build commit by a stronger measure than the rule (5-gram share at
most 0.09). 2 holds (the production `Overlap` over the committed samples). 3 fails: nothing leaks at 434b727. 4 holds (the
96/96 and 100/100 shape counts). 5 holds (`build_dataset.py`).

**V-9 (block ends past the finding): FOLLOW-UP.** 1 fails: each case follows AMENDMENT 1 item 5's frame as written (a
sibling item with no blank line before it, a list title, a summary line are not anchors, headings or rules). 2 holds (the
production `_family_findings` at 434b727). 3 is small (4 states read). 4 holds (the listed lines). 5 holds (decide-harvest).

**V-16 (five rules pinned only by the record bytes): FOLLOW-UP.** 1 fails: evidence demand 6 names its mutants, and all of
them are red on named tests (the builder's table); no frozen criterion names these five. 2 holds (each mutant changes the
production output at 434b727). 3 fails today: the data is right (V-5, V-8). 4 holds (M8, M12, M14, M19, M21). 5 holds (the
test files are in the boundary).

**V-17 (the F6 level rule untested): FOLLOW-UP.** 1 fails: item 5 asks for tests on three named real lines, and they exist;
the overclaim is a test comment's. 2: not applicable (a comment). 3 fails: no F6 block at 434b727 has a deeper heading. 4
holds (M13). 5 holds (`tests/test_decide_harvest.py`).

**V-15 (outside-16 count 52 against 51): INFO.** Condition 3 fails: one source in a summary count; no row or label changes.

## 6. NOT done

- The decide-harvest CLI at 434b727 was not re-run: it reads its sources at the HEAD of `--root`, and a checkout at 434b727
  needs a second worktree or a checkout, which the venue rule forbids. Reproduced instead in process with the test's
  replica, which the PIN script pins to the CLI (`369 c4589e0d77a97d9b`), and the new script's result equals the builder's
  CLI number (`1113 4d139bab00d0991c`).
- No CPU smoke of `train.py` (the builder's evidence demand 5, not this brief's); no PC run and no CI run (no bridge, by rule).
- The near-duplicate measure is word 5-grams: a paraphrase, a translation or a partial quote under 5 words is not measured.
  Paraphrased registry names in ap queries are not measured.
- Not re-read: the builder's 265 recall misses and every one of the 726 family blocks. Read: 30 seeded anchors, the 13
  locator mismatches, the 18 unplaced ids, the 11 blocks that hold another class-word anchor, the 23 blocks over 20 lines
  (listed with their last lines, not read in full), 12 predicate-walk states.
- The evasion shapes of V-3 were measured against the production `Overlap` with the real held-out texts, not planted
  through `collect_v2` on a fixture repository (that needs a new git repository; I made no git write beyond the worktree).
- GitNexus `impact` ran against the shared tree's index (the worktree has none); the callers were read in the worktree.
- `report_lint.py` result: section 8.
- Scratch at the end: see section 8; the worktree is removed last.

## 7. Gate recommendation

**NOT-READY** on V-6 alone (the leak flags miss the blocking predicate stated in words: at least 61, and with the whole
walk 93, `v1.*` rows per question unflagged against item 8), under my reading of AMENDMENT 1 item 8; if the coordinator
reads item 8 as the explicit outcome words only, V-6 is a FOLLOW-UP and the recommendation is MERGE-READY-WITH-FOLLOWUPS.
Everything else I attacked held, reproduced through the production path: the record rebuilds byte for byte (V-1); no
held-out finding, entry or linked commit reaches training by identity or by text (V-2, V-3); every ap label recomputes from
the raw sources (V-5) and every finding class and blocking answer matches its report line (V-8); the loader's two changes
behave as the amendment says (V-11); the labels are one-hot, joined and deterministic (V-14); decide-harvest's 369 rows and
version 1's bytes hold (V-13); both test runs `143 passed` (set `5d6a3ce56265`). The repair is one narrow change plus a
record regeneration; the follow-ups are V-3, V-4, V-9, V-16 and V-17. The coordinator owns the gate.

## 8. Gates on this report, and cleanup

- `python3 scripts/report_lint.py --root <the worktree> tasks/briefs/jev-laya/VERIFY-DSV2-report.md` after three bounded
  rounds (round 1: `32 refs — OK 11, NEAR 0, MISS 9, UNCHECKABLE 4, UNRESOLVED 8`; round 2: `OK 29 ... UNCHECKABLE 3`):
  `report_lint: 32 refs — OK 31, NEAR 0, MISS 1, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`. The one MISS is the B9 citation in
  V-9: the number is right (`git show 434b727:tasks/briefs/s0-02-support/VERIFY-B9-report.md | sed -n 463p` prints the F-13
  anchor), and the lint reads the backticked `INFO (no action` on the same report line, which quotes the report's later
  lines. Stopped at three rounds (AF-AP-76). A last read-only run after the worktree was removed, `--rev da2ba1b` from the
  shared repo: `report_lint: 36 refs — OK 31, NEAR 0, MISS 1, UNCHECKABLE 0, UNRESOLVED 4 (at da2ba1b)`; the four
  unresolved are bare `ap_probe.py:80` / `:82` short names for `docs/research/findings/ap-hawk-probe/ap_probe.py` (the
  full path is cited in V-4 and V-7), left as they are after the three rounds.
- Separator bytes in this report: `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` prints 0 (checked after every edit).
- Probe scripts, all rc 0, in `$V/probes/`: agree.py, aplabels.py, blockwords.py, edits.py, entry_tail.py, fclass.py, leaks.py,
  linkage.py, linkage2.py, linkage3.py, loader.py, mutate.py, neardup.py, records.py, regress.py, shorthand.py. They read
  `$W`; to re-run one, recreate the worktree at da2ba1b with the brief's command first.
- Git writes: the worktree add (03:26Z) and its removal (below); nothing else. `git status --short` in the worktree read 0
  lines after the test runs and after the mutation audit, and the four code files hashed to the premise values.
- Worktree removed at 04:27Z: `git -C /home/user/agent-factory worktree remove --force <scratch>/wt` rc 0; `git worktree list`
  shows no verify-dsv2 entry; the scratch holds 22 MB (the v1 and v2 rebuilds, the labels, the probes, the test logs).
