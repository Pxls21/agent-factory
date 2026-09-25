# CTX1: CLAUDE.md shortened losslessly into skills; GitNexus stops rewriting it; no re-index without an update (D-089)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/jev-pipes/CTX1-report.md` (write it
incrementally from the start). PIN: 715caaf (origin; every boundary file is unchanged from the PIN to the local head, measured).

## WHY

The owner (D-089, 2026-09-25): shorten CLAUDE.md "losslessly, and anything you take out, you turn into a skill that you then
reference in the Claude.md"; under 1,000 lines is fine, ideally 500. And: stop GitNexus rewriting CLAUDE.md on every re-index;
"I don't think anything should be re-indexed unless it's updated first." CLAUDE.md is re-sent with every request of every session
and re-injected whole each time it changes on disk (`docs/research/findings/jev-pipes/CONTEXT-BUDGET-2026-09-25.md`: 7.1% of this
session's re-sent tokens in re-injections alone); the GitNexus banner rewrite after each commit is one of those changes.

## CONTRACT

1. **Lossless.** Every sentence taken out of CLAUDE.md moves VERBATIM into a skill: an existing one where its topic already lives
   (`orchestration`, `build-loop`, `deep-work`, `anti-hollow-green`, `session-continuity`, `code-intel-trio`, ...) or a new one
   whose description triggers on exactly the situations its text governs (for example the environment and tool quirks, the PC
   bridge and lane operations, the Ouroboros stdio quirks). Where the text was, CLAUDE.md keeps a one-line pointer naming the skill.
   The only allowed drop is an exact duplicate (the same sentence twice); list each one. A mechanical check proves it: every
   non-empty line of the PIN's CLAUDE.md, whitespace-normalized, is found in the new CLAUDE.md or in a skill file the new CLAUDE.md
   names, except the listed duplicates. Paste its summary line.
2. **What stays** is what every turn needs: the git branch and push rules, the NO STUBS rule, the STANDING PROJECT RULES (their
   text is hash-gated: do not touch it), the ground-truth reading order, the current model routing (the table and the rules in force,
   not their history), the pointers, and the GitNexus block. Target 500 lines or fewer; report lines and bytes before and after.
3. **Every consumer of CLAUDE.md's text keeps working** (orchestration 0h). The quirk readers read the new quirk locations as well
   as CLAUDE.md: `scripts/jev_context.py` `inst_quirks`, `scripts/hiccup_scan.py` (its quirk candidates, and the rule-phrase check in
   `tests/test_hiccup_scan.py`), `scripts/jev_locate.py`. `.claude/hooks/search-intercept.py` anchors that quote a moved sentence cite
   its new place. `tests/test_claude_md_lint.py` and `harness-ports/tests/test_context_mirrors.sh` stay green (keep the 17 `## `
   sections, so the AGENTS.md and `.hermes.md` mirrors need no change).
4. **No automatic rewrite of CLAUDE.md or AGENTS.md by GitNexus.** Every automatic `gitnexus analyze` call site passes
   `--skip-agents-md`. The committed GitNexus blocks lose their volatile counts line (the block is ours from now on; say so in the
   CLAUDE.md sentence that says GitNexus owns it). Keep the skill-file behavior of analyze as it is.
5. **No re-index without an update.** `scripts/hooks/post-commit` re-indexes a graph only when the commit changed a file that graph
   reads; a commit that touches only Markdown, `wiki/`, `todo/`, `transcripts/` or `tasks/` launches none of the four (graft,
   GitNexus, codebase-memory, code-review-graph). One line in the hook's log says which ran or why none did.
6. **Install order.** Each change to CLAUDE.md on disk is re-injected into the coordinator's context whole: build the new CLAUDE.md
   in your scratch dir and install it with ONE write at the end. Skill edits follow the repository's mirror rule (read how
   `.agents/skills/` ports and `scripts/skill_bake_finish.sh` work; run the bake tail once at the end and list its paths).

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. The losslessness check's summary (lines checked, found, the duplicate list), and a negative control: the check reports a line
   you remove on purpose from a scratch copy.
3. Tests: the post-commit re-index rule with fake indexer binaries on PATH in a temp repo (a docs-only commit launches none, a code
   commit launches each, every analyze call carries `--skip-agents-md`), red first on the PIN's hook; the quirk readers finding a
   quirk that now lives in a skill.
4. `bash scripts/test_summary.sh` over the consumer set below (and your new tests) twice, with the set id; `bash
   harness-ports/tests/test_context_mirrors.sh`; pyflakes rc 0; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0 for every file
   you write.
5. NOT-done and DISCREPANCIES.

## BOUNDARY

MODIFY: `CLAUDE.md`; `.claude/skills/*/SKILL.md` and their ports under `.agents/skills/`; `scripts/hooks/post-commit`,
`scripts/resume-heal.sh`, `harness-ports/bin/pc-setup.sh` (the analyze flag only); `scripts/jev_context.py`, `scripts/hiccup_scan.py`,
`scripts/jev_locate.py`, `.claude/hooks/search-intercept.py` (quirk sources and anchor text only); their tests. CREATE: new skill
directories (both trees), new tests, your report. NOT: `AGENTS.md` and `.hermes.md` content beyond the GitNexus block's counts line;
the STANDING PROJECT RULES text; any file another lane holds (`.lanes-live`: `scripts/laya_systemone_server.py`,
`scripts/laya_ft/*`, `scripts/jev.py`, `scripts/qwen_jev.py`, `scripts/push_clean.sh`, `scripts/safe_commit.sh`,
`scripts/hooks/pre-commit` and their tests). Scratch: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ctx1/`.

## STANDING RULES

No git writes (the coordinator commits); never run `gitnexus analyze` for real on this tree (it outlives the tool's time cap; the
tests use fakes); no PC bridge; no outward-facing action. Never read a real secret file. Two other lanes are live in this tree:
touch nothing outside your boundary. The disk is tight (1.8 GB free; the bake tail's worktree needs about 1 GB): delete your own
scratch copies as you go.

## PREMISE — MEASURED at authoring (2026-09-25 12:5xZ, the sandbox, the PIN's bytes)

```
$ wc -l -c CLAUDE.md AGENTS.md .hermes.md; git show 715caaf:CLAUDE.md | sha256sum | cut -c1-16
   809  92730 CLAUDE.md
   419  32758 AGENTS.md
   523  45068 .hermes.md
6eae9de1c792c420
$ grep -c '^## ' CLAUDE.md
17
$ bash harness-ports/tests/test_context_mirrors.sh | tail -1
11 passed, 0 failed
$ bash scripts/test_summary.sh tests/test_claude_md_lint.py tests/test_hiccup_scan.py tests/test_jev_context.py tests/test_jev_locate_echo.py tests/test_search_intercept.py
pytest-summary: 233 passed in 66.48s (0:01:06)
$ bash scripts/pc_suite.sh set-id -- <the same five files>
5 files set=bcfd3537c9e3
$ node .gitnexus/run.cjs analyze --help | grep -A1 -E 'skip-agents-md|no-stats'
  --skip-agents-md                    Skip updating the gitnexus section in
                                      AGENTS.md and CLAUDE.md
  --no-stats                          Omit volatile file/symbol counts from
                                      AGENTS.md and CLAUDE.md
$ grep -n -E 'gitnexus analyze' scripts/hooks/post-commit scripts/resume-heal.sh harness-ports/bin/pc-setup.sh   (call sites)
scripts/hooks/post-commit:51, scripts/resume-heal.sh:21, harness-ports/bin/pc-setup.sh:107 and :125
$ grep -l CLAUDE.md scripts/*.py .claude/hooks/*.py    (the readers of its text; counts of the name per file)
scripts/jev_context.py 6, scripts/hiccup_scan.py 6, scripts/jev_locate.py 1, .claude/hooks/search-intercept.py 6,
.claude/hooks/graft-first-nag.py 2, scripts/gn_mcp.py 1, scripts/jev.py 1
```

A question for you, not a fact: `scripts/setup.sh`, `scripts/push_clean.sh`, `scripts/push_when_green.sh`,
`.claude/hooks/graft-first-nag.py` and `scripts/gn_mcp.py` also name CLAUDE.md; read each and say whether the shortening touches it.
