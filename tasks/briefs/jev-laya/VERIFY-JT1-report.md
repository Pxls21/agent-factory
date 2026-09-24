# VERIFY-JT1 report (task #224, rule 0f)

Role: adversarial-verifier (sandbox, Opus 5.5). PIN: 7d73932 (JT1's files). Local HEAD at start: 161d0f3 (adds the
VERIFY-JT1 brief and a live-state line only; `git diff --stat 7d73932 HEAD` touches no JT1 file).
Started: Thu Sep 24 13:37:41 UTC 2026 (`date -u`).

## 0. Premise re-measured

```
$ for f in ...; do git rev-parse --short=12 7d73932:$f; git hash-object $f; done
e2d02c35ecc8 scripts/jev.py  wt=e2d02c35ecc8
91ff34e0d914 scripts/jev_local.sh  wt=91ff34e0d914
b1eb74892575 scripts/hiccup_scan.py  wt=b1eb74892575
e70eb70948f4 scripts/hiccup_families.tsv  wt=e70eb70948f4
9491dbc0f81c tests/test_jev_client.py  wt=9491dbc0f81c
e37a5a228cb0 tests/test_hiccup_scan.py  wt=e37a5a228cb0
45d4f7ebf6fc docs/HICCUPS.md  wt=45d4f7ebf6fc
$ bash scripts/test_summary.sh tests/test_jev_client.py tests/test_hiccup_scan.py --basetemp /tmp/vjt1/bt
77 passed in 22.48s
pytest-exit: 0
pytest-summary: 77 passed in 22.48s
```

All seven blob ids match the brief's premise block, and the working tree equals the PIN for every JT1 file. 77 passed
matches.

## 1. Gates and contract items reproduced (13:38-13:48Z)

```
$ python3 -m pytest tests/test_jev_client.py tests/test_hiccup_scan.py -q --basetemp /tmp/vjt1/bt -p no:cacheprovider   (run 2)
77 passed in 20.98s
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 40 files scanned, clean                                   rc=0
$ python3 scripts/lint_delta.py --base HEAD
lint_delta (worktree vs HEAD): 0 .py changed, 0 NEW pyflakes hit(s), 0 removed   (JT1 is committed now: vacuous)
$ python3 scripts/lint_delta.py --base 7d73932~1
lint_delta (worktree vs 7d73932~1): 8 .py changed, 0 NEW pyflakes hit(s), 0 removed   rc=0
$ python3 -m pyflakes scripts/jev.py scripts/hiccup_scan.py tests/test_jev_client.py tests/test_hiccup_scan.py   rc=0
$ bash -n scripts/jev_local.sh   rc=0
$ LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <each of the 7 files>   0 0 0 0 0 0 0
```

Gate screen negative control (fixture tree `/tmp/vjt1/gatefx`, one listed gate file):

```
import os                                   -> no_laya_in_gates: 1 files scanned, clean              rc=0
import os; import jev                       -> gate-file-import-unresolved: scripts/g.py:2 imports jev   rc=4
subprocess.run(["python3","scripts/hiccup_scan.py",...])  -> 1 files scanned, clean                   rc=0
```

No listed gate file, hook, workflow or harness script names `hiccup_scan`, `jev_local` or `scripts/jev.py` (grep over the
40 listed files and `scripts/ .github/ harness-ports/ .claude/hooks/`, the other lanes' files excluded: 0 hits).

Scratch root for every live run: `/tmp/vjt1/root` holds byte-identical copies of `scripts/jev.py`, `jev_local.sh`,
`hiccup_scan.py`, `hiccup_families.tsv`, `transcript_export.py`, `pc_bridge_exec.py`, `laya_systemone_server.py`,
`docs/INCIDENT-LOG.md` and `CLAUDE.md` (sorted sha256 lists identical). It has NO `.pc-bridge.env`, so no run of mine can
reach the bridge, the shared `.jev/calls.jsonl` gets no line from me, and `docs/HICCUPS.md` is never overwritten.

A1, live against the real server (pid 30467 on 127.0.0.1:47411, `--venue local`), 13:47-13:48Z:

```
$ python3 scripts/jev.py health --venue local
{"cmd": "health", "health": {"calls": 31, "device": "cpu", ..., "ok": true, "revision": "1c5edc17a7acd8701df6fc341c0d179f1c62c982", ...}, "latency_ms": 3.9, "venue": "local"}   rc=0
$ python3 scripts/jev.py rank --venue local --query 'pytest fails: FileNotFoundError for the --basetemp directory' \
    --chunk 'pytest creates only the last component of --basetemp; mkdir -p its parent first' \
    --chunk 'a trailing & backgrounds the whole && list' --chunk 'sqlite over the bridge: ship the SQL as a base64-decoded script file'
{"cmd": "rank", "fan_out": 3, "latency_ms": 1937.4, "ranking": [["c0", 0.4902], ["c1", 0.179], ["c2", 0.1677]], "server_latency_ms": 1924.9, "venue": "local"}   rc=0 wall=2.04s
$ python3 scripts/jev.py ask --venue local --state '<same query>' --instructions 'Is this error caused by the test environment setup?'
{"answer": {"action": {"act_probability": 1.0}, "confidence": 0.5634, "noul": 0.4366, "type": "noul"}, "cmd": "ask", "latency_ms": 1205.8, ...}   rc=0
$ python3 scripts/jev.py classify --venue local --state '<same query>' --label 'environment quirk' --label 'code bug'
{"choice": "code bug", "cmd": "classify", "confidence": 0.0625, "latency_ms": 780.5, "probabilities": {"code bug": 0.6461, "environment quirk": 0.3539}, ...}   rc=0
$ stat -c '%a %n' .jev .jev/calls.jsonl        -> 700 .jev / 600 .jev/calls.jsonl
  every line: the ten D-6 keys exactly; state_sha256 set for ask/classify/rank, None for health
$ grep -c -E 'basetemp|FileNotFoundError' .jev/calls.jsonl   -> 0
```

`fan_out` 3 equals the chunk count, and the matching note ranks first. A1 holds.

Static check of the answer-echo question (A4): the real answers come from `laya.Agent.system_one`
(`/root/venv-laya-probe/.../laya/agent.py:320-368`): a noul answer holds numbers only, a choice answer holds the labels
(`choice`, `probabilities` keys), a score answer holds the criteria (`legend`). None holds the state. The server's 500 text
is `system_one failed: <type>: <message>`, and the only laya raise on the request path is
`question %r options exceed head_max_len=%d` (question id only; `laya/common.py` raises nothing). So on the real path the
logged `answers` and `reason` cannot carry state text.

## 2. Observations (numbered, no severity filter)

Harnesses (scratch only): `/tmp/vjt1/attack_jev.py`, `attack_failopen.py`, `attack_pc.py`, `attack_local.py`,
`attack_hiccup_secrets.py`, `live_names.py`. Every secret is a fake string.

### The client (`scripts/jev.py`)

**F-1 (INFO, reproduced) A3 holds for every scrubber class at every cut offset.** 13 classes (named `=`, PC_BRIDGE_TOKEN,
X-Agent-Token, Bearer long and short, sk-, ghp_, AIza, xox, `api_key:`, the bridge link, opaque 40+, a PEM block), the cap
set at every offset from the secret's first character to its last, in an `ask` state, a `rank` query and a `rank` chunk:
1,182 calls, 0 value pieces (5+ characters of the value) in the recorded request bytes. Scrub-then-cap is correct by
construction: the scrub sees the whole text, so no cut can re-create a piece.

**F-2 (FOLLOW-UP, reproduced; owner: `transcript_export.scrub`, outside JT1) a list-valued named secret in a dict state is
sent.** `jev.ask({"password": ["hunter2hunter"]}, ...)` sends `hunter2hunter`: `_text` JSON-encodes the dict and scrubs the
JSON, and the named rule's value lookahead stops at `[` (`_V` then `"`). `scrub(json.dumps(state))` alone leaks it too, so jev
applies the scrubber as D-5 says; the gap is the scrubber's. The seven other nested shapes (dict value, a ghp_ dict KEY, a
string, a nested `token`, an int token, a Bearer inside a list, a 5-deep `api_key`) send nothing.

**F-3 (INFO, reproduced) invalid UTF-8 and out-of-range options fail open with an uninformative reason.** A lone surrogate
(import API) or a raw `0xff` byte in argv: nothing sent, no log line, `None` / exit 3 `jev: unavailable: internal error:
UnicodeEncodeError`. `--timeout 1e300` passes `_check_opts` and dies in the socket layer: exit 3 `internal error:
OverflowError` (a usage error by the contract's own split, exit 64). A bridge env file that is not UTF-8: exit 3 `internal
error: UnicodeDecodeError` (no file content in the line). A secret holding a surrogate is still redacted (value class covers
it); `--state-file` with `0xff` is read with `errors="replace"` and sent scrubbed.

**F-4 (FOLLOW-UP, reproduced) a non-`Unavailable` exception stops the venue walk.** `_ask_venues` catches only `Unavailable`.
A local reply of 200,000 nested brackets raises `RecursionError` in `json.loads` (not a `ValueError`); `_http` does not catch
it, so `--venue auto` reports `internal error: RecursionError` and never tries the PC venue. Still fail-open (exit 3, one
line, `None`). Fix: catch `RecursionError` beside `ValueError` in `_http` (the scanner's `feed` already does).

**F-5 (FOLLOW-UP, reproduced) the local venue's `--timeout` is per socket read, not a total deadline.** A double that sends
the headers and then one body byte every 0.25 s answered `ask --timeout 1` after 12.0 s, and the answer was accepted. A
double that sends nothing times out at 1.0 s (correct). The PC venue bounds the total (`curl -m`, runner `max_time`). The real
server writes its body in one call, so this needs a misbehaving endpoint.

**F-6 (INFO, reproduced) `_OPENER` follows redirects.** A `302 Location: http://127.0.0.1:<other port>/elsewhere` from the
`--url` endpoint made jev send a bodiless GET to the other port and accept that port's answer (`noul 0.123`). The POST body is
not forwarded (urllib turns a POST 302 into a GET; 307/308 raise `HTTPError`), so no state leaves; but the `--url` pin and the
"loopback only" comment are not absolute. Fix (defence in depth): build `_OPENER` without `HTTPRedirectHandler`.

**F-7 (INFO, reproduced) `fan_out` compares by `==`.** `fan_out: true` passes for a 1-chunk rank and the CLI prints
`"fan_out": true`; `fan_out: 2.0` passes for 2 chunks. Not material: a 1-chunk batch is a per-chunk call. Rejected correctly:
absent, `None`, `"2"`, 1 or 3 for 2 chunks.

**F-8 (INFO, reproduced) 28 more reply shapes fail open with the import API never raising:** deep nesting (200 and 500),
invalid UTF-8, a 5,000-digit int (`ValueError` at parse), `1e999`, empty 200, a JSON list, answers as a list, an answer as a
string, `noul` true or `"0.5"`, an extra answer id, an unhashable or list `choice`/`probabilities`, HTTP 204, a short body
(`IncompleteRead`), a garbage status line (`BadStatusLine`), a close without reply (`RemoteDisconnected`), no bytes (timeout at
1.0 s). Each: `None` and one reason; the CLI gives exit 3 and exactly one stderr line.

**F-9 (INFO, reproduced) the PC venue keeps the token and link out of every channel I could test** (injected runner, fake
env file with `export` and quotes): not in `sys.argv`, not in `os.environ`, not in a child's environment, not in the command,
not in the call log, not in any reason when the scrubber can see them (a link and a named token are redacted in a remote
stderr); the runner's own stderr never reaches the caller; a runner exception reports only its type. The bind warning
mid-JSON and twice with CRLF still parses; a warning whose path holds a space, a status line followed by a junk line, and
a status glued to the body all fail open (`no HTTP status`). Residual: a SHORT bare token (no name, under 40 characters)
inside a remote stderr would reach the reason and the log (the scrubber's recall); the real runner never puts its curl text
in the envelope (it returns `"bridge error"`).

**F-10 (UNVERIFIED, FOLLOW-UP) the PC venue's request size is unmeasured.** `pc_command` puts the whole request, base64, in one
bridge command: 43,142 bytes for 8 chunks of 4,000 characters, 343,822 bytes for 64. The repo's other bridge senders slice at
40,000 characters because "the bridge caps one reply/request" (`scripts/pc_lane.sh:255-258`, `scripts/pc_suite.sh:73`), the
bridge REPLY caps at about 45 KB (AF-AP-15), and Linux refuses one exec argument over 131,072 bytes (my own exec of the
64-chunk command: `OSError: [Errno 7] Argument list too long`). The bridge server's exec method is not in the repo. The
coordinator's live PC check used 3 short chunks. A cut request is malformed JSON, so the failure is exit 3, never a wrong
answer; but `rank --venue pc` above about 40 KB may never work, and nothing says so.

**F-11 (INFO, static + reproduced) the call log cannot carry state text on the real path** (section 1: laya answers hold
numbers, labels or criteria only). It writes `answers` verbatim, so an endpoint that echoed the state in an answer field would
put state text in the log; not the case for the pinned server.

### The launcher (`scripts/jev_local.sh`, scratch copies on spare ports, stand-ins that keep the real server's load-then-bind order)

**F-12 (FOLLOW-UP, reproduced) `start` reports success when the port is held by another process.**
```
(a) port held by a bare listener: start -> (0, 'jev_local: started (pid 337, --threads 2, ...); /health answers once the model has loaded (about two minutes)')
    +4.7s server pid 337 alive=False ; status -> (3, 'down')     server log: OSError: [Errno 98] Address already in use
```
With the real server this shows only after the ~123 s model load (it binds after loading). D-7 names no port check.

**F-13 (FOLLOW-UP, reproduced) the pidfile identity check does not cover the port.** `our_pid` accepts any process whose
cmdline holds `laya_systemone_server.py`. With `.jev/server.pid` naming a second laya server on another port (as the J2 server
on 47412 is), ours down:
```
    start  -> (0, 'jev_local: already starting (pid 408); /health answers once the model has loaded')     (ours never starts)
    status -> (3, 'down')
    stop   -> (0, 'jev_local: stopped (pid 408)')          the OTHER server (port 40825) alive after our stop: False
```
Not idle: this container's `pid_max` is 32768 and PIDs have wrapped (new PIDs ~1,634 while the server is 30467), and the J2
server is a `laya_systemone_server.py --port 47412` in the same `.jev/` directory. D-7 only says "kills the pidfile's pid", so
this is not a contract break; the lane's claim "after checking that pid is this server" is broader than the check. Fix: also
require `--port 47411` (or no `--port`) in the cmdline.

**F-14 (INFO, reproduced) `start` says `started` for a server that dies at load** (stand-in exits after 1 s: rc 0 `started`,
then `status` `down`, a stale pidfile). The message says `/health` answers later, so it does not overclaim; the stale
pidfile is harmless unless F-13's reuse hits it.

**F-15 (INFO, observed, not JT1's file) the J2 pidfile is stale:** `.jev/server-47412.pid` names 31429 (no such process); the
J2 server on 47412 runs as pid 25324 (`ps`, 13:5xZ). Read-only observation; I did not touch it.

### The scanner (`scripts/hiccup_scan.py`, byte-identical copy, through its CLI on fixture transcripts of the real record shapes)

**F-16 (see section 3 for the disposition; reproduced) D-11's order puts parts of short secrets on the page.** Normalizing
first turns digits into `N`, which shrinks an 8-19 character value below the scrubber's floor, so a value the raw scrub
redacts survives. In an error's first line (both cluster tables) and in an Agent description (the agents table):
```
password-colon  raw scrub: 'password: <redacted>'             page: `curl: server said password: abNcd then closed`
bearer          raw scrub: 'Authorization: Bearer <redacted>' page: `curl: server said Authorization: Bearer abcNxyz then closed`
x-agent-token   raw scrub: 'X-Agent-Token: <redacted>'        page: `curl: server said X-Agent-Token: zqN then closed`
api-key-colon   raw scrub: 'api_key: <redacted>'              page: `... api_key: <redacted> ...`          (8 left: still redacted)
sk-15           raw scrub: 'sk-<redacted>'                    page: `curl: server said sk-abcdefN then closed`
xox             raw scrub: 'xox-<redacted>'                   page: `curl: server said xoxb-abcN then closed`
```
The lane's report bounds this residual as "a secret shorter than 20 characters with no name, no provider prefix and no URL";
that bound is false: named (`password:`, `X-Agent-Token:`), Bearer and prefixed (`sk-`, `xox`) secrets leak their letters.
A6's claim "Fake secrets in error text are absent from the page" rests on a 13-character fake (`hunter2hunter` stays 13
after normalization).

**F-17 (see section 3; reproduced) three page fields never pass the scrubber at all.** Tool names (context-cost table and
the clusters' `tools` column), model names (served-model and agents tables) and agent ids (agents table) are printed through
`_plain()` only. Full-size fakes planted there reach the page verbatim:
```
   PAGE> | 2026-09-20 | claude-opus-5-5 23 · AGENT_TOKEN=cVMjXl1uWH1c9Ogzoc_-k60yOL5KP5pr 1 |
   PAGE> | ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 | - | claude-opus-5-5 1 | 1 | 0 | 0 | 2026-09-20 10:17 | 2026-09-20 10:17 |
   PAGE> | AGENT_TOKEN=cVMjXl1uWH1c9Ogzoc_-k60yOL5KP5pr | 1 | 62 | 9.1% | 62 | 62 |
   PAGE> | https://leading-twist-aruba-pulse.trycloudflare.com/exec | 1 | 62 | 9.1% | 62 | 62 |
page bytes=5589; scrub(page)==page: False
```
Live exposure today: none. Streaming all 241 live transcripts: 48 distinct tool names over 38,360 tool calls, all plain
identifiers (longest 43); model names normal; 240 agent ids, all `[A-Za-z0-9]`. The committed page: sha256
`dd993ed1d9ba...` (27,917 bytes, as the lane reported), `scrub(page) == page`, no sk-/ghp_/xox/AIza/trycloudflare shape; its
"token"/"Secret" words are prose (`a claim token sits within N line(s)`, `[Secret-Store Writes]`).

**F-18 (BLOCKER candidate, see section 3; reproduced through the CLI) `--jev` changes the agents table near and past the
40,000-byte cap, breaking KC-J1b.** `build_page` trims agents until the page fits; the advisory column adds bytes, so the
`--jev` page can trim where the plain page does not, or trim more. Fixture `/tmp/vjt1/kc` (181 subagent transcripts, two
COVERED clusters, so the `--jev` run makes zero model calls; `/tmp/vjt1/kc_confirm.py`):
```
plain rc=0 page_bytes=39924
jev   rc=0 page_bytes=39149 uncovered_shown=0 filled=0 run_s=0.1
KC-J1b: jev page minus the column == plain page: False          (the lane's own _strip_jev_column)
agent rows: plain=181 jev=176
plain 'not shown' line: []
jev   'not shown' line: ['5 older agents active in the window are not shown (the page cap).']
```
Past the cap it is common, not a corner: 160 over-cap pages (200-300 agents, random description lengths, the same minimal
76-byte column) differ outside the column in 12 (`/tmp/vjt1/kc_rate.py`). The live page is 27,917 bytes today (114 agents
in its 7-day window); the code trims because the page is expected to reach the cap. The lane's KC-J1b checks (unit test,
live frozen pair) all ran far below the cap.

**F-19 (FOLLOW-UP, reproduced; the registry's AF-AP-152 class) `excerpt()` is quadratic on a long identifier run.** `_URL`
(`[a-z][a-z0-9+.-]*://`, case-blind) and `_KV` (`[A-Za-z_][A-Za-z0-9_]*=`) restart the scan of a run at every position.
```
n=20000 letters excerpt 3.630s | n=40000 letters excerpt 12.595s | n=40000 _URL 11.107s, _KV 2.689s, _QUOTED 0.001s, _RUN 0.000s
CLI: one error record whose line after `Exit code 1` is 40,000 letters -> rc=0 wall=14.3s
```
400 KB on one such line would take about 20 minutes (quadratic). The live scan (~1 GB) runs in about 10 s, so no such line
exists today. Fix: a lookbehind anchor on both (`(?<![A-Za-z0-9+.-])`, `(?<![A-Za-z0-9_])`), plus a timing test.

**F-20 (FOLLOW-UP, reproduced) one long tool name makes the page impossible.** Tool names are not cut: a 45,000-character
tool name gave `hiccup_scan: the page is 137629 bytes, over the 40000-byte cap; nothing written` (rc 2). D-11's cap holds (it
fails closed), but the whole page is lost to one field; the agent trim cannot help. Fix with F-17: pass tool names, models and
agent ids through the same cut (and scrub).

**F-21 (INFO, reproduced) extreme but well-formed timestamps.** A transcript whose newest record is `0001-01-03T00:00:01Z`
crashes: `OverflowError: date value out of range` with a traceback, rc 1 (A6 says "never a crash" for MALFORMED lines; this
line is well-formed). One record at `9999-12-31T23:59:59Z` becomes the page clock (`Clock: 9999-12-31T23:59:59Z`) and every
real day drops out of the 14-day table (0 rows). Contrived inputs.

**F-22 (INFO, reproduced) D-8 determinism holds under hostile environments.** The lane's fixture plus my secrets fixture,
each run writing a fresh page, scan rc 0 every time, one sha256 (`e8dd5a29ffbc2df7...`) for: `TZ=UTC LC_ALL=C.UTF-8`;
`TZ=Pacific/Kiritimati LC_ALL=C`; `TZ=America/St_Johns LC_ALL=tr_TR.UTF-8`; `PYTHONHASHSEED=1`; `PYTHONHASHSEED=4242
PYTHONUTF8=0 LC_ALL=POSIX`; `PYTHONHASHSEED=random LANG=de_DE.UTF-8`; and a copy in another directory with other mtimes.
Wrong JSON types inside records (a list `tool_use_id`, a dict `content`, a list `name`, a string `usage`, a list attachment,
an int timestamp, a dict `type`) give rc 0 and a page.

**F-23 (INFO, static) one huge line is read whole.** `feed` streams by line, but a single line is read into memory whole and
`--limit-bytes` is checked after the read. The live transcripts' largest records are `task_reminder` attachments (~166 KB
each); not tested at the GB scale (2.9 GB disk free).

### Found in the live runs (the real server on 47411)

**F-24 (CONTRACT-DEFECT, reproduced live) `rank` returns a signal-free ranking for a long query, and the fan-out guard
cannot see it.** The server gives each chunk the state `{"query": q, "chunk": text}` (query first,
`laya_systemone_server.py:135,139`), laya serializes it and cuts it from the right to the window (`laya/common.py`:
`st = st[:room]`; `max_len` 1024, `head_max_len` 256 in the snapshot's `rl_agent_config.json`). D-5's default cap is 4,000
characters PER TEXT, so a query near the cap fills the window and every chunk is cut away:
```
$ python3 scripts/jev.py rank --venue local --query 'pytest fails: FileNotFoundError for the --basetemp directory' --chunk C1 --chunk C2 --chunk C3
{"cmd": "rank", "fan_out": 3, ..., "ranking": [["c0", 0.4902], ["c1", 0.179], ["c2", 0.1677]], ...}          (short query: real ranking)
$ python3 scripts/jev.py rank --venue local --timeout 240 --query '<the same, then 3,874 characters of pytest error lines>' --chunk C1 --chunk C2 --chunk C3
{"cmd": "rank", "fan_out": 3, "latency_ms": 32987.3, "ranking": [["c0", 0.4958], ["c1", 0.4958], ["c2", 0.4958]], ...}   rc=0
```
Token counts (the snapshot's tokenizer): the long query's JSON part is 1,101 tokens, more than the ~980 left after the
head; 4,000 characters of plain English is 889 tokens (about 90 left for a chunk). This is D-1's rejected failure (one score
for every chunk) arriving with `fan_out` equal to the chunk count, so the client prints a ranking, rc 0. The builder followed
D-1 and D-5; the defect is the pinned default. Returned to the coordinator: amend D-5/D-1 (a query budget well under the
window, for example 1,000 characters or a token count, and/or refuse a rank whose N>1 scores are all equal). The scanner's
own `--jev` use is safe (queries are 160-character keys, chunks 300 characters). Cross-check: the J2 probe
(`docs/research/findings/ap-hawk-probe/ap_probe.py`) used its own HTTP client with short queries, and 0 of its 100 samples has
tied top-3 scores, so J2's "no signal" verdict is not this artifact. Any other `jev.rank` consumer that passes a long query
(the JT2 lane's tools, which I did not read) would get this silently.

**F-25 (INFO, reproduced live) the scrubber's opaque rule erases long identifiers from what jev sends.** 30 labels of the form
`L01-` plus 60 `x` (64 identifier characters each) all became `<opaque-redacted>`, and `classify` refused with `jev: usage: a
choice question needs at least two distinct criteria (after the scrub and the cap)` (exit 64, accurate). A chunk made of a
40+ character identifier (many test names) is sent as `<opaque-redacted>`: correct under D-5, but it removes signal when
ranking code symbols.

**F-26 (INFO, reproduced live) the paths the lane did not run live work:** `ask --type score` (score 1.0121 in [0, 2],
confidence 0.0421) and a 30-label `classify` (30 probabilities summing to 1.0, flat as expected).

**F-27 (INFO, reproduced) the real launcher against the adopted server:** `bash scripts/jev_local.sh status` printed the
health JSON (rc 0); `start` printed `jev_local: already running: ...` (rc 0); pid 30467 untouched (elapsed 02:07:40).

**F-28 (INFO, reproduced) 16 processes x 25 calls on one call log:** 400 lines, 0 unparsable, each with the ten keys.
Pre-existing modes are corrected: `.jev` 755 -> 700 and `calls.jsonl` 644 -> 600 after one call; a caller-named existing
directory keeps 755 by design (its file is 600).

### Mutation audit (scratch copies only: `/tmp/vjt1/mutants.py`, one anchored replacement per mutant, count asserted 1)

```
PRISTINE                         rc=0 | 77 passed in 22.68s
B1-drop-scrub                    rc=1 | 3 failed, 74 passed | test_a_secret_straddling..[named-token], [sk-key], test_every_scrubber_class_is_removed..
B2-cap-then-scrub                rc=1 | 2 failed, 75 passed | test_a_secret_straddling_the_cap..[named-token], [sk-key]
B3-log-state-text                rc=1 | 1 failed, 76 passed | test_call_log_never_holds_the_state_and_has_the_modes
B4-wall-clock-header             rc=1 | 2 failed, 75 passed | test_page_rows_are_exact, test_same_input_bytes_give_the_same_page_bytes_and_no_wall_clock
V1-no-fchmod                     rc=0 | 77 passed            | SURVIVES (no test with a pre-existing 0644 log file)
V2-no-default-dir-remode         rc=0 | 77 passed            | SURVIVES (no test with an existing default .jev at another mode)
V3-feed-no-recursion-catch       rc=0 | 77 passed            | SURVIVES (no deeply nested line in the fixture)
V4-scrub-before-normalize        rc=1 | 1 failed, 76 passed | test_page_rows_are_exact
V5-window-wall-clock             rc=1 | 3 failed, 74 passed | test_page_rows_are_exact, test_the_jev_column_is_advisory.., test_the_page_trims..
V6-accept-any-pc-status          rc=1 | 1 failed, 76 passed | test_pc_failures_fail_open[http503]
V7-http-no-httpexception-catch   rc=0 | 77 passed            | SURVIVES (only the reason text changes: the outer catch-alls still fail open)
V8-no-loopback-check             rc=1 | 1 failed, 76 passed | test_usage_errors_exit_64_and_send_nothing[non-loopback-url]
V9-no-stderr-sink                rc=1 | 4 failed, 73 passed | test_pc_path_..._survives_the_bind_warning[data-line|leading|none|status-line]
V10-noul-no-finite-check         rc=1 | 1 failed, 76 passed | test_failure_is_exit_3_with_one_reason_line_and_none_from_the_api[nan]
V11-bind-greedy-prefix           rc=1 | 4 failed, 73 passed | test_auto_falls_back.., test_pc_health.., test_pc_path..[data-line], [status-line]
V12-last-family-wins             rc=1 | 4 failed, 73 passed | test_page_rows_are_exact, test_real_first_line_shapes..[Terminated|cwd|python exception]
V13-no-exitcode-join             rc=1 | 6 failed, 71 passed | test_fake_secrets_never_reach_the_page, test_fixture_counts_are_exact, +4
V14-jev-asks-covered-too         rc=1 | 2 failed, 75 passed | test_jev_unavailable_says_na.., test_the_jev_column_is_advisory..
V15-local-stop-no-identity       rc=1 | 1 failed, 76 passed | test_jev_local_start_is_idempotent_and_stop_kills_only_its_pid
FIX-F16-prescrub                 rc=1 | 1 failed, 76 passed | test_page_rows_are_exact (its pinned row `for T password:` becomes `for sk-<redacted> password:`)
FIX-F17-scrub-fields             rc=0 | 77 passed
FIX-F18-trim-from-plain          rc=0 | 77 passed            (trim both pages against one budget with 8,000 bytes kept for the column)
```
The brief's four (B1-B4) die as the lane reported. **F-29 (FOLLOW-UP) three test gaps:** V1 and V2 survive although the code
is right (F-28 shows it re-modes), V3 survives although `feed` handles the case; add a pre-existing-mode test and a
deep-nesting line. V7 is low value. The FIX rows are compatibility probes, not mutants: F-17's and F-18's fixes keep the
suite green; F-16's needs one expected row updated (the secret stays hidden either way).

Discriminators, PIN copy vs a copy with the three fixes (`/tmp/vjt1/fixroot`), my fixtures:
```
root     secrets fixture: short-secret stubs on page=5/5  full secrets on page=4/4
fixroot  secrets fixture: short-secret stubs on page=0/5  full secrets on page=0/4
root     KC fixture: plain agent rows=181 jev agent rows=176  not-shown lines: plain=0 jev=1
fixroot  KC fixture: plain agent rows=141 jev agent rows=141  not-shown lines: plain=1 jev=1
```
And F-16, F-17 and F-18 reproduced with the REPO's own `scripts/hiccup_scan.py` (== PIN), `--out` to scratch: 5 of 5 stubs,
all four full fakes, and `plain 39924 bytes / 181 rows` vs `jev 39149 bytes / 176 rows + "5 older agents ... not shown"`;
the shared `.jev/calls.jsonl` stayed at 121 lines (no model call: every cluster covered) and `docs/HICCUPS.md` untouched.

### Evidence audit (the lane's load-bearing claims, re-derived)

**F-30 (INFO, reproduced) the E4.3 cross-check is exact.** `hiccup_scan.py --transcript <main> --limit-bytes 651687566`:
`files=1 bytes=651687566 lines=114378 unparsable=8 ... tool_use=16736 tool_result=16730 errors=239 ... task_reminder=1739
silent_turn_reminder=1064 compactions=118 ... page_bytes=11627 sha256=11acf74096ac...` (the lane's sha); `task_reminder`
1,739 records, 289,208,111 bytes, 44.4%. E4.3's own lines (`JEV-LEVERAGE-EVIDENCE-2026-09-24.md:381-401, 553-555`): the
same bytes, lines, calls, results, errors, reminders and compactions; exit code N 149 = 100 + 20 + 17 + 10 + 2 here; sleep 28,
denial 23, "GitHub MCP/API and misc" 14 = UNCOVERED 14, edit anchor 11, input validation 8, ripgrep 4, user declined 2.

**F-31 (INFO, reproduced) A6 and A7 live.** A frozen live set (main at 669,113,813 bytes by `--limit-bytes`, 234 idle
subagent files as they are, 6 active ones copied; idle-file fingerprint `66f288136397fa4f` before and after): two runs,
`files=241 bytes=1007099249 lines=205159 unparsable=18 ... errors=694 clusters=409 uncovered=18 ... page_bytes=28142
sha256=b153c72ab604...` twice, `cmp` identical. `--jev --jev-venue local` on the same set: `jev: uncovered_shown=5 filled=5
run_s=70.1` (cells `AF-AP-148 0.5303`, `CLAUDE.md:420 0.5146`, `AF-AP-102 0.4222`, `AF-AP-104 0.4558`, `AF-AP-58 0.2789`), and
the lane's own column-strip gives the plain page back (KC-J1b holds this far below the cap). The committed page is the
lane's (sha256 `dd993ed1d9ba...`, 27,917 bytes).

**F-32 (INFO) D-9 seeding holds on today's data.** 18 UNCOVERED clusters, 27 events, none above 4; the GitHub MCP tool group
has 9 events in 5 different shapes (no single shape reaches 5). A new 4-event cluster (`PreToolUse:Bash hook error: ...
search-intercept.py`) comes from the JT3 lane's in-progress hook.

**F-33 (INFO) covering rules are loose.** Every `Exit code 143 :: Terminated` maps to the GitNexus `analyze` line;
`Found N matches of the string to replace` (the Edit tool) maps to `anchor_edit.py`'s uniqueness rule (another tool). The
test checks that the phrase's words exist in CLAUDE.md, not that the rule covers the family. 8 of 14 rows are `none`
(the lane's DISC-2, honest).

**F-34 (INFO) stale prose to fix with the repair:** `scripts/hiccup_scan.py:13` ("Nothing secret reaches the page",
F-16/F-17) and `:20` ("The column never changes any other number", F-18); `scripts/jev_local.sh:9` ("after checking that pid
is this server", F-13); `scripts/jev.py:20` ("`--url` pins one loopback endpoint", F-6) and `:28` ("No gate file may import or
RUN this module (scripts/no_laya_in_gates.py)": the screen refuses an import but, by its declared limit, not an exec). The
JT1 report's self-attack 2 (the residual bound) and 3 (KC-J1b) are falsified by F-16 and F-18.

**F-35 (INFO, static) the per-day p90 is one rank high when 0.9n is whole:** `ctx[int(0.9 * len(ctx))]` is the maximum for
n = 10 (nearest-rank p90 is index 8). Definitional; the brief names no method.

## 3. Blocking predicate, per candidate

| Finding | 1 contract | 2 canonical path | 3 material | 4 discriminator | 5 in boundary | Disposition |
|---|---|---|---|---|---|---|
| F-18 `--jev` trims agents differently | D-10 KC-J1b: "the column never changes any other number" | yes: the repo's scanner at the PIN, CLI, no model call | yes: 181 vs 176 agent rows plus a "5 not shown" line; 12 of 160 over-cap pages differ | `/tmp/vjt1/kc_confirm.py`; a one-budget trim flips it, suite 77 green | yes (`build_page`) | **BLOCKER** |
| F-16 normalize-then-scrub leaks | D-11 "nothing secret reaches the page"; A6 | yes | letters of 8-19 character named/prefixed secrets; none on the live page | yes: pre-scrub gives 0/5 | the PINNED D-11 order causes it | **CONTRACT-DEFECT** (amend D-11 to scrub, normalize, scrub, cut) |
| F-24 long query hides every chunk | D-1 + D-5 default 4,000 vs the 1,024-token window | yes, live on the real server | yes: a signal-free ranking, rc 0, fan_out 3 | short vs long query | the PINNED default causes it | **CONTRACT-DEFECT** (a query budget and/or refuse all-equal scores) |
| F-17 tool/model/agent-id fields unscrubbed | D-11 | yes | no live instance: 48 tool names in 38,360 calls, all identifiers; models and ids harness-set | yes: `scrub` in `_plain`, suite green | yes | FOLLOW-UP (cheap: fold into the F-18 repair) |
| F-20 one long tool name loses the page | D-11 cap holds (fails closed) | yes | the page is lost, not wrong | yes | yes | FOLLOW-UP |
| F-19 quadratic `excerpt` | none (D-8 is about bytes); AF-AP-152 class | yes (14.3 s for 40,000 characters) | no live instance | yes | yes | FOLLOW-UP |
| F-12, F-13, F-14 launcher | D-7 asks neither a port check nor an identity check | scratch copies | F-13 can kill the J2 server if its pid lands in `server.pid` | yes | yes | FOLLOW-UP |
| F-4, F-5, F-6 client | A2 met (each fails open) | doubles | need a misbehaving endpoint | yes | yes | FOLLOW-UP |
| F-2 list-valued secret | D-5 met (jev scrubs) | yes | the scrubber's gap | yes | no (`transcript_export`) | FOLLOW-UP to the scrubber's owner |
| F-10 PC request size | none | cannot, without the bridge | unknown | none | - | UNVERIFIED |
| F-29 test gaps (V1, V2, V3) | none | - | code correct | the surviving mutants | yes | FOLLOW-UP |

## 4. Gate recommendation

**NOT-READY** — one finding meets the whole blocking predicate: **F-18** (`--jev` changes the agents table near and past the
40,000-byte cap, against D-10/KC-J1b; reproduced with the repo's scanner at the PIN). Two **CONTRACT-DEFECTs** go back to the
coordinator for an explicit amendment before the repair: **F-16** (D-11's pinned normalize-then-scrub order leaks letters of
short named secrets; A6's claim rests on a 13-character fake) and **F-24** (D-5's 4,000-character default lets a long query
push every chunk out of Laya's 1,024-token window, so `rank` returns an equal-score ranking with `fan_out` N and rc 0).
Everything else is FOLLOW-UP or INFO. The one focused repair, keyed JT1 / brief `tasks/briefs/jev-laya/JT1-brief.md` /
code at 7d73932: a one-budget trim in `build_page` (F-18) with a near-cap test; the F-17 `scrub` in `_plain` and a cut on
tool names (F-20); the stale docstrings (F-34); and F-16/F-24 as the coordinator amends them. Nothing in this recommendation
depends on an unreproduced item; F-10 (PC request size) is UNVERIFIED and does not bear on it.

## 5. What I reproduced, what I read only, what I skipped

- Reproduced (commands and outputs above): the premise; both gates (77 passed twice); pyflakes; the gate screen and its
  negative control; A1 live (all four commands, plus score and 30-label classify); A2-A5 with new shapes (doubles and an
  injected runner); A4 modes and concurrency; A6 and A7 live; the E4.3 cross-check; D-8 under seven environments; every
  finding marked "reproduced", the blocker and both CONTRACT-DEFECTs through the real path at the PIN; 19 mutants and 3 fix
  probes on scratch copies.
- Read only (static): the laya answer shapes and raise sites; `pc_bridge_exec.run` (token via `--config -` on stdin, not
  argv); the bridge protocol in `PC-BRIDGE.md`; the other bridge senders' 40,000-character slicing.
- Skipped, and why: the real bridge and the PC venue live (the brief forbids it; the coordinator's 13:3xZ live check
  stands); a cold start or stop of the real server (never stop 47411); the J2 server on 47412 and the other lanes' files
  (never touched, never run; only the J2 pidfile and `ps` line were read); a multi-GB single-line transcript (disk had
  2.9 GB free; F-23 is static).
- My writes: this report; scratch files under `/tmp/vjt1/` only. No tracked file was modified (`git status` shows only the
  other lanes' changes and this report). No commit, no push, no bridge call, no subagent.
- Served model (my transcript `agent-ac7d6fa52334a9d4b.jsonl`, counted per assistant record at 14:2xZ): 241 of 241
  `claude-opus-5-5`, 0 `"stop_reason":"refusal"`.
