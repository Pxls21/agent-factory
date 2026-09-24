# VERIFY-JT3 — the independent verify of the search intercept and the Bash quirk guard (tasks #228, #225, #236; rule 0f)

PIN: the content of the five boundary files as hashed below (uncommitted in the shared tree at local HEAD ee44b41; a push can
rewrite commit IDs but not blobs: re-measure the blobs first). COMPONENT: `.claude/hooks/search-intercept.py` (H, new),
`tests/test_search_intercept.py` (TH, new), `scripts/install_session_hooks.py` (I), `tests/test_session_hooks.py` (TI),
`.claude/settings.json` (S). The contract is `tasks/briefs/jev-laya/JT3-brief.md` (D-1 to D-5, A1 to A5) as corrected at 13:3xZ
(file order is the default; `jev.rank` only behind an off-by-default switch and it may only REORDER, never decide what is cut).
The builder's report `tasks/briefs/jev-laya/JT3-report.md` is an INPUT TO ATTACK, not a truth.
LANE: verify-jt3 (sandbox; agent `adversarial-verifier`, Opus 5.5, in the SHARED tree, no worktree isolation). Do NOT spawn subagents.
Report: `tasks/briefs/jev-laya/VERIFY-JT3-report.md` (write it incrementally from the start).

## Why this lane exists

H runs on EVERY Bash and Grep call of every session rooted at `/home/user` once registered. A wrong block stalls all work; a wrong
pass defeats the purpose (the owner's ask: "when you try to run grep, it blocks you, it runs it itself, and then it gives you the
output ... it prunes it", D-072 item 4). It already went live early, before any review (AF-AP-148's second shape, 13:52:56Z), and
blocked real calls; its own off switch `.jev/intercept-off` has held it inert since 14:07:03Z. Nobody independent has attacked it.

## Items (report EVERY observation; no severity filter; rank downstream)

1. Premise: re-measure the five blobs and the test set below; read the contract and the report.
2. D-1 scope: what H intercepts and what it must pass through. Attack both directions with shapes of your own: a grep inside a
   pipeline or a compound command, `git grep`, `grep -c`, grep on a log or JSONL file, grep with `-r` over a path outside the repo,
   a Grep-tool call with odd parameters, multi-line commands, heredocs, commands that only mention "grep" in a string or comment.
   Is any legitimate non-search command blocked? Is the escape hatch (the identical call repeated within 120 s) sound: keyed
   correctly, not reusable by a DIFFERENT command, not stuck after a failure?
3. D-2 the quirk table: the four shipped rules (trailing-amp, pkill-self, safe-commit-backtick, rev-parse-two). New shapes for false
   positives AND false negatives: `&&` and `&` inside quotes, heredocs and comments; the deliberate `( ... && nohup ... & )` form;
   `pkill -f` naming a pattern that cannot self-match; backticks in a single-quoted `-m`. Re-derive at least one of the report's
   measured rates from this session's transcript yourself.
4. D-3 fail-open: graft absent or slow, `rg` absent, a malformed or huge payload, an unreadable cwd, a timeout, Jev down or slow
   with the rank switch on. Every case must exit 0 with no output and no traceback, and must never hang the calling tool: measure
   the worst-case wall time you can provoke.
5. D-4 size: every answer under 9,000 characters, including multibyte text, very long lines and thousands of matches. Say what the
   model actually receives when H blocks (the report measured about 280 extra characters of harness wrapper).
6. Semantics and exposure: `rg` honours `.gitignore` while `grep -r` does not, so a condensed answer can MISS untracked or ignored
   files the original command would have searched (name concrete misses in this tree), and the pathless form now searches `.`.
   Can H ever print content from a file the original command would not have read (for example a gitignored secret file such as
   `.pc-bridge.env`)? Use FAKE secrets in scratch files only; never print a real one.
7. The rank switch (`.jev/intercept-jev-rank-on` or `AF_SEARCH_INTERCEPT_JEV_RANK=1`): off by default; when on, Jev can only reorder
   the lines file order already chose (mutant M5); what happens on a Jev error mid-answer? Use the 127.0.0.1:47411 server; never stop it.
8. The installer and registration: I and S as committed would register H for every fresh session, where `.jev/intercept-off` does not
   exist, so H would be ON by default. State what that means and whether any other hook entry lacks the fail-open guard the report
   mentions. Do NOT run the installer against `/home/user/.claude/settings.json`; use `--target` with a scratch file.
9. Cost: the report's ~35 ms median per Bash call with nothing to do. Re-measure; say what share is Python start-up and compile.
10. Mutants on scratch copies only: at least five of your own design beyond the builder's six; each should turn a named test red.

Then apply the blocking predicate (contract-mapped, reproduced through the real path, materially effective, a concrete discriminator,
in-boundary) and give ONE gate recommendation: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID.

## Evidence rules

Reproduce every claim you rely on; paste counts and outputs from commands you ran. Drive H directly with crafted PreToolUse payloads
on stdin (as the tests do) or through a scratch settings file; never through the shared session's live registration. Mutants on
scratch copies ONLY (never edit, stash, restore or check out a tracked file in this tree). Test secrets are FAKE strings (QZJ8...
and X4Z9... style). The sandbox venv has no pytest-xdist: never pass `-n`. Use a short `--basetemp` (for example `/tmp/vjt3/bt`;
make the parent first). Record which model served your turns if you can see it.

## Standing rules

No outward actions (no pushes, PRs, comments, GitHub writes, bridge calls, third-party APIs). Do not commit. NEVER remove or create
`.jev/intercept-off` or the rank switch in the shared tree, and never edit `/home/user/.claude/settings.json`: both change live
behaviour for every agent. Other lanes are editing `scripts/jev_context.py`, `scripts/jev_locate.py`, `scripts/jev_echo.py`,
`tests/test_jev_context.py`, `tests/test_jev_locate_echo.py` and `docs/research/findings/jev-locate-bench/` (JT2), and reading the
`src/agent_factory/decisions/` files (VERIFY-J1-1-R4): never touch those. Check every file you write with
`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`.

## PREMISE — MEASURED at authoring (2026-09-24 14:5xZ, /home/user/agent-factory at local HEAD ee44b41)

```
$ git rev-parse --short HEAD
ee44b41
$ git hash-object .claude/hooks/search-intercept.py tests/test_search_intercept.py scripts/install_session_hooks.py tests/test_session_hooks.py .claude/settings.json
c0c23042925ad8016a40980c83206026070b17a2
3470a6e91a3f80a9f722c8a81f36d5e4cde5f34d
ec47d5d7cec93ea6f7e2e5ed03ac4a5aee43173b
d612f704d8341e7211b5016525108312ce87817e
197e738a66f36952883403f6043398b901bb0ff5
$ wc -l .claude/hooks/search-intercept.py tests/test_search_intercept.py | tail -3
 1080 .claude/hooks/search-intercept.py
  414 tests/test_search_intercept.py
 1494 total
$ git diff --stat -- scripts/install_session_hooks.py tests/test_session_hooks.py .claude/settings.json | tail -4
 .claude/settings.json            |  4 ++--
 scripts/install_session_hooks.py | 12 +++++++-----
 tests/test_session_hooks.py      | 11 +++++++----
 3 files changed, 16 insertions(+), 11 deletions(-)
$ bash scripts/test_summary.sh tests/test_search_intercept.py tests/test_session_hooks.py tests/test_hooks_worktree.py --basetemp /tmp/jt3c/bt
pytest-exit: 0
pytest-summary: 87 passed in 22.11s
$ ls -la --time-style=+%H:%M:%S .jev/intercept-off | awk '{print $6, $7}'
14:07:03 .jev/intercept-off
```
