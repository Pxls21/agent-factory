# VERIFY-SESSION-EXPORT report (task #252; orchestration 0f; D-031)

Role: adversarial-verifier (sandbox, Opus 5.5). Brief: `tasks/briefs/jev-laya/VERIFY-SESSION-EXPORT-brief.md`. PIN: db1de1c
(`db1de1cb138e95d1840cbf25b2078b3d61f891e3`, on origin/claude/soundbox-kit-migration-iz1jwf). Contract:
`tasks/briefs/jev-laya/SESSION-EXPORT-brief.md` + AMENDMENT 1 (G1-G6) + AMENDMENT 2. Builder's report:
`tasks/briefs/jev-laya/SESSION-EXPORT-report.md`.

Venue: a clean detached worktree at the PIN,
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-session-export/wt` (added 2026-09-25T06:24Z).
Scratch: the same `verify-session-export/` dir. No network, no bridge, no subagents.

R1 (re-verify of the one D-031 repair, PIN ce2e1c5, 2026-09-25 12:2xZ): GATE RECOMMENDATION FOR THE REPAIR:
**MERGE-READY-WITH-FOLLOWUPS**. It rests on reading R1-F-1 as not material; see "# R1 re-verify", R1.11. The first
round's text below stands as written.

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

---

# R1 re-verify (the one D-031 repair; task #252)

Started 2026-09-25T11:12:18Z. Scope (the coordinator's message): re-run my harness through the repaired CLI; attack the
new surface (the four new rules, the F-7 path forms, and above all AMENDMENT 3's committed-run exemption); regressions.
PIN: ce2e1c5 (`ce2e1c5003f6c524d5ad98b03aa895999a95a685`, on origin; head 157ddd6 adds only a chat-digest sync). Contract:
the original brief with AMENDMENTS 1 and 2, plus AMENDMENT 3 (`tasks/briefs/jev-laya/SESSION-EXPORT-R1-brief.md`). The
repair's report: `tasks/briefs/jev-laya/SESSION-EXPORT-R1-report.md`. Venue: a clean detached worktree at ce2e1c5,
`<scratch>/verify-session-export/wt`, added 11:1xZ. Same rules as before: no network, no bridge, no ship, FAKE canaries
only, no real secret read.

R1 STATUS: DONE 2026-09-25 12:2xZ (started 11:12:18Z). GATE RECOMMENDATION FOR THE REPAIR: **MERGE-READY-WITH-FOLLOWUPS**
(R1.11). It rests on one reading: R1-F-1 is not material. The coordinator owns the gate.

TL;DR:
- **F-1 is closed.** 7 of 7 escaped shapes are gone through the real CLI, and the real export's escaped letters+digits
  class falls from 145 to 0. The key dump is dropped. The new rules work on their own shapes.
- **AMENDMENT 3 holds, with one leak path.** The exemption keeps exactly the committed runs, and the named rules still run
  first on 17 of 17 committed FAKE credentials. One path lets an uncommitted value through: in a strict result,
  `<identifier>=<committed run>` stays whole, because `_committed` never checks the name (R1-F-1). Real text has 105 such
  keeps and no secret-shaped name among them. A one-line fix is tested: 233 of 233 lane tests stay green.
- **The tests do not pin the exactness.** 8 widening mutants survive the lane's tests, and my harness catches all 8
  (R1-F-2).
- **The chat digests widen the set.** The digests under `transcripts/` add 10,156 runs. 22 strict keeps come only from
  them and stay unread (R1-F-7, UNVERIFIED).
- **The rest reproduces exactly:** the real export, `scrub`, the chat export and the importers.

- [x] Gates at ce2e1c5: 238 passed twice, set 6dde7977ceba (R1.1)
- [x] My harness through the repaired CLI: the repair report's section 4 reproduced (R1.2)
- [x] AMENDMENT 3: 40 rows; named rules first; exact membership; one leak path (R1.3, R1.8)
- [x] New shapes for the new rules and the path forms: 47 rows (R1.4)
- [x] A pre-existing hang in two rules, timed at both PINs (R1.5)
- [x] The real export and five counts over it (R1.6)
- [x] Regressions: `scrub` and the chat export byte-identical, importers green (R1.7)
- [x] 17 new mutants: 5 red, 12 survive; my harness catches the 8 that widen AMENDMENT 3 (R1.8)
- [x] Inventory, predicate, recommendation (R1.9 to R1.11); cleanup (R1.12)

## R1.0 Premise

```
$ sha256sum < <file> | cut -c1-16      (the worktree at ce2e1c5)
af9d73eab7af665b  scripts/transcript_export.py        (the repair report's section 3: af9d73eab7af665b...)
630dfe64fe28aa76  tests/test_transcript_export.py
9f56802d112465ef  scripts/session_export.py           (the repair report: 9f56802d112465ef...)
bcda8895814ee561  tests/test_session_export.py
39c88510acb21ee2  scripts/ship_to_pc.py               (unchanged since db1de1c)
37cc6c042aea1771  tests/test_ship_to_pc.py            (unchanged since db1de1c)
$ git diff --stat ce2e1c5 157ddd6
 transcripts/sandbox/chat-2026-09-25.md | 2258 +++++++++++++++++++++++++++++++-
```

## R1.1 Gates at ce2e1c5, clean worktree

```
$ bash scripts/test_summary.sh tests/test_transcript_export.py tests/test_session_export.py tests/test_ship_to_pc.py   (11:17:17Z)
238 passed in 33.21s
pytest-exit: 0
pytest-summary: 238 passed in 33.21s
$ (the same, 11:17:51Z)
238 passed in 32.30s
pytest-exit: 0
pytest-summary: 238 passed in 32.30s
$ bash scripts/pc_suite.sh set-id -- tests/test_transcript_export.py tests/test_session_export.py tests/test_ship_to_pc.py
3 files set=6dde7977ceba
```

`git status --short` in the worktree was empty after both runs.

## R1.2 My harness through the repaired CLI (reproduced; judges the repair report's section 4)

The same scripts as the first round (`<scratch>/verify-session-export/h/`), run against the worktree's CLI (the exporter's
default repo is then the worktree at ce2e1c5). One edit, like the repair lane's: attack 1's protections-off control stubs
`scrub_payload` and `scrub_strict` as `lambda s, *a, **k: s`, since `scrub_strict` now also takes `keep`. My first attack-1
run passed a RELATIVE base path, so the fixture's `cwd` was relative and the exporter (correctly: `archive_dirs` keeps
absolute paths only) ignored the pruner archive; the harness's own control flagged it (`archive-bare ...
[CONTROL: absent even when off]`). The run below uses an absolute path, as the first round did.

Attack 1 (11:19:16Z), pasted without the unchanged control rows:

```
export rc 0; gate total 0
protections-off export rc 3
json-cmd-export  json-cmd-body  json-write-cfg  json-edit-yaml  json-hook  json-notif  json-stophook   -  0   (all 7)
url-pass-at  url-token-user  curl-u  bearer-lower  unlisted-name                                          -  0
glob-keyfile  rel-keyfile  dot-keyfile-read  dslash-keyfile-read  quoted-glob-env                         -  0
survivors 12 of 38: short-echo printenv-bare split-lines split-events urlenc-pass netrc secret-key-base docker-auth thinking-prose archive-bare symlink-read bg-output
```

(The full table is in `<scratch>/verify-session-export/r1-a1.out`; every positive control is present when the protections
are off.) This is the repair report's list exactly (its section 4: the same 12 tags). All 7 escaped shapes are gone.

Attack 1c (11:19:50Z), pasted:

```
export rc 0; gate total 0; key-form canaries in the gate: [('pseudonym-key-HEX', '0'), ('pseudonym-key-b64', '0'), ('pseudonym-key-b64url', '0'), ('pseudonym-key-hex', '0')]
xxd-key          strict-passed result: key recoverable by joining the dump: False | key hex 8-char pieces present 0/8 | bridge-token 8-char windows present 0
od-key           strict-passed result: key recoverable by joining the dump: False | key hex 8-char pieces present 0/8 | bridge-token 8-char windows present 0
b64-wrapped-key  strict-passed result: key recoverable by joining the dump: False | key hex 8-char pieces present 0/8 | bridge-token 8-char windows present 0
xxd-bridge-env   strict-passed result: key recoverable by joining the dump: False | key hex 8-char pieces present 0/8 | bridge-token 8-char windows present 10
```

(The label `strict-passed` is my script's wording from the first round; the three key results are now DROPPED.) F-4's key
half is closed; its bridge-env half is unchanged, as the repair report says.

Attack 3 (11:20Z): every property holds (stable across folders and runs, keyed, HMAC equal to my computation, the key in
no output), and `tok44-esc  raw-in-export False pseudonymised False`, exported as
`{"command":"export PC_BRIDGE_TOKEN=\"<redacted>\" && bash scripts/pc.sh ls"}`. The G6 case of F-1 is closed.

The repair report's section 4 is reproduced: same counts, same survivors.

## R1.3 AMENDMENT 3 under attack (reproduced)

`h/attack_a3.py`. A scratch fixture repo (`git init` in my scratch, with its own identity and `core.hooksPath=/dev/null`;
never the project's repo) whose commit c2 tracks FAKE values in a text file, a force-added ignored file and a binary
file, and holds other FAKE values only in an earlier commit (removed at c2), a later commit, another branch, an untracked
file, a staged file and an uncommitted edit. First, the production `repo_runs(repo, c2)` is asked which values it holds:
exactly the committed ones (the precondition). Then one transcript echoes the values through the real CLI
(`export --repo <fixture> --commit <c2>`). Each row is read in its own call's events. Pasted (11:3xZ):

```
fixture repo: c2 has 26 committed runs
precondition (a value is in the production set exactly when it is committed at c2): holds
  not in the set: e-early l-later u-untracked s-staged w-worktree o-otherbranch
export rc 0; gate total 0; committed runs line: 26 at c2
  named raw PC_BRIDGE_TOKEN=                                     normal result      gone
  named escaped NAME=\"v\"                                       tool_call          gone
  named Bearer                                                   normal result      gone
  named bearer-lower                                             normal result      gone
  named basic-auth                                               normal result      gone
  named url-password                                             normal result      gone
  named url-token-user                                           normal result      gone
  named curl-user                                                tool_call          gone
  named pass-name                                                normal result      gone
  named password: (yaml)                                         strict result      gone
  named escaped JSON api_key                                     tool_call (Write)  gone
  named X-Agent-Token                                            normal result      gone
  named provider keys (ghp_ sk- AIza xoxb-)                      normal result      gone, gone, gone, gone
  named PEM block                                                normal result      gone
  named bridge link                                              normal result      gone
  named PC_BRIDGE_TOKEN= in a strict result                      strict result      gone
  named NAME="v" (raw) in a strict result                        strict result      gone
  bare committed 44-char run                                     normal result      kept
  bare committed 24-char token line                              strict result      kept
  committed value after NAME=                                    strict result      kept
  edge: committed 44-char run +1 char                            normal result      pseudo
  edge: committed 44-char run -1 char                            normal result      pseudo
  edge: committed 44-char run prefix char                        normal result      pseudo
  edge: committed 44-char run swapcase                           normal result      pseudo
  edge: committed 44-char run glued -tail                        normal result      pseudo
  edge: committed token line +1 char                             strict result      gone
  edge: committed token line -1 char                             strict result      gone
  edge: <uncommitted identifier>=<committed> as a token line     strict result      kept (EXPECTED gone)
  edge: <uncommitted identifier>=<committed> inside a line       strict result      kept (EXPECTED gone)
  source: earlier commit, removed at c2                          normal result      pseudo
  source: a later commit (c3)                                    normal result      pseudo
  source: another branch                                         normal result      pseudo
  source: untracked file                                         normal result      pseudo
  source: staged only                                            normal result      pseudo
  source: uncommitted edit of a tracked file                     normal result      pseudo
  source: ignored but force-added (tracked)                      normal result      kept
  source: inside a tracked binary file                           normal result      kept
rows 37, unexpected 2
standalone gate CLI (it rebuilds the set from the manifest's repo and commit): rc 0, total 0
```

(A first run read every row against the whole export and flagged the two `-1 char` rows; the kept committed values hold
their own shorter prefixes, so that was my harness. The table above reads each row in its own call's events.)

Answers to the coordinator's two questions:
- **Does the exemption apply only after the named rules?** Yes. 17 of 17 named shapes on COMMITTED fake values are
  redacted in normal results, strict results and tool inputs (every rule of `SECRET_PATTERNS` and `PAYLOAD_PATTERNS`,
  the new ones included). The code agrees: `scrub_payload` runs every named rule before the opaque rule and its callable
  (`scripts/transcript_export.py:138-150`), and `scrub_strict` runs `scrub_payload` before its three sub-rules
  (`:184-192`).
- **Can a secret-shaped value escape redaction because a matching run exists in a tracked file?** A value that is ITSELF
  committed at the export commit is kept (AMENDMENT 3's intent). Membership is exact: one character more or less, a
  prefix, a glued tail or another case is not exempt, and a value only in an earlier commit, a later commit, another branch,
  an untracked or staged file, or an uncommitted edit is not exempt. ONE path lets an UNCOMMITTED value through (below).

The exported bytes of the two unexpected rows (the FAKE identifier and the committed run masked):

```
toolu_vfy_a3_028 -> '<C:secret-ident>=<committed c-tok>\n'
toolu_vfy_a3_029 -> 'x <C:secret-ident>=<committed c-tok> y\n'
```

Mechanism (`scripts/transcript_export.py:174-181`): `_committed(s, keep)` accepts `s` when `s in keep`, OR when `s` is
`NAME=` followed by a committed run, with `_HEAD_NAME = [A-Za-z_][A-Za-z0-9_]*=`. The name part is never checked (neither
committed nor redacted), so in a strict result any identifier-shaped value glued by `=` to a committed run of 12+ (a token
line) or 20+ (a key run) characters is kept raw. AMENDMENT 3 exempts "a run that occurs verbatim in a file tracked by
the repo"; `X=C` does not occur there. The repair report names the branch (its section 1: "`_committed` also accepts
`NAME=<a committed value>`"); the coordinator's acceptance message names only the run-shape reading.

## R1.4 The new rules, the F-7 path forms and the R-2 key forms under new shapes (reproduced)

`h/attack_r3.py`: 47 rows through the real CLI, each read in its own call's events. `expect` is `gone` where the rule
claims the shape, `limit` where the repair report names the limit (or where the shape is outside R-3's list), `gone?`
where R-3's wording claims it and the code does not. Pasted (11:25:20Z):

```
export rc 0; gate total 0
  bearer: lowercase, no digit, outside a header                bearer-lower       limit  LEAK
  bearer: raw JSON "authorization":"bearer v"                  bearer-lower       gone   scrubbed
  bearer: Proxy-Authorization: bearer v                        bearer-lower       gone   scrubbed
  bearer: authorization:bearer<TAB>v                           bearer-lower       gone   scrubbed
  bearer: curl -H "authorization: bearer v" (tool input)       bearer-lower       gone   scrubbed
  bearer: token on the next line                               bearer-lower       gone   scrubbed
  bearer: BEARER v (caps, digit, no header)                    bearer-lower       gone   scrubbed
  curl: -U proxyuser:pass (proxy credentials)                  curl-user          limit  LEAK
  curl: --proxy-user u:pass                                    curl-user          limit  LEAK
  curl: -u on a continued line of a printed script (result)    curl-user          limit  LEAK
  curl: a -K config file read back: user = "bob:pass"          curl-user          limit  LEAK
  httpie: http -a bob:pass                                     curl-user          limit  LEAK
  curl: -u 'bob:pass' (quoted)                                 curl-user          gone   scrubbed
  curl: --user=bob:pass                                        curl-user          gone   scrubbed
  PASS name without a separator: DBPASS=v                      pass-name          gone?  LEAK
  PASS name without a separator: ROOTPASS=v                    pass-name          gone?  LEAK
  PASS name without a separator: export MYSQLPASS=v            pass-name          gone?  LEAK
  lowercase db_pass: v (yaml)                                  pass-name          limit  LEAK
  GPG_PASSPHRASE=v (a name that ends in PHRASE)                pass-name          limit  LEAK
  MYSQL_PWD=v                                                  pass-name          limit  LEAK
  DB_PASS = "v" (spaces around =)                              pass-name          gone   scrubbed
  bare PASS: v (colon)                                         pass-name          limit  LEAK
  export SMTP_PASS=v                                           pass-name          gone   scrubbed
  DB.PASS=v (dot separator)                                    pass-name          gone?  scrubbed
  url token user: letters only                                 url-token-user     limit  LEAK
  url token user: 7 characters                                 url-token-user     limit  LEAK
  url token user: git+https scheme                             url-token-user     gone   scrubbed
  url token user: inside a quoted URL in a tool input          url-token-user     gone   scrubbed
  escaped: JSON value on the next line after the colon (Write) escaped-credential limit  LEAK
  escaped: passphrase with a space, second word                escaped-credential limit  LEAK
  escaped twice: a JSON string inside a JSON string (hook stdout) escaped-credential gone   scrubbed
  F-6: https://user:a@b@host/path                              url-password       gone   scrubbed
  F-6: npm-style path with @scope after the host               url-password       gone   scrubbed
  F-7: brace expansion qwen-{builder,jev}/api-key              F-7                limit  LEAK
  F-7: a glob with one literal character: cat .*               F-7                limit  LEAK
  F-7: a glob with no literal: cat ~/.config/*/*               F-7                limit  LEAK
  F-7: a path set in an earlier call: cat $D/api-key           F-7                limit  LEAK
  F-7: ../ segments                                            F-7                gone   scrubbed
  F-7: glob api-ke?                                            F-7                gone   scrubbed
  F-7: name in a variable, same command                        F-7                gone   scrubbed
  F-7: path inside $(echo ...)                                 F-7                gone   scrubbed
  R-2: xxd ~/.config/session-export/*                          R-2                gone   DROPPED
  R-2: xxd ~/.config/*/* (no literal)                          R-2                limit  16/16 key groups left
  R-2: python open(...pseudonym.key) in -c                     R-2                gone   DROPPED
  R-2: for f in ~/.config/session-export/*                     R-2                gone   DROPPED
  R-2: find -name 'pseudo*' -exec xxd                          R-2                gone   DROPPED
  R-2: od $K (path set in an earlier call)                     R-2                limit  16/16 key groups left
```

Every `gone` row is scrubbed; every `limit` row leaks as its limit says (the digit rule of `bearer-lower` and
`url-token-user`, curl's other credential flags, the case-sensitive `PASS`, names outside the list, a value split by a
line break or a space, a path the text does not spell, a glob with fewer than 2 literal characters). One group contradicts
R-3's own words: R-3 asks for "assignments to names that end in `PASS`", and `pass-name` needs a `_` or `-` before
`PASS` (or `PASS` alone): `(?<![A-Za-z0-9])(?:[A-Za-z0-9]*[_-]PASS["']?\s*[:=]|PASS\s*=)` (`scripts/transcript_export.py`,
the `pass-name` rule). So `DBPASS=`, `ROOTPASS=` and `MYSQLPASS=` leak. The repair report describes the rule as "a name
ending in capital `PASS`" and does not name the separator requirement.

## R1.5 A hang: two payload rules are quadratic on a dotted run (pre-existing; the repair report names it)

`h/regex_time.py` times each payload rule and the whole scrubs on 100 KB adversarial texts, each case in its own process
under a 60 s limit (11:27:02Z): 11 of 12 cases take at most 0.66 s for the whole `scrub_strict`; `a.a.a...` (100 KB, no
`://`) is killed at 60 s. `h/rule_scale.py` then runs each rule alone at 5, 10 and 20 KB of `a.a.a...`, at ce2e1c5 and at
the original PIN db1de1c (11:28:36Z), pasted (rules that stay under 0.02 s are not printed):

```
ce2e1c5 payload:0  a.a.a... at 5 KB / 10 KB / 20 KB: 0.15 / 0.68 / 2.48 s
ce2e1c5 payload:4  a.a.a... at 5 KB / 10 KB / 20 KB: 0.02 / 0.06 / 0.32 s
db1de1c payload:0  a.a.a... at 5 KB / 10 KB / 20 KB: 0.15 / 0.65 / 2.49 s
db1de1c payload:3  a.a.a... at 5 KB / 10 KB / 20 KB: 0.02 / 0.07 / 0.25 s
```

`payload:0` is the bare bridge-host rule `(?<![A-Za-z0-9\-])(?:[A-Za-z0-9\-]+\.)+trycloudflare\.com`: every label start
is a legal start (the lookbehind allows a `.` before it), and from each the repeated `label.` group runs to the end of the
run and backtracks; four times the time per doubling, so about a minute at 100 KB and hours at a megabyte. The scrub runs
on a whole text before the cap. `payload:4` (`url-password`; `payload:3` at db1de1c) grows faster than linear from its
`\b`-anchored scheme, the shape the repair lane named and fixed in its new `url-token-user` rule only. Both rules were
already in db1de1c: not caused by R1. My first round missed them. The repair report's section 10 names both ("9.06 s for
`"a." * 20000`", and 0.95 s for `url-password`) and says "a pathological text would slow the export, not break it". At
the measured doubling, 1 MB of such a run takes about 1.8 hours in `payload:0` alone. The real export finishes, so no real text today is
such a run; the live tailer the JEV-FIT plan will build on `convert()` would stall on one.

## R1.6 The real export at the builder's offsets, and counts over it (reproduced; counts only)

The export ran from the worktree's CLI, with a scratch key my harness made (never the real key). The offsets came from the
first round's builder manifest: 317 sources, the same set the repair report used. Those sources predate the lane
transcript that holds the FAKE `orphan` canary, so no file needed to be excluded. Pasted from `<scratch>/r1-real.log`
(started 11:29:29Z). I condensed the 18 pattern lines and 78 canary lines: `grep` counted every one at 0.

```
$ python3 wt/scripts/session_export.py export --out <scratch>/r1-real \
      --offsets <scratchpad>/session-export-r1/builder-manifest.json --key <scratch>/r1key/cfg/pseudonym.key --jobs 4 \
      --repo <scratch>/wt --commit 6ee93223b2cb7c06c85edf6a0faaa24ccf2baed5
export 2026-09-25T11:29:29Z: 317 sources, 1178943962 bytes read, 38865748 bytes written, 589.2 s
folders {"-home-user-agent-factory": {"sources": 1, "bytes_read": 3074681}, "-home-user": {"sources": 316, "bytes_read": 1175869281}}
committed runs 296985 at 6ee93223b2cb7c06c85edf6a0faaa24ccf2baed5
events {"api_error": 72, "file_change": 2796, "harness_notice": 488, "hook": 2644, "notification": 6684, "pruner_archive": 1, "summary": 131, "text": 16267, "thinking": 4997, "tool_call": 46435, "tool_result": 46422}
capped {"hook": 2, "notification": 1753, "summary": 2, "text": 40, "tool_call": 41, "tool_result": 20}
dropped_secret_path 29 strict_results 2572 unsettled 0 seam_adjusted 2 thinking_signature_only 29704 duplicate_notifications 2 file_changes_unrecorded 364 pseudonyms 10838 pruner_archives 1 archives 1 archives_skipped 0 archives_unlinked 0 archives_unmatched 0
gate: 317 files, 126937 events, 0 unreadable lines
(18 pattern lines, each 0; 78 canary lines, each 0)
total 0
$ (the manifest) repo: commit 6ee93223b2cb..., runs 296985, runs_sha256 9780a3842b7fec17...; key id 69c5df6455a6; gate total 0, bad 0
```

The export matches the repair report's section 3 line by line: sources, bytes read, committed runs, events, capped, every
counter, and the gate. The runs digest also matches (`9780a3842b7fec17...`). Only "bytes written" differs: 38,865,748
here and 38,866,988 there. The key differs, so the pseudonym hex differs and xz compresses it to a different size. The
wall time is 589.2 s here and 564.3 s there.

The escaped class F-1 counted (`h/escaped_count.py`, 12:08:30Z). Named credentials behind an escaped quote, by bucket:

```
file_change    already-scrubbed                   1
harness_notice already-scrubbed                   18
harness_notice under-8 (below the rule's floor)   16
harness_notice variable-or-template               2
notification   already-scrubbed                   12
notification   under-8 (below the rule's floor)   78
tool_call      already-scrubbed                   333
tool_call      under-8 (below the rule's floor)   602
tool_call      variable-or-template               39
tool_result    already-scrubbed                   1
tool_result    under-8 (below the rule's floor)   3
--- totals by bucket: {'already-scrubbed': 365, "under-8 (below the rule's floor)": 699, 'variable-or-template': 41}
```

At db1de1c this count was `letters+digits` 145 (my first round, section 4a). It is now 0. The 699 under-8 values sit
below the credential rule's own 8-character floor, which `scrub` has always had.

`h/r1_measure.py` runs the production `convert()` over the same sources with R1's code and the set of 6ee9322. It wraps
`_committed` and `settle` to count first passes. Pasted (11:49Z):

```
$ python3 h/r1_measure.py <scratchpad>/session-export-r1/builder-manifest.json <scratch>/r1key/cfg/pseudonym.key <scratch>/wt 6ee93223b2cb7c06c85edf6a0faaa24ccf2baed5
committed runs at 6ee93223b2cb: 296985; held only by transcripts/ (the chat digests): 10156
  of them mixed case + digits (token-like): 303
  kept: NAME= branch (the whole run is NOT committed)                105
  kept: NAME= branch, name UPPER env-style                           30
  kept: NAME= branch, name lower snake                               69
  kept: NAME= branch, name other                                     6
  kept: NAME= branch, the name itself committed                      4
  kept: digest-only AND mixed case + digits                          22
  kept: exact committed run                                          4321
  kept: exact run only the chat digests hold                         142
  surviving PASS assignments with a separator (should be 0)          0
  NAME= branch, top upper-case env-style names: LANE_ID x5, HERMES_GIT_SHA x4, HEAD x2, CHANNEL_ID x2, HOME x2, RID x2, BRANCH x2, PWD x2
  no-separator PASS assignments whose value SURVIVES the export, by name: none
```

(The counter "no-separator PASS assignments in the input" never fired: 0 in the input.) Three readings:
- **The strict pass's keeps reproduce the repair report exactly.** 4,321 exact runs plus 105 through the NAME= branch make
  4,426. The report's section 5 gives 4,094 key runs plus 332 token lines, also 4,426. The two instruments are separate
  and use the same first-pass rule.
- **The NAME= branch (R1.3's leak) fires 105 times on real text.** Every name is an env-style name (30), a lower snake
  name (69) or another single-word name (6). None is mixed case with digits, so no real secret-shaped name was kept.
- **The chat digests widen the set.** The auto-committed chat digests under `transcripts/` hold 10,156 of the committed
  runs, and no other tracked file holds them. 303 of those are mixed case with digits. The strict pass keeps 142 values
  only because a digest holds them, and 22 of those are mixed case with digits. I did not read those values (standing rule).

Real reader calls on a low-literal glob (the F-7 floor, R1.4's `cat .*` and `~/.config/*/*` rows). `h/glob_floor_count.py`
sends every real tool input (the same sources and offsets) through R1's `call_mode()` and through a copy whose literal
floor is 0 (the only edit). It prints counts and glob WORDS only (12:15Z):

```
    reader cat on .* (hits at floor 0: .pc-bridge.env)                           1
    reader head on * (hits at floor 0: .pc-bridge.env,qwen-jev/omniroute.key,session-export/pseudonym.key) 1
    reader tail on * (hits at floor 0: .pc-bridge.env,qwen-jev/omniroute.key,session-export/pseudonym.key) 3
  mode differs with the floor at 0: (None, 'strict') -> (None, 'drop')           412
  mode differs with the floor at 0: (None, None) -> (None, 'drop')               2920
  mode differs with the floor at 0: (None, None) -> (None, 'strict')             727
  of them: a reader (cat/head/tail/xxd/od/less/more/strings/base64/source/.) on such a glob 5
  tool calls                                                                     46435
  glob words behind the difference: ** x4901, * x3739, .** x1227, .* x255, *** x137, .*? x91, .*/ x91, */ x75, scripts/hooks/* x42, *? x39, s/.* x31, ?** x26, *s* x25, b/.*/ x24, accepted/* x24
```

The floor does real work. At floor 0, 4,059 of 46,435 real calls would change mode, mostly for markdown `**` and regex
`.*`. Five real calls are readers on such a glob. `h/reader_glob_check.py` reads their results in MY scrubbed export, never
the raw transcripts, and prints counts only (12:17Z):

```
reader calls on a low-literal glob in the export: 5
  tail  result chars   3869 | markers already: <redacted> 0, bridge-link 0 | bridge env names present: False | the strict pass would add 0 <redacted> markers
  head  result chars    414 | markers already: <redacted> 1, bridge-link 0 | bridge env names present: False | the strict pass would add 0 <redacted> markers
  tail  result chars    546 | markers already: <redacted> 0, bridge-link 0 | bridge env names present: False | the strict pass would add 0 <redacted> markers
  cat   result chars    634 | markers already: <redacted> 0, bridge-link 0 | bridge env names present: False | the strict pass would add 2 <redacted> markers
      would redact: assignment  21 chars, shape path-like, words 1, uncommitted keylike 20+ runs inside 0
      would redact: assignment  21 chars, shape path-like, words 1, uncommitted keylike 20+ runs inside 0
  tail  result chars    287 | markers already: <redacted> 0, bridge-link 0 | bridge env names present: False | the strict pass would add 2 <redacted> markers
      would redact: assignment 141 chars, shape mixed case + digits, words 27, uncommitted keylike 20+ runs inside 0
      would redact: assignment 141 chars, shape mixed case + digits, words 27, uncommitted keylike 20+ runs inside 0
```

None of the five results read the bridge env file. The strict pass would add only assignment values: a one-word path of 21
characters and a 27-word line. Neither holds an uncommitted key-like run. So the glob floor let no secret-shaped value
through in the real transcripts.

## R1.7 Regressions (reproduced)

`scrub`, the chat export and every other importer (worktree at ce2e1c5, 11:49Z to 12:11Z):

```
$ git diff --numstat db1de1c~1 ce2e1c5 -- scripts/transcript_export.py
104	0	scripts/transcript_export.py
$ (python: each region of db1de1c~1 against ce2e1c5)
SECRET_PATTERNS block identical: True
_NAME .. _redact_run identical: True
def scrub( identical: True
def turns( identical: True
def export( identical: True
def main( identical: True
$ (the chat export: db1de1c~1's transcript_export.py and ce2e1c5's, on 5 real transcripts; sha256 over each output tree)
11:49:59Z
transcript 1 (7355669 bytes): rc 0/0, 1 day files, parent 66c6804ed131ed9b ce2e1c5 66c6804ed131ed9b IDENTICAL
transcript 2 (1709822 bytes): rc 0/0, 1 day files, parent 776bd5a9459b4daf ce2e1c5 776bd5a9459b4daf IDENTICAL
transcript 3 (861187 bytes): rc 0/0, 1 day files, parent 20dc29a2a6edd39f ce2e1c5 20dc29a2a6edd39f IDENTICAL
transcript 4 (3074681 bytes): rc 0/0, 3 day files, parent e11a8379781dd32c ce2e1c5 e11a8379781dd32c IDENTICAL
transcript 5 (724178443 bytes): rc 0/0, 18 day files, parent 9d1b1429502dc487 ce2e1c5 9d1b1429502dc487 IDENTICAL
11:50:10Z
$ bash scripts/test_summary.sh tests/test_hiccup_scan.py tests/test_jev_context.py tests/test_jev_locate_echo.py harness-ports/tests/test_hermes_session_export.py harness-ports/tests/test_qwen_matrix.py
pytest-exit: 0
pytest-summary: 132 passed in 28.49s
$ bash scripts/test_summary.sh "tests/test_laya_ft.py::test_version_2_record_rebuilds_byte_identically_at_the_pin"
pytest-exit: 0
pytest-summary: 1 passed in 90.17s (0:01:30)
$ bash scripts/test_summary.sh tests/test_jev_client.py tests/test_decisions_canonical.py tests/test_edit_snapshot_ap_screen.py   (12:10:30Z)
pytest-exit: 0
pytest-summary: 382 passed in 30.07s
```

R1 only adds lines to `transcript_export.py`. `scrub` and everything the chat export runs are byte-identical, and so are
the chat digests. The only users of the new names (`PAYLOAD_PATTERNS`, `scrub_payload`, `scrub_strict`, `RUN_SHAPES`,
`OPAQUE_MARK`) are the two lane files and their tests (a literal sweep of the worktree's `*.py`). The DSV2 record test
is green at ce2e1c5, so the record regenerated at harvest holds. `git status --short` in the worktree stayed empty after
every run.

## R1.8 New mutants on the repair (scratch copies only)

`h/mutate_r1.py`: 17 mutants, none of them among the builder's R1a-R4l. The builder's mutants REMOVE a piece. Most of
mine WIDEN one: they exempt or redact more than the contract says. Each mutant is one exact-anchor edit (asserted to match
once) on a scratch copy of the eight lane files. The worktree is never edited. The two lane test files then run. A mutant
marked `a3` also runs my AMENDMENT 3 attack against the mutant copy (`VFX_WT`), and the output lists the rows that differ
from the real code. A mutant marked `gate` runs `h/gate_probe.py`: a planted output whose FAKE `ghp_` token is committed.

The attack got three strict rows for these mutants: swapcase, a glued `-tail`, and `NAME=<committed> <letters-only
secret>`. Baselines on the real code (12:0xZ):

```
$ python3 h/attack_a3.py <scratch>/mr1/a3-base      (tail; the 37 earlier rows are unchanged from R1.3)
  edge: committed token line swapcase                            strict result      gone
  edge: committed token line glued -tail                         strict result      gone
  edge: NAME=<committed> <letters-only secret>                   strict result      gone
rows 40, unexpected 2
$ python3 h/gate_probe.py <scratch>/mr1/gp-base
gate probe (committed set named): rc 3, total 1, counted by: github-token 1
gate probe (control, no repo named): rc 3, total 2, counted by: github-token 1, opaque-run 1
```

The gate still counts a committed `ghp_` token under its named rule. The exemption covers `opaque-run` only, as AMENDMENT 3
says. Mutants, pasted (`<scratch>/mr1/mutants.out`, 11:5xZ to 12:04Z):

```
X1    gate: a committed match skipped for EVERY pattern, not only opaque-run   | 72 passed in 10.81s | red: NONE (the mutant survives)
      gate probe: gate probe (committed set named): rc 0, total 0, counted by: none; gate probe (control, no repo named): rc 3, total 2, counted by: github-token 1, opaque-run 1
X2a   _committed: a run INSIDE a committed run counts (truncations exempt)     | 233 passed in 12.92s | red: NONE (the mutant survives)
      a3 probe: ... rows 40, unexpected 3; ... | rows that differ from the real code: edge: committed token line -1 char: gone -> kept (EXPECTED gone)
X2b   _committed: a run HOLDING a committed run counts (glued forms exempt)    | 233 passed in 12.98s | red: NONE (the mutant survives)
      a3 probe: ... rows 40, unexpected 4; ... | rows that differ from the real code: edge: committed token line +1 char: gone -> kept (EXPECTED gone) || edge: committed token line glued -tail: gone -> kept (EXPECTED gone)
X3    _committed: case-insensitive membership                                  | 233 passed in 13.21s | red: NONE (the mutant survives)
      a3 probe: ... rows 40, unexpected 3; ... | rows that differ from the real code: edge: committed token line swapcase: gone -> kept (EXPECTED gone)
X4a   pseudonymizer: a run INSIDE a committed run stays raw                    | 233 passed in 13.39s | red: NONE (the mutant survives)
      a3 probe: ... export rc 3; gate total 1; ... rows 40, unexpected 3; standalone gate CLI ...: rc 3, total 1 | rows that differ from the real code: edge: committed 44-char run -1 char: pseudo -> kept (EXPECTED pseudo)
X4b   pseudonymizer: a run HOLDING a committed run stays raw                   | 233 passed in 13.56s | red: NONE (the mutant survives)
      a3 probe: ... export rc 3; gate total 3; ... rows 40, unexpected 5; standalone gate CLI ...: rc 3, total 3 | rows that differ from the real code: edge: committed 44-char run +1 char: pseudo -> kept (EXPECTED pseudo) || edge: committed 44-char run prefix char: pseudo -> kept (EXPECTED pseudo) || edge: committed 44-char run glued -tail: pseudo -> kept (EXPECTED pseudo)
X4c   pseudonymizer: case-insensitive membership                               | 233 passed in 13.42s | red: NONE (the mutant survives)
      a3 probe: ... export rc 3; gate total 1; ... rows 40, unexpected 3; standalone gate CLI ...: rc 3, total 1 | rows that differ from the real code: edge: committed 44-char run swapcase: pseudo -> kept (EXPECTED pseudo)
X5    repo_runs: the tracked files' WORKING-TREE copies, not the commit's blobs | 3 failed, 230 passed in 13.40s | red: test_an_offsets_rerun_reads_the_commit_its_manifest_names, test_repo_runs_refuses_a_blob_git_cannot_give, test_the_gate_reads_the_committed_runs_its_manifest_names
      a3 probe: precondition ...: FAILS for l-later s-staged w-worktree; ... committed runs line: 29 at c2; rows 40, unexpected 5; ... | rows that differ from the real code: source: a later commit (c3): pseudo -> kept (EXPECTED pseudo) || source: staged only: pseudo -> kept (EXPECTED pseudo) || source: uncommitted edit of a tracked file: pseudo -> kept (EXPECTED pseudo)
X6    assignment rule: a value HOLDING a committed run keeps the whole line    | 233 passed in 13.24s | red: NONE (the mutant survives)
      a3 probe: ... rows 40, unexpected 3; ... | rows that differ from the real code: edge: NAME=<committed> <letters-only secret>: gone -> kept (EXPECTED gone)
X8    RUN_SHAPES: the token floor 12 -> 8 (a wider committed set)              | 2 failed, 231 passed in 13.31s | red: test_committed_runs_stay_as_they_are, test_run_shapes_are_the_rules_own_shapes
      a3 probe: ... committed runs line: 32 at c2; rows 40, unexpected 2; ... | no row differs from the real code
X9    escaped-credential: the value eats the backslash of the closing escaped quote | 11 failed, 222 passed in 13.44s | red: test_a_credential_behind_an_escaped_quote_is_redacted, test_an_escaped_long_token_is_redacted_not_pseudonymized, test_escaped_credentials_are_redacted
X10   bearer-lower: no digit needed outside a header (prose 'bearer tokens')   | 233 passed in 13.37s | red: NONE (the mutant survives)
X11a  url-token-user: the 8-character floor lowered to 1                       | 233 passed in 13.35s | red: NONE (the mutant survives)
X11b  url-token-user: no digit needed                                          | 1 failed, 232 passed in 13.25s | red: test_r1_rules_keep_text_with_no_secret
X12   curl-user: the window crosses a pipe or a command separator              | 233 passed in 13.14s | red: NONE (the mutant survives)
X13   cap: the strict seam check without keep                                  | 72 passed in 11.12s | red: NONE (the mutant survives)
X18   workers never take the committed set (--jobs > 1)                        | 3 failed, 69 passed in 11.26s | red: test_committed_runs_stay_as_they_are, test_opaque_values_become_stable_keyed_pseudonyms, test_the_gate_reads_the_committed_runs_its_manifest_names
```

(`...` marks where I cut repeated probe summary text: the precondition held, and the committed-run count and the
standalone gate matched the baseline, except where printed.) Summary:

- **5 of 17 are red** on the lane's tests: X5, X8, X9, X11b and X18.
- **8 widening mutants of AMENDMENT 3 survive the lane's tests:** X1, X2a, X2b, X3, X4a, X4b, X4c and X6. My harness
  catches every one of them (the rows above). So the production code IS exact: at ce2e1c5 each of these rows reads as
  the contract says (R1.3). But no lane test pins that exactness, so a later edit that widened membership would stay green.
- **The export's own gate backs up the pseudonymizer.** Under X4a, X4b and X4c the export exits 3, because the gate's
  exemption is exact.
- **Nothing backs up the strict pass.** Under X2a, X2b, X3 and X6 the export exits 0 with gate total 0. The gate never
  checks the strict pass's shapes (R1-F-10).
- **4 survivors only over-redact:** X10, X11a, X12 and X13. None of them leaks.

`h/survivors_r1.py` checks that these 4 survivors are real behaviour changes. It sends one benign input per mutant
through the real code and each mutant, and prints output digests (12:0xZ):

```
real code:
X10  'bearer authentication' in prose                          87e16b068f81
X11a a 4-character url user with a digit                       3d77416a65c0
X12  curl, then a pipe, then date -u                           9f0499e2e5a4
X13  an over-long strict result, a committed run in its head   edc99f1a83cd
X10:   X10 row c0cccd19ddfc, the other three rows as the real code
X11a:  X11a row 9e99852ec6be, the other three rows as the real code
X12:   X12 row 7d09077cf3ae, the other three rows as the real code
X13:   X13 row "cap returned None (the text becomes the seamless marker)", the other three rows as the real code
```

(The mutant blocks are condensed. Each block printed all four rows, and the three unchanged rows equal the real code's
digests.) Each survivor changes exactly its own row. The three rule survivors on their inputs (`scrub_payload`, 12:2xZ):

```
X10   real 'the API uses bearer authentication on every call'
      mut  'the API uses bearer <redacted> on every call'
X11a  real 'clone ssh://git2@example.com/zq/zq.git'
      mut  'clone ssh://<redacted>@example.com/zq/zq.git'
X12   real 'curl -s https://example.com/x | date -u +%H:%M:%S'
      mut  'curl -s https://example.com/x | date -u +%H:<redacted>'
```

X10 survives because the lane's prose controls put only short words after `bearer` (`the bearer of bad news`, `bearer
tokens are fine here`, `tests/test_transcript_export.py:601`). The 8-character floor keeps those words, with or without
the digit rule. X13 loses the whole over-long strict result when a committed run sits in its kept head: the text becomes
the seamless marker and counts as unsettled.

Candidate fixes for the two contract deviations, each tried on a scratch copy (12:0xZ to 12:1xZ):

```
candidate fix (the NAME= branch refuses a keylike name of 12+ characters): tests: 233 passed in 13.39s
  a3 probe: precondition ... holds; export rc 0; gate total 0; committed runs line: 26 at c2; rows 40, unexpected 0; ... | rows that differ from the real code: edge: <uncommitted identifier>=<committed> as a token line: kept (EXPECTED gone) -> gone || edge: <uncommitted identifier>=<committed> inside a line: kept (EXPECTED gone) -> gone
candidate pass-name fix (an upper-case name ending in PASS, no separator, with =): tests: 1 failed, 232 passed in 12.72s
  PASS name without a separator: DBPASS=v                      pass-name          gone?  scrubbed
  PASS name without a separator: ROOTPASS=v                    pass-name          gone?  scrubbed
  PASS name without a separator: export MYSQLPASS=v            pass-name          gone?  scrubbed
  negative/edge BYPASS=enabledforall             changed: True
  negative/edge COMPASS=northnorthwest           changed: True
  negative/edge PASS: test_zq_something_long     changed: False
  negative/edge PASS=$((PASS+1))                 changed: False
  negative/edge SKIPPASS=12345678                changed: True
```

The NAME= fix is one line in `_committed`:
`return s in keep or bool(m) and s[m.end():] in keep and not (m.end() > 12 and _keylike(s[:m.end() - 1]))`.
It closes R1.3's leak, and all 233 lane tests stay green. The pass-name fix makes the lane's own negative control red:
`BYPASS=abcdefghij` must stay (`tests/test_transcript_export.py:603`). So the separator requirement is a deliberate choice
that a test pins, and R-3's words ("names that end in `PASS`") also cover `BYPASS`. The coordinator settles that wording.

## R1.9 Finding inventory, R1 round (no severity filter)

Each item: class · evidence · contract mapping · canonical path · material effect · reproduction · suggested fix.

**R1-F-1 · FOLLOW-UP (the one contract deviation in AMENDMENT 3's code; read the gate line) · the NAME= branch keeps an
uncommitted value.**
- Evidence: REPRODUCED through the real CLI (R1.3, rows `toolu_vfy_a3_028/029`; R1.8). Real text: 105 NAME= keeps and
  no token-like name among them (R1.6).
- Contract: AMENDMENT 3 exempts "a run that occurs verbatim in a file tracked by the repo". The run `<identifier>=<committed>`
  does not occur there. D-2's strict pass redacts such a run. The repair report names the branch (its section 1). The
  coordinator's acceptance message does not.
- Canonical path: yes (`export`, a strict result).
- Material effect: an uncommitted, identifier-shaped FAKE value leaves the export raw. On real text there is no instance,
  and I found no plausible source. A secret would have to be an assignment's NAME, glued by `=` to a committed run.
  Env files, key files and profiles put the secret on the right of `=`.
- Reproduction: `python3 h/attack_a3.py <abs dir>` (2 unexpected rows). The mutation that removes the branch is the
  builder's R4c (red on two lane tests). The corrected implementation is the candidate in R1.8.
- Fix: the one-line candidate in R1.8 (233/233 green, my rows gone), plus my three a3 rows as lane tests.

**R1-F-2 · FOLLOW-UP · no lane test pins the exact membership of AMENDMENT 3.**
- Evidence: 8 widening mutants survive the lane's 233 tests (X1, X2a, X2b, X3, X4a, X4b, X4c, X6). My harness catches
  each one (R1.8).
- Contract: evidence demand 5 asks for "one [mutant] per new rule, each red on a named test". The builder's removal
  mutants meet it. Widening is not demanded.
- Canonical path: the code at ce2e1c5 is exact (R1.3). The gap is in the regression tests.
- Material effect: none today. A later edit could widen membership and stay green. For the strict pass nothing at run
  time would notice (gate total 0 under X2a, X2b, X3 and X6).
- Reproduction: `python3 h/mutate_r1.py <abs dir> X1 X2a X2b X3 X4a X4b X4c X6`.
- Fix: port the a3 edge rows (±1 character, prefix, swapcase, glued tail, `NAME=<committed> <letters>`) and
  `h/gate_probe.py` into `tests/test_transcript_export.py` and `tests/test_session_export.py`.

**R1-F-3 · FOLLOW-UP · 4 over-redacting widenings survive (X10, X11a, X12, X13).**
- Evidence: REPRODUCED. Each changes its own benign input (R1.8).
- Contract: the rules' own comments ("so prose such as \"bearer tokens\" stays"; the 8-character floor; the pipe-bounded
  window; `cap` keeps committed runs through `keep`).
- Material effect: evidence loss only (over-redaction), no leak.
- Fix: add `bearer authentication`, `ssh://git2@host`, `curl ... | date -u +%H:%M:%S` to
  `test_r1_rules_keep_text_with_no_secret` (each redacted by its mutant above), and an over-long strict result with a
  committed run to the cap tests.

**R1-F-4 · FOLLOW-UP (wording question) · `pass-name` needs `_` or `-` before `PASS`.**
- Evidence: REPRODUCED (R1.4). `DBPASS=`, `ROOTPASS=` and `export MYSQLPASS=` leak. Real input: 0 such assignments (R1.6).
- Contract: R-3 says "names that end in `PASS`". The lane pins `BYPASS=abcdefghij` as NOT a secret (line 603), and the
  literal wording would redact it.
- Material effect: 0 real instances. A plausible shell-script shape.
- Fix: an explicit list of prefixes without a separator (`DB`, `ROOT`, `MYSQL`, `PG`, `SMTP`, `REDIS`, `ADMIN`, ...), or
  a ruling that the separator form is what R-3 meant. The repair report should name the requirement: its prose says "a
  name ending in capital `PASS`".

**R1-F-5 · FOLLOW-UP · the F-7 glob floor (2 literal characters) misses `cat .*` and `cat ~/.config/*/*`.**
- Evidence: REPRODUCED with FAKE key tokens (R1.4). Real text: 5 reader calls on such globs, and none holds a
  secret-shaped run (R1.6).
- Contract: R-3 lists "a glob that matches a secret path". The repair report documents the floor (its section 1), and the
  lane pins it (R3j). At floor 0, 4,059 real calls would change mode.
- Material effect: none on real text. A leak shape for a key file printed through a no-literal glob.
- Fix: in reader commands only (`cat`, `head`, `tail`, `xxd`, `od`, `less`, `strings`, `base64`, `source`), take a glob
  with 0 or 1 literal characters when it can expand to a SECRET_FILES path. Bash's `*` skips dotfiles, so `.*` is the
  dotfile form.

**R1-F-6 · FOLLOW-UP (pre-existing; the repair report names it) · `bridge-host` is quadratic and `url-password` is
super-linear on a dotted run (R1.5).**
- Evidence: REPRODUCED at ce2e1c5 and at db1de1c.
- Contract: none new. The live tailer that JEV-FIT plans needs a linear scrub.
- Material effect: for 1 MB of `a.a.a...`, about 1.8 hours in `payload:0` alone (from the measured doubling). The real
  export finishes today.
- Fix: start `bridge-host` only where no `.` precedes it, `(?<![A-Za-z0-9\-.])`, as `url-token-user` does for its scheme.
  Check that a host right after an ellipsis is still covered by the named `bridge-link` rule or by a test.

**R1-F-7 · UNVERIFIED (contract question for the coordinator) · the auto-committed chat digests widen the set.**
- Evidence: MEASURED, counts only (R1.6). 10,156 committed runs exist only in `transcripts/`. The strict pass keeps 142
  values only because a digest holds them, and 22 of those are mixed case with digits. I did not read them.
- Contract: AMENDMENT 3 rests on "the repo's hooks keep secrets out of it". The digests are machine-committed transcript
  text whose only filter is `scrub`, which is weaker than the strict pass.
- Material effect: unknown. The premise also says a committed secret is already exposed, so the export would add no new
  exposure beyond origin.
- Fix: leave `transcripts/` out of the set (a one-path filter in `repo_runs`, at a cost of the 142 keeps), or have the
  coordinator run a known-values check of the real secrets against `repo_runs(HEAD)`. A hit is an origin incident in its
  own right.

**R1-F-8 · FOLLOW-UP (disclosed) · the limits of the new rules (R1.4's `limit` rows).**
- Leaking shapes: `bearer` with no digit outside a header; curl's `-U` and `--proxy-user`; a `-u` on a continued line; a
  `-K` config file; httpie's `-a`; lowercase `db_pass`; `GPG_PASSPHRASE`; `MYSQL_PWD`; `PASS:`; a url token user of
  letters only or under 8 characters; an escaped value on the next line; the second word of a passphrase; brace
  expansion; a path set in an earlier call; R-2 with a no-literal glob or a variable path.
- Each is outside R-3's list or named in the repair report's NOT-done. Fix: the F-5 continuation.

**R1-F-9 · FOLLOW-UP (disclosed) · F-4's bridge-env half.** An `xxd` of a bridge env file still shows 10 eight-character
windows of the token (R1.2, attack 1c). R-2 covers the pseudonym key only, as the brief words it.

**R1-F-10 · INFO · what the gate cannot see.**
- The gate counts named and opaque shapes only, so a strict-pass regression is invisible to it (R1.8: X2a, X2b, X3, X6).
- Its exemption keys on the rule name `opaque-run` (the repair report's section 10; it fails loud).

**R1-F-11 · INFO · the standalone gate trusts the manifest.** It rebuilds the set from the manifest's `repo.path` and
`commit`, and does not compare `runs`/`runs_sha256` with the result. An edited manifest could widen the gate's opaque
exemption. The shipper reads the recorded gate, so this is hypothetical misuse only.

**R1-F-12 · INFO · the set's sources.** Runs from tracked BINARY blobs and from force-added ignored files are exempt (R1.3).
This fits AMENDMENT 3's words ("a file tracked by the repo"). A random 12-character run in a binary is exempt too.

**R1-F-13 · INFO · evidence audit of the repair report.**
- Reproduced exactly: section 3's real-export summary, section 4 (my harness: 12 survivors, 7 of 7 escaped shapes
  gone, key dumps dropped), and section 5's strict-pass keeps (4,426, R1.6).
- Not re-derived: section 5's opaque split (28,302 / 80,981), the builder's 36 mutants ("36 of 36 red"), and the 410
  canonical tool-call texts that no longer parse (section 10: pre-existing, R1 adds none).
- Two wording gaps: the report calls `pass-name` "a name ending in capital `PASS`" without the separator requirement
  (R1-F-4), and it says the quadratic rule "would slow the export, not break it" (R1-F-6: about 1.8 hours per megabyte).

**R1-F-14 · INFO · my own harness corrections this round.**
- A relative base path made attack 1's pruner control fire. The exporter keeps absolute `cwd` paths only, so the fault was
  mine (R1.2).
- Blob-wide detection flagged the `-1 char` rows falsely. The fixed harness reads each row in its own call's events (R1.3).

**First-round items, status at ce2e1c5:**
- F-1: closed (R1.2, R1.6: 0 letters+digits values).
- F-2 and F-3: addressed by AMENDMENT 3. The effect is measured in the repair report's section 5, and I reproduced its
  strict half.
- F-4: the key half is closed; the bridge-env half is open (R1-F-9).
- F-5: partly closed by R-3 (R1-F-8).
- F-6: closed (R1.4 F-6 rows).
- F-7: partly closed (R1-F-5, R1-F-8).
- F-8 to F-11: outside R1's boundary.

## R1.10 The blocking predicate, item by item (R1 round)

| Finding | 1 contract | 2 canonical | 3 material | 4 discriminator | 5 ownership | Blocks? |
|---|---|---|---|---|---|---|
| R1-F-1 NAME= branch | yes (AMENDMENT 3, D-2) | yes (CLI) | NO on real text: 0 of 105 keeps have a token-like name, and no plausible source | yes (a3 rows; R4c; the candidate fix) | yes | no, see the note |
| R1-F-2 exactness not pinned | no (demand 5 is met) | code exact | no (latent) | yes (8 mutants) | yes | no |
| R1-F-3 over-redacting survivors | partial (comments) | yes | evidence loss only | yes | yes | no |
| R1-F-4 no-separator PASS | wording (R-3 vs a pinned BYPASS) | yes | no (0 real) | yes | yes | no |
| R1-F-5 glob floor | partial (R-3; floor documented) | yes | no (5 real calls, no secret shape) | yes | yes | no |
| R1-F-6 quadratic rules | no (pre-existing) | yes | no (the real export finishes) | yes (timings) | outside R1's items | no |
| R1-F-7 chat digests in the set | question | measured | unknown | none yet | coordinator | no (UNVERIFIED) |
| R1-F-8, R1-F-9 limits | outside R-3's list | yes | disclosed | yes | follow-up | no |

Note on R1-F-1: it meets conditions 1, 2, 4 and 5. It fails condition 3 only as a question of real-world materiality: the
leak is real for its shape, and that shape is absent from real text and implausible in secret files. If the coordinator
counts any reproduced leak of an uncommitted value as material in itself, R1-F-1 blocks, and the fix is the one line in
R1.8. No finding qualifies as CONTRACT-DEFECT: nothing new falsifies evidence, corrupts state or loses data. The
evidence-loss items are over-redactions that the lane's own design accepts.

## R1.11 Gate recommendation for the repair

**MERGE-READY-WITH-FOLLOWUPS.** It rests on one reading: R1-F-1, a reproduced leak of a hostile shape with 0 real
instances, is not material. If the coordinator reads it as material, the recommendation is NOT-READY on R1-F-1 alone, and
the fix is one tested line. R1-F-7 is UNVERIFIED (22 values unread) and needs the coordinator's known-values check or
ruling. The coordinator owns the gate.

The repair did what it was asked:
- F-1 is closed: 7 of 7 escaped shapes are gone, and the real export's letters+digits class is 0.
- The key dump is dropped.
- R-3's rules and the F-6 and F-7 forms work on their own shapes.
- AMENDMENT 3 holds for exact membership, and the named rules run first on 17 of 17 committed shapes.
- The real export reproduces the repair report.
- `scrub` and the chat export are byte-identical, and every importer is green.

Follow-ups, in order of value:
1. The NAME= line (R1-F-1).
2. The exactness tests (R1-F-2).
3. The chat-digest question (R1-F-7).
4. The linear `bridge-host` (R1-F-6).
5. The over-redaction controls (R1-F-3).
6. The PASS wording (R1-F-4).
7. The reader-glob rule (R1-F-5).
8. The F-5 and F-7 continuations (R1-F-8, R1-F-9).

## R1.12 What I reproduced, reviewed statically, skipped, and NOT-done (R1 round)

- **Reproduced** (commands and outputs above): the gates at ce2e1c5 twice (R1.1); my harness through the repaired CLI
  (R1.2); AMENDMENT 3 in 40 rows with the production `repo_runs` as a precondition (R1.3, R1.8); 47 new-shape rows
  (R1.4); rule timings at both PINs (R1.5); the real export and five counts over it (R1.6); the regressions (R1.7);
  17 new mutants, 4 survivor probes and 2 candidate fixes (R1.8).
- **Reviewed statically:** `repo_runs` (ls-tree `-z` parsing, blob-only, refusal on a missing blob), `cmd_export`'s
  repo/commit resolution, `cmd_gate`, `_pool_map`'s initializer, and the wiring of `keep` into `settle` and `cap`
  (`scripts/session_export.py:398, 425, 430`). `Source.settled` scrubs non-strict texts only, so it needs no `keep`
  (`:609`).
- **Skipped, and why:** the builder's 36 mutants (my 17 cover the new surface), the section 5 opaque split, the shipper
  (unchanged since db1de1c; F-8 stays a follow-up), and anything on the PC (no bridge by rule).
- **NOT-done:** no ship. The real pseudonym key was never read. I read no real value: the 22 digest-only token-like keeps,
  the 4 reader-glob assignment values and the first round's 17 unexplained escaped values stay unread (counts and shapes
  only). The known-values check is the coordinator's (R1-F-7).
- **Cleanup at the end:** the worktree is removed with `git worktree remove`. Deleted: the real-data export
  (`r1-real/`), my scratch key, every fixture dir and the mutant copies. Kept: the `h/` scripts and the `.out` files,
  which hold counts, tags and digests only.
