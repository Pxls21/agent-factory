# LS-B12: five more labels (task #385; D-113 item 2, D-114)

Role: a new sandbox code-implementer lane (Opus 5.5). PIN: origin f8f1350. Authored 2026-09-30 by the coordinator. Read
first: skill `label-authoring` (the recipe: follow it step by step), skill `box-and-labels` (the table), the nine stacks
in `scripts/stacks.toml` (`find` shows a tool with a model mode run in its plain order), the docstring of
`scripts/stack.py`, and D-113, D-114 and D-115 in `docs/08_DECISION_LOG.md`. Do NOT spawn subagents.

## What the owner asked for

- D-113 (2026-09-29 21:09:10Z): "there should be like a word for each one, a word that represents a script that when
  found will trigger a script in a specific succession ... and it will use those variables".
- D-114 (2026-09-29 22:58:14Z): "... the 5 others that you'll add at 385, add them in the Claude MD as well."
- D-115 (2026-09-30 02:47:32Z): "yes, have jev powered labels". NOT this lane: task #391 builds that advisory class
  after you. Every label you add runs its tool's plain mode; `scripts/stack.py` still refuses a model call.

## CONTRACT

Five stacks in `scripts/stacks.toml`. Each is read-only and inward, calls no model, runs no shell, and each `argv` is a
list of words (the recipe's rules).

1. `cbm`: codebase-memory's graph search, `codebase-memory-mcp cli search_graph --project home-user-agent-factory
   --query <q>`. Input `q` (text, required); the box body is `q`; rated. The CLI starts a temporary daemon ("this
   command started a temporary CBM daemon"): measure whether any process outlives the step. If one does, say so and
   propose the fix; never leave one running.
2. `changes`: GitNexus change detection, `node .gitnexus/run.cjs detect-changes --scope <scope> --repo .`, with
   `--base-ref <base>` for scope `compare`. Inputs `scope` (a choice: all, staged, unstaged, compare; default all) and
   `base` (optional; used only with compare). No body; not rated (a check, like `ci`). A partial or truncated result is
   not a clean check (CLAUDE.md's GitNexus block): read the CLI's own output format and make the stack's output say so
   when it happens.
3. `why`: the chronology, `bash scripts/why.sh <file> [<fn>]`. Inputs `file` (path, required) and `fn` (symbol,
   optional). No body; rated.
4. `locate`: `python3 scripts/jev_locate.py --order lexical --no-jev-log <q>`, with `--in <scope>` when given. Inputs
   `q` (text, required) and `scope` (path, optional); the box body is `q`; rated.
5. `fix-echo`: `python3 scripts/jev_echo.py --diff <diff> --order lexical --no-jev-log`. Input `diff` (a commit id or a
   patch file path; choose the parameter type from `scripts/stack.py`'s types and say why). No body; rated.

For all five:
- The recipe's step 1 first: run each command by hand on the real tree (exit codes, output size, what it prints when
  its tool is missing), and paste what you measured. `ok_rc` comes from that measurement. A step whose tool can be
  missing carries `unmapped_if`, so a missing tool reads `unmapped`, never ok.
- Nothing written in the repo tree outside the run directory: measure each step (the files under the tree newer than a
  stamp file taken before the run). Writes under `$HOME` (tool caches, logs) are reported, not refused.
- No label named after a runner subcommand (`list`, `catalog`, `explain`, `rate`; VERIFY-LS-B11 F-13).

6. **The catalog keeps all fourteen stacks** under `CATALOG_CAP` (4,000 characters; past it, `stack.py catalog` drops
   whole stacks). It printed 2,704 characters at authoring. Shorten notes if you must, never drop a stack; paste the new
   size.
7. **Listing (D-114):** a row per new label in `box-and-labels`'s table, replacing its "Task #385 (backlog) adds five
   labels" paragraph; and the five words with what each runs in CLAUDE.md's labels line, replacing its "Task #385 adds
   five" sentence.
8. **Tests** in `tests/test_stack.py`: the committed registry loads with fourteen stacks; `explain` shows each new plan;
   per new stack a negative control that refuses a bad input with its exact message; `cbm` reads `unmapped` when its
   binary is missing (fake it the way the existing tests fake a missing tool).
9. **One real run of each new label** (the recipe's step 4), each run's sections pasted, capped. `python3
   <W>/scripts/stack.py --tree /home/user/agent-factory <label> ...` runs your registry against the main tree, whose
   graphs are indexed; say where each run's directory went.

## WHERE YOU WORK

In a worktree at the PIN under your scratch
(`git -C /home/user/agent-factory -c core.hooksPath=/dev/null worktree add -q --detach <W> f8f1350`), never the shared
tree. Your one shared-tree write is your deliverable, `tasks/briefs/labeling/LS-B12.patch` (`git -C <W> diff f8f1350`
over every file you change, new files included), which must apply at the PIN with `git apply --check`. Remove the
worktree before you report.

## BOUNDARY

- MODIFY, in your worktree only: `scripts/stacks.toml`, `tests/test_stack.py`, `.claude/skills/box-and-labels/SKILL.md`
  (the table and the task #385 paragraph), `CLAUDE.md` (the labels line only).
- CREATE: a script under `scripts/` only if a step needs new logic (the recipe's step 2), with its own tests.
- READ: `scripts/stack.py` (never change it; a schema change belongs to task #391), the five tools,
  `scripts/ls_req.py` (a box takes its label from this registry).
- NOT yours: `.claude/settings.json`, `scripts/install_session_hooks.py`, `/home/user/.claude/settings.json` (the LIVE
  session hooks, the chat box included), the live `.jev/`, `.agents/` (the coordinator syncs the skill copies at
  landing).
- Beside you: K2 round 4 (a sandbox builder in its own worktree, on `scripts/filepacks.py`, `scripts/codemap.py` and
  their tests) and SCRUB2-R1 round 5Q on the PC. Touch none of their files.

## GATES

In your worktree, each call under 10 minutes, twice, `--basetemp` as a pytest ARGUMENT outside every work tree, counts
pasted from `scripts/test_summary.sh` with set ids from `bash scripts/pc_suite.sh set-id -- <files>`: every test that
names a file you change (`python3 scripts/stack.py gate paths="<your files>" mode=plan graph=no` in your worktree lists
them; re-collect on the PIN, the coordinator states no count here), plus `tests/test_claude_md_lossless.py
tests/test_skill_frontmatter.py tests/test_system1_context.py` (the CLAUDE.md and skill readers), plus `bash
harness-ports/tests/test_context_mirrors.sh`. Mutation: a named mutant per new stack (a wrong flag, a missing
`unmapped_if`, a dropped `--order lexical`), each killed; your driver's control first (AF-AP-223), bytecode off and a
fresh copy or a cleared `__pycache__` per mutant (AF-AP-192).

## REPORT

Return the whole report as your final message: the premise re-run; per label what you measured by hand (step 1); files
with line counts and sha256; the patch's sha256 and `git apply --check` at the PIN; per contract item its pasted
evidence; the gates; the mutants; the catalog size; NOT done, first-class; DISCREPANCIES; your self-attack (how could a
label run something it should not, write outside its run directory, or read ok when its tool is missing?).

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

## PREMISE — MEASURED at authoring (2026-09-30, main tree; PIN origin f8f1350)

Printed by `bash scripts/premise_block.sh` from the main tree. The `git show` lines read committed objects at the PIN;
the last four read the container's tools. Nine stacks today; the two "Task #385" lines are the ones item 7 replaces;
`jev_locate.py` names `no-jev-log` twice (its flag and its help). The set id is `tests/test_stack.py` alone; re-collect
on the PIN. Expected to differ: nothing.

```
$ git merge-base --is-ancestor f8f1350 HEAD && echo f8f1350-is-an-ancestor-of-HEAD
f8f1350-is-an-ancestor-of-HEAD
$ git show f8f1350:scripts/stacks.toml | sha256sum | cut -c1-16
05ba1573b6212e7b
$ git show f8f1350:scripts/stack.py | sha256sum | cut -c1-16
ef819f69430d7459
$ git show f8f1350:tests/test_stack.py | sha256sum | cut -c1-16
749d679db3b2d4eb
$ git show f8f1350:.claude/skills/box-and-labels/SKILL.md | sha256sum | cut -c1-16
2e9f240f996c66e0
$ git show f8f1350:CLAUDE.md | sha256sum | cut -c1-16
ff513317d6c86173
$ git show f8f1350:scripts/stacks.toml | grep -c '^\[stacks\.[a-z-]*\]$'
9
$ git show f8f1350:scripts/stack.py | grep -n '^CATALOG_CAP\|^STACK_KEYS'
93:STACK_KEYS = {"summary", "replaces", "outward", "rated", "params", "steps", "notes", "body"}
95:CATALOG_CAP = 4000        # the SessionStart catalog stays under this: the harness swaps a hook text over 10,000
$ git show f8f1350:CLAUDE.md | grep -n 'Task #385'
376:commit) · `harvest` (a finished lane's models, refusals, hand-back, report) · `ci` (the stage0-ci verdict). Task #385
$ git show f8f1350:.claude/skills/box-and-labels/SKILL.md | grep -n 'Task #385'
40:Task #385 (backlog) adds five labels: codebase-memory, GitNexus detect-changes, `scripts/why.sh`,
$ git show f8f1350:scripts/jev_echo.py | grep -n 'add_argument("--diff"'
286:    ap.add_argument("--diff", required=True)
$ git show f8f1350:scripts/jev_locate.py | grep -c 'no-jev-log'
2
$ git show f8f1350:scripts/why.sh | grep -n '^#   scripts/why.sh'
9:#   scripts/why.sh <file> [function_name]
10:#   scripts/why.sh scripts/validate-ledger validate
$ command -v codebase-memory-mcp node rg
/root/.local/bin/codebase-memory-mcp
/opt/node22/bin/node
/usr/bin/rg
$ test -f .gitnexus/run.cjs && echo gitnexus-cli-present
gitnexus-cli-present
$ bash scripts/pc_suite.sh set-id -- tests/test_stack.py | tail -1
1 files set=2ac01abb1067
```
