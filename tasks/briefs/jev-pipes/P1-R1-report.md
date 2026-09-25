# P1-R1 report: the one focused repair of the P1 replay instrument (task #267; D-031; VERIFY-P1 F-PERSIST and G-PASS)

Lane: sandbox build (code-implementer, Opus 5.5). Brief: `tasks/briefs/jev-pipes/P1-R1-brief.md`. PIN: e8c14bf. Repair key
(D-031): task #231, seed `seed_5aa221965993` v1.0.0, production digest `replay_pruner.py` f10df15241c34828. Started
2026-09-25 09:21Z (clock `date -u`: 09:21:22). No subagent, no git write, loopback only, the live Laya server not used, no PC
bridge. Scratch: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/p1-r1/` (below: `$S`).

STATUS: DONE (10:0xZ). R-1, R-2 and R-3 done; each evidence demand has a section below.

## 1. Premise re-measure (evidence demand 1) [verified, 09:21Z-09:27Z]

```
$ git show e8c14bf:<file> | sha256sum | cut -c1-16   vs   sha256sum <file> (shared tree)
f10df15241c34828  f10df15241c34828  scripts/jev_pipes/replay_pruner.py
28b097e1ad7f67f6  28b097e1ad7f67f6  tests/test_jev_pipes_replay.py
d54c2746bfc50e2c  d54c2746bfc50e2c  tests/fixtures/jev_pipes/make_fixture.py
797329fdac2a446a  797329fdac2a446a  docs/research/findings/jev-pipes/P1-replay-2026-09-25.md
7789b1c8c983f9e6  7789b1c8c983f9e6  scripts/jev_pipes/accounting.py
1e6f77216996d2f5  1e6f77216996d2f5  scripts/jev_pipes/transcript.py
54e1212d125e2654  54e1212d125e2654  scripts/jev_pipes/bridge.mjs
$ git diff e8c14bf HEAD -- scripts/jev_pipes/ tests/test_jev_pipes_replay.py tests/fixtures/jev_pipes/ | wc -l    -> 0
$ git diff e8c14bf -- scripts/jev_pipes/ tests/test_jev_pipes_replay.py tests/fixtures/jev_pipes/ | wc -l         -> 0
$ sed -n '165p' scripts/jev_pipes/replay_pruner.py
    chars_saved = result["charsBefore"] - result["charsAfter"] if pruned else 0
$ bash scripts/test_summary.sh tests/test_jev_pipes_replay.py
pytest-exit: 0
pytest-summary: 34 passed in 13.50s
$ bash scripts/pc_suite.sh set-id -- tests/test_jev_pipes_replay.py
1 files set=17f6a5adc0c9
$ python3 $S/pass_path.py /home/user/agent-factory $S/premise <variant>   (the verifier's probe, copied unchanged)
persisted | harness PASS 21 0 0.0 49962.8 0 49962.8 | oracle PASS 0 43231.3 | diffs 1 [['toolu_pp_px', 'chars_saved', 3085, 1263]]
v0        | harness PASS 20 0 0.0 37290.1 0 37290.1 | oracle PASS 0 37290.1 | diffs 0 []
v1        | harness PASS 20 1 0.05 37768.2 2077 35691.2 | oracle PASS 1 35691.2 | diffs 0 []
v2        | harness FAIL 20 2 0.1 38086.9 4273 33813.9 | oracle FAIL 2 33813.9 | diffs 0 []
v1neg     | harness PASS 20 0 0.0 64221.9 0 64221.9 | oracle PASS 0 64221.9 | diffs 0 []
$ VARIANTS=v0,v1,v2,v1neg python3 $S/mutate.py $S/pin-tree $S/pin-probe    (the verifier's driver, unchanged; a static copy)
M1 suite 34 passed | M2 34 passed | M3 34 passed | M4 2 failed | M5 34 passed | M6 2 failed | M7 14 failed | M8 4 failed
M9 34 passed | M10 34 passed        -> six of ten survive: M1, M2, M3, M5, M9, M10 (same as VERIFY-P1 section 8)
```

`$S/pin-tree` is a static copy of the PIN (`git archive e8c14bf -- <the 12 paths the test file reads>`, 82 files, 688K; a
read, nothing written to the repository). The lane's suite runs there: `34 passed in 13.39s`. After the driver, the three
mutated files are back at their PIN hashes (f10df15241c34828, 1e6f77216996d2f5, 54e1212d125e2654).

Two discrepancies, neither one matters:

- PD-1 [verified]: the persisted row reads `3085 vs 1263` here, `3083 vs 1261` in the brief. The footer the pruner renders
  names the persisted file's absolute path, and my scratch path is 2 characters shorter than the verifier's (126 against
  128 characters, measured), so the rendered output is 2 characters shorter and both savings are 2 higher. The mechanism
  and the ratio (x2.4) are the same. Every test below computes such lengths from the fixture's own paths.
- PD-2 [verified]: the brief's "0 diff lines" holds for its three paths. The findings directory
  `docs/research/findings/jev-pipes/` holds five newer files of the SBS1 lane (b63bc66, f9b8dfb); the P1 findings report
  itself is unchanged (797329fdac2a446a at the PIN and in the tree).

## 2. R-2 first: the PASS-path tests, red on the PIN's harness (evidence demand 2, the red half) [verified, 09:4xZ]

New fixture `tests/fixtures/jev_pipes/make_pass_fixture.py`: the builder and the oracle, ported from VERIFY-P1's
`probe/pass_path.py`. The oracle imports nothing from `scripts/jev_pipes/`; a test holds that import boundary. The port is
byte-identical to the verifier's builder on the five variants they share (both built into one directory, since a persisted
record carries its absolute path), and the two oracles agree row by row (chars saved, following calls, next context, miss)
and on the bar:

```
$ python3 $S/port/compare_port.py $S
v0 bytes_equal True 195552 5f95fee06d8a | oracle rows 20 vs 20 | per-row saved/following/context/miss equal True | bar PASS 0 37290.1 vs PASS 0 37290.1
v1 bytes_equal True 197394 ff91e362266c | oracle rows 20 vs 20 | per-row saved/following/context/miss equal True | bar PASS 1 35691.2 vs PASS 1 35691.2
v2 bytes_equal True 199227 6bfbf53e3914 | oracle rows 20 vs 20 | per-row saved/following/context/miss equal True | bar FAIL 2 33813.9 vs FAIL 2 33813.9
v1neg bytes_equal True 251337 b0559ab172d2 | oracle rows 20 vs 20 | per-row saved/following/context/miss equal True | bar PASS 0 64221.9 vs PASS 0 64221.9
persisted bytes_equal True 204642 4fbf6965e04c | oracle rows 21 vs 21 | per-row saved/following/context/miss equal True | bar PASS 0 43260.8 vs PASS 0 43260.8
```

Two variants are ADDITIONS to the brief's five (flagged, section 9): `edge20` (a token at the 20th lookahead item and a
re-run at the 20th call: inside, so both count) pins the window's inside edge, which no variant of the five reaches; and
`persisted_miss` pins R-1's miss baseline both ways. After its first persisted result a tool input uses a token only the FILE
holds (no miss: the model never saw it). After its second, a tool input uses a token the stub showed and the prune dropped
(a miss). Result 14 carries stderr, and a later tool input uses a token only the stderr holds: no miss, because the hook
keeps stderr. That result is the negative control for "a non-persisted result is unchanged", the only row where the text
the model saw differs from the pruner's input (a forced or inverted `persisted` condition survives without it).

The new tests on the PIN's `replay_pruner.py` (shared tree, before any harness edit; `sha256sum | cut -c1-16` =
f10df15241c34828):

```
$ python3 -m pytest tests/test_jev_pipes_replay.py -q -p no:cacheprovider
FAILED tests/test_jev_pipes_replay.py::test_pass_path_pruned_rows_end_to_end[persisted]
FAILED tests/test_jev_pipes_replay.py::test_pass_path_pruned_rows_end_to_end[persisted_miss]
2 failed, 40 passed in 21.74s
$ python3 -m pytest tests/test_jev_pipes_replay.py -q -p no:cacheprovider -k pass_path     (the diff lists, verbatim)
[persisted]
  ('toolu_pp_px', 'chars_saved', 3125, 1303)
  ('toolu_pp_px', 'persisted', False, True)
  ('toolu_pp_px', 'tokens_saved', 11545.566502463056, 4814.0394088669955)
  ('summary', 'tokens_saved', 50110.591133004935, 43379.06403940888)
  ('summary', 'net', 50110.591133004935, 43379.06403940888)
  ('summary', 'char_keep_rate', 0.6646067767594313, 0.6908869935108622)
[persisted_miss]
  ('toolu_pp_pxa', 'chars_saved', 3125, 1303)
  ('toolu_pp_pxa', 'miss', True, False)
  ('toolu_pp_pxa', 'miss_cost', 2364, 0)
  ('toolu_pp_pxa', 'persisted', False, True)
  ('toolu_pp_pxa', 'miss_tokens>0', True, False)
  ('toolu_pp_pxa', 'tokens_saved', 13084.975369458129, 5455.911330049262)
  ('toolu_pp_pxb', 'chars_saved', 3125, 1303)
  ('toolu_pp_pxb', 'persisted', False, True)
  ('toolu_pp_pxb', 'tokens_saved', 13854.679802955667, 5776.847290640395)
  ('summary', 'misses', 2, 1)
  ('summary', 'miss_rate', 0.09090909090909091, 0.045454545454545456)
  ('summary', 'miss_cost', 4924, 2560)
  ('summary', 'verdict', 'FAIL', 'PASS')
  ('summary', 'tokens_saved', 68054.43349753697, 52347.53694581282)
  ('summary', 'net', 63130.43349753697, 49787.53694581282)
  ('summary', 'char_keep_rate', 0.6296653672469026, 0.6772948063270644)
2 failed, 6 passed, 34 deselected in 6.26s
```

Each R-1 site is red for its own reason: site 1 (`chars_saved`, the file's 3,125 against the stub's 1,303), site 2
(`toolu_pp_pxa` counted as a miss on a token only its file held; in `persisted_miss` it turns a PASS into a FAIL), and
site 3 (`char_keep_rate`). The `persisted` flag is the row field site 3 needs (it does not exist at the PIN). v0, v1, v2,
v1neg and edge20 pass on the PIN: its non-persisted accounting agrees with the oracle, and so does result 14's.

## 3. R-1: the repair, and the green half of evidence demand 2 [verified, 09:5xZ]

The three sites, confirmed on the PIN's bytes (`git show e8c14bf:scripts/jev_pipes/replay_pruner.py | cat -n`). All three have
one shape, the pruner's input standing in for the text the model saw; none lies outside the boundary:

```
   123	        source = persisted_text if cand.persisted else (result or {}).get("stdout")
   165	    chars_saved = result["charsBefore"] - result["charsAfter"] if pruned else 0
   186	        hits, rerun = accounting.miss(source, answer["output"], history, [i.tokens for i in look], calls, cand.rerun_key)
   220	    chars_before = sum(r["source_chars"] or 0 for r in rows)
```

PIN line 165 subtracts `charsBefore`, the length of the pruner's input (`vendor/jev-pruner/src/output.ts:554`), which
for a persisted result is the file:
`scripts/jev_pipes/bridge.mjs:237` (`persisted_text`).
PIN line 186 passes the file text as the miss baseline (PIN line 123). PIN line 220 sums the bridge's output length, again
the file:
`scripts/jev_pipes/bridge.mjs:242` (`out.source_chars`).
The stub is what the model saw: the tool result's text, whose length is `cand.chars`; the hook caps the pruned output at
that stub:
`vendor/jev-pruner/hooks/fast-jev-output.ts:197-202` (`maxChars`).

The change, in `scripts/jev_pipes/replay_pruner.py` only (GitNexus impact: `decision_row` LOW, `summarize` LOW, one caller
each, `main`; graft: the row's saving fields are read only by `summarize` and `accounting.verdict`):

- `scripts/jev_pipes/replay_pruner.py:160` (`decision_row`) takes `seen`, the text the model saw, beside `source`; its
  one caller passes `job["answer"]["text"]` (`scripts/jev_pipes/replay_pruner.py:338`, `main`).
- Site 1, `scripts/jev_pipes/replay_pruner.py:170` (`chars_saved`): `cand.chars - charsAfter` for a persisted result,
  `charsBefore - charsAfter` otherwise, as before.
- Site 2, `scripts/jev_pipes/replay_pruner.py:188` (`baseline`): the miss check's original text is `seen` for a persisted
  result, `source` otherwise; `:192` (`accounting.miss(baseline`) uses it.
- Site 3, `scripts/jev_pipes/replay_pruner.py:228` (`chars_before`): `result_chars` for a persisted row, `source_chars`
  otherwise. The row gains the field it needs, `"persisted"` (`scripts/jev_pipes/replay_pruner.py:183`). A row logged
  before this repair has no such key and counts as before (`r.get`); section 6 shows that this moves nothing in the
  committed logs.

This settles VERIFY-P1's F-MISS-BASELINE (UNVERIFIED there) the way the brief rules: a token only the file held is not a
miss, because the model never saw it in either world. The `persisted_miss` variant reproduces the old behaviour (a miss on
such a token, which turns a PASS into a FAIL) and pins the new one.

Green, the same tests on the repaired harness (`sha256sum | cut -c1-16` = 615f1974630e5408):

```
$ python3 -m pytest tests/test_jev_pipes_replay.py -q -p no:cacheprovider      (shared tree, right after the edit)
42 passed in 19.35s
$ cd $S/r1-tree && bash scripts/test_summary.sh tests/test_jev_pipes_replay.py   (static copy: PIN archive + the 3 files)
pytest-exit: 0
pytest-summary: 42 passed in 19.55s
```

And red once more with the FINAL test files on a PIN copy (`$S/pin-red-tree`: the PIN's `replay_pruner.py`
f10df15241c34828, the test file d96f54bc5a4b2138, the fixture 61df6a072962104d), the same 22 diff lines as section 2:

```
$ cd $S/pin-red-tree && bash scripts/test_summary.sh tests/test_jev_pipes_replay.py
pytest-exit: 1
pytest-summary: 2 failed, 40 passed in 19.51s
_______________ test_pass_path_pruned_rows_end_to_end[persisted] _______________
____________ test_pass_path_pruned_rows_end_to_end[persisted_miss] _____________
```

## 4. The mutation table rerun (evidence demand 3) [verified, 09:5xZ]

Driver `$S/mutate_r1.py` (VERIFY-P1's `probe/mutate.py` adapted): one exact replacement at a time in the static copy
`$S/r1-tree`, never in the shared tree. Each mutant's anchor is checked to match exactly once, the COMMITTED suite runs,
and the file is restored from a scratch copy and checked by sha256. After all 22, the five mutated files read their
repaired hashes again (615f1974630e5408, 7789b1c8c983f9e6, 1e6f77216996d2f5, 54e1212d125e2654, 61df6a072962104d). The
verifier's external oracle column is gone: that oracle is inside the committed suite now.

M1-M9 use the verifier's replacement strings unchanged. **M10 is re-expressed (a deviation of the text, not of the mutant):**
its PIN line is the line R-1 changed, so "the saving doubled" doubles the repaired expression. M11-M22 are this repair's
own attacks.

| # | Mutant | Red on (named tests) |
|---|---|---|
| M1 | a token miss not counted | `test_pass_path_pruned_rows_end_to_end[v1]`, `[v2]`, `[edge20]`, `[persisted_miss]` |
| M2 | a re-run miss not counted | `[v2]`, `[edge20]` |
| M3 | a miss costs nothing | `[v1]`, `[v2]`, `[edge20]`, `[persisted_miss]` |
| M4 | `Index.following` ignores the boundary | `test_accounting_fixture_end_to_end[replay]`, `[unbudgeted]`, and all seven pass-path variants |
| M5 | `decision_row` counts every later request | all seven pass-path variants |
| M6 | `few_chunks` by the harness's own line count | the two `test_accounting_fixture_end_to_end` and all seven pass-path variants |
| M7 | `document` by size over 12,000 | 14 of the lane's tests (the fail-open set and more) |
| M8 | the history not reset at a compaction | 11 tests, the lane's four and all seven pass-path variants |
| M9 | the lookahead starts one item late | `[v1neg]` |
| M10 | the saving doubled (re-expressed) | all seven pass-path variants |
| M11 | site 1 reverted (a persisted saving from the file) | `[persisted]`, `[persisted_miss]` |
| M12 | site 2 reverted (a persisted miss baseline from the file) | `[persisted_miss]` |
| M13 | site 3 reverted (a persisted keep-rate denominator from the file) | `[persisted]`, `[persisted_miss]` |
| M14 | site 1 over-applied (every saving from the model's text) | `[persisted_miss]` |
| M15 | site 2 over-applied (every miss baseline from the model's text) | `[persisted_miss]` |
| M16 | site 3 over-applied (every denominator from the model's text) | `[persisted_miss]` |
| M17 | a persisted result never misses | `[persisted_miss]` |
| M18 | the item window one short (19) | `[edge20]` |
| M19 | the call window one short (19) | `[edge20]` |
| M20 | the call window starts one call late | `[v2]`, `[v1neg]` |
| M21 | the 5% bar made strict (`accounting.py`) | `test_accounting_tokens_saved_and_the_bar`, `[v1]` |
| M22 | the oracle imports the harness | `test_pass_path_oracle_imports_nothing_from_the_harness` |

The driver's summary lines, verbatim (two calls, to stay under the tool's time cap; full logs `$S/mutate-r1-a.log`,
`$S/mutate-r1-b.log`):

```
SUMMARY: killed 11 of 11: ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11']; survivors: []
SUMMARY: killed 11 of 11: ['M12', 'M13', 'M14', 'M15', 'M16', 'M17', 'M18', 'M19', 'M20', 'M21', 'M22']; survivors: []
```

Each new mutant is red for its own reason, not an incidental one (`$S/why_red.py`: the mutant applied, the
`persisted_miss` variant alone, its diff lines):

```
M12: ('toolu_pp_pxa', 'miss', True, False); ('toolu_pp_pxa', 'miss_cost', 2364, 0); ... ('summary', 'verdict', 'FAIL', 'PASS')
M14: ('toolu_pp_14', 'chars_saved', 692, 647); ('toolu_pp_14', 'tokens_saved', 1363.5467980295568, 1274.8768472906406); ...
M15: ('toolu_pp_14', 'miss', True, False); ('toolu_pp_14', 'miss_cost', 2427, 0); ... ('summary', 'verdict', 'FAIL', 'PASS')
M16: ('summary', 'char_keep_rate', 0.6775959683942014, 0.6772948063270644)
M17: ('toolu_pp_pxb', 'miss', False, True); ('toolu_pp_pxb', 'miss_cost', 0, 2560); ('toolu_pp_pxb', 'miss_tokens>0', False, True); ...
```

M14's 692 against 647 is result 14's stderr line and its newline (45 characters), the only row where the model's text and
the pruner's input differ. Before the repair, six of ten survived (section 1); now none of the 22 survives.

## 5. Gates (evidence demand 4) [verified, 09:5xZ]

```
$ bash scripts/test_summary.sh tests/test_jev_pipes_replay.py        (run 1, shared tree, 09:54Z)
pytest-exit: 0
pytest-summary: 42 passed in 19.28s
$ bash scripts/test_summary.sh tests/test_jev_pipes_replay.py        (run 2)
pytest-exit: 0
pytest-summary: 42 passed in 19.21s
$ bash scripts/pc_suite.sh set-id -- tests/test_jev_pipes_replay.py
1 files set=17f6a5adc0c9
$ pyflakes scripts/jev_pipes/replay_pruner.py tests/test_jev_pipes_replay.py tests/fixtures/jev_pipes/make_pass_fixture.py
(no output) rc=0          (pyflakes 3.4.0; its negative control, a planted unused import in scratch, reads rc=1)
$ LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>        -> 0 for each of:
scripts/jev_pipes/replay_pruner.py, tests/test_jev_pipes_replay.py, tests/fixtures/jev_pipes/make_pass_fixture.py,
docs/research/findings/jev-pipes/P1-replay-2026-09-25.md, tasks/briefs/jev-pipes/P1-R1-report.md, and the scratch scripts
```

The set id is the brief's (17f6a5adc0c9): one file, the same path; the count moved from 34 to 42 (the seven variants and
the import-boundary test). One wasted call, stated: my first pyflakes line set its program name in a `( )` subshell, so the
shell ran the `.py` file itself ("Permission denied", rc 126); that was my command, not pyflakes, and the rerun above is
the gate.

Further gates, pasted:

```
$ python3 scripts/report_lint.py tasks/briefs/jev-pipes/P1-R1-report.md --min-refs 10     (this report, final)
report_lint: 13 refs — OK 13, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
$ python3 scripts/ap_screen.py <the three .py files>          -> 6 hits (AP-32, sha256 lines), rc 0
$ python3 scripts/ap_screen.py --tests <test file, new fixture> -> 9 hits (AP-66 x8, AF-AP-80 x1), rc 0
every flagged line's text is already in the PIN's files (checked line by line): no hit is on a line this repair wrote
$ seed verify commands: AC1 4 | AC2 42 passed in 19.55s | AC3 PINNED | AC5 11 passed, 31 deselected in 8.71s | AC6 IGNORED
```

## 6. The committed FAIL does not move (evidence demand 5) [verified, 09:5xZ]

All five committed decision logs (`.jev/pipes/`, mode 600), summarized by the PIN's `summarize` (`$S/pin-tree`) and by the
repaired one over the same rows, per set (primary, secondary Read, secondary Grep), every key compared (`$S/logs/summ.py`):

```
p1-decisions-plan-all.jsonl: rows 3525 modes ['plan-all'] pruned 0 chars_saved>0 0 persisted-key 0 | PIN-vs-R1 summary keys differing 0 [] new keys [] | primary verdict FAIL pruned 0 net 0 char_keep_rate 1.0
p1-decisions-plan.jsonl: rows 3492 modes ['plan'] pruned 0 chars_saved>0 0 persisted-key 0 | PIN-vs-R1 summary keys differing 0 [] new keys [] | primary verdict FAIL pruned 0 net 0 char_keep_rate 1.0
p1-decisions-sample.jsonl: rows 360 modes ['replay'] pruned 0 chars_saved>0 0 persisted-key 0 | PIN-vs-R1 summary keys differing 0 [] new keys [] | primary verdict FAIL pruned 0 net 0 char_keep_rate 1.0
p1-decisions-unbudgeted.jsonl: rows 60 modes ['unbudgeted'] pruned 0 chars_saved>0 0 persisted-key 0 | PIN-vs-R1 summary keys differing 0 [] new keys [] | primary verdict FAIL pruned 0 net 0 char_keep_rate 1.0
p1-decisions.jsonl: rows 3492 modes ['replay'] pruned 0 chars_saved>0 0 persisted-key 0 | PIN-vs-R1 summary keys differing 0 [] new keys [] | primary verdict FAIL pruned 0 net 0 char_keep_rate 1.0
```

So F-PERSIST moves no committed figure. None of the 10,929 rows was pruned, none carries a non-zero saving, and the two
harnesses agree on every summary key of every set. The keep rate stays 1.0 whatever its denominator, because the
numerator is 0.

## 7. R-3: the two sentences of the findings report [verified, 09:5xZ]

`docs/research/findings/jev-pipes/P1-replay-2026-09-25.md`, the word diff against the PIN (`git diff --word-diff=plain
e8c14bf`), and nothing else in the file:

- Headline (`docs/research/findings/jev-pipes/P1-replay-2026-09-25.md:4`, "main transcript"): "in this session (3,153)"
  now reads "in this session's main transcript (3,153; the Bash results of its subagent transcripts, counted in
  `tasks/briefs/jev-pipes/VERIFY-P1-report.md` C-1h, were not replayed)" (F-SCOPE).
- Section 6 (`docs/research/findings/jev-pipes/P1-replay-2026-09-25.md:101`, "least state"): "the one real request whose
  chunk may have been partly visible (3,133 characters before it) scored 0.5494-0.5502" now reads "the one real request
  with the least state before its chunk (3,133 characters) scored 0.5494-0.5502, but its chunk was not visible either
  (`tasks/briefs/jev-pipes/VERIFY-P1-report.md` 1(b)-i), so only the synthetic probe above shows the answer for a chunk
  the model can see" (N-3).

No number changes: every number of the old file is in the new one, and the only digits added are the `1`s of `VERIFY-P1`,
`C-1h` and `1(b)-i` (a multiset compare of the numbers: `numbers added: {'1': 4} | numbers removed: {}`). The facts
behind the second sentence were re-read from the full-set log: 294 requests sent, the least state before a chunk is 3,133
characters, one request (byte offset 38,608, Bash, HTTP 200, scores 0.5494 to 0.5502). The verifier's counts (5,774
subagent Bash results; 961 tokens against a room of 855) are cited by section, not restated: I did not re-measure them.

## 8. Self-attack: the three likeliest ways this repair is wrong [10:0xZ]

1. **The new tests mirror the fix: the oracle shares the code's assumption.** Ruled out four ways. The oracle imports
   nothing from `scripts/jev_pipes/`, and a test holds that (M22 red). Its builder is byte-identical to VERIFY-P1's on
   the five shared variants, and its values agree row by row with the verifier's oracle, which was written before this
   repair (section 2). Its persisted rule is the seed's definition, "characters removed from the expensive model's input",
   computed from the fixture's own stub text, never from `cand.chars`. Its non-persisted rule (stdout) comes from the
   hook, which swaps only stdout and keeps stderr (`vendor/jev-pruner/hooks/fast-jev-output.ts:264`, `stdout`), not from
   the harness. Last, on the PIN the new tests are red only for the persisted variants, for the three sites' own reasons,
   and green wherever the PIN was already right.
2. **The repair changes what a non-persisted result counts; the brief says it stays unchanged.** Ruled out. v0, v1, v2,
   v1neg and edge20 hold the same oracle values on the PIN and on the repair. Result 14 is the one row whose model-visible
   text differs from the pruner's input (its stderr). It pins the non-persisted branch of all three sites: each
   over-applied mutant fails there alone (M14, M15, M16). The five committed logs summarize identically under both
   harnesses, every key of every set (section 6).
3. **`cand.chars` and the pruner's `charsAfter` are different units.** Python counts code points, JavaScript counts
   UTF-16 units, so a stub with characters above U+FFFF would be overcounted by up to that count, and in a corner the
   saving could go negative. NOT ruled out in general; measured harmless here. In the main transcript (pinned at
   720,578,154 bytes), 40 persisted results of 2,000+ characters have stubs of 2,035 to 2,213 characters, and 0 of them
   holds such a character (`$S/astral.py`, counts only). The brief's contract names `cand.chars`, so I kept it. Switching
   to UTF-16 units (`len(seen.encode("utf-16-le")) // 2`, and the same in the keep rate) would be a deviation, so it is
   reported here for the coordinator, not made.

Smaller risks, checked: `decision_row` gained a positional parameter, and its one caller is `main` (GitNexus impact
LOW; grep finds no other caller, and the tests reach it only through `main`). A pre-repair row has no `persisted` key, and
`summarize` reads it as before (`r.get`); section 6 shows this moves nothing in the committed logs.

## 9. NOT done, DISCREPANCIES, DEVIATIONS and ADDITIONS (loud) [10:0xZ]

NOT done:

- No commit, no push (the coordinator's). No live run: the local scorer cannot prune (VERIFY-P1), so every pruned row
  here comes from the synthetic fixture and a loopback fake scorer. The live Laya server was not contacted (0 requests).
- AF-AP-211 stays OPEN in `docs/INCIDENT-LOG.md` (outside this boundary; its status is the coordinator's). Echo, read
  only: nothing in `scripts/`, `src/` or `harness-ports/` outside `scripts/jev_pipes/` reads `persistedOutputPath` or
  `charsBefore`. Inside `scripts/jev_pipes/`, `bridge.mjs` reads the file as the pruner's input (correct, the hook does
  the same), and `transcript.py` only flags a persisted result. No fourth site.
- Not in this brief, so not touched: VERIFY-P1's N-1 (the findings' prefix median, 49,926, is the Bash-only value
  labelled "all 294"), F-GITIGNORE (`vendor/*`), N-10 (an empty `--sources` glob), N-11 (scores outside [0, 1]). The
  unit residual (section 8, item 3) is open.
- Wiki, ledger and task DB: the coordinator's.

DISCREPANCIES:

- PD-1 and PD-2 (section 1): the persisted row's saving shifts by 2 with the scratch path's length; the SBS1 lane's files
  share the findings directory. Neither matters.
- R-3's "say so, measured": the boundary allows the findings report the two sentences only, so the statement that
  F-PERSIST moves no committed figure, with its measurement, is here (section 6), not in the findings. The corrected
  sentences add no number: they cite the verify report's sections (C-1h, 1(b)-i) for the counts I did not re-measure
  (5,774; 961 against 855). If the coordinator wants those numbers inline, that is a two-word edit.
- The findings report's section 7 still says the independent verify round "has not run". VERIFY-P1 has run since, so the
  sentence is stale. It is outside my two sentences, so I left it (adjacent).

DEVIATIONS (each flagged, none self-accepted as a contract change):

- M10's replacement text is re-expressed on the repaired line (section 4); the mutant, "the saving doubled", is the same.
- `decision_row` takes a new positional parameter `seen` (the text the model saw), and its row gains the field
  `persisted`. Site 2 needs the text and site 3 needs the flag. The seed's row fields are all still there.

ADDITIONS beyond the brief's named variants (each kills a mutant nothing else kills):

- `edge20` (the inside edge of both 20-windows; kills M18 and M19). `persisted_miss` (the miss baseline both ways, plus
  result 14's stderr control; kills M12, M14, M15, M16, M17). `test_pass_path_oracle_imports_nothing_from_the_harness`
  (kills M22). The brief's five variants are there unchanged; `persisted` is VERIFY-P1's case byte for byte.

## 10. Adjacent observations (reported, not fixed)

- A-1: `main` keys candidates by (path, byte offset) (`chosen`), and `transcript.windows` yields one snapshot per
  tool-result block. A user record with two big tool results would pair both snapshots with one candidate. It has not
  happened: 0 of the 3,492 pointers in `.jev/pipes/p1-decisions.jsonl` has two rows (0 of 360 in the sample log). Stated
  as a structural risk only.
- A-2: the findings report's section 7 (stale verify-round sentence), above.

## 11. Files (sha256 at 10:0xZ)

```
MODIFIED:
615f1974630e5408d47d225e0f2d9829d2688322ffc80f9e6be08726c6485278  scripts/jev_pipes/replay_pruner.py        (+18 -5)
d96f54bc5a4b21385a22ffec2a41f82b0083344d1c3289ecccb65f326c1d8294  tests/test_jev_pipes_replay.py            (+77 -1)
9cee9d538f9bb331ab2205c398862842ef55c6379503c4c9396f2b50fca5872e  docs/research/findings/jev-pipes/P1-replay-2026-09-25.md (the two sentences)
CREATED:
61df6a072962104d8278386bc9211bdf440cf5b2ed1cd266071c13461e6edf50  tests/fixtures/jev_pipes/make_pass_fixture.py (252 lines)
tasks/briefs/jev-pipes/P1-R1-report.md (this report; not hashed, it would contain its own hash)
UNCHANGED (PIN hashes, checked): tests/fixtures/jev_pipes/make_fixture.py d54c2746bfc50e2c, scripts/jev_pipes/accounting.py
7789b1c8c983f9e6, scripts/jev_pipes/transcript.py 1e6f77216996d2f5, scripts/jev_pipes/bridge.mjs 54e1212d125e2654
```

The other lane's files in the tree (`scripts/session_export.py`, `scripts/transcript_export.py`, their tests,
`tasks/briefs/jev-laya/SESSION-EXPORT-R1-report.md`) were not touched. GitNexus `detect_changes` over the whole tree reads
7 files, 112 symbols and risk "critical"; the critical flows are that lane's (`Cmd_gate` into the scrub functions). This
lane's changed symbols are `decision_row`, `summarize` and `main` (an AST compare against the PIN; `open_log` is listed
by line-window overlap only, its body is byte-identical) and the two findings sections.
