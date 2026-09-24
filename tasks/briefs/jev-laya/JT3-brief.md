# JT3: the search intercept and the Bash quirk guard (tasks #228, #225; D-072 item 4)

Role: code-implementer (sandbox, Opus 5.5). PIN: the local HEAD named in the dispatch message.
Report: `tasks/briefs/jev-laya/JT3-report.md` (write it incrementally from the start).

## Why

The owner (D-072): "when you try to run grep, it blocks you, it runs it itself, and then it gives you the output, the condensed,
serialized output. It prunes it." Today `.claude/hooks/graft-first-nag.py` only nags, and the nag is ignored: this session made
70 Grep calls and about 13,000 Bash calls, many of them greps. And a rule written in CLAUDE.md does not stop a recurring command
shape: the trailing-`&` rule bit again at 12:1xZ today (58 such commands and 37 `pkill -f` in this session; task #225). This lane
turns both into one PreToolUse hook that blocks ONCE, explains or answers, and lets an identical repeat through.

## Boundary

- CREATE: `.claude/hooks/search-intercept.py`, `tests/test_search_intercept.py`, the report.
- MODIFY: `scripts/install_session_hooks.py` (the installed PreToolUse entry: matcher `Grep|Bash`, command runs
  `search-intercept.py` through `scripts/hook_context.py`, same fail-open guard as the other entries), `tests/test_session_hooks.py`
  (only the assertions that name the PreToolUse matcher or command), `.claude/settings.json` (the repo-rooted twin of the same
  entry). The coordinator regenerates the vendored manifest and commits; you never commit.
- READ: `.claude/hooks/graft-first-nag.py` (its semantic-search classifier; keep the file itself unchanged, the Hermes and Codex
  adapters use it), `scripts/hook_context.py`, `scripts/jev.py` (JT1's; import, never edit), CLAUDE.md (the quirk lines),
  `docs/INCIDENT-LOG.md`.

## Pinned decisions (a conflict with the tree is a STOP-and-report)

- **D-1 One hook, two jobs, one escape hatch.** `search-intercept.py` reads the PreToolUse payload. (a) A SEMANTIC search (the
  nag's classifier: a bare identifier aimed at project code, as a Grep call or as a simple Bash `grep`/`rg` command over code
  paths, optionally piped into `head`/`tail`/`wc`; compound commands are never intercepted for search) is answered: run
  `graft ask` for the identifier in the path and the search itself (`rg` with the same pattern, path and glob, capped), rank the
  hits with `jev.rank` when there are more than 12 (fail-open to file order), and exit 2 with the condensed answer on stderr. (b)
  A Bash command matching a QUIRK rule is blocked with the rule's explanation and its CLAUDE.md or AF-AP anchor on stderr, exit 2.
  (c) The escape hatch: the same tool name and input seen again within 120 s passes untouched (exit 0), so a wrong intercept
  costs one call. State lives in `.jev/intercept-seen.json` (0600; entries older than 10 minutes pruned).
- **D-2 The quirk table is closed and measured.** Candidates: a `&&` list ending in a trailing `&` (CLAUDE.md "A trailing `&`
  backgrounds the WHOLE `&&` list"); `pkill -f` in a compound command whose other parts name the same target (CLAUDE.md, the
  2026-09-14 rc 144); backticks inside a double-quoted `safe_commit.sh -m "..."` (CLAUDE.md, 2026-09-15); `git rev-parse --short`
  with two revisions in one call (CLAUDE.md). For each, stream this session's transcript
  (`/root/.claude/projects/-home-user/*.jsonl`, line by line, never whole; about 662 MB), count the Bash commands it matches,
  read at least 20 matches (or all, if fewer) and classify each as a real instance or a false positive. A rule ships only with a
  false-positive rate at or under 5% on that read; the others stay out, and the report says why. Paste the table.
- **D-3 Fail-open.** Any error, a missing tool, a timeout (graft 20 s, the whole hook 45 s), a malformed payload: exit 0 with no
  output. The off switch: a file `.jev/intercept-off`, or `AF_SEARCH_INTERCEPT=0` in the hook's environment.
- **D-4 Size.** Every stderr answer stays under 9,000 characters (AF-AP-183: the harness swaps hook text over 10,000 for a 2 KB
  preview). The answer's first line says what happened and how to get the raw result (repeat the call).
- **D-5 Standard library only** (the hook runs under `python3` with no venv), plus `graft` and `rg` on the PATH.

## Contract

- **A1** Live: install into a scratch settings file (`python3 scripts/install_session_hooks.py --target /tmp/jt3/settings.json`)
  and run the installed PreToolUse command through `sh -c` with real payloads: a semantic Grep (intercepted, graft's answer and
  ranked hits on stderr, exit 2); the identical repeat (exit 0); a literal-token Grep (exit 0); a simple semantic `rg` Bash command
  (intercepted); a compound Bash command with a grep in it (exit 0); each shipped quirk rule's positive and a near-miss negative.
  Paste them. Never edit `/home/user/.claude/settings.json`; the coordinator re-installs after review.
- **A2** Fail-open: graft absent, `rg` absent, Jev down, a malformed payload, the off switch: each exit 0 with no output.
- **A3** Every answer under 9,000 characters (a test with a search that matches thousands of lines).
- **A4** The existing suites stay green: `tests/test_session_hooks.py` (with your matcher edits), `tests/test_hooks_worktree.py`,
  `harness-ports/tests/run-all.sh`.
- **A5** Mutants on scratch copies: (1) no escape hatch; (2) intercept compound commands; (3) no size cap; (4) fail closed on a
  graft error. Each turns a named test red; paste the kill table.
- **Gates:** `python -m pytest tests/test_search_intercept.py tests/test_session_hooks.py tests/test_hooks_worktree.py -q
  --basetemp /tmp/jt3/bt` twice (make the parent first); `bash harness-ports/tests/run-all.sh`; `python3 scripts/lint_delta.py
  --base HEAD` with no new hit.

## Standing rules

Do not spawn subagents. No outward actions (no push, PR, comment, bridge call). Do not commit. Never edit
`/home/user/.claude/settings.json`. Touch only the boundary; report adjacent defects. Other agents edit
`src/agent_factory/decisions/volatile.py` and `tests/test_decisions_*.py` (J1-1-R4), the JT1 files (`scripts/jev.py`,
`scripts/jev_local.sh`, `scripts/hiccup_scan.py`, their tests, `docs/HICCUPS.md`) and the JT2 files (`scripts/jev_context.py`,
`scripts/jev_locate.py`, `scripts/jev_echo.py`, their tests): never touch those. The local Laya server for tools is
127.0.0.1:47411 (through `jev.py`); never stop it. Never print a secret. No `-n` for pytest. Kill by pid only. Check every written
file with `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`.

## PREMISE — MEASURED at authoring (2026-09-24 13:0xZ, /home/user/agent-factory at eb52e9b)

```
$ python3 -c "import json; s=json.load(open('/home/user/.claude/settings.json')); print(s['hooks']['PreToolUse'][0]['matcher'])"
Grep
$ grep -n -A2 '"PreToolUse": \[' scripts/install_session_hooks.py
51:        "PreToolUse": [{"matcher": "Grep", "hooks": [{"type": "command", "command": guarded(
52-            ".claude/hooks/graft-first-nag.py", f"{wrap} PreToolUse -- python3 {r}/.claude/hooks/graft-first-nag.py",
53-            True)}]}],
$ grep -n 'def test_a_present_hook_keeps_its_blocking_exit' tests/test_session_hooks.py
189:def test_a_present_hook_keeps_its_blocking_exit(tmp_path):      (a present hook's exit 2 passes through the guard)
$ timeout 60 graft ask "who calls merged in install_session_hooks" --in scripts     (2,656 ms, 201 bytes, rc 0)
$ quirk-shape counts over this session's 13,101 Bash calls (rough regexes, 12:23Z; re-measure with your exact rules):
   58  a && list ending in a trailing &       37  pkill -f       26  backtick inside safe_commit.sh -m "..."
  353  git rev-parse --short followed by a second token (noisy: includes redirections)
```
