# SCRUB2-R1 round 2: the repairs after VERIFY-SCRUB2-R1 (task #321)

Authored 2026-09-28 12:4xZ by the coordinator. Lane: the SCRUB2-R1 builder, resumed (sandbox `code-implementer`,
Opus 5.5). Round 1's brief (`tasks/briefs/system1/SCRUB2-R1-brief.md`) still holds except where this file changes it.

## WHY

VERIFY-SCRUB2-R1 (`tasks/briefs/system1/VERIFY-SCRUB2-R1-report.md`) graded round 1 NOT-READY. It found three blockers
(B1 to B3), each reproduced through `export()` and `convert()`, each with a red test. The coordinator also ruled V4
blocking. Round 2 closes all four and folds in V5 and V21. Everything round 1 got right stays right.

## CONTRACT (round 2)

1. **B1 (V1): linear on backslash runs.** The pair alternative `\\\\(?!\\*[\"'])` in `_VE`, `_CV` and `_CL` re-scans a
   backslash run at every pair. Drop it or make it atomic in all three classes. Add backslash texts to the timing test
   (`LINEAR_CHILD`): a Cookie head, a `pwd` head and a `credentials` head, each followed by at least 32,000 backslashes,
   under the same wall-time bound. Then check every rule you changed in either round against backslash runs, not only
   dash and space runs. The class is a lookahead or an alternation that re-scans a run inside a quantified group. Task
   #333's three older rules stay out of this round, but no rule may get slower.
2. **B2 (V2): a Cookie value after an escaped line break.** After the Cookie head's colon, an escaped `\n`, `\r` or `\t`
   counts as whitespace. `_COOKIE_X` stops at a colon followed by an escaped line break. The three shapes of the red test
   `test_b2_...` are hidden in canonical JSON, in pasted JSON and in decoded text.
3. **B3 (V3): Negotiate never crosses a line.** The Negotiate token never takes a word from the next line (for example
   `[ \t]+` after `negotiate`, or a stop at a header name). The next header's Basic or Token credential is hidden in all
   four paths: `scrub`, `scrub_payload`, the digest and `convert()`.
4. **V4: no PIN redaction lost in any view (the coordinator's ruling).** Item 5 of round 1 ("no redaction the PIN makes
   may be lost") holds in every view: canonical JSON, the decoded digest and `convert()`'s decoded events. A literal
   backslash-n, -r, -t or -f in decoded text is two characters, as in a Windows path or a regex. It may no longer cut a
   `pwd` or `credentials` value, or end a Cookie line, where the PIN hid the whole value. You may add over-redaction to
   keep these redactions: for example, a literal escape followed by value characters continues the value. Report the
   added over-redaction's cost on the corpus, with counts and your reason, as round 1's item 6 did. F15's named
   over-redactions stay removed.
5. **V5: the six surviving mutants.** One assertion each kills M2, M3, M17, M20, M21 and M22 as a FAILED test. The
   verifier's section V5 describes each one. M22 needs a base64 Negotiate token (with `+`, `/` and `=`), the real SPNEGO
   shape; the committed test's fakes are hex.
6. **V21: comments match the code.** The Cookie rule's comment states its real time cost. The Negotiate rule's comment
   claims only the AF-AP-157 coverage the rule has.
7. **Everything round 1 made true stays true:** F1, F15, F2, F7, F10, F12 (the eleven survivors killed), the value gate,
   test isolation (no committed test opens a real source), the Laya lock (the pre-fit comparison again, with item
   counts), and item 6's measurement rows for each rule you change in this round.

Not in this round: V11 and V12 (they leak on the PIN too; task #319's scope), V10 (the edit screen; task #329), task
#333's older rules, F3, F8, F16, F17.

The verifier's `$V/candidate_te.py` (its V22) is a feasibility copy, not a spec. It closes B1 to B3 in scratch, but it
does not address V4, and nobody measured its item-6 rows. Read it; do not copy it blind.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below. Stop and report CONTRACT-INVALID on a mismatch that matters.
2. The verifier's six red tests (`$V/probes/test_vscrub2r1_red.py`), run in a scratch copy's `tests/`, never in the
   shared tree: 6 failed before your change (measured below), 6 passed after. Fold equivalent assertions into
   `tests/test_transcript_export.py`.
3. Before and after your change: the verifier's reproduction commands for B1, B2 and B3 (its sections V1 to V3), and
   `lost_shapes.py` and `rand_lost2.py` for V4. The LOST cells and the lost fake tokens go to 0. A cell you keep needs
   the ruling in item 4 and a stated reason.
4. Each new test has a named mutant that reds it as a FAILED test (AF-AP-223). The verifier's mutants M2, M3, M17, M20,
   M21 and M22 (`$V/probes/mutate_v.py`) are killed.
5. `bash scripts/test_summary.sh` twice on the floor's set (12 files set=27f27a25516b), pasted with its set id. Every
   red is fixed, or named with its cause.
6. pyflakes rc 0. `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0 for every file you write.
7. NOT-done and DISCREPANCIES.

## BOUNDARY

Round 1's BOUNDARY, unchanged: MODIFY `scripts/transcript_export.py` and `tests/test_transcript_export.py`. Only if
needed: `scripts/session_export.py` and `tests/test_session_export.py` (only `PATTERN_NAMES` and the F10 test), and
`scripts/known_values_check.py` and its test. The dataset manifests' code hash, by the builder's step. CREATE your report
`tasks/briefs/system1/SCRUB2-R1-R2-report.md`. READ everything else, including the verifier's scratch `$V`; never write
there.

## STANDING RULES

Round 1's STANDING RULES hold, with these changes:
- The coordinator re-applied round 1's patch to the shared tree. The five files are yours again, listed in `.lanes-live`.
- Two verifiers run in their own worktrees (`/tmp/vbce-wt`, `/tmp/vland-ci`, `/tmp/vland-s`). Never touch them.
- The disk is shared: about 1.2 to 1.4 GB free. Keep scratch under 200 MB in `.../scratchpad/scrub2r1/` and delete it
  as you go. `lane_gate` refuses below 1,500 MB, so use `scripts/test_summary.sh` with a short `--basetemp`.
- If the harness's classifier refuses a transcript read for item 6, stop that step and report it. Do not work around
  it; the coordinator runs the measurement then.
- If the harness refuses your report-file write, return the whole report as your final message.
- No subagents. No git writes. No PC bridge. No outward-facing action.

## PREMISE — MEASURED at authoring (2026-09-28 12:4xZ, the sandbox tree; HEAD = origin 2c234ca, before this brief's commit)

`$S` = `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad`; `$V` = `$S/vscrub2r1`. `$V/new` is the
verifier's patched copy (a `git archive` of HEAD plus the patch; its scrubber files have not changed since).

```
$ git rev-parse --short HEAD
2c234ca
$ git log --oneline cdbc1b8..2c234ca -- scripts/transcript_export.py scripts/session_export.py tests/test_transcript_export.py tests/test_session_export.py | wc -l
0
$ sha256sum tasks/briefs/system1/SCRUB2-R1.patch | cut -c1-16
e72a85cca2a3382d
$ cd $V/new && sha256sum <the five files> | cut -c1-16,65-
014439fb2694d273  scripts/transcript_export.py
0462fe2e9bdd14bc  scripts/session_export.py
00e7e9f80aedf16f  tests/test_transcript_export.py
c1bb29a1ec924a71  tests/test_session_export.py
449811004a7abed8  docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
$ sha256sum $V/probes/test_vscrub2r1_red.py $V/candidate_te.py | cut -c1-16
9ddf9f3cc3b3a34e  (test_vscrub2r1_red.py)
7f650748a0e60460  (candidate_te.py)
$ cd $V/new && masked.sh absent $V/new -- python3 -m pytest -q tests/test_vscrub2r1_red.py   (a copy of the file in tests/, removed after; 12:38:35Z)
FAILED tests/test_vscrub2r1_red.py::test_b1_the_named_rules_run_in_linear_time_on_a_backslash_run
FAILED tests/test_vscrub2r1_red.py::test_b2_a_cookie_value_on_the_next_line_is_hidden_in_json_as_in_text[headers:\n  Cookie:\n    session=%s\n]
FAILED tests/test_vscrub2r1_red.py::test_b2_a_cookie_value_on_the_next_line_is_hidden_in_json_as_in_text[Set-Cookie:\r\n  sid=%s]
FAILED tests/test_vscrub2r1_red.py::test_b2_a_cookie_value_on_the_next_line_is_hidden_in_json_as_in_text[Cookie:\nsid=%s]
FAILED tests/test_vscrub2r1_red.py::test_b3_a_negotiate_header_with_no_token_leaves_the_next_header_whole[Basic]
FAILED tests/test_vscrub2r1_red.py::test_b3_a_negotiate_header_with_no_token_leaves_the_next_header_whole[Token]
6 failed in 60.25s (0:01:00)
$ cd $V/probes && masked.sh absent $V/probes -- python3 lost_shapes.py | grep 'LOST'
cookie yaml next line                  dec:hid  raw:LOST  raw2:hid
cookie yaml next line CRLF             dec:hid  raw:LOST  raw2:hid
cookie colon then newline              dec:hid  raw:LOST  raw2:hid
cookie after literal-bs-n path         dec:LOST  raw:hid  raw2:hid
cookie after literal-bs-r              dec:LOST  raw:hid  raw2:hid
cookie literal-bs-t in value           dec:LOST  raw:hid  raw2:hid
cookie literal-bs-n in value           dec:LOST  raw:hid  raw2:hid
pwd literal-bs-n split short head      dec:LOST  raw:hid  raw2:hid
pwd literal-bs-t inside                dec:LOST  raw:hid  raw2:hid
pwd literal-bs-r inside                dec:LOST  raw:hid  raw2:hid
pwd literal-bs-f inside                dec:LOST  raw:hid  raw2:hid
credentials literal-bs-n split         dec:LOST  raw:hid  raw2:hid
credentials literal-bs-t inside        dec:LOST  raw:hid  raw2:hid
LOST cells: 13
$ grep -l -E 'transcript_export|known_values_check|session_export' tests/*.py | wc -w ; bash scripts/pc_suite.sh set-id -- <those files>
12
12 files set=27f27a25516b
```

Quoted, not re-run at authoring (the verifier's `$V/results.txt` line 12; your item 1 re-measures it):
`rand_lost2 (20000 texts, 10595 fakes): dec B-literal 93, dec N-eats 22 (13+9); raw F15-consistent 90; raw TRUE-LOSS NEW-dec-hides 20; NEW-dec-shows 28`.
