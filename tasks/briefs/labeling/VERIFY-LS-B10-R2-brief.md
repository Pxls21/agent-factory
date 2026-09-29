# VERIFY-LS-B10 round 2: re-check the F1 fix and the round's other items (task #364)

PIN: 03ad1b6 (the origin head at authoring; the boundary files are byte-identical from the landing d8fcc58 to it).

Role: the VERIFY-LS-B10 verifier, resumed (sandbox adversarial-verifier, Opus 5.5). Do NOT spawn subagents. Return the
whole report as your final message (your hand-back); write no report file.

LS-B10 round 2 landed at origin d8fcc58 ("LS-B10 round 2 landed (task #364; GATED-PENDING-VERIFY): every request line
gets one receipt on the fallback path too"), GATED-PENDING-VERIFY. It is LS-B10's one focused repair
(D-031) of your F1. Its report of record is `tasks/briefs/labeling/LS-B10-R2-report.md`: read the coordinator note at its
top first (the ruling on its N1), then its DISCREPANCIES (D1 to D13) and its self-attack. The hook is still NOT
registered; the registration stays the unapplied `tasks/briefs/labeling/LS-B10-registration.patch`.

## SCOPE (the re-check, narrow)

1. **Premise.** Re-run the block below with `bash scripts/premise_block.sh` from `/home/user/agent-factory`; on a
   difference, stop and report CONTRACT-INVALID with the diff.
2. **F1.** Your S1, S1b, S2, S2b and 5d' through the real hook at the PIN: every request line gets exactly one receipt; a
   byte-identical repeat gets `refused: duplicate id` and exit 2 on the fallback path as on the transcript path; the
   record that carried a fallback line still reads as "same" (nothing runs twice).
3. **The round's design** (the report's D2 and D11): the bind rows (`kind: "bind"`), `fb` and `after` on fallback rows,
   the transcript-path condition, "a fallback line is never same", and the catch-up exclusion of records an earlier
   round answered or bound. Attack them: can any shape run a request twice, or leave a request line with no receipt,
   without the harness losing a record?
4. **F4** (the report's D4 and D5): above the cap the receipts stay undelivered and the next prompt reports them; at
   cap-1 and at the cap, behaviour is unchanged; the cap values 1 and 0.
5. **F6.** The six named tests kill V1, V2, V3, V5, V6 and V12 on the PIN's bytes.
6. **F10**, inside the registration patch: it applies at the PIN, and the count it states comes from the code.
7. **N1 is ruled a follow-up** (issue #84): report it again only if you find a shape that does NOT need a lost harness
   record.
8. **Gates at the PIN**, in your own worktree (never the shared tree), `--basetemp` as a pytest ARGUMENT outside every
   work tree, counts pasted from `scripts/test_summary.sh` with set ids: `tests/test_ls_req.py` twice (the landing's two
   runs: `1 files set=35c6a92807a9`, `pytest-summary: 58 passed` each); then, with the registration patch applied in a
   scratch worktree, your two sets (the builder's 199 and 328).
9. **Gate recommendation** under D-034's blocking predicate.

## STANDING RULES

- No git write in the shared tree (a worktree add and remove, hooks off, is the one exception); no outward action; no PC
  bridge; never register the hooks.
- Never read a secret file (`.pc-bridge.env`, any `*.env`, any key file); a secret in a test is a fake built at run time.
  In any real transcript, read only `text` blocks, `tool_use` inputs and record types, never a `thinking` block, and print
  only counts, bytes and ids.
- A long gate in ONE foreground call, each under 10 minutes; stamps from `date -u`; commits cited by origin id or subject.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- Stop every process you start before you report; kill by pid only. Remove your worktrees.

## PREMISE — MEASURED at authoring (2026-09-29, main tree@03ad1b6; PIN origin 03ad1b6)

Printed by `bash scripts/premise_block.sh` from the main tree at origin 03ad1b6, before this brief's commit (which
touches no boundary file). The hook is registered nowhere (the two 0 counts; `[rc=1]` is grep's exit code for them).
Expected to differ: nothing. Re-run every `$` line from `/home/user/agent-factory`; on any difference, stop and report
CONTRACT-INVALID with the diff.

```
$ git merge-base --is-ancestor 03ad1b6 HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ git diff --quiet 03ad1b6 HEAD -- scripts/ls_req.py tests/test_ls_req.py tasks/briefs/labeling/LS-B10-registration.patch tasks/briefs/labeling/LS-B10-R2.patch tasks/briefs/labeling/LS-B10-R2-report.md && echo boundary-unchanged-since-PIN
boundary-unchanged-since-PIN
$ git log -1 --format=%s -- scripts/ls_req.py | cut -c1-70
LS-B10 round 2 landed (task #364; GATED-PENDING-VERIFY): every request
$ sha256sum scripts/ls_req.py tests/test_ls_req.py tasks/briefs/labeling/LS-B10-registration.patch tasks/briefs/labeling/LS-B10-R2.patch tasks/briefs/labeling/LS-B10-R2-report.md | cut -c1-16,65-
cb4943a96f6578e5  scripts/ls_req.py
64faf22cf543bc56  tests/test_ls_req.py
ded5c249f249c372  tasks/briefs/labeling/LS-B10-registration.patch
e4b3d90ccb8b45f9  tasks/briefs/labeling/LS-B10-R2.patch
6ea9beb2e90b8dbe  tasks/briefs/labeling/LS-B10-R2-report.md
$ wc -l scripts/ls_req.py tests/test_ls_req.py | tail -1
  2664 total
$ grep -n '^def known\|^def bind_row\|^def row_of\|^def reconcile\|^def cmd_prompt\|^def cmd_stop' scripts/ls_req.py
609:def known(c, idx, seen, path):
633:def row_of(ctx, session, transcript, c, status, reason, delivered, **extra):
641:def bind_row(ctx, session, transcript, c, fbrow):
878:def reconcile(ctx, st, recs=None, restart=None):
945:def cmd_prompt(ctx, payload):
1035:def cmd_stop(ctx, payload):
$ grep -c ls_req .claude/settings.json /home/user/.claude/settings.json
.claude/settings.json:0
/home/user/.claude/settings.json:0
[rc=1]
$ git apply --check tasks/briefs/labeling/LS-B10-registration.patch && echo registration-applies-at-HEAD
registration-applies-at-HEAD
```
