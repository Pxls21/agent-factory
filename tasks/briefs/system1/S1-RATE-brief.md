# S1-RATE: every System-1 injection carries an id, and the agent scores it on the first line of its next text (task #295, D-092 item 3)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/S1-RATE-report.md` (write it
incrementally from the start). PIN: the local HEAD f2403c2 (subject "skills: four held lessons baked"; its push to origin is queued behind CI, so cite commits by subject in anything you write). Design: `docs/research/findings/system1-context/DESIGN-2026-09-25.md`
(layers L1, L2, L3, L6). Rulings: D-092 (item 3) and D-093 in `docs/08_DECISION_LOG.md`.

## WHY

The owner (D-092 item 3): each time the System-1 layer injects context, the agent scores how relevant it was to the task at
hand and how useful the information was, as a fixed-format line at the top of its next reply, so that a script extracts the
scores deterministically and a GEPA-style loop trains on them (task #297: Laya learns to rank skill sections from these
scores and from the situations L1 detects). Today no injection carries an id, nothing asks for a score, and nothing
extracts one. The premise block measures how often an injection happens and how the transcript records it.

## CONTRACT

1. **The stamp.** Every injection that reaches the model through `scripts/hook_context.py` carries an id: a first line
   `[S1 <id> <source>]` and a last line that asks for the score (item 2). `<id>` is `s1-` and 8 lowercase hex digits,
   random per injection. `<source>` is the wrapped hook's file stem (`system1-context`, `search-intercept`,
   `edit-snapshot`, ...). The text between the two lines is byte-identical to what the wrapper hands the model today.
   - A blocking hook's message is context the model reads too: when the wrapped hook exits 2 with a non-empty stderr (the
     search intercept's graft answer), stamp that stderr the same way; the exit code and stdout stay as they are. Any other
     non-zero exit passes through unchanged and unstamped.
   - Off switch: the file `<repo>/.jev/s1-rate-off` (the wrapper's output is then byte-identical to the PIN's). Any failure
     while stamping hands the model the unstamped context: never block, never lose the context.
   - ONE implementation of the stamp and of the score syntax, used by the wrapper and the extractor. The tests never
     import it: they write the expected lines as literals (the oracle stays independent).
2. **The score line.** The request line tells the agent, in about 200 bytes, to begin the next text it writes with
   `S1-RATE <id> rel=<0-3> use=<0-3>`, optionally followed by a space and a note of at most 120 characters (useful when a
   score is 0: what was wrong). One line per injection not yet scored, before any other text. The scale, written in the
   request line itself:
   - `rel`: 0 unrelated to the task at hand, 1 same area but not this step, 2 relevant to this step, 3 governs this step.
   - `use`: 0 noise or already known, 1 confirms what I knew, 2 I used it, 3 it changed what I did.
   You may shorten the words; a change to the scale or the syntax is a DISCREPANCIES row with the reason.
3. **Telemetry and the join.** One JSON line per stamp in `<repo>/.jev/injections.jsonl`: the time, the id, the source, the
   event, the tool name, the payload's `tool_use_id` (when it has one), the session id, the agent id (or `main`), the bytes
   and the sha256 of the stamped text; never the text. The wrapper reads these from the payload it already passes through.
   S1-ALL built the section join for the prompt path: each injected entry in `.jev/system1.jsonl` carries `skill`,
   `heading`, `score`, `project` and `sha` (the first 16 hex digits of the sha256 of that block's text), so a transcript
   attachment split at its `[system1 · ` label lines hashes to those `sha` values. Give the TOOL path of
   `system1-context.py` the same: its record gains the payload's `tool_use_id` and each injected entry the block's `sha`;
   nothing else in the tool path changes (its rows, budgets and output bytes stay the PIN's).
4. **The extractor, `scripts/s1_scores.py`.** It reads Claude Code transcripts (a session's main JSONL and its
   `subagents/` files), finds every stamped injection (the premise block names the record kinds that hold hook context;
   find them all), pairs each with the first assistant text after it in the same thread (the main thread or the same
   subagent), and parses the S1-RATE lines at the top of that text. Output, one JSON line per injection: id, source, event,
   tool, session, agent, time, status (`scored`, `missing`, `malformed`, `late` = scored in a later text, `unknown-id` = a
   score for an id never injected in that thread, `duplicate`), rel, use, note, and the skill sections the injection held
   (read from its own `full details: <file> § <heading>` pointer lines, so the join works when `.jev/` is gone; the
   `.jev/*.jsonl` lines add fields when present). A note passes through `transcript_export.scrub` before it is written. A
   summary per source: injections, scored, the compliance rate, the mean rel and use. It prints ids and counts only, never
   an injection's text or a prompt.
5. **Nothing else changes.** Blocking behavior, exit codes, the timeout, the hooks' own output and telemetry (except the
   tool path's new fields in item 3), the Codex and Hermes adapters under `harness-ports/`, and `wiki-context.py` stay as they are.
   (`wiki-context.py` is registered without the wrapper; stamping it needs a settings change, and it also feeds the PC
   Hermes lanes: say so under NOT-done; the coordinator takes it to the owner.)

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. Tests: a new `tests/test_s1_rate.py`, and the hook_context tests in `tests/test_session_hooks.py` updated to the stamped
   form. Cover: the stamp on PreToolUse, PostToolUse and UserPromptSubmit; an exit-2 stderr stamped with its exit code and
   stdout unchanged; other non-zero exits unchanged; the off switch; a stamping failure gives the unstamped context; the
   telemetry line (its fields, no text); the REAL `system1-context.py` through the REAL wrapper on a fixture tool call
   (stamped, and its `system1.jsonl` record carries the `tool_use_id` and the `sha` its stamped block hashes to); the extractor on a fixture transcript whose records copy the SHAPE of real
   ones (fake content): scored, missing, late, each malformed form (a bad id, `rel=4`, the fields out of order, the line
   below other text), unknown-id, duplicate, and two threads kept apart; a fake secret planted in a note never reaches the
   output. A negative control reds for each on the PIN's code or on a named mutant (a kill is a FAILED test, never an
   error: AF-AP-223).
3. A live read: the extractor over this session's real transcripts (in process; ids and counts only): the injections
   found per record kind and per source, and how many carry a stamp (0 before the landing).
4. The wrapper's added cost per call, p50 and p95 over at least 200 calls, with its command: it must stay under 20 ms.
5. `bash scripts/test_summary.sh` twice on `tests/test_s1_rate.py tests/test_session_hooks.py tests/test_system1_context.py
   tests/test_search_intercept.py tests/test_edit_snapshot_ap_screen.py` with the set id (the floor below); pyflakes rc 0;
   `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0 for every file you write.
6. NOT-done and DISCREPANCIES.

## BOUNDARY

MODIFY: `scripts/hook_context.py`; `.claude/hooks/system1-context.py` (only the tool path's record: `tool_use_id` and
each entry's `sha`); `tests/test_session_hooks.py` and `tests/test_system1_context.py` (the two test files that name the
wrapper: their expected output gains the stamp, and the new fields get their tests). CREATE: `scripts/s1_scores.py`,
`tests/test_s1_rate.py`, your report. READ everything else. The vendored manifest covers `.claude/`: do not regenerate
it; the coordinator does at landing, and adds the standing rule to CLAUDE.md.

**LIVE-FILE RULE (AF-AP-222):** `scripts/hook_context.py` wraps the hooks of the coordinator's own session: it runs on every
Read, Write, Edit, Bash and Grep call and every prompt, the running lanes' calls included. Build and test each new version in
your scratch, then move it into place with one `mv`; it never blocks on its own account. The off switch is the file
`.jev/s1-rate-off`; the coordinator uses it if the wrapper misbehaves. Once it is in place, your own context gets stamped
injections too: score them as the request says.

## STANDING RULES

No git writes in this tree; no PC bridge; no outward-facing action. Transcripts hold secrets: read them in process, print ids
and counts, never a prompt's or an injection's text. The disk is shared (1.8G free): scratch under 150 MB in
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/s1rate/`, deleted as you go; a short
`--basetemp` with its parent created first. Test counts pasted from `scripts/test_summary.sh`; stamps from `date -u`. Long
commands in one foreground call; kill by pid, never by name.

## PREMISE — MEASURED at authoring (2026-09-25 23:2xZ, the sandbox tree at f2403c2)

```
$ git log -1 --format='%h %s' HEAD | cut -c1-100
f2403c2 skills: four held lessons baked (env-tool-quirks: a waiter on a task .output reads the trail
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-100
eade28c transcripts: scrubbed sandbox chat digests (2026-09-25)
$ wc -l < scripts/hook_context.py; sed -n 34,44p scripts/hook_context.py
46
        return 0
    out = proc.stdout.decode("utf-8", "replace")
    if proc.returncode != 0:
        sys.stdout.write(out)
        sys.stderr.write(proc.stderr.decode("utf-8", "replace"))
        return proc.returncode
    if out.strip():
        print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": out.rstrip("\n")}}))
    return 0
$ grep -o 'hook_context.py [A-Za-z]* -- python3 [^ ;]*' .claude/settings.json | sed 's#\$CLAUDE_PROJECT_DIR/##'
hook_context.py PostToolUse -- python3 .claude/hooks/edit-snapshot.py"
hook_context.py UserPromptSubmit -- python3 .claude/hooks/system1-context.py"
hook_context.py PreToolUse -- python3 .claude/hooks/search-intercept.py"
hook_context.py PreToolUse -- python3 .claude/hooks/system1-context.py"
$ grep -l hook_context tests/*.py harness-ports/tests/*
tests/test_session_hooks.py
tests/test_system1_context.py
$ grep -n 'sha=hashlib' .claude/hooks/system1-context.py
846:                     sha=hashlib.sha256(text.encode("utf-8")).hexdigest()[:16])
$ python3 /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/s1rate/measure_injections.py /root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl | cut -c1-200
records ('hook_success', 'SessionStart') 87
records ('hook_success', 'PostToolUse') 79
records ('hook_additional_context', 'PostToolUse') 70
records ('hook_additional_context', 'SessionStart') 68
records ('hook_success', 'PreToolUse') 61
records ('hook_additional_context', 'PreToolUse') 61
records ('hook_success', 'UserPromptSubmit') 54
records ('hook_additional_context', 'UserPromptSubmit') 3
keys hook_success ['command', 'content', 'durationMs', 'exitCode', 'hookEvent', 'hookName', 'stderr', 'stdout', 'toolUseID', 'type']
keys hook_additional_context ['content', 'hookEvent', 'hookName', 'toolUseID', 'type']
assistant texts 6714 | injections pending at each text: [(0, 6535), (1, 161), (2, 14), (3, 3), (4, 1)]
$ bash scripts/test_summary.sh tests/test_session_hooks.py tests/test_system1_context.py tests/test_search_intercept.py tests/test_edit_snapshot_ap_screen.py   (run at authoring)
pytest-exit: 0
pytest-summary: 465 passed in 70.04s (0:01:10)
4 files set=76b279850729
```

A question for you, not a fact: which record kinds in a Claude Code transcript hold the context a hook hands the model
(the additionalContext of PreToolUse, PostToolUse and UserPromptSubmit; a blocking hook's stderr; a UserPromptSubmit hook's
plain stdout), and does each keep the text byte for byte?
