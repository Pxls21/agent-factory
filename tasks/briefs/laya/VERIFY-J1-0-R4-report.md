# VERIFY-J1-0-R4 — independent adversarial verify of the never-a-gate screen, round 4 (task #184)

Lane verify-j1-0-r4 · sandbox · agent `adversarial-verifier` (claude-opus-5-5) · shared tree, no worktree · brief
`tasks/briefs/laya/VERIFY-J1-0-R4-brief.md`. PIN 0e7b6c3 (post-push SHA of local 5090671); origin head 11195d9.
Component: `scripts/no_laya_in_gates.py` (S), `scripts/gate_files.txt` (L), `tests/test_no_laya_in_gates.py` (T).
Contract: AMENDMENT 3 (R4-1..R4-6, `tasks/briefs/laya/J1-0-R4-brief.md`) on AMENDMENT 2 (`tasks/briefs/laya/J1-0-R3-brief.md`),
graded against (B) of `tasks/briefs/laya/VERIFY-J1-0-R23-STAMP-report.md`. The builder's report
`tasks/briefs/laya/J1-0-R4-report.md` is an input to attack. Honey `full`. Evidence tiers: SOLID (reproduced here, pasted),
UNSURE (inferred or partial).

**TL;DR — `MERGE-READY-WITH-FOLLOWUPS` (the coordinator owns the gate).** Everything the frozen acceptance names is met
and reproduced (gates 92 passed twice, set e3695f80792b; both modes clean; bash's own parse agrees on the live tree; all 6
throwaway-repo hook commits behaved as graded). New findings are follow-ups; the top three:
- [ ] V-01: an R4 REGRESSION. A `$'…'` heredoc delimiter holding an escape hides a later source edge; it landed through the
      real hook, and R3 refused the same text.
- [ ] V-04: EXPONENTIAL scan time, introduced by R4 (`arith()`): a 192-byte line takes 27.6 s.
- [ ] V-05: `ALLOWED_DYNAMIC_LOADS` trusts any unknown base, and counts sites, not loads. Re-pointed through the real hook, the
      hook's own `lint_delta` ran a foreign file; the comment at `scripts/no_laya_in_gates.py:697-698` (`re-pointed at another file`) says this cannot happen.
- [x] No live gate holds any fail-open shape found here (grep + bash's own parse, both modes).
- [ ] Under a literal reading of the brief's materiality clauses, V-01, V-05 and V-06 would block (see the GATE line).

## 1 — PREMISE (re-measured)

```
$ date -u; git rev-parse HEAD; git rev-parse origin/claude/soundbox-kit-migration-iz1jwf
Wed Sep 23 11:41:45 UTC 2026
11195d9ec292b8ee220c7319ea53a2ad3a35d634
11195d9ec292b8ee220c7319ea53a2ad3a35d634
$ git log --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf -8 | cut -c1-110   (the PIN row)
0e7b6c3 J1-0-R4 landed (task #172; GATED-PENDING-VERIFY): the never-a-gate screen scans to the end of each text,
$ git diff --stat 0e7b6c3 11195d9 -- <S> <L> <T> scripts/hooks/pre-commit ; echo rc
rc=0                      (empty: the boundary and the hook are unchanged after the PIN)
$ blob[:12] lines path (at 0e7b6c3) + the worktree blob
ae8b2046e118 1419 scripts/no_laya_in_gates.py      worktree=ae8b2046e118
9790cb714afa 1097 tests/test_no_laya_in_gates.py   worktree=9790cb714afa
8eaccfa87a98 53 scripts/gate_files.txt             worktree=8eaccfa87a98
7731a91c7d3e 133 scripts/hooks/pre-commit          worktree=7731a91c7d3e
1f16b01f1923 162 scripts/lint_delta.py             worktree=1f16b01f1923
eb20dde7e198 96 scripts/ap_screen.py               worktree=eb20dde7e198
```
```
$ grep -n "^def \|^class \|^ALLOWED_DYNAMIC_LOADS\|^EXTERNAL_MODULES" scripts/no_laya_in_gates.py  vs the brief's block
LINE MAP IDENTICAL (34 rows)
$ sed -n 699,703p scripts/no_laya_in_gates.py   -> the three ALLOWED_DYNAMIC_LOADS entries, each x1 (same as the brief)
$ grep -c . scripts/gate_files.txt; grep -v "^#" scripts/gate_files.txt | grep -c .
53
40
$ grep -n "no_laya_in_gates" scripts/hooks/pre-commit
127:"$PY" "$REPO_ROOT/scripts/no_laya_in_gates.py" --staged
$ /root/venv-agent-factory/bin/python -c "import yaml; print(yaml.__version__)"; python3 -c ...; bash --version | head -1
6.0.3
system python3 yaml 6.0.1
GNU bash, version 5.2.21(1)-release (x86_64-pc-linux-gnu)
$ git diff --cached --stat            (the shared index: empty, it equals HEAD 11195d9, whose list names the hook)
$ python3 scripts/no_laya_in_gates.py (x3) ; python3 scripts/no_laya_in_gates.py --staged (x3)   [shared tree, read-only]
no_laya_in_gates: 40 files scanned, clean   rc=0 wall=.388 / .385 / .387 s
no_laya_in_gates: 40 files scanned, clean   staged rc=0 wall=.841 / .845 / .823 s
$ git archive 0e7b6c3 -- scripts tests/test_no_laya_in_gates.py tests/fixtures/decisions .github harness-ports/bin \
    .claude/hooks/edit-snapshot.py proofs | tar -x -C /tmp/vj10r4/pin ; sha256[:16] of S, L, T there
ab33c767c65c6f56  scripts/no_laya_in_gates.py     (= the builder's parked sha, J1-0-R4-report § LANDING)
abb01939f762fb62  scripts/gate_files.txt          (=)
5c6218f1bfab20bd  tests/test_no_laya_in_gates.py  (=)
```
Premise verdict: SOLID, no mismatch. Every item below stands on the measured premise; no item is CONTRACT-INVALID by premise.

## 11 — GATES (run early, on the shared tree, read-only; PYTHONDONTWRITEBYTECODE=1)

```
$ date -u
Wed Sep 23 11:46:30 UTC 2026
$ /root/venv-agent-factory/bin/python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/vj10r4/bt1
92 passed in 7.92s          pytest rc=0
$ ... --basetemp=/tmp/vj10r4/bt2
92 passed in 7.52s          pytest rc=0
$ bash scripts/pc_suite.sh set-id -- tests/test_no_laya_in_gates.py
1 files set=e3695f80792b
$ /root/venv-agent-factory/bin/python -m pyflakes scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py
pyflakes rc=0
```
Both modes of the screen on the shared tree: in § 1 above (`40 files scanned, clean`, rc 0, twice three runs).

## 2 — R4-2, the shell lexer, against bash itself (NEW shapes; oracle ≠ the builder's `bash -n` + probe)

Instrument (`/tmp/vj10r4/lex/lex.py`, removed at the end): one throwaway tree per shape; `scripts/g.sh` = `#!/bin/bash` + the
shape, listed; `scripts/h.sh` = `echo HELPER-RAN; : > "$MARK"`, unlisted. Oracle 1: bash RUNS the fixture (timeout 10 s) and the
marker says whether the helper ran. Oracle 2: `bash -x` xtrace shows a `.`/`source` of `scripts/h.sh` executing. Screen: the PIN
screen `/tmp/vj10r4/pin/scripts/no_laya_in_gates.py --root <tree>`. A third bash instrument, bash's own parse printed by
`declare -f` of a never-called function wrapping the text, re-derives the mechanism below. `H` = the line `. scripts/h.sh`.

Batch 1 (pasted, columns trimmed; `bash_ran`/`xtrace` = oracles 1/2):
```
C0     bash_ran=True  xtrace=True  screen_rc=4   agree(caught)   gate-file-sources: scripts/g.sh:2: scripts/h.sh
HS1    bash_ran=True  xtrace=True  screen_rc=4   agree(caught)   gate-file-sources: scripts/g.sh:3: scripts/h.sh     cat <<<EOF; H; EOF=1
HS2-HS6 (<<< "it's", <<<'a'"b'c", <<<x <<EOF, "$(cat <<<"it's")", <<<$(echo "a)"))            all agree(caught) at H's line
TH1    bash_ran=True  xtrace=True  screen_rc=4   agree(caught)   gate-file-sources: scripts/g.sh:7: scripts/h.sh     cat <<A <<'B'
TH2    bash_ran=True  xtrace=True  screen_rc=4   agree(caught)   gate-file-sources: scripts/g.sh:7: scripts/h.sh     bodies B / A crossed
TH3    bash_ran=False xtrace=False screen_rc=0   agree(clean)                                                        <<'A' <<B, $(H) in A
TH4    bash_ran=True  xtrace=True  screen_rc=4   agree(caught)   gate-file-sources: scripts/g.sh:3: scripts/h.sh     <<A <<'B', $(H) in both
PQ1-PQ4 (<<E"O"F, <<E\OF, <<"E"OF, <<E''OF; $(H) in the body, H after)                          all agree(caught) at H's line only
PQ5a   bash_ran=False xtrace=False screen_rc=4   FALSE-REFUSAL?  gate-file-sources: scripts/g.sh:5: scripts/h.sh     <<$'E\tF'
PQ5b   bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN                                                           <<$'E\tF'
       bash-stderr: scripts/g.sh: line 6: EtF: command not found
PQ6a/PQ7a ($"EOF", $'EOF'; EOF then H)  agree(caught) · PQ6b/PQ7b ($EOF then H then EOF)  agree(clean)
TB1-TB4 (<<- with tab bodies, a space-then-tab line, three tabs, a quoted 'E F' word)            all agree
HC1    bash_ran=True  xtrace=True  screen_rc=4   agree(caught)   gate-file-sources: scripts/g.sh:6: scripts/h.sh     "$(cat <<EOF ... )"
HC2, HC3, HC5, HC6                                                                                 all agree(caught)
HC4    bash_ran=True  xtrace=True  screen_rc=4   caught-by-R4-1  gate-file-unparseable: scripts/g.sh:2: heredoc <<EOF pending
       bash-stderr: scripts/g.sh: line 4: warning: here-document at line 2 delimited by end-of-file (wanted `EOF')
PS1-PS4 (> >(H), ">(H)" quoted, tee >(cat), "$(cat <(echo "it's"))")                            all agree
LS1-LS3 ($"it's", $"a $(echo "b") c", "a$")                                                       all agree(caught)
PB1-PB9 (${x//\}/a}, "${x//'}'/a}", "${x//"}"/a}", ${x//[}]/a}, "${x:-'}", ...)                  all agree
PB10   bash_ran=False xtrace=False screen_rc=4   refused(R4-1)   gate-file-unparseable: scripts/g.sh:2: ${ unclosed  (bash: unexpected EOF too)
CA1-CA4, CA6, CA7 (a|\)), ')'|a), [\)]|a), in "$( )", "a)", extglob @(a|b))                     all agree(caught)
CA5    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       r="$(time case a in a) echo "it's";; esac)"; H; : "'"; # "
CP1    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       coproc . scripts/h.sh
CP2, CP3 (coproc NAME { H; }, coproc ( H ))                                                       agree(caught)
FN1-FN4 (function f { H; }, f() ( H ), function f ( H ), f() { H \n})                           all agree(caught)
EV1    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       eval ". scripts/h.sh"      (F-B3 S22, KNOWN)
EV2    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       eval '. scripts/h.sh'      (F-B3 S22, KNOWN)
SP1    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       command . x                (F-B3 S03, KNOWN)
SP2    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       builtin source x           (F-B3 S02, KNOWN)
SP3    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       \. x                       (F-B3 S30, KNOWN)
SP4    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       '.' x                      (F-B3 S32, KNOWN)
SP5    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       alias s=. on an earlier line (F-B3 S08, KNOWN)
SP6    bash_ran=True  xtrace=False screen_rc=4   agree(caught)   gate-file-sources: scripts/g.sh:2: /dev/fd/3   exec 3< x; . /dev/fd/3
```
Batch 2 — the siblings of the two new mechanisms, and false-refusal probes (pasted):
```
AQ1    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       cat <<$'echo \x41'; body; echo A; H; echo \x41   (no bash error at all)
AQ2    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       <<$'E\x4fF'
AQ3    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       <<$'E\\F'
AQ4    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       <<$'E\'F'
AQ5    bash_ran=True  xtrace=True  screen_rc=4   caught-by-R4-1  gate-file-unparseable: scripts/g.sh:2: heredoc <<\tEOF pending
TK1    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       time (( x = 1 << true )); H; true                 (only time's output on stderr)
TK2    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       time -p (( ... ))
TK3    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       ! time (( ... ))
TK4    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       if time (( ... )); then :; fi
TK5    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       "$(time -p case a in a) echo "it's";; esac)"
TK6    bash_ran=True  xtrace=True  screen_rc=4   agree(caught)   the same without an apostrophe: re-syncs at once
TK7    bash_ran=True  xtrace=True  screen_rc=4   caught-by-R4-1  gate-file-unparseable: scripts/g.sh:2: heredoc <<2 pending   (no re-sync line)
DA1    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       y=$[ 1 << true ]; H; true
DA2    bash_ran=True  xtrace=True  screen_rc=4   caught-by-R4-1  gate-file-unparseable: scripts/g.sh:2: heredoc <<2 pending
DA3    bash_ran=True  xtrace=True  screen_rc=4   agree(caught)   "$[ 1 << true ]" (quoted)
CQ1    bash_ran=True  xtrace=True  screen_rc=0   FAIL-OPEN       coproc source scripts/h.sh
FR1    bash_ran=False xtrace=False screen_rc=4   FALSE-REFUSAL?  echo { . scripts/h.sh }
FR2    bash_ran=False xtrace=False screen_rc=4   FALSE-REFUSAL?  a=( . scripts/h.sh )
FR3    bash_ran=False xtrace=False screen_rc=4   FALSE-REFUSAL?  a=( newline . scripts/h.sh newline )
FR4    bash_ran=False xtrace=False screen_rc=4   FALSE-REFUSAL?  echo } . scripts/h.sh
FR5    bash_ran=False xtrace=False screen_rc=0   agree(clean)    [[ x == ( . ) ]]   (a bash syntax error)
FR6    bash_ran=False xtrace=False screen_rc=4   (by design)     if false; then H; fi        (a static screen refuses an unreached edge)
FR7    bash_ran=False xtrace=False screen_rc=4   (by design)     f() { H; } never called
HD1    bash_ran=False xtrace=False screen_rc=4   refused(R4-1)   "$(cat <<EOF / body / EOF)" — bash: a warning, then runs on
EN1    bash_ran=True  xtrace=True  screen_rc=4   agree(caught)   cat \ newline <<EOF
EN2    bash_ran=True  xtrace=True  screen_rc=4   caught-by-R4-1  <<E\ newline OF: bash's delimiter is EOF; the screen's is E<newline>OF
```
Mechanism, from both sides (SOLID). bash's parse (`declare -f`) prints AQ1's heredoc as `cat <<'echo A'` and every fixture's `H`
as its own command. The screen's own `_command_segments` on the same texts (PIN module, `opened=None` in all four = no R4-1):
```
=== AQ1  opened=None     seg line 2: raw="cat <<$'echo \\x41' >/dev/null"          (lines 3-6 read as the heredoc body)
=== TK1  opened=None     seg line 2: 'time' · 'x = 1 << true' · '2>/dev/null'       (( read as two subshells, << true = a heredoc)
=== DA1  opened=None     seg line 2: raw='y=$[ 1 << true ]'                         ($[ not modelled, << true = a heredoc)
=== CA5  opened=None     seg line 2: 'time case a in a' · then one masked segment spanning lines 2-3
_unquote("$'echo \\x41'") -> 'echo \\x41'
_LEADING_KEYWORDS = ['!', 'do', 'elif', 'else', 'if', 'then', 'until', 'while']
```
- AQ: `_unquote` (`scripts/no_laya_in_gates.py:126`) drops the `$` of `$'…'` but keeps the escapes literal. bash translates them.
  So the screen's delimiter (`echo \x41`) is not bash's (`echo A`); the body runs past bash's end; a later line equal to the
  screen's delimiter re-syncs it.
- TK: `commands()` reads `((` as arithmetic only when every earlier word is in `_LEADING_KEYWORDS` or is `for`
  (`_LEADING_KEYWORDS`, `scripts/no_laya_in_gates.py:251`); the case tracker uses the same test (`at_command`, `scripts/no_laya_in_gates.py:190`).
  `time` (and `time -p`) is missing. So `<< true` is a heredoc (TK1-TK4), and a case pattern's `)` closes the `$(` (TK5, CA5).
- DA: `$[ … ]` is not modelled (the builder's D4 names it). Its `<<` is a heredoc that ends at a later line equal to the operand,
  so D4's "which ends in an R4-1 refusal" is false as stated: DA1 is CLEAN, DA2 alone ends in R4-1.
- Every one of these needs a later line equal to the phantom delimiter (`true`, `echo \x41`), or a crafted quote re-sync (CA5,
  TK5). Without it, R4-1 refuses (TK7, DA2): the backstop works when the scan ends open, and is blind when it ends closed.

Live tree (measured): `grep -nE` over the 12 listed shell/workflow gates for `time (( | time case | coproc | $[ | <<$' | { . | =( .`
finds nothing. bash's own parse of every listed shell text and every workflow `run:` value (`/tmp/vj10r4/canon3.py`, `declare
-f`, never executed) finds exactly 2 source commands, both `ALLOWED_SOURCES` pairs, in the worktree AND the index:
```
SOURCE commands bash parsed: 2
  SRC scripts/pc_lane.sh -> "$ROOT/.pc-bridge.env";    [[ -f "$ROOT/.pc-bridge.env" ] && . "$ROOT/.pc-bridge.env";]
  SRC scripts/pc_lane.sh -> "$PC_LANE_BRIDGE_FN";    [[ -z "${PC_LANE_BRIDGE_FN:-}" ] || . "$PC_LANE_BRIDGE_FN";]
INDEX == WORKTREE
```
So no live gate holds a desync shape or a hidden source edge today (SOLID, two instruments), and no false-refusal shape above is
live (the live screen reads clean in both modes, § 1).

## 3 — R4-1, the end-state backstop (NEW unfinished constructs, not the builder's eight)

`/tmp/vj10r4/r41/r41.py`: each text is `#!/bin/bash`, `echo ok`, then the shape on line 3; `want` = the start line a refusal must
name, or None when the text closes. `bash -n` is the reference. Pasted:
```
U1   bash-n rc=2  screen rc=4  want=3    OK   gate-file-unparseable: scripts/g.sh:3: quote $' open        echo $'it\'s  (escaped last quote)
U2   bash-n rc=0  screen rc=4  want=None OK   gate-file-sources: scripts/g.sh:4: scripts/h.sh           $'a\\' closes
U3   bash-n rc=2  screen rc=4  want=3    OK   gate-file-unparseable: scripts/g.sh:3: quote $' open        $'a\\\'b
U4   bash-n rc=0  screen rc=4  want=3    OK   gate-file-unparseable: scripts/g.sh:3: heredoc <<EOF pending  delimiter line "EOF  "
U5   bash-n rc=0  screen rc=4  want=3    OK   gate-file-unparseable: scripts/g.sh:3: heredoc <<EOF pending  "EOF " then H
U6   bash-n rc=0  screen rc=0  want=None OK                                                            "echo a \" at EOF, no newline
U7   bash-n rc=0  screen rc=0  want=None OK                                                            backslash-newline, then EOF
U8   bash-n rc=0  screen rc=4  want=None OK   gate-file-sources: scripts/g.sh:4: scripts/h.sh           x=$(( 1 + 2 ) ) closes
U9   bash-n rc=0  screen rc=4  want=None OK   gate-file-sources: scripts/g.sh:3: scripts/h.sh           "$(( . scripts/h.sh ) )": caught
U10  bash-n rc=2  screen rc=4  want=3    OK   gate-file-unparseable: scripts/g.sh:3: ` unclosed           $(echo `date)
U11  bash-n rc=2  screen rc=4  want=3    OK   gate-file-unparseable: scripts/g.sh:3: $( unclosed          $(echo `date) `
U12  bash-n rc=0  screen rc=4  want=None OK   gate-file-sources: scripts/g.sh:5: scripts/h.sh           ')' inside a # comment in $( )
U13  bash-n rc=2  screen rc=4  want=3    OK   gate-file-unparseable: scripts/g.sh:3: quote " open         $"abc
U14  bash-n rc=2  screen rc=4  want=3    OK   gate-file-unparseable: scripts/g.sh:3: heredoc << without a delimiter
U15  bash-n rc=2  screen rc=4  want=3    OK   gate-file-unparseable: scripts/g.sh:3: ${ unclosed          "${x:-a
```
15 of 15 OK (SOLID): each refusal names its start line; each text bash closes is scanned to its end (U2, U8, U9, U12 catch
the `H` after the construct). U4/U5 are refusals of text bash accepts with a warning: fail-closed, by R4-1's letter.

Live tree (measured with the PIN module's `_command_segments` over every listed shell text and every workflow `run:` value):
```
worktree: 27 shell texts scanned (files + workflow run: values), 2006 segments, 0 ending open
index: 27 shell texts scanned (files + workflow run: values), 2006 segments, 0 ending open
```
No live gate text ends in a state R4-1 refuses, in either mode (SOLID).

## 4 — R4-3, the workflow parse (NEW YAML shapes)

`/tmp/vj10r4/yml/yml.py`: one tree per shape, `.github/workflows/w.yml` listed; `real-line(s)` = the YAML line(s) holding the
command text; `safe_load runs` = PyYAML's constructed `run:` values (what a YAML consumer gets). Pasted:
```
Y1    rc=4 real-line(s)=[10]  screen: gate-file-sources: .github/workflows/w.yml:10: scripts/h.sh     run: | with a heredoc, H after
Y1b   rc=4 real-line(s)=[8, 10]  screen: gate-file-sources: .github/workflows/w.yml:10: scripts/h.sh  H in a <<'EOF' body = data
Y2    rc=0 real-line(s)=[8]  screen:                                        run: > folds to 'echo a . scripts/h.sh\n' (right)
Y2b   rc=4 real-line(s)=[9]  screen: gate-file-sources: .github/workflows/w.yml:8: scripts/h.sh      folded, more-indented line
Y2c   rc=4 real-line(s)=[9]  screen: gate-file-sources: .github/workflows/w.yml:8: scripts/h.sh      folded, blank line
Y3    rc=4 real-line(s)=[6]  screen: gate-file-sources: .github/workflows/w.yml:6: scripts/h.sh ; (the same line twice)  &r / *r
Y3b   rc=4 real-line(s)=[6]  screen: gate-file-sources: .github/workflows/w.yml:6: scripts/h.sh      a whole step aliased
Y4    rc=4 real-line(s)=[6]  screen: gate-file-sources: .github/workflows/w.yml:6: scripts/h.sh      "run": quoted key
Y4b   rc=4 real-line(s)=[7]  screen: gate-file-sources: .github/workflows/w.yml:7: scripts/h.sh      ? run / : value
Y4c   rc=4 real-line(s)=[6]  screen: gate-file-sources: .github/workflows/w.yml:6: scripts/h.sh      !!str run:
Y4d   rc=0 real-line(s)=[6]  screen:                                        Run: (capital) — safe_load runs=[]
Y5    rc=4 real-line(s)=[7]  screen: gate-file-sources: .github/workflows/w.yml:7: scripts/h.sh      duplicate run:, H second; safe_load keeps H
Y5b   rc=4 real-line(s)=[6]  screen: gate-file-sources: .github/workflows/w.yml:6: scripts/h.sh      duplicate run:, H first; safe_load keeps 'echo ok'
Y6    rc=0 real-line(s)=[]  screen:                                         defaults: run: shell/working-directory (a mapping)
Y7    rc=4 real-line(s)=[8]  screen: gate-file-sources: .github/workflows/w.yml:8: scripts/h.sh      matrix include: key named run
Y7b   rc=0 real-line(s)=[7, 9]  screen:                                     run: ${{ matrix.cmd }}, matrix.cmd = ['. scripts/h.sh']
Y7c   rc=0 real-line(s)=[6, 8]  screen:                                     run: ${{ env.CMD }}, env CMD = . scripts/h.sh
Y8    rc=4 real-line(s)=[7]  screen: gate-file-sources: .github/workflows/w.yml:7: scripts/h.sh      shell: bash {0}
Y9    rc=0 real-line(s)=[7]  screen:                                        shell: python, run: exec(open('scripts/h.py').read())
Y9b   rc=0 real-line(s)=[9]  screen:                                        shell: python, runpy.run_path("scripts/h.py")
Y9c   rc=0 real-line(s)=[9]  screen:                                        shell: python, sys.path.insert(0,'scripts'); import helper
Y10   rc=4 real-line(s)=[13]  screen: gate-file-sources: .github/workflows/w.yml:13: scripts/h.sh     multi-document file, 2nd doc
Y11   rc=4 real-line(s)=[8]  screen: gate-file-sources: .github/workflows/w.yml:8: scripts/h.sh      a tab inside a literal block
Y11b  rc=4 real-line(s)=[]  screen: gate-file-unparseable: .github/workflows/w.yml                  a tab as indentation (ScannerError)
Y12   rc=4 real-line(s)=[8]  screen: gate-file-sources: .github/workflows/w.yml:8: scripts/h.sh      run: |2
Y13   rc=4 real-line(s)=[6]  screen: gate-file-sources: .github/workflows/w.yml:7: scripts/h.sh      "echo a\n. scripts/h.sh" (7 = the NEXT step)
Y14   rc=4 real-line(s)=[8]  screen: gate-file-sources: .github/workflows/w.yml:7: scripts/h.sh      a single-quoted value over 3 lines
Y15   rc=4 real-line(s)=[8]  screen: gate-file-sources: .github/workflows/w.yml:8: scripts/h.sh      an action input named run (conservative)
```
Reading (SOLID for the screen's side; the GitHub side is INFERRED from its documented model, not run here):
- The screen scans the parsed (folded) value, which is what a YAML consumer and GitHub run: Y2 is CLEAN and right.
- Wrong refusal lines: Y2b, Y2c (folded), Y13 (double-quoted, names the next step's line), Y14 (single-quoted). `_workflow_runs`
  (`scripts/no_laya_in_gates.py:492`) adds 2 for `>` and 1 for a quoted value, then the scanner counts the VALUE's newlines, which
  a folded or quoted scalar does not keep line for line. The docstring (`scripts/no_laya_in_gates.py:473`) says "any other style
  maps to the line the value starts on"; the code does not do that either. The refusal still fires in all four.
- Duplicate keys (Y5, Y5b): both values are scanned whatever the order, so the result is safe whichever value GitHub keeps.
- `${{ … }}` (Y7b, Y7c): GitHub substitutes expressions into the `run:` text before the shell parses it (its documented model,
  the root of "script injection"), so the step's shell runs `. scripts/h.sh`; the screen reads CLEAN. Not covered by R4-3's text.
- `shell: python` (Y9, Y9b, Y9c): the step's process is Python running the listed text, which loads `scripts/h.py` / imports
  `scripts/helper.py` into itself; the screen scans the text as bash and reads CLEAN. The builder's D4 lists this shape under
  "refusals that are safe but may be false (fail-closed …)": false as stated for any Python text that loads a file.
- Capital `Run:` (Y4d) is not scanned; whether GitHub accepts `Run:` as `run:` is NOT measured here (UNSURE).
- Live workflows (measured with `yaml.compose_all`): `run:` styles `{'None': 1}` (planning-checks) and `{'None': 12, "'|'": 4}`
  (stage0-ci); no `shell:` key; no `${{` in any `run:` value. None of Y2b/Y2c/Y7b/Y7c/Y9*/Y13/Y14 is live.

## 5 — R4-4, dynamic loads (NEW shapes, not the builder's 37) and the exception set

Instrument (`/tmp/vj10r4/dyn/dyn.py`): per shape, a tree with the LISTED gate `proofs/x/check_y.py` and the LISTED
`proofs/x/listed.py`; UNLISTED look-alikes at `proofs/x/helper.py`, `harness-ports/bin/helper.py`, `harness-ports/bin/listed.py`,
`sub/proofs/x/listed.py`. Each file writes a marker named after its own path when its code runs. Runtime oracle: `python3
proofs/x/check_y.py` from the tree root (Python 3.11.15, the hook's interpreter). `ran=` lists the files whose code ran. Pasted:
```
P1    screen_rc=0 FAIL-OPEN                ran=['harness-ports/bin/listed.py']      sys.path.insert(0,'harness-ports/bin'); import listed
P2    screen_rc=4 refused(right)           ran=['proofs/x/helper.py']               sys.path.append(...); import helper
P2b   screen_rc=4 refused(right)           ran=['harness-ports/bin/onlyhp.py']      (gate-file-import-unresolved)
P3    screen_rc=0 FAIL-OPEN                ran=['harness-ports/bin/listed.py']      sys.path.insert + importlib.import_module('listed')
P4    screen_rc=4 refused(right)           ran=['proofs/x/helper.py']               getattr(importlib, 'util').spec_from_file_location
P5    screen_rc=0 FAIL-OPEN                ran=['proofs/x/helper.py']               getattr(importlib.util, 'spec_from_file_location')(...)
P6    screen_rc=0 FAIL-OPEN                ran=['proofs/x/helper.py']               vars(builtins)['exec'](open(...).read())
P6b   screen_rc=0 FAIL-OPEN                ran=['proofs/x/helper.py']               __builtins__.exec(open(...).read())
P6c   screen_rc=0 FAIL-OPEN                ran=['proofs/x/helper.py']               import builtins as b; b.exec(open(...).read())
P7    screen_rc=4 refused(right)           ran=['proofs/x/helper.py']               types.ModuleType + exec(code, mod.__dict__)
P8    screen_rc=0 FAIL-OPEN                ran=['proofs/x/helper.py']               pkgutil.resolve_name('helper:X')
P11   screen_rc=0 FAIL-OPEN                ran=['proofs/x/helper.py']               importlib.util.find_spec('helper') + exec_module
P11b  screen_rc=0 clean(right)             ran=['proofs/x/listed.py']               the same for 'listed'
P12   screen_rc=4 refused(right)           ran=['proofs/x/helper.py']               ldr = SourceFileLoader(...); ldr.load_module()
P12b  screen_rc=4 refused(no unlisted run) ran=['proofs/x/listed.py']               L = SourceFileLoader; L(.., listed).load_module()
P13-P17  screen_rc=4 refused(right)        class body · default argument · decorator · comprehension (x2) · match guard
P18-P21  screen_rc=4 refused(right)        os.sep.join · str.format · % · "".join  (each gate-file-import-unresolved)
P22   screen_rc=4 refused(right)           ran=['harness-ports/bin/listed.py']      __file__ = '...'; dirname(__file__)/listed.py
P23   screen_rc=0 FAIL-OPEN                ran=['harness-ports/bin/listed.py']      sys.modules[__name__].__file__ = '...'
P24   screen_rc=0 FAIL-OPEN                ran=['harness-ports/bin/listed.py']      globals()['__file__'] = '...'
P25   screen_rc=4 refused(no unlisted run) ran=[]                                   if TYPE_CHECKING: run_path(...)
P26   screen_rc=4 refused(no unlisted run) ran=[]                                   if False: run_path(...)
P27   screen_rc=0 FAIL-OPEN                ran=['sub/proofs/x/listed.py']           os.chdir('sub'); runpy.run_path('proofs/x/listed.py')
P28   screen_rc=0 FAIL-OPEN                ran=['proofs/x/helper.py']               imp.load_source('h', 'proofs/x/helper.py')
P29   screen_rc=0 FAIL-OPEN                ran=['harness-ports/bin/helper.py']      site.addsitedir + a .pth line that execs a file
P32, P36, P38  clean(right)                exec of the listed file · import_module('listed') · import_module('os.path')
P39   screen_rc=4 refused(right)           ran=['proofs/x/yaml.py']                 import_module('yaml') with a repo yaml.py beside it
P40   screen_rc=0 FAIL-OPEN                ran=['harness-ports/bin/json.py']        sys.path.insert + import_module('json')
```
Grading each CLEAN (SOLID: the runtime marker, not an argument):
- Declared in the docstring (`scripts/no_laya_in_gates.py:33-35`, "Also not followed"): P5 (a loader reached through getattr),
  P6 and P24 (the `globals()` family), and, under "other ways to run code in the process", P8, P11, P28, P29.
- KNOWN (issue #37, F-B4: the import rule ignores `sys.path`): P40 exactly; P1 and P3 are NEW members: an unlisted file SHADOWS a
  LISTED module name, so the screen proves the listed file while Python loads the other. R4-4 defines a module-name load as
  "exactly like AMENDMENT 2's static imports", so P3 inherits F-B4 by the contract's own text.
- NOT declared: P6b/P6c (`exec` reached as `__builtins__.exec` or through an aliased `builtins`; `_loader_name` accepts an
  attribute `exec` only on the literal name `builtins`, `scripts/no_laya_in_gates.py:1014-1015`); P27 (a relative literal is
  resolved against the repo root, `_as_path`, `scripts/no_laya_in_gates.py:720`, while an `os.chdir` moves the process);
  P23 (`__file__` re-pointed through the module object).
- Refusals of loads that never run or reach a listed file (P12b, P25, P26): fail-closed; no live instance (the live screen is clean).
- Live gates (grep over the 28 listed Python gates for `os.chdir`, `TYPE_CHECKING`, `__builtins__`, `find_spec`, `resolve_name`,
  `addsitedir`, `import builtins`): no match. None of the CLEAN shapes is live.

The exception set (`/tmp/vj10r4/exc/exc.py`): a tree holding the REAL `scripts/lint_delta.py` (variants below) and a listed
`.claude/hooks/edit-snapshot.py`; "exactness" = the logic of `test_allowed_dynamic_loads_match_the_live_tree_exactly`
(`_load_sites` + the count of sites whose values hold `("under", tail)`), applied to each variant. Pasted:
```
E0 live lint_delta.py (control)                            runtime screen rc=0 no_laya_in_gates: 2 files scanned, clean
                                                           live-tree exactness test logic: sites covering the tail=[106] -> PASS
E1a same site, base re-pointed to an env value             runtime screen rc=0 no_laya_in_gates: 2 files scanned, clean
                                                           live-tree exactness test logic: sites covering the tail=[106] -> PASS
E1b a wrapper: ONE site, a second call with another base   runtime screen rc=0 no_laya_in_gates: 2 files scanned, clean
                                                           live-tree exactness test logic: sites covering the tail=[103] -> PASS
E1c a second DIRECT site with the same tail (count control) runtime screen rc=4 gate-file-import-unresolved: scripts/lint_delta.py line 102 ; … line 109
                                                           live-tree exactness test logic: sites covering the tail=[102, 109] -> FAIL (2 != 1)
E1d(i) REMOVE the live load, ADD one with another base     runtime screen rc=0 no_laya_in_gates: 2 files scanned, clean
                                                           live-tree exactness test logic: sites covering the tail=[106] -> PASS
E1d(ii) REMOVE the live load, ADD one with another tail    runtime screen rc=4 gate-file-import-unresolved: scripts/lint_delta.py:106   `spec_from_file_location`
                                                           live-tree exactness test logic: sites covering the tail=[] -> FAIL (0 != 1)
E1d(iii) REMOVE the live load only                         runtime screen rc=0 no_laya_in_gates: 2 files scanned, clean
                                                           live-tree exactness test logic: sites covering the tail=[] -> FAIL (0 != 1)
```
- Re-pointing: YES, through the base (E1a, E1d(i)). The key is (gate, literal tail) under an UNKNOWN base, so any unknown base
  satisfies it. The comment at `scripts/no_laya_in_gates.py:697-698` says "so an entry cannot be re-pointed at another file (the
  F-B5 class)": false as stated. The builder's report declares the same residual ("each entry trusts that the unknown base is the
  repo root, by review", Self-attack 3), so it is known to the builder but mis-stated in S.
- A second, new load under one entry: YES, through a wrapper (E1b): `_load_errors` counts site INDEXES
  (`uses.setdefault`, `scripts/no_laya_in_gates.py:1112`), so one site that a wrapper calls twice counts once.
  D3's "at most" (runtime) and "exactly" (test) both hold per SITE; neither bounds the number of loads.
- The commit that removes a live load and adds a different one: with the same tail and another base, both the runtime screen and
  the exactness test stay green (E1d(i)); with another tail, the runtime screen refuses the new load (E1d(ii)). Removing a load
  alone reads clean at commit time; only the exactness test, which the hook does not run (it runs the screen, not pytest), goes
  red (E1d(iii)). Through the real hook: § 8.

## 6 — the seven live sites, by an independent AST walk

My walk (a wider net than `_LOADERS`: `spec_from_file_location`, `SourceFileLoader`, `SourcelessFileLoader`, `ExtensionFileLoader`,
`run_path`, `run_module`, `import_module`, `__import__`, `exec`, `eval`, `compile`, `exec_module`, `load_module`, `find_spec`,
`module_from_spec`, `load_source`, `resolve_name`, `addsitedir`, `zipimporter`, `reload`, as a Name or an attribute) over the 28
listed Python gates at the worktree (= the PIN for every file but `proofs/S0-05/check_egress.py`, whose worktree diff vs 0e7b6c3
is a 2-line docstring change by another lane):
```
listed Python gates: 28
my AST census: 115 calls in 19 files       (108 of them are re.compile(...) — not a loader; the screen rightly skips them)
  AST proofs/S0-02/check_buzz_authz.py:80 spec_from_file_location(path)        + :83 module_from_spec, :84 exec_module
  AST proofs/S0-03/check_omniroute_roundtrip.py:114 spec_from_file_location(_S0_01_CHECKER)   + :117, :123
  AST proofs/S0-05/check_egress.py:122 spec_from_file_location(_PINS_FILE)    + :125, :128
  AST scripts/ap_screen.py:26 spec_from_file_location(ROOT / ".claude" / "hooks" / "edit-snapshot.py")   + :27, :28
  AST scripts/ledger-gen:17 SourceFileLoader(str(path))                        + :21, :22
  AST scripts/lint_delta.py:106 spec_from_file_location(hook)                  + :107, :109
  AST scripts/proof-runner:39 SourceFileLoader(str(path))                      + :43, :44
--- the screen's _load_sites on the same files:
  SCREEN scripts/ap_screen.py:26 kind=path values=["('at', '.claude/hooks/edit-snapshot.py')"]   `spec_from_file_location`
  SCREEN scripts/lint_delta.py:106 kind=path values=["('under', '.claude/hooks/edit-snapshot.py')"]   `spec_from_file_location`
  SCREEN scripts/proof-runner:39 kind=path values=["('at', 'scripts/validate-ledger')", "('under', 'scripts/validate-ledger')"]   `SourceFileLoader`
  SCREEN scripts/ledger-gen:17 kind=path values=["('at', 'scripts/validate-ledger')", "('under', 'scripts/validate-ledger')"]   `SourceFileLoader`
  SCREEN proofs/S0-02/check_buzz_authz.py:80 kind=path values=["('at', 'proofs/S0-01/check_acp_conformance.py')", "('at', 'proofs/S0-01/tools/nostr_verify.py')"]   `spec_from_file_location`
  SCREEN proofs/S0-03/check_omniroute_roundtrip.py:114 kind=path values=["('at', 'proofs/S0-01/check_acp_conformance.py')"]   `spec_from_file_location`
  SCREEN proofs/S0-05/check_egress.py:122 kind=path values=["('at', 'proofs/S0-01/pins.py')"]   `spec_from_file_location`
screen sites: 7
```
Same 7 sites (SOLID; no `import_module`, `__import__`, `run_path`, builtin `exec`/`eval`/`compile`, `find_spec`, `load_source`
or `reload` in any listed Python gate). Resolution per site, read from primary source:
- `scripts/ap_screen.py:26`: `ROOT = Path(__file__).resolve().parents[1]` (`scripts/ap_screen.py:22`) → the repo's
  `.claude/hooks/edit-snapshot.py`, listed. Right.
- `proofs/S0-02/check_buzz_authz.py:80` (`spec_from_file_location` in `_load_by_path`, called at :91 and :92 with `S0_01_CHECKER` and `NOSTR_VERIFY`,
  `proofs/S0-02/check_buzz_authz.py:40-41`, both `ROOT / "proofs" / "S0-01" / …` with `ROOT = HERE.parent.parent`). Right.
- `proofs/S0-03/check_omniroute_roundtrip.py:114`: `_S0_01_CHECKER = HERE.parent / "S0-01" / "check_acp_conformance.py"` (:104). Right.
- `proofs/S0-05/check_egress.py:122`: `_PINS_FILE = Path(__file__).resolve().parents[1] / "S0-01" / "pins.py"` (:114). Right.
- `scripts/proof-runner:39` and `scripts/ledger-gen:17` (`SourceFileLoader`): `path = root / "scripts" / "validate-ledger"`, falling back to
  `Path(__file__).resolve().with_name("validate-ledger")` when absent; `root` is the `--root` argument resolved
  (`scripts/proof-runner:279-282`, `scripts/ledger-gen:62-66`). The two values the screen lists are exactly those two branches.
  Right, under the declared assumption that `--root` is the repo (CI: `python scripts/ledger-gen --root .`).
- `scripts/lint_delta.py:106` loads `hook`, built at `scripts/lint_delta.py:103` from `REPO`.
  `REPO` is git's top level of the CWD (`scripts/lint_delta.py:35`). Soundness of (file, target) x1 when the root is not this checkout:
  - a git worktree or a throwaway clone: REPO is that checkout's top level, and its own hook screens its own copy. Sound, except
    that the hook's `--staged` screen reads the INDEX copy while `lint_delta` loads the DISK copy (the F-A3 index/worktree class,
    KNOWN, "by design per J1-0-R1");
  - a plain copy with no `.git`: `git rev-parse` fails at import, so nothing is loaded;
  - `lint_delta.py` run with its CWD inside ANOTHER repository: REPO is that repository, whose `.claude/hooks/edit-snapshot.py`
    this screen never saw. The key cannot tell, because the base is unknown by construction (§ 5, E1a). The hook path always
    runs it from the committing repo's root, so this needs a manual invocation. INFO.

## 7 — R4-5 and R4-6

R4-5 (SOLID): `.claude/hooks/edit-snapshot.py` is listed (`scripts/gate_files.txt:53`); it is byte-unchanged since the PIN
(`git diff --stat 0e7b6c3 -- .claude/hooks/edit-snapshot.py` empty; last commit 2d10a2c, 02:56Z, before the PIN); nothing under
`.claude/` was modified by the component commit (`git diff --stat 5090671^ 5090671`, measured here: 4 files changed, none under `.claude/`).
```
$ (PIN module) _check_line over every line of .claude/hooks/edit-snapshot.py
.claude/hooks/edit-snapshot.py: 477 lines, vocabulary hits under _check_line: 0
```
and the whole-screen result with it listed is `40 files scanned, clean` in both modes (§ 1).

R4-6, the docstring's exec-edge numbers (`scripts/no_laya_in_gates.py:30-33`), two instruments of mine:
1. bash's OWN parse (`/tmp/vj10r4/canon3.py`: each listed shell text and each workflow `run:` value wrapped in a never-called
   function and printed back by `declare -f`; single-quoted text masked; a command counts when its command word is `bash`, `sh`,
   `python`, `python3`, `"$PY"` or `node` after a command-position token and its first path argument, `$VAR/` prefixes removed,
   is a tracked file). Worktree and index identical:
   ```
   EXEC edges (interpreter + tracked repo file): 17
   distinct targets: 15 ; unlisted: 9
   UNLISTED SET IDENTICAL: 9 names   (diff against the docstring's/builder's list: hermes-session-export.py, sync-lane-skills.sh,
   sync-skills.sh, run-all.sh, test_context_mirrors.sh, fubuki_pin_sync.sh, no_laya_in_gates.py, pc_bridge_exec.py, transcript_export.py)
   ```
   A first draft of my matcher missed the `if python3 scripts/transcript_export.py` edge (`scripts/push_clean.sh:118`, no `if`
   in my prefix set) and a second over-masked; the numbers above are the corrected third run.
2. A loose text grep (interpreter, optional `$VAR/` prefix, a path; kept when it names a tracked file):
   ```
   edges (text occurrences naming a tracked file): 30
   distinct targets: 22
   unlisted: 13: harness-ports/bin/hermes-session-export.py harness-ports/bin/qwen-server.sh harness-ports/bin/sync-lane-skills.sh
   harness-ports/bin/sync-skills.sh harness-ports/tests/run-all.sh harness-ports/tests/test_context_mirrors.sh scripts/fubuki_pin_sync.sh
   scripts/lane_context.sh scripts/no_laya_in_gates.py scripts/pc_bridge_exec.py scripts/realleg_sync.sh scripts/ripwire_review.sh
   scripts/transcript_export.py
   ```
Both figures in the docstring reproduce exactly (SOLID for 17/15/9 by an instrument independent of the scanner; the grep is
independent of the scanner but similar in design to the builder's). F-B11 is closed as claimed. R4-6's "the same limit" sentence
is gone; the paragraph states that dynamic loads are followed and exec edges are the declared limit (`scripts/no_laya_in_gates.py:21-33`).

### Pre-existing or introduced by R4? (the R3 screen = `git show 5090671^:scripts/no_laya_in_gates.py`, same trees)
```
PQ5b  R3: rc=4 gate-file-sources: scripts/g.sh:5: scripts/h.sh      R4: rc=0 clean
AQ1   R3: rc=4 gate-file-sources: scripts/g.sh:5: scripts/h.sh      R4: rc=0 clean
AQ2   R3: rc=4 gate-file-sources: scripts/g.sh:5: scripts/h.sh      R4: rc=0 clean
AQ3   R3: rc=4 gate-file-sources: scripts/g.sh:5: scripts/h.sh      R4: rc=0 clean
AQ4   R3: rc=4 gate-file-sources: scripts/g.sh:5: scripts/h.sh      R4: rc=0 clean
CA5, TK1-TK5, DA1, CP1, CQ1                                         R3: rc=0 clean   R4: rc=0 clean   (pre-existing)
P1, P3, P6b, P6c, P11, P23, P27; Y7b, Y9                            R3: rc=0 clean   R4: rc=0 clean   (pre-existing)
FR1-FR4, FA1 (below), PQ5a                                          refused by both  (pre-existing false refusals)
HC4   R3: rc=4 gate-file-sources: scripts/g.sh:5: scripts/h.sh      R4: rc=4 gate-file-unparseable: scripts/g.sh:2: heredoc <<EOF pending
HD1   R3: rc=0 clean                                                R4: rc=4 gate-file-unparseable: scripts/g.sh:2: heredoc <<EOF pending
EN2   R3: rc=0 clean                                                R4: rc=4 gate-file-unparseable: scripts/g.sh:2: heredoc <<E…
P12b  R3: rc=0 clean                                                R4: rc=4 gate-file-import-unresolved: proofs/x/check_y.py:2
P25   R3: rc=0 clean                                                R4: rc=4 gate-file-import-unlisted: proofs/x/check_y.py:4 loads proofs/x/helper…
Y13   R3: rc=0 clean                                                R4: rc=4 gate-file-sources: .github/workflows/w.yml:7: scripts/h.sh
Y2b   R3: rc=4 gate-file-sources: .github/workflows/w.yml:9: …      R4: rc=4 gate-file-sources: .github/workflows/w.yml:8: …
```
- The AQ class (a `$'…'` heredoc delimiter holding an ANSI-C escape) is a REGRESSION introduced by R4: R3 did not register
  `<<$'…'` as a heredoc at all, so it scanned the `H` line and refused it; R4 registers it with the un-translated word and masks
  `H`. R3's refusal was an accident of mis-parsing (it would read any `<<$'EOF'` body as code), but on these inputs R4 turns a
  refusal into CLEAN.
- New R4 refusals of text bash accepts (HD1, EN2, P12b, P25): fail-closed side effects of R4-1/R4-4; none is live.
- Y2b (folded): R3 happened to name line 9 (the right one); R4 names line 8.
- FA1, a natural shape (`FIND_ARGS=( . -maxdepth 1 -name g.sh )` then `find "${FIND_ARGS[@]}"`), is refused by both screens
  (`gate-file-sources: scripts/g.sh:2: -maxdepth 1 -name g.sh`) while bash runs it cleanly: an array element `.` reads as a source
  command. Pre-existing (the `(` split, the verifier's F-B6 m10 area); not live.

## 8 — the real hook, a throwaway repository (`/tmp/vj10r4/hook/repo`)

Set-up (pasted): the repo = the PIN subset of § 1 (`git archive 0e7b6c3 -- scripts tests/... .github harness-ports/bin
.claude/hooks/edit-snapshot.py proofs`, 851 files, screen/list sha256 `ab33c767c65c6f56`/`abb01939f762fb62`); the base commit made
with `core.hooksPath` = an EMPTY directory; then `core.hooksPath` = `/tmp/vj10r4/hook/hooks`, holding ONLY `pre-commit`, byte-equal
to `git show 0e7b6c3:scripts/hooks/pre-commit` (`cmp` rc 0). No post-commit hook ran; no index or project outside `/tmp/vj10r4` was
touched. `$PY` = `/root/venv-agent-factory/bin/python` (the hook's default).
```
=== COMMIT 1 (clean change: a comment line appended to the listed scripts/pc_suite.sh)
lint_delta (index vs HEAD): 0 .py changed, 0 NEW pyflakes hit(s), 0 removed
no_laya_in_gates: 40 files scanned, clean
[master 032b286] vj10r4 clean
commit rc=0; HEAD=032b286

=== COMMIT 2 (AQ1: a new LISTED gate whose heredoc delimiter is $'echo \x41'; UNLISTED helper carries the vocabulary)
#!/bin/bash
cat <<$'echo \x41' >/dev/null
body
echo A
. scripts/h.sh
echo \x41
lint_delta (index vs HEAD): 0 .py changed, 0 NEW pyflakes hit(s), 0 removed
no_laya_in_gates: 41 files scanned, clean
[master 504d8a1] vj10r4 AQ1
commit rc=0; HEAD=504d8a1
--- bash runs the committed gate:
laya HELPER RAN in pid 25508 (…sourced, so the gate itself)
x41
gate rc=0

=== COMMIT 3 (TK1: time (( x = 1 << true )), then the source, then 'true'; appended to the listed gate)
no_laya_in_gates: 41 files scanned, clean
[master 5a335be] vj10r4 TK1
commit rc=0; HEAD=5a335be
--- bash runs the committed gate:  (the helper line printed twice: once per source edge)

=== COMMIT 4 (ALLOWED_DYNAMIC_LOADS re-pointed: lint_delta.py:103's base becomes an env value; the tail is unchanged)
-    hook = REPO / ".claude" / "hooks" / "edit-snapshot.py"
+    hook = Path(os.environ.get("AF_HOOK_ROOT", REPO)) / ".claude" / "hooks" / "edit-snapshot.py"
lint_delta (index vs HEAD): 1 .py changed, 0 NEW pyflakes hit(s), 0 removed
laya FOREIGN EDIT-SNAPSHOT RAN in pid 25768: /root/venv-agent-factory/bin/python /tmp/vj10r4/hook/repo/scripts/lint_delta.py --staged
no_laya_in_gates: 41 files scanned, clean
[master 24ae8f3] vj10r4 E1a
commit rc=0; HEAD=24ae8f3        (committed with AF_HOOK_ROOT=/tmp/vj10r4/hook/evil, a directory outside the repo)

=== COMMIT 5 (the strongest false refusal: a find-argument array whose first element is '.')
lint_delta (index vs HEAD): 0 .py changed, 0 NEW pyflakes hit(s), 0 removed
gate-file-sources: scripts/hooks/vj-fr.sh:2: -maxdepth 1 -name vj-fr.sh
COMMIT BLOCKED by the never-a-gate screen (rc=4)
commit rc=1; HEAD=24ae8f3
--- bash runs the refused gate:
gate rc=0
```
Reading (SOLID, real hook, real commits):
- The strongest fail-open is AQ1, because it is an R4 regression (§ 2): the committed listed gate sources an unlisted helper
  that carries the vocabulary, the hook's screen reads `41 files scanned, clean`, and bash runs the helper in the gate's shell.
- Commit 4 answers item 5's commit question through the real hook: the commit re-points the one allowed dynamic load, and in the
  same commit the hook's OWN `lint_delta` process (pid 25768) loads and runs a foreign `edit-snapshot.py` that carries the
  vocabulary; the screen reads clean. This is F-B2's ES reproduction, re-opened through the exception entry (§ 5, E1a).
- Commit 5 is refused by text bash runs cleanly; it predates R4 (the R3 screen refuses it too) and is not live.

## 9 — cost on pathological inputs (the real screen, `--root`, one listed file; wall clock, 4 busy cores)

The brief's four shapes, each at three sizes (`/tmp/vj10r4/cost/cost.py`; pasted):
```
nested $( "$( … )" ) lines, depth 3              1.25 MB     1.30 s  rc=0  no_laya_in_gates: 1 files scanned, clean
nested $( "$( … )" ) lines, depth 3              2.50 MB     2.52 s  rc=0
nested $( "$( … )" ) lines, depth 3              5.00 MB     5.07 s  rc=0
12500 heredocs (one per line)                    0.30 MB     0.33 s  rc=0
25000 heredocs (one per line)                    0.60 MB     0.57 s  rc=0
50000 heredocs (one per line)                    1.20 MB     1.05 s  rc=0
a 0.5 MB single line (echo a a a …)              0.50 MB     0.67 s  rc=0
a 1.0 MB single line (echo a a a …)              1.00 MB     1.19 s  rc=0
a 2.0 MB single line (echo a a a …)              2.00 MB     2.39 s  rc=0
YAML with 2500 steps                             0.12 MB     0.43 s  rc=0
YAML with 5000 steps                             0.23 MB     0.92 s  rc=0
YAML with 10000 steps                            0.46 MB     2.00 s  rc=0
```
All four are linear (double the input, about double the time). SOLID.

Shapes aimed at the new code's own algorithms (`cost2.py`, `cost3.py`; pasted):
```
$(( nested 10 deep, each closed by ') )' (bash -n rc=0, 0.00s)     0.06 s  rc=0
$(( nested 12 deep …                                               0.09 s  rc=0
$(( nested 14 deep …                                               0.17 s  rc=0
$(( nested 16 deep …                                               0.47 s  rc=0
$(( nested 18 deep (160 bytes; bash -n rc=0 in 0.003s)             1.76 s  rc=0
$(( nested 20 deep (176 bytes; bash -n rc=0 in 0.003s)             7.01 s  rc=0
$(( nested 22 deep (192 bytes; bash -n rc=0 in 0.002s)            27.62 s  rc=0  no_laya_in_gates: 1 files scanned, clean
R3 (5090671^) on the 22-deep line: 0.04 s rc=0
5000 / 10000 / 20000 heredoc operators on ONE line                 0.10 / 0.15 / 0.27 s   (linear)
'! ' x 5000 then true (bash -n rc=0)                               0.40 s
'! ' x 10000 / 20000 then true (bash -n rc=2: bash refuses them)   1.33 / 5.91 s          (quadratic)
one line nested $(echo " x 150 (bash -n rc=0)                      0.06 s  rc=0
one line nested $(echo " x 400 (bash -n rc=0)                      0.07 s  rc=4  gate-file-unparseable: scripts/g.sh:1: constructs nested too deep to scan
Python gate: a loader + a 3000-term sum                            0.06 s  rc=1  RecursionError: maximum recursion depth exceeded during ast construction
python3 runs a 3000-term sum itself: rc=1 RecursionError: maximum recursion depth exceeded during compilation
```
- EXPONENTIAL, introduced by R4 (SOLID): `v=$(( $(( … x ) ) … ) )` nested k deep, each level closed by `) )` (a command
  substitution holding a subshell, which bash parses at once). The time multiplies by about 4 every two levels. `arith()`
  (`def arith`, `scripts/no_laya_in_gates.py:332-354`) scans the whole body, fails at the closing pair, restores, and `dollar()` then re-scans the
  same body as commands (`scripts/no_laya_in_gates.py:317-321`). Each inner level is scanned twice per outer attempt, so the cost
  is 2^k. A 192-byte line costs 27.6 s (R3: 0.04 s); by extrapolation ~224 bytes cost minutes and ~256 bytes hours. The hook
  runs the screen on every commit, so one such line in any listed gate would stall every commit. Not live (the live screen runs
  in 0.39 s, § 1).
- Quadratic in a run of leading keywords (`at_command`, `scripts/no_laya_in_gates.py:190`, and the `((` test at :251 re-check
  every earlier word): 0.40 s at the largest run bash accepts. Minor.
- Nesting past about 150-400 levels is refused as "constructs nested too deep to scan" while bash accepts it: fail-closed, by
  design (`scripts/no_laya_in_gates.py:465-466`).
- A Python gate whose `ast.parse` raises RecursionError exits 1 with a traceback, not `gate-file-unparseable` (exit 4):
  `_import_errors` has only `except SyntaxError` (`scripts/no_laya_in_gates.py:629-632`, present at R3). Python itself cannot compile
  that file, and the hook still blocks (rc 1), so only the exit code and message differ. INFO.

## 10 — MUTANTS (new; not the builder's m1-m25)

Driver `/tmp/vj10r4/mut/mutants.py`: per mutant, `cp -al` of the PIN copy, the mutated file written as a NEW inode (write +
rename), exact-once anchor (count asserted 1), `py_compile`, `pytest --collect-only` (92 collected, every mutant), then the full
file. Pasted (12:20:37Z-12:24:28Z):
```
N1   R4-1 collected=92  92 passed in 7.17s           SURVIVED    _command_segments: RecursionError -> opened = None
N2   R4-1 collected=92  1 failed, 91 passed in 7.24s KILLED by test_scan_ending_inside_a_construct_fails_closed[backtick]
N3   R4-1 collected=92  92 passed in 7.36s           SURVIVED    heredoc(): no delimiter word -> return, no refusal
N4   R4-1 collected=92  92 passed in 7.46s           SURVIVED    no_heredoc_pending names heredocs[-1] instead of [0]
N5   R4-1 collected=92  1 failed, 91 passed in 7.43s KILLED by test_scan_ending_inside_a_construct_fails_closed[heredoc]
N6   R4-2 collected=92  1 failed, 91 passed in 7.55s KILLED by test_shell_member_trigger_is_caught[S18]
N7   R4-2 collected=92  92 passed in 7.84s           SURVIVED    a backslash no longer marks a heredoc word quoted
N8   R4-2 collected=92  92 passed in 8.02s           SURVIVED    <<- strips all leading whitespace, not only tabs
N9   R4-2 collected=92  1 failed, 91 passed in 7.78s KILLED by test_shell_member_trigger_is_caught[S34]
N10  R4-2 collected=92  2 failed, 90 passed in 7.99s KILLED by test_live_tree_clean, test_live_tree_clean_staged
N11  R4-2 collected=92  92 passed in 7.96s           SURVIVED    backticks drop every backslash
N12  R4-2 collected=92  92 passed in 7.94s           SURVIVED    '!' removed from _LEADING_KEYWORDS
N13  R4-2 collected=92  92 passed in 7.96s           SURVIVED    arith(): any ')' at depth 0 closes, no subshell fallback
N16  R4-3 collected=92  92 passed in 7.98s           SURVIVED    a quoted "run": key is skipped
N17  R4-3 collected=92  1 failed, 91 passed in 7.82s KILLED by test_unparseable_workflow_refused
N18  R4-3 collected=92  92 passed in 7.67s           SURVIVED    PyYAML missing -> [] (no runs) instead of unparseable
N19  R4-3 collected=92  92 passed in 7.88s           SURVIVED    folded (>) values mapped like plain ones
N20  R4-3 collected=92  92 passed in 7.78s           SURVIVED    only .yml is parsed; a listed .yaml is one shell text again
N22  R4-4 collected=92  92 passed in 7.62s           SURVIVED    builtins.exec is not a loader
N23  R4-4 collected=92  92 passed in 8.21s           SURVIVED    an ambiguous import_module name takes the first candidate
N24  R4-4 collected=92  92 passed in 8.51s           SURVIVED    for/with/walrus/augmented targets no longer rebind a name
N25  R4-4 collected=92  92 passed in 7.98s           SURVIVED    except-as no longer rebinds a name
N28  R4-4 collected=92  92 passed in 7.82s           SURVIVED    a relative __import__ is resolved as absolute
N29  R4-4 collected=92  1 failed, 91 passed in 7.99s KILLED by test_every_loader_kind_is_an_include_edge[compile-read_text]
N32  R4-4 collected=92  92 passed in 8.23s           SURVIVED    an ALLOWED_DYNAMIC_LOADS target need not be listed
N34  R4-5 collected=92  3 failed, 89 passed in 7.99s KILLED by test_live_tree_clean, test_real_tree_lists_the_dynamically_loaded_helper, test_live_tree_clean_staged
N35  R4-5 collected=92  1 failed, 91 passed in 8.08s KILLED by test_edit_snapshot_hook_load_is_an_include_edge
pin intact: {'scripts/no_laya_in_gates.py': True, 'scripts/gate_files.txt': True}
```
(N34 lists the hook as `.claude/hooks/./edit-snapshot.py` in L; N35 skips the vocabulary scan for `.claude/` paths.)
AF-AP-138, the 10 distinct killing tests by node id on the UNMUTATED copy (`/tmp/vj10r4/pin`, screen sha ab33c767c65c6f56):
```
10 passed in 1.63s
```
Survivor discriminators (`/tmp/vj10r4/mut/disc.py`; one input each, the PIN screen vs the mutant screen, the runtime judged by
bash or Python; N13 re-judged by the marker oracle, since its helper output is captured by `$( )`). Pasted, trimmed:
```
N1   PIN: rc=4 gate-file-unparseable: scripts/g.sh:1: constructs nested too deep to scan | MUTANT: rc=0 … clean   bash: helper RAN
N12  PIN: rc=4 gate-file-sources: scripts/g.sh:3: scripts/h.sh                           | MUTANT: rc=0 … clean   bash: helper RAN
N13d bash_ran=True  xtrace=True  PIN screen_rc=4 agree(caught)                           | MUTANT screen_rc=0 FAIL-OPEN
N16  PIN: rc=4 gate-file-sources: .github/workflows/w.yml:4: scripts/h.sh                | MUTANT: rc=0 … clean
N18  PIN: rc=4 gate-file-unparseable: .github/workflows/w.yml   (PyYAML hidden)          | MUTANT: rc=0 … clean
N20  PIN: rc=4 gate-file-sources: .github/workflows/w.yaml:6: scripts/h.sh               | MUTANT: rc=0 … clean
N22  PIN: rc=4 gate-file-import-unlisted: proofs/x/check_y.py:2 loads proofs/x/helper.py | MUTANT: rc=0 … clean   python: rc=0 (ran)
N23  PIN: rc=4 gate-file-import-unresolved: proofs/x/check_y.py:3                        | MUTANT: rc=0 … clean   python: HELPER-RAN
N24  PIN: rc=4 gate-file-import-unresolved: proofs/x/check_y.py:5                        | MUTANT: rc=0 … clean   python: HELPER-RAN
N32  PIN: rc=4 gate-file-import-unlisted: scripts/lint_delta.py:106 loads .claude/hooks/ed… | MUTANT: rc=0 … clean   `spec_from_file_location`
N7   PIN: rc=0 clean | MUTANT: rc=4 gate-file-sources: scripts/g.sh:3: scripts/h.sh        bash: helper not run   (fail-closed only)
N8   PIN: rc=0 clean | MUTANT: rc=4 gate-file-sources: scripts/g.sh:5: scripts/h.sh        bash: helper not run   (fail-closed only)
N11  PIN: rc=0 clean | MUTANT: rc=4 gate-file-unparseable: scripts/g.sh:2: quote ' open    bash: helper not run   (fail-closed only)
N3   PIN: rc=4 heredoc << without a delimiter | MUTANT: rc=0 clean                         bash: rc=2 syntax error (no gate runs it)
N4   PIN: rc=4 … heredoc <<A pending          | MUTANT: the same (differs only in the name when a text ends without a newline)
N19  PIN: rc=4 … w.yml:6 | MUTANT: … w.yml:5   (real line 7: both wrong, § 4)
N25  PIN: rc=4 unresolved | MUTANT: rc=0 clean                                              python: LISTED-RAN (the mutant is right)
N28  PIN: rc=4 unresolved | MUTANT: rc=0 clean                                              python: ImportError, nothing loaded
```
- 27 new mutants, 9 killed, 18 survived. 10 survivors turn a refusal into CLEAN on text whose helper really runs, so they are
  real test gaps, one or more per contract line R4-1..R4-4: N1 (R4-1: the RecursionError branch), N12 and N13 (R4-2: `!` before
  `((`, the `$((`-to-subshell fallback), N16, N18, N20 (R4-3: quoted `run` keys, missing PyYAML, `.yaml` files: the builder's
  "fails closed" and D5 claims have no test), N22, N23, N24, N32 (R4-4: `builtins.exec`, dynamic-module ambiguity, loop-variable
  rebinding, an allowed target that is unlisted). The builder's evasion script had `builtins-exec` and `loop-var` shapes; neither
  became a committed test.
- 3 survivors only refuse more (N7, N8, N11): coverage gaps on the fail-closed side.
- 5 are harmless or equivalent: N3 (bash cannot parse the text), N4 (the same line), N19 (line number only), N25 and N28 (no
  runtime load can differ).
- R4-5: both new mutants are killed.

## Contract re-check (frozen AMENDMENT 3 on AMENDMENT 2) and the builder's claims

| contract line | acceptance, as frozen | verdict here | evidence |
|---|---|---|---|
| R4-1 | a text ending open is refused at its START line, both modes; never the reason the live tree fails | MET | § 3: 15/15 new shapes; live 0 of 27 texts end open, worktree and index |
| R4-2 | members S12…S36 caught, BH-2 refused, live tree clean both modes; heredoc bodies are data | MET as frozen (live-tree scope) | committed member tests green (§ 11); bash's own parse finds only the 2 allowed sources live (§ 2); NEW desyncs outside the live tree: V-01, V-02, V-03 |
| R4-3 | workflows parsed; each `run:` its own text; refusal names file + YAML line; S39, S40, X3, YH-4 refused, YH-3 names its line | MET for literal and plain values; the line is wrong for folded/quoted values (V-06) | § 4 |
| R4-4 | named loaders closed over the list; (a) exceptions exact (file, target) + counted; (b) 7 live sites accounted, live clean; ES refused; a new unlisted load refused | MET per site; the count is per site and the base is trusted (V-05) | § 5, § 6, § 8 (reachability commit refused `gate-file-import-unlisted: proofs/S0-99/check_vj.py:2 loads scripts/vjh.py`, rc 1) |
| R4-5 | the hook listed, `.claude/` untouched | MET | § 7 |
| R4-6 | limits paragraph corrected; the exec-edge count re-measured | MET | § 7: 17/15/9 and 30/22/13 reproduced |
| "nothing else changes" | vocabulary, exit codes, texts, SELF, no bypass, output format, AMENDMENT 2 rules | MET | the block from `# ---------- Matching ----------` to the end of `main()` is byte-identical to R3 (`diff` of `git show 5090671^:…` vs the PIN: IDENTICAL); `_module_candidates` is the removed search loop moved verbatim |

Reachability through the real hook in `--staged` mode for R4-4 (throwaway repo, pasted):
```
lint_delta (index vs HEAD): 2 .py changed, 0 NEW pyflakes hit(s), 0 removed
gate-file-import-unlisted: proofs/S0-99/check_vj.py:2 loads scripts/vjh.py
COMMIT BLOCKED by the never-a-gate screen (rc=4)
commit rc=1; HEAD=24ae8f3
```
The builder's "issue #37 findings closed incidentally", checked (the R3 screen = `5090671^`):
```
S09    R4: agree(caught)  gate-file-sources: scripts/g.sh:2: scripts/h.sh      R3: … scripts/g.sh:2: \
S10    R4: agree(caught)  gate-file-sources: scripts/g.sh:2: scripts/h.sh      R3: FAIL-OPEN (rc 0)
S04    R4: agree(caught)  gate-file-sources: scripts/g.sh:2: <(cat scripts/h.sh)   R3: … scripts/g.sh:2: <
pc_lane.sh: 609 lines, 650 segments, opened=None, last segment line 609
  seg line 386 masked='echo QQQQQQQQ…'   seg line 397 masked='echo QQQQQQQQ…'   (the `). ` text inside echo strings is masked)
segments with line >= 293: 363
```
- F-B9 closed (S09, S04 name the real target). F-B3's S10 closed (R3 read it CLEAN). F-B7 closed (lines 386 and 397 are scanned
  and masked; the old blind span 293-610 now yields 363 segments). F-B11 closed (§ 7). All SOLID.
- F-B6 "partly": the named killing tests exist and pass (fails_closed[param], S24, S34, in the 92); the kill claims rest on the
  builder's m13/m14/m23, not re-run by brief rule (UNSURE). The vacuous comment fixture it names is still there
  (`# . scripts/helper.sh would be refused`, `tests/test_no_laya_in_gates.py:468`), as the builder says.
- The builder's cost claim: R3 vs R4 on the same live tree and list, back to back, 3 runs each, twice: R3 .30/.32/.29 and
  .37/.29/.33 s; R4 .39/.41/.39 and .44/.39/.39 s. About +0.08-0.10 s, as claimed (SOLID).

## FINDING INVENTORY (no severity filter; V- ids are this lane's)

Each row: classification · evidence · contract mapping · canonical path · material effect · reproduction · suggested fix.

- **V-01 FOLLOW-UP — an R4 REGRESSION: a `$'…'` heredoc delimiter with an ANSI-C escape hides a later source edge.** SOLID.
  - Mechanism: `_unquote` (`scripts/no_laya_in_gates.py:126`) drops the `$` of `$'…'` but keeps its escapes; bash translates them
    (its parse prints `cat <<'echo A'`). The screen's heredoc then ends at a later line equal to the untranslated text.
  - R3 refused AQ1 at the right line; R4 reads it CLEAN (AQ1-AQ4, PQ5b). Real hook: commit 2 landed (`41 files scanned, clean`),
    and bash then ran the unlisted, vocabulary-carrying helper in the gate's shell.
  - Contract: R4-2's "heredoc delimiters by bash's word rules" (its examples are `<<\EOF`, `<<'EOF'`, `<<"EOF"`, `<<-EOF`,
    `END-X`; `$'…'` is not among them; R4-2 is scoped to "the text the live tree holds") + AMENDMENT 2's source rule. Partial.
  - Material: a crafted gate sources unlisted code and the screen reads CLEAN. But it needs a deliberate `$'…'` delimiter with an
    escape AND a crafted re-sync line (without it R4-1 refuses); no live instance (grep; bash's own parse). A deliberate evader
    already has the declared exec-edge door (R23's F-B3 standard).
  - Reproduction: `/tmp/vj10r4/lex/cases2.py` AQ1; § 8 commit 2. Fix: apply bash's ANSI-C translation in `_unquote`, or refuse a
    `<<$'…'` word holding a backslash (fail closed); add AQ1 as a test.
- **V-02 FOLLOW-UP — `time` before `((` or `case` desyncs the scan** (TK1-TK5, CA5). SOLID. The keyword set
  (`_LEADING_KEYWORDS`, `scripts/no_laya_in_gates.py:121`) lacks `time`, so `(( … << w ))` becomes a heredoc and a case pattern's `)` closes a quoted
  `$(`. Pre-existing (R3 CLEAN too). Real hook: commit 3 landed. Needs a crafted re-sync line (TK7 alone refuses); not live.
  Contract: the docstring's "follows bash's … arithmetic, case … rules"; R4-2's frozen scope is the live tree. Fix: accept `time`
  and `time -p` as leading words; add TK1 and TK5 as tests.
- **V-03 FOLLOW-UP — `$[ … ]` arithmetic: its `<<` is a heredoc that can end at a later line** (DA1 CLEAN). SOLID. Pre-existing.
  The builder's D4 ("which ends in an R4-1 refusal") is false as stated; only DA2's shape refuses. Fix: model `$[ … ]` as
  arithmetic, or refuse it; correct D4 and the self-attack line "Its known exotic triggers refuse instead (D4)".
- **V-04 FOLLOW-UP — EXPONENTIAL scan time, introduced by R4.** SOLID. Nested `$(( … ) )` costs 2^k: 27.62 s for a 192-byte line
  (R3: 0.04 s). `def arith` (`scripts/no_laya_in_gates.py:332`) scans, fails and restores; `dollar()` re-scans the body as
  commands. One such line in any listed gate would stall every commit (a DoS; no fail-open). Not live (the live run is 0.39 s).
  Contract: none (cost is not a frozen line; item 9 makes it a finding). Fix: decide `$((`-arithmetic vs `$( (`-subshell once
  per start position (memoize), never by a full re-scan.
- **V-05 FOLLOW-UP — the exception set trusts any unknown base and counts sites, not loads.** SOLID.
  - E1a/E1d(i): the entry is re-pointed through its base; both the runtime check and the exactness test stay green.
  - E1b: a wrapper makes one site carry a second load.
  - Real hook, commit 4: the commit landed while the hook's own `lint_delta` process ran a foreign `edit-snapshot.py` carrying the
    vocabulary. This is F-B2's ES shape, re-opened through the entry.
  - The comment at `scripts/no_laya_in_gates.py:697-698` (`re-pointed at another file`, "the F-B5 class") and
    the "never more" at `scripts/no_laya_in_gates.py:696` are false as stated.
  - The builder's report declares the base residual (Self-attack 3).
  - Contract: R4-4(a) (exact (file, target), count checked): met per site. Material: needs a deliberate edit of the load's base or
    a wrapper; the F-B5 class (KNOWN, issue #37).
  - Fix: correct the comment; bind each entry to its base expression (e.g. `REPO`, the parameter `root`) and count wrapper calls.
- **V-06 FOLLOW-UP — wrong R4-3 refusal lines for folded and multi-line quoted `run:` values** (Y2b, Y2c, Y13 names the next
  step's line, Y14). SOLID.
  - `_workflow_runs` (`start_mark`, `scripts/no_laya_in_gates.py:492`) adds a style offset, then counts the value's own newlines. Its docstring
    (`scripts/no_laya_in_gates.py:472-473`, ending `a folded or flow value has no line of its own`) says every other style maps to the value's start line: false as stated.
  - The refusal still fires; no live workflow uses these styles.
  - Contract: R4-3's line clause (mapped). Material: only the diagnostic line; the decision does not change.
  - Fix: for any style other than `|`, report the value's start line (what the docstring says).
- **V-07 FOLLOW-UP — GitHub `${{ … }}` substitution hides a source** (Y7b, Y7c; the screen scans the text before GitHub
  substitutes). SOLID (screen side) / INFERRED (GitHub side). Pre-existing; no live `${{` in any `run:`. Not in R4-3's text.
  Fix: refuse `${{` in `run:` values that reference `matrix`, `env`, `inputs` or step outputs, or declare the limit.
- **V-08 FOLLOW-UP — `shell: python` steps that load files read CLEAN** (Y9, Y9b, Y9c). SOLID / INFERRED (GitHub side). D4 files
  this under "refusals that are safe": false as stated. Pre-existing; no live `shell:` key. Fix: refuse a step whose `shell:` is not
  bash/sh (or apply R4-4's Python rules to its text); correct D4.
- **V-09 FOLLOW-UP — undeclared Python load spellings.** SOLID. `__builtins__.exec` and an aliased `builtins` (P6b, P6c;
  `node.attr` in `_loader_name`, `scripts/no_laya_in_gates.py:1014`), `os.chdir` + a relative literal
  (P27; `def _as_path`, `scripts/no_laya_in_gates.py:720`), `__file__` re-pointed through `sys.modules[__name__]` (P23). Deliberate; none in the 28
  listed Python gates. Fix: treat exec/eval/compile on any name bound to the builtins module as a loader; refuse relative-literal
  loads after `os.chdir`; declare the `__file__` rebinding family in the docstring.
- **V-10 FOLLOW-UP — declared R4-4 limits, measured:** P5 (getattr), P6/P24 (the globals()/vars family), P8
  (`pkgutil.resolve_name`), P11 (`importlib.util.find_spec` + `exec_module`, a natural idiom), P28 (`imp.load_source`), P29
  (`site.addsitedir` + a `.pth` line). All run unlisted code; the docstring's "other ways to run code in the process" covers them
  in general. Fix: add `find_spec`, `resolve_name`, `load_source`, `addsitedir` to `_LOADERS` or name them in the docstring.
- **V-11 FOLLOW-UP (KNOWN class F-B4)** — `sys.path` shadowing of a LISTED module name (P1 static import, P3 `import_module`):
  new members; R4-4 defines module-name loads "exactly like AMENDMENT 2's static imports".
- **V-12 FOLLOW-UP (KNOWN class F-B3)** — `coproc . x`, `coproc source x` (CP1, CQ1): new prefix-word members. `eval`,
  `command .`, `builtin source`, `\.`, `'.'`, alias (EV1, EV2, SP1-SP5): KNOWN members, re-observed with bash's verdict.
- **V-13 FOLLOW-UP — mutation test gaps** (§ 10): 10 new survivors turn a refusal into CLEAN on text whose helper runs (N1, N12,
  N13, N16, N18, N20, N22, N23, N24, N32); 3 more only refuse more (N7, N8, N11). The builder's "a missing PyYAML fails
  closed" and D5 (`.yaml`) have no test. Fix: one fixture per discriminator in § 10.
- **V-14 INFO — false refusals (fail-closed), none live.** Pre-existing: an array element `.` (FA1, a natural `find` argument
  array; FR2, FR3), `{`/`}` in argument position (FR1, FR4). Introduced by R4: a heredoc delimiter followed by `)` in a `$( )`
  (HD1; bash accepts it with a warning), a line continuation inside a heredoc word (EN2), a loader class read as a value (P12b),
  loads under `if TYPE_CHECKING:` / `if False:` (P25, P26), nesting past about 150-400 levels.
- **V-15 INFO** — `scripts/lint_delta.py:106` (`spec_from_file_location`) under the (file, tail) key: sound on the hook path; the
  F-A3 index/worktree gap (KNOWN) remains; a manual run from another repository's CWD loads that repository's file (§ 6).
- **V-16 INFO** — a Python gate whose `ast.parse` raises RecursionError exits 1 with a traceback, not `gate-file-unparseable`
  (`_import_errors`, pre-existing); Python cannot compile such a file either, and the hook still blocks.
- **V-17 INFO** — quadratic cost in a run of leading keywords (`at_command`): 0.40 s at the longest run bash accepts.
- **V-18 INFO** — a YAML alias yields the anchor's refusal line twice (Y3). A capital `Run:` is not scanned (Y4d); whether GitHub
  accepts `Run:` is NOT measured (UNVERIFIED).

### Predicate table (the candidates closest to blocking; every other row fails conjunct 1 or 3 plainly)
| id | 1 contract | 2 canonical (real screen / real hook) | 3 material | 4 discriminator | 5 in boundary | BLOCKS? |
|---|---|---|---|---|---|---|
| V-01 | partial — R4-2's word-rule clause; its examples and live-tree scope omit `$'…'` | yes / yes (commit 2 landed) | no, by itself — a deliberate delimiter plus a crafted re-sync line; not live; the exec door is open by design | yes — AQ1 (R3 rc 4, R4 rc 0, bash runs it) | yes — `_unquote` | no → FOLLOW-UP |
| V-02 | weak — docstring claim; R4-2 frozen scope met | yes / yes (commit 3) | no, by itself — crafted re-sync; not live; pre-existing | yes — TK1 | yes | no → FOLLOW-UP |
| V-03 | weak — D4 is a report claim; R4-1 holds as written | yes / not run | no — deliberate; not live; pre-existing | yes — DA1 vs DA2 | yes | no → FOLLOW-UP |
| V-04 | none — cost is not a frozen line | yes / not run (a hang would stall the commit) | no, by itself — a crafted line; not live | yes — k=16..22 series, R3 0.04 s | yes — `arith()` | no → FOLLOW-UP |
| V-05 | R4-4(a) met per site; the comment overstates | yes / yes (commit 4, the hook's own process) | no, by itself — a deliberate base edit or wrapper; F-B5 class, KNOWN; residual declared in the report | yes — E1a, E1b | yes | no → FOLLOW-UP |
| V-06 | yes — R4-3's line clause | yes / not run | no — only the diagnostic line; the refusal fires; no live workflow uses the style | yes — Y13 | yes | no → FOLLOW-UP |
| V-08 | none — R4-3 says scan as shell; Python steps are outside it | yes / not run | no — not live; D4's claim false | yes — Y9 | yes | no → FOLLOW-UP |

## GATE RECOMMENDATION

**`MERGE-READY-WITH-FOLLOWUPS`**. No finding meets the complete blocking predicate as dispositioned above. That disposition
applies R23's standard to conjunct 3: a fail-open that needs a deliberately crafted text, with no live instance, is not material
by itself; V-06 changes only a refusal's line number. This recommendation depends on that reading. If the coordinator reads the
brief's materiality clauses literally (any fixture where the screen reads CLEAN while unlisted code runs; any stated claim that is
false as stated), then V-01 (the R4 regression), V-05 (the false comment at `scripts/no_laya_in_gates.py:697`) and V-06 (R4-3's
line) meet all five conjuncts, and the recommendation becomes `NOT-READY` on those three. Everything the frozen acceptance names is
met and reproduced here (the contract table above). The coordinator owns the final gate.

## Evidence discipline — reproduced, read, skipped

- Reproduced here (commands and output pasted above): the premise; the gates; every item 2-5 and 9-10 fixture, against bash or
  Python at runtime plus the PIN and R3 screens; the hook commits (§ 8 and the reachability commit); the census (§ 6); both exec-edge
  counts (§ 7); the incidental-closure claims; the cost claim.
- Read, not run: how the 7 live sites resolve (primary source, plus the screen's own values); the F-B6 kill claims (tests exist and
  pass; the builder's m13/m14/m23 not re-run); GitHub's behaviour for `${{ }}`, duplicate keys, `Run:` and `shell: python`
  (its documented model; no Actions run); "nothing else changes" (diff read, byte-identical blocks measured).
- Skipped, by the brief: the builder's S/X/BH/YH rows, its 37 evasion shapes and m1-m25 (except to confirm that named killing
  tests pass); the PC and the bridge. Not run by choice: the live gate files themselves (they push, commit and call the PC). bash's
  own parse (`declare -f`, never executed) stood in for them.
- In pasted blocks, text after the tool's own line format (the shape under test, `(pre-existing)`, a backticked identifier
  from the cited line) is my annotation, separated by at least two spaces. A `path:line` that points into a MODIFIED fixture copy
  (not the repo) is written `path line N`, so the linter does not check it against the repo file.

## report_lint (one fix round of the three allowed; pasted)

```
$ python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/VERIFY-J1-0-R4-report.md --root .
report_lint: 61 refs — OK 48, NEAR 0, MISS 0, UNCHECKABLE 13, UNRESOLVED 0 (worktree)      lint rc=0
```
Round 0 read `OK 21, NEAR 4, MISS 23`; the fixes added a cited-line identifier to each flagged line, or reworded a fixture-copy
`path:line` as `path line N` (the rule is in the evidence-discipline note).

## DISCREPANCIES

- **Brief item 2's "NEW shapes" include six KNOWN ones.** `eval ". x"`/`eval '. x'`, `command . x`, `builtin source x`, `\. x`,
  `'.' x` and an alias to `.` are F-B3 members already filed as issue #37 (R23's S22, S03, S02, S30, S32, S08). I ran them with
  bash's verdict (§ 2) and report them as KNOWN (V-12), not as new findings.
- **Brief item 3's "an unterminated `$'…'`" overlaps the builder's `ansi` shape** (`echo $'open`, one of its eight). I used
  escape-bearing variants instead (U1: an escaped last quote; U3: `\\` then `\'`).
- **The brief's premise block was measured at local 5090671; the PIN is 0e7b6c3.** The blobs are identical (§ 1), so no item
  changes.
- **The shared worktree differs from the PIN in one listed gate.** `proofs/S0-05/check_egress.py` carries another lane's 2-line
  docstring change. My read-only live-tree runs read the worktree. The load site at line 122 is not in that diff.
- **The throwaway repo's vendored-manifest gate was inert.** The PIN subset carries no `sandbox-kit/VENDORED-MANIFEST.md`, so
  that hook gate skipped itself in § 8. The screen's gate ran as in the real repo. The hook's `lint_delta` wrote
  `.claude/hooks/__pycache__/` inside the throwaway only; it was removed with it.
- **My own instrument had two bugs, corrected before the numbers were used (§ 7).** The first exec-edge matcher missed `if cmd`;
  the second masked across two quoted strings. N13's first runtime check read the helper's stdout, which `$( … | cat )`
  captures; the marker oracle re-judged it (§ 10).
- **Recommendation vs a literal reading of the brief's predicate.** See the GATE RECOMMENDATION line: it names the three findings
  that would block under a literal reading of the materiality clauses.

## NOT-done

- No PC or bridge run (the brief). The PC's PyYAML is not measured, so the builder's open item stands. Also, no committed test
  pins the missing-PyYAML refusal (N18).
- GitHub Actions was not run. Y4d (`Run:`), Y5/Y5b (duplicate keys), Y7b/Y7c (`${{ }}`) and Y9 (`shell: python`) are graded
  on the screen side only, and inferred on the GitHub side.
- The builder's m1-m25 were not re-run (the brief). Its F-B6 kill claims are checked only as far as "the killing tests exist and
  pass".
- No fix and no test were written (a verify lane; boundary = this report).
- /bug-echo and registry rows are the coordinator's step. Candidate classes:
  - V-01: a more faithful lexer that mis-translates one quoting form, and so regresses a shape the cruder lexer refused
    (fidelity regression);
  - V-04: a backtracking re-scan that goes exponential in nesting depth, in a hook that runs on every commit;
  - V-05: an exception keyed by a literal tail under an unknown base (F-B5's class, in the dynamic-load rule).
