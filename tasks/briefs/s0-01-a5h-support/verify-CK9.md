# VERIFY-CK9 — adversarial grade of checker lane A5g (round 9)

## PREMISE — PASS with one drift

`git rev-parse HEAD` = `f42fe7f39b0d2a8a16fecc1ed97719bf6ff07148`, `= origin/claude/soundbox-kit-migration-iz1jwf`.
`git log --oneline -3`: `f42fe7f transcripts: scrubbed sandbox chat digests` / `0df17d6 S0-01 WIP checkpoint 8m: …(lane A5g)…` / `4a54a8b ledger: …`.
`git status --porcelain` at dispatch: EMPTY (clean).
`df -h /` before the first batch: `/dev/vda 252G 24G 14G 65% /`.
Work tree: `git archive HEAD | tar -x` into `/tmp/.../scratchpad/vck9/repo` (+ `repo2` for the parallel lane). No git command other than
`rev-parse`/`log`/`status`/`show` was run against `/home/user/agent-factory`; nothing was edited, restored, stashed or checked out there.

DRIFT: the brief names `proofs/S0-01/check_acp_conformance.py` sha256 `4a11b2d6…` as "at HEAD". `4a11b2d6d198d1a3…` is the file at the
PARENT commit `4a54a8b`. At HEAD it is `cc80f7b7cc83b50fe18f9f73dbbcdaf768f7ee1c1e0792b866b0e1e2e94636d1`. Graded against HEAD.
Lane-report PIN drift: `A5g-report.md` says `PIN: e84b7ef1…` — that commit is not in this branch's last 3; the landed commit is `0df17d6`.

Shared-tree drift DURING my run (read-only observation): origin/HEAD advanced to `9fe6691`
("wiki: live-state…"). `git diff --stat f42fe7f..9fe6691` = `wiki/topics/live-state.md | 4 ++--` only; all six scope files are
byte-identical at `9fe6691` and at my PIN (sha compared per file). Working tree dirty with the B5e/N5g lanes' files, untouched by me.

## ITEM R1 — the A21d shape table (38 shapes, executed against HEAD's `check_tee_status`)

Harness: `scratchpad/vck9/teerun/a21d_table.py`. Timeline = 6 alternating frames, seq 1..6 (c2a 3 / a2c 3 / last_seq 6).

### B5d-legal RUNNING shapes — all 10 ACCEPTED
exact snapshot · `drained=false` · `stdin_reader_done=false` · `write_errors=["terminated: SIGTERM"]` ·
fwd_c2a deficit 1 · fwd_a2c deficit 1 · fwd deficit 1 in BOTH directions ·
rec_c2a trails 1 with updated_seq−1 · rec_a2c trails 1 with updated_seq−1 · rec trails 1 AND fwd deficit 1.

### Out-of-bound RUNNING siblings — all 17 REJECTED, exact reason
| shape | exact reason |
|---|---|
| seq lag 2 (both dirs trail 1) | `run-1: tee-status.json running snapshot updated_seq 4 trails timeline last seq 6 by more than one` |
| fwd_c2a deficit 2 | `… running snapshot forwarded_c2a 1 trails recorded_c2a 3 by more than one` |
| fwd_a2c deficit 2 | `… running snapshot forwarded_a2c 1 trails recorded_a2c 3 by more than one` |
| forwarded AHEAD of recorded | `… running snapshot forwarded_c2a 4 trails recorded_c2a 3 by more than one` |
| `["terminated: SIGKILL"]` | `… write_errors has unexpected entries: ['terminated: SIGKILL']` |
| SIGTERM + a second entry | `… write_errors has unexpected entries: ['terminated: SIGTERM', 'disk full']` |
| rec_c2a AHEAD of timeline by 1 | `… running snapshot updated_seq 7 trails timeline last seq 6 by more than one` |
| rec_c2a trails 2 | `… running snapshot updated_seq 4 trails timeline last seq 6 by more than one` |
| seq-sum violated | `… running snapshot recorded deficits 0+0 do not sum to updated_seq lag 1` |
| deficit direction-sum mismatch (c2a−1, a2c+1) | `… running snapshot recorded_a2c 4 trails timeline a2c count 3 by more than one` |
| `drained` not a bool | `… drained is not a bool` |
| `stdin_reader_done` not a bool | `… stdin_reader_done is not a bool` |
| recorded is `True` (bool, not int) | `… c2a recorded/forwarded is not int` |
| `updated_seq` float | `… updated_seq is not int` |
| `agent_returncode` set while running | `… not final but agent_returncode is not null` |
| `exit_code` set while running | `… not final but exit_code is not null` |
| `final` = 0 | `… final is not a bool` |

### FINAL shapes — 2 accepted, 9 rejected
accept: exact final; signal exit (rc −15 → exit 143).
reject: SIGTERM entry on FINAL → `write_errors is not empty` · drained=false → `drained is not true` ·
stdin_reader_done=false → `stdin_reader_done is not true when final` · fwd_c2a deficit 1 → `forwarded_c2a != recorded_c2a` ·
fwd_a2c deficit 1 → `forwarded_a2c != recorded_a2c` · rec_c2a trails 1 → `recorded_c2a 2 != timeline c2a count 3` ·
updated_seq lag 1 → `updated_seq 5 != timeline last seq 6` · rc null → `final but agent_returncode is not int` ·
raw negative exit → `exit_code -15 != expected 143`.

**Item-4 answer: ZERO checker lines reject a B5d-shaped status, running or final.** The A21d semantics are correct.

## ITEM R1 — the REAL tee, both statuses, through the rewritten checker

`scratchpad/vck9/teerun/run_real_tee.py` runs the committed `proofs/S0-01/tools/frame_tee.py` (at my PIN) twice.

| run | tee rc | actual status (verbatim keys) | `check_tee_status` |
|---|---|---|---|
| SIGTERM | 70 | `{"agent_returncode":null,"drained":true,"exit_code":null,"final":false,"forwarded_a2c":1,"forwarded_c2a":1,"recorded_a2c":1,"recorded_c2a":1,"stdin_reader_done":false,"updated_seq":2,"updated_utc":"…","write_errors":["terminated: SIGTERM"]}` | **ACCEPTED** |
| clean exit (client EOF) | 0 | `{"agent_returncode":0,"drained":true,"exit_code":0,"final":true,"forwarded_a2c":1,"forwarded_c2a":1,"recorded_a2c":1,"recorded_c2a":1,"stdin_reader_done":true,"updated_seq":2,"updated_utc":"…","write_errors":[]}` | **ACCEPTED** |

Timeline parsed with `cc._load_timeline_raw` in both cases (2 entries, c2a 1 / a2c 1, last_seq 2).
Parent checker (`4a54a8b`, sha `4a11b2d6…`, isolated in `scratchpad/vck9/parentpkg/`) on the SAME two live statuses:
`PARENT SIGTERM: REJECTED -> Failure: run-1: tee-status.json write_errors is not empty` · `PARENT CLEAN: ACCEPTED`.
`tests/test_s0_01_frame_tee.py::TestSigtermStatusVsChecker::test_sigterm_status_satisfies_check_tee_status` at HEAD: `1 passed`;
no `xfail` marker remains anywhere in that file; it imports the real `check_acp_conformance` and calls
`cc.check_tee_status(framedir, "run-1", cc._load_timeline_raw(framedir, "run-1"))`.

## ITEM R3 — the 20 `in out` survivors, one verdict each

`grep -c` at HEAD over `tests/test_s0_01_check_acp_conformance.py`: `in out` **20** · `in result` **9** · `startswith(` **14** · ` or ` **26**.
(All 26 ` or ` hits are inside literal expected strings or an assert *message* — zero disjunctive reason assertions. That target IS met.)

Column "computable?" = could the test have asserted the FULL reason string from values it already holds?

| # | T: | test | asserted | full reason available to the test | computable? |
|---|---|---|---|---|---|
| 1 | 734 | `test_del_neg_fixture` | `"negative:"` + `"neg-malformed-initialize.json absent"` | `failure_reason: negative: negative: fixtures/neg-malformed-initialize.json absent` | YES — no dynamic value at all |
| 2 | 1947 | `test_neg_nan_timeline` | `"negative:"` + `"not strict JSON"` | `…: timeline.jsonl line 1 is not strict JSON: <JSONDecodeError text>` | PARTLY — the tail is a CPython message; the **line number** is deterministic and is not asserted |
| 3 | 1961 | `test_neg_c2a_not_seq1` | `"negative:"` + `"seq 1 is not a c2a frame"` | `failure_reason: negative: negative: seq 1 is not a c2a frame` | YES — no dynamic value |
| 4 | 1972 | `test_neg_classify_wrong` | `"negative:"` + `"initialize params != fixture"` | `failure_reason: negative: negative: initialize params != fixture` | YES — no dynamic value |
| 5 | 2004 | `test_sequence_guard_skip_one_leg` | `"check sequence mismatch"` | `failure_reason: golden: check sequence mismatch - first missing: check_manifests:cancel` | YES — no dynamic value (T:3831 already asserts this shape exactly) |
| 6 | 2128 | `test_audit_p1_generic_child_survives_teardown` | `"survived teardown"` | `failure_reason: run-1: process 54321 (/usr/bin/sleep 60) survived teardown` | YES — pid and cmd are the test's own literals |
| 7 | 2170 | `test_symlink_upstream_record` | `"symlink in evidence tree"` | `failure_reason: golden: symlink in evidence tree: run-1/upstream-records/999999.json` | YES — link name is the test's literal |
| 8 | 2181 | `test_symlink_manifest_gz` | same | `failure_reason: golden: symlink in evidence tree: run-1/manifest-evil.txt.gz` | YES |
| 9 | 2228 | `test_neg_foreign_id_response_before_real` | `"99999"` + `"does not match"` | `failure_reason: negative: negative: agent response id 99999 does not match the request id at seq 2` | YES — id and seq are the test's own |
| 10 | 2336 | `test_tee_status_forwarded_lt_recorded` | `"trails recorded_c2a"` + `"by more than one"` | `…running snapshot forwarded_c2a {r-2} trails recorded_c2a {r} by more than one`, `r = ts["recorded_c2a"]` | YES — the test holds `r` |
| 11 | 2350 | `test_tee_status_recorded_ne_timeline` | **`"tee-status.json"`** | `…running snapshot recorded_c2a {c+5} trails timeline c2a count {c} by more than one` | YES — **weakest assertion in the file: this substring matches all ~25 tee-status reasons**; the docstring itself says "…or the updated_seq consistency check", i.e. the author did not know which rule fires |
| 12 | 2414 | `test_shutdown_owned_pid_survives` | `"survived shutdown"` | `failure_reason: shutdown: process 12300 (/usr/bin/sleep 60) survived shutdown` | YES — the test's own literals |
| 13 | 3079 | `test_ck7_f8b…` | `"trails recorded_a2c"` + `"by more than one"` | computable from `ts["recorded_a2c"]` | YES |
| 14 | 3094 | `test_ck7_f8c…` | `"recorded_c2a"` + `"trails timeline c2a count"` | computable from `real_c2a` (already a local) | YES |
| 15 | 3694 | `test_ck8_startup_missing_keys` | `"startup-line missing keys"` | `failure_reason: run-1: startup-line missing keys: ['context_limit', 'heartbeat', 'max_turns_per_session', 'meh', 'memory', 'model', 'presence', 'subscribe', 'typing']` (computed by me) | YES — but `_EXPECTED_STARTUP_KEYS` is a **function-local** at C:1049, so the test must hardcode the 21 keys; hoist it to module scope |
| 16 | 3725 | `test_ck8_post_body_union_shape_rejected` | `"body key set mismatch"` | `failure_reason: run-1: upstream POST record stream body key set mismatch: ['response_format', 'temperature']` | YES |
| 17 | 3803 | `test_ck8_f42_wrong_startup_pin` | `startup_key in out` | `failure_reason: {leg}: startup {k} is '{real}', expected '{wrong}'` | YES — all four values are parametrize inputs |
| 18 | 3804 | same | `wrong_val in out` | same | YES |
| 19 | 3936 | `test_ck8_running_forwarded_deficit_2_rejected` | `"trails recorded_c2a"` + `"by more than one"` | computable | YES |
| 20 | 3956 | `test_ck8_running_seq_sum_invariant` | `"do not sum to updated_seq lag"` | `…running snapshot recorded deficits 0+0 do not sum to updated_seq lag 1` | YES |

**19 of 20 are fully computable; #2 is computable except for an interpreter-generated tail.** Eight of them (#1, 3, 4, 5, 7, 8, 9, 15)
carry no dynamic value whatsoever. The lane's not-done reason ("20 `in out` survivors carry dynamic values (deficit amounts, pid
numbers, window bounds)") is **not accurate**: no `in out` survivor asserts a window bound, and every pid/deficit in the list is a
literal or a local the test already holds — the same `cmd[:40]` technique the lane applied to four other tests (`test_teardown_has_tee`
T:1609, `test_proc_closure` T:1577, `test_orphan_pair` T:1622, `test_pc_launch_exemption` T:1636, all now exact) closes all twenty.

`startswith(` survivors (14): 3 are legitimate PASS-line/header shape checks (T:514, 522, 2690); T:2037 (`malformed evidence:` +
exception repr) is legitimately a prefix; T:1106 (`mention owner created_at … outside window`) is the ONE case whose tail is a
derived window bound. The other 9 (T:822, 1255, 1272, 1283, 1293, 1458, 1900, 2027, 2055) are exactly computable.
`in result` survivors (9): 4 are PASS-line shape (T:523, 524, 526, 2061), 1 is skip-reason logic (T:2773); T:2401
(`"updated_seq" in result`) is weak AND its comment names the wrong rule (see R9-CK-F9).

## ITEM R2 — pins (PASS)

- `grep -rn "_PINS_PENDING" proofs/ tests/` → 2 hits, both **comments** (`pins.py:126`, `check_acp_conformance.py:1099`). The dict is gone.
- `proofs/S0-01/pins.py` is **byte-identical at the parent `4a54a8b` and at HEAD** — all 16 `PINNED_STARTUP_*` were already landed by the
  coordinator; A5g's change is consumption only. (The report's "14 `PINNED_STARTUP_*` imports added" undercounts: C:71-86 imports **16**.)
- Literal sweep of the checker for the pinned startup values (`"bypassPermissions"`, `"Queue"`, `"Mentions"`, `"Steer"`,
  `"(agent default)"`, `"allowlist(1)"`, `"owner-only"`): **one** hit — `C:477 if rt != "owner-only":`, and that is `check_env`'s
  `BUZZ_ACP_RESPOND_TO`, a different surface (see R9-CK-F12). The startup-line side is 100% pins.
- All **21** startup keys are constrained: 19 value-pinned in the `checks` dict (C:1100-1116), `respond_to` via `expected_rt`
  (C:1120-1121), `pubkey` format-only (C:1096-1098). `required_keys = _EXPECTED_STARTUP_KEYS` (C:1055) is the full 21 set — CK8-F6's
  "there is a required set of 11 inside a 21-key allowed set … 10 of 21 keys have unconstrained values" is **CLOSED**.
- `test_ck8_startup_values_come_from_pins` monkeypatches `PINNED_STARTUP_PERMISSION_MODE` and asserts the EXACT reason quoting the
  patched value. Genuine consumption proof — for **one** pin (see R9-CK-F13).
- Parenthesised value carrying `=` rejected: C:1077-1078, exact test at T:3696-3705. Duplicate key: C:1088-1089. Unknown key: C:1086-1087.
  Unparsable token: C:1064-1065 (a key with a `-` fails `(\w+)=` and is rejected fail-closed — probed by hand).

## ITEM R4/R5/R6

**R4 (A25 omission at the dispatcher) — PASS.** `test_ck8_f38_check_sequence_omission` (T:3810-3832) monkeypatches `cc._run_check`
itself and asserts `out == "failure_reason: golden: check sequence mismatch - first missing: check_env:run-2"` — exact, and it is the
dispatcher, not the check. Note the guard's fallback branch (C:1738) is a MEMBERSHIP scan, so a pure **re-ordering** of the sequence
falls through to `check sequence mismatch (63 vs 63 expected)` — still a Failure, but the "first missing" wording never applies.

**R5 (seven dead presence gates) — 1 of 7 done; the ruling is NOT met.**
Deleted: the AF-AP-40 `mentions_dir.is_dir()` branch in `check_two_users`. I re-derived the deadness proof independently:
`check_mentions` calls `_require_dir(leg_dir/"mentions", …)` at **C:494** and runs for EVERY leg in the first loop of
`EXPECTED_CHECK_SEQUENCE`, before `check_two_users`; the live-path test `test_twousers_mentions_dir_absent` (T:2261-2269) asserts the
exact `failure_reason: two-users: mentions/ absent`. Deletion accepted.
The other six were neither deleted nor given a killing test, and the lane offered no proof for any of them. My own re-derivation:

| gate (CK7 ref → HEAD) | predicate | earlier assertion on the same path | verdict |
|---|---|---|---|
| `C:890` → **C:931** | `first_term is not None` | C:904-906 requires `stopReason == "end_turn"` for every prompt response | DEAD (re-derived) |
| `C:898` → **C:938** | `len(new_seqs)>=2 and len(term_seqs)>=1` | C:888 (`len(news)!=2` → Failure) + C:904-906 | DEAD (re-derived) |
| `C:1327` → **C:1519** | `init_resp_idx is not None and session_new_idx is not None` | `session_new_idx` forced by C:1506; `init_resp_idx` NOT re-derived | **UNSURE** |
| `C:1340` → **C:1532** | `new_resp_idx is not None and prompt_idx is not None` | C:725-726 (`session/new has no sessionId response`) + C:1506 | DEAD (re-derived) |
| `C:1367` → **C:1559** | `sid1 is not None and sid2 is not None` | C:725-726 runs for run-1 AND run-2 | DEAD (re-derived) |
| `C:1373` → **C:1565** | `r1m.exists() and r2m.exists()` | `check_mentions` requires `owner.event.json` for run-1/run-2 (`pins.EXPECTED_MENTIONS`) and runs first | DEAD (re-derived) |

**R6 (real-leg tee-status) — PASS.** `test_ck8_real_leg_tee_status` is parametrised over all 5 legs and skips today with the exact
ruled reason. Verbatim from `base2` (`-rs`): `tee-status.json absent in run-1 (corpus predates the tee status)` and the same for
run-2 / cancel / shutdown / two-users. The hostile variant `test_ck8_tee_status_hostile_bundle` uses the synthetic `bundle` fixture,
never skips, and asserts the exact `failure_reason: run-1: tee-status.json write_errors has unexpected entries: ['some random error']`.
`proofs/S0-01/evidence/golden/run-1/` in the sandbox has 16 files and **no `timeline.jsonl` and no `tee-status.json`** — the skip
reason is honest.

## ITEM R8 — CK8's F1-F10 as ruled

| CK8 id | ruled outcome | what is at HEAD | my verdict |
|---|---|---|---|
| F1 owned-set shape / buzz-pid binding | exact reasons + delete-mutants die | C:1192-1193 + C:1200-1201; `test_ck8_owned_set_empty` / `test_ck8_owned_missing_buzz_pid`, both exact (`shutdown: owned-pids.json owned is empty or not a list` / `… does not contain buzz-acp.pid 12300`) | see mutant table (F13a-OFF / F13b-OFF) |
| F2 FIFO + timeout | walk extended to the fixtures dir, in-process cap, exit 70 documented, default 90 s, non-int → 64 | walk C:1629-1645 covers `golden/` AND `_fixtures()`; `_check_with_timeout` C:1581-1593; `check_bundle(timeout_s=90)` C:1596; module docstring lists 0/1/2/64/70; `main()` default 90 (C:1751) | **PARTIAL — two holes, R9-CK-F1 and R9-CK-F2** |
| F3 F14 per leg × two pids | 5 legs × {tee_pid, agent_child_pid} | `test_ck8_f14_rid_pid_not_in_owned`, 10 params, exact reason each; guards C:1209-1212 run before the shutdown branch | see mutant table (F14-SKIP-CANCEL) |
| F4 two A20a structural rules re-gated | both | `test_ck8_f4_no_agent_parented_by_tee` reaches C:1274-1275; `test_ck8_f4_no_tee_parented_by_buzz` does **not** reach C:1272-1273 | **HALF-CLOSED — R9-CK-F4** |
| F5 F43 source scan + self-test | scan extended, "self-test … so the scan itself is proven non-hollow" | scan extended to `open(w/a/+)`, `Path.open`, `json.dump`, `shutil.copy*`, `os.replace`, ALL module-level fns + class methods | **scan extended, self-test HOLLOW — R9-CK-F3** |
| F6 allowed vs required keys | required = full 21 | `required_keys = _EXPECTED_STARTUP_KEYS` (21) | CLOSED |
| F7 GET fingerprint `is None` | null is the only accepted value | C:617-619; fixture GET now carries `null` (T:308-312) so BOTH arms run in the sandbox; `test_ck8_get_fingerprint_non_null_rejected` + `test_ck7_f24_get_fingerprint_bogus`, both exact | CLOSED |
| F8 per-shape POST key sets + role sequences | both | C:621-639; `test_ck7_f22`/`f23`, `test_ck8_post_body_union_shape_rejected`, `test_ck8_nonstream_roles_wrong` | key sets CLOSED; **role ORDER untested — see ROLES-SET mutant** (`_POST_ROLES_STREAM == _POST_ROLES_NONSTREAM == ["system","user"]`, so the "per-shape role sequence" split carries no information) |
| F9 teardown duplicate | same rule on both scans | C:1222-1225 (after) + C:1326-1329 (teardown); `test_ck7_f30_after_scan_duplicate_pid` + `test_ck8_teardown_scan_duplicate_pid`, both exact | CLOSED |
| F10 F34 test RUNS the tee | subprocess | `test_ck8_f34_frame_tee_subprocess_keys` spawns `P/"tools"/"frame_tee.py"`, 2 frames, SIGTERM, asserts `tuple(ts.keys()) == PINNED_TEE_STATUS_KEYS`; AST instrument kept as `test_ck7_f34_frame_tee_keys_match_pin_ast` | CLOSED |

CLI domain probed by hand (`--timeout-s`): `abc` → 64 `usage: --timeout-s requires an integer` · `1e3` → 64 · ` 7 ` → accepted ·
**`0` → accepted, cap OFF** · **`-5` → accepted, cap OFF**. `proofs/S0-01/spec.json` invokes the checker with no `--timeout-s`
(`["python3","proofs/S0-01/check_acp_conformance.py","proofs/S0-01/evidence"]`, `timeout_s: 120`), so the default 90 s applies there.

## ITEM 6 — the coordinator's `pc_post.sh` hunk (PASS, with a named false-positive hazard)

Parser tolerance: `line.split(None, 4)` over `ps -eww -o pid,ppid,etimes,stat,args --no-headers` yields exactly 5 fields; stat flags
(`Ssl+`, `I<`, `SLl`) contain no whitespace and land in `parts[3]`; `args` keeps its spaces in `parts[4]`. Live probe on this box:
89 rows, minimum field count 5, **zero** rows with fewer (kernel threads emit `[kthreadd]`), so the fail-loud `sys.exit` at
`pc_post.sh:39` is not spuriously reachable. `-eww` removes the 80-column clip (`test_scan_rows_are_not_clipped_at_80_columns`).

Helper filter (`pc_post.sh:70`): an OWNED row is never dropped — reproduced,
`tests/test_s0_01_pc_post_scan.py::test_owned_row_is_never_dropped_by_the_helper_filter` passes.
A FOREIGN row that names a pinned path AND matches `pc_post.sh`/` ps -e` **is** dropped from the body while still counted in the
header's `pinned_present` (which is computed over the full live table, `pc_post.sh:73-74`). I executed the consumer side directly on a
synthetic leg:

```
pinned_present=3 (consistent)                                   -> ACCEPT
pinned_present=4 (foreign pinned-naming helper dropped from body) -> REJECT
   run-1: process-scan-after.txt header pinned_present=4 inconsistent with body (3)
```

**Answer to the brief's question:** the checker's process-evidence rule needs BOTH the owned rows and the FULL pinned population —
`body_owned` vs header `owned_present` (C:1228-1230) and `body_pinned` vs header `pinned_present` (C:1234-1238) are both consumed.
So the drop is **fail-closed and loud**, not a hole: a legitimate concurrent capture whose helper names a pinned path REDS the leg.
That is a false-positive availability hazard on the PC, not a hollow green.
Separately: the header's 8th field `owned_zombies` is required by `_SCAN_HEADER_RE` (C:145) and consumed by **nothing** (R9-CK-F11).

## ITEM 3 — F43 hardlink fixture and the contamination hunt

- `-n 2` is **impossible here**: pytest-xdist is not installed in `/root/venv-agent-factory` (`ModuleNotFoundError: No module named
  'xdist'`). Stated as NOT run, with the reason, rather than skipped silently.
- Two serial full runs of the three files, both green and identical (`315 passed, 10 skipped`), basetemp 126 M each — no
  cross-test contamination observed in serial mode.
- Write-path grep over the test file: the F43 scan itself performs exactly the grep the brief asks for, and it passes on the pristine
  file, i.e. **no** `.write_text` / `.write_bytes` / `open(w|a|+)` / `json.dump` / `shutil.copy*` / `os.replace` call sits in a
  non-exempt module-level function or class method. Every test-side bundle mutation goes through `_rewrite` (T:477-486, unlinks first).
- The `_EXEMPT_FNS` set (T:3256-3261) is the remaining exposure. Of the eleven exempt writer helpers only `_write_timeline` and
  `_write_tee_status` unlink before writing; `_write_runtime_identity`, `_write_env`, `_write_startup_and_log`, `_write_model`,
  `_write_manifests`, `_write_mentions`, `_write_upstream_records`, `_write_process_scan`, `_write_negative` do **not**. I grepped for
  test-side callers of those nine (excluding the session fixture at T:416-455): **zero**. So CK8's mechanism is still latent, not live.
- **New exposure I found:** the `bundle` fixture hardlinks the TRACKED tools directory, not a session-scoped copy —
  `T:467-468 dest_tools = tmp_path/"tools"; shutil.copytree(P/"tools", dest_tools, copy_function=os.link)` — and the checker reads
  `HERE/"tools"/"frame_tee.py"` (C:401) with `HERE` monkeypatched to `tmp_path`. An in-place write to `tmp_path/tools/<file>` would
  corrupt a **tracked source file**, not just the session bundle. No test writes there today (grep for `"tools"` in the test file:
  T:33, 160, 396, 467, 468, 3462, 3488 — all reads or the fixture itself), and the (hollow) scan would not catch a future one.
- The scan's self-test does not guard the scan — proven, see R9-CK-F3.

## ITEM 7 — counts and hygiene

```
base1  (plain pytest, 3 files, -p no:randomly, --basetemp)   315 passed, 10 skipped in 897.08s (0:14:57)   basetemp 126M
base2  (bash scripts/test_summary.sh <3 files>)
       pytest-exit: 0
       pytest-summary: 315 passed, 10 skipped in 916.09s (0:15:16)                                          basetemp 126M
```
Collection: `test_s0_01_check_acp_conformance.py` 314 + `test_s0_01_audit_cp5_controls.py` 3 + `test_s0_01_pc_post_scan.py` 8 = 325 =
315 passed + 10 skipped. Both runs identical in outcome (determinism pair). The box was contended throughout (other lanes' pytest
processes; load average 2.1-6.3) — durations are upper bounds.
`python -m pyflakes` over `check_acp_conformance.py`, `pins.py`, the three lane test files, `test_s0_01_frame_tee.py` and
`tools/frame_tee.py`: **rc=0, no output.**
Skip reasons: 4 × `real leg predates scan v2.3 (no enumeration header)` (T:2691) · 1 × `real v2.2 sample: probe_sha256 mismatch
(capture predates current probe)` (T:2775) · 5 × `tee-status.json absent in <leg> (corpus predates the tee status)` (T:3845).
Line deltas re-derived (`git show 4a54a8b:<f> | wc -l` vs `f42fe7f`): checker 1694→1790 (+96, report correct);
`test_s0_01_check_acp_conformance.py` 3370→**3956 (+586)** — the report says 3952/+582; `test_s0_01_frame_tee.py` 2056→2058 (+2, correct);
`pins.py` 156→156 (unchanged).
Report `file:line` refs re-derived: "`check_mentions` C:494 `_require_dir`" — correct at HEAD (C:494 is
`mentions_dir = _require_dir(leg_dir / "mentions", leg, "mentions/")`).

## HOSTILE-INPUT SWEEP on `check_tee_status` (fail-closed, one asymmetry)

14 numeric attacks (`NaN`, `Infinity`, `-Infinity`, `1e400` on `recorded_*`, `forwarded_*`, `updated_seq`, `agent_returncode`) across
both arms: **14/14 REJECTED** with a named reason. `tee-status.json` = `[]` → `is not an object`; empty file → `JSONDecodeError`,
which `main()` turns into `failure_reason: malformed evidence: JSONDecodeError: …` rc 1. No NaN wormhole.

Asymmetry found (executed): the RUNNING arm enforces `_is_strict_int` on the counters and `updated_seq` (C:1407, C:1413); the FINAL
arm does not, so float counters pass it.
```
FINAL   recorded_c2a=3.0 forwarded_c2a=3.0 -> ACCEPT
FINAL   updated_seq=6.0                    -> ACCEPT
RUNNING recorded_c2a=3.0 forwarded_c2a=3.0 -> REJECT  c2a recorded/forwarded is not int
RUNNING updated_seq=6.0                    -> REJECT  updated_seq is not int
```

## FINDINGS

Line refs are `C:` = `proofs/S0-01/check_acp_conformance.py`, `T:` = `tests/test_s0_01_check_acp_conformance.py`, on my copy
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vck9/repo/...` — byte-identical to
`/home/user/agent-factory/...` at PIN `f42fe7f` (and at the current origin tip `9fe6691`).

### R9-CK-F1 — SOLID — **BLOCKING** — a non-positive `--timeout-s` silently disables the wall-clock cap
`C:1765` `timeout_s = int(args[idx + 1])` has no positivity floor; `C:1599` gates only on `is not None`; `C:1588`
`_signal.alarm(timeout_s)` — CPython accepts `alarm(0)` and `alarm(-N)` and both CANCEL any pending alarm.
Reproduced (`_check_with_timeout(t, sleep-3s-fn)`): `t=1` → `SystemExit(70)` after 1.0 s; **`t=0` → returned after 3.0 s, cap did not
fire**; **`t=-1` → same**. End-to-end with a hostile tree (below): `--timeout-s 3` → `failure_reason: checker timed out after 3s` rc 70;
`--timeout-s 0` and `--timeout-s -1` → still running at the 20 s external kill (rc 124).
This is precisely the class CLAUDE.md's tactic 1 names ("numeric guards reject the WHOLE unusable class … positivity on the FINAL
value"), applied to the guard CK8-F2 was raised to install. `spec.json` never passes the flag, so the proof runner is not exposed;
any operator invocation is.
**Red test to add:**
```python
def test_ck9_timeout_arg_non_positive_rejected():
    for bad in ("0", "-1"):
        r = subprocess.run([sys.executable, str(CHECKER), "--timeout-s", bad, "/tmp/x"],
                           capture_output=True, text=True, timeout=10)
        assert r.returncode == 64, bad
        assert r.stderr.strip() == "usage: --timeout-s must be a positive integer"
```
**Fix:** after `int()`, `if timeout_s <= 0: print("usage: --timeout-s must be a positive integer", file=sys.stderr); return 64`, and in
`check_bundle` gate on `timeout_s is not None and timeout_s > 0` (or assert `> 0`).

### R9-CK-F2 — SOLID — **BLOCKING** — the non-regular-entry walk runs AFTER the checker's first read, so a FIFO on a read path is never named
`C:1613 identities = json.loads(identities_path.read_text())` executes at the top of `_check_bundle_uncapped`; the structural walk that
rejects non-regular entries is at `C:1629-1645`, sixteen lines later. `_require_file` (`C:182-185`) tests `path.exists()`, which is TRUE
for a FIFO. Reproduced end-to-end with `mkfifo <fixtures>/identities.json` and a minimal evidence tree:
```
default cap (90 s): blocked past a 12 s external kill (rc 124)
--timeout-s 3     : failure_reason: checker timed out after 3s     rc 70
--timeout-s 0 / -1: still blocked at the 20 s external kill (rc 124)   [with F1]
```
So under the default the checker burns the full 90 s and reports `checker timed out after 90s` instead of
`fixtures: non-regular entry in evidence tree: identities.json` — the exact vector CK8's item-1d table already showed
("HEAD checker, FIFO in the --fixtures-dir instead of under golden/ … checker timed out after 6s"). The lane's
`test_ck8_fifo_in_fixtures_dir_rejected` (T:3584-3591) places an EXTRA `evil.fifo`, which the walk does catch, so the regression test
does not cover the reported vector.
**Red test to add:**
```python
def test_ck9_fifo_at_identities_json_is_named_not_timed_out(bundle):
    fx = bundle.parent / "fixtures"
    (fx / "identities.json").unlink(); os.mkfifo(fx / "identities.json")
    start = time.monotonic()
    rc, out = _check(bundle)                     # _check passes timeout_s=None: must NOT block
    assert time.monotonic() - start < 5
    assert rc == 1
    assert out == "failure_reason: fixtures: non-regular entry in evidence tree: identities.json"
```
**Fix:** hoist the two walk loops (`C:1629-1645`) above the `identities.json` read, or make `_require_file` reject anything that is not
`S_ISREG` before returning.

### R9-CK-F3 — SOLID — **BLOCKING** — the F43 source-scan's self-test does not exercise the scan (R8-CK-F5 is not closed at the class)
`T:3237-3342`. The real scan walks the AST and appends to `violations`; the "self-test" at `T:3320-3342` builds a SECOND, inline matcher
over a separate source string and asserts `len(self_violations) >= 3`. The two share only the `_WRITE_MODES` / `_SHUTIL_WRITERS` name
bindings, no code path. Reproduced, three runs of `-k f43_no_direct`, all with a REAL in-place violation
(`(bundle / "golden" / "run-1" / "argv.txt").write_text(...)`) injected into the non-exempt `test_ck8_owned_set_empty`:
```
(a) pristine scan + violation                                  -> 1 failed   (control is red)
(b) _WRITE_ATTRS = set()            + violation                -> 1 passed   (SURVIVES)
(c) real scan short-circuited (`if True: continue` at T:3278) + violation -> 1 passed   (SURVIVES)
```
The docstring's claim "Self-tests with a deliberately-violating source string so the scan itself is proven non-hollow" (T:3240-3241)
is therefore false.
**Red test / fix:** extract the collector — `def _scan_direct_writes(src: str) -> list[str]` at module scope — have the real assertion
call it on `inspect.getfile(...)` and have the self-test call **the same function** on a violating source string that includes
`p.write_text(x)` and `p.write_bytes(x)`, asserting the returned categories cover all six patterns.

### R9-CK-F4 — SOLID — **BLOCKING** — the A20a rule "no tee process parented by buzz-acp" still has no test
`C:1272-1273`. `grep -rn "no tee process parented by buzz-acp" tests/` returns **0 assertion hits** — the only hit is the docstring of
`test_ck8_f4_no_tee_parented_by_buzz` (T:3640), which then asserts
`out == "failure_reason: run-1: recomputed owned closure != owned-pids.json"` (T:3650) — the closure rule at `C:1259`, not the A20a rule
the test is named for. R8-CK-F4 asked for BOTH A20a rules to be re-gated; only `no agent process parented by a tee process`
(`C:1274-1275`, `test_ck8_f4_no_agent_parented_by_tee`) actually is.
**Red test to add** (owned closure intact, so `C:1259` cannot fire first):
```python
def test_ck9_no_tee_parented_by_buzz(bundle):
    sp = bundle / "golden" / "run-1" / "process-scan-after.txt"
    _rewrite(sp, _scan_header("after", pinned_present=2) + "\n"
             + f"12300 1 100 {PINNED_BUZZ_ACP_EXE_REALPATH} --r\n"
             + "12340 12300 90 /usr/bin/python3 /tmp/not-the-tee.py\n"
             + f"12345 12340 80 /usr/bin/python3 {PINNED_AGENT_REALPATH}\n")
    rc, out = _check(bundle)
    assert rc == 1
    assert out == "failure_reason: run-1: no tee process parented by buzz-acp"
```

### R9-CK-F6 — SOLID — R5 is met for 1 of 7 gates; six survive with no proof and no test
See the R5 table above. Five of the six are dead by my own re-derivation (`C:931`, `C:938`, `C:1532`, `C:1559`, `C:1565`); `C:1519` I
could not settle. The ruling required, per gate, either deletion backed by a delete-mutant + raise-instrument proof, or retention with
a killing test. Neither exists for any of the six, and the lane's report row is titled "R5 F40/F41" as if both were addressed.
**Fix:** delete the five re-derived-dead conjuncts (leaving the real comparison), and for `C:1519` either re-derive `init_resp_idx`'s
presence from `check_initialize_frames` or add a hostile golden whose a2c initialize response carries no `protocolVersion` and assert
the exact reason.

### R9-CK-F7 — SOLID — R3's exact-reason conversion is not "blocked by dynamic values"; 20 of 20 are computable
See the R3 table. Eight of the twenty carry no dynamic value at all. The four conversions the lane DID do
(`test_teardown_has_tee` T:1609, `test_proc_closure` T:1577, `test_orphan_pair` T:1622, `test_pc_launch_exemption` T:1636) use exactly
the f-string technique that closes the other sixteen. The report's not-done reason ("carry dynamic values (deficit amounts, pid
numbers, window bounds)") names a window bound that no `in out` survivor asserts.

### R9-CK-F8 — SOLID — the weakest assertion in the suite
`T:2350` `assert "tee-status.json" in out` — matches every one of the ~25 reasons `check_tee_status` can print, and its own docstring
(`T:2340-2341`) hedges "fails on the running arm's recorded deficit check **or** the updated_seq consistency check". The mutation this
test performs (`recorded_c2a += 5`, `forwarded_c2a` follows) deterministically hits `C:1422-1424`.
**Fix:** `assert out == f"failure_reason: run-1: tee-status.json running snapshot recorded_c2a {real+5} trails timeline c2a count {real} by more than one"`.

### R9-CK-F9 — SOLID — stale comment falsified by the A21d rewrite
`T:2402` `# updated_seq 99999 is way ahead of the timeline, so updated_seq != rec_c2a + rec_a2c fires`. With the RUNNING arm in place
the rule that fires first is `C:1416-1418` (`lag not in (0,1)`), not `C:1431`. Reproduced in the shape table: an updated_seq ahead of
the timeline yields `running snapshot updated_seq 7 trails timeline last seq 6 by more than one`. The assertion
`assert "updated_seq" in result` (T:2401) matches either, so the comment was never falsified by a test.

### R9-CK-F10 — SOLID — a vacuous control, and the report describes it wrongly
`T:2284` `with pytest.raises((FileNotFoundError, cc.Failure)):`. That disjunction passes whether or not the R5 gate exists — it cannot
distinguish "gate deleted" from "gate present", so it is not a control for the deletion. The A5g report says the test was "updated to
`pytest.raises(FileNotFoundError)`" (singular) — the committed code is the tuple.
**Fix:** `with pytest.raises(FileNotFoundError):` (the live-path coverage is already exact at `T:2269`).

### R9-CK-F11 — SOLID — a scan-header field that nothing consumes
`_SCAN_HEADER_RE` (`C:143-145`) requires `owned_zombies=(\d+)` (group 8). `grep -n "group(8)\|owned_zombies"` over the checker: the
regex line only. `owned_present`, `owned`, `pinned_present`, `buzz_acp_pid`, `buzz_present` and `rows` all have consistency rules;
`owned_zombies` has none — the producer's zombie classification (`pc_post.sh:41-45`, which removes those rows from `rows`, from
`table_pids` and therefore from `owned_present`) is accepted unchecked.
**Fix or decision:** either add `int(hdr.group(8)) + int(hdr.group(6)) <= int(hdr.group(5))` plus a killing test, or drop the field
from the header shape. Today it is evidence nobody grades.

### R9-CK-F12 — SOLID — the same pinned value is a literal on the env surface
`C:472` `if rt != "allowlist":` and `C:477` `if rt != "owner-only":` in `check_env`, while `check_config_echo` reads the same semantic
value from `PINNED_STARTUP_RESPOND_TO` / `PINNED_STARTUP_RESPOND_TO_TWO_USERS`. A pin change would move one surface and not the other.

### R9-CK-F13 — SOLID — R2's "one wrong-value bundle per key" is met for 4 of 19 keys
`test_ck8_f42_wrong_startup_pin` (T:3765-3805) is parametrised over `mcp_cmd`, `permission_mode`, `respond_to`,
`respond_to (two-users)` — four of the nineteen value-pinned keys — and asserts two substrings, not the exact reason.
`test_ck8_startup_values_come_from_pins` monkeypatches exactly one pin (`PINNED_STARTUP_PERMISSION_MODE`). Fifteen pinned keys
(`relay, agent_cmd, idle_timeout, max_turn, agents, heartbeat, subscribe, dedup, session_policy, meh, ignore_self, context_limit,
max_turns_per_session, presence, typing, memory, model` minus the ones covered) have no wrong-value bundle.
**Fix:** parametrise over the `checks` dict itself so the test count follows the pin count, and assert
`out == f"failure_reason: {leg}: startup {k} is {wrong!r}, expected {pin!r}"`.

### R9-CK-F14 — SOLID — a not-done reason that is false
The A5g report's Not-done table says `test_s0_01_pc_post_scan.py (3rd lane file) | Not in the sandbox run; requires the PC.`
Run here: `pytest tests/test_s0_01_pc_post_scan.py tests/test_s0_01_audit_cp5_controls.py -q` → **`11 passed in 1.71s`**, basetemp 260 K.
The file needs no PC; it spawns local `python -c "time.sleep(120)"` processes and shells `pc_post.sh scan`.

### R9-CK-F15 — SOLID — a typed test count in the report (AF-AP-37 class)
Report Files table: `tests/test_s0_01_check_acp_conformance.py | 3370 | 3952 | +582`. Measured
(`git show f42fe7f:tests/test_s0_01_check_acp_conformance.py | wc -l`) = **3956**, delta **+586**.

### R9-CK-F16 — SOLID — ruling R1's expected parent failure is wrong for the shape the committed test produces
R1 requires the rewritten tee test to "FAIL on the parent checker with `drained is not true`". The real tee's SIGTERM status in a
one-frame run is fully forwarded, so `drained` is **true**; the parent rejects it at `C:1337` with
`run-1: tee-status.json write_errors is not empty` (reproduced against the parent module in isolation). The test IS genuinely red on
the parent and green at HEAD — the ruling's stated reason simply describes a loaded SIGTERM, not the one the test creates.

### R9-CK-F18 — SOLID — FINAL/RUNNING type-strictness asymmetry
`C:1382-1397` (FINAL) applies only value comparisons; `C:1407` and `C:1413` (RUNNING) apply `_is_strict_int`. A final status with
`"recorded_c2a": 3.0`, `"forwarded_c2a": 3.0` or `"updated_seq": 6.0` is ACCEPTED (executed). B5d R3/A21b calls the final status "exact
in every field"; the counters' TYPE is not part of that today.
**Fix:** run the `_is_strict_int` gate on all six numeric fields before either arm branches, and add a final-arm float bundle test.

### R9-CK-F19 — SOLID — the bundle fixture hardlinks the TRACKED tools directory
`T:467-468` `dest_tools = tmp_path / "tools"; shutil.copytree(P / "tools", dest_tools, copy_function=os.link)` where
`P = ROOT/"proofs"/"S0-01"`. The checker reads `HERE/"tools"/"frame_tee.py"` at `C:401` with `HERE` monkeypatched to `tmp_path`, so an
in-place write under `tmp_path/tools/` would rewrite a **tracked source file**, not merely the session bundle. No test writes there
today (verified by grep) and the F43 scan is hollow (R9-CK-F3), so nothing would catch a future one.
**Fix:** copy the tools tree with the default `copy_function`, or hardlink from a session-scoped copy the way the evidence tree does.

### R9-CK-F21 — SOLID — the real-leg gate converts three known failures into skips
`T:2764-2777`: `_KNOWN_SKIP_REASONS = {"probe_sha256 mismatch", "agent_interpreter_realpath mismatch", "spawned_at_utc is later than
the first frame"}`; any real-leg Failure whose text CONTAINS one of them becomes `pytest.skip`, not a red. One of the ten skips in both
full runs is exactly that (`real v2.2 sample: probe_sha256 mismatch (capture predates current probe)`). A genuine identity break on a
re-captured corpus would be swallowed. Pre-existing, not A5g's change, but it lives in a lane file and it is a fail-open.

### R9-CK-F22 — SOLID — report overclaim
A5g report row: `R5 F40/F41 | Dead mentions_dir.is_dir() gate in check_two_users deleted … | suite green after deletion`. F41 is six
other gates; none was touched. The Not-done table does not carry them either.

### R9-CK-F23 — SOLID — `_EXPECTED_STARTUP_KEYS` is function-local
`C:1049` defines it inside `check_config_echo`, so a test cannot import the 21-key set to build the exact `missing keys` list; that is
the mechanical reason `T:3694` stays a substring assertion. Hoist it to module scope next to `EXPECTED_RECORD_KEYS`.

### R9-CK-F24 — SOLID — version-string drift
`C:1` "S0-01 ACP conformance checker **v2.2**" vs `T:1` "check_acp_conformance.py **v2.1** test suite". Pre-existing.

### R9-CK-F25 — SOLID — the A25 fallback message can never be right for a reorder
`C:1735-1738`: on `_executed != EXPECTED_CHECK_SEQUENCE` the loop reports the first pair NOT IN `_executed` (membership, not order); a
pure re-ordering has no missing pair and falls through to `golden: check sequence mismatch (63 vs 63 expected)`. Order IS caught (by
the `!=`), but the diagnostic is uninformative for that case.

### R9-CK-F26 — context, not a defect — brief premise drift
The brief's `sha256 4a11b2d6…` is the parent file (`4a54a8b`), not HEAD (`cc80f7b7…`); the lane report's `PIN e84b7ef1…` is not in this
branch's last three commits. Neither changes the grading target.

### R9-CK-F27 — SOLID — the per-leg entry allowlist is name-based, not type-based
`C:1674-1677` checks only `item.name not in allowed`, and `_require_file` (`C:182-185`) only checks `exists()`. A **directory** named
`tee-status.json` (or any other required-file name) passes the allowlist, passes the walk (dirs are legal), passes `_require_file`, and
fails only as `failure_reason: malformed evidence: IsADirectoryError: …` — a generic reason, not `non-regular entry`. Same root cause as
R9-CK-F2; the same `S_ISREG` gate in `_require_file` closes both.

### R9-CK-F28 — SOLID — the shared test helper disables the guard CK8-F2 installed
`T:497-507` `_check` calls `cc.check_bundle(bndl, timeout_s=None)`, i.e. every one of the ~300 bundle tests runs with the wall-clock cap
OFF. Consequence: a regression in the structural walk turns `test_ck8_fifo_in_evidence_tree` / `test_ck8_fifo_in_fixtures_dir_rejected`
from RED into a **hang** rather than a failure (confirmed as a design property; the mutant run for that guard was launched under an
external `timeout`). Only `test_ck8_check_bundle_timeout` (T:3594-3610, explicit `timeout_s=1`) exercises the cap, and nothing
exercises the 90 s default.
**Fix:** give `_check` a generous but finite cap (e.g. `timeout_s=30`) so a walk regression fails loudly instead of wedging the suite,
and add one test that asserts the default is 90 (`inspect.signature(cc.check_bundle).parameters["timeout_s"].default == 90`).

Verified mechanisms behind F2/F27 (executed): `cc._require_file(<a directory>)` returns the path; `cc._require_file(<a FIFO>)` returns
the path; `cc.check_tee_status` on a directory-named-`tee-status.json` raises `IsADirectoryError`, not a `Failure`.

## MUTANT TABLES — 28 mutants + 2 controls; 15 killed, 13 survived

All runs on scratch copies; one mutant at a time per tree; `--basetemp` per run, deleted after; both trees restored and verified
byte-identical to PIN afterwards. Subsets are justified below each table.

### A. R1's named set and its siblings — `-k "tee_status or ck8_running"` (28 selected)
Sufficiency: every mutant here only WIDENS an acceptance condition inside `check_tee_status`, so only a test that expects a
tee-status Failure can change outcome. `grep '"final": True' / ["final"] = True` over `tests/` returns exactly five tests, all in this
subset; the only other tests that touch `tee-status.json` are `test_ck8_f34_*` (key-set/AST, never calls the arms), `test_f43_no_direct*`
(source scan), `test_golden_regen`, `test_twousers_*` (they write a VALID status via `_write_tee_status`, which a widening cannot break).

| id | mutation | result | killing test(s) |
|---|---|---|---|
| NOOP-control | none | 23 passed, 5 skipped, 286 deselected (181.10s) | — |
| FINAL-RELAXED-drained | `C:1384` `drained is not True` → `not isinstance(drained, bool)` | **KILLED** | `test_tee_status_drained_false_final` |
| FINAL-RELAXED-werr | `C:1386` `write_errors != []` → SIGTERM-tolerant | **KILLED** | `test_ck8_running_sigterm_on_final_rejected` |
| FINAL-RELAXED-fwdc2a | `C:1388` `fwd_c2a != rec_c2a` → deficit ∈ {0,1} | **SURVIVED** | none (23 passed, 5 skipped) |
| FINAL-RELAXED-fwda2c | `C:1390` same for a2c | **SURVIVED** | none |
| FINAL-RELAXED-recc2a | `C:1392` `rec_c2a != c2a_count` → deficit ∈ {0,1} | **SURVIVED** | none |
| FINAL-RELAXED-reca2c | `C:1394` same for a2c | **SURVIVED** | none |
| FINAL-RELAXED-seq | `C:1396` `updated_seq != last_seq` → lag ∈ {0,1} | **SURVIVED** | none |
| FINAL-RELAXED-stdin | `C:1437` `stdin_reader_done is not True` → bool | **SURVIVED** | none |
| RUN-DIFF2 | `C:1416` `lag not in (0,1)` → `(0,1,2)` | **SURVIVED** | none |
| RUN-FWD2 | `C:1410` `deficit not in (0,1)` → `(0,1,2)` | **KILLED ×3** | `test_tee_status_forwarded_lt_recorded`, `test_ck7_f8b_tee_status_forwarded_a2c_mismatch`, `test_ck8_running_forwarded_deficit_2_rejected` |
| RUN-RECDEF2 | `C:1422` `deficits[d] not in (0,1)` → `(0,1,2)` | **SURVIVED** | none |
| RUN-ANYERR | `C:1404` running write_errors gate disabled | **KILLED ×3** | `test_ck7_f8a_tee_status_write_errors`, `test_ck8_tee_status_hostile_bundle`, `test_ck8_running_sigkill_errors_rejected` |
| RUN-NOSUM | `C:1431-1433` deleted (global `updated_seq == rec_c2a+rec_a2c`) | **SURVIVED** subset **and full 3-file suite** (`pytest-exit: 0`, `315 passed, 10 skipped in 916.32s`) | none |
| RUN-DEFICIT-SUM | `C:1425-1427` deleted (per-direction deficit sum) | **KILLED** | `test_ck8_running_seq_sum_invariant` |

### B. A5e's combined 24-guard mutant, re-derived at HEAD, FULL 3-file suite
A5e's line list (302, 304, 320, 326, 892, 899, 1162, 1166, 1187, 1195, 1210, 1215, 1217, 1219, 1222, 1272, 1276, 1280, 1288, 1299,
1307, 1365, 1418, 1420 in the A5e-era file) re-mapped to HEAD by exact source text → 323, 325, 341, 347, 931, 938, 1259, 1263, 1284,
1292, 1307, 1312, 1314, 1316, 1319, **1386+1404**, **1390+1410**, **1392+1422**, 1429, 1440, 1448, 1506, 1559, 1561 — 27 `if` lines,
because F8a/F8b/F8c each now exist on BOTH the FINAL and the RUNNING arm and the A5e killers reach the RUNNING one (the fixture status
is `final: false`). Every one patched to `if False and (…):`.

```
pytest-exit: 1
pytest-summary: 32 failed, 283 passed, 10 skipped in 949.26s (0:15:49)   basetemp 126M
```
All 21 A5e-named killers FAIL: `test_ck7_f1_… f2 f3 f4a f4b f5 f6a f6b f7a f7b f7c f7d f8a f8b f8c f8d f8e f8f f9a f9b f9c`.
Plus 11 more: `test_proc_tee_parent`, `test_proc_agent_parent`, `test_proc_closure`, `test_orphan_pair`,
`test_pc_launch_exemption`, `test_tee_status_forwarded_lt_recorded`, `test_ck8_f4_no_tee_parented_by_buzz`,
`test_ck8_tee_status_hostile_bundle`, `test_ck8_running_sigkill_errors_rejected`, `test_ck8_running_sigterm_on_final_rejected`,
`test_ck8_running_forwarded_deficit_2_rejected`.
**24/24 still die after A5g's checker rewrite.** (Brief item (b): DONE.)

### C. CK7/CK8 blocking-id guards and the item-2 mutants
Control `C-NOOP` over the union subset: `20 passed, 294 deselected`.

| id | mutation | subset | result | killing test(s) |
|---|---|---|---|---|
| KEYSET-SUBSET | `C:635` key-set pin → subset check | `-k "f22_post_body_extra or post_body_union"` | **KILLED ×2** | `test_ck7_f22_post_body_extra_key`, `test_ck8_post_body_union_shape_rejected` |
| ROLES-SET | `C:638` `roles != expected_roles` → `set(roles) != set(expected_roles)` | `-k "f23_post_body_wrong_role or nonstream_roles_wrong"` | **SURVIVED** | none |
| F13a-OFF | `C:1192` owned empty/not-a-list | `-k ck8_owned` | **KILLED** | `test_ck8_owned_set_empty` |
| F13b-OFF | `C:1200` owned must contain buzz-acp.pid | `-k ck8_owned` | **KILLED** | `test_ck8_owned_missing_buzz_pid` |
| F14-SKIP-CANCEL | `C:1209`+`C:1211` skipped for leg `cancel` | `-k ck8_f14` | **KILLED ×2** | `test_ck8_f14_rid_pid_not_in_owned[cancel-tee_pid]`, `[cancel-agent_child_pid]` |
| F10-OFF | `C:1241` shutdown "body must be empty" loop → `in []` | `-k "shutdown_owned_pid_survives or audit_p"` | **KILLED** | `test_shutdown_owned_pid_survives` |
| F11-OFF | `C:1331` teardown "body must be empty" loop → `in []` | `-k "survives_teardown or audit_p"` | **KILLED** | `test_audit_p1_generic_child_survives_teardown` |
| F19-OFF | `C:1644` non-regular-entry rule | `-k fifo` | **KILLED BY HANG** | `test_ck8_fifo_in_evidence_tree` blocks (control: `2 passed … in 2.34s`; mutant: `Terminated`, rc 124 at a 150 s external cap) |
| AGENTPAR-OFF | `C:1274` "no agent process parented by a tee process" | `-k "ck8_f4 or proc_closure or orphan_pair"` | **KILLED** | `test_ck8_f4_no_agent_parented_by_tee` |
| TEEPAR-OFF | `C:1272` "no tee process parented by buzz-acp" | **FULL 3-file suite** | **SURVIVED** (`pytest-exit: 0`, `315 passed, 10 skipped in 893.94s`) | none |

Sufficiency for KEYSET-SUBSET / ROLES-SET: both only widen an acceptance condition in `check_upstream_records`; only the two tests that
assert the corresponding reason can change outcome (`grep` for `body key set mismatch` / `message roles` over `tests/`: those two each).

### D. Test-file mutants — the F43 source scan (`-k f43_no_direct`, 1 test, ~0.5 s each)
All three runs carry a REAL in-place violation injected into the non-exempt `test_ck8_owned_set_empty`:
`(bundle / "golden" / "run-1" / "argv.txt").write_text("…")`.

| id | mutation | result |
|---|---|---|
| CTRL-F43 | pristine scan + the violation | **KILLED** — `1 failed` (`T:3319 AssertionError`) — the control IS red |
| F43-ATTRS-OFF | `T:3262 _WRITE_ATTRS = set()` + the violation | **SURVIVED** — `1 passed` |
| F43-SCAN-OFF | `T:3278` → `if True: continue` (real scan fully disabled) + the violation | **SURVIVED** — `1 passed` |

### R9-CK-F5 — SOLID — **BLOCKING** — six of the FINAL arm's ten rules have no killing test
Reproduced: `FINAL-RELAXED-fwdc2a`, `-fwda2c`, `-recc2a`, `-reca2c`, `-seq`, `-stdin` each SURVIVE the subset that provably contains
every test able to kill them. Exactly five tests in the whole suite build a `final: true` status (`T:2317`, `T:2368`, `T:2381`,
`T:3119`, `T:3906`) and they attack only `drained`, `exit_code`, `agent_returncode` and `write_errors`. B5d R3/A21b says the final
status is exact in every field; `C:1388`, `C:1390`, `C:1392`, `C:1394`, `C:1396` and `C:1437` are exactly the fields that make it so,
and A5g rewrote that arm without adding a single test for any of them.
**Red tests to add** (one per rule; the fixture is running-shaped so each must build the final status explicitly):
```python
@pytest.mark.parametrize("field,delta,reason", [
    ("forwarded_c2a", -1, "forwarded_c2a != recorded_c2a"),
    ("forwarded_a2c", -1, "forwarded_a2c != recorded_a2c"),
    ("recorded_c2a",  -1, "recorded_c2a {n} != timeline c2a count {c}"),
    ("recorded_a2c",  -1, "recorded_a2c {n} != timeline a2c count {a}"),
    ("updated_seq",   -1, "updated_seq {n} != timeline last seq {s}"),
])
def test_ck9_final_arm_is_exact(bundle, field, delta, reason): ...
def test_ck9_final_stdin_reader_done_false_rejected(bundle): ...   # exact: "stdin_reader_done is not true when final"
```

### R9-CK-F17 — SOLID — `C:1431-1433` is dead code through the live entry point
`check_timeline` (`C:261-262`) rejects any timeline whose `seq` is not `1..N`, and it runs for every leg before `check_tee_status`
(`EXPECTED_CHECK_SEQUENCE`, `C:214-232`). On such a timeline `last_seq == c2a_count + a2c_count`, so the RUNNING arm's deficit-sum rule
(`C:1425`) and the global seq-sum rule (`C:1431`) are the SAME predicate, and `C:1425` fires first; the FINAL arm's three exact
equalities make `C:1431` unreachable there too. Executed proof both ways: `RUN-NOSUM` (delete `C:1431-1433`) SURVIVES the **full**
3-file suite (`315 passed, 10 skipped`), while `RUN-DEFICIT-SUM` (delete `C:1425-1427`) is KILLED by
`test_ck8_running_seq_sum_invariant` — the kill is by REASON TEXT only, since `C:1431` then catches the identical condition. Direct
call with a non-contiguous timeline `[1,2,3,4,5,7]` (unreachable via `check_bundle`) is the only shape where the two differ.
**Fix or decision:** either delete `C:1431-1433` as dead, or move it ABOVE the arm split so it is the single seq-sum rule and the
arms stop restating it.

### R9-CK-F20 — SOLID — the POST role SEQUENCE is pinned in code but only the role NAMES are tested
`ROLES-SET` (`C:638` → order-and-duplicate-blind set comparison) SURVIVES: `test_ck7_f23_post_body_wrong_role` uses `['tool']` and
`test_ck8_nonstream_roles_wrong` uses `['assistant']`, both wrong NAMES. A reordered `['user','system']` or a duplicated
`['system','system','user']` body is unattacked. Note also `_POST_ROLES_STREAM == _POST_ROLES_NONSTREAM == ["system","user"]`
(`C:623-624`), so the "per-shape role sequences" the report claims carry no per-shape information at all.
**Red test:** `r["body"]["messages"] = [{"role":"user",…},{"role":"system",…}]` →
`assert out == "failure_reason: run-1: upstream POST record stream message roles ['user', 'system'] != expected ['system', 'user']"`.

### R9-CK-F29 — SOLID — the RUNNING arm's two UPPER bounds have no killing test
`RUN-DIFF2` (`C:1416` `lag not in (0,1)` → `(0,1,2)`) and `RUN-RECDEF2` (`C:1422` `deficits[d] not in (0,1)` → `(0,1,2)`) both SURVIVE.
Every existing test drives those values NEGATIVE (status ahead of the timeline), which stays rejected under the widening. B5d R2's
invariants 2 and 3 are the two the checker most needed to pin, and their upper edge is unpinned. My shape table shows the checker
DOES reject "seq lag 2" and "recorded deficit 2" today — nothing holds it there.
**Red tests:** a running snapshot with `updated_seq = last_seq - 2` and both recorded counts trailing by 1 →
`… running snapshot updated_seq {s-2} trails timeline last seq {s} by more than one`; and one with `recorded_c2a = c2a_count - 2`,
`recorded_a2c = a2c_count`, `updated_seq = rec_c2a + rec_a2c` → `… running snapshot recorded_c2a … trails timeline c2a count … by more than one`.

## WHAT I REPRODUCED vs WHAT I ONLY READ

Reproduced (executed this session): the premise (rev-parse/log/status, per-file sha vs HEAD and vs the parent) · both full clean suites
plus a third (`base1`/`base2`/`base3`, all `315 passed, 10 skipped`) · the 28-test subset control · all 28 mutants in the four tables ·
the 38-shape A21d matrix · the REAL tee under SIGTERM and under a clean exit, both statuses through the rewritten checker · the same two
statuses through the PARENT checker in isolation · the tee tripwire test at HEAD · the FIFO hang at `fixtures/identities.json` under
three cap settings · the `--timeout-s` domain (0 / -1 / abc / 1e3 / " 7 ") both in-process and via the CLI · the NaN/±inf/1e400/empty/`[]`
sweep on both arms · the FINAL/RUNNING float asymmetry · `_require_file` on a directory and on a FIFO · `check_process_evidence` on a
dropped-foreign-helper scan · `pc_post_scan` + `audit_cp5_controls` standalone (11 passed) · the live `ps -eww` field-count probe ·
pyflakes · the collection counts · the exact `startup-line missing keys` list.

Reviewed statically only: the six R5 dead-presence-gate derivations (I traced each to the earlier assertion; I did not build a hostile
bundle for any, and `C:1519` I could not settle — marked UNSURE) · A5f's 51-attack table (I re-read CK8's record and re-verified the
current code and tests for F22-F26/F14/F30/F34, but did not rebuild all 51 bundles) · the `_write_*` exempt-helper contamination
analysis (grep for callers, not an executed corruption).

Deliberately skipped, with reasons: `-n 2` / xdist (not installed — `ModuleNotFoundError: No module named 'xdist'`) · the PC suite
(no bridge banner this session) · per-file hashing of the session-pristine bundle across runs (the bundle lives under pytest's
`basetemp` and is destroyed with it; three identical green full runs plus the write-path audit stand in, and the class-level defect
R9-CK-F3 is proved directly) · re-running A5f's full 51-attack sweep (CK8 already recorded it; I re-verified the code paths it
targeted and built the follow-up mutants instead).

## VERDICT

**NOT-READY.**

Blocking ids: **R9-CK-F1** (`--timeout-s 0` / negative silently disables the wall-clock cap → unbounded hang, reproduced),
**R9-CK-F2** (the non-regular-entry walk runs after the first read, so the exact CK8-F2 vector — a FIFO at `fixtures/identities.json` —
is still uncovered by the walk and by the new test; reproduced), **R9-CK-F3** (the F43 source-scan self-test does not exercise the
scan; the scan can be fully disabled with a real violation present and the test still passes — R8-CK-F5 is not closed and the
docstring says it is), **R9-CK-F4** (the A20a rule `no tee process parented by buzz-acp` has no test; `TEEPAR-OFF` survives the FULL
3-file suite, and the test named for it asserts the closure rule instead), **R9-CK-F5** (six of the FINAL arm's ten rules — the arm
this lane rewrote — have no killing test; six independent survivors).

Non-blocking but real, all reported above: F6, F7, F8, F9, F10, F11, F12, F13, F14, F15, F16, F17, F18, F19, F20, F21, F22, F23, F24,
F25, F26, F27, F28, F29.

The three things the lane declared NOT done and I graded as my own work: (a) the R1 mutant set — built and run, two killed, four
survived plus three more survivors from the siblings I added; (b) the 24-guard combined mutant — re-derived at HEAD (27 `if` lines
because three guards now exist on both arms) and re-run on the full suite: **24/24 still die**; (c) the `in out` census — all twenty
are exactly computable, nineteen fully.

This verdict does not depend on anything I failed to reproduce. Every blocking id was executed. The one place my reasoning rests on
reading rather than execution is the R5 deadness derivations (R9-CK-F6), and that reading makes that finding milder, not stronger.

Hygiene: both scratch trees restored and verified byte-identical to PIN `f42fe7f` across all 8 scope files; every `--basetemp`
deleted; `df -h /` 252G/25G/13G/67% at close. `/home/user/agent-factory` never edited, restored, stashed or checked out — the only
commands run there were `rev-parse`, `log`, `status`, `show`, `diff`. Its working-tree dirt (`scripted_backend.py`,
`test_s0_01_scripted_backend.py`, `tests/red/…`) belongs to the other live lanes, not to me.
