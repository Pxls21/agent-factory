# S198A report — the transcript scrubber stops a value before the next secret name (AF-AP-157, task #198 increment A)

LANE: s198a (sandbox agent `code-implementer`, shared tree, no worktree). PIN 9801fb5. Report finished 2026-09-23 16:3xZ.

TL;DR — DONE (tests green, differential clean), NOT committed (lane rule). FIRST: the real transcript shows NO old-scrubber
digest line holding a value the new scrub redacts (0 runs; §7), so no credential rotation is indicated by this class. The fix
reaches BEYOND the brief's literal head check: extensions X1–X4 (§2.2) are flagged for the coordinator to accept or reject.
Item 3 (no new exposure) and item 4 (linear) forced them. X2 changes a SECOND pattern (the Bearer rule).

- [x] item 1 premise: boundary blobs MATCH at the PIN, 172dbe2, 87b708d and the tree; the 3 leaks reproduce (§1). D1: P's test file has no pytest test.
- [x] item 2: 10 chained + 4 in-run + 6 later-rule shapes close; floor read on the uncut run, cut values exempt (§2.1).
- [x] item 3: (a) 259 T strings, 0 violations; (b) 100,000 generated, 0 violations, 0 of 176,838 planted fake secrets leak (the PIN leaks in 45,331 inputs); (c) real transcript, 0 differing digest lines, 0 violations, 0 old leaks (§4, §7).
- [x] item 4: order unchanged; 2 patterns changed; 22 adversarial families at 16k–128k, every ratio ~2.0 (§5).
- [x] item 5: 21 red at the PIN for their stated reasons, 72 green after; 27 negative controls keep their PIN output (§3).
- [x] item 6: 13 mutants (m1–m5 per the brief, plus 8 more), each red on a named test for its stated reason (§6).
- [x] item 7: 72 passed twice (set 4e81d5d61609); P's script 15 checks twice; lint_delta 0 new hits (§8).
- [ ] NOT done: the AF-AP-157 exposure of `transcripts/pc/` (needs the PC state.db, §7); `volatile.py` (increment B); no commit or push (§11).

FINAL blobs: `scripts/transcript_export.py` 37d94bd615568fdbac6dd69a2e95df56a4448674 (AST-identical to 515d78b, the blob every
measurement in §3–§7 ran on; comments only differ, proved in §8); `tests/test_transcript_export.py` 12dbaae6d0da1e21381d3c104edaad73d2a2d938
(sha256 prefix efb6cd6016181f0a, the file the red, green and mutant runs used).

## 1. Premise re-measure (contract item 1)

Measured 2026-09-23 15:12:13Z (`date -u`), shared tree HEAD 87b708d (the brief's own commit on top of 172dbe2).

```
== 9801fb5 (9801fb5e4d600f3608ee09e7387f0ac12db374e6)
a47e0e5861c90912df2e3eee31a77b5bf66e1e7b scripts/transcript_export.py
8d1723beb46ecde73fdddf6a6048df32ff5635b5 tests/test_transcript_export.py
04326ece5b7a6ac59b76e2fc2a3d7ec6ff5b7c70 harness-ports/bin/hermes-session-export.py
0d7893bf5d2ec1a16a013bb06ca1d7cc0baf65ec harness-ports/tests/test_hermes_session_export.py
== 172dbe2, == HEAD (87b708d9...), == worktree (git hash-object): the same four ids, byte for byte
== git status --porcelain on the boundary + readers: empty
```

Boundary verdict: MATCH at the PIN, 172dbe2, HEAD and the working tree. No CONTRACT-INVALID.

Premise gates (15:12:34Z):

```
grep lines: 24 SECRET_PATTERNS, 29 key block, 33 credential assignment, 35 Bearer, 37 sk-, 38 gh*, 39 AIza, 40 xox, 42 trycloudflare, 44 opaque, 48 def scrub  (as the brief)
P imports S by path: hermes-session-export.py:8, :23, :27                                                                   (as the brief)
python -m pytest -q -p no:cacheprovider tests/test_transcript_export.py harness-ports/tests/test_hermes_session_export.py
23 passed in 1.19s   rc=0
23 passed in 1.28s   rc=0
bash scripts/pc_suite.sh set-id -- tests/test_transcript_export.py harness-ports/tests/test_hermes_session_export.py
2 files set=4e81d5d61609
five chained shapes through the PIN's scrub (scratch copy, blob a47e0e5):
LEAK 'passwd=aAPI_KEY : X4Z92Q0X1ZX02Z71' -> 'passwd=<redacted> : X4Z92Q0X1ZX02Z71'
LEAK "token='_API_KEY = 6Z4Z02ZX6Z4Z" -> "token='<redacted> = 6Z4Z02ZX6Z4Z"
LEAK "password='-db_password: 62669Q3JJ88ZX5466" -> "password='<redacted> 62669Q3JJ88ZX5466"
ok   'key: service-API_KEY: QZJ8QZJ8QZJ8' -> 'key: service-API_KEY: <redacted>'
ok   'mask-PASSWORD=QZJ8QZJ8QZJ8;token: WQ7XWQ7XWQ7XWQ7X' -> 'mask-PASSWORD=<redacted>;token: <redacted>'
```

DISCREPANCY D1 (gate coverage, not a boundary mismatch): pytest collects NO test from
`harness-ports/tests/test_hermes_session_export.py` — it defines only `main()` (file:45), no `test_*` function:

```
python -m pytest --collect-only -q -p no:cacheprovider harness-ports/tests/test_hermes_session_export.py
no tests collected in 0.01s   rc=5
python3 harness-ports/tests/test_hermes_session_export.py
test_hermes_session_export: 15 checks passed   rc=0
```

So the brief's `23 passed` is T's 23 tests alone (1+1+1+1+7+1+8+1+1+1). P's real gate is the script, run by
`harness-ports/tests/run-all.sh:12-14`. Every gate below runs BOTH: the pytest line over the brief's set (set=4e81d5d61609)
AND P's script, so P's 15 checks are not silently absent. I did not change P's test file (read-only; adjacent observation,
reported, not fixed).

DISCREPANCY D2 (a third reader the brief does not name): `harness-ports/bin/qwen_matrix.py:126-137` (`_scrub_messages`) also
loads S by path and applies `scrub` to matrix prompts; its test `harness-ports/tests/test_qwen_matrix.py:229-241` asserts
`api-key=<redacted>`, `Bearer <redacted>`, `sk-<redacted>`. Baseline at the PIN: `test_qwen_matrix: 4 tests passed` rc=0.
Found by a literal sweep (`git grep -n transcript_export`); crg `callers_of scrub` lists it too (`target_resolution: unresolved`).
I run it as an adjacent-consumer check after the change (read-only). The outward path is `scripts/push_clean.sh:117-118`
(`transcript_export.py --out transcripts/sandbox` on every push).

Impact tooling: GitNexus `impact scrub` failed (`LadybugDB unavailable ... checkpoint is in progress`, risk UNKNOWN), so the
blast radius comes from crg `callers_of` (3: `export`, `qwen_matrix._scrub_messages`, `hermes-session-export._body`) plus the
literal sweep above. No other caller found.

## 2. Design (contract items 2 and 4) — FINAL, then the history that produced it

### 2.1 The final rule (S at blob 37d94bd; its code is AST-identical to 515d78b, the blob every measurement ran on)

Terms. V = the PIN's value class `[^\s"'&,;]`; a run = a maximal V sequence. NAME = the PIN's name alternation plus a bare
`[_-]key` (`scripts/transcript_export.py` `_NAME`). WORD = a name read at its SHORTEST: a fixed secret word, or `_key`/`-key`
with no alphanumeric prefix (`_WORD`). HEAD = WORD, an optional quote, whitespace, `:` or `=` (`_HEAD`).

Credential entry (`SECRET_PATTERNS[1]`, callable `_redact_run`):
1. Start = the PIN's group 1 over NAME (name, quote, whitespace, separator, whitespace, quote). The bare `[_-]key` alternative
   never matches earlier than the PIN's compound form on plain text (the compound starts at the alphanumeric run's start); it
   only lets a match start where a previous value stopped before `_key`/`-key`.
2. Floor = the PIN's, read on the UNCUT run: `(?=V{8})`. Below it nothing matches, as at the PIN.
3. The value (`_VALUE`) is one linear pass over tokens:
   - an in-run head: WORD, `:`/`=`, then a value character (the name stays; the text after it is that name's value);
   - a bridge link (`https?://<host>.trycloudflare.com`) taken WHOLE, its tail crossing `&`, `,`, `;` up to whitespace, a quote
     or `)`, in-run heads still split inside it;
   - a value character that starts neither a HEAD nor a Bearer match nor a link.
   It stops before a head whose value starts past the run (a quote or whitespace after the name or the separator) and before
   a Bearer match (`Bearer`, case as the Bearer rule, whitespace, 8 token characters). The next match takes the head with its
   own floor; the Bearer rule takes the Bearer match.
4. Every value piece is replaced by `<redacted>`, whatever its length; G1 and in-run heads are kept (`_CUT`).

Bearer entry (`SECRET_PATTERNS[2]`): `(Bearer\s+)` then the floor on the uncut token run `(?=[A-Za-z0-9._\-]{8})`, then token
characters that start neither a following Bearer match nor a bridge link; `\1<redacted>` as before.

Order: `SECRET_PATTERNS` order is unchanged (key block, credential, Bearer, sk, gh, AIza, xox, bridge link, opaque); the key
block's comment still holds (its behavioral test `test_key_block_after_a_credential_keyword_is_scrubbed_whole` is green).

Floor decision (the brief's question): the floor is read once, on the uncut run, exactly as at the PIN; it is NOT applied to a
value cut short by a head, nor to a value after an in-run head, nor to a Bearer token cut before a following Bearer/link.
Reasons: (a) item 3 — the PIN redacted every byte of a qualifying run, so a floor on a piece shows bytes the PIN hid
(`passwd=QZJ8Q_api_key=X4Z9...` would show `QZJ8Q_`; `passwd=QZJ8QZJ8_API_KEY=X4Z9X4Z` the 7-character value); (b) the floor
spares prose (`sort_key: name`), and a run that already reached 8 characters after a secret name is not prose; (c) past the run
a value is an ordinary assignment and keeps the ordinary floor, so `"api_key": short` keeps its PIN output everywhere.

### 2.2 DEVIATIONS / EXTENSIONS beyond the brief's literal head check — flagged for the coordinator (not self-accepted)

The brief specifies "the value stops before a head". Meeting item 3 (no new exposure) and item 4 (linear) forced four
extensions. Each was found by this lane's own differential or timing, not assumed:

| id | extension | why (evidence) | behavior change vs the PIN |
|----|-----------|----------------|---------------------------|
| X1 | the credential value stops before a Bearer match | a head the PIN swallowed now starts its own value, which could eat `Bearer`; the Bearer rule then never fired and its token showed — 56 runs in 20,000 generated inputs (15:4xZ classifier) | `token=QZJ8:Bearer X4Z9...` was `token=<redacted> X4Z9...` (leak), now `token=<redacted>Bearer <redacted>` |
| X2 | the Bearer rule (a SECOND pattern) stops its token before a following Bearer match and a bridge link; its floor reads the uncut run | X1 handed text to the Bearer rule, whose own token class ate a following `Bearer` or `https` — 5 examples in the full 100k run (16:0xZ): `Bearer <v1>Bearer <v2>` showed `<v2>`, `Bearer <v>https://...` showed the link | `Bearer QZJ8QZJ8QZJ8Bearer X4Z9...` was `Bearer <redacted> X4Z9...` (leak), now both redacted |
| X3 | the credential value takes a bridge link whole (past `&`, `,`, `;`) | a value that ended at `&` inside a link left the link rule nothing to match; the tail showed — 9 runs in 20,000 inputs. The first fix (a conditional stop before such a link) was QUADRATIC: `password=` + 4000 links took 11,670 ms at 112k characters (x4 per doubling), so it was replaced | `api_key=https://…trycloudflare.com/x&s=X4Z9...` was `api_key=<redacted>&s=X4Z9...` (leak), now `api_key=<redacted>`; a link with no `&,;` keeps its PIN output |
| X4 | inside a value a name is read at its SHORTEST (fixed word or bare `_key`/`-key`); an assignment may start at a bare `_key`/`-key` | with the compound reading, `password=QZJ8QZJ8my_key: X4Z9...` showed `QZJ8QZJ8my` (the password) — the compound class read the whole glued run as the name; 119,859 planted fake-secret bytes shown in 100k inputs (16:03Z run before X4) | tension with item 2 "a name stays a name": a compound name GLUED to a value keeps only its `_key` suffix visible (`DB_PASSWORD=QZJ8QZ12REDIS_KEY=X4Z9X4Z9` -> `DB_PASSWORD=<redacted>_KEY=<redacted>`); premise shape 1 reads `passwd=<redacted>API_KEY : <redacted>` (the stray `a` is value, hidden as at the PIN) |

Contract reading (stated, both items need it): item 2's "a name stays a name" shows bytes the PIN hid inside its value (the
premise's own `aAPI_KEY`). So "value byte" in item 3 excludes the shortest-form head (WORD + quote + whitespace + separator)
and the `Bearer` keyword handed to its rule. The differential enforces exactly that and counts the excused bytes.

RESIDUAL R-1 (reduced by X4, measured): a secret value that itself contains a shortest-form head (for example `…token=…` or
`…_key:…` inside a password) shows that head's bytes (at most the word, a quote, whitespace and the separator). A base64 value
can only end in `=`, so `…_key=` at its end is the one realistic shape; the value's other bytes stay redacted.

### 2.3 History (both states reported, per rule 5)

- State A (15:35Z, blob 9e6d4bd): value stops before heads (compound NAME), floor on the uncut run, in-run heads continue.
  Green on T (59 passed); the differential's 2,000-input smoke run (15:39Z) found 65 violation bytes (digit-flip confirmed 32)
  and the planted-secret oracle found 201 inputs with a new leak. Basis: the harness in §4. Classified (15:4xZ, 20,000 inputs):
  56 Bearer runs, 9 bridge-link-tail runs, 0 other.
- State B (15:45Z, blob c6f303f): + a stop before a Bearer match and before a link that runs past the value. 100,000 inputs
  (15:51Z): 134 violation bytes left (Bearer-rule gaps, 5 examples), and the R-1 count (119,859 planted bytes shown inside
  compound "heads") showed the head allowance was excusing real value bytes; the link stop was quadratic (11,670 ms at 112k).
- State C (FINAL, 16:03Z, blob 515d78b): X1-X4 as above. Everything in §3-§6 is measured on State C.

## 3. Tests (contract item 5): red at the PIN, green after (FINAL, State C)

New in T (`tests/test_transcript_export.py`, all behavioral; no source-text pin, so AF-AP-80 does not arise; pattern order is
guarded by the existing behavioral `test_key_block_after_a_credential_keyword_is_scrubbed_whole`):

- `SCRUB` loads S by path (as P does).
- `CHAINED` (10, `test_a_value_stops_before_the_next_secret_name`): the three premise leaks; a `token` head whose separator ends
  the run; upper case with the name at the run's very end; a quote before `:` (JSON); a quote after `=`; lower case with a
  hyphenated name; three heads in one run; a value glued to a `*_key` name (X4).
- `IN_RUN` (4, `test_a_value_cut_by_a_head_is_redacted_at_any_length`): a short piece cut by a head (m5), a short value after an
  in-run head (m6), an empty piece, two env lines glued (X4). The PIN hides these values too but swallows the second name.
- `LATER_RULES` (6, `test_a_match_leaves_a_later_rule_its_whole_match`): X1 (two), X3 (two), X2 (two).
- `PIN_OUTPUTS` (27, `test_negative_controls_keep_their_pin_output`): plain assignments, premise shapes 4 and 5, a link inside a
  value, `Bearer` with a short token (in a value and after a Bearer token), `x_key=`, four no-value names, five short values, the
  ten planted classes. Every expected output was pasted from a run of the PIN's scrub (`ctl_outputs.py`, `all_outputs.py`).
- `test_value_head_check_stays_linear_on_a_long_run` (m12) and `test_chained_values_never_reach_disk` (the 20 shapes, one turn
  each, through the real CLI).

RED at the PIN — scratch tree = `git show 9801fb5:scripts/transcript_export.py` (blob a47e0e5) + the final T (sha256
efb6cd6016181f0a, identical to the shared tree's), 2026-09-23 16:03:15Z:

```
21 failed, 51 passed in 1.15s   rc=1
RED test_a_value_stops_before_the_next_secret_name[passwd=aAP... :: AssertionError: a chained value survived: 'passwd=<redacted> : X4Z92Q0X1ZX02Z71'
RED test_a_value_stops_before_the_next_secret_name[token='_AP... :: AssertionError: a chained value survived: "token='<redacted> = 6Z4Z02ZX6Z4Z"
RED test_a_value_stops_before_the_next_secret_name[password='... :: AssertionError: a chained value survived: "password='<redacted> 62669Q3JJ88ZX5466"
RED test_a_value_stops_before_the_next_secret_name[api_key=QZ... :: AssertionError: a chained value survived: 'api_key=<redacted> X4Z92Q0X1ZX02Z71'
RED test_a_value_stops_before_the_next_secret_name[password=Q... :: AssertionError: a chained value survived: 'password=<redacted> = X4Z92Q0X1ZX02Z71'
RED test_a_value_stops_before_the_next_secret_name[secret: QZ... :: AssertionError: a chained value survived: 'secret: <redacted>": "X4Z92Q0X1ZX02Z71"'
RED test_a_value_stops_before_the_next_secret_name[TOKEN=QZJ8... :: AssertionError: a chained value survived: "TOKEN=<redacted>'X4Z92Q0X1ZX02Z71'"
RED test_a_value_stops_before_the_next_secret_name[passwd=qzj... :: AssertionError: a chained value survived: 'passwd=<redacted> : x4z92q0x1zx02z71'
RED test_a_value_stops_before_the_next_secret_name[password=Q... :: AssertionError: a chained value survived: 'password=<redacted> : X4Z92Q0X1ZX02Z71'
RED test_a_value_stops_before_the_next_secret_name[password=Q... :: AssertionError: a chained value survived: 'password=<redacted> X4Z92Q0X1ZX02Z71'
RED test_a_value_cut_by_a_head_is_redacted_at_any_length[pass... :: AssertionError: the second name did not stay a name: 'passwd=<redacted>'
RED test_a_value_cut_by_a_head_is_redacted_at_any_length[pass... :: AssertionError: the second name did not stay a name: 'passwd=<redacted>'
RED test_a_value_cut_by_a_head_is_redacted_at_any_length[toke... :: AssertionError: the second name did not stay a name: 'token=<redacted>'
RED test_a_value_cut_by_a_head_is_redacted_at_any_length[DB_P... :: AssertionError: the second name did not stay a name: 'DB_PASSWORD=<redacted>'
RED test_a_match_leaves_a_later_rule_its_whole_match[passwd=Q... :: AssertionError: a later rule's secret survived: "passwd=<redacted>'QZJ8QZJ8/Bearer <redacted>"
RED test_a_match_leaves_a_later_rule_its_whole_match[token=QZ... :: AssertionError: a later rule's secret survived: 'token=<redacted> X4Z92Q0X1ZX02Z71'
RED test_a_match_leaves_a_later_rule_its_whole_match[passwd=Q... :: AssertionError: the output moved: 'passwd=<redacted> https://<bridge-link-redacted>'
RED test_a_match_leaves_a_later_rule_its_whole_match[api_key=... :: AssertionError: a later rule's secret survived: 'api_key=<redacted>&s=X4Z92Q0X1ZX02Z71'
RED test_a_match_leaves_a_later_rule_its_whole_match[Authoriz... :: AssertionError: a later rule's secret survived: 'Authorization: Bearer <redacted> X4Z92Q0X1ZX02Z71'
RED test_a_match_leaves_a_later_rule_its_whole_match[Bearer Q... :: AssertionError: a later rule's secret survived: 'Bearer <redacted>://qz-jf.trycloudflare.com/X4Z92Q0X1ZX02Z71'
RED test_chained_values_never_reach_disk                         :: AssertionError: a chained value reached disk: X4Z9…
{'passed': 51, 'failed': 21}
```

Each red is for its stated reason: 10 `CHAINED` shapes leak a value; the 4 `IN_RUN` shapes do not leak at the PIN but swallow the
second name (they exist to kill m5/m6/m9); 5 of 6 `LATER_RULES` shapes leak at the PIN. The sixth (a swallowed head before a link) does not
leak at the PIN, but its output moves; under m8 it leaks (§6). The CLI test puts a value on disk. All 27 negative controls,
the old 23 tests and the new linear test pass at the PIN (51 = 23 + 27 + 1).

GREEN after — shared tree, S blob 515d78b3ce557854eb62a1245f5a501fa0325957, 16:03:15Z:

```
72 passed in 1.15s   rc=0                                     (T + P's file; P contributes 0 pytest tests, D1)
test_hermes_session_export: 15 checks passed   rc=0          (P's real gate)
test_qwen_matrix: 4 tests passed   rc=0                      (adjacent consumer, D2)
```

## 4. Differential (contract item 3): PIN S vs new S — NO new exposure measured

Harness (scratchpad `diffcore.py`, `diff_ab.py`; prints counts only). Two instruments per input:
- Instrument 1: exact origin tracker — replays each version's `SECRET_PATTERNS` in order, maps every output character to its
  input index; templates by group span, the new callable black-box (its return value split on `<redacted>`, kept segments
  located in the match; lazy and greedy alignment must agree, else counted `ambiguous`); the rebuilt output must equal
  `scrub()` (asserted on every input).
- Instrument 2: digit flip, black-box — a digit→digit swap preserves every class in both versions (no pattern holds a digit
  literal), so a digit is redacted iff flipping it leaves `scrub()`'s output unchanged. Run on every differing input, and on
  every 50th input whatever it does (instrument 1 cross-check).
- Allowance (independent regex): a byte the PIN redacts and the new scrub shows must lie in a SHORTEST-form head (secret word or
  bare `_key`/`-key`, quote, whitespace, `:`/`=`) or be the `Bearer` keyword handed to its rule. Anything else = violation.
- Planted-secret oracle (b only): fake values from `QZJFLMV0-9` (no name can be spelled from it), counted only when placed right
  after a valid assignment start (independent `G1_END` regex; 30,300 placements after `:''` or `:='` were skipped — neither
  version reads those as assignments, both leak them: a pre-existing gap, adjacent defect A3).

(a) every planted string in T — AST string literals + module constants + the composites the tests build (259 inputs), 16:03:25Z:
```
(a) T strings: inputs=259 same=223 differ=36 violations=0 flip_viol=0 flip_disagree=0 revealed_head_bytes=234 revealed_bearer_keyword_bytes=12 over_redacted_bytes=386 ambiguous=0
```
(b) generator, seed 198, 100,000 inputs (names in both cases incl. glued/compound forms, 26 separators incl. quotes and
whitespace, quotes, 5 value alphabets, chained assignments up to depth 5, joiners incl. `&,;` and nothing, plus sk/Bearer/gh/
AIza/xox/bridge-link/opaque/key-block/Basic extras), 16:03:25Z–16:09:00Z:
```
(b) generator seed=198: inputs=100000 same=22318 differ=77682 violations=0 flip_viol=0 flip_disagree=0 revealed_head_bytes=1528778 revealed_bearer_keyword_bytes=3558 over_redacted_bytes=1768908 ambiguous=0 tracker_vs_flip_disagree_on_2pct_sample=0 (334s)
(b) planted fake secrets after a valid assignment start: 176838 (skipped, no valid start: 30300); inputs where a planted byte outside any HEAD shows: old=45331 (915869 bytes) new=0 (0 bytes); planted bytes inside a HEAD shown by the new scrub (R-1): 0
```
Harness negative controls (the harness can see what it claims to exclude):
```
vs m1  (PIN value group), 5,000:  planted: old=2264 new=2264 inputs            (the AF-AP-157 leak class is visible)
vs m5  (floor on cut value), 5,000: violations=13753 flip_viol=1669
vs m7  (X1 off), 5,000:            violations=261 flip_viol=137
vs m9  (X4 off), 5,000:            violations=15339 flip_viol=3652; planted new=417 inputs (6239 bytes)
vs m10 (X2 off), 5,000:            violations=0  (the class is rare) -> 100,000: violations=140 flip_viol=18 (16:14:55Z-16:20:39Z)
```
State history for the same harness: State A 2,000 inputs → 65 violation bytes; State B 100,000 → 134; State C 100,000 → 0.

(c) real transcripts: §7 (FIRST RESULT: no old-scrubber digest line holds a value the new scrub redacts).

## 5. Order and cost (contract item 4)

Order: unchanged (§2.1). Changed patterns: `SECRET_PATTERNS[1]` (credential) and `SECRET_PATTERNS[2]` (Bearer). Best of 5,
`time.perf_counter`, ms at 16k / 32k / 64k / 128k characters | ratio per doubling (State C, 16:09:31Z; `timing2.py`):

```
== new SECRET_PATTERNS[1] credential (the entry alone)
C1 'password=' + 'a' run                                  8.79     18.25     36.45     73.19 |  2.08  2.00  2.01
C2 'password=' + '_key' run                               8.79     18.08     35.59     73.66 |  2.06  1.97  2.07
C3 'blob ' + 'Ab1' run (the old test)                     2.31      4.60      9.22     18.47 |  1.99  2.00  2.00
C4 'password=QZJ8api_key' + spaces + 'x'                  3.17      6.16     12.34     23.15 |  1.94  2.00  1.88
C5 'password=' + '-a' run                                 8.54     17.30     35.06     72.32 |  2.03  2.03  2.06
C6 'password=' + 'x_api_key=' run                         3.13      6.27     12.63     25.69 |  2.00  2.01  2.04
C7 'password=' + 'token=' run                             0.99      2.00      4.04      8.15 |  2.02  2.02  2.02
C8 'passwd=' + 'QZJ8.api_key : ' run                      4.53      9.06     18.38     36.96 |  2.00  2.03  2.01
C9 'password=' + 'a' run + '_key=x'                       8.38     16.87     34.12     72.27 |  2.01  2.02  2.12
C10 ('api_key' + 1000 spaces) run                         2.73      5.77     11.56     24.22 |  2.11  2.00  2.09
C11 'password=' + link run                                8.00     16.46     31.68     65.30 |  2.06  1.92  2.06
C12 'password=' + link+'&' run                            7.70     15.67     31.27     64.83 |  2.03  2.00  2.07
C13 'password=QZJ8Bearer' + spaces + 'x'                  2.74      5.43     10.73     21.55 |  1.98  1.98  2.01
C14 'password=' + 'https' run                             8.60     17.43     35.75     72.68 |  2.03  2.05  2.03
C15 'password=' + 'QZJ8/Bearer X4Z9X4Z9 ' run             2.42      4.89      9.76     19.36 |  2.02  2.00  1.98
== new SECRET_PATTERNS[2] Bearer (the entry alone)
B1 'Bearer ' + 'A' run                                    0.72      1.44      2.97      6.00 |  1.99  2.06  2.02
B2 'Bearer ' + 'xBearer ' run                             1.19      2.41      4.82      9.82 |  2.02  2.00  2.04
B3 'Bearer ' + 'https' run                                0.89      1.82      3.68      7.43 |  2.06  2.02  2.02
B4 'Bearer ' + 'Bearer' run (no spaces)                   0.82      1.63      3.45      6.69 |  1.99  2.11  1.94
B5 'Bearer ABCDEFGHBearer' + spaces + 'x'                 0.30      0.56      1.12      2.29 |  1.89  2.00  2.04
B6 'Bearer ' + 'h' run                                    0.76      1.57      3.18      6.32 |  2.06  2.02  1.99
B7 ('Bearer QZJ8QZJ8https://a.trycloudflare.com/ ') run   0.47      0.95      1.91      3.82 |  2.05  2.00  2.00
```
The whole-scrub rows for the same families are linear too (all ratios 1.43–2.81 per step; the one irregular row, C14 2.81/1.43,
re-measured three times at 16:09Z: `1.97 2.10 2.06`, `2.03 2.07 2.03`, `2.02 2.05 2.04`; 75.36 ms at 128k). Nothing grows faster
than linear. Cost vs the PIN (same families, 16:10:01Z): the credential entry is a CONSTANT factor slower on long value runs
(C1 1.24 ms → 73.19 ms at 128k; the per-character head/Bearer/link check), equal on no-value text (C3 18.59 → 18.47); the
Bearer entry B1 0.22 → 6.00 ms. The quadratic design that was rejected: State B's conditional link stop, `password=` + 500 / 1000 /
2000 / 4000 links: 193.8 / 661.8 / 2645.3 / 11670.2 ms (x4 per doubling).

## 6. Mutants (contract item 6) — each on a scratch copy (`mutants.py`, edits asserted to apply exactly once), final T

| mutant | edit | red count | named test(s) red for the stated reason (verbatim message head) |
|--------|------|-----------|---------------------------------------------------------------|
| m1 | the PIN's value group back | 19 failed, 53 passed | `test_a_value_stops_before_the_next_secret_name[passwd=aAPI_KEY : X4...]` :: `a chained value survived: 'passwd=<redacted> : X4Z92Q0X1ZX02Z71'` (all 10 CHAINED) |
| m2 | head check `=` only (no `:`) | 10 failed, 62 passed | `...[passwd=aAPI_KEY : X4...]` :: `a chained value survived`; `...[password='-db_passwo...]` :: `a chained value survived: "password='<redacted> 62669Q3JJ88ZX5466"` |
| m3 | head check case-sensitive | 7 failed, 65 passed | `...[passwd=aAPI_KEY : X4...]`, `...[token='_API_KEY = 6Z...]`, `...[password=QZJ8QZJ8QZJ...]` (`_TOKEN =`) :: `a chained value survived` |
| m4 | quote dropped from the head | 2 failed, 70 passed | `...[secret: QZJ8QZJ8.api...]` :: `a chained value survived: 'secret: <redacted>": "X4Z92Q0X1ZX02Z71"'` |
| m5 | floor applied to the head-cut value | 5 failed, 67 passed | `test_a_value_cut_by_a_head_is_redacted_at_any_length[passwd=QZJ8Q_a...]` :: `a value inside the run survived: 'passwd=QZJ8Q_api_key=<redacted>'` |
| m6 | no in-run head (each head's value gets its own floor) | 2 failed, 70 passed | `...[passwd=QZJ8QZJ...]` :: `a value inside the run survived: 'passwd=<redacted>API_KEY=X4Z9X4Z'` |
| m7 | X1 off (value eats `Bearer`) | 3 failed, 69 passed | `test_a_match_leaves_a_later_rule_its_whole_match[token=QZJ8:Bearer ...]` :: `a later rule's secret survived: 'token=<redacted> X4Z92Q0X1ZX02Z71'` |
| m8 | X3 off (link = plain value text) | 3 failed, 69 passed | `...[api_key=https://qz...]` :: `a later rule's secret survived: 'api_key=<redacted>&s=X4Z92Q0X1ZX02Z71'` |
| m9 | X4 off (compound name in the head check) | 4 failed, 68 passed | `...[password=QZJ8QZJ8my_...]` :: `a chained value survived: 'password=QZJ8QZJ8my_key: <redacted>'`; `...[DB_PASSWORD=QZ...]` :: `a value inside the run survived: 'DB_PASSWORD=QZJ8QZ12REDIS_KEY=<redacted>'` |
| m10 | X2 off (the PIN's Bearer rule) | 3 failed, 69 passed | `...[Authorization: Bea...]` :: `a later rule's secret survived: 'Authorization: Bearer <redacted> X4Z92Q0X1ZX02Z71'`; `...[Bearer QZJ8QZJ8QZJ...]` :: `... 'Bearer <redacted>://qz-jf.trycloudflare.com/X4Z92Q0...'` |
| m11 | no bare `_key`/`-key` start | 2 failed, 70 passed | `...[password=QZJ8QZJ8my_...]` :: `a chained value survived: 'password=<redacted>_key: X4Z92Q0X1ZX02Z71'` |
| m12 | unanchored compound name in the head check | 5 failed, 67 passed in 42.52s | `test_value_head_check_stays_linear_on_a_long_run` :: `the value's head check is not linear on a long run` (the old `test_compound_key_rule_stays_linear_on_a_long_run` stays GREEN under m12) |
| m13 | the floor removed | 6 failed, 66 passed | `test_negative_controls_keep_their_pin_output[sort_key: name-...]` :: `assert 'sort_key: <redacted>' == 'sort_key: name'` (+4 controls, + `test_prose_beside_a_key_name_survives`) |

Run 16:12:11Z–16:13:21Z. m5's brief wording "(if your rule exempts it)": the rule does exempt it; m5 is killed.

## 7. Differential (c): the real session transcript — counts and locators only, never text

FIRST (the brief asks for this first): **NO old-scrubber output line holds a value the new scrub redacts. 0 runs in 0 turns.**
No credential rotation is indicated by this class, for this transcript or the digests committed from it.

Input: `/root/.claude/projects/-home-user/*.jsonl` matches ONE file (this session, 535,503,794 bytes at 16:24:26Z, still
growing). With 1.1 GB free on `/` a raw copy was unsafe for the other live lanes. So `diff_c.py` (scratchpad) fixed a
newline-aligned byte range and wrote a reduced snapshot (user/assistant lines, text blocks only, mode 0600, 10,607,913 bytes).
It then proved the snapshot exact under the PIN's own `turns()`: byte range → 5260 turns sha=2fa2d6aab4390def; snapshot → 5260
turns sha=2fa2d6aab4390def; EQUAL. It then ran the two real CLIs on it: `python3 <PIN copy of transcript_export.py> --transcript
<snapshot> --out <scratch>/old` and the same with the shared tree's S into `<scratch>/new`.

```
live size=535503794 range=[0,535503794) bytes
snapshot: 46193 user/assistant lines kept, 10607913 bytes, mode 0o600
PIN turns(): byte range -> 5260 turns sha=2fa2d6aab4390def; snapshot -> 5260 turns sha=2fa2d6aab4390def; EQUAL
CLI old: rc=0 files=16
CLI new: rc=0 files=16
digest files: old=16 new=16 same names=True
digest lines (old): 32472; differing lines: 0
layout replica == real CLI output for every day and both versions: True
numbered replica == turns(): True
turns=5260 differing turns=1 violations: 0 bytes in 0 turns; revealed shortest-form head bytes=7; revealed Bearer keyword bytes=0; newly redacted bytes=0; ambiguous alignments=0
NEWLY REDACTED BYTES THAT THE OLD DIGEST SHOWED: 0 runs in 0 turns
committed digest lines searched: 181027
first differing digest lines: []
```

Readout: the two exporters write byte-identical digests (0 of 32,472 lines differ). Exactly one turn scrubs differently before
the 4,000-character cap. The difference lies past the cap, so it never reaches a digest: 7 bytes of one shortest-form head
become visible, and no byte is newly hidden or newly shown outside a head. A re-run at 16:26Z (535,851,205 bytes, 5,262 turns)
gave the same counts.

Link to what is on origin: 15 of the 16 committed `transcripts/sandbox/chat-*.md` files are byte-identical to the PIN's fresh
digest of the same day. The 16th, `chat-2026-09-23.md`, differs only in line 1, the header's turn count (953 committed vs 1066
now; last committed at fa4532e 2026-09-23T14:34:07+00:00), plus the turns added since. So the 0-run result covers the committed
sandbox digests.

EXTRA check (not in the brief), with its blind spot stated: re-scrubbing all 121 committed digest files (`transcripts/sandbox`
and `transcripts/pc`, 181,027 lines) gives: the PIN changes 0 lines; PIN and new outputs differ on 0 lines; the new scrub hides
bytes the PIN leaves visible in 0 lines. BLIND SPOT: re-scrubbing scrubbed text cannot see this very class, because the swallowed
name is already gone (`passwd=<redacted> : X4Z9...`). So for `transcripts/pc/` (P's PC lane exports, 105 files, whose raw
sources are PC Hermes state.db sessions not in this glob), the AF-AP-157 question is NOT answered here. Answering it needs the PC
state.db sessions run through P at both versions: NOT done (the bridge is out of this lane's scope).

Cleanup: the snapshot, both digest trees and the locator file were deleted (`c_work` removed at 16:25:38Z and again at
16:26:09Z after the re-run). The old-scrubber digests could hold a leaked credential, so none were kept.

## 8. Gates (contract item 7) — final blob, 16:28:19Z–16:28:25Z

```
AST identical (515d78b vs final; comments are not in the AST): True
comment example: 'passwd=<redacted>_key: v' | no-value head: 'password=<redacted>token=&x'
37d94bd615568fdbac6dd69a2e95df56a4448674      (scripts/transcript_export.py)
12dbaae6d0da1e21381d3c104edaad73d2a2d938      (tests/test_transcript_export.py)
python -m pytest -q -p no:cacheprovider tests/test_transcript_export.py harness-ports/tests/test_hermes_session_export.py
72 passed in 1.07s   rc=0
72 passed in 1.06s   rc=0
bash scripts/pc_suite.sh set-id -- tests/test_transcript_export.py harness-ports/tests/test_hermes_session_export.py
2 files set=4e81d5d61609
bash scripts/test_summary.sh tests/test_transcript_export.py harness-ports/tests/test_hermes_session_export.py
pytest-exit: 0
pytest-summary: 72 passed in 1.12s
python3 harness-ports/tests/test_hermes_session_export.py        (P's real gate, D1; twice)
test_hermes_session_export: 15 checks passed   rc=0
test_hermes_session_export: 15 checks passed   rc=0
python3 harness-ports/tests/test_qwen_matrix.py                  (adjacent consumer, D2)
test_qwen_matrix: 4 tests passed   rc=0
python3 scripts/lint_delta.py --base HEAD
lint_delta (worktree vs HEAD): 2 .py changed, 0 NEW pyflakes hit(s), 0 removed   rc=0
python3 scripts/lint_delta.py --base 9801fb5 --no-ap
lint_delta (worktree vs 9801fb5): 12 .py changed, 0 NEW pyflakes hit(s), 0 removed   rc=0
python3 -m pyflakes scripts/transcript_export.py tests/test_transcript_export.py   rc=0
python3 scripts/ap_screen.py scripts/transcript_export.py          --- AP_SCREEN over 1 path(s): 0 hits over 1 files ---
python3 scripts/ap_screen.py --tests tests/test_transcript_export.py   --- TEST_SCREEN over 1 path(s): 0 hits over 1 files ---
```

The brief wrote the lint gate as `python3 scripts/lint_delta.py`. Bare, it refuses:
`lint_delta.py: error: one of the arguments --staged --base is required` (rc 2). `--staged` is vacuous here, because nothing is
staged by lane rule. So I ran `--base HEAD` (this lane's two files) and `--base 9801fb5` (the PIN; its 12 files include the
J1-1-R2 and B11/B12 commits that landed after the PIN). Its advisory screen at 16:27:07Z printed 4 tells, all in other lanes'
files (`tests/test_decisions_canonical.py` AF-AP-39, `tests/test_edit_snapshot_ap_screen.py` AF-AP-159,
`tests/test_s0_02_buzz_authz.py` AP-32/AP-51). None was in this lane's files.

The shared tree moved during the lane: HEAD went 87b708d → 0e60603 (B12 landed as 321bcee, plus J1-3 and T94 briefs and
ledger commits). `git log 87b708d..HEAD` touches none of S, T, P, P's test, `qwen_matrix.py` or its test (0 commits). The HEAD
blobs of S/T/P/P-test are still the PIN's (a47e0e5, 8d1723b, 04326ec, 0d7893b). This lane's working-tree diff is 2 files,
200 insertions(+), 4 deletions(-), measured before the comment fix.

## 9. Self-attack — the three likeliest ways this change is wrong

1. The differential's allowance excuses real secret bytes. This already happened once, in State B: the compound "head" hid
   119,859 planted bytes. Ruled out now, measured, not argued: the allowance is the SHORTEST-form head (independent regex), and
   the planted-secret oracle counts shown planted bytes separately (R-1: 0; new leaks: 0 of 176,838). What remains is stated
   as R-1 (§2.2): a secret that itself contains `word:`/`word=` shows those bytes.
2. The generator misses a real shape where the new rule shows bytes. Partly ruled out. Three independent sources give 0
   violations: T's 259 strings, 100,000 generated inputs (checked by two instruments; tracker vs digit-flip disagreement 0 on
   the 2% sample and on every differing input), and 5,262 real turns. Sensitivity was shown by mutants: the harness catches
   m5/m7/m9 at 5,000 inputs and m10 only at 100,000 (140 bytes). A class rarer than m10's in both the generator and the real
   transcript would go unseen: that is the residual.
3. A super-linear input the 22 timing families miss. Ruled out by construction plus measurement. `_VALUE` is the last element
   of its pattern, so the engine never backtracks into it. Each alternative is bounded, except `\s*`/`\s+` after a word or
   `Bearer` (scanned once per run end) and the host scan (once per `https://`). The Bearer token is a tempered class with
   bounded lookaheads. Every family measures ~2.0 per doubling. The known quadratic shapes were measured on purpose: the
   rejected conditional link stop (x4 per doubling) and m12 (42.52 s tree, red on the linear test).

A fourth, specific to the implementation: `_CUT` re-tiles the isolated value, and if it disagreed with `_VALUE`, a head could be
redacted or a piece kept. Ruled out: instrument 1 aligns the callable's ACTUAL output against the match and asserts the rebuilt
output equals `scrub()` on every input (0 failures). A kept piece would appear as a violation, a redacted head as `over`. The
digit-flip instrument agrees with the tracker on every digit checked.

## 10. Adjacent defects (reported, NOT fixed; each verified at 16:3xZ with fake values, identical at the PIN and after)

- A1: `Authorization: Basic QZJ8QZJ8QZJ8QZJ8` is never redacted. The value run `Basic` is 5 characters, under the floor, and the
  credential is under the 40-character opaque rule.
- A2: the Bearer rule is case-sensitive, so `authorization: bearer X4Z9...` and `token=QZJ8:bearer X4Z9...` show the token.
- A3: AF-AP-157 between the provider rules and the bridge-link rule: `https://xoxb-qzjfqzjfqz.trycloudflare.com/exec?t=X4Z9...`
  → `https://xox-<redacted>.trycloudflare.com/exec?t=X4Z9...`. The xox rule ate the host's start, so the link rule no longer
  matches and the tail shows. Hosts like this are unlikely (trycloudflare names are random words), but the class is real.
- A4: `api_key:''X4Z9...` and `SECRET:='X4Z9...'` are not read as assignments. The generator placed 30,300 such values, and
  neither version redacted them.
- A5 (D1): `harness-ports/tests/test_hermes_session_export.py` holds no pytest test, so a pytest-only gate over it is vacuous.
  Its gate is its script (`run-all.sh`).
- A6 (D2): `harness-ports/bin/qwen_matrix.py:126-137` is a third reader of S; the brief does not name it.
- A7: `python3 scripts/lint_delta.py` needs `--staged` or `--base`. A brief that writes it bare has an rc-2 gate.
- A8: for increment B (`src/agent_factory/decisions/volatile.py`): this lane's differential showed that "stop before a head"
  alone creates new exposures through later classes (Bearer, bridge links) and through compound-name absorption of a glued
  value. Increment B should run the same kind of differential (its `_YIELD` chain guard is the other half of the class).
- A9: suggested registry echo (the coordinator's file, outside this boundary): the AF-AP-157 row could name four sub-shapes
  measured here: a value eats a later rule's keyword (Bearer); a value ends inside a later rule's match (link at `&`); a
  prefix class eats the next keyword (Bearer→Bearer, Bearer→`https`, xox→link host); a compound name absorbs a glued value.

## 11. NOT done (first-class)

- NOT committed, NOT pushed (lane rule: the coordinator commits through `safe_commit.sh`). Files for the commit: the two
  boundary files and this report.
- NOT done: the AF-AP-157 exposure question for `transcripts/pc/` (105 committed PC lane exports written by P). Their raw
  sources are PC Hermes state.db sessions, not the brief's glob, and re-scrubbing scrubbed text is blind to this class (§7).
  It needs those sessions run through P at both versions on the PC.
- NOT done: `volatile.py` (increment B, out of scope).
- NOT done: the registry, ledger, wiki and task-DB updates (the coordinator's files).
- Tooling limits: GitNexus `impact` was unavailable (`LadybugDB ... checkpoint is in progress`, risk UNKNOWN), so the blast radius
  is crg `callers_of` plus a literal sweep (§1). The brief's bare `lint_delta.py` form errors; see §8.
- Scratch left in the session scratchpad (fakes only, no transcript text): `pin_transcript_export.py`, `S_515d78b.py`, `red_tree/`,
  `mut/m1..m13/`, and the harness scripts (`diffcore.py`, `diff_ab.py`, `diff_c.py`, `committed_check.py`, `mutants.py`,
  `timing2.py`). The real-transcript snapshot and both digest trees were deleted.
