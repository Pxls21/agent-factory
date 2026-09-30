# VERIFY-LS-B12: attack the five plain labels (task #385; D-111, D-113, D-114)

Role: a sandbox adversarial-verifier (Opus 5.5). PIN: e2f4f08 ("K2 round 4 landed ...", the commit after 8b940f8,
"LS-B12 landed ..."; CI ran on e2f4f08 and covers both, and K2 round 4 changed none of the LS-B12 files). Do NOT spawn subagents. Return the
whole report as your final message (your hand-back); write no report file.

## WHAT LANDED

Five stacks in `scripts/stacks.toml`, each a read-only label the chat box can run (D-113, D-114): `cbm`
(codebase-memory's graph search), `changes` (GitNexus change detection, one step per scope, a partial or capped first
line as the headline), `why` (`scripts/why.sh`), `locate` (`scripts/jev_locate.py`) and `fix-echo`
(`scripts/jev_echo.py`), the last two in their plain lexical order with `--no-jev-log`. Tests in `tests/test_stack.py`;
the catalog's rated list in `tests/test_session_hooks.py` (the builder's one-line fix, applied at the landing); five
rows in skill `box-and-labels`; CLAUDE.md's labels line. The contract: `tasks/briefs/labeling/LS-B12-brief.md`. The
builder's report of record: `tasks/briefs/labeling/LS-B12-report.md` (read the coordinator note, then its NOT DONE and
DISCREPANCIES; every claim is a hypothesis). The labels run from the Stop hook when a box asks (D-111: no box runs a
shell or a script), so a label's side effect happens outside the permission checks: that is why the rules of skill
`label-authoring` matter here.

Known and open (task #399), not findings to re-derive: the builder's D2 (graft's `ask` refreshes a stale graph by
default and writes graft's gitignored caches into the tree, from `find`, `locate` and `fix-echo`), D3 (python3 steps
write `scripts/__pycache__`), and the cbm daemon that outlives its step. Measure only what they do NOT cover.

## ATTACK (report every observation; no severity filter)

1. **Premise.** Re-run the block below with `bash scripts/premise_block.sh` from `/home/user/agent-factory`; on a
   difference, stop and report CONTRACT-INVALID with the diff.
2. **Writes outside the run directory** (skill `label-authoring`: nothing written outside the run dir). For each of the
   five labels, measure every write (`strace -f -e trace=%file`, or `find -newer` over the tree, `$HOME` and `/tmp`)
   with a warm graph and a stale one: any write that D2, D3 and the cbm daemon do not cover (the tree, `.gitnexus/`,
   codebase-memory's cache, `$HOME`, `/tmp`). Also a label run while another label or a commit's post-commit refresh
   runs.
3. **Run nothing it should not (D-111).** Every way to put a parameter into a tool's argument vector as more than one
   element or as an option: a leading `-`, `--`, an `=`-joined option, a newline, NUL, a look-alike character, a very
   long value, for `q`, `file`, `fn`, `scope`, `base` and `diff`. Then each tool's own parsing of the value it gets:
   `scripts/why.sh` with `file` and `fn` (does it pass them to `git log -L` or a grep as a pattern?), GitNexus
   `detect-changes --base-ref` (a value that names a file, a ref such as `HEAD@{...}`), `jev_echo.py` with `diff` (a
   path inside the tree that is not a diff; a symlink out of the tree), `jev_locate.py` and cbm with `q`.
4. **Ok with the tool missing, or unmapped when it answered.** Each `unmapped_if` against the tool's real
   missing-tool text; a tool present but broken (the builder's cbm cache-root conflict reads FAILED: is that right?);
   `why` without GitNexus (reads ok with its impact section silently gone: the builder's adjacent defect); `locate`'s
   missing `answered: none` guard (its NOT DONE 6). And `.gitnexus/run.cjs`'s `gitnexus@latest` fallback (the
   builder's adjacent defect): can `changes` or `impact` fetch and run an unpinned package from npm in this container?
   Measure it with the network cut (`unshare --net`); never let it fetch.
5. **`changes`' honesty.** A partial or capped result is its headline, and `No changes detected.` covers only symbols
   the index holds (the catalog note). Does any run read ok while the index is stale or the listing is cut, with
   nothing in the output that says so? A label's output is evidence, never a verdict: judge it by that rule.
6. **Through the box.** Run each label through `scripts/ls_req.py`'s parser and `scripts/stack.py` the way LS-B10's
   tests do (a temp state directory, never the live `.jev/`): the body parameter of `cbm` and `locate` (the registry
   now names a body for five stacks), a two-line body, the parameters set twice, an unknown key.
7. **The catalog and ratings.** The catalog stays under 4,000 characters with 14 stacks (the builder measured 3,729);
   what happens at the next label, and does the catalog drop whole stacks as its test says? `rate` on the four rated
   labels, and a rating for `changes` (not rated) refused with its exact message.
8. **Mutation.** Re-run the builder's driver from its scratch
   (`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/lsb12/mutate.py`, its last results in
   `lsb12/mutants/results.txt`; copy it into your own scratch before you run it), its control first
   (AF-AP-223: a `--basetemp` parent that no longer exists makes every mutant error at setup and read KILLED), and add
   mutants for clauses its tests may miss.
9. **The commit hook's screen tells at the landing** (advisory; printed by the pre-commit AP screen): AF-AP-115 (an
   executable resolved from the caller's PATH, `shutil.which`) and AF-AP-175 (a quoted HEAD passed to git), both in
   `tests/test_stack.py`. Say for each whether it is real, with the lines.
10. **Gates at the PIN**, in your own worktree, `--basetemp` as a pytest ARGUMENT outside every work tree, counts
    pasted from `scripts/test_summary.sh` with set ids, each call under 10 minutes: `tests/test_stack.py
    tests/test_session_hooks.py tests/test_search_intercept.py tests/test_ls_req.py` (`4 files set=d9c691f4f8de`).
11. **A gate recommendation** under D-034's blocking predicate (MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY /
    CONTRACT-INVALID), each blocking finding with its reproduction command. A label that runs a command it should not,
    or writes outside its run directory beyond the known D2 and D3, counts as core-blocking.

## STANDING RULES

- A clean detached worktree at the PIN under your scratch dir (`git worktree add --detach`, hooks off), removed at the
  end; no git write in the shared tree (a worktree add and remove is the one exception); no outward action, no PC
  bridge, no subagent.
- Run labels with `--tree <your worktree>` and `--log-dir` under your scratch, never the live `.jev/`. Never touch
  `/home/user/.claude/settings.json`, the repo's `.claude/settings.json` or `scripts/install_session_hooks.py` in the
  shared tree, and never run `scripts/install_session_hooks.py`.
- Never read a secret file (`.pc-bridge.env`, any `*.env`, any key file); a secret in a test is a fake built at run
  time. From transcripts, read only `text` blocks, `tool_use` inputs and record types, never a thinking block; print
  only counts, bytes and ids.
- The box characters are not ASCII: build test strings in code (`chr()`), and check each written file
  (`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0).
- A long gate in ONE foreground call; stamps from `date -u`; commits cited by origin id or subject.
- Never a top-level `cd` (AF-AP-249): use `git -C`, absolute paths or a `( cd … )` subshell. Never `pkill -f` a pattern
  your own command line matches; stop every process you start, by pid (the cbm daemon included).
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- This is defensive testing of the owner's own tooling: each probe is a bound to measure, never an exploit.

Head the report "## VERIFY-LS-B12" with a line "Written <date -u stamp>".

## PREMISE — MEASURED at authoring (2026-09-30, sandbox main tree; PIN origin e2f4f08)

Printed by `bash scripts/premise_block.sh` from the sandbox main tree. Every line reads committed objects at the PIN
(the last line prints a set id from path strings). Expected to differ: nothing; on any difference, stop and report
CONTRACT-INVALID with the diff.

```
$ git merge-base --is-ancestor e2f4f08 HEAD && echo e2f4f08-is-an-ancestor-of-HEAD
e2f4f08-is-an-ancestor-of-HEAD
$ git log -1 --format=%s e2f4f08 | cut -c1-60
K2 round 4 landed: provenance by blob, the redesign round (t
$ git log -1 --format=%s 8b940f8 | cut -c1-60
LS-B12 landed: five more plain labels, cbm, changes, why, lo
$ git diff --stat 8b940f8 e2f4f08 -- scripts/stacks.toml scripts/stack.py tests/test_stack.py tests/test_session_hooks.py .claude/skills/box-and-labels/SKILL.md CLAUDE.md | wc -l
0
$ git show e2f4f08:scripts/stacks.toml | sha256sum | cut -c1-16
07a3bc500c25927d
$ git show e2f4f08:scripts/stack.py | sha256sum | cut -c1-16
ef819f69430d7459
$ git show e2f4f08:tests/test_stack.py | sha256sum | cut -c1-16
4190d5e59d8281fd
$ git show e2f4f08:tests/test_session_hooks.py | sha256sum | cut -c1-16
b6ecdf51954cdc6f
$ git show e2f4f08:tasks/briefs/labeling/LS-B12.patch | sha256sum | cut -c1-16
3e844cc909baaa2d
$ git show e2f4f08:scripts/stacks.toml | grep -n '^\[stacks\.\(cbm\|changes\|why\|locate\|fix-echo\)\]$'
545:[stacks.cbm]
574:[stacks.changes]
638:[stacks.why]
675:[stacks.locate]
703:[stacks.fix-echo]
$ git show e2f4f08:scripts/stacks.toml | grep -c '^body *='
5
$ ls /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/lsb12/mutate.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/lsb12/mutants/results.txt | wc -l
2
$ bash scripts/pc_suite.sh set-id -- tests/test_stack.py tests/test_session_hooks.py tests/test_search_intercept.py tests/test_ls_req.py | tail -1
4 files set=d9c691f4f8de
```
