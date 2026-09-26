# VERIFY-SCRUB2 report (task #303): the scrubber hardening (SCRUB2, task #292)

Lane: adversarial-verifier (sandbox, Opus 5.5). Started 2026-09-26 (bucket 01:4xZ). Written incrementally.
Target: cdbc1b8 ("SCRUB2 landed (task #292 ...", origin tip). Local HEAD at start 981a130 (the brief's commit, one ahead of
origin, touching no target file). Contract: `tasks/briefs/system1/SCRUB2-brief.md` items 1-8, the lane's report
`tasks/briefs/system1/SCRUB2-report.md`, VERIFY-SCRUB1's findings F1-F3, F8-F10, F12-F14, F17, AF-AP-224.
Scratch: `<scratch>/vscrub2/` (`<scratch>` = `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad`).

## STATUS

**NOT-READY: blockers F1, F7, F15** (section 15; the finding inventory is section 14). No recommendation rests on an
unreproduced claim.

The lane was stopped at 03:33:29Z and resumed by a fresh agent at 05:02:41Z (`date -u`). The coordinator reports a
container restart at about 05:40Z; the work continued from this report and the scratch (re-checked at 05:42:52Z: the
target unchanged, the scratch intact, no process of this lane left).

## 1. PREMISE, re-measured (01:4xZ)

| # | Premise line | Measured now | Verdict |
|---|---|---|---|
| P1 | `git log -1 HEAD` = cdbc1b8 "SCRUB2 landed (task #292 ..." | cdbc1b8 is origin's tip and has that subject; local HEAD moved on to 4af2284 (981a130 the brief, b631f9a live-state, 4af2284 the retro that registered #304/#305). `git diff cdbc1b8 HEAD` on every target file and both manifests: empty; the working tree leaves them unmodified | holds |
| P2 | `git show --stat` of cdbc1b8: 11 files, 995+/58- | identical | holds |
| P3 | the grep of `_KEY_L`, `_KEY_R`, the two PEM markers, cookie, authorization, pwd, credentials, the opaque rule, 148, 160, 179, 203 | identical line numbers and text | holds |
| P4 | `def known_values` 286, `def export` 335, `def main` 358; `ENV_NAME` 35, `NotRegularFile` 38, `_read_regular` 42, `main` 119 | identical | holds |
| P5 | `len(gate_patterns()), len(PATTERN_NAMES)` = 23 23 | `23 23` | holds |
| P6 | the PIN of SCRUB2 (4b3b699) = the landing's parent for the target files | `git diff --stat 4b3b699 cdbc1b8^` over the seven target files and the manifests: empty | holds |

sha256 prefixes of the target bytes: exporter 6ad316dccfca0147 (the lane's), `known_values_check.py` cfdf2ffec10e6d10,
test file 5b22cc0040767dc7; the PIN exporter 2136062e0af69815. Copies: `<scratch>/vscrub2/t` = `git archive cdbc1b8
scripts tests pyproject.toml`, `<scratch>/vscrub2/pin` = the same at 4b3b699 (5.5 MB each).
Verdict: the premise holds. No CONTRACT-INVALID.

## 2. Fresh gates on the two changed test files (02:0xZ)

Inside VERIFY-SCRUB1's `masked.sh` (a private mount namespace: the real sources unreachable; guard booleans all True):
```
$ masked.sh absent <scratch>/vscrub2/t -- bash scripts/test_summary.sh tests/test_transcript_export.py tests/test_known_values_check.py --basetemp=...   (twice)
pytest-summary: 207 passed in 2.22s
pytest-summary: 207 passed in 2.11s
$ masked.sh fakes  ... (twice)
pytest-summary: 207 passed in 2.02s
pytest-summary: 207 passed in 2.03s
2 files set=f3473b81d07d
```
Reproduced: the lane's 207 and its set id.

## 3. Attack item 5 first: no committed test opens a real source (02:0xZ)

Own instrument, not the lane's: `<scratch>/vscrub2/trace.sh` runs pytest under `strace -f -qq -e trace=%file` (every syscall
naming a file, every process) with my own `sitecustomize` (`<scratch>/vscrub2/envlog/`) that logs each `os.environ` lookup of
`GH_TOKEN`/`GITHUB_TOKEN` (names and caller lines only), inside `masked.sh`:
```
(a) target tests + scripts, absent venue:  207 passed in 4.42s
    <copy>/.pc-bridge.env 0 syscalls | tree .pc-bridge.env 0 | /root/.codiv/api.env 0 | pseudonym.key 0 | any /root/.config/qwen 0 | token lookups 0
(b) target, fakes venue:                   207 passed in 4.64s
    <copy>/.pc-bridge.env 1 syscall, 0 opens (pytest's rootdir walk: newfstatat, plus two ENOTDIR probes of <entry>/pyvenv.cfg
    and <entry>/conda-meta/history) | every other source 0 | token lookups 0
(c) NEGATIVE CONTROL, the PIN's tests + scripts (4b3b699), fakes venue: 184 passed in 6.57s
    <copy>/.pc-bridge.env 61 syscalls (30 opens) | api.env 60 (30) | pseudonym.key 60 (30) | token lookups 94:
    30+30 transcript_export.py:264, 15+15 test_known_values_check.py:22, 1+1 test_transcript_export.py:855, 1+1 :861
```
Reproduced exactly (the lane's section 6: 0/0 in both venues against 61/30, 60/30, 60/30 and 94 lookups on the PIN). The
instrument is not blind: the control shows every open. Set A under the same trace: section 8.
(Note by the resumed lane, 2026-09-26 05:5xZ: set A under the trace is section 10, not 8.)

**Other reach paths (static, then checked):** the test file's only CLI child (`test_transcript_export.py:374`) names a missing
transcript, so `main()` returns 3 before `export()`; the `CHILD` of `_export_in_a_child` calls `export()` with fixture sources;
`test_push_clean_lock.py` writes a FAKE exporter into its throwaway repo (`:176`) and runs push_clean with `TRANSCRIPT_SYNC=0`
elsewhere; no other file in `tests/` or `harness-ports/tests/` calls `main()` or `export()` (grep). The autouse tripwire
guards `MOD` of this one file only: a future test elsewhere that runs the real CLI would reach the real sources (INFO, F13).

## 4. Attack item 1: the anchors, hostile shapes both ways (02:0xZ)

`<scratch>/vscrub2/anchors.py`: 8 fake key families built at run time (sk 19 and 51, sk-proj with `_` and `-`, gho 26, ghp 40,
AIza 39, xoxp 17, xoxb 56); 51 left contexts (ASCII punctuation, `_`, `__`, a letter, a digit, 7 non-ASCII letters and digits,
every raw JSON escape `\n \t \r \b \f \" \\ \/`, `\u00e9`, `\u0022`, `\u000a`, `\uABCD`, an escaped backslash before `n`
and before `u00e9`, ANSI `\x1b[31m`, `\x1b[0m`, `\x1b[m`, their raw `\u001b[31m`, a real newline and tab, NBSP, ZWSP, a
combining mark, URL path and query, backtick, paren, angle, `@`) and 28 right contexts; each through the target's and the PIN's
`scrub`, `scrub_payload`, `scrub_strict`. LEAK = an 8-character window of the key's secret part survives.
```
scrub          cases=600  leaks: target 18, PIN 105  newly caught 87  newly missed 0
scrub_payload  cases=600  leaks: target 18, PIN 105  newly caught 87  newly missed 0
scrub_strict   cases=600  leaks: target 3,  PIN 21   newly caught 18  newly missed 0
target leaks, all SHORT keys (sk 19, gho 26, xoxp 17; every real-length key is taken in every context):
  L letter, L digit (by design, SCRUB1's M16), L ansi \x1b[31m / \x1b[0m / \x1b[m and raw \u001b[31m (glued to the letter `m`)
```
Every right context is taken now (non-ASCII letters, `_`, `__`, quotes, the escape after the key, ANSI after it); the xoxb
+ `_` tail (F2) is whole. The escaped-backslash contexts (`\\n` + key) are taken too: a key glued to a literal `n` after an
escaped backslash reads as separated (over-redaction only).

**End to end** (`<scratch>/vscrub2/e2e.py`, a fixture transcript in the real record shapes: user str, user and assistant
text blocks, thinking, a tool_use input, a tool result; one fresh fake key per record; 17 contexts x 8 families x 6 kinds;
the target's and the PIN's `export(..., sources=())` and `session_export.convert()` with a fake key, events read as text
and as JSON lines both ways): the target leaks only `after a letter` and `after ESC[31m` (the short families), in both
writers; the PIN leaked also `line start`, `after a tab`, `after \x01` (the tool_use input's canonical JSON: F3),
`before é`, `before です`, `after é`/`after です` (48-char opaque), `before _` (gh, xox), `literal \n` and `literal
\u00e9`. **export/convert: target leaks the PIN did not: none.** The target's chat_find (`--excerpt --json`) and hiccup_scan
CLIs over the same fixture: 0 leaks, but NOT discriminating: both normalize every 20+ run to `T` after the scrub
(`hiccup_scan.py:83`), so they hide the letter-glued keys the scrub leaves too; their scrub call is `scrub`/`scrub_payload`
on DECODED strings, which the rule grid covers. The raw-JSON writers are session_export's canonical text (reproduced) and
hermes-session-export/qwen_matrix (PC, not run).

**The LOST direction** (`<scratch>/vscrub2/lost.py`: the same grid with 6-letter markers glued on each side, 31,104 texts x
3 functions): 0 texts where a piece of the KEY the PIN hid shows. Non-secret text the PIN hid that the target shows (each
the key's neighbour, hidden by the PIN only because the opaque rule took the key's whole glued run): (a) a raw JSON escape's
letter or hex digits before a key (`\n`, `\t`, `\r`, `\b`, `\f`, `\uXXXX`: the lane's 8 raw-view regions; the target keeps
the escape whole); (b) text glued to a gh or xox key by `_`, `__` (and by `-` after a raw escape): the lane's self-test class;
(c) in `scrub_strict` only, a NAME before `=` glued to a key followed by a non-ASCII letter (the PIN's strict key run took
`NAME=KEY` whole; the target's provider rule takes the key first). None is part of a key. Item 6's literal "no redaction
the PIN makes may be lost" is not met by (a)-(c); the lane disclosed (a) and (b) (F6, INFO).

**Section 4, continued by the resumed lane (05:1xZ): the corpus re-measurement of the lane's section 3 table.** Instrument:
the first verifier's `<scratch>/vscrub2/measure_v2.py` (read in full before use). Each candidate is the PIN's rule list with
ONE rule inserted from source text (a landed rule, or a rejected form), or the landed file itself (LANDED); a text counts
when the candidate's `scrub` output differs from the PIN's. That is the FIRST number of each cell of SCRUB2-report.md
section 3 (texts changed); this instrument does not count NEW or LOST regions.

Partition check before the re-run: `measure_v2.py sub k 6` splits a sorted live glob by `i % 6`. Since the interrupt, 5
subagent transcripts were born (`stat %W`: 03:36:58Z to 05:02:30Z), and no older one was modified after 03:18Z. So the
brief's literal `measure_v2.py sub 5 6` would split a shifted list and count some files twice and others never.
`<scratch>/vscrub2/frozen.py` keeps only files born before 03:18:00Z (the start of sub 0): 303 files, 510,683,893 bytes,
which equals the lane's LANDED subagent bytes. Its per-part texts and characters equal the head lines of m-sub-0 to m-sub-4
exactly (count mode, no scrub). Part 5 ran over that list: `python3 frozen.py sub 5 6 > m-sub-5.txt`, rc 0, 586,163 texts,
167,788,263 characters, 193 s.

Aggregate (`<scratch>/vscrub2/agg.py`). sub = m-sub-0 to m-sub-5, 3,360,914 texts. main = m-main-0 to m-main-3 (of 8)
plus m32-main-16 to m32-main-31 (of 32): lines [0, n//2) and [n//2, n) of the fixed 744,747,851-byte prefix, 4,139,221
texts. digests = the committed set read with `git show` (`digests_at.py`). root2 as it is now: 14,250 texts, which is the
lane's 519 lines plus 13,731 strings, so that corpus is unchanged.

| Candidate | digests (cdbc1b8: 18 files, 3,577,907 B) | main dec | main raw | sub dec | sub raw | root2 | lane's cells (texts) |
|---|---|---|---|---|---|---|---|
| LANDED | 1 | 23 | 24 | 45 | 33 | 0 | 1, 23, 24, 45, 33, 0 |
| N-pwd (rejected) | 0 | 14 | 7 | 5 | 4 | 0 | 0, 14, 7, 5, 4, 0 |
| PWD2 (taken) | 0 | 0 | 0 | 2 | 2 | 0 | 0, 0, 0, 2, 2, 0 |
| N-credentials (rejected) | 0 | 5 | 9 | 65 | 55 | 0 | 0, 5, 9, 65, 55, 0 |
| CRED2 (taken) | 0 | 0 | 5 | 1 | 1 | 0 | 0, 0, 5, 1, 1, 0 |
| COOKIE (taken) | 0 | 0 | 0 | 0 | 0 | 0 | 0 everywhere |
| AUTH-any (rejected) | 1 | 41 | 24 | 60 | 35 | 0 | 1, 41, 24, 60, 35, 0 |
| AUTH2 (taken) | 1 | 23 | 13 | 38 | 27 | 0 | 1, 23, 13, 38, 27, 0 |
| P3 (rejected) | 0 | 1 | 1 | 12 | 8 | 0 | 0, 1, 1, 12, 8, 0 |
| P3E (taken) | 0 | 0 | 0 | 4 | 2 | 0 | 0, 0, 0, 4, 2, 0 |

Every texts-changed cell reproduces exactly. The digests at the PIN (4b3b699: 18 files, 3,561,429 bytes) give the same
counts. The lane's "3,577,907 bytes" is the set after the e12d5f2 sync, not the PIN's (a provenance detail; the counts
agree). At HEAD (8d39d6a: 19 files) every candidate changes 0 digests: the landed exporter wrote them. Not reproduced by
this instrument: the NEW and LOST region counts (the second and third numbers of each cell). Section 5 re-checks the
REASONS behind the rejected forms.

## 5. Attack item 2: the five new shapes (resumed lane, 05:2xZ)

Instruments (scratch; every value a fake from `secrets`; labels, booleans and masked shapes printed only):
`shapes2.py` (the first verifier's, reviewed before use: 96 spellings and 42 ordinary texts through the target's and the
PIN's `scrub` and `scrub_payload`, then canonical-JSON validity), `jsonbreak.py`, `escape_named.py` (end to end: the
target's and the PIN's `export()` with `sources=()`, the digest path, and `session_export.convert()` with a fake key, the
session-export path), and over the corpus `reasons.py`, `reasons2.py`, `escape_corpus.py`, `escape_committed.py`.

**5a. The JSON-escape contexts: three new rules miss them (reproduced end to end).** One fake per cell; LEAK = 8
characters of the fake survive; target / PIN, each as digest / convert:

| Shape | line start in a tool input | after a tab | a JSON document (escaped quotes) | a pasted JSON line, literal `\n` | plain (control) |
|---|---|---|---|---|---|
| `pwd=` | hid/LEAK , LEAK/LEAK | hid/LEAK , LEAK/LEAK | hid/LEAK , LEAK/LEAK | **LEAK/LEAK** , LEAK/LEAK | hid/hid , LEAK/LEAK |
| `credentials=` | hid/LEAK , LEAK/LEAK | hid/LEAK , LEAK/LEAK | hid/LEAK , LEAK/LEAK | **LEAK/LEAK** , LEAK/LEAK | hid/hid , LEAK/LEAK |
| `Cookie: sid=` | hid/LEAK , LEAK/LEAK | hid/LEAK , LEAK/LEAK | hid/LEAK , LEAK/LEAK | **LEAK/LEAK** , LEAK/LEAK | hid/hid , LEAK/LEAK |
| `Authorization: Token` | hid/hid , LEAK/LEAK | hid/hid , LEAK/LEAK | hid/LEAK , LEAK/LEAK | hid/hid , LEAK/LEAK | hid/hid , LEAK/LEAK |
| `passphrase=` (control: `_NAME`) | hid/hid , LEAK/LEAK | hid/hid , LEAK/LEAK | hid/hid , LEAK/LEAK | hid/hid , LEAK/LEAK | hid/hid , LEAK/LEAK |
| `password=` (control: `_NAME`) | hid/hid , hid/hid | hid/hid , hid/hid | hid/hid , hid/hid | hid/hid , hid/hid | hid/hid , hid/hid |

Mechanism (read from `transcript_export.py`): canonical JSON writes a line start as `\n` and a tab as `\t`, so the
name follows the letter `n` or `t`. The Cookie rule's `\b` (line 95) and the `pwd`/`credentials` rules'
`(?<![A-Za-z0-9])` (lines 103, 105) fail there. That is VERIFY-SCRUB1 F3's class, which SCRUB2 closed for the provider
rules with `_KEY_L`'s escape lookbehinds (line 67) but did not give the new rules. In a JSON document inside a string the
quotes are `\"`: the new rules accept a bare quote only (`[\"']?`), while the older payload rules take `\\*[\"']` (lines
148, 153, 160). `password` and `passphrase` stay hidden everywhere because `_NAME` has no left anchor for them and the
payload R1 rule (line 153) covers `_NAME` in escaped quotes. The digest path (origin-bound) leaks only when chat text holds
a literal escape (a pasted JSON line, a code string such as `"user=zq\npwd=..."`). Not a regression: the PIN leaked every
cell of the new shapes. Against the contract: SCRUB2-brief.md EVIDENCE DEMANDS 3 asks for "each new rule in every context
(..., a JSON escape, ..., at a line start and end, ...) through the real functions and through export() and convert()
end to end". The lane's convert() test (`test_scrub2_shapes_never_reach_the_session_export`, lines 1255-1289) puts the
item-3 shapes in JSON members only; `_named_shapes()` (lines 1168-1198) has no escape or line-start context. Corpus
exposure (`escape_corpus.py`, `escape_committed.py`, the section 4 corpus): 4 raw `Authorization` regions in escaped
quotes and 2 raw `credentials` regions after an escape show a non-path value, and each value is committed text (a
fixture bearer value; a file name); 9 `pwd` regions show a path. So 0 uncommitted instances today. Finding F1 below.

Added 05:5xZ, the demand's "a non-ASCII letter on either side": `Cookie: sid=<fake>` right after `é` or `の` LEAKS in
both writers, the digest included (target and PIN alike): the rule's leading `\b` (line 95) does not hold between two
Unicode letters, the anchor class SCRUB2 replaced in the provider and opaque rules (VERIFY-SCRUB1 F2, F12). `pwd`, `credentials` and
`Authorization: Token` after `é`/`の`, and all four before `é`, are hidden in both writers.

**5b. `Negotiate` is a dead scheme.** `Authorization: Negotiate <token>` comes out as `Authorization: <redacted> <token>`
in `scrub` and `scrub_payload`: the credential rule (line 88, `Authorization` is in `_NAME`) runs first and takes the
9-letter scheme word as the value (its floor is 8), so AUTH2's `negotiate` alternative never fires. Every other listed
scheme is under 8 characters and is taken. The lane's report (D4) lists Negotiate as covered; no test holds it. Beyond
item 3's wording ("`Authorization: Token <v>`"). Finding F2.

**5c. Other spellings that pass** (`shapes2.py`; every one "PIN leaked too", so none is a regression): `curl -b "k=v"`,
`curl --cookie k=v`, `document.cookie = "k=v"`, `cookies={'sid': v}`, a quoted cookie value (`Cookie: sid="v"`), a
cookie with no `name=`, `Cookie2:`; `Authorization: Digest username=..., response="v"`, `AWS4-HMAC-SHA256
Credential=v/...`, `GoogleLogin auth=v`, `Authorization=Token v` (an `=`); `oldpwd=v`, `--pwd v`, `-pwd v`,
`pwd => v`, and a value starting with `/ ~ . $ \` (by design); `credentials: v` and `credentials: "v"` (the
annotation form, by design), `'credentials' = v` (a quoted name then `=`: 2 corpus regions, a separator and a path),
`credential=v`, `creds=v`; `gpg --passphrase v`, `pass_phrase=v`; a PEM with 2 dashes or a lower-case header.
Finding F3 (INFO).

**5d. Ordinary text the target now redacts** (`shapes2.py`, "new with SCRUB2" unless noted): `Authorization: Key rotation
is manual`, `Authorization: Digest authentication`, `AUTHORIZATION: Basic authentication is weak` (the lane's A4 names
this one); `pwd = os.getcwd()` (A4), `pwd = Path.cwd().resolve()`, a Windows path `pwd=C:\Users\...`;
`credentials = get_credentials()` (A4), `Client(credentials=credentials)`, `self.credentials = credentials`,
`credentials=service_account.Credentials.from_service_account_file(path)`, `credentials = self._load_credentials()`;
prose naming both 4-dash header lines, and a table with `--- BEGIN PRIVATE KEY ---` / `--- END PRIVATE KEY ---`
headings; `passphrase = getpass.getpass()`, `passphrase=os.environ["GPG_PASSPHRASE"]` (what the PIN already does for
`password`). Every cookie text and the short-word `Authorization` prose stayed (the 8-character floor). The corpus
cost of the landed rules is section 4's LANDED row, which the lane classified as fixtures and documented fakes. Finding F4.

**5e. Canonical-JSON validity** (`shapes2.py`, `jsonbreak.py`). After `scrub_payload` the target breaks 29 of
the rows' canonical JSON, the PIN 24. Of the target's 29, 21 are new: the Cookie rule in 10 quoted spellings
(`echo "... Cookie: sid=v ..."`: its class `[^\r\n"']+` takes the backslash of the closing `\"`), and `pwd`,
`credentials` and `passphrase` ordinary texts in quotes. The PIN's own credential rule breaks the same class (a quoted
`X-Api-Key:`, `password=`, `token:` in a Bash command: broken, value hidden, both trees), and the file says so at line
169 ("scrub's own class, _V, takes that backslash"). AUTH2 keeps the JSON valid (its class has no backslash). SCRUB2 also
removes 10 PIN breaks (the lenient PEM rule takes 5 malformed blocks whole before the opaque rule eats the `n` of a
`\n`). `convert()` emits the text as a string field and never re-parses it, so no event is lost. Finding F5 (INFO).

**5f. The reasons behind the rejected forms, re-checked on the section 4 corpus** (`reasons.py`, `reasons2.py`: each region
a rejected form takes and its landed form does not):
- N-pwd: 27 path or reference values, and 6 names right after a letter, which are the 6 escape-preceded regions of
  `escape_corpus.py` (1 dec, 5 raw), each with a path value; 0 other values. The lane's reason holds.
- N-credentials: 140 regions of the bare-colon annotation form (124 of one masked word shape, `Aa{11}`), 2 glued names, 2
  quoted-name-then-`=` regions (a separator and a path). The reason holds.
- AUTH-any: 93 dec and 79 raw regions, every scheme word outside the known list, 128 of them after a capitalised
  `AUTHORIZATION` heading; no value is token-like (16+ characters with a digit). The reason holds.
- P3: 191 regions, 153 of them 1,000+ characters, the longest 37,309 (the lane: "up to 15,522", on its own count), and 0
  key-body lines (40+ base64 characters on one line) inside any of them. The reason holds, and rejecting P3 hid no key.

**5g. CRED2's raw-view cost, re-checked (added 06:0xZ).** The lane's section 3 describes CRED2's raw regions (main raw
5 texts / 10 regions, subagents raw 1 / 1) as "5 distinct uncommitted values behind a JSON key `credentials` in the record
structure ... the shape the rule is for". `cred_raw.py` (each raw-view region the landed rule takes and the PIN's scrub does
not, over the section 4 corpus): 0 of the 11 CRED2 regions sit behind a JSON key. 10 of 11 are ordinary code or prose
(masked: `..._credentials=None)\n\n...`, a `credentials ==` line before a path, `credentials===\n===...`,
`..._CREDENTIALS=0\n000:...`) whose value, decoded, is under 8 characters: in the raw view the JSON escapes (`\n`) count
as value characters, so the value passes the 8-character floor and the redaction runs into the next line. The 11th is a
probe line. Through the real `convert()` (a Bash tool input, target vs PIN): `Client(credentials=None)` + a blank line +
`rows = client.list()` loses `None)` and `rows`; `GOOGLE_APPLICATION_CREDENTIALS=0` + a newline + `next_step_here` loses
the whole next line; the PIN changes neither. Over-redaction, not a leak; the decoded digests are not affected (the floor
holds there). PWD2's 3 raw regions: 1 a JSON key holding a placeholder, 2 probe lines, as the lane says. Finding F15.

## 6. Attack item 3: timing (resumed lane, 05:3xZ)

Instruments: the first verifier's `timing.py` (31 hostile families, each call in a child so a regex can be killed; no
secret involved), driven by `timing_run.py` in two chunks with a 20 s child timeout; `exposure.py` (the corpus's worst
inputs, timed); `e2e_timing.py` (the real `export()` and `convert()`); `pemfix.py` (the cause, and a candidate guard, in
memory only). `scrub`, sizes n = 250, 500, 1000, 2000; seconds at the two largest sizes and the growth per doubling:

| Family (text length at n = 2000) | target | PIN |
|---|---|---|
| a run of dashes, no BEGIN (60,000) | 7.58 s at 30,000, **over 20 s** at 60,000, x4.0 | 0.014 s, x2.0 |
| a dash run + one BEGIN (60,026) | 8.11 s at 30,013, **over 20 s**, x4.1 | 0.013 s, x1.9 |
| 4-dash BEGIN lines, no END (60,000) | 1.04 s, 4.07 s, x3.9 | 0.014 s, x1.9 |
| spaced 3-dash BEGIN lines, no END (52,000) | 0.19 s, 0.86 s, x4.5 | 0.012 s, x2.1 |
| 4-dash BEGIN + a wrong END, repeated (120,000) | 2.87 s, 11.18 s, x3.9 | 0.028 s, x2.0 |
| `cookie: x ` heads on one line (20,000) | 0.072 s, 0.276 s, x3.8 | 0.005 s, x1.9 |
| `Set-Cookie:` heads (22,000) | 0.082 s, 0.315 s, x3.8 | 0.007 s, x2.8 |
| the other 24 families (5-dash BEGIN with no END, Authorization heads and spaces, pwd, credentials, passphrase, escapes before provider prefixes, the right anchor, the opaque union boundary, `_` runs, quotes, spaces) | linear, at most 0.035 s | linear |

Cause (`pemfix.py`): the lenient private-key rule (line 81). With it removed, both dash families are linear (0.028 s at
60,000). Its head `-{3,}[ \t]*BEGIN` retries at every dash of a run and backtracks through the run each time. A start
guard `(?<!-)` makes the dash run linear (0.033 s at 60,000) and keeps all four malformed-PEM fixtures' outputs equal to
the landed rule's (key body hidden in each). Many BEGIN heads with no END stay quadratic under the guard (1.96 s at
60,000): each head's lazy body scans to the end of the text. The Cookie rule's lookahead scans the rest of the line from
every head.

Exposure (`exposure.py`, 7,669,040 strings, 1,281,887,150 bytes, every transcript, both views): the longest dash run is
278 characters; the most BEGIN heads in one string is 14; the most cookie heads on one line is 60. The worst real strings
take at most 0.068 s on the target (0.046 s on the PIN). End to end (`e2e_timing.py`, one user turn and one tool result):

```
15,000 dashes          target: export() 1.92 s, convert() 3.84 s  | PIN: export() 0.00 s, convert() 0.02 s
2,000 BEGIN lines      target: export() 4.01 s, convert() 10.64 s | PIN: export() 0.02 s, convert() 0.11 s
```

The growth is quadratic, so a tool result with 60,000 dashes would cost about a minute in `convert()` and a longer one
many minutes (not run: the 20 s child cap). Measured exposure today: none. Finding F7.

## 7. Attack item 4: the value gate (resumed lane, 05:3xZ)

Instrument: `gate3.py` = the first verifier's `gate2.py` (reviewed) with bounded sizes (a 256 MiB random raw key would
need tens of GB for its windows, on a shared sandbox with no swap) and two race cases. FIXTURE sources only, made in
scratch; each `export()` in a child with a timeout; every output line checked for any 8-byte piece of every fake first.

- **Non-regular sources, both kinds (env-file, raw-file):** a FIFO, a directory, a symlink to each, `/dev/null`,
  `/dev/zero`, `/dev/urandom` and a unix socket each refuse at once: rc 4 in 0.03 to 0.04 s, nothing written, one line
  `value gate: cannot read the source <basename> (NotRegularFile | IsADirectoryError | OSError)`. A dangling symlink and
  an empty file are "missing or empty, skipped" (rc 0, one line with the path), as designed since SCRUB1 (VERIFY-SCRUB1 F10).
- **Races:** a regular source replaced by a FIFO right after the `os.path.exists()` check refuses (NotRegularFile), for
  both kinds: the `fstat` is on the opened descriptor. A 3 MiB raw key truncated after its first 1 MiB chunk is read short
  and the export writes (rc 0): a source that shrinks during the read is never refused. The real key is 32 bytes, read
  in one chunk.
- **Size:** no cap. A random raw key of 64 KiB takes 0.64 s and 50 MB, 256 KiB 2.94 s and 172 MB, 1 MiB 15.0 s and 654
  MB (the windows of six printed forms). A 256 MiB sparse env file: 1.41 s, 523 MB, skipped (no `NAME=value` line).
- **Malformed names:** `# comment`, a blank line, a CRLF line, a line whose name holds a space, and a line with a lone CR
  before `BAD-NAME=` give `GOOD_NAME`, `<malformed line 4>`, `ALSO_GOOD`, `<malformed line 5>`: numbered by "\n"
  lines, as grep numbers them.
- **Residual of VERIFY-SCRUB1 F13:** a NAME shaped like an identifier passes `ENV_NAME` and is printed as it is. A fake `ghp_<hex>=<v>`
  line puts the fake token on the refusal line (my instrument withheld the line). This is the contract's own rule
  (item 5); a real env file with a token as a key name is hypothetical. Finding F8 (INFO).
- **Unknown kinds:** `env_file` (a typo, with a FIFO behind it), `''`, and a good source followed by an unknown kind
  each refuse before any source is read (0.03 s, no hang; the line names the source's basename and the kind).
- **Controls:** a good env file with its value pasted refuses (`good.env:ZQ_GOOD_TOKEN value whole=1 windows=25/25`);
  clean text writes.
- **Reach without `main()`** (a literal sweep of `KNOWN_VALUE_SOURCES`, `known_values(`, `export(` outside
  `transcripts/`, `tasks/`, `docs/`, `wiki/`, vendored trees): no default binds a source anywhere. The production path is
  `main()` (`push_clean.sh:185` runs the CLI). `known_values_check.py` takes sources from its CLI only.
  `qwen_matrix.py:127`, `hermes-session-export.py:23` and `laya_ft/common.py:39` load `scrub` only. One more caller exists
  in the tree: the SYNTH1 lane's UNCOMMITTED `scripts/s1_synth.py:1406` and `:1414` pass `TE.KNOWN_VALUE_SOURCES` at call
  time (SCRUB2's pattern), and its tests set fixture sources. Not SCRUB2's, not touched; noted as INFO (F9).

## 8. Attack item 6: the consumer patches (measured 05:3xZ, before the container restart the coordinator reports at about 05:40Z; written 05:4xZ)

**`session_export.PATTERN_NAMES` against the rules, in order.** A probe per name (`t/scripts`, fakes only): each of the 23
names' own fake text is changed by the rule at the same index; 23 names for 23 rules (14 of `SECRET_PATTERNS`, 9 of
`PAYLOAD_PATTERNS`). The list is aligned now.

**Does a test catch a misaligned list?** `mutate3.py se` (the first verifier's 7 name mutants, reviewed), inside
`masked.sh absent` on `<scratch>/vscrub2/mt` (a copy of cdbc1b8; checked equal to `t` before and after):
```
CONTROL (unmutated): rc=0 72 passed in 14.23s
N1 PATTERN_NAMES: pwd <-> credentials                      SURVIVED 72 passed
N2 PATTERN_NAMES: cookie <-> authorization-scheme          KILLED   1 failed  (test_gate_counts_patterns_and_canaries_and_prints_none)
N3 PATTERN_NAMES: private-key <-> private-key-malformed    SURVIVED 72 passed
N4 PATTERN_NAMES: one name dropped (count 22)              KILLED   6 failed  (test_no_canary_survives_the_export, ...)
N5 PATTERN_NAMES: sk-key <-> github-token                  KILLED   1 failed
N6 PATTERN_NAMES: opaque-run <-> bridge-link               KILLED   6 failed
N7 PATTERN_NAMES: an extra name (count 24)                 KILLED   6 failed
TOTAL {'KILLED': 5, 'SURVIVED': 2, 'INVALID': 0}
```
So the next rule change is not silent. A count change makes `gate_patterns()` (line 805) fall back to `pattern-N` names;
the two exemptions of `gate_file()` (lines 846, 849) key on the name `opaque-run`, so they stop, the gate counts the
harness's long tool names, and 6 tests fail (fail closed). Moving `opaque-run` itself is caught the same way. Two
same-count swaps survive: `pwd`/`credentials` and `private-key`/`private-key-malformed`. No exemption keys on those
names, so only the gate report's per-pattern labels would be wrong. No test pins each name to its rule. Finding F10.

**The two test patches.** `tests/test_session_export.py`: `ORACLE_SHAPES[0]` is now the landed opaque rule, typed, and
line 1128 pins it equal to `se.RUN_SHAPES` (by design, a typed copy, so a rule change forces the oracle's edit); the gate
total moves from 10 to 11, and a new assertion holds `pattern:authorization-scheme == 1` (N2's kill shows it pins).
`tests/test_jev_locate_echo.py`: the `é`-glued run is VERIFY-SCRUB1 F12's leak, which SCRUB2 closes; the de-vacuous assertion (line 596,
every counter at least 3) needs a third unstable tail, and the patch adds a third letter-glued fake key (`xoxb-` + 20: 26
characters, under the opaque floor; the xox rule's left anchor fails after the letter, so the whole-text scrub leaves it and
a cut that starts on it is taken). The comment at line 561 is corrected. Stale: the docstring at line 544 still says "tail
cuts on a run", which the lane named and left (outside its boundary). Finding F11 (INFO).

## 9. Attack item 7: the Laya lock (measured 05:3xZ, written 05:4xZ)

The first verifier's `laya_v.py` (reviewed: `build_dataset.collect_v2` / `collect` from the tree, `common.scrub` bound
in turn to the PIN's scrub, the target's, and a control N-pwd = the PIN with `pwd` added to its credential names; whole
items compared; no bytecode written), one commit per call (`laya_run.py`):
```
v2 collect_v2 at 434b727dfd: PIN 6220 items | target 6220, differs from the PIN in 0 | N-pwd control differs in 16
   the 16 items N-pwd changes: the target equals the PIN on 16 of them
v1 collect at eb256f49c0:    PIN 1788 items | target 1788, differs in 0 | N-pwd control differs in 0
v1 collect at 0b342c7a29:    PIN 1788 items | target 1788, differs in 0 | N-pwd control differs in 0
common.scrub is loaded from the tree's exporter; its rules equal the target's: True   (each run)
positive control (the PIN's scrub, then every "e" -> "E"): differs in 1788 of 1788 (eb256f4), 1788 of 1788 (0b342c7),
   6220 of 6220 (434b727)
```
The brief's question, answered: the landed `pwd` rule changes none of the 16 v2 items that the rejected name form
changes, and the pre-fit check proves it. The check is not blind in either version: N-pwd reds 16 v2 items, and the
positive control reaches every v1 and v2 item (N-pwd alone would not show that for v1, where it changes 0).
The manifest: `2026-09-25-recorded/dataset-manifest.json` records the exporter as 6ad316dccfca0147..., which equals the
sha256 of the landed `scripts/transcript_export.py`; cdbc1b8 changed that one line only (`git show`). The dataset rebuild
(the lane's 99070c33... bytes) and the Laya pair were not re-run here (the coordinator's landing gate ran the pair: 74
passed); the pre-fit comparison answers the lock question.

## 10. Attack item 5, continued: set A under the trace (resumed lane, 05:5xZ)

A static copy `<scratch>/vscrub2/sa` = `git archive cdbc1b8` of scripts, tests, harness-ports, src, docs, .claude/hooks,
.claude/skills, wiki and the top-level context files (65 MB, no `.pc-bridge.env`), the lane's own copy recipe. First the
bare gate, `masked.sh absent` (every guard boolean True):
```
$ masked.sh absent sa -- bash scripts/test_summary.sh <set A> --basetemp=...        15 files set=271f9e77620b
pytest-exit: 0
pytest-summary: 746 passed, 1 skipped in 96.43s (0:01:36)
```
(the set id from `pc_suite.sh`'s `set_id`; `test_summary.sh` prints none.) Then `trace2.sh` (`trace.sh` with strace's
output piped through a filter that keeps only lines naming a source path: the same counts, a bounded log) under
`masked.sh fakes` (all five sources present as FAKES), set A in three groups:
```
group 1 (transcript_export, known_values_check, session_export, chat_find, hiccup_scan, jev_client, jev_context):
   465 passed in 87.75s     | tree .pc-bridge.env 0 | api.env 0 | pseudonym.key 0 | /root/.config/qwen 0 | token lookups 0
group 2 (jev_locate_echo, recorded_labels, qwen_jev, edit_snapshot_ap_screen):
   248 passed, 1 skipped in 26.21s | every source 0      | token lookups 88: 44 + 44 test_jev_locate_echo.py:101
group 3 (ship_to_pc, push_clean_lock, hermes_session_export, qwen_matrix):
   33 passed in 49.27s      | every source 0            | token lookups 548: 267 + 267 test_push_clean_lock.py:51,
                              5 + 5 test_ship_to_pc.py:153, 2 + 2 urllib/request.py:2516 and :2526 (the proxy scan)
the copy's own FAKE .pc-bridge.env: 1 newfstatat per group, 0 opens (pytest's rootdir walk)
```
Together: 746 passed, 1 skipped, the bare run's count. Group 3's 31 lines that name a `.pc-bridge.env`: 3 the copy's
fake (a stat and two ENOTDIR probes), 24 `<basetemp>/<test>/repo/.pc-bridge.env` (the ship_to_pc fixture repos' own
files: 22 openat, 1 newfstatat, 1 unlink) and 4 `unlinkat(<dirfd>, ".pc-bridge.env")` (the basetemp cleanup). 24 + 4 =
28, the lane's number. **Reproduced: no set-A test opens a real source; the token lookups are the lane's A2 (child
environments copied whole: 267, 44 and 5 per variable, plus urllib once), not gate reads.** The copy was deleted after
the runs.

## 11. Attack item 8: mutation on the new code (resumed lane, 05:5xZ)

Both drivers run inside `masked.sh absent` on `<scratch>/vscrub2/mt` (`git archive cdbc1b8`), the unmutated control first,
every edit's anchor exactly once, KILLED only on a FAILED test (AF-AP-223), an error-only run INVALID; `mt` equal to the
pristine copy `t` after every call.

**The lane's 52 mutants on the final bytes** (`mutate2_lane.py`, the first verifier's adaptation of the lane's
`mutate2.py`; the lane's own pass ran before its D8 edit, its D11):
```
CONTROL (unmutated): rc=0 207 passed in 2.15s            (both calls)
mutants 0-25:  TOTAL {'KILLED': 26, 'SURVIVED': 0, 'INVALID': 0}
mutants 26-51: TOTAL {'KILLED': 26, 'SURVIVED': 0, 'INVALID': 0}
```
Reproduced: 52 of 52 killed (R1-R5, E1-E3, L1-L5, O1-O4, N1-N2, P1-P2, C1-C2, K1-K2, A1-A2, M1-M2, S1-S5, F1-F7, V12, V13,
V15-V20, V23, M1', M9'). The FIFO mutants (F2, F6, F7) are killed by the tests' timeouts as FAILED tests (22 to 42 s).

**The first verifier's own 28 mutants** (`mutate3.py te`):
```
CONTROL (unmutated): rc=0 207 passed in 2.14s
KILLED 14: W9 (pwd: a $ start is a value), W12 (opaque floor 41), W16 (cookie stops at a space), W17 (kind check inside the
  read loop), W18 (a directory as NotRegularFile), W19 (name prefix match), W20 (lines from 0), W21 (splitlines numbering),
  W22 (no O_NONBLOCK, 41.97s), W23 (raw key by plain open, 22.15s), W24 (TYPESAFE skip dropped), W25 (autouse tripwire
  removed), W26 (MIN_VALUE 9), W27 (xox takes _)
SURVIVED 13: W1 cookie floor 8 -> 12, W2 cookie floor 8 -> 5, W3 authorization floor 8 -> 12, W4 pwd floor 8 -> 12,
  W5 credentials floor 8 -> 12, W6 negotiate dropped, W7 ntlm/key/ssws/digest dropped, W8 pwd: a backslash start is a
  value, W10 upper-case \uXXXX hex not an escape, W13 lenient PEM: no tab, W14 lenient PEM: no BLOCK suffix,
  W15 lenient PEM: greedy body, W28 sk refuses a following dash
INVALID 1: W11 (its edit put a bare quote into a raw string: a collection error; my instrument's defect, not a kill)
```
Two survivors are equivalent mutants: W6 (Negotiate never fires, section 5b) and W28 (the greedy class already takes every
dash, so `(?!-)` never decides). The other 11 are behaviours of the new rules that no test pins: the 8-character floor of
each new named rule (in either direction), four of the ten schemes (only Token, a bearer, Basic and ApiKey are tested),
the backslash exclusion of `pwd`, upper-case hex in `\uXXXX`, and the lenient PEM rule's tab, `BLOCK` suffix and lazy
body (a greedy body would join two blocks and hide the text between them). The landed code is right on each (read, and
section 5's probes); the tests do not hold it. Finding F12. In total, with section 8's 7 name mutants: 71 of 84
valid, non-equivalent mutants killed (the lane's 52 of 52; mine 14 of 25 here and 5 of 7 in section 8).

## 12. VERIFY-S1-RATE F6, confirmed; a new gap, not SCRUB2's (resumed lane, 05:5xZ)

`f6_aws_jwt.py` (fakes built at run time; labels and booleans only), in an S1-RATE note, in prose and assigned, through the
target's and the PIN's `scrub`, `scrub_payload`, `scrub_strict`, and the target's `export()`:
```
AKIA + 16 (a key id, 20 chars)        leaks in note and prose through scrub and scrub_payload; the digest leaks | PIN identical
ASIA + 16 (a temporary key id)        the same                                                                   | PIN identical
JWT, 3 segments of 20, 22, 32         all three segments (the signature too) survive scrub and scrub_payload     | PIN identical
JWT with a 79-char payload            only the header (the public {"alg": ...} encoding) survives: the opaque rule takes the rest
AWS secret key (40 base64, / or +)    leaks in note and prose: `/` and `+` cut the opaque rule's run under 40      | PIN identical
scrub_strict takes all of them; an assignment (`aws_secret_access_key = <v>`) takes them through the credential rule
```
**Confirmed.** Not covered by SCRUB2's contract: items 1-8 and the VERIFY-SCRUB1 findings it set out to close (VERIFY-SCRUB1 F14's list:
`passphrase`, `pwd`, `credentials`, `Cookie`, `Authorization: Token`, malformed PEM) name no AWS key id, AWS secret key
or JWT, and the PIN behaves identically. So it is a new gap, task #319, with the AWS secret access key in prose (40 base64
characters holding `/` or `+`, about 72% of random keys) as a third shape for the same task. Present exposure: the 19
committed digests at HEAD hold no AWS key id, JWT or AWS-secret-like shape (a literal sweep, counts only). Finding F14
(INFO, outside the boundary).

## 13. Stale context, evidence audit, static gates (resumed lane, 05:5xZ)

- **Static:** pyflakes rc 0 on the four boundary files; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` prints 0 for the seven
  target files and this report.
- **Stale context the diff falsifies:** the docstring at `tests/test_jev_locate_echo.py:544` ("tail cuts on a run"; the
  lane named it; F11). Older line cites into the exporter, stale before SCRUB2 and moved again by it:
  `tests/test_decisions_canonical.py:627` (`:33`, the lane's A3), `src/agent_factory/decisions/volatile.py:75` (`:64`) and
  `:107` (`:57-62`; that file last changed on 09-24, before SCRUB1). `docs/INCIDENT-LOG.md`'s AF-AP-224 row still lists
  "the right side ... task #292" as OPEN: the coordinator's row, to update with this verdict. The exporter's own comments
  match the code (VERIFY-SCRUB1 F17's "40+" is fixed).
- **Evidence audit (the lane's report against what I reproduced):** section 3's texts-changed layer, every cell (section 4
  here); the Laya lock 0 of 6,220 and 0 of 1,788 at both v1 commits, and N-pwd's 16 (section 9); 52 of 52 mutants
  (section 11); the touch proof, set A included (sections 3, 10); set A 746 passed, 1 skipped, 15 files set=271f9e77620b
  (section 10); the manifest's one-line change (section 9); the test line ranges it cites (`_named_shapes` 1168-1198, the
  SCRUB2 tests 900-1289, the tripwire 391-401). Not true as written: D4's "Negotiate" among the covered schemes (F2), and
  the digest-size figure "3,577,907 bytes" is cdbc1b8's digest set, not the PIN's (section 4, a detail). Overstated by its
  name: `test_scrub2_shapes_never_reach_the_session_export` covers the item-3 shapes as JSON members only (F1). Not
  reproducible by rule here: the new digests' known-value check and "the real gate passes the real transcript" (both need
  the real sources; the coordinator's).
- **Mechanisms re-derived from primary source:** F1 (lines 95, 103, 105 against `_KEY_L` at 67; section 5a), F7 (line 81;
  removing it or guarding its head makes the dash run linear; section 6), F2 (line 88 runs before line 98, floor 8).

## 14. FINDING INVENTORY (no severity filter) (06:0xZ)

Evidence: R = reproduced here through the named path; S = read from source; U = not verifiable by this lane. Canonical path =
the production consumer at the target's bytes (cdbc1b8, the scratch copies checked against its blobs). `<s>` =
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2`. In sections 1-4, "(F2)" and "F3" name
VERIFY-SCRUB1's findings; "F6" and "F13" name this report's.

| # | Class | Finding | Evidence | Contract mapping | Canonical path | Material effect | Reproduction | Suggested fix |
|---|---|---|---|---|---|---|---|---|
| F1 | **BLOCKER** | The new named rules miss contexts the contract lists: `Cookie:`, `pwd=`, `credentials=` at a line start or after a tab inside a tool input (canonical JSON puts the escape letter `n`/`t` before the name), and after a literal `\n` in chat text; `Cookie:` after a non-ASCII letter; `pwd`, `credentials`, `Cookie`, `Authorization: Token` in a JSON document inside a tool input (escaped quotes). The rules use `\b` (line 95) or `(?<![A-Za-z0-9])` (103, 105) and a bare-quote head, where the provider rules got `_KEY_L`'s escape lookbehinds (67) and the payload rules take `\\*["']` | R (section 5a) | SCRUB2-brief EVIDENCE DEMANDS 3: "each new rule in every context (..., a JSON escape, a non-ASCII letter on either side, at a line start and end, ...) through the real functions and through export() and convert() end to end"; VERIFY-SCRUB1 F3's class | yes: `session_export.convert()` (line start, tab, escaped quotes); `export()`, the committed digest (Cookie after `é`/`の`; all three after a literal `\n`) | a credential in these shapes reaches the session export or a committed digest; `test_scrub2_shapes_never_reach_the_session_export` covers JSON members only; not a regression (the PIN had no such rules); 0 uncommitted instances in this session's transcripts | `python3 <s>/escape_named.py` (target convert column LEAK for rows 1-3 of pwd, credentials, Cookie; digest LEAK for the literal-`\n` row); `python3 <s>/escape_nonascii.py` (Cookie after é/の: target LEAK/LEAK); red test: add `{"command": "first line\npwd=%s rest"}` to the convert() test | give the three rules `_KEY_L`'s left side and take `\\*["']` around the name and value like lines 148/153/160; tests in every listed context through both writers; re-measure item 6 rows; re-run the Laya pre-fit check |
| F2 | FOLLOW-UP | `Negotiate` is a dead scheme: the credential rule (line 88; `Authorization` in `_NAME`, floor 8) runs first and takes the 9-letter scheme word, so `Authorization: Negotiate <token>` keeps the token; the report's D4 lists Negotiate as covered | R (5b) | none (item 3 names `Authorization: Token`; D4 is the lane's extension) | yes (`scrub`, `scrub_payload`) | a Negotiate token survives; D4 is not true as written | `python3 <s>/negotiate.py`; mutant W6 survives (equivalent) | order the scheme rule before the credential rule, or keep the credential rule off a known scheme word; a test |
| F3 | INFO | Other spellings pass, all as on the PIN: `curl -b`/`--cookie`, `document.cookie =`, a quoted cookie value, `Cookie2:`, `Digest ... response=`, `AWS4-HMAC-SHA256 Credential=`, `Authorization=Token`, `credential=`, `creds=`, `pass_phrase=`, `gpg --passphrase`, 2-dash or lower-case PEM | R (5c) | none (outside item 3's shapes) | yes | pre-existing shape gaps | `python3 <s>/shapes2.py` | a later scrubber increment |
| F4 | INFO | Ordinary text newly redacted beyond the lane's A4: `Authorization: Key rotation ...`, `Authorization: Digest authentication`, `pwd=C:\...`, `Client(credentials=credentials)`, `self.credentials = credentials`, prose naming both 4-dash header lines, dash-table headings | R (5d) | item 3 (cost by measurement: the lane's corpus counts stand; these are costs the corpus lacked) | yes (`scrub`) | over-redaction in digests; no leak | `python3 <s>/shapes2.py` | optional narrowing |
| F5 | INFO | Canonical-JSON validity: the Cookie, `pwd`, `credentials` rules (and `passphrase` as a name) take the backslash of a closing `\"` (21 new breaks in `shapes2.py`'s rows); the PIN's credential rule has the same class (line 169 says so); AUTH2 stays valid; the lenient PEM removes 10 PIN breaks | R (5e) | none | yes (`scrub_payload`); `convert()` never re-parses, no event lost | invalid JSON inside some tool_call texts | `python3 <s>/jsonbreak.py` | exclude a backslash before a quote from the value classes (`_VQ`) |
| F6 | INFO | (the first verifier's) LOST neighbours: non-secret text the PIN hid shows now (an escape's letter before a key, text glued to a gh/xox key by `_`, a strict-pass name); no piece of a key | R (section 4) | item 6's literal "no redaction ... lost"; condition 3 fails (no secret shown; the escape must stay) | yes | none (the JSON escape stays valid) | `python3 <s>/lost.py` | none |
| F7 | **BLOCKER** | The lenient private-key rule (line 81) is quadratic on a run of dashes (with or without BEGIN) and on BEGIN heads with no END: `-{3,}` retries at every dash and the lazy body scans to the end per head | R (section 6) | AF-AP-152 (registered 2026-09-23, names `scripts/transcript_export.py`; remedy: an anchor and a timing test on a long run); its edit screen does not fire on line 81 | yes: `export()` and `convert()` | 15,000 dashes: export 1.92 s, convert 3.84 s (PIN 0.00, 0.02); 60,000: over 20 s in `scrub` alone; the digest export runs on every push; 0 present exposure (longest dash run 278) | `python3 <s>/timing_run.py scrub 26 27` (dashes: 7.58 s at 30k, TIMEOUT at 60k; PIN 0.014 s); `python3 <s>/e2e_timing.py 15000 dashes` | `(?<!-)` before `-{3,}` (linear, fixtures unchanged: `pemfix.py`) plus a bound for heads with no END; a timing test on a long run |
| F8 | INFO | A NAME shaped like an identifier (a pasted `ghp_...` token) passes `ENV_NAME` and is printed on the refusal line (VERIFY-SCRUB1 F13's residual) | R (section 7) | item 5 (its own rule, met) | yes | hypothetical: a token as an env key | `python3 <s>/gate3.py` (the line is withheld) | print `<line N>` for every name |
| F9 | INFO | A second caller of the real sources exists: SYNTH1's UNCOMMITTED `scripts/s1_synth.py:1406`, `:1414` (the tuple read at call time) | S | none (another lane's file) | n/a | none today | `grep -n KNOWN_VALUE_SOURCES scripts/s1_synth.py` | SYNTH1's verify traces it |
| F10 | FOLLOW-UP | `PATTERN_NAMES`: two same-count swaps survive (`pwd`/`credentials`, `private-key`/`private-key-malformed`); no test pins each name to its rule; count changes and an `opaque-run` move fail closed (6 tests) | R (section 8) | none (the coordinator's patch; the brief's question) | yes (`gate_patterns`, `gate_file`) | a future swap mislabels the gate report | `masked.sh absent <s>/mt -- python3 <s>/mutate3.py se` | a test mapping each name to a probe its rule changes |
| F11 | INFO | Stale context: `tests/test_jev_locate_echo.py:544` ("tail cuts on a run"); older exporter line cites (`test_decisions_canonical.py:627`, `volatile.py:75`, `:107`); AF-AP-224 still lists #292 as OPEN | S | the diff falsifies the first; the rest pre-date it | n/a | none | read | the coordinator's edits |
| F12 | FOLLOW-UP | 11 non-equivalent survivors among my 28 mutants: the new rules' 8-character floors (W1-W5), four of ten schemes (W7), `pwd`'s backslash exclusion (W8), upper-case `\uXXXX` hex (W10), the lenient PEM's tab, BLOCK suffix, lazy body (W13-W15); the code is right, no test holds it | R (section 11) | none (the lane's 52 of 52 meet demand 3's controls) | n/a | a future regression goes unseen | `masked.sh absent <s>/mt -- python3 <s>/mutate3.py te` | one assertion each |
| F13 | INFO | (the first verifier's) the autouse tripwire guards `MOD` of `tests/test_transcript_export.py` only; a future test elsewhere that runs the real CLI would reach the real sources | S (section 3) | item 4 (met for the committed tests) | n/a | none today | read | a suite-level guard |
| F14 | INFO | VERIFY-S1-RATE F6 confirmed: `AKIA`/`ASIA` key ids, a JWT whose segments are all under 40 (signature included), and an AWS secret key with `/` or `+` pass `scrub` and `scrub_payload` and reach the digest; PIN identical | R (section 12) | none: not in SCRUB2's contract, a new gap (task #319) | yes | 0 such shapes in the 19 committed digests at HEAD | `python3 <s>/f6_aws_jwt.py` | task #319 |
| F15 | **BLOCKER** | CRED2's raw-view cost is misdescribed: the lane calls its raw regions "values behind a JSON key `credentials` ... the shape the rule is for"; 0 of 11 are, 10 of 11 are ordinary code or prose whose decoded value is under 8 characters and passes the floor only because the raw view counts JSON escapes as value characters; the redaction then eats the next line | R (5g) | item 3: "a shape that costs ordinary-text redactions goes in only with its count and your reason, else it is a DISCREPANCIES row": the cost was reported as no ordinary text | yes: `convert()` | ordinary words deleted from the session export (`Client(credentials=None)` + `rows ...`; `..._CREDENTIALS=0` + the next line); the decision table's evidence false for this rule; no leak | `python3 <s>/cred_convert.py` (target: `None)`, `rows`, `next_step_here` gone; PIN: none); `python3 <s>/cred_raw.py` | the same repair as F1: the value class stops at an escape (or the floor counts decoded characters); re-measure CRED2 and PWD2 |
| F16 | INFO | Value-gate residuals: a source that shrinks during the read is read short, never refused; no size cap (a 1 MiB raw key: 15.0 s, 654 MB) | R (section 7) | item 5 (met) | yes | hypothetical for the real 32-byte key | `python3 <s>/gate3.py` | optional: compare `fstat` size with bytes read; a size cap |
| F17 | INFO | (the first verifier's; the lane's A5) a SHORT key right after an ANSI colour code (`\x1b[31m`, `\x1b[0m`, `\x1b[m`) leaks, glued to the letter `m`; every real-length key is taken | R (section 4) | item 1 (the letter decision, SCRUB1 M16) | yes | short fakes only | `python3 <s>/anchors.py` | optional: treat an SGR sequence's `m` as a separator |

## 15. GATE RECOMMENDATION (06:0xZ)

**NOT-READY: blockers F1, F7, F15.** Each is reproduced here through the production writer at the target's bytes; the
recommendation depends on nothing this lane did not reproduce. Two readings carry weight and are the coordinator's to
confirm: F7 reads AF-AP-152 as a repository-wide rule for this file; F15 reads item 3's "its count and your reason" as
required evidence. Read otherwise, F7 or F15 is a FOLLOW-UP, and F1 alone still blocks.

The blocking predicate, all five conditions, per blocker:
- **F1.** (1) SCRUB2-brief EVIDENCE DEMANDS 3 names "a JSON escape", "a non-ASCII letter on either side" and "at a line
  start" for each new rule, through `export()` and `convert()`. (2) Reproduced through both. (3) A credential in a new
  shape reaches the session export, or a committed digest; the test named "never reach the session export" does not cover
  it. (4) `escape_named.py` and `escape_nonascii.py` give fixed LEAK cells; one added line in the convert() test reds.
  (5) The three rules are SCRUB2's.
- **F7.** (1) AF-AP-152, which names this file and prescribes an anchor and a timing test. (2) `export()` and `convert()`
  measured. (3) A quadratic stall of the per-push digest export and of the session export on one long dash line (0
  present exposure; the repo fixed task #187's instance in this file on the same terms). (4) `timing_run.py scrub 26 27`:
  over 20 s at 60,000 dashes against 0.014 s on the PIN. (5) SCRUB2's new rule.
- **F15.** (1) Item 3's cost rule: the rule's ordinary-text cost was reported as none. (2) `convert()` reproduced. (3)
  Ordinary words deleted from the session export, and the decision's evidence false. (4) `cred_convert.py`. (5) SCRUB2's
  rule and report.

Not blocking: F2 (outside item 3's wording), F10 and F12 (test gaps; the code is right), and the INFO rows (pre-existing,
hypothetical, or outside the boundary). No CONTRACT-DEFECT: nothing corrupts state or loses data outside the contract (F15's
over-redaction falls under item 3). No CONTRACT-INVALID: the premise holds, and F1's contexts are achievable (the provider
rules already handle them).

**A bounded repair, one wave, inside the four boundary files:** F1 and F15 together (the three named rules treat a JSON
escape as an escape before the name and inside the value, and take escaped quotes); F7 (a start guard and a bound for
heads with no END; a timing test); then item 6's rows for the changed rules and the Laya pre-fit check again (cheap:
sections 4 and 9). Cheap to fold in, not required: F2's rule order, F12's pins, F5's value class.

**What holds (reproduced):** item 1 (every real-length key taken in every context; no key redaction lost); item 2's
measurement (every texts-changed cell of the lane's table; the rejected forms' reasons); item 4 (non-regular sources
refuse at once; no default binds a source; names and counts only, F8 aside); item 5 (0 opens of any real source, set A
included; the token lookups are A2's child environments); item 6 (the name list aligned; the patches right); item 7 (0 of
6,220 and 0 of 1,788 items at both v1 commits; N-pwd's 16 unchanged by the landed rule; the manifest's hash); item 8 (52 of
52 lane mutants). Reviewed statically only: the exporter's comments and the stale cites, the AF-AP-152 screen's blind
spot, SYNTH1's caller. Skipped, with reasons, in section 16.

## 16. NOT done (06:0xZ)

- Not run, by rule: the known-value check of the new digests and the gate on the real sources (this lane never reads a
  real source; the coordinator's). The 256 MiB random raw key (tens of GB for its windows on a shared sandbox with no
  swap; bounded sizes instead).
- Not run, by choice: the Laya pair's 74 tests and the dataset rebuild (the pre-fit comparison answers the lock; the
  coordinator's landing gate ran the pair); the NEW/LOST region counts of the lane's table (the texts layer, section 5's
  probes and the first verifier's LOST grid cover the decisions); hermes-session-export and qwen_matrix on real Hermes
  JSON (the PC; no bridge).
- No git write; no tracked file touched (this report is untracked); no PC bridge; no subagent. Other lanes' files not
  touched (SYNTH1's `s1_synth.py` read by grep only). Scratch `<s>`: 27 MB (the first verifier's instruments and mine);
  the set-A copy (65 MB) deleted after use; `tr2/` traces kept (small). No bytecode written into the tree (`git status`
  unchanged: the other lanes' 9 entries only).
