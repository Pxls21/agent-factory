# K2: a context pack pops up when a file is touched (P1) and packs cover every file (P2) (task #353, D-106)

Written 2026-09-29 from 04:0xZ (clock read at 04:06:10Z) by the coordinator. Lane: sandbox `code-implementer`
(Opus 5.5). The design is settled here; build it, do not redesign it. Where reality disagrees with this brief, stop
and report CONTRACT-INVALID with the measurement.

## The owner's words (D-106, 2026-09-29 00:51:42Z; voice-typed, quoted where clear)

"have Jev focus on enriching the compaction message ... so that we lose less data. Maybe it organizes tasks ... and
create context packs for each one or something. That way, whenever we're working on a specific file or something, it
will just pop up the relevant context. You know what I'm saying? Create like a map. Each file, each whatever, has its
own built-in like ... context pack". The plan: `docs/research/findings/jev-trim/D105-DESIGN-v1.md` §10.3 (READ), items
P1 and P2; this lane is K2 of §10.4. Jev is not in this lane: the fixed rules come first, and Jev replaces them only
after it beats them on the replay (D-106).

## What exists (READ; do not rebuild)

- `.claude/hooks/system1-context.py` (READ, never modified): the System-1 hook. PreToolUse on Write, Edit and Bash
  injects skill lines once per context window. Its parts you reuse by importing the file with `importlib` (its name
  has a hyphen): `shell_code` and `command_positions` (the shell parser: quoted data and heredoc bodies are masked, so
  only real command words count), `window_id` (session id plus agent id), `WindowLock` (the per-window flock),
  `open_regular` (O_NOFOLLOW opens), `read_stdin`, and the semantics of `reset` (a compact forgets the window; a resume
  or a clear forgets the session's windows). Copying them instead of importing them is out.
- `scripts/codemap.py` (L2a, task #284; MODIFY only to add a file-level reader, see item 3): one JSON pack per code
  file under `.jev/codemap/<path>.json`, built after each commit by `scripts/hooks/post-commit`; `edit_context(file_path,
  old_string)` and `lookup(path, line, end_line)` read a pack in well under a millisecond. For an Edit of `def cmd_run(`
  in `scripts/stack.py` its `demo` printed a 603-byte entry (premise below).
- `scripts/hook_context.py` (READ): the wrapper every injecting hook runs through. It stamps the output
  `[S1 <id> <source>]` (the source is the script's name, here `filepacks`) and adds the score request, so each pack
  injection is scored like any System-1 injection (task #295).
- `scripts/hooks/post-commit` (MODIFY, item 5): its code-map refresh section is the model for yours.
- The installed tools, checked at authoring (orchestration 0l): the enabled plugins are `aegis`, `fast-jev-output` and
  `honey`. Aegis's `CONTEXT-MAP.md` and `CONTEXT.md` are a glossary the model reads on its own (`wiki/CONTEXT.md` is
  one), not a per-file injector. `fast-jev-output` is jev-pruner's Bash-output pruner (a `tool.call` function hook that
  trims output over 10,000 tokens). Neither puts a file's context in front of the model when the file is touched, so
  this lane duplicates neither.

## Measured at authoring (the design reads off these; the probe is in the premise)

`tasks/briefs/jev-trim/k2_authoring_probe.py` (READ) over the main transcript up to a byte cap (141 context windows):

- The main loop touches few files through Read, Edit or Write (median 5 per window) and many through Bash reader
  commands (median 32, p90 58, max 93). 83.4% of the files it touches in a window are touched only through Bash. So
  Read, Edit and Write alone would miss most of the owner's "whenever we're working on a specific file": the Bash
  readers are in scope.
- A reader call names 1 file at the median, 3 at p90, 23 at most.
- Most code files are named nowhere in the ledger-plane documents (none in the ledger for 79%, none in the incident log
  for 85%), and a few are named often (29 ledger lines and 30 incident-log lines for `scripts/pc_lane.sh`). Ledger lines
  average about 745 bytes. So a pack keeps the newest few mentions per source, each cut to a snippet.

## Boundary

- CREATE: `scripts/filepacks.py` (the builder, the reader, the hook and the replay), `tests/test_filepacks.py`.
- MODIFY: `scripts/codemap.py` (a file-level reader only, if `lookup` cannot give one), `scripts/hooks/post-commit`
  (item 5), `tests/test_codemap.py` (only for the new reader).
- READ: everything named above; `tests/test_system1_context.py` (its payload fixtures and window tests are the model
  for yours); `docs/research/findings/jev-trim/D105-DESIGN-v1.md`.
- NOT yours: `.claude/settings.json`, `scripts/install_session_hooks.py`, `tests/test_session_hooks.py`, anything under
  `.claude/`. Registering the hook is the coordinator's landing step, after the LS-B9 verifier finishes with the
  installer; your report gives the exact entries (item 8). The Read-narrowing hook (task #340), task packs (P3), the
  summarizer's instructions (P4), the compaction moment (P5) and Jev are other increments.

## Items (each with a test and a named mutant the test kills; a real run pasted where it applies)

1. **Premise.** Re-run the PREMISE block below. On a difference other than the ones it lists as expected, stop and
   report CONTRACT-INVALID.
2. **P2, the builder: `filepacks.py build`.** Resolve HEAD once (`git rev-parse --verify HEAD^{commit}`) and thread that
   SHA to every read (AF-AP-175). The tracked files are `git ls-tree -r --name-only <sha>`. One pass over each source
   (never one search per file): find the path tokens, keep those that are tracked files, matched on a whole-path
   boundary (`scripts/stack.py` must not match inside `scripts/stack.py.json` or `x/scripts/stack.py`). The sources,
   exactly:
   - the ledger `todo/BUILD-TASKLIST.md`, the decision log `docs/08_DECISION_LOG.md`, the incident log
     `docs/INCIDENT-LOG.md`;
   - the skills `.claude/skills/<name>/SKILL.md` for these nine names: env-tool-quirks, pc-bridge-lanes, orchestration,
     build-loop, deep-work, anti-hollow-green, session-continuity, code-intel-trio, ouroboros-stdio;
   - the briefs and reports `tasks/briefs/**/*.md` (a mention is the brief's path; newest first by its last commit);
   - the commit subjects of the last 400 commits, from ONE `git log --name-only` call (the newest 3 per file).
   Per mention keep: the source, the line number, the registry id when the line is a registry row (`D-NNN`,
   `AF-AP-NNN`), the ledger line's bold headline (at most 160 characters), and a snippet of at most 240 characters
   around the first mention in the line. Keep the newest 3 per source (the highest line numbers), the newest 3 briefs,
   the newest 3 commits. Write one pack per file that has anything: `.jev/filepacks/<path>.json`, atomically (temp file
   and rename); remove a pack whose file has nothing any more; write `.jev/filepacks/BUILD.json` (schema, the SHA, the
   file count, the milliseconds). Paste the build time of two runs on this tree.
3. **The reader: `entry(rel, tool_input, budget)`.** For a code file with a code-map pack, its code part comes first:
   `codemap.edit_context` for an Edit; `codemap.lookup` over the range for a Read with `offset` and `limit`; otherwise a
   file-level entry (the symbol count and the first few symbols with their spans, the covering tests, the registry
   rows), which you add to `codemap.py` as a reader if `lookup` cannot give it. Then the P2 lines. Cut at a line
   boundary, never mid-line, within the budget. Measure it in process over at least 200 recorded payloads: paste p50
   and p95 (the aim is p95 under 5 ms).
4. **P1, the hook: `filepacks.py hook` (PreToolUse) and `filepacks.py hook --reset` (SessionStart).**
   - Triggers: Read, Edit and Write of a tracked file inside the repo root; Bash, the files named as arguments of a
     reader command word at a command position. The readers, exactly: cat, head, tail, sed, awk, grep, egrep, rg, less,
     more, nl, wc, diff, cmp. Use the System-1 parser, so `echo "cat scripts/x.py"`, a heredoc body naming a file and
     `git add scripts/x.py` inject nothing.
   - Once per window: the seen keys are `file:<rel>` (Read, Write, Bash) and `sym:<rel>:<symbol>` (Edit), kept in
     `.jev/filepacks-seen/<window id>.json` under a `WindowLock`. The reset has the System-1 semantics.
   - Budgets: 1200 bytes per file (PACK_BUDGET), at most 2 files per call (the first named), at most 64 files per
     window (PACK_WINDOW_MAX; the probe's p90 is 60).
   - Off switch: the file `.jev/filepacks-off` (a dangling link counts, as `system1-off` does).
   - Fail quiet: any error gives empty stdout and exit 0, and one record in `.jev/filepacks.jsonl` (the System-1 log's
     record shape: event, tool, tool_use_id, injected with key, bytes and sha, skipped with why, bytes, window, t, ms).
   - The boundary: only tracked files. A path outside the root, a path with `..`, an untracked file, or a pack path that
     is a symlink gives nothing.
5. **The post-commit refresh.** `scripts/hooks/post-commit` starts `filepacks.py build` in the background, niced, one at
   a time (a blocking flock, as the code-map refresh), with one line per commit in its log; it never blocks or fails
   the commit.
6. **The dry run: `filepacks.py replay --transcript PATH --bytes N`.** Replay the main loop's recorded tool calls through
   the hook's planner with a temporary state directory (never the live `.jev/filepacks-seen`), splitting windows at the
   compaction boundaries. Read only compaction boundaries and `tool_use` inputs; print only counts, bytes and file
   paths, never other record content. Print per window the injections and bytes, then the median, p90 and max. Paste it
   for the premise's cap.
7. **Tests** (the project's rule 14: normal behavior, failure behavior and the security boundary), each killing a named
   mutant, and a mutation summary on your final bytes:
   - normal: an Edit injects its symbol's entry once per window; a second Edit of the same symbol injects nothing and
     one of another symbol does; a Read with `offset` and `limit` shows the symbols in range; `sed -n 1,40p <file>`
     injects; a compact reset re-arms; a tracked document gets its P2 lines only;
   - failure: a corrupt pack gives nothing for that file and a log record; a missing `.jev` gives empty stdout and exit
     0; a lock held past its wait gives nothing and a log record; over budget, the cut falls on a line boundary; empty
     or missing fields (no `file_path`, an empty command, a `tool_input` that is not an object, empty stdin) give
     nothing; a P2 pack built at an older commit is still read, and the code part keeps the code map's own freshness
     mark (a stale code pack says so, never passes as fresh);
   - security boundary: `/etc/passwd`, `../x`, an untracked file in a temp repo and a symlinked pack path give nothing;
     the data words above give nothing;
   - the latency through the real wrapper (`python3 scripts/hook_context.py PreToolUse -- python3
     scripts/filepacks.py hook`), p50 and p95 over recorded payloads, pasted.
8. **Gates**, each twice: every test that names one of your paths (`python3 scripts/stack.py gate paths=<your paths>
   mode=plan` lists them), plus `tests/test_system1_context.py` and `tests/test_codemap.py`, in a clean detached
   worktree, with `--basetemp` as a pytest ARGUMENT outside any work tree (never `PYTEST_ADDOPTS`). Counts pasted from
   `scripts/test_summary.sh` with the set id from `bash scripts/pc_suite.sh set-id -- <files>`.

## Report

Return the whole report as your final message (not a summary): the premise re-run; files with line counts and sha256;
per item what you did with its pasted evidence; the gates; the mutants; the registration the coordinator adds at
landing, written out in both spellings (the repo's `.claude/settings.json` and `scripts/install_session_hooks.py`: a
PreToolUse group for `Read|Edit|Write|Bash` through `scripts/hook_context.py`, and the SessionStart reset); NOT done,
first-class; a DISCREPANCIES list; and your self-attack.

Standing rules: no git write in the shared tree (the coordinator commits); no outward action, no PC bridge, no
subagent; never read a secret file (`.pc-bridge.env`, any `*.env`, any key file), and build test secrets as fake strings
at run time; never run `scripts/install_session_hooks.py` and never touch `/home/user/.claude/settings.json`; a long
gate in ONE foreground call; stamps from `date -u`; cite commits by origin id or subject, never a local id; a server or
background job you start is yours to stop before the report.

## PREMISE — MEASURED at authoring (2026-09-29, main tree; PIN origin 3cd69de)

Printed by `bash scripts/premise_block.sh` from the main tree, whose HEAD was origin's tip (3cd69de plus a commit of
transcript digests). The transcript count is taken within a byte cap, so it does not move as the session grows, and
Part B reads the documents at 3cd69de. Expected to differ: the demo's byte count, if a graph re-indexed the callers of
`scripts/stack.py` since; nothing else.

```
$ git merge-base --is-ancestor 3cd69de HEAD && echo 3cd69de-is-an-ancestor-of-HEAD
3cd69de-is-an-ancestor-of-HEAD
$ sha256sum .claude/hooks/system1-context.py scripts/codemap.py scripts/hook_context.py scripts/hooks/post-commit tasks/briefs/jev-trim/k2_authoring_probe.py | cut -c1-16,65-
df094d99240380bc  .claude/hooks/system1-context.py
f77c79f914348600  scripts/codemap.py
1f4912ce9389185d  scripts/hook_context.py
23c605f1ec16c1d6  scripts/hooks/post-commit
10ec956aea6b79a0  tasks/briefs/jev-trim/k2_authoring_probe.py
$ grep -n '^TOOL_BUDGET\|^TOOLS = \|^def shell_code\|^def command_positions\|^def plan_tool\|^def window_id\|^def open_regular\|^class WindowLock\|^def reset\|^def main' .claude/hooks/system1-context.py
63:TOOL_BUDGET = 2048
77:TOOLS = ("Write", "Edit", "Bash")
181:def command_positions(cmd):
357:def shell_code(cmd):
568:def plan_tool(payload, table, seen, budget=TOOL_BUDGET):
868:def window_id(payload):
875:def open_regular(path, flags, follow=False):
936:class WindowLockTimeout(TimeoutError):
940:class WindowLock:
990:def reset(payload, state, now):
1014:def main(argv):
$ grep -n '^PACK_DIR\|^def pack_path\|^def lookup\|^def edit_context\|^def _load_pack' scripts/codemap.py
39:PACK_DIR = Path(".jev") / "codemap"
118:def pack_path(root: Path, rel: str) -> Path:
865:def _load_pack(root, rel):
878:def lookup(path, line, end_line=None, root=None):
918:def edit_context(file_path, old_string, root=None, replace_all=False):
$ grep -n 'codemap refresh' scripts/hooks/post-commit | cut -c1-100
165:printf '%s %s codemap refresh %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(git rev-parse --short HE
$ grep -n '"matcher"' .claude/settings.json
51:        "matcher": "Edit|Write|Read",
99:        "matcher": "Grep|Bash",
108:        "matcher": "Write|Edit|Bash",
$ ls scripts/filepacks.py tests/test_filepacks.py .jev/filepacks 2>&1 | cut -c1-90
ls: cannot access 'scripts/filepacks.py': No such file or directory
ls: cannot access 'tests/test_filepacks.py': No such file or directory
ls: cannot access '.jev/filepacks': No such file or directory
$ python3 tasks/briefs/jev-trim/k2_authoring_probe.py --transcript /root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl --bytes 792000000 --rev 3cd69de
A windows=141 bytes=792000000
A files per window, Read/Edit/Write: median 5 p90 13 max 25
A files per window, reader Bash: median 32 p90 58 max 93
A files per window, the union: median 32 p90 60 max 93
A share of the union seen only through reader Bash: 0.834
A files per reader call: median 1 p90 3 max 23 calls 6003
B source ledger: lines 1749 bytes 1304869
B source decisions: lines 144 bytes 136355
B source incidents: lines 866 bytes 694738
B source skills: lines 2796 bytes 300265
B code files 1174
B lines naming a file, ledger: median 0.0 p90 2 max 29 none 0.79
B lines naming a file, decisions: median 0.0 p90 0 max 3 none 0.98
B lines naming a file, incidents: median 0.0 p90 1 max 30 none 0.85
B lines naming a file, skills: median 0.0 p90 0 max 12 none 0.93
$ printf '{"tool_name":"Edit","tool_input":{"file_path":"%s/scripts/stack.py","old_string":"def cmd_run("}}' "$PWD" > /tmp/k2-premise-edit.json && python3 scripts/codemap.py demo /tmp/k2-premise-edit.json | sed -n '2p;3p'
enclosing: cmd_run
--- the entry L2b would inject (603 bytes) ---
```
