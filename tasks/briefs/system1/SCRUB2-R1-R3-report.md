<!-- Coordinator note (2026-09-28): the SCRUB2-R1 round-3 lane's hand-back, extracted verbatim from its transcript by `python3 scripts/stack.py harvest agent=a88c7c57f2fa2a96b` (run s-20260928T231833Z-9a593b; hand-back sha256 2cc1bdfc83ff; 1510 assistant records, all claude-opus-5-5, 0 refusal stops). The report of record for round 3 (task #321). -->

SCRUB2-R1 round 3 is done (task #321). The harness refuses report-file writes, so this message is the whole round-3 section.

# SCRUB2-R1 round 3: N1 and N2 repaired (task #321), report

Written 2026-09-28 23:0xZ (from `date -u`) by the SCRUB2-R1 build lane (sandbox `code-implementer`, Opus 5.5). The brief is `tasks/briefs/system1/SCRUB2-R1-R3-brief.md`.

- **Status:** built and self-checked. Nobody has verified it independently. I made no git write of any kind.
- **N1 is closed:**
  - The pwd floor counts characters, like the PIN's floor.
  - The credentials floor counts the characters before the value's first escape. D1 is kept as ruled.
- **N2 is closed:** a head the PIN never read no longer frees a later value that the PIN hid. There are three stops:
  - in the Cookie rule, for a head the PIN never read;
  - in the scheme rule, after an escaped quote (a sibling I found this round);
  - in the pwd and credentials rules, for every head.
- **Results:**
  - The 16 red items pass.
  - F-MUT: seven assertions each kill their own mutant.
  - All 81 mutants are KILLED on the final bytes.
  - On the real corpus, round 3 loses 0 value characters against the PIN. Round 2 lost 548.

---

## 1. NOT-done

1. **No git write.** There is no commit and no push, by the standing rule. The coordinator commits the five files.
2. **Corpus row C is not attributed to a change.** Row C lists what round 3 shows and round 2 hid (section 7). It is not split between the Cookie segment stop, the scheme stop and the pwd and credentials stops. On generated text the split is visible (sections 5 and 7). On the corpus it is a count only.
3. **D6's start guard is left as ruled** (DISCREPANCY R3-D8). The new stops now cover its protective part. The guard still shows the names of rules that ran earlier. Dropping `_APART` from it would hide those names again, as the PIN did. I did not do this, because D6 is to be kept as ruled. It is offered.
4. **V12 (round 2's D9) is still not fixed.** It is out of scope.
5. **I did not run the verifier's `mut.py` as written**, because its anchors are round-2 text. Its 19 mutants are re-anchored in my driver (`mut3.py`, group `x`). All 19 are KILLED.
6. **One unexplained test failure was not diagnosed** (R3-D5).
7. **Not re-run:**
   - W6 and W11/W28 (equivalent in round 2);
   - W17 to W20 (value-gate code this round does not touch).
8. **Corpus scope.** The corpus scan drops thinking blocks from both views and never reads them. Round 2's corpus rows included every string of a record, so its counts are not strictly comparable. Row B (round 2 against the PIN) was re-measured here the same way, so rows A, B and C compare like with like.

## 2. DISCREPANCIES

**R3-D1. rl2_prov's own table shows `OTHER|credentials`: 3 decoded and 5 raw.**
- Every lost position in those 8 regions is D1's (K) or a later credentials head's name (NAME).
- The verifier's `classify()` tests K and N1 on a whole region. A region that mixes the two therefore lands in OTHER.
- The shape is `credentials = sid=\rcredentials = =`:
  - D1 keeps the first value, because it has an escape before its 8th character.
  - The K variant (D1 undone) hides that value but stops before the second `credentials =` head. So the name stays in the K variant too.
- My per-position classifier (`rl2_refine.py`, section 6) puts all 8 regions in K+NAME, with REAL 0.
- Each value after those names is PINSHOW or NOVALUE.
- So "0 N2 losses" holds by per-position class. The verifier's table still prints 8 OTHER rows, and the verifier must judge them.

**R3-D2. The scheme rule got an N2 stop, which is beyond the verifier's shape list.**
- The contract's words cover it: "a head the PIN never read ... never frees a later value the PIN hid".
- The shape is `Authorization: \"Basic abcdefgh.pwd= <v>`:
  - the escaped-quote scheme branch's token took `.pwd=`, so the pwd rule found no head;
  - round 2 leaks `<v>` in the decoded and raw views, and the PIN hid it in both;
  - a bare-quoted decoded head behaves the same in canonical JSON, where its quote is escaped.
- The fix: after an escaped quote only, the token stops before a head that stands apart (`_APART`). Plain heads keep the PIN's token whole, which a test pins.

**R3-D3. The floor of a Cookie head the PIN never read is now searched in its segment, not by a lookahead to the line's end.**
- Why: my first candidate kept round 2's line lookahead and added the stops, so each head read the rest of its line again.
  - Measured on `my_cookie: ` repeated: 0.022 / 0.084 / 0.323 / 1.47 s at 8,000 / 16,000 / 32,000 / 64,000 characters. Each doubling of the input cost four times as much.
  - The final design grows about x2 per doubling (section 8).
- Cost: such a head hides less than round 2 did, but never less than the PIN, which never read it.
  - Corpus row C: round 2 hid 3,131 positions that the PIN and round 3 both show.
  - Round 2 also hid 224 positions that the PIN hid and round 3 shows. All 224 are head names (row A has only K, NAME and ESC).

**R3-D4. The pwd and credentials stops show more names (D6's class).**
- Generated text, NAME positions from round 2 to round 3: 26,825 → 29,241 (decoded) and 14,998 → 16,910 (raw).
- Corpus, NAME positions: subagent decoded 584 → 692 and subagent raw 471 → 579. The main transcript is unchanged (68).
- Every value after these names is HID, NOVALUE or PINSHOW.
- **Residual risk:** a value that itself ends in a non-alphanumeric character, then `pwd` or `credentials`, then a separator, then whitespace, a quote or the end shows that tail. An example is a base64 value ending in `/pwd=`.
  - Estimate for base64 values: about 3 in 10 million. The corpus has 0.
  - `_KEY_L` narrows the stop. Without it, the estimate was about 1 in 100,000 with more names.

**R3-D5. One failure of a pre-existing test, not reproduced.**
- `test_the_value_gate_reads_a_variable_and_a_raw_key_file` (SCRUB1's) failed once in a mutation-driver control run: 4 parallel pytest runs, `1 failed, 169 passed in 5.19s`.
- Its text holds no word that any changed rule reads.
- The driver kept only the last line, so I have no failure output. The driver now keeps failure lines.
- Not reproduced in:
  - 12 more parallel control runs;
  - the floor, twice;
  - the two test files, once;
  - the isolation trace, twice;
  - 6,000 replays of its body (3,000 each on round 2 and round 3, 0 differ).
- Cause unknown. I infer it was environmental, but that is not verified.

**R3-D6. HEAD moved under the lane.**
- HEAD went 0d06ae7 (the premise) → a430de7 → 093780c → b20b9c2. These were other lanes' commits, and pushes rewrote some ids.
- `git log 0d06ae7..HEAD` over the five files, `known_values_check.py`, `conftest.py`, `pyproject.toml` and `scripts/laya_ft/` lists 0 commits.
- The floor set stayed 12 files set=27f27a25516b.

**R3-D7. The brief's direction says "as D2 did for the scheme rule with `_OTHER_HEAD`".**
- D2 actually used `[ \t]+` after an escaped quote. `_OTHER_HEAD` is the Negotiate token's stop (B3/D5).
- Round 3's scheme stop uses `_APART`. A glued head with a glued value (`abc.pwd=xyz12345`) stays in the token and is hidden there.

**R3-D8. D6's start guard is now needed only for names whose rules ran earlier.**
- `_LATER_PWD` and `_LATER_CRED` cover pwd and credentials heads at the value's start too.
- The guard still stops a value from starting at `Authorization:`, `Cookie:`, `token:` and similar names, which it shows (D6 as ruled).
- R2g and R2g2 (the guard's `_APART` removed) survived until two assertions pinned the ruled behavior:
  - `pwd: Authorization: Basic zz` stays as written;
  - `credentials = password: zz` stays as written.
- Kept unchanged (NOT-done 3).

**R3-D9. `candidate_n1.diff` was used for its classes, not its form.**
- Its `_credentials_floor` callable checks the floor on the matched value.
- With round 3's stop, the matched value can be shorter than the run the PIN's floor read.
- Round 3 checks the same condition in a lookahead from the value's start, so the PIN's floor decision holds when a stop cuts the value. floor_units shows the same 7 D1 cells per credentials head as the verifier's candidate.

**R3-D10. The test prefix `test_r3_` is shared.** A pre-existing `test_r3_named_shapes_are_scrubbed` (line 622, an earlier lane's R3) has the same prefix as this round's six tests. Nothing collides.

**R3-D11. A stray bytecode file.**
- `scripts/__pycache__/transcript_export.cpython-311.pyc` (gitignored) is dated 2026-09-28 22:10:00Z, inside this lane's Laya record-test run.
- Every command here set PYTHONDONTWRITEBYTECODE=1. I did not identify the writer.
- I left the file in place: it is outside the boundary and gitignored.

---

## 3. Handback (short form)

**Files** (final sha256; `.lanes-live`'s set):

- `scripts/transcript_export.py`, f6fe76b2b67d316acc574c6e7ade4c7aedd994dc7157c4f599ee15018bc15274. Against round 2: 72 insertions, 27 deletions.
  - 96-103: `_SEP` extracted; `_APART = _NAMES + _SEP` (its pattern string is identical to round 2's, checked).
  - 104-112: `_LATER_PWD`, `_LATER_CRED` and their comment.
  - 114-123: `_COOKIE_PIN`, `_COOKIE_FLOOR` and their comment.
  - 124-131: `_PWD_FLOOR`, `_CRED_FLOOR` and their comment.
  - 147-157: `_cookie_or_same`.
  - 198-215: the Cookie rule.
  - 216-226: the scheme rule.
  - 227-244: pwd and credentials, with F-DOC's comment.
- `tests/test_transcript_export.py`, 39478c66e3ab96ed12724edda9d80687c5e256899c792d3303a419826262df5b. Against round 2: 154 insertions, 4 deletions.
  - 1493-1494 and 1510: two timing rows; the row count is now 32.
  - 1662-1663: the R2_LITERAL comment says "first 8 characters", no longer "units".
  - 1748-1893: this round's block. The 16 red items (4 tests), `R3_N2`, and 6 new tests.
- `docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json`, 21658ac0d86de6151603628e74a256cb2235d8146aae597268ffb6be092b31e9. Only line 10 changed: the exporter hash.
- Unchanged: `scripts/session_export.py` (0462fe2e9bdd14bc) and `tests/test_session_export.py` (c1bb29a1ec924a71). `scripts/known_values_check.py` is untouched (cfdf2ffec10e6d10).
- Against HEAD b20b9c2 (rounds 1 to 3): `5 files changed, 805 insertions(+), 19 deletions(-)`.

**Counts** (pasted; every run went through `masked.sh absent` with a private `--basetemp`):

| Run | Result | Set |
|---|---|---|
| Floor, 1st | `pytest-summary: 877 passed in 182.64s (0:03:02)` | 12 files set=27f27a25516b |
| Floor, 2nd | `pytest-summary: 877 passed in 179.09s (0:02:59)` | 12 files set=27f27a25516b |
| The two test files | `pytest-summary: 320 passed in 30.53s` | 2 files set=e8f27bcb91e7 |
| Set A's other six (the consumers of `scrub()` that detect_changes lists) | `pytest-summary: 96 passed, 1 skipped in 35.96s` (the skip is `test_qwen_jev.py:37` LOUD SKIP, as in round 2) | 6 files set=d11be22044d4 |
| Laya record tests (round 2's nine part-C ids) | `pytest-summary: 9 passed in 230.82s (0:03:50)` | 1 files set=8b147318aa48 |

- 877 = round 2's 855 plus 22 items: the 16 red items and 6 new tests.
- 320 = 298 + 22.

**Mutation** on the final bytes. KILLED only on a FAILED test; every edit matches exactly once and compiles; `pytest -x`:

| Group | Result |
|---|---|
| x: the verifier's X1-X19, re-anchored | 19 of 19 KILLED |
| rep: R2b, R2g, R2g2, R2d, R2k, M2', M22, R1d, N1-se | 9 of 9 KILLED |
| w: W1-W5, W7-W10, W12-W16 | 14 of 14 KILLED |
| y: this round's clauses, Y1-Y34 | 39 of 39 KILLED |
| all | 81 KILLED, 0 SURVIVED, 0 INVALID |

---

## 4. Premise (evidence demand 1)

Re-run with `bash scripts/premise_block.sh` through `masked.sh absent`, 2026-09-28 20:47Z. It holds:
```
$ git rev-parse --short HEAD
0d06ae7
 M docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
 M scripts/session_export.py
 M scripts/transcript_export.py
 M tests/test_session_export.py
 M tests/test_transcript_export.py
e36f708b5515cd36  scripts/transcript_export.py
0462fe2e9bdd14bc  scripts/session_export.py
c917c5ccaf08074a  tests/test_transcript_export.py
c1bb29a1ec924a71  tests/test_session_export.py
8d5427fdac6ee5f8  docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
8498307a91f35f8c  tasks/briefs/system1/vscrub2r2/vscrub2r1r2_red.py
7215866e517cc2e6  tasks/briefs/system1/vscrub2r2/candidate_n1.diff
16 failed
16 passed
/dev/vda          258020 25838     12101  69% /
```

---

## 5. What changed, and why

### N1: the floors count characters

- `_PWD_FLOOR = (?=[^\s"'&,;]{8})` is the PIN's floor, so it costs nothing.
- `_CRED_FLOOR` has two lookaheads, both O(1) per head:
  - `(?=[^\s"'&,;]{8})`;
  - no escape backslash at offsets 0 to 7. An escape backslash is the last backslash of an odd run, followed by n, r, t or f.
- Parity is found by fixed-width lookbehinds: 0, 2, 4 or 6 backslashes before the escape.
  - The value starts with no backslash (the start guard), so a run within its first 8 characters has 7 at most.
- So a pair or an odd run before another letter counts as characters (N1 fixed), and only D1's escapes keep a value.

### N2: a head the PIN never read never frees a later value

**Cookie rule.**
- `_COOKIE_PIN` is the head as the PIN read it:
  - `\b` or `set-cookie`;
  - a bare quote before the colon;
  - after the colon, a bare quote, or whitespace and escaped `\n`, `\r` or `\t` with no quote after them.
- From such a head, the value is round 2's: the rest of the line, over later heads too, as the PIN's value was. The group is `value`.
- Any other head sets `(?P<new>)`. Examples are an escaped quote, `my_cookie:`, and a head after a literal `\t`.
  - Its match is a segment up to a later head that stands apart (`_APART`) or a later Cookie head (`_COOKIE`).
  - `_cookie_or_same` searches `=[^\s;"']{8}` in that segment (`_COOKIE_FLOOR`).
- Why both stops: `_APART` covers the later scheme, pwd and credentials heads, which run after the Cookie rule. `_COOKIE` covers a later glued PIN head, such as `my_cookie: a Cookie:x Authorization: y sid=<v>`: without that stop the segment swallowed it (mutant Y30).

**Scheme rule.** After an escaped quote (`(?P<esc>)`), the token stops before `_APART`.

**pwd and credentials.**
- A value stops before `_LATER_PWD` or `_LATER_CRED`. These are a later pwd or credentials head that stands apart (`_SEP`), anchored by `_KEY_L` as their rules read a head.
- A pwd value stops before later pwd or credentials heads. A credentials value stops before later credentials heads. Those are the heads a rule still reads after the value; the Cookie and scheme rules ran before.
- This covers:
  - `\"credentials\": écredentials = <v>`;
  - `x\tcredentials==credentials = <v>`;
  - the `_APART` variant `pwd="credentials": cookie:credentials =  <v>`;
  - a new pwd head swallowing a later pwd or credentials head.

**Rejected designs** (measured):
1. **Candidate 1.**
   - Its design had three parts:
     - a line lookahead per new Cookie head;
     - stops before every `_COOKIE`;
     - an unanchored `_APART` stop in pwd and credentials.
   - It was quadratic (R3-D3). rl2_prov showed D6-LOSS 26 decoded and 12 raw, which were chains of names, plus `OTHER|credentials` 32 and 17.
2. **Moving the Cookie rule after pwd and credentials.**
   - When a later rule hides the only `name=value`, such as a scheme token `abc=defghijk`, the Cookie floor fails.
   - That Cookie line's first value then shows where the PIN hid it: a new V4 loss.

### F-DOC

The pwd and credentials comment (lines 227-240) now states:
- both floors count characters (N1);
- the pwd floor costs nothing;
- the credentials floor's real cost: a decoded value with a literal `\n`, `\r`, `\t` or `\f` among its first 8 characters stays (D1), and a pair or an odd run before another letter costs nothing;
- the `_APART` start guard and the `_LATER_*` stops.

The other comments I checked against the code:
- the Cookie rule's comment gives round 3's census: at most 0.06 s at 64,000 characters;
- the `_COOKIE_PIN`, `_LATER_*` and floor comments;
- the `_cookie_or_same` docstring;
- the test file's R2_LITERAL comment.

### Tests (`tests/test_transcript_export.py`)

**The 16 red items.**
- The block from `# N1, decoded text (the digest)` to the file's end is byte-identical to the verifier's file: 1,801 characters, checked mechanically. That covers the four tests, their decorators and their comments.
- `_hidden` is verbatim.
- The helpers use this file's own names:
  - `B = BS`;
  - `_h(n) = token_hex(n)[:n]`, using the file's `from secrets import token_hex`;
  - `_canon` and `MOD` are the file's own, with an identical body and the same file loaded.
- The verifier's unedited file passes on the final exporter: `16 passed in 0.07s` (pytest's own line, in a scratch copy).

**Six new tests** (lines 1800-1893):
- `test_r3_a_head_the_pin_never_read_frees_no_later_value`: nine N2 shapes in `scrub`, `scrub_payload`, pasted JSON, the digest and `convert()`.
- `test_r3_a_cookie_head_the_pin_read_keeps_its_whole_line`: PIN heads keep the whole line; new heads after `\t`+LF, `\n\"` and ` \"`.
- `test_r3_a_new_cookie_heads_floor_is_searched_in_its_segment`: 8 against 7 characters, a search rather than a start match, `;`, and the segment stop.
- `test_r3_a_value_stops_only_before_a_head_that_a_later_rule_reads`: the stops, `_KEY_L`, the plain scheme head kept whole, and the two D6 pins.
- `test_r3_the_credentials_floor_counts_characters_to_its_first_escape`: F15's class in raw JSON with `\f`, `\t`, `\r\n`, offset 7, and 2, 4 or 6 backslashes before the escape.
- `test_r3_each_clause_the_verifier_found_unpinned_is_pinned`: F-MUT.

**Timing rows:** `my_cookie: ` × 12,000, and `my_cookie: a pwd: ` × 6,000 then a value.

**Red and green:**
- On round 2's exporter (a scratch copy): `19 failed, 16 passed, 212 deselected in 4.94s`. That is the 16 red items plus the N2, segment and stop tests.
- On the PIN: `7 failed, 28 passed`. The PIN lacks round 2 and 3's features, and the 16 red items pass there.
- On round 3: all pass.

**F-MUT, each assertion against its own mutant** (only the F-MUT test, no `-x`). The failing line is that mutant's assertion:

| Mutant | Fails at line |
|---|---|
| X3 | 1880 |
| X6 | 1883 |
| X7 | 1885 |
| X8 | 1886 |
| X10 | 1888 |
| X13 | 1890 |
| X14 | 1893 |

On round 3, X14's shape needed changing:
- The verifier's `\"Negotiate abcdefghcredentials = <v>` is now saved by the new scheme stop.
- The assertion uses `\"Negotiate abcdefghCookie: sid=<v>` instead. The Cookie rule runs before the scheme rule, so only the Negotiate rule's `_Q` head saves it.

---

## 6. Evidence demand 2: the tables

Each probe ran through `vrun3.py`, which loads the verifier's `lib`, `prov` and `corpus_scan` from source with the work directory swapped. `variant()` is re-pointed at `_CRED_FLOOR` for K and F. No probe was edited. All runs went through `masked.sh absent`.

**floor_units.py** (77 rows, final bytes): `LOST cells by (head, view): [(('"credentials": "', 'dig'), 7), (('"credentials": "', 'txt'), 7), (('credentials=', 'dig'), 7), (('credentials=', 'txt'), 7)]`
- All are D1 escape shapes: `\n`, `\t`, `\n\n`, `\n\n\n`, a trailing `\n`, `\r\n`, and `\f` at offset 7.
- pwd heads: 0. Cookie: 0.
- The pair and odd-run shapes are hidden.

**e2e_floor.py**, run twice with fresh fakes; the final run:
```
new | turn: pwd="<7 chars with \\>" digest:hid convert:hid | Write: pwd="<chars with \\>" in code digest:hid convert:hid | Bash: --pwd=<chars with \t> digest:hid convert:hid | result: PWD: <chars with \n\n> digest:hid convert:hid | turn: credentials=<chars with \\> digest:hid convert:hid | control: pwd=<8 plain> digest:hid convert:hid
pin | ... | Write: pwd="<chars with \\>" in code digest:hid convert:LEAK | ... (all other places hid)
```

**e2e_n2.py**, run twice; the final run:
```
new
   N2 turn: \"Cookie\" then pwd='..'            digest:hid  convert:hid
   N2 result: my_cookie then db_pwd=".."        digest:hid  convert:hid
   N2 result: my_cookie then pwd: next line     digest:hid  convert:hid
   N2 turn: my_cookie then Cookie: next line    digest:hid  convert:hid
   N1-raw Bash: --pwd=<8 chars, one pair>       digest:hid  convert:hid
   cookie values: digest 0, convert 0
pin (all five hid)   cookie values: digest 2, convert 4
```

**rand_v4b.py** (4,000 texts, six views):

| | Seed 20260928 | Seed 7331 |
|---|---|---|
| Round 2, before | F 48, Fc 197, K 698, O 14, Ot 4 | F 42, Fc 212, K 680, O 16, Ot 4 |
| Round 3 | `{'K': 692}` (dig 346, txt 346); F, Fc, O, Ot 0 | `{'K': 668}` (334/334); F, Fc, O, Ot 0 |

**rl2_prov.py** (20,000 texts), final bytes:
```
dec|D6|HID 652  dec|D6|NOVALUE 391  dec|D6|PINSHOW 1390  dec|ESC 184  dec|F5 125  dec|K 68
dec|OTHER|credentials|anchor-ANCHOR-MISS,floor-ANCHOR-MISS,value-ANCHOR-MISS 3
raw|D6|HID 397  raw|D6|NOVALUE 97  raw|D6|PINSHOW 915  raw|ESC 229  raw|F5 364  raw|K 39
raw|OTHER|credentials|anchor-ANCHOR-MISS,floor-ANCHOR-MISS,value-ANCHOR-MISS 5
```
- The ANCHOR-MISS markers are the verifier's `clause()`, whose anchors are round-2 text.
- Round 2, before: `dec|N1 30`, `raw|N1 76`, plus these OTHER rows:
  - decoded: credentials anchor 1, credentials head 1, pwd anchor 1, pwd apart 1;
  - raw: cookie 1, credentials anchor 1, credentials head 8, pwd anchor 1.
- Round 3: N1 0, D6-LOSS 0, and OTHER cookie or pwd 0.

**rl2_refine.py** (the same generator; per-position classes: K, NAME from `_APART`, ESC, OHNAME from `_OTHER_HEAD`, REAL):
```
round 3: lost positions: dec ESC 599, K 1085, NAME 29241, OHNAME 11, REAL 0; raw ESC 1533, K 563, NAME 16910, OHNAME 11, REAL 0
         regions: dec K+NAME 3, raw K+NAME 5 (rl2_prov's OTHER); OHNAME 1 + 1
         values after a lost NAME: dec HID 648, NOVALUE 1320, PINSHOW 847; raw HID 413, NOVALUE 520, PINSHOW 734; LOSS 0
round 2: REAL dec 57, raw 257; OHNAME 238 / 532
```
- OHNAME is round 2's Negotiate `_OTHER_HEAD` stop (B3/D5), with the same class in round 2.
- Example: `...Negotiate <30 chars>credentials=Authorization:`. The PIN's opaque rule hid the 41-character run. Round 2 and round 3 hide the token and show the name.

**Other probes:**
- `b2b3_var.py`: B2 n=455, LOST 0 in all 6 views. B3 n=672, LOST 0.
- `d2_lost.py` (d2_sib's generator, counted per text): 1,440 texts × 6 views, LOST 0.
- `sch_n2.py` (R3-D2's shapes):
  - the three escaped-quote rows: PIN hid, round 2 LEAK, round 3 hid;
  - the `pwd=\n  <v>` row leaks on all three versions, the PIN too.

---

## 7. N2's cost (the measurement)

**The corpus.** This session's main transcript to 777,669,405 bytes, plus the verifier's 363 subagent files.
- Totals: 305,349 lines, 8,504,700 texts, 43,323 candidates.
- Thinking blocks were dropped. Only counts and masked shapes left the process.
- Each cell is texts changed / NEW regions / LOST regions:

| Row | main/dec | main/raw | sub/dec | sub/raw |
|---|---|---|---|---|
| A: round 3 against the PIN | 22 / 16 / 22 | 9 / 20 / 18 | 135 / 189 / 306 | 129 / 314 / 465 |
| B: round 2 against the PIN | 24 / 16 / 30 | 10 / 16 / 20 | 140 / 184 / 343 | 131 / 279 / 467 |
| C: round 3 against round 2 | 7 / 8 / 12 | 4 / 6 / 12 | 33 / 67 / 54 | 37 / 58 / 68 |

- **Row A, lost positions:**
  - K: 240 / 1,412 / 3,209 / 140 (main/dec, main/raw, sub/dec, sub/raw);
  - NAME: 68 / 0 / 692 / 579;
  - ESC: 0 / 8 / 112 / 521;
  - REAL: 0; OHNAME: 0.
  - Values after the lost names: HID 34, NOVALUE 12, PINSHOW 93, LOSS 0.
- **Row B, lost positions:** REAL 48 / 12 / 375 / 113, which is 548 value characters. The masked shapes are N1's backslash content.
- **Row C, lost positions** (round 2 hid them, round 3 shows them):
  - PIN-HID: 224, all names (row A);
  - PIN-SHOWN: 3,131 (132 / 132 / 380 / 2,487). This is round 3 giving back round 2's over-hiding on heads the PIN never read.

**Digest identity.** The main transcript, fixed at 780,053,941 bytes, exported with `sources=()`: the PIN and round 3 give `identical: 20 of 20`. I deleted the digests after the comparison.

**D7's constant.** The 20 committed digests (3,732,291 characters), best of 3:

| Version | scrub | scrub_payload |
|---|---|---|
| PIN | 2.604 s | 4.898 s |
| Round 2 | 3.475 s | 5.480 s |
| Round 3 | 3.568 s | 5.984 s |

**Per character.** A new-head segment costs about 1 µs per character (`my_cookie: ` + `apwd=`×n: 0.065 s at 64,000). Round 2 spent about 0.1 µs. Growth is linear.

---

## 8. B1: the timing census

- **`census2.py`** on the final exporter (65 families × 8 targets), worst per target at 64,000 characters:

| Target | Worst | Family |
|---|---|---|
| pemL | 0.0027 s | dash |
| neg | 0.0472 s | neg cookie |
| cookie | 0.0517 s | ck heads esc2 |
| scheme | 0.0120 s | neg https |
| pwd | 0.0431 s | pwd heads |
| cred | 0.0296 s | cred heads |
| scrub | 0.1298 s | ck heads esc2 |
| payload | 0.1948 s | ck heads tab |

- **Flagged rows.** Ten rows were flagged on one noisy step. Re-timed at 64,000 to 512,000, best of 3, they grow x1.74 to x2.56 per doubling:
  - neg cookie [2.23, 1.94, 2.0];
  - ck heads esc2 [2.56, 1.84, 1.74];
  - esc quotes [1.97, 2.04, 2.0];
  - auth bs [1.9, 1.97, 2.02];
  - pwd+esc [2.1, 2.14, 1.93];
  - pwd+pairs+eq [2.05, 2.0, 1.96];
  - ck heads q [1.94, 1.96, 2.23];
  - neg Bearer [2.4, 2.0, 1.83];
  - pwd bs head [2.01, 2.03, 2.03];
  - sch \q sp [1.77, 1.97, 2.07].
- **The census before the comment-only edits** (same patterns, checked equal) flagged 6 rows, re-timed at x1.70 to x2.35.
- **Fifteen families aimed at this round's clauses** (`retime.py`; 16,000 / 64,000 / 256,000, so each step is x4 in size) grow x3.79 to x4.92 per step, which is linear:
  - new-head lines;
  - new-head + PIN and apart heads;
  - PIN escape heads;
  - the scheme stop;
  - pwd and credentials later-head runs;
  - credentials floor runs.
  - Worst at 64,000: cookie 0.0534 s, pwd 0.0307 s, cred 0.0266 s.
- **Y31**, a line lookahead per new head, is killed by the timing test (`24.27s` run).

---

## 9. The Laya lock and the manifest

**`laya_r2.py`** (round 2's pre-fit comparison, reading the tree's exporter):

| Collection | Round 3 against the PIN | Controls |
|---|---|---|
| v2 `collect_v2` at 434b727dfd | differs in 0 of 6,220 items | N-pwd changes 16 items, and the new scrub equals the PIN on 16 of 16; E changes 6,220 |
| v1 `collect` at eb256f49c0 | 0 of 1,788 | E changes 1,788 |
| v1 `collect` at 0b342c7a29 | 0 of 1,788 | E changes 1,788 |

`common.scrub is the tree's exporter (the new one): True`.

**The manifest.**
- `HF_HUB_OFFLINE=1 /root/venv-laya-probe/bin/python scripts/laya_ft/build_dataset.py --version 2 --commit 434b727dfd2b6daa5aa3cf4d638e706f5dfa59cb --out <scratch>/v2new --model-dir .../typed-decisions`, rc 0.
- The raw diff against the recorded manifest is one line: `"scripts/transcript_export.py": "f6fe76b2b67d316acc574c6e7ade4c7aedd994dc7157c4f599ee15018bc15274"`. It was copied in.
- `test_version_2_record_rebuilds_byte_identically_at_the_pin` is among the 9 passed (section 3).

---

## 10. Gates

Section 3's table. All runs used `masked.sh absent` and a private `--basetemp` under the scratch directory, which is outside every work tree. Nothing else ran.

---

## 11. Mutation

The driver is `mut3.py`:
- four worker copies of the final tree;
- an unmutated control in each (12 runs green in the final pass);
- KILLED only on FAILED;
- failure lines kept in `mut3-failures.txt`: 81 entries, all from mutants, 0 from the value-gate test.

**Group x.** X1 through X19 are all KILLED. The first failing test for each:

| Mutant | First failing test |
|---|---|
| X1 | `test_r2_a_value_stops_before_an_escaped_quote_at_depth_two` |
| X2 | `test_r2_a_literal_escape_in_decoded_text_keeps_the_value_hidden` |
| X3 | the timing test first under `-x`; also its own F-MUT line |
| X4, X5 | the plain-text Cookie differential |
| X6, X7, X10, X13, X14 | the F-MUT test |
| X8 | `test_n2_…` |
| X9, X18 | the Negotiate base64 test |
| X11, X12 | `test_r2_a_value_never_starts_at_another_rules_head` |
| X15, X19 | `test_r1_named_rules_hold_every_f1_context_end_to_end` |
| X16 | the R2_LITERAL test |
| X17 | `test_r3_a_cookie_head_the_pin_read_keeps_its_whole_line` |

**Group rep.**

| Mutant | Killed by |
|---|---|
| R2b | `test_r3_a_cookie_head_the_pin_read_keeps_its_whole_line` |
| R2g, R2g2 | `test_r3_a_value_stops_only_before_a_head_that_a_later_rule_reads` (the D6 pins) |
| R2d | the Negotiate next-header test |
| R2k, M2' | the escape-unit test |
| M22 | the Negotiate base64 test |
| R1d | the F1 end-to-end test |
| N1-se | `test_each_gate_pattern_name_labels_its_own_rule` |

**Group w.** W1 to W16 are all KILLED, each by the same kind of test as in round 2.

**Group y.**

| Mutant | Clause | Killed by |
|---|---|---|
| Y1, Y2 | the round-2 floors | N1 red items |
| Y3 | K, D1 undone | F15 test |
| Y4 | window 0-6 | F15 test |
| Y5 | window 0-8 | R2_LITERAL |
| Y6, Y7, Y8 | parity 2, 4, 6 | round-3 F15 test |
| Y6b | parity 0 | F15 test |
| Y9 | without f | round-3 F15 test |
| Y9b, Y9c, Y9d | without t, r, n | F15 test |
| Y10, Y15 | no `_KEY_L` | stops test |
| Y11 | `_LATER_PWD` without pwd | F1 contexts test |
| Y12, Y13, Y14 | N2 shapes | N2 test |
| Y15b | `_LATER_CRED` with pwd | stops test |
| Y16 | `_COOKIE_PIN` without `\b` | red N2 items |
| Y17, Y18, Y19, Y34 | `_COOKIE_PIN` forms | plain-text differential |
| Y20 to Y24 | `_COOKIE_PIN` escapes and lookahead | PIN-head test |
| Y25, Y26, Y27 | segment floor | segment test |
| Y28 | match, not search | F1 end-to-end test |
| Y29 | no `_APART` stop in the segment | red N2 items |
| Y30 | no `_COOKIE` stop in the segment | N2 test (its row added this round) |
| Y31 | line lookahead per head | timing test |
| Y32 | no scheme stop | N2 test |
| Y33 | the scheme stop on plain heads too | stops test |

---

## 12. Everything else holds

- **B1:** section 8.
- **B2 and B3:** `b2b3_var` 0 LOST; round 2's B2 and B3 tests pass.
- **D2:** `d2_lost` 0 LOST of 1,440 × 6.
- **D6:** the start guard is unchanged and now pinned.
- **D1:** kept. floor_units' 7 cells; the F15 tests.
- **D7:** section 7.
- **F1:** `test_r1_named_rules_hold_every_f1_context_end_to_end` passes in the floor.
- **F15:** its test plus the round-3 F15-class test.
- **F2:** the Negotiate tests pass.
- **F7:** census pemL at most 0.0027 s.
- **F10:** N1-se is KILLED.
- **F12:** the W group is 14 of 14 KILLED.
- **The value gate:** `known_values_check.py` is HEAD's bytes. The diff hunks are only lines 94-131, 145-157 and 196-244, so no gate line changed. The gate's tests are in the floor.
- **Test isolation** (round 2's strace and env-logger trace, re-pointed; the two test files):
  - absent: `320 passed in 46.30s`, 0 syscalls on any source path, 0 token lookups;
  - fakes: `320 passed in 46.57s`, 0 opens. The copy's fake `.pc-bridge.env` got 1 `newfstatat` and 2 ENOTDIR probes (`pyvenv.cfg`, `conda-meta/history`), which is pytest's venv detection, as in round 2.
- **The Laya lock:** section 9.
- **Digest identity:** section 7.

---

## 13. Self-attack

1. **`_COOKIE_PIN` might misread a head the PIN read as new.** Its line would then get stops, and a value the PIN hid through that Cookie line would show. Ruled out by:
   - the 6,000-text plain differential against SCRUB2's Cookie rule;
   - REAL 0 in rl2_prov, rand_v4b and the corpus;
   - Y16 to Y24 and Y34 all KILLED;
   - `b2b3_var` and e2e_n2 hid.
   - Residual: head forms outside these generators. Case-insensitivity, `Set-Cookie`, spaces before the colon, and escapes or quotes after it are covered.
2. **The new-head path might be super-linear again**, as candidate 1 was. Ruled out by:
   - the census and the 15 aimed families;
   - ten flagged rows re-timed to 512,000;
   - two new timing-test rows;
   - Y31 KILLED by them.
3. **The credentials lookahead might miscount**, keeping N1 alive or growing D1. Ruled out by:
   - floor_units: 0 N1 cells, and the same 7 D1 cells as the verifier's candidate;
   - Y1 to Y9d all KILLED;
   - the red items pass;
   - rand_v4b: F and Fc are 0.
   - Residual: runs longer than 7 cannot fall in the window, because the value starts without a backslash.

A fourth risk, stated in R3-D4: the stops show a value's own tail when that tail spells a later head. It is bounded and counted.

---

## 14. Evidence tiers

- **Verified here** (ran, output above):
  - the premise;
  - the red items (both files);
  - the verifier's five probes and b2b3, plus d2_lost;
  - the refined classes;
  - rand_v4b before and after;
  - the corpus rows A, B and C;
  - digest identity;
  - D7 timings;
  - the census and re-times;
  - the Laya lock and the manifest rebuild;
  - the gates;
  - the 81 mutants and the 7 per-assertion F-MUT kills;
  - the isolation trace.
- **Inferred:**
  - R3-D5 is environmental;
  - the probability estimate in R3-D4;
  - that row C's PIN-SHOWN positions are mostly new-head Cookie segments. This is not attributed on the corpus (NOT-done 2).
- **Assumed:**
  - the verifier's read-only probes behave as their docstrings say, with `vrun3.py` changing only paths and `variant()`;
  - HEAD's intervening commits do not affect the lane. This is checked by `git log -- <paths>` only.

---

## 15. Scratch

`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/scrub2r3/`, 6.8 MB. I never wrote the verifier's scratch.

**Instruments:**
- `vrun3.py`: the probe runner;
- `rl2_refine.py`: per-position classes;
- `corpus3.py`: rows A, B and C;
- `mut3.py`: the mutation driver;
- `xone.py`: F-MUT per assertion;
- `retime.py`: census re-times and aimed families;
- `d2_lost.py`, `sch_n2.py`, `digests_r3.py`, `d7.py`, `flake.py`, `trace_r3.sh`, `ctl4.sh`.

**Outputs:**
- `final-*.txt`;
- `c3-*.json`: the corpus rows;
- `laya-r3-*.txt`;
- `floor1.txt`, `floor2.txt`, `two.txt`, `seta.txt`, `layaC.txt`;
- `mut3-failures.txt`;
- `premise-out.txt`.

**Trees:**
- `pintree` (6ad316dc);
- `r2tree` (e36f708b);
- `mt` (the final five files and the unedited red file);
- `cand1_transcript_export.py`: the rejected candidate 1.