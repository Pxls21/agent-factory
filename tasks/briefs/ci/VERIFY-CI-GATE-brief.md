# VERIFY-CI-GATE — the push gate that reads the branch's last stage0-ci verdict (AF-AP-126 mechanized; task #163)

PIN: 148e38d (origin head at authoring; every file below is byte-identical to HEAD, measured in the premise block).
LANE: verify-ci-gate (sandbox; agent `adversarial-verifier`, in the SHARED tree, no worktree isolation). Honey `full`: line-bounded
findings, evidence anchors, SOLID/UNSURE. Do NOT spawn subagents.

WHAT LANDED (the coordinator's own work, graded so far only by its own tests — rule 0f: GATED-PENDING-VERIFY until you return):
- `scripts/ci_gate.py` (new, commit 3b4adb9 → 010d1bc on origin): reads the branch's stage0-ci push runs through the Actions API and
  decides from the newest run whose head commit is in `origin/<branch>`'s history: success → allow; queued/in progress → allow ("this
  push supersedes it"); cancelled → skip to the next older run; any other completed result → REFUSE (exit 1) unless `CI_FIX` equals
  that run's id; no run in the history → allow with a note; an unreadable API → exit 2, or a loud warning and exit 0 when
  `CI_GATE_OFFLINE=<reason>` is set.
- `scripts/push_clean.sh:69-70`: calls the gate after its fetch (`:60`) and before any rewrite or push (`:92`), `|| exit $?`.
- `.github/workflows/stage0-ci.yml:3-15`: `paths-ignore: ['transcripts/**']` on push (a transcripts-only push runs no CI) and
  `concurrency` with `cancel-in-progress: true` per ref.
- Tests: `tests/test_ci_gate.py` (27, incl. one that drives the REAL push_clean.sh against a throwaway bare origin) and two new cases in
  `tests/test_stage0_ci_workflow.py`.
- The OWNER's goal (2026-09-23, the third time): no more "Run failed: stage0-ci" mails from pushes onto a red head. The procedural rule
  the gate mechanizes: read each pushed head's CI run to its conclusion before the next push (CLAUDE.md, the push bullet).

BOUNDARY: CREATE `tasks/briefs/ci/VERIFY-CI-GATE-report.md` (write it incrementally from the start); nothing else. Mutants run in
scratch copies only (never a git restore in this shared tree; each mutant compiles and collects, AF-AP-78). Another sandbox agent runs
in this tree on disjoint files (`proofs/S0-05/`, `tests/test_s0_05_egress.py`, `tasks/briefs/s0-05-support/`): never touch, run or
revert them. Never run `git stash`, `git checkout -- …`, `git restore`, `git add`, `git commit` or `git push` in this tree. READ-ONLY on
the real remote: GET requests to `api.github.com` for this repository's runs are allowed (they are how the gate works); never push to
origin, never re-run, cancel or dispatch a workflow, never open, edit or comment on an issue or PR. Any push test uses a throwaway bare
repository under `/tmp`. No PC or bridge use.

CODE INTEL FIRST: `graft ask` before any grep for code questions; `scripts/lane_context.sh -q 'how does push_clean decide whether to
push' -s decide -s main -s fetch_runs -o /tmp/vcig/pack.md scripts/ci_gate.py scripts/push_clean.sh`.

## Items (attack the whole contract, not the builder's cases; report EVERY observation, no severity filter)

1. PREMISE: re-run the premise commands below on the PIN; stop CONTRACT-INVALID on a mismatch that changes this brief.
2. The decision table against its docstring (`ci_gate.py:8-17`): every status/conclusion GitHub can return (read the Actions API
   documentation or measure), malformed run records (a missing key, a null conclusion on a completed run, a non-string sha), an empty
   list, duplicate run numbers, a re-run (`run_attempt` > 1) whose latest attempt differs from its first. Does every path end in a NAMED
   verdict (exit 0/1/2 with its text), or can one end in a traceback? A traceback is exit 1 by accident, not by design.
3. The history filter (`ci_gate.py:73-75`): a run whose sha is absent locally, a stale or missing `origin/<branch>` ref, a rewritten
   (force-pushed) branch, merge commits, a shallow clone (measured: this clone is not shallow). Can a red verdict be skipped so that an
   older green one, or "no run", allows the push?
4. The in-progress allow: can a sequence of pushes proceed with no verdict ever read, and is that consistent with the procedural rule it
   mechanizes (read each pushed head's run to its conclusion before the next push)? Measure it with fixture runs. Weigh it against the
   workflow's `cancel-in-progress` (a cancelled run never mails) and against push_clean's own transcripts push (`:98-105`, which does not
   call the gate). Do not decide the policy: state what the gate allows, what the rule says, and the concrete sequence that separates them.
5. The API read (`ci_gate.py:59-62`): no Authorization header is sent. Measured below: through this sandbox's proxy the call is
   authenticated (limit 15000). What does the gate do where it is NOT (the PC, a plain shell): a private repository's 404, the 60-per-hour
   limit's 403, a 5xx, a timeout, a redirect? `per_page=50` newest first: can the verdict run fall off the page? The branch name is not
   URL-encoded: which branch names break the query?
6. push_clean integration: the gate's position (after the fetch, before the rewrite and the push); does `|| exit $?` keep 1 and 2
   distinct to the caller; the `--lanes-live` path (`:22-46`: the push runs from a detached worktree — does the gate run there against
   the right ref and root?); `set -euo pipefail` (`:12`) with the gate's exit.
7. The environment channels: `CI_FIX` (whitespace, a stale id left in a shell, a non-numeric value), `CI_GATE_OFFLINE` (whitespace-only
   counts as unset?), and `CI_GATE_RUNS_JSON` (`push_clean.sh:67-70`: a test input reachable in production — can it make an unread verdict
   pass quietly? what does the operator see?).
8. The workflow half: paths-ignore semantics (a push that changes transcripts AND a code file must still run CI; a push whose commits
   touch only transcripts must not; a new branch's first push), the concurrency group (a pull_request run is in another group), and the
   two exact-shape tests in `tests/test_stage0_ci_workflow.py:58-71` — do they pin behaviour or only text?
9. Mutation audit (scratch copies): at least M1 the history filter removed · M2 a cancelled run refused · M3 a cancelled run read as a
   verdict (allow) · M4 an in-progress run refused · M5 the newest chosen by list order · M6 `CI_FIX` compared without `str()` or without
   `.strip()` · M7 the push_clean call moved after the push · M8 `|| exit $?` → `|| true` · M9 the offline branch allowing without the
   variable · M10 `event=push` dropped from the query. One row each: mutant · compiles · collected · killed-by (test id) / SURVIVED /
   EQUIVALENT with the reason. Before you count a kill, run the killing test on the UNMUTATED tree and paste that it passes (AF-AP-138).
10. Anything else you find.

## Verdict

Apply the blocking predicate (contract-mapped · reproduced through the real code path · materially effective · a concrete discriminator ·
in the boundary of what landed) and return a GATE RECOMMENDATION: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID.
Every non-blocking finding is a follow-up row (the coordinator files it as a `verify-followup` issue, D-034).

## Report (`tasks/briefs/ci/VERIFY-CI-GATE-report.md`)

PREMISE re-measured · each item with its evidence (commands and output pasted, file:line refs) · the mutant table · findings ranked,
each with the blocking predicate applied · the gate recommendation · NOT-done. Lint floor: `python3 scripts/report_lint.py --min-refs 12
--map G=scripts/ci_gate.py --map PCL=scripts/push_clean.sh --map T=tests/test_ci_gate.py --map W=.github/workflows/stage0-ci.yml
--map TW=tests/test_stage0_ci_workflow.py tasks/briefs/ci/VERIFY-CI-GATE-report.md --root .`; apply its `fix:` hints for at most three
rounds, then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23 07:07Z, sandbox @ 148e38d)

````
$ date -u '+%Y-%m-%d %H:%MZ'
2026-09-23 07:07Z

$ git rev-parse origin/claude/soundbox-kit-migration-iz1jwf
148e38dc044d576e1f9b2c75e8f7602baaf6c653

$ git diff --stat origin/claude/soundbox-kit-migration-iz1jwf HEAD -- scripts/ci_gate.py scripts/push_clean.sh tests/test_ci_gate.py .github/workflows/stage0-ci.yml tests/test_stage0_ci_workflow.py | wc -l
0

$ for f in scripts/ci_gate.py scripts/push_clean.sh tests/test_ci_gate.py .github/workflows/stage0-ci.yml tests/test_stage0_ci_workflow.py; do printf '%s %s %s\n' "$(sha256sum < $f | cut -c1-16)" "$(wc -l < $f)" "$f"; done
f19a6cbb99ea10b0 100 scripts/ci_gate.py
ab2412d387131433 109 scripts/push_clean.sh
e9def321313dccaa 184 tests/test_ci_gate.py
718365358d1e855b 112 .github/workflows/stage0-ci.yml
0f0c020fcf227103 111 tests/test_stage0_ci_workflow.py

$ git log --format='%h %s' -3 -- scripts/ci_gate.py scripts/push_clean.sh
010d1bc Push gate: push_clean refuses while the branch's last stage0-ci run is red (AF-AP-126 mechanized; task #162)
75f3e3a push_clean: rewrite ONLY commits that carry a model-identifier trailer — a foreign commit keeps its object id (the owner's signed-key commit 80422cb had been rewritten to e719da8, orphaning the tag accepted/S0-11); pre-push: a NEW ref is ranged against what origin already has, not its whole history (the tag push was blocked by 22 trailer lines in commits on origin for days); AF-AP-69; the governance procedure amended
303600a briefs: lane N5f — the probe's LATER interpreter reading wins, the crash path writes a complete evidence set, reason strings pinned exactly (VERIFY-N5e round 9); push_clean --lanes-live follows origin's rewritten SHA

$ grep -n 'set -e\|git fetch\|ci_gate.py\|CI_GATE_RUNS_JSON\|git push' scripts/push_clean.sh
12:set -euo pipefail
60:git fetch origin "$BRANCH"
67:# last stage0-ci verdict is red, unless the push names the red run it fixes (CI_FIX=<run id>). CI_GATE_RUNS_JSON is a
69:python3 "$(dirname "$0")/ci_gate.py" --branch "$BRANCH" --origin-ref "origin/$BRANCH" \
70:  ${CI_GATE_RUNS_JSON:+--runs-json "$CI_GATE_RUNS_JSON"} || exit $?
92:git push -u origin "$SHA:refs/heads/$BRANCH"
103:      && git push -q origin "$(git rev-parse HEAD):refs/heads/$BRANCH" \

$ mkdir -p /tmp/vcig/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_ci_gate.py tests/test_stage0_ci_workflow.py -q -p no:cacheprovider --basetemp=/tmp/vcig/bt 2>&1 | tail -1; rm -rf /tmp/vcig
37 passed in 1.11s

$ curl -sS -o /dev/null -D - 'https://api.github.com/repos/Pxls21/agent-factory/actions/workflows/stage0-ci.yml/runs?branch=claude/soundbox-kit-migration-iz1jwf&event=push&per_page=1' | grep -i '^HTTP\|^x-ratelimit-limit\|^x-ratelimit-remaining\|^x-ratelimit-resource'
HTTP/1.1 200 Connection Established
HTTP/1.1 200 OK
X-Ratelimit-Limit: 15000
X-Ratelimit-Remaining: 14998
X-Ratelimit-Resource: core

$ git rev-parse --is-shallow-repository; git rev-list --count origin/claude/soundbox-kit-migration-iz1jwf
false
1154
````
