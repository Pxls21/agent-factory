# S1-VIEW-GUARDS (task #460): the S1 view's guards, from VERIFY-S3-5-VIEW's follow-ups

Role: code-implementer (sandbox, Opus 5.5). PIN: 29791594 (the origin head at authoring; full id in the premise).
The coordinator commits other work in the same tree while you run; the premise therefore checks that the PIN is an
ancestor of HEAD and that your boundary files are unchanged since it, never where `origin` points.
Report: your FINAL MESSAGE is the report, whole (the harness may refuse a subagent's Write of a report file; the
coordinator saves it as `tasks/briefs/jev-laya/S1-VIEW-GUARDS-report.md`). Do NOT spawn subagents. Touch ONLY the
files in the boundary; report adjacent defects, never fix them. Planting FAKE keys and markers in fixtures is
defensive testing of the owner's own data path (D-118: the scrub stays), authorized by the owner.

## WHY

Task #444 landed the RWKV view of the S1 dataset: `scripts/s1_train/render.py` and `scripts/s1_train/view.py`, built
to `tasks/briefs/jev-laya/S3-5-VIEW-brief.md`, whose pinned decisions D-1 to D-7 stay the contract. Its adversarial
verify, `tasks/briefs/jev-laya/VERIFY-S3-5-VIEW-report.md`, returned MERGE-READY-WITH-FOLLOWUPS. Three record orders,
built through the real exporter, break the view's headline claim:
- F1: a non-hook event splits a hook run, so a hook of the carrier's own call or prompt lands in the state;
- F2: a call's result is written before its PreToolUse run, so the call's own output lands in the state;
- F3: the exporter cut the carrier, so the candidate silently loses its middle.

None of the three is in today's export: the coordinator's counts-only run over the real export and the real view
read 0, 0 and 0 over 1,091 rows (2026-10-01 22:3xZ, ledger). Task #441 trains on the view, and a later export may hold
those orders. This task makes the claim hold by construction. Each such row is counted and dropped. Every refusal
exits 2. The tests gain the items behind the verifier's 12 surviving mutants.

Round table (D-115): round 1 is task #444 (`92d74958`), verified by VERIFY-S3-5-VIEW: MERGE-READY-WITH-FOLLOWUPS, no
blocker, follow-ups F1 to F3 above and 12 surviving mutants. This is the first repair of the view; no blocker class
recurs and no budget is spent.

## GOAL

1. `scripts/s1_train/view.py` drops and counts the three shapes (D-8), exits 2 on every refusal (D-9), refuses a
   symlinked `--out` and one inside a git work tree (D-10), and checks three more input facts (D-11).
2. `tests/test_s1_train_view.py` gains the fixture items and tests of D-12, so that each of the verifier's 12 surviving
   mutants is killed or shown equivalent, and the run test no longer mirrors the code.

## BOUNDARY

- MODIFY `scripts/s1_train/view.py`, `tests/test_s1_train_view.py`.
- READ, never modify:
  - `scripts/s1_train/render.py`: D-1 does not change, and its `VERSION` stays `s1-render-v1`;
  - `scripts/session_export.py`, `scripts/s1_scores.py`, `scripts/hook_context.py`, `scripts/laya_ft/build_s1.py`,
    `scripts/laya_ft/common.py`, `scripts/transcript_export.py`, `tests/test_session_export.py`: the same reads as
    the S3-5-VIEW brief's boundary;
  - `tasks/briefs/jev-laya/S3-5-VIEW-brief.md` (the contract), `tasks/briefs/jev-laya/S3-5-VIEW-report.md` (the
    builder's readings), `tasks/briefs/jev-laya/VERIFY-S3-5-VIEW-report.md` (the findings, the record orders O1 to
    O9, Q7's inputs, Q8's fixture gaps and the mutant table with each exact edit).
- Every other file is out of bounds. The verifier's scratch scripts are not yours to read: build your fixtures from
  the report's descriptions.

## PINNED DECISIONS (D-1 to D-7 stand; these add to them; a conflict with the tree is a STOP-and-report)

**D-8 Three guards after D-3.** D-3 gives each found id a `state_event`; let `s` be its index in the file's events.
The guards are these three, in this order:
- `same_call_hook_in_state`: the carrier's call id is not null, and some event before index `s` is a hook event whose
  text parses as a JSON dict that renders (`render.block(event)` is not `""`), whose `toolUseID` equals that call id,
  and whose `hookEvent` equals the row's `hook_event` (the verify report's O5, O7, O8). The call id is the
  attachment's `toolUseID` for a hook carrier and the event's `call_id` for a tool_result carrier, as `carriers()`
  gives it now.
- `own_result_in_state`: the row's `hook_event` is `PreToolUse`, its carrier is not `tool_result`, and a `tool_result`
  event whose `call_id` equals the call id lies before index `s` (O6).
- `carrier_truncated`: the carrier event's `truncated` is not null (the report's q3b).

A row that meets a guard is not written, and its id is not counted `found`. It is counted once, under the name of the
first guard it meets, in `counts.not_found`. That dict always holds five keys: `ambiguous`, `not_in_export` and the
three guard names. The stdout line gains `, N dropped by the guards` after the ambiguous count. D-3's refusal of an id
seen before its state ends is checked before the guards and still refuses the whole view. `summary.json`'s `version`
becomes `s1-view-v2`. These definitions are the ones the verifier's counts-only measure used. Copy them; do not
redesign them.

**D-9 Every refusal exits 2.** D-5 asks for exit 2 with nothing written; four inputs exited 1 with a traceback (the
report's Q7a to Q7d, F13). Turn these into `Refused`, with the input named in the reason:
- `RecursionError`, `TypeError` and `ValueError` raised while an input is read and checked (the manifest, an export
  file, an event, the build);
- `OSError` raised while `--out` is created or written.

Catch them where the input is read, never with a bare `except Exception` around `main`.

**D-10 `--out`.** Refuse (exit 2, nothing written) an `--out` that is a symbolic link, to anything, an empty
directory included (F14). Also refuse one whose path, or whose nearest existing parent, lies inside a git work tree: a
`.git` entry, file or directory, in that directory or any parent. D-6 already says the output lives outside git. Use
no subprocess. Both `check_out` calls apply both rules.
AMENDED 2026-10-02 11:5xZ (D-134, the owner's REDESIGN after the D-115 review of task #460): first refuse (exit 2,
nothing written) an `--out` with a `..` part. A part that does not exist yet changes what a later `..` names once
`os.makedirs` creates it, so no check of the text can tell which entry the kernel will open (rounds 2 and 3: B1 and
B2). Without a `..` the two rules above are exact.

**D-11 Three input facts (D-5's verification, extended; F9, F10, F12):**
- a manifest entry's `output` must resolve, after symbolic links, inside the export directory;
- two entries whose outputs resolve to one file are refused, the same as two entries with one spelling (the
  builder's I-6);
- each event's `src` must equal its manifest entry's `src`.

Each failure is a refusal (exit 2) that names the entry.

**D-12 The tests (F15, F16, F25).** The fixture gains the items Q8 lists:
- a split run (O5, O7 and O8, each dropped as `same_call_hook_in_state`);
- a call's result before its PreToolUse run (O6, dropped as `own_result_in_state`);
- an exporter-cut carrier (q3b, dropped as `carrier_truncated`);
- a denial with its call's PreToolUse hooks before it;
- a run at a file's first event;
- a run of exactly two LFs;
- ids out of state order;
- a candidate over 4,000 characters;
- a CR or a double LF in a chunk;
- `step_found` false;
- duplicated call ids. `step_event` is the LAST tool_call with the carrier's call id before `state_event`: pin it
  (F25).

Each of the 12 surviving mutants (N1, N10, N14, N15, N19, N20, N26, N31, N33, N39, N49, N53; the exact edits are in
the report's mutant table) goes red on a named test, or the report shows it equivalent with the reason. One expected
case: D-10 refuses every symbolic link before `os.path.lexists` is reached, so N19 may become equivalent. The run
test derives each carrier's run from the fixture's own hook records, by `toolUseID` and `hookEvent` (F16), never from
the code's adjacency loop and never through `render.block` or `render.render`. N20 is killed by calling `write()` on
a directory that holds a file. The Q7 inputs (D-9) and the D-10 and D-11 refusals each get a test that asserts exit 2
and the named reason.

Out of scope, reported only if you meet them: F4 and F5 (which "seen" the heads train on: a question for task #441),
F11 (a dropped manifest entry: needs a source of completeness), F17 (a blank line inside a cut block: D-1), F7 and F24
(the exporter), F23 (a crash between the two output writes).

## EVIDENCE DEMANDS

1. Premise: re-run the block below at your HEAD. On any difference, stop and report CONTRACT-INVALID with the
   differing lines.
2. Fixtures through the REAL producers, as in task #444: raw transcript records modeled on
   `tests/test_session_export.py`'s builders, exported by the real exporter (`init-key` FAKE key, a fixture repo,
   `--known-values key-only`), and a frozen build written by `build_s1.write_split`. A shape the exporter cannot be
   made to write (the q3b cut needs a stamped text whose JSON escaping grows past the exporter's 32,768-character cap)
   is built by the exporter if at all possible. If it is not, say how you built it and why.
3. Normal behaviour: every id the old fixture found is still found, with the same row bytes (`view.jsonl` byte-equal
   to the PIN's on the PIN's fixture). The new items are found or dropped as D-8 says, each with its count.
4. Failure behaviour: each D-9, D-10 and D-11 refusal, and each existing refusal, asserts exit 2 and the reason.
5. Security boundary: the existing marker, FAKE key and own-id tests still pass. No dropped row's candidate reaches
   any output.
6. Determinism: two runs, byte-identical outputs.
7. Mutants on a scratch copy of the two files, one exact edit each, the baseline green first, `COLUMNS=1000` in the
   run's environment (pytest cuts its summary lines at 80 columns otherwise). The set: the verifier's 12 survivors,
   plus each guard of D-8 off, the guard order swapped, each D-9 catch removed, each D-10 rule off, each D-11 check
   off, and `step_event` from the first call. Paste the table: the edit, killed or survived, and the test that failed.
8. Tests run twice: `bash scripts/test_summary.sh tests/test_s1_train_view.py --basetemp <your scratch dir>/bt`
   (paste each `pytest-summary:` line) and `bash scripts/pc_suite.sh set-id -- tests/test_s1_train_view.py`. Keep
   the file under two minutes.
9. Gates: `pyflakes` on both files; `python3 scripts/ap_screen.py <both files>` (paste its tells and answer each);
   the separator check on both (`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0; it exits 1 when it prints 0).
10. NOT run here: the real run. After landing, the coordinator runs `view.py` over the real export and the frozen
    build. The expected result: `view.jsonl` byte-equal to task #444's real run, three zero guard counts, and the
    same 19 counts. You never read those files.

## STANDING RULES

No outward-facing action (no push, PR or comment); no network; no PC bridge. Never commit, stash, checkout or reset in
`/home/user/agent-factory` (the coordinator commits). Never read `.jev/`, the coordinator's scratchpad, `/root/.codiv/`,
`.pc-bridge.env`, any `*.env`, the pseudonym key under `/root/.config/session-export/`, or a real transcript under
`/root/.claude/projects/`; never run the exporter with `--known-values default`, nor `scripts/known_values_check.py`
with its default sources. FAKE strings for anything secret-shaped, built at run time. Long commands in ONE foreground
call; no background job. Never `cd` at a command's top level (wrap it: `( cd <dir> && ... )`). A pytest `--basetemp`
parent must exist first. Every test run with `PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=sandbox HF_HUB_OFFLINE=1`, no `-n`
(no xdist here). The coordinator lands other work in this tree while you run: touch nothing outside the boundary, and
expect `git log` to move. Your final message is the report: files and lines, the pasted counts, the mutant table,
discrepancies, and what is NOT done.

## PREMISE — MEASURED at authoring (2026-10-02 03:1xZ, /home/user/agent-factory@2979159415b0)

```
$ git merge-base --is-ancestor 2979159415b0629ae4d564e5e62ca912aa01a9a8 HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ git diff --stat 2979159415b0629ae4d564e5e62ca912aa01a9a8 -- scripts/s1_train/ tests/test_s1_train_view.py | wc -l
0
$ git log -1 --format='%h %s' -- scripts/s1_train/ tests/test_s1_train_view.py | cut -c1-110
92d74958 Task #444 landed (GATED-PENDING-VERIFY): the RWKV view of the S1 dataset; its real run equals the pro
$ sha256sum scripts/s1_train/__init__.py scripts/s1_train/render.py scripts/s1_train/view.py tests/test_s1_train_view.py | awk '{print substr($1,1,16), $2}'
e3b0c44298fc1c14 scripts/s1_train/__init__.py
901c086a6a90f90a scripts/s1_train/render.py
16f1905ce72aee78 scripts/s1_train/view.py
439c3fc55d0d5c3f tests/test_s1_train_view.py
$ wc -l scripts/s1_train/render.py scripts/s1_train/view.py tests/test_s1_train_view.py
  125 scripts/s1_train/render.py
  357 scripts/s1_train/view.py
  888 tests/test_s1_train_view.py
 1370 total
$ bash scripts/pc_suite.sh set-id -- tests/test_s1_train_view.py
1 files set=470c76f8303f
$ mkdir -p /tmp/p460 && PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=sandbox HF_HUB_OFFLINE=1 bash scripts/test_summary.sh tests/test_s1_train_view.py --basetemp /tmp/p460/bt 2>&1 | grep 'pytest-summary' | sed -E 's/ in [0-9.]+s.*//'; rm -rf /tmp/p460
pytest-summary: 61 passed
$ grep -n '^def \|while j > 0\|lexists\|before\[-1\]\|s1-view-v1\|"not_found": {' scripts/s1_train/view.py
52:VERSION = "s1-view-v1"
73:def sha256_text(text):
77:def _flag(value):
81:def _inc(counter, key):
87:def read_build(bdir):
144:def read_manifest(edir):
161:def stream_events(edir, entry):
198:def carriers(events, ids):
223:def facts_of(src, events, text, starts, ids):
232:        while j > 0 and events[j - 1]["kind"] == "hook":     # back over the run of hooks that holds the carrier
238:                          "step_event": events[before[-1]]["seq"] if before else None,
247:def view(build, export):
268:    counts = {"build_ids": len(ids), "found": 0, "not_found": {"ambiguous": 0, "not_in_export": 0}, "carrier": {},
318:def check_out(out):
321:        if os.path.lexists(out) and not (os.path.isdir(out) and not os.listdir(out)):
327:def write(out, rows, summary):
339:def main(argv=None):
$ sha256sum tasks/briefs/jev-laya/VERIFY-S3-5-VIEW-report.md | cut -c1-12
85fdf2dbfb50
```

## What the real data showed (the coordinator, counts only; you never read these files)

```
# the verifier's counts-only measure (D-8's three definitions) over the real export and task #444's real view, 2026-10-01 22:3xZ
{"carrier_not_relocated": 0, "carrier_truncated": 0, "own_result_in_state": 0, "rows": 1091, "same_call_hook_in_state": 0}
# D-11's three facts over the same export, 2026-10-02 03:1xZ (outputs inside the export directory, resolved outputs unique, every event's src equal to its entry's)
{"entries": 390, "inside": 390, "outside": 0, "resolved_dupes": 0, "events": 202346, "src_mismatch": 0}
```

So after landing, the real run must find the same 1,091 rows, drop none, and refuse nothing.
