# T0-REPLAY: how plain trimming rules would have kept this session's context at a set level (task #346, D-105)

Written 2026-09-28 22:4xZ by the coordinator. Lane: sandbox `code-implementer`, model opus. A measurement tool, its tests
and one real run. You build and measure; the design verdict stays in the main loop.

## The owner's words (D-105, 2026-09-28 18:23:30Z)

Use Jev to trim the context window itself, so "we never get to a stage where we need compaction, because the context
stays at the optimum level". Above that level, find "which parts of the transcripts are useless to what we're doing" and
remove them from the active context, "almost on a turn-by-turn basis". "The logs are still there ... It's just the active
context."

## Your question

Under plain, deterministic trimming rules (no model decides anything), what would this session's active context have
looked like request by request, how often would a trim have fired, what would the trims have cost the prompt cache, and
how often did the session LATER USE something the rules would have archived? The answer picks the rule set, the age A,
the budget B and the low-water mark L for each venue (design §3, §6 T0).

Read first (READ): `docs/research/findings/jev-trim/D105-DESIGN-v1.md` (the policy, §3.1) and
`docs/research/findings/jev-trim/TRIM-AUDIT-2026-09-28.md` (§3: this session measured; the definitions you must match).

## Boundary

- CREATE `scripts/jev_trim/__init__.py`, `scripts/jev_trim/replay.py`, `tests/test_jev_trim_replay.py`, and the run's
  outputs under `docs/research/findings/jev-trim/replay-2026-09-28/` (JSON and one markdown summary, written by
  `replay.py`, never by hand).
- READ, reuse, never modify: `scripts/jev_pipes/transcript.py` (`iter_records`, the pinned-length streaming) and
  `scripts/jev_pipes/accounting.py` (`tokens`, `miss`, `percentile`: the committed P1 miss definition), and the fixture
  makers under `tests/fixtures/jev_pipes/` if they help.
- No git writes, no PC bridge, no subagents, no outward action, no model or network call. Start no process that outlives
  your run.
- Other lanes are live in this tree (the `.lanes-live` file lists their files). Touch none of them.

## Safety (read before any code)

- The transcripts can hold secret values. Stream them in memory. Your outputs, prints and report carry counts, sizes,
  byte offsets, `tool_use_id`s, tool names and rule names only: never any text from a record. A test proves it (item 6).
- Never read a thinking block's text. Its size comes from the request's `output_tokens` minus the visible characters, as
  the audit did (§3, Method); the only thinking fields you may read are the block's type and whether its stored text is
  empty.
- Read no secret file and no `*.env` file.
- If the harness or its classifier refuses a read, do not work around it (another path, another tool, a copy): stop
  that part, report the refusal verbatim with its time, and finish what you can. A verify lane met one such refusal on
  these transcripts on 2026-09-26 (`docs/INCIDENT-LOG.md`, 2026-09-26 12:2xZ).

## Items

1. **Premise.** Re-run every command in the PREMISE block below from the main tree. Any difference other than the ones
   the block names as expected: stop, report CONTRACT-INVALID with the difference, build nothing.
2. **The timeline.** One streaming pass over a transcript pinned at a byte length (take `stat -c %s` at your start; the
   main file grows while you run). Build, per API request (the first assistant record of each `requestId`, `isSidechain`
   false; the whole context = `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`, the audit's
   definition), the items that entered the context before it, each with: kind (tool result by tool name, tool input,
   visible assistant text, thinking, typed user text, task reminder, hook context, other attachment), its request index,
   its size, its turn (stop-hook boundaries, and the latest user `promptId`, both), its segment (between
   `compact_boundary` records) and its pairing (a tool result's call). Sizes: exact where the API gives them; user-side
   content at 2.90 characters per token (the audit's fit, §3.4); state every modeled size as modeled.
3. **The policy** (design §3.1), as a pure function over the timeline: rules R1 (superseded copies: task reminders but the
   newest; a Read of a file read again later; a hook context replaced by a newer one from the same source), R2 (thinking
   before the current turn), R3 (tool results older than A requests become stubs), R4 (large tool inputs older than A
   become stubs). The protected set (design §3.1) is never archived: the segment's first user message, the owner's typed
   messages, the newest copy of each loaded skill body, everything in the current turn, the last K turns (K = 2 default),
   and a stub keeps its call and result paired. A stub costs 40 tokens (a parameter). Hysteresis: when the active context
   passes B, archive in rule order, oldest first, until it is at or under L; then only append until it passes B again.
   Two modes: `between-turn` (a trim may fire only at a stop-hook boundary; the context may pass B inside a turn) and
   `per-request` (a trim may fire before any request). Simulate within each real segment from its real start; say so.
4. **What each cell reports**, for a grid of B in {100000, 131072, 150000, 200000, 250000}, L = 0.75 B (also 0.6 B at
   B = 200000), A in {10, 20, 50}, the rule sets {R1}, {R1, R2}, {R1, R2, R3}, {R1, R2, R3, R4}, and both modes:
   - the active context per request: median, p90, max; requests over B; the share of requests whose protected set alone
     passes B (the audit's R5 at 100000);
   - trims: count; tokens archived per trim; requests between trims;
   - the cache model: per trim, the tokens after the edit point are written again; each later request reads fewer tokens.
     Price both with ratios to the base input price (cache read, the 1-hour cache write) taken from Anthropic's prompt
     caching page: fetch it, cite the lines, or mark the ratios UNSURE and make them parameters. Report the net per cell
     against the real session (no trim);
   - USE-AFTER-ARCHIVE: for each archived item, `accounting.miss` with the committed definition (distinctive tokens used
     in the next 20 tool inputs or assistant texts and absent from the kept text and the earlier history; or the same
     command re-run within the next 20 tool calls), and a second horizon, the rest of the segment. Counts per rule, per
     tool and per age bucket (0-10, 11-50, 51-200, 201+ requests). This is a lower bound on need: say so.
5. **The runs.** (a) This session's main transcript,
   `/root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl`, pinned at your start. (b) The
   cross-check: with no policy, at the audit's pin (byte length 777,005,680), your per-day request counts and medians must
   equal the audit's §3.1 table (09-26: 781 requests, median 545,883; 09-28: 792, median 460,505). If they differ, find
   why before anything else and report it. (c) The three longest subagent transcripts under
   `/root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/subagents/` modified since 2026-09-26, each
   pinned at your start (some are live lanes; the pin makes that safe), in `per-request` mode: the closest thing here to
   a Hermes lane.
6. **Tests** (`tests/test_jev_trim_replay.py`, deterministic, synthetic transcripts built at run time):
   - normal: the timeline of a hand-built transcript; each rule archives exactly the expected items (the age boundary,
     supersede keeps the newest, thinking only before the current turn); hysteresis fires at B and lands at or under L;
     `between-turn` never trims inside a turn; the protected set is never archived; a stub keeps its pair;
   - failure: an unparseable line, a record cut at the pin, a request with no usage, a transcript with no requests;
   - the security boundary: a fixture holds a fake secret-shaped value built at run time; no 8-character piece of it
     appears in any output file, print or JSON (the repo's own `_hidden` pattern, e.g.
     `tasks/briefs/system1/vscrub2r2/vscrub2r1r2_red.py`);
   - a use-after-archive fixture: a token only an archived item held, cited later, counts 1; the same token also in a
     kept item counts 0 (the negative control).
   Name at least five mutants of your own (the age boundary off by one; supersede keeps the oldest; hysteresis stops at
   B, not L; the protected set ignored; the kept-item check dropped from the miss count) and show each killed.
7. **Gates**, each twice, with a private `--basetemp` outside any work tree, pasted from `bash scripts/test_summary.sh`
   with the set id from `bash scripts/pc_suite.sh set-id -- <files>`: `tests/test_jev_trim_replay.py`, and
   `tests/test_jev_pipes_replay.py` (the modules you reuse must stay green and unchanged).

## Report

Return the whole report as your final message (a report-file write is refused for subagents). Include: the premise
re-run; files with line counts and sha256; the gates pasted; the mutants; the cross-check (b); for each run, the table of
cells (at least: B, L, A, rule set, mode, median and p90 context, requests over B, trims, net cache units,
use-after-archive at 20 and at the horizon); and a DISCREPANCIES list (anything in this brief that did not match what
you found). Give no design recommendation: report what the numbers are.

## PREMISE — MEASURED at authoring (2026-09-28, main tree@6222e4a)

Printed by `bash scripts/premise_block.sh` from the main tree at the PIN, origin 6222e4a (the pushed id). Expected to
differ when you re-run it: nothing in the output. HEAD may have moved past the PIN (later coordinator commits); the
first line checks that the PIN is still an ancestor, and the second that the reused files did not change since. The
last line is one file's count (`tests/test_jev_pipes_replay.py`).

```
$ git merge-base --is-ancestor 6222e4a HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ git diff --stat 6222e4a HEAD -- scripts/jev_pipes/ tests/test_jev_pipes_replay.py tests/fixtures/jev_pipes/ | tail -1
$ grep -n '^def tokens\|^def miss\|^def percentile\|^CHARS_PER_TOKEN\|^LOOKAHEAD' scripts/jev_pipes/accounting.py
16:CHARS_PER_TOKEN = 4.06
17:LOOKAHEAD = 20
26:def tokens(text: str) -> frozenset:
36:def miss(original: str, kept: str, history: set | frozenset, lookahead_tokens: list[frozenset],
44:def tokens_saved(chars_saved: int, following_calls: int) -> float:
48:def percentile(values: list[float], q: float) -> float | None:
$ grep -n '^def iter_records\|^def scan\|^class Request\|^class Index' scripts/jev_pipes/transcript.py
31:class Request:
62:class Index:
85:def iter_records(path: str, limit: int, stats: collections.Counter) -> Iterator[tuple[int, dict]]:
132:def scan(path: str, limit: int, tools: set[str], min_chars: int, tokenize: Callable[[str], frozenset]) -> Index:
$ ls scripts/jev_trim 2>&1 | head -1
ls: cannot access 'scripts/jev_trim': No such file or directory
$ git grep -c -e jev_trim -e context_recall -- '*.py' '*.sh' '*.toml' | wc -l
0
$ test -s /root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl && echo main-transcript-present
main-transcript-present
$ test "$(ls /root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/subagents/ | grep -c 'jsonl$')" -ge 300 && echo at-least-300-subagent-transcripts
at-least-300-subagent-transcripts
$ sed -n 200,202p docs/research/findings/jev-trim/TRIM-AUDIT-2026-09-28.md | cut -c1-120
| 2026-09-26 | 00:12:50Z to 14:24:45Z | 781 | 545,883 | 733,680 | 783,173 | 130,278 | 2 |
| 2026-09-27 | no records (the day's first-offset jumps from 744,582,551 to 758,644,821) | 0 | — | — | — | — | 0
| 2026-09-28 | 12:17:26Z to 21:44:16Z (pin) | 792 | 460,505 | 714,430 | 783,147 | 127,359 | 3 |
$ python3 -m pytest -q -p no:cacheprovider --basetemp=/tmp/t0-premise-bt tests/test_jev_pipes_replay.py 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*//'
42 passed
```
