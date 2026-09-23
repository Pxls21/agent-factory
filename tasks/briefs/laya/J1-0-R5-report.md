# J1-0-R5 — report (task #188; AMENDMENT 4; lane j1-0-r5, sandbox, shared tree)

Brief: `tasks/briefs/laya/J1-0-R5-brief.md`. PIN e37a052. Boundary: `scripts/no_laya_in_gates.py`, `tests/test_no_laya_in_gates.py`,
this report. Scratch: `/tmp/j10r5/`. Honey `ultra` Lever-2: data, not prose. Evidence tiers: VERIFIED (run here, pasted),
INFERRED, ASSUMED.

## PREMISE (re-measured, 2026-09-23 13:0x-13:19Z) — VERIFIED, no mismatch

```
$ git rev-parse HEAD            (at dispatch; 13:19Z the coordinator landed 1e4c40a, a brief-only commit: tasks/briefs/s0-02-support/B10-brief.md)
688b4bdb5f3def448692075eed108cd9998daee0
$ for rev in e37a052 688b4bd HEAD 0e7b6c3: git rev-parse $rev:<screen> $rev:<tests>   (+ git hash-object of the worktree)
ae8b2046e118f6cc2bb8ce1b51f8600fc27dc450   (screen, all four revs and the worktree)
9790cb714afa10c555467fc8f25db9aa5d7f1c4b   (tests, all four revs and the worktree)
worktree == HEAD for both boundary files
PIN == 688b4bd for both boundary files      (688b4bd adds only transcripts/sandbox/chat-2026-09-0{3,23}.md)
$ git log -1 --format='%h %s' -- scripts/no_laya_in_gates.py | cut -c1-90
0e7b6c3 J1-0-R4 landed (task #172; GATED-PENDING-VERIFY): the never-a-gate screen scans to
$ grep -n '^def _unquote\|^    def dollar\|^    def arith\|^def _workflow_runs\|start_mark\|^ALLOWED_DYNAMIC_LOADS\|never more\|re-pointed at another file\|a folded or flow value has no line' scripts/no_laya_in_gates.py
126:def _unquote(word):
313:    def dollar(self, in_dq):
332:    def arith(self, start, skip, what):
470:def _workflow_runs(content):
473:    starts on (a folded or flow value has no line of its own after the first)."""
492:                    runs.append((value.start_mark.line + (2 if value.style in ("|", ">") else 1), value.value))
696:# reviewed to reach) -> how many such loads the gate file may hold, never more. A load is covered only
698:# re-pointed at another file (the F-B5 class). Closed: a new entry is a reviewed change here.
699:ALLOWED_DYNAMIC_LOADS = {
$ bash scripts/pc_suite.sh set-id -- tests/test_no_laya_in_gates.py
1 files set=e3695f80792b
$ PYTHONDONTWRITEBYTECODE=1 /root/venv-agent-factory/bin/python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/j10r5/bt0 | tail -1
92 passed in 7.30s
$ python3 scripts/no_laya_in_gates.py; python3 scripts/no_laya_in_gates.py --staged
no_laya_in_gates: 40 files scanned, clean      rc=0
no_laya_in_gates: 40 files scanned, clean      rc=0
# R3 = git show 5090671^:scripts/no_laya_in_gates.py (blob 18c3939889cf = 0e7b6c3^'s; 5090671 is the pre-push twin of 0e7b6c3)
# V-01 (AQ1's shape) in /tmp/j10r5/v01: scripts/g.sh listed, scripts/h.sh unlisted
$ cat -A scripts/g.sh
#!/bin/bash$
cat <<$'echo \x41'$
echo A$
. scripts/h.sh$
echo \x41$
$ bash scripts/g.sh; echo "bash rc=$?"
HELPER-RAN
x41
bash rc=0
$ python3 /tmp/j10r5/r3.py --root /tmp/j10r5/v01; echo R3 rc=$?
gate-file-sources: scripts/g.sh:4: scripts/h.sh
R3 rc=4
$ python3 /tmp/j10r5/r4.py --root /tmp/j10r5/v01; echo R4 rc=$?
no_laya_in_gates: 1 files scanned, clean
R4 rc=0
# V-04 (/tmp/j10r5/tools/kseries.py: "#!/bin/bash\nv=" + "$(( "*k + "x" + " ) )"*k + "\n", one listed gate)
k=14 bytes=128 bash-n=ok R3 rc=0 0.06 s  no_laya_in_gates: 1 files scanned, clean
k=16 bytes=144 bash-n=ok R3 rc=0 0.04 s  no_laya_in_gates: 1 files scanned, clean
k=18 bytes=160 bash-n=ok R3 rc=0 0.05 s  no_laya_in_gates: 1 files scanned, clean
k=14 bytes=128 bash-n=ok R4 rc=0 0.16 s  no_laya_in_gates: 1 files scanned, clean
k=16 bytes=144 bash-n=ok R4 rc=0 0.47 s  no_laya_in_gates: 1 files scanned, clean
k=18 bytes=160 bash-n=ok R4 rc=0 1.67 s  no_laya_in_gates: 1 files scanned, clean
```
Tools: GNU bash 5.2.21(1)-release; Python 3.11.15 (system and venv); PyYAML 6.0.3 (venv).
Live exposure (grep over the 40 listed files, and a `yaml.compose_all` census of the two listed workflows): no `<<$'` in any
listed gate; `run:` styles are `{'None': 1}` (planning-checks) and `{'None': 12, "'|' multiline": 4}` (stage0-ci). So R5-1 and
R5-4 cannot change a live verdict; R5-2 must not (the memo is exact, below).

## Outcome (read first)

- [x] R5-1, R5-2, R5-3, R5-4 built in `scripts/no_laya_in_gates.py`; R5-5 is the corrections section below. VERIFIED.
- [x] 20 new tests in `tests/test_no_laya_in_gates.py`, appended; nothing removed. 15 are RED at the PIN. The other 5 are
      preservation tests, green at both by design; they kill mutants m4, m5, m8, m13 and N13. VERIFIED.
- [x] Gates: `112 passed` twice, set `e3695f80792b`; the live tree is `40 files scanned, clean` in both modes; the live scan cost
      is within ±1.6 % (interleaved A/B); the real hook blocks AQ1 and lands a clean commit; pyflakes and AP screen show no new hit. VERIFIED.
- [x] 15 mutants (m1-m13, plus the verifier's N13 and N19): all KILLED, each killing test green on the unmutated tree. VERIFIED.
- [ ] **The differential's last rule is NOT met on 10 measured rows and 2 inferred ones, all pre-existing:** TK1-TK5, CA5 and
      DA1 (bash runs the helper), Y9, Y9b and Y9c (python runs it); Y7b and Y7c (GitHub, inferred). Meeting the rule means
      fixing V-02/V-03/V-07/V-08, which the brief forbids. D1.
- [ ] One design addition beyond the contract's words: R5-2's memo refuses a revisit it cannot prove, which adds a new
      refusal text. D2 has the reason and the evidence.

## Per contract line

**R5-1 — option (b), chosen.** A heredoc word holding `$'` and a backslash is refused as `gate-file-unparseable:
<file>:<line>: heredoc <<WORD: $'...' escape not translated`, exit 4, naming the operator's line.
- Code: `scripts/no_laya_in_gates.py:453` (`if "$'" in word and "\\" in word:` in `def heredoc`), the line after the
  existing `heredoc << without a delimiter` refusal. Docstrings updated:
  - the module docstring, `scripts/no_laya_in_gates.py:20` (`heredoc word holding $' and a backslash`);
  - `scripts/no_laya_in_gates.py:112` (`class _Open`);
  - `scripts/no_laya_in_gates.py:128` (`def _unquote`): it reads a `$'…'` part as `'…'`, which is right only without a backslash.
- Why (b), not (a):
  - (b) is one predicate that holds for every ANSI-C escape family: `\a … \cx`, `\u` and `\U`, whose output depends on the
    locale, and `\0`/`\x00`/`\c@`, which truncate the word at a NUL.
  - (a) would re-implement bash's translation table, about 15 families, each one a new chance of the fidelity regression
    that produced V-01 (AF-AP-153).
  - The cost of (b) is false refusals of exotic words. No listed gate has any `<<$'` (premise grep).
  - bash's own parse, measured by `declare -f` on a function holding each heredoc (`/tmp/j10r5/tools/bashdelim.py`), confirms
    the mechanism:
    `$'echo \x41'` → `echo A`, `$'E\'F'` → `E'F`, `$'E\x4fF'` → `EOF`, `$'EOF'` → `EOF`; inside double quotes `"$'E\tF'"`
    stays literal, and so does `\$'E\tF'`.
- Known over-refusals of (b), all fail-closed: `"$'E\tF'"` and `\$'E\tF'` (bash reads them literally, and `_unquote` agrees);
  PQ5a (bash treats the `.` line as body text; R4 refused it at line 5 as a source edge, R5 at line 2 as an escape).
- A line continuation inside the word (`<<$\`, newline, `'E\tF'`) does not reach the predicate. The scan's delimiter then
  holds a newline and can never match, so R4-1 refuses it (`heredoc <<$<newline>E\tF pending`) in both R4 and R5; measured,
  and bash runs the helper there, so the refusal is right.
- Tests: `test_heredoc_word_with_an_ansi_c_escape_is_refused` (`tests/test_no_laya_in_gates.py:1119`; AQ1, AQ2, AQ3, AQ4,
  PQ5b, plus `mid-word` `E$'\x4f'F`, which R3 AND R4 both read CLEAN while bash runs the helper); the positive control
  `test_heredoc_word_in_ansi_c_quotes_without_an_escape_still_reads` (`tests/test_no_laya_in_gates.py:1130`: `<<$'EOF'`, clean,
  and bash never runs the helper).

**R5-2 — the memo.** The decision is made once per start position.
- Code:
  - `def arith` (`scripts/no_laya_in_gates.py:338`): a failure is stored in `self.not_arith` keyed by the start
    (`scripts/no_laya_in_gates.py:168`, `self.not_arith = {}`) with `None` when the attempt read no heredoc body, else the
    `pending` heredocs it ran under (`scripts/no_laya_in_gates.py:367`, `self.not_arith[start] = None if self.bodies_read == reads else pending`).
  - A revisit returns False when the stored value is `None` or equals the current `pending`; otherwise it raises
    `_Open` with `re-read with other heredocs pending` (`scripts/no_laya_in_gates.py:354`). It never re-runs. D2 says why.
  - `def read_bodies` counts every call (`scripts/no_laya_in_gates.py:462`, `self.bodies_read += 1`), even one with
    nothing pending.
- Exactness, by construction. Besides the text, an attempt reads one piece of state: the pending heredocs, and only through
  `read_bodies`. So R5's segment list equals R4's for any text on which the guard does not fire; when it fires, R5 refuses.
  R5 is never CLEAN where R4 refused. Checked on the live tree with R4's and R5's `_command_segments`:
  `worktree: 27 shell texts, 2006 segments, 0 differ` and `index: 27 shell texts, 2006 segments, 0 differ`;
  `_source_errors` output is identical.
- Cost (the k-series, `/tmp/j10r5/tools/kseries.py`, same session, 13:47Z):
  ```
  k=20 bytes=176 bash-n=ok R4 rc=0 6.75 s  no_laya_in_gates: 1 files scanned, clean
  k=22 bytes=192 bash-n=ok R4 rc=0 27.57 s  no_laya_in_gates: 1 files scanned, clean
  k=22 bytes=192 bash-n=ok R3 rc=0 0.04 s  no_laya_in_gates: 1 files scanned, clean
  k=14 bytes=128 bash-n=ok R5 rc=0 0.05 s  no_laya_in_gates: 1 files scanned, clean
  k=16 bytes=144 bash-n=ok R5 rc=0 0.07 s  no_laya_in_gates: 1 files scanned, clean
  k=18 bytes=160 bash-n=ok R5 rc=0 0.07 s  no_laya_in_gates: 1 files scanned, clean
  k=20 bytes=176 bash-n=ok R5 rc=0 0.11 s  no_laya_in_gates: 1 files scanned, clean
  k=22 bytes=192 bash-n=ok R5 rc=0 0.06 s  no_laya_in_gates: 1 files scanned, clean
  # the heredoc-per-level series ("v=" + "$(( <<Wj " per level + "x" + " ) )"*k, then the k delimiter lines; bash -n accepts it)
  k=16 bytes=284 bash-n=0 R4 1.10 s rc=0 no_laya_in_gates: 1 files scanned, clean
  k=16 bytes=284 bash-n=0 R5 0.06 s rc=0 no_laya_in_gates: 1 files scanned, clean
  k=22 bytes=392 bash-n=0 R5 0.06 s rc=0 no_laya_in_gates: 1 files scanned, clean
  # toward the recursion guard (dev copy, same code)
  k=100 bytes=816 bash-n=ok R5 rc=0 0.13 s   k=200 bytes=1616 R5 rc=0 0.23 s   k=330 bytes=2656 R5 rc=0 0.59 s
  k=400 bytes=3216 bash-n=ok R5 rc=4 0.06 s  gate-file-unparseable: scripts/g.sh:1: constructs nested too deep to scan
  ```
  Live tree, interleaved A/B, 10 runs each (`/tmp/j10r5/tools/abtime.py`, 13:44Z): worktree R5/R4 wall median ratio
  0.984 (-1.6 %), CPU 0.998; `--staged` wall 1.014 (+1.4 %), CPU 1.005. Bound: 10 %. Met.
- Tests:
  - `test_nested_arithmetic_attempts_scan_in_bounded_time` (`tests/test_no_laya_in_gates.py:1155`): `V-04`, k=22, and
    `heredoc-per-level`, k=22; 5 s timeout; each must still find the source edge after the nest.
  - `test_arithmetic_memo_keeps_every_decision` (`tests/test_no_laya_in_gates.py:1180`): the brief's "same verdicts as before"
    fixture. An R4 arithmetic case (`shift-in-subshell`, `arith-in-subshell`) and an R4 subshell case (`subshell-in-subshell`),
    each inside a failed outer attempt, so the memo is read.
  - `test_arithmetic_memo_refuses_a_revisit_it_cannot_prove` (`tests/test_no_laya_in_gates.py:1204`).

**R5-3 — the comment.** `scripts/no_laya_in_gates.py:726-732`, above `ALLOWED_DYNAMIC_LOADS`, states only what
`_load_errors` enforces:
- an entry binds (gate file, literal repo path) and a SITE count;
- more sites than the count are all refused, and the path must itself be listed;
- the base directory is not bound. A re-pointed base still matches, and a wrapper that runs one site twice makes a second
  load that counts once (F-B5's class, issue #37).
"never more" and "cannot be re-pointed at another file" are gone. The entries and counts are unchanged. **R5-3 needs no test
(a comment); none was added.** The existing `test_closed_sets_locked` still pins the entries.

**R5-4 — workflow lines.**
- `def _workflow_runs` (`scripts/no_laya_in_gates.py:497`) returns `(first line, text, literal)`, where literal is
  `value.style == "|"` (`scripts/no_laya_in_gates.py:522`). The first line is still computed as before: the line after the
  indicator for `|` and `>`, else the start mark's line.
- `def _source_errors` (`scripts/no_laya_in_gates.py:529`) names the first line for every refusal in a non-literal value,
  both `gate-file-sources` (`scripts/no_laya_in_gates.py:556`, `lineno if by_line else first_line`) and
  `gate-file-unparseable` (`scripts/no_laya_in_gates.py:558`, `opened[0] if by_line else first_line`). A non-workflow text keeps its line-for-line map
  (`scripts/no_laya_in_gates.py:539`, `texts = [(1, content, True)]`).
- The `_workflow_runs` docstring states exactly that mapping.
- Tests:
  - `test_folded_or_quoted_run_refusal_names_its_first_line` (`tests/test_no_laya_in_gates.py:1227`): Y2b→7, Y2c→7, Y13→6,
    Y14→6. R4 named 8, 8, 7 and 7; for Y13, 7 is the next step's line.
  - `test_quoted_run_that_ends_open_names_its_first_line` (`tests/test_no_laya_in_gates.py:1237`): the R4-1 branch;
    R4 named 7, R5 names 6.
  - `test_literal_run_block_keeps_its_line_map` (`tests/test_no_laya_in_gates.py:1246`): Y1, a heredoc then a source edge
    inside a `|` block, refused at 10, unchanged.
  - The existing `test_workflow_run_ending_inside_a_construct_names_its_yaml_line` (`tests/test_no_laya_in_gates.py:819`) still passes.

**R5-5:** the section "Corrections to the J1-0-R4 report" below.

## RED at the PIN, GREEN after (pasted)

RED: the new test file run in `/tmp/j10r5/red` (a `git archive e37a052` subset, screen sha256[:16] `ab33c767c65c6f56` = the PIN):
```
$ pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/j10r5/btr1 -k '<the 20 new tests>'
FAILED ...::test_heredoc_word_with_an_ansi_c_escape_is_refused[AQ1]      (AQ2, AQ3, AQ4, PQ5b, mid-word the same)
FAILED ...::test_nested_arithmetic_attempts_scan_in_bounded_time[V-04]   (heredoc-per-level the same)
FAILED ...::test_arithmetic_memo_refuses_a_revisit_it_cannot_prove[bash-valid]   (trusted-memo-reads-clean the same)
FAILED ...::test_folded_or_quoted_run_refusal_names_its_first_line[Y2b]  (Y2c, Y13, Y14 the same)
FAILED ...::test_quoted_run_that_ends_open_names_its_first_line
15 failed, 5 passed, 92 deselected in 11.97s
```
The reasons, from `--tb=line`, in the same order:
- AQ*: the rc assert fails, because the PIN reads CLEAN (the `_bash_runs_helper` check before it passed).
- V-04 and heredoc-per-level: `Failed: …: the scan of 22 nested $(( attempts took more than 5 s`.
- The memo refusals: the PIN names `gate-file-sources: scripts/g.sh:5` and `:6`.
- Y2b and Y2c: the PIN names `w.yml:8`. Y13 and Y14: `w.yml:7`.
- The ends-open test: the PIN names `w.yml:7: quote " open`.
The 5 that pass at the PIN are preservation tests, green by design: the `<<$'EOF'` control, the three memo-decision rows,
and the literal-block case. Their RED is in the mutant table (m4, m5, m8, m13, N13). GREEN after: the gates section.

## The R3 differential (gate; `/tmp/j10r5/tools/diff3.py` on the final screen; its output file was written 13:44:14Z)

Screens: R3 = `git show 5090671^:scripts/no_laya_in_gates.py`, R4 = the PIN, R5 = the final file (sha256[:16] `db28614c4bb72601`).
The verifier's instrument was removed. Every shape is REBUILT from the verify report's one-line descriptions. The rebuilds
reproduce every R3/R4 verdict the report records: AQ1-AQ4 and PQ5b (R3 rc 4 at line 5, R4 rc 0), AQ5 and TK7 and DA2
(R4-1), CA5, TK1-TK5 and DA1 (clean in both), Y2b (R3 9, R4 8), Y13 (R3 0, R4 7), and the rest of § 2/§ 4's R4 column.
Oracle ("runs?"):
- shell shapes: `bash scripts/g.sh`;
- workflow shapes: every PyYAML `run:` value run by `bash -c`, or by `python3 -c` for a `shell: python` step;
- the helpers write a marker file, so captured output still counts.
`g.sh`/`w.yml` below are the fixture's `scripts/g.sh` / `.github/workflows/w.yml`.

| shape | runs? | R3 | R4 | R5 | rule |
|---|---|---|---|---|---|
| AQ1 | yes | rc=4 g.sh line 5 | rc=0 | rc=4 g.sh line 2 `heredoc <<$'echo \x41': $'...' escape not translated` | ok (fixed) |
| AQ2 | yes | rc=4 line 5 | rc=0 | rc=4 line 2 `<<$'E\x4fF'` | ok (fixed) |
| AQ3 | yes | rc=4 line 5 | rc=0 | rc=4 line 2 `<<$'E\\F'` | ok (fixed) |
| AQ4 | yes | rc=4 line 5 | rc=0 | rc=4 line 2 `<<$'E\'F'` | ok (fixed) |
| AQ5 | yes | rc=4 line 5 | rc=4 line 2 `heredoc <<\tEOF pending` | rc=4 line 2 `<<$'\tEOF'` escape | ok |
| PQ1-PQ4 | yes | rc=0 | rc=4 line 5 | rc=4 line 5 | ok |
| PQ5a | no | rc=4 line 5 | rc=4 line 5 | rc=4 line 2 `<<$'E\tF'` escape | ok (still refused; false refusal) |
| PQ5b | yes | rc=4 line 5 | rc=0 | rc=4 line 2 `<<$'E\tF'` escape | ok (fixed) |
| PQ6a, PQ7a | yes | rc=4 line 5 | rc=4 line 5 | rc=4 line 5 | ok |
| PQ6b, PQ7b | no | rc=4 line 4 | rc=0 | rc=0 | R3 refusal lost since R4; right (the `.` line is body text; bash never runs it) |
| TK1, TK2, TK3, TK4, TK5 | yes | rc=0 | rc=0 | rc=0 | **NOT MET** (pre-existing; V-02, issue #46; D1) |
| TK6 | yes | rc=4 line 2 | rc=4 line 2 | rc=4 line 2 | ok |
| TK7 | yes | rc=4 line 3 | rc=4 line 2 `heredoc <<2 pending` | the same as R4 | ok |
| CA1-CA4, CA6 | yes | rc=4 line 3 | rc=4 line 3 | rc=4 line 3 | ok |
| CA5 | yes | rc=0 | rc=0 | rc=0 | **NOT MET** (pre-existing; V-02; D1) |
| CA7 | yes | rc=4 line 4 | rc=4 line 4 | rc=4 line 4 | ok |
| DA1 | yes | rc=0 | rc=0 | rc=0 | **NOT MET** (pre-existing; V-03; D1) |
| DA2 | yes | rc=4 line 3 | rc=4 line 2 `heredoc <<2 pending` | the same as R4 | ok |
| DA3 | yes | rc=4 line 3 | rc=4 line 3 | rc=4 line 3 | ok |
| Y1, Y1b | yes | rc=0 | rc=4 w.yml line 10 | rc=4 w.yml line 10 | ok |
| Y2 | no | rc=4 line 8 | rc=0 | rc=0 | R3 refusal lost since R4; right (the value folds to `echo a . scripts/h.sh`) |
| Y2b, Y2c | yes | rc=4 line 9 | rc=4 line 8 | rc=4 line 7 (the value's first line) | ok (R5-4) |
| Y3 | yes | rc=0 | rc=4 line 6, twice | the same as R4 | ok |
| Y3b, Y4, Y4c | yes | Y4 rc=4 line 6; Y3b, Y4c rc=0 | rc=4 line 6 | rc=4 line 6 | ok |
| Y4b | yes | rc=0 | rc=4 line 7 | rc=4 line 7 | ok |
| Y4d (`Run:`) | no (PyYAML key `Run`) | rc=4 line 6 | rc=0 | rc=0 | R3 refusal lost since R4; NOT proven right (GitHub's reading of `Run:` not measured; V-18) |
| Y5 | yes | rc=4 line 7 | rc=4 line 7 | rc=4 line 7 | ok |
| Y5b | no | rc=4 line 6 | rc=4 line 6 | rc=4 line 6 | ok (fail-closed) |
| Y6 | no | rc=0 | rc=0 | rc=0 | ok |
| Y7, Y8, Y10, Y11, Y12, Y15 | yes | rc=4 | rc=4 (lines 8, 7, 13, 8, 8, 8) | the same as R4 | ok |
| Y7b | GitHub, inferred | rc=0 | rc=0 | rc=0 | **NOT MET, inferred** (V-07; D1) |
| Y7c | GitHub, inferred | rc=4 line 6 (the `env:` line) | rc=0 | rc=0 | **NOT MET, inferred**: R3's refusal, lost since R4 (V-07; D1) |
| Y9, Y9b, Y9c | python runs it | rc=0 | rc=0 | rc=0 | **NOT MET** (python, not bash; V-08; D1) |
| Y11b | YAML error | rc=4 line 7 | rc=4 `w.yml` (unparseable) | the same as R4 | ok |
| Y13, Y14 | yes | rc=0 | rc=4 line 7 | rc=4 line 6 | ok (R5-4) |
| R5-ansi-noescape | no | rc=4 line 3 | rc=0 | rc=0 | R3 refusal lost since R4; right (body text; the R5-1 control) |
| R5-mid-word `E$'\x4f'F` | yes | rc=0 | rc=0 | rc=4 line 2 escape | ok (fixed; R3 and R4 both missed it) |
| R5-k22, R5-hd22 | yes | rc=4 (lines 3, 25) | the same | the same | ok (R4: 27.57 s and 54.61 s, measured 13:47Z and 13:52Z) |
| R5-arith-in-sub, R5-sub-in-sub, R5-shift-in-sub | yes | rc=4 (lines 2, 2, 3) | the same | the same | ok |
| R5-plain-multiline | yes | rc=4 line 8 | rc=4 line 7 | rc=4 line 6 | ok (R5-4) |
| R5-guard-valid | yes | rc=4 line 5 | rc=4 line 5 | rc=4 line 2 `$(( re-read with other heredocs pending` | ok (still refused) |
| R5-guard-K1 | no (bash: syntax error) | rc=0 | rc=4 line 6 | rc=4 line 2 guard | ok |
| R5-quoted-open | no | rc=0 | rc=4 line 7 `quote " open` | rc=4 line 6 | ok (R5-4) |

Rule 1, "every R3 refusal stays a refusal in R5": lost on PQ6b, PQ7b, Y2 and R5-ansi-noescape, where bash does not run the
helper (R3's refusals were false). It is also lost on Y4d, where the right answer is not measured, and on Y7c. All six
changes are R4's, and R5 equals R4 on them.
Rule 2, "no R5 row exit 0 where bash runs an unlisted file": **not met** on TK1-TK5, CA5 and DA1 (bash). Also on Y9, Y9b and
Y9c if python counts, and on Y7b and Y7c on the inferred GitHub side. R5 changes none of these rows. See D1.

## Mutants (`/tmp/j10r5/tools/mutants.py`; scratch tree `/tmp/j10r5/mut/tree`; each written as a new inode, anchor asserted once, `py_compile`, `--collect-only`, then the whole file)

| id | mutation | collected | result | killed by |
|---|---|---|---|---|
| m1 | R5-1 reverted (the PIN's `heredoc()`) | 112 | 6 failed, 106 passed — KILLED | `…ansi_c_escape_is_refused[AQ1, AQ2, AQ3, AQ4, PQ5b, mid-word]` |
| m2 | memo removed (the PIN's `arith()`) | 112 | 4 failed, 108 passed — KILLED | `…scan_in_bounded_time[V-04, heredoc-per-level]`, `…revisit_it_cannot_prove[bash-valid, trusted-memo-reads-clean]` |
| m3 | R5-4 reverted (both lines counted) | 112 | 5 failed, 107 passed — KILLED | `…names_its_first_line[Y2b, Y2c, Y13, Y14]`, `test_quoted_run_that_ends_open_names_its_first_line` |
| m4 | R5-1 widened to every `$'` word | 112 | 1 failed, 111 passed — KILLED | `test_heredoc_word_in_ansi_c_quotes_without_an_escape_still_reads` |
| m5 | a success remembered, and a revisit jumps to its end | 112 | 1 failed, 111 passed — KILLED | `test_arithmetic_memo_keeps_every_decision[arith-in-subshell]` |
| m6 | the guard trusts the memo (returns False) | 112 | 2 failed, 110 passed — KILLED | `…revisit_it_cannot_prove[bash-valid, trusted-memo-reads-clean]` |
| m7 | key (start, pending), re-run per state (this lane's first draft) | 112 | 4 failed, 108 passed — KILLED | `…scan_in_bounded_time[V-04, heredoc-per-level]` (timeouts) + the two refusal rows |
| m8 | a literal block also mapped to its first line | 112 | 2 failed, 110 passed — KILLED | `test_literal_run_block_keeps_its_line_map`, `test_workflow_run_ending_inside_a_construct_names_its_yaml_line` |
| m9 | R5-1 narrowed to words that start with `$'` | 112 | 1 failed, 111 passed — KILLED | `…ansi_c_escape_is_refused[mid-word]` |
| m10 | sensitivity dropped (every failure holds under any heredocs) | 112 | 2 failed, 110 passed — KILLED | `…revisit_it_cannot_prove[bash-valid, trusted-memo-reads-clean]` |
| m11 | `read_bodies` counted only when it pops a heredoc | 112 | 2 failed, 110 passed — KILLED | the same two rows |
| m12 | R5-4 reverted for the unparseable line only | 112 | 1 failed, 111 passed — KILLED | `test_quoted_run_that_ends_open_names_its_first_line` |
| m13 | a success recorded as a failure (a revisit re-reads it as commands) | 112 | 1 failed, 111 passed — KILLED | `test_arithmetic_memo_keeps_every_decision[shift-in-subshell]` |
| N13 | the verifier's: `arith()` closes at any `)` at depth 0 | 112 | 3 failed, 109 passed — KILLED | `…keeps_every_decision[subshell-in-subshell]` + the two refusal rows |
| N19 | the verifier's: folded (`>`) mapped like plain | 112 | 2 failed, 110 passed — KILLED | `…names_its_first_line[Y2b, Y2c]` |

The unmutated screen was restored after every mutant (`unmutated screen restored: True`). AF-AP-138: the 20 distinct
killing tests, by node id, on the unmutated scratch tree (screen sha256[:16] `db28614c4bb72601` = the dev and final file):
`20 passed in 1.46s`; m13's killing test, `shift-in-subshell`, run the same way afterwards: `1 passed in 0.20s`. No survivor.

## Gates (pasted; shared tree, final files installed 13:45:25Z by write + rename, mode 644 kept)

```
$ date -u
Wed Sep 23 13:45:44 UTC 2026
$ /root/venv-agent-factory/bin/python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/j10r5/bt1
112 passed in 8.89s          rc=0
$ ... --basetemp=/tmp/j10r5/bt2
112 passed in 9.98s          rc=0
$ bash scripts/pc_suite.sh set-id -- tests/test_no_laya_in_gates.py
1 files set=e3695f80792b
# before (13:44:29Z, the PIN screen in the tree) — time python3 scripts/no_laya_in_gates.py [--staged], 3 runs each
no_laya_in_gates: 40 files scanned, clean real 0m0.445s / 0m0.398s / 0m0.379s
no_laya_in_gates: 40 files scanned, clean real 0m0.946s / 0m0.899s / 0m0.865s      (--staged)
# after (13:45:32Z, the R5 screen installed)
no_laya_in_gates: 40 files scanned, clean real 0m0.463s / 0m0.451s / 0m0.464s
no_laya_in_gates: 40 files scanned, clean real 0m0.841s / 0m0.917s / 0m0.835s      (--staged)
# the controlled comparison is the interleaved A/B under R5-2 (another lane was active on the box)
$ /root/venv-agent-factory/bin/python -m pyflakes scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py
pyflakes rc=0
$ python3 scripts/ap_screen.py scripts/no_laya_in_gates.py
--- AP_SCREEN over 1 path(s): 7 hits over 1 files ---
AF-AP-40: 7          (all in _glob_structural, lines 1262-1278; the PIN copy shows the same 7 at lines 1229-1245)
$ python3 scripts/ap_screen.py --tests tests/test_no_laya_in_gates.py
--- TEST_SCREEN over 1 path(s): 0 hits over 1 files ---      (PIN copy: 0)
$ pytest tests/test_shell_syntax.py -q -p no:cacheprovider --basetemp=/tmp/j10r5/btss1      (the adjacent hook fixture)
4 passed in 1.25s
```
The live-tree tests `test_live_tree_clean` and `test_live_tree_clean_staged` are in the 112; the scanned count is 40.

The real pre-commit hook in a throwaway repository (`/tmp/j10r5/hook/repo`): `git archive e37a052` of `scripts`,
`tests/test_no_laya_in_gates.py`, `tests/fixtures/decisions`, `.github`, `harness-ports/bin`, `.claude/hooks/edit-snapshot.py`
and `proofs` (850 files), plus the two final files; `git init`. The base commit ran under an empty hooks directory; then
`core.hooksPath` = `/tmp/j10r5/hook/hooks`, which holds only `pre-commit`, byte-equal to the repo's (`cmp` rc 0; D6).
```
=== COMMIT 1 (clean: a comment line appended to the listed scripts/pc_suite.sh)
lint_delta (index vs HEAD): 0 .py changed, 0 NEW pyflakes hit(s), 0 removed
no_laya_in_gates: 40 files scanned, clean
[master 9ec202f] j10r5 clean
commit rc=0; HEAD=9ec202f
=== COMMIT 2 (AQ1: a new LISTED gate, heredoc word $'echo \x41'; the UNLISTED helper carries the vocabulary)
lint_delta (index vs HEAD): 0 .py changed, 0 NEW pyflakes hit(s), 0 removed
gate-file-unparseable: scripts/j10r5-aq1.sh:2: heredoc <<$'echo \x41': $'...' escape not translated
COMMIT BLOCKED by the never-a-gate screen (rc=4)
commit rc=1; HEAD=9ec202f
--- bash runs the staged gate:
laya HELPER RAN in pid 13982
=== CONTROL (the PIN screen, sha256[:16] ab33c767c65c6f56, in the throwaway worktree; the same staged commit)
no_laya_in_gates: 41 files scanned, clean
[master 59f6df5] j10r5 AQ1 under the PIN screen
commit rc=0; HEAD=59f6df5
```
The control is V-01 reproduced through the real hook. The same staged commit is blocked by R5.

## Corrections to the J1-0-R4 report (R5-5; `tasks/briefs/laya/J1-0-R4-report.md` is not edited)

1. D4, `tasks/briefs/laya/J1-0-R4-report.md:118`: "`$[ … ]` arithmetic: its `<<` reads as a heredoc, which ends in an R4-1
   refusal". **False as stated.**
   - What is true: the `<<` inside `$[ … ]` registers a heredoc, and that heredoc ends at the first later line equal to its
     operand. When such a line exists, the scan re-syncs and reads CLEAN while bash runs the edge between.
   - Only without such a line does it end in an R4-1 refusal.
   - Fixtures: the verify report's DA1 (`tasks/briefs/laya/VERIFY-J1-0-R4-report.md:141`, `y=$[ 1 << true ]`, then H,
     then `true`: FAIL-OPEN) and DA2 (`tasks/briefs/laya/VERIFY-J1-0-R4-report.md:142`: `heredoc <<2 pending`).
   - Re-measured here: DA1 is rc 0 under R3, R4 and R5 while bash runs the helper; DA2 is refused by R4-1.
2. D4's heading, `tasks/briefs/laya/J1-0-R4-report.md:116` ("refusals that are safe but may be false"), with its item
   `tasks/briefs/laya/J1-0-R4-report.md:120` ("a workflow step with `shell: python`: its `run:` text is scanned as bash").
   **False as stated.**
   - What is true: scanning a Python step's text as bash is not a refusal when the Python text loads a file. The screen reads
     CLEAN while the step's Python process loads unlisted code. That is a fail-open, not a safe refusal.
   - Fixtures: the verify report's Y9 (`tasks/briefs/laya/VERIFY-J1-0-R4-report.md:243`, `exec(open('scripts/h.py').read())`),
     Y9b (`runpy.run_path`) and Y9c (`sys.path.insert` + `import helper`), rc 0 (V-08).
   - Re-measured here: all three are rc 0 under R3, R4 and R5, and `python3 -c` of each value runs the helper.
3. Self-attack 1, `tasks/briefs/laya/J1-0-R4-report.md:421`: "Its known exotic triggers refuse instead (D4)". **False as
   stated.** What is true: known triggers re-sync and read CLEAN.
   - DA1 (V-03), and `time` before `((`/`case` (TK1-TK5, CA5; V-02, `tasks/briefs/laya/VERIFY-J1-0-R4-report.md:134`).
   - The `$'…'` heredoc words AQ1-AQ4 and PQ5b (V-01, an R4 regression; AQ1 is `FAIL-OPEN` at `tasks/briefs/laya/VERIFY-J1-0-R4-report.md:129`).
   - R5-1 now refuses the `$'…'` class. The `$[` and `time` triggers still read CLEAN in R5 (the differential, D1).

## Issue #46 / #37 rows closed incidentally (with evidence)

- **V-13, survivor N13** ("arith(): any ')' at depth 0 closes, no subshell fallback"): KILLED by
  `test_arithmetic_memo_keeps_every_decision[subshell-in-subshell]` and by both rows of `…revisit_it_cannot_prove`
  (mutant N13 above). The fixture puts a source edge in a `$( ( … ) )` that begins `$((`.
- **V-13, survivor N19** ("folded (>) values mapped like plain ones"): KILLED by
  `test_folded_or_quoted_run_refusal_names_its_first_line[Y2b, Y2c]` (mutant N19 above).
- V-01's class member `E$'\x4f'F` (a `$'` part in the middle of a word). R3 AND R4 both read it CLEAN while bash runs the helper
  (differential row R5-mid-word); R5-1 refuses it. It is inside R5-1's contract, so it is not an issue row, but it was not in the report.
- Not closed (re-measured, unchanged): V-02 (TK, CA5), V-03 (DA1), V-07 (Y7b, Y7c), V-08 (Y9*), V-14 (PQ5a is still a false
  refusal, with a new message), V-16, V-17, and the other V-13 survivors. N1, N12, N16, N18, N20, N22, N23, N24 and N32 were
  not re-run.

## Self-attack — the three most likely ways this change is wrong

1. **R5-1 misses a spelling in which bash translates an escape.**
   - The predicate is literal: `$'` anywhere in the word, and a backslash anywhere in it (m9 shows the `anywhere` matters).
   - A continuation-split `$\`, newline, `'E\tF'` hides the `$'` from it. It is still refused by R4-1 in both R4 and R5, and
     bash does run the helper there, so the refusal is right (measured, § R5-1).
   - Double-quoted `"$'…'"` and escaped `\$'…'` are not ANSI-C in bash (its parse, measured). They are over-refused, fail-closed.
   - Residual: none found. Not every quoting combination was enumerated.
2. **The memo changes a verdict.**
   - The one piece of state an attempt reads is covered by the guard.
   - The live tree shows 0 segment differences in 27 texts and 2006 segments, in both modes.
   - The three decision fixtures pin R4's lines, and m5, m6, m10, m11 and m13 are killed.
   - This lane's first draft keyed the memo by (start, pending). It passed the V-04 series but was exponential on a
     bash-valid series (m7; k=16 1.18 s). That is why the heredoc-per-level row is a committed test.
   - Residual: the guard refuses some bash-valid texts R4 decided, all rc 4 in both screens in the sweep (D2).
3. **R5-4 names a line outside the value.**
   - Every style's first line is computed as before (for block scalars, the line after the indicator).
   - The value's first line is inside the value for Y2b, Y2c (7), Y13, Y14 (6), a plain multi-line value (6), and a plain value
     that starts on the line after `run:` (7, measured).
   - A literal block keeps its line-for-line map (m8 killed).

## report_lint (two fix rounds of the three allowed; pasted)

```
$ python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/J1-0-R5-report.md --root .
round 1: report_lint: 34 refs — OK 28, NEAR 1, MISS 3, UNCHECKABLE 2, UNRESOLVED 0 (worktree)      lint rc=1
round 2: report_lint: 34 refs — OK 34, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)      lint rc=0
```
Round 1's fixes: one reference per report line with its own backticked token, and the R5-3 range widened to 732.

## DISCREPANCIES

- **D1 — the differential's rule 2 conflicts with "do not fix it here". I followed "do not fix" and the standing rule
  "report adjacent defects, never fix them".**
  - R5 is exit 0 while the runtime runs an unlisted helper on:
    - TK1-TK5 and CA5 (V-02), and DA1 (V-03): bash, measured;
    - Y9, Y9b and Y9c (V-08): python, measured;
    - Y7b and Y7c (V-07): GitHub substitutes `${{ }}`; inferred, not run.
  - R4 gives the same verdict on every one of them, and so does R3 except Y7c, which R3 refused through its raw-line scan
    of the `env:` line.
  - Meeting rule 2 means fixing V-02, V-03, V-07 and V-08, which the brief assigns to issue #46.
  - **The gate is NOT met on these 10 measured and 2 inferred rows. I have not self-accepted this; the coordinator decides.**
- **D2 — a design addition in R5-2: a new refusal text, `$(( re-read with other heredocs pending` (also `(( …`), exit 4.**
  - The contract names the memo (once per start position). It does not say what to do when a stored failure may not hold.
  - Measured:
    - a memo keyed by (start, pending heredocs) re-runs per state and is exponential on a bash-valid text (m7; k=16
      1.18 s; the same series costs R4 54.61 s at k=22);
    - a start-only memo that trusts every failure reads a text CLEAN that R4 refused (`trusted-memo-reads-clean`,
      bash-invalid; m6, m10).
  - So a revisit the memo cannot prove is refused. A sweep of variants of the shape (`/tmp/j10r5/tools/guardsweep2.py`,
    installed screen) printed `variants: 95 bash-valid: 25 reach the guard: 4 of those refused by R4 (rc 4): 4`. So each of
    the 4 is refused by R4 too, only at another line.
  - A bash-valid text of that shape without a source edge (R4: clean) would be a NEW false refusal. It is fail-closed, and
    none is live (0 segment differences).
  - The existing error texts are unchanged; this one is added.
- **D3 — "linear" is met as "one decision per start", not as one scan per character.**
  - A character inside d failed `$((` attempts is scanned 1 + d times. So the k-series is quadratic in k.
  - d is bounded by the recursion guard: k=330 in 0.59 s; k=400 refused, `constructs nested too deep to scan`.
  - The contract's numbers are met: k=22 0.06 s against the 1 s bound; live tree +1.4 % against the 10 % bound.
- **D4 — shapes rebuilt, not replayed.**
  - The verify lane's `/tmp/vj10r4` instrument no longer exists. The AQ/PQ/TK/CA/DA/Y fixtures are rebuilt from the report's
    descriptions.
  - They match every R3/R4 verdict the report records. My CA1-CA4, CA6, CA7, TK5, TK6, Y7b, Y7c and Y11b texts may differ from
    the verifier's bytes.
  - Y7c's R3 verdict depends on my unquoted `env:` value.
- **D5 — 5 of the 20 new tests cannot be RED at the PIN.** The brief asks for fixtures showing that nothing changed: the
  `<<$'EOF'` control, the memo-decision rows and the literal-block case. Their negative controls are mutants m4, m5, m8, m13 and N13.
- **D6 — the hook gate's hooks directory holds only `pre-commit`**, byte-equal to the repo's, rather than `scripts/hooks` whole.
  The whole directory would run `post-commit` and start background reindexers outside this boundary (the J1-0-R4 report's
  side-effects section). The verify lane set it up the same way. The gate under test is pre-commit.
- **D7 — HEAD moved during the lane.**
  - 1e4c40a (13:17Z) is a brief-only commit, `tasks/briefs/s0-02-support/B10-brief.md`.
  - At 13:45Z another lane held uncommitted `proofs/S0-02/` edits in the tree. None of the edited files is listed: the two
    listed S0-02 files, `proofs/S0-02/check_buzz_authz.py` and `proofs/S0-02/oracle/denial_table.py`, show 0 modified.
  - The live screen read `40 files scanned, clean` in both modes after the install, and again at 13:55:39Z
    (`112 passed in 10.31s`, both modes rc 0).
  - After the push, HEAD is 774d764 (13:54:10Z, `docs/INCIDENT-LOG.md` + a verify report). 1e4c40a became 9b3bbdb on origin.
    774d764 landed after the install; if it went through this tree's hook, the R5 screen passed it in `--staged` mode
    (INFERRED; the commit path was not observed). HEAD's boundary blobs are still the PIN's (`ae8b2046e118`,
    `9790cb714afa`): this lane's files are uncommitted.
  - GitNexus `detect-changes --scope all` (13:5xZ) covers the whole dirty tree, other lanes included:
    `Changes: 23 files, 40 symbols`, `Affected processes: 5`, `Risk level: medium`. The five processes are all another lane's
    S0-02 `Build_bundle` flows. For this file it names `_Open`, `_unquote`, `_ShellScan`, `scan`, `arith`, `dq` and
    `read_bodies`. `scan` and `dq` are not changed here: the index predates the edit, and shifted lines map to old ranges.
- **D8 — a new cost finding, not fixed.** The `((` command form nested k deep (`(( ` × k, `x`, ` ) )` × k) is quadratic.
  - Each `((` start's attempt scans its whole body once; the memo does not help, because no start repeats.
  - Timings: R4 0.62 s at k=1000, 2.40 s at k=2000 (bash -n accepts; 14 KB); R5 0.64 s and 2.18 s; R3 0.05 s even at k=4000.
  - It is a V-04 sibling introduced by R4, but not the `$((` series R5-2 names. For issue #46.
- **D9 — an adjacent overclaim, reported, not fixed.** The docstring of `test_allowed_dynamic_loads_match_the_live_tree_exactly`
  says "covers exactly its count of loads". It counts load SITES, which is V-05's point. R5-3 names only the comment.

## NOT-done

- No commit, stage, push or bridge use (the brief). The two files are installed in the shared tree, uncommitted, for the coordinator.
- V-02, V-03, V-07 and V-08 are not fixed (D1). The `((` quadratic (D8) is not fixed. D9's docstring is not changed.
- GitHub Actions was not run: Y4d, Y7b and Y7c are inferred on the GitHub side.
- The verifier's other V-13 survivors were not re-run.
- No `/bug-echo` run and no registry row: `docs/INCIDENT-LOG.md` is outside the boundary. Candidate classes for the coordinator:
  - D2's trap: a memo whose key is finer than the decision re-opens the blow-up it was meant to close.
  - D8: a restore-and-rescan that stays quadratic when no start repeats.
  - V-01's mid-word sibling (`E$'\x4f'F`): an unquote that is wrong for one quoting form anywhere in the word, not only at its start.
- Scratch `/tmp/j10r5/` is removed at the end (the brief), instruments included. The fixture texts survive as the appendix;
  the timing and mutation drivers do not, and their outputs are pasted above.

## Appendix — the rebuilt fixture texts (verbatim from `/tmp/j10r5/tools/diff3.py`, which is removed with the scratch)

Each shell shape is `#!/bin/bash\n` + the text, saved as `scripts/g.sh` and listed. Each workflow shape is the whole
`.github/workflows/w.yml`, listed. The unlisted helper `scripts/h.sh` is `echo HELPER-RAN; : > "$MARK"`, and `scripts/h.py`
and `scripts/helper.py` write the same marker. The screens run with `--root <tree>`. The k-series and the
heredoc-per-level series are the `R5-k22` and `R5-hd22` rows with 22 replaced by k.
```python
H = ". scripts/h.sh"
TAB = "\t"
HEAD = "on: push\njobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n"
SHAPES = [
    # ---- § 2 AQ: a $'...' heredoc word with an ANSI-C escape (line 2 the operator, 5 the source, 6 R4's delimiter)
    ("AQ1", "sh", "cat <<$'echo \\x41' >/dev/null\nbody\necho A\n" + H + "\necho \\x41\n"),
    ("AQ2", "sh", "cat <<$'E\\x4fF' >/dev/null\nbody\nEOF\n" + H + "\nE\\x4fF\n"),
    ("AQ3", "sh", "cat <<$'E\\\\F' >/dev/null\nbody\nE\\F\n" + H + "\nE\\\\F\n"),
    ("AQ4", "sh", "cat <<$'E\\'F' >/dev/null\nbody\nE'F\n" + H + "\nE\\F\n"),
    ("AQ5", "sh", "cat <<$'\\tEOF' >/dev/null\nbody\n" + TAB + "EOF\n" + H + "\n"),
    # ---- § 2 PQ: quoted delimiters; $(H) in a quoted body is data, the H after is an edge
    ("PQ1", "sh", "cat <<E\"O\"F >/dev/null\n$(" + H + ")\nEOF\n" + H + "\n"),
    ("PQ2", "sh", "cat <<E\\OF >/dev/null\n$(" + H + ")\nEOF\n" + H + "\n"),
    ("PQ3", "sh", "cat <<\"E\"OF >/dev/null\n$(" + H + ")\nEOF\n" + H + "\n"),
    ("PQ4", "sh", "cat <<E''OF >/dev/null\n$(" + H + ")\nEOF\n" + H + "\n"),
    ("PQ5a", "sh", "cat <<$'E\\tF' >/dev/null\nbody\nE\\tF\n" + H + "\nE" + TAB + "F\n"),
    ("PQ5b", "sh", "cat <<$'E\\tF' >/dev/null\nbody\nE" + TAB + "F\n" + H + "\nE\\tF\n"),
    ("PQ6a", "sh", "cat <<$\"EOF\" >/dev/null\nbody\nEOF\n" + H + "\n"),
    ("PQ6b", "sh", "cat <<$\"EOF\" >/dev/null\n$EOF\n" + H + "\nEOF\n"),
    ("PQ7a", "sh", "cat <<$'EOF' >/dev/null\nbody\nEOF\n" + H + "\n"),
    ("PQ7b", "sh", "cat <<$'EOF' >/dev/null\n$EOF\n" + H + "\nEOF\n"),
    # ---- § 2 TK: `time` before (( or case
    ("TK1", "sh", "time (( x = 1 << true ))\n" + H + "\ntrue\n"),
    ("TK2", "sh", "time -p (( x = 1 << true ))\n" + H + "\ntrue\n"),
    ("TK3", "sh", "! time (( x = 1 << true ))\n" + H + "\ntrue\n"),
    ("TK4", "sh", "if time (( x = 1 << true )); then :; fi\n" + H + "\ntrue\n"),
    ("TK5", "sh", "r=\"$(time -p case a in a) echo \"it's\";; esac)\"; " + H + "; : \"'\"; # \"\n"),
    ("TK6", "sh", "r=\"$(time -p case a in a) echo \"its\";; esac)\"; " + H + "; : \"'\"; # \"\n"),
    ("TK7", "sh", "time (( x = 1 << 2 ))\n" + H + "\n"),
    # ---- § 2 CA: case patterns
    ("CA1", "sh", "case x in (a|\\)) : ;; esac\n" + H + "\n"),
    ("CA2", "sh", "case x in ')'|a) : ;; esac\n" + H + "\n"),
    ("CA3", "sh", "case x in [\\)]|a) : ;; esac\n" + H + "\n"),
    ("CA4", "sh", "r=\"$(case x in a) : ;; esac)\"\n" + H + "\n"),
    ("CA5", "sh", "r=\"$(time case a in a) echo \"it's\";; esac)\"; " + H + "; : \"'\"; # \"\n"),
    ("CA6", "sh", "case x in \"a)\") : ;; esac\n" + H + "\n"),
    ("CA7", "sh", "shopt -s extglob\ncase x in @(a|b)) : ;; esac\n" + H + "\n"),
    # ---- § 2 DA: $[ ... ] arithmetic
    ("DA1", "sh", "y=$[ 1 << true ]\n" + H + "\ntrue\n"),
    ("DA2", "sh", "y=$[ 1 << 2 ]\n" + H + "\n"),
    ("DA3", "sh", "y=\"$[ 1 << true ]\"\n" + H + "\ntrue\n"),
    # ---- § 4 Y: workflow shapes (line 6 = the first step)
    ("Y1", "wf", HEAD + "      - run: |\n          cat <<EOF\n          body\n          EOF\n          " + H + "\n"),
    ("Y1b", "wf", HEAD + "      - run: |\n          cat <<'EOF'\n          " + H + "\n          EOF\n          " + H + "\n"),
    ("Y2", "wf", HEAD + "      - run: >\n          echo a\n          " + H + "\n"),
    ("Y2b", "wf", HEAD + "      - run: >\n          echo a\n          echo b\n            " + H + "\n"),
    ("Y2c", "wf", HEAD + "      - run: >\n          echo a\n\n          " + H + "\n"),
    ("Y3", "wf", HEAD + "      - run: &r " + H + "\n      - run: *r\n"),
    ("Y3b", "wf", HEAD + "      - &s {run: " + H + "}\n      - *s\n"),
    ("Y4", "wf", HEAD + "      - \"run\": " + H + "\n"),
    ("Y4b", "wf", HEAD + "      - ? run\n        : " + H + "\n"),
    ("Y4c", "wf", HEAD + "      - !!str run: " + H + "\n"),
    ("Y4d", "wf", HEAD + "      - Run: " + H + "\n"),
    ("Y5", "wf", HEAD + "      - run: echo ok\n        run: " + H + "\n"),
    ("Y5b", "wf", HEAD + "      - run: " + H + "\n        run: echo ok\n"),
    ("Y6", "wf", "on: push\ndefaults:\n  run:\n    shell: bash\njobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n"
                 "      - run: echo ok\n"),
    ("Y7", "wf", "on: push\njobs:\n  a:\n    runs-on: ubuntu-latest\n    strategy:\n      matrix:\n        include:\n"
                 "          - run: " + H + "\n    steps:\n      - run: echo ok\n"),
    ("Y7b", "wf", "on: push\njobs:\n  a:\n    runs-on: ubuntu-latest\n    strategy:\n      matrix:\n"
                  "        cmd: ['" + H + "']\n    steps:\n      - run: ${{ matrix.cmd }}\n"),
    ("Y7c", "wf", "on: push\njobs:\n  a:\n    runs-on: ubuntu-latest\n    env:\n      CMD: " + H + "\n    steps:\n"
                  "      - run: ${{ env.CMD }}\n"),
    ("Y8", "wf", HEAD + "      - shell: bash {0}\n        run: " + H + "\n"),
    ("Y9", "wf", HEAD + "      - shell: python\n        run: exec(open('scripts/h.py').read())\n"),
    ("Y9b", "wf", HEAD + "      - shell: python\n        run: |\n          import runpy\n          runpy.run_path(\"scripts/h.py\")\n"),
    ("Y9c", "wf", HEAD + "      - shell: python\n        run: |\n          import sys; sys.path.insert(0, 'scripts')\n"
                  "          import helper\n"),
    ("Y10", "wf", HEAD + "      - run: echo ok\n---\n" + HEAD.replace("  a:", "  b:") + "      - run: " + H + "\n"),
    ("Y11", "wf", HEAD + "      - run: |\n          echo a\n          " + TAB + H + "\n"),
    ("Y11b", "wf", HEAD + "      - run: echo ok\n" + TAB + "- run: " + H + "\n"),
    ("Y12", "wf", HEAD + "      - run: |2\n          echo a\n          " + H + "\n"),
    ("Y13", "wf", HEAD + "      - run: \"echo a\\n" + H + "\"\n      - run: echo ok\n"),
    ("Y14", "wf", HEAD + "      - run: 'echo a\n\n          " + H + "'\n"),
    ("Y15", "wf", HEAD + "      - uses: actions/github-script@v7\n        with:\n          run: " + H + "\n"),
    # ---- the fixtures J1-0-R5 adds that are not one of the shapes above
    ("R5-ansi-noescape", "sh", "cat <<$'EOF' >/dev/null\n" + H + "\nEOF\necho done\n"),
    ("R5-k22", "sh", "v=" + "$(( " * 22 + "x" + " ) )" * 22 + "\n" + H + "\n"),
    ("R5-arith-in-sub", "sh", "v=$(( $(( $(" + H + ") + 1 )) ) )\n"),
    ("R5-sub-in-sub", "sh", "v=$(( $(( " + H + " ) ) ) )\n"),
    ("R5-shift-in-sub", "sh", "v=$(( $(( 1 << 2 )) ) )\n" + H + "\n"),
    ("R5-plain-multiline", "wf", HEAD + "      - run: echo a\n\n          " + H + "\n      - run: echo ok\n"),
    ("R5-mid-word", "sh", "cat <<E$'\\x4f'F >/dev/null\nbody\nEOF\n" + H + "\nE\\x4fF\n"),
    ("R5-hd22", "sh", "v=" + "".join("$(( <<W%d " % j for j in range(22)) + "x" + " ) )" * 22 + "\n"
                      + "".join("W%d\n" % j for j in range(22)) + H + "\n"),
    ("R5-guard-valid", "sh", "x=$(( <<A $(( $(:\nA\n) ) ) ) )\n" + H + "\n"),
    ("R5-guard-K1", "sh", "x=$(( <<A $(( $(:\n) ) ))\nA\n) <<B )) ) )\n" + H + "\nB\n"),
    ("R5-quoted-open", "wf", HEAD + '      - run: "echo a\\necho \\"open"\n      - run: echo ok\n'),
]
```
