# VERIFY-S1-RATE report (task #309): the stamp, the score line and the extractor against their full contract

Role: adversarial-verifier (sandbox, Opus 5.5). Contract: `tasks/briefs/system1/S1-RATE-brief.md` (CONTRACT 1-5, EVIDENCE
DEMANDS). Brief: `tasks/briefs/system1/VERIFY-S1-RATE-brief.md`. Started 2026-09-26 03:5xZ. Scratch:
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-s1rate/`.

STATUS: DONE (04:3xZ). Gate recommendation: CONTRACT-INVALID for item 4's measurement clause (F1); the rest survived. Section 3.

## 0. Premise re-measured (2026-09-26 03:5xZ)

```
4b5434f transcripts: scrubbed sandbox chat digests (2026-09-26)
49dd6f5 S1-RATE: the wiki excerpt is stamped too (task #295, D-095): wiki-context register
2a98301 S1-RATE live again (D-095): the main thread pairing proven (s1-ffb64a49 scored; 5 
cf8a186 S1-RATE landed on the owner ruling (task #295, D-095: the safeguard stop was a fal
HEAD 2dfd0f5; git diff --name-status origin..HEAD:
A	tasks/briefs/system1/VERIFY-S1-RATE-brief.md
M	todo/BUILD-TASKLIST.md
1f4912ce9389185d  scripts/hook_context.py
f599e056cc60098c  scripts/s1_scores.py
00d32032a9660f08  tests/test_s1_rate.py
df094d99240380bc  .claude/hooks/system1-context.py
1d968a9a122bb7f0  .claude/settings.json
59000b94c8df0fa0  scripts/install_session_hooks.py
fab9b615481333c8  .claude/hooks/wiki-context.py
live registration count (grep -c hook_context.py ~/.claude/settings.json): 5
.jev/s1-rate-off: cannot access '.jev/s1-rate-off': No such file or directory
.jev/injections.jsonl lines: 37
df free: 1.7G
```

Verdict on the premise: MATCHES. HEAD 2dfd0f5 is origin 4b5434f plus the brief and the ledger only (no code file differs);
all seven sha256 prefixes equal the brief's; the live registration count is 5; the off switch is absent. `injections.jsonl`
grew from 35 to 37 rows since authoring: live stamps (this session's), not a mismatch.

## 1. Finding inventory

### The inventory (written 04:3xZ)

Every observation, numbered. Evidence: VERIFIED = a command run here, its output above; UNVERIFIED = not reproduced.

**F1. CONTRACT-DEFECT: a reply over about 200 characters leaves no text record, so its score lines are invisible, and
every `missing` in the live read is that shape.** (The ground of the gate recommendation.)
- Evidence: VERIFIED (structure counted in every file; my own thread, where I wrote the lines; a controlled probe).
  Mechanism UNVERIFIED: the second block has the keys and a non-empty signature of an ordinary thinking block. So the
  record says the API returned it as thinking. Whether the model's visible text went into it, or the text was dropped
  and the model thought twice, cannot be told without reading a thinking block's content, which this lane must not do.
- Contract mapping: item 4 (pair each stamped injection with "the first assistant text after it in the same thread",
  parse "the S1-RATE lines at the top of that text", the statuses, "the compliance rate" per source); evidence demand 3;
  the brief's WHY ("a wrong pairing, a lost score ... corrupts both").
- Canonical path: the production extractor on the real transcripts.
- Material effect: at the last run, 49 `missing` + 1 `open` of 86 stamped injections; for all 50 the first reply after
  the injection has two signed thinking blocks and no text record (class U 50 of 50; a recorded text without the score:
  0). `missing` is false for my own five (I scored every injection I received) and for the builder's three (its D9),
  and unknowable from the records for the rest. It is proven for none. The per-source compliance measures how often
  the next reply stayed under about 200 characters. For each class-U injection the extractor pairs a later reply. The
  scored rows are real, but only short replies carry a recoverable score, so the sample D-096 validates the labeler
  against is selected by reply length.
- Reproduction: `python3 scripts/s1_scores.py /root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl
  --out - 2>/dev/null | python3 -c 'import sys,json; [print(r["id"], r["agent"], r["status"]) for r in map(json.loads,
  sys.stdin) if r["id"] in ("s1-67bbdfcb","s1-4108338a","s1-bd94f402")]'` prints the three rows of my thread
  `aa0dae34736dbcde3` as `missing`. The shape check:
  `cd <scratch> && python3 a6_scan.py >/dev/null && python3 a6_pair.py && python3 a6_classify.py`, which printed
  `status agree 86  disagree 0` and `totals by class: {'U': 50}` at the last run.
- Why a repair inside the extractor cannot meet the clause: the only record that may hold those lines is a thinking
  block. The extractor must never read one: the standing rule, and the class the D-095 safeguard stopped
  (`reasoning_extraction`).
- Amendment options for the coordinator: (a) in the extractor's boundary: a status for an injection whose first reply
  has no text record but two or more thinking blocks (block types only, no content read), kept out of the compliance
  rate and counted in the summary, so no row reads `missing` without evidence; (b) the request asks for a short first
  text (the score lines alone, well under 200 characters), then measure the recorded share again; (c) find the
  mechanism (the binary, or the harness's owner) before choosing; (d) a capture channel the harness records as-is.
  (a) makes the evidence honest and recovers nothing; (b) or (d) recovers the scores.

**F2. FOLLOW-UP: the extractor restates part of the score syntax.** Contract item 1 ("ONE implementation of ... the score
syntax"). VERIFIED by mutation: with the prefix changed in `hook_context.py` alone, a well-formed line in the new syntax
reads `missing` (`ATTEMPT_RX`'s own `S1-RATE` literal, `scripts/s1_scores.py:69`; the order, range and note checks at
217, 219, 221 restate `rel=`, `use=`, `[0-3]`). No effect on today's output. Fix: build those four regexes from
constants in `hook_context.py` (a `SCORE_PREFIX`, the field names, the range).

**F3. FOLLOW-UP: five mutants survive the builder's tests (test gaps; the code is right on each).** VERIFIED (attack 11):
telemetry `bytes` counted as characters (every test text is ASCII); the body's leading whitespace stripped (no test body
starts with whitespace); compliance counting `open`; the rel/use means over `scored` only; the join ignoring the
session. Contract items 1, 3 and 4. Fix: a non-ASCII hook text in `test_the_telemetry_line`, the leading-newline and
whitespace shapes of attack 1, and the summary's numbers asserted on the fixture session.

**F4. FOLLOW-UP: an unusable state directory gives a stamp with no telemetry line and no error line.** VERIFIED (attack
3: read-only for the hook's uid, a real ENOSPC on a full tmpfs, a file in the directory's place). Contract item 3 ("one
JSON line per stamp") against item 1 ("any failure while stamping hands the model the unstamped context"). The builder
reads the telemetry write as outside stamping ("A failed telemetry write loses the line, never the stamp", the
wrapper's docstring), and this is not in its DISCREPANCIES. Effect: those rows lose `tool_use_id` and `sha_ok`; the
score is kept. The brief's expectation for this case (the unstamped text and an `error` line) cannot hold: no error line
can be written where the stamp line cannot. Fix: list it as a DISCREPANCY; take `tool_use_id` from the transcript
record's `toolUseID` so the join does not depend on the log.

**F5. INFO: malformed payloads are stamped with null fields.** VERIFIED: not JSON, a JSON array or string, empty,
invalid UTF-8, a non-string session id, a 5,000-digit integer, and no session id or `tool_use_id` are all stamped with
null fields and `agent` `main`. Only a payload nested past the recursion limit falls back to the unstamped text with an
`error: RecursionError` line. This follows the contract ("the payload's tool_use_id (when it has one)"). It differs from
the brief's item-3 expectation.

**F6. FOLLOW-UP, outside this boundary (escalate to the owner of `scripts/transcript_export.py`): `scrub` passes an AWS
key id and a short-segment JWT.** VERIFIED (attack 7): fake `AKIA` + 16 characters and a fake three-segment JWT, each
segment under 40 characters, came out of a note unredacted. `sk-`, `ghp_`, Bearer, `password=` and a 40-hex token were
redacted. The extractor calls `scrub`, as the contract names it.

**F7. INFO: a markdown-bold score line gets `why` `range`, not `syntax`** (the range check sees `use=1**`). A diagnostic
label only.

**F8. INFO: an `S1-RATE:` remark in the score position reads as an attempt.** With an injection waiting, it becomes that
injection's `malformed` (`bad-id`); with none, a row of its own. The live `malformed` row is exactly this: the SYNTH1
lane's (thread `a58226189b58bf46f`, record `bbb8616c`, line 69, 03:39:23Z), 141 characters starting `S1-RATE:`, with
no id and no `rel=`/`use=`.

**F9. INFO: cost holds; it grows only with very large payloads.** VERIFIED: added p50 about 4 ms and p95 about 10 ms on
every stamping path, 1.5 ms without output. `fields()` parses the whole payload: +14 ms at 1.5 MB, +57 ms at 7.7 MB.
This session's real payloads peak at 267 KB. Optional hardening: read only the four fields, or skip the parse above a
size.

**F10. INFO: what survived the attack** (all VERIFIED above): byte identity on 340 hostile cases; the cap exact at 9,500
UTF-16 units; D1 confirmed from the binary's own exit-code table; signals, the 55 s bound and the off switch in four
shapes and on the production path; the telemetry fields, sha256 and bytes through the real registered commands; no fake
secret under `.jev/`; the tool path's `tool_use_id` and per-entry `sha` (one and two blocks); registration (`--check`, a
no-op second install, `--remove` keeping foreign hooks, settings and installer in agreement); one hook text per record
(1,175 of 1,175); 24 parallel appends whole; the live joins 86 of 86 (sha256 equal) and 43 of 43 sections; my pairing
equal to the extractor's on 86 of 86.

**F11. INFO, for the coordinator: F1's pattern reaches beyond S1-RATE.** Any reader of assistant text in these
transcripts misses the longer texts written before a tool call since 2026-09-23: the chat digests, the session exports,
SYNTH1's sample of chat history. Two-thinking messages run about 2,000 a day since then, and recorded texts over 200
characters before a tool call fell from 223-294 a day to 42-103.

**F12. INFO: the log keeps one rotated generation.** Two wrappers rotating at the same moment could overwrite
`injections.jsonl.1`. Theoretical; it would cost join fields only.

**F13. INFO: `AF_S1_RATE_STATE`, if exported into the harness's environment, moves the off switch too.** It is the
documented test seam, read once; nothing sets it live.

**F14. INFO, process: one transient directory outside scratch.** `/tmp/vs1r-ro` was needed because uid 65534 cannot
traverse the scratchpad's 0700 parent. It was removed in the same command. No request misled me; the requests' "one line
per unscored injection" covered the pairs that arrived together.

### Per-finding fields

| # | class | evidence | contract mapping | canonical path | material effect | reproduction | suggested fix |
|---|---|---|---|---|---|---|---|
| F1 | CONTRACT-DEFECT | VERIFIED; mechanism UNVERIFIED | item 4 (pairing, statuses, compliance); evidence demand 3 | yes: the production extractor, real transcripts | yes: 49 `missing` + 1 `open` unproven, 8 of them false; compliance and the scored sample length-biased | the two commands under F1 | amend item 4: options (a) to (d) under F1 |
| F2 | FOLLOW-UP | VERIFIED (mutation) | item 1 (ONE implementation) | yes, by mutation of the one place | none today; a syntax change would silently desync | `<scratch>`: the prefix mutant, attack 4 | build the four regexes from hook_context constants |
| F3 | FOLLOW-UP | VERIFIED (5 surviving mutants) | items 1, 3, 4 | yes (the test suite) | none on today's code (my harnesses show it right) | `python3 <scratch>/a11_mut.py` | the three test additions under F3 |
| F4 | FOLLOW-UP | VERIFIED | item 3 vs item 1 | yes (copies, the real wrapper code) | rows lose `tool_use_id`, `sha_ok`; scores kept | `python3 <scratch>/a3_fail.py` (+ the uid-65534 run) | a DISCREPANCY row; `tool_use_id` from the record |
| F5 | INFO | VERIFIED | item 3 ("when it has one") | yes | none | `python3 <scratch>/a3_fail.py` | none |
| F6 | FOLLOW-UP (outside) | VERIFIED | item 4 names `scrub`; met | yes | an AWS key id or short JWT in a note survives | `python3 <scratch>/a7_shapes.py` | rules for both in `transcript_export.scrub` (its owner) |
| F7 | INFO | VERIFIED | item 4 (`why` labels, D6) | yes | label only | `python3 <scratch>/a7_shapes.py` | test the syntax before the range |
| F8 | INFO | VERIFIED | item 4 (malformed, D6) | yes | a remark can become a waiting injection's `malformed` | `python3 <scratch>/a7_shapes.py`; live row `bbb8616c` | treat `S1-RATE:` with no id and no fields as prose |
| F9 | INFO | VERIFIED | evidence demand 4 | yes (copies) | none at real sizes (max 267 KB) | `python3 <scratch>/a10_cost.py 250` | optional: parse only the fields needed |
| F10 | INFO | VERIFIED | items 1, 2, 3, 5 | yes | none | attacks 1-5, 8-10 | none |
| F11 | INFO (escalation) | VERIFIED (counts) | none (beyond this increment) | n/a | other transcript readers miss long texts | the per-day table, attack 6 | a coordinator check of the digests and exports |
| F12 | INFO | reviewed statically | item 3 | no (theoretical race) | join fields only | none | rotate with a unique name, or skip |
| F13 | INFO | reviewed statically | item 1 (off switch) | no | none unless exported | none | none |
| F14 | INFO (process) | VERIFIED | none | n/a | none | n/a | none |

### Gate re-run (fresh, 2026-09-26 03:56:56Z to 03:58:04Z; set 6065cf93f091, `--basetemp` in scratch)

```
481 passed in 67.94s (0:01:07)
pytest-exit: 0
pytest-summary: 481 passed in 67.94s (0:01:07)
```

### Attack 1 and 2: byte identity, exit codes and channels (reproduced, 04:0xZ)

Harness `<scratch>/a1_bytes.py`: the PIN wrapper (`git show cf8a186^:scripts/hook_context.py`, sha256 prefix
5f2ed3707dcf89a7) and a copy of the new wrapper (1f4912ce9389185d) run the same fake hook (`<scratch>/fixture-hook.py`,
which writes a payload file's bytes) on 17 hostile shapes x 4 events x 5 modes. The oracle is written as literals: exit 0
with output, the new additionalContext == `[S1 <id> fixture-hook]` + LF + the PIN's additionalContext + LF + the request;
exit 2 with a non-blank stderr on PreToolUse or PostToolUse, the new stderr == stamp line + LF + the PIN's stderr (+ LF when
it has none) + the request + LF, and stdout and the exit code equal the PIN's; every other case byte-identical to the PIN.
Shapes: multi-byte UTF-8, no trailing newline, CRLF, a CR at the end, empty, whitespace-only, newlines only, leading and
trailing newlines, invalid UTF-8, a NUL byte, a stamp look-alike first line, U+2028/U+2029/U+0085, astral characters, ANSI
escapes, one space, a JSON-looking text. Modes: exit 0 (stdout), exit 0 with stdout and stderr, exit 2, exit 1, exit 3.

```
A1/A2 cases 340  failed 0
telemetry lines by kind: {'stamp': 130}
```

130 = 13 non-blank shapes x 4 events x 2 exit-0 modes + 13 x 2 tool events (exit 2): exactly one line per stamp, none for
the unstamped cases. On exit 0 the hook's stderr is dropped by both wrappers (the PIN's behavior, unchanged).

The D4 cap, `<scratch>/a1_cap.py` (the stamp adds 300 UTF-16 units around a body with no trailing newline):

```
  exit0 ascii  body_units  9199  stamped=True  out_units 9499
  exit0 ascii  body_units  9200  stamped=True  out_units 9500
  exit0 ascii  body_units  9201  stamped=False  out_units 9201
  exit0 astral body_units  9200  stamped=True  out_units 9500
  exit0 astral body_units  9201  stamped=False  out_units 9201
  exit2 ascii  body_units  9199  stamped=True  out_units 9500
  exit2 ascii  body_units  9200  stamped=False  out_units 9200
```

The boundary is exact at 9,500 UTF-16 units for ASCII and astral text and for the exit-2 tail newline; each skip logs
one `too-long` line.

D1, read from the running Claude Code 2.1.280 binary (`/opt/claude-code/bin/claude`, its own per-event exit-code table,
near byte offset 212,615,963): PreToolUse "Exit code 2 - show stderr to model and block tool call"; PostToolUse "Exit code
2 - show stderr to model immediately"; UserPromptSubmit "Exit code 2 - block processing, erase original prompt, and show
stderr to user only"; SessionStart "Exit code 2 - show stderr to user only". D1's reading is correct. The same binary
builds every exit-2 message as `[<command>]: <stderr or "No stderr output">` and renders `hook_blocking_error` to the
model as `<hookName> hook blocking error from command: "<command>": <blockingError>`, and `hook_additional_context` as
`<hookName> hook additional context: <content joined with LF>`.

### Attack 2 (rest) and 3: signals, the time bound, the off switch, unusable state, malformed payloads (reproduced)

Harness `<scratch>/a3_fail.py`, PIN wrapper vs a copy of the new one, output of the run at 04:06:10Z to 04:07:07Z (case
names and booleans; `telemetry` = the kinds of line written):

```
signal 9: new == PIN (rc 247, stdout, stderr) -> True | no-file
signal 15: new == PIN (rc 241, stdout, stderr) -> True | no-file
hang: PIN (rc, stdout, 'did not run', seconds, telemetry) -> True | (0, b'', True, 55.0, 'no-file')
hang: new (rc, stdout, 'did not run', seconds, telemetry) -> True | (0, b'', True, 55.1, 'no-file')
off switch as file|dangling-link|directory|empty-mode-000-file, x 3 events: new bytes == PIN bytes -> True (12 of 12), no-file
off switch at <copy root>/.jev (no env seam): new bytes == PIN bytes -> True | no-file
control: switch removed at <copy root>/.jev: stamped -> True | ['stamp']
missing state dir (created by the wrapper?) -> ('stamped', True, '0o700') | ['stamp']
a file where the state dir should be -> stamped | n/a
full tmpfs state (ENOSPC), PostToolUse out0: what the model gets -> stamped | []
full tmpfs state (ENOSPC), PreToolUse err2: what the model gets -> stamped | []
control: tmpfs with room again -> stamped | ['stamp']
payload not-json|json-array|json-string|empty|invalid-utf8|session-as-number|huge-int -> stamped | (['stamp'], [(None, None, None, 'main')])
payload no-session-no-tuid: what the model gets / fields -> stamped | (['stamp'], [(None, None, 'Bash', 'main')])
payload deep-nesting: what the model gets / fields -> plain | (['error:RecursionError'], [])
```

Read-only state for the hook's uid (`setpriv --reuid=65534`; re-run in a transient `/tmp/vs1r-ro`, removed in the same
command, because the scratchpad's parent `/tmp/claude-0` is mode 0700 and uid 65534 cannot reach it): exit 0 and exit 2
both go out STAMPED and the state directory stays empty (no stamp line, no error line). The full disk is a real ENOSPC: an
8 KB tmpfs mounted in scratch and filled, never the real disk.

What bounds the wrapper's run time: `TIMEOUT_S = 55` on the wrapped hook (unchanged from the PIN; measured 55.0 s and
55.1 s on a hook that sleeps forever), under the harness's 60 s default (the live registrations set no `timeout`). The
stamping adds no blocking call: the log opens with `O_NONBLOCK|O_NOFOLLOW` and writes only to a regular file.

### Attack 5: telemetry and secrets, through the real registered commands (reproduced; first run 04:09:06Z, written 04:1xZ)

Harness `<scratch>/a5_telemetry.py`: the command strings come from the real installer's `our_hooks()` rooted at the
mirror (so the guards, the `cd` and the default state `<mirror>/.jev` are the production shape, no `AF_*` seam), the
hooks are copies of the real ones, and fake secrets are built at run time: `sk-...` in a Bash tool input, `ghp_...` in a
prompt, `AKIA...` in two hooks' texts (search-intercept's trailing-amp QUIRK GUARD quotes the command; edit-snapshot's
pyflakes tell quotes an unused import of that name).

```
telemetry lines 5  stamp lines 5  other []
  pre-bash system1-context: id s1-5f7bf773 source system1-context exit 0 bytes 2122 failed checks []
  pre-bash search-intercept exit2: id s1-6812752f source search-intercept exit 2 bytes 1165 failed checks ['sha256(minus the exit-2 tail LF)']
  post-write edit-snapshot: id s1-05730a85 source edit-snapshot exit 0 bytes 575 failed checks []
  prompt wiki-context.py: id s1-83057979 source wiki-context exit 0 bytes 2258 failed checks []
  prompt system1-context.py: id s1-746bad75 source system1-context exit 0 bytes 2082 failed checks []
system1.jsonl records 2  tool-path records 1
  tool record tool_use_id == payload's: True; entries 1, blocks cut from the stamped text 1; every entry sha == its block's: True
the hook-text secret is in the search-intercept text the model reads: True; in the edit-snapshot text: True
secret leaks under .jev: none
```

Each line's keys are exactly {t, id, source, event, tool, tool_use_id, session, agent, exit, bytes, sha256}; the
subagent payload's `agent_id` lands as `agent`; `bytes` and `sha256` are those of the stamped text as emitted. The one
"failed check" is my alternative hypothesis, kept as a control: for exit 2 the logged sha256 covers the tail newline, so it
equals the harness's tool_result tail (which keeps the stderr's trailing newline, the builder's 16 of 16), not the text
without it. No fake secret reached any file under the mirror's `.jev/` (injections.jsonl, system1.jsonl,
system1-cache.json, system1-seen/, intercept-seen.json).

### Attack 6: the extractor on the real transcripts (reproduced; written 04:1xZ)

Three instruments, all in process and read-only, printing ids, positions, block types, lengths and booleans only (never a
text, and never a thinking block's content: thinking blocks are counted by type and key set only):
`<scratch>/a6_scan.py` (every occurrence of a stamp line in ANY non-assistant record, every assistant block by type),
`<scratch>/a6_pair.py` (my own pairing rules against the rows of a COPY of the extractor, notes dropped), and
`<scratch>/a6_classify.py` (the shape of the first reply after each non-scored injection).

**Record kinds.** Stamp lines occur in non-assistant records only as: `hook_additional_context` `attachment.content`
(at the start of the text) with the same text in `rendered`; `hook_success.stdout` (the wrapper's raw JSON, which the
model never reads; the extractor rightly skips it); one blocked call's `tool_result` (s1-eec6d769, the builder's), and
tool outputs that printed a stamp (the coordinator's smoke runs s1-61e92776 and s1-f35e7a02, neither of them in the real
telemetry; fixture ids in files read by lanes; my own harness output). No stamp sits in a record kind the extractor does not read. Every `hook_additional_context`
record in the session holds exactly one text (1,175 of 1,175), no stamp id appears in two records, no string holds two
stamps: on this data the harness neither splits one hook's text across records nor merges two into one (the binary's
list path, `content: additionalContexts`, rendered joined with LF, gets a fixture test under attack 7).

**Pairing.** My pairing and the extractor's agree on all 68 stamped injections (04:12:34Z): 29 scored, 38 missing, 1 open,
`in mine only []`, `in the extractor only []`, `status agree 68  disagree 0`. The extractor applies its own rules
correctly to the records it reads.

**Why each non-scored injection reads as it does.** For every one of the 39 (38 `missing` + the 1 `open`), the first
assistant reply after it in its thread has two signed `thinking` blocks and NO `text` block (class U: 39 of 39). Not one
has a recorded text without the score (class R: 0) or a tool-call-only reply (class N: 0); none has a compaction boundary
or a person's prompt before its first reply. By thread: SYNTH1 lane `a58226189b58bf46f` 14, HCTX1 lane
`a84e4c9e6aa89fbd0` 5 (+1 open), the builder `ab23deb88411a50c8` 3 (D9's three), mine `aa0dae34736dbcde3` 3, main 13.
The last re-run (04:34:40Z) found the same on more data: 86 stamped, `status agree 86  disagree 0`, 36 scored, 49
missing, 1 open, and `totals by class: {'U': 50}`; my thread's missing ids are now five: s1-67bbdfcb, s1-4108338a,
s1-bd94f402, s1-945b5ed2, s1-2b50fca7, each scored by me at the top of a reply over 200 characters.

The pattern, measured without reading any thinking content:

- In the five transcript files with stamps, no message holds both two thinking blocks and a text block. Recorded text
  blocks before a tool call in my own thread run 52 to 196 characters.
- A controlled probe in my own thread: my replies over 200 characters (six in a row, one written as a probe with a score
  line on top) were recorded as `[thinking, thinking, tool_use]`; the next reply, 188 characters, was recorded as
  `[thinking, text, tool_use]`.
- My three `missing` rows (s1-67bbdfcb, s1-4108338a at lines 46 and 49; s1-bd94f402 at line 269) were scored at the top of
  replies over 200 characters (I wrote those lines; message `1AuyZ4LF`, lines 51-55, and message `BGswrU2i`, lines
  273-275). A search of every non-thinking string of every record in my file finds those score lines nowhere except the
  injections' own request lines and my search command.
- Session-wide, by day: until 2026-09-21 two-thinking messages were rare and long pre-tool texts were recorded (2026-09-16
  to 09-19: 0 two-thinking messages, 223 to 294 texts over 200 characters a day); from 2026-09-23 (the Opus 5.5 routing,
  D-054) two-thinking messages run 1,868 / 2,140 / 2,019 a day and texts over 200 characters fall to 103 / 42 / 50.

The main thread's belief: its last compaction boundary is line 142600 (03:41:24Z); after it, 12 stamps: 10 scored, 2
missing (s1-004a6fcb, s1-9431a158), both class U (at 04:34:40Z: 14 stamps, 12 scored, the same 2 missing). No record
contradicts the belief that it scored every one.

The one `malformed` row: the SYNTH1 lane's (thread `a58226189b58bf46f`, record `bbb8616c`, line 69, 03:39:23Z): a
141-character line at the top of a text that starts `S1-RATE:` and holds no id and no `rel=`/`use=`, a remark in the
score position; the extractor reads it as `bad-id` and, with nothing pending in that text, makes it a row of its own.

What this means for the live read's numbers: `missing` is not evidence of a non-answer for any of the 38 rows. It is false
for my three (I wrote the lines), false by the builder's D9 statement for its three, and unknowable from the records for
the other 32. The per-source compliance (0.36 / 0.41 / 0.50) measures how often the reply after an injection stayed short
enough to be recorded as text. For each class-U injection the extractor pairs with the next RECORDED text, a later reply,
not "the first assistant text after it". The scored rows are real, but they are a length-selected subsample (only short
replies carry a recoverable score), which matters for D-096's check of the labeler against real scores.

### Attack 7: the extractor's rules against hostile shapes (reproduced; written 04:2xZ)

`<scratch>/a7_shapes.py` writes fixture transcripts shaped like the real records (the key sets a6 measured: one content
block per assistant record, the records of one reply sharing `message.id`; attachments with `type`, `hookName`,
`toolUseID`, `hookEvent`, `content` and a `rendered` frame) and runs a copy of the extractor's CLI. My expectations are
literals, written from the contract and from reading the code:

```
PASS two injections on one call, one text scores both
PASS two texts in one record's content list (binary's list path)
PASS two parallel calls, pre and post each, one text scores all four (any order)
PASS score line inside a code block at the top                      -> malformed below-text
PASS score in the SECOND text block of ONE record (not the real layout) -> missing
PASS score in the second text block of one reply, one record per block (the real layout) -> late
PASS a subagent's id scored in the main thread                      -> unknown-id in main, missing in the subagent
PASS open: the thread ends on a tool call after the injection
PASS a subagent file whose agentId differs from its file name       -> keyed on agentId
PASS class U: the first reply has two thinking blocks and no text (the live pattern) -> missing
PASS an `S1-RATE:` remark at the top while two injections wait      -> the remark becomes the first one's malformed bad-id
DIFF a bold score line (markdown)
     ('main', 's1-00000ab1', False): want ('malformed', 'syntax') got ('malformed', 'range')
PASS a CRLF score line
PASS fake secrets in notes pass through scrub
     note secret sk    : full in output False, core in output False
     note secret ghp   : full in output False, core in output False
     note secret aws   : full in output True, core in output True
     note secret bearer: full in output False, core in output False
     note secret pw    : full in output False, core in output False
     note secret jwt   : full in output True, core in output True
     note secret hex40 : full in output False, core in output False
cases 14  as my oracle expects 13
```

Live data on the thread keys: no `agentId` of a transcript spans two files (the 34 that do are the workflow
`journal.jsonl` files' `started`/`result` records, which hold no hook attachment and no assistant record); no subagent
file's `agentId` differs from its file name; the main file holds no sidechain record without an `agentId`.

### Attack 4, 8 and 9: one implementation, the request line, registration (reproduced; written 04:2xZ)

**One implementation.** The extractor imports its acceptance syntax from the wrapper (`hc.SCORE_RX`, `hc.STAMP_RX`,
`hc.ID_RX`, `hc.NOTE_MAX`, `hc.request`, `hc.SCRIPT_RX`), but restates pieces of the score syntax for its diagnostics:
`ATTEMPT_RX` carries its own `S1-RATE` literal (`scripts/s1_scores.py:69`), and the `order`, `range` and `note-too-long`
checks carry their own `rel=`, `use=` and `[0-3]` (lines 217, 219, 221). Mutation on a scratch copy: with the prefix
changed in the ONE place (`SCORE_RX` and `REQUEST` in `hook_context.py`), a well-formed line in the new syntax reads
`missing`:

```
mutant applied in the ONE place (SCORE_RX and REQUEST): 1 1
a well-formed line in the mutated syntax -> [('s1-0000beef', 'missing', None)]
```

The oracle half holds: `tests/test_s1_rate.py`, `tests/test_session_hooks.py` and `tests/test_system1_context.py` import
neither script (the only importer under `tests/` is SYNTH1's `tests/test_s1_synth.py`, which stamps fixture data with
it; SYNTH1's file, outside this increment).

**The request line.** 269 bytes, ASCII, one line:
`Begin your next text with "S1-RATE <id> rel=R use=U" (+ a note <=120 chars: why, if a 0), one line per unscored
injection. rel 0 unrelated,1 same area not this step,2 relevant to this step,3 governs it; use 0 noise/known,1 confirms,2
used it,3 changed what I did`. The scale is the contract's item 2 in shortened words, the change the contract allows
(rel: unrelated / same area not this step / relevant to this step / governs it; use: noise/known / confirms / used it /
changed what I did), and it agrees with CLAUDE.md's SYSTEM-1 SCORE LINE paragraph. "One line per unscored injection"
covers two requests arriving together: two arrived together in my thread (s1-67bbdfcb, s1-4108338a) and I wrote two
lines. No request misled me. The request cannot help with attack 6's finding: it tells the agent where to write the score,
and a reply over about 200 characters does not land as a text record.

**Registration** (the real installer, every run with `--target` in scratch):

```
== 1 --check on a copy of the live target
session hooks: present in <scratch>/a9/live-copy.json   rc=0
== 2 fresh install, then a second install, then --check
session hooks: installed 6 in <scratch>/a9/fresh.json   rc=0
session hooks: unchanged in <scratch>/a9/fresh.json     rc=0
second install: bytes unchanged
session hooks: present in <scratch>/a9/fresh.json       rc=0
== 3 hooks block of the live copy equals a fresh install's: True
== 4 --remove on the live copy plus a foreign hook in our group, a foreign group, a foreign matcher and another key
session hooks: removed ours from <scratch>/a9/mixed.json   rc=0
after --remove: our commands left 0 | foreign kept [('Notification', None, 'echo foreign-group'),
  ('PostToolUse', 'Bash', 'echo foreign-post'), ('PreToolUse', 'Grep|Bash', 'echo foreign-in-our-group')] | other key kept {'keep': True}
re-install rc=0, --check rc=0
```

`.claude/settings.json` and the installer register the same five wrapped hooks, each with the wrapper's event argument
equal to its registered event: (PostToolUse, Edit|Write|Read, edit-snapshot), (PreToolUse, Grep|Bash, search-intercept),
(PreToolUse, Write|Edit|Bash, system1-context), (UserPromptSubmit, -, system1-context), (UserPromptSubmit, -,
wiki-context).

### Attack 10: cost (reproduced; written 04:3xZ)

`<scratch>/a10_cost.py 250`: the PIN wrapper and a copy of the new one on the same hook command, 250 paired rounds per
case, the order shuffled per round (seed 309), 3 warm-up rounds not counted; run 04:24:28Z to 04:25:58Z:

```
exit0 1.4KB                        n=250  pin p50   26.6 p95   30.3  new p50   30.7 p95   39.5  paired diff p50   4.1 p95   9.8  mean   4.5 ms
exit0 9,000 chars                  n=250  pin p50   26.6 p95   34.9  new p50   30.5 p95   41.2  paired diff p50   4.1 p95  10.5  mean   4.3 ms
exit2 stderr 1.4KB                 n=250  pin p50   27.5 p95   34.3  new p50   31.6 p95   39.2  paired diff p50   4.0 p95   9.6  mean   4.2 ms
no output                          n=250  pin p50   26.0 p95   31.0  new p50   27.4 p95   32.9  paired diff p50   1.5 p95   5.5  mean   1.5 ms
real system1-context (tool path)   n=250  pin p50   59.6 p95   70.3  new p50   60.8 p95   71.9  paired diff p50   0.9 p95   9.7  mean   0.9 ms
telemetry lines written by the new wrapper: 759
```

Under 20 ms at p50 and p95 on every path (the real system1-context case measured mostly its once-per-window no-output
path: both wrappers shared one System-1 state). One more axis the builder did not measure: `fields()` parses the whole
payload, which the PIN never did, so the added cost grows with the payload (40 paired rounds each): 0.15 MB +5.4 ms p50
/ +8.2 ms p95; 1.53 MB +14.0 / +17.9 ms; 7.67 MB +57.1 / +73.9 ms. This session's Read/Write/Edit calls since 2026-09-23
(3,722; tool input plus result, approximated from the transcripts) run p50 3.9 KB, p95 31 KB, p99 50 KB, max 267 KB,
none over 1 MB: theoretical here.

Other probes (reproduced): a Bash call that injects two System-1 blocks has two entries whose `sha` both equal their
blocks' (the text holds non-ASCII `·`); 24 wrappers appending in parallel wrote 24 whole JSON lines with distinct ids; no
file under `harness-ports/`, nor `AGENTS.md` or `.hermes.md`, names the wrapper or the extractor (item 5: the adapters
unchanged). The live state join on a copy of the real `.jev/` (run just before this section was written, 04:3xZ): `injections.jsonl 86 rows (sha256 equal 86),
system1.jsonl 43 sections`; 86 telemetry ids against 86 transcript injections, none unmatched in either direction.

### Attack 11: the mutants (reproduced; written 04:3xZ)

`<scratch>/a11_mut.py`: my own driver. A mirror holds copies of the two scripts, `transcript_export.py`, the installer,
`tests/test_s1_rate.py` and `tests/test_session_hooks.py`; the targets are all of `tests/test_s1_rate.py` and the six
hook_context tests of `tests/test_session_hooks.py`. The unmutated control runs first; each mutant runs alone on a fresh
copy; each patch must match exactly once; a KILL needs a junit `<failure>` (an `<error>` never counts, AF-AP-223). Run
04:27:10Z to 04:27:42Z:

```
control: passed 21 failure 0 error 0 skipped 0
KILLED    B stamp-every-nonzero-exit: failed ['test_other_exits_pass_through_unchanged'] errors 0
KILLED    B stamp-a-prompt-block: failed ['test_other_exits_pass_through_unchanged'] errors 0
KILLED    B no-off-switch: failed ['test_the_off_switch_gives_the_pins_bytes'] errors 0
KILLED    B no-fallback: failed ['test_a_stamping_failure_hands_over_the_unstamped_context'] errors 0
KILLED    B count-code-points: failed ['test_a_text_the_stamp_would_push_over_the_harness_limit_goes_unstamped'] errors 0
KILLED    B no-scrub: failed ['test_the_extractor_pairs_every_status_and_keeps_threads_apart', 'test_the_extractor_prints_ids_and_counts_only_and_scrubs_notes'] errors 0
KILLED    B no-synthetic-skip: failed ['test_the_extractor_pairs_every_status_and_keeps_threads_apart'] errors 0
KILLED    B no-duplicate: failed ['test_the_extractor_pairs_every_status_and_keeps_threads_apart', 'test_the_extractor_prints_ids_and_counts_only_and_scrubs_notes'] errors 0
KILLED    N source-is-command-name: failed ['test_the_source_is_the_wrapped_hooks_file_stem'] errors 0
SURVIVED  N telemetry-bytes-as-chars: failed [] errors 0
SURVIVED  N body-leading-whitespace-stripped: failed [] errors 0
KILLED    N agent-default-not-main: failed ['test_the_telemetry_line'] errors 0
KILLED    N session-key-wrong: failed ['test_the_telemetry_line'] errors 0
KILLED    N prompt-event-unstamped: failed ['test_the_stamp_on_each_event[UserPromptSubmit]', 'test_the_telemetry_line'] errors 0
SURVIVED  N compliance-counts-open: failed [] errors 0
SURVIVED  N mean-rel-scored-only: failed [] errors 0
SURVIVED  N join-ignores-session: failed [] errors 0
KILLED    N sections-drop-sha: failed ['test_the_extractor_reads_the_sections_and_joins_the_state_files'] errors 0
mutants 18  killed by FAILED tests 13
```

The builder's names, with my own patches: 8 of 8 killed by FAILED tests. New mutants for clauses the builder's 29 do not
name: 5 of 10 killed. The 5 survivors are test gaps, not code defects: the code is right on each, as my own harnesses
show (the byte identity on 340 cases, leading newlines and whitespace included; the telemetry `bytes` against a text
holding a non-ASCII `·`; the live compliance arithmetic 4/11, 7/17, 3/6, 0/1 matches the summary's definition).

## 2. Reproduced vs reviewed statically vs skipped

Reproduced (commands run here, outputs above): the premise; the gate (481 passed); attacks 1 to 11. The PIN wrapper came
from `git show cf8a186^:scripts/hook_context.py` and the PIN hook from `git show cf8a186^:.claude/hooks/system1-context.py`,
both run as copies. Every hook, wrapper and extractor run used scratch copies (sha256 prefixes equal to the premise's)
and scratch state. The transcripts were read in place, read-only, printing ids, positions, block types, lengths and
booleans only.

Reviewed statically: the diffs of cf8a186, 2a98301 and 49dd6f5; the system1-context tool path (only the record's two
fields change); the harness's handling of a UserPromptSubmit exit 2, read from the binary's table and its message
builder, not exercised live.

Not reproduced (UNVERIFIED): D4's premise that the harness swaps a hook text over 10,000 characters for a preview
(AF-AP-183's measurement; I found the binary's renderers, not the swap constant), and the mechanism of F1.

Skipped, with the reason: the Codex and Hermes adapters on the PC (no bridge in this lane; a grep shows none names the
wrapper); 21 of the builder's 29 named mutants (8 reproduced plus 10 new cover the clauses); the builder's system1-context
join-key test in its red state (the property was reproduced directly: attack 5 and the two-block probe); the whole
`tests/test_vendored_manifest.py` (forbidden). Scratch peaked under 10 MB; the bulky outputs and the tmpfs are gone, and the harness scripts and the two mirrors stay (1.3 MB) so the reproduction commands can be re-run.


## 3. Gate recommendation

**CONTRACT-INVALID** (for contract item 4's measurement clause only; F1, returned as a CONTRACT-DEFECT for an explicit
amendment). This rests on two things I did not reproduce: the mechanism of F1, and whether the other agents' `missing`
rows were answered (unknowable from the records; I claim it only for my own five and, by its D9, the builder's three).

Why not NOT-READY: no repair inside the extractor can pair a score the transcript does not hold as text. The only record
that may hold it is a thinking block, which the extractor must never read. A repair can only stop calling those rows
`missing` (option (a)), and that is itself a change to the frozen status set and compliance definition, the
coordinator's to amend.

Items 1, 2, 3 and 5, the wiki-context registration of 49dd6f5, the registration and the cost survived the attack. On
their own they would be MERGE-READY-WITH-FOLLOWUPS (F2, F3, F4, F6). The stamp is safe to keep live while item 4 is
amended; the numbers the extractor prints today should not be read as compliance.

Blocking reproduction (F1): the two commands under F1 above.

