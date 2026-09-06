# BRIEF — S0-01 lane B5d: the tee drains client frames until client EOF, the running status is written inside the timeline lock, every reverted fix gets its killing test (VERIFY-B5c, round 8)
PIN: (set at dispatch)

Build lane (sandbox Opus 4.6 code-implementer). honey: ultra. Your output is a PROPOSAL graded by the round-9 verifier. Read in order:
this brief; `tasks/briefs/s0-01-b5d-support/verify-B5c.md` (the verdict — every finding id below refers to it, with its exact probes and
red tests); `tasks/briefs/s0-01-b5c-frame-tee-repair.md` + `tasks/briefs/s0-01-b5c-support/verify-B5b.md` (the previous rulings and
findings); the probe scripts under `tasks/briefs/s0-01-b5c-support/probes/` and the verifier's re-aimed runner at
`scratchpad/vb8/work/mut8.py` (+ its probes) if present — use them.

FIRST ACTION (halt loud): `git rev-parse HEAD` equals the PIN; `bash scripts/test_summary.sh tests/test_s0_01_frame_tee.py` → `78 passed`;
then REPRODUCE R8-B5c-F1 before touching code — the p9 shape with a 6 s gap (agent reads one line, answers, exits 0; the client holds
stdin open and sends frame 2 six seconds later) → today `rc 0, recorded 1 of 2, drained true, write_errors []` (SILENT LOSS). Paste it.

## Coordinator rulings (binding)
- R1 (F1/F2/F12/F14 — the drain contract): after the agent exits, the tee drains client frames UNTIL CLIENT EOF — there is no stall
  timeout on the c2a side; every frame the client writes before closing its end is recorded; `stdin_reader_done` is true on every
  clean exit; the 5 s per-leg drain cost disappears. A client that never closes keeps the tee alive — that is buzz-acp's shutdown
  responsibility (it TERMs/KILLs the group), and the SIGTERM path (non-final status, exit 70) covers it. Rewrite the docstring's
  contract paragraph accordingly. Tests: the p9 shape with gaps of 1 s, 6 s and 8 s → the late frame is recorded and, once the
  client closes, rc 0 with `drained true`; the "after reap" test genuinely waits for the agent's death (poll `tee-status.json`
  `agent_returncode`/a sentinel file) before sending the late frame; the mutant "exit when the agent exits" (the old timeout with
  any value, including 0) must be killed by these tests — paste the runs.
- R2 (F3/F5/F6/F9 — status consistency): `_write_status` runs INSIDE the timeline lock immediately after each timeline write (the
  per-frame snapshot cannot be torn and trails the timeline by at most the frame whose line is written but whose status write was
  interrupted); `forwarded_<dir>` is incremented under the lock after the forward completes and the snapshot is taken after that
  increment, so `forwarded == recorded` on every snapshot except the single in-flight frame. Invariants the tests pin, under
  bidirectional load with a spinning reader (≥ 10 000 reads) and across 20 SIGKILLs: `updated_seq == recorded_c2a + recorded_a2c`
  on EVERY snapshot; `timeline_last_seq - updated_seq ∈ {0, 1}`; `recorded_<dir> - forwarded_<dir> ∈ {0, 1}` on running snapshots
  and `== 0` on the final status; the directional file never ahead of the timeline (12 trials, both directions loaded, `len(results)
  == 12`). Mutants N4 (snapshot outside the lock), D3 (no status_lock), N3 (write order swapped), C1 (no c2a running status) must
  each be killed by a NAMED test. (The checker's A21d rule for NON-final legs is relaxed to these same bounds by a separate checker
  lane — report the exact invariants you implemented so the two sides agree.)
- R3 (F4 — the SIGTERM status): unchanged on the tee side (non-final, `["terminated: SIGTERM"]`, exit 70); the checker will whitelist
  exactly that entry on non-final legs (separate lane). Add the test the verifier asked for as an xfail-strict against
  `check_tee_status` with reason `checker A21d non-final arms pending (lane A5g)` so it turns red the day the checker lands.
- R4 (F10/F11/F13/F15/F16/F17/F18): F10 an `ast`-level test that the SIGTERM handler body is exactly `raise _Terminated()`; F11 exact
  list equality for the directional-close entries; F13 exact single entries everywhere (`startswith`/`>= 1` gone — paste the greps);
  F15 the docstring says "rewritten after every recorded frame" and names the non-final SIGTERM write; F16 the contended pair is two
  real contended runs (nice 19, four burners; paste load); F17 every Popen-based test body kills its tee/agent in `finally`; F18 the
  rename is disclosed in the report.

## Boundary (touch ONLY): `proofs/S0-01/tools/frame_tee.py`, `tests/test_s0_01_frame_tee.py`. `proofs/S0-01/pins.py` and
`proofs/S0-01/check_acp_conformance.py` are READ-ONLY (import `check_tee_status` in tests only). Edit the shared tree in place — no
commits, no git state changes, no other paths, no subagents, no outward actions; one mutant copy at a time under …/scratchpad/lb5d/
with `--basetemp` per run; 4 shared cores — no xdist; long runs in ONE foreground call; the contended pair serially at the end.

## Acceptance bar
The verifier's 54-mutant set (its `mut8.py`) re-run: A2 (now "exit when the agent exits"), A6, C1, D3, N3, N4, N6, N8 killed by
NAMED tests (C4/N10 the accepted equivalents); killsnap 20/20 under the R2 invariants; p9 gap sweep 1/4/6/8 s all recorded;
hang.py A-E; sigterm_deadlock 12/12; the ordering probe 12/12; the forward-lag probe 0 violations of the R2 bounds. Gate (paste):
pyflakes rc 0; the suite TWICE idle + the contended pair; `tmp_path` hygiene. Report to …/scratchpad/wf-results-r5/B5d.md (draft
B5d-draft.md as you go): done (finding → test → red before / green after), the mutant table, the probe table, not_done → reason (an
empty not_done beside an unmet item reopens the lane), files, summaries, discrepancies, adjacent defects, the exact invariant list
for the checker lane. Authorization context: defensive verification tooling on the owner's own system; the tee records the owner's
own ACP frames; no credentials are involved.
