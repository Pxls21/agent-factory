# VERIFY-J1-1-R4 — report (task #198; D-070 as amended by D-073; rule 0f)

Lane: verify-j1-1-r4 (sandbox, adversarial-verifier, Opus 5.5, shared tree, no worktree). Brief:
`tasks/briefs/laya/VERIFY-J1-1-R4-brief.md`. Frozen contract: C1-C7 of `tasks/briefs/laya/J1-1-R4-REDESIGN-brief.md`
as amended by D-073 (`docs/08_DECISION_LOG.md`). The builder's report `tasks/briefs/laya/J1-1-R4-report.md` is an input
to attack. Nothing committed, nothing pushed, no bridge call. Scratch: `/tmp/vj11r4/` (references, mutants, drivers).
Status: COMPLETE 2026-09-24 15:02Z. GATE RECOMMENDATION (section 17): MERGE-READY-WITH-FOLLOWUPS. Finding inventory:
section 12; the blocking predicate: section 13. Sections appear in the order they were written (section 7 follows 10).

## 0. Premise (re-measured 2026-09-24 13:47Z-13:53Z)

The four boundary blobs match the PIN exactly. HEAD moved twice after the brief (d0b1748 = the brief's own commit;
a4031e3 and cb131aa = wiki and incident-log lines only); `git diff --stat 9fc89ba HEAD` over `src/agent_factory/decisions`,
the six gate test files, `tests/fixtures/decisions` and `scripts/decide-harvest` is EMPTY.

```
$ git rev-parse --short HEAD                      -> cb131aa   (brief: 9fc89ba; 3 commits after it, none in the boundary)
$ git hash-object volatile.py test_decisions_canonical.py test_decisions_ledger.py test_decisions_redaction_properties.py
fe48dd32aec165a0fb6f8be0c531f4dd835f7a40   (PIN fe48dd32...)  MATCH
d33945a0195e3f5c6a60690f068f6f90744b49b0   (PIN d33945a0...)  MATCH
d13c3bd83edbbbef5282c4c458c8d35a2058fc57   (PIN d13c3bd8...)  MATCH
ebe46e0fe16460f8509a194924a912c867d0d79a   (PIN ebe46e0f...)  MATCH
$ git log --format='%h %s' -3 -- src/agent_factory/decisions/volatile.py
132b80e decisions: J1-1-R4 - the redaction pass redesigned ... (GATED-PENDING-VERIFY)
fdac751 J1-1-R3 landed GATED-PENDING-VERIFY ...
fb016d0 J1-1-R2 landed ...
$ grep -c -E '^def (test_|_)' tests/test_decisions_redaction_properties.py   -> 37   (PIN 37)
```
Machine: 4 cores, load average 4.9-5.6 from other lanes at the start (a Laya server, other lanes' mutant runs).
Every timing below is on this contended box.

Re-checked after the worker restart (about 14:49Z) and again at the end (15:02:05Z): the four blobs are unchanged
(fe48dd32aec1 d33945a0195e d13c3bd83edb ebe46e0fe164). Two pushes rewrote the commit ids meanwhile (the brief's commit
d0b1748 is now ece8dd1; HEAD 211b095 at the end); `git diff --stat 9fc89ba HEAD` over the boundary (the decisions package,
the six gate test files, the fixtures, `scripts/decide-harvest`) is still EMPTY.

The five-file gate of the premise, re-run by me (13:53:47Z-13:56:09Z):
```
$ bash scripts/test_summary.sh tests/test_decisions_canonical.py tests/test_decisions_ledger.py tests/test_decisions_no_model.py \
    tests/test_decide_harvest.py tests/test_decisions_redaction_properties.py --basetemp /tmp/vj11r4/bt
339 passed in 142.12s (0:02:22)
pytest-exit: 0
```
339 = the premise's count and the builder's (report section 6).

## 1. Item 1: the builder's C1/C2/C3 sweep on seeds of my own choosing (REPRODUCED)

Driver `/tmp/vj11r4/sweep_builder.py`: imports the property module read-only and calls its own `_run_seed` and
`_report` (generator, oracle, both references from `git show` with their blobs asserted, and `make_row -> append ->
the line on disk -> replay` for every input), 100,000 inputs per seed, 4 processes. Seeds 424242 and 31337.
```
seed 424242 (13:56:21Z-14:02:57Z, 394.9 s)         seed 31337 (14:03:11Z-14:09:30Z, 379.5 s)
  C1 leak (every sink, every form): 0                C1 leak (every sink, every form): 0
  C2 d556c9b hidden by its redactor: 378402          C2 d556c9b hidden by its redactor: 377956
  C2 d556c9b newly visible (redactor): 0             C2 d556c9b newly visible (redactor): 0
  C2 d556c9b newly visible (decision_state, redactor): 0    (same): 0
  C2 d556c9b newly visible (decision_state, cut shift): 446  (same): 504
  C2 fdac751 hidden by its redactor: 382595          C2 fdac751 hidden by its redactor: 382235
  C2 fdac751 newly visible (redactor): 0             C2 fdac751 newly visible (redactor): 0
  C2 fdac751 newly visible (decision_state, redactor): 0    (same): 0
  C2 fdac751 newly visible (decision_state, cut shift): 437  (same): 497
  C2 * cut shift of a near-miss value: 446 / 437     cut shift of a near-miss value: 504 / 497
  C3 non-idempotent: 0                               C3 non-idempotent: 0
  checked covered: 406145   near-miss: 54398         checked covered: 405778   near-miss: 54878
  planted: 467662 (no distinctive window: 7119)      planted: 467761 (no distinctive window: 7105)
  oracle: a window in the row's non-state text: 0    oracle: ...: 0
  refused (normalize, ledger, references): 0         refused decision-state-abs-path: 1
```
Every cut-shift value is of the near-miss kind (no "cut shift of a covered value" line on either seed). The one refusal
on seed 31337 is a GENERATOR artifact, found by replaying the generator: input 84384, `b1.finding_kind.file =
"p/../-----BEGIN PGP PRIVATE KEY BLOCK----- ..."`, which `normalize` refuses for `/../` (see finding F-10).

## 2. My own oracle (used by items 2-5)

`/tmp/vj11r4/vlib.py`, independent of `volatile.py` for the COVERAGE decision: the five value forms and the key block
written out from the redesign brief (rule 6 and the prototype's forms), each matched WHOLE at EVERY start by a lookahead,
with the brief's rule-4 guard. Two checks:
- EXACT (position level, no windows): every position a form covers lies inside the union of the implementation's merged
  spans, AND `_redact_str`'s output equals the replacement of those merged spans rebuilt in my code. Together: no covered
  character is kept. Negative control: with `_spans` emptied, `password: QZJ8QZJ8QZJ8` reports `covered-kept` at
  positions 10-21 (run 14:0xZ).
- WINDOWS at the sinks (as the builder's): distinctive 4-character windows of each planted core in `decision_state`,
  `canonical()`, the parsed state of the line `make_row -> append` wrote, and `replay`'s row; plus a count of windows
  found in the line's non-state text (digests and locator masked) as an oracle-miss detector.
Three defects of MY first draft were found by its own smoke run and fixed before any number below: the replay sink
searched the whole row (hex digests matched digit windows: 3 false hits), cores holding U+212A were searched un-NFC'd,
and the closure-round counter counted two `_spans` calls per field.

## 3. Item 2: the builder's named gaps

**2a. Secrets in several fields of one state at once.** My sweep (section 7) plants in EVERY text field of every state
(2-4 fields per schema, `paths` with 1-4 items) and runs each state through `make_row -> append -> replay`. Result there.

**2b. Whitespace inside a value before normalize** (hand probes `/tmp/vj11r4/probe_hand.py`, redactor level on the
normalized text, new vs d556c9b vs fdac751, exact check and fixed point on each):
```
'password: QZJ8<NBSP>X4Z9X4Z9X4Z9'  -> 'password: QZJ8 X4Z9X4Z9X4Z9'           same at both refs (4 chars: under the floor)
'API_KEY=QZJ8<TAB>X4Z9X4Z9'         -> 'API_KEY=<redacted:envval> X4Z9X4Z9'   same at both refs
'bearer QZJ8QZJ8<EMSP>X4Z9...'      -> unchanged (8-char run: under 16)      same at both refs
'token:<IDEOGRAPHIC SP><32 run>'    -> 'token: <redacted:token>'             same (normalize makes it one space)
'password :<TAB><TAB>X4Z9X4Z9X4Z9'  -> 'password : <redacted:envval>'        same
'sk-QZJ8<NEL>X4Z9X4Z9X4Z9'          -> unchanged (NEL is whitespace: sk-QZJ8 under 8)  same
'sk-QZJ8<ZWSP>X4Z9X4Z9X4Z9'         -> unchanged (U+200B is no whitespace, no sk char) same
```
Every case: exact check True, a fixed point, byte-identical to both references. Normalize collapses every `\s` run
(Python's `\s` = `str.isspace`) to one space BEFORE redact, and every value class stops at that space; a value split by
whitespace is two values, each measured against its floor. By design in all three versions; no form covers the parts.

**2c. Case folds other than U+0130, U+0131, U+017F, U+212A.** Closed by enumeration over all 1,114,112 code points: the
only non-ASCII characters Python's `re` accepts for a case-blind name letter or for the bearer and token run classes are
exactly those four (K: U+212A; S: U+017F; I: U+0130, U+0131; the run classes: all four). NFC maps U+212A to `K` before
redact runs. NFC also maps exactly two more code points into ASCII: U+037E to `;` (a widened-value stop) and U+1FEF to a
backtick; both in normalize, identical in all three versions (`password: X4Z9X4Z9<U+037E>QZJ8...` -> the first 8 hidden,
the rest after `;` visible at all three). Look-alikes that are not case folds (fullwidth `ＫＥＹ=`, Cyrillic `kеy:`, the
ligature `ﬆecret:`, a BOM inside `pass<BOM>word:`) are covered by no form and visible at all three versions (F-11).

**2d. The cut-shift kind through decision_state (D-E).** Both of my builder-sweep seeds: every cut-shift value is of the
generator's near-miss kind (446/437 and 504/497; no covered one). My own sweep classifies each newly visible value by my
INDEPENDENT forms (`cov=` in section 7), so a generator label cannot hide a covered one; and the exact check makes a
covered cut-shift impossible (bound only cuts redact's output, which keeps no covered position).

## 4. Item 3: new shapes (hand probes `/tmp/vj11r4/probe_hand.py`: 46 cases, 46 exact-check True and fixed points, 0 exceptions; each beside both references)

- **A secret in a dict KEY / nested dicts, lists, bytes** (a non-string field value is `str()`'d by normalize):
  `{'sk-X4Z9X4Z9X4Z9': 1}` -> `{'<redacted:sk>': 1}`; `{'password': 'X4Z9X4Z9X4Z9'}` -> value hidden; `{'a': {'b':
  {'API_KEY': 'X4Z9X4Z9'}}}` -> hidden; `b'password: X4Z9X4Z9X4Z9'` -> hidden; `{'Bearer <16>'}` -> hidden. Identical at
  both references. Visible at ALL THREE (no form covers them): `{'password': ['X4Z9X4Z9X4Z9']}` and
  `['API_KEY', '=', 'X4Z9X4Z9']` (F-11).
- **An input that spells a placeholder (D-F)**: `password: X4Z9<redacted:bearer>QZJ8` -> `password: <redacted:envval>`;
  `password: <redacted:X4Z9X4Z9>` (a fake class) -> hidden; `password: <redacted:sX4Z9X4Z9` -> hidden;
  `password: X4Z9X4Z9<redacted:s` (a cut prefix after a secret, at the end) -> hidden; `password: <<redacted:sk>>X4Z9X4Z9`
  -> hidden. Differs from both references in the LABEL only: `password: <redacted:sk>X4Z9X4Z9` -> `password:
  <redacted:sk>` (refs: `<redacted:envval>`), `API_KEY=<redacted:token>X4Z9X4Z9` -> `API_KEY=<redacted:token>` (the held
  placeholder wins the tie at the same start, rule 3/4). Visible at all three: `token <redacted:sk><32 run>` and the tail
  in `sk-X4Z9X4Z9<redacted:sk>X4Z9` (no form covers a run after a placeholder).
- **A value that meets two other spans at once (the D-A closure)**: `password: a-sk-X4Z9X4Z9Xbearer <16>:tail` ->
  `password: <redacted:envval>` (BOTH references leave the bearer run `QZJ8QZJ8QZJ8QZJ8:tail` visible: the new code hides
  a value the references leak); `KEY=a"bearer <16>"sk-X4Z9X4Z9X4Z9'tail more` -> `KEY=<redacted:envval> more` (same at
  refs); `password:KEY=token:<32>&api_key=X4Z9X4Z9X` -> `password:<redacted:envval>` (same); two key blocks joined by a
  quote inside a widened value (same).
- **A head at the very end of the field limit**: in my sweep (25% of bounded fields are padded so the last head or value
  straddles the limit), checked by C1 at every sink and by C3 through decision_state (section 7); and a dedicated grid:
  every bounded field's limit (all 16 non-enum fields with a limit, limits 40/80/120/200/400), 13 head/value shapes (`KEY=`, `API_KEY=`,
  `password: `, `"api_key": "`, `token: `, `_TOKEN `, `bearer `+padding, `sk-`, a key block, a widened value into a
  bearer run, a NAME= value into a bearer run and a glued name, a held placeholder + tail, NAME= + held + tail), the limit
  placed at every offset from 8 characters before the head to past the value: **8,819 cases, 0 C3 failures
  (`decision_state` of its own output), 0 canary characters (Q, Z, J, 8) in the output field.**
- **NFC re-composition after a placeholder (a new C3 exception class, F-6).** `canonical()` and the next `normalize`
  apply NFC. A placeholder ends in `>`, and `>` + U+0338 (combining long solidus overlay) composes to `≯` (U+226F).
  Redaction can leave a U+0338 right after a placeholder when the span's class excludes it (sk, bearer, key block):
  ```
  raw 'sk-QZJ8QZJ8QZJ8<U+0338>rest'   ds1 = '<redacted:sk>'+U+0338+'rest'   ds2 = '<redacted:sk' + U+226F + 'rest'
    new / d556c9b / fdac751: NOT-IDEMPOTENT (all three);  make_row -> append: refused decision-row-state-not-canonical
  raw 'bearer QZJ8QZJ8QZJ8QZJ8<U+0338> rest'                    NOT-IDEMPOTENT at all three; make_row refuses
  raw '-----BEGIN RSA PRIVATE KEY----- AAAA -----END RSA PRIVATE KEY-----<U+0338>x'   NOT-IDEMPOTENT at all three
  raw 'token: <32 run><U+0338>'   FIXED at all three (the widened value takes U+0338 and the union covers it)
  ```
  No secret byte is involved (the value is already replaced); the effect is a refused row. Pre-existing at both
  references; the `decision_state` docstring names one known idempotence exception (J1-1-R1 D-2) and neither this nor A-1.
- **Non-UTF-8 / surrogate text**: a lone surrogate inside a widened value -> hidden; inside a bearer run -> it breaks the
  run (visible at all three versions); `make_row` refuses any surrogate (its `state_digest` encode raises, wrapped as
  `decision-row-invalid`), so nothing reaches the ledger. `API_KEY=X4Z9<NUL>X4Z9` -> hidden.

## 5. Item 4: the closure's over-masking (D-A)

**Real data: no row changes.** `scripts/decide-harvest` run read-only over every committed source at HEAD (277 sources,
`--out` in scratch), three times: the tree's code, and scratch copies whose `volatile.py` is d556c9b's (blob
20ebcd54f3ed) or fdac751's (2d5cf0072469):
```
new / d556c9b / fdac751: harvest: 298 rows (ap.violates_row=143, v1.finding_class=152, wf.drift=3); refused: 90 records
refusal lines identical across the three (78 no-title-column, 10 bad-title, 2 bad-class)
rows whose state differs, new vs fdac751: 0 of 298; row_digest differs: 0
rows whose state differs, new vs d556c9b: 0 of 298; row_digest differs: 0
rows holding any placeholder: 3
J2 sample (docs/research/findings/j2-v1-probe/sample.json, drawn at 14add38 BEFORE the redesign landed at 132b80e):
  its 100 row_digests found in the new-code ledger: 100 of 100
```
**Consumers.** `scripts/decide-harvest` reads no state field (it calls `make_row`/`append` and `replay` for validation;
it prints refusal REASON codes only, never the detail). `docs/research/findings/j2-v1-probe/v1_probe.py` reads
`question_id`, `row_digest`, `incumbent_answer`, `state["lane"]` and `state["title"]`. The schema is closed, so no key can
disappear; on the committed corpus no value changes either. **No consumer loses a field it reads.**

**Synthetic layouts where a NAME is now hidden** (`/tmp/vj11r4/names_hidden.py`: 40,000 dense generated texts, half from
the builder's generator, half from mine; a text counts when a name the reference keeps is gone in the new output:
d556c9b 5,471 (13.68%), fdac751 7,015 (17.54%)). Minimal hand examples:
```
L1  'PASSWD=x,sk-abcdefghbearer QZJ8QZJ8QZJ8QZJ8,AGENT_TOKEN: X4Z9X4Z9X4Z9 rest'
    new:     'PASSWD=<redacted:envval> <redacted:envval> rest'
    refs:    'PASSWD=<redacted:envval> QZJ8QZJ8QZJ8QZJ8,AGENT_TOKEN: <redacted:envval> rest'   (both refs show the bearer run)
L1b 'PASSWD=xbearer QZJ8QZJ8QZJ8QZJ8,AGENT_TOKEN: X4Z9X4Z9X4Z9 rest'
    new:     'PASSWD=<redacted:envval> <redacted:envval> rest'
    refs:    'PASSWD=<redacted:envval> X4Z9X4Z9X4Z9 rest'   (both refs: NAME= eats AGENT_TOKEN, its 12-char value SHOWS)
L6  'task-password:v1bearer QZJ8QZJ8QZJ8QZJ8==token: X4Z9X4Z9X4Z9 rest'   (the builder's R-4 note)
    new:     'ta<redacted:sk>:<redacted:envval> <redacted:envval> rest'
    refs:    'ta<redacted:sk>:v1<redacted:bearer>token: <redacted:envval> rest'
control 'PASSWD=xbearer QZJ8QZJ8QZJ8QZJ8 AGENT_TOKEN: X4Z9X4Z9X4Z9 rest' -> the name after a SPACE stays (all three)
```
The layouts: (i) a `NAME=` value (`\S+`) that meets a span holding whitespace (a bearer run, a key block, an sk+bearer
union) runs through it to the next whitespace, so a name GLUED after that span (`,NAME:`, `==token:`) is hidden;
(ii) a widened value that meets a span holding a quote, `&`, `,` or `;` runs through it likewise; (iii) rule 5's greedy
value over a later head (`password: mykey=...`, also at both references). A name after whitespace is never hidden by the
closure. In the sampled cases the hidden name is collateral of hiding a value that the reference itself shows (L1, L1b).

## 6. Item 6: the adjacent defects A-1 and A-2 (both REPRODUCED)

**A-1 (paths order and a second pass).** Reproduced at all three versions, identical:
```
paths = ["a/b", "a/sk-QZJ8QZJ8QZJ8"]  (v1.finding_class)
new      ['a/b', 'a/<redacted:sk>'] -> ['a/<redacted:sk>', 'a/b'] NOT-IDEMPOTENT
d556c9b  ['a/b', 'a/<redacted:sk>'] -> ['a/<redacted:sk>', 'a/b'] NOT-IDEMPOTENT
fdac751  ['a/b', 'a/<redacted:sk>'] -> ['a/<redacted:sk>', 'a/b'] NOT-IDEMPOTENT
make_row -> append: refused decision-row-state-not-canonical      (fail closed; nothing written)
paths = ["a/b", "b/sk-QZJ8QZJ8QZJ8"] (redaction keeps the order) -> accepted, ['a/b', 'b/<redacted:sk>']
```
Mechanism (primary source): `_normalize_field` sorts a list BEFORE `redact` (volatile.py:199-200), and `redact` maps each
item (:340-341) without re-sorting, so a redaction that moves an item across another breaks `decision_state`'s fixed point;
`_validate_row` (d) (ledger.py:270-281) then refuses the row. No byte leaks and nothing corrupt is written: the effect is a
lost row. Incidence against the references is in section 7 (my sweep draws 1-4 items per `paths` list). Grade: pre-existing
at both references, fail-closed, accepted by D-073 as D-F (the generator's one-item lists); the fix (sort after redact, or
re-sort in `redact`) sits in `volatile.py` but outside the redaction pass the redesign contract scoped (F-4, FOLLOW-UP).

**A-2 (`tests/test_decisions_no_model.py` coverage).** Reproduced by reading: `J1_TESTS` (:25-30) lists canonical, ledger,
decide_harvest and no_laya_in_gates, not the new property file, so the model-blocked subprocess run never executes it.
Graded by running it under the test's own blocker helper (`_run_blocked`, the same `sitecustomize` import blocker):
```
python -m pytest tests/test_decisions_redaction_properties.py (model packages blocked)  -> rc 0, 39 passed in 31.33s,
                                                                                            blocked import attempts: []
negative control, same harness: python -c "import laya"                                  -> rc 1, attempts ['laya'],
                                                                                            "ImportError: model-import-blocked: laya"
```
The file has no model dependency today; the gap is that no gate would catch one added later. C7's two frozen clauses
(the no-model test green; no model import in `src/agent_factory/decisions/`) hold: the imports there are `bisect`, `os`,
`re`, `unicodedata`, `dataclasses`, `hashlib`, `json`, `posixpath`, `stat` and the package's own modules. The fix is one
list entry in a file outside this lane's boundary (F-5, FOLLOW-UP).

## 8. Evidence audit of the builder's report (spot checks, reproduced)

- **C4.** `git diff --stat fdac751 HEAD -- tests/fixtures/decisions/` empty; golden-digest lines changed in
  `tests/test_decisions_canonical.py` since fdac751: 0; `-k "golden_digests_exact or relanding_stable"`: `2 passed,
  134 deselected in 0.05s`. HOLDS.
- **C5.** The 41 ids of `test_verifier_r3_shape_frees_no_value`, compared by me with the R3 verifier's own case files
  (`/tmp/vj113r3/n_cases.json`, `item4_cases.json`, 40 cases, `raw_state.msg = "set " + raw + " now"`): 39 equal character
  for character, 0 mismatched; the one left out is `R3-floor7` (`sk-ghjlmqfuPASSWORD= XZVXZVX`, a 7-character value), which
  that verifier filed as KNOWN by design (its F-10) and which rule 6 keeps (the 8-character floor): a no-value-byte test for
  it would contradict the frozen floor. `item5-example` and `stub` come from its section 5 and the redesign brief. The
  D-059 residue `R3-pad` (`NAME==v`) is in the set and is now hidden. HOLDS.
- **"Every input row kept; no assertion weakened."** Collected ids of the two edited test files at fdac751 (177) are ALL
  present at HEAD (229; the 52 new ids = the 41 + 11 C5 shapes); the diff fdac751..HEAD of both files removes no `assert`,
  `skip`, `xfail` or `pytest.mark` line (every such line in the diff is an addition). HOLDS.
- **Line counts of the landing commit 132b80e**: volatile.py 205/129, canonical 227/78, ledger 69/4, property file 762 new,
  as the report says. The commit touches exactly the four files, the report, one decision-log row and one ledger line.
- **The property file's 39 tests** (the report's count): `39 passed` in my blocked run above. HOLDS.

## 9. Item 5: C6 against my own adversarial inputs

**A quadratic term in the "linear" detection (F-9).** `_matches` builds the argument `text[start:end]` for
`_cut_placeholder` on EVERY accepted envval or widened head (volatile.py:377-378), before `_cut_placeholder` looks at
`end == len(text)`. In dense text every such value runs to the end of the text (`\S+` and the widened class take `KEY=`
itself), so the copies total about n^2/4 characters. Measured as CPU time of the process (best of 2; the box's load
average was 5-10 from other lanes, which CPU time mostly screens out), against a SCRATCH copy that differs only in that
line (`end == len(text) and end - start < 18 and _cut_placeholder(...)`: a value longer than the longest placeholder, 18
characters, can never be a proper prefix of one) and gives byte-identical output on every input below:
```
shape          chars    tree (CPU)            no-slice scratch copy
KEY= heads      50000     117.0 ms              71.0 ms
               100000     270.4 ms  x2.3       141.9 ms  x2.0
               200000     713.6 ms  x2.6       310.4 ms  x2.2
               400000    1962.5 ms  x2.8       627.8 ms  x2.0
API_KEY= heads  50000      99.6 ms              55.4 ms
               100000     264.4 ms  x2.7       110.7 ms  x2.0
               200000     616.1 ms  x2.3       229.7 ms  x2.1
               400000    1889.9 ms  x3.1       517.0 ms  x2.3
(an earlier run: KEY= 400000 -> 2091.3 ms CPU, over 2 s)
```
cProfile at 200,000 characters (`KEY=` x 50,000): 2 closure rounds; 100,000 heads; `_matches` 0.593 s own time;
`_cut_placeholder` called 99,997 times. Reading of C6: the frozen text sets the scale by its examples (20,000
characters; the builder's D-I adds 100,000, accepted by D-073); at that scale the worst cases stay far under 2 s (0.27 s
at 100,000). The term only reaches 2 s near 400,000 characters, 20 times the contract's scale; without a size, "under
2 s" could not be measured for any algorithm. The report's "linear" (D-C) is true of the head scan and false of the
whole detection. FOLLOW-UP, one-line fix (check the length before slicing).

**My worst shapes at the contract's scale** (`/tmp/vj11r4/c6.py 2 20000,100000`, `_redact_str` directly and through
`decision_state`; CPU time, best of 2, wall time beside it; 14:4xZ):
```
shape                                 20k cpu (wall)        100k cpu (wall)        x (5x size)
API_KEY= heads (builder's)            33.6 ms (33.9)        249.4 ms (261.6)       7.4
KEY= heads                            38.9 ms (38.9)        267.9 ms (274.2)       6.9
PASSWD=KEY= heads                     29.3 ms (29.7)        208.0 ms (213.4)       7.1
KEY:= (widened + NAME= at once)       18.6 ms (18.6)        124.4 ms (125.8)       6.7
envval through bearer, quotes         24.4 ms (24.4)         73.6 ms (73.6)        3.0
wide through envval through bearer    12.6 ms (12.6)         66.1 ms (66.1)        5.3
alternating classes glued              6.8 ms (6.8)          34.9 ms (34.9)        5.2
held placeholders + tails              9.4 ms (9.4)          53.2 ms (53.2)        5.7
cut prefixes (KEY=<redacted:s)        16.9 ms (16.9)         90.8 ms (90.9)        5.4
BEGIN lines inside values             12.8 ms (12.8)         66.1 ms (66.1)        5.2
token heads, runs of 31                7.1 ms (7.1)          37.2 ms (37.2)        5.2
one long value, heads inside          39.3 ms (39.3)        224.3 ms (224.6)       5.7
decision_state KEY= heads, file field 53.6 ms              305.0 ms
decision_state KEY= heads, msg field  38.4 ms              274.9 ms
nested list/dict depth 800 via str(): 25,618 chars, decision_state 16.0 ms
points at or over 2 s: none
```
The dense-head shapes grow 6.7-7.4x for 5x the size (linear: 5x): the same slice term. Closure rounds stay at most 3
on every input I built or generated (section 7), so the loop adds a bounded factor. Past the recursion limit (depth
5,000) `str()` inside `normalize` raises `RecursionError` at all three versions and `make_row` wraps it as
`decision-row-invalid` (F-16).

## 10. Item 7: my own mutants (scratch copies only; 14 of my design, none of the builder's 22)

Harness `/tmp/vj11r4/mutants.py`: per mutant a copy of `src/agent_factory`, the three J1 redaction test files, their
fixtures and `pyproject.toml` under `/tmp/vj11r4/mut/<name>/`; each edit is one exact string replacement asserted to occur
once; a `conftest.py` in the copy asserts the imported `volatile.py` is the copy's own. The pristine copy's `volatile.py`
blob is fe48dd32 (the tree's) and its test files are the tree's byte for byte (the property file differs only in `ROOT`,
pointed at the tree for `git show` of the references). The tree was never edited.
```
mutant (what it breaks)                                   3 J1 files: result            named killer, re-run alone: mutant RED / pristine GREEN
PRISTINE (no edit)                                        268 passed in 66.89s          --
VM01 union merges TOUCHING spans (start <= end)           1 failed, 267 passed          test_a_held_placeholder_keeps_its_class_and_bytes[<redacted:sk><redacted:bearer>]
VM02 _HELD without privkey                                9 failed, 259 passed          test_token_run_keeps_the_token_placeholder_and_no_placeholder_is_relabelled
VM03 bearer floor 16 -> 17                                28 failed, 240 passed         test_v1_class_beyond_the_driver[no-value]
VM04 envval not in _THROUGH (NAME= never runs through)    6 failed, 262 passed          test_a_cut_placeholder_at_the_end_is_no_span[KEY=]
VM05 closure: the `meets` clause dropped (if ok only)     3 failed, 265 passed          test_a_value_runs_through_a_span_it_meets[under-the-floor-into-a-span]
VM06 merged class = LOWEST rank in the group              15 failed, 253 passed         test_r4_env_check_reads_the_value_after_the_bearer_merge[widened-bearer-padding]
VM07 token separator loses its one-space alternative      21 failed, 247 passed         test_token_assignment_forms_redacted
VM08 bearer padding `=*` -> `=?`                          3 failed, 265 passed          test_v1_class_beyond_the_driver[padding]
VM09 cut-placeholder guard applies anywhere, not at end   1 failed, 267 passed          test_the_linear_detection_equals_every_form_matched_at_every_start
VM10 key block END found with bisect_right                1 failed, 267 passed          test_the_linear_detection_equals_every_form_matched_at_every_start
VM11 closure stops after ONE round                        268 passed  (SURVIVES)        none: EQUIVALENT (below)
VM12 name set without PASSWD (leak mutant)                13 failed, 255 passed         test_env_assignment_forms_redacted_and_prose_kept
VM13 _stops drops every gap stop (crash mutant)           174 failed, 94 passed         test_secret_redacted_every_class  (mechanism: IndexError, confirmed)
VM13b _stops: no stop after a region inside a gap         268 passed  (SURVIVES)        none: NOT equivalent (below) -> F-7
```
Every killer above was re-run alone against its mutant (`1 failed`) and against the pristine copy (`1 passed`).

**VM11 is an equivalent mutant (F-8, INFO).** Output of the tree vs VM11: 0 differences over 120,004 texts (the builder's
generator seed 4242 and mine, plus the builder's own round-2 case, seed 198 input 638) and 0 over 533,275 differentially
fuzzed candidates. Mechanism (argued from the code, `_spans`): a NAME= value stops only at whitespace outside regions and
only fixed spans (bearer, key block) cover whitespace, so NAME= ends are final after round 1; a widened value that grows
in round 2 does so only through a NAME= span grown in round 1, and stops at that span's end (whitespace), which the union
already covers; a later `meets` flip adds a span inside the union. So the rounds after the first (the builder measured up
to 3) add spans but never output. Not a test gap; the fixed-point loop is dead weight for output (and extra cost).

**VM13b survives and is NOT equivalent (F-7, FOLLOW-UP).** It over-masks: when a span ends inside a delimiter gap of the
widened class (`" `), the positions after it are no stop, so the widened value runs on over the next word.
```
'key: aKEY=b" rest more'       tree 'key: <redacted:envval> rest more'     VM13b 'key: <redacted:envval> more'
'password: xKEY=a" tail more'  tree 'password: <redacted:envval> tail more' VM13b 'password: <redacted:envval> more'
"key: aPASSWD=b' next word"    tree "key: <redacted:envval> next word"      VM13b "key: <redacted:envval> word"
both references keep the word in all three; VM13b changes the output on 2,186 of 20,000 generated texts (10.9%)
```
No test pins where a value that runs through a span stops after it (rule 5 read after the replacement, D-A): the C1, C2
and C3 oracles cannot see over-masking, and the equivalence test covers `_matches`, not the closure. The tree's behaviour
is right; the gate would not notice it becoming wrong in the over-masking direction. Fix: one named row such as
`'key: aKEY=b" rest more' -> 'key: <redacted:envval> rest more'` in `test_a_value_runs_through_a_span_it_meets`.

**Fuzzing the tree** (`/tmp/vj11r4/fuzz_c3.py`; piece-level mutation of seed shapes; per candidate the exact C1 check,
redact's fixed point, and the fixed point after a cut at each limit 20/40/80/120/200/400):
```
seed 11        77,351 candidates in 60 s    hits: none
seed 20260925 179,541 candidates in 140 s   hits: none
seed 777      156,399 candidates in 140 s   hits: none   (re-run after the 14:49Z worker restart killed the first attempt)
negative control: the same fuzzer on VM05's copy -> HIT C3a within 40 s, minimized to 'key=XBearer babababababababa'
```

## 7. My own generator and sweep, through the real path (items 2a, 3, and A-1's incidence)

`/tmp/vj11r4/vgen.py` (mine; it imports no generator or oracle of the builder's): per input ONE closed state with fake
secrets planted in EVERY text field at once, `paths` with 1-4 items, Unicode whitespace inside values and heads (NBSP, EM
SPACE, IDEOGRAPHIC SPACE, NEL, OGHAM, THIN SPACE, tabs, newlines), zero-width breaks, U+212A/U+017F/U+0130/U+0131 in names,
NFC-mapped characters (U+037E, U+1FEF, U+212A, decomposed e+acute and A+ring, U+2126), full, cut and fake placeholders,
values holding `<` and `>`, dict/list/bytes field values (`str()` by normalize), dict-shaped assignments, list-wrapped
values, homoglyph and fullwidth names, glued chains of 2-4 assignments, and 25% of bounded fields padded so the last head
straddles the limit. Every state goes through `make_row -> append -> the line on disk -> replay` (3 processes).
```
                                              seed 777001 (908.5 s)      seed 777002 (718.9 s)
inputs                                        100000                     100000
C1x: fields checked by the EXACT oracle       316879, failures 0         316885, failures 0
C1s: a covered core's window in a sink        0                          1 -> oracle false positive (below)
C2 d556c9b hidden by its redactor (cores)     1425047                    1431000
C2 fdac751 hidden by its redactor (cores)     1443196                    1449394
C2 newly visible at the redactor level        0 / 0                      0 / 0
C2 newly visible via decision_state           cut shift only, all cov=False (by MY forms): 1310 / 1278 and 1303 / 1269
C3 decision_state not a fixed point           891, all pure `paths` reorders (A-1)   834, all pure `paths` reorders
   the references' own A-1 count              887 / 887                  832 / 832
ledger rows written / refused                 99062 / 891 (state-not-canonical)   99125 / 834
normalize refused (generator artifact)        47 (decision-state-abs-path)        41
cores covered by my forms / not covered       1544876 / 187088           1551541 / 187188
cores covered though planted as near-miss     53615                      53609   (checked as covered: the independent label)
closure rounds (calls of _regions per field)  {1: 163945, 2: 137238, 3: 15696}   {1: 163215, 2: 137966, 3: 15704}
```
- **Several secrets in one state (2a):** every state carries 2-4 planted fields at once; 0 leaks, 0 C3 misses other
  than A-1. Multi-field states behave as independent fields (each field is redacted on its own; no cross-field path).
- **The one C1s hit on seed 777002 (input 64342) is my oracle's, not a leak:** the matched window `N=<r` sits in another
  field (`row_id` = `flask-TOKEN=<redacted:envval> order`), spelled by a KEPT `TOKEN=` followed by a placeholder; the core
  itself (`action_excerpt`, `...client_keY =:>AErſN=<r_449...`) is hidden whole (`client_keY =<redacted:envval>`), and
  the exact check of that field is True.
- **A-1's incidence:** the new code misses its fixed point on 891 and 834 states against 887/887 and 832/832 at the
  references. The 4 + 2 extra states (seed 777001: 30097, 46148, 46435, 60043; seed 777002: 3784, 51692) are each a
  state where BOTH references leave a covered value visible (a bearer run glued to a key block, e.g. `bearer
  Q8XQQ9RYiEw-----BEGIN ...` -> refs `bearer Q8XQQ9RYiEw<redacted:privkey>`) and the new code hides it; the new
  placeholder moves the item in the sort order and `make_row` refuses the row (where the references would write one
  carrying the value).
- **My oracle's residue (F-18, INFO):** 75 and 79 cores had a window that also occurs in the line's fixed non-state text
  (row keys and constants I did not exclude); a detector of oracle misses, not a sink check (the state sinks are separate).

## 11. Stale context and small static observations

- Four test names still describe the deleted machinery (full references in section 18):
  tests/test_decisions_canonical.py:1300 `test_bearer_merge_step_keeps_every_j1_1_r2_redaction`;
  tests/test_decisions_ledger.py:1712 `test_bearer_merge_step_keeps_every_j1_1_r2_redaction_in_the_file`;
  tests/test_decisions_canonical.py:1282 `test_r4_env_check_reads_the_value_after_the_bearer_merge`;
  tests/test_decisions_ledger.py:1694 `test_r4_value_after_a_bearer_merge_never_reaches_the_ledger_file`. The comment at canonical :1301-1302
  ("the negative controls are mutants (the verifier's FIX-A as written, a step that re-enters the bearer run)") names
  mutants that cannot be built against the new code. The block comments were reworded with a historical frame ("D-070
  removed that guard"); `git grep` of `_yield_pattern|_YIELD|_BEARER_MERGE|_envval_wide|_ENVVAL_WIDE|_SECRET_NAME|
  _BEARER_RUN|_ASSIGNMENT_HEAD|merge step|sequential passes` over src, scripts, tests, harness-ports, wiki, the current
  plan docs, seeds and the instruction files finds only volatile.py:47, whose "it replaces six sequential substitution
  passes" is accurate history (F-12, INFO).
- `volatile.py:91-97` claims "Every start in linear time" and says the old whole-form match "re-reads a long value once
  per head inside it"; line 378 does the same by slicing (F-9).
- The `decision_state` docstring (volatile.py:497-504) names one idempotence exception (J1-1-R1 D-2); A-1 and the NFC
  class (F-6) are two more (F-12).
- `python -m pyflakes` over the four boundary files: rc 0.

## 12. Finding inventory (no severity filter)

Evidence level: VERIFIED = reproduced by me in this session through the stated command; STATIC = read from source only.
Canonical path = `decision_state` / `make_row -> append -> the line on disk -> replay` at the PIN blobs.

| id | class | finding | evidence | contract mapping | canonical path | material effect | reproduction | suggested fix |
|---|---|---|---|---|---|---|---|---|
| F-1 | INFO | The builder's C1/C2/C3 sweep reproduces on two seeds of mine (424242, 31337; 100,000 each): C1 0, C3 0, C2 0 against both references at the redactor level and through decision_state (cut shift only, all near-miss) | VERIFIED | C1, C2, C3 | yes | none (confirms) | `python /tmp/vj11r4/sweep_builder.py <seed> 100000 <dir>` | none |
| F-2 | INFO | My independent generator and position-EXACT oracle: 0 kept covered positions over 633,764 field texts (two seeds), 0 real sink leaks, 0 C2 regressions, C3 misses only A-1; multi-field states, Unicode whitespace, case folds, placeholder spellings, dict/list values, limit-straddling heads all included | VERIFIED | C1, C2, C3 | yes (every state through the ledger) | none (confirms) | `python /tmp/vj11r4/vgen.py <seed> 100000 3` | none |
| F-3 | INFO | Real corpus: `decide-harvest` over all 277 committed sources gives 298 rows byte-identical at the new code and both references; the J2 sample's 100 row digests are all present; no consumer (`decide-harvest`, `v1_probe.py`) loses a field it reads | VERIFIED | item 4 | yes | none | section 5 (scratch harvest copies under `/tmp/vj11r4/hv/`) | none |
| F-4 | FOLLOW-UP | A-1: `normalize` sorts `paths` before `redact`; a redaction that reorders items breaks the fixed point and `make_row` refuses the row. Identical at both references; my sweeps: 891/834 (new) vs 887/832 (each reference); the extra 4+2 are states where the references show a covered value and the new code hides it | VERIFIED | C3 as amended: D-073 accepts D-F (one-item lists) and names A-1 adjacent | yes | a refused row (fail closed, loud); no leak | section 6 probe; section 7 | sort list fields after redact (or re-sort in `redact`), then extend the generator to multi-item lists |
| F-5 | FOLLOW-UP | A-2: `J1_TESTS` omits the property file, so the model-blocked run never executes it; under the same blocker it passes (39 passed, 0 attempts) | VERIFIED | C7 (both frozen clauses hold) | n/a (test harness) | none today; no guard against a later model import there | section 6 | add the file to `J1_TESTS` (a file outside this lane's boundary) |
| F-6 | FOLLOW-UP | NFC re-composition: `>` + U+0338 composes to U+226F, so a U+0338 kept right after an sk, bearer or key-block placeholder makes `decision_state` miss its fixed point; `make_row` refuses. Identical at both references; no secret byte involved | VERIFIED | C3 in spirit (the contract's generator never draws combining marks); the docstring's idempotence claim | yes (make_row refuses) | a refused row (fail closed); no leak | section 4 probe | let the span take the combining marks that follow it, or apply NFC to redact's output before `bound`, and pin it with a named row |
| F-7 | FOLLOW-UP | Mutant VM13b (no stop after a span inside a delimiter gap) SURVIVES all 268 tests and is not equivalent: it hides the next word in 2,186 of 20,000 generated texts (`key: aKEY=b" rest more` -> `... more`); no test pins where a value that runs through a span stops | VERIFIED | none frozen (C1-C7 do not forbid over-masking; D-A accepts more masking) | scratch mutant | none today (the tree is right); the gate is blind to over-masking | section 10 | named row `'key: aKEY=b" rest more' -> 'key: <redacted:envval> rest more'` in `test_a_value_runs_through_a_span_it_meets` |
| F-8 | INFO | VM11 (closure stops after one round) is EQUIVALENT: 0 output differences over 653,279 texts; the rounds after the first add spans already inside the union | VERIFIED + argued | none | scratch mutant | extra cost only | section 10 | optional: one round, with the argument written down |
| F-9 | FOLLOW-UP | `_matches` slices `text[start:end]` for every accepted NAME=/widened head before `_cut_placeholder` checks `end == len(text)`: about n^2/4 copied characters on dense heads; 1.96-2.09 s CPU at 400,000 characters; linear (0.63 s) with the slice avoided on a scratch copy with identical output. Contract scale fine (0.27 s at 100,000). The "linear" claims (D-C; volatile.py:91-97) overstate it | VERIFIED | C6 (holds at the frozen 20,000 and D-I's 100,000 scale) | yes (`redact`, `decision_state`) | cost only, and only far above the contract's scale | section 9 | `end == len(text) and end - start < 18 and ...` (no slice for a value longer than any placeholder); fix the comment |
| F-10 | INFO | The builder's generator emits an input `normalize` refuses (seed 31337 input 84384, `p/../`); its sweep asserts `not refused`, so a seed change could turn it red for a non-redaction reason. The fixed seeds keep the gate deterministic | VERIFIED | none | test harness | none today | section 1 | have the generator avoid `/../` in path fields |
| F-11 | INFO | Pre-existing form gaps, visible at all three versions (no form covers them): list-wrapped values (`{'password': ['...']}`, `['API_KEY', '=', '...']`), fullwidth `ＫＥＹ=`, Cyrillic `kеy:`, `ﬆecret:`, a BOM or zero-width break inside a name or run, whitespace-split values under the floor, a run after a held placeholder | VERIFIED | none (not covered by any frozen form) | yes | these values stay visible, as before | section 3, 4 probes | a future form review (e.g. a JSON array after a secret name) |
| F-12 | INFO | Stale names and claims: four test names and one comment describe the deleted merge step; the `decision_state` docstring names one idempotence exception of three | VERIFIED (read) | none | n/a | none | section 11 | rename the tests; list A-1 and F-6 in the docstring |
| F-13 | INFO | Case folds are a closed set: exactly U+0130, U+0131, U+017F, U+212A reach the case-blind classes in this `re`; NFC maps U+212A, U+037E and U+1FEF into ASCII, identically in all three versions | VERIFIED | C1 (item 2c) | n/a (enumeration) | none | section 3 | none |
| F-14 | INFO | Over-masking (D-A): names glued after a span holding whitespace, a quote, `&`, `,` or `;` are hidden (13.7% / 17.5% of dense synthetic texts lose a name vs d556c9b / fdac751); in the sampled cases the hidden name is collateral of hiding a value the reference shows; labels differ for a held placeholder with a tail (`<redacted:sk>` vs the references' `<redacted:envval>`) | VERIFIED | item 4; D-A accepts it | yes | less text kept; 0 of 298 real rows affected | section 5 | none required |
| F-15 | INFO | C4 (goldens unchanged, 2 passed), C5 (39 of the R3 verifier's 40 shapes char for char + item5 + stub; `R3-floor7` rightly left out), C7 (imports), the premise (339 passed, twice) and "no row deleted, no assertion weakened" all HOLD | VERIFIED | C4, C5, C7 | yes | none | sections 0, 6, 8 | none |
| F-16 | INFO | A field value nested past the recursion limit makes `normalize`'s `str()` raise `RecursionError` (not `DecisionStateError`) at all three versions; `make_row` wraps it as `decision-row-invalid` | VERIFIED | none (normalize, outside the redaction pass) | yes | a refused row | section 9 | optional: refuse non-string field values by name |
| F-17 | INFO | C6 at the contract's scale: my 12 adversarial shapes at 20,000 and 100,000 characters, and through `decision_state`, all far under 2 s (max 305 ms) | VERIFIED | C6 | yes | none | section 9 | none |
| F-18 | INFO | My own oracle's residue: 75/79 cores per seed had a window in the line's fixed text (row keys I did not exclude); one boundary false positive (input 64342) diagnosed by mechanism; three first-draft oracle defects fixed before any number | VERIFIED | none | n/a | none (oracle quality, disclosed) | section 2, 7 | none |

## 13. The blocking predicate, applied

No finding meets all five conditions:
- F-4 (A-1) and F-6 (NFC): reproduced through the real path with a discriminator, but pre-existing and identical at both
  references (no regression), fail closed (a loud refusal, counted by `decide-harvest`, never a silent loss or a leak),
  and outside the frozen contract's reach (D-073 accepted D-F and named A-1 adjacent; the contract's generator draws no
  combining marks). Not CONTRACT-DEFECT: no evidence is falsified, no state corrupted, nothing lost silently.
- F-7 (VM13b): a gate gap, not a code defect; the frozen contract does not forbid over-masking (D-A accepts it) and the
  tree's behaviour is right. Condition 1 and 3 fail.
- F-9 (the slice): C6's measurable part holds at the contract's scale (20,000; D-I's 100,000); the term reaches 2 s only
  near 400,000 characters. Conditions 1 and 3 fail at the frozen scale.
- F-5: C7's frozen clauses hold; the fix lies outside the boundary (condition 5 fails).
- Every other finding is INFO.

## 14. Reproduced, reviewed statically, skipped

- **Reproduced (commands run this session):** the premise (blobs; 339 passed twice, 13:53Z and 14:58Z); the builder's
  sweep on seeds 424242 and 31337; my own sweep on 777001 and 777002; the exact-oracle negative control; the 46 hand
  probes; the 8,819-case limit grid; the case-fold enumeration; the three-version harvest over 277 sources; the J2
  digest check; the name-hiding layouts; A-1 at three versions and through `make_row`; A-2 under the blocker; the NFC
  class at three versions; C4/C5/C7; the id and assertion diff of the two edited test files; the landing commit's counts;
  C6 (slice scaling, profile, 12 shapes); 14 mutants plus each killer alone; the VM11 differential; 413,291 fuzzed
  candidates on three seeds plus the VM05 negative control; the served-model count.
- **Reviewed statically:** the design against the redesign brief (rules 1-6), `_spans`/`_stops`/`_regions` for edge
  cases (argued in F-8), the consumers' field reads, the stale comments and names, pyflakes.
- **Skipped, and why:** the builder's own 22 mutants (their evidence; my 14 target what they do not); CI and the PC
  suite (no bridge use is allowed on this lane); `lint_delta` and `detect-changes` (builder gates on an already
  committed change; pyflakes run instead); a proof that no C1 leak exists for ALL inputs (the exact oracle over 633,764
  generated fields and 413,291 fuzzed texts is evidence, not proof).

## 15. NOT done

No commit, push, PR, comment or bridge call. No file in the tree was edited except this report (untracked). Mutants lived
only under `/tmp/vj11r4/mut/`. The worker restart at about 14:49Z killed one foreground fuzz run (seed 777), which I
re-ran; the background sweep (seed 777002) survived and completed; all scratch state I relied on after the restart was
re-verified (reference blobs 20ebcd54f3ed and 2d5cf0072469, the pristine mutant copy equal to the tree, the harvest
copies' blobs), and the four boundary blobs were re-checked at 14:51Z (unchanged; HEAD ee44b41 after a push rewrote the
commit ids: the brief's commit is now ece8dd1, and no commit since the PIN touches the boundary).

## 16. Served model

This lane's transcript (`/root/.claude/projects/-home-user/bdab799a-.../subagents/agent-a54062a49c9da2bf0.jsonl`),
counted per ASSISTANT record at 14:56Z: 337 of 337 on `claude-opus-5-5`; stop reasons `tool_use` 154, none 183; no
`refusal` stop.

## 17. GATE RECOMMENDATION: MERGE-READY-WITH-FOLLOWUPS

No finding satisfies the complete blocking predicate. C1 (0 leaks at every sink on four 100,000-input seeds, two
generators, a position-exact oracle), C2 (0 regressions against d556c9b and fdac751), C3 (0 misses outside A-1), C4, C5,
C6 at the contract's scale and C7 all reproduce. The follow-ups, none blocking: F-4 (A-1), F-5 (A-2), F-6 (NFC after a
placeholder), F-7 (a gate gap for over-masking, mutant VM13b), F-9 (the slice's quadratic term and the "linear" claim).
The recommendation depends on nothing I did not reproduce; the coordinator owns the final gate decision.

## 18. Line references (at the PIN blobs; `scripts/report_lint.py` checks them)

- src/agent_factory/decisions/volatile.py:91 `finditer` (the "Every start in linear time" comment, F-9)
- src/agent_factory/decisions/volatile.py:116 `_HELD` (VM02)
- src/agent_factory/decisions/volatile.py:121 `_THROUGH` (VM04)
- src/agent_factory/decisions/volatile.py:199 `_path` (normalize maps each list item, A-1)
- src/agent_factory/decisions/volatile.py:200 `sorted` (the sort BEFORE redact, A-1)
- src/agent_factory/decisions/volatile.py:341 `_redact_str` (redact maps list items, no re-sort, A-1)
- src/agent_factory/decisions/volatile.py:354 `PLACEHOLDERS` (the cut-placeholder guard, VM09)
- src/agent_factory/decisions/volatile.py:366 `bisect_left` (the key block's END search, VM10)
- src/agent_factory/decisions/volatile.py:378 `_cut_placeholder` (the slice, F-9)
- src/agent_factory/decisions/volatile.py:399 `_stops` (VM13, VM13b)
- src/agent_factory/decisions/volatile.py:422 `stops` (the stop kept after a region inside a gap: VM13b drops it, F-7)
- src/agent_factory/decisions/volatile.py:426 `_spans` (the closure, F-8)
- src/agent_factory/decisions/volatile.py:453 `meets` (VM05)
- src/agent_factory/decisions/volatile.py:456 `grown` (the fixed-point loop, VM11 / F-8)
- src/agent_factory/decisions/volatile.py:497 `decision_state` (its idempotence docstring, F-12)
- src/agent_factory/decisions/ledger.py:273 `restate` (the fixed-point check that refuses A-1 and F-6 rows)
- src/agent_factory/decisions/ledger.py:404 `raw_state` (make_row's call of decision_state)
- tests/test_decisions_no_model.py:25 `J1_TESTS` (A-2)
- tests/test_decisions_redaction_properties.py:456 `test_c1_c2_c3_canary_sweep` (the builder's sweep, item 1)
- tests/test_decisions_redaction_properties.py:641 `test_a_value_runs_through_a_span_it_meets` (F-7's suggested row)
- tests/test_decisions_redaction_properties.py:689 `test_the_linear_detection_equals_every_form_matched_at_every_start`
- scripts/decide-harvest:877 `make_row` (the harvest's only row path, item 4)
- docs/research/findings/j2-v1-probe/v1_probe.py:59 `MASK` (the J2 probe reads the state's title, item 4)

`python3 scripts/report_lint.py --min-refs 15` on this report (round 2 of 3, 15:0xZ): `report_lint: 27 refs — OK 27, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`, rc 0.
