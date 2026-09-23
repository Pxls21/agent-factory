# VERIFY-C1-R1 — targeted adversarial verify of the C1-R1 repair (`scripts/verify_command.py`, task #160)

**Lane:** VERIFY-C1-R1, sandbox `adversarial-verifier` (Opus 5.5). **PIN:** `ee66397` (V and T byte-identical to the C1-R1
landing `0e1deb2`). **Aliases:** `V` = `scripts/verify_command.py`, `T` = `tests/test_verify_command.py`. **Brief:**
`tasks/briefs/canny/VERIFY-C1-R1-brief.md` (origin `09792f4`). Written incrementally from 2026-09-23 06:10Z.
Scratch: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vc1r1/` (called `$S` below).

## OUTCOME

**GATE RECOMMENDATION: `MERGE-READY-WITH-FOLLOWUPS`** (full line under "GATE RECOMMENDATION" below). No blocker: every
contract item (C1-A2 (a)-(e), R1-R8) holds and was reproduced through the real CLI with bash as the oracle; Canny's frozen
tables are 328/328 unchanged against the PIN `3f531c4` (my own comparator, red on three planted changes).

- **Premise:** every line reproduces (§1). No CONTRACT-INVALID.
- **D1 / D2:** FOLLOW-UP each: both follow the contract's letter, are Canny-faithful, and are declared and pinned.
  The builder's fixes graded against bash (§3): **L-PF** closes 6 of 14 hollow shapes and adds 2 false negatives.
  **L-TR** closes 2 of 11 and refuses 4 status-preserving commands (two are the temp-directory cleanup idiom).
  My **L-PF2** closes 14 of 14 and adds no false negative on 21 legitimate shapes (it keeps Canny's 3). My **WPG**
  removes 3 of the 4 hollow
  `with_pipefail` rewrites. No candidate moves a frozen answer.
- **New, undeclared (F-2):** the pipefail scan still accepts a VT, FF or newline inside `set -o pipefail`
  (8 shapes). This is the VERIFY-C1 F2 mechanism in ASCII form; it is inherited, not a regression. First follow-up.
- **Declared limits:** all eight pins are live (each closed by my own fix → its strict xfail XPASS-fails, 65 others
  green); every docstring bullet has a pin (§5).
- **Mutants:** 28 new: 13 killed, 1 equivalent (searched, 0 of 205,335 pairs differ), 14 survived with live
  discriminators. Three of the survivors reopen a hollow green that T does not pin (F-4). The brief's required mutants are
  killed, except the in-loop reorder (equivalent), the unstripped-command feed (survives, cheap direction only) and the
  missing `with_pipefail` re-check (survives) (§6).
- **Gates:** `65 passed, 8 xfailed` twice from the root and once from `/tmp`, set `d9bd6dad2d0e`; pyflakes and both
  screens clean (§7).

## 1. PREMISE — re-measured (item 1): every line reproduces; no mismatch

Sandbox, `/home/user/agent-factory`, HEAD `09792f4` (the brief's own commit; `git diff --stat ee66397 HEAD` over V, T and
the builder's report is empty, and so is the working tree against HEAD).

```
$ identities (sha256[:16] lines path), git show ee66397:<path> and the working tree agree
d9f71bb3962bdb4a 351 scripts/verify_command.py
195c1b6378adaad8 490 tests/test_verify_command.py
769a2b90023c422e 515 tasks/briefs/canny/C1-R1-report.md
$ git diff --stat 0e1deb2 ee66397 -- scripts/verify_command.py tests/test_verify_command.py      (empty)
$ bash scripts/pc_suite.sh set-id -- tests/test_verify_command.py     (set_id is local: scripts/pc_suite.sh:46 `set_id()`, no bridge call)
1 files set=d9bd6dad2d0e
$ (repo root, run 1) /root/venv-agent-factory/bin/python -m pytest tests/test_verify_command.py -q -p no:cacheprovider --basetemp=$S/gate/bt1
65 passed, 8 xfailed in 0.46s     rc=0
$ (repo root, run 2) ... --basetemp=$S/gate/bt2
65 passed, 8 xfailed in 0.49s     rc=0
$ (cd /tmp && /root/venv-agent-factory/bin/python -m pytest /home/user/agent-factory/tests/test_verify_command.py -q -p no:cacheprovider --basetemp=$S/gate/bt3)
65 passed, 8 xfailed in 0.50s     rc=0
$ --collect-only
73 tests collected in 0.02s
$ /usr/bin/python3 $S/shapes.py $S/stub3     (the C1-R1 brief's script; H3's U+00A0 written as a Python escape; bash under env -i)
H1    port=does-not-count   port_rc=1 bash_rc=0  'pytest && false || true'
H1b   port=does-not-count   port_rc=1 bash_rc=0  'pytest && echo ok || true'
H2    port=does-not-count   port_rc=1 bash_rc=0  "trap 'exit 0' EXIT; pytest"
H3    port=does-not-count   port_rc=1 bash_rc=0  'set\xa0-o pipefail; pnpm test | tail'
H4    port=does-not-count   port_rc=1 bash_rc=0  'set -o pipefail\r\npnpm test | tail'
H5    port=does-not-count   port_rc=1 bash_rc=0  'echo \\\npytest'
H6    port=does-not-count   port_rc=1 bash_rc=0  'exec true; pytest'
H6b   port=does-not-count   port_rc=1 bash_rc=0  'coproc pytest'
CTRL  port=counts           port_rc=0 bash_rc=3  'pytest'
CTRL2 port=counts           port_rc=0 bash_rc=3  'set -o pipefail; pnpm test | tail'
$ the rule-(a) mutant (V:147 `"||" in last  # (a)` -> `False  # (a)`), my driver $S/mutdrv.py, scratch tree
PREM-a  KILLED  compiles=yes collected=73 | 2 failed, 63 passed, 8 xfailed   -> [a_H1], [a_H1b]
$ D1, strings built in Python; PIN = git show 3f531c4:scripts/verify_command.py (8420e9a202de6afb); FINAL = V
'set -o pipefailé; pnpm test | tail'   PIN=does-not-count(1)  FINAL=counts(0)  bash_rc(fail)=0 (C.UTF-8 and no LANG) bash_rc(pass)=0
'set -o pipefail-x; pnpm test | tail'  PIN=counts(0)          FINAL=counts(0)  bash_rc(fail)=0
'set -o pipefail\xa0; pnpm test | tail' PIN=counts(0)         FINAL=counts(0)  bash_rc(fail)=0
   bash stderr: "set: pipefailé: invalid option name" (and pipefail-x, pipefail\xa0 alike)
$ D2
with_pipefail("trap 'exit 0' EXIT; pytest | tail") -> "set -o pipefail && trap 'exit 0' EXIT; pytest | tail"
is_verify(that rewrite) -> True ; bash (pytest stubbed to exit 3) rc=0 ; CLI --with-pipefail prints it, rc=0
$ python3 scripts/report_lint.py --min-refs 12 --map V=scripts/verify_command.py --map T=tests/test_verify_command.py tasks/briefs/canny/C1-R1-report.md --root .
report_lint: 96 refs — OK 96, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
```

Instruments (all mine, in `$S`): `shapes.py` (the brief's oracle); `stub3/`, `stub0/` (26 check words each, `#!/bin/sh` +
`exit 3` / `exit 0`); `mutdrv.py` (each mutant is its own `scripts/` + `tests/` tree so T's `parents[1]` at T:20 resolves to
it; every substitution must match exactly once; V and T are `py_compile`d and T must collect 73, else INVALID — AF-AP-78).
Interpreters are pinned by absolute path (`/usr/bin/python3`, `/bin/bash`, `/usr/bin/env -i`); a stub `PATH` exists only
inside the one `env -i` bash call (AF-AP-134). bash is `GNU bash, version 5.2.21(1)-release`, Python `3.11.15`.

## 2. The contract through bash (item 2) — every rule holds; the frozen tables are unchanged; the comparator can go red

`$S/triple.py` runs each command through V's API **and** the real CLI (`/usr/bin/python3 scripts/verify_command.py --
CMD`; the harness asserts the two agree on every row), through the PIN V (`3f531c4`), through **my own node oracle**
(`$S/canny_oracle.js`: Canny's `isVerify`/`withPipefail` control flow written by me, the regex literals spliced in as
text from `checks.ts` lines 9-11, 36, 39, 42, 50, 62, 72, 92; nothing from Canny imported or run), and through bash with
every check stubbed to exit 3 (`rc_fail`) and to exit 0 (`rc_pass`). HOLLOW = V counts while `rc_fail` is 0; FN = V refuses
a status-preserving command (`rc_fail` non-zero, `rc_pass` 0), the cheap direction.

### 2a. C1-A2 (a)-(e): closed shapes refused, matching status-preserving shapes still counted

```
$ /usr/bin/python3 $S/item2.py $S          (41 rows; V = final, PIN = 3f531c4, Canny = my JS oracle)
a-c1   V=refuses PIN=counts  Canny=counts  rc_fail=0    rc_pass=0    ok     'pytest && false || true'
a-c2   V=refuses PIN=counts  Canny=counts  rc_fail=0    rc_pass=0    ok     'pytest && echo ok || true'
a-c3   V=refuses PIN=refuses Canny=refuses rc_fail=0    rc_pass=0    ok     'set -o pipefail; pnpm test | tail || true'
a-k1   V=counts  PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    ok     'command -v pytest || exit 1; pytest'
a-k2   V=counts  PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    ok     'pytest && echo ok'
a-fn   V=refuses PIN=refuses Canny=refuses rc_fail=3    rc_pass=0    FN     'false || pytest'
b-c1   V=refuses PIN=counts  Canny=counts  rc_fail=0    rc_pass=0    ok     "trap 'exit 0' EXIT; pytest"
b-c2   V=refuses PIN=counts  Canny=counts  rc_fail=0    rc_pass=0    ok     "cd /tmp; trap 'exit 0' EXIT; pytest"
b-c3   V=refuses PIN=counts  Canny=counts  rc_fail=0    rc_pass=0    ok     "trap 'exit 0' ERR\npytest"
b-k1   V=counts  PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    ok     'true trap; pytest'
b-k2   V=counts  PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    ok     'TRAP=1 pytest'
b-fn   V=refuses PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    FN     "trap 'echo done' EXIT; pytest"
c-c1   V=refuses PIN=counts  Canny=counts  rc_fail=0    rc_pass=0    ok     'set -o pipefail\r\npnpm test | tail'
c-c2   V=refuses PIN=counts  Canny=counts  rc_fail=0    rc_pass=0    ok     'set -o pipefail\r; pnpm test | tail'
c-k1   V=counts  PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    ok     'set -o pipefail\npnpm test | tail'
c-k2   V=counts  PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    ok     'pytest "a\rb"'
c-k3   V=counts  PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    ok     'pytest # note\r'
d-c1   V=refuses PIN=counts  Canny=counts  rc_fail=0    rc_pass=0    ok     'echo \\\npytest'
d-c2   V=refuses PIN=counts  Canny=counts  rc_fail=0    rc_pass=0    ok     'echo \\\n  pytest'
d-k1   V=counts  PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    ok     'echo hi\npytest'
d-k2   V=counts  PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    ok     'echo "a\\\nb"; pytest'
d-fn   V=refuses PIN=refuses Canny=refuses rc_fail=3    rc_pass=0    FN     'pytest \\\n --maxfail=1'
d-fn2  V=refuses PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    FN     'echo \\\\\npytest'
e-c1   V=refuses PIN=counts  Canny=counts  rc_fail=0    rc_pass=0    ok     'exec true; pytest'
e-c2   V=refuses PIN=counts  Canny=counts  rc_fail=0    rc_pass=0    ok     'coproc pytest'
e-c3   V=refuses PIN=counts  Canny=counts  rc_fail=0    rc_pass=0    ok     'cd /tmp; exec true; pytest'
e-k1   V=counts  PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    ok     'executor=1; pytest'
e-fn   V=refuses PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    FN     'exec pytest'
e-fn2  V=refuses PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    FN     'exec 2>&1; pytest'
r1-194 V=refuses PIN=counts  Canny=counts  rc_fail=0    rc_pass=0    ok     'set\xa0-o pipefail; pnpm test | tail'
r1-194k V=counts  PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    ok     'set -o pipefail; pnpm test | tail'
r1-174 V=refuses PIN=counts  Canny=counts  rc_fail=0    rc_pass=0    ok     'pytest\xa0#; exit 0'
r1-174k V=counts  PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    ok     'pytest #; exit 0'
r1-90  V=counts  PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    ok     'npm testé'
r1-99  V=counts  PIN=counts  Canny=counts  rc_fail=127  rc_pass=127  ok     'tscé'
r1-118 V=refuses PIN=refuses Canny=refuses rc_fail=127  rc_pass=127  ok     'echoé tsc'
r1-124 V=counts  PIN=counts  Canny=refuses rc_fail=127  rc_pass=127  ok     'tsc\xa0--help'
r1-140 V=refuses PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    FN     "trapé 'exit 0' EXIT; pytest"
r1-141 V=refuses PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    FN     'execé true; pytest'
r1-160 V=refuses PIN=refuses Canny=counts  rc_fail=127  rc_pass=127  ok     'npm\xa0test'  patterns=['^npm\\stest$']
r1-160k V=counts  PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    ok     'npm test'  patterns=['^npm\\stest$']
tally: {'ok': 33, 'FN': 8}
```

Every rule refuses each closed shape, including shapes the builder's T does not carry (`a-c3`, `b-c2`, `b-c3`, `c-c2`,
`d-c2`, `e-c3`); every matching status-preserving shape still counts. The 8 FN rows are the cheap direction the letter
buys: (a) refuses any `||` in the last segment (`false || pytest`), (b) any `trap` at a segment start
(`trap 'echo done' EXIT` keeps the status), (d) a real continuation of the check, (e) `exec pytest`, and the declared
`exec 2>&1` / escaped-backslash pair (V:33-35, `exec 2>&1; pytest`).

### 2b. R1 — `re.ASCII` on every site (static) and each flag-sensitive probe (above, rows `r1-*`)

`ast` over V lists 15 `re` call sites; every one carries the flag, passed by keyword wherever a positional slot would
be `count` or `maxsplit`:

| site | pattern | flag | answer-changing probe (row above) | bash |
|---|---|---|---|---|
| V:89-115 | `VERIFY = [` (3 patterns) | `re.ASCII` | `r1-90` `npm testé` counts; `r1-99` `tscé` counts | rc 3/0; rc 127 |
| V:118 | `_PRINTS_OR_INSPECTS` | `re.ASCII` | `r1-118` `echoé tsc` refused | rc 127 |
| V:124 | `_ASKS_ONLY` | `re.ASCII` | `r1-124` `tsc\xa0--help` counts; T:222-225 pins it (`def test_nbsp_before_help_does_not_trigger_asks_only`, a real U+00A0 byte pair) | rc 127 |
| V:127 | `_NEGATED` | `re.ASCII` | none: every part is `str.strip()`ped first, which removes a superset of `\s` | — |
| V:140, V:141 | `_TRAP`, `_EXEC_OR_COPROC` | `re.ASCII` | `r1-140`/`r1-141` `trapé …`, `execé …` refused | FN, rc 3/0 |
| V:160 | user `patterns` | `re.ASCII` | `r1-160` `npm\xa0test` refused under `^npm\stest$` (Canny counts) | rc 127 |
| V:172 | quoted-string strip | `flags=re.ASCII` | inert (no `\b\w\s\d`, no IGNORECASE): 0 differences over 1,112,064 code points × 3 contexts | — |
| V:174 | comment strip | `flags=re.ASCII` | `r1-174` `pytest\xa0#; exit 0` refused (closes a PIN hollow green); `pytest #; exit 0` counts | rc 0/0; rc 3/0 |
| V:194-196 | pipefail scan | `flags=re.ASCII` | `r1-194` H3 refused; CTRL2 counts | rc 0/0; rc 3/0 |
| V:200 | segment split | `flags=re.ASCII` | inert: 0 differences, same sweep | — |
| V:223 | lone `&` | `flags=re.ASCII` | inert: 0 differences, same sweep | — |
| V:257 | `with_pipefail` tail test | `flags=re.ASCII` | `with_pipefail("npm test |\xa0tail -5")` → `None` (PIN and Canny rewrite it) | — |

The docstring (V:7-17, `every regex here runs with`) states exactly this. **R1 holds.** The flags that change an answer
but carry no T row are listed in §6 (mutants R1-VERIFY1, R1-USER, R1-PRINTS, R1-TRAP).

### 2c. `with_pipefail` through bash

```
$ /usr/bin/python3 $S/wp.py $S      (final V; PIN and Canny shown as "same" when equal; bash run on the rewrite)
'npm test |\xa0tail -5'                  final=None                                           pin='set -o pipefail && npm test |\xa0tail -5' canny=(same as pin)
'npm test | tail -5'                     final='set -o pipefail && npm test | tail -5'        pin=same canny=same bash(rewrite) fail/pass=(3, 0)
'npm test | tailé'                       final='set -o pipefail && npm test | tailé'          pin=None canny=same bash(rewrite) fail/pass=(127, 127)
'npm test | head -5'                     final=None                                           pin=same canny=same
"trap 'exit 0' EXIT; pytest | tail"      final="set -o pipefail && trap 'exit 0' EXIT; pytest | tail"         pin=same canny=same bash(rewrite) fail/pass=(0, 0)
'exec true; pytest | tail'               final='set -o pipefail && exec true; pytest | tail'                  pin=same canny=same bash(rewrite) fail/pass=(0, 0)
"true && trap 'exit 0' EXIT; pytest | tail" final="set -o pipefail && true && trap 'exit 0' EXIT; pytest | tail" pin=same canny=same bash(rewrite) fail/pass=(0, 0)
'pytest; echo done' / 'echo hi | tail'   final=None                                           pin=same canny=same
```

Three rewrites are hollow greens (rows 5-7): D2 (§3). Row 6 is the (e) analogue of the declared D2 example and has no pin.

### 2d. The CLI refusals R5-R7 (`$S/cli.py`; `/usr/bin/python3 scripts/verify_command.py …`, env `PATH=/usr/bin:/bin` unless shown)

```
R5-3w    rc=2 stdout=b''  stderr_lines=1 'COMMAND must be one argument, got 3; quote it'   ['--', 'python', '-c', 'import pytest']
R5-2w    rc=2 stdout=b''  stderr_lines=1 'COMMAND must be one argument, got 2; quote it'   ['--', 'pytest', 'x']
R5-2wb   rc=2 stdout=b''  stderr_lines=1 'COMMAND must be one argument, got 2; quote it'   ['--', 'true', 'pytest']
R5-1w    rc=1 stdout=b'does-not-count\n'                                                  ['--', "python -c 'import pytest'"]
R5-1wc   rc=0 stdout=b'counts\n'                                                          ['--', 'pytest']
R5-pf2w  rc=2 stdout=b''  stderr_lines=1 'COMMAND must be one argument, got 2; quote it'   ['--with-pipefail', '--', 'npm', 'test | tail -5']
R6-e     rc=2 stdout=b''  stderr_lines=1 '--pattern value is empty'                         ['--pattern', '', '--', 'make build']
R6-e2    rc=2 stdout=b''  stderr_lines=1 '--pattern value is empty'                         ['--pattern', '^x$', '--pattern', '', '--', 'make build']
R6-ok    rc=0 stdout=b'counts\n'                                                          ['--pattern', '^make build$', '--', 'make build']
R6-sp    rc=0 stdout=b'counts\n'                                                          ['--pattern', ' ', '--', 'true nothing']
R6-grp   rc=0 stdout=b'counts\n'                                                          ['--pattern', '(?:)', '--', 'true nothing']
R6-dot   rc=0 stdout=b'counts\n'                                                          ['--pattern', '.*', '--', 'true nothing']
R6-nov   rc=2 stdout=b''  stderr_lines=1 '--pattern requires a value'                       ['--pattern']
R7-strict  rc=2 stdout=b'' stderr_lines=1 "cannot write the rewrite: 'utf-8' codec can't encode character '\udcff' …"   env PYTHONUTF8=1 PYTHONIOENCODING=utf-8:strict
R7-default rc=0 stdout=b'set -o pipefail && \xffnpm test | tail -5\n'                     (surrogateescape writes the byte back)
R7-ascii   rc=2 stdout=b'' stderr_lines=1 "cannot write the rewrite: 'ascii' codec …"      env PYTHONIOENCODING=ascii:strict
R7-cjk     rc=2 stdout=b'' stderr_lines=1 "cannot write the rewrite: 'latin-1' codec can't encode character '中' …"
R7-none    rc=1 stdout=b''                                                                 ['--with-pipefail', '--', 'npm test'] (strict env)
X-unk      rc=2 stderr='unknown option: \udcff' (1 line; stderr keeps backslashreplace under a strict PYTHONIOENCODING)
X-pat      rc=2 stderr="invalid pattern: '(\udcff': missing ), unterminated subpattern at position 0" (1 line)
X-ws       rc=2 stderr='COMMAND is empty'      ['--', ' \t\n']
```

R5 holds (V:305-312, `COMMAND must be one argument`), including the two-word boundary.
R6 holds (V:287-290, `--pattern value is empty`).
R7 holds (V:332-337, `cannot write the rewrite`) under every strict encoding tried. `R6-sp`, `R6-grp`,
`R6-dot`: a pattern that matches every string is still accepted — only the literal empty string is refused (F-9).

### 2e. Canny's frozen tables, answer for answer (PIN V vs final V) — my comparator, with its red controls

`$S/frozencmp.py` captures the tables at **runtime** from each T module (the `parametrize` Mark on
`def test_is_verify_27_rows`, the `CHECKS`/`HIDES`/`KEEPS` objects), from the PIN T sitting next to the PIN V in its own
tree and from the final T; checks that both T sources carry the four literal override/config calls; compares all 328
answers; and runs the same 328 through my Canny oracle as a credibility check on that oracle.

```
$ frozencmp.py <PIN V 3f531c4> <final V> <PIN T> <final T>
tables identical: rows=True (27) CHECKS=True (11) HIDES=True (154) KEEPS=True (143)
answers compared: 328  differing(ref vs cand): 0  cand-vs-expected mismatches: 0  Canny(JS)-vs-expected mismatches: 0
rc=0
$ planted P1: _ASKS_ONLY without `version` (scratch V)
answers compared: 328  differing(ref vs cand): 1  cand-vs-expected mismatches: 1  ...   DIFF ('row', 'tsc --version', False, True)   rc=1
$ planted P2: pipefail scan `\w*o` -> `o` (scratch V)
answers compared: 328  differing(ref vs cand): 1  cand-vs-expected mismatches: 1  ...   DIFF ('row', 'set -euo pipefail\npnpm test | tail -5', True, False)   rc=1
$ planted P3: one KEEPS form `time {c}` -> `times {c}` in a scratch T
tables identical: rows=True (27) CHECKS=True (11) HIDES=True (154) KEEPS=False (143)   rc=1
```

328/328 unchanged; each single-answer plant turns the comparator red with exactly one diff, and a table drift turns it
red too. My JS oracle agrees with all 328 expected answers, so it is a usable Canny reference for §4.

## 3. D1 and D2 — dispositions, and the builder's candidate fixes graded against bash in both directions (item 3)

`$S/mkvariants.py` builds each candidate as a scratch copy of V: **L-PF** (the builder's: the scan ends
`pipefail(?=[\s;&|]|$)`), **L-PF2** (mine: the scan's `\s` replaced by bash's blanks `[ \t]` and the end by bash's word
terminators, `(?:^|[;&\n])[ \t]*set[ \t]+([+-])\w*o[ \t]+pipefail(?=[ \t\n;&|<>]|$)`), **L-TR** (the builder's: rule (b)
at every `&&`-part start), **L-TRE** (L-TR plus the same for (e)), **WPG** (mine: `with_pipefail` returns `None` when the
ORIGINAL command already trips a C1-A2 rule). `$S/grade.py` / `$S/gradewp.py` grade them through bash (stubs exit 3 / 0).

### 3a. D1 — `set -o pipefail` + a kept suffix counts (the `é` case is new in C1-R1)

**Reproduced** (§1): `set -o pipefailé; pnpm test | tail` → PIN `does-not-count`, final `counts`, bash rc 0 with
`set: pipefailé: invalid option name`. My JS oracle says Canny counts it too: the final V now agrees with Canny here, and
the PIN's refusal was an accident of its missing flag. **Disposition: FOLLOW-UP, not a blocker.** Leg 1 of the predicate
fails: R1 (and C1 item 2) mandate the flag on the scan, the required result (H3 → does-not-count) holds, the docstring
declares the family (V:52-55, `The pipefail scan ends in`), and T pins both examples as strict xfails, both live (§5):
T:428-430 (`def test_limit_pipefail_option_word_suffix`) and
T:433-435 (`def test_limit_pipefail_non_ascii_suffix`).

**The family is wider than declared (F-2).** In my 14-shape hollow corpus for the scan, 8 shapes count while bash never
sets pipefail because the scan's `\s` (ASCII: space, tab, `\n`, `\r`, `\v`, `\f`) accepts characters bash does not treat
as blanks inside the `set` command: a vertical tab or form feed next to `set`, `-o` or `pipefail`, and a newline inside
the statement (bash ends the `set` command there). They are hollow at the PIN and in Canny too (inherited; JS `\s`
includes them). `re.ASCII` closed the Unicode spaces (H3) but not these ASCII ones: the same mechanism as VERIFY-C1's F2
blocker, in ASCII form, and the sibling pattern AF-AP-135 names. The docstring's pipefail bullet covers only the
option-word suffix, so this family is undeclared.

```
$ /usr/bin/python3 $S/grade.py $S      (tallies; the full rows are in $S; bash rc fail/pass per row)
pipefail scan, HOLLOW corpus (14: 6 option-word suffixes incl. `é` `-x` NBSP `=1` `.` `\;`, 8 VT/FF/newline placements)
  FINAL  HOLLOW 14   LPF  HOLLOW 8 (all 8 VT/FF/newline shapes stay open)   LPF2  HOLLOW 0
pipefail scan, LEGITIMATE corpus (21 status-preserving shapes: `set -o pipefail;`, `set -euo pipefail;`/`\n`, `-o errexit`
after it, trailing spaces, `\n`, `;`, `&&` with and without spaces, a `# comment`, tabs, `2>/dev/null`, `-eo`, `|| true` …)
  FINAL  FN 3   LPF  FN 5   LPF2  FN 3
  the FN rows:
P-k13  rc=3/0  FINAL=cnt  LPF=ref~ LPF2=cnt   'set -o pipefail>/dev/null; pnpm test | tail'
P-k21  rc=3/0  FINAL=cnt  LPF=ref~ LPF2=cnt   'set -o pipefail<&-; pnpm test | tail'
P-k17  rc=3/0  FINAL=ref~ LPF=ref~ LPF2=ref~  'set -e -o pipefail; pnpm test | tail'        (pre-existing, Canny's too)
P-k18  rc=3/0  FINAL=ref~ LPF=ref~ LPF2=ref~  'set -o errexit -o pipefail; pnpm test | tail' (pre-existing, Canny's too)
P-k19  rc=3/0  FINAL=ref~ LPF=ref~ LPF2=ref~  '{ set -o pipefail; }; pnpm test | tail'     (pre-existing, Canny's too)
$ frozencmp.py <PIN V> <variant> …   LPF and LPF2: answers compared: 328  differing(ref vs cand): 0
```

**Grade.** L-PF closes 6 of 14 and leaves the 8 whitespace shapes open; it adds 2 false negatives (a redirection right
after `pipefail`, which bash reads as a word end). **L-PF2 closes 14 of 14, adds no false negative on the 21 legitimate
shapes, and moves no frozen answer**; it turns both pipefail pins into XPASS failures (§5, mutant L5-PF2), so it ships
with the two xfails deleted and the docstring bullet updated. The three remaining FNs are Canny's, independent of either
fix.

### 3b. D2 — rules (b)/(e) see only segment starts; `with_pipefail` builds that shape

**Reproduced** (§1, §2c): `with_pipefail("trap 'exit 0' EXIT; pytest | tail")` returns a rewrite that counts while bash
exits 0; so do the `exec true` and `coproc` analogues (§2c row 6, and `coproc pytest | tail` in §3c), which T does not
pin. My JS oracle returns the same rewrites, so `with_pipefail` is Canny-faithful. **Disposition: FOLLOW-UP, not a
blocker.** C1-A2 words (b)/(e) as "any segment begins with", which the port implements (V:148 `_TRAP.match(s)`,
V:151 `_EXEC_OR_COPROC.match(s)`); C1 item 1 makes `with_pipefail` a port of `withPipefail`; the docstring declares the
family (V:48, `(b) and (e) see only segment starts`) and T pins the trap examples (T:418-420 `def test_limit_trap_after_and`,
T:423-425 `def test_limit_with_pipefail_rewrites_trap`), both live (§5).

```
trap/exec off a segment start, HOLLOW corpus (11 positions: after `&&` ×4, after `||`, `{`, `(`, `!`, `then`, `time`, `builtin`)
  FINAL  HOLLOW 11   LTR  HOLLOW 9   LTRE  HOLLOW 7        (L-TR closes only the two `&&` trap rows)
LEGITIMATE corpus (9 status-preserving shapes)
  FINAL  FN 2   LTR  FN 6   LTRE  FN 7
  the rows L-TR newly refuses:
T-k2  rc=3/0  FINAL=cnt  LTR=ref~ LTRE=ref~  "true && trap 'echo done' EXIT; pytest"
T-k3  rc=3/0  FINAL=cnt  LTR=ref~ LTRE=ref~  "mkdir -p out && trap 'rm -rf out' EXIT && pytest"
T-k4  rc=3/0  FINAL=cnt  LTR=ref~ LTRE=ref~  'tmp=$(mktemp -d) && trap \'rm -rf "$tmp"\' EXIT && pytest'
T-k8  rc=3/0  FINAL=cnt  LTR=ref~ LTRE=ref~  'pnpm install && trap - EXIT && pytest'
  (L-TRE also refuses 'true && exec pytest', rc 3/0)
```

**Grade.** L-TR closes 2 of the 11 off-start positions and refuses 4 status-preserving commands, two of them the common
temp-directory cleanup idiom (`trap 'rm -rf …' EXIT` between `&&` parts). A position rule cannot reach `||`, braces,
subshells, `!`, reserved words or `builtin` without parsing command positions: that is the H9 redesign, so the off-start
family should stay declared. **Not recommended as the fix.**

### 3c. WPG — the `with_pipefail` half of D2, graded

```
$ /usr/bin/python3 $S/gradewp.py $S    (13 inputs; bash run on each rewrite)
FINAL=rewrite bash=0/0 HOLLOW | WPG=None   "trap 'exit 0' EXIT; pytest | tail"
FINAL=rewrite bash=0/0 HOLLOW | WPG=None   'exec true; pytest | tail'
FINAL=rewrite bash=0/0 HOLLOW | WPG=None   'coproc pytest | tail'
FINAL=rewrite bash=0/0 HOLLOW | WPG=rewrite bash=0/0 HOLLOW  "true && trap 'exit 0' EXIT; pytest | tail"   (the declared off-start family)
FINAL=rewrite bash=3/0 ok     | WPG=None   "trap 'echo done' EXIT; pytest | tail"      (cheap direction, same trade as (b))
FINAL=rewrite bash=3/0 ok     | WPG=None   'exec 2>&1; pytest | tail'                  (cheap direction, same trade as (e))
… 5 plain tail rewrites identical in both; 2 inputs None in both
tally [hollow rewrites, status-preserving rewrites, None]: FINAL [4, 7, 2]   WPG [1, 5, 7]
$ frozencmp.py <PIN V> <WPG> …   answers compared: 328  differing(ref vs cand): 0
```

WPG removes 3 of the 4 hollow rewrites, keeps every plain `| tail` rewrite (the config test's rewrite included), and
gives up only rewrites of commands that (b)/(e) already refuse. It turns T:423-425 (`def test_limit_with_pipefail_rewrites_trap`) into an XPASS failure (§5, L5-WPG).
It is the cheapest fix for the part of D2 that the module causes itself (AF-AP-136).

## 4. New hollow greens (item 4)

**The brief's named shapes, all through bash** (`$S/item4.py`):

```
B1     V=refuses PIN=refuses Canny=refuses rc_fail=0    rc_pass=0    ok     'pytest || :'
B2     V=refuses PIN=refuses Canny=refuses rc_fail=0    rc_pass=0    ok     'pytest | true'
B3     V=refuses PIN=refuses Canny=refuses rc_fail=0    rc_pass=1    ok     '! pytest'
B4     V=refuses PIN=refuses Canny=refuses rc_fail=0    rc_pass=0    ok     'pytest &'
B5     V=refuses PIN=refuses Canny=refuses rc_fail=0    rc_pass=0    ok     '(pytest; exit 0)'
B6     V=refuses PIN=refuses Canny=refuses rc_fail=0    rc_pass=0    ok     'pytest; exit 0'
B7     V=refuses PIN=refuses Canny=refuses rc_fail=0    rc_pass=0    ok     'set -o pipefail; set +o pipefail; pnpm test | tail'
B8     V=counts  PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    ok     'timeout 5 pytest'
B9     V=refuses PIN=refuses Canny=refuses rc_fail=0    rc_pass=0    ok     'pytest 2>&1 | tee log'
B10    V=counts  PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    ok     'x=$(pytest)'
B11    V=refuses PIN=refuses Canny=refuses rc_fail=0    rc_pass=0    ok     'echo $(pytest)'
B12    V=counts  PIN=counts  Canny=counts  rc_fail=3    rc_pass=0    ok     'x=`pytest`'
D-H7   V=counts  PIN=counts  Canny=counts  rc_fail=0    rc_pass=0    HOLLOW 'export R=$(pytest)'
D-H8   V=counts  PIN=counts  Canny=counts  rc_fail=0    rc_pass=0    HOLLOW 'pytest(){ return 0; }; pytest'
D-H9   V=counts  PIN=counts  Canny=counts  rc_fail=0    rc_pass=0    HOLLOW '/bin/echo tsc'
D-HD   V=counts  PIN=counts  Canny=counts  rc_fail=0    rc_pass=0    HOLLOW "cat <<'pytest'\nfoo\npytest"
tally: {'ok': 12, 'HOLLOW': 4}
```

Every named shape is right: the port refuses each status-hiding one and counts only the three that carry the check's
status (`timeout`, and a bare assignment from `$( )` or backticks, which bash propagates). The four HOLLOW rows are the
declared families, each pinned (§5).

**Classification of what this round found beyond the named list** (all measured in §2c and §3, bash as the oracle):

| family | example (measured) | counts at PIN / in Canny | C1-A2 | declared in V | finding |
|---|---|---|---|---|---|
| pipefail scan accepts non-blank ASCII whitespace | a VT, FF or newline inside `set -o pipefail` (8 shapes, §3a) | yes / yes | not closed | no | **F-2** |
| option-word suffix after `pipefail` | `set -o pipefail=1; …`, `set -o pipefail.; …` (with `-x`, `é`, NBSP) | yes (not `é`) / yes | not closed | yes (V:52-55) | F-1 (D1) |
| trap/exec/coproc off a segment start beyond the `&&` example | after `||`, in braces or a subshell, after `!`, `then`, `time` (§3b) | yes / yes | not closed | yes, as a family (V:48, `see only segment starts`) | F-3 (D2) |
| `with_pipefail` rewrites an (e) shape | `exec true; pytest | tail`, `coproc pytest | tail` (§2c, §3c) | yes / yes | not closed | no example, no pin | F-3 (D2) |

The PIN and Canny columns are measured (`triple.evaluate` without bash over the §3 hollow corpora): pipefail corpus
counts final 14 / PIN 13 (all but `é`) / Canny 14; off-start corpus 12 / 12 / 12. I kept the exploratory hunt to the
brief's named shapes and to these corpora; I did not widen it this round.

## 5. The declared limits are live (item 5) — all eight, each closed by my own scratch fix

`$S/spec_item5.json` through `$S/mutdrv.py` (compile + collect 73 each). Every fix is mine, not the builder's L-rows:

```
L5-H7     (refuse a segment starting export/declare/readonly/typeset/local)  1 failed, 65 passed, 7 xfailed -> test_limit_h7_builtin_swallows_status [XPASS(strict)]
L5-H8     (refuse a function definition)                                     1 failed, 65 passed, 7 xfailed -> test_limit_h8_function_shadows_check
L5-H9     (basename the first word before the print/inspect denylist)       1 failed, 65 passed, 7 xfailed -> test_limit_h9_path_bypasses_denylist
L5-HD     (refuse `<<` not followed by `<`)                                   1 failed, 65 passed, 7 xfailed -> test_limit_heredoc_terminator [XPASS(strict)]
L5-TRAND  (rule (b) at every &&-part start)                                   2 failed, 65 passed, 6 xfailed -> test_limit_trap_after_and, test_limit_with_pipefail_rewrites_trap
L5-WPG    (with_pipefail declines when the original trips C1-A2)              1 failed, 65 passed, 7 xfailed -> test_limit_with_pipefail_rewrites_trap
L5-PFX    (pipefail\b(?!-))                                                   1 failed, 65 passed, 7 xfailed -> test_limit_pipefail_option_word_suffix
L5-PFE    (pipefail\b(?![^\x00-\x7f]))                                        1 failed, 65 passed, 7 xfailed -> test_limit_pipefail_non_ascii_suffix
L5-PF2    (my L-PF2 scan, §3a)                                                2 failed, 65 passed, 6 xfailed -> both pipefail limit tests
$ pytest tests/test_verify_command.py --runxfail --tb=line -k limit     (each xfail's own failure on the final V)
tests/test_verify_command.py:400: AssertionError: assert True is False      (and :405, :410, :415, :420, :430, :435 alike: `assert is_verify(`)
tests/test_verify_command.py:425: assert "set -o pipefail && trap 'exit 0' EXIT; pytest | tail" is None
8 failed, 65 deselected in 0.04s
```

All eight pins are live: a fix of the shape turns exactly its own strict xfail into an XPASS failure while the other 65
tests stay green. Each fails today for its target assertion, never another exception (`def _declared_limit` at T:393-395
sets `raises=AssertionError`). **Every docstring bullet has a pin:**

| docstring bullet | pin |
|---|---|
| V:41-42 `a prefix assignment swallows the status` (H7) | T:398-400 `def test_limit_h7_builtin_swallows_status` |
| V:43 `a shell function shadows the check` (H8) | T:403-405 `def test_limit_h8_function_shadows_check` |
| V:44-45 `the first-word rules` (H9) | T:408-410 `def test_limit_h9_path_bypasses_denylist` |
| V:46-47 `A here-doc terminator line reads as a command` | T:413-415 `def test_limit_heredoc_terminator` |
| V:48 `see only segment starts` | T:418-420 `def test_limit_trap_after_and` |
| V:49-51 `builds this shape itself` | T:423-425 `def test_limit_with_pipefail_rewrites_trap` |
| V:52-53 `The pipefail scan ends in` | T:428-430 `def test_limit_pipefail_option_word_suffix` |
| V:54-55 `a non-ASCII letter passes too` | T:433-435 `def test_limit_pipefail_non_ascii_suffix` |

Two gaps inside those bullets (INFO, F-12):
V:48 (`see only segment starts`) names (e), but only the trap shape is pinned.
V:44-45 (`the first-word rules`) names (b)/(e) bypasses with no example or pin.

## 6. Mutation audit (item 6) — 28 new mutants, none of them the builder's rows

Scratch trees via `$S/mutdrv.py`; every mutant compiles and collects 73 (no INVALID). **13 killed · 1 equivalent
(searched) · 14 survived with a live discriminator.**

| id | mutation (V) | result | killed by / discriminator (final → mutant; bash fail/pass) |
|---|---|---|---|
| N-SCAN-ASCII | `flags=0` on the pipefail scan (V:194-196) | KILLED 3 failed | `test_ascii_pipefail_scan_refuses_nbsp_in_set`, `…_cli`, `test_limit_pipefail_non_ascii_suffix` (XPASS) |
| N-ORD-AFTER | the C1-A2 check moved after the pattern loop | KILLED 7 failed | all seven `test_c1_a2_refuses_status_hiding_shapes` rows |
| N-ORD-INLOOP | the C1-A2 check moved after the pattern match, inside the loop (`return not _hides_status(…)`) | **EQUIVALENT** | searched: 567 measured/frozen commands + 40,500 pairwise joins × 5 pattern settings = 205,335 (`is_verify`, `with_pipefail`) pairs, 0 differ; structurally the check now runs only where the original returns True |
| N-RAW | `_hides_status(command, …)`: fed the unstripped command | SURVIVED | `pytest "a\rb"`, `pytest # note\r`, `echo "a\\\nb"; pytest`: True → False; bash 3/0 (cheap direction; T has no D7 row) |
| N-EX1-R5 | R5's `sys.exit(2)` → 1 | KILLED | `test_cli_refuses_more_than_one_command_word` |
| N-EX1-R6 | R6's exit → 1 | KILLED | `test_cli_refuses_empty_pattern` |
| N-EX1-R7 | R7's exit → 1 | KILLED | `test_cli_with_pipefail_encoding_failure_exits_2` |
| N-EX1-NOVAL | `--pattern requires a value` exit → 1 | SURVIVED | CLI `--pattern`: rc 2 → rc 1 (no T row for this branch; pre-existing) |
| N-EX1-UNK / -NODD / -EMPTY / -BADPAT | the other four refusals' exit → 1 | KILLED ×4 | `test_cli_usage_error_unknown_option`, `…_no_dashdash`, `…_empty_command`, `…_invalid_pattern` |
| N-WP-NORECHECK | `with_pipefail` without its re-check (V:253-254 `if not is_verify(candidate, patterns):` deleted) | SURVIVED | `with_pipefail("pytest; echo done")`: None → `set -o pipefail && pytest; echo done`, bash on it 0/0; `echo hi | tail` likewise |
| N-SEGSTRIP | `.strip()` dropped from the segments (V:200) | SURVIVED | `cd /tmp; trap 'exit 0' EXIT; pytest` and `cd /tmp; exec true; pytest`: False → **True**, bash 0/0 — reopens a hollow green |
| N-A-BARE | rule (a) on the whole text instead of the last segment | SURVIVED | `command -v pytest || exit 1; pytest`: True → False; bash 3/0 (cheap) |
| N-C-CRLF | rule (c) needs `\r\n` instead of `\r` | SURVIVED | `set -o pipefail\r; pnpm test | tail`: False → **True**, bash 0/0 — reopens a hollow green |
| N-B-LAST / N-E-LAST | (b) / (e) test the last segment only | KILLED ×2 | `[b_H2]`; `[e_H6]` |
| N-COPROC | `coproc` dropped from `_EXEC_OR_COPROC` | KILLED | `[e_H6b]` |
| N-TRAP-NOB | `trap\b` → `trap` | SURVIVED | `trapdoor=1; pytest`: True → False; bash 3/0 (cheap) |
| N-TRAP-UNI | `re.ASCII` dropped from `_TRAP` | SURVIVED | `trapé 'exit 0' EXIT; pytest`: False → True; bash 3/0 (the mutant is the more accurate one) |
| N-USER-UNI | `re.ASCII` dropped from user patterns (V:160) | SURVIVED | `npm\xa0test` under `^npm\stest$`: False → True; bash 127 |
| N-VERIFY1-UNI / N-VERIFY2-UNI | `re.ASCII` dropped from `VERIFY[1]` / `VERIFY[2]` | SURVIVED ×2 | `tscé` / `eslinté`: True → False; bash 127 |
| N-PRINTS-UNI | `re.ASCII` dropped from `_PRINTS_OR_INSPECTS` | SURVIVED | `echoé tsc`: False → True; bash 127 |
| N-R5-BOUND | `len(command_parts) > 1` → `> 2` | SURVIVED | CLI `-- pytest x`: rc 2 → **`counts` rc 0** (classifies the first word only; T pins 3 words, not 2) |
| N-R7-CATCH | `except UnicodeEncodeError` → `UnicodeDecodeError` | KILLED | `test_cli_with_pipefail_encoding_failure_exits_2` |
| N-EMPTY-NOSTRIP | `if not command.strip():` → `if not command:` | SURVIVED | CLI `-- ' \t\n'`: rc 2 → `does-not-count` rc 1 (pre-existing) |

All five mutants the brief requires are here. `re.ASCII` dropped at the scan, the check moved after the loop, and the
three new refusals' exit codes are all killed. The in-loop variant is equivalent (searched, 0 of 205,335 pairs differ).
The unstripped-command feed and the missing re-check survive, each with a live discriminator. Survivors that **reopen a
hollow green** that T does not pin: N-SEGSTRIP, N-C-CRLF, N-WP-NORECHECK (F-4). The discriminators are rows the tree lacks, not
defects in V.

## 7. Gates (item 7), run fresh at 2026-09-23 06:31:02Z, pasted verbatim

```
d9f71bb3962bdb4a 351 scripts/verify_command.py
195c1b6378adaad8 490 tests/test_verify_command.py
$ bash scripts/pc_suite.sh set-id -- tests/test_verify_command.py
1 files set=d9bd6dad2d0e
$ (repo root, run 1) /root/venv-agent-factory/bin/python -m pytest tests/test_verify_command.py -q -p no:cacheprovider --basetemp=$S/gate/g1
65 passed, 8 xfailed in 0.48s
rc=0
$ (repo root, run 2) /root/venv-agent-factory/bin/python -m pytest tests/test_verify_command.py -q -p no:cacheprovider --basetemp=$S/gate/g2
65 passed, 8 xfailed in 0.46s
rc=0
$ (cd /tmp && /root/venv-agent-factory/bin/python -m pytest /home/user/agent-factory/tests/test_verify_command.py -q -p no:cacheprovider --basetemp=$S/gate/g3)
65 passed, 8 xfailed in 0.52s
rc=0
$ /root/venv-agent-factory/bin/python -m pyflakes scripts/verify_command.py tests/test_verify_command.py
pyflakes rc=0
$ python3 scripts/ap_screen.py scripts/verify_command.py
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---
rc=0
$ python3 scripts/ap_screen.py --tests tests/test_verify_command.py
--- TEST_SCREEN over 1 path(s): 0 hits over 1 files ---
rc=0
```

The set id `d9bd6dad2d0e` hashes the path string (`pc_suite.sh set_id`), so it matches the brief's premise. V and T are
byte-identical to the PIN at the end of this lane. `git status --short` shows other lanes' edits (S0-05, the CI workflow,
the ledger, the wiki); the only path this lane wrote is this report.

## 8. FINDING INVENTORY (no severity filter)

| id | finding | class | evidence | contract mapping | canonical path | material effect | reproduction | suggested fix |
|---|---|---|---|---|---|---|---|---|
| F-1 | D1: `set -o pipefail` + a kept suffix counts while bash never sets pipefail; `é` is new in C1-R1 (R1's mandated flag; Canny counts it too) | FOLLOW-UP | reproduced | none contradicted: R1 mandates the flag; declared at V:52-55 (`The pipefail scan ends in`) | yes, the CLI | a hollow green on a malformed option word; declared and pinned | §1 D1 rows; `$S/d1d2.py` | L-PF2 (§3a), then drop the two pipefail xfails and update the bullet |
| **F-2** | **NEW, undeclared:** the pipefail scan's whitespace class accepts a VT, FF or newline inside the set statement; 8 shapes count while bash never sets pipefail | FOLLOW-UP (first in line) | reproduced | none: R1's required result (H3) holds, C1-A2 does not name it, the docstring says `The list is not exhaustive` (V:39) | yes, the CLI | hollow greens; inherited (PIN and Canny too), not a regression | `$S/grade.py` (hollow corpus) | L-PF2 closes all 8, adds 0 FN on 21 legitimate shapes, moves 0 of 328 frozen answers; at minimum declare + pin |
| F-3 | D2: (b)/(e) are positional; `with_pipefail` hands back hollow rewrites for trap (declared), `exec true` and `coproc` inputs (both unpinned) | FOLLOW-UP | reproduced | none: C1-A2's letter "any segment begins with" is met; `with_pipefail` is Canny-faithful; declared at V:48 (`(b) and (e) see only segment starts`) | yes | the module's own suggestion can be a hollow green | §2c, §3b, §3c | WPG for the rewrite half (3 of 4 closed, cheap-direction cost only); keep the off-start family declared; not L-TR (2 of 11 closed, 4 FN incl. the cleanup idiom) |
| F-4 | three mutants survive that reopen a hollow green T does not pin: the segment `.strip()` (V:200), bare-CR rule (c), and the `with_pipefail` re-check (V:253-254, `if not is_verify(candidate, patterns):`) | FOLLOW-UP | reproduced | none: R2's listed rows exist and are live | n/a (test coverage) | a later edit could reopen these shapes silently | N-SEGSTRIP, N-C-CRLF, N-WP-NORECHECK (§6) | rows: `cd /tmp; trap 'exit 0' EXIT; pytest`, `cd /tmp; exec true; pytest`, `set -o pipefail\r; pnpm test | tail` → False; `with_pipefail("pytest; echo done") is None` |
| F-5 | D7 is unpinned: a CR or continuation inside quotes or a comment still counts (`_hides_status` reads the executed text) | FOLLOW-UP (low) | reproduced | none | n/a | cheap direction only | N-RAW (§6) | the three D7 rows |
| F-6 | R5's two-word boundary is unpinned: a `> 2` regression would print `counts` for `-- pytest x` | FOLLOW-UP | reproduced | none: R5 holds in V (V:305-312, `COMMAND must be one argument`) | yes, the CLI | reopens part of VERIFY-C1 F4 if regressed | N-R5-BOUND (§6) | a two-word CLI row |
| F-7 | answer-changing `re.ASCII` flags with no row: `VERIFY[1]`, `VERIFY[2]`, `_PRINTS_OR_INSPECTS`, `_TRAP`, `_EXEC_OR_COPROC`, user patterns | FOLLOW-UP (low) | reproduced | none: R1 asks for the flag, not a row per flag; the six inline flags R1 added are fully covered (3 pinned, 3 inert) | n/a | none today (bash 127 or cheap direction) | N-*-UNI (§6) | one row each, or a comment saying why not |
| F-8 | pre-existing CLI branches with no row: `--pattern requires a value`; a whitespace-only COMMAND | FOLLOW-UP (low) | reproduced | C1 item 5 (exit 2) holds in V | yes | exit code unpinned | N-EX1-NOVAL, N-EMPTY-NOSTRIP | two CLI rows |
| F-9 | a user pattern that matches everything is still accepted (`' '`, `(?:)`, `.*`), and the API accepts `patterns=[""]` | INFO | reproduced | R6's letter is the empty value only | yes | a configured catch-all | §2d `R6-sp`/`R6-grp`/`R6-dot` | optional: refuse a pattern that matches the empty string |
| F-10 | cheap-direction false negatives by the letter of C1-A2 and of Canny: `false || pytest`, `trap 'echo done' EXIT; pytest`, a continued check, `exec pytest`, `exec 2>&1; pytest`, `trapé`/`execé`, `set -e -o pipefail`, `set -o errexit -o pipefail`, `{ set -o pipefail; }` | INFO | reproduced | by design (V:33-35 declares two) | yes | a nudge, never a false pass | §2a, §3a | none required |
| F-11 | N-ORD-INLOOP is equivalent | INFO | searched, 0 of 205,335 pairs | n/a | n/a | none | `$S/equiv.py` | none |
| F-12 | two bullets pin one example each: V:48 (`see only segment starts`) names (e) but no (e) shape is pinned; V:44-45 (`the first-word rules`) names (b)/(e) bypasses with no pin | INFO | static + reproduced (§2c) | R3 asks for one example per listed limit, which holds | n/a | the unpinned halves can drift | n/a | add an (e) off-start row and an `exec` rewrite pin |
| F-13 | the builder's report audited: premise, oracle table, 328/328, D1, D2, the eight pins, and the three inert flags all reproduce; its ungraded candidates are now graded (§3) | INFO | reproduced | n/a | n/a | none | §1-§6 | none |

## GATE RECOMMENDATION

**`MERGE-READY-WITH-FOLLOWUPS`** — no finding meets leg 1 of the blocking predicate (contract mapping): R1-R8 and C1-A2
hold as written and are reproduced through the real CLI and bash; Canny's frozen tables are 328/328 unchanged. F-2 is the
first follow-up: an undeclared hollow-green family in the pipefail scan (L-PF2 closes it at no measured cost), then F-3's
`with_pipefail` half (WPG) and F-4's three rows. C2 must still treat a green `is_verify` as necessary, not sufficient,
until F-2 and F-3 are closed or declared. This recommendation rests on stub check binaries (exit 3 / exit 0) in the
sandbox's bash 5.2.21, as the contract's evidence demands specify; no real test runner and no PC venue.

## 9. Reproduced vs reviewed statically; skipped; NOT-done

- **Reproduced** (this session, primary): every premise line; each C1-A2 rule, each R1 site and each CLI refusal
  through the real CLI and bash; the frozen-table comparison and its three red controls; D1, D2 and the graded candidates;
  the brief's item-4 list; all eight limits live; 28 new mutants with discriminators; the gates.
- **Static only:** the `ast` inventory of the 15 `re` call sites (backed by the runtime probes); the docstring-bullet →
  pin mapping; Canny's `src/checks.ts` (read; literals copied as text into my node oracle, nothing run or imported);
  the ledger and incident-log sweep (no line there is falsified by this round; F-2 is a fresh instance of AF-AP-135's class,
  and §3b-§3c answer AF-AP-136's OPEN question).
- **Deliberately skipped:** the builder's own mutant rows (the brief forbids reusing them); real check binaries and the PC
  venue; `scripts/no_laya_in_gates.py` (not in this brief); widening the exploratory hunt beyond the brief's named shapes
  and the §3 corpora; GitNexus/graft (the boundary is two files read in full; this report makes no reachability or
  DORMANT claim).
- **NOT-done:** no fix applied (every variant and mutant lives under `$S`); no commit, push, PR or comment; no bridge use.

## 10. Report lint (two fix rounds of the three allowed)

Round 1 read `67 refs — OK 42, NEAR 3, MISS 19, UNCHECKABLE 3`: lines that carried several refs with the tokens for only
some of them (mostly the bullet-to-pin paragraph, now a table), four refs whose token wrapped to the next line or sat one
line off, and short backticked spans that threw off the token pairing. Round 2 fixed them. The final run, after the last
edits:

```
$ python3 scripts/report_lint.py --min-refs 12 --map V=scripts/verify_command.py --map T=tests/test_verify_command.py tasks/briefs/canny/VERIFY-C1-R1-report.md --root .
report_lint: 67 refs — OK 67, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
```
