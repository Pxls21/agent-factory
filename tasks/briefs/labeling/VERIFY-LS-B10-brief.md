# VERIFY-LS-B10: attack the chat form before its hooks are registered on every prompt and every Stop (task #364, D-108)

Written 2026-09-29 from 13:3xZ (clock read at 13:30:29Z) by the coordinator. Role: sandbox `adversarial-verifier`, model
opus. Do NOT spawn subagents. Return the WHOLE report as your final message (a report-file write is refused for
subagents).

PIN: 757ca51 (origin `claude/soundbox-kit-migration-iz1jwf`). The landing is origin 1f30c40; 757ca51 replaced two stale
local ids in the report with origin 164bf49 (its message says where), so the report differs from the lane's hand-back
there only.

The change under test: LS-B10, landed GATED-PENDING-VERIFY and NOT registered: `scripts/ls_req.py`,
`tests/test_ls_req.py`, `tasks/briefs/labeling/LS-B10-registration.patch` (not applied). The builder's account:
`tasks/briefs/labeling/LS-B10-report.md` (every claim a hypothesis; read its NOT done list and DISCREPANCIES first). The
contract: `tasks/briefs/labeling/LS-B10-brief.md` (items 1 to 10, TESTS). The owner's intent: D-108's row in
`docs/08_DECISION_LOG.md` (item 6). The transport risks: `tasks/briefs/labeling/LS-PREMORTEM-report.md` §A (P1 to P8).

Why it matters: once registered, the UserPromptSubmit half runs on every prompt and the Stop half on every Stop of the
main session, and the Stop half runs `scripts/stack.py` with arguments taken from chat text. A request that drops
without a word breaks the owner's premise ("I don't think it will drop anything silently"); a request that runs twice,
runs from a stale or foreign line, or reaches a shell is worse; a slow Stop stalls every turn.

## What to attack (the full frozen contract, never only the builder's cases)

1. **Premise.** Re-run the PREMISE block below; on a difference, stop and report CONTRACT-INVALID.
2. **Nothing reaches a shell.** Build hostile request lines and blocks: backquotes, `$( )`, `;`, `|`, newlines inside
   values, a block whose end word appears inside its own text, an unclosed block, `=` inside a value, duplicate keys, a
   label with a path or shell characters, a parameter the runner refuses, NUL and control bytes, CRLF. For each: what ran
   (argv as `scripts/stack.py` received it), what the receipt said. Any shell evaluation is core-blocking.
3. **Only the current turn's own requests run, each exactly once.** A REQ line quoted from an earlier turn (stale
   nonce); the current nonce inside a code fence, bold, a line over 200 characters, a non-breaking space, a lookalike
   `REQ` (Unicode confusables, zero-width characters); the same id twice; the same request repeated in a later text
   block of the same turn; a REQ line inside a `tool_use` input or a tool result (must never run); a REQ line in a
   subagent's transcript or its hand-back; two Stops in one turn (the second must not re-run the first's requests).
4. **Nothing drops without a word.** Every P3 shape through the REAL hook entry on fixture transcripts: requests in an
   earlier text block of the final message; a thinking-only final message; `stop_hook_active` true; an interrupt and an
   API error (no Stop: the reconciler must report `unanswered`); a budget overrun; the cap at cap-1 with
   `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` unset and set; a hook crash mid-round (which receipts exist, what the reconciler
   says). Count receipts per request: exactly one, always.
5. **The transcript read.** The stored byte offset: a transcript shorter than the offset (a restore), a new transcript
   file for the same session (resume), a compaction boundary inside the window, a partial last line (the harness still
   writing), a record over 1 MB. Measure the hook's time through the real entry on a copy of this session's transcript
   tail (p50, p95, max over at least 20 Stops) and compare with the builder's numbers.
6. **The ledger and the pairing.** Rows point at the right transcript record uuid and the right stack run; concurrent
   appends (two sessions); a ledger row for every receipt, refusals included; the item-6 pairing on your own fixture.
7. **The other Stop hooks.** The retro gate defers while a current-nonce REQ line closes the final message and fires at
   the chain's end (its sentinel written then, not before); the chain-end git check reports what
   `/root/.claude/stop-hook-git-check.sh` would (READ it; never run it against the shared tree's state in a way that
   writes); the order of the three Stop hooks in the patched `.claude/settings.json`.
8. **The off switch and failure.** `.jev/req-off` silences both hooks at once; a hook error prints one line and exits 0;
   a Stop with no current-nonce REQ line never blocks; no hook waits past its budget.
9. **The registration patch.** It applies to the landing PIN; in a clean worktree with it applied,
   `tests/test_session_hooks.py`, `tests/test_search_intercept.py` and `tests/test_ls_req.py` pass; the manifest check
   result; what breaks elsewhere (every test that names a patched path).
10. **Mutation.** Re-run the builder's mutants on the final bytes (the control first, AF-AP-223), then write your own for
   the clauses no mutant covers, and report killed and survived with the test that kills each.

## Coordinator's observations at landing (hypotheses to test, never findings)

- The AP screen flags `scripts/ls_req.py:242`: `hook_log` swallows a failed write of its own diagnostics line
  (`except Exception: pass`). Is that the only silent path? Does any receipt, ledger or reconciler path swallow the same
  way (the project's rule: every fail-soft is fail-loud)?
- It also flags `tests/test_ls_req.py:991` (AF-AP-175: one quoted `HEAD` in a fixture's `worktree add`). Harmless in a
  fixture, or does any production path name a ref twice?
- The coordinator's gate ran `tests/test_ls_req.py` under CI's Python (3.12.3, a scratch venv at
  `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ci312`): `43 passed`. CI also runs as a non-root user: does anything in the file or the hooks need
  root (a path, a signal to another user's process)?
- The lane kept a copy of this session's transcript tail at `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/tx/tail40m.jsonl`
  (41,943,040 bytes; the coordinator's known-values check over it: NO HIT). Reuse it for item 5's timing, or copy your
  own tail; delete any copy you make before you report.

## Rules

- Work in a clean detached worktree under your own scratch dir at the PIN the dispatch names
  (`git -c core.hooksPath=/dev/null worktree add -q --detach <W> <PIN>`), and remove it at the end. No git write in the
  shared tree; no outward action, no PC bridge, no subagent.
- NEVER register the hooks: never apply the patch in the shared tree, never run `scripts/install_session_hooks.py`,
  never touch `/home/user/.claude/settings.json`, the repo's `.claude/`, or the live `.jev/`. Tests and probes use a state
  directory of your own.
- Never read a secret file (`.pc-bridge.env`, any `*.env`, any key file); a secret in a test is a fake built at run
  time. In any real transcript, read only `text` blocks, `tool_use` inputs and record types, never a `thinking` block,
  and print only counts, bytes and ids.
- `--basetemp` as a pytest ARGUMENT outside any work tree, never `PYTEST_ADDOPTS`; a long gate in ONE foreground call;
  counts pasted from `scripts/test_summary.sh` with their set ids; stamps from `date -u`; commits cited by origin id or
  subject. Stop every process you start before you report.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.

## Report

Every observation with no severity filter; then the blocking predicate (D-034: only a CORE-BLOCKING finding re-opens the
build; here a request that reaches a shell, runs from a stale or foreign line, runs twice, or drops with no receipt and
no reconciler report counts as core-blocking); then a gate recommendation (MERGE-READY / MERGE-READY-WITH-FOLLOWUPS /
NOT-READY / CONTRACT-INVALID); and a separate list of what must hold before registration.

## PREMISE — MEASURED at authoring (2026-09-29 13:3xZ, a clean detached worktree @757ca51)

Printed by `bash scripts/premise_block.sh` from that worktree's root; re-run each `$` line there. The two `[rc=N]` lines
are expected: `grep -c` exits 1 when every count is 0 (nothing registered), and `ls` exits 2 (no live `.jev/req`).

```
$ git rev-parse --short=7 HEAD
757ca51
$ git log --format='%h %s' -3 -- scripts/ls_req.py tests/test_ls_req.py tasks/briefs/labeling/LS-B10-registration.patch tasks/briefs/labeling/LS-B10-report.md
757ca51 Two local ids replaced by origin ids before the push (13:2xZ)
1f30c40 LS-B10 landed (13:2xZ; task #364, D-108 item 6; GATED-PENDING-VERIFY, NOT registered): the chat form
$ sha256sum scripts/ls_req.py tests/test_ls_req.py tasks/briefs/labeling/LS-B10-registration.patch tasks/briefs/labeling/LS-B10-report.md
7dfb0b9d91f8473287e1006ba34d8f54ab282aeefad095d65965af7b301c14aa  scripts/ls_req.py
cfa360f21aae083e94e3fe32e1835c7606e6191cb0524f0e6bcda7139115a83d  tests/test_ls_req.py
b7a5d6c0dbbeeffeaccc21be68f8e348e5491ee3c9e7f3cdd86797e870a47062  tasks/briefs/labeling/LS-B10-registration.patch
68a67b68f371c350147c8f9f718417f789ebd034dc25d03e40a05673a9cf9e67  tasks/briefs/labeling/LS-B10-report.md
$ wc -l scripts/ls_req.py tests/test_ls_req.py tasks/briefs/labeling/LS-B10-registration.patch
  1181 scripts/ls_req.py
  1058 tests/test_ls_req.py
   391 tasks/briefs/labeling/LS-B10-registration.patch
  2630 total
$ git apply --check tasks/briefs/labeling/LS-B10-registration.patch && echo patch-applies
patch-applies
$ git apply --stat tasks/briefs/labeling/LS-B10-registration.patch
 .claude/hooks/turn-retro-gate.sh |    9 ++
 .claude/settings.json            |   27 +++++
 scripts/install_session_hooks.py |   25 ++++-
 tests/test_session_hooks.py      |  190 +++++++++++++++++++++++++++++++++++++-
 4 files changed, 239 insertions(+), 12 deletions(-)
$ grep -c 'ls_req' .claude/settings.json scripts/install_session_hooks.py .claude/hooks/turn-retro-gate.sh /home/user/.claude/settings.json /home/user/agent-factory/.claude/settings.json
.claude/settings.json:0
scripts/install_session_hooks.py:0
.claude/hooks/turn-retro-gate.sh:0
/home/user/.claude/settings.json:0
/home/user/agent-factory/.claude/settings.json:0
[rc=1]
$ ls -d /home/user/agent-factory/.jev/req
ls: cannot access '/home/user/agent-factory/.jev/req': No such file or directory
[rc=2]
$ bash scripts/pc_suite.sh set-id -- tests/test_ls_req.py
1 files set=35c6a92807a9
$ rm -rf /tmp/premise-lsb10 && mkdir -p /tmp/premise-lsb10 && bash scripts/test_summary.sh tests/test_ls_req.py --basetemp=/tmp/premise-lsb10/bt | grep '^pytest-summary:' | sed -E 's/ in [0-9.]+s.*//'
pytest-summary: 43 passed
```
