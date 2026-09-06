# BRIEF — S0-01 lane B5c: the frame tee's drain, running status and exit paths, graded by the round-6 verifier's findings
PIN: (set at dispatch — scripts/pc_lane.sh refuses to run without a full SHA here)

You are the BUILD lane (Hermes on the PC, role code-implementer). honey: ultra. `.hermes.md` carries the
project rules. Your output is a PROPOSAL: the sandbox adversarial verifier grades it against the full
contract; never self-accept, never issue a gate verdict. CONTEXT BUDGET: this brief plus the two files
plus the verify report fit one context — load no skills, read no other docs unless a seam below sends you
there. Write `report-draft.md` in your lane dir as you go (incremental-report rule, AF-AP-16).

FIRST ACTION (halt loud on any mismatch): `git rev-parse HEAD` equals the PIN; `git log --oneline -1`
subject starts `S0-01 WIP checkpoint 7:`; tree clean; `sha256sum proofs/S0-01/tools/frame_tee.py` starts
`214b65e9` (the file the verifier graded — if it differs, STOP: the premise moved). Then reproduce the
verdict's headline before changing anything: apply mutant A1 from
`tasks/briefs/s0-01-b5c-support/verify-B5b.md` (the c2a drain loop `while ti.is_alive():` →
`while False and ti.is_alive():`) on a scratch copy and run the tee suite — the brief's premise is that it
stays green (`68 passed`). If it does not, STOP and report.

## What this lane is for
The round-6 verifier (`tasks/briefs/s0-01-b5c-support/verify-B5b.md`, ids R6-B5b-F1…F20) returned
NOT-READY on the tee: the fix for the audit's P2 finding ("the tee can lose output and still exit 0") is
present in the code and guarded by NOTHING; a one-line revert keeps the suite green and reproduces the
audit signature (F1); the round-5 test that carried that shape was deleted (F2); an unwritable
`frames-client-to-agent.jsonl` hangs the tee forever with an EOF-consuming agent (F3); a race-dependent
test fails the contended gate 2/2 (F4); the A21d running status tears under SIGKILL in 15/20 trials (F5);
the SIGTERM status satisfies no contract arm (F6); `write_errors` is unbounded on six arms (F7); the
drain-stop reason is asserted with `startswith` (F8); status-write failures are silent and the tee exits
0 when it cannot write its own status (F9); no status exists before the first frame (F10); the SIGTERM
handler can self-deadlock on the non-reentrant lock (F11); no mutation pass was run (F12); dead code
(F13); the directional file can lead the timeline by one frame after SIGKILL (F17); docstrings overstate
"forwarded" (F18); the a2c pump has the same unhandled `finally` traceback (F19). Make every one of
these a RED test first, then green.

## Coordinator rulings (binding — the verifier asked for decisions; these are them)
- F6 (SIGTERM status): the TERM path writes a NON-final status (`final: false`, both exit fields null)
  with the entry `"terminated: SIGTERM"` appended to `write_errors`, then exits 70. Reason: a TERMed tee
  is an abnormal cleanup (`pc_post.sh` TERMs survivors) and the checker must see it as a non-clean leg;
  the A21d/A21b exit-field rules stay as they are. Assert `agent_returncode is None` in that test.
- F11 (handler deadlock): the signal handler takes NO lock — it raises a private exception
  (`_Terminated`) that the main thread catches at its top level, where it appends the F6 entry and writes
  the status outside any lock context (a `with` block unwinds and releases). Remove `rc_val` (F13).
- F5 (torn snapshot): `_write_status` snapshots `seq` and the counters under the SAME lock that guards
  the timeline write + counter increment (one atomic read of `(seq, recorded_*, forwarded_*)`), never
  under `status_lock` alone. Test = a concurrent reader asserting `updated_seq == recorded_c2a +
  recorded_a2c` on every snapshot, plus killsnap 20/20 A21d-consistent.
- F17 (directional leads the timeline): write the TIMELINE line first, then the directional line; both
  under the lock. After a SIGKILL the directional file may then be one frame SHORT of the timeline, never
  ahead. (The checker's tolerance for that on non-final legs is a separate checker item — not yours.)
- F7 (unbounded write_errors): one entry per (arm, direction) with a count, exact text
  `"<arm> <dir>: <errno text> (N occurrences)"` for repeated failures; first occurrence keeps the current
  exact text; the forward arms keep the `forward_broken` latch. Assert the exact single entry.
- F9 (silent status failures): count status-write failures; print ONE stderr line at exit with the
  count; an unwritable status at the FINAL write makes the tee exit 70 (a leg without its evidence file
  must not exit 0). Test with the status path symlinked to `/dev/full`.
- F10: one `_write_status()` immediately after `runtime-identity.json` is written (12 keys, zeros,
  `updated_seq 0`).
- F3/F19 (finally tracebacks): in both pumps the `finally` closes the directional file inside its own
  `try/except OSError` (error → `write_errors` entry `"directional <dir> close: <errno text>"`), then
  ALWAYS runs the rest (`stdin_reader_done`, `dst.close()`). Test = case B (unwritable c2a directional
  file, EOF-consuming agent) exits 70 within a bounded wait; case D2 (a2c) records the entry.
- F1/F2: add the p9-shaped test (a late client frame written ≥1 s AFTER `proc.wait()` returned, with the
  client holding stdin open) asserting the frame is in `frames-client-to-agent.jsonl` AND rc 70 AND the
  exact `write_errors` list; restore the deleted round-5 test `test_tee_exits_cleanly_with_agent_code`
  under the round-6 contract (rc 70, frame 2 recorded, exact list `["forward c2a: BrokenPipeError",
  "drain c2a: stopped with 2 recorded, 1 forwarded"]`). Both must be RED on the PIN's tee only through
  mutants A1/A3/A6 — i.e. they must kill A1, A2, A3, A4, A6 and the composed A3+A6.
- F4 (race-dependent test): apply the `712fe01` pattern to
  `test_agent_exits_without_consuming_stdin_exit_70` — the agent closes its stdin BEFORE answering and the
  client sends the late frames only after reading the answer — so every scheduling order yields rc 70.
- F8: the drain-stop assertion is exact list equality with counts computed from the status.
- F14 (the +5 s drain in the production shape): keep the 5 s stall window; the module docstring states
  the cost and that buzz-acp's 5 s shutdown kill can land inside the drain, which is why the status is a
  running file. F18: the docstring says "forwarded" = written into the agent's stdin pipe, not received.
- F16 (key set duplicated): the tee stays STANDALONE (no import of pins.py — it is a sha-pinned tool);
  the TEST imports `PINNED_TEE_STATUS_KEYS` from `proofs/S0-01/pins.py` (already added by the coordinator)
  and asserts the tee's key set AND ORDER equal to it; drop the test's local `STATUS_KEYS` copy.

- F-PC-1 (found 2026-09-06 by the first PC suite run — a venue-dependent DEADLOCK, AF-AP-46 sibling): `test_rewrite_is_atomic`
  hung in 4/4 PC sessions (`pytest -n 8` on 12 cores): its 500-frame fixture agent sat in `anon_pipe_write` after 165 frames with the
  tee alive and `forwarded_a2c == recorded_a2c == 165` — the test polls `tee-status.json` before draining the tee's stdout, so once the
  pipe capacity is reached (pipes drop to ONE page under `fs.pipe-user-pages-soft` pressure on a busy box) the agent, the tee and the
  test wait on each other forever. Ruling: the test drains the tee's stdout on a reader thread WHILE it polls, bounds every wait, and
  asserts the atomicity property it exists for (every snapshot is a complete 12-key JSON document) — never depend on pipe capacity to
  park output. Sweep the file for the same shape (any test that starts the tee, polls a file or sleeps, and only then calls
  `communicate()`): each is a finding to fix in this lane and to list in the report.

- F-PC-2 (same PC run): `TestTeeStatus::test_agent_burst_within_pipe_buffer_drained` timed out (`subprocess.TimeoutExpired … 15
  seconds`) — its premise "the burst fits the pipe buffer" is venue-dependent (see F-PC-1: pipe capacity is not a constant). Ruling:
  the test must not encode a pipe size; assert the drain property with a reader that consumes the tee's stdout concurrently, or size
  the burst from `fcntl.F_GETPIPE_SZ` on the actual pipe and prove the property on both sides of that measured value.
- F4 reproduced on the PC in the same run (`assert 0 == 70`, `test_agent_exits_without_consuming_stdin_exit_70`): the verifier's
  contended-gate failure is not a sandbox artefact.

## Deliverables (boundary — touch ONLY these two paths; everything else is read-only)
1. MODIFY `proofs/S0-01/tools/frame_tee.py` — the rulings above; module docstring updated (F14/F18, the
   TERM semantics, the write order); no new dependencies; Python 3.12+ stdlib only.
2. MODIFY `tests/test_s0_01_frame_tee.py` — one named test per finding (F1 F2 F3 F4 F5 F6 F7 F8 F9 F10
   F11 F17 F19), each RED before its fix; exact assertions only (no `in`/`startswith`/`or`, no two-sided
   counts); tests write only under `tmp_path`; timing tests follow AF-AP-46 (precondition before the
   handshake, never a scheduling race).

## Acceptance bar (the verifier's set is the bar — your own mutant list is not evidence)
Every survivor in the verdict's mutant table must be killed by a NAMED test: A1 A2 A3 A4 A6, the composed
A3+A6, B2, D3. Run the verifier's own runner `tasks/briefs/s0-01-b5c-support/probes/mut.py` (set
`PROBE_WORK=<your work dir>` holding `base/` = a copy of your finished tree, and `PROBE_TEE`) and paste
killed/total for all 43 + the composed one; replay `probes.py` p1–p8, `hang.py` (cases A–D), `killsnap.py`
(20 trials → 20/20 consistent), `sigterm_deadlock.py` (12 trials, all answered < 1 s), `f9probe.py`
(idle 12 + under 8 burners 12 → rc 70 every time), `lockrepro.py` (the handler no longer holds a lock), and
`cost.py` (the 11-frame shape stays within 2× of the pre-change median). Paste every table verbatim.

## Gate (paste verbatim into the report AND the commit body; VERDICT RED = the lane is not done)
- `$HOME/venv-agent-factory/bin/python -m pyflakes proofs/S0-01/tools/frame_tee.py tests/test_s0_01_frame_tee.py`
- `bash scripts/test_summary.sh tests/test_s0_01_frame_tee.py` twice IDLE, then twice CONTENDED
  (`nice -n 19` with four `yes > /dev/null` burners running) — four summary lines pasted.
- The mutant table and the probe tables above.
- Report fields: done (finding → test → the red observed before the fix / on revert), mutants killed/total
  with the survivor list, not_done (→ reason; an empty not_done beside any unmet item reopens the lane),
  files touched, the four summary lines, pyflakes, discrepancies with this brief, adjacent defects
  (report only — never fix outside the two files).

Standing rules: no subagents; no outward-facing actions (no PRs, comments, pushes; the coordinator
commits); long runs in ONE foreground call; never `git stash`/reset the worktree; every exact-text
claim above is a hypothesis — verify the seams at your PIN and STOP LOUD on contradiction. Authorization
context: defensive tooling on the owner's own system (the tee records the owner's own ACP traffic in a
test rig); no credentials are involved.
