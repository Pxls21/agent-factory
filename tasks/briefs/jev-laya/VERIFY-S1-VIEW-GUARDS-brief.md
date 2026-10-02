# VERIFY-S1-VIEW-GUARDS (task #460): the adversarial verify of the S1 view's guards

Role: adversarial-verifier (sandbox, Opus 5.5). PIN: 0555298e (the landing on origin; full id in the premise).
Report: your FINAL MESSAGE is the report, whole. The harness may refuse a report-file Write from a subagent ("Subagents
should return findings as text"); never route around a refusal. The coordinator saves it as
`tasks/briefs/jev-laya/VERIFY-S1-VIEW-GUARDS-report.md`. Keep working notes in your own scratch directory. Do NOT spawn
subagents. Touch NO tracked file. Planting FAKE keys and markers in fixtures is defensive testing of the owner's own
data path (D-118: the scrub stays), authorized by the owner.

## THE SUBJECT

The landing 0555298e changed `scripts/s1_train/view.py` (357 to 429 lines) and `tests/test_s1_train_view.py` (61 to
92 tests), and added the build lane's report `tasks/briefs/jev-laya/S1-VIEW-GUARDS-report.md` (the lane's own report;
the coordinator replaced two local commit ids in its lines 3 and 21 before the push, nothing else).

**The frozen contract is `tasks/briefs/jev-laya/S1-VIEW-GUARDS-brief.md` at the PIN:** its decisions D-8 to D-12 and
its evidence demands 1 to 10, on top of D-1 to D-7 of `tasks/briefs/jev-laya/S3-5-VIEW-brief.md`, which stand. Attack
the code against THOSE, never against the builder's own tests or report. The builder's report names its one deviation
(its section 9: every `--out` in the tests moved outside any git work tree) and its open observations (its section 10).
Grade the deviation and each observation as contract-conformant, a sound reading of an open point, or a defect.

Why it matters: task #441 trains small heads on the states this view marks. The guards exist so that no state holds
text the agent had not seen when the hook ran (a hook of the carrier's own call, the call's own result) and no
candidate is a cut text. A guard that misses its shape poisons the training silently; a guard that drops a sound row
shrinks it silently.

**Round table (D-115).** Round 1: task #444, landing 92d74958, VERIFY-S3-5-VIEW returned MERGE-READY-WITH-FOLLOWUPS
with no blocker (follow-ups F1 to F3, 12 surviving mutants). Round 2: task #460, this landing, the first repair. No
blocker class recurs and no budget is spent.

## THE COORDINATOR'S REAL RUN (counts only; you never read these files)

The coordinator ran the landed `view.py` (its sha256 prefix `9ca2bece43af9a9f`) over the frozen build and the export
that task #444's real run used, in the sandbox. Its stdout, then its timing wrapper's line:

```
s1-view: 1091 build ids, 1091 found, 0 not in the export, 0 ambiguous, 0 dropped by the guards; 390 files, 202346 events, 172333 blocks, 170573221 characters rendered
rc=0 wall=306.7s peak_rss_mb=1447
```

`view.jsonl` is byte-equal to task #444's real run (sha256 prefix `29c5207de39d`). `summary.json` differs from that
run's only in five keys: the code hash of `scripts/s1_train/view.py`, `version` (`s1-view-v1` to `s1-view-v2`), and
the three new counts under `counts.not_found` (`same_call_hook_in_state`, `own_result_in_state`, `carrier_truncated`),
each 0.

## QUESTIONS (answer each with evidence; a question is not a claim)

**Q1. D-8, the guards, both ways.** Build the record orders O5 to O8 and q3b of `tasks/briefs/jev-laya/VERIFY-S3-5-VIEW-report.md`
through the real exporter and check each drop and its count. Then look for the misses and the false drops: a hook event
with the carrier's call id but another `hookEvent`; one whose text renders `""`; one whose text is not a JSON dict; a
call id reused by an earlier call (duplicated call ids); a run split by more than one non-hook event; a tool_result
carrier. Is an id that meets two guards counted once, under the first? Can a dropped id still count as `found` or
reach the label or split counts?

**Q2. `own_result_in_state` with a null call id (the builder's observation).** D-8's first guard requires a non-null
call id; its second does not say so. Does a carrier with a null call id meet the second guard through any `tool_result`
whose `call_id` is null? Can the real exporter write such a carrier or such a result? Grade it against D-8's wording.

**Q3. D-9, every refusal exits 2.** Find any input that still exits 1 (a traceback) or exits 0 with a wrong or partial
output. The builder named a build row whose `state.chunk` is not a string. Is any catch so broad that a defect in the
code reads as an input refusal? Does any refusal's reason on stderr carry session text (an exception message that
quotes the offending value)?

**Q4. D-10, `--out`.** A symbolic link to a directory, to a file, to an empty directory, dangling; an `--out` inside a
git work tree through a `.git` directory and through a `.git` file (a worktree or a submodule); a missing `--out`
whose nearest existing parent is in a tree; a symbolic link in a parent component (the builder's observation: it is
followed); the gap between the two `check_out` calls. Can any of these put an output inside a git work tree?

**Q5. D-11, the inputs.** An `output` that escapes the export directory (`../`, an absolute path, a symbolic link to
outside, a link inside the directory that points outside); one file named twice (`./a` against `a`, `d/../a`, a
symbolic link, a hard link); an event whose `src` differs from its entry's. Which does the code refuse? Is a hard link
"one file" under D-11's wording, and what does the code do with it?

**Q6. The tests.** Is the run test (F16) independent of the code's adjacency loop and of `render.block` and
`render.render`? Is any new test a mirror of the code it tests? Does the deviation (every `--out` outside a git tree)
hide a D-10 refusal, or weaken any test of the old fixture? Run NEW mutants (not the builder's 36; one exact edit
each, on a scratch copy, the baseline green first) on D-8 to D-11, and name each survivor.

**Q7. Normal behaviour, determinism, the boundary.** Is `view.jsonl` on the old fixture byte-equal to the one at the
round-1 landing 92d74958? Are two runs byte-identical, and two working directories? Does a dropped row's candidate
reach any output: `view.jsonl`, `summary.json`, stdout or stderr?

## EVIDENCE DEMANDS

1. Premise: re-run the block below at your HEAD; on any difference, stop and report CONTRACT-INVALID with the
   differing lines.
2. The builder's tests at the PIN, twice: `bash scripts/test_summary.sh tests/test_s1_train_view.py --basetemp <scratch dir>/bt`
   (paste each `pytest-summary:` line) and `bash scripts/pc_suite.sh set-id -- tests/test_s1_train_view.py`.
3. Every claim reproduced through the real code path (the CLI, or the module functions over exports the real exporter
   made from fixture transcripts), with the command and its output pasted.
4. The mutant table: each mutant's exact edit, the tests that failed, the survivors named.
5. Every observation reported, with no severity filter. Then the blocking predicate: a finding BLOCKS only when it
   shows the view's headline claim false (a written row whose state holds text the agent had not seen when the hook
   ran, through a shape a D-8 guard is defined to catch or through any other; a candidate that is not the injected
   text; a wrong label or split; an input check that passes a corrupted input and writes rows; a secret or thinking
   text in an output; an output written inside a git work tree) or contradicts a frozen D-rule (D-1 to D-12).
   Everything else is a follow-up.
6. A gate recommendation: MERGE-READY, MERGE-READY-WITH-FOLLOWUPS, NOT-READY or CONTRACT-INVALID. The coordinator owns
   the gate.

## STANDING RULES

No outward-facing action (no push, PR or comment); no network; no PC bridge. Never commit, stash, checkout or reset in
`/home/user/agent-factory`, and never write a tracked file there: make scratch copies (`git archive 0555298e` into your
scratch directory) for mutants and fixtures. Never read `.jev/`, the coordinator's scratchpad, `/root/.codiv/`,
`.pc-bridge.env`, any `*.env`, the pseudonym key under `/root/.config/session-export/`, any real export, or a real
transcript under `/root/.claude/projects/`; never run the exporter with `--known-values default`, nor
`scripts/known_values_check.py` with its default sources. FAKE strings for anything secret-shaped, built at run time,
never a literal; a test failure message names a canary, never its value. Long commands in ONE foreground call; no
background job. Never `cd` at a command's top level (wrap it: `( cd <dir> && ... )`). A pytest `--basetemp` parent
must exist first. Every test run with `PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=sandbox HF_HUB_OFFLINE=1`, no `-n`; set
`COLUMNS=1000` when a driver reads pytest's short summary (pytest cuts it to 80 columns off a terminal). Other lanes
may land commits while you work: the premise names the files that matter, and a change to any of them is a
stop-and-report.

## PREMISE — MEASURED at authoring (2026-10-02 05:5xZ, /home/user/agent-factory@0555298e)

Re-run each command at your HEAD; its output must match.

```
$ git rev-parse --verify 0555298e^{commit}
0555298e6c218a51374a52e7002a865ba18c3aba
$ git merge-base --is-ancestor 0555298e HEAD && echo the PIN is an ancestor of HEAD
the PIN is an ancestor of HEAD
$ git log -1 --format=%s 0555298e | cut -c1-120
Task #460 landed, gated pending verify: the S1 view's guards; the real run finds all 1,091 ids, drops none and repeats t
$ git diff --stat 0555298e HEAD -- scripts/s1_train tests/test_s1_train_view.py tasks/briefs/jev-laya/S1-VIEW-GUARDS-brief.md tasks/briefs/jev-laya/S1-VIEW-GUARDS-report.md tasks/briefs/jev-laya/S3-5-VIEW-brief.md scripts/session_export.py scripts/s1_scores.py scripts/hook_context.py scripts/laya_ft/build_s1.py scripts/laya_ft/common.py scripts/transcript_export.py tests/test_session_export.py | wc -l
0
$ git diff --stat 2979159415b0 0555298e -- scripts/s1_train/render.py scripts/s1_train/__init__.py scripts/session_export.py scripts/s1_scores.py scripts/hook_context.py scripts/laya_ft/build_s1.py scripts/laya_ft/common.py scripts/transcript_export.py tests/test_session_export.py | wc -l
0
$ git diff --stat 2979159415b0 0555298e -- scripts/s1_train/view.py tests/test_s1_train_view.py
 scripts/s1_train/view.py    | 164 ++++++++---
 tests/test_s1_train_view.py | 664 +++++++++++++++++++++++++++++++++++++-------
 2 files changed, 686 insertions(+), 142 deletions(-)
$ sha256sum scripts/s1_train/__init__.py scripts/s1_train/render.py scripts/s1_train/view.py tests/test_s1_train_view.py | awk '{print substr($1,1,16), $2}'
e3b0c44298fc1c14 scripts/s1_train/__init__.py
901c086a6a90f90a scripts/s1_train/render.py
9ca2bece43af9a9f scripts/s1_train/view.py
668e4b46b7e241da tests/test_s1_train_view.py
$ wc -l scripts/s1_train/render.py scripts/s1_train/view.py tests/test_s1_train_view.py
   125 scripts/s1_train/render.py
   429 scripts/s1_train/view.py
  1360 tests/test_s1_train_view.py
  1914 total
$ grep -n '^VERSION\|^def \|^class \|^GUARDS\|"not_found": {' scripts/s1_train/view.py
67:VERSION = "s1-view-v2"
69:GUARDS = ("same_call_hook_in_state", "own_result_in_state", "carrier_truncated")   # D-8, in the order they are met
85:class Refused(Exception):
89:def sha256_text(text):
93:def _flag(value):
97:def _inc(counter, key):
103:def read_build(bdir):
161:def read_manifest(edir):
191:def stream_events(path, entry):
231:def carriers(events, ids):
256:def facts_of(src, events, text, starts, ids):
299:def view(build, export):
376:def check_out(out):
396:def write(out, rows, summary):
411:def main(argv=None):
$ grep -c '^def test_' tests/test_s1_train_view.py
57
$ bash scripts/pc_suite.sh set-id -- tests/test_s1_train_view.py
1 files set=470c76f8303f
$ mkdir -p /tmp/p460v && PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=sandbox HF_HUB_OFFLINE=1 bash scripts/test_summary.sh tests/test_s1_train_view.py --basetemp /tmp/p460v/bt 2>&1 | grep pytest-summary | sed -E 's/ in [0-9.]+s.*//'; rm -rf /tmp/p460v
pytest-summary: 92 passed
$ sha256sum tasks/briefs/jev-laya/S1-VIEW-GUARDS-report.md tasks/briefs/jev-laya/S1-VIEW-GUARDS-brief.md tasks/briefs/jev-laya/VERIFY-S3-5-VIEW-report.md | awk '{print substr($1,1,12), $2}'
75679ba5c0f7 tasks/briefs/jev-laya/S1-VIEW-GUARDS-report.md
ff5878312bf3 tasks/briefs/jev-laya/S1-VIEW-GUARDS-brief.md
85fdf2dbfb50 tasks/briefs/jev-laya/VERIFY-S3-5-VIEW-report.md
```
