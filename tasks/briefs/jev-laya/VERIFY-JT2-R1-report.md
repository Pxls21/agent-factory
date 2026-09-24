# VERIFY-JT2-R1 report: the independent verify of the Jev locator and bug-echo after their one repair

Lane: VERIFY-JT2-R1 (sandbox adversarial-verifier, Opus 5.5). Brief: `tasks/briefs/jev-laya/VERIFY-JT2-R1-brief.md`.
Status: COMPLETE. Round one (section 19): NOT-READY on F-16. JT2-R2 reverify (section 21): MERGE-READY-WITH-FOLLOWUPS.

## 0. Premise re-measure (first action)

```
$ date -u
Thu Sep 24 18:07:35 UTC 2026
$ git log --oneline -2
64c5441 VERIFY-JT2-R1 brief: the independent verify of the Jev locator and bug-echo after their one repair (rule 0f)
b97c84c jev: JT2-R1 lands, the one repair of the Jev locator and bug-echo (F-20, F-21, F-23; GATED-PENDING-VERIFY)
--- HEAD blobs:
926080a0aede scripts/jev_context.py
70720f113389 scripts/jev_locate.py
a8acebaa5f59 scripts/jev_echo.py
78371dec3b10 tests/test_jev_context.py
f2c03454e6bb tests/test_jev_locate_echo.py
--- working-tree blobs (git hash-object):
926080a0aede scripts/jev_context.py
70720f113389 scripts/jev_locate.py
a8acebaa5f59 scripts/jev_echo.py
78371dec3b10 tests/test_jev_context.py
f2c03454e6bb tests/test_jev_locate_echo.py
--- git status --short on the five: (empty)
```

All five match the brief's PREMISE at HEAD and in the working tree. HEAD 64c5441 adds only the brief on top of b97c84c. The premise holds; the lane proceeds.

## 1. Contracts read

JT2: `JT2-brief.md` D-1..D-7, A1..A6 and its gates; D-077 (`docs/08_DECISION_LOG.md:88`, the default order is `lexical`,
Jev opt-in); the client's D-076 (b) (`:87`, rank cuts its query to 1,000 characters and each chunk to 2,500 AFTER the scrub)
and D-080 (`:91`, the character bound is a stated limit, not a token guarantee; JT2-R1 is JT2's one repair). The repair
brief `JT2-R1-brief.md` (F-20 BLOCKER, F-23; F-22 excluded). The previous verify `VERIFY-JT1R1-JT2-report.md` section 9
and F-20..F-23. The lane's report `JT2-R1-report.md`. The repair commit b97c84c touches `scripts/jev_context.py`
(docstring, the constant's comment, NEW `fit_scrubbed`, `jev_query`, `jev_rank`), `scripts/jev_echo.py` (NEW `LABEL`,
`SIDE_CHARS` 560 -> derived 488, NEW `echo_query`, `main`), the two test files, `docs/INCIDENT-LOG.md` (AF-AP-193's fix
line) and the lane report; `scripts/jev_locate.py` is unchanged (70720f113389 at both commits).

Other lanes' dirty files at start (never touched here): `.claude/settings.json`, `scripts/install_session_hooks.py`,
`tests/test_session_hooks.py`, `.claude/hooks/search-intercept.py`, `scripts/gpu_window.sh`, `tests/test_search_intercept.py`,
two report files. The box: 4 CPUs, load 6.5-7.3 (another lane's model work), so wall times here are contended.

## 2. Gates, re-run fresh (18:14-18:16Z; PYTHONDONTWRITEBYTECODE=1, `--basetemp /tmp/vjt2r1/bt`, no `-n`)

```
== JT2 pair run 1: Thu Sep 24 18:14:53 UTC 2026
pytest-exit: 0
pytest-summary: 86 passed in 20.46s
== JT2 pair run 2: Thu Sep 24 18:15:13 UTC 2026
pytest-exit: 0
pytest-summary: 86 passed in 19.19s
== JT1 pair: Thu Sep 24 18:15:33 UTC 2026
pytest-exit: 0
pytest-summary: 94 passed in 33.96s
$ bash scripts/pc_suite.sh set-id -- tests/test_jev_context.py tests/test_jev_locate_echo.py
2 files set=dc3e2b7404ab
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 40 files scanned, clean          rc=0
$ python3 -m pyflakes <the 5 JT2 files> docs/research/findings/jev-locate-bench/bench.py      rc=0 (no output)
$ python3 scripts/lint_delta.py --base HEAD
lint_delta (worktree vs HEAD): 2 .py changed, 0 NEW pyflakes hit(s), 0 removed      rc=0 (the 2 are another lane's)
U+2028/U+2029 in the four changed JT2 files: 0 each
```

No SKIPPED line in any run (`-rs`). 86 + 94 = 180 = the coordinator's landing RESULT (`180 passed` twice). The JT1 pair's 94
equals VERIFY-JT1R1-JT2's F-01 count, and `scripts/jev.py` is still 2d419d932bf6 (the previous verify's premise blob).

## 3. Red-green, reproduced (scratch trees under `/tmp/vjt2r1`, 18:16-18:18Z)

Two scratch trees by `git archive HEAD` of the five JT2 files, `jev.py`, `transcript_export.py`, `test_summary.sh`,
`tests/conftest.py`, `pyproject.toml`: `head` (as archived) and `pin` (the three production scripts replaced by their
86337b7 blobs f25e3219e9bd / 79ab68f0ce63 / 70720f113389; tests at HEAD, 78371dec3b10 / f2c03454e6bb).

```
== head 18:16:48Z   pytest-exit: 0   pytest-summary: 86 passed in 19.88s
== pin  18:17:08Z   pytest-exit: 1   pytest-summary: 7 failed, 79 passed in 17.68s
FAILED tests/test_jev_context.py::test_the_query_keeps_the_questions_end_after_the_scrub_lengthens_it
   AssertionError: ted> password=<redacted> password=<redacted> password=<redac
FAILED tests/test_jev_locate_echo.py::test_the_echo_query_reaches_jev_whole_at_its_maximum_size[both-sides-long]
   AssertionError:  IOError):
FAILED tests/test_jev_locate_echo.py::test_the_echo_query_reaches_jev_whole_at_its_maximum_size[one-side-long]
   AssertionError: ("/proc/%d/stat" % pid):
FAILED tests/test_jev_locate_echo.py::test_the_locator_query_keeps_its_last_words_after_the_scrub
   AssertionError: word=<redacted> password=<redacted> password=<redacted> pass
FAILED tests/test_jev_locate_echo.py::test_every_jev_query_fits_rank_whole_after_the_scrub
   AssertionError: assert ('<opaque-reda...n: <redacted>' == 'sh2JV4QS4FhH...ken: X4Z9JRp6'
FAILED tests/test_jev_locate_echo.py::test_the_echo_side_budget_is_tied_to_rank_s_cut
   AttributeError: module 'jev_echo_under_test' has no attribute 'LABEL'
FAILED tests/test_jev_locate_echo.py::test_without_the_scrubber_no_jev_query_is_built_or_sent
   AssertionError: assert ('why does it fail' is None)
```

The same seven tests and reasons as the lane's table (its section 5). Four are red for the findings' own reasons (the
label and head cut: both maximum-size cases; the last words: the in-process and the CLI F-21 tests); the sweep is red
because rank's scrub changed the raw query (the property the finding names); two guard new API (`LABEL`, the None path),
as the lane's deviation 6 states. The F-23 venue test is green on the PIN (the code was right; a pin, not a fix).

## 4. The set: every JT2 query that reaches `jev.rank` (two instruments)

Literal sweep (`grep -rn` for `jev.(rank|ask|classify|health|_call|_api|main)(`, `jev_rank(`, `jev_query(`,
`fit_scrubbed(`, `echo_query(`, `rank_chunks(` over `scripts/ tests/ docs/research/findings/jev-locate-bench/
harness-ports/ .claude/hooks/ src/ proofs/ spikes/`) and code-review-graph `callers_of` by qualified name agree:

- JT2 production code calls the client ONCE: `scripts/jev_context.py:812` `jev.rank(q` (the batch of `JEV_BATCH`) inside `jev_rank`, with
  `q = jev_query(query)` computed at `:804`. No JT2 file calls `jev.ask`, `jev.classify`, `jev.health` or `jev._call`.
- crg `callers_of scripts/jev.py::rank`: `hiccup_scan.jev_column` (JT1), `jev_context.jev_rank` (JT2), and tests.
- crg `callers_of jev_context.py::jev_rank`: `bench.py::run` (`:190`, `jc.jev_rank(c["input"], ...)`, no url, so venue
  `local`), `jev_locate.py::rank_chunks` (`:73`), and tests. crg `callers_of rank_chunks`: `jev_echo.main`,
  `jev_locate.main`. crg `callers_of fit_scrubbed`: `jev_query`, `echo_query`. graft agrees on `rank_chunks`,
  `fit_scrubbed` and `echo_query`.

So the set is the lane's Q1 (the locator's question, `jev_locate.py:137`), Q2 (bug-echo's labelled query,
`jev_echo.py:327` then `:328`) and Q3 (the A3 bench input, `bench.py:190`), and all three reach `jev.rank` only as
`jev_query(...)` = `fit_scrubbed(..., 1000, "tail")`. Q2 is also fitted per side first (`fit_scrubbed(side, 488, "head")`).
The claim holds.

## 5. The rule on NEW shapes (in process: the REAL `jev_context.jev_rank` -> the REAL `jev.rank` -> my recording double)

Scripts: `/tmp/vjt2r1/dbl.py` (routed like the server: only `POST /v1/systemone`; a varied score per chunk, so the
all-equal refusal never fires by accident), `/tmp/vjt2r1/attack1.py` (imports the production files read-only from the
repo). Per locator shape the checks are: what the double received == `jev_query(question)` (so rank's scrub and cut
removed nothing); at most 1,000; a scrub fixed point; `scrub(q)[:1000] == q`; a TAIL of `scrub(question).strip()`;
the LONGEST such tail (every longer tail within 1,000 re-checked and found unstable). Per bug-echo shape: received ==
`(LABEL % (A, B)).strip()` with A, B the fitted sides; label first; at most 1,000; fixed; the join itself fixed; each
side a head of its scrubbed side and the longest stable one within 488. None of these shapes is the lane's generator.

```
S1-3 combining e+U+0301   len=1000 head='é é '            tail=': LAST_WORDS'   (6 cut offsets each)
S1-3 emoji ZWJ            len=1000 head='💻 👩‍💻 '   tail=': LAST_WORDS'
S1-3 flag RI pair         len=1000 head='🇩🇪 🇩🇪 '          tail=': LAST_WORDS'
S1-3 astral math X, CJK, devanagari virama, arabic harakat, hangul jamo, BOM+RLM: len=1000, tail=': LAST_WORDS'
     (heads: 'ष क्ष ', 'ّ بَّ ', 'ᆨ 각 ': the cut splits grapheme clusters; the scrub does not care; see F-10)
S4 a named value straddling the raw cut, 24 offsets: len=1000 tail=' E: LAST_WORDS'
S5 lengthening values near both ends, k=1/5/20/60: len=1000 tail=' E: LAST_WORDS'
S7 NBSP / U+2028 (built with chr) / NEL / U+3000 / ZWSP around named values: len=1000, the end kept
S8 an unterminated key header at the START of a 3,600-character question: sent len=22 '<private-key-redacted>';
   the PIN's raw tail would have ended with LAST_WORDS: True (see F-09)
S9 a 106,878-character question, secrets at both ends: len=1000, jev_query 0.023 s, tail='cret: <redacted> E: LAST_WORDS'
S12 bug-echo: a side of only a key block (no END), a side of only named values (80 each), an empty added side,
    a whitespace-only removed side, a removed side ending in `password =`, an added side starting `= 'QZJ8...'`,
    a value on a continuation line, sides that CONTAIN the label text, `Bearer` and a bridge link at the removed
    side's end, combining and astral characters at 488, a glued run at 488, the marker regrow at 488, 2 KB of prose
    per side: every one label first, both sides, <= 1,000, fixed; e.g.
    'the defect: <private-key-redacted>; fixed as: x = load()'   (56)
    'the defect: a a ... b token: <redact' ... (998: the side's head stopped before the regrow)
requests to the double: 104      FAILS: 0
```

Two shapes send a FAKE value in clear on BOTH the PIN and the fix (the scrubber never sees a name before it): a name
and its value split across the two sides (`password` | `= 'QZJ8...'`), and a value on a continuation line
(`api_key = \` | `'QZJ8...'`). The scrub runs per text in both versions; these are the scrubber's gap class (the
previous verify's F-04), not this repair's (see F-12).

## 6. Leakage at the cut, through the REAL `jev_locate.py` CLI: the PIN tree against the fix (`/tmp/vjt2r1/attack2.py`)

Each FAKE secret straddles the raw 1,000-character cut: the question's last 1,000 raw characters start k characters
into the secret's value. A leak = a fragment of the planted value that the WHOLE-text scrub removes, found in the query
the double received. `--order jev --jev-url <double> --instruments rg --no-jev-log`, subprocess, cwd `/`.

```
named value (ADJ-D shape)  pin   k=3 req=1 leak=['8kkkkk', 'kkkkkk'] | k=8 leak=['kkkkkk'] | k=12 leak=['kkkkkk']
named value (ADJ-D shape)  head  k=3 req=1 leak=none | k=8 leak=none | k=12 leak=none
sk- provider key           pin   k=3 leak=['8BBBBB', 'BBBBBB'] | k=8 leak=['BBBBBB'] | k=12 leak=['BBBBBB']
sk- provider key           head  none | none | none
ghp_ token                 pin   leak=['8CCCCC', 'CCCCCC'] | ['CCCCCC'] | ['CCCCCC']        head  none | none | none
Bearer token               pin   leak=['8DDDDD', 'DDDDDD'] | ['DDDDDD'] | ['DDDDDD']        head  none | none | none
bridge link                pin   leak=['-abcd-', '-efgh.'] | ['-efgh.', '.com/s'] | ['.com/s', '.trycl']   head  none x3
key block body (base64-like, `+`/`/` every 16; a fixture file gives rg a hit)
                           pin   k=3 body segments in the query=11 | k=40 =9 | k=100 =6
                           head  k=3 =0 | k=40 =0 | k=100 =0
whole-text scrub keeps any body segment: False
```

(My first key-block run used plain runs the opaque rule catches, so its PIN "fragments" were only END-line pieces; the
second run above uses a realistic body. A first try with the plain fixture made 0 requests in both trees: rg found no
hit, so Jev was not asked; the fixture was fixed, not the reading.)

Reading: the lane's ADJ-D named one shape; the PIN's raw-cut-first leaked FIVE more classes (every scrubber class
that needs its prefix or its header: `sk-`, `ghp_`, Bearer, bridge links, key blocks). The fix scrubs the whole text
first, so a sent query is always a piece of `scrub(question)`: nothing the whole-text scrub removes can reach the
endpoint. Verified here for all six; structural by construction (`fit_scrubbed` returns a slice of `s = scrub(text)`).

## 7. Cost: the scrub's scaling and the settle loop's worst case (contended box: load 6.5-7.3 on 4 CPUs)

The repair scrubs the WHOLE question (locator) and each WHOLE side (bug-echo) before it cuts; bug-echo builds its query
on EVERY order (`jev_echo.py:327`, before `rank_chunks`), the default included. At the PIN the echo cut each side raw to
560 and scrubbed at most 1,144 characters, and only under `--order jev`. So the scrub's scaling matters on the default
path. The scrub is linear on every hostile shape I tried (a 4x text costs 3.8x-4.8x):

```
shape                      100 KB s   400 KB s    ratio
glued run e+A*N              0.0203     0.0797      3.9
a. repeated (F-16)           0.0209     0.0849      4.1
password=+long value         0.0670     0.2998      4.5     (the costliest: about 0.75 us per character)
in-run heads                 0.0475     0.2298      4.8
BEGIN then END-prefix        0.0025     0.0098      4.0
(12 more shapes: _A, token, token:+spaces, Bearer+spaces, links, sk-, _key=, -a- glued, quotes, api key=, code: 3.8-4.2)
```

The settle loop (`fit_scrubbed`), rounds counted by a separate counter, time = the real function, best of 3:

```
TAIL (n=1000)
  lane: e+A*1100 tail                rounds= 962 out=  39 fit_scrubbed=0.100 s
  e+password*140 (a run of names)    rounds= 962 out=  39 fit_scrubbed=0.102 s
  e+_key*300 run                     rounds= 962 out=  39 fit_scrubbed=0.113 s
  e+PC_BRIDGE_TOKEN*70 run           rounds= 962 out=  39 fit_scrubbed=0.110 s
  e+A*600 then 'password=<redacted> '*20   rounds= 562 out= 439 fit_scrubbed=0.132 s
  e+A*500 then 'Bearer <redacted> '*28     rounds= 458 out= 543 fit_scrubbed=0.071 s
HEAD (n=488)
  A*1000+e head                      rounds= 450 out=  39 fit_scrubbed=0.024 s
  _key*300+e head                    rounds= 450 out=  39 fit_scrubbed=0.028 s
```

962 is the maximum for this class (every length from 1,000 down to 40 unstable: a tail that starts inside a 40+ run
the whole text glued to a letter; 962 = 1000 - 39 + 1), a few more rounds than the lane's 951 and the same order of time
(0.10-0.13 s here against its 0.149 s). A longer run needs contiguous instability, and only the opaque-run class gives
it; sparse instabilities stop the loop at the first stable length. Bound: at most 1,000 scrubs of at most 1,000
characters (tail) and 2 x 450 of at most 488 (bug-echo's sides); the whole-text scrub is linear. It cannot stall a pack:
a Jev pack costs 36-165 s (D-077) and a default echo pack stayed at 0.33-0.67 s (section 8).

## 8. Regressions: D-077, KC-J5, determinism, budget, A3

bug-echo, the REAL CLI, the PIN tree and the fix back to back, a counting double as `--jev-url`,
`--instruments rg-token,rg-shape` (four real commits: the two A4 commits and the two largest code removals in the last
800 commits, 167e063 with 1,211 removed lines and 79f8f5b):

```
de06db6 pin/head x default/lexical: rc=0 requests=0 sha=53106fe4759a bytes=3902   all four byte-identical: True
40543ab pin/head x default/lexical: rc=0 requests=0 sha=898496b9f617 bytes=1335   all four byte-identical: True
167e063 pin/head x default/lexical: rc=0 requests=0 sha=42aa8d913cde bytes=1413   all four byte-identical: True  (1164 removed lines)
79f8f5b pin/head x default/lexical: rc=0 requests=0 sha=2ba1c9a42a96 bytes=1721   all four byte-identical: True  (856 removed lines)
wall: pin 0.37-0.50 s, head 0.33-0.67 s (noise on the loaded box; no measurable cost from the whole-side scrub)
```

The locator, three questions (a quirk-shaped error, F-21's lengthening shape, a "where is X decided" question),
`--instruments rg,registry,quirks,git-log`:

```
basetemp      | default/lexical x PIN/HEAD: [(rc 0, requests 0, '62fbbd637ae4')] | identical: True
   jev: rc=0 requests=6 | KC-J5 items same set: True, same order: False | files same set: True | sent == jev_query(q): True
F-21 shape    | [(0, 0, '0871cebfe0e0')] | identical: True
   jev: rc=0 requests=3 | KC-J5 items same set: True, same order: False | files same set: True | sent == jev_query(q): True
where decided | [(0, 0, 'bcc8f3907429')] | identical: True
   jev: rc=0 requests=6 | KC-J5 items same set: True, same order: False | files same set: True | sent == jev_query(q): True
```

Determinism and A5 on `--order jev` (the path the repair changed):

```
echo de06db6 determinism: rc 0 0 requests 6 6 identical bytes: True 6919b1dba614
   --budget 99999 chars=4082 | --json 5308 | --budget 1000 chars=1000 | --json 307
locate determinism: rc 0 0 requests 3 3 identical bytes: True cdd219e8e9ad
   --budget 99999 chars=3236 | --json 4670 | --budget 1000 chars=975 | --json 808
distinct queries sent: 2 | all <= 1000: True | echo label first: [True]
```

A3: the 20 committed inputs (`cases.json`) against the query JT2 sent at its landing (6b171fb: the raw last 1,200, then
`jev.rank` scrubbed and capped at 4,000, no 1,000 cut) and the fix's `jev_query`:

```
cases 20 | query at 6b171fb == query under the fix: 20 | differ: []
longest input 933 | longest scrubbed 933
```

So a rerun sends the same 20 queries; the committed results and D-077's reading still describe the same inputs.

## 9. The label and the sides: can the join form a scrub match? (`/tmp/vjt2r1/joinbrute.py`)

The lane measured 0 unstable joins in 30,000 random pairs and marked the claim INFERRED. My brute force builds each side
from a vocabulary of the scrubber's own edges (every name spelling and case, 11 separator and quote forms, values over
and under the 8-character floor, marker fragments `<redac` / `redacted>`, `Bearer` with and without a space, link
pieces, `sk-`/`ghp_`/`AIza`/`xoxb-` one character under their floors, key-header pieces, `é`, runs of 30-45, `\`, `;`,
`,`, `&`) and runs the REAL `echo_query`, then checks `scrub(query) == query` and `jev_query(query) == query.strip()`:

```
exhaustive pairs: 186517 | random pairs: 60000 | unstable joins: 0        (61 s)
```

(the random half pads each side to 400-490 characters, so the 488 head fit is active.) Structural reason, which the
count supports: the label's two separators follow `defect` and `as`, which are not names; the label meets A's end with
`;`, which ends every value, run and name the scrub reads; it meets each side's start after a space; and each side is
already a scrub fixed point. A private-key header cannot span the label (it holds lower-case letters and `;`). Still a
measurement plus an argument, not a proof (see F-08).

## 10. Mutation audit: NEW mutants (`/tmp/vjt2r1/mutate.py`; a fresh copy of the HEAD scratch tree per mutant, the anchor
matched exactly once, PYTHONDONTWRITEBYTECODE=1, the copy deleted after; baseline `86 passed in 19.88s`; 18:35-18:41Z)

```
N1   KILLED   1 failed, 85 passed | settle loop steps by 2 (not the longest) | the sweep
N2   KILLED   2 failed, 84 passed | fit_scrubbed does not strip | test_from_file_reads_the_last_4000_characters; the sweep
N3   KILLED   5 failed, 81 passed | jev_query keeps the head | per_chunk..._capped_to_its_tail; F-21 in process; from_file; locator CLI; the sweep
N4   KILLED   4 failed, 82 passed | echo sides swapped | test_echo_jev_order_keeps_the_base_selection; maximum-size x2; the sweep
N5   KILLED   4 failed, 82 passed | SIDE_CHARS off by one (489) | maximum-size x2; the sweep; the side-budget pin
N6   KILLED   1 failed, 85 passed | venue "pc" (the bridge) | test_jev_rank_asks_the_local_venue_only_never_the_bridge
N7   KILLED   1 failed, 85 passed | no venue (the client's default, auto) | test_jev_rank_asks_the_local_venue_only_never_the_bridge
N8   KILLED   6 failed, 80 passed | jev_rank sends the raw query (rank scrubs and cuts) | per_chunk; F-21 x2; from_file; the sweep; no-scrubber
N9   KILLED   1 failed, 85 passed | re-scrub-and-accept (the lane's rejected (b)) | the sweep
N10  KILLED   1 failed, 85 passed | drop the None guard (no scrubber) | test_without_the_scrubber_no_jev_query_is_built_or_sent
N11  KILLED   5 failed, 81 passed | jev_query bound 999 | per_chunk; F-21 x2; maximum-size[both]; the sweep
N12  KILLED   5 failed, 81 passed | NO whole-text scrub, only the settle check (re-opens ADJ-D) | F-21 in process ("QZJ8" not in q); maximum-size x2; locator CLI; the sweep
N13  KILLED   3 failed, 83 passed | fit the joined query's head (the added side can vanish) | maximum-size x2; the sweep
N15  SURVIVES 86 passed           | F-22: drop JT2's own all-equal guard (J3) | none
N16  KILLED   2 failed, 84 passed | bypass jev.rank through jev._api with venue auto | the venue test; the sweep
N17  KILLED   5 failed, 81 passed | the label without spaces | echo base selection; maximum-size x2; the sweep; the side-budget pin
N18  KILLED   7 failed, 79 passed | tail and head swapped inside fit_scrubbed | 7 tests
N19  KILLED  13 failed, 73 passed | always one character short | 13 tests
```

17 of 18 killed; the survivor is F-22's dead guard, as before (see F-06). F-23: the venue test kills all three new
venue shapes (`pc`, no venue, a bypass of `jev.rank` with `auto`), besides the lane's `auto` (M3): it fails for any JT2
call that is not venue `local` or that carries a url. N12 (cut the RAW text, keep the settle check) is the mutant that
would re-open the leak: it dies on the F-21 test's `"QZJ8" not in q` and on value equality, so the leak class is
guarded by an assertion, not only by an oracle.

## 11. The scrubber missing, for real (a scratch copy of the HEAD tree with `scripts/transcript_export.py` DELETED, so
the import fails as in a broken deployment; both CLIs, `--order jev`, the double as `--jev-url`)

```
locate rc=0 requests=0
    ['Jev unavailable: the query is not sent: the scrubber (scripts/transcript_export.py) did not import (unranked)']
    QZJ8 or X4Z9 on stdout: False | first lines: ['# jev locate', 'question: [withheld: the scrubber did not import]', ...]
echo de06db6 rc=0 requests=0
    ['Jev unavailable: the query is not sent: the scrubber (scripts/transcript_export.py) did not import (unranked)', ...]
    QZJ8 or X4Z9 on stdout: False | first lines: ['# jev echo', 'diff: [withheld: the scrubber did not import]', ...]
```

No path sends text without the scrubber: `fit_scrubbed` returns None, `jev_rank` stops before `jev.rank` (`:805`), and
`jev.rank` would refuse too. The display is withheld as before (D-4).

## 12. Evidence audit: the lane's load-bearing claims, re-derived from primary source

- The settle step's mechanism (the lane's section 3: "338 of 20,000 head cuts grew by 1-2"), on the real scrubber:

```
cut ' error: token: <redact'   scrub -> ' error: token: <redact'   grew by 0     (7 value characters: under the floor)
cut 'error: token: <redacte'   scrub -> 'ror: token: <redacted>'   grew by 2     (8: the whole run is one value piece)
cut 'rror: token: <redacted'   scrub -> 'ror: token: <redacted>'   grew by 1
cut 'ror: token: <redacted>'   scrub -> 'ror: token: <redacted>'   grew by 0
```

  `_redact_run` replaces every value piece with the 10-character marker whatever its length, so a marker fragment of
  8-9 characters after a name regrows. Confirmed; without the settle step (mutant M4 / my N9) the sweep goes red.
- The lane's live numbers, recomputed offline through the real `defect(parse_patch(git show))` and `echo_query`:

```
40543ab PIN built 1144 | fix: query 1000, jev_query 999, label first True, fixed True, sides 488/488
de06db6 PIN built 1013 | fix: query 941, jev_query 941, label first True, fixed True, sides 488/429
```

  (999 = the 1,000-character join with the added side's trailing space stripped; the lane's "999 = 24 + 488 + 488 - 1".)
- The lane's red count (7 failed, 79 passed on the PIN) and green count (86 passed): reproduced (sections 2-3).
- "No existing test changed": `git diff 86337b7 b97c84c -- tests/` is insertions only (46/0, 181/0); one of the 46 is a
  pin line added inside the existing `test_the_query_bound_leaves_room_for_a_chunk` (the lane says so).
- The commit's AF-AP-193 line in `docs/INCIDENT-LOG.md`: see section 14.

## 13. Live check: the locator on the REAL server (the lane ran bug-echo live, never the locator)

`/tmp/vjt2r1/live_locate.py`: the REAL `jev_locate.main` in process, production venue (`local`, no `--jev-url`),
`jev.LOG_PATH` pointed at a scratch log, `jev._http` wrapped to record each POST. The question is F-21's shape (2,204
characters; 70 FAKE 8-character named values near the end, which the scrub lengthens), `--instruments rg --in
scripts/jev_context.py --top 4`.

```
start 18:43:11Z question chars 2204
jev_locate: 6 hits, 5 chunks, 5 ranked by Jev, 1 of 1 instruments answered, wall 7.9 s
end 18:43:19Z rc 0 wall 7.9 s
requests 1 to ['http://127.0.0.1:47411/v1/systemone'] | distinct queries 1
sent chars 1000 | ends with LAST_WORDS_OF_THE_ERROR: True | == jc.jev_query(question): True | QZJ8 in sent: False
tail: 'rd=<redacted> then jev_query raised: LAST_WORDS_OF_THE_ERROR'
replies: [('laya-rl-agent', 5, [0.3161, 0.3423, 0.3882, 0.4256, 0.4453])]
scratch call log lines 1 | venues ['local'] | ok [True]
log state_sha256 == sha256(sent state): True
ranking: Jev reorders the lexical order's selection (KC-J5: it never drops an item); 5 of 5 chunks scored, one noul each
1. 0.426 rg scripts/jev_context.py:758 — def fit_scrubbed(text, n, keep="tail"):
2. 0.388 rg scripts/jev_context.py:778 — def jev_query(text): ...
```

Before and after: the server `/health` ok (calls 330, then 331); the shared `.jev/calls.jsonl` 245 lines, 222,292
bytes, last written 16:48:12Z (the previous verifier's), unchanged. One live model call in this lane.

## 14. Stale-context sweep and the AF-AP-193 row

`grep -rn` over `docs/ wiki/ scripts/ tests/ STATUS.md README.md CLAUDE.md AGENTS.md .hermes.md` (archive and briefs
excluded) for `nothing is cut there`, `tail is kept`, `SIDE_CHARS 560`, `560-character`, `raw 1,000`, `last 1,000
characters`, `jev_query`: no live document repeats the falsified claims. The two falsified comments (the module
docstring's `jev_rank()` bullet, the constant's comment) were rewritten in the repair commit; the remaining hits are the
new tests' own docstrings (accurate) and a historical `wiki/topics/live-state.md@1e68103:50` status line (`JEV_QUERY_CHARS` 1000, still true). The
wiki and the Jev findings pages describe no query shape. The commit's `AF-AP-193` row (`docs/INCIDENT-LOG.md@1e68103:669`) now
adds "AND check the cut is a fixed point of the downstream transform" with the lane's 338-of-20,000 measurement; the
mechanism is reproduced in section 12. Its ECHO column still reads "JT2 (the one BUG site, JT2-R1)": section 15 shows
that JT2 holds more sites of the class upstream of the scrub, which that echo's grep ("a slice beside `scrub(`") could
not see, because the cuts sit beside `clean(` or in a tool's flag.

## 15. NEW: raw cuts UPSTREAM of the scrub on JT2's paths (AF-AP-127 / AF-AP-193's class, missed by the echo)

`fit_scrubbed` scrubs "the whole text" it is given. On one query path that text is itself a raw cut:
`jev_locate.read_question` keeps the RAW last 4,000 characters of a `--from-file` input (`scripts/jev_locate.py:90` `FROM_FILE_CHARS`,
`text = text[-FROM_FILE_CHARS:]`, before any scrub; unchanged since JT2). A credential whose NAME falls before that
cut arrives as a nameless value, which no scrub can recognize afterwards. Three consequences, reproduced:

(a) The Jev query (a REGRESSION of this repair, for these shapes). When the rest of the 4,000-character window
collapses under the scrub (long runs, key blocks, payload lines), `fit_scrubbed`'s tail within 1,000 now reaches the
window's START, so the nameless value is sent. At the PIN the raw last-1,000 cut could never reach the start of a
4,000-character window. The REAL CLI (`jev_locate.py --from-file F --order jev --jev-url <double> --instruments rg`):

```
opaque run pin  k=3 requests=1 | whole-file scrub hides the value: True | value in the query sent: False | '<opaque-redacted> open_socket raised in fit_'
opaque run pin  k=9 requests=1 | ... value in the query sent: False
opaque run head k=3 requests=1 | whole-file scrub hides the value: True | value in the query sent: True  | query 91 chars: 'sword=QZJ8abcdefghijklmnop <opaque-redacted>'
opaque run head k=9 requests=1 | ... value in the query sent: True  | query 85 chars: 'QZJ8abcdefghijklmnop <opaque-redacted> open_'
key block  pin  k=3/9           | ... value in the query sent: False | '<opaque-redacted>\n-----END RSA PRIVATE KEY--'
key block  head k=3 requests=1 | ... value in the query sent: True  | query 96 chars: 'sword=QZJ8abcdefghijklmnop <private-key-reda'
key block  head k=9 requests=1 | ... value in the query sent: True  | query 90 chars: 'QZJ8abcdefghijklmnop <private-key-redacted> '
```

A log-shaped file (60 debug lines each carrying a 280-character base64url payload; one config line
`... loaded config: password=QZJ8abcdefghijklmnop region=eu`, FAKE, straddling the cut), through the REAL
`jev_locate.read_question` into the REAL `jc.jev_rank` (the exact values `main` passes via `rank_chunks`; in process
because rg's eight distinctive tokens were the payloads, so the CLI found no chunk to rank):

```
pin  k=38 cut leaves 'g: password=QZ' | question 4000 -> scrubbed 788 | whole-file scrub hides the value: True | value in the query sent: False
pin  k=41/44/49                       | ... value in the query sent: False   (the PIN's query starts '-09-24T18:00:57Z DEBUG sent pa')
head k=38 cut leaves 'g: password=QZ' | question 4000 -> scrubbed 788 | ... value in the query sent: False | 'g: password=<redacted> region='
head k=41 cut leaves 'password=QZJ8a' | ... value in the query sent: False | 'password=<redacted> region=eu\n'
head k=44 cut leaves 'sword=QZJ8abcd' | ... value in the query sent: True  | 'sword=QZJ8abcdefghijklmnop reg'
head k=49 cut leaves '=QZJ8abcdefghi' | ... value in the query sent: True  | '=QZJ8abcdefghijklmnop region=e'
```

It falsifies the lane's ADJ-D line (`JT2-R1-report.md:274-276`: "The fix scrubs the whole text first, so this cannot
recur on JT2's path") and the module docstring's "Every query reaches jev.rank ... scrubbed FIRST ..., then cut"
(`scripts/jev_context.py:17-19`, the `fit_scrubbed` bullet) for `--from-file` inputs, and it breaks, end to end, the client's D-5 ("Scrub, then
cap (AF-AP-127). Every text that leaves the process (the state, the query, each chunk) passes through
`transcript_export.scrub` first, then the cap ... Rejected: cap then scrub", `JT1-brief.md:37-39`), which JT2's D-3
routes every text through. Destination: the LOCAL endpoint only (the venue pin holds; the server's log holds no
request text: 468 lines, 0 with `"query"` or `state`). Needed together: `--order jev` (opt-in, D-077), `--from-file`
over 4,000 characters, a credential whose name the 4,000 cut removes, and a window that scrubs below about 1,000
characters (payload-heavy logs do: 4,000 -> 785-792 here). The fix is in-boundary, one line in `read_question`:
scrub the whole read text, then keep its last 4,000 (the existing `--from-file` test asserts only that the file's head
stays out, so it stays green).

(b) The pack's display (pre-existing, both trees, EVERY order including the default): the `question:` line shows the
nameless value, although `show()` scrubs, because the name was cut before it:

```
pin  k=3 rc=0 | whole-file scrub hides it: True | value on the pack: True | question: sword=QZJ8abcdefghijklmnop then open_socket raised in
pin  k=9 rc=0 | whole-file scrub hides it: True | value on the pack: True | question: QZJ8abcdefghijklmnop then open_socket raised in retry_
head k=3 rc=0 | ... value on the pack: True | head k=6: True | head k=9 rc=0 | ... value on the pack: True
```

(c) Chunk texts (pre-existing, `--order jev` for Jev, the display on any order): rg itself cuts each output line at
400 columns (`scripts/jev_context.py:534`, `--max-columns` 400 with `--max-columns-preview`) and `hit()` cuts the cleaned raw
text to 400 (`:281`; also the quirk windows `:618` and the merge join `:703`), all before any scrub. A long value cut
to 1-7 characters falls under the scrub's 8-character floor. A FAKE value in a 400+ column repo line, the REAL CLI:

```
spaced rg cut  5 into the value | whole line hides it: True | sent to Jev: ['QZJ8a']   | on the pack: []
spaced rg cut  7 into the value | whole line hides it: True | sent to Jev: ['QZJ8abc'] | on the pack: []
glued  rg cut  5 into the value | whole line hides it: True | sent to Jev: ['QZJ8a']   | on the pack: ['QZJ8a']
glued  rg cut  7 into the value | whole line hides it: True | sent to Jev: ['QZJ8abc'] | on the pack: ['QZJ8abc']
(cuts 2, 8 and 10 characters into the value: nothing; 8+ is over the floor and redacted)
```

At most 7 characters of a value, from repo text (which should hold no secret), the same exposure the scrubber's own
floor allows for short values (the previous verify's F-03).

## 16. Live confirmation of section 15 (a) on the exact production venue

`/tmp/vjt2r1/live_fromfile.py`: the REAL `jev_locate.main(["--from-file", F, "--root", <fixture>, "--order", "jev",
"--instruments", "rg", "--top", "4"])`, venue `local` (no `--jev-url`), the REAL server on 127.0.0.1:47411,
`jev.LOG_PATH` pointed at a scratch log, `jev._http` wrapped to record the POST body. F is 5,409 characters; its raw
last 4,000 start 9 characters into `password=QZJ8abcdefghijklmnop` (FAKE), and the rest is a long run plus an end line.

```
start 18:56:52Z | file chars 5409 | whole-file scrub hides the value: True
jev_locate: 2 hits, 1 chunks, 1 ranked by Jev, 1 of 1 instruments answered, wall 0.7 s
end 18:56:53Z rc 0
POST http://127.0.0.1:47411/v1/systemone | query chars 83 | FAKE value in the query: True | 'QZJ8abcdefghijklmnop <opaque-redacted> open_sock'
   reply model laya-rl-agent fan_out 1
scratch call log lines 1 | venues ['local']
shared .jev/calls.jsonl before and after: 245 lines, 222,292 bytes | server /health ok, calls 332
```

## 17. Finding inventory (no severity filter)

Evidence levels: R = reproduced by a command in this lane; S = static reading. Canonical = the production CLI or import
API of the files at b97c84c (or a byte-identical scratch copy), the real client, a recording double for what is SENT,
the real server where the endpoint matters.

- **F-01 INFO (R).** Premise, gates and counts hold: 5 blobs match at HEAD and in the tree; 86 passed twice, JT1 pair 94
  (180 = the landing RESULT); no skips; no_laya_in_gates, pyflakes, lint_delta and the separator check clean. Mapping:
  the verify brief's premise; JT2 gates. Fix: none.
- **F-02 INFO (R).** Red-green reproduced: the final tests on the PIN production blobs give `7 failed, 79 passed`, the
  lane's seven tests with its reasons; the HEAD copy gives 86. Mapping: JT2-R1 evidence demand 2.
- **F-03 INFO (R).** The set is complete: JT2's one call to the client is `jev_context.py:812`; its three builders
  (locator `jev_locate.py:137`, bug-echo `jev_echo.py:327`, bench `bench.py:190`) all pass through
  `jev_query` = `fit_scrubbed(..., 1000, "tail")`; two instruments agree (literal sweep and code-review-graph by
  qualified name; graft on three symbols). Mapping: F-20 "every query JT2 builds".
- **F-04 INFO (R).** The rule holds on new shapes (multi-byte and combining characters at the cut, a marker or a value
  straddling the cut at 24 offsets, lengthening values near both ends, Unicode spaces, a 106,878-character question,
  15 bug-echo side shapes): 104 requests, 0 failures of sent == passed, <= 1,000, fixed point, piece of the scrubbed
  text, LONGEST piece, label first. F-20 and F-21 are closed for every shape tested. Mapping: F-20.
- **F-05 INFO (R).** The label never joins a side into a scrub match: 0 unstable joins in 246,517 pairs (186,517
  exhaustive fragment pairs of the scrubber's edges + 60,000 random, head fit active), plus the structural argument
  (section 9). The lane's INFERRED claim is now measured eight times wider; still not a formal proof. Fix: none.
- **F-06 FOLLOW-UP (R; F-22, unchanged, excluded by the brief).** JT2's own all-equal guard (`jev_context.py:817`, was
  `:790`) is still unreachable through the real `jev.rank`: mutant N15 (J3) survives, 86 passed. The comment at
  `:819-821` ("this catches the rest") stays false on the production path. Fix: as F-22 (delete it, or test it with a
  rank that lacks the client's refusal).
- **F-07 INFO (R).** Mutation audit: 17 of 18 NEW mutants killed (section 10). F-23's venue test fails for every
  non-local shape tried (`pc`, no venue, a bypass of `jev.rank` with `auto`), besides the lane's `auto`. The leak mutant
  N12 dies on an assertion (`"QZJ8" not in q`), not only on the oracle.
- **F-08 INFO (R).** The settle loop's worst case is 962 rounds for a tail (the class maximum), 450 for a 488 head,
  0.10-0.13 s on this loaded box; the scrub is linear on 16 hostile shapes (about 0.75 us per character at worst); no
  stall: a default echo pack stayed at 0.33-0.67 s on the four commits, a Jev pack costs 36-165 s. The lane's "951
  rounds, 0.149 s" is the same order; its bound ("at most 1,000 scrubs") holds.
- **F-09 INFO (R).** After an unterminated private-key header ANYWHERE in the question, the whole-text scrub redacts to
  the end, so the locator's query is `<private-key-redacted>` and the question's last words are gone (S8). This is the
  scrubber's documented rule and the safe direction (the PIN's raw tail sent the text after the header, which for a
  real key is its body). The docstring's "the locator keeps the question's END" means the END of the SCRUBBED
  question. Fix (optional): one clause in the `jev_query` docstring.
- **F-10 INFO (R).** Character cuts split grapheme clusters (a combining mark, a ZWJ emoji, a Devanagari conjunct or a
  Hangul syllable loses its base at a tail's start or a side's end). Harmless for the scrub; no contract speaks to
  graphemes. Fix: none needed.
- **F-11 INFO (R).** With `transcript_export.py` deleted in a scratch copy, both CLIs exit 0, send nothing, print the
  new reason and withhold the display. Mapping: the brief's "scrubber missing" question.
- **F-12 FOLLOW-UP (R; the scrubber's owner, as the previous verify's F-04).** Two shapes send a FAKE value in clear on
  BOTH the PIN and the fix, because the scrubber never sees a name before the value: a name and its value split across
  the two echo sides (`password` | `= 'QZJ8...'`), and a value on a continuation line (`api_key = \` | `'QZJ8...'`).
  Rare in diffs. Fix: outside JT2 (scrubber hardening), or scrub the joined removed+added text once as a guard.
- **F-13 INFO (R).** Regressions checked and absent: D-077 (default == `--order lexical` == the PIN, byte for byte, zero
  requests: bug-echo on 4 commits including the two largest code removals, the locator on 3 questions); KC-J5 (the
  jev order keeps the lexical item and file sets); determinism (identical bytes on reruns); A5 (<= 9,000; <= 1,000 at
  `--budget 1000`); A3 (all 20 committed queries identical to what the fix sends).
- **F-14 INFO (R).** The repair closed six leak classes at the old 1,000 cut, through the real CLI: the PIN sent
  fragments of a named value, an `sk-` key, a `ghp_` token, a Bearer token, a bridge link and a key-block body that
  straddled the cut; the fix sends none (section 6). Broader than the lane's ADJ-D (one shape).
- **F-15 INFO (R).** The lane's load-bearing evidence re-derived: the marker-regrow mechanism (8 characters grow by 2,
  9 by 1, 7 stay), the live numbers (40543ab 1,144 -> 999; de06db6 1,013 -> 941), the red and green counts, "no existing
  test changed" (insertions only).
- **F-16 BLOCKER (R, live).** `--from-file` cuts the RAW file to its last 4,000 characters (`scripts/jev_locate.py:90`, `FROM_FILE_CHARS`)
  BEFORE any scrub, so a credential whose name falls before the cut arrives nameless. The repair's rule scrubs only that
  window and, when the window collapses under the scrub (a long run, a key block, payload-heavy log lines: 4,000 ->
  785-792 characters), keeps the window's START in the query: the nameless value is SENT to the Jev endpoint. The PIN
  could not send it (its raw last-1,000 cut never reached a 4,000-character window's start), so this is a regression of
  this repair for these shapes (it also closed the broader F-14 classes). Reproduced through the real CLI with a
  recording double (4 of 4 cases), through the real `read_question` -> `jev_rank` on a log-shaped file (2 of 4 cut
  positions: those that remove the name), and LIVE on the production venue against the real server (section 16). It
  falsifies the lane's ADJ-D line ("this cannot recur on JT2's path", `JT2-R1-report.md:274-276`) and the module
  docstring's "scrubbed FIRST ..., then cut" (`jev_context.py:17-19`) for `--from-file` inputs. Exposure: `--order jev`
  (opt-in) + `--from-file` over 4,000 + a credential whose name the cut removes + a window that scrubs below about 1,000;
  destination local only (the venue pin holds; the server logs no request text). Fix (one line, in boundary):
  `read_question` scrubs the whole read text, THEN keeps its last 4,000 (or passes the whole text and lets
  `fit_scrubbed` and `show()` cut after their scrub); a test: a `--from-file` input whose 4,000 cut lands inside a
  credential's name and whose window collapses under the scrub, asserting the value is in neither the query sent nor the
  pack (the existing `--from-file` test stays green: it checks only that the file's head is out).
- **F-17 FOLLOW-UP (R).** The same raw cut shows the nameless value on the pack's `question:` line on EVERY order, the
  default included, on the PIN and the fix alike (pre-existing since JT2): `show()` scrubs, but the name is already
  gone (section 15 (b)). The F-16 fix removes it too.
- **F-18 FOLLOW-UP (R).** Chunk texts are cut RAW before any scrub: rg's own `--max-columns 400` (`jev_context.py:534`),
  `hit()`'s `[:TEXT_CAP]` (`:281`), the quirk windows (`:618`) and the merge join (`:703`). A long value cut to 1-7
  characters falls under the scrub's 8-character floor and reaches the Jev chunk (`--order jev`) and, depending on the
  snippet window, the pack (section 15 (c): `QZJ8a`, `QZJ8abc`). Pre-existing; at most 7 characters, from repo text; the
  same exposure the scrubber's floor allows for short values. Fix: re-read the matched line and scrub it before the
  400 cut (drop rg's column cap for the text, keep it for speed on the match), or accept and document the floor.
- **F-19 FOLLOW-UP (R; the registry's owner).** `AF-AP-193`'s ECHO column (`docs/INCIDENT-LOG.md@1e68103:669`) names JT2 as "the
  one BUG site", fixed by JT2-R1; F-16..F-18 are further sites in JT2 that its grep ("a slice beside `scrub(`") could
  not see: a cut beside `clean(`, a cut in `read_question`, a cut by a tool flag. Fix: widen the echo (every slice or
  tool-side truncation on a path that a later stage scrubs) and the row's signature.
- **F-20 INFO (R).** A lone surrogate in the question (argv decodes invalid UTF-8 with surrogateescape) makes
  `--order jev` fail open with `Jev unavailable: call 1 of 2: internal error: UnicodeEncodeError (unranked)`, rc 0, zero
  requests, on the PIN and the fix alike. No regression; the reason text is the client's and vague.
- **F-21 INFO (R).** Two small API edges of the new code: `fit_scrubbed`'s `keep` is a free string (any value but
  `"tail"` keeps the head: `keep='Tail'` -> `'alpha'`), and `jev_rank(None, ...)` with the scrubber present reports
  "the scrubber ... did not import" (only reachable through the import API: `echo_query` returns None only without the
  scrubber). Fix: an `assert keep in ("tail", "head")`, and a distinct reason for a None query.
- **F-22 INFO (R).** My side effects: two live model calls (the server's `calls` 330 -> 332), both logged to scratch call
  logs; the shared `.jev/calls.jsonl` unchanged (245 lines, 222,292 bytes, last written 16:48:12Z); no tracked file
  written except this report; scratch 1.9 MB under `/tmp/vjt2r1`.

## 18. The blocking predicate, per candidate

| finding | 1 contract | 2 canonical path | 3 material | 4 discriminator | 5 in boundary | disposition |
|---|---|---|---|---|---|---|
| F-16 `--from-file` value in the Jev query | the client's scrub-then-cap rule for "every text that leaves the process (the state, the query, each chunk)" (JT1 D-5, amended by the in-scope D-076 (b), "after the scrub the client cuts the query"); JT2 D-3 routes every JT2 query through that client; AF-AP-127 (repo-wide) and AF-AP-193 (the class the repair brief names, "fix the set, not the instances"); the repair's own `fit_scrubbed` cites AF-AP-127 | yes: the real CLI with a recording double (4/4), the real `read_question` -> `jev_rank` (2/4 cut positions, the ones that remove the name), and LIVE on the production venue against the real server | yes: a credential value the whole-file scrub redacts is in the query sent; a regression of THIS repair for these shapes; falsifies the lane's ADJ-D evidence and the docstring | yes: the commands in sections 15-16; PIN False, fix True; a scrub-before-cut `read_question` flips it | yes: `scripts/jev_locate.py:90`, in the JT2-R1 MODIFY list | **BLOCKER** |
| F-17 `--from-file` value on the pack | JT2's docstring claim only ("Displayed text passes transcript_export.scrub first"); stdout is not in D-5's list | yes (CLI, both trees) | a whole value on stdout, every order | yes | yes | FOLLOW-UP (pre-existing since JT2; the F-16 fix removes it) |
| F-18 chunk text cut raw | D-5 names "each chunk" | yes (CLI + double) | at most 7 characters of a value, from repo text: the exposure the scrubber's own 8-character floor accepts | yes | yes | FOLLOW-UP (pre-existing; floor-level) |
| F-06 (F-22) dead guard | JT2 D-3 fail-open | the code is unreachable | none: the client refuses first | N15 | yes | FOLLOW-UP (excluded by the brief) |
| F-12 split-name values | the scrubber's coverage | yes | a value in clear on PIN and fix alike | yes | no (the scrubber) | FOLLOW-UP |
| F-19 AF-AP-193 echo scope | the registry's echo duty | n/a (a record) | the echo under-reports the class | F-16..F-18 | the registry's owner | FOLLOW-UP |

On F-16's first column, stated plainly so the coordinator can overrule it: JT2's OWN brief never names the scrub (its
D-5 says "the last 4,000 characters"), and JT2-R1's frozen F-20 criterion (wholeness: rank's cut a no-op, the END kept,
the label and both sides kept) HOLDS for `--from-file`. The mapping rests on the client's rule and the repo-wide
invariant that JT2's queries inherit through D-3, which D-031's condition (1) admits ("or an applicable repo-wide
invariant"). If the coordinator reads condition 1 as JT2's own frozen text only, F-16 is instead a CONTRACT-DEFECT (a
new exact-production-path defect that falsifies evidence), returned for an explicit ruling.

## 19. Gate recommendation

**NOT-READY** on ONE finding: **F-16** (`--from-file`'s raw 4,000-character cut upstream of the scrub lets a nameless
credential value into the Jev query when the window collapses under the scrub; a regression of this repair for those
shapes, reproduced through the real CLI and live on the production venue; it falsifies the lane's ADJ-D closure). The
repair's own contract is otherwise met in full: F-20 and F-21 are closed for every shape tried (the set is complete,
the rule holds, the label never breaks, the loop is bounded), F-23's venue test is real, and D-077, KC-J5, A3, A5 and
determinism hold. Per D-031 the first repair INTRODUCED this blocker, so one focused second repair is the coordinator's
to authorize: one line in `read_question` (scrub the whole read text, then cut) plus one test; the same line removes
F-17. If the coordinator rules condition 1 against F-16 (section 18), my recommendation becomes
MERGE-READY-WITH-FOLLOWUPS with F-16 returned as a CONTRACT-DEFECT. This recommendation depends on no unreproduced claim.

FOLLOW-UPs: F-06 (F-22), F-12, F-17 (with F-16's fix), F-18, F-19. INFO: F-01..F-05, F-07..F-11, F-13..F-15, F-20..F-22.

## 20. What I reproduced, read only, and skipped

- Reproduced: the premise; both gate pairs and the JT1 pair; the static gates; the red-green on scratch trees; the set
  with two instruments; the rule on new shapes (104 requests); the six closed leak classes through the CLI (PIN against
  the fix); the scrub's scaling and the settle loop's worst case; D-077, KC-J5, determinism, A5 and A3's queries; the
  join brute force (246,517 pairs); 18 new mutants; the scrubber-missing path by deleting the module in a copy; the
  lane's mechanism and numbers; F-16..F-18 (CLI, in process, and one live call); lone surrogates; two API edges; two
  live calls in all, scratch call logs only.
- Read only: `transcript_export.scrub` (every rule), `jev.py`'s `_prep`, `_text`, `_build`, `_ask_venues`, `_call`;
  the bench's `run`; the tests' doubles; the AF-AP-193 row; D-031 and the contract-gate skill's repair budget.
- Skipped, and why: the lane's own M1-M6 (its claims; my 18 mutants are new shapes); a live bug-echo run (the lane ran
  40543ab live; the send-side bytes are client-side and covered by the double; live calls kept to two); JT3's hook and
  its ADJ-B (VERIFY-JT3-R1's file; not touched, not read); `scripts/laya_ft/` (VERIFY-FT1's); the PC venue and the bridge
  (forbidden; the venue pin is tested); a full-tree `lane_gate.sh` copy (the brief's gate pair was run directly).
- My writes: this report only in the tracked tree; scratch under `/tmp/vjt2r1` (1.9 MB: two small scratch trees, three
  fixture repos, the drivers, two scratch call logs); mutant copies deleted after each run. No commit, push, PR,
  comment, bridge call or subagent; `.jev/intercept-off` untouched; the Laya server never stopped (`/health` ok).
- Served model: my transcript (`subagents/agent-a31a66846563e8647.jsonl`, counted per assistant record at 18:5xZ):
  266 of 266 `claude-opus-5-5`, 0 `"stop_reason":"refusal"`.
- Report lint (`python3 scripts/report_lint.py --min-refs 10` on this file, after one round of token fixes):
  `report_lint: 12 refs — OK 11, NEAR 1, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.

## 21. JT2-R2 reverify (the second repair for F-16; coordinator-authorized under D-031; 19:09-19:3xZ)

**Recommendation: MERGE-READY-WITH-FOLLOWUPS.** F-16 and F-17 are closed on every shape I have (reproduced, and once live);
no regression in D-077, KC-J5, A3, A5 or determinism; the new observations are INFO or FOLLOW-UP (a cost on large
`--from-file` inputs, where no latency criterion is frozen, and two test gaps where the code is right). This
recommendation depends on no unreproduced claim.

### 21.1 Premise

```
55ade43 jev: JT2-R2, the second repair of the Jev locator (VERIFY-JT2-R1 F-16, F-17; D-031; GATED-PENDING-VERIFY)
 scripts/jev_locate.py | 6 +++++-    tests/test_jev_locate_echo.py | 22 ++++++++++++++++++++++
sha256/16 now:  39284e31bd8a5dac scripts/jev_locate.py        9be5cff23207f76b tests/test_jev_locate_echo.py
                1a4c822d5274437a scripts/jev_context.py       b03edb82eaf07ec3 scripts/jev_echo.py
                6bbac21debbedf72 tests/test_jev_context.py    (blobs 926080a0aede / a8acebaa5f59 / 78371dec3b10: round one's)
sha256/16 at b97c84c: 05f78d2e8d02f0fa scripts/jev_locate.py  7c88cff91805d66d tests/test_jev_locate_echo.py
HEAD e8e2bed at the end: the same five digests; `git diff --stat 55ade43 HEAD -- scripts/ tests/`: empty
```

All match the coordinator's message. SHAs: a push has since rewritten the branch (the trailer strip); the SHAs in this
report are the local pre-push ones the briefs and the coordinator gave, and their post-push equivalents hold the same
trees: b97c84c -> f74dfd7, 55ade43 -> 8be6460, 64c5441 -> 298b86c (checked with `rev-parse <sha>^{tree}`). Line
references to files other lanes edit are pinned as `path@1e68103:NN` where the file has moved since. The change: `read_question` now does `fitted = jc.fit_scrubbed(text,
FROM_FILE_CHARS, "tail")` on the whole file and uses it, else the raw `text[-FROM_FILE_CHARS:]`; one new test.

### 21.2 Gates and red-green

```
== JT2 pair run 1: 19:10:38Z  pytest-exit: 0  pytest-summary: 87 passed in 19.47s
== JT2 pair run 2: 19:10:58Z  pytest-exit: 0  pytest-summary: 87 passed in 19.20s
== JT1 pair:       19:11:17Z  pytest-exit: 0  pytest-summary: 94 passed in 32.11s        (87 + 94 = 181, the coordinator's count)
pyflakes (jev_locate.py, the test file) rc=0 | no_laya_in_gates: 40 files scanned, clean | U+2028/9: 0, 0
new test + the old --from-file test, R1's jev_locate.py (05f78d2e8d02f0fa) with the R2 test file:
  FAILED tests/test_jev_locate_echo.py::test_from_file_is_scrubbed_whole_before_its_cut
  E   AssertionError: ... 'state': {'query': 'QZJ8abcdefghijklmnop <opaque-redacted> open_socket raised in retry_pool: LAST_W...
  1 failed, 1 passed in 1.41s
the same two tests on R2 (39284e31bd8a5dac): 2 passed in 1.45s
```

### 21.3 F-16 and F-17 closed: my shapes, R1 (b97c84c's locator) against R2, the REAL CLI and a recording double

`/tmp/vjt2r1/r2_close.py` (`--from-file F --order jev --instruments rg --in scripts/jev_context.py --root <repo>`); a
marker = the FAKE value or a FAKE key-body segment; "in query" = any query the double received:

```
C1 opaque run k=3        R1 requests=1 | in query: True  | on pack: True  || R2 requests=1 | in query: False | on pack: False | query tail 'fit_scrubbed: LAST_WORDS'
C1 opaque run k=9        R1 in query: True  | on pack: True                   || R2 in query: False | on pack: False
C1 key block  k=3        R1 in query: True  | on pack: True                   || R2 in query: False | on pack: False
C1 key block  k=9        R1 in query: True  | on pack: True                   || R2 in query: False | on pack: False
C3 value straddles the cut (the cut 6 characters into the value)          R1 True / True   || R2 False / False
C4a key block, BEGIN ~2,000 characters before the cut, body in the window R1 requests=0 / on pack: True || R2 requests=1 / False / False
C4b 5,585-character dotted value, name ~2,600 before the cut             R1 in query: False / on pack: True || R2 False / False
C5 file scrubs below 4,000 (2 KB prose, 7 KB key block, 1 KB tail)       R1 requests=0 / on pack: True || R2 requests=1 / False / False
(stderr never held a marker; "whole-file scrub keeps a marker: False" for every case)
```

The log-shaped file (60 payload lines, one FAKE config line straddling the cut): the query in process through the real
`read_question` -> `jev_rank`, the pack through the CLI (default order):

```
R1 k=38/41 | value in the query: False | on the default pack: False  (the cut kept the name)
R1 k=44    | value in the query: True  | on the default pack: True  | query starts 'sword=QZJ8abcdefghijklmnop'
R1 k=49    | value in the query: True  | on the default pack: True  | query starts '=QZJ8abcdefghijklmnop regi'
R2 k=38/41/44/49 | question 1116 chars | value in the query: False | on the default pack: False | query starts '2026-09-24T18:00:02Z DEBUG'
```

The scrubber-missing fallback (a copy of R2 with `transcript_export.py` DELETED):

```
lexical rc=0 requests=0 | value on stdout: False | ['question: [withheld: the scrubber did not import]'] | 'ranking: lexical order (lexical overlap), Jev not asked'
jev     rc=0 requests=0 | value on stdout: False | ['question: [withheld: the scrubber did not import]'] | 'Jev unavailable: the query is not sent: the scrubber ... did not import (unranked)'
(the instruments still run on the raw tail: 3 hits, 3 chunks)
```

Live, once, on the production venue (the same `live_fromfile.py` construction that sent the value at R1, now running
R2 from the repo): `rc 0 | POST http://127.0.0.1:47411/v1/systemone | query chars 1000 | FAKE value in the query:
False`; the scratch call log gained one line (venue `local`); the shared `.jev/calls.jsonl` stayed 245 lines, 222,292
bytes; server `/health` ok, calls 332 -> 333.

### 21.4 Does R2 change a pack for a file with nothing to redact? Yes, in three benign ways

Seven files with `scrub(text) == text` (a trace-like text), R1 against R2, the default order, `--instruments
rg,registry,quirks,git-log`, the real repo:

```
a no trailing newline            identical: True
b one trailing newline           identical: False | R1 'question: File "scripts/jev_context.py", line 829, ...' | R2 'question: s File "scripts/jev_context.py", ...'
c trailing blank lines+spaces    identical: False | R1 'question: "scripts/jev_context.py", line 829, ...' | R2 'question: s File ...'
d cut inside a glued run         identical: False | R1 'question: <opaque-redacted> es = jev.rank(q, ...' | R2 'question: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA es = ...'
e window starts at a space       identical: True
f short file + newline           identical: True
g last 4,000 are whitespace      identical: False | R1 rc=64 'jev_locate: usage: the bug text is empty' | R2 rc=0, a pack
```

(1) `strip()` runs on the WHOLE text before the cut, so the 4,000-character window moves left by the file's trailing
whitespace: a file ending in a newline (most files) starts its question one character earlier (b, c; R2's pack for b
equals its pack for a). (2) Beyond `strip()`: a cut inside a glued run is settled (d: the question is 21 characters
shorter and shows up to 39 run characters where R1's display showed the redaction marker). (3) A file whose last
4,000 characters are whitespace is now read, not refused (g). None loses content; all follow from scrub, strip, then
fit. Also: for inputs that DO hold secrets, the instruments now search the scrubbed text. `tokens()` (rg, git log) is
unchanged on my probe; `words()` (the lexical overlap) gains `opaque` and `redacted` and loses the value fragments.

### 21.5 Cost: new on the default `--from-file` path

```
the settle loop at n=4,000 (the real fit_scrubbed, one run each, load 5.7):
  e+A*6000 (glued run at the end)              rounds= 3962 out=   39 fit_scrubbed(n=4000)=1.69 s
  e+A*2400 then 'password=<redacted> '*80      rounds= 2362 out= 1639 fit_scrubbed(n=4000)=2.20 s
  e+_key*1500 run                              rounds= 3962 out=   39 fit_scrubbed(n=4000)=1.86 s
the whole-file scrub, the CLI wall (default order, --instruments rg):
  10 MB R1 wall=0.1 s | R2 wall=2.4 s          40 MB R1 wall=0.2 s | R2 wall=9.5 s
```

Linear (about 0.24 us per character on a log); R1 read the whole file too but only cut it. A 400 MB log would add about
95 s, plus the scrub's transient copies in memory. No latency criterion is frozen (D-1's 30 s budget is per instrument).

### 21.6 Regressions

```
the bench and bug-echo never call read_question (grep: no hit); jev_context.py and jev_echo.py are byte-identical to
  round one, so A3 (its 20 queries), bug-echo's D-077 equality and the echo's query hold as measured in sections 8 and 13
positional Q1/Q2/Q3 | R1/R2 x default/lexical identical: True | requests [0]              (D-077)
from-file R2 KC-J5: jev requests 6 | items same set True | files same set True | value in any query: False
   --budget 99999 chars=3703 | --json 5732 | --budget 1000 chars=783                            (A5)
from-file R2 determinism (jev order): identical bytes True
```

### 21.7 Mutants on R2 (fresh copies of the R2 scratch tree, PYTHONDONTWRITEBYTECODE=1; baseline 87 passed)

```
R2-M1 KILLED   1 failed, 86 passed | always the raw tail (R1's read)             | test_from_file_is_scrubbed_whole_before_its_cut
R2-M2 KILLED   1 failed, 86 passed | fit the file's HEAD                          | test_from_file_reads_the_last_4000_characters
R2-M3 SURVIVES 87 passed           | scrub, strip, then cut by hand (the rejected form)
R2-M4 KILLED   1 failed, 86 passed | fitted computed, never used                  | test_from_file_is_scrubbed_whole_before_its_cut
R2-M5 SURVIVES 87 passed           | window 1,000 instead of 4,000
R2-M6 SURVIVES 87 passed           | no fallback without the scrubber
N12   KILLED   5 failed, 82 passed | no whole-text scrub in fit_scrubbed (the leak mutant)
N15   SURVIVES 87 passed           | F-22's guard dropped (unchanged, F-06)
R1-M5 SURVIVES 86 passed           | the same 1,000 window on R1's raw cut: R2-M5's gap predates R2
R2-M6 with the scrubber deleted: rc=1 | AttributeError: 'NoneType' object has no attribute 'strip'   (the real R2: rc 0, 21.3)
```

R2-M3 is equivalent in safety: a tail cut of scrubbed text is unstable only at a glued run (21.4 d), and every
consumer re-scrubs (`fit_scrubbed` for the query, `show()` for the display). The commit's rejection reason ("a cut
inside a `<redacted>` marker regrows") describes a HEAD cut; `fit_scrubbed` is still the better choice (the question
is a fixed point). R2-M5 and R2-M6 are test gaps; the code is right.

### 21.8 Findings of this reverify (no severity filter)

- **F-16 CLOSED (R, live).** No shape of mine sends a value the whole-file scrub redacts: C1 x4, C3, C4a, C4b, C5, the
  log file at four cut positions, live. The new test is red on R1's locator and green on R2.
- **F-17 CLOSED (R).** No marker on any pack (default order included) for the same shapes.
- **F-19 ADDRESSED (R, read).** The `AF-AP-193` echo (`docs/INCIDENT-LOG.md:671`, commit 4faffc1) now lists F-16, F-17 and
  F-18 as JT2 sites of the class.
- **R2-a INFO (R).** The pack changes for files with nothing to redact in three benign ways (21.4): the window moves by
  the trailing whitespace, a cut in a glued run settles, and a whitespace-tailed file is now read (rc 0, was 64). The
  locator's docstring (`scripts/jev_locate.py:9`, `--from-file reads it` "(its last 4,000 characters when larger)") and
  JT2's D-5 wording could say "of the scrubbed text".
- **R2-b INFO (R).** For `--from-file` inputs holding secrets, `words()` now sees `opaque` and `redacted`, a small
  lexical-overlap bias toward chunks that mention them; `tokens()` is unchanged. The positional question is still not
  scrubbed before the instruments (local processes only); the two input modes now differ there.
- **R2-c FOLLOW-UP (R).** Cost on the default `--from-file` path: the whole-file scrub is linear (40 MB: 9.5 s against
  0.2 s at R1) and the settle loop at n=4,000 reaches 1.7-2.2 s on adversarial tails. Bounded, no frozen latency
  criterion, no stall of a normal pack. Fix options: scrub only the last few MB (a residual: a secret whose name lies
  before that bound, in a window that collapses), or accept and document the cost.
- **R2-d FOLLOW-UP (R; tests).** Two gaps where the code is right: no test runs `--from-file` without the scrubber
  (R2-M6 survives; the mutant crashes with rc 1), and no test pins the 4,000 window size (R2-M5 survives; so does R1-M5,
  so the gap predates R2).
- **R2-e INFO (R).** R2-M3 (scrub then cut by hand) survives and is equivalent in safety; the commit's rejection reason
  names the head-cut case.
- Unchanged, FOLLOW-UP to the issue as the coordinator states: F-06, F-12, F-18, F-21 (their functions are untouched:
  `jev_context.py` and `jev_echo.py` are byte-identical; `read_question` is not their code).

### 21.9 The blocking predicate

No finding of this reverify meets it: F-16 and F-17 are closed; R2-a, R2-b and R2-e change no claimed output against a
frozen criterion (the scrub-then-cut order is the repair's intent); R2-c has no frozen latency criterion (condition 1);
R2-d are test gaps, not code defects (condition 3). Recommendation (repeated): **MERGE-READY-WITH-FOLLOWUPS**.

My writes this round: this section; scratch under `/tmp/vjt2r1` (the R2 tree, the drivers; mutant copies deleted). One
live call (server calls 332 -> 333), a scratch call log only. No commit, push or subagent; `.jev/intercept-off`, the
JT3 files and the FT1-F files untouched; the server never stopped.

Report lint after this section (`python3 scripts/report_lint.py --min-refs 10`, one round of fixes for lines other lanes moved):
`report_lint: 14 refs — OK 11, NEAR 3, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.
