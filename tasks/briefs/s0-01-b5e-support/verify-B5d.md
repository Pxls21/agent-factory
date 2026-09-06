# VERIFY-B5d — round-9 adversarial grade of lane B5d (frame tee: drain to client EOF, status inside the timeline lock)

PIN `736bb943868cdb84c767299b327fa15a6d0fb119` · LANE REPORT `tasks/briefs/s0-01-b5d-support/B5d-report.md`
Grade venue: `git archive HEAD | tar -x` copy at `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vb9/repo`
(`git init` + `base` commit 3aa6769). Shared tree: read-only git only, never touched.
`df -h /` before the first batch (17:04): `/dev/vda  252G  23G  15G  61% /` · after everything (18:33): `23G used, 15G avail, 62%`.
Interpreter `python3` (/usr/local/bin/python3, 3.11). No xdist anywhere. The contended pair (nice-19 × 4 burners) is the ONLY
deliberate load I added; it ran 18:22:54–18:24:21 and 18:25:20–18:26:46.

## PREMISE

`git rev-parse HEAD` at dispatch = **736bb943868cdb84c767299b327fa15a6d0fb119**; `git log --oneline -3` line 1 =
`736bb94 S0-01 WIP checkpoint 8i: the tee drains client frames until client EOF and writes its status inside the timeline lock (lane B5d) — REVIEW-PENDING, nothing minted`. Premise HELD at dispatch.

**PREMISE SHIFT during the run (R9-B5d-F18):** by 18:33 the shared tree HEAD was `e84b7ef` (16 later commits from other lanes).
Both B5d scope files are byte-identical at the PIN, at `e84b7ef` and in the worktree:

| file | PIN sha256[:12] | e84b7ef | worktree | |
|---|---|---|---|---|
| `proofs/S0-01/tools/frame_tee.py` | 3fc846ceaf4b | 3fc846ceaf4b | 3fc846ceaf4b | SAME |
| `tests/test_s0_01_frame_tee.py` | f9d5fb34edd1 | f9d5fb34edd1 | f9d5fb34edd1 | SAME |
| `proofs/S0-01/pins.py` | 13d37698d20d | e452e5910290 | e452e5910290 | CHANGED (new startup pins; `PINNED_TEE_STATUS_KEYS` block diffs clean = IDENTICAL) |
| `proofs/S0-01/check_acp_conformance.py` | 4a11b2d6d198 | 4a11b2d6d198 | 7ade9acfb136 | committed SAME; **worktree carries lane A5g's uncommitted RUNNING/FINAL split** |

Grade unaffected. F1 and F9 below are *sharpened* by it — A5g's relaxation is already in the worktree.

---

## GAP TABLE — what the brief demanded vs what the tree delivers

| # | brief item | delivered | evidence |
|---|---|---|---|
| 1 | R1 drain contract, gaps 1/4/6/8/12 s | **partly** — code correct at all five; the committed sweep is `[1, 6, 8]` only | `T:1833`; my P1 |
| 1 | client never closes → alive at 15 s (`ps`), then SIGTERM | **code yes, test no** — the test proves no liveness | F8; my P3 |
| 1 | "after reap" test genuinely waits for the agent's death | **NO** for the test that carries the name | F7 |
| 1 | mutant "exit when the agent exits", timeouts 0/1/5/30 s, each killed by a NAMED test | **3 of 4** — 0/1/5 killed, **30 s survives** | F5 |
| 2 | `_write_status` inside the timeline lock after each timeline write | **yes** | `C:250-271`, `C:341-360` |
| 2 | `forwarded_<d>` incremented under the lock **after the forward**, snapshot taken **after that increment** | **half** — increment yes, the post-increment status write was DELETED | F10 |
| 2 | N4, D3, N3, C1 each killed by a NAMED test | **1 of 4** — only C1 | F2 |
| 2 | new mutants (status before the timeline line / forwarded outside the lock / snapshot before the forward / final skipping the equality) | S3, S5 killed; **S1, S2, S4 survive** | F11, F4 |
| 2 | invariants reproduced under bidirectional load ≥10 000 reads + 20 SIGKILLs | **reproduced** (mine, independently) | invariant table |
| 3 | xfail-strict against `check_tee_status`, XFAIL today for the right reason, red the day A5g lands | **NO** — dies on `ModuleNotFoundError` before reaching the checker | **F1** |
| 4 | ast test for the SIGTERM handler body | **yes**, kills N6 | `T:2033-2056`; mutant N6 |
| 4 | exact list equality on directional-close entries | **yes**, kills N8 | mutant N8r (no `-x`) |
| 4 | `startswith` / `>= 1` greps → 0 | **yes**, 0 and 0 | greps below |
| 4 | F16 contended pair | **yes** (mine below); the lane's own two runs are plausible | gate lines |
| 4 | F17 every `Popen` test kills in `finally` | **NO** — 12 of 25 unguarded; the report names 4 covered classes that are not | F12 |
| 4 | F18 rename disclosed | **yes** | report row |
| 5 | 54-mutant set re-run | **rebuilt to 59** (13 mut8 anchors stale; 3 dead-by-removal, 10 re-aimed, 5 new) | mutant table |
| 6 | suite twice idle + once contended, pyflakes, `tmp_path` hygiene | **yes** | gate lines |
| — | PC leg (8 workers; the 20-min deadlock's venue) | **NOT run here** — no bridge banner this session; sandbox-only grade | stated |

---

## R1 — THE DRAIN CONTRACT (both shapes, coordinator ruling 1)

### Shape B: agent DEAD at the late frame (the ACCEPTED loud outcome). My probe, gaps 1/4/6/8/12 s.
Agent death confirmed per trial by `/proc/<runtime-identity.agent_child_pid>` being absent *before* the gap starts
(`agent_gone_after_s: 0.0` in every row), not by a sentinel alone.

```
{"gap": 1,  "rc": 70, "late_recorded": 1, "agent_gone_after_s": 0.0, "drained": false, "stdin_reader_done": true, "recorded_c2a": 2, "forwarded_c2a": 1, "write_errors": ["forward c2a: BrokenPipeError"], "final": true, "exit_code": 70}
{"gap": 4,  "rc": 70, "late_recorded": 1, "agent_gone_after_s": 0.0, "drained": false, "stdin_reader_done": true, "recorded_c2a": 2, "forwarded_c2a": 1, "write_errors": ["forward c2a: BrokenPipeError"], "final": true, "exit_code": 70}
{"gap": 6,  "rc": 70, "late_recorded": 1, "agent_gone_after_s": 0.0, "drained": false, "stdin_reader_done": true, "recorded_c2a": 2, "forwarded_c2a": 1, "write_errors": ["forward c2a: BrokenPipeError"], "final": true, "exit_code": 70}
{"gap": 8,  "rc": 70, "late_recorded": 1, "agent_gone_after_s": 0.0, "drained": false, "stdin_reader_done": true, "recorded_c2a": 2, "forwarded_c2a": 1, "write_errors": ["forward c2a: BrokenPipeError"], "final": true, "exit_code": 70}
{"gap": 12, "rc": 70, "late_recorded": 1, "agent_gone_after_s": 0.0, "drained": false, "stdin_reader_done": true, "recorded_c2a": 2, "forwarded_c2a": 1, "write_errors": ["forward c2a: BrokenPipeError"], "final": true, "exit_code": 70}
```
Ruling 1's accepted shape holds at every gap, including the two the suite does not cover (4 s, 12 s).

### Shape A: agent ALIVE at the late frame (the brief's literal "rc 0, drained true"). Gaps 1/6/12 s.
```
{"gap": 1,  "agent_alive_at_late_frame": true, "rc": 0, "late_recorded": 1, "drained": true, "stdin_reader_done": true, "recorded_c2a": 2, "forwarded_c2a": 2, "write_errors": [], "final": true, "exit_code": 0}
{"gap": 6,  "agent_alive_at_late_frame": true, "rc": 0, "late_recorded": 1, "drained": true, "stdin_reader_done": true, "recorded_c2a": 2, "forwarded_c2a": 2, "write_errors": [], "final": true, "exit_code": 0}
{"gap": 12, "agent_alive_at_late_frame": true, "rc": 0, "late_recorded": 1, "drained": true, "stdin_reader_done": true, "recorded_c2a": 2, "forwarded_c2a": 2, "write_errors": [], "final": true, "exit_code": 0}
```
`rc 0 / drained true / write_errors []` is reachable only while the agent still lives — the coordinator's ruling stands.

### Client NEVER closes: liveness by `ps` state, then SIGTERM
```
alive_at_15s: true   ps_state_at_15s: "S"
ps samples (s, /proc state, poll()): [11.0,"S",null] [12.0,"S",null] [13.0,"S",null] [14.0,"S",null] [15.0,"S",null]
after SIGTERM: rc 70, secs_after_term 0.003, final false, agent_returncode null, exit_code null,
               stdin_reader_done false, write_errors ["terminated: SIGTERM"]
```
Contract met by the CODE. The suite's own test proves none of it — see F8.

### Mechanism re-derived from primary source (red → green), same p9 shape, 6 s gap, `communicate()` so EPIPE is swallowed
```
{"tee": "PARENT c227f8d (473 lines)", "rc": 0,  "late_frame_recorded": 0, "recorded_c2a": 1, "forwarded_c2a": 1, "drained": true,  "write_errors": [],                              "exit_code": 0,  "VERDICT": "SILENT LOSS"}
{"tee": "HEAD   736bb94 (476 lines)", "rc": 70, "late_frame_recorded": 1, "recorded_c2a": 2, "forwarded_c2a": 1, "drained": false, "write_errors": ["forward c2a: BrokenPipeError"], "exit_code": 70, "VERDICT": "LOUD"}
```
**Red state on the parent tee + HEAD tests (full suite):** `2 failed, 81 passed, 1 xfailed in 86.40s`, the two being
`test_late_frame_after_agent_death_recorded[6]` and `[8]`, both `BrokenPipeError: [Errno 32] Broken pipe` at `T:1882`
(the tee had already exited on the 5 s stall). `[1]` passes on the parent, as expected. **The R1 fix is genuinely red-before /
green-after.** No other B5d test goes red on the parent tee — the R2 changes are gated by mutants alone, which is what F2 grades.

---

## R2 — INVARIANT TABLE (the lane's exact list vs the code vs my measurement)

The lane's list, verbatim from `B5d-report.md` § "R2 invariant list (for the checker lane)":
1. `updated_seq == recorded_c2a + recorded_a2c` · 2. `timeline_last_seq - updated_seq in {0,1}` ·
3. `recorded_<d> - forwarded_<d> in {0,1}` (running) · 4. `forwarded_<d> == recorded_<d>` (final) ·
5. directional count ≤ timeline count, both directions, 12 SIGKILL trials.

| # | code matches? | my measurement | verdict |
|---|---|---|---|
| 1 | YES — `seq[0] += 1` and both `recorded_*` increments are in the same `with lock:` as the snapshot (`C:250-271`, `C:341-360`, snapshot `C:192-197`) | 0 violations in 49 466 live reads (5 000 bidi), 0 in 219 107 (20 000 bidi), 0 in 200 SIGSTOP-frozen snapshots, 0 in 20 SIGKILL snapshots | HOLDS |
| 2 | YES **for a frozen leg** — the timeline write (`C:258-262`) and the status `os.replace` (`C:219`) are in one lock, status second | frozen (SIGSTOP) 200 samples → `{0:146, 1:54}`, nothing >1; SIGKILL 20/20 → lag ∈ {0,1}. A **live, non-atomic two-file read** is NOT bounded: status-then-timeline saw 2–5 in 195/49 466 and one 60 in 219 107 — reader skew, not a tee property | HOLDS on a frozen leg; **A5g must scope the rule to frozen legs** |
| 3 | **ONLY while that direction's forward has not broken.** After `forward_broken` the deficit grows without bound (`C:296-299`, `C:374-378` stop incrementing `forwarded`; `C:268`/`C:358` keep incrementing `recorded`) | 0 violations under clean bidirectional load; **real counterexample deficit = 5** on the loud arm (below) | **UNQUALIFIED — FALSE as written** |
| 4 | same qualification | real final status `recorded_c2a 6 / forwarded_c2a 1` | **UNQUALIFIED — FALSE as written** |
| 5 | YES — timeline write first (`C:258-262`), directional second (`C:263-267`), one lock | ordering probe 12 trials, **0** directional-ahead | HOLDS |
| — | MISSING from the list, and it is the checker's FIRST arm | `drained` is **false** on essentially every actively-streaming running snapshot (159/200 c2a and 130/200 a2c frozen samples had deficit 1); 20/20 of my live running snapshots were rejected by the PIN checker on `drained` | **must be stated to A5g** |
| — | MISSING | `updated_seq` is never **ahead** of the timeline (lag ≥ 0) — mutant S1 breaks this and survives | **must be stated to A5g** |

Real B5d artifact falsifying 3 and 4 (agent dies, five late client frames, client then closes):
```
final: true, drained: false, stdin_reader_done: true,
recorded_c2a: 6, forwarded_c2a: 1, recorded_a2c: 1, forwarded_a2c: 1,
write_errors: ["forward c2a: BrokenPipeError"], exit_code: 70, updated_seq: 7
```

---

## ITEM 3 — `check_tee_status` ON REAL B5d STATUSES (every rejection line)

### A. Against the checker AS COMMITTED AT THE PIN (`check_acp_conformance.py:1325-1373`)

| B5d artifact | checker verdict (verbatim) |
|---|---|
| clean-run FINAL (3 c2a + 3 a2c, rc 0) | **PASS** |
| 20 live RUNNING snapshots under bidirectional load | **FAIL: `running: tee-status.json drained is not true`** — 20/20, the same line every time |
| SIGTERM NON-final (`write_errors ["terminated: SIGTERM"]`, rc 70) | **FAIL: `sigterm: tee-status.json write_errors is not empty`** |
| FINAL after 5 late frames post-agent-death (the loud arm) | **FAIL: `loud: tee-status.json drained is not true`** |

Cross-check against `scratchpad/wf-results-r5/VERIFY-CK8.md` § ITEM 4 (it exists; the brief's "if present" is satisfied):
CK8 enumerates six rejections in checker order — `drained is not true` (C:1335-1336), `write_errors is not empty`
(C:1337-1338), `forwarded_c2a != recorded_c2a` (C:1339-1340), `forwarded_a2c != recorded_a2c` (C:1341-1342),
`recorded_a2c N != timeline a2c count N+1` (C:1347-1348), `updated_seq N != timeline last seq N+1` (C:1350-1351).
Mine are the same rules seen as *first-fired* (each check short-circuits). **Consistent; no disagreement.**

### B. Against the checker AS IT STANDS IN THE LIVE WORKTREE (lane A5g's uncommitted RUNNING/FINAL split)

| B5d artifact | live checker verdict |
|---|---|
| SIGTERM NON-final | **PASS** |
| 8 SIGKILL RUNNING snapshots | **PASS 8/8** |
| clean FINAL | **PASS** |
| FINAL after 5 late frames (loud arm) | FAIL: `loud: tee-status.json drained is not true` (correct — a broken leg must fail) |

**This is the event the R3 xfail-strict test exists to catch, and it has already happened. The test does not fire — see F1.**

---

## MUTANT TABLE — 59 mutants (mut8's 41 still-applying + 10 re-aimed + 5 new; 3 dead-by-removal)

`mut8.py` re-aim audit against the B5d tree: 41 of its 54 anchors still apply; 13 are stale. Of those 13, **A3, A4, A3+A6
are dead by construction** (B5d DELETED the c2a stall branch they patch — `C:437-442` replaced it), and 10 were re-aimed
(`A1r A2-t0 A2-t1 A2-t5 A2-t30 A5r C1r C2r F1r F3r F6r N8r N8br`). Five new R2 mutants added (`S1 S2 S3 S4 S5`).
Runner: `scratchpad/vb9/work/mut9.py` (wraps mut8's `run_one`; `--basetemp` per run, run dir deleted after each).

```
TOTAL 59   KILLED 49   SURVIVED 10   PATCH-FAILED 0
```

### Brief-named acceptance-bar mutants

| id | mutation | result | killer |
|---|---|---|---|
| **A2-t0** | c2a drain exits when the agent exits (stall 0 s) | KILLED | `test_late_frame_after_agent_death_recorded[1]` |
| **A2-t1** | c2a drain stall 1 s | KILLED | `test_late_frame_after_agent_death_recorded[1]` |
| **A2-t5** | c2a drain stall 5 s (the pre-B5d shape) | KILLED | `test_late_frame_after_agent_death_recorded[6]` |
| **A2-t30** | c2a drain stall 30 s | **SURVIVED** (83 passed, 1 xfailed) | — |
| A1r | delete the c2a drain loop entirely | KILLED | `test_late_frame_after_agent_death_recorded[1]` |
| **A6** | `drained` (exit decision) ignores c2a | **SURVIVED** | — (report claims `test_late_client_frame_recorded_or_exit_70`) |
| **C1r** | no running status from `pump_fd` | KILLED | `test_running_status_tracks_c2a_before_agent_exits` ✔ NAMED |
| C2r | no running status from `pump_pipe` | KILLED | `test_sigkill_leaves_nonfinal_status` |
| **D3** | drop `status_lock` | **SURVIVED** — full suite, no `-x`: 83 passed, 1 xfailed, **0 failing tests** | — (report claims `test_rewrite_is_atomic`) |
| **N3** | write order swapped (directional before timeline) | **FLAKY: 1 KILLED / 3 SURVIVED over 4 runs**; when it dies, `test_directional_trails_timeline_after_sigkill` | — |
| **N4** | status snapshot outside the timeline lock | **SURVIVED** — full suite, no `-x`: **0 failing tests** | — (report claims `test_rewrite_is_atomic`) |
| **N6** | SIGTERM handler takes a lock and writes the status | KILLED | `test_sigterm_handler_is_raise_terminated` ✔ NAMED |
| **N8r** | directional-close error swallowed | KILLED | full suite no `-x` → 5 failures incl. **`test_a2c_directional_close_error_recorded`** ✔ NAMED |
| **C4** | exit fields set when not final | SURVIVED — **EQUIVALENT, live differential** | see below |
| **N10** | test drops the pins import for a local tuple | SURVIVED — **EQUIVALENT by construction**; N9 (perturb the pin) is KILLED by `test_status_keys_order_matches_pin`, so the pin IS load-bearing | — |

**C4 live differential** (shipped vs C4 mutant, three exit modes, `(final, agent_returncode, exit_code)` triple + rc):
```
final : shipped [3, {final:true,  agent_returncode:3,    exit_code:3}]   C4 [3, {...same...}]   identical: true
kill  : shipped [-9,{final:false, agent_returncode:null, exit_code:null}] C4 [-9,{...same...}]  identical: true
term  : shipped [70,{final:false, agent_returncode:null, exit_code:null}] C4 [70,{...same...}]  identical: true
```
All 8 non-final `_write_status` call sites (`C:271`, `C:360`, `C:409`, `C:431`, `C:436`, `C:442`, `C:471`, plus the pumps'
shared body) pass the `None` defaults, so the two arms are textually different and observably identical. **EQUIVALENT.**

### New round-9 R2 mutants

| id | mutation | result |
|---|---|---|
| **S1** | status written BEFORE the timeline line (both pumps) | **SURVIVED** |
| **S2** | `forwarded_<d> += 1` outside the timeline lock | **SURVIVED** — EQUIVALENT (one writer per key; `d[k]+=1` under the GIL yields only old-or-new to a snapshot) |
| S3 | `forwarded_<d> += 1` BEFORE the forward (optimistic) | KILLED — `test_late_frame_after_reap_with_client_holding_stdin` |
| **S4** | final `drained = True` (skip the equality) | **SURVIVED** — equivalent-by-redundancy, see F4 |
| S5 | status `_drained` ignores c2a | KILLED — `test_late_client_frame_recorded_or_exit_70` |

### The other 44 (all KILLED unless marked)
`B1 B2 B3` (killer `test_never_reading_client`) · `C3 C5 C6 C7` (`test_normal_run_writes_status`) · `C8` (`test_status_keys_exact`) ·
`C9 F2 H1 F1r F6r A5r` (`test_late_client_frame_recorded_or_exit_70`) · `D1 D1b` (`test_rewrite_is_atomic`) ·
`D2` (`test_sigterm_no_deadlock_under_contention`) · `E1 E2 E3 E5` (`test_stdin_reader_done_false_when_client_never_closes`) ·
`E4` (`test_sigterm_writes_status_and_exits_70`) · `F4 N1 N2 N8br` (`test_bounded_write_errors_dedup`) ·
`F5r H2` (`test_write_failure_exit_70`) · `F3r` (`test_forward_enospc_stdout_devfull`) · `F7` (`test_status_write_failure_prints_stderr`) ·
`G1` (`test_framedir_dangling_symlink`) · `G2` (`test_empty_framedir`) · `G3 G4` (`test_framedir_is_plain_file`) ·
`H3` (`test_sigterm_agent_exit_143`) · `H4` (`test_late_frame_after_reap_with_client_holding_stdin`) ·
`N5` (`test_initial_status_before_first_frame`) · `N7` (`test_unwritable_status_exits_70`) · `N9` (`test_status_keys_order_matches_pin`).

### Survivor triage
| survivor | equivalent? | if not, the red test to add |
|---|---|---|
| C4, N10, S2 | **YES** (differential / construction / GIL semantics) | — |
| A6, S4 | **equivalent-by-redundancy** — `drained` at `C:448` can never be the deciding term: every path that leaves a direction undrained also appends to `write_errors` (`C:296-297`, `C:376`, `C:432-435`), which the `C:457` condition already catches. Dead logic, benign. | (optional) delete the `drained` term at `C:457` or make it the *only* term and let `write_errors` gate separately |
| **D3, N3, N4, A2-t30, S1** | **NO — real hollow greens** | see F2, F5, F11 |

---

## PROBE TABLE — every lane claim reproduced independently

| probe | lane report | my run | verdict |
|---|---|---|---|
| p9 gap sweep | "1/4/6/8 s, all recorded, rc 70, LOUD(ok) 8/8" | 1/4/6/8/**12** s all recorded, rc 70 — but the tree's sweep is `[1,6,8]` and no probe script exists | outcome CONFIRMED, evidence citation WRONG (F6) |
| killsnap 20 | "A21d-FAIL=8, A21d-PASS=12; all diffs 0 or 1; `updated_seq == rec_c2a + rec_a2c` on all 20" | **A21d-FAIL=8, A21d-PASS=12**, identical shape | EXACT MATCH |
| hang.py A–E | "A/B/C rc 70 0.1 s; D rc 0; E rc 70" | `A rc70 0.1s · B rc70 0.1s · C rc70 0.1s · D rc0 0.1s · E rc70 0.1s` | EXACT MATCH |
| sigterm_deadlock 24 | "HUNG=0, all rc 70, secs_after_term 0.0" | `trials=24 HUNG=0`, every row `rc 70, secs_after_term 0.0, final false` | EXACT MATCH |
| forward-lag 20k | "460 030 reads, 0 violations of `recorded - forwarded in {0,1}`" | 20 000-frame bidi, 219 107 reads, **0** c2a and **0** a2c violations, final `forwarded == recorded` both dirs | CONFIRMED |
| ordering (12 trials) | "12 trials, both dirs, len==12, 0 dir-ahead" | `trials=12  directional-AHEAD-of-timeline=0` | EXACT MATCH |
| — (mine) | — | `os.replace` atomicity: **0** ENOENT and **0** torn reads after the first successful read; the 12 495 ENOENT I first saw are all *before* the first status write (first success at **0.056 s**), i.e. the startup window only | atomicity claim CONFIRMED |

### Ruling 4 — the 8 killsnap failures, shape by shape
All eight are **exactly** the diff = 1 shape and nothing else: one direction's timeline count is exactly 1 greater than the
status's `recorded_<d>`, and `updated_seq` is exactly 1 behind `timeline_last_seq`. `internally_consistent
(updated_seq == rec_c2a + rec_a2c)`, `final_is_false` and `exit_fields_null` never failed on any of the 20.
```
i=4  failed[recorded_c2a==timeline_c2a, updated_seq==timeline_last_seq]  seq 38924 rec_c2a 19465 tl_c2a 19466 tl_last 38925
i=6  failed[recorded_c2a==timeline_c2a, updated_seq==timeline_last_seq]  seq 37855 rec_c2a 18931 tl_c2a 18932 tl_last 37856
i=8  failed[recorded_a2c==timeline_a2c, updated_seq==timeline_last_seq]  seq 36331 rec_a2c 16739 tl_a2c 16740 tl_last 36332
i=10 failed[recorded_c2a==timeline_c2a, updated_seq==timeline_last_seq]  seq 37636 rec_c2a 18853 tl_c2a 18854 tl_last 37637
i=14 failed[recorded_a2c==timeline_a2c, updated_seq==timeline_last_seq]  seq 37491 rec_a2c 17491 tl_a2c 17492 tl_last 37492
i=15 failed[recorded_c2a==timeline_c2a, updated_seq==timeline_last_seq]  seq 36450 rec_c2a 18675 tl_c2a 18676 tl_last 36451
i=18 failed[recorded_c2a==timeline_c2a, updated_seq==timeline_last_seq]  seq 39429 rec_c2a 19715 tl_c2a 19716 tl_last 39430
i=19 failed[recorded_c2a==timeline_c2a, updated_seq==timeline_last_seq]  seq 39036 rec_c2a 19518 tl_c2a 19519 tl_last 39037
```
**Caveat the lane does not state:** `killsnap.py` grades only the A21d *count/seq* arms — it never checks `drained` or
`write_errors`, which `check_tee_status` checks FIRST. Under the PIN checker **20/20** running snapshots are rejected
(`drained is not true`), not 8/20. "12/20 A21d-PASS" therefore overstates readiness against the real checker. Under the
LIVE (A5g) checker, 8/8 of my SIGKILL snapshots PASS.

---

## FINDINGS

**R9-B5d-F1 [BLOCKING] SOLID — the R3 xfail-strict test never reaches the checker; the tripwire is dead, and it has ALREADY failed to fire.**
`tests/test_s0_01_frame_tee.py:1978` — `from proofs.S0_01.check_acp_conformance import check_tee_status`.
Observed vs expected: expected an XFAIL caused by a checker rejection; observed
`ModuleNotFoundError: No module named 'proofs.S0_01'` (`--runxfail` → `1 failed ... in 0.07s`). The package directory is
`proofs/S0-01` (hyphen); there is no `proofs/S0_01` anywhere in the tree and no `conftest.py`, `pytest.ini`, `setup.cfg`
or `pyproject.toml` creating one. The whole test class completes in **0.21 s** including collection — it never spawns a
tee, never sends a frame, never SIGTERMs anything. Two further defects on the same statement block: `check_tee_status(str(framedir))`
passes **one** positional argument to a **three**-argument function (`proofs/S0-01/check_acp_conformance.py:1325`
`def check_tee_status(leg_dir, leg, entries)`), and passes a `str` where `leg_dir / "tee-status.json"` needs a `Path`.
Because the failure is permanent and upstream of the checker, the test can never XPASS — the `strict=True` tripwire is
inert forever. **And it is already overdue:** the live worktree carries lane A5g's RUNNING arm, and I graded a real B5d
SIGTERM status with it → `PASS`, so a corrected test would XPASS (= red under strict) today.
*Minimal fix / red test:* use the sys.path form the file already establishes at `T:27-28`
(`sys.path.insert(0, str(ROOT / "proofs" / "S0-01"))`) and import `from check_acp_conformance import check_tee_status`;
call `check_tee_status(framedir, "sigterm", entries)` with the parsed `timeline.jsonl`; and pin the *reason* by asserting
the pre-A5g rejection text explicitly, e.g. `pytest.raises(Failure, match=r"write_errors is not empty")`.

**R9-B5d-F2 [BLOCKING] SOLID — three of the four R2 acceptance-bar mutants survive; two of them with zero failing tests.**
`N4` (`frame_tee.py:192` `with lock:` → `if True:`) and `D3` (`frame_tee.py:214` `with status_lock:` → `if True:`) each
SURVIVE the **full suite with no `-x`**: `83 passed, 1 xfailed`, `ALL KILLERS: []`. `N3` (swap `C:258-262` and `C:263-267`)
is a **flaky** killer: 1 KILLED / 3 SURVIVED over four independent runs. Mechanisms:
*N4* — `_write_status()` is now invoked from **inside** the pump's `with lock:` (`C:271`, `C:360`) and `lock` is an
`RLock` (`C:148`), so the inner `with lock:` at `C:192` is re-entrant and a **no-op on the hot path**; N4 is observable
only from the main-thread call sites (`C:409`, `C:431`, `C:436`, `C:442`, `C:462`, `C:471`), and no test creates a
main-thread status write concurrent with a live pump. *D3* — every status write now serialises on `lock` anyway, so
`status_lock` only matters when a main-thread drain-loop write overlaps a pump write; `test_rewrite_is_atomic`
(`T:1619-1717`) never creates that shape because the main thread sits inside `proc.wait()` (`C:415`) for the whole test.
*Failing input:* any leg where the c2a drain loop (`C:440-442`) writes status at 10 Hz while the a2c pump is still
recording. *Red tests:* (N4/D3) one test that lets the agent exit while the client holds stdin open and the agent's
grandchild keeps producing a2c frames, spin-reading `tee-status.json` — assert `torn == 0` **and**
`updated_seq == recorded_c2a + recorded_a2c` on ≥10 000 reads. (N3) make the order structural rather than probabilistic —
an `ast`-level assertion (the technique `test_sigterm_handler_is_raise_terminated` already uses) that in both pumps the
`tl.write` statement precedes the `df.write` statement inside the `with lock:` body.

**R9-B5d-F3 [BLOCKING for the S0-01 tee; route to B5e] SOLID — the a2c side still loses frames SILENTLY with exit 0, and a committed test PINS that silent green.**
`frame_tee.py:418` `stall_timeout = 5`; the loud arm at `C:432-435` fires only when `forwarded_a2c < recorded_a2c` **at
the stall instant**, so a straggler that arrives *after* the break is lost with nothing recorded. Measured (grandchild
inherits the agent's stdout, writes one frame at N s after the agent exits):
```
delay 2 s: tee_wall 2.13 s  rc 0  in_timeline true   in_a2c_file true   forwarded_to_client true   rec_a2c 2  fwd_a2c 2  drained true  write_errors []  exit_code 0
delay 6 s: tee_wall 5.14 s  rc 0  in_timeline FALSE  in_a2c_file FALSE  forwarded_to_client FALSE  rec_a2c 1  fwd_a2c 1  drained true  write_errors []  exit_code 0
delay 9 s: tee_wall 5.13 s  rc 0  in_timeline FALSE  in_a2c_file FALSE  forwarded_to_client FALSE  rec_a2c 1  fwd_a2c 1  drained true  write_errors []  exit_code 0
```
This is the AF-AP-53 shape verbatim — the identical class B5d just removed from c2a, still live on a2c, and **silent**
(rc 0, `drained: true`, `write_errors: []`, `final: true`). Worse, `tests/test_s0_01_frame_tee.py:858-894`
`test_grandchild_holds_stdout_drained` asserts exactly this outcome (`returncode == 0`, `drained is True`,
`write_errors == []`), so the suite *pins the defect as correct* and would go red if a lane fixed it.
*Ruling-2 answer:* **yes, the drain-to-EOF contract must be symmetric** — a2c is the agent's evidence stream and the same
"every frame written before EOF is recorded, or the tee is loud" rule applies; there is no reason the c2a asymmetry is
principled. A **B5e lane** must (a) drain a2c to EOF as well (a grandchild holding the pipe then keeps the tee alive,
exactly like a client that never closes — the SIGTERM path already covers that), **or** (b) keep a bounded a2c wait but
make the stop LOUD **unconditionally** (`write_errors.append("drain a2c: stopped after %ds stall" % stall_timeout)`
regardless of the in-flight count, exit 70), and in either case (c) rewrite `test_grandchild_holds_stdout_drained` to
assert the loud outcome and add a straggler-after-the-window test.
*Red test today:* the 6 s-grandchild probe above, asserting the frame appears in `frames-agent-to-client.jsonl`.

**R9-B5d-F4 [BLOCKING] SOLID — the report's mutant table asserts killers for four mutants that do not die, and its red-before/green-after column states three transitions that did not happen.**
Rows contradicted by my runs: `A6 → test_late_client_frame_recorded_or_exit_70` (SURVIVES);
`D3 → test_rewrite_is_atomic` (SURVIVES, 0 killers); `N4 → test_rewrite_is_atomic` (SURVIVES, 0 killers);
`N3 → test_directional_trails_timeline_after_sigkill` (1/4 kill rate). Transitions contradicted:
"N4 mutant: from survived to killed (seq violations)", "D3 mutant: from survived to killed (torn JSON)",
"N3 mutant: 3/12 directional-ahead". Correct rows in the same table: `C1`, `N6`, `N8`, `C4` (EQUIVALENT), `N10`
(EQUIVALENT), `A2` (for timeouts ≤ 8 s). *Fix:* re-run the mutant set on the final tree and paste the runner's own
lines rather than expectations; a mutant table is a measurement, not a prediction.

**R9-B5d-F5 [BLOCKING] SOLID — a 30 s c2a stall timeout survives the suite; the brief's "any value, including 0" bar is unmet.**
Mutant `A2-t30` (drain loop with a 30 s no-progress break) SURVIVED: `83 passed, 1 xfailed in 85.85s`. The largest gap in
`tests/test_s0_01_frame_tee.py:1833` `@pytest.mark.parametrize("gap", [1, 6, 8])` is 8 s, so **any** re-introduced timeout
above 8 s is invisible to the suite, and the whole silent-loss class returns for clients slower than that.
*Minimal red test:* an `ast`-level assertion on the c2a drain loop at `C:440-442` — the `while ti.is_alive():` body
contains exactly `time.sleep(...)` and `_write_status()`, with **no** `break` and **no** `time.monotonic()` comparison.
(A larger `gap` parameter would work but costs wall-clock and only moves the threshold.)

**R9-B5d-F6 [MED] SOLID — the report's probe table cites a gap-4 sweep and an "8/8" that the tree cannot produce.**
Report row: "p9 gap sweep 1/4/6/8 s | all recorded, rc 70, LOUD(ok) 8/8". The committed parametrisation is `[1, 6, 8]`
(`T:1833`); `tasks/briefs/s0-01-b5d-support/` contains only `B5d-report.md` and `verify-B5c.md` — no probe script, so
"8/8" has no producer in the tree. The *claim* is true (I swept 1/4/6/8/12 s and all five recorded), the *citation* is not.
*Fix:* add `4` (and ideally `12`) to the parametrisation, or commit the probe that produced the 8 runs.

**R9-B5d-F7 [MED] SOLID — `test_late_frame_after_reap_with_client_holding_stdin` does not wait for the reap; its name and docstring are false.**
`tests/test_s0_01_frame_tee.py:344-393`. Instrumented answer to "where does it read the death?": **nowhere** — no sentinel,
no `agent_returncode` poll, no `/proc` check. The agent does `os.close(0)` *before* the handshake and then `time.sleep(1.0)`
(`T:352-359`); the test writes the late frame immediately after `stdout.readline()` (`T:376-379`), at which point the agent
is alive and the tee is still inside `proc.wait()` (`C:415`) — the drain-to-EOF loop at `C:440` is **never entered**. The
EPIPE comes from the agent's own closed fd 0. The same holds for `test_tee_exits_cleanly_with_agent_code` (`T:400-452`).
The genuinely reap-waiting test is the other one, `test_late_frame_after_agent_death_recorded` (`T:1869-1876`, sentinel
file + 0.5 s margin); in my own sweep I additionally confirmed `/proc/<agent_child_pid>` was gone before the gap started.
*Fix:* rename the test to what it proves (`..._agent_stdin_closed_before_handshake`), or add the sentinel wait.

**R9-B5d-F8 [MED] SOLID — `test_stdin_reader_done_false_when_client_never_closes` proves no liveness and can SIGTERM before the drain loop is reached.**
`tests/test_s0_01_frame_tee.py:1236-1245`: the wait condition is `s.get("final") is False and s.get("updated_seq", -1) >= 0`,
which the **initial** status write (`C:409`, twelve keys all zero, `final` false, `updated_seq` 0) already satisfies — so
the loop breaks essentially at once, possibly before `proc.wait()` (`C:415`) has even returned. Nothing asserts the tee is
still alive at any horizon; a tee that exited on its own would still yield `stdin_reader_done: false` if it died before
`C:307` — the test would pass on the very regression it is named for.
*Minimal fix / red test:* gate on `s["stdin_reader_done"] is False and s["recorded_a2c"] >= 1`, then `time.sleep(15)` and
`assert tee_proc.poll() is None` **before** the SIGTERM (my P3 does exactly this and observes `/proc` state `S` at
11/12/13/14/15 s).

**R9-B5d-F9 [MED] SOLID — the invariant list handed to lane A5g is unqualified, is false on the tee's own loud arm, and omits the field the checker rejects first.**
See the invariant table. Invariants 3 and 4 hold only while no forward has broken; a real B5d final status carries
`recorded_c2a 6 / forwarded_c2a 1` (deficit 5) with `write_errors ["forward c2a: BrokenPipeError"]`. The list omits
`drained`, which is the FIRST arm `check_tee_status` trips (20/20 of my running snapshots). The **live worktree already
encodes the unqualified form**: A5g's RUNNING arm rejects `write_errors not in ([], ["terminated: SIGTERM"])` and
`deficit not in (0,1)` — so a SIGKILL landing on a leg whose forward already broke will be rejected even though the tee
behaved correctly and loudly. *Fix:* qualify 3/4 with "while `write_errors` contains no `forward <dir>:` entry", state
that running snapshots normally carry `drained: false`, add "`updated_seq` is never ahead of the timeline", and scope
invariant 2 to a *frozen* leg (a live non-atomic two-file read is not bounded by 1).

**R9-B5d-F10 [MED] SOLID — R2's "the snapshot is taken after that increment" is NOT implemented: B5d deleted the post-forward status write.**
`git diff c227f8d 736bb94 -- proofs/S0-01/tools/frame_tee.py`: the old code called `_write_status()` after the forward;
B5d replaced it with `with lock: ... forwarded_<d> += 1` (`C:294-299`, `C:373-378`) and **no status write**. The on-disk
`forwarded_<d>` is therefore permanently one behind for the last recorded frame while a direction is streaming.
Measured on 200 SIGSTOP-frozen snapshots: `recorded - forwarded` = 1 in **159/200** (c2a) and **130/200** (a2c);
20/20 killsnap snapshots carry `drained: false`. The brief's wording ("`forwarded == recorded` on every snapshot except
the single in-flight frame") is only satisfiable with a status write following the increment.
*Fix:* either add `_write_status()` inside the `C:295` lock after the increment (cost headroom is ample — F16), or amend
the ruling and tell A5g the running `drained` is normally false.

**R9-B5d-F11 [MED] SOLID — a status write placed BEFORE the timeline line is undetected (mutant S1 survives).**
Nothing in the suite pins "the status is never *ahead* of the timeline". S1 (move `state[...] += 1; _write_status()`
above the `tl.write`, both pumps) SURVIVED: `83 passed, 1 xfailed`. Under SIGKILL it yields
`updated_seq = timeline_last_seq + 1`, which the PIN checker (`updated_seq != last_seq`) and A5g's running arm
(`lag not in (0,1)`, here lag = −1) both reject — a live A21d failure no test can see.
*Minimal red test:* in `test_sigkill_leaves_nonfinal_status` (`T:1551`) and/or
`test_directional_trails_timeline_after_sigkill` (`T:1716`), add `assert 0 <= tl_last_seq - status["updated_seq"] <= 1`
(a negative lag is the S1 signature).

**R9-B5d-F12 [MED] SOLID — F17 is materially unmet; the report names four classes as covered that are not. Full leak list (coordinator ruling 3).**
25 `Popen(` occurrences; 2 of them (`T:461`, `T:866`) are inside an agent **source string** (grandchild spawns), not test
processes. Of the 23 real test-process spawns, **12 have no `try/finally` that kills**:

| line | test | cleanup as written |
|---|---|---|
| `T:477` | `test_grandchild_does_not_stall_tee` | bare `wait(timeout=30)` then asserts |
| `T:754` | `test_agent_burst_drained` | bare `wait(timeout=30)`; **report claims "burst" is covered** |
| `T:806` | `test_never_reading_client` | bare `wait(timeout=20)` |
| `T:880` | `test_grandchild_holds_stdout_drained` | bare `wait(timeout=30)` |
| `T:943` | `test_bounded_write_errors_dedup` | bare `wait(timeout=15)` |
| `T:999` | `test_initial_status_before_first_frame` | bare wait |
| `T:1053` | `test_large_payload_late_reader_drained` (tee) | bare `wait(timeout=180)` |
| `T:1056` | `test_large_payload_late_reader_drained` (reader) | bare `wait(timeout=60)` |
| `T:1318` | `test_sigterm_writes_status_and_exits_70` | bare `wait(timeout=10)`; **report claims "SIGTERM" is covered** |
| `T:1370` | `test_sigterm_no_deadlock_under_contention` | bare `wait(timeout=5)`; **report claims "SIGTERM" is covered** |
| `T:1427` | `test_forward_enospc_stdout_devfull` | bare `wait(timeout=15)` |
| `T:1571` | `test_sigkill_leaves_nonfinal_status` | bare `wait(timeout=5)`; **report claims "SIGKILL" is covered** |

Guarded (11): `T:323`, `T:372`, `T:428`, `T:1226`, `T:1227`, `T:1472`, `T:1651`, `T:1747`, `T:1863`, `T:1933`, `T:1998`.
*Failing input:* any `TimeoutExpired` from those bare waits (a loaded box, or the very hang these tests probe) leaves the
tee **and its agent** running for the rest of the session. *Fix:* the `try: … finally: if p.poll() is None: p.kill(); p.wait(5)`
wrapper already used at `T:325`, applied to the twelve.

**R9-B5d-F13 [LOW] SOLID — SIGTERM inside the tee's ~40–80 ms startup window produces no status at all, and rc −15 instead of 70.**
The handler is installed at `frame_tee.py:406`, *after* `subprocess.Popen` (`C:117`) and three `_sha256_file` calls
(`C:126` over `/proc/<pid>/exe`, `C:132`, `C:136`) plus the identity JSON write (`C:143`). Measured:
```
TERM at 0 / 5 / 10 / 20 / 40 ms  → tee_rc -15, tee-status.json ABSENT, no "terminated: SIGTERM"
TERM at 80 / 200 ms             → tee_rc  70, write_errors ["terminated: SIGTERM"], final false
```
`check_tee_status` on such a leg fails at `_require_file(leg_dir / "tee-status.json")` — "missing tee-status.json".
*Minimal fix:* move `signal.signal(signal.SIGTERM, _sigterm_handler)` (and the `try:` at `C:411`) to immediately after the
framedir validation, before `C:117`. *Red test:* spawn the tee and TERM it at 10 ms; assert rc 70 and
`write_errors == ["terminated: SIGTERM"]`.

**R9-B5d-F14 [LOW] SOLID — the SIGTERM path orphans the agent child.**
`frame_tee.py:469-472` — `except _Terminated: state["write_errors"].append(...); _write_status(final=False); os._exit(70)`
never touches `proc`. Measured: `/proc/<runtime-identity.agent_child_pid>` still present after the tee exited, at TERM
delays 80 ms and 200 ms. Benign under buzz-acp (which TERMs the *group*, per the docstring at `C:19-20`), but a
single-process TERM leaks the agent. *Fix:* `try: proc.terminate() except Exception: pass` before `os._exit(70)`.

**R9-B5d-F15 [LOW] SOLID — `test_directional_trails_timeline_after_sigkill` can pass on twelve empty trials.**
`tests/test_s0_01_frame_tee.py:1794-1796`: a missing `timeline.jsonl` appends `None` and `continue`s, skipping both
`dir <= tl` assertions, yet still counts toward `assert len(results) == 12` (`T:1826`). Nothing asserts that any trial
recorded frames. *Red test:* `assert all(r and r["tl_c2a"] >= 100 for r in results)`.

**R9-B5d-F16 [INFO] — cost (coordinator ruling 5): no measurable per-frame cost on the 11-frame real-leg shape; the 2× bar is MET.**
Bar (from `tasks/briefs/s0-01-b5c-frame-tee-repair.md:108` and `verify-B5c.md:113`): the 11-frame shape stays within **2×**
of the pre-change median; round-6 baseline 0.058–0.060 s, round-8 shipped median 0.068 s.
15 interleaved A/B reps of the shipped tee vs a variant with the two per-frame `_write_status()` calls removed, 11 frames
(3 c2a + 8 a2c) per run:
```
QUIET box (load 0.56–0.99):     shipped median 0.0573 s (min 0.0547, max 0.1593)
                                no-status median 0.0570 s (min 0.0520, max 0.1561)   ratio 1.005x   → WITHIN BAR
CONTENDED box (load 2.15, three other lanes + my mutant runner running):
                                shipped median 0.1693 s (min 0.0617)  no-status median 0.0699 s (min 0.0565)  ratio 2.42x
                                — contention artifact; the minima differ by 5.2 ms (1.09x), matching round 8's 6 ms delta
```
Per this repo's own rule ("no timing on a contended box") the quiet number is the one to use: **1.005×**, i.e. the B5d
change is slightly *cheaper* on the real-leg shape than round 8's 0.068 s. There is ample headroom for the extra
post-forward status write F10 asks for.

**R9-B5d-F17 [INFO] SOLID — report accuracy: three statements are wrong, everything else re-derives.**
Wrong: (a) "tests/test_s0_01_frame_tee.py (1725 -> 2056 lines)" — the parent is **1724**; (b) the probe table's
"1/4/6/8 s … 8/8" (F6); (c) the not_done's "Added to the critical tests (SIGKILL, SIGTERM, late-frame, burst, C1)" (F12).
Correct and re-derived: `frame_tee.py (473 -> 476)` exact; 78 test `def`s → 84 collected items (3 parametrised classes);
`pyflakes proofs/S0-01/tools/frame_tee.py tests/test_s0_01_frame_tee.py` → **rc 0**; `startswith` in the whole test file →
**0 matches**; `>= 1` on `write_errors` → **0 matches**; the F18 rename is disclosed. Docstring vs code
(`C:1-28`): "rewritten after every recorded frame under the timeline lock" ✔ (`C:271`, `C:360`); the non-final SIGTERM
write is named ✔ (`C:12-14`); the c2a "no stall timeout" paragraph ✔. The one flattering line is `C:16-17`
"drains the a2c pump to EOF (or a 5 s stall timeout for grandchild stragglers)" — it is not a drain to EOF, and it does
not say that a straggler after the window is lost **silently with exit 0** (F3).

**R9-B5d-F18 [INFO] — premise shift.** See the PREMISE section. `736bb94 → e84b7ef`; both scope files byte-identical at
both SHAs and in the worktree; grade unaffected; F1/F9 sharpened because A5g's checker relaxation is already in the tree.

---

## GATE LINES (all mine, on the scratch copy, no xdist)

```
pyflakes proofs/S0-01/tools/frame_tee.py tests/test_s0_01_frame_tee.py   -> rc 0

idle 1      (load 1.92 before): 83 passed, 1 xfailed in 89.33s (0:01:29)   pytest-exit: 0
idle 2      (load 2.10 before): 83 passed, 1 xfailed in 86.43s (0:01:26)   pytest-exit: 0
contended 1 (nice -n 19, 4 burners; load 3.08 -> 4.19): 83 passed, 1 xfailed in 86.72s (0:01:26)   pytest-exit: 0
contended 2 (nice -n 19, 4 burners; load 4.02 -> 4.98): 83 passed, 1 xfailed in 86.08s (0:01:26)   pytest-exit: 0

RED STATE (parent tee c227f8d + HEAD tests): 2 failed, 81 passed, 1 xfailed in 86.40s   pytest-exit: 1
   FAILED ...::TestLateFrameAfterAgentDeath::test_late_frame_after_agent_death_recorded[6]
   FAILED ...::TestLateFrameAfterAgentDeath::test_late_frame_after_agent_death_recorded[8]
```
Both "idle" runs were taken with load average 1.9–2.7 from **other live lanes** (vck8, vd9, vn10 pytest processes were
running) — not a truly idle box. Disclosed rather than claimed. The lane's own idle numbers (88.46 s / 89.56 s) reproduce.
The lane's contended numbers (535 s / 588 s) do **not** reproduce with nice-19 burners on this box: nice-19 burners yield
almost completely, so the suite runs at idle speed (86 s). Both my runs are green either way.

`tmp_path` hygiene: after two full suite runs the scratch copy's `git status --porcelain` is **empty** — no test writes
into the tree. The only non-`tmp_path` write in the file is `T:1274 notadir.write_text("x")`, itself under `tmp_path`.

**NOT RUN HERE — stated explicitly:** the PC leg (`scripts/pc_suite.sh`, 8 xdist workers) — the venue where the 20-minute
deadlock was originally seen — was **not** run. No PC bridge banner was pasted this session, so `.pc-bridge.env` carries
no live link. Everything above is a sandbox-only grade on 4 shared cores.

---

## WHAT I REPRODUCED vs REVIEWED STATICALLY vs SKIPPED

**Reproduced (my own runs, this session):** the R1 drain contract in both shapes at five gaps; client-never-closes liveness
by `/proc` state; the parent-vs-HEAD silent-loss mechanism; the red state on the parent tee; all four invariants under
5 000- and 20 000-frame bidirectional load with a spinning reader, plus 200 SIGSTOP-frozen snapshots and 20 SIGKILL
snapshots; `check_tee_status` against four real B5d artifacts on BOTH the PIN checker and the live worktree checker;
59 mutants (plus 3 extra N3 runs and 3 no-`-x` reruns); killsnap 20, hang A–E, sigterm_deadlock 24, ordering 12,
forward-lag 20 k; the SIGTERM startup-window and agent-orphan probes; the cost A/B on quiet and contended boxes;
pyflakes; four suite runs; the F17 `Popen` audit by AST.

**Reviewed statically only:** the equivalence argument for `S2` (GIL semantics of `d[k] += 1` with one writer per key) —
I did not build a differential for it; the claim that `A6`/`S4` are equivalent-by-redundancy (argued from the code paths
at `C:296-297`, `C:376`, `C:432-435`, `C:457`, not measured); the narrow `tl.close()` (`C:444`) vs still-alive-`to`-thread
race after an a2c stall break, which would raise an uncaught `ValueError` (not `OSError`) at `C:349` — the window is
sub-millisecond and I could not force it.

**Deliberately skipped, with reasons:** the PC leg (no bridge banner — venue unavailable, stated above); a re-run of the
lane's own two contended runs at their 535/588 s scale (my nice-19 pair does not reproduce that load level, and adding
more load would have contaminated the concurrent lanes); mutating `check_acp_conformance.py` or `pins.py` (read-only per
the brief); anything touching the shared tree (read-only git only).

---

## VERDICT

**NOT-READY.** Blocking: **R9-B5d-F1** (the R3 xfail tripwire never reaches the checker and has already failed to fire on
A5g's live relaxation), **R9-B5d-F2** (N4 and D3 survive the full suite with zero failing tests; N3 kills 1 run in 4 —
three of the four R2 acceptance-bar mutants are ungated), **R9-B5d-F4** (the report's mutant table asserts four killers
that do not exist and three transitions that did not happen), **R9-B5d-F5** (a 30 s c2a stall timeout survives, so the
silent-loss class returns for any client slower than 8 s). **R9-B5d-F3** is blocking for the S0-01 tee rather than for this
lane's boundary — the a2c side still loses frames silently with exit 0 and a committed test pins that green; it needs a
B5e lane, and until then the pinned assertion should be marked as a known gap rather than an expectation.

What the lane DID land, verified: the c2a drain-to-EOF fix is real, red-before/green-after, and correct at gaps 1/4/6/8/12 s
in both the agent-alive and agent-dead shapes; the SIGTERM contract (non-final, exit 70, `["terminated: SIGTERM"]`,
0.003 s response) holds; `_write_status` inside the timeline lock is genuinely in place; C1, N6, N8 are killed by their
named tests; C4 and N10 are confirmed equivalent by live differential; `os.replace` atomicity holds (0 torn reads, 0
mid-rewrite absences); the invariants hold on frozen legs; the cost bar is met at 1.005×; pyflakes is clean and the suite
is 83 passed / 1 xfailed on four independent runs.

No part of this verdict rests on anything I did not reproduce, **except**: the `S2`/`A6`/`S4` equivalence calls are static
arguments, not measurements (they affect only survivor triage, not the blocking set); and the PC-leg behaviour is unknown
here — if the 20-minute deadlock class is PC-specific, this sandbox grade cannot speak to it.
