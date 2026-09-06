Everything is reproduced and the tree is clean. Final report.

---

## PREMISE CHECK — PASS

`git log --oneline -2` in `/home/user/agent-factory`: `7cd83c7 transcripts: scrubbed sandbox chat digests (2026-09-06)` on top of `5f81e34 S0-01 WIP checkpoint 7a: … (AF-AP-47) — REVIEW-PENDING, nothing minted`. Matches the brief. Brief file read in full, ends with the expected sentence.

Scratch copy built with `git archive HEAD | tar -x` into `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vck7`. All work done there; the shared tree got only `git log` / `git status` / `git archive`. Verified byte-identical to HEAD at the end (`diff -rq` vs a fresh archive: no differences). All mutant trees deleted; `df` 22 GB free.

**ENOSPC window:** my own 4-way concurrent mutant batch (09:00–09:17 UTC) is what filled the disk. All 13 of its logs are VOID and discarded — every failure was `OSError` inside the `bundle` fixture, never a behavioural message. Everything reported below was produced after 09:26 UTC, one tree at a time, each with a dedicated `--basetemp` deleted afterwards.

---

## MUTATION AUDIT — the headline result

One combined mutant, 24 guards disabled one line each (`if False and …`), run against the lane's own suite:

```
3 failed, 238 passed, 5 skipped in 657.79s (0:10:57)
FAILED test_proc_closure · test_orphan_pair · test_pc_launch_exemption
```

Only the three A20a closure/descendant-tree guards were killed. **21 of 24 disabled guards produced no failure.** Disabling guards can only make the checker more permissive, so a test can go pass→fail but never fail→pass; the three reds are all process-closure assertions and cannot be attributed to the other 21. Independent second instrument: the removed reason strings appear **0 times** in `test_s0_01_check_acp_conformance.py`, `test_s0_01_audit_cp5_controls.py`, `test_s0_01_pc_post_scan.py`.

---

## FINDINGS

Paths relative to my copy root `…/scratchpad/vck7/`; line numbers identical to HEAD. `C` = `proofs/S0-01/check_acp_conformance.py`, `T` = `tests/test_s0_01_check_acp_conformance.py`.

### Hollow gates — implemented, untested (mutation survivors)

**R7-CK-F1 — SOLID — `C:890-893`.** A24 ingress-concurrency ("second mention not pending during the first turn") — the audit's P1 *"Two sequential users satisfy a concurrent-user requirement"* repair — has **no test**. Mutant: guard disabled → suite green. Grep: reason string 0× in all three test files. The check does work: my re-signed sequential attack (user2 `created_at` moved past the first terminal, event re-signed, receipt id updated) gave exactly `failure_reason: two-users: second mention not pending during the first turn`. **Fix:** add that attack as a named test.

**R7-CK-F2 — SOLID — `C:896-899`.** A24 observed-serialization ("second session/new precedes the first terminal") — no test. Same mutant/grep. Attack (second `session/new` moved before the first terminal, timestamps re-stamped monotone) → `failure_reason: two-users: second session/new precedes the first terminal`.

**R7-CK-F3 — SOLID — `C:318-321`.** A23 response cardinality — the audit's P1 *"Conflicting terminal responses are silently collapsed"* — has **no test**. Mutant survived; `"duplicate response for id"` 0× in tests. Attack (error response with the same id inserted immediately before the successful `end_turn`) → `failure_reason: run-1: duplicate response for id 2 at seqs [11, 12]`. An audit P1 repair with zero regression coverage.

**R7-CK-F4 — SOLID — `C:302-306`.** A23 frame classes (a2c agent request / c2a client response) — no tests; both mutants survived. Attacks fire correctly (`run-1: a2c frame at seq 3 is an agent request (method='session/request_permission')`, `run-1: c2a frame at seq 3 is a client response (id=901)`).

**R7-CK-F5 — SOLID — `C:325-328`.** A23 response-envelope validity — no test; mutant survived. Attack (`result` and `error` in one envelope) → `run-1: response at seq 2 is not a valid JSON-RPC envelope`.

**R7-CK-F6 — SOLID — `C:1153`, `C:1161`.** A20b identity ppid bindings (`tee_pid ppid is not buzz_acp_pid`, `agent_child_pid ppid is not tee_pid`) — no tests; both mutants survived. Only the `not found in scan` arm is covered (`test_audit_p1_rid_pids_unbound_to_scan`).

**R7-CK-F7 — SOLID — `C:1178-1191`.** The teardown-scan header rules (mode / `rows=0` / `owned` / `owned_present`) have **no tests** — all four mutants survived. Only the after-scan equivalents are tested (`test_v23_mode_mismatch`, `test_v23_rows_zero`, `test_v23_owned_count_mismatch`, `test_v23_owned_present_mismatch`). A5c's report claims these rules as done; they are ungated on the teardown file.

**R7-CK-F8 — SOLID — `C:1230,1236,1243,1250-1252,1255-1256,1260-1261`.** Six A21d sub-rules with no tests, all mutants survived: `write_errors` non-empty, `forwarded_a2c != recorded_a2c` (only the c2a arm is tested), `recorded_a2c != timeline`, `updated_utc` format, final-but-`agent_returncode`-not-int, not-final-but-`exit_code`-not-null (only the `agent_returncode` arm is tested, `T:2306-2311`).

**R7-CK-F9 — SOLID — `C:1315,1367,1369`.** Golden structural rules with no tests, mutants survived: "exactly one of each request kind", run-1/run-2 raw sessionId identity, run-1/run-2 first `t_utc` identity.

### Contract violations — hostile bundles the complete checker ACCEPTS (exit 0, full PASS line)

**R7-CK-F10 — SOLID — `C:1112-1121`.** A20 v2.3 rule 4 ("shutdown legs: … an EMPTY body") is not enforced. Attack: shutdown `process-scan-after.txt` = valid header (`buzz_present=0 owned_present=0`) plus body rows `424242 1 999 /usr/bin/sleep 900` and `424243 424242 999 /usr/bin/python3 <PINNED_TEE_PATH>` → `PASS: … 63 checks executed over 5 legs`. **A live process running the pinned tee after shutdown is accepted.** The shutdown branch skips the "not owned and cmd names no pinned path" rule entirely. **Fix:** in the shutdown branch require `all_procs == []`.

**R7-CK-F11 — SOLID — `C:1192-1196`.** A20 v2.3 rule 5 ("the teardown scan `owned_present == 0` with an empty body") is not enforced for non-shutdown legs. Attack: run-1 teardown = valid header + `999001 1 999 /usr/bin/python3 <PINNED_TEE_PATH> --still-running` → PASS. Only pids in `owned_set` are survivors, but the producer's keep rule (`pc_post.sh:62`) persists *any* row naming a pinned path — so a leftover tee/agent outside the recorded closure is captured in the evidence and then silently accepted. This re-opens the audit's P1 cleanup gap for the non-owned case. **Fix:** require an empty teardown body on every leg.

**R7-CK-F12 — SOLID — `C:1119`.** A20 v2.3 rule 4 requires `buzz_present == 0` on the shutdown after-scan **and** the teardown scan; `td_hdr.group(4)` is never read. Attack: shutdown teardown header `buzz_present=1` → PASS.

**R7-CK-F13 — SOLID — `C:1093-1096` + `C:1112`.** The shutdown leg's cleanup proof is vacuous when the evidence declares an empty owned set. Attack: shutdown `owned-pids.json` = `{"buzz_acp_pid":12300,"owned":[],"taken_at":"ready+after"}`, headers `owned=0 owned_present=0`, empty bodies → PASS. Nothing binds the shutdown leg's owned set to `buzz-acp.pid`, to `runtime-identity.json`, or to any other leg. This is precisely the "positive evidence, never a vacuous 'no line contains'" rule A20d was written for. **Fix:** require `owned_set` non-empty and containing `buzz-acp.pid` + rid `tee_pid`/`agent_child_pid` on every leg.

**R7-CK-F14 — SOLID — `C:1140-1163`.** Shutdown-leg runtime-identity pids are never bound to anything (identity binding lives only in the non-shutdown branch). Attack: shutdown rid `tee_pid=77777`, `agent_child_pid=88888` → PASS. (The same mutation on run-1 correctly fails: `run-1: tee_pid 77777 not found in scan`.)

**R7-CK-F15 — SOLID — `C:1093-1096`.** `owned-pids.json` is never validated beyond `.get("owned", [])`. Attack: `{"owned":[12300,12340,12345],"junk":"whatever","taken_at":"never"}` (no `buzz_acp_pid`) → PASS. A20 pins the object shape.

**R7-CK-F16 — SOLID — `C:1104-1110`.** The header's `buzz_acp_pid` (group 3) is never read. Attack: header `buzz_acp_pid=999999` with the correct body → PASS.

**R7-CK-F17 — SOLID.** `pinned_present` (group 7) has no consumer anywhere. Attack: `pinned_present=4242` → PASS.

**R7-CK-F18 — SOLID — `C:1381`.** A8's blank-line rule is not enforced on the positive timeline: `_load_timeline_raw` filters `if line.strip()`. Attack: blank + whitespace-only lines inserted into `run-1/timeline.jsonl` → PASS. The identical class **is** a Failure in frames files (`C:266-271`, `frames-…jsonl blank line at line N`) and in the coordinator-owned validator (`negative_contract.py:59`, reproduced: `negative: timeline.jsonl line 2 is blank`). Same filtering at `C:1300` (golden.jsonl) and `C:1065` (scan bodies). The lane's classification of `timeline_blank_line`/`timeline_ws_line` as "contract-permitted because the raw loader filters it" is circular — the loader *is* the defect.

**R7-CK-F19 — SOLID — HANG — `C:1409-1414`.** A FIFO in the evidence tree makes the checker never terminate. The 5-F18 walk tests `is_symlink()` only; a FIFO is not a symlink, and every `read_text()` on it blocks with no timeout. Reproduced end-to-end: `os.mkfifo(golden/run-1/agent-stderr.txt)`, then the CLI with `--fixtures-dir` → *"checker did not terminate in 25 s"*. A5b's survivor `golden_fifo_entry` is not "contract-permitted" — it is a denial of verification that will hang CI. **Fix:** reject any non-regular, non-directory entry in the walk (`stat.S_ISREG`/`S_ISDIR`), and give the CLI a wall-clock cap.

**R7-CK-F20 — SOLID — `C:1442-1447`.** The 5-F19 secret screen is presence-gated and `agent-stderr.txt` is not required in positive legs. Attack pair: write `bearer sk-live-DEADBEEF` → `failure_reason: run-1: agent-stderr.txt contains a secret-shaped string`; then `unlink` the file → PASS. Deleting the file in *all five* positive legs → PASS. (The negative leg is safe: `NEGATIVE_REQUIRED_FILES` makes absence a Failure.)

**R7-CK-F21 — SOLID.** Leg directories have no entry allowlist. Attacks: `golden/run-1/EXTRA.txt` → PASS; `golden/run-1/extra-dir/x.json` → PASS. The same class is closed for `golden/` (`C:1400-1406`), `manifests/` (`C:1396-1398`), `mentions/` (`C:478-481`) and `negative/` (`C:1267-1271`). This omission is what makes F19 and F20 exploitable.

**R7-CK-F22 — SOLID — `C:594-601`.** Upstream POST record bodies accept arbitrary extra keys. Attack: `body["evil_tool_calls"]=[{"exfil":"yes"}]` → PASS. Only `body.model`, `stream`, and a mention-text search are pinned.

**R7-CK-F23 — SOLID.** Non-stream upstream POST records are unconstrained. Attack: every message `role` in `000001.json` rewritten to `"assistant"` → PASS.

**R7-CK-F24 — SOLID — `C:592-593`.** GET records' `authorization_fingerprint` is never checked. Attack: `"f"*64` on the GET record → PASS.

**R7-CK-F25 — SOLID — `C:1017-1025`.** The startup line is not exact-matched: tokens without `=` are skipped and keys outside `required_keys` ignored. Attack: append ` backdoor=on unparsed_token` to `startup-line.txt` **and** the matching `buzzacp.log` line → PASS.

**R7-CK-F26 — SOLID — `C:510-517`.** Receipt `mention_pubkeys` accepts extra 64-hex entries and the empty list. Both attacks → PASS.

**R7-CK-F27 — SOLID — `C:1117` (`_HEX64_ANYWHERE_RE`).** 63-hex boundary. Attack: `S0_01_FRAMEDIR = "/tmp/frames/" + "a"*63` → PASS. Contract pins 64; recorded as a chosen boundary, not a violation.

**R7-CK-F28 — SOLID — `C:1084-1090` vs `C:823-825`.** `buzz-acp.exit` is pinned to `"0"` only on the shutdown leg. Attack: `run-1/buzz-acp.exit` = `-9` → PASS.

**R7-CK-F29 — SOLID — `C:252-258`.** Every entry sharing one `t_mono_ns` and one `t_utc` → PASS (non-decreasing permits equality). Contract-permitted; recorded.

**R7-CK-F30 — SOLID — `C:1149`, `C:1157`.** Duplicate scan rows for one pid are tolerated and only `[0]` is identity-bound. Attack: append `12340 999999 90 /usr/bin/python3 <PINNED_TEE_PATH> --imposter` with `owned_present=4` → PASS.

**R7-CK-F31 — SOLID — `C:1253`.** `final` is truthiness-tested while `drained` is strictly `is not True`. Attack: `"final": "no"` (truthy string) + `agent_returncode: 0` + `exit_code: 0` → PASS, taking the **final** branch on a status shape the producer never emits.

**R7-CK-F32 — SOLID — `C:1226`.** `stdin_reader_done` is in the key set but its value is never asserted. Attack: `false` → PASS. Contract-permitted by A21d's literal text; flagged because it is the tee's own drain evidence (B5's 4-F14 asserts the value in the producer suite, the consumer does not).

### Fixture vs producer (A27)

**R7-CK-F33 — SOLID — `T:304-310`.** The synthetic bundle's header is not what the producer writes. `_scan_header` defaults `pinned_present=0`; the same body (three rows naming `PINNED_BUZZ_ACP_EXE_REALPATH` / `PINNED_TEE_PATH` / `PINNED_AGENT_REALPATH`) makes the real producer emit `pinned_present=3`. Verified by running `pc_post.sh scan` standalone (diff below). Invisible because of F17. A5c's own report concedes the header lines are hand-written per bundle.

**R7-CK-F34 — SOLID — `T:340-363`.** The `tee-status.json` fixture is hand-authored; its docstring claims it is "Derived from the committed frame_tee.py output". No test binds `_TEE_STATUS_KEYS` (`C:104-109`) to `frame_tee.py`'s actual output. I confirmed by reading `frame_tee.py:148-166` that the twelve keys currently match — so this is an **unguarded coupling**, not a live break. A27 required the fixture be produced by running the committed producer.

**R7-CK-F35 — SOLID.** There is no real-leg test for `check_tee_status`, and the real corpus contains no `tee-status.json` in any leg. A21d has zero real-producer coverage.

### Exact-reason discipline (A28)

**R7-CK-F36 — SOLID — `T:2556-2560`, `T:2617-2622`, `T:2707-2725`.** Three real-leg tests are literally the `ok or <substring>` shape A28 forbids: `assert "tee_sha256 mismatch" in result`, `assert "manifest timestamps not pre < start < post" in result`, and a three-element `_KNOWN_SKIP_REASONS` substring set. All three currently take the `ok` branch on this corpus, so they are one-sided greens that cannot distinguish "checker passed" from "checker failed for the excused reason".

**R7-CK-F37 — SOLID.** ~25 non-exact reason assertions remain despite A28/5-F11/6-F13. Load-bearing ones: `T:1961` `assert "check sequence mismatch" in out` (the A25 guard's only test does not pin the first-missing pair), `T:1569`/`T:2087` `"survived teardown" in out`, `T:2364` `"survived shutdown" in out`, `T:2129`/`T:2140` `"symlink in evidence tree" in out` (5-F18 required naming the path), `T:2189`, `T:2217`, `T:2300`, `T:2350`.

### A25 sequence guard

**R7-CK-F38 — SOLID — `C:1470-1476`.** The guard itself is sound. I reproduced the audit's P2 verbatim by deleting run-2's `check_env` invocation at the dispatcher (not a rename): `failure_reason: golden: check sequence mismatch - first missing: check_env:run-2`. A same-length duplicate+omission (two-users omitted, cancel doubled) is also caught. `len(EXPECTED_CHECK_SEQUENCE) == 63`, no duplicate pairs, PASS line reports `len(_executed) == 63` — matches the observed `63 checks executed over 5 legs`. Weakness: the lane's own test mutates by **rename** (`skip_cancel`), which changes `fn.__name__` and so never exercises a true omission, and it asserts a substring (F37).

**R7-CK-F39 — SOLID — `C:220-224`.** `_run_check` appends the pair *after* the function returns, so a check that returns without asserting anything (the vacuous shutdown process check of F13) still counts as executed. The guard proves invocation, never that the check had anything to assert.

### Reachability

**R7-CK-F40 — SOLID — `C:878-879` vs `C:472`.** The AF-AP-40 fix in `check_two_users` is unreachable from the live entry point: `check_mentions` fails first with `two-users: mentions/ absent` (reproduced by deleting the dir → that reason, not `mentions/ absent in two-users`). Only the direct-call test `T:2244` covers it.

**R7-CK-F41 — SOLID — `C:890`, `C:898`, `C:1327`, `C:1340`, `C:1367`, `C:1373`.** Six dead presence gates remain, each provably non-None/present by an earlier check on the same path. A5b's brief item 5 asked for *every* such guard to be treated like the mentions one; only that one was.

### A26

**R7-CK-F42 — SOLID — `C:1027-1035`, `C:1039`.** A26 partially applied: `agents`/`dedup`/`ignore_self` come from pins, but `"mcp_cmd": ""`, `"permission_mode": "bypassPermissions"` and `expected_rt = "allowlist(1)"` remain local literals of pinned values. The wrong-value control works (`run-1: startup agents is '4', expected '1'`).

### Suite economics and hygiene

**R7-CK-F43 — SOLID — `T:441-459`.** One run of the three files consumes **4.7 GB** of temp (measured under a dedicated `--basetemp` on both runs). The `bundle` fixture does three `copytree` calls per test. Two concurrent runs of this suite exhaust this box's disk — that is exactly the 09:00–09:17 ENOSPC event.

**R7-CK-F44 — SOLID.** Duration 672.76 s / 659.32 s, on a **contended** box (other lanes' `test_s0_01_scripted_backend.py` / `test_s0_01_frame_tee.py` and another verifier's mutant trees ran throughout). Treat as an upper bound, not a clean measurement.

**R7-CK-F45 — SOLID — `T:80-87`.** 5-F17 is closed. Verified empirically with a `conftest.py` `pytest_sessionfinish` probe: `5-F17 RESTORE CHECK: nv._point_mul is the original -> True`. `_orig_pm` is captured at import (`T:68`) before any patch.

**R7-CK-F46 — context, not a defect.** The shared working tree has moved past HEAD since I archived it — `proofs/S0-01/pins.py` is now modified (uncommitted, coordinator-owned). A pins change (e.g. `PINNED_GOLDEN_SHA256`, currently `None`) changes checker behaviour; this grading is against HEAD `7cd83c7` as briefed.

**R7-CK-F47 — SOLID.** A5b's "17 contract-permitted survivors" list is stale and mis-classified. I re-graded all 17 by direct attack:

| survivor | observed now | grade |
|---|---|---|
| `timeline_blank_line` | PASS | **contract violation** (A8) — F18 |
| `timeline_ws_line` | PASS | **contract violation** (A8) — F18 |
| `golden_jsonl_trailing_blank_lines` | PASS (sha re-pinned) | **contract violation** (A8) — F18 |
| `golden_fifo_entry` | **HANG** | **worse than permitted** — F19 |
| `teardown_file_empty` | `run-1: process-scan-teardown.txt has no enumeration header` | now **KILLED** by A5c |
| `buzzacp_log_empty_nonshutdown` | `run-1: buzzacp.log has no line containing 'buzz-acp starting:'` | now **KILLED** |
| `manifest_pre_post_swapped_ts` | `run-1: manifest timestamps not pre < start < post` | **KILLED** |
| `leg_dir_extra_file` | PASS | permitted, but the class is closed everywhere else — F21 |
| `record_post_extra_body_keys` | PASS | permitted; egress evidence under-constrained — F22 |
| `record_body_messages_assistant_only` | PASS | permitted — F23 |
| `record_get_bogus_fingerprint` | PASS | permitted — F24 |
| `startup_extra_unknown_token` | PASS | permitted — F25 |
| `mentions_receipt_extra_pubkey_junk` | PASS | permitted — F26 |
| `record_mention_pubkeys_empty` | PASS | permitted — F26 |
| `env_value_hex_63_plus_boundary` | PASS | permitted (chosen boundary) — F27 |
| `exit_negative_nonshutdown` | PASS | permitted — F28 |
| `timeline_identical_mono_and_utc` | PASS | permitted — F29 |

---

## AUDIT'S EIGHT BLOCKERS — replayed verbatim as hostile bundles

| audit blocker | attack | observed | verdict |
|---|---|---|---|
| P1 negative = a2c request, same id | `{"jsonrpc":"2.0","id":0,"method":"session/request_permission","params":{}}` | `1 failure_reason: negative: negative: agent sent a request (method 'session/request_permission') instead of a response at seq 2` | CLOSED |
| P1 negative failed delivery | `agent_exit_code=-9, agent_argv=["/usr/bin/true"], agent_child_pid=-1` | `1 … negative: agent_argv mismatch`; `probe_error` alone → `negative: probe reported an error: BrokenPipeError: request not delivered`; `agent_exit_code=-9` alone → `negative: agent_exit_code is -9, expected 0` | CLOSED |
| P1 manifest symlink | symlink in evidence tree; retargeted `l` line | `1 … golden: symlink in evidence tree: golden/run-1/active.py`; `1 … run-1: baseline gz sha256 mismatch` | CLOSED (but F19: FIFO evades the same walk) |
| P1 generic survivor after teardown | `12345 1 130 /usr/bin/sleep 60` in teardown | `1 … run-1: process 12345 (/usr/bin/sleep 60) survived teardown` | CLOSED for owned pids; **F10/F11 re-open it for non-owned rows naming pinned paths** |
| P1 rid pids unbound to scan | `tee_pid=77777, agent_child_pid=88888` | `1 … run-1: tee_pid 77777 not found in scan` | CLOSED on non-shutdown legs; **F14: not on shutdown** |
| P1 two sequential users | user2 `created_at` after first terminal, re-signed | `1 … two-users: second mention not pending during the first turn` | code CLOSED, **F1: no test** |
| P1 conflicting terminals | error response with same id before `end_turn` | `1 … run-1: duplicate response for id 2 at seqs [11, 12]` | code CLOSED, **F3: no test** |
| P2 tee lost output | `forwarded_a2c = recorded_a2c - 1` | `1 … run-1: tee-status.json forwarded_a2c != recorded_a2c` | CLOSED, **F8: no test** |
| P2 omitted leg check | run-2 `check_env` invocation deleted at the dispatcher | `1 … golden: check sequence mismatch - first missing: check_env:run-2` | CLOSED |

---

## REAL-CORPUS OUTCOMES — `scratchpad/realleg/golden/`

`pytest -k real_leg` → **41 passed, 5 skipped in 10.57s**. Corpus is v2.2: 4-field scans, no v2.3 header, shutdown after-scan is 0 bytes, no `tee-status.json`, no `run-2`, no `golden.jsonl`.

| check | run-1 | cancel | shutdown | two-users | negative |
|---|---|---|---|---|---|
| timeline | ok | ok | ok | ok | — |
| initialize_frames | ok | ok | ok | ok | — |
| runtime_identity | ok | ok | ok | ok | — |
| env | ok | ok | ok | ok | — |
| mentions | ok | ok | ok | ok | — |
| route | ok | ok | ok | ok | — |
| config_echo | ok | ok | ok | ok | — |
| manifests | ok | ok | ok | ok | — |
| **process_evidence** | **SKIP** `real leg predates scan v2.3 (no enumeration header)` | same | same | same | — |
| buzzacp_log | ok | ok | ok | ok | — |
| prompt_turn | ok | — | ok | — | — |
| cancel / shutdown / two_users | — | ok | ok | ok | — |
| tee_status | **no test exists** (F35) | — | — | — | — |
| negative | — | — | — | — | **SKIP** `real v2.2 sample: probe_sha256 mismatch (capture predates current probe)` |

Matches the brief's expectation exactly. Note the skip in `test_real_leg_process_evidence` is reached through the header check at `T:2634-2639`; the earlier `owned-pids.json` guard does not fire because the corpus does carry that file.

---

## FIXTURE-VS-PRODUCER HEADER DIFF

`pc_post.sh scan after` run standalone (`S0_01_REPO=<my copy>`) against a three-level tree I spawned with the pinned paths in argv:

```
PRODUCER (3 owned rows, all naming pinned paths):
# process-scan v2.3 mode=after rows=96 buzz_acp_pid=18034 buzz_present=1 owned=3 owned_present=3 pinned_present=3 owned_zombies=0 utc=2026-09-06T08:46:14Z

FIXTURE _scan_header("after") for the identical 3-row body (T:304-310, T:331):
# process-scan v2.3 mode=after rows=50 buzz_acp_pid=12300 buzz_present=1 owned=3 owned_present=3 pinned_present=0 owned_zombies=0 utc=2026-09-05T12:00:00Z
                                                                                                  ^^^^^^^^^^^^^^^^^
```

**Diff: `pinned_present=0` (fixture) vs `pinned_present=3` (producer)** for the same body. `rows`/`buzz_acp_pid`/`utc` differ legitimately per run. The clean-shutdown shape matches:

```
PRODUCER after kill:   # process-scan v2.3 mode=after    rows=92 buzz_acp_pid=18034 buzz_present=0 owned=3 owned_present=0 pinned_present=0 owned_zombies=1 utc=…
PRODUCER teardown:     # process-scan v2.3 mode=teardown rows=92 buzz_acp_pid=18034 buzz_present=0 owned=3 owned_present=0 pinned_present=0 owned_zombies=1 utc=…
FIXTURE  shutdown/teardown: same field pattern (rows=50, buzz_pid=12300, owned=3)
```

Producer/consumer semantic mismatch worth noting: the producer computes `owned_present = len(owned & table_pids)` over the **full** ps table (`pc_post.sh:66`), while the checker compares it to the count of **body** rows (`C:1108`). They diverge whenever an owned process's cmd contains `pc_post.sh` or ` ps -eo ` (dropped by `pc_post.sh:63` but still counted). Not reachable today; latent.

---

## PASTED SUMMARY LINES

Lane suite = `tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_audit_cp5_controls.py tests/test_s0_01_pc_post_scan.py`, `-q -p no:randomly`, dedicated `--basetemp`, post-ENOSPC:

```
241 passed, 5 skipped in 672.76s (0:11:12)      # run 1, tmp footprint 4.7 G
241 passed, 5 skipped in 659.32s (0:10:59)      # run 2, tmp footprint 4.7 G
```

Combined 24-guard mutant, same command:

```
3 failed, 238 passed, 5 skipped in 657.79s (0:10:57)
```

Real-leg subset: `41 passed, 5 skipped in 10.57s`.
`python3 -m pyflakes` over `check_acp_conformance.py`, the three test files, `pins.py`, `negative_contract.py`: **rc=0, no output**.

---

## WHAT I REPRODUCED vs REVIEWED STATICALLY vs SKIPPED

**Reproduced (ran on my copy):** all nine audit-blocker replays; all 17 A5b survivors individually; every finding F10–F32 as a hostile bundle through `check_bundle`; the FIFO hang end-to-end through the CLI; the A24/A23/A25 controls; the combined 24-guard mutant against the full lane suite; the producer standalone header diff; the 5-F17 restore probe; the real-corpus run; both suite runs; pyflakes; the tree-integrity diff.

**Reviewed statically only:** `frame_tee.py:148-166` key set vs `_TEE_STATUS_KEYS` (F34) — read, not executed; the 21-survivor attribution rests on the combined mutant plus the zero-assertion grep rather than 21 individual runs (sound in the fail-closed direction: disabling guards can only remove failures, and the three reds are all closure assertions).

**Deliberately skipped:** re-running the round-4 65-attack harness (its work trees were deleted in the disk cleanup; I re-graded the 17 named survivors directly instead, which is stronger per-item evidence). The audit's backend credential-redaction P1 and the `frame_tee.py` drain P2 at producer level — lanes D5/B5 files, outside my scope and dirty in the shared tree; I graded only the checker's *consumption* of `tee-status.json`. Individual one-at-a-time runs for the 21 survivors — cost, see above. Anything executed in the shared working tree.

---

## VERDICT: **NOT-READY**

Blocking ids: **R7-CK-F1, F2, F3, F4, F5** (the audit's own P1 repairs for two-users concurrency and terminal cardinality, plus the A23 frame classes, all shipped with zero regression tests — a single edit silently re-opens three audit blockers), **F10, F11, F13** (A20 v2.3 rules 4 and 5 unenforced: a live pinned-tee process after shutdown/teardown is accepted, and an empty declared owned set makes the shutdown cleanup proof vacuous), and **F19** (a FIFO in the evidence tree hangs the checker with no timeout).

Second tier, not individually blocking but all real: F6–F9 (untested teardown-header, identity-ppid, A21d and golden rules), F12, F14–F18, F20–F21 (evidence-tree entry discipline), F33–F37 (fixture provenance and A28 exact-reason discipline), F42.

This verdict does not depend on anything I failed to reproduce. The one claim resting on reading rather than execution is F34 (`frame_tee.py` key set currently matching `_TEE_STATUS_KEYS`), and that reading makes the finding *milder*, not stronger.