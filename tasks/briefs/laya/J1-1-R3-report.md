# J1-1-R3 report — lane j1-1-r3 (task #202; D-059; the THIRD focused repair)

STATUS: COMPLETE, 2026-09-24. The diff is UNSTAGED in `/tmp/j113s/wt` (nothing staged, committed or pushed).
OUTCOME:
- MET: C1 (R-1, R-2 and R-4 close), C2 (R-3's `NAME= v` closes; `NAME==v` declared), C3 (V-M3, V-M11 and V-M4 killed; also V-M6
  and V-M10), C5 (invariants, goldens, idempotence, linear cost), C6 (comments true).
- C4: MET against d556c9b (0 newly visible BODY inputs in 6 x 20,000; grid `new_leak: 0`). **NOT MET against fb016d0**:
  20/13/20 and 238/261/257 inputs. Every exposure is attributed to R-1/R-2/R-4/R-3, and each exposed byte is visible at
  d556c9b too. A guard-level change cannot meet it together with C1 (DISCREPANCY D-1, section 9). Read D-1, D-2 and D-3 first.
- Tests: 121 -> 177 passed, twice, set 16a7b628685e. Mutation audit: 58 of 58 killed.

Venue: the SANDBOX, in a private `git clone --shared` at `/tmp/j113s/wt`, detached at ff7a671 (the coordinator's sandbox
continuation of `tasks/briefs/pc/pc-j1-1-r3.md`; the PC run on the local route edited nothing). Scratch: `/tmp/j113s/`.
Brief: `tasks/briefs/laya/J1-1-R3-brief.md` (governs). Boundary: `src/agent_factory/decisions/volatile.py`,
`tests/test_decisions_canonical.py`, `tests/test_decisions_ledger.py`, this report.

## 0. Premise — re-measured (2026-09-24T03:04Z, /tmp/j113s/wt@ff7a671)

```
$ git rev-parse HEAD
ff7a671ef7de584e4b16923e16b560c0f994167f
$ (blob ids of the boundary at each reference)
d556c9b 20ebcd54f3ed src/agent_factory/decisions/volatile.py
fb016d0 bf04415d72c1 src/agent_factory/decisions/volatile.py
0e60603 bf04415d72c1 src/agent_factory/decisions/volatile.py
feb26d7 bf04415d72c1 src/agent_factory/decisions/volatile.py
ff7a671 bf04415d72c1 src/agent_factory/decisions/volatile.py
d556c9b 0afbf1b821ed tests/test_decisions_canonical.py
fb016d0/0e60603/feb26d7/ff7a671 440ac2426d8f tests/test_decisions_canonical.py
d556c9b 4a8bccead05f tests/test_decisions_ledger.py
fb016d0/0e60603/feb26d7/ff7a671 6648679bd40a tests/test_decisions_ledger.py
worktree = ff7a671 for all three (bf04415d72c1 395 lines, 440ac2426d8f 1060, 6648679bd40a 1612)
$ (the 30 lane-patch verifier files vs /tmp/vj11r2, sha256 each)
files=30 diff=0
a97a7add8084 repro.py · cba34afa49ae fixa/volatile.py · 5da6e5ead1cb fixb/volatile.py   (= the PC brief's premise prefixes)
$ PYTHONPATH=/tmp/j113s/wt/src python -c 'import agent_factory.decisions.volatile as v; print(v.__file__)'
/tmp/j113s/wt/src/agent_factory/decisions/volatile.py
$ PYTHONPATH=/tmp/j113s/wt/src python tasks/briefs/laya/j1-1-r3-support/vj11r2/repro.py src   (2026-09-24T03:04:11Z, the PIN)
R-1 body-in-ledger-line=True  state.msg='Authorization: Bearer QZJ8QZJ8ıQZJ8QZJ8QZJ8QZJ8QZJ8'
R-2 body-in-ledger-line=True  state.msg='<redacted:sk>token <redacted:token>: X4Z9X4Z9X4Z9'
R-4 body-in-ledger-line=True  state.msg='ta<redacted:sk>password:<redacted:envval> X4Z9X4Z9X4'
R-3 body-in-ledger-line=True  state.msg='ta<redacted:sk>= QZJ8QZJ8QZJ8QZJ8QZJ8'
replayed rows: 4
$ python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py -q -p no:cacheprovider --basetemp=/tmp/j113s/bt/pin0 | tail -1   (2026-09-24T03:04:18Z)
121 passed in 3.62s
$ python -m pytest tests/test_decide_harvest.py -q -p no:cacheprovider --basetemp=/tmp/j113s/bt/pinh | tail -1
33 passed in 8.34s
$ bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py
2 files set=16a7b628685e
$ bash scripts/pc_suite.sh set-id -- tests/test_decide_harvest.py
1 files set=87e28761f102
```
Verdict: the premise holds. The four leaks reproduce at the PIN; the counts and set ids equal the briefs'.
The editable install is a plain `.pth` entry (`/home/user/agent-factory/src`), so pytest's `pythonpath = ["src"]` and an explicit
`PYTHONPATH=<copy>/src` both put the copy's own src first (checked again by every mutant's red below).

## 1. Design — measured before any test was written (scratch copies only)

### 1a. FIX-A as written fails C4 against fb016d0 (a DISCREPANCY driver; see section 9)
C4 says "Every value that d556c9b OR fb016d0 redacts stays redacted". The verifier measured FIX-A/FIX-B against d556c9b only
(its section 10: "differential vs the PIN"). Against fb016d0, FIX-A's R-4 line (`_ASSIGNMENT_HEAD` gains `|(?i:bearer)\s`) refuses a
yield wherever a value runs into the word `bearer`. That includes a bearer that never matches (a run under 16) and a merge after
which no head follows. fb016d0 hid the first value in those shapes, and FIX-A shows it again. Measured on the fixed module files
(`/tmp/j113s/v/explore1.py`; `d556`/`fb01` = the two references, `fixa`/`fixb` = the verifier's files, sha prefixes cba34afa49ae /
5da6e5ead1cb):
```
glue-nohead 'task-password:QZJ8QZJ8bearer abcdefghijklmnop rest'
   d556: V1vis=True   'ta<redacted:sk>:QZJ8QZJ8<redacted:bearer> rest'
   fb01: V1vis=False  'ta<redacted:sk>password:<redacted:envval> rest'
   fixa: V1vis=True   'ta<redacted:sk>:QZJ8QZJ8<redacted:bearer> rest'
   fixb: V1vis=True   'ta<redacted:sk>:QZJ8QZJ8<redacted:bearer> rest'
R4-a 'task-password:QZJ8QZJ8bearer abcdefghijklmnop==token: X4Z9X4Z9X4'
   d556: V1vis=True  V2vis=False  'ta<redacted:sk>:QZJ8QZJ8<redacted:bearer>token: <redacted:envval>'
   fb01: V1vis=False V2vis=True   'ta<redacted:sk>password:<redacted:envval> X4Z9X4Z9X4'
   fixa: V1vis=True  V2vis=False  (= d556)
R2-a 'sk-abcdefgh-token QZJ8…(32)ıpassword: X4Z9X4Z9X4Z9'
   d556: RUNvis=True  V2vis=False ;  fb01: RUNvis=False V2vis=True ;  fixa: RUNvis=True V2vis=False (= d556)
```
Two kinds of exposure against fb016d0 follow:
- **trade**: the input is a true chain (the merged value, or the token run, swallows a second head). d556c9b hides V2 and shows
  V1 (or the run). fb016d0 hides V1 and frees V2 (the regressions R-2/R-4). C1 requires V2 hidden. Under any guard, the only two
  outputs are "yield" (fb016d0's) and "no yield" (the PIN form), so the guard cannot hide both. The existing tests pin the PIN form
  for chains (`tests/test_decisions_canonical.py@ff7a671:911-919`, the `chain-widened` … `chain-token-run` rows), and the chain design
  (`src/agent_factory/decisions/volatile.py@ff7a671:51-54`: "so the run keeps its PIN form") says the run keeps its PIN form when the value holds another head. C1 and "every value fb016d0 redacts" therefore cannot both hold on
  these inputs with a guard-level change. Hiding both would need the value classes to stop at a head or at a bearer placeholder
  (task #198's rule). That is a redesign of the redaction pass, outside D-059's scope.
- **pure**: nothing that fb016d0 showed is newly hidden. Each is an avoidable over-refusal by the guard.

### 1b. Candidates measured (three-way differential, `/tmp/j113s/v/tri3.py`: the verifier's `diff3.py` generator and both its
instruments, asserted to agree per module; secret roles for "trade" = body/tokchar/special)
```
cand=fixb seed=11 ascii_only=True {'better than both': 3103, 'inputs': 20000, 'vs_f body-newly-visible pure': 69, 'vs_f body-newly-visible trade': 7}
cand=fixb seed=2 ascii_only=False {'better than both': 3912, 'inputs': 20000, 'vs_f body-newly-visible pure': 31, 'vs_f body-newly-visible trade': 249}
cand=k1 seed=11 ascii_only=True {'better than both': 3144, 'inputs': 20000, 'vs_f body-newly-visible pure': 29, 'vs_f body-newly-visible trade': 7}
cand=k1 seed=2 ascii_only=False {'better than both': 3950, 'inputs': 20000, 'vs_f body-newly-visible pure': 6, 'vs_f body-newly-visible trade': 237}
cand=k2 seed=11 ascii_only=True {'better than both': 3161, 'inputs': 20000, 'vs_f body-newly-visible pure': 13, 'vs_f body-newly-visible trade': 7}
cand=k2 seed=2 ascii_only=False {'better than both': 3955, 'inputs': 20000, 'vs_f body-newly-visible pure': 3, 'vs_f body-newly-visible trade': 235}
```
No `vs_d` key appears: no candidate shows a body byte that d556c9b hides. No `UNATTRIBUTED` key appears: every exposure against
fb016d0 is on an input that holds U+0130/U+0131/U+017F or the word `bearer`.
- K1 = FIX-B with the R-4 line as a CROSSING, not a head: the NAME= and widened branch scans step over `(?i:bearer)\s+` when 16
  bearer-run characters follow (a real merge) and keep looking for a head. The token branch gets no bearer step, because
  `_TOKEN`'s run cannot cross `<`.
- K2 = K1, but the step replays the bearer match's own run as the bearer pass runs it: possessive, stopping where it yields to a
  depth-0 `_YIELD`. A head the bearer consumes (its value too short to yield) is then no head.
- K2's remaining "pure" rows are chains that the design's conservative head rule refuses. Either the merged tail holds a head
  whose value is glued (so the merged value would swallow it whole), or a token head (whose run `_TOKEN` has already redacted).
  The same rule refuses the same shapes without a merge, at fb016d0 too (`task-password:abcdefghkey=X4Z9X4Z9`). fb016d0 yielded
  on them only because its guard judged the pre-merge value.
- DECISION: K2. The guard now judges the value its class actually takes after the bearer pass, with the letters read as `_TOKEN`
  and the PIN's bearer run read them. Every difference from fb016d0 traces to R-1, R-2 or R-4 (or FIX-B's R-3 row). The residue
  against fb016d0 is reported as a DISCREPANCY (section 9), never hidden.
- FINAL FORM = K2 with the step's `=*+` padding removed. Both scan classes already take `=`, and no head starts at `=`, so it
  was an equivalent element; removing it makes every element killable (section 4). Checked equal on the generator
  (`/tmp/j113s/v/same_out.py`, K2 file vs the final file):
```
seed=11 ascii=True inputs=20000 differing_outputs=0
seed=2 ascii=False inputs=20000 differing_outputs=0
seed=12 ascii=True inputs=20000 differing_outputs=0
seed=21 ascii=False inputs=20000 differing_outputs=0
```
  Every number in sections 3-6 was measured on the FINAL file (`volatile.py` blob 2d5cf0072469), not on K2.

## 2. What changed (the clone `/tmp/j113s/wt`, unstaged; blob ids bf04415d72c1 -> 2d5cf0072469, 440ac2426d8f -> 733fe70b705b, 6648679bd40a -> 9900d9648fb8)

`git diff --stat`: `src/agent_factory/decisions/volatile.py | 82 +++++++++----`, `tests/test_decisions_canonical.py | 199 +++++++-`,
`tests/test_decisions_ledger.py | 101 ++++`, `3 files changed, 356 insertions(+), 26 deletions(-)`.

`src/agent_factory/decisions/volatile.py`, the reason per changed line (final line numbers):
| lines | change | reason (contract) |
|---|---|---|
| `src/agent_factory/decisions/volatile.py:5-6` | docstring: "AMENDMENT 3, D-059 -- their yield guard" | C6 (the module header lists the amendments) |
| `src/agent_factory/decisions/volatile.py:46-63` | the comment "sk and bearer (AMENDMENT 2, D-057, VERIFY-J1-1-R1 V-1; AMENDMENT 3, D-059," rewritten | C6: the verifier's falsified `:45-46` (R-1) and `:52-54` (R-2, R-4) statements, now true: the PIN's case-blind bearer run; "That value" is the text its class takes after the passes before it |
| `src/agent_factory/decisions/volatile.py:70` | `_BEARER_RUN = r"(?i:[A-Za-z0-9._~+/-])"` | R-1 (FIX-A line 75): the PIN's case-insensitive run set, one name for the pass and the step |
| `src/agent_factory/decisions/volatile.py:73-88` | `def _yield_pattern` replaces the `_YIELD = (` literal; its comment rewritten | one definition, two depths (the real `_YIELD` and the step's depth-0 yield). C6: the falsified `:64-65` is now "an upper-case NAME= that a non-space follows is _ENVVAL's" |
| `src/agent_factory/decisions/volatile.py:83` | `_ENVVAL_HEAD + r"(?=[^\s=])(?!(?:" + merge` | R-4: the NAME= scan may step over a bearer merge (my improvement of FIX-A line 61; section 1) |
| `src/agent_factory/decisions/volatile.py:84` | `(?!" + _ENVVAL_HEAD + r"\S)` | R-3 / C2 (FIX-B) |
| `src/agent_factory/decisions/volatile.py:85` | `r"(?=[^\s\"'&,;]{8})(?!(?:" + merge` | R-4: the widened scan may step over a bearer merge |
| `src/agent_factory/decisions/volatile.py:87` | `(?=(?i:[A-Za-z0-9+/]){32})` in the check and the scan | R-2 (FIX-A line 72) |
| `src/agent_factory/decisions/volatile.py:91-102` | the comment "A value glued to "bearer", whitespace and 16+ run characters is longer after" | C6 for the new code, including its declared limit (depth 2 keeps the PIN form) |
| `src/agent_factory/decisions/volatile.py:103-106` | `_BEARER_MERGE = (`: `(?i:bearer)\s+`, the 16-run lookahead, the run replayed possessively (`*+`), each character guarded by `_yield_pattern(r"(?!)")` | R-4: the scan reads the value the env classes take after the bearer pass; a head the bearer consumes is no head |
| `src/agent_factory/decisions/volatile.py:107` | `_YIELD = _yield_pattern(_BEARER_MERGE)` | R-4 |
| `src/agent_factory/decisions/volatile.py:108-110` | `_BEARER = re.compile(` with `_BEARER_RUN` in its lookahead and run | R-1 |
Unchanged: `_SECRET_NAME`, `_ASSIGNMENT_HEAD` (`src/agent_factory/decisions/volatile.py:68`, `_ASSIGNMENT_HEAD = _SECRET_NAME`: no bearer head, unlike FIX-A),
`_ENVVAL_HEAD`, `_SK`, `_TOKEN`, `_ENVVAL`,
`_ENVVAL_WIDE`, `_PRIVKEY`, the placeholders, `_redact_str`'s pass order (the D-1 class order), `bound`, `normalize`, the schemas.
Refactor check (`/tmp/j113s/v/attr3.py`, section 5c): the final file with all four changes reverted equals fb016d0's output on
all 120,000 differential inputs (no `V_none != fb016d0` key in any run).

## 3. Tests (each file: one block at the end; the rows are FAKE `QZJ8` bodies)

Where the new tests are (each line: the reference and an identifier from it):
- `tests/test_decisions_canonical.py:17-19`: the docstring now names "tasks/briefs/laya/J1-1-R3-brief.md (C1-C5)".
- `tests/test_decisions_canonical.py:1062-1085`: the block header "J1-1-R3 -- AMENDMENT 3 to J1-1 (D-059; tasks/briefs/laya/J1-1-R3-brief.md," and `_TR = "ab" * 16`.
- `tests/test_decisions_canonical.py:1086`: `_R1_ROWS = [` (5 rows); `tests/test_decisions_canonical.py:1095`: `_R2_ROWS = [` (4); `tests/test_decisions_canonical.py:1119`: `_R4_ROWS = [` (6).
- `tests/test_decisions_canonical.py:1155`: `_R3_ROWS = [` (4); `tests/test_decisions_canonical.py:1173`: `_MUTANT_ROWS = [` (4); `tests/test_decisions_canonical.py:1189`: `_MERGE_CONTROL_ROWS = [` (5).
- `tests/test_decisions_canonical.py:1221`: `def test_r1_bearer_run_takes_the_pin_letters`.
- `tests/test_decisions_canonical.py:1228`: `def test_r2_token_check_reads_the_run_as_the_token_class_does`.
- `tests/test_decisions_canonical.py:1234`: `def test_r4_env_check_reads_the_value_after_the_bearer_merge`.
- `tests/test_decisions_canonical.py:1240`: `def test_r3_upper_name_equals_space_value_behind_sk_or_bearer`.
- `tests/test_decisions_canonical.py:1246`: `def test_surviving_mutant_rows_stay_redacted`.
- `tests/test_decisions_canonical.py:1252`: `def test_bearer_merge_step_keeps_every_j1_1_r2_redaction`.
- `tests/test_decisions_canonical.py:928`: every row goes through `def _assert_driver_row`: no `QZJ8` byte in the output or in `canonical()`, the exact text,
  a fixed point of `decision_state`, and the same digest when the fake value changes.
- `tests/test_decisions_ledger.py:1613-1626`: the block header "J1-1-R3 (D-059, C1-C4): the same rows as tests/test_decisions_canonical.py's".
- `tests/test_decisions_ledger.py:1627`: `_R1_SHAPES = [`; `tests/test_decisions_ledger.py:1667`: `_MERGE_CONTROL_SHAPES = [`; the same 28 shapes.
- `tests/test_decisions_ledger.py:1681`: `def test_r1_bearer_token_bytes_never_reach_the_ledger_file`.
- `tests/test_decisions_ledger.py:1687`: `def test_r2_second_value_never_reaches_the_ledger_file`.
- `tests/test_decisions_ledger.py:1693`: `def test_r4_value_after_a_bearer_merge_never_reaches_the_ledger_file`.
- `tests/test_decisions_ledger.py:1699`: `def test_r3_upper_name_equals_space_value_never_reaches_the_ledger_file`.
- `tests/test_decisions_ledger.py:1705`: `def test_surviving_mutant_rows_stay_off_the_ledger_file`.
- `tests/test_decisions_ledger.py:1711`: `def test_bearer_merge_step_keeps_every_j1_1_r2_redaction_in_the_file`.
- `tests/test_decisions_ledger.py:1591`: each shape goes through `def _assert_no_value_byte_on_disk` (`make_row` -> `append` -> the file bytes -> `replay`;
  no Q, Z or J byte in the file, and `replay` returns the row).
Totals: 121 -> 177 (+28 per file).

RED at the head and GREEN after. The new tests (`-k 'r1_ or r2_ or r4_ or r3_ or surviving or merge_step or zz_imports'`) run
in minimal trees built by `/tmp/j113s/mktree.sh`: `pyproject.toml`, `src/` with the named `volatile.py`, `tests/conftest.py`, the
decision fixtures, the two final test files, plus a scratch-only guard `tests/test_zz_import_path.py` that asserts the tree
imports its OWN `volatile.py`:
```
=== red_head 2026-09-24T04:08:16Z volatile blob bf04415d72c1     (fb016d0, the head)
30 failed, 27 passed, 121 deselected in 1.08s
=== red_pin 2026-09-24T04:08:18Z volatile blob 20ebcd54f3ed      (d556c9b, for information)
22 failed, 35 passed, 121 deselected in 0.88s
=== green 2026-09-24T04:08:19Z volatile blob 2d5cf0072469        (the final code)
57 passed, 121 deselected in 0.34s
```
The 30 red at the head (15 per file; `/tmp/j113s/logs/final_redgreen_red_head.log`): R-1 dotless-i-inside, dotless-i-first,
long-s-tail, dotted-I-inside; R-2 sk-dotless-i, bearer-long-s, sk-quote-dotted-I; R-4 widened-bearer-padding,
upper-bearer-padding, bearer-yield-then-bearer, head-the-bearer-leaves, special-letter-in-the-merged-run; R-3 sk-name-space,
bearer-name-space, sk-value-then-name-space. The 26 green at the head (13 per file) are the four class controls (R-1
ascii-control, R-2 ascii-control, R-4 space-before-bearer-control, R-3 no-prefix-control), the four C3 rows and the five C4
controls. They pin behaviour the head already has; their negative controls are mutants (section 4; DISCREPANCY D-3).
The 22 red at d556c9b (12 canonical + 10 ledger) are the three R-3 rows and head-the-bearer-leaves, which leak there too,
plus rows that pin J1-1-R2's V-1 output: V-M3/V-M11 and the C4 controls, whose first value d556c9b's sk run frees. In the
canonical file two more rows fail on the exact text alone (space-before-bearer-control, bearer-run-of-15-glued); the
ledger file's check is body-only, so they pass there. This is not a regression claim: d556c9b predates the V-1 repair.

## 4. Mutation audit (scratch copies only; `/tmp/j113s/mut/mutr3.py`, 2026-09-24T04:08:25Z to 04:13:34Z)

Per mutant: exact-count edits (count asserted 1) of the final `volatile.py`, written into one minimal tree `/tmp/j113s/mut/tree`
(its `__pycache__` cleared each time). Then `py_compile`, the collection count equal to the baseline (AF-AP-78), and the run of
the two files plus the import guard; the guard must stay green, and it did in all 58. Every killing test is re-run on the
UNMUTATED tree `/tmp/j113s/green` (AF-AP-138). The builder's 30 rows (its report's section 10) are translated onto the new
structure: a branch removed from `_yield_pattern` leaves BOTH depths (the real `_YIELD` and the step's depth-0 yield), and
b-m4k puts the global `(?i)` at the start of `_BEARER`'s pattern. The builder's `mut.py` no longer exists; the edits follow
the verifier's rebuild (`tools/mut7.py`), adjusted to the new line texts. V-M1…V-M13 are the verifier's (section 8 of its
report). n1-n10 are mine, one per element of the new step, plus n6 = the verifier's FIX-A R-4 line as written.
```
BASELINE (unmutated): rc=0 178 passed in 4.92s collected=178          (177 + the import guard)
RESTORED pristine: rc=0 178 passed in 3.80s; volatile equals the final file: True      (batch 0-29)
RESTORED pristine: rc=0 178 passed in 3.79s; volatile equals the final file: True      (batch 29-58)
```
Abbreviations: `c::` = `tests/test_decisions_canonical.py::`, `l::` = `tests/test_decisions_ledger.py::`; `r1` `r2` `r4` `r3`
`c3` `c4` = the six new tests of each file (section 3); `v1row`, `control`, `class`, `straddle`, `shapes43`, `ledger-v1row`,
`ledger-control` = J1-1-R2's tests, as in its report.

| id | owner | mutant | run (mutated; collected 178/178, compile ok, guard green) | killing tests | unmutated re-run |
|---|---|---|---|---|---|
| m1 | brief | R-4 step reverted (FIX-A line 61's role): _YIELD without the bearer merge step | 10 failed, 168 passed :: KILLED | c::r4[bearer-yield-then-bearer], c::r4[head-the-bearer-leaves], c::r4[special-letter-in-the-merged-run], c::r4[upper-bearer-padding], c::r4[widened-bearer-padding], l::r4[bearer-yield-then-bearer], l::r4[head-the-bearer-leaves], l::r4[special-letter-in-the-merged-run], l::r4[upper-bearer-padding], l::r4[widened-bearer-padding] | rc=0 10 passed |
| m2 | brief | R-2 reverted (FIX-A line 72): token check/scan case-sensitive | 6 failed, 172 passed :: KILLED | c::r2[bearer-long-s], c::r2[sk-dotless-i], c::r2[sk-quote-dotted-I], l::r2[bearer-long-s], l::r2[sk-dotless-i], l::r2[sk-quote-dotted-I] | rc=0 6 passed |
| m3 | brief | R-1 reverted (FIX-A line 75): _BEARER_RUN case-sensitive (pass and step) | 10 failed, 168 passed :: KILLED | c::r1[dotless-i-first], c::r1[dotless-i-inside], c::r1[dotted-I-inside], c::r1[long-s-tail], c::r4[special-letter-in-the-merged-run], l::r1[dotless-i-first], l::r1[dotless-i-inside], l::r1[dotted-I-inside], l::r1[long-s-tail], l::r4[special-letter-in-the-merged-run] | rc=0 10 passed |
| m3b | lane | R-1 reverted in the _BEARER pass only (fb016d0's exact line 75) | 10 failed, 168 passed :: KILLED | c::r1[dotless-i-first], c::r1[dotless-i-inside], c::r1[dotted-I-inside], c::r1[long-s-tail], c::r4[special-letter-in-the-merged-run], l::r1[dotless-i-first], l::r1[dotless-i-inside], l::r1[dotted-I-inside], l::r1[long-s-tail], l::r4[special-letter-in-the-merged-run] | rc=0 10 passed |
| m4 | brief | FIX-B reverted: the widened branch refuses every upper-case NAME= | 6 failed, 172 passed :: KILLED | c::r3[bearer-name-space], c::r3[sk-name-space], c::r3[sk-value-then-name-space], l::r3[bearer-name-space], l::r3[sk-name-space], l::r3[sk-value-then-name-space] | rc=0 6 passed |
| m5 | brief | V-M3: the token branch's name case-sensitive | 2 failed, 176 passed :: KILLED | c::c3[V-M3-upper-token-space], l::c3[V-M3-upper-token-space] | rc=0 2 passed |
| m6 | brief | V-M11: (?<=_) dropped in the token branch only | 2 failed, 176 passed :: KILLED | c::c3[V-M11-underscore-token-space], l::c3[V-M11-underscore-token-space] | rc=0 2 passed |
| m7 | brief | V-M4: _ASSIGNMENT_HEAD's token alternative case-sensitive | 2 failed, 176 passed :: KILLED | c::c3[V-M4-upper-token-head-in-a-chain], l::c3[V-M4-upper-token-head-in-a-chain] | rc=0 2 passed |
| b-m1 | builder | _SK back to its PIN form | 43 failed, 135 passed :: KILLED | c::c4[bearer-run-of-15-glued], c::c4[head-the-bearer-consumes], c::c4[merge-no-head], c::c4[short-bearer-no-merge], c::c4[token-run-glued-to-bearer], c::r3[sk-name-space], c::r3[sk-value-then-name-space], c::r4[space-before-bearer-control], c::c3[V-M11-underscore-token-space], c::c3[V-M3-upper-token-space], … (+33 more) | rc=0 43 passed |
| b-m2 | builder | _BEARER back to its PIN form | 9 failed, 169 passed :: KILLED | c::r3[bearer-name-space], c::r4[head-the-bearer-leaves], c::class[token-space-bearer], c::v1row[V1-g], c::straddle, c::shapes43, l::r3[bearer-name-space], l::r4[head-the-bearer-leaves], l::ledger-v1row[V1-g] | rc=0 9 passed |
| b-m3 | builder | the verifier's option-B bearer (exact) | 12 failed, 166 passed :: KILLED | c::r3[bearer-name-space], c::r4[bearer-yield-then-bearer], c::r4[head-the-bearer-leaves], c::class[no-value], c::class[token-space-bearer], c::control[C-4], c::v1row[V1-g], c::straddle, l::r3[bearer-name-space], l::r4[bearer-yield-then-bearer], l::r4[head-the-bearer-leaves], l::ledger-control[C-4] | rc=0 12 passed |
| b-m4a | builder | _YIELD without the NAME= branch | 11 failed, 167 passed :: KILLED | c::c4[head-the-bearer-consumes], c::class[upper-api_key-short], c::class[upper-key-short], c::class[upper-passwd-short], c::class[upper-secret-short], c::class[upper-token-short], c::v1row[V1-f], c::straddle, c::shapes43, l::c4[head-the-bearer-consumes], l::ledger-v1row[V1-f] | rc=0 11 passed |
| b-m4b | builder | _YIELD without the widened branch | 33 failed, 145 passed :: KILLED | c::c4[bearer-run-of-15-glued], c::c4[merge-no-head], c::c4[short-bearer-no-merge], c::r3[bearer-name-space], c::r3[sk-name-space], c::r3[sk-value-then-name-space], c::r4[head-the-bearer-leaves], c::r4[space-before-bearer-control], c::class[name-api_key], c::class[name-passwd], … (+23 more) | rc=0 33 passed |
| b-m4c | builder | _YIELD without the token branch | 8 failed, 170 passed :: KILLED | c::c4[token-run-glued-to-bearer], c::c3[V-M11-underscore-token-space], c::c3[V-M3-upper-token-space], c::class[token-space-bearer], c::class[token-space-sk], l::c4[token-run-glued-to-bearer], l::c3[V-M11-underscore-token-space], l::c3[V-M3-upper-token-space] | rc=0 8 passed |
| b-m4d1 | builder | widened branch without its chain guard | 9 failed, 169 passed :: KILLED | c::r4[bearer-yield-then-bearer], c::r4[head-the-bearer-leaves], c::r4[special-letter-in-the-merged-run], c::r4[widened-bearer-padding], c::class[chain-widened], l::r4[bearer-yield-then-bearer], l::r4[head-the-bearer-leaves], l::r4[special-letter-in-the-merged-run], l::r4[widened-bearer-padding] | rc=0 9 passed |
| b-m4d2 | builder | NAME= branch without its chain guard | 9 failed, 169 passed :: KILLED | c::r4[upper-bearer-padding], c::c3[V-M10-upper-apikey-chain], c::c3[V-M4-upper-token-head-in-a-chain], c::class[chain-upper-past-a-stop], c::class[chain-upper-token-space], c::class[chain-upper], l::r4[upper-bearer-padding], l::c3[V-M10-upper-apikey-chain], l::c3[V-M4-upper-token-head-in-a-chain] | rc=0 9 passed |
| b-m4d3 | builder | token branch without its chain guard | 9 failed, 169 passed :: KILLED | c::r2[ascii-control], c::r2[bearer-long-s], c::r2[sk-dotless-i], c::r2[sk-quote-dotted-I], c::class[chain-token-run], l::r2[ascii-control], l::r2[bearer-long-s], l::r2[sk-dotless-i], l::r2[sk-quote-dotted-I] | rc=0 9 passed |
| b-m4e | builder | widened branch without its 8+ value condition | 4 failed, 174 passed :: KILLED | c::c4[head-the-bearer-consumes], c::class[lower-equals], c::class[no-value], l::c4[head-the-bearer-consumes] | rc=0 4 passed |
| b-m4e3 | builder | token branch without its 32+ condition | 10 failed, 168 passed :: KILLED | c::r2[ascii-control], c::r2[bearer-long-s], c::r2[sk-dotless-i], c::r2[sk-quote-dotted-I], c::class[chain-token-run], c::class[token-space-no-run], l::r2[ascii-control], l::r2[bearer-long-s], l::r2[sk-dotless-i], l::r2[sk-quote-dotted-I] | rc=0 10 passed |
| b-m4f | builder | NAME= branch accepts = padding | 1 failed, 177 passed :: KILLED | c::class[padding] | rc=0 1 passed |
| b-m4g | builder | _SK floor on the truncated run | 21 failed, 157 passed :: KILLED | c::c4[bearer-run-of-15-glued], c::c4[head-the-bearer-consumes], c::c4[merge-no-head], c::c4[short-bearer-no-merge], c::r3[sk-name-space], c::r4[space-before-bearer-control], c::c3[V-M11-underscore-token-space], c::c3[V-M3-upper-token-space], c::class[name-api_key], c::class[name-passwd], … (+11 more) | rc=0 21 passed |
| b-m4g2 | builder | _BEARER floor on the truncated run | 2 failed, 176 passed :: KILLED | c::v1row[V1-g], c::straddle | rc=0 2 passed |
| b-m4h | builder | widened branch without its NAME= exclusion | 3 failed, 175 passed :: KILLED | c::c3[V-M10-upper-apikey-chain], c::class[chain-upper-past-a-stop], l::c3[V-M10-upper-apikey-chain] | rc=0 3 passed |
| b-m4i | builder | _ASSIGNMENT_HEAD without its token alternative | 3 failed, 175 passed :: KILLED | c::c3[V-M4-upper-token-head-in-a-chain], c::class[chain-upper-token-space], l::c3[V-M4-upper-token-head-in-a-chain] | rc=0 3 passed |
| b-m4j | builder | _ASSIGNMENT_HEAD without its name alternative | 24 failed, 154 passed :: KILLED | c::r2[ascii-control], c::r2[bearer-long-s], c::r2[sk-dotless-i], c::r2[sk-quote-dotted-I], c::r4[bearer-yield-then-bearer], c::r4[head-the-bearer-leaves], c::r4[special-letter-in-the-merged-run], c::r4[upper-bearer-padding], c::r4[widened-bearer-padding], c::c3[V-M10-upper-apikey-chain], … (+14 more) | rc=0 24 passed |
| b-m4k | builder | _BEARER with a global (?i) | 1 failed, 177 passed :: KILLED | c::class[lower-equals] | rc=0 1 passed |
| b-m4n-KEY | builder | _SECRET_NAME without KEY | 9 failed, 169 passed :: KILLED | c::r2[bearer-long-s], c::r4[bearer-yield-then-bearer], c::class[chain-token-run], c::v1row[V1-d], c::straddle, c::shapes43, l::r2[bearer-long-s], l::r4[bearer-yield-then-bearer], l::ledger-v1row[V1-d] | rc=0 9 passed |
| b-m4n-TOKEN | builder | _SECRET_NAME without TOKEN | 12 failed, 166 passed :: KILLED | c::r4[special-letter-in-the-merged-run], c::r4[upper-bearer-padding], c::r4[widened-bearer-padding], c::class[chain-upper-past-a-stop], c::class[chain-upper], c::v1row[V1-e], c::straddle, c::shapes43, l::r4[special-letter-in-the-merged-run], l::r4[upper-bearer-padding], l::r4[widened-bearer-padding], l::ledger-v1row[V1-e] | rc=0 12 passed |
| b-m4n-SECRET | builder | _SECRET_NAME without SECRET | 7 failed, 171 passed :: KILLED | c::r2[sk-quote-dotted-I], c::r3[sk-value-then-name-space], c::c3[V-M10-upper-apikey-chain], c::class[name-secret], l::r2[sk-quote-dotted-I], l::r3[sk-value-then-name-space], l::c3[V-M10-upper-apikey-chain] | rc=0 7 passed |
| b-m4n-PASSWORD | builder | _SECRET_NAME without PASSWORD | 26 failed, 152 passed :: KILLED | c::c4[bearer-run-of-15-glued], c::c4[merge-no-head], c::c4[short-bearer-no-merge], c::r2[ascii-control], c::r2[sk-dotless-i], c::r3[sk-name-space], c::r4[head-the-bearer-leaves], c::r4[space-before-bearer-control], c::v1row[V1-a], c::v1row[V1-b], … (+16 more) | rc=0 26 passed |
| b-m4n-PASSWD | builder | _SECRET_NAME without PASSWD | 1 failed, 177 passed :: KILLED | c::class[name-passwd] | rc=0 1 passed |
| b-m4n-APIKEY | builder | _SECRET_NAME without API_?KEY | 2 failed, 176 passed :: KILLED | c::r3[bearer-name-space], c::class[name-api_key] | rc=0 2 passed |
| b-m4u-KEY | builder | _ENVVAL_HEAD without KEY | 3 failed, 175 passed :: KILLED | c::c3[V-M10-upper-apikey-chain], c::class[upper-key-short], l::c3[V-M10-upper-apikey-chain] | rc=0 3 passed |
| b-m4u-TOKEN | builder | _ENVVAL_HEAD without TOKEN | 1 failed, 177 passed :: KILLED | c::class[upper-token-short] | rc=0 1 passed |
| b-m4u-SECRET | builder | _ENVVAL_HEAD without SECRET | 1 failed, 177 passed :: KILLED | c::class[upper-secret-short] | rc=0 1 passed |
| b-m4u-PASSWORD | builder | _ENVVAL_HEAD without PASSWORD | 5 failed, 173 passed :: KILLED | c::class[chain-upper-past-a-stop], c::v1row[V1-f], c::straddle, c::shapes43, l::ledger-v1row[V1-f] | rc=0 5 passed |
| b-m4u-PASSWD | builder | _ENVVAL_HEAD without PASSWD | 1 failed, 177 passed :: KILLED | c::class[upper-passwd-short] | rc=0 1 passed |
| b-m4u-APIKEY | builder | _ENVVAL_HEAD without API_?KEY | 3 failed, 175 passed :: KILLED | c::c3[V-M10-upper-apikey-chain], c::class[upper-api_key-short], l::c3[V-M10-upper-apikey-chain] | rc=0 3 passed |
| V-M1 | verifier | _SECRET_NAME case-sensitive | 42 failed, 136 passed :: KILLED | c::c4[bearer-run-of-15-glued], c::c4[merge-no-head], c::c4[short-bearer-no-merge], c::r2[ascii-control], c::r2[bearer-long-s], c::r2[sk-dotless-i], c::r2[sk-quote-dotted-I], c::r4[head-the-bearer-leaves], c::r4[space-before-bearer-control], c::r4[upper-bearer-padding], … (+32 more) | rc=0 42 passed |
| V-M2 | verifier | bearer literal case-sensitive (the _BEARER pass) | 26 failed, 152 passed :: KILLED | c::test_over_limit_identity_every_class, c::r1[ascii-control], c::r1[dotless-i-first], c::r1[dotless-i-inside], c::r1[dotted-I-inside], c::r1[long-s-tail], c::r2[bearer-long-s], c::r3[bearer-name-space], c::r4[bearer-yield-then-bearer], c::test_secret_redacted_every_class, … (+16 more) | rc=0 26 passed |
| V-M5 | verifier | _SK lookahead {8} -> {7} | 1 failed, 177 passed :: KILLED | c::control[C-2] | rc=0 1 passed |
| V-M6 | verifier | widened value condition {8} -> {7} | 2 failed, 176 passed :: KILLED | c::c4[head-the-bearer-consumes], l::c4[head-the-bearer-consumes] | rc=0 2 passed |
| V-M7 | verifier | _BEARER lookahead {16} -> {15} (the pass) | 2 failed, 176 passed :: KILLED | c::c4[bearer-run-of-15-glued], l::c4[bearer-run-of-15-glued] | rc=0 2 passed |
| V-M8 | verifier | widened branch's scan emptied | 9 failed, 169 passed :: KILLED | c::r4[bearer-yield-then-bearer], c::r4[head-the-bearer-leaves], c::r4[special-letter-in-the-merged-run], c::r4[widened-bearer-padding], c::class[chain-widened], l::r4[bearer-yield-then-bearer], l::r4[head-the-bearer-leaves], l::r4[special-letter-in-the-merged-run], l::r4[widened-bearer-padding] | rc=0 9 passed |
| V-M9 | verifier | NAME= branch scan class narrowed \S -> the widened class | 3 failed, 175 passed :: KILLED | c::c3[V-M10-upper-apikey-chain], c::class[chain-upper-past-a-stop], l::c3[V-M10-upper-apikey-chain] | rc=0 3 passed |
| V-M10 | verifier | _ENVVAL_HEAD narrowed: API_?KEY -> API_KEY | 2 failed, 176 passed :: KILLED | c::c3[V-M10-upper-apikey-chain], l::c3[V-M10-upper-apikey-chain] | rc=0 2 passed |
| V-M12 | verifier | (?<=_) dropped in _ASSIGNMENT_HEAD only | 3 failed, 175 passed :: KILLED | c::c3[V-M4-upper-token-head-in-a-chain], c::class[chain-upper-token-space], l::c3[V-M4-upper-token-head-in-a-chain] | rc=0 3 passed |
| V-M13 | verifier | _ASSIGNMENT_HEAD token alternative loses its whitespace separator | 3 failed, 175 passed :: KILLED | c::c3[V-M4-upper-token-head-in-a-chain], c::class[chain-upper-token-space], l::c3[V-M4-upper-token-head-in-a-chain] | rc=0 3 passed |
| n1 | lane | the step skips the whole bearer run (no replayed yield) | 2 failed, 176 passed :: KILLED | c::r4[head-the-bearer-leaves], l::r4[head-the-bearer-leaves] | rc=0 2 passed |
| n2 | lane | the step's run not possessive | 2 failed, 176 passed :: KILLED | c::c4[head-the-bearer-consumes], l::c4[head-the-bearer-consumes] | rc=0 2 passed |
| n3 | lane | the step without its 16-run lookahead | 3 failed, 175 passed :: KILLED | c::c4[bearer-run-of-15-glued], c::c4[short-bearer-no-merge], l::c4[short-bearer-no-merge] | rc=0 3 passed |
| n4 | lane | no step in the widened branch | 8 failed, 170 passed :: KILLED | c::r4[bearer-yield-then-bearer], c::r4[head-the-bearer-leaves], c::r4[special-letter-in-the-merged-run], c::r4[widened-bearer-padding], l::r4[bearer-yield-then-bearer], l::r4[head-the-bearer-leaves], l::r4[special-letter-in-the-merged-run], l::r4[widened-bearer-padding] | rc=0 8 passed |
| n5 | lane | no step in the NAME= branch | 2 failed, 176 passed :: KILLED | c::r4[upper-bearer-padding], l::r4[upper-bearer-padding] | rc=0 2 passed |
| n6 | lane | the verifier's FIX-A R-4 line as written (a bearer head, no step) | 9 failed, 169 passed :: KILLED | c::c4[bearer-run-of-15-glued], c::c4[head-the-bearer-consumes], c::c4[merge-no-head], c::c4[short-bearer-no-merge], c::c4[token-run-glued-to-bearer], l::c4[head-the-bearer-consumes], l::c4[merge-no-head], l::c4[short-bearer-no-merge], l::c4[token-run-glued-to-bearer] | rc=0 9 passed |
| n7 | lane | the step's run case-sensitive (the step only) | 2 failed, 176 passed :: KILLED | c::r4[special-letter-in-the-merged-run], l::r4[special-letter-in-the-merged-run] | rc=0 2 passed |
| n8 | lane | the step's bearer literal case-sensitive | 2 failed, 176 passed :: KILLED | c::r4[bearer-yield-then-bearer], l::r4[bearer-yield-then-bearer] | rc=0 2 passed |
| n9 | lane | the step's lookahead {16} -> {15} | 1 failed, 177 passed :: KILLED | c::c4[bearer-run-of-15-glued] | rc=0 1 passed |
| n10 | lane | a bearer head in the token branch's scan (FIX-A's head there) | 2 failed, 176 passed :: KILLED | c::c4[token-run-glued-to-bearer], l::c4[token-run-glued-to-bearer] | rc=0 2 passed |

mutants: 58 | killed: 58 | survivors: 0 | guard failures: 0 | re-runs not green: 0

The brief's rows: m1 (the R-4 step reverted) is killed by exactly the R-4 tests (5 per file). m2 (R-2 reverted) by exactly
the R-2 tests. m3 and m3b (R-1 reverted, pass and step, or the pass alone) by the R-1 tests plus the R-4 special-letter row.
m4 (FIX-B reverted) by exactly the C2 tests. m5, m6 and m7 (V-M3, V-M11, V-M4) each by their own C3 row in both files.
First run of this audit (before two rows changed, `/tmp/j113s/logs/mut_29_58.log`): 56 killed, 2 SURVIVED, V-M6 (the widened
value condition `{8}` -> `{7}`) and V-M10 (`API_?KEY` -> `API_KEY` in `_ENVVAL_HEAD`). The verifier had classed both as
changing no body byte. On my code each frees a value on rare generator inputs (`/tmp/j113s/mut/surv.py`,
`/tmp/j113s/logs/survivors.log`):
```
seed=11 ascii=True inputs=20000 {'V-M10 hides a body byte the final code shows': 21, 'V-M10 outputs differ': 35, 'V-M6 hides a body byte the final code shows': 1, 'V-M6 outputs differ': 492, 'V-M6 shows a body byte the final code hides': 2}
seed=2 ascii=False inputs=20000 {'V-M10 hides a body byte the final code shows': 11, 'V-M10 outputs differ': 23, 'V-M10 shows a body byte the final code hides': 1, 'V-M6 hides a body byte the final code shows': 4, 'V-M6 outputs differ': 378, 'V-M6 shows a body byte the final code hides': 2}
(shortened extracts of /tmp/j113s/mut/surv_show.py's output)
V-M10 IN "sk-9663SECRETAPIKEY='J6JX…6'&Secret = 539449Q9Q545"   final "<redacted:sk>='…'&Secret = <redacted:envval>"   mutant '<redacted:sk>APIKEY=<redacted:envval> = 539449Q9Q545'
V-M6  IN 'db_API_KEY=Q48JZQ0 BEARER X9J9J55787420X2J7Password==JZX677sk-ZX5__Z-2JKeyApiKey"=Z3XQZ28'   final '… <redacted:bearer>Password=<redacted:envval>"=Z3XQZ28'   mutant '… <redacted:bearer>JZX677<redacted:sk>ApiKey"=Z3XQZ28'
```
Two edits closed both gaps. `head-the-bearer-consumes` now carries a 7-character value, one under the floor, so V-M6's
replayed yield flips there. A new row, `V-M10-upper-apikey-chain`, puts `task-DB_APIKEY='plainvalue'&Secret = <body>` in both
files. The final run above kills all 58.

## 5. C1, C4 and C5 measurements (every run on the final file, blob 2d5cf0072469)

### 5a. C1: the verifier's case files, rebuilt with its own scripts (`icase_ledger.py`, `r2_chain.py`, `r4_ledger.py`, `r3_ledger.py`, `fixcases.py`)
Each row goes through `tools/ledger_worker.py`: `decision_state` -> `canonical` -> `make_row` -> `append` -> the JSONL line on
disk -> `replay`. `treepin` = d556c9b; `treenew` = `treefixa` = `treefixb` = my code (`/tmp/j113s/logs/FINAL_c1_casefiles.log`):
```
icase treefixa  replay={'replayed': 10, 'err': None} idem-all=True rows-with-the-checked-body=[]
r2    treefixa  replay={'replayed': 4, 'err': None} idem-all=True rows-with-the-checked-body=[]
r3    treefixa  replay={'replayed': 7, 'err': None} idem-all=True rows-with-the-checked-body=['R3-f task-PASSWORD==v (padding form)']
r4    treefixa  replay={'replayed': 5, 'err': None} idem-all=True rows-with-the-checked-body=[]
msg dotless-i inside       PIN line-has-body=False NEW line-has-body=False err=None idem=True
snippet dotless-i inside   PIN line-has-body=False NEW line-has-body=False err=None idem=True
msg dotless-i first        PIN line-has-body=False NEW line-has-body=False err=None idem=True
snippet dotless-i first    PIN line-has-body=False NEW line-has-body=False err=None idem=True
msg long-s tail            PIN line-has-body=False NEW line-has-body=False err=None idem=True
snippet long-s tail        PIN line-has-body=False NEW line-has-body=False err=None idem=True
msg dotted-I inside        PIN line-has-body=False NEW line-has-body=False err=None idem=True
snippet dotted-I inside    PIN line-has-body=False NEW line-has-body=False err=None idem=True
msg control ascii          PIN line-has-body=False NEW line-has-body=False err=None idem=True
snippet control ascii      PIN line-has-body=False NEW line-has-body=False err=None idem=True
R2-a sk, token space, dotless-i, password:   V2-in-line PIN=False NEW=False | RUN-in-line PIN=True  NEW=True  idem=True
R2-b bearer, token space, long-s, key=       V2-in-line PIN=False NEW=False | RUN-in-line PIN=True  NEW=True  idem=True
R2-c sk, _token quote, dotted-I, secret:     V2-in-line PIN=False NEW=False | RUN-in-line PIN=True  NEW=True  idem=True
R2-ctl same shape, ASCII (guard sees head)   V2-in-line PIN=False NEW=False | RUN-in-line PIN=True  NEW=True  idem=True
R4-a sk, widened, bearer ==, token:        V2-in-line PIN=False NEW=False | V1-in-line PIN=True  NEW=True  idem=True
R4-b sk, upper NAME=, bearer ==, token:    V2-in-line PIN=False NEW=False | V1-in-line PIN=True  NEW=True  idem=True
R4-c bearer, widened, bearer ), key:       V2-in-line PIN=False NEW=False | V1-in-line PIN=True  NEW=True  idem=True
R4-d sk, 'cupbearer' word, @ glue, secret= V2-in-line PIN=False NEW=False | V1-in-line PIN=False NEW=False idem=True
R4-ctl same as a, a space before bearer    V2-in-line PIN=False NEW=False | V1-in-line PIN=True  NEW=False idem=True
R3-a task-DB_PASSWORD= v               body-in-line PIN=True  NEW=False idem=True
R3-b Bearer … API_KEY= v               body-in-line PIN=True  NEW=False idem=True
R3-c sk-…SECRET= v                     body-in-line PIN=True  NEW=False idem=True
R3-f task-PASSWORD==v (padding form)   body-in-line PIN=True  NEW=True  idem=True      (the declared residue, section 8)
```
(The treefixb lines are identical, since both links point at my tree.) The checked body of the R-2/R-4 rows is V2. V1/the
run stays in the line exactly as at d556c9b: the chain form, section 8.

The field-and-cut sweep, the verifier's 12 shapes (`tools/fieldsweep.py`, `fieldsweep_grade.py`; pin = d556c9b):
```
treenew volatile: /tmp/j113s/v/treenew/src/agent_factory/decisions/volatile.py ledgers: 427 replayed rows: 17078 replay errors: []
R3-upper-eq-space    {'ok/ok': 577, 'leak->ok': 692}
R3-padding           {'ok/ok': 576, 'leak/leak': 597}
R1-bearer-dotless    {'ok/ok': 1141}
R2-token-longs       {'ok/ok': 481, 'leak/leak': 1900}
w-colon              {'ok/ok': 544, 'leak->ok': 817}
w-eq-quoted          {'ok/ok': 608, 'leak->ok': 723}
w-apikey-sp          {'ok/ok': 545, 'leak->ok': 724}
A-upper-eq           {'ok/ok': 576, 'leak->ok': 245}
C-token-quote        {'ok/ok': 576, 'leak->ok': 1025}
bearer-w             {'ok/ok': 577, 'leak->ok': 1054}
bearer-A             {'ok/ok': 577, 'leak->ok': 532}
bearer-C             {'ok/ok': 609, 'leak->ok': 1382}
fields where the NEW line leaks, per shape: {'R3-padding': 21, 'R2-token-longs': 20}
```
No `ok->LEAK` and no `NON-IDEM(new)` in any shape. R2-token-longs draws the run and V2 from one alphabet, so its `leak/leak`
rows are the run, as at d556c9b. My extension separates them: V2 in `B20`, the run as `ab`*16 (`/tmp/j113s/v/fieldsweep_r3.py`,
a copy with only SHAPES and output names changed; pin = fb016d0):
```
treenew volatile: /tmp/j113s/v/treenew/src/agent_factory/decisions/volatile.py ledgers: 449 replayed rows: 17928 replay errors: []
R4-widened           {'ok/ok': 1372, 'leak->ok': 979}
R4-upper             {'ok/ok': 1372, 'leak->ok': 979}
R4-bearer-yield      {'ok/ok': 1432, 'leak->ok': 1269}
R4-head-left         {'ok/ok': 1372, 'leak->ok': 1009}
C4-merge-no-head     {'ok/ok': 1631}
C4-head-consumed     {'ok/ok': 1811}
C4-token-glued       {'ok/ok': 2321}
R2-split             {'ok/ok': 1186, 'leak->ok': 1195}
fields where the NEW line leaks, per shape: {}
```

### 5b. C4: the verifier's differential (`tools/diff3.py`, its method: 6 seeds x 20,000; seeds 11/12/13 ASCII, 2/21/22 with U+0130/U+0131/U+017F)
```
=== diff3 vs d556c9b 2026-09-24T04:13:44Z new=2d5cf0072469
  vs d556c9b seed=11 ascii_only=True inputs=20000 outputs_differ=3204 newly_visible_inputs=3192 newly visible BODY inputs = 0 | INSTRUMENT DISAGREE = 0
  vs d556c9b seed=12 ascii_only=True inputs=20000 outputs_differ=3165 newly_visible_inputs=3154 newly visible BODY inputs = 0 | INSTRUMENT DISAGREE = 0
  vs d556c9b seed=13 ascii_only=True inputs=20000 outputs_differ=3253 newly_visible_inputs=3242 newly visible BODY inputs = 0 | INSTRUMENT DISAGREE = 0
  vs d556c9b seed=2 ascii_only=False inputs=20000 outputs_differ=2690 newly_visible_inputs=2684 newly visible BODY inputs = 0 | INSTRUMENT DISAGREE = 0
  vs d556c9b seed=21 ascii_only=False inputs=20000 outputs_differ=2730 newly_visible_inputs=2719 newly visible BODY inputs = 0 | INSTRUMENT DISAGREE = 0
  vs d556c9b seed=22 ascii_only=False inputs=20000 outputs_differ=2625 newly_visible_inputs=2614 newly visible BODY inputs = 0 | INSTRUMENT DISAGREE = 0
=== diff3 vs fb016d0 2026-09-24T04:15:24Z new=2d5cf0072469
  vs fb016d0 seed=11 ascii_only=True inputs=20000 outputs_differ=120 newly_visible_inputs=120 newly visible BODY inputs = 20 | INSTRUMENT DISAGREE = 0
  vs fb016d0 seed=12 ascii_only=True inputs=20000 outputs_differ=113 newly_visible_inputs=112 newly visible BODY inputs = 13 | INSTRUMENT DISAGREE = 0
  vs fb016d0 seed=13 ascii_only=True inputs=20000 outputs_differ=143 newly_visible_inputs=143 newly visible BODY inputs = 20 | INSTRUMENT DISAGREE = 0
  vs fb016d0 seed=2 ascii_only=False inputs=20000 outputs_differ=3187 newly_visible_inputs=391 newly visible BODY inputs = 238 | INSTRUMENT DISAGREE = 0
  vs fb016d0 seed=21 ascii_only=False inputs=20000 outputs_differ=3152 newly_visible_inputs=430 newly visible BODY inputs = 261 | INSTRUMENT DISAGREE = 0
  vs fb016d0 seed=22 ascii_only=False inputs=20000 outputs_differ=3180 newly_visible_inputs=426 newly visible BODY inputs = 257 | INSTRUMENT DISAGREE = 0
```
(The BODY count is the sum of the `newly:*` keys whose role set holds `body`, parsed from `diff3.py`'s own output line.)
Against d556c9b the only newly visible roles are `name`, `sep`, `keyname` and `pad`, D-1's accepted class, e.g. seed=11
`{'newly:name+sep': 416, 'newly:name': 2746, 'newly:keyname+pad': 27, 'newly:keyname+name+pad': 3}`. **C4 against fb016d0 is NOT
met: DISCREPANCY D-1.**

### 5c. The exposures against fb016d0, attributed mechanically (`/tmp/j113s/v/attr3.py`)
The final file with each of its four changes reverted singly (R1 `_BEARER_RUN`, R2 the token check, R4 the step, R3 FIX-B)
gives five variants. An exposure is attributed to a change when the variant keeping ONLY that change shows exactly the same
newly visible body positions. "trade" = the final code ALSO hides a secret byte (body/tokchar/special) that fb016d0 showed.
```
=== attr3 2026-09-24T04:17:26Z final=2d5cf0072469
seed=11 ascii_only=True {'attributed to R4': 20, 'attributed to R4 pure': 13, 'attributed to R4 trade': 7, 'exposures': 20, 'inputs': 20000, 'pure': 13, 'trade': 7}
seed=12 ascii_only=True {'attributed to R4': 13, 'attributed to R4 pure': 6, 'attributed to R4 trade': 7, 'exposures': 13, 'inputs': 20000, 'pure': 6, 'trade': 7}
seed=13 ascii_only=True {'attributed to R4': 20, 'attributed to R4 pure': 13, 'attributed to R4 trade': 7, 'exposures': 20, 'inputs': 20000, 'pure': 13, 'trade': 7}
seed=2 ascii_only=False {'attributed to NONE ALONE (a combination)': 9, 'attributed to NONE ALONE (a combination) trade': 9, 'attributed to R1': 221, 'attributed to R1 trade': 221, 'attributed to R3': 1, 'attributed to R3 trade': 1, 'attributed to R4': 7, 'attributed to R4 pure': 3, 'attributed to R4 trade': 4, 'exposures': 238, 'inputs': 20000, 'pure': 3, 'trade': 235}
seed=21 ascii_only=False {'attributed to NONE ALONE (a combination)': 8, 'attributed to NONE ALONE (a combination) pure': 1, 'attributed to NONE ALONE (a combination) trade': 7, 'attributed to R1': 247, 'attributed to R1 trade': 247, 'attributed to R4': 6, 'attributed to R4 pure': 3, 'attributed to R4 trade': 3, 'exposures': 261, 'inputs': 20000, 'pure': 4, 'trade': 257}
seed=22 ascii_only=False {'attributed to NONE ALONE (a combination)': 10, 'attributed to NONE ALONE (a combination) trade': 10, 'attributed to R1': 238, 'attributed to R1 trade': 238, 'attributed to R4': 9, 'attributed to R4 pure': 3, 'attributed to R4 trade': 6, 'exposures': 257, 'inputs': 20000, 'pure': 3, 'trade': 254}
```
With all four changes reverted, the variant equals fb016d0 on all 120,000 inputs (no `V_none != fb016d0 (REFACTOR DEFECT)` key).
What the buckets are (examples: `/tmp/j113s/v/out/attr3_*.json`):
- R1 trades (221-247 per special-letter seed): fb016d0's bearer did not even match a token holding U+0130/U+0131/U+017F (R-1),
  so the token showed. With the PIN's run restored, the bearer matches, and the chain rule gives d556c9b's output (the first
  two examples print `C==D: True`):
  `bearer İZ8QQ16ZZ1201414QQ564967Api_Key: "9Z376930X1872J6X63JZPASSWORD:00Zſ1206Q0Z9"&…` fb016d0 `bearer İZ8QQ…Api_Key: "<redacted:envval>"…`,
  final = d556c9b `<redacted:bearer>: "9Z376930X1872J6X63JZPASSWORD:<redacted:envval>"…`.
- R4 trades (true chains): the value fb016d0 freed (V2) is hidden, and the first value shows as at d556c9b.
- R4 pure (13/6/13 ASCII, 3/3/3 special): chains the design's conservative head rule refuses, where fb016d0 yielded only
  because it judged the pre-merge value. Either the tail after the merge holds a head whose value is glued (the merged value
  would swallow it whole), or a token head whose run `_TOKEN` already redacts. The same rule refuses the same shapes without a
  merge at fb016d0 as well (measured: `task-password:abcdefghkey=X4Z9X4Z9` -> `ta<redacted:sk>:abcdefghkey=<redacted:envval>` at
  d556c9b, fb016d0 and final). Every such byte is visible at d556c9b too (the vs-d556c9b count is 0).
- R3 (1 trade), combinations (8-10, one pure in seed 21).

### 5d. C4: the verifier's 71,280-shape grid (`tools/b1grid.py` + `b1grid_cls.py`) against both references
```
-- reference d556c9b
shapes: 71280 {'closed': 27632, 'both_leak': 23130, 'both_ok': 20518, 'new_leak': 0, 'nonidem_new': 0}
both-leak by value: {'v7': 11565, 'v1': 11565}
not explained by the 8-char floor: 0
-- reference fb016d0
shapes: 71280 {'closed': 736, 'both_leak': 23130, 'both_ok': 47414, 'new_leak': 0, 'nonidem_new': 0}
both-leak by value: {'v7': 11565, 'v1': 11565}
not explained by the 8-char floor: 0
```
The d556c9b row equals the verifier's FIX-B figure ("fixb {'closed': 27632, 'both_leak': 23130, 'new_leak': 0, 'nonidem_new': 0}").
The 736 closed against fb016d0 are R-3. B1's eight V-1 rows stay closed: `test_v1_name_swallowed_by_sk_or_bearer_frees_no_value`
and `test_v1_row_no_value_byte_reaches_the_ledger_file`, 8 + 8, are in the 177 passed.

### 5e. C5: idempotence, goldens, probe, cost
```
=== idem5 2026-09-24T04:17:59Z new=2d5cf0072469            (tools/idem5.py; SEED=77 with the special letters, then ASCII=1 SEED=78)
{'new states': 20000, 'fixa states': 20000, 'fixb states': 20000}
{'new states': 20000, 'fixa states': 20000, 'fixb states': 20000}
```
0 NON-IDEMPOTENT in 40,000 states (the tool prints a `new NON-IDEMPOTENT` key for any failure). The field sweeps above
(17,078 + 17,928 rows, every bounded field at every cut) show no `NON-IDEM(new)` either.
Goldens and probe (`/tmp/j113s/v/b4_mine.py`: my own, since `b4_worker.py` hardcodes the shared tree; each tree imported in
its own subprocess, the import path asserted):
```
ap.violates_row      fixture=594584bde9869086 d556c9b=594584bde9869086 fb016d0=594584bde9869086 mine=594584bde9869086 variant(mine)=594584bde9869086 all-equal=True
b1.finding_kind      fixture=9e18ed7e5146a2c3 d556c9b=9e18ed7e5146a2c3 fb016d0=9e18ed7e5146a2c3 mine=9e18ed7e5146a2c3 variant(mine)=9e18ed7e5146a2c3 all-equal=True
b1.finding_sev       fixture=8c42d5dd1e8c349e d556c9b=8c42d5dd1e8c349e fb016d0=8c42d5dd1e8c349e mine=8c42d5dd1e8c349e variant(mine)=8c42d5dd1e8c349e all-equal=True
b2.hit_role          fixture=3ced4cd39a61faa5 d556c9b=3ced4cd39a61faa5 fb016d0=3ced4cd39a61faa5 mine=3ced4cd39a61faa5 variant(mine)=3ced4cd39a61faa5 all-equal=True
d1.bug_echo_scores   fixture=5a8c4ad2659c0e6b d556c9b=5a8c4ad2659c0e6b fb016d0=5a8c4ad2659c0e6b mine=5a8c4ad2659c0e6b variant(mine)=5a8c4ad2659c0e6b all-equal=True
v1.finding_class     fixture=f41a299c4a38ab30 d556c9b=f41a299c4a38ab30 fb016d0=f41a299c4a38ab30 mine=f41a299c4a38ab30 variant(mine)=f41a299c4a38ab30 all-equal=True
wf.drift             fixture=a51a56c48e98cca6 d556c9b=a51a56c48e98cca6 fb016d0=a51a56c48e98cca6 mine=a51a56c48e98cca6 variant(mine)=a51a56c48e98cca6 all-equal=True
probe states: 226 | mine==fb016d0: 226 | mine==d556c9b: 226 | refused(mine): 0 | idempotent(mine): 226
```
No golden digest changes, and `test_golden_digests_exact` is in the 177 passed.
Cost (`/tmp/j113s/v/cost_r3.py`: the verifier's `cost6.py` generators, plus 8 aimed at the merge step; best of 5 `.sub` per
size under a 10 s alarm; PIN = d556c9b, FB = fb016d0, NEW = final; times in ms; ratios per doubling):
```
=== cost_r3 2026-09-24T04:25:43Z NEW=2d5cf0072469 PIN=d556c9b FB=fb016d0; uptime:  04:25:43 up 1 day,  4:28,  0 user,  load average: 0.93, 1.16, 1.53; nproc=4
generator                                          mod       16k     32k     64k    128k    256k  (ms)  ratios per doubling
sk many heads, each a 1000-char head-free value    NEW      2.47    4.93    9.83   19.88   38.95  2.00 1.99 2.02 1.96
sk one head, one huge head-free value              NEW      2.77    7.58   13.80   20.96   42.58  2.74 1.82 1.52 2.03
sk one head, huge NAME= value (branch A scan)      NEW      2.29    4.64    9.32   19.25   39.10  2.03 2.01 2.07 2.03
sk one head, huge token run (branch C scan)        NEW      1.94    3.92    7.75   15.50   31.25  2.03 1.97 2.00 2.02
sk run of near-heads KE                            NEW      2.60    5.23   10.35   21.01   42.25  2.01 1.98 2.03 2.01
sk run of near-heads PASSWOR                       NEW      2.84    5.70   11.47   23.22   47.72  2.00 2.01 2.02 2.06
sk run of near-heads API_KE / token_               NEW      2.77    5.49   11.02   22.26   45.46  1.98 2.01 2.02 2.04
sk head, value of near-heads KEY"x (A scan)        NEW      2.71    5.39   10.97   22.59   46.68  1.99 2.04 2.06 2.07
sk head, value of near-heads PASSWOR:              NEW      2.68    5.44   11.01   23.29   47.85  2.03 2.03 2.11 2.05
sk repeated 'sk-abcdefghPASSWORD=QZ8 '             NEW      1.41    2.87    5.69   11.38   23.84  2.04 1.98 2.00 2.09
bearer many heads, each a 1000-char value          NEW      2.55    5.16   10.30   20.85   40.28  2.02 1.99 2.03 1.93
bearer one head, one huge head-free value          NEW      2.55    5.05   10.08   20.80   43.24  1.98 2.00 2.06 2.08
bearer one long run of near-heads token.           NEW      2.71    5.45   10.71   21.91   46.71  2.01 1.96 2.05 2.13
bearer one head, huge value of 'bearerx'           NEW      2.72    5.43   11.18   22.58   47.42  2.00 2.06 2.02 2.10
R3 sk head, glued merge, huge head-free bearer run PIN      0.01    0.02    0.05    0.10    0.20  2.01 1.99 2.00 1.98
R3 sk head, glued merge, huge head-free bearer run FB       0.02    0.03    0.05    0.10    0.20  1.82 1.89 1.94 2.00
R3 sk head, glued merge, huge head-free bearer run NEW      2.36    4.75    9.50   19.01   37.91  2.01 2.00 2.00 1.99
R3 sk head, glued merge, bearer run of near-heads  PIN      0.01    0.02    0.05    0.10    0.20  2.01 1.99 2.00 1.99
R3 sk head, glued merge, bearer run of near-heads  FB       0.01    0.03    0.05    0.10    0.20  1.85 1.87 1.95 1.97
R3 sk head, glued merge, bearer run of near-heads  NEW      2.95    7.86   14.82   21.93   44.05  2.66 1.89 1.48 2.01
R3 sk head, glued merge, run of consumed heads     PIN      0.01    0.02    0.05    0.10    0.20  2.01 1.99 2.00 1.99
R3 sk head, glued merge, run of consumed heads     FB       0.01    0.03    0.05    0.10    0.20  1.84 1.91 1.96 1.97
R3 sk head, glued merge, run of consumed heads     NEW      0.02    0.03    0.06    0.11    0.20  1.59 1.79 1.87 1.90
R3 sk head, one scan across many merges            PIN      0.01    0.02    0.05    0.10    0.13  2.01 1.99 1.99 1.34
R3 sk head, one scan across many merges            FB       0.01    0.03    0.05    0.07    0.20  1.83 1.92 1.32 2.89
R3 sk head, one scan across many merges            NEW      2.73    5.47   10.91   21.83   43.88  2.00 2.00 2.00 2.01
R3 sk many heads, each glued to a merge            PIN      0.05    0.10    0.19    0.40    0.78  1.99 1.87 2.08 1.96
R3 sk many heads, each glued to a merge            FB       0.98    1.93    3.93    7.84   15.56  1.98 2.03 2.00 1.99
R3 sk many heads, each glued to a merge            NEW      2.11    4.23    8.42   17.09   34.20  2.00 1.99 2.03 2.00
R3 sk near-merge words (bearer, short run)         PIN      0.01    0.02    0.05    0.10    0.20  2.01 2.00 2.00 1.99
R3 sk near-merge words (bearer, short run)         FB       0.01    0.03    0.05    0.10    0.20  1.83 1.90 1.94 1.98
R3 sk near-merge words (bearer, short run)         NEW      0.02    0.03    0.05    0.10    0.20  1.80 1.89 1.93 1.97
R3 bearer chain, each yield glued to a merge       PIN      0.21    0.41    0.84    1.67    3.34  1.99 2.04 1.99 2.00
R3 bearer chain, each yield glued to a merge       FB       1.90    3.81    7.58   15.35   30.88  2.01 1.99 2.03 2.01
R3 bearer chain, each yield glued to a merge       NEW      4.55    9.09   18.32   36.64   74.03  2.00 2.02 2.00 2.02
R3 bearer yield, merge with a bearer run of heads  PIN      0.09    0.17    0.35    0.70    1.40  1.99 2.00 2.01 2.02
R3 bearer yield, merge with a bearer run of heads  FB       0.09    0.18    0.35    0.72    1.44  1.90 1.96 2.04 2.00
R3 bearer yield, merge with a bearer run of heads  NEW      0.10    0.19    0.36    0.72    1.42  1.84 1.93 2.01 1.97
max ratio per doubling: {'PIN': 2.75, 'FB': 2.89, 'NEW': 2.74}
_redact_str sk head, value of near-heads KEY"x (A sc PIN      2.02    4.38    8.23   16.15   32.66  2.17 1.88 1.96 2.02
_redact_str sk head, value of near-heads KEY"x (A sc FB       2.30    4.52    9.16   18.48   36.90  1.97 2.02 2.02 2.00
_redact_str sk head, value of near-heads KEY"x (A sc NEW      2.93    5.65   11.68   23.96   48.65  1.93 2.07 2.05 2.03
_redact_str bearer one head, huge value of 'bearerx' PIN      1.70    3.40    6.76   14.98   27.62  2.00 1.99 2.22 1.84
_redact_str bearer one head, huge value of 'bearerx' FB       2.67    5.36   10.74   21.54   44.66  2.01 2.00 2.01 2.07
_redact_str bearer one head, huge value of 'bearerx' NEW      3.84    7.01   14.48   30.00   60.24  1.83 2.07 2.07 2.01
_redact_str sk many heads, each a 1000-char head-fre PIN      1.60    3.20    6.60   13.29   30.41  1.99 2.07 2.01 2.29
_redact_str sk many heads, each a 1000-char head-fre FB       2.69    6.04   11.73   21.77   42.55  2.24 1.94 1.86 1.95
_redact_str sk many heads, each a 1000-char head-fre NEW      3.31    6.54   13.25   26.32   52.83  1.98 2.03 1.99 2.01
_redact_str R3 sk head, one scan across many merges  PIN      1.54    2.99    6.10   12.14   24.58  1.94 2.04 1.99 2.03
_redact_str R3 sk head, one scan across many merges  FB       2.46    4.89    9.96   19.45   39.62  1.99 2.04 1.95 2.04
_redact_str R3 sk head, one scan across many merges  NEW      5.29   10.74   21.18   42.66   85.09  2.03 1.97 2.01 1.99
_redact_str R3 bearer chain, each yield glued to a m PIN      1.27    2.42    4.93    9.54   19.14  1.90 2.04 1.94 2.01
_redact_str R3 bearer chain, each yield glued to a m FB       2.74    5.09   10.13   20.44   40.87  1.86 1.99 2.02 2.00
_redact_str R3 bearer chain, each yield glued to a m NEW      5.63   11.19   22.16   44.21   90.20  1.99 1.98 1.99 2.04
```
Two single-step outliers for NEW (2.74 and 2.66 at 16k->32k, each followed by 1.82/1.52 and 1.89/1.48) were re-measured
alone, best of 7, twice (`/tmp/j113s/logs/FINAL_cost_r3_remeasure.log`):
```
2026-09-24T04:26:11Z re-measure, NEW _SK.sub, best of 7, twice
sk one head, one huge head-free value                   2.46    4.80    9.74   20.40   42.57  ratios 1.95 2.03 2.10 2.09
sk one head, one huge head-free value                   2.38    4.84   10.11   20.66   41.66  ratios 2.03 2.09 2.04 2.02
R3 sk head, glued merge, bearer run of near-heads       2.71    5.49   10.92   21.82   43.96  ratios 2.02 1.99 2.00 2.02
R3 sk head, glued merge, bearer run of near-heads       2.76    5.46   11.00   21.93   43.83  ratios 1.98 2.01 1.99 2.00
```
Linear. In the worst case `_redact_str` on a merge chain costs about 2x fb016d0 (87-92 ms against 40-42 ms at 256k), and the
other generators 1.2-1.3x. `test_env_assignment_redaction_does_not_backtrack_exponentially` is in the 177 passed.

## 6. Gates in the clone after the single write (`/tmp/j113s/logs/clone_gates.log`; the scratch copy's own runs: `scratch_gates.log`)

The write (2026-09-24T04:27:21Z): the three files were copied from `/tmp/j113s/work` once. The blob ids match the scratch copy's
(2d5cf0072469, 733fe70b705b, 9900d9648fb8).
```
=== clone gates 2026-09-24T04:27:36Z HEAD=ff7a671 volatile=2d5cf0072469
/tmp/j113s/wt/src/agent_factory/decisions/volatile.py
decisions run 1 rc=0 :: 177 passed in 3.85s :: PASSED-lines=177 sha=4de926ecf032da97
decisions run 2 rc=0 :: 177 passed in 3.71s :: PASSED-lines=177 sha=4de926ecf032da97
2 files set=16a7b628685e
harvest run 1 rc=0 :: 33 passed in 10.52s
harvest run 2 rc=0 :: 33 passed in 11.36s
1 files set=87e28761f102
pyflakes-rc=0
--- repro (after the write)
volatile: /tmp/j113s/wt/src/agent_factory/decisions/volatile.py
R-1 body-in-ledger-line=False state.msg='Authorization: <redacted:bearer>'
R-2 body-in-ledger-line=False state.msg='<redacted:sk> QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8ıpassword: <redacted:envval>'
R-4 body-in-ledger-line=False state.msg='ta<redacted:sk>:QZJ8QZJ8<redacted:bearer>token: <redacted:envval>'
R-3 body-in-ledger-line=False state.msg='ta<redacted:sk>PASSWORD= <redacted:envval>'
replayed rows: 4
repro rc=0
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---
--- TEST_SCREEN over 2 path(s): 1 hits over 2 files ---
AP-70: 1
    tests/test_decisions_ledger.py:1292: except Exception:
no_laya rc=0 :: no_laya_in_gates: 40 files scanned, clean
end 04:28:07Z
```
In the scratch copy before the write (2026-09-24T04:26:27Z, the same blobs): `run 1 rc=0 :: 177 passed in 3.63s :: PASSED-lines=177
sha=4de926ecf032da97`, `run 2 rc=0 :: 177 passed in 3.68s :: PASSED-lines=177 sha=4de926ecf032da97`, `harvest run 1: 33 passed in 8.96s`,
`harvest run 2: 33 passed in 8.42s`.
The PIN's own tests (`git archive d556c9b tests/test_decisions_canonical.py tests/test_decisions_ledger.py`, blobs 0afbf1b821ed /
4a8bccead05f) on the final code, plus the import guard (`/tmp/j113s/logs/FINAL_pin_own_tests.log`):
```
=== PIN's own tests (d556c9b 0afbf1b821ed/4a8bccead05f) + guard on the final code 2026-09-24T04:26:53Z volatile=2d5cf0072469
73 passed in 2.39s
```
ap_screen at the head (the clone before the write, bf04415d72c1) printed the same two lines: `0 hits over 1 files`, and
`1 hits … AP-70` at `tests/test_decisions_ledger.py:1292` ("except Exception:"). So there are 0 new hits; the one AP-70 hit is the
PIN's own line (my rows are appended after it). `no_laya_in_gates` before the write: `rc=0`, `no_laya_in_gates: 40 files scanned,
clean`.
pyflakes rc=0 on the three files; the 177 are in set 16a7b628685e; the adjacent consumer's 33 (set 87e28761f102) equal the PIN's
`33 passed`.

## 7. Per contract line

| line | status | where | evidence |
|---|---|---|---|
| C1 R-1, R-2, R-4 close | DONE | `src/agent_factory/decisions/volatile.py:70` `_BEARER_RUN` and `src/agent_factory/decisions/volatile.py:108-110` (R-1); `src/agent_factory/decisions/volatile.py:87` (R-2) and `src/agent_factory/decisions/volatile.py:83-85` (R-4), both in the scans that end in `_ASSIGNMENT_HEAD`; `src/agent_factory/decisions/volatile.py:103-107` `_BEARER_MERGE` (R-4) | the repro: `body-in-ledger-line=False` x4 (section 6); the case files R-1 10/10, R-2 4/4, R-4 5/5 with the checked body absent, `replay` OK, idem (5a); the tests `test_r1_bearer_run_takes_the_pin_letters` … (`tests/test_decisions_canonical.py:1221-1239`) and `test_r1_bearer_token_bytes_never_reach_the_ledger_file` … (`tests/test_decisions_ledger.py:1681-1698`) RED at fb016d0, GREEN after (section 3); the field sweeps (5a) |
| C2 R-3 `NAME= v` closes; `NAME==v` declared | DONE | `src/agent_factory/decisions/volatile.py:84` `_ENVVAL_HEAD` | R3-a/b/c `body-in-line PIN=True NEW=False`; the tests `c::r3` `:1240`, `l::r3` `:1699` RED at fb016d0, GREEN after; the grid closes 736 against fb016d0; the `==` residue in section 8, not pinned by any test |
| C3 the three survivors die | DONE | tests `c::c3` `:1246`, `l::c3` `:1705` | m5 (V-M3), m6 (V-M11), m7 (V-M4) KILLED, each by its own row in both files; the killers pass unmutated (section 4) |
| C4 no regression against d556c9b | DONE | — | the differential 0 BODY in 6/6 runs; grid `new_leak: 0`; B1's 8+8 V-1 tests pass |
| C4 no regression against fb016d0 | **NOT MET** | — | the differential 20/13/20 and 238/261/257 inputs; grid `new_leak: 0`. DISCREPANCY D-1 |
| C5 invariants | DONE | placeholders, refusal texts, schemas, limits, `canonical()`, row shape, D-1 order untouched (section 2) | idem 0 of 40,000; the goldens unchanged (7/7 + variants); probe 226 == both refs; cost linear (5e); the PIN's 72 pass |
| C6 comments true | DONE | `src/agent_factory/decisions/volatile.py:5-6` `AMENDMENT 3, D-059`, `src/agent_factory/decisions/volatile.py:46-63` `_BEARER_RUN`, `src/agent_factory/decisions/volatile.py:74-81` `_ENVVAL`, `src/agent_factory/decisions/volatile.py:91-102` `_TOKEN` | the three falsified statements rewritten (section 2 table); the new step's comment states its depth-2 limit |
| tests RED at the head, GREEN after | DONE for the R rows; NOT POSSIBLE for C3/C4 controls | section 3 | 30 of 56 new tests red at fb016d0; the 26 green ones pin behaviour the head already has. DISCREPANCY D-3 |
| mutation audit m1-m7 + the builder's 30 | DONE | section 4 | 58 of 58 killed (m1-m7, m3b, 30 builder, 10 verifier, 10 lane) |
| report lint | see section 14 | | |

## 8. Declared residues (each measured; none hidden)

- **`NAME==v` behind sk or bearer (C2's declared residue).** `R3-f task-PASSWORD==v (padding form)   body-in-line PIN=True
  NEW=True idem=True` (5a). The verifier's sweep: `R3-padding {'ok/ok': 576, 'leak/leak': 597}`, leaking in 21 fields. It leaks
  at d556c9b, fb016d0 and the final code alike. Branch A's padding rule `(?=[^\s=])`, written for bearer's `=*`, also stops the
  sk run, which has no padding. No test pins it.
- **The chain family (KNOWN: AF-AP-157 F-1/D-3, task #198).** In a chain, the first value (V1, or a token run) keeps the PIN's
  output and stays visible, as at d556c9b: `RUN-in-line PIN=True NEW=True` for R2-a/b/c/ctl, `V1-in-line PIN=True NEW=True` for
  R4-a/b/c (5a). The new R-2/R-4 rows put a plain word (`plainval`) or `ab`*16 there and pin the exact output, as the `chain-*`
  rows already do (`tests/test_decisions_canonical.py:912-920`, the `chain-widened` … `chain-token-run` rows).
- **Values fb016d0 hid only by the accident of R-1/R-2/R-4** show again, as at d556c9b (D-1; 5c).
- **The conservative head rule on a merged value** (the R4 "pure" bucket): a merged tail whose head has a glued value, or a
  token head, is refused like the same shape without a merge.
- **The step's depth-2 limit** (`src/agent_factory/decisions/volatile.py:98-101`, "The replayed run yields to a"): the replayed bearer run yields to a `_YIELD` without the step. A bearer
  glued inside the stepped bearer's own value can therefore make a scan refuse where the bearer pass later consumes the head.
  The run then keeps its PIN form, never showing a byte d556c9b hides. Not measured separately; the differential (0 BODY
  against d556c9b) covers it statistically.
- **The widened form's 8-character floor (A4, by design):** the grid's `both-leak by value: {'v7': 11565, 'v1': 11565}`,
  `not explained by the 8-char floor: 0` (5d).
- **D-1's `keyname` class** (a key's tail that spells a name): `newly:keyname+pad` 24-35 per 20,000 against d556c9b, the
  coordinator's accepted class (VERIFY-J1-1-R2 finding 5).

## 9. DISCREPANCIES (flagged loudly; each needs the coordinator)

- **D-1. C4 against fb016d0 is NOT met, and a guard-level change cannot meet it together with C1.** Measured newly visible
  BODY inputs against fb016d0: 20 / 13 / 20 (ASCII) and 238 / 261 / 257 (special letters) of 20,000 each; against d556c9b
  0 in all six (5b).
  - Every exposure is attributed to one of the contract's own fixes (5c): R-1 221 / 247 / 238, R-4 6-20 per seed, R-3 1,
    combinations 8-10.
  - 235-257 of each special-letter run and 7 of each ASCII run are trades: a secret byte fb016d0 showed is now hidden.
  - The rest ("pure": 13 / 6 / 13 ASCII, 3 / 4 / 3 special) are all attributed to R-4, except one combination in seed 21. The
    inspected examples are the design's conservative chain rule applied to the merged value (INFERRED for the rest).
  - Every exposed byte is visible at d556c9b too.
  - Why it is infeasible: on a true chain, d556c9b hides V2 and fb016d0 hides V1, so "every value either redacts" needs both
    hidden. A yield guard has only two outputs: yield (V2 freed, C1 violated) or no yield (V1 shown, the PIN form). Hiding both
    needs a value class that stops at a head or at the bearer placeholder: task #198's rule, measured by the verifier as
    opening a stub-exposure class (its section 9). That is a redesign of the redaction pass, which D-059 leaves to the owner
    (PATH-2).
  - Options for the coordinator: (a) amend C4 to "no body byte d556c9b hides becomes visible, and against fb016d0 only the
    attributed R-1/R-2/R-4/R-3 classes", which this change meets with the pasted evidence; (b) the redesign.
- **D-2. FIX-A was improved, not adopted as written.** Its R-4 line (a `(?i:bearer)\s` head in all three scans) refuses a
  yield wherever a value runs into the word `bearer`. That includes a bearer that never matches (a run under 16), a merge with
  no head after it, and the token branch, whose run cannot cross `<`. Pure regressions against fb016d0 per 20,000: FIX-B 69
  (ASCII) / 31 (special) against the final 13 / 3 (section 1b). The replacement is a step over the real merge (section 2).
  n6 (FIX-A's line as written) is a KILLED mutant: 9 tests, among them the C4 controls merge-no-head, short-bearer-no-merge and
  token-run-glued-to-bearer.
- **D-3. "Each new test RED at the head" cannot hold for 26 of the 56 new tests** (13 per file). These are the four class
  controls, the four C3 rows and the five C4 controls. They pin behaviour fb016d0 already has; the verifier says so of the C3
  rows ("The behaviour they guard is right today; the tests do not pin it"). Their negative controls are mutants (killer sets
  from `/tmp/j113s/mut/mut_*.json`):
  - C3: m5-m7 and V-M10.
  - The C4 controls: n2, n3, n6, n9, n10, V-M6 and V-M7.
  - The R-1/R-2 ASCII controls: V-M1, V-M2, b-m4d3, b-m4e3, b-m4j, b-m4n-PASSWORD.
  - The R-4 control: V-M1, b-m1, b-m4b, b-m4g, b-m4n-PASSWORD.
  - The R-3 control (`DB_PASSWORD= <body>`): no mutant in the table kills it. It pins `_ENVVAL_WIDE`'s own `NAME= v`
    handling, which this change does not touch, and it is green at d556c9b and fb016d0 as well.
- **D-4. Two killing rows beyond C3.** V-M6 and V-M10 survived the first audit. On my code each frees a value on rare
  generator inputs (section 4), so both were closed: `head-the-bearer-consumes` now carries a 7-character value, and the row
  `V-M10-upper-apikey-chain` is new. Both edits stay inside the test boundary; C3 named only V-M3, V-M11 and V-M4.
- **D-5. The builder's 30-mutant table is translated, not replayed byte for byte.** The texts it mutated no longer exist (the
  `_YIELD` literal became `_yield_pattern`). Each row removes the same element from the new structure, at both depths (4).
  The brief's "line 61 -> R-4" row (m1) reverts the step (`_YIELD = _yield_pattern(r"(?!)")`), because `_ASSIGNMENT_HEAD`
  (`src/agent_factory/decisions/volatile.py:68`, `_ASSIGNMENT_HEAD = _SECRET_NAME`) is unchanged in this form.
- **D-6. Venue and instruments.**
  - The sandbox private clone `/tmp/j113s/wt` replaces the shared tree and the PC, per the coordinator's lane instructions.
    `/tmp/j113/…` maps to `/tmp/j113s/…`.
  - The verifier's tools are used from path-only copies in `/tmp/j113s/v/tools`
    (`diff -r` against the lane-patch copies: every changed line is a path, plus `import os` and the `VREF`/`VNEW`
    environment overrides in `vload.py`). `/tmp/vj11r2` was read, never written or run in place.
  - `b4_worker.py` is not used (it hardcodes the shared tree); `/tmp/j113s/v/b4_mine.py` replaces it.
  - Mine, labelled as mine: `explore1.py`, `tri3.py`, `attr3.py`, `same_out.py`, `fieldsweep_r3.py` (a SHAPES-only variant),
    `cost_r3.py` (cost6 + 8 generators), `mutr3.py`, `surv.py`, `surv_show.py`, `b4_mine.py`, `/tmp/j113s/mktree.sh`.
- **D-7. `/tmp/vj11r2` was meant to stay read-only; Python wrote into it.** My scripts loaded the verifier's
  `fixa/volatile.py` and `fixb/volatile.py` by path (`explore1.py` at 03:09:56Z, then `tri3.py` and `same_out.py`). Python's
  import machinery then created `/tmp/vj11r2/fixa/__pycache__/volatile.cpython-311.pyc` and the same under `fixb/`. The 30
  verifier files are still byte-identical to the lane-patch copies (sha256, `files=30 diff=0`, rechecked at the end). I did
  not delete the two cache directories: deleting would be a second modification of a directory that is not mine. The
  coordinator may remove them. `/tmp/j113` was never touched (no file newer than 03:00Z).

## 10. Adjacent findings (reported, not fixed)

- **A-1. A token run that shrinks under a merge.** The token branch yields on the pre-merge run (32+ with the word `bearer`
  glued on). After the bearer pass the run is under 32, and no class takes it. Pre-existing at all three
  (`/tmp/j113s/logs/adjacent_A1.log`):
  `'sk-abcdefgh-token QZJ8…(28)bearer abcdefghijklmnop'` run-visible d556c9b=True fb016d0=True final=True;
  the 32-character control: d556c9b=True fb016d0=False final=False.
- **A-2. The verifier's V-M6 and V-M10 are not body-neutral.** Its report (section 8, finding 7) says they change no body
  byte. On my code V-M6 frees V1 in 2 of 20,000 generator inputs per mode and V-M10 frees V2 in 1 (section 4). Both are trades,
  not uniformly worse: V-M10 also hides a body byte my code shows on 21 (ASCII) and 11 (special) inputs, V-M6 on 1 and 4
  (`/tmp/j113s/logs/survivors.log`). Not measured on fb016d0.
- **A-3. The conservative chain rule over-refuses glued chains** whose second value the outer value would swallow whole:
  `task-password:abcdefghkey=X4Z9X4Z9` -> `ta<redacted:sk>:abcdefghkey=<redacted:envval>` (`abcdefgh` visible) at d556c9b,
  fb016d0 and final. This belongs to #198's design space.
- **A-4. Cost.** `_redact_str` on the merge-chain generators takes about 2x fb016d0 (87-92 ms against 40-42 ms at 256k); it
  stays linear.
- **A-5. Statements outside my boundary** (VERIFY-J1-1-R2 section 12), untouched:
  - `tasks/briefs/laya/J1-1-R2-report.md:98` ("cannot expose a body byte the PIN redacts").
  - `tasks/briefs/laya/J1-1-R2-report.md:239` ("Each class fires where its PIN form fires").
  - `tasks/briefs/laya/J1-1-R2-report.md:542` ("Over 160,000 fuzz inputs these are the ONLY PIN-redacted bytes"): all three
    falsified by R-1, R-2 and R-4.
  - `todo/BUILD-TASKLIST.md:1352` ("J1-1-R2 HOME AND LANDED"; it quotes the lane's 160,000-input fuzz).
  - The verifier's `docs/INCIDENT-LOG.md` item is already amended at this PIN: `docs/INCIDENT-LOG.md:586` (`AF-AP-157`) names
    R-3 and "increment B (`volatile.py`) is J1-1-R3". After this change R-3's `NAME= v` form is closed and `NAME==v` is not;
    updating that row is the coordinator's.

## 11. NOT done (first-class)

- C4 against fb016d0 (D-1): not met. It waits on the coordinator's amendment or the owner's redesign decision.
- The `NAME==v` padding residue: not fixed (declared, section 8).
- No git add, commit, stash or push; no PR, issue or comment; no incident-log, wiki or ledger entry (the coordinator's).
  The clone stays in place with the unstaged diff.
- Not measured: how often the residue and trade shapes occur in real ledgers or documents; V-M6/V-M10 on fb016d0; the step's
  depth-2 limit on its own; the full-tree suite (not asked; the gates are the two decision files and the harvest suite).
- No PC or bridge use; no subagent.

## 12. Self-attack: the three likeliest ways this change is wrong

1. **The step mis-emulates the bearer pass, so the guard misjudges.** The step shares the pass's literal, its run class
   (`_BEARER_RUN`) and its 16-character lookahead; the mutants that split them (m3, n7, n8, n9) are killed. Its replayed yield
   is the same `_yield_pattern` without the step. Depth-1 yields are a subset of depth-0 yields, so a mismatch can only refuse
   more, and a refusal gives d556c9b's output. Measured: 0 BODY exposures against d556c9b in 120,000 inputs, grid
   `new_leak: 0` against both references, and 35,006 sweep rows with no `ok->LEAK`. Residual: shapes outside the generators
   (three or more glued bearers) are covered by the argument, not by an exhaustive measurement.
2. **The nested pattern backtracks exponentially.** A yield sits inside a step inside a yield. Against that: the replayed run
   is possessive, and each scan still stops at its first head or terminator. 22 cost generators, 8 of them aimed at the step,
   are linear to 256k (outliers re-measured), and `test_env_assignment_redaction_does_not_backtrack_exponentially` is green.
   Residual: an adversarial input outside the generators.
3. **D-1 is misread, and C4 was meant to be met as written.** The lane is then NOT-READY on C4 by construction: no guard-level
   form can hide both values of a chain. Against that: the trade/pure split and the attribution are mechanical (`attr3.py`),
   every exposure traces to a contract fix, and the cheapest alternative (FIX-A as written) is measured worse on the same
   metric (D-2). The decision stays the coordinator's.

## 13. Evidence tiers

- VERIFIED (run in this lane, output pasted): the premise (0); RED/GREEN (3); the mutation audit, 58 of 58 killed, with killer
  sets green unmutated (4); the case files, sweeps, differential, attribution, grid, idempotence, goldens, probe and cost (5);
  the gates in the scratch copy and the clone, with the repro (6); the equivalence of K2 and the final form over 80,000 inputs
  (1b); A-1, A-2 and A-3.
- INFERRED: the step's depth-2 limit refuses and never exposes (argument in 12.1); linear cost beyond 256k; that each R4 "pure"
  exposure is a glued-tail or token-head chain (examples inspected, `/tmp/j113s/v/out/attr3_*.json`; the pure/trade split itself
  is mechanical).
- ASSUMED: nothing load-bearing. The rarity of the residue shapes in real text is NOT claimed (not measured).

## 14. Report lint (`python3 scripts/report_lint.py --min-refs 10 tasks/briefs/laya/J1-1-R3-report.md`; at most three fix rounds)
```
round 1 (first run):  report_lint: 8 refs — OK 1, NEAR 1, MISS 2, UNCHECKABLE 4, UNRESOLVED 0 (worktree)
                      report_lint: FLOOR — OK 1 < --min-refs 10: the report cites too little to be graded        (rc=1)
fix round 1 -> run 2: report_lint: 51 refs — OK 47, NEAR 1, MISS 1, UNCHECKABLE 2, UNRESOLVED 0 (worktree)         (rc=1)
fix round 2 -> run 3: report_lint: 61 refs — OK 57, NEAR 0, MISS 3, UNCHECKABLE 1, UNRESOLVED 0 (worktree)         (rc=1)
fix round 3 -> final: report_lint: 62 refs — OK 61, NEAR 0, MISS 0, UNCHECKABLE 1, UNRESOLVED 0 (worktree)         (rc=0)
UNCHECKABLE  report:552   tests/test_decisions_ledger.py:1292      no claim token on the report line   (inside pasted ap_screen output; left verbatim)
```
Fix round 1 wrote short references (`volatile.py:NN`, bare `:NN`) as repo paths, each with an identifier from its range. It
pinned head-era lines as `@ff7a671`, and moved the stale A-5 citations to their lines at this PIN. The NEAR it found was a
real error of mine: the comment reflow (section 1, final form) moved `_BEARER_MERGE`, `_YIELD` and `_BEARER` down one line,
and the section 2 table was corrected to `:103-106`, `:107` and `:108-110`. Fix rounds 2 and 3 added same-line tokens.
Disclosure: re-linting the report after this paste gives `63 refs — OK 61, NEAR 0, MISS 1, UNCHECKABLE 1` (rc=1). The one
MISS is the quoted UNCHECKABLE line in the block above: the linter reads it as a new reference whose line holds no token
from the cited code line. The fix-round budget is spent, so the paste stays verbatim.
