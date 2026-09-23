# C1-R1 — the ONE focused repair of VERIFY-C1 on the verify-command classifier port (`scripts/verify_command.py`)

**Role:** `code-implementer`, IN THE SANDBOX, no worktree (a disjoint boundary in the shared tree). Do NOT spawn subagents.
**D-031 key:** component C1 · contract `tasks/briefs/canny/C1-brief.md` + AMENDMENT C1-A2 below · V digest `8420e9a202de6afb`.
This is the one repair VERIFY-C1 buys; the next round is a targeted verify, then residue goes to issues.

**Boundary (touch ONLY these):** V = `scripts/verify_command.py`, T = `tests/test_verify_command.py`, and your report
`tasks/briefs/canny/C1-R1-report.md`. Two other lanes are LIVE in the same working tree (E3: S0-05 files; VERIFY-J1-2-R1:
`src/agent_factory/decisions/`, `tests/test_decisions_ledger.py`): never `git stash`, `checkout`, `restore`, `add`, `reset` or
`commit` there, and never touch their files. Canny (`/home/user/qkal/canny`) is STATIC READING ONLY: never run, build,
install, import or require it. Canny's frozen tables in T (the 27 rows, the 11 × 14 HIDES, the 11 × 13 KEEPS, the
override) keep their expected answers: never edit one.

**Inputs:** VERIFY-C1's report `tasks/briefs/canny/VERIFY-C1-report.md` (NOT-READY on F2; F1 returned as a CONTRACT-DEFECT;
its §"The closing rules, MEASURED" and §"The CONTRACT-DEFECT amendment I propose" are the design you implement).

## PREMISE — MEASURED at authoring (2026-09-23 05:3xZ, sandbox, /home/user/agent-factory@3f531c4)

```
$ git diff --stat ea9538a 3f531c4 -- scripts/verify_command.py tests/test_verify_command.py
(empty = byte-identical)
8420e9a202de6afb 273 scripts/verify_command.py
a9aedce65126da71 302 tests/test_verify_command.py
$ bash scripts/pc_suite.sh set-id -- tests/test_verify_command.py
1 files set=d9bd6dad2d0e
$ (cd /tmp && /root/venv-agent-factory/bin/python -m pytest /home/user/agent-factory/tests/test_verify_command.py -q -p no:cacheprovider --basetemp=/tmp/c1r1p/bt)
45 passed in 0.24s
$ the six inline regex calls without re.ASCII (V:7 claims every pattern carries it)
V:117  bare = re.sub(r'"[^"]*"|\'[^\']*\'', "", command)
V:119  bare = re.sub(r"(^|(?<!\\)\s)#[^\n]*", r"\1", bare)
V:140  r"(?:^|[;&\n])\s*set\s+([+-])\w*o\s+pipefail\b", bare
V:145  segments = [s.strip() for s in re.split(r"[;\n]", bare)]
V:163  if re.search(r"(?<!>)&(?!>)", part):
V:197  if re.search(r"(?<!\|)\|(?!\|)(?!\s*tail\b)", bare):
$ /usr/bin/python3 shapes.py <stubdir>   (the script is below; every check binary stubbed to `exit 3`; bash under env -i)
H1    port=counts           port_rc=0 bash_rc=0  'pytest && false || true'
H1b   port=counts           port_rc=0 bash_rc=0  'pytest && echo ok || true'
H2    port=counts           port_rc=0 bash_rc=0  "trap 'exit 0' EXIT; pytest"
H3    port=counts           port_rc=0 bash_rc=0  'set\xa0-o pipefail; pnpm test | tail'
H4    port=counts           port_rc=0 bash_rc=0  'set -o pipefail\r\npnpm test | tail'
H5    port=counts           port_rc=0 bash_rc=0  'echo \\\npytest'
H6    port=counts           port_rc=0 bash_rc=0  'exec true; pytest'
H6b   port=counts           port_rc=0 bash_rc=0  'coproc pytest'
CTRL  port=counts           port_rc=0 bash_rc=3  'pytest'
CTRL2 port=counts           port_rc=0 bash_rc=3  'set -o pipefail; pnpm test | tail'
$ the F3 discriminators through the API (the survivors N5, N10, N11, N13 of VERIFY-C1)
npm teste-acute -> True            # is_verify("npm testé")
pipefail | grep -- --help -> True  # is_verify("set -o pipefail; npm test | grep -- --help")
patterns=[] -> False               # is_verify("pnpm test", patterns=[])
echo set -o pipefail; ... | tail -> False   # is_verify("echo set -o pipefail; pnpm test | tail")
$ F4 / F5 through the CLI
/usr/bin/python3 scripts/verify_command.py -- python -c 'import pytest'      -> counts, rc=0   (three argv words)
/usr/bin/python3 scripts/verify_command.py -- "python -c 'import pytest'"   -> does-not-count, rc=1   (one word)
/usr/bin/python3 scripts/verify_command.py --pattern '' -- 'make build'     -> counts, rc=0
/usr/bin/python3 scripts/verify_command.py --pattern '' -- 'echo hi'        -> does-not-count, rc=1
```

The oracle script (copy it to your scratch dir; pin every interpreter by absolute path and keep the stub `PATH` inside
`env -i` for the one bash call, AF-AP-134):

```python
import subprocess, sys
PORT = "/home/user/agent-factory/scripts/verify_command.py"
STUB = sys.argv[1]  # a dir holding pytest, pnpm, npm, tsc: each `#!/bin/sh` + `exit 3`
shapes = [("H1", "pytest && false || true"), ("H1b", "pytest && echo ok || true"),
          ("H2", "trap 'exit 0' EXIT; pytest"), ("H3", "set -o pipefail; pnpm test | tail"),
          ("H4", "set -o pipefail\r\npnpm test | tail"), ("H5", "echo \\\npytest"),
          ("H6", "exec true; pytest"), ("H6b", "coproc pytest"),
          ("CTRL", "pytest"), ("CTRL2", "set -o pipefail; pnpm test | tail")]
for tag, cmd in shapes:
    port = subprocess.run(["/usr/bin/python3", PORT, "--", cmd], capture_output=True, text=True)
    sh = subprocess.run(["/usr/bin/env", "-i", f"PATH={STUB}:/usr/bin:/bin", "/bin/bash", "-c", cmd],
                        capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=10)
    print(f"{tag:5} port={port.stdout.strip() or port.stderr.strip()[:40]!s:16} port_rc={port.returncode} bash_rc={sh.returncode}  {cmd!r}")
```

## CONTRACT

**AMENDMENT C1-A2 (the coordinator's, 2026-09-23; adopts VERIFY-C1's measured "deviation 2", F1).** The port adds a
status-integrity pre-filter Canny does not have, because C2 consumes `is_verify` as a gate. `is_verify` returns False when,
in the command's executed text: **(a)** the last segment contains `||` anywhere, not only in the `&&`-part carrying the
check; **(b)** any segment begins with `trap`; **(c)** the command contains a carriage return; **(d)** the command contains
a backslash line continuation; **(e)** any segment begins with `exec` or `coproc`. The families this does NOT close are
declared, never hidden: H7 (a builtin or prefix assignment swallows the status: `export R=$(pytest)`), H8 (a shell function
shadows the check: `pytest(){ return 0; }; pytest`), H9 (the first-word denylist bypassed by a path, quoting,
`env`/`eval`/`builtin` or a backslash: `/bin/echo tsc`), and a here-doc terminator (`cat <<'pytest'`).

1. **R1 = VERIFY-C1 F2, the blocker.** Every regex in V carries `re.ASCII`, the six inline calls above included, or the
   module docstring names each exception with its reason; the docstring states the truth either way. Required result:
   H3 → does-not-count, CLI rc 1.
2. **R2 = C1-A2 (a)-(e).** Each rule has a T row per closed shape (H1, H1b, H2, H4, H5, H6, H6b → does-not-count) and a
   negative control (the rule removed → its row reds, compiled and collected, AF-AP-78). Canny's frozen tables stay
   answer-for-answer unchanged; show it by running the full T and by comparing every frozen-table answer before and after.
3. **R3 = the declared limits.** The module docstring lists H7, H8, H9 and the here-doc terminator as known hollow greens,
   with one example each. Each is pinned by one `pytest.mark.xfail(strict=True)` test that asserts the SAFE answer
   (does-not-count), so a later fix that closes one turns its test into an XPASS failure and forces the docstring update.
4. **R4 = VERIFY-C1 F3.** Four rows kill the survivors N5, N10, N11 and N13, asserting today's measured answers (above):
   True, True, False, False.
5. **R5 = VERIFY-C1 F4.** The CLI takes exactly ONE word after `--`; more than one → exit 2 with one stderr line.
6. **R6 = VERIFY-C1 F5.** An empty `--pattern` value → exit 2 with one stderr line.
7. **R7 = VERIFY-C1 F6.** An encoding failure on the `--with-pipefail` path exits 2 with one stderr line, never 1 (1 means
   "no rewrite"). Reproduce it first (a question, not measured at authoring); if it does not reproduce, say how you tried.
8. **R8 = VERIFY-C1 F8, F10, F11 (hygiene).** T:198's `"   echo tsc"` row aimed at the layer that really does the work
   (the `.strip()` at V:166), or drop the dead `^\s*` at V:80 with a row that shows `.strip()` covers it; one docstring
   sentence on the `ValueError` dialect consequence (F10); T:257 passes two argv words so it reaches
   `missing -- before COMMAND` (F11).

## Evidence demands

- The oracle script re-run on your final V: H1-H6b does-not-count (port_rc 1), CTRL and CTRL2 still count; paste the table.
- Gates: T twice from the repo root and once with `/tmp` as the working directory (AF-AP-130), each pasted verbatim with its
  set id; pyflakes on V and T; `python3 scripts/ap_screen.py scripts/verify_command.py` and `--tests
  tests/test_verify_command.py`.
- The mutant table: one negative control per new rule and per CLI refusal, each compiled and collected; the result and the
  test that killed it.
- Report `tasks/briefs/canny/C1-R1-report.md`: what changed (V/T lines), the tables above, DISCREPANCIES, NOT-done
  first-class. Cite as `V:<line>` / `T:<line>`, then run `python3 scripts/report_lint.py --min-refs 12 --map
  V=scripts/verify_command.py --map T=tests/test_verify_command.py tasks/briefs/canny/C1-R1-report.md --root .`; apply its
  `fix:` hints for at most three rounds, then paste the line and finish. Write the report incrementally.

**Standing do-nots:** no subagents; no outward-facing actions (no pushes, PRs, issues, comments); never touch the PC bridge;
touch only the boundary files; report adjacent defects, never fix them; stop and report if the tree contradicts this brief.
