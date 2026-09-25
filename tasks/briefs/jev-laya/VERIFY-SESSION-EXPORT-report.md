# VERIFY-SESSION-EXPORT report (task #252; orchestration 0f; D-031)

Role: adversarial-verifier (sandbox, Opus 5.5). Brief: `tasks/briefs/jev-laya/VERIFY-SESSION-EXPORT-brief.md`. PIN: db1de1c
(`db1de1cb138e95d1840cbf25b2078b3d61f891e3`, on origin/claude/soundbox-kit-migration-iz1jwf). Contract:
`tasks/briefs/jev-laya/SESSION-EXPORT-brief.md` + AMENDMENT 1 (G1-G6) + AMENDMENT 2. Builder's report:
`tasks/briefs/jev-laya/SESSION-EXPORT-report.md`.

Venue: a clean detached worktree at the PIN,
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-session-export/wt` (added 2026-09-25T06:24Z).
Scratch: the same `verify-session-export/` dir. No network, no bridge, no subagents.

STATUS: DONE 2026-09-25T07:32:03Z (started 06:24:34Z). GATE RECOMMENDATION: **NOT-READY** (one blocker, F-1; the
coordinator owns the gate).

TL;DR: A token or password assigned under a name the scrubber knows, inside a double-quoted value, survives the export
when it sits in a tool input, a hook, a notification or a system record: the exporter writes these as JSON before it
scrubs, the escaped quote (`\"`) hides the value from the credential rule, and the leak gate (the same rules) reads 0.
Reproduced through the real CLI (7 of 7 shapes; a 44-character token under `PC_BRIDGE_TOKEN` becomes a pseudonym,
against G6). The real export holds 145 such values; 25 of the 42 distinct ones are repo fixtures, 17 are unexplained.
One added payload rule fixes the fixtures with the builder's 141 tests green. Also returned: two CONTRACT-DEFECTs (the
opaque-run rule pseudonymises 1,860 repo test names; the strict pass eats PC results of commands that only source the
env file) and seven follow-ups. Everything else held: completeness exact, the converter exact at every tested offset,
determinism, the pseudonym properties, the shipper against every remote attack.

- [x] Premise re-measured: 6 hashes, 3 line numbers, 141 passed twice, set 6dde7977ceba (sections 0-1)
- [x] Attack 1 (secrets that survive): 29 of 38 shapes leak; 7 are F-1, the rest follow-ups (sections 2, 7, 8)
- [x] Attack 2 (scrubbing too much): F-2, F-3 (section 5)
- [x] Attack 3 (pseudonyms): hold, except the escaped token (section 3)
- [x] Attack 4 (converter): 1,086 splits and 9,526 every-byte splits, 0 mismatches (section 9)
- [x] Attack 5 (completeness): 244,494 of 244,494 lines accounted (section 6)
- [x] Attack 6 (shipper): 17 of 18 cases, the one miss outside its stated use (section 10)
- [x] Attack 7 (regressions): scrub unchanged, chat export byte-identical on 5 real transcripts, importers green (section 11)
- [x] New mutants: 37, 30 red (section 12)

## 0. Premise re-measure (evidence demand 1)

```
$ git show db1de1c:<file> | sha256sum | cut -c1-16      (the worktree, 06:24Z)
395db6ddefe0e7fc  scripts/transcript_export.py
a402db33b776d1a7  tests/test_transcript_export.py
7bf26338e88c7bcc  scripts/session_export.py
05f83f7a0636c5dd  tests/test_session_export.py
39c88510acb21ee2  scripts/ship_to_pc.py
37cc6c042aea1771  tests/test_ship_to_pc.py
$ grep -n 'def scrub(\|def scrub_payload\|def scrub_strict' scripts/transcript_export.py
85:def scrub(text: str) -> str:
110:def scrub_payload(text: str, opaque=None) -> str:
140:def scrub_strict(text: str, opaque=None) -> str:
```

All six hashes and the three line numbers match the brief's premise block.

## 1. Gates at the PIN, clean worktree (evidence demand 4)

```
$ bash scripts/test_summary.sh tests/test_transcript_export.py tests/test_session_export.py tests/test_ship_to_pc.py   (06:24:50Z)
141 passed in 14.78s
pytest-exit: 0
pytest-summary: 141 passed in 14.78s
$ (the same, 06:25:05Z)
141 passed in 13.29s
pytest-exit: 0
pytest-summary: 141 passed in 13.29s
$ bash scripts/pc_suite.sh set-id -- tests/test_transcript_export.py tests/test_session_export.py tests/test_ship_to_pc.py
3 files set=6dde7977ceba
```

`git status --short` in the worktree was empty after both runs (the tests write only to temp dirs).

## 2. Attack 1: secrets that survive the real exporter (reproduced)

Harness: `verify-session-export/h/vfx.py` (record shapes, FAKE canaries made at runtime from a hash; nothing prints a
value) and `h/attack1.py`. It builds one transcript in the harness's compact record shapes with 38 shapes, one FAKE
canary each, runs the real CLI (`scripts/session_export.py export --root <fixture> --out <dir> --jobs 1 --key <my key>`),
and counts each canary's leak form in the decompressed output (full value, or any 8-character window). The positive
control runs the same tree with the scrubbers and the denylist off (the builder's own negative-control method): every
leak form appeared there, so each shape reaches the output path it claims to test.

Result (`python3 h/attack1.py <scratch>/a1`, pasted; tags and counts only):

```
export rc 0; gate total 0
protections-off export rc 3
tag                  expect    leaks  full  shape (positive control: present when off)
ctl-raw-assign       scrubbed  -      0     Bash result, raw NAME=value
ctl-json-result      scrubbed  -      0     Bash result, raw JSON "token": "v"
ctl-quoted-raw       scrubbed  -      0     Bash result, raw NAME="v"
short-echo           ?         LEAK   1     Bash `echo $VAR` result, 32 hex, bare
printenv-bare        ?         LEAK   1     Bash `printenv NAME` result, 24 alnum, bare
printenv-44          ?         -      0     Bash `printenv NAME` result, 44 url-safe, bare
split-lines          ?         LEAK   1     Bash result, NAME=\<newline> value (line continuation)
split-events         ?         LEAK   1     NAME= at the end of one result, the value at the start of the next
b64                  ?         -      0     Bash result, base64 of NAME=value
urlenc-pass          ?         LEAK   1     URL-encoded password%3D<v>
urlenc-link          ?         -      0     URL-encoded bridge link https%3A%2F%2F<host>
json-cmd-export      ?         LEAK   1     tool_call: Bash command with NAME="v" (canonical JSON)
json-cmd-body        ?         LEAK   1     tool_call: Bash command with a JSON body "password": "v"
json-write-cfg       ?         LEAK   1     tool_call: Write of a JSON config "api_key": "v"
json-edit-yaml       ?         LEAK   1     tool_call: Edit new_string token: "v"
json-hook            ?         LEAK   1     hook attachment stdout {"token": "v"}
json-notif           ?         LEAK   1     notification attachment secret: "v"
json-stophook        ?         LEAK   1     stop_hook_summary hookErrors password="v" (text is canonical JSON)
url-pass-at          ?         LEAK   1     https://user:pa@ss@host (a raw @ in the password)
url-token-user       ?         LEAK   1     https://<token>@host (token as the user, no colon)
curl-u               ?         LEAK   1     tool_call: curl -u user:pass
bearer-lower         ?         LEAK   1     Bash result, lowercase `authorization: bearer v`
netrc                ?         LEAK   1     Bash `cat ~/.netrc` result: password <v> (space, no =)
unlisted-name        ?         LEAK   1     Bash `printenv` result DB_PASS=v (a name outside the list)
secret-key-base      ?         LEAK   1     secret_key_base: v (a compound name the rule misses)
docker-auth          ?         LEAK   1     docker config "auth": "<b64 user:pass>"
thinking-prose       ?         LEAK   1     thinking block, prose `the password is v`
diff-json            scrubbed  -      0     file_change diff line +  "token": "v" (raw text)
archive-bare         ?         LEAK   1     pruner archive holding a bare token
glob-keyfile         ?         LEAK   1     Bash `cat ~/.config/qwen-*/api-key` (glob) result
rel-keyfile          ?         LEAK   1     Bash `cd ~/.config/qwen-builder && cat api-key` (relative) result
dot-keyfile-read     ?         LEAK   1     Read /root/.config/qwen-builder/./api-key
dslash-keyfile-read  ?         LEAK   1     Read /root/.config/qwen-builder//api-key
symlink-read         ?         LEAK   1     Read of a symlink made to omniroute.key one call earlier
quoted-glob-env      ?         LEAK   1     Bash `cat '.pc-bridge.e'*` result ZQ_ENDPOINT=v (strict would take it)
bg-output            ?         LEAK   1     background `cat .../qwen-builder/api-key`, output read by TaskOutput
grep-dir             ?         -      0     Grep over the qwen-builder dir (input names the dir only)
mcp-arg              ?         -      0     tool_call: an MCP tool input {"password": v}
survivors 29 of 38: short-echo printenv-bare split-lines split-events urlenc-pass json-cmd-export json-cmd-body json-write-cfg json-edit-yaml json-hook json-notif json-stophook url-pass-at url-token-user curl-u bearer-lower netrc unlisted-name secret-key-base docker-auth thinking-prose archive-bare glob-keyfile rel-keyfile dot-keyfile-read dslash-keyfile-read symlink-read quoted-glob-env bg-output
```

The export exits 0 and its own leak gate reads `total 0` with 29 FAKE canaries in the output. The CLI printed none.

The exported bytes of the JSON-escape class (`h/inspect1.py`, each canary masked as `<C:tag>`), pasted:

```
line 25 coordinator/tool_call tool=Bash: {"command":"export PC_BRIDGE_TOKEN=\"<C:json-cmd-export>\" && bash scripts/pc.sh ls","description":"vfy"}
line 27 coordinator/tool_call tool=Bash: {"command":"curl -s -d '{\"password\": \"<C:json-cmd-body>\"}' https://api.example.com/login","description":"vfy"}
line 29 coordinator/tool_call tool=Write: {"content":"{\n  \"api_key\": \"<C:json-write-cfg>\",\n  \"region\": \"eu\"\n}\n","file_path":"/home/user/agent-factory/cfg/service.json"}
line 31 coordinator/tool_call tool=Edit: {"file_path":"/home/user/agent-factory/cfg/app.yaml","new_string":"token: \"<C:json-edit-yaml>\"","old_string":"token: \"x\"","replace_all":false}
line 33 hook/hook tool=None: {...,"stdout":"{\"token\": \"<C:json-hook>\"}","toolUseID":"toolu_vfy_hook","type":"hook_success"}
line 34 system/notification tool=None: {"data":{"note":"secret: \"<C:json-notif>\""},"type":"structured_output"}
line 35 hook/hook tool=None: {...,"hookErrors":["retry with password=\"<C:json-stophook>\""],...}
```

Mechanism (re-derived from primary source, `scripts/transcript_export.py:27-68`): the credential rule is
`(NAME["']?\s*[:=]\s*["']?)(?=_V{8})(_VALUE)` with `_V = [^\s"'&,;]`. In raw text `NAME="v"` matches (the optional
quote takes the `"`). The exporter canonicalises tool inputs (`session_export.py:433`), hook and other attachments
(`:509-513`), system records (`:516`) and journal records (`:407`) with `json.dumps` BEFORE scrubbing, so a quote inside
a string becomes `\"`. The rule cannot take the backslash as its optional quote, and its 8-character lookahead fails on
the `"` that follows it (`"` is not in `_V`), so `NAME=\"v\"` and `"name": "v"` nested in a string match nothing. The
leak gate (`gate_file`, `:694-723`) runs the same patterns over the same escaped text, so it cannot see these either.
The same line in a raw result is scrubbed (controls `ctl-quoted-raw`, `ctl-json-result`). A top-level input key is
not escaped (`mcp-arg`: `{"password":"v"}` is caught); only a JSON document or quoted value INSIDE a string field is.

Two expectations of mine that the run corrected: the URL-encoded link is caught (the bare-host rule matches from the
`2F` of `%2F`, so the host goes; verified in process), and `grep-dir` is caught (the credential rule reads the file name
`api-key` followed by `:` as a `-key` assignment).

## 3. Attack 3: pseudonyms (reproduced)

`h/attack3.py`: two transcripts in two project folders; the real CLI run twice with key 1 and once with key 2 (each key
made by the CLI's own `init-key`). Pasted:

```
k1-run1: rc 0
k1-run2: rc 0
k2: rc 0
SHA_A pseudonym under k1, count per folder (owner text + tool_call + tool_result = 3 each): {'-vfy-a': 3, '-vfy-b': 3}
SHA_A pseudonym equals HMAC-SHA256(k1, value)[:12] computed here: True
raw SHA_A / SHA_B in the k1 export: False False
two runs, same key: outputs byte-identical (per .xz sha): True
another key gives another pseudonym: True
k1 in any printed form in any output or CLI text: False
tok44-raw     raw-in-export False pseudonymised False
tok44-esc     raw-in-export False pseudonymised True
tok44-cmdarg  raw-in-export False pseudonymised False
gh-long       raw-in-export False pseudonymised False
bearer-long   raw-in-export False pseudonymised False
sk-long       raw-in-export False pseudonymised False
the escaped call as exported: {"command":"export PC_BRIDGE_TOKEN=\"[opaque:<hmac of the token>]\" && bash scripts/pc.sh ls"}
```

Stable across files and runs: yes. Keyed: yes. The key in no output: yes. A named-rule value redacted, not pseudonymised:
yes in raw text (5 of 5 shapes), NO in canonical JSON: a 44-character `PC_BRIDGE_TOKEN` value inside a tool call becomes
`[opaque:<hmac>]`, because the escaped quote hides it from the named rule and only the opaque-run rule sees it. AMENDMENT 1
G6 says a value a named rule catches (token names first in its list) stays fully redacted and never becomes a pseudonym.

## 4. The real export, reproduced at the builder's offsets (counts only)

My own export at the PIN over the real transcripts, with MY key (made by `init-key` in my scratch; the real key was not
read) and the builder's manifest as `--offsets` (so it reads the same bytes; `--offsets` refuses any input whose sha256
differs, and it did not). Pasted, the canary lines left out (50 of them, all 0):

```
$ python3 wt/scripts/session_export.py export --out <scratch>/real-export --offsets <builder>/session-export/manifest.json --key <my key> --jobs 4
rc=0   (06:41:59Z to 06:48:00Z)
export 2026-09-25T06:41:59Z: 317 sources, 1178943962 bytes read, 38705784 bytes written, 361.2 s
folders {"-home-user-agent-factory": {"sources": 1, "bytes_read": 3074681}, "-home-user": {"sources": 316, "bytes_read": 1175869281}}
events {"api_error": 72, "file_change": 2796, "harness_notice": 488, "hook": 2644, "notification": 6684, "pruner_archive": 1, "summary": 131, "text": 16267, "thinking": 4997, "tool_call": 46435, "tool_result": 46422}
capped {"hook": 2, "notification": 1753, "summary": 2, "text": 37, "tool_call": 40, "tool_result": 20}
dropped_secret_path 11 strict_results 2543 unsettled 0 seam_adjusted 0 thinking_signature_only 29704 duplicate_notifications 2 file_changes_unrecorded 364 pseudonyms 69846 pruner_archives 1 archives 1 archives_skipped 0 archives_unlinked 0 archives_unmatched 0
gate: 317 files, 126937 events, 0 unreadable lines
pattern:... 0 (all 13)
total 0
```

Every count equals the builder's run 1 (report section 2). Only `bytes written` differs (38,705,784 against 38,706,220):
another key gives other pseudonym hex, so xz compresses differently.

### 4a. The JSON-escape class in the real export (counts only; no value read or printed)

`h/escaped_count.py` counts a credential NAME (the scrubber's own name list), an optional escaped quote, `:` or `=`, then an
ESCAPED quote and a value, and sorts each value by structure in process. Positive control first: on the attack-1 export it
finds exactly the 7 planted escaped shapes (`tool_call 4, hook 2, notification 1`). On the real export (pasted totals):

```
--- totals by bucket: {'UPPER-placeholder': 1, 'already-scrubbed': 27, 'letters+digits 20-39': 102, 'letters+digits 40+': 1, 'letters+digits 8-19': 42, 'lowercase-word': 66, 'other': 55, "under-8 (below the rule's floor)": 699, 'variable-or-template': 113}
```

145 values of 8 or more characters with letters and digits (the shape the credential rule takes in raw text) sit behind an
escaped quote after a credential name, 143 in tool calls and 2 in harness notices. The rule and the gate saw none.
`h/escaped_count2.py` then checked each exact value, in process, against every git-tracked file of the worktree:

```
distinct values 42 | occurrences 145
distinct values also in a tracked repo file: 25
occurrences bridge-name  in-repo      1
occurrences other-name   NOT-in-repo  25
occurrences other-name   in-repo      119
```

25 of the 42 are committed test fixtures (fake by the repo's rules). The other 17 (25 occurrences), none after a bridge
name, are in subagent transcripts (build and verify lanes), under names such as `nfake_key`, `owner_key`, `token`,
`password`. `h/escaped_list.py` prints a pointer per value (name, length, character classes, kind, tool, src, line; no value
and no part of one); the list is in `<scratch>/verify-session-export/` and can be regenerated. Whether any of the 17 is a
real secret is UNVERIFIED: I did not read them (standing rule). The names suggest fixtures.

## 5. Attack 2: what the scrub removes from ordinary text (reproduced, counts)

`h/attack2.py` runs the production `convert()` over every real transcript to the builder's offsets, in 4 processes, with
the production pseudonymizer wrapped: each opaque-run match is classified at the moment the pipeline takes it (no second
regex pass). Values are printed only for classes proven to be repo code identifiers or repo paths (a `def`/`class` name or
a git-tracked path component of the worktree). Pasted (06:54:24Z to 06:58:18Z):

```
opaque-run matches pseudonymised: 109328
  repo test name                         44541   40.7%
  kebab-case                             29877   27.3%
  hex64 (sha256)                         12886   11.8%
  hex40 (commit id)                       7824    7.2%
  repo path component                     4709    4.3%
  test_* not defined in the tree now      4665    4.3%
  mixed case+digits (blob or token)       1400    1.3%
  other                                   1335    1.2%
  lower_snake other                        884    0.8%
  repo def/class name                      729    0.7%
  mcp tool name                            196    0.2%
  hex other length                         154    0.1%
  UPPER_SNAKE                              108    0.1%
  harness id                                20    0.0%
  top repo test name (repo identifiers; safe to show): test_spec_negative_leg_counts_meet_the_registry_floor_except_the_declared_shortfall x1364, test_golden_non_async_kind_order_binds_through_check_golden x821, test_golden_two_async_records_in_opposite_raw_orders_normalize_identically x818, test_committed_negative_leg_cmd_reports_the_protocol_violation x814, test_explicit_gpg_symlink_is_refused_before_any_process_runs x689, test_leg_file_table_matches_the_runner_writes x539
  distinct repo test name: 1860
  top repo def/class name (repo identifiers; safe to show): _assert_ck16_classifier_operand_contract x729
  distinct repo def/class name: 1
  top repo path component (repo identifiers; safe to show): s0-01-d5n-backend-one-atomic-write-primitive-the-drain-bounded x782, 2026-09-23-bug-echo-fail-open-line-parser x773, s0-06-m2-four-scope-the-leak-agent-seeded-the-oracles-scoped-the-shapes-named x373, s0-03-o3-omniroute-the-collector-complete-the-screen-recursive-the-call-exact x297, RESEARCH-FINDINGS-2-part1-laya-sieve-fp32-build-spec x122, s0-01-a5j-checker-the-class-not-the-instance x116
  distinct repo path component: 57
strict pass:
  assign-line values redacted              3706
  chars after the payload pass             6139997
  key-run chars redacted                   210680
  key-run redactions                       5783
  key-run: a repo path                     1783
  key-run: hex                             3
  key-run: other                           1320
  key-run: other path-like                 2637
  key-run: test path or name               40
  texts (every strict pass call)           4353
  top repo paths the strict pass redacts: tests/test_s0_01_check_acp_conformance x104, tests/test_s0_01_acp_probe x53, proofs/S0-01/tools/pc/pc_launch x43, tests/test_s0_01_scripted_backend x41, proofs/S0-01/tools/acp_probe x37, proofs/S0-01/check_acp_conformance x30
```

(109,328 is counted at scrub time, before the cap; the builder's 69,846 counts pseudonyms left in the exported text after
the cap, which cuts the 1,753 capped notifications. `texts` counts strict-pass CALLS: `settle` calls it again for its
fixed-point check.)

Answer to the brief's question: yes, the export's pass is the same rule as the plain `scrub`
(`\b[A-Za-z0-9_\-]{40,}\b`), so every test name, slug or path component of 40 or more identifier characters is taken. It
becomes a stable pseudonym instead of `<opaque-redacted>`, so the same name still joins across events, but its words are
gone. The sha256 and commit ids G6 was written for are 19.0% of what the rule takes; 1,860 distinct repo test names are
40.7%. A Jev that learns "this edit, then this test failed" keeps the join and loses the test's name.

The strict pass: `h/survey.py` split the 2,096 Bash calls whose command names a secret path. 1,190 only SOURCE
`.pc-bridge.env` (`. ./.pc-bridge.env` or `source`), which prints nothing from it; their 1,189 results are strict-passed like
the 905 results of calls that could print it. That is where the 1,783 repo-path redactions above come from (every PC suite
and lane run over the bridge sources the env file).

## 6. Attack 5: completeness (reproduced, counts)

`h/survey.py` reads every real transcript to the builder's offsets (record types and shapes only) and joins each input
line with my export's event lines. Pasted (06:59:37Z):

```
input lines 244494 (manifest totals.lines: see report); sources whose line or bad-line count differs from the manifest: 0
  bad line                                                               22
  line with events                                                       124138
  no events: maybe-duplicate-notification                                2
  no events: skipped_attachment:<25 types>                               51957  (per type below)
  no events: skipped_record:ai-title 51, atis-latch 8846, cost-state 67, custom-title 7493, last-prompt 8925, mode 8773, queue-operation 4517
  no events: thinking_signature_only (whole record)                      29703
attachment types (38): agent_listing_delta 133, auto_mode 397, auto_mode_exit 1, batching_reminder_sent 4947, command_permissions 34, compact_file_reference 263, date 284, date_change 40, deferred_tools_delta 971, deferred_tools_record 121, dynamic_skill 22, edited_text_file 488, environment 669, file 336, hook_additional_context 613, hook_success 688, hook_system_message 3, instructions 304, invoked_skills 77, mcp_instructions_delta 553, model 277, nested_memory 367, output_style 6, output_style_instructions 4, prompt_snapshot 547, queued_command 1408, read_truncation_notice 27, remote_session_change 482, session_context 273, silent_turn_reminder 1246, skill_listing 616, structured_output 30, task_reminder 2285, task_status 212, thinking_drop 7, total_tokens_reminder 40862, ultra_effort_enter 2, ultra_effort_exit 1
```

124,138 + 22 + 2 + 51,957 + 38,672 + 29,703 = 244,494: every input line is either on an event or in a counted drop
class, per type equal to the builder's table. No line is dropped silently and no dropped class has events. The 38
attachment types are the builder's 38 (13 exported, 25 counted). Record types: assistant 96,599, user 48,379, attachment
59,596, system 1,162, started 34, result 30 and the 7 bookkeeping types. (The builder counts 29,704 signature-only BLOCKS;
29,703 RECORDS hold nothing else.)

## 7. The JSON-escape boundary, exactly (reproduced in process on the production scrubber)

A FAKE 18-character value, each input canonicalised by the exporter's own `canon()` and passed to `scrub_payload`:

```
heredoc, unquoted NAME=v             -> scrubbed | mode: None
heredoc, NAME="v"                    -> LEAKS | mode: None
NAME='v' (single quotes)             -> scrubbed | mode: None
yaml api_key: "v" via heredoc        -> LEAKS | mode: strict
yaml api_key: v (unquoted)           -> scrubbed | mode: None
curl -H "X-Agent-Token: v"           -> scrubbed | mode: None
top-level input key {password: v}    -> scrubbed | mode: None
```

Only a DOUBLE-quoted value fails (JSON writes the quote as `\"`). The fourth row is the realistic one: a Bash heredoc
that writes an `api_key` into a Hermes profile names `.hermes/profiles/`, so its RESULT gets the strict pass, but its
COMMAND (scrubbed by the payload pass only, D-2) carries the value out.

## 8. Attack 1c: the pseudonym key and an env file as a hex dump (reproduced)

`h/attack1c.py`: Bash calls whose commands name `/root/.config/session-export/pseudonym.key` (text only; nothing reads the
real key) with results in `xxd`, `od -An -tx1` and `base64 -w 16` format of a FIXTURE key made by `init-key` in scratch,
and an `xxd` of a fake `.pc-bridge.env`. The export runs with that same fixture key, so its gate knows the key's four
printed forms. Pasted:

```
export rc 0; gate total 0; key-form canaries in the gate: [('pseudonym-key-HEX', '0'), ('pseudonym-key-b64', '0'), ('pseudonym-key-b64url', '0'), ('pseudonym-key-hex', '0')]
xxd-key          strict-passed result: key recoverable by joining the dump: True  | key hex 8-char pieces present 8/8 | bridge-token 8-char windows present 0
od-key           strict-passed result: key recoverable by joining the dump: True  | key hex 8-char pieces present 8/8 | bridge-token 8-char windows present 0
b64-wrapped-key  strict-passed result: key recoverable by joining the dump: False | key hex 8-char pieces present 0/8 | bridge-token 8-char windows present 0
xxd-bridge-env   strict-passed result: key recoverable by joining the dump: False | key hex 8-char pieces present 0/8 | bridge-token 8-char windows present 10
```

The strict pass takes runs of 20+ key characters and lone-token lines; a grouped hex dump has neither, and the gate looks
for four contiguous forms only. Real transcripts (`h/keydump_count.py`, pointers and counts only): 9 Bash calls name the
key path (verification commands among them, mine included); 0 of their results is shaped like a hex dump. So nothing
real has leaked this way; the path is open.

## 9. Attack 4: the resumable converter (reproduced)

`h/attack4.py`: the reader acts only on `\n` positions, so every line boundary b, b-1, b+1 and three interior points of
each line cover every behaviour class of a byte offset. For each: the prefix as a live file converted from 0, then the whole
file from the returned offset with the returned state; plus a chain that appends one line at a time, and a half-written
line at every line. Pasted (07:01:06Z to 07:03:05Z):

```
attack1 fixture        bytes   51571 lines   78 events   80 | two-part splits   466, mismatches 0 | line-by-line chain same | half-written line at every line ok
attack3 fixture        bytes    5162 lines    9 events    9 | two-part splits    52, mismatches 0 | line-by-line chain same | half-written line at every line ok
builder build_tree main bytes  435167 lines   85 events   83 | two-part splits   510, mismatches 0 | line-by-line chain same | half-written line at every line ok
builder subagent       bytes    4366 lines   10 events   10 | two-part splits    58, mismatches 0 | line-by-line chain same | half-written line at every line ok
mid-line start: refused (ValueError)
```

And literally every byte offset of the two small fixtures:

```
attack3 fixture    every byte offset 1..5161: mismatches 0
builder subagent   every byte offset 1..4365: mismatches 0
```

Events (digest of every field), the final offset and the final state counters equal the one-pass result in every split.
A half-written last line is never read; the next call reads it once.

## 10. Attack 6: the shipper against a fake bridge (reproduced)

`h/attack6.py`: a real `session_export.py` export (2 files; the big one 4 chunks); a copy of `ship_to_pc.py` in a temp tree
whose `.pc-bridge.env` names a local fake with a fake token; proxy variables removed; every run asserts the token and URL
are not printed. The fake runs each command with bash in a temp dir that stands for the PC and can drop, replay, kill the
shipper, or change a file at chosen calls. Pasted (07:04:59Z):

```
export: 2 files; the big file has 4 chunks
6a rel dotdot         refused before any call              OK  rc 2 calls 0
6a rel dot            refused before any call              OK  rc 2 calls 0
6a rel stage          refused before any call              OK  rc 2 calls 0
6a rel absolute       refused before any call              OK  rc 2 calls 0
6a rel empty-part     refused before any call              OK  rc 2 calls 0
6a rel backslash      refused before any call              OK  rc 2 calls 0
6a rel newline        refused before any call              OK  rc 2 calls 0
6a rel manifest-name  refused before any call              OK  rc 2 calls 0
6a hostile file name + remote dir: shipped, nothing ran    OK  rc 0, PWNED files 0
6b foreign chunks pre-seeded in a file's stage: resent     OK  rc 0 resent 4 of 4
6b a replayed chunk call: no wrong file placed, no manifest OK  replay fired True; run rc 5 (wrong file placed False, manifest False); rerun rc 0
6c stale manifest + a dropped chunk: run exits 5           OK  rc 5
6c ... and the stale manifest.json is still on the PC      FAIL stale manifest present with 1 of 2 files unverified
6d SIGKILL mid-run, then rerun: complete, resumes          OK  killed rc -9; kept before rerun 4; rerun sent 2 of 6 chunks
6d SIGKILL during a join, then rerun: complete             OK  rc 0
6e kept chunk changed between runs: rerun resends it       OK  first rc 5, rerun rc 0, resent [0, 3]
6e kept chunk changed before the join: refused, then rerun ok OK  run rc 5 (corrupt file placed False, manifest False), rerun rc 0
6e finished file changed after arrival: rerun re-ships it  OK  rerun rc 0, big chunks resent 4
cases 18, failing 1: 6c ... and the stale manifest.json is still on the PC
```

The hostile case names a file `x$(touch PWNED1)y'z;touch PWNED2.jsonl.xz` and a remote dir `ex$(touch PWNED3)`: every
path is quoted, nothing ran. The one FAIL is my expectation, not the shipper's contract: its docstring says to use a fresh
remote dir per export (INFO F-10). The same harness against the three shipper mutants that the builder's tests miss
(section 11) turns them red: under SM1 (the join keeps a file without its whole-file sha256 check) a chunk changed on the
PC before the join gives `run rc 0 (corrupt file placed True, manifest True)`.

## 11. Attack 7: regressions (reproduced)

- The diff to the scrubber adds lines only: `git diff --numstat db1de1c~1 db1de1c` reads `56 0 scripts/transcript_export.py`
  and `157 0 tests/test_transcript_export.py`; `SECRET_PATTERNS`, `_NAME` to `_redact_run`, `scrub`, `turns`, `export` and
  `main` are byte-identical to the parent.
- The chat export, parent CLI against PIN CLI, on 5 REAL transcripts (the output hashed and deleted; nothing printed):

  ```
  transcript 1 (7355669 bytes): rc 0/0, 1 day files, parent 66c6804ed131ed9b pin 66c6804ed131ed9b IDENTICAL
  transcript 2 (1580256 bytes): rc 0/0, 1 day files, parent 8883316bc6c1ce9a pin 8883316bc6c1ce9a IDENTICAL
  transcript 3 (845950 bytes): rc 0/0, 1 day files, parent d74a5725f8ebde79 pin d74a5725f8ebde79 IDENTICAL
  transcript 4 (3074681 bytes): rc 0/0, 3 day files, parent e11a8379781dd32c pin e11a8379781dd32c IDENTICAL
  transcript 5 (715066322 bytes): rc 0/0, 18 day files, parent 294b97ce0272b215 pin 294b97ce0272b215 IDENTICAL
  ```

- Every other importer of the module uses `scrub` only (`hiccup_scan.py`, `jev.py`, `jev_context.py`,
  `laya_ft/build_dataset.py`, `laya_ft/teacher_label.py`, `harness-ports/bin/hermes-session-export.py`, `qwen_matrix.py`,
  two test files). Their tests at the PIN:

  ```
  $ bash scripts/test_summary.sh tests/test_hiccup_scan.py tests/test_jev_context.py tests/test_jev_locate_echo.py harness-ports/tests/test_hermes_session_export.py harness-ports/tests/test_qwen_matrix.py
  pytest-summary: 132 passed in 27.30s          (set 2ef22e68630d)
  $ bash scripts/test_summary.sh "tests/test_laya_ft.py::test_version_2_record_rebuilds_byte_identically_at_the_pin"
  pytest-summary: 1 passed in 85.46s (0:01:25)
  ```

  (The builder's reported red on that test was before the harvest regenerated the DSV2 record; at the PIN it passes.)
- Red first, reproduced: the parent's `transcript_export.py` with the PIN's `tests/test_transcript_export.py` gives
  `38 failed, 72 passed in 1.04s`, every failure an `AttributeError` for the missing new functions (the builder's 31 + 7).

## 12. Mutation table: NEW mutants (evidence demand 3)

`h/mutate.py`: each mutant is one exact-anchor edit (asserted to match exactly the stated number of times) on a scratch
copy of the lane's files; the worktree is never edited. Only test FUNCTION names are printed (parametrize ids hold fake
secret-shaped strings). Pasted, 07:06:56Z to 07:10:34Z:

| Id | The edit | pytest | Red tests, or the gap |
|---|---|---|---|
| N1 | settle: one pass, no fixed point | 26 passed | SURVIVES. Real data needs it: 38 real texts change on a second pass (`h/n1n4.py`); without the loop the gate would find them and exit 3 (loud) |
| N2 | a result with no call: normal scrub, not strict | 4 failed | fixed_offsets, no_canary_survives, offsets_refuse, secret_paths |
| N3 | call_mode never strict | 5 failed | fixed_offsets, no_canary_survives, offsets_refuse, pruner_archives, secret_paths |
| N4 | `_fix` is the identity | 26 passed | SURVIVES. 0 lone surrogates in the real corpus (`h/n1n4.py`); a regression would crash an export loudly (UnicodeEncodeError) |
| N5 | `_paths` reads top-level keys only | 26 passed | SURVIVES. The fixture's secret attachments carry the path at the top level too |
| N6 | gate scans the text field only | 1 failed | gate_counts_patterns_and_canaries |
| N7 | gate skips the opaque-run rule in every field | 1 failed | gate_counts_patterns_and_canaries |
| N8 | cap: no inward move of the seam | 1 failed | the_cap_seam_forms_no_secret_shape |
| N9 | load_key: mode check removed | 1 failed | a_missing_or_loose_key_refuses |
| N10 | load_key follows a symlink | 1 failed | a_missing_or_loose_key_refuses |
| N11 | convert accepts a mid-line start | 1 failed | convert_in_parts |
| N12 | --offsets: the input sha256 not compared | 1 failed | offsets_refuse_a_changed_prefix_or_archive |
| N13 | archive_unchanged always true | 26 passed | SURVIVES; equivalent: read_archive re-checks the sha256 and the export still refuses (rc 2, "archive") |
| N14 | speaker ignores origin | 1 failed | roles_follow_the_transcript_type |
| N15 | exit code read on any result | 1 failed | outcomes_are_the_harness_fields |
| N16 | G4 identity without the tool-use id | 1 failed | a_repeated_notification_is_kept_once |
| N17 | SECRET_PATH without `.hermes/profiles/` | 4 failed | fixed_offsets, no_canary_survives, offsets_refuse, secret_paths |
| N18 | SECRET_PATH without `qwen-jev/omniroute.key` | 5 failed | convert_in_parts, fixed_offsets, no_canary_survives, offsets_refuse, secret_paths |
| N19 | attachments never dropped by path | 5 failed | edited_files, fixed_offsets, no_canary_survives, offsets_refuse, secret_paths |
| N20 | a file_change on a secret path not dropped | 5 failed | bash_file_changes, fixed_offsets, no_canary_survives, offsets_refuse, secret_paths |
| N21 | the export's gate without the key's forms | 1 failed | the_key_is_never_exported_or_printed |
| N22 | file_change and pruner_archive lose the large cap | 2 failed | pruner_archives, read_results_and_write_inputs |
| P1 | Bearer-tail payload rule removed | 5 failed | gate_counts, named_rules_take_a_long_value, no_canary_survives, payload_shapes |
| P2 | bare bridge-host payload rule removed | 9 failed | fixed_offsets, gate_counts, named_rules, no_canary_survives, offsets_refuse, payload_shapes, strict_pass_takes_every_value |
| P3 | URL-password payload rule removed | 6 failed | fixed_offsets, gate_counts, named_rules, no_canary_survives, offsets_refuse, payload_shapes |
| P4 | scrub_strict without the assignment-line rule | 6 failed | pruner_archives, secret_paths, strict_pass_is_a_fixed_point, strict_pass_takes_every_value |
| P5 | scrub_strict without the key-run rule | 2 failed | strict_pass_is_a_fixed_point, strict_pass_takes_every_value |
| P6 | scrub_strict without the lone-token-line rule | 1 failed | strict_pass_takes_every_value |
| P7 | `_keylike`: a letter is enough | 2 failed | strict_pass_keeps_plain_output, strict_pass_takes_every_value |
| P8 | the opaque rule runs with its marker before the callable | 6 failed | named_rules_take_a_long_value, opaque_values_become_stable_keyed_pseudonyms, the_opaque_callable_gets_only_what_no_named_rule_takes |
| SM1 | join keeps the file without the whole-file sha256 check | 5 passed | SURVIVES the builder's tests; attack6 red (a corrupt file placed, manifest sent, rc 0) |
| SM2 | a kept chunk counts whatever its sha256 | 5 passed | SURVIVES; attack6 red (a changed chunk is never resent: rc 5 forever) |
| SM3 | a finished file counts by presence | 5 passed | SURVIVES; attack6 red (a changed file is never re-shipped: rc 5 forever) |
| SM4 | a rel may start with the stage dir | 5 passed | SURVIVES the builder's tests AND attack6 (measured: my `stage` case renames no file, so the shipper refuses on "missing here" first) |
| SM5 | a rel may repeat in the manifest | 5 passed | SURVIVES the builder's tests and attack6 (measured; no case lists one output twice) |
| SM6 | an error reply is not a refusal | 1 failed | a_wrong_token_is_refused |
| SM7 | the remote dir may hold control characters | 5 passed | SURVIVES (no test) |

30 of 37 red on the builder's tests. The exporter's and scrubber's protections are well pinned (every secret-path,
strict, gate and key mutant is red). The survivors: defence-in-depth (N1, N4, N5); one equivalent (N13); the shipper's
three remote-verification checks (SM1-SM3), which attack6 shows the production code gets right and turns red; and three
input checks (SM4, SM5, SM7) that neither suite pins. In process, the production `safe_rel` refuses `.ship/x.xz`, `..`,
`a/../b` and a control character, and accepts `-home-user/.ship/x.xz` (a deeper `.ship` part collides with no stage dir).

## 13. Evidence audit of the builder's report

Reproduced and true: every count of run 1 (section 4, exactly); the 38 attachment types and their counts, and that every
input line maps to an event or a counted drop (section 6); two runs with the same key give byte-identical outputs
(attack 3, on my fixtures; the builder's own two real runs not re-run); the chat export byte-identical (section 11, on 5
real transcripts rather than its 77 fixtures); `scrub` untouched; the 38 new scrubber tests red first; pyflakes clean;
`no_laya_in_gates` clean (`41 files scanned, clean`); 0 separator characters in the six files; the pseudonym key in no
output in its four printed forms; the converter resumes (section 9); the shipper's resume and refusal behaviour (section 10).

Overstated or missing: section 3 of the builder's report says the gate "cannot see ... a secret in a shape it does not
know". F-1 below is a shape the scrubber DOES know (a credential assignment), hidden from it by the exporter's own JSON
encoding, so the gate's 0 is weaker than the report says. The report does not measure what the opaque-run rule takes from
ordinary text (F-2). The DSV2 red test it reports is green at the PIN (the harvest regenerated the record).

Not re-run by me (and why): the coordinator's known-values check (it reads real secret values; forbidden to this lane);
the builder's own mutants M1-M7, A1-A3, G1-G5, S1-S5 (the brief asks for NEW mutants); a ship over the real bridge
(forbidden).

## 14. Finding inventory (no severity filter)

Evidence levels: VERIFIED = reproduced by me in this session through the named command; STATIC = read from source only.

**F-1 [BLOCKER] A named credential behind a JSON-escaped quote survives the export and the leak gate.**
- Evidence: VERIFIED. Attack 1 (7 shapes leak with gate `total 0`), attack 3 (`tok44-esc`: a 44-character `PC_BRIDGE_TOKEN`
  value becomes `[opaque:<hmac>]`), section 7 (only double-quoted values fail), section 4a (145 such values of 8+ letters
  and digits in the real export; the gate saw none).
- Where: the exporter canonicalises BEFORE it scrubs: tool inputs `scripts/session_export.py:433` (`text = canon(inp)`),
  attachments `:509-513`, system records `:516`, journal records `:407`; the credential rule
  `scripts/transcript_export.py:27-68` takes an optional quote `["']?` and needs 8 value characters from `[^\s"'&,;]`, so
  `\"` defeats it; `scrub_payload` `:110-122` adds no rule for it; the gate `gate_file` `session_export.py:694-723` runs the
  same patterns on the same escaped text.
- Contract mapping: D-1/D-2 ("For a tool_call, text is the call's input as canonical JSON (scrubbed)"; "Every text passes
  the extended scrubber"); D-6 (the gate scans for "the scrubber's own secret shapes" and must find 0; the canary test
  plants "a FAKE secret in every payload shape" and asserts none survives); AMENDMENT 1 G6 ("Values the named rules catch
  (token names, ...) stay fully redacted"; "a fake token caught by a named rule is redacted, not pseudonymized").
- Canonical path: the real CLI `scripts/session_export.py export` at the PIN on production-shaped records.
- Material effect: a secret-class value (a token, password or API key assigned under a name the scrubber knows) reaches the
  training corpus that ships to the PC, raw when under 40 characters and as a keyed pseudonym when longer; the leak gate
  reads 0, so the shipper's only guard passes it. Realistic trigger: `export NAME="..."` in a Bash command; a heredoc that
  writes `api_key: "..."` into a Hermes profile (section 7, row 4: its result is strict-passed, its command is not); a
  Write or Edit of a JSON or YAML config; a hook that prints JSON. Real corpus: 145 occurrences, 42 distinct values; 25
  are committed repo fixtures; 17 are unexplained (F-14).
- Reproduction: `python3 h/attack1.py <dir>` (rows `json-*`), `python3 h/attack3.py <dir>` (row `tok44-esc`).
- Discriminator (VERIFIED): a scratch copy with ONE added payload rule, a named credential whose value follows an escaped
  quote, plus its gate name:
  `(re.compile(r"(" + _NAME + r"(?:\\[\"'])?\s*[:=]\s*\\[\"'])(?=[^\\\"'\s]{8})[^\\\"'\s]+", re.I), r"\1<redacted>")`
  in `PAYLOAD_PATTERNS` and `"escaped-credential"` in `PATTERN_NAMES`. Result: the builder's three test files
  `141 passed in 14.83s`; attack 1 `survivors 21 of 38` (every `json-*` row gone); attack 3 `tok44-esc ... pseudonymised
  False`, exported as `PC_BRIDGE_TOKEN=\"<redacted>\"`; `scrub` (the chat export) untouched. Scrubbing each string leaf
  before `canon()` is the other fix; either way the canary test needs the escaped shapes (tool input, hook, notification,
  stop-hook summary text) and the G6 escaped-token case.
- Also in this finding: a `stop_hook_summary` is scrubbed in `outcome.hook_errors` (raw) but leaks the same value in its
  canonical `text` (attack 1, `json-stophook`).

**F-2 [CONTRACT-DEFECT] The coarse opaque-run rule turns ordinary engineering text into pseudonyms.**
- Evidence: VERIFIED (section 5). 109,328 matches over the real corpus: 40.7% the repo's own test function names (1,860
  distinct), 27.3% kebab-case slugs, 4.3% repo path components; the sha256 and commit ids G6 was written for are 19.0%.
- Where: `scripts/transcript_export.py:81` (`\b[A-Za-z0-9_\-]{40,}\b`) through `scrub_payload` `:119-121`, as G6 rules.
- Contract mapping: AMENDMENT 1 G6 makes these values pseudonyms by design; the brief (attack surface 2) calls a scrub that
  eats a Jev's evidence a data defect. The rule is the contract's, so the fix is an amendment, not a repair.
- Material effect: data loss. The same test name still joins across events, but the words that say which test ran or
  failed are gone from the RWKV stream (the owner, D-086: "all the data should be usable").
- Answer to the brief's question: yes, it is the same rule as the plain `scrub`; only the marker differs.
- Amendment options for the coordinator (not decided here): in this export, exempt a run that is lowercase words joined by
  `_` or `-` (test and function names, slugs), or exempt exact names defined in the tree and tracked path components.
  Random tokens mix case and digits; both options keep the hex ids and blobs under the rule.

**F-3 [CONTRACT-DEFECT] The strict pass runs on results of commands that only SOURCE `.pc-bridge.env`.**
- Evidence: VERIFIED (section 5). 1,190 of 2,096 secret-path Bash calls only source the env file (it prints nothing);
  their 1,189 results are strict-passed. Across all strict texts the pass redacts 5,783 key runs (1,783 of them repo
  paths such as `tests/test_s0_01_check_acp_conformance`) and 3,706 assignment values.
- Where: `scripts/session_export.py:295-300` (`call_mode`: any input naming a secret path is strict), as D-2 rules.
- Contract mapping: D-2 ("A Bash command that names such a path ... its result goes through the strict pass").
- Material effect: data loss in every PC suite and lane result that ran through the bridge.
- Amendment option: exempt a call whose only secret-path use is `.`/`source`, AND whose rest neither names the sourced
  variables (`$PC_BRIDGE_TOKEN`, `$PC_BRIDGE_URL`) nor prints the environment (`env`, `printenv`, `set`, `declare -p`,
  `export -p`): a sourced variable printed by the same command is the risk the strict pass covers today.

**F-4 [FOLLOW-UP] The pseudonym key (and a bridge env file) exported through a hex dump.**
- Evidence: VERIFIED (section 8): `xxd` or `od` of the key file by a Bash call that names it is strict-passed, and the
  whole key is recoverable from the export; the gate, armed with the key's four contiguous forms, reads 0. An `xxd` of a
  bridge env file leaves 10 of the token's 25 eight-character windows in the ASCII column.
- Contract mapping: G6 (the key "never exported, never printed").
- Why not a blocker: it needs someone to dump the key; the real transcripts hold 0 such results (section 8). The
  predicate excludes hypothetical misuse by itself.
- Suggested fix (cheap, same boundary, worth folding into the F-1 repair): drop, not strict-pass, the result of ANY call
  whose input names `session-export/pseudonym.key`; optionally let the gate also look for the key's hex with whitespace and
  dump offsets removed.

**F-5 [FOLLOW-UP] Secret shapes outside the scrubber's named rules survive the payload pass (15 of attack 1's 29).**
- Evidence: VERIFIED (section 2): `short-echo`, `printenv-bare`, `split-lines` (`NAME=\` then a newline), `split-events`,
  `urlenc-pass` (`password%3D<v>`), `url-token-user` (`https://<token>@host`), `curl-u` (`-u user:pass`), `bearer-lower`
  (`authorization: bearer <v>`), `netrc` (`password <v>`), `unlisted-name` (`DB_PASS=<v>` from `printenv`),
  `secret-key-base`, `docker-auth` (base64 of `user:pass`, 38 characters), `thinking-prose`, `archive-bare` (a bare token
  in a pruner archive). A base64 blob of 40+ characters with no `+` or `/` becomes a pseudonym (`b64` row); one with them
  survives in pieces.
- Contract mapping: none frozen. The contract fixes no shape list beyond D-6's examples, and the builder's self-attack
  item 1 names the category. Cheap additions in `PAYLOAD_PATTERNS`: a case-insensitive `bearer`; `curl -u user:pass`;
  a URL userinfo with no password; `password <v>` (netrc); `NAME=\` + newline.

**F-6 [FOLLOW-UP] The builder's URL-password rule leaves the part of a password after a raw `@`.**
- Evidence: VERIFIED (attack 1 `url-pass-at`): `https://bob:<p1>@<p2>@db.example.com` keeps `<p2>`.
- Where: `scripts/transcript_export.py:103` (`[^\s/@'"<>]+@` stops at the first `@`). Fix: take the userinfo up to the LAST
  `@` before the host.

**F-7 [FOLLOW-UP] Secret-path spellings the textual denylist misses.**
- Evidence: VERIFIED (attack 1 rows `glob-keyfile`, `rel-keyfile`, `dot-keyfile-read`, `dslash-keyfile-read`,
  `symlink-read`, `quoted-glob-env`, `bg-output`; the in-process `call_mode` table: `.pc-bridge.en?`, `api.e*`,
  `QWEN-BUILDER/api-key`, `session-export/./pseudonym.key` give no protection; `$HOME/...`, `~/...`, quoted paths and
  `.env.bak` do).
- Contract mapping: D-2's denylist is a set of textual regexes and the code implements them faithfully; `bg-output` is the
  builder's own NOT-done item. `os.path.normpath` before the match fixes `./` and `//`; globs, relative paths and links
  are limits of any textual denylist.
- Material effect on the real data: small. The qwen key is 64 hex (`openssl rand -hex 32`,
  `harness-ports/bin/qwen-server.sh:164`), so a bare dump of it becomes a pseudonym, not raw text.

**F-8 [FOLLOW-UP] The shipper's tests do not pin its remote checks.**
- Evidence: VERIFIED (section 12): SM1 (the join's whole-file sha256 check), SM2 (re-hashing kept chunks), SM3 (re-hashing
  finished files), SM4, SM5 and SM7 survive `tests/test_ship_to_pc.py`. The production code is right (section 10), and
  attack 6 turns SM1-SM3 red; SM1 is the dangerous one (a corrupt file placed, the manifest sent, rc 0).
- Contract mapping: D-7's test list is met (dropped, corrupted, final sha256, wrong token); the verify brief's surface 6
  (a remote file changed after a verified chunk) is not in the suite. Fix: add the three `6e` cases as tests.

**F-9 [FOLLOW-UP] Exporter test gaps.**
- N1 (the fixed-point loop in `settle`, `session_export.py:274-282`) survives, and 38 real texts need a second pass
  (without the loop the gate would find them and exit 3, loud). N4 (`_fix`, `:162-164`) survives; 0 lone surrogates in
  the real corpus. N5 (`_paths` recursion, `:171-181`) survives; real attachments carry a top-level path. N13 is equivalent.
- Fix: one fixture text that needs a second pass, one with a lone surrogate, one attachment whose secret path is nested only.

**F-10 [INFO] A stale `manifest.json` in a reused remote dir stays while a new export is incomplete.**
- Evidence: VERIFIED (section 10, case 6c). The docstring (`ship_to_pc.py:9`) says to use a fresh dir per export, so this
  is outside the shipper's stated use. Option: refuse a remote dir whose `manifest.json` differs, or remove it first.

**F-11 [INFO] Fields copied without the scrub.** `tool`, `call_id`, `ts`, `model`, `stop_reason` and `outcome.denial_kind`
are harness-written and copied as is (`session_export.py:359-364, 476-477`); the gate reads them (the opaque-run rule
skips a one-identifier `tool` or `call_id`). The manifest is not gated; it holds paths, hashes, counts and call ids, no
transcript text. STATIC.

**F-12 [INFO] Verified claims** (the evidence audit, section 13).

**F-13 [INFO] The builder's self-attack understates the gate's blind spot** (section 13).

**F-14 [UNVERIFIED] 17 unexplained values of the F-1 class in the real export.** 17 distinct values (25 occurrences), all
in subagent (lane) transcripts, under generic names (`nfake_key`, `owner_key`, `token`, `password`, `access_key`,
`secret`), not in any tracked repo file. I did not read them (standing rule); the names suggest fixtures.
`python3 h/escaped_list.py <export dir> <worktree>` prints one pointer per value (name, length, character classes, kind,
tool, src, line) for the coordinator's check.

## 15. The blocking predicate, item by item

| Finding | 1 contract | 2 canonical path | 3 material | 4 discriminator | 5 in boundary | Result |
|---|---|---|---|---|---|---|
| F-1 | yes: D-1, D-2, D-6, G6 | yes: the real CLI at the PIN | yes: secret-class values in the shipped corpus; the gate's 0 is false for this class; a token value pseudonymised against G6 | yes: attack 1 and 3 red at the PIN, green with a one-rule candidate while the 141 builder tests stay green | yes: `transcript_export.py` `PAYLOAD_PATTERNS`, `session_export.py` | BLOCKER |
| F-2 | the rule IS the contract (G6) | yes | yes: data loss | yes: the measurement | the fix is a contract amendment | CONTRACT-DEFECT |
| F-3 | the rule IS the contract (D-2) | yes | yes: data loss | yes: the measurement | the fix is a contract amendment | CONTRACT-DEFECT |
| F-4 | yes: G6 | yes | only after a hypothetical key dump; 0 in the real data | yes | yes | FOLLOW-UP |
| F-5 | no frozen shape list | yes | yes, for those shapes | yes | yes | FOLLOW-UP |
| F-6 | no (the builder's own extra rule) | yes | partial value | yes | yes | FOLLOW-UP |
| F-7 | the contract's denylist is textual and met | yes | small (the real key is 64 hex) | yes | partly (normpath) | FOLLOW-UP |
| F-8 | D-7's test list is met | yes | none in production (the code is right) | yes: SM1-SM3 | yes | FOLLOW-UP |
| F-9 | none | yes | none (loud or absent on real data) | yes | yes | FOLLOW-UP |

## 16. Gate recommendation

**NOT-READY: F-1 meets the complete blocking predicate (reproduced through the real CLI at the PIN; the recommendation
does not depend on anything I did not reproduce; the real-corpus exposure of F-14 is UNVERIFIED and not needed for it).**

The repair is one focused change, keyed to task #252, the brief with AMENDMENTS 1 and 2, and the production digests
`scripts/session_export.py` 7bf26338e88c7bcc and `scripts/transcript_export.py` 395db6ddefe0e7fc:
1. Scrub a value behind a JSON-escaped quote: a payload rule (the candidate in F-1) or scrub each string before `canon()`.
   `scrub` stays untouched, so the chat export stays byte-identical.
2. Canary tests for the escaped shapes (a Bash command, a Write or Edit input, a hook, a notification, a stop-hook
   summary's text) and the G6 case (an escaped 44-character token is redacted, not pseudonymised).
3. Recommended in the same change (F-4, cheap): drop the result of any call that names the pseudonym key path.

F-2 and F-3 go back to the coordinator as contract questions (amendments, not repairs). Everything else is follow-up.
The exporter is otherwise solid: completeness is exact, the converter is exact at every tested offset, determinism and the
pseudonym properties hold, and the shipper survived every remote attack I made.

## 17. What I reproduced, reviewed statically, skipped, and NOT-done

- Reproduced: sections 1-12 (every pasted output is from this session, 2026-09-25T06:24Z to 07:3xZ).
- Static only: F-11; the line anchors quoted in the findings; the journal-record (`started`/`result`) path of F-1 (same
  `canon()` mechanism, no fixture of its own).
- Skipped by rule: the real bridge and any ship to it; reading any real secret or the real pseudonym key (my exports used
  keys made by `init-key` in my scratch); the coordinator's known-values check; subagents.
- Skipped as out of scope: the builder's own mutants (the brief asks for new ones); the `task_reminder` size question
  (the builder's open choice, not a verify item).
- NOT-done: whether any of the 17 F-14 values is a real secret; F-1's candidate fix was proven on a scratch copy only (it
  is not the lane's fix and is not committed); the shipper's behaviour on the real bridge (chunk size against the bridge's
  real argument limit, the listing reply size) stays untested, as the builder's own self-attack item 3 says.
- Harness (kept for reruns): `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-session-export/h/`
  (`vfx.py`, `attack1.py`, `attack1c.py`, `attack2.py`, `attack3.py`, `attack4.py`, `attack6.py`, `inspect1.py`,
  `escaped_count.py`, `escaped_count2.py`, `escaped_list.py`, `survey.py`, `keydump_count.py`, `n1n4.py`, `mutate.py`).
  `VFX_WT=<tree>` points the attack scripts at another tree (the candidate fix was run that way). The worktree was removed
  at the end (07:3xZ); to rerun, re-add it (`git -C /home/user/agent-factory worktree add --detach
  <scratch>/verify-session-export/wt db1de1c`) or set `VFX_WT`. `verify-session-export/fixrepo/` holds the candidate
  fix of F-1 on copies of the lane's files (not committed; not the lane's fix). My copy of the real export, the fixture
  trees (some held the builder's canaries), the fixture keys and the mutant copies were deleted; `attack2.out` and
  `survey.out` (counts and repo identifiers only) remain.
