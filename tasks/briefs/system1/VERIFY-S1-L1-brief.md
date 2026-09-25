# VERIFY-S1-L1: attack the situation-to-skill hook against its full contract (D-090, design L1 and L3)

Role: adversarial-verifier (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/VERIFY-S1-L1-report.md`
(write it incrementally from the start). PIN: 2ff48df (origin). The frozen contract: `tasks/briefs/system1/S1-L1-brief.md`
(CONTRACT 1-5 and EVIDENCE DEMANDS). The builder's report: `tasks/briefs/system1/S1-L1-report.md`. Attack the contract, never
the builder's own cases, and reproduce every claim you rely on through the REAL registered command line (the command string in
`.claude/settings.json` and in `scripts/install_session_hooks.py`'s output, fed a hook payload on stdin).

## WHY

The hook runs before every Write, Edit and Bash call and on every prompt, in every session, and it went live before its gate
(AF-AP-222). A wrong injection teaches the agent a wrong rule; a slow or crashing hook taxes every call; a telemetry line that
copies a command copies its secrets. The coordinator re-ran the builder's gate (124 passed, set 2dc71b948b8b): that proves
reproducibility, not correctness (orchestration 0f). You are the independent pass.

## WHAT TO ATTACK (report every observation; no severity filter)

1. **Verbatim.** Every injected line is byte-identical to a line of the named skill file, and the pointer names the right file
   and heading: the tool path (every table row) and the prompt path. Include rows whose skill was edited after the table was
   generated (two skill bakes landed while the lane ran; the builder says 7 rows moved by a few lines).
2. **Once per window.** The marker and its reset on compact, resume and clear (and not on startup); a subagent window against
   the main thread; two processes writing the marker at once (corruption, a lost update); marker growth; the 7-day prune.
3. **Budgets.** 2,048 bytes per tool call and 4,096 per prompt, cut at a line boundary with the pointer kept; a multi-byte
   UTF-8 character at the boundary; a single skill line longer than the budget (the builder's D9: `pc-bridge-lanes` lines 19
   and 23).
4. **Never blocks, always exits 0.** Malformed JSON, empty stdin, a very large stdin, a missing or unreadable skill file, a
   table row whose anchor no longer resolves, a read-only or missing `.jev/`, a full disk (simulate it; never fill the real
   disk), a slow filesystem. What bounds the hook's run time, and what happens at the harness's hook timeout?
5. **Kill switch and the exception path.** Nothing reaches `additionalContext`; one telemetry line names the exception type.
6. **Telemetry and secrets.** The contract lists the telemetry fields (time, event, tool, situations matched, keys injected or
   skipped, bytes). Prove that no tool input text reaches `.jev/system1.jsonl` or any other file: commands, file contents, file
   paths beyond what the contract names, prompt text. Use fake secret strings built at run time.
7. **Matching.** For each row: false positives and false negatives on real input shapes. The builder's D11 (quoting and
   heredocs are not masked) is a known follow-up: measure its harm on the replay rather than re-reporting it.
8. **The prompt path.** How often it injects a section unrelated to the prompt, on prompts from this session's main
   transcript (counts only: never print, store or quote prompt text).
9. **The builder's numbers.** Reproduce the replay (1,598 of 16,684 calls; median 16,672 bytes per window) and the latency
   table, or report the difference and its cause.
10. **Registration.** `.claude/settings.json` and the installer agree; `--remove` removes only ours; a second install is a
    no-op; the session-start reset runs while the kill switch is on (the builder's D6): is that right?
11. **The coordinator's manifest change.** First-party 16 to 18 and the remainder list in `tests/test_vendored_manifest.py`.

## GATE

Apply the blocking predicate of skill `contract-gate`: contract-mapped, reproduced through the real registered command,
materially effective, a concrete discriminator, in-boundary. A red test is necessary, not sufficient. Return one gate
recommendation: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID, with each blocking finding's
reproduction command.

## BOUNDARY

READ everything. WRITE only your report and scratch under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-s1l1/`. Every reproduction runs on a copy
(of the hook, the table, a skill, the `.jev/` state), never on the live files. Never create or delete the live kill switch
`.jev/system1-off`, and never run `scripts/install_session_hooks.py` without `--target <a scratch path>`: the default target,
`/home/user/.claude/settings.json`, is live for this whole session. Other lanes hold this tree: INSTALL1 (`scripts/setup.sh`,
`harness-ports/bin/pc-setup.sh`, `upstream.lock.yaml`, `scripts/hooks/post-commit`, `.gitignore`, new slopo files) and L5
(`scripts/chat_find.py`, `tests/test_chat_find.py`): touch none of their files.

## STANDING RULES

No git writes; no PC bridge; no outward-facing action. Transcripts and tool inputs hold secrets: print and store counts, ids
and positions only. Test secrets are fake strings built at run time. The disk is shared (2.0G free; INSTALL1 must keep 1 GB):
keep your scratch under 200 MB and delete it as you go. Long runs go in one foreground call each.

## PREMISE — MEASURED at authoring (2026-09-25 16:3xZ)

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf
2ff48df AF-AP-220 addendum: the codebase-memory Read hook is silent by design for a file the graph covers ("Po
$ git log --format=%h --grep='^S1-L1 landed' -n 1 origin/claude/soundbox-kit-migration-iz1jwf
6195b77
$ df -h / | awk 'NR==2{print $4}'
2.0G
$ sha256sum <file> | cut -c1-16   (HEAD bytes = the PIN bytes; a push rewrites ids, not trees)
a3e37aba8adbc014  .claude/hooks/system1-context.py
eef9252d0c0c2b9f  .claude/hooks/system1-situations.json
73cd14590abbd0d5  .claude/settings.json
a6632b8003ccffe3  scripts/install_session_hooks.py
575dc3ed876f0084  .claude/hooks/session-start.sh
5f2ed3707dcf89a7  scripts/hook_context.py
$ grep -c system1-context /home/user/.claude/settings.json   (the live registration)
2
$ ls .jev/system1-off; wc -l < .jev/system1.jsonl
No such file or directory
214
$ python3 -c "import json; print(len(json.load(open(\".claude/hooks/system1-situations.json\"))[\"rows\"]))"
38
$ bash scripts/test_summary.sh tests/test_system1_context.py tests/test_session_start_hook.py tests/test_session_hooks.py tests/test_hooks_worktree.py   (the coordinator's run after the lane's hand-back, before the landing commit)
pytest-summary: 124 passed in 14.25s
4 files set=2dc71b948b8b
```

A question for you, not a fact: the builder's D3 makes the injected LINE, not the section, the once-per-window unit. Can a
row's excerpt arrive split across calls so that a rule reads without its qualifying line? Show a case or say why not.
