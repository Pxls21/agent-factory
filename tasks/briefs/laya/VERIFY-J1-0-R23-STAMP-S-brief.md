# VERIFY-J1-0-R23-STAMP-S — the sandbox continuation of the PC verify of J1-0-R2, J1-0-R3 and the future-stamp gate (task #140)

PIN: c269263 (origin head at authoring; every boundary file is byte-identical to the PC brief's PIN 5a00d13, measured below).
LANE: verify-j1-0-r23-stamp-s (sandbox; agent `adversarial-verifier` on the D-054 pin, in the SHARED tree, no worktree isolation). Honey
`full`: line-bounded findings, evidence anchors, SOLID/UNSURE. Do NOT spawn subagents.

WHY THIS LANE EXISTS: the PC lane `pc-verify-j1-0-r23-stamp.md--5a00d13` died 2026-09-23 08:39:29Z on route capacity (two admission
refusals, then an 80 s first-token stall; four local lanes live, vLLM KV cache 0.93; incident log 08:3xZ). Its draft completed part (A)
(J1-0-R2: MERGE-READY for (A)) and never started (B) or (C). The coordinator copied that draft, sha256 verified against the PC, to your
report path before dispatch.

THE CONTRACT is the PC brief `tasks/briefs/pc/pc-verify-j1-0-r23-stamp.md`: read it WHOLE, including its appendix and PREMISE. Its items
(B) B1-B5, (C) C1-C5 and "Common" D1, its predicate, its AUTHORIZATION + DO-NOTS and its Report section are yours, under the VENUE MAP
below. For (A): re-run A1 (the landing gates) here and reproduce A2's rows a, b2 and c through the real hook in a throwaway repo. A row
that does not reproduce is a finding; otherwise (A) stands as drafted.

VENUE MAP (PC brief → this sandbox):
- `$HOME/tmp-vj10/` → `/tmp/vj10/`: every throwaway repo, tree and basetemp lives there and is removed when you are done with it. The
  sandbox has about 1.9 GB free (measured below).
- The hook's `$PY` (`scripts/hooks/pre-commit:13-14`) resolves to `/root/venv-agent-factory/bin/python` here (Python 3.11.15, pyflakes
  3.4.0; measured below), not the system `python3`. Say which interpreter each hook gate ran under.
- C3's `/proc/<lane pid>/environ` read concerns the PC lanes, which you cannot reach (no bridge use): write `NOT run: the lanes run on
  the PC` for that half; the repository grep half runs here.
- C4's clock: `timedatectl` exists here (read-only). A `curl -sI https://api.github.com` answered `400 Bad Request` through the proxy at
  authoring (measured below): find a `Date:` header source this sandbox can read with a GET (headers only), or say that none was found.
- pytest: `-p no:cacheprovider --basetemp=/tmp/vj10/bt`, removed after each run.

BOUNDARY: MODIFY `tasks/briefs/laya/VERIFY-J1-0-R23-STAMP-report.md` (the PC draft, already in place): keep part (A), head it
"(A) — from the PC lane's draft (sha256 856dd688…), re-checked in the sandbox" with your A1 and A2 re-runs, then add (B), (C), D1, the
predicate tables and one GATE RECOMMENDATION per component. Nothing else. Mutants in scratch copies only (never a git restore in this
shared tree); each mutant compiles (`python3 -m py_compile` / `bash -n`) and its suite collects (AF-AP-78); before you count a kill,
run the killing test on the UNMUTATED tree and paste that it passes (AF-AP-138). Other sandbox agents work in this tree on disjoint
files (`proofs/S0-02/`, `proofs/S0-05/`, their tests, `tasks/briefs/s0-02-support/`, `tasks/briefs/s0-05-support/`,
`tasks/briefs/hermes-repin/`) and one in the private worktree `/tmp/wt-ci166`: never touch, run or revert them. Never run `git stash`,
`git checkout -- …`, `git restore`, `git add`, `git commit` or `git push` in this tree; a throwaway repo under `/tmp/vj10/` is yours.
No outward-facing action; no PC or bridge use. Test vocabulary in fixtures is the screen's own closed list, in throwaway trees only.

CODE INTEL FIRST: `graft ask` before any grep for code questions; `scripts/lane_context.sh -q 'how does the never-a-gate screen follow
include edges' -s _command_segments -s _source_errors -s _import_errors -s _package_files -o /tmp/vj10/pack.md scripts/no_laya_in_gates.py
scripts/stamp_check.py scripts/hooks/pre-commit`.

Report lint: `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/VERIFY-J1-0-R23-STAMP-report.md --root .` (no `--map`
flags; cite full repo-relative paths); apply its `fix:` hints for at most three rounds, then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23 08:45Z, sandbox @ c269263)
```
$ date -u; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
Wed Sep 23 08:45:42 UTC 2026
c269263
$ for f in <boundary>; do blob at 5a00d13 vs c269263; done
18c3939889cf 18c3939889cf SAME scripts/no_laya_in_gates.py
55a9a43af463 55a9a43af463 SAME tests/test_no_laya_in_gates.py
b7b48b8da487 b7b48b8da487 SAME scripts/gate_files.txt
7731a91c7d3e 7731a91c7d3e SAME scripts/hooks/pre-commit
6173ca76b508 6173ca76b508 SAME scripts/stamp_check.py
fa2a374363d4 fa2a374363d4 SAME tests/test_stamp_check.py
56f4863ca1a8 56f4863ca1a8 SAME tests/test_shell_syntax.py
$ git diff --quiet c269263 -- <boundary> && echo tree == c269263 on the boundary
tree == c269263 on the boundary
$ ls /root/venv-agent-factory/bin/python && /root/venv-agent-factory/bin/python --version && /root/venv-agent-factory/bin/python -m pyflakes --version
/root/venv-agent-factory/bin/python
Python 3.11.15
3.4.0 Python 3.11.15 on Linux
$ mkdir -p /tmp/vj10p && python -m pytest tests/test_no_laya_in_gates.py tests/test_stamp_check.py tests/test_shell_syntax.py -q -p no:cacheprovider --basetemp=/tmp/vj10p/bt | tail -1   (x2)
57 passed in 4.80s
57 passed in 4.70s
$ python3 scripts/no_laya_in_gates.py; python3 scripts/no_laya_in_gates.py --staged
no_laya_in_gates: 38 files scanned, clean
no_laya_in_gates: 38 files scanned, clean
$ grep -rn SKIP_STAMP_CHECK . | grep -v "^./.git/" | cut -c1-140   (graft cache and briefs trimmed below)
./scripts/hooks/pre-commit:114:# clock, never typed. Bypass (printed, so it shows in review): SKIP_STAMP_CHECK=1 git commit ...
./scripts/hooks/pre-commit:115:if [ -n "${SKIP_STAMP_CHECK:-}" ]; then
./scripts/hooks/pre-commit:116:  echo "pre-commit: SKIP_STAMP_CHECK set — the future-stamp gate bypassed." >&2
./tests/test_stamp_check.py:190:    assert "SKIP_STAMP_CHECK" in hook
$ command -v timedatectl; curl -sS -I -m 10 https://api.github.com | head -4
/usr/bin/timedatectl
HTTP/1.1 200 Connection Established

HTTP/1.1 400 Bad Request
$ sha256sum <the PC draft> (copied from the PC lane dir, sha verified against the PC)
856dd68863d0d895979acfd5072a0a0a3cf49ff558ead8edaf82a720c986bf4c
130
$ grep -n "^## \|^### " <the PC draft>
21:## (A) J1-0-R2 — a listed gate file must be a REGULAR file
23:### A1 — landing gates at the PIN (reproduced)
34:### A2 — AMENDMENT 1 through the REAL hook in a throwaway repo
71:### A3 — positive staged path (a test that pins a CLEAN exit on a well-formed index w/ 100755)
88:### (A) findings (inventory, no severity filter)
113:### (A) predicate table (findings vs the five conjuncts)
121:### (A) GATE RECOMMENDATION
$ df -h /home/user | tail -1
/dev/vda        252G   36G  1.9G  96% /
```
