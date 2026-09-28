> **COORDINATOR NOTE (2026-09-28 18:1xZ):** the harness refused the lane's report-file write, and the lane put the whole report in its final text message (63,540 characters, sha256 prefix e692c1c6f80c), with a short summary as its hand-back. This copy is that text message, extracted from the subagent transcript, never retyped; control tags neutralized: 0. The lane served `claude-opus-5-5` on 1,131 assistant records with 0 refusal stops (read by `python3 scripts/stack.py harvest`). Not yet verified.

SCRUB2-R1 round 2 is done (task #321). This message holds the whole report, because the harness refused the report-file write, as the brief allowed for.

# SCRUB2-R1 round 2: the repairs after VERIFY-SCRUB2-R1 (task #321), report

Written 2026-09-28 18:0xZ by the SCRUB2-R1 build lane (sandbox `code-implementer`, Opus 5.5), under `tasks/briefs/system1/SCRUB2-R1-R2-brief.md`.
- **Status:** built and self-checked. Not verified independently. No git write of any kind.
- **The report file does not exist.** The harness refused the write ("Subagents should return findings as text, not write report files"). The exporter's credentials comment (lines 191-195) names `tasks/briefs/system1/SCRUB2-R1-R2-report.md, D1`, so this message needs saving at that path (D16).

## HANDBACK (short form)

**Files changed** (final sha256; the lane's `.lanes-live` set):
- `scripts/transcript_export.py`, e36f708b5515cd36:
  - lines 69-103: the classes, `_COOKIE_X`, `_NAMES`, `_OTHER_HEAD`, `_APART`, `_SCHEME`;
  - lines 119-125: the `_cookie_or_same` docstring;
  - lines 146-156: the Negotiate rule;
  - lines 166-178: the Cookie rule;
  - lines 179-187: the scheme rule (D2);
  - lines 188-199: pwd and credentials.
- `tests/test_transcript_export.py`, c917c5ccaf08074a:
  - 1420-1448: `R1_ORDINARY` and the F15 test;
  - 1467-1511: `LINEAR_CHILD`;
  - 1553-1559: the Cookie differential;
  - 1591-1743: the helper and nine new tests, 14 items.
- `docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json`, 8d5427fdac6ee5f8. Line 10 holds the exporter hash, set by K265's step.
- Unchanged: `scripts/session_export.py` (0462fe2e9bdd14bc) and `tests/test_session_export.py` (c1bb29a1ec924a71).

**Counts** (pasted from `scripts/test_summary.sh`):

| Run | Result | Set |
|---|---|---|
| Floor, 1st | `pytest-summary: 855 passed in 175.41s (0:02:55)` | 12 files set=27f27a25516b |
| Floor, 2nd | `pytest-summary: 855 passed in 170.20s (0:02:50)` | 12 files set=27f27a25516b |
| Set A's other six | `pytest-summary: 96 passed, 1 skipped in 35.24s` | 6 files set=d11be22044d4 |
| `tests/test_laya_ft.py` (4 runs, 44 passed) | `pytest-summary: 31 passed in 285.80s (0:04:45)` · `pytest-summary: 4 passed in 177.77s (0:02:57)` · `pytest-summary: 4 passed in 125.68s (0:02:05)` · `pytest-summary: 5 passed in 240.24s (0:04:00)` | 1 file set=8b147318aa48 |

**Mutation**, final bytes; the kill table is in section 5, one line per mutant:

| Group | Result |
|---|---|
| r2 | 17 of 17 KILLED |
| v5 | 6 of 6 KILLED |
| w | 26 KILLED, 2 equivalent survivors (W11, W28) |
| r1 | 19 of 19 KILLED |
| se | 8 of 8 KILLED |
| all | 0 INVALID |

**NOT-done:** section 10. **DISCREPANCIES:** section 11. Read D1, D2, D6 and D7 first.

---

## 0. Summary

- **B1, B2 and B3 are closed.**
  - The verifier's six red tests now give `6 passed in 0.59s` on the final exporter. At the premise they failed 6 of 6.
  - Its reproductions for V1 to V3 now hide the value or run in linear time.
- **A defect of B3's class was found and fixed this round (D2).**
  - Round 1's `_Q` let the scheme rule read an escaped-quote head (`Authorization: \"Negotiate`).
  - With `\s+` after the scheme word, the token became the next line's `Authorization`. That header's credential then showed.
  - The PIN hid it: its scheme rule never read such a head, so the next header's own match hid the credential. So this is a lost PIN redaction in the decoded view (V4).
  - 22 of 22 texts per escaped-quote form leaked on round 1, and on this round before the fix. Now 2 of 22 leak, the same 2 the PIN leaks.
- **V4 is closed except the kept classes.** Each has its ruling and reason:
  - `lost_shapes`: 13 LOST cells to 1 (D1).
  - `rand_lost2`: 253 lost fake tokens to 24 (D1: 14; F15-consistent: 10).
  - On the corpus, 11 head words the PIN hid now show (D6). The coordinator must rule on these.
- **V5:** M2, M3, M17, M20, M21 and M22 are each KILLED as a FAILED test. M2, M3 and M17 are tested in their round-2 forms (D3).
- **V21:**
  - The Cookie rule's comment now states its measured cost.
  - The Negotiate rule's comment names its stops and claims no other coverage.
  - Four more comments claimed more than the code does ("read once", "the rules take under 0.3 s"). They are corrected.

## 1. Premise, re-measured before any edit (12:5xZ to 13:0xZ)

| # | Brief | Measured | Verdict |
|---|---|---|---|
| P1 | HEAD 2c234ca at authoring; the dispatch names origin 7df5f03 | Local HEAD 1b7fec8 at resume. `git log cdbc1b8..HEAD` on the four scrubber files: 0 commits. | Holds (HEAD moved five times later, D8) |
| P2 | Patch e72a85cca2a3382d | The same | Holds |
| P3 | The five files equal round 1's finals | Byte-equal (014439fb, 0462fe2e, 00e7e9f8, c1bb29a1, 449811004a7a) | Holds |
| P4 | Red test 9ddf9f3cc3b3a34e; candidate 7f650748a0e60460 | The same | Holds |
| P5 | Red run: 6 failed | `6 failed in 60.19s`; the first stall is the Cookie head text, 33.27 s for one scrub | Holds |
| P6 | `lost_shapes`: 13 LOST cells | 13 | Holds |
| P7 | `rand_lost2`: 93; 13 + 9; 90; 20; 28 | 93; 13 + 9; 90; 20; 28 | Holds |
| P8 | Floor: 12 files set=27f27a25516b | The same | Holds |

## 2. What changed

### `scripts/transcript_export.py`

- Final sha256: e36f708b5515cd360d69f2bfbd977f488f8d5bb8dce4e3d1fe8917d09392df5b.
- Against round 1's final: 74 lines added, 32 removed.
- Against HEAD, together with the test file and the manifest: `3 files changed, 562 insertions(+), 15 deletions(-)`.

**Lines 69-79.** The comment on the classes:
- A backslash run is read by its length.
- A run before a quote is never value (F5, M17).
- An escape stays in a value only when a value unit follows it (V4).

**Lines 80-89.** `_Q`, `_PAIRS`, `_ODD`, `_ESC`, `_LODD`, `_LESC`, `_VF`, `_VU`, `_LF`, `_CL`.
- Each class reads a run whole and checks one character after it.
- No lookahead reads a run again at each pair (B1).

**Lines 90-95.** `_COOKIE`, and `_COOKIE_X`. `_COOKIE_X` also stops before a later head in this case (B2, D4):
- its colon is followed by whitespace, escaped line ends or tabs;
- and then by a real line end or a quote.

**Lines 96-103.** `_NAMES`, `_OTHER_HEAD`, `_APART` and `_SCHEME`.

**Lines 119-125.** The `_cookie_or_same` docstring.

**Lines 146-156.** The Negotiate rule:
- the token is on the word's own line (`[ \t]+`);
- it stops before `_BEARER`, `_LINK` and `_OTHER_HEAD`;
- `=` only pads its end.

**Lines 166-178.** The Cookie rule:
- after the colon, `(?:\s|\\[nrt])*` treats an escaped `\n`, `\r` or `\t` as whitespace;
- the floor reads characters, as the PIN's did (V4);
- both branches read `_CL` line units;
- the comment states the cost.

**Lines 179-187.** The scheme rule (D2):
- a plain or bare-quoted head is the PIN's head, with `\s+`;
- an escaped-quote head must have its token on the scheme's own line (`[ \t]+`).

**Lines 188-199.** pwd and credentials, both behind `_APART`:
- the pwd floor is `_VU`: escapes count;
- the credentials floor is `_VF`: no escape counts.

### `tests/test_transcript_export.py`

- Final sha256: c917c5ccaf08074a.
- Against round 1's final: 160 lines added, 15 removed.
- Collected items: 211 to 225. 14 added, 0 removed.

**Lines 1420-1435.** `R1_ORDINARY` now holds credentials texts only:
- F15's two shapes;
- F15-1 with CRLF;
- `f(credentials=cred12)\r\nnext_line_words`, which kills M2';
- `f(credentials=cred)\tpadding_word_here`, which kills M3'.

**Lines 1438-1448.** The F15 test's positive part asserts that no piece of the value shows and that the head stays.

**Lines 1467-1511.** `LINEAR_CHILD` has 14 texts and asserts 28 rows. The new texts:
- a Cookie, a pwd and a credentials head, each followed by 60,000 backslashes;
- a cookie value, then 60,000 backslashes and a quote;
- 30,000 escaped newlines after a pwd head;
- 14,000 escaped Cookie heads;
- 7,000 CRLF Set-Cookie heads;
- a 60,000-character base64 Negotiate token.

Its comment now states the slowest call measured.

**Lines 1553-1559.** The Cookie differential selects its rule by `_cookie_or_same`.

**Lines 1591-1743.** `_through_convert_turns` and nine new tests, 14 items (section 4).

### The recorded manifest

`docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json`:
- line 10 is the exporter hash, now e36f708b…;
- the file's sha256 is 8d5427fdac6ee5f8;
- against HEAD: 1 insertion, 1 deletion.

### Unchanged in the boundary

| File | sha256 (16) |
|---|---|
| `scripts/session_export.py` | 0462fe2e9bdd14bc |
| `tests/test_session_export.py` | c1bb29a1ec924a71 |
| `scripts/known_values_check.py` | cfdf2ffec10e6d10 |
| `tests/test_known_values_check.py` | f5ad1fc62a39c969 |
| the OpenJev manifest | not touched |

## 3. The contract, item by item

### B1: linear time on backslash runs

The verifier's `bs_timing.py`, run through `<scratch>/scrub2r1/r2/vrun2.py`, which swaps the candidate in. Seconds:

```
round 1 (014439fb)
new  pwd+bs         scrub    8000:0.3776 16000:1.1349 32000:4.3835
new  cred+bs        scrub    8000:0.2523 16000:1.1415 32000:4.7101
new  cookie+bs      scrub    8000:0.5370 16000:2.2522 32000:9.4875
final rules (te_r2e.py; the same compiled rules as e36f708b)
new  pwd+bs         scrub    8000:0.0073 16000:0.0150 32000:0.0293 64000:0.0619
new  cred+bs        scrub    8000:0.0069 16000:0.0158 32000:0.0288 64000:0.0625
new  cookie+bs      scrub    8000:0.0062 16000:0.0125 32000:0.0397 64000:0.0497
pin  pwd+bs         scrub    8000:0.0021 16000:0.0037 32000:0.0091 64000:0.0152
pin  cred+bs        scrub    8000:0.0022 16000:0.0047 32000:0.0082 64000:0.0165
pin  cookie+bs      scrub    8000:0.0050 16000:0.0115 32000:0.0195 64000:0.0376
```

The verifier's `e2e_bs.py 32000 <kind> new all`, through `export()` and `convert()`:

```
round 1  cookie all new n=32000: export() 8.78 s, convert() 17.43 s (5 events)
final    cookie all new n=32000: export() 0.03 s, convert() 0.22 s (5 events)
final    pwd all new n=32000: export() 0.04 s, convert() 0.30 s (5 events)
final    cred all new n=32000: export() 0.04 s, convert() 0.25 s (5 events)
```

- `LINEAR_CHILD` holds the three texts the brief asks for, with 60,000 backslashes each. The brief asks for at least 32,000.
- The slowest call in three runs of the test's child: 0.2821 s, 0.2493 s and 0.2666 s. The bound is 2 s.
- Every rule changed in either round was checked against every census family: section 7.

### B2: a Cookie value after an escaped line break

- **`lost_shapes`, raw view.** Three cells were LOST and now hide: "cookie yaml next line", its CRLF form, and "cookie colon then newline".
- **`e2e_yaml.py`, round 1:**
  `convert: Write yaml (convert) LEAK, Bash heredoc Set-Cookie (convert) LEAK`.
- **`e2e_yaml.py`, final:**
  `digest: user turn hid | convert: Write yaml (convert) hid, Bash heredoc Set-Cookie (convert) hid, user turn (digest+convert) hid, printf \r\n (convert) hid`.
- **The red test's three shapes now pass.** `test_r2_a_cookie_value_on_the_next_line_is_hidden_in_every_view` (3 items):
  - it checks decoded text, canonical JSON, pasted JSON and `convert()`;
  - it also pins where the marker starts.

### B3: Negotiate never crosses a line

**`e2e_neg.py`:**
- Round 1: `Negotiate (no token), next line Basic scrub:LEAK payload:LEAK digest:LEAK convert:LEAK`, and the same for Token.
- Final: `scrub:hid payload:hid digest:hid convert:hid` for both. The control hid in both versions.

**The escaped-quote form (D2)**, `<scratch>/scrub2r1/probe_w6b.py`:
- Each of 11 schemes, then a line end, then a Basic or a Token header, per quote form.
- The counts are texts where the second header's fake value shows.

Before the fix (the tree at 1f91c06a, "final" = the tree):

```
plain  final   texts 22  dec LEAK 20  raw LEAK  0
plain  round1  texts 22  dec LEAK 22  raw LEAK  0
plain  pin     texts 22  dec LEAK 20  raw LEAK  0
esc1   final   texts 22  dec LEAK 22  raw LEAK  0
esc1   round1  texts 22  dec LEAK 22  raw LEAK  0
esc1   pin     texts 22  dec LEAK  2  raw LEAK  0
esc3   final   texts 22  dec LEAK 22  raw LEAK  0
esc1'  final   texts 22  dec LEAK 22  raw LEAK  0
```

After the fix (the tree at f9b92269):

```
plain  final   texts 22  dec LEAK 20  raw LEAK  0      (pin 20)
bare   final   texts 22  dec LEAK 20  raw LEAK  0      (pin 20)
esc1   final   texts 22  dec LEAK  2  raw LEAK  0      (pin 2)
esc3   final   texts 22  dec LEAK  2  raw LEAK  0      (pin 2)
esc1'  final   texts 22  dec LEAK  2  raw LEAK  0      (pin 2)
```

- **The 2 left in each escaped form are the `Bearer` scheme.** The PIN's Bearer rule crosses the line too, and it leaks the same two.
- **The 20 in the plain and bare forms are V11:** pre-existing, and not this round.
- **The new test** `test_r2_after_an_escaped_quote_the_scheme_token_is_on_its_own_line` (3 items):
  - before the fix (1f91c06a, in a scratch copy): `3 failed in 0.53s`;
  - after the fix: `3 passed in 0.40s`.

### V4: no PIN redaction lost in any view

`lost_shapes` after the change. Every other row hid, gained, or leaked on both versions:

```
credentials literal-bs-n split         dec:LOST  raw:hid  raw2:hid
LOST cells: 1
```

`rand_lost2` (20,000 texts, 10,595 fake tokens), before (round 1):

```
dec:B-literal-escape                                                   93
dec:N-eatsB-literal-escape                                             13
dec:N-eatsother                                                        9
raw:F15-consistent (the PIN's decoded view shows it too)               90
raw:TRUE-LOSS (the PIN hid it decoded) NEW-dec-hides                   20
raw:TRUE-LOSS (the PIN hid it decoded) NEW-dec-shows                   28
```

After (the final rules):

```
dec:B-literal-escape                                                   13
raw:F15-consistent (the PIN's decoded view shows it too)               10
raw:TRUE-LOSS (the PIN hid it decoded) NEW-dec-hides                   1
```

`<scratch>/scrub2r1/r2/cls2.py` sorts each lost token by what else would hide it:
- `dec K (credentials floor) 13`
- `raw K (credentials floor) 1`
- `raw F15-consistent 10`
- N 0, other 0.

K means "hidden if the credentials floor counts escapes", which is F15-2's structure.

**Kept classes, each with its ruling and reason:**

| Class | Size | Ruling | Reason |
|---|---|---|---|
| D1 | 1 cell and 14 tokens | "F15's named over-redactions stay removed" | The decoded `credentials=abc\n<value>` and F15-2's raw `_CREDENTIALS=0\nnext_step_here` are the same bytes to the scrubber. It has no view flag, so one of the two must lose. |
| F15-consistent | 10 raw tokens | The same ruling | The PIN's own decoded view shows each of them. Its raw view hid them only by reading across an escaped line end, which is F15's class. |
| D6 | 11 corpus regions, head words | None covers them | A ruling is needed (section 11). |

The cost of the added over-redaction on the corpus is in section 6.

### V5: the six survivors

| Verifier's mutant | Round-2 form | Killed by |
|---|---|---|
| M2 (`_VE` takes an escaped CR) | M2': an escaped CR is a value character | `test_r1_an_escaped_newline_or_tab_ends_a_value`, its CRLF item |
| M3 (`_CV` takes an escaped tab) | M3': an escaped tab is a value character | the same test, its tab item |
| M17 (`_VE`'s pair without its lookahead) | M17': an escaped-backslash run may stand before a quote | `test_r2_a_value_stops_before_an_escaped_quote_at_depth_two` |
| M20 (no `\b` or `\f` before pwd) | unchanged | `test_r2_a_pwd_name_after_a_backspace_or_form_feed_escape_is_taken` |
| M21 (Negotiate floor 8 to 12) | unchanged | `test_r2_the_negotiate_token_is_base64_and_stops_before_other_heads`, a 10-character token |
| M22 (no `+` or `/`) | M22': `=` removed from the brief's form (D3) | the same test, a base64 token with `+`, `/` and `==` |

### V21: the comments match the code

- **The Cookie comment (166-176)** names the old costs and the measured one: "time grows linearly with the text (round 2's census: under 0.1 s for this rule on each 64,000-character text of 78 hostile families, about x2 per doubling)".
- **The Negotiate comment (146-154)**:
  - names its stops: a Bearer match, a bridge link, and `_OTHER_HEAD`'s heads;
  - ends with "No other head stops it: any other word stays in the token."
- **Corrected in the same pass:**
  - the classes' comment said a run "is read once, whole". It is read by its length, plus once more when its one-character check fails.
  - The same comment said "An even run … is value". That is false before a quote (M17).
  - The `_cookie_or_same` docstring said "read once".
  - The Negotiate comment said the credential rule takes the word. That is true only after a plain head (D2).
  - The timing test said "the rules take under 0.3 s". It now states the slowest measured, 0.28 s.

### Item 7: everything round 1 made true

- **F1, F15, F2, F7, F10, F12:** the r1 group (19) and the eleven F12 survivors are KILLED on the final bytes. The eleven: W1-W5, W7, W8, W10, W13-W15. Their tests pass in the floor.
- **The value gate:** W17 to W26 are KILLED. `tests/test_known_values_check.py` is unchanged and green in the floor.
- **Test isolation:** section 9.
- **The Laya lock:** section 8.
- **Item 6's rows:** section 6.

## 4. Tests

**The 14 new items, and the mutants that red each:**

| Test | Items | Covers | Mutants |
|---|---|---|---|
| `test_r2_a_cookie_value_on_the_next_line_is_hidden_in_every_view` | 3 | B2 | R2b |
| `test_r2_the_negotiate_token_never_takes_the_next_header` | 2 (Basic, Token) | B3 | R2d, R2e |
| `test_r2_the_negotiate_token_is_base64_and_stops_before_other_heads` | 1 | V5 | M21, M22, R2f, R2n |
| `test_r2_a_literal_escape_in_decoded_text_keeps_the_value_hidden` | 1 | V4 | R2i |
| `test_r2_a_value_never_starts_at_another_rules_head` | 1 | D6 | R2g, R2g2, R2m |
| `test_r2_an_escape_stays_in_a_value_only_before_a_value_character` | 1 | V4 | R2k, R2l |
| `test_r2_a_value_stops_before_an_escaped_quote_at_depth_two` | 1 | V5 | M17' |
| `test_r2_a_pwd_name_after_a_backspace_or_form_feed_escape_is_taken` | 1 | V5 | M20 |
| `test_r2_after_an_escaped_quote_the_scheme_token_is_on_its_own_line` | 3 | D2 | R2o, R2p, W6 |

Changed tests: `R1_ORDINARY` (M2', M3', R2h) and `LINEAR_CHILD` (R2a, R2c, R2j).

**The final test file on round 1's exporter** (a scratch copy with 014439fb): `13 failed, 285 passed in 66.24s (0:01:06)`.
- Red, each for its own reason:
  - the timing test;
  - the B2 test (3 items) and the B3 test (2 items);
  - the base64, literal-escape, head and escape tests;
  - the escaped-quote test (3 items).
- Green there by design. These pin round-1 behaviour, and each is killed by a named mutant:
  - the depth-two test (M17');
  - the `\b` and `\f` test (M20);
  - `R1_ORDINARY`'s CRLF and tab items (M2', M3').

**The verifier's six red tests** (`$V/probes/test_vscrub2r1_red.py`, 9ddf9f3c):
- They ran in a scratch copy's `tests/`, never in the tree.
- Before: `6 failed in 60.19s`. After: `6 passed in 0.59s`.
- Equivalent assertions are folded into the B2 and B3 tests and the timing test.

**The floor, twice.** Command: `masked.sh absent <scratch>/scrub2r1/empty -- bash scripts/test_summary.sh <the 12 files> --basetemp <scratch>`. Runs at 17:25Z and 17:28Z:

```
pytest-summary: 855 passed in 175.41s (0:02:55)
pytest-summary: 855 passed in 170.20s (0:02:50)
12 files set=27f27a25516b   (pc_suite.sh's set_id formula, computed locally)
```

- 855 = round 1's 841 plus this round's 14 items.
- The floor is green.

**Set A's other six**, once:
- The files: `tests/test_chat_find.py`, `tests/test_hiccup_scan.py`, `tests/test_recorded_labels.py`, `tests/test_qwen_jev.py`, `harness-ports/tests/test_hermes_session_export.py`, `harness-ports/tests/test_qwen_matrix.py`.
- The one skip is `tests/test_qwen_jev.py:37: LOUD SKIP` (it runs only in the PC's venv).

```
pytest-summary: 96 passed, 1 skipped in 35.24s
6 files set=d11be22044d4
```

**`tests/test_laya_ft.py` whole** (1 file set=8b147318aa48), on the final exporter and manifest:
- It ran in four runs by node id. One whole run takes over 10 minutes under this load; the model fixture's setup alone took up to 385 s.

```
pytest-summary: 31 passed in 285.80s (0:04:45)    (22 + 9 items; the two record tests among them)
pytest-summary: 4 passed in 177.77s (0:02:57)
pytest-summary: 4 passed in 125.68s (0:02:05)
pytest-summary: 5 passed in 240.24s (0:04:00)
```

## 5. Mutation: the kill table

**Method** (`<scratch>/scrub2r1/mutate_r2.py`, inside `masked.sh absent`):
- It runs on a scratch copy of the tree (`scripts/`, `tests/`, `pyproject.toml`, `CLAUDE.md`). The six scrubber files were checked byte-equal to the tree's first.
- The unmutated control runs first.
- Each anchor matches exactly once; this was checked for all five groups.
- Each mutated file must compile.
- KILLED only on a FAILED test (AF-AP-223).
- `PYTHONDONTWRITEBYTECODE=1`, `pytest -x`, and each group's expected count is a literal.

The runs went from 17:32Z to 17:45Z, on exporter e36f708b and test file c917c5cc. The driver's own lines:

```
group r2 (this round's named mutants)
CONTROL (unmutated): rc=0 225 passed in 6.50s
R2a B1: _PAIRS reads the rest of its run again at each pair              KILLED   1 failed, 205 passed in 43.11s | test_the_key_block_and_cookie_rules_run_in_linear_time
R2b B2: the Cookie head crosses no escaped line end                      KILLED   1 failed, 211 passed in 6.18s | test_r2_a_cookie_value_on_the_next_line_is_hidden_in_every_view[
R2c B1: _COOKIE_X stops at an escaped line end after the colon           KILLED   1 failed, 205 passed in 25.31s | test_the_key_block_and_cookie_rules_run_in_linear_time
R2d B3: the Negotiate word may end its line (\s+)                        KILLED   1 failed, 214 passed in 6.11s | test_r2_the_negotiate_token_never_takes_the_next_header[Basic]
R2e B3: the Negotiate token has no stop at another rule's head           KILLED   1 failed, 214 passed in 5.95s | test_r2_the_negotiate_token_never_takes_the_next_header[Basic]
R2f the Negotiate token takes = anywhere                                 KILLED   1 failed, 216 passed in 6.04s | test_r2_the_negotiate_token_is_base64_and_stops_before_other_hea
R2g pwd: a value may start at another rule's head                        KILLED   1 failed, 218 passed in 6.40s | test_r2_a_value_never_starts_at_another_rules_head
R2g2 credentials: a value may start at another rule's head               KILLED   1 failed, 218 passed in 6.35s | test_r2_a_value_never_starts_at_another_rules_head
R2h credentials: the floor counts escapes (_VU)                          KILLED   1 failed, 203 passed in 2.98s | test_r1_an_escaped_newline_or_tab_ends_a_value
R2i Cookie: the floor counts no backslash                                KILLED   1 failed, 217 passed in 6.34s | test_r2_a_literal_escape_in_decoded_text_keeps_the_value_hidden
R2j Cookie: an escaped line end always ends the line                     KILLED   1 failed, 205 passed in 14.79s | test_the_key_block_and_cookie_rules_run_in_linear_time
R2k an escape joins a pwd or credentials value with no value unit after it KILLED   1 failed, 219 passed in 6.15s | test_r2_an_escape_stays_in_a_value_only_before_a_value_character
R2l an escape joins a Cookie line with no line unit after it             KILLED   1 failed, 219 passed in 8.09s | test_r2_an_escape_stays_in_a_value_only_before_a_value_character
R2m _APART: a name glued to its value stands apart too                   KILLED   1 failed, 218 passed in 6.41s | test_r2_a_value_never_starts_at_another_rules_head
R2n _OTHER_HEAD: only the credential rule's names                        KILLED   1 failed, 216 passed in 6.51s | test_r2_the_negotiate_token_is_base64_and_stops_before_other_hea
R2o the scheme rule after an escaped quote crosses the line end again (\s+) KILLED   1 failed, 222 passed in 7.10s | test_r2_after_an_escaped_quote_the_scheme_token_is_on_its_own_li
R2p the scheme rule's plain head reads no further than its line          KILLED   1 failed, 222 passed in 6.70s | test_r2_after_an_escaped_quote_the_scheme_token_is_on_its_own_li
TOTAL {'KILLED': 17, 'SURVIVED': 0, 'INVALID': 0} of 17 run; group expects 17

group v5 (VERIFY-SCRUB2-R1's six survivors; M2, M3, M17 on their round-2 forms)
CONTROL (unmutated): rc=0 225 passed in 6.19s
M2' an escaped CR is a value character (no escape)                       KILLED   1 failed, 203 passed in 3.48s | test_r1_an_escaped_newline_or_tab_ends_a_value
M3' an escaped tab is a value character (no escape)                      KILLED   1 failed, 203 passed in 3.12s | test_r1_an_escaped_newline_or_tab_ends_a_value
M17' an escaped-backslash run may stand before a quote                   KILLED   1 failed, 220 passed in 6.58s | test_r2_a_value_stops_before_an_escaped_quote_at_depth_two
M20 pwd _KEY_L: no \b or \f escape                                       KILLED   1 failed, 221 passed in 7.41s | test_r2_a_pwd_name_after_a_backspace_or_form_feed_escape_is_take
M21 Negotiate floor 8 -> 12                                              KILLED   1 failed, 216 passed in 7.03s | test_r2_the_negotiate_token_is_base64_and_stops_before_other_hea
M22 Negotiate token: no + or / (base64)                                  KILLED   1 failed, 216 passed in 7.65s | test_r2_the_negotiate_token_is_base64_and_stops_before_other_hea
TOTAL {'KILLED': 6, 'SURVIVED': 0, 'INVALID': 0} of 6 run; group expects 6

group w (VERIFY-SCRUB2's 28, re-anchored)
CONTROL (unmutated): rc=0 237 passed in 7.74s
W1 cookie floor 8 -> 12                                                  KILLED   1 failed, 207 passed in 6.13s | test_the_cookie_rule_hides_what_scrub2s_rule_hid_on_plain_text
W2 cookie floor 8 -> 5                                                   KILLED   1 failed, 207 passed in 6.06s | test_the_cookie_rule_hides_what_scrub2s_rule_hid_on_plain_text
W3 authorization floor 8 -> 12                                           KILLED   1 failed, 208 passed in 5.91s | test_each_named_rule_takes_8_characters_and_leaves_7
W4 pwd floor 8 -> 12                                                     KILLED   1 failed, 208 passed in 6.38s | test_each_named_rule_takes_8_characters_and_leaves_7
W5 credentials floor 8 -> 12                                             KILLED   1 failed, 208 passed in 6.36s | test_each_named_rule_takes_8_characters_and_leaves_7
W6 negotiate dropped from the scheme rule                                KILLED   1 failed, 222 passed in 6.03s | test_r2_after_an_escaped_quote_the_scheme_token_is_on_its_own_li
W7 ntlm, key, ssws, digest dropped                                       KILLED   1 failed, 196 passed in 3.03s | test_r1_contexts_red_on_scrub2s_forms_exactly_where_verify_scrub
W8 pwd: a backslash start is a value                                     KILLED   1 failed, 209 passed in 6.28s | test_a_pwd_value_that_starts_with_a_backslash_stays
W9 pwd: a $ start is a value                                             KILLED   1 failed, 191 passed in 2.75s | test_the_shape_gaps_leave_ordinary_text
W10 escape hex upper case not an escape                                  KILLED   1 failed, 210 passed in 6.79s | test_an_upper_case_escape_separates_and_an_escaped_backslash_is_
W11 escape anchor also after an escaped quote (the verifier's edit, repaired to compile) SURVIVED 237 passed in 7.76s |
W12 opaque floor 40 -> 41                                                KILLED   1 failed, 109 passed in 1.35s | test_the_opaque_callable_gets_only_what_no_named_rule_takes
W13 PEM lenient: tabs no longer spaces                                   KILLED   1 failed, 206 passed in 5.88s | test_the_lenient_key_block_rule_hides_what_scrub2s_rule_hid
W14 PEM lenient: BLOCK suffix dropped                                    KILLED   1 failed, 206 passed in 5.74s | test_the_lenient_key_block_rule_hides_what_scrub2s_rule_hid
W15 PEM lenient: greedy body (.* not .*?)                                KILLED   1 failed, 206 passed in 5.77s | test_the_lenient_key_block_rule_hides_what_scrub2s_rule_hid
W16 cookie: stops at the first space                                     KILLED   1 failed, 190 passed in 2.89s | test_the_shape_gaps_are_scrubbed
W17 value gate: kind check inside the read loop                          KILLED   1 failed, 181 passed in 2.83s | test_a_source_of_an_unknown_kind_is_refused_before_any_source_is
W18 value gate: a directory reads as NotRegularFile                      KILLED   1 failed, 172 passed in 2.34s | test_the_value_gate_fails_closed_on_a_source_it_cannot_read
W19 value check: prefix match for the name                               KILLED   1 failed, 180 passed in 2.48s | test_a_malformed_env_line_is_named_by_its_line_number
W20 value check: lines counted from 0                                    KILLED   1 failed, 180 passed in 3.31s | test_a_malformed_env_line_is_named_by_its_line_number
W21 value check: numbered by splitlines                                  KILLED   1 failed, 236 passed in 7.45s | test_a_malformed_env_line_is_printed_as_its_line_number
W22 value check: no O_NONBLOCK (a FIFO blocks)                           KILLED   1 failed, 179 passed in 22.43s | test_a_source_that_is_not_a_regular_file_refuses_at_once
W23 value gate: raw key read with a plain open                           KILLED   1 failed, 179 passed in 22.76s | test_a_source_that_is_not_a_regular_file_refuses_at_once
W24 production tuple: TYPESAFE skip dropped                              KILLED   1 failed, 171 passed in 2.29s | test_a_hostname_does_not_block_when_its_key_holds_no_secret
W25 the autouse tripwire removed                                         KILLED   1 failed, 177 passed in 2.54s | test_a_test_that_names_no_sources_meets_the_tripwire
W26 env floor 8 -> 9 (MIN_VALUE)                                         KILLED   1 failed, 183 passed in 2.88s | test_the_8_character_floor_counts_8_and_skips_7
W27 xox right anchor lets _ in the key                                   KILLED   1 failed, 185 passed in 2.92s | test_every_provider_rule_takes_its_key_on_the_right_and_after_an
W28 sk right anchor refuses a following dash (equivalent)                SURVIVED 237 passed in 7.92s |
TOTAL {'KILLED': 26, 'SURVIVED': 2, 'INVALID': 0} of 28 run; group expects 28

group r1 (round 1's 19, re-anchored)
CONTROL (unmutated): rc=0 225 passed in 6.21s
R1a pwd: SCRUB2's left anchor                                            KILLED   1 failed, 195 passed in 2.81s | test_r1_named_rules_hold_every_f1_context_end_to_end
R1b credentials: SCRUB2's left anchor                                    KILLED   1 failed, 195 passed in 2.98s | test_r1_named_rules_hold_every_f1_context_end_to_end
R1c Cookie: \b as the left anchor                                        KILLED   1 failed, 195 passed in 2.74s | test_r1_named_rules_hold_every_f1_context_end_to_end
R1d _Q takes a bare quote only                                           KILLED   1 failed, 195 passed in 2.89s | test_r1_named_rules_hold_every_f1_context_end_to_end
R1e' an odd run before a quote is value (the backslash of an escaped quote) KILLED   1 failed, 197 passed in 3.13s | test_r1_a_value_stops_before_an_escaped_quote[echo "pwd=%s"-echo
R1f' an escaped newline is a value character (no escape)                 KILLED   1 failed, 203 passed in 2.91s | test_r1_an_escaped_newline_or_tab_ends_a_value
R1g' a tab ends a Cookie line                                            KILLED   1 failed, 203 passed in 2.90s | test_r1_an_escaped_newline_or_tab_ends_a_value
R1h' an escaped backslash pair is no value unit                          KILLED   1 failed, 210 passed in 6.31s | test_an_upper_case_escape_separates_and_an_escaped_backslash_is_
R1i credentials: SCRUB2's quoted-key head                                KILLED   1 failed, 195 passed in 3.35s | test_r1_named_rules_hold_every_f1_context_end_to_end
F2a the Negotiate rule never fires                                       KILLED   1 failed, 204 passed in 3.17s | test_every_authorization_scheme_hides_its_token
F2b the Negotiate token takes a following Bearer                         KILLED   1 failed, 204 passed in 3.00s | test_every_authorization_scheme_hides_its_token
F7a no start guard on the lenient head                                   KILLED   1 failed, 205 passed in 43.03s | test_the_key_block_and_cookie_rules_run_in_linear_time
F7b the END read with -{3,}                                              KILLED   1 failed, 205 passed in 43.95s | test_the_key_block_and_cookie_rules_run_in_linear_time
F7c a head with no END scans again (the .* branch dropped)               KILLED   1 failed, 205 passed in 28.58s | test_the_key_block_and_cookie_rules_run_in_linear_time
F7d the shared END never read (102+ dashes)                              KILLED   1 failed, 206 passed in 5.85s | test_the_lenient_key_block_rule_hides_what_scrub2s_rule_hid
F7e the Cookie no-value branch dropped                                   KILLED   1 failed, 205 passed in 43.33s | test_the_key_block_and_cookie_rules_run_in_linear_time
F7f _COOKIE_X never matches (a later head that crosses the line end is swallowed) KILLED   1 failed, 207 passed in 6.15s | test_the_cookie_rule_hides_what_scrub2s_rule_hid_on_plain_text
R1j' the backslash of an escaped quote stays in a Cookie line            KILLED   1 failed, 199 passed in 2.96s | test_r1_a_value_stops_before_an_escaped_quote[echo "Cookie: sid=
R1k the scheme rule's token takes a backslash                            KILLED   1 failed, 118 passed in 1.27s | test_a_credential_behind_an_escaped_quote_is_redacted[obj8-Zk1lR
TOTAL {'KILLED': 19, 'SURVIVED': 0, 'INVALID': 0} of 19 run; group expects 19

group se (PATTERN_NAMES)
CONTROL (unmutated): rc=0 73 passed in 22.72s
N1 PATTERN_NAMES: pwd <-> credentials                                    KILLED   1 failed, 72 passed in 22.90s | test_each_gate_pattern_name_labels_its_own_rule
N2 PATTERN_NAMES: cookie <-> authorization-scheme                        KILLED   1 failed, 25 passed in 20.46s | test_gate_counts_patterns_and_canaries_and_prints_none
N3 PATTERN_NAMES: private-key <-> private-key-malformed                  KILLED   1 failed, 72 passed in 22.36s | test_each_gate_pattern_name_labels_its_own_rule
N4 PATTERN_NAMES: one name dropped (count 23)                            KILLED   1 failed, 1 passed in 2.78s | test_no_canary_survives_the_export
N5 PATTERN_NAMES: sk-key <-> github-token                                KILLED   1 failed, 25 passed in 20.37s | test_gate_counts_patterns_and_canaries_and_prints_none
N6 PATTERN_NAMES: opaque-run <-> bridge-link                             KILLED   1 failed, 1 passed in 2.52s | test_no_canary_survives_the_export
N7 PATTERN_NAMES: an extra name (count 25)                               KILLED   1 failed, 1 passed in 2.52s | test_no_canary_survives_the_export
N8 PATTERN_NAMES: authorization-negotiate <-> credential                 KILLED   1 failed, 25 passed in 19.71s | test_gate_counts_patterns_and_canaries_and_prints_none
TOTAL {'KILLED': 8, 'SURVIVED': 0, 'INVALID': 0} of 8 run; group expects 8
```

- **The two survivors are equivalent:**
  - W11: `(?<![A-Za-z0-9])` already holds after any quote.
  - W28: the class already takes every dash, so no dash can follow the run.
- **Re-anchored this round:**
  - W3, on the scheme rule's shared floor;
  - W6 and W7, on `_SCHEME`;
  - R1k, on the scheme rule's token class;
  - the v5 forms (D3).

## 6. Measurement (item 6)

**Method.** The same as measure3, in `<scratch>/scrub2r1/measure4.py`, `measure5.py` and `measure6.py`:
- A candidate rule list and its base both run with character provenance. Each run is asserted equal to the real output.
- NEW means hidden now and shown by the base. LOST means hidden by the base and shown now.
- The scripts keep counts and masked shapes only. No region text leaves the process.
- Views: `dec` is every string of a record, decoded. `raw` is the raw JSONL line.

**Corpus:**

| Source | Size |
|---|---|
| The committed digests | 20 |
| The main transcript, fixed | 763,973,021 bytes; 148,711 lines; 4,144,420 strings |
| 358 subagent transcripts (this lane's own excluded) | 595,442,190 bytes at 14:07Z |
| The second project root | 3,074,681 bytes; 519 lines; 13,731 strings |

**Cells** are texts changed / NEW regions / LOST regions.
- The base is the PIN (cdbc1b8's exporter, 6ad316dc).
- Two rows differ: R2/R1's base is round 1's list, and FIX's base is this round's list before D2's fix.

```
cand     digest  main/dec  main/raw  sub/dec   sub/raw   root2/dec root2/raw
NEG2     0/0/0   0/0/0     0/0/0     5/7/0     4/7/0     0/0/0     0/0/0
COOKIE2  0/0/0   0/0/0     1/0/2     7/8/2     10/12/28  0/0/0     0/0/0
PWD2     0/0/0   0/0/0     2/0/4     2/6/0     16/19/31  0/0/0     0/0/0
CRED2    0/0/0   10/0/12   6/0/14    13/2/27   21/16/34  0/0/0     0/0/0
AUTH-R2  0/0/0   0/0/0     0/0/0     0/0/0     4/5/0     0/0/0     0/0/0
FINAL2   0/0/0   10/0/12   7/0/20    17/23/29  31/58/93  0/0/0     0/0/0
R2/R1    0/0/0   16/14/2   5/25/0    9/42/23   10/26/22  0/0/0     0/0/0
FIX      0/0/0   0/0/0     0/0/0     0/0/0     0/0/0     0/0/0     0/0/0
```

**Where each row comes from:**
- **NEG2, COOKIE2, PWD2, CRED2, FINAL2 and R2/R1:** `measure4.py`, from 14:07Z to 14:25Z, on the list before D2's fix.
- **FIX:** `measure6.py`, from 16:31Z to 16:48Z, on the same file list. The subagent transcripts had grown to 599,134,185 bytes by then.
  - The fix changes no text of the corpus in any view, so the rows above stand for the final list.
  - Its self-test on a fake fixture did see the fix: FIX dec NEW 1, LOST 1.
- **AUTH-R2** is the PIN with this round's scheme rule. Its 5 NEW regions are round 1's F1 gains (`\"authorization\": \"bearer <token>` in raw JSON), the same as round 1's AUTH row.

**FINAL2's 154 LOST regions, sorted by masked shape** (`m4-all.json`). "Committed" means the exact region text, at least 6 characters, occurs in a tracked file.

| Count | Class | Views | Committed |
|---|---|---|---|
| 90 | F5: the backslash of a closing escaped quote after a value (JSON validity; round 1's F5 class) | main/raw 8, sub/dec 1, sub/raw 81 | too short to test |
| 43 | F15 and D1: a credentials value that passed the PIN's floor only through an escape, then the next line's words | main/dec 10, main/raw 10, sub/dec 22, sub/raw 1 | 31 committed (F15 quotes in sources, tests and reports); 12 are the verifier's probe texts |
| 5 | F15-class pwd: a Windows path `C:\...` of 6 decoded characters, over the PIN's floor only because the raw view counts `\\` as two characters | main/raw 2, sub/raw 3 | the PIN's decoded view shows it too |
| 11 | D6: another rule's head word (`credentials=`, `Authorization:`, `credentials:`) | main/dec 2, sub/dec 5, sub/raw 4 | all committed |
| 5 | A lone escape or whitespace, after a Cookie head or trailing a value | sub/dec 1, sub/raw 4 | too short to test |

**`measure5.py`: round 2 against round 1, each region placed by the PIN.** It ran before D2's fix; FIX is 0, so it holds for the final list.

| Class | Regions | By view | What they are |
|---|---|---|---|
| NEW RESTORED | 97 | main/dec 14, main/raw 25, sub/dec 38, sub/raw 20 | the PIN hid them and round 1 showed them |
| NEW BEYOND | 10 | sub/dec 4, sub/raw 6 | the PIN showed them too: a Cookie line after a literal `\n` running into code or a Markdown table, in the verifier's probe texts |
| LOST PIN-HID | 11 | | D6's head words |
| LOST R1-ONLY | 36 | sub/dec 18, sub/raw 18 | head words that round 1's Negotiate token took (B3's class) |

**V4's added over-redaction:**
- BEYOND's 10 regions.
- Plus the raw view's 45 RESTORED regions (main/raw 25, sub/raw 20). These are SCRUB2's old over-redaction of the next line across an escaped line end, back for pwd and Cookie (D12).
- The reason:
  - in decoded text a literal `\n` is two characters of the value (a Windows path, a regex);
  - the same bytes in raw JSON are a line end, and the scrubber has no view flag;
  - so keeping every decoded redaction the PIN made brings back the raw one too.
- An escape still ends a value when no value unit follows it, for example a line end and then whitespace.

## 7. Timing census

**Method:** `<scratch>/scrub2r1/rule_timing2.py drive <exporter>`.
- Each of the 28 rules runs alone against 78 hostile families, at 4,000 to 64,000 characters.
- One child per rule and family, with a 12 s timeout.
- A rule is flagged when it grows more than x3 per doubling at over 0.02 s.

The final rules (f9b92269, the same compiled rules as e36f708b), at 17:04Z:

```
S00 -----BEGIN [A-Z0-9 ]*(?:PRIVATE|SECRET)                worst 0.0015 s (5-dash BEGIN, no END)
S01 (?<!-)-{3,}[ \t]*BEGIN [A-Z0-9 ]*(?:PRIV               worst 0.0037 s (BEGIN head + dash body)
S02 ((?i:authorization)(?:\\*[\"'])?\s*:\s*(               worst 0.0284 s (Negotiate + base64 run)
S03 ((?:AGENT_TOKEN|PC_BRIDGE_TOKEN|X-Agent-               worst 0.0259 s (Negotiate + token= words)
S04 (Bearer\s+)(?=[A-Za-z0-9._\-]{8})(?:(?!(               worst 0.0007 s (Bearer heads)
S05 ((?:(?<![A-Za-z0-9])|(?<=\\[nrtbf])|(?<=               worst 0.0558 s (cookie: heads, 1 line)
S06 ((?i:authorization)(?:[\"']?\s*:\s*[\"']               worst 0.0430 s (authorization spaces)
S07 ((?:(?<![A-Za-z0-9])|(?<=\\[nrtbf])|(?<=               worst 0.0280 s (pwd= heads)
S08 ((?:(?<![A-Za-z0-9])|(?<=\\[nrtbf])|(?<=               worst 0.0268 s (credentials= heads)
S09 (?:(?<![A-Za-z0-9])|(?<=\\[nrtbf])|(?<=\               worst 0.0081 s (credentials = heads)
S10 (?:(?<![A-Za-z0-9])|(?<=\\[nrtbf])|(?<=\               worst 0.0077 s (pwd backslashes)
S11 (?:(?<![A-Za-z0-9])|(?<=\\[nrtbf])|(?<=\               worst 0.0070 s (\u0000 escapes)
S12 (?:(?<![A-Za-z0-9])|(?<=\\[nrtbf])|(?<=\               worst 0.0072 s (ghp_ runs)
S13 https?://[a-z0-9\-]+\.trycloudflare\.com               worst 0.0022 s (Negotiate + base64 run)
S14 (?:\b|(?a:\b))[A-Za-z0-9_\-]{40,}(?:\b|(               worst 0.0052 s (\u0000 escapes)
P00 (?<![A-Za-z0-9\-])(?:[A-Za-z0-9\-]+\.)+t               worst 3.9736 s (x.trycloudflare labels)
P01 ((?-i:Bearer)\s+<redacted>)[~+/=][A-Za-z               worst 0.0004 s (Bearer heads)
P02 ((?i:authorization)(?:\\*[\"'])?\s*:\s*(               worst 0.0060 s (authorization spaces)
P03 ((?:(?:AGENT_TOKEN|PC_BRIDGE_TOKEN|X-Age               worst 0.0404 s (pwd=a\n heads)
P04 (\b[A-Za-z][A-Za-z0-9+.\-]*://[^\s/:@'\"               worst 4.0524 s (x.trycloudflare labels)
P05 ((?i:authorization)(?:\\*[\"'])?\s*[:=]\               worst 0.0119 s (authorization spaces)
P06 ((?<![A-Za-z0-9_.\-])curl\b[^\n|;&]{0,20               worst 0.4051 s (curl -x runs)
P07 ((?<![A-Za-z0-9])(?:[A-Za-z0-9]*[_-]PASS               worst 0.0167 s (x_PASS= heads)
P08 ((?<![A-Za-z0-9+.\-])[A-Za-z][A-Za-z0-9+               worst 0.0054 s (pwd=a\n heads)
X_ASSIGN_LINE                                              worst 2.4900 s (spaces)
X_KEY_RUN                                                  worst 0.0044 s (backslashes)
X_TOKEN_LINE                                               worst 0.0025 s (dash run + BEGIN)
X_CUT                                                      worst 0.0309 s (NAME=v lines)
SUPER-LINEAR (growth > x3 per doubling at > 0.02 s, or a 12 s timeout):
  S03 ((?:AGENT_TOKEN|PC_BRIDGE_TOKEN|X-Ag cookie: heads, 1 line        4000:0.001 8000:0.002 16000:0.003 32000:0.007 64000:0.023 x3.5
  S03 ((?:AGENT_TOKEN|PC_BRIDGE_TOKEN|X-Ag ghp_ runs                    4000:0.001 8000:0.002 16000:0.003 32000:0.006 64000:0.022 x3.5
  S03 ((?:AGENT_TOKEN|PC_BRIDGE_TOKEN|X-Ag pwd=a + escaped backslash pairs + quote 4006:0.002 8006:0.002 16006:0.003 32006:0.008 64006:0.026 x3.2
  S05 ((?:(?<![A-Za-z0-9])|(?<=\\[nrtbf])| cookie: heads, 1 line        4000:0.002 8000:0.004 16000:0.008 32000:0.017 64000:0.056 x3.2
  P00 (?<![A-Za-z0-9\-])(?:[A-Za-z0-9\-]+\ a. labels                    4000:0.146 8000:0.562 16000:3.106 x5.5
  P00 (?<![A-Za-z0-9\-])(?:[A-Za-z0-9\-]+\ x.trycloudflare labels       4012:0.089 8012:0.297 16012:0.920 32012:3.974 x4.3
  P03 ((?:(?:AGENT_TOKEN|PC_BRIDGE_TOKEN|X curl -x runs                 4000:0.001 8000:0.003 16000:0.005 32000:0.010 64000:0.036 x3.6
  P04 (\b[A-Za-z][A-Za-z0-9+.\-]*://[^\s/: a. labels                    4000:0.015 8000:0.060 16000:0.240 32000:0.929 64000:3.933 x4.2
  P04 (\b[A-Za-z][A-Za-z0-9+.\-]*://[^\s/: a- runs                      4000:0.015 8000:0.086 16000:0.265 32000:1.027 64000:3.977 x3.9
  P04 (\b[A-Za-z][A-Za-z0-9+.\-]*://[^\s/: sk- runs                     3999:0.010 7998:0.078 15999:0.162 31998:0.706 63999:2.683 x3.8
  P04 (\b[A-Za-z][A-Za-z0-9+.\-]*://[^\s/: x.trycloudflare labels       4012:0.018 8012:0.059 16012:0.235 32012:0.982 64012:4.052 x4.1
  X_ASSIGN_LINE                            spaces                       4000:0.500 8000:2.490 x5.0
  X_CUT                                    Cookie: a=bcdefghij + backslashes 4020:0.001 8020:0.002 16020:0.004 32020:0.007 64020:0.028 x3.8
drive: 199 s
```

The PIN (6ad316dc), at 14:50Z. The worst lines of the rules this round changed, and its super-linear list:

```
S04 ((?i:\b(?:set-)?cookie)[\"']?\s*:\s*[\"'               worst 3.0839 s (cookie: heads, 1 line)
S05 ((?i:authorization)[\"']?\s*:\s*[\"']?(?               worst 0.0097 s (authorization spaces)
S06 ((?<![A-Za-z0-9])(?i:pwd)[\"']?\s*[:=]\s               worst 0.0046 s (pwd=credentials = runs)
S07 ((?<![A-Za-z0-9])(?i:credentials)(?:[\"'               worst 0.0036 s (é-dash runs)
P00 worst 4.0137 s; P04 worst 4.2523 s; X_ASSIGN_LINE worst 1.9537 s; P06 worst 0.3888 s; X_CUT worst 0.0271 s (no flag)
SUPER-LINEAR: S01 (7 families; the lenient key-block rule round 1 fixed), S02 (cookie: heads, 1 line, 0.024 s, x3.9),
S04 (cookie: heads 3.084 s; Set-Cookie: heads 2.772 s; Set-Cookie:\r\n heads 2.018 s), P00 (2 families), P04 (4 families),
X_ASSIGN_LINE (spaces)
```

**The rules changed this round, final against the PIN:**

| Rule | Final worst | PIN worst |
|---|---|---|
| Negotiate (S02) | 0.0284 s | none: the PIN has no such rule |
| Cookie (S05) | 0.0558 s | 3.0839 s, super-linear |
| scheme (S06) | 0.0430 s | 0.0097 s |
| pwd (S07) | 0.0280 s | 0.0046 s |
| credentials (S08) | 0.0268 s | 0.0036 s |

**The flags on S03, S05, P03 and X_CUT are noise near the threshold.** Re-timed in process, best of three, on the regexes alone:

| Rule, family | 64k | 128k | 256k | 512k |
|---|---|---|---|---|
| S03, "cookie: heads, 1 line" | 0.0188 | 0.0240 | 0.0489 | 0.1140 |
| S05, the same family | 0.0247 | 0.0455 | 0.1239 | 0.2413 |
| S06, "authorization spaces" | 0.0225 | 0.0459 | 0.0979 | 0.1748 |

- P03 is the PIN's own regex. Three child runs each on the final and the PIN gave 0.022 to 0.037 s at 64,000 characters, with growth near x2.
- X_CUT is the PIN's regex too; the PIN's run had no flag on it.

**P00, P04 and X_ASSIGN_LINE are super-linear on both the PIN and the final.** These are task #333's three older rules, unchanged.

**Final against round 1**, `<scratch>/scrub2r1/cmp_r1.py`:
- Each changed rule runs on every family at 16,000 and then 64,000 characters, best of three, in process.
- A family where a version takes over 0.5 s at 16,000 is not run further.

```
Negotiate    families where round 1 is quadratic (skipped): 0 | final over 2x round 1 at 64k (and > 5 ms): [('Negotiate + base64 run', 0.0041, 0.027)] | max ratio (6.65, 'Negotiate + base64 run')
Cookie       families where round 1 is quadratic (skipped): 3 | final over 2x round 1 at 64k (and > 5 ms): [('Cookie: a=b + escaped newlines', 0.0071, 0.0147), ('Cookie: + escaped newline x runs', 0.006, 0.0168)] | max ratio (2.8, 'Cookie: + escaped newline x runs')
scheme       families where round 1 is quadratic (skipped): 0 | final over 2x round 1 at 64k (and > 5 ms): none | max ratio (1.8, 'authorization spaces')
pwd          families where round 1 is quadratic (skipped): 1 | final over 2x round 1 at 64k (and > 5 ms): [('pwd escaped quotes', 0.0091, 0.0203), ('pwd=a + backslashes + quote', 0.0042, 0.0087), ('pwd=a + escaped newlines', 0.0041, 0.011), ('pwd=a + escaped newlines + quote', 0.0041, 0.011)] | max ratio (2.68, 'pwd=a + escaped newlines')
credentials  families where round 1 is quadratic (skipped): 1 | final over 2x round 1 at 64k (and > 5 ms): none | max ratio (1.64, 'pwd=a + escaped backslash pairs + quote')
```

- Five families that were quadratic in round 1 are linear now.
- On seven families a changed rule costs 2 to 6.6 times round 1's constant. All of them stay under 0.03 s at 64,000 characters (D7).

**Extra families through the whole `scrub()` and `scrub_payload()`** (`<scratch>/scrub2r1/extra_fam.py`):
- The texts use real line ends after Cookie, pwd and Negotiate heads, plus mixed escapes and heads.
- All grow about x2 per doubling up to 64,000 characters.
- They cost 1.1 to 4.4 times the PIN's constant.

## 8. The Laya lock

**The pre-fit comparison** (`<scratch>/scrub2r1/laya_r2.py`):
- It runs the builder's own collection with `common.scrub` bound in turn to four scrubbers:
  - the PIN;
  - the tree's exporter;
  - the N-pwd control: the PIN with `pwd` among its credential names;
  - the E control: the PIN's scrub, then every `e` changed to `E`.
- It compares whole items, on the tree at f9b92269 (the same compiled rules as e36f708b).

```
v2 collect_v2 at 434b727dfd   new differs from the PIN in 0 items (lengths 6220 vs 6220)
                              N-pwd control differs in 16 items; the new scrub equals the PIN on 16 of them
                              E control differs in 6220 items
v1 collect at eb256f49c0      new 0 of 1788; N-pwd control 0; E control 1788
v1 collect at 0b342c7a29      new 0 of 1788; N-pwd control 0; E control 1788
common.scrub is the tree's exporter (the new one): True, in each run
```

**0 items changed, so K265's step ran next.**
- The command: `HF_HUB_OFFLINE=1 /root/venv-laya-probe/bin/python scripts/laya_ft/build_dataset.py --version 2 --commit 434b727dfd2b6daa5aa3cf4d638e706f5dfa59cb --out <scratch>/scrub2r1/v2new --model-dir /root/hf-laya-probe/hub/models--convaiinnovations--laya/snapshots/1c5edc17a7acd8701df6fc341c0d179f1c62c982/typed-decisions`.
- It ran inside `masked.sh absent`, on the final exporter, at 17:19Z. Exit code 0.
- `dataset.jsonl`: sha256 99070c33830832ca11e64226eddac1934ccd300c73b4d5d8d8c7bf5a36271f9d, 12,800,855 bytes. That equals the record's `dataset` field.
- The manifest differs from HEAD's in one line, the exporter hash: 6ad316dc… to e36f708b….
- It was copied over the recorded manifest. The record tests pass (section 4, the first Laya run).

**The digests** (round 1's check, `<scratch>/scrub2r1/digests_r2.py`):
- This session's main transcript, fixed at 769,872,662 bytes, was exported with `sources=()` by two exporters:
  - the PIN: a scratch tree of cdbc1b8's `transcript_export.py` and `known_values_check.py`;
  - the final exporter.
- Result: `identical: 20 of 20; differ: []`.
- `new digests: 20 files, 3794708 bytes, sha256 of the concatenation 12cab720ace9cd70`.
- 19 of the 20 are byte-equal to the committed digests. Today's `chat-2026-09-28.md` differs because the transcript grew after it was committed.
- The new digests are kept in `<scratch>/scrub2r1/digests-r2-new/` for the coordinator's known-value check.

## 9. Gates

- **pyflakes: exit code 0** on `scripts/transcript_export.py`, `tests/test_transcript_export.py`, `scripts/session_export.py`, `tests/test_session_export.py` and `scripts/known_values_check.py`.
- **The separator grep** (`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`) prints 0 for each file written: the exporter, the test file and the manifest.
  - This report is a message, not a file (D16), and it holds no such character.
- **`scripts/ap_screen.py --limit 100000`**, on the two code files and (with `--tests`) the two test files: 17 hits, 0 inside this lane's changed lines.
- **GitNexus `detect-changes --scope all`:** `Changes: 9 files, 53 symbols`, `Affected processes: 5`, `Risk level: medium`.
  - Three of the nine files belong to LS-B7: `scripts/install_session_hooks.py`, its test, and `.claude/settings.json`.
  - The index is 41+ commits behind, so it still names round 1's removed `_VE` and `_CV`.
  - The five flows are `scrub()`'s callers: Search, Main, Render, Cmd_label and On_text.
- **`impact SECRET_PATTERNS`:** risk UNKNOWN, no callers resolved.
  - It is a module-level list, read by `scrub()`, `scrub_payload()` and the `session_export` names test.
  - It was checked by text.
- **Test isolation**, with `<scratch>/scrub2r1/trace_r1.sh` at 17:45Z:
  - it applies strace to file syscalls with the verifier's filter and environment logger;
  - it ran on both changed test files (298 items).

  | Mode | Source opens | Token lookups | Note |
  |---|---|---|---|
  | absent | 0 | 0 | |
  | fakes | 0 | 0 | 1 `newfstatat` of the copy's fake `.pc-bridge.env`: pytest's collection stat, not an open |
  | control | 1, 1, 1 | 1 | a scratch test that opens the three planted fakes and reads GH_TOKEN; the trace sees it |

## 10. NOT-done

- **V11 is not fixed.** It is pre-existing: plain and bare heads still leak the next header's credential in 20 of 22 texts per form, as on the PIN. It is task #319's scope, not this round's.
- **V12 is not fixed.** Fixing it would also hide the one raw K token in `rand_lost2`.
- **Task #333's three older rules** (P00, P04, X_ASSIGN_LINE) are still super-linear, as on the PIN.
- **F3, F8, F16, F17 and V10** are not in this round.
- **The OpenJev manifest** is not regenerated (round 1's D8).
- **The known-value check** of `<scratch>/scrub2r1/digests-r2-new/` is the coordinator's, at landing.
- **The report file** was not written: the harness refused (D16).
- **Not done here:** independent verification, and any commit.

## 11. DISCREPANCIES

**D1. V4 and F15 conflict on one shape, and F15 wins (1 cell, 14 tokens).**
- Two texts are the same bytes to the scrubber:
  - the decoded `credentials=abc\n<value>`, where `\n` is a literal backslash and n: two characters;
  - F15-2's raw `_CREDENTIALS=0\nnext_step_here`, where `\n` is a JSON line end.
- `scrub()` and `scrub_payload()` each run on both views, so no view flag exists inside the boundary.
- The credentials floor counts no escape. So F15's named shapes stay removed, and a decoded value with an escape before its eighth unit shows.
- The options:
  - (a) a view flag passed in by the callers, which is outside this boundary;
  - (b) count escapes in the credentials floor, which is mutant R2h. It brings back F15-2's over-redaction, and R2h reds the F15 test.
- pwd has no named F15 shape, so its floor counts escapes (V4).

**D2. A new defect was found and fixed: B3's shape after an escaped quote.**
- My own probe found it during round 2, after the first final.
- The cause:
  - round 1 gave the scheme rule `_Q`, so it read escaped-quote heads. The PIN's `[\"']?` never did.
  - The scheme rule's `\s+` then crossed the line end.
- The fix:
  - plain and bare-quoted heads keep the PIN's head and its `\s+`;
  - after an escaped quote, the token must be on the scheme's own line.
- Rejected designs:
  - `[ \t]+` for every head. It loses the PIN's redaction of a token on the next line (`Authorization: Basic` then `  <token>`).
  - An `_OTHER_HEAD` stop on the token. It also fixes V11, which is out of scope, and it still lets the Negotiate entry take a word from the next line.
- The verifier's V11 probed plain heads only.
- The fix added one test (3 items), two mutants (R2o, R2p) and two measurement rows (AUTH-R2, FIX).

**D3. M2, M3, M17 and M22 are tested in their round-2 forms.**
- The classes they mutated (`_VE`, `_CV`) no longer exist.
- M2' and M3' remove `\r` or `\t` from the escape set of `_ODD` and `_ESC` together. The escape then becomes a value character.
- M3 mutated the Cookie class. A Cookie line now takes an escaped tab by design (`_LODD`), so M3' mutates the pwd and credentials escape set instead.
- M17' lets an even run stand before a quote in `_PAIRS`.
- M22' removes only `+` and `/`, because `=` is now padding only (D5).

**D4. `_COOKIE_X` differs from the brief's wording.**
- The brief says: "`_COOKIE_X` stops at a colon followed by an escaped line break."
- That form made each head read the rest of its line:
  - on 64,000 characters of escaped Cookie heads, the Cookie rule took 1.9 s (x3.9 per doubling);
  - on CRLF heads, 1.02 s (x4.3).
- The final form stops before a later head only when its colon is followed by whitespace, escaped line ends or tabs, and then a real line end or a quote.
- Mutant R2c (the brief's form) is KILLED by the timing test.

**D5. The Negotiate token's `_OTHER_HEAD` stop, and `=` as padding only, go beyond B3's literal fix.**
- With `[ \t]+` alone, the same-line case still leaked: `Authorization: Negotiate Authorization: Basic <v>`.
- With `=` allowed inside the token, `Cookie: x Authorization: Negotiate =zqheads:<v>` lost a PIN redaction: the Cookie rule's floor found no `=` left.
- Both are pinned by mutants (R2e, R2f).

**D6. 11 head words the PIN hid now show. A ruling is needed.**
- `_APART` means a pwd or credentials value never starts at another rule's head that stands apart. A head stands apart when a quote or whitespace comes before its `:` or `=`, or when no value character follows them.
- Without it, a value that began at the next head hid that head, and the head's own value then showed. This is AF-AP-157, found by VERIFY-SCRUB2-R1's differential.
- 4 texts in `test_r2_a_value_never_starts_at_another_rules_head` cover it. The PIN hid each value.
- The cost on the corpus is 11 regions, all header names, all committed:
  - `credentials=` in a code string: 2;
  - `Authorization:`: 6;
  - `credentials:`: 3.
- The text after each is hidden by its own rule, or shown by the PIN too.
- V4 says no PIN redaction may be lost. These are redactions of names, not values. The coordinator must rule.

**D7. "No rule may get slower": no rule's growth class got worse, but some constants did.**
- Every rule changed in either round is linear on the 78 census families and on the extra families.
- The unchanged rules are the PIN's regexes.
- Against round 1, seven families cost 2 to 6.6 times its constant, all under 0.03 s at 64,000 characters. Two causes:
  - the `_OTHER_HEAD` check at each Negotiate token character;
  - V4's escape lookahead.

**D8. HEAD moved five times during the round, docs only.**
- The sequence:
  - 1b7fec8 at resume;
  - 34d3af0: the coordinator's `reset --keep`, with the owner's authorization;
  - then d7609d8, 4bdb6b1, c4b87d1 and 50c5daa.
- No commit touched a scrubber file, a floor test, `scripts/` or the Laya findings.
- The floor set stayed 12 files set=27f27a25516b.
- This lane's files matched their last write after each move.
- Other lanes' live files (LS-B7, LS-B9) sit in the tree; none is in this lane's floor.

**D9. V12 is not fixed.** It is out of scope. A V12 fix would hide the one raw K token in `rand_lost2`.

**D10. A one-character Negotiate token is hidden.**
- The token's 8-character floor reads the run ahead, but the token stops at `_OTHER_HEAD`. So in `Authorization: Negotiate _Authorization: ...` the token is just `_`.
- This is 8 regions on the corpus (FINAL2 NEW, in the verifier's probes).
- It over-redacts one character:
  - the PIN showed the `_`;
  - round 1 took the whole `_Authorization` and freed the next header's value.

**D11. W6 is no longer equivalent.**
- Round 1 called it equivalent, because the Negotiate rule took every token first.
- Round 2's Negotiate rule refuses a token that is not base64. After an escaped quote, the scheme rule's `negotiate` entry then takes it (`Authorization: \"Negotiate ab=<v>`).
- A new assertion now kills W6.

**D12. V4 reverses round 1's F15-class removal for pwd and Cookie.**
- F15 named credentials only.
- Round 1 also removed, for pwd and Cookie, the over-redaction across an escaped line end.
- V4's continuation brings it back when the next line starts with a value unit:
  - in raw JSON, `pwd=abcdefgh\r\nnext` now hides `next`;
  - with whitespace first (`\r\n  next`), the value ends at the line end.
- The cost is in section 6.

**D13.** The 10 raw F15-consistent tokens are kept under F15's ruling (section 3, V4).

**D14.** V1 falsified round 1's report, section 3 and its self-attack 3, on the backslash classes. This round's census has backslash families for every changed rule.

**D15.** The measurement corpus holds the verifier's own probe texts, in subagent transcripts. Most of FINAL2's sub/raw LOST regions and measure5's BEYOND regions come from them.

**D16. The harness refused the report-file write.**
- The exporter comment at lines 191-195 names `tasks/briefs/system1/SCRUB2-R1-R2-report.md, D1`.
- That file exists only once this message is saved there.

## 12. Self-attack

1. **The split scheme rule loses a PIN redaction.** Ruled out:
   - its first branch is the PIN's head, byte for byte, with `\s+`;
   - the second branch can match only where the first cannot, which is after an escaped quote;
   - `probe_w6b.py`: plain and bare forms leak 20 of 22 on the final and on the PIN alike;
   - FIX: 0 changed texts on the whole corpus;
   - the Laya lock: 0 items changed.
2. **V4's continuation brings back quadratic time.** An escape run followed by a non-unit backtracks through the run once per attempt, and attempts start only at a head. Ruled out by measurement:
   - the census: 78 families, every changed rule;
   - `LINEAR_CHILD`: 30,000 escaped newlines after a pwd head;
   - the re-timing up to 512,000 characters (x2 per doubling);
   - killed mutants for each stop (R2a, R2c, R2j).
3. **A kept class hides a real leak.** D1 is a real risk, and it is not ruled out for future text:
   - in decoded text, a secret after `credentials=` whose first 8 units hold a literal `\n`, `\r`, `\t` or `\f` shows;
   - measured: every such region on the corpus is an F15 shape or a quote of one (31 committed, 12 in the verifier's probes), and none is a credential;
   - D6 shows names only;
   - this is the cost of F15's ruling, stated in D1.

## 13. Evidence tiers

- **Verified** (run here, output pasted): every count and time in sections 3 to 9, the red and green runs, the kill table, the Laya lock and the rebuild, the digests, and the isolation trace.
- **Inferred:**
  - The measure4 and measure5 rows stand for the final list: FIX is 0 on the same files, and the rules differ only in the scheme rule.
  - The census, the V4 probes and the Laya lock ran on f9b92269 or te_r2e.py. They stand for e36f708b: the compiled rule lists are equal (checked), and the later edits are comments only (checked token by token).
- **Assumed:** the verifier's probes (`$V/probes/*`) measure what their docstrings say. I read them but did not audit them line by line.

## 14. Scratch

`<scratch>` is `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad`.

**Kept** in `<scratch>/scrub2r1/` (9 MB):
- Instruments: `mutate_r2.py`, `rule_timing2.py`, `cmp_r1.py`, `extra_fam.py`, `measure4.py`, `measure5.py`, `measure6.py`, `laya_r2.py`, `digests_r2.py`, `probe_w6.py`, `probe_w6b.py`, `r2/vrun.py`, `r2/vrun2.py`, `r2/cls2.py`.
- Their outputs: `m4-*.json`, `m5-*.json`, `m6-*.json`, `census-*.txt`, `kill-*.txt`, `floor*.txt`, `laya-*.out`.
- `digests-r2-new/`, and `v2new/manifest.json` with `summary.json`.
- The exporter versions: `r2/te_r1.py`, `r2/te_r2d.py`, `r2/te_r2e.py`, `te_pin.py`.

**Deleted:**
- the scratch trees: `c/`, `red2/`, `mt2/`, `after/`, `r2/root_r1/`, `r2/root_r2/`, `pintree/`;
- the PIN's digests, the basetemps, and the rebuilt `dataset.jsonl`.

Nothing was written under `$V`.