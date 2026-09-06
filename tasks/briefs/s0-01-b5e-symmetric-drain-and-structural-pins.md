# BRIEF — S0-01 lane B5e: the tee drains BOTH directions to EOF, every lock/order/timeout rule is pinned structurally, the SIGTERM path is complete from the first millisecond, every test cleans up (VERIFY-B5d, round 9)
PIN: (set at dispatch)

You are the sandbox BUILD lane (Opus 4.6 `code-implementer`). honey: ultra. Your output is a PROPOSAL graded by VERIFY-B5e; never
self-accept. Interpreter `python3`. Edit the shared tree IN PLACE — no worktree, no branch, no commits, no git state changes (never
`git stash`/`checkout`/`restore`/`reset`). Other lanes may be live in the tree (the dispatcher lists their files) — never touch them.
Long runs in ONE foreground call; no xdist; `--basetemp` under …/scratchpad/lb5e/ per run, deleted after; the contended pair
(nice 19, four burners) is the only load you add, serially at the end; `df -h /` first. Report to …/scratchpad/wf-results-r5/B5e.md.

FIRST ACTION (halt loud on mismatch): `git rev-parse HEAD` equals the PIN; your two boundary files are clean at HEAD;
`bash scripts/test_summary.sh tests/test_s0_01_frame_tee.py` → the count at the PIN (paste it — the xfail test was rewritten by lane A5g
into a plain passing test, so expect `84 passed` or the dispatcher's stated count). Then REPRODUCE R9-B5d-F3 before touching code and paste
it: an agent whose grandchild inherits its stdout and writes one frame 6 s after the agent exits → today the tee exits at ~5.1 s with
rc 0, `drained true`, `write_errors []`, and the frame is in NEITHER the timeline nor the a2c file — SILENT LOSS, exit 0.

## The verdict you are closing — `tasks/briefs/s0-01-b5e-support/verify-B5d.md` (read it whole; the rulings below are binding)
BLOCKING:
- F3 (the contract is SYMMETRIC): the a2c drain runs UNTIL EOF on the agent's stdout, exactly as c2a runs until client EOF — the
  `stall_timeout = 5` loop at ~:417-442 goes; a grandchild that holds the fd keeps the tee alive and buzz-acp's SIGTERM path (non-final,
  exit 70, `["terminated: SIGTERM"]`) is the bound, as for a client that never closes. Rewrite `test_grandchild_holds_stdout_drained`
  (~:858-894) to the new contract — it currently PINS the silent loss (rc 0, drained true, [] with the frame missing): a grandchild that
  writes a frame 6 s after the agent's exit and then closes → the frame is in the timeline AND the a2c file, forwarded to the client,
  rc 0, `drained true`, `write_errors []`; a grandchild that never closes → the tee is alive at 15 s (`/proc` state, not output), then
  SIGTERM → rc 70 non-final. Docstring ~:16-17 rewritten (no "5 s stall" clause). Mutants: an a2c stall timeout re-introduced at
  0 / 5 / 30 s — each killed by a NAMED test.
- F2 + F5 + F11 (structural pins, no probabilistic killers): (a) an `ast`-level test that BOTH drain loops (`while ti.is_alive()` and
  the new a2c loop) contain only `time.sleep(...)` + `_write_status()` — no `break`, no `time.monotonic()` comparison — kills A2-t30
  and the a2c timeouts deterministically; (b) an `ast`-level test that in both pumps the timeline write precedes the directional write
  inside the `with lock:` body — kills N3 deterministically (it killed 1 run in 4); (c) a test with a MAIN-THREAD status write concurrent
  with a live pump: the agent exits while the client holds stdin open and the agent's grandchild keeps streaming a2c frames, a spinning
  reader ≥ 10 000 reads → `torn == 0` and `updated_seq == recorded_c2a + recorded_a2c` on every read — kills N4 (the inner `with lock:` is
  a re-entrant no-op on the hot path) and D3 (`status_lock` dropped); (d) in `test_sigkill_leaves_nonfinal_status` and
  `test_directional_trails_timeline_after_sigkill` assert `0 <= timeline_last_seq - status["updated_seq"] <= 1` — kills S1 (status written
  before the timeline line). Every one of N3, N4, D3, S1, A2-t30 must die on a NAMED test, full suite, no `-x`.
- F4 the report's mutant table asserted killers that do not exist: your table is a MEASUREMENT — paste the runner's lines per mutant
  (`scratchpad/vb9/work/mut9.py` is the verifier's 59-mutant runner; use it, re-aim what your edits move, say which).
NON-BLOCKING, ship them:
- F1 is lane A5g's (the rewritten `test_sigterm_status_satisfies_check_tee_status`) — READ-ONLY for you; do not touch that test.
- F7 `test_late_frame_after_reap_with_client_holding_stdin` (~:344-393) and `test_tee_exits_cleanly_with_agent_code` (~:400-452) never
  wait for the reap (the agent closes fd 0 before the handshake; the EPIPE is its own): rename each to what it proves
  (`…_agent_stdin_closed_before_handshake`) or add the sentinel wait the other test uses (~:1869-1876) — say which.
- F8 `test_stdin_reader_done_false_when_client_never_closes` (~:1236-1245) proves no liveness (its wait is satisfied by the INITIAL
  status write): gate on `stdin_reader_done is False and recorded_a2c >= 1`, then sleep 15 s and `assert tee_proc.poll() is None`
  BEFORE the SIGTERM.
- F15 `test_directional_trails_timeline_after_sigkill` can pass on twelve empty trials: `assert all(r and r["tl_c2a"] >= 100 for r in results)`.
- F6 the gap sweep parametrisation gains 4 and 12 (`[1, 4, 6, 8, 12]`); no "8/8" claim without a producer in the tree.
- F12 the twelve unguarded `Popen` tests (the verdict lists them by line) get the `try: … finally: if p.poll() is None: p.kill(); p.wait(5)`
  wrapper already used at ~:325; paste the AST census (guarded/unguarded) after.
- F13 the SIGTERM handler is installed AFTER `Popen` and three sha256 reads (~:406 vs :117): a TERM in the first ~40-80 ms leaves NO
  status and rc −15. Move the handler install (and the `try:`) to right after the framedir validation, before the spawn; red test: TERM at
  10 ms → rc 70, `write_errors == ["terminated: SIGTERM"]`, status present (non-final).
- F14 the SIGTERM path orphans the agent: `proc.terminate()` (guarded) before `os._exit(70)`; red test: after SIGTERM the agent pid is gone
  within 2 s.
- F9/F10 (for the record, not code): the B5d brief's "snapshot after the increment" ruling is AMENDED — a running snapshot may trail
  the last forward by one frame (`recorded - forwarded ∈ {0,1}`), the final status is exact; the invariant list is QUALIFIED: 3 and 4
  hold only while no `forward <dir>:` error has been recorded (a broken forward is a failing leg the checker rejects — correctly); running
  snapshots normally carry `drained: false`; `updated_seq` is never ahead of the timeline. Put the qualified list in your report verbatim.
- F16 cost: re-measure the 11-frame real-leg shape on a quiet box against the 2× bar (the verdict measured 1.005× for B5d); paste the
  number with the load average. F17 report hygiene: the parent test file is 1724 lines; counts pasted, never typed.

## Boundary (touch ONLY): `proofs/S0-01/tools/frame_tee.py`, `tests/test_s0_01_frame_tee.py` (EXCEPT the test
`test_sigterm_status_satisfies_check_tee_status`, which lane A5g owns). READ-ONLY: `proofs/S0-01/pins.py`,
`proofs/S0-01/check_acp_conformance.py`, everything else. Mutants: copy your FINAL file to scratch, mutate the tree file, run, restore
from the scratch copy — never from git. Tests write only under `tmp_path`; every spawned tee/agent is killed in `finally`.

## Acceptance bar
The 59-mutant set re-run on the final tree (paste the runner's totals and every survivor with its equivalence argument; C4/N10/S2/A6/S4
may stay as stated equivalents); the new a2c timeout mutants (0/5/30 s), the handler-after-Popen mutant, the orphan mutant, N3, N4, D3,
S1, A2-t30 — each KILLED by a NAMED test; the grandchild straggler probe at 2/6/9 s all recorded; killsnap 20/20 with every diff ∈ {0,1};
the suite TWICE idle + ONCE contended (`bash scripts/test_summary.sh tests/test_s0_01_frame_tee.py`, all lines pasted); pyflakes rc 0;
`tmp_path` hygiene; the PC leg is the coordinator's (state NOT run here). Report fields: done (finding → test → red before / green after,
red output pasted), the qualified invariant list, the mutant table (measured), the probe table, not_done → reason (an empty not_done
beside an unmet item reopens the lane), files, summaries, discrepancies (halt and report rather than improvise), adjacent defects.
Standing rules: no subagents; no outward-facing actions; no commits. Authorization context: defensive verification tooling on the
owner's own system; the tee records the owner's own ACP frames; no credentials are involved.
