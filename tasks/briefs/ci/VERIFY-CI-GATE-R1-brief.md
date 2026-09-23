# VERIFY-CI-GATE-R1 — the targeted verify of the push gate's one focused repair (task #171; issue #34)

PIN: the origin commit of the local f77563f "CI-GATE-R1 landed (task #166, issue #34): …" (push_clean rewrites the unpushed range, so
the dispatch prompt names the post-push SHA; the five files below are measured on f77563f, and push_clean proves tree identity across
its rewrite).
LANE: verify-ci-gate-r1 (sandbox; agent `adversarial-verifier` on the D-054 pin). Honey `full`: line-bounded findings, evidence
anchors, SOLID/UNSURE. Do NOT spawn subagents.

WHY THIS LANE EXISTS: CI-GATE-R1 is the ONE focused repair (D-031) of VERIFY-CI-GATE's findings (issue #34). The builder's own gates
(129 passed twice, 39/39 mutants) and the coordinator's re-run of them are one oracle run twice (rule 0f). This gate decides every
push the coordinator makes; its purpose is the owner's: no push onto a red or unknown head, so no "Run failed" mail floods the owner's
inbox. A wrong 0 costs the owner an inbox; a wrong 1, 2 or 75 blocks the coordinator's pushes.

THE CONTRACT: `tasks/briefs/ci/CI-GATE-R1-brief.md` C1-C7 (read it WHOLE, with its "WHAT IS DECIDED" block: do not re-decide those
rulings, grade the code against them). The builder's report `tasks/briefs/ci/CI-GATE-R1-report.md` is a CLAIM to test, never evidence:
its DISCREPANCIES D1-D8 are readings you grade one by one (accept, or a finding with its reproduction). The prior verify's findings are
`tasks/briefs/ci/VERIFY-CI-GATE-report.md` F1-F23.

ITEMS (report every observation, no severity filter; the predicate and the recommendation come at the end):
1. PREMISE: re-measure the block below on the PIN. A mismatch not explained by a commit you can name stops the lane CONTRACT-INVALID.
2. C1-C2, with NEW shapes (never the builder's rows): hostile run records (every key missing in turn; `id` a float, a huge int, a
   negative; `run_number` 0 or negative; `head_sha` with a trailing newline, 40 hex plus one; `status`/`conclusion` of other JSON
   types; `head_branch` differing only in case or trailing space; a payload that is a list, `null`, a string, `total_count` absent,
   `workflow_runs` not a list); histories (a run's sha reachable only through a merge's second parent; a force-moved origin where an
   older red run's commit left the history; a red run followed by a green run for an older commit; the run for the exact head in
   progress while an older green run exists; `cancelled` then `success`; a `skipped` or `neutral` conclusion; `timed_out`,
   `action_required`, `stale`, `startup_failure`). For each: the exit code and text the contract demands, the one the gate gives, through
   the REAL CLI (a throwaway repo under `/tmp/vcg1/` with `--runs-json` and a non-github origin, as the tests do).
3. The expected-run check (C2 f) on real git: a push that changes only files under `transcripts/`; only `.github/`; a path named
   `transcripts` at the root (a file, not the directory); `transcripts2/x`; a submodule change; a mode-only change; a deleted file; a
   path with a newline or a non-ASCII byte. Which of these start a real workflow run (read the workflow's triggers and GitHub's
   documented `paths-ignore` semantics) and does the gate's answer match? A mismatch either way is a finding: a missed run means a wrong
   0 (the owner's inbox), a phantom run means a stuck 75.
4. The tri-state history filter (C2 e) and D1: reproduce the builder's measurement (a deleted parent object; three commit-date orders)
   on git 2.43 here, then attack: a missing TREE or BLOB object (not a commit); a corrupt pack; an `objects/info/alternates` that
   points nowhere; a grafted or replaced commit (`git replace`); `GIT_DIR`/`GIT_WORK_TREE` set in the caller's environment. Which of
   these can make the gate read a red run as "not in history" and so allow?
5. C3/C4 — the API read and the waiter, in-process with the network and the clock replaced (never the live API in a loop): an HTTP 200
   whose body is not JSON; a body cut mid-JSON; a redirect; a 304; `Retry-After`; a slow body past the 20 s timeout; the waiter across
   a run that goes in_progress → completed/cancelled → a newer run registered; a deadline of 0 and of 1; a KeyboardInterrupt (the
   builder lists a traceback as NOT-done: confirm and classify). ONE live GET of this repository's runs (read-only) to confirm the query
   shape on the real API; never re-run, cancel or dispatch a workflow.
6. C5 — push_clean.sh, ONLY in throwaway repos whose origin is a bare repository under `/tmp/vcg1/` (the pattern of
   `tests/test_ci_gate.py`'s push_clean tests): the FETCH_HEAD equality under a narrowed refspec, under a `remote.origin.fetch` with
   two lines, under a `url.<base>.insteadOf` rewrite, and after `git fetch` fails (network down: an origin path that does not exist);
   a local branch or tag named `origin/<branch>`; `--lanes-live` where the inner run fails at each stage (the gate, the trailer check,
   the push) and `git worktree list` afterwards; `--lanes-live` with a dirty working copy of `scripts/ci_gate.py` declared in
   `.lanes-live` (the committed bytes must decide). Does the gate's code pass through unchanged at every exit?
7. C6 — the workflow pin: does `tests/test_stage0_ci_workflow.py` read BOTH triggers' `paths-ignore` from the parsed YAML, so a
   comment-only or a reordering edit cannot satisfy it while a real change does not? Run one scratch mutant each way.
8. D1-D8: grade each against the contract text, with a reproduction where the reading changes an exit code.
9. Mutation audit with NEW rows (not R1-R25 or X1-X14), in scratch copies only (`/tmp/vcg1/mut/`): at least one per contract line
   C1-C6 and one per D-reading you accept. Each mutant compiles (`python3 -m py_compile` / `bash -n`) and its suite collects (AF-AP-78);
   before you count a kill, run the killing test on the UNMUTATED copy and paste that it passes (AF-AP-138). A survivor is a finding.
10. Issue #34's ledger: for each of F1-F23, CLOSED (with the test that pins it on the PIN) or OPEN (with its current reproduction). The
   builder lists F10 (PR runs), F12 (part), F13 (docs: the coordinator added the CLAUDE.md push bullet and the wiki line in the landing
   commit), F14-F16, F18 (runtime half), F21-F23 as open.

BOUNDARY: CREATE `tasks/briefs/ci/VERIFY-CI-GATE-R1-report.md` and write it incrementally. Nothing else in the repository: `scripts/`,
`tests/` and `.github/` are READ-ONLY for you (the coordinator pushes through these exact scripts while you work). Scratch, throwaway
repositories, bare origins, mutants and basetemps live under `/tmp/vcg1/` and are removed when you are done (the sandbox had 1.4 GB
free at authoring). pytest: `-p no:cacheprovider --basetemp=/tmp/vcg1/bt<n>`, removed after each run.

STANDING DO-NOTS: never run `scripts/push_clean.sh`, `git push`, `git fetch`, `git pull`, `git commit`, `git stash`, `git checkout
-- …`, `git restore`, `git worktree add|remove|prune` or any command that moves a ref in `/home/user/agent-factory`: that tree's origin
is the REAL remote. Every push_clean run and every git mutation happens in a throwaway repository under `/tmp/vcg1/` whose origin is a
bare repository under `/tmp/vcg1/`. Other sandbox agents work in the shared tree on disjoint files (`proofs/S0-02/`, `proofs/S0-05/`,
their tests, `tasks/briefs/s0-02-support/`, `tasks/briefs/s0-05-support/`, `tasks/briefs/laya/`, `tasks/briefs/hermes-repin/`,
`tasks/briefs/continuity/`, `upstream.lock.yaml`, `docs/HARNESS-PORTS.md`, `tests/test_upstream_lock_lane_runtime.py`): never touch,
run or revert them. READ-ONLY on the real remote: GET requests to `api.github.com` for this repository's runs and jobs only; never
re-run, cancel or dispatch a workflow; never open, edit or comment on an issue or PR. No PC or bridge use. No outward-facing action.

CODE INTEL FIRST: `graft ask` before any grep for code questions;
`scripts/lane_context.sh -q 'how does the push gate decide from the runs and the history' -s _decide -s valid_runs -s in_history -s first_change_after -s _wait -o /tmp/vcg1/pack.md scripts/ci_gate.py scripts/push_clean.sh`.

PREDICATE: a finding blocks only if it is contract-mapped (C1-C7 or a WHAT IS DECIDED ruling), reproduced through the real CLI or the
real push_clean in a throwaway repo, materially effective (a wrong exit code on a reachable input: a 0 where the contract demands a
refusal is the worst class), with a concrete discriminator, and in-boundary for the repair (the five files). Everything else is a
follow-up. ONE GATE RECOMMENDATION per component: (a) `scripts/ci_gate.py` decide/validate, (b) the waiter, (c) `scripts/push_clean.sh`,
(d) the workflow and its pin — each `MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`. The coordinator
owns the final gate.

Report lint: `python3 scripts/report_lint.py --min-refs 20 tasks/briefs/ci/VERIFY-CI-GATE-R1-report.md --root .` (no `--map` flags;
cite full repo-relative paths); apply its `fix:` hints for at most three rounds, then paste and finish. The report ends with
DISCREPANCIES and NOT-done.

## PREMISE — MEASURED at authoring (2026-09-23 09:33Z, sandbox @ f77563f, local; the post-push SHA is named at dispatch)
```
$ date -u
Wed Sep 23 09:33:03 UTC 2026
$ git rev-parse --short HEAD; git log -1 --format=%s | cut -c1-90
f77563f
CI-GATE-R1 landed (task #166, issue #34): the push gate waits (exit 75) while the pushed h
$ for f in <the five>; do blob at f77563f, sha256 prefix, lines; done
7a0bb510406d d868ae9004186d48 116 .github/workflows/stage0-ci.yml
12b792fa794a f1e2246f043ff702 398 scripts/ci_gate.py
dae355ad2e17 4e835e99bdf2a86e 128 scripts/push_clean.sh
1ca772706916 70c04c384332b61d 843 tests/test_ci_gate.py
7a2f4a8b422d 25b8c7ceeab3e921 129 tests/test_stage0_ci_workflow.py
$ git diff --quiet f77563f -- <the five> && echo tree == f77563f
tree == f77563f on the five
$ grep -n "^def \|^class " scripts/ci_gate.py
76:class DataError(Exception):
80:class GitError(Exception):
84:def _git(root, *args):
94:def _error_line(stderr):
98:def check_clone(root):
110:def resolve_commit(root, ref):
118:def origin_url(root):
123:def repo_slug(root):
132:def _get_json(url):
144:def fetch_runs(repo, branch):
149:def fetch_jobs(repo, run_id):
157:def _is_int(value):
161:def valid_runs(payload, branch):
192:def read_runs(root, branch, runs_json=None):
205:def in_history(root, sha, origin_sha):
220:def first_change_after(root, sha, origin_sha):
229:def decide(runs, is_ancestor, ci_fix="", change_after=lambda sha: None):
234:def _decide(runs, is_ancestor, ci_fix, change_after):
266:class _Parser(argparse.ArgumentParser):
272:def _seconds(text):
282:def _say(rc, text, err=False):
287:def _body(text):
291:def _wait_hint(args, ref):
303:def _print_failed_jobs(root, run):
314:def _wait(args, verdict, hint):
346:def main(argv=None):
$ grep -c "^def test" tests/test_ci_gate.py tests/test_stage0_ci_workflow.py
tests/test_ci_gate.py:55
tests/test_stage0_ci_workflow.py:12
$ git config --get-all remote.origin.fetch; git rev-parse --is-shallow-repository
+refs/heads/*:refs/remotes/origin/*
false
$ git --version
git version 2.43.0
$ for i in 1 2; do /root/venv-agent-factory/bin/python -m pytest tests/test_ci_gate.py tests/test_stage0_ci_workflow.py -q -p no:cacheprovider --basetemp=/tmp/cg1/bt$i | tail -1; done
129 passed in 13.04s
129 passed in 14.06s
$ bash scripts/pc_suite.sh set-id -- tests/test_ci_gate.py tests/test_stage0_ci_workflow.py
2 files set=f94590af83b6
$ python3 scripts/ci_gate.py --branch claude/soundbox-kit-migration-iz1jwf --origin-ref refs/remotes/origin/claude/soundbox-kit-migration-iz1jwf; echo "gate rc=$?"   (09:2xZ)
WAIT by ci-gate: run #977 (8aa4577) is in_progress — https://github.com/Pxls21/agent-factory/actions/runs/35841647411
Wait for the verdict: python3 scripts/ci_gate.py --branch claude/soundbox-kit-migration-iz1jwf --wait 1800
or push without waiting: CI_WAIT_SKIP=<reason>
gate rc=75
$ df -h /tmp | tail -1   (09:3xZ)
/dev/vda        252G   36G  1.4G  97% /
```
