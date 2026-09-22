# REPIN — the FORMAL repin of the Hermes LANE runtime (D-043 → D-048 option (b))

STATUS: AUTHORED 2026-09-22 17:0xZ; two increments, the second serialized behind T90-R2 (same file, `scripts/pc_lane.sh`).

## Why (measured facts, 2026-09-22 14:xxZ, pasted from the D-043 row)
- S0-01's proof runtime = the pinned `/home/rocco/s0-01-pinned/hermes-agent` at `527da60` (0.21.0; venv python 3.13.11; SQLite 3.47.2) — UNCHANGED by this increment.
- The LANE runtime = `~/.local/bin/hermes` → `/home/rocco/.hermes/hermes-agent/venv/bin/hermes` at `b3399c1` (0.21.1; python 3.11.15; SQLite 3.53.1; committed 2026-09-08 14:05:24Z); the pin is an ancestor: 31,816 commits, `3939 files changed, 535669 insertions(+), 785641 deletions(-)`; `transform_terminal_output` present in both trees; the shared `state.db` in WAL.
- The lanes left the pin on 2026-09-08 when the owner ran `hermes update` to escape the SQLite 3.47.2 WAL-reset bug (`session_persistence_failed`, VERIFY-B5j) — option (a) "point the lanes back at the pinned venv" would reintroduce it; REJECTED (D-048).
- D-043: an installed runtime is never legitimized by being installed — hence a FORMAL pin with its evidence, not a shrug.

## REPIN-a (sandbox; agent `code-implementer`; boundary exact)
- `upstream.lock.yaml`: a NEW entry `hermes-agent-lane-runtime` beside the existing hermes entry (never editing it): `commit: b3399c139624a0081d70397741a5b45f60fbe1f4` (MEASURED over the bridge 2026-09-22 17:0xZ: `git -C /home/rocco/.hermes/hermes-agent rev-parse HEAD` → `b3399c139624a0081d70397741a5b45f60fbe1f4`, committed `2026-09-08T14:05:24Z`; `hermes --version` → `Hermes Agent v0.21.1 (2026.9.7) · upstream b3399c13`; venv python `3.11.15`, sqlite `3.53.1`; the proof runtime `git -C /home/rocco/s0-01-pinned/hermes-agent rev-parse --short HEAD` → `527da60`), `version: 0.21.1`, `python: 3.11.15`, `sqlite: 3.53.1`, `role: lane-runtime (scripts/pc_lane.sh → hermes on the PC); NOT the S0-01 proof runtime`, `reason: SQLite ≥ 3.51.3 for WAL on the shared profile state.db (VERIFY-B5j); owner-run hermes update 2026-09-08`, `diff_from_proof_pin: 31816 commits, 3939 files`, `verified: harness-ports/tests/run-all.sh (sandbox) + the lanes' record since 2026-09-08 14:2xZ` — count it by DATE, not by header grep (only 1 of the 37 `tasks/briefs/pc/report-*.md` files names the runtime, measured): the number of `HOME`/`LANDED` ledger notes in `todo/BUILD-TASKLIST.md` stamped on or after 2026-09-08 14:2xZ whose lane ran on the PC (paste the grep and its count).
- `tests/test_upstream_lock_lane_runtime.py`: the entry exists with exactly those keys; `commit` is 40 hex; the S0-01 hermes entry is byte-identical to its committed value (a golden of that entry's lines); the negative control: an entry with a 7-hex commit → red by name.
- `docs/HARNESS-PORTS.md`: a short §"Lane runtime pin" (what the pin covers, what it does not — the S0-01 proof runtime — and the drift check REPIN-b adds).
- Gates: the test twice; `python3 scripts/verify-planning-repo.sh` (the planning docs' own check); pyflakes; the report `tasks/briefs/hermes-repin/REPIN-a-report.md` (DATA).

## REPIN-b (the drift check in the dispatcher — AFTER T90-R2 lands; PC lane or sandbox)
- `scripts/pc_lane.sh` preflight: read the pinned commit from `upstream.lock.yaml` (the `hermes-agent-lane-runtime` entry) and compare it with the PC's `git -C ~/.hermes/hermes-agent rev-parse HEAD` in the same bridge probe that already reads the lane state; a mismatch REFUSES the launch with `lane-runtime-drift: <pc-sha> != <pin>` (rc 64) — never a warning; the resume path is exempt only for a lane that already started on the pinned sha (record the sha in `lane.meta` at launch and compare on resume).
- `harness-ports/tests/test_pc_lane_dispatcher.sh`: the fake bridge returns a mismatching sha → rc 64 with the exact line; matching → the launch proceeds; a lane.meta with the pinned sha + a drifted PC → resume refused by name.
- Mutants: m1 drop the comparison → red; m2 compare a 7-hex prefix → the near-miss fixture red.

## NOT this increment's
Re-auditing 31,816 commits by reading; regenerating S0-01's evidence (its runtime is the untouched pin); any `hermes update`.
