# DSV2-R1: the one focused repair of dataset v2 (task #251; D-031; VERIFY-DSV2 finding V-6)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/jev-laya/DSV2-R1-report.md` in the main
tree (write it incrementally from the start). This is the ONLY repair round DSV2 gets (D-031): repair V-6 and nothing else.

## GOAL

The version-2 dataset flags every finding state that states the blocking outcome in words (AMENDMENT 1 item 8 of
`tasks/briefs/jev-laya/DSV2-brief.md`). The verifier found the flags miss the blocking predicate stated as its walk ("Canonical:
yes. Material: yes.", "Predicate: not contract-mapped", "Not material"): 93 unflagged states per v1 question, 35 of them true
(38% against a 9.3% base rate). A training run selects on these flags (item 8), so a missing flag keeps a leaky row in training.
Finding V-6 in `tasks/briefs/jev-laya/VERIFY-DSV2-report.md` is the full evidence.

## THE RULE (the coordinator's ruling per form, read off the verifier's measurement below; copy, do not redesign)

Extend the `blocking-words` pattern in `LEAKS` (`scripts/laya_ft/build_dataset.py:143-148`; MODIFY) with exactly these five forms.
They stay ONE leak kind, `blocking-words`, as item 8 frames them:

| Form | Pattern (Python `re`) | Why |
|---|---|---|
| F-a the predicate walk | `(?i)\bcontract[- ]mapp\|\bcanonical(?: path\| reproduction)?\s*[:=]\|\bmaterial(?: effect)?\s*[:=]\|\bdiscriminator\s*[:=]\|\btask ownership\b\|\bin[- ]boundary\s*[:=]` | the blocking predicate's items stated with a value (item 8 names "blocking predicate") |
| F-b a class summary | `\bNo \[CLASS\]` | "No BLOCKER" after the mask |
| F-c a negated block | `(?i)\b(?:does not\|doesn't\|do not\|did not\|would not\|will not\|cannot) block\b` | the outcome in words; the old pattern had only "does not block" |
| F-d the class stated | `(?i)\b(?:is\|as) (?:a \|an )?\[CLASS\]` | the sibling of the flagged "not a [CLASS]" |
| F-e materiality stated | `(?i)\bno material effect\b\|\bnot material\b\|\bimmaterial\b` | the predicate's "materially effective" item |

(The `\|` above is the table's escape for `|`; the pattern has a plain `|`.) NOT added, with the reason: a bare "blocks" or
"blocked" (a domain verb: hooks and gates block calls; 5 true of 34, near the base rate); "hollow green" (names a defect, not the
outcome); "defence-in-depth", "optional hardening", "hypothetical" (a severity word; 1 true of 14, under the base rate); "must fix"
(1 row, false). If the F-a pattern flags a state whose words do not state the predicate (a false positive you can show), report it
in DISCREPANCIES with the row; do not narrow the pattern on your own.

## VENUE (load-bearing)

Work ONLY in a clean detached worktree at the PIN: `git -C /home/user/agent-factory worktree add --detach <scratch>/wt <PIN>`.
The main tree is shared: the SESSION-EXPORT lane's partial change to `scripts/transcript_export.py` sits there, and the record's
manifest hashes that file, so a record built in the main tree is wrong by construction (orchestration 0j). Edit, regenerate and
test in the worktree. At the end, copy exactly the changed boundary files into the main tree at the same paths, paste their
sha256, and remove the worktree (`git -C /home/user/agent-factory worktree remove --force <scratch>/wt`). Scratch:
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/dsv2-r1/` (the disk has about 2 GB free; stay under 500 MB).

## BOUNDARY

MODIFY: `scripts/laya_ft/build_dataset.py` (the `LEAKS` pattern only), `tests/test_laya_ft.py` (the `flag_leaks` unit test near
`:1290-1306`, extended), `docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json` and `summary.json`
(regenerated, never hand-edited). READ: everything else. `labels.jsonl` in the record must come out byte-identical; if it does not,
STOP and report. CREATE: your report. The seven follow-ups (V-3, V-4, V-9, V-11, V-15, V-16, V-17) are NOT this repair: report
anything adjacent, fix nothing outside the boundary.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below in your worktree; stop and report CONTRACT-INVALID on a mismatch that matters.
2. Red first: the extended unit test (one state per form F-a to F-e, each flagged `blocking-words`; two negatives, "the hook blocks
   the call" and "optional hardening", each unflagged) fails on the PIN's pattern. Show it by running the new test against a scratch
   copy that holds the PIN's `build_dataset.py`, then green on yours.
3. The record, regenerated at the build commit with your code, the way `tests/test_laya_ft.py:1323` does it:
   `build_dataset.py --version 2 --commit 434b727 --out <dir> --model-dir <the laya venue's model dir>` with the Laya venue's
   python, then `recorded_labels.py --dataset <dir> --out <labels> --summary <summary>`. Paste the old and new sha256 of the
   dataset, the manifest, `labels.jsonl` (must be unchanged) and `summary.json`, and the leak counts before and after.
4. The discriminator: the verifier's probe `scratchpad/verify-dsv2/probes/blockwords.py` (copy it; point `V` at your rebuild).
   Paste its full output. For each of F-a to F-e the unflagged count must read 0.
5. Version 1's byte clause still holds: the dataset at 0b342c7 is `d7cd9b49...` (`tests/test_laya_ft.py` covers it).
6. The gate, in your worktree, as TWO foreground calls (one run took 601 s under load; the tool caps a call at 600 s):
   `bash scripts/test_summary.sh tests/test_laya_ft.py` and
   `bash scripts/test_summary.sh tests/test_decide_harvest.py tests/test_recorded_labels.py`. Paste both summaries and each set id
   (`bash scripts/pc_suite.sh set-id -- <files>`).
7. `pyflakes` rc 0 on the changed Python files; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` prints 0 on every file you wrote.
8. NOT-done, and DISCREPANCIES (anything in the tree that disagrees with this brief).

## STANDING RULES

No network; no PC bridge; no outward-facing action; no git writes except your worktree's add and remove. FAKE strings for anything
secret-shaped. A pytest `--basetemp` parent must exist first.

## PREMISE — MEASURED at authoring (2026-09-25 04:3xZ, the sandbox clone at the PIN)

PIN: 12623b3 (the origin head; the boundary files are as DSV2 committed them at 71e540f).

```
$ git show 12623b3:<file> | sha256sum | cut -c1-16
f71590b4be1c7108  scripts/laya_ft/build_dataset.py
8e52b288ea722a0e  tests/test_laya_ft.py
efd3c91306cc967b  docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
0098e52e0dbfc01d  docs/research/findings/laya-ft-labels/2026-09-25-recorded/labels.jsonl
4fdd169cc9a05ec6  docs/research/findings/laya-ft-labels/2026-09-25-recorded/summary.json
f63cd97ef441b817  scripts/transcript_export.py
$ git show 12623b3:scripts/laya_ft/build_dataset.py | grep -n 'LEAKS = (\|"blocking-words"\|def flag_leaks'
143:LEAKS = (   # AMENDMENT 1 item 8, flagged per row (never a reason to leave one out; task #238 decides)
145:    ("blocking-words", re.compile(r"(?i)\bblocks? (?:the )?(?:merge|landing|push)\b|\bdoes not block\b"
409:def flag_leaks(rows, names):
$ bash scripts/pc_suite.sh set-id -- tests/test_decide_harvest.py tests/test_laya_ft.py tests/test_recorded_labels.py
3 files set=5d6a3ce56265
$ python3 scratchpad/verify-dsv2/probes/blockwords.py     (on the verifier's rebuild, byte-identical to the record, V-1)
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

A question for you, not a fact: the probe's "not a [CLASS] / is a [CLASS]" row counts both halves; F-d adds only "is a" and "as
a". Does F-d plus the old "not a" leave 0 unflagged in that row? If not, say which states remain.
