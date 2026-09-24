# VERIFY-JT3 report — the independent verify of the search intercept and the Bash quirk guard

Lane: verify-jt3 (sandbox, agent adversarial-verifier, served model claude-opus-5-5 as stated by the harness; no subagents).
Started 2026-09-24 14:53Z. Written incrementally; the final section carries the gate recommendation.

## 1. Premise (re-measured 14:53Z)

```
$ git rev-parse --short HEAD
89b908f            # brief pinned ee44b41; the only delta ee44b41..89b908f is the brief itself (1 file, 93 insertions)
$ git hash-object <the five boundary files>
c0c23042925ad8016a40980c83206026070b17a2   .claude/hooks/search-intercept.py      MATCH
3470a6e91a3f80a9f722c8a81f36d5e4cde5f34d   tests/test_search_intercept.py         MATCH
ec47d5d7cec93ea6f7e2e5ed03ac4a5aee43173b   scripts/install_session_hooks.py       MATCH
d612f704d8341e7211b5016525108312ce87817e   tests/test_session_hooks.py            MATCH
197e738a66f36952883403f6043398b901bb0ff5   .claude/settings.json                  MATCH
$ wc -l  -> 1080 / 414 / 1494 total                                                MATCH
$ git diff --stat (I, TI, S) -> 3 files changed, 16 insertions(+), 11 deletions(-) MATCH
$ bash scripts/test_summary.sh tests/test_search_intercept.py tests/test_session_hooks.py tests/test_hooks_worktree.py --basetemp /tmp/vjt3/bt
pytest-exit: 0
pytest-summary: 87 passed in 39.98s                                                MATCH (count)
$ ls -la .jev/intercept-off -> 14:07:03                                            MATCH
```

Premise: HOLDS. No CONTRACT-INVALID stop on the premise.

## 2. D-1 scope (reproduced through the real hook; scratch state dirs only)

Harness: `probe.py` in the verifier scratchpad runs `python3 .claude/hooks/search-intercept.py` with crafted payloads and
`AF_SEARCH_INTERCEPT_STATE=<scratch dir>`; canonical-path checks also go through the scratch-installed command
(`install_session_hooks.py --target <scratch>/inst/settings.json`, then `sh -c <installed command>` from cwd `/`).
Full table: `d1_scope.out` (64 shapes). Summary of what I measured (rc 2 = blocked with an answer, rc 0 = passed silently):

- Answered (rc 2): simple `grep -rn`/`rg` over code paths; `| head`, `| wc -l`, `2>/dev/null`, `2>&1 | head`; a trailing
  `# comment`; `/usr/bin/grep`, `\grep`; an absolute path inside the repo; `grep -c`/`-l`/`-o`/`rg -l` (see F-2); `-A 3`,
  `-m 1`; `-E 'a|b'`; `rg 'a|b'`; a regex dot (`our.hooks`); `grep -rn ERROR scripts` and `grep -rln PASS proofs` (literal-token
  sweeps over non-code evidence files, answered because the nag's classifier treats every path under proofs/scripts/src/... as
  code: by design of D-1, noted as INFO); the pathless `rg -n X` and `grep -rn X` (search `.`); Grep calls with a code path,
  pathless (cwd in the repo), `glob *.py`, `type py`, `output_mode count`, odd `-A/multiline/head_limit`, `path: 0`.
- Passed (rc 0, no output, 30-54 ms): every compound form (`cd ... && grep`, `;`, `|& head`, `&`, `| tee`), multi-line
  commands, a heredoc on stdin, `git grep`, `echo "grep ..."`, a comment-only command, `LC_ALL=C grep`, `timeout 5 grep`,
  grep without `-r` on a directory, a basic-regex `|`, `rg --json`, `grep -Z`, grep on a file outside the repo, `-r` over
  `/usr/lib/...`, an unexpanded shell glob (`scripts/*.py`: rg errors, fail-open), `grep -rn X .` (the nag does not call `.`
  code), Grep with `path "."`, `path docs`, a list-valued glob, a bad rg type, a pathless Grep from cwd `/home/user`.

No legitimate NON-search Bash command was blocked by the search half in this table. The quirk half is section 3.

### F-1 (the hidden-path miss): a blocked search is answered "rg: 0 hits." while the raw call would find the hits

The real Grep tool searches hidden paths; the hook's rg does not (`run_rg` passes no `--hidden`). Two instruments:

```
Grep tool (this session, hook off by the off switch):  pattern "_heredoc_delim", no path  ->  Found 1 file: .claude/hooks/search-intercept.py
grep -rl --exclude-dir=.git _heredoc_delim .           ->  ./.claude/hooks/search-intercept.py (+ its .pyc)
rg -l --sort path -e _heredoc_delim -- .  (hook flags) ->  0 files
```

Through the INSTALLED command (`sh -c`, cwd `/`, scratch state), the same Grep payload `{"pattern": "_heredoc_delim"}`:

```
rc=2 stdout=0 chars=1201
SEARCH INTERCEPT (search-intercept.py): this Grep call was answered here and did NOT run; repeat the identical call within 120 s for the raw result.
Search: '_heredoc_delim' in ..
graft ask '_heredoc_delim' (lexical ranking; it may list near names):
1. is_token_delim · function  sandbox-kit/codebase-memory-mcp/src/semantic/semantic.c ...   (five unrelated near names)
rg: 0 hits.
```

Same result for `glob *.py`, for Bash `grep -rn _heredoc_delim`, and for `_PKILL_VALUE_LONG`, `_backtick_end`. graft's card
tree does not cover `.claude/` either (`graft/` top dirs: docs, harness-ports, proofs, sandbox-kit, scripts, src, tasks,
tests), so nothing in the answer points at the real definition. The tree holds 3,101 tracked files under `.claude/` (every
hook, including H itself) and 3,080 under `.agents/`. For Bash `grep -r` the miss set is larger (rg also drops ignored files;
the builder flagged that one as NOT reconciled). The repo's untracked `.ignore` (`!graft/`) re-admits the gitignored
`graft/` card tree to rg, so pathless answers also carry graft-card lines (`./graft/scripts/install_session_hooks.md:3: ...`).

Frequency (`replay.py`, `replay.out`): every historical search H would have intercepted (main + subagent transcripts: 20
Grep calls, 85 Bash commands) replayed on today's tree with H's own `run_rg` and with the raw tool's file set (Grep tool:
rg `--hidden`, `.git` excluded; Bash grep: rg `-uu`, `.git` excluded). 1 of 105 answers differs: the JT3 builder's own
`Grep _heredoc_delim` (H shows 7 hits, the raw tool 10; the defining file `.claude/hooks/search-intercept.py` is the one
missing). No historical case gave a false "0 hits" on today's tree; the constructed pathless probes above do.

### F-2 (output widening): names-only and count-only searches are answered with full matching lines

Scratch repo `/tmp/vjt3/fakerepo` (git repo, graft built there; `.pc-bridge.env` and `secret_dir/` gitignored, one hidden dir;
every value a FAKE string `QZJ8FAKE...`/`X4Z9FAKE...`), a copy of H at `<repo>/.claude/hooks/` so ROOT is that repo:

```
raw: grep -rl FAKE_TOKEN_NAME scripts   ->  scripts/cfg.py                       (a file name only)
raw: grep -rc FAKE_TOKEN_NAME scripts   ->  scripts/cfg.py:2                     (a count only)
H:   the same two commands, and the Grep tool {"pattern": "FAKE_TOKEN_NAME", "path": "scripts"} (default output_mode
     files_with_matches): rc=2, and the answer carries   scripts/cfg.py:1: FAKE_TOKEN_NAME = "QZJ8FAKEVALUEFAKEVALUE0001"
```

So H puts line content into the model's context where the caller asked only which files match (`-l`, the Grep tool's
default mode, `output_mode count`, `grep -c`, `-o`). The same happens in this tree (`B20`, `B42` in `d1_scope.out`).

Item 6 answer (exposure): H did NOT read any file the original would not read. rg (hook flags) and graft's index both skip
gitignored and hidden files: the fake `.pc-bridge.env`, `secret_dir/cfg.py` and `.hidden_code/cfg.py` values never
appeared in any H answer, while raw `grep -rn FAKE_TOKEN_NAME` printed all three. graft's answer lists only symbols from
graft's own card tree (tracked and untracked, not ignored or hidden: 2 cards in the scratch repo). The widening is in the
OUTPUT MODE (F-2), not in the file set; the file set is narrower than the original's (F-1). graft telemetry would otherwise
fire on every answered search; `scripts/setup.sh:296` disables it and it is off in this container (`graft telemetry`:
"off — you disabled it"), INFO only.

Pathless form (item 6): in this agent's Bash tool stdin is `/dev/null` (`/proc/$$/fd/0 -> /dev/null`) and a bare
`rg -c our_hooks` searched the tree (3 files listed), so H's explicit `.` matches the raw behaviour here; the builder saw a
pipe on its stdin (a hang). Harness-dependent, INFO.

## 3. D-2 the quirk table

### 3.1 Re-derived from the transcripts (independent script `measure.py`, the hook's own rule functions, streamed)

```
                         main transcript          main, ts <= 13:34:42Z     subagent transcripts (485 files, NOT read by the builder)
Bash commands            13,496                   13,255                    16,812
trailing-amp             81                       80   (builder: 80)        31
pkill-self               3                        3    (builder: 3)         33
safe-commit-backtick     2                        2    (builder: 2)         0
rev-parse-two            2                        2    (builder: 2)         2
```

The builder's four counts reproduce exactly at its cutoff, and so does its `$!` count (34 of the 80).

### 3.2 F-3 (BLOCKER candidate): trailing-amp's 0% false-positive rate is a mirror; by harm it is 23% to 51%

The builder counted a match as "real" when it "holds the quirk's shape": only a lexer mis-parse could then count as a false
positive, so the D-2 measurement cannot fail for this rule. The anchor line in CLAUDE.md names the harm: the whole list runs
in a background subshell, so output is lost, a step races the next line, and `$!` is the subshell. Measured here:
`true && sleep 3 & B=$!` gives `$!` = the subshell (pid 14541, a bash), and `kill $B` leaves `sleep 3` alive.

Partition of the 81 main-transcript matches by what follows the offending `&` (`amp_detail` in `measure.py`, then read by hand):

| Class | Main | Subagents | Harm? |
|---|---|---|---|
| detach form `( ... && nohup X ... & )`: the `&` closes an explicit subshell group | 25 | 0 | none: all 25 are this project's lane-launch idiom `( cd $SP/priv && ... nohup bash pc_lane.sh ... > log 2>&1 & ) ; echo "launch started"`, every one rc 0 |
| `$!` used after the `&` | 34 | 17 | real: `$!` names the subshell (measured above) |
| other commands follow, no `$!` | 22 | 14 | read one by one (`amp_other_detail.out` and full-list reads): 6 main + 2 sub are real (output the caller wanted is lost: `echo ignored`, `echo "gate files: ..."`, a `grep -n` result, `id`/`ls` diagnostics; two run a `safe_commit.sh` COMMIT inside the background list, 2026-09-15 07:35 and 07:58; one assigns `SP=` inside the list and the next line prints `log $SP/...` with SP empty, 2026-09-22 18:09); 4 sub are the builder's own live probes (`true && true &`); the other 16 main + 8 sub are launch lists whose earlier steps (`cd X`, `mkdir -p D`, `SP=...` used only by the job) prepare the background job: no output lost, no race, no `$!` |

False-positive rate (a block of a command that would have run as intended):
- detach form only: 25 of 81 = 31% (main); 25 of 108 = 23% (main + subagents, probes excluded);
- detach form plus the harmless launch lists: 41 of 81 = 51% (main); 49 of 108 = 45% (both).

Either reading is far above D-2's 5% bar. Live confirmation (the ~14 minutes H was live, 13:52:56Z to 14:07:03Z, main and
subagent transcripts): the two foreign trailing-amp blocks both stopped harmless launches, and both agents paid a call to
rewrite them:

```
14:03:20 coordinator  SP=... && nohup bash scripts/lane_gate.sh ... > $SP/k170gate.log 2>&1 < /dev/null &    BLOCKED (trailing-amp)
14:03:24 coordinator  the same, split onto lines (cd // SP=... // nohup ... &)                                  ran
14:03:07 J1-1-R4 lane cd /tmp/vj11r4 && nohup python sweep_builder.py ... > log 2>&1 & // echo started           BLOCKED (trailing-amp)
14:03:10 J1-1-R4 lane cd /tmp/vj11r4 // nohup python /tmp/vj11r4/sweep_builder.py ... & // echo "pid=$!"       ran
```

The rule's Fix line ("Put the `nohup ... &` on its own line") would also turn the detach idiom's scoped `cd` into a `cd` of
the caller's shell. Canonical path: `( cd /tmp && nohup sleep 1 > /dev/null 2>&1 & )` through the hook gives rc 2
(`quirk_shapes.py` T01). Repair inside the boundary: exempt the `& )` detach form and require a harm signal (`$!` after the
`&`, or an output-producing step inside the list), or keep trailing-amp out of SHIPPED; then re-measure on the same reads.

### 3.3 Other shapes (`quirk_shapes.py`, 51 shapes, the hook's own `quirk(Parsed(...))`; semantics confirmed in bash/git/pgrep)

- Correct (no fire): `&&`/`&` inside double or single quotes, comments, heredoc bodies (`<<`, `<<-` tabs, quoted delimiter,
  a redirect after the delimiter, two heredocs on one line, a heredoc inside `$()`), `(a && b) &`, `{ a && b; } &`,
  `nohup sh -c 'a && b' &`, `&>`, `(( 1 && 2 )) &`; bracket or escaped pkill patterns, `^` anchors, `-x`, a variable
  pattern; single-quoted, escaped, `$(printf)` and quoted-heredoc commit messages; `git rev-parse` without `--short`.
- More false positives (INFO, rare): `[[ -f a && -f b ]] &` (the `&&` is inside `[[ ]]`); `a && b & wait`; a parallel
  `for ...; do a && b & done; wait`; `pkill -u nobody -f X`, `pkill --older 60 -f X`, `pkill -P <pid> -f X` (pgrep with the
  same selectors does not select the wrapper shell: measured); `git rev-parse --short HEAD --prefix sub` (git: rc 0).
- False negatives (FOLLOW-UP for T03, INFO for the rest): **T03** `cd /tmp &&` newline `nohup sleep 1 &` (bash joins them into
  one list: `x=1 &&`-newline-`x=2 &` leaves x unset, measured; the lexer resets at the newline; 0 occurrences in either
  transcript set); `a || b &` (the same backgrounding, outside the `&&` wording); `timeout 5 pkill -f X` and `sudo pkill -f X`
  (pgrep under `timeout` selects the wrapper: measured); `kill $(pgrep -f X)`; a backtick in `M="..."` then `-m "$M"`;
  **pkill patterns with `\|`**: Python's `re` reads `\|` as a literal pipe, pkill's glibc regex as alternation, so
  `pkill -f 'frame_tee\|fake_agent'` killed its own shell twice (subagents, 2026-09-06, rc 143) and the rule did not fire.
- pkill-self across all transcripts (outcome-checked, `pkill_disagreements.out`, `pkill_results.out`): 36 fires (3 main, 33 subagents);
  34 died (143/144, or SIGKILL shown as "Exit code 1" with no output after the pkill), 1 was refused by the auto-mode
  classifier (never ran), 1 survived and printed its later output (a false positive by outcome; its pattern sat only deep
  in a 33-line command). 1 of 35 known = 3%, under the bar. Recall: 34 of 36 self-kills caught (the two `\|` misses).
- safe-commit-backtick: 2/2 real (main; none in the subagents); `safe_commit.sh` refuses any first argument other than
  `-m` (`scripts/safe_commit.sh:10` `[ "${1:-}" = "-m" ]`), so the rule's shape is exact. rev-parse-two: 4/4 real: the coordinator's two
  (2026-09-07 22:39, never ran, stopped by the harness's own sleep guard; 22:57, failed silently behind `2>/dev/null`) and two
  deliberate probes that failed with rc 128 as the rule predicts (the builder's at 13:18:53, this lane's at 15:10:38).

## 4. D-3 fail-open and the worst-case wall time (`failopen.py`, `failopen.out`, `bkenets32` run)

All through the real hook, scratch state, PATH shims, fake local Jev endpoints on scratch ports (the real 47411 untouched):

```
base (Grep 'ROOT' in scripts, 140 hits)   rc=2  0.8-3.9 s   answer in file order
graft sleeps 30 s                         rc=0  20.1 s      no output (graft 20 s limit)
rg hangs                                  rc=0  10.1 s      no output (rg 10 s limit)
switch ON, Jev sleeps                     rc=2  20.8 s      file order kept, "the Jev reorder was unavailable (url: timeout after 20s)"
switch ON, Jev HTTP 500 / non-JSON / reset rc=2 ~1 s        file order kept, the reason named
switch ON, Jev VALID reply, reversed      rc=2  0.9 s       "reordered by Jev"
switch ON, graft 16-19 s + Jev sleeps     rc=2  36.9-39.9 s answer, file order
switch ON, Jev dribbles 1 byte / 5 s      rc=0  45.0 s      no output: the 45 s alarm; urllib's timeout is per read, so jev's 20 s is not a total bound
pkill -f "(a+)+b"; echo a*40              rc=0  45.0 s      no output: Python regex backtracking until the 45 s alarm (default config, switch OFF)
50 MB payload                             rc=0  0.2 s
NUL byte in cwd / 3,000-deep $( ... )     rc=0  0.0-0.1 s   (RecursionError caught)
```

Every case exits 0 with no output or 2 with an answer, no traceback, no stray stdout. Worst case provoked: 45.0 s, twice
(both inside the D-3 45 s budget, under hook_context's 55 s and Claude Code's 60 s). FOLLOW-UP F-5: the pkill rule runs a
caller-written regex over up to 200,000 characters on EVERY Bash call that holds `pkill -f`, with the switch off; a
backtracking pattern stalls that call 45 s, and every identical repeat stalls again (fail-open records nothing). Bound the
text length or the regex work. INFO F-6: with the switch on, a dribbling Jev loses the whole answer at 45 s rather than
keeping file order at 20 s.

### 4.1 The escape hatch (item 2; `escape.py`, `escape.out`, the real hook, scratch state)

```
E1 first quirk call blocked                         rc=2
E2 identical repeat passes                          rc=0
E3 a third identical call within 120 s passes       rc=0   (the record is not consumed)
E4 same command, another description                rc=0   (DEV-3: the label is not in the key)
E5 same command + a timeout parameter               rc=2   (every other input field is in the key)
E6 same command from another cwd                    rc=0   (cwd is not in the key; fail-open direction)
E7 a different command                              rc=2   (not reusable by a different command; mutant V3 kills this)
E8 a Grep call                                      rc=2   (the tool name is in the key)
E9 graft broken: fail-open, no record written; graft back: the same call is answered (rc 2): not stuck after a failure
E10 24 DIFFERENT quirk commands blocked at once against one state file: rc=2 x24, but only 15 keys survive;
    the 24 identical repeats: 15 pass, 9 are BLOCKED A SECOND TIME (their record was lost)
```

F-7 (FOLLOW-UP): `record_seen` is a read-modify-replace of one JSON file shared by every agent in the container; its
verify-after-write passes before a later writer replaces the file, so concurrent blocks lose records and a wrong
intercept can cost two calls, not the one D-1(c) promises. The window is milliseconds and blocks are rare, so the practical
rate is low. Cross-agent sharing also lets agent B's first identical call pass raw because agent A was blocked (INFO).

## 5. D-4 size, and what the model receives

- Thousands of matches: the whole-repo `self` search answered in 5,218 characters (the builder's figure; its test
  `test_a_real_search_matching_thousands_of_lines_stays_under_the_cap` passes in my runs), `ROOT` in scripts 3,370;
  a scratch repo with 2,400+ matches in 60 files whose names and lines are CJK and astral emoji, plus one 1 MB line:
  rc 2, 6,735 Python characters, 8,151 UTF-16 units, 15,703 UTF-8 bytes; the 1 MB line arrives as rg's 240-byte preview;
  "rg: at least 2136 hits" (rg's 2 MB read cap hit and counted).
- The backstop cut CAN fire (INFO F-15, a report claim corrected): with the Jev switch on, a long Jev note, a 400-character
  `Search:` line, a 50,000-character graft answer and 3,000 hits in long paths, `format_answer` returns 8,821 characters
  ending `[answer cut at 8800 characters; ...]`, so the `Cut:` line (what was cut, per file) is lost. Still under 9,000.
  With the switch off the same input gives 8,694 and keeps the `Cut:` line.
- Unit (INFO): H caps Python characters; AF-AP-183's 10,000 was read from a JavaScript binary (UTF-16 `.length`). Astral
  text counts double there; my mixed CJK/emoji fixture reached 8,151 units. No tracked path in this tree is non-ASCII
  (`git ls-files` count 0), so the risk is theoretical here.
- What the model receives on a block (primary source, the live records of 13:54:35Z and 14:03:20Z, main transcript):
  `PreToolUse:Bash hook error: [<the whole installed command>]: <stderr>`. The prefix is 344 characters with the
  installed `/home/user` command (the builder estimated about 280): an 8,800-character answer arrives as about 9,145, still
  under 10,000. The block is recorded with `is_error: true`.

## 6. The rank switch (item 7)

- Off by default: `test_jev_is_not_called_while_its_switch_is_off` green; my own run with the switch off wrote no
  `calls.jsonl`. Positive control against the REAL server (127.0.0.1:47411, health ok, never stopped), switch ON by
  environment only (the shared `.jev/intercept-jev-rank-on` was never created), scratch state:

```
switch OFF  rc=2 0.9 s   rg: 140 hits in 28 files; the first 20 in file order:
switch ON   rc=2 10.8 s  ... the first 20 in file order; reordered by Jev (advisory, a switch that is off by default; 9.9 s):
shown: off=20 on=20; same SET=True; same ORDER=False; the Cut line identical: True
```

  Jev's first pick for "Where is ROOT defined" was `scripts/fubuki_pin_sync.sh:69: echo "FUBUKI_OS_ROOT=$PIN"`, not a
  definition: consistent with the J2 result that put the switch off.
- A Jev error mid-answer (fake endpoints, section 4): timeout, HTTP 500, non-JSON, a connection reset all keep file order
  and name the reason; a VALID reply can only permute the shown hits (jev checks the id set, `scripts/jev.py:219` `set(answers) != set(ids)`, and H checks
  `sorted(ranked) == order`). A dribbling reply is the one case that loses the answer (45 s alarm, F-6).
- M5 (the builder's, re-run in section 9 with its own anchor): 2 red, the same two tests as its table; my V7 (switch
  forced on) turned `test_jev_is_not_called_while_its_switch_is_off` red; the positive control above shows the same-set
  property live.

## 7. The installer and registration (item 8)

- I (the installer) and S as committed register H on `Grep|Bash` for every session. `setup.sh:357` runs the installer
  against `/home/user/.claude/settings.json` on every SessionStart, and `.jev/` is gitignored (`.gitignore:64`), so a fresh
  container has no `intercept-off`: H is ON from the first session after the push. In THIS container it is already
  registered (live settings 13:52:56Z, matcher `Grep|Bash`, 2,045 bytes) and held off only by `.jev/intercept-off`: whoever
  removes that file turns H on for every agent at once, with the working-tree H of that moment.
- Scratch-target installer runs (`inst2/settings.json` with a foreign `Bash` entry and a `model` key): `--check` rc 1
  before, install rc 0, the old nag entry replaced, the foreign entry and other keys kept, `--check` rc 0 after, `--remove`
  leaves only the foreign entry. `/home/user/.claude/settings.json` was only read, never written.
- Every entry the installer writes carries the fail-open guard (`[ -f ... ] || exit 0; cd ... || exit 0`). In the repo-rooted
  S only the new PreToolUse entry has it. Run against a project dir whose scripts are missing, S's entries give:
  SessionStart rc 127, **UserPromptSubmit rc 2** (Claude Code blocks the prompt on exit 2), **PostToolUse rc 2**, Stop rc
  127, PreToolUse rc 0. Pre-existing, outside the lane's permitted edit of S (FOLLOW-UP F-13).
- Cost while registered but OFF (the state of this container now): every Bash and Grep call still starts two Python
  processes (section 8); the off switch saves about 1 ms (F-11).

## 8. Cost (item 9; `cost.py`, interleaved, n=40 each, 4 CPUs, load 1.13)

```
python3 -c pass                  13.7 ms median   (Python start-up)
python3 -I -S -c pass            10.3 ms
python3 compile(H) only          25.3 ms          (start-up + compiling 1,080 lines: compile is about 11.6 ms)
H with the off-switch file       35.7 ms          (the switch is read in main(), after the whole module compiled and ran)
H, a non-matching Bash command   36.7 ms          (builder: 35.1 ms)
installed command (sh + hook_context.py + H)     72.4 ms   p90 84.0 ms  (builder: ~111 ms "at a busy moment")
```

Share of H's 36.7 ms: Python start-up about 37%, compiling about 32%, module import and the decision about 31%. The
installed command adds a second Python (hook_context.py) and a shell: 72 ms on every Bash and Grep call, about 16 minutes
over this session's 13,496 main-transcript Bash calls. F-11 (FOLLOW-UP): a shell-level `[ -f .../.jev/intercept-off ] &&
exit 0` in the registered command, or a thin entry importing a byte-cached module, would remove most of it.

Unreadable cwd (item 4, the last case): H's copy in the scratch repo, run as `nobody` (`setpriv`), payload cwd a root-only
0700 directory INSIDE the hook's repo: rc 0, no output, 60 ms; the same payload as root: rc 2, answered.

## 9. Mutants (item 10; scratch copies only; the real hook's sha256 `a8fd4d39...` checked before and after every batch)

The builder's A5 table reproduced with the builder's own anchors through my runner (`builder_mutants.py`): M1 7 red,
M2 5, M3 5, M4 1, M5 2, M6 1, the same named tests as the report's table. Control (an unmutated copy): 59 passed.

My own mutants (`mutants.py`; `mutants1.out`, `mutants2.out`, `mutants3.out`):

| Id | Mutation | pytest | Named red test(s) |
|---|---|---|---|
| V1 | no explicit `.` when the search has no path | 1 failed | `test_a_real_search_matching_thousands_of_lines_stays_under_the_cap` |
| V2 | the escape key includes the description label | 1 failed | `test_the_escape_key_ignores_only_the_description_label` |
| V3 | the escape key ignores the command (a different command reuses the hatch) | 1 failed | `test_the_escape_key_ignores_only_the_description_label` |
| V4 | the inside-the-repo check deleted | **59 passed: SURVIVES** | none (F-8a) |
| V5 | the basic-regex `\|` guard removed | 1 failed | `test_a_search_this_hook_cannot_reproduce_passes[grep -rn 'our_hooks\|merged' scripts]` |
| V6 | an unknown short option ignored instead of refused | 1 failed | `test_a_search_this_hook_cannot_reproduce_passes[grep -rvn our_hooks scripts]` |
| V7 | the Jev switch ON by default | 2 failed | `test_jev_is_not_called_while_its_switch_is_off`, `test_the_same_search_twice_gives_the_same_answer` |
| V8 | the 45 s alarm exits 2 (blocks) | 1 failed | `test_the_whole_hook_budget_is_a_backstop` |
| V9 | block even when the seen record cannot be written | 1 failed | `test_a_state_that_cannot_be_written_never_blocks` |
| V10 | heredoc bodies not skipped by the lexer | 2 failed | `test_quoted_grouped_or_heredoc_text_never_fires_a_rule[cat > /tmp/jt3x.sh <<'EOF'...]`, `[git commit -m "$(cat <<'EOF'...]` |
| V11 | trailing-amp ignores an explicit `( ... )` group | 1 failed | `test_quoted_grouped_or_heredoc_text_never_fires_a_rule[(cd /tmp && nohup sleep 1 > /dev/null 2>&1) &]` |
| V12 | pkill `-A`/`-v` no longer exempt | 1 failed | `test_quoted_grouped_or_heredoc_text_never_fires_a_rule[pkill -A -f foo; echo foo]` |
| V13 | the off-switch FILE ignored | 1 failed | `test_the_off_switch_file_and_environment` |
| V14 | seen entries never pruned | 1 failed | `test_the_seen_file_is_0600_and_old_entries_are_pruned` |
| V15 | the seen file written 0644 | 1 failed | `test_the_seen_file_is_0600_and_old_entries_are_pruned` |
| G1 | safe-commit rule fires on ANY substitution (`dq_tick` -> `subst`) | **59 passed: SURVIVES** | none (F-8b) |
| G2 | git value options (`-C`, `-c`, ...) not skipped | **SURVIVES** | none (F-8c) |
| G3 | no command-length cap | **SURVIVES** | none (F-8d) |
| G4 | pkill: the eval-quoted spelling not searched | **SURVIVES** | none (F-8d) |
| G5 | the seen window's lower bound dropped (a future timestamp counts as seen) | **SURVIVES** | none (F-8d) |

14 of my 15 V-mutants are killed by named tests. F-8a (FOLLOW-UP): V4 survives because graft itself refuses an out-of-repo
`--in` (`graft ask ... --in ../../../tmp/...`: rc 1, "nothing indexed under ..."), so H fails open anyway and
`test_a_search_outside_the_repository_passes` is green for a reason other than the guard it names; it should assert graft is
never spawned. F-8b (FOLLOW-UP): G1 would block every safe `-m "$(printf ...)"` and quoted-heredoc commit message (the builder
counted 24 such commands) and no test notices: add the safe `$(...)` forms with `safe_commit.sh` to the negative list.
F-8c/d (INFO): no positive `git -C DIR rev-parse --short A B` case, no MAX_CMD, eval-spelling or clock-skew case.

## 10. F-4 (BLOCKER): the new and edited tests go red wherever graft is absent, which is CI

`stage0-ci.yml` (`tests` job, ubuntu-latest) installs only `pyflakes pytest jsonschema rfc3339-validator PyYAML` and runs
`python -m pytest tests/ -q`; nothing installs graft (setup.sh installs it in the sandbox only), and the graft index
(`graft/`) is gitignored, so a CI checkout has neither. TH has no skip guard for graft or rg (the JT2 sibling
`tests/test_jev_locate_echo.py:27` has `NEEDS_RG = pytest.mark.skipif(shutil.which("rg") is None, ...)`). Reproduced with
the contract's own pytest command and PATH without graft (rg present):

```
$ PATH=/usr/local/bin:/usr/bin:/bin python3 -m pytest tests/test_search_intercept.py tests/test_session_hooks.py -q
FAILED tests/test_search_intercept.py::test_semantic_grep_is_answered_once_then_the_identical_repeat_passes
FAILED tests/test_search_intercept.py::test_the_escape_key_ignores_only_the_description_label
FAILED tests/test_search_intercept.py::test_a_simple_rg_bash_command_is_answered
FAILED tests/test_search_intercept.py::test_a_real_search_matching_thousands_of_lines_stays_under_the_cap
FAILED tests/test_search_intercept.py::test_the_same_search_twice_gives_the_same_answer
FAILED tests/test_search_intercept.py::test_jev_is_not_called_while_its_switch_is_off
FAILED tests/test_search_intercept.py::test_with_the_switch_on_and_jev_down_the_answer_keeps_file_order
FAILED tests/test_search_intercept.py::test_rg_absent_fails_open
FAILED tests/test_search_intercept.py::test_the_minimal_path_still_answers
FAILED tests/test_session_hooks.py::test_installed_commands_run_through_a_shell
10 failed, 71 passed in 6.73s
```

Red-green discriminator on the EXISTING suite A4 names (a `git archive HEAD` copy vs the same copy with the five boundary
files, PATH without graft): HEAD `tests/test_session_hooks.py` 22 passed; with JT3's edits 1 failed, 21 passed
(`test_installed_commands_run_through_a_shell`, whose new assertion needs graft to answer). If rg is also absent on the runner
(not verified here), `_bin()` and `run_rg(shutil.which("rg"), ...)` fail at setup as well. A red `stage0-ci` makes
`push_clean.sh`'s CI gate refuse the next push (AF-AP-126). Not run on a GitHub runner (an outward action); the runner's
tool set is read from the workflow file.

### Anchors (the seams the findings rest on; line numbers read at 15:5xZ, boundary blobs unchanged)

- F-1: `.claude/hooks/search-intercept.py:794` `cmd = [rg, "--null", ...` holds no `--hidden`; the scope decision is
  `.claude/hooks/search-intercept.py:743` `def semantic_scope`.
- F-3, F-9, F-17: `.claude/hooks/search-intercept.py:375` `def _rule_trailing_amp`.
- F-5, F-10: `.claude/hooks/search-intercept.py:473` `rx = re.compile(pat.value, ...)` inside
  `.claude/hooks/search-intercept.py:459` `def _rule_pkill_self`.
- F-7, F-18: `.claude/hooks/search-intercept.py:982` `def record_seen` (read-modify-replace) and
  `.claude/hooks/search-intercept.py:959` `def seen_key`.
- F-11: `.claude/hooks/search-intercept.py:1054` `intercept-off` is read inside `main()`, after the module compiled; the
  budget alarm is `.claude/hooks/search-intercept.py:1059` `signal.alarm(HOOK_BUDGET_S)`.
- F-4: `tests/test_session_hooks.py:136` `assert r.returncode == 2 and r.stdout == ""` (needs graft);
  `.github/workflows/stage0-ci.yml:40` `pip install pyflakes pytest` (no graft) and `.github/workflows/stage0-ci.yml:46`
  `python -m pytest tests/ -q`; the sibling guard `tests/test_jev_locate_echo.py:27` `NEEDS_RG`.
- F-8a: `tests/test_search_intercept.py:168` `def test_a_search_outside_the_repository_passes`.
- F-19: `scripts/setup.sh:296` `graft telemetry disable`.

## 11. Finding inventory (no severity filter)

Evidence levels: R = reproduced in this lane through the real hook or the named production command; T = re-derived from the
transcripts with the hook's own functions; S = reviewed statically. "Canonical" = through H's real `main()` / the installed
command (or, for F-4, the contract's pytest command under the CI workflow's declared tool set).

| # | Class | Finding | Evidence | Contract | Canonical | Material effect | Reproduction | Suggested fix |
|---|---|---|---|---|---|---|---|---|
| F-1 | BLOCKER | A Grep-tool search is answered by an rg that skips hidden paths; the Grep tool itself searches them. `_heredoc_delim`: raw Grep finds `.claude/hooks/search-intercept.py`, H answers "rg: 0 hits." with five unrelated near names | R (installed cmd + Grep tool + grep -r), T (replay: 1 of 105 historical answers differs, the builder's own `_heredoc_delim` search, defining file missing) | D-1(a) "the search itself (rg with the same pattern, path and glob)"; D-1(c)'s one-call cost assumes the model can tell a wrong answer | yes | a false count/absence for any identifier under `.claude/` (every hook) or `.agents/` | `{"tool_name":"Grep","tool_input":{"pattern":"_heredoc_delim"},"cwd":"/home/user/agent-factory"}` -> rc 2, "rg: 0 hits." | for Grep calls add `--hidden --glob '!.git'` in `run_rg`; test with a hidden-dir fixture. The Bash `grep -r` half (ignored + hidden) is the builder's flagged NOT-reconciled gap: FOLLOW-UP, or say in the count line what rg skipped |
| F-2 | FOLLOW-UP | Output widening: `grep -l`/`-c`/`-o`, `rg -l`, the Grep tool's default `files_with_matches` and `count` are answered with full matching lines | R (fake-secret scratch repo: the line with `QZJ8FAKE...` shown where the raw call prints only the name/count) | none explicit | yes | line content (possibly a hardcoded secret) enters the context where only names/counts were asked | `grep -rl FAKE_TOKEN_NAME scripts` in `/tmp/vjt3/fakerepo` | honour names/counts modes (answer with the file list or the counts) |
| F-3 | BLOCKER | trailing-amp false-positive rate by harm 23% (detach form only, all transcripts) to 51% (main, with harmless launch lists); the builder's 0% counts only lexer mis-parses (a mirror) | T (`measure.py`; 81 main + 31 sub matches partitioned and read), R (T01 rc 2), live records (both foreign trailing-amp blocks, 14:03:07 and 14:03:20, stopped harmless launches) | D-2 "a rule ships only with a false-positive rate at or under 5%" | yes | blocks every `( ... && nohup ... & )` lane launch (25/25 in the main transcript) and most setup-then-launch lists; each costs a call and a rewrite | `( cd /tmp && nohup sleep 1 > /dev/null 2>&1 & )` -> rc 2 | exempt the `& )` detach form and require a harm signal (`$!` after, an output-producing step, a variable used after); re-measure on both transcript sets; or keep it out of SHIPPED |
| F-4 | BLOCKER | 9 TH tests and TI's edited shell test fail where graft is absent; CI (`stage0-ci`, `pytest tests/`) installs no graft and has no graft index; TH has no skip guard | R (contract pytest command, PATH without graft: 10 failed, 71 passed; HEAD's `test_session_hooks.py` 22 passed vs JT3 1 failed under the same PATH), S (workflow YAML, `.gitignore`) | A4 "the existing suites stay green: tests/test_session_hooks.py"; the CI gate (AF-AP-126) | reproduced under the workflow's declared tool set; not run on a GitHub runner | stage0-ci red; push_clean refuses the next push | `PATH=/usr/local/bin:/usr/bin:/bin python3 -m pytest tests/test_search_intercept.py tests/test_session_hooks.py -q` | loud skip guards (`skipif(shutil.which("graft") is None ...)`, and for rg, as JT2's `NEEDS_RG`); TI's shell test skips or accepts the nag-less path without graft |
| F-5 | FOLLOW-UP | pkill-self runs a caller-written regex over up to 200,000 characters on every `pkill -f` Bash call (switch irrelevant); a backtracking pattern stalls the call 45.0 s, and each repeat stalls again | R | D-3 budget honoured (45 s) | yes | a 45 s stall per call, then fail-open | `pkill -f "(a+)+b"; echo aaaa...(40)` -> rc 0 after 45.0 s | cap the searched text or the regex work |
| F-6 | INFO | Switch on: a dribbling Jev loses the whole answer at the 45 s alarm (urllib's timeout is per read) instead of keeping file order at 20 s | R (fake endpoint) | D-1 "fail-open to file order" (switch off by default) | yes | 45 s, no answer | `fakejev.py <port> drip` + `AF_SEARCH_INTERCEPT_JEV_RANK=1` | a total deadline around `jev.rank` |
| F-7 | FOLLOW-UP | Escape-hatch records are lost under concurrent blocks (24 at once: 15 kept; 9 repeats blocked a second time) | R (synthetic concurrency) | D-1(c) "costs one call" | yes | a second block in a millisecond race; rare | `escape.py` E10 | a lock or per-key record files |
| F-8a | FOLLOW-UP | `test_a_search_outside_the_repository_passes` survives deletion of the guard it names (graft refuses the out-of-repo `--in`) | R (V4) | test quality | n/a | a guard regression would go unseen | V4 | assert graft/rg are never spawned for an outside path |
| F-8b | FOLLOW-UP | No test of the safe `$(printf ...)`/quoted-heredoc commit forms: mutant G1 would block all of them unseen | R (G1) | test quality | n/a | a regression would block ~24 historical safe commits | G1 | add them to the negative list |
| F-8c/d | INFO | No positive `git -C DIR rev-parse --short A B`, no MAX_CMD, eval-spelling or clock-skew test (G2-G5 survive) | R | test quality | n/a | low | G2-G5 | optional |
| F-9 | FOLLOW-UP | trailing-amp misses `a &&` newline `b &` (bash backgrounds the whole list: measured) | R, T (0 occurrences) | D-2 recall (not measured by the contract) | yes | missed guard; none seen historically | T03 | join `&&`-newline before the rule |
| F-10 | FOLLOW-UP | pkill-self: `\|` read as a literal by Python, as alternation by pkill (2 real self-kills missed, rc 143); FPs for `-u`, `--older`, `-P`; FNs under `timeout`/`sudo`, `kill $(pgrep -f X)` | T, R (pgrep) | D-2 | yes | 2 of 36 self-kills missed; rare FPs | `pkill_disagreements.out`, `quirk_shapes.py` P04-P09 | translate `\|`; skip selector-restricted pkills; strip prefix commands |
| F-11 | FOLLOW-UP | Cost: 72.4 ms per Bash/Grep call through the installed command; the off switch saves ~1 ms because H compiles before `main()` reads it | R (n=40) | none | yes | ~16 min over this session's Bash calls | `cost.py` | a shell-level off-switch test in the registered command; a cached module |
| F-12 | INFO | I+S commit = H ON in every fresh container (`.jev/` gitignored); in this container H is already registered and held only by `.jev/intercept-off` | S, R (installer on scratch targets) | brief item 8 | n/a | rollout decision for the coordinator | section 7 | re-arm deliberately after the repair |
| F-13 | FOLLOW-UP | Repo-rooted S: SessionStart/UserPromptSubmit/PostToolUse/Stop have no fail-open guard; a missing script gives rc 2 on UserPromptSubmit (blocks the prompt) and PostToolUse | R (scratch project dir) | pre-existing; outside the lane's permitted S edit | yes | latent | section 7 | the installer's `[ -f ] || exit 0` guard on every S entry |
| F-14 | INFO | The harness prefix on a block is 344 characters (report: ~280); 8,800 arrives as ~9,145 < 10,000 | T (live records) | D-4 | yes | none | section 5 | correct the report |
| F-15 | INFO | The 8,800 backstop can fire (switch on, long Jev note): the `Cut:` line is lost; 8,821 < 9,000 | R (`format_answer`) | D-4 holds | yes | a lost cut count, corner case | section 5 | reserve the note in the budget |
| F-16 | INFO | Reach: the Bash search half would have answered 7 of 13,496 main and 78 of 16,812 subagent Bash commands; Grep 20 of 134 calls; most greps are compound (`cd ... && grep`) and pass by contract | T | D-1 by design | n/a | value, not correctness | `measure.out` | none required |
| F-17 | INFO | More trailing-amp FPs: `[[ a && b ]] &`, `a && b & wait`, `for ...; do a && b & done; wait`; rev-parse `--prefix` | R | D-2 | yes | rare | `quirk_shapes.out` | with F-3 |
| F-18 | INFO | The escape key excludes cwd and session (shared by all agents); any other parameter change re-blocks | R | D-1(c) | yes | fail-open direction | `escape.out` E5/E6 | none required |
| F-19 | INFO | graft telemetry would run on every answered search; `setup.sh:296` disables it (off here) | S, R | none | n/a | none while setup runs | `graft telemetry` | keep |
| F-20 | INFO | The VERIFY brief's item-4 wording (every case exit 0) repeats DISC-2 for Jev down with the switch on; graded against D-1 as corrected (exit 2, file order) | S | D-1 vs A2 | n/a | none | section 4 | none |
| F-21 | INFO | AP-screen tells on H (env read once in `main`, PATH-resolved graft/rg, `signal.signal` before `try`, the `_kill` swallow): none is a defect here (the alarm handler exits, it does not raise; graft/rg answers are not a trust decision) | S | none | n/a | none | `scripts/ap_screen.py` | none |
| F-22 | INFO | The builder's D-2 read covered only the main transcript; the 485 subagent transcripts add 31 trailing-amp and 33 pkill-self matches; pkill-self stays under 5% (1 of 35) | T | D-2 | n/a | evidence gap filled | `measure.out` | none |
| F-23 | INFO | The `Search:` line prints `in ..` for a pathless search (cosmetic) | R | none | yes | none | G02 | print `.` once |

Reproduced vs static: everything in sections 2-10 was run in this lane except where marked S. Deliberately skipped: a GitHub
runner (an outward action); a live block in the real harness (it would need `.jev/intercept-off` removed: forbidden; the
live transcript records stand in); graft index races under concurrent `graft ask` (UNVERIFIED); Jev ranking quality (out of
scope; the switch is off); JT2's and J1-1-R4's files (never touched). My V7 mutant runs sent two rank calls to the real
local Laya server (127.0.0.1:47411, default URL inside the tests' own state dirs); the server was never stopped.

## 12. Gate recommendation

**NOT-READY** — three findings meet the whole blocking predicate:

- **F-4** (strongest): TH and TI's edited shell test require graft (and rg) with no skip guard; CI installs neither. Reproduced
  with the contract's pytest command under the workflow's tool set; not run on a GitHub runner.
- **F-3**: trailing-amp blocks correct commands at 23-51% against D-2's 5% bar, confirmed by both live foreign blocks. This
  depends on reading D-2's "false positive" as "a block of a command that would have run as intended"; under the builder's
  reading (a lexer mis-parse only) the rate is 0% by construction, and F-3 would drop to FOLLOW-UP.
- **F-1**: Grep-tool answers omit hidden paths and can say "rg: 0 hits." for code that exists. Its contract mapping (D-1(a)
  "the search itself") is the weakest of the three; if the coordinator reads D-1(a) as "rg defaults", F-1 drops to FOLLOW-UP.

All three sit inside the boundary (H, TH, TI) and fit one focused repair: loud graft/rg skip guards in TH and TI; `--hidden
--glob '!.git'` for Grep-tool searches plus a hidden-dir test; trailing-amp narrowed (the `& )` detach exempt, a harm
signal required) and re-measured on both transcript sets, or kept out of SHIPPED. If the coordinator downgrades F-3 and F-1,
the remaining blocker is F-4 alone; with F-4 repaired the lane would be MERGE-READY-WITH-FOLLOWUPS. Keep `.jev/intercept-off`
in place until the repair's verify: the live registration is already in this container.

Model: every one of this lane's 347 assistant records (counted at 15:5xZ) was served by `claude-opus-5-5`; no refusal stop.
