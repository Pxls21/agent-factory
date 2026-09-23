# VERIFY-CI-GATE-R1 — report (task #171; issue #34)

LANE: verify-ci-gate-r1 (sandbox, agent `adversarial-verifier`, Opus 5.5). PIN: origin 5689d9f (tree 61045eb = local f77563f).
STATUS: COMPLETE 2026-09-23 — GATE RECOMMENDATIONS: (a) `scripts/ci_gate.py` decide/validate MERGE-READY-WITH-FOLLOWUPS ·
(b) the waiter MERGE-READY-WITH-FOLLOWUPS · (c) `scripts/push_clean.sh` MERGE-READY-WITH-FOLLOWUPS · (d) the workflow and its pin
MERGE-READY. No finding meets the whole blocking predicate in the measured production state; the PC clone was NOT measured
(VR-1, VR-3, VR-4 escalate if a push venue carries replace refs/grafts, a non-canonical github URL, or a tag named like the
branch). All 90 hostile CLI rows of item 2 end in the contract's code; of 21 expected-run shapes (item 3), 17 match GitHub's
documented rule and 4 miss a run (3 config-dependent, 1 benign); six damaged or rewritten history states make the gate allow
(item 4), and two of them (replace refs, grafts) get through the real push_clean; 44 NEW mutants: 30 KILLED, 14 SURVIVED
(9 test gaps).

## 1. PREMISE — re-measured 2026-09-23 09:40Z

```
$ date -u
Wed Sep 23 09:40:50 UTC 2026
$ git rev-parse --short HEAD   (origin head = local head)
b511e4a
$ git log --oneline 5689d9f..refs/remotes/origin/claude/soundbox-kit-migration-iz1jwf
b511e4a Wiki live-state 09:3xZ: CI-GATE-R1 landed ...
649663a Briefs VERIFY-AF-AP-127 (task #155) and VERIFY-CI-GATE-R1 (task #171) ...
$ git diff --stat 5689d9f origin/<branch>
 tasks/briefs/ci/VERIFY-CI-GATE-R1-brief.md        | 149 ++++
 tasks/briefs/continuity/VERIFY-AF-AP-127-brief.md | 147 ++++
 wiki/topics/live-state.md                         |   2 +
$ f77563f tree / 5689d9f tree
61045ebf10711fabeb4107fbc911e7afa109adcc / 61045ebf10711fabeb4107fbc911e7afa109adcc
$ for f in <the five>; do blob at 5689d9f, sha256 prefix, lines; done
7a0bb510406d d868ae9004186d48 116 .github/workflows/stage0-ci.yml
12b792fa794a f1e2246f043ff702 398 scripts/ci_gate.py
dae355ad2e17 4e835e99bdf2a86e 128 scripts/push_clean.sh
1ca772706916 70c04c384332b61d 843 tests/test_ci_gate.py
7a2f4a8b422d 25b8c7ceeab3e921 129 tests/test_stage0_ci_workflow.py
$ git diff --quiet 5689d9f -- <the five> && echo ...
tree == 5689d9f on the five
$ grep -c "^def test" (at 5689d9f)
tests/test_ci_gate.py:55
tests/test_stage0_ci_workflow.py:12
$ git config --get-all remote.origin.fetch; git rev-parse --is-shallow-repository; git --version
+refs/heads/*:refs/remotes/origin/*
false
git version 2.43.0
```
Verdict: PREMISE HOLDS. Every blob matches the brief's f77563f table byte for byte; the defs table (`grep -n "^def \|^class "`)
matches line for line; the two commits after the pin change none of the five files.

## 2. Fresh gates (the builder's claim, re-run; not evidence by itself)

```
$ for i in 1 2; do /root/venv-agent-factory/bin/python -m pytest tests/test_ci_gate.py tests/test_stage0_ci_workflow.py -q -p no:cacheprovider --basetemp=/tmp/vcg1/bt$i | tail -1; done
129 passed in 13.74s
rc=0
129 passed in 15.64s
rc=0
$ bash scripts/pc_suite.sh set-id -- tests/test_ci_gate.py tests/test_stage0_ci_workflow.py
2 files set=f94590af83b6
$ ... --collect-only | tail -1
129 tests collected in 0.05s
$ bash -n scripts/push_clean.sh ; pyflakes scripts/ci_gate.py tests/test_ci_gate.py tests/test_stage0_ci_workflow.py
bash-n rc=0
pyflakes rc=0
```
Code intel: `scripts/lane_context.sh -q 'how does the push gate decide from the runs and the history' -s _decide -s valid_runs
-s in_history -s first_change_after -s _wait -o /tmp/vcg1/pack.md scripts/ci_gate.py scripts/push_clean.sh` → rc 0, 166 lines.
graft skeleton matches the premise's defs table; GitNexus impact upstream LOW for all five symbols (one direct caller each);
AP screen: AP-1 ×1 (`scripts/ci_gate.py:357` `os.environ.get`, the one env read of the three overrides, C2 g "read once"). crg `tests_for` is
blind here: it returns 0 for `valid_runs`/`in_history`/`first_change_after` and unrelated tests for `_decide`/`_wait` (the
suite drives them through `subprocess` and `ci_gate.main`) — INFO, instrument limit, not a coverage fact.

## 3. Item 2 — C1-C2 with new shapes, through the REAL CLI

Venue: throwaway repo `/tmp/vcg1/p2/work` (branch feat) + bare origin `/tmp/vcg1/p2/origin.git`; the gate is the repo's
`scripts/ci_gate.py` (read-only), default `--origin-ref` (`refs/remotes/origin/feat`), `--runs-json`, non-github origin.
Probes: `/tmp/vcg1/p2/probe2.py` (records) and `/tmp/vcg1/p2/probe2h.py` (histories). Each row: the contract's code (`want`),
the gate's (`rc`); for every validation row the same input again under `CI_GATE_OFFLINE=probe` (contract: 0 + WARNING).

Records (68 rows; condensed — identical outcomes joined; full rows in the probe output):
```
rows: 68  ok: 68  BAD: 0  TRACEBACK: 0  OFFLINE-checked: 54  OFFLINE-BAD: 0
ok  want=2 rc=2 | older record lacks <each of the 7 keys> (verdict red, valid) | ... (workflow_runs[1] (id 1008) has no run_number) ... | OFFLINE rc=0
ok  want=2 rc=2 | id float 1009.0 / id string '1009' / id -Infinity | ... id is 1009.0, not an integer ... | OFFLINE rc=0
ok  want=0 rc=0 | id huge int 10**30 / id negative -5 | ci-gate: run #9 (bb42cbf) passed
ok  want=0 rc=0 | run_number 0 / -3 / 2**70 | ci-gate: run #0 (bb42cbf) passed  |  run #-3  |  run #1180591620717411303424
ok  want=2 rc=2 | run_number 9.0 / NaN / Infinity | ... run_number is nan, not an integer ...
ok  want=2 rc=2 | head_sha + trailing newline / 40 hex + 1 / + space / leading space / 39 hex / NUL / mixed case / null / int / list | ... not 40 lowercase hex ... | OFFLINE rc=0
ok  want=2 rc=2 | status list / dict / number / bool | ... status is ['completed'], not a string ... | OFFLINE rc=0
ok  want=2 rc=2 | status 'Completed' / 'in_progress ' / 'IN_PROGRESS' | ... has the status 'Completed': neither completed nor unfinished ... | OFFLINE rc=0
ok  want=2 rc=2 | conclusion list / dict / bool / 1.5 | ... not a string or null ... | OFFLINE rc=0
ok  want=1 rc=1 | conclusion '' / 'SUCCESS' / ' success' | REFUSED by ci-gate: run #9 (bb42cbf) concluded SUCCESS — ...
ok  want=2 rc=2 | head_branch 'Feat' / 'feat ' / 'feat\n' / 'refs/heads/feat' / null | ... head_branch is 'Feat', not 'feat' ... | OFFLINE rc=0
ok  want=2 rc=2 | event 'Push' / 'push ' / null / 'workflow_dispatch' | ... event is 'Push', not 'push' ... | OFFLINE rc=0
ok  want=2 rc=2 | payload null / a string / a number / a list of runs / {} / total_count only / workflow_runs null|string|dict | (the payload carries no workflow_runs list) | OFFLINE rc=0
ok  want=2 rc=2 | workflow_runs [null] / empty file / truncated JSON / trailing garbage / UTF-8 BOM | (workflow_runs[0] is not an object) / (JSONDecodeError: ...) | OFFLINE rc=0
ok  want=1 rc=1 | total_count absent, workflow_runs valid (red) | REFUSED by ci-gate: run #9 (bb42cbf) concluded failure — ...
ok  want=0 rc=0 | total_count wrong (99), workflow_runs valid (green) | ci-gate: run #9 (bb42cbf) passed
ok  want=1 rc=1 | duplicate id across two run_numbers (verdict red) | REFUSED ...;  same with CI_FIX=1009 -> rc=0
```
Histories on real git (22 rows, `/tmp/vcg1/p2/outh.txt`):
```
rows: 22 BAD: 0
ok  want=1  rc=1  | H1 red run on the merge's 2nd parent; first parent adds transcripts/t.md | REFUSED by ci-gate: run #9 (66d3483) concluded failure — u9
ok  want=75 rc=75 | H1 red run on the merge's 2nd parent; first parent adds m.txt | WAIT by ci-gate: the pushes after run #9 (66d3483), which concluded failure, change m.txt and no newer run is registered yet
ok  want=0  rc=0  | H2 force-moved origin (red 2c0f6d4 left history, is-ancestor rc=1); new head adds transcripts/t.md; GitHub's push diff red..head = ['r.txt', 'transcripts/t.md'] | ci-gate: run #9 (29da89f) passed
ok  want=75 rc=75 | H2 force-moved origin (red efbf571 left history, is-ancestor rc=1); new head adds g.txt; GitHub's push diff red..head = ['g.txt', 'r.txt'] | WAIT by ci-gate: the pushes after run #9 (38a74cb), which concluded success, change g.txt ...
ok  want=75 rc=75 | H3 red #10 on the head C, green #11 on its parent B; C adds c.txt | WAIT by ci-gate: the pushes after run #11 (352a163), which concluded success, change c.txt and no newer run is registered yet
ok  want=0  rc=0  | H3 red #10 on the head C, green #11 on its parent B; C adds transcripts/t.md | ci-gate: run #11 (352a163) passed
ok  want=75 rc=75 | H4 the head's run in_progress, an older green run exists | WAIT by ci-gate: run #10 (c1a2173) is in_progress — u10
ok  want=75 rc=75 | H5a cancelled on the head, success on its parent (head changes code) | WAIT by ci-gate: the pushes after run #9 (8d59e3a), which concluded success, change f.txt and no newer run is registered yet
ok  want=0  rc=0  | H5b cancelled then success on the SAME head sha | ci-gate: run #9 (c1a2173) passed
ok  want=0  rc=0  | H5c a lone cancelled run on the head | ci-gate: no stage0-ci run in this branch's history; nothing to read
ok  want=1  rc=1  | H6/H7 the head's run concluded skipped | neutral | timed_out | action_required | stale | startup_failure   (each: REFUSED ... concluded <x>)
ok  want=0  rc=0  | the same six with CI_FIX=1010 naming the run  (each: ... CI_FIX=1010 declares this push fixes it)
```
Reading (item 2): every hostile record and every history shape ends in the contract's code with its text; no traceback in 90
CLI rows. Observations that do not change a code (inventory rows V-1..V-4): a negative, zero or huge `id`/`run_number` is
accepted (the contract asks only int-not-bool); a duplicated `id` is accepted; `total_count` is never read; H2 (force-moved
origin, transcripts-only new head) reads the older green as the verdict (0) although GitHub's push diff for that force push
(`before..after` = `red..head`, DOC) contains `r.txt`, so a run WOULD start — a missed run, benign in substance (the head's
code equals the green run's code; `scripts/push_clean.sh` never force-pushes); H3 and H5a print "no newer run is registered
yet" while a newer-by-sha run IS registered (red, or cancelled) — the contract's own text (C2 f), inexact (open under F12/F18).

## 4. Item 3 — the expected-run check (C2 f) on real git vs GitHub's documented `paths-ignore`

GitHub's rule, read from primary source (the docs repository, `raw.githubusercontent.com/github/docs/main`:
`data/reusables/actions/workflows/triggering-a-workflow-paths3.md`, `…-paths5.md`, and the "Filter pattern cheat sheet" of
`content/actions/reference/workflows-and-actions/workflow-syntax.md`), verbatim: "When all the path names match patterns in
`paths-ignore`, the workflow will not run." · "If there are no files changed, the workflow will not run." · "Pushes to existing
branches: A two-dot diff compares the head and base SHAs directly with each other." · "`**`: Matches zero or more of any
character." · "Path patterns must match the whole path, and start from the repository's root." · "If a push contains more than
1,000 commits, the workflow will always run. If generating the diff times out, the workflow will always run." So
`transcripts/**` matches exactly the paths that start with `transcripts/` (dotfiles included; the file `transcripts` and
`transcripts2/x` excluded) — the same predicate as `scripts/ci_gate.py:226` `path.startswith(IGNORED_PREFIX)`. Case: the docs
are silent; `[CB]at` "matches `Cat` or `Bat`" implies case-sensitive matching (INFERRED).

Probe `/tmp/vcg1/p3/probe3.py`: per shape, a green run on the pushed base, ONE push changing only the shape's paths, no newer
run registered; `want` = 75 when GitHub starts a run (the gate must wait), 0 when it does not (the green verdict stands).
```
ok          transcripts-only                   GitHub run=no  (DOC) want=0  gate=0  | changed=[b'transcripts/sandbox/d.md'] | ci-gate: run #9 (b9523e6) passed
ok          .github-only                       GitHub run=yes (DOC) want=75 gate=75 | changed=[b'.github/workflows/other.yml'] | WAIT by ci-gate: the pushes after run #9 ...
ok          root FILE named transcripts        GitHub run=yes (DOC) want=75 gate=75 | changed=[b'transcripts', b'transcripts/old.md'] | WAIT ... change transcripts and no newer run i
ok          transcripts2/x                     GitHub run=yes (DOC) want=75 gate=75 | changed=[b'transcripts2/x'] | WAIT ...
ok          Transcripts/x (case)               GitHub run=yes (INFERRED) want=75 gate=75 | changed=[b'Transcripts/x'] | WAIT ...
ok          dotfile transcripts/.meta          GitHub run=no  (DOC) want=0  gate=0  | changed=[b'transcripts/.meta'] | ci-gate: run #9 (d076dbd) passed
ok          mode-only code.py +x               GitHub run=yes (INFERRED) want=75 gate=75 | changed=[b'code.py'] | WAIT ...
ok          mode-only transcripts/old.md +x    GitHub run=no  (DOC) want=0  gate=0  | changed=[b'transcripts/old.md'] | ci-gate: run #9 (d076dbd) passed
ok          deleted code.py                    GitHub run=yes (DOC) want=75 gate=75 | changed=[b'code.py'] | WAIT ...
ok          deleted transcripts/old.md         GitHub run=no  (DOC) want=0  gate=0  | changed=[b'transcripts/old.md'] | ci-gate: run #9 (d076dbd) passed
ok          newline path transcripts/a\nb      GitHub run=no  (DOC) want=0  gate=0  | changed=[b'transcripts/a\nb.md'] | ci-gate: run #9 (c9b36a9) passed
ok          newline path code\nx.py            GitHub run=yes (DOC) want=75 gate=75 | changed=[b'code\nx.py'] | WAIT ...
ok          non-UTF-8 byte transcripts/\xff    GitHub run=no  (DOC) want=0  gate=0  | changed=[b'transcripts/\xff.md'] | ci-gate: run #9 (c9b36a9) passed
ok          non-UTF-8 byte \xff.py             GitHub run=yes (DOC) want=75 gate=75 | changed=[b'\xff.py'] | WAIT ... change \udcff.py and no newer run is regist
ok          empty commit (no file changed)     GitHub run=no  (DOC) want=0  gate=0  | changed=[] | ci-gate: run #9 (c9b36a9) passed
MISSED-RUN  code change then revert (net none) GitHub run=yes (DOC: each push's own diff has code.py) want=75 gate=0  | changed=[] | ci-gate: run #9 (c9b36a9) passed
ok          submodule gitlink added at sub     GitHub run=yes (INFERRED) want=75 gate=75 | changed=[b'sub'] | WAIT ...
ok          submodule under transcripts/sub    GitHub run=no  (DOC) want=0  gate=0  | changed=[b'transcripts/sub'] | ci-gate: run #9 (a2ed7d7) passed
MISSED-RUN  gitlink bump, .gitmodules ignore=all GitHub run=yes (INFERRED) want=75 gate=0  | changed=[] | ci-gate: run #9 (de8fed4) passed
MISSED-RUN  gitlink bump, local diff.ignoreSubmodules=all GitHub run=yes (INFERRED) want=75 gate=0  | changed=[] | ci-gate: run #9 (0f7b97b) passed
MISSED-RUN  diff.relative=true, --root scripts/ GitHub run=yes (DOC) want=75 gate=0  | changed=[b'code.py'] | ci-gate: run #9 (7683f48) passed
```
Discriminator for the three config-dependent misses (same repos, git 2.43):
```
== gitlink bump, .gitmodules ignore=all (green de8fed4)
  contract cmd:            [rc=0]
  + --ignore-submodules=none: sub
== gitlink bump, local diff.ignoreSubmodules=all (green 0f7b97b)
  contract cmd:            [rc=0]
  + --ignore-submodules=none: sub
== diff.relative=true, --root scripts/
  contract cmd from scripts/:
  + --no-relative:             code.py
```
Reading (item 3): all 17 shapes the brief names end where GitHub's documented rule says (a phantom run: none). Four misses,
each a wrong 0 inside the registration window (inventory rows E-1..E-3): (E-1) a committed `.gitmodules` `ignore = all` or a
local `diff.ignoreSubmodules=all` hides a gitlink bump from `git diff` itself — the contract's exact command (C2 f) returns
nothing, so the code matches the contract and the contract's command is blind; this repo has 0 gitlinks (`git ls-files -s`,
mode 160000: `0`) and neither config is set here (`git config --get diff.ignoreSubmodules`: empty), so no effect today. (E-2)
`diff.relative=true` plus a gate run from a subdirectory (`--root` a subdirectory, or push_clean started from one) hides every
change outside it; unset here. (E-3) a change pushed and reverted in the next push nets to nothing: two runs start, the gate
reads the older green; benign in substance (the head's code IS the green run's code, and the second push's run cancels the
first by `cancel-in-progress`). Fix for E-1/E-2: `git diff --ignore-submodules=none --no-relative …` in
`scripts/ci_gate.py:223` (the `--no-renames` call; measured above) — a contract amendment, since C2 f names the command.

## 5. Item 4 — the tri-state history filter (C2 e), D1, and the attacks

Probes `/tmp/vcg1/p4/probe4.py` and `/tmp/vcg1/p4/probe4b.py` (git 2.43.0). Shape of every attack: root A → R (code; the red
run #9 is on R) → T (transcripts only; origin's head). The right answer is 1 (R is in origin's history and red), or 2 when
the clone cannot tell. A 0 is the wrong allow.

D1 reproduced (the builder's measurement: B's parent object deleted, B a true ancestor of C, three date orders):
```
  same second   merge-base rc=1 err=[error: Could not read 00b919567d8dd1238b2eb2b1e83f9fe4facea578] · cat-file -e rc=0 err=[]
refused     rc=2 | D1 same second: gate on the red run B | REFUSED by ci-gate: git cannot tell whether commit c558780… is in the history of a8d2da5…: merge-base --is-ancestor exited 1 (error: Could not read 00b9195…
  B 1 s earlier merge-base rc=0 err=[error: Could not read 00b919567d8dd1238b2eb2b1e83f9fe4facea578] · cat-file -e rc=0 err=[]
refused     rc=1 | D1 B 1 s earlier: gate on the red run B | REFUSED by ci-gate: run #9 (c558780) concluded failure — u
  B 1 s later   merge-base rc=1 err=[error: Could not read 00b919567d8dd1238b2eb2b1e83f9fe4facea578] · cat-file -e rc=0 err=[]
refused     rc=2 | D1 B 1 s later: gate on the red run B | REFUSED by ci-gate: git cannot tell whether commit 5f43f3b… …
```
The builder's three rows reproduce exactly (exit 1 + `error:` twice, exit 0 + `error:` once); the gate never allows.

The attacks (`WRONG-ALLOW` = the gate exits 0 while the red run is in origin's history):
```
refused     rc=1 | control (undamaged) | REFUSED by ci-gate: run #9 (bc1ca4a) concluded failure — u
refused     rc=2 | R's tree object deleted | ... git cannot list the paths changed after bc1ca4a…: diff exited 128 (fatal: unable to read tree b5b7a54…)
refused     rc=2 | T's (the head's) tree object deleted | ... diff exited 128 (fatal: unable to read tree 04a33dc…)
refused     rc=1 | R's blob f.txt deleted | REFUSED by ci-gate: run #9 (bc1ca4a) concluded failure — u
    merge-base rc=128 err=[error: inflate: data stream error (incorrect header check) / error: unable to unpack bc1ca4a] · cat-file -e rc=128 err=[same]
WRONG-ALLOW rc=0 | R's loose object overwritten with garbage | ci-gate: no stage0-ci run in this branch's history; nothing to read
WRONG-ALLOW rc=0 | R's packed object: 16 bytes flipped inside the pack | ci-gate: no stage0-ci run in this branch's history; nothing to read
refused     rc=1 | alternates intact (control) | REFUSED by ci-gate: run #9 (4db232c) concluded failure — u
    is-shallow: 'false' stderr: ''
WRONG-ALLOW rc=0 | alternates -> nowhere (R absent, history incomplete) | ci-gate: no stage0-ci run in this branch's history; nothing to read
    merge-base rc=1 err=[] · cat-file -e rc=0 err=[]
WRONG-ALLOW rc=0 | git replace <head> <parentless copy> | ci-gate: no stage0-ci run in this branch's history; nothing to read
refused     rc=1 | same, GIT_NO_REPLACE_OBJECTS=1 in the caller's env | REFUSED by ci-gate: run #9 (4db232c) concluded failure — u
    merge-base rc=1 err=[hint: Support for <GIT_DIR>/info/grafts is deprecated …] · cat-file -e rc=0
WRONG-ALLOW rc=0 | .git/info/grafts makes the head a root | ci-gate: no stage0-ci run in this branch's history; nothing to read
WRONG-ALLOW rc=0 | gate: R's object deleted (non-shallow clone) | ci-gate: no stage0-ci run in this branch's history; nothing to read
WRONG-ALLOW rc=0 | GIT_DIR=<different repo>/.git | ci-gate: no stage0-ci run in this branch's history; nothing to read
refused     rc=1 | GIT_DIR=.git (relative: resolves under --root) | REFUSED ...
refused     rc=1 | GIT_WORK_TREE=/tmp (no GIT_DIR) | REFUSED ...
refused     rc=2 | GIT_OBJECT_DIRECTORY=<empty dir> | REFUSED by ci-gate: the origin ref 'refs/remotes/origin/feat' does not resolve to a commit; fetch it first
refused     rc=2 | shallow clone + GIT_SHALLOW_FILE=/dev/null | REFUSED by ci-gate: this clone is shallow, ...
```
The canonical consumer — the REAL `scripts/push_clean.sh` (by absolute path, so `$(dirname "$0")/ci_gate.py` is the real gate)
in each damaged clone, a local commit to push, `CI_GATE_RUNS_JSON` = the red run on R:
```
  pcl-control    push_clean rc=1   not pushed | REFUSED by ci-gate: run #9 (2358d1e) concluded failure — u / ...
  pcl-absent     push_clean rc=1   not pushed | ci-gate: no stage0-ci run in this branch's history; nothing to read / == boundary (1 commits) == / ... / == pushing aa5bb5b… == / error: Could not read 1d214b7… /  ! [rejec…
  pcl-corrupt    push_clean rc=128 not pushed | error: header for 1d214b7… too long, exceeds 32 bytes / fatal: loose object 1d214b7… is corrupt     (the fetch, before the gate)
  pcl-replace    push_clean rc=0   PUSHED     | ci-gate: no stage0-ci run in this branch's history; nothing to read / == boundary (1 commits) == / ... / == pushing aa5bb5b… ==
  pcl-graft      push_clean rc=0   PUSHED     | ci-gate: no stage0-ci run in this branch's history; nothing to read / ... / == pushing aa5bb5b… == / hint: Support for <GIT_DIR>/info/grafts is deprecated
  pcl-alternates push_clean rc=1   not pushed | error: unable to normalize alternate object path: /tmp/vcg1/p4/nowhere/objects / REFUSED: dirty working tree — …
```
(`pcl-absent`: the gate allowed; `git push` then failed on its own — `! [rejected] HEAD -> feat (non-fast-forward)`: git could
not walk the ancestry to prove a fast-forward. `pcl-alternates`: `git diff --quiet` errors, so push_clean's dirty-tree check
refuses. Both stops are accidents of other git calls, not the gate.)

Discriminators, measured (read-only git on the same clones):
```
  R deleted (absent)    cat-file -e <sha>: rc=1 err='' · batch-check: 'f6cc6c59853f missing' rc=0 · rev-list --quiet <origin>: rc=128 err='error: Could not read 2358d1e…'
  R corrupt (loose)     cat-file -e <sha>: rc=0 err='' · batch-check: '… missing' rc=0 · rev-list --quiet <origin>: rc=128 err='error: inflate: data stream error (incorrect header check)'
  healthy, R present    cat-file -e <sha>: rc=0 err='' · batch-check: '… commit 165' rc=0 · rev-list --quiet <origin>: rc=0 err=''
  healthy, foreign sha  cat-file -e <sha>: rc=1 err='' · batch-check: '… missing' rc=0 · rev-list --quiet <origin>: rc=0 err=''
  alternates->nowhere   cat-file -e <sha>: rc=1 err='error: unable to normalize alternate object path: …' · rev-list --quiet <origin>: rc=128
  replace, NO_REPLACE   merge-base rc 0          grafts, GIT_GRAFT_FILE=/dev/null   merge-base rc 0
```
Reading (item 4) — which attacks make the gate read a red run as "not in history" and allow: a corrupt commit object (loose or
packed), an alternates file that points nowhere, a deleted red commit in a non-shallow clone, `git replace`, `.git/info/grafts`,
and an absolute `GIT_DIR` naming another repository (the gate then ignores `--root`). Not: a missing tree (→ 2 at the diff), a
missing blob (→ 1, correct), `GIT_WORK_TREE`, a relative `GIT_DIR`, `GIT_OBJECT_DIRECTORY` (→ 2 at step b), `GIT_SHALLOW_FILE`.
Mechanism (primary source: `scripts/ci_gate.py:213` `if _git(root, "cat-file", "-e", f"{sha}^{{commit}}")[0] != 0:` → `return False`):
the "absent → not in history" branch is taken for ANY failure of the peeled `cat-file`, and the contract's soundness argument
("an absent commit cannot be reachable from a complete ref", C2 e) assumes that a non-shallow clone whose ref resolves has a
complete history; a corrupt, deleted or alternates-held commit breaks that assumption without making the clone shallow, and
replace refs / grafts rewrite the local history view exactly as `.git/shallow` does, yet `--is-shallow-repository` says `false`.
Through the canonical consumer only replace and grafts end in a push (rows H-1); the other three are stopped by push_clean's own
git calls (rows H-2..H-4). No such state exists in this clone: `.git/objects/info/` holds no alternates file, `.git/info/grafts`
is absent, `git replace -l | wc -l` = `0` (measured, section 3's environment block). A fix for the five history attacks, each
part measured above: in `_git`'s env `GIT_NO_REPLACE_OBJECTS=1` and `GIT_GRAFT_FILE=/dev/null` (next to `LC_ALL=C`; replace and
grafts then read `merge-base rc 0`), and before reading any "absent" as "not in history", prove the history complete once per
decision with `git rev-list --quiet <origin_sha>` (exit 0 healthy; 128 for the deleted, the corrupt loose, the corrupt packed
and the alternates-held commit; it does NOT see replace or grafts: `rev-list --quiet (replace, as is) rc=0`, `(grafts, as is)
rc=0`) — the absent test then stays sound. The `GIT_DIR` row needs a separate fix: drop `GIT_DIR`/`GIT_WORK_TREE`/
`GIT_OBJECT_DIRECTORY` from `_git`'s env so that `-C --root` decides the repository (in push_clean an exported `GIT_DIR`
redirects push_clean's own git calls too, so the gate and the push agree there; the standalone gate and the waiter silently
ignore `--root`). Because C2 e names the test and the soundness
argument, this is a contract amendment, not a repair of the code against its contract.

```
$ git -C corrupt-pack/work rev-list --quiet <origin>      → error: inflate: data stream error (invalid distance too far back) / error: Could not read 4db232c… / rc=128
$ git -C replace/work rev-list --quiet <head>             → rc=0
$ git -C graft/work rev-list --quiet <head>               → rc=0
```

## 6. Item 5 — C3 (the API read) and C4 (the waiter), in-process

Probe `/tmp/vcg1/p5/probe5.py`: the repo's `scripts/ci_gate.py` loaded read-only by importlib; for C3 only the constant `API`
points at a local `ThreadingHTTPServer` that plays each failure (urllib, `json.load`, validation and `main()` are the real
code; `no_proxy` covers 127.0.0.1); the throwaway repo's origin is `https://github.com/o/r` (never contacted). The red run is on
the head, so a readable body must give 1.
```
== C3: the API read against a local server (127.0.0.1:40615); the red run is on the head
  ok                    rc=1   0.0s | REFUSED by ci-gate: run #9 (ed34d25) concluded failure — u9
  notjson               rc=2   0.0s | REFUSED by ci-gate: the runs could not be read (JSONDecodeError: Expecting value: line 1 column 1 (char 0)). Retry, or set CI_GATE_OFFLINE=<reason> to
  notjson      OFFLINE  rc=0   0.0s | WARNING: ci-gate could not read the runs (JSONDecodeError: …); pushing anyway: CI_GATE_OFFLINE=probe
  cut                   rc=2   0.0s | REFUSED by ci-gate: the runs could not be read (IncompleteRead: IncompleteRead(115 bytes read, 615 more expected)). …
  cut          OFFLINE  rc=0   0.0s | WARNING: ci-gate could not read the runs (IncompleteRead: …); pushing anyway: CI_GATE_OFFLINE=probe
  truncjson             rc=2   0.0s | REFUSED by ci-gate: the runs could not be read (JSONDecodeError: Unterminated string starting at: line 1 column 80 (char 79)). …
  truncjson    OFFLINE  rc=0   0.0s | WARNING: …
  redirect              rc=1   0.0s | REFUSED by ci-gate: run #9 (ed34d25) concluded failure — u9          (302 to the same host, followed)
  redirectoff           rc=1   0.0s | REFUSED by ci-gate: run #9 (ed34d25) concluded failure — u9          (302 to another host name, followed)
  notmod                rc=2   0.0s | REFUSED by ci-gate: the runs could not be read (HTTP Error 304: Not Modified). …
  notmod       OFFLINE  rc=0   0.0s | WARNING: …
  retry403              rc=2   0.0s | REFUSED by ci-gate: the runs could not be read (HTTP Error 403: Forbidden; X-RateLimit-Remaining: 0). …   (Retry-After: 60 sent, not shown)
  retry403     OFFLINE  rc=0   0.0s | WARNING: …
  retry429              rc=2   0.0s | REFUSED by ci-gate: the runs could not be read (HTTP Error 429: Too Many Requests). …                     (Retry-After: 30 sent, not shown)
  retry429     OFFLINE  rc=0   0.0s | WARNING: …
  slowheaders           rc=2  20.0s | REFUSED by ci-gate: the runs could not be read (TimeoutError: timed out). …
  drip                  rc=1  36.0s | (headers at once, then the body in 4 pieces 12 s apart: each socket read < 20 s; the decision came after 36.0 s)
```
(The drip row's first captured line was the slow-headers server thread's own BrokenPipe report, printed while `sys.stderr` was
redirected for the drip call; the gate's rc and time are the row's evidence.)

The waiter, the clock replaced (`_sleep`/`_now`), the runs file rewritten at each sleep; the origin ref is a real
`refs/remotes/origin/feat`; H changes `code.py` over its parent, whose run #9 is green:
```
  W1 in_progress -> cancelled -> newer run registered -> success: rc=0 slept=[30, 30, 30]
      | WAIT by ci-gate: run #10 (a1d13aa) is in_progress — u10
      | WAIT by ci-gate: the pushes after run #9 (6a69947), which concluded success, change code.py and no newer run is registered yet
      | WAIT by ci-gate: run #11 (a1d13aa) is queued — u11
      | ci-gate: run #11 (a1d13aa) passed
  W2 in_progress -> cancelled, nothing newer (deadline 120 s): rc=75 slept=[30, 30, 30, 30]
      | … | WAIT by ci-gate: 120 s passed and the verdict is still unknown: the pushes after run #9 (6a69947) … | Wait for the verdict: … | or push without waiting: CI_WAIT_SKIP=<reason>
  W3 --wait 0 on an unfinished run: rc=75 slept=[]
  W4 --wait 1 on an unfinished run: rc=75 slept=[1.0]
  W5 --wait 1, the read fails at the deadline: rc=2 slept=[1.0]
      | REFUSED by ci-gate: the runs could not be read (JSONDecodeError: …); 1 read(s) in a row failed while waiting
  W6 an INVALID record mid-wait (event=pull_request), then valid: rc=0 slept=[30, 30]
      | WAIT by ci-gate: the runs could not be read (workflow_runs[0] (id 1010): event is 'pull_request', not 'push'); retry 1 of 2
      | ci-gate: run #10 (a1d13aa) passed
  W7 origin moves H -> H2 during the wait; H's run cancelled by H2's; H2's run goes green: rc=75 slept=[30, 30, 30, 30, 30]
      | WAIT by ci-gate: run #10 (a1d13aa) is in_progress — u10
      | WAIT by ci-gate: the pushes after run #9 (6a69947), which concluded success, change code.py and no newer run is registered yet
      | WAIT by ci-gate: 150 s passed and the verdict is still unknown: …
      (origin now b6865b5 = H2 b6865b5; the waiter judged H a1d13aa)
== C4: huge --wait values and Ctrl-C, through the real CLI (subprocess)
  --wait 999999999999… (400 chars) rc=1 | TRACEBACK OverflowError: int too large to convert to float
  --wait 999999999999… (5000 chars) rc=64 | ci_gate.py: error: argument --wait: SECONDS must be a whole number >= 0, not '9999…
  --wait 1e400 (5 chars) rc=64 | ci_gate.py: error: argument --wait: SECONDS must be a whole number >= 0, not '1e400'
  --wait -0 (2 chars) rc=75 | or push without waiting: CI_WAIT_SKIP=<reason>
  --wait ٣ (1 chars) rc=75 | or push without waiting: CI_WAIT_SKIP=<reason>          (an Arabic-Indic 3: int() accepts it; a real 3 s wait)
  SIGINT after 2 s of --wait 60: rc=-2 traceback=True last=[KeyboardInterrupt]
  SIGINT to the process group (a terminal Ctrl-C) under bash: bash rc=-2 stdout=''
```
The ONE live GET (read-only; `urlopen` wrapped to count calls; the decision then used the real git of this clone, no second GET):
```
Wed Sep 23 10:04:27 UTC 2026
GETs: 1 | url: https://api.github.com/repos/Pxls21/agent-factory/actions/workflows/stage0-ci.yml/runs ? branch=claude%2Fsoundbox-kit-migration-iz1jwf&event=push&per_page=50
slug: Pxls21/agent-factory | total_count: 979 | returned: 50
head_branch: {'claude/soundbox-kit-migration-iz1jwf': 50}
event: {'push': 50}
status: {'in_progress': 1, 'completed': 49} | conclusion: {None: 1, 'success': 30, 'failure': 19}
run_attempt: {1: 50}
  newest: 979 3846636 in_progress None
origin ref: refs/remotes/origin/claude/soundbox-kit-migration-iz1jwf -> 3846636
live decision (no second GET): 75 | WAIT by ci-gate: run #979 (3846636) is in_progress — https://github.com/Pxls21/agent-factory/actions/runs/35845975349
```
(Origin moved b511e4a → 3846636 during the lane; `git diff --quiet 5689d9f 3846636 -- <the five>`: equal.)

Reading (item 5): C3 holds on every shape — a non-JSON 200, a cut body, a truncated body, a 304, a 403/429 each end in a named 2
and in 0 + WARNING under `CI_GATE_OFFLINE`; the 403 text carries the code and `X-RateLimit-Remaining`; a redirect is followed
(also to another host name). The 20 s `timeout` bounds each socket operation, not the read: slow headers end at 20.0 s, a
drip-fed body ran 36.0 s (F23's slow-drip half is now VERIFIED; the DNS half stays unmeasured). C4 holds: one line per state
change, `--wait 0` answers at once, `--wait 1` sleeps once, three failed reads end in 2, the deadline ends in 75 with the hint.
Four observations: W7 — the waiter resolves the origin ref once (`scripts/ci_gate.py:360` `origin_sha = resolve_commit`, before
`scripts/ci_gate.py:380` `return _wait(args, verdict, hint)`), so when origin moves during a wait it keeps judging the old head
and waits out its deadline (75) although the new head's run passed — the conservative direction, never a wrong 0; C4 says "It
runs the decision every 30 s", and the decision includes step b; undisclosed in D1-D8. A 400-digit `--wait` ends in a Python
traceback with rc 1 (the code for "red"), not 64 (`scripts/ci_gate.py:316` `deadline = _now() + args.wait`: int→float overflow);
`_seconds` rejects 5000 digits only because of Python's int-string limit. SIGINT ends in a `KeyboardInterrupt` traceback and
death by signal (rc -2; under bash the whole group dies, so push_clean cannot push after it) — the builder's NOT-done item,
confirmed. `Retry-After` is never shown (C3 does not ask for it).

## 7. Item 6 — C5, the REAL push_clean.sh in throwaway repos (bare origins under /tmp/vcg1/p6)

Probe `/tmp/vcg1/p6/probe6.py`: each throwaway repo COMMITS byte copies of `scripts/push_clean.sh` (4e835e99bdf2a86e) and
`scripts/ci_gate.py` (f1e2246f043ff702) and runs `bash scripts/push_clean.sh <mode>` there; "pushed" compares origin's
`refs/heads/feat` before and after the run; "worktrees" counts `git worktree list` entries after it (1 = no leak). Seams outside
the scripts: a bare origin's `hooks/pre-receive` (the push fails) and a private `GIT_EXEC_PATH` whose `git-filter-branch` fails
or changes the tree (the trailer and tree stages fail). "Someone else" = a second clone that pushes a red commit to origin.
```
script bytes: 4e835e99bdf2a86e push_clean.sh · f1e2246f043ff702 ci_gate.py
== (6a) FETCH_HEAD equality and the full remote ref (--no-delegates-live)
ok  want rc=1 pushed=False | rc=1 pushed=False worktrees=1 | control: the head's run red | REFUSED by ci-gate: run #9 (1cf72ad) concluded failure — u9
ok  want rc=0 pushed=True  | rc=0 pushed=True  worktrees=1 | control: the head's run green | ci-gate: run #9 (1cf72ad) passed / == boundary (1 commits) == / … / == pushing 2f02195… ==
   remote.origin.fetch: ['+refs/heads/*:refs/remotes/origin/*', '+refs/heads/feat:refs/remotes/mirror/feat']
ok  want rc=1 pushed=False | rc=1 pushed=False worktrees=1 | two refspec lines, both map feat | * [new branch] feat -> mirror/feat / REFUSED by ci-gate: run #9 (2b311b1) concluded failure — u9
ok  want rc=2 pushed=False | rc=2 pushed=False worktrees=1 | two lines: feat -> x/feat, side -> origin/feat; origin moved to a red head | REFUSED: refs/remotes/origin/feat is not the commit 'git fetch origin feat' ju…
BAD want rc=2 pushed=False | rc=1 pushed=False worktrees=1 | a negative refspec ^refs/heads/feat; origin moved to a red head | REFUSED by ci-gate: run #10 (6453b8b) concluded failure — u10
   get-url origin -> /tmp/vcg1/p6/insteadof/origin.git
ok  want rc=1 pushed=False | rc=1 pushed=False worktrees=1 | url.<base>.insteadOf rewrite; origin moved to a red head | REFUSED by ci-gate: run #10 (238bba0) concluded failure — u10
ok  want rc=128 pushed=False | rc=128 pushed=False worktrees=1 | git fetch fails (origin path does not exist; FETCH_HEAD from an earlier fetch) | fatal: '…/does-not-exist.git' does not appear to be a git repository / …
ok  want rc=1 pushed=False | rc=1 pushed=False worktrees=1 | a local TAG named origin/feat at the old green head; origin moved to a red head | REFUSED by ci-gate: run #10 (a39c2eb) concluded failure — u10
ok  want rc=1 pushed=False | rc=1 pushed=False worktrees=1 | a REMOTE tag named feat (green) while origin's branch feat moved to a red head | ci-gate: run #9 (2b7b51c) passed / == boundary (1 commits) == / 0330071 the local commit to push / == pushing 03300712…
   FETCH_HEAD: 2b7b51cd8fa76fc793fe683b23bd470b1a7e395f		tag 'feat' of /tmp/vcg1/p6/remote-tag/origin
   tracking ref origin/feat: 2b7b51c  red head: a39c2eb
== (6b) --lanes-live: the inner run fails at each stage; worktrees afterwards; the code passes through
ok  want rc=1 pushed=False  | rc=1 pushed=False worktrees=1  | the gate: red -> 1 | REFUSED by ci-gate: run #9 (2b7b51c) concluded failure — u9
ok  want rc=75 pushed=False | rc=75 pushed=False worktrees=1 | the gate: in_progress -> 75 | WAIT by ci-gate: run #9 (b6e0759) is in_progress — u9 / Wait for the verdict: python3 scripts/ci_gate.py --branch feat --runs-json …
ok  want rc=2 pushed=False  | rc=2 pushed=False worktrees=1  | the gate: runs unreadable -> 2 | REFUSED by ci-gate: the runs could not be read (FileNotFoundError: …)
ok  want rc=2 pushed=False  | rc=2 pushed=False worktrees=1  | the gate: a record invalid -> 2 | REFUSED by ci-gate: the runs could not be read (workflow_runs[0] (id 1009): event is 'pull_request', not 'push'). …
ok  want rc=3 pushed=False  | rc=3 pushed=False worktrees=1  | the trailer check: filter-branch fails, the trailer stays -> 3 | ci-gate: run #9 (b6e0759) passed / == boundary (2 commits) == / … / 1 trail[er(s) remain — ABORT.]
ok  want rc=2 pushed=False  | rc=2 pushed=False worktrees=1  | the tree check: filter-branch changes the tree -> 2 TREE MISMATCH | … / TREE MISMATCH after rewrite — ABORT, do not push.
ok  want rc=1 pushed=False  | rc=1 pushed=False worktrees=1  | the push: origin's pre-receive refuses -> 1 | ci-gate: run #9 (589dafd) passed / … / == pushing 450d9cf… ==
ok  want rc=0 pushed=True   | rc=0 pushed=True worktrees=1   | control: green, pushed from the worktree | … / == branch ref followed origin to 450d9cf (…
   branch ref followed origin: True | lane edit kept: a live lane's edit
== (6c) --lanes-live with dirty, DECLARED working copies of the scripts (the committed bytes must decide)
ok  want rc=1 pushed=False | rc=1 pushed=False worktrees=1 | dirty gate prints a green line, exits 0 | REFUSED by ci-gate: run #9 (589dafd) concluded failure — u9
ok  want rc=1 pushed=False | rc=1 pushed=False worktrees=1 | dirty gate half-edited (a syntax error) | REFUSED by ci-gate: run #9 (a92d9a1) concluded failure — u9
ok  want rc=1 pushed=False | rc=1 pushed=False worktrees=1 | dirty push_clean.sh (comment) AND dirty gate (exit 0), both declared | REFUSED by ci-gate: run #9 (a92d9a1) concluded failure — u9
INFO (outer = the working copy): a declared push_clean.sh edited back to $OLDPWD + a dirty gate: rc=0 pushed=True worktrees=1 | == boundary (1 commits) == / … / == pushing 8e75008… == / == branch r…
rows: 20 BAD: 1
$ ls -d /tmp/push-clean-wt.* | wc -l
0
```
The one BAD row is my expectation, not the script: with `^refs/heads/feat` added, the command-line fetch still moved the
tracking ref (`negative: tracking=6453b8b origin feat=6453b8b`), so the gate read the red head and refused (1, nothing pushed).
The remote-tag row, read after the run and fixed by hand in the throwaway clone:
```
remote-tag before: tracking=2b7b51c origin branch feat=a39c2eb origin tag feat=2b7b51c
after 'git fetch origin refs/heads/feat': FETCH_HEAD=a39c2eb tracking=a39c2eb
real clone: local tags named like the branch: 0; refs/tags total: 4
```
Reading (item 6): the gate's code passes through unchanged at every exit tried — 1, 2, 75 and push_clean's own 3 and 2 (TREE
MISMATCH), in both modes; the detached worktree is removed after every inner failure (`worktrees=1` on all 20 rows, no
`/tmp/push-clean-wt.*` left); a narrowed or re-pointed refspec refuses (2); an `insteadOf` rewrite, a failed fetch, a local branch
or tag named `origin/feat` are all handled; a dirty, declared `scripts/ci_gate.py` never decides (three new shapes). Two
observations: (P-1) a REMOTE tag named exactly like the branch defeats the FETCH_HEAD check — `git fetch origin "$BRANCH"`
(`scripts/push_clean.sh:64` `git fetch origin "$BRANCH"`) resolves the name with `refs/tags/` before `refs/heads/` (FETCH_HEAD above says `tag 'feat'`), so a
stale tracking ref at the tag's commit passes `scripts/push_clean.sh:70` (`$FETCHED`), the gate reads the stale green (`ci-gate: run #9 (2b7b51c)
passed`), and only git's own non-fast-forward rule stopped the push; the contract names that exact fetch command (C5), so this
is a hole in the check's premise; fix `git fetch origin "refs/heads/$BRANCH"` (measured above); the real clone holds no such tag
locally (the remote's tag list was not read: `git ls-remote` is outside the brief's allowed reads). (P-2, INFO) the OUTER
`--lanes-live` run is always the working copy the operator names: a lane that holds `scripts/push_clean.sh` dirty and declared
controls the inner call (the last row pushed onto red after the outer copy was edited back to `$OLDPWD`); inherent to running a
script from disk; a guard could refuse a `.lanes-live` that lists either script.

## 8. Item 7 — C6, the workflow pin reads BOTH triggers from the parsed YAML

Primary source: `tests/test_stage0_ci_workflow.py:73` `test_the_push_gate_ignores_exactly_what_both_triggers_ignore` loads
`scripts/ci_gate.py` by path and compares `on["push"]["paths-ignore"]` and `on["pull_request"]["paths-ignore"]` from
`yaml.safe_load` with `[gate.IGNORED_PREFIX + "**"]`; `tests/test_stage0_ci_workflow.py:67` `test_pull_request_runs_skip_transcript_only_changes`
`test_pull_request_runs_skip_transcript_only_changes` pins the whole `pull_request` dict. One scratch mutant each way (rows of
section 9, driver `/tmp/vcg1/mut/driver.py`):
```
N45   | C6-null | NULL EDIT (must pass): reorder + comments + flow style + anchor | compiles=ok collected=129 | 129 passed in 13.40s | SURVIVED |
N44   | C6 | pull_request's paths-ignore removed, its text left in a comment | compiles=ok collected=129 | 2 failed, 127 passed in 13.13s | KILLED | test_pull_request_runs_skip_transcript_only_changes, test_the_push_gate_ignores_exactly_what_both_triggers_ignore
      E       AssertionError: assert None == {'paths-ignore': ['transcripts/**']}
N43   | C6 | pull_request ignores one level only | ... | 2 failed, 127 passed | KILLED | (the same two tests)
N46   | C6 | push gains a second ignored pattern the gate does not know | ... | 2 failed, 127 passed | KILLED | test_transcript_only_push_runs_no_ci, test_the_push_gate_ignores_exactly_what_both_triggers_ignore
```
N45 rewrote the whole `on:` block as `pull_request: {paths-ignore: &ignored ['transcripts/**']}` then `push: paths-ignore:
*ignored` (order swapped, comments gone, flow style, an anchor): the parsed triggers are equal, so it passes — correctly. N44
deleted the key and left its text in a comment: red. Reading (item 7): yes — the pin reads both triggers from the parsed YAML;
a comment-only or reordering edit cannot fail it and a real change cannot pass it.

## 9. Item 9 — mutation audit, NEW rows (N*, none of R1-R25 / X1-X14), scratch copies only

Driver `/tmp/vcg1/mut/driver.py`; per row a fresh copy of `/tmp/vcg1/mut/base` (the five files at the PIN bytes — sha256
prefixes d868ae9004186d48 / f1e2246f043ff702 / 4e835e99bdf2a86e / 70c04c384332b61d / 25b8c7ceeab3e921, re-hashed after the audit —
plus `scripts/setup.sh`, `tests/conftest.py`, `pyproject.toml`); one exact-string edit whose anchor occurs exactly once; the file
must change; `py_compile` / `bash -n` / `yaml.safe_load`; `--collect-only`; both test files. Driver self-test (its INVALID paths fire):
```
S1 | INVALID anchor count 0
S2 | INVALID: the file did not change
S3 | INVALID compile FAIL PyCompileError
```
Unmutated control: `129 passed in 14.26s` (rc 0). Rows (pasted from `/tmp/vcg1/mut/chunk{1,2,3}.txt`; killer lists cut to 3):
```
N1    | C1 | the expected-run 75 loses its WAIT by ci-gate: prefix | compiles=ok collected=129 | 3 failed, 126 passed in 13.40s | KILLED | test_a_code_push_after_the_green_run_waits_for_its_run, test_the_waiter_follows_a_push_to_its_verdict[three-polls], …[a-repeated-state]
N2    | C1 | a git failure during the decision exits 1 (red) instead of 2 | compiles=ok collected=129 | 2 failed, 127 passed in 13.27s | KILLED | test_cli_refuses_when_git_cannot_walk_the_history, test_an_ancestry_read_that_exits_128_on_a_present_commit_refuses
N3    | C1 | the CI_GATE_OFFLINE warning goes to stdout | compiles=ok collected=129 | 29 failed, 100 passed in 14.11s | KILLED | test_cli_fails_closed_when_the_runs_cannot_be_read[None], … +26
N4    | C1 | a push-mode 75 omits the waiter command and the escape | compiles=ok collected=129 | 5 failed, 124 passed in 13.21s | KILLED | test_cli_waits_while_the_verdict_run_is_unfinished[requested], … +2
N5    | C1 | the CI_WAIT_SKIP warning goes to stdout | compiles=ok collected=129 | 6 failed, 123 passed in 14.26s | KILLED | test_cli_waits_while_the_verdict_run_is_unfinished[requested], … +3
N6    | C1 | --wait -1 is accepted (usage error not 64) | compiles=ok collected=129 | 2 failed, 127 passed in 14.74s | KILLED | test_usage_errors_exit_64[argv3], test_usage_errors_exit_64[argv4]
N52   | C1 | an allow (0) prints to stderr, stdout stays empty | compiles=ok collected=129 | 9 failed, 120 passed in 14.58s | KILLED | test_cli_refuses_a_red_head_and_allows_the_declared_fix, test_cli_reads_ancestry_from_git, test_a_padded_ci_fix_allows +6
N7    | C2a | the shallow refusal skipped in wait mode | compiles=ok collected=129 | 129 passed in 14.67s | SURVIVED |
N7b   | C2a | a failed --is-shallow-repository read counts as complete | compiles=ok collected=129 | 129 passed in 13.89s | SURVIVED |
N8    | C2b | the origin ref resolved without ^{commit} (a tree resolves) | compiles=ok collected=129 | 129 passed in 14.12s | SURVIVED |
N9    | C2c | the --runs-json github refusal anchored at the URL's start | compiles=ok collected=129 | 2 failed, 127 passed in 14.68s | KILLED | test_runs_json_never_decides_against_a_github_origin[https://github.com/o/r], …[git@github.com:o/r.git]
N11   | C2d | head_sha checked by prefix (41 hex / a trailing newline pass) | compiles=ok collected=129 | 129 passed in 14.78s | SURVIVED |
N12   | C2d | a bool passes as an int | compiles=ok collected=129 | 2 failed, 127 passed in 14.59s | KILLED | test_cli_validates_every_record_before_deciding[run_number-bool], …[id-bool]
N13   | C2d | head_branch compared case-insensitively | compiles=ok collected=129 | 129 passed in 15.06s | SURVIVED |
N14   | C2d | a repeated run_number accepted | compiles=ok collected=129 | 1 failed, 128 passed in 14.94s | KILLED | test_cli_refuses_a_repeated_run_number
N15   | C2d | a non-object record reaches .get (traceback) | compiles=ok collected=129 | 1 failed, 128 passed in 14.46s | KILLED | test_cli_refuses_a_payload_without_a_run_list[payload2-workflow_runs[0]
N16   | C2e/D1 | git's error: lines no longer count (D1) | compiles=ok collected=129 | 1 failed, 128 passed in 14.00s | KILLED | test_cli_refuses_when_git_cannot_walk_the_history
N17   | C2e/D1 | git runs in the caller's locale (D1's prefix premise) | compiles=ok collected=129 | 129 passed in 13.02s | SURVIVED |
N51   | C2e | an absent commit reads as IN history | compiles=ok collected=129 | 3 failed, 126 passed in 12.83s | KILLED | test_cli_reads_ancestry_from_git, test_a_full_page_without_a_verdict_cannot_decide[50-2], …[49-0]
N20   | C2f | the expected-run check only for green verdicts | compiles=ok collected=129 | 1 failed, 128 passed in 15.18s | KILLED | test_a_kept_ci_fix_cannot_bless_the_red_run_again_after_its_fix_run_was_cancelled
N21   | C2f | the ignored prefix loses its slash (transcripts2/, a root file 'transcripts') | compiles=ok collected=129 | 129 passed in 13.31s | SURVIVED |
N23   | C2f | 'requested' is no longer unfinished | compiles=ok collected=129 | 2 failed, 127 passed in 14.93s | KILLED | test_unfinished_newest_run_waits[requested], test_cli_waits_while_the_verdict_run_is_unfinished[requested]
N24   | C2g | the page rule needs 51 records | compiles=ok collected=129 | 1 failed, 128 passed in 13.42s | KILLED | test_a_full_page_without_a_verdict_cannot_decide[50-2]
N25   | C2g/D4 | D4 undone: exactly the page size | compiles=ok collected=129 | 129 passed in 13.91s | SURVIVED |
N48a  | C2f/D3 | D3 undone: OFFLINE cannot rescue a null conclusion | compiles=ok collected=129 | 1 failed, 128 passed in 13.07s | KILLED | test_cli_cannot_decide_a_completed_run_with_no_conclusion
N48b  | C2g/D3 | D3 undone: OFFLINE cannot rescue a full page | compiles=ok collected=129 | 1 failed, 128 passed in 12.75s | KILLED | test_a_full_page_without_a_verdict_cannot_decide[50-2]
N26   | C3 | an HTTP error's text loses its status | compiles=ok collected=129 | 3 failed, 126 passed in 12.91s | KILLED | test_an_unreadable_api_cannot_decide[403-rate-limit], …[404], …[500]
N28   | C3 | a non-JSON API body is no longer caught (traceback) | compiles=ok collected=129 | 129 passed in 13.44s | SURVIVED |
N49   | C3/D6 | D6: the redaction misses user:password@ | compiles=ok collected=129 | 1 failed, 128 passed in 13.45s | KILLED | test_a_non_github_origin_cannot_decide[https://user:s3cret@gitlab.example/o/r.git]
N29   | C4 | the waiter prints every poll | compiles=ok collected=129 | 2 failed, 127 passed in 13.67s | KILLED | test_the_waiter_follows_a_push_to_its_verdict[a-repeated-state], test_the_waiter_stops_at_its_deadline
N30   | C4 | the waiter retries a git failure like a read failure | compiles=ok collected=129 | 129 passed in 12.56s | SURVIVED |
N31   | C4/D8 | D8 undone: a failed read at the deadline retries (75) | compiles=ok collected=129 | 1 failed, 128 passed in 16.62s | KILLED | test_the_waiter_ignores_the_push_overrides
N32   | C4/D7 | D7 undone: an invalid record ends the wait at once | compiles=ok collected=129 | 129 passed in 15.61s | SURVIVED |
N33   | C4/D2 | D2: the ignore line omits CI_GATE_OFFLINE | compiles=ok collected=129 | 1 failed, 128 passed in 15.29s | KILLED | test_the_waiter_ignores_the_push_overrides
N34   | C4 | the last sleep overshoots | compiles=ok collected=129 | 1 failed, 128 passed in 18.54s | KILLED | test_the_waiter_stops_at_its_deadline
N35   | C4 | failed jobs listed for the wrong verdict | compiles=ok collected=129 | 2 failed, 127 passed in 15.74s | KILLED | test_the_waiter_lists_the_failed_jobs_of_a_red_verdict, test_the_waiter_keeps_the_red_verdict_when_the_jobs_cannot_be_read
N37   | C5 | the FETCH_HEAD check reads the short name | compiles=ok collected=129 | 1 failed, 128 passed in 13.91s | KILLED | test_push_clean_reads_the_full_remote_ref_not_a_local_origin_branch
N38   | C5 | --lanes-live collapses every failure to 1 | compiles=ok collected=129 | 129 passed in 13.90s | SURVIVED |
N39   | C5 | the worktree removed only after a success | compiles=ok collected=129 | 1 failed, 128 passed in 13.23s | KILLED | test_push_clean_lanes_live_refusal_leaves_no_worktree
N54   | C5 | RANGE reads the short name again | compiles=ok collected=129 | 129 passed in 14.55s | SURVIVED |
N43   | C6 | pull_request ignores one level only | compiles=ok collected=129 | 2 failed, 127 passed in 12.61s | KILLED | test_pull_request_runs_skip_transcript_only_changes, test_the_push_gate_ignores_exactly_what_both_triggers_ignore
N44   | C6 | pull_request's paths-ignore removed, its text left in a comment | compiles=ok collected=129 | 2 failed, 127 passed in 13.13s | KILLED | (the same two)
N46   | C6 | push gains a second ignored pattern the gate does not know | compiles=ok collected=129 | 2 failed, 127 passed in 12.46s | KILLED | test_transcript_only_push_runs_no_ci, test_the_push_gate_ignores_exactly_what_both_triggers_ignore
N45   | C6-null | NULL EDIT (must pass): reorder + comments + flow style + anchor | compiles=ok collected=129 | 129 passed in 13.40s | SURVIVED |
```
The first `E` line of eight load-bearing kills (re-run with capture, same code):
```
N2    E  AssertionError: WARNING: ci-gate: runs read from …/runs.json (a test input), not the Act…   (rc 1 where 2 was due)
N16   E  AssertionError: ci-gate: no stage0-ci run in this branch's history; nothing to read        (allowed where 2 was due)
N20   E  AssertionError: ci-gate: run #9 (b924eaf) concluded failure; CI_FIX=1009 declares this push fixes it   (0 where 75 was due)
N48b  E  AssertionError: assert 'REFUSED by ci-gate: the runs could not be read (no verdict in the newest 50 runs' in 'WARNING: …
N31   E  assert 75 == 2
N37   E  AssertionError: From …/origin   (push_clean exit 2 where 1 was due)
N39   E  AssertionError: ['worktree …/work', 'worktree /tmp/push-clean-wt.2CeaQn']   (the leak)
N44   E  AssertionError: assert None == {'paths-ignore': ['transcripts/**']}
```
AF-AP-138 — every distinct killing test (67; truncated parametrized IDs mapped back to full node IDs from the base tree's own
collection) on the UNMUTATED tree:
```
rows: 44 {'KILLED': 30, 'SURVIVED': 14}
distinct killing tests: 67
compiles all ok: True | collected: ['129']
truncated killers: 67 -> full node ids: 67 | unmatched: []
67 passed in 10.19s
unmutated rc=0
```
(A first attempt with the truncated IDs exited 4 — a pytest usage error, no test ran — and is not counted.)

Survivors, classified:
| row | class | why |
|---|---|---|
| N45 | EQUIVALENT BY DESIGN | the null edit must pass (item 7) |
| N7b | EQUIVALENT (git ≥ 2.15) | a failed `--is-shallow-repository` on a real repo implies step b fails too (2 either way) |
| N17 | EQUIVALENT IN VENUE | no git message catalogs here (`/usr/share/locale/de/LC_MESSAGES/git.mo`: absent), so the locale changes nothing; D1's `error:` premise is unpinned where catalogs exist |
| N25 | EQUIVALENT ON API DATA | the API never returns more than `per_page`; D4's `>=` differs only for a 51-record file |
| N8 | EQUIVALENT ON push_clean INPUT | push_clean always passes a remote-tracking ref; only a hand-typed tree/blob `--origin-ref` with an empty run list differs (0 vs 2) |
| N7 | SURVIVED — test gap | C2 a is never exercised in `--wait` mode |
| N11 | SURVIVED — test gap | no 41-hex / trailing-newline `head_sha` row (item 2's shapes); under the mutant such a red record reads "absent" → 0 |
| N13 | SURVIVED — test gap | no case-only `head_branch` row |
| N21 | SURVIVED — test gap | no `transcripts2/x` or root-file `transcripts` row (item 3's shapes); under the mutant → a missed run (0) |
| N28 | SURVIVED — test gap | no non-JSON 200 through the API path (the runs-json path has its own `except`); under the mutant → a traceback rc 1 |
| N30 | SURVIVED — test gap | no git failure inside a wait |
| N32 | SURVIVED — D7 unpinned | no invalid record inside a wait (my W6 probe shows the landed retry) |
| N38 | SURVIVED — test gap (C5) | every `--lanes-live` test ends in 1; the 75/2 pass-through there is unpinned (my item-6 rows show the landed code passes them) |
| N54 | SURVIVED — test gap (C5) | the RANGE half of "the full ref" is unpinned (the gate half is pinned, N37 killed) |
Tally: 44 rows — 30 KILLED, 14 SURVIVED (1 null edit by design, 4 equivalent, 9 test gaps: N7, N11, N13, N21, N28, N30, N32, N38,
N54), 0 INVALID; every mutant compiled and collected 129. Per contract line (computed from `/tmp/vcg1/mut/rows.jsonl`):
```
C1       7/7 killed (N1 N2 N3 N4 N5 N6 N52)
C2a      0/2 killed (N7* N7b*)
C2b      0/1 killed (N8*)
C2c      1/1 killed (N9)
C2d      3/5 killed (N11* N12 N13* N14 N15)
C2e      2/3 killed (N16 N17* N51)
C2f      3/4 killed (N20 N21* N23 N48a)
C2g      2/3 killed (N24 N25* N48b)
C3       2/3 killed (N26 N28* N49)
C4       5/7 killed (N29 N30* N31 N32* N33 N34 N35)
C5       2/4 killed (N37 N38* N39 N54*)
C6       3/3 killed (N43 N44 N46)
C6-null  0/1 killed (N45*)
total 30 / 44 killed; * = survived
```
Per accepted D-reading: D1 N16 killed / N17 equivalent in venue; D2 N33 killed; D3 N48a, N48b killed; D4 N25 equivalent on
API data; D6 N49 killed; D7 N32 survived (unpinned); D8 N31 killed.

## 10. Evidence audit (the builder's load-bearing claims, re-derived)

- 129 passed twice, set f94590af83b6: REPRODUCED (section 2).
- Red-green, "83 failed, 46 passed" against the landed scripts: REPRODUCED on a scratch copy with the ae16c6a bytes
  (`git show ae16c6a:<file>`) and the final tests:
  ```
  f19a6cbb99ea10b0 scripts/ci_gate.py (landed, ae16c6a)
  ab2412d387131433 scripts/push_clean.sh (landed, ae16c6a)
  718365358d1e855b .github/workflows/stage0-ci.yml (landed, ae16c6a)
  70c04c384332b61d tests/test_ci_gate.py (final)
  25b8c7ceeab3e921 tests/test_stage0_ci_workflow.py (final)
  83 failed, 46 passed in 10.27s
  landed rc=1
  ```
- D1's three date orders: REPRODUCED (section 5). The mechanism (git's walk follows commit dates) re-derived: the same deleted
  parent gives exit 1 or exit 0 by the order alone.
- The live decision: REPRODUCED with a newer run (section 6: `75 | WAIT by ci-gate: run #979 (3846636) is in_progress`).
- The builder's 39 mutants (R1-R25, X1-X14): NOT re-run (their claim); this lane ran 44 NEW rows instead (section 9).
- Stale context: `CLAUDE.md:34-39` (the push bullet: `scripts/ci_gate.py`, `CI_WAIT_SKIP=<reason>`) and `wiki/topics/infrastructure-and-tooling.md:42-45` (`ci_gate.py`) and `:78` now describe
  exit 75, `--wait 1800`, `CI_WAIT_SKIP` and `CI_GATE_OFFLINE` — true to the code. `AGENTS.md:23` / `.hermes.md:27` (`scripts/push_clean.sh --no-delegates-live`; "Push only
  through") still carry the condensed bullet with no gate (Codex/Hermes lanes cannot push; INFO, as F13 filed it). The ledger
  line `todo/BUILD-TASKLIST.md:215` quotes the old "this push supersedes it" as a dated 06:28Z record (history, not stale
  context). `docs/INCIDENT-LOG.md` AF-AP-141 says `scripts/ci_gate.py` "answers 2 otherwise" and marks it FIXED: true for the
  `merge-base` exit, not for the `cat-file -e` exit at `scripts/ci_gate.py:213` (`_git(root, "cat-file", "-e", f"{sha}^{{commit}}")`; section 5; inventory VR-12).

## 11. Item 8 — D1-D8, graded against the contract text

| D | the builder's reading | grade | evidence |
|---|---|---|---|
| D1 | C2 e: exit 1 is "not in history" only with no `error:`/`fatal:` line; otherwise "cannot tell" → 2 | ACCEPT — fail-closed, the contract's own "ANY other outcome → 2" | three date orders reproduced (section 5); without it the same-second case allows (N16 KILLED, E line `ci-gate: no stage0-ci run …`). Caveat: after an `error:` line the code falls to the `cat-file -e` test, which reads ANY failure as "absent" — so "cannot tell → 2" holds only while the red commit itself is readable (VR-2). N17 (no `LC_ALL=C`) is equivalent here: no git catalogs in this venue |
| D2 | C4: the waiter ignores `CI_GATE_OFFLINE` too | ACCEPT — C4's own rule ("three in a row → 2") cannot hold if OFFLINE turned a failed read into 0 | `test_the_waiter_ignores_the_push_overrides`; N33 KILLED (the ignore line) |
| D3 | `CI_GATE_OFFLINE` also rescues a completed run with no conclusion (C2 f) and a full page (C2 g) | ACCEPT — both are the API's data; WHAT IS DECIDED: OFFLINE rescues "failures to READ or VALIDATE the Actions API data"; without it no escape exists (CI_WAIT_SKIP changes only a 75) | N48a, N48b KILLED |
| D4 | C2 g "exactly 50" read as `>= 50` | ACCEPT — equal on API data (never more than `per_page`), fail-closed on a larger file | N25 EQUIVALENT ON API DATA |
| D5 | `test_unfinished_newest_run_allows` renamed `…_waits`; 3 → 5 statuses | ACCEPT — the brief's own "becomes the 75 table"; an "allows" name would be false | `tests/test_ci_gate.py:75` `test_unfinished_newest_run_waits` |
| D6 | (i) the github check needs the host to BE github.com; (ii) the refusal drops userinfo | ACCEPT both, with a finding at the edge: github.com with a port, `www.` or an uppercase host is "not github" — the normal path refuses 2 (fail-closed) but `--runs-json` then DECIDES (rc 0) where C2 c demands 64 (VR-3, reproduced) | N49 KILLED; section 11's CLI rows below |
| D7 | the waiter retries every DataError (invalid record, unknown status, null conclusion, full page), not only a failed read | ACCEPT as a reading — C2 treats validation as part of reading the runs; both end in 2, about 60 s later | W6 reproduced (an invalid record mid-wait → `retry 1 of 2` → 0); N32 SURVIVED: unpinned |
| D8 | at the deadline a failed last read returns 2, not 75 | ACCEPT as a reading — "returns the final decision"; the final decision of a failed read is 2; both mean "do not push" | W5 reproduced (`--wait 1`, read fails at the deadline → 2); N31 KILLED |

Undisclosed readings (not in D1-D8): (U1) steps a and b run ONCE per waiter invocation (`scripts/ci_gate.py:359-360` `check_clone(args.root)` before
`scripts/ci_gate.py:380` `return _wait(args, verdict, hint)`), so the waiter never re-resolves origin — C4 "It runs the decision every 30 s"; W7 reproduces the effect
(VR-7). (U2) `_seconds` accepts any Unicode decimal digit (`--wait ٣` = 3 s) and `-0`; harmless.

D6 edge, the real CLI, a throwaway repo, `--runs-json` with a green run (no network: the runs-json path reads the URL locally):
```
origin https://github.com/o/r (get-url: https://github.com/o/r) -> rc=64 | ci_gate.py: error: --runs-json is a test input and origin is a github.com remote: it never decides a real push (unset CI_GATE_RUNS_JSON)
origin ssh://git@github.com:22/o/r.git (get-url: ssh://git@github.com:22/o/r.git) -> rc=0 | WARNING: ci-gate: runs read from ../green.json (a test input), not the Actions API ci-gate: run #9 (76ed6e0) passed
origin https://github.com:443/o/r (get-url: https://github.com:443/o/r) -> rc=0 | WARNING: … ci-gate: run #9 (76ed6e0) passed
origin https://www.github.com/o/r (get-url: https://www.github.com/o/r) -> rc=0 | WARNING: … ci-gate: run #9 (76ed6e0) passed
origin https://GitHub.com/o/r (get-url: https://GitHub.com/o/r) -> rc=0 | WARNING: … ci-gate: run #9 (76ed6e0) passed
```
and the regex in-process: `https://github.com:443/o/r`, `https://www.github.com/o/r`, `https://GitHub.com/o/r`,
`ssh://git@github.com:22/o/r.git` → NOT github; `/srv/mirrors/github.com/o/r`, `file:///tmp/github.com/o/r.git`,
`https://evil.example/github.com/o/r` → `o/r` (read as github.com).

## 12. Item 10 — issue #34's ledger on the PIN (F1-F23 of `tasks/briefs/ci/VERIFY-CI-GATE-report.md`)

| F | status | the pinning test on the PIN, or the current reproduction |
|---|---|---|
| F1 | CLOSED as filed; the CLASS has open siblings | shallow: `test_cli_refuses_a_shallow_clone_even_offline`; stale ref: `test_push_clean_refuses_a_stale_origin_ref`; local `origin/<b>` branch: `test_push_clean_reads_the_full_remote_ref_not_a_local_origin_branch`; exit 128 on a present commit: `test_an_ancestry_read_that_exits_128_on_a_present_commit_refuses`; a walk error: `test_cli_refuses_when_git_cannot_walk_the_history`. Open siblings of the same class ("cannot tell" read as "not in history"): VR-1 (replace/grafts: push_clean PUSHED), VR-2 (absent/corrupt/alternates), VR-4 (a remote tag named like the branch) |
| F2 | CLOSED | `test_push_clean_lanes_live_refusal_leaves_no_worktree`; item 6: `worktrees=1` after every inner failure stage (gate 1/2/75, trailers 3, TREE MISMATCH 2, push 1) |
| F3 | CLOSED | `test_cli_cannot_decide_an_unknown_status` (None, 7, "", "weird", "COMPLETED"); item 2: 'Completed', 'in_progress ', 'IN_PROGRESS' → 2 |
| F4 | CLOSED (one gap) | `test_the_runs_query_is_encoded`, `test_an_unreadable_api_cannot_decide`, `test_repo_slug_reads_each_github_form`, `test_a_non_github_origin_cannot_decide`, `test_blank_overrides_count_as_unset`, `test_a_padded_ci_fix_allows`, `test_runs_json_with_a_local_origin_says_so_on_stderr`, `test_push_clean_passes_cannot_decide_through`; gap: a non-JSON 200 through the API path (N28 SURVIVED; the landed code gives 2, item 5 `notjson`) |
| F5 | CLOSED for the canonical URL; OPEN at the edge | `test_runs_json_never_decides_against_a_github_origin` (64); open: VR-3 (github.com with a port / `www.` / uppercase → the test input decides, rc 0) |
| F6 | CLOSED | `test_the_runs_query_is_encoded` (`fix#1`, `fix&y`, `claude/x`, `feat-é`); `test_cli_validates_every_record_before_deciding[head_branch-foreign]`, `[event-pr]`; the live GET (section 6): `branch=claude%2F…`, 50/50 this branch and `push` |
| F7 | CLOSED | `test_cli_validates_every_record_before_deciding` (17 shapes, no traceback), `test_cli_refuses_a_payload_without_a_run_list`; item 2: 68 record shapes, `TRACEBACK: 0` (other traceback paths: VR-8, VR-9 — not F7's class) |
| F8 | CLOSED | `test_usage_errors_exit_64`; residual VR-8 (a 400-digit `--wait` → traceback rc 1) |
| F9 | CLOSED by decision | `test_unfinished_newest_run_waits`, `test_cli_waits_while_the_verdict_run_is_unfinished`, `test_push_clean_waits_for_an_unfinished_verdict`, the expected-run tests; live 75 (section 6) |
| F10 | paths-ignore half CLOSED; PR-runs half OPEN (policy) | `test_pull_request_runs_skip_transcript_only_changes`; the gate still asks only `event=push` (`scripts/ci_gate.py:145` `urllib.parse.urlencode`) — undecided |
| F11 | CLOSED | `test_a_full_page_without_a_verdict_cannot_decide` (50 → 2) |
| F12 | CLOSED for a code fix push; OPEN for a transcripts-only one | `test_a_kept_ci_fix_cannot_bless_the_red_run_again_after_its_fix_run_was_cancelled`; open, reproduced (section 12 rows below): a kept CI_FIX re-blesses the red run on every later transcripts-only push (harmless: such pushes start no run) |
| F13 | CLOSED for CLAUDE.md and the wiki; INFO for the mirrors | `CLAUDE.md:34-39` (`CI_WAIT_SKIP=<reason>`), `wiki/topics/infrastructure-and-tooling.md:42-45,78` (`ci_gate.py`); `AGENTS.md:23` (`scripts/push_clean.sh --no-delegates-live`), `.hermes.md:27` unchanged (their lanes cannot push) |
| F14 | OPEN — UNVERIFIED | the owner's notification setting is not measurable here |
| F15 | OPEN — DOC | re-read from primary source (section 4): "If any path names do not match … the workflow will run"; no live mixed push |
| F16 | OPEN | push_clean exits 2 for the FETCH_HEAD refusal (`scripts/push_clean.sh:74` `exit 2`), TREE MISMATCH (`scripts/push_clean.sh:104` `TREE MISMATCH after rewrite`) and the gate's "cannot decide"; 1 for the dirty tree, the lanes refusals, the gate's red and a failed push (item 6 rows); the text tells them apart |
| F17 | CLOSED | `test_an_unreadable_api_cannot_decide[403-rate-limit]` (`HTTP Error 403: Forbidden; X-RateLimit-Remaining: 0`); `Retry-After` never shown (INFO) |
| F18 | docstring half CLOSED; runtime half OPEN | a lone cancelled run still prints "no stage0-ci run in this branch's history" (H5c); new inexact text "no newer run is registered yet" while one is (H3, H5a, W1) |
| F19 | CLOSED (one gap) | `[head_sha-option]`, `[head_sha-short]`, `[head_sha-upper]`; gap: 41 hex / a trailing newline are unpinned (N11 SURVIVED; the landed `fullmatch` refuses both, item 2) |
| F20 | CLOSED for `scripts/ci_gate.py`; the outer script is inherently the working copy | `test_push_clean_lanes_live_runs_the_committed_gate`; item 6 (6c): three new dirty shapes refused; VR-15 (a declared `scripts/push_clean.sh` controls the inner call) |
| F21 | OPEN — UNVERIFIED | no non-proxied shell here (no PC use) |
| F22 | types and repeats CLOSED; re-run half OPEN | `[run_number-str]`, `[run_number-bool]`, `test_cli_refuses_a_repeated_run_number`; `run_attempt` still unread (live: `run_attempt: {1: 50}`) |
| F23 | slow-drip half now VERIFIED OPEN; DNS half UNVERIFIED | item 5: a drip-fed body decided after 36.0 s against the 20 s timeout (VR-10) |

F12's open half, the real CLI (a throwaway repo; the red run #9 on R; origin's head a transcripts-only commit):
```
REFUSED by ci-gate: run #9 (3dfc0be) concluded failure — / Read its failed jobs first. A push that carries the fix sets CI_FIX=1009.
  CI_FIX='' rc=1
ci-gate: run #9 (3dfc0be) concluded failure; CI_FIX=1009 declares this push fixes it
  CI_FIX='1009' rc=0
ci-gate: run #9 (3dfc0be) concluded failure; CI_FIX=1009 declares this push fixes it
  next push, CI_FIX still 1009: rc=0
WAIT by ci-gate: the pushes after run #9 (3dfc0be), which concluded failure, change code.py and no newer run is registered yet
  a code push, CI_FIX still 1009: rc=75
```

## 13. Finding inventory (no severity filter) — the blocking predicate applied

Predicate columns (the brief's): (1) contract-mapped (C1-C7 or a WHAT IS DECIDED ruling) · (2) reproduced through the real CLI or
the real push_clean in a throwaway repo · (3) materially effective: a wrong exit code on a reachable input · (4) a concrete
discriminator · (5) in-boundary (the five files). Evidence: VERIFIED = reproduced this session; DOC = GitHub documentation only;
INFERRED = reasoned from primary source, not measured. BLOCKER needs all five.

**VR-1 · FOLLOW-UP (top) · a replaced or grafted local history reads the red run as "not in history", and the REAL push_clean pushes.**
Evidence VERIFIED (section 5: `pcl-replace push_clean rc=0 PUSHED`, `pcl-graft push_clean rc=0 PUSHED`; the gate said `ci-gate: no
stage0-ci run in this branch's history`). (1) no for the code: C2 a refuses only `--is-shallow-repository` = `true`, and C2 e's
soundness argument names only shallowness; `git replace` and `.git/info/grafts` truncate the local history exactly as `.git/shallow`
does but are not "shallow" to git. (2) yes. (3) not in the measured state: this clone has `git replace -l | wc -l` = `0` and no
grafts file; the precondition is a deliberate local history rewrite. (4) yes: `GIT_NO_REPLACE_OBJECTS=1` / `GIT_GRAFT_FILE=/dev/null`
→ `merge-base rc 0` (measured). (5) yes. Fix: set both in `_git`'s env at `scripts/ci_gate.py:87` (next to `LC_ALL=C`), or refuse
like a shallow clone — a C2 a amendment. ESCALATION TRIGGER: any push venue whose clone carries replace refs or a grafts file
(the PC clone was NOT measured).

**VR-2 · FOLLOW-UP · a missing or unreadable red commit in a NON-shallow clone reads "absent → not in history"; the gate allows.**
Evidence VERIFIED (section 5: a deleted commit, a corrupt loose object, a corrupt packed object, alternates pointing nowhere —
each `WRONG-ALLOW rc=0`). Through the canonical consumer each push was stopped by ANOTHER git call (`git fetch` rc 128 on the
corrupt object; `git push` "non-fast-forward" on the deleted one; push_clean's dirty-tree check on the broken alternates) — an
accident, not the gate. Mechanism: `scripts/ci_gate.py:213` (`_git(root, "cat-file", "-e", f"{sha}^{{commit}}")`) reads ANY failure of `git cat-file -e <sha>^{commit}` as "absent", and
C2 e's argument "an absent commit cannot be reachable from a complete ref" assumes an intact object store; the corrupt case is
not even "absent" (C2 e's category) — git says `error: inflate: data stream error`. (1) partial: the corrupt case contradicts C2 e's
category "ABSENT"; the deleted/alternates cases follow its letter. (2) the gate: yes; push_clean: no push. (3) not through
push_clean; the standalone gate and the waiter print a false "no stage0-ci run" (0). (4) yes: `git rev-list --quiet <origin>` =
0 healthy, 128 in all four damaged clones (measured). (5) yes. Fix: prove the history complete once per decision (`rev-list
--quiet <origin_sha>`) before trusting absence — a C2 e amendment. Same anti-pattern as AF-AP-141 (an exit code read as a
boolean without its stderr), an unexploded sibling in the function AF-AP-141 marks FIXED (VR-12).

**VR-3 · FOLLOW-UP · the `--runs-json` guard misses github.com remotes written with a port, `www.` or an uppercase host.**
Evidence VERIFIED (section 11: `ssh://git@github.com:22/o/r.git`, `https://github.com:443/o/r`, `https://www.github.com/o/r`,
`https://GitHub.com/o/r` → rc 0, the test input decided). (1) yes: C2 c and WHAT IS DECIDED ("refused (exit 64) when origin is a
github.com remote, so it can never decide a real push"). (2) yes, the real CLI. (3) not in the measured state: this clone's origin
is `https://github.com/Pxls21/agent-factory` (refused, 64); the path needs a non-canonical URL AND a leftover
`CI_GATE_RUNS_JSON` — the misuse F5 itself classed as a follow-up — and with such a URL every normal push already ends in 2.
(4) yes. (5) yes (`scripts/ci_gate.py:71` `GITHUB`, used at `scripts/ci_gate.py:364`). Fix: parse the host (urlsplit / the scp
form), lowercase it, drop the port and a leading `www.`, then compare with `github.com`. ESCALATION TRIGGER: a push venue whose
origin URL uses such a form.

**VR-4 · FOLLOW-UP · a remote TAG named exactly like the branch defeats C5's FETCH_HEAD check.** Evidence VERIFIED (section 7:
`FETCH_HEAD: 2b7b51c… tag 'feat' of …`, tracking ref stale at the tag's commit, the gate `ci-gate: run #9 (2b7b51c) passed`; the push
then failed "non-fast-forward"). Mechanism: `git fetch origin "$BRANCH"` (`scripts/push_clean.sh:64` `git fetch origin "$BRANCH"`) resolves the name with
`refs/tags/` before `refs/heads/`. (1) no for the code: C5 names that exact fetch command; the check's purpose (F1-B) is what fails.
(2) yes, the real push_clean. (3) not in the probe (git's fast-forward rule stopped the push); a wrong push also needs a local branch
that already contains the red head while the tracking ref is stale. (4) yes: `git fetch origin refs/heads/feat` → `FETCH_HEAD=a39c2eb
tracking=a39c2eb`. (5) yes. Fix: fetch `refs/heads/$BRANCH` explicitly.

**VR-5 · FOLLOW-UP · the expected-run check is blind to ignored submodules and to `diff.relative`.** Evidence VERIFIED (section 4:
a gitlink bump under `.gitmodules` `ignore = all` or `diff.ignoreSubmodules=all` → 0; `diff.relative=true` + a subdirectory root →
0; GitHub starts a run in each — gitlink rows INFERRED, the relative row DOC). (1) no for the code: C2 f names the exact command.
(3) none today: 0 gitlinks here, both configs unset. (4) yes: `--ignore-submodules=none`, `--no-relative` (measured). (5) yes. Fix:
add both flags at `scripts/ci_gate.py:223` (the `--no-renames` call) — a C2 f amendment.

**VR-6 · INFO · net-diff misses that are benign in substance.** A push reverted by the next push (section 4, E-3) and a force-moved
origin whose new head equals the green code (section 3, H2): runs start that the gate does not expect; the head's code IS the green
run's code. push_clean never force-pushes.

**VR-7 · FOLLOW-UP · the waiter judges the origin sha it resolved at start.** Evidence VERIFIED (section 6, W7: origin moved H → H2,
H2's run #12 passed, the waiter waited out 150 s and returned 75). (1) partial: C4 "It runs the decision every 30 s", and the decision
includes step b; not disclosed in D1-D8 (U1). (3) the conservative direction (75, never a wrong 0); push_clean re-decides after its
own fetch. (4) yes. (5) yes. Fix: re-resolve the ref at each poll, or name the frozen sha in the waiter's lines.

**VR-8 · FOLLOW-UP · a 309-4300-digit `--wait` ends in a Python traceback with rc 1 (the "red" code).** Evidence VERIFIED (section 6:
`--wait 999999999999… (400 chars) rc=1 | TRACEBACK OverflowError: int too large to convert to float`). (1) yes: C1 "a Python traceback
is never a verdict". (3) no: the waiter never pushes; an absurd operator input. Fix: cap SECONDS in `_seconds`
(`scripts/ci_gate.py:272` `def _seconds(text)`) and exit 64 above it.

**VR-9 · INFO · SIGINT during `--wait` ends in a KeyboardInterrupt traceback and death by signal (rc -2; 130 in a shell).** The
builder's NOT-done, confirmed (section 6); under bash the whole group dies, so push_clean cannot push after it.

**VR-10 · FOLLOW-UP · the 20 s timeout does not bound a drip-fed body (F23, now VERIFIED).** Section 6: `drip rc=1 36.0s`. C3
keeps `timeout=20` (met literally); no contract line bounds the total. Fix: a wall-clock bound around the read.

**VR-11 · FOLLOW-UP · nine contract lines the suite does not pin (surviving mutants).** N7 (C2 a in `--wait` mode), N11 (41-hex /
trailing-newline `head_sha`), N13 (case-only `head_branch`), N21 (the prefix boundary: `transcripts2/`, a root file `transcripts`),
N28 (a non-JSON 200 through the API path), N30 (a git failure inside a wait), N32 (D7), N38 (the `--lanes-live` pass-through of 75
and 2), N54 (RANGE's full ref). The landed code handles every one correctly (sections 3-7) — unpinned, not broken. Fix: one test
row each in `tests/test_ci_gate.py`.

**VR-12 · FOLLOW-UP (registry, outside the boundary) · AF-AP-141's row is FIXED-too-early.** It says `scripts/ci_gate.py` "answers
2 otherwise"; the `cat-file -e` boolean at `scripts/ci_gate.py:213` (`_git(root, "cat-file", "-e", f"{sha}^{{commit}}")`) is the same class and still reads a corrupt commit as absent
(VR-2). Fix: amend the row; extend the screen's signature to `cat-file -e` exit-code booleans.

**VR-13 · INFO · inexact texts.** "no newer run is registered yet" while a newer run IS registered (cancelled, or red with a lower
`run_number`: sections 3 and 6, H3/H5a/W1); a lone cancelled run prints "no stage0-ci run in this branch's history" (H5c; F18's
runtime half); `Retry-After` never shown.

**VR-14 · INFO · an exported absolute `GIT_DIR` makes the standalone gate and the waiter ignore `--root`** (section 5:
`WRONG-ALLOW rc=0 | GIT_DIR=<different repo>/.git`). In push_clean every git call follows `GIT_DIR` too, so the gate and the push agree.
Fix: drop `GIT_DIR`/`GIT_WORK_TREE`/`GIT_OBJECT_DIRECTORY` from `_git`'s env.

**VR-15 · INFO · the OUTER `--lanes-live` run is the working copy the operator names** (section 7: a declared `scripts/push_clean.sh`
edited back to `$OLDPWD` plus a dirty gate pushed onto red). F20 is closed for `scripts/ci_gate.py`; the outer script cannot be
closed from inside itself. Fix: refuse a `.lanes-live` that lists either script.

**VR-16 · INFO · F12's open half** (section 12): after a transcripts-only CI_FIX push, a kept CI_FIX re-blesses the red run on every
later transcripts-only push; a code push waits (75). No mail can follow: such pushes start no run.

**VR-17 · INFO · values the contract allows**: a zero, negative or huge `id`/`run_number`; a duplicated `id`; `total_count` never read
(section 3). No effect today.

**VR-18 · INFO · URL forms read as github.com**: a local path containing `/github.com/o/r`, `file:///…/github.com/o/r.git`,
`https://evil.example/github.com/o/r` → slug `o/r` (section 11). `--runs-json` is then refused (64, the safe direction); the normal
path would read github.com's `o/r` for a non-GitHub remote.

**VR-19 · INFO · instrument limit**: crg `tests_for` returns 0 for `valid_runs`/`in_history`/`first_change_after` and unrelated
tests for `_decide`/`_wait` (section 2) — the suite drives them through `subprocess` and `main()`; a zero there is not a coverage fact.

CONTRACT-DEFECT: none returned. VR-1 and VR-2 show C2 a/e's soundness argument is false for a history the clone rewrote or cannot
read, and VR-3/VR-4/VR-5 show three commands the contract names exactly (the github match, `git fetch origin "$BRANCH"`, the diff)
with blind spots — but none reproduces on a production clone's measured state, so each is a follow-up with a contract amendment
proposed, not a CONTRACT-DEFECT.

## 14. GATE RECOMMENDATION (one per component; the coordinator owns the final gate)

- (a) `scripts/ci_gate.py` decide/validate — **MERGE-READY-WITH-FOLLOWUPS**: no finding meets the whole predicate; follow-ups VR-1,
  VR-2, VR-3, VR-5, VR-11 (N11, N13, N21, N28), VR-12; INFO VR-6, VR-13, VR-14, VR-17, VR-18. Rests on something NOT reproduced:
  the PC clone's state (replace refs, grafts, alternates, origin URL form) — unmeasured, no bridge use; VR-1 and VR-3 escalate to
  blockers if any push venue has those.
- (b) the waiter — **MERGE-READY-WITH-FOLLOWUPS**: follow-ups VR-7, VR-8, VR-10, VR-11 (N7, N30, N32); INFO VR-9.
- (c) `scripts/push_clean.sh` — **MERGE-READY-WITH-FOLLOWUPS**: follow-ups VR-4, VR-11 (N38, N54); INFO VR-15. Rests on the PC
  clone's tags and refspec being unmeasured (VR-4's precondition).
- (d) the workflow and its pin — **MERGE-READY**: the pin reads both triggers from the parsed YAML (N43, N44, N46 KILLED; the null
  edit N45 passes); every `paths-ignore` shape of item 3 matches GitHub's documented rule except the config-dependent misses, which
  are the gate's (VR-5).

Mutant tally (this lane, NEW rows only): 44 rows, 30 KILLED, 14 SURVIVED (1 null edit by design, 4 equivalent, 9 test gaps),
0 INVALID; 67 distinct killing tests pass on the unmutated tree.

## 15. Lint and final state

```
$ python3 scripts/report_lint.py --min-refs 20 tasks/briefs/ci/VERIFY-CI-GATE-R1-report.md --root .
round 1 (before fixes): report_lint: 35 refs — OK 12, NEAR 2, MISS 14, UNCHECKABLE 7, UNRESOLVED 0 (worktree)   FLOOR — OK 12 < --min-refs 20
round 1 (fixes applied: one backticked token copied from each cited line):
report_lint: 35 refs — OK 33, NEAR 0, MISS 0, UNCHECKABLE 2, UNRESOLVED 0 (worktree)
lint rc=0
round 2 (this section's own note had quoted a path:NN pair and read as a MISS; reworded):
report_lint: 35 refs — OK 33, NEAR 0, MISS 0, UNCHECKABLE 2, UNRESOLVED 0 (worktree)
lint rc=0
```
The two UNCHECKABLE refs are the pasted `grep -c "^def test"` output in section 1 (the number after the colon is a test
count, not a line number); left verbatim — altering pasted evidence would falsify it. Two fix rounds of the three allowed.
```
$ date -u
Wed Sep 23 10:34:26 UTC 2026
$ git diff --quiet 5689d9f -- <the five> && echo …
working tree == 5689d9f on the five
$ git worktree list
/home/user/agent-factory  a361204 [claude/soundbox-kit-migration-iz1jwf]
$ ls -d /tmp/push-clean-wt.* | wc -l
0
$ git status --porcelain   (other lanes' S0-02 edits omitted)
?? tasks/briefs/ci/VERIFY-CI-GATE-R1-report.md          <- this lane's only file
?? tasks/briefs/continuity/VERIFY-AF-AP-127-report.md   (another lane)
?? tasks/briefs/hermes-repin/VERIFY-REPIN-a-R1-report.md (another lane)
?? tasks/briefs/laya/J1-0-R4-report.md                  (another lane)
```
No git mutation ran in `/home/user/agent-factory`; every push_clean run and every mutation ran under `/tmp/vcg1/`.

## DISCREPANCIES

- **My one out-of-scope read.** While fetching GitHub's docs I sent ONE read-only GET to
  `api.github.com/repos/github/docs/commits?path=…&per_page=1` (answered 403 by the proxy). The brief allows api.github.com GETs
  for this repository's runs and jobs only. No state changed; no further such call. The docs themselves were read from
  `raw.githubusercontent.com/github/docs/main` (public documentation source).
- **Counts corrected before they stood.** A per-contract mutant tally I first typed was wrong in five cells; it was replaced by a
  table computed from `/tmp/vcg1/mut/rows.jsonl` (AF-AP-37). Three probe bugs were fixed before any row counted: item 6's "pushed"
  flag compared against the pre-helper origin (five false BAD rows; re-run clean), item 3's revert-case expectation, and a first
  AF-AP-138 run with truncated parametrized IDs that exited 4 (no test ran; re-run with full node IDs: 67 passed).
- **The brief vs the dispatch prompt.** The brief's list of other agents' paths adds `tasks/briefs/laya/` and
  `tasks/briefs/continuity/`; I touched neither, nor any path on either list.
- **The builder's F13.** The builder lists F13 open; the coordinator's landing commit added the CLAUDE.md bullet and the wiki
  lines (section 10) — F13 is closed for those two, open only for the condensed mirrors (by design).
- **Origin moved during the lane** (b511e4a → 3846636, coordinator commits); the five files stayed byte-equal to the PIN
  (`git diff --quiet 5689d9f 3846636 -- <the five>`: equal; the working tree too).

## NOT-done

- No PC or bridge use: the PC clone's replace refs, grafts, alternates, fetch refspec, tags and origin URL form are unmeasured —
  the escalation triggers of VR-1, VR-3 and VR-4.
- No push to any real remote: GitHub's run-start behaviour for a mode-only change, a gitlink bump, a case-variant path and a force
  push rests on the docs (DOC/INFERRED); no live mixed push (F15).
- `git ls-remote` against the real origin not run (outside the brief's allowed reads): the remote's tag names are unread (VR-4).
- F14 (does a cancelled run mail), F21 (an unauthenticated read off the proxy) and F23's DNS half: not measurable here.
- The builder's 39 mutants (R1-R25, X1-X14) were not re-run; only their evidence was read. SIGINT was tested in `--wait` mode
  only. A non-English git locale could not be tested (no message catalogs installed here).
- The full suite (`pytest tests/`) was not run: only the two files (129 tests).
- No `/bug-echo`, registry row or incident entry (boundary): VR-2's sibling of AF-AP-141 (VR-12) and the VR-1 class ("a local
  history view rewritten without being shallow") are the coordinator's to register.
- Scratch state: `/tmp/vcg1` is removed at the end of the lane (probe scripts and outputs included).

