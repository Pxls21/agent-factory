# VERIFY-REPIN-a — the targeted adversarial verify of the Hermes LANE-runtime pin entry

PIN: 905bb1d (origin; the REPIN-a landing). Component: `upstream.lock.yaml` (the appended `lane_runtime.hermes-agent-lane-runtime` section, lines 161-173), `tests/test_upstream_lock_lane_runtime.py` (8 tests), `docs/HARNESS-PORTS.md` §12. Contract (frozen): `tasks/briefs/hermes-repin/REPIN-brief.md` §REPIN-a + D-048 item 3 (`docs/08_DECISION_LOG.md`). The builder's report `tasks/briefs/hermes-repin/REPIN-a-report.md` is an input to attack.
ROLE: adversarial-verifier (sandbox, the D-054 pin); READ-ONLY on the tree (scratch copies only); never commit; no bridge use — the PC-side values are attacked by CONSISTENCY, not re-measured.
BOUNDARY (added at dispatch 2026-09-23): CREATE `tasks/briefs/hermes-repin/VERIFY-REPIN-a-report.md` (write it incrementally from the start); nothing else. Other sandbox agents work in this tree on disjoint files (`proofs/S0-05/`, `tests/test_s0_05_egress.py`, `tasks/briefs/s0-05-support/`, `tasks/briefs/s0-02-support/`): never touch, run or revert them. Never run `git stash`, `git checkout -- …`, `git restore`, `git add`, `git commit` or `git push`. No outward-facing action. Do NOT spawn subagents.
CODE INTEL FIRST: `graft ask` before any grep for code questions (item 4's second instrument stays a grep).
DISPATCH RULE: only after the J0-a probe lane has finished (no timing on a contended box).

## Items
1. Reproduce: the 8 tests twice; `bash scripts/verify-planning-repo.sh`; `python3 scripts/validate-ledger integrity --root .`; the S0-12 suite — paste.
2. The golden of `selected_core.hermes-agent`: does the test assert the LINES or a parsed dict? A whitespace-only edit of the existing entry (a scratch copy) — caught or not? Is that in contract (the brief says "byte-identical")?
3. The entry's key set: is it CLOSED (an extra key `foo:` in a scratch copy → red)? The 7-hex control — does a 39-hex or a 41-hex commit also fail by name? An uppercase hex?
4. Consumers (the builder claims none reads `lane_runtime`): verify with two instruments (graft `ask` + grep over scripts/, proofs/, tests/, harness-ports/, .github/) that the claim holds, and state plainly that the pin is UNENFORCED until REPIN-b; is `docs/HARNESS-PORTS.md` §12 honest about that (a hollow green in prose is a finding)?
5. Internal consistency of the recorded facts against the primary sources in the repo: D-043's row (527da60 vs b3399c1, 31,816 commits, 3939 files, SQLite versions), the `hermes-agent` entry's `observed_version: 0.21.0`, the incident-log entry for the 2026-09-08 `hermes update` — any contradiction is a finding.
6. The `verified:` field's count (43) — reproduce the builder's grep from its report; is the grep's shape sound (does it count ledger notes, or matches of words like HOME in unrelated lines)? If the count is not reproducible or the grep over-counts, the field is a finding (a typed number in disguise).
7. Report lint on the builder's report (paste).

## Output
`tasks/briefs/hermes-repin/VERIFY-REPIN-a-report.md`: observations with file:line + SOLID/UNSURE, the GATE RECOMMENDATION with the blocking predicate applied. `report_lint --min-refs 8` (≤ 3 rounds).

## PREMISE — MEASURED at dispatch (2026-09-23 08:14Z, sandbox @ ae16c6a; the brief was written 2026-09-22 before the measured-premise rule)

The component is byte-identical to the PIN: `upstream.lock.yaml` and the test file have no diff since 905bb1d; `docs/HARNESS-PORTS.md` gained three hunks ABOVE §12 (T92, PCJ1), so §12 moved from line 684 to line 728 with its text unchanged (same section sha). Item 1's count below is the floor; item 4's grep already reads empty outside the test (the `.pyc` is the test's own bytecode).

````
$ date -u
2026-09-23 08:14Z

$ git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf; git merge-base --is-ancestor 905bb1d HEAD; echo rc=$?
ae16c6a
rc=0

$ git diff --stat 905bb1d HEAD -- upstream.lock.yaml tests/test_upstream_lock_lane_runtime.py | wc -l
0

$ git diff 905bb1d HEAD -- docs/HARNESS-PORTS.md | grep ^@@   (the hunks since the PIN)
@@ -361,10 +361,21 @@ own git worktree, and leaves the final
@@ -384,6 +395,7 @@ starting a second one. Keyed on the STAT
@@ -442,6 +454,38 @@ restart-when-idle --max-wait 1800`, the

$ section 12 at the PIN vs HEAD (line of the heading; sha of the section text to EOF)
905bb1d heading-line=684 section-sha=d06447ac04c3ccd4
HEAD heading-line=728 section-sha=d06447ac04c3ccd4

$ grep -n lane_runtime -A13 upstream.lock.yaml | head -16
164:lane_runtime:
165-  hermes-agent-lane-runtime:
166-    commit: b3399c139624a0081d70397741a5b45f60fbe1f4
167-    version: "0.21.1"
168-    python: "3.11.15"
169-    sqlite: "3.53.1"
170-    role: "lane-runtime (scripts/pc_lane.sh -> hermes on the PC); NOT the S0-01 proof runtime"
171-    reason: "SQLite >= 3.51.3 for WAL on the shared profile state.db (VERIFY-B5j); owner-run hermes update 2026-09-08"
172-    diff_from_proof_pin: "31816 commits, 3939 files"
173-    verified: "harness-ports/tests/run-all.sh (sandbox) + 43 PC-lane HOME/LANDED notes since 2026-09-08 14:2xZ"

$ pytest tests/test_upstream_lock_lane_runtime.py (sandbox venv)
8 passed in 0.14s

$ bash scripts/pc_suite.sh set-id -- tests/test_upstream_lock_lane_runtime.py
1 files set=bbc177a039e2

$ grep -rln lane_runtime scripts proofs tests harness-ports .github   (readers outside the test)
tests/__pycache__/test_upstream_lock_lane_runtime.cpython-311-pytest-9.1.1.pyc
tests/test_upstream_lock_lane_runtime.py

$ ls tasks/briefs/hermes-repin/
REPIN-a-report.md
REPIN-brief.md
VERIFY-REPIN-a-brief.md

$ grep -c "J0-a SANDBOX LEG FILED" todo/BUILD-TASKLIST.md   (the dispatch rule: J0-a finished)
1
````
