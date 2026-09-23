# VERIFY-J1-1-R2 report — the targeted independent verify of the sk/bearer yield repair (task #197)

LANE: verify-j1-1-r2 (sandbox, `adversarial-verifier`, Opus 5.5, shared tree, no worktree isolation for own work).
Brief: `tasks/briefs/laya/VERIFY-J1-1-R2-brief.md`. PIN fb016d0 (the J1-1-R2 landing on origin; local 9ad0e66).
Contract: D-057 + B1..B5 of `tasks/briefs/laya/J1-1-R2-brief.md`, on top of D-056; J1-1-R1 A1..A5 in force.
Scratch: `/tmp/vj11r2/` only; the four scratch worktrees and the large outputs were removed at the end, the instruments (1.1 MB:
`tools/`, `repro.py`, the small `treepin`/`treenew`/`pinsrc` copies, `fixa`/`fixb`) are kept for re-runs. Every secret below is FAKE (`QZJ8…`, `X4Z9…`, `WQ7X…`).

STATUS: COMPLETE, 2026-09-23. GATE RECOMMENDATION: **NOT-READY** on three B2 regressions (R-1, R-2, R-4; section 17; each
reproduced through the real ledger path, each on a rare input), with a measured three-line repair (FIX-A, section 10). The
builder's own evidence reproduces exactly (sections 1, 8, 11); B1's eight rows, B4 and B5 hold; R-3 is a V-1 residue (FOLLOW-UP).

## 1. PREMISE — re-measured at the PIN (item 1)

```
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-09-23T15:28:23Z
$ git rev-parse --short HEAD ; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
15f20d3
0dfd28e
$ git log --format="%h %s" -1 fb016d0 | cut -c1-120
fb016d0 J1-1-R2 landed (task #192; GATED-PENDING-VERIFY): the sk and bearer classes yield to a later class's secret assi
$ for rev in fb016d0 9ad0e66 0dfd28e 15f20d3 <worktree>; do <blob id per boundary file>; done
bf04415d72c1eb788e17d0b1e877bc8fdb23dbc5 src/agent_factory/decisions/volatile.py      (all five revisions and the worktree)
440ac2426d8f559ca898f6e3664bc2807141987c tests/test_decisions_canonical.py            (all five)
6648679bd40a1dc953287e9733a28a83c3c5573b tests/test_decisions_ledger.py               (all five)
11df78562cf331a6fd2e5e302be9bb846e91e975 tasks/briefs/laya/J1-1-R2-report.md         (all five)
$ git diff --stat d556c9b fb016d0 -- <the three boundary files>
 src/agent_factory/decisions/volatile.py |  38 +++++-
 tests/test_decisions_canonical.py       | 214 +++++++++++++++++++++++++++++++-
 tests/test_decisions_ledger.py          |  78 ++++++++++++
 3 files changed, 326 insertions(+), 4 deletions(-)
$ git diff --stat d556c9b HEAD -- src/agent_factory/decisions tests/fixtures/decisions
 src/agent_factory/decisions/volatile.py | 38 ++++++++++++++++++++++++++++++---     (ledger.py, canonical.py, fixtures: unchanged)
$ grep -n <the brief's line-map pattern> src/agent_factory/decisions/volatile.py
57:_SECRET_NAME = r"(?i:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY)"
61:_ASSIGNMENT_HEAD = _SECRET_NAME + r"[\"']?\s?[:=]|(?i:(?:\b|(?<=_))token)[\"'\s]"
62:_ENVVAL_HEAD = r"(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY)="
67:_YIELD = (
74:_BEARER = re.compile(
77:_SK = re.compile(r"sk-(?=[A-Za-z0-9_-]{8})(?:(?!" + _YIELD + r")[A-Za-z0-9_-])*")
354:def _redact_str(text: str) -> str:
387:def decision_state(question_id: str, state: dict, root: str | os.PathLike | None = None) -> dict:
$ date -u ; for i in 1 2; do /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py -q -p no:cacheprovider --basetemp=/tmp/vj11r2/bt/r$i | tail -1; done
2026-09-23T15:34:46Z
121 passed in 3.60s      rc=0
121 passed in 3.48s      rc=0
$ bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py
2 files set=16a7b628685e
$ sed -n '163,201p' tasks/briefs/laya/J1-1-R2-brief.md > /tmp/vj11r2/v1_rows.py; sha256sum | cut -c1-16  -> 76b471d70524727b (the builder's copy: the same)
$ /root/venv-agent-factory/bin/python /tmp/vj11r2/v1_rows.py      (run from the repo root; 14 rows, all "ok", as the builder's section 5)
replayed rows: 14 shapes: 14 leaking: 0          rc=0
$ git worktree add --detach /tmp/vj11r2/pinwt d556c9b; cp <new V> …/volatile.py; + a scratch-only tests/test_zz_vj_import_path.py
  (asserts volatile.__file__ starts with /tmp/vj11r2/pinwt/src/ — the venv has an editable install of the SHARED tree)
bf04415d72c1 src/agent_factory/decisions/volatile.py   0afbf1b821ed tests/test_decisions_canonical.py   4a8bccead05f tests/test_decisions_ledger.py
$ date -u; cd /tmp/vj11r2/pinwt && PYTHONPATH=/tmp/vj11r2/pinwt/src python -m pytest -q -p no:cacheprovider <the two PIN files> tests/test_zz_vj_import_path.py
2026-09-23T15:35:21Z
73 passed in 2.63s      rc=0      (= the PIN's 72 + the import-path guard)
$ /root/venv-agent-factory/bin/python /tmp/vj11r2/tools/chained5.py     (the five KNOWN chained shapes; PIN V loaded from d556c9b, new V from fb016d0)
LEAK 'passwd=aAPI_KEY : X4Z92Q0X1ZX02Z71' -> 'passwd=<redacted:envval> : X4Z92Q0X1ZX02Z71'   same-as-PIN=True
LEAK "token='_API_KEY = 6Z4Z02ZX6Z4Z" -> "token='<redacted:envval> = 6Z4Z02ZX6Z4Z"   same-as-PIN=True
LEAK "password='-db_password: 62669Q3JJ88ZX5466" -> "password='<redacted:envval> 62669Q3JJ88ZX5466"   same-as-PIN=True
LEAK 'key: service-API_KEY: QZJ8QZJ8QZJ8' -> 'key: <redacted:envval> QZJ8QZJ8QZJ8'   same-as-PIN=True
LEAK 'mask-PASSWORD=QZJ8QZJ8QZJ8;token: WQ7XWQ7XWQ7XWQ7X' -> 'ma<redacted:sk>=QZJ8QZJ8QZJ8;token: <redacted:envval>'   same-as-PIN=True
```
PREMISE VERDICT: holds byte for byte (blob ids, line map, `121 passed` x2 on set `16a7b628685e`, driver `leaking: 0`, the PIN's
own tests `72 passed` against the new V, the five chained shapes identical to the brief's block and to the PIN's output). No
CONTRACT-INVALID stop. Scratch trees: `/tmp/vj11r2/treepin` = `git archive d556c9b src tests/fixtures/decisions`,
`/tmp/vj11r2/treenew` = the same at fb016d0; `diff -rq` between them: only `volatile.py` differs (20ebcd54f3ed vs bf04415d72c1;
ledger.py 71fc398a5340 and canonical.py 607b65b613e2 in both). Ledger-path instrument: `/tmp/vj11r2/tools/ledger_worker.py`
(per case `decision_state` -> `canonical` -> `make_row` -> `append` -> the appended line read back from disk -> `replay` of the
whole file; it asserts `volatile.__file__` is inside the tree it was given).

## 2. The flag-scope regression (found first; it drives items 2, 3 and 4)

READ FROM THE DIFF, THEN MEASURED. At the PIN `_BEARER = re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/-]{16,}=*")`: the GLOBAL
`(?i)` makes its run class case-insensitive. The new `_BEARER` form (`src/agent_factory/decisions/volatile.py:74-76`) scopes the flag to
`(?i:bearer)`, so the lookahead `(?=[A-Za-z0-9._~+/-]{16})` and the run `[A-Za-z0-9._~+/-]` are case-SENSITIVE. In Python's
`re`, a case-insensitive `[A-Za-z]` also matches four non-ASCII letters; three of them survive `normalize` (NFC):
```
$ /root/venv-agent-factory/bin/python /tmp/vj11r2/tools/probe_icase.py
PIN _BEARER: (?i)bearer\s+[A-Za-z0-9._~+/-]{16,}=* flags 34
NEW _BEARER flags 32 (re.I set: False )
U+0130 LATIN CAPITAL LETTER I WITH DOT ABOVE: NFC-stable=True (?i)[A-Za-z]=True [A-Za-z]=False
U+0131 LATIN SMALL LETTER DOTLESS I: NFC-stable=True (?i)[A-Za-z]=True [A-Za-z]=False
U+017F LATIN SMALL LETTER LONG S: NFC-stable=True (?i)[A-Za-z]=True [A-Za-z]=False
U+212A KELVIN SIGN: NFC-stable=False (?i)[A-Za-z]=True [A-Za-z]=False
```
**R-1 (bearer run).** A bearer token that holds U+0130, U+0131 or U+017F is redacted whole by the PIN; the new V leaves the whole
token visible (the letter within the first 16 run characters: the lookahead fails) or the tail after the letter. Through the
REAL path of both trees (`/tmp/vj11r2/tools/icase_ledger.py`: 5 shapes x 2 schemas; `replay` accepts all 10 rows in both trees;
`idem=True` for every row):
```
msg dotless-i inside       PIN line-has-body=False NEW line-has-body=True  err=None idem=True
    NEW state.msg = 'set Authorization: Bearer QZJ8QZJ8ıQZJ8QZJ8QZJ8QZJ8QZJ8 now'
snippet dotless-i inside   PIN line-has-body=False NEW line-has-body=True  err=None idem=True
msg dotless-i first        PIN line-has-body=False NEW line-has-body=True  err=None idem=True
    NEW state.msg = 'set Authorization: Bearer ıQZJ8QZJ8QZJ8QZJ8QZJ8 now'
msg long-s tail            PIN line-has-body=False NEW line-has-body=True  err=None idem=True
    NEW state.msg = 'set Authorization: <redacted:bearer>ſQZJ8QZJ8 now'
msg dotted-I inside        PIN line-has-body=False NEW line-has-body=True  err=None idem=True
    NEW state.msg = 'set Authorization: Bearer QZJ8QZJ8QZİQZJ8QZJ8QZJ8 now'
msg control ascii          PIN line-has-body=False NEW line-has-body=False err=None idem=True
    NEW state.msg = 'set Authorization: <redacted:bearer> now'
(the snippet rows of b2.hit_role: the same four NEW leaks, the control ok; PIN state.msg is 'set Authorization: <redacted:bearer> now' in all five)
```
**R-2 (the token branch's chain guard).** `_TOKEN` (unchanged, `src/agent_factory/decisions/volatile.py:85`) keeps its GLOBAL `(?i)`, so its run class
`[A-Za-z0-9+/]` matches the three letters; `_YIELD`'s token branch (`src/agent_factory/decisions/volatile.py:71-72`) checks its value and scans for a
second head with a case-SENSITIVE `[A-Za-z0-9+/]`. A special letter inside the token run hides a following `NAME[:=]` head from
the guard; sk/bearer yields; `_TOKEN`'s run then swallows the second NAME, and the SECOND value, which the PIN redacted, reaches
the ledger. (`/tmp/vj11r2/tools/r2_chain.py`; RUN = `QZJ8`x8, V2 = `X4Z9X4Z9X4Z9`; `replay` accepts 4 of 4 rows in both trees.)
```
R2-a sk, token space, dotless-i, password:
   PIN -> '<redacted:sk> QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8ıpassword: <redacted:envval>'
   NEW -> '<redacted:sk>token <redacted:token>: X4Z9X4Z9X4Z9'
R2-b bearer, token space, long-s, key=
   PIN -> '<redacted:bearer> QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8ſkey=<redacted:envval>'
   NEW -> '<redacted:bearer>token <redacted:token>=X4Z9X4Z9X4Z9'
R2-c sk, _token quote, dotted-I, secret:
   PIN -> '<redacted:sk>"QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8İsecret: <redacted:envval>'
   NEW -> '<redacted:sk>token"<redacted:token>: X4Z9X4Z9X4Z9'
R2-ctl same shape, ASCII (guard sees head)
   PIN -> '<redacted:sk> QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8password: <redacted:envval>'
   NEW -> '<redacted:sk> QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8password: <redacted:envval>'
R2-a  V2-in-line PIN=False NEW=True  | RUN-in-line PIN=True  NEW=False idem=True
R2-b  V2-in-line PIN=False NEW=True  | RUN-in-line PIN=True  NEW=False idem=True
R2-c  V2-in-line PIN=False NEW=True  | RUN-in-line PIN=True  NEW=False idem=True
R2-ctl V2-in-line PIN=False NEW=False | RUN-in-line PIN=True  NEW=True  idem=True
```
R-2 trades a value the PIN leaked (the run; the V-1 class) for a value the PIN redacted (V2). B2 counts the second: "every value
the PIN redacts stays redacted". Both R-1 and R-2 falsify the builder's by-construction claims (its section 1: "Where v2 does
not yield, the match equals the PIN's" and "no head starts inside that value or straddles its end"), which were measured on
ASCII inputs only (its section 14 discloses "Unicode separators … not generated"). Disposition: section 11.

## 3. Item 2 — B1 beyond the builder's rows (my own shapes)

**3a. The grid** (`/tmp/vj11r2/tools/b1grid.py`; none of the builder's or the appendix's rows): 22 name spellings (KEY, key, Key,
kEY, TOKEN, token, Token, SECRET, secret, Secret, PASSWORD, password, PassWord, PASSWD, passwd, PassWd, API_KEY, api_key,
Api_Key, APIKEY, apikey, ApiKey) x 12 separators (`=` `:` ` =` `= ` ` = ` ` :` `: ` ` : ` `"=` `':` `": "` `'='`) x 45
prefixes (`sk-` with 0..10 run characters before the name; `task-` `kiosk-` `whisk_x-sk-` `tsk-` at offsets 0/2/5; `bearer `
`Bearer ` `BEARER ` `bEaReR ` at offsets 0/4/8/11/16; a name inside a longer word: `…mon`+`key`, `…don`+`key`) x 6 values
(20, 8, 7 and 1 body characters; 32- and 40-character runs). Body alphabet `{Q,Z,J,X,4,9}`, used by no other byte. Each shape
as `b1.finding_sev.msg`, both V versions, `decision_state` then `canonical`:
```
$ /root/venv-agent-factory/bin/python /tmp/vj11r2/tools/b1grid.py
shapes: 71280 {'closed': 26896, 'both_leak': 23866, 'both_ok': 20518, 'new_leak': 0, 'nonidem_new': 0}
$ /root/venv-agent-factory/bin/python /tmp/vj11r2/tools/b1grid_cls.py
both-leak by value: {'v7': 11565, 'v1': 11565, 'v20': 184, 'v8': 184, 'run32': 184, 'run40': 184}
not explained by the 8-char floor: 736
by (value, sep): [(('v20', '= '), 184), (('v8', '= '), 184), (('run32', '= '), 184), (('run40', '= '), 184)]
by name: [('PASSWORD', 148), ('API_KEY', 112), ('SECRET', 108), ('PASSWD', 108), ('APIKEY', 108), ('TOKEN', 88), ('KEY', 64)]
```
The 23,130 v7/v1 rows are the widened class's 8-character floor (A4 by design: "so prose such as `key: sorted` is not
redacted"; the PIN's own `password: v7` stays too). **R-3, a V-1 residue:** the other 736 are an UPPER-CASE name, then `= `
(equals, one space), then a value, behind every prefix kind. `_YIELD`'s widened branch refuses any upper-case `NAME=` head
(`(?!` + `_ENVVAL_HEAD` + `)`, `src/agent_factory/decisions/volatile.py:69`) because "an upper-case NAME= is _ENVVAL's" (`src/agent_factory/decisions/volatile.py:65`), but `_ENVVAL`'s
`\S+` cannot start at a space, so `_ENVVAL` never takes `PASSWORD= v` and `_ENVVAL_WIDE` would: the run keeps its PIN form and
the name's value is freed, at the PIN and after. Sibling: the `==` form (branch A's padding rule, written for bearer's `=*`,
also stops the sk run, which has no padding). Through the ledger (`/tmp/vj11r2/tools/r3_ledger.py`; `replay` 7 of 7 in both trees):
```
R3-a task-DB_PASSWORD= v               PIN -> 'ta<redacted:sk>= QZJ8QZJ8QZJ8QZJ8QZJ8'   NEW -> the same   body-in-line PIN=True  NEW=True
R3-b Bearer … API_KEY= v               PIN -> 'Authorization: <redacted:bearer> QZJ8QZJ8QZJ8QZJ8QZJ8'   NEW -> the same   PIN=True NEW=True
R3-c sk-…SECRET= v                     PIN -> '<redacted:sk>= QZJ8QZJ8QZJ8QZJ8QZJ8'   NEW -> the same   PIN=True NEW=True
R3-e no prefix PASSWORD= v (control)   PIN -> 'DB_PASSWORD= <redacted:envval>'        NEW -> the same   PIN=False NEW=False
R3-f task-PASSWORD==v (padding form)   PIN -> 'ta<redacted:sk>==QZJ8QZJ8QZJ8QZJ8QZJ8' NEW -> the same   PIN=True NEW=True
R3-g no prefix PASSWORD==v (control)   PIN -> 'DB_PASSWORD=<redacted:envval>'          NEW -> the same   PIN=False NEW=False
```
**3b. Every field, every cut** (`/tmp/vj11r2/tools/fieldsweep.py` + `ledger_worker2.py` + `fieldsweep_grade.py`): 12 shapes
(8 of my own V-1 closers over each `_YIELD` branch and both classes, glued so `action_target`'s first-token rule keeps the value;
2 R-3 shapes; 1 R-1 and 1 R-2 shape) in each of the 16 bounded fields, cut by the bound so that k = 0..len(shape) characters
of the shape survive (two glues: `m`-run and `m`-run + space), plus each shape whole, in the three `file` fields, in
`action_target` and as a `paths` item. Every row through `make_row` -> `append` -> the line on disk; ledgers rotate every 40 rows.
```
treepin ledgers: 427 replayed rows: 17078 replay errors: []
treenew ledgers: 427 replayed rows: 17078 replay errors: []
w-colon              {'ok/ok': 544, 'leak->ok': 817}
w-eq-quoted          {'ok/ok': 608, 'leak->ok': 723}
w-apikey-sp          {'ok/ok': 545, 'leak->ok': 724}
A-upper-eq           {'ok/ok': 576, 'leak->ok': 245}
C-token-quote        {'ok/ok': 576, 'leak->ok': 1025}
bearer-w             {'ok/ok': 577, 'leak->ok': 1054}
bearer-A             {'ok/ok': 577, 'leak->ok': 532}
bearer-C             {'ok/ok': 609, 'leak->ok': 1382}
R3-upper-eq-space    {'ok/ok': 577, 'leak/leak': 692}
R3-padding           {'ok/ok': 576, 'leak/leak': 597}
R1-bearer-dotless    {'ok/ok': 257, 'ok->LEAK': 884}
R2-token-longs       {'ok/ok': 481, 'leak->ok': 705, 'leak/leak': 1195}
fields where the NEW line leaks, per shape: {'R3-upper-eq-space': 20, 'R3-padding': 21, 'R1-bearer-dotless': 20, 'R2-token-longs': 20}
```
(state, `canonical()` and the appended line agree on every row, asserted; no row is refused; no new output is non-idempotent.)
Item 2 verdict: every one of my closer shapes closes in every field and at every cut position, with no matchable fragment left
by a cut and every output a fixed point; B1's eight rows are closed (section 1). Open beyond the rows: R-3 (not a regression)
and the flag-scope leaks R-1/R-2 (regressions, section 2). The R-2 shape carries two fake bodies over one alphabet, so its
`leak/leak` rows are the run at the PIN and V2 after (section 2 separates them by string).

## 4. Item 3 — B2, an independent differential

**Instruments** (`/tmp/vj11r2/tools/diff3.py`, my own generator and two instruments, both V versions at `_redact_str` on
normalize-stable text): (1) a SWAP oracle with no knowledge of the patterns — a body byte is visible iff swapping it for a
class-equivalent byte (Q<->Z, J<->X, digit pairs; no name, flag, hex or placeholder rule tells them apart) changes the output;
(2) an ORIGIN tracker — the module's own six compiled passes re-run through `finditer`, every output character carrying its
input index, asserted equal to the real `_redact_str` on every input. The two must agree on every body position of every input
(`INSTRUMENT DISAGREE` counts a miss; it stayed 0 in every run below). The generator tags each character's role: `body`,
`keyname` (a secret-name spelling INSIDE a key's or token's body), `name`, `sep`, `pad` (bearer `=`), `head`, `tokchar`,
`special` (U+0130/U+0131/U+017F, 3 % per body character unless `--ascii-only`), `prefix`, `fill`, `ws`; `name2`/`sep2` mark
a value that holds a second head (the KNOWN chain family).
```
$ for s in 11 12 13; do diff3.py $s 20000 --ascii-only; done
seed=11 ascii_only=True {'inputs': 20000, 'outputs_differ': 3123, 'newly_visible_inputs': 3111, 'newly:name': 2701, 'newly:name+sep': 376, 'newly:keyname+pad': 29, 'newly:body+name': 1, 'newly:keyname+name+pad': 3, 'newly:body+name+sep': 1}
seed=12 ascii_only=True {'inputs': 20000, 'outputs_differ': 3087, 'newly_visible_inputs': 3076, 'newly:name': 2661, 'newly:keyname+pad': 35, 'newly:name+sep': 374, 'newly:body+name+name2+sep2': 1, 'newly:keyname+name+pad': 1, 'newly:body+name': 2, 'newly:body+name+name2': 1, 'newly:body+name+sep': 1}
seed=13 ascii_only=True {'inputs': 20000, 'outputs_differ': 3147, 'newly_visible_inputs': 3136, 'newly:name': 2714, 'newly:name+sep': 388, 'newly:keyname+name+pad+sep': 2, 'newly:body+name': 2, 'newly:keyname+pad': 28, 'newly:keyname+name+pad': 2}
```
**D-1 tested: FALSE as stated, three ways.**
1. **Body bytes newly visible in pure ASCII (R-4): 9 of 60,000 inputs** (the `body+…` keys above). Mechanism, traced by hand on
   the first: the sk (or bearer) run yields to `password':` because the value it sees, `X1334Q588J9Zbearer`, ends at a space
   and holds no head; `_BEARER` then replaces `bearer <token>` and the space inside its match disappears; `_ENVVAL_WIDE` and
   `_ENVVAL`, which run later, compute the value on the MERGED text, run through `<redacted:bearer>` and swallow the next head,
   and that head's value, which the PIN redacted, is freed. The guard decides on a value extent that a later pass changes.
   Minimal shapes through the ledger (`/tmp/vj11r2/tools/r4_ledger.py`, field `wf.drift.observed`; `replay` 5 of 5 in both trees):
```
R4-a IN  'task-password:QZJ8QZJ8bearer abcdefghijklmnop==token: X4Z9X4Z9X4'
     PIN 'ta<redacted:sk>:QZJ8QZJ8<redacted:bearer>token: <redacted:envval>'
     NEW 'ta<redacted:sk>password:<redacted:envval> X4Z9X4Z9X4'
R4-b IN  'task-PASSWORD=QZJ8QZJ8bearer abcdefghijklmnop==token: X4Z9X4Z9X4'      (branch A: _ENVVAL's \S+ swallows too)
     NEW 'ta<redacted:sk>PASSWORD=<redacted:envval> X4Z9X4Z9X4'
R4-c IN  'Bearer abcdefghijklmnoppassword:QZJ8QZJ8Bearer abcdefghijklmnop)key: X4Z9X4Z9X4'   (a bearer yield; ")" glue)
     PIN '<redacted:bearer>:QZJ8QZJ8<redacted:bearer>)key: <redacted:envval>'
     NEW '<redacted:bearer>password:<redacted:envval> X4Z9X4Z9X4'
R4-ctl IN 'task-password:QZJ8QZJ8 bearer abcdefghijklmnop==token: X4Z9X4Z9X4'     (a space before "bearer": no merge)
     NEW 'ta<redacted:sk>password:<redacted:envval> <redacted:bearer>token: <redacted:envval>'   (better than the PIN)
R4-a/b/c  V2-in-line PIN=False NEW=True | V1-in-line PIN=True NEW=False idem=True;  R4-ctl  V2 PIN=False NEW=False
```
   The merge needs three things: the value runs INTO the word `bearer` (no space before it; `(?i:bearer)` has no left
   boundary, so `…QZJ8QZJ8cupbearer abc…` works: measured); the PIN's bearer match ends before the second name (`=` padding,
   or a glue byte that `[^\s"'&,;]` holds and the bearer run does not; measured: `==` `:` `)` `(` `#`); and the second value
   follows its separator after a SPACE (with `…@key=X4Z9…`, no space, the merged value swallows that value too and redacts it:
   measured, no leak). Contrived text, but ASCII, deterministic, and a value the PIN redacted.
2. **Body bytes newly visible with U+0130/U+0131/U+017F (R-1, R-2; section 2).**
3. **"Name" bytes that belong to a real secret (`keyname`, 29-35 per 20,000 ASCII inputs).** A key's or token's body whose
   tail spells a secret name, then a separator and a value, now shows that tail. Example (seed 1):
   `'Bearer 5ZXZX3J04Z…0063551PASSWORD=&Bearer …'` — PIN `'<redacted:bearer>&<redacted:bearer> …'`, NEW
   `'<redacted:bearer>PASSWORD=<redacted:envval> …'`: the token's last 8 body bytes and its padding. The C-4 family does it
   with a plain colon: `Authorization: Bearer <token ending in "key">: rejected` shows `key`. The text cannot say whether
   `PASSWORD` ends the token or starts a label, so V-1's rule reads it as a label. The coordinator accepted D-1 at landing
   ("B2 covers values, and the other classes keep names the same way", fb016d0's message); that ruling's premise ("a secret
   NAME stays visible") does not hold for these bytes: they are a value's bytes, at most 8 of them, drawn from the 22-spelling
   name dictionary (a few bits of the token, never its random part). INFO for the coordinator.

## 5. Item 4 — the chain guard's boundaries

`/tmp/vj11r2/tools/guard4.py` + `guard4b.py`: the first value V1 over `{Q,Z,J,8}`, the second value V2 over `{X,4,V,9}` (no name,
placeholder or filler holds an upper-case V; a first run with `W` in V2's alphabet was an instrument error of mine — `PASSWORD`
holds a `W` — and is not counted). 4 prefixes (`task-`, `sk-bcdfghmn-`, `Bearer …`, `bearer …-my-`) x 6 first assignments
(`password: `, `password=`, `password: "`, `PASSWORD=`, `token `, `token'`) x 23 second heads — mixed case (`Key:` `kEy=`
`PassWord:` `API_key=` `apiKEY:` `SECRET=` `tOkEn:`), quoted (`key":` `key' =` `token"` `token'`), every token separator
(`token ` `token:` `token=` `_token ` `-token ` `Token ` `TOKEN ` `TOKEN=`) — x 6 placements (at the value's very end, in its
middle, at its start, after a space, after a comma, after a quote); plus a head at the very end of the text, and a head split
by the bound (msg, limit 200, the cut at every position from 2 characters before the second head to 1 past V2).
Grades: `same` = the PIN's output byte for byte; `better` = some PIN-visible body byte hidden and none newly shown; `WORSE` =
a body byte the PIN hid is now visible.
```
$ guard4.py        shapes: 3312 {'same': 1928, 'better': 1384}
$ guard4b.py       {'end-of-text same': 123, 'end-of-text better': 42, 'cut same': 3171, 'cut better': 924}   (no NON-IDEM key: every cut output is a fixed point)
```
Item 4 verdict: in ASCII the guard keeps the PIN's output or improves it at every boundary I built (0 WORSE of 7,572). Its two
blind spots are the ones item 3's generator found, both WORSE than the PIN: R-2 (a U+0130/U+0131/U+017F in a token run hides
the next head from the case-sensitive scan; section 2) and R-4 (the value's extent grows after the guard ran, when `_BEARER`
merges across the space inside `bearer <token>`; section 4). Neither is a KNOWN row: F-1 and D-3 are identical at the PIN
d556c9b and after (section 1's five shapes); R-2 and R-4 are not.

## 6. Item 5 — B4 identity

`/tmp/vj11r2/tools/b4_worker.py`, one subprocess per tree (PIN = treepin, new = treenew, FIX-A, FIX-B — the candidate fixes of
section 10), each importing its own `agent_factory` (asserted):
```
ap.violates_row.json       committed=594584bde9869086 new(state)=594584bde9869086 new(variant)=594584bde9869086 unchanged-in-all-4-trees=True
b1.finding_kind.json       committed=9e18ed7e5146a2c3 new(state)=9e18ed7e5146a2c3 new(variant)=9e18ed7e5146a2c3 unchanged-in-all-4-trees=True
b1.finding_sev.json        committed=8c42d5dd1e8c349e new(state)=8c42d5dd1e8c349e new(variant)=8c42d5dd1e8c349e unchanged-in-all-4-trees=True
b2.hit_role.json           committed=3ced4cd39a61faa5 new(state)=3ced4cd39a61faa5 new(variant)=3ced4cd39a61faa5 unchanged-in-all-4-trees=True
d1.bug_echo_scores.json    committed=5a8c4ad2659c0e6b new(state)=5a8c4ad2659c0e6b new(variant)=5a8c4ad2659c0e6b unchanged-in-all-4-trees=True
v1.finding_class.json      committed=f41a299c4a38ab30 new(state)=f41a299c4a38ab30 new(variant)=f41a299c4a38ab30 unchanged-in-all-4-trees=True
wf.drift.json              committed=a51a56c48e98cca6 new(state)=a51a56c48e98cca6 new(variant)=a51a56c48e98cca6 unchanged-in-all-4-trees=True
probe states: 226 refused(new): 0 | new==PIN: 226 fixa==PIN: 226 fixb==PIN: 226 | idempotent(new): 226
string values (goldens + probe): 6077
  treenew: redaction differs from the PIN on 0; values the redactor changes at all: 0
  treefixa: redaction differs from the PIN on 0; values the redactor changes at all: 0
  treefixb: redaction differs from the PIN on 0; values the redactor changes at all: 0
```
(`tests/fixtures/decisions/probe/questions.json`: 226 questions; 6,077 = every key and value string of the seven goldens and the
probe file, duplicates kept.) Observation: no committed fixture string holds anything the redactor changes, so this identity
check touches no secret class; it proves "no fixture string changes", nothing about the classes.
Idempotence on my shapes: the grid 71,280 (`nonidem_new: 0`), the field sweep 17,078 (`idem` on every row), the guard cut sweep
4,095 (no NON-IDEM), and `/tmp/vj11r2/tools/idem5.py` (my generator's texts, a random pad so the bound cuts anywhere, three
schemas' fields):
```
$ N=20000 SEED=77 idem5.py   {'new states': 20000, 'fixa states': 20000, 'fixb states': 20000}   (with U+0130/U+0131/U+017F; 0 NON-IDEMPOTENT)
$ ASCII=1 N=20000 SEED=78    {'new states': 20000, 'fixa states': 20000, 'fixb states': 20000}   (0 NON-IDEMPOTENT)
```
Item 5 verdict: B4 holds for the new V (and for both candidate fixes).

## 7. Item 6 — B5 cost

`/tmp/vj11r2/tools/cost6.py` (my own generators; best of 5 full `.sub` scans per size under a 10 s SIGALRM; the sandbox is shared
with other lanes, `uptime` at start: load average 1.24, 2.35, 2.93 on 4 cores). 2026-09-23T16:04:07Z. Times in ms:
```
generator                                          mod       16k     32k     64k    128k    256k  (ms)  ratios per doubling
sk many heads, each a 1000-char head-free value    PIN      0.02    0.03    0.06    0.09    0.34  1.94 1.97 1.54 3.77
sk many heads, each a 1000-char head-free value    NEW      1.79    3.59    7.27   14.89   31.89  2.01 2.03 2.05 2.14
sk one head, one huge head-free value              NEW      1.81    3.69    7.61   15.06   30.93  2.03 2.06 1.98 2.05
sk one head, huge NAME= value (branch A scan)      NEW      1.73    3.46    6.89   13.94   27.90  2.00 1.99 2.02 2.00
sk one head, huge token run (branch C scan)        NEW      1.69    3.40    6.88   13.66   27.82  2.01 2.02 1.99 2.04
sk run of near-heads KE                            NEW      2.55    5.23   10.17   20.26   42.18  2.05 1.94 1.99 2.08
sk run of near-heads PASSWOR                       NEW      2.88    5.67   11.40   23.30   47.23  1.97 2.01 2.04 2.03
sk run of near-heads API_KE / token_               NEW      2.74    5.39   11.19   22.95   45.58  1.97 2.07 2.05 1.99
sk head, value of near-heads KEY"x (A scan)        NEW      2.12    4.26    8.54   17.27   34.78  2.01 2.01 2.02 2.01
sk head, value of near-heads PASSWOR:              NEW      2.06    4.18    8.36   16.91   33.18  2.03 2.00 2.02 1.96
sk repeated 'sk-abcdefghPASSWORD=QZ8 '             NEW      1.30    2.58    5.15   10.31   20.71  1.99 1.99 2.00 2.01
bearer many heads, each a 1000-char value          NEW      1.88    3.81    9.73   16.97   30.05  2.03 2.56 1.74 1.77
bearer one head, one huge head-free value          NEW      1.92    3.76    7.57   15.08   30.76  1.96 2.01 1.99 2.04
bearer one long run of near-heads token.           NEW      2.70    5.46   10.79   22.26   43.96  2.02 1.98 2.06 1.97
bearer one head, huge value of 'bearerx'           NEW      2.00    4.03    8.08   16.10   32.30  2.02 2.01 1.99 2.01
max ratio per doubling: {'PIN': 3.77, 'NEW': 2.56, 'FIXA': 2.12, 'FIXB': 2.25}
_redact_str sk head, value of near-heads KEY"x (A sc PIN      2.07    4.23    8.16   16.11   32.16  2.05 1.93 1.98 2.00
_redact_str sk head, value of near-heads KEY"x (A sc NEW      2.31    4.67    9.27   18.43   37.95  2.02 1.99 1.99 2.06
_redact_str bearer one head, huge value of 'bearerx' PIN      1.68    3.45    6.84   13.98   27.70  2.06 1.99 2.04 1.98
_redact_str bearer one head, huge value of 'bearerx' NEW      2.71    5.35   10.88   21.57   43.29  1.97 2.03 1.98 2.01
_redact_str sk many heads, each a 1000-char head-fre NEW      2.67    5.35   10.47   21.22   42.41  2.00 1.96 2.03 2.00
```
(the full 56-row table with the PIN, FIX-A and FIX-B rows of every generator is the command's output; every FIX-A/FIX-B row is
linear, max ratio 2.12 / 2.25.) The two outliers (NEW "bearer many heads" 2.56 then 1.74; PIN 3.77 at a 0.09 -> 0.34 ms step)
are noise on a shared box: each is followed by a compensating step and no row trends upward. Why it stays linear, read from the
pattern: every `_YIELD` branch starts with a secret name followed by a separator that is not an sk or bearer run character, so a
full guard scan can start only at a run's end (at most 2 per run: `API_KEY`/`KEY`); every candidate is itself a head, so a
scan stops at the next candidate. The price: the new `_SK.sub` is about 100x the PIN's per character (47.23 ms vs 0.45 ms at
256k); the whole `_redact_str` about 1.2-1.6x. `test_env_assignment_redaction_does_not_backtrack_exponentially` is in the
`121 passed` (section 1). Item 6 verdict: B5 holds.

## 8. Item 7 — the builder's evidence

The builder's mutation tool (`/tmp/j11r2/tools/mut.py`) was removed with its scratch, so I rebuilt 18 of its 30 mutants from the
descriptions in its mutation table and wrote my own driver (`/tmp/vj11r2/tools/mut7.py`): a scratch worktree
`/tmp/vj11r2/mutwt` at fb016d0 plus a scratch-only import-path guard; per mutant an exact-count edit of the pristine new V
(count asserted 1), `py_compile`, the collection count equal to the baseline (AF-AP-78), the run, then the killing tests re-run
on the UNMUTATED copy (AF-AP-138); the pristine file restored at the end (asserted equal to fb016d0's). 2026-09-23T16:06:20Z to 16:10:38Z.
```
BASELINE (unmutated): rc=0 122 passed in 3.57s collected=122          (the 121 + the import-path guard)
m1     builder  _SK back to its PIN form                         :: 25 failed, 97 passed  :: KILLED | unmutated re-run of killers: rc=0 25 passed
m2     builder  _BEARER back to its PIN form                     :: 5 failed, 117 passed  :: KILLED | rc=0 5 passed
m3     builder  the verifier's option-B bearer (exact)           :: 6 failed, 116 passed  :: KILLED | rc=0 6 passed
m4a    builder  _YIELD without the NAME= branch                  :: 9 failed, 113 passed  :: KILLED | rc=0 9 passed
m4b    builder  _YIELD without the widened branch                :: 19 failed, 103 passed :: KILLED | rc=0 19 passed
m4c    builder  _YIELD without the token branch                  :: 2 failed, 120 passed  :: KILLED | rc=0 2 passed
m4d1   builder  widened branch without its chain guard           :: 1 failed, 121 passed  :: KILLED | rc=0 1 passed
m4d2   builder  NAME= branch without its chain guard             :: 3 failed, 119 passed  :: KILLED | rc=0 3 passed
m4d3   builder  token branch without its chain guard             :: 1 failed, 121 passed  :: KILLED | rc=0 1 passed
m4e    builder  widened branch without its 8+ value condition    :: 2 failed, 120 passed  :: KILLED | rc=0 2 passed
m4e3   builder  token branch without its 32+ condition           :: 2 failed, 120 passed  :: KILLED | rc=0 2 passed
m4f    builder  NAME= branch accepts = padding                   :: 1 failed, 121 passed  :: KILLED | rc=0 1 passed
m4g    builder  _SK floor on the truncated run                   :: 11 failed, 111 passed :: KILLED | rc=0 11 passed
m4g2   builder  _BEARER floor on the truncated run               :: 2 failed, 120 passed  :: KILLED | rc=0 2 passed
m4h    builder  widened branch without its NAME= exclusion       :: 1 failed, 121 passed  :: KILLED | rc=0 1 passed
m4i    builder  _ASSIGNMENT_HEAD without its token alternative   :: 1 failed, 121 passed  :: KILLED | rc=0 1 passed
m4j    builder  _ASSIGNMENT_HEAD without its name alternative    :: 4 failed, 118 passed  :: KILLED | rc=0 4 passed
m4k    builder  _BEARER with a global (?i)                       :: 1 failed, 121 passed  :: KILLED | rc=0 1 passed
RESTORED pristine: rc=0 122 passed in 3.60s; volatile sha matches fb016d0: True
$ /tmp/vj11r2/tools/mut7_check.py     (the killer node ids against the builder's table rows, abbreviations expanded)
identical killer sets: 18            (m1 … m4k: builder-listed == measured, by node id, every row)
```
The builder's evidence reproduces: every rebuilt mutant is red for the stated reason with the identical killer set, and every
killer set is green unmutated. (Not rebuilt: its m4n-*/m4u-* rows, the 12 single-name removals; the six `_SECRET_NAME` and six
`_ENVVAL_HEAD` names are covered by the m4j/V-M1/V-M10 family below and by its own table.)

My own mutants (the brief's five kinds, and a few more):
```
V-M1   (?i:) dropped: _SECRET_NAME case-sensitive                 :: 22 failed, 100 passed :: KILLED | rc=0 22 passed
V-M2   (?i:) dropped: bearer literal case-sensitive               :: 10 failed, 112 passed :: KILLED | rc=0 10 passed
V-M3   (?i:) dropped: _YIELD token branch case-sensitive          :: 122 passed            :: SURVIVED
V-M4   (?i:) dropped: _ASSIGNMENT_HEAD token alternative          :: 122 passed            :: SURVIVED
V-M5   _SK lookahead {8} -> {7}                                   :: 1 failed, 121 passed  :: KILLED (control[C-2]) | rc=0 1 passed
V-M6   widened value condition {8} -> {7}                         :: 122 passed            :: SURVIVED
V-M7   _BEARER lookahead {16} -> {15}                             :: 122 passed            :: SURVIVED
V-M8   widened branch's chain guard removed (guard class emptied) :: 1 failed, 121 passed  :: KILLED (class[chain-widened]) | rc=0 1 passed
V-M9   NAME= branch guard class narrowed \S -> the widened class  :: 1 failed, 121 passed  :: KILLED (class[chain-upper-past-a-stop]) | rc=0 1 passed
V-M10  _ENVVAL_HEAD narrowed: API_?KEY -> API_KEY                 :: 122 passed            :: SURVIVED
V-M11  (?<=_) dropped in the _YIELD token branch only             :: 122 passed            :: SURVIVED
V-M12  (?<=_) dropped in _ASSIGNMENT_HEAD only                    :: 1 failed, 121 passed  :: KILLED (class[chain-upper-token-space]) | rc=0 1 passed
V-M13  _ASSIGNMENT_HEAD token alternative loses its \s separator  :: 1 failed, 121 passed  :: KILLED (class[chain-upper-token-space]) | rc=0 1 passed
```
Survivor discriminators (`/tmp/vj11r2/tools/mut7_disc.py`, `b1.finding_sev.msg`, the unmutated new V vs the mutant):
```
V-M3   IN 'desk-access-TOKEN QZJ8…(40)'           new V 'de<redacted:sk>TOKEN <redacted:token>'          mutant 'de<redacted:sk> QZJ8…(40)'   (body visible)
V-M4   IN 'mask-PASSWORD=abc_TOKEN QZJ8…(40)'     new V 'ma<redacted:sk>=abc_TOKEN <redacted:token>'     mutant 'ma<redacted:sk>PASSWORD=<redacted:envval> QZJ8…(40)'   (body visible)
V-M11  IN 'desk-access_token QZJ8…(40)'           new V 'de<redacted:sk>token <redacted:token>'          mutant 'de<redacted:sk> QZJ8…(40)'   (body visible)
V-M6   IN 'task-password: QZJXQZJ'               new V 'ta<redacted:sk>: QZJXQZJ'                       mutant 'ta<redacted:sk>password: QZJXQZJ'   (the 7-char value is visible in both: A4's floor)
V-M7   IN 'Authorization: Bearer abcdefghijklmno' new V (unchanged)                                    mutant 'Authorization: <redacted:bearer>'   (over-redaction, no leak)
V-M10  IN 'desk-SERVICE_APIKEY=QZJ8QZ'           new V 'de<redacted:sk>APIKEY=<redacted:envval>'        mutant 'de<redacted:sk>KEY=<redacted:envval>'   (the name splits, no leak)
```
Item 7 verdict: the builder's 18 rebuilt mutants reproduce exactly. Three of my survivors are REAL test gaps, each a mutant that
reopens a leak no committed test sees: V-M3 (a case variant of the token space head behind sk: `…-TOKEN <run>`), V-M11 (the
`_token` space head behind sk: `…_token <run>`), V-M4 (the chain guard's case-blind token head: `…=abc_TOKEN <run>`). The
behaviour they guard is right today; the tests do not pin it. V-M6, V-M7 and V-M10 change no body byte (a visible name next to a
floor-length value, an over-redaction of a 15-character bearer token, a split name): mirror-precision drifts, not leaks.

## 9. Item 8 — the candidate rule for task #198 (INFORMATIONAL; never blocking)

Rule measured on scratch copies of the new V (`/tmp/vj11r2/tools/mkr8.py`): "a value run never extends over a following
`NAME[:=]` head", as a tempered run in the three value classes, head = `_SECRET_NAME + r"[\"']?\s?[:=]"`:
`_ENVVAL`'s `\S+` -> `(?:(?!HEAD)\S)+`; `_ENVVAL_WIDE`'s value `[^\s"'&,;]{8,}` -> `(?:(?!HEAD)[^\s"'&,;]){8,}`; `_TOKEN`'s run
`[A-Za-z0-9+/]{32,}` -> `(?:(?!HEAD)[A-Za-z0-9+/]){32,}`. R8a = the rule; R8b = the rule plus `_YIELD`'s three chain guards removed.
```
$ /root/venv-agent-factory/bin/python /tmp/vj11r2/tools/r8_measure.py
'passwd=aAPI_KEY : X4Z92Q0X1ZX02Z71'                PIN/NEW 'passwd=<redacted:envval> : X4Z92Q0X1ZX02Z71'     R8a/R8b 'passwd=aAPI_KEY : <redacted:envval>'
"token='_API_KEY = 6Z4Z02ZX6Z4Z"                     PIN/NEW "token='<redacted:envval> = 6Z4Z02ZX6Z4Z"         R8a/R8b "token='_API_KEY = <redacted:envval>"
"password='-db_password: 62669Q3JJ88ZX5466"          PIN/NEW "password='<redacted:envval> 62669Q3JJ88ZX5466"   R8a/R8b "password='-db_password: <redacted:envval>"
'key: service-API_KEY: QZJ8QZJ8QZJ8'                PIN/NEW 'key: <redacted:envval> QZJ8QZJ8QZJ8'            R8a/R8b 'key: <redacted:envval>API_KEY: <redacted:envval>'
'mask-PASSWORD=QZJ8QZJ8QZJ8;token: WQ7XWQ7XWQ7XWQ7X' PIN/NEW/R8a 'ma<redacted:sk>=QZJ8QZJ8QZJ8;token: <redacted:envval>'   R8b 'ma<redacted:sk>PASSWORD=<redacted:envval>token: <redacted:envval>'
'password: mykey=X4Z9Q'                               PIN/NEW 'password: <redacted:envval>'                      R8a/R8b 'password: mykey=X4Z9Q'
'password: QZJ8key=X4Z9X4Z9'                         PIN/NEW 'password: <redacted:envval>'                      R8a/R8b 'password: QZJ8key=<redacted:envval>'
$ DIFF_NEW=<r8a|r8b> diff3.py <11|12> 20000 --ascii-only        (PIN vs the rule; my item-3 generator and both instruments)
r8a seed=11 ascii inputs=20000 outputs_differ=5197 newly_visible_inputs=5197 with-newly-visible-BODY=684 disagree=0
r8a seed=12 ascii inputs=20000 outputs_differ=5125 newly_visible_inputs=5125 with-newly-visible-BODY=727 disagree=0
r8b seed=11 ascii inputs=20000 outputs_differ=6075 newly_visible_inputs=6075 with-newly-visible-BODY=689 disagree=0
r8b seed=12 ascii inputs=20000 outputs_differ=6043 newly_visible_inputs=6043 with-newly-visible-BODY=732 disagree=0
r8a seed 11: body-exposure inputs: 684 of which chained (a value holding a 2nd head): 626
   IN  'client-PASSWORD: "6API_KEY:890X8J8Q"sk-6681, sk-47QJPassword'   PIN 'client-PASSWORD: "<redacted:envval>"…'   R8 'client-PASSWORD: "6API_KEY:<redacted:envval>"…'
$ the 121 tests (+ import guard) in a scratch worktree at fb016d0:   r8a: 122 passed      r8b: 5 failed, 117 passed (the five chain-* guard rows)
```
Reading for task #198: the rule closes F-1 (the four widened shapes: the SECOND value is redacted) in both variants, and D-3's
shape only with the guards removed (R8b). It opens a new class: the FIRST value's stub before the second head falls under the
8-character floor and shows (`6`, `825`, `QZJ8`; `mykey=X4Z9Q` whole, the builder's own design-time warning), in 3.4-3.7 % of my
generator's ASCII inputs (mostly chained values). A stopped value would need to be redacted whatever its length (drop the floor
when a head stops the value), a design question for #198, unmeasured here. Note: R8a passes all 121 committed tests, so those
tests would not stop a rule that opens this class.

   The 9 ASCII inputs of item 3 with newly visible body bytes (all hold a `bearer` glued after a value: R-4). In ASCII, FIX-A
   (section 10) differs from the new V only in R-4's head, and it reports 0 of them, so all 9 are R-4's:
```
#1 IN  "task-password':X1334Q588J9Zbearer Q_.43XXB_F1~B660API_KEY==token: Q8Q661Q40"                     newly visible 'Q8Q661Q40'
   PIN "ta<redacted:sk>':X1334Q588J9Z<redacted:bearer>token: <redacted:envval>"      NEW "ta<redacted:sk>password':<redacted:envval> Q8Q661Q40"
#2 IN  'BEARER QQ1H_4ZH4-D029C4FKeyAPI_KEY: "069QQ0X4"bearer 04Z5~AA5ApiKeyapikey= 9Q518Q30X878Bearer 048J59317JXQJJ72Key=XX8JJ31TOKEN= 32QJ1Q0X5985'   newly visible '32QJ1Q0X5985'
#3 IN  'BEARER 7783ZQ4904437Q4J28X69Z6J900QQZQZ3870Q2J8PASSWORD:Q76163460J3J9XQ56313Bearer E3.3D958.XD_A~9Q==password: 783481JX35ZXAPIKEY= Z64051003219'   newly visible '783481JX35ZX'
#4 IN  "sk-4Q03 value; BEARER 9Q748Q48265Q2Q7TOKEN':214bearer FD39GG71E727QBBTokenapikey=ZZ26813X5secret= JJ6Q011103J204060Q54"   newly visible 'JJ6Q011103J204060Q54'
#5 IN  'sk-486220Q551X85X0Xapi_key= 975X8146865XJ351ZZ25878064J1293QBEARER 5JQ82X369119X672Z=API_KEY = 60QJ067839998XZ7Z963ZZ5Z751X8982passwd : 38Q8Q94XZJ12 rejected'   newly visible '60QJ067839998XZ7Z963ZZ5Z751X8982'
#6 IN  'fix&sk-3J-6Z0Xapikey = 19Q21ZZ51542J2154482BEARER 49X2J433Api_KeyTOKEN==817QX2854100745Q084Q5J31289858257887819QAPI_KEY : Q1503Z10'   newly visible 'Q1503Z10'
#7 IN  'Bearer 598X500986Z49Q6PASSWORDToken= X2X6Z15Bearer +E2C124D5_/X4BGapikey==PASSWD: "3399Z51ZXXQJ"password==42Q7604'   newly visible '3399Z51ZXXQJ'
#8 IN  'sk-19X61XZSECRET: Z6X9951X86446Q63J53079820X81418Xbearer 5786Z8555J7409Z2==passwd= JZ962X2XX, db_ApiKey"=57854Z75J'   newly visible 'JZ962X2XX'
#9 IN  'via, sk-Z5J2 BEARER Q562228470282J762914991QJ8JQ138J340J22Q5PASSWDSecret = 69355686BEARER 4Q345XJ56581J6J13PASSWORD==XZJ31Z43apikey= 6Z89Z460'   newly visible '6Z89Z460'
```
   With the special letters (`diff3.py 2|21|22 20000`, 3 % per body character, a deliberately dense rate): 1,944 / 1,923 /
   1,960 inputs of 20,000 newly show body bytes (R-1, R-2, R-4 together; `disagree=0` in each). The name-only rows
   (`newly:name`, `newly:name+sep`, 2,661-2,714 and 374-388 per ASCII seed) are D-1's accepted class.

## 10. A measured candidate fix (scratch copies only; a proposal, not built into the tree)

FIX-A — the three regressions, one line each (`/tmp/vj11r2/tools/mkfix.py`, applied to a copy of `volatile.py`@fb016d0):
```
61: _ASSIGNMENT_HEAD = … |(?i:(?:\b|(?<=_))token)[\"'\s]|(?i:bearer)\s"                                  (R-4: a value that runs into "bearer " is a chain)
72:     r"(?=(?i:[A-Za-z0-9+/]){32})(?!(?i:[A-Za-z0-9+/])*?(?:" + _ASSIGNMENT_HEAD + r"))"                 (R-2: mirror _TOKEN's global (?i))
75:     r"(?i:bearer)\s+(?=(?i:[A-Za-z0-9._~+/-]){16})(?:(?!" + _YIELD + r")(?i:[A-Za-z0-9._~+/-]))*=*"   (R-1: the PIN's run set restored)
```
FIX-B = FIX-A + the R-3 residue: `69: r"|(?!" + _ENVVAL_HEAD + r"\S)" + _SECRET_NAME …` (refuse the widened branch only where
`_ENVVAL` can match, i.e. a non-space after `=`).
Measured (every line above is pasted in sections 3-7 or here):
```
fixa on fixwt (799f786e4861): 122 passed in 4.13s    fixa on pinwt2 (the PIN's own tests): 73 passed in 3.05s    fixa driver: replayed rows: 14 shapes: 14 leaking: 0
fixb on fixwt (9ae38ff276ef): 122 passed in 4.76s    fixb on pinwt2:                       73 passed in 2.77s    fixb driver: replayed rows: 14 shapes: 14 leaking: 0
differential vs the PIN, 6 seeds x 20,000 (3 ASCII, 3 with the special letters), FIX-A and FIX-B:  newly visible BODY inputs = 0 in all 12 runs
  (e.g. FIX-A seed=2: 'newly:name': 2188, 'newly:name+sep': 368, 'newly:keyname+pad': 22, 'newly:keyname+name+pad': 3 — no body key)
grid 71,280: fixa {'closed': 26896, 'both_leak': 23866, 'new_leak': 0, 'nonidem_new': 0}; fixb {'closed': 27632, 'both_leak': 23130, 'new_leak': 0, 'nonidem_new': 0} (R-3 residue 736 -> 0)
ledger cases through treefixa/treefixb: R-1 10/10 and R-2 4/4 and R-4 5/5 rows body-free, replay OK, idem; R-3: fixa 4 rows leak (as the PIN), fixb 1 (the '==' form)
chain-guard boundaries (guard4/guard4b) with FIX-B: shapes: 3312 {'same': 1928, 'better': 1384}; {'end-of-text same': 123, 'end-of-text better': 42, 'cut same': 3171, 'cut better': 924}
goldens: the seven digests unchanged; probe states 226 == PIN; fixture strings 0 changed; idempotence 40,000 states 0 NON-IDEMPOTENT; cost linear (max ratio 2.12 / 2.25)
```
What FIX-A leaks or refuses: it refuses nothing (no row refused anywhere above). It leaks what the PIN leaks where its guard
keeps the PIN form: a value glued to `bearer` (`task-password:QZJ8QZJ8bearer …` shows `QZJ8QZJ8`, as at the PIN; the new V hid
it) and the KNOWN D-3/F-1 shapes; the `keyname` tails (D-1's class) stay. FIX-B also leaves R-3's `==` padding form open
(branch A's padding rule, written for bearer, would need an sk-only branch). Not measured: FIX-A/FIX-B against the builder's
full 30-mutant table (18 rebuilt mutants were run on the new V, not on the fixes), and no new test rows were written (out of my
boundary).

## 11. Item 9 — gates (final run, one foreground call)

```
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-09-23T16:15:55Z
shared-tree volatile blob: bf04415d72c1eb788e17d0b1e877bc8fdb23dbc5
$ for i in 1 2; do /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py -q -p no:cacheprovider --basetemp=/tmp/vj11r2/bt/final$i -rA; done
run 1 rc=0 :: 121 passed in 4.29s :: PASSED-lines=121 sha=2475237d4d259cce
run 2 rc=0 :: 121 passed in 4.33s :: PASSED-lines=121 sha=2475237d4d259cce       (the builder's g1/g2: sha=2475237d4d259cce — the same 121 ids)
$ bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py
2 files set=16a7b628685e
$ cd /tmp/vj11r2/pinwt   (git worktree at d556c9b + the new V + the import-path guard)
pinwt: HEAD=d556c9b volatile=bf04415d72c1 canonical-tests=0afbf1b821ed ledger-tests=4a8bccead05f
73 passed in 2.86s      rc=0      (the PIN's own 72 + the guard)
$ /root/venv-agent-factory/bin/python -m pyflakes <the three boundary files>                     pyflakes-rc=0
$ python3 scripts/ap_screen.py src/agent_factory/decisions/volatile.py                           --- AP_SCREEN over 1 path(s): 0 hits over 1 files ---
$ python3 scripts/ap_screen.py --tests tests/test_decisions_canonical.py tests/test_decisions_ledger.py
--- TEST_SCREEN over 2 path(s): 1 hits over 2 files ---
AP-70: 1
    tests/test_decisions_ledger.py:1292: except Exception:          (the PIN's own `except Exception` line, as the builder reported)
```
Item 9 verdict: the gates the builder and the coordinator ran reproduce. They are green, and they do not see R-1, R-2, R-3 or R-4.

## 12. Stale-context sweep (statements my findings falsify; I edit none of them)

- `src/agent_factory/decisions/volatile.py:45-46` (the `D-057` comment) "each fires where its PIN form fires": false for `_BEARER` on U+0130/U+0131/U+017F (R-1).
- `src/agent_factory/decisions/volatile.py:52-54` "The run does not yield when" the value holds another head, "so the run keeps its PIN form": true of the value as the guard sees it, false for the value `_ENVVAL`/`_ENVVAL_WIDE` later take (R-4) and for a token
  run with a special letter (R-2).
- `src/agent_factory/decisions/volatile.py:64-65` "an upper-case NAME= is _ENVVAL's, whose \S+ value runs further": false for `NAME= v` (a space after `=`), R-3.
- `tasks/briefs/laya/J1-1-R2-report.md:98` "cannot expose a body byte the PIN redacts" (its by-construction argument, lines 98-102), `:239` "Each class fires where its PIN form fires", `:542` "Over 160,000 fuzz inputs these are the ONLY
  PIN-redacted bytes that now show: name words … and that `=`": falsified by R-1, R-2, R-4 (the by-construction argument misses
  the flag scope and the bearer pass that runs between the guard and the value classes).
- `docs/INCIDENT-LOG.md:559` (`AF-AP-157`) "closed for plain values by J1-1-R2": R-3 is V-1 on plain values
  (`task-DB_PASSWORD= v`, `Bearer …API_KEY= v`), still open.
- `todo/BUILD-TASKLIST.md:1351` quotes "0 new exposures in a 160,000-input byte fuzz" as the LANE's report (attributed, so not a
  false ledger claim); the property it reports does not hold (R-4 in ASCII).
- `fb016d0`'s message: "D-1 (a secret NAME stays visible after the placeholder) is accepted: B2 covers values": the accepted
  bytes include a value's own tail when a key or token ends in a name spelling (section 4, point 3; INFO).

## 13. The blockers, reproduced with one self-contained command (no scratch tool)

`/tmp/vj11r2/repro.py <src dir>` (32 lines: the four shapes as `b1.finding_sev.msg` through `make_row` -> `append` -> the line on
disk -> `replay`; FAKE bodies). Run on the shared tree (= the PIN fb016d0) and on `git archive d556c9b src`:
```
== fb016d0 (the shared tree)
volatile: /home/user/agent-factory/src/agent_factory/decisions/volatile.py
R-1 body-in-ledger-line=True  state.msg='Authorization: Bearer QZJ8QZJ8ıQZJ8QZJ8QZJ8QZJ8QZJ8'
R-2 body-in-ledger-line=True  state.msg='<redacted:sk>token <redacted:token>: X4Z9X4Z9X4Z9'
R-4 body-in-ledger-line=True  state.msg='ta<redacted:sk>password:<redacted:envval> X4Z9X4Z9X4'
R-3 body-in-ledger-line=True  state.msg='ta<redacted:sk>= QZJ8QZJ8QZJ8QZJ8QZJ8'
replayed rows: 4
== d556c9b (git archive)
volatile: /tmp/vj11r2/pinsrc/src/agent_factory/decisions/volatile.py
R-1 body-in-ledger-line=False state.msg='Authorization: <redacted:bearer>'
R-2 body-in-ledger-line=False state.msg='<redacted:sk> QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8ıpassword: <redacted:envval>'
R-4 body-in-ledger-line=False state.msg='ta<redacted:sk>:QZJ8QZJ8<redacted:bearer>token: <redacted:envval>'
R-3 body-in-ledger-line=True  state.msg='ta<redacted:sk>= QZJ8QZJ8QZJ8QZJ8QZJ8'
replayed rows: 4
```
The script, verbatim (FAKE bodies; run from anywhere with the venv interpreter and a `src` directory as its argument):
```python
import sys, os, json, tempfile
sys.path.insert(0, sys.argv[1]); import agent_factory.decisions.volatile as v; print("volatile:", v.__file__)
from agent_factory.decisions.ledger import make_row, append, replay
SRC = {"kind": "incident_log", "path": "docs/INCIDENT-LOG.md", "source_digest": "a" * 64}
ROWS = [("R-1", "Authorization: Bearer QZJ8QZJ8ıQZJ8QZJ8QZJ8QZJ8QZJ8", "QZJ8QZJ8"),
        ("R-2", "sk-abcdefgh-token " + "QZJ8" * 8 + "ıpassword: X4Z9X4Z9X4Z9", "X4Z9X4Z9X4Z9"),
        ("R-4", "task-password:QZJ8QZJ8bearer abcdefghijklmnop==token: X4Z9X4Z9X4", "X4Z9X4Z9X4"),
        ("R-3", "task-DB_PASSWORD= QZJ8QZJ8QZJ8QZJ8QZJ8", "QZJ8QZJ8")]
d = tempfile.mkdtemp(dir="/tmp"); led = os.path.join(d, "l.jsonl")
for rid, msg, body in ROWS:
    row = make_row(producer="decide-harvest/incident-log", question_id="b1.finding_sev", raw_state={"file": "src/a.py", "kind": "k", "msg": msg},
                   incumbent_answer="accepted", source_ref=dict(SRC, locator=rid), root=None)
    append(led, row); line = open(led, encoding="utf-8").read().splitlines()[-1]
    print(f"{rid} body-in-ledger-line={body in line!s:5s} state.msg={json.loads(line)['state']['msg']!r}")
print("replayed rows:", len(replay(led)))
```

## 14. Finding inventory (no severity filter; numbered; disposition by the blocking predicate)

| # | Class | Finding | Evidence | Contract mapping | Canonical path | Material effect | Reproduction | Suggested fix |
|---|---|---|---|---|---|---|---|---|
| 1 | **BLOCKER** | R-1: `_BEARER`'s run and lookahead lost the PIN's case-insensitivity (global `(?i)` scoped to `(?i:bearer)`, `src/agent_factory/decisions/volatile.py:74-76`); a bearer token holding U+0130/U+0131/U+017F is no longer redacted (whole, or its tail) | VERIFIED: both trees, 2 schemas, `replay` accepts; field sweep 884 `ok->LEAK` rows over 20 fields; ~1,950 per 20,000 special-letter generator inputs (with R-2/R-4) | B2 "Every value the PIN redacts stays redacted"; D-057 "no value the PIN redacts may leak after" | `decision_state` -> `canonical` -> `make_row` -> `append` -> file -> `replay`, at fb016d0 | A PIN-redacted token reaches the append-only ledger. The input needs one of three NFC-stable non-ASCII letters inside the token (not RFC 6750; a Turkish-locale case mapping of a token yields U+0130/U+0131): rare | section 13 `R-1`; section 2 | FIX-A line 75: `(?i:[A-Za-z0-9._~+/-])` in the lookahead and the run (measured, section 10) |
| 2 | **BLOCKER** | R-2: `_YIELD`'s token branch checks its value and scans for a second head with a case-SENSITIVE `[A-Za-z0-9+/]` (`src/agent_factory/decisions/volatile.py:71-72`) while `_TOKEN`'s run is case-insensitive (`src/agent_factory/decisions/volatile.py:85`); a special letter in the run hides the next `NAME[:=]` from the guard and the SECOND value is freed | VERIFIED: 3 shapes + ASCII control, both trees, `replay` 4/4 | B2; the brief's item 4 ("any shape where the guard makes the output worse than the PIN") | same | The PIN-redacted second value reaches the ledger; needs a special letter inside a token run glued to a second head: rare | section 13 `R-2`; section 2 | FIX-A line 72: `(?i:[A-Za-z0-9+/])` in the value check and the guard scan (measured) |
| 3 | **BLOCKER** | R-4: the chain guard decides on the value as the sk/bearer pass sees it; `_BEARER` then merges across the space inside `bearer <token>`, and `_ENVVAL`/`_ENVVAL_WIDE` take the merged value, swallow the next head and free its value (`src/agent_factory/decisions/volatile.py:61`, `:67-73`, the pass order `:361-365`) | VERIFIED: 9 of 60,000 ASCII generator inputs (all listed, two instruments agree), 3 minimal shapes + a control through `wf.drift.observed`, `replay` 5/5 | B2; item 4 | same | The PIN-redacted second value reaches the ledger in pure ASCII; needs a value that runs into the word `bearer` (glued, or `cupbearer`) and a bearer token that ends in `=` padding or a glue byte (`:` `)` `@` …) before the next head: contrived | section 13 `R-4`; section 4 | FIX-A line 61: `\|(?i:bearer)\s` in `_ASSIGNMENT_HEAD` (measured; these shapes then give the PIN's output) |
| 4 | FOLLOW-UP | R-3: a V-1 residue — an upper-case `NAME= v` (a space after `=`) or `NAME==v` behind sk/bearer still frees the value, at the PIN and after (`src/agent_factory/decisions/volatile.py:69` `(?!_ENVVAL_HEAD)`; `:68` `(?=[^\s=])`) | VERIFIED: 736 grid rows; ledger 7/7, both trees | Not B1 (its eight rows close). J1-1-R1 A4 (in force) promises a prefixed name's value becomes envval; D-057 scoped "closing V-1" to the eight rows, so blocking on it would expand the frozen contract: the coordinator's call | same | A value reaches the ledger (pre-existing, no regression); falsifies AF-AP-157's "closed for plain values" | section 13 `R-3`; section 3a | FIX-B line 69: `(?!_ENVVAL_HEAD\S)` (measured: 736 -> 0, no new leak); the `==` form needs an sk-only padding rule (not built). Fold into the same repair |
| 5 | INFO | D-1's premise does not hold for every visible "name": when a key's or token's body ENDS in a name spelling followed by a separator and a value, those tail bytes (<= 8, from the 22-spelling dictionary) and bearer padding now show (29-35 per 20,000 ASCII inputs) | VERIFIED (section 4, point 3) | D-1 accepted by the coordinator ("B2 covers values") | same | A few bits of a token (a dictionary word), never its random part | section 4 example | None cheap: the text is ambiguous. Record the refinement in D-1's ruling |
| 6 | FOLLOW-UP | Test gaps: my mutants V-M3 (token branch `(?i:)` dropped), V-M11 (`(?<=_)` dropped in the token branch) and V-M4 (the head's token alternative case-sensitive) each reopen a leak and survive all 121 tests | VERIFIED (section 8) | The J1-1-R2 brief's m4 list (removals) is met; these are flag/lookbehind variants it did not name | n/a (tests) | A future edit can reopen `…-TOKEN <run>`, `…_token <run>` or the chain `…=abc_TOKEN <run>` unseen | section 8 discriminators | Three class rows: `desk-access-TOKEN <run>`, `desk-access_token <run>`, `mask-PASSWORD=abc_TOKEN <run>` |
| 7 | INFO | Mirror-precision survivors with no body effect: V-M6 (widened value check `{7}`), V-M7 (bearer `{16}`->`{15}`, an over-redaction), V-M10 (`API_?KEY`->`API_KEY` splits the name) | VERIFIED | none | n/a | none on bytes | section 8 | optional exact-output rows |
| 8 | INFO | B4 holds: 7 golden digests unchanged, 226 probe states == PIN and fixed points, 6,077 fixture strings unchanged; but no committed fixture string holds anything the redactor changes | VERIFIED (section 6) | B4 | the real `state_digest` | none | `b4_worker.py` | none |
| 9 | INFO | B5 holds: linear 16k..256k on 14 adversarial generators; the sk/bearer pass costs ~100x the PIN per character (47.23 ms vs 0.45 ms at 256k); `_redact_str` ~1.2-1.6x | VERIFIED (section 7), shared box | B5 | `.sub` and `_redact_str` | none | `cost6.py` | none |
| 10 | INFO | The builder's evidence reproduces: 18 of its mutants rebuilt from its table, identical killer sets by node id, every killer set green unmutated; tests, driver, the PIN's own tests, goldens | VERIFIED (sections 1, 8, 11) | — | — | — | — | — |
| 11 | INFO | Why the builder's fuzz missed 1-3: ASCII-only (disclosed) and no value glued to `bearer`; its by-construction argument omits the flag scope and the rewrite `_BEARER` makes between the guard and the value classes | INFERRED from its sections 1, 14 + my findings | — | — | — | — | future fuzz: NFC-stable non-ASCII letters; glued class words |
| 12 | FOLLOW-UP | Stale context (section 12): `src/agent_factory/decisions/volatile.py:45-47` (the `D-057` comment block, also its lines 52-54 and 64-65); the builder's report (its lines 98-102, 239, 542); AF-AP-157's "closed for plain values" (`docs/INCIDENT-LOG.md:559`) | VERIFIED (grep + findings) | the repo's own honesty rule (a doc that flatters is a hollow green) | — | misleads the next reader | section 12 | fix in the same change as the repair |
| 13 | INFO | Item 8 (task #198's candidate rule): closes F-1's four widened shapes; D-3 only with the guards removed; opens a stub-exposure class (3.4-3.7 % of ASCII generator inputs; `password: mykey=X4Z9Q` whole); R8a passes all 121 tests | VERIFIED (section 9) | informational | `_redact_str` | — | `r8_measure.py`, `diff3.py` | #198 must redact a head-stopped value regardless of the floor, and add tests for that class |
| 14 | KNOWN | AF-AP-157 F-1 and D-3: the five chained shapes, identical at the PIN d556c9b and after | VERIFIED (section 1) | KNOWN (never blocks) | — | — | — | task #198 |
| 15 | KNOWN | Issues #49 (V-2…V-6, V-15, V-16, V-12…V-14) and #47: not re-derived; the 8-character floor rows of my grid (23,130) and the 43-table's V-6/V-7 rows sit there | not re-derived | KNOWN | — | — | — | — |
| 16 | INFO | Echo sweep for R-1/R-2's class: the committed transcript scrubber (`scripts/transcript_export.py`@HEAD) sets `re.I` only on its bridge-link rule and has no mirror design, and its Bearer rule keeps `Bearer\s+` (no R-4 merge); `proofs/S0-04/tools/pc/capture_leg.py:46` is a leak DETECTOR (over-matching is safe) | VERIFIED (read-only grep; S198A's in-flux working copy not read) | none | — | — | — | — |
| 17 | INFO | Suffix-extended names (`keys:`, `tokens:`, `passwords=`, `secretary:`, `keyboard:`) are no assignment in any class and keep the PIN's output; prefix-extended (`monkey:`, `turkey=`) are better than the PIN; the four enum fields refuse a secret-bearing value (`decision-state-bad-enum`) | VERIFIED (`b1extra.py`) | — | — | — | — | — |

## 15. Reproduced, reviewed statically, skipped

- REPRODUCED (run in this lane, output pasted): the premise (blob ids, line map, both test runs and the set id, the driver, the
  PIN's own tests against the new V, the five chained shapes); R-1..R-4 through the real ledger path in both trees; the grid
  (71,280), the field-and-cut sweep (17,078 rows per tree), the differential (6 x 20,000 per variant, two instruments), the
  guard boundaries (7,572 shapes), B4 (goldens, probe, fixture strings, 40,000-state idempotence per variant), the cost table
  (14 generators x 4 variants x 16k..256k), 18 rebuilt builder mutants + 13 of my own, the candidate fix FIX-A/FIX-B, the
  item-8 rule R8a/R8b, the final gates. The builder's 30-row killer sets are a subset of the 121 tests, which pass twice.
- REVIEWED STATICALLY: the linear-cost argument (section 7, backed by the timings); why the builder's fuzz missed R-1/R-2/R-4
  (row 11); the realism of each blocker's input (rows 1-3: rare, stated as judgement, not measured against real ledgers).
- REPORT LINT (not required of this lane; two fix rounds on my own references): `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/VERIFY-J1-1-R2-report.md --root .` -> `report_lint: 21 refs — OK 21, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.
- SKIPPED, with reason: the builder's 12 single-name mutants m4n-*/m4u-* (single-name deletions; covered by its own table and
  by the V-M1/V-M10 family); issue #47 and #49's rows (KNOWN, not re-derived); the transcript scrubber's in-flux working copy
  (S198A's boundary; only the committed version was read); the full-tree suite (not asked; the brief's gates are the two
  files); `report_lint.py` on this report (not asked of this lane); the PC (the rules forbid it here).

## 16. NOT done (first-class)

- No fix was applied to the tree; FIX-A/FIX-B exist only as scratch copies and were not run against the builder's full 30-row
  mutant table or given test rows. No test was written (my boundary is this report).
- No real ledger or real document was scanned for how often R-1/R-2/R-4 inputs occur; their rarity is argued, not measured.
- The R-3 `==` padding form has no measured fix.
- No commit, stage, stash or push; no PR, issue or comment; no bridge use; no subagent.

## 17. GATE RECOMMENDATION

**NOT-READY** — blockers R-1, R-2 and R-4 (findings 1-3). Each meets the whole predicate: B2-mapped ("every value the PIN
redacts stays redacted"); reproduced through `decision_state` -> `make_row` -> `append` -> the line on disk -> `replay` at fb016d0
(section 13, one self-contained command, PIN comparison included); material (a value the PIN d556c9b redacted reaches the
append-only ledger; the builder's "0 new exposures" is false); a concrete discriminator (the command above, and FIX-A as the
corrected variant); in-boundary (`src/agent_factory/decisions/volatile.py:61` `_ASSIGNMENT_HEAD`, and lines 71-72 and 74-76 of the same file). Everything in this recommendation was reproduced; the one
judgement in it is materiality: every blocker needs a rare input (a U+0130/U+0131/U+017F inside a token for R-1/R-2; a value
glued to the word `bearer` for R-4). A measured repair exists: FIX-A, three one-line changes, which passes the 121 tests, the
PIN's 72, the driver, the goldens, idempotence, linear cost and 120,000 differential inputs with 0 body exposures. FIX-B adds
R-3. Whether a third J1-1 repair fits the D-031 budget, or the coordinator accepts these rare-input regressions as recorded
follow-ups, is the coordinator's decision. KNOWN rows (F-1, D-3, issues #49 and #47) did not weigh on this recommendation.
