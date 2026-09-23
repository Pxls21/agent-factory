# VERIFY-J1-0-R5 — report (task #193; lane verify-j1-0-r5, sandbox, shared tree)

Brief: `tasks/briefs/laya/VERIFY-J1-0-R5-brief.md`. PIN 10f1823. Contract: AMENDMENT 4 (R5-1..R5-5) in
`tasks/briefs/laya/J1-0-R5-brief.md`, on AMENDMENT 3 (`tasks/briefs/laya/J1-0-R4-brief.md`) and AMENDMENT 2
(`tasks/briefs/laya/J1-0-R3-brief.md`). Builder's report (an input to attack): `tasks/briefs/laya/J1-0-R5-report.md`.
Scratch: `/tmp/vj10r5/`. Honey `full`. Evidence tiers: VERIFIED (run here, pasted), INFERRED, ASSUMED.

## 1. PREMISE (re-measured 2026-09-23T14:36:43Z)

```
$ git rev-parse HEAD ; git rev-parse origin/claude/soundbox-kit-migration-iz1jwf
905a8c76698c78d47a3a3cfd3f02de4efc9c1f2c
fa4532ee0b1993cdf5b14fa2b9e143d6d09eea7c
$ git log -1 --format="%h %s" 10f1823 | cut -c1-120
10f1823 J1-0-R5 landed (task #188; GATED-PENDING-VERIFY; VERIFY-J1-0-R5 = task #193): the never-a-gate screen refuses ev
$ git diff --stat 10f1823^ 10f1823
 scripts/no_laya_in_gates.py         |  81 +++--
 tasks/briefs/laya/J1-0-R5-report.md | 581 ++++++++++++++++++++++++++++++++++++
 tests/test_no_laya_in_gates.py      | 157 ++++++++++
 3 files changed, 795 insertions(+), 24 deletions(-)
$ blob[:12] per revision (PIN / HEAD / worktree / origin), lines at PIN
4f88fbb47d02 x4  1452 scripts/no_laya_in_gates.py
d2e04630f09d x4  1254 tests/test_no_laya_in_gates.py
8eaccfa87a98 x4    53 scripts/gate_files.txt
7731a91c7d3e x4   133 scripts/hooks/pre-commit
```
```
$ grep -n (the R5 seams) scripts/no_laya_in_gates.py            # line map: MATCHES the brief's premise
128:def _unquote(word):   150:class _ShellScan:   174:    def scan(self):   338:    def arith(self, start, skip, what):
354: ... " re-read with other heredocs pending")   454: ... "heredoc <<%s: $'...' escape not translated" % word)
493:        opened = (first_line, "constructs nested too deep to scan")   497:def _workflow_runs(content):   732:ALLOWED_DYNAMIC_LOADS = {
$ bash scripts/pc_suite.sh set-id -- tests/test_no_laya_in_gates.py
1 files set=e3695f80792b
$ PYTHONDONTWRITEBYTECODE=1 /root/venv-agent-factory/bin/python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/vj10r5/bt0
112 passed in 9.17s          pytest rc=0          (14:37:17Z)
$ python3 scripts/no_laya_in_gates.py; echo rc=$?; python3 scripts/no_laya_in_gates.py --staged; echo rc=$?
no_laya_in_gates: 40 files scanned, clean      rc=0
no_laya_in_gates: 40 files scanned, clean      rc=0
$ grep -c . scripts/gate_files.txt
53
```
Premise: **no mismatch**; no item is CONTRACT-INVALID on premise grounds. Screens used below: R3 = `git show 5090671^:scripts/no_laya_in_gates.py`
(blob `18c3939889cf`, sha256[:16] `a8a1e114d32c1528`), R4 = `git show 10f1823^:…` (blob `ae8b2046e118`, `ab33c767c65c6f56`), R5 = the
shared tree's `scripts/no_laya_in_gates.py`, run read-only with `--root <throwaway tree>` (sha256[:16] `db28614c4bb72601`, = the PIN
blob). Tools: GNU bash 5.2.21(1)-release; Python 3.11.15; PyYAML 6.0.3 (venv, the hook's `$PY`) and 6.0.1 (system `python3`).
Harness: `/tmp/vj10r5/tools/h.py` (each shape in its own tree: `scripts/gate_files.txt` lists only the gate, the unlisted helper
`scripts/h.sh` writes a marker file, so bash's own execution says whether a source ran; workflow values run through
`bash --noprofile --norc -e`, GitHub's default for an unspecified shell).

## 2. R5-1, the `$'…'` family, by bash itself (VERIFIED; `/tmp/vj10r5/tools/item2.py`, output `/tmp/vj10r5/item2.out`)

bash's own reading of each word, independently of the builder's tool (`declare -f` re-serializes the delimiter after bash's quote
handling; `/tmp/vj10r5/tools/bashdelim.py`):
```
<<-$'\tEOF'   bash ends at TAB+"EOF"   declare -f: cat <<-'<TAB>EOF'   (bash checks the UNSTRIPPED line first; the scan only strips)
<<$'EOF'x     bash ends at 'EOFx'      <<x$'EOF'   'xEOF'      <<"$'EOF'"  the literal $'EOF'      <<\$'EOF'   '$EOF'
<<$''EOF      bash ends at 'EOF'       <<$'EOF (never closed)   no end (syntax error)
```
Trap layout: `cat <<WORD >/dev/null`, a body line, then bash's delimiter line and the scan's (`_unquote`) delimiter line on the two
sides of `. scripts/h.sh`, both orders when they differ; `[no-edge]` is the same heredoc with no source line (a false-refusal probe).

| shape | bash ran helper | R3 | R4 | R5 | agree? |
|---|---|---|---|---|---|
| S1 `<<-$'\tEOF'`, tab body, TAB+EOF then H (bash-first) | yes | rc 4 :5 | **rc 0** | rc 4 :2 escape | yes (R4's V-01 class, fixed) |
| S1 (scan-first: `\tEOF` literal, H, TAB+EOF) | no | rc 4 :5 | rc 4 :5 | rc 4 :2 escape | refusal (false, as in R4) |
| S1 [no-edge] | no | rc 0 | rc 4 :2 `heredoc <<\tEOF pending` | rc 4 :2 escape | refusal (false, as in R4) |
| S2 `<<$'EOF'x` (EOFx, H) / [no-edge] | yes / no | rc 4 / 0 | rc 4 :5 / 0 | rc 4 :5 / 0 | yes / yes |
| S3 `<<x$'EOF'` (xEOF, H) / [no-edge] | yes / no | **rc 0** / 0 | rc 4 :5 / 0 | rc 4 :5 / 0 | yes / yes |
| S4 `<<"$'EOF'"` (literal `$'EOF'`, H) / [no-edge] | yes / no | rc 4 / 0 | rc 4 :5 / 0 | rc 4 :5 / 0 | yes / yes |
| S5 `<<\$'EOF'` ($EOF, H) | yes | rc 4 :5 | rc 4 :5 | rc 4 :2 escape | yes |
| S5 [no-edge] | no | rc 0 | rc 0 | **rc 4 :2 escape** | **NO: a false refusal R5 adds** (V5-02) |
| S6 `<<$''EOF` (EOF, H) / [no-edge] | yes / no | rc 4 / 0 | rc 4 :5 / 0 | rc 4 :5 / 0 | yes / yes |
| S7 `<<$'EOF` never closed | no (`bash -n` rc 2) | rc 0 | rc 4 `quote $' open` | rc 4 `quote $' open` | yes (refused) |
| S7b `<<$'EOF` closed by a `'` two lines later | no (the H line is inside the word) | rc 0 | rc 4 `heredoc … pending` | the same | refusal (false, as in R4) |
| A1 `. $'scripts/h\x2esh'` | yes | rc 4 :2 | rc 4 :2 | rc 4 :2 | yes |
| A2 `source $'\x73cripts/h.sh'` | yes | rc 4 | rc 4 | rc 4 :2 | yes |
| A3 `. scripts/$'h.sh'` | yes | rc 4 | rc 4 | rc 4 :2 | yes |
| A4 `. "$(printf %s $'scripts/h.sh')"` | yes | rc 4 | rc 4 | rc 4 :2 | yes |
| A5-A8 the COMMAND WORD in ANSI-C: `$'.' x`, `$'\x2e' x`, `$'source' x`, `$'\x73ource' x` | yes | rc 0 | rc 0 | **rc 0** | **NO: fail-open, KNOWN class F-B3** |
| A9 `$"." scripts/h.sh` (locale quoting) | yes | rc 0 | rc 0 | rc 0 | NO: fail-open, KNOWN class F-B3 |

Answers to item 2:
- **No new fail-open in any heredoc shape.** Every shape where bash runs the helper is refused by R5. The predicate is on the raw word
  (`"$'" in word and "\\" in word`, `scripts/no_laya_in_gates.py:453`), so a word evades it only if bash's word holds an ANSI-C escape
  while the scanner's raw word lacks `$'` or `\`. The only such spelling found, a line continuation between `$` and `'`, leaves a
  newline in the scan's delimiter, which never matches: R4-1 refuses it (the builder measured it; not re-derived here). A continuation
  BEFORE the word keeps `$'` and `\` in the raw word and is refused by the predicate (D-MX1a, § 8).
- **False refusals R5 adds:** `<<\$'EOF'` with no source line (S5 [no-edge]): bash reads `$EOF`, `_unquote` also reads `$EOF`
  (correct), but the predicate fires first. The contract's option (b) wording ("a heredoc word holding `$'` with a backslash
  inside") mandates this refusal literally, so it is per contract. No listed gate holds it (grep below). S1's and S7b's false refusals
  are R4's, unchanged.
- **Does R5-1 cover `$'` in a source ARGUMENT?** R5-1's predicate is heredoc-only. It does not need to cover arguments: AMENDMENT 2's
  source rule refuses every `.`/`source` command whose exact (file, target) pair is not allowed, whatever the target's spelling (A1-A4
  refused by R3, R4 and R5 alike). **No source-argument gap.** The gap is the command WORD: `$'.' x`, `$'\x2e' x`, `$'source' x` and
  `$"." x` run the helper and read CLEAN in all three screens. That is F-B3's quoted-command-word class (`'.' x`, `\. x`,
  `'source' x` are its S30-S32 in `tasks/briefs/laya/VERIFY-J1-0-R23-STAMP-report.md:278`, re-observed as SP3/SP4 in
  `tasks/briefs/laya/VERIFY-J1-0-R4-report.md:122`): KNOWN (issue #37), pre-existing (R3 CLEAN), new spellings only (V5-01).
- Live exposure (re-measured): no listed gate holds a heredoc word with `$` or a backslash; the only `$'` in listed shell text is
  `$'\n'` inside `${…}` in `scripts/pc_lane.sh:67`, `:313`, `:332`. So R5-1 changes no live verdict.

## 3. R5-2, the memo and its new refusal (VERIFIED)

**(a) A WRONG non-refusal from the start-only memo: not found, by three independent instruments.**
- The mechanism, re-derived from `def arith` (`scripts/no_laya_in_gates.py:338-374`): a SUCCESS is never stored, so a `$((` that
  first decides arithmetic is re-attempted on every revisit, under the revisit's own pending heredocs. The brief's scenario (first
  visit arithmetic, revisit command substitution) therefore re-decides fresh. Only FAILURES are stored: `None` when the attempt made
  no `read_bodies` call, else the pending tuple. A stored tuple that differs from the revisit's pending raises the guard (`:354`).
  A decision that FLIPS with the pending state needs a newline inside a nested `$( … )` (so a pending heredoc can swallow a line);
  that newline is a `read_bodies` call, so such a failure is stored as a tuple and its revisit under other heredocs is refused, not
  trusted. Built and measured: `x=$(( <<A $(( $(:\nA\n) ) ) ) )` (the builder's family) refuses with the guard text.
- Instrument 1, end-to-end differential (`/tmp/vj10r5/tools/fuzz_memo.py`): R4's and R5's real `_command_segments` and
  `_source_errors`, imported from their files, on random texts (atoms `$((`, `((`, `$(`, `)`, ` ) )`, `<<A`, `<<'C'`, `<<-D`, `#`, `'`,
  `"`, backticks, `case`, `$[`, newlines, delimiter lines, `. scripts/h.sh`):
  ```
  {"seed": 1, "stats": {"total": 20000, "guard": 30, "guard-and-r4-refused": 30}, "found": {}}
  {"seed": 2, "stats": {"total": 100000, "r4-clean": 10053, "r5-clean": 10053, "r4-opened": 84077, ..., "guard": 91, "guard-and-r4-refused": 91}, "found": {}}
  {"seed": 3, ... "r4-clean": 10010, "r5-clean": 10010, ... "guard": 85, "guard-and-r4-refused": 85}, "found": {}}
  {"seed": 4, ... "r4-clean": 10046, "r5-clean": 10046, ... "guard": 78, "guard-and-r4-refused": 78}, "found": {}}
  {"seed": 5, ... "r4-clean": 10208, "r5-clean": 10208, ... "guard": 97, "guard-and-r4-refused": 97}, "found": {}}
  ```
  `found: {}` = no REGRESSION (R5 CLEAN where R4 refused), no SEGDIFF (segments differ with neither refusing), no ERRDIFF.
- Instrument 2, a shadow oracle at every memo hit (`/tmp/vj10r5/tools/shadow.py`): at each hit, R4's real `arith()` re-decides on
  an R4 scanner holding the SAME state (text, position, segments, pending heredocs); R5's own run is untouched.
  ```
  {"seed": 11, "stats": {"exact": 2775, "hit-stored-None": 2433, "hit-stored-eq": 342, "guard": 85}, "wrong": 0}
  {"seed": 12, "stats": {"exact": 2924, "hit-stored-None": 2570, "hit-stored-eq": 354, "guard": 95}, "wrong": 0}
  {"seed": 13, "stats": {"exact": 2792, "hit-stored-None": 2417, "hit-stored-eq": 375, "guard": 91}, "wrong": 0}
  ```
- Instrument 3, the dangerous sub-case targeted (`/tmp/vj10r5/tools/shadow2.py`): a hit whose stored value is `None` while the
  current pending heredocs DIFFER from those at storage time (the builder's "holds under any pending heredocs"), texts dense in
  `<<W` openers, comments, quotes and nested `$( … \n … )` at 2-6 levels:
  ```
  {"seed": 21, "stats": {"exact": 16024, "None-hit-with-other-pending": 964, "guard": 194}, "wrong": 0}
  {"seed": 22, "stats": {"exact": 15714, "guard": 201, "None-hit-with-other-pending": 886}, "wrong": 0}
  {"seed": 23, "stats": {"exact": 16004, "None-hit-with-other-pending": 895, "guard": 254}, "wrong": 0}
  {"seed": 24, "stats": {"exact": 15765, "guard": 210, "None-hit-with-other-pending": 858}, "wrong": 0}
  ```
  3,603 trusted `None` hits under other heredocs, each re-decided by R4 the same way. **The builder's exactness claim survives.**
  Residual (UNSURE, not reproduced): the docstring's "the pending heredocs are the only state an attempt reads, and only through
  read_bodies" omits one more read, the nested memo comparison itself (a stored tuple compared with the current pending). By the
  mechanism above, a tuple entry nested in an attempt is created inside that same attempt (so its `read_bodies` calls are counted
  there), unless a pass reached the inner `$((` while the outer one was hidden; I could not build such a text (arith mode and command
  mode hide the same quoted text, and every command-mode hider ends at a counted newline). Bash was not needed as the oracle here:
  R5 = R4 on every sampled hit, so any R5-versus-bash difference is R4's (issue #46 rows).

**(b) False refusals R5 adds — CONFIRMED, a family, fail-closed, none live** (`/tmp/vj10r5/tools/guardnew.py`, seed 31):
```
{"seed": 31, "stats": {"body:texts": 4, "levels:GUARD-NEW-bash-valid": 349, "levels:guard": 349, "levels:texts": 349,
 "multi:texts": 339, "operand:GUARD-NEW-bash-valid": 221, "operand:guard": 391, "operand:texts": 391}}
levels:GUARD-NEW-bash-valid "x=$(( <<A $(( $(:\nA\n) ) ) ) )\n"
levels:GUARD-NEW-bash-valid "x=$(( <<-D $(( $(:\n\tD\n) ) ) ) )\n"
levels:GUARD-NEW-bash-valid "x=$(( <<'B' $(( $(:\nB\n) ) ) ) )\n"
operand:GUARD-NEW-bash-valid "x=$(( <<\\E $(( $(:\nE\n) ) ) ) )\n"
```
570 unique texts, each `bash -n` rc 0, R4 `_source_errors == []`, R5 refused with `$(( re-read with other heredocs pending`. Through
the real screen (`/tmp/vj10r5/tools/h.py`, bash run for real):
```
G1-guard-valid-no-edge  "x=$(( <<A $(( $(:\nA\n) ) ) ) )\necho done\n"   bash_ran=False bash-n=0
    R3 0 no_laya_in_gates: 1 files scanned, clean
    R4 0 no_laya_in_gates: 1 files scanned, clean
    R5 4 gate-file-unparseable: scripts/g.sh:2: $(( re-read with other heredocs pending
G3-guard-echo-inner     "x=$(( <<A $(( $(echo 1\nA\n) ) ) ) )\necho \"$x\"\n"   bash_ran=False bash-n=0   (R3 0, R4 0, R5 4, the same text)
```
The family: a heredoc opener inside a `$((` operand (a shift in the arithmetic attempt, a heredoc in the command re-scan) followed by
a nested `$((` whose attempt reads a body at a newline inside a `$( … )`. The other two families the brief names reach no guard:
several pending heredocs with different quoting on a COMMAND (`multi`, 339 texts, 0 guard: no enclosing failed attempt) and `$((`
inside an unquoted heredoc body (`body`, 0 guard: each body is scanned by a fresh `_ShellScan` with its own memo, `:475`). The
builder predicted this family in D2 ("would be a NEW false refusal"); none is live (the live tree reads clean in both modes, so the
guard does not fire there). V5-03.

**(c) Is D2's text within "the existing error texts" rule?** The R5 brief (`tasks/briefs/laya/J1-0-R5-brief.md:59`): "Nothing else
changes: … the existing error texts, … the output line format". Read literally, that forbids CHANGING an existing text; D2 changes none
and adds a reason inside R4-1's existing `gate-file-unparseable: <file>:<line>: <what>` format, as R5-1(b) itself prescribes for its
own new reason. So the TEXT is within the rule. The BEHAVIOUR is beyond R5-2's words: its memo option ("made once per start
position (memoized)") names no refusal, and its only refusal clause belongs to the depth option ("refused with the R4-1 refusal
text"). The builder declared it (D2). Two doc gaps follow (V5-04, FOLLOW-UP): the four docstrings that enumerate `_Open`'s causes
omit the guard — the module docstring (`scripts/no_laya_in_gates.py:19`, `cannot finish in sync`), `class _Open` (`:113`, "The scan cannot finish in sync: a
construct is still open … or a heredoc word holds an escape"), `class _ShellScan` (`:159`) and `_command_segments` (`:485`, "_Open: R4-1,
R5-1; or nesting too deep"); and the guard fires on texts the scan CAN finish in sync (R4 finishes them), so `:113`'s framing is false
for it. Only `def arith`'s docstring (`:341-348`) describes it.

## 4. R5-4, the workflow line map (VERIFIED; `/tmp/vj10r5/tools/item4.py`, output `/tmp/vj10r5/item4.out`)

Each fixture is the whole `.github/workflows/w.yml` (lines 1-5 the job head, line 6 the first step). "span" = the file lines that hold
the value's content. The oracle runs PyYAML's value of every `run:` through `bash --noprofile --norc -e` (as GitHub runs its script
file). "GitHub runs" = which text the YAML spec gives the step (PyYAML's value is printed beside it; GitHub's own parser was not run).

| fixture | GitHub runs (YAML spec) | PyYAML value | bash ran helper | R4 line | R5 line | R5 in the value? |
|---|---|---|---|---|---|---|
| W1 `>-` + blank line, H on 9 | folded, final break stripped | `echo a\n. scripts/h.sh` | yes | 8 | 7 | in (7-9) |
| W2 `>+` + blank line | folded, trailing breaks kept | `echo a\n. scripts/h.sh\n\n` | yes | 8 | 7 | in (7-10) |
| W3 `\|-`, H on 8 | literal, final break stripped | `echo a\n. scripts/h.sh` | yes | 8 | 8 | in, its own line |
| W4 `\|+` | literal, trailing breaks kept | `echo a\n. scripts/h.sh\n\n` | yes | 8 | 8 | in, its own line |
| W5 `\|2`, first line more indented | literal; spaces past the indicated indent are content | `  echo a\n. scripts/h.sh\n` | yes | 8 | 8 | in, its own line |
| W5b `\|2`, leading blank line | literal | `\n. scripts/h.sh\n` | yes | 8 | 8 | in, its own line |
| W6 plain over 3 lines (`;` line) | flow-folded (breaks → spaces) | `echo a ; . scripts/h.sh` | yes | 6 | 6 | in (6-8) |
| W6b plain, blank line | flow-folded (a blank line → `\n`) | `echo a\n. scripts/h.sh` | yes | 7 | 6 | in (6-8) |
| W6c plain starting on the line after `run:` | flow-folded | `echo a; . scripts/h.sh` | yes | 7 | 7 | in (7-8) |
| W7 `"echo a\n\` + escaped line break | escapes applied; the escaped break is dropped | `echo a\n. scripts/h.sh` | yes | 7 | 6 | in (6-7) |
| W7b `"echo a;\` + escaped break + blank line | escapes + folding | `echo a;\n. scripts/h.sh` | yes | 7 | 6 | in (6-8) |
| W8 `'echo ''a''` + blank line | flow-folded; `''` → `'` | `echo 'a'\n. scripts/h.sh` | yes | 7 | 6 | in (6-8) |
| W9 `{run: "echo a\n. scripts/h.sh"}` | escapes applied | `echo a\n. scripts/h.sh` | yes | **7 (OUT)** | 6 | in (6) — fixed by R5 |
| W9b `{run: "echo a` + blank + H`"}` | flow-folded | `echo a\n. scripts/h.sh` | yes | 7 | 6 | in (6-8) |
| W9c `{run: . scripts/h.sh}` | plain | `. scripts/h.sh` | yes | 6 | 6 | in (6) |
| **W10** `run: &x`, then `\|` alone on 7, `echo a` 8, H 9 | literal | `echo a\n. scripts/h.sh\n` | yes | 8 | **8 = `echo a`** | in, but NOT its own line: the literal map is shifted by one |
| **W10b** `run: &x`, `\|` on 7, H on 8 | literal | `. scripts/h.sh\n` | yes | 7 | **7 = the `\|` line** | **OUT** |
| **W11** `run: !!str`, `>` on 7, `echo a`, blank, H | folded | `echo a\n. scripts/h.sh\n` | yes | 8 (in) | **7 = the `>` line** | **OUT (R4 was in: worse than R4)** |
| **W12** `run: &x`, plain H on 7 | plain | `. scripts/h.sh` | yes | 6 | **6 = the key line** | **OUT** |
| **W12b** `run: !!str`, `". scripts/h.sh"` on 7 | double-quoted | `. scripts/h.sh` | yes | 6 | **6** | **OUT** |

- Every shape the brief names (W1-W9c) is refused (rc 4), and R5 names a line inside the value: **R5-4 holds for them**. R5 also
  fixes W9 (a one-line flow mapping, where R4 named line 7, a line the 6-line file does not have).
- **V5-05 (new; see the inventory): a node property on an earlier line moves the named line out of the value.** PyYAML's
  `ScalarNode.start_mark` is the node's FIRST PROPERTY (an anchor `&x` or a tag `!!str`), not the scalar
  (measured: `start_mark.line(0b)=5` for all four shapes, the `run:` line). `_workflow_runs` adds 2 for a block and 1 otherwise
  (`scripts/no_laya_in_gates.py:521`, `value.start_mark.line`), so with the property on the line before the indicator it names the indicator's own line
  (W10b, W11), shifts a literal block's line map by one (W10 names `echo a` for the helper on the next line), and names the key line
  for a flow scalar (W12, W12b). The R5 docstring (`scripts/no_laya_in_gates.py:499-501`, `else the start mark's line`: "The first line is where the value starts:
  the line after the indicator of a block (| or >) … Only a literal block (|) keeps its lines, so a refusal in it names its own line")
  is false as stated for W10, W10b and W11. The verdict is right in every row (rc 4); only the line is wrong. W11 is worse than R4.
  No live workflow holds an anchor, alias or tag (`grep -nE '&[A-Za-z]|\*[A-Za-z]|!!' .github/workflows/*.yml`: no hit).
  GitHub's acceptance of these shapes was NOT measured (PyYAML accepts them; anchors in workflows are INFERRED only).
- **The fix, RUN on a scratch copy** (`/tmp/vj10r5/fix/tree`, a `git archive 10f1823` subset): take the scalar TOKEN's start line,
  which sits on the block indicator or the flow scalar's first character, keyed by its end mark (the node's `end_mark` is the token's):
  ```
  token_line = {t.end_mark.index: t.start_mark.line for t in yaml.scan(content, Loader=yaml.SafeLoader)
                if isinstance(t, yaml.ScalarToken)}          # inside the existing try, after compose_all
  line = token_line.get(value.end_mark.index, value.start_mark.line)
  runs.append((line + (2 if value.style in ("|", ">") else 1), value.value, value.style == "|"))
  ```
  Measured (`/tmp/vj10r5/fix_item4.out`): W10 → 9 (the helper's own line), W10b → 8, W11 → 8, W12 → 7, W12b → 7, all inside; W1-W9c
  unchanged; the builder's Y1, Y1b, Y2, Y2b, Y2c, Y3, Y3b, Y4, Y4b, Y4c, Y5, Y10, Y11, Y12, Y13, Y14, Y15 byte-IDENTICAL output;
  `tests/test_no_laya_in_gates.py` on the fixed copy `112 passed in 8.86s`; the live tree through the fixed copy
  `40 files scanned, clean` rc 0 in both modes. It changes no verdict (no rc differs in any fixture), so it can neither leak nor
  refuse anything new; the cost is one more `yaml.scan` pass over each workflow file.
- A smaller wording point (INFO): the docstring's reason clause "any other style (plain, quoted, folded) folds or escapes its line
  breaks" is loose for a folded block's MORE-INDENTED lines, whose breaks YAML keeps (Y2b: `echo b\n  . scripts/h.sh`); the rule it
  justifies (name the first line) is what the code does.

## 5. R5-3 and R5-5 (VERIFIED)

**R5-3 — the comment, quoted** (`scripts/no_laya_in_gates.py:726-731`, `unresolved base directory`):
> Dynamic loads whose target static resolution cannot prove: (gate file, literal repo path) -> how many load sites in that gate file
> may name that path joined to an unresolved base directory. More such sites than the count are all refused, and the path must
> itself be listed. An entry binds only the gate file, the literal path and the site count. The base directory is not bound: a site
> whose base is re-pointed (an environment value, another directory) still matches, and a wrapper that runs one site twice makes a
> second load that counts once. Both are outside this check (F-B5's class, issue #37). Closed: a new entry is a reviewed change here.

Each claim against `_load_errors` (`scripts/no_laya_in_gates.py:1111-1160`) and the real screen, on trees holding the REAL
`scripts/lint_delta.py` at the PIN or a one-line variant (`/tmp/vj10r5/tools/item5.py`, output `/tmp/vj10r5/item5.out`):
```
E0-live                          rc=0  no_laya_in_gates: 3 files scanned, clean
E1a-env-base                     rc=0  no_laya_in_gates: 3 files scanned, clean            base = Path(os.environ["OTHER"])
E1b-wrapper-twice                rc=0  no_laya_in_gates: 3 files scanned, clean            one site in a wrapper, called with two bases
E1c-second-direct-site           rc=4  gate-file-import-unresolved: scripts/lint_delta.py:106 ; gate-file-import-unresolved: scripts/lint_delta.py:107
                                 (the variant's lines: 106 = `spec_from_file_location`, the live site; 107 = its inserted second site)
E3-argv-base                     rc=0  no_laya_in_gates: 3 files scanned, clean            base = Path(sys.argv[-1])
E4-absolute-literal-base         rc=4  gate-file-import-unresolved: scripts/lint_delta.py:106      base = Path("/tmp/elsewhere"); 106 = `spec_from_file_location`
E5-other-tail                    rc=4  gate-file-import-unresolved: scripts/lint_delta.py:106      REPO / ".claude/hooks/other.py"; 106 = `spec_from_file_location`
E6-relative-literal-same-path    rc=0  no_laya_in_gates: 3 files scanned, clean            two more sites naming the listed path by a relative literal
E2-live-unlisted                 rc=4  gate-file-import-unlisted: scripts/lint_delta.py:106 loads .claude/hooks/edit-snapshot.py   (106 = `spec_from_file_location`)
```
| claim | code | measured | verdict |
|---|---|---|---|
| (gate file, literal repo path) → a count of sites naming that path joined to an UNRESOLVED base | key `(entry, value[1])` reached only for a value that is not None/"code"/"at" (`:1144`); `uses` holds site indexes | E0, E6 (relative-literal sites to the same path are not counted: they are "at" values, checked against the list) | true |
| more such sites than the count are ALL refused | `for index in indexes: found[index][1] = True` (`:1151-1154`) | E1c: both 106 and 107 | true |
| the path must itself be listed | `unlisted.add(value[1])` (`:1146-1147`) | E2 | true |
| binds only gate file, path, site count | the key and the count | E5 | true |
| the base is not bound; a re-pointed base still matches | any unresolved base | E1a, E3 | true, with one precision: a base re-pointed to an ABSOLUTE literal directory is refused (E4: `_as_path` returns None for "/…", `:758`), so "another directory" holds only for a directory the resolver cannot tell. That claims LESS enforcement than exists, never more (INFO, V5-06) |
| a wrapper that runs one site twice counts once | site indexes, not calls | E1b | true |
| closed; a new entry is a reviewed change | `test_closed_sets_locked` pins the dict (`tests/test_no_laya_in_gates.py:644-656`) | read | true (the review half is process) |
| per-entry `# base:` comments (unchanged from R4) | `REPO = … git rev-parse --show-toplevel` (`scripts/lint_delta.py:35`); `root = args.root.resolve()` (`scripts/proof-runner:282`, `scripts/ledger-gen:66`) | read | true (each also falls back to `Path(__file__)…with_name`, a resolved "at" value, not the unresolved base) |

**No word in the comment claims more than the code enforces.** "never more" and "cannot be re-pointed at another file" are gone
(`git diff 10f1823^ 10f1823`). R5-3 is met.

**R5-5 — the corrections section** (`tasks/briefs/laya/J1-0-R5-report.md:344-366`, `Corrections to the J1-0-R4 report`). Each quote matches its source line exactly
(`sed -n` of `tasks/briefs/laya/J1-0-R4-report.md:116`, `refusals that are safe but may be false`, then `:118`, `:120`, `:421`), and each citation says what the section says it says
(`tasks/briefs/laya/VERIFY-J1-0-R4-report.md:129` AQ1 FAIL-OPEN, `:134` TK1, `:141` DA1 FAIL-OPEN, `:142` DA2 caught by R4-1, `:243` Y9).
The fixtures, re-run here (the builder's appendix texts; `/tmp/vj10r5/item5b.out`):
```
DA1  bash ran helper=True bash-n=0 | R3 0 | R4 0 | R5 (0, 'no_laya_in_gates: 1 files scanned, clean')
DA2  bash ran helper=True bash-n=0 | R3 4 | R4 4 | R5 (4, 'gate-file-unparseable: scripts/g.sh:2: heredoc <<2 pending')
TK1  bash ran helper=True bash-n=0 | R3 0 | R4 0 | R5 (0, 'no_laya_in_gates: 1 files scanned, clean')
CA5  bash ran helper=True bash-n=0 | R3 0 | R4 0 | R5 (0, 'no_laya_in_gates: 1 files scanned, clean')
Y9   python ran helper=True | R3 0 | R4 0 | R5 (0, 'no_laya_in_gates: 1 files scanned, clean')
Y9b  python ran helper=True | R3 0 | R4 0 | R5 (0, 'no_laya_in_gates: 1 files scanned, clean')
Y9c  python ran helper=True | R3 0 | R4 0 | R5 (0, 'no_laya_in_gates: 1 files scanned, clean')
```
1. D4's `$[ … ]` line: **the correction is true.** DA1 reads CLEAN while bash runs the helper; only DA2's shape ends in R4-1. Its
   mechanism holds: the scan takes `<< true` as a heredoc whose body ends at the later `true` line, so the `.` line between is data.
2. D4's `shell: python` item: **true.** Y9, Y9b, Y9c are fail-opens (python loads the unlisted helper; R5 rc 0), not safe refusals.
3. Self-attack 1: **true.** TK1, CA5 and DA1 re-sync and read CLEAN in R5; the AQ shapes are refused by R5-1 (item 2). These rows are
   KNOWN (issue #46: V-02, V-03, V-08), reported here only as the corrections' evidence.

## 6. The real hook, a throwaway repository (VERIFIED; `/tmp/vj10r5/tools/hook.sh`, output `/tmp/vj10r5/hook.out`)

`/tmp/vj10r5/hook/repo` = the 850-file PIN subset of § 8, `git init`, base commit under an EMPTY hooks directory; then
`core.hooksPath=/tmp/vj10r5/hook/hooks`, which holds ONLY `pre-commit` = `git show 10f1823:scripts/hooks/pre-commit`
(`cmp` with the shared tree's `scripts/hooks/pre-commit`: rc 0). No post-commit hook runs. The hook runs the repository's own
`scripts/no_laya_in_gates.py` (the PIN's bytes, `db28614c4bb72601`) with `--staged`. Pasted:
```
base commit 0f2636a (850 files, empty hooks dir)
core.hooksPath=/tmp/vj10r5/hook/hooks
=== C1 clean: a comment line appended to the listed scripts/pc_suite.sh
    lint_delta (index vs HEAD): 0 .py changed, 0 NEW pyflakes hit(s), 0 removed
    no_laya_in_gates: 40 files scanned, clean
    commit rc=0; HEAD=b284889
--- staged gate scripts/vj-aq1.sh (listed): cat <<$'echo \x41' >/dev/null / body / echo A / . scripts/vj-helper.sh / echo \x41
--- bash runs the staged gate: helper ran=yes          (the unlisted helper carries the vocabulary)
=== C2 AQ1 (must be blocked, screen rc 4)
    gate-file-unparseable: scripts/vj-aq1.sh:2: heredoc <<$'echo \x41': $'...' escape not translated
    COMMIT BLOCKED by the never-a-gate screen (rc=4)
    commit rc=1; HEAD=b284889
--- staged gate scripts/vj-a5.sh (listed): $'.' scripts/vj-helper.sh           helper ran=yes
=== C3 A5, KNOWN class F-B3 ($'.' as the command word)
    no_laya_in_gates: 41 files scanned, clean
    commit rc=0; HEAD=0f3bc90
--- staged gate scripts/vj-g1.sh (listed): x=$(( <<A $(( $(: / A / ) ) ) ) ) / echo done
--- bash -n: rc=0
--- bash runs it: … line 5: warning: here-document at line 5 delimited by end-of-file (wanted `A') … line 6: A: command not found done
=== C4 G1, the D2 guard family (a false refusal R5 adds)
    gate-file-unparseable: scripts/vj-g1.sh:2: $(( re-read with other heredocs pending
    COMMIT BLOCKED by the never-a-gate screen (rc=4)
    commit rc=1; HEAD=0f3bc90
=== C4-control: the same staged G1 commit with R4's screen in the throwaway worktree
    no_laya_in_gates: 42 files scanned, clean
    commit rc=0; HEAD=0bcde3c
--- R5 screen restored: db28614c4bb72601
--- staged workflow .github/workflows/vj.yml: 6 `      - run: &x`  7 `          |`  8 `          . scripts/vj-helper.sh`
=== C5 W10b through the hook (refused; which line is named?)
    gate-file-unparseable: scripts/vj-g1.sh:2: $(( re-read with other heredocs pending
    gate-file-sources: .github/workflows/vj.yml:7: scripts/vj-helper.sh
    COMMIT BLOCKED by the never-a-gate screen (rc=4)
    commit rc=1; HEAD=0bcde3c
```
(lint_delta's `0 NEW pyflakes hit(s)` line printed before every screen line; trimmed after C1.)
- C1 lands; **C2 (AQ1) is blocked at the operator's line**, rc 4 from the screen, rc 1 from the hook. R5-1 holds through the hook.
- **No NEW fail-open was found in items 2-4**, so C3 commits the KNOWN F-B3 member A5 instead: it lands (41 files, clean) and bash
  runs the unlisted helper. KNOWN (issue #37), reported for completeness.
- **C4 is the strongest new false refusal** (V5-03): a bash-valid gate with no source edge is blocked; the same staged commit lands
  under R4 (C4-control). And C5 shows the consequence: once such a text is in history, R5 refuses EVERY later commit on the branch
  (the `vj-g1.sh:2` line in C5's output). None is in the live history: the live tree reads clean in both modes (§ 9).
- **C5 is V5-05 through the real hook**: the refusal names `vj.yml:7`, the `|` indicator line; the source edge is on line 8.

## 7. Cost, through the real screen (VERIFIED; `/tmp/vj10r5/tools/cost.py`; one listed `scripts/g.sh` per tree; wall clock on a 4-core sandbox, load 1.4-2.0, 15:03-15:16Z)

```
$ cost.py kseries      (v=$(( … x ) ) … k levels, then . scripts/h.sh)
k=22     bytes=195     bash-n=0  R5 rc=4    0.06 s  gate-file-sources: scripts/g.sh:3: scripts/h.sh
k=100    bytes=819     bash-n=0  R5 rc=4    0.10 s  (the same)
k=200    bytes=1619    bash-n=0  R5 rc=4    0.27 s
k=300    bytes=2419    bash-n=0  R5 rc=4    0.51 s
k=330    bytes=2659    bash-n=0  R5 rc=4    0.57 s
k=360    bytes=2899    bash-n=0  R5 rc=4    0.06 s  gate-file-unparseable: scripts/g.sh:1: constructs nested too deep to scan
k=400    bytes=3219    bash-n=0  R5 rc=4    0.06 s  (the same)
$ cost.py d8           (D8, KNOWN: the (( command form)
D8 (( k=1000  bytes=7002   R5 0.56 s  R4 0.57 s  R3 0.04 s   (all rc=0)
D8 (( k=2000  bytes=14002  R5 2.06 s  R4 2.04 s  R3 0.05 s   (all rc=0)
$ cost.py bodyheavy    (D3 with a body: k failed $(( levels around B bytes of plain words, then a source edge)
body k=50  B=100000   bytes=100418  bash-n=0  R5 rc=4    4.39 s
body k=100 B=100000   bytes=100818  bash-n=0  R5 rc=4   11.95 s
body k=200 B=100000   bytes=101618  bash-n=0  R5 rc=4   22.97 s
body k=300 B=100000   bytes=102418  bash-n=0  R5 rc=4   37.64 s
$ cost.py bodyheavy-r3r4
body k=100 B=100000   R3 rc=4    0.06 s
body k=16  B=100000   R5 rc=4    1.44 s    R4 rc=TIMEOUT>600s  600.09 s    R3 rc=4    0.08 s
$ cost.py dqnest       (a 5 MB gate-shaped file: 10,330 lines of x="$( echo "$( … a )" )" nested 40 deep)
5MB dq-nest d=40 lines=10330   bytes=4999735  bash-n=0  R5 rc=4    5.32 s  gate-file-sources: scripts/g.sh:10332: scripts/h.sh
one dq-nest d=150 / d=190      R5 rc=4 0.06 s each (the edge found);  d=250: rc=4 constructs nested too deep to scan (bash-n=0)
$ cost.py heredocs
50k heredocs sequential              bytes=1100015  bash-n=0  R5 rc=4  0.99 s
50k heredocs on one line             bytes=877797   bash-n=2  R5 rc=4  0.85 s   (bash itself refuses: its per-command heredoc limit)
10k pending + 10k $((1)) one line    bytes=207798   bash-n=2  R5 rc=4  0.91 s   (R5-2's tuple(self.heredocs) per attempt)
10k pending + 10k $( (1) ) one line  bytes=227798   bash-n=2  R5 rc=4  0.25 s
$ cost.py longline
2MB line plain words        R5 rc=4 2.35 s     2MB line $((1))      R5 rc=4 1.05 s     2MB line $( (1) )  R5 rc=4 2.13 s
2MB line one dq string      R5 rc=4 0.76 s     2MB line ;-separated R5 rc=4 2.56 s (bash -n itself crashed: rc -11)
```
- R5-2's numbers reproduce: k=22 in 0.06 s (bound 1 s); k=330 0.57 s, k=360+ refused (builder: 0.59 s and 400 refused). The live
  tree's cost is re-measured in § 9.
- Linear: the 5 MB `$( "$( … )" )` file (5.32 s, about 1 µs per byte), 50,000 heredocs, every 2 MB single line.
- **Super-linear outside D8 — V5-07: the depth × body product of failed `$((` attempts.** A character inside d failed attempts is
  scanned 1 + d times (the builder's D3, true as stated); with a real body that is d × B: k=300 around 100 KB costs 37.64 s through the
  real screen, R3 0.06 s. Cost is linear in k at fixed B (4.39 → 11.95 → 22.97 → 37.64 s) and, by the mechanism, linear in B at fixed
  k; d is capped near 330 by the recursion guard, so the worst case is about 330 × the file size (INFERRED extrapolation: ~6 min for
  1 MB, not run). The k-series itself (body growing with k) is quadratic, as D3 says. R5 is far better than R4 (2^k: > 600 s at
  k=16 on this body) and meets R5-2's numeric lines; the headline "linear in `$((` nesting" holds only in D3's reading ("one
  decision per start"). No fail-open: the hook stalls, then refuses or passes correctly. Not live.
- The recursion guard refuses bash-valid nests (k=360 `$((`, d=250 `$( "$(`): KNOWN (V-14, "nesting past about 150-400 levels").

## 8. MUTANTS (new; never the builder's m1-m13, N13 or N19; `/tmp/vj10r5/tools/mutants.py`, output `/tmp/vj10r5/mutants.out`)

Each on its own scratch tree `/tmp/vj10r5/mut/tree-<id>` (a copy of `/tmp/vj10r5/mut/base` = `git archive 10f1823` of `scripts`,
`tests/test_no_laya_in_gates.py`, `tests/fixtures/decisions`, `.github`, `harness-ports/bin`, `.claude/hooks/edit-snapshot.py`,
`proofs`: 850 files; unmutated there: `112 passed in 10.48s`, screen sha256[:16] `db28614c4bb72601`). Anchor asserted exactly once,
`py_compile`, `--collect-only`, then the whole file (15:18-15:19Z).

| id | line | mutation (a line no builder row targets) | compiles / collected | result | killed by |
|---|---|---|---|---|---|
| MX1 | R5-1 | the refusal names the word's END line: `self.line(start)` → `self.line(self.i)` (`scripts/no_laya_in_gates.py:454`) | yes / 112 | **112 passed — SURVIVED** | — |
| MX2 | R5-1 | `_unquote` keeps the `$` of `$'…'` (`:144`, `in ("'", '"')` → `in ('"',)`) | yes / 112 | 1 failed, 111 passed — KILLED | `test_heredoc_word_in_ansi_c_quotes_without_an_escape_still_reads` |
| MX3 | R5-2 | an equal stored tuple is never trusted (`:352`, `in (None, pending)` → `in (None,)`) | yes / 112 | **112 passed — SURVIVED** | — |
| MX4 | R5-2 | the read counter's baseline one lower, so every failure is stored as a tuple (`:355`, `self.bodies_read - 1`) | yes / 112 | 1 failed, 111 passed — KILLED | `test_nested_arithmetic_attempts_scan_in_bounded_time[heredoc-per-level]` |
| MX5 | R5-4 | a shell text loses its line map (`:539`, `(1, content, True)` → `False`) | yes / 112 | 39 failed, 73 passed — KILLED | 39 tests, e.g. `test_sourced_helper_refused`, `test_shell_member_trigger_is_caught[S12]` |
| MX6 | R5-4 | a PLAIN `run:` value keeps line-for-line (`:522`, `value.style == "\|"` → `in ("\|", None)`) | yes / 112 | **112 passed — SURVIVED** | — |

AF-AP-138, the 40 distinct killing tests by node id on the UNMUTATED base tree: `40 passed in 2.64s` (rc 0).

The survivors are not equivalent (`/tmp/vj10r5/survivors.out`, the mutant screen vs the real one on one fixture each):
```
D-MX1a line continuation before the word  "cat <<\\\n$'E\\tF' >/dev/null\nbody\nE<TAB>F\n. scripts/h.sh\n"   bash ran helper=True bash-n=0
    R5  rc=4 gate-file-unparseable: scripts/g.sh:2: heredoc <<\ | $'E\tF': $'...' escape not translated
    MX1 rc=4 gate-file-unparseable: scripts/g.sh:3: heredoc <<\ | $'E\tF': $'...' escape not translated
D-MX3 no heredoc at all; clean text  "x=$(( $(( $(:\n) ) ) ) )\necho done\n"   bash ran helper=False bash-n=0
    R5  rc=0 no_laya_in_gates: 1 files scanned, clean
    MX3 rc=4 gate-file-unparseable: scripts/g.sh:2: $(( re-read with other heredocs pending
D-MX6 plain run: value over a blank line (W6b)   bash ran helper=True
    R5  rc=4 gate-file-sources: .github/workflows/w.yml:6: scripts/h.sh
    MX6 rc=4 gate-file-sources: .github/workflows/w.yml:7: scripts/h.sh
```
(` | ` marks a newline inside ONE refusal: see V5-09.) Three survivors = three test gaps (V5-08): R5-1(b)'s "naming the operator's
line" is pinned only by single-line words, where the operator's line and the word's line coincide; R5-2's "holds under the same
[heredocs]" branch has no test (MX3 falsely refuses a clean text with no heredoc at all); R5-4's "every scalar style except a literal
block" has no PLAIN multi-line case. The code under test is right on all three (the real screen's lines above); only the pins are
missing. Each needs one fixture: D-MX1a, D-MX3, D-MX6.

## 9. GATES (shared tree, read-only; 2026-09-23T15:22:03Z-15:22:23Z)

```
$ bash scripts/pc_suite.sh set-id -- tests/test_no_laya_in_gates.py
1 files set=e3695f80792b
$ PYTHONDONTWRITEBYTECODE=1 /root/venv-agent-factory/bin/python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/vj10r5/bt1
112 passed in 8.74s
rc=0
$ PYTHONDONTWRITEBYTECODE=1 /root/venv-agent-factory/bin/python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/vj10r5/bt2
112 passed in 8.71s
rc=0
$ python3 scripts/no_laya_in_gates.py; echo rc=$?
no_laya_in_gates: 40 files scanned, clean
rc=0
$ python3 scripts/no_laya_in_gates.py --staged; echo rc=$?
no_laya_in_gates: 40 files scanned, clean
rc=0
$ /root/venv-agent-factory/bin/python -m pyflakes scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py; echo rc=$?
rc=0
```
Both counts carry set `e3695f80792b` (1 file). R5-2's live-tree bound, an interleaved A/B (R4 = `/tmp/vj10r5/screens/r4.py`, R5 =
`scripts/no_laya_in_gates.py`, `python3`, 10 runs each, every run rc 0 and `40 files scanned, clean`, 15:22:58Z, load 1.0-2.1):
```
worktree R4 median 0.392 s  R5 median 0.397 s  ratio R5/R4 1.013
--staged R4 median 0.829 s  R5 median 0.853 s  ratio R5/R4 1.028
```
+1.3 % and +2.8 %, inside the 10 % bound. Red-green of the builder's 20 new tests, reproduced on a scratch copy (`/tmp/vj10r5/red`:
the PIN subset with R4's screen, sha256[:16] `ab33c767c65c6f56`, and R5's test file): `15 failed, 5 passed, 92 deselected in 11.55s`
— the same 15 ids the builder lists (AQ1-AQ4, PQ5b, mid-word; V-04, heredoc-per-level; bash-valid, trusted-memo-reads-clean; Y2b,
Y2c, Y13, Y14; the ends-open test). The 5 green ones are the preservation tests the builder declares (D5). The builder's live-exposure
census, re-run: `.github/workflows/planning-checks.yml {'None': 1}`, `.github/workflows/stage0-ci.yml {'None': 12, "'|' multiline": 4}`
(the same). Other lanes' uncommitted files were in the tree during these runs (`proofs/S0-02/check_buzz_authz.py`, a LISTED gate,
among them); the screen read 40 clean with them.

## FINDING INVENTORY (no severity filter; V5- ids are this lane's)

Each row: classification · evidence · contract mapping · canonical path · material effect · reproduction · suggested fix.

- **V5-05 BLOCKER — R5-4: a node property on the line before a `run:` scalar moves the named line out of the value, and shifts a
  literal block's line map.** SOLID.
  - Evidence: § 4 (W10, W10b, W11, W12, W12b through the real screen) and § 6 C5 (the real hook names `vj.yml:7`, the `|` line; the
    edge is on line 8). PyYAML's `ScalarNode.start_mark` is the node's first property (`&x`, `!!str`), so `start_mark.line + 2`
    (`scripts/no_laya_in_gates.py:521`, `value.start_mark.line`) is the indicator's own line when the property sits on the line above it.
  - Contract: R5-4 — "A workflow refusal names a line inside the value" (false for W10b, W11, W12, W12b), "a literal block (`|`),
    which keeps its line-for-line map" (false for W10: the helper on line 9 is named 8) and "The docstring says exactly that": the R5
    docstring (`scripts/no_laya_in_gates.py:499-501`) says `the line after the indicator of a block` "(| or >)" and "a refusal in it names
    its own line", both false as stated for W10, W10b and W11. The builder's report repeats both claims (its R5-4 section, "the line
    after the indicator for `|` and `>`", and self-attack 3, "A literal block keeps its line-for-line map").
  - Canonical: the real screen (`--root`) and the real hook (C5). Material: under the brief's clause "a stated claim is false as
    stated" — yes. The verdict is right in every row (rc 4); only the named line is wrong; W11 is worse than R4 (R4 named a line inside
    the value). No live workflow holds an anchor, alias or tag; GitHub's acceptance of these shapes is NOT measured (valid YAML 1.2;
    PyYAML accepts them).
  - Discriminator: W10b — expected 8, R5 names 7; W11 — expected a line in 8-10 (R5-4's rule: 8), R5 names 7; W10 — expected 9,
    R5 names 8.
  - Fix (RUN, § 4): key the first line on the scalar TOKEN (`yaml.scan`), by the node's `end_mark.index`; 112 tests pass, every
    builder Y shape byte-identical, the live tree clean in both modes; no rc changes anywhere, so nothing new leaks or is refused. Add
    W10, W10b and W11 as tests.
- **V5-03 FOLLOW-UP — the D2 guard refuses a family of bash-valid texts R4 reads CLEAN.** SOLID. § 3(b): 570 unique `bash -n`-valid
  texts (seed 31), e.g. `x=$(( <<A $(( $(:\nA\n) ) ) ) )\necho done`; real hook C4 blocked, C4-control (R4) lands; C5 shows that such
  a text already in history blocks every later commit. Contract: R5-2's memo option names no refusal (a declared design addition, D2).
  Material: no — no live-tree shape is refused (the live tree reads clean in both modes). Fix: none needed now. UNRUN question, not a recommendation: re-run a body-reading failed attempt under the new pending heredocs
  once per (start, pending) within a global budget, and refuse only past the budget?
- **V5-07 FOLLOW-UP — super-linear cost outside D8: failed `$((` nests cost depth × body.** SOLID. § 7: k=300 around 100 KB = 37.64 s
  (R3 0.06 s; R4 > 600 s at k=16). The mechanism is the builder's D3 (1 + d scans per character, d ≤ ~330), true as stated.
  Contract: R5-2's numeric lines are met (k=22 0.06 s; live +1.3 % / +2.8 %); its headline "linear" holds only in D3's reading.
  Material: no (no fail-open; a crafted file stalls the hook; not live). UNRUN question, not a recommendation: cap the total re-scan
  work per text and refuse past the cap (fail closed), or reuse the inner command re-scans' segments instead of re-scanning?
- **V5-08 FOLLOW-UP — three new mutants survive (test gaps).** SOLID. § 8: MX1 (R5-1's "naming the operator's line": only single-line
  words are pinned), MX3 (R5-2's equal-tuple trust branch: no test; the mutant refuses a clean text with no heredoc), MX6 (R5-4's
  "every scalar style": no plain multi-line case). Each is non-equivalent (discriminators D-MX1a, D-MX3, D-MX6). Contract: beyond the
  brief's required test list. Material: no (the code is right; the pins are missing). Fix: add D-MX1a, D-MX3 and D-MX6 as tests (each fixture was RUN above: the real screen gives the right answer, and the matching
  mutant gives another).
- **V5-04 FOLLOW-UP — the docstrings that enumerate `_Open`'s causes omit the R5-2 guard.** SOLID (read). The module docstring
  (`scripts/no_laya_in_gates.py:19`, `cannot finish in sync`), `class _Open` (`scripts/no_laya_in_gates.py:112-113`: "The scan cannot finish in sync: a construct is
  still open … or a heredoc word holds an escape"), `class _ShellScan` (`scripts/no_laya_in_gates.py:150-159`) and `_command_segments`
  (`scripts/no_laya_in_gates.py:485`, `_Open: R4-1, R5-1; or nesting too deep`); only `def arith` (`scripts/no_laya_in_gates.py:338-348`) describes it. Contract: no frozen line
  requires these texts (R5-2 has no docstring clause). Material: documentation only. Fix (a doc edit, UNRUN): name the guard in the four places.
- **V5-01 KNOWN (issue #37, class F-B3) — the command word spelled in ANSI-C or locale quoting.** SOLID. § 2 A5-A9 (`$'.' x`,
  `$'\x2e' x`, `$'source' x`, `$'\x73ource' x`, `$"." x`): bash runs the helper; R3, R4 and R5 read CLEAN; real hook C3 lands. New
  spellings of F-B3's `'.' x` / `\. x` / `'source' x` (`tasks/briefs/laya/VERIFY-J1-0-R23-STAMP-report.md:278`). Not R5 code.
- **V5-02 INFO — `<<\$'EOF'` with no source line: a false refusal R5 adds.** SOLID. § 2 S5 [no-edge]: R3/R4 CLEAN, R5 rc 4; bash
  and `_unquote` both read `$EOF`. Mandated by R5-1(b)'s literal predicate ("a heredoc word holding `$'` with a backslash"). Not live.
- **V5-06 INFO — R5-3's "another directory" is true only for a directory the resolver cannot tell.** SOLID. § 5 E4: a base
  re-pointed to an absolute literal (`Path("/tmp/elsewhere")`) is refused. The comment claims less enforcement than exists, never
  more, so R5-3 holds. Fix (a comment edit, UNRUN, optional): "another directory held in a value the resolver cannot tell".
- **V5-09 INFO — a refusal can span two stderr lines.** SOLID. § 8 D-MX1a: R5-1's message embeds the raw word
  (`scripts/no_laya_in_gates.py:454`, `escape not translated`), and a word holding a newline (a line continuation before it, or a newline inside `$'…'`) splits one
  refusal across two lines; R4's `heredoc <<… pending` does the same on that text (pre-existing class). The message also drops a `<<-`
  operator's `-` (S1). UNRUN question: escape newlines in the printed word (`%r` would change every existing R5-1 text the tests pin)?
- **V5-10 UNVERIFIED — the memo's stated premise omits one read.** `def arith`'s docstring (`scripts/no_laya_in_gates.py:343-344`, `the only state an attempt reads`:
  "the pending heredocs are the only state an attempt reads, and only through read_bodies") and the builder's "Exactness, by
  construction" omit the nested memo comparison, which reads the memo dict and compares the pending tuple without `read_bodies`. The
  conclusion survived every test here (§ 3(a): 3,603 targeted `None` hits, 0 wrong); I could not build a text where the omission
  changes a verdict. Not blocking (static; no frozen line requires the premise). Fix (a doc edit, UNRUN): state the premise with the nested lookup.
- **V5-11 INFO — `_workflow_runs`'s reason clause is loose.** "any other style (plain, quoted, folded) folds or escapes its line
  breaks" (`scripts/no_laya_in_gates.py:501`, `folds or escapes its`) is not true of a folded block's more-indented lines (YAML keeps those breaks: Y2b); the
  rule it justifies is what the code does.
- **V5-12 INFO (KNOWN, V-14) — the recursion guard refuses bash-valid deep nests** (k=360 `$((`, d=250 `$( "$(`; § 7).
- **V5-13 INFO — confirmations.** R5-1 has no new fail-open (§ 2). The memo's exactness conclusion survives (§ 3(a)). R5-2's numbers,
  R5-3's comment and R5-5's corrections are true (§§ 5, 7, 9). The builder's RED claim (15 of 20) reproduces (§ 9). KNOWN rows
  re-observed only as the corrections' evidence: TK1, CA5 (V-02), DA1 (V-03), Y9/Y9b/Y9c (V-08); D8 measured (2.06 s at k=2000).

### Predicate table (the rows closest to blocking; every other row fails conjunct 1 or 3 plainly)
| id | 1 contract | 2 canonical (real screen / real hook) | 3 material | 4 discriminator | 5 in boundary | BLOCKS? |
|---|---|---|---|---|---|---|
| V5-05 | yes — R5-4's own sentences (inside the value; literal line map; the docstring says exactly that) | yes / yes (C5) | yes — stated claims false as stated (the R5 docstring, the builder's R5-4 section and self-attack 3); the verdict itself is right | yes — W10b 7 vs 8; the RUN fix names 8 | yes — `_workflow_runs`, S | **yes** |
| V5-03 | weak — D2, a declared addition to R5-2's memo option | yes / yes (C4) | no — no live-tree shape refused | yes — G1 (R4 0, R5 4) | yes | no → FOLLOW-UP |
| V5-07 | partial — R5-2's headline word; its numeric lines are met | yes / not run | no — no fail-open, not live, D3 true as stated | yes — k=300 B=100 KB 37.64 s vs R3 0.06 s | yes | no → FOLLOW-UP |
| V5-08 | partial — clauses of R5-1/R5-2/R5-4 beyond the required test list | yes (scratch copies) | no — pins missing, code right | yes — D-MX1a, D-MX3, D-MX6 | yes, T | no → FOLLOW-UP |
| V5-04 | no — no frozen line on these docstrings | read | documentation only | yes — the guard raises `_Open` | yes | no → FOLLOW-UP |
| V5-01 | KNOWN F-B3 (issue #37) | yes / yes (C3) | fail-open, but KNOWN and pre-R4 | yes — A5 | no — issue #37 | no → KNOWN |

## GATE RECOMMENDATION

**`NOT-READY`** — one finding, **V5-05**, meets the complete blocking predicate as the brief writes it: R5-4's own sentences
("names a line inside the value"; a literal block "keeps its line-for-line map"; "The docstring says exactly that") are false for a
node property on the line before the scalar, reproduced through the real screen and the real hook, with a concrete discriminator, inside
`scripts/no_laya_in_gates.py`. **This recommendation rests on the materiality clause "a stated claim is false as stated"** (the
reading the coordinator applied to V-06 last round). Every verdict (rc) is right; only the named line and the docstring are wrong; the
shapes are exotic and not live. If the coordinator reads a wrong diagnostic line on a non-live shape as immaterial, the recommendation
becomes **`MERGE-READY-WITH-FOLLOWUPS`** (V5-03, V5-04, V5-07, V5-08 as follow-ups). The repair is small and already RUN on a scratch
copy (§ 4): four lines in `_workflow_runs`, plus W10, W10b and W11 as tests. Everything else AMENDMENT 4 names reproduces: R5-1 (no new
fail-open; AQ1 blocked by the real hook), R5-2 (k=22 0.06 s; live +1.3 % / +2.8 %; no wrong memo decision in 72,000 re-decided hits),
R5-3 (no over-claiming word) and R5-5 (all three corrections true).

## Evidence discipline — reproduced, read, skipped

- Reproduced here (VERIFIED): the premise; every item-2, item-4 and item-5 fixture under bash (or python) and the real screen; the memo
  differential and both shadow oracles; the guard family; the cost series; six new mutants with AF-AP-138; the real hook (C1-C5); the
  gates; the builder's RED claim; the live cost A/B; the live-exposure census; the V5-05 fix on a scratch copy.
- Read, not executed: the R5 diff (`git diff 10f1823^ 10f1823 -- scripts/no_laya_in_gates.py`); the docstrings for V5-04, V5-10,
  V5-11; the per-entry `# base:` sources (`scripts/lint_delta.py:35`, `--show-toplevel`; `scripts/proof-runner:282` and `scripts/ledger-gen:66`, `args.root.resolve()`).
- Skipped, by the brief's rules: the builder's own mutants (m1-m13, N13, N19) and its sweep driver (machinery not changed, the readiness
  claim does not depend on them); re-deriving issue #46 / #37 rows (KNOWN); GitHub Actions itself (INFERRED side of W-shapes and Y7b/Y7c).
- Instruments named: bash 5.2.21 (oracle), PyYAML 6.0.3 (the hook's venv), R3/R4 from `git show`, R5 = the shared tree's file read-only.
  Code intel: the brief's pack (`scripts/lane_context.sh … -o /tmp/vj10r5/pack.md`: graft skeletons, GitNexus impact, crg callers,
  ripwire, AP screen `AF-AP-40: 7`, all in `_glob_structural`, pre-existing).

## Appendix — key fixture texts (verbatim Python literals; each shell text is saved as `scripts/g.sh` after `#!/bin/bash\n`, each workflow as `.github/workflows/w.yml`)

```python
H = ". scripts/h.sh"; TAB = "\t"
HEAD = "on: push\njobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n"
# item 2 (the trap layout: body, then bash's and the scan's delimiter lines around H)
S1_bash_first = "cat <<-$'\\tEOF' >/dev/null\n" + TAB + "body\n" + TAB + "EOF\n" + H + "\n\\tEOF\n"
S5_no_edge    = "cat <<\\$'EOF' >/dev/null\nbody\n$EOF\necho done\n"
A5            = "$'.' scripts/h.sh\n"
# item 3 (the D2 guard family) and the survivors' discriminators
G1     = "x=$(( <<A $(( $(:\nA\n) ) ) ) )\necho done\n"
D_MX1a = "cat <<\\\n$'E\\tF' >/dev/null\nbody\nE" + TAB + "F\n" + H + "\n"
D_MX3  = "x=$(( $(( $(:\n) ) ) ) )\necho done\n"
D_MX6  = HEAD + "      - run: echo a\n\n          " + H + "\n      - run: echo ok\n"
# item 4, V5-05
W10  = HEAD + "      - run: &x\n          |\n          echo a\n          " + H + "\n"
W10b = HEAD + "      - run: &x\n          |\n          " + H + "\n"
W11  = HEAD + "      - run: !!str\n          >\n          echo a\n\n          " + H + "\n"
W12  = HEAD + "      - run: &x\n          " + H + "\n"
W12b = HEAD + "      - run: !!str\n          \"" + H + "\"\n"
# item 7, V5-07
body_heavy = lambda k, B: "v=" + "$(( " * k + "x " * (B // 2) + " ) )" * k + "\n" + H + "\n"
```

## report_lint (two fix rounds of the three allowed; pasted)

```
$ python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/VERIFY-J1-0-R5-report.md --root .
round 1: report_lint: 38 refs — OK 14, NEAR 1, MISS 15, UNCHECKABLE 8, UNRESOLVED 0 (worktree)      FLOOR — OK 14 < --min-refs 15   lint rc=1
round 2: report_lint: 38 refs — OK 36, NEAR 0, MISS 0, UNCHECKABLE 2, UNRESOLVED 0 (worktree)       lint rc=0
```
Round 1's fixes: a backticked token copied from each cited line onto the citing report line; three ranges widened so the named symbol
falls inside (`class _Open` 112-113, `class _ShellScan` 150-159, `def arith` 338-348). The 2 UNCHECKABLE are the pasted E1c output
line (§ 5), which cites the throwaway VARIANT of `scripts/lint_delta.py` (its line 107 is the variant's inserted site, not the
repository file's line 107); left verbatim.

## DISCREPANCIES

- **DV-1 — the tree moved during the lane; no item changed.** HEAD 905a8c7 / origin fa4532e at 14:36Z; HEAD 00b85df / origin 9801fb5
  at 15:26Z. The four boundary blobs stayed the PIN's at every read (`4f88fbb47d02`, `d2e04630f09d`, `8eaccfa87a98`, `7731a91c7d3e`).
  Other lanes' uncommitted files came and went (J1-1-R2's, B11's, then `tests/test_validate_ledger.py` and
  `tasks/briefs/continuity/S198A-report.md`); I touched none of them.
- **DV-2 — item 6's "strongest new fail-open" does not exist.** No new fail-open was found in items 2-4, so commit C3 uses the KNOWN
  F-B3 member A5, labelled as such.
- **DV-3 — C4-control swapped R4's screen into the THROWAWAY worktree** for one commit and restored R5 (sha256[:16] printed). That
  commit stayed in the throwaway history, which is why C5's output also shows the G1 refusal. The shared tree was never touched.
- **DV-4 — interpreter.** The harness runs the screens with the hook's `$PY` (`/root/venv-agent-factory/bin/python`, PyYAML 6.0.3); the
  brief's gate commands use system `python3` (PyYAML 6.0.1). Both read the live tree `40 files scanned, clean` in both modes.
- **DV-5 — one extrapolation.** V5-07's "~6 min for 1 MB at k=300" is INFERRED from the measured linear series, not run.
- **DV-6 — the recommendation depends on a reading.** NOT-READY rests on the literal clause "a stated claim is false as stated"
  (V5-05); the alternative reading is stated on the recommendation itself.

## NOT-done

- No edit, stage, commit or push in the shared tree; no bridge or PC use. My only file is this report.
- The V5-05 fix was run only on a scratch copy (its diff is in § 4); it is not applied anywhere.
- GitHub Actions was not run: GitHub's acceptance of W10-W12b (anchors, tags) and the GitHub side of Y7b/Y7c stay INFERRED.
- The builder's mutants m1-m13, N13 and N19 and its sweep driver were not re-run (outside the brief's scope).
- No `/bug-echo` run and no registry row (`docs/INCIDENT-LOG.md` is outside the boundary). Candidate classes for the coordinator:
  a YAML node's `start_mark` taken as its scalar's position (V5-05: node properties sit before the scalar); a refusal message that
  embeds raw input and so can span lines (V5-09).
- Scratch `/tmp/vj10r5/` (fixture trees, mutant trees, the throwaway repository, the tools) is removed at the end, as the brief says;
  the outputs are pasted above and the key fixture texts are in the appendix.
