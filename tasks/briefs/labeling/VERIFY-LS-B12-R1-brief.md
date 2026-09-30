# VERIFY-LS-B12-R1: verify the repair of fix-echo's status and of search text read as an option (task #385)

Role: the VERIFY-LS-B12 verifier, resumed (a sandbox adversarial-verifier, Opus 5.5): the cheapest independent review
of a repair is the original verifier, whose probes are still in its scratch (orchestration 0f). PIN: origin 631dc86
(the landing; CI run #1181 passed). Authored 2026-09-30 10:3xZ by the coordinator. Read first: the repair brief
`tasks/briefs/labeling/LS-B12-R1-brief.md`, the builder's report of record `tasks/briefs/labeling/LS-B12-R1-report.md`
(its coordinator note, then the report), and your own `tasks/briefs/labeling/VERIFY-LS-B12-report.md`. Do NOT spawn
subagents.

## THE ROUND TABLE (D-115)

| Round | Landed | Verify | Blockers |
|---|---|---|---|
| LS-B12, the build | 8b940f8 | VERIFY-LS-B12: NOT-READY | F-1 (a status keyed on a substring of output that carries repo text); F-2 (tool side effects, to task #399) |
| LS-B12-R1, the first repair (D-031) | 631dc86 | this verify | ? |

If this verify finds a blocker, name its class: the SAME class as F-1 (a label's status decided by text that repo
content can supply), the class of F-3 (a value reaching a tool as an option), or another. A second repair needs
D-115's review first; the class you name decides what that review puts to the owner.

## ITEMS

1. **Premise.** Re-run the block below with `bash scripts/premise_block.sh` from the main tree. Stop CONTRACT-INVALID
   on any difference.
2. **F-1 closed?** Re-run your F-1 probes at the PIN (the removed-line route and the site-snippet route). Then attack
   the new marker, `"ranking": "no instrument answered` on the step's stdout or stderr:
   - can repo text, a path, a usage message, a traceback or an exception message put it on either stream RAW (not
     JSON-escaped)? jev_echo writes stderr too;
   - render()'s skeleton (a pack over its budget) and its last fallback (`{"tool", "truncated"}`): can a
     missing-tools pack reach either at the step's budget? The builder measured 3,060 characters at most and a
     682-character skeleton at `BUDGET_MIN`;
   - does the missing-tools case still read unmapped, exit 1, on a real removed line (your PATH farm)?
3. **F-8 closed?** Your four nothing-to-echo cases read ok, exit 0, and the print says why. The builder's NOT done 8:
   rg present with nothing to search plus graft unmapped still reads "rg-and-graft unavailable". Grade it.
4. **The sweep.** The builder's table (report, item 3):
   - `cbm`: the marker is now `{"error":"project not found`. Can a result row or stderr carry it raw?
   - `changes`: a new probe step (`node .gitnexus/run.cjs --version`) carries the launch marker, and the scope steps
     `need` it and carry none. Does a heading that holds the old marker now read ok? Does a runner that cannot launch
     still read unmapped? What does a probe that launches while the scope step fails read?
   - ripwire and sentrux keep the bare marker (the builder's NOT done 4: only a tracked path could forge it). Grade it.
5. **F-3 closed?** graft `ask [--in S] -- <text>`, GitNexus `query --repo . -- <text>` (through `.gitnexus/run.cjs`),
   cbm `--project=<slug> --query=<text>`. Your three cases per tool, end to end through `locate` and through the box
   (your World harness). `search_text` is unchanged (a test pins it byte-identical): confirm. Check the builder's
   table of every other call that passes a value to a tool. NOT done 5 (whether npx, pnpm dlx or bunx pass `--` on):
   measure it if the network cut allows, or say why not.
6. **No regression.** The other labels read as at 74285a5 on the same inputs, except where the repair meant a change.
   The catalog keeps all fourteen stacks under 4,000 characters (the builder: 3,769).
7. **The builder's NOT done list (1 to 8):** grade each. Items 1 and 2 were done at landing (the skill copy synced,
   the manifest regenerated): check them at the PIN.
   Also grade the four advisory tells the landing commit's anti-pattern screen printed: AP-51 on
   `tests/test_jev_context.py`; AF-AP-115 on `tests/test_jev_context.py` and `tests/test_stack.py`; AF-AP-175 on
   `tests/test_stack.py`.
8. **Mutation.** Re-run the builder's 14 mutants (its driver is in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/lsb12r1-lane/`)
   and your own new ones. Driver control first (AF-AP-223); bytecode off and a cleared `__pycache__` per mutant
   (AF-AP-192).
9. **Gates**, each call under 10 minutes, `--basetemp` as a pytest argument outside every work tree, counts pasted
   from `scripts/test_summary.sh`: the six files `tests/test_stack.py tests/test_session_hooks.py
   tests/test_search_intercept.py tests/test_ls_req.py tests/test_jev_context.py tests/test_jev_locate_echo.py`
   (`6 files set=b0ad308a6f97`) twice; `tests/test_vendored_manifest.py -k
   test_committed_manifest_matches_fresh_generation` once.
10. **The blocking predicate (D-034)** on every finding, and a GATE RECOMMENDATION; the coordinator owns the gate.

## WHERE YOU WORK

A detached worktree at the PIN under your scratch (hooks off), removed before you report; your tiny worlds and
private HOMEs as before. Never the shared tree.

Beside you: the K2 re-scoped build (a sandbox builder in its own worktree, on `scripts/filepacks.py` and
`scripts/codemap.py`) and the scrubber's option A build on the PC. A real cbm run can read FAILED on a cache-root
conflict with another lane's daemon (your F-11). Never stop a daemon you did not start; say so and go on.

## STANDING RULES

- No git write in the shared tree (a worktree add and remove, hooks off, is the one exception); no `git fetch` in the
  shared repo; no outward action; no PC bridge; never register a hook.
- Never read a secret file (`.pc-bridge.env`, any `*.env`, any key file). In any real transcript, read only `text`
  blocks, `tool_use` inputs and record types, never a `thinking` block, and print only counts, bytes and ids.
- Measure network behavior only under `unshare --net`.
- Never a top-level `cd` (AF-AP-249): `git -C`, absolute paths or a `( cd … )` subshell.
- A long gate in ONE foreground call; stamps from `date -u`; commits cited by origin id or subject.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- Stop every process you start before you report, the codebase-memory daemon included. Kill by pid only, found with an
  anchored pattern (`pgrep -f '^python3 …'`): the harness's wrapper shell for a background task carries the whole
  command text.

## REPORT

Return the whole report as your final message: the premise re-run; per item its evidence, each claim tagged
reproduced, static or inferred; the finding inventory with no severity filter; the gates; the mutants; the blocking
predicate per finding; the class of each blocker; the recommendation; deviations; cleanup.

## PREMISE — MEASURED at authoring (2026-09-30, main tree; PIN origin 631dc86)

```
$ git rev-parse 631dc86
631dc865e3044ea1f8b8372b6240207dec9712ec
$ git merge-base --is-ancestor 631dc86 origin/claude/soundbox-kit-migration-iz1jwf && echo PIN-is-on-origin
PIN-is-on-origin
$ git diff --name-only 631dc86 HEAD -- scripts/stacks.toml scripts/jev_echo.py scripts/jev_context.py scripts/jev_locate.py scripts/stack.py tests/test_stack.py tests/test_jev_context.py tests/test_jev_locate_echo.py tests/test_session_hooks.py tests/test_search_intercept.py tests/test_ls_req.py .claude/skills/box-and-labels/SKILL.md .agents/skills/box-and-labels/SKILL.md | wc -l
0
$ for f in scripts/stacks.toml scripts/jev_echo.py scripts/jev_context.py tests/test_stack.py tests/test_jev_context.py tests/test_jev_locate_echo.py .claude/skills/box-and-labels/SKILL.md .agents/skills/box-and-labels/SKILL.md; do printf '%s %s\n' "$(git show 631dc86:$f | sha256sum | cut -c1-16)" "$f"; done
6805bdf1539c93e2 scripts/stacks.toml
be644c8f7f8568ea scripts/jev_echo.py
36130ab90683ae35 scripts/jev_context.py
45e605b334b96aa4 tests/test_stack.py
593ea3bcf688b6b2 tests/test_jev_context.py
2bf6399ff5d98281 tests/test_jev_locate_echo.py
3f49116282c3689a .claude/skills/box-and-labels/SKILL.md
3f49116282c3689a .agents/skills/box-and-labels/SKILL.md
$ git show 631dc86:tasks/briefs/labeling/LS-B12-R1.patch | sha256sum | cut -c1-16
100457db934324bb
$ git diff --stat 74285a5 631dc86 -- scripts/ tests/ .claude/skills/box-and-labels/ .agents/skills/box-and-labels/ | tail -1
 8 files changed, 471 insertions(+), 88 deletions(-)
$ git show 631dc86:scripts/stacks.toml | grep -n 'unmapped_if'
10:# unmapped_if: their wrappers print "<name>_review: <bin> missing — run scripts/setup.sh" and exit 0 when the binary
169:unmapped_if = "missing — run scripts/setup.sh"
316:unmapped_if = "missing — run scripts/setup.sh"
487:unmapped_if = "missing — run scripts/setup.sh"
497:unmapped_if = "missing — run scripts/setup.sh"
565:unmapped_if = '{"error":"project not found'
603:unmapped_if = "gitnexus runner: could not launch"
682:# that does not exist exits 64. No unmapped_if: its registry and quirk instruments answer in every checkout of this
735:unmapped_if = '"ranking": "no instrument answered'
$ git show 631dc86:scripts/stacks.toml | grep -n 'jev_echo.py'
708:# task #385: scripts/jev_echo.py in its plain order, after a fix: the lines the diff's code hunks remove are the
714:# which jev_echo.py writes only when the diff removes code lines and no instrument answered (rg and graft missing). A
717:summary = "after a fix: other sites like the lines it removed, from jev_echo.py (rg and graft) in the plain lexical order"
725:# box, which jev_echo.py opens and reads); word refuses the '/' of a patch path or of a remote ref.
732:argv = ["python3", "scripts/jev_echo.py", "--diff", "{diff}", "--order", "lexical", "--no-jev-log", "--json"]
$ git show 631dc86:scripts/jev_echo.py | grep -n 'no instrument answered' | cut -c1-120
43:# The ranking when the diff removes code lines and no instrument answered. stacks.toml's fix-echo step runs this
46:NO_ANSWER = ("no instrument answered: each one is unmapped or had nothing to search (see the notes), so no site is "
$ git show 631dc86:scripts/jev_context.py | grep -n '"ask"\|"query",\|--query=' | cut -c1-140
457:    argv = (ctx.tools["graft"] + ["ask"] + (["--in", ctx.scope] if ctx.scope else [])
469:    rc, out, reason = run_tool(ctx.tools["node"] + [".gitnexus/run.cjs", "query", "--repo", ".", "--",   # as graft
495:    argv = ctx.tools["cbm"] + ["cli", "search_graph", "--project=" + ctx.slug, "--query=" + search_text(question, toks)]
515:            rc, out, reason = run_tool(ctx.tools["crg"] + ["query", "callers_of", name], ctx.root, budget.left())
$ python3 scripts/stack.py catalog | python3 -c "import sys;t=sys.stdin.read();print(len(t), sum(1 for l in t.splitlines() if l[:1].islower()))"
3769 14
$ bash scripts/pc_suite.sh set-id -- tests/test_stack.py tests/test_session_hooks.py tests/test_search_intercept.py tests/test_ls_req.py tests/test_jev_context.py tests/test_jev_locate_echo.py
6 files set=b0ad308a6f97
```
