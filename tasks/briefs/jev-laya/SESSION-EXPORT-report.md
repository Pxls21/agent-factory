# SESSION-EXPORT report (task #252; D-084, D-086)

Role: code-implementer (sandbox, Opus 5.5). Brief: `tasks/briefs/jev-laya/SESSION-EXPORT-brief.md`. PIN: e6bab18
(local HEAD = origin head = `e6bab182cedf77e3568401113041df2c6783d46a` at start, 2026-09-25T02:40:57Z).

STATUS: DONE, all evidence demands filled (2026-09-25T06:1xZ); NOT committed (the coordinator commits); the shipper NOT
run against the real bridge (the coordinator ships). A container restart stopped the lane at about 03:4xZ; it resumed
05:04Z with AMENDMENT 2 (origin 6750a25). State at the resume, checked on disk: `scripts/transcript_export.py` and its
tests carried G6 (110 passed before the stop); the exporter and its tests were rebuilt for both amendments after it; no
pseudonym key existed (made 05:22Z); the two pre-amendment exports were deleted and replaced by the final two runs.

Files (all in the boundary): `scripts/transcript_export.py` (+56 lines), `tests/test_transcript_export.py` (+157),
`scripts/session_export.py` (900 lines, new), `tests/test_session_export.py` (885, new), `scripts/ship_to_pc.py` (369,
new), `tests/test_ship_to_pc.py` (298, new), this report. Scratch producers: `sx/` under the session scratchpad. The
pseudonym key: `/root/.config/session-export/pseudonym.key` (32 bytes, mode 0600, dir 0700, key id d23396be261a; never
printed). Output: `<scratchpad>/session-export/` (the export to ship) and `<scratchpad>/session-export-run2/` (the
determinism rerun; not for shipping).

## 0. Premise re-measure (evidence demand 1)

Verdict: NO design-relevant mismatch. Measured 2026-09-25T02:41Z-02:55Z (`date -u`), producers in
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/sx/` (`survey.py`, `survey2.py`, `survey3.py`,
`premise.py`, `premise2.py`; each prints names, types and counts only, never a value).

| Premise line | Authoring (02:2xZ) | Re-measured | Verdict |
|---|---|---|---|
| `du -sh` | 1.3G | 1.3G | match |
| depth histogram (10 / 6 / 8) | 38 / 1 / 257 | 38 / 1 / 259 | +2 subagent transcripts (this lane's own and one more lane: growth) |
| main session bytes | 704,448,851 | 705,586,594 (grows live) | growth |
| Read/Write/Edit naming a secret path: pc-bridge.env / dotenv / qwen-builder / qwen-jev / codiv / hermes | 3 / 5 / 0 / 0 / 1 / 0 | 3 / 5 / 0 / 0 / 1 / 0 | exact |
| Bash naming: pc-bridge.env | 1,699 | 1,625 (`\.pc-bridge\.env` in `input.command`); 1,727 (`pc-bridge` substring) | regex choice: the authoring regex is not in the brief; no variant gives 1,699; magnitude agrees |
| Bash naming: dotenv | 1,680 | 1,945 (`\.env\b`); 1,924 (`\.env(?![\w.])`); 1,856 (`(?<=[\w-])\.env\b`) | regex choice, as above |
| Bash naming: qwen-builder / qwen-jev / codiv / hermes profile | 38 / 6 / 8 / 323 | 39 / 6 / 8 / 324 | growth |
| EDIT cause-in-prefix probe (main session) | n 652, prior 614, err 11, err_prior 9 | n 652, prior 614, err 11, err_prior 9 (`premise.py`: an Edit whose `file_path` appeared in an earlier tool input's `file_path`) | exact |
| TEST probe | n 824, prev 40, ... | NOT re-measured: the brief gives no definition of a test command or of its outcome | - |
| `grep -n '^def \|^SECRET_PATTERNS'` | 51, 56, 85, 91, 116, 134 | 51, 56, 85, 91, 116, 134 | exact |
| zstandard / xz / gzip / free disk | absent / present / present / 2.7G | absent / present / present / 2.4G | less free disk (other lanes) |

Record shapes the design depends on (all 298 files; `survey*.py`):
- Every user record that holds a `tool_result` holds exactly one (45,067 records; 0 with two or more), so the record-level
  `toolUseResult` and `toolDenialKind` belong to that one result.
- Thinking blocks: 33,375 blocks; 4,724 carry plain text in `thinking` (main 1,364, subagent 3,360); 28,651 carry an empty
  `thinking` and only a `signature` (an opaque blob). Answer to the brief's question: SOME thinking blocks carry plain text;
  the export keeps those (scrubbed) and drops the signature-only ones (counted per source as `thinking_signature_only`).
- `rendered` on attachments appears only from 2026-09-08 on (e.g. `total_tokens_reminder` 0 of 16,687 before 09-08, all
  after): it is a harness-version field, so the attachment rule is by type, never by `rendered`.


## 1. The scrubber (evidence demand 2)

DEVIATION (flagged, allowed by the brief's "or add a stricter pass beside it"): `scrub` and `SECRET_PATTERNS` are NOT
changed. Two functions are added beside them in `scripts/transcript_export.py`:
- `scrub_payload(text)` = `scrub`'s named rules, then `PAYLOAD_PATTERNS` (4 rules: a bridge host with no `http(s)://`
  scheme, every label; a Bearer token's tail in `~+/=`; `Authorization: Basic` credentials; a URL userinfo password), then
  `scrub`'s coarse opaque-run rule last (the G6 order, below). This is "the extended scrubber" D-2 runs on every text.
- `scrub_strict(text)` = `scrub_payload`, then every assignment value on a line (env file, `grep -n` prefix, `export`,
  curl config), every run of 20+ `[A-Za-z0-9_\-+/=]` holding a letter and a digit, every line that is one 12+ token
  holding a letter and a digit. The strict pass of D-2.
Why beside and not inside: `scrub` has 15+ importers (`hiccup_scan.py`, `jev.py`, `jev_context.py`, `laya_ft/common.py`
and `teacher_label.py` of the live DSV2 lane, `harness-ports/bin/hermes-session-export.py`, `qwen_matrix.py`, 5 test
files; graft/rg 50 hits in 17 files) and two laya_ft dataset manifests record this file's sha256 as provenance. Changing
`scrub` would change their outputs mid-lane. ADJACENT DEFECT (reported, not fixed): those consumers still miss the four
payload shapes (for example a bare `*.trycloudflare.com` host reaches `docs/HICCUPS.md` or a jev query unscrubbed);
folding `PAYLOAD_PATTERNS` into `scrub`, or switching them to `scrub_payload`, is the coordinator's call.

Tests (all in `tests/test_transcript_export.py`, appended; 0 existing lines changed, `git diff -U0` removed-line count 0):
31 new parametrized cases: 7 payload shapes, 10 payload negative controls, 1 "the payload rules leave every pinned fixture
as scrub leaves it" (all PIN_OUTPUTS, CHAINED, IN_RUN, LATER_RULES, QUOTED_OR_COMPOUND, PLANTED and the 7 key families),
6 strict shapes, 6 strict negative controls, 1 fixed-point + linearity case (43,400-character run in under 3 s).

Red first (verified, 2026-09-25T02:5xZ): `31 failed, 72 passed in 1.36s` against the unchanged file, every failure
`AttributeError: module ... has no attribute 'scrub_payload'` / `'scrub_strict'`. Semantic red (verified, booleans only):
each of the 7 payload shapes and 5 of the 6 strict shapes leaves a fake value through the CURRENT `scrub` (strict row 4,
the curl config, is already caught by `scrub`; that row pins the strict pass's line-level output). Green:
`103 passed in 1.39s`.

Chat export byte-identical (verified): `sx/chat_identity.py` runs the PIN copy (`sha256 f63cd97e...`, saved before any
edit) and the new CLI over all 77 fixtures the existing tests build (the main fixture, every text of PIN_OUTPUTS /
CHAINED / IN_RUN / LATER_RULES / QUOTED_OR_COMPOUND / PLANTED, the 7 key families, the prose and long-run cases, the two
cap-straddle cases): `fixtures 77: byte-identical 77, differing 0`. By construction too: `scrub` is untouched.
Re-run after the G6 change (2026-09-25T05:21:47Z) and again at 06:13:50Z, after the file's last edit (a comment fix at
05:38Z): both
`fixtures 77: byte-identical 77, differing 0`. `git diff --stat` reads `scripts/transcript_export.py | 56 ++++`,
`tests/test_transcript_export.py | 157 ++++`, `2 files changed, 213 insertions(+)`: no deletions (the removed-line count
of `git diff -U0` on both files is 0). The comment fix: the block comment above PAYLOAD_PATTERNS said "`scrub_payload` is
scrub, then these rules"; G6 made that false (the opaque-run rule now runs after these rules), so it now points to the
order in the docstring.

G6 in the scrubber (AMENDMENT 1). `scrub_payload(text, opaque=None)` and `scrub_strict(text, opaque=None)` take an
optional callable for the coarse opaque-run rule (`\b[A-Za-z0-9_\-]{40,}\b`): with none, the rule writes its marker
`<opaque-redacted>` as before; with one, the callable's return value replaces the match. Order inside `scrub_payload`:
every named SECRET_PATTERNS rule, then the 4 PAYLOAD_PATTERNS, then the opaque-run rule last, so a long value that a
named rule takes (a 44-character bridge token, a GitHub token, a bridge host, a Bearer tail, Basic credentials, a URL
password) is redacted by that rule and never reaches the callable. `scrub` (the chat export) is unchanged and keeps the
marker. Tests: 7 more (6 NAMED_LONG cases: the named rule takes the long value and the callable sees nothing; 1 case: a
fake 40-hex commit id reaches the callable, the marker stays without one, and the strict pass passes the callable
through). Red first (verified, this lane's transcript line 361, 2026-09-25T03:41:10Z): `7 failed, 103 passed in 1.34s`,
all 7 because the `opaque` argument did not exist (`TypeError`; each test calls it). Green: `110 passed in 1.21s`
(2026-09-25T05:21:47Z).

## 1b. AMENDMENT 1 (G1-G6): premise re-measure (read 2026-09-25T03:3xZ, origin 16748dc)

Measured with `sx/survey5.py` and `sx/survey6.py` (names, tag names, types and counts only):

| Item | Field in the records (AF-AP-42; example `src`, line) | Measured | Verdict |
|---|---|---|---|
| G1 | attachment `edited_text_file` {`filename`, `snippet`} (main, line 737) | 461 records | as the amendment says |
| G2 | assistant `message.model`, `message.stop_reason` (every assistant record; 94,341 of 94,341 carry `model`); API errors: assistant `isApiErrorMessage` (true 61; main line 913), `error` (str, 61), `apiErrorStatus` (int: 429 x45, 403 x5, 529, 500; main line 3337), model `<synthetic>`, stop `stop_sequence` 52 / `refusal` 9; system `subtype=api_error` (11; main line 37251) | no user, attachment or system record carries `model` or `stop_reason` | as the amendment says |
| G3 | Read results, Write inputs | see section 2 (capped counts after the change) | - |
| G4 | the notification's own XML fields `<task-id>`, `<tool-use-id>`, `<status>` or `<event>` | `sx/survey6.py`, main session: 1,378 notification records (queued attachments and user texts). Status notifications by (task-id, status): 718 singletons, 16 pairs, 4 triples, 2 quadruples; of the first two records of each of these 22 groups, 21 carry DIFFERENT `<tool-use-id>`s (different tasks that reuse a task id; in 4 one record has no `<tool-use-id>`) and 1 the same. Monitor events by (task-id, event): 604 singletons, 2 pairs, both byte-identical. `source_uuid` on 635 queued records links to 0 user records (`survey5.py`) | CONTRADICTED: a notification is recorded ONCE (a queued attachment or a user text), not twice. Implemented as ruled with a strict identity (task-id, tool-use-id, status, event; no task-id = never merged), so only true repeats drop; (task-id, status) alone would merge different tasks |
| G5 | `toolUseResult.bashEditDiff` {`changedFiles` [str], `files` [{`filePath`, `hunks` [{`oldStart`, `oldLines`, `newStart`, `newLines`, `lines`}], `created`?, `deleted`?}], `moreFiles` int, `shared`?, `unavailable`?} (main line 33457) | 1,722 results; `files` is a subset of `changedFiles` in all; 24 list changed files with no `files` entry; `moreFiles` > 0 on 118 | as the amendment says |
| G6 | the coarse opaque-run rule (`\b[A-Za-z0-9_\-]{40,}\b`, `scripts/transcript_export.py` SECRET_PATTERNS, last class) | - | as ruled |

## 2. The export over every transcript (evidence demand 3)

The final two runs used the code as delivered (`scripts/session_export.py` sha256 `7bf26338...`,
`scripts/transcript_export.py` `395db6dd...`; the manifests' `code_sha256` `d1b42067...`; key id `d23396be261a`):
- run 1: `python3 scripts/session_export.py export --out <scratchpad>/session-export`, started 2026-09-25T05:47:40Z;
- run 2: `python3 scripts/session_export.py export --out <scratchpad>/session-export-run2 --offsets
  <scratchpad>/session-export/manifest.json`, started 05:53:18Z.

DEVIATION (flagged): each run was started detached (`setsid nohup`) and waited for in one foreground `tail --pid` call. One
run takes about 5.5 minutes, and the Bash tool stops a call at 600 s; a stopped run would leave a half-written out dir.
Nothing ran unwatched.

Run 1's summary, pasted (run 2 printed the same lines except its id and `333.1 s`):
```
export 2026-09-25T05:47:40Z: 317 sources, 1178943962 bytes read, 38706220 bytes written, 329.3 s
folders {"-home-user-agent-factory": {"sources": 1, "bytes_read": 3074681}, "-home-user": {"sources": 316, "bytes_read": 1175869281}}
events {"api_error": 72, "file_change": 2796, "harness_notice": 488, "hook": 2644, "notification": 6684, "pruner_archive": 1, "summary": 131, "text": 16267, "thinking": 4997, "tool_call": 46435, "tool_result": 46422}
capped {"hook": 2, "notification": 1753, "summary": 2, "text": 37, "tool_call": 40, "tool_result": 20}
dropped_secret_path 11 strict_results 2543 unsettled 0 seam_adjusted 0 thinking_signature_only 29704 duplicate_notifications 2 file_changes_unrecorded 364 pseudonyms 69846 pruner_archives 1 archives 1 archives_skipped 0 archives_unlinked 0 archives_unmatched 0
```

| Measure (verified: run 1's manifest and `sx/analyze.py` over its output) | Value |
|---|---|
| Sources, per folder (AMENDMENT 2) | 317: `-home-user/` 316 files (1,175,869,281 bytes read), `-home-user-agent-factory/` 1 file (3,074,681 bytes). `src` is the path under `/root/.claude/projects/` |
| Input lines read | 244,494, of which 22 do not parse (last row) |
| Events | 126,937 (per kind in the pasted `events` line) |
| Capped, per kind (after G3) | hook 2, notification 1,753, summary 2, text 37, tool_call 40, tool_result 20; none at the large cap |
| The large cap (G3) | 171 Read results, 52 Write inputs and 29 file changes are over 32,768 characters and are kept whole (each is under 131,072). D-3 alone would have cut these 252 events |
| Dropped (secret path) | 11 events: 5 file-tool calls (2 Read, 3 Write), each a call and a result, and 1 `file` attachment that names `.pc-bridge.env` |
| Strict pass | 2,543 events (the results, file changes and archives of calls whose input names a secret path, and results with no call in the transcript) |
| Bytes | read 1,178,943,962; written 38,706,220 (`.xz`) + 381,078 (manifest) = 39,087,298, 3.3% of read. The decompressed stream is 311,771,416 bytes |
| Text bytes per kind (decompressed) | tool_result 98,206,413; notification 76,877,299; tool_call 55,723,149; file_change 14,203,852; text 8,271,331; harness_notice 3,140,724; summary 2,514,682; hook 2,440,930; thinking 1,250,035; pruner_archive 25,516; api_error 15,311 |
| Wall time | run 1 329.3 s, run 2 333.1 s (4 workers; the largest source first) |
| Determinism (D-4) | 317 of 317 outputs byte-identical across the two runs. sha256 over the sorted `sha  path` lines: `ec4db91b84d9938e6a94397a1e3f50a0a7e84df3b2b19f39b1d41d924eb12519` for both. The manifests differ only in `export_id` and `wall_seconds`; every `output_sha256` matches its file. The main session: offset 714,512,525, input sha256 `9366613f...`, output sha256 `fc14d407...`, 12,496,368 bytes |
| Pseudonyms (G6) | 69,846 `[opaque:<12 hex>]` in the exported text |
| Repeated notifications (G4) | 2 dropped |
| Bash file changes (G5) | 2,796 file_change events; 364 more files that the harness counted in `moreFiles` and did not record |
| Thinking | 4,997 plain-text blocks exported; 29,704 signature-only blocks counted, not exported |
| Pruner archives (AMENDMENT 2) | the records' `cwd` values name 1 archive dir that exists (`/home/user/agent-factory/.claude/fast-jev-output`; `/home/user` has none). It holds 1 archive (25,516 bytes) named by a call id, exported as 1 pruner_archive event. 0 named by the clock, 0 with no call in any transcript, 0 skipped (not a regular file) |
| Skipped records (bookkeeping) | ai-title 51, atis-latch 8,846, cost-state 67, custom-title 7,493, last-prompt 8,925, mode 8,773, queue-operation 4,517 |
| Skipped attachments | 51,957 records of 25 types (the G1 table below) |
| Input lines that do not parse | 22 lines in 13 sources. The JSON breaks in the middle of a record (`Expecting ',' delimiter` or `':' delimiter` at a letter), and the rest of the line is not a record either. They are counted in `bad_lines` and are not exported |

The 1,753 capped notifications: 1,679 are `task_reminder` attachments (the harness's task list; 2,285 records, most over
32,768 characters), 20 queued commands, 20 task-notification user texts, 12 `structured_output` attachments, 12 workflow
journal `result` records, 9 user texts with no `origin`, and 1 `file` attachment. The model read the task reminders, so they
are exported. They take about 55 MB of the 312 MB stream. Skipping them, or keeping one per change, is a coordinator call.

The 11 dropped events and the premise's counts: the premise's per-class counts (3 / 5 / 0 / 0 / 1 / 0) overlap. The 3
`.pc-bridge.env` calls and the 1 `.codiv/api.env` call also match `*.env`. A scan of every `tool_use` block with the
export's own SECRET_PATH finds 5 file-tool calls: Read 2 (one on `.pc-bridge.env`, one on another `.env`) and Write 3 (two
on `.pc-bridge.env`, one on `.codiv/api.env`). 5 calls x 2 events + 1 attachment = 11.

### The brief's three questions

1. Harness fields that hold an outcome beyond `is_error` (each named in a real record: `src`, line):
   - Exported in `outcome`:
     - the first line `Exit code N` of an error result's content (`-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl`
       line 1124; 711 results);
     - `toolUseResult.timedOutAfterMs` (same file, line 5745; 33);
     - the record's `toolDenialKind` (line 3857; 53);
     - `hookErrors` on a `stop_hook_summary` system record (`-home-user-agent-factory/bdab799a-...jsonl` line 246; 286).
     - `is_error` itself is on 36,233 result blocks (main line 17).
   - Found but NOT exported (D-1 fixes the outcome list; adding one is a schema change for the coordinator):
     - `toolUseResult.interrupted` (every Bash result, 14,647; main line 17; 0 of them true);
     - `returnCodeInterpretation` (90; line 1359);
     - `success` (1,312; line 371);
     - `status` (281, Agent results; line 399);
     - `code` (23, a WebFetch HTTP status; line 39597);
     - `truncated` (17; line 5046);
     - `persistedOutputPath` / `persistedOutputSize` (56; line 457; output the harness moved to a file);
     - `backgroundTaskId` (529; line 2470).
     - The API error fields (`isApiErrorMessage`, `error`, `apiErrorStatus`; main lines 913 and 3337) become the `api_error`
       kind (G2), not an outcome.
2. The whole export after the cap: 126,937 events; 311,771,416 bytes of JSONL, 38,706,220 bytes compressed.
3. Thinking blocks: some carry plain text. 4,997 do and are exported (scrubbed); 29,704 carry only a signature.

### G1: every attachment type in the transcripts (38 types; counts up to run 1's offsets)

| What the export does | Types (records) |
|---|---|
| `text` or `notification` by its speaker, deduplicated (G4) | queued_command (1,408) |
| `hook` | hook_success (688), hook_additional_context (613), hook_system_message (3) |
| `harness_notice` (G1) | edited_text_file (488) |
| `notification` | task_reminder (2,285), silent_turn_reminder (1,246), file (336), compact_file_reference (263), task_status (212), date_change (40), structured_output (30), read_truncation_notice (27) |
| counted per type, not exported (meters and configuration: SKIP_ATTACHMENTS) | total_tokens_reminder (40,862), batching_reminder_sent (4,947), deferred_tools_delta (971), environment (669), skill_listing (616), mcp_instructions_delta (553), prompt_snapshot (547), remote_session_change (482), auto_mode (397), nested_memory (367), instructions (304), date (284), model (277), session_context (273), agent_listing_delta (133), deferred_tools_record (121), invoked_skills (77), command_permissions (34), dynamic_skill (22), thinking_drop (7), output_style (6), output_style_instructions (4), ultra_effort_enter (2), ultra_effort_exit (1), auto_mode_exit (1) |

A type that is not in the list (a new harness type) is exported as a `notification` (the test's `future-att` case). The
path denylist applies to every exported attachment: one that names a secret file becomes DROPPED.

## 3. The leak gate (evidence demand 4)

The gate ran inside both exports (each log reads `total 0`; the detached runs' exit codes were not captured) and again
on its own at 2026-09-25T05:59:01Z:
`python3 scripts/session_export.py gate <scratchpad>/session-export --key /root/.config/session-export/pseudonym.key`,
rc 0. Its output, pasted:
```
gate: 317 files, 126937 events, 0 unreadable lines
pattern:private-key 0
pattern:credential 0
pattern:bearer 0
pattern:sk-key 0
pattern:github-token 0
pattern:google-key 0
pattern:slack-token 0
pattern:bridge-link 0
pattern:opaque-run 0
pattern:bridge-host 0
pattern:bearer-tail 0
pattern:basic-auth 0
pattern:url-password 0
total 0
```
It also printed 50 `canary:` lines: the 46 test canaries and the 4 printed forms of the pseudonym key. All 50 read 0 (counted
with grep: `canary lines: 50, non-zero: 0`; the lines are not pasted, because they only list test tags).

What the gate counts: a match of each of the 13 shapes (the 9 SECRET_PATTERNS rules and the 4 PAYLOAD_PATTERNS rules), but
only when the rule would still change it; every canary; and every printed form of the key. It checks every string of every
event. One exemption: the opaque-run rule skips a `tool` or `call_id` that is one identifier, because harness tool names
and call ids can be 40 or more characters (`mcp__Claude_Code_Remote__register_repo_root` has 43). What it cannot see: a secret in a shape it does not know (section 7, item 1).

The canary tests (green in both test_summary runs, section 6):
- `test_no_canary_survives_the_export` plants 46 FAKE canaries, each in its payload shape: a Write of a `.env` file; a Bash
  result that prints env lines; a `grep -n` over an env file; a key file printed through Bash and read through Read; a curl
  config with the token header; bridge links and bare bridge hosts; Bearer and Basic headers; a URL password; a PEM block;
  GitHub-token shapes in thinking, in a tool result and in a workflow journal; a hook's stdout; a queued command; an edited
  file's snippet; a Bash file change; two pruner archives; a Read of the pseudonym key file; and more. It asserts that none
  survives in the export or in the CLI's output, and that the gate reads 0.
- `test_the_canaries_show_when_the_protections_are_off` is its negative control: with the scrubbers and the denylist off,
  every canary the export reads reaches the output and the gate counts each one.
- `test_gate_counts_patterns_and_canaries_and_prints_none` checks the gate's own counts on planted shapes and that it prints
  no match.

## 4. The shipper (evidence demand 5)

`scripts/ship_to_pc.py <export dir> <remote dir>` (its docstring holds the full design):
- It checks the export before any call:
  - `manifest.json` is readable;
  - its gate reads total 0 and 0 unreadable lines (rc 3 otherwise);
  - every listed output is present with the manifest's sha256 and has a safe relative path (rc 2 otherwise);
  - the remote dir is absolute, not `/`, and has no `..` (rc 2 otherwise).
- The bridge URL and token come from `<repo>/.pc-bridge.env`, read in process. curl gets them on stdin (`--config -`), never
  in argv. curl's own error text is never printed, because it can name the bridge link.
- Chunks: 72,000 bytes each, which is 96,000 base64 characters. One chunk command is about 96,300 bytes, under the 131,072
  limit. Up to 4 calls are in flight.
- On the PC:
  - a chunk is decoded to a temp name and kept only when its sha256 matches; otherwise the PC answers rc 5, and the chunk is
    sent again, at most 3 times;
  - a join checks the whole file's sha256 against the manifest (rc 7 otherwise). A join is idempotent: a file already in
    place with the right sha256 returns 0.
- Each run first lists the PC's finished files and kept chunks, with their sha256s, and then sends only what is missing or
  differs. `manifest.json` ships last, and only when every file it lists is in place.
- Exit codes: 0 done; 2 bad input; 3 the gate is not 0; 4 the bridge refused the token, or the PC could not be listed; 5 not
  complete (a rerun resumes).

Tests: `tests/test_ship_to_pc.py`, 5 tests, all green (section 6).
- Test setup:
  - The export is a real `session_export.py` export of 3 transcripts in 2 folders; its largest file has 5 chunks.
  - Each test runs a copy of the shipper in a temp tree whose `.pc-bridge.env` names a fake bridge on 127.0.0.1. This is the
    tests/test_pc_sh.py pattern: the real bridge cannot be reached from a test. Proxy variables are removed from the
    environment.
  - The fake bridge runs each command with bash in a temp dir that stands for the PC.
  - Every run asserts that neither the token nor the URL (nor `127.0.0.1`) is printed.
- `test_every_file_arrives_whole_in_bounded_chunks_and_the_manifest_last`:
  - every file's sha256 on the PC equals the manifest's, and no staged chunk is left;
  - each chunk of the largest file is sent once;
  - the largest base64 in one call is exactly 96,000 characters, and every command is under 131,072 bytes;
  - between 2 and 4 calls are in flight;
  - the first call is the listing, and the manifest's chunk and join come after every other join;
  - a rerun makes one listing call and sends nothing.
- `test_a_dropped_chunk_resumes_from_the_verified_chunks`:
  - chunk 1 of the largest file is dropped: it gets a gateway page 3 times and never runs;
  - the run exits rc 5, does not send the manifest, and the PC keeps chunks 0, 2, 3 and 4;
  - the rerun sends exactly chunk 1, that file's join, the manifest's chunk and the manifest's join, and every sha256 matches.
- `test_a_corrupted_chunk_is_refused_on_the_pc`:
  - one base64 character is changed in transit once: the PC refuses the chunk (rc 5), keeps the resend (rcs `[5, 0]`), and the
    file arrives whole;
  - the character is changed on every send: 3 refusals, chunk 2 is never kept, there is no join and no manifest, and the run
    exits rc 5.
- `test_a_wrong_token_is_refused`: the run exits rc 4 with `the bridge refused the request (forbidden)`; neither token is
  printed; the fake runs nothing.
- `test_a_bad_export_is_refused_before_any_call`: 8 cases, and 0 calls in all of them:
  - a gate that found something (rc 3);
  - a changed file, a missing file, an output path with `..`, a relative remote dir, `/`, a remote with `..`, and no env
    file (rc 2 each).

Red evidence: the shipper tests passed on their first run, so they were NOT red first. Mutants S1-S5 (section 5) each turn
at least one of them red. NOT run: the real bridge (the brief forbids contact).

## 5. Mutants (evidence demand 6)

`sx/mutants.py` works on scratch copies only; the repo tree is never edited. For each mutant it copies the lane's 6 files
(and `tests/conftest.py`, `pyproject.toml`) to a scratch dir, makes one edit, and runs the named test files there with `-v
--tb=no -rN`, so it prints only test ids and outcomes. Then it deletes the copy. The final run over the final files was at
2026-09-25T06:11:46Z-06:13:28Z. Its summary lines, pasted:

| Mutant | The edit | pytest summary | Red tests |
|---|---|---|---|
| M1 one scrub rule removed (the new Basic-auth rule) | its PAYLOAD_PATTERNS line deleted | 4 failed, 22 passed | test_no_canary_survives_the_export (the canary survives); test_gate_counts_patterns_and_canaries_and_prints_none; test_fixed_offsets_give_byte_identical_output and test_offsets_refuse_a_changed_prefix_or_archive (in both, the first export's gate is 3) |
| M2 one scrub rule removed (the existing GitHub-token rule) | its SECRET_PATTERNS line deleted | 5 failed, 21 passed | the 4 above and test_opaque_values_become_stable_keyed_pseudonyms (the 44-character token becomes a pseudonym) |
| M3 the denylist emptied | SECRET_PATH never matches | 8 failed, 18 passed | test_secret_paths_are_dropped_or_strict_passed, test_no_canary_survives_the_export, test_edited_files_are_harness_notices, test_bash_file_changes_follow_the_result, test_pruner_archives_follow_their_results, test_convert_in_parts_gives_the_same_events_as_one_pass, test_fixed_offsets..., test_offsets_refuse... |
| M4 the cap off | `elif len(text) > limit:` becomes `elif False:` | 3 failed, 23 passed | test_cap_keeps_head_and_tail, test_read_results_and_write_inputs_get_the_large_cap, test_the_cap_seam_forms_no_secret_shape |
| M5 the offset ignored (read to the end of the file) | `end = None` at the start of convert() | 1 failed, 25 passed | test_fixed_offsets_give_byte_identical_output (the rerun reads past its offset, and the guard refuses with rc 2) |
| M6 G6: a fixed key | the HMAC key becomes 32 zero bytes | 1 failed, 25 passed | test_opaque_values_become_stable_keyed_pseudonyms |
| M7 G6: the pseudonym on a named-rule match | the opaque-run rule runs first, with the callable | 8 failed, 128 passed | test_named_rules_take_a_long_value_before_the_opaque_rule (6 cases), test_payload_rules_leave_every_pinned_fixture_as_scrub_leaves_it, test_opaque_values_become_stable_keyed_pseudonyms |
| A1 one project folder | the source glob reads `-home-user` only | 5 failed, 21 passed | test_every_project_folder_is_read, test_events_keep_the_schema, test_no_canary_survives..., test_fixed_offsets..., test_the_cap_seam... |
| A2 the state not carried | Source drops the state it is given | 1 failed, 25 passed | test_convert_in_parts_gives_the_same_events_as_one_pass |
| A3 the archives ignored | no archive lookup | 4 failed, 22 passed | test_pruner_archives..., test_secret_paths... (the strict count), test_the_canaries_show_when_the_protections_are_off (the archive canaries), test_fixed_offsets... |
| G1 an edited file as a notification | `elif False:` | 1 failed, 25 passed | test_roles_follow_the_transcript_type |
| G2 the model dropped | `"model": None` | 1 failed, 25 passed | test_model_and_stop_reason_come_from_the_record |
| G3 the large cap off | `big = False` | 2 failed, 24 passed | test_read_results_and_write_inputs_get_the_large_cap, test_pruner_archives... |
| G4 no dedupe | `if False:` | 1 failed, 25 passed | test_a_repeated_notification_is_kept_once |
| G5 bashEditDiff ignored | `if False:` | 3 failed, 23 passed | test_bash_file_changes..., test_secret_paths..., test_the_canaries_show... |
| S1 no sha256 check on the PC | the chunk's check always passes | 1 failed, 4 passed | test_a_corrupted_chunk_is_refused_on_the_pc |
| S2 the listing ignored | the listing returns nothing | 2 failed, 3 passed | test_a_dropped_chunk_resumes_from_the_verified_chunks, test_every_file_arrives_whole_in_bounded_chunks_and_the_manifest_last |
| S3 the manifest first | the manifest ships before the files | 3 failed, 2 passed | test_every_file..., test_a_dropped_chunk..., test_a_corrupted_chunk... |
| S4 eight calls in flight | IN_FLIGHT = 8 | 1 failed, 4 passed | test_every_file... (more than 4 in flight) |
| S5 chunks over 96,000 characters | CHUNK = 100000 | 3 failed, 2 passed | test_every_file..., test_a_dropped_chunk..., test_a_corrupted_chunk... |

A finding the mutants forced (fixed in the test, verified): at first M7 left `test_opaque_values_...` green. Its only
named-rule case was a credential assignment (`PC_BRIDGE_TOKEN=<40 characters>`). There, the fixed-point loop redacts the
pseudonym on its second pass, because the credential rule takes `[opaque:...]` as a value. The test now also has a
44-character GitHub-token case (`long-gh`), which no second pass repairs, and M7 turns it red. At the scrubber level, M7 was
red from the start (`test_named_rules_take_a_long_value_before_the_opaque_rule`).

Failure output holds no canary (verified): `sx/failure_output_check.py` ran the 15 non-shipper mutants again with
`--tb=short` and searched each full output, in process, for every canary and every 8-character window of one. The result
was `canaries in it: []` for all 15. To make this hold, every text comparison in `tests/test_session_export.py` goes through
`_expect`. On a mismatch it reports the first differing character, both lengths and the NAMES of the canaries in the actual
text, never the text. A printed canary would reach this session's transcript, and the next real export's gate counts
canaries.

## 6. Gates (evidence demand 7)

`bash scripts/test_summary.sh tests/test_transcript_export.py tests/test_session_export.py tests/test_ship_to_pc.py`, twice
(2026-09-25T06:00:13Z and 06:00:26Z), pasted:
```
141 passed in 12.42s
pytest-exit: 0
pytest-summary: 141 passed in 12.42s
```
```
141 passed in 12.39s
pytest-exit: 0
pytest-summary: 141 passed in 12.39s
```
(110 in test_transcript_export.py, 26 in test_session_export.py, 5 in test_ship_to_pc.py.)

- `bash scripts/pc_suite.sh set-id -- tests/test_transcript_export.py tests/test_session_export.py tests/test_ship_to_pc.py`:
  `3 files set=6dde7977ceba`.
- `pyflakes` on the 6 Python files: rc 0, no output.
- `python3 scripts/no_laya_in_gates.py`: `no_laya_in_gates: 41 files scanned, clean`, rc 0.
- `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` on the 6 Python files and this report: 0 in each (the last check ran after the last
  edit to this report).
- The chat export on its 77 fixtures: byte-identical 77 of 77 (section 1).

Expected red outside this lane, verified: `tests/test_laya_ft.py::test_version_2_record_rebuilds_byte_identically_at_the_pin`
fails in the shared tree (`1 failed in 69.20s`, run with `S0_01_VENUE=sandbox`). The rebuilt dataset manifest differs at
byte 707: the first character of the sha256 it records for `scripts/transcript_export.py` (`f63cd97e...` at HEAD,
`395db6dd...` with this change). This is the DSV2 record the coordinator regenerates at the harvest. The rest of that file
passed (`1 failed, 41 passed in 516.63s`). Not my file: not touched.

## 7. Self-attack: the three most likely ways this change is wrong

1. A secret in a shape the scrubber does not know passes through. The gate only knows the scrubber's 13 shapes, the canaries
   and the key's forms, so its 0 says nothing about unknown shapes. The strict pass runs only where a call names a secret
   path. Two residual examples: a token under 40 characters that a command which names no secret path prints alone (`echo
   $VAR`), and a password written in prose. How far this is ruled out: partly. Measured: 0 matches in 126,937 events; 11
   payloads dropped; 2,543 results strict-passed. The step that would cut the risk further is a known-values check: count,
   in process, each value of `.pc-bridge.env` and of the key files in the export, counts only. NOT built, because the brief
   forbids searching the records for secrets; it is the coordinator's call.
2. Roles or kinds are wrong for real record shapes that the fixtures miss. Ruled out as far as the surveys reach. The
   fixtures copy the real shapes: compact JSON and the harness's field names, surveyed over all 317 files. Every record
   type and attachment type in the data is named in section 2 with what the export does with it. The one failure in this
   session came from a fixture that was NOT in the real shape: the test wrote spaced JSON (`"cwd": "`), which 0 of the 317
   real files hold, so the archive lookup found no directory. The fixture was fixed, not the code.
3. The shipper fails on the real bridge in a way the fake does not show. The fake runs the same bash commands, but the PC adds
   the tirith bash hook, the tunnel, and the bridge's own limits. The 96,000-character chunk is the brief's number; the size
   proven through this bridge is 40,000 (`scripts/pc_suite.sh:73`, `scripts/pc_lane.sh:265`). Not ruled out, because no
   bridge contact was allowed. It fails loud: an over-size or refused call leaves the file unjoined and the manifest unsent
   (rc 4 or 5), and a rerun resumes. Watch the first real run; if chunk calls end with `no JSON reply`, lower `CHUNK`.

Two smaller risks:
- Pseudonyms join only under one key. A new key changes every pseudonym, so exports made under two keys do not join.
- A secret that no named rule knows, 40 or more characters long, becomes a stable pseudonym: it can be linked across events,
  but it cannot be reversed without the key. This is G6's intended trade.

## 8. NOT-done (first-class)

- The shipper has NOT run against the real bridge (forbidden to this lane); the coordinator ships. Nothing is committed (the
  coordinator commits).
- 22 input lines in 13 sources do not parse, and they are neither exported nor recovered.
- Pruner archives named by the clock (`bash-<Date.now()>.txt`) cannot be linked to a call. The export counts them
  (`archives_unlinked`) and does not emit them. There are none today.
- The harness outcome fields beyond D-1's list are not exported (section 2 lists them).
- `task_reminder` attachments are exported whole: 1,679 of them capped, about 55 MB of the stream. Repeated task lists are
  not deduplicated.
- The strict pass follows the call id. So background output files, Monitor events and TaskOutput results of a command that
  named a secret path pass only the normal scrub, because they arrive under other ids. A Bash command that names a secret
  path keeps its own text with the normal scrub, as D-2 says.
- The gate has no known-values check (section 7, item 1).
- The premise's TEST probe was not re-measured: the brief does not define a test command or its outcome.
- Adjacent defects, reported and not fixed:
  - the other consumers of `scrub` miss the four payload shapes (section 1);
  - the G4 premise was contradicted (section 1b), and DATA-SESSION or JEV-MAP counts built on "twice-recorded" notifications
    may be off.
- `tests/test_laya_ft.py::test_version_2_record_rebuilds_byte_identically_at_the_pin` is red in the shared tree while this
  change is there (section 6). It is not regenerated here: not my file.
- Red first: the scrubber's tests were red first (31, then 7 more for G6). The exporter's amendment tests and the shipper's
  tests were written after the code and passed on their first run. Their red is shown by mutants only (section 5).
- GitNexus `detect_changes` was not run: the coordinator commits. The new names (`scrub_payload`, `scrub_strict`,
  `PAYLOAD_PATTERNS`) are used only in this lane's four files (a literal sweep).
