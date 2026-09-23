# VERIFY-CI-GATE — report (lane verify-ci-gate, sandbox, Opus 5.5)

STATUS: COMPLETE 2026-09-23 07:4xZ — GATE RECOMMENDATION: **MERGE-READY-WITH-FOLLOWUPS** (no finding meets the full blocking
predicate in the measured production state; F1 blocks if any push venue's clone is shallow, has a narrowed refspec or a local
`origin/<branch>` branch — the PC clone was NOT measured). Details at the end.

Scope under review (byte-identical PIN 148e38d → origin head bee499f, measured below):
G=`scripts/ci_gate.py` · PCL=`scripts/push_clean.sh` · T=`tests/test_ci_gate.py` · W=`.github/workflows/stage0-ci.yml` ·
TW=`tests/test_stage0_ci_workflow.py`.

## 1. PREMISE — re-measured (2026-09-23 07:12Z, sandbox)

Origin moved past the brief's 05c90dc to bee499f (a transcripts-only push). Every file under review is byte-identical across
PIN 148e38d → origin bee499f → HEAD → the working tree. No mismatch; the brief stands.

````
$ date -u '+%Y-%m-%d %H:%MZ'
2026-09-23 07:12Z
$ git rev-parse origin/claude/soundbox-kit-migration-iz1jwf
bee499f76906f068659c101d709e819e8a58f6f6
$ git diff --stat 148e38d origin/claude/soundbox-kit-migration-iz1jwf -- <the five files> | wc -l
0
$ git diff --stat origin/claude/soundbox-kit-migration-iz1jwf HEAD -- <the five files> | wc -l
0
$ git diff --stat -- <the five files> | wc -l          # working tree vs HEAD
0
f19a6cbb99ea10b0 100 scripts/ci_gate.py
ab2412d387131433 109 scripts/push_clean.sh
e9def321313dccaa 184 tests/test_ci_gate.py
718365358d1e855b 112 .github/workflows/stage0-ci.yml
0f0c020fcf227103 111 tests/test_stage0_ci_workflow.py
$ git log --format='%h %s' -3 -- scripts/ci_gate.py scripts/push_clean.sh | cut -c1-140
010d1bc Push gate: push_clean refuses while the branch's last stage0-ci run is red (AF-AP-126 mechanized; task #162)
75f3e3a push_clean: rewrite ONLY commits that carry a model-identifier trailer — a foreign commit keeps its object id (the owner's signed-
303600a briefs: lane N5f — the probe's LATER interpreter reading wins, the crash path writes a complete evidence set, reason strings pinne
$ grep -n 'set -e\|git fetch\|ci_gate.py\|CI_GATE_RUNS_JSON\|git push' scripts/push_clean.sh
12:set -euo pipefail
60:git fetch origin "$BRANCH"
67:# last stage0-ci verdict is red, unless the push names the red run it fixes (CI_FIX=<run id>). CI_GATE_RUNS_JSON is a
69:python3 "$(dirname "$0")/ci_gate.py" --branch "$BRANCH" --origin-ref "origin/$BRANCH" \
70:  ${CI_GATE_RUNS_JSON:+--runs-json "$CI_GATE_RUNS_JSON"} || exit $?
92:git push -u origin "$SHA:refs/heads/$BRANCH"
103:      && git push -q origin "$(git rev-parse HEAD):refs/heads/$BRANCH" \
$ /root/venv-agent-factory/bin/python -m pytest tests/test_ci_gate.py tests/test_stage0_ci_workflow.py -q -p no:cacheprovider --basetemp=/tmp/vcig/bt 2>&1 | tail -3; echo "rc=${PIPESTATUS[0]}"
.....................................                                    [100%]
37 passed in 1.13s
rc=0
$ curl -sS -o /dev/null -D - '.../actions/workflows/stage0-ci.yml/runs?branch=claude/soundbox-kit-migration-iz1jwf&event=push&per_page=1' | grep -i '^HTTP\|^x-ratelimit-...'
HTTP/1.1 200 Connection Established
HTTP/1.1 200 OK
X-Ratelimit-Limit: 15000
X-Ratelimit-Remaining: 14990
X-Ratelimit-Resource: core
$ git rev-parse --is-shallow-repository; git rev-list --count origin/claude/soundbox-kit-migration-iz1jwf
false
1157
$ git remote get-url origin        # (credentials, if any, would be redacted; none present)
https://github.com/Pxls21/agent-factory
````

(1157 vs the brief's 1154: the three commits 9048b7e, 05c90dc, bee499f landed after the PIN — none touches the five files.)

Code-intel pack (`scripts/lane_context.sh ... -o /tmp/vcig/pack.md scripts/ci_gate.py scripts/push_clean.sh`, rc 0, 134 lines):
graft skeleton G `decide` L31-L47, `repo_slug` L50-L56, `fetch_runs` L59-L62, `main` L65-L96, `is_ancestor` L73-L75;
crg `tests_for(fetch_runs)` = **0 results** (no test reaches the API read); AP screen: AP-1 ×2 (`os.environ.get` at G:85, G:94 — the
two env channels of item 7); GitNexus impact `decide`/`fetch_runs` LOW (one direct caller, `main`).

## 2. The decision table against its docstring (G:8-17, `completed/success`)

Sources. GitHub REST docs, "List workflow runs for a workflow" (read 2026-09-23): run `status` is "string or null", `conclusion`
"string or null", `run_number` "required, integer", `head_sha` "required, string"; the query's status/conclusion enum is
`completed, action_required, cancelled, failure, neutral, skipped, stale, success, timed_out, in_progress, queued, requested,
waiting, pending`. Measured on the live history (20 GETs, 07:2xZ): 972 push runs, `run_attempt` = 1 on all 972, no duplicate
`run_number`, list order == `run_number` descending, statuses {completed 971, in_progress 1}, conclusions {failure 666,
success 305, None 1}, zero `cancelled` so far, zero `pull_request` runs from this branch. Types on the wire: id int,
run_number int, run_attempt int, head_sha str, status str, conclusion NoneType (in progress).

Probe 1 — `decide()` directly (`/tmp/vcig/probes/probe_decide.py`, the module loaded from the scratch copy, sha f19a6cbb99ea10b0;
CONDENSED: rows with an identical outcome are joined on one line; the script re-runs in well under a second):
````
status='requested' / 'pending' / 'waiting' / 'queued' / 'in_progress'  -> rc=0 ... is <status>; this push supersedes it
status=None                                                -> rc=0 ci-gate: run #7 (ccccccc) is None; this push supersedes it
status=''                                                  -> rc=0 ci-gate: run #7 (ccccccc) is ; this push supersedes it
status='COMPLETED'                                         -> rc=0 ci-gate: run #7 (ccccccc) is COMPLETED; this push supersedes it
conclusion='success'                                       -> rc=0 ci-gate: run #7 (ccccccc) passed
conclusion='cancelled'                                     -> rc=0 ci-gate: run #6 (bbbbbbb) passed
conclusion= failure|neutral|skipped|timed_out|action_required|stale|startup_failure|None|''|'SUCCESS' -> rc=1 REFUSED ... concluded <x>
missing key run_number|head_sha|status|conclusion|id       -> TRACEBACK KeyError
run_number=None (2 runs)                                   -> TRACEBACK TypeError: '<' not supported between instances of 'int' and 'NoneType'
run_number str only '10' vs '9'                            -> rc=1 REFUSED by ci-gate: run #9 (ccccccc) concluded failure   <- lexical sort: '9' > '10'
id=None, CI_FIX='None'                                     -> rc=0 ... concluded failure; CI_FIX=None declares this push fixes it
empty list                                                 -> rc=0 ci-gate: no stage0-ci run in this branch's history; nothing to read
dup #7: green listed first, red second                     -> rc=0 ci-gate: run #7 (ccccccc) passed
dup #7: red listed first, green second                     -> rc=1 REFUSED by ci-gate: run #7 (bbbbbbb) concluded failure
re-run: attempt 2 in_progress / success / failure          -> rc=0 / rc=0 / rc=1  (run_attempt is never read; the record's own status/conclusion decides)
only run is cancelled                                      -> rc=0 ci-gate: no stage0-ci run in this branch's history; nothing to read
````
Probe 2 — the real CLI (`main()` + the real `git merge-base`) on a throwaway repo, one malformed runs file each:
````
missing_run_number   rc=1  stderr_last=[KeyError: 'run_number']
missing_head_sha     rc=1  stderr_last=[KeyError: 'head_sha']
missing_status       rc=1  stderr_last=[KeyError: 'status']
missing_conclusion   rc=1  stderr_last=[KeyError: 'conclusion']
missing_id           rc=1  stderr_last=[KeyError: 'id']
head_sha_null        rc=1  stderr_last=[TypeError: expected str, bytes or os.PathLike object, not NoneType]
head_sha_int         rc=1  stderr_last=[TypeError: expected str, bytes or os.PathLike object, not int]
head_sha_option      rc=0  stdout=[ci-gate: no stage0-ci run in this branch's history; nothing to read]     (head_sha "--help")
head_sha_refname     rc=1  (head_sha "HEAD" reads as in history)
status_null          rc=0  stdout=[ci-gate: run #9 (e27869b) is None; this push supersedes it]
workflow_runs_null   rc=1  stderr_last=[TypeError: 'NoneType' object is not iterable]
workflow_runs_dict   rc=1  stderr_last=[TypeError: string indices must be integers, not 'str']
--- argparse usage error (no --origin-ref):  rc=2   ci_gate.py: error: the following arguments are required: --origin-ref
````
Reading:
- Every DOCUMENTED value ends in a named verdict. The documented unfinished statuses allow; every non-success, non-cancelled
  conclusion refuses (fail closed, matches "any other completed result -> REFUSE", G:13).
- `decide(runs, is_ancestor` (G:94) runs OUTSIDE the `try:` block (G:77). Every malformed record — a missing key, a null/int `head_sha`, a
  non-list `workflow_runs` — ends in a Python traceback with rc 1: refused by accident, not by the named verdict, and
  `CI_GATE_OFFLINE` cannot turn it into a warning (the offline branch covers the read only). Direction: fail closed. No
  malformed record occurs in the 972 live runs.
- The status test is `run["status"] != "completed"` (G:37): ANY other value allows, including `None`, which the documented
  schema permits ("string or null"). The docstring names only "queued / in_progress" (G:11). Direction: fail OPEN on an
  unknown status. Never observed live.
- The sort key trusts `run_number` to be an int (G:33): a string run_number sorts lexically ('9' > '10'), mixed types
  traceback. The documented type is "required, integer"; measured int on all 972.
- The docstring's "64 usage" (G:17) is false: argparse exits 2, the same code as "the runs could not be read".
- Re-runs: the gate reads each record's own `status`/`conclusion` and never `run_attempt`; no run on this branch has ever
  been re-run (972/972 attempt 1), so "the list shows the latest attempt" is UNVERIFIED on live data (documented shape only).
- "only run is cancelled" prints "no stage0-ci run in this branch's history" — a run exists; the text is inexact.

## 3. The history filter (G:73-75, `def is_ancestor`)

`is_ancestor` returns `returncode == 0` (G:75): every non-zero code reads as "not in history". Measured `git merge-base
--is-ancestor` codes: `ancestor=0 not-ancestor=1 absent-object=128 bad-ref=128`; in a `--depth 2` clone, a commit that IS in
origin's history but lies beyond the shallow boundary: `128`. So "not an ancestor" (1) and "cannot tell" (128) collapse into the
same skip.

Real CLI (`/tmp/vcig/probes/hist`; run #3 red on C3, run #1 green on C1, C4 and C5 run-less as after transcripts-only pushes):
````
--- full clone:     REFUSED by ci-gate: run #3 (34ed45d) concluded failure — u                    rc=1
--- shallow clone:  ci-gate: no stage0-ci run in this branch's history; nothing to read           rc=0
--- missing origin ref (standalone gate):  ci-gate: no stage0-ci run in this branch's history ... rc=0
--- --root not a git repo:                 ci-gate: no stage0-ci run in this branch's history ... rc=0
````
Real `push_clean.sh` (scratch copy, sha ab2412d387131433; throwaway bare origins under `/tmp/vcig/probes/pcl`):
````
A shallow: push_clean rc=0 ; origin feat moved: 19eabde… -> 608601d… ; red run #3 is on 43204d3… (in origin's history: 0=0 means yes)
  ci-gate: no stage0-ci run in this branch's history; nothing to read
  == pushing 608601df4380a6f259ce6b86a0e1a215ce99c23b ==
B stale ref: push_clean rc=0 ; origin feat: H2(red)=265236a -> now 2d38778 ; local origin/feat after fetch=e3eea64
  ci-gate: run #1 (e3eea64) passed
  == pushing 2d387780fec594bef0b788ac42b2f876e21fb3a3 ==
C control (default refspec, same stale ref before the fetch): push_clean rc=1 ; origin feat stays 265236a (H2=265236a)
  REFUSED by ci-gate: run #2 (265236a) concluded failure — u
D missing ref: push_clean rc=128   (dies at PCL:62 `git rev-list --count`, before the gate)
````
- A (shallow clone): a red run whose commit IS in origin's history but beyond the boundary is skipped; with no visible run left
  the gate allows and push_clean pushes. Reachable through the real path in a clone made with `--depth N` where the newest run's
  commit is deeper than N (e.g. `--depth 1` while the head is a run-less transcripts commit). This sandbox clone is not shallow
  (measured, item 1). The PC clone: NOT measured (no bridge use).
- B (stale `origin/<branch>`): when the fetch refspec does not cover the branch, `git fetch origin "$BRANCH"` (PCL:60) updates
  FETCH_HEAD only; the gate reads the stale ref, skips the red head H2 (not an ancestor of the stale H1) and reads the older green
  run; push_clean pushes fast-forward onto the red H2 with no `CI_FIX`. This sandbox's refspec is the default
  (`+refs/heads/*:refs/remotes/origin/*`, measured); control C (default refspec) refuses.
- D: a missing origin ref cannot reach the gate through push_clean (the `rev-list` at PCL:62 fails first under `set -e`); the
  standalone gate fails OPEN on it (and on a non-repo `--root`).
- Merge commits: a red run on a merge's SECOND parent reads as in history (`REFUSED ... run #5`, rc=1) — as designed.
- Force-pushed branch: push_clean never force-pushes (PCL:92 `git push -u origin` has no plus-refspec and no force flag); a manual force-push drops the old runs from
  the history by design. Reviewed statically; not probed further.

## 4. The in-progress allow (G:37-38, `run["status"] != "completed"`) against the procedural rule

The rule the gate mechanizes (CLAUDE.md push bullet; ledger 06:4xZ "Run #971 is read to its conclusion before the next push"):
read each pushed head's run to its conclusion before the next push. What the gate allows: a push whenever the newest in-history
run is not `completed`. Fixture runs through the real push_clean (`/tmp/vcig/probes/seq`; after each push the simulated state
cancels the superseded run, as `cancel-in-progress` would, and adds the new run `in_progress`):
````
== Sequence S1: four pushes, each while the previous push's run is still in progress (H1 breaks the build) ==
push H1 decision: ci-gate: run #1 (d2a4cca) passed
push H2 decision: ci-gate: run #2 (da3f266) is in_progress; this push supersedes it
push H3 decision: ci-gate: run #3 (1d54e09) is in_progress; this push supersedes it
push H4 decision: ci-gate: run #4 (9853743) is in_progress; this push supersedes it
runs now: [(1, 'completed', 'success'), (2, 'completed', 'cancelled'), (3, 'completed', 'cancelled'), (4, 'completed', 'cancelled'), (5, 'in_progress', None)]
== Sequence S2: a red verdict, a CI_FIX push, then a push WITHOUT CI_FIX while the fix's run is in progress ==
push H5 (no CI_FIX, head red): rc=1 REFUSED by ci-gate: run #5 (258c8bf) concluded failure — u
push H5 (CI_FIX=1005): rc=0 ci-gate: run #5 (258c8bf) concluded failure; CI_FIX=1005 declares this push fixes it
push H6 (no CI_FIX; the only COMPLETED non-cancelled verdict in history is red #5): rc=0 ci-gate: run #6 (519ff70) is in_progress; this push supersedes it
origin feat log: H6 H5 H4 H3 H2 H1 H0
````
- What the gate allows: S1 — a chain of pushes, each inside the previous run's window, proceeds with NO verdict ever read; the
  superseded runs end `cancelled`, so their verdicts are never known to anyone. S2 — after a `CI_FIX` push, a further push needs
  no `CI_FIX` while the fix's run is in progress, although the last completed verdict is red.
- What the rule says: each of H2, H3, H4 (S1) and H6 (S2) waits for the previous head's run to conclude.
- The separating sequence: push Hk; push Hk+1 before run(Hk) completes (~20-23 min on this repo — the ledger's 06:4xZ line
  quotes run #970's tests job at `1347.12s`; not re-measured here). Rule: forbidden. Gate: allowed (`is in_progress; this push
  supersedes it`).
- Weighed against `cancel-in-progress` (W:13-15): a superseded run is cancelled, so a burst yields at most ONE completed run (the
  last). Failure mails then come only from runs left to finish: at most one per red episode plus one per failed `CI_FIX` attempt
  — the owner's stated goal (no mails from pushes onto a KNOWN red head) is met; "read every head's verdict" is not.
  "A cancelled run never mails" is UNVERIFIED: GitHub's notification docs say a completed-run notification covers "successful,
  failed, neutral, and canceled runs", and "You can also choose to receive a notification only when a workflow run has failed" —
  the owner's setting is not measurable from here.
- Live data point (read-only GET, 07:39Z): run #972 (05c90dc) concluded `success` at 07:31:09Z; the coordinator's next push
  (b03b090, run #973 created 07:31:54Z) came after it — the rule held, and the gate would have read "#972 passed".
- Weighed against push_clean's own transcripts push (PCL:98-105 `TRANSCRIPT_SYNC`, not gated): W:8-9 `paths-ignore` makes it start no run (live:
  no run exists for 148e38d or bee499f; run #972 is on 05c90dc), so it neither mails nor cancels the gated push's run. Consistent.

## 5. The API read (G:59-62, `def fetch_runs`)

No `Authorization` header is sent (G:61 `urlopen(url, timeout=20)`); this sandbox's proxy authenticates the call (limit 15000,
item 1) and `GH_TOKEN`/`GITHUB_TOKEN` are set here but never read by the gate. The repository is PUBLIC
(`repository.private = False` in the live run record), so an unauthenticated shell (the PC) reads it under the 60-per-hour
limit — not measurable from this sandbox (every egress goes through the authenticating proxy).

Failure classes through the REAL `main()` → `fetch_runs()` (`/tmp/vcig/probes/api/drive.py`: the scratch module with only
the constant `API` pointed at a local server `server.py`, `repo_slug` routed to the response mode; long message tails cut at `...`):
````
ok        rc=0    0.0s  ci-gate: no stage0-ci run in this branch's history; nothing to read
e404      rc=2    0.0s  REFUSED by ci-gate: the runs could not be read (HTTP Error 404: Not Found). Retry, or set CI_GATE_OFFLINE=<reason> to push without the gate.
e403rate  rc=2    0.0s  REFUSED by ci-gate: the runs could not be read (HTTP Error 403: Forbidden). Retry, ...
e429      rc=2    0.0s  REFUSED by ci-gate: the runs could not be read (HTTP Error 429: Too Many Requests). Retry, ...
e500      rc=2    0.0s  REFUSED by ci-gate: the runs could not be read (HTTP Error 500: Internal Server Error). Retry, ...
e502      rc=2    0.0s  REFUSED by ci-gate: the runs could not be read (HTTP Error 502: Bad Gateway). Retry, ...
html200   rc=2    0.0s  REFUSED by ci-gate: the runs could not be read (Expecting value: line 1 column 1 (char 0)). Retry, ...
noruns    rc=2    0.0s  REFUSED by ci-gate: the runs could not be read ('workflow_runs'). Retry, ...
redirect  rc=0    0.0s  ci-gate: no stage0-ci run in this branch's history; nothing to read      (302 followed to the ok body)
page51    rc=0    0.1s  ci-gate: no stage0-ci run in this branch's history; nothing to read      (50 newest cancelled, the red verdict is #1 on page 2)
slow      rc=2   20.0s  REFUSED by ci-gate: the runs could not be read (timed out). Retry, ...
--- CI_GATE_OFFLINE='  ' (whitespace only):       e403rate rc=2  REFUSED by ci-gate: the runs could not be read (HTTP Error 403: Forbidden) ...
--- CI_GATE_OFFLINE='pc has no token':            e403rate rc=0  WARNING: ci-gate could not read the runs (HTTP Error 403: Forbidden); pushing anyway: CI_GATE_OFFLINE=pc has no token
````
Real API, real `fetch_runs` (GETs only):
````
real branch (baseline)                       ->  50 runs, events=['push'], head_branches=['claude/soundbox-kit-migration-iz1jwf']
real branch + '#tail' (fragment)             ->  30 runs, events=['push'], head_branches=['claude/soundbox-kit-migration-iz1jwf']
real branch + '&x=1'                         ->  50 runs, events=['push'], head_branches=['claude/soundbox-kit-migration-iz1jwf']
'fix&y' (a valid ref name)                   ->   0 runs, events=[], head_branches=[]
'feat-é' (a valid ref name)                  -> EXCEPTION UnicodeEncodeError: 'ascii' codec can't encode character '\xe9' in position 81 ...
real API, nonexistent workflow file          -> EXCEPTION HTTPError: HTTP Error 404: Not Found
pull_request runs of stage0-ci in the repo: total_count 0 []
$ git check-ref-format --branch <name>:  fix&y valid · fix#y valid · a+b valid · a%41b valid · feat-é valid · a=b valid · a'b valid
````
Reading:
- A private repo's 404, the rate limit's 403 (and a 429), a 5xx, a non-JSON 200, a body without `workflow_runs`, and a timeout
  (20.0 s measured) all end in the named exit 2; whitespace-only `CI_GATE_OFFLINE` counts as unset. The 403 text says only
  "HTTP Error 403: Forbidden" — the operator cannot tell a rate limit from an auth refusal. A redirect is followed (urllib).
- Verdict off the page: `per_page=50`, no pagination (G:60). When the 50 newest runs are all cancelled or outside the history,
  the red verdict on page 2 is never read and the gate allows ("no stage0-ci run in this branch's history"). With
  `cancel-in-progress` the newest run is never cancelled by concurrency (its canceller is newer), so this needs 50 manual cancels
  or 50 runs dropped by force-pushes; live: 0 cancelled runs in 972.
- The branch is interpolated raw (G:60 `runs?branch={branch}`). Every name above is a legal git ref. `#` starts a fragment: `&event=push&per_page=50`
  is dropped (30 runs came back instead of 50). `&` ends the value: `fix&y` asks for branch `fix` (0 runs) and the gate would
  allow on "no run". `+` decodes to a space, `%41` to `A`. Non-ASCII fails closed (UnicodeEncodeError inside the `try`). The
  production branch `claude/soundbox-kit-migration-iz1jwf` has none of these characters; its `/` is accepted unencoded (baseline
  50 runs, all this branch). The gate never checks that a returned run's `head_branch` equals the requested branch.
- Not measured: a DNS stall (the 20 s timeout does not bound `getaddrinfo`), a slow-drip body (the timeout is per socket read).

## 6. push_clean integration (PCL:12, PCL:22-46, PCL:60-70, PCL:92: `set -euo pipefail`, `--lanes-live`, `ci_gate.py`, `git push -u origin`)

(HEAD moved to 3eca373 at 07:24Z — four local ledger/brief/wiki commits, none under `scripts/`, `tests/` or `.github/`; the five
files re-hashed identical at 07:27:32Z.)

Position: fetch PCL:60 `git fetch origin` → range PCL:61-63 `git rev-list --count` → gate PCL:69-70 `ci_gate.py` → rewrite PCL:80 `git filter-branch`
→ push PCL:92 `git push -u origin`. A run with nothing to push exits at PCL:63 `Nothing to push` before the gate (no read needed). Exit codes through the REAL push_clean
(`/tmp/vcig/probes/int`, a throwaway bare origin, the scratch scripts copied beside the work repo):
````
red           push_clean rc=1  origin moved=no    REFUSED by ci-gate: run #9 (faf6149) concluded failure — u
unreadable    push_clean rc=2  origin moved=no    REFUSED by ci-gate: the runs could not be read (Expecting value: line 1 column 1 (char 0)). Retry, ...
missing-file  push_clean rc=2  origin moved=no    REFUSED by ci-gate: the runs could not be read ([Errno 2] No such file or directory: '/tmp/vcig/probes/int/nope.json'). ...
offline       push_clean rc=0  origin moved=YES   WARNING: ci-gate could not read the runs (Expecting value: line 1 column 1 (char 0)); pushing anyway: CI_GATE_OFFLINE=probe
````
`|| exit $?` keeps 1 and 2 distinct. They are not unique to the gate: PCL:57-58 (dirty tree) also exits 1, PCL:85 (TREE
MISMATCH) also exits 2; the text tells them apart.

`--lanes-live` (declared dirty `lane.txt`, the head's run red, then the same with `CI_FIX`; EXCERPT: git's `From` line, the
runs-json notice and the `Read its failed jobs first` line trimmed):
````
lanes-live red: rc=1 origin moved=no
   | == --lanes-live: dirty set is exactly the declared lane files; rewriting/pushing from a detached worktree ==
   |  * branch            feat       -> FETCH_HEAD
   | REFUSED by ci-gate: run #9 (faf6149) concluded failure — u
   worktrees registered after the refusal:
   | /tmp/vcig/probes/int/l     a4a8fb2 [feat]
   | /tmp/push-clean-wt.SR7M0e  a4a8fb2 (detached HEAD)
   lane file still dirty:  M lane.txt
lanes-live CI_FIX: rc=0 origin now a4a8fb2 local feat a4a8fb2
   | ci-gate: run #9 (faf6149) concluded failure; CI_FIX=1009 declares this push fixes it
   | == boundary (1 commits) ==
   | == pushing a4a8fb2d5479f4bf6d3167e657a40d3534d11ef6 ==
   | == branch ref followed origin to a4a8fb2 (identical tree; lane edits untouched) ==
--- errexit on a failing subshell (the PCL:32 shape, `--no-delegates-live ); rc=$?`):
$ bash -c 'set -euo pipefail; ( exit 2 ); rc=$?; echo "cleanup line reached, rc=$rc"'; echo "outer rc=$?"
outer rc=2
````
- The gate runs in the worktree against the right ref and root: `$(dirname "$0")` is the main tree's `scripts/` (absolute,
  `$OLDPWD`), `--root .` is the worktree, which shares refs and objects; it refused on red and allowed with `CI_FIX`.
- `set -euo pipefail` (PCL:12) + PCL:32 `--no-delegates-live ); rc=$?`: a failing subshell trips errexit,
  so PCL:33 `git worktree remove --force` (and `git worktree prune`) never runs. The exit code survives (1 above), but the detached worktree stays registered
  and on disk (`/tmp/push-clean-wt.SR7M0e` above). Pre-existing for every inner failure (PCL:85 `TREE MISMATCH`, PCL:88 `trailer(s) remain`, a failed push); the gate
  makes a refusal a routine outcome. On the real repo each leak is a checkout of 9131 tracked files (`git archive HEAD` =
  166 MB) plus a `.git/worktrees/push-clean-wt.*` entry. The lane's own dirty file is untouched.

## 7. The environment channels (G:85, G:94, PCL:69-70: CI_GATE_OFFLINE, CI_FIX, CI_GATE_RUNS_JSON)

Real CLI (`/tmp/vcig/probes/env`; red run #9 id 1009 on HEAD unless noted):
````
CI_FIX=' 1009 ' (spaces)                     rc=0  ci-gate: run #9 (f562cae) concluded failure; CI_FIX=1009 declares this push fixes it
CI_FIX=$'1009\n' (a real trailing newline)   rc=0  ci-gate: run #9 (f562cae) concluded failure; CI_FIX=1009 declares this push fixes it
CI_FIX=$'\t1009\t' (tabs)                    rc=0  ci-gate: run #9 (f562cae) concluded failure; CI_FIX=1009 declares this push fixes it
CI_FIX='1008' (stale id)                     rc=1  REFUSED by ci-gate: run #9 (f562cae) concluded failure — u
CI_FIX='yes' (non-numeric)                   rc=1  REFUSED by ci-gate: run #9 (f562cae) concluded failure — u
CI_FIX='' (empty)                            rc=1  REFUSED by ci-gate: run #9 (f562cae) concluded failure — u
CI_FIX='1009' while the head is green        rc=0  ci-gate: run #9 (f562cae) passed
CI_FIX='1009' kept after the fix run was cancelled rc=0  ci-gate: run #9 (f562cae) concluded failure; CI_FIX=1009 declares this push fixes it
CI_GATE_OFFLINE set, head RED                rc=1  REFUSED by ci-gate: run #9 (f562cae) concluded failure — u
````
`CI_GATE_RUNS_JSON` through the REAL push_clean, an operator shell with the variable left exported, an empty runs file (EXCERPT:
the boundary's commit line trimmed; stderr summarized):
````
push_clean rc=0 ; origin moved to two
  stdout:
   | ci-gate: runs read from /tmp/vcig/probes/env/empty.json (a test input), not the Actions API
   | ci-gate: no stage0-ci run in this branch's history; nothing to read
   | == boundary (1 commits) ==
   | == pushing 84c3f64379ecb7a0c36afefe689332802d84826c ==
  stderr (4 lines): git's own fetch/push lines only — no WARNING
CI_GATE_RUNS_JSON='' (empty): rc=2 -> REFUSED by ci-gate: the runs could not be read (origin is not a github.com remote: '/tmp/vcig/probes/env/o.git'). Retry,
````
Reading:
- `CI_FIX`: surrounding whitespace is stripped (G:94); a stale, non-numeric or empty value refuses; it can only bless the
  exact verdict run, and it never overrides anything when the head is green. One narrow re-bless: when the fix's own run is
  cancelled with no newer run (only a manual cancel does that — concurrency's canceller is always newer), the verdict falls back
  to the old red run and a `CI_FIX` still exported in that shell allows the next push with no new declaration. The Claude Code
  harness does not persist env between Bash calls; a human or PC shell with `export CI_FIX=…` does.
- `CI_GATE_OFFLINE`: whitespace-only counts as unset (item 5: rc 2); it only turns a READ failure into a warning; a red verdict
  still refuses with it set (rc 1 above). It cannot rescue the malformed-record traceback (item 2).
- `CI_GATE_RUNS_JSON` (PCL:67-70): a test input reachable in production. When set and non-empty, the Actions API is never
  called; a green or empty file lets the push proceed with rc 0. What the operator sees: one stdout line
  `ci-gate: runs read from <path> (a test input), not the Actions API` among push_clean's normal output; nothing on stderr, no
  WARNING, no refusal. It "says so" (PCL:67-68 contract) but does not fail loud. Not set in `.claude/settings*.json` or
  `.claude/hooks` (grep: no hits). An empty value is ignored by `${…:+…}` and the API path runs.

## 8. The workflow half (W:3-15 `paths-ignore`, TW:58-71 `test_transcript_only_push_runs_no_ci`)

GitHub docs ("Workflow syntax", read 2026-09-23), verbatim: "When all the path names match patterns in `paths-ignore`, the
workflow will not run. If any path names do not match patterns in `paths-ignore`, even if some path names match the patterns,
the workflow will run." · "If a push contains more than 1,000 commits, the workflow will **always** run. If generating the diff
times out, the workflow will **always** run." · "If the generated diff contains more than 3,000 files and the files the workflow
filter matches are not in the first 3,000 returned by the filter, the workflow will **not** run." · "Path filters are not
evaluated for pushes of tags." · Pushes to existing branches: "A two-dot diff compares the head and base SHAs directly with each
other." · Pushes to new branches: "A two-dot diff against the parent of the ancestor of the deepest commit pushed." · Concurrency:
"By default, any existing `pending` job or workflow in the same concurrency group will be canceled and the new queued job or
workflow will take its place."

Live (GETs, 07:3xZ):
````
head_sha=148e38d: repo-wide runs total_count=0 []                    <- transcripts-only push, no run
head_sha=bee499f: repo-wide runs total_count=0 []                    <- transcripts-only push, no run
head_sha=05c90dc: repo-wide runs total_count=1 [('stage0-ci', 972, 'push', 'in_progress', None)]
stage0-ci push runs, all branches: head_branch histogram {'claude/soundbox-kit-migration-iz1jwf': 100} total_count 972
stage0-ci runs, all events (newest 100): event histogram {'push': 100}
````
Commits 60777a5~1..bee499f: every commit touches either only `transcripts/` (148e38d, bee499f) or no transcripts file at all —
no push since W landed mixed the two.
push_clean to a branch origin lacks (throwaway): `rc=128`, `fatal: couldn't find remote ref brandnew` at PCL:60 `git fetch origin`, before the gate.

Workflow-file negative controls against TW (scratch copies; each YAML-valid; `pytest tests/test_stage0_ci_workflow.py`):
````
W1 paths-ignore removed                              rc=1  1 failed, 9 passed in 0.07s  failed=[test_transcript_only_push_runs_no_ci ]
W2 transcripts/** -> transcripts/* (1 level)         rc=1  1 failed, 9 passed in 0.06s  failed=[test_transcript_only_push_runs_no_ci ]
W3 push also filtered to branches: [main]            rc=1  1 failed, 9 passed in 0.06s  failed=[test_transcript_only_push_runs_no_ci ]
W4 group without github.ref                          rc=1  1 failed, 9 passed in 0.06s  failed=[test_newer_push_cancels_superseded_run ]
W5 cancel-in-progress: false                         rc=1  1 failed, 9 passed in 0.07s  failed=[test_newer_push_cancels_superseded_run ]
W6 paths-ignore ALSO on pull_request                 rc=0  10 passed in 0.05s  failed=[]
W7 concurrency block removed                         rc=1  1 failed, 9 passed in 0.06s  failed=[test_newer_push_cancels_superseded_run ]
````
Reading:
- Transcripts-only push → no run: VERIFIED live twice (148e38d, bee499f; repo-wide, any event). A push that changes transcripts
  AND a code file → runs: per the docs ("If any path names do not match … the workflow will run"); NOT live-evidenced (no such
  push yet; a test push to origin is out of bounds). A new branch's first push: per the docs a two-dot diff against the parent
  of the deepest pushed commit's ancestor, so code commits run; unreachable through push_clean anyway (rc 128 above). Tag pushes
  are not path-filtered (unchanged by W); the repo has no stage0-ci tag or pull_request runs at all (total_count 972 = this
  branch's 972).
- Concurrency: the group is `stage0-ci-<github.ref>`; a pull_request run's ref is `refs/pull/<n>/merge`, another group, so a
  push never cancels a PR run; the gate's `event=push` filter keeps PR runs out of the verdict. Both moot today: zero PR runs.
  Edge: a transcripts-only push creates no run, so it does NOT cancel an in-progress run — G:11 `concurrency cancels it` is
  true only for a push that starts a run (harmless: that run then completes and is the next verdict).
- TW:58-71 pin TEXT — the parsed YAML dicts, by exact equality. Exact equality is the strongest local pin (W1-W5, W7 each killed
  by name), but no local test can pin GitHub's semantics; behaviour rests on the live record above. W6 survives (a PR-side filter
  is outside both tests; not harmful).

## 9. Mutation audit (scratch copies only; driver `/tmp/vcig/mut/{mutants.py,apply.py,run.sh}`)

Each mutant: a fresh copy of the scratch tree (the five files at the PIN bytes + `scripts/setup.sh`), one exact-string edit
(anchor count asserted = 1), `py_compile` of G, `bash -n` of PCL, `--collect-only`, then both test files (T + TW, 37 tests).
Raw rows (pasted from `/tmp/vcig/mut/table.txt`):
````
M1 | history filter removed | py_compile=ok bash-n=ok | collected: 37 tests collected in 0.03s | rc=1 3 failed, 34 passed in 1.08s | killed-by: tests/test_ci_gate.py::test_run_outside_the_history_is_ignored tests/test_ci_gate.py::test_no_run_in_the_history_allows_with_a_note[runs1] tests/test_ci_gate.py::test_cli_reads_ancestry_from_git 
M2 | cancelled run refused | py_compile=ok bash-n=ok | collected: 37 tests collected in 0.03s | rc=1 1 failed, 36 passed in 1.10s | killed-by: tests/test_ci_gate.py::test_cancelled_run_is_skipped_for_the_next_older_verdict 
M3 | cancelled run read as a verdict (allow) | py_compile=ok bash-n=ok | collected: 37 tests collected in 0.03s | rc=1 1 failed, 36 passed in 1.08s | killed-by: tests/test_ci_gate.py::test_cancelled_run_is_skipped_for_the_next_older_verdict 
M4 | in-progress run refused | py_compile=ok bash-n=ok | collected: 37 tests collected in 0.03s | rc=1 3 failed, 34 passed in 1.09s | killed-by: tests/test_ci_gate.py::test_unfinished_newest_run_allows[queued] tests/test_ci_gate.py::test_unfinished_newest_run_allows[in_progress] tests/test_ci_gate.py::test_unfinished_newest_run_allows[waiting] 
M5 | newest chosen by list order | py_compile=ok bash-n=ok | collected: 37 tests collected in 0.03s | rc=1 1 failed, 36 passed in 1.13s | killed-by: tests/test_ci_gate.py::test_newest_is_chosen_by_run_number_not_list_order 
M6a | CI_FIX compared without str() | py_compile=ok bash-n=ok | collected: 37 tests collected in 0.03s | rc=1 3 failed, 34 passed in 0.95s | killed-by: tests/test_ci_gate.py::test_ci_fix_naming_the_red_run_allows tests/test_ci_gate.py::test_cli_refuses_a_red_head_and_allows_the_declared_fix tests/test_ci_gate.py::test_push_clean_refuses_before_pushing_onto_a_red_head 
M6b | CI_FIX read without .strip() | py_compile=ok bash-n=ok | collected: 37 tests collected in 0.03s | rc=0 37 passed in 1.16s | killed-by: NONE
M7 | push_clean gate call moved after the push | py_compile=ok bash-n=ok | collected: 37 tests collected in 0.03s | rc=1 1 failed, 36 passed in 0.96s | killed-by: tests/test_ci_gate.py::test_push_clean_refuses_before_pushing_onto_a_red_head 
M8 | || exit $? -> || true | py_compile=ok bash-n=ok | collected: 37 tests collected in 0.03s | rc=1 1 failed, 36 passed in 0.97s | killed-by: tests/test_ci_gate.py::test_push_clean_refuses_before_pushing_onto_a_red_head 
M9 | offline branch allows without the variable | py_compile=ok bash-n=ok | collected: 37 tests collected in 0.03s | rc=1 3 failed, 34 passed in 0.89s | killed-by: tests/test_ci_gate.py::test_cli_fails_closed_when_the_runs_cannot_be_read[None] tests/test_ci_gate.py::test_cli_fails_closed_when_the_runs_cannot_be_read[not tests/test_ci_gate.py::test_cli_fails_closed_when_the_runs_cannot_be_read[{"no_runs": 
M10 | event=push dropped from the query | py_compile=ok bash-n=ok | collected: 37 tests collected in 0.03s | rc=0 37 passed in 1.11s | killed-by: NONE
X1 | || exit $? -> || exit 1 (collapses 2 into 1) | py_compile=ok bash-n=ok | collected: 37 tests collected in 0.03s | rc=0 37 passed in 1.08s | killed-by: NONE
X2 | per_page=50 -> per_page=1 | py_compile=ok bash-n=ok | collected: 37 tests collected in 0.03s | rc=0 37 passed in 1.07s | killed-by: NONE
X3 | branch filter dropped from the query | py_compile=ok bash-n=ok | collected: 37 tests collected in 0.03s | rc=0 37 passed in 1.16s | killed-by: NONE
X4 | urlopen timeout removed | py_compile=ok bash-n=ok | collected: 37 tests collected in 0.03s | rc=0 37 passed in 1.13s | killed-by: NONE
X5 | CI_GATE_OFFLINE read without .strip() | py_compile=ok bash-n=ok | collected: 37 tests collected in 0.03s | rc=0 37 passed in 1.06s | killed-by: NONE
X6 | the runs-json notice removed (the test input no longer says so) | py_compile=ok bash-n=ok | collected: 37 tests collected in 0.03s | rc=0 37 passed in 1.06s | killed-by: NONE
X7 | unknown status allows -> only queued/in_progress allow, the rest refuse | py_compile=ok bash-n=ok | collected: 37 tests collected in 0.03s | rc=1 1 failed, 36 passed in 1.12s | killed-by: tests/test_ci_gate.py::test_unfinished_newest_run_allows[waiting] 
X8 | repo_slug regex accepts any host | py_compile=ok bash-n=ok | collected: 37 tests collected in 0.03s | rc=0 37 passed in 1.03s | killed-by: NONE
````
AF-AP-138 — every killing test on the UNMUTATED scratch tree (G f19a6cbb99ea10b0, PCL ab2412d387131433, T e9def321313dccaa):
````
tests/test_ci_gate.py::test_run_outside_the_history_is_ignored PASSED
tests/test_ci_gate.py::test_no_run_in_the_history_allows_with_a_note[runs0] PASSED
tests/test_ci_gate.py::test_no_run_in_the_history_allows_with_a_note[runs1] PASSED
tests/test_ci_gate.py::test_cli_reads_ancestry_from_git PASSED
tests/test_ci_gate.py::test_cancelled_run_is_skipped_for_the_next_older_verdict PASSED
tests/test_ci_gate.py::test_unfinished_newest_run_allows[queued] PASSED
tests/test_ci_gate.py::test_unfinished_newest_run_allows[in_progress] PASSED
tests/test_ci_gate.py::test_unfinished_newest_run_allows[waiting] PASSED
tests/test_ci_gate.py::test_newest_is_chosen_by_run_number_not_list_order PASSED
tests/test_ci_gate.py::test_ci_fix_naming_the_red_run_allows PASSED
tests/test_ci_gate.py::test_cli_refuses_a_red_head_and_allows_the_declared_fix PASSED
tests/test_ci_gate.py::test_push_clean_refuses_before_pushing_onto_a_red_head PASSED
tests/test_ci_gate.py::test_cli_fails_closed_when_the_runs_cannot_be_read[None] PASSED
tests/test_ci_gate.py::test_cli_fails_closed_when_the_runs_cannot_be_read[not json] PASSED
tests/test_ci_gate.py::test_cli_fails_closed_when_the_runs_cannot_be_read[{"no_runs": []}] PASSED
============================== 15 passed in 1.03s ==============================
````
| mutant | compiles | collected | verdict | killed-by / reason |
|---|---|---|---|---|
| M1 history filter removed | ok | 37 | KILLED | `test_run_outside_the_history_is_ignored` (T:80), `test_no_run_in_the_history_allows_with_a_note` [runs1] (T:93), `test_cli_reads_ancestry_from_git` (T:142) |
| M2 cancelled refused | ok | 37 | KILLED | `test_cancelled_run_is_skipped_for_the_next_older_verdict` (T:73) |
| M3 cancelled read as allow | ok | 37 | KILLED | `test_cancelled_run_is_skipped_for_the_next_older_verdict` (T:73, first assertion) |
| M4 in-progress refused | ok | 37 | KILLED | `test_unfinished_newest_run_allows` [queued/in_progress/waiting] (T:67) |
| M5 newest by list order | ok | 37 | KILLED | `test_newest_is_chosen_by_run_number_not_list_order` (T:87) |
| M6a `CI_FIX` without `str()` | ok | 37 | KILLED | `test_ci_fix_naming_the_red_run_allows` (T:56), `test_cli_refuses_a_red_head_and_allows_the_declared_fix` (T:131), `test_push_clean_refuses_before_pushing_onto_a_red_head` (T:162) |
| M6b `CI_FIX` without `.strip()` | ok | 37 | SURVIVED | no test sends a padded `CI_FIX` through `main()` (T:61 feeds `decide()` directly). Effect in the SAFE direction: a padded id refuses |
| M7 gate after the push | ok | 37 | KILLED | `test_push_clean_refuses_before_pushing_onto_a_red_head` (T:162), its origin-ref STATE assertion `== red` (T:179) |
| M8 `\|\| true` | ok | 37 | KILLED | `test_push_clean_refuses_before_pushing_onto_a_red_head` (T:162), rc assertion `refused.returncode == 1` (T:177) |
| M9 offline allows without the variable | ok | 37 | KILLED | `test_cli_fails_closed_when_the_runs_cannot_be_read` ×3 (T:150) |
| M10 `event=push` dropped | ok | 37 | SURVIVED — EQUIVALENT ON TODAY'S DATA | no test reaches `fetch_runs` (crg `tests_for` = 0). Live: 100/100 newest stage0-ci runs are `push` events and the repo has 0 `pull_request` runs, so today's verdict is unchanged; NOT equivalent once a PR or dispatch run exists |
| X1 `\|\| exit 1` | ok | 37 | SURVIVED | no push_clean test of the exit-2 path |
| X2 `per_page=1` | ok | 37 | SURVIVED | untested read; equivalent today (newest run #972 not cancelled), not in general |
| X3 branch filter dropped | ok | 37 | SURVIVED — EQUIVALENT ON TODAY'S DATA | all 972 stage0-ci push runs in the repo are on this branch |
| X4 timeout removed | ok | 37 | SURVIVED | a hung API would hang the push |
| X5 `CI_GATE_OFFLINE` without `.strip()` | ok | 37 | SURVIVED | FAIL-OPEN direction: whitespace-only would bypass the read |
| X6 the runs-json notice removed | ok | 37 | SURVIVED | PCL:67-68's "says so" is untested |
| X7 only queued/in_progress allow | ok | 37 | KILLED | `…[waiting]` — the suite pins `waiting` → allow (a hardening fix must keep it) |
| X8 `repo_slug` any host | ok | 37 | SURVIVED | `repo_slug` untested |

Tally: brief set M1-M10 (11 rows with M6a/M6b): 9 KILLED, 2 SURVIVED (M6b safe-direction; M10 equivalent on today's data).
Extras X1-X8: 1 KILLED (X7), 7 SURVIVED. Every survivor sits in code no test reaches (`fetch_runs`, `repo_slug`, the env
strips in `main`, push_clean's exit-2 path, the runs-json notice).

## 10. Anything else

- **Short-name ref shadowing** (G:74 `--is-ancestor` via PCL:69 `--origin-ref "origin/$BRANCH"`): a local branch literally named
  `origin/<branch>` wins git's disambiguation; the gate reads its history and git's ambiguity warning is swallowed by
  `capture_output=True`. Measured: `rev-parse origin/feat -> warning: refname 'origin/feat' is ambiguous. eea086b… (H1=eea086b
  H2=3ae2229)` then `ci-gate: run #1 (eea086b) passed rc=0` with red run #2 on H2 skipped. Pre-existing for PCL:61's RANGE too.
- **`--lanes-live` runs the WORKING COPY** of PCL and G (PCL:32 `bash "$OLDPWD/scripts/push_clean.sh"`, G via
  `$(dirname "$0")`): a lane whose declared files include either script would decide the push with unreviewed bytes. Reviewed
  statically.
- **Stale context**: `wiki/topics/infrastructure-and-tooling.md:41` ("strips trailers, proves tree identity, pushes") and `:71`
  (`push_clean.sh --> filter-branch --> git push`) omit the gate; `AGENTS.md:23` / `.hermes.md:27` (`Push only through`) carry a condensed push
  bullet without it (they also omit `--lanes-live`; Codex/Hermes lanes cannot push — pc-lane.sh refuses `git push`).
  CLAUDE.md:34 `CI GATE (AF-AP-126` names the gate; it says "REFUSES while it is red" and does not mention the in-progress allow.
- **Evidence audit** (builder's claims re-derived): T collects 27 and TW 10 (`27 tests collected`, `10 tests collected`; the
  two TW cases landed in 60777a5, not 010d1bc); the "eight mutants … each killed by name" list maps onto M7/M8, M3, M1, M6a, M4,
  M9, M5 here — all killed; the three workflow negative controls (W1, W7, W5) reproduce as "1 failed, 9 passed" each on exactly
  their test; the live read reproduces (`ci-gate: run #972 (05c90dc) is in_progress; this push supersedes it`, 07:19:17Z) and
  its mechanism — origin's head bee499f has no run, so its parent's run #972 is the verdict — is confirmed by the repo-wide
  `head_sha` query (bee499f: 0 runs).
- **Latent owner-mail path when a PR is open**: W:10 `pull_request:` has no `paths-ignore`, so with a PR open from this branch
  every push — transcripts-only syncs included — starts a pull_request run in its own concurrency group, and the gate's
  `event=push` filter never reads it. Today: 0 pull_request runs in the repo (measured), so moot.

## Findings inventory — ranked, blocking predicate applied

Predicate columns: (1) contract-mapped · (2) canonical reproduction through the production path at the PIN · (3) material
effect in the measured production state · (4) concrete discriminator · (5) inside this increment's boundary.
Evidence levels: VERIFIED = reproduced this session; DOC = GitHub documentation only; UNVERIFIED = neither.

**F1 — FOLLOW-UP (top) · the history filter reads "cannot tell" as "not in history" (G:75 `.returncode == 0`).**
Evidence VERIFIED (items 3 and 10). Every non-zero `merge-base` code — 128 for an absent object or a bad ref — skips the run.
Through the REAL push_clean on throwaway origins: A, a shallow clone, the red run beyond the boundary → "no stage0-ci run in
this branch's history" → pushed; B, a fetch refspec that does not cover the branch leaves `origin/<branch>` stale after
PCL:60 `git fetch origin "$BRANCH"` → the older green run is read → pushed onto the red head with no `CI_FIX`; a local branch named
`origin/<branch>` shadows the remote ref passed at PCL:69 `--origin-ref` (git's ambiguity warning is swallowed). Control C
(default refspec) refuses. (1) yes — G:8-9 `whose head commit is in the history of`
the origin ref; CLAUDE.md:34 `CI GATE (AF-AP-126` "REFUSES while it is red". (2) the code path is exact; the clone state is not this sandbox's. (3) NO in the measured production
state: this clone is full and uses `+refs/heads/*:refs/remotes/origin/*`; all 972 live run SHAs give code 0 here. (4) yes.
(5) yes. → FOLLOW-UP. ESCALATION TRIGGER: if any venue that runs push_clean has a shallow clone, a narrowed refspec or such a
local branch, this meets all five and blocks — the PC clone was NOT measured. Fix: in `is_ancestor`, return "in history" on 0,
"not in history" on 1, and raise a read failure (exit 2) on anything else; refuse (exit 2) when `git rev-parse
--is-shallow-repository` is true; pass `refs/remotes/origin/$BRANCH` and check it equals `FETCH_HEAD` after the fetch. On
today's history the code-128 → exit-2 change causes no false refusal (972/972 code 0).

**F2 — FOLLOW-UP · a gate refusal in `--lanes-live` mode leaks the detached worktree (PCL:32 `--no-delegates-live ); rc=$?`).**
Evidence VERIFIED (item 6). `set -euo pipefail` (PCL:12) trips on the failing subshell, so
PCL:33 `git worktree remove --force` never runs; the exit code survives (1). (1) partial: the gate's own contract holds (position, `|| exit $?`), but
PCL:19 calls it `throwaway DETACHED worktree`. (2) yes. (3) garbage only: a registered worktree plus a checkout per refusal (166 MB
tracked on the real tree), no wrong push, no data loss. (4) yes (`git worktree list` after a refusal). (5) the line predates this
increment and leaks on every inner failure (PCL:85 `TREE MISMATCH`, PCL:88 `trailer(s) remain`, a failed push); the gate makes
refusal routine. → FOLLOW-UP. Fix: `rc=0; ( … ) || rc=$?` at PCL:32 (today `--no-delegates-live ); rc=$?`).

**F3 — FOLLOW-UP · an unknown or null run status allows (G:37 `run["status"] != "completed"`).** Evidence VERIFIED (item 2:
`status=None -> rc=0 … is None; this push supersedes it`, also via the CLI). (1) G:11 names only `queued / in_progress`; the
REST schema allows `status` "string or null". (2) the real `decide`/`main`, input by runs file. (3) none observed (972/972 live
statuses known). (4) yes. (5) yes. → FOLLOW-UP. Fix: allow only requested/queued/pending/waiting/in_progress; anything else →
exit 2 with its text (X7 shows the suite pins `waiting` → allow; keep it).

**F4 — FOLLOW-UP · the API read and the env strips have no test.** Evidence VERIFIED by mutation (item 9): M10 (`event=push`
dropped from G:60 `?branch={branch}&event=push&per_page=50`), X2, X3, X4 (G:61 `urlopen(url, timeout=20)`), X8 (`repo_slug`)
survive — crg `tests_for(fetch_runs)` = 0; X1 (PCL:70 `|| exit $?` → `|| exit 1`), X5 (G:85 `.strip()`), X6 (the
notice at G:79 `(a test input), not the Actions API`) and M6b (G:94 `.strip()`) survive. (1) brief item 9 (M10 is a required row);
standing rule 14 (failure-behaviour tests). (3) none today: the production lines are correct, and M10/X3 are equivalent on
today's data. → FOLLOW-UP. Fix: monkeypatch `urllib.request.urlopen` to capture the URL (assert `event=push`, `per_page=50`, an
encoded branch, `timeout=20`) and to raise 403/404/5xx/timeout; `repo_slug` cases (https, ssh, `.git`, trailing slash,
non-github → ValueError); a push_clean test for exit 2; CLI tests for a padded `CI_FIX` and a whitespace-only
`CI_GATE_OFFLINE`; assert the runs-json notice.

**F5 — FOLLOW-UP · `CI_GATE_RUNS_JSON` replaces the verdict in production with only a stdout line (PCL:70
`CI_GATE_RUNS_JSON:+--runs-json`).** Evidence VERIFIED (item 7: an exported variable and an empty file → push_clean rc 0,
pushed, nothing on stderr). (1) PCL:68 "`replaces the Actions API and says so`" — it says so, on stdout, not as a warning.
(3) only when the variable is left set (misuse) → FOLLOW-UP. Fix: print the notice as `WARNING:` on stderr, or refuse
`--runs-json` when origin is a github.com remote (the tests use a local bare origin).

**F6 — FOLLOW-UP · the branch is interpolated raw and the returned runs are never checked (G:60 `?branch={branch}`).**
Evidence VERIFIED on the real API (item 5): `#` drops `&event=push&per_page=50` (30 runs back), `fix&y` asks for `fix` (0 runs →
"no run" → allow), non-ASCII fails closed; all are legal ref names. (3) none for the production branch (50 runs, all this
branch). Fix: `urllib.parse.urlencode(...)` for the query, and skip (or refuse on) any run whose `head_branch`/`event` differ.

**F7 — FOLLOW-UP · a malformed record ends in a Python traceback with rc 1 (G:94 `decide(runs, is_ancestor` runs outside the
try block, G:84 `except Exception as exc`).** Evidence VERIFIED (item 2, twelve CLI cases). Fail closed, but not a named verdict, and
`CI_GATE_OFFLINE` cannot rescue it. (3) none live. Fix: validate keys and types (int `run_number`, 40-hex `head_sha`, str
`status`) inside the `try` → exit 2 with the reason; this also closes F22's lexical sort and F19's option-shaped sha.

**F8 — FOLLOW-UP (doc) · "64 usage" is false (G:17 `64 usage`).** argparse exits 2 (measured), the same code as "the runs
could not be read". Fix: map argparse errors to 64, or correct the docstring.

**F9 — INFO for the coordinator (policy; the brief says do not decide) · the in-progress allow
(G:37-38 `this push supersedes it`) is weaker than the procedural rule.** Evidence VERIFIED (item 4, S1 and S2). What the gate allows: any push while the newest
in-history run is unfinished — S1 pushed H2-H4 with no verdict read, S2 pushed H6 without `CI_FIX` while the fix's run ran. What
the rule says: read each pushed head's run to its conclusion first. Mails: at most one per red episode plus one per failed
`CI_FIX` attempt (cancelled runs aside — F14).

**F10 — FOLLOW-UP (latent) · with a PR open, W:10 `pull_request:` runs have no `paths-ignore` and the gate never reads them
(`event=push`).** Evidence VERIFIED that it is moot today (0 pull_request runs in the repo); W6 survives TW. Fix when a PR opens:
add the same `paths-ignore` to `pull_request`, and decide whether the gate reads PR runs.

**F11 — INFO · a verdict can fall off the 50-run page (G:60 `per_page=50`, no pagination).** VERIFIED on the local server (`page51`: rc 0).
Needs 50 newest runs all cancelled or out of history; live: 0 cancelled in 972. Fix: follow `rel="next"` to a cap, then exit 2.

**F12 — INFO · a still-exported `CI_FIX` re-blesses the old red run after a manual cancel of the fix run.** VERIFIED (item 7).

**F13 — FOLLOW-UP (docs) · stale context.**
`wiki/topics/infrastructure-and-tooling.md:41` `strips trailers, proves tree identity` omits the gate. INFO: `AGENTS.md:23` / `.hermes.md:27` "`Push only through`" are condensed (no `--lanes-live` either).

**F14 — UNVERIFIED · "a cancelled run never mails".** DOC: notifications cover "successful, failed, neutral, and canceled runs"
unless the owner chose "only when a workflow run has failed". The owner's setting is not measurable here.

**F15 — DOC, not live · a push that changes transcripts AND code runs CI** ("If any path names do not match … the workflow will
run"). No such push exists yet; a test push is out of bounds. The transcripts-only case is VERIFIED live (148e38d, bee499f).

**F16 — INFO · exit codes are not unique to the gate:** PCL:57 `dirty working tree` exits 1, PCL:85 `TREE MISMATCH` exits 2, and a
traceback exits 1 (F7). The text distinguishes them.

**F17 — INFO · the 403 text is only "HTTP Error 403: Forbidden"** (G:90 `the runs could not be read`): a rate limit reads like
an auth refusal.

**F18 — INFO · two inexact messages:** G:11 `concurrency cancels it` is false for a push that starts no run (a transcripts-only
push cancels nothing); a lone cancelled run prints "no stage0-ci run in this branch's history".

**F19 — INFO · `head_sha` reaches git unvalidated (G:74 `--is-ancestor`):** `--help` → allow, `HEAD` → in history. Only from a
crafted runs file; the API returns 40-hex.

**F20 — INFO · `--lanes-live` decides with the WORKING COPY of both scripts (PCL:32 `$OLDPWD/scripts/push_clean.sh`).** Reviewed
statically.

**F21 — INFO · unauthenticated off the proxy.** `GH_TOKEN`/`GITHUB_TOKEN` are unused; the repo is public, so a plain shell reads
under 60/h; a 403 there fails closed (F17). Not measured against GitHub from a non-proxied shell.

**F22 — INFO · record trust:** `run_number` sorted as given (G:33 `key=lambda r: r["run_number"]`; strings sort lexically),
duplicates resolve by list order, re-runs by each record's own status (0 re-runs live).

**F23 — UNVERIFIED · a DNS stall or a slow-drip body is not bounded by the 20 s timeout.** Not measured.

CONTRACT-DEFECT: none (no exact-production-path defect that falsifies evidence, corrupts state or loses data in the measured
production state).

## GATE RECOMMENDATION

**MERGE-READY-WITH-FOLLOWUPS** — no finding meets the full blocking predicate in the measured production state (this sandbox's
clone: full, default refspec). This rests on one thing NOT reproduced: the state of any OTHER clone that runs push_clean (the PC
clone was not measured — no bridge use). If a push venue is shallow, has a narrowed fetch refspec, or carries a local
`origin/<branch>` branch, F1 blocks. Also resting on documentation only: F14 (cancelled-run mails) and F15 (mixed pushes).
Follow-up rows for the coordinator (D-034): F1, F2, F3, F4, F5, F6, F7, F8, F10, F13; INFO: F9, F11, F12, F16-F22;
UNVERIFIED: F14, F15, F23.

Mutant tally: brief set M1-M10 = 11 rows, 9 KILLED, 2 SURVIVED (M6b safe-direction; M10 equivalent on today's data); extras
X1-X8 = 1 KILLED, 7 SURVIVED; every kill re-checked green on the unmutated tree (15 passed).

## NOT-done

- No PC or bridge use: the PC clone's depth, refspec and branches (F1's trigger) and an unauthenticated API read from a
  non-proxied shell (F21) are unmeasured.
- No push to the real origin: mixed-push `paths-ignore` semantics (F15), a new branch's first push and live `cancel-in-progress`
  behaviour rest on the GitHub docs; the transcripts-only case is verified from the existing live history.
- The owner's notification setting (F14) — not measurable; the owner's mailbox was not read.
- DNS stalls and slow-drip bodies (F23) not measured; re-run semantics rest on the documented schema (0 live re-runs).
- The `--lanes-live` leak was measured on a throwaway repo; the real repo shows one worktree (no leak today).
- Only the two files under review were run (37 tests, on the repo and on the scratch copy); the full suite was not.
- No `/bug-echo`, registry row or incident entry (boundary: this report only) — F1's class (a check that reads "cannot tell" as a
  negative) is the coordinator's to register.
- Scratch state left for inspection under `/tmp/vcig/` (probes, mutants, pack). The probe's own leaked worktree
  (`/tmp/push-clean-wt.SR7M0e`, registered in the throwaway repo `/tmp/vcig/probes/int/l`) was removed after the evidence was
  pasted; no `/tmp/push-clean-wt.*` directory remains. This repository's tree: only this report is mine (07:39:18Z
  `git status`: the other lanes' S0-05 edits and reports untouched; one worktree).

## Lint (pasted; two fix rounds of the three allowed)

````
$ python3 scripts/report_lint.py --min-refs 12 --map G=scripts/ci_gate.py --map PCL=scripts/push_clean.sh --map T=tests/test_ci_gate.py --map W=.github/workflows/stage0-ci.yml --map TW=tests/test_stage0_ci_workflow.py tasks/briefs/ci/VERIFY-CI-GATE-report.md --root .
report_lint: 116 refs — OK 116, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
````
