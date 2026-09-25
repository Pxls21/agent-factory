# VERIFY-S1-L1 report: the situation-to-skill hook against its full contract (D-090, design L1 and L3)

Lane: adversarial-verifier (sandbox, Opus 5.5). Started 2026-09-25 16:4xZ. Brief PIN 2ff48df; origin abae110 (= PIN + the brief commit)
and local HEAD 368a36f (+ one wiki commit); `git diff 2ff48df HEAD -- .claude scripts tests` is empty. Status: DONE (17:3xZ). Gate recommendation:
MERGE-READY-WITH-FOLLOWUPS (0 blocking findings; 26 non-blocking). The coordinator owns the gate.

**RESUMED after a container restart** (`date -u`: 2026-09-25T16:48:08Z). The first run died at about 16:4xZ while it re-measured the
premise; this pass re-measures it from the start.

## 0. Premise re-measurement (16:4xZ, the sandbox, after the resume)

MATCH on every line that matters, so no CONTRACT-INVALID. Two lines moved as expected, and neither changes a byte in scope:

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf
abae110 VERIFY-S1-L1 and L5 briefs (D-090) ...      (brief: 2ff48df; abae110 is the brief commit itself, and local HEAD
                                                      368a36f adds one wiki commit: git diff --name-only abae110 HEAD =
                                                      wiki/topics/live-state.md; git diff 2ff48df HEAD -- .claude scripts tests = empty)
$ git log --format=%h --grep='^S1-L1 landed' -n 1 origin/claude/soundbox-kit-migration-iz1jwf
6195b77
$ df -h / | awk 'NR==2{print $4}'
2.0G
$ sha256sum <file> | cut -c1-16      (working tree, and `git show 2ff48df:<file>`: identical)
a3e37aba8adbc014  .claude/hooks/system1-context.py
eef9252d0c0c2b9f  .claude/hooks/system1-situations.json
73cd14590abbd0d5  .claude/settings.json
a6632b8003ccffe3  scripts/install_session_hooks.py
575dc3ed876f0084  .claude/hooks/session-start.sh
5f2ed3707dcf89a7  scripts/hook_context.py
$ grep -c system1-context /home/user/.claude/settings.json
2
$ ls .jev/system1-off; wc -l < .jev/system1.jsonl
ls: cannot access '.jev/system1-off': No such file or directory
303                                   (brief: 214; the hook is live on every call, so the log grows)
$ python3 -c '... len(rows)'
38
$ bash scripts/test_summary.sh tests/test_system1_context.py tests/test_session_start_hook.py tests/test_session_hooks.py tests/test_hooks_worktree.py --basetemp <scratch>/bt/p1
pytest-summary: 124 passed in 12.69s    (rc 0)
$ printf '%s\n' <the 4 files> | sort | sha256sum | cut -c1-12      (pc_suite.sh's set_id formula, run locally)
2dc71b948b8b
```

Safety checks before running anything: the builder's tests point the hook's state at a tmp dir (`AF_SYSTEM1_STATE`), run
`session-start.sh` with `CLAUDE_CODE_REMOTE=false` or inside a fake tree with a fake setup.sh, and run the installer only
with `--target <tmp>`. HOME is /root; `/root/.claude/settings.json` holds no hooks, so the live registration is the one in
`/home/user/.claude/settings.json` (7 command entries, 2 of them system1): no double registration.

## Method (applies to every section below)

Scratch copy `verify-s1l1/repo/` (572 KB): the hook, its table, `session-start.sh`, `wiki-context.py`, `settings.json`,
`hook_context.py`, the installer, and the SKILL.md of the 19 corpus skills (every row skill is among them); `cmp` equal to
the tree. Every behaviour reproduction runs the command STRING read from the copy's `.claude/settings.json` through
`sh -c`, with `CLAUDE_PROJECT_DIR=<copy>` and a payload on stdin, and reads `additionalContext` from the wrapper's one JSON
line. State is the copy's own `.jev/` (the production default path; `AF_SYSTEM1_STATE` is never set). The oracle
(`verify-s1l1/h.py::check`) is mine: its own heading parser, and it requires every injected line to be a whole line INSIDE
the pointer's section (the builder's oracle accepts a line anywhere in the file), a `…` exactly where lines are not
adjacent, and the pointer's skill equal to the label's.

## 1. Verbatim (item 1) — reproduced

- **Static: all 38 rows resolve to exactly the line ranges of the builder's section-2 table**, including the 7 rows the
  second skill bake moved (pc-suite 76-79, proof-regen 67-68, test-vendored-manifest 80-86, test-proof-status 63-66,
  test-gate 74, pasted-count 74, push-delegate-work 534-539). Every resolved line is inside the named section (my parser).
  No skill line mimics a label, a pointer or `…`; no corpus skill repeats a heading.
- **Dynamic: every row through the registered PreToolUse command, with my own fixtures** (`verify-s1l1/rows_dyn.py`: other
  shapes than the builder's, e.g. `git -C <dir> push`, `git add -A && git commit`, a `.sh` under harness-ports/tests, an
  Edit of src/agent_factory/, a Write of a test file), a fresh window per row, up to 6 calls: 89 calls, 0 oracle
  failures, 0 lines delivered twice, every line of every matched row delivered, every output ≤ 2,048 bytes and equal to the
  telemetry `bytes`. Exceptions: F1 (a missed fixture) and F3 (row order, by design).
- **Prompt path: 40 prompts through the registered UserPromptSubmit command** (`verify-s1l1/prompt_dyn.py`): 0 oracle
  failures, every excerpt ≤ 2,048 bytes, every total ≤ 4,096 and equal to the telemetry. Exception: F4.

**F1. The command-position prefix has no `while`, `until`, `if`, `elif`, `!` or `{`, so `while pgrep -f '[l]ane_gate'
>/dev/null; do sleep 5; done` injects nothing.** CMD_POS (system1-context.py:82) lists `then|do|else|nohup|setsid|exec|
time|sudo|env|xargs|timeout`. The `pgrep` row's own rule is about a "liveness/wait loop", and `while pgrep …` /
`until ! pgrep …` / `if pgrep …; then` are that loop's usual shapes. The same gap hides every row's command after
`if`/`while`/`until`/`!` (e.g. `if bash scripts/pc.sh …; then`). Frequency on the replay: section 9a.

**F2. The answer to the brief's D3 question: YES, a rule arrives without its qualifying line, and mostly by the row
design, not only by the budget.** A selector names a PHYSICAL line of a hard-wrapped paragraph, and one physical line
often holds the end of one rule and the start of the next. Static count over the 38 rows (an "entry" as the hook's own
ENTRY_START_RX defines it): 6 runs start mid-entry and 11 end mid-entry. The ones that change what a rule says:
- `push` (env-tool-quirks 40-47, `…`, 50) skips lines 48-49: "*(Since CTX1, D-089, no automatic `gitnexus analyze`
  rewrites AGENTS.md or CLAUDE.md: the race above now needs a manual analyze run without `--skip-agents-md`.)*". So the
  injection tells the agent to run `git checkout -- AGENTS.md CLAUDE.md && … push_clean.sh` on every push, a command that
  discards uncommitted edits to those two files, without the line that says the race behind it is now rare.
- `push-delegate-work` (orchestration 534-539) starts inside a code span, "origin/<branch>..HEAD` before ANY push**", so
  the words "run `git log" (line 533) never arrive; it ends "never HEAD.** **The push is also its", and the rule it
  starts ("own CALL, sequenced after you have READ every gate/probe result it depends on", 540-541) never arrives.
- `test-edit` and `gate-edit-tactics` (anti-hollow-green 14-16) end "not just the golden path. **A": the numeric-guard
  rule on line 17-18 ("A fail-closed NUMERIC guard … must reject the WHOLE unusable class — `not math.isfinite(x)` AND a
  positivity check") is cut to one dangling word. `test-edit`'s second run ends "(d) A gain on one axis NEVER converts to
  trust on an orthogonal axis — combine" (line 34); "quality×confidence with AND (a ceiling), never a sum" never arrives.
- Starts with another tool's text: `pc-suite` starts "checkpoint commit pastes; long sets run it DETACHED …" (the tail
  of the lane_gate.sh entry: "it" is lane_gate.sh, not pc_suite.sh); `anchor-edit` starts "DELTA gate: new hits only; …"
  (the tail of lint_delta.py's entry).
- Ends mid-sentence with no change of meaning: `ops-script` "(recover a", `ouroboros` "each question issues a Synapse
  fan-out: submit" (the payload shape on line 23 never arrives), `claude-md-gitnexus-block` "never hand-edit" ("it."),
  `test-gate`/`pasted-count` "— a `git archive`", `brief` "One hour after 0k, the".
- The budget split is real too, and it happened live in THIS lane's window (the telemetry record at 17:00:56Z): my report heredoc held
  "`git -C <dir> push`" after a backtick (F6), `push` injected 1.5 KB, and `push-delegate-work` arrived cut after
  line 536, ending "**While any delegate is LIVE, log-then-push-HEAD is itself" (the predicate, "a TOCTOU race …", is on
  537 and waits for the next push-shaped call in the window, which may never come). Replay count of cut remainders that
  never arrive: section 9a.

**F3. The `brief` row injects its four runs in ROW order (orchestration 173-174, 179-183, then 27-32, then 211-215):**
rule 0l arrives before 0a, with `…` between. Verbatim and inside the section; the order is the row's priority. INFO.

**F4. On the prompt path an excerpt whose FIRST line is longer than the share (2,048 bytes less the label and the
pointer) is skipped whole, pointer included.** Only two corpus lines are that long (of 3,663): pc-bridge-lanes 19 (4,667
bytes) and 23 (4,800), the builder's D9 lines. But the excerpt start is the entry that shares the most weight with the
prompt, and a 4,800-byte line holds the most words, so it wins for PC-lane prompts. Reproduced through the registered
command: "launch the pc lane with pc_lane.sh and re-attach it later" scores `pc-bridge-lanes § Launching, re-attaching and
sizing PC lanes` best (18.79), its excerpt starts at line 23, telemetry `skipped: budget`, and only the second section
(`Lane throughput and admission`, 928 bytes) reaches the model. The best section's pointer never arrives. The contract
says "Cut at a line boundary and keep the pointer"; D9 names the lines but not this prompt-path effect. Classification in
the inventory, after the prompt replay (section 8).

**F5. A single heading word can carry an unrelated section over the threshold.** "the systemctl user unit restart on the
PC failed with XDG_RUNTIME_DIR" injects `orchestration § Repair briefs: the unit of work is the SET …` (score 12.88 against
MIN_PROMPT_SCORE 12.0; the lead token is "unit"). The governing text (pc-bridge-lanes line 23) cannot be reached: "pc" is two
letters (TOKEN_RX needs three) and no other word of the prompt is in a pc-bridge-lanes heading. Frequency: section 8.

## 2. Once per window (item 2) — reproduced through the registered SessionStart and PreToolUse commands

`verify-s1l1/window_dyn.py` and `conc_dyn.py`, on the copy, with the SessionStart command string of the copy's
settings.json (`session-start.sh`, `CLAUDE_CODE_REMOTE=false`):

| step | main window | subagent window (same session) | other session | telemetry `removed` |
|---|---|---|---|---|
| first `git commit` call | injects | injects | injects | |
| same call again | nothing | | | |
| SessionStart `startup`, `fork`, `""`, `"weird"` | nothing (kept) | nothing (kept) | | 0 each |
| `compact` (no agent_id) | injects again | nothing (kept) | nothing (kept) | 1 |
| `compact` with the subagent's agent_id | nothing | injects again | | 1 |
| `resume`, then `clear` | injects again | injects again | nothing (kept) | 2, 2 |
| SessionStart with empty stdin | rc 0, no output | | | |

- **7-day prune:** 4 files of another session, mtime 8 days back (a `.json`, its `.lock`, a `.tmp`, a second agent's
  `.json`), all removed by the next `startup`; `removed` counts the 2 `.json` only. A LIVE window whose marker has not
  changed for 8 days is pruned too, by any session's SessionStart, and then injects again (INFO: only an idle week).
- **Two processes at once, lock free:** 16 parallel calls in one fresh window (8 command shapes, 4 trials): 83 lines
  delivered per trial, 0 delivered twice, 0 missing from the marker, every marker valid JSON, no stray `.tmp`.
- **F8. Lock held > 0.5 s: the once-per-window rule breaks, and more than "one repeated injection".** With the window's
  `.lock` held from outside (a slow sibling), every call waits LOCK_WAIT_S and goes on unlocked (hook-internal ms: min
  506, median 525). Two trials of 16 parallel calls: 37 and 40 lines delivered twice in the same window, and 36 and 29
  delivered lines missing from the marker (lost updates, so they come back on later calls). The docstring's "the worst
  case is one repeated injection" (system1-context.py:473) is not what happens. What holds the lock that long: the whole
  plan (row matching and skill reads) runs inside it (lines 561-568), so one slow call is enough (F7). Measured end to
  end: a 198 KB heredoc of minified-JS-like text (`a&&b||c(d);` repeated, no `/`, no spaces) held the window for 36.5 s;
  a `git commit` call launched 1.5 s later in the same window waited 517 ms, then injected `commit` and
  `commit-increment`, and the slow call then injected the same rows again (1,891 bytes, rc 0).
- Marker growth: bounded by the distinct lines the table and the corpus can inject (3,663 corpus lines, 16-hex keys:
  under about 80 KB); files: one marker and one `.lock` per window, until a reset or the prune. Live now: 4 windows, 8 files.
- `fork` is not reset (the contract names compact, resume and clear only; a fork gets a new session id, so its window
  starts empty while its context holds the parent's transcript, as the builder's D5 says for a resume). INFO.

## 3. Budgets (item 3) — reproduced

- Tool path: 89 calls in section 1 (up to 5 rows at once) and every live record (377, max 2,030 bytes): never over 2,048;
  the telemetry `bytes` equals the injected bytes on every call.
- **The boundary, in bytes, with multi-byte text** (a copy of env-tool-quirks whose `commit` line is rebuilt of 2-, 3- and
  4-byte characters to an exact size; the registered command): 1,874 and 1,875 bytes inject (2,046 and 2,047 bytes out,
  the line verbatim, no U+FFFD); 1,876 and 1,877 bytes are skipped `budget`, and the next row takes the room. So the cut is
  exact in bytes and never splits a character. The wrapper's JSON line is larger (`json.dumps` escapes non-ASCII: 5,213
  bytes for 2,047 bytes of text); the model reads the decoded string.
- Prompt path: 40 synthetic prompts (section 1) and the 148 human prompts of the replay: every excerpt ≤ 2,048, every
  total ≤ 4,096 (max 4,094).
- A single line longer than the budget: no row selects one (the builder's table test holds that). On the prompt path it
  drops the best section with its pointer (F4): 3 of the 217 real human prompts (1.4 %) — 2 lost their best section, 1 got
  nothing at all.

## 4. Never blocks, always exits 0 (item 4) — reproduced

Every hostile input below ran through the registered command on a fresh copy (`verify-s1l1/hostile.py`): rc 0 and
0 bytes of stderr every time.

| input | injected | telemetry |
|---|---|---|
| empty stdin; `{not json`; invalid UTF-8; 100k-deep JSON; 50k-deep `tool_input` | nothing | nothing / JSONDecodeError / UnicodeDecodeError / RecursionError ×2 |
| NUL escapes in the command; `cwd` an int, `session_id` a dict, `agent_id` `../../../etc/passwd` | yes | marker `nosession._________etc_passwd.json`: no traversal |
| a 30 MB Write | yes (0.31 s wall) | normal |
| `command` a list or null; `tool_input` a string; `file_path` a list; tool `Read` | nothing | normal, matched [] |
| skill dir missing; SKILL.md a directory; table missing; table not JSON | nothing | FileNotFoundError / IsADirectoryError / FileNotFoundError / JSONDecodeError |
| a row regex that does not compile | nothing | `error` (the type of `re.error` is named `error`) |
| the `commit` row's anchor broken | `commit-increment` only | `commit` skipped `unresolved` |
| `.jev` missing / `.jev` a regular file | yes (created) / nothing | normal / none |
| full disk (`ulimit -f 0`: every write fails) | nothing | none (the log cannot be written); an orphan `…json.<pid>.tmp` is left per call |
| a torn marker (`{"keys": [`) | nothing, and nothing on every later call of that window | JSONDecodeError each call, until a reset |

**What bounds the run time: nothing inside the hook except the 2 s stdin wait and the 0.5 s lock wait.** The skill files
and the table are read with a plain `open()` (lines 112, 293, 335, 381), and the matching has no bound (F7). The wrapper
bounds it: `hook_context.py` kills the hook at 55 s (line 21, "under Claude Code's 60 s default hook timeout"; no
registration sets `timeout`). Reproduced with a FIFO in place of env-tool-quirks' SKILL.md and a `git commit` call: rc 0 after
55.1 s, no output, stderr "hook_context: python3 did not run: Command '['python3', …" (the TimeoutExpired text, hook_context.py:32-33; the
hook did run), no telemetry line,
no process left. So at the timeout the tool call goes on after a 55 s stall, and the decision is missing from the log.
(`hook_context.py` also reads its own stdin unbounded, line 29: pre-existing, shared by every wrapped hook.)

**F7. The command-position scan is quadratic on long runs with no spaces, many separators, and no `/`** (`(?:\S*/)?` at
line 84 rescans the rest of the run from every separator). Measured in process: 40 KB of `;` 2.6 s, of `x;` 1.4 s, of `a|`
1.3 s (×4 per doubling); a 22 KB minified-JS-like heredoc (`a&&b||c(d);`) 0.47 s; one `/` every 200 characters brings it
to 0.000 s. End to end, a 198 KB such heredoc took 36.5 s through the registered command and held the window lock the
whole time (F8). None of the 16,830 real calls came near it (max 14.1 ms in process), so this is a FOLLOW-UP.

**F9. A failed marker write leaves its temp file.** `write_json_atomic` (lines 443-455) removes nothing on an error, so
every call on a full disk leaves one `<marker>.json.<pid>.tmp` (0 bytes, one inode) until the 7-day prune. INFO.

## 5. The kill switch and the exception path (item 5) — reproduced

`verify-s1l1/ks_secrets.py`, registered commands, copy: with `.jev/system1-off` as a file, a directory or a symlink to a
file, PreToolUse and UserPromptSubmit print 0 bytes, rc 0, and log nothing; the SessionStart reset still runs, prints
nothing and logs its one line. A dangling symlink named `system1-off` does NOT switch it off (`os.path.exists` follows
it; INFO, only by hand). The exception path (a directory at the marker path): rc 0, 0 bytes out, 0 bytes stderr, exactly
one telemetry line, keys `error, event, ms, t, tool`, `error: OSError`.

**D6, the reset while the switch is on: right.** The switch exists to silence injection. The reset injects nothing and
prints nothing; it only forgets windows that have ended. If it did not run while the switch is on, a window compacted
during an off period would keep its old marker, and after the switch is removed that window would never get those lines
again. The one side effect is its telemetry line.

## 6. Telemetry and secrets (item 6) — reproduced

Canaries built at run time (`"CNRY" + secrets.token_hex(12)`) in 11 fields over 8 calls: the command, the description,
Write content, a Write path (a directory name), Edit old and new text, an Edit path outside the repo, `cwd`,
`transcript_path`, `tool_use_id`, a human prompt, a harness-event prompt, and the SessionStart payload. Injections happened
on 5 of the 8 calls, so the canaries rode through real matching. Then every file in the copy was scanned for each
canary and for its hex part, with the marker, its lock, the prompt cache and the log all present, and the hook's stdout
and stderr too: **0 hits**. `strace -f` over four of the calls: the hook and the wrapper open for writing, create, rename or
unlink only paths under the copy's `.jev/`; nothing outside it. Telemetry key sets are exactly: PreToolUse `bytes, event,
injected, matched, ms, skipped, t, tool, window`; UserPromptSubmit the same without `tool`, plus `why` when it declines;
SessionStart `event, ms, removed, source, t`; an exception `error, event, ms, t, tool`. The live log (377 records at
16:55Z) has only those key sets and no `error` record. Logged values that come from the harness payload itself:
`tool`, `source` (verbatim) and the window id (the session id and agent id, cleaned and cut to 80 characters, D6).

## 7. Matching (item 7) — reproduced on the replay, counts only

- **Per-row false positives from quoted or heredoc text** (the V2/V3 masking of section 9a; injections per row over the full
  transcript, V0 → heredocs masked → heredocs and unowned quotes masked): `graft` 38 → 19 → 18, `lane-context` 33 → 17 →
  16, `code-review-graph` 6 → 5 → 2, `ouroboros` 6 → 4 → 3, `test-vendored-manifest` 22 → 15 → 15, `test-gate` 76 → 62 →
  57, `ops-script` 97 → 80 → 76, `vendored-manifest-write` 34 → 28 → 27, `proof-regen` 49 → 43 → 41, `pc-suite` 67 →
  57 → 57, `pc-lane` 72 → 66 → 63, `pgrep` 103 → 94 → 94. So for graft, lane-context, ouroboros and code-review-graph about
  half of the injections come from a command named inside a document or a string, not run; for test-gate, ops-script
  and test-vendored-manifest a fifth to a third. `pasted-count` goes UP (43 → 61) when `test-gate` fires less:
  the two share env-tool-quirks line 74, and the dedupe hands the line to whichever row fires first.
- **False negatives:** F1 (`while`/`until`/`if`/`!` shapes; 4 calls of 16,830 get other text, no row's count changes).
  Path rows see only repo-relative paths: of the Write/Edit calls, 209 of 1,212 in the main transcript and 574 of 3,237 in
  the 293 subagent transcripts target `/tmp` (scratch copies, lane drafts), and 18 subagent calls a worktree path. Those
  get only the text rows and the `test_*.py` filename pattern. INFO.
- My own fixtures (section 1) hit every row with shapes the builder's fixtures do not use; only F1 missed.

## 8. The prompt path (item 8) — measured on this session's 217 human prompts, counts only

- Which records are prompts: user records with an `origin` and no `isMeta`. `origin.kind` is `human` on 217 and
  `task-notification` on 548; the hook's prefix list filters all 548 (`<task-notification>`). Compaction summaries (130)
  and meta records carry no `origin`.
- Outcome in sequence with the tool calls (shared window marker, as in production): 146 prompts inject, 70 inject nothing,
  1 has no tokens. 2 excerpts on 76, 1 on 70; median 2,226 bytes, max 4,094. In a fresh window per prompt: 148 of 217
  (68 %).
- **"Unrelated" cannot be counted without reading prompts, which the brief forbids. Proxies (fresh window per prompt):**
  the best section's lead (the prompt words found in its heading or skill name) is ONE word in 108 of 146; a one-word lead
  AND under 20 % of the prompt's words in the injected text: **54 of 148 (36 %)**, weak evidence of relatedness; a lead of
  two words or more AND at least 20 % overlap: 23 of 148 (16 %); in between: 71. F5 shows one such case in full.
- F4 on real prompts: 3 of 217 (2 lose their best section, 1 gets nothing).
- The oracle over all 148 real injections: 0 failures (verbatim, inside the section, pointer right), 0 over budget.
- Live: the prompt path has never injected in a live session. All 8 live UserPromptSubmit records (16:02-16:55Z) are
  `why: harness-event` (task notifications). The builder listed this as not verified live; it is still not.

## 9a. Replay (item 9) — the builder's numbers REPRODUCED EXACTLY by an independent replay

`verify-s1l1/replay.py` (mine, not the builder's): the main transcript streamed once, `plan_tool` of the copy per
Write/Edit/Bash `tool_use` in file order, windows split at `compact_boundary`, variant B also reset at every
`SessionStart:resume` hook attachment. Counts only. Cut at the builder's last call (2026-09-25T16:00:25.300Z):

```
windows: 130 (compact_boundary records: 129); recorded SessionStart:resume runs: 9
calls: {'Bash': 15488, 'Write': 537, 'Edit': 659} | total 16684
V0: calls that received an injection: {'Bash': 1336, 'Write': 142, 'Edit': 120} total 1598 | injected bytes 2043712
V0 variant B (+ resume resets) bytes: 2093622
bytes per injected call: median 1275.0 max 2046
bytes per window (A, 130 windows): median 16672.5, p90(index) 20427, max 25680, windows with none 2
Write/Edit/Bash calls per window: median 131.0 max 310
```
Every one of the 38 per-row lines (matched / injected / cut / skipped duplicate / skipped budget) equals the builder's
section-5 table. (The builder's "median 16672" is this 16672.5 printed as an integer.) One trap on the way, in my harness,
not the hook: the hook takes ROOT from its own file, so a copy of the hook at another path makes every transcript path
non-relative and every path row silent (my first run: Write 41, Edit 61); the replay sets the module ROOT back to the
repo.

Full transcript to now (16:47:26Z, 16,830 calls, 131 windows): 1,605 calls injected, 2,050,556 bytes, median 16,545 bytes
per window. The in-process `plan_tool` time on the 16,830 REAL calls: median 0.22 ms, p99 2.94 ms, max 14.1 ms, none over
50 ms, so F7's quadratic case never happened on a real call (FOLLOW-UP, not a blocker).

Variant measurements (same pass, same dedupe):
- **F1** (CMD_POS plus `while|until|if|elif|!|{`): 4 calls get other text, 1 injection fewer overall. Real but rare here.
- **D11, measured as asked** (heredoc bodies masked unless a shell reads them; then quoted spans masked too unless
  `pc.sh`, `ssh`, `eval` or `sh -c` owns them): injected calls 1,605 → 1,552 (-3.3 %) → 1,533 (-4.5 %); bytes -4.4 % and
  -5.1 %; 271 and 357 calls get other text. The builder measured -2.5 % with its own masking. On a doc-writing workload
  it is far higher: this lane's own report heredocs drew `push`, `push-delegate-work`, `ouroboros`, `pgrep`, `pc-suite`,
  `ops-script`, `pc-sqlite`, `pc-podman`, `background`, `graft` and `vendored-manifest-write` (F6).
- **Rows cut and never finished in their window (D3's budget half):** 38 windows closed with a row that had arrived
  only in part: `push-delegate-work` 19 of 131 windows (its tail, the TOCTOU race and "Push the REVIEWED SHA explicitly
  … never HEAD", never arrived), `code-edit-guidelines` 6, `brief-contract` 5, `graft` 2, six other rows 1 each.

## 9b. Latency (item 9) — reproduced within a few ms

`verify-s1l1/latency.py`, the registered commands on a copy, 20 runs each (builder's value in brackets):

```
reference: hook_context.py wrapping `true`                 wall median   30.3 ms [28.2]
PreToolUse Bash, no row matches (ls -la)                   wall median   58.0 ms [58.3] | hook-internal  2.5 ms [2.5]
PreToolUse Bash, 2 rows inject (git commit), fresh window  wall median   62.1 ms [61.4] | hook-internal  5.5 ms [5.3]
PreToolUse Bash, same window again (duplicate)             wall median   62.8 ms [59.1] | hook-internal  5.3 ms [5.0]
PreToolUse Edit of a code file, fresh window               wall median   62.5 ms [61.5] | hook-internal  4.6 ms [4.4]
UserPromptSubmit, cold cache (first prompt builds it)      wall          89.7 ms [91.9] | hook-internal 34.6 ms [33.7]
UserPromptSubmit, warm cache, 2 excerpts inject            wall median   70.4 ms [66.5] | hook-internal 10.2 ms [10.6]
UserPromptSubmit, warm cache, nothing scores               wall median   66.7 ms [63.9] | hook-internal  6.7 ms [6.0]
SessionStart: session-start.sh with the reset (compact)    wall median   34.9 ms [35.3] | hook-internal  0.8 ms [0.8]
kill switch on: PreToolUse Bash (git commit)               wall median   55.3 ms [57.4]
```
Live, in the real harness (the hook's own `ms`, 368 PreToolUse records, 16:02-16:55Z, other lanes running): median 2.8 ms,
p90 6.0, p99 11.2, max 14.6. The floor is two Python starts.

## 10. Registration (item 10) — reproduced

- `.claude/settings.json` and `our_hooks()` agree on every event, matcher, script and wrapper after normalising paths,
  guards, `cd` and the env prefix. The one difference is old: SessionStart runs `session-start.sh` directly in one and
  through `bash` in the other (not touched by S1-L1).
- **The committed installer reproduces the live file byte for byte** (`--target` a scratch file, then `cmp` with
  `/home/user/.claude/settings.json`), and `--check --target <copy of the live file>` says `present`. So the
  registration that went live mid-lane (D1, AF-AP-222) is the reviewed one.
- A second install prints `unchanged` and leaves inode, mtime and mode alone; `--check` is 1 before and 0 after.
- `--remove` on a scratch file with foreign entries keeps foreign groups, a foreign event and a top-level key. It also
  deletes (INFO, the merge rule predates S1-L1, `git diff 3c495c9 6195b77` touches only `our_hooks`, the docstring and the
  message): a foreign hook in the SAME group as one of ours, and a hook whose command names `<repo>/.claude/hooks/` even if
  the owner wrote it (`my-own-owner-hook.sh`).
- D6 (the reset while the switch is on): right (section 5).

## 11. The coordinator's manifest change (item 11) — reproduced

`sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv` has both hook files `first-party` (18 first-party rows); the manifest row
`.claude/ (first-party)` says 18, `kit-adapted` 17. On a `git archive HEAD` export (so the ignored `.claude/fast-jev-output/`
of the shared tree is absent; `.claude sandbox-kit vendor .agents/skills/anti-hollow-green` plus the lock, SBOM, script and
test; 73 MB, deleted after), one test per run: `test_real_claude_split_counts_and_class_file`,
`test_k1h_claude_classification_and_remainder`, `test_k1h_honey_copy_byte_change_falls_back_to_first_party` and
`test_committed_manifest_passes_check_at_a_later_head`: 1 passed each. Negative control: with
`.claude/hooks/system1-situations.json` removed from the export, the first test fails `assert ['17', '0'] == ['18', '0']`.

## 12. Mutation audit: the builder's 91 tests against my mutants — 7 of 8 SURVIVE

`verify-s1l1/mutate.py`: each mutant alone on the copy's hook, graded by the builder's own test file copied beside it
(91 passed unmutated), restored after each:

```
SURVIVED m1 window lock removed (no flock)                        91 passed
SURVIVED m2 budget counts characters, not bytes                    91 passed
SURVIVED m3 telemetry logs the Write/Edit path                     91 passed
SURVIVED m4 telemetry logs the prompt's words (lower-cased)        91 passed
SURVIVED m5 marker stores the prompt's words                       91 passed
KILLED   m6 continuation lines dropped                             test_the_tool_budget_cuts_at_a_line_boundary_and_keeps_the_pointer
SURVIVED m7 the 7-day prune removed                                91 passed
SURVIVED m8 unresolved rows raise instead of skip                  91 passed
```
Each survivor is a real behaviour change, not an equivalent: m2 injects **2,272 bytes** on a multi-byte line where the
real hook stays at 1,175 (the budget is the contract's); m1 is the F8 duplicate class; m3-m5 leak input into state
(the telemetry test's canary is upper-case and only in a Bash command and a prompt, while the tokenizer lower-cases, and it
scans `system1.jsonl` only); m8 turns one broken anchor into "nothing injected for any row".
`test_a_changed_skill_line_is_reported_unresolved_not_injected` calls `resolve()` directly: its name claims a runtime
behaviour it never runs. The implementation is right on every one of these (sections 2, 3, 4, 6); the gate is what is weak.
The builder's own 23 + 3 mutants were not re-run (their claim, not re-verified).

## 13. Reachability, stale context, evidence audit

- **Delivery in the real harness, main thread:** the 15 main-window injections in the live telemetry (16:03:48Z-16:46:45Z)
  match 15 `hook_additional_context` attachments with a system1 label in the main transcript (Bash 12, Edit 2, Write 1),
  same first and last times. In this lane's own subagent window the context arrives as hook context on my own calls, seen
  directly: the live telemetry for this window, read at 17:34:50Z (`date -u`), holds 102 calls, 12 with an injection, 18 distinct
  rows, 3 row injections cut. By my own record of those calls, 3 fit the call (`stamp` on the resume stamp, `test-gate` on the premise
  gate, `test-vendored-manifest` on the manifest tests; the last one said exactly how to run them) and 9 came from command
  names inside my report and fixture heredocs (F6).
- **Stale text the change makes false or incomplete:** `system1-context.py:472-473` ("the worst case is one repeated
  injection", F8); `docs/HARNESS-PORTS.md:223` ("all five project hooks are ported": there are six, and system1 is not
  ported, per the builder's own NOT-done) and `STATUS.md:50` ("four of the five hooks"): F11. The installer's line 5
  ("none of the five project hooks fired there") describes the past incident and is right.
- **Spot checks of the builder's evidence:** the AF-AP-204 file (`-home-user-agent-factory/bdab799a-….jsonl`): 3,074,681
  bytes, 53 assistant records, 0 `tool_use`, as claimed. `/tmp/agent-factory-setup.log:75` now reads `session hooks:
  unchanged in …` because the 16:44Z resume rewrote the log; the live file's mtime is 16:02, as claimed, and it equals the
  committed installer's output. The section-2 table: every range reproduced. The replay: every figure reproduced. The
  latency: reproduced. The mutation claim: not re-run (section 12). The contract's evidence demand 4, re-run here:
  `pytest-summary: 124 passed in 12.69s` and `124 passed in 13.27s` (4 files set=2dc71b948b8b), pyflakes rc 0, the U+2028/9
  grep 0 on all 8 files and this report. The landing commit touches only boundary files plus the coordinator's manifest
  files; `wiki-context.py` is `fab9b615481333c8`, unchanged; no skill file changed.

## 14. Reproduced, reviewed statically, skipped

- Reproduced (through the registered command strings on copies, or in process with the production functions): every
  item above except those listed next.
- Reviewed statically only: hook_context.py's unbounded stdin read (F18); the harness's own 60 s default (quoted from
  hook_context.py:21, not measured); "no network" (the imports: json, os, re, sys, time, select, hashlib, math, stat,
  fcntl; the wrapper: json, subprocess, sys).
- Not reproducible here (UNVERIFIED): whether a PreToolUse `additionalContext` is delivered when search-intercept blocks
  the same Bash call with exit 2 (no blocked call on the main thread since 16:02Z to observe; the marker records the lines
  either way); whether a subagent's own compaction fires SessionStart with its `agent_id` (the reset handles the payload if
  it does, section 2); the prompt path in a live session (never fired on a human prompt yet).
- Skipped on purpose: the builder's own mutants (a claim; my own set is the audit); a genuinely slow filesystem (no FUSE;
  a FIFO stands in for a read that never returns); the whole `tests/test_vendored_manifest.py` (disk: the four tests that
  pin the change ran one at a time on an export). Scratch: 1.4 MB at the end (`verify-s1l1/`: scripts and two small copies;
  `bash setup_copy.sh` rebuilds the copies).

## FINDING INVENTORY (no severity filter; 26 findings, 0 BLOCKER)

Fields: class · evidence · contract mapping · canonical path · material effect · reproduction · suggested fix. `V` =
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-s1l1` (run `bash V/setup_copy.sh` first).

1. **F1 CMD_POS has no `while|until|if|elif`, `!`, `{`** · FOLLOW-UP · reproduced · C1 (recognition; shapes unpinned) ·
   yes · 4 of 16,830 replay calls get other text, no row count moves · `cd V && python3 f1_while_pgrep.py` (rc 1 now) ·
   add the keywords and `!\s`, `\{\s` to CMD_POS; a `while pgrep` fixture.
2. **F2 rows start or end inside an entry; qualifiers left out** · FOLLOW-UP (the most important one) · reproduced
   statically (17 runs) and live in this lane's window · C1 "key lines, verbatim": the lines are verbatim, and which
   lines are key is not pinned; this is the brief's D3 question, answered YES · yes · `push` omits env-tool-quirks 48-49
   (the CTX1 qualifier on its `git checkout -- AGENTS.md CLAUDE.md` advice); `push-delegate-work` drops "run `git log"
   (533) and cuts "**The push is also its" (539); `test-edit`/`gate-edit-tactics` end on "**A" and drop the NaN
   numeric-guard rule (17-18); the budget half: 19 of 131 windows never got push-delegate-work's "Push the REVIEWED SHA
   explicitly … never HEAD" · `cd V && python3 rows_static.py` (rc 1, 17 runs) · select whole entries: push +48-49,
   push-delegate-work 533-541, test-edit/gate-edit-tactics to 18 (or stop at 15); order push-delegate-work before push, or
   give it its own call; pc-suite and anchor-edit need a line break in the skill (outside this boundary).
3. **F3 the `brief` row injects in row order, not file order** · INFO · reproduced · none · yes · none (verbatim, in section) ·
   section 1 · none needed.
4. **F4 prompt path: an excerpt whose first line exceeds the share is dropped with its pointer** · FOLLOW-UP (borderline,
   see the gate) · reproduced · C4 "cut at a line boundary and keep the pointer" only if a skipped excerpt counts as a
   cut one; the builder's report defines skip ≠ cut and its budget test pins a skipped row with no pointer · yes · 3 of
   217 real human prompts (2 lose the best section, 1 gets nothing); only pc-bridge-lanes 19 and 23 (D9) are that long ·
   `cd V && python3 f4_prompt_pointer.py` (rc 1 now) · when no line fits, emit the label and pointer, or start at the
   next entry that fits; or wrap the two skill lines (outside this boundary).
5. **F5 one heading word carries an unrelated section** · FOLLOW-UP · reproduced (the systemctl prompt → "Repair
   briefs" on "unit") plus replay proxies (54 of 148 injections weak, 23 strong) · none (relevance is unpinned) · yes ·
   prompt-path noise at about 2.2 KB each · `cd V && python3 prompt_dyn.py` (prompt 23) · a second lead word, or a
   higher threshold for one-word leads; check it against `.jev/system1.jsonl` on the day of use.
6. **F6 (the builder's D11) quoted and heredoc text fires command rows** · FOLLOW-UP (known; measured as asked) ·
   reproduced · none · yes · -3.3 % / -4.5 % injected calls; about half of graft, lane-context, ouroboros and
   code-review-graph injections; far more on report-writing work: in this verify lane's own window 9 of 12 injected calls were heredoc text (section 13) ·
   `cd V && python3 replay.py` (the V2/V3 lines) · the builder's owner-aware masking; heredoc bodies as data unless a
   shell reads them.
7. **F7 the command-position scan is quadratic** on long runs with no spaces, many separators and no `/` · FOLLOW-UP ·
   reproduced (in process; 198 KB end to end: 36.5 s) · C5 "keep the latency low" (qualitative) · yes · none on real
   calls (max 14.1 ms of 16,830; live max 14.6 ms) · section 4 snippet (`command_positions("echo " + ";" * 40000)` 2.6 s) ·
   bound the scan (length cap, or no backtracking directory prefix).
8. **F8 a lock held > 0.5 s breaks once-per-window, and the docstring says otherwise** · FOLLOW-UP · reproduced
   (external holder: 37-40 lines twice, 29-36 lost from the marker; and F7's slow call beside a normal one) · C3 ·
   yes · only when a sibling holds the lock > 0.5 s; never seen live or in the replay · `cd V && python3 conc_dyn.py` ·
   on lock timeout inject nothing (fail quiet), and correct system1-context.py:472-473.
9. **F9 a failed marker or cache write leaves `<file>.<pid>.tmp`** · INFO · reproduced (`ulimit -f 0`) · none · yes ·
   one inode per failed call until the 7-day prune · `cd V && python3 hostile.py` · unlink the temp file on error.
10. **F10 the builder's 91 tests survive 7 of 8 mutants** (lock removed; budget in characters, which injects 2,272
    bytes; the path, lower-cased prompt words, or prompt words in the marker; prune removed; unresolved handler removed) ·
    FOLLOW-UP · reproduced · evidence demand 2 (covered in name, weak in fact) · yes (the registered-command tests) · none
    on today's code (sections 2-6 prove it right), a weak gate for regressions ·
    `cd V && python3 mutate.py` · tests for a parallel burst, a multi-byte boundary, a lower-case canary in Write/Edit
    paths and contents and the prompt scanned across every state file, and the unresolved skip through the registered
    command; these 7 mutants are the acceptance bar if a hardening lane runs (contract-gate: the verifier's set).
11. **F11 docs now incomplete** · FOLLOW-UP (coordinator docs; outside the builder's boundary) · reviewed · the NO STUBS
    prose rule · n/a · `docs/HARNESS-PORTS.md:223` "all five project hooks are ported" and `STATUS.md:50`: six hooks
    now, system1 not ported (the builder's report says so; the docs do not); `.jev/system1-off` is named in the
    orchestration skill, not in CLAUDE.md · `grep -n "five project hooks" docs/HARNESS-PORTS.md` · one line each.
12. **F12 a dangling symlink named `system1-off` does not switch it off** · INFO · reproduced · C4 (hypothetical misuse)
    · yes · none in practice · `cd V && python3 ks_secrets.py` · `os.path.lexists`.
13. **F13 SessionStart `fork` resets nothing** · INFO · reproduced · none (the contract names three sources) · yes · a
    fork gets a new session id; like D5 · `cd V && python3 window_dyn.py` · none needed.
14. **F14 the prune removes a live window idle for 7 days** · INFO · reproduced · none · yes · re-injection after a
    week · window_dyn.py · none needed.
15. **F15 a torn marker silences its window until a reset** · INFO · reproduced · C4 (fail quiet by design) · yes ·
    none in practice (atomic replace) · hostile.py · none needed.
16. **F16 one uncompiled regex or one missing skill file silences every row of the call; `re.error` logs as `error`** ·
    INFO · reproduced · C4 (it logs its type) · yes · none (the table test compiles and resolves every row) ·
    hostile.py · catch per row.
17. **F17 skill and table reads use a plain `open()`: a FIFO stalls the call 55 s, the killed call logs nothing, and
    the wrapper says "did not run"** · INFO · reproduced · C4 never blocks: holds (rc 0 at 55.1 s) · yes · hypothetical
    misuse · section 4 · O_NONBLOCK for the reads too.
18. **F18 hook_context.py reads its stdin unbounded** (line 29) · INFO, pre-existing · static · none · n/a · none seen ·
    — · bound it like the hook does.
19. **F19 `--remove` deletes a foreign hook sharing a group with ours, and any hook naming `<repo>/.claude/hooks/`** ·
    INFO, pre-existing (the merge rule predates S1-L1) · reproduced (`--target` scratch) · none · yes · owner hooks in
    the repo's hooks dir would go · section 10 · match our exact commands.
20. **F20 SessionStart: settings.json runs the script, the installer runs `bash` on it** · INFO, pre-existing ·
    reproduced · none · n/a · none · section 10 · none needed.
21. **F21 path rows see repo-relative paths only** (`/tmp` scratch: 209 main + 574 subagent Write/Edit; 18 worktree) ·
    INFO · reproduced (counts) · none · n/a · small · section 7 · none needed.
22. **F22 the tool path reads skill files without the mtime cache** (C5's wording; the builder's D4) · INFO · reproduced
    (code; latency) · C5 literal · yes · none: it measures faster than loading the cache · — · the coordinator records
    D4 as accepted, or amends the wording.
23. **F23 the prompt path would inject on 68 % of human prompts, median 2.2 KB, and has never fired live on one** ·
    INFO · reproduced (replay; live telemetry) · none · n/a · a context cost to watch · replay.py · watch the day-of-use
    telemetry.
24. **F24 delivery when search-intercept blocks the same Bash call (exit 2)** · UNVERIFIED · no blocked call since 16:02Z
    to observe · C1/C3 (the marker records the lines either way) · live harness only · unknown · — · observe one live.
25. **F25 whether a subagent's own compaction sends SessionStart with its `agent_id`** · UNVERIFIED · the reset handles
    it when it does (section 2) · C3 · live harness only · unknown · — · observe one live.
26. **F26 reproduced as claimed** · INFO (positive) · reproduced: the replay to the byte and per row; latency within a
    few ms; 124 passed twice (set 2dc71b948b8b); pyflakes; the separator grep; verbatim on 38 rows and 188 prompts;
    both budgets exact in bytes; every hostile input rc 0, including a read-only `.jev/` bind mount (no output, no files);
    the kill switch; secrets (0 canary hits, strace clean); resets; the lock under a free burst; registration and the
    live file byte-identical; the manifest pins with a negative control; live delivery 15 of 15 on the main thread.

## GATE RECOMMENDATION: MERGE-READY-WITH-FOLLOWUPS

No finding meets the whole blocking predicate; this does not depend on anything I did not reproduce (F24 and F25 are
open, and either one would be a follow-up of its own if it failed). The closest is **F4**: reproduced through the
registered prompt command, in the boundary, with a red discriminator. But it contradicts the frozen C4 only if a skipped
excerpt counts as a cut one, and the builder's report and budget test define it the other way. It also touches 3 of 217
prompts on a path that has not fired live. If the coordinator reads C4 the other way, the reproduction is
`cd V && bash setup_copy.sh && python3 f4_prompt_pointer.py` (rc 1). Follow-ups in order of value: F2 (the rows' text: the
push qualifier, push-delegate-work's head and tail, the NaN rule), F10 (the 7 surviving mutants as the bar), F8 (fail
quiet on lock timeout; fix the docstring), F4, F5 and F6 (noise), F11 (docs), then F1 and F7.

Non-blocking findings: 26 (9 FOLLOW-UP, 15 INFO, 2 UNVERIFIED).
