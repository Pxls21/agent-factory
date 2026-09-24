# VERIFY-COORD-0924: the independent verify of three coordinator landings of 2026-09-24 (rule 0f)

Role: adversarial-verifier (sandbox, Opus 5.5). PIN: the local HEAD named in the dispatch message (the three landings below are in it).
Report: `tasks/briefs/kit-k1-support/VERIFY-COORD-0924-report.md` (write it incrementally from the start).

Each landing below was built and gated by the coordinator alone, so each is GATED-PENDING-VERIFY. Attack each against its own contract
(stated below), with NEW shapes, never only the coordinator's cases. Report every meaningful observation with no severity filter, then
apply the blocking predicate (contract-mapped, reproduced through the real path, materially effective, a concrete discriminator,
in-boundary) and give one GATE RECOMMENDATION per landing: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID.

## L1: the five project hooks in a `/home/user`-rooted session (task #214, AF-AP-172; commit "hooks: all five project hooks live…")

Files: `scripts/hook_context.py`, `scripts/install_session_hooks.py`, `tests/test_session_hooks.py`, `.claude/settings.json` (the
PostToolUse and PreToolUse commands now go through `hook_context.py`), the new block in `scripts/setup.sh` and the new line in
`scripts/resume-heal.sh`. The live file is `/home/user/.claude/settings.json` (READ it; never edit it).

Contract:
- `hook_context.py <Event> -- <cmd...>`: stdin passes through unchanged; exit 0 with output gives ONE JSON object
  `{"hookSpecificOutput": {"hookEventName": <Event>, "additionalContext": <output without its final newline>}}`; exit 0 with no output
  prints nothing; a non-zero exit passes stdout, stderr and the exit code through unchanged (a blocking hook's exit 2 keeps its
  meaning); a usage error or a command that cannot run prints one stderr line and exits 0 (a broken registration never blocks).
- `install_session_hooks.py [--target PATH] [--check | --remove]`: writes the five entries (SessionStart, UserPromptSubmit, PostToolUse
  matcher `Edit|Write|Read`, PreToolUse matcher `Grep`, Stop) with absolute paths; replaces ONLY entries whose command names
  `<repo>/.claude/hooks/`; keeps every other key and entry; refuses (exit 1, file untouched) a file that is not a JSON object; the
  write is atomic; a second run is a no-op; `--remove` restores the file to exactly what it was before our entries; `--check` exits 0
  only when the file already holds exactly our entries.
- The Codex and Hermes adapters under `harness-ports/` still parse the hooks' PLAIN output (the hook scripts are unchanged).

Suspicions to test (not a limit on what you look at): output that is not valid UTF-8, or very large; a hook that writes to stderr and
exits 0; a hook that times out near the 55 s wrapper limit; a repo path with a space or a quote; a foreign hook entry whose command
happens to contain our marker path; `--remove` on a file where the owner hand-edited one of our entries; concurrent installs; the file
mode and ownership after the atomic replace; what Claude Code does when `cd <repo>` fails (repo absent) for each of the five events,
especially Stop and SessionStart; whether any installed command reads anything from the current directory before its `cd`.

## L2: the CI-race fix and its registry row (AF-AP-181; commit "tests: one-read /proc state helper…")

Files: `tests/test_s0_01_frame_tee.py` (the helper `_proc_state_after_kill`, both call sites, the class `TestProcStateAfterKill`),
`.claude/hooks/edit-snapshot.py` (the TEST_SCREEN row AF-AP-181) and `tests/test_edit_snapshot_ap_screen.py` (`TestAFAP181`).
Contract: the helper reads `/proc/<pid>/stat` once; a missing file (ENOENT or ESRCH) reads as "gone"; the state letter is taken after
the LAST `)`; both sites accept exactly `("Z", "gone")`. The screen row fires on the shape "a race handler whose fallback value its own
assert rejects" (an `except` that assigns a string literal, then within two lines an `assert <same name> == <a different literal>`)
and stays quiet on the fixed shape. Find a shape of the same class the row misses, and a legitimate shape it flags.

## L3: the never-a-gate screen's vocabulary gains `mojev` and `packedscorer` (D-071, J1-0 AMENDMENT 6)

Files: `scripts/no_laya_in_gates.py` (`SIMPLE_TOKENS`) and `tests/test_no_laya_in_gates.py` (`test_mojev_vocabulary_fires`,
`test_simple_tokens_locked`). Contract: both tokens fire case-insensitively as whole maximal runs of `[A-Za-z0-9_-]` in every listed
gate file, with the exact `path:line:token` line; longer runs (`mojev_probe`, `packedscorer_test`) stay clean; the live tree stays
clean; the lock test names the whole list. Check whether any spelling MoJev's own code or CLI uses (read the audit's evidence file
`docs/research/findings/jev-audit/mojev-evidence.md` row 10.5) would still pass a gate file unflagged.

## Evidence rules

Reproduce every claim you rely on. Paste counts and outputs from commands you ran. Mutants run on scratch copies ONLY (never edit,
stash, restore or check out a tracked file in this tree). Record which model served your turns if you can see it. The sandbox venv has
no pytest-xdist: never pass `-n`. Use a short `--basetemp` (for example `/tmp/vc2/bt`; `mkdir -p` its parent first).

## Standing rules

Do not spawn subagents. No outward actions (no pushes, PRs, comments, GitHub writes). Do not commit. Never edit
`/home/user/.claude/settings.json` or any `.claude/` file; run installs only with `--target` pointing into your own scratch directory.
Another agent is editing `src/agent_factory/decisions/volatile.py`, `tests/test_decisions_canonical.py` and
`tests/test_decisions_ledger.py` right now: never touch or run those. Never print a secret; test secrets are fake strings.

## PREMISE — MEASURED at authoring (2026-09-24 11:4xZ, /home/user/agent-factory at e8692c2)

```
$ for f in ...; do git rev-parse --short=12 HEAD:$f; done
9d49a8de0577 scripts/hook_context.py
9fdb4b6c1a72 scripts/install_session_hooks.py
b2a8bf7744d0 tests/test_session_hooks.py
ad968bc98b60 .claude/settings.json
071bb0cf6a29 tests/test_s0_01_frame_tee.py
57e41b13faa0 .claude/hooks/edit-snapshot.py
1ec171f90691 tests/test_edit_snapshot_ap_screen.py
3eb0b06249fe scripts/no_laya_in_gates.py
4c8688e3483a tests/test_no_laya_in_gates.py
$ python3 scripts/install_session_hooks.py --check
session hooks: present in /home/user/.claude/settings.json
$ pytest tests/test_session_hooks.py tests/test_edit_snapshot_ap_screen.py tests/test_no_laya_in_gates.py -q
309 passed in 11.87s
$ pytest tests/test_s0_01_frame_tee.py -q -k 'ProcStateAfterKill or kill'
13 passed, 108 deselected in 7.46s
```
