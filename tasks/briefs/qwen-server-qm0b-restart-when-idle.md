# Lane QM0-b — `qwen-server.sh restart-when-idle`: a deferred, PC-side restart that applies a pending unit change only once every piece of work the local server is used for has finished (no local-route lane alive, no request in flight, no matrix cell running), and the dispatcher queues local lanes behind it instead of failing (build lane: PC Hermes `code-implementer`; dispatched on QM0's landing — same file)

PIN: `efde78d` (QM0 lands first: the six knobs, the route-aware `guard`, the guard before every persistent write; this
lane builds ON those bytes — re-derive `harness-ports/bin/qwen-server.sh`'s sha256 + line count at the PIN and paste them).

**Why (owner ask 2026-09-15 13:2xZ: "is there a way where you can script it where the server restarts when all the current work it's
used for is done").** Today a unit change (the effort switch to `medium` for a build lane, a matrix cell's flags) needs a restart of
`qwen-builder`; the restart kills any lane running ON the local model and any interactive turn in flight, so it is refused while work is
live — and then nobody applies it later. The deferred restart makes "later" mechanical: the change waits, watches, applies itself the moment
the server is idle and no local-route lane holds it, and logs what it did. Boundary: `harness-ports/bin/qwen-server.sh` (S),
`harness-ports/tests/test_qwen_server.sh` (T), `scripts/pc_lane.sh` (D, its step 1c only), `harness-ports/tests/test_pc_lane_dispatcher.sh`
(or the test that covers step 1c — find it), `docs/HARNESS-PORTS.md`, `PC-BRIDGE.md`, one quirk line in `CLAUDE.md` (mirrors are not
yours), the report `tasks/briefs/qwen-matrix-support/QM0b-report.md`.

## Items (every item = code + a deterministic test + a pasted line)
1. **`restart-when-idle [--max-wait S] [--poll S]`** with the target `QWEN_*` env in the environment. It renders the candidate unit; if
   it is byte-identical to the installed unit AND `health` passes → prints `already applied` and exits 0 (nothing started). Otherwise it writes
   the env snapshot to `~/qwen-builder/pending/env` (atomically: temp + rename; a newer call REPLACES it), starts ONE detached watcher
   (`setsid`, pid in `~/qwen-builder/pending/watcher.pid`; a second call while a watcher runs replaces the env and does not start a second
   watcher — the watcher re-reads the env every poll), and returns 0 with `pending: watcher <pid>`. The unit file is NOT written at this point
   (AF-AP-79: nothing persistent changes until the apply).
2. **The watcher loop** (default poll 30 s, default max-wait 8 h): applies only when ALL hold on the same poll — (a) `guard` rc 0 (no
   LOCAL-route lane alive; cloud lanes are ignored by construction), (b) idle: the server's `/metrics` `llamacpp:requests_processing` is 0 on
   TWO consecutive polls (an interactive turn counts as busy; read the exact metric name from the live `/metrics` and pin it in a fixture),
   (c) no matrix cell lock (`~/qwen-builder/matrix/.cell.lock` absent — the cell runner will create it; define the path here). Then it runs
   `install` with the pending env (QM0's install: guard first, then the write and the restart), waits for `health`, appends
   `applied <utc> env-sha=<12> argv-sha=<12>` to `~/qwen-builder/logs/deferred-restart.log`, removes the pending env and its own pidfile, exits 0.
   `--max-wait` elapsed → appends `expired <utc> blocked-by=<the last reason>` and exits 75 with the env left in place (never silent). An
   install failure → `failed <utc> rc=<n>` and exit n. Each poll that waits logs its blocking reason once per reason change
   (`waiting: local lane <pidfile>` / `waiting: busy` / `waiting: matrix cell`), never a line per poll.
3. **`status`** gains a `pending restart:` line (env sha, since, watcher pid alive/dead, the last blocking reason) and `none` otherwise.
4. **The dispatcher (`scripts/pc_lane.sh` step 1c).** When the lane's route is local and the server's running effort (read from
   `/props`'s alias? no — from `systemctl --user cat`'s ExecStart `reasoning_effort` value vs the running process argv; use the running
   argv) differs from the lane's, the dispatcher calls `QWEN_EFFORT=<role effort> qwen-server.sh restart-when-idle --max-wait 1800` and
   then WAITS in the foreground (polling the log for `applied`/`expired`/`failed` on this env sha) before launching the lane: a lane
   must never start against the wrong effort. `applied` → launch; `expired` → die with the blocking reason (the coordinator decides);
   `failed` → die with rc. In the common case (no local lane alive, server idle) this is one poll. Cloud-route lanes skip the step
   entirely (as today).
5. **Tests.** T: a fake `systemctl`/`systemd-analyze` on PATH (QM0's harness), a fake `/metrics` (a stub `curl` on PATH returning a
   fixture, or a tiny `python3 -m http.server` handler under the test's control) and fake lane pidfiles with real `sleep` children carrying
   `HERMES_MODEL` — the eight combinations of (local lane alive, busy, cell lock) with `--poll 1`: only (no, no, no) applies; the two-consecutive-
   idle rule (busy-then-idle-once must NOT apply); a newer pending env replaces the older with ONE watcher pid; `--max-wait 3` → rc 75, the
   log line, the env still present; a failing fake install → rc propagated and logged; `already applied` when the unit is unchanged; the
   unit file's sha256 unchanged for the whole waiting period (AF-AP-79); `status` lines in every state. D: the dispatcher's step 1c under a
   fake `qwen-server.sh` that records `restart-when-idle` calls and writes `applied`/`expired` to the log on cue — launch after `applied`,
   die on `expired` with the reason, skip on a cloud route. Keep every existing check green; paste `run-all.sh` → `ALL SUITES PASSED`.
6. **Docs + report** (`QM0b-report.md`, the same shape as QM0's; lint `--map S=… --map D=scripts/pc_lane.sh --min-refs 10`, three rounds).
7. **Discipline.** NEVER run `restart-when-idle`, `install` or `restart` against the real unit or the real `.lanes/` in this lane; the live
   server is under lanes; fakes only; kill your `sleep` children by pid; no git writes.
