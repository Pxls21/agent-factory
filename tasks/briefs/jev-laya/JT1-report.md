# JT1 report: the programmable Jev tool and the hiccup tracker (task #221 steps 1-2)

| Field | Value |
|---|---|
| Lane | JT1, sandbox code-implementer, `claude-opus-5-5` |
| Brief | `tasks/briefs/jev-laya/JT1-brief.md` |
| PIN | local HEAD `b683db7` (branch `claude/soundbox-kit-migration-iz1jwf`), shared tree, no worktree |
| Started | 2026-09-24T12:22:56Z (`date -u`) |
| Status | DONE 13:3xZ: A1-A8 evidenced below; gates green (77 passed x2); NOT done: the real server's cold start/stop, the live PC check (the coordinator's) |

## 0. Premise re-measured (12:21Z, before any code)

```
$ git rev-parse --short HEAD
b683db7
$ git log --oneline 4e3bdde..b683db7
b683db7 briefs: JT1, the programmable Jev tool and the hiccup tracker (task #221 steps 1-2); .jev/ ignored
$ git diff --stat 4e3bdde b683db7 -- scripts/laya_systemone_server.py scripts/transcript_export.py scripts/pc_bridge_exec.py scripts/gate_files.txt scripts/no_laya_in_gates.py scripts/lint_delta.py .gitignore
 .gitignore | 3 +++
$ grep -c -E 'jev|hiccup' scripts/gate_files.txt
0
$ grep -n -E '^def (scrub|turns|export)|^SECRET_PATTERNS' scripts/transcript_export.py
56:SECRET_PATTERNS = [
85:def scrub(text: str) -> str:
91:def turns(path):
116:def export(transcript: str, out: str, cap: int) -> list:
$ grep -n -E '^def run' scripts/pc_bridge_exec.py
22:def run(cmd: str, url: str, token: str, attempts: int = 3, max_time: int = 110):
$ grep -n -E '^def _chunk_map|^def _answer' scripts/laya_systemone_server.py
118:def _chunk_map(state):
130:def _answer(state, questions):
$ ls -la /root/.claude/projects/-home-user/*.jsonl ; ls .../*/subagents | wc -l
-rw------- 1 root root 662019691 Sep 24 12:21 /root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl
469
$ free -m | head -2 ; nproc
Mem:           16095        7074        1388          12        7976        9021
4
$ cat .jev/server.pid ; ps -o pid,ppid,etime,args -p 30467
30467
30467 30462       06:56 /root/venv-laya-probe/bin/python scripts/laya_systemone_server.py --threads 2 --device cpu
$ curl -s -m 5 127.0.0.1:47411/health        (real 0m0.018s)
{"ok": true, "snapshot": "/root/hf-laya-probe/hub/models--convaiinnovations--laya/snapshots/1c5edc17a7acd8701df6fc341c0d179f1c62c982", "subfolder": "typed-decisions", "calls": 16, "device": "cpu", "device_reason": "cpu explicitly requested", "revision": "1c5edc17a7acd8701df6fc341c0d179f1c62c982"}
$ ls -la .jev/
drwx------  2 root root 4096 Sep 24 12:16 .
-rw-r--r--  1 root root 1966 Sep 24 12:18 server.log
-rw-r--r--  1 root root    6 Sep 24 12:16 server.pid
```

Verdict: the premise holds. HEAD moved 4e3bdde -> b683db7 with only the brief and `.gitignore` (`.jev/`); every cited seam
line is unchanged; the server (pid 30467) answers `/health` in 18 ms. Drift that does not change the design: the transcript
grew (661,840,993 -> 662,019,691 bytes), subagent transcripts 467 -> 469, free memory 14,779 -> 9,021 MB available.
The server's `main()` loads the model BEFORE `serve_forever()` (server lines 216-226), so `/health` does not answer at all
during the ~123 s load; D-3's "answers within 1 s" therefore means "a loaded server is up".

Baseline gates before any file of mine existed:

```
$ python3 scripts/no_laya_in_gates.py ; echo rc=$?
no_laya_in_gates: 40 files scanned, clean
rc=0
$ python3 scripts/lint_delta.py --base HEAD ; echo rc=$?
lint_delta (worktree vs HEAD): 3 .py changed, 0 NEW pyflakes hit(s), 0 removed
  (two advisory AP tells, both on the other agent's files: volatile.py AF-AP-152, test_decisions_canonical.py AF-AP-39)
rc=0
```

## Discrepancies (running list)

- **DISC-1 `lint_delta.py --base HEAD` cannot see an untracked file.** It enumerates files with
  `git diff --name-only --diff-filter=ACMR HEAD` (`scripts/lint_delta.py:78`), which lists tracked changes only. Every file of
  this lane is untracked (the coordinator commits), so the brief's lint gate is vacuous for them. I run it as named AND run
  pyflakes directly over my files (the same checker lint_delta wraps; a new file's base has no hits, so every hit is new). I do
  NOT `git add -N` (it would stage entries in the shared index that `safe_commit.sh` refuses on).

## A1 — live runs against the REAL local server (pid 30467, `--venue local`), 12:48-12:49Z

```
$ python3 scripts/jev.py health --venue local
{"cmd": "health", "health": {"calls": 16, "device": "cpu", "device_reason": "cpu explicitly requested", "ok": true, "revision": "1c5edc17a7acd8701df6fc341c0d179f1c62c982", "snapshot": "/root/hf-laya-probe/hub/models--convaiinnovations--laya/snapshots/1c5edc17a7acd8701df6fc341c0d179f1c62c982", "subfolder": "typed-decisions"}, "latency_ms": 3.3, "venue": "local"}
rc=0

$ Q=$'Exit code 1\nFileNotFoundError: [Errno 2] No such file or directory: \'/tmp/ps/bt\' (pytest --basetemp parent missing)'
$ time python3 scripts/jev.py rank --venue local --query "$Q" --instructions "Does this note explain or fix the error in the query?" \
    --chunk "<the eight CLAUDE.md quirk notes of the premise probe jev_measure2.py, in its order c0..c7>"
{"cmd": "rank", "fan_out": 8, "latency_ms": 3783.6, "ranking": [["c0", 0.5643], ["c7", 0.4823], ["c5", 0.465], ["c1", 0.3825], ["c4", 0.3784], ["c6", 0.3348], ["c3", 0.3125], ["c2", 0.2165]], "server_latency_ms": 3780.7, "venue": "local"}
real	0m3.858s
rc=0

$ time python3 scripts/jev.py ask --venue local --state "$Q" --instructions "Is this error caused by the test environment setup rather than by the code under test?"
{"answer": {"action": {"act_probability": 1.0}, "confidence": 0.5337, "noul": 0.5337, "type": "noul"}, "cmd": "ask", "latency_ms": 384.5, "server_latency_ms": 381.5, "venue": "local"}
real	0m0.461s
rc=0

$ time python3 scripts/jev.py classify --venue local --state "$Q" --label "tooling or environment quirk" --label "code bug" --label "flaky test" --instructions "Which class of problem does this tool error belong to?"
{"choice": "code bug", "cmd": "classify", "confidence": 0.0025, "latency_ms": 427.8, "probabilities": {"code bug": 0.3604, "flaky test": 0.3389, "tooling or environment quirk": 0.3007}, "server_latency_ms": 424.5, "venue": "local"}
real	0m0.504s
rc=0

$ time python3 scripts/jev.py health --venue local
{"cmd": "health", "health": {"calls": 19, ...same fields...}, "latency_ms": 2.6, "venue": "local"}
real	0m0.079s
rc=0
```

Read-off (verified): `rank` returns `fan_out` 8 = the chunk count, and its eight scores are IDENTICAL to the coordinator's premise
measurement at 12:17Z (c0 0.5643, c7 0.4823, c5 0.4650, c1 0.3825, c4 0.3784, c6 0.3348, c3 0.3125, c2 0.2165): the client
speaks D-1's list form and the server fanned out. The server's `calls` counter moved 16 -> 19 (one per POST: rank, ask,
classify). `classify` answered, but nearly flat (0.36 / 0.34 / 0.30, confidence 0.0025): the same weakness D-2 records.

The real call log after these runs (`.jev/`, printed by field, never the state):

```
$ stat -c '%a %n' .jev .jev/calls.jsonl
700 .jev
600 .jev/calls.jsonl
2026-09-24T12:48:20.799203Z health local 0 [] - 3.3 True None answers: None keys: answers,cmd,latency_ms,n_questions,ok,qtypes,reason,state_sha256,ts,venue
2026-09-24T12:49:36.274093Z rank local 8 ['noul'] f8aa2b5028ca 3783.6 True None answers: 8 keys: (same ten)
2026-09-24T12:49:46.534250Z ask local 1 ['noul'] 671d9da2d9dc 384.5 True None answers: 1 keys: (same ten)
2026-09-24T12:49:46.997261Z classify local 1 ['choice'] 671d9da2d9dc 427.8 True None answers: 1 keys: (same ten)
2026-09-24T12:49:47.502234Z health local 0 [] - 2.6 True None answers: None keys: (same ten)
$ grep -c -E 'FileNotFoundError|basetemp|pytest' .jev/calls.jsonl
0
```

`jev_local.sh` against the adopted server (no second start):

```
$ bash scripts/jev_local.sh status ; echo rc=$?
{"ok": true, "snapshot": "...1c5edc17...", "subfolder": "typed-decisions", "calls": 16, "device": "cpu", ...}
rc=0
$ bash scripts/jev_local.sh start ; echo rc=$?
jev_local: already running: {"ok": true, ...}
rc=0
$ cat .jev/server.pid ; ps -o pid,etime,args -p 30467
30467
30467       34:44 /root/venv-laya-probe/bin/python scripts/laya_systemone_server.py --threads 2 --device cpu
$ bash scripts/jev_local.sh bogus ; echo rc=$?
jev_local: usage: jev_local.sh start [--threads N] | stop | status
rc=64
```

## Test build notes (red first, then green)

- `tests/test_jev_client.py` first run (12:5xZ): `4 failed, 43 passed in 15.01s`. All four were the bind-warning cases
  (`status-line`, `data-line`, PC health, auto fallback): the warning regex's optional path prefix was `\S*`, which is
  greedy and ate the `200` status digits glued before `/home/...` (and, on the data line, the JSON's closing characters).
  This is a real defect the test found, not a test bug. Fix: the prefix starts at `/` and holds only `[A-Za-z0-9._/-]`
  (`scripts/jev.py`, `_BIND_WARNING`). Re-run: `47 passed in 16.94s`.
- The AF-AP-33 tell on `jev_local.sh` (health-only liveness): `healthy()` now also requires `"revision":
  "1c5edc17..."` in the health JSON, so a squatter on port 47411 does not count as this server. Re-checked live: `status`
  and `start` still recognise the adopted server (rc 0, "already running").

## A6 — `hiccup_scan.py` over the live transcripts (13:11Z)

The transcripts grow while agents work, and the disk had 834 MB free (98% used), so a 1.2 GB snapshot was impossible.
The inputs were frozen instead: the main transcript is append-only, so `--limit-bytes` at its size pins its bytes; the
subagent files written in the last 30 minutes (5) were copied, mode kept, into a scratch `subagents/` dir (deleted
after); the other 232 files were passed as they are, and their (path, size) fingerprint was taken before and after
both runs. Script: the lane's scratch `a6.sh`.

```
main limit=665166663 files=238 active-copied=5
inputs fingerprint before: 556afb30139611d1
13:11:27Z
hiccup_scan: files=238 bytes=991613899 lines=201293 unparsable=18 assistant_usage_model=77946 tool_use=37822 tool_result=37810 errors=670 clusters=400 uncovered=16 task_reminder=1777 silent_turn_reminder=1094 compactions=121 refusal_stops=27 clock=2026-09-24T13:11:24Z page=<out> page_bytes=27600 sha256=40e575a518a651735fd3da31087cf7a00a6ba554763c3117b94b9d8ee939488e
run1 wall=10.705s
hiccup_scan: files=238 bytes=991613899 lines=201293 unparsable=18 assistant_usage_model=77946 tool_use=37822 tool_result=37810 errors=670 clusters=400 uncovered=16 task_reminder=1777 silent_turn_reminder=1094 compactions=121 refusal_stops=27 clock=2026-09-24T13:11:24Z page=<out> page_bytes=27600 sha256=40e575a518a651735fd3da31087cf7a00a6ba554763c3117b94b9d8ee939488e
run2 wall=10.046s
inputs fingerprint after:  556afb30139611d1
40e575a518a651735fd3da31087cf7a00a6ba554763c3117b94b9d8ee939488e  /tmp/jt1/a6-run1.md
40e575a518a651735fd3da31087cf7a00a6ba554763c3117b94b9d8ee939488e  /tmp/jt1/a6-run2.md
cmp: identical
27600
```

Secret check on that live page against the REAL bridge values (read in-process; only booleans printed):

```
bridge token on page: False
bridge host on page: False
trycloudflare on page: False | sk- keys: 0 | ghp_: 0 | Bearer + token: 0
20+ identifier runs on the page: ['mcp__Exa__web_search_exa', 'mcp__github__actions_list', 'mcp__github__actions_run_trigger', 'mcp__github__get_job_logs', 'mcp__github__issue_read']
$ LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' /tmp/jt1/a6-run1.md
0
```
(The five 20+ runs are tool names in the context-cost and cluster tables, not excerpts; D-11 normalizes excerpts.)

Peak memory of one full live scan (238 files, 991 MB): `child maxrss 36 MB`, wall 28.7 s on the contended box
(10.0-10.7 s above; 9.9 s at 12:39Z).

**Incident on the way (unexplained, not caused by the scan):** the first A6 attempt at 13:10Z returned `Exit code 137`
(SIGKILL) with no output after run 1 had written its page. The kernel log holds no OOM or kill record (its only event is a
bash segfault 22 hours earlier), the scanner peaks at 36 MB, and the Laya server (pid 30467) was untouched. Free memory
was 5.6 GB of 16 GB then, with other agents running. The retry above ran clean.

The fixture (A6's exact-count half) is `tests/test_hiccup_scan.py`: `MAIN` (28 lines) and `SUB` (4 lines) mirror the
measured key shapes (assistant `message.{model,usage,stop_reason,id}` + `requestId`; user `tool_result` blocks with
`is_error` and the record's `toolUseResult.agentId`; `attachment.{type: task_reminder, itemCount, content}` and
`{type: silent_turn_reminder, text}`; `system/compact_boundary` with `compactMetadata`; a refusal record whose content is
a lone `thinking` block, as in the live data; subagent records with `agentId` and `isSidechain: true`). Hand-derived exact
counts: 13 assistant records with usage and model, 11 tool_use, 11 tool_result, 9 errors, 1 task_reminder, 1
silent_turn_reminder, 1 compaction, 1 refusal stop, 3 malformed lines (truncated JSON, a JSON list, invalid UTF-8)
counted, never a crash.

## A7 — `--jev` on the live page (13:13Z), local venue only

```
$ time python3 scripts/hiccup_scan.py --jev --jev-venue local --out docs/HICCUPS.md
A7 wall=43.405s
hiccup_scan: files=238 bytes=992096506 lines=201436 unparsable=18 assistant_usage_model=78019 tool_use=37854 tool_result=37841 errors=671 clusters=401 uncovered=16 task_reminder=1777 silent_turn_reminder=1094 compactions=121 refusal_stops=27 clock=2026-09-24T13:13:53Z page=docs/HICCUPS.md page_bytes=27917 sha256=dd993ed1d9baabd735dff70a58f60787fcfd5946092b1615da1aa1967a3d948e jev: uncovered_in_top=4 filled=4 run_s=32.0
```
(`uncovered_in_top` was renamed `uncovered_shown` right after this run: it counts the UNCOVERED rows of both cluster
tables. Page bytes do not depend on that stdout label.)

The four UNCOVERED rows the page shows, with the advisory cell (live Laya answers; unvalidated suggestions, KC-J1b):

```
| 22 | `failed to get job logs: failed to download log content for job N: failed to download logs: HTTP N` | UNCOVERED | - | 3 | ... | mcp__github__get_job_logs | CLAUDE.md:420 0.5146 |
| `failed to cancel workflow run: POST U N Resource not accessible by integration []` | UNCOVERED | 3 | 2026-09-23 06:14 | mcp__github__actions_run_trigger | AF-AP-102 0.4222 |
| `File content (N tokens) exceeds maximum allowed tokens (N). Use offset and limit parameters ...` | UNCOVERED | 2 | 2026-09-18 14:27 | Read | AF-AP-104 0.4558 |
| `` pdftoppm is not installed. Install poppler-utils (...) to enable PDF page rendering. `` | UNCOVERED | 2 | 2026-09-24 02:13 | Read | AF-AP-58 0.2789 |
```

Read-off: the column filled for all 4 UNCOVERED clusters the page shows (1 in the top-25 table, 3 in "new this week"); 16
clusters are UNCOVERED in all, and the other 12 are not on the page. The suggestions look weak on inspection (e.g.
CLAUDE.md:420 is the post-push PIN quirk, for a GitHub log download error); that is what "advisory" means here, and it
matches the audit's point that Jev must be measured (step 3) before anyone reads its column as a classification.

KC-J1b on live data (13:14Z, `a7kc.sh`: one frozen input set, a plain run and a `--jev` run):

```
hiccup_scan: files=238 bytes=992317515 lines=201511 ... page_bytes=27603 sha256=0ef3177a46c8135444bd73f222aec55c8e88628b71c686f8689ea25714a3cb9b
hiccup_scan: files=238 bytes=992317515 lines=201511 ... page_bytes=27906 sha256=e1c340e6f716f9ecd1ba66ce1033862e107f272a8ea4f27b20bb3bed8b283602 jev: uncovered_shown=4 filled=4 run_s=26.4
jev run wall=35.215s
jev page differs from plain: True | column headers: 2
KC-J1b: jev page minus the advisory column == plain page: True
```
(The script's (path, size) fingerprint moved between before and after because it includes the main transcript's full size,
which grew while the scans read only up to the byte limit; both stats lines show the same bytes, lines and counts.)

## A8 — mutants on scratch copies (13:22-13:27Z)

Runner: the lane's scratch `mutants.py` copies the 12 files the two test files need into its own directory per mutant
(`/tmp/jt1/mut/<id>/`), applies ONE string replacement (anchor count asserted == 1), and runs both test files there. The
tracked tree is never touched (`git status` before and after: only this lane's untracked files and the other agent's).

```
PRISTINE rc=0 76 passed in 20.70s failed=[]
M1 drop the scrub (jev) | rc=1 | 3 failed, 73 passed | killed by: test_a_secret_straddling_the_cap_never_reaches_the_request[named-token], [sk-key], test_every_scrubber_class_is_removed_from_every_text_sent
M2 cap before scrub (jev) | rc=1 | 2 failed, 74 passed | killed by: test_a_secret_straddling_the_cap_never_reaches_the_request[named-token], [sk-key]
M3 log the state text (jev) | rc=1 | 1 failed, 75 passed | killed by: test_call_log_never_holds_the_state_and_has_the_modes
M4 wall-clock header in the page (hiccup) | rc=1 | 2 failed, 74 passed | killed by: test_same_input_bytes_give_the_same_page_bytes_and_no_wall_clock, test_the_jev_column_is_advisory_and_changes_nothing_else
M5 no bind-warning strip (jev PC path) | rc=1 | 5 failed, 71 passed | killed by: test_auto_falls_back_to_the_pc_when_local_is_refused_or_slow, test_pc_health_is_a_curl_get_on_the_pc_loopback, test_pc_path_...[data-line], [leading], [status-line]
M6 no per-chunk fan-out guard (jev rank) | rc=1 | 1 failed, 75 passed | killed by: test_rank_refuses_a_reply_without_per_chunk_fan_out
M7 excerpt without the scrub (hiccup) | rc=1 | 2 failed, 74 passed | killed by: test_fake_secrets_never_reach_the_page, test_page_rows_are_exact
M8 chunks sent as a dict, the rejected D-1 form (jev) | rc=1 | 11 failed, 65 passed | killed by: test_rank_sends_the_list_form_with_one_noul_question_per_chunk, test_rank_keeps_caller_ids_and_the_cli_prints_one_json_line, + 9 more
M9 Jev column asks for covered clusters too (hiccup) | rc=1 | 2 failed, 74 passed | killed by: test_jev_unavailable_says_na_with_the_reason_and_stops_asking, test_the_jev_column_is_advisory_and_changes_nothing_else
M10 call log file mode 0644 (jev) | rc=1 | 1 failed, 75 passed | killed by: test_call_log_never_holds_the_state_and_has_the_modes
M11 the pinned server revision is not checked (jev_local.sh) | rc=1 | 1 failed, 75 passed | killed by: test_jev_local_does_not_count_a_squatter_on_its_port_as_its_server
M12 stop trusts any pid in the pidfile (jev_local.sh) | rc=1 | 1 failed, 75 passed | killed by: test_jev_local_start_is_idempotent_and_stop_kills_only_its_pid
M13 an apostrophe opens a quoted string (hiccup) | rc=1 | 1 failed, 75 passed | killed by: test_an_apostrophe_is_not_a_quote_but_a_long_quoted_string_is
```
(The summaries above are cut to the kill lists; the full lines are in the runner's log, `/tmp/jt1/mutants.log`.)

The four mutants the brief names are M1-M4: each turned the named tests red. History that matters:
- The first table (13:05Z, 11 mutants) had M11 SURVIVE: the revision check added for the AF-AP-33 tell had no test.
  `test_jev_local_does_not_count_a_squatter_on_its_port_as_its_server` was added and kills it.
- The second table (13:16Z) was VOID: its PRISTINE control was red (`1 failed, 75 passed`) because my new apostrophe
  test asserted a phrase past the 160-character cut. Every "kill" in that table was that one broken test. The test was
  corrected (the line now fits under the cut, with a 52-character span between the apostrophes) and the table re-run
  green above. Without the pristine control this would have read as 13 kills.

## A2-A5 — the unit evidence (`tests/test_jev_client.py`, 49 tests), mapped to the contract

`python -m pytest tests/test_jev_client.py -v --basetemp /tmp/jt1/bt -p no:cacheprovider` (13:28Z): `49 passed in 19.26s`,
every test PASSED by name. The HTTP test double RECORDS each request (method, path, headers, body bytes); its replies
only carry the server's shape and are never a claimed model answer (the live answers are A1).

- **A2 fail-open.** `test_failure_is_exit_3_with_one_reason_line_and_none_from_the_api[http500|http503|non-json|timeout|nan]`
  and `test_connection_refused_is_exit_3_and_none`: the CLI exits 3, stdout is empty, stderr is exactly one line
  (`jev: unavailable: url: HTTP 503 (model not loaded)`, `... url: non-JSON reply`, `... url: timeout after 0.5s`,
  `... url: connection refused`, and a NaN noul refused), and the import API returns `None` with `jev.last_reason` set.
  `test_usage_errors_exit_64_and_send_nothing[9 cases]` (exit 64, the double records 0 requests, incl. a non-loopback
  `--url`) and `test_import_api_never_raises_on_bad_input`. Live, without the model:
  ```
  $ python3 scripts/jev.py health --url http://127.0.0.1:<unused port> --no-log ; echo rc=$?
  jev: unavailable: url: connection refused
  rc=3
  $ python3 scripts/jev.py ask --venue pc --bridge-env /nonexistent/none.env --no-log --state s --instructions i ; echo rc=$?
  jev: unavailable: pc: no bridge env file
  rc=3
  $ python3 scripts/jev.py rank --url http://127.0.0.1:47411/ --no-log --query q --chunk a --timeout 0.001 ; echo rc=$?
  jev: unavailable: url: timeout after 0.001s
  rc=3
  $ python3 scripts/jev.py ask --url http://example.com:80 --state s --instructions i ; echo rc=$?
  jev: usage: --url must be http://<loopback host>[:port] (127.0.0.1, localhost or ::1)
  rc=64
  ```
- **A3 scrub then cap.** `test_a_secret_straddling_the_cap_never_reaches_the_request[named-token|sk-key]`: the cap cuts
  7 characters into the secret's value (below the named-value floor of 8 and the sk- floor of 12); the recorded request
  bodies of an `ask` state and a `rank` query and chunk hold none of those 7 characters, and each text is exactly the cap
  long (the cap did apply). `test_every_scrubber_class_is_removed_from_every_text_sent`: all ten scrubber classes of
  `tests/test_transcript_export.py` (fake values) planted in state, query, chunk, instructions and a label; none is sent.
  Killed mutants: M1 (drop the scrub), M2 (cap before scrub).
- **A4 the call log.** `test_call_log_never_holds_the_state_and_has_the_modes`: a marker sent 4 times (the request bodies
  prove it left) is absent from the log; dir `0o700`, file `0o600`; each line has exactly the ten D-6 keys; each
  `state_sha256` equals the sha256 of the canonical JSON of the state AS RECORDED by the double. Live: see A1 (700/600,
  0 state-text matches). `test_a_failed_call_is_logged_with_its_reason_and_no_log_writes_nothing`. Killed: M3, M10.
- **A5 the PC path.** `test_pc_path_sends_the_request_base64_encoded_and_survives_the_bind_warning[none|status-line|
  data-line|leading]` with an injected runner and a fake env file: the runner receives the fake link and token, the
  command holds neither, the request decodes from the command's base64 exactly, `attempts=1`, and a reply with the real
  warning text (`/home/rocco/.local/share/tirith/shell/lib/bash-hook.bash: line 12: bind: warning: line editing not
  enabled`, the shape seen in the live transcripts) glued to the status line, the data line or leading still parses.
  The runner's stderr (which could name the bridge link) never surfaces. `test_pc_failures_fail_open[5 cases]`,
  `test_pc_without_a_bridge_env_is_unavailable_and_never_runs`, `test_auto_prefers_a_healthy_local_endpoint`,
  `test_auto_falls_back_to_the_pc_when_local_is_refused_or_slow` (a /health slower than 1 s falls through, D-3).
  Killed: M5. The real bridge was never called by this lane. The command the bridge would run (sample request):
  ```
  printf %s 'eyJtb2RlbCI6ICJsYXlhIiwg...fX19' | base64 -d | curl -sS --noproxy '*' -m 30 -H 'Content-Type: application/json' --data-binary @- -w '\n%{http_code}\n' http://127.0.0.1:47411/v1/systemone
  curl -sS --noproxy '*' -m 1 -w '\n%{http_code}\n' http://127.0.0.1:47411/health
  ```
- **D-7 `jev_local.sh`.** Live: status and idempotent start against the adopted server (A1 block). Tests:
  `test_jev_local_start_is_idempotent_and_stop_kills_only_its_pid` runs the real launcher logic on a scratch copy (spare
  port, `PY` = this python) against a STAND-IN process named `laya_systemone_server.py` that answers `/health` only (404
  elsewhere) and never a model question: `start` writes the server's own pid, a second `start` while it loads says
  `already starting`, the server got `--device cpu --threads 3 --host 127.0.0.1 --port <p> --hf-home /root/hf-laya-probe`,
  `stop` kills that pid and removes the pidfile, and a pidfile naming a foreign process is removed without signalling
  it. `test_jev_local_does_not_count_a_squatter_on_its_port_as_its_server`, `..._names_a_missing_snapshot_and_reports_down`
  (exit 2, one line naming the path), `..._usage_errors_exit_64[6]`. Killed: M11, M12.

## Independent cross-check of the port against E4.3 (13:32Z)

The evidence lane's own parser (`jev_e4e5.py` / `jev_e5_side.py`, E4.3) printed exact counts for the main transcript's
first 651,687,566 bytes. The file is append-only and `--limit-bytes` keeps E4.3's stopping rule, so the port must match:

```
$ python3 scripts/hiccup_scan.py --transcript /root/.claude/projects/-home-user/bdab799a-...jsonl --limit-bytes 651687566 --out /tmp/jt1/e43.md
hiccup_scan: files=1 bytes=651687566 lines=114378 unparsable=8 assistant_usage_model=35505 tool_use=16736 tool_result=16730 errors=239 clusters=155 uncovered=9 task_reminder=1739 silent_turn_reminder=1064 compactions=118 refusal_stops=20 clock=2026-09-24T11:19:32Z page_bytes=11627 sha256=11acf74096ac8d579c77054573936f5f43221623a7ddd61c3ec1098dfbf84e2d
`task_reminder` attachments: 1739 records, 289208111 bytes, 44.4% of all bytes parsed.
Errors by family: exit code N 100, harness blocked a foreground sleep 28, auto-mode denial 23, Terminated (SIGTERM) 20, missing path 17, UNCOVERED 14, edit anchor 11, python exception 10, input validation 8, ripgrep timeout 4, cwd is not the repo 2, user declined 2.
```

| Count | E4.3 (published) | port | |
|---|---:|---:|---|
| bytes parsed / lines / unparsable | 651,687,566 / 114,378 / 8 | 651,687,566 / 114,378 / 8 | same |
| tool calls / tool results / errors | 16,736 / 16,730 / 239 | 16,736 / 16,730 / 239 | same |
| `task_reminder` records, bytes, share | 1,739 / 289,208,111 / 44.4% | 1,739 / 289,208,111 / 44.4% | same |
| `silent_turn_reminder` / compactions | 1,064 / 118 | 1,064 / 118 | same |
| sleep blocks / auto-mode denials / input validation / ripgrep / user declined / edit anchor | 28 / 23 / 8 / 4 / 2 / 11 | 28 / 23 / 8 / 4 / 2 / 11 | same |
| `Exit code N` (E4.3: one family) | 149 | 100 + 20 + 17 + 10 + 2 = 149 (exit code N, Terminated, missing path, python exception, cwd) | same total |
| "other (GitHub MCP/API and misc)" | 14 | UNCOVERED 14 | same |

## Gates (final, 13:30-13:31Z, HEAD 27374ec; set `2 files set=3aca4dc1e88c` = tests/test_jev_client.py tests/test_hiccup_scan.py)

```
$ mkdir -p /tmp/jt1
$ python -m pytest tests/test_jev_client.py tests/test_hiccup_scan.py -q --basetemp /tmp/jt1/bt      (run 1)
77 passed in 20.63s
run1 rc=0
$ python -m pytest tests/test_jev_client.py tests/test_hiccup_scan.py -q --basetemp /tmp/jt1/bt      (run 2)
77 passed in 21.03s
run2 rc=0
$ python3 scripts/lint_delta.py --base HEAD ; echo rc=$?
lint_delta (worktree vs HEAD): 3 .py changed, 0 NEW pyflakes hit(s), 0 removed
rc=0      (its 2 advisory tells are on the other agent's volatile.py and test_decisions_canonical.py; see DISC-1:
           it does not see this lane's untracked files at all)
$ python3 scripts/no_laya_in_gates.py ; echo rc=$?
no_laya_in_gates: 40 files scanned, clean
rc=0
$ python3 -m pyflakes scripts/jev.py scripts/hiccup_scan.py tests/test_jev_client.py tests/test_hiccup_scan.py ; echo rc=$?
rc=0      (the real lint check for this lane's files; DISC-1)
$ bash -n scripts/jev_local.sh ; echo rc=$?
rc=0
$ for f in <the 7 lane files + docs/HICCUPS.md>; do LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' $f; done
0 (each file)
```

Earlier runs, for the record: 73 passed x2 at 13:00Z (before the squatter, stand-in, apostrophe and import-guard
tests); 74, 76 and 77 as tests were added. The count moved only by added tests; no test was removed or skipped.

## Files (all CREATED; nothing modified)

| File | Lines | What |
|---|---:|---|
| `scripts/jev.py` | 546 | client + CLI. `_prep` :91 (scrub, then cap), `_build` :141 (D-1 list form, D-2 choice), `_result` :201 (fan-out and answer checks), `_http` :243, `pc_command` :306, `parse_pc_reply` :318, `_BIND_WARNING` :74, `_pc` :342, `_ask_venues` :361 (D-3 order), `_write_log` :385, `_call` :400 (D-6 line), import API :436-460, `main` :479 |
| `scripts/jev_local.sh` | 126 | `healthy` :25 (ok + pinned revision), `alive` :33, `our_pid` :39 (pidfile pid alive and is the server), `cmd_start` :48, `cmd_stop` :88, `cmd_status` :111 |
| `scripts/hiccup_scan.py` | 685 | `excerpt` :77 (D-11), `cluster_key` :89, `load_families` :101, `Scan` :173, `render` :396 (D-12), `build_page` :519, `load_candidates` :550, `lexical_top` :565, `jev_column` :578 (D-10), `main` :623 |
| `scripts/hiccup_families.tsv` | 23 | 14 families (9-line header) |
| `tests/test_jev_client.py` | 607 | 49 tests |
| `tests/test_hiccup_scan.py` | 431 | 28 tests |
| `docs/HICCUPS.md` | 251 | generated 13:13Z by `hiccup_scan.py --jev --jev-venue local` (27,917 bytes) |
| `tasks/briefs/jev-laya/JT1-report.md` | - | this report |

Runtime state (untracked, `.jev/` ignored): `.jev/calls.jsonl` 13 lines (A1 5, A7 4, KC-J1b check 4; all `ok`), dir
700, file 600. The adopted server (pid 30467, `--threads 2 --device cpu`) is still running and healthy.

## Deviations from the brief (each deliberate; flagged for the coordinator)

1. **The advisory Jev column also appears in the "new this week" table** (UNCOVERED rows only). D-10 says "for each
   UNCOVERED cluster"; on the live data only 1 of 16 reaches the top 25, 3 more show under "new this week". KC-J1b holds
   for both tables (test and live check).
2. **One extra line in the error section:** `Errors by family: ...` (a roll-up). The 46 foreground-sleep blocks are 46
   one-event clusters, so without it the family view is invisible outside the per-day columns.
3. **The page does not print the scanned directory's path** (D-8 read strictly: the same bytes under another path give
   the same page). The stats line on stdout names the output path.
4. **Agent rows are trimmed only when the 40,000-byte cap forces it** (oldest first, with a line saying how many). My
   first version capped at 60 rows and hid 51 of 111; all 114 fit today (27.9 KB).
5. **D-11 is applied to agent descriptions too** (they are transcript text), so digits read `N`: `Build JN-N-RN ledger
   repair`. A readability cost; exempting descriptions from the number rule is a one-line change if wanted.
6. **The quoted-string rule skips an apostrophe inside a word** (`(?<![A-Za-z0-9])`): as first written, `don't ...
   user's` became `donSs` on the live page. Test + mutant M13.
7. **`jev.py` extras:** `--log-file`, `--bridge-env` (test seams), `--state-file`/`--query-file`/`--chunks-file`,
   `ask --type/--criterion`; `jev.last_reason` / `jev.last_log_error`; instructions and labels are scrubbed and capped
   too (the brief names state, query, chunk); chunk ids must be `[A-Za-z0-9_.:#-]{1,64}` and scrub-invariant; at most
   64 chunks; a non-loopback `--url` is a usage error (exit 64) before anything is sent; `rank` REFUSES a reply whose
   `fan_out` is not the chunk count (the measured batch-form failure would otherwise pass as a ranking).
8. **`hiccup_scan.py --jev-venue auto|local|pc`** (default auto): this lane used `local` for every live `--jev` run so
   that no path could reach the bridge.
9. **`jev_local.sh`:** `healthy()` also requires the pinned revision (AF-AP-33); `--hf-home` is passed explicitly and the
   HF offline variables are exported; `status` exits 3 when down; `start` reports `already starting` while this server's
   pid is alive and loading (the server answers nothing during its ~123 s load).

## Discrepancies

- **DISC-1** (above) `lint_delta.py --base HEAD` enumerates `git diff --name-only --diff-filter=ACMR HEAD`
  (`scripts/lint_delta.py:78`), which never lists an untracked file, so it cannot gate this lane's files. Measured: none
  of the lane's files appears in its output. Substitute: pyflakes over the four .py files, rc 0.
- **DISC-2 Most families have no covering rule.** 8 of the 14 rows carry `none`: exit code N, foreground-sleep block,
  auto-mode denial, input validation, ripgrep timeout, user declined (6 of the 7 E4.3 families), python exception,
  pytest run red, missing path. The brief's D-9 expects "an AF-AP-<n> id or a short CLAUDE.md phrase" per family; I did
  not invent coverage. The registry search for each is in the lane's transcript (13:0xZ). These are candidates for new
  rows or quirk lines (not this lane's boundary). The 5 rules that exist are checked by a test against the real
  registry / CLAUDE.md text.
- **DISC-3 The E4.3 family patterns meet D-11's normalization.** `InputValidationError` is 20 characters, so the
  normalized line reads `<tool_use_error>T: ...` and E4.3's pattern never matches it (0 events at first). The map's regexes
  are written against the normalized text; measured over every live error: 16 raw `InputValidationError` lines = 16
  normalized `<tool_use_error>T: ` keys, 0 mismatches.
- **DISC-4 The server answers nothing during its ~123 s model load** (`load_agent` runs before `serve_forever`,
  `scripts/laya_systemone_server.py:216-226`): D-3's "health within 1 s" can only mean a loaded server.
  `jev_local.sh start` therefore treats a live pidfile pid as "already starting".
- **DISC-5 HEAD moved under the lane:** b683db7 (PIN) was push-rewritten to 5b51ce2, then eb52e9b, then 27374ec. Among
  this lane's inputs only `docs/INCIDENT-LOG.md` changed (registry rows 182 -> 187); the tests count rows dynamically.
- **DISC-6** The coordinator's ledger says J2 is running and "scoring runs after JT1 frees the local endpoint"
  (commit 2ea5f62). This lane's last Laya use was 13:14Z; `docs/HICCUPS.md` was not regenerated after that so as not to
  load the shared endpoint.
- **DISC-7** An unexplained SIGKILL (exit 137) hit the first A6 attempt (A6 section).

## NOT done

- **The live cold start and stop of the REAL server through `jev_local.sh`.** The lane adopted pid 30467 (D-7: "adopt
  it") and never restarted it: the coordinator's J2 scoring uses it, and a restart costs about 2 minutes of downtime.
  What IS proven: status and idempotent start against the real server (live), and the launcher's own mechanics (setsid
  nohup, the pidfile naming the server's own pid, idempotent start while loading, stop by pid, a foreign pid never
  signalled) against a stand-in process in a scratch copy. The real `start` from cold remains unverified.
- **The PC path live.** Built and unit-tested with an injected runner only; the real bridge was never called (brief: the
  coordinator runs the one live PC check).
- **The Jev column's quality.** 4 live suggestions, unmeasured; they look weak (A7). Step 3 of the audit is the measure.
- The 12 UNCOVERED clusters that are on no table get no Jev cell.
- No new registry rows or quirk lines for the `none` families (DISC-2): outside the boundary.
- `subagents/*.meta.json` (it holds `description`) is not used; descriptions come from the main transcript's Agent call,
  as D-12 says (all 114 live agents in the window joined).
- GitNexus `impact` / `detect_changes`: not run. The lane created new files only and edited no existing symbol; the
  coordinator's commit owns `detect_changes`.
- No commit, no push, no bridge call (standing rules).

## Self-attack: the three most likely ways this is wrong

1. **The fixture mirrors my own parser instead of real data** (a hollow exact-count test). Ruled out by three things.
   The fixture's shapes come from key-shape probes of the live transcripts (message keys, stop_reason values, the
   `toolUseResult.agentId` join, attachment and compactMetadata keys, subagent `agentId`), and its expected numbers are
   hand-derived. The port reproduces E4.3's independently published counts EXACTLY (cross-check above). And the live A6
   run parses 991 MB / 238 files with no crash.
2. **A secret reaches the page or the endpoint.** Ruled out as far as tests can show: every scrubber class planted in
   every text is absent from the request (M1 killed); a secret cut by the cap leaves no stub (M2 killed); the page's
   excerpt path scrubs (M7 killed); the live page holds neither the real bridge token nor its host (checked in-process,
   booleans only). Residual: D-11 normalizes before it scrubs, so a secret shorter than 20 characters with no name, no
   provider prefix and no URL can reach the page with its digits turned to N. The brief pinned that order.
3. **The Jev column leaks into the numbers, or a bad endpoint reply is read as an answer.** KC-J1b: the page minus the
   column equals the plain page (unit test, M4/M9 killed, and the live frozen-input check: True). Bad replies: a missing
   `fan_out` (the measured batch form), NaN, answers for other ids, non-JSON and HTTP errors are all refused with exit 3
   (M6 killed; A2 tests). Residual: the real PC bridge envelope was never seen live. If it differed from
   `{rc, stdout, stderr}`, the PC venue would fail open, not answer wrongly.

## Evidence tiers

- **Verified here (primary source or probe this session):** A1 live answers and latencies; A2-A5 by 49 named tests;
  A6 determinism on live data (two identical sha256), the live page's secret check, and the exact E4.3 cross-check; A7
  live column (4 of 4 filled) and live KC-J1b; A8 13 mutants killed with a green pristine control; the gates pasted above.
- **Inferred:** that the 5 subagent files copied for A6 were the only ones being written (mtime < 30 min); that the
  13:10Z SIGKILL came from outside the scan (no kernel record; 36 MB peak).
- **Assumed:** that the PC's bridge envelope and the PC endpoint match the sandbox contract (never exercised by this lane).
