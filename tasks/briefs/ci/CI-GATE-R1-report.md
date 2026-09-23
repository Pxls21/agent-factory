# CI-GATE-R1 — report (lane ci-gate-r1, task #166, issue #34; sandbox, Opus 5.5)

STATUS: DONE (tests green, not committed) 2026-09-23 09:24Z. C1-C7 built in the five boundary files; both test files 129 passed
twice (set f94590af83b6); mutation audit 39/39 KILLED (R1-R25 + X1-X14), 0 SURVIVED, 0 INVALID; one live GET + one live decision
(rc 75: run #976 in progress). Eight discrepancies (D1-D8), one flaky test found and fixed (section 8). NOT-done at the end.

Scope: G=`scripts/ci_gate.py` · PCL=`scripts/push_clean.sh` · T=`tests/test_ci_gate.py` · W=`.github/workflows/stage0-ci.yml` ·
TW=`tests/test_stage0_ci_workflow.py`. Venue: the private worktree `/tmp/wt-ci166` (detached at origin head c269263).

## 1. PREMISE — re-measured in the worktree (2026-09-23 08:29Z)

````
$ date -u '+%Y-%m-%d %H:%M:%SZ'
2026-09-23 08:29:56Z
$ git rev-parse HEAD ; git rev-parse --abbrev-ref HEAD ; git rev-parse refs/remotes/origin/claude/soundbox-kit-migration-iz1jwf
c269263fbc9935d0f668628704ca933a85149380
HEAD
c269263fbc9935d0f668628704ca933a85149380
$ git status --porcelain | head          # (empty)
$ git diff ae16c6a HEAD -- <the five files> | wc -l
0
$ for f in <the five files>; do sha256 lines path; done
f19a6cbb99ea10b0 100 scripts/ci_gate.py
ab2412d387131433 109 scripts/push_clean.sh
e9def321313dccaa 184 tests/test_ci_gate.py
718365358d1e855b 112 .github/workflows/stage0-ci.yml
0f0c020fcf227103 111 tests/test_stage0_ci_workflow.py
$ git rev-parse --is-shallow-repository ; git config --get-all remote.origin.fetch
false
+refs/heads/*:refs/remotes/origin/*
$ git worktree list
/home/user/agent-factory  c269263 [claude/soundbox-kit-migration-iz1jwf]
/tmp/wt-ci166             c269263 (detached HEAD)
$ /root/venv-agent-factory/bin/python -m pytest tests/test_ci_gate.py tests/test_stage0_ci_workflow.py -q -p no:cacheprovider --basetemp=/tmp/ci166/bt0 | tail -3
37 passed in 1.17s
rc=0
$ bash scripts/pc_suite.sh set-id -- tests/test_ci_gate.py tests/test_stage0_ci_workflow.py
2 files set=f94590af83b6
````

Reading: the five files are byte-identical to the brief's PIN ae16c6a (same sha256 prefixes and line counts as the brief's
premise block); origin moved ae16c6a → c269263 without touching them. The landed count (37) and the set id (f94590af83b6)
match the brief. The brief stands.

## 2. Code intel and the measured git seams (before any edit)

Pack: `scripts/lane_context.sh -q 'how does push_clean decide whether to push' -s decide -s main -s fetch_runs -s repo_slug
-o /tmp/ci166/pack.md scripts/ci_gate.py scripts/push_clean.sh` → rc 0, 149 lines. graft skeleton G (as landed): `decide`
L31-L47, `repo_slug` L50-L56, `fetch_runs` L59-L62, `main` L65-L96, `is_ancestor` L73-L75. GitNexus impact upstream:
`decide` / `fetch_runs` / `repo_slug` LOW (one direct caller, `main`); `main` UNKNOWN (the name is ambiguous across the repo) →
confirmed by a literal sweep (`ci_gate|CI_GATE_|CI_WAIT_SKIP|CI_FIX` over code): the only code consumers are PCL and T.
crg `tests_for(fetch_runs)` = 0, `tests_for(repo_slug)` = 0 (the verifier's F4, re-read). AP screen: AP-1 ×2, the two
`os.environ.get` reads (landed G@c269263:85 `CI_GATE_OFFLINE` and G@c269263:94 `CI_FIX`); C2 keeps env reads, now once.

Git seams, measured on throwaway repos (git 2.43.0, this sandbox; scripts `/tmp/ci166/probe{1,2,3}`):
````
merge-base --is-ancestor: clean ancestor rc=0 stderr 0 bytes · clean not-ancestor rc=1 stderr 0 bytes · absent sha rc=128
cat-file -e <absent>^{commit}: rc=128 · cat-file -e <present commit>^{commit}: rc=0 · a blob sha: merge-base 128, cat-file ^{commit} 128
--- a parent object deleted (A, parent of B; B is C's parent, a TRUE ancestor):
B vs C: rc=1 stderr=[error: Could not read 54bd8638d348f4e35b4585509362c35a9fb8a3d5]
X vs C: rc=1 stderr=[error: Could not read 54bd8638d348f4e35b4585509362c35a9fb8a3d5]
a literally written bogus commit: cat-file -e ^{commit} rc=128 ("bogus commit object"), merge-base rc=128
rev-parse --verify --quiet refs/remotes/origin/nope^{commit}: rc=1 · '--help^{commit}': rc=1 · outside a repo: is-shallow rc=128
clone --depth 1 <local path>: "warning: --depth is ignored in local clones; use file:// instead." → not shallow; file:// → true
rename code/a.py -> transcripts/a.py: default --name-only "t.txt transcripts/a.py" · --no-renames "code/a.py t.txt transcripts/a.py"
non-ASCII path without -z: "transcripts/\303\251.md" (quoted) · with -z: raw bytes
narrowed refspec (+refs/heads/main:…) after 'git fetch origin feat': tracking=39986d3 FETCH_HEAD=2fcdd6e (stale) · default: both 2fcdd6e
local branch 'origin/feat': rev-parse origin/feat -> "warning: refname 'origin/feat' is ambiguous." + the local branch's sha
````
Reading, for the design:
- On git 2.43 a failed history walk (a missing parent object) can exit **1**, not 128, with `error: Could not read …` — for a
  TRUE ancestor too. Read by exit code alone, that is F1's class again ("cannot tell" read as "not in history"). The gate
  reads exit 1 as "not in history" only when git printed no `error:`/`fatal:` line (git runs under `LC_ALL=C`, so the prefix
  is the English one). This is my reading of C2 e's "ANY other outcome → 2"; flagged under DISCREPANCIES (D1).
- The answer depends on the walk ORDER, which follows commit dates (found later, from a flaky gate run; section 8). Measured
  with pinned dates, the same deleted parent A, B the parent of C:
  ````
  B=2026-09-23T00:00:00+00:00 C=2026-09-23T00:00:00+00:00 -> merge-base --is-ancestor B C rc=1 stderr=[error: Could not read 40188f476af41f0738aff2facb16ea20acefba9b]
  B=2026-09-23T00:00:00+00:00 C=2026-09-23T00:00:01+00:00 -> merge-base --is-ancestor B C rc=0 stderr=[error: Could not read 40188f476af41f0738aff2facb16ea20acefba9b]
  B=2026-09-23T00:00:01+00:00 C=2026-09-23T00:00:00+00:00 -> merge-base --is-ancestor B C rc=1 stderr=[error: Could not read 40188f476af41f0738aff2facb16ea20acefba9b]
  ````
  Exit 0 with an error line is sound (inferred from git's walk: B is marked from C only through a parent edge git read); the
  gate reads any exit 0 as "in history".
- "Exit 128 with the object present" (mutant R3's scenario) did not occur through real git 2.43 in any probe: a missing parent
  gives 1 or 0 with an error line, an unparseable commit also fails `cat-file -e ^{commit}` (so it reads as absent). The R3 kill
  uses an injected exit code at the git seam (T, in-process); the real-git missing-parent test covers the error-line path.
- `--depth` needs a `file://` URL in a test clone; the diff needs `-z` (a quoted non-ASCII transcripts path would read as code).

## 3. Per contract line — files:lines and the tests that pin each

**C1 — exit codes and texts.**
- Codes: G:64 `USAGE, WAIT = 64, 75`. Every verdict leaves through G:282 `def _say`, which prints to stdout only for a plain 0:
  G:283 `print(text, file=sys.stderr if rc or err`.
- argparse errors exit 64: G:266 `class _Parser`, G:269 `self.exit(USAGE`. Pinned by T:582 `test_usage_errors_exit_64` (5 shapes).
- The landed red refusal is kept byte for byte: G:259 `Read its failed jobs first` (T:52 `test_failure_refuses_and_names_the_run`).
- The landed CI_FIX allow is kept: G:257 `declares this push fixes it` (T:64 `test_ci_fix_naming_the_red_run_allows`).
- A 75 names its run (G:243 `is {status}`) or its pushes (G:252 `the pushes after`).
- Every 75 in push mode gets the waiter command and the escape: G:291 `def _wait_hint`, G:300 `or push without waiting`.
  Pinned exactly by T:208 `test_cli_waits_while_the_verdict_run_is_unfinished`; at the deadline by T:674 `test_the_waiter_stops_at_its_deadline`.
- Every 2 names its cause: a local git failure is a G:80 `class GitError`, the API's data a G:76 `class DataError`.
- No traceback: T:295 `test_cli_validates_every_record_before_deciding` asserts `"Traceback" not in` stderr for 17 broken records.

**C2 — the decision, in order.**
- a · G:98 `def check_clone`; the fix text G:105 `git fetch --unshallow origin`; it runs first (G:359 `check_clone(args.root)`).
  T:342 `test_cli_refuses_a_shallow_clone_even_offline`: a real `git clone --depth 1 file://…`, 2 with and without CI_GATE_OFFLINE.
- b · G:110 `def resolve_commit`; the sha is resolved once and threaded to every later git call (G:360 `origin_sha = resolve_commit`).
  T:331 `test_cli_refuses_an_origin_ref_that_is_not_a_commit`: 2 with and without CI_GATE_OFFLINE (the landed gate allowed).
- c · `--runs-json` against a github.com origin: G:364 `if GITHUB.search(origin_url` → G:365 `return _say(USAGE`.
  Any other origin: the notice goes to stderr, G:367 `WARNING: ci-gate: runs read from`.
  A read failure is 2; CI_GATE_OFFLINE makes it 0 with G:387 `WARNING: ci-gate could not read the runs`.
  T:560 `test_runs_json_never_decides_against_a_github_origin`, T:569 `test_runs_json_with_a_local_origin_says_so_on_stderr`,
  T:168 `test_cli_fails_closed_when_the_runs_cannot_be_read` (landed, unchanged).
- d · G:161 `def valid_runs`: the keys (G:68 `KEYS = (`), each field's type and value (G:176 `for key, ok, wanted in`).
  `head_branch` equals `--branch`: G:182 `("head_branch", run["head_branch"] == branch`; `event` is push: G:183 `("event", run["event"] == "push"`.
  A repeated `run_number`: G:186 `at = first_at.setdefault`.
  T:295 `test_cli_validates_every_record_before_deciding` (17 broken records: 2 naming `workflow_runs[0]` and the field, each rescued by CI_GATE_OFFLINE),
  T:316 `test_cli_refuses_a_payload_without_a_run_list`, T:324 `test_cli_refuses_a_repeated_run_number`.
- e · G:205 `def in_history`: exit 0 → in; exit 1 with no `error:`/`fatal:` line → out (G:211 `if rc == 1 and error is None`).
  The commit object absent → out (G:213 `cat-file`); anything else → G:216 `git cannot tell whether commit`, naming the sha and git's code.
  Cancelled runs are skipped before any history read (G:236 `"cancelled"`).
  T:160 `test_cli_reads_ancestry_from_git` (landed; its verdict kept: an absent object is not in history),
  T:356 `test_cli_refuses_when_git_cannot_walk_the_history` (real git, a parent object deleted, dates pinned),
  T:374 `test_an_ancestry_read_that_exits_128_on_a_present_commit_refuses` (exit 128 injected at the git seam).
- f · unfinished → 75: G:242 `if status in UNFINISHED` (the list at G:67 `UNFINISHED = (`).
  Another status → 2: G:244 `if status != "completed"`. Completed with no conclusion → 2: G:246 `if conclusion is None`.
  The expected-run check: G:252 `the pushes after`, computed by G:220 `def first_change_after` (`--no-renames`, `-z`).
  Its ignored prefix: G:226 `path.startswith(IGNORED_PREFIX)`. Then success (G:255 `passed`), CI_FIX (G:257 `CI_FIX={ci_fix}`), red (G:258 `REFUSED by ci-gate`).
  T:75 `test_unfinished_newest_run_waits` (the landed `…_allows`, changed BY DECISION, F9), T:226 `test_cli_cannot_decide_an_unknown_status`,
  T:242 `test_cli_cannot_decide_a_completed_run_with_no_conclusion`, T:394 `test_a_code_push_after_the_green_run_waits_for_its_run`,
  T:405 `test_a_transcripts_only_push_keeps_the_green_verdict`, T:414 `test_a_rename_out_of_code_into_transcripts_waits`,
  T:425 `test_a_red_run_followed_by_a_transcripts_only_push_refuses`,
  T:433 `test_a_kept_ci_fix_cannot_bless_the_red_run_again_after_its_fix_run_was_cancelled` (F12, see NOT-done).
- g · G:260 `if len(runs) >= PER_PAGE` → 2; otherwise the landed note (G:263 `no stage0-ci run in this branch's history`).
  T:445 `test_a_full_page_without_a_verdict_cannot_decide`: 50 → 2, 49 → the note.
- The overrides are read once and stripped: G:357 `ci_fix, wait_skip, offline = (os.environ`.
  CI_WAIT_SKIP changes only a 75: G:391 `if rc == WAIT and wait_skip`.
  T:253 `test_ci_wait_skip_changes_only_a_wait`, T:263 `test_blank_overrides_count_as_unset`, T:272 `test_a_padded_ci_fix_allows`.

**C3 — the API read.**
- G:145 `query = urllib.parse.urlencode`; G:135 `urllib.request.urlopen(url, timeout=TIMEOUT)` with G:61 `TIMEOUT = 20`.
- An HTTP error's text is urllib's status line (`HTTP Error 403: Forbidden`) plus, when present, G:139 `X-RateLimit-Remaining`.
- T:485 `test_the_runs_query_is_encoded` (`fix#1`, `fix&y`, `claude/x`, `feat-é`): the path, no fragment, the parsed query
  exactly {branch, `event=push`, `per_page=50`}, an ASCII URL, timeout 20.
- T:527 `test_an_unreadable_api_cannot_decide`: 403 with `X-RateLimit-Remaining: 0`, 404, 500, a `URLError`, a `socket.timeout` → 2;
  each 0 + WARNING under CI_GATE_OFFLINE. T:510 `test_the_api_verdict_decides` (the API path decides a red run).
- G:123 `def repo_slug`: T:541 `test_repo_slug_reads_each_github_form` (https, ssh, `.git`, a trailing slash, ssh://),
  T:548 `test_a_non_github_origin_cannot_decide` (→ 2, no request sent, no credential printed). The live GET: section 7.

**C4 — the waiter.**
- G:314 `def _wait(`; the deadline G:316 `deadline = _now() + args.wait`; the 30 s poll G:343 `_sleep(min(POLL_SECONDS, remaining))`.
- One line per state change: G:336 `if line != shown`. The deadline: G:340 `if remaining <= 0`. Three failed reads: G:326 `failures == READ_TRIES`.
- The overrides are ignored, with one line: G:378 `ignores {`. The failed jobs: G:303 `def _print_failed_jobs` over G:149 `def fetch_jobs`.
- `--origin-ref` defaults to `refs/remotes/origin/<branch>`: G:356 `ref = args.origin_ref or`.
- It never fetches or pushes: G:84 `def _git` is its only git seam, and the waiter runs only rev-parse, merge-base, cat-file,
  diff and remote get-url through it.
- T:631 `test_the_waiter_follows_a_push_to_its_verdict` ([no newer run registered] → [in_progress] → [success]: 3 polls, and 4 with a
  repeated state; one line per state), T:649 `test_the_waiter_lists_the_failed_jobs_of_a_red_verdict`,
  T:666 `test_the_waiter_keeps_the_red_verdict_when_the_jobs_cannot_be_read`, T:674 `test_the_waiter_stops_at_its_deadline` (bounded: the fake clock asserts after 200 sleeps),
  T:686 `test_the_waiter_retries_a_failed_read`, T:697 `test_the_waiter_gives_up_after_three_failed_reads_in_a_row`,
  T:707 `test_a_good_read_resets_the_waiters_failure_count`, T:714 `test_the_waiter_ignores_the_push_overrides`.

**C5 — push_clean.sh.**
- The full ref: PCL:68 `ORIGIN_REF="refs/remotes/origin/$BRANCH"`; the range PCL:76 `RANGE="$ORIGIN_REF..HEAD"`.
- The FETCH_HEAD check: PCL:69 `FETCHED=$(git rev-parse --verify --quiet FETCH_HEAD`, PCL:70 `!= "$FETCHED"`, PCL:74 `exit 2`.
  T:769 `test_push_clean_refuses_a_stale_origin_ref`, T:785 `test_push_clean_reads_the_full_remote_ref_not_a_local_origin_branch`.
- `--lanes-live`: PCL:35 `rc=0`, PCL:36 `|| rc=$?` running `bash "$WT/scripts/push_clean.sh"`.
  T:825 `test_push_clean_lanes_live_refusal_leaves_no_worktree`, T:836 `test_push_clean_lanes_live_runs_the_committed_gate`.
- The gate call: PCL:88 `--origin-ref "$ORIGIN_REF"`, PCL:89 `|| exit $?` (unchanged: every gate code passes through).
  T:743 `test_push_clean_waits_for_an_unfinished_verdict` (75, nothing pushed; CI_WAIT_SKIP pushes with its WARNING),
  T:759 `test_push_clean_passes_cannot_decide_through` (2, not 1), T:180 `test_push_clean_refuses_before_pushing_onto_a_red_head` (landed).
- The comment above the call: PCL:80 `CI GATE (AF-AP-126`, ending at PCL:87 `refuses it (64)`.

**C6 — the workflow.**
- W:10 `pull_request:`, W:13 `paths-ignore:`, W:14 `'transcripts/**'`; the gate's prefix G:66 `IGNORED_PREFIX = "transcripts/"`.
- TW:67 `test_pull_request_runs_skip_transcript_only_changes`, TW:73 `test_the_push_gate_ignores_exactly_what_both_triggers_ignore`
  (reads BOTH triggers' `paths-ignore` from the YAML and compares each with the gate's constant).

**C7 — the docstring.**
- The decision table G:13 `step  condition` (steps a-g), G:33 `Exit codes: 0 allow`, the waiter G:41 `--wait SECONDS (the waiter`.
- F18's two inexact lines are gone: G@c269263:11 `concurrency cancels it` and G@c269263:15 `no run in the history`.
- "64 usage" is true now (G:269 `self.exit(USAGE`).

## 4. Mutation audit (scratch copies only; driver `/tmp/ci166/mut/driver.py`, rows `/tmp/ci166/mut/mutants.py`)

Per row: a fresh tree `/tmp/ci166/mut/tree-<ID>` holding the six test inputs (G, PCL, T, W, TW, plus `scripts/setup.sh`,
`tests/conftest.py`, `pyproject.toml`); each edit's anchor must occur exactly once; the mutated file's sha256 must differ
from the worktree's; `py_compile` G, `bash -n` PCL, `yaml.safe_load` W; `--collect-only`; then both test files. A kill needs
pytest rc 1 AND a FAILED line; the first failure's `E` line was read for every row (all AssertionError / `assert`).

Driver self-test (its INVALID paths must fire):
````
S1 | anchor missing | INVALID anchor count 0 for 'this text is not in the file'
S2 | no-op edit | INVALID: the file did not change
S3 | syntax broken | scripts/ci_gate.py f1e2246f043ff702->848c999431b615d1 | py_compile=FAIL bash-n=ok yaml=ok | INVALID
````
Final run (the final test files; 09:13:50Z → 09:18:12Z; `rows 39 KILLED 39 SURVIVED 0 INVALID 0`; no leaked
`/tmp/push-clean-wt.*` afterwards: `0`):

| id | mutant | compiles (py/bash/yaml) | collected | pytest | killed-by (count: tests) |
|---|---|---|---|---|---|
| R1 | the tri-state back to returncode == 0 | ok/ok/ok | 129 | 2 failed, 127 passed | KILLED 2: `test_an_ancestry_read_that_exits_128_on_a_present_commit_refuses`, `test_cli_refuses_when_git_cannot_walk_the_history` |
| R2 | the shallow refusal removed (any rev-parse answer accepted) | ok/ok/ok | 129 | 1 failed, 128 passed | KILLED 1: `test_cli_refuses_a_shallow_clone_even_offline` |
| R3 | a present object with exit 128 read as not in history | ok/ok/ok | 129 | 1 failed, 128 passed | KILLED 1: `test_an_ancestry_read_that_exits_128_on_a_present_commit_refuses` |
| R4 | push_clean passes origin/$BRANCH to the gate again | ok/ok/ok | 129 | 1 failed, 128 passed | KILLED 1: `test_push_clean_reads_the_full_remote_ref_not_a_local_origin_branch` |
| R5 | the FETCH_HEAD check removed | ok/ok/ok | 129 | 1 failed, 128 passed | KILLED 1: `test_push_clean_refuses_a_stale_origin_ref` |
| R6 | `( … ); rc=$?` restored (the leak) | ok/ok/ok | 129 | 1 failed, 128 passed | KILLED 1: `test_push_clean_lanes_live_refusal_leaves_no_worktree` |
| R7 | the inner run uses $OLDPWD/scripts/push_clean.sh | ok/ok/ok | 129 | 1 failed, 128 passed | KILLED 1: `test_push_clean_lanes_live_runs_the_committed_gate` |
| R8 | an unfinished run allows | ok/ok/ok | 129 | 21 failed, 108 passed | KILLED 21: `test_a_good_read_resets_the_waiters_failure_count`, `test_blank_overrides_count_as_unset[   ]` +19 |
| R9 | an unknown or null status allows (status type check + unknown-status branch) | ok/ok/ok | 129 | 5 failed, 124 passed | KILLED 5: `test_cli_cannot_decide_an_unknown_status[7]`, `test_cli_cannot_decide_an_unknown_status[COMPLETED]` +3 |
| R10 | the record validation removed (per-record loop skipped) | ok/ok/ok | 129 | 18 failed, 111 passed | KILLED 18: `test_cli_refuses_a_payload_without_a_run_list[payload2-workflow_runs[0] is not an object]`, `test_cli_refuses_a_repeated_run_number` +16 |
| R11 | the query built without urlencode | ok/ok/ok | 129 | 3 failed, 126 passed | KILLED 3: `test_the_runs_query_is_encoded[feat-\xe9]`, `test_the_runs_query_is_encoded[fix#1]` +1 |
| R12 | the head_branch/event check removed | ok/ok/ok | 129 | 2 failed, 127 passed | KILLED 2: `test_cli_validates_every_record_before_deciding[event-pr]`, `test_cli_validates_every_record_before_deciding[head_branch-foreign]` |
| R13 | the page rule removed | ok/ok/ok | 129 | 1 failed, 128 passed | KILLED 1: `test_a_full_page_without_a_verdict_cannot_decide[50-2]` |
| R14 | the expected-run check removed | ok/ok/ok | 129 | 5 failed, 124 passed | KILLED 5: `test_a_code_push_after_the_green_run_waits_for_its_run`, `test_a_kept_ci_fix_cannot_bless_the_red_run_again_after_its_fix_run_was_cancelled` +3 |
| R15 | --no-renames removed | ok/ok/ok | 129 | 1 failed, 128 passed | KILLED 1: `test_a_rename_out_of_code_into_transcripts_waits` |
| R16 | CI_WAIT_SKIP rescues a red verdict | ok/ok/ok | 129 | 1 failed, 128 passed | KILLED 1: `test_ci_wait_skip_changes_only_a_wait` |
| R17 | a whitespace-only CI_WAIT_SKIP counts as set | ok/ok/ok | 129 | 2 failed, 127 passed | KILLED 2: `test_blank_overrides_count_as_unset[   ]`, `test_blank_overrides_count_as_unset[\t\n]` |
| R18 | CI_GATE_OFFLINE rescues a shallow clone (steps a/b) | ok/ok/ok | 129 | 2 failed, 127 passed | KILLED 2: `test_cli_refuses_a_shallow_clone_even_offline`, `test_cli_refuses_an_origin_ref_that_is_not_a_commit` |
| R19 | --runs-json accepted with a github.com origin | ok/ok/ok | 129 | 2 failed, 127 passed | KILLED 2: `test_runs_json_never_decides_against_a_github_origin[git@github.com:o/r.git]`, `test_runs_json_never_decides_against_a_github_origin[https://github.com/o/r]` |
| R20 | argparse errors exit 2 | ok/ok/ok | 129 | 5 failed, 124 passed | KILLED 5: `test_usage_errors_exit_64[argv0]`, `test_usage_errors_exit_64[argv1]` +3 |
| R21 | the waiter skips the expected-run check | ok/ok/ok | 129 | 2 failed, 127 passed | KILLED 2: `test_the_waiter_follows_a_push_to_its_verdict[a-repeated-state]`, `test_the_waiter_follows_a_push_to_its_verdict[three-polls]` |
| R22 | the waiter ignores its deadline | ok/ok/ok | 129 | 2 failed, 127 passed | KILLED 2: `test_the_waiter_ignores_the_push_overrides`, `test_the_waiter_stops_at_its_deadline` |
| R23 | CI_FIX honoured in wait mode | ok/ok/ok | 129 | 1 failed, 128 passed | KILLED 1: `test_the_waiter_ignores_the_push_overrides` |
| R24 | event=push dropped from the query | ok/ok/ok | 129 | 4 failed, 125 passed | KILLED 4: `test_the_runs_query_is_encoded[claude/x]`, `test_the_runs_query_is_encoded[feat-\xe9]` +2 |
| R25 | the pull_request paths-ignore removed | ok/ok/ok | 129 | 2 failed, 127 passed | KILLED 2: `test_pull_request_runs_skip_transcript_only_changes`, `test_the_push_gate_ignores_exactly_what_both_triggers_ignore` |
| X1 | push_clean `\|\| exit $?` -> `\|\| exit 1` (collapses 2 and 75 into 1) | ok/ok/ok | 129 | 2 failed, 127 passed | KILLED 2: `test_push_clean_passes_cannot_decide_through`, `test_push_clean_waits_for_an_unfinished_verdict` |
| X2 | per_page=50 -> per_page=1 | ok/ok/ok | 129 | 4 failed, 125 passed | KILLED 4: `test_the_runs_query_is_encoded[claude/x]`, `test_the_runs_query_is_encoded[feat-\xe9]` +2 |
| X3 | branch dropped from the query | ok/ok/ok | 129 | 4 failed, 125 passed | KILLED 4: `test_the_runs_query_is_encoded[claude/x]`, `test_the_runs_query_is_encoded[feat-\xe9]` +2 |
| X4 | urlopen timeout removed | ok/ok/ok | 129 | 4 failed, 125 passed | KILLED 4: `test_the_runs_query_is_encoded[claude/x]`, `test_the_runs_query_is_encoded[feat-\xe9]` +2 |
| X5 | CI_GATE_OFFLINE read without .strip() | ok/ok/ok | 129 | 2 failed, 127 passed | KILLED 2: `test_blank_overrides_count_as_unset[   ]`, `test_blank_overrides_count_as_unset[\t\n]` |
| X6 | the runs-json notice removed | ok/ok/ok | 129 | 1 failed, 128 passed | KILLED 1: `test_runs_json_with_a_local_origin_says_so_on_stderr` |
| X7 | exit 1 with an error line read as not in history (this lane's refinement, D1) | ok/ok/ok | 129 | 1 failed, 128 passed | KILLED 1: `test_cli_refuses_when_git_cannot_walk_the_history` |
| X8 | repo_slug / the github check accept any host (the landed regex) | ok/ok/ok | 129 | 1 failed, 128 passed | KILLED 1: `test_a_non_github_origin_cannot_decide[https://notgithub.com/o/r]` |
| X9 | the diff without -z (quoted non-ASCII paths) | ok/ok/ok | 129 | 1 failed, 128 passed | KILLED 1: `test_a_transcripts_only_push_keeps_the_green_verdict` |
| X10 | the waiter's failure count is not reset by a good read | ok/ok/ok | 129 | 1 failed, 128 passed | KILLED 1: `test_a_good_read_resets_the_waiters_failure_count` |
| X11 | the waiter honours CI_WAIT_SKIP | ok/ok/ok | 129 | 1 failed, 128 passed | KILLED 1: `test_the_waiter_ignores_the_push_overrides` |
| X12 | the waiter honours CI_GATE_OFFLINE | ok/ok/ok | 129 | 1 failed, 128 passed | KILLED 1: `test_the_waiter_ignores_the_push_overrides` |
| X13 | CI_FIX read without .strip() (the verifier's M6b) | ok/ok/ok | 129 | 1 failed, 128 passed | KILLED 1: `test_a_padded_ci_fix_allows` |
| X14 | a credential in a non-github origin URL printed | ok/ok/ok | 129 | 1 failed, 128 passed | KILLED 1: `test_a_non_github_origin_cannot_decide[https://user:s3cret@gitlab.example/o/r.git]` |

The kill reasons for the load-bearing rows (the first `E` lines of their outputs, earlier run on the same code):
````
R1  E  AssertionError: ci-gate: no stage0-ci run in this branch's history; nothing to read   (allowed where 2 was due)
R3  E  assert 0 == 2
R5  E  AssertionError: ci-gate: run #8 (fc9dd87) passed  … == boundary (2 commits) ==        (read the stale green, pushed)
R6  E  assert 2 == 1   where 2 = len(['worktree …/work', 'worktree /tmp/push-clean-wt.d8dabm'])   (the leak)
R7  E  AssertionError: == --lanes-live: … == boundary (1 commits) ==                           (the dirty gate allowed; pushed)
R22 E  AssertionError: the waiter ignored its deadline / assert 201 <= 200
````
AF-AP-138 — every distinct killing test (76) on the UNMUTATED worktree (G f1e2246f043ff702, PCL 4e835e99bdf2a86e, T 70c04c384332b61d):
````
$ mapfile -t K < /tmp/ci166/mut/killers.txt; /root/venv-agent-factory/bin/python -m pytest -q -p no:cacheprovider --basetemp=/tmp/ci166/bt-kill3 "${K[@]}" | tail -1
distinct killing tests: 76
76 passed in 10.49s
unmutated rc=0
````
Tally: R1-R25 = 25 rows, 25 KILLED. Extras X1-X14 = 14 rows, 14 KILLED (X1-X6 and X13 are the verifier's survivors X1-X6 and M6b;
X7, X9-X12, X14 guard this lane's own additions; X8 is the verifier's X8). 0 SURVIVED, 0 EQUIVALENT, 0 INVALID.
Notes: R9 is two edits (the status type check AND the unknown-status branch), since a null status is refused by validation (d)
before the decision (f). R21 is two edits (a waiter-only decision without the expected-run check).

## 5. Red-green

The final test files against the LANDED scripts and workflow (`git show HEAD:<file>`, G f19a6cbb99ea10b0, PCL ab2412d387131433,
W 718365358d1e855b), scratch tree `/tmp/ci166/redgreen`:
````
83 failed, 46 passed in 10.79s
landed rc=1
````
The 46 that pass on the landed code are the landed assertions (24 in T, 10 in TW) and 12 new guards for behaviour the landed
gate already had: the 404 / 500 / timeout texts, the five `repo_slug` forms, a non-github `gitlab.example` origin, CI_WAIT_SKIP never
rescuing a red, a red run behind a transcripts-only push, the API path deciding a red run. Every test this lane adds for new
behaviour is red there, e.g. the F12 test:
````
E       AssertionError: ci-gate: runs read from …/runs.json (a test input), not the Actions API
E         ci-gate: run #9 (dece669) concluded failure; CI_FIX=1009 declares this push fixes it
E       assert 0 == 75
landed rc=1   ·   worktree: 1 passed in 0.24s
````

## 6. Gates (the final bytes: G f1e2246f043ff702 398 lines · PCL 4e835e99bdf2a86e 128 · T 70c04c384332b61d 843 · W d868ae9004186d48 116 · TW 25b8c7ceeab3e921 129)

````
2026-09-23 09:18:33Z
$ /root/venv-agent-factory/bin/python -m pytest tests/test_ci_gate.py tests/test_stage0_ci_workflow.py -q -p no:cacheprovider --basetemp=/tmp/ci166/bt8
129 passed in 13.77s
rc=0
$ /root/venv-agent-factory/bin/python -m pytest tests/test_ci_gate.py tests/test_stage0_ci_workflow.py -q -p no:cacheprovider --basetemp=/tmp/ci166/bt9
129 passed in 12.91s
rc=0
$ bash scripts/pc_suite.sh set-id -- tests/test_ci_gate.py tests/test_stage0_ci_workflow.py
2 files set=f94590af83b6
rc=0
$ bash -n scripts/push_clean.sh
rc=0
$ /root/venv-agent-factory/bin/python -m pyflakes scripts/ci_gate.py tests/test_ci_gate.py tests/test_stage0_ci_workflow.py
rc=0
````
The set id is the premise's (the same two files); the count moved 37 → 129. An earlier pair of gate runs was NOT identical
(129 / 1 failed + 128 passed): section 8 gives the cause and the fix. `git status --porcelain`: the last block of this report.

## 7. The live read (C3) and one live decision (read-only GETs; the worktree's own module and CLI)

````
$ git remote get-url origin | sed -E 's#(://)[^/@]*@#\1<redacted>@#'
https://github.com/Pxls21/agent-factory
$ git rev-parse refs/remotes/origin/claude/soundbox-kit-migration-iz1jwf
2ebd486002152266c0d9333e112b1ca83d7a4c8a
2026-09-23 09:02:54Z
# ONE live GET through the new encoded query: g.fetch_runs(g.repo_slug("/tmp/wt-ci166"), branch)
slug: Pxls21/agent-factory
total_count: 976 | returned: 50
head_branch values: {'claude/soundbox-kit-migration-iz1jwf': 50}
event values: {'push': 50}
every head_branch == branch: True
validated records: 50
newest: 976 6e0dbdc in_progress None

2026-09-23 09:03:04Z
$ python3 scripts/ci_gate.py --branch claude/soundbox-kit-migration-iz1jwf        # CI_* unset
WAIT by ci-gate: run #976 (6e0dbdc) is in_progress — https://github.com/Pxls21/agent-factory/actions/runs/35839780738
Wait for the verdict: python3 scripts/ci_gate.py --branch claude/soundbox-kit-migration-iz1jwf --wait 1800
or push without waiting: CI_WAIT_SKIP=<reason>
rc=75
$ git log --oneline -3 refs/remotes/origin/claude/soundbox-kit-migration-iz1jwf
2ebd486 transcripts: scrubbed sandbox chat digests (2026-09-23)
6e0dbdc VERIFY-REPIN-a home NOT-READY (task #156): three small blockers in the lane-runtime pin's te
f1c2dff Wiki live-state 08:4xZ: VERIFY-J1-0-R23-STAMP died on route capacity; VERIFY-E3 and B9-R1 go
````
Reading: `branch=claude%2Fsoundbox-kit-migration-iz1jwf` (urlencoded) returns this branch's runs only, all `push`, all 50 valid.
The decision used the default `--origin-ref` (`refs/remotes/origin/<branch>`, shared refs, last fetched by the coordinator): origin's
head 2ebd486 is a transcripts-only sync commit, so its parent's run #976 is the verdict run — in progress, hence 75. This is the
F9 case live: on the same state the landed gate would allow (its code: G@c269263:38 `this push supersedes it`; not run). The ci_gate.py bytes were f1e2246f043ff702 then and now.

## 8. A finding during the gates: one flaky test, fixed (the gate was right, the test was not)

````
$ … --basetemp=/tmp/ci166/bt2   →   129 passed in 13.69s   rc=0
$ … --basetemp=/tmp/ci166/bt3   →   1 failed, 128 passed in 13.04s   rc=1
$ ls /tmp/ci166/bt3              →   test_cli_refuses_when_git_cann0        (pyproject keeps a FAILED test's tmp dir)
$ (in that repo) git merge-base --is-ancestor <red B> <head C>
error: Could not read e3bd39d2cf1047249c6577b154a8b23eaa3dbbdc
merge-base rc=0
$ (in that repo) ci_gate.py … → WAIT by ci-gate: the pushes after run #9 (f550b92), which concluded failure, change f.txt … rc=75
````
Mechanism (measured, section 2): git's walk follows commit dates. In bt3 the test's two commits fell in different seconds, git
proved B an ancestor before it tripped on the deleted parent and answered 0; the gate read "in history" (sound) and the
expected-run check gave 75. The test had assumed git always answers 1 here. Four more runs before the fix (bt4-bt7) passed:
1 failure in 7 runs. Fix, test only: T:362-363 now pin `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` (the same second → the walk reads
the missing parent first → exit 1 + error → 2). Evidence after the fix: the pinned test `passed=30 failed=0` in 30 runs; the gate
pair bt8/bt9 above; the mutation audit rerun (39/39) and the red count rerun (83 failed, 46 passed) on the final file.
Class for the coordinator's registry (not written here: boundary): a test over a corrupt or partial object store must pin the
commit dates, since git's walk order — and so its exit code — follows them.

## DISCREPANCIES (each a reading or a deviation; the contract text first, then what the code does)

- **D1 · C2 e "exit 1 → not in history".** The code reads exit 1 as "not in history" only with no `error:`/`fatal:` line on
  stderr; exit 1 WITH one is "cannot tell" → 2 (G:211 `if rc == 1 and error is None`). Evidence: git 2.43 answers exit 1 +
  `error: Could not read …` for a TRUE ancestor when the walk reaches a missing parent first (section 2, three date orders).
  My reading of "ANY other outcome → 2"; fail-closed. Guard: X7, killed by T:356 `test_cli_refuses_when_git_cannot_walk_the_history`. To undo: drop `and error is None`.
- **D2 · C4 names CI_FIX and CI_WAIT_SKIP as ignored in wait mode.** The code ignores CI_GATE_OFFLINE too (one line names all set ones).
  Reason: C4's "a failed read is retried; three in a row → 2" cannot hold if OFFLINE turns the first failed read into 0, and the
  waiter "reports the run's verdict, not a push decision". Guard: X12.
- **D3 · The contract names the CI_GATE_OFFLINE rescue for c, d and an unknown status.** The code also rescues a completed run with
  no conclusion (C2 f) and a full page with no verdict (C2 g): both are the API's data, and without a rescue the operator has no
  escape at all (CI_WAIT_SKIP changes only a 75). Pinned by T:242 `test_cli_cannot_decide_a_completed_run_with_no_conclusion` and
  T:445 `test_a_full_page_without_a_verdict_cannot_decide`.
- **D4 · C2 g "exactly as many records as the page size".** The code uses `>=` (G:260 `if len(runs) >= PER_PAGE`): equal on API data
  (the API never returns more than `per_page`); a larger test file also refuses.
- **D5 · Test names.** `test_unfinished_newest_run_allows` is now `test_unfinished_newest_run_waits` (T:75; "allows" would be false);
  its parameters grow from 3 to the contract's 5 statuses.
- **D6 · Two edits in G beyond the letter of C2 c, both in the non-github refusal.** (i) The github.com test needs the host to BE
  github.com: G:71 `GITHUB = re.compile` now starts with `(?:^|[/@])`; the landed regex read `https://notgithub.com/o/r` as github.com's
  o/r (the gate would read an unrelated repository's verdict). (ii) The refusal drops a URL's userinfo (G:127 `shown = re.sub`);
  the landed text printed the whole origin URL, credentials included. Guards: X8, X14.
- **D7 · C4 "a read failure during the wait is retried".** The code retries every API-data failure (a failed read, an invalid record,
  an unknown status, a completed run with no conclusion, a full page): all raise the same G:76 `class DataError`. Such a state ends
  in 2 after three polls (about 60 s) instead of at once.
- **D8 · C4 "returns the final decision (75 when the deadline passes)".** When the last poll's read failed, the waiter returns 2 (its
  last decision could not be made), not 75: G:326 `failures == READ_TRIES or _now() >= deadline`. Pinned by T:714 `test_the_waiter_ignores_the_push_overrides` (`--wait 0` on an
  unreadable file → 2).
- **Readings, not deviations:** git runs under `LC_ALL=C` (G:87 `LC_ALL`); the waiter's state lines are the first line of each 75
  text, and the waiter command + escape print once, with the final 75; `--wait` suggests 1800 s (the ledger quotes ~22 min runs).

## Self-attack — the three likeliest ways this change is wrong

1. **The expected-run check waits for a run GitHub never creates.** Cases: a head commit message with `[skip ci]` (and variants), a
   diff of more than 3,000 files, a disabled workflow, an Actions outage, or the newest run cancelled by hand. Checked: `git log -i
   --grep '[skip ci|ci skip|no ci|skip actions|actions skip]'` over the branch → `0` of `1175` commits; every 75 prints the
   CI_WAIT_SKIP escape (T:208 `test_cli_waits_while_the_verdict_run_is_unfinished`); the hand-cancelled case waits rather than
   re-blessing a red run (T:433 `test_a_kept_ci_fix_cannot_bless_the_red_run_again_after_its_fix_run_was_cancelled`). Not ruled out: the text
   "no newer run is registered yet" is inexact when the newer run is registered but cancelled (NOT-done).
2. **The tri-state misreads a healthy repository.** Checked: a healthy walk prints nothing on stderr (0 bytes for exit 0 and for
   exit 1, section 2); `LC_ALL=C` fixes the prefixes; exit 0 is sound; the live decision on the real clone (1175 commits) found
   run #976 in history and answered 75. Residual, not measured: a git that prints an unrelated `error:` line during a clean walk
   would give a false 2 (fail-closed, with git's line in the text).
3. **push_clean's FETCH_HEAD check refuses a legitimate push.** Checked: with the default refspec the tracking ref equals FETCH_HEAD
   after `git fetch origin <b>` (probe 3); every push_clean test runs through the check, the `--lanes-live` ones inside the detached
   worktree (FETCH_HEAD is per-worktree; the inner run fetches and compares in the same worktree). Residual: the PC clone's refspec
   was not measured (no bridge use); a narrowed one now refuses with exit 2 and the fix text, by design.
4. (Venue) The new tests run in CI under a newer git. The missing-parent test expects 2 on both paths: exit 1 + error (git 2.43,
   measured) and exit 128 + a present object (git 2.45+, INFERRED from git's walk code, not measured here).

## NOT-done

- Issue #34 findings NOT closed, by id:
  - **F10**, second half: the gate still reads `event=push` runs only; whether it should read pull_request runs is undecided.
    The `paths-ignore` half is closed (C6).
  - **F12**: closed only as a side effect, for a fix push that changed code
    (T:433 `test_a_kept_ci_fix_cannot_bless_the_red_run_again_after_its_fix_run_was_cancelled`: 75 instead of a re-bless); the 75 text there
    says "no newer run is registered yet" although the fix's run is registered (cancelled). Still open: a CI_FIX push that changed
    only `transcripts/` starts no run, and a kept CI_FIX re-blesses the red run on the next push.
  - **F13**: docs outside the boundary. CLAUDE.md's push bullet (`CI GATE (AF-AP-126`) does not mention exit 75, CI_WAIT_SKIP or
    `--wait`; nor do the AGENTS.md / .hermes.md mirrors or `wiki/topics/infrastructure-and-tooling.md`.
  - **F14** (does a cancelled run mail?), **F15** (a mixed push runs CI: DOC only — the expected-run check relies on it),
    **F21** (unauthenticated reads off the proxy), **F23** (a DNS stall or a slow-drip body is not bounded by the 20 s timeout).
  - **F16**: exit codes are still shared: push_clean's new FETCH_HEAD refusal is a third 2 (with TREE MISMATCH and the gate's).
  - **F18**, runtime half: a lone cancelled run still prints the landed note "no stage0-ci run in this branch's history" (C2 g keeps it).
  - **F22**, re-run half: `run_attempt` is still not read (each record's own status decides).
  - Closed by this change: F1, F2, F3, F4, F5, F6, F7, F8, F9 (by decision), F10 (paths-ignore), F11, F17, F19, F20, F22 (types, repeats).
- No commit, no push, no fetch (standing do-nots); no PC or bridge use.
- No `/bug-echo`, registry row or incident entry for D1's class or section 8's class (boundary): the coordinator's.
- Ctrl-C during `--wait` ends in Python's KeyboardInterrupt traceback (exit 130), not a named verdict.
- The waiter was not run live (one live decision only; run #976 was still in progress).
- The full suite (`pytest tests/`) was not run: only the two files (129 tests).
- Scratch state left for inspection: `/tmp/ci166/` (probes, `mut/` trees and outputs, `redgreen/`, the bt dirs).

## Lint (pasted; two fix rounds of the three allowed)

````
$ python3 scripts/report_lint.py --min-refs 12 --map G=scripts/ci_gate.py --map PCL=scripts/push_clean.sh --map T=tests/test_ci_gate.py --map W=.github/workflows/stage0-ci.yml --map TW=tests/test_stage0_ci_workflow.py tasks/briefs/ci/CI-GATE-R1-report.md --root /tmp/wt-ci166
round 1: report_lint: 153 refs — OK 142, NEAR 1, MISS 9, UNCHECKABLE 1, UNRESOLVED 0 (worktree)   (test refs without the test's name; one 3-character backtick span)
final:   report_lint: 154 refs — OK 154, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
rc=0
````

## Final state of the worktree (09:24:19Z)

````
$ git -C /tmp/wt-ci166 status --porcelain
 M .github/workflows/stage0-ci.yml
 M scripts/ci_gate.py
 M scripts/push_clean.sh
 M tests/test_ci_gate.py
 M tests/test_stage0_ci_workflow.py
?? tasks/briefs/ci/CI-GATE-R1-report.md
$ git -C /tmp/wt-ci166 rev-parse HEAD
c269263fbc9935d0f668628704ca933a85149380
$ ls -d /tmp/push-clean-wt.* 2>/dev/null | wc -l
0
````
Exactly the six boundary paths: five modified, this report untracked. HEAD unmoved (c269263); nothing committed, fetched or pushed.
