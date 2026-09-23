# VERIFY-J1-0-R4 — the targeted verify of the never-a-gate screen's fourth round (task #184)

PIN: the post-push SHA of the local landing commit 5090671 ("J1-0-R4 landed (task #172; GATED-PENDING-VERIFY): …"); the dispatch
prompt names it. Read it with `git log --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf -8` and match the subject.
COMPONENT: `scripts/no_laya_in_gates.py` (S, the screen), `scripts/gate_files.txt` (L, the list), `tests/test_no_laya_in_gates.py`
(T). The builder's report `tasks/briefs/laya/J1-0-R4-report.md` is an INPUT TO ATTACK, not a truth.
LANE: verify-j1-0-r4 (sandbox; agent `adversarial-verifier` on the D-054 pin, in the SHARED tree, no worktree isolation). Honey
`full`: line-bounded findings, evidence anchors, SOLID/UNSURE. Do NOT spawn subagents.

WHY THIS LANE EXISTS: J1-0-R4 is GATED-PENDING-VERIFY (rule 0f). Its gates were the builder's own tests, its own 25 mutants and its
own 37 evasion shapes; the coordinator re-ran the tests and both screen modes in a clean worktree, which is a second run of the same
oracle, not an independent review. The screen runs in the pre-commit hook on every commit (`scripts/hooks/pre-commit:127`): a
fail-open lets a gate load or source unlisted code (the KC-J1 property: no Laya code in a gate, directly or through what a gate
runs); a false refusal blocks every commit on the branch.

CONTRACT (frozen): AMENDMENT 3, R4-1..R4-6, in `tasks/briefs/laya/J1-0-R4-brief.md` (section "The contract"), on top of AMENDMENT 2
in `tasks/briefs/laya/J1-0-R3-brief.md` (every rule there stands unless R4 replaces it), graded against the (B) section of
`tasks/briefs/laya/VERIFY-J1-0-R23-STAMP-report.md` (F-B1, F-B2). KNOWN, already filed as issue #37: F-A2, F-B3..F-B11, F-C1, F-C2 and
the INFO rows of that report. The builder claims it closed F-B9, F-B7, F-B11, F-B3's S10 spelling and part of F-B6 (report section
"Issue #37 findings closed incidentally"): verify each of those claims; report other issue-#37 findings as KNOWN, do not re-derive
them.

## Items (report EVERY observation; no severity filter; rank downstream)

1. PREMISE. Re-measure the block below on the PIN (the blob ids, the line map, the exception set, the list count, both screen modes,
   the gate run with its set id). A mismatch that changes an item is CONTRACT-INVALID for that item; say which.
2. R4-2, the shell lexer, by an instrument the builder did not use. The builder compared the scanner with `bash -n` plus a probe
   line after every line. Use a different oracle: for example, run each fixture under bash itself in a throwaway directory where the
   sourced file writes a marker (so bash's own execution says whether a `.`/`source` ran), or bash's `set -x` trace. NEW shapes,
   never the builder's S/X/BH/YH rows or its 37 evasion shapes: a here-string `<<<` (never a pending heredoc); two heredocs on one
   line (`cat <<A <<'B'`); a partly quoted delimiter (`<<E"O"F`); `<<-` with tab-indented bodies and delimiter; a heredoc opened
   inside `$( )` inside double quotes; `>( )` process substitution; `$"…"` locale strings; `${var//pat/rep}` holding `}` and quotes;
   `case … in pat) . x ;; esac` with a `)` inside a pattern; `coproc`; `function f { . x; }` and `f() ( . x )` bodies; `eval ". x"`
   and `eval '. x'`; `command . x`, `builtin source x`, `\. x`, `'.' x`; an alias that expands to `.`; `exec 3< x; . /dev/fd/3`. For
   each: bash's verdict (ran or not), the screen's verdict, and whether they agree. A disagreement where bash RUNS the file and the
   screen says CLEAN is a fail-open; a disagreement the other way is a false refusal (say whether any live gate file holds that
   shape).
3. R4-1, the end-state backstop. New unfinished constructs (never the builder's eight): an unterminated `$'…'`; a heredoc whose
   delimiter line has trailing spaces; an escaped newline at end of file; a `$((` closed by `) )`; a backtick opened inside `$( )`.
   For each: refused with the right START line, or correctly closed. Does any live gate file end in a state R4-1 would refuse, in
   either mode (measure, do not assume)?
4. R4-3, the workflow parse. New YAML shapes: `run: |` holding a heredoc; `run: >` (folded: newlines become spaces, which changes
   the shell text — does the screen scan the folded or the literal text, and which one does GitHub run?); anchors and aliases
   reusing a `run:`; `"run":` quoted keys; a duplicate `run:` in one step (which value does PyYAML keep, which does GitHub run?); a
   `run:` under `defaults:` or a matrix `include:`; `shell: bash {0}` and `shell: python` (the builder's D4 says refused safely: is
   it?); a multi-document file; tabs. For each: the refusal's file:line against the real YAML line of the command.
5. R4-4, dynamic loads. NEW evasion shapes, never the builder's 37 (listed in its report section "Adversarial R4-4 shapes"):
   `sys.path.insert(0, <dir>)` or `sys.path.append` followed by a plain `import <name>` that resolves to an unlisted repo file (does
   AMENDMENT 2's static-import rule see the path change?); `importlib.util` reached through `getattr(importlib, "util")`;
   `vars(builtins)["exec"]`; `types.ModuleType` plus `exec(code, mod.__dict__)`; `pkgutil`/`zipimport`/`importlib.resources` loads;
   `SourceFileLoader(...).load_module()` and `.exec_module()` through an intermediate object; a loader call inside a class body, a
   default argument, a decorator expression, a comprehension, a `match` case guard; a target built with `os.path.join` from `os.sep`,
   `str.format`, `%`, or `"".join`; `__file__` rebound; a load inside `if TYPE_CHECKING:` (never runs) and inside `if False:`. For each:
   refused, resolved to a listed file, or CLEAN — and whether CLEAN is right. Then the exception set `ALLOWED_DYNAMIC_LOADS` (S:699):
   can an entry be satisfied by a DIFFERENT target (re-pointing), or can one entry's count cover a second, new load? D3 says the
   runtime enforces "at most" and a live-tree test enforces "exactly": measure both, and say what a commit that REMOVES a live load
   and ADDS a different one sees.
6. The seven live sites (report table, census at 792fdbb): reproduce the census with an independent AST walk over every listed Python
   gate, and say for each site whether the screen's resolution is right. `scripts/lint_delta.py:106` resolves through `git rev-parse
   --show-toplevel`: is keying it by (file, target) with count 1 sound when the runtime root is not the repo (a worktree, a copy)?
7. R4-5 and R4-6. The listed hook scans clean under the vocabulary rule (measure). The docstring's re-measured exec-edge numbers
   (the builder: scanner 17 edges, 15 targets, 9 unlisted; a loose grep 30 edges, 13 unlisted): reproduce them with your own
   instrument, or say what you count instead.
8. The real hook. In a THROWAWAY repository under `/tmp/vj10r4/` (a `git archive` subset of the PIN plus your fixtures), with
   `core.hooksPath` pointed at a temporary directory that holds ONLY a copy of `scripts/hooks/pre-commit` (so no post-commit hook runs:
   the builder's own run created a codebase-memory project and overwrote `/tmp/graft-build.log` through post-commit): commit one
   clean change, then your strongest fail-open from items 2-5 and your strongest false refusal. Paste each commit's outcome and rc.
9. Cost. The builder measured +0.10 s (worktree) and +0.08 s (`--staged`) on the live tree. Measure on pathological inputs through
   the real screen: a 5 MB gate-shaped shell file with deep `$( "$( … )" )` nesting; 50,000 heredocs; a 2 MB single line; a YAML
   file with 10,000 steps. A super-linear case is a finding (the hook runs on every commit).
10. MUTANTS (new; never the builder's m1-m25): in scratch copies under `/tmp/vj10r4/mut/` only. At least one per contract line R4-1..R4-5,
   each targeting a line the builder's rows did not touch. Each mutant compiles and collects (AF-AP-78); before you count a kill,
   run the killing test on the UNMUTATED copy and paste that it passes (AF-AP-138). A survivor is a finding; m24 (the `( . x )`
   subshell) is KNOWN.
11. GATES, each command with its output and the set id (`bash scripts/pc_suite.sh set-id -- <files>`): `tests/test_no_laya_in_gates.py`
   twice; `python3 scripts/no_laya_in_gates.py` and `--staged` on the shared tree (read-only use of the index); pyflakes on S and T.

## Boundary

CREATE `tasks/briefs/laya/VERIFY-J1-0-R4-report.md` (write it incrementally from the start); nothing else in the repository.
NEVER place a modified screen, list or test in the SHARED tree, not even for a moment: the pre-commit hook runs the screen from the
working tree (AF-AP-148), and a modified copy there blocks every commit on the branch (the builder's run did this for 3.5 minutes).
Every mutant, fixture tree and throwaway repository lives under `/tmp/vj10r4/` and is removed at the end (the sandbox had about
1.3 GB free at authoring). pytest: `-p no:cacheprovider --basetemp=/tmp/vj10r4/bt<n>` (create the parent first), removed after each
run. Other sandbox agents work in this tree on disjoint files: `proofs/S0-02/`, `proofs/S0-05/` (E3-R1 holds
`proofs/S0-05/tools/pc/run_s0_05_units.sh`), `tests/test_s0_05_egress.py`, `tasks/briefs/s0-02-support/`,
`tasks/briefs/s0-05-support/`, `tasks/briefs/continuity/`, `tasks/briefs/laya/VERIFY-J1-1-report.md`: never touch, run or revert
them. Nothing under `.claude/` is edited (another lane holds that tree's manifest). Never run `git stash`, `git checkout -- …`,
`git restore`, `git add`, `git commit` or `git push` in the shared tree. No outward-facing action; no PC or bridge use.

CODE INTEL FIRST: `graft ask` before any grep for code questions; the pack:
`scripts/lane_context.sh -q 'how does the never-a-gate screen decide a gate file sources or loads unlisted code' -s _ShellScan -s _workflow_runs -s _Resolver -s _load_errors -s _source_errors -o /tmp/vj10r4/pack.md scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py scripts/hooks/pre-commit`.

PREDICATE: a finding blocks only if it is contract-mapped (R4-1..R4-6 or AMENDMENT 2), reproduced through the real screen (and, for
anything claimed about commits, through the real hook in the throwaway repository), materially effective (a gate file sources or
loads unlisted code and the screen reads CLEAN; or a live-tree shape is falsely refused; or a stated claim is false as stated), with a
concrete discriminator, and in-boundary (S, L, T). Everything else is a follow-up. Emit ONE GATE RECOMMENDATION:
`MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`. The coordinator owns the final gate.

Report lint: `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/VERIFY-J1-0-R4-report.md --root .` (no `--map` flags;
cite full repo-relative paths); apply its `fix:` hints for at most three rounds, then paste and finish. The report ends with
DISCREPANCIES and NOT-done.

## PREMISE — MEASURED at authoring (2026-09-23 11:27Z, sandbox @ local 5090671, before the push)
```
$ git log -1 --format="%h %s" 5090671 | cut -c1-90
5090671 J1-0-R4 landed (task #172; GATED-PENDING-VERIFY): the never-a-gate screen scans to
$ git diff --stat 5090671^ 5090671
 scripts/gate_files.txt              |    3 +
 scripts/no_laya_in_gates.py         | 1014 ++++++++++++++++++++++++++++++-----
 tasks/briefs/laya/J1-0-R4-report.md |  469 ++++++++++++++++
 tests/test_no_laya_in_gates.py      |  442 +++++++++++++++
 4 files changed, 1804 insertions(+), 124 deletions(-)
$ blob[:12] lines path (at 5090671)
ae8b2046e118  1419 scripts/no_laya_in_gates.py
9790cb714afa  1097 tests/test_no_laya_in_gates.py
8eaccfa87a98    53 scripts/gate_files.txt
7731a91c7d3e   133 scripts/hooks/pre-commit
1f16b01f1923   162 scripts/lint_delta.py
eb20dde7e198    96 scripts/ap_screen.py
$ grep -n "^def \|^class \|^ALLOWED_DYNAMIC_LOADS\|^EXTERNAL_MODULES" scripts/no_laya_in_gates.py
83:EXTERNAL_MODULES = frozenset(["fubuki_os", "jsonschema", "lint", "pyflakes", "yaml"])
103:def _is_python_gate(entry, content):
111:class _Open(Exception):
126:def _unquote(word):
147:class _ShellScan:
455:def _command_segments(content, first_line=1):
470:def _workflow_runs(content):
499:def _source_errors(entry, content):
531:class _Tree:
591:def _package_files(tree, base, parts, names):
618:def _flagged_by_vocabulary(entry, module, names):
627:def _import_errors(entry, content, tree, listed_set):
699:ALLOWED_DYNAMIC_LOADS = {
710:def _norm(kind, path):
720:def _as_path(value):
728:def _join(left, right):
741:def _parent(value, times=1):
753:def _with_name(value, name):
760:class _Resolver:
1010:def _loader_name(node, aliases):
1022:def _load_sites(entry, parsed, nodes=None):
1059:def _inert(code):
1070:def _module_candidates(tree, importer_dir, module):
1078:def _load_errors(entry, parsed, tree, listed_set, nodes=None):
1144:def _check_line(line, is_py):
1185:def _read_staged(path):
1197:def _read_file(root, path):
1208:def _parse_allowlist(text):
1219:def _load_allowlist(list_path):
1224:def _glob_structural(root):
1250:def _glob_structural_staged():
1270:def _exists_staged(path):
1279:def _index_mode(path):
1291:def main():
$ sed -n 699,703p scripts/no_laya_in_gates.py
699: ALLOWED_DYNAMIC_LOADS = {
700:     ("scripts/lint_delta.py", ".claude/hooks/edit-snapshot.py"): 1,   # base: git rev-parse --show-toplevel
701:     ("scripts/proof-runner", "scripts/validate-ledger"): 1,          # base: the --root argument
702:     ("scripts/ledger-gen", "scripts/validate-ledger"): 1,            # base: the --root argument
703: }
$ grep -c . scripts/gate_files.txt; grep -v "^#" scripts/gate_files.txt | grep -c .
53
40
$ grep -n "no_laya_in_gates" scripts/hooks/pre-commit
127:"$PY" "$REPO_ROOT/scripts/no_laya_in_gates.py" --staged
$ /root/venv-agent-factory/bin/python -c "import yaml; print(yaml.__version__)"; python3 -c ...; bash --version | head -1
6.0.3
system python3 yaml 6.0.1
GNU bash, version 5.2.21(1)-release (x86_64-pc-linux-gnu)
$ python3 scripts/no_laya_in_gates.py; echo rc=$?; python3 scripts/no_laya_in_gates.py --staged; echo rc=$?
no_laya_in_gates: 40 files scanned, clean
rc=0
no_laya_in_gates: 40 files scanned, clean
rc=0
$ (the coordinator's landing gate, a clean detached worktree at the pre-landing HEAD c84f161 + the three parked files; 11:2xZ)
/root/venv-agent-factory/bin/python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=... (twice)
92 passed in 7.41s
92 passed in 7.19s
bash scripts/pc_suite.sh set-id -- tests/test_no_laya_in_gates.py
1 files set=e3695f80792b
pyflakes rc=0 (both Python files)
```
Not measured at authoring, and so written as questions above: whether any new lexer shape disagrees with bash, whether any new
dynamic-load shape reads CLEAN, and whether any new mutant survives.
