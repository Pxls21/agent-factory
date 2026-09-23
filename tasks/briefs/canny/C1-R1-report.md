# C1-R1 — the focused repair of VERIFY-C1 on `scripts/verify_command.py` (task #159)

**Lane:** C1-R1, sandbox `code-implementer` (Opus 5.5), shared tree, no worktree. **Brief:** `tasks/briefs/canny/C1-R1-brief.md`
(origin `5694755`). **Aliases:** `V` = `scripts/verify_command.py`, `T` = `tests/test_verify_command.py`.
**Status:** DONE, uncommitted (the coordinator commits). Written incrementally from 2026-09-23 05:42Z.

## OUTCOME

**Built as the brief specifies, R1-R8, with one regression the brief's own R1 buys, declared and pinned.**

- H1, H1b, H2, H3, H4, H5, H6, H6b → `does-not-count`, CLI rc 1; CTRL and CTRL2 still count (§5a).
- Canny's frozen tables: 328/328 answers unchanged, PIN V vs final V (§5b).
- T: `65 passed, 8 xfailed` twice from the root and once from `/tmp`, set `d9bd6dad2d0e`; pyflakes and both screens clean (§7).
- Mutants: 24 killed, 5 survived (each shown equivalent), 0 invalid (§6). VERIFY-C1's survivors N5, N10, N11, N13 and
  its equivalent N8 are now killed.
- **Read §8 first.** D1: `re.ASCII` on the pipefail scan (the brief's R1) turns `set -o pipefail` + U+00E9 into a hollow
  green the PIN refused. D2: rules (b)/(e), as worded, miss a `trap`/`exec` off a segment start, and `with_pipefail`
  itself builds that shape. Both are declared in the docstring and pinned by strict xfails. Neither is fixed: the
  contract has no rule for them.

## 1. PREMISE — re-measured (2026-09-23 05:3xZ-05:4xZ, sandbox, HEAD `2236669`)

HEAD is two commits past the brief's PIN `3f531c4` (`5694755` = the brief itself, `2236669` = transcripts). Neither touches
V or T. Every line of the brief's premise block reproduces.

```
$ git diff --stat ea9538a 3f531c4 -- scripts/verify_command.py tests/test_verify_command.py    (empty)
$ git diff --stat 3f531c4 HEAD   -- scripts/verify_command.py tests/test_verify_command.py    (empty)
$ git diff --stat HEAD           -- scripts/verify_command.py tests/test_verify_command.py    (empty)
8420e9a202de6afb 273 scripts/verify_command.py
a9aedce65126da71 302 tests/test_verify_command.py
$ bash scripts/pc_suite.sh set-id -- tests/test_verify_command.py
1 files set=d9bd6dad2d0e
$ (cd /tmp && /root/venv-agent-factory/bin/python -m pytest /home/user/agent-factory/tests/test_verify_command.py -q -p no:cacheprovider --basetemp=/tmp/c1r1p/bt)
.............................................                            [100%]
45 passed in 0.24s
rc=0
$ grep -n -E 're\.(sub|search|split|finditer|...)\(' scripts/verify_command.py    (the six inline calls, none with re.ASCII)
117:    bare = re.sub(r'"[^"]*"|\'[^\']*\'', "", command)
119:    bare = re.sub(r"(^|(?<!\\)\s)#[^\n]*", r"\1", bare)
139:    for m in re.finditer(          (pattern on :140)
145:    segments = [s.strip() for s in re.split(r"[;\n]", bare)]
163:        if re.search(r"(?<!>)&(?!>)", part):
197:    if re.search(r"(?<!\|)\|(?!\|)(?!\s*tail\b)", bare):
$ /usr/bin/python3 shapes.py <scratch>/stub      (the brief's script, copied verbatim; H3 carries U+00A0 as in the brief's bytes)
H1    port=counts           port_rc=0 bash_rc=0  'pytest && false || true'
H1b   port=counts           port_rc=0 bash_rc=0  'pytest && echo ok || true'
H2    port=counts           port_rc=0 bash_rc=0  "trap 'exit 0' EXIT; pytest"
H3    port=counts           port_rc=0 bash_rc=0  'set\xa0-o pipefail; pnpm test | tail'
H4    port=counts           port_rc=0 bash_rc=0  'set -o pipefail\r\npnpm test | tail'
H5    port=counts           port_rc=0 bash_rc=0  'echo \\\npytest'
H6    port=counts           port_rc=0 bash_rc=0  'exec true; pytest'
H6b   port=counts           port_rc=0 bash_rc=0  'coproc pytest'
CTRL  port=counts           port_rc=0 bash_rc=3  'pytest'
CTRL2 port=counts           port_rc=0 bash_rc=3  'set -o pipefail; pnpm test | tail'
$ the F3 discriminators through the API (env -i PATH=/usr/bin:/bin /usr/bin/python3)
npm teste-acute -> True
pipefail | grep -- --help -> True
patterns=[] -> False
echo set -o pipefail; ... | tail -> False
$ F4 / F5 through the CLI (env -i PATH=/usr/bin:/bin /usr/bin/python3 scripts/verify_command.py ...)
-- python -c 'import pytest'      counts          rc=0
-- "python -c 'import pytest'"    does-not-count  rc=1
--pattern '' -- 'make build'      counts          rc=0
--pattern '' -- 'echo hi'         does-not-count  rc=1
```

Blast radius before the edit: GitNexus `impact is_verify --direction upstream` → the V function has `impactedCount 3`,
`risk LOW` (its callers are `with_pipefail` and `_cli`, both in V); a literal sweep of `scripts tests harness-ports src
proofs` for `verify_command|is_verify|with_pipefail` finds only V, T and `tests/test_laya_probe_report.py`, whose two hits
are the phrase "verify_command equivalent" in prose (no import). C2 is not built.

## 2. Measured BEFORE building (PIN copy of V, `git show 3f531c4:scripts/verify_command.py` into scratch)

### 2a. R7 / F6 — reproduced

```
$ env -i PATH=/usr/bin:/bin PYTHONIOENCODING=utf-8:strict /usr/bin/python3 <pin>/scripts/verify_command.py --with-pipefail -- $'\xffnpm test | tail -5'
Traceback (most recent call last):
  ...
    print(result)
UnicodeEncodeError: 'utf-8' codec can't encode character '\udcff' in position 19: surrogates not allowed
rc=1
$ env -i PATH=/usr/bin:/bin /usr/bin/python3 <pin>/... --with-pipefail -- $'\xffnpm test | tail -5' | od -c     (default handler)
s e t   - o   p i p e f a i l   & &   377 n p m   t e s t   |   t a i l   - 5 \n       rc=0
$ env -i PYTHONUTF8=1 PYTHONIOENCODING=utf-8:strict /usr/bin/python3 <pin>/... (same argv)       (the env T uses)
rc=1    stderr lines: 6
```

The crash exits 1, which the CLI contract defines as "no rewrite", and prints a six-line traceback. It needs a strict stdout
error handler; the default handler (`surrogateescape`) writes the raw byte and exits 0.

### 2b. Side effects of the contract's own rules — probed through bash (stub exit 3 / exit 0, `env -i`, absolute interpreters)

`probe.py` loads a copy of V by path and runs each shape in `/bin/bash -c` twice (check stubbed to fail, then to pass).
HOLLOW = counts while bash exits 0 with the check failing; FN = refused while bash carries the status (the cheap direction).

```
=== PIN V
X1a  port=counts  rc_fail=0   rc_pass=0   HOLLOW 'set -o pipefail-x; pnpm test | tail'
X1b  port=refuses rc_fail=0   rc_pass=0   ok     'set -o pipefailé; pnpm test | tail'
X1c  port=counts  rc_fail=0   rc_pass=0   HOLLOW 'set -o pipefail\xa0; pnpm test | tail'
X1d  port=counts  rc_fail=0   rc_pass=0   HOLLOW 'set -éo pipefail; pnpm test | tail'
X2a  port=counts  rc_fail=0   rc_pass=0   HOLLOW "true && trap 'exit 0' EXIT; pytest"
X2b  port=counts  rc_fail=0   rc_pass=0   HOLLOW 'true && exec true; pytest'
X2c  port=counts  rc_fail=0   rc_pass=0   HOLLOW "set -o pipefail && trap 'exit 0' EXIT; pytest | tail"
X2d  port=counts  rc_fail=0   rc_pass=0   HOLLOW 'set -o pipefail && exec true; pytest | tail'
X2e  port=counts  rc_fail=0   rc_pass=0   HOLLOW "{ trap 'exit 0' EXIT; }; pytest"
X3   port=counts  rc_fail=0   rc_pass=0   HOLLOW 'pytest\xa0#; exit 0'
X3b  port=refuses rc_fail=3   rc_pass=0   FN     'true \xa0# ; pytest'
FNe  port=counts  rc_fail=3   rc_pass=0   ok     'exec 2>&1; pytest'
FNd  port=counts  rc_fail=3   rc_pass=0   ok     'echo \\\\\npytest'
D3   port=counts  rc_fail=127 rc_pass=127 ok     'set -o pipefail && npm test | tailé'
```

What each row predicts for the build (confirmed after it in §5):

- **X1b is the one regression R1 buys.** `pipefail\b` at V@3f531c4:140 without `re.ASCII` sees `é` as a word character, so
  there is no boundary and the port refuses. With the flag the brief requires, `é` is a non-word character, the boundary matches,
  and the port counts while bash says `set: pipefailé: invalid option name`. It joins X1a/X1c, which are hollow at the
  PIN in both flag modes: `\b` accepts any character bash keeps in the option word.
- **X1d and X3 are hollow greens `re.ASCII` closes**: `\w*o\s+pipefail` at V@3f531c4:140
  and `(?<!\\)\s)#` at V@3f531c4:119 were both Unicode at the PIN.
- **X2a-X2e are H2/H6 shapes the literal rules (b)/(e) do not reach**: the `trap`/`exec` is not at a segment start.
  X2c/X2d are what `with_pipefail` itself returns for `trap 'exit 0' EXIT; pytest | tail` / `exec true; pytest | tail`.
- **FNe/FNd become false negatives** under (e)/(d): `exec 2>&1` only redirects, and `echo \\` + newline is an escaped
  backslash, not a continuation. Cheap direction.
- **D3 flips under the flag on `(?!\s*tail\b)` at V@3f531c4:197** (`with_pipefail` now rewrites, like Canny) **and stays
  harmless**: bash exits 127 either way.

## 3. What changed (uncommitted working-tree edits; the coordinator commits)

`V` 273 → 351 lines, sha256/16 `8420e9a202de6afb` → `d9f71bb3962bdb4a`. `T` 302 → 490 lines, `a9aedce65126da71` →
`195c1b6378adaad8`. `git diff --stat`: 2 files changed, 286 insertions(+), 20 deletions(-). Nothing else in the tree touched
(the report is new).

**V — code**

| item | where | what |
|---|---|---|
| R1 | V:172, V:174 | `flags=re.ASCII` on both `re.sub` calls in `def executed` (by keyword: a fourth positional argument is `count`) |
| R1 | V:195 | `flags=re.ASCII` on the pipefail scan — closes H3 |
| R1 | V:200 | `flags=re.ASCII` on `re.split(r"[;\n]", bare` (by keyword: a third positional argument is `maxsplit`) |
| R1 | V:223 | `flags=re.ASCII` on the lone-`&` test `(?<!>)&(?!>)` |
| R1 | V:257 | `flags=re.ASCII` on the `with_pipefail` tail test `(?!\s*tail\b)` |
| R2 | V:140-141 | `_TRAP` and `_EXEC_OR_COPROC`, compiled with `re.ASCII`, matched at a segment start |
| R2 | V:144-152 | `def _hides_status`: (a) `"||" in last` V:147 · (b) `_TRAP.match(s)` V:148 · (c) `"\r" in bare` V:149 · (d) `"\\\n" in bare` V:150 · (e) `_EXEC_OR_COPROC.match(s)` V:151 |
| R2 | V:210-213 | `if _hides_status(bare, segments, last)` returns False, placed AFTER `user_re = _compile_patterns(patterns)` (V:208) so an invalid pattern still raises |
| R2 | V:217 | comment only: the ported per-part `if "||" in part:` (checks.ts:69) is now subsumed by rule (a); kept for fidelity |
| R6 | V:287-290 | `if args[i + 1] == "":` → `--pattern value is empty`, exit 2 |
| R5 | V:305-314 | more than one word after `--` → `COMMAND must be one argument, got N; quote it`, exit 2; then `command = command_parts[0] if command_parts else ""` replaces the `" ".join` |
| R7 | V:332-337 | `except UnicodeEncodeError` around `print(result)` → `cannot write the rewrite: …`, exit 2 |

**V — module docstring (R1, R3, F10)**

- V:7-17 `Regex semantics`: names every regex that runs with the flag (now all of them), says what the flag does to a Unicode
  space in `set -o pipefail` and before `#`, and names its cost (declared below).
- V:19-24 Deviation 1 keeps its text and gains the F10 sentence (V:22 `means invalid in Python's`): `(?i)` valid here and
  dead in Canny, a variable-length lookbehind valid in Canny and a `ValueError` here.
- V:26-35 `AMENDMENT C1-A2` rules (a)-(e) as the brief words them, the meaning of "segment", and the two cheap-direction
  false negatives (d) and (e) buy.
- V:37-55 `Known hollow greens`: H7, H8, H9 (broadened to (b)/(e), which are first-word rules too), the here-doc
  terminator, and two families this lane measured — (b)/(e) off a segment start (with the `with_pipefail` rewrite that
  builds one), and `pipefail\b` with a kept suffix (with the non-ASCII case the flag opens). One example each; each pinned.
- The MIT notice and the `Ported by agent-factory (D-052)` sentence are unchanged.

**T**

| item | where | what |
|---|---|---|
| R8 F8 | T:195-203 | `def test_leading_spaces_do_not_count` keeps `   echo tsc` and adds `"\xa0echo tsc"` (T:203), which only a `str.strip()` can clean (`\s` under `re.ASCII` cannot match U+00A0); the comment names the real mechanism |
| comment | T:206-212 | `def test_pipefail_does_not_excuse_or_true`: its "kills M5" became false under rule (a); the comment now says so |
| R8 F11 | T:262-272 | `def test_cli_usage_error_no_dashdash` passes `"--pattern", "^npm test$"` (T:267) and asserts `missing -- before COMMAND` |
| F11 keep | T:275-283 | new `def test_cli_usage_error_unknown_option` carries the old argv `"npm test"` so that branch keeps its test |
| helper | T:330-331 | `def _one_stderr_line`: exactly one newline-terminated non-empty stderr line |
| R1 | T:337-362 | four rows: H3 via the API `def test_ascii_pipefail_scan_refuses_nbsp_in_set` (T:337) and the CLI `def test_ascii_pipefail_scan_refuses_nbsp_in_set_cli` (T:343); the comment-strip flag `def test_ascii_comment_strip_keeps_nbsp_hash` (T:353); the tail-test flag `def test_ascii_tail_test_needs_an_ascii_space_before_tail` (T:360) |
| R2 | T:367-381 | `def test_c1_a2_refuses_status_hiding_shapes`, ids `a_H1`, `a_H1b`, `b_H2`, `c_H4`, `d_H5`, `e_H6`, `e_H6b` |
| R2 order | T:384-386 | `def test_invalid_pattern_raises_even_when_c1_a2_refuses` |
| R3 | T:390-435 | `def _declared_limit` (strict, `raises=AssertionError`) and the eight limit tests listed under this table |
| R4 | T:438-450 | `def test_verify_c1_survivors`, ids `N5_ascii_verify`, `N10_not_a_check_arg`, `N11_empty_patterns`, `N13_set_anchor`: True, True, False, False |
| R5-R7 | T:453-490 | `def test_cli_refuses_more_than_one_command_word` (T:454), `def test_cli_refuses_empty_pattern` (T:467), `def test_cli_with_pipefail_encoding_failure_exits_2` (T:479; argv byte `b"\xffnpm test | tail -5"`, env `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8:strict` and nothing else) |

Canny's frozen tables (T:39-189: the 27 rows, `CHECKS`, `HIDES`, `KEEPS`, the override, the pipefail config test) are
byte-for-byte untouched; §5b proves their answers too.

The eight R3 limit tests, one per docstring example:

- H7: `def test_limit_h7_builtin_swallows_status` (T:399)
- H8: `def test_limit_h8_function_shadows_check` (T:404)
- H9: `def test_limit_h9_path_bypasses_denylist` (T:409)
- here-doc: `def test_limit_heredoc_terminator` (T:414)
- (b)/(e) off a segment start: `def test_limit_trap_after_and` (T:419)
- the `with_pipefail` rewrite: `def test_limit_with_pipefail_rewrites_trap` (T:424)
- `pipefail-x`: `def test_limit_pipefail_option_word_suffix` (T:429)
- `pipefail` + U+00E9, the cost of R1: `def test_limit_pipefail_non_ascii_suffix` (T:434)

## 4. RED, then GREEN

**RED — the final T against the PIN V** (scratch tree: `scripts/` = `git show 3f531c4:scripts/verify_command.py`, sha256/16
`8420e9a202de6afb`; `tests/` = the final T, so `parents[1]` resolves to the PIN V):

```
$ cd <scratch>/redpin && /root/venv-agent-factory/bin/python -m pytest tests/test_verify_command.py -q -p no:cacheprovider --basetemp=/tmp/c1r1p/bt -rfX
FAILED tests/test_verify_command.py::test_ascii_pipefail_scan_refuses_nbsp_in_set
FAILED tests/test_verify_command.py::test_ascii_pipefail_scan_refuses_nbsp_in_set_cli
FAILED tests/test_verify_command.py::test_ascii_comment_strip_keeps_nbsp_hash
FAILED tests/test_verify_command.py::test_ascii_tail_test_needs_an_ascii_space_before_tail
FAILED tests/test_verify_command.py::test_c1_a2_refuses_status_hiding_shapes[a_H1]
FAILED tests/test_verify_command.py::test_c1_a2_refuses_status_hiding_shapes[a_H1b]
FAILED tests/test_verify_command.py::test_c1_a2_refuses_status_hiding_shapes[b_H2]
FAILED tests/test_verify_command.py::test_c1_a2_refuses_status_hiding_shapes[c_H4]
FAILED tests/test_verify_command.py::test_c1_a2_refuses_status_hiding_shapes[d_H5]
FAILED tests/test_verify_command.py::test_c1_a2_refuses_status_hiding_shapes[e_H6]
FAILED tests/test_verify_command.py::test_c1_a2_refuses_status_hiding_shapes[e_H6b]
FAILED tests/test_verify_command.py::test_limit_pipefail_non_ascii_suffix - [...
FAILED tests/test_verify_command.py::test_cli_refuses_more_than_one_command_word
FAILED tests/test_verify_command.py::test_cli_refuses_empty_pattern - Asserti...
FAILED tests/test_verify_command.py::test_cli_with_pipefail_encoding_failure_exits_2
15 failed, 51 passed, 7 xfailed in 0.52s
rc=1
```

Each red is its target assertion (`--tb=line`): `assert True is False` for the two R1 `is_verify` rows (H3 via the API,
the comment strip) and the seven C1-A2 rows, `assert 0 == 1` for the H3 CLI row,
`assert 'set -o pipefail && npm test |\xa0tail -5' is None` for the tail test,
`[XPASS(strict)] the cost of re.ASCII on the pipefail scan` for the `pipefail` + U+00E9 limit (the PIN refused that shape:
the limit is caused by R1, as §2b predicted), `assert 0 == 2` for the one-word and empty-pattern refusals, `assert 1 == 2`
for the encoding failure. The R4 rows, the ordering guard, the two re-aimed CLI tests and the leading-whitespace test pass
on the PIN: they pin mechanisms the PIN already had, and they are proven by mutants instead (§6).

**GREEN — the final T against the final V:** `65 passed, 8 xfailed` (the gate runs are pasted in §7).

## 5. Evidence on the final V (`d9f71bb3962bdb4a`)

### 5a. The brief's oracle script (copied verbatim; every check stubbed to `exit 3`; bash under `env -i`)

```
$ /usr/bin/python3 shapes.py <scratch>/stub3
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
rc=0
```

H1-H6b: does-not-count, CLI rc 1. CTRL and CTRL2 still count. The required H3 result holds.

### 5b. Canny's frozen tables, answer for answer (PIN V vs final V)

`frozen.py` reads the tables from each T's own source (`ast` for the 27 rows, a module import for `CHECKS`/`HIDES`/`KEEPS`),
never retyped, checks the two T files carry identical tables, then compares every frozen answer:

```
$ /root/venv-agent-factory/bin/python frozen.py <pin T> <pin V> <final T> <final V>
tables identical: 27rows=True (27) CHECKS=True (11) HIDES=True (154) KEEPS=True (143)
answers compared: 328  differing: 0  27rows-as-expected(cand)=27/27  hides-counted(cand)=0  keeps-refused(cand)=0
rc=0
```

328 = 27 rows + 154 HIDES + 143 KEEPS + 2 override + 1 config `is_verify` + 1 config `with_pipefail`. **Negative control of
the comparator** (its zero must be able to go red): the same script against a scratch V whose last-segment scan reads the
FIRST segment printed `answers compared: 328  differing: 71  27rows-as-expected(cand)=23/27  hides-counted(cand)=33
keeps-refused(cand)=33`, `rc=1`.

### 5c. The §2b shapes on the final V (the predictions, confirmed)

```
$ /usr/bin/python3 probe.py <final V> stub3 stub0 extra
X1a  port=counts  rc_fail=0   rc_pass=0   HOLLOW 'set -o pipefail-x; pnpm test | tail'
X1b  port=counts  rc_fail=0   rc_pass=0   HOLLOW 'set -o pipefailé; pnpm test | tail'
X1c  port=counts  rc_fail=0   rc_pass=0   HOLLOW 'set -o pipefail\xa0; pnpm test | tail'
X1d  port=refuses rc_fail=0   rc_pass=0   ok     'set -éo pipefail; pnpm test | tail'
X2a  port=counts  rc_fail=0   rc_pass=0   HOLLOW "true && trap 'exit 0' EXIT; pytest"
X2b  port=counts  rc_fail=0   rc_pass=0   HOLLOW 'true && exec true; pytest'
X2c  port=counts  rc_fail=0   rc_pass=0   HOLLOW "set -o pipefail && trap 'exit 0' EXIT; pytest | tail"
X2d  port=counts  rc_fail=0   rc_pass=0   HOLLOW 'set -o pipefail && exec true; pytest | tail'
X2e  port=counts  rc_fail=0   rc_pass=0   HOLLOW "{ trap 'exit 0' EXIT; }; pytest"
X3   port=refuses rc_fail=0   rc_pass=0   ok     'pytest\xa0#; exit 0'
X3b  port=counts  rc_fail=3   rc_pass=0   ok     'true \xa0# ; pytest'
FNe  port=refuses rc_fail=3   rc_pass=0   FN     'exec 2>&1; pytest'
FNd  port=refuses rc_fail=3   rc_pass=0   FN     'echo \\\\\npytest'
D3   port=counts  rc_fail=127 rc_pass=127 ok     'set -o pipefail && npm test | tailé'
rc=0
```

Net on this 14-shape set, PIN → final (counted from the probe output: `HOLLOW=9 FN=1 ok=4` → `HOLLOW=8 FN=2 ok=4`):
hollow greens 9 → 8 (closed: X1d, X3; opened: X1b); false negatives 1 → 2 (X3b fixed; FNe, FNd new). The set was built
to find side effects, so these counts are not a rate.

### 5d. Every docstring claim, checked on the final V

The eight declared examples (V:41-55, from `export R=$(pytest)` on) and the H9 broadening to (b)/(e), through bash:

```
$ /usr/bin/python3 probe.py <final V> stub3 stub0 doc
H7   port=counts  rc_fail=0   rc_pass=0   HOLLOW 'export R=$(pytest)'
H8   port=counts  rc_fail=0   rc_pass=0   HOLLOW 'pytest(){ return 0; }; pytest'
H9   port=counts  rc_fail=0   rc_pass=0   HOLLOW '/bin/echo tsc'
HD   port=counts  rc_fail=0   rc_pass=0   HOLLOW "cat <<'pytest'\nfoo\npytest"
TRa  port=counts  rc_fail=0   rc_pass=0   HOLLOW "true && trap 'exit 0' EXIT; pytest"
WPr  port=counts  rc_fail=0   rc_pass=0   HOLLOW "set -o pipefail && trap 'exit 0' EXIT; pytest | tail"
PFx  port=counts  rc_fail=0   rc_pass=0   HOLLOW 'set -o pipefail-x; pnpm test | tail'
PFe  port=counts  rc_fail=0   rc_pass=0   HOLLOW 'set -o pipefailé; pnpm test | tail'
9b1  port=counts  rc_fail=0   rc_pass=0   HOLLOW "\\trap 'exit 0' EXIT; pytest"
9b2  port=counts  rc_fail=0   rc_pass=0   HOLLOW "builtin trap 'exit 0' EXIT; pytest"
9e1  port=counts  rc_fail=0   rc_pass=0   HOLLOW "'exec' true; pytest"
9e2  port=counts  rc_fail=0   rc_pass=0   HOLLOW 'builtin exec true; pytest'
9e3  port=counts  rc_fail=0   rc_pass=0   HOLLOW 'command exec true; pytest'
rc=0
$ with_pipefail on the final V (env -i PATH=/usr/bin:/bin /usr/bin/python3)
"set -o pipefail && trap 'exit 0' EXIT; pytest | tail"
'set -o pipefail && exec true; pytest | tail'
F10 (?i) valid here: True
F10 lookbehind raises: invalid pattern: '(?<=a+)b': look-behind requires fixed-width pattern
```

The JS half of the F10 sentence (dead in Canny / valid in Canny) is VERIFY-C1's measurement; Canny is not run here.

## 6. The mutant table (final V `d9f71bb3962bdb4a`, final T `195c1b6378adaad8`)

`mutants.py` builds each mutant in its own scratch tree (`scripts/` + `tests/`), requires every substitution to match
exactly once, then `py_compile`s V and T and collects T (must be 73 items). A mutant failing either step prints INVALID and
is never a kill (AF-AP-78). Driver totals: **KILLED=24 SURVIVED=5 INVALID=0**.

| id | mutation | compiles · collect | result | killed by |
|---|---|---|---|---|
| R2a | rule (a) removed | yes · 73 | 2 failed, 63 passed, 8 xfailed | `[a_H1]`, `[a_H1b]` |
| R2b | rule (b) removed | yes · 73 | 1 failed, 64 passed, 8 xfailed | `[b_H2]` |
| R2c | rule (c) removed | yes · 73 | 1 failed, 64 passed, 8 xfailed | `[c_H4]` |
| R2d | rule (d) removed | yes · 73 | 1 failed, 64 passed, 8 xfailed | `[d_H5]` |
| R2e | rule (e) removed | yes · 73 | 2 failed, 63 passed, 8 xfailed | `[e_H6]`, `[e_H6b]` |
| R2g | the pre-filter moved above the patterns compile | yes · 73 | 1 failed, 64 passed, 8 xfailed | `test_invalid_pattern_raises_even_when_c1_a2_refuses` |
| R1-195 | `re.ASCII` dropped from the pipefail scan | yes · 73 | 3 failed, 63 passed, 7 xfailed | `test_ascii_pipefail_scan_refuses_nbsp_in_set`, `…_cli`, `test_limit_pipefail_non_ascii_suffix` (XPASS strict) |
| R1-174 | `re.ASCII` dropped from the comment strip | yes · 73 | 1 failed, 64 passed, 8 xfailed | `test_ascii_comment_strip_keeps_nbsp_hash` |
| R1-257 | `re.ASCII` dropped from the tail test | yes · 73 | 1 failed, 64 passed, 8 xfailed | `test_ascii_tail_test_needs_an_ascii_space_before_tail` |
| R1-172 | `re.ASCII` dropped from the quoted-string strip | yes · 73 | 65 passed, 8 xfailed | **EQUIVALENT** (below) |
| R1-200 | `re.ASCII` dropped from the segment split | yes · 73 | 65 passed, 8 xfailed | **EQUIVALENT** (below) |
| R1-223 | `re.ASCII` dropped from the lone-`&` test | yes · 73 | 65 passed, 8 xfailed | **EQUIVALENT** (below) |
| R5 | one-word refusal removed, the PIN `" ".join` restored | yes · 73 | 1 failed, 64 passed, 8 xfailed | `test_cli_refuses_more_than_one_command_word` |
| R6 | empty `--pattern` refusal removed | yes · 73 | 1 failed, 64 passed, 8 xfailed | `test_cli_refuses_empty_pattern` |
| R7 | encoding-failure guard removed | yes · 73 | 1 failed, 64 passed, 8 xfailed | `test_cli_with_pipefail_encoding_failure_exits_2` |
| N5 | `re.ASCII` dropped from `VERIFY[0]` (VERIFY-C1 survivor) | yes · 73 | 1 failed, 64 passed, 8 xfailed | `[N5_ascii_verify]` |
| N10 | `_not_a_check(check)` → `_not_a_check(part)` (survivor) | yes · 73 | 1 failed, 64 passed, 8 xfailed | `[N10_not_a_check_arg]` |
| N11 | `user_re is not None` → `user_re` (survivor) | yes · 73 | 1 failed, 64 passed, 8 xfailed | `[N11_empty_patterns]` |
| N13 | the `(?:^|[;&\n])` anchor dropped (survivor) | yes · 73 | 1 failed, 64 passed, 8 xfailed | `[N13_set_anchor]` |
| N8 | the missing-`--` branch deleted (VERIFY-C1: EQUIVALENT) | yes · 73 | 1 failed, 64 passed, 8 xfailed | `test_cli_usage_error_no_dashdash` |
| F8s | `.strip()` → `.rstrip()` at the segment, part and check | yes · 73 | 2 failed, 63 passed, 8 xfailed | `test_leading_spaces_do_not_count` at T:203 (`"\xa0echo tsc"`; T:202 `is_verify("   echo tsc")` passes), `test_pipefail_with_config` |
| M9 | `^\s*` dropped from `_PRINTS_OR_INSPECTS` | yes · 73 | 65 passed, 8 xfailed | **EQUIVALENT** (every check is stripped first; kept by choice, §8 D5) |
| M5 | the per-part `\|\|` rule (checks.ts:69) dropped | yes · 73 | 65 passed, 8 xfailed | **EQUIVALENT** (rule (a) refuses every such input first) |
| L-H7 | close H7 in scratch (refuse `export …`) | yes · 73 | 1 failed, 65 passed, 7 xfailed | `test_limit_h7_builtin_swallows_status` (XPASS strict) |
| L-H8 | close H8 (refuse `(){`) | yes · 73 | 1 failed, 65 passed, 7 xfailed | `test_limit_h8_function_shadows_check` (XPASS strict) |
| L-H9 | close H9 (refuse a check word given by path) | yes · 73 | 1 failed, 65 passed, 7 xfailed | `test_limit_h9_path_bypasses_denylist` (XPASS strict) |
| L-HD | close the here-doc (refuse `<<`) | yes · 73 | 1 failed, 65 passed, 7 xfailed | `test_limit_heredoc_terminator` (XPASS strict) |
| L-TR | close (b) off a segment start (trap at any `&&`-part start) | yes · 73 | 2 failed, 65 passed, 6 xfailed | `test_limit_trap_after_and`, `test_limit_with_pipefail_rewrites_trap` (XPASS strict) |
| L-PF | close `pipefail\b` (require a separator after `pipefail`) | yes · 73 | 2 failed, 65 passed, 6 xfailed | `test_limit_pipefail_option_word_suffix`, `test_limit_pipefail_non_ascii_suffix` (XPASS strict) |

**The five survivors are equivalent, each shown:**

- R1-172 / R1-200 / R1-223: `re.ASCII` changes only `\w \W \b \B \d \D \s \S` and case folding; the three patterns hold none
  of them (V:172 `"", command, flags=re.ASCII`, V:200 `[;\n]`, V:223 `(?<!>)&(?!>)`). Measured: over every one of the 1,112,064 non-surrogate
  code points, in five contexts that exercise each pattern's literals, the match spans are identical with and without the
  flag (`spans identical … True` ×3). The flags are there because R1 says every regex carries one.
- M9: VERIFY-C1's F8 measurement stands. This lane kept Canny's literal and re-aimed the row instead (F8s is the proof).
- M5: every input that reaches the per-part check has no `||` in `last` (rule (a) returned first), and a part is a
  substring of `last`.

**The L-rows are information, not repairs:** each shows its strict xfail asserts the safe answer through the real
function, and that a fix fails the suite until the docstring and the pin are updated. In every L-row the other 65 tests
pass, so none of those scratch fixes moves a frozen answer — useful to the coordinator (§8 D1, D2), never applied here.

## 7. Gates (pasted verbatim; 2026-09-23 05:53:14Z)

```
d9f71bb3962bdb4a 351 scripts/verify_command.py
195c1b6378adaad8 490 tests/test_verify_command.py
$ bash scripts/pc_suite.sh set-id -- tests/test_verify_command.py
1 files set=d9bd6dad2d0e
$ (repo root, run 1) /root/venv-agent-factory/bin/python -m pytest tests/test_verify_command.py -q -p no:cacheprovider --basetemp=/tmp/c1r1g/bt1
..........................................................xxxxxxxx...... [ 98%]
.                                                                        [100%]
65 passed, 8 xfailed in 0.47s
rc=0
$ (repo root, run 2) /root/venv-agent-factory/bin/python -m pytest tests/test_verify_command.py -q -p no:cacheprovider --basetemp=/tmp/c1r1g/bt2
..........................................................xxxxxxxx...... [ 98%]
.                                                                        [100%]
65 passed, 8 xfailed in 0.46s
rc=0
$ (cd /tmp && /root/venv-agent-factory/bin/python -m pytest /home/user/agent-factory/tests/test_verify_command.py -q -p no:cacheprovider --basetemp=/tmp/c1r1g/bt3)
..........................................................xxxxxxxx...... [ 98%]
.                                                                        [100%]
65 passed, 8 xfailed in 0.48s
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

The set id is the PIN's (`d9bd6dad2d0e`): it hashes the path string, not the content. The count moved from `45 passed`
to `65 passed, 8 xfailed` on that set.

## 8. DISCREPANCIES and deviations from the brief (read these first)

- **D1 — R1 opens one hollow green: `set -o pipefail` followed by U+00E9.** The brief requires `re.ASCII` on the pipefail
  scan (V:195, `pipefail\b", bare, flags=re.ASCII`) to close H3, and it does. The same flag makes `\b` match before a
  non-ASCII letter, so `set -o pipefailé; pnpm test | tail` now counts while bash prints `invalid option name` and exits 0.
  The PIN refused it (§2b X1b; §4 shows its pin XPASSing on the PIN). It is a new member of an older family:
  `pipefail\b` accepts any character bash keeps in the option word, and `pipefail-x` / `pipefail` + NBSP are hollow at the
  PIN in both flag modes (Canny has them too). Declared in V:52-55 (`The pipefail scan ends in`), pinned by
  `def test_limit_pipefail_option_word_suffix` (T:429) and `def test_limit_pipefail_non_ascii_suffix` (T:434).
  **Not fixed:** the contract has no rule for it. A candidate measured in scratch only: `pipefail(?=[\s;&|]|$)` (mutant
  L-PF) keeps the other 65 tests green; it has NOT been graded against bash for false negatives.
- **D2 — Rules (b) and (e), as worded ("any segment begins with"), miss a `trap`/`exec`/`coproc` that is not at a segment
  start** (§2b/§5c X2a-X2e, hollow at the PIN and after). The sharpest case is the port's own `def with_pipefail`: it
  prepends `set -o pipefail && `, which moves the first word off the segment start. For `trap 'exit 0' EXIT; pytest | tail`
  it returns `set -o pipefail && trap 'exit 0' EXIT; pytest | tail`, and `is_verify` counts that rewrite while bash exits 0
  (§5d). Declared in V:48-51 (`see only segment starts`), pinned by `def test_limit_trap_after_and` (T:419) and
  `def test_limit_with_pipefail_rewrites_trap` (T:424). **Not fixed:** widening the rule changes the design this contract
  froze. A candidate measured in scratch only: `trap` at any `&&`-part start (L-TR) keeps the other 65 tests green; its
  (e) analogue and the other positions (`{`, `||`, `|`) are not measured.
- **D3 — H9 is declared wider than the brief words it.** Rules (b) and (e) are first-word rules, and the same bypasses
  defeat them: `\trap`, `builtin trap`, `'exec'`, `builtin exec`, `command exec` are 5/5 hollow (§5d).
  V:44-45 (`the first-word rules`) names them.
- **D4 — Four declared limits beyond the brief's four** (the four limit tests named in D1 and D2), so the docstring's
  promise that "Each is pinned by a strict xfail test" holds for every example it gives. All eight go through
  `def _declared_limit` (T:393-395), which sets `raises=AssertionError`: only the safe-answer assertion satisfies an xfail.
- **D5 — R8/F8: the brief's mechanism is imprecise, so its first option was taken in a precise form.** The brief (after
  VERIFY-C1) says the leading-whitespace work is done by "the .strip()" at line 166 of the PIN V.
  At the PIN that strip, V@3f531c4:166 `check = part.split("|")[0].strip()`, never removes LEADING whitespace:
  the part was already stripped at V@3f531c4:156 (`part = raw.strip()`), and the first strip to act on `   echo tsc`
  is the segment strip, V@3f531c4:145 `segments = [s.strip() for s in`. The three strips back each other up, so no row can aim at one of them. The row
  `"\xa0echo tsc"` (T:203) aims at the strips together: F8s reds exactly that line while `   echo tsc` (T:202) survives on
  `^\s*`. `^\s*` stays in `_PRINTS_OR_INSPECTS` (V:119) so the literal still matches checks.ts:35-36; M9 stays EQUIVALENT
  by that choice. The brief's other option (drop `^\s*`) was not taken.
- **D6 — R8/F11: VERIFY-C1's suggested argv does not reach the branch.** Measured: `/usr/bin/python3
  scripts/verify_command.py npm test` → `unknown option: npm`, rc 2 (V:298, `unknown option`). The re-aimed test passes
  `"--pattern", "^npm test$"` (T:267): two argv words the option loop consumes, so the parser reaches `missing -- before
  COMMAND` (V:302), and the test asserts that exact line. N8 is now KILLED. The old one-word argv moved to the new
  `def test_cli_usage_error_unknown_option` (T:275) so the unknown-option branch keeps its test.
- **D7 — Rules (c) and (d) read the executed text, as the amendment words it**, not the raw command (VERIFY-C1's R4 said
  "a `\r` anywhere in the command"). A CR or continuation inside quotes or a comment is not refused, and bash does not act
  on either there. Measured on the final V, all three count and bash carries the status (rc 3 failing, rc 0 passing):
  `pytest "a\rb"`, `pytest # note\r`, `echo "a\\\nb"; pytest`.
- **D8 — Smaller additions beyond the brief's letter**, each traced to this change: the ordering guard
  `def test_invalid_pattern_raises_even_when_c1_a2_refuses` (T:384; R2g reds it); the R1 rows for the comment-strip and
  tail-test flags and the H3 CLI row (named in §3); `def _one_stderr_line` (T:330); the corrected comment in
  `def test_pipefail_does_not_excuse_or_true` (T:206-212).
- **D9 — The ported per-part check is now dead by construction** (V:217, `if "||" in part:`; M5 EQUIVALENT). Kept,
  with a comment, because it is the checks.ts:69 line.

## 9. Self-attack — the three likeliest ways this change is wrong

1. **A flag that reads right and does nothing.** `re.sub(p, r, s, re.ASCII)` passes 256 as `count`, and
   `re.split(p, s, re.ASCII)` passes it as `maxsplit`. Ruled out: all six calls pass the flag by keyword,
   `flags=re.ASCII` at V:172, V:174, V:195, V:200, V:223 and V:257. The three that change answers are each killed when dropped (R1-195, R1-174,
   R1-257). The three that cannot are proven equivalent over every code point (§6).
2. **Rules that refuse real checks, so nobody can pass the gate.** Ruled out for Canny's corpus: 328/328 frozen answers
   unchanged, including all 143 KEEPS (§5b), and the comparator's zero can go red (71 differing on a planted mutant). Not
   ruled out in general: (d) and (e) refuse two measured status-carrying shapes (FNe `exec 2>&1; pytest`, FNd). A
   common idiom, `exec >log 2>&1; pytest`, falls under FNe (inferred from FNe, not run separately). Cheap direction;
   declared at V:33-35 (`exec 2>&1; pytest`).
3. **Pins that look live and are not.** A bare `xfail` passes on any exception, and a row written from the code's own
   assumption is a mirror. Ruled out: every limit uses `raises=AssertionError` (T:393-395); each is shown live by a
   closing mutant (the L-rows: XPASS strict → FAILED); the RED run shows every new passing row red on the PIN for its
   exact reason; every hollow-green claim in the docstring was graded by bash, not by the port (§5d). The R7 test runs
   in a fixed two-variable env (`PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8:strict`), so the host locale cannot turn it green
   or red; it passed from the root and from `/tmp`.

## 10. NOT-done (first-class)

- **Not closed, declared:** H7, H8, H9, the here-doc terminator, (b)/(e) off a segment start (including the
  `with_pipefail` rewrite), and `pipefail\b` with a kept suffix (including the `é` case R1 opened). Each is a strict xfail
  (`_declared_limit`, T:398-435).
- **No commit, no push, no PR**, per the brief. V, T and this report are working-tree edits for the coordinator.
- **No PC run; no real check binaries.** Bash 5.2.21 in the sandbox; every check word is a stub that exits 3 or 0.
- **Canny not run.** The JS half of F10 is VERIFY-C1's measurement.
- **The candidate fixes in D1/D2 (L-PF, L-TR) were graded against T only**, never against bash for false negatives.
- **Adjacent, reported, not fixed:** `_NEGATED`'s `^\s*` (V:127) is dead for the same reason as M9's (one-off scratch
  mutant `r"^!"`: compiles, `73 tests collected`, `65 passed, 8 xfailed`); the API still treats `patterns=[""]` as a
  catch-all (only the CLI refuses an empty `--pattern`); `with_pipefail` can return a declared hollow green (D2);
  VERIFY-C1's F7 defects in `C1-report.md` are outside this boundary.
- **`scripts/no_laya_in_gates.py` was not run** (the C1 brief's gate; this brief does not list it).
- **`detect_changes` was run, but it cannot isolate this lane.** `node .gitnexus/run.cjs detect-changes --scope all`
  reads the whole shared tree: `Changes: 7 files, 22 symbols`, `Risk level: medium`, and both `Affected processes` are
  E3's S0-05 `check` flows, not this lane's. The V symbols it lists are `VERIFY`, `is_verify`, `with_pipefail`, `_cli`,
  `command_parts`; the CLI truncates the rest (`... and 7 more`). `VERIFY` is a line-shift artifact: the block from
  `VERIFY = [` to `]` hashes `c0fd854b46d84b3f` at the PIN and in the final V. No re-index was run; nothing is committed,
  and the post-commit hook re-indexes on the coordinator's commit.

## 11. Report lint

Two fix rounds of the three allowed. The first run read `104 refs — OK 67, NEAR 1, MISS 20, UNCHECKABLE 16`: every MISS was
a report line that cited several code lines and carried a token for only some of them, or a PIN-era number written as a
bare `V:NN`. Round 1 added a copied token per cited line and pinned PIN-era numbers as `V@3f531c4:NN`
(`97 refs — OK 95, NEAR 0, MISS 2`). Round 2 fixed the last two (`96 refs — OK 96`). The final run, after the last edits:

```
$ python3 scripts/report_lint.py --min-refs 12 --map V=scripts/verify_command.py --map T=tests/test_verify_command.py tasks/briefs/canny/C1-R1-report.md --root .
report_lint: 96 refs — OK 96, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
rc=0
```

Scratch instruments (session scratchpad `…/scratchpad/c1r1/`, not committed): `shapes.py` (the brief's oracle), `probe.py`,
`frozen.py`, `mutants.py`, the PIN copy `pin/`, the RED tree `redpin/`, the mutant trees `mut/<id>/`, stub dirs `stub3/`,
`stub0/`.
