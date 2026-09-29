> Coordinator note (2026-09-29 01:2xZ): the report of record, extracted by `scripts/stack.py harvest` (the lane's report-file write is refused). Served model: claude-opus-5-5 on all 713 assistant records, 0 refusal stops; `report_lint` 0 refs. The worker restart of about 01:13Z stopped the lane between tool calls; it was resumed by message and re-checked its hashes and scratch.

# VERIFY-SCRUB2-R1-R3 report (task #321): the scrubber repair's round 3, attacked

Verifier: adversarial-verifier (the round-2 verifier, resumed), Opus 5.5. Report stamp: 2026-09-29 01:18:40Z (`date -u`). I checked the final bytes at 01:11:30Z and again at 01:15:21Z, after the worker restart. The lane's five files still match the premise hashes, and my scratch is intact (63 MB).

The harness forbids report `.md` files, so I did not write `tasks/briefs/system1/VERIFY-SCRUB2-R1-R3-report.md`. This message is the whole report.

---

## GATE RECOMMENDATION: **NOT-READY**

**One finding meets the whole blocking predicate: R3V-1 (N2R).**

A head the PIN never read can free a later value that `scrub_payload`'s PAYLOAD rules hid on the PIN:
- the R1 escaped-quote credential (`NAME=\"v\"`);
- the PASS rule (`DB_PASS="v"`);
- curl's `-u "user:pass"`.

The value then shows in `session_export.convert()`'s events. This is the round-3 contract's item 2 (N2), word for word, and round 2's item 4 (V4). The coordinator already ruled this class CORE-BLOCKING in round 3's brief. Round 3 fixed the heads its own stops name (pwd, credentials, Cookie, `_APART` names). It did not fix the heads of the rules that run after them.

**Reproduction.** Every value is a fake built at run time. Everything runs through the masking runner, in scratch only.
```
S=/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad; W3=$S/vscrub2r3
# end to end: export(sources=()) and session_export.convert() (a fake key), for round 3, round 2 and the PIN
PYTHONDONTWRITEBYTECODE=1 $S/vscrub1/masked.sh absent $W3/vt -- python3 $W3/probes/e2e_n2r.py
# the red file (11 items): round 3 fails 11 of 11, the PIN passes 11 of 11
mkdir -p $W3/bt/red-new $W3/bt/red-pin
cd $W3/red_new     && PYTHONDONTWRITEBYTECODE=1 $S/vscrub1/masked.sh absent $W3/vt -- bash /home/user/agent-factory/scripts/test_summary.sh tests/test_vscrub2r1r3_red.py --basetemp=$W3/bt/red-new/b
cd $W3/red_pintree && PYTHONDONTWRITEBYTECODE=1 $S/vscrub1/masked.sh absent $W3/vt -- bash /home/user/agent-factory/scripts/test_summary.sh tests/test_vscrub2r1r3_red.py --basetemp=$W3/bt/red-pin/b
# the seeded differential (4,000 texts x 6 views)
cd $W3/probes && PYTHONDONTWRITEBYTECODE=1 $S/vscrub1/masked.sh absent $W3/vt -- python3 rand_n2c.py 4000 new 20260929
```

**Everything else I attacked holds:**
- N1 is closed.
- V4 holds per position on generated text and on the corpus, in both the digest and convert() modes.
- R3-D1 (the builder is right), R3-D3 in isolation, and the R3-D2 plain-head promise hold.
- B1 is linear to 512,000 characters.
- These hold as ruled: F1, F15, F2, F7, F10, F12, B2, B3, D1, D2 and D6.
- The value gate is byte-identical to the PIN's.
- Test isolation holds.
- The Laya lock holds (0 of 6,220 and 0 of 1,788, twice, with the controls firing).
- Digest identity holds (21 of 21).
- Mutation: 8 of the builder's y-group mutants, F10's mutant and 7 of F12's reproduce as FAILED tests.

**If the coordinator rules N2R an edge case under D-034**, the recommendation becomes MERGE-READY-WITH-FOLLOWUPS. The arguments for that ruling are narrow: the leak is in convert() only (the digest is unaffected), and the scanned corpus holds 0 occurrences. The arguments against it are stronger. The shapes are natural: a heredoc HTTP request with a Cookie line followed by `export DB_PASSWORD="…"`, or an ini file with a Cookie line followed by `token="…"`. The contract names this class verbatim. HEAD hides every one of these values.

---

## 0. Premise

- **Re-run at 23:53Z, before any work.** No unexpected difference, so there is no CONTRACT-INVALID.
  - `PIN-is-an-ancestor-of-HEAD`.
  - Lane files: `f6fe76b2b67d316a scripts/transcript_export.py`, `0462fe2e9bdd14bc scripts/session_export.py`, `39478c66e3ab96ed tests/test_transcript_export.py`, `c1bb29a1ec924a71 tests/test_session_export.py`, `21658ac0d86de615 …/dataset-manifest.json`.
  - Documents: `a999989ca57b20da` (SCRUB2-R1-R3-report.md), `088b26ef39d2d904` (SCRUB2-R1-R3-brief.md), `baff2425fb28cdff` (VERIFY-SCRUB2-R1-R2-report.md).
  - `2 files set=e8f27bcb91e7`.
- **Re-checked at 01:11:30Z.** Same five hashes and the same set id. My brief hashes to `ed48cdf1caf194bd`.
  - 12 local commits exist since 0c11fd1. None touches the five files, `known_values_check.py`, `tests/conftest.py`, `pyproject.toml` or `scripts/laya_ft/` (`git log … | wc -l` → `0`).
  - Origin is now 0e6d4a1, from other lanes' pushes.
- **The copies I used** (all under `$W3`):
  - `new/`: a HEAD archive with the lane's five files on top. Its hashes equal the premise.
  - `pintree/`: the PIN, 6ad316dc (`session_export` 68c712893ffed4e9).
  - `r2tree/`: round 2, e36f708b.
  - The PIN and my `new` copy both hold `known_values_check.py` cfdf2ffec10e6d10, the same as HEAD.

## 1. NOT-done

1. **No report file.** The harness forbids report `.md` files. This hand-back is the whole report.
2. **Not re-run:**
   - the builder's full 81-mutant set. I re-ran 16 of them (8 y-group, F10's N1, 7 of F12's W-group), plus 14 mutants of my own;
   - D7's digest timings on the real transcripts (the B1 census covers linearity);
   - the builder's "set A" (96 passed, 1 skipped), which I did not identify;
   - W6 and W11/W28 (round 2 found them equivalent).
3. **Corpus scope.**
   - Thinking blocks are never read, so convert()'s thinking events are not scanned.
   - Subagent transcripts modified in the last 5 minutes were excluded (2 at listing).
   - The main transcript was scanned to 783,146,580 bytes.
4. **No fix attempted.** That is not my role. The suggested directions below are unmeasured.
5. **R3-D5's cause is unknown.** 168 runs did not reproduce it.

## 2. DISCREPANCIES with the builder's report

- **D-a. "N1 and N2 closed" / "0 N2 losses".** N2 is not closed in convert()'s views (R3V-1). The builder's N2 evidence cannot see the class:
  - my round-2 `e2e_n2.py` and the 3 red N2 items put pwd, credentials or Cookie heads after the new head;
  - `rand_v4b` and `rl2` generate no PAYLOAD heads;
  - `corpus3.py` calls `prov.kept(..., "scrub")` only (its lines 79, 85, 165, 178, 179), so its corpus rows never run a PAYLOAD rule.
- **D-b. R3-D3 says "such a head hides less than round 2 did, but never less than the PIN".** This is false in convert(). The segment's marker removes the name of a later R1, PASS or curl head, and that rule then finds nothing (R3V-1). In isolation (no later head of another rule) it holds (R3V-8).
- **D-c. R3-D4 estimates the tail residual only for pwd and credentials values** (about 3 in 10 million, with `_KEY_L`). R3-D2's scheme stop uses bare `_APART`, with no `_KEY_L`, so a token glued to a name also stops. For a Basic or bearer token after an escaped-quote head whose final base64 quartet spells `pwd=`, followed by whitespace, a bare quote, `&`, `,`, `;` or the end, the rate is about 1 in 100,000 (R3V-2). An escaped quote after the token (the canonical-JSON case) does not stop it.
- **D-d. Corpus row A (REAL 0) is scrub-only.** My convert()-mode scan gets the same number, REAL 0. The scope differs; the number does not.
- **D-e. Digest identity.** The builder has 20 of 20; I have 21 of 21 at a later cut (the transcript gained a day). This is consistent.
- **D-f. R3-D1.** The builder is right. The misfiling was my round-2 whole-region `classify()`, which put mixed K+NAME regions into OTHER.

---

## 3. Finding inventory (no severity filter)

| id | class | one line |
|---|---|---|
| R3V-1 | **BLOCKER** | N2R: a head the PIN never read frees a later value a PAYLOAD rule hid (convert()) |
| R3V-2 | FOLLOW-UP (needs a ruling) | Tail residual: a value's own tail that spells a head shows (R3-D4, and R3-D2's TOKEN class) |
| R3V-3 | FOLLOW-UP | F-MUT3: mutants V12 and V14 survive with real output changes (test gaps on two round-3 clauses) |
| R3V-4 | FOLLOW-UP (fix with R3V-1) | Three comments state the invariant N2R breaks |
| R3V-5 | INFO | Mutants V3 (equivalent) and V13 (hides more only) survive |
| R3V-6 | INFO / UNVERIFIED cause | R3-D5 not reproduced: 168 runs, 0 failures |
| R3V-7 | INFO | R3-D1 judged: the 8 OTHER regions are K+NAME |
| R3V-8 | INFO | R3-D3 in isolation: REAL 0 on 9,000 texts × 6 views; linear |
| R3V-9 | INFO | The builder's N2/V4 instruments are scrub-only or lack PAYLOAD heads (why R3V-1 was missed) |
| R3V-10 | INFO | Census: one single-pass reading above the Cookie comment's "at most 0.06 s" |
| R3V-11 | INFO | Round 3 hides more than the PIN in many shapes (not a loss) |

### R3V-1 (BLOCKER): N2R, a head the PIN never read frees a later PAYLOAD-rule value in convert()

- **Evidence level:** reproduced.
  - end to end through `export()` and `session_export.convert()`;
  - red tests;
  - two seeded differentials on each of two versions;
  - the mechanism re-derived from f6fe76b2's source.
- **Contract mapping:** round 3 item 2: "A head the PIN never read (an escaped-quote head, `my_cookie:`, a head after a literal `\t` or `\r`) never frees a later value the PIN hid." Also round 2 item 4 (V4), which round 3 keeps.
- **Canonical path:** yes. The lane's `session_export.convert()` (a fake key) turns a synthetic transcript into events.
  - The leak shows in the tool_call event (the canonical JSON of a Bash or Write input), the tool_result event and the user-turn event.
  - `export()` (the digest) runs too, with `sources=()`, so no source is read.
- **Material effect:** a whole fake credential that the PIN hid appears in convert()'s output, which is the session export.
- **Discriminator:** `probes/test_vscrub2r1r3_red.py` (sha256 prefix 10fac0733a8cbfb0, `1 files set=8d2adae291be`). Round 3 `11 failed`, round 2 `11 failed`, the PIN `11 passed`. Section 5 has the pasted lines.
- **Ownership:** `scripts/transcript_export.py`, a lane file.

**End to end (e2e_n2r.py, final run 01:11:45Z):**

| shape (all fakes) | round 3 digest / convert | round 2 | PIN |
|---|---|---|---|
| Bash heredoc: `Cookie: session=<c>` line, then `export DB_PASSWORD="<v>"` | hid / **LEAK** | hid / LEAK | hid / hid |
| Write config: Cookie line, then `token="<v>"` | hid / **LEAK** | hid / LEAK | hid / hid |
| tool result: `my_cookie: sid=<c>; DB_PASS="<v>"` | hid / **LEAK** | hid / LEAK | hid / hid |
| user turn: `my_cookie: sid=<c>; curl -u "admin:<v>" …` | LEAK / **LEAK** | LEAK / LEAK | LEAK / hid |
| Bash: Cookie line, then `api_key="<v>"` | hid / **LEAK** | hid / LEAK | hid / hid |

The PIN shows the cookie value `<c>` in these shapes (digest 1, convert 5), and round 3 hides it (0 / 0). Round 3 trades a value the PIN showed for one the PIN hid. The contract forbids the second loss whatever the gain.

The red file's 11 items:
- 5 × a line-start Cookie in canonical JSON, then `export DB_PASSWORD="v"` / `token="v"` / `api_key="v"` / `AGENT_TOKEN="v"` / `SMTP_PASS='v'`;
- 4 × decoded: `my_cookie: sid=c; DB_PASS="v"`; `my_cookie: sid=c; curl -u "admin:v" …`; `x\rPWD: sid=cSMTP_PASS='v'` (a literal backslash-r); `my_cookie: sid=c; password=\"v\"`;
- 2 × canonical JSON: `x\tpwd=sid=c\nDB_PASSWORD="v"`; `y\rcredentials = sid=c\r\ntoken="v"`.

**Mechanism** (from f6fe76b2):

1. **The Cookie rule's new-head branch** (line 213): `(?(new)(?P<seg>(?:(?!_APART|_COOKIE)_CL)*)…)`. `_cookie_or_same` (line 155) writes the head plus `<redacted>` when `_COOKIE_FLOOR` (`=[^\s;"']{8}`) is in the segment.
   - `_CL` crosses escaped line ends (`_LESC(?=_LF)`), so in canonical JSON a whole command string is one "line". A Cookie line after an escaped `\n` is a new head: the PIN's `\b` fails after the `n`.
   - The segment stops only at a quote or an escaped quote, or before `_APART` / `_COOKIE`. `_APART = _NAMES + _SEP`, with `_SEP = (?:\\*["']\s*[:=]|\s+[:=]|[:=](?![^\s"'&,;]))`.
   - So `DB_PASSWORD=\"` is not apart (the `=` is followed by a backslash), `DB_PASS` and `SMTP_PASS` are not `_NAMES` at all, and `curl -u` is no name.
   - The segment runs over each of these heads and stops right before the value's quote. The marker replaces the head's name.
   - In `scrub_payload`, R1 `((?:_NAME|_PASS)(?:\\+["'])?\s*[:=]\s*\\+["'])`, the PASS rule and the curl rule run after the SECRET rules, find no head, and the value shows.
2. **pwd and credentials values from a head the PIN never read:** `(?:(?!_LATER_PWD)_VU)+`. `_LATER_PWD` and `_LATER_CRED` stop only before pwd and credentials heads. `_VU` continues over an escape that a value unit follows (V4), so the value takes `\nDB_PASSWORD=` and stops at `\"`.
3. **The scheme rule after an escaped quote:** `(?(esc)(?!_APART))` has the same `_APART` gap. Example: `Authorization: \"Token <tok>password=\\\"V\\\"`, where the PIN's R1 hid V.
4. **Chains:** a head that a stop frees can then take an R1 head as its value. Example: Negotiate's `_OTHER_HEAD` stop frees `credentials=`, and `credentials=` + a line end + `password=\"V\"` takes `password=` as its value. The `<redacted>` marker's `>` also satisfies `_KEY_L`.

**Size:**

| measurement | lost later values (views) |
|---|---|
| rand_n2c.py, 4,000 texts × 6 views, round 3, seed 20260929 | 923 (call 280, call2 278, ptxt 280, txt 85; dig 0, pdig 0) |
| same, round 3, seed 11 | 1,001 (call 298, call2 307, ptxt 298, txt 98) |
| same, round 2, seeds 20260929 / 11 | 1,024 / 1,130 (round 2 also lost 14 / 17 in dig) |

- By first head (seed 20260929): Cookie heads the PIN never read 350; Cookie heads that are escaped in a raw view 68; credentials new heads 216; pwd new heads 289.
- The later heads freed are all PAYLOAD heads: AGENT_TOKEN, DB_PASS, DB_PASSWORD, PASS, SMTP_PASS, X_PASS, api_key, curl -u / --user, password (quoted and escaped-quoted), token, secret, X-Agent-Token.
- sch3.py (3,000 texts × 6 views, seed 42), LATER class: 1,400 characters: bare 182, esc1 448, esc1s 336, esc3 392, plain 42 (the plain row is the chain in point 4).
- The digest (scrub(): what the push syncs as `transcripts/sandbox`) loses 0 in dig and pdig. The leak is convert()-only, which is the session export.

**Exposure:** on this session's corpus, REAL 0 in convert() mode and in digest mode (R3V-7 and section 4, item 2). No occurrence exists today. The shapes are natural, so the zero is today's data, not a bound.

**Suggested fix (unmeasured):** every value that starts at a head the PIN never read needs a stop before every head a LATER rule in `scrub_payload` reads, not only the SECRET rules' heads. That covers the Cookie new-head segment, `_LATER_PWD` / `_LATER_CRED`, and the scheme token after an escaped quote. The heads to add:
- a separator followed by an escaped quote (`[:=]\s*\\+["']` after a `_NAMES` or `_PASS` name);
- `_PASS` names with `=` or `:`;
- `(?<![A-Za-z0-9_.\-])curl\b`.

Then re-measure with `rand_n2c.py` (both seeds) and `sch3.py` (LATER class) to 0. After that, run the 11 red items, `census3.py` with `retime3.py`, the Laya lock (these stops also change `scrub()`) and the floor. An alternative to measure, not recommend: run the PAYLOAD heads' rules before the new-head values in `scrub_payload`.

### R3V-2 (FOLLOW-UP, needs a ruling): tail residual, where a value's own tail spells a head

- **Evidence level:** reproduced.
  - `r3d4.py`, 3,000 texts × 5 views, seed 9: characters lost against the PIN in the value BODY 0; in the TAIL 24,817.
  - The losses occur only where the tail spells `pwd` or `credentials` + a separator after a non-alphanumeric character: `/pwd=`, `+pwd=`, `-pwd=`, `.pwd=`, `_pwd=`, `=pwd=`, `/PWD:`, `/pwd =`, `/pwd"=`, `/credentials=`, `+Credentials=`. `%2Fpwd=` loses nothing.
  - `sch3.py`, TOKEN class: 3,573 characters (bare 714, esc1 881, esc1s 924, esc3 1,054). This is new in round 3; round 2 had no TOKEN class.
  - Direct check: settle(`Authorization: \"Basic dXNlcjpwd= next`) gives round 3 `…Basic <redacted>pwd= next`; the PIN's Basic payload rule gives `…Basic <redacted> next`. Followed by `\"`, round 3 hides the whole token. The digest: the PIN shows the whole token there, so round 3 hides more.
- **Contract mapping:** V4 (round 2 item 4), literally: the PIN hid these characters. So the predicate holds on its face, and an explicit ruling is needed, as D1 and D6 had.
- **Material effect:** only the characters that spell a head name at a value's end show (`pwd=`, `credentials=`). No body character was shown across 28,390 lost characters.
- **Rates:**
  - pwd and credentials values (with `_KEY_L`): about 3 in 10 million base64 values, the builder's estimate. My analytic check agrees: (1/32)^4 × about 1/3 for one pad.
  - Basic and bearer tokens after an escaped-quote head (no `_KEY_L`): at most about 1 in 100,000. That is (1/32)^3 for `pwd` in any case × about 1/3 for one pad, and only when a non-backslash separator follows. Lower-case `pwd=` decodes to byte 0xA7, so an ASCII `user:pass` cannot end in it.
- **My D-034 reading:** not CORE-BLOCKING.
- **Suggested fix:** put `_KEY_L` before the name in the scheme stop (`(?(esc)(?!` + `_KEY_L` + `_APART))`), as `_LATER_PWD` does. That keeps R3-D2's `.pwd=` case and drops the glued `…jpwd=` case. Or rule the residual D6's class (a name shown).

### R3V-3 (FOLLOW-UP): F-MUT3, two round-3 clauses are pinned by no test

- **V12:** the scheme stop after an escaped quote uses `_OTHER_HEAD` in place of `_APART`. It SURVIVED (247 passed).
  - mutdiff.py, 3,000 texts × 6 views: 457 texts differ; the mutant shows 74 planted fakes that round 3 hides, and hides 72 that round 3 shows. Example: `Authorization: \'ApiKey <tok>.token=abcpwd="<v>"`.
  - Kill it with R3-D7's own rule: "a glued head with a glued value stays in the token and is hidden there". For example, settle(`Authorization: \"Basic abcdefgh.token=zq12`) must be `…Basic <redacted>`.
- **V14:** `_LATER_PWD` without `_KEY_L`'s escape-letter branch (`(?<![A-Za-z0-9])` only). It SURVIVED.
  - 282 texts differ; the mutant shows 962 planted fakes that round 3 hides, and hides 0 that round 3 shows. Example: decoded `pwd=<v1>\tPWD: <v2>` (a literal backslash-t): round 3 hides v2, V14 shows it.
  - Kill it by asserting v2 hidden.
- In both examples the mutant falls back to the PIN's behavior. That is no loss against the PIN, so this is not a blocker. But the protections round 3 adds there are unguarded.

### R3V-4 (FOLLOW-UP, fix in the same change as R3V-1): comments that state the broken invariant

These three comments claim an invariant that R3V-1 shows the code does not keep. In `scrub_payload`, R1, PASS and curl read heads after those values.
- line 120, `_COOKIE_PIN`: "a later head that stands apart (_APART) or a later Cookie head (_COOKIE), which their rules take";
- lines 104-110, `_LATER_PWD`: "the heads a rule still reads after that value (the Cookie and scheme rules ran before)";
- lines 239-241, the pwd/credentials rule: "neither runs over a later pwd or credentials head that a rule still reads".

### R3V-5 (INFO): surviving mutants V3 and V13

- **V3** (`_COOKIE_PIN` without `_KEY_L`) is equivalent. 0 of 3,000 texts differ in any of the 6 views. `\b` before `cookie` already implies `_KEY_L`'s first branch. For `set-cookie`, only the match start moves, and the head is kept as written.
- **V13** (the segment stops at `_COOKIE_PIN` heads only) hides more only. v13chk.py, 3,000 lines of 2-4 new Cookie heads: 655 differ; LOSS 0, GAIN 1,526.

### R3V-6 (INFO; cause UNVERIFIED): R3-D5 not reproduced

- 30 rounds × 4 parallel runs of `tests/test_transcript_export.py -x` (one copy and one basetemp each): `120 247 passed`.
- The builder's control shape, 6 rounds × 4 workers × both files: `24 247 passed`, `24 73 passed`.
- 0 failures in 168 runs. These lines are the harness's `uniq -c` of pytest's last line, not test_summary.sh.
- The test's text holds no word a changed rule reads, and its code (the value gate, `turns()`, `main()`) is byte-identical to the PIN's.

### R3V-7 (INFO): R3-D1 judged

The shape `credentials = sid=\rcredentials = =` classifies per position as:
- decoded: K 4, ESC 2, NAME 11;
- raw: NAME 11.

The value after the name is PINSHOW, or HID when a value follows. REAL is 0. The builder is right. My round-2 table misfiled mixed regions.

### R3V-8 (INFO): R3-D3 in isolation

`ck3.py` builds Cookie lines with no other rule's head after them:
- 37 head forms: case, Set-Cookie, spaces before the colon, escapes and quotes after it, a letter, digit, `_` or non-ASCII letter before it;
- 1-4 pairs with escapes, pairs and `%3D`, sometimes a second head;
- 3,000 texts (seed 5) + 6,000 texts (seed 6), × 6 views.

REAL 0, NAME 0, K 0; only ESC (non-value characters). Linear: see item 7.

### R3V-9 (INFO): why R3V-1 was missed

See D-a. Any future V4 or N2 claim should be measured in convert() mode as well. `probes/corpus_n2r.py` does that: it settles decoded texts and the canonical JSON of each tool input, as convert() does.

### R3V-10 (INFO): census noise against the Cookie rule's comment (line 211)

The comment says "at most 0.06 s … on each 64,000-character text". My single pass, under other lanes' load, read 0.0854 s (`r3 new seg long` at 64k). The minimum of 3 is 0.0482 s. Growth is linear.

### R3V-11 (INFO): round 3 hides more than the PIN in many shapes

Examples:
- the cookie values in R3V-1's shapes;
- `écookie:` / `のcookie:` (escape_nonascii: the PIN LEAK, round 3 hid);
- heads after a literal backslash-letter (`C:\npwd=<v>`: the PIN showed it in all 6 views, round 3 hides it).

This is by design (F1, F12). It is not a finding against the contract.

---

## 4. Evidence by brief item

**1. N1 and N2.**
- My round-2 red file on the final bytes (`1 files set=bcd44bc128b4`): round 3 `16 passed in 0.06s`, round 2 `16 failed in 0.12s`, the PIN `16 passed in 0.05s`.
- New N1 shapes: `floor_units2.py` (every head × backslash content × position, 6 views) shows only D1's 7 cells per credentials head, in decoded views, as ruled. `e2e_floor.py`: all hid. `pos3.py`: REAL 0 (below). **N1 closed.**
- Round 2's N2 shapes: `e2e_n2.py` all hid; cookie values 0/0 (the PIN's 2/4).
- New N2 shapes: `rand_n2c.py` covers the Cookie head forms the brief lists, plus pwd and credentials heads in every view. Result: **R3V-1**.

**2. V4 (my own classifier: pos3helpers.classify, per position).**
- Classes: ESC (not a value character, whitespace included), NAME, K (hidden when the credentials floor counts escapes: D1 undone), REAL.
- rl2, 20,000 texts (seed 20260929), decoded and raw scrub:
  - round 3 REAL 0 (dec: ESC 723, K 359, NAME 30,646; raw: ESC 1,653, K 224, NAME 17,958);
  - round 2 REAL: dec 57, raw 210.
- v4b, 4,000 texts × 6 views: round 3 REAL 0 (K 3,489 only in dig and txt, which is D1); round 2 REAL 120-167 per view.
- Corpus, `corpus_n2r.py` (convert() mode = settle of decoded texts and of each tool input's canonical JSON; digest mode = scrub of decoded texts; masked shapes only; thinking never read):
  - **main:** 155,026 lines, 54,607 texts, 2,214 with a changed rule's word. 1 changed (dec, both modes): NAME 11. **REAL 0.**
  - **subagents:** 366 settled files (649,143,786 bytes at listing), 157,280 lines, 84,952 texts, 4,303 candidates. Changed: call/settle 37, dec/scrub 71, dec/settle 71.
    - Classes: call ESC 98, NAME 156; dec ESC 380, K 1,366, NAME 495 / 519.
    - Values after the names round 3 newly shows: HID 13, NOVALUE 4, PINSHOW 30 / 32 (dec) and 14 (call), LOSS 5. The LOSS 5 is one shape: a credentials value that is a chain of names, classes K+NAME.
    - **REAL 0.**
- The builder's REAL 0 is re-derived, and it extends to convert() mode on today's corpus. R3-D1: R3V-7.

**3. R3-D2** (`sch3.py`, 3,000 texts × 6 views, seed 42).
- Plain and bare heads: `scrub()` equals round 2's in 3,000 of 3,000 texts. A plain head keeps the PIN's whole token in the digest.
- Lost against the PIN: 7,534 value characters in all (round 2: 6,196):
  - TOKEN 3,573 (R3V-2);
  - LATER 1,400 (R3V-1);
  - OTHER 2,561. OTHER is the generator's structure (names, `next`); no planted secret is in it.

**4. R3-D3.** In isolation: R3V-8. With a later PAYLOAD head: R3V-1. Linear: see item 7.

**5. R3-D4.** R3V-2 (BODY 0, TAIL 24,817).

**6. R3-D5.** R3V-6.

**7. B1** (`census3.py` = round 2's 65 families + 32 aimed at round-3 clauses = 97 families × 8 targets, at 8k / 16k / 32k / 64k characters).
- The 32 new families target: `_COOKIE_PIN`'s lookahead, the new-head segment and its floor search, the `_LATER_*` stops, `_CRED_FLOOR`'s lookbehinds, the scheme stop after an escaped quote, and `_KEY_L` escapes.
- Worst at 64k:

| target | worst at 64k | family |
|---|---|---|
| cookie | 0.0854 s | r3 new seg long |
| scheme | 0.0454 s | r3 sch esc token |
| pwd | 0.0343 s | pwd heads |
| cred | 0.0292 s | r3 later cred |
| pemL | 0.0062 s | (F7) |
| neg | 0.0512 s | |
| scrub | 0.1220 s | r3 cred floor esc |
| payload | 0.1498 s | auth bs |

- 14 flagged rows (a single ×3+ step above 0.02 s) and 4 worst rows were re-timed at 64k→512k, minimum of 3 runs (`retime3.py`). Every row grows ×1.6-×2.6 per doubling.
- Worst at 512k: payload `auth bs` 0.8122 s, payload `pwd\q heads` 0.7340 s. No stop, no timeout.

**8. Earlier rounds stay true.**
- **F1, F15, F2** (VERIFY-SCRUB2's scripts via `after_v3.py`):
  - escape_named: 30 of 30 target cells hid/hid;
  - escape_nonascii: 12 of 12 hid/hid;
  - cred_convert (F15): "T redacted: False | ordinary words gone: []" (D1 as ruled);
  - negotiate: 11 of 11 schemes "token survives in: none".
- **B2 and B3** (`b2b3_var.py`): LOST 0 in all 6 views (B2 n=455, B3 n=672).
- **D2** (`d2_sib.py`): round 3 equals round 2 in every cell, and every cell is ≤ the PIN's.
- **D6** (`d6chk.py`, 10 shapes × 6 views): 0 LOST rows.
- **D1:** floor_units2 shows only the 7 D1 cells.
- **F7:** pemL worst 0.0062 s.
- **F10:** the session_export mutant N1 is KILLED by `test_each_gate_pattern_name_labels_its_own_rule`.
- **F12:** W1, W4, W5, W7, W8, W10, W13: 7 of 7 KILLED.
- **The value gate:** `known_values_check.py` is unchanged (cfdf2ffec10e6d10). `transcript_export.py`'s value-gate section, `main()` and `turns()` are byte-identical to the PIN's. Its tests pass in the floor.
- **Test isolation** (strace on file syscalls plus a GH_TOKEN/GITHUB_TOKEN lookup logger; the two files):
  - absent: `320 passed in 45.77s`; 0 syscalls and 0 opens on all four source paths; 0 token lookups.
  - fakes: `320 passed in 44.85s`; 0 opens. There are 3 stat-only syscalls on the copy's fake `.pc-bridge.env` (`…/.pc-bridge.env/pyvenv.cfg`, `…/conda-meta/history`, one `newfstatat`); 0 lookups.
  - control: `1 passed in 0.25s`; opens 1 / 1 / 1 and 1 GH_TOKEN lookup. The instrument sees what it must.
  - These are pytest's last lines through the trace harness.
- **The Laya lock** (`laya_lock.py`; git reads of the shared repo only):

| run | round 3 differs from the PIN | control N-pwd | control E |
|---|---|---|---|
| v2 `collect_v2` at 434b727dfd | 0 of 6,220 items | 16 | 6,220 |
| v1 `collect` at eb256f49c0 | 0 of 1,788 | 0 | 1,788 |
| v1 `collect` at 0b342c7a29 | 0 of 1,788 | – | 1,788 |

- **The manifest:** one line differs from HEAD's: `"scripts/transcript_export.py": "f6fe76b2b67d316acc574c6e7ade4c7aedd994dc7157c4f599ee15018bc15274"`, the full sha256 of the lane's file.
- **Digest identity** (`digests3.py`: the main transcript streamed to a fixed end, no copy on disk, `sources=()`):
  - "fixed at 784899080 bytes; digests pin 21 new 21 ; identical 21 ; differ []";
  - 19 of 21 are byte-equal to the committed digests. The two that differ, 2026-09-28 and 2026-09-29, grew since the last committed export.

**9. Mutation** (my driver `mut3v.py`: 4 worker copies of the final bytes; the control passes whole first; KILLED only on a FAILED test).
- Controls: 4 × `247 passed` (and 4 × `73 passed` for the session file).
- **The builder's y-group, 8 reproduced, all KILLED:**

| mutant | failing test |
|---|---|
| Y3 | `test_r1_an_escaped_newline_or_tab_ends_a_value` |
| Y10 | `test_r3_a_value_stops_only_before_a_head_that_a_later_rule_reads` |
| Y13 | `test_r3_a_head_the_pin_never_read_frees_no_later_value` |
| Y16 | `test_n2_a_newly_read_cookie_head_never_frees_a_later_value[my_co…]` |
| Y25 | `test_r3_a_new_cookie_heads_floor_is_searched_in_its_segment` |
| Y28 | `test_r1_named_rules_hold_every_f1_context_end_to_end` |
| Y29 | `test_n2_a_newly_read_cookie_head_never_frees_a_later_value[{\"C…]` |
| Y32 | `test_r3_a_head_the_pin_never_read_frees_no_later_value` |

- **My 14 mutants for clauses the y-group does not cover:** 10 KILLED:
  - V1: `_COOKIE_PIN` with no space before the colon;
  - V2: no line end after the colon;
  - V4: `_COOKIE_FLOOR` without its `=`;
  - V5 and V6: a new head never hides / always hides;
  - V7 and V8: `_LATER_*` stops at any separator;
  - V9: `_CRED_FLOOR` without its 8-character lookahead;
  - V10 and V11: the floors 8 → 7.
- 4 SURVIVED: V3 and V13 (R3V-5), V12 and V14 (R3V-3).

---

## 5. Pasted gates (through masked.sh absent, a private `--basetemp` argument, scratch copies)

```
floor pass 1 (start 23:59:33Z)
pytest-exit: 0
pytest-summary: 877 passed in 146.32s (0:02:26)
12 files set=27f27a25516b
floor pass 2 (start 00:02:00Z)
pytest-exit: 0
pytest-summary: 877 passed in 143.90s (0:02:23)
12 files set=27f27a25516b
the two changed test files: 320 passed in 29.82s   (2 files set=e8f27bcb91e7)
round-2 red file (16): round 3 "16 passed in 0.06s"; round 2 "16 failed in 0.12s"; PIN "16 passed in 0.05s"   (1 files set=bcd44bc128b4)
N2R red file (11), first run: round 3 pytest-exit: 1 / pytest-summary: 11 failed in 0.11s; round 2 11 failed in 0.09s; PIN pytest-exit: 0 / 11 passed in 0.04s
N2R red file (11), final 01:11:45Z:
== N2R red on new (final)
pytest-exit: 1
pytest-summary: 11 failed in 0.09s
== N2R red on pintree (final)
pytest-exit: 0
pytest-summary: 11 passed in 0.04s
1 files set=8d2adae291be
```

## 6. Reproduced, reviewed statically, skipped

- **Reproduced:**
  - every number above;
  - the R3V-1 mechanism, re-derived from f6fe76b2's source and confirmed by provenance, which asserts equality with the real `scrub` / `scrub_payload` / `settle` output on every text.
- **Reviewed statically:**
  - the comment claims in R3V-4;
  - the ASCII argument in R3V-2 (lower-case `pwd=` decodes to 0xA7);
  - the V3 equivalence argument (also 0 of 3,000 by differential).
- **Skipped:** see NOT-done.
- **Worker restart:** the sandbox worker restarted at about 01:13Z. After it, the scratch was intact and the lane hashes were unchanged (01:15:21Z).
- **Scratch after cleanup:** 63 MB, and every `rm` target was guarded.

## 7. Paths

- **Scratch root:** `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2r3/`
- **Probes** in `probes/`:
  - `e2e_n2r.py`, `test_vscrub2r1r3_red.py`, `rand_n2c.py`, `sch3.py`, `ck3.py`, `r3d4.py`;
  - `pos3.py`, `pos3helpers.py`, `corpus_n2r.py`;
  - `census3.py`, `retime3.py`;
  - `mut3v.py`, `mutdiff.py`, `v13chk.py`;
  - `after_v3.py`, `b2b3_var.py`, `d2_sib.py`, `d6chk.py`, `digests3.py`;
  - `lib.py`, `prov.py`, `floor_units2.py`, `e2e_floor.py`, `e2e_n2.py`.
- **Isolation and Laya instruments:** `vprobes/trace3.sh`, `vprobes/laya_lock.py`. `vt/` holds the symlinks they use.
- **Red trees:** `red_new/`, `red_r2tree/`, `red_pintree/` (each `scripts/transcript_export.py` + `tests/`).
- **Outputs:** `results.txt`, `n2c_*.txt`, `pos3_*.txt`, `sch3_new_42.txt`, `census3_a.txt`, `census3_b.txt`, `retime3.txt`, `mut3v.txt`, `mut3v_f.txt`, `mutdiff.txt`, `f1f15f2_r3.txt`, `b2b3d2_r3.txt`, `scan_n2r_main.json`, `scan_n2r_sub.json` (masked shapes and counts only).

**Recommendation (repeated): NOT-READY on R3V-1 (N2R).** I reproduced it end to end through `convert()` on the final bytes, with a red discriminator (round 3 11 failed / the PIN 11 passed). It becomes MERGE-READY-WITH-FOLLOWUPS only if the coordinator rules N2R an edge case under D-034. The follow-ups are R3V-2 (needs a ruling), R3V-3 and R3V-4.