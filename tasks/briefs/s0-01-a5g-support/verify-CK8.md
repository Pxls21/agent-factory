# VERIFY-CK8 — adversarial grade of checker lanes A5e + A5f (+ the coordinator's pc_post.sh hunk), round 8

## PREMISE — PASS (with drift, see R8-CK-F21)

`git -C /home/user/agent-factory rev-parse --short HEAD` at start = **`220ffde`**, tree dirty with the five live lane files
(`frame_tee.py`, `scripted_backend.py`, three test files) + `tasks/briefs/s0-01-n5f-...md` — matches the brief. Brief read in full.
Shared tree touched with `git log / status / show / rev-parse / archive` ONLY.
Scratch copy `git archive HEAD | tar -x` → `…/scratchpad/vck8/repo`; `sha256(check_acp_conformance.py)` = `4a11b2d6d198…` = the brief's pin.
End state: my copy `git status --porcelain` = 0 lines, checker sha unchanged `4a11b2d6d198…`; all mutant trees deleted.

```
df -h /   (before first batch)  /dev/vda  252G   22G   16G  59% /
df -h /   (end)                 /dev/vda  252G   23G   15G  61% /
scratch footprint (end)         201M
```

Interpreter `/usr/local/bin/python3` → `/usr/bin/python3.11`, pytest 9.1.1 (`/root/venv-agent-factory/bin/python3` is a symlink to the
same binary). 4 cores shared with the live build lanes; every suite run serial, one at a time, dedicated `--basetemp`, deleted after.

---

## ITEM 7 — COUNTS, HYGIENE (pasted verbatim)

Lane suite = `tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_audit_cp5_controls.py tests/test_s0_01_pc_post_scan.py`,
via `bash scripts/test_summary.sh <files> --basetemp=<dedicated> -p no:randomly`, serial, one at a time:

```
pytest-summary: 274 passed, 5 skipped in 823.72s (0:13:43)      # run 1   basetemp du -sh: 122M
pytest-summary: 274 passed, 5 skipped in 796.09s (0:13:16)      # run 2   basetemp du -sh: 122M
```

279 collected (214 test functions). Skips, exactly, with reasons:

```
SKIPPED [4] tests/test_s0_01_check_acp_conformance.py:2664: real leg predates scan v2.3 (no enumeration header)
SKIPPED [1] tests/test_s0_01_check_acp_conformance.py:2748: real v2.2 sample: probe_sha256 mismatch (capture predates current probe)
```

Real-leg corpus IS present in the sandbox (`…/scratchpad/realleg/golden`, legs run-1/cancel/shutdown/two-users/negative):
`41 passed, 5 skipped, 224 deselected in 7.37s` (`-k real_leg`) — the 5 skips are the same 5 above.

```
python3 -m pyflakes proofs/S0-01/check_acp_conformance.py tests/test_s0_01_check_acp_conformance.py \
        tests/test_s0_01_audit_cp5_controls.py tests/test_s0_01_pc_post_scan.py proofs/S0-01/pins.py
→ rc=0, no output
```

A28 reason-assertion greps over `tests/test_s0_01_check_acp_conformance.py` (target 0):

| pattern | count | lines |
|---|---|---|
| `assert … in out` | **12** | 725, 1596, 1932, 1946, 1957, 1989, 2113, 2155, 2166, 2213, 2324, 2387 |
| `assert … in result` | **8** | 514, 515, 517, 2046, 2241, 2374, 2586, 2647 |
| `startswith("failure_reason:` | **14** | 813, 1097, 1246, 1263, 1274, 1284, 1447, 1565, 1608, 1621, 1885, 2012, 2022, 2040 |
| ` or ` as an operator in a reason assertion | **0** | (T:784 / T:802 are literal text inside exact-equality strings — grep false positives) |

A5f's not_done declares these open, so the numbers are consistent with its report; they are still 34 non-exact reason assertions.

---

## ITEM 1 — CK7's BLOCKING IDS: guard → regression test → mutant → killer

Guard lines are **re-derived at HEAD `220ffde`** (A5e's report line refs are stale — R8-CK-F15).
Every mutation below is `if <cond>:` → `if False:` (a FULL disable, stronger than A5e's `if False and <cond>:`, which leaves the second
clause of an `or` live — A5e disclosed that limitation) or `for … in <it>:` → `for … in []:`.

### 1a. Combined mutant M-ALL — 42 guards disabled at once, full lane suite

```
45 failed, 229 passed, 5 skipped in 760.05s (0:12:40)
```

All **21** A5e `test_ck7_f*` tests went RED, plus A5f's 8 (`f22, f23, f24, f25, f26_extra, f26_empty, f14, f30`), plus
`test_proc_tee_parent, test_proc_agent_parent, test_proc_closure, test_proc_closure_seed, test_teardown_has_tee, test_orphan_pair,
test_pc_launch_exemption, test_dup_startup_key, test_audit_p1_generic_child_survives_teardown, test_symlink_upstream_record,
test_symlink_manifest_gz, test_tee_status_extra_key, test_tee_status_recorded_ne_timeline, test_shutdown_owned_pid_survives,
test_v23_teardown_survivor`, and `audit_cp5_controls::test_shutdown_owned_survivor_is_named_whatever_its_command`.
**36 of 42 guards killed; 6 survivors.**

### 1b. CK7 blocking ids, one mutant each, with a control (`test_passing_v2_bundle` green in every run)

| id | guard @HEAD | mutation | result | killing test |
|---|---|---|---|---|
| F1 | `C:912` `if not (owner_ev[…] < first_term_epoch and user2_ev[…] < first_term_epoch):` | iffalse | **KILLED** | `test_ck7_f1_second_mention_after_first_terminal` (`1 failed, 1 passed`) |
| F2 | `C:919` `if new_seqs[1]["seq"] < term_seqs[0]["seq"]:` | iffalse | **KILLED** | `test_ck7_f2_second_session_new_before_first_terminal` |
| F3 | `C:317` `if len(seqs) > 1:` | iffalse | **KILLED** | `test_ck7_f3_duplicate_response_id` |
| F4a | `C:299` a2c + method + id | iffalse | **KILLED** | `test_ck7_f4a_a2c_agent_request` |
| F4b | `C:301` c2a + id − method | iffalse | **KILLED** | `test_ck7_f4b_c2a_client_response` |
| F5 | `C:323` `jsonrpc != "2.0" or ("result" in f)==("error" in f)` | iffalse (FULL, both clauses) | **KILLED** | `test_ck7_f5_invalid_response_envelope` |
| F10 | `C:1209` shutdown after-scan survivor loop | emptyloop | **KILLED** ×2 | `test_shutdown_owned_pid_survives`, `audit_cp5_controls::test_shutdown_owned_survivor_is_named_whatever_its_command` |
| F11 | `C:1299` teardown survivor loop | emptyloop | **KILLED** ×3 | `test_teardown_has_tee`, `test_audit_p1_generic_child_survives_teardown`, `test_v23_teardown_survivor` |
| **F13a** | `C:1160` `owned` empty / not a list | iffalse | **SURVIVED** | **NONE** |
| **F13b** | `C:1168` `buzz_pid not in owned_set` | iffalse | **SURVIVED** | **NONE** |
| **F19** | `C:1541` non-regular (FIFO/socket/device) entry in the walk | iffalse | **SURVIVED** | **NONE** |

### 1c. Survivor confirmation M-SURV — 8 guards disabled, full lane suite

```
274 passed, 5 skipped in 671.76s (0:11:11)      # IDENTICAL to the un-mutated runs
```

| id | guard @HEAD | reason string | test coverage |
|---|---|---|---|
| S1 | `C:1072` `if missing:` (F25 required startup keys) | `startup-line missing keys: […]` | 0 occurrences in all 3 test files |
| S2 | `C:1160` (F13a) | `owned-pids.json owned is empty or not a list` | 0 |
| S3 | `C:1168` (F13b) | `owned-pids.json does not contain buzz-acp.pid <pid>` | 0 |
| S4 | `C:1179` (F14b) | `owned-pids.json does not contain rid agent_child_pid <pid>` | 0 |
| S5 | `C:1294` (F30 teardown arm) | `process-scan-teardown.txt duplicate rows for pid(s) […]` | 0 |
| S6 | `C:1541` (F19) | `golden: non-regular entry in evidence tree: <path>` | 0 |
| S7 | `C:1240` A20a | `no tee process parented by buzz-acp` | 0 (was 2 at parent commit `2877327`) |
| S8 | `C:1242` A20a | `no agent process parented by a tee process` | 0 (was 1 at `2877327`) |

**8/8 survive at full-suite scope.** Second, independent instrument: `grep -c` of each reason string over all three test files = 0.

### 1d. F19 reproduced end-to-end with a real FIFO

```
# HEAD checker, mkfifo golden/run-1/timeline.jsonl
failure_reason: golden: non-regular entry in evidence tree: golden/run-1/timeline.jsonl     rc=1  elapsed 0s
# same tree, C:1541 disabled, --timeout-s 8
failure_reason: checker timed out after 8s                                                  rc=70 elapsed 8s
# HEAD checker, FIFO in the --fixtures-dir instead of under golden/ (walk does not cover it)
failure_reason: checker timed out after 6s                                                  rc=70 elapsed 6s
```

So the code fix works, the SIGALRM cap is a real backstop — and **neither has a test**; the walk covers `golden/` only, and the cap
lives only in `main()` (`check_bundle()` called in-process, as every test does, has no cap).

---

## ITEM 2 — A5f's F22–F26, F14, F30, F34, F43 + the new mutants

### 2a. Hostile bundles — 51 attacks through the real `check_bundle` on the suite's own synthetic PASS bundle

Harness: the suite's session-bundle builder invoked standalone, `cp -al` per attack, mutations unlink-before-write, `cc.HERE`/
`PINNED_GOLDEN_SHA256` set exactly as the `bundle` fixture does. Control (no mutation) →
`PASS: S0-01 acp-conformance - 63 checks executed over 5 legs; golden x2 identical (11 normalized lines, sha256 e088d7827be7); …`

**A5f's reported reasons reproduce EXACTLY (8/8):**

| id | attack | observed |
|---|---|---|
| F22 | POST body `evil_tool_calls=[{"exfil":"yes"}]` | `run-1: upstream POST record body has extra keys: ['evil_tool_calls']` |
| F23 | POST message `role="tool"` | `run-1: upstream POST record message role 'tool' not in allowed set` |
| F24 | GET fp `"f"*64` | `run-1: upstream GET record authorization_fingerprint mismatch` |
| F25 | startup + log append ` backdoor=on` | `run-1: startup-line unknown key 'backdoor'` |
| F26 extra | receipt `mention_pubkeys` + 64-hex | `run-1: mention owner receipt mention_pubkeys ['ff4d…','aaaa…'] != expected ['ff4d…']` |
| F26 empty | `mention_pubkeys = []` | `run-1: mention owner receipt mention_pubkeys [] != expected ['ff4d…']` |
| F14 | shutdown rid `tee_pid=77777` | `shutdown: owned-pids.json does not contain rid tee_pid 77777` |
| F30 | after-scan duplicate row | `run-1: process-scan-after.txt duplicate rows for pid(s) [12340]` |

**42 of 51 attacks are rejected with an exact reason. 9 are ACCEPTED (exit 0, full PASS line):**

| # | attack | verdict |
|---|---|---|
| a04 | GET `authorization_fingerprint = null` on run-1 (a POST-carrying leg) | **PASS** — null is the only non-pinned value accepted (R8-CK-F7) |
| a06 | `subscribe=Everything context_limit=999999 max_turns_per_session=999 model=(gpt-9 jailbreak)` | **PASS** (R8-CK-F6) |
| a10 | `model=(agent default backdoor=on evil=1)` | **PASS** — parens swallow `key=value` tokens (R8-CK-F6) |
| c01 | startup line stripped to only the 11 REQUIRED keys | **PASS** (R8-CK-F6) |
| c02 | POST body carrying the union `max_tokens+stream_options+tools+response_format+temperature` | **PASS** (R8-CK-F8) |
| c03 | non-stream title POST `messages = [{"role":"assistant",…}]` | **PASS** (R8-CK-F8) |
| b05 | every timeline entry sharing one `t_mono_ns`/`t_utc` | PASS — contract-permitted (CK7-F29, unchanged) |
| b07 | `stdin_reader_done=false` on a non-final status | PASS — correct under the B5d ruling |
| b17 | 63-hex `S0_01_FRAMEDIR` | PASS — chosen boundary (CK7-F27, unchanged) |

Other CK7 items re-attacked and now CLOSED with exact reasons: F10 `shutdown: process 424242 (/usr/bin/sleep 900) survived shutdown` ·
F11 `run-1: process 999001 (…) survived teardown` · F12 `shutdown: process-scan-teardown.txt buzz_present=1 (expected 0)` ·
F13a `shutdown: owned-pids.json owned is empty or not a list` · F13b `… does not contain buzz-acp.pid 12300` ·
F15 `run-1: owned-pids.json has extra keys: ['junk']` · F16 `… header buzz_acp_pid=999999 != buzz-acp.pid 12300` ·
F17 `… header pinned_present=4242 inconsistent with body (3)` · F18 `run-1: timeline.jsonl blank line at line 2` ·
F20 `run-1: agent-stderr.txt absent` · F21 `run-1: unexpected entry EXTRA.txt` / `unexpected entry extra-dir` ·
F28 `run-1: buzz-acp.exit is '-9', expected '0'` · F31 `run-1: tee-status.json final is not a bool` ·
F47 golden trailing blank → `golden: golden.jsonl blank line at line 12` · symlink → `golden: symlink in evidence tree: …` ·
A20e foreign pinned process → `run-1: process 77000 (…) not in buzz-acp descendant tree`.

### 2b. New mutants the brief asked for

| id | mutation | result | killing test |
|---|---|---|---|
| M-KEYSUB | `C:1331` key-set pin relaxed to a subset check (`if not _TEE_STATUS_KEYS.issubset(set(ts.keys())):`) | **KILLED** | `test_tee_status_extra_key` (`1 failed, 2 passed`) |
| M-ROLE | `C:604` role set widened with `"tool"` | **KILLED** | `test_ck7_f23_post_body_wrong_role` |
| M-F14-shutdown | `C:1177` → `if leg != "shutdown" and rid_tee not in owned_set:` | **KILLED** | `test_ck7_f14_shutdown_rid_pids_not_in_owned` |
| M-F14-run-1 | `C:1177` → `if leg != "run-1" and …` | **KILLED** | `test_proc_closure_seed` (T:1568 — repurposed by A5f from the m59 mutual-parent attack) |
| **M-F14-run-2** | `C:1177` → `if leg != "run-2" and …` | **SURVIVED** | none (`81 passed, 5 skipped` over the 86-test process-evidence subset) |
| **M-F14-cancel** | `C:1177` → `if leg != "cancel" and …` | **SURVIVED** | none (`81 passed, 5 skipped`) |
| **M-F14-two-users** | `C:1177` → `if leg != "two-users" and …` | **SURVIVED** | none (`81 passed, 5 skipped`) |
| **M-F14b** | `C:1179` disabled on ALL legs | **SURVIVED** | none (`81 passed, 5 skipped`; and full-suite green in M-SURV) |
| M-F30a | `C:1190` after-scan duplicate | **KILLED** | `test_ck7_f30_after_scan_duplicate_pid` |
| **M-F30b** | `C:1294` teardown duplicate | **SURVIVED** | none (full-suite green in M-SURV) |

F24 null arm: `C:595` `if get_fp is not None and get_fp != expected_fp` — null is the **only** non-pinned value accepted, and it IS
accepted on a POST-carrying leg (a04). The real corpus's GET (`000001.json GET /models fp=None`) carries null; the synthetic
fixture's GET carries the pinned fingerprint (`T:302-306`) — the two arms are exercised by different corpora and the null arm's only
coverage is the real-leg accept path. Assessment in R8-CK-F7.

F25 required vs allowed: there **is** a required set of 11 (`relay, agent_cmd, mcp_cmd, idle_timeout, max_turn, agents, dedup,
session_policy, ignore_self, permission_mode, respond_to`) inside a 21-key allowed set. A one-token line therefore does NOT pass:
`run-1: startup-line missing keys: ['agent_cmd','agents','dedup','idle_timeout','ignore_self','max_turn','mcp_cmd','permission_mode','respond_to','session_policy']`.
Duplicate key → `run-1: startup-line duplicate key 'agents'`. Parenthesised values parse correctly on the real corpus
(`model=(agent default)`, empty `mcp_cmd=`, the double space after `agent_cmd`) — `test_real_leg_config_echo` is the real-producer proof.

F26 ordering/duplicates: `mpk != [identities["agent"]]` is list equality, so duplicates fail
(`… mention_pubkeys ['ff4d…','ff4d…'] != expected ['ff4d…']`). Ordering is unconstrained in practice because the expected list always
has exactly one element.

### 2c. Totals

**51 distinct mutations exercised · 40 killed · 11 survived.**
(42 in M-ALL → 36 killed / 6 survived; + S7, S8 → survived; + 5 per-leg F14a → 2 killed / 3 survived; + M-KEYSUB, M-ROLE → killed.)
**51 hostile bundles · 42 rejected with the exact expected reason · 9 accepted.**

---

## ITEM 3 — F43 hardlink fixture: the contamination hunt

**Instrument:** a verifier-added `conftest.py` that, after EVERY test, sha256-hashes all 151 files of the session-pristine bundle
(`<basetemp>/bundle0/**`) and logs any change. It also records `st_nlink`, so its log proves it was actually watching
(61 112 nlink-only churn entries — the per-test `cp -al` copies coming and going).

* Serial run 1: `274 passed, 5 skipped in 823.72s`, temp 122 MB (down from A5d's 4.7 GB).
* Serial run 2 (with the probe): `274 passed, 5 skipped in 796.09s`, temp 122 MB, **0 pristine-bundle content changes across all 279 tests.**
* `-n 2`: **NOT RUN HERE — `pytest-xdist` is not installed in this sandbox** (`ModuleNotFoundError: No module named 'xdist'`);
  A5f's `-n 8` runs were on the PC. Reasoned, not reproduced: xdist gives each worker its own `basetemp`, so `_session_bundle` is built
  per worker and the hardlink-sharing surface is intra-worker — identical to serial, so the contamination class below is not xdist-specific.

**Every write path to a bundle path, AST-enumerated (not grepped):** inside `test_*` functions there are **zero** `open()`,
`json.dump`, `shutil.copy*` or `os.replace` calls; 232 `_rewrite()` calls; `copytree`/`rename` only at T:1803/1805 and T:1861/1863
(both create a NEW `run-2-copy` path, then `rmtree`+`rename` — safe); `symlink_to` only at T:2152/2163 (new paths — safe).
Only two writer helpers are called from tests — `_write_timeline` (31 tests) and `_write_tee_status` (2 tests) — and both unlink first
(T:143-145, T:353). **The shipped test file is clean.**

**The guard against it is hollow.** `test_f43_no_direct_writes_outside_rewrite` (T:3210-3232) flags only `.write_text` / `.write_bytes`
attribute calls inside module-level `test_*` functions. I appended three in-place-write mutants and ran them:

```
4 passed, 269 deselected in 28.48s      # test_f43_no_direct_writes_outside_rewrite PASSES beside all three mutants
```

and the pristine probe proves all three actually corrupt the shared inode:

```
CONTENT CHANGED after test_ck8_inplace_write_mutant    bundle0/evidence/golden/run-1/buzz-acp.exit    9a271f2a91 -> cfeb3721a8
CONTENT CHANGED after test_ck8_inplace_write_mutant_b  bundle0/evidence/golden/run-1/owned-pids.json  555230f452 -> 260bb234a0
CONTENT CHANGED after test_ck8_inplace_write_mutant_c  bundle0/evidence/golden/run-1/buzz-acp.exit    cfeb3721a8 -> 9a271f2a91
```

Mutant a = `with open(p, "w")`, b = `json.dump(obj, open(p, "w"))`, c = `shutil.copy(src, p)`. See R8-CK-F5.

---

## ITEM 4 — A21d AS THE CHECKER ENFORCES IT TODAY vs THE B5d TEE RULING (no fix; feeds the A5g brief)

B5d rulings taken from `tasks/briefs/s0-01-b5d-tee-drain-to-eof.md` R1/R2/R3. Every row below was REPRODUCED by feeding that exact
status shape through `check_bundle`; the reason string is verbatim from the run.

### Running snapshot (`final: false`)

| # | B5d-legal shape | checker line | exact reason printed |
|---|---|---|---|
| 1 | `drained: false` (one frame in flight — `_drained` is computed, not asserted, by the tee) | `C:1335-1336` | `run-1: tee-status.json drained is not true` |
| 2 | `write_errors: ["terminated: SIGTERM"]` (R3: whitelist exactly this on non-final legs) | `C:1337-1338` | `run-1: tee-status.json write_errors is not empty` |
| 3 | `recorded_c2a - forwarded_c2a == 1` (R2 bound `{0,1}` on running snapshots) | `C:1339-1340` | `run-1: tee-status.json forwarded_c2a != recorded_c2a` |
| 4 | `recorded_a2c - forwarded_a2c == 1` | `C:1341-1342` | `run-1: tee-status.json forwarded_a2c != recorded_a2c` |
| 5 | `updated_seq == last_seq - 1` **with** the matching `recorded_*` lag (R2: `updated_seq == recorded_c2a + recorded_a2c`) | `C:1345-1346` / `C:1347-1348` (fires first) | `run-1: tee-status.json recorded_a2c 7 != timeline a2c count 8` |
| 6 | `updated_seq == last_seq - 1` alone | `C:1350-1351` | `run-1: tee-status.json updated_seq 10 != timeline last seq 11` |

Rows 1–6 are ALL of the rejections; nothing else in `check_tee_status` fires on a B5d-shaped running status.
`stdin_reader_done: false` on a running status is **accepted** (`C:1358-1359` gates it on `final is True`) — consistent with R1.

### Final status (`final: true`)

No rejection. B5d's final contract (exact equality of `recorded`/`forwarded`, `drained true`, `stdin_reader_done true`,
`updated_seq == last_seq`, `write_errors []`, `exit_code = rc if rc>=0 else 128+(-rc)`) is exactly what `C:1335-1369` enforces.
The one gap is evidentiary, not logical: there is **no real-leg `tee-status.json`** anywhere in the corpus, so A21d has zero
real-producer coverage (CK7-F35, still in A5f's not_done), and the only fixture is hand-authored to the strict shape.

---

## ITEM 5 — `_PINS_PENDING`

* Values are consumed from the dict everywhere: `C:1077` defines it, `C:1079` and `C:1085` read it; `grep -rn "bypassPermissions"`
  over `proofs/` + `tests/` finds it only at `C:1077`, in the five committed `startup-line.txt` evidence files, and in the test
  fixture's startup line (`T:201`). No stray literal in the checker.
* **NOT a one-line change.** The switch needs: 2 names added to the `from pins import (…)` block, the dict deleted, the 2-line
  `TODO(A5f-F42)` comment deleted, 2 dict reads renamed — ≈6 touched lines in the checker, plus the pins.py hunk.
  `expected_rt = "owner-only" if leg != "two-users" else "allowlist(1)"` (`C:1089`) is **still a bare pair of literals** and is not
  mentioned in A5f's not_done.
* **No test pins either value.** `grep -n "_PINS_PENDING" tests/` → 0 hits. The values are only implicitly asserted by the passing
  bundle's hand-written startup line.
* **The precondition has already landed.** At the live tip `c9c7e1d` `proofs/S0-01/pins.py` carries
  `PINNED_STARTUP_MCP_CMD = ""`, `PINNED_STARTUP_PERMISSION_MODE = "bypassPermissions"`, `PINNED_STARTUP_RESPOND_TO = "owner-only"`,
  `PINNED_STARTUP_RESPOND_TO_TWO_USERS = "allowlist(1)"` — values identical to the local literals — while
  `check_acp_conformance.py` at `c9c7e1d` still contains `_PINS_PENDING` at line 1077 and the `expected_rt` ternary at 1089.
  **Four pins are landed but unconsumed (dead constants).**

---

## ITEM 6 — THE COORDINATOR'S `pc_post.sh` HUNK

### Parser tolerance of `ps -eww -o pid,ppid,etimes,stat,args`

Live survey of the sandbox's own table (97 rows): **0 rows with fewer than 5 whitespace fields**; stat tokens observed
`SLl, S, I<, I, SN, SL, Z, RN, Ss, R, Sl, SNl` — all whitespace-free, so a wider flag string such as `Ssl+` parses identically;
max row width 1293 chars (no 80-column clipping with `-ww`). `pc_post.sh:34` `line.split(None, 4)` therefore keeps `args` intact,
including embedded spaces, and the checker's `_parse_scan_v23` (`C:1116` `line.split(None, 3)`) mirrors it. Zombie rows render as
`482 1 68861 Z [sh] <defunct>` — 5 fields, correctly routed to `zombies` by `parts[3].startswith("Z")` (`pc_post.sh:37`).

Row-injection probe: a child spawned with a literal newline **plus a forged scan row** in its argv —
`x\n999999 1 42 /usr/bin/python3 <PINNED_TEE_PATH>` — is rendered by procps with the newline collapsed to a space, so the scan file
stays one row per process and `_parse_scan_v23` returns exactly one tuple. Injection is not reachable. Note the safety is inherited
from `ps`, not from producer escaping: `pc_post.sh:76` writes `cmd` verbatim into a line-oriented file with no quoting.

Latent (UNSURE, see R8-CK-F13): `pc_post.sh:35-36` silently `continue`s any row with <5 fields. Such a row would be absent from
`rows`, hence from `rows=`, `table_pids`, `owned_present` and `pinned_present` **consistently** — a dropped owned survivor would be
invisible AND leave no header/body inconsistency. I could not construct one (procps always emits `[comm]`).

### The helper filter (`pc_post.sh:67`)

Reproduced against real process trees, with the target reparented to init (ppid 1) so it is genuinely outside the owned closure:

| probe | target | in body? | header `pinned_present` vs body | checker outcome |
|---|---|---|---|---|
| h1 (reproduces `test_owned_row_is_never_dropped_by_the_helper_filter`) | OWNED row whose cmd contains `pc_post.sh` and ` ps -eo` | **kept** | 1 == 1 | `owned_present` == owned body rows, as the comment at `pc_post.sh:65-66` claims |
| g1 | FOREIGN (ppid 1) row naming a pinned path | **kept** | 1 == 1 | visible; A20e then fails it — `run-1: process 77000 (…) not in buzz-acp descendant tree` |
| g2 | FOREIGN row naming a pinned path AND containing `pc_post.sh` | **dropped** | 1 vs 0 | **MISMATCH → Failure** `process-scan-after.txt header pinned_present=1 inconsistent with body (0)` |
| g3 | FOREIGN row naming a pinned path AND containing ` ps -e` | **dropped** | 1 vs 0 | same Failure |

**Answer to the brief's question.** The checker's process-evidence rule needs BOTH the full owned set (for the closure recomputation
at `C:1220-1228` and `owned_present`) AND every row naming a pinned path (for A20a `C:1231-1233`, A20e `C:1268-1276`, and the shutdown
empty-body rule `C:1209`). The producer's helper filter CAN drop a pinned-naming foreign row — but `pinned_present` is computed over
the FULL table (`pc_post.sh:71`) while the checker counts body rows (`C:1203-1208`), so the drop becomes a **loud, fail-CLOSED
Failure**, never a silent hole. It is therefore not a hole; it is a false-positive risk: a legitimately concurrent capture whose helper
command line also names a pinned path would fail the leg. No test covers that path (R8-CK-F14).

Both clauses of the second filter are unreachable for OWNED rows by construction (`r[0] in owned` short-circuits) — which is exactly
the property `test_owned_row_is_never_dropped_by_the_helper_filter` pins, and it reproduces.

---

## FINDINGS

`C` = `…/scratchpad/vck8/repo/proofs/S0-01/check_acp_conformance.py`, `T` = `…/scratchpad/vck8/repo/tests/test_s0_01_check_acp_conformance.py`
(line numbers identical to HEAD `220ffde`). Everything below was reproduced unless stated.

### R8-CK-F1 — SOLID — **BLOCKING** — CK7's F13 shipped with zero regression coverage
`C:1159-1161`, `C:1167-1169`. Both guards survive `if False:` with the full lane suite green (M-SURV `274 passed, 5 skipped`), and
neither reason string appears anywhere in the three test files (`grep -c` = 0). The rules DO work: `{"owned": []}` on shutdown →
`shutdown: owned-pids.json owned is empty or not a list`; owned without the buzz pid → `shutdown: owned-pids.json does not contain
buzz-acp.pid 12300`. Observed: a single edit re-opens the audit's "vacuous shutdown cleanup proof" with no test failing.
Expected: a named killing test per arm, as the A5e/A5f briefs require for every landed rule.
**Red test to add:** `test_ck8_owned_set_empty` and `test_ck8_owned_missing_buzz_pid`, each asserting the exact reason above.

### R8-CK-F2 — SOLID — **BLOCKING** — CK7's F19 shipped with zero regression coverage, and the timeout is undocumented and out of reach in-process
`C:1541-1542` (the non-regular-entry rule) survives `if False:` with the suite green; `grep -c "non-regular"` over the tests = 0.
Reproduced: HEAD rejects a FIFO instantly (`golden: non-regular entry in evidence tree: golden/run-1/timeline.jsonl`, rc 1); with the
guard disabled the checker hangs and only the SIGALRM cap returns (`failure_reason: checker timed out after 8s`, rc 70). Three further
gaps: (a) the walk covers `golden/` only — a FIFO in the `--fixtures-dir` still hangs to the cap (reproduced, rc 70 after 6 s);
(b) the cap exists only in `main()` (`C:1671-1675`), so `check_bundle()` — every test and any in-process consumer — has none;
(c) `--timeout-s` has no test and exit code **70 is undocumented** (module docstring `C:3` lists 0/1/2/64), while
`proofs/S0-01/spec.json` sets the runner's own `timeout_s: 120` — the same number as the checker's default cap, so a slow-but-valid
run races its own killer.
**Red tests to add:** `test_ck8_fifo_in_evidence_tree` (exact reason), `test_ck8_fifo_in_fixtures_dir_times_out` (rc 70 + exact line),
`test_ck8_timeout_arg_rejects_non_int` (rc 64), and a docstring fix listing 70.

### R8-CK-F3 — SOLID — **BLOCKING** — F14 is tested on 2 of 5 legs for `tee_pid` and 0 of 5 for `agent_child_pid`
`C:1176-1180`. Per-leg mutants: `leg != "shutdown"` → killed by `test_ck7_f14_shutdown_rid_pids_not_in_owned`; `leg != "run-1"` →
killed by `test_proc_closure_seed`; `leg != "run-2"`, `leg != "cancel"`, `leg != "two-users"` → **SURVIVE** (`81 passed, 5 skipped`
each over the process-evidence subset). `C:1179` (`rid_agent`) disabled on every leg → **full suite green** (M-SURV). The rule fires
correctly when attacked (`run-1: owned-pids.json does not contain rid tee_pid 77777`,
`cancel: owned-pids.json does not contain rid agent_child_pid 88888`). A5f's report states F14 "validates rid tee_pid and
agent_child_pid in owned_set on EVERY leg" — the code does; the gate does not.
**Red tests to add:** parametrise over `LEGS` × {`tee_pid`, `agent_child_pid`} — 10 exact-reason cases.

### R8-CK-F4 — SOLID — **BLOCKING** — A5f's F14 ordering change silently un-gated two A20a structural rules
`C:1240-1241` `no tee process parented by buzz-acp` and `C:1242-1243` `no agent process parented by a tee process` have **zero**
assertions at HEAD. At the parent commit they had three:
`git show 2877327:tests/test_s0_01_check_acp_conformance.py | grep -n "no tee process parented\|no agent process parented"` → lines
1516, 1528, 1552; the same grep at `220ffde` returns 0. Both guards disabled → full suite green (M-SURV S7/S8). A5f's discrepancies
disclose that `test_proc_tee_parent` / `test_proc_agent_parent` now assert `recomputed owned closure != owned-pids.json` instead, and
`test_proc_closure_seed`'s own docstring now reads "F14: owned=[12300] excludes rid pids → caught first" — but the lost coverage is
**not** in A5f's not_done, and the brief's rule is that an empty not_done beside an unmet item reopens the lane.
**Red tests to add:** restore the two attacks with a FULL owned set (so F14 passes and the structural guard is the one that fires),
asserting the two exact reasons.

### R8-CK-F5 — SOLID — **BLOCKING** — the F43 source-scan guard is hollow, and its docstring is false
`T:3210-3232`. The AST scan flags only `.write_text` / `.write_bytes` attribute calls inside module-level `test_*` functions. Its own
docstring claims it forbids `open(,'w')` — not implemented. Three mutants (`open(p,"w")`, `json.dump(obj, open(p,"w"))`,
`shutil.copy(src,p)`) all pass the guard (`4 passed, 269 deselected`) and each provably corrupts the session-pristine bundle
(hashes above). It also ignores every non-`test_`-prefixed helper, which is exactly where `_write_process_scan` (T:317-343) writes
WITHOUT unlinking — one call from a test away from the same corruption. This is the mechanism behind the "intermittent hardlink
contamination" A5f reported and could not root-cause.
**Red test to add:** extend the scan to `open(...)` / `Path.open(...)` with a mode containing `w`/`a`/`+`, plus `json.dump`,
`shutil.copy*`, `os.replace`, over ALL module-level functions, and self-test it with a deliberately-violating source string.

### R8-CK-F6 — SOLID — F25 is an allowed-key set, not an exact match; 10 of 21 keys have unconstrained values
`C:1029-1088`. Three accepted hostile bundles: values of `subscribe`, `context_limit`, `max_turns_per_session`, `model` rewritten →
PASS; `model=(agent default backdoor=on evil=1)` → PASS (a parenthesised value swallows arbitrary `key=value` tokens, bypassing the
`unknown key` rule at `C:1066`); a startup line reduced to only the 11 required keys → PASS. Unpinned keys: `pubkey, heartbeat,
subscribe, meh, context_limit, max_turns_per_session, presence, typing, memory, model`. Separately, `C:1072` (`missing keys`) has no
test (M-SURV green). A5f's report line "Startup-line exact match: all tokens must be key=value with key in `_EXPECTED_STARTUP_KEYS`"
overstates what landed.
**Red tests to add:** pin the security-relevant values (`subscribe`, `max_turns_per_session`, `context_limit`) in `pins.py`; make the
required set the full 21; reject `(` values that contain `=`; add a `missing keys` exact-reason test.

### R8-CK-F7 — SOLID — F24's null arm is unpinned and is the weaker of two available rules
`C:592-596`. `authorization_fingerprint = null` on a GET is accepted even on a leg whose POSTs carry the pinned fingerprint (a04 →
PASS). The header screen (`C:585-589`) already rejects any `authorization`-shaped header, so this field is the SOLE record of an
outbound credential on a GET; accepting null lets a bundle erase it. The real corpus's GET carries `null`
(`realleg/golden/run-1/upstream-records/000001.json`) while the synthetic fixture's GET carries the pinned fingerprint (`T:302-306`) —
so the two arms are exercised by different corpora, and the null arm's only coverage is the real-leg accept path.
**Red test to add:** pin GET fingerprints to `is None` exactly (matching the real producer), change the fixture's GET record to null,
and add `test_ck8_get_fingerprint_non_null_rejected` asserting the exact reason.

### R8-CK-F8 — SOLID — F22's key pin is a union across two real request shapes; F23 pins only the role vocabulary
`C:602-620`. `_ALLOWED_POST_BODY_KEYS` unions the real corpus's two shapes (`{max_tokens, messages, model, stream, stream_options,
tools}` and `{messages, model, response_format, temperature}`), so a body carrying all of them at once passes (c02 → PASS) though no
real request has that shape — A5f's own self-attack #3 predicted this. F23 constrains role VALUES only: the non-stream title POST's
entire `messages` array can be replaced with `[{"role":"assistant","content":"whatever"}]` and it passes (c03 → PASS), so CK7-F23
("non-stream upstream POST records are unconstrained") is only partially closed.
**Red tests to add:** two per-shape key sets keyed on `body.get("stream")`; and a content/role-sequence assertion on the non-stream POST.

### R8-CK-F9 — SOLID — F30's teardown arm has no test
`C:1293-1297`. Disabled → full suite green (M-SURV S5); `grep -c "process-scan-teardown.txt duplicate rows"` over the tests = 0.
The rule works: two identical teardown rows → `run-1: process-scan-teardown.txt duplicate rows for pid(s) [99001]`.
**Red test to add:** `test_ck8_teardown_scan_duplicate_pid` with that exact reason.

### R8-CK-F10 — SOLID — F34's test does not run the tee; its name and docstring say it does
`T:3348-3369`. It AST-parses `proofs/S0-01/tools/frame_tee.py` and compares the `_write_status` dict's string keys to
`PINNED_TEE_STATUS_KEYS`; the docstring reads "run the committed frame_tee.py and verify its emitted key set", and the A5f brief said
"RUN the committed tee once in a test and bind its emitted key set to `pins.PINNED_TEE_STATUS_KEYS`". A5f's table concedes "via AST
extraction" but not_done does not list the unmet requirement. The coupling itself HOLDS: I re-extracted at HEAD and at the live tip
`c9c7e1d` (where B5d's 43-line `frame_tee.py` rewrite landed) — 12 keys, exact match, one dict literal, both times. Also the test
compares SETS while `pins.py:128` claims "Order = the tee's write order" — order is unbound.
**Red test to add:** execute the committed tee once (`subprocess`, a two-frame stdin, SIGTERM) and read the emitted
`tee-status.json`'s key list, asserting `tuple(keys) == PINNED_TEE_STATUS_KEYS`.

### R8-CK-F11 — SOLID — A21d rejects six B5d-legal running shapes (item 4 table); no fix here, lane A5g
`C:1335-1351`. Recorded for the A5g brief. The consumer-side gap that A5g cannot fix on its own: there is no real-leg
`tee-status.json` anywhere in the corpus, so every A21d rule is proven against a hand-authored fixture only (CK7-F35, still open).

### R8-CK-F12 — SOLID — `_PINS_PENDING`, and four pins that have already landed unconsumed
See item 5. `C:1077/1079/1085` plus the untouched `expected_rt` literals at `C:1089`. No test pins the values; the switch is ≈6 lines,
not one; and at the live tip the four `PINNED_STARTUP_*` constants exist in `pins.py` with matching values while the checker still
reads the local dict, so they are dead constants today.
**Red test to add:** `test_ck8_startup_values_come_from_pins` — monkeypatch `pins.PINNED_STARTUP_PERMISSION_MODE` and assert the
checker's reason quotes the patched value (a test the current dict would fail).

### R8-CK-F13 — SOLID on tolerance, UNSURE on the latent drop — `pc_post.sh` parser
`pc_post.sh:33-42`. Tolerance verified empirically (item 6). The latent item: `pc_post.sh:35-36` silently drops rows with <5 fields;
such a drop is self-consistent across `rows=`, `owned_present` and `pinned_present`, so an owned survivor lost this way would be
invisible to every checker rule. I could not construct a live row with an empty `args` (procps substitutes `[comm]`), so I mark the
reachability UNSURE rather than claiming a hole.
**Red test to add (producer side):** make the `<5 fields` branch fail loud (`sys.exit`) rather than `continue`, and pin that with a
test that feeds a synthetic short row through the same parser.

### R8-CK-F14 — SOLID — the helper filter is fail-closed, but the false-positive path is untested
`pc_post.sh:67` + `C:1203-1208`. Reproduced (item 6 table). `test_owned_row_is_never_dropped_by_the_helper_filter`
(`tests/test_s0_01_pc_post_scan.py:181-201`) reproduces standalone. What no test covers: the g2/g3 path where a FOREIGN pinned-naming
row is filtered and the leg then fails on `pinned_present … inconsistent with body`. That is the only way a legitimate concurrent
capture can red a leg, and it would be diagnosed as evidence tampering.
**Red test to add:** spawn an orphaned process whose cmd contains a pinned path AND `pc_post.sh`, run the real producer, and assert the
checker's exact `pinned_present … inconsistent with body` reason — pinning the behaviour as deliberate.

### R8-CK-F15 — SOLID — A5e's report `file:line` refs do not resolve at HEAD
19 of the 21 cited lines (`C:302, 304, 320, 326, 892, 899, 1187, 1195, 1215, 1217, 1219, 1222, 1272, 1276, 1288, 1299, 1307, 1418, 1420`)
land on unrelated code at `220ffde`; only `C:1280` and `C:1365` coincidentally still name their guard. Expected drift (A5f edited the
file afterwards), but the record now misleads a reader. The HEAD-resolved guard table is in item 1 of this report.

### R8-CK-F16 — SOLID — A5f's countable claims do not re-derive
"211 test-function write calls transformed by AST" → 232 `_rewrite()` calls inside test functions at HEAD (232 in the file total).
"`_write_timeline` … is called from 33 test functions" → 31. Neither is a defect; both are AF-AP-37-class typed numbers in a report
that a reader will treat as measured.

### R8-CK-F17 — SOLID — fixture-provenance docstrings still overclaim
`T:346-350` `_write_tee_status`: "Derived from the committed frame_tee.py output plus the three running-status fields" — the values are
hand-authored; only the key SET is bound, and only by an AST read (R8-CK-F10). CK7-F34's docstring complaint is unresolved and
CK7-F35 (no real-leg `tee-status.json`) is still open, so A21d has zero real-producer coverage.

### R8-CK-F18 — SOLID — `-n 2` NOT RUN HERE
`pytest-xdist` is absent in this sandbox (`ModuleNotFoundError: No module named 'xdist'`). A5f's `-n 8` numbers are PC numbers.
Reasoned, not reproduced: xdist gives each worker its own basetemp, so the pristine bundle is per-worker and the hardlink-sharing
surface is intra-worker; R8-CK-F5's class is therefore not xdist-specific. Anything depending on parallel behaviour in my verdict is
flagged here — nothing does.

### R8-CK-F19 — SOLID — F43's disk fix is real and no contamination reproduces
122 MB per serial run (from 4.7 GB), twice, and 0 pristine-bundle content changes across 279 tests with a per-test hashing probe that
demonstrably saw all 151 files (61 112 nlink-churn entries). A5f's "intermittent sandbox hardlink contamination" does not reproduce at
HEAD. Its self-attack #2 ("the root cause is not identified") is now answered by R8-CK-F5: the discipline is correct in the shipped
file; only the guard that is supposed to keep it correct is hollow.

### R8-CK-F20 — SOLID — A28 remains open, and A5f says so
34 non-exact reason assertions (item 7 table). The three one-sided real-leg greens CK7-F36 named are unchanged: `T:2586`
`assert "tee_sha256 mismatch" in result`, `T:2647` `assert "manifest timestamps not pre < start < post" in result`, and the
`_KNOWN_SKIP_REASONS` substring set at `T:2737-2750`. All three currently take the `ok` branch on this corpus.

### R8-CK-F21 — context, not a defect — PREMISE DRIFT during the grading
The shared tree moved from `220ffde` to **`c9c7e1d`** while I graded, and is now clean (the coordinator committed the live lanes'
work: checkpoints 8h/8i/8j, two pins commits, ledger/wiki). Of my scope files only `proofs/S0-01/pins.py` changed (+12 lines: the four
`PINNED_STARTUP_*` constants — see R8-CK-F12). `check_acp_conformance.py`, the three test files and `pc_post.sh` are byte-identical at
`c9c7e1d`. `frame_tee.py` changed (B5d, ±43/40 lines) and the F34 coupling still holds against it. Everything above is graded at
`220ffde` as briefed.

### R8-CK-F22 — SOLID — undocumented exit code and a self-racing timeout
`C:3` documents exit codes 0/1/2/64; `C:1672-1674` can exit **70**. `proofs/S0-01/spec.json` sets `timeout_s: 120` for the positive
leg, the same value as the checker's own default `--timeout-s`, so on a slow venue the runner and the checker's alarm race, and the
runner's failure mode differs from the checker's (`failure_reason: checker timed out after 120s`, rc 70) with no test pinning either.
**Red test to add:** a CLI test asserting rc 70 + the exact line for `--timeout-s 1` against a slow tree, and a docstring/spec fix.

---

## WHAT I REPRODUCED vs REVIEWED STATICALLY vs SKIPPED

**Reproduced (ran on my copy):** both clean lane-suite runs; the real-leg subset; the 42-guard combined mutant against the full suite;
the 8-guard survivor mutant against the full suite; 18 single/targeted mutant runs (F1-F5, F10, F11, F13a, F13b, F19, F14a, F14b, F30a,
F30b, key-set-subset, role-widened, five per-leg F14a); 51 hostile bundles through the real `check_bundle` (42 exact reasons, 9 PASSes);
the FIFO hang and the SIGALRM backstop end-to-end through the CLI, including the fixtures-dir variant; the three in-place-write mutants
and the per-test pristine-bundle hashing that proves they corrupt it; the producer probes (ps field survey, zombie shape, newline-argv
injection attempt, four helper-filter trees with orphaned targets); the F34 AST coupling at HEAD and at the live tip; pyflakes; all greps.

**Reviewed statically only:** the claim that pytest-xdist would not change the hardlink-sharing surface (R8-CK-F18) — xdist is not
installed here, so that is reasoning, not a run. The `<5 fields` drop path in `pc_post.sh` (R8-CK-F13) — I could not construct a live
row that hits it. The B5d rulings themselves were read from the B5d brief, not re-derived from the tee's code (the tee is another
lane's file and was dirty in the shared tree); the six A21d rejections were reproduced against the checker with those shapes.

**Deliberately skipped:** the `-n 2` run (xdist absent — R8-CK-F18); grading `frame_tee.py`, `scripted_backend.py`, `acp_probe.py` and
their tests (other lanes' files, outside scope); re-running A5e's weaker `if False and …` combined mutant verbatim (my `if False:`
version is a strict superset and covers the two `or`-guards A5e could not fully disable); any execution inside the shared working tree.

---

## VERDICT: **NOT-READY**

Blocking ids: **R8-CK-F1** (CK7's F13 owned-set shape and buzz-pid binding: zero regression tests, both guards survive a full disable
with the suite green), **R8-CK-F2** (CK7's F19 non-regular-entry rule: zero regression tests, guard survives; the walk misses the
fixtures dir; the wall-clock cap exists only in `main()`, has no test, and its exit code 70 is undocumented), **R8-CK-F3** (F14 is
gated on 2 of 5 legs for `tee_pid` and 0 of 5 for `agent_child_pid` — three per-leg skip mutants and the whole `agent_child_pid` arm
survive), **R8-CK-F4** (A5f's F14 ordering change silently un-gated two A20a structural rules that had three assertions at the parent
commit and have none now, undeclared in not_done), and **R8-CK-F5** (the F43 source-scan guard misses `open(,'w')`, `json.dump` and
`shutil.copy` — its own docstring claims otherwise — and all three provably corrupt the session-pristine bundle).

Second tier, all real, none individually blocking: R8-CK-F6 (F25 is an allowed-set, not exact; 10 unpinned values; parens bypass the
unknown-key rule; `missing keys` untested), F7 (GET null-fingerprint arm), F8 (POST body key union; non-stream messages unconstrained),
F9 (teardown duplicate rule untested), F10 (F34's test does not run the tee, contra its docstring and its brief), F11/F17 (A21d vs
B5d, and A21d's zero real-producer coverage), F12 (four pins landed unconsumed; `expected_rt` literals; no test pins the values),
F13/F14 (`pc_post.sh` latent short-row drop; untested fail-closed false-positive path), F15/F16 (stale line refs and non-re-derivable
counts in the lane reports), F20 (34 non-exact reason assertions), F22 (undocumented exit 70 / self-racing timeout).
R8-CK-F19 records what genuinely landed: F43's 4.7 GB → 122 MB with no reproducible contamination.

This verdict does **not** depend on anything I failed to reproduce. Every blocking finding rests on a mutant run and a grep, both
pasted above. The two non-reproduced items (R8-CK-F18's xdist reasoning, R8-CK-F13's unreachable short-row path) are second-tier and
are flagged in place.
