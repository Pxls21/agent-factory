# S1-RATE report (task #295, D-092 item 3)

Lane: code-implementer (sandbox, Opus 5.5). Started 2026-09-25 23:2xZ. Brief: `tasks/briefs/system1/S1-RATE-brief.md`.
Written incrementally; the sections fill as the work lands. Commits are cited by subject (the local HEAD is ahead of origin).

## STATUS

DONE (tests green in the tree, twice; 29 of 29 named mutants killed by FAILED tests; landed live at 23:58:34Z by one `mv` per file). Verified live: 4 real stamps found in this session's transcripts, joined to the wrapper's telemetry with sha256 equal 4 of 4; 1 real score paired end to end. NOT committed (no git writes). Open item for the coordinator: 3 of my 4 live stamps read `missing` (section 7).

## 1. Premise re-measured (2026-09-25 23:2xZ)

Local HEAD is `4b3b699` ("ledger: the S1-RATE entry counted 202 injection records ..."), two commits past the PIN
(f2403c2, "skills: four held lessons baked"). `git diff --stat f2403c2 HEAD` touches only
`tasks/briefs/system1/S1-RATE-brief.md` and `todo/BUILD-TASKLIST.md`: no file in my boundary moved.

| premise line | measured at authoring | re-measured | verdict |
|---|---|---|---|
| origin head | eade28c transcripts: scrubbed ... | eade28c transcripts: scrubbed ... | match |
| `wc -l scripts/hook_context.py` | 46 | 46 | match |
| `sed -n 34,44p` | the return-0 / non-zero passthrough / additionalContext print block | byte-identical block | match |
| settings registrations through the wrapper | 4 (edit-snapshot PostToolUse, system1-context UserPromptSubmit + PreToolUse, search-intercept PreToolUse) | the same 4 | match |
| tests naming hook_context | tests/test_session_hooks.py, tests/test_system1_context.py | the same 2 | match |
| `sha=hashlib` in system1-context.py | line 846 | line 846 | match |
| measure_injections.py records | 87/79/70/68/61/61/54/3 | 87/79/70/68/61/61/54/3 | match |
| assistant texts, pending histogram | 6714; [(0,6535),(1,161),(2,14),(3,3),(4,1)] | 6715; [(0,6536),(1,161),(2,14),(3,3),(4,1)] | match (one more text: the session is live) |

Verdict: the premise holds. No CONTRACT-INVALID.

PIN gate re-run before any change (the four existing files, set=76b279850729, `--basetemp` in scratch):

```
pytest-exit: 0
pytest-summary: 465 passed in 65.46s (0:01:05)
```

## 2. The brief's question: which records hold what a hook hands the model, and byte for byte?

Measured in process over this session's transcripts (the main JSONL and 341 files under `subagents/`, 2026-09-25 23:3xZ;
counts and key sets only, never a text), and read from the running Claude Code 2.1.280 binary where the transcripts hold no
sample. Every model-visible hook record carries `rendered` (a list of one `{"content": ...}`), whose text is the frame the
model reads; hook records without `rendered` are not sent to the model.

| channel | record kind | where the text sits | model frame (`rendered`) | byte for byte? |
|---|---|---|---|---|
| additionalContext (PreToolUse, PostToolUse, UserPromptSubmit, SessionStart, SubagentStart) | `attachment.type == "hook_additional_context"` | `attachment.content`, a list of strings (1,051 of 1,051 hold one) | `<system-reminder>\n{hookName} hook additional context: {text}\n</system-reminder>` | yes: 971 of 971 PreToolUse/PostToolUse records equal the `additionalContext` of the wrapper's JSON on the paired `hook_success.stdout`; the text sits verbatim in `rendered` in 1,050 of 1,050 |
| a UserPromptSubmit or SessionStart hook's plain stdout (wiki-context.py, session-start.sh) | `attachment.type == "hook_success"` with `rendered` | `attachment.content` (and the raw `stdout`) | `<system-reminder>\n{hookName} hook success: {text}\n</system-reminder>` | stdout minus its trailing newline in 50 of 54 UserPromptSubmit records; the other 4 are over 10,000 characters and hold the harness's preview instead (AF-AP-183) |
| a PreToolUse hook's exit-2 stderr (the search intercept's answer) | a `user` record, `message.content[].type == "tool_result"`, `is_error: true` | `"{hookName} hook error: [{command}]: {stderr}"`; `toolUseResult` holds `"Error: "` + the same | the tool_result itself | the stderr keeps its trailing newline (16 of 16); no other record holds the stderr, so byte identity is checked live after the landing (section 7: the telemetry's sha256 against the body after the prefix) |
| a PostToolUse (or PostToolUseFailure) hook's exit-2 stderr | `attachment.type == "hook_blocking_error"`, `blockingError.blockingError == "[{command}]: {stderr}"` | read from the 2.1.280 binary | not sampled | 0 records in this session (no wrapped PostToolUse hook exits 2) |
| a PreToolUse/PostToolUse hook's JSON stdout | `hook_success` with no `rendered` | `stdout` (the raw JSON), `content` is "" | none: not sent | not model text; the extractor never reads it (it would count every additionalContext twice) |
| other | `hook_system_message` (3: the user-visible `systemMessage`), `system` `stop_hook_summary` (Stop hooks, not wrapped) | | | not wrapped by hook_context.py |

UserPromptSubmit payloads carry no `tool_use_id` (the harness makes a fresh one for the record), and a wrapped
UserPromptSubmit hook with JSON output leaves no `hook_success` record at all: its only trace is the
`hook_additional_context` record. Threads: every record of the main JSONL has `isSidechain: false` and no `agentId`; each
subagent file holds one `agentId` (304 of 304 `subagents/*.jsonl`, 34 of 38 workflow files; 4 hold none).
Exit 2 reaches the model only on PreToolUse and PostToolUse (on UserPromptSubmit and SessionStart the harness shows the
stderr to the person only), so the wrapper stamps an exit-2 stderr on those two events only (DISCREPANCIES D1).

## 3. What was built (the diff is against the PIN; line numbers are the working tree's)

Impact before editing: GitNexus `impact plan_tool` answered "Target 'plan_tool' not found" (risk UNKNOWN: the index
does not hold `.claude/hooks/`), so the callers were confirmed by a text search: `main` (system1-context.py), the
latency test `tests/test_system1_context.py` (`s1.plan_tool`, a best-of-three bound) and the S1-L1 verifier's replay
script under `docs/research/findings/system1-context/verify-s1l1/` (research, reads the record). `hook_context.py`
has no Python importer; it runs only as a command (settings.json, install_session_hooks.py, the two test files).

- `scripts/hook_context.py` (built in scratch, moved into place with one `mv`, section 4): the stamp section (`ID_RX`,
  `STAMP_RX`, `SCORE_RX`, `NOTE_MAX`, `REQUEST`, `new_id`, `request`, `stamp`, `source_of`): the ONE implementation,
  imported by the extractor. `fields` reads tool, tool_use_id, session and agent from the payload it already passes
  through; `log` appends one line to `<state>/injections.jsonl` (0600, O_NOFOLLOW, O_NONBLOCK, rotation at 4 MB);
  `stamped` returns the unstamped text on the off switch, on a stamped length over 9,500 UTF-16 units (logged
  `too-long`) and on any exception (its type logged). `main` stamps an exit-0 output, and an exit-2 non-empty stderr on
  PreToolUse and PostToolUse only; every other path is the PIN's. The request line is 269 bytes with its id.
- `.claude/hooks/system1-context.py` (scratch, then one `mv`): `plan_tool` puts the payload's `tool_use_id` in its
  record (null when absent) and each injected entry's `sha` (the first 16 hex digits of the sha256 of the block's bytes,
  sliced from the injection by the entry's own `bytes` count, which counts one newline per line); the docstring's
  telemetry paragraph says so. Rows, budgets, output bytes and the prompt path are untouched.
- `scripts/s1_scores.py` (new): the extractor, as the brief's item 4 describes it; the status set gains `open`
  (DISCREPANCIES D3).
- `tests/test_s1_rate.py` (new, 15 tests), `tests/test_session_hooks.py` (4 tests moved to the stamped form, an
  autouse fixture keeps the wrapper's telemetry in tmp), `tests/test_system1_context.py` (`context()` checks and cuts
  the stamp, `run()` and an autouse fixture set `AF_S1_RATE_STATE`, the burst test's own parse unstamps, and the new
  `test_the_tool_record_carries_its_join_keys`).

Pre-landing run in a scratch mirror (symlinks to the tree, real copies of the files under test, no `.git`; 23:5xZ):
478 passed, 3 failed. The 3 (READ CONTEXT needs git history; the search-intercept test's inner run of the same file)
fail identically in a PIN mirror (PIN wrapper, PIN hook, PIN tests: 3 failed, 125 passed), so they are the mirror's.

Anchors: the stamp's fallback `scripts/hook_context.py:127` (`stamped`), the block sha `.claude/hooks/system1-context.py:596`, the pairing `scripts/s1_scores.py:250` (`on_text`).
Files and line ranges (the working tree; `git diff -U0`, the new files whole):
`scripts/hook_context.py` 1-175 (rewritten: 136 lines in, 7 out); `.claude/hooks/system1-context.py` 38-41, 570-573,
596-599; `scripts/s1_scores.py` 1-448 (new); `tests/test_s1_rate.py` 1-447 (new); `tests/test_session_hooks.py` 6-8, 12,
17-18, 23-41, 58-62, 72, 75-79, 177-178; `tests/test_system1_context.py` 19-23, 54-62, 79-80, 85-95, 97-98, 105, 795,
1163-1188; this report.

## 4. Landing and the gate (evidence demand 5)

The live files were checked against the PIN's sha256 just before the landing (`sha256sum -c`: both OK), the scratch
copies compiled and passed pyflakes, and both paths sit on one filesystem (device 65024), so each `mv` is one rename:
`.claude/hooks/system1-context.py` and `scripts/hook_context.py` at 23:58:34Z (modes 644 and 755 kept). The off switch
`.jev/s1-rate-off` was never needed.

Gate, the five files of the brief, set id from `pc_suite.sh`'s formula (6065cf93f091), `--basetemp` in scratch. The last
two runs, after the final test edit (the `hook_blocking_error` fixture):

```
run 1 start 00:07:23Z
pytest-exit: 0
pytest-summary: 481 passed in 76.18s (0:01:16)
run 2 start 00:08:39Z
pytest-exit: 0
pytest-summary: 481 passed in 73.38s (0:01:13)
6065cf93f091
```

(The two runs before that edit, 23:58:44Z and 00:00:03Z: `481 passed in 73.25s` and `481 passed in 70.44s`.) The count
is the PIN's 465 plus 15 in `tests/test_s1_rate.py` plus 1 in `tests/test_system1_context.py`. pyflakes over the six
code files: rc 0. `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` prints 0 for each of `scripts/hook_context.py`,
`scripts/s1_scores.py`, `.claude/hooks/system1-context.py`, `tests/test_s1_rate.py`, `tests/test_session_hooks.py`,
`tests/test_system1_context.py` and this report. The real `.jev/injections.jsonl` held 4 lines after both gates, all
from live calls in my own thread: no test wrote there.

## 5. The wrapper's added cost (evidence demand 4)

Command: `python3 <scratch>/s1rate/timing.py 250` (the PIN wrapper and the new one on the same hook call, 250 rounds per
case, the order shuffled per round, seed 295; a realistic PreToolUse payload on stdin; the hook a `printf` of 1.4 KB, a
`true`, or an exit-2 stderr). Run 2026-09-25 23:56:58Z to 23:57:44Z:

```
output (exit 0, 1.4 KB)  n=250  pin p50   28.4 p95   37.3  new p50   32.7 p95   39.7  added (paired new-pin) p50   4.2 p95   9.8  (p50 new-p50 pin   4.2, p95 new-p95 pin   2.4) ms
no output                n=250  pin p50   27.8 p95   33.4  new p50   29.2 p95   38.2  added (paired new-pin) p50   1.5 p95   9.1  (p50 new-p50 pin   1.4, p95 new-p95 pin   4.7) ms
block (exit 2, stderr)   n=250  pin p50   28.3 p95   38.7  new p50   32.4 p95   45.2  added (paired new-pin) p50   4.0 p95  13.6  (p50 new-p50 pin   4.1, p95 new-p95 pin   6.5) ms
telemetry lines written by the new wrapper: 500
```

Verdict: under 20 ms at p50 and p95 on every path. The paired p95s carry the noise of two process starts (the PIN's own
p50-to-p95 spread is 5 to 10 ms).

## 6. Negative controls (evidence demand 2)

Harness: `<scratch>/s1rate/mutate.py` (scratch only, not committed). It applies each named mutant to a scratch MIRROR's
copy (symlinks to the tree, real copies of the files under test, no `.git`), runs the mutant's target tests with
`--junitxml`, and counts a kill only when every target's outcome is `failure`: an `error` never counts (AF-AP-223). An
unmutated control run goes first. Last run 00:07:02Z to 00:07:14Z:

```
control (unmutated mirror): 14 target tests, all passed
KILLED stamp-every-nonzero-exit, stamp-a-prompt-block        -> test_other_exits_pass_through_unchanged
KILLED stderr-unstamped, always-a-newline                    -> test_a_blocking_stderr_is_stamped_... [PreToolUse, PostToolUse]
KILLED request-without-id, fixed-id                          -> test_the_stamp_on_each_event
KILLED no-off-switch, off-switch-exists-not-lexists          -> test_the_off_switch_gives_the_pins_bytes
KILLED no-fallback                                           -> test_a_stamping_failure_hands_over_the_unstamped_context
KILLED no-size-cap, count-code-points                        -> test_a_text_the_stamp_would_push_over_the_harness_limit_...
KILLED no-telemetry, telemetry-holds-the-text, sha-of-the-bare-text -> test_the_telemetry_line (+ the join tests)
KILLED block-sha-off-by-a-line, no-tool-use-id (system1-context.py) -> test_the_tool_record_carries_its_join_keys
KILLED first-text-only, no-below-text, loose-range, no-duplicate, no-synthetic-skip, no-open, one-thread-per-file,
       post-blocks-unread, blocked-calls-unread              -> test_the_extractor_pairs_every_status_and_keeps_threads_apart
KILLED no-scrub, rows-hold-the-text                          -> test_the_extractor_prints_ids_and_counts_only_and_scrubs_notes
KILLED section-sha-without-pointer, sha-ok-always            -> test_the_extractor_reads_the_sections_and_joins_the_state_files
mutants: 29, killed by FAILED tests: 29
```

(The harness prints one line per mutant with each target's outcome; the lines are grouped above, and every outcome
printed was `failure`.)

On the PIN (the PIN wrapper and hook, no extractor, the new test files; junit outcomes per test):
`test_s1_rate`: 14 failure, 1 passed (`test_other_exits_pass_through_unchanged` passes on the PIN by design: it holds
behavior the PIN already has, and its controls are the two mutants above); `test_session_hooks`: 5 failure (the 4 tests
moved to the stamped form, and READ CONTEXT, which fails in any mirror for want of git history), 19 passed;
`test_system1_context`: 83 failure (`context()` now requires the stamp), 58 passed (no injection through the wrapper),
the new join-key test among the failures. Errors: 0.

Tests only green, never seen red: none of the new ones. The hand count in one oracle was wrong on first run (21
injections where the fixture holds 14); the literal was recounted from the fixture and fixed, the code untouched.

## 7. The live read (evidence demand 3)

The extractor over this session's real transcripts (the main JSONL and every `subagents/` file), in process, summary only.

Before the landing (23:4xZ, the scratch copy against the tree's transcripts): 1,164 texts a hook handed the model, none
stamped: `hook_additional_context` 1,071, `hook_success` 77, `tool_result` 16, `hook_blocking_error` 0. By source (from
the stamp, else the hook command of the record or of its paired `hook_success`): edit-snapshot 767, system1-context 168,
wiki-context 54, session-start 23, search-intercept 16, graft-first-nag 1, settings 2, unknown 133 (SessionStart and
UserPromptSubmit texts whose hook left no command in any record).

After the landing (00:10:00Z):

```
  hook_additional_context  injections   1077  stamped      3
  hook_success             injections     77  stamped      0
  hook_blocking_error      injections      0  stamped      0
  tool_result              injections     17  stamped      1
  edit-snapshot          injections    770  stamped     2  scored 1  late 0  malformed 0  missing 1  open 0  compliance 0.50  rel 1.00  use 0.00
  search-intercept       injections     17  stamped     1  scored 0  late 0  malformed 0  missing 1  open 0  compliance 0.00  rel -  use -
  system1-context        injections    171  stamped     1  scored 0  late 0  malformed 0  missing 1  open 0  compliance 0.00  rel -  use -
score rows of their own: unknown-id 0  duplicate 0  malformed 0
state join: injections.jsonl 4 rows (sha256 equal 4), system1.jsonl 1 sections
```

All 4 stamps are my own calls, which I triggered on purpose: a Read (PostToolUse, edit-snapshot, s1-9bc9eea1), a
semantic Grep the search intercept blocked (the stamped stderr inside the tool_result, s1-eec6d769), a `pgrep` Bash call
(PreToolUse, system1-context, s1-d5aee01b), and a Write (PostToolUse, edit-snapshot, s1-65769182). What this proves:
- Byte for byte: the sha256 the wrapper logged equals the sha256 of the text the extractor found in the transcript, for
  all 4 records, including the blocked call's stderr inside its tool_result (the brief's open question, answered live).
- The section join: the system1 block's sha computed from the transcript text matched the tool path's new `sha` field
  in the real `.jev/system1.jsonl` (1 section).
- End to end, once: s1-65769182 is `scored` (rel 1, use 0, a note): my real score line at the top of my next text,
  found and paired.
- NOT proven: the other 3 read `missing`. I began each following text with their S1-RATE lines, but the transcript
  holds no text record carrying those lines, so the extractor finds none (DISCREPANCIES D9). Compliance measured from
  transcripts is therefore a floor.

## NOT-done

1. `wiki-context.py` is not stamped: it is registered without the wrapper (a settings change) and it also feeds the PC
   Hermes lanes (brief item 5). For the owner, through the coordinator.
2. The Codex and Hermes adapters under `harness-ports/` stamp nothing (brief item 5: unchanged by design).
3. The vendored manifest (it covers `.claude/`, and `.claude/hooks/system1-context.py` changed) is not regenerated; the
   standing rule for CLAUDE.md is not written. Both are the coordinator's at landing.
4. No commit, no push, no ledger, task DB or wiki update (no git writes in this lane).
5. The live pairing of a score with its stamp holds for 1 of 4 live stamps (section 7, D9). Not investigated further.
6. `hook_blocking_error` (a PostToolUse exit 2) is read and tested on a fixture whose shape comes from the 2.1.280
   binary; this session has no live sample (no wrapped PostToolUse hook exits 2).
7. No `/bug-echo`: this increment found no code defect in the existing tree; the one falsified comment is listed under
   ADJACENT DEFECTS.

## DISCREPANCIES

- D1. The brief: stamp a wrapped hook's exit-2 stderr. Done on PreToolUse and PostToolUse only. On UserPromptSubmit and
  SessionStart the harness shows an exit-2 stderr to the person only (Claude Code's exit-code table), so a stamp there
  would ask the person to score. No wrapped hook exits 2 on those events today. Held by
  `test_other_exits_pass_through_unchanged` and the `stamp-a-prompt-block` mutant.
- D2. The request line is 269 bytes with its id, not about 200: the whole scale is in it. The words are shortened, the
  scale and the syntax are the brief's: `Begin your next text with "S1-RATE <id> rel=R use=U" (+ a note <=120 chars: why,
  if a 0), one line per unscored injection. rel 0 unrelated,1 same area not this step,2 relevant to this step,3 governs
  it; use 0 noise/known,1 confirms,2 used it,3 changed what I did`.
- D3. The extractor's status set gains `open`: no assistant text after the injection in its thread yet (a live thread,
  or a subagent that ended on a tool call). It stays out of the compliance rate, which counting it as `missing` would
  understate.
- D4. A stamped text over 9,500 UTF-16 units goes out unstamped (logged `too-long`): the harness swaps a hook text over
  10,000 characters for a 2 KB preview of its head (AF-AP-183), which would drop the hook's own text. Not in the brief;
  it follows "never lose the context". The largest wrapped hook text measured in this session is about 4,500 characters.
- D5. `injections.jsonl` also carries `exit` (0 or 2: the channel of the stamp) on each stamp line, and two kinds of
  line with no `id`: `{"event", "source", "skipped": "too-long"}` and `{"event", "error": <type>}` (the failure made
  visible; the AP-24 tell asked for that). Readers key on `id`.
- D6. `malformed` rows carry `why` (bad-id, range, order, note-too-long, syntax, below-text). A line at the top of a text
  with no valid id goes to the first injection of that text left without a line; with none left, it is a row of its
  own. A later line for an id already settled is a `duplicate` row (a malformed first answer stays `malformed`).
- D7. The CLI: rows go to `--out FILE` (`-` for stdout); the summary to stdout (to stderr with `--out -`).
- D8. A stderr with no newline at its end gets one before the request line (the request needs its own line); every other
  byte between the two stamp lines is the hook's.
- D9. Live: 3 of my 4 live stamps read `missing` because the transcript holds no text record with their score lines,
  although I began each following text with them (section 7). The extractor pairs scores only with assistant text
  records. For the coordinator: run `python3 scripts/s1_scores.py <main transcript>` after the main thread's first
  stamped injections, to see whether the main thread's texts carry the lines.
- D10. The premise: HEAD is two doc-only commits past the PIN (the brief and a ledger line); no file in my boundary moved.

## ADJACENT DEFECTS (reported, not fixed: outside my boundary)

- `scripts/install_session_hooks.py:13` (the docstring, `unchanged`): the search intercept's exit-2 stderr "which the wrapper passes
  through unchanged". Since this landing the wrapper stamps it.

## Self-attack: the three likeliest ways this change is wrong

1. The stamp alters what the model receives beyond the two added lines (encoding, JSON, the exit-2 stderr). Ruled out:
   the tests hold the body byte for byte against literals and the off switch returns the PIN's exact bytes; live, the
   wrapper's sha256 equals the transcript text's for all 4 records, the blocked call's stderr included.
2. The wrapper blocks or drops context on its own account. Ruled out on every path I could reach: each stamping step
   sits in one try that returns the unstamped text (a RecursionError payload in the test; `no-fallback` killed);
   telemetry failures cost only the line; exit codes and stdout are unchanged (tests, two mutants); the size cap keeps a
   stamp from pushing a text into the harness's preview (tests, UTF-16 counting, two mutants); the added cost is p50
   4.2 ms and p95 9.8 ms on the stamp path. Residual: an exception outside `stamped()` (a stdout write) behaves as the
   PIN's did.
3. The extractor miscounts or mispairs. Ruled out on fixtures: only a hook text's first line can be its stamp (a stamp
   quoted inside a hook text is not an injection); a PreToolUse/PostToolUse `hook_success` is not read (no double count);
   threads split by file and by agentId (`one-thread-per-file` killed); harness-written assistant records are not texts
   (`no-synthetic-skip` killed). Residual, live: section 7 and D9, texts missing from the transcript make compliance a
   floor.

## Evidence tiers

- Verified (a command run, its output pasted above): the premise; the gate (481 passed, four runs); pyflakes; the
  line-separator check; 29 of 29 mutants killed by FAILED tests; the PIN outcomes; the added cost; the live read (4
  stamps, sha256 equal 4, 1 section joined, 1 score paired); no test line in the real telemetry.
- Verified, the report itself: `python3 scripts/report_lint.py tasks/briefs/system1/S1-RATE-report.md` printed `report_lint: 3 refs — OK 3, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)` (its first run caught a line number I had typed, 269 for 250, now fixed).
- Inferred: the exit-2 behavior per event (Claude Code's exit-code table, as I know it; not re-read from the binary).
  The 10,000-character swap (AF-AP-183's measurement, not re-measured).
- Assumed: none I rely on for a verdict.

Report written 00:1xZ.
