# VERIFY-J1-1-R3 — report (task #216 verifies task #202)

STATUS: COMPLETE (2026-09-24). GATE RECOMMENDATION: NOT-READY (F-1, F-2: C4a hits reproduced through the ledger; section 14).

Lane: verify-j1-1-r3 (sandbox, agent `adversarial-verifier`, shared tree, no worktree). PIN 942ad5e. Brief
`tasks/briefs/laya/VERIFY-J1-1-R3-brief.md` (committed 7aa7f35). Contract: D-059 (AMENDMENT 3) as amended by D-067, C1-C6 of
`tasks/briefs/laya/J1-1-R3-brief.md` with C4 replaced by C4a/C4b. Scratch: `/tmp/vj113r3/`. Written incrementally.

## 1. Premise (re-measured 2026-09-24 05:11:09Z..05:11:20Z)

Every line of the brief's premise block reproduced at the PIN, and the shared tree's four boundary blobs equal the PIN's blobs:

```
$ git rev-parse --short '942ad5e^{commit}'            -> 942ad5e
$ merge-base --is-ancestor 942ad5e origin/...         -> pin-is-on-origin
$ git log -1 942ad5e -- volatile.py                   -> fdac751 J1-1-R3 landed GATED-PENDING-VERIFY: ...
$ git ls-tree 942ad5e (V, TH, TC, TL)                 -> 2d5cf0072469 / bb0187044a6a / 733fe70b705b / 9900d9648fb8
$ git hash-object (shared tree, same four files)      -> 2d5cf0072469 / 733fe70b705b / 9900d9648fb8 / bb0187044a6a (identical)
$ git ls-tree d556c9b -- volatile.py                  -> 20ebcd54f3ed
$ git ls-tree fb016d0 -- volatile.py                  -> bf04415d72c1
$ pytest TC TL -q                                     -> 177 passed   (set=16a7b628685e, 2 files)
$ pytest tests/test_decide_harvest.py -q              -> 67 passed    (set=87e28761f102, 1 file)
$ grep anchors in V                                   -> 68 _ASSIGNMENT_HEAD, 69 _ENVVAL_HEAD, 70 _BEARER_RUN, 73 def _yield_pattern,
                                                         103 _BEARER_MERGE, 107 _YIELD, 108 _BEARER
$ grep -c '^| D-067 |' docs/08_DECISION_LOG.md        -> 1
$ ls -d /tmp/vj11r2/tools /tmp/j113s/v/tools          -> both present
```

HEAD of the shared tree was 7aa7f35 at 05:11Z (the brief commit, one commit after the PIN; later 67cb0fa, section 8); `git diff --stat 942ad5e HEAD -- src/ tests/` is
empty. PREMISE HOLDS — no CONTRACT-INVALID stop.

## 2. Item 2 — C4a, independently (my own generator; through `decision_state` and the ledger)

### 2a. Instruments (all mine; `/tmp/vj113r3/`)
- `gen113.py` — a grammar generator, five families (`special`, `seps`, `glue`, `chains`, `mix`). BODY = EVERY character of a
  secret value (sk run, bearer run, token run, assignment value), special letters and run punctuation included. This is
  stricter than the builder's `diff3.py`, whose `body` role excludes `special` and `tokchar` (bearer-alphabet) characters
  (read at `/tmp/j113s/v/tools/diff3.py`; its saved d556c9b hits hold none of those roles, so this changes nothing on its
  own inputs). Names (`name`, `keyname`, token-form `tname`), separators (`sep`, `quote`), padding (`pad`) and the `sk-`/`bearer`
  literals (`head`) are counted apart. Fake bodies only (letters with no name letter, digits, the special letters).
- Special letters: U+0130, U+0131, U+017F, plus U+212A (Kelvin), U+00B5, U+03C3, U+03C2, U+1E9E. A full code-point sweep
  (0x80..0x10FFFF) shows exactly four non-ASCII letters match the case-blind run classes: U+0130, U+0131, U+017F, U+212A, and NFC
  maps U+212A to `K`, so through `decision_state` only the first three survive (the comment at
  `src/agent_factory/decisions/volatile.py:49-50` "which normalize keeps" is true).
- `c4diff.py` — each input goes into one of the 21 text-carrying fields of the seven closed schemas (round-robin over
  `SCHEMAS`: `sym`, `file`, `snippet`, `kind`, `msg`, `class_slug`, `finding_title`, `lane`, `finding_id`, `title`, `paths`,
  `action_target`, `action_excerpt`, `row_id`, `row_title`, `expected`, `observed`); the four enum fields are fixed. Two
  instruments per module, asserted to agree: A = a class-preserving one-character swap in the RAW state, compared at
  `decision_state`'s output (black box); B = my own origin tracker (the module's normalize, its six compiled passes via
  `finditer` asserted equal to `_redact_str`, then the field's cut asserted equal to `decision_state`'s field). Every visible
  byte is split by why d556c9b hid it: `d556-redacted` (absent from d556c9b's uncut `_redact_str` output) or `d556-cut` (present
  there, beyond the field limit).
- `steps.py` prints each pass; `ledger_probe.py` runs a case list in a tree's OWN interpreter (`PYTHONPATH=<tree>/src`):
  `decision_state` -> `canonical` -> `make_row` -> `append` to a fresh file -> the file bytes -> `replay`.
- The seams tested (the PIN's line numbers):
  - `src/agent_factory/decisions/volatile.py:421` `def decision_state` (normalize -> redact -> bound, the one public composition)
  - `src/agent_factory/decisions/volatile.py:388` `def _redact_str` (the six passes in the D-1 order)
  - `src/agent_factory/decisions/volatile.py:111` `_SK` (its run guarded by `_YIELD`) and `src/agent_factory/decisions/volatile.py:108` `_BEARER` (the two class forms under test)
  - `src/agent_factory/decisions/ledger.py:335` `def make_row`, `src/agent_factory/decisions/ledger.py:432` `def append`
  - `src/agent_factory/decisions/ledger.py:507` `def replay`, `src/agent_factory/decisions/canonical.py:35` `def canonical`
- Trees: `git archive` of 942ad5e, d556c9b and fb016d0 into `/tmp/vj113r3/{pin,d556,fb01}` (volatile blobs 2d5cf0072469 /
  20ebcd54f3ed / bf04415d72c1; `ledger.py` 71fc398a5340 in all three). The shared passes (`_PRIVKEY`, `_ENVVAL`, `_TOKEN`,
  `_ENVVAL_WIDE`, `PLACEHOLDERS`) are asserted identical in the three modules.

### 2b. Run 1 (seed 11, 15,000 inputs per family; 2026-09-24 05:27:10Z..05:31:03Z)
Instrument disagreements: 0 in all 75,000 inputs x 3 modules (no `INSTRUMENT DISAGREE` key). Refusals: 0. PIN non-idempotent: 0.

| family | inputs | out differs vs d556c9b | newly visible vs d556c9b (inputs) | BODY `d556-redacted` | BODY `d556-cut` |
|---|---|---|---|---|---|
| special | 15000 | 961 | 957 | 0 | 44 |
| seps | 15000 | 2573 | 2516 | 0 | 99 |
| glue | 15000 | 2207 | 2167 | 0 | 115 |
| chains | 15000 | 1452 | 1413 | **2** | 93 |
| mix | 15000 | 1914 | 1885 | 0 | 66 |

The non-BODY newly visible bytes are names (the D-1 class: a name glued to a key run now shows) and separators. The `d556-cut`
bytes are NOT redacted by d556c9b: its redactor leaves them visible and only the field limit hides them; the PIN's shorter
output moves them inside the limit (finding F-5, INFO). **The two `d556-redacted` inputs are C4a hits.**

### 2c. The two C4a hits, reduced to pure-ASCII shapes (finding F-1 and F-2)
`python3 /tmp/vj113r3/steps.py` shows each pass. Two distinct mechanisms:

- **N-1 (hit 1, `v1.finding_class.title`): a widened-form name whose tail is an upper-case `KEY=`.** The sk/bearer run yields
  at `api_KEY=` / `ApiKEY=` / `APİ_KEY=` by the widened branch (`src/agent_factory/decisions/volatile.py:84-85`, its `_SECRET_NAME` alternative), whose exclusion
  `(?!" + _ENVVAL_HEAD + r"\S)` tests only the name's FIRST character, and whose chain scan stops at `"'&,;`. But `_ENVVAL`
  (`src/agent_factory/decisions/volatile.py:139`, `_ENVVAL = re.compile(`, case-sensitive, it runs before `_ENVVAL_WIDE`) takes
  the name's tail `KEY=` with a `\S+` value, which runs past the `"` and swallows the next head: its value is freed.
- **N-2 (hit 2, `b2.hit_role.sym`): an sk inside a glued bearer run.** The step `_BEARER_MERGE`
  (`src/agent_factory/decisions/volatile.py:103-106`, `_BEARER_MERGE`) replays the bearer run on the text the sk pass sees, before `_SK` has run.
  The real bearer pass runs after `_SK` and stops at the inner `<redacted:sk>`. When the inner sk run ends on a character the
  bearer run takes but the sk run does not (`.`, `~`, `+`, `/`, U+0130/U+0131/U+017F), the replay runs on past a head whose own
  value holds a second head (so it is no depth-0 yield), the scan sees no head, the run yields, and the widened value swallows
  that head in the real text: its value is freed. This is an R-4 shape the step does not close.

My minimal shapes (`/tmp/vj113r3/n_cases.py`; field `b1.finding_sev.msg` = `"set " + raw + " now"`; V3 = `X4Z9X4Z9X4Z9`):
```
== N1-sk-api_KEY 'sk-QZJ8QZJ8api_KEY=plainval"password: X4Z9X4Z9X4Z9'
   d556  V3-visible=False 'set <redacted:sk>=plainval"password: <redacted:envval> now'
   fb01  V3-visible=True  'set <redacted:sk>api_KEY=<redacted:envval> X4Z9X4Z9X4Z9 now'
   pin   V3-visible=True  'set <redacted:sk>api_KEY=<redacted:envval> X4Z9X4Z9X4Z9 now'
== N1-sk-ApiKEY 'sk-QZJ8QZJ8ApiKEY=plainval&secret: X4Z9X4Z9X4Z9'                 (d556 hides V3; fb01 and pin show it)
== N1-bearer-api_KEY 'Bearer QZJ8QZJ8QZJ8QZJ8api_KEY=plainval,token= X4Z9X4Z9X4Z9'    (d556 hides V3; fb01 and pin show it)
== N1-control-API_KEY 'sk-QZJ8QZJ8API_KEY=plainval"password: X4Z9X4Z9X4Z9'          (all upper: V3 hidden at all three)
== N1-sk-dotted-I 'sk-QZJ8QZJ8APİ_KEY=plainval;passwd : X4Z9X4Z9X4Z9'           (V3 visible at all three: not a regression)
== N2-dot 'sk-QZJ8QZJ8password:plainvalbearer abcdefghijklmnopsk-qqqqqqqq.secret = X4Z9X4Z9X4Z9token: plainvl2'
   d556  V3-visible=False 'set <redacted:sk>:plainval<redacted:bearer><redacted:sk>.secret = <redacted:envval> plainvl2 now'
   fb01  V3-visible=True  'set <redacted:sk>password:<redacted:envval> = X4Z9X4Z9X4Z9token: <redacted:envval> now'
   pin   V3-visible=True  'set <redacted:sk>password:<redacted:envval> = X4Z9X4Z9X4Z9token: <redacted:envval> now'
== N2-plus  ('+Secret = …key: …')  and  N2-tilde-key ('PASSWORD=…~key= …token: …')   (d556 hides V3; fb01 and pin show it)
== N2-control-no-inner-sk (the same shape without the inner "sk-")                  (V3 visible at all three: not a regression)
```
Through the real path (`ledger_probe.py`, 05:35:26Z, each tree's own interpreter; and again 05:35:38Z against the shared tree's
`src`, `PYTHONDONTWRITEBYTECODE=1`, ledgers under `/tmp/vj113r3/ledgers/`):
```
tree d556 (20ebcd54f3ed): N1-sk-api_KEY / N1-sk-ApiKEY / N1-bearer-api_KEY / N2-dot / N2-plus / N2-tilde-key
                          V3-in-state=False V3-in-line=False replayed=1 equal=True
tree pin  (2d5cf0072469): the same six   V3-in-state=True  V3-in-line=True  replayed=1 equal=True
shared tree src (2d5cf0072469): the same six V3-in-line=True replayed=1 equal=True (row_ids 3b4610097df5 5e9200629c26
                          eccd0abab839 e786ec091fa2 2a800aa043c1 ba61b9f2f3c6); controls N1-control-API_KEY V3-in-line=False
```
The ledger line on disk at the PIN (`/tmp/vj113r3/ledgers/pin/N1-sk-api_KEY.jsonl`) holds
`"msg":"set <redacted:sk>api_KEY=<redacted:envval> X4Z9X4Z9X4Z9 now"`, and `replay` accepts it.

Both are ALSO present at fb016d0 in these ASCII forms (the J1-1-R2 code): N-1 is a J1-1-R2 regression that neither
VERIFY-J1-1-R2 nor J1-1-R3 found (the builder's and the verifier's generators never draw a mixed-case `KEY` name); N-2 is R-4 left
open by the step. Neither is a KNOWN row: AF-AP-157's chain family (task #198) is the other direction (the guard refuses and the
first value keeps d556c9b's output); issue #47 (O-1, D-2, O-4) and issue #49 (V-2..V-6, V-12..V-16) hold no such row.

### 2d. All runs (seeds 11 and 22, five families; plus a targeted family `n12`, seed 11; 165,000 inputs)
Seed 22 ran 05:36:49Z..05:41:28Z; `n12` (names drawn 40% from `api_KEY`, `Api_KEY`, `apiKEY`, `ApiKEY`, `aPI_KEY`, `apI_KEY`,
`ApIKEY`, with glue and chains) in the same window. 0 instrument disagreements, 0 refusals, 0 PIN non-idempotent in every run.

| run | inputs | out differs vs d556c9b | newly visible vs d556c9b | **BODY `d556-redacted` (C4a)** | BODY `d556-cut` | vs fb016d0 BODY inputs (trade/pure) | of those, hidden at d556c9b: redactor / cut only |
|---|---|---|---|---|---|---|---|
| special_11 | 15000 | 961 | 957 | 0 | 44 | 540 (531/9) | 0 / 12 |
| seps_11 | 15000 | 2573 | 2516 | 0 | 99 | 405 (335/70) | 0 / 11 |
| glue_11 | 15000 | 2207 | 2167 | 0 | 115 | 648 (558/90) | 0 / 24 |
| chains_11 | 15000 | 1452 | 1413 | **2** | 93 | 653 (598/55) | **1** / 20 |
| mix_11 | 15000 | 1914 | 1885 | 0 | 66 | 544 (510/34) | 0 / 16 |
| special_22 | 15000 | 989 | 978 | 0 | 51 | 531 (522/9) | 0 / 13 |
| seps_22 | 15000 | 2628 | 2570 | 0 | 101 | 458 (370/88) | 0 / 16 |
| glue_22 | 15000 | 2323 | 2284 | **2** | 115 | 657 (565/92) | **1** / 23 |
| chains_22 | 15000 | 1434 | 1404 | 0 | 83 | 641 (607/34) | 0 / 19 |
| mix_22 | 15000 | 1931 | 1897 | 0 | 81 | 524 (495/29) | 0 / 18 |
| n12_11 | 15000 | 1681 | 1643 | **5** | 97 | 791 (732/59) | 0 / 25 |
| **total** | **165000** | | | **9** | **945** | **6392** | **2** / 205 |

(The seed-11 runs predate the redactor/cut split of the last column; their split is recomputed from the saved hits by
`classify.py`, which re-evaluates each input.) BODY C4a count per family: special 0, seps 0, glue 2, chains 2, mix 0, n12 5.

Every C4a hit assigned to a mechanism (`/tmp/vj113r3/classify.py`; two SCRATCH-ONLY classifier variants of the PIN's file, built
by `mkfix.py` and never landed: `fixN1` makes the widened branch refuse a `(?i:API_?)` prefix whose tail is an upper-case
`_ENVVAL_HEAD` and a non-space; `fixN2` stops the step's replayed run where an sk match starts). A hit is N-1 when `fixN1` hides
it, N-2 when `fixN2` does:
```
{'C4a N-1': 6, 'C4a N-2': 3, 'C4b-redactor N-2': 2}        (no UNCLASSIFIED row)
chains_11  C4a N-1  v1.finding_class.title          body='hjVfh42h94J9Mhg33Mjh9z65u0HJgZu5x'
chains_11  C4a N-2  b2.hit_role.sym                 body='3jZuu04Gq5uVlvıU26uU'
glue_22    C4a N-2  ap.violates_row.row_title       body='0'      (a one-character value glued to a bearer; d556c9b's widened value took it)
glue_22    C4a N-2  d1.bug_echo_scores.class_slug   body='Vu4HqXXF119xfM'
n12_11     C4a N-1  x5 (action_excerpt x2, wf.drift.expected, b2.hit_role.snippet, b1.finding_sev.file)
```
The nine hits span eight fields of six schemas, including a path field (`b1.finding_sev.file`). C4a's claim "zero" is
FALSE at the PIN: 9 of 165,000 generated inputs, and the six hand-made ASCII shapes of section 2c.

## 3. Item 3 — C4b, independently (the same generator against fb016d0)

- Newly visible BODY inputs against fb016d0: 6,392 of 165,000 (table above; per run 405..791). Trades dominate (a byte fb016d0
  showed is now hidden).
- **C4b's second condition (the byte also visible at d556c9b):** fails on 2 inputs where d556c9b's REDACTOR hid the byte
  (chains_11 `b2.hit_role.sym`, glue_22 `ap.violates_row.row_title`); both are the N-2 C4a hits above. 205 more inputs have a
  byte that d556c9b shows in its redactor output but its field limit cuts (the F-5 cut shift; visible at the redactor level).
- **My attribution** (`/tmp/vj113r3/attrib.py`): my own pattern builder takes each of the 16 subsets of {R1 `_BEARER_RUN`
  case-blind, R2 the token check case-blind, R4 the merge step, R3 FIX-B's `\S`} and applies it to fb016d0's class forms. Asserted
  at string level: the empty subset gives fb016d0's exact `_SK.pattern`/`_BEARER.pattern`, the full subset gives the PIN's. Per
  exposure E: the minimal subsets whose variant shows all of E, the changes NECESSARY (reverting one alone from the PIN hides a
  byte of E) and the single changes SUFFICIENT. 05:43:08Z..05:43:28Z, the same 11 x 15,000 inputs:
```
harness: variant(none) == fb016d0 and variant(all) == PIN on all 165,000 inputs (no "HARNESS BROKEN" key in any run)
special_11 {R1: 502, R1+R4: 23, R2: 1, R4: 14}                                  exposures 540
seps_11    {R1: 221, R1+R2: 1, R1+R4: 25, R2: 1, R3: 2, R4: 153, R4+R3: 2}          exposures 405
glue_11    {R1: 435, R1|R3: 2, R1+R2: 1, R1+R4: 54, R2: 2, R2+R4: 1, R3: 1, R4: 150, R4+R3: 2}   exposures 648
chains_11  {R1: 523, R1+R2: 1, R1+R4: 29, R2: 4, R3: 2, R4: 93, R4+R3: 1}          exposures 653
mix_11     {R1: 412, R1+R4: 52, R1+R4+R3: 1, R2: 4, R2+R4: 1, R3: 1, R4: 68, R4+R3: 5}   exposures 544
special_22 {R1: 495, R1+R4: 25, R2: 1, R4: 10}                                  exposures 531
seps_22    {R1: 248, R1+R2+R4: 1, R1+R4: 40, R2: 5, R4: 162, R4+R3: 2}           exposures 458
glue_22    {R1: 450, R1|R3: 1, R1+R2: 1, R1+R3: 1, R1+R4: 42, R1+R4+R3: 1, R2: 2, R3: 2, R4: 156, R4+R3: 1}   exposures 657
chains_22  {R1: 512, R1+R4: 26, R2: 2, R2+R4: 1, R3: 1, R4: 97, R4+R3: 2}          exposures 641
mix_22     {R1: 413, R1+R4: 38, R1+R4+R3: 2, R2: 2, R2+R4: 1, R3: 3, R4: 63, R4+R3: 2}   exposures 524
n12_11     {R1: 642, R1+R2+R4: 1, R1+R3: 1, R1+R4: 46, R2: 1, R3: 2, R4: 98}          exposures 791
```
  (`R1|R3` = either change alone shows it; one glue_11 exposure therefore has no single NECESSARY change.) Every exposure has a
  minimal subset: the attribution half of C4b holds on my inputs; no exposure is unattributed. The two C4b exposures that fail
  the second condition are attributed to R1 alone (`minimal: R1 necessary: ['R1'] single: ['R1']`): R-1's case-blind run lets
  the bearer match, the value merges, and N-2 frees the next value, which d556c9b hid.
- The builder's "all four reverted equals fb016d0": my own harness equals fb016d0 on all 165,000 of my inputs. I did not run the
  builder's `attr3.py` (brief item 2). Read only: it reverts by exact-count text edits of the final file, so its all-reverted
  variant differs from fb016d0's text (`_yield_pattern(r"(?!)")` keeps `(?:(?!)|\S)*?` where fb016d0 has `\S*?`). I re-typed its
  four edits on a copy of the PIN file (`/tmp/vj113r3/bvar/volatile.py`) and measured: `pattern text equal to fb016d0: False
  False`, `inputs 20000 builder-style all-reverted != fb016d0: 0`. The builder's claim holds on my inputs (equivalent regexes).

## 4. Item 4 — C1-C3 beyond the builder's rows

### 4a. My own R-1 / R-2 / R-4 / R-3 shapes (`/tmp/vj113r3/item4_cases.py`), through the real path
Each shape sits in `b1.finding_sev.msg` as `"set " + raw + " now"` and runs through `ledger_probe.py` in each tree's own
interpreter (05:46:05Z; corrected shapes re-run 05:47:00Z). Fake values use only X Z V x z v and the special letters, and no other
text in a shape holds those letters, so "a value byte in the state" = a value LETTER in the state's canonical text, and "in the
line" = the value or any 3-character window of it in the raw ledger bytes. `replay` = rows replayed and equal to the made row
(its fixed-point check, `src/agent_factory/decisions/ledger.py:273`, `restate = decision_state(qid, row["state"], None)`, runs
inside it).
| id | class | value | d556: value byte in state / in line / replay | fb01: value byte in state / in line / replay | pin: value byte in state / in line / replay |
|---|---|---|---|---|---|
| R1-a | R-1 | `XZVXZVXZ\u0131XZVXZVXZVX` | no / no / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R1-b | R-1 | `\u017fXZVXZVXZVXZVXZVX` | no / no / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R1-c | R-1 | `XZV\u0130XZV\u0131XZV\u017fXZVX` | no / no / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R1-d | R-1 | `XZVXZVXZVXZVXZV\u0131` | no / no / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R1-e | R-1 | `\u0131\u0131\u0131\u0131\u0131\u0131\u0131\u0131\u017f\u017f\u017f\u017f\u0130\u0130\u0130\u0130` | no / no / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R1-f | R-1 | `XZ.VX~ZV+XZ/VX-ZV_\u0130XZVX` | no / no / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R1-g | R-1 | `XZVXZVXZVX\u017fXZVXZ` | no / no / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R2-a | R-2 | `XZVXZVXZVXZV` | no / no / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R2-b | R-2 | `XZVXZVXZVXZV` | no / no / 1 ok | no / no / 1 ok | no / no / 1 ok |
| R2-c | R-2 | `XZVXZVXZVXZV` | no / no / 1 ok | no / no / 1 ok | no / no / 1 ok |
| R2-d | R-2 | `XZVXZVXZVXZV` | no / no / 1 ok | no / no / 1 ok | no / no / 1 ok |
| R2-e | R-2 | `XZVXZVXZVXZV` | no / no / 1 ok | no / no / 1 ok | no / no / 1 ok |
| R4-a | R-4 | `XZVXZVXZVXZV` | no / no / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R4-b | R-4 | `XZVXZVXZVXZV` | no / no / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R4-c | R-4 | `XZVXZVXZVXZV` | no / no / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R4-h | R-4 | `XZVXZVXZVXZV` | LEAK / LEAK / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R4-i | R-4 | `XZVXZVXZVXZV` | LEAK / LEAK / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R4-d | R-4 | `XZVXZVXZVXZV` | no / no / 1 ok | no / no / 1 ok | no / no / 1 ok |
| R4-e | R-4 | `XZVXZVXZVXZV` | LEAK / LEAK / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R4-f | R-4 | `XZVXZVXZVXZV` | LEAK / LEAK / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R4-g | R-4 | `XZVXZVXZVXZV` | no / no / 1 ok | no / no / 1 ok | no / no / 1 ok |
| R4-n2-a | R-4 | `XZVXZVXZVXZV` | no / no / 1 ok | LEAK / LEAK / 1 ok | LEAK / LEAK / 1 ok |
| R4-n2-b | R-4 | `XZVXZVXZVXZV` | no / no / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R3-a | R-3 | `XZVXZVXZVXZV` | LEAK / LEAK / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R3-b | R-3 | `XZVXZVXZVXZV` | LEAK / LEAK / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R3-c | R-3 | `XZVXZVXZVXZV` | LEAK / LEAK / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R3-d | R-3 | `XZVXZVXZVXZV` | LEAK / LEAK / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R3-e | R-3 | `XZVXZVXZVXZV` | LEAK / LEAK / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R3-f | R-3 | `XZVXZVXZ` | LEAK / LEAK / 1 ok | LEAK / LEAK / 1 ok | no / no / 1 ok |
| R3-floor7 | R-3 (A4 floor, by design) | `XZVXZVX` | LEAK / LEAK / 1 ok | LEAK / LEAK / 1 ok | LEAK / LEAK / 1 ok |
| R3-pad | R-3 (NAME==v, declared residue) | `XZVXZVXZVXZV` | LEAK / LEAK / 1 ok | LEAK / LEAK / 1 ok | LEAK / LEAK / 1 ok |

Reading: at the PIN every R-1 (7), R-2 (5) and R-3 (6) shape of mine keeps its value out of the state, `canonical()` and the
ledger line, and `replay` accepts every row. R-4: 10 of 11 hidden; **`R4-n2-a` leaks at the PIN and not at d556c9b** (the N-2
mechanism of F-2: the outer run is an sk, and an inner sk ends the real bearer run early). `R4-n2-b` (the same shape behind a
bearer) is hidden: the bearer's guard runs after `_SK`, so its step sees the real text; N-2 needs an sk as the OUTER run.
`R3-floor7` (a 7-character value: A4's 8-character floor, by design) and `R3-pad` (`NAME==v`: C2's declared residue) leak at all
three, as declared. C1 as frozen covers the verifier's repro rows and case files; `R4-n2-a` is outside that list, so it maps to
C4a (F-2), not to C1.
Shape errors of mine, corrected before the table: R1-d had 15 run characters (under the bearer's 16 floor), R4-a/b/c had no
8-character sk run (so no yield: the KNOWN widened chain), and the first state check read `/` and `.` of `src/a.py` as value bytes.

### 4b. The three C3 mutants, rebuilt by me on a scratch copy (`/tmp/vj113r3/mutdrv.py`, `mkmut.py`)
Scratch tree `/tmp/vj113r3/mutwt` (the PIN archive) plus a scratch-only guard test asserting the tree imports its own
`volatile.py`; per mutant: exact-count edits (count asserted), `py_compile`, collection count = baseline (178), the run, the pristine
file restored, the killing tests re-run on the UNMUTATED tree. 2026-09-24 05:49:07Z..05:50:49Z:
```
BASELINE 178 0 178 passed
m5 (V-M3: the yield token branch case-sensitive)          KILLED 2 failed, 176 passed | unmutated: 2 passed
   killers: test_decisions_canonical.py::test_surviving_mutant_rows_stay_redacted[V-M3-upper-token-space]
            test_decisions_ledger.py::test_surviving_mutant_rows_stay_off_the_ledger_file[V-M3-upper-token-space]
m6 (V-M11: (?<=_) dropped in the yield token branch)      KILLED 2 failed, 176 passed | unmutated: 2 passed
   killers: …[V-M11-underscore-token-space] in both files
m7 (V-M4: _ASSIGNMENT_HEAD token alternative case-sensitive) KILLED 2 failed, 176 passed | unmutated: 2 passed
   killers: …[V-M4-upper-token-head-in-a-chain] in both files
RESTORED 0 178 passed pristine: True
```
C3 holds: each of the three is killed by its own named row in both files.

## 5. Item 5 — the merge step (`_BEARER_MERGE`, `_yield_pattern`) attacked

`/tmp/vj113r3/item5.py` (mine), 2026-09-24 05:54:40Z..05:54:57Z: a full product grid, each shape in `b1.finding_sev.msg`, graded
against d556c9b by the visible BODY bytes (EQUAL = same output; BETTER = hides a superset; WORSE = a byte d556c9b's redactor hides
is visible; MIXED = both). Axes: outer run (sk, bearer, `ta` + sk) x six names/separators (`password:`, `PASSWORD=`, `secret = `,
`api_key=`, `Key: `, `TOKEN=`) x the bearer word (`bearer`, `BEARER`, `bEaReR`, `cupbearer`) x eleven runs (15 characters; 16; 16
with U+0131 first, U+017F at 8, U+0130 last; punctuation `. ~ + / - _`; a head inside the run; an inner sk ended by `.` or by the
tail; a second bearer glued inside the run: the declared depth-2 limit; `bearerbearer` inside the run) x padding (none, `=`, `==`)
x eight tails (end of text, ` rest`, `token: v`, `=key : v`, `password: v`, `)api_key= v`, a second glued merge, a chain head
`.secret = v1token: v2`) x placement (glued to the value, inside quotes, the bearer as the value's last word).
```
shapes 40392 {'BETTER': 23328, 'EQUAL': 17000, 'MIXED': 64}          (no WORSE-only shape)
  outer=sk {BETTER 9744, EQUAL 3672, MIXED 48}   outer=task {BETTER 3840, EQUAL 9608, MIXED 16}   outer=bearer: no MIXED
  run=run-inner-sk-dot {MIXED 32}   run=run-inner-sk-plain {MIXED 32}   tail=chain-head {MIXED 64}   pad=none {MIXED 64}   place=glued {MIXED 64}
fixN2 classifier on the 64: {'fixN2 hides every newly visible byte': 64}
example 'set sk-ghjlmqfupassword:plainonebearer ghjlmqfu01235678sk-ghjlmqfu..secret = XZVXZVXZVXZVtoken: zvzvzvzv now'
   d556 'set <redacted:sk>:plainone<redacted:bearer><redacted:sk>..secret = <redacted:envval> zvzvzvzv now'
   pin  'set <redacted:sk>password:<redacted:envval> = XZVXZVXZVXZVtoken: <redacted:envval> now'
```
Every shape where the PIN is worse than d556c9b is the N-2 mechanism (F-2): an OUTER sk, an inner sk inside the merged bearer
run, and a chain head after it. Everything else the brief lists is d556c9b's output or better: a run under 16, a bearer at the
very end of a value, a bearer inside quotes, the bearer word in four spellings, a special letter at the run's first, middle and
last place, a bearer glued to a second bearer, a merge whose tail holds a second head, and the depth-2 limit
(`src/agent_factory/decisions/volatile.py:98-101`, "The replayed run yields to a"): 0 WORSE. The word `bearer` holds no letter that U+0130, U+0131, U+017F or U+212A
folds to, so "bearer with each special letter" can only mean the run; it is covered at three places.

## 6. Item 6 — C5, cost and identity

Goldens (`/tmp/vj113r3/item6_identity.py`, mine; each module loaded by path, `canonical()` from the PIN tree; the constants read
from `tests/test_decisions_canonical.py`'s `GOLDEN_DIGESTS`):
```
ap.violates_row      const=594584bde9869086 fixture_expected=594584bde9869086 d556=594584bde9869086 fb01=594584bde9869086 pin=594584bde9869086 variant(pin)=594584bde9869086 all-equal=True
b1.finding_kind      const=9e18ed7e5146a2c3 … pin=9e18ed7e5146a2c3 variant(pin)=9e18ed7e5146a2c3 all-equal=True
b1.finding_sev       const=8c42d5dd1e8c349e … pin=8c42d5dd1e8c349e variant(pin)=8c42d5dd1e8c349e all-equal=True
b2.hit_role          const=3ced4cd39a61faa5 … pin=3ced4cd39a61faa5 variant(pin)=3ced4cd39a61faa5 all-equal=True
d1.bug_echo_scores   const=5a8c4ad2659c0e6b … pin=5a8c4ad2659c0e6b variant(pin)=5a8c4ad2659c0e6b all-equal=True
v1.finding_class     const=f41a299c4a38ab30 … pin=f41a299c4a38ab30 variant(pin)=f41a299c4a38ab30 all-equal=True
wf.drift             const=a51a56c48e98cca6 … pin=a51a56c48e98cca6 variant(pin)=a51a56c48e98cca6 all-equal=True
probe states: 226 (refused by all three: 0) | pin == d556c9b == fb016d0: 226 | idempotent(pin): 226
```
`git diff --stat d556c9b 942ad5e -- tests/fixtures/decisions/golden tests/fixtures/decisions/probe
tests/fixtures/decisions/gate_violation` is empty (the only fixture change since d556c9b is J1-3's five `sources/` files). No fixture
string changes.

Idempotence on my shapes: 0 PIN non-idempotent in the 165,000 differential inputs (every field slot, section 2d); 0 of 121,176 on
the item-5 merge grid placed in three bounded fields (`b1.finding_sev.msg` 200, `wf.drift.observed` 400,
`d1.bug_echo_scores.class_slug` 80); every item-4 row passed `replay`'s fixed-point check.

Cost (`/tmp/vj113r3/cost113.py`, mine; `_redact_str`, best of 5 under a 10 s alarm; 2026-09-24 05:56:51Z; load 1.11, nproc 4;
times in ms; ratios per doubling):
```
generator                                    mod       16k     32k     64k    128k    256k   ratios
G1 one value, many glued merges              pin      2.55    5.17   10.21   20.40   41.32  2.03 1.98 2.00 2.03
G2 merges + near-heads between               pin      2.48    4.98    9.97   20.07   40.82  2.01 2.00 2.01 2.03
G3 one merge, huge run of near-heads         pin      2.62    4.95    9.94   20.08   41.08  1.89 2.01 2.02 2.05   (d556 3.02 at 256k)
G4 bearer guard, many glued merges           pin      2.53    5.09   10.18   20.65   41.13  2.01 2.00 2.03 1.99
G5 many sk heads, each glued to a merge      pin      3.36    6.68   13.38   26.97   54.03  1.99 2.00 2.02 2.00
G6 'R16bearer ' chained (nested attempt)     pin      2.45    4.89    9.84   19.74   39.77  1.99 2.01 2.01 2.01
G7 near-bearer words, no space               pin      3.36    6.79   13.51   27.87   57.36  2.02 1.99 2.06 2.06
G8 near-heads + dotless i                    pin      3.87    7.77   15.69   31.84   64.79  2.01 2.02 2.03 2.04
G9 token-glued merges                        pin      2.52    4.99    9.99   20.15   40.25  1.98 2.00 2.02 2.00
G10 merges + inner sk (N-2 shape)            pin      3.51    7.04   14.09   28.01   56.30  2.00 2.00 1.99 2.01
G11 widened value of name-ish runs           pin      3.74    7.43   15.11   31.01   62.14  1.99 2.03 2.05 2.00
G12 many sk yields to api_KEY= (N-1)         pin      4.31    8.62   17.34   34.58   68.67  2.00 2.01 2.00 1.99   (d556 25.71 at 256k)
max ratio per doubling: {'pin': 2.06, 'fb01': 2.1, 'd556': 2.46}          (full table with fb01/d556 rows: rerun the tool)
```
Linear on every generator, including the nested and glued merge shapes; the PIN costs 1.0-1.3x fb016d0 and up to 13.6x d556c9b on
G3 (41.08 against 3.02 ms at 256k: the step replays the run and checks a yield at each character). C5 holds.
`test_env_assignment_redaction_does_not_backtrack_exponentially` is in the gate runs (section 8).

## 7. Item 7 — the builder's evidence

Red-green of the new tests (scratch trees `/tmp/vj113r3/red_{fb01,d556}` = the PIN archive with the reference's `volatile.py`,
plus my import guard; 05:57:55Z / 05:57:59Z):
```
PIN tests on fb01's volatile (bf04415d72c1): 30 failed, 148 passed   -> 30 of the new J1-1-R3 tests, 0 other, guard green
   r1 4+4, r2 3+3, r4 5+5, r3 3+3; the 15 params equal the builder's list (dotless-i-first … widened-bearer-padding)
PIN tests on d556's volatile (20ebcd54f3ed): 50 failed, 128 passed   -> 22 of the new tests (the builder's 22) + 28 J1-1-R2 tests
```
Mutants: 38 rebuilt by me from the descriptions (`mkmut.py`; my own edit texts; `mutdrv.py`), 05:49:07Z..05:52:35Z, baseline
`178 passed` (177 + the guard), every mutant compiled and collected 178, the pristine file restored at the end (`RESTORED 0 178
passed pristine: True` after each batch), every killer set green on the unmutated tree.
```
the builder's rows (30): m1 m2 m3 m4 m5 m6 m7 b-m1 b-m4a b-m4b b-m4c b-m4d1 b-m4d3 b-m4e3 b-m4f b-m4g b-m4j b-m4k b-m4n-PASSWORD
  V-M1 V-M2 V-M6 V-M7 V-M10 n1 n2 n3 n6 n9 n10                          -> 30 KILLED, the failure count equal to its table row
  killer sets by node id: 23 identical in full; 7 (b-m1, b-m4b, b-m4g, b-m4j, b-m4n-PASSWORD, V-M1, V-M2) contain the table's
  listed ten with the same total; 0 mismatches
my own (8):
  MY-A the step's possessive replay made greedy (== n2)          KILLED 2 failed  (c4[head-the-bearer-consumes] x2)
  MY-B the depth-0 yield dropped from the step (== n1)           KILLED 2 failed  (r4[head-the-bearer-leaves] x2)
  MY-C _BEARER_RUN case-sensitive in the STEP only (not the pass)  KILLED 2 failed  (r4[special-letter-in-the-merged-run] x2)
  MY-D FIX-B's lookahead removed entirely                         KILLED 3 failed  (c3[V-M10-upper-apikey-chain] x2, class[chain-upper-past-a-stop])
  MY-E the step's 16 floor raised to 17                           KILLED 8 failed  (four r4 rows x2)
  MY-F the step's \s+ -> \s                                       SURVIVED 178 passed   (equivalent: normalize leaves single spaces)
  MY-G FIX-B's \S -> .                                            KILLED 6 failed  (the r3 rows)
  MY-H the step's 16 floor lowered to 8                           KILLED 1 failed  (c::c4[bearer-run-of-15-glued])
```
The brief's five kinds are all present (possessive -> greedy: MY-A; the depth-0 yield dropped: MY-B; `_BEARER_RUN` back to
case-sensitive: m3 for pass and step, MY-C for the step alone; FIX-B's lookahead removed: MY-D; the step's floor changed: MY-E,
MY-H, n9). MY-F is an equivalent mutant through `decision_state` (finding F-7).

D-3 (the 26 tests the head cannot red; which named negative-control mutant reds each, from my rebuilt runs):
```
| test row (both files)                          | D-3's named mutants that red it: canonical / ledger |
| r1…[ascii-control]                             | V-M2 / V-M2 |
| r2…[ascii-control]                             | b-m4d3,b-m4e3,b-m4j,b-m4n-PASSWORD,V-M1 / the same |
| r4…[space-before-bearer-control]               | b-m1,b-m4b,b-m4g,b-m4n-PASSWORD,V-M1 / — (no mutant of my 38 reds the ledger twin) |
| r3…[no-prefix-control]                         | — / — (disclosed by the builder: no mutant kills it) |
| surviving…[V-M3 / V-M11 / V-M4 / V-M10 rows]   | m5 / m6 / m7 / V-M10, each in both files |
| merge_step…[merge-no-head]                     | n6 / n6 |
| merge_step…[short-bearer-no-merge]             | n3,n6 / n3,n6 |
| merge_step…[bearer-run-of-15-glued]            | V-M7,n3,n6,n9 / V-M7 |
| merge_step…[head-the-bearer-consumes]          | V-M6,n2,n6 / V-M6,n2,n6 |
| merge_step…[token-run-glued-to-bearer]         | n6,n10 / n6,n10 |
```
24 of the 26 are red under a named mutant. Two are red under none: the R-3 control in both files (disclosed in the builder's
D-3) and the LEDGER twin of the R-4 control, `tests/test_decisions_ledger.py`'s `space-before-bearer-control` (NOT disclosed: D-3
lists V-M1, b-m1, b-m4b, b-m4g and b-m4n-PASSWORD as the R-4 control's negative controls, but each reds only the canonical twin,
whose exact-text check sees the change; the ledger twin checks body bytes only, and the body stays hidden under each). Finding F-4.

## 8. Item 8 — gates (one foreground call, the shared tree, `PYTHONDONTWRITEBYTECODE=1`, `--basetemp` under `/tmp/vj113r3/bt/g`)
```
=== gates 2026-09-24T05:59:14Z HEAD=67cb0fa V=2d5cf0072469 TC=733fe70b705b TL=9900d9648fb8 TH=bb0187044a6a
decisions run 1 rc=0 :: 177 passed in 3.64s
decisions run 2 rc=0 :: 177 passed in 3.70s
2 files set=16a7b628685e
harvest run 1 rc=0 :: 67 passed in 19.70s
harvest run 2 rc=0 :: 67 passed in 20.72s
1 files set=87e28761f102
pyflakes rc=0                                   (volatile.py, test_decisions_canonical.py, test_decisions_ledger.py)
no_laya_in_gates: 40 files scanned, clean       (no_laya rc=0)
-k backtrack: 1 passed, 94 deselected           (test_env_assignment_redaction_does_not_backtrack_exponentially)
end 06:00:04Z
```
HEAD moved during the lane (six coordinator commits after the PIN, b26f9f9 through 67cb0fa; the brief is b26f9f9 on origin, and
7aa7f35 was its local id before the push rewrite); `git diff --stat 942ad5e HEAD` over `src/` and the three test files is empty, so every gate ran on
the PIN's boundary blobs. The tree's other dirty files are K215's; I touched none.

## 9. Stale-context sweep (statements F-1/F-2 falsify; I edit none of them)
- `src/agent_factory/decisions/volatile.py:58-60`: "'That value' is the text its class takes after the passes before it: … the
  env checks read on past a bearer match glued to the value (_BEARER_MERGE)". The env checks run inside the sk pass and read the
  text BEFORE that pass has redacted a later sk (F-2).
- `src/agent_factory/decisions/volatile.py:95-96` (`its run as the bearer`): "So the env value scans step over such a match: its run as the bearer pass runs
  it". Not when an sk inside the run is redacted first (F-2).
- `src/agent_factory/decisions/volatile.py:76-77`: "an upper-case NAME= that a non-space follows is _ENVVAL's, whose \S+ value
  runs further". True but incomplete: the upper-case tail of `api_KEY=` is _ENVVAL's too, and the widened branch does not see it
  (F-1). These three are C6 sentences (F-3).
- `tasks/briefs/laya/J1-1-R3-report.md:707` (section 12.1, on `_yield_pattern`): "Depth-1 yields are a subset of depth-0 yields, so a mismatch can only
  refuse more". The argument assumes the step and the bearer pass read the same text (F-2).
- `docs/08_DECISION_LOG.md:78` (D-067): "C4a: no BODY byte that d556c9b hides becomes visible (measured: 0 newly visible BODY
  inputs …)". The measurement is true of the verifier's generator; the clause is false at the PIN (F-1, F-2).
- `todo/BUILD-TASKLIST.md:1410` and `wiki/topics/live-state.md:34` (`VERIFY-J1-1-R3`) describe J1-1-R3 as waiting on this verify; the coordinator
  updates them.

## 10. Feasibility (scratch-only; a measurement, not a proposal to land)
C4a is not contradictory. The two classifier edits of `mkfix.py` together (`fixN12`, in `/tmp/vj113r3/fixtree`): `177 passed in
3.83s` on the PIN's own test files; on the four hit-bearing runs (chains_11, glue_22, n12_11, special_22; 15,000 each, 06:01:00Z..
06:05:31Z) `vs d556: BODY inputs (d556-redacted)`: 0, 0, 0, 0; C4b redactor-hidden: 0; PIN non-idempotent: 0; instrument
disagreements: 0. My six hand-made shapes and `R4-n2-a` are hidden there (`V3-in-line=False`, replayed 1, equal). Whether a
fourth round or the redesign follows is the coordinator's call under D-059.

## 11. Finding inventory (no severity filter; disposition by the brief's blocking predicate)

| # | class | finding | evidence | contract mapping | canonical path | material effect | reproduction | suggested fix |
|---|---|---|---|---|---|---|---|---|
| F-1 | **BLOCKER** | **N-1.** The widened branch (`src/agent_factory/decisions/volatile.py:84-85`) lets the sk/bearer run yield at a `(?i)` `API_?KEY` name whose tail is an upper-case `KEY=` (`api_KEY=`, `ApiKEY=`, `APİ_KEY=`). Its exclusion `(?!_ENVVAL_HEAD\S)` tests only the name's first character and its scan stops at `"'&,;`; but `_ENVVAL` (`:139`) takes the tail `KEY=` with `\S+`, crosses the stop, swallows the next head and frees its value, which d556c9b hid | VERIFIED: 6 of 165,000 generated inputs (5 fields of 5 schemas, a path field among them); hand shapes N1-sk-api_KEY, N1-sk-ApiKEY, N1-bearer-api_KEY | C4a (D-067) | reproduced through `decision_state` -> `make_row` -> `append` -> the line on disk -> `replay` (accepted), in the PIN archive tree AND against the shared tree's `src` (blob 2d5cf0072469) | a fake secret value (`X4Z9X4Z9X4Z9`) in the append-only ledger line: J1-1's headline capability | `sk-QZJ8QZJ8api_KEY=plainval"password: X4Z9X4Z9X4Z9` -> d556c9b `…password: <redacted:envval>`, PIN `…api_KEY=<redacted:envval> X4Z9X4Z9X4Z9`; `/tmp/vj113r3/ledger_probe.py /tmp/vj113r3/n_cases.json`; the scratch classifier `fixN1` hides it | refuse the widened branch where the name's upper-case tail is an `_ENVVAL` head (scratch form: `(?!(?:(?i:API_?))?" + _ENVVAL_HEAD + r"\S)`), so the run reaches the `KEY=` position and branch A judges it with `\S`; measured scratch-only (section 10). Also present at fb016d0: a J1-1-R2 regression VERIFY-J1-1-R2 did not find |
| F-2 | **BLOCKER** | **N-2.** `_BEARER_MERGE` (`:103-106`) replays the bearer run on the text the sk pass sees, before `_SK` has run; the real bearer pass runs after `_SK` and stops at an inner `<redacted:sk>`. When the inner sk run ends on `.`, `~`, `+`, `/` or U+0130/U+0131/U+017F, the replay runs past a head whose own value holds a head, the scan sees none, the outer sk yields, and the widened value swallows that head in the real text: its value, which d556c9b hid, is freed. An R-4 shape the step leaves open; it needs an OUTER sk | VERIFIED: 3 of 165,000 generated inputs; 64 of 40,392 item-5 grid shapes (all 64 hidden by `fixN2`); hand shapes N2-dot, N2-plus, N2-tilde-key; item-4 `R4-n2-a` | C4a; C4b's second condition on its special-letter form (2 inputs, attributed to R1, the byte hidden by d556c9b's redactor) | the same real path, both trees | a fake secret value in the ledger line | `sk-QZJ8QZJ8password:plainvalbearer abcdefghijklmnopsk-qqqqqqqq.secret = X4Z9X4Z9X4Z9token: plainvl2` -> d556c9b `….secret = <redacted:envval> plainvl2`, PIN `password:<redacted:envval> = X4Z9X4Z9X4Z9token: <redacted:envval>`; `fixN2` hides it | stop the step's replayed run where an sk match starts (scratch form: `|sk-[A-Za-z0-9_-]{8}` added to the replayed character's negative lookahead), so the scan continues over the inner sk's text and sees the head; measured scratch-only. The ASCII form is present at fb016d0 too (R-4 not fully closed) |
| F-3 | FOLLOW-UP | Comments F-1/F-2 falsify (section 9): `volatile.py:58-60`, `:95-96`, `:76-77`; the builder's section 12.1 argument; D-067's C4a premise | VERIFIED (read against the mechanisms) | C6 | n/a (text) | none on its own; tied to F-1/F-2 | section 9 | rewrite with the code fix |
| F-4 | FOLLOW-UP | D-3 is incomplete: the LEDGER twin of the R-4 control (`tests/test_decisions_ledger.py`, `space-before-bearer-control`) is red under none of my 38 mutants, including the five D-3 names for it (each reds only the canonical twin, whose exact-text check sees the change; the ledger check is body-only) | VERIFIED (item 7 matrix) | the J1-1-R3 brief's "each new test RED at the head" and its disclosure (D-3) | n/a (tests) | a test without a working negative control; no behaviour change | `/tmp/vj113r3/out/mut_{a,b}.json`, item 7's matrix | disclose it in D-3, or give the ledger twin a check a mutant can red (the exact state, as the canonical twin has) |
| F-5 | INFO | Cut shift: 945 of 165,000 inputs show at the PIN a BODY byte that d556c9b's field LIMIT hid while its redactor left it visible; the PIN's shorter output moves it inside the limit. 205 of the fb016d0 exposures are of the same kind at d556c9b | VERIFIED (instrument B's `d556-cut` split, instrument A agrees) | none as written (C4a says "redacts"; D-067 says "hides") | through `decision_state` | a byte d556c9b's redactor also shows | `c4diff.py`, `why == d556-cut` | the coordinator may rule whether "hides" covers the bound cut |
| F-6 | INFO | The builder's instrument is narrower than the contract's BODY: `diff3.py`'s `body` role excludes special letters and bearer-alphabet run characters, and its generator draws no mixed-case `KEY` name and no sk inside a bearer run, which is why its 0 missed F-1/F-2. Its saved d556c9b hits hold no `special`/`tokchar` role | VERIFIED (read `/tmp/j113s/v/tools/diff3.py`; parsed its six saved JSON files) | evidence for C4a | n/a | the measured 0 was not evidence of the property | section 2a | measure BODY as every value character; generate name case variants and nested key forms |
| F-7 | INFO | MY-F (the step's `\s+` -> `\s`) survives: equivalent through `decision_state` (normalize leaves single spaces); it would differ only for a direct `redact()` call on un-normalized text (`redact` is exported by `src/agent_factory/decisions/__init__.py`, documented "Applied AFTER normalize") | VERIFIED | none | n/a | none through the ledger | `mutdrv.py` MY-F | none needed |
| F-8 | INFO | Cost: linear on 12 generators aimed at the step (max ratio per doubling 2.06); 1.0-1.3x fb016d0; up to 13.6x d556c9b (G3, one huge merged run: 41.08 vs 3.02 ms at 256k) | VERIFIED | C5 (holds) | `_redact_str` | none | `cost113.py` | none |
| F-9 | INFO | Exactly four non-ASCII letters match the case-blind run classes (U+0130, U+0131, U+017F, U+212A); NFC maps U+212A to `K`, so the comment at `volatile.py:49-50` is true | VERIFIED (a 0x80..0x10FFFF sweep) | C6 (holds) | n/a | none | section 2a | none |
| F-10 | KNOWN | The `NAME==v` residue (`R3-pad`), the 8-character floor (`R3-floor7`), and AF-AP-157's chain family (a chain's first value or token run keeps d556c9b's output: the `ghjlmqfu…` runs in R2-a..e) reproduce as declared | VERIFIED | KNOWN rows | — | — | item 4 table | — (never weighed) |
| F-11 | INFO | The builder's claims that reproduce: the red-green split (30 new tests red at fb016d0 and no other test; 22 new tests red at d556c9b); 30 of its mutant rows (counts and killer sets); m5/m6/m7 each killed by its own C3 row; the goldens and the probe unchanged; its all-reverted variant equal to fb016d0 on my inputs; every fb016d0 exposure attributed to R1/R2/R4/R3 or a combination; C1-C3 on my R-1/R-2/R-3 shapes; cost linear; the gates (177 x2, 67 x2, pyflakes, no_laya) | VERIFIED | C1, C2, C3, C5 | real path for item 4 | — | sections 3, 4, 6, 7, 8 | — |
| F-12 | INFO | The brief's "committed as 7aa7f35" names the local id; on origin the brief is b26f9f9 (`git diff --stat 7aa7f35 b26f9f9` empty: the push rewrite stripped trailers only) | VERIFIED | none | — | none | section 8 | none |

## 12. Reproduced, reviewed statically, skipped
- Reproduced (this lane, output pasted): the premise; the differential (165,000 inputs, two instruments, 0 disagreements); the
  nine C4a hits and their classification; the six hand shapes through the ledger in the PIN tree, the d556c9b and fb016d0 trees and
  the shared tree's `src`; the attribution lattice (16 variants, harness identity); item 4's 31 shapes through the ledger; 38
  mutants; the red-green split; the item-5 grid (40,392); the goldens, probe and idempotence; cost; the gates; the fixN12
  feasibility runs.
- Static only: the stale-context statements (section 9); the builder's `diff3.py`/`attr3.py` method (read, never run).
- Skipped: the builder's other 28 mutant rows (I rebuilt 30 of 58 plus 8 of my own); the full-tree suite (not asked); K215's files
  and any PC or bridge use (standing rules).

## 13. NOT done (first-class)
- No fix: F-1 and F-2 are not repaired in the tree; the classifier variants live only in `/tmp/vj113r3/fixN1`, `fixN2`, `fixN12`,
  `fixtree`.
- No git add, commit, stash, checkout, restore, reset or clean; no edit of any tracked file; no outward-facing action; no subagent.
- Not measured: how often F-1/F-2 shapes occur in real ledgers or transcripts; F-1/F-2 against `scripts/transcript_export.py`'s own
  scrubber (outside the boundary).

## 14. GATE RECOMMENDATION: NOT-READY

F-1 and F-2 each satisfy the whole blocking predicate: (1) contract mapping: C4a as frozen by D-067 ("no BODY byte that d556c9b
redacts becomes visible"), and for F-2's special-letter form C4b's second condition; (2) canonical reproduction: `decision_state`
-> `make_row` -> `append` -> the ledger line on disk -> `replay` at the PIN, in the PIN archive and against the shared tree's
`src`; (3) material effect: a fake secret value in the append-only ledger line, the property J1-1 exists to guarantee; (4) a
concrete discriminator: deterministic inputs that d556c9b redacts and the PIN shows, and scratch variants that hide them with all
177 tests passing; (5) task ownership: both live in V's class forms (`_yield_pattern`, `_BEARER_MERGE`). The brief's rule applies:
a C4a hit blocks. C4a is satisfiable (section 10), so this is not CONTRACT-INVALID. Under D-067 the failed C4a voids the amendment.
Note for the decision: both mechanisms also exist at fb016d0 in their ASCII forms, so reverting J1-1-R3 to fb016d0 does not remove
them; only d556c9b's class forms lack them (with V-1 open). D-059 routes a new regression class to a redesign (the owner's
PATH-2 question). KNOWN rows did not weigh. This recommendation rests on nothing I did not reproduce.

## 15. Report lint (`python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/VERIFY-J1-1-R3-report.md`)
```
first run:            report_lint: 14 refs — OK 7, NEAR 1, MISS 2, UNCHECKABLE 4, UNRESOLVED 0 (worktree)   FLOOR 7 < 15, rc=1
fix round 1 -> run 2: report_lint: 22 refs — OK 21, NEAR 0, MISS 1, UNCHECKABLE 0, UNRESOLVED 0 (worktree)  rc=1
fix round 2 -> run 3: report_lint: 22 refs — OK 22, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)  rc=0
```
Round 1 corrected one wrong number of mine (the ledger's fixed-point line is 273, not 260) and added same-line tokens; round 2
added `_YIELD` beside the `_SK` reference (a three-letter name is no claim token).
