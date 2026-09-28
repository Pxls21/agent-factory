# LS-B9: the stack runner and the first eight stacks (task #339, D-103)

Authored 2026-09-28 15:0xZ by the coordinator. Lane: sandbox `code-implementer` (Opus 5.5).
Design of record: `docs/research/findings/labeling/LS-DESIGN-v2-2026-09-28.md` (§2 to §5). Read it first.

## WHY

The owner (D-103): the tools are many, and "instead of having you or jev try to manage that and try to discern which
situation to use it in each time ... Create script stacks ... and then tie them to specific labels"; the stack runs
"these tools based on the variables you put in and then just give you the output", so "it'll use the scripts, the tools
in the correct way each every time". A stack is a named, fixed sequence of instrument calls with typed parameters, kept
in a committed registry and run by one runner, in ONE tool call. `scripts/lane_context.sh` is the precedent (one
command, every instrument, `unmapped — <tool> unavailable` when one is absent); this lane generalizes it.

## CONTRACT

1. **The CLI.** `python3 scripts/stack.py` with these forms:
   - `list`: the catalog, one line per stack (label, parameters, summary).
   - `explain <label> key=value …`: the resolved plan (each step's argv, shell-quoted; a chained input shown as
     `<lines of STEP>`). It runs nothing and writes no record.
   - `<label> key=value … [--rate RUN[.STEP]=REL/USE]…`: run the stack.
   - `rate RUN[.STEP]=REL/USE …`: ratings only (REL and USE are 0 to 3).
   - Options: `--tree PATH` (the target tree; default: the git toplevel of the current directory; must be a toplevel);
     and, for tests only, `--registry PATH`, `--log-dir PATH`, `--transcript-root PATH`.
   - A parameter is a `key=value` token. An unknown key, a missing required key or a repeated key is refused with
     exit 2 and a message naming the known keys.
2. **The registry, `scripts/stacks.toml`.** Copy this shape; do not redesign it.
   ```toml
   version = 1                          # any other value: exit 3

   [tools]                              # tool name -> candidate paths; the first that exists is used
   code-review-graph = ["/root/venv-crg/bin/code-review-graph", "code-review-graph"]

   [stacks.<label>]                     # label: ^[a-z][a-z0-9-]{1,23}$
   summary = "<one line>"
   replaces = "<the hand sequence it replaces>"
   outward = false                      # a stack with true is refused at load (exit 3); wave 1 has none

   [stacks.<label>.params.<name>]       # name: ^[a-z][a-z0-9_]{0,23}$
   type = "path"                        # path paths symbol symbols text word words agent choice int
   required = true
   default = "…"                        # optional; it must itself validate
   choices = ["…"]                      # choice only
   split_from = "<text param>"          # words only: derived, the words of that text parameter

   [[stacks.<label>.steps]]
   id = "<step id>"                     # ^[a-z][a-z0-9_]{0,23}$, unique in its stack
   argv = ["prog", "{param}", "{list*}", "{list*:-e}", "{opt?:-q}", "{@step*}", "--out={run}/x.md"]
   group = 1                            # groups run in ascending order; steps of one group run in parallel
   timeout = 60                         # seconds, 1 to 3600
   cap_lines = 40                       # lines printed; the full output is saved
   ok_rc = [0]                          # the exit codes that count as success
   required = true                      # a failed, timed-out, unmapped or skipped required step: the run exits 1
   when = { mode = "run" }              # optional: run only if each named parameter matches ("*" = set, "" = unset)
   repeat = "{runs}"                    # optional: run N times; the sections are numbered
   foreach = "<list param>"             # optional: run once per element, with {each}
   ```
3. **Placeholders.** `{name}`: a scalar parameter or built-in, allowed inside a longer element (`--out={run}/x.md`).
   `{name*}`: a list, spliced as separate elements; the element must be exactly the placeholder. `{name*:FLAG}`: each
   element preceded by FLAG. `{name?:FLAG}`: FLAG and the value when the parameter is set, nothing when unset.
   `{@step*}`: the non-empty stdout lines of a step in an earlier group, each validated as a `path`; if that step
   failed, timed out, was unmapped or printed nothing, this step is SKIPPED with the reason. Built-ins: `{tree}`, `{run}`
   (this run's output dir), `{main}` (the main tree), `{head}`, `{branch}`, `{each}`, and `{transcript}` for an `agent`
   parameter (exactly one match of `<transcript-root>/*/*/subagents/agent-<id>.jsonl`, default root
   `/root/.claude/projects`; zero or two matches: exit 2).
4. **Types.** `path`: resolves (realpath) inside the target tree, does not begin with `-`, and is not on the deny list:
   `.pc-bridge.env`, any `*.env`, anything under `.git/`, `/root/.codiv/`, `/root/.claude/projects/` (except through
   `{transcript}`), `~/.config/qwen-*`, `/root/.config/session-export/`. It need not exist (a deleted file can be
   gated). `paths`, `symbols` and `words` are comma-separated lists of `path`, `symbol` and `word`. `symbol`:
   `^[A-Za-z_][A-Za-z0-9_.:]{0,127}$`. `word`: `^[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}$`. `text`: 1 to 500 characters, no
   NUL, no newline, not beginning with `-`. `agent`: `^a[0-9a-f]{16}$`. `int`: `^[0-9]{1,6}$`. Every check runs before
   any step does.
5. **Execution.** Each step runs with `cwd` = the target tree, as an argument vector (never a shell, never
   `shell=True`), in its own session (`start_new_session=True`). A step past its timeout: SIGTERM to its process group,
   SIGKILL 3 s later, section status `TIMEOUT after N s`. argv[0] that names a `[tools]` entry, or a program or script
   that does not exist: `unmapped — <tool> unavailable`, never a silent blank. The whole print is capped at 9,000
   characters (sections shortened from the largest; the header says so). Exit codes: 0 every required step passed; 1 a
   required step did not; 2 a usage or parameter refusal; 3 a registry or log error.
6. **Records.** The log dir is `<main tree>/.jev/stacks/`, where the main tree comes from
   `git rev-parse --path-format=absolute --git-common-dir` (its parent), so a run from a worktree logs to the main
   tree (AF-AP-235's class). Each run gets a dir `s-<UTC yyyymmddTHHMMSSZ>-<6 hex>/` with one output file per step,
   and one JSON line in `runs.jsonl`: `v`, `run`, `ts`, `label`, `params`, `tree`, `head`, `rc`, and `steps` (per step:
   `id`, `argv`, `rc`, `status` of ok/failed/timeout/unmapped/skipped, `secs`, `bytes`, `sha256`, `out`). A rating
   appends `{"v":1,"rating":"RUN[.STEP]","rel":N,"use":N,"ts":…}`. Each line is one write under `flock` of
   `.jev/stacks/.lock`.
7. **Two helpers (CREATE).**
   - `scripts/gate_files.py PATH…`: prints, sorted and unique, one per line, every file under `tests/` named
     `test_*.py` and every file under `harness-ports/tests/` (tracked or untracked, never `__pycache__`, text files
     only) whose text contains a given path string, plus each given path that is itself such a file. It is the
     project rule "a changed file's gate includes every test that names its path" as a script.
   - `scripts/handback_extract.py --transcript PATH --out FILE`: streams the subagent JSONL, never whole; writes the
     `message` of the last `SubagentHandback` tool_use to FILE with control tags neutralized (`<` becomes `<\` before
     `system-reminder`, `function_calls`, `invoke`, `parameter` and `antml:` tags); prints `handback: found|absent`,
     its bytes, the neutralized count and a sha256 prefix. It never prints the message and never reads a `thinking`
     block's text.
8. **The eight stacks, wave 1.** Before you write a step, verify the instrument's interface (run its `--help` or read
   its usage) and paste the form that works. Where the plan below is wrong about an interface, follow the instrument
   and name the change under DISCREPANCIES.

   | Label | Parameters | Steps (group: step = argv) |
   |---|---|---|
   | `harvest` | `agent` (agent, required), `report` (path) | 1: `models` = `python3 scripts/hiccup_scan.py --transcript {transcript} --out {run}/hiccup.md`; `handback` = `python3 scripts/handback_extract.py --transcript {transcript} --out {run}/handback.md`. 2: `agent_row` = `grep -F "\| {agent} \|" {run}/hiccup.md`; `lint` = `python3 scripts/report_lint.py --root {tree} {report}` when report is set, else on `{run}/handback.md`; `sha` = `sha256sum {report}` when set |
   | `gate` | `paths` (paths, required), `mode` (choice plan/run, default plan), `runs` (choice 1/2, default 2) | 1: `tests` = `python3 scripts/gate_files.py {paths*}`. 2: `setid` = `bash scripts/pc_suite.sh set-id -- {@tests*}`. 3: `run` = `bash scripts/test_summary.sh {@tests*}`, when mode=run, repeat `{runs}`, timeout 1800 |
   | `ctx` | `files` (paths, required), `q` (text), `sym` (symbols) | 1: `pack` = `bash scripts/lane_context.sh {q?:-q} {sym*:-s} -o {run}/ctx.md {files*}` (print the pack, capped; verify how the script writes it) |
   | `impact` | `sym` (symbol, required) | 1, in parallel: `gitnexus` = `node .gitnexus/run.cjs impact {sym} --direction upstream --repo .` (timeout 120); `crg_callers` = `code-review-graph query callers_of {sym}`; `crg_tests` = `code-review-graph query tests_for {sym}`; `ripwire` = `bash scripts/ripwire_review.sh edit-check {sym}` |
   | `find` | `q` (text, required), `words` (words, split_from q) | 1, in parallel: `graft` = `graft ask {q}`; `rulings` = `python3 scripts/owner_rulings.py {words*}`; `chat` = `python3 scripts/chat_find.py {q} --hits 5`; `registry` = the AF-AP registry rows (lines starting `\| AF-AP-`) in `docs/INCIDENT-LOG.md` that contain any of the words, case-insensitive (git grep's `--and` grouping; verify) |
   | `premise` | `files` (paths, required) | 1, in parallel: `tracked` = `git ls-files --error-unmatch -- {files*}`; `sha` = `sha256sum -- {files*}`; `lines` = `wc -l -- {files*}`; `last` = `git log -1 --format=%h %ci %s -- {each}`, foreach files |
   | `echo` | `pattern` (text, required), `roots` (paths, default `scripts,harness-ports,src,proofs,.claude/hooks,.github`) | 1: `code` = `rg -n --no-heading -e {pattern} -- {roots*}`; `files` = `rg -l -e {pattern} -- {roots*}`; `registry` = `git grep -n -i -E -e {pattern} -- docs/INCIDENT-LOG.md`. 2: `ap` = `python3 scripts/ap_screen.py {@files*}` |
   | `ci` | `branch` (word, default the current branch) | 1: `verdict` = `python3 scripts/ci_gate.py --branch {branch}`, ok_rc [0, 75] (75 = the verdict is not in yet) |

   Search steps whose "nothing found" exit is 1 (`grep`, `git grep`, `rg`) list 1 in `ok_rc`. No stack calls a model
   (KC-J1: no Laya or Jev in a gate) or takes an outward action.

Not in this lane: CLAUDE.md and its mirrors, the output-style files, any hook or settings file, the T2 chat form, the
wave-2 stacks, and any change to an existing script (the coordinator wires discovery after your verify).

## EVIDENCE DEMANDS

1. Premise: re-run the block below with `bash scripts/premise_block.sh`; stop and report CONTRACT-INVALID on a
   mismatch that matters.
2. The interface table: for each instrument a stack calls, the form you verified, pasted.
3. `tests/test_stack.py`, temp dirs and a temp registry of tiny real programs for the runner's rules (no stub of an
   instrument the claim depends on). Every test passes `--log-dir` under its own `tmp_path`: no test writes the repo's
   `.jev/`, on CI or here. Cases, each with its exact exit code or message, and each with a named mutant that makes it
   a FAILED test (AF-AP-223):
   - no shell: a `text` value holding `$(touch X)`, backticks and `;` reaches the program as one literal element and
     `X` is never created;
   - option injection: a `text` value `-rf` is refused, exit 2;
   - the deny list: each entry refused before any step runs (a marker step never runs);
   - a path outside the tree refused; a symlink out of the tree refused;
   - the process-group kill: a step that starts a grandchild and sleeps; after the timeout neither pid is alive;
   - `unmapped — <tool> unavailable` for a missing program, and the run's exit is 1 only when that step is required;
   - a chained step SKIPPED when its source failed or printed nothing;
   - one group's two 1-second steps finish in under 1.8 s together; groups run in order;
   - `when`, `repeat` and `foreach`;
   - the 9,000-character cap;
   - a run from a worktree logs to the main tree (make a temp repo and a worktree of it);
   - the record's fields; `--rate` and `rate` records; exit 2 for an unknown, missing or repeated key; exit 3 for a
     bad registry version and for an `outward = true` stack.
4. For each of the eight stacks: `explain` with sample parameters, pinned in a test (it runs anywhere, CI included);
   and a real run on this tree, pasted in the report with its wall time (capped output). Tests that need a sandbox-only
   instrument (graft, GitNexus, code-review-graph, ripwire, rg) skip with the reason when it is absent: CI runs
   `python -m pytest tests/ -q -rs` on ubuntu with Python 3.12 and has none of them. `premise` and `gate` in plan mode
   run in the test on the real tree; check that `scripts/pc_suite.sh set-id` needs no bridge env. For `harvest`, the
   test builds a small subagent JSONL (assistant records with a model, one `SubagentHandback` tool_use whose message
   holds a control tag) under a temp `--transcript-root`; your report adds one real run on
   `agent=a2f621e1d36efd61d` (a finished lane of this session; counts and the extracted file's sha256 only, not its
   text).
5. Gates: `bash scripts/test_summary.sh` twice on `tests/test_stack.py`, plus `tests/test_no_laya_in_gates.py`, plus
   every existing test that enumerates `scripts/` (find them: a grep of `tests/*.py` for a walk of that directory),
   with the set id from `bash scripts/pc_suite.sh set-id -- <files>`; `python3 -m pyflakes` rc 0 on every file you
   write; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0 for each.
6. NOT-done and DISCREPANCIES.

## BOUNDARY

- CREATE: `scripts/stack.py`, `scripts/stacks.toml`, `scripts/gate_files.py`, `scripts/handback_extract.py`,
  `tests/test_stack.py`, your report `tasks/briefs/labeling/LS-B9-report.md`.
- MODIFY: nothing.
- READ: everything else. Never write under `/root/.claude/`; runs of the real stacks write only to
  `.jev/stacks/` (git ignores `.jev/`).

## STANDING RULES

- No git writes, no PC bridge, no subagents, no outward-facing action.
- Never read a secret source (`.pc-bridge.env`, any `*.env`, `/root/.codiv/`, `~/.config/qwen-*`,
  `/root/.config/session-export/`); the runner's deny list exists for the same reason.
- The main tree holds two other lanes' files (listed in `.lanes-live`: SCRUB2-R1's five and LS-B7's six); touch only
  your boundary. `scripts/transcript_export.py` is mid-edit by another lane: do not import it.
- The disk is shared (about 1.6 GB free; the lane gate refuses below 1,500 MB): scratch under 100 MB in
  `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ls-b9/`; delete what you create there.
- Long commands in one foreground call, each under 10 minutes. Kill by pid only. Stamps from `date -u`, never typed;
  counts pasted from `scripts/test_summary.sh`. Never use an unquoted heredoc for text with backticks.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- If the harness refuses your report-file write, return the whole report as your final message.

## PREMISE — MEASURED at authoring (2026-09-28 15:0xZ, the main tree; `bash scripts/premise_block.sh`)

```
$ python3 -c 'import sys, tomllib; print(sys.version.split()[0], "tomllib ok")'
3.11.15 tomllib ok
$ grep -n -E 'python-version|python -m pytest tests/' .github/workflows/stage0-ci.yml
34:          python-version: '3.12'
46:        run: python -m pytest tests/ -q -rs   # -rs: every skip prints its reason (FU-4, VERIFY-I59-A)
60:          python-version: '3.12'
82:          python-version: '3.12'
101:          python-version: '3.12'
$ command -v graft sentrux ripwire rg node
/opt/node22/bin/graft
/root/.local/bin/sentrux
/root/.local/bin/ripwire
/usr/bin/rg
/opt/node22/bin/node
$ ls -la /root/venv-crg/bin/code-review-graph .gitnexus/run.cjs
-rw-r--r-- 1 root root 19564 Sep 26 09:39 .gitnexus/run.cjs
-rwxr-xr-x 1 root root   230 Sep  2 21:37 /root/venv-crg/bin/code-review-graph
$ sed -n '2,6p' scripts/test_summary.sh
# test_summary.sh — run pytest and print a mechanical summary line.
# Usage: scripts/test_summary.sh [pytest paths...]  (default: tests/)
# Prints:
#   pytest-exit: <exit code>
#   pytest-summary: <last non-empty output line>
$ grep -n 'set-id)' scripts/pc_suite.sh
121:set-id)
$ python3 scripts/hiccup_scan.py --help | head -3
usage: hiccup_scan.py [-h]
                      [--project-dir PROJECT_DIR | --transcript TRANSCRIPT]
                      [--limit-bytes LIMIT_BYTES] [--out OUT] [--jev]
$ python3 scripts/report_lint.py --help | head -3
usage: report_lint.py [-h] [--map MAP] [--rev REV] [--tolerance TOLERANCE]
                      [--root ROOT] [--min-refs MIN_REFS]
                      report
$ python3 scripts/owner_rulings.py --help | head -2
usage: owner_rulings.py [-h] [--log LOG] [--all] [--width WIDTH]
                        words [words ...]
$ python3 scripts/chat_find.py --help | head -2
usage: chat_find.py [-h] [--match {words,error}] [--order {lexical,jev}]
                    [--hits HITS] [--since SINCE] [--until UNTIL]
$ python3 scripts/ci_gate.py --help | head -2
usage: ci_gate.py [-h] --branch BRANCH [--origin-ref ORIGIN_REF] [--root ROOT]
                  [--runs-json RUNS_JSON] [--wait SECONDS]
$ python3 scripts/ap_screen.py --help | head -3
usage: ap_screen.py [-h] [--tests] [--s0-01] [--staged-shell] [--limit LIMIT]
                    [paths ...]

$ grep -n -E '^# *(usage|Usage)|^#   -' scripts/lane_context.sh | head -8
5:#   - graft skeleton of every changed file (symbols + line ranges, ~5% of the tokens of the file)
6:#   - graft ask for the question the brief poses (structural answer: callers / seams / resolution)
7:#   - per symbol: GitNexus impact (blast radius + risk), code-review-graph callers_of + tests_for,
9:#   - ripwire test-gate over the files (the tests to run + the UNTESTED blast radius)
10:#   - the anti-pattern registry screen over the WHOLE files (production → AP_SCREEN, tests → TEST_SCREEN)
$ grep -n -E 'edit-check\)|test-gate\)|callers\)' scripts/ripwire_review.sh | head -4
48:  callers)
60:  test-gate)
67:  edit-check)
$ ls scripts/stack.py scripts/stacks.toml scripts/gate_files.py scripts/handback_extract.py tests/test_stack.py
ls: cannot access 'scripts/stack.py': No such file or directory
ls: cannot access 'scripts/stacks.toml': No such file or directory
ls: cannot access 'scripts/gate_files.py': No such file or directory
ls: cannot access 'scripts/handback_extract.py': No such file or directory
ls: cannot access 'tests/test_stack.py': No such file or directory
[rc=2]
$ git check-ignore -v .jev/stacks/runs.jsonl
.gitignore:68:.jev/	.jev/stacks/runs.jsonl
$ git rev-parse --git-common-dir
.git
$ git -C /home/user/i59-landing rev-parse --git-common-dir
/home/user/agent-factory/.git
$ grep -c '' scripts/gate_files.txt
54
$ df -m / | tail -1
/dev/vda          258020 36314      1625  96% /
```

Two facts for you to handle, not to hide: `git rev-parse --git-common-dir` is relative (`.git`) in the main tree and
absolute in a worktree, hence `--path-format=absolute` (git 2.43.0 here); and `scripts/gate_files.txt` is the KC-J1
list of gate-defining files, a different thing from your `scripts/gate_files.py` (its walk covers `scripts/hooks/*`,
`.github/workflows/*.yml` and `proofs/*/check_*.py`, so your files need no entry there; `tests/test_no_laya_in_gates.py`
stays in your gate to prove it).
