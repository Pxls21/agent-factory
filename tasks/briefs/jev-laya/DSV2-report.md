# DSV2 report: the Laya/RWKV training set, version 2, labeled with recorded answers (task #251; D-083)

Role: code-implementer (sandbox, Opus 5.5). Brief: `tasks/briefs/jev-laya/DSV2-brief.md`. PIN: 434b727.
STATUS: DONE (not verified): built under AMENDMENT 1 (D-085) and gated in the sandbox, 2026-09-25 01:46Z-03:1xZ. Three test
runs green (143 passed each) on trees with HEAD's `scripts/transcript_export.py`; the version-2 record rebuilds byte for
byte at the PIN; the CPU smoke joins 8 of 8 rows. WARNING: the SESSION-EXPORT lane's edit to `scripts/transcript_export.py`
(in the tree since 03:1xZ) turns the record test red on one manifest hash; one regenerated file fixes it (section 12,
adjacent risk 1). Nothing is committed (the coordinator commits). No verify round has run. Sections 1-6 are the first pass (the STOP) and
stay as written; their line numbers are at the PIN (this lane's edits moved some lines since). Sections 7-12 are the build.

## 1. Premise (evidence demand 1)

Measured 2026-09-25 01:23Z (`date -u`), sandbox.

| Premise line | Brief | Measured now | Match |
|---|---|---|---|
| HEAD / origin head | 434b727dfd2b / 434b727dfd2b | 9c4446a4cba2 / 9c4446a4cba2 (2 commits past the PIN: dfd03d6 adds this brief only; 9c4446a touches `transcripts/sandbox/chat-2026-09-25.md` only) | moved; neither commit touches the boundary or a harvest input |
| decide-harvest last lines | `negatives: 0 ...`, `sources: 298 read (incident_log=1, lane_report=165, transcript_jsonl=0, verify_report=132), 276 with no records; refused: 153 records; skipped: 0 duplicates` | identical (these 3 summary lines go to stdout; the stderr file ends with `harvest-source-unparseable` lines); rc 3 (`return 3 if refused else 0`, `scripts/decide-harvest@434b727:914`) | yes |
| rows.jsonl sha256/16, question counts | `c4589e0d77a97d9b`; v1.finding_class 213, ap.violates_row 153, wf.drift 3 | `c4589e0d77a97d9b`; 369 rows, the same counter | yes |
| `REPORT_RX` line | `35:REPORT_RX = re.compile(r"/VERIFY-[^/]*-report\.md$")` | identical | yes |
| venv | torch 2.14.0+cpu laya 0.3.5 | torch 2.14.0+cpu laya 0.3.5 | yes |
| DATA-INT reproduction | finding_class rows 86 (missing truth 0, ambiguous 0); OpenJev agrees 38; majority INFO 49; truth FOLLOW-UP 34, INFO 49, BLOCKER 3; blocking rows 86, OpenJev correct at 0.5 72, always-false 83, TP 1 FN 2 FP 12 | identical, all eight numbers (`$S/premise_dataint.py`: the version-1 rebuild at 0b342c7 joined to the committed OpenJev labels by key, truth = decide-harvest's class by source path + finding id) | yes |
| version-1 baseline | `d7cd9b49...` at 0b342c7 | `d7cd9b49abac267bb9b5290641ea353180a9a61047ce6c590809520b085cea1c`, 4077876 bytes, 1788 rows (ap 1616, v1 86 + 86), rc 0, 10.7 s | yes |

`$S` = `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/dsv2`.

The premise block holds. The seam trace (section 2) does not.

## 2. STOP: the design conflicts with a seam outside the boundary

**The trainer's loader refuses a commit-message row.** The brief's version-2 mode reads commit messages as ap states ("each
against the registry's lexical top 16"), so each commit row needs a source that names a commit. `train.py` loads a dataset
only through `rows, dmanifest = C.load_dataset(args.dataset)` (`scripts/laya_ft/train.py:252`, before `--limit` at
`:259-260`), and that loader runs
`check_no_heldout` over every row (`scripts/laya_ft/common.py@434b727:227`), which calls `row_identities`
(`common.py:176-187`). `row_identities` knows two source kinds, `verify_finding` and `incident`, and raises
`DatasetError("... unknown source kind ...")` for any other. `train.py` maps that to "refused", exit 64 (`train.py:377-379`).
`teacher_label.py:204` loads the same way. `common.py` is READ-only in the brief's boundary.

Probe (`$S/probe_source_kind.py`, one-row datasets through the real `C.load_dataset`):

```
incident -> loaded 1 row
commit -> DatasetError: row ap-50888d483d0a866078d7: unknown source kind 'commit'
```

So a version-2 dataset that holds commit rows cannot pass evidence demand 5 (the CPU smoke must load it) without a change
to `common.py`. The only kinds the loader accepts would misname a commit as a report finding or an incident entry; I will
not do that. I have not written any code.

Options for the coordinator (the decision is yours):

1. **Add `scripts/laya_ft/common.py` to the boundary** (with its tests in `tests/test_laya_ft.py`). The smallest change:
   `row_identities` learns a `commit` kind with the identity `("commit", <sha>)`, and `check_no_heldout` must not look up
   `heldout["commit"]` (today it indexes `heldout[kind]` for every identity, `common.py:195`, so a new kind also needs
   `heldout_identities` to return an empty `commit` set, or a skip for kinds with no sample). The version-1 bytes do not
   depend on either function.
2. **Leave commit rows out of version 2** and record them as NOT-done. Everything else in the brief is buildable inside
   the boundary as written.
3. Something else you choose.

## 3. The brief's two open questions, measured

All counts at the PIN 434b727, read-only, producers under `$S/survey/` (each rc 0).

### 3.1 Can every family's block end be found without ambiguity? No, not for every family.

Producer: `families_survey.py` (DATA-INT's `goal2a.py` regexes for F1-F4, F6-F8, F11, F12; lines decide-harvest does
not admit today; 132 reports: 102 `VERIFY-*`, 30 `report-pc-verify-*`). The end rule tried: the next anchor (the
admitted grammar or any family) or markdown heading, as `j2c._blocks` ends a bullet; for F6 the next heading of the same
or higher level.

| Family | Anchor lines | 2 distinct class words on the line | Block <= 5 lines | 6-20 | > 20 | Runs to EOF |
|---|---|---|---|---|---|---|
| F1 (all 66 are decide-harvest's `bad-title` refusals) | 66 | 4 | 58 | 8 | 0 | 0 |
| F2 | 145 | 3 | 94 | 49 | 2 | 0 |
| F3 | 251 | 2 | 141 | 100 | 10 | 0 |
| F4 | 54 | 3 | 29 | 24 | 1 | 0 |
| F6 | 84 | 0 | 12 | 62 | 10 | 0 |
| F7 | 32 | 1 | 26 | 3 | 3 | 1 |
| F8 | 79 | 2 | 50 | 28 | 1 | 2 |
| F11 | 7 | 0 | 3 | 4 | 0 | 0 |
| F12 | 1 | 0 | 1 | 0 | 0 | 0 |
| total | 719 | 15 | 414 | 278 | 27 | 3 |

(These are anchor lines. DATA-INT 3.2 counts distinct (report, id) first occurrences and skips ids the grammar admits
elsewhere, so some of its numbers are lower, for example F3 245 there and 251 here.)

Where the end is wrong: the last finding before an unheaded section swallows it. Seen:
`tasks/briefs/s0-01-n5l-support/VERIFY-N5m-report.md:13` (F8, `1. BLOCKER — ...`) runs 75 lines to end of file, whose
last line is a graft banner; `tasks/briefs/pc/report-pc-verify-b4.md--95c0bb1.md:127` (F7, `5. B4-05 — INFO / SOLID`) runs
64 lines and takes the report's `Retro:` paragraph. Most long blocks read as one long finding (for example
`VERIFY-J1-2-R1-report.md:82`, an F6 heading with a 47-line body). I did not read all 27 long blocks. A list-item rule
(the item ends at a blank line followed by an unindented line) would cut the two bad cases, but would also cut F6 and
bold-paragraph findings that run over several paragraphs. The rule needs your choice, or a per-family rule I define and
test.

The 15 two-class anchor lines, read one by one (all 15 are in `$S/survey/families.json`):
- 6 name two classes in the class slot, for example `R1-F-7 FOLLOW-UP / UNVERIFIED` (`jev-laya/VERIFY-GW1-R1-report.md:162`),
  `F-10 (UNVERIFIED, FOLLOW-UP)` (`jev-laya/VERIFY-JT1-report.md:146`), `VE3R1-F2 — FOLLOW-UP/INFO`
  (`s0-05-support/VERIFY-E3-R1-report.md:404`). These are ambiguous: they should stay refused.
- 4 put the second word in a qualifier right after the class, for example `V-11 FOLLOW-UP (KNOWN class F-B4)`
  (`laya/VERIFY-J1-0-R4-report.md:749`). decide-harvest's own table grammar already reads `CLASS (qualifier)` as CLASS
  (`_parse_class`, `scripts/decide-harvest:381-388`).
- 5 carry the second word later in the prose, for example `F-17 FOLLOW-UP — ... INFO-level.`
  (`laya/VERIFY-J1-3-R2-report.md:550`).

The brief says "one class word". Read literally (one class word on the whole line), it refuses all 15. Read as "one
class in the class slot" (a second class word joined by `/` or `,` inside the slot is ambiguous; a qualifier or later
prose is not), it refuses 6 and admits 9. I would take the second reading and test it both ways, unless you rule otherwise.

### 3.2 Commit messages that cite an AF-AP id in passing

Producer: `commits_survey.py`. 1576 commits reachable from the PIN; 457 cite an AF-AP id (DATA-INT's 457); every one of
them cites at least one row in the 201-row registry.

| Where the ids sit | Commits |
|---|---|
| an id in the subject line | 222 |
| ids in the body only | 235 |
| the commit adds a registry row new in that commit (ids on `+|` lines minus ids on `-|` lines of its `docs/INCIDENT-LOG.md` diff) | 143 (all 143 cite the rows they add; 54 also cite other rows) |

A first count that took every `+| AF-AP-n |` line as an addition gave 197: it counted edited rows. The rule above is the
corrected one.

Six body-only citations read (the first six in log order, `$S/survey/commits.json`): 2 name the defect's class as an
instance ("AF-AP-145's class: every `exit` ...", aa1eb84; "AF-AP-187's class in prose", 2304181), 1 gives the change's
motive ("Why: AF-AP-145 (...)", 41b79a8), 2 describe FOLLOWING the rule, not breaking it ("Priced first (AF-AP-201)",
2969794; "(AF-AP-139; its own negative control ...)", 1b80f5d), 1 is a component's name ("the AF-AP-200 tell", 18d6468).
So a body-only citation is often not "this message shows this anti-pattern". Six is a small sample.

Deterministic ways to tell them apart, cheapest first:
1. Position: subject line vs body only (measured above; no reading needed).
2. The registry-add rule above (the commit creates the row).
3. A phrase rule on the words around each occurrence ("'s class", "met again", "second shape" for an instance;
   "Priced first", "per", "Why:" for compliance or motive). It needs its own precision read before use.

The brief's provenance list has one `commit-cite`. If you want 1, it splits into two values (subject vs body only), so a
training run can select. That is a change to the brief's vocabulary, so it is your call.

## 4. Other points the amendment should settle (measured; not stop reasons on their own)

1. **D-1 leaves the ap question with positives only.** Producer `ap_survey.py`, ranking exactly as `build_dataset.rank`:
   a version-2 build at the PIN would hold about 9,072 ap rows (110 non-held-out incident entries x 16 = 1,760; 457
   commits x 16 = 7,312). Cited candidates, the only rows D-1 labels: incident 76 (heading 12, body 72; both counted
   once), registry-commit 172, commit subject 70, commit body-only 190. That is 508 labels, all "true", and 8,564
   unlabeled rows. 309 commit-cited ids fall outside their commit's top 16. A noul question with no negatives cannot
   teach "false". If you want "not cited in a source that cites something" to be a recorded "false", the provenance list
   needs a value for it (for example `not-cited`).
2. **Heading/body agreement (D-2, DATA-INT X3):** 6 entries cite registry rows in both the heading and the body; 4 cite
   the same set, 2 differ (1 body superset).
3. **F14 table rows.** decide-harvest refuses 153 records at the PIN: `bad-title` 66 (all F1), `no-title-column` 78,
   `bad-finding-id` 6, `bad-class` 3. Of the 78 `no-title-column` rows, 48 carry no class word, because their "class"
   column means something else: 31 in `laya/VERIFY-J1-1-R3-report.md` (test-input classes such as `R-1`) and 17 in
   `s0-01-a5k-support/VERIFY-CK12-report.md:428-444` (checker-issue names). The other 30 (20 in `kit-k1-support/VERIFY-K150-report.md`, header
   at `:560`, `| ID | Class | Evidence | Contract mapping | Canonical path | Material effect | ...`; 10 in
   `pc/report-pc-verify-m3.md--e776dd0.md`, a close variant) are real findings with a class but no title cell: the
   finding text sits in "Material effect". Admitting
   them needs a title rule the brief does not give. They also meet an existing test:
   `test_class_table_without_a_title_column_refuses_each_row` (`tests/test_decide_harvest.py:1000`) asserts the refusal
   for a row with an id and one class word. Admitting F14 as the brief words it means changing that test's expectation.
   The 3 `bad-class` rows are `FOLLOW-UP / UNVERIFIED` (x2) and `resolved`: they stay refused under any reading.
4. **F13 tables mix two kinds.** 87 rows under 11 header shapes. Some have a finding column (`id | finding | class | ...`,
   `# | severity | where (at 517c65e) | one line`). Others are blocking-predicate or disposition tables (`# | 1
   contract-mapped | 2 canonical repro | ...`, `id | 1 contract | ...`, `id | production mutation | ...`): their cells
   are the verifier's reasons for the class, and they hold no finding text. As a training state, such a row would put
   the label's own evidence in the input (the leak `j2c` avoided by keeping only the title cell). I would admit F13 only
   under a header with a finding or title column, and dedup by first occurrence per (report, id), as the version-1
   builder does (AF-AP-199).
5. **Duplicate reports across the two sets (X2).** `tasks/briefs/pc/report-pc-verify-o2.md--d12fc13.md` is
   byte-identical to `tasks/briefs/s0-03-support/VERIFY-O2-report.md`, and the B67 pair shares lines (both line 234 read
   `3. FOLLOW-UP — B7 exact-values preflight test is a source mirror. ...`). `fit_rows` merges identical (state,
   question) rows and keeps both sources. Near-identical blocks would stay as two rows with the same label.
6. **Regression tests are runnable.** CI clones with `fetch-depth: 0` (`.github/workflows/stage0-ci.yml:30`), so a test
   can build the 369-row fixture from `git archive 434b727` into a temp repo (a git write only there). The version-1 byte
   test needs the Laya venv and model: it would use the existing fixture and its declared loud skip outside the sandbox
   venue (`def laya_venue():`, `tests/test_laya_ft.py:673`).
7. **The manifest's `code` hashes change by construction.** `scripts/decide-harvest` and `build_dataset.py` are both in
   `CODE` (`build_dataset.py:37-39`). So version 1's `manifest.json` changes; its `dataset.jsonl` (`d7cd9b49...`) is the
   byte clause, and the brief's evidence demand 4 names the dataset bytes.
8. **Version-1 byte safety constrains the decide-harvest change.** `j2c._blocks` (the version-1 cut) calls
   decide-harvest's `BULLET_FINDING_RE`, `_heading_text`, `MARKDOWN_HEADING_RE`, `_split_table_row`, `_is_separator`,
   `_title_column`, `_parse_class` and `FINDING_ID_RE` directly (`docs/research/findings/j2c-fulltext/j2c.py:58-93`). The
   new families must be added beside these, never by changing them, or version 1's bytes move.

## 5. What this lane did and did not do

Done (all read-only except this report):
- The premise block, re-measured line by line (section 1): it holds.
- The seam trace of the brief's consumers (`common.py`, `train.py`, `teacher_label.py`, `evaluate.py` (reads no
  `sources`), `j2c.py`, `ap_probe.py`, `v1_probe.py`, `decide-harvest`, both test files).
- One probe that proves the conflict (section 2) and four read-only surveys (sections 3-4).

NOT done (every build item; the STOP is why):
- No change to `scripts/decide-harvest`, `tests/test_decide_harvest.py`, `scripts/laya_ft/build_dataset.py`,
  `tests/test_laya_ft.py`; `scripts/laya_ft/recorded_labels.py` and its tests are not created; nothing is written under
  `docs/research/findings/laya-ft-labels/2026-09-25-recorded/`.
- Evidence demands 2 (precision read of 20 and the recall check), 3, 4, 5 (CPU smoke), 6 (mutants) and 7 (gates on
  written code): not run. There is no code to gate.
- The survey numbers are regex counts at one commit. They are for the amendment, not the dataset's final counts.

Files written: this report only (`tasks/briefs/jev-laya/DSV2-report.md`). Scratch only: `$S/premise/`, `$S/v1-0b342c7/`,
`$S/premise_dataint.py`, `$S/probe_source_kind.py`, `$S/survey/`.

## 6. Self-attack: how this STOP could be wrong

1. *The loader might accept a commit row some other way.* Ruled out by the probe through the real `C.load_dataset`: the
   positive control (`incident`) loads and `commit` is refused. `row_identities` has no extension hook
   (`common.py:176-187`), and `train.py` has one load path (`:252`).
2. *Commit messages might be meant as label sources for incident rows, not as their own rows.* Then no new kind would
   be needed. Ruled out by the brief's own wording: the messages are "scrubbed with `transcript_export.scrub`, the ids
   masked as `ap_probe` masks them" (only a state is scrubbed and masked), and each is ranked "against the registry's
   lexical top 16" (its own candidate list).
3. *Stopping might be too strict when most of the brief is buildable.* That is option 2. It changes the brief's goal,
   and the pinned rule for this lane is stop-and-report, not a self-accepted cut.

## 7. Build under AMENDMENT 1: the design decisions (written before the code)

Read at 01:46Z: `tasks/briefs/jev-laya/DSV2-brief.md:114-168` (AMENDMENT 1) and `docs/08_DECISION_LOG.md` D-085. HEAD
8aa05a8 (origin 2a1be2b plus one transcript commit). The PIN stays 434b727 for the fixture and the version-2 record.

New measurements that shaped the rules (all at the PIN, `$S/survey/`):

- **F8 list numbers as ids:** 0 of 65 (report, number) ids repeat inside a report (`examples.py`). No family anchor
  restates an id the admitted grammar already admits in its report (0).
- **The list-item end rule, measured on every list-family block (`listrule.py`).** A strict markdown reading (any
  unindented line after a blank line ends the item) cuts 21 blocks, and it leaves the b4 findings with no finding text
  (`report-pc-verify-b4.md--95c0bb1.md:46`, the anchor line is `1. B4-01 — BLOCKER / SOLID`; its body is lines 48-72,
  unindented). A section-title reading (only a short line with no end punctuation ends the item) keeps those bodies,
  but keeps report text after a list's last finding: 4 blocks take a `GATE RECOMMENDATION: ...` line
  (`VERIFY-S198A-report.md:59`, `VERIFY-T94-report.md:77`, `report-pc-verify-b3.md--c6c384a.md:119`,
  `report-pc-verify-g3.md--7f60d83.md:102`), 4 take a `No BLOCKER. No CONTRACT-DEFECT. ...` line, and 6 run into the
  next numbered item whose word is not a class word (`2. **FOLLOW-UPS`, `5. CONTRACT-INVALID`, `3. SHOULD-FIX`,
  `5. **LOW`, `10. **HIGH`).
- **Code fences are unbalanced in one report:** `VERIFY-E3-R1-report.md` closes a fence at line 102 with no opener after
  line 90, so a fence toggle flips the parity for the rest of the file and would hide its 9 real findings (lines
  108-419). The admitted grammar does not track fences either.
- **F13 header shapes (`f13_headers.py`, 87 rows, 11 shapes).** Two shapes have a `finding` column and are still
  blocking-predicate tables (`finding | 1 contract | 2 canonical path | ...`), and one keeps its class in a worded
  `disposition` column (`VERIFY-J1-1-report.md:388`).

The rules (each tested on the real lines named):

1. **Families** F1, F2, F3, F4, F6, F7, F8, F11, F12 use DATA-INT's regexes (`goal2a.py`), first match wins, on lines the
   admitted grammar does not admit. They sit beside decide-harvest's grammar helpers; none of those helpers changes.
   An F1 line is admitted only where the grammar refused it `bad-title`; an `unterminated-heading` refusal stays.
2. **Class slot:** the class word the family reads. A second class word joined to it by `/`, `,`, `or` or `&`
   (`FOLLOW-UP / UNVERIFIED`, `(UNVERIFIED, FOLLOW-UP)`, `FOLLOW-UP/INFO`) refuses the line as `ambiguous-class`; a
   qualifier after the class or a class word later in the prose does not.
3. **Block end** (the frame, then per family): the block ends before the next anchor line of any family or of the
   admitted grammar, before a markdown heading, or before a horizontal rule. F6 ends only at a heading of the same or a
   higher level. A list-item anchor (numbered or bulleted) also ends after a blank line at an unindented line that is
   (a) a sibling item (the same marker kind), (b) a section title (60 characters or fewer, no end punctuation, not a
   list, table, fence, bold or quote line), or (c) a verdict line (a gate word `MERGE-READY`, `NOT-READY`,
   `CONTRACT-INVALID`, a line opening `GATE RECOMMENDATION`, or `No <CLASS>`). Trailing blank lines are dropped. A block
   over 60 lines is cut to 60 and carries `"block_end": "cap"`. Nothing is fence-aware (the E3-R1 finding above).
4. **F13:** a row is admitted only in a table whose header has a title column (`finding...`, `what`, `one line`) and a
   class column named `class` or `severity`, and no numbered predicate column (`1 contract`, ...). The class cell
   follows rule 2; the state is the title cell only, as version 1 keeps for a table row. F14 stays refused.
5. **Dedup:** the admitted grammar's findings first (version 1's order), then family line anchors in line order, then
   F13 rows in line order; an id already admitted in the report is a restatement, not admitted and not refused.
6. **Titles** (decide-harvest's `title` field only): the anchor text after the class slot, through the line that
   closes a wrapped bold span, bold markers dropped, leading separators cut.
7. **Commit rows (amendment 2, D-085):** per candidate row, `registry-commit` when the commit adds that row, else
   `commit-subject` when the subject cites it. A row cited only in the body of an admitted commit gets no label
   (counted): it is cited, so `not-cited` would be false, and the body is not trusted. A commit's linked incident entries
   are the anchored entries whose masked heading appears on an added line of its `docs/INCIDENT-LOG.md` diff (read with
   10 lines of context, so a wrapped heading is whole).
8. **Recorded answers live in the sources, never in the state** (AF-AP-189): each source carries `answer`,
   `provenance` and any `leak`; the state is what the model reads.

## 8. Build progress (checkpoint 02:2xZ; the final numbers are in sections 9-12)

- `scripts/laya_ft/common.py`: `row_identities` knows `commit` -> `("commit", <full sha>)`; any other unknown kind still
  raises; `check_no_heldout` reads a kind no sample holds (`commit`) as empty, while a sampled kind (`v1`, `incident`)
  missing from the held-out dict still raises (fail-closed, not `.get` for every kind). Probe: the `commit` row now
  loads; the version-1 dataset at 0b342c7 loads (1788 rows, `d7cd9b49...`).
- `scripts/decide-harvest`: the grammar's two record loops moved verbatim into `_grammar_records` (a pure move, for the
  builder to read the same records); the families beside it (`FAMILY_ANCHORS`, `_family_findings`,
  `_family_block_end`, `_family_title`, `_f13_columns`). In-process at the PIN (`$S/dh/inproc.py`): the PIN script gives
  369 rows `c4589e0d77a97d9b` (the fixture, reproduced) and the new script 1113 rows with the 369 as an ordered
  subsequence; the 744 new rows are 726 `v1.finding_class` and 18 `ap.violates_row`, all from verify reports. Refusals:
  153 -> 93 (`bad-title` 66 -> 0, all admitted by F1; `ambiguous-class` 6 new; the other 87 unchanged).
- The three pinned block ends hold (J1-2-R1:82 keeps its 46-line body; b4:127 stops at :137; N5m:13 stops at :19).
- `scripts/laya_ft/build_dataset.py --version 2` at the PIN: rc 0, 40 s, 6196 rows, `f1b92d6f...`; version 1 at
  0b342c7 with the new code: `d7cd9b49abac267bb9b5290641ea353180a9a61047ce6c590809520b085cea1c` (unchanged).
- `scripts/laya_ft/recorded_labels.py`: 5301 labels, 0 conflicts, 895 unlabeled (880 rows of incident entries that
  cite nothing, 15 body-only citations inside admitted commits).
- CPU smoke (the brief's exact command): rc 0, 8 examples joined (v1.blocking 4, v1.finding_class 4), 4 steps, loss
  0.708023, guards all true, labels `records 5301, torn 0, duplicates 0`, 0 stale (join_labels refuses a stale label).
  The first 8 dataset rows are findings, so an extra smoke (not the brief's command) ran 8 ap labels (4 commit rows,
  4 incident rows): rc 0, loss 1.002937, guards true.

## 9. Evidence demand 2: the families, precision and recall

All counts are at the PIN, on the final code. Producers: `$S/survey/precision_recall.py` and `$S/survey/report_rows.py`
(both rc 0, re-run 02:5xZ-03:0xZ; outputs `$S/survey/precision_recall.out` and `$S/survey/report_rows.out`). They read the
reports through the final `_grammar_records` and `_family_findings`.

**Admitted per family** (the builder's first occurrence per (report, id), AF-AP-199; `findings_by_family` in the record's
manifest):

| grammar (today's) | F1 | F2 | F3 | F4 | F6 | F7 | F8 | F11 | F12 | F13 | families | all |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 212 | 66 | 143 | 250 | 52 | 84 | 22 | 77 | 7 | 1 | 24 | 726 | 938 |

decide-harvest itself at the PIN (the real CLI, 240 s, rc 3): 1113 rows, sha256/16 `4d139bab00d0991c`, per question
`ap.violates_row=171`, `v1.finding_class=939`, `wf.drift=3`. That is the old 369 rows plus 726 `v1.finding_class` rows and
18 `ap.violates_row` rows. Its refusals fell from 153 to 93 records. (The grammar's 213 finding rows are 212 first
occurrences: one report repeats an id.)

**Precision.** 20 of the 726 family findings, drawn by `random.Random(20260925).sample`. The rule: the finding id and its
recorded class both sit on the finding's own anchor line. Result: **20/20**. I also read each line: all 20 are finding
anchors, and the class is the verifier's class for that finding (one reader).

| Line (at the PIN) | Family | Id | Class | Rule | Text on the line |
|---|---|---|---|---|---|
| `tasks/briefs/laya/VERIFY-J1-0-R23-STAMP-report.md@434b727:525` | F3 | F-B10 | INFO | yes | `F-B10 — INFO (SOLID).** S21` |
| `tasks/briefs/jev-laya/VERIFY-GW1-report.md@434b727:257` | F2 | F-5 | FOLLOW-UP | yes | `F-5 FOLLOW-UP. EPERM reads a` |
| `tasks/briefs/pc/report-pc-verify-g2.md--f84265f.md@434b727:205` | F8 | 3 | INFO | yes | `3. **INFO:**` |
| `tasks/briefs/jev-laya/VERIFY-GW1-R1-report.md@434b727:174` | F2 | R1-F-10 | INFO | yes | `R1-F-10 INFO.` |
| `tasks/briefs/laya/VERIFY-J1-2-report.md@434b727:201` | F3 | F7 | BLOCKER | yes | `F7 — BLOCKER.` |
| `tasks/briefs/s0-02-support/VERIFY-B9-report.md@434b727:433` | F3 | F-7 | FOLLOW-UP | yes | `F-7 · FOLLOW-UP · SOLID — th` |
| `tasks/briefs/s0-05-support/VERIFY-E3-report.md@434b727:923` | F3 | F19 | FOLLOW-UP | yes | `F19 — FOLLOW-UP (doc). Decla` |
| `tasks/briefs/s0-05-support/VERIFY-E2-R1-report.md@434b727:140` | F3 | F3 | FOLLOW-UP | yes | `F3 — FOLLOW-UP — the namespa` |
| `tasks/briefs/jev-laya/VERIFY-JT2-R1-report.md@434b727:807` | F1 | R2-e | INFO | yes | `R2-e INFO (R).** R2-M3 (scru` |
| `tasks/briefs/s0-02-support/VERIFY-B9-report.md@434b727:439` | F3 | F-8 | FOLLOW-UP | yes | `F-8 · FOLLOW-UP · SOLID — fa` |
| `tasks/briefs/pc-t90-support/VERIFY-T94-report.md@434b727:74` | F8 | 2 | FOLLOW-UP | yes | `2. **FOLLOW-UP, SOLID.**` |
| `tasks/briefs/laya/VERIFY-J1-1-R1-report.md@434b727:664` | F3 | V-24 | INFO | yes | `V-24 — INFO (no finding).**` |
| `tasks/briefs/hermes-repin/VERIFY-REPIN-a-report.md@434b727:299` | F3 | F17 | INFO | yes | `F17 — INFO.** The premise ho` |
| `tasks/briefs/pc/report-pc-verify-g3.md--7f60d83.md@434b727:100` | F8 | 6 | FOLLOW-UP | yes | `6. FOLLOW-UP, SOLID — fixtur` |
| `tasks/briefs/jev-laya/VERIFY-T243-245-report.md@434b727:345` | F2 | A-F7 | INFO | yes | `A-F7 INFO (pre-existing) — p` |
| `tasks/briefs/canny/VERIFY-C1-R1-report.md@434b727:494` | F13 | F-9 | INFO | yes | `a user pattern that matches` |
| `tasks/briefs/laya/VERIFY-J1-0-R1-report.md@434b727:136` | F3 | R4 | FOLLOW-UP | yes | `R4 — FOLLOW-UP (contract gap` |
| `tasks/briefs/canny/VERIFY-C1-R1-report.md@434b727:496` | F13 | F-11 | INFO | yes | `F-11` |
| `tasks/briefs/laya/VERIFY-J1-0-R4-report.md@434b727:762` | F1 | V-16 | INFO | yes | `V-16 INFO** — a Python gate` |
| `tasks/briefs/jev-laya/VERIFY-T243-245-R1-report.md@434b727:184` | F2 | R1-A-F1 | BLOCKER | yes | `R1-A-F1 BLOCKER — A-F1's roo` |

The rule is weak on its own: a family reads the id and the class from the anchor line, so the rule mostly re-checks the
regex. The read is the stronger half, and it has one reader.

**Recall.** Lines in anchor position (a list item, a heading, a bold opener or a table row) with a class word in their first
80 characters that neither the grammar nor a family admits: **265**.

| Why not admitted | Lines |
|---|---|
| no family shape | 122 |
| a table row outside F13 (predicate, disposition or other tables) | 88 |
| `no-title-column` (F14; refused by ruling 6) | 30 |
| `restated` (the id is admitted earlier in the report) | 15 |
| `ambiguous-class` (two classes in the slot) | 6 |
| `bad-class` | 2 |
| `bad-finding-id` | 2 |

(The builder counts 17 restatements. The other 2 are F13 rows of `tasks/briefs/canny/VERIFY-C1-report.md`, lines 376 and
378, whose class cell sits after character 80: `$S/survey/restated_check.py`.)

A seeded sample of 12 of the 122 "no family shape" lines, read one by one. 5 are real findings the families miss (marked
MISSED); 7 are not findings.

| Line (at the PIN) | Text on the line | My read |
|---|---|---|
| `tasks/briefs/laya/VERIFY-J1-3-R1-report.md@434b727:492` | `branches are untested; the` | MISSED: a bold class-id, `**FOLLOW-UP-3 — ...**`, no bullet |
| `tasks/briefs/s0-05-support/VERIFY-S0-05-report.md@434b727:275` | `- **M1 (pid-only) — F-2, FOL` | a mutant row that points at finding F-2 |
| `tasks/briefs/jev-laya/VERIFY-JT3-report.md@434b727:168` | `- False negatives (FOLLOW-UP` | a list of cases, one class each |
| `tasks/briefs/s0-01-b5j-support/VERIFY-B5i-report.md@434b727:339` | `### VB-F14 [INFO] SOLID — th` | MISSED: a bracketed class in a heading |
| `tasks/briefs/laya/VERIFY-J1-3-R2-report.md@434b727:575` | `explanation "bold` | prose that names a class |
| `tasks/briefs/jev-laya/VERIFY-JT3-report.md@434b727:165` | `- More false positives (INFO` | a list of cases |
| `tasks/briefs/laya/VERIFY-J1-3-R1-report.md@434b727:531` | `harvest-output-invalid:  (EN` | MISSED: a bold class-id, `**INFO-9**` |
| `tasks/briefs/pc-t90-support/VERIFY-T94-report.md@434b727:57` | `## 7. Sibling sweep — INFO` | a section heading, no id |
| `tasks/briefs/s0-05-support/VERIFY-S0-05-report.md@434b727:281` | `counts O_WRONLY and O_RDWR` | a mutant row that points at finding F-3 |
| `tasks/briefs/s0-01-a5o-support/VERIFY-A5o-report.md@434b727:7` | `1. [BLOCKER] The asserted bi` | MISSED: a bracketed class in a numbered item |
| `tasks/briefs/s0-01-vb-f12-support/VERIFY-G2-report.md@434b727:271` | `## Item 7 — exhaustive bound` | a section heading |
| `tasks/briefs/pc/report-pc-verify-gov2e.md--949aa85.md@434b727:27` | `6. INFO/DISCREPANCY: the bri` | MISSED: an indented numbered item |

So about 5 in 12 of the no-shape lines are missed findings. Scaled to 122 that is roughly 50 (inferred from a sample of
12, not counted). The shapes: a bracketed class (`[INFO]`, `[BLOCKER]`), a bold class-id with no bullet, an indented
numbered item. None of them is in DATA-INT's family list; adding one is a new family, not a fix here.

## 10. Evidence demand 3: the version-2 counts (the record at the PIN)

The record is `docs/research/findings/laya-ft-labels/2026-09-25-recorded/`:

| File | Lines | Bytes | sha256 |
|---|---|---|---|
| `dataset-manifest.json` | 133 | 3737 | `efd3c91306cc967b7ddc...` |
| `labels.jsonl` | 5301 | 2667100 | `0098e52e0dbfc01db12bfceb0a807db6fad533e10cf7380c72e368926375ca58` |
| `summary.json` | 206 | 5973 | `4fdd169cc9a05ec6a000...` |

The dataset (`dataset.jsonl`, 12795031 bytes, `f1b92d6fa79c2f145052fec9f301f1e719987ae5f7d14e19f663eb67426b5c48`) is not in
the record: it rebuilds byte for byte from the PIN, and `test_version_2_record_rebuilds_byte_identically_at_the_pin` checks
that. Commit 434b727, commit time 1790299156 (git's `%ct`; each label's `ts`).

**Rows.** 6196 after the merge of identical (state, question) rows (24 merged). Cut to Laya's window: ap 253,
`v1.blocking` 6, `v1.finding_class` 7.

| Question | Rows | Labeled | Unlabeled |
|---|---|---|---|
| ap.violates_row | 4544 | 3649 | 895 |
| v1.blocking | 826 | 826 | 0 |
| v1.finding_class | 826 | 826 | 0 |
| all | 6196 | 5301 | 895 |

Conflicts (a row whose sources record two answers): 0. The 895 unlabeled rows: 880 from the 55 kept incident entries that
cite no registry row (55 x 16), and 15 rows cited only in the body of an admitted commit.

**Sources by kind, question, recorded answer and provenance** (a merged row counts each of its sources; `summary.json`,
`rows_by_source_question_answer_provenance`):

| Source kind | Question | Answer | Provenance | Sources |
|---|---|---|---|---|
| verify_finding | v1.finding_class | INFO | verifier-class | 408 |
| verify_finding | v1.finding_class | FOLLOW-UP | verifier-class | 341 |
| verify_finding | v1.finding_class | BLOCKER | verifier-class | 68 |
| verify_finding | v1.finding_class | CONTRACT-DEFECT | verifier-class | 10 |
| verify_finding | v1.finding_class | UNVERIFIED | verifier-class | 10 |
| verify_finding | v1.finding_class | KNOWN | verifier-class | 1 |
| verify_finding | v1.blocking | false | verifier-class | 760 |
| verify_finding | v1.blocking | true | verifier-class | 78 |
| incident | ap.violates_row | true | body-cite | 64 |
| incident | ap.violates_row | true | heading-cite+body-cite | 8 |
| incident | ap.violates_row | true | heading-cite | 4 |
| incident | ap.violates_row | false | not-cited | 804 |
| incident | ap.violates_row | none | none | 880 |
| commit | ap.violates_row | true | registry-commit | 88 |
| commit | ap.violates_row | true | commit-subject | 62 |
| commit | ap.violates_row | false | not-cited | 2619 |
| commit | ap.violates_row | none | none | 15 |

**The class balance per question** (per row, as `labels.jsonl` holds it; D-3: reported, not rebalanced):

| Question | Answer | Labels | Share |
|---|---|---|---|
| ap.violates_row | true | 226 | 6.2% |
| ap.violates_row | false | 3423 | 93.8% |
| v1.blocking | true | 77 | 9.3% |
| v1.blocking | false | 749 | 90.7% |
| v1.finding_class | INFO | 404 | 48.9% |
| v1.finding_class | FOLLOW-UP | 334 | 40.4% |
| v1.finding_class | BLOCKER | 67 | 8.1% |
| v1.finding_class | CONTRACT-DEFECT | 10 | 1.2% |
| v1.finding_class | UNVERIFIED | 10 | 1.2% |
| v1.finding_class | KNOWN | 1 | 0.1% |

Version 1 had 86 finding rows (INFO 49, FOLLOW-UP 34, BLOCKER 3) and no row of the three rare classes (DATA-INT X4).
Version 2 has 10, 10 and 1. KNOWN is still one row. Labels by provenance: ap `not-cited` 3423, `registry-commit` 88,
`body-cite` 64, `commit-subject` 62, `heading-cite+body-cite` 8, `heading-cite` 4; both v1 questions `verifier-class` 826.

**The ap sources** (amendment items 2 and 3; `sources.ap` in the manifest):

| | Commits | Incident entries |
|---|---|---|
| at the PIN | 1576 | 210 |
| cite at least one registry row | 457 (all commits) | 55 (of the 110 kept) |
| held out by identity | 82 (linked to a held-out entry; each would be admitted otherwise) | 100 |
| admitted | 174: `registry-commit` 71, `commit-subject` 103 | 110 (55 label their 16 rows; 55 cite nothing) |
| not admitted: the citation is in the body only | 201 | none |
| every cited row outside the top 16 (all 16 rows `not-cited`) | 52 | 6 |
| rows cited only in the body of an admitted commit (unlabeled) | 15 | none |

The commit counts add up: 174 + 201 + 82 = 457. Linkage, measured before the builder ran: 104 commits add at least one
held-out entry, every one of the 100 held-out headings is linked, and the link sets have sizes {1: 91, 2: 12, 3: 1}.
Registry rows added per registry-adding commit (143 commits): {1: 105, 2: 26, 3: 7, 4: 3, 5: 1, 6: 1}.

**Held-out exclusions (D-3).**

| Source kind | Identities held out | Excluded by identity | Excluded by text |
|---|---|---|---|
| verify_finding (J2 v1 and J2c: the same 100 findings) | 100 | 100 | 0 |
| incident (the AP sample) | 100 | 100 | 0 |
| commit | none (no sample holds a commit) | 82 (linked) | 0 |

The overlap test: a state is held out when it CONTAINS a held-out text after one normal form (`overlap_norm`: the class
words and AF-AP ids masked as the states mask them, scrubbed, lower case, whitespace collapsed). The held-out texts are
the J2c blocks, the J2 v1 titles and the AP headings: 290 distinct after the normal form, 286 used, 4 J2 v1 titles under
40 characters not used (for example `mutation test gaps`). The builder runs the test twice: on every candidate source,
and again on every final row. At the PIN it excludes nothing; the tests prove it on planted texts (section 11).

**Heading/body agreement (D-2, DATA-INT X3).** 6 kept entries cite registry rows in both the heading and the body:

| Agreement | Entries |
|---|---|
| the same set | 4 |
| the heading's set inside the body's | 1 (`docs/INCIDENT-LOG.md@434b727:30`: heading `AF-AP-192`, `AF-AP-193`; the body adds `AF-AP-39`) |
| the body's set inside the heading's | 0 |
| other | 1 (`docs/INCIDENT-LOG.md@434b727:38`: heading `AF-AP-188`, body `AF-AP-187`) |

**Leaks (amendment item 8).** Flagged per row in its sources (`"leak": "<kind>"`, kinds joined by `+`); no row is left out.

| Kind | Rows | Sources by kind and provenance |
|---|---|---|
| `ap-id`: an AF-AP id in the state | 126 | commit `not-cited` 68, incident unlabeled 32, incident `not-cited` 24, commit `registry-commit` 1, commit `commit-subject` 1 |
| `row-name`: the positive row's registry name, verbatim, in the query | 33 | commit `registry-commit` 29, incident `body-cite` 4 |
| `blocking-words` | 35 per v1 question | `verifier-class` 36 per question (a merged row has two sources) |
| `class-word`: a class word left after the mask | 1 per v1 question | `verifier-class` 1 per question |

All 126 `ap-id` rows hold the id in the chunk (the candidate row's own registry text), none in the query: the query's ids
are masked. The one `class-word` row holds the plural `blockers` (the leak rule reads plurals; the mask does not).

**Not admitted** (the builder's counts; decide-harvest refuses the same records, except `restated`):

| Reason | Records |
|---|---|
| `no-title-column` (F14: 30 rows with a class word; 48 whose "class" column holds no class word) | 78 |
| `restated` | 17 |
| `ambiguous-class` | 6 |
| `bad-finding-id` | 6 |
| `bad-class` | 3 |
| `bad-title` | 0 (was 66; all 66 are F1 lines, now admitted) |

**Block ends.** One block is capped at 60 lines: `F1 — BLOCKER` at `tasks/briefs/s0-05-support/VERIFY-E1-R1-report.md@434b727:110`
(lines 110-169); both of its rows carry `"block_end": "cap"`. The three pinned lines, tested at the PIN: N5m:13 ends
at line 19, before `Reproduced controls` (so also before the graft banner); b4:127 ends at line 137, before `Named mutant
disposition` (so also before `Retro:`); J1-2-R1:82 keeps its body through line 127 and stops at `### F2 — FOLLOW-UP`.

## 11. Evidence demands 4-7: tests, smoke, mutants, gates

**4. Tests.** `bash scripts/test_summary.sh tests/test_decide_harvest.py tests/test_laya_ft.py tests/test_recorded_labels.py`
(the sandbox venue: the Laya venv tests run). Set id: `3 files set=5d6a3ce56265` (`scripts/pc_suite.sh set-id -- <the
three files>`; the same id from `printf ... | sort | sha256sum | cut -c1-12`). The `common.py` tests are in
`tests/test_laya_ft.py`, as amendment item 1 says.

| Run | Tree | Result (pasted) |
|---|---|---|
| 1 | HEAD 8aa05a8 + the lane's files | `143 passed in 354.77s (0:05:54)` |
| 2 | the same | `143 passed in 369.01s (0:06:09)` |
| 3 | HEAD e6bab18 (after the coordinator's three commits) + the lane's files | `143 passed in 369.38s (0:06:09)` |

Per file: `tests/test_decide_harvest.py` 90 (67 existing + 23 new), `tests/test_laya_ft.py` 42 (33 existing + 9 new),
`tests/test_recorded_labels.py` 11. Both test files only gain lines (0 deleted), so every existing test runs unchanged.
The two named regressions pass in every run: the 369-row fixture
(`test_pin_rows_are_the_regression_fixture_and_the_families_only_add_rows`) and version 1's bytes
(`test_version_1_is_byte_identical_and_still_loads`: `d7cd9b49...` at 0b342c7, and the 1788 rows load through
`load_dataset`). Adjacent consumers (`tests/test_decisions_no_model.py`, `tests/test_decisions_ledger.py`,
`tests/test_decisions_redaction_properties.py`, `tests/test_no_laya_in_gates.py`, `tests/test_edit_snapshot_ap_screen.py`),
once: `448 passed in 74.96s (0:01:14)`.

**5. CPU smoke.** The brief's command, on the version-2 dataset (`f1b92d6f...`) and the recorded labels (`0098e52e...`):
`/root/venv-laya-probe/bin/python scripts/laya_ft/train.py --dataset <v2> --labels <labels> --out $S/smoke --mode head
--device cpu --epochs 1 --batch-size 2 --limit 8`.

- rc 0. `epoch 1/1 loss 0.708023 (4 steps, 29 s)`.
- Examples: n 8 (`v1.blocking` 4, `v1.finding_class` 4). **8 of the 8 rows joined a label.** No stale label: `join_labels`
  raises on one, and it did not.
- Labels: `records 5301, torn 0, duplicates 0, used 8`, teachers `{"recorded @ verifier-class": 8}`.
- Guards: `act_head_unchanged`, `encoder_unchanged`, `model_dir_unchanged` all true.

The first 8 rows are findings, so the brief's smoke never reads an ap label. An extra smoke (not the brief's command) ran
8 ap labels (4 commit rows, 4 incident rows; 1 `heading-cite+body-cite`, 7 `not-cited`): rc 0,
`epoch 1/1 loss 1.002937 (4 steps, 35 s)`, 8 ap examples, guards true. Both checkpoints (105 MB each) were deleted after
the read; the two `train-manifest.json` files stay in `$S/smoke/` and `$S/smoke-ap/`.

**6. Mutants** (on a shared scratch clone, `$S/mut`, removed after; each file restored from a pristine tar, and every
mutated file checked byte-identical to the shared tree after the restore). Control, the five named tests with no mutant:
`5 passed in 12.54s`.

| Mutant | Named test | Red for |
|---|---|---|
| a: a family admitted without a class word (F3's class group widened to any word) | `test_a_line_with_an_id_and_no_class_word_is_not_admitted` | `assert ['F-1', 'F-2', 'F4'] == ['F-1', 'F-2']` |
| b: a held-out text let through (the text-overlap exclusion off) | `test_heldout_text_is_left_out_wherever_it_is_planted` | the PC twin's `F-2` is admitted |
| c: a target that is not one-hot (0.9 / 0.1) | `test_the_target_is_one_hot_on_the_recorded_answer_and_reads_back` | red, but through the tool's own read-back guard: `the answer {'noul': 0.9} does not read back as its target` |
| c2: one-hot on another option (answer and target agree, so the guard passes) | the same | `assert [1.0, 0.0, 0.0, 0.0, 0.0, 0.0] == [0.0, 1.0, 0.0, 0.0, 0.0, 0.0]` |
| d: version 1's output changed (`MASK_ID` `AF-AP-?` to `AF-AP-#`) | `test_version_1_is_byte_identical_and_still_loads` | red, but the build failed before the byte check (a traceback; read then as the held-out gate) |
| d2: version 1's states changed (`.strip()`; the gate untouched) | the same | `assert 'cd32be5bfef2...412c56a3c1358' == 'd7cd9b49abac...9520b085cea1c'` |
| e: a commit linked to a held-out entry let through | `test_a_commit_that_adds_a_heldout_entry_is_held_out_and_the_loader_is_the_backstop` | `assert 0 == 1` (the excluded-commit count) |

c and d went red, but not on the named assertion, so c2 and d2 prove those assertions discriminate. The loader half of
item 2 (a planted row that names a held-out entry) is the same test's second part: `HeldOutLeak` from the real
`check_no_heldout`.

**7. Gates** (re-run 03:0xZ on the final files):

- pyflakes: 0 on all 7 code files.
- `python3 scripts/no_laya_in_gates.py`: `no_laya_in_gates: 41 files scanned, clean`, rc 0.
- Separators (`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`): 0 in every file I wrote (the 7 code files, the 3 record files and
  this report). `tests/test_decide_harvest.py` holds 7, all older than this lane: the PIN's copy holds 7, and my added
  lines hold 0.
- `scripts/lint_delta.py --base HEAD`: three advisory tells, each read. AP-51 (a byte-identity claim; no dataclass here
  feeds an `asdict` sink). AF-AP-72 (`int(f[1:])` sorts the family names in a parametrize list; no upstream field).
  AF-AP-175 (the tests pass `"HEAD"` of a private temp repo; the production path resolves the ref once,
  `scripts/laya_ft/build_dataset.py:278` `rev-parse`, and reads by that sha).
- GitNexus: `impact` on `row_identities` and `check_no_heldout` is HIGH (the loader serves `train.py` and
  `teacher_label.py`, and now `recorded_labels.py`); I warn here as the rule says. `detect-changes`: 5 files, 69 symbols, 13 processes, risk high.
  GitNexus does not index `scripts/decide-harvest` (no `.py` suffix); graft and a text search show one caller of
  `_finding_candidates`, `_candidates` (`scripts/decide-harvest:1030` `_finding_candidates(source=source`).
- report_lint on this report: the summary line is pasted at the end of section 12.

## 12. Files, deviations, adjacent defects, NOT-done, self-attack

**Files changed** (nothing committed; `git diff --numstat HEAD`):

- `scripts/laya_ft/common.py` (+9 -2): `SAMPLED_KINDS` at `scripts/laya_ft/common.py:63`.
- `scripts/laya_ft/common.py:186-187`: `row_identities` learns `ids.add(("commit", s["commit"]))`.
- `scripts/laya_ft/common.py:202`: `check_no_heldout` looks up a kind in `SAMPLED_KINDS` strictly; any other kind reads empty.
- `scripts/decide-harvest` (+261 -4): the families at `scripts/decide-harvest:403-437` (`FAMILY_ANCHORS`, `BLOCK_CAP`).
- `scripts/decide-harvest:441`: `class FamilyFinding`.
- `scripts/decide-harvest:495`: `def _family_block_end`.
- `scripts/decide-harvest:530`: `def _family_findings`.
- `scripts/decide-harvest:597-659`: `def _grammar_records` (the grammar's two loops, moved verbatim).
- `scripts/decide-harvest:662-765`: `def _finding_candidates` now reads `_grammar_records`, adds the family candidates
  from line 718, and sorts by line (stable) at `scripts/decide-harvest:764` `candidates.sort`.
- `scripts/laya_ft/build_dataset.py` (+387 -2): the block `version 2 (task #251` starts at `scripts/laya_ft/build_dataset.py:136`;
  `PROVENANCES`, `LEAKS` and `AP_ID_LEAK` sit at `scripts/laya_ft/build_dataset.py:141-149`.
- `scripts/laya_ft/build_dataset.py:275`: `def collect_v2`.
- `scripts/laya_ft/build_dataset.py:409`: `def flag_leaks`.
- `scripts/laya_ft/build_dataset.py:543`: `def build_v2`.
- `scripts/laya_ft/build_dataset.py:584`: `def build` takes `version=1`; the two deleted lines are its old signature and
  `main`'s old call, and `scripts/laya_ft/build_dataset.py:628` adds `--version`.
- `scripts/laya_ft/recorded_labels.py` (new, 113 lines): `scripts/laya_ft/recorded_labels.py:28` `def label_record`.
- `scripts/laya_ft/recorded_labels.py:46`: `def recorded`.
- `tests/test_decide_harvest.py` (+282, lines 1145-1426), `tests/test_laya_ft.py` (+268, lines 1081-1348),
  `tests/test_recorded_labels.py` (new, 183 lines).
- The record: `docs/research/findings/laya-ft-labels/2026-09-25-recorded/` (3 files, section 10). This report.
- Not mine: `tests/test_transcript_export.py` (+128) is the SESSION-EXPORT lane's (task #252);
  `docs/research/findings/laya-ft-data/JEV-INTEGRATION-MAP-2026-09-25.md` and
  `tasks/briefs/jev-laya/SESSION-EXPORT-report.md` are other lanes' files. I did not touch them.

**Deviations (flagged; each is a choice you may overrule):**

1. **`_grammar_records` is a move inside decide-harvest.** The grammar's two record loops left `_finding_candidates` for
   a function of their own, word for word, so the builder reads the same records. None of the helpers `j2c._blocks` calls
   changed (the AST test). Proof that the move changed nothing: the 369 rows keep their sha and their order.
2. **18 new `ap.violates_row` rows in decide-harvest.** A family finding whose title (or F13 row) names an AF-AP id makes an
   ap row, as the grammar already does for its findings. The brief asked for finding formats only. The fixture test pins
   the 18.
3. **A new refusal reason, `ambiguous-class`** (6 lines), and a new state, `restated` (17: neither admitted nor refused).
   decide-harvest's stdout does not count restatements; the builder's manifest does.
4. **Commit provenance is per row, not per commit.** A commit that adds AF-AP-5 and names AF-AP-3 in its subject labels
   the AF-AP-5 row `registry-commit` and the AF-AP-3 row `commit-subject`. The amendment says "a commit that meets both
   gets `registry-commit`"; for the rows the commit adds, the result is the same.
5. **A row cited only in the body of an admitted commit gets no label** (15 rows). It is cited, so `not-cited` would be
   false; the body is not admitted, so `true` would break amendment item 2.
6. **Every registry-adding commit is admitted, whatever its message says** (unless a held-out link excludes it). The 143
   registry-adding commits add {1: 105, 2: 26, 3: 7, 4: 3, 5: 1, 6: 1} rows. In the dataset, 65 commits give
   `registry-commit` positives: 46 give 1, 16 give 2, 2 give 3, and one (b341e48) gives 4 from one message.
7. **I ran `scripts/pc_suite.sh set-id`.** The dispatch lists `pc_suite.sh` under "no PC bridge"; demand 4 names this
   command. I read its branch first: `set-id` calls a local function, `set_id`, and nothing else
   (`scripts/pc_suite.sh:121-122`, `set_id "$@"`). The same id also comes from a plain shell pipe.
8. **The record holds no `dataset.jsonl`.** The brief's record list names the manifest, the labels and a summary. The
   dataset rebuilds from the PIN (12.8 MB).
9. **`summary.json` in the record is `recorded_labels.py`'s summary.** It holds the label counts, the manifest's count
   blocks and the builder's own `summary.json` whole.
10. **The `class-word` leak rule reads plurals** (`blockers`); `j2c._mask` does not mask them. 1 row per v1 question.
11. **F13 states are the title cell only** (version 1's rule for a table row), not a block. The brief asks for "the whole
    finding block"; a table row has no block.
12. **GitNexus rates the two `common.py` symbols HIGH.** The change there is the two lines the amendment names, and the
    version-1 dataset still loads.

**Adjacent defects and risks (reported, not fixed):**

1. **The SESSION-EXPORT lane can turn two of these tests red.** `scripts/transcript_export.py` is in the builder's
   `CODE` (`scripts/laya_ft/build_dataset.py:44-46`), and its `scrub` scrubs every state. Task #252's boundary MODIFIES that file.
   `test_version_2_record_rebuilds_byte_identically_at_the_pin` compares the whole manifest, `code` hashes included, so ANY
   byte change there makes it red until the record is rebuilt. A change in `scrub`'s output would also move version 1's
   bytes (`d7cd9b49`) and turn `test_version_1_is_byte_identical_and_still_loads` red.
   **Measured, 03:14Z: it has happened.** At 03:1xZ the #252 lane's edit was in the tree (`scripts/transcript_export.py`
   +45 lines, sha256/16 `d0f7037f19c25c90`; HEAD's and the record's is `f63cd97ef441b817`). It adds `scrub_payload` and
   `scrub_strict` beside `scrub` and leaves `scrub` as it is. Result on that tree: the version-2 test fails, `1 failed, 1
   passed in 85.61s (0:01:25)`, at the manifest compare (`At index 707 diff: b'd' != b'f'`); the version-1 test passes.
   A rebuild on that tree (`$S/v2-now`, rc 0, 38 s) differs from the record in ONE manifest field,
   `code/scripts/transcript_export.py`; the dataset (`f1b92d6f...`), the builder's summary and so the labels are
   unchanged. The fix is one regenerated file: `dataset-manifest.json` from `build_dataset.py --version 2 --commit
   434b727` on the final #252 bytes, in the SAME commit as #252's `transcript_export.py` (AF-AP-56's rule for attested
   inputs). If DSV2 is committed first, its record matches HEAD's `transcript_export.py` and its tests pass there.
   Any later edit to `scripts/decide-harvest`, `build_dataset.py`, `common.py`, `j2c.py`, `v1_probe.py` or `ap_probe.py`
   has the same effect (D-4 by construction).
2. **An unbalanced code fence** in `tasks/briefs/s0-05-support/VERIFY-E3-R1-report.md` (a closer at line 102 with no opener
   after line 90). Nothing here tracks fences; a reader that does would hide that report's 9 findings.
3. **Finding shapes no family reads** (section 9): a bracketed class, a bold class-id with no bullet, an indented numbered
   item. About 50 findings (inferred).
4. **decide-harvest's stdout does not count restatements** (17 at the PIN).

**NOT done:**

- No PC run and no CI run (no bridge, by rule). The two byte tests need the Laya venv and model: they run in the sandbox
  venue only, and CI skips them by the existing declaration (the `laya_venue` fixture).
- `scripts/lane_gate.sh` was not used: its `git archive` copy has no history, so the PIN tests cannot run there (the PIN is
  a declared input; the test helper fails loud when git lacks the PIN).
- The record holds no `dataset.jsonl` (deviation 8).
- The phrase rule for body-only citations (amendment item 2 makes it a later increment).
- The precision read has one reader and 20 lines; the recall read is a sample of 12.
- Nothing fence-aware; the missed shapes of section 9 stay missed.
- What to do with leak-flagged rows (task #238's decision).
- No verify round (the coordinator's rule 0f).

**Self-attack: the three most likely ways this work is wrong.**

1. *The families changed what decide-harvest admitted before.* Ruled out at the PIN by
   `test_pin_rows_are_the_regression_fixture_and_the_families_only_add_rows`: the PIN script's 369 rows
   (`c4589e0d77a97d9b`) are an ordered subsequence of the new rows, the additions are exactly 726 + 18, and the refusals
   are the listed counts. Also by the AST test on the helpers `j2c._blocks` calls, and by version 1's bytes (`d7cd9b49`,
   rebuilt with the new code; mutant d2 proves that test discriminates).
2. *A held-out finding or entry reaches a training state* by identity, through a commit, or as text in another report.
   Ruled out for identity (100 of 100 findings, 100 of 100 entries), for linked commits (82 excluded; mutant e red), and
   for contained text (0 hits at the PIN on every final row; planted texts in a PC twin and in a Q-7 title are caught;
   mutant b red). The loader's gate at train time is the backstop (a planted row raises `HeldOutLeak`). Not ruled out: a
   paraphrase or a partial quote passes the containment test, and 4 short J2 v1 titles are not tested.
3. *A label is wrong*: a family reads the wrong class, or a block runs into the next finding. Partly ruled out: precision
   20/20 by rule and by my read; the slot rule on three real lines; the three pinned block ends and the cap. Not ruled out:
   one capped block (the cap cuts; it does not choose the end), no fence tracking, and `not-cited` negatives that are
   false where an entry violates a row it does not name (amendment item 3 accepts this; J2 scores the same truth).

Report lint, 2026-09-25 03:12Z, after two rounds (the first found 1 MISS and 2 UNCHECKABLE, all fixed):
`report_lint: 68 refs — OK 68, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`. Separator bytes in this report: 0.
