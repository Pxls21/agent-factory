# VERIFY-B5g — round-12 adversarial grade of lane B5g (S0-01 frame tee: guards that can fail, pins that see dataflow, wording that matches the pinned source)

**Grade venue:** `git archive 0f2606d51fdc9be04d506e5f4f1e87e31804f45e | tar -x` copies under the session
scratchpad (`vb12pristine`, `vb12red`, `vb12mut`, `vb12cA/cB`, `vb12inst`). Shared tree: read-only git only,
never written. **STATUS: FINAL.**

## PREMISE (every row reproduced by me)

| item | value |
|---|---|
| PIN | `0f2606d51fdc9be04d506e5f4f1e87e31804f45e` — `git cat-file -e` OK |
| PIN subject | `S0-01 WIP checkpoint 8s: tee guards that can fail, pins that see dataflow, wording that matches the pinned source (lane B5g) — REVIEW-PENDING, nothing minted` |
| PIN parent | `4e6cc03`; the B5g change spans `4b43284..0f2606d` and is byte-identical to `1f32dc2..0f2606d` (verified) |
| `proofs/S0-01/tools/frame_tee.py` | sha256 `2f0666c2b2a91a025aaf3dad3be06e6f38b9dce8244d325258ec12d347416ac2`, **473** lines — matches the lane's FILE IDENTITY table |
| `tests/test_s0_01_frame_tee.py` | sha256 `b046bc24a6ee3bce4f4c102f062fea34dcdac8afeef9cb8c844d2d1301fcd1e0`, **2931** lines — matches |
| worktree == PIN bytes | both scope files `git status --porcelain`-clean at every check, sha256 equal to the PIN's throughout |
| shared-tree dirty set at start | A5i (`check_acp_conformance.py`, `test_s0_01_check_acp_conformance.py`, `tests/red/test_s0_01_backend_credential_screen.py`) + D5j (`scripted_backend.py`, `test_s0_01_scripted_backend.py`) — untouched by me |
| interpreter | `/usr/local/bin/python3` 3.11.15, pytest 9.1.1; `/usr/bin/python3.12` 3.12.3 and `/usr/bin/python3.13` 3.13.12 present, **no pytest on either** |
| xdist | not installed — substituted two concurrent pytest processes (as B5f did) |
| collected / defs | `98 tests collected in 0.03s`; `grep -c "    def test_"` → **90** (98 = 90 + 8 parametrised extras) — matches |
| nproc / `pid_max` / `df -h /` | 4 cores; `/proc/sys/kernel/pid_max` = **32768**; `/dev/vda 252G 30G 7.7G 80% /` |
| PREMISE SHIFT during my run | HEAD moved `0f2606d` → `9da1041` → `77546be` → `73efb9f` → `24e0961` and the tree went clean. **`git diff --stat 0f2606d HEAD -- <both scope files>` is EMPTY** and the worktree copies still hash `2f0666c2…` / `b046bc24…`. Grade unaffected. |
| PC leg | **NOT run by me.** No bridge banner, and my brief forbids outward actions. This is a **sandbox-only, single-worker grade.** |
| network | **NOT used.** `acp.rs@1c8321cd` was read from the session-scratchpad cache `acp_1c8321cd.rs`, sha256 `44e82861763694d2b82d02b15ee100ffd6c78874a2b2282865e6656c539c38f1` — byte-identical to the sha256 the B5f verifier recorded from its own fetch, and `upstream.lock.yaml:16-18` pins buzz at `1c8321cd08feb597f8bcff5195c21148fb3e98ed`. **This is a sha256-identity chain, not an independent re-fetch** — see the note under item 6. |

## GATE LINES (mine, verbatim, on the PIN venue)

```
PIN full suite, idle 1 (load 1.28 -> 1.80):      98 passed in 172.90s (0:02:52)   PYTEST_RC=0
PIN full suite, idle 2 (load 1.36 -> 1.20):      98 passed in 170.13s (0:02:50)   PYTEST_RC=0
PIN full suite, 4 CPU burners (load 2.19 -> 5.74):  98 passed in 179.75s (0:02:59)   PYTEST_RC=0
RED STATE, true parent tee 736bb94 + PIN tests, full suite, NO -x (load 1.70 -> 2.09):
                                                 9 failed, 89 passed in 173.91s (0:02:53)   PYTEST_RC=1
pyflakes proofs/S0-01/tools/frame_tee.py tests/test_s0_01_frame_tee.py     -> rc 0
tripwire through the PIN's checker (venue checker sha256 3edd8a2023c7…, NOT the shared tree's A5i edit de13655a…):
  test_sigterm_status_satisfies_check_tee_status   1 passed, 97 deselected in 0.20s
AP_SCREEN over the ADDED lines of the B5g delta (4b43284..0f2606d)        -> 0 hits
```
The coordinator's gates of record reproduce: sandbox `98 passed` (mine 172.90 s / 170.13 s vs the lane's
170.08 s / 169.49 s); the red state `9 failed, 89 passed` reproduces **exactly**, same nine test names.

---

# ITEM 1 — F1..F15 CLOSURE TABLE (VERIFY-B5f's findings), one row each

Every red-before below was produced by me on `vb12red` = the PIN's tests + `git show
736bb94:proofs/S0-01/tools/frame_tee.py` (sha256 `3fc846ce…`, 476 lines).

| # | B5f finding | closed by | my verdict (all reproduced unless stated) |
|---|---|---|---|
| **F1** [BLOCKING] red state did not reproduce; one CONTROL row was a deterministic RED | the lane re-ran the full suite on `736bb94`, no `-x`, and re-labelled the row | **CLOSED.** My run: `9 failed, 89 passed in 173.91s`, identical failure set to the lane's paste. `test_write_status_snapshot_and_rewrite_are_locked` is listed **genuine-red** and is red alone on the parent in 0.11 s (`test:2519`). |
| **F2** [MED] one row passed 5/5, one failed 5/5 | re-labelled: `test_sigterm_kills_agent_child` genuine-red, tripwire = CONTROL | **CLOSED.** My 5× on the parent: `kills_agent_child` **1 failed 5/5** (2.17-2.22 s); tripwire **1 passed 5/5** (0.20-0.21 s). Exactly the lane's labels. |
| **F3** [BLOCKING] five artifacts invert the pinned source | five sites reworded to "SIGKILLs the group (`killpg`) and then waits up to 5 s for it to exit" | **PARTLY CLOSED — a sixth site still contradicts the source.** The five listed sites are now accurate against `acp.rs@1c8321cd` (item 6). **`tests/test_s0_01_frame_tee.py:1517` still reads `# R1: SIGTERM it (buzz-acp's shutdown responsibility).`** — `grep -c SIGTERM acp.rs@1c8321cd` = **0**. See **F-B5g-2**. |
| **F4** [BLOCKING] doc-anchor is a string-only tautology | `test_docstring_pins_the_meaning_not_the_tokens` (3 tokens + 2 blacklist regexes) | **PARTLY CLOSED.** DOCSTRING-HYBRID and COMMENT-TERM now die (measured). But **two false docstrings that satisfy every assertion survive the full suite** — DOCSTRING-ORDER and DOCSTRING-WRONGEVENT, `98 passed` each. See **F-B5g-1**. The pin is still a token set + a two-item blacklist. |
| **F5** [MED] N4/D3 pin is a mirror | added `test_write_status_reads_no_state_outside_the_lock` beside the existing arm | **CLOSED for MIRROR-SNAPSHOT.** MIRROR-SNAPSHOT now **KILLED** (`state/seq read outside \`with lock:\` at [174…180]`, test:2542). The existing `status_lock`/`os.replace` arm was kept (D3 still dies on it). Residual mirror MIRROR-STALE passes the pin but dies on 11 other tests — see item 3(b). |
| **F6** [BLOCKING] census fail-open (`if …exists():`) | `assert gc_pid_path.exists()` at all 3 sites; `except (OSError, ValueError)` narrowed to `except ProcessLookupError` | **CLOSED.** PIDFILE-ABSENT dies at **all three sites individually** (item 4). |
| **F7** [BLOCKING] 14/16 typed `file:line` refs wrong | the lane regenerated the DONE table from `grep -n` | **CLOSED for the DONE table** (48 refs spot-checked, all land on the right statements). **NOT closed for the MUTANT/PROBE tables and the AP-screen block** — see **F-B5g-5**. |
| **F8** [LOW] three VALUE-form premise asserts vacuous under the sharp control | converted to the FLAG form at `test:503/510/515`, `:900/907/912`, `:1074/1081/1086` | **CLOSED and verified at all three sites.** Loop-only mutation KILLED at each: `test:515` 10.38 s, `test:912` 10.29 s, `test:1086` 10.42 s. The regression-class control (NC-PREMISE-REAL-501) also fires. |
| **F9** [BLOCKING] the coordinator's tripwire is vacuous | `loaded` flag + `assert loaded` at `test:2328/2335/2340` | **CLOSED.** NC-TRIPWIRE-LOOPONLY **KILLED**: `no recorded frame: the wait for updated_seq >= 1 timed out` at `test:2340`, `1 failed, 97 deselected in 10.35s`. |
| **F10** [LOW] undisclosed 7th AP-screen hit at `test:2120` | ruled FALSE POSITIVE in the report (`test:2138` on the B5g tree) | **CLOSED in substance, but the whole AP block is a carry-forward** — the B5g delta produces **zero** AP-screen hits (reproduced). See **F-B5g-5**. |
| **F11** [LOW] `proc = None` pin uses `any(...)` | `pre_proc` list + `assert pre_proc and all(...)` at `test:2798-2806` | **CLOSED.** MIRROR-PREINIT **KILLED** (`proc is rebound to a non-None value before the handler install`, test:2803); NO-PREINIT also killed by the same line. |
| **F12** [LOW] AF-AP-59 class not pinned, only the instance | `test_grandchild_cleanup_is_own_pid_scoped` — two split-needle literals | **NOT CLOSED.** B5f's exact CENSUS-WORLD spelling dies, but **six spellings of the same world-scoped census pass the pin**, two of them literal `pgrep -f`. See **F-B5g-3**. The class is still only instance-pinned. |
| **F13** [LOW, UNSURE] no identity check before the kill | `/proc/<pid>/cmdline` must contain `time.sleep`; `FileNotFoundError` → already gone | **CLOSED for pid reuse (which is unreachable here), and it introduces a new fail-loud-on-benign-race path.** A ZOMBIE has an existing `/proc/<pid>` and an EMPTY cmdline → the assert fires. Measured 6/6, window ≈ 0.97 s. Not reachable at any of the three current sites (margins measured). See **F-B5g-4** and item 4. |
| **F14** [INFO] header named the dispatch commit as the PIN | header now says "Dispatched at `cf48eda`. Work landed in child commit on HEAD `1f32dc2`" | **NOT MET.** `1f32dc2` is not the landing commit — `git diff 1f32dc2 0f2606d -- <both scope files>` is **133 insertions / 62 deletions**; `git show 1f32dc2:tests/test_s0_01_frame_tee.py` gives the pre-B5g file. The landing commit is `0f2606d` and it is named nowhere in the report. See **F-B5g-6**. |
| **F15** [INFO] `assert gone` sits before the pipe closes | closes moved inside the `finally` at `test:560-561/1133-1134/2664-2665` | **PARTLY CLOSED — and the DONE table's claim for it is false.** The closes are inside the `finally` but still **after** `assert gc_pid_path.exists()`, the F13 identity assert and `assert gone`. The design said "before the own-pid assertion". The lane's row reads "ensures pipe close even on assertion failure" — it does not. See **F-B5g-7**. |

### Every new/changed test against the TRUE parent tee (`736bb94`), individually — my runs

| test | on the parent | lane's label | my label |
|---|---|---|---|
| `test_docstring_pins_the_meaning_not_the_tokens` | **RED** `module docstring does not name killpg` (test:2918), 0.16 s | genuine-red | **agree** |
| `test_write_status_reads_no_state_outside_the_lock` | **RED** `state/seq read outside \`with lock:\`` (test:**2542**), 0.11 s | genuine-red (says test:2541) | **agree; line off by 1** |
| `test_write_status_snapshot_and_rewrite_are_locked` | **RED** `stdin_reader_done is not read inside \`with lock:\`` (test:2519), 0.11 s | genuine-red | **agree** |
| `test_status_write_follows_timeline_write_in_pumps` | GREEN 0.04 s | CONTROL — kills S1 | **agree** (S1 and S1F both die on it) |
| `test_grandchild_cleanup_is_own_pid_scoped` | GREEN 0.04 s | CONTROL — kills CENSUS-WORLD | **agree for that ONE spelling only** — six other spellings pass (F-B5g-3) |
| `test_sigterm_status_satisfies_check_tee_status` | GREEN 0.20-0.21 s **5/5** | CONTROL — premise assert | **agree** (kills NC-TRIPWIRE-LOOPONLY) |
| `test_grandchild_straggler_recorded` | **RED** | genuine-red | agree |
| `test_grandchild_never_closes_sigterm_required` | **RED** | genuine-red | agree |
| `test_drain_loops_have_no_break_or_timeout` | **RED** (test:2432) | genuine-red | agree |
| `test_sigterm_during_sha256_produces_status` | **RED** | genuine-red | agree |
| `test_no_statement_between_signal_and_try` | **RED** (test:2788) | genuine-red | agree |
| `test_sigterm_kills_agent_child` | **RED 5/5** (2.17-2.22 s) | genuine-red | agree |
| `test_timeline_before_directional_in_pumps` | GREEN 0.04 s | (not listed) | CONTROL — kills N3 |
| the three `finally` blocks (F6/F13/F15) | GREEN on the parent | (not labelled) | CONTROL — kills PIDFILE-ABSENT ×3 and GRANDCHILD-UNKILLED (sites 1-2 only) |
| the three FLAG-form premise asserts (F8) | GREEN on the parent | CONTROL (one site pasted) | CONTROL at all three — kills the loop-only mutation at each (item 5) |

**One correction to the lane's F3 red-before.** The DONE table says F3's red-before is "genuine-red via F4
test (`source says 'SIGKILLs the group after 5 s'`)". On the parent that assertion is **never reached** — the
F4 test dies three assertions earlier at `test:2918` (`module docstring does not name killpg`). The honest
red-before for F3's five sites is COMMENT-TERM, which I measured dying with exactly that message at
`test:2928`.

---

# ITEM 2 — THE MUTANT TABLE, MEASURED BY ME ON THE PIN

Runner `vb12mut.py` + `vb12muts.py` (B5f's 40, re-anchored on the B5g bytes) + `vb12muts2.py` (my own 17).
Protocol per mutant: restore both scope files from the pristine archive → apply → `ast.parse` both → run the
NAMED killer(s) → **escalate a green to the full suite, no `-x`** → restore → re-assert sha256
(`2f0666c2b2a9` / `b046bc24a6ee`, printed by the runner after every batch). An anchor dry-run confirmed all
51+10 mutants apply cleanly and change bytes before any pytest ran (0 PATCH-FAILED, 0 NO-OP, 0 SyntaxError).

**Safety deviation, stated up front:** B5f's `CENSUS-WORLD` kills every `import time; time.sleep` process on
the box. The shared box carries two other lanes' live processes, so I did **not** run a mutant that signals a
pid it did not spawn. The F12 pin is a *pure text* pin, so I graded CENSUS-WORLD by running only
`test_grandchild_cleanup_is_own_pid_scoped` against the mutated source (that test reads the file and spawns
nothing), and my six census VARIANTS are enumerate-only with the own-pid kill left intact.

## A. B5f's 40, re-measured on the B5g tree

| # | id | result on the PIN | killer (NAMED) / note |
|---|---|---|---|
| 1 | INSTALL-LATE | **KILLED** | `test_sigterm_during_sha256_produces_status` (`-15 == 70`, test:2730) + `test_no_statement_between_signal_and_try` (`Popen precedes the handler install`, test:2792) |
| 2 | GAP-1 | **KILLED** | `test_no_statement_between_signal_and_try` (`statement after signal.signal is Assign at line 213`, test:2788) |
| 3 | EXCEPT-WRONG | **KILLED** | `test_sigterm_writes_status_and_exits_70` + `…during_sha256…` (`1 == 70`) |
| 4 | EXIT-0 | **KILLED** | same two (`0 == 70`) |
| 5 | STATUS-FINAL-TRUE | **KILLED** | same two (write_errors mismatch, test:2735) |
| 6 | ERR-MISSING | **KILLED** | same two (`[] == ['terminated: SIGTERM']`, test:2734) |
| 7 | ORPHAN | **KILLED** | `test_sigterm_kills_agent_child` (`agent pid 3518 state S after 2 s`, test:2893) |
| 8 | TRY-SHRINK2 | **KILLED** | same two as EXCEPT-WRONG (`1 == 70`) — B5f's implementation reproduces |
| 9 | N3 | **KILLED** | `test_timeline_before_directional_in_pumps` (`tl.write at 282 is NOT before df.write at 277`, test:2476) |
| 10 | PUMP-TIMEOUT | **KILLED** | straggler + `test_grandchild_never_closes_sigterm_required` (`tee exited before 15 s`, test:1089) |
| 11-14 | A2-t0 / t1 / t5 / t30 | **KILLED ×4** | `test_drain_loops_have_no_break_or_timeout` (`expected 2 drain loops…found 1`, test:2413) |
| 15-16 | a2c-t0 / a2c-t5 | **KILLED ×2** | straggler **and** the structural pin |
| 17 | a2c-t30 | **KILLED** | structural pin only — B5f's reading of F-B5e-9 reproduces |
| 18 | A2C-DELETE | **KILLED** | straggler + structural pin |
| 19 | A2C-WRONG-THREAD | **KILLED** | `test_grandchild_straggler_recorded` only |
| 20 | S1 | **KILLED** | AST pin (`_write_status at 275 precedes tl.write at 278`, test:2497) |
| 21 | S1F (faithful) | **KILLED** | AST pin (test:2497); also `test_directional_trails_timeline_after_sigkill` (`trial 0: lag -1 not in {0,1}`, test:2141). Graded by the single-sample lag alone it **survives** — B5f's 12-trial claim reproduces |
| 22 | N4 | **KILLED** | now by **two** pins: `…snapshot_and_rewrite_are_locked` (test:2513) **and** the new `…reads_no_state_outside_the_lock` |
| 23 | D3 | **KILLED** | `…snapshot_and_rewrite_are_locked` (`no \`with status_lock:\``, test:2514) — the arm the new pin does NOT cover |
| 24 | INSTALL-LATE-B | **KILLED** | AST pin (test:2792) |
| 25 | NO-PREINIT | **KILLED** | AST pin, now via the `all(...)` message (test:2803) |
| 26 | LOCK-READS-OUT | **KILLED** | both lock pins (test:2519 and test:2542, `[177, 182]`) |
| 27 | DOCSTRING-TERM | **KILLED** | F4 test (`module docstring does not name killpg`, test:2918) |
| 28 | GRANDCHILD-UNKILLED | **KILLED** | `test_grandchild_keeps_tee_alive` (`grandchild pid 3898 still alive after kill`, test:559). **Graded on site 3 alone it SURVIVES** (`1 passed in 45.35s`) — see F-B5g-8 |
| 29 | DRAIN-ORDER | **EQUIVALENT** | `2 passed` named; **FULL SUITE `98 passed in 169.65s`**. B5f's ruling stands |
| 30 | **DOCSTRING-HYBRID** | **KILLED** (was SURVIVED) | F4 test (`does not state SIGKILL cannot be handled`, test:**2919**) — the lane's table says test:2922 |
| 31 | **COMMENT-TERM** | **KILLED** (was SURVIVED) | F4 test wrap-tolerant regex (`source says 'SIGKILLs the group after 5 s'`, test:**2928**) — the lane's table says test:2926 |
| 32 | **PIDFILE-ABSENT** | **KILLED** (was SURVIVED) | all three sites, `3 failed, 95 deselected in 63.77s` — test:**525**, :**1096**, :**2625** (the lane pasted one line, "test:526", which matches none) |
| 33 | **CENSUS-WORLD** (B5f's exact spelling) | **KILLED** | `test_grandchild_cleanup_is_own_pid_scoped` (`a world-scoped process sweep is back in the test file (AF-AP-59)`) — text-only run, no processes touched |
| 34 | LAG-12-DROPPED | **SURVIVED** — `1 passed`, **FULL SUITE `98 passed in 169.61s`** | assertion deletion; excluded from the denominators, as B5f had it |
| 35 | **PIN-LOCK-NAME** | **SURVIVED** — **FULL SUITE `98 passed in 170.52s`** | **accepted rename mirror — I concur, see the ruling below** |
| 36 | **MIRROR-SNAPSHOT** | **KILLED** (was SURVIVED) | the new F5 pin (`state/seq read outside \`with lock:\` at [174…180]`, test:2542) |
| 37 | **MIRROR-PREINIT** | **KILLED** (was SURVIVED) | the F11 `all(...)` pin (test:2803) |
| 38 | MIRROR-S1-FLUSH | **KILLED** | `test_directional_trails_timeline_after_sigkill` (`trial 2: dir c2a (502) > timeline c2a (501)`, test:2131) |
| 39 | PIN-NULLLOCK | **KILLED** | race test (`1 torn reads out of 2685965`, test:2667) |
| 40 | PIN-NULLLOCK-L | **KILLED** | race test (`29 snapshots where updated_seq != recorded_c2a + recorded_a2c`, test:2668) |

## B. The lane's 8 targeted mutants — all re-measured, all confirmed

| id | lane's claim | my measurement |
|---|---|---|
| DOCSTRING-HYBRID | KILLED, test:2922 | **KILLED**, test:**2919** |
| COMMENT-TERM | KILLED, test:2926 | **KILLED**, test:**2928** |
| PIDFILE-ABSENT | KILLED, test:526 | **KILLED** at test:**525 / 1096 / 2625** |
| CENSUS-WORLD | KILLED, test:2813 | **KILLED**; the assertion is at test:**2815** (2813 is `needle_pgrep = …`) |
| MIRROR-SNAPSHOT | KILLED, test:2541 | **KILLED**, test:**2542** |
| MIRROR-PREINIT | KILLED, test:2806 | **KILLED**, test:**2803** |
| NC-TRIPWIRE-LOOPONLY | KILLED, test:2340, 10.32 s | **KILLED**, test:2340, 10.35 s ✔ |
| NC-VALUE-LOOPONLY-501 | KILLED, test:515, 10.36 s | **KILLED**, test:515, 10.38 s ✔ |

Every kill is real. Six of the eight pasted killer lines are off by 1-3 lines or name a non-assert line; two
are exact — and the two exact ones are the two the lane could copy straight from a pytest tail.

## C. My own 17 (item 3 and the gaps)

| id | what it does | result |
|---|---|---|
| **DOCSTRING-ORDER** | docstring keeps `killpg`, `SIGKILL cannot be handled`, `last RUNNING status`, trips neither regex, and says buzz-acp **sends SIGTERM first and escalates to killpg only after 5 s** | **SURVIVED — `98 passed in 170.42s`** |
| **DOCSTRING-WRONGEVENT** | same tokens; the 5 s bound stated on the **wrong event** ("how long buzz-acp waits BEFORE the kill") | **SURVIVED — `98 passed in 169.34s`** |
| **TESTDOC-TERM** | reverts ONE **test** docstring (test:862-863) to "SIGKILLs the group after 5 s" | **SURVIVED — `98 passed in 169.44s`** |
| **MIRROR-STALE** | every field read inside `with lock:` (F5 pin passes) but the object published is the PREVIOUS call's locked snapshot | pin **PASSES**, race test **passes 3/3 named (45.4 s)**; **FULL SUITE KILLED — `11 failed, 87 passed`** by exact-value assertions |
| **CENSUS-PS-E** | `ps -eo pid,args` + a Python filter | pin **PASSES** |
| **CENSUS-PGREP-X** | `pgrep -x python3` + `/proc/<pid>/cmdline` filter | pin **PASSES** |
| **CENSUS-PGREP-A** | `pgrep -a -f time.sleep` | pin **PASSES** |
| **CENSUS-PROC-WALK** | `os.listdir("/proc")` scan | pin **PASSES** |
| **CENSUS-PGREP-TIGHT** | `subprocess.run(["pgrep","-f","import time; time.sleep"]…)` — the banned shape with the two spaces removed | pin **PASSES**; full suite red only on the mutant's OWN emptiness assertion (`world census: 8920` — a sibling test's sleeper, in a *serial* venue) |
| **CENSUS-PKILL-SQ** | `subprocess.run(['pkill', '-f', …])` — single quotes | pin **PASSES** |
| **PIDFILE-ABSENT-S1/-S2/-S3** | the pid file is written at the other two sites but not this one | **KILLED ×3**: test:525 (3.38 s) · test:1098 (15.36 s) · test:2629 (45.34 s) |
| **GRANDCHILD-UNKILLED-S3** | drop the own-pid kill, graded by site 3 only | **SURVIVED** `1 passed, 97 deselected in 45.35s` |
| **NC-LOOPONLY-900** | loop-only threshold at the 2nd FLAG site | **KILLED** `no a2c frame recorded before SIGTERM` test:912, 10.29 s |
| **NC-LOOPONLY-1074** | loop-only threshold at the 3rd FLAG site | **KILLED** `no a2c frame recorded before the liveness window` test:1086, 10.42 s |
| **NC-PREMISE-REAL-501** | the real regression: the fixture agent never emits the handshake | **KILLED** test:512, 10.37 s |
| **NC-FLAG-LOOPONLY** | the contention test's loop-only threshold (B5f's sharp control) | **KILLED** (re-measured) |

```
TOTALS over the 48 rows the brief names (B5f's 40 + the lane's 8; the 8 are a subset of the 40's ids):
  KILLED-BY-NAMED   37   (was 27 in round 11)
  EQUIVALENT         1   DRAIN-ORDER            (full-suite SURVIVED, 98 passed — accepted)
  SURVIVED (real)    1   PIN-LOCK-NAME          (accepted rename mirror — ruling below)
  EXCLUDED           1   LAG-12-DROPPED         (assertion deletion, not a code mutant)
  PATCH-FAILED       0   SYNTAX-ERROR 0
PLUS my 17: 10 SURVIVED (3 docstring/test-doc + 6 census spellings + MIRROR-STALE-at-the-pin),
            7 KILLED.
```

### PIN-LOCK-NAME — my ruling: **accepted, and the acceptance is load-bearing, not a shrug**
The mutant renames `status_lock` → `stlock` in the tee **and** in the pin's string, so the pin passes by
construction; full suite `98 passed in 170.52s`. A rename is semantically neutral: nothing observable
changes. The question that matters is whether the pin's *name* is the only thing holding the lock, and it is
not — **PIN-NULLLOCK** keeps the name `status_lock` and makes it `contextlib.nullcontext()`, and the race
test kills it (`1 torn reads out of 2685965`). Same for `lock` (PIN-NULLLOCK-L, `29 snapshots where
updated_seq != recorded_c2a + recorded_a2c`). So the name pin is a *readability* pin sitting behind a
behavioural one. **Accepted.** The one thing I would add is that this is only true while the race test
exists; if it is ever deleted or shortened, the name pin becomes the whole guard and PIN-LOCK-NAME stops
being benign.

---

# ITEM 3 — THE NEW PINS ATTACKED AS MIRRORS

## 3(a) F4 `test_docstring_pins_the_meaning_not_the_tokens` — it still pins a token set

The pin (`tests/test_s0_01_frame_tee.py:2915-2931`) asserts five things: `killpg` ∈ doc,
`SIGKILL cannot be handled` ∈ doc, `last RUNNING status` ∈ doc, `SIGTERM path[^.]*(covers it|bounds)` ∉ doc,
and `SIGKILLs[\s#]+the[\s#]+group[\s#]+after[\s#]*5[\s#]*s` ∉ **the tee source**.

I wrote two docstrings that satisfy all five and still misstate the pinned behaviour. Both **survive the
whole suite**.

**DOCSTRING-ORDER — a false ORDER (exactly the counter-example the brief predicted):**
```
buzz-acp ends such a leg by sending SIGTERM to the group first and only
escalating to ``killpg(SIGKILL)`` if the group ignores it for 5 s
(``crates/buzz-acp/src/acp.rs:421-444``, pinned ``1c8321cd``); once it
escalates, SIGKILL cannot be handled, so the leg's evidence is its
last RUNNING status (A21d).  A wedged leg therefore gets a 5 s grace
period before the group dies.
```
```
DOCSTRING-ORDER  named killer : 1 passed, 97 deselected in 0.04s
DOCSTRING-ORDER  FULL SUITE   : SURVIVED   98 passed in 170.42s (0:02:50)
```
It is false in the strongest possible way: **`grep -c SIGTERM` over `acp.rs@1c8321cd` is `0`.** A reader of
this docstring would budget a 5 s grace period that does not exist — the identical operational error F-B5e-1
and F3 were opened for.

**DOCSTRING-WRONGEVENT — the bound on the wrong event:**
```
buzz-acp ends such a leg with ``killpg(SIGKILL)`` on the whole process
group; the 5 s bound is on how long buzz-acp waits BEFORE the kill for
the leg to drain (...); SIGKILL cannot be handled, so the leg's evidence is its
last RUNNING status (A21d).
```
```
DOCSTRING-WRONGEVENT  named killer : 1 passed, 97 deselected in 0.05s
DOCSTRING-WRONGEVENT  FULL SUITE   : SURVIVED   98 passed in 169.34s (0:02:49)
```

**A first attempt of mine was killed by an accident and I caught it by running it.** My original
DOCSTRING-ORDER line-wrapped as `…so the leg's evidence is its last RUNNING status` but broke `SIGKILL\ncannot
be handled` across a newline, so the literal token check failed (`test:2919`) — a kill by line-wrapping, not
by meaning. I re-wrote the mutant to keep every asserted phrase on one line before reporting the result
(AF-AP-36: a verifier's proposed mutant is a hypothesis like any other). That accident is itself evidence:
**three of the five assertions are whitespace-sensitive literal substring checks over prose.**

**Grade: the assertion pins a token set, not meaning.** The two positive tokens are necessary conditions
that a false docstring can satisfy verbatim; the two negatives are a blacklist of the two mutations already
known. The design's own words ("the doc-anchor pins MEANING") are not met.

**Third measured hole: the scope claim in the test's own docstring is false.** `test:2911-2912` says the pin
covers "**the whole source file (comments + test docstrings included)**". It reads `src = Path(TEE).read_text()`
— `proofs/S0-01/tools/frame_tee.py` only. Mutant **TESTDOC-TERM** reverts one *test* docstring (test:862-863)
to "SIGKILLs the group after 5 s":
```
TESTDOC-TERM  named killer : 1 passed, 97 deselected in 0.19s
TESTDOC-TERM  FULL SUITE   : SURVIVED   98 passed in 169.44s (0:02:49)
```
So the increment whose subject line is "wording that matches the pinned source" ships a test whose docstring
misstates its own scope — the hollow green in prose, inside the guard against hollow greens in prose. The
lane's SELF-ATTACK #2 admits the mechanism; the test's docstring still claims the opposite.

**Measured scope enumeration** (so this is not an argument): exactly eight tests read `Path(TEE)`
(test:2366, 2395, 2443, 2484, 2504, 2531, 2766, 2915) and exactly one reads `Path(__file__)` (test:2811).
Nothing else in the file reads either source.

## 3(b) F5 `test_write_status_reads_no_state_outside_the_lock` — stale-but-locked

**MIRROR-STALE**: `_write_status` keeps the whole `with lock:` snapshot (so no `state[…]`/`seq[…]` Subscript
exists outside it and the pin passes), then publishes the **previous** call's locked snapshot from a closure
cache:
```python
_cur = (snap_seq, snap_rec_c2a, …, snap_errors)
if _prev_snap:
    (snap_seq, snap_rec_c2a, …, snap_errors) = _prev_snap["v"]
_prev_snap["v"] = _cur
```
```
MIRROR-STALE  named killers (snapshot pin + dataflow pin + the 45 s race test):
              3 passed, 95 deselected in 45.39s      <- ACCEPTED by all three
MIRROR-STALE  FULL SUITE:  11 failed, 87 passed in 173.22s (0:02:53)
              e.g. TestTeeStatus::test_signal_exit_status,
                   TestSigtermHandler::test_sigterm_writes_status_and_exits_70,
                   TestRunningStatus::test_directional_trails_timeline_after_sigkill, …
```
**Answer to the brief's question: yes, the new pin accepts it, and no, the race test does not catch it (3/3
green, 45.4 s).** The class is nonetheless covered — by eleven ordinary exact-value assertions on the
published status. So F5's pin is a mirror for stale-but-locked, but the *defect* is not un-gated. That is
worth stating precisely because the lane's DONE table presents the pin as the guard: the guard here is the
value assertions, and the pin's contribution is limited to the "read outside the lock" shape (which it does
kill — MIRROR-SNAPSHOT, N4, LOCK-READS-OUT).

## 3(c) F12 `test_grandchild_cleanup_is_own_pid_scoped` — the instance is pinned, the class is not

The pin is two literal substrings: `subprocess.run(["pgrep", "-f"` and `"pkill"` (double-quoted). Measured,
one variant per row, each run against the pin alone:

| variant | census it reintroduces | F12 pin |
|---|---|---|
| CENSUS-WORLD (B5f's exact text) | `subprocess.run(["pgrep", "-f", …])` | **KILLED** ✔ |
| **CENSUS-PGREP-TIGHT** | `subprocess.run(["pgrep","-f", …])` — same call, two spaces removed | **PASSES** |
| **CENSUS-PGREP-A** | `subprocess.run(["pgrep", "-a", "-f", "time.sleep"])` | **PASSES** |
| **CENSUS-PGREP-X** | `pgrep -x python3` + a `/proc/<pid>/cmdline` filter | **PASSES** |
| **CENSUS-PS-E** | `ps -eo pid,args` + a Python filter | **PASSES** |
| **CENSUS-PROC-WALK** | `os.listdir("/proc")` scan | **PASSES** |
| **CENSUS-PKILL-SQ** | `subprocess.run(['pkill', '-f', …])` — single quotes | **PASSES** |

**The CLASS is not pinned; only the one spelling B5f happened to write is.** Two of the six survivors are
literal `pgrep -f` — the exact string AF-AP-59 is named after.

**And the repo already contains a strictly better pin.** `.claude/hooks/edit-snapshot.py` gained an AF-AP-59
row in `cf48eda` — *the very commit that dispatched this lane* — with the signature
```
["']pgrep["']\s*,\s*["']-f["']|\bpgrep\s+-f\b|["']ps["']\s*,\s*["']-e[a-z]*["']
```
That regex catches CENSUS-WORLD, CENSUS-PGREP-TIGHT, CENSUS-PGREP-A and CENSUS-PS-E (4 of my 6 + B5f's).
**Cheapest structural pin that closes most of the class:** import `AP_SCREEN` from the hook (the pattern
B5f already used for its F10 work) and assert that no row matches the test file's own source — one import
and one loop, strictly stronger than two hand-typed literals, and it can never drift from the registry.

**But text cannot close the class, and the brief's design should say so.** `CENSUS-PGREP-X` and
`CENSUS-PROC-WALK` evade every plausible word list, and so would `shell=True`, `psutil.process_iter()`, or an
argv built by concatenation. The durable closure is **ownership-by-construction**: one
`_kill_own_grandchild(framedir)` helper that reads the pid file, checks identity and kills, plus an AST pin
that `os.kill` and every `subprocess.*` call in the file appear only inside that helper (or in a named
allow-list of call sites). Then a world-scoped sweep cannot be *added* without breaking a structural
assertion, rather than merely failing to match a string. I would ship the AP_SCREEN import now (minutes) and
the helper + AST pin as the real fix.

---

# ITEM 4 — F6 (the census that cannot skip) and F13 (identity before the kill)

## 4a. F6 — PIDFILE-ABSENT dies at ALL THREE sites, measured individually

The lane pasted one line. I built three single-site mutants (the fixture agent writes `grandchild.pid` at
the other two sites and not at this one) plus the combined one:

```
PIDFILE-ABSENT-S1   KILLED   3.38s   AssertionError: agent never wrote grandchild.pid   test:525
                    FAILED …TestGrandchildStdout::test_grandchild_keeps_tee_alive
PIDFILE-ABSENT-S2   KILLED  15.36s   AssertionError: agent never wrote grandchild.pid   test:1098
                    FAILED …TestTeeStatus::test_grandchild_never_closes_sigterm_required
PIDFILE-ABSENT-S3   KILLED  45.34s   AssertionError: agent never wrote grandchild.pid   test:2629
                    FAILED …TestStructuralPins::test_concurrent_main_thread_status_vs_pump
PIDFILE-ABSENT (all three)   3 failed, 95 deselected in 63.77s
                    test:525  test_grandchild_keeps_tee_aliv0/frames/grandchild.pid
                    test:1096 test_grandchild_never_closes_s0/frames/grandchild.pid
                    test:2625 test_concurrent_main_thread_st0/frames/grandchild.pid
```
**F6 is genuinely closed at all three sites.** (Line numbers differ from the PIN's 527/1100/2631 by the 2/4/6
lines each mutant deletes above the site — none of them is the lane's pasted "test:526".)

I also confirmed the F6 fix does not add a flake: the pid file was present in every one of my PIN runs
(2 idle suites, 1 burner suite, 10 concurrent-process runs, ~12 full suites inside mutant escalations).

## 4b. F13 — the identity assert: right hazard, wrong failure semantics

The implementation (`test:533-538`, `:1106-1111`, `:2637-2642`, identical at all three):
```python
try:
    cmdline = open("/proc/%d/cmdline" % gc_pid).read().replace("\0", " ")
    assert "time.sleep" in cmdline, (
        "pid %d is not the grandchild (cmdline: %s)" % (gc_pid, cmdline))
except FileNotFoundError:
    gc_pid = None  # already gone
```

**The reachable direction is NOT pid reuse — it is the zombie.** A process that has exited but not yet been
reaped still has `/proc/<pid>` and reads back an **EMPTY** cmdline, so the assert fires. `FileNotFoundError`
covers only the fully-reaped case. Measured (`vb12zombie.py`, the fixture shape — parent spawns grandchild,
parent exits, grandchild is reparented to pid 1):
```
rep0 gc_pid=12220  empty-cmdline window ends 1.765s  /proc gone at 1.767s  F13_ASSERT_WOULD_FIRE=True
rep1 … 1.970 / 1.972  True      rep2 … 1.971 / 1.973  True
rep3 … 1.970 / 1.972  True      rep4 … 1.969 / 1.971  True      rep5 … 1.968 / 1.970  True
```
Grandchild `sleep(1.0)` → the **zombie window is ≈ 0.97 s, 6/6**, and the F13 assert fires throughout it.
A benign outcome (our grandchild died on its own, which is exactly what the census wants) is reported as a
test FAILURE with a confusing message (`pid N is not the grandchild (cmdline: )`).

**Is it reachable at the three call sites? Measured: no, with a 14 s margin — but only at the site that
matters.** I instrumented all three F13 checks and ran them:
```
F13-BRANCH present pid=13735 state=S cmdline_len=53 match=True   <- site 1 (grandchild sleep(30), body ~3.4 s)
F13-BRANCH present pid=13742 state=S cmdline_len=54 match=True   <- site 2 (grandchild sleep(120), body ~15 s)
F13-BRANCH already-gone pid=13750 (kill and `assert gone` SKIPPED)  <- site 3
3 passed, 95 deselected in 63.79s
```
Site 3's grandchild is the 3000×`sleep(0.01)` streamer; the census runs at the spin loop's fixed 45 s
deadline (`test:2607`). Grandchild lifetime, measured:
```
IDLE            30.48s / 30.54s / 30.46s   margin to the 45 s census 14.5s
4 CPU BURNERS   30.64s / 30.76s / 30.56s   margin 14.2-14.4s   (load 2.9 -> 4.0)
```
`time.sleep(0.01)` dominates, so load barely moves it: the 0.97 s zombie window sits 14 s away from the
census. **Not reachable today. It is a timing margin, not a structural guarantee** — halving the loop
deadline, lengthening the stream, or a venue with coarser sleep granularity puts the census in the window.

**Pid reuse — the direction the design named — is unreachable here, with the arithmetic.**
`/proc/sys/kernel/pid_max = 32768`. Pid allocation rate measured across a full suite under 4 burners:
`14682 → 15608 over 180 s` = **5.1 pids/s** (idle sampling gave the same order, ~18/s peak inside the
suite). Reuse of a *specific* pid requires the allocator to travel a full lap, i.e. ≈ 32768 pids between
allocation and the census. Sites 1 and 2 hold a **live** grandchild at census (measured above), so reuse is
impossible there. At site 3 the grandchild is allocated ≈ 45 s before the census, so reuse needs
32768/45 ≈ **728 pids/s** — 140× the measured rate. `P(reuse) ≈ 0` in this sandbox. On the PC under
`-n 8` the rate would have to rise ~140× as well; I did not measure it there (PC leg NOT run).

**Ruling: the semantic is wrong, though not currently harmful.** "The pid at `/proc/<pid>` is not our
grandchild" means **our grandchild is gone** — the census's success condition. Failing the test there
converts a pass into a red. Fail-loud belongs on the one case that is genuinely alarming: a *live* process
with a different cmdline. Safer form, same three sites:
```python
gone_or_foreign = False
try:
    cmdline = open("/proc/%d/cmdline" % gc_pid).read().replace("\0", " ")
except FileNotFoundError:
    gone_or_foreign = True                      # reaped
else:
    if "time.sleep" not in cmdline:
        st = open("/proc/%d/stat" % gc_pid).read().split()[2]
        assert st == "Z", (                     # a LIVE foreign process is the real alarm
            "pid %d is a live foreign process, refusing to kill it (cmdline: %s)" % (gc_pid, cmdline))
        gone_or_foreign = True                  # zombie: our grandchild, already dead
if gone_or_foreign:
    gc_pid = None
else:
    os.kill(gc_pid, sig.SIGKILL)
```
*Exact red test to add:* a fixture whose grandchild exits ~0.3 s before the census (`sleep(0.3)` with the
liveness gate removed) — RED on the PIN today with `pid N is not the grandchild (cmdline: )`, GREEN under
the form above. The structural answer that needs no heuristic at all is `os.pidfd_open(gc_pid)` taken while
the grandchild is known alive (3.9+), or putting the grandchild in its own process group and `killpg`-ing the
recorded pgid — both immune to reuse by construction.

## 4c. Site 3's census does no work beyond the pid-file assertion

The instrumentation above shows site 3 always takes the already-gone branch, so its `os.kill` and its
`assert gone` never execute. Measured consequence:
```
GRANDCHILD-UNKILLED graded on site 3 alone:  SURVIVED   1 passed, 97 deselected in 45.35s
```
Sites 1 and 2 carry the entire kill-path coverage (GRANDCHILD-UNKILLED dies there,
`grandchild pid 3898 still alive after kill`, test:559). Not blocking — but the DONE table's "the grandchild
census cannot skip" is true of the pid-file assertion at three sites and of the kill at **two**.

---

# ITEM 5 — F8/F9 FLAG-FORM PREMISES AT ALL FOUR SITES, AND THE NEGATIVE DIRECTION

## 5a. The loop-only mutation is red at every one of the four sites

Each control mutates **only** the loop's break threshold to `>= 10**9`; the post-loop `assert loaded` is
untouched. This is the sharp AF-AP-57 shape that left the old VALUE form green in round 11.

| site | test | control | result |
|---|---|---|---|
| `test:503/510/515` | `test_grandchild_keeps_tee_alive` | NC-VALUE-LOOPONLY-501 | **KILLED** `no a2c frame recorded before the liveness window` **test:515**, `1 failed, 97 deselected in 10.38s` |
| `test:900/907/912` | `test_never_reading_client` | NC-LOOPONLY-900 | **KILLED** `no a2c frame recorded before SIGTERM` **test:912**, `10.29s` |
| `test:1074/1081/1086` | `test_grandchild_never_closes_sigterm_required` | NC-LOOPONLY-1074 | **KILLED** `no a2c frame recorded before the liveness window` **test:1086**, `10.42s` |
| `test:2328/2335/2340` | `test_sigterm_status_satisfies_check_tee_status` (the tripwire) | NC-TRIPWIRE-LOOPONLY | **KILLED** `no recorded frame: the wait for updated_seq >= 1 timed out` **test:2340**, `10.35s` |
| `test:1643/1650/1655` | `test_sigterm_no_deadlock_under_contention` (was already FLAG) | NC-FLAG-LOOPONLY | **KILLED** (re-measured) |

The regression-class control also fires: **NC-PREMISE-REAL-501** (the fixture agent never emits the
handshake response, so the tee records no a2c frame at all) → `1 failed`, `no a2c frame recorded before the
liveness window` at test:512, 10.37 s. So the asserts fire both under the sharp mutation *and* on the real
regression they exist for. **F8 and F9 are closed, at five sites, verified by me.**

## 5b. Negative direction — the whole suite under 4 CPU burners

`nproc` = 4, so four spinners double-subscribe the box.
```
BURNER PIDS: 14665 14666 14667 14668            (mine; killed by pid afterwards, verified gone)
LOAD-WITH-BURNERS 2.19 1.89 1.73      LOAD-END 5.74 3.67 2.45
98 passed in 179.75s (0:02:59)     PYTEST_RC=0
```
**Zero premise-assert flakes: 98/98 green at 1-minute load 5.74, wall +5.4 % vs the 170.13 s idle run.**
The lane introduced no contention flake. (B5f measured +21 % on its tree at load 7.45; my window was
quieter, so the two are not directly comparable — the verdict, 0 flakes, is the same.)

---

# ITEM 6 — F3: THE WORDING AGAINST THE PINNED SOURCE

**Source provenance, stated honestly.** My brief's non-negotiables forbid network beyond localhost, so I did
**not** re-fetch `acp.rs`. I read the session-scratchpad copy `acp_1c8321cd.rs`, whose sha256
`44e82861763694d2b82d02b15ee100ffd6c78874a2b2282865e6656c539c38f1` (5030 lines) equals the value the B5f
verifier recorded from its own `raw.githubusercontent.com` GET, and `upstream.lock.yaml:16-18` pins buzz at
`1c8321cd08feb597f8bcff5195c21148fb3e98ed`. **This is a sha256-identity chain over a cached artifact, not an
independent re-resolution.** Every claim below was re-derived by me from that file's bytes.

Re-derived from the cached pinned source:
* `acp.rs:422-444` `pub async fn shutdown(&mut self)` — `match self.child.id() { Some(pid) if kill_process_group(pid) => {} _ => { let _ = self.child.start_kill(); } }`, **then**
  `tokio::time::timeout(std::time::Duration::from_secs(5), self.child.wait())` at `:439`, with the comment at
  `:436-437` *"Bounded wait: if the child doesn't exit within 5s **after SIGKILL**, give up"*.
* `acp.rs:2323-2329` `fn kill_process_group(pid)` → `killpg(Pid::from_raw(pid as i32), Signal::SIGKILL).is_ok()` at `:2328`.
* `impl Drop for AcpClient` `:2297-2312` — killpg(SIGKILL) then a **non-blocking** `try_wait()`; no 5 s wait.
* `grep -n "from_secs(5)"` → `:439` plus `:3222, :3241, :3271, :3414, :3867, :4567`; `#[cfg(test)] mod tests`
  opens at **`:2351`**, so **the only production `from_secs(5)` is the post-kill wait**.
* `grep -c SIGTERM` → **0**. `grep -c SIGKILL` → 8.

## The five sites the lane names — all now accurate

| site | text | verdict |
|---|---|---|
| `frame_tee.py:422-425` | "buzz-acp SIGKILLs the group (killpg) and then waits up to 5 s for it to exit (acp.rs:421-444, pinned 1c8321cd)" | **ACCURATE** |
| `frame_tee.py:429-432` | same, c2a side | **ACCURATE** |
| `test:862-864` | same + "SIGKILL cannot be handled … last RUNNING status (A21d). The SIGTERM path covers an operator/systemd TERM." | **ACCURATE** |
| `test:1028-1032` | same | **ACCURATE** |
| `test:1472-1476` | same | **ACCURATE** |
| (module docstring `frame_tee.py:16-25`) | "killpg(SIGKILL) on the whole process group and a bounded 5 s wait (acp.rs:421-444, :2323-2328, pinned 1c8321cd)" | **ACCURATE**; `:2323-2328` is exact |

Two residual nits inside those six, both LOW:
1. The citation `acp.rs:421-444` is off by one at the start — `:421` is the last line of the doc comment,
   `shutdown()` opens at `:422`. (B5f called this immaterial; it is still wrong on a line the lane retyped.)
2. "waits up to 5 s for **it** to exit", where "it" refers back to "the group": the source waits on
   `self.child.wait()` — the **direct child only**, not the group. The tee's grandchild is SIGKILLed by
   `killpg` but is not what the 5 s wait waits for. Exact wording: "…and then waits up to 5 s for the child
   to exit".

## The sixth site the lane did not fix — and it states the falsest claim of all

```
tests/test_s0_01_frame_tee.py:1517:            # R1: SIGTERM it (buzz-acp's shutdown responsibility).
```
`grep -c SIGTERM acp.rs@1c8321cd` = **0**. This is the original F-B5e-1 wording class ("that is buzz-acp's
shutdown responsibility") surviving in the file, and it **directly contradicts the module docstring the same
lane wrote** four lines from `frame_tee.py:22-23`: *"The SIGTERM path below covers an operator/systemd TERM,
**not buzz-acp**."* An exhaustive grep of both scope files for `shutdown responsibility|TERMs/KILLs|after 5
s|SIGTERM path covers it` returns exactly this one residue (plus the two lines of the F4 test that quote the
banned phrase on purpose). See **F-B5g-2**.

---

# ITEM 7 — REPORT DISCIPLINE

## 7a. F14 — the landing commit: **NOT MET**

Report header: *"Dispatched at `cf48eda`. Work landed in child commit on HEAD `1f32dc2d15e51c8ccf59a3a5421b5c2bf4810ba6`."*

* `cf48eda` **is** the dispatch commit (the brief + the VERIFY-B5f verdict + the AF-AP-59 screen row). ✔
* `1f32dc2` is **not** the landing commit. `git diff --stat 1f32dc2 0f2606d -- <both scope files>` →
  `2 files changed, 133 insertions(+), 62 deletions(-)`, and that diff is byte-identical to
  `4b43284..0f2606d`. `git show 1f32dc2:tests/test_s0_01_frame_tee.py` gives the **pre-B5g** file.
* The landing commit `0f2606d` appears nowhere in the report.

This is B5f's F14 repeated with a different wrong sha: a reader who follows the header lands on the tree
*before* the work. The sha256s in FILE IDENTITY are correct and are what saved the grade — but the sentence
is false as written. **F14 NOT MET.**

## 7b. `file:line` spot-checks — 48 refs, by `sed -n` on the PIN

**The DONE table is clean.** Every ref lands on the statement claimed: F6 `test:527/1100/2631` (the
`assert gc_pid_path.exists()` lines) and `test:540/1113/2644` (the `except ProcessLookupError:` lines);
F9 `test:2328/2335/2340`; F8 `test:503/510/515`, `:900/907/912`, `:1074/1081/1086` (all exact);
F13 `test:532-536/1105-1109/2636-2640`; F15 `test:560-561/1133-1134/2664-2665`; F11 `test:2798-2806`;
F12 `test:2808-2814`; F10 `test:2138` (`if sp.exists():`); F3 `frame_tee.py:423/430` and
`test:862/1029/1472`. Two ends are off by one (F4's block runs to `:2931` not `:2928`; F5's to `:2542` not
`:2541`) — trivial. **F7's DONE-table half is closed.**

**The MUTANT and PROBE tables are not.** Six of the eight pasted killer lines are wrong (item 2B): 2922 vs
**2919**, 2926 vs **2928**, 526 vs **525/1096/2625**, 2813 vs **2815**, 2541 vs **2542**, 2806 vs **2803**.
Every one of these is a line pytest prints for free; the two that are exact (2340, 515) are the two the lane
evidently copied. Same AF-AP-37 class as round 11, moved from one table to another.

## 7c. The AP-screen rulings — the block does not describe this lane's delta

The lane's gate block reads:
```
AP screen hits on this lane's delta:
  AP-1     tests/test_s0_01_frame_tee.py:469,1034,2529 -- FALSE POSITIVE: os.environ.get inside agent …
  AF-AP-40 tests/test_s0_01_frame_tee.py:527,1100,2631 -- FALSE POSITIVE: gc_pid_path.exists() is now …
  AF-AP-40 tests/test_s0_01_frame_tee.py:2138 -- FALSE POSITIVE: sp.exists() in the lag assertion's …
```
Reproduced by me, using the same `AP_SCREEN` the tool imports, over the **added** lines (which is all
`scripts/lint_delta.py:141-148` screens):

```
AP_SCREEN over the ADDED lines of 4b43284..0f2606d (== 1f32dc2..0f2606d, the lane's own base):
  0 hits
AP_SCREEN over the ADDED lines of 9b2803c..4b43284  (the PREVIOUS round's delta):
  AF-AP-40  tests/test_s0_01_frame_tee.py:527   if gc_pid_path.exists():
  AF-AP-40  tests/test_s0_01_frame_tee.py:1091  if gc_pid_path.exists():
  AF-AP-40  tests/test_s0_01_frame_tee.py:2120  if sp.exists():
  AF-AP-40  tests/test_s0_01_frame_tee.py:2594  if gc_pid_path.exists():
  AP-1      tests/test_s0_01_frame_tee.py:469   fd = os.environ.get("S0_01_FRAMEDIR", "")
  AP-1      tests/test_s0_01_frame_tee.py:1032  fd = os.environ.get("S0_01_FRAMEDIR", "")
  AP-1      tests/test_s0_01_frame_tee.py:2527  fd = os.environ.get("S0_01_FRAMEDIR", "")
  total 7
```
Three separate problems:
1. **This lane's delta produces zero AP-screen tells.** The `if …exists():` guards are gone (replaced by the
   F6 asserts); the `os.environ.get` lines were not touched this round. The block is B5f's screen output
   with the line numbers re-mapped to the B5g tree.
2. **lint_delta never prints line numbers** — its AP branch prints `f"  {ap_id:6s}{f}: {msg}"` over a joined
   blob of added lines. So the pasted per-line refs cannot have come from the tool; they were composed by
   hand. The lane brief's own rule: "Every number and every `file:line` in the report is PASTED from a tool
   run on the FINAL tree … never typed (F7, AF-AP-37)."
3. Ruling each hit REAL/FALSE-POSITIVE was a gate item. Substantively the rulings are fine (the three
   `if gc_pid_path.exists():` hits no longer exist because the lane fixed them, which is the *strongest*
   possible answer; `test:2138` is a genuine false positive — an absent status file is caught loudly by
   `test_initial_status_before_first_frame`, which I confirmed is present and passing). But the honest gate
   line is **"0 tells on the added lines"**, and the report should say so.

I did **not** re-run `scripts/lint_delta.py` end-to-end: the shared tree carries other lanes' uncommitted
edits, so `--base` would screen their lines too, and creating a clean worktree writes to the shared repo's
admin files. I reproduced the exact screen the tool applies, over the exact line set it applies it to.

## 7d. Other report claims, checked

| lane claim | my check |
|---|---|
| tee 473 lines / test 2931 lines / both sha256 | ✔ exact |
| "Before: 96 passed, 88 defs. After: 98 passed, 90 defs (8 parametrised extras)" | ✔ `98 tests collected`, `grep -c "    def test_"` = 90 |
| "idle 1: 98 passed in 170.08s / idle 2: 169.49s, pytest-exit 0" | ✔ reproduces (172.90 s / 170.13 s, rc 0) |
| "red state 9 failed, 89 passed in 170.93s" | ✔ reproduces (173.91 s), identical failure set |
| "pyflakes … rc 0" | ✔ |
| "post-suite census: live leaks: 0" | ✘ — see **F-B5g-9** (two of the lane's own processes are still alive) |
| "cost median 0.0642 s … within the noise band" | ✔ direction confirmed; my A/B is tighter (item 8) |
| DISCREPANCY "9 failed vs verifier's 8 failed — the delta is the new test" | ✔ exactly right |
| F3 red-before "genuine-red via F4 test (`source says 'SIGKILLs the group after 5 s'`)" | ✘ — on the parent the F4 test dies 3 assertions earlier at test:2918; COMMENT-TERM is the honest red-before (test:2928) |
| SELF-ATTACK #3 "FileNotFoundError is caught … the identity check is additive safety, not a new failure mode" | ✘ — the zombie path is a new failure mode (item 4b, 6/6) |

---

# ITEM 8 — COST

`vb11cost.py`'s 11-frame real-leg shape (3 c2a in, 8 a2c out, full spawn→exit wall clock), 15 reps × 3
batches, **the PIN tee and the true parent tee `736bb94` measured back-to-back in the same window** (sha256s
printed before the run: `2f0666c2b2a91a02` / `3fc846ceaf4b687b`).

```
LOAD-BEFORE 1.46 2.23 2.23                LOAD-AFTER 1.47 2.21 2.22
PIN    batch0 {"reps": 15, "median": 0.0557, "min": 0.0525, "max": 0.1572}
PARENT batch0 {"reps": 15, "median": 0.0578, "min": 0.0532, "max": 0.1612}
PIN    batch1 {"reps": 15, "median": 0.0622, "min": 0.0558, "max": 0.1617}
PARENT batch1 {"reps": 15, "median": 0.0583, "min": 0.0535, "max": 0.1663}
PIN    batch2 {"reps": 15, "median": 0.0570, "min": 0.0547, "max": 0.1592}
PARENT batch2 {"reps": 15, "median": 0.0591, "min": 0.0542, "max": 0.0682}
```
Per-batch PIN/PARENT ratio **0.96× / 1.07× / 0.96×**; median-of-medians PIN 0.0570 s vs PARENT 0.0583 s →
**0.98×**. Against the 0.058-0.060 s baseline: **0.95×-1.07×**. **No measurable cost from this lane's
changes**, which is the expected answer — the lane's only tee edit is two comment lines. The lane's
0.0642 s median sits inside the same band from a busier window; its "within the noise band" call is
**correct**, and my A/B against the parent in one window is the confirmation it did not make.

---

# ITEM 9 — INTERPRETERS AND HYGIENE

## 9a. 3.11 / 3.12 / 3.13

pytest is installed on **3.11 only** (`/usr/bin/python3.12 -c "import pytest"` and the 3.13 equivalent both
raise). As B5f did, I re-implemented the pins standalone and ran the tee's real SIGTERM behaviour directly.

**The pins (`vb12py.py`, every B5g assertion, against the PIN's bytes):**
```
3.11.15  F5_stray=[] F5b_stdin_in_lock=True errs=True | F11 pre_proc=1 all_None=True | F4 killpg=True
         cannot=True running=True neg1=True neg2=True | F12 pin_ok=True | next_after_install=Try
3.12.3   identical
3.13.12  identical
```

**The tee's real SIGTERM window (`vb12win.py`, no pytest, 6 reps per mode per interpreter):**
```
3.11.15  poll  n=6 rc={70: 6} status_present=6/6  write_errors=['terminated: SIGTERM'] final=False updated_seq=2
3.11.15  t0    n=6 rc={-15: 6} status_present=0/6
3.12.3   poll  n=6 rc={70: 6} status_present=6/6  (identical last-status object)
3.12.3   t0    n=6 rc={-15: 6} status_present=0/6
3.13.12  poll  n=6 rc={70: 6} status_present=6/6
3.13.12  t0    n=6 rc={-15: 6} status_present=0/6
```
The docstring's "the only uncovered SIGTERM window is Python interpreter startup before the handler install
(default disposition: rc −15, no status file)" reproduces **6/6 on all three interpreters**.
**Could not run:** the pytest suite on 3.12/3.13 (no pytest; no install attempted).

## 9b. The tripwire through the PIN's checker

The shared tree's `proofs/S0-01/check_acp_conformance.py` is A5i's live edit (sha256 `de13655acc86…`). I ran
the tripwire from my `git archive` venue, whose checker is the PIN's (`3edd8a2023c7…`):
```
test_sigterm_status_satisfies_check_tee_status   1 passed, 97 deselected in 0.20s
```
The test does reach the checker: `cc._load_timeline_raw(...)` at test:2352 and `cc.check_tee_status(...)` at
test:2354 — not a decorative import.

## 9c. Process census across two full suites

```
--- census PRE ---            (only the LANE's leaked pair, see F-B5g-9)   my live leaks: 0
=== IDLE SUITE RUN 1 ===      98 passed in 172.90s (0:02:52)
=== IDLE SUITE RUN 2 ===      98 passed in 170.13s (0:02:50)
--- census POST-RUN-2 ---     17999 ppid 1 Z [big_agent.py] <defunct>
                              18002 ppid 1 Z [agent.py]     <defunct>      my live leaks: 0
--- delayed census (+45 s) --- both zombies reaped; my live leaks: 0
df -h /  ->  /dev/vda 252G 30G 7.7G 80% /
```
**Zero live leaks from any of my runs**; the only survivors are reaped zombies. Also zero after the burner
suite, after the 15-mutant batches, and after the concurrency rounds (the PIDFILE-ABSENT mutants do leave
`sleep(120)` orphans by design; each self-exited within its own sleep and I signalled none of them).

## 9d. The three grandchild tests, 5 rounds × two concurrent pytest processes

No xdist in the sandbox; two separate venue copies (`vb12cA`, `vb12cB`) running the three affected tests
simultaneously, five rounds (10 worker runs):
```
LOAD-START 1.26 2.37 2.17
round1  A: 3 passed, 95 deselected in 63.88s   B: 63.78s
round2  A: 63.65s   B: 63.55s
round3  A: 63.55s   B: 63.59s
round4  A: 63.58s   B: 63.56s
round5  A: 63.55s   B: 63.57s
LOAD-END 3.18 2.71 2.36
post-run census of `time.sleep` / `frame_tee.py`: no survivors of mine
```
**10/10 green, zero cross-test interference, zero surviving sleepers.** Each worker kills only the pid it
recorded, so a sibling worker's grandchild is untouched. The AF-AP-59 fix behaves as designed under
concurrency — *for the code as it stands* (F-B5g-3 is about what the pin permits, not about this code).

One measured caveat on venue sensitivity: my `CENSUS-PGREP-TIGHT` escalation shows a world-scoped census
going red **inside a single serial suite** (`world census: 8920` — a sibling test's own sleeper caught
between two tests). So a reintroduced world census would not even need the PC's 8 workers to flake; the
serial suite is enough. That makes the weakness of the F12 pin more consequential, not less.

## 9e. pyflakes and shared-tree hygiene

```
pyflakes proofs/S0-01/tools/frame_tee.py tests/test_s0_01_frame_tee.py   -> rc 0
```
Every mutant ran on `git archive` copies under `…/scratchpad/vb12*`; both scope files re-hashed to
`2f0666c2b2a9…` / `b046bc24a6ee…` after **every** batch (the runner prints it and asserts it on restore); the
shared tree's two scope files were `git status --porcelain`-clean at every check and I never wrote to the
shared tree. The burner PIDs were killed by pid and verified gone; no `pkill` was used anywhere.

---

# ITEM 10 — THE DESIGN ITSELF (where I would have designed differently)

The brief's design is mostly right and the lane executed it. Seven places I would have written differently,
each with the measurement that says so.

**1. Design item 4 ("the doc-anchor pins MEANING") cannot be met by a token list, and asking for one
guaranteed the outcome.** Three literal substrings plus two blacklist regexes is a list of the mutations
already known; DOCSTRING-ORDER and DOCSTRING-WRONGEVENT survive `98 passed` (item 3a). What actually pins
meaning is an **oracle**, not a word list: vendor `crates/buzz-acp/src/acp.rs@1c8321cd` under the repo
(217 KB, and `upstream.lock.yaml` already pins the commit), and make the test assert the mechanical facts the
prose depends on — `SIGTERM` count == 0, `killpg(…, Signal::SIGKILL)` present, exactly one `from_secs(5)`
outside `#[cfg(test)]` and it lexically **after** the kill inside `shutdown()`. Then a docstring that says
"SIGTERM first" is contradicted by a committed artifact instead of by a list of forbidden phrases. That is
anti-hollow-green tactic 4 (an independent oracle) applied to prose.
*Cheaper interim:* put the canonical sentence in `proofs/S0-01/pins.py` as a constant and have every comment
and docstring cite it; then there is exactly one place that can be wrong and the pin is an equality, not an
absence.

**2. Design item 4's scope wording ("absent from the SOURCE, which also reads the comments and the three
test docstrings") is ambiguous, and the ambiguity landed in the shipped code as a false docstring.** The
implementation reads `Path(TEE)` only, so TESTDOC-TERM survives (`98 passed`), while the test's own docstring
claims the opposite. I would have written the design as two explicit assertions — one over
`Path(TEE).read_text()` and one over `Path(__file__).read_text()` — so there is nothing to interpret.

**3. Design item 7's F12 pin is the weakest available form, and a stronger one shipped in the dispatch
commit itself.** `cf48eda` added an AF-AP-59 row to `.claude/hooks/edit-snapshot.py` with a regex that
catches four of my six census spellings; the lane hand-typed two literals that catch none of them. The
design should have said *import `AP_SCREEN` and assert no row matches this file* (B5f already used that
import for its F10 work). And it should have said out loud that **no text pin can close the class** — the
`/proc` walk and `pgrep -x` variants evade any word list — so the durable fix is ownership-by-construction:
one `_kill_own_grandchild(framedir)` helper plus an AST pin that `os.kill` and every `subprocess.*` call in
the file occur only at named sites. Writing "CENSUS-WORLD must die" as the acceptance made an instance kill
look like a class closure.

**4. Design item 10's F13 semantic is inverted.** "Assert `/proc/<pid>/cmdline` contains `time.sleep`" makes
the *benign* outcome (our grandchild is already dead) a test failure whenever it is caught as a zombie
(measured 6/6, ~0.97 s window), while the direction it was written for — pid reuse — needs 728 pids/s here
against a measured 5 pids/s. I would have specified: cmdline mismatch on a **zombie** ⇒ already gone;
cmdline mismatch on a **live** process ⇒ hard failure ("refusing to kill a foreign pid"). Better still, drop
the heuristic: `os.pidfd_open(gc_pid)` while the grandchild is known alive, or spawn it into its own process
group and `killpg` the recorded pgid — reuse-proof by construction, no `/proc` parsing.

**5. Design item 9's F15 clause was written loosely and the lane satisfied the letter, not the case.** "Close
the pipes inside the `finally` before the own-pid assertion" — the closes went inside the `finally` but
*after* three assertions (one of them newly added by this same increment), so the case B5f named is still
open and the DONE table claims otherwise. The unambiguous instruction is structural: wrap the census in its
own `try: … finally: tee_proc.stdout.close(); tee_proc.stderr.close()`.

**6. The mutant clause ("the verifier's 40 re-run on the final tree") was a bookkeeping ask, and the lane
honestly declared it NOT_DONE.** Forty full re-runs is ~2 h of box time to re-confirm rows whose killers the
delta never touched. I would have scoped it to the rows the delta can move — the 8 targeted ones plus every
mutant whose killer was edited (the three value sites, the tripwire, the docstring test, the preinit pin, the
three `finally` blocks): ~18 rows, all of which I measured in about 25 minutes. Then the lane is not choosing
between an honest NOT_DONE and an unaffordable gate. (Having now measured all 48: the lane's structural
argument was **correct** — every one of the 27 previously killed-by-named rows is still killed, and two are
killed by *two* pins now. But "correct in hindsight" is not evidence, and the brief should not have made the
lane produce it.)

**7. The design's site inventory was hand-made and under-counted.** It named five wording sites; there are
six (`test:1517`). It named three census sites without noticing that at one of them the kill path is
unreachable (GRANDCHILD-UNKILLED survives graded on site 3 alone). Both enumerations should have come from a
grep/instrumented run pasted into the brief. This is the same discipline the brief imposes on the lane's
report, not imposed on the brief itself.

One design decision I would **keep** and would defend: the F5 dataflow pin *as an addition beside* the
existing `status_lock`/`os.replace` arm rather than a replacement. D3 dies only on the old arm and MIRROR-
SNAPSHOT only on the new one — dropping either would have created exactly the AF-AP-36 failure mode.

---

# FINDINGS

**F-B5g-1 [MED] SOLID — the F4 doc-anchor still pins a token set: two docstrings that satisfy every
assertion and misstate the pinned behaviour survive the whole suite. (Charged to the DESIGN, not the lane —
the lane met the acceptance it was given.)**
`tests/test_s0_01_frame_tee.py:2915-2931`.
*Observed vs expected:* expected a pin that catches a false statement of the shutdown bound. Observed:
**DOCSTRING-ORDER** ("buzz-acp sends SIGTERM to the group first and only escalates to `killpg(SIGKILL)` if
the group ignores it for 5 s … A wedged leg therefore gets a 5 s grace period") → `98 passed in 170.42s`.
**DOCSTRING-WRONGEVENT** ("the 5 s bound is on how long buzz-acp waits BEFORE the kill for the leg to
drain") → `98 passed in 169.34s`. Both contain `killpg`, `SIGKILL cannot be handled`, `last RUNNING status`;
neither trips either regex. `grep -c SIGTERM acp.rs@1c8321cd` = **0**, so the first is maximally false.
*Failing input:* either docstring above, verbatim.
*Minimal fix:* vendor `acp.rs@1c8321cd` under the repo and assert the mechanical facts the prose rests on
(SIGTERM count 0; `killpg(…, Signal::SIGKILL)` present; exactly one `from_secs(5)` outside `#[cfg(test)]`,
lexically after the kill in `shutdown()`), or collapse the prose to one constant in `proofs/S0-01/pins.py`
that every site cites and the test compares by equality.
*Exact red test to add:*
```python
def test_shutdown_prose_matches_the_pinned_source(self):
    rs = (ROOT / "vendor" / "buzz-acp" / "acp.rs").read_text()      # sha256-pinned in upstream.lock.yaml
    assert rs.count("SIGTERM") == 0
    doc = ast.get_docstring(ast.parse(Path(TEE).read_text()))
    assert "SIGTERM" not in doc.split("The SIGTERM path")[0], \
        "the docstring attributes a SIGTERM to buzz-acp; the pinned source sends none"
```
RED today on DOCSTRING-ORDER, GREEN on the PIN (verified by hand against the cached `acp.rs`; the vendored
path does not exist yet, so the test as written is a specification, not a run).
*Also charged here as a report claim:* the DONE table's "**F4** doc-anchor pins meaning" is refuted by the
two runs above.

**F-B5g-2 [BLOCKING] SOLID — a sixth committed artifact still states a claim the pinned source contradicts,
and it contradicts the module docstring this same lane wrote.**
`tests/test_s0_01_frame_tee.py:1517`.
*Observed vs expected:* the line reads `# R1: SIGTERM it (buzz-acp's shutdown responsibility).`
`grep -c SIGTERM` over `acp.rs@1c8321cd` (sha256 `44e82861…`) is **0**; `frame_tee.py:22-23` says *"The
SIGTERM path below covers an operator/systemd TERM, **not buzz-acp**."* This is the original F-B5e-1 wording
class ("that is buzz-acp's shutdown responsibility") that F3 was opened to remove, still in the file. The
lane fixed five sites and missed this one; the F4 regex cannot see it (wrong phrase, wrong file).
*Failing input:* `grep -n "shutdown responsibility" tests/test_s0_01_frame_tee.py` → `1517`.
*Minimal fix:* `# R1: SIGTERM it (an operator/systemd TERM; buzz-acp SIGKILLs the group instead).`
*Exact red test to add:* extend the F4 pin to the test file with the phrase that is actually false —
```python
tsrc = Path(__file__).read_text()
assert not re.search(r"buzz-acp'?s?[\s#]+shutdown[\s#]+responsibility", tsrc), \
    "buzz-acp sends no SIGTERM (acp.rs@1c8321cd: 0 occurrences)"
```
**RUN:** RED on the PIN today at `test:1517`; GREEN after the one-line reword. (I ran the regex over the PIN's
bytes: 1 match.)

**F-B5g-3 [MED] SOLID — the F12 pin closes one spelling of the AF-AP-59 class, not the class; the repo
already ships a stronger signature. (Charged to the DESIGN.)**
`tests/test_s0_01_frame_tee.py:2808-2816`; `.claude/hooks/edit-snapshot.py` AF-AP-59 row.
*Observed vs expected:* six world-scoped censuses reintroduced into the three `finally` blocks, one per
mutant, each graded against the pin alone: `ps -eo pid,args`+filter, `pgrep -x`, `pgrep -a -f`,
`os.listdir("/proc")`, `subprocess.run(["pgrep","-f",…])` (the banned call with two spaces removed), and
`subprocess.run(['pkill', …])` (single quotes) — **all six PASS**. B5f's exact spelling dies, as claimed.
Two of the six survivors are literal `pgrep -f`.
*Failing input:* delete one space — `subprocess.run(["pgrep","-f","import time; time.sleep"] …)`.
*Minimal fix (now):* import the registry's own signature instead of hand-typing literals —
```python
import importlib.util
spec = importlib.util.spec_from_file_location("es", ROOT / ".claude/hooks/edit-snapshot.py")
es = importlib.util.module_from_spec(spec); spec.loader.exec_module(es)
src = Path(__file__).read_text()
bad = [ap for ap, rx, _ in es.AP_SCREEN if ap == "AF-AP-59" and rx.search(src)]
assert not bad, "a world-scoped process sweep is back in the test file (AF-AP-59)"
```
That catches CENSUS-WORLD, -PGREP-TIGHT, -PGREP-A and -PS-E. *Minimal fix (durable):* ownership-by-
construction — a single `_kill_own_grandchild(framedir)` helper plus an AST pin that `os.kill` and every
`subprocess.*` call in the file occur only at named sites. **The class cannot be closed by text**:
`CENSUS-PGREP-X` and `CENSUS-PROC-WALK` evade every word list, and so would `shell=True` or `psutil`.
*Exact red test to add:* the AP_SCREEN import above — **RUN:** PIN PASS, CENSUS-PGREP-TIGHT RED (I verified
the regex `["']pgrep["']\s*,\s*["']-f["']` matches that mutant's source and not the PIN's).

**F-B5g-4 [MED] SOLID (mechanism), NOT REACHABLE today (measured) — the F13 identity assert fails the test on
the benign outcome: a zombie grandchild has an existing `/proc/<pid>` and an EMPTY cmdline.**
`tests/test_s0_01_frame_tee.py:533-538`, `:1106-1111`, `:2637-2642`.
*Observed vs expected:* `except FileNotFoundError: gc_pid = None` treats only the fully-reaped case as "gone".
Measured (`vb12zombie.py`, the fixture shape, 6 reps): after the grandchild exits, `/proc/<pid>/cmdline` reads
back empty for **≈ 0.97 s** before `/proc/<pid>` disappears, and `"time.sleep" in cmdline` is False
throughout — `F13_ASSERT_WOULD_FIRE=True` **6/6**. The message a reader would get is
`pid N is not the grandchild (cmdline: )`.
*Reachability, measured:* site 1 and site 2 hold a **live** grandchild at census (instrumented run:
`F13-BRANCH present … state=S … match=True`). Site 3's grandchild dies at **30.5 s** (idle) / **30.6-30.8 s**
(4 burners) against a census fixed at the 45 s loop deadline — a **14.2-14.5 s margin** to a 0.97 s window.
Not reachable on this box; it is a timing margin, not a structural guarantee.
*Pid reuse (the direction the design named) is unreachable, with arithmetic:* `pid_max` = 32768; measured
allocation rate under load `14682 → 15608 over 180 s` = **5.1 pids/s**; reuse at site 3 needs ≈ 32768 pids in
the 45 s since allocation = **728 pids/s**, 140× the measured rate. Sites 1-2 cannot reuse at all (live).
*Minimal fix:* treat a cmdline mismatch on a **zombie** as already-gone and reserve the hard failure for a
**live** foreign process (code in item 4b); or remove the heuristic with `os.pidfd_open` / a per-grandchild
process group.
*Exact red test to add:* a fourth fixture whose grandchild exits ~0.3 s before the census — RED on the PIN
today, GREEN under the corrected form.
*Also charged here as a report claim:* SELF-ATTACK #3 says the identity check "is additive safety, not a new
failure mode". It is a new failure mode; the mitigation it names (`FileNotFoundError` caught) does not cover
the zombie, and a `PermissionError` on a restricted procfs is not caught at all (it propagates past
`except ProcessLookupError`).

**F-B5g-5 [BLOCKING] SOLID — the "AP screen hits on this lane's delta" gate block does not describe this
lane's delta, and its line numbers cannot have come from the tool.**
`tasks/briefs/s0-01-b5g-support/B5g-report.md` § GATE LINES; `scripts/lint_delta.py:140-150`.
*Observed vs expected:* the report lists 7 hits with per-line refs. Reproduced with the same `AP_SCREEN` the
tool imports, over the added lines it screens: **the B5g delta (`4b43284..0f2606d`, byte-identical to
`1f32dc2..0f2606d`, the lane's own base) yields 0 hits.** The 7 listed hits are the **previous** round's
(`9b2803c..4b43284`: AP-1 at 469/1032/2527, AF-AP-40 at 527/1091/2120/2594), re-mapped to B5g line numbers.
And `lint_delta` prints `f"  {ap_id:6s}{f}: {msg}"` — **no line numbers at all** — so the refs were composed
by hand, against the lane brief's own rule ("Every number and every `file:line` … PASTED … never typed").
*Failing input:* `python3 scripts/lint_delta.py --base 1f32dc2` on a tree holding only the B5g change.
*Minimal fix:* paste the tool's real output. The honest line is `anti-pattern screen: no tells on the added
lines` — which is the strongest possible result, because the three `if gc_pid_path.exists():` guards that
produced last round's AF-AP-40 hits are the ones this lane removed.
*Exact red test to add:* none (report artifact).

**F-B5g-6 [BLOCKING] SOLID — F14 is not met: the header names a commit that does not contain the work, for
the second round running.**
`tasks/briefs/s0-01-b5g-support/B5g-report.md:3`.
*Observed vs expected:* "Work landed in child commit on HEAD `1f32dc2d15e51c8ccf59a3a5421b5c2bf4810ba6`".
`git diff --stat 1f32dc2 0f2606d -- <both scope files>` → `2 files changed, 133 insertions(+), 62
deletions(-)`; `git show 1f32dc2:tests/test_s0_01_frame_tee.py` is the pre-B5g file. The landing commit
`0f2606d` is named nowhere in the report. B5f's F14 asked for exactly this and the design repeated it
("the header names the dispatch commit AND the landing commit").
*Failing input:* `git show 1f32dc2:proofs/S0-01/tools/frame_tee.py | sha256sum` → not `2f0666c2…`.
*Minimal fix:* "Dispatched at `cf48eda`; work landed in `0f2606d` (parent `4e6cc03`)."

**F-B5g-7 [BLOCKING] SOLID — F15 was not implemented as designed, and the DONE table's claim for it is
false.**
`tests/test_s0_01_frame_tee.py:560-561`, `:1133-1134`, `:2664-2665`.
*Observed vs expected:* the design said "close the pipes inside the `finally` **before the own-pid
assertion**". The closes are inside the `finally` but **after** `assert gc_pid_path.exists()` (line 527), the
F13 identity assert (line 535) and `assert gone` (line 559) — and this increment *added* the first two, so
there are now three assertion paths in front of the closes where there was one. The DONE table row reads
"(structural: ensures pipe close even on assertion failure)": under PIDFILE-ABSENT, which I ran, the
assertion at `test:525` fires and `tee_proc.stdout.close()` / `stderr.close()` never execute.
*Failing input:* the PIDFILE-ABSENT run above — `3 failed`, and no pipe close on any of the three.
*Minimal fix:* an inner `try/finally` around the census —
```python
finally:
    if tee_proc.poll() is None:
        tee_proc.kill(); tee_proc.wait(timeout=5)
    try:
        ...          # the whole census, asserts included
    finally:
        tee_proc.stdout.close(); tee_proc.stderr.close()
```
*Exact red test to add:* none needed — PIDFILE-ABSENT is already the demonstrator; the fix is verified by
re-running it and checking the fds are closed (`/proc/<pytest-pid>/fd` no longer holds the tee pipes).

**F-B5g-8 [LOW] SOLID — at site 3 the own-pid kill and its assertion are unreachable; two of the three sites
carry the whole kill-path coverage.**
`tests/test_s0_01_frame_tee.py:2637-2664`.
*Observed vs expected:* instrumented run of all three F13 checks:
`F13-BRANCH already-gone pid=13750 (kill and 'assert gone' SKIPPED)` at
`test_concurrent_main_thread_status_vs_pump`, while sites 1 and 2 report `present … match=True`. Consequence,
measured: **GRANDCHILD-UNKILLED graded on site 3 alone SURVIVES** (`1 passed, 97 deselected in 45.35s`); it
dies on sites 1-2.
*Failing input:* `-k test_concurrent_main_thread_status_vs_pump` with the `os.kill` line deleted.
*Minimal fix:* either lengthen site 3's grandchild past the 45 s deadline (`range(6000)`) so the kill path is
exercised there too, or state in the DONE table that site 3 contributes the pid-file assertion only.

**F-B5g-9 [BLOCKING] SOLID — "post-suite census: live leaks: 0" is false: two of the lane's own processes
have been wedged since 18:48, in a mutual pipe deadlock, and were still alive at the end of my grade.**
`tasks/briefs/s0-01-b5g-support/B5g-report.md` § PROBE TABLE / GATE LINES.
*Observed vs expected:* every census I took (5 of them, over ~2 h) shows
```
17819 17818 S  5845  python3 -m pytest tests/test_s0_01_frame_tee.py -k "test_grandchild_keeps_tee_alive or …"
17907 17819 Sl 5486  /usr/local/bin/python3 …/scratchpad/b5gmut/proofs/S0-01/tools/frame_tee.py
```
`b5gmut` is the lane's own mutant venue (its shell line, still visible in `ps`, is the PIDFILE-ABSENT run and
its restore `cp`). Mechanism, from primary evidence and re-derived by me:
* `/proc/17819/wchan` = `anon_pipe_read`, `Threads: 1` — the test process is blocked reading a pipe.
* `/proc/17819/fd/12 -> pipe:[309720]` — it **still holds the write end of the tee's stdin**.
* `/proc/17907/fd/0 -> pipe:[309720]`; thread `17909` wchan = `anon_pipe_read` — the tee's c2a reader is
  blocked on that same pipe; thread `17907` wchan = `hrtimer_nanosleep` — the main thread is inside a
  `while ti.is_alive(): time.sleep(0.1)` drain loop.
* `/proc/17907/fd/3` points at `…/pytest-634/test_concurrent_main_thread_st0/frames/timeline.jsonl` — site 3.
* The tee has no children and no `time.sleep` process survives, so the a2c side already reached EOF.
That is a closed cycle: the tee waits forever for stdin EOF; the test waits forever on the tee's output.
The lane's censuses evidently scoped to its own suite's descendants and missed it.
*Failing input:* not reproduced — 10 concurrent runs, 2 idle suites, 1 burner suite and ~12 escalation
suites of the same three tests produced **zero** hangs for me. **This is one observed instance with a
directly evidenced mechanism, not a measured rate.**
*Minimal fix (report):* re-run the census and paste the truth; reap the pair (it is the lane's to kill — **I
did not signal it**, per my brief).
*Minimal fix (code, and worth a follow-up regardless of this lane):* the deadlock is only possible because
the test holds the tee's stdin open while blocking on its stdout. Close `tee_proc.stdin` before any blocking
read, or read with a deadline. **F-B5g-7's inner `finally` does not fix this** — the block is upstream of
the `finally`.

**F-B5g-10 [LOW] SOLID — the F4 test's own docstring misstates its scope.**
`tests/test_s0_01_frame_tee.py:2911-2912`: *"and the whole source file (comments + test docstrings included)
never claims…"*. It reads `src = Path(TEE).read_text()` — `frame_tee.py` only. Measured: **TESTDOC-TERM**
(one test docstring reverted to "SIGKILLs the group after 5 s") → `98 passed in 169.44s`. A wording pin whose
own wording is wrong, inside the increment titled "wording that matches the pinned source".
*Minimal fix:* either add `assert not re.search(<same regex>, Path(__file__).read_text())`, or change the
docstring to "…and the tee source (comments included)".

**F-B5g-11 [LOW] SOLID — two residual inaccuracies inside the six corrected wording sites.**
`frame_tee.py:20`, `:424`, `:431`; `tests/test_s0_01_frame_tee.py:863`, `:1029`, `:1473`.
(a) the citation `acp.rs:421-444` is off by one — `shutdown()` opens at `:422`; `:421` is a doc-comment line.
(b) "waits up to 5 s for **it** to exit", antecedent "the group": the source waits on `self.child.wait()`,
the **direct child** only. *Fix:* "…and then waits up to 5 s for the child to exit (`acp.rs:422-444`…)".

**F-B5g-12 [LOW] SOLID — six of the eight mutant-table killer lines are wrong; the F3 red-before is
misattributed.**
Report § MUTANT TABLE / DONE TABLE. Measured: 2922→**2919**, 2926→**2928**, 526→**525/1096/2625**,
2813→**2815**, 2541→**2542**, 2806→**2803**. And the F3 row's red-before ("genuine-red via F4 test, `source
says 'SIGKILLs the group after 5 s'`") cannot happen on the parent — the F4 test dies three assertions
earlier at `test:2918`; the honest red-before is COMMENT-TERM (`test:2928`, measured). Same AF-AP-37 class as
round 11's F7, relocated from the DONE table to the MUTANT table. *Fix:* paste the pytest tails.

**F-B5g-13 [INFO] SOLID — premise shift during my grade; grade unaffected.**
HEAD moved `0f2606d` → `9da1041` → `77546be` → `73efb9f` → `24e0961` and the working tree went clean while I
measured. `git diff --stat 0f2606d HEAD -- <both scope files>` is **EMPTY** and the worktree copies still
hash `2f0666c2…` / `b046bc24…`. I graded the PIN's bytes throughout and never wrote to the shared tree.

**F-B5g-14 [INFO] — carry-forwards from round 11, unchanged and not in this lane's scope.**
B5f's F16 (the 12-trial lag assertion's two silent-skip paths at `test:2138` / `:2145`), F18
(`os.makedirs` at `frame_tee.py:120` still inside the uncovered pre-install window, with the docstring still
attributing the whole window to interpreter startup), and F-B5e-18 (SIGTERM against a wedged pump, still
unreproduced by anyone). None were in the B5g design. **F-B5g-9 is arguably the first sighting of the
F-B5e-18 class in the wild** — a tee that cannot be terminated because both ends are blocked on each other.

---

# WHAT I REPRODUCED vs REVIEWED STATICALLY vs DELIBERATELY SKIPPED

**Reproduced (my own runs this session, on `git archive 0f2606d` copies; load stated at every timing claim):**
the PIN full suite ×2 idle (`98 passed` 172.90 s / 170.13 s) plus 9 more full suites inside mutant
escalations; the full no-`-x` red state on the true parent `736bb94` (`9 failed, 89 passed in 173.91s`);
individual parent runs of all 8 deterministic changed tests plus 5 reps each of the two timing-sensitive
rows; **57 distinct mutants** (B5f's 40 re-anchored on the B5g bytes + my 17) over ~90 runner pytest
invocations, with 10 full-suite escalations; the four premise-assert loop-only controls plus the
regression-class control; the whole suite under 4 CPU burners (`98 passed in 179.75s`, load 5.74); 10
concurrent-process runs of the three grandchild tests; the process census across two idle suites plus a
delayed census; the zombie/empty-cmdline probe (6/6) and the site-3 grandchild lifetime idle and loaded
(3+3); an instrumented run showing which F13 branch each of the three sites takes; the pid-allocation rate
under load; the cost probe 3×15 reps on **both** the PIN and the parent tee in one window; the AST/text pins
and the tee's real SIGTERM behaviour on 3.11 **and** 3.12 **and** 3.13; the AP_SCREEN over both deltas; 48
`file:line` refs by `sed -n`; the pinned `acp.rs` ranges, the `from_secs(5)` census, the `Drop` path and the
`SIGTERM` count read from the sha256-verified file.

**Reviewed statically only:**
* The claim that `acp.rs::shutdown()` is a production path (B5f verified ≥20 call sites in `lib.rs` and
  `pool.rs` over the network). I hold only `acp.rs`, in which the sole `.shutdown()` is at `:3093`, inside
  `#[cfg(test)] mod tests` (opens `:2351`). **Inherited from B5f, not re-derived by me.**
* F-B5g-7's fd consequence (that the pipes stay open after an assertion in the `finally`) — Python control
  flow, argued from the code, not instrumented.
* The exact source of the lane's DOCSTRING-HYBRID and COMMENT-TERM mutants: the report does not publish them,
  so I graded B5f's implementations. My kill lines (2919 / 2928) differ from the lane's (2922 / 2926); the
  rows are correct in verdict and unverifiable in detail.

**Deliberately skipped, with reason:**
* **The PC leg** (`scripts/pc_suite.sh`, 8 xdist workers). No BRIDGE READY banner and my brief forbids the
  bridge. Two findings are venue-sensitive and would read differently there: **F-B5g-3** (a world-scoped
  census is far more likely to go red under 8 workers) and **F-B5g-4** (the pid-allocation rate, hence the
  reuse arithmetic). `sysctl kernel.pid_max` on the PC: **NOT run** — the coordinator's runbook
  (`PC-BRIDGE.md`, `docs/OBSERVABILITY-RUNBOOK.md`) records no value for it, so I have no PC figure to cite.
  **This is a sandbox-only, single-worker grade.**
* **A network re-fetch of `acp.rs@1c8321cd`.** My non-negotiables forbid network beyond localhost. I used the
  session cache under a sha256-identity chain and say so at the top of item 6.
* **`pytest -n 4`** — xdist not installed; substituted two concurrent pytest processes × 5 rounds.
* **The pytest suite on 3.12 / 3.13** — pytest is not installed for either; no install attempted. The pins
  and the tee's real SIGTERM behaviour ran there standalone instead.
* **Any mutant that signals a pid it did not spawn.** B5f's `CENSUS-WORLD` SIGKILLs every
  `import time; time.sleep` process on the box, and two other lanes are live here. I graded it text-only
  (which is all the F12 pin looks at) and made my six variants enumerate-only.
* **Killing the lane's wedged pair (17819 / 17907).** Not my processes; my brief says PID-targeted kills of
  processes I started only. They are still running.
* **Forcing pid reuse** — it would need ~32768 pids on a box shared with two live lanes; the arithmetic
  above answers the question without it.
* **A restricted-procfs fixture** for the `PermissionError` half of F-B5g-4 — no way to restrict `/proc` for
  one process here without touching the box.

---

# VERDICT

# NOT-READY

**This increment closes almost everything round 11 opened, and the closures are real.** Measured by me on the
PIN: the seven real survivors of round 11 are down to **one accepted rename mirror** — DOCSTRING-HYBRID,
COMMENT-TERM, PIDFILE-ABSENT, CENSUS-WORLD, MIRROR-SNAPSHOT and MIRROR-PREINIT all die by a named test;
PIDFILE-ABSENT dies at **all three sites individually** (3.38 s / 15.36 s / 45.34 s); the loop-only premise
mutation is red at **all four** flag sites plus the contention site, and the real regression fires them too;
the red state on the true parent reproduces **exactly** (`9 failed, 89 passed`, same nine names); the suite is
green twice idle, green under 4 CPU burners with **zero** flakes, and 10/10 green under two concurrent
processes with no cross-test interference and no leaks of mine; the pins are byte-identical on 3.11, 3.12 and
3.13, and the tee's SIGTERM behaviour is 6/6 identical on all three; and there is **no cost** (PIN 0.0570 s
vs parent 0.0583 s, measured back-to-back in one window). The five wording sites the design named are now
accurate against the pinned source, re-derived by me.

It is NOT-READY on five items. Four are cheap; one is a one-line code fix of the increment's own class.

**Blocking set**

1. **F-B5g-2 — a sixth artifact still contradicts the pinned source.**
   `tests/test_s0_01_frame_tee.py:1517` reads `# R1: SIGTERM it (buzz-acp's shutdown responsibility).`
   `grep -c SIGTERM acp.rs@1c8321cd` = 0, and `frame_tee.py:22-23` says the opposite. This is F-B5e-1's own
   class, alive in the increment whose subject line is "wording that matches the pinned source". One line,
   plus the one-line regex that keeps it fixed.
2. **F-B5g-5 — the AP-screen gate block describes the previous round's delta.** This lane's delta yields
   **0** tells (reproduced with the tool's own `AP_SCREEN` over the lines it screens), and `lint_delta` emits
   no line numbers at all, so the seven pasted per-line refs were composed by hand — against the brief's
   explicit "PASTED … never typed". The true result is the strongest possible one and should simply be
   pasted.
3. **F-B5g-6 — F14 still not met.** The header names `1f32dc2` as the landing commit; that tree does not
   contain the work (133 insertions away). Second round running, after a finding that asked for exactly this.
4. **F-B5g-7 — F15 shipped as the letter, not the case, and the DONE table claims otherwise.** The pipe
   closes went inside the `finally` but behind three assertions, two of them added by this increment; under
   PIDFILE-ABSENT (which I ran) they do not execute. "Ensures pipe close even on assertion failure" is false.
5. **F-B5g-9 — "post-suite census: live leaks: 0" is false.** Two of the lane's own processes (a pytest of
   the three grandchild tests in `b5gmut` and its `frame_tee.py` child) have been wedged since 18:48 in a
   mutual pipe deadlock — evidenced by both wchans, the shared pipe inodes in both fd tables, and the site-3
   framedir on the tee's fd 3. I did not signal them.

**Should ship with the blockers (each measured, none blocking on its own):** F-B5g-1 (the F4 pin still takes
a token set — two false docstrings survive `98 passed`; charged to the design), F-B5g-3 (the F12 pin closes
one spelling of six; the repo's own AF-AP-59 regex closes four of them for one import), F-B5g-4 (the F13
assert fails on the benign zombie outcome; not reachable today, 14 s margin, but the semantic is inverted),
F-B5g-10 (the F4 test's docstring misstates its own scope), F-B5g-11 (citation off by one; "waits for the
group" should be "waits for the child"), F-B5g-12 (six wrong mutant-table lines and a misattributed F3
red-before), F-B5g-8 (site 3's kill path is unreachable — GRANDCHILD-UNKILLED survives when graded there).

**Recorded, not charged:** F-B5g-13 (premise shift, grade unaffected), F-B5g-14 (round-11 carry-forwards
outside this design).

**This verdict's dependence on things I did not reproduce.** None of the five blockers rests on an
unreproduced claim: each has a pasted run or a primary-source read above, and every fix I propose that could
be run, I ran. Two qualifications belong in the verdict line itself: **(a)** F-B5g-9 is **one observed
instance** with a directly evidenced mechanism — I did **not** reproduce the hang in ~25 runs of the same
tests, so it is charged as a false evidence claim (the census) plus a diagnosed hazard, not as a measured
flake rate; **(b)** the single claim I inherited rather than re-derived is that `acp.rs::shutdown()` is
reached from production (`lib.rs`/`pool.rs`), which needs a file I do not hold — if that were false, F3's
whole wording exercise would be moot, but nothing in my findings turns on it.

**Venue.** Sandbox only, single worker, 4 cores, `pid_max` 32768. **The PC leg was NOT run by me** — no
bridge, and my brief forbids it. F-B5g-3 and F-B5g-4 would both read differently under `pytest -n 8` on the
PC and I say so in each finding.

**Shared-tree hygiene.** Every mutant ran on `git archive` copies under `…/scratchpad/vb12*`; both scope
files re-hashed to `2f0666c2b2a9…` / `b046bc24a6ee…` after every batch (asserted by the runner on each
restore); the shared tree's two scope files were `git status --porcelain`-clean at every check and I never
wrote to the shared tree. The four CPU burners I started were killed by pid and verified gone; no `pkill`
was used; another lane's wedged processes were left alone.
