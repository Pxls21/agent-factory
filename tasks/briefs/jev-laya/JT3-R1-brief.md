# JT3-R1 — the one focused repair of the search intercept and the quirk guard (tasks #228, #225, #236; D-031)

PIN: the content of the five files hashed below (JT3's build, uncommitted; re-measure the digests first). CONTRACT:
`tasks/briefs/jev-laya/JT3-brief.md` (D-1 to D-5, A1 to A5). EVIDENCE: `tasks/briefs/jev-laya/VERIFY-JT3-report.md` (F-1, F-2, F-3,
F-4 in detail, with the verifier's reproductions and measurement scripts). LANE: jt3-r1 (sandbox; agent `code-implementer`, Opus 5.5,
in the SHARED tree, no worktree isolation). Do NOT spawn subagents. Report: `tasks/briefs/jev-laya/JT3-R1-report.md` (write it
incrementally from the start). This is the ONE repair D-031 allows for this contract revision: fix the set, not the instances.

## Boundary (MODIFY only these)

`.claude/hooks/search-intercept.py`, `tests/test_search_intercept.py`, `tests/test_session_hooks.py` (only the tests JT3 added or
edited), and your report. `scripts/install_session_hooks.py` and `.claude/settings.json` only if a fix below needs them (say why).
Measurement scripts go in a scratch directory under `/tmp`; paste their output. READ anything else. Report adjacent defects; never
fix them.

## The coordinator's disposition (the set each blocker names)

- **F-4, the tests' environment.** CI (`.github/workflows/stage0-ci.yml`) installs no graft and has no graft index. Every test that
  needs graft or rg carries a LOUD skip guard (`pytest.mark.skipif(shutil.which("graft") is None, reason=...)` and the rg twin, the
  pattern of `NEEDS_RG` in `tests/test_jev_locate_echo.py`). A test whose subject is fail-open or a quirk rule must RUN without graft
  or rg: it builds its own PATH and never depends on the host's tools. The sandbox run (graft present) keeps every test running.
- **F-1 and F-2, answer fidelity.** The class: an answer that differs from what the raw call would return. (a) Scope: a Grep-tool
  answer searches what the Grep tool searches (probe the Grep tool on a scratch repo with a hidden directory and an ignored file;
  never assume its rules); a Bash `grep -r` answer searches what `grep -r` searches, or its count line states exactly what it
  skipped; a Bash `rg` answer keeps rg's defaults. (b) Mode: names-only (`-l`, `files_with_matches`) and count-only (`-c`, `count`)
  calls are answered with names or counts, never with matching lines; any other output mode the hook cannot reproduce passes through
  (exit 0). The answer never shows fewer files than the raw call without saying so.
- **F-3, trailing-amp false positives.** D-2's false positive is a block of a command that would have run as intended (the
  verifier's reading; the coordinator adopts it). Narrow the rule: the `( ... & )` detach form is exempt, and a block needs a sign
  that backgrounding the whole list changes the outcome (for example `$!` used later, or a later step that depends on the list).
  Re-measure on BOTH transcript sets (the main transcript and the subagent transcripts; stream line by line, never whole; read at
  least 20 matches per set, or all) and paste the table. The rule ships only at 5% or less under that definition; otherwise it leaves
  SHIPPED and the report says so. The two live blocks in the verifier's section 3.2 (14:03:07 and 14:03:20) are negative cases.
- **Not in this repair** (they go to a verify-followup issue; do not fix): F-5, F-6, F-7, F-8a to F-8d, F-9 (say if your narrowed
  rule covers it), F-10, F-11, F-13, F-23, and the INFO rows.
- **Carry, read only.** JT1-R1 (live) makes `jev.rank` return None for a signal-free rank (D-076 (b)); the hook's None path falls
  back to file order (`search-intercept.py:877`). Never edit `scripts/jev.py`.

## Evidence demands

1. Premise: re-measure the block below; stop and report on any mismatch.
2. For each of F-1, F-2, F-3 and F-4: a new test that is RED on the PIN code for the reason the finding names and GREEN after, both
   runs pasted. For F-1 and F-2, a table over a scratch fixture (a hidden directory, an ignored file, a FAKE secret line): per tool
   and mode, the raw call's files or counts beside the hook's answer. The `_heredoc_delim` reproduction below must list the hook file.
3. `bash scripts/test_summary.sh tests/test_search_intercept.py tests/test_session_hooks.py tests/test_hooks_worktree.py --basetemp
   /tmp/jt3r1/bt` twice (graft present; make the parent first), then the pair `tests/test_search_intercept.py
   tests/test_session_hooks.py` under `PATH=/usr/local/bin:/usr/bin:/bin` (graft absent) and under a PATH with neither graft nor rg:
   0 failed in both, the skip counts pasted. `bash harness-ports/tests/run-all.sh`.
4. Mutants on scratch copies only (check the real hook's sha256 before and after every batch): drop a skip guard (run under the
   no-graft PATH); drop the Grep scope fix; answer a names-only call with lines; remove the detach exemption; plus JT3's four A5
   mutants. Each red on a named test; paste the kill table.
5. `python3 scripts/lint_delta.py --base HEAD` with no new hit, pyflakes on the two test files and the hook,
   `python3 scripts/no_laya_in_gates.py`, and the separator check below on every file you write.
6. The report: files and lines changed, pasted counts, the D-2 table, the mutant table, deviations with reasons, NOT-done.

## Standing rules

No outward actions (no commits, pushes, PRs, comments, GitHub writes, bridge calls, third-party APIs). Never create or remove
`.jev/intercept-off`: it holds the live hook off in this container; run the hook with a scratch `AF_SEARCH_INTERCEPT_STATE`. Never
edit `/home/user/.claude/settings.json`. Other lanes: JT1-R1 edits `scripts/jev.py`, `scripts/hiccup_scan.py`,
`tests/test_jev_client.py`, `tests/test_hiccup_scan.py` and `docs/HICCUPS.md`; FT1 creates `scripts/laya_ft/` and
`tests/test_laya_ft.py`; an OpenJev run writes `docs/research/findings/j2b-variants/openjev/`: never touch those. The local Laya
server (127.0.0.1:47411) is never stopped. Test secrets are FAKE strings (QZJ8... and X4Z9... style). No `-n` for pytest. Kill by pid
only. Check every file you write with `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`.

## PREMISE — MEASURED at authoring (2026-09-24 16:0xZ, /home/user/agent-factory at local HEAD 144c9a8)

```
$ sha256sum .claude/hooks/search-intercept.py tests/test_search_intercept.py scripts/install_session_hooks.py tests/test_session_hooks.py .claude/settings.json
a8fd4d39471cd81371bf4a5b076f118fd51670c9140d06ca7a067567677f9d9d  .claude/hooks/search-intercept.py
fffeb5eeb12db260563bc72731587cc0a73b869e133c4ae58d2a4396270588b4  tests/test_search_intercept.py
30c4862939017c5c8a3e93fa40c2d609f269f23e84bdf97c5169ee1c947c20b9  scripts/install_session_hooks.py
87aa2f4e59498477859bd7b06cbafc09d8ae5c29ea03ce32aa41eb8d65ab4f54  tests/test_session_hooks.py
ad7fe12e10a72d510ad6fec560dc031b903926338e32ac5dd9534318b5da996c  .claude/settings.json
$ command -v graft rg
/opt/node22/bin/graft
/usr/bin/rg
$ bash scripts/test_summary.sh tests/test_search_intercept.py tests/test_session_hooks.py tests/test_hooks_worktree.py --basetemp /tmp/jt3r1p/bt
pytest-exit: 0
pytest-summary: 87 passed in 21.78s
$ PATH=/usr/local/bin:/usr/bin:/bin bash scripts/test_summary.sh tests/test_search_intercept.py tests/test_session_hooks.py --basetemp /tmp/jt3r1p/bt2
pytest-exit: 1
pytest-summary: 10 failed, 71 passed in 7.53s
$ (F-1) the hook, scratch state, payload {"tool_name":"Grep","tool_input":{"pattern":"_heredoc_delim"},"cwd":"/home/user/agent-factory"}
rc 2; count line: rg: 9 hits in 1 file (all shown, file order):
$ rg -l --hidden --glob '!.git' _heredoc_delim /home/user/agent-factory
/home/user/agent-factory/.claude/hooks/search-intercept.py
/home/user/agent-factory/tasks/briefs/jev-laya/VERIFY-JT3-report.md
$ (F-3) the hook, scratch state, payload {"tool_name":"Bash","tool_input":{"command":"( cd /tmp && nohup sleep 1 > /dev/null 2>&1 & )"}}
rc 2; first line: QUIRK GUARD (search-intercept.py, rule trailing-amp): this Bash command was NOT run; repeat the identical call within 120 s for the raw result.
```

The one file of the F-1 answer is the verify report (it quotes the identifier); the defining file under `.claude/` is missing.
