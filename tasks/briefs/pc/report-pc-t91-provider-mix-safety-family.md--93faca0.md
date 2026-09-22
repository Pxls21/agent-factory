DONE: T91 proposal implemented and self-validated. This is not a gate verdict; sandbox adversarial verification still must grade it.

Changed:
- `harness-ports/bin/pc-lane.sh`
- `scripts/pc_lane.sh`
- `harness-ports/tests/test_pc_lane.sh`
- `harness-ports/tests/test_pc_lane_dispatcher.sh`
- `tasks/briefs/pc-t91-support/T91-report.md`

Report:
- `/home/rocco/agent-factory/.lanes/pc-t91-provider-mix-safety-family.md--93faca0/tree/tasks/briefs/pc-t91-support/T91-report.md`
- Draft copy updated at:
  `/home/rocco/agent-factory/.lanes/pc-t91-provider-mix-safety-family.md--93faca0/report-draft.md`

Verified:
- `bash -n` on both production scripts and both touched shell tests: rc 0.
- `git diff --check`: rc 0.
- `bash harness-ports/tests/test_pc_lane.sh` ×2:
  - `59 passed, 0 failed`
  - `59 passed, 0 failed`
- `bash harness-ports/tests/test_pc_lane_dispatcher.sh` ×2:
  - `pc_lane dispatcher: 24 passed, 0 failed`
  - `pc_lane dispatcher: 24 passed, 0 failed`
- `bash harness-ports/tests/run-all.sh`:
  - `ALL SUITES PASSED`
  - included `test_pc_lane.sh 59 passed, 0 failed`
  - included `test_pc_lane_dispatcher.sh pc_lane dispatcher: 24 passed, 0 failed`
- Mutants killed:
  - deleting `SAFETY_RX`: `54 passed, 5 failed`
  - dropping the safety regex anchor: `58 passed, 1 failed`
  - inverting provider-mix caveat condition: `pc_lane dispatcher: 22 passed, 2 failed`
- `report_lint`: `report_lint: 0 refs — OK 0, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (at 93faca0)`

Key outcomes:
- Safety-filter provider refusals now become `FAILED`, never `report.md`.
- Drafts on safety refusal now become `report.partial.md`, and the dispatcher fetches them as partial evidence.
- Provider mix is printed at harvest from read-only OmniRoute SQLite data.
- Provider mix is labeled per combo, not per lane.
- The tag→lane measurement showed no reliable lane key in `call_logs`; exact per-lane provider attribution remains NOT built.

Not done:
- No commit, push, PR, comment, service restart, or OmniRoute config change.
- No exact tag→lane attribution field added.
- Independent adversarial verification has not run.

🌱 graft saved ~17,303 tokens this turn.
