# LS-B10 round 2: a receipt for every request line on the fallback path too (task #364, VERIFY-LS-B10 F1)

Role: code-implementer, a fresh lane (sandbox, Opus 5.5). Do NOT spawn subagents. Return the whole report as your final
message.

Authored 2026-09-29 by the coordinator.

LS-B10 (`scripts/ls_req.py`, `tests/test_ls_req.py`, the unapplied `tasks/briefs/labeling/LS-B10-registration.patch`)
landed at 757ca51, not registered. Its verify, `tasks/briefs/labeling/VERIFY-LS-B10-report.md`, returned NOT-READY on F1;
read the coordinator note at its top (the rulings) and its F1, F4, F6, F10 and F11 first. This round is LS-B10's one
focused repair (D-031, D-034): F1, plus three items the note routes here. The original contract,
`tasks/briefs/labeling/LS-B10-brief.md`, stays true in full; every item the verifier found holding stays holding.

## CONTRACT (this round)

1. **F1: the fallback path gives every request line exactly one receipt.** Today `known()` (`scripts/ls_req.py:584`)
   reads a fallback candidate (no uuid) as "same" as any row with the same `sha`, so `cmd_stop` (`:1029`) and `reconcile`
   (`:858`) skip it: a byte-identical repeat of a request line, in one fallback text or re-issued after a fallback round,
   gets no receipt, no ledger row and no report, and in the verifier's S2 the Stop exits 0 on the model's unanswered line.
   After this round it gets `refused: duplicate id` and the Stop exits 2, exactly as on the transcript path. Match by
   occurrence, not by text; the verifier's suggested shape (a fallback row absorbs at most ONE transcript line, the first
   in transcript order at or after the fallback round's `read`, bound by a row that carries its uuid and line; within one
   fallback text "same" needs the same `line`) is a hypothesis to test, not a spec. The record that carried a fallback
   line must still read as "same" (the verifier's case 5d': nothing runs twice). Cover the reverse order the verifier
   left static (a transcript row first, then a fallback candidate) and two identical malformed current-nonce lines.
2. **F4: nothing is marked delivered above the cap.** At a Stop whose count is above the cap, the hook writes its
   refusal receipts as undelivered, keeps them in `undelivered`, and exits 0; the next prompt reports them (the
   verifier: safe whatever the harness does with text above the cap). At cap-1 and at the cap, today's behavior stays.
   `at_cap` is at `:1066`.
3. **F6: the never-run and window clauses get tests.** Six of the verifier's mutants survive the whole suite with the
   behavior correct: V1 (the subagent guard, `agent_id`), V2 (sidechain records read), V3 (a `tool_use` input read as
   text), V12 (a `tool_result` read as text), V5 (the Stop ignores a new transcript path), V6 (the Stop ignores a shrink).
   Add a test that kills each, named for it; V1 to V3 and V12 are the injection boundary (standing rule 14).
4. **F10: the hook count is true.** Inside the registration patch, `scripts/install_session_hooks.py` states and prints
   the count it registers (from the code, not a literal), and `tests/test_session_hooks.py` names and asserts that count,
   so neither says "eight" beside 13 hooks.
5. **F11, ruled by the coordinator (no code change):** item 7's specific wording governs; the chain-end git report
   reports as the harness's own check would, once per chain, and item 10's never-block rule covers request handling
   only. Say so in the module docstring where item 10 is stated.

## WHERE YOU WORK: a worktree, never the shared tree (orchestration 0p)

- Make a detached worktree at the PIN under your own scratch: `git -C /home/user/agent-factory -c core.hooksPath=/dev/null
  worktree add -q --detach <W> <PIN>`. Build and test there only.
- The verifier's attacks are your red items: its scratch `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vlsb10/`
  (`attack4.py` and `attack4b.py` for F1 and F4, `mut/my_driver.py` and `mut/my_mutants.py` for F6). Its `harness.py`
  imports `World` from a worktree at `vlsb10/wt` that it removed: copy what you run into your own scratch and point it at
  your worktree; never write the verifier's scratch.
- Your one deliverable in the shared tree: `tasks/briefs/labeling/LS-B10-R2.patch`, the `git -C <W> diff` against the PIN
  of the three files below. Prove it applies (`git apply --check`) on a fresh worktree at the PIN and that the gates pass
  there.
- Remove every worktree you made, and stop every process you started, before you report.

## BOUNDARY

- MODIFY, in your worktree only: `scripts/ls_req.py`, `tests/test_ls_req.py`,
  `tasks/briefs/labeling/LS-B10-registration.patch` (the patch file itself: the F10 edits go inside it).
- CREATE, in the shared tree: `tasks/briefs/labeling/LS-B10-R2.patch`. Nothing else in the shared tree.
- READ: everything named above; `scripts/stack.py`, `scripts/stacks.toml`, `scripts/handback_extract.py` (ls_req's
  neutralizer; it changed after 757ca51, VERIFY F14), `.claude/hooks/turn-retro-gate.sh`, `.claude/settings.json`.
- Never register the hooks: never run `scripts/install_session_hooks.py` outside a test's temp target, never touch
  `/home/user/.claude/settings.json`, anything under the shared tree's `.claude/`, or the live `.jev/`. Tests give the
  ledger and the nonce store a state directory of their own.
- Two verify lanes (VERIFY-SCRUB2-R1-R4, VERIFY-H1a) run beside you in their own worktrees; touch none of their files.

## EVIDENCE DEMANDS

1. Premise: re-run the block below with `bash scripts/premise_block.sh` from `/home/user/agent-factory`; stop and report
   CONTRACT-INVALID on a difference.
2. Red first: the verifier's S1, S1b and S2 (and their controls) fail at the PIN in your worktree and pass after; the six
   mutants of item 3 survive the PIN's suite and are killed after; the F4 case (Stops above the cap) before and after.
3. Gates, each twice, in your worktree, with `--basetemp` as a pytest ARGUMENT outside every work tree and counts pasted
   from `scripts/test_summary.sh` with set ids from `bash scripts/pc_suite.sh set-id -- <files>`: `tests/test_ls_req.py`;
   with the registration patch applied, the verifier's two sets (its item 9: the brief's three files, and
   `tests/test_filepacks.py tests/test_hooks_worktree.py tests/test_jev_context.py tests/test_system1_context.py
   tests/test_strip_cbm_hooks.py`).
4. Mutation on your final bytes, each driver's control first (AF-AP-223: check the `--basetemp` parent exists before you
   count a kill): the builder's 70 and 14 (their drivers are named in `tasks/briefs/labeling/LS-B10-report.md`), the
   verifier's 14, and a new mutant per clause of items 1 and 2.
5. The patch's proof (the worktree section).
6. NOT-done and DISCREPANCIES first in the report; then your self-attack: how could a request line still get no receipt?

## STANDING RULES

- No git write in the shared tree (a worktree add and remove, hooks off, is the one exception); no outward action; no PC
  bridge.
- Never read a secret file (`.pc-bridge.env`, any `*.env`, any key file); a secret in a test is a fake built at run time.
  In any real transcript, read only `text` blocks, `tool_use` inputs and record types, never a `thinking` block, and print
  only counts, bytes and ids.
- The sandbox VM rebooted twice today while tests ran (14:09:29Z, about 14:20:10Z; cause open, memory looked small): run
  `free -m` before a heavy command, keep each run's evidence on disk as you go, and say which runs a reboot voided.
- A long gate in ONE foreground call, each under 10 minutes; stamps from `date -u`, substituted, never typed; commits
  cited by origin id or subject.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- Stop every process you start before you report; kill by pid only.

## PREMISE — MEASURED at authoring (2026-09-29, main tree@0ab1df7; PIN origin 0ab1df7)

Printed by `bash scripts/premise_block.sh` from the main tree at origin 0ab1df7, after the push. The PIN is 0ab1df7; the boundary files are byte-identical from it to HEAD (the second line). The hook is not registered (the two 0 counts). The count on the last run is the PIN's `tests/test_ls_req.py` in the main tree. Re-run every `$` line from `/home/user/agent-factory`; on any difference, stop and report CONTRACT-INVALID with the diff.

```
$ git merge-base --is-ancestor 0ab1df7 HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ git diff --quiet 0ab1df7 HEAD -- scripts/ls_req.py tests/test_ls_req.py tasks/briefs/labeling/LS-B10-registration.patch scripts/handback_extract.py && echo boundary-unchanged-since-PIN
boundary-unchanged-since-PIN
$ sha256sum scripts/ls_req.py tests/test_ls_req.py tasks/briefs/labeling/LS-B10-registration.patch scripts/handback_extract.py tasks/briefs/labeling/VERIFY-LS-B10-report.md | cut -c1-16,65-
7dfb0b9d91f84732  scripts/ls_req.py
cfa360f21aae083e  tests/test_ls_req.py
b7a5d6c0dbbeeffe  tasks/briefs/labeling/LS-B10-registration.patch
b0a7f91bd2527d69  scripts/handback_extract.py
af1e577ecc418efd  tasks/briefs/labeling/VERIFY-LS-B10-report.md
$ wc -l scripts/ls_req.py tests/test_ls_req.py | tail -1
  2239 total
$ grep -n 'def known\|at_cap = \|def cmd_stop\|def reconcile' scripts/ls_req.py
584:def known(c, idx, seen):
837:def reconcile(ctx, st, recs=None, restart=None):
990:def cmd_stop(ctx, payload):
1066:    at_cap = n >= ctx.cap - 1
$ grep -c 'ls_req' .claude/settings.json /home/user/.claude/settings.json
.claude/settings.json:0
/home/user/.claude/settings.json:0
[rc=1]
$ git apply --check tasks/briefs/labeling/LS-B10-registration.patch && echo registration-patch-applies
registration-patch-applies
$ ls /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vlsb10/attack4.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vlsb10/attack4b.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vlsb10/mut/my_mutants.py
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vlsb10/attack4.py
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vlsb10/attack4b.py
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vlsb10/mut/my_mutants.py
$ mkdir -p /tmp/lsb10r2-premise && bash scripts/test_summary.sh tests/test_ls_req.py --basetemp /tmp/lsb10r2-premise/bt 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*//'
pytest-summary: 43 passed
$ bash scripts/pc_suite.sh set-id -- tests/test_ls_req.py | tail -1
1 files set=35c6a92807a9
```
