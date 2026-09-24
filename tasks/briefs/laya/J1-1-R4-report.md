# J1-1-R4 — report (task #198; D-069, D-070)

Lane: J1-1-R4 build (sandbox, code-implementer, shared tree, no worktree). PIN 8c684be. Brief:
`tasks/briefs/laya/J1-1-R4-REDESIGN-brief.md`. Nothing committed or pushed. No verdict here: the independent verify decides.
Scratch: `/tmp/j1r4b/` (references, prototypes, mutants; removed at the end of the lane).

## 1. Premise (re-measured 2026-09-24 11:29Z on the PIN)

Every premise line holds.

```
$ git log --format='%h %s' -4 -- src/agent_factory/decisions/volatile.py
fdac751 J1-1-R3 landed GATED-PENDING-VERIFY: the redaction regressions fixed; C4 amended (D-067)
fb016d0 J1-1-R2 landed (task #192; GATED-PENDING-VERIFY): the sk and bearer classes yield to a later
f0e431f J1-1-R1 landed (task #139; GATED-PENDING-VERIFY): bound after redact, the widened secret cla
01ca7d5 J1-1 landed (GATED-PENDING-VERIFY): the decisions module (seven closed state schemas, normal
$ git rev-parse --short=12 <rev>:src/agent_factory/decisions/volatile.py
d556c9b 20ebcd54f3ed    fb016d0 bf04415d72c1    HEAD 2d5cf0072469    8c684be 2d5cf0072469
$ pytest canonical ledger no_model decide_harvest -q          (11:29:04Z..11:30:04Z)
248 passed in 59.74s                                          set: 4 files set=25abb828084e
$ grep -l redacted tests/fixtures/decisions/golden/*.json     (no output, rc=1)
callers of decision_state: ledger.py:273 (restate), ledger.py:404 (make_row), canonical.py:77
```
The prototype core, run from a scratch copy, reproduces the three premise outputs (`password: <redacted:envval>`,
`ta<redacted:sk>: <redacted:envval>`, `Authorization: <redacted:bearer>: rejected`).

HEAD moved during the lane: 16 coordinator commits, 8c684be..3161435 (12:48Z). `git diff 8c684be HEAD` over
`src/agent_factory/decisions/`, the five gate test files, `tests/fixtures/decisions/` and the brief is empty; HEAD's
`volatile.py` blob is still 2d5cf0072469.

## 2. What changed

`src/agent_factory/decisions/volatile.py` (205 added, 129 deleted; final sha256 prefix 0cfe104a7996):
- Deleted: `_SECRET_NAME`, `_ASSIGNMENT_HEAD`, `_ENVVAL_HEAD`, `_BEARER_RUN`, `_yield_pattern`, `_BEARER_MERGE`, `_YIELD`,
  `_BEARER`, `_SK`, `_TOKEN`, `_ENVVAL`, `_ENVVAL_WIDE`, `_PRIVKEY`, `_envval_wide`, the old `_redact_str`, and every comment
  on the yield or the merge step. No other module used them (grep of `src/ scripts/ tests/`).
- Added: `import bisect` (:26); the detection comment (:47-81); `_NAME` (:82), `_FORMS` (:84), `_DETECTORS` (:101),
  `_PADDING` (:105), `_PRIVKEY_BEGIN` and `_PRIVKEY_END` (:112-113), `_HELD` (:116), `_RANK` (:119), `_THROUGH` and
  `_THROUGH_RANKS` (:121-122); functions `_cut_placeholder` (:347), `_matches` (:357), `_regions` (:387), `_stops` (:399),
  `_spans` (:426), and a new `_redact_str` (:461).
- Docstrings: the module header (:3-6, D-070) and `decision_state` (:497, the sentence about a cut placeholder).
- Unchanged: `normalize`, `redact`, `bound`, the body of `decision_state`, `PLACEHOLDERS`, the limits, the schemas.

The pass as built:
1. `_matches`: every form at every start. A zero-width lookahead finds each HEAD at every position; the value is the rest of
   the maximal run of its class that holds the head's end (the runs are found once per text, so the detection is linear).
   Held placeholders are spans of their own class. A key block runs from every BEGIN line to the first END line at or
   after its end, or to the end of the value.
2. `_spans`: the closure. The envval and widened value classes take every placeholder character, so such a value that meets
   another span runs through it and on, as the text will read after the replacement (it meets its floor there). Every head
   counts, one inside another span too. The spans only grow; the loop stops when a round adds nothing.
3. `_redact_str`: the union. Overlapping spans merge (touching spans stay apart). Each merged span becomes ONE placeholder,
   of the class of its member with the earliest start; a tie goes by held > privkey > sk > bearer > envval (NAME=) >
   token > envval (widened). Text outside every span is kept byte for byte.

`tests/test_decisions_canonical.py` (227 added, 78 deleted): 46 expected strings replaced, each with a one-line rule
comment (section 5); comments that described the old yield or merge step fixed; the C5 block (:1306-1404, 41 named shapes).
`tests/test_decisions_ledger.py` (69 added, 4 deleted): two comments fixed; the C5 ledger twins (:1717-1778, 11 shapes).
`tests/test_decisions_redaction_properties.py` (new, 762 lines, 39 tests): the generator, the canary oracle, C1/C2/C3/C6,
and one named test per rule (the mutants' killers).

## 3. Deviations from the brief (read these first)

- **D-A: rule 5 is read on the text after the replacement (the closure in `_spans`); the brief's prototype has no such
  step.** Measured reasons: (1) the prototype's single union is not a fixed point: `password: xyBearer QZJ8QZJ8QZJ8QZJ8:tail`
  gives `password: <redacted:envval>:tail`, and a second pass takes `:tail` (C3 fails); d556c9b and fdac751 both hide
  `:tail` there. (2) My first closure (the union pass repeated on its own output) still lost one C2 case: seed 198 input
  638, a `PASSWD=` head inside another span whose value the references carried through a bearer to a later value. The
  closure inside the detection closes both. Effect: more masking in some layouts (for example the five merged R-4 rows now
  also hide the name after the merged placeholder). Idempotence is then a property of the one pass, not a loop.
- **D-B: the cut-placeholder guard also covers the upper-case `NAME=` form**; rule 4 names only the widened form. Measured
  reason: with held placeholders at the top rank, the prototype breaks C3 when the cut lands inside a held placeholder after
  `KEY=` (`KEY=<redacted:s` became `KEY=<redacted:e` on the second `decision_state`). The old code relabelled such a
  placeholder to envval; the brief's rule 4 forbids that.
- **D-C: linear every-start** (head + class run) instead of the prototype's whole-form lookahead. Measured: the prototype
  is quadratic (section 4, C6).
- **D-D: key-block BEGIN lines at every start too** (the prototype used `finditer`). Effect: a block glued to the END line
  before it (sharing its dashes) is hidden; d556c9b shows its body.
- **D-E: C2 "hides" is asserted at the redactor level, and through `decision_state` for every kind but the cut shift**
  (VERIFY-J1-1-R3 F-5). The cut-shift counts are pasted, not asserted; every one is a near-miss value (no form covers it
  in any version) that a reference's field limit cut and its own redactor showed.
- **D-F: generator limits.** Planted values never hold `<` or `>` (a value could spell a placeholder), and a `paths` list
  holds one item (adjacent defect A-1). Named tests cover held and cut placeholders; values with `<` and `>` were
  spot-checked (section 4, C1).
- **D-G:** C5's named tests are new rows in the two existing files (41 and 11), not layout pins.
- **D-H:** the property file reads private names: `_ROW_FIELDS`, `_SOURCE_REF_FIELDS` (the oracle's fixed row text) and
  `_matches`, `_RANK` (the equivalence test only). The C1/C2 oracle imports no redaction form.
- **D-I:** the C6 test also bounds 100,000-character inputs (the brief asks for 20,000).

## 4. Contract rows

### C1 leak — the canary sweep (`tests/test_decisions_redaction_properties.py::test_c1_c2_c3_canary_sweep`)
Generator: 21 text-carrying fields of the seven schemas in turn; covered forms (sk, bearer, upper NAME=, token, widened,
key block) with fake values from each class's alphabet and U+0130/U+0131/U+017F; context of prose, delimiters, names in
random case (special letters included) and with prefixes, glued `bearer`/`sk-` runs, whole placeholders, chains of two and
three assignments; near-miss values (under a floor, no name) for C2. A value LEAKS when one of its distinctive 4-character
windows (in no other input text, no placeholder, no fixed row text) is in `decision_state`, `canonical()`, the appended
line (`make_row -> append`, digests and locator masked) or `replay`'s row. Negative control
`test_the_oracle_sees_every_covered_value_when_nothing_is_redacted` (normalize only: every covered value found).

Full sweep, `J1R4_FULL=1 pytest "...::test_c1_c2_c3_canary_sweep[<seed>]" -q -s`, one call per seed (load average 5.5-7
on 4 cores; the ledger file then differed from its final bytes only by the S-2 rename, section 9):
```
2026-09-24T12:55:08Z
seed 20260924:
  C1 leak (every sink, every form): 0
  C2 d556c9b cut shift of a near-miss value: 464
  C2 d556c9b hidden by its redactor: 379161
  C2 d556c9b newly visible (decision_state, cut shift): 464
  C2 d556c9b newly visible (decision_state, redactor): 0
  C2 d556c9b newly visible (redactor): 0
  C2 fdac751 cut shift of a near-miss value: 439
  C2 fdac751 hidden by its redactor: 383317
  C2 fdac751 newly visible (decision_state, cut shift): 439
  C2 fdac751 newly visible (decision_state, redactor): 0
  C2 fdac751 newly visible (redactor): 0
  C3 non-idempotent: 0
  checked covered: 406534
  checked near-miss: 54870
  inputs: 100000
  oracle: a window in the row's non-state text: 0
  planted: 468710
  planted, no distinctive window: 7306
  refused (normalize, ledger, references): 0
.
1 passed in 292.04s (0:04:52)
rc=0
```
```
2026-09-24T13:00:07Z
seed 198:
  C1 leak (every sink, every form): 0
  C2 d556c9b cut shift of a near-miss value: 516
  C2 d556c9b hidden by its redactor: 375552
  C2 d556c9b newly visible (decision_state, cut shift): 516
  C2 d556c9b newly visible (decision_state, redactor): 0
  C2 d556c9b newly visible (redactor): 0
  C2 fdac751 cut shift of a near-miss value: 500
  C2 fdac751 hidden by its redactor: 379763
  C2 fdac751 newly visible (decision_state, cut shift): 500
  C2 fdac751 newly visible (decision_state, redactor): 0
  C2 fdac751 newly visible (redactor): 0
  C3 non-idempotent: 0
  checked covered: 403388
  checked near-miss: 54923
  inputs: 100000
  oracle: a window in the row's non-state text: 0
  planted: 465401
  planted, no distinctive window: 7090
  refused (normalize, ledger, references): 0
.
1 passed in 158.01s (0:02:38)
rc=0
```
The default run (2,500 inputs per seed) is part of the gate (section 6).

The first full sweep (12:20Z) failed on 3 inputs (seed 20260924: 26977, 28654, 70279), line and replay only. Reproduced:
each window (`duce`, `oduc`, `rodu`) sat in the row key `producer`, which my hand list of fixed row text had left out
(the state and `canonical()` were clean). An oracle defect, not a leak. Fix: the row keys come from the ledger module, and
the sweep now counts any window in a line's non-state text apart ("oracle: ...", asserted 0).

Spot check, values with `<` and `>` (outside the generator's alphabets), `redact()` directly:
```
'password: ab<cd>efQZJX' -> 'password: <redacted:envval>' | leaked: []
'KEY=<x>QZJX<y>' -> 'KEY=<redacted:envval>' | leaked: []
'api_key: QZ<J>X8QZJX' -> 'api_key: <redacted:envval>' | leaked: []
'password: QZJX<redacted:sk>QZJX' -> 'password: <redacted:envval>' | leaked: []
'token: QZJXQZJXQZJXQZJXQZJXQZJXQZJXQZJX<b>' -> 'token: <redacted:token>' | leaked: []
```

### C2 no regression against both references
The same sweep (above). Each reference is `git show <rev>:src/agent_factory/decisions/volatile.py` written under the test's
`tmp_path` and loaded by path; its blob is asserted (d556c9b 20ebcd54f3ed, fdac751 2d5cf0072469). Newly visible at the
redactor level: **0 against each, both seeds** (hidden by the reference's redactor: 379161 / 383317 and 375552 / 379763
planted values). Through `decision_state`: 0 of the redactor kind; the cut-shift counts (464, 439, 516, 500) are all
near-miss values (D-E).

### C3 idempotence
`decision_state(q, decision_state(q, s)) == decision_state(q, s)`: 0 failures in 200,000 generated states over every
schema's text fields (above); `make_row`'s own fixed-point check (`ledger.py:273`) refused 0 rows in the same inputs; the
ledger tests pass (section 6). Targeted: `test_a_cut_placeholder_at_the_end_is_no_span` (every placeholder cut at every
position after five heads, then a second `decision_state`). Closure rounds, measured over 40,000 generated fields and every
C6 input (a round = one call of `_regions`; the last round adds nothing):
```
rounds over 40,000 generated fields: {1: 20305, 2: 18762, 3: 933} max (3, (20260924, 4))
```
Inferred, not proved: NAME= values grow in round 1 (through spans holding whitespace), widened values in round 2 (through a
grown NAME= value holding a quote, `&`, `,` or `;`), and a round-2 extension covers no stop of either class.

### C4 goldens
`test_golden_digests_exact` and `test_relanding_stable`: `2 passed, 134 deselected in 0.05s`. `git diff --stat 8c684be --
tests/fixtures/decisions/` and `git diff --stat HEAD -- tests/fixtures/decisions/`: empty.

### C5 named shapes
- `tests/test_decisions_canonical.py::test_verifier_r3_shape_frees_no_value` (41 ids): VERIFY-J1-1-R3 section 2c
  (N1-sk-api_KEY, N1-sk-ApiKEY, N1-bearer-api_KEY, N1-sk-dotted-I, N1-control-API_KEY, N2-dot, N2-plus, N2-tilde-key,
  N2-control-no-inner-sk), section 4a (R4-n2-a, R4-n2-b, R1-a..g, R2-a..e, R4-a,b,c,h,i,d,e,f,g, R3-a..f, R3-pad),
  section 5's grid example (`item5-example`) and the brief's `stub` (`password: mykey=X4Z9Q`). Each asserts no canary
  character and no 4-character window of each planted value in `decision_state` and `canonical()`, and a fixed point.
  The 39 verifier shapes were checked character for character against `/tmp/vj113r3/n_cases.py` and `item4_cases.py`:
  `mismatches: 0 of 39`. Left out: `R3-floor7`, a 7-character value under the widened floor by design (visible at
  d556c9b, at fdac751 and here).
- `tests/test_decisions_ledger.py::test_verifier_r3_shape_value_never_reaches_the_ledger_file` (11 ids: the N1/N2 shapes,
  R4-n2-a, stub): `make_row -> append -> the line on disk -> replay`, no letter and no window of each value in the line or
  in `replay`'s row.
- The V-1 rows (D-057) and R-1..R-4 rows (D-059) keep their named tests and their no-value-byte assertions (section 5).
- Each rule has a named test in the property file (`test_every_start_and_greedy_value`, `test_union_merges_overlapping_spans`,
  `test_tie_at_the_same_start_goes_by_the_fixed_priority`, `test_a_held_placeholder_keeps_its_class_and_bytes`,
  `test_a_cut_placeholder_at_the_end_is_no_span`, `test_the_widened_floor_is_eight`, `test_a_value_runs_through_a_span_it_meets`,
  `test_a_key_block_glued_to_an_end_line_is_hidden`).

### C6 cost (`test_the_detection_stays_linear_on_the_worst_inputs`, `redact()` directly, one run per shape)
```
2026-09-24T13:02:53Z
C6 API_KEY= + one long value      20000 chars       4.5 ms
C6 API_KEY= + one long value     100000 chars      20.3 ms
C6 API_KEY= heads                 20000 chars      60.4 ms
C6 API_KEY= heads                100000 chars     244.2 ms
C6 BEGIN + a long label run       20000 chars      10.8 ms
C6 BEGIN + a long label run      100000 chars      50.3 ms
C6 BEGIN glued to END             20000 chars       8.7 ms
C6 BEGIN glued to END            100000 chars      43.1 ms
C6 BEGIN lines, no END            20000 chars       7.8 ms
C6 BEGIN lines, no END           100000 chars      40.1 ms
C6 END + a long label run         20000 chars      11.3 ms
C6 END + a long label run        100000 chars      50.3 ms
C6 bearer + 16-run                20000 chars       7.5 ms
C6 bearer + 16-run               100000 chars      33.9 ms
C6 bearer + whitespace runs       20000 chars       5.7 ms
C6 bearer + whitespace runs      100000 chars      28.8 ms
C6 bearer runs                    20000 chars      10.3 ms
C6 bearer runs                   100000 chars      53.9 ms
C6 key: heads                     20000 chars      25.6 ms
C6 key: heads                    100000 chars     160.4 ms
C6 mixed heads                    20000 chars      15.6 ms
C6 mixed heads                   100000 chars     112.6 ms
C6 placeholders                   20000 chars       7.7 ms
C6 placeholders                  100000 chars      38.7 ms
C6 sk- + one long run             20000 chars       4.1 ms
C6 sk- + one long run            100000 chars      20.2 ms
C6 sk- runs                       20000 chars      13.0 ms
C6 sk- runs                      100000 chars      57.1 ms
C6 token+ heads                   20000 chars      10.0 ms
C6 token+ heads                  100000 chars      42.8 ms
C6 widened over placeholders      20000 chars      10.5 ms
C6 widened over placeholders     100000 chars      53.2 ms
.
1 passed in 1.31s
rc=0
```
For comparison, the brief's prototype core (whole form at every start), scratch,
5,000 / 10,000 / 20,000 characters: `API_KEY= heads 102.4ms 406.1ms 1260.4ms ratios 3.97 3.10`, `sk- runs 24.4ms 64.3ms
248.1ms ratios 2.64 3.86`, `key: heads 62.9ms 235.2ms 952.5ms ratios 3.74 4.05`. The alarm in the test stops a runaway
match at 10 s; each case must finish under 2 s.

Equivalence of the linear detection with each form matched whole at every start
(`test_the_linear_detection_equals_every_form_matched_at_every_start`, 20,000 random texts with special letters, quotes,
placeholders and key blocks; every kind > 50 spans): green. Scratch negative control (the widened floor 7 in the linear
version only): `mismatches 3302`.

### C7 no model
`tests/test_decisions_no_model.py`: 4 of the gate's 339 (section 6). Imports in `src/agent_factory/decisions/`: `bisect`,
`os`, `re`, `unicodedata`, `dataclasses`, `hashlib`, `json`, `posixpath`, `stat` and the package's own modules; no model
package.

## 5. Changed expected layouts (46 rows; every input row kept; every no-value-byte assertion kept; no skip or xfail)

| test function | rows changed |
|---|---|
| `test_v1_class_beyond_the_driver` | 15 |
| `test_v1_name_swallowed_by_sk_or_bearer_frees_no_value` | 8 |
| `test_r4_env_check_reads_the_value_after_the_bearer_merge` | 6 |
| `test_bearer_merge_step_keeps_every_j1_1_r2_redaction` | 5 |
| `test_surviving_mutant_rows_stay_redacted` | 4 |
| `test_r2_token_check_reads_the_run_as_the_token_class_does` | 4 |
| `test_r3_upper_name_equals_space_value_behind_sk_or_bearer` | 3 |
| `test_token_named_residual_shape_redacted` | 1 |

Same functions and counts as the premise's 46. Before the edit, each changed row was checked on the final code: no value
byte, no `abcdefgh`, a fixed point, and the same digest with another fake value (46 of 46). `tests/test_decisions_ledger.py`:
no expected string changed (its assertions are body-only). Comments that described the old yield or merge step as current
were fixed in both files (for example the J1-1-R2 and J1-1-R3 block headers, the `NAME==v` residue note, now hidden).

## 6. Gates

```
$ pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py tests/test_decisions_no_model.py \
    tests/test_decide_harvest.py tests/test_decisions_redaction_properties.py -q -p no:cacheprovider --basetemp /tmp/j1r4b/bt
2026-09-24T13:31:06Z  339 passed in 99.11s (0:01:39)    run 1 rc=0
2026-09-24T13:32:45Z  339 passed in 103.82s (0:01:43)   run 2 rc=0
set: 5 files set=b2e178f42ec6     files: volatile 0cfe104a7996, canonical 8e039e2c3674, ledger 3cb623f2345d,
                                   properties 2dfc6300162f (sha256 prefixes); U+2028/U+2029 count 0 in each
$ python3 scripts/lint_delta.py --base HEAD         -> 3 .py changed, 0 NEW pyflakes hit(s), 0 removed; rc=0
  (advisory tells: AF-AP-152 on volatile.py, answered by the C6 test; AF-AP-39 on the canonical test file, fake values in
  f-strings, no command line)
$ python -m pyflakes (the four files)               -> rc=0
$ node .gitnexus/run.cjs detect-changes --scope all --repo .      (12:49Z; the symbol list is cut at 15 by the tool)
Changes: 3 files, 46 symbols
Affected processes: 8
Risk level: high
Affected execution flows:
  • Make_row → _cut_placeholder (7 steps) — changed: decision_state, _redact_str, _spans, _matches, _cut_placeholder
  • Make_row → _nfc_collapse (6 steps) — changed: decision_state
  • Make_row → _refuse_path (6 steps) — changed: decision_state
  • Make_row → _regions (6 steps) — changed: decision_state, _redact_str, _spans, _regions
  • Make_row → _stops (6 steps) — changed: decision_state, _redact_str, _spans, _stops
  • Make_row → _apply_case (5 steps) — changed: decision_state
  • Make_row → _strip_pin_suffix (5 steps) — changed: decision_state
  • Make_row → Bound (4 steps) — changed: decision_state
```
The index is stale: `Indexed commit: 40543ab`, `Current commit: 3161435`; the new test file (untracked) is not in its count.
Risk "high": every flow is `make_row -> decision_state`, which this lane changes by design. Impact before editing
(`_redact_str`, `redact`, `_yield_pattern`: LOW; `_envval_wide`: UNKNOWN, confirmed unused outside the module by grep).

## 7. Mutants (scratch copy of the tree's four files; `PYTHONPATH` guard asserts the copy's `volatile.py` is imported)

Final run (13:20Z..13:28Z; `volatile.py`, the canonical and the property files at their final bytes; the ledger file before
the S-2 rename only), counts equal to the first full run at 12:38Z, 268 tests each:

| mutant | result | a named killer (re-run alone: mutant red, pristine green) |
|---|---|---|
| M1 overlap rule dropped (overlapping spans not merged) | 100 failed, 168 passed | `test_union_merges_overlapping_spans[union-takes-the-longer-end]`; `test_verifier_r3_shape_frees_no_value[stub]` |
| M2a drop one detector: sk | 80 failed, 188 passed | `test_secret_redacted_every_class` |
| M2b drop one detector: bearer | 64 failed, 204 passed | `test_v1_control_keeps_its_pin_redaction[C-4]` |
| M2c drop one detector: envval (NAME=) | 20 failed, 248 passed | `test_v1_class_beyond_the_driver[upper-key-short]` |
| M2d drop one detector: token | 32 failed, 236 passed | `test_order_is_normalize_then_redact` |
| M2e drop one detector: wide | 128 failed, 140 passed | `test_env_assignment_forms_redacted_and_prose_kept` |
| M2f drop one detector: privkey | 11 failed, 257 passed | `test_private_key_blocks_longer_than_the_limit_gnupg_and_endless` |
| M3 priority table reversed | 21 failed, 247 passed | `test_a_cut_placeholder_at_the_end_is_no_span[token = ]`; `test_token_named_residual_shape_redacted[run-then-base64url-tail]` |
| M4 held-placeholder protection removed | 26 failed, 242 passed | `test_a_held_placeholder_keeps_its_class_and_bytes[password: <redacted:token>]` |
| M5 cut-placeholder guard removed | 11 failed, 257 passed | `test_a_cut_placeholder_at_the_end_is_no_span[KEY=]` |
| M6 finditer in place of every-start (whole form, non-overlapping) | 7 failed, 261 passed | `test_every_start_and_greedy_value[head-inside-a-value]`; `test_v1_class_beyond_the_driver[chain-widened]` |
| M7 union replaced by first-wins | 9 failed, 259 passed | `test_a_key_block_glued_to_an_end_line_is_hidden` |
| M8 widened floor at 0 | 10 failed, 258 passed | `test_the_widened_floor_is_eight[prose]` |
| M9 no closure (base spans only) | 13 failed, 255 passed | `test_a_value_runs_through_a_span_it_meets[under-the-floor-into-a-span]` |
| M10 closure: a value stops at the delimiter inside a span | 12 failed, 256 passed | `test_a_value_runs_through_a_span_it_meets[widened-over-bearer]` |
| M11 closure: a head inside another span is not extended | 2 failed, 266 passed | `test_a_value_runs_through_a_span_it_meets[head-inside-a-span]` |
| M12 bearer padding dropped | 5 failed, 263 passed | `test_v1_class_beyond_the_driver[padding]` |
| M13 token head without `(?<=_)` | 15 failed, 253 passed | `test_v1_name_swallowed_by_sk_or_bearer_frees_no_value[V1-e]` |
| M14 bearer run case-sensitive (R-1) | 20 failed, 248 passed | `test_r1_bearer_run_takes_the_pin_letters[dotless-i-inside]`; `test_verifier_r3_shape_frees_no_value[R1-a]` |
| M15 sk floor 8 -> 9 | 22 failed, 246 passed | `test_v1_name_swallowed_by_sk_or_bearer_frees_no_value[V1-a]` |
| M16 token floor 32 -> 33 | 5 failed, 263 passed | `test_secret_redacted_every_class` |
| BASELINE (no edit) | 268 passed | — |

M1-M8 are the brief's eight kinds ("drop one detector" once per detector); M9-M16 are mine. After the mutant runs the C5
ledger list was renamed (section 9, S-2); no test's data changed. The first run's per-test lists were overwritten; the
named killers above were re-run one by one on the final files against their mutant (red) and the pristine copy (green).

## 8. Adjacent defects (reported, not fixed)

- **A-1 (pre-existing, outside the pass): `normalize` sorts a `paths` list BEFORE `redact`, so redaction can change the
  order and `decision_state` is then not a fixed point; `make_row` refuses such a row (fail closed, no leak).** Probe
  (`paths = ["a/b", "a/sk-QZJ8QZJ8QZJ8"]`): d556c9b, fdac751 and the new code each give `['a/b', 'a/<redacted:sk>'] ->
  ['a/<redacted:sk>', 'a/b'] NOT-IDEMPOTENT`. The `decision_state` docstring's idempotence claim does not name it.
- **A-2:** `tests/test_decisions_no_model.py`'s `J1_TESTS` does not list the new property file, so the model-blocked
  subprocess run does not cover it (that file is outside my boundary).
- **A-3:** the replaced comments cited the scrubber's lines 29-31 and 33; those lines moved (now 57-62 and 64). My new
  comments cite the current lines.
- **A-4:** `R3-floor7` (a 7-character value) stays visible by design (the widened form's floor).
- **A-5:** the GitNexus index is stale (section 6).

## 9. Self-attack: the three most likely ways this change is wrong

1. **A leak class the generator never draws.** The oracle only sees its own grammar. Checked: C2 against both references at
   the redactor level (0 of 754,713 and 763,080 hidden values newly visible), all 41 verifier and brief shapes, special
   letters in names and runs, values with `<` and `>` (spot check). Not checked: whitespace inside a value before
   normalize (the value classes stop at whitespace by design), case folds other than U+0130/U+0131/U+017F/U+212A, states
   with secrets in several fields at once (the sweep fills one field per input).
2. **The closure breaks idempotence or over-masks for a consumer.** Checked: 200,000 states, 0 non-idempotent; the cut test
   over every placeholder prefix; the existing straddle tests; goldens unchanged; `test_decide_harvest.py` (67) green.
   Over-masking is real and visible in the 46 layouts (names next to a placeholder go more often).
3. **The linear rewrite differs from the forms.** Checked: the equivalence test (20,000 texts, every kind > 50 spans) and
   60,000 scratch inputs (0 mismatches), a scratch negative control (3,302 mismatches), and mutants M2a-f, M6, M12-M16 red.

Found and fixed during the lane (S-1, S-2): S-1, the oracle's missing row key (section 4, C1). S-2, my C5 ledger list first
reused the module name `_R4_SHAPES` of an existing list; the existing test had captured its list at decoration time
(collection unchanged, 93), and the new list is now `_VERIFIER_R3_SHAPES` (no module name is bound twice in the four files).

## 10. Evidence tiers

- Verified this session (a pasted run or probe): the premise; C1-C7 as pasted; the 46 layout rows; the mutant table; the
  prototype's premise outputs, its quadratic cost and its two C3 breaks; A-1's probe; lint and detect-changes.
- Inferred: the three-round bound of the closure (argument in C3; the measured maximum is 3).
- Assumed: CI's full-history checkout serves `git show d556c9b:...` and `fdac751:...` (the workflow sets `fetch-depth: 0`;
  not run in CI by me).

## 11. NOT done

- No commit, push, PR or comment (the coordinator commits after the verify).
- CI's whole `pytest tests/` suite not run; only the brief's five-file gate. The new file adds about 24 s to it by default.
- No PC run. The 100,000-input sweep runs only with `J1R4_FULL=1` (not in the default gate).
- Nothing else. `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/J1-1-R4-report.md` (round 1 of 3):
  `report_lint: 38 refs — OK 38, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`, rc=0.

## 12. Line references (as of the final bytes; `scripts/report_lint.py` checks them)

- src/agent_factory/decisions/volatile.py:26 `import bisect`
- src/agent_factory/decisions/volatile.py:82 `_NAME`
- src/agent_factory/decisions/volatile.py:84 `_FORMS`
- src/agent_factory/decisions/volatile.py:101 `_DETECTORS`
- src/agent_factory/decisions/volatile.py:105 `_PADDING`
- src/agent_factory/decisions/volatile.py:112 `_PRIVKEY_BEGIN`
- src/agent_factory/decisions/volatile.py:113 `_PRIVKEY_END`
- src/agent_factory/decisions/volatile.py:116 `_HELD`
- src/agent_factory/decisions/volatile.py:119 `_RANK`
- src/agent_factory/decisions/volatile.py:121 `_THROUGH`
- src/agent_factory/decisions/volatile.py:122 `_THROUGH_RANKS`
- src/agent_factory/decisions/volatile.py:347 `def _cut_placeholder`
- src/agent_factory/decisions/volatile.py:357 `def _matches`
- src/agent_factory/decisions/volatile.py:387 `def _regions`
- src/agent_factory/decisions/volatile.py:399 `def _stops`
- src/agent_factory/decisions/volatile.py:426 `def _spans`
- src/agent_factory/decisions/volatile.py:461 `def _redact_str`
- src/agent_factory/decisions/volatile.py:497 `def decision_state`
- src/agent_factory/decisions/ledger.py:273 `restate` (the fixed-point check)
- src/agent_factory/decisions/ledger.py:404 `raw_state` (make_row's call)
- src/agent_factory/decisions/canonical.py:77 `canonical(decision_state(question_id, state, root))`
- scripts/transcript_export.py:57-62 `PGP PRIVATE KEY BLOCK` (the key-block label family)
- scripts/transcript_export.py:64 `8-character floor`
- tests/test_decisions_canonical.py:1393 `def test_verifier_r3_shape_frees_no_value`
- tests/test_decisions_ledger.py:1752 `def test_verifier_r3_shape_value_never_reaches_the_ledger_file`
- tests/test_decisions_redaction_properties.py:456 `def test_c1_c2_c3_canary_sweep`
- tests/test_decisions_redaction_properties.py:475 `def test_the_oracle_sees_every_covered_value_when_nothing_is_redacted`
- tests/test_decisions_redaction_properties.py:496 `def test_generator_plants_every_form_and_context_class`
- tests/test_decisions_redaction_properties.py:536 `def test_every_start_and_greedy_value`
- tests/test_decisions_redaction_properties.py:555 `def test_union_merges_overlapping_spans`
- tests/test_decisions_redaction_properties.py:576 `def test_tie_at_the_same_start_goes_by_the_fixed_priority`
- tests/test_decisions_redaction_properties.py:587 `def test_a_held_placeholder_keeps_its_class_and_bytes`
- tests/test_decisions_redaction_properties.py:593 `def test_a_cut_placeholder_at_the_end_is_no_span`
- tests/test_decisions_redaction_properties.py:619 `def test_the_widened_floor_is_eight`
- tests/test_decisions_redaction_properties.py:641 `def test_a_value_runs_through_a_span_it_meets`
- tests/test_decisions_redaction_properties.py:648 `def test_a_key_block_glued_to_an_end_line_is_hidden`
- tests/test_decisions_redaction_properties.py:689 `def test_the_linear_detection_equals_every_form_matched_at_every_start`
- tests/test_decisions_redaction_properties.py:740 `def test_the_detection_stays_linear_on_the_worst_inputs`
