# VERIFY-SCRUB2-R1-R2 report (task #321): the scrubber repair's round 2, attacked

<!-- Coordinator note (2026-09-28): this report is the lane's hand-back, extracted verbatim from its transcript by `python3 scripts/stack.py harvest agent=a90d7cc077452b42d` (run s-20260928T204245Z-c9cdaa; hand-back sha256 584a0d9a56d4; 436 assistant records, all claude-opus-5-5, 0 refusal stops). The harness refused the lane's own write of this file. Its red tests and its N1 candidate are kept beside it in `tasks/briefs/system1/vscrub2r2/`. -->


**Gate recommendation: NOT-READY.** Two findings meet the whole blocking predicate. Both are V4 losses (round 2, item 4: "no redaction the PIN makes may be lost in any view"), and no ruling covers either:
- **N1, floor units.** The pwd and credentials floors count a backslash pair (or a whole even run), an odd run, and a whole group of escapes as ONE unit each; the PIN counted characters. A value of 8 or more characters with literal backslash content now falls under the floor. It shows where the PIN hid it: in the digest, in `convert()`'s text events, and, for a literal pair, in canonical JSON too.
- **N2, a newly read head swallows the next head (AF-AP-157).** Round 1 made the Cookie, pwd and credentials heads read heads the PIN never read: `\"Cookie\": \"`, `my_cookie:`, a head after a literal `\t` or `\r`, an escaped-quote key. Such a head's value can run over a later pwd, credentials or Cookie head and stop right before that head's value, at a quote or a real line end. The PIN hid that value; round 2 shows it. This answers the brief's item 4 question: the sibling rules still read escaped-quote heads.

Both reproduce through `export()` and `convert()` at the lane's bytes, and both have red tests (FAILED on round 2, passed on the PIN). Both fixes belong in `scripts/transcript_export.py`. For N1 I built a fix candidate in scratch: it loses 0 tokens that round 2 hides, loses 110 fewer overall, and all 298 committed test items pass. So N1 is not a CONTRACT-INVALID case: it can be fixed while F15 stays removed and D1 stays as ruled. The recommendation depends on nothing I did not reproduce.

**D-034 reading:** in my judgment both are CORE-BLOCKING. The round's headline is V4, and the verify brief's own WHY names "a rule that hides LESS than before" as the risk. On these shapes the credential screen fails open, and the builder's "V4 closed" claim holds only for its own instruments' alphabet. Exposure: on this session's corpus both classes occur only in probe or test texts, with 0 live-credential shapes. That is the same position as F7 and V1, which were ruled blocking. If you judge them edge cases under D-034 instead, the recommendation becomes MERGE-READY-WITH-FOLLOWUPS.

Everything else the brief asked about holds: B1, B2, B3, D2's fix, D6 (under your ruling), D7 on the real corpus, F1, F15, F2, F7, F10, F12, the value gate, test isolation, the Laya lock, the digest identity, and every builder mutant I re-ran. Seven round-2 clauses are pinned by no test (FOLLOW-UP).

Lane: sandbox Opus 5.5, adversarial verifier. No subagents, no git writes, no bridge, and nothing written in the shared tree. Stamp from `date -u`: 2026-09-28 20:37:25Z (bucket 20:3xZ).
- **Report file: not written.** The harness tells subagents to return findings as text, not report files, and it refused the builder's write the same way (its D16). This message is the whole report, per the brief's fallback.
- **Paths:** `W` = `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2r2` (65 MB at the end); `S` = the scratchpad root.

## 1. Premise, re-measured (18:4xZ)

| Premise line | Measured | Verdict |
|---|---|---|
| HEAD fc4d1a1 | da9daeb at start (this brief's commit), 0d06ae7 at the end. `git log da9daeb..HEAD` on the lane's files and `known_values_check.py`: 0 | holds; the new commits touch docs only |
| `git status`: 5 files M | the same 5 | holds |
| sha256 prefixes | e36f708b5515cd36, 0462fe2e9bdd14bc, c917c5ccaf08074a, c1bb29a1ec924a71, 8d5427fdac6ee5f8; builder report 9f8458c240020749 | holds at start and again at 20:35Z |
| `git diff --stat` | 3 files, 562 insertions, 15 deletions | holds |
| probes, `masked.sh` | present | holds |
| free disk 1,300 MB | 1,304 MB at start, about 11,800 MB later (freed by someone else) | holds |

No CONTRACT-INVALID.

## 2. Gates, pasted

**The copy:** `W/new` is a `git archive HEAD` of `scripts/`, `tests/`, the Laya findings, `pyproject.toml` and `CLAUDE.md`, with the lane's five files on top (hashes equal the premise). The floor's tests also read `src/`, `.claude/` and four findings dirs, which I added from HEAD. Every run was inside `masked.sh absent` with `--basetemp` under `W`.

```
floor pass 1 (18:52:37Z)
pytest-exit: 0
pytest-summary: 855 passed in 166.30s (0:02:46)
12 files set=27f27a25516b
floor pass 2 (18:55:36Z)
pytest-exit: 0
pytest-summary: 855 passed in 152.82s (0:02:32)
12 files set=27f27a25516b
```

Venue-only failures came first, each naming a file missing from the copy (never a scrubber test):
- `2 errors in 1.94s`: no `src/` and no `.claude/hooks`.
- `12 failed, 843 passed`: no `.claude/skills` and no `j2c-fulltext`.
- `6 failed, 849 passed`: no `j2-v1-probe`, `ap-hawk-probe`, `j2b-variants` or `COUNCIL-VERDICT-JEV-LAYA-v1.md`.

```
VERIFY-SCRUB2-R1's red tests (9ddf9f3cc3b3a34e), 1 files set=ca17e58537f1
round 2: pytest-exit: 0  pytest-summary: 6 passed in 0.77s
round 1: pytest-exit: 1  pytest-summary: 6 failed in 60.20s (0:01:00)
PIN:     pytest-exit: 0  pytest-summary: 6 passed in 0.29s
this verifier's red tests (W/probes/test_vscrub2r1r2_red.py), 1 files set=bcd44bc128b4
round 2: pytest-exit: 1  pytest-summary: 16 failed in 0.11s
PIN:     pytest-exit: 0  pytest-summary: 16 passed in 0.04s
round 1: pytest-exit: 1  pytest-summary: 11 failed, 5 passed in 0.09s
```

**Static checks:** pyflakes gives rc 0 on the four code files. `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` prints 0 for all five lane files.

## 3. Finding inventory (no severity filter)

Evidence: R = reproduced here through the named path; S = read from source; U = not verified.

### N1 — BLOCKER: the pwd and credentials floors count backslash content as single units (V4)

**What:** `_VF` and `_VU` (`scripts/transcript_export.py:86-87`) each read one of these as ONE unit:
- a backslash pair, or a whole even run (`_PAIRS`);
- an odd run (`_ODD`);
- a whole group of escapes (`_ESC`, with its `+`).

The pwd floor `(?=_VU{8})` (line 196) and the credentials floor `(?=_VF{8})` (line 199) count those units. The PIN counted characters (`[^\s"'&,;]{8}`).

**Examples, in decoded text (the PIN hid each; round 2 shows each):**
- `pwd="Pa\\w0rd"`: 8 characters, 7 units.
- `pwd=ab\ncdef`: 8 characters, 7 units.
- `pwd=M1\n\nab`: an escape group counts as one unit.
- `credentials=K12\\abc`: a pair, not an escape, so D1 does not cover it.

**In canonical JSON:** a decoded pair becomes four backslashes, and `_PAIRS` takes the whole run as one unit. So an 8-character decoded value with one pair shows in a tool call. The PIN hid it in both views, so this is a true loss, not an F15-consistent one. Round 1 counted per pair and hid these, so here round 2 regressed from round 1.

**Measured (R):**
- `floor_units.py` (77 rows), round 2 LOST cells: pwd heads 9 of 10 shapes decoded; credentials 10 of 10. In every raw view, 3 of 10 shapes (the pair and odd-run shapes). Cookie 0: its floor reads characters.
- `rand_v4b.py` (character-provenance differential, 4,000 texts, two seeds): true decoded losses beyond D1 are 48 and 42 tokens. D1's class (K) is 698 and 680.
- End to end (`e2e_floor.py`, `e2e_n2.py`, twice with fresh fakes). The digest LEAKs a user turn `pwd="<8 chars, one pair>"` and `credentials=<8 chars, one pair>`. `convert()` LEAKs those two, a tool result `PWD: <9 chars with \n\n>`, and a Bash input `--pwd=<8 chars, one pair>` (a tool_call). The PIN hid all of them.
- **Why the instruments missed it:** `lost_shapes.py`, `rand_lost2.py` and the test file's `R2_LITERAL` always put a 12- to 32-character fake after the escape, so the unit count always clears 8.
- **Corpus** (`corpus_scan.py`): decoded N1 regions are 0 in the main transcript and 13 in subagent transcripts. Every shape is probe or test code (string concatenations, F15's own quoted shape). No live-credential shape.

**Blocking predicate:**
1. **Contract mapping:** round 2 item 4, "in every view", and "a literal backslash-n … may no longer cut a pwd or credentials value … where the PIN hid the whole value". Evidence demand 3: "the LOST cells and the lost fake tokens go to 0; a cell you keep needs the ruling in item 4 and a stated reason". No ruling covers N1: D1 is credentials escapes before the eighth unit, and pwd has no F15 shape (the builder's own D1).
2. **Canonical path:** `export()` and `convert()` at e36f708b.
3. **Material effect:** a value the PIN hid reaches the committed digest and the session export. Exposure today is probe texts only.
4. **Discriminator:** 13 red items (`test_n1_*`), FAILED on round 2 and passed on the PIN.
5. **Ownership:** the classes and floors are this round's code.

**Fix (feasible; scratch candidate `W/probes/candidate_n1_te.py`, not a spec):**
- The pwd floor reads characters as the PIN's did: `(?=[^\s"'&,;]{8})`.
- The credentials floor counts characters before the first escape (a callable), so F15's shapes keep their next line and D1 stays.

**On the candidate:**
- Both changed test files pass (298 items), and N1's 13 red items pass.
- `rand_v4b`: 0 tokens lost that round 2 hides; 110 fewer lost.
- `floor_units`: only the 7 D1 escape cells per credentials head remain.
- Not timed beyond the committed timing test, which passes.

**Reproduce:**
- `cd $W/probes && python3 floor_units.py`
- `$S/vscrub1/masked.sh absent $W/vrun -- python3 $W/probes/e2e_floor.py`
- `$S/vscrub1/masked.sh absent $W/vrun -- python3 $W/probes/e2e_n2.py` (its N1-raw row)
- Copy `$W/probes/test_vscrub2r1r2_red.py` into a copy's `tests/` and run it.

### N2 — BLOCKER: a head the PIN never read swallows the next head (AF-AP-157; the item 4 sibling)

**What:** round 1 (F1) gave the Cookie head `_KEY_L`, which accepts a head after `_`, a non-ASCII letter or a literal escape letter, and `_Q` escaped quotes. pwd and credentials got the same. When such a head's value runs over a later pwd, credentials or Cookie head and ends right before that head's value, the later value shows. The PIN never read the first head, so the later rule hid its value.

**Shapes:**
- `{\"Cookie\": \"sid=<c>; pwd='<v>'\"}`
- `my_cookie: session=<c>; db_pwd="<v>"`
- `my_cookie: sid=<c>; pwd:`, newline, `  <v>`
- `my_cookie: sid=<c>; Path=/ Cookie:`, newline, `  sid=<v>`
- In the credentials rule itself: `\"credentials\": écredentials = <v>`, and `x\tcredentials==credentials = <v>`, where `\t` is literal.
- A variant through `_APART`: `pwd="credentials": cookie:credentials =  <v>`. `_APART` stops pwd there, so the credentials rule takes the first head, and its value swallows the second.

**Measured (R):**
- End to end (`e2e_n2.py`, twice): 4 of 4 Cookie shapes LEAK on round 2 (the digest for the two user turns; `convert()` for all four). The PIN hid all four. Round 2 hides the cookie values the PIN showed, so it trades one value for another.
- `rand_v4b`: 18 and 20 tokens per 4,000 texts.
- `rl2_prov.py` (rand_lost2's generator, provenance): 4 decoded and 10 raw value regions in 20,000 texts.
- **Corpus:** 16 regions in subagent transcripts, all the credentials rule's escaped-quote head, all in probe texts. 0 in the main transcript.

**Blocking predicate:**
1. **Contract mapping:** round 2 item 4 and item 7 (round 1's item 5), and AF-AP-157, task #198's invariant for this file. The brief's item 4 asks this exact question.
2. **Canonical path:** `export()` and `convert()`.
3. **Material effect:** a pwd, credentials or Cookie value the PIN hid reaches the digest and the session export. Exposure today is probe texts only.
4. **Discriminator:** 3 red items (`test_n2_*`), FAILED on round 2 and passed on the PIN.
5. **Ownership:** the heads and values are this round's code (lines 90-102 and 166-199).

**Fix direction (not built):** do what D2 did for the scheme rule. Plain heads stay as the PIN read them. A head the PIN never read gets a value that stops before a later head that stands apart, like the Negotiate token's `_OTHER_HEAD` stop. Moving the Cookie rule after pwd and credentials is another option. Measure the cost, as item 6 asks.

**Reproduce:** `$S/vscrub1/masked.sh absent $W/vrun -- python3 $W/probes/e2e_n2.py`, plus the red items `test_n2_*`.

### F-MUT — FOLLOW-UP: seven clauses changed in either round are pinned by no test (R)

I wrote 19 mutants, one per round-2 clause the builder's set does not cover (`W/probes/mut.py new`): 11 KILLED, 8 SURVIVED. A differential (6,000 texts, plus shapes aimed at each clause) shows seven survivors change what is hidden: each shows a fake that round 2 hides.

| Mutant | Clause | Texts that differ | Texts where the mutant leaks more |
|---|---|---|---|
| X3 | `_LESC` reads one escape per unit (no `+`) | 189 | 23 |
| X6 | `_COOKIE_X`: no escaped line end or tab after the colon | 5 | targeted: a decoded `Cookie: a Cookie:\n`, newline, value |
| X7 | `_NAMES` without cookie | 296 | 31 |
| X8 | `_NAMES` without pwd | 94 | 29 |
| X10 | `_OTHER_HEAD` reads no escaped quote | 0 | targeted: `Negotiate abcdefghpwd\": \"<v>` |
| X13 | the Negotiate token has no stop before a bridge link | 34 | 7 |
| X14 | the Negotiate head reads no escaped quote | 375 | 124 |

- X17 (an escaped tab after the Cookie colon is no whitespace) changes output text only: 100 texts, 0 leaks.
- KILLED: X1, X2, X4, X5, X9, X11, X12, X15, X16, X18, X19.
- **Fix:** one assertion per survivor.

### F-DOC — FOLLOW-UP: the pwd and credentials comment understates the floor's cost (S)

- Line 191: "The pwd floor counts escapes (_VU, V4)" implies decoded parity, which N1 shows is not there.
- Lines 193-195 state D1's cost as escapes only. Pairs, odd runs and escape groups also keep a value under the floor.
- The builder's D1 and its section 12 carry the same understatement.
- **Fix:** with N1.

### V-B1 — INFO: B1 holds; every rule is linear on backslash runs (R)

- `bs_timing` (8 families, 8,000 to 64,000 characters): growth about x2 per doubling. Worst `scrub` 0.085 s (`pwd+bs+x`); worst `scrub_payload` 0.10 s. The builder measured round 1 at 4.4 to 9.5 s at 32,000.
- End to end at 32,000 backslashes: `export()` 0.03 to 0.04 s, `convert()` 0.21 to 0.25 s. PIN: 0.01 to 0.02 s and 0.04 to 0.18 s.
- `census2.py`: 65 families × 8 targets, including families built for `_APART`, `_OTHER_HEAD`, `_COOKIE_X`, escape groups, `_Q` runs, and dash, space, tab and quote runs.
  - Worst single rule 0.049 s; `scrub()` 0.12 s; `scrub_payload()` 0.17 s.
  - Twelve rows were flagged on one noisy step. Re-timed to 512,000, best of 3, every one grows x1.8 to x2.5 per doubling.
  - **Control:** the same census on the PIN flags its known quadratics: the lenient key block at 12.1 s on 32,000 dashes, SCRUB2's Cookie rule at 3.7 s.
- Per rule, round 2 is slower than the PIN on its own worst family, but linear: pwd 0.026 against 0.008 s; credentials 0.026 against 0.003 s.

### V-D7 — INFO: D7's constants are harmless on the real corpus (R)

- **20 committed digests (3,732,291 characters):**
  - `scrub()`: PIN 2.787 s, round 1 3.231 s, round 2 3.156 s (1.13x the PIN).
  - `scrub_payload()`: 4.881 s, 5.738 s, 5.407 s (1.11x).
- **`convert()`** over the main transcript's first 52,449,077 bytes (6,736 events, best of 2): PIN 25.4 s, round 1 28.0 s, round 2 27.8 s (1.09x).

### V-B2 — INFO: B2 holds (R)

- `e2e_yaml.py`: every place is hidden on round 2 and on the PIN.
- `b2b3_var.py`: 455 texts (7 head forms × 13 separators, real and escaped × 5 value forms), 6 views. LOST 0.
- Round 2 shows 0 in the decoded views and 21 in canonical JSON (the PIN 195). The 21 are a decoded literal two-character `\n` before a quoted value, which both versions show (V12's pre-existing class).
- The red test's three shapes pass.

### V-B3 — INFO: B3 holds (R)

- `e2e_neg.py`: every path hides the value on round 2 and on the PIN.
- `b2b3_var.py`: 672 texts, 0 LOST.
- The Negotiate rule matches none of those texts, in four encodings. It never takes the next line's word.

### V-D2 — INFO: D2's fix holds for the scheme rule (R)

`d2_sib.py`: 12 schemes × 5 quote forms × 4 line ends × 6 following headers = 1,440 texts, 6 views. 0 texts lost against the PIN. The sibling rules are N2.

### V-D6 — INFO: D6 holds under your ruling (R)

- **The builder's 11 regions,** rebuilt from `m4-all.json`'s masked shapes with fresh letters:
  - `credentials=`: followed by `" + a("…")`, which the PIN shows too.
  - `Authorization:`: followed by `Negotiate` (the credential rule hides it on both versions), then a 3-letter token both versions show.
  - `credentials:`: followed by a CamelCase word the PIN shows too.
- **Corpus:** every lost name-and-separator region, by provenance. Main transcript 2, all PINSHOW. Subagents 39: 10 HID, 29 PINSHOW. 0 values lost.
- **Structure:** `_APART` fires only where the PIN's value stopped at whitespace, a quote or a separator right after the name. The PIN's redaction there covered the name alone.

### V-F — INFO: item 7 holds: F1, F15, F2, F7, F10, F12, the value gate (R)

- **F1** (VERIFY-SCRUB2's scripts through my re-pointed runner `after_v2.py`):
  - `escape_named.py`: before (SCRUB2's committed code), 13 of 20 named-rule cells leak (3 LEAK/LEAK, 10 hid/LEAK). Round 2: 20 of 20 hid/hid.
  - `escape_nonascii.py`: 12 of 12 hid.
- **F15:** `cred_convert.py` prints `ordinary words gone: []` twice. Before: `['None)', 'rows']` and `['next_step_here', '=0']`.
- **F2:** `negotiate.py` prints `token survives in: none` for Negotiate. Before: `scrub, scrub_payload`.
- **F7:** the lenient key-block rule's worst census time is 0.003 s; the PIN's was 12.1 s.
- **F10:** the se mutant N1 is killed, and the F10 test passes in the floor.
- **F12:** W1 to W5, W7, W8, W10 and W13 to W15, re-run with the builder's anchors: 11 of 11 KILLED by a FAILED test.
- **Value gate:** `known_values_check.py` is HEAD's bytes (cfdf2ffec10e6d10). The diff touches no gate line, and the gate's tests pass in the floor.

### V-ISO — INFO: test isolation holds (R)

The previous verifier's `trace.sh` (strace on every process's file syscalls, plus a token-lookup logger), over the two changed test files (2 files set=e8f27bcb91e7):
- **absent:** `298 passed in 40.99s`. 0 syscalls on any source path; 0 token lookups.
- **fakes:** `298 passed in 44.76s`. 0 opens. The copy's fake `.pc-bridge.env` sees one `newfstatat` and two ENOTDIR probes, all from pytest's venv detection.
- **control** (a scratch test that opens the three planted fakes and reads GH_TOKEN): 1 open each, 1 lookup.

### V-LAYA — INFO: the Laya lock holds (R)

The pre-fit comparison (`laya_lock.py`) on the lane's exporter:
- **v2** `collect_v2` at 434b727dfd: round 2 differs from the PIN in 0 of 6,220 items. Controls: N-pwd changes 16 items, and round 2 equals the PIN on all 16; E changes 6,220.
- **v1** `collect` at eb256f49c0 and at 0b342c7a29: 0 of 1,788 items each; the E control changes all 1,788.
- **The recorded manifest** differs from HEAD in one line, which holds e36f708b's full sha256. The OpenJev manifest is untouched.

### V-ROWS — INFO: item 6's rows, partly reproduced (R)

- **Digest identity:** the main transcript, fixed at 774,854,705 bytes, exported with `sources=()` by the PIN and by round 2. Identical 20 of 20; 19 byte-equal to the committed digests. `chat-2026-09-28.md` differs because the transcript grew. This matches the builder.
- **`corpus_scan.py`** (`scrub()`, character provenance; texts changed / NEW regions / LOST regions):
  - main/raw 7/0/20: equal to the builder's FINAL2 main/raw.
  - main/dec 15/0/17, against the builder's 10/0/12. The transcript has grown about 10 MB since its fixed end, and the added regions are K (D1) and D6 PINSHOW.
  - The subagent rows (dec 81/101/187, raw 98/147/364) are not comparable: that corpus has grown since 14:07Z (the builder's own final probes, two verify lanes).
- **Classes on the corpus:** F5 315; ESC 19; K 162; D6 41 (0 lost); N1 35; the credentials-head form of N2 16. N1's `main/raw 2` is the builder's F15-consistent Windows path.

### V-MUT — INFO: the builder's mutants, re-run (R)

- With the builder's anchors in my driver (KILLED only on a FAILED test): R2b, R2g, R2d, R2k, M2', M22, R1d and N1 are 8 of 8 KILLED, each by the test the builder names. F12's eleven: 11 of 11.
- **W11 and W28 survive and are equivalent.** 0 of 6,000 texts differ in `scrub`, `scrub_payload` and canonical JSON. W11's added lookbehind is implied by `(?<![A-Za-z0-9])` after a quote. W28's class takes every dash, so no dash can follow the run.

### I-D1 — INFO: D1 reproduces exactly as the builder states (R)

- `lost_shapes`: 1 LOST cell (credentials literal-bs-n split, decoded).
- `rand_lost2`: decoded B-literal 13; raw F15-consistent 10; raw TRUE-LOSS NEW-dec-hides 1.
- D1 is a real conflict between item 4 and F15's ruling on identical bytes. Evidence demand 3 allows it as a kept cell. My N1 candidate keeps D1 as it is.

### I-RAW — INFO: the generator's raw F-class losses are F15-consistent (R)

- `rand_v4b`'s raw F-class losses (197 and 212 tokens) are all shown by the PIN's own decoded view. The PIN's raw floor hid them only by counting the backslashes of an escaped quote (F5's class).
- The raw losses that are not consistent are N1's 8-character values with a literal pair.

### I-PRE — INFO: pre-existing classes, both versions (R)

- V12's class: a decoded literal `\n` before a quoted Cookie value shows in canonical JSON.
- `Authorization: Negotiate abcdefghpassword\": \"<v>\"`: `scrub()` shows `<v>`; `scrub_payload`'s R1 rule hides it.

### I-PROC — INFO: my process slips (none touched the shared tree)

- The harness's rm safety check stopped one command with an unguarded `$W/$t` target; it did not run. Every later removal uses `${W:?}`.
- My first two provenance versions had artifacts:
  - difflib aligned a token's letter with a letter of `<redacted>`;
  - the K and F checks counted escape letters as lost.
  Both were fixed and self-tested before the corpus numbers above.
- My first N1-raw value was 9 characters (`token_hex(1)` gives two); I fixed it to 8 and re-ran.
- My probe loaders cached bytecode inside `W/new` only. The shared tree's recent `.pyc` files belong to other lanes whose pytest runs were live.

## 4. Contract status

**Round 2's items:**

| Item | Status |
|---|---|
| 1 B1 | holds (V-B1) |
| 2 B2 | holds (V-B2) |
| 3 B3 | holds (V-B3) |
| 4 V4 | fails: N1, N2. D1 kept under its ruling; D6 holds under your ruling |
| 5 V5 | holds. The builder's v5 kill file shows 6 of 6; I re-ran M2' and M22 |
| 6 V21 | the two named comments hold; the pwd/credentials comment understates (F-DOC) |
| 7 round 1 | holds (V-F, V-ISO, V-LAYA, V-ROWS) |

**The brief's WHAT TO ATTACK:**
1. B1 and D7: hold.
2. B2 and B3: hold.
3. V4: fails (N1, N2). D6 shown, region by region and on the corpus.
4. D2: the fix holds; the sibling rules are N2.
5. Item 7: holds.
6. Mutation: done. 8 builder mutants and F12's 11 KILLED; W11 and W28 equivalent; 19 new mutants.

## 5. What I skipped, and why

- The dataset rebuild with the Laya venv: the pre-fit comparison is the contract's lock, and the builder and the previous verifier rebuilt it.
- The whole `tests/test_laya_ft.py` and set A's other six files: not in this brief's gate; the floor is.
- The builder's full mutant groups: I re-ran 8 of them, W11, W28 and F12's eleven.
- An N2 fix candidate: direction only.
- The subagent rows at the builder's fixed file list: that corpus has grown since.
- GitNexus `detect-changes`: the index is stale, and it bears on nothing here.
- The PC: no bridge, by rule.

## 6. DISCREPANCIES

- The brief asks for a report file. The harness tells subagents to return text, and it refused the builder's write. This message is the report.
- HEAD moved from da9daeb to 0d06ae7, docs only.
- Free disk rose from 1,304 MB to about 11,800 MB (not my action).
- The builder's "V4 is closed except the kept classes" is false (N1, N2). Its `lost_shapes` and `rand_lost2` numbers are true, but those instruments cannot draw short values or newly read heads.
- The copy needed more of HEAD than the brief lists (`src/`, `.claude/`, four findings dirs) before the floor would run.

## 7. Files (all under `W`)

- `probes/test_vscrub2r1r2_red.py`: the 16 red items (N1 13, N2 3).
- `probes/lib.py`, `prov.py`: the six views and the exact character-provenance instrument.
- N1 and N2: `probes/floor_units.py`, `floor_units2.py`, `e2e_floor.py`, `e2e_n2.py`, `rand_v4b.py`, `rand_v4b_variants.py`, `rl2_prov.py`.
- `probes/candidate_n1_te.py`: the N1 feasibility candidate (not a spec).
- Timing: `probes/census2.py`, `convert_time.py`; outputs `census_new.txt`, `census_pin.txt`.
- D2, B2, B3: `probes/d2_sib.py`, `b2b3_var.py`.
- Corpus and digests: `probes/corpus_scan.py`, `digests_id.py`; outputs `scan_main.json`, `scan_sub4.json`.
- Mutation: `probes/mut.py`, `surv_diff.py`; outputs `mut_rep.txt`, `mut_new.txt`, `mut_f12.txt`.
- F1, F15, F2: `probes/after_v2.py`; outputs `f1f15f2.txt`, `escn_before.txt`, `escn_after.txt`.
- `results.txt` (the raw numbers), `floor1.txt`, `floor2.txt`.
- `new/`: the scratch copy (HEAD plus the lane's files). `pintree/` and `r1tree/`: the PIN and round 1.

**Gate recommendation: NOT-READY.** The blockers are N1 and N2. They reproduce with `e2e_floor.py`, `e2e_n2.py` and the red file `test_vscrub2r1r2_red.py` (round 2: 16 failed; PIN: 16 passed).
