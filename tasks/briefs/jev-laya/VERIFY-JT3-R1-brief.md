# VERIFY-JT3-R1: the independent verify of the search intercept and quirk guard after its one repair (tasks #228, #225, #236)

Role: adversarial-verifier (sandbox, Opus 5.5). PIN: the content of the files hashed below (JT3 plus JT3-R1, uncommitted in the
shared tree; re-measure the digests first). Report: `tasks/briefs/jev-laya/VERIFY-JT3-R1-report.md` (write it incrementally).

JT3-R1 is the ONE repair D-031 allows for this contract revision, after VERIFY-JT3 returned NOT-READY on F-1 (a Grep answer skipped
hidden paths), F-2 (names and count modes answered with lines), F-3 (trailing-amp false positives) and F-4 (tests red without graft).
Attack the repaired hook against its FULL contract (`tasks/briefs/jev-laya/JT3-brief.md`, D-1 to D-5 and A1 to A5), the repair brief
(`tasks/briefs/jev-laya/JT3-R1-brief.md`) and VERIFY-JT3's findings (`tasks/briefs/jev-laya/VERIFY-JT3-report.md`), with NEW shapes,
never only the lane's cases; the lane's report is `tasks/briefs/jev-laya/JT3-R1-report.md`. Report every meaningful observation with
no severity filter, then apply the blocking predicate (contract-mapped, reproduced through the real path, materially effective, a
concrete discriminator, in-boundary) and give ONE gate recommendation: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY /
CONTRACT-INVALID.

## The coordinator's rulings the repair was built on (grade against these)

- **F-3's false positive** is a block of a command that would have run as intended. A later step that reads `$!` (or a variable the
  backgrounded list assigned) is HARM even when it only prints it: `$!` then names the subshell, not the job (CLAUDE.md, the
  2026-09-21 pidfile race). Under that reading the lane measured 1 false positive in 53 fires over both transcript sets; re-grade the
  lane's classification in its section 3.2 and say whether 5% or less holds.
- **The premise's F-1 count** read "13 hits in 3 files" at the repair's start where the brief pasted "9 hits in 1 file": the extra
  hits are the brief and its ledger line, committed later. The substance (the defining file missing) held; the lane went on.

## Suspicions to test (not a limit)

- F-1 and F-2 as a set: does every answer search what the raw call searches, in its mode (lines, names, counts), and say exactly
  what it skipped? Try shapes the lane did not: `.rgignore`, a global git excludes file, a symlinked directory, a file over rg's
  size limit, a path argument that is a file, a glob with a hidden segment, `grep -rl` with `--include`, the Grep tool's `type`
  and `-i`, case differences, and a pattern with regex metacharacters.
- F-3: the narrowed rule on shapes outside the 53 fires (subshells, `wait`, functions, `coproc`, a `$!` inside a quoted string, a
  multi-line command), both directions (a harmful command passed, a harmless one blocked). The lane reported one shape it would
  still block wrongly (`( a && job & more ) ; echo $!`); confirm or refute.
- F-4: the suites under the CI workflow's declared tool set (no graft; no graft and no rg), and whether any skip hides a test that
  could run.
- Regressions on what VERIFY-JT3 found sound: fail-open (D-3), the 9,000-character cap (D-4), the escape hatch, the off switch, the
  Jev switch off by default.
- The follow-ups in issue #71 (F-5 to F-13, F-23) are NOT part of this repair: note whether the repair changed any of them.

## Evidence rules

Reproduce every claim you rely on; paste counts and outputs from commands you ran. Mutants on scratch copies ONLY (never edit, stash,
restore or check out a tracked or lane file in this tree), one fresh copy per mutant with `PYTHONDONTWRITEBYTECODE=1` (AF-AP-192).
Run the hook only with a scratch `AF_SEARCH_INTERCEPT_STATE`. Use a short `--basetemp` (make the parent first); never pass `-n`.
Record which model served your turns if you can see it.

## Standing rules

No outward actions (no commits, pushes, PRs, comments, GitHub writes, bridge calls, third-party APIs). Do not spawn subagents. Never
create or remove `.jev/intercept-off` (it holds the live hook off). Never edit `/home/user/.claude/settings.json`. Other lanes: JT2-R1
edits `scripts/jev_context.py`, `scripts/jev_locate.py`, `scripts/jev_echo.py` and their tests; VERIFY-FT1 reads `scripts/laya_ft/`:
never touch those. The local Laya server on 127.0.0.1:47411 is never stopped. Test secrets are FAKE strings (QZJ8... and X4Z9...
style). Kill by pid only (never `pkill`, the JT3-R1 lane slipped once). Check every file you write with
`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`.

## PREMISE — MEASURED at authoring (2026-09-24 17:2xZ, /home/user/agent-factory, local HEAD 8186e7e after the push)

```
$ sha256sum .claude/hooks/search-intercept.py tests/test_search_intercept.py tests/test_session_hooks.py
927410a382b2138fac9bd06e8f84c31e9411301a69005192e5b9b427c17e5b2c  .claude/hooks/search-intercept.py
ffb8f18123a4f0e024817b064a6fa77ddf9ee090839fdd5cc000dfaf61782096  tests/test_search_intercept.py
2a3a90c86ba3001e13bf92922352c0b4dc5652bb376d1d4e74c348d2afa2c254  tests/test_session_hooks.py
$ sha256sum scripts/install_session_hooks.py .claude/settings.json   (unchanged by the repair; JT3's versions)
30c4862939017c5c8a3e93fa40c2d609f269f23e84bdf97c5169ee1c947c20b9  scripts/install_session_hooks.py
ad7fe12e10a72d510ad6fec560dc031b903926338e32ac5dd9534318b5da996c  .claude/settings.json
$ bash scripts/test_summary.sh tests/test_search_intercept.py tests/test_session_hooks.py tests/test_hooks_worktree.py --basetemp /tmp/j3c/bt
pytest-exit: 0
pytest-summary: 117 passed in 48.46s
$ PATH=/usr/local/bin:/usr/bin:/bin bash scripts/test_summary.sh tests/test_search_intercept.py tests/test_session_hooks.py --basetemp /tmp/j3c/bt2
pytest-exit: 0
pytest-summary: 78 passed, 33 skipped in 19.38s
```
