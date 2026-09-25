# S1-L1 report: the situation-to-skill hook (D-090; design L1 and L3)

Lane: code-implementer (sandbox, Opus 5.5). Started 2026-09-25 15:1xZ. PIN 3c495c9; tree HEAD 25db08e (the brief commit).
Status: DONE (16:1xZ). Build, tests, replay and latency complete; the gate recommendation is not mine.

## 0. Premise re-measurement (verified, 15:2xZ, the sandbox; PIN 3c495c9, tree HEAD 25db08e = PIN + the brief commit)

MATCH on every line of the brief's block, so no CONTRACT-INVALID:

```
$ git show 3c495c9:<file> | sha256sum | cut -c1-16      (and the working tree: identical)
fab9b615481333c8  .claude/hooks/wiki-context.py
5f2ed3707dcf89a7  scripts/hook_context.py
30c4862939017c5c  scripts/install_session_hooks.py
ad7fe12e10a72d51  .claude/settings.json
0dd289beee186a01  .claude/hooks/session-start.sh
$ git diff --name-only 3c495c9 HEAD
tasks/briefs/system1/S1-L1-brief.md
wiki/topics/live-state.md
registrations (event | matcher | command): the five rows of the brief, byte for byte
$ grep -c -i -E 'Load `[a-z-]+` (before|when)' CLAUDE.md
13
$ bash scripts/test_summary.sh tests/test_session_hooks.py tests/test_hooks_worktree.py
pytest-summary: 28 passed in 1.88s
$ bash scripts/pc_suite.sh set-id -- tests/test_session_hooks.py tests/test_hooks_worktree.py
2 files set=0b50704afd94
```

**The brief's question, answered from `scripts/hook_context.py` (46 lines, read whole) and the running binary.**
- `hook_context.py` never reads `tool_name`. Whatever the settings `matcher` sends it, for any of its four events
  (`EVENTS = ("PreToolUse", "PostToolUse", "UserPromptSubmit", "SessionStart")`, line 20), a zero exit with non-blank
  stdout becomes one line `{"hookSpecificOutput": {"hookEventName": <argv[1]>, "additionalContext": <stdout, trailing
  newlines stripped>}}` (lines 40-41). So yes: for EVERY tool the matcher lets through. A non-zero exit passes stdout,
  stderr and the code through unchanged (lines 36-39, so exit 2 still blocks). A usage error, a command that cannot
  start, or the 55 s timeout print one stderr line and exit 0 (lines 25-34).
- UserPromptSubmit is in `EVENTS`, so it is wrapped the same way with `hookEventName: "UserPromptSubmit"`. The running
  binary (`/opt/claude-code/bin/claude`, its zod output schemas) accepts `additionalContext` for both PreToolUse and
  UserPromptSubmit (`hookEventName:R("UserPromptSubmit"),additionalContext:o().optional(),...`). `wiki-context.py` is
  registered unwrapped (plain stdout); the S1A audit counted 48 of its injections, so plain stdout reaches the model for
  that event.
- One limit (inferred from the code, not exercised): a wrapped command that prints its own JSON object is not passed
  through. It is wrapped again as a string. The new hook prints plain text, so this does not apply to it.

**Payload facts read from the running binary (primary source; they shape the marker):** every hook input carries
`session_id`; `agent_id` is "present only when the hook fires from within a subagent ... Absent for the main thread";
SessionStart's `source` is one of `startup`, `resume`, `clear`, `compact`, `fork`. A subagent is its own context
window, so the marker key is (`session_id`, `agent_id` or `main`).

## 1. What was built (verified; final state 16:1xZ)

| file | kind | what |
|---|---|---|
| `.claude/hooks/system1-context.py` | CREATE, 587 lines, sha256 `a3e37aba8adbc014` | One hook, three entries: PreToolUse on Write, Edit and Bash (L1); UserPromptSubmit (L3); `--reset` (called by `session-start.sh`). Plain-text output. |
| `.claude/hooks/system1-situations.json` | CREATE, 627 lines, sha256 `eef9252d0c0c2b9f` | The situation table: 38 rows and the L3 prompt corpus (19 skills). |
| `tests/test_system1_context.py` | CREATE, 484 lines, sha256 `2bd7568e12822e32` | 91 tests through the real registered command lines. |
| `.claude/settings.json` | MODIFY, +8 at 59-66, +9 at 88-96 | A second UserPromptSubmit group, and a PreToolUse group with matcher `Write\|Edit\|Bash`. Both use the guarded form `[ -f …/system1-context.py ] && [ -f …/hook_context.py ] \|\| exit 0; python3 …/hook_context.py <Event> -- python3 …/system1-context.py`. The five existing groups are byte-identical. |
| `scripts/install_session_hooks.py` | MODIFY, docstring 2/6/10/14-16, `our_hooks` 52-55 and 60-63, `main` 134 | The same two groups with absolute paths, the fail-open guard and the wrapper. "five" becomes "six" where it counts today's hooks; the message becomes `installed 6 in`. |
| `.claude/hooks/session-start.sh` | MODIFY, +7 at 12-18 (the reset only) | Before the web-only exit: if `system1-context.py` exists, run it with `--reset`, output discarded, `\|\| true`. |
| `tests/test_session_hooks.py` | MODIFY | Six hooks and seven commands; the fail-open and event-name tests now cover EVERY group, not only the first per event; the fake repo holds `system1-context.py`; group count 6 → 8. |
| `tests/test_session_start_hook.py` | MODIFY, +23 at 91-113 | The real `session-start.sh` resets the marker from its stdin payload. It does so outside the web container, prints nothing, and keeps the marker on `startup` and another session's marker on `compact`. |

How it works (each point measured or read from a primary source this session):
- **Window = (`session_id`, `agent_id` or `main`).** The running binary's hook-input schema says `agent_id` is present only
  inside a subagent. The marker is `.jev/system1-seen/<session>.<agent>.json` (0600), locked with `flock` (0.5 s wait, then
  it goes on without the lock).
- **The dedupe unit is the injected LINE** (a sha1 of skill + line). A row whose lines were all injected is skipped as a
  duplicate. A row cut by the budget delivers its remaining lines on the next matching call in the window (seen live on
  this lane's own calls: `pc_suite.sh` got pc-suite and test-gate, the next call got ops-script).
- **Budget:** rows in table order. Each row is a label `[system1 · <id>] skill <skill>, the governing lines verbatim:`, its
  verbatim lines, then `full details: .claude/skills/<skill>/SKILL.md § <heading>`. The cut is at a line boundary; a cut
  row keeps its pointer; a row whose first line does not fit is skipped (`budget`); `…` marks a gap between
  non-adjacent lines. A prompt injects at most two sections (the second only at ≥ 0.75 of the best score), each at most
  2,048 bytes.
- **Selectors:** a row's `lines` entry is a substring that must name exactly ONE line of its section (the entry from that line
  is taken, continuation lines included) or a `[from, to]` pair. A skill edit that breaks an anchor raises `LookupError`: the
  row is skipped as `unresolved` in telemetry and the table test goes red.
- **Command detection:** a row's `command` regex is matched at shell command positions (the start, after `;`, `&&`, `\|\|`,
  `\|`, `(`, `$(`, a backtick, `then`/`do`/`else`, `nohup`/`setsid`/`exec`/`time`/`sudo`/`env`/`xargs`/`timeout N`, past
  assignments, an interpreter and a directory). So `grep 'git commit' f` and `echo "git push"` stay silent. `commit` and
  `push` need `(?![-\w])` (a first draft matched `git commit-tree`).
- **Cache:** the prompt path reads the corpus through `.jev/system1-cache.json`, keyed on `mtime_ns` and size (parse and
  tokenize 19 skills 21.3 ms, cache load 2.0 ms; medians of 15). The tool path parses the 1-3 files it needs directly.
- **Latency work:** compiling the command-position prefix once instead of into every row's regex, and compiling a row's
  detectors only when its tool applies, took the in-hook no-match cost from 8.2 ms to 2.5 ms (section 6).
- **Robustness:** stdin is read with a bounded 2 s wait (this Bash tool's fd 0 is a socket; session-start.sh's test inherits
  stdin). State files are opened `O_NONBLOCK|O_NOFOLLOW` and must be regular files (the edit-snapshot hook flagged AF-AP-70a
  on the first draft: a FIFO at a marker path would hang a hook that runs on every Bash call). Atomic writes loop on short
  writes (the disk is at 94 %).

## 2. The situation table (verified: every row resolves against the current skills; 38 rows)

Line numbers are those of the skill files in the tree at the end of the lane. Two coordinator skill bakes landed
mid-lane (7cfd8cc, then the coordinator commit "skill bake: env-tool-quirks ... and orchestration", unpushed at harvest; ids as on origin after the coordinator push). The second inserted lines above seven rows,
and every row still resolves by content:

| row | was | now |
|---|---|---|
| pc-suite | 74-77 | 76-79 |
| proof-regen | 65-66 | 67-68 |
| test-vendored-manifest | 78-84 | 80-86 |
| test-proof-status | 61-64 | 63-66 |
| test-gate | 72 | 74 |
| pasted-count | 72 | 74 |
| push-delegate-work | 530-535 | 534-539 |

| # | id | tools | detects (all must match) | skill § section : lines | source |
|---|---|---|---|---|---|
| 1 | `pc-sqlite` | Bash | cmd `pc\.sh\b` + anywhere `\bsqlite3\b` | pc-bridge-lanes § Bridge calls : 30 | CLAUDE.md:350 pc-bridge-lanes: 'a PC-side sqlite ... command' |
| 2 | `pc-podman` | Bash | cmd `pc\.sh\b` + anywhere `\bpodman\b` | pc-bridge-lanes § Bridge calls : 31 | CLAUDE.md:350 pc-bridge-lanes: 'a PC-side ... podman command' |
| 3 | `pc-call` | Bash | cmd `pc\.sh\b` | pc-bridge-lanes § Bridge calls : 28-29 | CLAUDE.md:350 pc-bridge-lanes: 'a `pc.sh` ... call' |
| 4 | `pc-lane` | Bash | cmd `pc_lane\.sh\b\|pc-lane\.sh\b` | pc-bridge-lanes § Launching, re-attaching and sizing PC lanes : 24 | CLAUDE.md:77 pc-bridge-lanes: 'dispatching, re-attaching ... a PC lane'; CLAUDE.md:350 'a `pc_lane.sh` call' |
| 5 | `pc-suite` | Bash | cmd `pc_suite\.sh\b` | env-tool-quirks § Test gates and pasted counts : 76-79 | CLAUDE.md:350 pc-bridge-lanes: 'a `pc_suite.sh` call' (its section points on to env-tool-quirks, which holds the text); CLAUDE.md:304 env-tool-quirks: ops script pc_suite |
| 6 | `ouroboros` | Bash | cmd `ooo_mcp\.py\b\|ouroboros\b` | ouroboros-stdio § Ouroboros through the stdio client : 11-22 | CLAUDE.md:329 ouroboros-stdio: 'any Ouroboros interview round, fan-out submission, resume or seed generation' |
| 7 | `push` | Bash | cmd `git\s+(?:-C\s+\S+\s+)?push(?![-\w])\|push_clean\.sh\b\|push_when_green\.sh\b` | env-tool-quirks § Shell, git, commit-helper and tool quirks : 40-47,50 | CLAUDE.md:348 env-tool-quirks: 'a push' |
| 8 | `push-delegate-work` | Bash | cmd `git\s+(?:-C\s+\S+\s+)?push(?![-\w])\|push_clean\.sh\b\|push_when_green\.sh\b` | orchestration § The ORCHESTRATOR protocol (proven over a full MVP sprint) : 534-539 | CLAUDE.md:144-145 orchestration: 'pushing delegate work' |
| 9 | `stamp` | Write/Edit/Bash | text `\b[0-2]\d:[0-5](?:\d\|x)Z\b` | build-loop § The operative core (CLAUDE.md's index of this skill) : 341 | DESIGN L1 'a stamp in text': the count and stamp rule (CLAUDE.md keeps it; build-loop holds it verbatim) |
| 10 | `commit` | Bash | cmd `git\s+(?:-C\s+\S+\s+)?commit(?![-\w])\|safe_commit\.sh\b` | env-tool-quirks § Shell, git, commit-helper and tool quirks : 38-39 | CLAUDE.md:348 env-tool-quirks: 'a commit' |
| 11 | `commit-increment` | Bash | cmd `git\s+(?:-C\s+\S+\s+)?commit(?![-\w])\|safe_commit\.sh\b` | build-loop § The operative core (CLAUDE.md's index of this skill) : 315-323 | CLAUDE.md:386 build-loop: 'before any code increment, test or commit' |
| 12 | `proof-regen` | Bash | cmd `proof-runner\b\|validate-ledger\b\|ledger-gen\b` | env-tool-quirks § Test gates and pasted counts : 67-68 | CLAUDE.md:348 env-tool-quirks: 'a proof regeneration' |
| 13 | `vendored-manifest-write` | Bash | cmd `vendored_manifest\.py\b` + anywhere `--write\b` | env-tool-quirks § Shell, git, commit-helper and tool quirks : 55 | CLAUDE.md:348 env-tool-quirks: 'a `vendored_manifest.py --write`' |
| 14 | `test-vendored-manifest` | Bash | cmd `pytest\b\|test_summary\.sh\b\|lane_gate\.sh\b\|pc_suite\.sh\b\|relaunch-suite\.sh\b` + anywhere `test_vendored_manifest` | env-tool-quirks § Test gates and pasted counts : 80-86 | CLAUDE.md:348 env-tool-quirks: 'a test gate' (the suite that fills the disk) |
| 15 | `test-proof-status` | Bash | cmd `pytest\b\|test_summary\.sh\b\|lane_gate\.sh\b\|pc_suite\.sh\b\|relaunch-suite\.sh\b` + anywhere `test_proof_status` | env-tool-quirks § Test gates and pasted counts : 63-66 | CLAUDE.md:348 env-tool-quirks: 'a test gate' (the gpg socket-path suite) |
| 16 | `test-gate` | Bash | cmd `pytest\b\|test_summary\.sh\b\|lane_gate\.sh\b\|pc_suite\.sh\b\|relaunch-suite\.sh\b` | env-tool-quirks § Test gates and pasted counts : 74 | CLAUDE.md:348 env-tool-quirks: 'a test gate or pasted count' |
| 17 | `pasted-count` | Write/Edit/Bash | text `\b\d+ (?:passed\|failed\|xfailed\|xpassed\|errors?\|skipped)\b` | env-tool-quirks § Test gates and pasted counts : 74 | CLAUDE.md:348 env-tool-quirks: 'a test gate or pasted count' |
| 18 | `anchor-edit` | Bash | cmd `anchor_edit\.py\b` | env-tool-quirks § The ops scripts : 27-29 | CLAUDE.md:348 env-tool-quirks: 'an anchor edit'; CLAUDE.md:304 'an ops script (... anchor_edit)' |
| 19 | `ops-script` | Bash | cmd `(?:resume-heal\|orient\|relaunch-suite\|why\|verify-planning-repo)\.sh\b\|(?:replay_transcript_edits\|lint_delta)\.py\b\|pc_suite\.sh\b` | env-tool-quirks § The ops scripts : 15-25 | CLAUDE.md:304 env-tool-quirks: 'an ops script (resume-heal, orient, relaunch-suite, pc_suite, why, replay_transcript_edits, lint_delta, verify-planning-repo, anchor_edit)' |
| 20 | `background` | Bash | + anywhere `(?<![&>\|<])&(?![&>])(?=\s\|$)\|(?:^\|[;&\|(\s])(?:nohup\|setsid\|disown)\b` | env-tool-quirks § Shell, git, commit-helper and tool quirks : 51 | CLAUDE.md:348 env-tool-quirks: 'a background job' |
| 21 | `pgrep` | Bash | cmd `p(?:grep\|kill)\b` | env-tool-quirks § Shell, git, commit-helper and tool quirks : 35-37 | CLAUDE.md:348 env-tool-quirks: 'a `pgrep` or `pkill`' |
| 22 | `gitnexus` | Bash | cmd `gitnexus\b\|gn_mcp\.py\b\|run\.cjs\b` | code-intel-trio § GitNexus (tier ladder: native MCP → stdio → CLI; prefer richest alive) : 37-39 | CLAUDE.md:445 code-intel-trio: 'impact analysis' |
| 23 | `codebase-memory` | Bash | cmd `codebase-memory-mcp\b` | code-intel-trio § codebase-memory (binary: /root/.local/bin/codebase-memory-mcp; MCP on stdio or `cli` one-shots) : 49-54 | CLAUDE.md:445 code-intel-trio: 'Phase-1 grounding ... dead-wiring hunt' |
| 24 | `code-review-graph` | Bash | cmd `code-review-graph\b` | code-intel-trio § code-review-graph (venv: /root/venv-crg/bin/code-review-graph) : 64-67 | CLAUDE.md:445 code-intel-trio: 'impact analysis, dead-wiring hunt' |
| 25 | `graft` | Bash | cmd `graft\s+(?:ask\|skeleton\|build\|find)\b` | code-intel-trio § The core reflexes (CLAUDE.md's code-intelligence section) : 189-194,235-236 | CLAUDE.md:445 code-intel-trio: 'any semantic code question' |
| 26 | `lane-context` | Bash | cmd `lane_context\.sh\b` | code-intel-trio § § lane_context — the ONE-COMMAND tool pass (owner escalation 2026-09-07) : 168-180 | CLAUDE.md:445 code-intel-trio: 'Phase-1 grounding' (the pack) |
| 27 | `brief` | Write/Edit | path `^tasks/briefs/.+\.md$` not `(?i)report\|(?:^\|/\|-)pack\.md$\|ledger\|/VENUE-MAP\.md$` | orchestration § CLAUDE-5 PROMPTING & DELEGATION (2026-07-27 — source: Anthropic model docs, primary) : 173-174,179-183,27-32,211-215 | CLAUDE.md:144-145 orchestration: 'before authoring any brief' (and 0l, the owner-rulings check CLAUDE.md:145 names) |
| 28 | `brief-contract` | Write/Edit | path `^tasks/briefs/.+\.md$` not `(?i)report\|(?:^\|/\|-)pack\.md$\|ledger\|/VENUE-MAP\.md$` | contract-gate § The loop (this repo's shape) : 38-50 | CLAUDE.md:116 contract-gate: 'USE for every serious increment' (the contract lives in the brief) |
| 29 | `research-prompt` | Write/Edit | path `^docs/research/prompts/.+\.md$` | deep-work § Feature workflow (for any substantial new subsystem) : 505-507,511-517 | CLAUDE.md:372 deep-work: 'authoring a research prompt' |
| 30 | `live-state` | Write/Edit | path `^wiki/topics/live-state\.md$` | session-continuity § The wiki: per-commit freshness and the continuity spine (CLAUDE.md's onboarding-map entry) : 299-308 | CLAUDE.md:285 session-continuity: 'when updating `wiki/topics/live-state.md`' |
| 31 | `claude-md-gitnexus-block` | Write/Edit | path `^CLAUDE\.md$` text `GitNexus` | code-intel-trio § Superseded by CTX1: the GitNexus block's pre-CTX1 wording (history only) : 253-263 | CLAUDE.md:454 code-intel-trio: 'before editing this block' |
| 32 | `dormant-claim` | Write/Edit | text `\bDORMANT\b` | code-intel-trio § The core reflexes (CLAUDE.md's code-intelligence section) : 235-236 | CLAUDE.md:445 code-intel-trio: 'a ... DORMANT claim' |
| 33 | `test-edit` | Write/Edit | path `^tests/.+\.py$\|(?:^\|/)test_[^/]+\.(?:py\|sh)$\|(?:^\|/)[^/]+_test\.py$` | anti-hollow-green § Anti-hollow-green TACTICS — operational checklist (every gate, oracle, test, increment) : 14-16,31-34 | CLAUDE.md:181 anti-hollow-green: 'designing or reviewing ANY gate/oracle/test/guard' |
| 34 | `test-edit-increment` | Write/Edit | path `^tests/.+\.py$\|(?:^\|/)test_[^/]+\.(?:py\|sh)$\|(?:^\|/)[^/]+_test\.py$` | build-loop § The operative core (CLAUDE.md's index of this skill) : 315-323 | CLAUDE.md:386 build-loop: 'before any code increment, test or commit' |
| 35 | `gate-edit` | Write/Edit | path `^(?:scripts/hooks/\|\.claude/hooks/\|src/agent_factory/\|proofs/schemas/)\|^scripts/[^/]*(?:gate\|lint\|screen\|validate\|ledger\|proof\|push\|commit\|guard)[^/]*$` | deep-work § Phase index (CLAUDE.md's index of this skill) : 465-470 | CLAUDE.md:401 deep-work: 'a gate, security or store spine change' |
| 36 | `gate-edit-tactics` | Write/Edit | path `^(?:scripts/hooks/\|\.claude/hooks/\|src/agent_factory/\|proofs/schemas/)\|^scripts/[^/]*(?:gate\|lint\|screen\|validate\|ledger\|proof\|push\|commit\|guard)[^/]*$` | anti-hollow-green § Anti-hollow-green TACTICS — operational checklist (every gate, oracle, test, increment) : 14-16 | CLAUDE.md:181 anti-hollow-green: 'designing or reviewing ANY gate/oracle/test/guard' |
| 37 | `code-edit` | Write/Edit | path `^(?:proofs\|spikes\|scripts\|src\|tests\|harness-ports\|\.claude/hooks)/.+\.(?:py\|sh\|js\|mjs\|ts\|rs)$\|^scripts/[^/.]+$` | build-loop § The operative core (CLAUDE.md's index of this skill) : 308-314 | CLAUDE.md:379 build-loop: 'before writing code'; CLAUDE.md:386 'before any code increment' |
| 38 | `code-edit-guidelines` | Write/Edit | path `^(?:proofs\|spikes\|scripts\|src\|tests\|harness-ports\|\.claude/hooks)/.+\.(?:py\|sh\|js\|mjs\|ts\|rs)$\|^scripts/[^/.]+$` | build-loop § Behavioral guidelines (Andrej Karpathy skills) : 351-354,356-359 | CLAUDE.md:379 build-loop: 'before writing code (the four behavioral guidelines ...)' |

L3 prompt corpus (19): adversarial-review, anti-hollow-green, bug-echo, build-loop, code-intel-trio, contract-gate, deep-work, empirical-validation, env-tool-quirks, luck, orchestration, ouroboros-stdio, pc-bridge-lanes, premortem-roast, root-cause-debugging, session-continuity, thermo-nuclear-review, trace-the-chain, vendor-first. These are the 15 skills CLAUDE.md names in backticks, plus the 4 that
the text moved out of CLAUDE.md names (vendor-first, bug-echo, thermo-nuclear-review, premortem-roast). The 356 kit-verbatim library
skills are left out as noise for ordinary prompts. The list is data in the table, so the coordinator can widen it.

## 3. Situations the text names that no pattern can detect (no row)

1. CLAUDE.md:77 `pc-bridge-lanes`: "harvesting ... a PC lane, or sizing lanes per route". A harvest has no command of its
   own (it reads a report or a transcript), and sizing is a decision.
2. CLAUDE.md:350 `pc-bridge-lanes`: "a PC-side ... systemctl ... command". It is DETECTABLE (`pc.sh` + `systemctl`), but the
   governing text (the `XDG_RUNTIME_DIR` quirk) is inside pc-bridge-lanes line 23, ONE physical line of 4,800 bytes. That line
   can never fit a 2,048-byte call under a line-boundary cut, so there is no row. The same line holds the `pc_lane.sh` launch
   recipe ("makes its OWN private copy"), so the `pc-lane` row carries only line 24 and the pointer (DISCREPANCY D9).
3. CLAUDE.md:285 `session-continuity`: "answering the retro gate". The gate's feedback arrives as a harness-event prompt
   (`Stop hook feedback`), not as a tool input. The retro's usual edit (live-state.md) has a row.
4. CLAUDE.md:372 `deep-work`: "starting a substantial new subsystem". A judgment.
5. CLAUDE.md:401 `deep-work`: "a code review of a stretch, or any work where a wrong green is expensive". A judgment. The
   "gate, security or store spine change" part has rows (`gate-edit`, `gate-edit-tactics`, by path).
6. CLAUDE.md:409 `build-loop`: "adding a decision path, an event or a span to a component". A decision path is any branch;
   no pattern separates it from other code edits (the `code-edit` rows inject build-loop anyway).
7. CLAUDE.md:413 `session-continuity`: "on EVERY resume from a compaction summary". This is a SessionStart event, not a tool
   input; the hook's SessionStart role is the reset only (the brief).
8. CLAUDE.md:445 `code-intel-trio`: "any semantic code question" (as prose), "Phase-1 grounding" and "a dead-wiring hunt"
   (as intents), "when an MCP server fails to connect". None is a tool input. The instrument calls have rows (graft,
   gitnexus, codebase-memory, code-review-graph, lane-context); a semantic grep is search-intercept's job.
9. CLAUDE.md:348 `env-tool-quirks`: "a worktree-isolated Agent dispatch", and CLAUDE.md:144-145 `orchestration`:
   "dispatching agents". Both are the Agent tool, outside this hook's matcher (Write, Edit, Bash: the brief).
10. CLAUDE.md:181 `anti-hollow-green`: "reviewing" a gate, oracle, test or guard. Reviewing is reading; the edit side has rows.
11. CLAUDE.md:116: trace-the-chain, adversarial-review, root-cause-debugging, empirical-validation, luck. The text gives them
    no situation; they are in the L3 prompt corpus.

## 4. Tests (verified; counts pasted verbatim)

The brief's gate: my test files plus the two named suites, twice.
```
$ bash scripts/test_summary.sh tests/test_system1_context.py tests/test_session_start_hook.py tests/test_session_hooks.py tests/test_hooks_worktree.py
pytest-summary: 124 passed in 13.70s          (run 1, rc 0)
pytest-summary: 124 passed in 13.13s          (run 2, rc 0)
$ bash scripts/pc_suite.sh set-id -- tests/test_system1_context.py tests/test_session_start_hook.py tests/test_session_hooks.py tests/test_hooks_worktree.py
4 files set=2dc71b948b8b
$ bash scripts/test_summary.sh tests/test_session_hooks.py tests/test_hooks_worktree.py      (the premise's pair)
pytest-summary: 28 passed in 2.42s
2 files set=0b50704afd94
$ bash scripts/test_summary.sh tests/test_search_intercept.py tests/test_strip_cbm_hooks.py tests/test_wiki_context_hook.py tests/test_edit_snapshot_ap_screen.py tests/test_no_laya_in_gates.py tests/test_precommit_class_pin.py      (adjacent consumers)
pytest-summary: 432 passed in 50.23s
6 files set=3bf09c95aa44
$ pyflakes .claude/hooks/system1-context.py scripts/install_session_hooks.py tests/test_system1_context.py tests/test_session_hooks.py tests/test_session_start_hook.py
pyflakes rc=0
$ LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>      0 for each of the 8 files written or modified, and for this report
```

Evidence demand 2, mapped to tests (all through the command string `.claude/settings.json` holds, run with `sh -c` and
`CLAUDE_PROJECT_DIR` set; `test_the_installed_commands_reach_the_model_form` runs the absolute-path commands
`install_session_hooks.py` writes). The oracle is the skill file, read by the test: every line between a label and its
pointer must be a whole line of that skill (or `…`), the first line must be the row's own anchor found in its section,
and the pointer's heading must be a heading of the skill.
- every row, matching and not: `test_a_row_injects_its_lines_on_a_match[<38 ids>]`,
  `test_a_row_stays_silent_on_a_near_miss[<38 ids>]` (near misses: `git commit-tree`, `grep -n 'pc_suite.sh' CLAUDE.md`, a
  report path under tasks/briefs, `vendored_manifest.py --check`, `1520Z`, …), and
  `test_every_row_has_a_fixture_and_every_fixture_a_row`.
- the once-per-window rule and its reset: `test_once_per_window_and_the_reset`. It covers the same window, a subagent
  window, another session, and the real SessionStart command with `startup`, `compact`, `resume` and `clear`; `removed`
  goes 0,1,2,2. Also `test_session_start_hook.py::test_a_compaction_resets_the_system1_marker_in_every_environment`.
- both budgets: `test_the_tool_budget_cuts_at_a_line_boundary_and_keeps_the_pointer` (≤ 2,048; ops-script cut and completed
  over three calls, no line repeated, all of it in order); `test_the_prompt_budget` (a cut excerpt ≤ 2,048; two excerpts
  ≤ 4,096; the 0.75 ratio case).
- the kill switch: `test_the_kill_switch` (no output, no stderr, no telemetry; on again = injects).
- the telemetry line: `test_the_telemetry_line` (fields, the window id, keys; a canary in the command and in the prompt
  never reaches the log; 0600).
- an exception: `test_an_exception_injects_nothing_and_logs_its_type` (a directory, then a FIFO, at the marker path: rc 0,
  no output, `error: OSError`, and no hang; the control is the same call, which injects).
- the prompt path: `test_the_prompt_budget`, `test_the_prompt_path_filters_and_never_repeats` (chit-chat and weak
  matches inject nothing, a harness event injects nothing, with its control).
- also: `test_bad_input_never_blocks`, `test_a_stdin_that_never_closes_does_not_hang_the_reset`,
  `test_every_row_resolves_and_its_first_line_fits_a_call_alone`, `test_a_changed_skill_line_is_reported_unresolved_not_injected`,
  `test_the_harness_event_prefixes_are_wiki_contexts` (a drift guard against wiki-context.py's tuple),
  `test_both_events_are_registered_through_the_wrapper`.

**Red-green, by mutation (the tests were written after the code, so red first was proven by mutants, not by a
test-first run).** On a scratch copy (never the shared tree), each mutant applied alone, suite run with `-x`
(`scratchpad/s1l1/mutate.py`; final code):
```
('dedupe off', 'KILLED', ['test_a_row_injects_its_lines_on_a_match[brief-contract]'], '1 failed, 5 passed in 0.51s')
('marker never written', 'KILLED', ['test_a_row_injects_its_lines_on_a_match[brief-contract]'], '1 failed, 5 passed in 0.50s')
('budget ignored', 'KILLED', ['test_the_tool_budget_cuts_at_a_line_boundary_and_keeps_the_pointer'], '1 failed, 79 passed in 6.07s')
('prompt budget ignored', 'KILLED', ['test_the_prompt_budget'], '1 failed, 80 passed in 6.66s')
('pointer dropped on a cut', 'KILLED', ['test_a_row_injects_its_lines_on_a_match[pc-podman]'], '1 failed, 25 passed in 1.74s')
('kill switch removed', 'KILLED', ['test_the_kill_switch'], '1 failed, 82 passed in 7.24s')
('telemetry leaks the input', 'KILLED', ['test_the_telemetry_line'], '1 failed, 83 passed in 7.61s')
('telemetry line dropped', 'KILLED', ['test_a_row_injects_its_lines_on_a_match[anchor-edit]'], '1 failed, 2 passed in 0.17s')
('marker error swallowed', 'KILLED', ['test_an_exception_injects_nothing_and_logs_its_type'], '1 failed, 84 passed in 8.03s')
('FIFO opened blocking', 'KILLED', ['test_an_exception_injects_nothing_and_logs_its_type'], '1 failed, 84 passed in 37.87s')
('compact not reset', 'KILLED', ['test_once_per_window_and_the_reset'], '1 failed, 78 passed in 5.48s')
('resume resets every session', 'KILLED', ['test_once_per_window_and_the_reset'], '1 failed, 78 passed in 5.87s')
('subagent shares the main window', 'KILLED', ['test_once_per_window_and_the_reset'], '1 failed, 78 passed in 5.41s')
('stdin read unbounded', 'KILLED', ['test_a_stdin_that_never_closes_does_not_hang_the_reset'], '1 failed, 86 passed in 23.99s')
('lines not verbatim', 'KILLED', ['test_a_row_injects_its_lines_on_a_match[brief]'], '1 failed, 4 passed in 0.31s')
('harness events injected', 'KILLED', ['test_the_prompt_path_filters_and_never_repeats'], '1 failed, 81 passed in 7.07s')
('no prompt threshold', 'KILLED', ['test_the_prompt_path_filters_and_never_repeats'], '1 failed, 81 passed in 7.13s')
('second excerpt always', 'KILLED', ['test_the_prompt_budget'], '1 failed, 80 passed in 6.38s')
('commit regex loosened', 'KILLED', ['test_a_row_stays_silent_on_a_near_miss[commit]'], '1 failed, 49 passed in 3.23s')
('command anywhere, not at a command position', 'KILLED', ['test_a_row_stays_silent_on_a_near_miss[anchor-edit]'], '1 failed, 40 passed in 2.83s')
('positions at the separator, not the command word', 'KILLED', ['test_a_row_injects_its_lines_on_a_match[anchor-edit]'], '1 failed, 2 passed in 0.18s')
('brief row matches reports', 'KILLED', ['test_a_row_stays_silent_on_a_near_miss[brief]'], '1 failed, 42 passed in 2.97s')
('path detector ignored', 'KILLED', ['test_a_row_injects_its_lines_on_a_match[code-edit]'], '1 failed, 7 passed in 0.84s')
```
That is 23 of 23 killed. Two earlier survivors each got a test before this run: "no prompt threshold" (a weak heading
match now must inject nothing) and "second excerpt always" (the ratio case). A fourth set of three mutants on the
session-start and installer extensions (`mutate2.py`) was also 3 of 3 KILLED: "reset block removed from session-start.sh",
"system1 registered without the wrapper guard", "system1 prompt group dropped".

NOT run: `tests/test_vendored_manifest.py` (each test copies about 75 MB of vendored inputs, and the disk is at 94 %; its
first-party pins are known to go red until the coordinator regenerates, D8).

## 5. Replay over this session's main transcript (verified; counts only)

`scratchpad/s1l1/replay.py`, in process (`plan_tool`, the function `main()` calls), over the Write, Edit and Bash
`tool_use` inputs of `/root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl`. It prints no
transcript text and stores none. Variant A splits windows at every `compact_boundary`. Variant B also applies the
brief's reset at every recorded `SessionStart:resume` hook run. The span covers days when the table did not exist, so
this is what TODAY's table would have injected, not a past event.
```
transcript span (first..last Write/Edit/Bash call): 2026-09-02T21:10:21.992Z .. 2026-09-25T16:00:25.300Z
windows: 130 (compact_boundary records: 129); recorded SessionStart:resume runs: 9
calls: {'Bash': 15488, 'Write': 537, 'Edit': 659} | calls that received an injection: {'Bash': 1336, 'Write': 142, 'Edit': 120} | total 1598 of 16684
injected bytes, variant A (windows only): 2043712; variant B (+ resume resets): 2093622
bytes per injected call: median 1275, max 2046
bytes per window (A, 130 windows): median 16672, p90 20427, max 25680, windows with none 2
Write/Edit/Bash calls per window: median 131, max 310

per situation row (matched / injected / cut / skipped duplicate / skipped budget):
  pc-sqlite                     224     50     0    174      0
  pc-podman                     131     28     0    103      0
  pc-call                      2278    117     6   2155      6
  pc-lane                       593     72     0    519      2
  pc-suite                      367     66     0    301      0
  ouroboros                      63      6     1     57      0
  push                          913    127     4    785      1
  push-delegate-work            913    224   120    684      5
  stamp                        1754    102     0   1645      7
  commit                       1362    125     0   1224     13
  commit-increment             1362    122     8   1223     17
  proof-regen                   262     49     0    208      5
  vendored-manifest-write        76     33     0     43      0
  test-vendored-manifest         57     22     1     35      0
  test-proof-status              45     18     0     27      0
  test-gate                    1166     75     0   1076     15
  pasted-count                 1106     43     0   1032     31
  anchor-edit                   577     74    11    501      2
  ops-script                    503     97    12    377     29
  background                    566     99     0    455     12
  pgrep                         567    102    11    461      4
  gitnexus                      209     64     0    139      6
  codebase-memory                26      6     0     17      3
  code-review-graph              19      6     0     10      3
  graft                          84     38     6     42      4
  lane-context                   93     33     7     52      8
  brief                         204     61    12    143      0
  brief-contract                204     50    11    104     50
  research-prompt                 1      1     0      0      0
  live-state                     10      3     0      7      0
  claude-md-gitnexus-block        1      1     0      0      0
  dormant-claim                   2      2     0      0      0
  test-edit                     191     49     0    142      0
  test-edit-increment           191     33    20    157      1
  gate-edit                      64     19     0     45      0
  gate-edit-tactics              64      9     0     55      0
  code-edit                     382     60     1    314      8
  code-edit-guidelines          382     70    17    294     18

calls that received each skill section (A):
     486  env-tool-quirks § Shell, git, commit-helper and tool quirks
     317  build-loop § The operative core (CLAUDE.md's index of this skill)
     273  env-tool-quirks § Test gates and pasted counts
     224  orchestration § The ORCHESTRATOR protocol (proven over a full MVP sprint)
     195  pc-bridge-lanes § Bridge calls
     171  env-tool-quirks § The ops scripts
      72  pc-bridge-lanes § Launching, re-attaching and sizing PC lanes
      70  build-loop § Behavioral guidelines (Andrej Karpathy skills)
      64  code-intel-trio § GitNexus (tier ladder: native MCP → stdio → CLI; prefer richest alive)
      61  orchestration § CLAUDE-5 PROMPTING & DELEGATION (2026-07-27 — source: Anthropic model docs, primary)
      58  anti-hollow-green § Anti-hollow-green TACTICS — operational checklist (every gate, oracle, test, increment)
      50  contract-gate § The loop (this repo's shape)
      40  code-intel-trio § The core reflexes (CLAUDE.md's code-intelligence section)
      33  code-intel-trio § § lane_context — the ONE-COMMAND tool pass (owner escalation 2026-09-07)
      19  deep-work § Phase index (CLAUDE.md's index of this skill)
       6  code-intel-trio § codebase-memory (binary: /root/.local/bin/codebase-memory-mcp; MCP on stdio or `cli` one-shots)
       6  ouroboros-stdio § Ouroboros through the stdio client
       6  code-intel-trio § code-review-graph (venv: /root/venv-crg/bin/code-review-graph)
       3  session-continuity § The wiki: per-commit freshness and the continuity spine (CLAUDE.md's onboarding-map entry)
       1  code-intel-trio § Superseded by CTX1: the GitNexus block's pre-CTX1 wording (history only)
       1  deep-work § Feature workflow (for any substantial new subsystem)
```
AF-AP-204 checked: this session id also wrote `/root/.claude/projects/-home-user-agent-factory/bdab799a-….jsonl` (3.1 MB).
It holds 53 assistant records and no `tool_use` at all, so there are 0 calls to replay there; the file above is the whole
replay.

Reading: 1,598 of 16,684 calls (9.6 %) would have received text; the median context window gets 16,672 bytes (about
4k tokens). Five rows fired 1-3 times over 23 days (research-prompt, live-state, claude-md-gitnexus-block, dormant-claim;
ouroboros 6). `push-delegate-work` is cut 120 times because it follows the 1.5 KB `push` row, and completes on the next
push. `brief-contract` loses the budget to `brief` 50 times and arrives on the next brief edit.

## 6. Latency per event (verified; `scratchpad/s1l1/latency.py`, 20 runs each unless noted)

Wall = `sh -c <the registered command>` end to end (sh, `hook_context.py`, then the hook). "Hook-internal" = the hook's own
`ms` telemetry field.
```
python3 3.11.15 | 20 runs each | wall = sh -c <registered command> end to end (sh + hook_context.py + the hook)
(reference: one bare python3 start 14.5 ms)
reference: hook_context.py wrapping `true`           wall median   28.2 ms  p90   30.8 ms  hook-internal median     - ms  out>0 0/20
PreToolUse Bash, no row matches (ls -la)             wall median   58.3 ms  p90   63.2 ms  hook-internal median   2.5 ms  out>0 0/20
PreToolUse Bash, 2 rows inject (git commit), fresh window wall median   61.4 ms  p90   67.6 ms  hook-internal median   5.3 ms  out>0 20/20
PreToolUse Bash, same window again (duplicate, no output) wall median   59.1 ms  p90   69.1 ms  hook-internal median   5.0 ms  out>0 1/20
PreToolUse Edit of a code file, fresh window         wall median   61.5 ms  p90   66.0 ms  hook-internal median   4.4 ms  out>0 20/20
UserPromptSubmit, cold cache (first prompt builds it) wall median   91.9 ms  p90   91.9 ms  hook-internal median  33.7 ms  out>0 1/1
UserPromptSubmit, warm cache, 2 excerpts inject      wall median   66.5 ms  p90   72.5 ms  hook-internal median  10.6 ms  out>0 20/20
UserPromptSubmit, warm cache, nothing scores         wall median   63.9 ms  p90   70.8 ms  hook-internal median   6.0 ms  out>0 0/20
SessionStart: session-start.sh with the reset (compact), non-web wall median   35.3 ms  p90   43.7 ms  hook-internal median   0.8 ms  out>0 0/20
kill switch on: PreToolUse Bash (git commit)         wall median   57.4 ms  p90   68.0 ms  hook-internal median     - ms  out>0 0/20
```
The floor is two Python starts (hook_context.py and the hook): the kill-switch path does no work and costs 57.4 ms. The
hook's own work is 2.5-5.3 ms on a tool call and 6.0-10.6 ms on a prompt with a warm cache. Before the compile change the
same no-match call measured 77.9 ms wall and 8.2 ms internal. In the harness this hook runs in parallel with
search-intercept on Bash calls.

## 7. NOT done (first-class)

- L2, L4, L5 and L6 of the design are not in this lane.
- The coordinator's commit work, outside my boundary: `python3 scripts/vendored_manifest.py --write` (move plugin output
  under `.claude/` aside first, task #232), and the first-party pins in `tests/test_vendored_manifest.py` (D8).
- Harness ports: the Codex and Hermes adapters and the `.agents/` mirrors do not carry system1. It is a Claude Code hook
  only (not in the boundary).
- Not verified live: the UserPromptSubmit path (no prompt arrived after it went live; tested through the registered
  command only). Also: whether a subagent's own compaction fires SessionStart with its `agent_id`; if it does not, a
  compacted subagent keeps its marker. And whether a PreToolUse `additionalContext` is delivered when a sibling hook
  (search-intercept) blocks the same Bash call with exit 2; the marker records the lines as injected either way.
- The live `/home/user/.claude/settings.json`: I did not touch it and did not flip the kill switch (D1).
- Ledger, wiki and incident-log entries (not in the boundary): the setup.sh deploy hazard (D1) is a registry candidate.
- The scratch tools are not committed: `gen_table.py` (regenerates the table JSON from Python with raw-string regexes),
  `replay.py`, `latency.py`, `mutate.py`, `mutate2.py`, `check_rows.py`, `probe.py`, `probe_prompt.py`, with their outputs.

## 8. DISCREPANCIES (loud)

- **D1. The hook went LIVE in the whole session before its gate, through the repo's own machinery; not an action of
  mine.**
  - The chain: SessionStart `compact` at 16:02:08Z (my reset line ran; `removed: 0`) → `session-start.sh` → `setup.sh`
    → `install_session_hooks.py` from the WORKING TREE → `/tmp/agent-factory-setup.log:75` "session hooks: installed 6
    in /home/user/.claude/settings.json (live from the next tool call)"; the settings mtime is 16:02:27.33Z.
  - Observed live since then: this lane's own Bash and Edit calls got `[system1 · …]` injections with the right
    once-per-window and budget behaviour, and `.jev/system1.jsonl` keys this subagent as
    `bdab799a-dc80-5933-9c9e-c80f206f9a17.a45727e3e6c9672f7` and the main thread as `….main`.
  - The coordinator's 843b721 already notes it ("S1-L1 hook already firing on the coordinator calls before its gate").
  - The general hazard, not fixed (outside the boundary): setup.sh installs hooks from the working tree at every session
    start, so any lane's uncommitted hook or installer change deploys itself at the next compaction.
  - Undo options for the coordinator: `touch /home/user/agent-factory/.jev/system1-off` silences both events (the reset
    still runs); or `python3 scripts/install_session_hooks.py --remove`, then re-install from the reviewed commit.
- **D2. "You are the only lane in this tree" stopped being true.** INSTALL1 (brief 77ada56, task #274) was dispatched
  mid-lane; `tasks/briefs/system1/INSTALL1-report.md` appeared at 16:05:46Z. Its report names `scripts/setup.sh` and
  `scripts/slopo_embed_server.py`: no overlap with my boundary. The `.gitignore` change in the tree (+8 lines, slopo
  entries, 16:14:47Z) is INSTALL1's, not mine. HEAD moved from 25db08e to the coordinator skill-bake commit (unpushed at harvest) in seven coordinator
  commits, and a push rewrote the range (the S1-L1 brief commit is now 25db08e). Two of them rebaked skills my table reads
  (env-tool-quirks, orchestration); all 38 rows still resolve, and seven moved by a few lines (section 2).
- **D3. Interpretation of "a section already injected is not injected again".** I dedupe injected LINES, not whole
  sections. A section is never repeated, but another part of it can still arrive (a cut row's remainder, or another row
  keyed to other lines of the same section). Section-level keys would silently drop rows that share a section: `commit`
  and `push` both live in env-tool-quirks § Shell, git, commit-helper and tool quirks.
- **D4. The mtime cache serves the prompt path only.** The tool path parses its 1-3 skill files directly (under 3 ms),
  which is cheaper than loading the 254 KB cache (section 1).
- **D5. The resume reset (the brief's rule) may re-inject text still in context.** A resume reloads the transcript, so
  earlier injections are probably still in the model's context (inferred). Replay variant B costs +49,910 bytes (+2.4 %)
  over the 9 recorded resumes.
- **D6. Additions beyond the literal contract:**
  - a one-line label before each row;
  - `…` between non-adjacent lines of a row;
  - the reset also prunes markers older than 7 days;
  - `system1.jsonl` moves to `system1.jsonl.1` at 4 MB;
  - the reset runs even while `system1-off` exists, so no marker outlives its window;
  - the telemetry `window` field holds the full session and agent id (not text; the ids are needed for correlation).
- **D7. Sources beyond the 13-line grep.** The brief's grep counts 13 "Load `x` before/when" lines. CTX1's section 6
  table has 16 rows plus 3 wrapped "skill `x` — load it" pointers. The rows derive from all of those, from CLAUDE.md:116
  (contract-gate), from :145 (the owner-rulings check, orchestration 0l), and from the design's L1 list ("a stamp in
  text").
- **D8. The vendored manifest check fails until the coordinator regenerates.** `python3 scripts/vendored_manifest.py
  --check` gives FAIL, "line 20", the `.claude/ (kit-adapted)` row: settings.json and session-start.sh are kit-adapted.
  The two new hook files will class `first-party` (the regenerator's rule for paths absent from the kit index, as for
  search-intercept.py). `tests/test_vendored_manifest.py` pins `first-party == 16` at :388 and :455, and `== 17` at :568;
  those need 18, 18 and 19.
- **D9. A skill-side limit.** pc-bridge-lanes lines 19 (4,667 bytes) and 23 (4,800 bytes) are single lines over the
  per-call budget. They hold the `pc_lane.sh` launch recipe, the systemctl `XDG_RUNTIME_DIR` quirk and the local-route
  concurrency rules. Wrapping those two lines in the skill (not my boundary) would let the `pc-lane` row carry the launch
  recipe and would allow a systemctl row.
- **D10. A false-positive tell.** The edit-snapshot hook raised an AF-AP-59 tell on the test file: `ps -eo pid,args |
  head` is a near-miss fixture string, never executed.
- **D11. Command detection does not parse quoting or heredocs; two live false positives on this lane's own calls.**
  - `pgrep` fired on `grep -E '…|pgrep|…'`: the `|` inside single quotes reads as a pipe.
  - `pc-call` fired on a `cat > f <<'EOF'` whose Python body holds a backtick-quoted `bash scripts/pc.sh` in a comment.
  - Measured A/B, blanking quoted spans before finding command positions (`quote_ab.py`, `quote_class.py`,
    `replay_masked.py`): command-detector matches fall from 18,414 to 15,861. Of the dropped matches, 328 sit inside a
    quote owned by a nested shell (`pc.sh '…'`, `bash -c`, `ssh`); masking would LOSE those real commands, such as a
    PC-side `pgrep` where the quirk applies. 405 are data arguments (grep, sed, echo, git -m, python -c) and 1,426 are
    unclassified.
  - With once-per-window dedupe the injected total moves only from 1,598 to 1,558 (-2.5 %), and bytes from 2,043,712 to
    2,003,210. The masked replay ran on a transcript 46 calls and one compaction longer (the coordinator is active).
  - Decision: the matcher is unchanged. Owner-aware masking (keep quotes owned by `pc.sh`, `bash -c`, `sh -c`, `ssh`,
    `eval`; blank the rest, and treat heredoc bodies as data) is a candidate improvement, NOT built.

## 9. Self-attack: the three likeliest ways this is wrong

1. **Noise the agent learns to ignore.** A row can fire where its rule does not bite: a stamp pasted correctly from
   `date -u`, a count pasted from test_summary, a `&` inside quotes, a one-off pytest, or a command word inside a quoted
   argument or a heredoc body (two seen live, D11). Ruled out as far as a test can: every row has a near miss; the replay
   puts text on 9.6 % of calls at a 16.7 KB median per window; each line arrives at most once per window, so a false
   positive mostly moves an injection earlier (quote masking would change the total by only 2.5 %, D11). NOT ruled out:
   whether the agent reads it. That is the design's day-of-use measurement (`.jev/system1.jsonl` has the data).
2. **The wrong context window in the real harness.** Ruled out live: the telemetry keyed this subagent's calls to its
   `agent_id` window and the main thread's to `main`, and the compact reset ran live at 16:02:08Z. NOT ruled out: a
   subagent's own compaction (section 7).
3. **Skill drift that breaks rows silently.** Ruled out: `resolve()` raises when an anchor is missing or doubled; the
   runtime then logs `unresolved` and injects nothing for that row; `test_every_row_resolves…` goes red on the next run.
   Two skill bakes landed mid-lane; all 38 rows still resolve, and seven only moved by a few lines.

## 10. Evidence tiers

- Verified (this session, primary):
  - the premise block; the hook_context.py reading and the binary's schemas;
  - the tests, twice, with set ids; the 23 + 3 mutants;
  - the replay counts; the latency;
  - the live injection on this lane's calls; the live install chain (setup log line, settings mtime, telemetry).
- Inferred:
  - that a resume keeps earlier injections in context (D5);
  - that the 16:02:08Z SessionStart was the main thread's compaction (the reset record says `source: compact`; the
    coordinator's next commit lands after it);
  - hook_context.py's JSON double-wrap limit (section 0).
- Assumed: none load-bearing. The subagent-compaction and blocked-sibling cases are listed as NOT verified.

Vendored-manifest paths: NEW `.claude/hooks/system1-context.py`, `.claude/hooks/system1-situations.json` (first-party);
CHANGED `.claude/settings.json`, `.claude/hooks/session-start.sh` (kit-adapted).
