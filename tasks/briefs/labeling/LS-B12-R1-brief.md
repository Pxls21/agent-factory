# LS-B12-R1: fix-echo's status, and search text that a tool reads as an option (task #385; the first repair under D-031)

Role: the LS-B12 builder, resumed (a sandbox code-implementer, Opus 5.5). PIN: origin 74285a5 (CI run #1177 passed).
Authored 2026-09-30 08:2xZ by the coordinator. Read first: the verifier's report of record
`tasks/briefs/labeling/VERIFY-LS-B12-report.md` (its coordinator note, then F-1, F-3 and F-8), the docstring of
`scripts/stack.py`, skill `label-authoring`, and D-031, D-111 and D-115 in `docs/08_DECISION_LOG.md`. Do NOT spawn
subagents.

## THE ROUND TABLE (D-115)

| Round | Landed | Verify | Blockers | Their class |
|---|---|---|---|---|
| LS-B12, the build | 8b940f8 (05:4xZ) | VERIFY-LS-B12: NOT-READY (07:58Z) | F-1: `fix-echo` reads unmapped when its own output holds the text `answered: none`. F-2: code-review-graph writes in the tree. | F-1: a status keyed on a substring of output that carries repo text. F-2: a tool's side effects (D2's class, from the build's own report). |

- Budget: this is the first repair (D-031: one focused repair by default).
- F-2 joins task #399 with D2 and F-9, so it is not in this round. No class recurs inside this component's rounds, the
  blocker count starts here, and no owner word stops it. So R1 goes ahead.
- If VERIFY-LS-B12-R1 finds a blocker again, the coordinator runs D-115's review before any second repair.
- Not in this round (issue #88, D-108 item 2): F-4 (`changes` on a stale index), F-5, F-6, F-7 and F-15 to F-25.

## CONTRACT (revision R1)

1. **F-1, the blocker: fix-echo's status never depends on repo text in its output.**
   - Measured at authoring on a scratch worktree at the PIN, with the verifier's probe patch (its removed line holds
     the text), then with the verifier's fix (`"--json"` added to the argv, `unmapped_if = '"answered": []'`):
     ```
     at the PIN, the probe:                    ## sites · unmapped — rg-and-graft unavailable   (answered: rg-token)
     with the fix, the probe:                  ## sites · ok · rc 0 · 0.12 s                    {"answered": ["rg-token"], ...
     with the fix, an add-only patch:          ## sites · unmapped — rg-and-graft unavailable   {"answered": [], ... "defect (removed)": "(none)", ...
     with the fix, PATH = python3 and git:     ## sites · unmapped — rg-and-graft unavailable   {"answered": [], ...
     ```
   - So the verifier's fix cures F-1 and keeps the missing-tools case, but it leaves F-8 (item 2). Use it or a better
     one.
   - Red tests first, through the real runner: (a) a patch whose removed line holds `answered: none` reads ok; (b) a
     site whose snippet holds it reads ok (the verifier's tiny-world route); (c) with neither rg nor graft on PATH, a
     real removed line still reads unmapped, exit 1.
   - The JSON skeleton: when a JSON pack does not fit its budget, `render()` falls back to a skeleton with no
     `answered` key (`scripts/jev_context.py:962-967`), and a status keyed on that key then reads ok. A question for
     you: can a pack from the missing-tools case reach the skeleton at the step's budget (`BUDGET_DEFAULT`, 6,000)?
     Answer it with a measurement, and pin the answer with a test.

2. **F-8: a diff with nothing to echo reads its own status, never "rg-and-graft unavailable".**
   - The verifier's cases: a non-diff file, a `HEAD:path` blob, an in-tree symlink to a non-diff, an add-only commit.
   - The run reads ok (exit 0), and its print says that nothing was echoed and why. A real removed line with no rg and
     no graft still reads unmapped (item 1 (c)).
   - The mechanism is yours. Keep the change as small as it can be. Before you edit a symbol in
     `scripts/jev_context.py` (its `build_pack` and `render` serve every Jev tool), run GitNexus impact on it and paste
     the result.

3. **The sweep: the other nine `unmapped_if` steps** (the premise's line map at the PIN): `gate`/graph (169),
   `impact`/ripwire (316), `review`/sentrux (487) and `review`/ripwire (497) on "missing — run scripts/setup.sh";
   `cbm`/search (562) on "project not found or not indexed"; `changes`/all, staged, unstaged and compare (597, 607, 617,
   627) on "gitnexus runner: could not launch".
   - For each, decide with a measurement whether repo text can reach that step's stdout or stderr: does its tool print
     file content, or only names and paths?
   - Where it can, fix it the way item 1 does, with a red test. Where it cannot, give one line of evidence each.

4. **F-3: no search text that starts with `-` reaches a tool as an option (D-111's class).**
   - Where: `search_text` (`scripts/jev_context.py:217`) feeds `graft ask` (:456), `node .gitnexus/run.cjs query`
     (:469) and `codebase-memory-mcp cli search_graph --query` (:494). Nothing marks the end of the options before it.
   - The verifier's cases: q=` --help` (graft printed its help, and the pack counted graft as answered),
     q=` --dir=/tmp/<x>`, and a question over 300 characters whose first quoted token is `--basetemp` (all three tools
     refused an unknown option).
   - The fix: each of those cases reaches each tool as a plain search text, or reaches it not at all. Per tool, a test
     records the argv the tool gets. A plain question's search text stays byte-identical (a regression test).
   - GitNexus rates `search_text` HIGH (3 direct callers, `inst_graft`, `inst_gitnexus` and `inst_cbm`; 3 flows;
     measured at authoring). Run impact before you edit, and paste it.
   - The same check for every other call in `scripts/jev_context.py` and `scripts/jev_echo.py` that passes a value to
     a tool (rg's patterns and tokens, code-review-graph's names, graft's `code like:` text): can the value start with
     `-`? Fix each one that can; one line of evidence for each one that cannot.

5. **The catalog and the listings.**
   - Correct `fix-echo`'s note (it now says a diff that removes no code line reads unmapped).
   - The catalog keeps all fourteen stacks under 4,000 characters (3,729 at the PIN, the verifier's count). Paste the
     new size.
   - In skill `box-and-labels`, correct only the rows that state these behaviors.

6. **Tests and mutants.**
   - Every new test goes through the real runner or the real function. Each negative control asserts its exact
     message.
   - One named mutant per item, each killed. Suggested: the argv without `--json`; the old `unmapped_if`; the F-8
     mechanism reverted; the leading-dash guard removed (one mutant per tool).
   - Your driver's control comes first (AF-AP-223). Bytecode off, and a fresh copy or a cleared `__pycache__` per
     mutant (AF-AP-192).

## WHERE YOU WORK

A new worktree at the PIN under your scratch
(`git -C /home/user/agent-factory -c core.hooksPath=/dev/null worktree add -q --detach <W> 74285a5`), never the shared
tree. Your one shared-tree write is your deliverable, `tasks/briefs/labeling/LS-B12-R1.patch` (`git -C <W> diff 74285a5`
over every file you change, new files included). It must apply at the PIN with `git apply --check`. Remove the worktree
before you report.

## BOUNDARY

- MODIFY, in your worktree only: `scripts/stacks.toml`, `scripts/jev_echo.py`, `scripts/jev_context.py`,
  `tests/test_stack.py`, `tests/test_jev_context.py`, `tests/test_jev_locate_echo.py`; `tests/test_session_hooks.py`
  only if a catalog pin moves; `.claude/skills/box-and-labels/SKILL.md` (item 5 only).
- READ: `scripts/stack.py` (never change it; the runner's schema belongs to task #391), `scripts/jev_locate.py`, the
  tools.
- NOT yours: F-2 and F-9 (task #399: code-review-graph's and graft's side effects); the issue #88 items;
  `.claude/settings.json`, `scripts/install_session_hooks.py`, `/home/user/.claude/settings.json`, the live `.jev/`,
  `.agents/`, `CLAUDE.md`.
- Beside you: VERIFY-K2-R4 (a sandbox verifier in its own worktree, on `scripts/codemap.py` and `scripts/filepacks.py`)
  and SCRUB2-R1 round 5Q on the PC. A real cbm run can read FAILED on a cache-root conflict with another lane's daemon
  (VERIFY-LS-B12 F-11). Never stop a daemon you did not start; say so and go on.

## GATES

In your worktree, each call under 10 minutes, twice, `--basetemp` as a pytest ARGUMENT outside every work tree, counts
pasted from `scripts/test_summary.sh` with set ids from `bash scripts/pc_suite.sh set-id -- <files>`:
- the six files `tests/test_stack.py tests/test_session_hooks.py tests/test_search_intercept.py tests/test_ls_req.py
  tests/test_jev_context.py tests/test_jev_locate_echo.py` (`6 files set=b0ad308a6f97`; re-collect on the PIN, the
  coordinator states no count here);
- every other test that names a file you change (`python3 scripts/stack.py gate paths="<your files>" mode=plan
  graph=no` in your worktree lists them);
- if you change the skill: `tests/test_claude_md_lossless.py tests/test_skill_frontmatter.py
  tests/test_system1_context.py` and `bash harness-ports/tests/test_context_mirrors.sh`.

## REPORT

Return the whole report as your final message:
- the premise re-run;
- per contract item, its pasted evidence; items 3 and 4 as a table (the step or the call, whether repo text or a
  leading `-` can reach it, the evidence);
- files with line counts and sha256; the patch's sha256 and `git apply --check` at the PIN;
- the gates, the mutants, the catalog size;
- the writes your runs made outside their run directories (graft's daily update check included if you saw it, F-9);
- NOT done, first-class; DISCREPANCIES;
- your self-attack: how could a label still read ok when its tool is missing, read unmapped when its tool answered,
  or hand a tool an option?

## STANDING RULES

- No git write in the shared tree (a worktree add and remove, hooks off, is the one exception); no outward action; no
  PC bridge; never register a hook.
- Never read a secret file (`.pc-bridge.env`, any `*.env`, any key file). In any real transcript, read only `text`
  blocks, `tool_use` inputs and record types, never a `thinking` block, and print only counts, bytes and ids.
- Never a top-level `cd` (AF-AP-249): `git -C`, absolute paths or a `( cd … )` subshell.
- A long gate in ONE foreground call; stamps from `date -u`; commits cited by origin id or subject.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- Stop every process you start before you report (the codebase-memory daemon included); kill by pid only.

## PREMISE — MEASURED at authoring (2026-09-30, main tree; PIN origin 74285a5)

```
$ git rev-parse 74285a5
74285a53abc88cbb0d5ae5acce8a15ffdb29602f
$ git merge-base --is-ancestor 74285a5 origin/claude/soundbox-kit-migration-iz1jwf && echo PIN-is-on-origin
PIN-is-on-origin
$ git diff --name-only 74285a5 HEAD -- scripts/stacks.toml scripts/jev_echo.py scripts/jev_context.py scripts/jev_locate.py scripts/stack.py tests/test_stack.py tests/test_jev_context.py tests/test_jev_locate_echo.py tests/test_session_hooks.py tests/test_search_intercept.py tests/test_ls_req.py | wc -l
0
$ for f in scripts/stacks.toml scripts/jev_echo.py scripts/jev_context.py scripts/jev_locate.py scripts/stack.py tests/test_stack.py tests/test_jev_context.py tests/test_jev_locate_echo.py; do printf '%s %s\n' "$(git show 74285a5:$f | sha256sum | cut -c1-16)" "$f"; done
07a3bc500c25927d scripts/stacks.toml
b03edb82eaf07ec3 scripts/jev_echo.py
9ccd68ae3a832371 scripts/jev_context.py
93441f4e45018817 scripts/jev_locate.py
ef819f69430d7459 scripts/stack.py
4190d5e59d8281fd tests/test_stack.py
c2816f7bf978692a tests/test_jev_context.py
2c9e34b92c6c3525 tests/test_jev_locate_echo.py
$ git show 74285a5:scripts/stacks.toml | grep -n 'unmapped_if'
10:# unmapped_if: their wrappers print "<name>_review: <bin> missing — run scripts/setup.sh" and exit 0 when the binary
169:unmapped_if = "missing — run scripts/setup.sh"
316:unmapped_if = "missing — run scripts/setup.sh"
487:unmapped_if = "missing — run scripts/setup.sh"
497:unmapped_if = "missing — run scripts/setup.sh"
562:unmapped_if = "project not found or not indexed"
597:unmapped_if = "gitnexus runner: could not launch"
607:unmapped_if = "gitnexus runner: could not launch"
617:unmapped_if = "gitnexus runner: could not launch"
627:unmapped_if = "gitnexus runner: could not launch"
671:# that does not exist exits 64. No unmapped_if: its registry and quirk instruments answer in every checkout of this
722:unmapped_if = "answered: none"
$ git show 74285a5:scripts/stacks.toml | grep -n 'jev_echo.py", "--diff'
719:argv = ["python3", "scripts/jev_echo.py", "--diff", "{diff}", "--order", "lexical", "--no-jev-log"]
$ git show 74285a5:scripts/jev_context.py | grep -n '^def clean\|^def search_text\|^def inst_graft\|^def inst_gitnexus\|^def inst_cbm\|^def _json_pack\|^def render\|^def build_pack'
119:def clean(text):
217:def search_text(question, toks):
453:def inst_graft(question, toks, ctx):
465:def inst_gitnexus(question, toks, ctx):
493:def inst_cbm(question, toks, ctx):
933:def _json_pack(pack, snip, k, nfiles):
951:def render(pack, top, budget, as_json=False):
972:def build_pack(title, head, chunks, mode, scores, rank_line, answered, notes, extra=(), tail=(), with_files=True):
$ git show 74285a5:scripts/jev_context.py | grep -n '"ask", search_text\|"query", search_text\|"--query", search_text'
456:    argv = ctx.tools["graft"] + ["ask", search_text(question, toks)]
469:    rc, out, reason = run_tool(ctx.tools["node"] + [".gitnexus/run.cjs", "query", search_text(question, toks),
494:    argv = ctx.tools["cbm"] + ["cli", "search_graph", "--project", ctx.slug, "--query", search_text(question, toks)]
$ git show 74285a5:scripts/jev_context.py | sed -n 962,967p
    if as_json:
        skel = json.dumps({"tool": pack["title"], "truncated": True, "ranking": clean(pack["ranking"])[:200],
                           "notes": [clean(n)[:40] for n in pack["notes"]][:12]}, ensure_ascii=False) + "\n"
        if len(skel) <= budget:
            return skel
        return json.dumps({"tool": pack["title"], "truncated": True}) + "\n"
$ git grep -n 'answered: none' 74285a5 -- scripts/stacks.toml tests/test_stack.py tests/test_jev_locate_echo.py | cut -d: -f1-3
74285a5:scripts/stacks.toml:672
74285a5:scripts/stacks.toml:701
74285a5:scripts/stacks.toml:722
74285a5:tests/test_jev_locate_echo.py:185
74285a5:tests/test_stack.py:2536
74285a5:tests/test_stack.py:2544
74285a5:tests/test_stack.py:2839
74285a5:tests/test_stack.py:2847
$ git show 74285a5:scripts/stack.py | grep -n 'any(step.unmapped_if in'
931:                and any(step.unmapped_if in b.decode("utf-8", errors="replace") for b in (stdout, stderr))):
$ python3 scripts/gate_files.py --why scripts/stacks.toml scripts/jev_echo.py scripts/jev_context.py
tests/test_jev_context.py  comment:1
tests/test_jev_locate_echo.py  comment:1
tests/test_session_hooks.py  code:475
tests/test_stack.py  code:2405,2554,2660,2668  comment:1,1288,2381,2817
```
