# BRIEF — review fixes 1: real CI, a fail-closed skill-sync gate, a hygienic hook-adapter test
PIN: (set at dispatch — scripts/pc_lane.sh refuses to run without a full SHA here)

You are the BUILD lane (Hermes on the PC, role code-implementer). The owner's reviewer found three
enforcement-layer defects; each is a verified seam below, with the contract that closes it. New
increment work is frozen until this lands. honey: ultra. `.hermes.md` carries the project rules.

> **AMENDED 2026-09-03 after lane round 1 halted (correctly) on this brief's own precondition:** it
> demanded a green harness baseline in a venue where the defects under repair make it red. The
> baseline is now RECORDED, not required: in the lane worktree (`.git` is a file) `run-all.sh`
> reports `2 SUITE(S) FAILED` — `test_hermes_hook_adapter.py` crashes with `NotADirectoryError`
> (blocker 3) and `test_pc_lane.sh` reports `21 passed, 8 failed` because the suite inherits the
> lane's own `LANE_ID` / `LANE_REPORT_DRAFT` from the environment (a FOURTH defect, deliverable 4;
> reproduced in the sandbox with `LANE_ID=leaked-from-parent bash harness-ports/tests/test_pc_lane.sh`).

FIRST ACTION (halt loud on any mismatch): `pwd && git rev-parse HEAD` equals the PIN, tree clean,
`$HOME/venv-agent-factory/bin/python -m pytest tests/ -q` → `74 passed`. RECORD the harness
baseline verbatim (`bash harness-ports/tests/run-all.sh` → expected `2 SUITE(S) FAILED`, with the
two failure shapes above — those are the defects, not a halt condition). Then confirm the seams:
`sed -n '105,111p' harness-ports/bin/sync-skills.sh` shows `comm … <(echo "$SRC_LIST") <(echo "$DST_LIST")`;
`sed -n '26p;79,89p' harness-ports/tests/test_hermes_hook_adapter.py` shows `tempfile.mkdtemp(prefix="hp-test-")`
never removed and `ROOT / ".git" / "turn-retro-acked"` unlinked at import time with no restore;
`cat .github/workflows/planning-checks.yml` runs only `scripts/verify-planning-repo.sh` on PRs and
pushes to `main` (so no workflow has ever run on this branch).

## Deliverables (boundary — touch ONLY these paths, tagged CREATE / MODIFY)
1. CREATE `.github/workflows/stage0-ci.yml` — `permissions: contents: read`; triggers `push`
   (all branches) and `pull_request`; `ubuntu-latest`, `actions/setup-python@v5` with 3.12; jobs:
   - `tests`: `python -m pip install pyflakes pytest "jsonschema==4.25.1" "rfc3339-validator==0.1.4"`
     (the pins EXACTLY as `scripts/setup.sh` line ~177), then `python -m pytest tests/ -q` and
     `python -m pyflakes scripts/validate-ledger scripts/proof-runner`.
   - `harness-suites`: `bash harness-ports/tests/run-all.sh` (needs git user config for its
     throwaway repos — set `git config --global user.email/user.name` in the job).
   - `ledger-integrity`: same pip pins, `python scripts/validate-ledger integrity` (exit 0 required).
   - `stage1-gate`: `continue-on-error: true`; `python scripts/validate-ledger stage1-gate | tee
     -a "$GITHUB_STEP_SUMMARY"`; the job is RED by design until Stage 1.
   - `planning`: `./scripts/verify-planning-repo.sh`.
   Leave `planning-checks.yml` in place (it guards `main`). CREATE `tests/test_stage0_ci_workflow.py`:
   the YAML parses (JSON-syntax-agnostic: use a minimal parser — PyYAML is NOT declared; if you
   need it, parse the workflow with `python -c` + `yaml` ONLY inside CI where `pip install pyyaml`
   is added to that job, and in the test assert structure by line-anchored regexes instead), the
   five job names exist, `stage1-gate` carries `continue-on-error: true`, the pip line equals the
   setup.sh pins, triggers include push + pull_request, `permissions: contents: read`.
2. MODIFY `harness-ports/bin/sync-skills.sh` — fail CLOSED: write the two lists to `mktemp` files
   (trap-cleaned), run each `comm` with its exit status checked (`|| { echo "sync-skills:
   comparison failed (comm rc=$?)" >&2; exit 65; }`), and never print "in sync" unless every
   comparison ran; `--check` keeps exit 1 on drift. MODIFY `harness-ports/tests/test_sync_skills.sh`:
   NEGATIVE CONTROL — a `PATH` whose first `comm` is a stub that exits 3 ⇒ the script exits 65
   with the failure line and WITHOUT "in sync"; positive controls unchanged (19 existing checks).
3. MODIFY `harness-ports/tests/test_hermes_hook_adapter.py` — (a) resolve the sentinel through
   `git rev-parse --git-common-dir` (works when `.git` is a file in a linked worktree); (b) save
   the sentinel's bytes (or its absence) at start and RESTORE them in a `finally`/`atexit` path
   that runs even when a check fails; (c) every temp dir via `tempfile.TemporaryDirectory` or
   removed in `finally`; (d) audit every other filesystem write/delete in the file (e.g. the
   `_LIVE_STATE.unlink` near line 144) — each is under a temp root or saved-and-restored.
   Prove order-independence: `bash harness-ports/tests/run-all.sh` twice, then the hook-adapter
   test alone AFTER `test_pc_lane.sh` and BEFORE it — identical results; `git status --short`
   empty after every run; `ls /tmp | grep -c hp-test-` unchanged before/after.

4. MODIFY `harness-ports/tests/test_pc_lane.sh` — hermetic against the caller's environment:
   `unset LANE_ID LANE_REPORT_DRAFT TERMINAL_CWD HERMES_MODEL HERMES_REASONING` at the top (the
   suite sets what it needs itself), and add a ROBUSTNESS CONTROL that re-runs one lane test with
   `LANE_ID=leaked-from-parent LANE_REPORT_DRAFT=/tmp/x` exported in the parent and asserts the
   lane still gets its own id and draft path. Root cause: `pc-lane.sh` honours an inherited
   `LANE_ID` (by design — the sandbox launcher sets it), so a suite run INSIDE a lane collided every
   test lane onto the parent's id and the replay guard re-printed the first report.

## Contract (the verifier grades against THIS list)
C1 `stage0-ci.yml` parses; five jobs; `stage1-gate` has `continue-on-error: true`; pins equal
   setup.sh; triggers push + pull_request; `permissions: contents: read` (test file proves each).
C2 Every job's commands run green LOCALLY in a clean shell (`env -i PATH=/usr/bin:/bin:$HOME/venv-agent-factory/bin
   HOME=$HOME bash -lc '<cmd>'`), except `stage1-gate` which exits 2 as designed — paste each.
C3 `sync-skills.sh` with a failing `comm` on PATH ⇒ exit 65, stderr names the failure, stdout has
   no "in sync"; with the real `comm` ⇒ unchanged behaviour; `--check` exit 1 on an injected drift.
C4 Hook-adapter test: passes in the lane worktree (`.git` is a FILE here — the crash the reviewer
   saw), restores the sentinel byte-for-byte, leaves no `hp-test-*` dir, `git status` clean.
C5 Order-independence per deliverable 3 (both orders, twice each) — paste the summaries.
C6 Full suites AFTER the fixes, in the lane worktree: `$HOME/venv-agent-factory/bin/python -m pytest
   tests/ -q` green twice (counts verbatim); `bash harness-ports/tests/run-all.sh` ALL SUITES PASSED
   twice — the recorded red baseline turned green by deliverables 3 and 4 (say so).
C7 Named mutants killed: sync-skills without the exit-65 path ⇒ the negative control reds; the
   hook-adapter test without the restore ⇒ a sentinel-diff check reds (add that check).
C8 Hooks pass on commit; only the boundary touched; no secret or bridge link in any file.

## Non-negotiables
No stubs in committed code; no test skipped or weakened; no subagents; no outward actions; never
sudo/install on the PC; do not load skills (the role text and this brief carry every rule). Commit
per green deliverable with a reasoning-record message. Deviation = STOP and report. Append each
finished section to `$LANE_REPORT_DRAFT`.

## Report (DATA, ≤ 60 lines)
files:lines · the literal invocations with counts · C1–C8 decisive lines · mutants · discrepancies ·
NOT-done · adjacent defects (file:line).
