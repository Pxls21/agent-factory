# VERIFY-T243-245: the independent verify of three coordinator tooling changes (tasks #243, #245; AF-AP-200)

Role: adversarial-verifier (sandbox, Opus 5.5). PIN: the content of the files hashed below (commits "push_clean: refuse a
push whose added notes cite a commit id the push rewrote", "stale_ids: the diff parser no longer fails open ...",
"ap_screen: --staged-shell, the pre-commit hook's advisory screen over staged *.sh files", "registry: AF-AP-200 ...";
all GATED-PENDING-VERIFY). Report: `tasks/briefs/jev-laya/VERIFY-T243-245-report.md` (write it incrementally from the
start). Cite commits by subject: the push rewrites their ids.

The coordinator built these while another verifier ran. Rule 0f: the coordinator's own gate runs are not independent
verification. Attack each change against its contract with NEW shapes, never only its own tests. Report every
meaningful observation with no severity filter, then apply the blocking predicate (contract-mapped, reproduced through
the real script, materially effective, a concrete discriminator, in-boundary) and give ONE gate recommendation per
change: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID.

## The contracts

A. `scripts/stale_ids.py` + its call in `scripts/push_clean.sh` (task #243). push_clean rewrites every range commit that
carries a model-identifier trailer, and every commit after it.
1. A push whose NET added lines (`git diff <origin-ref> <head>`) cite a commit that this push's rewrite replaced (a hex
   token of 7-40 characters with non-alphanumeric boundaries that prefixes the old id) is refused, exit 4, with nothing
   pushed, naming file:line, the old token and the new id at the same length.
2. `STALE_ID_OK=<reason>` pushes anyway and says so.
3. A citation of a commit that was not rewritten (on origin already, or kept byte for byte) never refuses.
4. A commit MESSAGE citation warns only.
5. A range it cannot map, or a git failure, refuses (non-zero; never a silent pass).
6. After a refusal, the note corrected to the new id pushes (the rewritten commits keep their new ids on the next run).
7. The same holds in `--lanes-live` mode (the inner run is the detached worktree's committed push_clean.sh).
8. The diff's shape cannot hide a citation: a config (`diff.noprefix`, `diff.mnemonicPrefix`, `color.ui=always`,
   `diff.external`, `diff.relative`, ...), a quoted path, a rename, a binary file, an added line starting `++ `.

B. `scripts/ap_screen.py --staged-shell` + its line in `scripts/hooks/pre-commit` (task #245).
1. Every staged (added, copied, modified or renamed) `*.sh` file outside `sandbox-kit/` and `.claude/` is screened with
   AP_SCREEN at commit, and its hits are printed.
2. Silent when there is no hit; never blocks a commit (the hook runs it with `|| true`).
3. Unstaged changes and untracked files are not screened.

C. The AF-AP-200 row in `.claude/hooks/edit-snapshot.py` AP_SCREEN: fires on a diff header parsed by its prefix
(`startswith("+++` / `startswith("--- a/`), not on front matter (`startswith("---")`) or a single `+`.

## Suspicions (not a limit)

- A: a path with a newline or a tab; a file deleted in the range that held a citation; a citation in a file renamed in
  the range; the full 40-character id; an id inside a URL (`.../commit/<id>`); a range of hundreds of commits (the
  token-by-id loop); an origin ref that moved during the run; a message citation of the commit's own old id; the
  refusal leaving the LOCAL branch rewritten in `--no-delegates-live` mode (is the next run's rewrite a no-op, so the
  reported new id stays true?); the temp file of old ids leaking on each exit path; `set -euo pipefail` interplay.
- B: a staged symlink `*.sh`; a file named `x.sh` in a directory `sandbox-kit-other/`; a `.sh` staged for deletion; a
  path with a space or non-ASCII (quoted by git without `-z`?); the hook run from a subdirectory; `$PY` without the
  hook's modules; an exception inside ap_screen (does a traceback print, does the commit still go?).
- C: a false-positive rate over the repo's first-party code (`python3 scripts/ap_screen.py scripts proofs harness-ports`).

## Evidence rules

Reproduce every claim through the real scripts. Use throwaway git repos with a bare origin under your scratch dir (the
committed tests show the harness: `tests/test_stale_ids.py`, `tests/test_ap_screen.py`); a green CI record for push_clean
is the `CI_GATE_RUNS_JSON` test input. Mutants on scratch copies ONLY, one fresh copy per mutant. NEVER run push_clean,
a commit or any git write in `/home/user/agent-factory` itself: its branch is shared and live. Use a short `--basetemp`
(make the parent first). Kill by pid only.

## Standing rules

No outward actions (no commits, pushes, PRs, comments, GitHub writes, bridge calls). Do not spawn subagents. Never
create or remove `.jev/intercept-off` (the JT3 search hook is live: a semantic Grep may be answered by it; repeat the
identical call within 120 s for the raw result). Another verifier is working on `scripts/gpu_window.sh`: do not touch
it or its tests. FAKE strings only for anything secret-shaped (the model-identifier trailer in a fixture is built
from parts, as the tests do). Check every file you write with `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` (0 expected).

## PREMISE — MEASURED at authoring (2026-09-24 21:38Z, /home/user/agent-factory at local HEAD)

```
$ for f in scripts/stale_ids.py scripts/push_clean.sh tests/test_stale_ids.py scripts/ap_screen.py scripts/hooks/pre-commit tests/test_ap_screen.py .claude/hooks/edit-snapshot.py tests/test_edit_snapshot_ap_screen.py; do echo "$(git rev-parse --short=12 HEAD:$f) $f"; done
0d2a66ea9009 scripts/stale_ids.py
b3f0faeeaa81 scripts/push_clean.sh
38c9e4298dbe tests/test_stale_ids.py
fb10f06b680b scripts/ap_screen.py
ddcf5707a3fc scripts/hooks/pre-commit
bcfac0093ba7 tests/test_ap_screen.py
fd6d5d54a3df .claude/hooks/edit-snapshot.py
bc4e48d7d29f tests/test_edit_snapshot_ap_screen.py
$ bash scripts/test_summary.sh tests/test_stale_ids.py   (twice)
pytest-summary: 9 passed in 3.79s
pytest-summary: 9 passed in 3.66s
$ bash scripts/pc_suite.sh set-id -- tests/test_stale_ids.py
1 files set=89acd12051d2
$ bash scripts/test_summary.sh tests/test_edit_snapshot_ap_screen.py tests/test_ap_screen.py   (twice)
pytest-summary: 194 passed in 0.59s
pytest-summary: 194 passed in 0.49s
$ bash scripts/pc_suite.sh set-id -- tests/test_ap_screen.py tests/test_edit_snapshot_ap_screen.py
2 files set=62551bca597a
```
