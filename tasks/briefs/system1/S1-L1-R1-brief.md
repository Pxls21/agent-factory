# S1-L1-R1: one focused repair of the situation-to-skill hook (the VERIFY-S1-L1 follow-ups; skill contract-gate)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/S1-L1-R1-report.md` (write it
incrementally from the start). PIN: f259652 (origin; the hook, its table and its tests are unchanged since the landing
6195b77, measured below). The frozen contract: `tasks/briefs/system1/S1-L1-brief.md`. The verdict and its evidence:
`tasks/briefs/system1/VERIFY-S1-L1-report.md` (read its FINDING INVENTORY first). The builder's report:
`tasks/briefs/system1/S1-L1-report.md`.

## WHY

The independent verify returned MERGE-READY-WITH-FOLLOWUPS: no blocker, but a row can deliver a rule without its qualifying
line (F2), the committed tests let 7 of the verifier's 8 injected bugs through (F10), a lock held by another call breaks the
once-per-window rule (F8), and an excerpt whose first line is too long is dropped with its pointer (F4; the coordinator reads
the contract's "cut at a line boundary and keep the pointer" as covering it, so F4 is required here). This is the ONE repair
round the contract gate allows: fix the whole set, and prove it with the verifier's independent reproductions, not with new
cases of your own alone.

## CONTRACT (each item: first a committed test that FAILS on the PIN for the stated reason, then the fix)

1. **F2, whole entries.** Every row's excerpt starts where a skill entry starts and ends where an entry ends; the verifier's
   `rows_static.py` finds 0 runs inside an entry. In particular: `push` gains the qualifier the verifier names (the CTX1 note
   on the `git checkout -- AGENTS.md CLAUDE.md` step); `push-delegate-work` starts at its entry's first words and ends after
   its last sentence; `test-edit` and `gate-edit-tactics` end after the NaN numeric-guard rule or stop before it. Where whole
   entries exceed the budget, split the row (a second row, or its own call) rather than cut inside an entry, and show on the
   replay how often each part arrives in a window (the verifier: "Push the REVIEWED SHA explicitly … never HEAD" never
   arrived in 19 of 131 windows). Two rows carried from the S1-L1 harvest: the `push` row also delivers env-tool-quirks'
   entry on `push_clean.sh --lanes-live` counting tracked dirt only; and a row for the orchestration subsection "A lane that
   registers a hook changes the coordinator's own session", if a tool input can detect its situation (a brief written under
   `tasks/briefs/` whose text names `.claude/settings.json` or `install_session_hooks.py`, or a command that runs the
   installer). If the table cannot express that detection, say why and give it no row.
2. **F10, the tests.** The verifier's 8 mutants (`mutate.py`) are each KILLED by a FAILED test. The tests the verifier names:
   a parallel burst on one window (the lock), a budget boundary inside a multi-byte character, a lower-case canary in a
   Write/Edit path, in Write/Edit content and in a prompt, searched in every state file (telemetry, marker, cache), the 7-day
   prune, and the unresolved-row skip through the registered command.
3. **F8, the lock.** On a lock timeout the call injects nothing and logs why (fail quiet); a line is never delivered twice
   in a window and never lost from the marker because of a held lock. Correct the docstring at the lock (lines 472-473 at
   the PIN).
4. **F4, the pointer.** When no line of a matched excerpt fits its share, the call emits the excerpt's label and pointer;
   the verifier's `f4_prompt_pointer.py` exits 0.
5. **F5, one-word leads.** A section whose only lead is one heading word needs a second lead word or a higher threshold.
   Report, on this session's prompts (counts only), the injections and the verifier's strong/weak split before and after.
6. **F6, quoted and heredoc text.** Command rows do not fire on text inside quotes or a heredoc body, except where a shell
   reads that text (`bash -c '…'`, `sh -c`, `pc.sh '…'`, `ssh <host> '…'`, `bash <<EOF`, `python3 - <<'PY'` is data, not a
   shell). Report the replay's per-row injections and the nested commands kept, before and after (the builder's D11 counted
   328 real nested commands inside quotes).
7. **F1.** `while`, `until`, `if`, `elif`, `!` and `{` start a command position; `f1_while_pgrep.py` exits 0.
8. **F7.** The command-position scan is linear: a 198 KB heredoc (the verifier's case) takes under 100 ms in process.
9. **Small fixes:** F9 (a failed marker or cache write removes its temp file), F12 (`os.path.lexists` for the kill switch),
   F16 (one bad row, a regex error or a missing skill file, skips that row only; `re.error` logs as its type), F17 (skill and
   table reads never block on a FIFO), F19 (`install_session_hooks.py --remove` removes only our exact commands, never a
   foreign hook in the same group).

The verifier's INFO findings F3, F13, F14, F15, F18, F20, F21 and F23 need no change here; the builder's D4 is accepted.

## ACCEPTANCE (the verifier's set is the bar; paste every output)

- **Fix the verifier's mutation harness first, in a copy in your scratch.** The coordinator measured it scoring a setup
  error as a kill. With its `--basetemp` parent `bt/` missing, all 8 mutants read KILLED on "2 passed, 1 error". A kill
  needs at least one FAILED test; a run with only errors is INVALID; an unmutated control run must pass before any mutant
  runs. Then: 8 of 8 KILLED by failed tests.
- The verifier's reproductions (its scratch, below; run `bash setup_copy.sh` after your change is in place): `f1_while_pgrep.py`,
  `rows_static.py` and `f4_prompt_pointer.py` exit 0; `conc_dyn.py` shows no line twice and none lost with an external
  lock holder (it exits 0 today and prints the evidence: make your own test rc-gated); `hostile.py`, `ks_secrets.py`,
  `window_dyn.py` and `rows_dyn.py` still hold; `replay.py`'s numbers before and after.
- The 124 existing tests plus yours, `bash scripts/test_summary.sh` twice with the set id; pyflakes rc 0;
  `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0 for every file you write.

## LIVE-FILE RULE (AF-AP-222)

`.claude/hooks/system1-context.py` and `.claude/hooks/system1-situations.json` run LIVE on every Write, Edit and Bash call of
every session in this container, your own included. Never edit them in place: write the new version in your scratch, prove it
there (`python3 -m py_compile`, `json.load`, its tests against the scratch copy), then put it in place with one `mv` on the
same filesystem. Keep the previous version in your scratch; if a live call breaks, put it back at once and say so.

## BOUNDARY

MODIFY: `.claude/hooks/system1-context.py`, `.claude/hooks/system1-situations.json`, `tests/test_system1_context.py`, and for
F19 only `scripts/install_session_hooks.py` and `tests/test_session_hooks.py`. CREATE: your report, new test files under
`tests/` if you need them. The verifier's scripts in
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-s1l1/` are the independent oracle: copy
what you run into your scratch and fix only the copy (the harness classification above); never edit the originals. No skill
file: where a fix needs a skill line broken in two (the verifier's D9: `pc-bridge-lanes` lines 19 and 23 are single 4.8 KB
lines; the `pc-suite` and `anchor-edit` rows need a break), write the proposed break as a patch in your report and the
coordinator applies it. A new file under `.claude/` changes the vendored manifest: list it; the coordinator regenerates the
manifest. Other lanes are live in this tree: INSTALL1 (`scripts/setup.sh`, `harness-ports/bin/pc-setup.sh`,
`upstream.lock.yaml`, `scripts/hooks/post-commit`, `.gitignore`, slopo files) and L5 (`scripts/chat_find.py`,
`tests/test_chat_find.py`): touch none of their files.

## STANDING RULES

No git writes; no PC bridge; no outward-facing action. Transcripts hold secrets: the replay and the prompt counts print and
store counts, ids and positions only. Test secrets are fake strings built at run time. The disk is shared (1.8G free; INSTALL1
must keep 1 GB): scratch under 200 MB in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/r1/`, deleted
as you go; a short `--basetemp` there with its parent created first. Test counts are pasted from `scripts/test_summary.sh`;
stamps from `date -u`. Long commands in one foreground call; kill by pid, never by name.

## PREMISE — MEASURED at authoring (2026-09-25 17:4xZ)

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf
f259652 container restart 16:4xZ: INSTALL1, VERIFY-S1-L1 and L5 re-dispatched as continuations from 
$ git diff --stat 6195b77 origin/claude/soundbox-kit-migration-iz1jwf -- .claude/hooks tests/test_system1_context.py scripts/install_session_hooks.py tests/test_session_hooks.py   (empty = unchanged since the landing)
$ git show <PIN>:<file> | sha256sum | cut -c1-16
a3e37aba8adbc014  .claude/hooks/system1-context.py
eef9252d0c0c2b9f  .claude/hooks/system1-situations.json
2bd7568e12822e32  tests/test_system1_context.py
a6632b8003ccffe3  scripts/install_session_hooks.py
06490455c7163016  tests/test_session_hooks.py
$ bash scripts/test_summary.sh tests/test_system1_context.py tests/test_session_start_hook.py tests/test_session_hooks.py tests/test_hooks_worktree.py   (the coordinator, at the S1-L1 harvest)
pytest-summary: 124 passed in 14.25s
4 files set=2dc71b948b8b
$ cd /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-s1l1 && bash setup_copy.sh && python3 <script>   (the verifier's reproductions, run by the coordinator after the verdict)
f1_while_pgrep.py rc=1 0s last: pgrep row on `while pgrep …`: NOT injected | matched: []
rows_static.py rc=1 0s last: 17 row runs start or end inside an entry
f4_prompt_pointer.py rc=1 0s last: best: pc-bridge-lanes § Launching, re-attaching and sizing PC lanes | its pointer in additionalContext: False | sk
conc_dyn.py rc=0 4s last: stray tmp files: []
hostile.py rc=0 2s last:      the next call in that window injects: False | error: JSONDecodeError
ks_secrets.py rc=0 1s last: injections that happened (so the canaries rode through real work): [2, 1, 2, 3, 0, 2, 0, 0]
window_dyn.py rc=0 2s last: A.main marker idle 8 days, after another session's startup: exists = False | A.main injects again: True
rows_dyn.py rc=0 6s last:    ('brief-contract', 'brief', 'out of order')
$ mkdir -p bt && /root/venv-agent-factory/bin/python mutate.py   (with the --basetemp parent present)
SURVIVED m1 m2 m3 m4 m5 m7 m8 (each "91 passed"); KILLED m6 ("1 failed, 79 passed": test_the_tool_budget_cuts_at_a_line_boundary_and_...)
$ the same WITHOUT bt/ (deleted by the verifier cleanup)
KILLED m1..m8, every one "2 passed, 1 error in 0.0Ns"  <- a setup error scored as a kill: the harness is hollow until fixed
$ df -h / | awk "NR==2{print \$4}"
1.8G
```

A question for you, not a fact: which single-word-lead rule keeps the verifier's 23 strong prompt-path matches and drops most
of its 54 weak ones? Measure two candidates before choosing.
