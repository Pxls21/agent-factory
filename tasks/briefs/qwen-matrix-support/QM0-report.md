# QM0 report — qwen-server matrix knobs and pre-write lane guard

## Outcome

PROPOSAL — QM0 items 1–4 and documentation are implemented at PIN `7537910`, but acceptance is blocked on an ownership-seam conclusion that this lane reversed. Current bytes passed the focused archive-copy suite twice at `qwen-server: 79 passed, 0 failed`; four hostile mutations died for their exact intended reasons. Those results do not settle whether a live PID named by `lane.pid` is sufficient identity. This build lane does not issue a gate verdict. The coordinator and sandbox-side adversarial verifier must resolve that contract before acceptance.

## NOT done

- The PID-reuse ownership seam is unresolved after a conclusion reversal; current code trusts any live PID named by a lane `lane.pid`. Acceptance must not proceed until the coordinator/verifier decides whether that is the intended ownership contract.
- No real `qwen-builder` `install`, `start`, `stop`, `restart`, or `uninstall` command ran. The live server and real lane tree were untouched.
- No live matrix/load run occurred. QM1 remains the consumer increment after independent acceptance and landing of this proposal.
- The aggregate harness suite did not print `ALL SUITES PASSED`: one unrelated dispatcher suite failed identically on the PIN and proposal, detailed under Discrepancies.
- ShellCheck did not run because it is unavailable on this host. Pyflakes is not installed and is not applicable to the changed shell/Markdown files.
- No commit, push, PR, service restart, or outward-facing action occurred.

## Premise audit

- VERIFIED at PIN: the launcher had no six matrix knobs and exposed no `guard`; its fixed argv ended at MTP settings, while `install()` wrote the unit and called systemd before its inline lane refusal. This reproduced QM1's blocker.
- VERIFIED pinned public contract: default `argv` had 34 tokens before this change. The new test embeds that fixture and strips only `--cache-ram 8192` before a byte comparison (`T:77`–`T:119`).
- VERIFIED baseline focused suite before edits: `qwen-server: 45 passed, 0 failed`.

## Item 1 — six matrix-cell knobs

- Added `QWEN_CACHE_RAM=8192` and optional `QWEN_CTXCP`, `QWEN_CMS`, `QWEN_UBATCH`, and `QWEN_SPEC_P_MIN`; made `QWEN_SPEC_TYPE` explicit with default `draft-mtp` (`S:43`–`S:48`).
- `argv()` now renders `--cache-ram`, optional `-ctxcp`, `-cms`, `-ub`, optional `--spec-draft-p-min`, and exactly one allowed speculation shape (`S:92`–`S:113`). `none` emits no speculation tokens; `ngram-mod` emits no MTP depth.
- `validate_knobs()` fails closed with rc 3: positive integers for cache/checkpoint/miss/ubatch; finite closed interval `[0,1]` for p-min; speculation type in `draft-mtp|none|ngram-mod`; an explicitly set `QWEN_MTP_N` is rejected outside `draft-mtp` (`S:66`–`S:89`).
- Default compatibility evidence is in the `--cache-ram 8192` assertion and byte comparison: the fixture hash equals the stripped-current hash in each 79/0 run, with exactly 36 current tokens (`T:74`–`T:119`).

## Item 2 — directly testable guard

- Added side-effect-free `guard`, which scans `QWEN_LANES_DIR/*/lane.pid`, verifies process liveness, reads `HERMES_MODEL` from the live process environment, prints `pidfile pid route`, and returns rc 7 if any local owner exists (`S:159`–`S:185`).
- `*-local` is `LOCAL`; absent/empty model and unreadable environment fail closed as `LOCAL`; all other model values are `CLOUD`. Dead pidfiles are reported `stale` and do not block (`T:250`–`T:279`).
- Tests use real child `/proc/<pid>/environ` data and kill/wait only their own `CHILD_PIDS`. They bind every guard call to a throwaway `QWEN_LANES_DIR` (`T:223`–`T:248`).

## Item 3 — guard before persistent or lifecycle effects

- Changed `install()` ordering is render/compare; an identical candidate validates inputs and returns without guard, write, or systemd; a changed candidate runs `guard_or_die`, then validates inputs, queries `systemctl --user is-active`, writes, and mutates systemd (`S:224`–`S:251`). A changed unit cannot reach even the active-state query under a local lane.
- `start`, `stop`, and `restart` share guarded `change_service()`; `uninstall()` guards before `disable --now` and unit deletion (`S:276`–`S:301`).
- Cloud-route lanes remain non-blocking. The fake `systemctl` sink records `daemon-reload`, `enable --now`, and `restart` for a changed already-active install (`T:331`–`T:336`).

## Item 4 — deterministic negative controls

- AF-AP-79 byte invariant uses `BEFORE`, `AFTER`, and the `CALLS` log: `AF-AP-79: local lane refusal preserves unit bytes and makes zero systemd/keygen/mkdir side effects` (`T:304`–`T:311`). Observed rc 7, identical SHA, and zero recorded calls.
- Explicit refusal: `qwen-server: a local-route lane is alive — service change refused 7`; the preceding record names the live `LOCAL` pidfile (`T:307`–`T:313`). The adjacent no-op assertion proves an identical unit returns rc 0 with byte identity and zero systemd calls (`T:314`–`T:321`).
- Each refusal in the `for action in start stop restart uninstall` loop preserves unit bytes and leaves the fake systemd call log empty (`T:339`–`T:347`).
- The `INSTALL_HOME` input-order negative control proves an unpinned explicit model is rejected before creating config/state (`T:209`–`T:216`).
- Four scratch mutations were killed: fixed cache RAM, local→cloud route, absent-route fail-open, and removed install guard. Each failed at the named assertion; no mutant touched the working tree.

## Documentation

- `docs/HARNESS-PORTS.md` records the full command surface, default cell, six knobs, domains, route policy, stale-pid handling, no-op behavior, and guard-before-effect contract (`H:397`–`H:409`).
- `PC-BRIDGE.md` tells operators to run `guard` before matrix/server restart and describes rc 7 local/absent behavior, unchanged-install no-op, and protected lifecycle actions (`P:170`–`P:177`).

## Gates

- Focused static/archive gate, two independent runs: `qwen-server: 79 passed, 0 failed`; `qwen-server: 79 passed, 0 failed`; `STATIC_ARCHIVE_RESULT run1=0 run2=0`.
- Bash syntax: rc 0 for `harness-ports/bin/qwen-server.sh` and `harness-ports/tests/test_qwen_server.sh`.
- `git diff --check`: rc 0.
- AP screen: S, H, and P each had 0 hits. T had one AF-AP-33 hit at the explicitly labelled fake `curl` sink that emits `status` and `data` (`T:322`–`T:326`); the safety oracle uses real child process state plus independent byte/call-log observations. The report had one AP-51 vocabulary hit in its self-attack sentence; it describes a hostile possibility and cites the disjoint controls, not a silent catch-all.
- GitNexus `detect-changes`: `Changes: 6 files, 5 symbols`, `Affected processes: 0`, `Risk level: low`. Its clone index reports the coordinator-staged brief files too; code-intel output remains advisory.

## Evidence tiers

- VERIFIED this session: PIN premise, 34-token old contract, current line-bounded implementation, focused 79-check archive runs twice, four killed mutants, Bash parse, diff check, AP screens, and identical PIN/proposal aggregate dispatcher failure.
- INFERRED: none used for implementation acceptance; sandbox-side independent verification remains required.
- ASSUMED: none used to claim a passing test or a real service result.

## Self-attack

1. Guard could classify the wrong route. Ruled out with real child `/proc/<pid>/environ` controls for local, cloud, absent, empty, stale, and unreadable-environment cases (`S:159`–`S:185`; `T:250`–`T:279`).
2. A refusal could still mutate the unit or systemd. Ruled out with `UNIT_PATH`, `BEFORE`, `AFTER`, and `CALLS`: rc/reason, byte-identical SHA, an empty fake systemd log, and absent key/log paths (`T:304`–`T:321`). Removing the changed-install guard kills the suite at that exact assertion.
3. New cell flags could silently change the old launch shape. Ruled out by the `PIN_ARGV` 34-token fixture compared byte-for-byte after removing only the required cache-RAM pair (`T:77`–`T:119`), plus `bad_knob` presence/omission and invalid-domain tests (`T:121`–`T:161`).

## Discrepancies

- CONCLUSION REVERSAL, ESCALATED: first, this lane added a `/proc/<pid>/cmdline` identity filter and reused-PID negative control because a stale pidfile can point at an unrelated live process after PID reuse. That state was based on preventing false ownership. After re-reading the brief, the lane removed both because the heuristic was not in the stated contract and could reject legitimate lane launch shapes. Current code therefore trusts any live PID named by `lane.pid`. The tests prove current behavior, not which design is correct; acceptance is blocked on coordinator/verifier resolution.
- `harness-ports/tests/run-all.sh` returned rc 1: all listed suites passed except `test_pc_lane_dispatcher.sh`, which printed `pc_lane dispatcher: 0 passed, 9 failed`; the aggregate ended `1 SUITE(S) FAILED`. A clean `git archive 7537910` reproduction of that dispatcher alone also printed `0 passed, 9 failed`. This is pre-existing and outside the brief's file boundary.
- `scripts/lane_gate.sh` expects pytest targets and cannot execute this shell suite directly. The equivalent required archive-copy isolation was run manually twice from `git archive 7537910` plus only S/T/H/P bytes; both runs were 79/0.
- ShellCheck exact output: `shellcheck: unavailable`. Pyflakes exact output: `/usr/bin/python3: No module named pyflakes`; there are no changed Python files.
- `scripts/why.sh` likewise reported current blast radius `index unavailable` for these shell functions; direct GitNexus impact returned `Target 'validate_knobs' not found` and `Target 'guard' not found`, each with risk `UNKNOWN`.
- `CLAUDE.md` already contained the exact requested guard guidance at the worktree PIN and was not modified by this lane. It is excluded from file identity.
- Final report lint: `report_lint: 46 refs — OK 20, NEAR 12, MISS 14, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`. This was bounded round 3; the 10-reference floor passed. Remaining heuristic misses are reported rather than chased. Later report wording and added test comments/explicit service paths shifted T/H/P line numbers; load-bearing ranges were manually re-anchored, and lint was not rerun beyond the three-round cap.

## File identity

- PIN `d059150d3dfdac152450ac58d3260b746deb9c992938466f4a9ae3e1232828ca` → proposal `3a663e4faba782bce3047517aeaa904b08022c91b6e826491d24ba05065dff84` — `harness-ports/bin/qwen-server.sh`, 199 → 302 lines.
- PIN `fe5e7834a8d45059013c3b35807732cb341ca5989a0de32f1173bc63e65f7d6f` → proposal `2b3e51ccbdec77a5ce54b494968a3b3a695f554059c42f4e651871994fa75082` — `harness-ports/tests/test_qwen_server.sh`, 129 → 357 lines.
- PIN `8bf48bde8c30a6239f53d3740a43e3958d23dd6e2c38287806c1edd52250cb88` → proposal `cb88ec6bffa1e3821083e7933ec051f3ef6184b3d5a09998b240a99a0de4d4bd` — `docs/HARNESS-PORTS.md`, 675 → 677 lines.
- PIN `872f058daac2203c11f7a626ddc877f7231e6f54e411787e726bcd5ebc322339` → proposal `6bb45bd3bb851424e4ee701f8fc53430fce939ee962de0eb42f1762343d99dd3` — `PC-BRIDGE.md`, 197 → 199 lines.
- Lane report: `tasks/briefs/qwen-matrix-support/QM0-report.md`, 97 lines at final capture; report hash is intentionally omitted because recording its own hash would change the file.

## Hygiene and handoff

- Timestamp: `2026-09-15T14:25:45Z`.
- No real server lifecycle command ran. Test children were killed and waited by PID; no background test process was intentionally retained.
- Retro: no new general lesson to bake beyond AF-AP-79 and the existing negative-control rules already cited.
- This is proposal evidence for the sandbox-side adversarial-verifier. The coordinator/verifier must resolve the lane PID identity contract and grade every final acceptance claim before landing it.
