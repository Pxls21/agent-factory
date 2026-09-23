# VERIFY-C1 — adversarial verify of `scripts/verify_command.py` (Canny `isVerify` port, D-052)

**Lane:** VERIFY-C1, sandbox `adversarial-verifier` (Opus 5). **PIN:** `ea9538a`.
**Aliases:** `V` = `scripts/verify_command.py`, `T` = `tests/test_verify_command.py`.

## OUTCOME

**GATE RECOMMENDATION: `NOT-READY` on one finding — F2 — with F1 returned as a `CONTRACT-DEFECT` for an explicit
amendment.** The port is, as a port, excellent: all three `VERIFY` regexes and all six other literals match `checks.ts`
character for character, the transcribed tables are byte-identical to Canny's, and an independent JS oracle built from
Canny's own literals agrees with the port on **all 495 commands** I put through both (297 Canny product commands, 198
hostile ones) — zero divergences in that set. The suite is 45/45, twice, and from `/tmp`.

F2 is the blocker: **contract item 2 says "compile with `re.ASCII`", the module docstring at `V:7` states that *all*
patterns are, and six of them are not** — and for one of them, the pipefail scan at `V:140` (`\w*o\s+pipefail\b`), the missing flag is what
lets `set<NBSP>-o pipefail; pnpm test | tail` be reported as a check while bash exits 0 with the check failing. The fix
is the contract-mandated flag plus an honest docstring; I measured that it keeps 45/45, 27/27 Canny rows and 297/297
product commands unchanged. It meets every leg of the blocking predicate inside the component boundary.

F1 is *not* a blocker and must not be treated as one: **43 command shapes count while bash returns 0 with the check
failing**, but the port answers exactly as Canny does on every one of them (verified against the JS oracle), so they
falsify the brief's WHY, not the port. They need a contract amendment, which I propose below with six measured rules
that close 23 of a curated 42 of them without moving a single Canny table row.

## IDENTITY (measured this session, sandbox @ `ea9538a`)

```
$ cd /home/user/agent-factory && git log --format='%h %s' -- scripts/verify_command.py tests/test_verify_command.py
9c70322 C1 landed (GATED-PENDING-VERIFY): Canny's verify-command classifier ported to scripts/verify_command.py, with its tables as tests
$ sha256sum … | cut -c1-16 ; wc -l
8420e9a202de6afb  273  scripts/verify_command.py
a9aedce65126da71  302  tests/test_verify_command.py
$ git archive ea9538a … | diff against the working tree
V identical
T identical
$ git -C /home/user/qkal/canny log -1 --format='%h %s'
f2c5e53 chore(release): 0.3.0 (#21)
$ sha256sum … | cut -c1-16
1d3f36a1063542ee  /home/user/qkal/canny/src/checks.ts
d5297358e03e58cc  /home/user/qkal/canny/test/checks.test.ts
0ba25891a959268c  /home/user/qkal/canny/LICENSE
$ /opt/node22/bin/node --version      ->  v22.22.2
$ bash --version | head -1            ->  GNU bash, version 5.2.21(1)-release (x86_64-pc-linux-gnu)
```

Every digest matches the brief's table. The working-tree copies of `V` and `T` are byte-identical to the PIN, so
everything below was measured against the production files themselves — no surrogate.

## Instruments

Three oracles, none of which borrows the module's own logic:

1. **JS oracle** — `…/scratchpad/vc1/work/oracle.js`: Canny's `checks.ts:8-93` re-expressed in JS from the regex
   **literals copied as text** out of `src/checks.ts` (`sed -n '9,11p' src/checks.ts`). Nothing in `/home/user/qkal/canny`
   was run, built, installed, imported or required.
2. **bash oracle** — `…/scratchpad/vc1/work/bash_oracle.sh`: each command run twice under `timeout 10 bash -c`, once with
   every check word stubbed to `exit 3` and once to `exit 0` (56 stub executables on a scratch `PATH`, plus `./gradlew`).
   A command is **status-preserving** iff `rc(check fails) != 0` **and** `rc(check passes) == 0`. A command the port
   **counts** whose `rc(check fails) == 0` is a **hollow green**.
3. **the port itself**, loaded by path from `/home/user/agent-factory/scripts/verify_command.py`.

---

# ITEM 1 — Port fidelity, regex by regex

**Reproduced.** Every regex literal in `V` is character-identical to its `checks.ts` counterpart. Method: `node` printed
`RegExp.prototype.source` for each literal copied out of `checks.ts`; Python `ast` extracted the string *values* from
`V`; the two lists were `diff`ed.

| literal | `checks.ts` | `V` | identical | `re.ASCII` in `V` |
|---|---|---|---|---|
| `VERIFY[0]` (33 alternatives, `pytest`…`nox`) | `:9` | `V:52-58` | yes | yes |
| `VERIFY[1]` (20, `tsc`…`webpack`) | `:10` | `V:61-66` | yes | yes |
| `VERIFY[2]` (25, `eslint`…`shellcheck`) | `:11` | `V:69-74` | yes | yes |
| `PRINTS_OR_INSPECTS` (`which|type|command|man|head|tail|git`) | `:35-36` | `V:80` | yes | yes |
| `ASKS_ONLY` | `:39` | `V:85` | yes | yes |
| `NEGATED` | `:42` | `V:88` | yes | yes |
| quoted-string strip (`bare = re.sub`) | `:50` | `V:117` | yes | **no** |
| comment strip (`$1` → `r"\1", bare`, `#[^\n]*`) | `:50` | `V:119` | yes | **no** |
| pipefail scan (`\w*o\s+pipefail\b`) | `:61-62` | `V:140` | yes | **no** |
| segment split (`re.split(r"[;\n]", bare)`) | `:63` | `V:145` | yes | n/a (no class) |
| lone-`&` (`r"(?<!>)&(?!>)"`) | `:72` | `V:163` | yes | n/a (no class) |
| `withPipefail` tail test (`(?!\s*tail\b)`) | `:93` | `V:197` | yes | **no** |

Alternative counts re-derived by a top-level `|` split of the copied literals: `checks.ts:9`=33, `:10`=20, `:11`=25,
**total 78** — matches the brief.

Control-flow fidelity, read from `checks.ts:58-80` against `V:123-176` (`def is_verify(`): `[…matchAll].at(-1)?.[1] === "-"` → the
`for m in re.finditer(` loop at `V:139-142` whose last iteration wins (same "last one wins"); `.findLast(Boolean) ?? ""`
→ the `reversed(segments)` scan at `V:147-150` with `last = ""` default; `split("&&")` → `V:155`; `part.includes("||")` → `if "||" in part:` at `V:157`
(**per `&&`-part in both**, confirmed by static read of `checks.ts:69`); `!pipefail && part.includes("|")` → `not pipefail and "|" in part` at `V:159`;
`part.split("|")[0]!.trim()` → `part.split("|")[0].strip()` at `V:166`; `.some()` short-circuit → the early `return True` at `V:171`/`V:174`.
`config.verify ? … : VERIFY` → `if user_re is not None` at `V:169`: **JS `[]` is truthy, and `patterns=[]` never counts in
the port too** — measured, they agree.

**F-D1 … F-D4 — the four JS/Python divergences I could build an input for** (`port` vs the JS oracle, 35-input Unicode
corpus + a patterns matrix):

| id | input | port | Canny (JS) | why | direction |
|---|---|---|---|---|---|
| D1 | `tsc<NBSP>--help`, `<U+3000>`, `<U+202F>`, `<U+FEFF>` | counts | does not | `_ASKS_ONLY` at `V:85` carries `re.ASCII`, JS `\s` matches Unicode spaces | **contract-sanctioned** (item 2, pinned by `assert is_verify(` … `is True` at `T:218`) |
| D2 | `set -o pipefailé; pnpm test \| tail` | does not count | counts | `V:140` (`\w*o\s+pipefail\b`) has **no** `re.ASCII`, so `\b` is Unicode and `pipefailé` has no boundary | safe (port refuses) |
| D3 | `with_pipefail("npm test \| tailé")` | `None` | rewrites | `V:197` (`(?!\s*tail\b)`) has **no** `re.ASCII`, same `\b` | safe (port refuses) |
| D4 | `patterns=["^npm\\stest$"]` vs `npm<NBSP>test` | does not count | counts | user patterns compiled with `re.ASCII` at `V:105`, JS `new RegExp(p)` has Unicode `\s` | safe |

D1 is the declared deviation. D2–D4 are undeclared — see **F2**.

---

# ITEM 2 — THE HOLLOW-GREEN CLASS (bash is the oracle)

**Reproduced.** 495 commands through the port, the JS oracle and bash. Canny's own tables first:

```
### T:121-136 HIDES  (11 x 14 = 154; none may count): n=154  port==JS-oracle on 154/154
  HOLLOW GREENS (port counts, bash rc==0 with the check failing): 0
### T:138-152 KEEPS  (11 x 13 = 143; all must count): n=143  port==JS-oracle on 143/143
  HOLLOW GREENS: 0     FALSE NEGATIVES (port refuses, bash preserves status): 0
```

**Every one of the 154 hiding forms is a real hide and every one of the 143 keeping forms is a real keep.** (The 22
"status-preserving" hits my harness reports inside HIDES are its own artefact: the `--help` and `git commit -m "…"` rows
hide *meaning*, not status, and a stub that exits 3 for `--help` is not the real program. Named here so the number is not
read as a finding.)

Then 198 hostile commands (plus a 16-command Unicode/CRLF corpus). **43 distinct shapes count while bash exits 0 with
the check stubbed to fail** — 26 from the first hostile batch, 14 from the second, 3 more from the Unicode corpus (two
of its five rows are shapes already counted, re-run with another check word). The port answers identically to the JS
oracle on all 198 hostile commands, so every one of these is Canny's answer too.

## THE HOLLOW-GREEN CLASS — nine families

| # | shape (representative) | port | bash rc, check failing | rule it slips | smallest closing rule |
|---|---|---|---|---|---|
| H1 | `pytest && false \|\| true` · `&& echo ok \|\| true` · `&& exit $? \|\| exit 0` (10) | counts | **0** | `V:157` (`if "||" in part:`) tests `\|\|` **per `&&`-part**; part 1 is a clean check | **R1**: test `"\|\|" in last` once, before the loop |
| H2 | `trap 'exit 0' EXIT; pytest` · `trap … ERR` (4) | counts | **0** | no rule looks at `trap`; the trap is in an *earlier* segment, `V:145-150` (`re.split(r"[;\n]", bare)`, `reversed(segments)`) keeps only the last | **R2**: any segment matching `^\s*trap\b` → refuse |
| H3 | `set<NBSP>-o pipefail; pnpm test \| tail` · `set -o<NBSP>pipefail` · `<U+3000>` (3) | counts | **0** | `V:140` (`\w*o\s+pipefail\b`) has no `re.ASCII`, so Unicode `\s` matches the NBSP; bash sees the word `set\xa0-o`, **command not found**, pipefail never set | **R3**: `re.ASCII` on `V:140` — what contract item 2 already requires |
| H4 | `set -o pipefail\r\npytest \| tail` · `set -o pipefail\r; …` (2) | counts | **0** | `\r` is ASCII `\s`, so `pipefail\b` still matches; bash says `set: pipefail: invalid option name` and carries on | **R4**: a `\r` anywhere in the command → refuse |
| H5 | `echo \`<newline>`  pytest` (2) | counts | **0** | `V:145` (`re.split(r"[;\n]", bare)`) splits on `\n`, so a backslash continuation becomes its own "command" and the `echo` denylist never sees the check | **R5**: `\\\n` in the command → refuse |
| H6 | `exec true; pytest` · `coproc pytest` (2) | counts | **0** | `exec` replaces the shell before the last segment runs; `coproc` backgrounds without a lone `&` for `V:163` (`r"(?<!>)&(?!>)"`) | **R8**: any segment matching `^\s*(exec\|coproc)\b` → refuse |
| H7 | `export R=$(pytest)` · `declare` · `readonly` · `typeset` · `FOO=$(pytest) echo done` · `env FOO=$(pytest) true` (6) | counts | **0** | the check matches inside `$( )`; bash returns the **builtin's** status, not the substitution's (a bare `R=$(pytest)` *does* propagate — rc 3 — so the family is exactly the builtin/prefix forms) | needs a first-word rule: refuse `^(export\|declare\|readonly\|typeset\|local)\b` and `^\w+=\S* ` prefixes |
| H8 | `pytest(){ return 0; }; pytest` · `pytest() { :; }` · `function pytest {…}` (3) | counts | **0** | the port matches the check word as *text*; bash resolves a shell function of the same name | refuse any command that contains a function definition (`^\s*(function\s+)?[\w-]+\s*\(\s*\)`) |
| H9 | `/bin/echo tsc` · `env echo tsc` · `eval echo tsc` · `builtin echo tsc` · `\echo tsc` · `'echo' tsc` · `EC=echo; $EC tsc` · `/usr/bin/printf … tsc` · `/usr/bin/echo tsc` · `/bin/true ! pytest` (10 measured; 9 in the curated set) | counts | **0** | `_PRINTS_OR_INSPECTS` (`V:80`) and `_NEGATED` (`V:88`) are **first-word-literal and `^`-anchored**; any path, alias-escape, quoting or wrapper defeats them. Canny's own comment at `checks.ts:31-34` admits this ("denylist of first words, move to parsing the command position if agents find other ways around it") | needs first-word normalisation (basename, unquote, strip `\`, peel `env`/`eval`/`builtin`/`command`/`nice`/`time`) — a redesign, not a rule tweak |
| — | `cat <<'pytest'` … `pytest` (1) | counts | **0** | the here-doc **terminator line** is read by `V:145` (`re.split(r"[;\n]", bare)`) as its own command | refuse a command containing `<<` |

Mechanisms re-derived directly from bash 5.2.21, not inferred:

```
$ STUB_RC=3 bash -c $'set -o pipefail\r\npytest | tail'   -> bash: set: pipefail: invalid option name ; rc=0
$ STUB_RC=3 bash -c $'set -o pipefail; pytest | tail' -> bash: $'set\302\240-o': command not found ; rc=0
$ STUB_RC=3 bash -c 'export R=$(pytest)'                   -> rc=0     (builtin status)
$ STUB_RC=3 bash -c 'R=$(pytest)'                          -> rc=3     (bare assignment DOES propagate)
$ STUB_RC=3 bash -c 'exec true; pytest'                    -> rc=0
$ STUB_RC=3 bash -c 'pytest(){ return 0; }; pytest'        -> rc=0
$ STUB_RC=3 bash -c 'pytest && false || true'              -> rc=0
$ STUB_RC=3 bash -c '/bin/echo tsc'                        -> rc=0
$ STUB_RC=3 bash -c $'cat <<\'pytest\'\nfoo\npytest'       -> rc=0
$ STUB_RC=3 bash -c $'echo \\\n  pytest'                   -> rc=0
$ STUB_RC=3 bash -c 'coproc pytest'                        -> rc=0
```

## The closing rules, MEASURED against the frozen tables

Each rule applied alone to a scratch copy, then all six together. "27rows" is Canny's `checks.test.ts:49-75`; "297prod"
is the `CHECKS = [` / `HIDES = [` / `KEEPS = [` product set (`T:107`/`T:121`/`T:138`) compared answer-for-answer
against the unpatched port. "HG closed" is scored against a **curated 42** of the 43 (the near-duplicate
`/usr/bin/echo tsc` dropped, and the NBSP rows carried as `pnpm test`):

```
rule                       suite                  27rows  297prod  HG closed
R1_or_on_whole_segment     45 passed in 0.24s     27/27   297/297   10/42
R2_trap_disarms            45 passed in 0.24s     27/27   297/297    4/42
R3_ascii_pipefail          45 passed in 0.27s     27/27   297/297    3/42
R4_reject_cr               45 passed in 0.23s     27/27   297/297    2/42
R5_reject_continuation     45 passed in 0.24s     27/27   297/297    2/42
R8_exec_coproc             45 passed in 0.23s     27/27   297/297    2/42
R1+R2+R3+R4+R5+R8          45 passed in 0.29s     27/27   297/297   23/42
```

**Six rules, 23 of the curated 42 hollow greens closed, not one Canny row moved and not one test red.** The remaining 19
(H7, H8, H9, the here-doc) need first-word normalisation and command-structure parsing — a redesign that contract item 1 forbids and
that belongs in an amendment, not in this lane.

---

# ITEM 3 — False negatives (the cheap direction, INFO only)

Shapes whose status **does** reach bash but the port refuses. None is a Canny table row; all are upstream-faithful.

`pytest | tail; exit ${PIPESTATUS[0]}` · `pytest || exit $?` · `pytest; rc=$?; exit $rc` · `pytest; exit $?` ·
`pytest; exit` · `pytest <&0` (the `&` in `<&0` trips `r"(?<!>)&(?!>)"` at `V:163`) · `set -o pipefail; pytest |& tee log` (the `&` in `|&`
trips `r"(?<!>)&(?!>)"` at `V:163`) · `set -o pipefail; cat f | pytest` (not the feeder `part.split("|")[0].strip()` at `V:166`) · `(set -o pipefail;
pytest | tail)` (the `set` is preceded by `(`, so the `(?:^|[;&\n])` anchor at `V:140` (`\w*o\s+pipefail\b`) misses it) · `{ pytest; }` ·
`for f in 1; do pytest; done` · `case x in *) pytest;; esac` · `if ! pytest; then exit 1; fi` · `command pytest` ·
`eval "pytest"` · `"pytest"` · `'pytest'` · `python -c "import pytest"` · `pytest \`<newline>` --maxfail=1` ·
`pytest <<EOF…` · `false || pytest` · `npm test -- --version` · `pytest & echo started; wait $!` · `pytest & wait $!`.

Cheap by construction: C2 nudges rather than mints a hollow green. No disposition beyond INFO.

---

# ITEM 4 — `with_pipefail`

**Reproduced, clean.** 29 candidates; the port matched the JS oracle on **29/29**; 17 produced a rewrite; **every one of
the 17 counts under `is_verify` and every one preserves the check's status in bash** (`rc_fail=3`, `rc_pass=0`, no
timeouts). Includes `| tail -f`, `| tail --pid=$$ -f`, `tail` with a file argument, `| tail -5 | tail -1` (two pipes),
`npm test|tail` (no spaces), `npm test > log | tail`, `cd web && pytest | tail -5`, `echo hi; pytest | tail -5`,
`pytest | tail -5 # note`, and a two-line command. Correctly returns `None` for `tailx`, `| tail | head`,
`| tail || true`, `|&`, `| head -5`, `| grep -v warn`, `| tee out.log`, `| cat | tail`, `pytest | tail; echo done`,
`pytest | tail && pnpm lint`, `pytest | tail &`, and `set +o pipefail; npm test | tail -5`. Nothing to report.

---

# ITEM 5 — The CLI (`def _cli()`, `V:202-273`)

**Reproduced.** Contract item 5's exit codes and lines all hold:

```
counts                      rc=0  stdout='counts'
does-not-count              rc=1  stdout='does-not-count'
--with-pipefail (rewrite)   rc=0  stdout='set -o pipefail && npm test | tail -5'
--with-pipefail (none)      rc=1  stdout=''            stderr=''
no --                       rc=2  stderr='unknown option: npm test'      (one line)
empty COMMAND               rc=2  stderr='COMMAND is empty'              (one line)
whitespace-only COMMAND     rc=2  stderr='COMMAND is empty'              (one line)
invalid --pattern           rc=2  stderr="invalid pattern: '(bad': missing ), unterminated subpattern"
--pattern with no value     rc=2  stderr='--pattern requires a value'
```

`--` twice, a second `--` inside the command, an option-looking word after `--`, and a command starting with `-` after
`--` all behave (the first `--` wins at `args[i]` / `saw_dashdash = True` (`V:219-222`), everything after it is command text).

**F4 — the argv join (`V:241`).** Contract item 5 writes the grammar as `-- COMMAND`, singular; `" ".join(command_parts)`
silently accepts N words. Measured, it flips answers in both directions because the caller's shell has already removed
the quoting that `executed()` / `bare = re.sub` at `V:117` relies on:

```
  -- 'true "pytest"'                 (1 arg)  -> does-not-count  rc=1
  -- true pytest                     (2 args) -> counts          rc=0
  -- 'python -c "import pytest"'     (1 arg)  -> does-not-count  rc=1     <- what T:211 asserts
  -- python -c 'import pytest'       (3 args) -> counts          rc=0     <- the same command, unquoted by the caller
```

The second pair is the expensive direction: the quote-removal defence that `import pytest"') is False` (`T:211`) pins is simply gone whenever a caller
writes the natural `verify_command.py -- $CMD` without re-quoting. **Grade: a single-string COMMAND is the contract, and
the CLI should refuse more than one word after `--`.** Measured: adding that refusal keeps the suite at **45 passed**
(every committed CLI test from `def test_cli_counts` at `T:235-302` already passes exactly one word) and turns the hazard into `rc=2`.

**F5 — `--pattern ''` is a catch-all.** `V:246` (`pats = user_patterns if user_patterns else None`) treats `['']` as
truthy; the empty string compiles to a regex that matches every check. `--pattern '' -- 'true nothing'` → `counts`. A
silent fail-open in the override channel.

**F6 — a crash in the `--with-pipefail` path is indistinguishable from "no rewrite".** A non-UTF-8 argv byte arrives as a
surrogate (`surrogateescape`); with the container's default `LANG=` the stdout error handler is also `surrogateescape`
and `print(result)` at `V:259` prints it fine, but under a strict stdout encoding the same input raises:

```
$ PYTHONIOENCODING=utf-8:strict python3 scripts/verify_command.py --with-pipefail -- $'\xffnpm test | tail -5'
UnicodeEncodeError: 'utf-8' codec can't encode character '\udcff' in position 19: surrogates not allowed
rc=1   (which contract item 5 defines as "no rewrite")
```

Narrow, but it is a fail-soft: the exception's exit code is the contract's negative answer.

**F11 — `str(SCRIPT), "npm test"` (`T:257`) does not reach `missing -- before COMMAND` (`V:238`).** `test_cli_usage_error_no_dashdash` passes `"npm test"` as one argv element, so
the parser hits `unknown option` at `V:234`, not `missing -- before COMMAND` at `V:238`. Confirmed by mutant N8 below.

---

# ITEM 6 — `patterns` (the override)

**Reproduced.** Port vs JS oracle over a 17-case matrix:

| patterns | command | port | JS | note |
|---|---|---|---|---|
| `user_re is not None` (`V:169`) | empty list | False | False | an empty JS array is truthy, so a `some` over it is false; the port reproduces that |
| `[".*"]` | `true nothing` | True | True | catch-all |
| `[".*"]` | `echo tsc` | **False** | False | `_not_a_check` at `V:167` runs **before** the pattern test in both |
| `[""]` | `true nothing` | True | True | empty string = catch-all (see F5) |
| `["^npm test$"]` | `set -o pipefail; npm test \| tail -5` | True | True | anchored pattern matches the feeder `part.split("|")[0].strip()` (`V:166`) |
| `["^npm test$"]` | `npm  test` | False | False | double space |
| `["^just check$"]` | `pnpm test` / `just check` | False / True | same | replaces, never adds (`T:175`) |
| `["(?<=npm )test"]` | `npm test` | True | True | lookbehind fine |
| `["npm t.st"]` / `["npm tëst"]` | `npm tëst` | True | True | Unicode in pattern and subject |
| `["^npm\|stest$"]` — i.e. `^npm\stest$` | `npm<NBSP>test` | **False** | **True** | D4: `re.ASCII` at `V:105` vs JS Unicode `\s` |
| `["(?i)NPM TEST"]` | `npm test` | **True** | **False** | Python honours inline flags; `new RegExp("(?i)…")` is a JS **SyntaxError**, so `safeRegex` returns null |

`patterns=None` and omitted both behave as the defaults. The item-3 deviation holds: `(unclosed`, `[z-a]`, `*`,
`(?<=a+)b`, `\` each raise `ValueError` from `V:107` and **each message contains the pattern's `repr`**; `with_pipefail`
raises too.

**F10 (INFO).** Two dialect consequences of the deviation, neither stated anywhere: `(?i)…` is a *valid* pattern here
and a dead one in Canny; a **variable-length lookbehind** (`(?<=a+)b`) is valid in Canny (JS allows them) and a hard
`ValueError` here. "Invalid" now means "invalid in Python", a different set from Canny's.

---

# ITEM 7 — MUTATION TABLE (new mutants, never the builder's M1-M11)

Scratch copies under `…/scratchpad/vc1/mut/<id>/`; each carries its own `scripts/` + `tests/` so `T:20`'s `parents[1]`
`pathlib.Path(__file__).resolve().parents[1]` resolves to the mutant. The tree was never touched. Every mutant compiles
(`py_compile`) and collects 45 — no syntax kills (AF-AP-78).

| id | mutation | compiles | passed/failed | verdict | killed by / discriminator |
|---|---|---|---|---|---|
| N1 | `.strip()` dropped from the check at `V:166` | yes | 44/1 | killed | `test_pipefail_with_config` |
| N2 | last segment → **first** (`reversed(segments)`, `V:147`) | yes | 38/7 | killed | `test_hides_exit_status`, `…[piped_with_pipefail]`, `…[pipefail_on_then_off_on]` (+4) |
| N3 | `re.split(r"[;\n]", …)` at `V:145` → `split(";")` | yes | 44/1 | killed | `test_hides_exit_status` |
| N4 | lookbehind dropped from `#[^\n]*` at `V:119` | yes | 44/1 | killed | `test_is_verify_27_rows[escaped_space_comment]` |
| N5 | `re.ASCII` dropped from `VERIFY[0]` | yes | **45/0** | **SURVIVED — real gap** | discriminator `is_verify("npm testé")`: orig True, mutant False (also `toxé`, `noxé -s lint`) |
| N6 | `r"(?<!>)&(?!>)"` at `V:163` → plain `&` | yes | 42/3 | killed | `…[piped_with_pipefail]`, `…[redirected_stderr]`, `test_keeps_exit_status` |
| N7 | `set -o pipefail && {command}` → `;` (`V:192`) | yes | 43/2 | killed | `test_cli_with_pipefail`, `test_pipefail_with_config` |
| N8 | `if not saw_dashdash:` / `missing -- before COMMAND` (`V:237-239`) deleted | yes | **45/0** | **SURVIVED — EQUIVALENT** | rc **and** stderr-line-count identical on all 7 argv shapes probed; only the message text differs, and contract item 5 pins "exit 2 with one stderr line", not the text |
| N9 | `check = part.split("\|")[0]` → `check = part` (`V:166`) | yes | 44/1 | killed | `test_pipefail_with_config` |
| N10 | `_not_a_check(check)` → `_not_a_check(part)` (`V:167`) | yes | **45/0** | **SURVIVED — real gap** | `is_verify("set -o pipefail; npm test \| grep -- --help")`: orig True, mutant False (also `\| tail --help`, `\| grep -v -- --version`) |
| N11 | `if user_re is not None` → `if user_re` (`V:169`) | yes | **45/0** | **SURVIVED — real gap** | `is_verify("pnpm test", patterns=[])`: orig **False**, mutant **True** — the JS `[]`-is-truthy semantic the brief's item 6 names has no test |
| N12 | `re.ASCII` dropped from `_ASKS_ONLY` (`V:85`) | yes | 44/1 | killed | `test_nbsp_before_help_does_not_trigger_asks_only` |
| N13 | `(?:^\|[;&\n])` anchor dropped from `\w*o\s+pipefail\b` (`V:140`) | yes | **45/0** | **SURVIVED — real gap** | `is_verify("echo set -o pipefail; pnpm test \| tail")`: orig **False**, mutant **True** — and bash rc is 0, so the anchor is what stops a hollow green. Canny's row `echo pipefail; …` (`checks.test.ts:53`) was clearly meant to cover this but has no `set -o` |
| N14 | `\|\|` tested on `last` instead of `part` (`V:157`) | yes | 44/1 | killed | `test_pipefail_does_not_excuse_or_true` |

**10 killed · 1 equivalent · 4 real gaps.** I also re-ran the builder's two survivors against the current 45-test suite:
`M1` (quote removal dropped) → `1 failed, 44 passed`, killed by `test_quoted_check_name_after_a_non_print_word` (`import pytest"') is False`, `T:211`);
`M5` (`||` rule dropped) → `1 failed, 44 passed`, killed by `test_pipefail_does_not_excuse_or_true` (`pnpm test || true") is False`, `T:205`). Both
landing-touch claims hold.

**F8 (INFO) — the builder's `M9 EQUIVALENT` claim is correct, and `is_verify("   echo tsc") is False` (`T:198`) is therefore a tautology.** I reproduced it:
removing `^\s*` from `_PRINTS_OR_INSPECTS` (`V:80`) changes **0 of 132** answers over a corpus carrying leading SP, TAB,
VT, FF, NBSP and U+001C, and leaves `45 passed`. The leading-space defence that `T:198` (`   echo tsc`) names is supplied
by the `.strip()` at `V:166`, not by the `^\s*` the test is aimed at — `str.strip()` removes a superset of ASCII `\s`, so
the anchor can never see whitespace. The test is right about the behaviour and blind to the mechanism.

---

# ITEM 8 — The builder's report (`C1-report.md`) audited against the PIN

Spot-checked every `V:`/`T:` range and every pasted count.

**Holds:** the premise re-measurement (all digests, the 78 alternatives, the table line ranges) — I re-derived each from
the clone; the mutant table's 11 rows and their kill claims; the `M9 EQUIVALENT` reasoning (reproduced above); all four
DISCREPANCIES; the landing note's `1 failed, 44 passed` for M1 and M5 (re-run above); `pyflakes` clean; the four
post-touch gate counts (`45 passed` ×2 from the root, `45 passed` from `/tmp`).

**F7 — three report defects, none of which changes a verdict:**

1. `C1-report.md:43` — "273 lines in V, **283 lines in T**". `T` is **302** lines. The line count was not remapped when
   the landing touch added the two rows; `V`'s 273 is right.
2. `C1-report.md:102` — "the coordinator reworded that row at landing and re-ran the lint **(the line is in the section
   below)**". No lint line is pasted in any section below; the C1 brief required it pasted. I re-ran it myself and it
   reads **identically to the pre-touch quote**, so the rewording did not move the verdict:
   `report_lint: 39 refs — OK 37, NEAR 1, MISS 1, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.
3. Three range ends are off by 1-2 lines: `KEEPS` is `T:138-152` (report says `T:138-154`); the two product tests end at
   `incorrectly not counted` at `T:168`, not `_all_forms(KEEPS)` at `T:167`; the NBSP test is `T:215-218` (report says `T:215-220`). All point into the right
   region.

**Contract item 4 (the notice) — verified present and verbatim.** `V:20` carries `Copyright (c) 2026 Kal`; the LICENSE
body (`LICENSE:5-21`) is present whitespace-normalised-identical in `V:22-38`; `V:5` reads `Port of qkal/canny` plus the pinned sha and file;
`V:40-41` carries `Ported by agent-factory (D-052)` verbatim; `T:3-5` names `test/checks.test.ts:47-137` and `:238-242`.

**Table transcription — verified byte-identical.** I evaluated Canny's own array literals in node and compared them to
`T`'s Python lists: 27 rows identical (values *and* booleans), `CHECKS` 11 identical (`T:107`), `HIDES` 14 identical
(`HIDES = [`, `T:121`), `KEEPS` 13 identical (`KEEPS = [`, `T:138`), products 154 and 143.

---

# FINDING INVENTORY

| id | finding | class | evidence | contract map | canonical path | material effect | reproduction | fix |
|---|---|---|---|---|---|---|---|---|
| **F1** | 43 shapes count while bash exits 0 with the check failing — nine families (H1-H9) | **CONTRACT-DEFECT** | reproduced (port + JS oracle + bash) | defeats the brief's **WHY**, not a stated criterion; the port matches Canny on all 42 | yes — `is_verify` and the CLI at the PIN | a lane could report a green the check never earned | `…/vc1/work/hostile.py`, `hostile2.py`, `uni_bash.py` | amendment below |
| **F2** | `re.ASCII` absent from `bare = re.sub` (`V:117`), `#[^\n]*` (`V:119`), `\w*o\s+pipefail\b` (`V:140`), `re.split(r"[;\n]", bare)` (`V:145`), `r"(?<!>)&(?!>)"` (`V:163`) and `(?!\s*tail\b)` (`V:197`) while the docstring at `V:7` states *all* patterns carry it; on `V:140` the omission is what makes H3 count | **BLOCKER** | reproduced | **contract item 2** — "compile with `re.ASCII`" **and** "State your choice in the module docstring" | yes — `python3 scripts/verify_command.py -- $'set\xa0-o pipefail; pnpm test \| tail'` → `counts`, rc 0 | false docstring + 3 hollow greens + 3 undeclared JS divergences (D2, D3, D4) | command above; discriminator = patch **R3** | add `re.ASCII` to `V:140`; correct `V:7-12` to name exactly which patterns carry the flag and why `V:119` deliberately does not |
| **F3** | 4 surviving mutants with real discriminators: N5 (`re.ASCII` on `VERIFY` untested), N10 (`_not_a_check` argument), N11 (`patterns=[]` untested), N13 (pipefail anchor untested although load-bearing) | FOLLOW-UP | reproduced | none — contract froze M1-M11, which the builder met | yes | coverage gap, no behaviour change | the four discriminators in the mutation table | four test rows, one per discriminator |
| **F4** | CLI joins N argv words into one COMMAND (`V:241`); flips `python -c "import pytest"` from does-not-count to counts | FOLLOW-UP (+ amendment) | reproduced | item 5 writes `-- COMMAND`, singular — an unstated extension, not a stated contradiction | yes — the real CLI | defeats the `T:211` quote defence for any caller who does not re-quote | the 4-row table in item 5 | refuse `len(command_parts) > 1` with rc 2 — measured `45 passed`, hazard → rc 2 |
| **F5** | `--pattern ''` is a silent catch-all (`pats = user_patterns if user_patterns else None`, `V:246`, + an empty regex) | FOLLOW-UP | reproduced | none | yes | fail-open in the override channel | `--pattern '' -- 'true nothing'` → `counts` | reject an empty `--pattern` value with rc 2 |
| **F6** | `UnicodeEncodeError` in the `--with-pipefail` path exits 1 = the contract's "no rewrite" | FOLLOW-UP | reproduced | none | yes, under a strict stdout encoding | a crash is reported as the negative answer | `PYTHONIOENCODING=utf-8:strict … -- $'\xffnpm test \| tail -5'` | wrap `if do_pipefail:` (`V:256-262`) and exit 2 on an encoding failure |
| **F7** | three report defects: stale "283 lines in T", a promised-but-absent post-touch lint line, three range ends off by 1-2 | FOLLOW-UP | reproduced | C1 brief's "paste the lint" | n/a | evidence gap; I recovered the missing number myself and it is unchanged | `report_lint … C1-report.md` | one edit to `C1-report.md:43` and `:102` |
| **F8** | `T:198` (`   echo tsc`) is a tautology: `^\s*` in `V:80` is dead under the `.strip()` at `V:166` (0/132 answers change) | INFO | reproduced | none — the behaviour the contract asked for is correct | yes | test names a mechanism it cannot exercise | M9 mutant, 132-input probe | if the row is to bind, point it at `.strip()` or drop `^\s*` as dead |
| **F9** | 24 status-preserving shapes the port refuses (item 3 list) | INFO | reproduced | none | yes | cheap direction only | the item-3 list | none — a nudge, by design |
| **F10** | dialect consequences of the `ValueError` deviation: `(?i)…` valid here / dead in Canny; variable-length lookbehind valid in Canny / `ValueError` here | INFO | reproduced | item 3 says "invalid pattern raises" without defining "invalid" | yes | a working Canny config can hard-fail here | the patterns matrix | one docstring sentence |
| **F11** | `str(SCRIPT), "npm test"` (`T:257`) never reaches `missing -- before COMMAND` (`V:238`); the missing-`--` message is unreachable from the suite (mutant N8 = EQUIVALENT under the contract) | INFO | reproduced | none | yes | diagnostic quality | N8 + the 7-shape argv matrix | pass `"npm", "test"` (or `--with-pipefail`) in that test |
| **F12** | C2 touchpoint: C2 must feed `is_verify` the lane's command as **one string**, never argv words (F4), and F1's H1/H2/H7/H8 mean a green `is_verify` is necessary, not sufficient | INFO | reasoned from F1/F4 | brief item 9 allows one line | n/a | design input for C2 | n/a | note it in the C2 brief |

## The `CONTRACT-DEFECT` amendment I propose (F1)

> **Deviation 2 (proposed).** The port adds a *status-integrity* pre-filter that Canny does not have, because C2 consumes
> `is_verify` as a gate rather than as a hint. `is_verify` returns False when, in the command's `executed()` text:
> (R1) the last segment contains `||` anywhere — not only in the `&&`-part carrying the check;
> (R2) any segment begins with `trap`;
> (R3) the pipefail scan is compiled with `re.ASCII`, so a Unicode space inside `set -o pipefail` no longer reads as a
>      `set` statement bash never executed;
> (R4) the command contains a carriage return;
> (R5) the command contains a backslash line continuation;
> (R8) any segment begins with `exec` or `coproc`.
> Measured at `ea9538a`: the 45-test suite stays green, Canny's 27 rows stay 27/27, the 297 product commands are
> answer-for-answer unchanged, and 23 of the curated 42 hollow greens close. R3 is not a deviation at all — it is
> contract item 2 applied where it was not.
> **Not closed by this amendment (documented, not fixed):** H7 (builtin/prefix status swallow), H8 (function shadowing),
> H9 (first-word denylist bypass by path, quoting, `env`/`eval`/`builtin` or `\`), and the here-doc terminator. These need
> first-word normalisation and command-structure parsing — a redesign that contract item 1 forbids in this increment.

## GATES (every count pasted with its invocation)

```
$ cd /home/user/agent-factory && /root/venv-agent-factory/bin/python -m pytest tests/test_verify_command.py -q \
    -p no:cacheprovider --basetemp=/tmp/claude-0/.../scratchpad/vc1/gate/bt1
.............................................                            [100%]
45 passed in 0.27s
rc=0

$ (same, --basetemp=…/bt2)                       45 passed in 0.24s       rc=0
$ cd /tmp && … pytest /home/user/agent-factory/tests/test_verify_command.py … --basetemp=…/bt3
45 passed in 0.26s
rc=0

$ … --collect-only                               45 tests collected in 0.02s
$ … pc_suite.sh set-id -- tests/test_verify_command.py
1 files set=d9bd6dad2d0e

$ /root/venv-agent-factory/bin/python -m pyflakes scripts/verify_command.py tests/test_verify_command.py
pyflakes rc=0

NEGATIVE CONTROL (the suite can go red — mutant N2 on a scratch copy):
$ cd …/vc1/mut/N2_first_segment_not_last && … pytest tests/test_verify_command.py -q …
FAILED tests/test_verify_command.py::test_pipefail_with_config - AssertionErr...
7 failed, 38 passed in 0.26s
rc=1

F4 PROBE (would a one-word CLI refusal break a committed test?):
  suite with the one-word CLI refusal: 45 passed in 0.24s
  `-- python -c 'import pytest'` -> rc 2

AUDIT OF THE BUILDER'S REPORT:
$ python3 scripts/report_lint.py --min-refs 8 --map V=scripts/verify_command.py \
    --map T=tests/test_verify_command.py tasks/briefs/canny/C1-report.md --root .
report_lint: 39 refs — OK 37, NEAR 1, MISS 1, UNCHECKABLE 0, UNRESOLVED 0 (worktree)

THIS REPORT'S OWN LINT (three fix rounds applied, then stopped as the brief directs):
$ python3 scripts/report_lint.py --min-refs 12 --map V=scripts/verify_command.py \
    --map T=tests/test_verify_command.py tasks/briefs/canny/VERIFY-C1-report.md --root .
report_lint: 124 refs — OK 123, NEAR 0, MISS 1, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
```

The one residual MISS is on the module-docstring source-line citation in the contract-item-4 paragraph. The cited line is right — it reads
`Port of qkal/canny @ f2c5e53, src/checks.ts:8-93.` — and the report line carries a backticked span copied from it; the
lint's token extractor reports only `reads` and `LICENSE` for that line, so its backtick pairing is being thrown by the
other spans there. Three rounds spent, then stopped per the brief; the floor of 12 refs is met ten times over.

Differential totals: **495 commands** through the port and the JS oracle — **495/495 agree, zero divergences**. The 7
divergences in the D1-D4 table come from two *separate* probes aimed at the ASCII/Unicode seam (a 35-input Unicode
corpus and a 17-case patterns matrix); 4 of the 7 are the deviation contract item 2 sanctions. **43** shapes across all
corpora are hollow greens against bash; **0** of Canny's own 297 product commands are.

## FOLLOW-UPS (non-blocking, for the coordinator to file under D-034)

1. Four regression rows closing the N5, N10, N11 and N13 gaps (F3) — `is_verify("npm testé")`,
   `is_verify("set -o pipefail; npm test | grep -- --help")`, `is_verify("pnpm test", patterns=[])`,
   `is_verify("echo set -o pipefail; pnpm test | tail")`.
2. CLI: refuse more than one word after `--` (F4) and an empty `--pattern` value (F5); exit 2 on an encoding failure in
   the `--with-pipefail` path (F6).
3. Correct `C1-report.md:43` ("283 lines in T" → 302) and `:102` (paste the post-touch lint line) — F7.
4. `is_verify("   echo tsc") is False` (`T:198`): aim it at `.strip()`, or drop the dead `^\s*` from `which|type|command|man|head|tail|git` (`V:80`) — F8.
5. One docstring sentence on the `ValueError` deviation's dialect consequences — F10.
6. `str(SCRIPT), "npm test"` (`T:257`): pass two argv words so the test reaches `missing -- before COMMAND` (`V:238`) — F11.
7. C2's brief: feed `is_verify` one string, never argv words; treat a green as necessary-not-sufficient until the F1
   amendment lands — F12.

## NOT-done (first-class)

- **I did not fix anything.** The tree is untouched apart from this report; every mutant and patch lives under
  `…/scratchpad/vc1/` and is deleted at hand-back.
- **No PC-side run.** Everything here is sandbox-measured against bash 5.2.21 and node v22.22.2. The hollow-green class
  is a property of bash's grammar, not of the venue, but I did not re-measure it on the PC.
- **I did not exercise real check binaries.** Every check word is a stub that exits 3 or 0. Two HIDES rows (`--help` and
  `git commit -m "…"`) are therefore mis-scored by my harness as "status-preserving"; both are meaning-hides, not
  status-hides, and I named that artefact rather than counting it.
- **`npm test --if-present`** (counts here; real npm exits 0 when there is no test script) is unverified — it needs the
  real binary. Same for `pytest -k <no-match>` (real pytest exits 5).
- **H7/H8/H9 closing rules are sketched, not measured.** Unlike R1-R5/R8, I did not build and score them, because they
  are redesigns rather than rule tweaks.
- **Out of scope, untouched, as the brief directs:** C2, anything in the Canny clone outside `checks.ts:8-93`, the MIT
  notice beyond its presence, and the live build lane's files (`src/agent_factory/decisions/ledger.py`,
  `tests/test_decisions_ledger.py`, `tasks/briefs/laya/`) — never read, run or cited.
- **One measurement-hygiene correction, stated for the record.** My stub `PATH` (which contains `git`, `python`,
  `python3`, `node` … all exiting 3) is exported inside the bash call that uses it, so two later commands *in the same
  call* silently ran stubs instead of the real binaries and returned `rc=3` that read like results. Both were re-run
  under `env -i PATH=/usr/bin:/bin`; the corrected numbers are the ones above (`does-not-count`, rc 1 under R3;
  `counts`, rc 0 at the PIN; `45 passed` under R3). No conclusion in this report rests on the poisoned runs.
- **Nothing in `/home/user/qkal/canny` was run, built, installed, imported or required.** Its regex literals were read as
  text and evaluated in my own `node` files.
