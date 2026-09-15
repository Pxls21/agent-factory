# Lane QM0 — `harness-ports/bin/qwen-server.sh`: the matrix's cell knobs, a side-effect-free `guard` that tells local-route lanes from cloud lanes, and the guard BEFORE every persistent write (AF-AP-79 closed with a byte-identity regression) — the prerequisite lane QM1 found missing (build lane: PC Hermes `code-implementer` on the CLOUD build route)

PIN: `PIN-PLACEHOLDER`

**Why (measured by lane QM1, `tasks/briefs/qwen-matrix-support/QM1-report.md`, in your tree).** The L1 matrix (`docs/research/findings/
RESEARCH-FINDINGS-1-VERIFIED.md` §4) needs server cells with `--cache-ram`, `-ctxcp`, `-cms`, a selectable `--spec-type`, `-ub` and
`--spec-draft-p-min`; the launcher renders none of them (its `argv()` ends in fixed MTP flags, S:57-68). Its live-lane refusal is inline in
`install()` and runs AFTER the unit is written, daemon-reloaded and enabled (S:145-157): under a live lane `install` mutates the persistent unit
text, then refuses the restart — the next unrelated restart applies it silently (AF-AP-79). And the refusal counts EVERY `.lanes/*/lane.pid`,
so a cloud-route lane that never touches the model server blocks its restart. Boundary: `harness-ports/bin/qwen-server.sh` (S),
`harness-ports/tests/test_qwen_server.sh` (T; today `45 passed, 0 failed` — every existing check stays green), `docs/HARNESS-PORTS.md` (the
qwen-server section), `PC-BRIDGE.md` (its qwen-builder lines), one quirk line in `CLAUDE.md` (the Environment section; the mirrors
`AGENTS.md`/`.hermes.md` are NOT yours — the pre-commit mirror gate is the coordinator's), the report
`tasks/briefs/qwen-matrix-support/QM0-report.md`. The pack is `tasks/briefs/qwen-matrix-support/QM1-pack.md` (the same files).

## Items (build in order; every item = code + a deterministic test in T + a pasted line)
1. **The six knobs, rendered by `argv()` and therefore into the unit text.** `QWEN_CACHE_RAM` (MiB; default 8192 = today's implicit server
   default, ALWAYS rendered as `--cache-ram N` so the unit text records it), `QWEN_CTXCP` (unset → no flag; set → `-ctxcp N`), `QWEN_CMS`
   (unset → no flag; set → `-cms N`), `QWEN_UBATCH` (unset → no flag; set → `-ub N`), `QWEN_SPEC_P_MIN` (unset → no flag; set →
   `--spec-draft-p-min X`), `QWEN_SPEC_TYPE` (default `draft-mtp` = today's argv byte-for-byte; `none` → neither `--spec-type` nor
   `--spec-draft-n-max`; `ngram-mod` → `--spec-type ngram-mod` and no `--spec-draft-n-max`; any other value → refused). Validation fails closed
   with a named line and rc 3 (the model-check rc): a non-positive or non-integer `QWEN_CACHE_RAM`/`QWEN_CTXCP`/`QWEN_CMS`/`QWEN_UBATCH`, a
   `QWEN_SPEC_P_MIN` outside [0,1], a `QWEN_SPEC_TYPE` outside `{draft-mtp, none, ngram-mod}` (the three the matrix uses; the binary's list is
   wider — say so in the docs, do not widen). Tests: the default argv is BYTE-IDENTICAL to the PIN's rendering except for the appended
   `--cache-ram 8192` (paste both hashes), each knob's presence and omission, each refusal with its exact message.
2. **`guard` — a side-effect-free subcommand.** Prints one line per live lane (`<pidfile> <pid> <route>`), where the route is read from
   `/proc/<pid>/environ`'s `HERMES_MODEL` (the dispatcher exports it; `tr '\0' '\n' < /proc/$pid/environ`): a value ending in `-local`, or an
   ABSENT/EMPTY value (the default route is local since 2026-09-14 — fail closed), is LOCAL; anything else is CLOUD. Exit 0 when no LOCAL lane
   is alive, 7 (the existing refusal rc) when one is; a dead pid in a pidfile is reported as `stale` and ignored. Tests: real child processes
   started under `env HERMES_MODEL=… sleep 300` (killed by pid in the trap) with pidfiles under a fake `QWEN_LANES_DIR` — a local lane → rc 7
   with its line, a cloud lane only → rc 0 with its line, no `HERMES_MODEL` → rc 7, a stale pidfile → rc 0 with `stale`; an unreadable
   `/proc/<pid>/environ` (a process of another user — simulate by pointing the reader at a non-existent pid dir) → LOCAL, fail closed.
3. **The guard BEFORE every persistent write (AF-AP-79).** `install` computes the candidate unit text, and if it differs from the installed
   text (or the unit is running and the argv changed) it calls the guard FIRST — before `unit > "$unit_path"`, before `daemon-reload`, before
   `enable`; on rc 7 it exits 7 with the guard's lines and NOTHING on disk or in systemd has changed. `start|stop|restart` and `uninstall` go
   through the guard too. The REGRESSION (the one AF-AP-79 names): with a live LOCAL lane and a changed candidate, `install` exits 7 AND the
   unit file's sha256 is unchanged AND the fake `systemctl`/`systemd-analyze` on PATH recorded ZERO calls (the harness already fakes the
   binary and the HF tree — add the fake systemctl the same way, recording argv lines to a file). With a live CLOUD lane only, `install`
   proceeds (the fake records `daemon-reload`, `enable --now`, `restart`). Paste both.
4. **Docs.** `docs/HARNESS-PORTS.md` (the knob table + `guard` + the before-write rule), `PC-BRIDGE.md` (the matrix restarts go through
   `guard`; a cloud lane never blocks the model server), one quirk line in `CLAUDE.md`'s Environment section: "`qwen-server.sh guard` before
   any model-server restart; cloud-route lanes do not block it; `install` writes nothing under a live local lane (AF-AP-79)".
5. **Gates.** `bash harness-ports/tests/test_qwen_server.sh` (paste the new `N passed, 0 failed`; N ≥ 45 + your checks), then
   `harness-ports/tests/run-all.sh` ONCE in one foreground call (`ALL SUITES PASSED`; ~2 min, under the 420 s cap), `bash -n`, and
   `shellcheck -S warning` on S if `shellcheck` exists on this host (say if it does not). Never run `install`, `restart` or `guard` against the
   REAL unit or the real `.lanes/` — the fake `QWEN_LANES_DIR` and fake PATH only; the live server is under a verify lane.
6. **Report** at `tasks/briefs/qwen-matrix-support/QM0-report.md`: FILE IDENTITY before/after, per item the pasted line, the two AF-AP-79
   pastes, DISCREPANCIES, NOT-done. Lint LAST: `python3 scripts/report_lint.py --map S=harness-ports/bin/qwen-server.sh
   --map T=harness-ports/tests/test_qwen_server.sh --min-refs 10 <report>`, at most THREE rounds, then paste and finish.
7. **Discipline.** Kill only what you start, by pid; no git writes; the model unit untouched.
