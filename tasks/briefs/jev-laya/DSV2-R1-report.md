# DSV2-R1 report (task #251; D-031 one repair; VERIFY-DSV2 finding V-6)

Lane: code-implementer, sandbox, Opus 5.5. Brief: `tasks/briefs/jev-laya/DSV2-R1-brief.md`. PIN 12623b3.
Status: DONE, not committed (05:0xZ). The five forms are in `blocking-words`, each reads 0 unflagged (F-a 93 -> 0), the record is
regenerated at 434b727 with `labels.jsonl` byte-identical, gate 42 + 101 passed, and the four files are copied into the main tree.
Discrepancies (section 10): D-1, the F-a false positive the brief asks for (1 row per question, `are canonical:`), plus 2 more
false-positive-only rows from F-c and F-d, all `false` answers, none narrowed as ruled. NOT done: section 11.

## 0. Premise re-measure (demand 1), part A: the PIN's boundary files

Clock at start: `Fri Sep 25 04:34:28 UTC 2026`. Main-tree HEAD (the DSV2-R1 brief commit, 9845b52 on origin) is two commits past the PIN; `git diff --stat 12623b3 24689bc`
touches only `tasks/briefs/jev-laya/DSV2-R1-brief.md`, `tasks/briefs/jev-laya/VERIFY-DSV2-report.md`, `todo/BUILD-TASKLIST.md`
(no boundary file).

```
$ git show 12623b3:<file> | sha256sum | cut -c1-16
f71590b4be1c7108  scripts/laya_ft/build_dataset.py
8e52b288ea722a0e  tests/test_laya_ft.py
efd3c91306cc967b  docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
0098e52e0dbfc01d  docs/research/findings/laya-ft-labels/2026-09-25-recorded/labels.jsonl
4fdd169cc9a05ec6  docs/research/findings/laya-ft-labels/2026-09-25-recorded/summary.json
f63cd97ef441b817  scripts/transcript_export.py
```

All six match the brief's premise block (verified).

## 0. Premise re-measure (demand 1), part B: the record rebuilds at the PIN; the probe reproduces

Worktree: `git -C /home/user/agent-factory worktree add --detach <scratch>/wt 12623b3` rc 0 (04:3xZ); `git status --short` 0 lines.
Build with the PIN's code, unedited worktree (the Laya venv `/root/venv-laya-probe/bin/python`, model dir
`C.DEFAULT_MODEL_DIR` = `/root/hf-laya-probe/hub/models--convaiinnovations--laya/snapshots/1c5edc17a7acd8701df6fc341c0d179f1c62c982/typed-decisions`):

```
$ HF_HUB_OFFLINE=1 /root/venv-laya-probe/bin/python scripts/laya_ft/build_dataset.py --version 2 --commit 434b727 --out <scratch>/pin/ds --model-dir <model dir>
build rc=0 elapsed=36s
$ python3 scripts/laya_ft/recorded_labels.py --dataset <scratch>/pin/ds --out <scratch>/pin/labels.jsonl --summary <scratch>/pin/summary.json
labels rc=0
manifest == record dataset-manifest.json      (cmp)
labels == record labels.jsonl                 (cmp)
summary == record summary.json                (cmp)
f1b92d6fa79c2f145052fec9f301f1e719987ae5f7d14e19f663eb67426b5c48  pin/ds/dataset.jsonl
efd3c91306cc967b7ddc320293cf53e150fc3ea075782c711a84f2d224011ff0  pin/ds/manifest.json
0098e52e0dbfc01db12bfceb0a807db6fad533e10cf7380c72e368926375ca58  pin/labels.jsonl
4fdd169cc9a05ec6a0005197d6ca59026deaca0b9f0a713b1e766ea43312e530  pin/summary.json
```

The verifier's probe, copied to `<scratch>/probes/blockwords_pin.py` with ONLY the `V =` line changed (diff: line 4, `V` points
at `<scratch>/pin`, where `v2` is a link to `ds`; the original's sha256 starts `a2e875503e85d89d`). Its 12 output lines are
IDENTICAL to the brief's premise block (`diff` rc 0 against the block cut from the brief by awk):

```
v1.blocking rows 826 base rate {'false': 749, 'true': 77}
predicate walk (contract mapping/canonical/material/discriminator/ownership)     rows 114 unflagged  93  answers(all) {'false': 76, 'true': 38}  answers(unflagged) {'false': 58, 'true': 35}
No [CLASS] summary                                                               rows   1 unflagged   1  answers(all) {'false': 1}  answers(unflagged) {'false': 1}
does not / doesn't block (any)                                                   rows   8 unflagged   1  answers(all) {'false': 8}  answers(unflagged) {'false': 1}
blocks / blocked (verb, any object)                                              rows  34 unflagged  32  answers(all) {'false': 29, 'true': 5}  answers(unflagged) {'false': 28, 'true': 4}
not a [CLASS] / is a [CLASS]                                                     rows  29 unflagged  12  answers(all) {'false': 22, 'true': 7}  answers(unflagged) {'false': 8, 'true': 4}
merge-ready words                                                                rows   4 unflagged   0  answers(all) {'false': 3, 'true': 1}  answers(unflagged) {}
hollow green                                                                     rows   6 unflagged   5  answers(all) {'false': 4, 'true': 2}  answers(unflagged) {'false': 3, 'true': 2}
no material effect / not material                                                rows   7 unflagged   6  answers(all) {'false': 7}  answers(unflagged) {'false': 6}
defence-in-depth / optional hardening / hypothetical                             rows  14 unflagged  12  answers(all) {'false': 13, 'true': 1}  answers(unflagged) {'false': 11, 'true': 1}
repair / must fix / fix before                                                   rows   1 unflagged   1  answers(all) {'false': 1}  answers(unflagged) {'false': 1}
ANY of the forms, unflagged: 143 {'false': 105, 'true': 38}
```

Set ids (`bash scripts/pc_suite.sh set-id -- <files>`, local function, no bridge call):
`3 files set=5d6a3ce56265` (the brief's three files; matches the brief), `1 files set=8b147318aa48` (tests/test_laya_ft.py),
`2 files set=fd0b1c7da4bc` (tests/test_decide_harvest.py tests/test_recorded_labels.py).

Premise verdict: HOLDS (verified). No CONTRACT-INVALID.

Seams read (verified in the worktree; line numbers at the PIN, and after this change +8 below the `LEAKS` block):
- `LEAKS` has one reader, `flag_leaks`, at `scripts/laya_ft/build_dataset.py@12623b3:415` (`kinds`, `LEAKS`), now at
  `scripts/laya_ft/build_dataset.py:423` (`kinds`, `LEAKS`). Text sweep of scripts/ tests/ src/ proofs/ docs/, plus GitNexus
  `impact LEAKS`: UNKNOWN, no resolved callers.
- `flag_leaks` has one caller, `build_v2` (GitNexus `impact flag_leaks`: LOW, 1 direct): `scripts/laya_ft/build_dataset.py:562` (`leak_counts`).
- The `leak` field has one reader, `summarize_v2`: `scripts/laya_ft/build_dataset.py@12623b3:528`, now
  `scripts/laya_ft/build_dataset.py:536` (`if "leak" in s`).
- `item_id` = prefix + `state_sha[:20]`, set in `make_row` (`scripts/laya_ft/build_dataset.py:488-495`, `make_row`) before
  `flag_leaks` runs; a label record carries no source field (`scripts/laya_ft/recorded_labels.py:40-43`, `label_key`), so
  `labels.jsonl` cannot change with the flags (inferred from code; proven in section 3).
- Version 1's `def build` never calls `flag_leaks`: `scripts/laya_ft/build_dataset.py@12623b3:584-619`, now
  `scripts/laya_ft/build_dataset.py:592-627` (`def build`).

## 1. Red first (demand 2)

The test: `test_leak_flags_mark_the_rows_and_leave_none_out` (`tests/test_laya_ft.py:1294`, extended in place). It adds five
`v1.blocking` rows, one per ruled form, each expected `blocking-words`, and the brief's two negatives, each expected unflagged:

| Row | State | Form |
|---|---|---|
| F-10 | `Predicate: not contract-mapped; the contract names no file-type rule` | F-a |
| F-11 | `No [CLASS] in this round.` | F-b |
| F-12 | `The finding would not block on its own.` | F-c |
| F-13 | `This is a [CLASS] by the rule.` | F-d |
| F-14 | `It is not material to the claim.` | F-e |
| F-15 | `the hook blocks the call` | negative (bare "blocks") |
| F-16 | `optional hardening` | negative (severity word) |

Each positive state matches only its own form: checked mechanically against the five patterns parsed from the brief and the
PIN's old pattern (F-a row matched by ['F-a'] only, and so on for F-b to F-e; both negatives matched by nothing). So dropping any
one form turns the test red. BEYOND THE BRIEF'S MINIMUM (flagged, not a deviation from the rule): a loop of 25 one-row checks
that, with the five form rows, covers every alternative of the five forms: F-a's six alternatives (the loop has `Contract
mapping:` with a space, F-10 has `contract-mapped` with a hyphen; `canonical:`, `canonical path:`, `canonical reproduction =`;
`material:` and `material effect:`; `discriminator:`; `task ownership`; `in boundary:` and `in-boundary:`), F-b, six of F-c's seven
verbs in the loop (the seventh, `would not`, is row F-12), F-d's `is`/`as` with `a`, `an` or no article (`is a` is row F-13),
and F-e's three words. Reason: one state per form leaves five of F-a's six alternatives untested, so a pattern that lost one
would stay green (anti-hollow-green tactic 3: a gate must kill mutants). The count assertion moves from
`v1.blocking|blocking-words: 1` to `6`.

Red run: a scratch copy (`git archive 12623b3` of `scripts/laya_ft`, `scripts/transcript_export.py`, `scripts/decide-harvest`,
`src/agent_factory`, the three probe dirs and `tests/conftest.py`; 552 KB) with the NEW test file copied in. Its
`build_dataset.py` hashes `f71590b4be1c7108` (the PIN's). The first two attempts died at collection (`scripts/decide-harvest`,
then `agent_factory` missing from the copy); both were added and neither is a test result.

```
$ cd <scratch>/red && python3 -m pytest tests/test_laya_ft.py -k test_leak_flags_mark_the_rows_and_leave_none_out -q -p no:cacheprovider --basetemp=<scratch>/bt/red
>       assert [[s.get("leak") for s in r["sources"]] for r in rows] == [
            ["class-word"], ["blocking-words"], [None], ["ap-id+row-name"]] + [["blocking-words"]] * 5 + [[None]] * 2
E       AssertionError: assert [['class-word..., [None], ...] == [['class-word...-words'], ...]
E         At index 4 diff: [None] != ['blocking-words']
tests/test_laya_ft.py:1312: AssertionError
FAILED tests/test_laya_ft.py::test_leak_flags_mark_the_rows_and_leave_none_out
1 failed, 41 deselected in 0.13s
pytest rc=1
```

Index 4 is the first new row (F-a): the exact expected reason. pytest truncates the rest of the diff, so the same copy's
`flag_leaks` was also run directly on all 32 states (7 rows plus 25 loop phrases):
`PIN builder flags 1 of 32 states: ['It does not block.']` (the old pattern's own `\bdoes not block\b`, kept in the loop on
purpose). The five form rows, the two negatives and 24 of the 25 alternatives are unflagged on the PIN.

## 2. The change, then green

`scripts/laya_ft/build_dataset.py:145-156` (the `blocking-words` entry of `LEAKS`; the rest of the file is untouched). The old
three lines stay byte for byte; eight lines are appended to the same regex literal (one comment line naming DSV2-R1 plus the
five forms with short trailing tags). They stay ONE kind, `blocking-words`, as the brief rules. The pattern text of each form is the
brief's table text with `\|` unescaped. One implementation detail, stated because it could look like a redesign: F-b is written
`(?-i:\bNo \[CLASS\])`. The brief's F-b carries no `(?i)` while the others do, and the whole regex starts with the old global
`(?i)`, so a plain append would have made F-b case-insensitive, a WIDER rule than the ruling. The scoped flag keeps each form's
flags exactly as ruled. On this dataset it matters for one state: `holds no [CLASS] call` (a blocking I/O call, a domain use)
stays unflagged, as the ruled case-sensitive F-b leaves it.

Independent equivalence check (verified): the five patterns parsed out of the brief's table by a regex over the brief file
(`\|` unescaped), the old pattern evaluated from the PIN's own source literal (`git show 12623b3:scripts/laya_ft/build_dataset.py`),
the new regex imported from the worktree. `new.search(s)` == `old.search(s) or any(form.search(s))` on all 1,652 `v1.*` states
of the rebuild plus 11 edge strings: `states checked: 1652 + 11 | new != old U forms: 0`. Edge strings: `No [CLASS]` True;
`no [CLASS] call`, `NO [CLASS]`, `It doesn’t block.` (curly apostrophe), `the hook blocks the call`, `optional hardening`,
`Canonical production path: x`, `contract map: x`, `Predicate: x`, `is known`, `in_boundary = 1` all False.

Green in the worktree:

```
$ python3 -m pytest tests/test_laya_ft.py -k test_leak_flags_mark_the_rows_and_leave_none_out -q -p no:cacheprovider --basetemp=<scratch>/bt/green
1 passed, 41 deselected in 0.20s
pytest rc=0
```

GitNexus before the edit (main tree's index; the worktree has none): `impact flag_leaks --direction upstream`: risk LOW, 1 direct
caller (`build_v2`), processes `build_v2` and `build`; `impact LEAKS`: risk UNKNOWN, no resolved callers (a module-constant read
the index does not record); the text sweep confirms `flag_leaks` (`:415`) is its only reader. The edit-snapshot hook on both
edits: `registry screen: no mechanical anti-pattern tells in this hunk`.

## 3. The record, regenerated at the build commit (demand 3)

In the worktree, after the final builder edit (the manifest hashes the builder, so it was not touched again):

```
$ HF_HUB_OFFLINE=1 /root/venv-laya-probe/bin/python scripts/laya_ft/build_dataset.py --version 2 --commit 434b727 --out <scratch>/new/ds --model-dir <model dir>
build rc=0 elapsed=37s
$ python3 scripts/laya_ft/recorded_labels.py --dataset <scratch>/new/ds --out <scratch>/new/labels.jsonl --summary <scratch>/new/summary.json
labels rc=0
{"conflicts": 0, "labeled": 5301, "labels": {"bytes": 2667100, "file": "labels.jsonl", "sha256": "0098e52e0dbfc01db12bfceb0a807db6fad533e10cf7380c72e368926375ca58"}, "rows": 6196, "unlabeled": {"ap.violates_row|commit": 15, "ap.violates_row|incident": 880}}
labels.jsonl BYTE-IDENTICAL to the record      (cmp)
```

| File | Old sha256 (PIN record, = the PIN rebuild) | New sha256 |
|---|---|---|
| dataset.jsonl (not committed; pinned by the manifest) | `f1b92d6fa79c2f145052fec9f301f1e719987ae5f7d14e19f663eb67426b5c48` | `99070c33830832ca11e64226eddac1934ccd300c73b4d5d8d8c7bf5a36271f9d` |
| dataset-manifest.json | `efd3c91306cc967b7ddc320293cf53e150fc3ea075782c711a84f2d224011ff0` | `a7545005e26c09f769993146b1be220bc0f666130cde30e1d1fd713a1e14b4d1` |
| labels.jsonl | `0098e52e0dbfc01db12bfceb0a807db6fad533e10cf7380c72e368926375ca58` | `0098e52e0dbfc01db12bfceb0a807db6fad533e10cf7380c72e368926375ca58` (UNCHANGED) |
| summary.json | `4fdd169cc9a05ec6a0005197d6ca59026deaca0b9f0a713b1e766ea43312e530` | `2b7f0d8a2101cb5a59682a795ad155830a20cede1450896d570fbeeaec9af5fd` |

What changed, key by key (a flattening diff of old vs new JSON; nothing else differs):

```
== manifest: 83 keys, 3 changed
  /code/scripts/laya_ft/build_dataset.py   f71590b4be1c7108f250e58a1d6528481e59cada6c54f47cd3c7542d4ef4f3d5 -> 1c95e37a0d99cfa874879bb0d1a9ee4674b2cfcedef9cbd749d77d6020c69297
  /dataset/bytes                           12795031 -> 12800855
  /dataset/sha256                          f1b92d6fa79c2f145052fec9f301f1e719987ae5f7d14e19f663eb67426b5c48 -> 99070c33830832ca11e64226eddac1934ccd300c73b4d5d8d8c7bf5a36271f9d
== summary: 138 keys, 5 changed
  /dataset_summary/leaks/v1.blocking|blocking-words                                                          35 -> 141
  /dataset_summary/leaks/v1.finding_class|blocking-words                                                     35 -> 141
  /dataset_summary/leaks_by_source_question_provenance_kind/verify_finding|v1.blocking|verifier-class|blocking-words       36 -> 148
  /dataset_summary/leaks_by_source_question_provenance_kind/verify_finding|v1.finding_class|verifier-class|blocking-words  36 -> 148
  /labels/dataset/sha256                   f1b92d6f... -> 99070c33...
```

The manifest still pins `scripts/transcript_export.py` at `f63cd97ef441b817...` (the PIN's; the main tree's modified copy was never
read). Leak counts, before -> after: `v1.blocking|blocking-words` 35 -> 141 rows; `v1.finding_class|blocking-words` 35 -> 141;
by source 36 -> 148 each; `class-word` 1 and 1, `ap-id` 126, `row-name` 33 unchanged. Row-level check of the two datasets:
`rows 6196 | rows differing outside the leak field: 0`; `sources changed v1.blocking: - -> blocking-words 112`, the same 112 for
`v1.finding_class`; `rows newly flagged (unflagged at PIN): {'v1.finding_class': 106, 'v1.blocking': 106}` (35 + 106 = 141; a merged
row carries several sources, so 36 + 112 = 148). No existing flag value changed (no `class-word` row gained `blocking-words`).

The worktree's record now holds the regenerated `manifest.json` (as `dataset-manifest.json`) and `summary.json`, `cmp`-equal to the
build outputs; `labels.jsonl` untouched.

## 4. The discriminator (demand 4)

The verifier's probe, copied to `<scratch>/probes/blockwords_new.py`, only the `V =` line changed (`V` = `<scratch>/new`, `v2` a link to
`ds`). Full output:

```
v1.blocking rows 826 base rate {'false': 749, 'true': 77}
predicate walk (contract mapping/canonical/material/discriminator/ownership)     rows 114 unflagged   0  answers(all) {'false': 76, 'true': 38}  answers(unflagged) {}
No [CLASS] summary                                                               rows   1 unflagged   0  answers(all) {'false': 1}  answers(unflagged) {}
does not / doesn't block (any)                                                   rows   8 unflagged   0  answers(all) {'false': 8}  answers(unflagged) {}
blocks / blocked (verb, any object)                                              rows  34 unflagged  23  answers(all) {'false': 29, 'true': 5}  answers(unflagged) {'false': 22, 'true': 1}
not a [CLASS] / is a [CLASS]                                                     rows  29 unflagged   0  answers(all) {'false': 22, 'true': 7}  answers(unflagged) {}
merge-ready words                                                                rows   4 unflagged   0  answers(all) {'false': 3, 'true': 1}  answers(unflagged) {}
hollow green                                                                     rows   6 unflagged   5  answers(all) {'false': 4, 'true': 2}  answers(unflagged) {'false': 3, 'true': 2}
no material effect / not material                                                rows   7 unflagged   0  answers(all) {'false': 7}  answers(unflagged) {}
defence-in-depth / optional hardening / hypothetical                             rows  14 unflagged   9  answers(all) {'false': 13, 'true': 1}  answers(unflagged) {'false': 9}
repair / must fix / fix before                                                   rows   1 unflagged   1  answers(all) {'false': 1}  answers(unflagged) {'false': 1}
ANY of the forms, unflagged: 37 {'false': 34, 'true': 3}
probe rc=0
```

F-a (predicate walk) 93 -> 0; F-b (No [CLASS]) 1 -> 0; F-c (negated block) 1 -> 0; F-d with the old "not a" (the probe's
"not a / is a [CLASS]" row) 12 -> 0; F-e (materiality) 6 -> 0. Every ruled form reads 0 unflagged. The residue is only the forms
the ruling left out (bare blocks/blocked 23, hollow green 5, severity words 9, must fix 1): ANY 143 {false 105, true 38} -> 37
{false 34, true 3}.

The brief's question on F-d: YES, F-d plus the old `not a` leaves 0 unflagged in that row (12 -> 0; row count 29 unchanged). By
construction too: the probe's row regex `(?i)\b(?:not|is|as) (?:a |an )?\[CLASS\]` is exactly the union of the old
`\bnot (?:a |an )?\[CLASS\]` (under the old pattern's global `(?i)`) and F-d. No state remains.

## 5. Version 1's byte clause (demand 5)

Direct build with the NEW builder (worktree `build_dataset.py` sha256 prefix `1c95e37a0d99cfa8`), in addition to the test below:

```
$ HF_HUB_OFFLINE=1 /root/venv-laya-probe/bin/python scripts/laya_ft/build_dataset.py --commit 0b342c7 --out <scratch>/v1/ds --model-dir <model dir>
v1 build rc=0 elapsed=10s
d7cd9b49abac267bb9b5290641ea353180a9a61047ce6c590809520b085cea1c  v1/ds/dataset.jsonl
committed openjev manifest dataset sha256: d7cd9b49abac267bb9b5290641ea353180a9a61047ce6c590809520b085cea1c
1788   (rows)
```

Holds (verified): version 1's `build()` never calls `flag_leaks`, and the bytes are unchanged. The test
`test_version_1_is_byte_identical_and_still_loads` runs in the gate (section 6).

## 6. The gate, in the worktree, two foreground calls (demand 6)

`git status --short` in the worktree before call 1: exactly the four boundary files (M). `--basetemp` under the scratch (parent
`<scratch>/bt` created first); `test_summary.sh` exports `S0_01_VENUE=sandbox`, so the Laya-venue tests RAN (0 `skip` lines in
either log).

```
$ bash scripts/test_summary.sh tests/test_laya_ft.py --basetemp=<scratch>/bt/g1          (04:50:33Z -> 04:55:41Z)
..........................................                               [100%]
42 passed in 307.89s (0:05:07)
pytest-exit: 0
pytest-summary: 42 passed in 307.89s (0:05:07)
$ bash scripts/pc_suite.sh set-id -- tests/test_laya_ft.py
1 files set=8b147318aa48

$ bash scripts/test_summary.sh tests/test_decide_harvest.py tests/test_recorded_labels.py --basetemp=<scratch>/bt/g2   (04:55:48Z -> 04:56:12Z)
101 passed in 24.10s
pytest-exit: 0
pytest-summary: 101 passed in 24.10s
$ bash scripts/pc_suite.sh set-id -- tests/test_decide_harvest.py tests/test_recorded_labels.py
2 files set=fd0b1c7da4bc
```

42 + 101 = 143, the count VERIFY-DSV2 reported for the three-file set `5d6a3ce56265` (the unit test was extended in place, so
the count does not move). Call 1 includes `test_version_2_record_rebuilds_byte_identically_at_the_pin`: two more builds at
434b727 with the new builder, equal to each other and to the regenerated `dataset-manifest.json`, the labels and `summary.json`
equal to the record, and the Laya fit check (0 truncated, 0 bad markers). With my own build that is three identical builds.
It also includes `test_version_1_is_byte_identical_and_still_loads` (demand 5).

Mutation audit of the change (`<scratch>/probes/mutate.py`; each mutant written into the scratch red copy's builder, never the
worktree, the red copy restored to the PIN builder afterwards, `f71590b4be1c7108` re-read): 26 mutants, each dropping or narrowing
one alternative of F-a to F-e. 24 killed by the extended test. Two survive, both expected: `F-b case-insensitive` (a widening,
left unpinned on purpose, see DISCREPANCIES D-4) and `F-c drop does not` (equivalent: the old pattern keeps `\bdoes not
block\b`). Control, the unmutated new builder: `rc 0 1 passed, 41 deselected`; `unexpected outcomes: 0`, rc 0.

## 7. pyflakes and separators (demand 7)

```
$ python3 -m pyflakes scripts/laya_ft/build_dataset.py tests/test_laya_ft.py
pyflakes rc=0
$ LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>      (per file)
0 scripts/laya_ft/build_dataset.py
0 tests/test_laya_ft.py
0 docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
0 docs/research/findings/laya-ft-labels/2026-09-25-recorded/summary.json
0 tasks/briefs/jev-laya/DSV2-R1-report.md   (re-checked after every append; final check in FILES)
0 probes/forms_review.py, probes/blockwords_new.py, probes/blockwords_pin.py   (scratch only)
```

## 8. Evidence tiers (data)

| Claim | Tier | Evidence |
|---|---|---|
| Premise holds: six PIN hashes, record rebuilds byte for byte at the PIN, probe output identical to the brief | verified | section 0 |
| New test red on the PIN builder for the exact reason, green on mine | verified | sections 1-2 |
| New regex = old pattern + the brief's five forms, exactly | verified | section 2 equivalence check, 0 of 1,663 disagree |
| Record regenerated at 434b727 with the new builder; `labels.jsonl` byte-identical | verified | section 3 (cmp, sha256) |
| Only the leak fields changed in the dataset; manifest and summary change only in the expected keys | verified | section 3 key diff and row diff |
| F-a to F-e each read 0 unflagged on the rebuild | verified | section 4 probe |
| Version 1 at 0b342c7 still `d7cd9b49...` | verified | section 5 direct build + gate test |
| Gate: 42 passed (set 8b147318aa48), 101 passed (set fd0b1c7da4bc) | verified | section 6 |
| Test kills 24 of 26 mutants, both survivors expected | verified | section 6 |
| `labels.jsonl` cannot change with any flag rule (item ids come from states) | inferred from code, then verified on this build | section 0 seams, section 3 |
| The residual unflagged 37 rows are the forms the ruling excluded, not new leak classes | inferred | section 4 table; I did not hunt other forms beyond D-8 below |

## 9. Deviations and additions (flagged loudly)

1. ADDITION: the unit test carries a 25-phrase loop, one per alternative of the five forms, beyond the brief's "one state per
   form". Reason: mutation resistance (section 6). The brief's shape is kept intact: five form rows + two negatives in the existing
   test, which is extended in place, not a new test.
2. IMPLEMENTATION CHOICE: F-b is `(?-i:\bNo \[CLASS\])` inside the one regex, to keep the ruled case sensitivity under the
   old global `(?i)` (section 2). Not pinned by a test on purpose: a test that asserts `no [CLASS]` stays unflagged would lock a
   known miss in as correct (D-4). The mutation audit shows it survives, as expected.
3. The old `\bdoes not block\b` alternative is kept although F-c subsumes it (minimal diff; no behaviour change).
4. One comment line and short trailing form tags sit inside the `LEAKS` literal (`scripts/laya_ft/build_dataset.py:148-155`, `F-a`
   to `F-e`). They are comments, not pattern text.
5. `--basetemp=<scratch>/bt/g1|g2` was added to the two `test_summary.sh` calls (the brief's commands have none; its standing
   rules name `--basetemp`). The set ids are computed on the test files alone.
6. The premise probe ran on MY rebuild at the PIN, not the verifier's: `verify-dsv2/v2/` (the probe's `V`) no longer exists
   in the scratch. My PIN rebuild is byte-identical to the record, so it is the same input (section 0).

## 10. DISCREPANCIES

D-1 (the brief asks for this one): F-a flags one state whose words do not state the predicate. Row: item
`v1-b7f4760641ec9368f38d` (both v1 questions; answers `false` and `INFO`), source `tasks/briefs/laya/VERIFY-J1-2-R1-report.md`
finding INFO-3. Its only F-a match is `canonical:` in "Named row refusals on lines that parse and are canonical: a 4300-digit
int -> ..." (`tasks/briefs/laya/VERIFY-J1-2-R1-report.md@434b727:421`, `decision-row-unknown-field`): "canonical" names a JSON line's
canonical form, not the predicate's "canonical path". No other alternative of `blocking-words` or `class-word` fires on the state
with that match blanked, so the row is flagged ONLY by it. Not narrowed, as the brief rules. I reviewed all 260 F-a matches in
the 114 `v1.blocking` rows (context printed per match, `<scratch>/pin/fa_review.txt`); every other match states a predicate item
(including `neither material:` and `**Contract mapping.**`).

D-2 (adjacent, F-c): item `v1-4e8e7681c7340257e51c` (answer `false`), `tasks/briefs/jev-laya/VERIFY-T243-245-report.md` C-F6,
"the row cannot block a commit: `lint_delta.py` blocks on new pyflakes hits only"
(`tasks/briefs/jev-laya/VERIFY-T243-245-report.md@434b727:445`, `lint_delta.py`). "cannot block" here is a hook's verb (the same
domain use the ruling excluded for a bare "blocks"), and F-c is the only match on the row. Not narrowed.

D-3 (adjacent, F-d): J2's mask is case-insensitive over the class words (`docs/research/findings/j2-v1-probe/v1_probe.py:34`,
`MASK`), so a plain-English "known" becomes `[CLASS]` and F-d reads it as a stated class. Three rows per question: VERIFY-FT1
F-6 "the size is known" (`tasks/briefs/jev-laya/VERIFY-FT1-report.md@434b727:347`, `select_trainable`; item
`v1-23533416c89aecdb28f8`, `false`, flagged ONLY by this match); VERIFY-T243-245 B-F1 "names this as a known limit" (item
`v1-968eb0e4429f8f43f3f8`, `true`) and VERIFY-K1-h finding 2 "the limitation is a known design constraint" (item
`v1-94f26e3e60f58c511d00`, `false`), both flagged by F-a anyway. Gray, not counted as false: VERIFY-GW1 F-2 and F-13 ("is
UNVERIFIED" about a sub-claim) and VERIFY-CI-GATE-R1 VR-3 ("the misuse F5 itself classed as a follow-up", another finding's class).
The old "not a [CLASS]" has the same exposure ("not known" becomes "not [CLASS]"). Not narrowed.
Total rows flagged only by a false-positive match: 3 per v1 question (D-1, D-2, the FT1 row of D-3), all `false` answers; a
run that drops flagged rows loses those 3 clean rows of 749 `false` per question.

D-4 (F-b case, measured): the ruled F-b is case-sensitive. A case-insensitive F-b would flag one more `v1.blocking` row:
"The window holds no blocking call" (masked `no [CLASS] call`; `tasks/briefs/laya/VERIFY-J1-2-R1-report.md@434b727:347`,
`finally`), a blocking I/O call, i.e. a domain use. So the ruling's case sensitivity avoids a false positive on this data.

D-5 (the brief's F-b rationale vs the data): the brief describes F-b as '"No BLOCKER" after the mask'. The one F-b row in the
data is "No blocking-predicate mapping (the contract wants ...)" (VERIFY-J1-0-R23-STAMP report at 434b727, line 176; masked
`No [CLASS]-predicate mapping`, answer `false`): a predicate statement, not a class summary. It is flagged either way.

D-6 (coupling with the SESSION-EXPORT lane, adjacent): the record's manifest pins `scripts/transcript_export.py` at
`f63cd97ef441b817...` (the PIN's). The main tree holds that lane's uncommitted change, which hashes `1cc0fdadb2b6aeda`. While it
sits there, `test_version_2_record_rebuilds_byte_identically_at_the_pin` fails in the main tree by construction (true before this
repair too; orchestration 0j). Whichever lands second must regenerate the record. If the new `scrub` changes any state, item
ids and `labels.jsonl` change too, and "labels unchanged" will not hold for that later regeneration.

D-7 (stale counts in past records, not edited, outside the boundary): the old `blocking-words` count of 35 per question is
quoted by `tasks/briefs/jev-laya/DSV2-report.md:494` (`verifier-class`), `tasks/briefs/jev-laya/VERIFY-DSV2-brief.md:42`
(`blocking-words`) and `tasks/briefs/jev-laya/VERIFY-DSV2-report.md:117` (`blocking-words`), and the ledger's DSV2 LANDED entry
(todo/BUILD-TASKLIST.md, line 1497 at HEAD (the D-087 commit, a1d4f70 on origin)). They record what was measured then. The record's own summary now says 141.

D-8 (residual near misses, measured on the rebuild, information only): curly-apostrophe "n’t block" 0 rows; "don't / didn't /
won't / wouldn't / can't / can not block" 0 rows; V-6's suggested `predicate:` (not ruled in) 23 rows, all already flagged by the
ruled forms; "Contract map:" (no "mapp") 1 row, flagged by other alternatives.

D-9 (tree movement during the lane, information): main-tree HEAD moved from the DSV2-R1 brief commit to the D-087 commit before the copy (three
coordinator commits), then to the 05:0xZ wiki and ledger commit (88445c1 after the coordinator's next push) by the end: the coordinator's push rewrote the unpushed range (the DSV2-R1 brief commit
is now 9845b52, the VERIFY-DSV2 report commit 7d53142; origin reads a1d4f70). 12623b3 is an ancestor of all of them. [Commit ids edited by the coordinator at harvest: the stale-id check refused the local ids.]
`git diff --stat 12623b3 HEAD` over the boundary files, `scripts/laya_ft`, the builder's other inputs (`scripts/decide-harvest`,
`scripts/transcript_export.py`, the three probe dirs, `src/agent_factory/decisions`) and the two other gate test files is EMPTY at
both checks (before the copy, and at 05:02Z after the worktree removal). The four main-tree boundary files hashed to their PIN
bytes just before the copy, and to my copies' bytes at the end.

D-10 (GitNexus `detect_changes`, main tree, information): the first try failed ("LadybugDB unavailable ... checkpoint is in
progress"); the retry rc 0: "6 files, 29 symbols, Risk level: high". The high risk comes from the SESSION-EXPORT lane's
`transcript_export.py` symbols (`scrub_strict`, `scrub_payload`, `_keylike` flows). Mine: `LEAKS` and
`test_leak_flags_mark_the_rows_and_leave_none_out`. It also lists `AP_ID_LEAK`, `overlap_norm` and the two version tests,
which only moved: their text is byte-identical to the PIN (checked; the v2 record test compared from its `def` to end of file).

## 11. NOT done

- No commit, no push, no git write in the main tree (the coordinator commits through `safe_commit.sh`).
- The seven follow-ups (V-3, V-4, V-9, V-11, V-15, V-16, V-17): untouched.
- V-6's "state the rule's vocabulary in the summary": not done. `summary.json` is regenerated, never hand-edited, and the
  builder's summary shape is outside "the `LEAKS` pattern only".
- The docs quoting the old count (D-7): not edited.
- No narrowing of any form for the false positives in D-1 to D-3 (as ruled).
- Tests not run in the main tree (shared, dirty by design); the full suite not run (only the brief's two calls).
- The GitNexus index was not re-analyzed.

## 12. Self-attack: the three likeliest ways this change is wrong

1. The combined regex is not what was ruled (a precedence slip across the concatenated fragments, a flag leaking between
   alternatives, a typo). Ruled out: the equivalence check parses the brief's own table and compares on 1,652 real states + 11
   edge strings (0 disagreements); the verifier's probe, whose regexes are the brief's, reads 0 unflagged per form; 24 of 26
   mutants die.
2. The record does not match the code that lands (built from the wrong tree, the builder edited after the build, the
   SESSION-EXPORT `transcript_export.py` read). Ruled out: built in the clean worktree at the PIN whose changed set is exactly
   the four files; the manifest's `build_dataset.py` hash `1c95e37a...` equals the copied file's sha256; its
   `transcript_export.py` hash is the PIN's; the gate's record test rebuilt twice more and matched; the copies `cmp`-equal the
   worktree.
3. The flags changed something a consumer reads besides the `leak` field (item ids, labels, row order, counts). Ruled out:
   `labels.jsonl` byte-identical; row diff `rows differing outside the leak field: 0` over 6,196 rows in the same order; the
   manifest diff shows only the code hash and the dataset's bytes and sha; the summary diff only the leak counts and the
   dataset sha.
(A fourth, the test as a mirror of the code: its states were written from the brief's table and checked against the brief's
patterns, it is red on the PIN, and it kills the mutants.)

## 13. Git writes and cleanup

- Git writes: the worktree add (04:3xZ) and `git -C /home/user/agent-factory worktree remove --force <scratch>/wt` (rc 0, 05:02:07Z);
  nothing else. `git worktree list` afterwards shows no dsv2-r1 entry (the other entry, `/tmp/cifix.mkxe4S`, is not mine).
- Main tree: the four boundary files were copied in with `cp` (each `cmp`-equal to the worktree) and this report was created. No
  git command wrote there. The SESSION-EXPORT lane's files (`scripts/transcript_export.py`, `tests/test_transcript_export.py`,
  `scripts/session_export.py`, `tests/test_session_export.py`, its report) were not touched.
- Scratch `<scratch>` = `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/dsv2-r1/`, 36 MB at the end
  (peak about 350 MB with the worktree and the pytest basetemp; the 101 MB basetemp was deleted). Kept for re-runs: `pin/` (the PIN
  rebuild, labels, summary, probe output, `fa_review.txt`), `new/` (the new rebuild, labels, summary, probe output), `v1/`, `red/`
  (the red copy, holding the PIN builder again), `probes/` (`blockwords_pin.py`, `blockwords_new.py`, `forms_review.py`, `mutate.py`,
  `bd_pin.py.txt`), `gate1.log`, `gate2.log`, `builder.diff`, `detect.json`.
- `python3 scripts/report_lint.py --root <worktree> <this report>`, three bounded fix rounds (AF-AP-76) on sections 0-7, pasted:
  round 1 `report_lint: 10 refs — OK 4, NEAR 0, MISS 4, UNCHECKABLE 2, UNRESOLVED 0 (worktree)`; round 2
  `report_lint: 12 refs — OK 10, NEAR 0, MISS 1, UNCHECKABLE 1, UNRESOLVED 0 (worktree)`; round 3
  `report_lint: 12 refs — OK 11, NEAR 0, MISS 0, UNCHECKABLE 1, UNRESOLVED 0 (worktree)` (the one UNCHECKABLE is the pasted pytest
  line `tests/test_laya_ft.py:1312: AssertionError`, left verbatim). The final read-only run over the whole report is the last
  line of the FILES section.

## FILES (each changed file's sha256 as copied into the main tree; re-read at 05:0xZ after the worktree removal)

```
1c95e37a0d99cfa874879bb0d1a9ee4674b2cfcedef9cbd749d77d6020c69297  scripts/laya_ft/build_dataset.py
b7f96af535195683c83088bb5f9f92998530e6d1b2c4cfe37a57c55b882ec449  tests/test_laya_ft.py
a7545005e26c09f769993146b1be220bc0f666130cde30e1d1fd713a1e14b4d1  docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
2b7f0d8a2101cb5a59682a795ad155830a20cede1450896d570fbeeaec9af5fd  docs/research/findings/laya-ft-labels/2026-09-25-recorded/summary.json
```

Unchanged, for reference: `docs/research/findings/laya-ft-labels/2026-09-25-recorded/labels.jsonl`
`0098e52e0dbfc01db12bfceb0a807db6fad533e10cf7380c72e368926375ca58` (= the PIN's).
CREATED: `tasks/briefs/jev-laya/DSV2-R1-report.md` (this file; its sha256 is in the hand-back message, taken after this last write).

Diffstat of the worktree before removal (`git diff --stat`, 12623b3 -> the four files):

```
 .../2026-09-25-recorded/dataset-manifest.json      |  6 +++---
 .../2026-09-25-recorded/summary.json               | 10 ++++-----
 scripts/laya_ft/build_dataset.py                   | 10 ++++++++-
 tests/test_laya_ft.py                              | 24 +++++++++++++++++++---
 4 files changed, 38 insertions(+), 12 deletions(-)
```

Final read-only lint of the whole report (no fix round after the three; each MISS is a correct number whose backticked
name wrapped onto the next report line, as the lint's own "cited line reads" shows):

```
report_lint: 22 refs — OK 17, NEAR 0, MISS 3, UNCHECKABLE 2, UNRESOLVED 0 (worktree)
```
