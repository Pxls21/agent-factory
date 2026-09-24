# JT2-R1 report — the one focused repair of the Jev bug locator and bug-echo (tasks #227, #229; D-031)

Lane: jt2-r1 (sandbox, `code-implementer`, Opus 5.5, shared tree, no worktree). Written incrementally.

## 0. Premise (evidence item 1) — MATCHED

Re-measured 2026-09-24 17:13:23Z (`date -u`), local HEAD `83c03f8f8eda67aafef89d1829f231759f438481`.

```
f25e3219e9bd scripts/jev_context.py        (HEAD blob = worktree blob)
70720f113389 scripts/jev_locate.py         (HEAD blob = worktree blob)
79ab68f0ce63 scripts/jev_echo.py           (HEAD blob = worktree blob)
60af25fa3823 tests/test_jev_context.py     (HEAD blob = worktree blob)
b5a110aafe74 tests/test_jev_locate_echo.py (HEAD blob = worktree blob)
scripts/jev_echo.py@83c03f8:37:SIDE_CHARS = 560
scripts/jev_echo.py@83c03f8:317:        query = "the defect: %s; fixed as: %s" % (...[:SIDE_CHARS], ...[:SIDE_CHARS])
scripts/jev_context.py@83c03f8:55:JEV_QUERY_CHARS = 1000
scripts/jev_context.py@83c03f8:755:def jev_query(text):   (body: t = str(text).strip(); return t[-JEV_QUERY_CHARS:])
scripts/jev_context.py@83c03f8:777:        opts["venue"] = "local"
scripts/jev_context.py@83c03f8:784:            res = jev.rank(jev_query(query), ...
```

Every line of the brief's PREMISE block reproduced byte for byte. No mismatch; work proceeds.

## 1. The defect, reproduced on the PIN tree (17:2xZ, recording loopback double, `--no-jev-log`)

Scratch double and driver under the session scratchpad (`jt2r1/double.py`, `repro.py`, `repro40.py`), the REAL
`scripts/jev_echo.py` as a subprocess and the REAL `jev_context.jev_rank`:

```
de06db6 rc=0 requests=6 distinct sent=1 built chars=1013 sent chars=1000 starts with 'the defect: ': False
40543ab rc=0 requests=1 distinct sent=1 sent chars=1000 starts with the label: False      (default instruments)
locator: question chars=2000 jev_query chars=1000 sent chars=1000 | sent ends with the question's last words: False |
  tail: 'ted> password=<redacted> password=<redac'
```

(40543ab with only `rg-token,rg-shape` found no candidate site, so Jev was not asked: `requests=0`; with the default
instruments, graft included, it was.) F-20 and F-21 hold as the verifier stated them. The alignment commit is
`d03e7c4` on this tree; the brief and the verifier name its pre-push SHA `e0d2bdc` (both objects exist; same change).

## 2. The set: every query JT2 sends to `jev.rank` (enumerated before the fix)

`jev.rank` has ONE JT2 call site: `scripts/jev_context.py@83c03f8:784` (inside `jev_rank`), which passes `jev_query(query)`.
Everything JT2 ranks goes through it. The builders that reach it:

| # | builder (what the query is) | built at | reaches `jev_rank` via | at the PIN |
|---|---|---|---|---|
| Q1 | the locator's bug text: the CLI argument, or `--from-file`'s last 4,000 characters | `scripts/jev_locate.py:81-95` (`read_question`) | `scripts/jev_locate.py:137` `rank_chunks` -> `scripts/jev_locate.py:73` `jc.jev_rank` | raw tail 1,000 cut BEFORE rank's scrub: loses its last words when the scrub lengthens it (F-21) |
| Q2 | bug-echo's labelled query `"the defect: %s; fixed as: %s"` | `scripts/jev_echo.py@83c03f8:317` | `scripts/jev_echo.py@83c03f8:318` `rank_chunks` -> `scripts/jev_locate.py:73` `jc.jev_rank` | up to 1,144 characters, tail-cut: loses its label and head (F-20) |
| Q3 | the A3 bench input (a registry mechanism cell) | `docs/research/findings/jev-locate-bench/bench.py` (`select`) | `docs/research/findings/jev-locate-bench/bench.py:190` `jc.jev_rank(c["input"], ...)` | same path as Q1 (outside my boundary; its 20 committed inputs are at most 933 characters) |

Instrument search texts (`search_text()` at most 300 characters to graft, GitNexus and codebase-memory; the echo's
`graft ask "code like: " + snippet[:200]`; rg `-e` patterns) never reach `jev.rank`; they are not Jev queries.
The chunk texts (`jev_text`, at most 400 characters of text plus a path) stay under rank's 2,500 chunk cut; F-08
(tokens, not characters) is a contract matter (D-080), not this repair.

Instruments, all agreeing (17:3xZ): GitNexus `impact jev_query` (risk HIGH, 6 impacted: `jev_rank` <- `bench.run`,
`rank_chunks` <- `bench.main`, `jev_echo.main`, `jev_locate.main`) and `impact jev_rank` (HIGH, 8); code-review-graph
`callers_of jev_rank` (`bench.run`, `rank_chunks`, six tests); graft (`rank_chunks` <- `jev_echo.main`,
`jev_locate.main`); a literal `jev\.rank\(|jev_rank\(|rank_chunks\(|jev_query\(` sweep over scripts/, tests/, the bench,
harness-ports/ and .claude/hooks/ (the other `jev.rank` callers are JT1's scanner, JT3's hook and the client tests: not
JT2's). HIGH risk is expected: every Jev order of both tools changes query; all three consumers are named above.

## 3. The measurement that shaped the rule (scratch `probe_scrub.py`, `probe_fit.py`; the real `transcript_export.scrub`)

```
20,000 generated texts (named values of 3-60 chars, provider keys, links, key blocks, é-prefixed runs, quotes):
{'idem_fail': 0, 'tail_fail': 110, 'tail_longer': 0, 'head_fail': 606, 'head_longer': 338, 'n': 20000, 'over1000': 492}
head_longer 'dHbW9G6H=...Authorization: Bearer <redacted>; the error: A5J=token: <redacted' -> '...=token: <redacted>'
scrub cost at 1,000 characters: 0.21-0.48 ms
the shrink rule on 30,000 more: max rounds {'tail': 26, 'head': 53} unstable joins 0 joins over 1000 0
adversarial: é+900-run tail: rounds 951, 0.149 s, out len 50, fixed True | sk-run+é head: rounds 475, 0.027 s, out 14
```

`scrub` is idempotent on whole texts (0 of 20,000), but a CUT of a scrubbed text is not always a fixed point: a head
cut inside a `<redacted>` marker after a name leaves 8-9 value characters that a second scrub turns back into the
10-character marker (338 of 20,000 grew by 1-2); a cut can also expose a token at a new word boundary, or split the next
secret name so the value before it absorbs the fragment (these shrink). So "scrub first, then cut at 488" alone would
still let rank's scrub lengthen bug-echo's query past 1,000 (1,002-1,004) and cut its end: the fix needs a settle step.

## 4. The rule (stated)

`jev_context.fit_scrubbed(text, n, keep)`: scrub the text with the scrub `jev.rank` applies (`transcript_export.scrub`,
the same function object as `jev._scrub`), strip it, then take its LONGEST tail (`keep="tail"`) or head (`"head"`) of at
most `n` characters that the scrub leaves unchanged. The result is a piece of the scrubbed text, at most `n` characters,
and a fixed point of the scrub, so `jev.rank`'s own scrub and its cut to `RANK_QUERY_CHARS` change nothing.
Terminates by construction (`n` falls by one per round; `""` is a fixed point). `None` without the scrubber (nothing is
sent; `jev.rank` would refuse too).

- Q1 and Q3 (and any future query): `jev_query(text) = fit_scrubbed(text, JEV_QUERY_CHARS, "tail")`: the question's
  END is kept (where an error line ends).
- Q2: each side is `fit_scrubbed(side, SIDE_CHARS, "head")` with `SIDE_CHARS = (JEV_QUERY_CHARS - len(label)) // 2 =
  488`, so `"the defect: " + A + "; fixed as: " + B` is at most 1,000 characters and a fixed point (the label's
  characters form no scrub match with a side: 0 unstable joins in 30,000); `jev_query` then keeps it whole: label
  first, both sides.
- `jev_rank` computes the query once (it was recomputed per batch) and, when it is `None`, sends nothing and returns
  the reason (the pack falls back to its base order, D-3).

Rejected: (a) the verifier's first form, a raw `SIDE_CHARS = 488`: the scrub lengthens 8-9 character values (F-21's
mechanism), so the scrubbed query exceeds 1,000 again; (b) re-scrub-and-accept (send `scrub(cut)`): converges for
tails but oscillates for heads (a marker fragment regrows at a fixed cut) and its output is no longer a piece of the
scrubbed text, so the property test's oracle would have to copy the loop; (c) cutting at whitespace only: a long line
has none; (d) sharing a short side's unused budget with the other side: more text for the model, but not this repair.

## 5. Red-green (evidence item 2)

The new and changed tests (files `tests/test_jev_context.py`, `tests/test_jev_locate_echo.py`):

| test | guards | on the PIN code |
|---|---|---|
| `test_the_query_keeps_the_questions_end_after_the_scrub_lengthens_it` (in process, `jc.jev_rank` + the double) | F-21 | RED: sent query ends `...password=<redac` |
| `test_the_echo_query_reaches_jev_whole_at_its_maximum_size[both-sides-long]` (CLI, fixture repo; PIN builds 1,144 = 40543ab's shape) | F-20 | RED: sent query starts ` IOError):` (label and head cut) |
| `...[one-side-long]` (CLI; PIN builds 1,029, one side over, de06db6's shape) | F-20 | RED: starts `("/proc/%d/stat" % pid):` |
| `test_the_locator_query_keeps_its_last_words_after_the_scrub` (CLI, `jev_locate.py`) | F-21 | RED: ends `...pass`; its head was `ssword=QZJ80017`, a FAKE value whose name the raw cut removed, sent unredacted (AF-AP-127's shape) |
| `test_every_jev_query_fits_rank_whole_after_the_scrub` (the sweep: 163 questions, 122 diffs) | both, the rule | RED: what arrived (`<opaque-reda...n: <redacted>`) != what JT2 passed (`sh2JV4QS4FhH...ken: X4Z9JRp6`): rank's scrub changed the raw query |
| `test_the_echo_side_budget_is_tied_to_rank_s_cut` | mutant J4 | RED: `no attribute 'LABEL'` (the pin is new) |
| `test_without_the_scrubber_no_jev_query_is_built_or_sent` | the new None path | RED: the PIN's `jev_query` returns the raw text |
| `test_jev_rank_asks_the_local_venue_only_never_the_bridge` | F-23 | GREEN (the code is right; the pin is new: see the mutant table) |
| `test_the_query_bound_leaves_room_for_a_chunk` (one line added: `jc._scrub is jev._scrub`) | the same scrub | GREEN |

RED: the FINAL test files against the PIN production blobs, in a scratch copy (`git archive HEAD` of the five scripts,
`pyproject.toml`, `tests/conftest.py`, `scripts/test_summary.sh`; blobs f25e3219e9bd / 70720f113389 / 79ab68f0ce63;
tests 78371dec3b10 / 0f9afa39ef9f), 17:41:52Z:

```
pytest-exit: 1
pytest-summary: 7 failed, 79 passed in 16.31s
```

(An earlier RED run at 17:35:11Z, in the shared tree before any production edit, with the sweep's first generator:
`7 failed, 79 passed in 15.31s`, the same seven tests.) GREEN, the shared tree after the fix (blobs 926080a0aede
jev_context.py, 70720f113389 jev_locate.py unchanged, a8acebaa5f59 jev_echo.py; tests as above), 17:40:22Z:

```
$ bash scripts/test_summary.sh tests/test_jev_context.py tests/test_jev_locate_echo.py --basetemp /tmp/jt2r1/bt   (run 1)
pytest-exit: 0
pytest-summary: 86 passed in 18.05s
(run 2)
pytest-exit: 0
pytest-summary: 86 passed in 18.32s
$ bash scripts/test_summary.sh tests/test_jev_client.py tests/test_hiccup_scan.py --basetemp /tmp/jt2r1/bt   (the JT1 pair)
pytest-exit: 0
pytest-summary: 94 passed in 31.11s
```

No skip in any run (rg and git are present; `-rs` printed none). 86 = the landed 78 + 8 new (the maximum-size test
counts twice, parametrized). The JT1 pair's 94 equals VERIFY-JT1R1-JT2's F-01 count: the client side is untouched.
The sweep's de-vacuousing counts (re-derived in scratch, same seed and order, `sweep_stats.py`): `{'questions': 163,
'diffs': 122, 'pin_lost_end': 39, 'tail_unstable': 4, 'pin_lost_label': 14, 'side_unstable': 9, 'q_over_1000': 126}`.
Its first version failed its own floor (`pin_lost_end` 0: my generator shortened more than it lengthened); I added a
lengthening-weighted family and two deterministic tail cases (FAKE `sk-` and `ghp_` keys glued to a letter) rather
than lower the floor.

FINAL-BYTES RERUN (after two test docstrings were corrected; `tests/test_jev_locate_echo.py` is now `f2c03454e6bb`,
the other blobs as above). RED, the PIN copy, 17:53:58Z: `pytest-exit: 1` / `pytest-summary: 7 failed, 79 passed in
16.86s` (the same seven tests). GREEN, the shared tree: 17:54:15Z `pytest-exit: 0` / `pytest-summary: 86 passed in
18.68s`; 17:54:34Z `pytest-exit: 0` / `pytest-summary: 86 passed in 19.41s`; the JT1 pair 17:54:54Z `pytest-exit: 0` /
`pytest-summary: 94 passed in 31.65s`. These are the counts of record.

## 6. The live check (evidence item 4; the real Laya server on 127.0.0.1:47411, never stopped)

Scratch driver `jt2r1/live_echo.py`: `jev_echo.main(["--diff", "40543ab", "--order", "jev"])` in process, the
production venue (`local`, no `--jev-url`), with `jev._http` wrapped to record each POST body and `jev.LOG_PATH` pointed
at a SCRATCH call log (`jt2r1/live-calls-40543ab.jsonl`). Server `/health` before: `ok: true`, 323 calls.

```
start 17:43:25Z
end 17:43:41Z rc 0 | jev_echo: 38 removed lines, 4 candidate sites, 4 ranked by Jev, wall 16.4 s
requests 1 to ['http://127.0.0.1:47411/v1/systemone'] | distinct queries 1
sent chars 999 | starts with the label: True | '; fixed as: ' count 1 | == echo_query(removed, added): True | scrub leaves it: True | PIN would build 1144
head: 'the defect: # Timing + progress so both you and the agent know how long it took and that i'
tail: ' the whole text stays under 9,000 characters.\n# SYNCHRONOUS by design:'
scratch call log lines 1 | venues ['local'] | ok [True]
log state_sha256 == sha256(recorded state): True
ranking: Jev reorders the lexical order's selection (KC-J5: it never drops an item); 4 of 4 candidate sites scored, one noul each; question: Does this
1. 0.542 graft scripts/hook_context.py
2. 0.522 graft harness-ports/bin/codex-hook-adapter.py:65
3. 0.517 graft harness-ports/bin/hermes-hook-adapter.py
4. 0.511 graft scripts/jev_context.py:169
```

999 = 24 + 488 + 488 - 1: both sides fit to 488 (`removed scrubbed 2316 | fitted 488`, `added scrubbed 4388 | fitted
488`), and the added side's cut ends on a space (`'RONOUS by design: '`) that `jev_query` strips. The live order equals the
verifier's "whole query" scratch run (section 9: 0.542 hook_context.py, 0.522, 0.517, 0.512 jev_context.py:166) and not
the landed PIN order (0.498 codex-hook-adapter.py:65 first); the fourth site's line moved 166 -> 169 because this repair
added three docstring lines above it. The shared `.jev/calls.jsonl`: 245 lines, 222,292 bytes before and after (its last
line is the verifier's 16:48:11Z).

de06db6 (the second A4 commit, extra): started 17:44:01Z; five of its six batches answered (`rank local ok True
n_questions 8`, 35.8-41.3 s each, the scratch log); I stopped my own client by pid at 17:47Z because another lane's two
`scripts/laya_ft/evaluate.py` processes held about 137% CPU each on this 4-CPU box (load 6.41) and the shared server was
answering at about 5 s per chunk. Its query under the fix, computed in process with the same code: `de06db6: PIN built
1013 | fixed query 941 starts with the label True | fixed-as count 1`. The server stayed up (`/health` ok, 329 calls).

## 7. Mutants (evidence item 5; scratch copies only; `jt2r1/mutate.py`, a fresh copy per mutant, the anchor must match
exactly once, `PYTHONDONTWRITEBYTECODE=1`; final bytes, 17:55:34-17:58:35Z; baseline `86 passed in 19.87s`)

| mutant | result | red on |
|---|---|---|
| M1 restore the tail cut for bug-echo (`SIDE_CHARS = 560`, the PIN's share) | 4 failed, 82 passed | the sweep; maximum-size [both-sides-long] and [one-side-long]; the side-budget pin |
| M2a cut before the scrub: `jev_query` = the RAW tail (the PIN), rank scrubs after | 4 failed, 82 passed | the sweep; the locator CLI test; the in-process F-21 test; the no-scrubber test |
| M2b cut before the scrub inside `fit_scrubbed` (raw text cut to n, then scrubbed and fitted) | 1 failed, 85 passed | the sweep |
| M2c cut before the scrub for bug-echo (each RAW side cut to 488, then scrubbed: the verifier's first form) | 4 failed, 82 passed | the sweep; maximum-size [both-sides-long] and [one-side-long]; the no-scrubber test |
| M3 drop the venue pin (`venue = "auto"`, the verifier's J7) | 1 failed, 85 passed | `test_jev_rank_asks_the_local_venue_only_never_the_bridge` |
| M4 no settle step (the plain cut, never re-checked by the scrub) | 1 failed, 85 passed | the sweep |
| M5 the side share ignores the label (`1,000 // 2`) | 4 failed, 82 passed | the sweep; maximum-size x2; the side-budget pin |
| M6 bug-echo's sides keep their tail instead of their head | 3 failed, 83 passed | the sweep; maximum-size x2 |
| J3 (F-22, NOT in this repair) drop JT2's own all-equal guard | 86 passed: SURVIVES | none, as F-22 states: the guard is unreachable through the real `jev.rank`; left as the brief orders |

M2b and M4 are killed by the sweep alone: only generated and fixed cuts that split a scrub token tell them apart (the
CLI fixtures' cuts are stable by their own precondition).

## 8. Static gates (evidence item 6; final bytes)

```
no_laya_in_gates: 40 files scanned, clean            (rc 0)
pyflakes scripts/jev_context.py scripts/jev_locate.py scripts/jev_echo.py tests/test_jev_context.py tests/test_jev_locate_echo.py   (rc 0, no output)
lint_delta (worktree vs HEAD): 6 .py changed, 0 NEW pyflakes hit(s), 0 removed    (the 6 include JT3-R1's two)
U+2028/U+2029 count: 0 in each of the five files and this report
report_lint.py (this report, the working tree, --min-refs 10): 18 refs — OK 15, NEAR 0, MISS 0, UNCHECKABLE 3, UNRESOLVED 0
report_lint.py --rev HEAD: 20 refs — OK 14, MISS 1 (the `jev_context.py:817` ref marked "now"), UNRESOLVED 2 (basenames quoted from the verifier's run)
```

`lint_delta`'s advisory screen flagged AF-AP-175 (a quoted `HEAD` passed to git) in `tests/test_jev_locate_echo.py`:
the new maximum-size test names `HEAD` twice (`--diff HEAD`, then `git show HEAD`), but of a fixture repository the
test itself creates under `tmp_path`, where no other process commits; the existing echo tests do the same. Not a
defect. GitNexus `detect-changes --scope all`: `Changes: 7 files, 25 symbols`, `Risk level: medium`, two flows
(`Rescore -> Files_to_read`, `Main -> Words`); the 7 files include JT3-R1's; several listed symbols (`BUDGET_DEFAULT`,
`_JEV_LOCK`, `files_to_read`, `INSTRUCTIONS`, `NOTE`, `get_patch`) only moved lines, and the index predates the new
symbols (`fit_scrubbed`, `echo_query`, `LABEL`).

## 9. Files and lines changed (the working tree; `git diff --stat`: `4 files changed, 276 insertions(+), 12 deletions(-)`)

- `scripts/jev_context.py` (f25e3219e9bd -> 926080a0aede, numstat 37/10): module docstring `jev_rank()` bullet, lines 17-23
  (it said the tail is kept "so nothing is cut there": falsified by F-20/F-21, rewritten, D-080's limit named);
  `JEV_QUERY_CHARS` comment, line 58 (same claim); NEW `fit_scrubbed`, lines 758-775; `jev_query`, lines 778-783 (now
  `fit_scrubbed(text, JEV_QUERY_CHARS, "tail")`, `None` for `None`); `jev_rank`, lines 804-806 (the query once, `None`
  -> the reason, nothing sent) and 812 (`jev.rank(q, ...)`).
- `scripts/jev_echo.py` (79ab68f0ce63 -> a8acebaa5f59, numstat 12/2): NEW `LABEL`, line 37; `SIDE_CHARS`, lines 38-39 (560 ->
  derived, 488); NEW `echo_query`, lines 260-265; `main`, line 327 (`query = echo_query(removed, added)`).
- `scripts/jev_locate.py`: NOT changed (70720f113389); its question reaches `jev.rank` only through `jev_rank`.
- `tests/test_jev_context.py` (60af25fa3823 -> 78371dec3b10, numstat 46/0): `test_the_query_keeps_the_questions_end_after_the_
  scrub_lengthens_it` (line 432); `test_jev_rank_asks_the_local_venue_only_never_the_bridge` (line 452, F-23); one pin
  line in `test_the_query_bound_leaves_room_for_a_chunk` (line 518, `jc._scrub is jev._scrub`). No existing test changed.
- `tests/test_jev_locate_echo.py` (b5a110aafe74 -> f2c03454e6bb, numstat 181/0): imports `random`, `string`; the JT2-R1 block
  from line 422: `_scrub`, `_racy_before`, `_fixed_after`, the maximum-size test (parametrized, line 444), the locator
  CLI test (475), `_longest_fixed_piece` (490), `_generated` (499), the sweep (520), the side-budget pin (578), the
  no-scrubber test (587). No existing test changed.
- `tasks/briefs/jev-laya/JT2-R1-report.md`: this report.

## 10. Echo of the class, and adjacent observations (reported, NOT fixed)

AF-AP-193 ("a cut taken before a length-changing transform") is registered, with the coordinator's own ECHO (17:1xZ):
JT2 was the one BUG site. My re-check of the other `jev.rank` clients (read only): the hiccup scanner's jev column sends
a cluster key and snippets of at most 300 characters (`scripts/hiccup_scan.py:594` cuts candidates with `[:300]`), far under
rank's 1,000 and 2,500, so neither shape applies.

- **ADJ-A (new nuance of AF-AP-193; for the registry's owner): "scrub first, then cut" is not enough when the next
  stage scrubs AGAIN before its own cut.** AF-AP-193's FIX line reads "apply the downstream transform first, then cut
  ... so the downstream cut is a no-op". A cut of a scrubbed text is not always a scrub fixed point: 338 of 20,000
  head cuts GREW by 1-2 characters under a second scrub (a cut inside `<redacted>` after a name leaves 8-9 value
  characters that the scrub regrows to the 10-character marker), and 110 of 20,000 tail cuts changed (a cut that
  exposes a run or a key at a new word boundary). The downstream cut then still bites. This repair's rule adds the
  settle step (the longest piece the scrub leaves unchanged). Suggested registry addendum: "... then cut, then check
  the cut is unchanged by the downstream transform (or shorten it until it is)". I did not edit
  `docs/INCIDENT-LOG.md` (outside my boundary). Mechanical signature: none simple.
- **ADJ-B (JT3-R1's file, in flight; INFERRED from reading, not reproduced).** `.claude/hooks/search-intercept.py:973`
  sends `"Where is %s defined, and which lines show how it is used?" % pattern` to `jev.rank`, with `spec["pattern"]`
  (`:1085`) unbounded as far as I found; a pattern of about 940+ characters would lose the template's END at rank's
  head cut. The hook's Jev switch is off by default and grep patterns are short; exposure is near nil. For JT3-R1 or a
  verify-followup; not touched.
- **ADJ-C (F-22, carried; not in this repair).** JT2's own all-equal guard (`scripts/jev_context.py:817` now, `len(set(scores.values())) == 1`) is
  still unreachable through the real `jev.rank` (mutant J3 survives, section 7); left, as the brief orders.
- **ADJ-D (the PIN's leak shape, closed here).** The PIN's raw tail cut could remove a secret's NAME and send its
  VALUE unredacted to the local endpoint: the locator RED shows the PIN query starting `ssword=QZJ80017` (a FAKE
  value). The fix scrubs the whole text first, so this cannot recur on JT2's path.

## 11. Deviations from the brief (flagged)

1. `scripts/jev_locate.py` (in the boundary) is NOT modified: its question reaches `jev.rank` only through `jev_rank`,
   which now fits it.
2. A new public helper, `jev_context.fit_scrubbed`, carries the rule for both tools (the brief left the how open).
3. `jev_rank` now computes the query ONCE (it was recomputed per batch) and, without the scrubber, returns the reason
   `the query is not sent: the scrubber (scripts/transcript_export.py) did not import` before calling `jev.rank` (which
   refused that case too, with its own reason). A new reason text on a path no deployed tree takes.
4. The live check ran IN PROCESS (a scratch driver calling `jev_echo.main`), not as a subprocess: the CLI has no way to
   put jev.py's call log anywhere but the shared `.jev/calls.jsonl` (`--no-jev-log` writes none), and the brief wants a
   scratch call log. The venue, the server and every byte sent are the production path's.
5. The second A4 commit's live run (de06db6) was stopped by me after 5 of 6 batches (section 6); the brief asks for one
   commit, and 40543ab is complete.
6. Three of the seven RED tests guard NEW behavior and are RED on the PIN for that reason, not the finding's: the
   side-budget pin (`no attribute 'LABEL'`), the no-scrubber test, and the sweep's echo half (it would stop on
   `echo_query`; its locator half fails first, for the finding's reason). The F-20/F-21 RED evidence is the two
   maximum-size runs, the locator CLI test and the in-process F-21 test.
7. The F-23 test reaches into jev.py's private names (`jev.LOCAL_URL`, `jev._pc`) through `monkeypatch`: if JT1 renames
   them the test fails loudly (`setattr` raises), never silently. It runs the REAL `jev.rank`.
8. The maximum-size and locator CLI tests need rg and git (the file's existing LOUD SKIP); where rg is absent (CI may
   lack it) the F-20 end-to-end check skips, and the sweep (no rg) still covers the echo builder and the locator path.

## 12. Self-attack: the three likeliest ways this is wrong

1. **The label joins a side into a scrub match, so `jev_query`'s tail cut takes the label again (F-20 back).** Ruled
   out as far as measured: the label's characters (`the defect: `, `; fixed as: `) hold no secret name, and `;`, `:`
   and spaces end every value, run and name, so each side meets the label as it meets a string's end; 0 unstable joins
   in 30,000 random pairs (section 3); all 122 sweep diffs assert `got == want`, where `want` is the joined query
   itself, label first. Not a proof for every input (INFERRED).
2. **The settle loop is slow or never settles.** It ends by construction (`n` falls by one per round; `""` is a fixed
   point; a single character matches no rule, so a non-empty text keeps at least one). Worst measured: 951 rounds, 0.149
   s (an `é`-glued 1,100-character run, which the sweep includes). Bound: at most 1,000 scrubs of at most 1,000
   characters (0.21-0.48 ms each), about half a second. The Jev call costs seconds per chunk.
3. **The rule leaks, or the test mirrors the code.** (a) The shrink can stop where a token the WHOLE-text scrub did not
   recognize falls below a floor (an `sk-` run glued to `é` leaves `sk-` + 11 characters); nothing the whole-text scrub
   redacts is ever shown, because the whole text is scrubbed first (AF-AP-127's rule). (b) The sweep's oracle
   `_longest_fixed_piece` is the rule's definition, a search like the code's: a mirror risk. Mitigated by assertions
   that do not depend on it (what arrived == what JT2 passed; at most 1,000; unchanged by the scrub; label first; END
   kept), by CLI tests with independent expectations (`scrub(question).strip()[-1000:]`, stable by precondition), and by
   mutants M2b and M4, which the sweep kills.

## 13. Evidence tiers

- VERIFIED (a command in this session): the premise; F-20 and F-21 on the PIN (double and CLI); the scrub measurements;
  the enumeration (GitNexus, code-review-graph, graft, grep); RED 7 on the PIN with the final tests; GREEN 86 twice;
  the JT1 pair 94; 8 mutants killed, J3 surviving; the live 40543ab query (label first, 999 characters, venue `local`,
  the scratch log's hash equals the recorded state); the shared call log untouched; the static gates.
- INFERRED: that no join is unstable for any input (measured on 30,122, reasoned, not proven); the worst-case cost
  bound (no exhaustive search for a slower input); ADJ-B (reading only); that the bench's future `run` sends the
  fitted query (same `jev_rank`; not run: it needs the live instruments and about 20 Jev packs).
- ASSUMED: whether CI has rg (the file's LOUD SKIP covers its absence). Served model: `claude-opus-5-5` per my own
  context; I did not count my transcript's records (the harvest does).

## 14. NOT done (first-class)

- NOT done: F-22 (JT2's dead all-equal guard) and the JT1-R1 findings: excluded by the brief.
- NOT done: the registry addendum for ADJ-A and any change to `docs/INCIDENT-LOG.md` (outside my boundary).
- NOT done: ADJ-B (JT3-R1's file).
- NOT done: a live run of de06db6 to the end (5 of 6 batches; stopped, section 6); a live locator (`jev_locate --order
  jev`) run: the brief asks for the echo; the locator path is proven with the double through the CLI.
- NOT done: sharing a short side's unused budget with the other side (more text for the model; not this repair).
- NOT done: a token-aware bound (F-08/D-080): out of scope by D-080.
- NOT done: commit, push, PR, any bridge call (standing rules). Scratch: `jt2r1/` under the session scratchpad
  (`pin_tree`, `fixed_tree`, drivers, logs; the mutant copies deleted after each run; `/tmp/jt2r1` holds only basetemp
  leftovers).

## 15. Summary

JT2-R1 repairs F-20 and F-21 as one set. There is one rule and one choke point (`jev_context.fit_scrubbed`, used by
`jev_query` for every query that reaches `jev.rank`): scrub the whole text with the scrub `jev.rank` applies, then keep
its longest tail (the locator; the END) or head (each bug-echo side; 488 characters) that the scrub leaves unchanged.
Rank's own scrub and its 1,000-character cut are then no-ops. The settle step exists because I measured that a cut of
scrubbed text is not always a scrub fixed point (338 of 20,000 head cuts grew under a second scrub), so the verifier's
first-form fix (a raw 488 share) and plain scrub-then-cut would both have let rank's cut bite again. Seven new or pinned
tests are RED on the PIN (7 failed, 79 passed) and GREEN after (86 passed, twice); the JT1 pair is untouched (94 passed);
eight mutants are killed, among them the brief's three (restore the tail cut for bug-echo; cut before the scrub; drop
the venue pin). Live on the real server, bug-echo's query for 40543ab (1,144 characters at the PIN) arrived whole:
999 characters, label first, venue `local`, logged only to a scratch file. F-22 is left as ordered. The rule's gap is
stated plainly: it is measured, not proven, that the label can never join a side into a scrub match. ADJ-A suggests an
addendum to AF-AP-193: scrub first, then cut, then check that the downstream scrub leaves the cut unchanged.
