# VERIFY-JT3-R1 report: the search intercept and quirk guard after its one repair

Role: adversarial-verifier (sandbox). Served model: claude-opus-5-5 (Opus 5.5, from the session's system prompt; no refusal stop
seen in this lane). Written incrementally; the gate recommendation is at the end.

## 0. Premise re-measure (first action, 2026-09-24 17:29Z, /home/user/agent-factory, local HEAD 28d5fcb)

```
$ sha256sum .claude/hooks/search-intercept.py tests/test_search_intercept.py tests/test_session_hooks.py
927410a382b2138fac9bd06e8f84c31e9411301a69005192e5b9b427c17e5b2c  .claude/hooks/search-intercept.py
ffb8f18123a4f0e024817b064a6fa77ddf9ee090839fdd5cc000dfaf61782096  tests/test_search_intercept.py
2a3a90c86ba3001e13bf92922352c0b4dc5652bb376d1d4e74c348d2afa2c254  tests/test_session_hooks.py
$ sha256sum scripts/install_session_hooks.py .claude/settings.json
30c4862939017c5c8a3e93fa40c2d609f269f23e84bdf97c5169ee1c947c20b9  scripts/install_session_hooks.py
ad7fe12e10a72d510ad6fec560dc031b903926338e32ac5dd9534318b5da996c  .claude/settings.json
$ bash scripts/test_summary.sh tests/test_search_intercept.py tests/test_session_hooks.py tests/test_hooks_worktree.py --basetemp /tmp/vj3r1/bt
pytest-exit: 0
pytest-summary: 117 passed in 46.13s
$ PATH=/usr/local/bin:/usr/bin:/bin bash scripts/test_summary.sh tests/test_search_intercept.py tests/test_session_hooks.py --basetemp /tmp/vj3r1/bt2
pytest-exit: 0
pytest-summary: 78 passed, 33 skipped in 19.96s
```

All five digests match the brief's PREMISE; both counts match. The verify proceeds on this PIN.

(Sections below are appended as the work lands.)

## 1. F-3: the narrowed trailing-amp rule, re-derived and re-graded (the coordinator's ruling)

Instrument: `/tmp/vj3r1/measure_amp.py` (mine, written for this lane). It streams every transcript line by line and runs
each Bash command through the hook's OWN rule function (`quirk(Parsed(cmd), rules=("trailing-amp",))`): once with the
repaired file, once with the PIN copy (`/tmp/vj3r1/pin/search-intercept.py`, sha256 `a8fd4d39...`, copied from the lane's
`/tmp/jt3r1/pin/`, digest checked). Every fire keeps its tool_result. The subagent set is all 287 `subagents/**/*.jsonl`
less two: this lane's (`agent-a11a6e8bb5d0d69d0`) and the JT3-R1 lane's (`agent-a0f26767c786231ef`, whose fires are its
own probes). Run at 17:4xZ (16 s):

```
            files  Bash cmds  repaired fires  PIN fires  repaired-not-PIN
main          1     13,746         35             81            0
sub         285     19,253         19             45            0
lane(JT3-R1)  1        104          2              3            0       (its own probes; excluded, as the lane did)
mine          1         25          0              0            0
```

Main reproduces the lane's 35 exactly (on 111 more commands). Sub is 19 against the lane's 18: the one extra fire is new
since the lane measured (VERIFY-FT1, 2026-09-24T17:38:24Z). The repaired rule fires only where the PIN rule fired
(a strict subset: 0 repaired-not-PIN).

### 1.1 Every fire read and classified (54: the lane's 53 plus the new one)

Reading applied: the coordinator's ruling. A later step that reads `$!` or a list-assigned variable is harm even
when it only prints it; a false positive is a block of a command that would have run as intended.

| Fires (my numbering, time order) | What reads what the list took | Class |
|---|---|---|
| main #1-#9, #11-#14, #17, #19-#21, #29-#30; sub #36-#38, #40-#42, #44, #52 | `echo "... pid $!"` (the subshell's pid printed) | real |
| main #10 | `(cd $S && nohup graft build ... & echo "build started pid $!")`: `$!` inside the group is the list's subshell | real |
| main #15 | `echo "D5m poller pid $!"` (the auto-mode classifier denied the call; it would have printed the wrong pid) | real |
| main #16 | `... lane_gate.sh ... & echo "gate pid $!"` | real |
| main #18 | `head -6 $SP/m2-gate/gate.log` then `$!`: result `head: cannot open '/m2-gate/gate.log'` | real |
| main #22-#28, #32 | `$!` plus a list-assigned `$GL`/`$GATELOG`/`$S`/`$SP` printed empty (`log ` , `-> /t-full.log`, `log=/t90-runall.log`) | real |
| main #31 | `echo $! > .../lane-g1.pid` (the CLAUDE.md 2026-09-21 incident shape) | real |
| main #34 | `$SP` read after the list (`(log /t90r2-runall.log)` printed without its directory) | real |
| main #35 | `P=$!` watchdog: `pkill -P $P; kill $P` would hit the list's subshell, not pytest | real |
| **main #33** | `(cd ... && setsid nohup bash -c '...' >/dev/null 2>&1 & echo $! > /dev/null)`: `$!` discarded; the pid is read later with `pgrep` | **false positive** |
| sub #39 | `PID=$!` ... `kill $PID` (the call also died on its own `pkill -f`, rc 144: a second quirk) | real |
| sub #43, #45 | printed pid vs the job's (`launched pid 316` beside pgrep's 318; `ps -p $!` shows `/bin/bash -c source ...`) | real |
| sub #46-#48 | `SRVPID=$!`/`SRV=$!` then `kill`: the probe server survives; #48 also `$PY` empty (`: command not found`, exit 127) | real |
| sub #49 | `USERPID=$!` labelled "uid 65534": it is the uid-0 subshell | real |
| sub #50, #51 | `MUTPID=$!`/`MP=$!` printed, then `tail --pid` (the wait works; the printed pid is the subshell's) | real |
| sub #53 | `cd /tmp/vk150/d6 && python3 ... & P=$!`, then relative `bin/systemctl`: `No such file or directory` | real |
| sub #54 (NEW, VERIFY-FT1 17:38:24Z) | `S=`, `P=`, `A=` assigned inside the backgrounded list, then `$S/vft1/t4.out`: `/vft1/t4.out: No such file or directory` | real |

```
false-positive rate under the ruling:  lane's set 1/53 = 1.9%   with the new fire 1/54 = 1.9%   (bar: 5%)
```

**Re-grade: the lane's section 3.2 classification holds, row for row, and 5% or less holds.** (Under the alternative the
lane named in D-J, where a merely printed pid "ran as intended", the rate would be about 64% and the rule would leave
SHIPPED; the ruling adopted the stricter harm reading, so that alternative is not the gate.) The new VERIFY-FT1 fire is
a live, current example of the harm the rule names: that call lost three variables to the background subshell.

### 1.2 The other direction: the 72 PIN fires the narrowed rule dropped (46 main, 26 sub)

25 are the `& )` detach form. I scanned all 72 results for error markers (`No such file`, `command not found`,
`Exit code [1-9]`, `rc=[1-9]`, `fatal`, `Error`): eight hits, none a trailing-amp harm. They are: the two live 14:03
blocks (negatives, by design); a builder probe (`true && true &`); four launches whose later steps use absolute paths
(the error lines come from other steps); and one `pkill -f "[r]un_packs.sh"` call (rc 144), which the repaired hook
still blocks through `pkill-self` (checked: `quirk()` returns `pkill-self` for it). The nine dropped fires that commit
inside a backgrounded list (`safe_commit.sh ... && ... &`, 2026-09-15 07:35 to 16:50) show the commit and the push
completing in their results.
No dropped fire shows a harm in its result.

### 1.3 New shapes through the REAL hook (`/tmp/vj3r1/amp_shapes.py`: `main()` in a subprocess, a fresh scratch state each)

```
blocked, harm real (bash-confirmed where marked):  A02 `( a && job & echo $! )`   A05 a function body `f() { a && b & }; f; echo $!`
   (bash: $! comm=bash)   A06   A15 `${!}`   A21 a detach group then a real list   A25 `a || b && job &`   A26 a pipeline in the list
   A28 an exported variable read two lines later   A07 `coproc cd /tmp && sleep 1 & echo $!` (bash: $! comm=bash,
   sleep its child: the whole list went to the background)
blocked, would run as intended (FALSE POSITIVES outside the 54 reads, 0 occurrences in them):
   A01 `( cd /tmp && nohup sleep 1 & echo more ) ; echo $!`  (the lane's ADJ-2: CONFIRMED; bash prints an empty parent $!)
   A16 `echo ${!name}` (indirection read as $!)   A17 a variable already set to the same value   A18 one set again before the read
   A03 `wait $!`: harm by the ruling's letter, but bash waits exactly as long (0.61 s for a 0.6 s job); INFO
passed, harm real (FALSE NEGATIVES; D-2 bars false positives only, so these are recall):
   A08 `$!` in an unquoted here-document (bash wrote the subshell's pid, comm=bash; the lexer drops heredoc bodies)
   A09 `P=$(echo $!)` (refs are not collected inside $( ))   A10 `a &&` newline `b &` (F-9, unchanged)
   A11 `cd X && job > log &` then `cat log` (bash: the caller's cwd is unchanged)   A12 `kill %1`   A19 `read X ... && job &`
   A24 the pidfile race `rm -f f && job &` then `echo 1 > f` (the CLAUDE.md incident's race half)
passed, correct:  A04 `& wait`   A13 `"\$!"`   A14 `$'$!'`   A20 the detach form over lines   A22 a comment   A23 single quotes
   A27 `$!` after a later `&`
```

F-3 disposition: the ruling's bar holds (1.9%), the live negatives pass, the harm signals fire through the real hook.
The false positives above are shapes that never occurred in 33,000 Bash commands; the false negatives are recall,
which D-2 does not bar (FOLLOW-UP rows in section 9).

## 2. F-1 and F-2: answer fidelity (scope and mode) against the raw call

### 2.1 Primary source: what the Grep tool runs (Claude Code 2.1.280, the harness binary `/opt/claude-code/bin/claude`)

The lane probed the Grep tool's behaviour (sound). I read its argument builder from the binary (function `AIn`, a
literal-token extraction). The tool runs rg with `--hidden`, `--glob !.git !.svn !.hg !.bzr !.jj !.sl` (the list
`vIn`), `--max-columns 500`, `-i`, `-l` for files_with_matches, `-c -H` for count (so its "occurrences" are matching
LINES), `--null` or `--json`, `--type`. Three more inputs matter:

- **the `glob` string is SPLIT**: `r.split(/\s+/)`, then each piece on `,` unless it holds `{` and `}`, and each part
  becomes its own `--glob`;
- **Read `deny` permission rules become `--iglob !**/<rule>` exclusions** (`qZe` then `gYt`);
- orphaned-version and task-output exclusions (`i8`, `jur`): these apply only to Claude's own config and tasks dirs.

This container has no `deny` rule in any settings file (read only: `/root/.claude/launcher-settings.json`,
`/root/.claude/settings.json`, `/home/user/.claude/settings.json`, the repo's `.claude/settings.json`), so the deny
exclusion is latent here.

### 2.2 The Grep tool, real tool beside the real hook (my Grep tool calls ran raw: `.jev/intercept-off` holds the live hook off)

Real tree, cwd the repo, hook `python3 .claude/hooks/search-intercept.py` with a scratch `AF_SEARCH_INTERCEPT_STATE`:

```
input                                                     real Grep tool                      the hook's rg part
glob ".claude/**/*.py", pathless (a hidden segment)       1 file: .claude/hooks/search-intercept.py   the same 1 file
path scripts, -i true, "OUR_HOOKS"                        1 file                              the same
type py, pathless                                         3 files                             the same 3
output_mode count, pathless                               8 files, 75 lines (53/2/3/3/3/9/1/1) the same 8, the same counts
path scripts, glob "*.{py,sh}" (braces)                   1 file                              the same
path scripts, output_mode count, "our.hooks" (regex dot)  scripts/install_session_hooks.py:3  the same
path scripts, glob "*.sh,*.py"                            1 file: scripts/install_session_hooks.py   "rg: 0 hits."   <- F-1 again
path scripts, glob "*.sh *.py"                            1 file: scripts/install_session_hooks.py   "rg: 0 hits."   <- F-1 again
pathless, glob "*.sh,*.py"                                (the tool splits it)                "rg: 0 hits."
```

Through the INSTALLED command as well (`install_session_hooks.py --target /tmp/vj3r1/inst/settings.json`, matcher
`Grep|Bash`, `sh -c <command>` from cwd `/`, scratch state): payload
`{"tool_name":"Grep","tool_input":{"pattern":"our_hooks","path":"scripts","glob":"*.sh,*.py"},"cwd":"/home/user/agent-factory"}`
gives rc 2, stdout 0 bytes, and `rg: 0 hits.` A discriminating probe rules out the reading "the tool ignores a bad
glob": `ROOT` in `scripts/` is in 31 files with no glob, in 14 with the split globs (`rg -l --hidden -g '*.sh' -g
'*.md'`), and in 0 with the one literal glob. The real Grep tool (`pattern ROOT, path scripts, glob "*.sh,*.md"`) returns
"Found 14 files", exactly the 14 of the split reading. The hook on the same input returns `rg: 0 hits.` The hook passes
the glob string to rg as ONE `--glob`. rg reads `,` and spaces outside braces literally, so nothing matches. The answer says that code which exists does not (VERIFY-JT3 F-1's
exact harm). This is **finding N-1**.

Fixture `/tmp/vj3r1/fx` (a git repo I built; FAKE values only). It holds tracked `scripts/cfg.py` (one line with two
matches), a hidden `.hidden_code/`, an `.rgignore`d `rgign/`, a `.git/info/exclude`d `exdir/`, a `.gitignore`d
`secret_dir/`, a 57 MB `scripts/big.py` with the match on line 600,001, a binary `scripts/bin.dat`, a UTF-16
`scripts/utf16.py` and a symlinked `scripts/linkdir` to a dir outside. The real hook is copied unmodified to
`fx/.claude/hooks/` (sha256 `927410a3...`, equal to the tree's) with the real nag, and `graft build` is run there. The
real Grep tool beside the hook:

```
files_with_matches   real tool 5 files {.hidden_code/h.py, big.py, cfg.py, sub/deep.py, utf16.py}   hook: the same 5
count                real tool h.py 1, cfg.py 2, deep.py 1, utf16.py 1, big.py 1 ("6 total occurrences")   hook: the same
content              real tool 6 lines                                                                    hook: the same 6
```

So the mirrored scope is exact on every shape the brief listed: `.rgignore`, `.git/info/exclude`, a symlinked
directory, a large file, a path that is a file, a hidden-segment glob, `type`, `-i`, case, and a regex metacharacter.
It is also exact on UTF-16 and on a two-match line. The only divergences are N-1 and the latent deny rules (N-4).

### 2.3 Bash searches (real tree and fixture; `/tmp/vj3r1/fidelity.py`: the raw command runs itself as the oracle)

```
real tree                                          raw files  answer  missing (why)                                extra
grep -rl our_hooks            (pathless)              21        8     13, all ignored or binary: .gitignore 7 (pycache, .pytest_cache,
                                                                      /graft/), .code-review-graph/.gitignore 1, .git/info/exclude 5 (.gitnexus/)
grep -rn our_hooks            (pathless)              16        8     8: .git/info/exclude 4, .gitignore 4
grep -rl --include=*.py our_hooks .                     3        3     -
grep -rl --include=scripts/*.py our_hooks .             0        1     -                                            1 (grep matches base names)
grep -rl --include=*.py --exclude-dir=tests/red scripted_backend tests
                                                        5        4     1 UNEXPLAINED: tests/red/test_s0_01_backend_credential_screen.py
grep -rl --include=*.py --exclude-dir=red ...           4        4     -
grep -rli OUR_HOOKS / -rl our.hooks / -rlw / -R -l / -rc  (scripts)    the same file; the one missing is a .gitignored .pyc
grep -c / rg -c / grep -rl  on one file                 1        1     -
rg -l --hidden _heredoc_delim                           6        6     -
fixture: grep -rl FAKE_TOKEN_NAME (pathless)            9        5     rgign/r.py (.rgignore: NOT named by the answer), exdir/e.py
                                                                      (.git/info/exclude: not named), bin.dat (binary), secret_dir, graft cache   utf16.py
fixture: grep -rl --exclude-dir=scripts/sub ... scripts 4        3     scripts/sub/deep.py UNEXPLAINED               utf16.py
fixture: rg -l / rg -c                                  4        4     -
```

What this shows:
- **N-2 (the statement is not exact)**: a `grep -r` answer says "not searched, which grep -r reads: files that
  .gitignore or .ignore rules exclude, and binary files". rg also honours `.git/info/exclude`, `.rgignore` and git's
  global excludes. On THIS tree `.gitnexus/` is excluded only by `.git/info/exclude:7` (`git check-ignore -v`), so a
  pathless `grep -r` answer drops `.gitnexus/*` hits under a statement that does not name them. The categories are
  right in spirit ("ignore rules"); the wording is narrower than the truth.
- **N-3 (fewer files, not stated)**: `--exclude-dir` (and `--exclude`) with a slash. grep matches base names, rg's
  `--glob !x/y` matches the path, so the answer drops files the raw grep lists and says nothing. The caller's likely
  intent is served (it asked to skip that dir); raw fidelity is not. `--include=<a/b>` is the mirror image: the answer
  shows more.
- UTF-16 (INFO): rg decodes a BOM file and finds a match that raw grep cannot see (the answer shows more).
- rg answers match file for file (VERIFY-JT3's reading holds: a Bash rg keeps rg's defaults).

### 2.4 How often: every historical search the repaired hook would intercept today, replayed (`/tmp/vj3r1/replay.py`)

All main and subagent transcripts (mine and the JT3-R1 lane's excluded), deduplicated: 101 searches the repaired hook
intercepts today (17 Grep calls, 84 Bash). Each ran through the real hook (scratch state). The raw oracle is the Bash
search itself (its grep/rg part), or, for a Grep call, rg with the Grep tool's own flags from 2.1 (not the lane's
mirror):

```
answered 85: identical file sets 84 (Bash 73, Grep 11) + 1 Grep whose Cut listing is truncated (the count line's 126
files equals the raw 126)   passed (fail-open, mostly graft refusing --in a single file or an unindexed path) 16
differences in files or counts: 0
glob split by the Grep tool in any historical Grep call: 0 of 145 Grep calls
```

The repair fixed F-1 and F-2 on every shape that occurred (VERIFY-JT3 measured 1 difference in 105 at the PIN; now 0 in
85). N-1 and N-3 have 0 historical occurrences.

### 2.5 F-2 through the graft part of a names-only answer (D-I)

On the fixture, the names-only and count-only answers carry graft's block. That block is symbol cards (`zq_lookup ·
function scripts/cfg.py:L4-L5`, `def zq_lookup()`) and file names (`r.py · file rgign/r.py`, a file rg ignores). No
fake secret value appeared in any names or count answer: graft's cards hold signatures, not constant assignments. The
`def` line of a searched function name is a matching line in the literal sense (for `our_hooks`:
`def our_hooks(root: Path) -> dict`). D-1(a) requires graft's answer in every answer, so D-I is the contract working,
not F-2. INFO.

## 3. F-4: the suites under the CI workflow's declared tool set

`.github/workflows/stage0-ci.yml` (`tests` job): `actions/setup-python` 3.12, `pip install pyflakes pytest jsonschema
rfc3339-validator PyYAML`, then `python -m pytest tests/ -q`. Nothing there installs graft or a graft index (rg:
not installed by the workflow either; the runner image is not read here).

```
$ PATH=/usr/local/bin:/usr/bin:/bin bash scripts/test_summary.sh tests/test_search_intercept.py tests/test_session_hooks.py --basetemp /tmp/vj3r1/bt2
pytest-exit: 0
pytest-summary: 78 passed, 33 skipped in 19.96s                         (no graft; rg present)
$ PATH=/tmp/vj3r1/farm-nogr/bin bash scripts/test_summary.sh <the same pair> --basetemp /tmp/vj3r1/bt3
   (my farm: 1,108 commands of /usr/local/bin:/usr/bin:/bin, every one but graft and rg; `command -v graft rg` finds neither)
pytest-exit: 0
pytest-summary: 77 passed, 34 skipped in 19.89s                         (no graft, no rg)
$ PATH=/usr/local/bin:/usr/bin:/bin bash scripts/test_summary.sh tests/test_hooks_worktree.py --basetemp /tmp/vj3r1/bt4
pytest-exit: 0
pytest-summary: 6 passed in 1.11s
$ bash harness-ports/tests/run-all.sh           -> rc 0, "ALL SUITES PASSED", 91.6 s (every suite line "N passed, 0 failed")
```

Both counts equal the lane's (78/33 and 77/34). Every skip carries the `LOUD SKIP` reason (`-rs` lines in the runs).
Python 3.12 (CI's version): `/usr/bin/python3.12` exists but has no pytest, and I did not install one (a third-party
download). The hook is standard-library only, so I ran it under 3.11 and 3.12 on nine payloads (four quirk rules,
the detach form, three searches in names/content/count, an unparseable command): **9 of 9 byte-identical** (rc,
stdout, stderr). The hook and both test files compile with `-W error`. Not run on a GitHub runner (an outward action).

**The skip audit (which skipped test could run?).** The 33 no-graft skips are 14 test functions (33 cases). Every
test that needs an ANSWER needs graft and rg, because `decide()` returns 0 when either is missing. So without them,
any search-side negative control is vacuous, and guarding those is right (the lane's D-D). One guarded test's
subject is fail-open: `test_with_the_switch_on_and_jev_down_the_answer_keeps_file_order` (A2 lists "Jev down"; D-1:
"fail-open to file order"). The repair brief's F-4 disposition says a test whose subject is fail-open "must RUN
without graft or rg: it builds its own PATH and never depends on the host's tools". This one uses the host's tools
and skips in CI. It could run there with stand-ins (a graft that answers, an rg that prints 13 or more `path\0N:text`
lines), the pattern `test_the_stand_in_path_answers` already uses. **Finding N-5.** The lane's summary sentence ("the
fail-open and quirk tests build their own PATH") is therefore not true of this test. The Jev switch's off-by-default
test (`test_jev_is_not_called_while_its_switch_is_off`) also skips in CI (a switch test, not a fail-open one).

The vendored manifest (INFO, the coordinator's step per the JT3 brief): `python3 scripts/vendored_manifest.py --check`
on the working tree prints `FAIL: vendored manifest drift` (the `.claude/ (kit-adapted)` hash, i.e. `settings.json`,
and `hooks/search-intercept.py: committed=<missing> generated=first-party`), rc 1. Measured on the working tree:
`python3 -m pytest tests/test_vendored_manifest.py -k test_committed_manifest_matches_fresh_generation` gives
`1 failed, 55 deselected` (the drift names only JT3's two `.claude/` paths, not another lane's). The commit that lands
JT3 must regenerate `sandbox-kit/VENDORED-MANIFEST.md` in the same push, or stage0-ci goes red (AF-AP-126).

## 4. The coordinator's added suspicion: the Jev rank query's template end (switch ON)

Reproduced through the REAL hook (`/tmp/vj3r1/jevq.py`). The hook ran as a subprocess with a scratch state,
`AF_SEARCH_INTERCEPT_JEV_RANK=1`, and `AF_SEARCH_INTERCEPT_JEV_URL` pointed at a recording loopback endpoint of my own
(127.0.0.1, an OS-chosen port; it answers only `/v1/systemone`, with a valid non-tied rank reply). The real Laya server
on 47411 was never addressed. The payload is a content-mode Grep in `scripts/` whose pattern is `ROOT|` plus dummy
alternatives (the nag's classifier accepts an alternation of names; `ROOT` gives more than 12 hits, so the rerank
runs). The query the hook builds is `"Where is %s defined, and which lines show how it is used?" % pattern`
(`.claude/hooks/search-intercept.py:973`): a 55-character template around the pattern. `jev.rank` sends
`_scrub(query)[:1000]` (`scripts/jev.py:99` `_prep`, `RANK_QUERY_CHARS = 1000`):

```
pattern    4 chars: query built   59, sent   59  template tail kept=True   pattern whole=True   answer: reordered by Jev
pattern  900 chars: query built  955, sent  955  tail kept=True   pattern whole=True
pattern  944 chars: query built  999, sent  999  tail kept=True   pattern whole=True
pattern  945 chars: query built 1000, sent 1000  tail kept=True   pattern whole=True
pattern  990 chars: query built 1045, sent 1000  tail kept=False  pattern whole=True    sent ends ...'|zq0139|zq014 '
pattern 1100 chars: query built 1155, sent 1000  tail kept=False  pattern whole=False   sent ends ...'|zq0139|zq0140'
pattern 3000 chars: query built 3055, sent 1000  tail kept=False  pattern whole=False
```

**REPRODUCED (finding N-6)**, with the exact boundary. From a 946-character pattern the query's template end is cut.
From 991 characters the pattern itself is cut. The scrub changed no length here (built equals sent up to 1,000). What it
costs: Laya scores the shown hits against a question that has lost its words, or against a cut name list, so the
reorder becomes noise. It cannot add or drop a hit: the set and the cut are fixed by file order before Jev sees them
(KC-J5), and the answer still says "reordered by Jev (advisory ...)". The switch is OFF by default, the code is JT3's
(unchanged by the repair), and no clause of D-1 to D-5 or of the repair brief bounds the query. Classification:
FOLLOW-UP. Fix: bound the pattern inside the query (e.g. the first 900 characters) so the template always survives,
or skip the rerank when the query would exceed `RANK_QUERY_CHARS`.

## 5. Mutation audit (scratch copies only; `/tmp/vj3r1/mutants.py`; real hook sha256 `927410a3...` before and after both batches: SAME)

One fresh copy per mutant under `/tmp/vj3r1/mut/<id>/` (anchor asserted to occur exactly once), run through the test
file's own seam `SEARCH_INTERCEPT_UNDER_TEST`, `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`, the F-4 child-run test
deselected (its kills are the test-file mutant below). My anchors, not the lane's.

| Mutant | Mutation | pytest | Named red test(s) |
|---|---|---|---|
| A5-1 | no escape hatch (`seen_recently` returns False) | 7 failed, 80 passed | the four `test_each_shipped_rule_...[*]`, `test_semantic_grep_is_answered_once_...`, `test_the_escape_key_...`, `test_the_window_expires_and_the_record_refreshes` |
| A5-2 | intercept compound commands (the search taken after the last `&&`/`;`) | 1 failed | `test_a_compound_or_dynamic_bash_search_is_never_intercepted[cd ...]` |
| A5-3 | no size cap (`SHOW`, `MAX_ANSWER` = 10**9) | 5 failed | the two cap tests, `test_jev_is_not_called_...`, `test_the_shown_hits_are_a_prefix_...`, `test_with_the_switch_on_and_jev_down_...` |
| A5-4 | fail closed on a graft error (graft's error becomes an answer) | 1 failed | `test_a_graft_error_fails_open` |
| R1 | the Grep scope's `--hidden` dropped | 1 failed | `test_an_answer_searches_what_the_raw_call_searches` |
| R1 | names-only answered with lines (Grep default and `-l`) | 2 failed | the F-1 and F-2 tests |
| R1 | the detach exemption removed | 1 failed | `test_trailing_amp_...[detach-then-bang]` |
| T1 (test file) | the two guards dropped from `test_semantic_grep_is_answered_once_...`, in a `git archive HEAD` copy + the five boundary files + a one-commit history | no graft: 3 failed, 76 passed, 32 skipped; graft present, F-4 test only: 2 failed | that test and both `test_the_pair_passes_where_graft_or_rg_is_absent[*]` cases (control in the same copy: 78 passed, 33 skipped) |
| N-f | list-assigned variables ignored by `_amp_harm` | 2 failed | `[var]`, `[export-var]` |
| N-h | `bang` never reset after a later `&` | 1 failed | `[bang-of-later-job]` |
| N-i | `${...}` refs not collected | 1 failed | `[export-var]` |
| N-m | "and binary files" dropped from the grep -r statement | 2 failed | the F-1 and F-2 tests |
| N-p | the grep -c zeros statement dropped | 1 failed | `test_names_and_counts_are_answered_with_names_and_counts` |
| **N-a** | the Grep scope's six VCS exclusions dropped (`--hidden` kept) | 87 passed | **SURVIVES** |
| **N-b** | count mode `--count` becomes `--count-matches` | 87 passed | **SURVIVES** |
| **N-c** | every glob dropped from the rg command | 87 passed | **SURVIVES** (no test passes a glob end to end: the class of N-1) |
| **N-d** | `-i` dropped from the rg command | 87 passed | **SURVIVES** |
| **N-e** | `--type` dropped from the rg command | 87 passed | **SURVIVES** |
| **N-g** | `_closes_group` stops skipping newlines (a multi-line detach form) | 87 passed | **SURVIVES** |
| **N-j** | `grep -R`'s `--follow` dropped | 87 passed | **SURVIVES** |
| **N-k** | the binary-file note entry dropped | 87 passed | **SURVIVES** |
| **N-l** | the names-mode cut trims at `\n` instead of NUL | 87 passed | **SURVIVES** |
| N-n | the inside-the-repo guard deleted (VERIFY-JT3 V4, F-8a) | 87 passed | SURVIVES: unchanged, as issue #71 expects |
| N-o | the safe-commit rule fires on any substitution (VERIFY-JT3 G1, F-8b) | 87 passed | SURVIVES: unchanged, as issue #71 expects |

The contract's four A5 mutants and every mutant the repair brief named are killed by named tests (the lane's table
reproduces). The nine survivors marked in bold are behaviours I measured to be correct today (sections 2.2 to 2.4: `-i`,
`type`, the VCS set, line counts), or rare paths, that no test pins. N-c matters most: the only glob defect found (N-1)
sits in a code path with no test.

## 6. A1 through the installed command, the gates, and the per-call cost

Installed command (`install_session_hooks.py --target /tmp/vj3r1/inst/settings.json`: "installed 5", matcher `Grep|Bash`,
the `[ -f ... ] || exit 0; cd ... || exit 0` guard), each payload through `sh -c <command>` from cwd `/`, a fresh
scratch state each (`/tmp/vj3r1/a1.py`):

```
semantic Grep (content)          rc=2  SEARCH INTERCEPT ... | identical repeat rc=0
semantic Grep (default names)    rc=2  SEARCH INTERCEPT ...
literal-token Grep               rc=0
simple semantic rg (Bash)        rc=2  SEARCH INTERCEPT (... Bash rg command was answered ...)
compound Bash with a grep        rc=0
trailing-amp positive / near miss / the detach form           rc=2 / 0 / 0
pkill-self, safe-commit-backtick, rev-parse-two positive / near miss   rc=2 / 0 each
stdout 0 bytes on every row
```

```
$ python3 scripts/lint_delta.py --base HEAD
lint_delta (worktree vs HEAD): 2 .py changed, 0 NEW pyflakes hit(s), 0 removed
$ python3 -m pyflakes .claude/hooks/search-intercept.py tests/test_search_intercept.py tests/test_session_hooks.py   -> rc 0
$ python3 scripts/no_laya_in_gates.py            -> no_laya_in_gates: 40 files scanned, clean
$ LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <the hook, both tests, the lane's report, this report, my scratch scripts>   -> 0 each
```

Per-call cost (issue #71 F-11; `/tmp/vj3r1/cost.py`, interleaved, n=40 each, a non-matching Bash command, load 1.37):
repaired hook median 41.3 ms (p90 55.3), PIN copy 37.7 ms (p90 52.1), repaired with the off-switch file 38.7 ms. The
repair adds about 3.6 ms to every Bash and Grep call (1,080 to 1,212 lines to compile). The off switch still saves
little, because it is read after the module compiles. F-11 stands, slightly larger.

## 7. Issue #71 follow-ups (not part of this repair): did the repair change them?

A mechanical check: the source of each function behind them is byte-identical between the PIN copy and the repaired hook
(`ast` segments compared: `_pkill_args`, `_rule_pkill_self`, `_rule_safe_commit_tick`, `_rule_rev_parse_two`,
`jev_reorder`, `seen_key`, `record_seen`, `seen_recently`, `_load_seen`, `_on_alarm`, `_kill`, `graft_answer`,
`answer_search`, `decide`, `main`, `semantic_scope`, `_inside`, `nag_says_semantic`, `bash_search`, `lex`,
`_heredoc_skip`: all "identical").

- **Unchanged:** F-5 (pkill regex backtracking; code identical, not re-run), F-6 (dribbling Jev), F-7 (`record_seen`
  race), F-8a (my N-n, the inside-the-repo guard deleted, still survives), F-8b (my N-o still survives), F-8c/d, F-9
  (A10: `a &&` newline `b &` still passes), F-10, F-13 (`.claude/settings.json` untouched), and F-23 (a content answer
  still prints `Search: '...' in ..`).
- **Changed:** F-11 is slightly larger, +3.6 ms per Bash and Grep call (section 6). The off switch is still read after
  the module compiles.

Stale text outside the boundary (the coordinator's, INFO):
- `docs/INCIDENT-LOG.md:20` says JT3's live blocks included "a trailing-`&` launch (both true positives)". That launch is
  the 14:03:20 command, a NEGATIVE under the F-3 ruling: the repaired rule passes it, and `LIVE_14_03_20` in the tests
  pins `fires=False`.
- `CLAUDE.md:685` still names `graft-first-nag.py` as the PreToolUse hook that "reminds you". Once JT3 lands, the
  registered hook is `search-intercept.py`, which answers or blocks.

## 8. Evidence audit of the lane's report (JT3-R1-report.md)

| Lane claim | Checked how | Verdict |
|---|---|---|
| D-A: the premise's F-1 count drift is the brief's own text | the coordinator's ruling (brief) and the lane's attribution | consistent |
| 35 main + 18 sub narrowed fires, 1 false positive (1.9%) | my streamed re-measure with the hook's own rule (section 1) | reproduced exactly, every row re-read |
| the narrowed fires are a strict subset of the PIN rule's | repaired-not-PIN = 0 in both sets | reproduced |
| the two live 14:03 blocks no longer fire | the real hook on the verbatim commands (tests) and my replay | reproduced |
| "an answer now searches what the raw call searches" | real Grep tool and raw commands beside the hook (section 2); 85 historical answers replayed | true on every probed shape and all 85 historical answers; **false for a comma or whitespace glob (N-1)** |
| names/count answered with names/counts | fixture and real tree, all three Grep modes and grep/rg `-l`/`-c` | reproduced |
| F-4: 78 passed/33 skipped (no graft), 77/34 (neither) | my own runs (my PATH farm) | reproduced |
| "the fail-open and quirk tests build their own PATH" | the skip lists under both tool sets | **not true of `test_with_the_switch_on_and_jev_down_...` (N-5)** |
| mutant table: the brief's four and JT3's four killed | my own anchors, fresh copies (section 5) | reproduced; nine of my new mutants survive (N-7) |
| gates: lint_delta 0 new, pyflakes clean, no_laya clean, run-all rc 0 | re-run | reproduced |
| self-attack "NOT probed: .rgignore, global excludes, max file size" | probed here: `.rgignore`, `.git/info/exclude`, a 57 MB file (Grep side identical); global excludes use the same rg on both sides (not probed live: it needs a HOME change the real tool would not see) | closed except the global-excludes live probe |
| ADJ-2 `( a && job & more ) ; echo $!` would block wrongly | A01 through the real hook, plus bash | confirmed |
| DISC-1 (283 vs 485 subagent files) | `find subagents -name '*.jsonl'`: 287 now (285 less mine and the lane's); the tasks dir holds 601 entries (symlinks plus outputs), probably VERIFY-JT3's larger count | explained; counts unaffected |

## 9. Finding inventory (no severity filter)

Evidence: R = reproduced in this lane through the real hook, or through the installed command, or with the real Grep tool
as the oracle; T = re-derived from the transcripts with the hook's own functions; S = read statically (primary source).

| # | Class | Finding | Evidence | Contract mapping | Canonical path | Material effect | Reproduction | Suggested fix |
|---|---|---|---|---|---|---|---|---|
| F-1 (VERIFY-JT3) | resolved | hidden paths now searched; the defining file is listed | R, T (0 of 85 historical answers differ) | repair brief (a) | yes | - | section 2.4 | - |
| F-2 (VERIFY-JT3) | resolved | names/count answered with names/counts; counts are lines, as the tool's `-c -H` | R (fixture, real tree, all modes) | repair brief (b) | yes | - | sections 2.2, 2.3 | - |
| F-3 (VERIFY-JT3) | resolved | 1 FP in 53 (1.9%), 1 in 54 with the new fire | T, R | D-2 + the ruling | yes | - | section 1 | - |
| F-4 (VERIFY-JT3) | resolved | 0 failed under no graft and under neither; the hook is identical on 3.12 | R | A4 + repair brief F-4 | the CI tool set simulated; not on a GitHub runner | - | section 3 | - |
| **N-1** | **BLOCKER** | A Grep call whose `glob` holds a comma or whitespace outside braces is answered `rg: 0 hits.` The Grep tool splits the glob (primary source) and finds the files. | R (installed command, real hook, real Grep tool, a discriminating probe: 14 files vs "0 hits"), S (binary) | repair brief F-1 (a) "a Grep-tool answer searches what the Grep tool searches ... never assume its rules"; "The answer never shows fewer files than the raw call without saying so" | yes (the installed PreToolUse command, `sh -c`, cwd `/`) | a false absence, VERIFY-JT3 F-1's exact harm; frequency 0 of 145 historical Grep calls | `{"tool_name":"Grep","tool_input":{"pattern":"ROOT","path":"/home/user/agent-factory/scripts","glob":"*.sh,*.md"},"cwd":"/home/user/agent-factory"}` gives rc 2, `rg: 0 hits.`; the Grep tool gives 14 files | split `glob` as the tool does (whitespace, then commas unless the piece holds `{` and `}`; one `--glob` each, also for the nag's glob check), or pass through when the glob holds a comma or whitespace outside braces; add an end-to-end glob test (it also kills N-c) |
| N-2 | FOLLOW-UP | the `grep -r` statement names only ".gitignore or .ignore rules"; rg also honours `.git/info/exclude` (this tree: `.gitnexus/`), `.rgignore`, the global excludes | R (real tree: 5 `.gitnexus/*` files; fixture: `rgign/`, `exdir/`) | repair brief (a) "states exactly what it skipped" (wording) | yes | small: gitignore(5) counts `.git/info/exclude` as gitignore rules; no `.rgignore` in this tree | `grep -rl our_hooks` (pathless, cwd the repo) | name every ignore source |
| N-3 | FOLLOW-UP | `--exclude`/`--exclude-dir` with a `/`: rg matches the path, grep the base name, so the answer drops files and says nothing; `--include` with a `/` is the mirror image (more files) | R (real tree, fixture) | repair brief (a) | yes | the answer follows the caller's stated exclusion, not raw grep; 0 historical intercepted occurrences | `grep -rl --include=*.py --exclude-dir=tests/red scripted_backend tests`: 4 files vs raw 5 | pass through when an include/exclude value holds a `/`, or name it in the count line |
| N-4 | FOLLOW-UP (latent) | Read `deny` permission rules become `--iglob` exclusions in the Grep tool; the hook's rg ignores them, so with a deny rule on a tracked, non-ignored file the hook would show what the tool refuses to read | S (binary: `qZe`, `gYt`); no deny rule exists here | repair brief (a) | not reproducible without a deny rule in a settings file I may not edit (UNVERIFIED live) | none today; an exposure path if deny rules are added | - | read the deny rules the way the tool does, or pass through when any exist |
| N-5 | FOLLOW-UP (contract-mapped) | `test_with_the_switch_on_and_jev_down_the_answer_keeps_file_order` (a fail-open subject: A2 "Jev down") uses the host's tools and skips in CI | R (skip lists) | repair brief F-4: a fail-open test "must RUN without graft or rg" | the CI tool set simulated | CI does not exercise the Jev-down fallback, which sits behind an off-by-default switch; the sandbox gate runs it | `PATH=/usr/local/bin:/usr/bin:/bin` run: `SKIPPED ... :388` | stand-in graft and rg (13 or more `path\0N:text` lines), as `test_the_stand_in_path_answers` does |
| N-6 | FOLLOW-UP | switch ON: a pattern of 946 characters or more loses the rank query's template end to jev's 1,000-character cut; from 991 the pattern too | R (recording endpoint, real hook) | none | yes (switch on) | only the order of the at most 20 shown hits; the switch is off by default | section 4 | bound the pattern inside the query, or skip the rerank past `RANK_QUERY_CHARS` |
| N-7 | FOLLOW-UP | nine surviving mutants: VCS exclusions, `--count-matches`, globs dropped, `-i`, `--type`, a multi-line detach, `-R --follow`, the binary note, the names-mode cut | R | none (every contract-named mutant is killed) | n/a | untested behaviour; N-c hid N-1 | section 5 | end-to-end tests for each |
| N-8 | FOLLOW-UP | trailing-amp recall: `$!` in a heredoc (bash-confirmed), in `$( )`, F-9, a `cd` then a relative path (bash-confirmed), `%1`, `read`, the pidfile race | R | D-2 bars false positives only | yes | a missed guard; none seen in the dropped fires' results | A08-A12, A19, A24 | refs in heredoc bodies and substitutions; a `cd` in the list as a harm signal |
| N-9 | INFO | trailing-amp false positives outside the reads: A01 (ADJ-2, confirmed), A16 `${!name}`, A17/A18 a variable already set or set again; A03 `wait $!` (harm by the ruling's letter, equivalent in bash) | R | D-2 (rate unaffected: 0 in 54 reads) | yes | rare | section 1.3 | stop the scan at the enclosing `)`; skip `${!name}` |
| N-10 | INFO | the vendored manifest check fails on the working tree (JT3's two `.claude/` paths) | R (`--check` rc 1; the pytest case 1 failed) | the JT3 brief gives it to the coordinator | yes | stage0-ci red if the landing commit omits it | section 3 | regenerate in the landing commit |
| N-11 | INFO | stale text: INCIDENT-LOG:20 ("both true positives"), CLAUDE.md:685 (the nag as the PreToolUse hook) | S | none (outside the boundary) | n/a | misleading docs | section 7 | correct both when JT3 lands |
| N-12 | INFO | +3.6 ms per call (F-11 slightly larger) | R (n=40) | none | yes | cost | section 6 | F-11's fix |
| N-13 | INFO | an identifier of about 8,000 characters or more: the uncapped `graft ask` label line fills the answer, and the backstop drops graft's answer and the rg part (8,822 chars, says to repeat) | R | D-4 holds | yes | a degenerate answer; hypothetical input | 9,000-char pattern | cap the label line |
| N-14 | INFO | UTF-16 BOM files: rg decodes, raw grep cannot (more in the answer); a pathless raw rg that searched nothing exits 2 with a warning while the hook says "0 hits"; unquoted shell globs bash would expand are read literally | R | none | yes | cosmetic or in the caller's favour | section 2.3 | none needed |
| N-15 | INFO | D-I: graft's block in a names-only answer carries signatures (`def our_hooks(root: Path) -> dict`), never constant values (fixture: no fake secret in any names or count answer) | R | D-1(a) requires graft's answer | yes | none found | section 2.5 | none |
| N-16 | INFO | DISC-1 explained (287 subagent transcripts; the tasks dir holds 601 entries) | R | none | n/a | none | section 8 | none |

Reproduced vs static: everything above was run in this lane except N-4 (read from the binary; a live probe needs a
deny rule in a settings file) and the F-5/F-10 behaviour (their code is byte-identical; not re-run). Deliberately
skipped: a GitHub runner and a live block in the real harness (both outward, or they need `.jev/intercept-off`
removed); pytest under Python 3.12 (no pytest there; installing one is a third-party download); a live probe of git's
global excludes. My probes never addressed 127.0.0.1:47411; the JT2-R1 and FT1 files were never touched; no file in
the tree was written but this report.

Served model: 322 assistant records in this lane's transcript (counted before this section), all `claude-opus-5-5`; no
`"stop_reason":"refusal"`.

## 10. Gate recommendation

**NOT-READY: one finding, N-1, meets the whole blocking predicate** (reproduced through the installed command and the real
Grep tool; nothing in the recommendation rests on an unreproduced claim):
1. contract-mapped: the repair brief's F-1 disposition ("a Grep-tool answer searches what the Grep tool searches ...
   never assume its rules"; "never shows fewer files than the raw call without saying so");
2. canonical: the installed PreToolUse command through `sh -c`, beside the real Grep tool;
3. material: a false `rg: 0 hits.` where the tool finds 14 files, VERIFY-JT3 F-1's exact harm;
4. discriminator: the deterministic payload in the inventory (the no-glob reading gives 31, the split reading 14, the
   hook 0);
5. in-boundary: `.claude/hooks/search-intercept.py` (`grep_tool_search` or `run_rg`).

For the coordinator's weighing (D-031 spent this contract revision's one repair): the shape occurred in 0 of 145
historical Grep calls, and the fix is small (split the glob as the tool does, or pass it through). Everything else the
repair claimed holds:
- F-1 and F-2 answer fidelity: 0 differences in 85 historical answers, and exact on every probed shape;
- F-3: 1.9% under the ruling, re-derived row by row;
- F-4: 0 failed under both CI tool sets;
- fail-open, the 9,000 cap, the escape hatch, the off switch and the Jev default all hold;
- every contract-named mutant is killed.

If the coordinator grades N-1 as a follow-up, this lane's recommendation becomes MERGE-READY-WITH-FOLLOWUPS (N-1 to N-8),
and the landing commit must carry the vendored-manifest regeneration (N-10). Keep `.jev/intercept-off` in place until
then.
