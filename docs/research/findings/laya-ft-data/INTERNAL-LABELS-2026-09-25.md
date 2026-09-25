# INTERNAL-LABELS 2026-09-25: the OpenJev label audit and the labeled data our own records hold

Task #233 (owner ask 2026-09-25), brief `tasks/briefs/jev-laya/DATA-INT-brief.md`. Role: evidence-gatherer (EXPLORE lane,
sandbox, Opus 5.5). This report measures and tabulates. It holds no verdict and no recommendation.

STATUS: COMPLETE for this lane, with the NOT-done list in section 5. Written incrementally 2026-09-25 00:45Z-01:15Z
(`date -u`). The only file this lane wrote in the repo is this report (`git status --porcelain` with
`GIT_OPTIONAL_LOCKS=0` lists it as the one untracked path; no `.pyc` newer than 00:45Z exists in the tree).

Headline numbers (details and methods below):
- Rebuild: `dataset.jsonl` sha256 `d7cd9b49...5cea1c` from three rebuilds, EQUAL to the manifest; eb256f49 and 0b342c7
  are the same tree (`124dd637...`), the local pre-push commit and its trailer-stripped rewrite.
- `v1.finding_class`: OpenJev's choice equals the verifier's class on 38/86 (0.4419); the majority class alone scores
  49/86. `v1.blocking`: 72/86 at 0.5 (TP 1, FN 2, FP 12, TN 71); answering "false" everywhere scores 83/86.
- `ap.violates_row`: 49 of 101 entries cite a registry row (69 positive rows, base rate 0.0427); OpenJev's order puts a
  cited row first for 17/49 entries (top-3 29/49), the lexical order 26/49 (33/49); 52 entries cite nothing.
- Goal 2: 811 new class-tagged findings (26 admitted by decide-harvest's grammar, 785 in the 11 other formats of 3.2
  that matched), 221 new AP rows at HEAD (10 positive), 326 id-anchored findings with no class word, plus decision
  records (3.1).

Scratch directory for every artifact named below:
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/data-int/` (called `$S` below).
Local HEAD at start: `5d7385a0fba0171c85539092c2134306701987a5` (2026-09-25T00:45:20Z), branch
`claude/soundbox-kit-migration-iz1jwf`.

## 0. Enumeration (the cells this report must fill)

| # | Cell | Section |
|---|---|---|
| E1 | the rebuild's `dataset.jsonl` sha256 against the manifest | 1 |
| E2 | which commit the rows were built from; eb256f49 vs `ds-0b342c7` | 1 |
| E3 | truth recovery per question type (recoverable, and why not) | 2.1 |
| E4 | `v1.finding_class`: accuracy, confusion, class counts | 2.2 |
| E5 | `v1.blocking`: accuracy at 0.5, outcome rates, score distribution per truth | 2.3 |
| E6 | `ap.violates_row`: per-entry top-1/top-3 (OpenJev, lexical), base rate | 2.4 |
| E7 | Goal 2 (a) verify and PC lane report findings not in the dataset | 3 |
| E8 | Goal 2 (b) incident entries and registry rows after the dataset's commit | 3 |
| E9 | Goal 2 (c) commit messages with findings or decisions | 3 |
| E10 | Goal 2 (d) chat digests and raw transcripts | 3 |
| E11 | Goal 2 (e) decide-harvest row kinds and counts on the current tree | 3 |
| E12 | adjacent defects and contradictions seen (recorded, not fixed) | 4 |
| E13 | NOT-done | 5 |

## 1. The rebuild (evidence demand 1) and the commit question

Environment for every Python run in this report: `PYTHONDONTWRITEBYTECODE=1` (no `__pycache__` writes in the tree),
`HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`; the builder reads every SOURCE through `git rev-parse`, `git ls-tree` and
`git show <sha>:<path>` (`scripts/laya_ft/build_dataset.py:42-72`); it imports its helper modules from the worktree it
runs from and hashes them into the manifest (`build_dataset.py:226`). Code extracted for the second rebuild came from
`git archive ee09d94 ... | tar -x -C $S/code-ee09d94` (read-only).

| Rebuild | Code | `--commit` | rc | `dataset.jsonl` sha256 | bytes | vs manifest `d7cd9b49...5cea1c` | SOLID/UNSURE |
|---|---|---|---|---|---|---|---|
| R1 (the brief's exact command) | current tree (`build_dataset.py` sha `8dbba45c320a`, commit f1679db 2026-09-24T19:40Z) | `eb256f49c0ee...` | 0 | `d7cd9b49abac267bb9b5290641ea353180a9a61047ce6c590809520b085cea1c` | 4077876 | EQUAL | SOLID |
| R2 | the manifest's own code: all 7 `code` hashes equal the manifest's (`build_dataset.py` sha `b9c29b4a06ee`, commit ee09d94 2026-09-24T17:10Z) | `eb256f49c0ee...` | 0 | `d7cd9b49...5cea1c` | 4077876 | EQUAL; its `manifest.json` is BYTE-IDENTICAL to the committed `dataset-manifest.json` (`cmp` rc 0) | SOLID |
| R3 | current tree | `0b342c7a2931...` | 0 | `d7cd9b49...5cea1c` | 4077876 | EQUAL | SOLID |

Commands (R1; R2 and R3 differ only as the table says):

```
cd /home/user/agent-factory && export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
/root/venv-laya-probe/bin/python scripts/laya_ft/build_dataset.py --out $S/rebuild-eb256f49-current \
    --commit eb256f49c0ee87a6ff2d122dcf13d6db6a70bc3f            # 23.9 s wall, rc 0
/root/venv-laya-probe/bin/python $S/code-ee09d94/scripts/laya_ft/build_dataset.py --repo /home/user/agent-factory \
    --out $S/rebuild-eb256f49-ee09d94code --commit eb256f49c0ee87a6ff2d122dcf13d6db6a70bc3f
/root/venv-laya-probe/bin/python scripts/laya_ft/build_dataset.py --out $S/rebuild-0b342c7-current \
    --commit 0b342c7a29317d611a7f415eb411802276533f1a
sha256sum $S/rebuild-*/dataset.jsonl     # three lines, all d7cd9b49abac267bb9b5290641ea353180a9a61047ce6c590809520b085cea1c
```

Manifest differences (`diff` of `json.tool --sort-keys` output against the committed
`docs/research/findings/laya-ft-labels/2026-09-24-openjev/dataset-manifest.json`):
- R1: the `build_dataset.py` code hash (`8dbba45c...` vs `b9c29b4a...`) and one added key `"repeated_finding_ids": 0`
  (the f1679db fix, AF-AP-199). Every count, the commit and the dataset block are equal.
- R2: no difference (byte-identical file).
- R3: the same two lines as R1, plus `"commit": "0b342c7a..."` in place of `"eb256f49..."`.

The commit question (the brief's open question), as measured:

| Fact | Evidence | SOLID/UNSURE |
|---|---|---|
| `eb256f49c0ee87a6ff2d122dcf13d6db6a70bc3f^{tree}` = `124dd63759c37c09a12bb0c9de6c57a2e681e02d` | `git rev-parse` | SOLID |
| `0b342c7a29317d611a7f415eb411802276533f1a^{tree}` = `124dd63759c37c09a12bb0c9de6c57a2e681e02d` (the same tree) | `git rev-parse` | SOLID |
| Both commits: subject "VERIFY-FT1 brief: the independent verify of the Laya fine-tune tooling (task #233, rule 0f)", author and committer time 1790270071 (2026-09-24T17:14:31Z) | `git cat-file -p` | SOLID |
| eb256f49 carries 2 trailer lines (`Co-Authored-By`/`Claude-Session`) and a `gpgsig`; parent `83c03f8f...`. 0b342c7 carries 0 trailer lines, no `gpgsig`; parent `559a7da8...` | `git cat-file -p ... \| grep -c -i -E '^(Co-Authored-By\|Claude-Session):'` | SOLID |
| 0b342c7 is an ancestor of HEAD; eb256f49 is not (`git merge-base --is-ancestor`); no branch contains eb256f49; it survives in the reflog (3 reflog lines: `commit: VERIFY-FT1 brief...` and `reset: moving to HEAD`) | `git branch -a --contains`, `git reflog --all` | SOLID |
| The ledger records the labeling run "on a dataset built at local eb256f4 (tree 124dd63759c37c09a12bb0c9de6c57a2e681e02d, dataset sha256 d7cd9b49abac267b...)" | `todo/BUILD-TASKLIST.md:1460` | SOLID (as a record of the claim) |
| The PC training jobs read `--dataset ~/laya-ft/ds-0b342c7` | `tasks/briefs/jev-laya/window1.jobs:5`, `tasks/briefs/jev-laya/VERIFY-GW1-brief.md:65` | SOLID (as text) |
| The PC's `ds-0b342c7/manifest.json` and its `dataset.jsonl` bytes | not read: the PC bridge is out of scope for this lane | UNKNOWN (records only: `wiki/topics/live-state.md:77` "rebuilt on the PC (sha d7cd9b49, identical)"; `transcripts/sandbox/chat-2026-09-24.md:5183`) |

Reading of the rows above, as facts only: eb256f49 is the local pre-push commit and 0b342c7 its trailer-stripped
rewrite (the `push_clean.sh` pattern); the builder reads only the tree, and the three sandbox rebuilds from either name
give the same `dataset.jsonl` bytes. A manifest built at `--commit 0b342c7` names `0b342c7` in its `commit` field (R3), so
the committed manifest (which names eb256f49) came from a build at eb256f49; the PC directory's own manifest was not read.
Every Goal 1 number below uses the R2 rebuild (`$S/rebuild-eb256f49-ee09d94code/dataset.jsonl`); R1 and R3 are the same bytes.

## 2. Goal 1: the label audit

Producer: `$S/audit_goal1.py` (run `PYTHONDONTWRITEBYTECODE=1 /root/venv-laya-probe/bin/python $S/audit_goal1.py $S`,
rc 0). It loads the R2 rebuild with the trainer's own loader `C.load_dataset` (sha check, held-out check), the labels
with `C.read_labels`, and joins them with `C.join_labels` (refuses a stale label). Every source text is
`git show eb256f49...:<path>`. Outputs: `$S/goal1_summary.json` (every number below), `$S/goal1_v1_rows.json` (86 findings,
truth and OpenJev answers per finding), `$S/goal1_ap_entries.json` (101 entries, cited rows, both orders, scores).

Join: 1788 dataset rows, 1788 label records (0 torn, 0 duplicate keys), 1788 joined, 0 rows without a label, 0 labels
without a row, 0 stale labels; every row has exactly 1 source. All 1788 labels: model `openjev-0.1`, endpoint
`api.codiv.ai`; 1787 took 1 attempt, 1 took 2. SOLID.

The counts as the producer printed them (`$S/goal1_summary.json`, five lines pasted from a `json.dumps` of it):

```
{"n": 86, "accuracy": "38/86", "balanced_accuracy": 0.4288, "per_class_recall": {"BLOCKER": "1/3", "FOLLOW-UP": "22/34", "INFO": "15/49"}, "truth_counts": {"BLOCKER": 3, "FOLLOW-UP": 34, "INFO": 49, "UNVERIFIED": 0, "CONTRACT-DEFECT": 0, "KNOWN": 0}, "openjev_choice_counts": {"BLOCKER": 12, "FOLLOW-UP": 54, "INFO": 17, "UNVERIFIED": 0, "CONTRACT-DEFECT": 2, "KNOWN": 1}}
{"BLOCKER": 1, "FOLLOW-UP": 2, "INFO": 0, "UNVERIFIED": 0, "CONTRACT-DEFECT": 0, "KNOWN": 0} {"BLOCKER": 8, "FOLLOW-UP": 22, "INFO": 2, "UNVERIFIED": 0, "CONTRACT-DEFECT": 1, "KNOWN": 1} {"BLOCKER": 3, "FOLLOW-UP": 30, "INFO": 15, "UNVERIFIED": 0, "CONTRACT-DEFECT": 1, "KNOWN": 0}
{"n": 86, "truth_true": 3, "truth_false": 83, "accuracy_at_0.5": "72/86", "TP": 1, "FN": 2, "FP": 12, "TN": 71, "noul_when_truth_true": {"n": 3, "min": 0.0263, "q1": 0.1231, "median": 0.2199, "q3": 0.4988, "max": 0.7777, "mean": 0.3413}, "noul_when_truth_false": {"n": 83, "min": 0.0006, "q1": 0.0074, "median": 0.0394, "q3": 0.2357, "max": 0.9973, "mean": 0.1842}}
{"entries": 101, "entries_citing_a_registry_row": 49, "entries_with_a_cited_row_in_16": 44, "positive_rows": 69, "rows": 1616, "base_rate": 0.0427}
{"openjev": {"top1_over_entries_citing": "17/49", "top3_over_entries_citing": "29/49"}, "lexical": {"top1_over_entries_citing": "26/49", "top3_over_entries_citing": "33/49"}}
```

### 2.1 Truth recovery per question type (E3)

| Question type | Rows | Truth recoverable | How it was recovered | Cross-checks | Rows without a truth, and why |
|---|---|---|---|---|---|
| `v1.finding_class` | 86 | 86 | the class `j2c._blocks` (decide-harvest's grammar: `BULLET_FINDING_RE` group `class`, or `_parse_class` of a table's class cell) returns for `sources[0].path` + `finding_id`, first block | (1) decide-harvest's own `_finding_candidates` on the same blob gives the same class for 86/86; (2) the row's state equals `scrub(_mask(block))` of that block for 86/86 (the join hit the right block); (3) 0 ids with a repeated block | 0 |
| `v1.blocking` | 86 | 86 | truth = the class above in `BLOCKING = {"BLOCKER", "CONTRACT-DEFECT"}` (`v1_probe.py:33`) | as above | 0 |
| `ap.violates_row` | 1616 (101 entries x 16) | 1616 as a citation fact | truth = the candidate `row` is among the AF-AP ids (`ap_probe.AP_ID`) named in the whole entry (`lines[i:entry_end(lines, i)]` of `docs/INCIDENT-LOG.md` at eb256f49; `entry_end` is the builder's), intersected with the 193 registry rows at that commit | the masked heading at `sources[].line` equals `sources[].heading` for 101/101; the recomputed lexical top 16 (`build_dataset.rank` on the uncut query) equals the dataset's candidate order for 101/101; 0 entries name an id outside the registry | a POSITIVE exists for 49 entries (784 rows; 69 positive rows). 52 entries (832 rows) cite no registry row anywhere: all 16 rows read "not cited", and the entry has no row to rank. 5 of the 49 cite rows none of which is among their 16 candidates (80 rows, all "not cited"): lines 26 (AF-AP-132, AF-AP-175), 356 (AF-AP-16, AF-AP-18), 391 (AF-AP-57), 446 (AF-AP-37), 452 (AF-AP-75) |

Why the AP rows are like this (facts, SOLID): at eb256f49 the log holds 201 anchored entries; the heading names a
registry row in 107 and the whole entry names one in 149. The held-out AP sample (`ap-hawk-probe/sample.json`, built at
2ea5f62 2026-09-24T12:42Z, 184 registry rows) took 100 entries, all of them entries whose HEADING names a registry row
(`ap_probe.cmd_sample`: `if ids:`). So the 101 trainable entries are the rest: 94 of them name no row in the heading
(the 7 that do are lines 10-20, all dated 2026-09-24; none of their headings exists in the log at 2ea5f62, which held
193 entries). 99 of the 101 entries are one line; 1 is 2 lines; 1 is 5 lines. 2 entries carry the 32 window-cut rows
(16 each; the query was cut, never the chunk).

Label-definition variant (both measured; the concluding pass picks): ap_probe's own label and decide-harvest's
`_parse_incident` take the ids in the HEADING only. On that definition 7 entries cite a row (10 positive rows, base rate
10/1616 = 0.0062). 42 entries cite only in the body. Body citations mostly name the class the incident belongs to; the
last word before each id occurrence in those 42 entries: "row" 8, "registry" 7, "rows" 6, "confirmed" 4, "ap" 4, others
1-2 each (for example "(AF-AP-157's class, met again)", "Rule confirmed (AF-AP-132's second shape)"; one reads
"AF-AP-140's stale-marker case does not ..." at line 135). A body citation is therefore not always "this entry shows
this row"; the per-occurrence semantics were not hand-graded (NOT-done 2).

### 2.2 `v1.finding_class`: OpenJev's choice against the verifier's class (E4)

86 findings from 11 reports (VERIFY-JT3 24, VERIFY-J1-1-R4 18, VERIFY-COORD-0924 10, VERIFY-REPIN-a-R1 6,
VERIFY-J1-1-R2 6, VERIFY-AF-AP-127-R1-REPIN-a-R2 5, VERIFY-J1-0-R4 4, VERIFY-J1-0-R5 4, VERIFY-AF-AP-127 3,
VERIFY-J1-0-R6 3, VERIFY-J1-1-R3 3). OpenJev's `choice` equals the argmax of its stored target for 86/86.

| Measure | Value |
|---|---|
| accuracy (choice = truth) | 38/86 = 0.4419 |
| balanced accuracy (mean recall over the 3 classes present) | 0.4288 |
| per-class recall | BLOCKER 1/3, FOLLOW-UP 22/34, INFO 15/49 |
| truth class counts | BLOCKER 3, FOLLOW-UP 34, INFO 49, UNVERIFIED 0, CONTRACT-DEFECT 0, KNOWN 0 |
| OpenJev choice counts | BLOCKER 12, FOLLOW-UP 54, INFO 17, UNVERIFIED 0, CONTRACT-DEFECT 2, KNOWN 1 |
| reference: majority class (INFO) on the same rows | 49/86 = 0.5698 |
| reference: `v1_probe.heuristic` (the fixed RULES) on the same row states | 33/86 = 0.3837 |
| mean stored target probability on the truth class | 0.42 (min 0.0001, q1 0.0088, median 0.3829, q3 0.8087, max 0.9952) |
| blocking split implied by the choice (choice in BLOCKING = truth in BLOCKING) | 71/86 |

Confusion (rows = the verifier's class, columns = OpenJev's choice; classes absent from both are omitted):

| truth \ choice | BLOCKER | FOLLOW-UP | INFO | CONTRACT-DEFECT | KNOWN | total |
|---|---|---|---|---|---|---|
| BLOCKER | 1 | 2 | 0 | 0 | 0 | 3 |
| FOLLOW-UP | 8 | 22 | 2 | 1 | 1 | 34 |
| INFO | 3 | 30 | 15 | 1 | 0 | 49 |
| total | 12 | 54 | 17 | 2 | 1 | 86 |

### 2.3 `v1.blocking`: OpenJev's `noul` against class-in-BLOCKING (E5)

Prediction = `noul >= 0.5` (0 rows at exactly 0.5). The stored target is `[1 - noul, noul]` for 86/86.

| Measure | Value |
|---|---|
| truth true (BLOCKER or CONTRACT-DEFECT) / false | 3 / 83 |
| accuracy at 0.5 | 72/86 = 0.8372 |
| outcomes (count, rate over 86) | TP 1 (0.0116), FN 2 (0.0233), FP 12 (0.1395), TN 71 (0.8256) |
| recall on truth true; false alarms on truth false | 1/3; 12/83 |
| reference: answer "false" on every row | 83/86 = 0.9651 |
| `noul >= 0.5` agrees with OpenJev's own choice being in BLOCKING | 71/86 |

Score distribution per truth value:

| truth | n | min | q1 | median | q3 | max | mean |
|---|---|---|---|---|---|---|---|
| true | 3 | 0.0263 | 0.1231 | 0.2199 | 0.4988 | 0.7777 | 0.3413 |
| false | 83 | 0.0006 | 0.0074 | 0.0394 | 0.2357 | 0.9973 | 0.1842 |

| noul bin | [0,.1) | [.1,.2) | [.2,.3) | [.3,.4) | [.4,.5) | [.5,.6) | [.6,.7) | [.7,.8) | [.8,.9) | [.9,1] |
|---|---|---|---|---|---|---|---|---|---|---|
| truth true (3) | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| truth false (83) | 52 | 7 | 5 | 3 | 4 | 4 | 2 | 1 | 1 | 4 |

### 2.4 `ap.violates_row`: where the cited rows rank among the 16 candidates (E6)

OpenJev order = the 16 candidates sorted by `noul` descending, ties by row number (ap_probe `cmd_score`'s Jev sort; 0
entries have a tied score). Lexical order = the dataset's candidate order, which equals `build_dataset.rank` (ap_probe's
sort key) for 101/101 entries. A hit = the best-ranked cited row sits at rank 1 (top-1) or at rank 3 or better (top-3).

Whole-entry citations (the brief's definition):

| Measure | OpenJev `noul` | lexical order |
|---|---|---|
| entries citing a registry row | 49 | 49 |
| entries with a cited row among their 16 (recall@16, the ceiling for both) | 44 | 44 |
| top-1 hits, over the 49 / over the 44 | 17/49; 17/44 | 26/49; 26/44 |
| top-3 hits, over the 49 / over the 44 | 29/49; 29/44 | 33/49; 33/44 |
| best rank of a cited row (rank: entries) over the 44 | 1:17 2:9 3:3 4:4 5:1 7:4 8:1 9:1 13:1 14:2 16:1 | 1:26 2:5 3:2 4:2 5:2 7:2 8:2 12:1 13:1 16:1 |
| reference: random order, expected top-1 over the 44 | 0.098 | 0.098 |
| base rate of positive rows | 69/1616 = 0.0427 | same |

Heading-only citations (ap_probe's label rule): 7 entries cite, all 7 have a cited row in their 16; OpenJev top-1 4/7,
top-3 5/7; lexical top-1 5/7, top-3 5/7; base rate 10/1616 = 0.0062.

The per-row binary view at 0.5 (not asked by the brief; recorded because the trained target is the per-row `noul`):

| Citation rule | TP | FN | FP | TN | accuracy | noul when cited (median, mean) | noul when not cited (median, mean) |
|---|---|---|---|---|---|---|---|
| whole entry | 62 | 7 | 1021 | 526 | 588/1616 | 0.9491, 0.8572 (n 69) | 0.6756, 0.6076 (n 1547) |
| heading only | 9 | 1 | 1074 | 532 | 541/1616 | 0.9496, 0.8227 (n 10) | 0.6866, 0.6170 (n 1606) |

Other OpenJev score facts on the 1616 rows: 1083 rows score `>= 0.5`; all 101 entries have at least one row `>= 0.5`;
the per-entry maximum has min 0.6087, median 0.9727, max 0.9997. Not-cited rows by bin (whole entry, n 1547):
[0,.1) 112, [.1,.2) 106, [.2,.3) 102, [.3,.4) 103, [.4,.5) 103, [.5,.6) 126, [.6,.7) 163, [.7,.8) 194, [.8,.9) 251,
[.9,1] 287. Cited rows by bin (n 69): [.2,.3) 2, [.3,.4) 1, [.4,.5) 4, [.5,.6) 2, [.6,.7) 3, [.7,.8) 5, [.8,.9) 6,
[.9,1] 46.

## 3. Goal 2: what our own records could add

Every Goal 2 count reads the tree at ONE pinned commit, `5d7385a0fba0171c85539092c2134306701987a5` (the local HEAD at
start, 2026-09-25T00:45:20Z; `$S/HEAD.pin`), through `git show`/`git ls-tree`, except the raw transcripts (read from
disk, counts only). "New" = not among the dataset's 86 training findings or 101 entries, and not among the 100 + 100
held-out identities. Label origin: INCUMBENT = an answer our process already wrote down (the verifier's class, the
coordinator's AF-AP citation, a gate word, an owner message); TEACHER-NEEDED = no recorded answer for the question.

Producers (all under `$S`, all rc 0): `goal2a.py` (report findings; `goal2a_summary.json`, `goal2a_per_report.json`,
`goal2a_examples.json`), `goal2a_sample.py` (seeded precision read, `goal2a_precision_sample.txt`),
`goal2a_noclass.py`, the builder at HEAD (`rebuild-HEAD-current/`), `goal2c.py` (`goal2c_summary.json`), `goal2d.py`
(`goal2d_summary.json`), `goal2d_verifiers.py` (`goal2d_verifiers.json`), decide-harvest (`dh-head/`).

### 3.1 The Goal 2 table (evidence demand 3)

| # | Source | Question type | NEW examples (count) | Label origin | Command | SOLID/UNSURE |
|---|---|---|---|---|---|---|
| a1 | `VERIFY-*-report.md`, findings decide-harvest's grammar admits | `v1.finding_class`, `v1.blocking` | 18 findings (FOLLOW-UP 9, INFO 9), all in 1 report new after eb256f49 (`VERIFY-JT3-R1-report.md`) = 36 rows | incumbent (the verifier's class) | `goal2a.py`; cross-check: the builder at HEAD has 104 findings = the 86 training keys kept + 18 new keys | SOLID |
| a2 | `tasks/briefs/pc/report-pc-verify-*.md`, admitted grammar | `v1.*` | 8 findings (FOLLOW-UP 2, INFO 6), 1 report (`report-pc-verify-k1-h.md--5276976.md`); the builder's `REPORT_RX` does not read this path set, decide-harvest does | incumbent | `goal2a.py`; `dh-head/ledger.jsonl` (8 v1 rows with a `/pc/` source) | SOLID |
| a3 | `VERIFY-*-report.md`, finding anchors in formats the grammar does not admit (families in 3.2) | `v1.*` | 735 distinct (report, id) findings with a class word: FOLLOW-UP 298, INFO 353, BLOCKER 62, CONTRACT-DEFECT 10, UNVERIFIED 11, KNOWN 1; 587 in reports that existed at eb256f49, 148 in the 9 new reports | incumbent (the class word on the verifier's own anchor line, read by regex) | `goal2a.py` | UNSURE (regex; see 3.2 for the precision read and the dedup rule) |
| a4 | `report-pc-verify-*.md`, formats not admitted | `v1.*` | 50 (FOLLOW-UP 26, INFO 17, BLOCKER 7), in 10 of 30 reports | incumbent | `goal2a.py` | UNSURE |
| a5 | `VERIFY-*-report.md`, anchors tagged only BLOCKING / NON-BLOCKING (no class word in the first 80 characters) | `v1.blocking` only | 22 (BLOCKING 20, NON-BLOCKING 2) | incumbent for blocking; the class is teacher-needed | `goal2a.py` | UNSURE |
| a6 | the 59 verify reports (40 `VERIFY-*`, 19 `report-pc-verify-*`) with no class-tagged finding at all | `v1.*` | 326 distinct id-anchored items (F/V/VB/VR ids at a line-start anchor) in 23 of the 59 reports; the other 36 hold no such anchor | teacher-needed (no class word) | `goal2a_noclass.py` | UNSURE (includes verification items and restatements) |
| a7 | `tasks/briefs/pc/report-pc-*.md` (lane reports, not verify; 32, 1 new after eb256f49) | none of the three | 0 class-tagged findings; decide-harvest: 1 `wf.drift` row | incumbent (`wf.drift`) | `goal2a.py`; `dh-head/` | SOLID |
| b1 | `docs/INCIDENT-LOG.md` entries new after eb256f49 | `ap.violates_row` | 9 entries (201 -> 210) = 144 rows at 16 candidates each; 6 of 9 cite a registry row in the whole entry (2 in the heading); 5 have a cited row among their 16; 7 positive rows of 144 | incumbent citation for the 6; the 3 that cite nothing have no positive (teacher-needed for a positive) | builder at HEAD (`rebuild-HEAD-current`), key diff against R2 | SOLID |
| b2 | registry rows new after eb256f49 (193 -> 201: AF-AP-194 ... AF-AP-201) | `ap.violates_row` | 47 new (entry, row) candidate pairs in 36 of the 101 old training entries, every one of them a new registry row entering the lexical top 16 (AF-AP-197 14, -195 10, -199 7, -201 5, -200 4, -196 4, -194 3; -198 none), displacing 47 old pairs; 1 more entry changes only its candidate order; 30 more rows change key with the same (entry, row) pair because the entry text changed | incumbent citation fact (positive only where the entry cites the row) | same key diff | SOLID |
| b3 | the builder's own total at HEAD | all three | 1968 rows (ap 1760 = 110 entries x 16; v1 104 x 2); 257 keys not in the training dataset (ap 221, v1 18 + 18); 77 training ap keys gone | as b1, b2, a1 | `build_dataset.py --commit 5d7385a0...` (rc 0; dataset sha256 `1fc4fbea8928d47da09d989f7dfb92edcad23c34bc7f5151f072870311e3b03f`) | SOLID |
| c1 | commit messages, `git log 5d7385a0` (1568 commits; 115 in 0b342c7..HEAD) | decisions (not one of the three) | P1 `Rejected:` alternative 147 commits (8 after the dataset); P2 D-nnn 223 (16); P7 owner ruling cited 37 (3) | incumbent (the message states the decision); no extractor exists | `goal2c.py` | UNSURE (pattern counts) |
| c2 | same | `ap.violates_row`-like (a commit that names an anti-pattern row) | P3 AF-AP-n: 457 commits (41 after), 994 occurrences, 195 distinct ids, 736 commit-id pairs | incumbent citation; the state (message or diff hunk) would need building | `goal2c.py` | UNSURE |
| c3 | same | `v1.*`-like | P4 a finding id within 3 words of a class word: 25 commits (0 after), 36 occurrences | incumbent | `goal2c.py` | UNSURE |
| c4 | same | gate recommendation (not one of the three) | P5 gate word: 182 commits (14 after), 260 occurrences; 102 distinct (VERIFY-lane, gate word) pairs over 79 lanes (NOT-READY 62, MERGE-READY-WITH-FOLLOWUPS 24, MERGE-READY 12, CONTRACT-INVALID 4) | incumbent | `goal2c.py`; the pair regex below | UNSURE |
| d1 | committed digests `transcripts/sandbox/chat-*.md` (18 files, 3,142,816 bytes) | owner rulings; gate recommendations; findings | user turns 442 (268 not starting with an injected prefix, 174 injected); assistant turns 6060 (8 at the 4000-character cap); assistant turns with a gate word 186 (246 occurrences); 67 distinct (VERIFY-lane, gate word) pairs; class-tagged finding anchors 1 | incumbent | `goal2d.py` | UNSURE (prefix rule; turns are capped) |
| d2 | committed digests `transcripts/pc/*.md` (119 files, 5,910,043 bytes; 47 `pc-verify*`) | findings; gate words | class-tagged finding anchors: 3 in 2 `pc-verify*` files, 0 elsewhere; gate words 47 in `pc-verify*`, 11 elsewhere | incumbent | `goal2d.py` | UNSURE |
| d3 | raw main session transcript `-home-user/<session>.jsonl` (700,478,822 bytes, 127,473 lines) | owner rulings | 206 owner text messages (user records: not a tool result, not `isMeta`/`isCompactSummary`, not an injected prefix); the day histogram is in `goal2d_summary.json` | incumbent (the owner's words); ruling vs question vs acknowledgement NOT classified | `goal2d.py` | UNSURE |
| d4 | same | coordinator gate recommendations | 186 assistant text blocks with a gate word (249 occurrences); 66 distinct (VERIFY-lane, gate word) pairs: NOT-READY 44, MERGE-READY-WITH-FOLLOWUPS 19, MERGE-READY 2, CONTRACT-INVALID 1 | incumbent | `goal2d.py` | UNSURE (a restated verifier recommendation counts) |
| d5 | same | dispatches (structure) | 255 Agent dispatches: code-implementer 108, adversarial-verifier 96, evidence-gatherer 16, council-* 26, claude 4, general-purpose 4, no type 1; 0 `hive-scout` / `hive-reviewer` (so decide-harvest's `b1.*` / `b2.*` transcript rows would be 0 even if this JSONL were committed); 530 task notifications; 18,940 tool-result blocks | n/a | `goal2d.py` | SOLID (counts of JSON fields) |
| d6 | raw session `-home-user-agent-factory/<session>.jsonl` (1,583,665 bytes, 280 lines) | owner rulings | 17 owner text messages; 0 dispatches | incumbent | `goal2d.py` | UNSURE |
| d7 | raw subagent transcripts (289 under `subagents/`, incl. workflows: code-implementer 128, adversarial-verifier 110, evidence-gatherer 16, council-* 26, general-purpose 5, claude 4) | `v1.*`; gate recommendations | verifiers: 666 distinct class-tagged ids in 35 of 110 transcripts (text, handback, Write content, Edit new_string, Bash command); 599 of them in the 39 transcripts that wrote a VERIFY report path committed at HEAD (so inside a1/a3); 67 in 4 transcripts that wrote no committed report themselves (BLOCKER 5, CONTRACT-DEFECT 1, FOLLOW-UP 29, INFO 32), and for all 4 the dispatch description names a VERIFY lane whose `VERIFY-<lane>-report.md` is committed at HEAD (so these are very likely inside a1/a3 too; not proven id by id); final message carries a gate word in 85 of 110 (NOT-READY 61, MERGE-READY-WITH-FOLLOWUPS 26, MERGE-READY 11, CONTRACT-INVALID 4) | incumbent | `goal2d.py`, `goal2d_verifiers.py`, an inline lane-name check | UNSURE (regex families; overlap by report path and lane name only) |
| d8 | `docs/08_DECISION_LOG.md` at HEAD (where rulings land; not a chat log) | decisions / owner rulings | 82 table rows D-001 ... D-082; 52 name the owner | incumbent | inline count (3.4) | SOLID |
| e | `scripts/decide-harvest` on the current tree (read-only, `--out $S/dh-head/ledger.jsonl`) | see 3.3 | 369 rows: `v1.finding_class` 213, `ap.violates_row` 153, `wf.drift` 3, `b1.*`/`b2.*`/`d1.*` 0 | incumbent only (it writes positives: "negatives: 0 (hand-labeled in J2)") | 3.3 | SOLID |

Totals by question type (sums of the rows above; the chat-log and commit rows overlap the reports and are not added):

| Question type | NEW with an incumbent label | NEW, teacher-needed | Notes |
|---|---|---|---|
| `v1.finding_class` + `v1.blocking` | 26 findings through the admitted grammar (a1 18 + a2 8; SOLID) + 785 in other formats (a3 735 + a4 50; UNSURE) = 811 findings = 1622 rows | 326 id-anchored items with no class word (a6; UNSURE); the class of the 22 blocking-only anchors (a5) | the training set has 86 findings; the verifier transcripts (d7) add none outside a committed report as far as measured; the 4 class-tagged anchors in the digests (d1 1, d2 3) were not traced to a report |
| `ap.violates_row` | 221 new builder rows at HEAD (144 from 9 new entries, 47 from new registry rows in old entries, 30 re-keyed by entry edits), 10 of them positive by whole-entry citation | the rows of the 3 new entries that cite nothing; every "not cited" row if absence is not taken as "false" | 736 (commit, AF-AP id) pairs in commit messages (c2) have no built state |
| other (not trained today) | gate recommendations: 102 distinct (VERIFY-lane, word) pairs in commits, 66 in the raw session, 85 verifier final messages; 82 decision-log rows; 223 owner text messages (not classified); decide-harvest `wf.drift` 3 | - | decide-harvest today: 369 rows, positives only |

The (VERIFY-lane, gate word) pair regex (c4, d1, d4): `\b(VERIFY-[A-Za-z0-9][A-Za-z0-9._-]*?)(?:-report\.md)?\b[^\n.]{0,120}?\b(MERGE-READY-WITH-FOLLOWUPS|MERGE-READY|NOT-READY|CONTRACT-INVALID)\b`.
The commit patterns (c1-c4) are listed with their regexes in `$S/goal2c_summary.json` (P1-P10); the remaining counts:
P6 `VERIFY-<lane>` named 570 commits; P8 `Echo:`/bug-echo 18; P9 `Cause:`/root cause 12; P10 BLOCKING/NON-BLOCKING 5;
344 commits match at least one of P1, P4, P5, P7. Message text totals 1,498,318 characters (median 497, max 7,958).
Spot check (4 seeded matches per pattern, read by me): P1 4/4, P4 4/4, P5 4/4, P7 4/4 are the named kind.

### 3.2 Goal 2 (a): the report formats, named, with a count each

Admitted by decide-harvest's grammar (the builder's cut, `j2c._blocks`): 204 distinct findings in 12 of 102 `VERIFY-*`
reports (86 in the dataset, 100 held out, 18 new; 1 repeated id, VERIFY-JT3-R1 N-10, AF-AP-199) and 8 in 1 of 30
`report-pc-verify-*` reports. Everything below is NOT admitted.

decide-harvest's own refusal reasons at HEAD (its stderr, `dh-head/stderr.txt`, 153 lines): `no-title-column` 78
(a `| ID | Class | ...` table with no header that starts with "finding" or equals "what"; 68 in `VERIFY-*`, 10 in
`report-pc-verify-*`), `bad-title` 66 (a `- **ID CLASS` bullet not followed by ` — `), `bad-finding-id` 6, `bad-class` 3.

The families (`$S/goal2a.py` `FAMILIES`, line-start anchors only, first family wins per line, applied to every line the
grammar did not admit; a finding = a distinct (report, id), attributed to its FIRST occurrence, so the column sums to the
distinct total; an id the grammar admitted is never counted again):

| Family | `VERIFY-*` first occurrence (any occurrence) | reports | `report-pc-verify-*` |
|---|---|---|---|
| F1 `- **ID CLASS` without ` — ` (= decide-harvest `bad-title`) | 66 (66) | 5 | 0 |
| F2 `**ID CLASS` at line start, no bullet | 145 (145) | 8 | 0 |
| F3 `**ID <sep> CLASS` (sep = em dash, en dash, hyphen, middle dot, colon; bullet optional) | 245 (245) | 16 | 6 |
| F4 `**ID (CLASS` | 54 (54) | 6 | 0 |
| F5 `**ID** <sep> CLASS` | 0 (0) | 0 | 0 |
| F6 markdown heading `### ID <sep> CLASS` | 81 (81) | 6 | 3 |
| F7 numbered `1. ID <sep> CLASS` | 13 (22) | 3 | 10 |
| F8 numbered `1. CLASS [ID]` (the number is the id when none follows) | 49 (51) | 13 | 28 |
| F9 `**CLASS ID` | 0 (lines matched; every id was one the grammar admitted) | 0 | 0 |
| F10 `- CLASS ID` | 0 (lines matched; every id was one the grammar admitted) | 0 | 0 |
| F11 `- **CLASS-n` (for example INFO-2) | 7 (7) | 1 | 0 |
| F12 `- ID <sep> CLASS` (plain bullet) | 1 (1) | 1 | 0 |
| F13 table row under a header other than `# \| class` (a class word as a cell, an id in the first 3 cells, a lettered id preferred over a row number) | 51 (74) | 12 | 0 |
| F14 `# \| class` table row decide-harvest refused (`no-title-column`, `bad-class`, `bad-finding-id`) | 23 (23) | 3 | 3 |
| total distinct | 735 | 55 reports hold at least one (50 hold only these) | 50 (10 reports) |

Also counted, not findings by the families: 96 (`VERIFY-*`) and 16 (`report-pc-verify-*`) residual anchor lines carry a
class word in their first 60 characters but match no family (prose such as "INFO only", a class inside parentheses after
the text, a heading that names a class); 1 in the PC lane reports.

Precision read (UNSURE: one reader, me): 40 first-occurrence findings drawn with `random.Random(20260925)` from the 785
(735 + 50), `$S/goal2a_precision_sample.txt`: 40/40 are a verifier's finding anchor carrying the class the regex read.
Recall was not measured (no complete hand census). Dedup risks, both directions: a report that reuses an id in two
rounds counts once; a finding cited once by a table row number and once by its id can count twice (the F13 lettered-id
preference cut the table count from 64 to 51 first occurrences).

Where the class words are absent (a6): the 59 verify reports with no class-tagged finding (40 `VERIFY-*`, 19
`report-pc-verify-*`) carry, over all their text, 1084 `F-n`/`Fn` tokens (in 44 reports), 100 gate words (50), 542
SOLID/UNSURE (37), 310 PASS/FAIL words (37), 31 BLOCKING/NON-BLOCKING (11) and 14 HIGH/MEDIUM/LOW/CRITICAL (4); 56 of
the 59 carry a gate word or an `F-n` token. Their anchor shapes include `### F-2 — <title> **SOLID**`,
`**F2 — <title>**`, `### VB-F3 [MED] SOLID — ...` and `### Finding CK13-01 — SOLID — ...` (shapes, not quotes of
findings).

### 3.3 Goal 2 (e): what decide-harvest extracts today

Command (read-only; its own `--root` default is the repo; it reads `git cat-file blob HEAD:<path>` and refuses a source
whose worktree bytes differ; it did not refuse):

```
cd /home/user/agent-factory && PYTHONDONTWRITEBYTECODE=1 python3 scripts/decide-harvest --out $S/dh-head/ledger.jsonl
rc=3   (3 = some records refused; 0 would mean none)
harvest: 369 rows, per question type: ap.violates_row=153, b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, d1.bug_echo_scores=0, v1.finding_class=213, wf.drift=3
negatives: 0 (hand-labeled in J2)
sources: 298 read (incident_log=1, lane_report=165, transcript_jsonl=0, verify_report=132), 276 with no records; refused: 153 records; skipped: 0 duplicates
```

| Row kind (question_id) | Rows | From | Producer | Incumbent answers |
|---|---|---|---|---|
| `v1.finding_class` | 213 | 205 `VERIFY-*` (204 distinct ids; decide-harvest keys a restated id by its nearest heading, so VERIFY-JT3-R1 N-10 has 2 rows, measured in the ledger), 8 `report-pc-verify-*` | adversarial-verifier | INFO 108, FOLLOW-UP 88, BLOCKER 10, KNOWN 3, UNVERIFIED 2, CONTRACT-DEFECT 2 |
| `ap.violates_row` | 153 | 143 from the incident log (109 distinct entry headings, 99 distinct registry rows; heading ids only), 10 from verify findings that name an AF-AP id | coordinator 143, adversarial-verifier 10 | "yes" (positives only) |
| `wf.drift` | 3 | 2 `tasks/briefs/*/...-report.md` lane reports, 1 PC lane report (`BOUNDARY DEVIATION` lines) | code-implementer | "yes" |
| `b1.finding_kind`, `b1.finding_sev`, `b2.hit_role` | 0 | `transcript_jsonl` sources: 0 committed (`transcripts/` holds only `.md`) | - | - |
| `d1.bug_echo_scores` | 0 | bug-echo tables in lane reports: none parsed | - | - |

### 3.4 Supporting counts

- Reproducibility: every producer was run twice. `goal1_summary.json`, `goal2a_summary.json`, `goal2c_summary.json`
  and `goal2d_verifiers.json` are byte-identical across the two runs. `goal2d_summary.json` differs only in the raw MAIN
  session transcript's size and record counts: that file is the live coordinator session and grew between the runs
  (700,478,822 -> 700,582,503 bytes; user records 20,213 -> 20,220, assistant 39,908 -> 39,925); every decision count
  (owner text 206, gate-word blocks 186, gate pairs 66, class-tagged ids) is equal in both runs. The table quotes the first run.
- Decision log (d8): `git show 5d7385a0:docs/08_DECISION_LOG.md`, rows matching `^\|\s*D-\d{3}\s*\|`: 82 (82
  distinct, D-001 to D-082); 52 of them contain the word "owner".
- The builder at HEAD (b3), sources: `verify_reports` 102, `reports_with_findings` 12, `verify_findings` 204,
  `repeated_finding_ids` 1, `incident_entries` 210, `registry_rows` 201, held-out excluded 100 + 100, 32 ap rows cut to
  the window, 0 merged duplicates.
- Class balance that Goal 2 sources add against the training rows: the 86 training findings hold BLOCKER 3, FOLLOW-UP 34,
  INFO 49 and none of UNVERIFIED, CONTRACT-DEFECT, KNOWN; J2's held-out sample (`j2-v1-probe/sample.json`, committed
  14add38 2026-09-24T13:04Z, drawn from 144 ledger rows) took every rare-class row then present (BLOCKER 7, KNOWN 3,
  CONTRACT-DEFECT 2, UNVERIFIED 2) by `v1_probe.cmd_sample`'s rule; the 3 training BLOCKERs are VERIFY-JT3 F-1, F-3, F-4
  (report added ec77d72 2026-09-24T16:02Z, after the sample). The a3 + a4 findings hold BLOCKER 69, CONTRACT-DEFECT 10,
  UNVERIFIED 11, KNOWN 1.

## 4. Adjacent defects and contradictions (recorded, not fixed)

| # | Fact | Evidence (git date of the cited file's last change) | SOLID/UNSURE |
|---|---|---|---|
| X1 | The committed manifest's `build_dataset.py` hash (`b9c29b4a...`, ee09d94) is not the tree's (`8dbba45c...`, f1679db). A rebuild with today's builder at the same commit gives the same `dataset.jsonl` bytes but a manifest that differs in 2 lines (the hash, and a new `repeated_finding_ids` key). `C.load_dataset` compares the dataset sha and `rows_total` with the manifest, never the `code` hashes (`scripts/laya_ft/common.py:203-228`, ee09d94 2026-09-24T17:10Z). | section 1, R1 vs R2 | SOLID |
| X2 | The builder reads `VERIFY-*-report.md` only (`REPORT_RX`, `scripts/laya_ft/build_dataset.py:35`, f1679db 2026-09-24T19:40Z); decide-harvest also classifies `tasks/briefs/pc/report-pc-verify-*.md` as verify reports (`scripts/decide-harvest:134`, 0d62801 2026-09-24T03:07Z) and admits 8 findings there at HEAD that the builder never reads. decide-harvest also requires exactly 4 path parts (`:129`); all 102 `VERIFY-*` reports have 4 at HEAD, so no difference from that rule today. | a2; `dh-head/ledger.jsonl` | SOLID |
| X3 | The AP question trains on the WHOLE entry with every AF-AP id masked (`build_dataset.py:113`) while ap_probe labels by HEADING ids (`ap_probe.py:80`) and decide-harvest harvests heading ids only (`decide-harvest:343`). The held-out AP sample took 100 of the 107 entries whose heading names a row, so 94 of the 101 training entries carry no heading citation and 52 carry no citation at all. VERIFY-FT1 already records the train/eval mismatch as F-13 (`tasks/briefs/jev-laya/VERIFY-FT1-report.md:389`, d483505 2026-09-24T18:36Z). | 2.1, 2.4 | SOLID |
| X4 | The 86 training findings hold no UNVERIFIED, CONTRACT-DEFECT or KNOWN row: J2's held-out rule (`v1_probe.py:55-57`, keep every rare-class row) took all 14 present at 14add38; the training BLOCKERs (3) came from a report added later (VERIFY-JT3, ec77d72). | 3.4 | SOLID |
| X5 | decide-harvest writes positives only ("negatives: 0 (hand-labeled in J2)", `decide-harvest:908`); its 153 ap rows carry no negative. | 3.3 | SOLID |
| X6 | The sandbox digests hold 268 "user" turns that start with no injected prefix, while the raw sessions hold 206 + 17 owner text records by this report's rule (which also drops `isMeta`/`isCompactSummary` records). `transcript_export.turns` (`scripts/transcript_export.py:91-113`) filters by text prefix and never reads `isMeta` (grep: 0 hits). The cause of the 45-turn difference was not established (the digests cover the newest transcript only; the rules differ). | d1, d3, d6 | UNSURE |
| X7 | 56 of the 59 verify reports with no class-tagged finding still carry a gate word or an `F-n` token (3.2 "Where the class words are absent"); the admitted grammar finds findings in 12 of 102 `VERIFY-*` reports and 1 of 30 `report-pc-verify-*` reports. | 3.2 | SOLID (counts) |

The cited files and their last change at the pinned HEAD (`git log -1 --format='%h %cI' 5d7385a0 -- <file>`):

| File | Last change |
|---|---|
| `scripts/decide-harvest` | 0d62801 2026-09-24T03:07:58Z (hash equals the manifest's: unchanged since the build) |
| `scripts/laya_ft/build_dataset.py` | f1679db 2026-09-24T19:40:24Z (after the manifest; see X1) |
| `scripts/laya_ft/common.py` | ee09d94 2026-09-24T17:10:20Z |
| `docs/research/findings/ap-hawk-probe/ap_probe.py`, `.../sample.json` | 2ea5f62 2026-09-24T12:42:21Z |
| `docs/research/findings/j2-v1-probe/v1_probe.py`, `.../sample.json` | 14add38 2026-09-24T13:04:31Z |
| `docs/research/findings/j2c-fulltext/j2c.py`, `.../sample.json` | ce5e283 2026-09-24T14:59:53Z |
| `scripts/transcript_export.py` | 5415c2a 2026-09-23T17:03:44Z |
| `docs/research/findings/laya-ft-labels/2026-09-24-openjev/labels.jsonl`, `dataset-manifest.json` | 1958d59 2026-09-24T18:09:11Z |
| `docs/INCIDENT-LOG.md` | d36ba41 2026-09-25T00:25:51Z (Goal 1 reads it at eb256f49, Goal 2 at 5d7385a0) |
| `docs/08_DECISION_LOG.md` | 2969794 2026-09-25T00:21:19Z |
| `todo/BUILD-TASKLIST.md`, `wiki/topics/live-state.md` | 5d7385a 2026-09-25T00:45:20Z |
| `tasks/briefs/jev-laya/window1.jobs` | 24a07a8 2026-09-24T21:46:23Z |
| `tasks/briefs/jev-laya/VERIFY-FT1-report.md` | d483505 2026-09-24T18:36:10Z |

## 5. NOT-done

1. The PC's `~/laya-ft/ds-0b342c7/manifest.json` and `dataset.jsonl` were not read (the PC bridge is out of scope). The
   claim that the PC copy is byte-identical rests on records only (`wiki/topics/live-state.md:77`, the f1679db message).
2. Body citations in incident entries were not hand-graded: whether each cited row is the row the entry "shows" (2.1
   gives the last-word tally only). The ap truth is the citation fact, in two variants (whole entry, heading).
3. The other-format finding counts (a3-a6) rest on regex families. Precision: one reader, 40 of 785, 40/40. Recall: not
   measured (no hand census of every report). The id dedup can merge or split findings (3.2).
4. Owner rulings were counted as owner text messages (206 + 17); they were not classified into rulings, questions,
   acknowledgements or pasted banners, because that needs reading the messages. The decision log (82 D-rows) is the
   committed record of rulings; the join between the two was not attempted.
5. Commit messages: pattern counts only. No (state, answer) pair was extracted. Precision was spot-checked (4 seeded
   matches each) for P1, P4, P5 and P7 only; P2, P3, P6 and P8-P10 were not checked.
6. No teacher labels were produced or measured (Qwen / QJ2 not run); "teacher-needed" rows are counted, not labeled.
7. Raw subagent transcripts: only the adversarial-verifier ones were read for findings; code-implementer (128),
   evidence-gatherer (16), council (26), general-purpose (5) and claude (4) outputs were counted, not classified. The 4
   workflow journals and the 198 tool-result files under the session directory were not analyzed.
8. The PC-side Hermes session databases (the PC lanes' own chat logs) were not read (bridge out of scope); only their
   committed digests (`transcripts/pc/*.md`) were counted.
9. The J2 and KC-J3 results named in the brief's WHY (`evaluate-summary.json`, `ap_noul.json`) were not re-derived; this
   report measures the training rows only.
