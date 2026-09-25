# S1-ALL: the System-1 layer reaches every skill and sends the relevant section verbatim (task #296, D-093)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/S1-ALL-report.md` (write it
incrementally from the start). PIN: a67489f (origin). Design: `docs/research/findings/system1-context/DESIGN-2026-09-25.md`
(layers L3 and L6). Rulings: D-092 and D-093 in `docs/08_DECISION_LOG.md`.

## WHY

The owner (D-093): the skills stay where they are, and the System-1 layer, not the harness's skill list, decides what the
agent sees: "Laya handles and manages the skills so that it doesn't have to all feed into the context", and "it doesn't just
rank skills, it provides relevant parts of the skill". Today the situation hook (`.claude/hooks/system1-context.py`) does
that per prompt (design L3) over 19 skills only (`prompt_corpus` in `.claude/hooks/system1-situations.json`); the other
398 are invisible to it. This lane makes every skill reachable, deterministically. Laya's ranking (task #297) and the
agent's injection scores (task #295) come after, on top of this corpus.

## CONTRACT

1. **Every skill in the corpus.** The prompt path ranks sections of every `SKILL.md` under `.claude/skills/` (and the
   user-level ones the harness also lists, `~/.claude/skills/*/SKILL.md`, if you find they belong; say what you decided and
   why). A skill's frontmatter `description` is the strongest signal of what it is for: use it. The corpus follows the tree
   (a skill added or removed changes it with no table edit); the 19 project skills keep at least the reach they have now.
2. **The section, verbatim.** What is injected stays what the hook injects today: the best one or two sections, verbatim,
   inside the prompt budget (4,096 bytes), each with its pointer, once per context window. For a skill that is not one of
   the project's own, add its one-line description before the section, so the agent knows what the skill is.
3. **Precision, measured on real prompts.** Replay at least 50 of the owner's real prompts from this session's transcripts
   (read in process; print prompt ids and the first words only, never whole prompts) through the old and the new hook:
   per prompt, the injected sections (skill § heading) and scores; the injection rate; how many injections come from
   non-project skills; the bytes. Choose the thresholds from that table and say why. Noise is worse than absence: a prompt
   that matches nothing well injects nothing.
4. **Fast.** The corpus index is cached and rebuilt only when a `SKILL.md` changes. Measure the build and the per-prompt time
   (p50, p95 over the replay set) with a warm cache; the hook must stay well under a second.
5. **Nothing else changes.** The tool-call path (the situation rows), the budgets, the once-per-window marker, the kill
   switch and the telemetry format stay as they are, except for new fields you add to the telemetry line.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. The replay table (item 3) and the timing (item 4), each with its command.
3. Tests in `tests/test_system1_context.py`: a non-project skill's section is reachable and carries its description; the
   corpus follows the tree (a skill added in a fixture tree is found with no table edit); the thresholds (a weak match
   injects nothing); the budget and the once-per-window marker with the larger corpus; the cache rebuilds on a changed
   `SKILL.md`. A negative control reds for each on the PIN's hook.
4. `bash scripts/test_summary.sh` twice on `tests/test_system1_context.py tests/test_session_hooks.py
   tests/test_skill_frontmatter.py` with the set id; pyflakes rc 0; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints
   0 for every file you write.
5. NOT-done and DISCREPANCIES.

## BOUNDARY

MODIFY: `.claude/hooks/system1-context.py`, `.claude/hooks/system1-situations.json`, `tests/test_system1_context.py`.
CREATE: your report. READ everything else. The vendored manifest covers `.claude/`: do not regenerate it; the coordinator
does at landing.

**LIVE-FILE RULE (AF-AP-222):** `.claude/hooks/system1-context.py` runs on every prompt and tool call of the coordinator's
own session. Build and test each new version in your scratch, then move it into place with one `mv`; it must never block
and always exit 0. The kill switch is the file `.jev/system1-off`; the coordinator uses it if the hook misbehaves.

## STANDING RULES

No git writes in this tree; no PC bridge; no outward-facing action. Transcripts hold secrets: read them in process, print ids
and counts, never a prompt's full text. The disk is shared (1.7G free): scratch under 150 MB in
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/s1all/`, deleted as you go; a short `--basetemp`
with its parent created first. Test counts pasted from `scripts/test_summary.sh`; stamps from `date -u`. Long commands in
one foreground call; kill by pid, never by name.

## PREMISE — MEASURED at authoring (2026-09-25 21:4xZ, /home/user/agent-factory; the files named are unchanged from the PIN)

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-90
a67489f SLOPO2 report: cite the pushed id of the D-093 retro commit (58a9c6f), not its loc
$ grep -n -E '^(PROMPT_|MIN_PROMPT|ONE_LEAD|SECOND_EXCERPT|TOOL_BUDGET|SKILLS_DIR|KILL|STATE)[A-Z_]* *=' .claude/hooks/system1-context.py
50:SKILLS_DIR = os.path.join(ROOT, ".claude", "skills")
52:TOOL_BUDGET = 2048
53:PROMPT_BUDGET = 4096
54:PROMPT_EXCERPTS = 2                  # the best one or two sections per prompt, each at most PROMPT_BUDGET // 2
55:PROMPT_SCAN_CHARS = 4000             # a pasted document is matched on its head
56:MIN_PROMPT_SCORE = 12.0              # below it a prompt injects nothing (noise is worse than absence)
57:ONE_LEAD_MIN_SCORE = 18.0            # a section whose heading and skill name share ONE word with the prompt (F5)
58:SECOND_EXCERPT_RATIO = 0.75          # a second section only when it scores at least this share of the best one
$ grep -n -E '^def (corpus_index|plan_prompt|plan_tool|tokens|split_sections|sections)' .claude/hooks/system1-context.py
110:def read_stdin(wait_s=STDIN_WAIT_S):
131:def load_table(path=TABLE_PATH):
135:def detectors(row):
143:def command_positions(cmd):
149:def _mask(edits, a, b, ch="x"):
154:def _word(reads, w):
168:def _code(cmd, i, hi, edits, closer, nest):
252:def _dquote(cmd, i, hi, edits, nest):
278:def _heredoc(cmd, i, hi, edits, doc, nest):
319:def shell_code(cmd):
335:def rel_path(path, cwd):
344:def tool_fields(tool, ti, cwd):
354:def error_name(exc):
363:def parse_skill(text):
380:def skill_file(skill):
384:def read_skill(skill):
388:def skill_pointer(skill, heading):
392:def line_key(skill, line):
397:def resolve(row, lines, sections):
424:def entry_units(idx, lines):
441:def compose(blocks, seen, budget, pointer_only=False):
493:def match_rows(table, tool, ti, cwd, skipped=None):
530:def plan_tool(payload, table, seen, budget=TOOL_BUDGET):
563:def tokens(text):
574:def corpus_index(corpus, cache_path):
598:def plan_prompt(payload, table, seen, cache_path, budget=PROMPT_BUDGET):
663:def window_id(payload):
670:def open_regular(path, flags, follow=False):
682:def read_regular(path, follow=False):
695:def write_json_atomic(path, data):
718:def load_seen(path):
766:def log(state, rec):
785:def reset(payload, state, now):
809:def main(argv):
$ python3 -c 'the prompt corpus in the situation table'
19 skills: adversarial-review anti-hollow-green bug-echo build-loop code-intel-trio contract-gate deep-work empirical-validation env-tool-quirks luck orchestration ouroboros-stdio pc-bridge-lanes premortem-roast root-cause-debugging session-continuity thermo-nuclear-review trace-the-chain vendor-first
40 tool rows
$ ls .claude/skills/*/SKILL.md | wc -l; ls /root/.claude/skills/*/SKILL.md | wc -l
413
4
$ du -sc .claude/skills/*/SKILL.md | tail -1   (1 KiB blocks)
6028	total
$ wc -l .claude/hooks/system1-context.py tests/test_system1_context.py
  856 .claude/hooks/system1-context.py
  925 tests/test_system1_context.py
 1781 total
$ tail -3 .jev/system1.jsonl | cut -c1-200   (the telemetry)
{"bytes": 0, "event": "PreToolUse", "injected": [], "matched": ["pc-call"], "ms": 5.8, "skipped": [{"key": "pc-bridge-lanes \u00a7 Bridge calls", "row": "pc-call", "why": "duplicate"}], "t": "2026-09-
{"bytes": 0, "event": "PreToolUse", "injected": [], "matched": ["push-delegate-work", "push", "commit", "commit-increment", "background"], "ms": 10.7, "skipped": [{"key": "orchestration \u00a7 The ORC
{"bytes": 0, "event": "PreToolUse", "injected": [], "matched": [], "ms": 3.0, "skipped": [], "t": "2026-09-25T21:49:06Z", "tool": "Bash", "window": "bdab799a-dc80-5933-9c9e-c80f206f9a17.main"}
$ python3 -c 'prompt-event telemetry: events, injected, bytes'
prompt events 51 injections 5 bytes 9500
[(None, 5)]
$ grep -n -E 'system1-off|AF_SYSTEM1' .claude/hooks/system1-context.py | head -4
29:Advisory, never a gate: every path exits 0 and nothing blocks. Off switch: the file <state>/system1-off (the reset
39:<state> is <repo>/.jev. Test seam, read once at start: AF_SYSTEM1_STATE (the state directory instead of <repo>/.jev).
811:    state = os.environ.get("AF_SYSTEM1_STATE") or os.path.join(ROOT, ".jev")
813:    if not resetting and os.path.lexists(os.path.join(state, "system1-off")):     # a dangling link counts (F12)
$ df -h / | awk 'NR==2{print $4}'
1.7G
```

A question for you, not a fact: the telemetry's `injected` entries carry no `skill` field (the count above reads None).
What does a prompt event's record hold today, and what should it hold so that task #295 can join the agent's scores to
each injected section?
