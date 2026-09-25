# S1-L1: the situation-to-skill hook, with skill sections beside the wiki excerpts (D-090; design L1 and L3)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/S1-L1-report.md` (write it
incrementally from the start). PIN: 3c495c9 (origin). Design: `docs/research/findings/system1-context/DESIGN-2026-09-25.md`
sections L1 and L3; evidence: `docs/research/findings/system1-context/AUDIT-2026-09-25.md`.

## WHY

Rules that say "load skill X before Y" do not load skills: 12 Skill calls in the main transcripts, 30 in subagents; the
harness's skill listing describes 72 of 485 skills (AF-AP-218, audit D13). What gets read is what a hook injects automatically
(the wiki hook fired 48 times, EDIT SNAPSHOT 533). The owner (D-090): feed the relevant skill parts VERBATIM with a pointer to
the full file, automatically, before the agent acts.

## CONTRACT

1. **One hook, `.claude/hooks/system1-context.py`, on two events.**
   - **PreToolUse (Write, Edit, Bash):** it recognizes the situation from the tool input (a file path or the command) and
     injects the governing skill section's key lines, verbatim, then one line `full details: <skill file> § <heading>`.
   - **UserPromptSubmit:** keyword matching of the prompt against skill SECTIONS (a skill split at its headings), injecting the
     best one or two excerpts with their pointers. This runs beside `wiki-context.py`, never inside it.
2. **The situation table** is a committed data file beside the hook, one row per situation: its id, the skill, the section
   heading, and the path and command patterns that detect it. It is derived from the "Load `<skill>` before/when <situation>"
   pointer lines in CLAUDE.md and from CLAUDE.md's other load rules (orchestration before a brief, anti-hollow-green for a
   gate or oracle, contract-gate, and so on). Give every row a test that shows a matching and a non-matching tool input.
   Where the text names a situation no pattern can detect, list it in the report and give it no row.
3. **Once per context window.** A section already injected is not injected again until the context resets. Record the
   injected keys per session in a marker under `.jev/`. The SessionStart hook clears it on `compact`, `resume` and `clear`.
4. **Budget and safety.**
   - At most 2,048 bytes per tool call and 4,096 per prompt. Cut at a line boundary and keep the pointer.
   - The hook never blocks and always exits 0.
   - It prints nothing when `.jev/system1-off` exists.
   - One JSON line per decision goes to `.jev/system1.jsonl`: time, event, tool, the situations matched, the keys injected
     or skipped (duplicate or budget), and the bytes.
   - An exception in the hook injects nothing and logs its type.
5. **Registration.**
   - Register in `.claude/settings.json` and in `scripts/install_session_hooks.py` (the `/home/user`-rooted session).
   - PreToolUse output goes through `scripts/hook_context.py`, the same way `edit-snapshot.py` and `search-intercept.py` do.
     Plain PreToolUse stdout never reaches the model (AF-AP-172).
   - Keep the latency low: no instrument calls and no network, and read the skill files with a cache keyed on their mtime.
     Report the measured latency per event.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. Tests through the REAL registered command lines. Feed fixture hook payloads to the command exactly as the settings file
   runs it, and assert what reaches `additionalContext`. Cover:
   - every situation row, matching and not matching;
   - the once-per-window rule and its reset;
   - both budgets;
   - the kill switch;
   - the telemetry line;
   - an exception;
   - the prompt path.
3. A replay: run the hook over the tool calls recorded in this session's main transcript (the Write, Edit and Bash inputs
   only, in process, counts only; never print or store transcript text). Report how many calls would have received which
   skill section, and the bytes per window.
4. `bash scripts/test_summary.sh` on your tests plus `tests/test_session_hooks.py` and `tests/test_hooks_worktree.py`, twice,
   with the set id; pyflakes rc 0; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0 for every file you write.
5. NOT-done and DISCREPANCIES.

## BOUNDARY

CREATE: `.claude/hooks/system1-context.py`, its situation table beside it, tests under `tests/`, your report. MODIFY:
`.claude/settings.json`, `scripts/install_session_hooks.py`, `.claude/hooks/session-start.sh` (the reset only), the tests of
those. READ everything else, above all the skills and CLAUDE.md. Not `wiki-context.py`, not any skill file. A new file under
`.claude/` changes the vendored manifest: list the paths; the coordinator regenerates it at commit. Scratch:
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/s1l1/`.

## STANDING RULES

Transcripts hold secrets: the replay prints counts and situation ids only. No git writes; no PC bridge; no outward-facing
action. You are the only lane in this tree. The disk is tight (about 2 GB free): keep test copies small and delete scratch as
you go.

## PREMISE — MEASURED at authoring (2026-09-25 15:1xZ, the sandbox, the PIN's bytes)

```
$ git show 3c495c9:<file> | sha256sum | cut -c1-16
fab9b615481333c8  .claude/hooks/wiki-context.py
5f2ed3707dcf89a7  scripts/hook_context.py
30c4862939017c5c  scripts/install_session_hooks.py
ad7fe12e10a72d51  .claude/settings.json
0dd289beee186a01  .claude/hooks/session-start.sh
$ (the hook registrations in .claude/settings.json, event | matcher | command prefix)
SessionStart | None | $CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh
PostToolUse | Edit|Write|Read | python3 $CLAUDE_PROJECT_DIR/scripts/hook_context.py PostToolUse -- python3 .../edit-snapshot.py
UserPromptSubmit | None | python3 $CLAUDE_PROJECT_DIR/.claude/hooks/wiki-context.py
Stop | None | bash $CLAUDE_PROJECT_DIR/.claude/hooks/turn-retro-gate.sh
PreToolUse | Grep|Bash | [ -f .../search-intercept.py ] && [ -f .../hook_context.py ] || exit 0; python3 ...
$ grep -c -i -E 'Load `[a-z-]+` (before|when)' CLAUDE.md
13
$ bash scripts/test_summary.sh tests/test_session_hooks.py tests/test_hooks_worktree.py
pytest-summary: 28 passed in 2.00s
$ bash scripts/pc_suite.sh set-id -- tests/test_session_hooks.py tests/test_hooks_worktree.py
2 files set=0b50704afd94
```

A question for you, not a fact: does `hook_context.py` pass a PreToolUse hook's stdout as `additionalContext` for every tool,
and what does it do with a UserPromptSubmit hook? Read it and say.
