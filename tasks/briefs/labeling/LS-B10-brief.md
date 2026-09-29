# LS-B10: the chat form (T2): labeled request lines in the coordinator's chat, run through the stack runner, one receipt per request (task #364, D-108)

Role: a new sandbox code-implementer lane (Opus 5.5). Authored 2026-09-29 10:5xZ by the coordinator. Read first: D-108's row
in `docs/08_DECISION_LOG.md`; `docs/research/findings/labeling/LS-DESIGN-v2-2026-09-28.md` §2 to §4 (the stack runner
this lane fronts); `tasks/briefs/labeling/LS-PREMORTEM-report.md` §A (P1 to P8) and its gate recommendation (transport
list A is your checklist).

## What the owner asked for (D-108 item 6, the owner's words where clear)

"The reason I wanted it in chat form is so that you don't make any tool calls. And Jev detects that and makes the tool
calls. You can do a hybrid setup where you can build scripts that Jev runs. But Jev detects it directly in the chat as a
form so that it's labeled. The whole point is to label the ... chat." Jev "is not a generative model. So it just
determines which script to be run ... We develop the scripts ... Jev detects the chat where it needs it called ... in the
future, it'll determine it implicitly ... for now, during training, we will label everything properly ... once we have
that data, we can train a model to do that without needing the output styles." On a dropped request: "I don't think it
will drop anything silently ... everything is segmented and labeled ... whatever's inside the box, you can write the
command or the quote or the prompt ... It will just copy that. It will be like a script."

What that means for this build:
- The coordinator writes a labeled form in its chat. A detector matches the label and runs the named script with the
  form's values, and the result comes back to the coordinator. The coordinator makes no tool call for it.
- The detector is lexical now: an exact grammar. A trained model may replace the detector later, reading the same
  labeled chat. So the grammar is also a labeling scheme, and every request, its place in the chat and its result are
  stored so they can become training pairs.
- The scripts stay ours: a label names a stack in `scripts/stacks.toml`, run by `scripts/stack.py` (LS-B9, landed and
  verified). This lane adds the chat transport, not new instruments. The tool-call form (T1,
  `python3 scripts/stack.py <label> ...`) stays as it is.

## Why receipts

Labeling makes a request unambiguous; the TRANSPORT can still miss one. A Stop hook's own input carries only the final
message's last text block (PM P3a), a thinking-only final message has none (P3b), and no Stop hook runs on an interrupt
or an API error (P3d). `stop_hook_active` stays true for the rest of a user turn (P1). The harness counts consecutive
blocking Stops with no tool call between them, resets that count at every tool round, and above
`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` (default 8) ends the turn and drops the pending feedback (P2). So every request gets a
receipt, and a reconciler reports any request that got none. "Nothing drops silently" becomes a measured property.

## CONTRACT

1. **The grammar.** One request per line: `REQ <nonce> <id> <label> key=value ...`. `<nonce>` is this turn's nonce;
   `<id>` is unique within the turn (`r1`, `r2`, ...); `<label>` names a stack; the parameters are the stack runner's
   own. A long value (a command, a quote, a prompt: "whatever's inside the box") goes in a block after its request line;
   define the block syntax (a heredoc-style form such as `q=<<Q1` ... `Q1`, whose end word the writer picks, is the
   direction). It must carry any text, backquotes and fences included, verbatim, and never reach a shell. Request lines
   and their blocks close the final text of the message (PM P3's change); text after them is refused as malformed.
2. **The nonce.** A UserPromptSubmit hook mints a fresh nonce per user prompt, keeps the turn's valid set (PM list A),
   and injects ONE line: the nonce and the grammar in a sentence. No nonce injected this turn means the chat form is off,
   and the coordinator uses tool calls (P13). A REQ line with an old or unknown nonce never runs: its receipt says
   `refused: stale nonce`. The current nonce anywhere in the text (a code fence, bold, a line over 200 characters, a
   non-breaking space) is intent: parse it, or answer `refused: malformed` (P3c).
3. **The Stop hook.** On Stop (the main thread only; register nothing on SubagentStop), collect every REQ line with the
   current nonce from EVERY assistant text block since the user prompt, read from the transcript at `transcript_path`,
   not only from `last_assistant_message` (closes P3a, and P3b where an earlier block holds the lines). Never read a
   `thinking` block. The transcript is large (this session's passed 800 MB at authoring): read from a stored byte offset
   per session, never the whole file, and measure the hook's own time (p50, p95, max) on a copy of a real transcript's
   tail. Run each unanswered request through `scripts/stack.py` as an argument vector, never a shell, under a wall budget
   you state (the direction: about 240 s per round, under a registration `timeout` of 300 s; requests past the budget get
   `refused: budget`). Return the receipts as the hook's blocking feedback (exit 2 with the text on stderr: the channel
   `.claude/hooks/turn-retro-gate.sh` uses, proven in this session), so the coordinator continues with them. Never key
   execution on `stop_hook_active` (P1). Count consecutive blocking rounds with no tool call between them, reset from the
   transcript (a `tool_use` record after the last receipt resets it); read `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` (default 8);
   at cap-1, refuse loudly ("continue with tool calls") and run nothing (P2).
4. **Receipts: exactly one per request, always.** `RES <nonce> <id> <status>`, where status is `ran rc=<rc> run=<stack run
   id>` followed by the runner's printed output (its own 9,000-character cap), or `refused: <reason>` (unknown label,
   malformed, a parameter the runner refuses, stale nonce, duplicate id, budget, cap), or `unanswered: <why>` (from the
   reconciler). Cap the whole feedback (state the cap) and name the saved outputs past it. Append every receipt to the
   MAIN tree's `.jev/req/ledger.jsonl` (found through `git rev-parse --git-common-dir`, as the stack runner finds its log):
   session id, nonce, id, label, status, the stack run id, and the uuid of the transcript record that carried the request.
5. **The reconciler (closes P3d, and the rest of P3b).** On the next UserPromptSubmit and on SessionStart, find every
   REQ line of the ended turn with no receipt in the ledger and report each in the injected context:
   `unanswered: <id> <label> (<how the turn ended, where the transcript shows it: an interrupt, an error, or unknown>)`.
   It never runs them: an interrupt is the owner's stop, and the coordinator re-issues a request that is still wanted.
6. **The labels are data.** A ledger row points at its request's transcript record and at its stack run
   (`.jev/stacks/<run>/`), so a later export can pair the chat before a request with its label and its result. Do not
   build that export; make the pairing possible and test it on a fixture.
7. **The other Stop hooks.** `turn-retro-gate.sh` fires on the first Stop after a new HEAD, so mid-chain it would land
   beside a receipt (PM P6): it defers (exit 0, its sentinel not written) when the final message carries a REQ line with
   the current nonce. The harness's git check (`/root/.claude/stop-hook-git-check.sh`, READ only) exits 0 whenever
   `stop_hook_active` is true, so after a request round it is silent for the rest of the turn (PM P4): at a chain's end
   (a Stop with no current-nonce REQ after a receipt), the chat-form hook runs the same dirty and unpushed checks and
   reports them as that check would.
8. **Registration as a patch, never a live edit (orchestration 0p).** The coordinator's own calls run
   `.claude/settings.json`, `.claude/hooks/` and `scripts/install_session_hooks.py` from the shared tree. Deliver
   `tasks/briefs/labeling/LS-B10-registration.patch` (`git diff` format against the PIN): the UserPromptSubmit and Stop
   entries in `.claude/settings.json` (each last in its list, each with an explicit `timeout`); the groups in
   `scripts/install_session_hooks.py` (`our_hooks` and its marker); the tests in `tests/test_session_hooks.py`; the
   retro-gate change in `.claude/hooks/turn-retro-gate.sh`. Prove it in a clean worktree at the PIN with your files:
   `tests/test_session_hooks.py`, `tests/test_search_intercept.py` and your tests pass; paste
   `python3 scripts/vendored_manifest.py --check` (expected to fail on the `.claude/` row until the coordinator
   regenerates the manifest at landing; say so if it does).
9. **An off switch.** While `.jev/req-off` exists, both hooks exit 0 at once and inject nothing.
10. **Fail loud, never stall.** A hook error prints one line naming what failed and exits 0; a Stop with no current-nonce
   REQ line never blocks; no hook waits past its budget.

## TESTS (each with a named mutant it kills; a negative control per gate, the exact error asserted)

- The grammar: blocks with backquotes and fences, a non-breaking space, bold, a line over 200 characters, an unclosed
  block, request lines followed by more text.
- The nonce: stale, none, a duplicate id.
- The transport, on fixture transcripts through the real hook entry: a request in an earlier text block of the final
  message runs; a request in a text block before a thinking-only final message runs; `stop_hook_active` true still runs;
  the cap refusal at cap-1; the budget refusal; a real `scripts/stack.py` run (a deterministic stack such as `premise`)
  producing a `ran` receipt with its run id.
- Receipts: exactly one per request, refusals included; the ledger rows; the pairing of item 6.
- The reconciler: a fixture turn ended by an interrupt reports `unanswered`; a request with a receipt is not reported.
- The retro gate's deferral; the chain-end git check; the off switch.
- The hook's time on a large fixture (a bound in the test, and the measured p50, p95, max in the report).

## BOUNDARY

- CREATE: `scripts/ls_req.py` (grep the tree for the name first), `tests/test_ls_req.py`,
  `tasks/briefs/labeling/LS-B10-registration.patch`.
- READ: `scripts/stack.py`, `scripts/stacks.toml`, `scripts/hook_context.py`, `.claude/hooks/turn-retro-gate.sh`,
  `.claude/settings.json`, `scripts/install_session_hooks.py`, `tests/test_session_hooks.py`,
  `tests/test_search_intercept.py`, `/root/.claude/stop-hook-git-check.sh`, the design and premortem sections above.
- NOT yours in the shared tree: `.claude/`, `scripts/install_session_hooks.py`, `tests/test_session_hooks.py`,
  `scripts/stack.py`, `scripts/stacks.toml`, `/home/user/.claude/settings.json`, the live `.jev/`. Tests never touch the
  real `.jev/`: give the ledger and the nonce store a state directory the tests set.
- Another lane (the scrubber, task #321) works in its own worktree on `scripts/transcript_export.py` and its tests: touch
  none of them.

## REPORT

Return the whole report as your final message: the premise re-run; files with line counts and sha256; per contract item
its pasted evidence; the gates; the mutants; the registration patch's proof; NOT done, first-class; a DISCREPANCIES list;
your self-attack (how could a request still drop without a word?).

## STANDING RULES

- Do NOT spawn subagents. No git write in the shared tree (the coordinator commits); no outward action; no PC bridge.
- Never register the hooks: never run `scripts/install_session_hooks.py`, never touch `/home/user/.claude/settings.json`,
  anything under `.claude/`, or the live `.jev/`.
- Never read a secret file (`.pc-bridge.env`, any `*.env`, any key file); a secret in a test is a fake built at run
  time. In any real transcript, read only `text` blocks, `tool_use` inputs and record types, never a `thinking` block,
  and print only counts, bytes and ids.
- `--basetemp` as a pytest ARGUMENT outside every work tree; counts pasted from `scripts/test_summary.sh` with set ids
  from `bash scripts/pc_suite.sh set-id -- <files>`; a long gate in ONE foreground call; stamps from `date -u`; commits
  cited by origin id or subject; the mutation driver's control first (AF-AP-223).
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- Stop every process you start before you report.

## PREMISE — MEASURED at authoring (2026-09-29, main tree; PIN origin bef1e9e)

Printed by `bash scripts/premise_block.sh` from the main tree at the PIN, before this brief's commit. The `[rc=1]` after
the three zero counts is grep's exit code when nothing matches: nothing is registered. The stack catalog is printed as
its stack names. `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` is unset here, so the harness default (8, PM P2) applies. Expected
to differ: nothing.

```
$ git merge-base --is-ancestor bef1e9e HEAD && echo bef1e9e-is-an-ancestor-of-HEAD
bef1e9e-is-an-ancestor-of-HEAD
$ ls scripts/ls_req.py tests/test_ls_req.py tasks/briefs/labeling/LS-B10-registration.patch 2>&1 | cut -c1-100
ls: cannot access 'scripts/ls_req.py': No such file or directory
ls: cannot access 'tests/test_ls_req.py': No such file or directory
ls: cannot access 'tasks/briefs/labeling/LS-B10-registration.patch': No such file or directory
$ grep -c 'ls_req' .claude/settings.json scripts/install_session_hooks.py /home/user/.claude/settings.json
.claude/settings.json:0
scripts/install_session_hooks.py:0
/home/user/.claude/settings.json:0
[rc=1]
$ sha256sum scripts/stack.py scripts/stacks.toml scripts/hook_context.py scripts/install_session_hooks.py tests/test_session_hooks.py tests/test_search_intercept.py tests/test_stack.py .claude/settings.json .claude/hooks/turn-retro-gate.sh | cut -c1-16,65-
c69a819138d21471  scripts/stack.py
6393305a0bf1a585  scripts/stacks.toml
1f4912ce9389185d  scripts/hook_context.py
0cc115498df91147  scripts/install_session_hooks.py
e7c008cc44919c31  tests/test_session_hooks.py
2e26aa762c7c0852  tests/test_search_intercept.py
3036e5784df20d2f  tests/test_stack.py
03b9e1e1b04d34d7  .claude/settings.json
3932dc634432500a  .claude/hooks/turn-retro-gate.sh
$ python3 -c "import json; d=json.load(open('.claude/settings.json')); print(sorted((k, len(v)) for k, v in d['hooks'].items()))"
[('PostToolUse', 1), ('PreToolUse', 2), ('SessionStart', 2), ('Stop', 2), ('UserPromptSubmit', 2)]
$ python3 scripts/stack.py list 2>&1 | grep -v '^  note:' | awk '{print $1}'
harvest
gate
ctx
impact
find
premise
echo
review
ci
$ printenv CLAUDE_CODE_STOP_HOOK_BLOCK_CAP || echo CLAUDE_CODE_STOP_HOOK_BLOCK_CAP-unset
CLAUDE_CODE_STOP_HOOK_BLOCK_CAP-unset
$ bash scripts/pc_suite.sh set-id -- tests/test_session_hooks.py tests/test_search_intercept.py tests/test_stack.py | tail -1
3 files set=bc6d12c0785b
$ rm -rf /tmp/lsb10-premise-bt; python3 -m pytest -q -p no:cacheprovider --basetemp=/tmp/lsb10-premise-bt tests/test_session_hooks.py tests/test_search_intercept.py tests/test_stack.py 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*//'; rm -rf /tmp/lsb10-premise-bt
334 passed
```
