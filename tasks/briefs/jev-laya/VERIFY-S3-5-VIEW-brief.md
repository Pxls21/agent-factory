# VERIFY-S3-5-VIEW (task #444): the adversarial verify of the RWKV view of the S1 dataset

Role: adversarial-verifier (sandbox, Opus 5.5). PIN: 3d05e645 (the origin head after the landing; full id in the premise).
Report: your FINAL MESSAGE is the report, whole. The harness may refuse a report-file Write from a subagent ("Subagents
should return findings as text"); never route around a refusal. Keep working notes in your own scratch directory. Do
NOT spawn subagents. Touch NO tracked file. Planting FAKE keys and markers in fixtures is defensive testing of the
owner's own data path (D-118: the scrub stays), authorized by the owner.

## THE SUBJECT

The landing 92d74958 (`git log -1 --format=%s 92d74958` names it; the PIN, its child, only replaced two local commit
ids in the report by their subjects) created `scripts/s1_train/__init__.py`,
`scripts/s1_train/render.py`, `scripts/s1_train/view.py`, `tests/test_s1_train_view.py` (61 tests: 40 test functions, some parametrized) and the build
lane's report `tasks/briefs/jev-laya/S3-5-VIEW-report.md`.

**The frozen contract is `tasks/briefs/jev-laya/S3-5-VIEW-brief.md` at the PIN:** its decisions D-1 to D-7 and its
evidence demands 1 to 9. Attack the code against THAT, never against the builder's own tests or report. The builder's
report lists the places where it read the brief one way (its section 0: D-0 and I-1 to I-15); grade each one as
contract-conformant, a sound reading of an open point, or a deviation.

Why it matters: task #441 trains small heads on the states this view marks, and task #448 renders the live transcript
with the same render. A state that holds text the agent had not seen when the hook ran teaches the heads to read the
future; a wrong candidate, label or split poisons the training silently.

## THE COORDINATOR'S REAL RUN (counts only; you never read these files)

The coordinator ran the landed view over the frozen build `.jev/laya-ft/s1-2026-10-01-pushed` and the 2026-10-01
export (a scratch copy) in the sandbox, twice. Both runs exited 0 and wrote byte-identical files. The first run's stdout, then its timing wrapper's line:

```
s1-view: 1091 build ids, 1091 found, 0 not in the export, 0 ambiguous; 390 files, 202346 events, 172333 blocks, 170573221 characters rendered
rc=0 wall_s=299.6 peak_rss_mb=1447 user_s=293.7
```

| Count | The real run | The prototype (the build brief's last section) |
|---|---|---|
| build_ids / found / not_in_export / ambiguous | 1091 / 1091 / 0 / 0 | 1091 / 1091 / - / - |
| split heldout / train | 220 / 871 | 220 / 871 |
| carrier hook_additional_context / tool_result | 1087 / 4 | 1087 / 4 |
| hook_event PostToolUse / PreToolUse / UserPromptSubmit | 323 / 728 / 40 | 323 / 728 / 40 |
| hook_run_before 0 / 1+ | 30 / 1061 | 30 / 1061 |
| step_found true / false | 1051 / 0 | 1051 / - |
| time_equal true / false | 1091 / 0 | 1091 / - |
| whole true / false | 1091 / 0 | 1091 / - |
| candidate_vs_chunk equal / equal_prefix / differs | 432 / 659 / 0 | 432 / 659 / - |
| label false / true | 431 / 660 | not counted |
| render cut / scrub_changed / hook_unparsed | 14561 / 15175 / 0 | 14561 / 15175 / not counted |
| render events / blocks / chars | 202346 / 172333 / 170573221 | - / - / 170573221 |

The prototype's 4 tool_result carriers were PreToolUse denials, so its PreToolUse row (724) and the view's (728) count
the same carriers. `hook_unparsed` is 0, where the builder's report inferred about 3.

## QUESTIONS (answer each with evidence; a question is not a claim)

**Q1. D-3, the state's end.** Can any text the agent had NOT seen when the hook ran reach the rendered text before
`state_end` (a later event, a hook of the carrier's own run, the id itself)? Can the walk back over hook events cross
into an earlier run of hooks whose text the agent DID see, and what does that cost the state? Build the record orders
the harness writes (two parallel calls, a PostToolUse run followed by the next call's PreToolUse run, a Stop hook
feedback next to a prompt-time hook, a compaction between a call and its hooks) through the real exporter, never from
the builder's fixture alone.

**Q2. D-2, the carrier (the builder's I-1).** The code finds a tool_result carrier only when the result's `is_error` is
true, through `s1_scores.injections_of`. Can a hook denial be recorded with `is_error` false or absent? The two readers
join a tool_result's list parts differently (`scripts/s1_scores.py:140` with an empty string, the exporter's
`_text_of` at `scripts/session_export.py:273` with a newline): build the two-part denial and say which carriers the
live scorer (over the raw transcript) and the view (over the export) each find.

**Q3. D-2, the candidate.** Is the candidate always the text that was stamped, without its stamp line and its request
line, under the body rules without the cap? Try a stamped text with CR LF line ends, trailing blank lines, a request
line that is not the last line, the id inside the injected text, and a text the scrub changes.

**Q4. D-1, the render.** Each row of D-1's table; the body rules in their order; the cap at exactly 4,000 and 4,001
characters and the cut mark's N; a body the scrub lengthens or shortens across the cap; `starts` for events that render
nothing; an empty body. Is a block a function of its event alone, as task #448 needs?

**Q5. D-5, the inputs.** Shapes the builder did not try: a manifest entry whose `output` escapes the export directory
(`../`, an absolute path, a symlink); one file named by two entries through different spellings; an xz file holding two
streams; an event whose `seq` is a bool; a labels file with a blank line; a dataset row whose `sources` list is empty.
Which does the code refuse, which pass, and does any pass write a wrong row?

**Q6. D-6 and D-7, the outputs.** The keys of a view row and their types (`label` a JSON boolean), the sort, every
string value of `summary.json` (no session text), the `code` hashes (the builder's I-4: eight imported files outside
`scripts/` are not hashed; is that D-6's wording or a gap?), the `--out` checks (a symlink, a file, a non-empty
directory, a directory that appears between the two checks), byte identity across two runs and across two working
directories.

**Q7. Failure behaviour.** Every refusal must exit 2 with its reason on stderr and write nothing. Find any input that
makes the view exit 1 (a traceback) or exit 0 with a wrong or partial output (the builder named JSON nested past the
recursion limit).

**Q8. The tests.** Is any of the 61 a mirror of the code it tests? Run NEW mutants (not the builder's 14 demanded and 22
extra ones: one exact edit each, on a scratch copy, the baseline green first) on the rules above, and name each
survivor.

## EVIDENCE DEMANDS

1. Premise: re-run the block below at your HEAD; on any difference, stop and report CONTRACT-INVALID with the
   difference.
2. The builder's tests at the PIN, twice: `bash scripts/test_summary.sh --basetemp <scratch dir> tests/test_s1_train_view.py`
   (paste each `pytest-summary:` line) and `bash scripts/pc_suite.sh set-id -- tests/test_s1_train_view.py`.
3. Every claim reproduced through the real code path (the CLI, or the module functions over exports the real exporter
   made from fixture transcripts), with the command and its output pasted.
4. The mutant table: each mutant's exact edit, the tests that failed, the survivors named.
5. Every observation reported, with no severity filter. Then the blocking predicate: a finding BLOCKS only when it shows
   the view's headline claim is false (a state that holds text the agent had not seen when the hook ran; a candidate
   that is not the injected text; a wrong label or split; an input check that passes a corrupted input and writes
   rows; a secret or thinking text in an output) or contradicts a frozen D-rule. Everything else is a follow-up.
6. A gate recommendation: MERGE-READY, MERGE-READY-WITH-FOLLOWUPS, NOT-READY or CONTRACT-INVALID. The coordinator owns
   the gate.

## STANDING RULES

No outward-facing action (no push, PR or comment); no network; no PC bridge. Never commit, stash, checkout or reset in
`/home/user/agent-factory`, and never write a tracked file there: make scratch copies (`git archive 3d05e645` into your
scratch directory) for mutants and fixtures. Never read `.jev/`, the coordinator's scratchpad, `/root/.codiv/`,
`.pc-bridge.env`, any `*.env`, the pseudonym key under `/root/.config/session-export/`, any real export, or a real
transcript under `/root/.claude/projects/`; never run the exporter with `--known-values default`, nor
`scripts/known_values_check.py` with its default sources. FAKE strings for anything secret-shaped, built at run time,
never a literal; a test failure message names a canary, never its value. Long commands in ONE foreground call; no
background job. A pytest `--basetemp` parent must exist first. Every test run with `PYTHONDONTWRITEBYTECODE=1
S0_01_VENUE=sandbox HF_HUB_OFFLINE=1`, no `-n`; set `COLUMNS=1000` when a driver reads pytest's short summary (pytest
cuts it to 80 columns off a terminal). Other lanes may land commits while you work: the premise names the files that
matter, and a change to any of them is a stop-and-report.

## PREMISE — MEASURED at authoring (2026-10-01 21:5xZ, /home/user/agent-factory@3d05e645)

Re-run each command at your HEAD; its output must match.

```
$ git rev-parse --verify 3d05e645^{commit}
3d05e645c219924ebd97d0816cb1d85645203e1b
$ git merge-base --is-ancestor 3d05e645 HEAD && echo the PIN is an ancestor of HEAD
the PIN is an ancestor of HEAD
$ git log -1 --format=%s 3d05e645 | cut -c1-120
S3-5-VIEW report: two local commit ids replaced by their subjects before the push
$ git log -1 --format=%s 92d74958 | cut -c1-120
Task #444 landed (GATED-PENDING-VERIFY): the RWKV view of the S1 dataset; its real run equals the prototype on all 19 co
$ git diff --stat 92d74958 3d05e645 -- scripts/s1_train tests/test_s1_train_view.py | wc -l
0
$ git diff --stat 3d05e645 HEAD -- scripts/s1_train tests/test_s1_train_view.py tasks/briefs/jev-laya/S3-5-VIEW-brief.md scripts/session_export.py scripts/s1_scores.py scripts/hook_context.py scripts/laya_ft/build_s1.py scripts/laya_ft/common.py scripts/transcript_export.py tests/test_session_export.py | wc -l
0
$ git ls-files scripts/s1_train tests/test_s1_train_view.py tasks/briefs/jev-laya/S3-5-VIEW-report.md
scripts/s1_train/__init__.py
scripts/s1_train/render.py
scripts/s1_train/view.py
tasks/briefs/jev-laya/S3-5-VIEW-report.md
tests/test_s1_train_view.py
$ sha256sum scripts/s1_train/__init__.py scripts/s1_train/render.py scripts/s1_train/view.py tests/test_s1_train_view.py | cut -c1-16
e3b0c44298fc1c14
901c086a6a90f90a
16f1905ce72aee78
439c3fc55d0d5c3f
$ wc -l scripts/s1_train/render.py scripts/s1_train/view.py tests/test_s1_train_view.py
  125 scripts/s1_train/render.py
  357 scripts/s1_train/view.py
  888 tests/test_s1_train_view.py
 1370 total
$ grep -n '^VERSION\|^CAP, HEAD, TAIL\|^CUT_MARK\|^LABELS\|^def ' scripts/s1_train/render.py
34:VERSION = "s1-render-v1"
35:CAP, HEAD, TAIL = 4000, 3000, 1000          # characters of a body, after the scrub and the newline rule
36:CUT_MARK = "\n[... %d characters cut ...]\n"  # %d: the body's length minus CAP
40:LABELS = {("owner", "text"): "Owner", ("coordinator", "text"): "Coordinator", ("agent", "text"): "Agent",
53:def _count(counts, key):
58:def newlines(text):
63:def clean(text, counts=None):
71:def body(text, counts=None):
80:def injections(a):
88:def hook_text(text, counts=None):
100:def block(event, counts=None):
117:def render(events, counts=None):
$ grep -n '^VERSION\|^CODE = \|^EVENT_KEYS\|^TARGETS\|^STEP_EVENTS\|^def ' scripts/s1_train/view.py
52:VERSION = "s1-view-v1"
57:EVENT_KEYS = frozenset(("seq", "src", "line", "ts", "role", "kind", "tool", "call_id", "text", "truncated", "outcome",
59:TARGETS = {(0.0, 1.0): True, (1.0, 0.0): False}     # the joined target over the options ["false", "true"]
60:STEP_EVENTS = ("PreToolUse", "PostToolUse")
63:CODE = ("scripts/decide-harvest", "scripts/hook_context.py", "scripts/laya_ft/__init__.py", "scripts/laya_ft/build_s1.py",
73:def sha256_text(text):
77:def _flag(value):
81:def _inc(counter, key):
87:def read_build(bdir):
144:def read_manifest(edir):
161:def stream_events(edir, entry):
198:def carriers(events, ids):
223:def facts_of(src, events, text, starts, ids):
247:def view(build, export):
318:def check_out(out):
327:def write(out, rows, summary):
339:def main(argv=None):
$ grep -c '^def test_' tests/test_s1_train_view.py
40
$ grep -n '^def injections_of\|^def stamp_of\|^HOOK_ERROR_RX\|^PLAIN_EVENTS' scripts/s1_scores.py
67:PLAIN_EVENTS = ("UserPromptSubmit", "SessionStart")        # the events whose plain stdout reaches the model
70:HOOK_ERROR_RX = re.compile(r"([A-Za-z]+):(\S+) hook error: \[")
117:def injections_of(r):
160:def stamp_of(kind, text):
$ grep -n '^def _text_of' scripts/session_export.py
254:def _text_of(content):
```
