# JT3 report: the search intercept and the Bash quirk guard (tasks #228, #225; D-072 item 4)

Lane: code-implementer (sandbox, Opus 5.5). PIN: local HEAD db71586 (branch claude/soundbox-kit-migration-iz1jwf).
Status: DONE (tests and gates green; nothing committed). REVIEW-PENDING with the coordinator. The hook went live early
through the SessionStart installer and is held inert by `.jev/intercept-off` (section 8).

## TL;DR

- `.claude/hooks/search-intercept.py` (PreToolUse, `Grep|Bash`) answers a semantic search once (graft's answer plus
  rg's hits in FILE order, cut to fit under 9,000 characters, the cut counted) and blocks four measured Bash quirks
  once. An identical repeat within 120 s passes. It fails open on every error. The Jev reorder is behind a switch
  that is OFF, per the coordinator's 13:3xZ correction; no Jev score decides the cut.
- D-2: all four candidate rules ship, each 0 false positives on its read (80/80, 3/3, 2/2, 2/2 real). The pkill rule
  is the measured, broader form (the Bash tool's `bash -c ... eval` wrapper makes a pattern's own literal self-match).
- Gates: `87 passed` twice (set `55faf317f51d`), run-all `ALL SUITES PASSED`, lint_delta 0 new hits. A5: 6 of 6
  mutants killed, the control green.
- Flagged: the early live install (section 8), DISC-2 (A2 against D-1), the deviations (section 11), NOT-done
  (section 12).

## 1. Premise re-measured (2026-09-24T13:09:42Z, HEAD db71586)

```
$ python3 -c "import json; s=json.load(open('/home/user/.claude/settings.json')); print(s['hooks']['PreToolUse'][0]['matcher'])"
Grep
$ grep -n -A2 '"PreToolUse": \[' scripts/install_session_hooks.py
51:        "PreToolUse": [{"matcher": "Grep", "hooks": [{"type": "command", "command": guarded(
52-            ".claude/hooks/graft-first-nag.py", f"{wrap} PreToolUse -- python3 {r}/.claude/hooks/graft-first-nag.py",
53-            True)}]}],
$ grep -n 'def test_a_present_hook_keeps_its_blocking_exit' tests/test_session_hooks.py
189:def test_a_present_hook_keeps_its_blocking_exit(tmp_path):
$ timeout 60 graft ask "who calls merged in install_session_hooks" --in scripts
rc=0 ms=1981 bytes=201
```

All four match the brief's PREMISE block. The quirk-shape counts are re-measured in section 2 with the exact rules.

Drift during the lane (does not change the design): at 13:1xZ HEAD moved db71586 -> 27374ec. The push rewrote db71586 as
db34178 (same tree, `8bc6616f2c3160bdf70df31b3e1adf4126bb5dad` both), and four commits followed (aa8c1d6, 2f73abb, 8f5c295,
27374ec). Among the files I run or edit, only `.claude/hooks/turn-retro-gate.sh` and `tests/test_hooks_worktree.py` changed
(+16 lines each, the retro gate's rewrite-twin mapping); my three MODIFY files did not change.

Other facts measured before design:

```
$ git rev-parse --short HEAD HEAD~1 ; echo rc=$?       (not only inside a compound command)
fatal: Needed a single revision
rc=128
$ transcript: /root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl  665,407,277 bytes, 117,398 lines
  tool_use names: Bash 13,250 · Grep 70 · (Bash result errors: Exit code 143 x20, Exit code 144 x6)
$ graft ask "merged" --in scripts           rc 0, 5,365 ms (the first call refreshed the graph), then 1.0-1.2 s per call
$ curl 127.0.0.1:47411/health               {"ok": true, ... "calls": 20, "device": "cpu", "revision": "1c5edc17..."}
$ tr '\0' ' ' < /proc/$$/cmdline             (inside a Bash tool call: how the harness wraps every command)
/bin/bash -c source /root/.claude/shell-snapshots/snapshot-bash-....sh 2>/dev/null || true && export PYTHONPATH="." ...
  && eval 'echo MARKER_JT3_PROBE; tr '"'"'\0'"'"' ... ' && pwd -P >| /tmp/claud...
```

Read-off (verified, primary source): the Bash tool never execs a command directly. It runs it through `eval` inside a
`&&` list in one `bash -c` process, and that process's command line holds the command text (each `'` spelled
`'"'"'`). Two consequences for the design: (1) every Bash-tool command is compound at the shell level, so a
`pkill -f PAT` whose PAT matches the command's own text kills the wrapper shell even when the typed command is one
simple command; (2) the trailing-`&` quirk keeps its meaning inside `eval` (the and-or list still runs in the
background). Measured against the transcript's exit codes in section 2.

Hook context (verified from `/root/.claude/settings.json`, read only): a user-level PreToolUse hook
`$HOME/.claude/hooks/cbm-code-discovery-gate` (matcher `Grep|Glob`) also runs on every Grep. Its script says it never
blocks and only adds codebase-memory context (exit 0 always). It does not conflict with an exit-2 block. No PreToolUse
hook in this session's transcript has ever exited 2 (2 `hook_success` PreToolUse records, both exit 0), so the blocking
path's delivery is taken from the harness contract (stderr to the model on exit 2) and D-4's measured 10,000-character
swap (AF-AP-183), not from a record in this transcript.

## 2. D-2: the quirk table, measured before any rule shipped (2026-09-24T13:34:42Z)

Method (verified). `measure_quirks.py` (scratchpad) streams the transcript line by line (`for raw in fh`), keeps each Bash
`tool_use` command and joins it to its `tool_result` by id. It imports the hook's OWN rule functions from
`.claude/hooks/search-intercept.py` (`QUIRK_RULES`), so the measured rules are the shipped rules. Every text printed from
the transcript went through `transcript_export.scrub` and was cut. `recall_check.py` then streams it again and asks the
reverse question: which commands show the quirk's FAILURE in their result, and did the rule fire on them?

```
$ python3 measure_quirks.py /root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl quirk_matches.json
{ "lines": 117438, "unparsable_lines": 8, "bash_commands": 13254, "lexer_unparsed": 3,
  "matches": {"trailing-amp": 80, "pkill-self": 3, "safe-commit-backtick": 2, "rev-parse-two": 2, "pkill-v1": 2},
  "rough":   {"trailing-amp": 58, "pkill-self": 50, "safe-commit-backtick": 26, "rev-parse-two": 462} }
real 0m6.576s
```

`rough` = the authoring-time regexes (the brief's 58 / 37 / 26 / 353, re-run on the grown transcript). `pkill-v1` = the
brief's literal wording ("a compound command whose other parts name the same target"), measured beside the shipped form.

| Rule (shipped id) | Exact-rule matches | Read | Real | False positive | FP rate | Authoring regex | Ships |
|---|---|---|---|---|---|---|---|
| a `&&` list ended by `&` (`trailing-amp`) | 80 | 80 (all) | 80 | 0 | 0.0% | 58 | YES |
| `pkill -f PAT`, PAT matches the command's own text (`pkill-self`) | 3 | 3 (all) | 3 | 0 | 0.0% | 50 | YES |
| backtick inside a double-quoted `safe_commit.sh -m "..."` (`safe-commit-backtick`) | 2 | 2 (all) | 2 | 0 | 0.0% | 26 | YES |
| `git rev-parse --short` with two or more revisions (`rev-parse-two`) | 2 | 2 (all) | 2 | 0 | 0.0% | 462 | YES |
| (not shipped) the brief's literal pkill form (`pkill-v1`) | 2 | 2 (all) | 2 | 0 | 0.0% | | NO, see below |

What "real" means here (the classification rule, stated so it can be checked): a real instance is a command that holds
the quirk's shape as the CLAUDE.md line defines it, read from the parsed command; a false positive is a match where that
shape is absent (for example the `&&` and `&` sit inside quotes, a heredoc body or a `( ... )` group). Each match was read
from its rendered offending text, and the three small rules also from their result lines.

Read-off per rule:

- **trailing-amp, 80 of 80 real.** Every found list is a `&&` list at one nesting level ended by `&`. Harm is visible in
  several: #17 (2026-09-08T13:31) assigned `SP=` inside the background list, so the parent's next command read
  `head: cannot open '/m2-gate/gate.log'`; #24 and #25 (2026-09-15) ran a `bash scripts/safe_commit.sh -m ...` COMMIT
  inside the background list; #79 is today's incident (the `ignored` check's output lost); 34 of the 80 commands use
  `$!`, which is then the subshell's pid. Mechanical split: 27 of the 80 sit inside an explicit `( ... )` group (the
  `( cd $SP/priv && ... nohup ... & )` launch form, a detach on purpose: there a block costs one extra call through the
  escape hatch), 53 at the top level; 55 have more commands after the `&`. Negative controls from the hand probe: the
  rule does not fire on `(cd x && y) &`, `{ a && b; } &`, `a && b` + newline + `nohup c &`, `nohup sh -c 'a && b' &`,
  `echo 'a && b &'`, a heredoc body holding `a && b &`, or `a && b &> /dev/null`.
- **pkill-self, 3 of 3 real, all three died:** 2026-09-06T06:57 `pkill -f "while :; do :; done"`, 2026-09-14T12:29
  `pkill -f "[r]un_packs.sh"` (the CLAUDE.md incident) and 2026-09-22T05:32 `pkill -f "pc_launch.py --leg"`, each with
  result `Exit code 144`. Recall (verified): of the 50 commands with `pkill ... -f`, exactly these 3 died with exit
  143 or 144, and the rule fired on exactly these 3. The other 47 ran to completion and the rule stayed silent (their
  patterns were bracket-protected or matched nothing in the command).
- **safe-commit-backtick, 2 of 2 real:** 2026-09-06T07:47 (a raw `` `# process-scan v2.3 ...` `` span inside `-m "..."`)
  and 2026-09-15T13:09 (its result: `/bin/bash: command substitution: line 3: syntax error`). The other 24 authoring-regex
  hits all use safe forms and correctly do not fire: `-m "$(printf '...')"` (backticks inside single quotes),
  `-m "$(cat <<'EOF' ...)"` (a quoted heredoc), or an escaped `` \` `` (2026-09-14T12:58).
- **rev-parse-two, 2 of 2 real:** 2026-09-07T22:39 `git rev-parse --short origin/... HEAD` and 2026-09-07T22:57
  `git rev-parse --short HEAD origin/... 2>/dev/null` (the error hidden by the redirection: the CLAUDE.md incident). The
  only two results in the session that contain "Needed a single revision" are `sed` prints of CLAUDE.md text, not failures.

Why the shipped pkill rule is not the brief's literal wording (a flagged refinement, not a redesign): the brief's form
requires a typed compound command whose OTHER parts name the target. Primary source (section 1) shows the Bash tool runs
every command via `eval` inside a compound `bash -c` whose command line holds the command text, so the pattern's own
literal also matches that shell. The literal form (`pkill-v1`) found 2 of the 3 real self-kills and missed the
2026-09-22 `pkill -f "pc_launch.py --leg"` (rc 144), whose only other occurrence of the target was its own argument. The
shipped form is: `-f` present, no `-x`/`-v`/`-A`, and the pattern (compiled as a Python regex) matches the command text or
its `eval`-quoted spelling. Same false-positive rate (0 of 3 read), better recall (3 of 3 against 2 of 3).

Limits of this measurement (stated, not hidden): three rules rest on reads of 2-3 matches, because that is all the
session holds; the recall passes above are the larger negative-side read (47 non-dying `pkill -f` commands and 24
safe-form commit messages correctly silent). The escape hatch bounds any false positive to one extra call. 3 of 13,254
commands did not lex (an unbalanced quote or substitution); on those no rule decides anything, so they pass.

## 3. Course correction from the coordinator (received 2026-09-24 13:3xZ), applied

The coordinator's note: the first J2 result (`docs/research/findings/ap-hawk-probe/results.json`) measured Jev's per-chunk
noul reranking picking the right registry row first 5% of the time, below random (6.1%), against 59% for lexical token
overlap. D-1(a) changed, and only D-1(a): hits are ordered by FILE ORDER by default; `jev.rank` stays behind an explicit
switch that is OFF by default; when the hits exceed the size cap they are cut by the default order, the answer says how
many were cut and how to get the rest (the repeat); no Jev score decides what is dropped (KC-J5, needle loss).

What the hook now does (verified by the probe below and by the tests in section 5):

- The shown hits are always a PREFIX of file order: at most 20 (`SHOW`), and only while their lines fit the answer's
  budget (`shown_count`). The rest are cut and counted per file in a `Cut:` line that names the repeat.
- The Jev switch: the file `.jev/intercept-jev-rank-on`, or `AF_SEARCH_INTERCEPT_JEV_RANK=1`. With it on and more than 12
  hits, `jev_reorder` may reorder ONLY the hits already chosen by file order; it never sees the cut ones, so the cut set
  is identical with the switch on or off. A Jev failure keeps file order and says so.
- My own live probe before the change showed the same weakness: with Jev ranking the first 24 of 39 `Unavailable`
  hits (9.9 s), it put `class Unavailable` first, then eleven `raise` sites in no useful order.

```
$ printf '%s' '{"tool_name":"Grep","tool_input":{"pattern":"Unavailable","path":"scripts"},"cwd":"/home/user/agent-factory"}' \
    | AF_SEARCH_INTERCEPT_STATE=$ST python3 .claude/hooks/search-intercept.py      (Jev switch off: the default)
rc=2 chars=2693 ms=4834
rg: 39 hits in 1 file; the first 20 in file order:
scripts/jev.py:81: class Unavailable(Exception):
scripts/jev.py:94: raise Unavailable("the scrubber (scripts/transcript_export.py) did not import; nothing is sent")
... (18 more lines, file order)
Cut: 19 more hits after the first 20, in file order; repeat the identical call within 120 s for the raw result. By file: scripts/jev.py (19)
$ ls $ST
intercept-seen.json            (no calls.jsonl: jev was never called)
```

## 4. A1: live, through the INSTALLED command (2026-09-24T13:48:52Z)

Installed into a scratch file only (`/home/user/.claude/settings.json` untouched: still matcher `Grep`, the nag, mtime
12:35:23, read-only check at 13:49:34Z):

```
$ python3 scripts/install_session_hooks.py --target /tmp/jt3/settings.json
session hooks: installed 5 in /tmp/jt3/settings.json (live from the next tool call)
install rc=0
$ python3 scripts/install_session_hooks.py --target /tmp/jt3/settings.json --check
session hooks: present in /tmp/jt3/settings.json
check rc=0
matcher: Grep|Bash
command: [ -f /home/user/agent-factory/.claude/hooks/search-intercept.py ] && [ -f /home/user/agent-factory/scripts/hook_context.py ] || exit 0; cd /home/user/agent-factory || exit 0; python3 /home/user/agent-factory/scripts/hook_context.py PreToolUse -- python3 /home/user/agent-factory/.claude/hooks/search-intercept.py
```

Each payload below went to that command through `sh -c`, from cwd `/` (`a1.py`, scratchpad). Output as printed
(stderr lines cut at 200 characters by the printer):

```
== 1 semantic Grep 'our_hooks' in scripts (intercepted)
   rc=2 stdout=0 chars stderr=1060 chars 3430 ms
   | SEARCH INTERCEPT (search-intercept.py): this Grep call was answered here and did NOT run; repeat the identical call within 120 s for the raw result.
   | Search: 'our_hooks' in scripts.
   | graft ask 'our_hooks' --in scripts (lexical ranking; it may list near names):
   | graft ask — "our_hooks"  (lexical)
   | 1. our_hooks · function  [symbol]
   |    scripts/install_session_hooks.py:L36-L58
   |    def our_hooks(root: Path) -> dict
   | 2. pc_bridge_exec.py · file  [symbol]
   |    scripts/pc_bridge_exec.py
   | 3. _glob_structural · function  [symbol]
   |    scripts/no_laya_in_gates.py:L1265-L1288
   |    def _glob_structural(root)
   | 4. _load_screens · function  [symbol]
   |    scripts/ap_screen.py:L25-L29
   |    def _load_screens()
   | 5. _ap_screen · function  [symbol]
   |    scripts/lint_delta.py:L102-L113
   |    def _ap_screen()
   | rg: 3 hits in 1 file (all shown, file order):
   | scripts/install_session_hooks.py:36: def our_hooks(root: Path) -> dict:
   | scripts/install_session_hooks.py:70: for event in sorted(set(hooks) | set(our_hooks(root))):
   | scripts/install_session_hooks.py:73: kept += our_hooks(root).get(event, [])
== 2 the identical repeat (passes untouched)
   rc=0 stdout=0 chars stderr=0 chars 77 ms
== 3 literal-token Grep '^PROOF-STATUS: S0-0[0-9]' in todo (passes)
   rc=0 stdout=0 chars stderr=0 chars 93 ms
== 4 simple semantic rg Bash: rg -n merged scripts | head -20 (intercepted)
   rc=2 stdout=0 chars stderr=1082 chars 812 ms
   | SEARCH INTERCEPT (search-intercept.py): this Bash rg command was answered here and did NOT run; repeat the identical call within 120 s for the raw result.
   | Search: 'merged' in scripts.
   | graft ask 'merged' --in scripts (lexical ranking; it may list near names):
   | graft ask — "merged"  (lexical)
   | ... (17 more lines)
== 5 compound Bash with a grep: cd ... && grep -rn merged scripts (passes)
   rc=0 stdout=0 chars stderr=0 chars 75 ms
== 6 trailing-amp positive: 'mkdir -p /tmp/jt3x && nohup sleep 1 > /dev/null 2>&1 &' (blocked)
   rc=2 stdout=0 chars stderr=679 chars 80 ms
   | QUIRK GUARD (search-intercept.py, rule trailing-amp): this Bash command was NOT run; repeat the identical call within 120 s for the raw result.
   | Found: the list `mkdir -p /tmp/jt3x && nohup sleep 1 > /dev/null 2>& 1 &`.
   | A `&&` list ends in a trailing `&`, so the WHOLE list runs in one background subshell: its output is lost when the call returns, a step can race the next line, and `$!` is the subshell's pid, not your
   | Anchor: CLAUDE.md "A trailing `&` backgrounds the WHOLE `&&` list" (bit 2026-09-21 and 2026-09-24 12:1xZ; task #225).
   | Fix: Put the `nohup ... &` on its own line (`a && b`, then a new line `nohup c > log 2>&1 &`), or group on purpose: `(a && b) &`.
== 6 trailing-amp near miss: 'mkdir -p /tmp/jt3x\nnohup sleep 1 > /dev/null 2>&1 &' (passes)
   rc=0 stdout=0 chars stderr=0 chars 74 ms
== 6 pkill-self positive: 'pkill -f "[r]un_packs.sh"; nohup bash run_packs.sh > /dev/null 2>&1' (blocked)
   rc=2 stdout=0 chars stderr=684 chars 75 ms
   | QUIRK GUARD (search-intercept.py, rule pkill-self): this Bash command was NOT run; repeat the identical call within 120 s for the raw result.
   | Found: `pkill -f "[r]un_packs.sh"` matches its own shell's command line ('run_packs.sh').
   | The pattern matches this command's own text, and the Bash tool runs every command through `eval` inside `bash -c '... eval '<command>' ...'`: pkill matches that shell and kills it (rc 143 or 144; the 
   | Anchor: CLAUDE.md "kill by pid, never by `pkill -f` inside a compound command that also names the target" (rc 144, 2026-09-14; AF-AP-34).
   | Fix: Kill by pid: read a pidfile, or run `pgrep -f '[x]yz'` in its OWN call, then `kill <pid>`.
== 6 pkill-self near miss: 'pkill -f "[r]un_packs.sh"; echo done' (passes)
   rc=0 stdout=0 chars stderr=0 chars 88 ms
== 6 safe-commit-backtick positive: 'bash scripts/safe_commit.sh -m "fix the `foo` bug" a.py' (blocked)
   rc=2 stdout=0 chars stderr=571 chars 79 ms
   | QUIRK GUARD (search-intercept.py, rule safe-commit-backtick): this Bash command was NOT run; repeat the identical call within 120 s for the raw result.
   | Found: a backtick inside the double-quoted `safe_commit.sh -m` message.
   | Inside double quotes bash runs each `...` span as a command substitution, so the phrase vanishes from the commit message (or runs as a command).
   | Anchor: CLAUDE.md "`scripts/safe_commit.sh -m "…"`: no backticks inside a double-quoted message" (2026-09-15).
   | Fix: Single-quote the message, escape each backtick as \`, or write the message to a file.
== 6 safe-commit-backtick near miss: "bash scripts/safe_commit.sh -m 'fix the `foo` bug' a.py" (passes)
   rc=0 stdout=0 chars stderr=0 chars 83 ms
== 6 rev-parse-two positive: 'git rev-parse --short HEAD HEAD~1' (blocked)
   rc=2 stdout=0 chars stderr=444 chars 75 ms
   | QUIRK GUARD (search-intercept.py, rule rev-parse-two): this Bash command was NOT run; repeat the identical call within 120 s for the raw result.
   | Found: `git rev-parse --short` with 2 revisions.
   | `git rev-parse --short` takes ONE revision; with two it fails: fatal: Needed a single revision (rc 128).
   | Anchor: CLAUDE.md "`git rev-parse --short REV1 REV2` fails ... one rev-parse per call".
   | Fix: Run one `git rev-parse --short <rev>` per revision.
== 6 rev-parse-two near miss: 'git rev-parse --short HEAD 2>/dev/null' (passes)
   rc=0 stdout=0 chars stderr=0 chars 85 ms
== 7 many hits, Jev switch ON (env), live Laya 127.0.0.1:47411: Grep 'Unavailable' in scripts
   rc=2 stdout=0 chars stderr=2709 chars 8977 ms
   | SEARCH INTERCEPT (search-intercept.py): this Grep call was answered here and did NOT run; repeat the identical call within 120 s for the raw result.
   | Search: 'Unavailable' in scripts.
   | graft ask 'Unavailable' --in scripts (lexical ranking; it may list near names):
   | graft ask — "Unavailable"  (lexical)
   | 1. Unavailable · class  [symbol]
   |    scripts/jev.py:L81-L82
   |    class Unavailable(Exception)
   | 2. _unmapped · function  [symbol]
   |    scripts/jev_context.py:L433-L434
   |    def _unmapped(name, reason)
   | 3. _pick_device · function  [symbol]
   |    scripts/laya_systemone_server.py:L39-L55
   |    def _pick_device(requested, cuda_available, free_bytes)
   | 4. _ap_screen · function  [symbol]
   |    scripts/lint_delta.py:L102-L113
   |    def _ap_screen()
   | 5. main · function  [symbol]
   |    scripts/ooo_mcp.py:L77-L116
   |    def main()
   | rg: 39 hits in 1 file; the first 20 in file order; reordered by Jev (advisory, a switch that is off by default; 8.2 s):
   | scripts/jev.py:81: class Unavailable(Exception):
   | scripts/jev.py:259: raise Unavailable(_os_reason(e, timeout))
   | scripts/jev.py:257: raise Unavailable(_os_reason(e.reason, timeout))
   | scripts/jev.py:261: raise Unavailable("bad HTTP reply: %s" % type(e).__name__)
   | scripts/jev.py:255: raise Unavailable("HTTP %d%s" % (e.code, _detail(body)))
   | scripts/jev.py:192: raise Unavailable("the choice probabilities do not cover the labels with numbers in [0, 1]")
   | scripts/jev.py:190: raise Unavailable("the choice is not one of the labels")
   | scripts/jev.py:244: """The parsed JSON object from a loopback endpoint; Unavailable on refusal, timeout, HTTP error or non-JSON."""
   | scripts/jev.py:213: raise Unavailable("the reply answers other ids than the chunks")
   | scripts/jev.py:221: raise Unavailable("the reply answers other ids than the question")
   | scripts/jev.py:205: raise Unavailable("health is not ok")
   | scripts/jev.py:196: raise Unavailable("the score is not a finite number in range")
   | scripts/jev.py:215: raise Unavailable("no per-chunk fan-out (fan_out=%r for %d chunks)" % (reply.get("fan_out"), len(ids)))
   | scripts/jev.py:94: raise Unavailable("the scrubber (scripts/transcript_export.py) did not import; nothing is sent")
   | scripts/jev.py:265: raise Unavailable("non-JSON reply")
   | scripts/jev.py:267: raise Unavailable("the reply is not a JSON object")
   | scripts/jev.py:209: raise Unavailable("the reply has no answers")
   | scripts/jev.py:185: raise Unavailable("noul is not a finite number in [0, 1]")
   | scripts/jev.py:198: raise Unavailable("the confidence is not a finite number in [0, 1]")
   | scripts/jev.py:182: raise Unavailable("the answer is not a %s answer" % qtype)
   | ... (1 more lines)
```

Read-off (verified): the semantic Grep and the simple `rg` command were answered (rc 2, stdout empty, the answer on
stderr, first line naming the repeat); the identical repeat, the literal-token Grep and the compound command passed
untouched (rc 0, no output, 74-93 ms); every shipped rule blocked its positive (rc 2, the rule id, the found text, the
anchor and the fix) and passed its near miss (rc 0). Run 7 is the Jev switch ON against the REAL local Laya server
(127.0.0.1:47411): `jev.rank` answered in 8.2 s (its call log: `{'venue': 'local', 'cmd': 'rank', 'n_questions': 20,
'latency_ms': 8158.4, 'ok': True}`) and reordered exactly the 20 lines the default answer shows (lines 81 to 267 of
`scripts/jev.py`): the same set, another order, so the cut did not move (KC-J5). The state file the runs wrote:

```
$ stat -c '%a %U %s %n' .jev .jev/intercept-seen.json
700 root 4096 .jev
600 root 615 .jev/intercept-seen.json
7 entries; ages (s): [26, 26, 26, 26, 27, 31, 102]
```

The seven entries are this lane's: A1's six blocked calls, and one from my red run of `tests/test_session_hooks.py`
at 13:47Z, taken before I gave its shell test its own state directory. The file did not exist before the lane; I
removed it after reading it (`rm -f .jev/intercept-seen.json`). Nothing else in `.jev/` was touched.

## 5. A2: fail-open, through the INSTALLED command (2026-09-24T13:54:27Z)

The same scratch-installed command, `/bin/sh -c`, each run with its own state directory (`a2.py`, scratchpad). "Minimal
PATH" = a directory holding only `python3`, `node`, and whichever of `graft` / `rg` the case keeps:

```
== 1 graft-absent: PATH without graft
   rc=0 stdout=0 bytes stderr=0 bytes 
== 2 rg-absent: PATH without rg
   rc=0 stdout=0 bytes stderr=0 bytes 
== 2c control: the same minimal PATH with both tools
   rc=2 stdout=0 bytes stderr=1067 bytes | SEARCH INTERCEPT (search-intercept.py): this Grep call was answered here and did NOT run; repeat the identical
   | rg: 3 hits in 1 file (all shown, file order):
== 3a jev-down, switch OFF (the default): Jev is not consulted
   rc=2 stdout=0 bytes stderr=3377 bytes | SEARCH INTERCEPT (search-intercept.py): this Grep call was answered here and did NOT run; repeat the identical
   | rg: 140 hits in 28 files; the first 20 in file order:
== 3b jev-down, switch ON: file order kept, noted
   rc=2 stdout=0 bytes stderr=3436 bytes | SEARCH INTERCEPT (search-intercept.py): this Grep call was answered here and did NOT run; repeat the identical
   | rg: 140 hits in 28 files; the first 20 in file order; the Jev reorder was unavailable (url: connection refused):
== 4.0 malformed payload b''
   rc=0 stdout=0 bytes stderr=0 bytes 
== 4.1 malformed payload b'not json'
   rc=0 stdout=0 bytes stderr=0 bytes 
== 4.2 malformed payload b'[1, 2]'
   rc=0 stdout=0 bytes stderr=0 bytes 
== 4.3 malformed payload b'\xff\xfe'
   rc=0 stdout=0 bytes stderr=0 bytes 
== 4.4 malformed payload b'{"tool_name": "Grep", "tool_input": []}'
   rc=0 stdout=0 bytes stderr=0 bytes 
== 4.5 malformed payload b'{"tool_name": "Bash", "tool_input": {"co'
   rc=0 stdout=0 bytes stderr=0 bytes 
== 5a off switch: AF_SEARCH_INTERCEPT=0
   rc=0 stdout=0 bytes stderr=0 bytes 
== 5b off switch: the file <state>/intercept-off
   rc=0 stdout=0 bytes stderr=0 bytes
```

Read-off (verified): graft absent, rg absent, all six malformed payloads and both off switches exit 0 with no output;
the control (2c: the same minimal PATH with both tools) answers, so 1 and 2 are not passing for a PATH reason. The same
cases also run in `tests/test_search_intercept.py`, plus a graft ERROR (a PATH script exiting 3), a graft TIMEOUT
(graft sleeping 30 s, `GRAFT_TIMEOUT_S=1`: exit 0 with no output, and graft's pid is gone afterwards), the whole-hook
BUDGET (stdin held open: exit 0 with no output after the 2 s alarm), and a state directory that cannot be written
(exit 0: the record is written before the block, so no block without it).

**DISC-2 (flagged; brief-internal, resolved in D-1's favour, confirmed by the coordinator's 13:3xZ note): A2 lists
"Jev down" among the cases that "exit 0 with no output", while D-1 says a failed rank keeps file order.** Both cannot
hold: under A2's wording, a Jev outage would withhold every answer. The hook follows D-1 and the coordinator's
correction. With the Jev switch OFF (the default), Jev is not consulted, so its state cannot matter (3a, and
`test_jev_is_not_called_while_its_switch_is_off`: no `calls.jsonl` line is written). With the switch ON and Jev down,
the answer keeps file order and says so (3b, `test_with_the_switch_on_and_jev_down_the_answer_keeps_file_order`: the
same shown lines as 3a, one failed `rank` line in the call log). A2's literal reading would need a Jev health probe on
every search, even with the switch off, and would withhold the answer on an outage; I did not build that.

## 6. A3: every answer under 9,000 characters

Live, through the installed command (2026-09-24T13:5xZ), a search that matches thousands of lines (`self`, no path, the
whole repository):

```
rc=2 chars=5218 bytes=5264
SEARCH INTERCEPT (search-intercept.py): this Grep call was answered here and did NOT run; repeat the identical call within 120 s for the raw result.
rg: 10462 hits in 1265 files; the first 20 in file order:
Cut: 10442 more hits after the first 20, in file order; repeat the identical call within 120 s for the raw result. By file: STATUS.md (2), docs/02_COMPONENT_AUDIT.md (1), ...
```

Tests: `test_every_answer_stays_under_9000_characters_on_a_huge_synthetic_search` (5,000 hits of 400-character lines, a
50,000-character graft answer, rg's byte cap hit: the answer stays under 9,000 and says "at least 5000 hits"),
`test_a_real_search_matching_thousands_of_lines_stays_under_the_cap` (the live case above), and the budget itself:
`shown_count` shows a prefix of file order only while its lines fit what the fixed parts leave (the cut line has
1,300 characters reserved), with a backstop cut at 8,800 that the budget keeps from firing.

Two defects found and fixed on the way (verified; each has its evidence):

- **rg's parallel walk made "file order" unstable.** The first test run failed: the same search twice gave a different
  11th line (`scripts/pc_lane.sh:119` once, `scripts/pc_suite.sh:25` the next), so the shown prefix, and with it the
  cut, moved between identical calls. Fix: `rg --sort path` (183 ms against 133 ms on the whole-repo worst case).
  Test: `test_the_same_search_twice_gives_the_same_answer`; its red on the unsorted version is a race, so it is likely,
  not certain.
- **A search with no path relied on rg's stdin heuristic.** rg searches stdin instead of the cwd when stdin looks
  readable. Measured: `echo "self from stdin" | rg -c -e self` printed `1` (stdin searched); with `-- .` it searched the
  tree (1,269 files); with stdin `/dev/null`, the hook's own case, rg 14.1 searched the tree. The hook now passes `.`
  explicitly, so a heuristic change cannot turn an answer into a silent "0 hits". Defensive: no red reproduces through
  the hook on rg 14.1. The A3 test asserts that the shown lines carry the explicit `./` prefix.

## 7. A5: mutants on scratch copies (final code, 2026-09-24T14:12:05Z)

`mutants.py` (scratchpad) copies the hook into the scratchpad, applies each mutation (each anchor asserted to occur
exactly once), and runs `tests/test_search_intercept.py` against the copy through the test file's
`SEARCH_INTERCEPT_UNDER_TEST` seam (the copy runs as if it sat at the real path). The real hook's sha256 was
`a8fd4d39471cd81371bf4a5b076f118fd51670c9140d06ca7a067567677f9d9d` before and after (the gated code, section 9). M5 and
M6 are added beyond the brief's four: M5 is the coordinator's KC-J5 rule, M6 the `splitlines` defect of section 13.

| Mutant | Mutation | pytest | Red tests (named) |
|---|---|---|---|
| M0 control | none (an unmutated scratch copy) | 59 passed | none: the seam itself changes nothing |
| M1 no escape hatch | `seen_recently` returns False | 7 failed, 52 passed | `test_semantic_grep_is_answered_once_then_the_identical_repeat_passes`, `test_the_escape_key_ignores_only_the_description_label`, `test_the_window_expires_and_the_record_refreshes`, `test_each_shipped_rule_blocks_its_positive_once_and_passes_its_near_miss[` x4 rules `]` |
| M2 intercept compound commands | any operator splits segments; the first grep/rg segment is searched | 5 failed, 54 passed | `test_a_compound_or_dynamic_bash_search_is_never_intercepted[` `cd ... && grep ...`, `grep ...; echo done`, `grep ... \| grep def`, `grep ... > /tmp/out.txt`, `rg ... &` `]` (full ids from a `-rf` run of this copy) |
| M3 no size cap | `SHOW = 10**9`, `MAX_ANSWER = 10**9` | 5 failed, 54 passed | `test_every_answer_stays_under_9000_characters_on_a_huge_synthetic_search`, `test_a_real_search_matching_thousands_of_lines_stays_under_the_cap`, `test_the_shown_hits_are_a_prefix_of_file_order_and_jev_only_reorders_them`, `test_jev_is_not_called_while_its_switch_is_off`, `test_with_the_switch_on_and_jev_down_the_answer_keeps_file_order` |
| M4 fail closed on a graft error | `graft_answer` returns an error text instead of raising | 1 failed, 58 passed | `test_a_graft_error_fails_open` |
| M5 a Jev score decides the cut | Jev reorders ALL hits and the first n of its order are shown | 2 failed, 57 passed | `test_the_shown_hits_are_a_prefix_of_file_order_and_jev_only_reorders_them`, `test_with_the_switch_on_and_jev_down_the_answer_keeps_file_order` |
| M6 `splitlines` in the rg parse | the rg output split with `str.splitlines()` | 1 failed, 58 passed | `test_a_matched_line_holding_a_form_feed_stays_whole` |

Raw output (the M2 ids are cut at their first space by the script's regex):

```
== M0-control (unmutated copy)  (pytest rc=0)  59 passed in 33.48s
== M1 no escape hatch  (pytest rc=1)  7 failed, 52 passed in 26.18s
   red: test_each_shipped_rule_blocks_its_positive_once_and_passes_its_near_miss[pkill-self]
   red: test_each_shipped_rule_blocks_its_positive_once_and_passes_its_near_miss[rev-parse-two]
   red: test_each_shipped_rule_blocks_its_positive_once_and_passes_its_near_miss[safe-commit-backtick]
   red: test_each_shipped_rule_blocks_its_positive_once_and_passes_its_near_miss[trailing-amp]
   red: test_semantic_grep_is_answered_once_then_the_identical_repeat_passes
   red: test_the_escape_key_ignores_only_the_description_label
   red: test_the_window_expires_and_the_record_refreshes
== M2 intercept compound commands  (pytest rc=1)  5 failed, 54 passed in 35.59s
   red: test_a_compound_or_dynamic_bash_search_is_never_intercepted[cd
   red: test_a_compound_or_dynamic_bash_search_is_never_intercepted[grep
   red: test_a_compound_or_dynamic_bash_search_is_never_intercepted[rg
== M3 no size cap  (pytest rc=1)  5 failed, 54 passed in 24.05s
   red: test_a_real_search_matching_thousands_of_lines_stays_under_the_cap
   red: test_every_answer_stays_under_9000_characters_on_a_huge_synthetic_search
   red: test_jev_is_not_called_while_its_switch_is_off
   red: test_the_shown_hits_are_a_prefix_of_file_order_and_jev_only_reorders_them
   red: test_with_the_switch_on_and_jev_down_the_answer_keeps_file_order
== M4 fail closed on a graft error  (pytest rc=1)  1 failed, 58 passed in 25.86s
   red: test_a_graft_error_fails_open
== M5 a Jev score decides the cut (KC-J5)  (pytest rc=1)  2 failed, 57 passed in 24.89s
   red: test_the_shown_hits_are_a_prefix_of_file_order_and_jev_only_reorders_them
   red: test_with_the_switch_on_and_jev_down_the_answer_keeps_file_order
== M6 splitlines in the rg parse (AF-AP-132)  (pytest rc=1)  1 failed, 58 passed in 24.59s
   red: test_a_matched_line_holding_a_form_feed_stays_whole
real hook unchanged: yes
```

Other red-green evidence (verified, from this lane's own runs): `test_the_same_search_twice_gives_the_same_answer`'s
failure mode was observed red before `--sort path` (section 6); `test_a_graft_timeout_fails_open_and_kills_graft` was red
(20.1 s against its 15 s bound) while `graft_answer` bound `GRAFT_TIMEOUT_S` as a default argument, so the override
never reached it (fixed: limits read at call time); `test_a_matched_line_holding_a_form_feed_stays_whole` was red on the
`splitlines` parse (`[('mod.py', ...oks')]`: the text cut at the form feed) and green on the fix;
`tests/test_session_hooks.py` was red in exactly the three places that name the PreToolUse matcher or command, against
the new installer, before I edited them (section 9).

## 8. INCIDENT (flagged first-class): the hook went live before review, through the SessionStart installer

Verified from primary sources:

```
$ python3 -c "...print(json.load(open('/home/user/.claude/settings.json'))['hooks']['PreToolUse'][0]['matcher'])"
Grep|Bash
$ ls -la --time-style=+%H:%M:%S /home/user/.claude/settings.json
-rw-r--r-- 1 root root 2045 13:52:56 /home/user/.claude/settings.json          (it was 2038 bytes, 12:35:23, matcher Grep at 13:49:34Z)
$ .jev/intercept-seen.json entries after my own file was removed at ~13:50Z (key prefix, UTC):
b565d7831861d24f 14:03:20.189557Z
bdb673cbbc4e56d2 13:54:35.514961Z
dc4120ef5c6a3fa2 14:03:07.209784Z
```

What happened: `.claude/hooks/session-start.sh` runs `scripts/setup.sh` on every SessionStart, and `setup.sh:357` runs
`scripts/install_session_hooks.py` against its DEFAULT target, `/home/user/.claude/settings.json`. At 13:52:56Z a
SessionStart somewhere in this container (not a call of mine: every installer run of mine used `--target
/tmp/jt3/settings.json`) installed my working-tree installer's new PreToolUse entry. From then on every agent rooted at
`/home/user` (the coordinator and the parallel lanes) ran `search-intercept.py` on each Grep and Bash call. Each call ran
whatever version of the file was on disk at that moment. Three calls that were not mine were blocked once each (the
entries above: 13:54:35, 14:03:07, 14:03:20); the hashes do not say whose calls they were.

Live proof in the real harness (this session, 14:06Z), and the seam it reveals. The model receives the block as:

```
PreToolUse:Bash hook error: [[ -f /home/user/agent-factory/.claude/hooks/search-intercept.py ] && ... python3 /home/user/agent-factory/.claude/hooks/search-intercept.py]: QUIRK GUARD (search-intercept.py, rule trailing-amp): this Bash command was NOT run; repeat the identical call within 120 s for the raw result.
Found: the list `true && true &`.
A `&&` list ends in a trailing `&`, ...
Anchor: CLAUDE.md "A trailing `&` backgrounds the WHOLE `&&` list" (bit 2026-09-21 and 2026-09-24 12:1xZ; task #225).
Fix: Put the `nohup ... &` on its own line ...
```

The identical call, repeated with another description, ran (`not blocked`): the escape hatch works in the real harness.
The harness prepends `PreToolUse:Bash hook error: [<the whole hook command>]: ` (about 280 characters) to the hook's
stderr, so an 8,800-character answer arrives as about 9,080, still under the 10,000-character swap (AF-AP-183).

What I did: at 14:07:03Z I created the hook's own off switch, `.jev/intercept-off` (D-3), so the hook is inert again
for every agent until the coordinator's review; a fresh quirk command then ran untouched (`not blocked: the off switch
holds`). I did NOT edit `/home/user/.claude/settings.json`. To re-arm after review: `rm .jev/intercept-off`. To take the
entry out instead: `python3 scripts/install_session_hooks.py --remove`, then re-install. Until then every Bash and Grep
call still pays the wrapper's start-up cost (section 9 has the numbers).

Why it matters beyond this lane: any installer change sitting in the working tree goes live at the next SessionStart
in this container, before review. A proposed registry row for the coordinator (I cannot write `docs/INCIDENT-LOG.md`;
it is READ-only in my brief): "an uncommitted edit to a file that a SessionStart hook executes is live at the next
session start: stage installer or hook changes behind their off switch, or land them in one step with the review".

## 9. A4 and the gates (final code: hook sha256 `a8fd4d39471cd81371bf4a5b076f118fd51670c9140d06ca7a067567677f9d9d`)

Pytest set: `bash scripts/pc_suite.sh set-id -- tests/test_search_intercept.py tests/test_session_hooks.py tests/test_hooks_worktree.py`
-> `3 files set=55faf317f51d`.

```
$ mkdir -p /tmp/jt3 && rm -rf /tmp/jt3/bt          (14:15:29Z)
$ python -m pytest tests/test_search_intercept.py tests/test_session_hooks.py tests/test_hooks_worktree.py -q --basetemp /tmp/jt3/bt
87 passed in 39.85s
pytest rc=0
$ rm -rf /tmp/jt3/bt ; (the same command again)      (14:16:15Z)
87 passed in 24.42s
pytest rc=0
$ bash harness-ports/tests/run-all.sh                  (14:16:45Z)
run-all rc=0
... (18 suites, each "passed, 0 failed" or "ALL OK")
build-roles --check                OK: 3 role config layers match their sources
ALL SUITES PASSED
$ python3 scripts/lint_delta.py --base HEAD
lint_delta (worktree vs HEAD): 2 .py changed, 0 NEW pyflakes hit(s), 0 removed
lint_delta rc=0
$ python3 -m pyflakes .claude/hooks/search-intercept.py tests/test_search_intercept.py     (untracked: lint_delta cannot see them, JT1's DISC-1)
pyflakes (the two untracked new files) rc=0
$ python3 scripts/report_lint.py tasks/briefs/jev-laya/JT3-report.md --min-refs 3
report_lint: 27 refs — OK 21, NEAR 0, MISS 0, UNCHECKABLE 6, UNRESOLVED 0 (worktree)     (the 6: pasted hit lines, not claims)
```

A4 read-off: `tests/test_session_hooks.py` was red in exactly three places against the new installer before I edited it
(`test_fresh_install_registers_the_five_hooks`, `test_installed_commands_run_through_a_shell`,
`test_wrapped_commands_name_their_own_event`: `3 failed, 19 passed`), and green after. `tests/test_hooks_worktree.py` and
`run-all.sh` needed no change. Every written file: `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` printed 0 (the hook, both
tests, the installer, `.claude/settings.json`, this report).

Not a gate of mine, stated so it is not a surprise: `tests/test_vendored_manifest.py` goes red until the coordinator
regenerates the manifest (the brief assigns it). `python3 scripts/vendored_manifest.py --check` (read-only):
`FAIL: vendored manifest drift: line 20: ... .claude/ (kit-adapted) ... ac057e4a... -> 640dec06...; .claude class drift:
hooks/search-intercept.py: committed=<missing> generated=first-party`. The class-pinned tests run beside the
regeneration (AF-AP-185).

## 10. Files touched (all uncommitted; the coordinator commits)

| File | Change |
|---|---|
| `.claude/hooks/search-intercept.py` | NEW, 1,080 lines: the shell lexer; the quirk table (`_rule_trailing_amp` line 375, `_rule_pkill_self` 459, `_rule_safe_commit_tick` 483, `_rule_rev_parse_two` 498, `SHIPPED` 545); the search (`bash_search` 669, `grep_tool_search` 705, `nag_says_semantic` 717, `semantic_scope` 743, `run_rg` 786, `graft_answer` 840, `jev_reorder` 855, `shown_count` 891, `format_answer` 903); the escape hatch (`seen_key` 959, `seen_recently` 977, `record_seen` 982); `decide` 1009, `main` 1049 |
| `tests/test_search_intercept.py` | NEW, 414 lines, 59 tests |
| `scripts/install_session_hooks.py` | the PreToolUse entry (line 53: matcher `Grep\|Bash`, `search-intercept.py`, the same `guarded(..., True)` fail-open guard); the docstring sentence my change falsified |
| `tests/test_session_hooks.py` | `import os` (line 8); the matcher and command assertions (lines 92-93); the shell test's PreToolUse check with its own state dir (line 134); the fake repo's hook-script list names `search-intercept.py` (line 160) |
| `.claude/settings.json` | the repo-rooted twin (line 73: matcher `Grep\|Bash`, the same command, with a `[ -f ... ] \|\| exit 0` guard) |
| `tasks/briefs/jev-laya/JT3-report.md` | this report |

Runtime state, not code: `.jev/intercept-off` (created 14:07:03Z, section 8). Scratch only: `/tmp/jt3/`, the scratchpad
(`jt3/`: the measurement, recall, A1, A2 and mutant scripts and their outputs).

## 11. Discrepancies and deviations (each flagged)

- **DISC-1 (inherited from JT1): `lint_delta.py --base HEAD` cannot see untracked files.** Run as named, plus pyflakes
  directly on my two new files.
- **DISC-2: A2 "Jev down -> exit 0 with no output" contradicts D-1 "fail-open to file order".** Resolved for D-1 and the
  coordinator's 13:3xZ correction (section 5).
- **DEV-1: D-1(a) changed mid-lane by the coordinator (13:3xZ):** file order by default, Jev behind a switch that is off,
  the cut never decided by Jev. Implemented (section 3); M5 kills a Jev-decided cut.
- **DEV-2: the shipped pkill rule is broader than the brief's literal wording.** Measured: same 0 false positives,
  recall 3 of 3 against 2 of 3 (section 2).
- **DEV-3: the escape-hatch key leaves out the Bash `description` field** (a label, never executed); every other input
  field counts. A repeat with a new description passes (tested, and live in the real harness).
- **DEV-4: `tests/test_session_hooks.py` edits include one fixture line** (the fake repo's hook-script list, line 160):
  the brief allowed only assertions that name the PreToolUse matcher or command. Without it,
  `test_wrapped_commands_name_their_own_event` fails, because the fake repo lacks the script the PreToolUse command names.
- **DEV-5: the repo-rooted `.claude/settings.json` entry carries a fail-open guard its siblings lack.** Without it, a
  missing hook file makes `python3` exit 2 and blocks EVERY Bash call (the F-L1-2 class the installer already guards).
- **DEV-6: "simple command" also admits a stderr redirection** (`2>/dev/null`, `2>&1`); it does not change the search.
  A stdout redirection, `&`, `;`, `&&`, `||`, a pipe into anything but head/tail/wc, a variable or a substitution is
  never a search.
- **DEV-7: the search scope is this repository.** A search whose path resolves outside it passes (graft indexes nothing
  else); tested (`test_a_search_outside_the_repository_passes`).
- **DEV-8: `.jev/intercept-off` created by me** to reverse the early live install (section 8); `rm` undoes it.
- **Premise drift:** HEAD moved db71586 -> ... -> 18ba7ed during the lane (others' commits); no commit touched my three
  MODIFY files (`git log db71586..HEAD -- <them>` is empty).

## 12. NOT done (first-class)

- NOT reviewed live by the coordinator, and NOT intentionally installed: the live settings carry the new entry only
  because of the SessionStart installer (section 8); the hook is inert behind `.jev/intercept-off` until the
  coordinator decides.
- NOT written: `docs/INCIDENT-LOG.md` entries and registry rows (READ-only in my brief). Proposed: the SessionStart
  auto-install class (section 8); rg output order without `--sort` (a "first N" display that moves between identical
  runs); rg's stdin heuristic when no path is given (a silent "0 hits" risk); a module constant bound as a default
  argument (an override never reaches it); `str.splitlines()` on tool output (AF-AP-132's class).
- NOT regenerated: the vendored manifest (the coordinator's job; the drift is pasted in section 9).
- NOT committed, NOT pushed (the rules).
- NOT built: a narrower trailing-amp rule that exempts the last list inside an explicit `( ... & )` detach (27 of the
  80 matches have that form; it would need its own measurement).
- NOT measured: the quality of the Jev reorder (the switch is off; one live run proves the mechanism works, section 4).
- NOT reconciled: rg respects `.gitignore` and skips hidden files, `grep -r` does not, so an answer can omit hits a raw
  `grep -r` would print. The answer names rg; the repeat returns the raw result.
- NOT a formal `/bug-echo` run: a read-only sibling scan instead (section 13).

## 13. Adjacent defects and observations (reported, not fixed)

- `scripts/jev_context.py` (JT2's in-flight file): its `parse_rg` (lines 417-427) splits rg output with
  `out.splitlines()`, so a matched line holding `\x0c`, `\x85` or U+2028 loses its tail (the class of the M6 mutant). Its
  rg call already uses `--sort path`, explicit dirs and stdin `/dev/null`.
- The other entries of the repo-rooted `.claude/settings.json` (edit-snapshot, wiki-context, the retro gate, session
  start) have no fail-open guard: a missing script there exits 2 (latent; the installer's twin entries are guarded).
- The harness shows a PreToolUse block to the model as `PreToolUse:Bash hook error: [<the full hook command>]: <stderr>`
  (about 280 characters before the hook's text; section 8), a seam no record in this transcript held before today.
- Cost on every call: the hook's fast path (a command that is neither a search nor a quirk) measured 35.1 ms median
  alone (46.3 ms before the imports moved), and the installed command through `hook_context.py` about 111 ms median at a
  busy moment (python3 alone: 14 ms). About half of the hook's own time is Python compiling the 1,080-line script, which
  is never byte-cached when run as `__main__`; a thin entry file importing a cached module would remove it (outside my
  one-file boundary).

## 14. Self-attack: the three most likely ways this change is wrong

1. **The trailing-amp rule blocks deliberate detaches.** 27 of its 80 matches are the `( cd ... && nohup ... & )`
   launch form, where backgrounding the whole list is intended. Ruled in or out: by the brief's definition these ARE the
   shape (0 false positives read), and the cost is bounded (one extra call; the escape hatch works in the real harness,
   section 8). Residual: a nuisance rate near 1 in 3 on this session's history. The coordinator may prefer the exemption
   in section 12.
2. **An answer can mislead: fewer or other hits than the raw search.** Guarded by: the same pattern, path, glob, type and
   case flags; `--sort path` (identical answers twice, tested); an explicit `.` (no stdin guess); newline-only parsing
   (M6); every grep/rg option the hook cannot reproduce makes it pass (`-v`, `rg -r`, grep without `-r` on a directory, a
   basic-regex `|`). Every answer states "repeat the identical call for the raw result" in its first line. Residual:
   rg's ignore rules (section 12).
3. **A hook on every Bash call can break or slow everything.** Guarded by: fail-open on any exception (tested for graft
   absent, rg absent, graft error, graft timeout with graft killed, the 45 s alarm with stdin held open, malformed
   payloads, an unwritable state); the record written before the block, so a failed write never blocks; the off switch
   (used live, section 8). Measured cost in section 13. Residual: the ~14 minutes it was live before review (three
   foreign calls blocked once each, their outcomes unknown to me).

## 15. Evidence tiers

- **Verified (this lane, primary source or a probe):** the premise and its drift; the harness's `bash -c ... eval`
  wrapper; the D-2 table with its reads and the recall passes; A1 through the installed command, with a real Laya reorder;
  A2 through the installed command; A3 live and in tests; the six mutants and the control; both gate runs, run-all and
  the lint; the early live install and its reversal; the live block and the live escape hatch in the real harness; the
  fast-path timings.
- **Inferred:** the three foreign intercepts were other agents' calls (the keys are hashes); the 10,000-character swap
  applies to the text with the harness's ~280-character prefix (either way the total stays about 9,080).
- **Assumed:** Claude Code's default hook timeout is 60 s (from `scripts/hook_context.py`'s docstring, not re-measured);
  a PreToolUse payload carries `cwd` (when it does not, the hook uses its own working directory, the repo root).
