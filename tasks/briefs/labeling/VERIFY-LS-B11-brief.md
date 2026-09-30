# VERIFY-LS-B11: attack the box before its hooks are registered (task #380; D-111, D-113, D-114)

Role: a sandbox adversarial-verifier (Opus 5.5). PIN: 69e7999 ("LS-B11 landed ..."). Do NOT spawn subagents. Return
the whole report as your final message (your hand-back); write no report file.

## WHAT LANDED

The box: a second request head in `scripts/ls_req.py`'s `parse_message` that feeds LS-B10's transport unchanged; a
stack-level `body` key in `scripts/stacks.toml` (ctx `q`, find `q`, echo `pattern`) that `scripts/stack.py` validates
and shows in `explain`. The contract: `tasks/briefs/labeling/LS-B11-brief.md`. The builder's report of record:
`tasks/briefs/labeling/LS-B11-report.md` (read its NOT DONE and DISCREPANCIES first; every claim is a hypothesis). The
hooks are NOT registered: `tasks/briefs/labeling/LS-B10-registration.patch` stays unapplied. The owner wants the box
live (D-113) and has made the labels the project's standard front door (D-114, skills `box-and-labels` and
`label-authoring`); this verify decides whether the registration may follow.

## ATTACK (report every observation; no severity filter)

1. **Premise.** Re-run the block below with `bash scripts/premise_block.sh` from `/home/user/agent-factory`; on a
   difference, stop and report CONTRACT-INVALID with the diff.
2. **The grammar against the contract (brief item 2).** Each malformed case and its exact reason. Top-edge forms: extra
   or missing spaces, a look-alike for `·`, `─` or `┌` (another code point that renders the same), tabs, trailing
   blanks, CRLF, the nonce twice or in another slot. Inside lines, the divider (two `┄`, mixed characters, trailing
   text), fences (four backquotes, `~~~`, an indented fence, a fence line inside a body), the closing rule with boxes
   and REQ lines mixed. The builder's readings D1 (a well-formed box with a non-current nonce is a stale request) and
   D2 (the fence exemption only in a message that holds a box): agree or not, and why.
3. **Run nothing it should not (D-111).** Every way to put a box's text into the runner's argument vector as more than
   one element, to set a parameter the stack does not declare, to reach a label the registry lacks, to run a stale or
   an illustration box, or to set the body parameter twice. Values with shell metacharacters, NUL, a very long value,
   look-alike keys.
4. **Run twice, or go unanswered.** A box and a REQ line with one id; the fallback path (`last_assistant_message` ahead
   of the transcript) with boxes; two Stop rounds over one message; a box split across two text blocks of one message
   while the transcript lags (the builder's NOT DONE 6); the cap, the 240 s budget and the reconciler with boxes.
5. **The REQ form unchanged (brief item 5).** Re-run the builder's differential probe from its scratch
   (`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/lsb11-lane/`) or write your own; the
   VERIFY-LS-B10 round-2 checklist (F1, F4, F6, F10) on the new bytes.
6. **Raw UTF-8.** The harness writes raw UTF-8 into the transcript; the committed fixtures write ASCII escapes. Run the
   hook-level box tests over raw-UTF-8 transcripts (the builder's probe was not committed: its NOT DONE 2).
7. **D4, the one-line body.** Measure the exact receipt a two-line body gets. A question for you, not a contract line:
   what is the smallest change to `scripts/stack.py` that lets a stack's body carry newlines while no other text
   parameter can? Propose it; do not build it.
8. **The registration with the box.** Apply `tasks/briefs/labeling/LS-B10-registration.patch` in a scratch worktree at
   the PIN and run `tests/test_ls_req.py tests/test_search_intercept.py tests/test_session_hooks.py`. Note:
   `tasks/briefs/jev-trim/K2-registration.patch` conflicts with it (VERIFY-K2 round 3, finding 6); report, do not
   rebase.
9. **Mutation.** Re-run the builder's driver, its control first (AF-AP-223: a `--basetemp` parent that no longer exists
   makes every mutant error at setup and read KILLED), and add mutants for clauses its tests may miss.
10. **The commit hook's screen tells on the landing** (advisory, printed by the pre-commit AP screen at the landing
    commit): AP-32 (hashing in edited code) in `scripts/ls_req.py` and `tests/test_ls_req.py`: is the hashed form
    exactly what the ledger holds and what a later read compares? AF-AP-175 (a quoted HEAD passed to git) in
    `tests/test_stack.py`: does any run name the ref more than once? Say for each whether it is real, with the lines.
11. **Gates at the PIN**, in your own worktree, `--basetemp` as a pytest ARGUMENT outside every work tree, counts
    pasted from `scripts/test_summary.sh` with set ids, each call under 10 minutes: `tests/test_ls_req.py
    tests/test_session_hooks.py tests/test_stack.py` (`3 files set=c3270831ad89`; the coordinator's landing gate read
    326 passed).
12. **What must hold before the registration**, and a gate recommendation under D-034's blocking predicate
    (MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID), each blocking finding with its
    reproduction command.

## STANDING RULES

- A clean detached worktree at the PIN under your scratch dir (`git worktree add --detach`, hooks off), removed at the
  end; no git write in the shared tree (a worktree add and remove is the one exception); no outward action, no PC
  bridge, no subagent.
- NEVER register the hooks: never touch `/home/user/.claude/settings.json`, the repo's `.claude/settings.json` or
  `scripts/install_session_hooks.py` in the shared tree, and never run `scripts/install_session_hooks.py`. Tests never
  touch the real `.jev/`: they set the state directory as LS-B10's tests do.
- Never read a secret file (`.pc-bridge.env`, any `*.env`, any key file); a secret in a test is a fake built at run
  time. From transcripts, read only `text` blocks, `tool_use` inputs and record types, never a thinking block; print
  only counts, bytes and ids.
- The box characters are not ASCII: build test strings in code (`chr()`), and check each written file
  (`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0).
- A long gate in ONE foreground call; stamps from `date -u`; commits cited by origin id or subject.
- Never a top-level `cd` (AF-AP-249): use `git -C`, absolute paths or a `( cd … )` subshell. Never `pkill -f` a pattern
  your own command line matches; stop every process you start, by pid.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- This is defensive testing of the owner's own tooling: each probe is a bound to measure, never an exploit.

Head the report "## VERIFY-LS-B11" with a line "Written <date -u stamp>".

## PREMISE — MEASURED at authoring (2026-09-29, sandbox main tree; PIN origin 69e7999)

Printed by `bash scripts/premise_block.sh` from the sandbox main tree. Every line reads committed objects at the PIN
(the last line prints a set id from path strings). The `[rc=1]` after `grep -c 'ls_req'` is expected: the hooks are
not registered, so the count is 0. Expected to differ: nothing; on any difference, stop and report CONTRACT-INVALID
with the diff.

```
$ git merge-base --is-ancestor 69e7999 HEAD && echo 69e7999-is-an-ancestor-of-HEAD
69e7999-is-an-ancestor-of-HEAD
$ git log -1 --format=%s 69e7999 | cut -c1-60
LS-B11 landed (task #380; GATED-PENDING-VERIFY): the box, th
$ git show 69e7999:scripts/ls_req.py | sha256sum | cut -c1-16
3f65b05429d6ae56
$ git show 69e7999:tests/test_ls_req.py | sha256sum | cut -c1-16
4154a754e8634f6a
$ git show 69e7999:scripts/stack.py | sha256sum | cut -c1-16
ef819f69430d7459
$ git show 69e7999:scripts/stacks.toml | sha256sum | cut -c1-16
05ba1573b6212e7b
$ git show 69e7999:tests/test_stack.py | sha256sum | cut -c1-16
749d679db3b2d4eb
$ git show 69e7999:scripts/stacks.toml | grep -c '^body *='
3
$ git show 69e7999:scripts/ls_req.py | grep -n '^TOP_RE\|^BOTTOM_RE\|^DIVIDER_RE\|^def parse_box\|^def parse_message\|^NONCE_LINE'
183:TOP_RE = re.compile("\u250c\u2500 ([a-z][a-z0-9-]{1,23}) \u00b7 ([a-z][a-z0-9]{0,15}) \u00b7 ([0-9a-f]{12})"
185:BOTTOM_RE = re.compile("\u2514\u2500+")
186:DIVIDER_RE = re.compile("\u2504{3,}")               # after an inside line's `│ `
216:NONCE_LINE = ("Chat form (LS-B10) nonce {n}: to run a stack without a tool call, end your message with one box per "
538:def parse_box(lines, k, top, source):
590:def parse_message(blocks, nonces, source):
$ git show 69e7999:.claude/settings.json | grep -c 'ls_req'
0
[rc=1]
$ git show 69e7999:tasks/briefs/labeling/LS-B10-registration.patch | sha256sum | cut -c1-16
ded5c249f249c372
$ bash scripts/pc_suite.sh set-id -- tests/test_ls_req.py tests/test_session_hooks.py tests/test_stack.py | tail -1
3 files set=c3270831ad89
```
