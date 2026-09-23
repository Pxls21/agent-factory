# CI-GATE-R1 — the push gate enforces "read each pushed head's run to its conclusion first", cannot be fooled by the clone, and ends every path in a named verdict (task #166; issue #34)

PIN: ae16c6a (origin head at authoring; the five boundary files are byte-identical to HEAD, measured in the premise block).
LANE: ci-gate-r1 (sandbox; agent `code-implementer`). Honey `ultra` Lever-2: your report is DATA: files:lines, pasted counts,
discrepancies, NOT-done. Do NOT spawn subagents.

VENUE: a PRIVATE git worktree at `/tmp/wt-ci166`, created by the coordinator at dispatch from origin's head (the five files there are
byte-identical to the PIN; re-measure). You edit ONLY there. Why: `push_clean.sh --lanes-live` runs the shared tree's WORKING COPY of
both scripts (VERIFY-CI-GATE F20, premise probe 10), and the coordinator pushes while you work. A half-edited gate in the shared tree
would decide a real push. Tests resolve their paths from the test file (`REPO = Path(__file__).resolve().parents[1]`), so running
pytest inside the worktree tests the worktree's bytes. Use `/root/venv-agent-factory/bin/python`.

CONTRACT SOURCES (read them whole before you design): `tasks/briefs/ci/VERIFY-CI-GATE-report.md` (findings F1-F23, the mutant table,
the fix line under each finding) · `scripts/ci_gate.py` and `scripts/push_clean.sh` as landed · `CLAUDE.md`, the push bullet under GIT
BRANCH RULES (the procedural rule this gate mechanizes: read each pushed head's CI run to its conclusion before the next push).

WHAT IS DECIDED (the coordinator's policy, 2026-09-23 07:4xZ, ledger note "VERIFY-CI-GATE HOME"; do not re-decide it, report a
contradiction as a DISCREPANCY):
- F9: an UNFINISHED verdict run REFUSES. It no longer "supersedes". The new exit code is 75 (EX_TEMPFAIL: wait and retry), distinct
  from 1 (red), 2 (cannot decide) and push_clean's own 2/3. `CI_WAIT_SKIP=<reason>` turns a 75 into an allow with a WARNING; it never
  changes a 1 or a 2.
- The waiter is part of the gate: `ci_gate.py --wait SECONDS`, not a second script.
- `--runs-json` is a test input: refused (exit 64) when origin is a github.com remote, so it can never decide a real push (F5).
- `CI_GATE_OFFLINE` rescues only failures to READ or VALIDATE the Actions API data. It never rescues a local git failure (a shallow
  clone, a stale origin ref, an ancestry read that cannot answer): the operator fixes those locally.
- argparse errors exit 64 (the docstring's promise; F8).

BOUNDARY (exact, all inside `/tmp/wt-ci166`): MODIFY `scripts/ci_gate.py`, `scripts/push_clean.sh`, `tests/test_ci_gate.py`,
`.github/workflows/stage0-ci.yml`, `tests/test_stage0_ci_workflow.py`; CREATE `tasks/briefs/ci/CI-GATE-R1-report.md` (write it
incrementally from the start). Read anything anywhere. Do NOT modify any other file in the worktree, and NOTHING in the shared tree
`/home/user/agent-factory` (read-only for you: the coordinator and two other agents work there). A line you cannot meet without another
file is a DISCREPANCY, never a silent edit.

STANDING DO-NOTS: never run `push_clean.sh`, `git push`, `git fetch`, `git pull`, `git commit`, `git stash`, `git checkout -- …`,
`git restore`, `git worktree add|remove|prune`, or any command that moves a ref, in the worktree or the shared tree: the worktree shares
the REAL origin remote and the real refs. Every push_clean run and every git mutation happens in a throwaway repository under `/tmp`
whose origin is a bare repository under `/tmp` (the pattern of `tests/test_ci_gate.py` `repo` / `test_push_clean_refuses_before_pushing_onto_a_red_head`).
READ-ONLY on the real remote: GET requests to `api.github.com` for this repository's runs and jobs are allowed (the gate's own reads);
never re-run, cancel or dispatch a workflow, never open, edit or comment on an issue or PR. No PC or bridge use. No outward-facing
action of any kind.

CODE INTEL FIRST: `graft ask` before any grep for code questions (run it in the shared tree: the five files are identical there);
`scripts/lane_context.sh -q 'how does push_clean decide whether to push' -s decide -s main -s fetch_runs -s repo_slug -o /tmp/ci166/pack.md scripts/ci_gate.py scripts/push_clean.sh`.

## The contract (build to it; the HOW is yours)

C1. EXIT CODES of `ci_gate.py`: 0 allow · 1 refused, the verdict run is red · 2 cannot decide · 64 usage · 75 wait. Every path ends
in one of them with its text; a Python traceback is never a verdict (F7). Text prefixes are fixed: `ci-gate:` (0, stdout),
`REFUSED by ci-gate:` (1 and 2, stderr), `WAIT by ci-gate:` (75, stderr), `WARNING: ci-gate` (an override that allowed, stderr).
Keep the landed texts of the red refusal and the CI_FIX allow (the current tests pin them). Every 2 names its cause; every 75 names the
run (or the pushes) it waits for and prints the waiter command and the `CI_WAIT_SKIP=<reason>` escape.

C2. THE DECISION, in this order:
 a. Shallow clone (`git rev-parse --is-shallow-repository` is `true`) → 2, naming `git fetch --unshallow origin` as the fix.
 b. The origin ref must resolve to a commit (`<ref>^{commit}`) → else 2.
 c. The runs: the Actions API, or `--runs-json` (refused with 64 when origin is a github.com remote; with any other origin it prints
    its notice as a `WARNING: ci-gate` line on stderr). A read failure → 2; `CI_GATE_OFFLINE=<reason>` → 0 with a WARNING.
 d. Every record is validated before any decision (F7, F19, F22, F6): keys `id`, `run_number`, `head_sha`, `status`, `conclusion`,
    `head_branch`, `event`; `id` and `run_number` are `int` and not `bool`; `head_sha` is 40 lowercase hex; `status` is a string;
    `conclusion` is a string or null; `head_branch` equals `--branch`; `event` equals `push`; no two records share a `run_number`.
    Any failure → 2 naming the record and the field (`CI_GATE_OFFLINE` rescues it: it is the API's data).
 e. Runs newest first by `run_number`. The history filter is TRI-STATE (F1): `merge-base --is-ancestor` exit 0 → in history; exit 1 →
    not in history; the run's commit object ABSENT (`git cat-file -e <sha>^{commit}` fails) → not in history (sound only because (a)
    refused shallow clones and (b) proved the ref: an absent commit cannot be reachable from a complete ref); ANY other outcome → 2
    naming the sha and git's exit code. Runs not in history are skipped; completed runs concluded `cancelled` are skipped.
 f. The first remaining run R decides:
    - `status` in {requested, queued, pending, waiting, in_progress} → 75 ("R is <status>").
    - `status` neither `completed` nor in that set → 2 (the API's data: `CI_GATE_OFFLINE` rescues it).
    - completed with `conclusion` null → 2.
    - THE EXPECTED-RUN CHECK: `git diff --no-renames --name-only <R.head_sha> <origin ref>` lists a path outside `transcripts/` → 75
      ("the pushes after R change <first path> and no newer run is registered yet"). Why: a push starts its run a few seconds after it
      lands, so right after a push the newest REGISTERED run is the previous one; without this check a push inside that window (and the
      waiter) reads the previous head's green as the verdict (premise probe 4). `transcripts/` mirrors the workflow's `paths-ignore`
      (DOC: when every changed path matches paths-ignore the workflow does not run); `--no-renames` because a rename out of code into
      `transcripts/` shows only its new path by default (premise probe 5) while GitHub sees the deleted path.
    - `conclusion` `success` → 0; `CI_FIX` equal to `str(R.id)` → 0 with the declaration; anything else → 1.
 g. No R: when the list holds exactly as many records as the page size asked for (50), → 2 ("no verdict in the newest 50 runs";
    F11, premise probe 6); otherwise → 0 with the landed "no stage0-ci run in this branch's history" note.
 `CI_FIX`, `CI_WAIT_SKIP` and `CI_GATE_OFFLINE` are read once, `.strip()`ped; blank means unset. `CI_WAIT_SKIP` changes only a 75.

C3. THE API READ (F4, F6, F17): the query is built with `urllib.parse.urlencode` (branch, `event=push`, `per_page=50`); `timeout=20`
stays; an HTTP error's text carries the status code and, when present, `X-RateLimit-Remaining`. ONE live GET from the worktree proves
the encoded query returns this branch's runs (paste: the count and that every `head_branch` equals the branch).

C4. THE WAITER: `ci_gate.py --branch <b> --wait SECONDS` (`--origin-ref` defaults to `refs/remotes/origin/<branch>`). It runs the
decision every 30 s while the decision is 75, up to SECONDS, printing one line only when the state changes, and returns the final
decision (75 when the deadline passes). In wait mode `CI_FIX` and `CI_WAIT_SKIP` are ignored (one line says so when either is set):
the waiter reports the run's verdict, not a push decision. A read failure during the wait is retried at the next poll; three in a
row → 2. On a red verdict it prints each failed job's name and id from `/repos/<slug>/actions/runs/<id>/jobs` (a failed jobs read is
one WARNING line; the rc stays 1). It never fetches, never pushes. `--runs-json` is re-read at each poll (tests).

C5. push_clean.sh:
 - After `git fetch origin "$BRANCH"`: `refs/remotes/origin/$BRANCH` must equal `FETCH_HEAD`, else exit 2 with a text naming a
   narrowed fetch refspec (F1-B). `RANGE` and the gate's `--origin-ref` use the full `refs/remotes/origin/$BRANCH` (a local branch
   named `origin/<branch>` must not shadow it; F1-C).
 - `--lanes-live`: `rc=0; ( … ) || rc=$?` so the detached worktree is removed after EVERY inner failure (F2, premise probe 9), and the
   inner run executes the detached worktree's own committed `scripts/push_clean.sh` (so `ci_gate.py` is HEAD's too), never
   `$OLDPWD`'s working copy (F20, premise probe 10).
 - The gate's exit code passes through unchanged (0/1/2/64/75); push_clean's own codes (1, 2 `TREE MISMATCH`, 3 trailers) stay.
 - The comment above the gate call says what the gate now enforces (C2) and that `CI_GATE_RUNS_JSON` is refused against github.com.

C6. THE WORKFLOW (F10): `pull_request:` gains the same `paths-ignore: ['transcripts/**']`. A test pins the gate's ignored prefix
(C2 f) equal to BOTH triggers' `paths-ignore`, read from the YAML (the constant and the workflow cannot drift apart).

C7. The module docstring is the decision table of C1-C4 (F18's two inexact lines go; "64 usage" becomes true).

## Tests demanded (in `tests/test_ci_gate.py` / `tests/test_stage0_ci_workflow.py`)

Two landed tests change BY DECISION, not by choice: `test_unfinished_newest_run_allows` becomes the 75 table (F9);
`test_cli_reads_ancestry_from_git` keeps its verdict (an absent object in a non-shallow clone is "not in history", C2 e). Every other
landed test keeps its assertion; the `run()` helper gains `head_branch`/`event`. New, at least:
- the status table (each unfinished status → 75; null, `""`, `"weird"`, a non-string → 2); CI_WAIT_SKIP turns each 75 into 0 with its
  WARNING and leaves a 1 and a 2 as they are; a whitespace-only CI_WAIT_SKIP / CI_GATE_OFFLINE / CI_FIX counts as unset; a padded
  `CI_FIX=" 1009 "` allows;
- record validation: each missing key, `run_number` as str and as bool, a short / uppercase / option-shaped (`--help`) `head_sha`, a
  foreign `head_branch`, a non-push `event`, a duplicate `run_number` → 2 naming the field; CI_GATE_OFFLINE rescues these;
- the tri-state filter on REAL git: an absent sha in a full clone → not in history; a bad `--origin-ref` → 2; a real
  `git clone --depth 1` of a throwaway repo → 2 even with CI_GATE_OFFLINE set;
- the expected-run check on real git: a code commit after the green run → 75; a transcripts-only commit after it → the green verdict;
  a rename from `code/` into `transcripts/` → 75 (the `--no-renames` case); a red run followed by a transcripts-only commit → 1;
- the page rule: 50 records none in history → 2; 49 → 0 with the note;
- the API read with `urllib.request.urlopen` replaced in-process: the URL carries the encoded branch (`#`, `&`, `/`, a non-ASCII
  character), `event=push`, `per_page=50`; `timeout=20`; HTTP 403 (its text carries the code and `X-RateLimit-Remaining`), 404, 500, a
  `URLError`, a `socket.timeout` → 2, and 0 + WARNING under CI_GATE_OFFLINE;
- `repo_slug`: https, ssh (`git@github.com:o/r.git`), `.git`, a trailing slash; a non-github origin → 2;
- `--runs-json` with a github.com origin → 64 (a throwaway repo whose origin URL is set to `https://github.com/o/r`; nothing is
  fetched); with a local origin → its WARNING notice; argparse errors → 64;
- the waiter, in-process with sleep and the clock replaced: [no newer run registered] → [in_progress] → [success] → 0 after three
  polls, one line per state change; a red end → 1 with the failed jobs listed (jobs read replaced); the deadline → 75; three read
  failures in a row → 2 (two then a success → the verdict); CI_FIX and CI_WAIT_SKIP set → ignored with their line;
- push_clean, the REAL script against a throwaway bare origin (extend the landed test's pattern): unfinished → 75 and nothing pushed;
  CI_WAIT_SKIP → pushed with its WARNING; a read failure → 2 passes through (not 1); a narrowed fetch refspec (`remote.origin.fetch`
  set to another branch) → 2 and nothing pushed; a local branch named `origin/feat` pointing at an old green commit while the remote ref
  is red → 1 (the full ref is read); `--lanes-live` refused by the gate → 1 AND `git worktree list` shows no leftover worktree; and
  `--lanes-live` with a working-copy `scripts/ci_gate.py` rewritten to `sys.exit(0)` and declared in `.lanes-live` still refuses a red
  head (the committed bytes decide);
- the workflow: `pull_request` carries the paths-ignore; the prefix pin of C6.

## Mutation audit (scratch copies of the worktree files only; each mutant compiles and collects, AF-AP-78)

One row each: mutant · compiles · collected · killed-by (test id) / SURVIVED / EQUIVALENT with the reason. Before you count a kill,
run the killing test on the UNMUTATED worktree and paste that it passes (AF-AP-138). At least: R1 the tri-state back to
`returncode == 0` · R2 the shallow refusal removed · R3 a present object with exit 128 read as "not in history" · R4 push_clean passes
`origin/$BRANCH` again · R5 the FETCH_HEAD check removed · R6 `( … ); rc=$?` restored (the leak) · R7 the inner run uses
`$OLDPWD/scripts/push_clean.sh` · R8 an unfinished run allows · R9 an unknown or null status allows · R10 the record validation
removed · R11 the query built without `urlencode` · R12 the `head_branch`/`event` check removed · R13 the page rule removed · R14 the
expected-run check removed · R15 `--no-renames` removed · R16 CI_WAIT_SKIP rescues a red verdict · R17 a whitespace-only CI_WAIT_SKIP
counts as set · R18 CI_GATE_OFFLINE rescues a shallow clone · R19 `--runs-json` accepted with a github.com origin · R20 argparse errors
exit 2 · R21 the waiter skips the expected-run check · R22 the waiter ignores its deadline (bound the test with a timeout) · R23 CI_FIX
honoured in wait mode · R24 `event=push` dropped from the query (VERIFY-CI-GATE's M10) · R25 the `pull_request` paths-ignore removed.

## Gates (paste every command with its output)

- `/root/venv-agent-factory/bin/python -m pytest tests/test_ci_gate.py tests/test_stage0_ci_workflow.py -q -p no:cacheprovider
  --basetemp=/tmp/ci166/bt<n>` TWICE in the worktree, identical counts; the set id `bash scripts/pc_suite.sh set-id --
  tests/test_ci_gate.py tests/test_stage0_ci_workflow.py` (premise: `f94590af83b6`).
- `bash -n scripts/push_clean.sh`; `/root/venv-agent-factory/bin/python -m pyflakes scripts/ci_gate.py tests/test_ci_gate.py
  tests/test_stage0_ci_workflow.py` (no new hit).
- The live read of C3 (one GET) and one live decision from the worktree: `python3 scripts/ci_gate.py --branch
  claude/soundbox-kit-migration-iz1jwf` (paste rc and text; a 75 is a valid outcome when a run is in flight).
- `git -C /tmp/wt-ci166 status --porcelain` at the end: exactly the six boundary paths.

## Report (`/tmp/wt-ci166/tasks/briefs/ci/CI-GATE-R1-report.md`)

PREMISE re-measured in the worktree · per contract line C1-C7: files:lines and the tests that pin it · the mutant table · the gates
pasted · DISCREPANCIES · NOT-done (every finding of issue #34 you did not close, by id: F10's "does the gate read PR runs", F12, F14,
F15, F21 and F23 are out of scope unless a contract line closes them). Lint floor: `python3 scripts/report_lint.py --min-refs 12 --map
G=scripts/ci_gate.py --map PCL=scripts/push_clean.sh --map T=tests/test_ci_gate.py --map W=.github/workflows/stage0-ci.yml --map
TW=tests/test_stage0_ci_workflow.py tasks/briefs/ci/CI-GATE-R1-report.md --root /tmp/wt-ci166`; apply its `fix:` hints for at most
three rounds, then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23 08:06Z, sandbox @ ae16c6a)

````
# (a) identities, line maps, the landed test count — scratchpad ci166/premise.sh
$ date -u
2026-09-23 08:06Z

$ git rev-parse origin/claude/soundbox-kit-migration-iz1jwf
ae16c6a2c0cd7b0076df2ec64e4c642907ecda2b

$ git diff origin/claude/soundbox-kit-migration-iz1jwf HEAD -- <the five files> | wc -l
0

$ git status --porcelain -- <the five files> | wc -l
0

$ for f in <the five files>; do sha256 lines path; done
f19a6cbb99ea10b0 100 scripts/ci_gate.py
ab2412d387131433 109 scripts/push_clean.sh
e9def321313dccaa 184 tests/test_ci_gate.py
718365358d1e855b 112 .github/workflows/stage0-ci.yml
0f0c020fcf227103 111 tests/test_stage0_ci_workflow.py

$ git log --format="%h %s" -2 -- scripts/ci_gate.py scripts/push_clean.sh | cut -c1-120
010d1bc Push gate: push_clean refuses while the branch's last stage0-ci run is red (AF-AP-126 mechanized; task #162)
75f3e3a push_clean: rewrite ONLY commits that carry a model-identifier trailer — a foreign commit keeps its object id 

$ grep -n (the gate lines) scripts/ci_gate.py
31:def decide(runs, is_ancestor, ci_fix=""):
33:    for run in sorted(runs, key=lambda r: r["run_number"], reverse=True):
34:        if not is_ancestor(run["head_sha"]):
37:        if run["status"] != "completed":
39:        if run["conclusion"] == "cancelled":
41:        if run["conclusion"] == "success":
43:        if ci_fix == str(run["id"]):
45:        return 1, (f"REFUSED by ci-gate: {where} concluded {run['conclusion']} — {run.get('html_url', '')}\n"
47:    return 0, "ci-gate: no stage0-ci run in this branch's history; nothing to read"
50:def repo_slug(root):
59:def fetch_runs(repo, branch):
60:    url = f"{API}/repos/{repo}/actions/workflows/{WORKFLOW}/runs?branch={branch}&event=push&per_page=50"
61:    with urllib.request.urlopen(url, timeout=20) as resp:
65:def main(argv=None):
71:    args = ap.parse_args(argv)
73:    def is_ancestor(sha):
75:                              capture_output=True).returncode == 0
84:    except Exception as exc:  # every read failure is the same verdict: unknown
85:        offline = os.environ.get("CI_GATE_OFFLINE", "").strip()
92:        return 2
94:    rc, message = decide(runs, is_ancestor, os.environ.get("CI_FIX", "").strip())

$ grep -n (the push lines) scripts/push_clean.sh
12:set -euo pipefail
29:  WT="$(mktemp -d /tmp/push-clean-wt.XXXXXX)"
30:  git worktree add -q --detach "$WT" HEAD || { echo "REFUSED: worktree add failed" >&2; exit 1; }
32:  ( cd "$WT" && TRANSCRIPT_SYNC=0 PUSH_BRANCH="$BRANCH" bash "$OLDPWD/scripts/push_clean.sh" --no-delegates-live ); rc=$?
33:  git worktree remove --force "$WT" 2>/dev/null; git worktree prune
60:git fetch origin "$BRANCH"
61:RANGE="origin/$BRANCH..HEAD"
69:python3 "$(dirname "$0")/ci_gate.py" --branch "$BRANCH" --origin-ref "origin/$BRANCH" \
70:  ${CI_GATE_RUNS_JSON:+--runs-json "$CI_GATE_RUNS_JSON"} || exit $?
85:[ "$TREE_BEFORE" = "$TREE_AFTER" ] || { echo "TREE MISMATCH after rewrite — ABORT, do not push." >&2; exit 2; }
88:[ "$LEFT" = "0" ] || { echo "$LEFT trailer(s) remain — ABORT." >&2; exit 3; }
92:git push -u origin "$SHA:refs/heads/$BRANCH"
103:      && git push -q origin "$(git rev-parse HEAD):refs/heads/$BRANCH" \

$ grep -n (the triggers) .github/workflows/stage0-ci.yml
4:  push:
8:    paths-ignore:
9:      - 'transcripts/**'
10:  pull_request:
15:  cancel-in-progress: true

$ pytest the two test files (sandbox venv)
37 passed in 1.28s

$ bash scripts/pc_suite.sh set-id -- tests/test_ci_gate.py tests/test_stage0_ci_workflow.py
2 files set=f94590af83b6

$ git rev-parse --is-shallow-repository; git config --get-all remote.origin.fetch
false
+refs/heads/*:refs/remotes/origin/*

# (b) behaviour probes on throwaway repos under /tmp — scratchpad ci166/probe.sh (probe 9 redone in the real layout: ci166/probe9.sh)
1. is_ancestor on an absent object and on a bad ref (git merge-base --is-ancestor)
   absent sha -> rc 128
   bad ref    -> rc 128
2. an unfinished newest run, a null status, a malformed record
   status=in_progress -> rc 0 | ci-gate: run #9 (adb0a9b) is in_progress; this push supersedes it
   status=queued -> rc 0 | ci-gate: run #9 (adb0a9b) is queued; this push supersedes it
   status=waiting -> rc 0 | ci-gate: run #9 (adb0a9b) is waiting; this push supersedes it
   status=null -> rc 0 | ci-gate: run #9 (adb0a9b) is None; this push supersedes it
   no run_number -> rc 1 | KeyError: 'run_number'
3. usage error
   missing --branch -> rc 2
4. the registration race: the newest run is green at S, origin head H has a code change and no run yet
   rc 0 | ci-gate: runs read from /tmp/ci166p/r.json (a test input), not the Actions API
ci-gate: run #9 (adb0a9b) passed
5. rename detection: code/a.py moved into transcripts/ (what git diff --name-only S..HEAD reports)
   default:      transcripts/a.py 
   --no-renames: code/a.py transcripts/a.py 
6. a full page of 50 runs, none in the history
   rc 0 | ci-gate: runs read from /tmp/ci166p/r.json (a test input), not the Actions API
ci-gate: no stage0-ci run in this branch's history; nothing to read
7. the URL fetch_runs builds for branch names with # and & (urlopen replaced, nothing sent)
   https://api.github.com/repos/o/r/actions/workflows/stage0-ci.yml/runs?branch=fix#1&event=push&per_page=50  timeout=20
   https://api.github.com/repos/o/r/actions/workflows/stage0-ci.yml/runs?branch=fix&y&event=push&per_page=50  timeout=20
   https://api.github.com/repos/o/r/actions/workflows/stage0-ci.yml/runs?branch=claude/x&event=push&per_page=50  timeout=20
8. --runs-json in a clone whose origin is github.com (the main tree; nothing is pushed)
   rc 0 | stdout: ci-gate: runs read from /tmp/ci166p/empty.json (a test input), not the Actions API
ci-gate: no stage0-ci run in this branch's history; nothing to read
10. which push_clean.sh the --lanes-live inner run executes (push_clean.sh:32)
   ( cd "$WT" && TRANSCRIPT_SYNC=0 PUSH_BRANCH="$BRANCH" bash "$OLDPWD/scripts/push_clean.sh" --no-delegates-live ); rc=$?
9. push_clean --lanes-live refused by the gate, push_clean.sh + ci_gate.py committed inside the throwaway repo: does the detached worktree survive?
   worktrees before: 1
   rc 1 | REFUSED by ci-gate: run #9 (1d57d46) concluded failure — 
   worktrees after:  2 | leaked: 1 | origin feat still 1d57d46 (red 1d57d46)
````
