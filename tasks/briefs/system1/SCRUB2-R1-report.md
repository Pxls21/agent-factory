# SCRUB2-R1 report (task #321): the scrubber repair wave after VERIFY-SCRUB2

Lane: code-implementer (sandbox, Opus 5.5). Started 2026-09-26 (bucket 08:2xZ). Written incrementally.
Brief: `tasks/briefs/system1/SCRUB2-R1-brief.md`. Contract: `tasks/briefs/system1/SCRUB2-brief.md` items 1-8. Findings:
`tasks/briefs/system1/VERIFY-SCRUB2-report.md` sections 14 and 15. Scratch: `<scratch>/scrub2r1/` (`<scratch>` =
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad`).

## STATUS

BUILT and self-checked (10:4xZ); not yet verified independently, and nothing committed. Items 1-3 built; items 4-8 hold.
- Floor, twice: `841 passed in 132.84s` and `841 passed in 131.17s`, 12 files set=27f27a25516b (824 + 17 new items).
- Other consumers: `96 passed, 1 skipped in 24.55s`, 6 files set=d11be22044d4; `tests/test_laya_ft.py` whole:
  `44 passed in 576.05s`, 1 file set=8b147318aa48; the record tests: `2 passed, 42 deselected in 117.62s`.
- The new tests on the PIN's scripts: `12 failed, 272 passed in 58.39s`, each red for its own reason.
- Mutation: this lane's 19 all KILLED; VERIFY-SCRUB2's 28: 25 KILLED (the eleven F12 survivors among them), 3 equivalent
  survivors (W6, W11, W28); `PATTERN_NAMES` 8 of 8 KILLED; 0 INVALID.
- Read first: D1 (a reversed conclusion on the lenient rule's design) and D16 (sections 2 and 3 re-run on the final file).

## 1. Premise, re-measured (08:3xZ)

| # | Premise line | Measured now | Verdict |
|---|---|---|---|
| P1 | origin tip 7a050b6 | origin tip 59229eb ("transcripts: scrubbed sandbox chat digests"), local HEAD = 59229eb, the tree clean. 7a050b6..59229eb changes 11 files: docs, briefs, `deploy/qwen.container`, one committed digest (`transcripts/sandbox/chat-2026-09-26.md`); no file under `scripts/`, `tests/`, `src/` or the Laya manifests | holds (the dispatch message names 59229eb) |
| P2 | `git log cdbc1b8..origin -- <3 scrubber files> \| wc -l` = 0 | 0 | holds |
| P3 | the rule lines 64-70, 78-106 | identical text and numbers (`_KEY_L` 67, lenient PEM 81, credential 88, Cookie 95, pwd 103, credentials 105); exporter sha256 6ad316dccfca0147 = SCRUB2's landed file | holds |
| P4 | `PATTERN_NAMES` at `session_export.py:136`, 23 names | identical | holds |
| P5 | the 12 files that name a scrubber file | the same 12 | holds |
| P6 | the floor: 824 passed, 12 files set=27f27a25516b | below | holds |

```
$ printf '%s\n' <the 12 files> | sort | sha256sum | cut -c1-12     (pc_suite.sh's set_id, run as its own pipeline)
27f27a25516b
$ masked.sh absent <scratch>/scrub2r1/empty -- bash scripts/test_summary.sh <the 12 files> --basetemp=<scratch>/scrub2r1/bt/p
pytest-exit: 0
pytest-summary: 824 passed in 120.82s (0:02:00)
```
Verdict: the premise holds. No CONTRACT-INVALID.

## 2. The verifier's reproductions, before and after (evidence demand 2) (09:0xZ)

Every command ran inside `masked.sh absent <scratch>/scrub2r1/empty` (the real sources unreachable; guard booleans all
True). BEFORE = the verifier's scripts as they are: their TARGET root `vscrub2/t` holds cdbc1b8's scrubber bytes, which
are this round's PIN (sha256 prefixes checked equal to the tree's before the change: exporter 6ad316dccfca0147,
session_export 68c712893ffed4e9, known_values_check cfdf2ffec10e6d10). AFTER = `<scratch>/scrub2r1/after.py <script>`,
which runs the same script text with exactly two swaps, each asserted to occur once and printed: the TARGET root becomes
`<scratch>/scrub2r1/after` (the same copy with this lane's final `transcript_export.py` 014439fb2694d273 and
`session_export.py` 0462fe2e9bdd14bc on top, its bytecode caches removed), and the work directory moves into this lane's
scratch. The PIN column of the escape scripts stays SCRUB2's PIN (4b3b699), as the verifier ran them.
**The AFTER column was first run at 08:5xZ on this lane's FIRST lenient-rule design (b81784c5615524df, section 9 D1), and
re-run on the final file at 10:2xZ (section 9 D16). The lines below are the final file's. F1, F15 and F2 printed the same
lines both times (the rules they exercise are byte-identical in the two files); the F7 numbers moved within noise.**

**F1** (`escape_named.py`, TARGET digest/convert; the PIN column unchanged, LEAK everywhere but `password=`):
```
                                      BEFORE      AFTER
pwd=           line start             hid/LEAK    hid/hid
pwd=           after a tab            hid/LEAK    hid/hid
pwd=           JSON doc (\" quotes)   hid/LEAK    hid/hid
pwd=           literal \n             LEAK/LEAK   hid/hid
credentials=   line start             hid/LEAK    hid/hid
credentials=   after a tab            hid/LEAK    hid/hid
credentials=   JSON doc (\" quotes)   hid/LEAK    hid/hid
credentials=   literal \n             LEAK/LEAK   hid/hid
Cookie:        line start             hid/LEAK    hid/hid
Cookie:        after a tab            hid/LEAK    hid/hid
Cookie:        JSON doc (\" quotes)   hid/LEAK    hid/hid
Cookie:        literal \n             LEAK/LEAK   hid/hid
Authorization: Token  JSON doc        hid/LEAK    hid/hid
every other cell (the plain controls, the passphrase and password controls, Token in the other contexts)   hid/hid both
```
`escape_nonascii.py`: BEFORE `Cookie: sid=` after é LEAK/LEAK, after の LEAK/LEAK, every other target cell hid/hid;
AFTER every target cell hid/hid (12 of 12).

**F15** (`cred_convert.py`, the target's convert()):
```
BEFORE  T redacted: True | ordinary words gone: ['None)', 'rows']
        T redacted: True | ordinary words gone: ['next_step_here', '=0']
AFTER   T redacted: False | ordinary words gone: []
        T redacted: False | ordinary words gone: []
```
**F2** (`negotiate.py`): BEFORE `Negotiate  token survives in: scrub, scrub_payload`; AFTER `none` for all 11 schemes.

**F7** (`timing_run.py scrub 26 27`, the dashes family, n = 250/500/1000/2000 = 7,500 to 60,000 dashes, 20 s child cap):
```
BEFORE  t 0.5387 1.8935 7.7384 TIMEOUT>20s x4.1 | pin 0.0018 0.0036 0.0072 0.0135 x1.9
AFTER   ../scrub2r1/after 0.0051 0.0094 0.0194 0.0357 x1.8 | t 0.4774 1.8969 7.7326 TIMEOUT>20s x4.1
        (the first design, 08:5xZ: after 0.0047 0.0098 0.0178 0.0363 x2.0 | t 0.5188 1.9578 7.8372 TIMEOUT>20s x4.0)
```
(`timing_run.py` prints the text length of the last call that finished, so its `len@2000` label reads 30000 in the
AFTER line: the PIN column's n=1000. The after-root finished n=2000, 60,000 dashes, in 0.0357 s.)
`e2e_timing.py 15000 dashes`: BEFORE `T export() 1.88 s, convert() 3.70 s`; AFTER `T export() 0.01 s, convert() 0.03 s`
(`P` 0.00 s and 0.02 s both times). AFTER at 60,000 dashes: `export() 0.05 s, convert() 0.20 s` (the first design: 0.04 s
and 0.19 s).

## 3. Every rule in the file, timed (item 2's check) (09:0xZ)

`<scratch>/scrub2r1/rule_timing.py`: each rule of `SECRET_PATTERNS` and `PAYLOAD_PATTERNS`, and the strict pass's
`_ASSIGN_LINE`, `_KEY_RUN`, `_TOKEN_LINE` and `_CUT`, alone (`pattern.sub`), over 55 hostile families (dash runs, BEGIN
heads with and without END, cookie and Authorization heads, `pwd`/`credentials`/`token` heads, backslash, space, quote and
`_` runs, `a.` labels, `a-` and `a:` and `a@` runs, `://` runs, curl heads, `_PASS` runs, escapes, provider prefixes,
non-ASCII glue), sizes 4,000 to 64,000 characters doubling, one child per rule and family (12 s cap). Flag: growth over
x3 per doubling above 0.02 s, or a timeout. The PIN file (6ad316dc):
```
S01 lenient PEM   dashes 16000:2.186 x4.1 | dash run + BEGIN 16027:2.056 x4.1 | 4-dash BEGIN, no END 63990:4.662 x4.1
                  spaced 3-dash BEGIN 63986:1.166 x4.0 | 4-dash BEGIN + wrong END 63960:3.201 x4.2
                  5-dash BEGIN, no END 32000:2.919 x4.0 | BEGIN head + dash body 8030:2.722 x4.1
S04 Cookie        cookie: heads, 1 line 64000:2.743 x3.9 | Set-Cookie: heads 63998:2.636 x4.2
P00 bridge host   a. labels 32000:5.664 x4.0 | x.trycloudflare labels 32012:2.033 x4.1
P04 url-password  a. labels 64000:2.428 x3.6 | a- runs 64000:2.545 x4.2 | sk- runs 63999:1.644 x3.8 | labels 2.355 x4.0
X_ASSIGN_LINE     spaces 16000:5.499 x4.0
(P03 escaped-credential flagged x3.4 at 0.021 s; re-timed alone to 512,000 characters: 0.0142, 0.0272, 0.0566, 0.1312 s,
linear. Every other rule: worst under 0.03 s, linear.)
```
The final file (014439fb; `rule_timing.py drive te_new.py S0 S1`, re-run at 10:2xZ, 37 s): every secret rule linear, no
flag. Worst S01 (the lenient rule) 0.0026 s (BEGIN head + dash body), S05 (Cookie) 0.0251 s (Set-Cookie: heads). The
first census, at 08:5xZ, ran on the first lenient design (b81784c5, D1, D16): S01 0.0026 s and S05 0.0224 s too, and one
flag, S11 (the AIza rule, unchanged) x29.9 at 0.106 s on one family, which re-timed alone to 512,000 characters (best of
three) as 0.0033, 0.0061, 0.0132, 0.0261 s, linear (load from the other lanes). The Cookie rule (byte-identical in both
files) re-timed to 512,000 characters: new 0.0155, 0.0313, 0.0782, 0.1646 s; the PIN's 2.5061, 10.1688, 41.1589 s (the
512,000 call was stopped by pid at 311 s).

So the class has five members in this file: S01 (F7) and S04 (SCRUB2's Cookie rule), both fixed here; and three that
predate SCRUB2 and stay as they are, reported (NOT fixed: outside the contract's named rules; see DISCREPANCIES):
P00 (`(?:[A-Za-z0-9\-]+\.)+trycloudflare\.com`: its start lookbehind allows a start after every `.`, and each start scans
the remaining labels), P04 (`\b[A-Za-z][A-Za-z0-9+.\-]*://`: `\b` lets every `.`, `-` or `+` restart the scheme, the same
class the last payload rule's comment records as fixed there), and `_ASSIGN_LINE` (two `[ \t]*` around an optional group
at a line start: the split points of a space run are tried in pairs).

**Why AF-AP-152's edit screen did not fire on line 81** (`.claude/hooks/edit-snapshot.py:327`; `python3
scripts/ap_screen.py scripts/transcript_export.py` on the PIN file prints hits for AF-AP-204 and AP-1 only). The tell has
two shapes: (1) a quantified group `(?:...)` whose body ends with a character its own quantified class also takes
(exponential backtracking), and (2) an alternative after `|` that opens with a quantified `[class]` followed by literal
word characters. Line 81 opens the PATTERN (no `|`) with a quantified LITERAL, `-{3,}` (not a `[class]`, and `{3,}`, not
`*` or `+`), so neither shape reads it. Its second cost is not a quantifier shape at all: a lazy `.*?` body that scans
to the end of the text once per BEGIN head, times many heads. The Cookie rule's cost (line 95) is the same per-head scan,
in a lookahead. P00's group body ends with `\.`, which its class does not take, so shape (1) does not fire (its cost is
the per-start scan, not exponential backtracking); P04 opens after `\b`, not `|`; `_ASSIGN_LINE`'s cost is two adjacent
quantifiers over one class, a shape the screen has no tell for. The screen is not in this lane's boundary.

## 4. What changed (09:3xZ)

`scripts/transcript_export.py` (final sha256 014439fb, section 10; b81784c5, which sections 2 and 3 first measured, was the
first lenient design: D1, D16):
- Lines 69-81: `_Q` (a quote escaped to any depth), `_VE` (the pwd and credentials value class, escape-aware), `_CV` (a
  cookie value's class), `_CL` (a Cookie header's class: a tab stays in the line), `_COOKIE` (a head to its colon, with
  `_KEY_L` before the name), `_COOKIE_X` (a later head whose own head holds a quote or a newline). In each value class an
  escaped `\n`, `\r`, `\t` or `\f` ends the value (`_CL`: `\n` and `\r` only), an escaped quote at any depth ends it before
  its backslashes, and an escaped backslash is one value character. The note above them says why (F1, F5, F15).
- Lines 84-101: `_key_block_or_same` and `_cookie_or_same`, the two rules' replacements (a match that finds no value or
  no END stays as it is; see F7).
- Lines 112-122 (F7): the lenient key-block rule. A head starts only at the first dash of a run (`(?<!-)`); the END is
  read by its last three dashes before `END` (`---[ \t]*END`), so a dash run in the body is not re-read from each dash;
  the head's closing run stays greedy as in SCRUB2's rule; an optional lookahead (group 1) records an END that shares
  the head's closing run (six or more dashes, then END), which SCRUB2's rule reached only by backtracking; group 2 is the
  first END after the run; else `.*` runs to the end of the text and the replacement returns the match unchanged, which
  ends the rule's scan (no later head can reach an END). Same output as SCRUB2's rule: section 5's differential.
- Lines 123-128 (F2): a new rule before the credential rule takes the token of `Authorization: Negotiate <token>` (the
  token stops before a Bearer match and a bridge link, AF-AP-157's class); the credential rule then takes the word
  `Negotiate` as before, so the output is `Authorization: <redacted> <redacted>` and no redaction of SCRUB2's is lost.
- Lines 138-144 (F1, F5, F15, and its own AF-AP-152 cost): the Cookie rule reads `_COOKIE`, `_Q`, `_CL`, `_CV`; a head with
  no `name=value` of 8+ up to its line's end matches to there and stays as it is, stopping before a `_COOKIE_X` head.
- Lines 145-149 (F1): the Authorization-scheme rule takes `_Q` beside the name (F1 lists `Authorization: Token` in a JSON
  document inside a tool input). Its scheme list is unchanged (`negotiate` stays in it; that alternative is now dead
  code, as it was at the PIN: mutant W6, equivalent).
- Lines 150-157 (F1, F5, F15): the pwd and credentials rules take `_KEY_L` before the name, `_Q` beside it, `_VE` for the
  value (the credentials rule's quoted-key form `\\*["']\s*:`).

`scripts/session_export.py:136-139`: `PATTERN_NAMES` gains `authorization-negotiate` at index 2 (24 names for 24 rules);
the order and names otherwise unchanged (brief boundary: "only the PATTERN_NAMES order and names").

## 5. Tests, the red run, and the mutation passes (09:3xZ)

`tests/test_transcript_export.py` (`import random` at 12; the new block 1291-1577), 16 new tests (one parametrized over 6):

| Test (line) | Holds | Killed by (FAILED) |
|---|---|---|
| `test_r1_named_rules_hold_every_f1_context_end_to_end` (1355) | 4 shapes x 7 contexts (line start, tab, literal `\n`, after é, after の, a JSON document, plain) through `main()` (the digest) and `convert()` | R1a, R1b, R1c, R1d, R1i |
| `test_r1_contexts_red_on_scrub2s_forms_exactly_where_verify_scrub2_found_them` (1399) | the same grid through `scrub_payload` on the canonical JSON: none leaks; with SCRUB2's four rule forms swapped in, exactly VERIFY-SCRUB2 5a's cells leak | R1a-R1d, R1i, W7 |
| `test_r1_a_value_stops_before_an_escaped_quote` x6 (1417) | F5: the value stops before `\"`'s backslash; the JSON parses back to the text with the value replaced | R1d, R1e, R1j, R1k |
| `test_r1_an_escaped_newline_or_tab_ends_a_value` (1431) | F15: 6 ordinary texts unchanged by scrub_payload and through `convert()` (SCRUB2's forms change all 6: in-test control); a value before `\n` still taken; a tab stays in a Cookie line | R1f, R1g, W7 |
| `test_every_authorization_scheme_hides_its_token` (1449) | F2 and W7: 11 schemes' tokens hidden in scrub and scrub_payload; Negotiate's output; the Bearer stop; escaped JSON; digest and convert | F2a, F2b, W7 |
| `test_the_key_block_and_cookie_rules_run_in_linear_time` (1485) | F7: 6 hostile texts (60,000 dashes; the same then BEGIN; 4,000 BEGIN heads with no END; a BEGIN head then 60,000 dashes; 12,000 cookie heads; 11,000 Set-Cookie heads) x scrub and scrub_payload, each call under 2 s, in a child with a 40 s timeout | F7a, F7b, F7c, F7e |
| `test_the_lenient_key_block_rule_hides_what_scrub2s_rule_hid` (1507) | seeded differential against SCRUB2's rule (5,000 texts, 3,465 of them hold a block SCRUB2's rule takes); an empty block, a block amid 5,000-dash rules, 50 heads with no END, two blocks with text between, a tab, a BLOCK suffix, each through the rule and `scrub` | F7d, W13, W14, W15 |
| `test_the_cookie_rule_hides_what_scrub2s_rule_hid_on_plain_text` (1539) | seeded differential against SCRUB2's Cookie rule (6,000 texts, 2,258 matches); a later head holding a quote or a newline keeps its value hidden | F7f, W1, W2 |
| `test_each_named_rule_takes_8_characters_and_leaves_7` (1552) | W1-W5: each named rule's floor, both ways | W1, W2, W3, W4, W5 |
| `test_a_pwd_value_that_starts_with_a_backslash_stays` (1561) | W8 | W8 |
| `test_an_upper_case_escape_separates_and_an_escaped_backslash_is_one_character` (1567) | W10: a key and a pwd name after `\u00C9`; an escaped backslash pair is one value character | R1a, R1h, W10 |

`tests/test_session_export.py` (1265-1308), the F10 test `test_each_gate_pattern_name_labels_its_own_rule` (1298): each of
the 24 names has a probe its own rule changes (gate_file's count: a match whose replacement differs); no two rules change
each other's probe, so any swap of two names reds it; in-test controls: N1's and N3's swaps leave both probes unchanged.
Killed by N1, N2, N3, N5, N8 (and N4, N6, N7 by the count).

The generators' alphabets (tactic 3f): the key-block differential draws whole malformed heads and END lines (3, 4 and
spaced dashes, PGP BLOCK), loose runs of 1, 2, 3 and 5 dashes, the words alone, spaces, tabs, newlines and filler; it
cannot draw a 5-dash head (the strict rule's), lower case, or a head split over lines. The Cookie differential draws
heads in two cases and Set-Cookie, colons, quotes, spaces, tabs, `\n` and `\r\n`, separators, names and 2- and 8-character
values; it draws no backslash, no `_` and no non-ASCII letter (where the rule changes on purpose; other tests hold those).
A wider scratch run (`<scratch>/scrub2r1/diff_rules.py`, dash runs of 1 to 8, header words, 50,000 texts each): key-block
3,632 texts changed by SCRUB2's rule, 0 differences; Cookie 3,752 and 0. Its control: the three-dash-closing form this lane
first wrote (section 9, D1) differs on 283 of the same 50,000 texts.

**Red run** (the new test files on the PIN's scripts, `<scratch>/scrub2r1/red` = `vscrub2/t` + the two new test files,
`masked.sh absent`): `12 failed, 272 passed in 58.39s`. Each red for its own reason: the two F1 grids list the leaked
cells; four F5 cases raise `JSONDecodeError` (the value took the backslash of `\"`), the fifth leaks its value (a pwd in
a JSON document); the F15 list holds all six texts; `('Negotiate', 'scrub')` leaks; the timing test stops at its
timeout after one call (`60,000 dashes|scrub|31.7152`); the escape test fails on its pwd line (`zq\u00C9pwd=...`); the
F10 test fails on the missing `authorization-negotiate`. Green on the PIN by design (regression pins, killed by named
mutants): the two differentials, the floor test, the backslash-start test, the Token-in-quotes case.

**Mutation** (`<scratch>/scrub2r1/mutate_r1.py`, inside `masked.sh absent`, on `<scratch>/scrub2r1/mt` = `git archive HEAD`
of scripts, tests, pyproject.toml plus this lane's four files, checked equal to the tree's; the unmutated control first;
each anchor exactly once; each mutated file compiled first; KILLED only on a FAILED test; `PYTHONDONTWRITEBYTECODE=1`):
```
group r1 (this lane's named mutants, 19)   CONTROL rc=0 223 passed      TOTAL KILLED 19, SURVIVED 0, INVALID 0
group w  (VERIFY-SCRUB2's 28, re-anchored) CONTROL rc=0 223 passed      TOTAL KILLED 25, SURVIVED 3, INVALID 0
group se (PATTERN_NAMES, N1-N8)            CONTROL rc=0 73 passed       TOTAL KILLED 8,  SURVIVED 0, INVALID 0
```
The eleven survivors of F12 (W1-W5, W7, W8, W10, W13-W15): all KILLED. The three survivors are equivalent: W6 (the new
Negotiate rule takes the token before the scheme rule can), W28 (the verifier's; the class already takes every dash),
and W11 (the verifier's edit put a bare quote into a raw string and did not compile, INVALID there; repaired to
`(?<=\\[nrtbf\"])` it compiles, and it cannot change a decision: `(?<![A-Za-z0-9])` already holds after any quote).
Re-anchoring (each on the new text, same semantics): W1/W2 on `_CV + r"{8}`, W3 on the scheme rule's floor, W4/W5 on
`_VE + r"{8}`, W8/W9 on the pwd start guard, W13-W15 on the new lenient rule's head and body, W16 on the Cookie match's
class; W17-W28 unchanged. N1-N7 re-anchored on the re-wrapped tuple; N8 new.

The kill table, one line per mutant (the driver's own lines from its runs at 09:2xZ, the first FAILED test named and
cut; KILLED only on a FAILED test, the count is the run's):
```
R1a  KILLED   3 failed  pwd: SCRUB2's left anchor                                  | test_r1_named_rules_hold_every_f1_context_end_to_end
R1b  KILLED   2 failed  credentials: SCRUB2's left anchor                          | test_r1_named_rules_hold_every_f1_context_end_to_end
R1c  KILLED   2 failed  Cookie: \b as the left anchor                              | test_r1_named_rules_hold_every_f1_context_end_to_end
R1d  KILLED   3 failed  _Q takes a bare quote only                                 | test_r1_named_rules_hold_every_f1_context_end_to_end
R1e  KILLED   3 failed  _VE: the backslash of an escaped quote is a value characte | test_r1_a_value_stops_before_an_escaped_quote[echo "pwd=%s"-
R1f  KILLED   1 failed  _VE: an escaped newline is a value character               | test_r1_an_escaped_newline_or_tab_ends_a_value
R1g  KILLED   1 failed  _CL: a tab ends a Cookie line                              | test_r1_an_escaped_newline_or_tab_ends_a_value
R1h  KILLED   1 failed  _VE: an escaped backslash is not one value character       | test_an_upper_case_escape_separates_and_an_escaped_backslash
R1i  KILLED   2 failed  credentials: SCRUB2's quoted-key head                      | test_r1_named_rules_hold_every_f1_context_end_to_end
F2a  KILLED   1 failed  the Negotiate rule never fires                             | test_every_authorization_scheme_hides_its_token
F2b  KILLED   1 failed  the Negotiate token takes a following Bearer               | test_every_authorization_scheme_hides_its_token
F7a  KILLED   1 failed  no start guard on the lenient head                         | test_the_key_block_and_cookie_rules_run_in_linear_time
F7b  KILLED   1 failed  the END read with -{3,}                                    | test_the_key_block_and_cookie_rules_run_in_linear_time
F7c  KILLED   1 failed  a head with no END scans again (the .* branch dropped)     | test_the_key_block_and_cookie_rules_run_in_linear_time
F7d  KILLED   1 failed  the shared END never read (102+ dashes)                    | test_the_lenient_key_block_rule_hides_what_scrub2s_rule_hid
F7e  KILLED   1 failed  the Cookie no-value branch dropped                         | test_the_key_block_and_cookie_rules_run_in_linear_time
F7f  KILLED   1 failed  _COOKIE_X never matches (a later head that crosses the lin | test_the_cookie_rule_hides_what_scrub2s_rule_hid_on_plain_te
R1j  KILLED   2 failed  _CL: the backslash of an escaped quote stays in a Cookie l | test_r1_a_value_stops_before_an_escaped_quote[echo "Cookie:
R1k  KILLED   2 failed  the scheme rule's token takes a backslash                  | test_a_credential_behind_an_escaped_quote_is_redacted[obj8-Z
W1   KILLED   2 failed  cookie floor 8 -> 12                                       | test_the_cookie_rule_hides_what_scrub2s_rule_hid_on_plain_te
W2   KILLED   2 failed  cookie floor 8 -> 5                                        | test_the_cookie_rule_hides_what_scrub2s_rule_hid_on_plain_te
W3   KILLED   1 failed  authorization floor 8 -> 12                                | test_each_named_rule_takes_8_characters_and_leaves_7
W4   KILLED   1 failed  pwd floor 8 -> 12                                          | test_each_named_rule_takes_8_characters_and_leaves_7
W5   KILLED   1 failed  credentials floor 8 -> 12                                  | test_each_named_rule_takes_8_characters_and_leaves_7
W6   SURVIVED 223 passed negotiate dropped from the scheme rule (equivalent: the ru | -
W7   KILLED   3 failed  ntlm, key, ssws, digest dropped                            | test_r1_contexts_red_on_scrub2s_forms_exactly_where_verify_s
W8   KILLED   1 failed  pwd: a backslash start is a value                          | test_a_pwd_value_that_starts_with_a_backslash_stays
W9   KILLED   2 failed  pwd: a $ start is a value                                  | test_the_shape_gaps_leave_ordinary_text
W10  KILLED   1 failed  escape hex upper case not an escape                        | test_an_upper_case_escape_separates_and_an_escaped_backslash
W11  SURVIVED 223 passed escape anchor also after an escaped quote (the verifier's  | -
W12  KILLED   3 failed  opaque floor 40 -> 41                                      | test_the_opaque_callable_gets_only_what_no_named_rule_takes
W13  KILLED   1 failed  PEM lenient: tabs no longer spaces                         | test_the_lenient_key_block_rule_hides_what_scrub2s_rule_hid
W14  KILLED   1 failed  PEM lenient: BLOCK suffix dropped                          | test_the_lenient_key_block_rule_hides_what_scrub2s_rule_hid
W15  KILLED   1 failed  PEM lenient: greedy body (.* not .*?)                      | test_the_lenient_key_block_rule_hides_what_scrub2s_rule_hid
W16  KILLED   7 failed  cookie: stops at the first space                           | test_the_shape_gaps_are_scrubbed
W17  KILLED   1 failed  value gate: kind check inside the read loop                | test_a_source_of_an_unknown_kind_is_refused_before_any_sourc
W18  KILLED   2 failed  value gate: a directory reads as NotRegularFile            | test_the_value_gate_fails_closed_on_a_source_it_cannot_read
W19  KILLED   2 failed  value check: prefix match for the name                     | test_a_malformed_env_line_is_named_by_its_line_number
W20  KILLED   2 failed  value check: lines counted from 0                          | test_a_malformed_env_line_is_named_by_its_line_number
W21  KILLED   1 failed  value check: numbered by splitlines                        | test_a_malformed_env_line_is_printed_as_its_line_number
W22  KILLED   2 failed  value check: no O_NONBLOCK (a FIFO blocks)                 | test_a_source_that_is_not_a_regular_file_refuses_at_once
W23  KILLED   1 failed  value gate: raw key read with a plain open                 | test_a_source_that_is_not_a_regular_file_refuses_at_once
W24  KILLED   2 failed  production tuple: TYPESAFE skip dropped                    | test_a_hostname_does_not_block_when_its_key_holds_no_secret
W25  KILLED   1 failed  the autouse tripwire removed                               | test_a_test_that_names_no_sources_meets_the_tripwire
W26  KILLED   1 failed  env floor 8 -> 9 (MIN_VALUE)                               | test_the_8_character_floor_counts_8_and_skips_7
W27  KILLED   2 failed  xox right anchor lets _ in the key                         | test_every_provider_rule_takes_its_key_on_the_right_and_afte
W28  SURVIVED 223 passed sk right anchor refuses a following dash (equivalent)      | -
N1   KILLED   1 failed  PATTERN_NAMES: pwd <-> credentials                         | test_each_gate_pattern_name_labels_its_own_rule
N2   KILLED   2 failed  PATTERN_NAMES: cookie <-> authorization-scheme             | test_gate_counts_patterns_and_canaries_and_prints_none
N3   KILLED   1 failed  PATTERN_NAMES: private-key <-> private-key-malformed       | test_each_gate_pattern_name_labels_its_own_rule
N4   KILLED   7 failed  PATTERN_NAMES: one name dropped (count 23)                 | test_no_canary_survives_the_export
N5   KILLED   2 failed  PATTERN_NAMES: sk-key <-> github-token                     | test_gate_counts_patterns_and_canaries_and_prints_none
N6   KILLED   7 failed  PATTERN_NAMES: opaque-run <-> bridge-link                  | test_no_canary_survives_the_export
N7   KILLED   7 failed  PATTERN_NAMES: an extra name (count 25)                    | test_no_canary_survives_the_export
N8   KILLED   2 failed  PATTERN_NAMES: authorization-negotiate <-> credential      | test_gate_counts_patterns_and_canaries_and_prints_none
```

## 6. Measurement, item 6 (the rows of each changed rule) (10:1xZ)

**Instrument** (`<scratch>/scrub2r1/measure3.py`, the SCRUB2 lane's `measure2.py` method): each candidate is this round's
PIN rule list (cdbc1b8's exporter, 6ad316dc, 14 rules) with ONE of this lane's changes (the same rule objects the new file
builds; the module asserts every other rule unchanged), plus FINAL (the new file's 15 rules). For every text a candidate's
`scrub` changes differently from the PIN's, both scrubs re-run with character provenance (which original characters each
hides; asserted equal to the real output), so NEW (hidden now, shown by the PIN) and LOST (hidden by the PIN, shown now)
are exact. Masked shapes only. Self-test first, on a fixture with a pwd value after an escaped newline, F15's
`Client(credentials=None)` text, a Negotiate header and a 4-dash key block: exactly the predicted regions (PWD NEW, CRED
LOST of 13 characters holding `\n`, NEG NEW in both views, no key-block change). Triggers per candidate (a text holding
none of its words cannot change): `BEGIN` and `KEY` (case as written) for the key block, else `negotiate`, `cookie`,
`authorization`, `pwd`, `credentials` in any case.

**Corpora** (09:3xZ-09:4xZ): the 19 committed digests at 59229eb (3,657,031 bytes); the main transcript fixed at 756,220,434
bytes (145,935 lines, 4,080,406 strings; one end for both calls, `FIXED_END`); 315 subagent transcripts plus 38
workflow-agent transcripts under `subagents/workflows/*/` (581,347,929 bytes, 140,969 lines, 3,757,803 strings; this
lane's own transcript `agent-a88c7c57f2fa2a96b` excluded, as SCRUB2 excluded its own); the second project root
(3,074,681 bytes, 519 lines, 13,731 strings). Views: `dec` = every string of every record, decoded (the digests' view);
`raw` = the raw JSONL line (the raw-JSON writers' view, an upper bound of what session_export scrubs as JSON).

Cells: texts changed / NEW regions / LOST regions.
```
cand    digest  main/dec  main/raw  sub/dec  sub/raw   root2/dec  root2/raw
PEM-L   0/0/0   0/0/0     0/0/0     0/0/0    0/0/0     0/0/0      0/0/0
NEG     0/0/0   0/0/0     0/0/0     0/0/0    0/0/0     0/0/0      0/0/0
COOKIE  0/0/0   0/0/0     0/0/0     0/0/0    1/0/2     0/0/0      0/0/0
AUTH2   0/0/0   0/0/0     0/0/0     0/0/0    4/5/0     0/0/0      0/0/0
PWD     0/0/0   0/0/0     1/0/2     0/0/0    7/4/14    0/0/0      0/0/0
CRED    0/0/0   0/0/0     5/0/10    5/0/11   10/6/18   0/0/0      0/0/0
FINAL   0/0/0   0/0/0     6/0/12    5/0/11   18/15/34  0/0/0      0/0/0
```

**Every region classified** (`<scratch>/scrub2r1/detail3.py`: FINAL only, the same provenance; each region's masked form
and neighbours, and whether its exact text occurs in a tracked file, in memory, a boolean only; it found 72 regions, the
table's 15 NEW + 57 LOST exactly):
- LOST, F15's class, 31 regions: the value or the header line ran over an escaped newline, carriage return or tab in the
  raw view, or passed the 8-character floor only because escapes counted as two characters each. What shows now is the
  next line or a short ordinary value. CRED 25 (main raw 10, subagents dec 11 and raw 4): `..._credentials=None)` and
  the next line, `..._CREDENTIALS=0` and the next line (`000:` line prefixes, `next_step_here`), `credentials===`
  headings, `get_credentials()` and the next line's `000<tab>` prefix, and VERIFY-SCRUB2's own quotes of these texts in
  its probes and report (the dec view holds them as literal `\n`); PWD 4 (main raw 2, subagents raw 2): a Windows path
  `C:\...` of 7 decoded characters; COOKIE 2 (subagents raw): a Markdown table after a `COOKIE:` cell, which SCRUB2's
  rule read across the rows (the raw view's escaped newlines did not end its line) to a quote 100+ characters on.
- LOST, F5's class, 26 regions (subagents raw; CRED 14, PWD 12): the single backslash of a closing `\"` after a value,
  which item 1 requires the rules to keep (the value itself stays hidden in every one; checked by the masked rows).
- NEW, 15 regions (subagents raw): 5 are the committed fake `"authorization": "bearer ..."` fixture of
  `tests/test_transcript_export.py` (NAMED_R3) read in escaped JSON: the shape the scheme rule's change is for. **The cost,
  10 regions of ordinary code**: 8 are a Python dict literal `(dict(names=(` after a quoted `"N-pwd":` or
  `"N-credentials":` key in the SCRUB2 lane's scratch source (4 each; `_Q` reads the escaped quote beside the name, so a
  quoted key followed by `:` takes the value, the same class as the credential rule's `"api_key": <anything>`); 2 are a
  format template `credentials=%s` after a quoted `"credentials":` key in a probe's source. None in the digests or the
  main transcript. My reason to take the cost: F1's JSON-document context (a JSON document inside a tool input) is the
  contract's demand, and this is its shape.

No LOST region is a value a rule is meant to hide: every one is F15's ordinary text or F5's backslash. The measurement's
alphabet is this session's text (tactic 3f): shapes this session never wrote are covered by the tests and the differential
generators only.

**The digests** (`<scratch>/scrub2r1/digests_r1.py`, the SCRUB2 lane's `digests.py` re-pointed; both exporters with
`sources=()`, no real source read): `transcript bytes read: 756632189 (fixed at start)`, `files new=19 pin=19 same set=True`,
`identical: 19 of 19; differ: []`, `new digests: 19 files, 3681611 bytes, sha256 of the concatenation d07c48f5b8385663`.
Landing changes no committed digest line. The new digests are in `<scratch>/scrub2r1/digests-new/` for the coordinator's
known-value check.

## 7. The Laya lock, item 8 (10:1xZ)

The builder's pre-fit comparison (`<scratch>/scrub2r1/laya_r1.py`, VERIFY-SCRUB2's `laya_v.py` re-pointed: this round's
PIN scrub, the new exporter's, and two positive controls; whole items compared; no bytecode written), `masked.sh absent`:
```
v2 collect_v2 at 434b727dfd: PIN 6220 items | new: differs from the PIN in 0 items | N-pwd control: 16 (the new scrub
   equals the PIN on 16 of them) | E control: 6220 | common.scrub is the tree's exporter (the new one): True
v1 collect at eb256f49c0:    PIN 1788 items | new: 0 | N-pwd control: 0 | E control: 1788
v1 collect at 0b342c7a29:    PIN 1788 items | new: 0 | N-pwd control: 0 | E control: 1788
```
(N-pwd = the PIN with `pwd` among its credential names; E = the PIN's scrub, then every `e` to `E`, which must reach every
item. The first attempt's control probe was wrong: this round's PIN already hides `pwd=abcdefgh1234`, so the control's own
assertion failed before any run; re-probed with a path value, which only N-pwd hides.)

0 changed items, so K265's step: `HF_HUB_OFFLINE=1 /root/venv-laya-probe/bin/python scripts/laya_ft/build_dataset.py
--version 2 --commit 434b727dfd2b6daa5aa3cf4d638e706f5dfa59cb --out <scratch>/scrub2r1/v2new --model-dir
/root/hf-laya-probe/hub/models--convaiinnovations--laya/snapshots/1c5edc17a7acd8701df6fc341c0d179f1c62c982/typed-decisions`
(rc 0, 45 s): `dataset.jsonl` sha256 99070c33830832ca11e64226eddac1934ccd300c73b4d5d8d8c7bf5a36271f9d, 12,800,855 bytes = the
record's `dataset` field; the manifest differs from the record in one line, the exporter's hash (6ad316dc... to
014439fb2694d273a44e75ef125b3a7f99411e1489e19819889a36e49e4e430d, the final file's sha256). Copied over
`docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json` (`git diff`: 1 insertion, 1 deletion).
The record's venue tests (they rebuild at the recorded commit and assert the manifest equal to the record byte for byte,
`tests/test_laya_ft.py:1491` compares `RECORD / "dataset-manifest.json"`, so the old record fails them against the new
exporter):
```
$ masked.sh absent ... bash scripts/test_summary.sh tests/test_laya_ft.py -k "version_2_record or version_1_is_byte"
pytest-summary: 2 passed, 42 deselected in 117.62s (0:01:57)
```
The OpenJev manifest is not regenerated (DISCREPANCIES D8).

## 8. Gates, pasted (10:1xZ)

```
$ masked.sh absent <scratch>/scrub2r1/empty -- bash scripts/test_summary.sh <the 12 floor files> --basetemp=...   (twice)
pytest-exit: 0
pytest-summary: 841 passed in 132.84s (0:02:12)
pytest-exit: 0
pytest-summary: 841 passed in 131.17s (0:02:11)
12 files set=27f27a25516b          (printf '%s\n' <files> | sort | sha256sum | cut -c1-12, pc_suite.sh's set_id)
```
841 = the floor's 824 plus this lane's 17 new test items (16 in `tests/test_transcript_export.py`, the escaped-quote test
counting 6, and the F10 test). No red.
Set A's six other consumer files (they reach the scrubber through chat_find, hiccup_scan, the harness ports), once:
`pytest-summary: 96 passed, 1 skipped in 24.55s`, 6 files set=d11be22044d4 (the skip: `tests/test_qwen_jev.py:37: LOUD
SKIP`, the PC's venv only).
`python3 -m pyflakes` on the four changed code files: rc 0. `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`: 0 in each of the six
files written (four code files, the manifest, this report). `scripts/ap_screen.py --limit 100000` over the four code files:
34 hits, 0 inside this lane's added lines (every hit on a line older than this lane). GitNexus `detect-changes --scope all`:
`Changes: 7 files, 76 symbols`, `Affected processes: 0`, `Risk level: low` (5 of the files this lane's; 2 the I59-B lane's).
GitNexus `impact` before the edits: `scrub_payload` CRITICAL (18 symbols, all in `session_export.py`'s record processing:
the change is to the scrubber the session export runs, as the contract asks), `scrub` MEDIUM (28), `SECRET_PATTERNS` and
`PATTERN_NAMES` UNKNOWN (module constants; a text search names their readers: `session_export.py` and the test file).

**Item 4, test isolation, re-checked on this lane's two changed test files (10:4xZ).** `<scratch>/scrub2r1/trace_r1.sh`
is VERIFY-SCRUB2's `trace2.sh` re-pointed at this lane's scratch: pytest under `strace -f -qq -e trace=%file` (every
process), filtered to the lines that name a source path, with the verifier's `sitecustomize` logger of GH_TOKEN and
GITHUB_TOKEN lookups. The copy `<scratch>/scrub2r1/tc` is `git archive HEAD` of scripts, tests and pyproject.toml plus
this lane's four files (hashes checked equal to the tree's).
```
(a) masked.sh absent: 284 passed in 27.60s
    <copy>/.pc-bridge.env 0 | tree .pc-bridge.env 0 | /root/.codiv/api.env 0 | pseudonym.key 0 | /root/.config/qwen 0 | token lookups 0
(b) masked.sh fakes (all five sources planted as fakes): 284 passed in 27.69s
    <copy>/.pc-bridge.env 1 syscall, 0 opens (a newfstatat, plus 2 ENOTDIR probes of paths under it: pytest's rootdir walk)
    every other source 0 | token lookups 0
(c) CONTROL, masked.sh fakes: a scratch-only test (never in the tree) opens the three planted fakes (the copy's
    .pc-bridge.env in its own process, the other two in a child) and looks up GH_TOKEN once: 1 passed in 0.14s
    <copy>/.pc-bridge.env 2 syscalls, 1 open | api.env 1 open | pseudonym.key 1 open | token lookups 1 (the control's line 27)
```
No test in the two changed files opens a source, and the instrument sees opens in the test process and in a child. The new
tests reach `main()` through the file's `_run` helper (fixture value-gate sources) and `convert()` with a fake key
(`token_bytes(32)`).

**Item 5, the value gate:** `scripts/known_values_check.py` and `tests/test_known_values_check.py` are unchanged (sha256
cfdf2ffec10e6d10 and f5ad1fc62a39c969; `git diff` names neither), and the test file is in the floor (841 passed, twice).

**Every test that names a changed file** (the build-loop gate rule): the 12 floor files; `harness-ports/tests/test_lane_done_gate.py`
and `harness-ports/tests/run-all.sh` match only the name `test_hermes_session_export.py` (in the extra set above);
`tests/test_laya_ft.py` names the recorded manifest and reaches the scrubber through
`scripts/laya_ft/common.py:39` (its `load_module` of the exporter). It ran
whole, once:
```
$ masked.sh absent <scratch>/scrub2r1/empty -- bash scripts/test_summary.sh tests/test_laya_ft.py -rs --basetemp=...
pytest-exit: 0
pytest-summary: 44 passed in 576.05s (0:09:36)
1 file set=8b147318aa48
```

## 9. DISCREPANCIES (10:4xZ)

- **D1. A reversed conclusion: the lenient rule's first design lost redactions (flag for the coordinator).** State 1
  (08:5xZ, exporter b81784c5): a three-dash head closing, a lazy body, then `(END)|\Z`. It rested on reasoning (a longer
  closing run only moves dashes into the body), not on a measurement. The seeded differential falsified it: 1,042 of 5,000
  texts came out different from SCRUB2's rule. The shrunk case is a head whose six closing dashes are shared with an END
  line, then a second END: SCRUB2's greedy closing run hides the whole text, the first design showed the tail
  `END PRIVATE KEY---` (re-checked at 10:4xZ: PIN `<M>`, first design `<M>END PRIVATE KEY---`, final `<M>`). State 2 (09:1xZ,
  the final 014439fb): the greedy closing run as in SCRUB2's rule, an optional lookahead (group 1) for an END that shares
  the closing run, group 2 for the first END after it, else `.*` to the end of the text, returned unchanged. It shows 0
  differences in the committed test's 5,000 texts and in 50,000 scratch texts (3,632 blocks), where the first design differs
  on 283 (the control). State 2 is the answer because it is the measured one; both states are named in sections 2, 3 and 5.
- **D2. F2 is a new rule, not a change to the credential rule.** The credential rule reads `Authorization` as a name and takes
  the scheme word `Negotiate` as the value, so the token was left. A new rule before it (`authorization-negotiate`) hides the
  token first; the credential rule then hides the word as before. Output: `Authorization: <redacted> <redacted>` (the PIN:
  `Authorization: <redacted> <token>`; checked at 10:4xZ). Every PIN redaction stays; SCRUB2's report D4 is now true.
  `PATTERN_NAMES` gains a name at index 2 (the brief allows order and names). The scheme rule's `negotiate` alternative stays
  dead code, as it was at the PIN (mutant W6, equivalent).
- **D3. The scheme rule's head changed too** (`_Q` beside `Authorization`). Item 1 names three rules; F1's context list also
  holds `Authorization: Token` in a JSON document inside a tool input, which leaked through `convert()` at the PIN (section 2).
  Its cost is in section 6 (AUTH2: 4 texts, 5 NEW regions, all the committed fake fixture; 0 LOST).
- **D4. A tab stays inside a Cookie header line.** `_CL` (the header's characters) ends only at an escaped `\n` or `\r`;
  `_CV` (a cookie's value) ends at an escaped `\t` and `\f` too. A header may separate its pairs with a tab, and ending the
  line there would show the next pair's value. Pinned by mutant R1g.
- **D5. Which escapes end a value.** An escaped `\n`, `\r`, `\t` or `\f` ends a pwd or credentials value; `\b` and a `\uXXXX`
  escape of whitespace do not (checked at 10:4xZ: `pwd=abcd` + `\u` + `0020efgh` stays hidden). `json.dumps` writes a space as
  a space and a tab as `\t`, so a `\uXXXX` space appears only when a writer escapes it on purpose; the cost of reading it as a
  value character is over-redaction only.
- **D6. The Cookie rule was made linear too.** F7 names line 81; item 2's check found SCRUB2's Cookie rule in the same class
  (section 3: 2.5, 10.2, 41.2 s at 64k, 128k, 256k characters). Its output equals SCRUB2's rule's on plain text (the 6,000-text
  differential) and changes on purpose only where item 1 asks (escapes, `_KEY_L`).
- **D7. Three older super-linear rules are NOT fixed**: P00 (the bridge-host payload rule, 5.66 s at 32,000 characters of
  `a.` labels), P04 (the URL-password payload rule, about 2.5 s at 64,000) and the strict pass's `_ASSIGN_LINE` (5.50 s at
  16,000 spaces), each x4 per doubling (section 3). They predate SCRUB2 and are outside the contract's named rules.
  Recommended: a follow-up task in AF-AP-152's class.
- **D8. The OpenJev manifest is not regenerated.** Its exporter hash (f63cd97e) is neither the PIN's (6ad316dc) nor this
  file's; it is a historical record of the 09-24 build (SCRUB2's D2 gives the reasons: four code hashes differ from today's
  files). Its data lock holds: `collect` at its commit (eb256f49c0) and at the v1 test's (0b342c7a29) differs from the PIN in 0
  of 1,788 items (section 7), and the v1 test (`test_version_1_is_byte_identical_and_still_loads`) passed.
- **D9. The PIN.** The brief pins origin 7a050b6; origin was 59229eb at dispatch (the dispatch names it). 7a050b6..59229eb
  changes no scrubber, test or manifest file (section 1, P1).
- **D10. The measurement corpus is wider than SCRUB2's:** 38 workflow-agent transcripts under `subagents/workflows/*/` are
  in it (a one-level glob missed them at first), and the main transcript has grown (fixed at 756,220,434 bytes).
- **D11. W11 repaired.** VERIFY-SCRUB2's W11 edit put a bare quote into a raw string and did not compile (INVALID in its run).
  Repaired to `(?<=\\[nrtbf\"])`, it compiles and survives as an equivalent mutant (section 5).
- **D12. `after.py` changes the verifier's scripts in two strings each** (the target root and the work directory; one each
  for `negotiate.py` and `timing_run.py`), each asserted to occur once and printed; nothing else changes.
- **D13. F7's "bound" is not a length cap.** A head with no END matches to the end of the text and is returned unchanged, so
  the rule's scan ends there; no later head could reach an END. A cap on the body would change what the rule hides (a longer
  real block would show); this form hides exactly what SCRUB2's rule hid (D1's differential).
- **D14. The ordinary-text cost of `_Q` beside the names:** 10 regions of ordinary code newly hidden in the subagents' raw
  view (8 `(dict(names=(` after a quoted `"N-pwd":` or `"N-credentials":` key, 2 `credentials=%s`), none in the digests
  or the main transcript (section 6). Taken for F1's JSON-document context.
- **D15. `convert()` in the new tests takes a fake key** (`token_bytes(32)`), and `main()` runs with fixture sources: the
  real key and the five sources are never opened (section 8's trace).
- **D16. Sections 2 and 3 first measured the wrong file.** Their AFTER runs (08:5xZ) used the first lenient design
  (b81784c5), before D1's redesign; the first draft of section 4 called b81784c5 the final file "before the blank-line fix",
  which was false (it differs in the lenient rule, its replacement function and one blank line). Found while writing this
  section; re-run at 10:2xZ on the final file (014439fb): F1, F15 and F2 printed the same lines, F7 and the census moved
  within noise, no rule flagged. Sections 2, 3 and 4 now carry the final file's lines, with the first run's numbers beside them.

## 10. Files, final hashes, evidence tiers (10:4xZ)

`git diff --stat` over the five tracked files: `5 files changed, 401 insertions(+), 18 deletions(-)`.

| File | Changed lines (the diff's hunks, new numbering) | sha256 (16) |
|---|---|---|
| `scripts/transcript_export.py` | 69-102, 114-128, 139-144, 146-149, 152-154, 156-157 | 014439fb2694d273 (434 lines; the PIN 6ad316dc, 383) |
| `scripts/session_export.py` | 136-139 | 0462fe2e9bdd14bc |
| `tests/test_transcript_export.py` | 12, 1291-1577 | 00e7e9f80aedf16f |
| `tests/test_session_export.py` | 1265-1308 | c1bb29a1ec924a71 |
| `docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json` | 10 (the exporter's hash) | 449811004a7abed8 |
| `tasks/briefs/system1/SCRUB2-R1-report.md` | created | - |

Where the changes sit (the code named on each line is on the cited line):
- scripts/transcript_export.py:79 `_COOKIE`, a Cookie head (the value classes `_Q`, `_VE`, `_CV`, `_CL` are lines 75-78).
- scripts/transcript_export.py:81 `_COOKIE_X`, a later head whose own head crosses a quote or the line's end.
- scripts/transcript_export.py:84 `def _key_block_or_same`, the lenient rule's replacement.
- scripts/transcript_export.py:97 `def _cookie_or_same`, the Cookie rule's replacement.
- scripts/transcript_export.py:119 `(?<!-)-{3,}`, the lenient key-block rule (F7), to line 122.
- scripts/transcript_export.py:127 `(?i:negotiate)`, the new Negotiate rule (F2).
- scripts/transcript_export.py:143 `_COOKIE`, the Cookie rule (F1, F5, F15, linear).
- scripts/transcript_export.py:148 `(?i:token|basic|bearer`, the scheme rule with `_Q` beside the name.
- scripts/transcript_export.py:154 `(?i:pwd)`, the pwd rule.
- scripts/transcript_export.py:156 `(?i:credentials)`, the credentials rule.
- scripts/session_export.py:136 `PATTERN_NAMES`, with `authorization-negotiate` third.
- tests/test_transcript_export.py:1485 `def test_the_key_block_and_cookie_rules_run_in_linear_time`.
- tests/test_transcript_export.py:1507 `def test_the_lenient_key_block_rule_hides_what_scrub2s_rule_hid`.
- tests/test_session_export.py:1298 `def test_each_gate_pattern_name_labels_its_own_rule`.

Untouched in the boundary: `scripts/known_values_check.py`, `tests/test_known_values_check.py`, the OpenJev manifest.
Scratch kept for the coordinator: `<scratch>/scrub2r1/digests-new/` (19 digests for the known-value check),
`v2new/manifest.json`, the instruments (`after.py`, `rule_timing.py`, `diff_rules.py`, `mutate_r1.py`, `measure3.py`,
`detail3.py`, `digests_r1.py`, `laya_r1.py`, `trace_r1.sh`, `trace_control.py`) and their JSON results.

**Verified** (run here, output pasted): the premise; the reproductions before and after on the final file; the rule census;
the red run; the three mutation passes; the measurement (with its self-test) and the region classes' counts; 19 of 19 digests
identical; the Laya lock with both controls, the manifest regeneration and the record tests; the floor twice, the extra set,
`tests/test_laya_ft.py`; pyflakes, the separator check, the AP screen, detect-changes; the test-isolation trace and its control.
**Inferred:** each region's class in section 6 (read from masked forms and neighbours, never the text); that the three
surviving mutants are equivalent (argued from the patterns, not by exhaustive input); that Hermes' session export and
`qwen_matrix` behave on real JSON as their unit tests show (the PC runs were not made).
**Assumed:** the real value-gate sources are regular files (never read; item 5's refusals are tested on fixtures, unchanged).

`python3 scripts/report_lint.py tasks/briefs/system1/SCRUB2-R1-report.md --min-refs 10` on this report:
`report_lint: 18 refs — OK 18, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.
Scratch deleted after the runs (each is rebuilt from its recipe in sections 2, 5 and 8): the copies `mt/`, `red/`,
`after/` and `tc/`, the basetemps, the PIN's digests (identical to the new ones) and the rebuilt `v2new/dataset.jsonl`
(its sha256 is in section 7). Kept: `digests-new/`, `v2new/manifest.json` and `summary.json`, the instruments, their JSON
results, the trace logs `tr/` and `killtable.txt`.

## 11. NOT done (10:4xZ)

- The three older super-linear rules, P00, P04 and `_ASSIGN_LINE` (D7): measured and reported, not fixed.
- The OpenJev manifest (D8).
- The known-value check of `<scratch>/scrub2r1/digests-new/`: the coordinator's, at landing (contract item 6).
- No git write, no push, no bridge use: nothing is committed. The landing is the coordinator's.
- AF-AP-152: no registry row and no screen change for line 81's shape (`scripts/ap_screen.py` and the edit-snapshot hook are
  outside the boundary; section 3 says why the screen missed it).
- Hermes' session export and `qwen_matrix` over real transcripts (the PC): not run.
- The full suite: not run (the floor, the extra consumer set and `tests/test_laya_ft.py` were).
- Out of this round (item 4): F3's shapes, F8, F16, F17, and the AWS and JWT shapes of task #319.

## 12. Self-attack: the three likeliest ways this change is wrong (10:4xZ)

1. **"No PIN redaction is lost" rests on this session's text and two generators.** The measured LOST regions are F15's
   ordinary text and F5's backslash only (section 6). One class they cannot rule out: a value with fewer than 8 characters
   before an escaped (or, in decoded text, a literal) `\n`, `\r`, `\t` or `\f` now shows whole. `pwd=ab` + `\n` + `cdefgh`,
   with a literal backslash-n, was hidden by the PIN and is not hidden now (checked at 10:4xZ). Item 1 requires this
   behaviour, and the corpus holds no such value, but a real secret that contains the two characters `\n` would show.
2. **`_Q` beside the names reads a quoted key's value in JSON inside JSON**, so escaped code loses text: 10 regions of
   ordinary code in this session (D14), none in the digests or the main transcript. A larger body of code would show more;
   the cost is over-redaction only, never a leak.
3. **Linear time is measured, not proved.** It holds on the 55 census families and the committed test's six texts. The
   argument: each head either reaches an END (the match takes the text up to it) or runs to the end of the text (the scan
   stops), and the lookahead reads one dash run once. A family that breaks it was not found, and three older rules stay
   super-linear (D7): a line with a long run of `a.` labels or spaces can still stall `scrub_payload` or the strict pass.
