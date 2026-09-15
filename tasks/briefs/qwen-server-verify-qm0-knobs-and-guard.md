# VERIFY-QM0 — adversarial verification of the qwen-server matrix knobs and the pre-write lane guard as LANDED (8aecbf8, in the PIN), graded against the launcher's CONTRACT (PC-BRIDGE.md §qwen-builder, `docs/HARNESS-PORTS.md` §qwen-server, D-030 the ownership contract, AF-AP-79 the guard-before-write rule), never against the builder's own cases (verify lane: PC Hermes `adversarial-verifier` on the CLOUD verify route — the SINGLE-MODEL RULE applies: the builder ran on the same cloud model, so you return FINDINGS, no gate verdict; sandbox fallback Opus 5 `adversarial-verifier`)

PIN: `efde78d`

**What you grade.** `harness-ports/bin/qwen-server.sh` (S, 302 lines at the PIN), `harness-ports/tests/test_qwen_server.sh` (T, 357 lines),
`docs/HARNESS-PORTS.md` (H) and `PC-BRIDGE.md` (P) as landed; the builder's report `tasks/briefs/qwen-matrix-support/QM0-report.md` (its own
lint after the bounded rounds: `46 refs — OK 20, NEAR 12, MISS 14` — re-anchor its load-bearing refs yourself; the coordinator found its
FILE IDENTITY row for H STALE: the doc was edited after hashing, the landed bytes are the lane tree's). D-030 (`docs/08_DECISION_LOG.md`)
settles the seam the lane escalated: ANY live PID named by a `.lanes/*/lane.pid` blocks; the route is `HERMES_MODEL` from that process's
environment; absent/unreadable = LOCAL; a dead pidfile is `stale` and does not block; PID reuse = a false REFUSAL at worst. Grade the code
against D-030, not against the lane's reversed heuristic. The coordinator's gates: sandbox `qwen-server: 79 passed, 0 failed` (= the PC ×2),
`harness-ports/tests/run-all.sh` ALL SUITES PASSED; the lane's `0 passed, 9 failed` dispatcher suite reproduced on NEITHER venue (`9 passed`
on the PC clone at 5a31ac8 and in the sandbox) — a lane-environment artifact, not yours to chase beyond one reproduction.

**NEVER on this venue:** run `install`, `start`, `stop`, `restart` or `uninstall` against the REAL unit (`qwen-builder` serves VERIFY-GOV1 on
the local slot); every lifecycle probe runs with `QWEN_LANES_DIR`, `UNIT_PATH`/the unit path variable, `XDG_RUNTIME_DIR` and the systemctl
sink pointed at YOUR scratch (read T for the fake-sink seams and reuse them). `guard` (read-only) may run against the real `.lanes/` — it must
print the live lanes and rc 7 while any local-route lane is alive (VERIFY-GOV1 is: expect rc 7 and its pidfile named).

## Items (every item = a reproduced probe with its exact command, output and file:line)
- **V1 — the guard against D-030, behaviorally.** Fake lanes under a scratch `QWEN_LANES_DIR`: a live child with `HERMES_MODEL=agentfactory-build-local`
  (LOCAL → rc 7), with `HERMES_MODEL=agentfactory-build` (CLOUD → rc 0), with NO `HERMES_MODEL` (LOCAL, fail-closed → rc 7), a pidfile naming a
  DEAD pid (stale, rc 0), a pidfile naming a live pid whose `/proc/<pid>/environ` is UNREADABLE (a process of another uid, e.g. pid 1: LOCAL →
  rc 7), an EMPTY pidfile, a pidfile with garbage, a pidfile naming the guard's OWN shell. Paste each line the guard prints (`pidfile pid route`).
  A `lane.pid` whose process is a zombie: live or dead? State what `kill -0` returns and what the guard does.
- **V2 — the guard before EVERY effect (AF-AP-79).** For each of `install` (changed unit), `start`, `stop`, `restart`, `uninstall`: with a LOCAL
  fake lane alive, the unit bytes BEFORE == AFTER, the systemctl sink log EMPTY, no key/config/log path created, rc 7 with the exact message
  (`S:224-251`, `S:276-301`). Then the ORDER: does `install` VALIDATE the knobs before or after the guard? The brief wanted the guard before the
  write — is the guard also before the render/compare (a render of an invalid knob set must not be needed to refuse)? Find the first
  side-effecting statement in each path and cite it.
- **V3 — the identical-unit no-op.** An unchanged candidate unit returns rc 0 WITHOUT the guard, without writing, without systemd (`S:224-251`).
  Attack: is "identical" decided on the RENDERED bytes or on a hash of inputs? Change ONLY the env in a way that renders the same bytes
  (e.g. `QWEN_SPEC_TYPE=draft-mtp` explicit vs default) — still a no-op? Change whitespace in the unit file on disk by hand — a changed candidate
  now (a restart under a live lane would be refused — good) or a no-op (a hand-edited unit silently kept)?
- **V4 — the knob domains (tactic 8).** `validate_knobs()` (`S:66-89`): for each knob, the boundary values: 0, negative, `1.5` for an integer,
  `1e3`, hex, leading `+`, empty string vs unset, `p-min` = 0, 1, `-0.0`, `nan`, `inf`, `1.0000001`; `QWEN_SPEC_TYPE` = `draft-mtp `(trailing space),
  `DRAFT-MTP`, `ngram-mod` with `QWEN_MTP_N` unset vs set. Paste the rc and message for each; every non-domain value must be rc 3 BEFORE any
  effect. NaN through `[[ … ]]` arithmetic is the AF wormhole class — prove it is refused.
- **V5 — the argv contract.** The 34-token PIN fixture byte-compared after stripping `--cache-ram 8192` (`T:77-119`): reproduce; then render
  each speculation shape (`draft-mtp` with n=3, `none`, `ngram-mod`) and paste the argv; confirm `none` emits NO speculation tokens and
  `ngram-mod` NO MTP depth; confirm every optional knob is absent from argv when unset (no empty `-ctxcp ""`).
- **V6 — the tests' oracles.** T's fake `systemctl` sink and fake `curl` (`T:322-326`, the AF-AP-33 hit the lane classified): do the tests ever
  read a value the fake produced as if the real server produced it? The AF-AP-79 byte invariant (`T:304-321`): which bytes — the unit file
  only, or also the key file, the config dir, the log? Add a scratch mutant that writes the KEY file before the guard: does any test go red?
- **V7 — the docs against the code.** H:397-409 and P:170-177 claim the command surface, the default cell, the six knobs and domains, the
  stale-pid rule, the no-op rule: check every claim against S line by line; list every doc claim the code does not make true.
- **V8 — the driver-free claim.** The lane killed four SCRATCH mutations (fixed cache RAM, local→cloud route, absent-route fail-open, the
  install guard removed) with no committed driver. Reproduce all four from the report's descriptions as scratch edits on a copy of S and run T:
  paste the failing assertion of each. Then two of your own (the stale-pid rule inverted; the `uninstall` guard removed).
- **V9 — the report.** Re-verify the FILE IDENTITY rows (S, T, P; H is known stale — say what its true sha at the PIN is); run
  `report_lint.py --map S=harness-ports/bin/qwen-server.sh --map T=harness-ports/tests/test_qwen_server.sh --map H=docs/HARNESS-PORTS.md --map P=PC-BRIDGE.md`
  and re-anchor the 14 MISS refs; grade every VERIFIED claim you can reproduce in ≤ 5 min; UNSURE for the rest, never false.

**Output.** `tasks/briefs/qwen-matrix-support/VERIFY-QM0-report.md`: line 1 `NO VERDICT (single-model rule): findings only`; FINDINGS first,
ranked by severity with the fix shape (a finding that a restart could reach a live lane is BLOCKING and goes first); then per item
SOLID/UNSURE with the command, the output and `file:line` (`S=`, `T=`, `H=`, `P=`; declare the map at the top); a NOT-done list. Report lint
with your map, `--min-refs 15`, the bounded rule (three rounds, then paste and finish). No edits to the landed bytes (scratch copies only);
NEVER a real lifecycle command.
