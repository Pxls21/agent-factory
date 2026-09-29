# LS-B11: the box, the chat form's labelled request (task #380, D-111, D-113)

Role: a new sandbox code-implementer lane (Opus 5.5). PIN: origin b2e1ed8. Authored 2026-09-29 by the coordinator. Read
first: D-111 and D-113 in `docs/08_DECISION_LOG.md`; the docstring of `scripts/ls_req.py` (the chat form LS-B10 built:
its grammar, receipts, Stop hook, nonce, reconciler, state); `tasks/briefs/labeling/VERIFY-LS-B10-R2-report.md` (the
coordinator note at its top, then its finding inventory: what must stay true). Do NOT spawn subagents.

## What the owner asked for (D-113, 2026-09-29 21:09:10Z, the owner's words where clear)

The coordinator showed this mock-up:

```
┌─ find · r1 · 3f9c2a7b1d04
│ q: where does the scrubber hide bearer tokens
└─
```

The owner: "this is my original design ... this is good ... the word [find] references a specific script ... you fill
out a form inside the box, and then that's what fills out the script. That way, you can use all the tools conveniently
and quickly"; "a word that represents a script that when found will trigger a script in a specific succession ... and
it will use those variables"; "So yeah as you described it". The description it confirmed: the label names a stack in
`scripts/stacks.toml`; the lines inside are the inputs, one `name: value` per line; for a text input, everything below a
dotted line (`┄┄┄`) is passed on exactly as written; one receipt per box, the result or a plain refusal, never silence;
every box and its receipt is kept as a labelled example; LS-B10's one-line form (`REQ ...`) stays as a fallback; a box
never carries a shell command or a script (D-111: the Stop hook runs outside the permission checks).

## CONTRACT

1. **Premise.** Re-run the block at the end with `bash scripts/premise_block.sh` from `/home/user/agent-factory`; on a
   difference, stop and report CONTRACT-INVALID with the diff.
2. **The box is a second request head in `parse_message`, feeding LS-B10's transport unchanged.** A box becomes a
   `Cand` of kind "request" (or "malformed") with the same nonce, id, label, params, text and sha fields, so the Stop
   hook, the duplicate-id rule, the stale-nonce rule, the cap, the budget, the receipts, the ledger, the fallback-bind
   rows and the reconciler treat it exactly as a REQ line. Its ledger row adds `form: "box"` (a REQ row `form: "req"`),
   so the export can tell the forms apart. The grammar, pinned (rejected alternatives in brackets):
   - Top edge: a line that starts `┌─ ` (U+250C, U+2500, space), then `<label> · <id> · <nonce>` (single spaces around
     each U+00B7), then optionally a space and one or more `─` (decoration); trailing blanks ignored. The label, id and
     nonce follow LS-B10's rules (`LABEL_RE`, `ID_RE`, 12 lowercase hex). [Rejected: the nonce on its own inside line;
     the owner confirmed the top edge.]
   - Inside lines: each starts with `│` (U+2502); `│ ` plus text, or a bare `│` for an empty line; trailing blanks are
     removed. First the parameters, one `key: value` per line (the key is `stack.py`'s NAME_RE; the value is the rest of
     the line after `: `, spaces allowed; each value is ONE element of the runner's argument vector, never a shell
     word). [Rejected: `key=value` inside the box; the owner reads the inside as a form.]
   - An optional divider `│ ┄┄┄` (three or more U+2504 and nothing else). Every inside line after it, up to the bottom
     edge, is the BODY: each line without its `│ ` prefix (a bare `│` gives an empty line), joined with newlines. The
     body goes to the parameter the stack names as its body (item 4). A body for a stack that names none, a second
     divider, or a parameter line that also sets the body parameter makes the box malformed.
   - Bottom edge: a line that starts `└─`, then optionally more `─`; trailing blanks ignored. No right edge.
   - Fences: a box may sit inside a fenced code block (a line of three backquotes, optionally followed by a language
     word), so the chat renders it as a box. Fence lines around and between boxes never break the closing rule.
   - Closing rule, extended: after the first request of a message (a REQ line or a box), only requests, their blocks,
     blank lines and fence lines may follow; text after them refuses every request of that message as malformed, as
     today.
   - Malformed with a current nonce, answered `refused: malformed (<why>)` with the box's id if its top edge parses,
     else `?`: a top edge that breaks the grammar; an unclosed box (no bottom edge before the message ends); an inside
     line that does not start with `│`; a parameter line with no `: `; the body cases above. A box whose top edge
     carries no current nonce is not a request (an illustration, like the mock-up above); a well-formed box with a
     non-current nonce is `refused: stale nonce`, as a REQ line is.
3. **The injected line.** `NONCE_LINE` (what the model reads every turn) names the box form with a one-box example and
   keeps the REQ form as the fallback; keep it short (it costs context every turn: paste its length before and after).
4. **A stack names its body parameter.** `scripts/stacks.toml`: a stack-level key `body = "<param>"` for each stack
   that has one free-text parameter a person would write as prose or a pattern (name your choice per stack and why);
   stacks with none name no body. `scripts/stack.py`: accept `body` in `STACK_KEYS` and validate it (it names a declared
   parameter), and show it in `explain`. No other registry change.
5. **The REQ form stays exactly as LS-B10 left it**, and every VERIFY-LS-B10 round-2 result stays true (F1, F4, F6,
   F10: the report's checklist). The ledger rows of both forms stay one per receipt.
6. **The design record.** The docstring of `scripts/ls_req.py` gets a THE BOX section beside THE GRAMMAR, and
   `docs/research/findings/labeling/LS-DESIGN-v2-2026-09-28.md` §3 gets a dated paragraph pointing to it.

## TESTS (each with a named mutant it kills; a negative control per gate, the exact error asserted)

- The grammar: a box with parameters; with a body (backquotes, a fence line, a leading space and an empty line inside
  it, all kept); inside a fence; two boxes; a box and a REQ line in one message; each malformed case of item 2, with its
  exact reason; a box with no nonce (not a request, no receipt); a stale nonce; a duplicate id across a box and a REQ
  line; a value holding spaces reaching the runner as one argument.
- Through the real hook entry, on fixture transcripts (as LS-B10's tests run `scripts/ls_req.py stop|prompt`): a box
  runs a real deterministic stack (such as `premise`) and gets a `ran` receipt with its run id; its ledger row carries
  `form: "box"`, the box's text and sha; the fallback path (`last_assistant_message` ahead of the transcript) answers a
  box once and binds its record, as for a REQ line.
- `scripts/stack.py`: a `body` that names no declared parameter is refused at load with its exact message; `explain`
  shows it.
- The hook's time on a large fixture with boxes (a bound in the test; the measured p50, p95, max in the report).

## WHERE YOU WORK

In a worktree at the PIN under your scratch directory (`git worktree add --detach <dir> b2e1ed8`, hooks off), never the
shared tree. The one file you write in the shared tree is your deliverable, `tasks/briefs/labeling/LS-B11.patch`
(`git -C <worktree> diff b2e1ed8` over every file you change, new files included), which must apply at the PIN with
`git apply --check`. Remove the worktree before you report.

## BOUNDARY

- MODIFY: `scripts/ls_req.py`, `tests/test_ls_req.py`, `scripts/stack.py` (the `body` key only),
  `scripts/stacks.toml` (the `body` lines only), `tests/test_stack.py` (the `body` tests),
  `docs/research/findings/labeling/LS-DESIGN-v2-2026-09-28.md` (item 6's paragraph).
- READ: everything else; `tasks/briefs/labeling/LS-B10-registration.patch` (never change it; say whether the box needs
  a change there, the coordinator expects none).
- NOT yours: `.claude/`, `scripts/install_session_hooks.py`, `/home/user/.claude/settings.json`, the live `.jev/`.
  Tests never touch the real `.jev/`: they set the state directory as LS-B10's tests do.
- Other lanes may run beside you: VERIFY-K2 round 3 (read-only, its own worktree) and a PC lane on the scrubber. Touch
  none of their files.

## GATES

In your worktree, `--basetemp` as a pytest ARGUMENT outside every work tree, counts pasted from `scripts/test_summary.sh`
with set ids from `bash scripts/pc_suite.sh set-id -- <files>`, each call under 10 minutes, twice: every test file that
names a file you change (`python3 scripts/stack.py gate paths="<your files>" mode=plan graph=no` lists them; re-collect
on the PIN, the coordinator states no count here), and then, with `tasks/briefs/labeling/LS-B10-registration.patch`
applied in a second scratch worktree, `tests/test_ls_req.py tests/test_search_intercept.py tests/test_session_hooks.py`.
Run your mutation driver's control first (AF-AP-223).

## REPORT

Return the whole report as your final message: the premise re-run; files with line counts and sha256; the patch's
sha256 and `git apply --check` at the PIN; per contract item its pasted evidence; the gates; the mutants; NOT done,
first-class; DISCREPANCIES; your self-attack (how could a box run twice, run something it should not, or go unanswered?).

## STANDING RULES

- No git write in the shared tree (a worktree add and remove, hooks off, is the one exception); no outward action; no
  PC bridge; never register the hooks (never run `scripts/install_session_hooks.py`).
- Never read a secret file (`.pc-bridge.env`, any `*.env`, any key file); a secret in a test is a fake built at run
  time. In any real transcript, read only `text` blocks, `tool_use` inputs and record types, never a `thinking` block,
  and print only counts, bytes and ids.
- The box characters are not ASCII: build test strings in code where the Write tool could alter them, and check each
  written file (`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0).
- Never a top-level `cd` (AF-AP-249): `git -C`, absolute paths or a `( cd … )` subshell.
- A long gate in ONE foreground call; stamps from `date -u`; commits cited by origin id or subject.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- Stop every process you start before you report; kill by pid only.

## PREMISE — MEASURED at authoring (2026-09-29, main tree; PIN origin b2e1ed8)

Printed by `bash scripts/premise_block.sh` from the main tree. Every line reads committed objects at the PIN.
`scripts/ls_req.py` is the file VERIFY-LS-B10 round 2 graded (its sha256 prefix cb4943a96f6578e5), unchanged since
03ad1b6; no stack names a body yet; the hooks are registered nowhere (each `[rc=1]` is grep's exit code for a zero
count). The set id is LS-B10's gate set (58 passed at 03ad1b6, twice, by the verifier); re-collect on the PIN.
Expected to differ: nothing.

```
$ git merge-base --is-ancestor b2e1ed8 HEAD && echo b2e1ed8-is-an-ancestor-of-HEAD
b2e1ed8-is-an-ancestor-of-HEAD
$ git show b2e1ed8:scripts/ls_req.py | sha256sum | cut -c1-16
cb4943a96f6578e5
$ git show b2e1ed8:tests/test_ls_req.py | sha256sum | cut -c1-16
64faf22cf543bc56
$ git show b2e1ed8:scripts/stack.py | sha256sum | cut -c1-16
c69a819138d21471
$ git show b2e1ed8:scripts/stacks.toml | sha256sum | cut -c1-16
6393305a0bf1a585
$ git show b2e1ed8:tests/test_stack.py | sha256sum | cut -c1-16
384253ec06482aa8
$ git diff --stat 03ad1b6 b2e1ed8 -- scripts/ls_req.py tests/test_ls_req.py | wc -l
0
$ git show b2e1ed8:scripts/ls_req.py | grep -n '^HEAD_RE\|^class Cand\|^def why_malformed\|^def parse_message\|^NONCE_LINE'
137:HEAD_RE = re.compile(r"REQ ([0-9a-f]{12}) ([a-z][a-z0-9]{0,15}) ([a-z][a-z0-9-]{1,23})((?: [^\s]+)*)")
169:NONCE_LINE = ("Chat form (LS-B10) nonce {n}: to run a stack without a tool call, end your message with request lines "
428:class Cand:
439:def why_malformed(line, nonce):
466:def parse_message(blocks, nonces, source):
$ git show b2e1ed8:scripts/stack.py | grep -n '^STACK_KEYS'
92:STACK_KEYS = {"summary", "replaces", "outward", "rated", "params", "steps", "notes"}
$ git show b2e1ed8:scripts/stacks.toml | grep -c '^\[stacks\.[a-z]*\]$'
9
$ git show b2e1ed8:scripts/stacks.toml | grep -c '^body *='
0
[rc=1]
$ git show b2e1ed8:.claude/settings.json | grep -c 'ls_req'
0
[rc=1]
$ bash scripts/pc_suite.sh set-id -- tests/test_ls_req.py | tail -1
1 files set=35c6a92807a9
```
