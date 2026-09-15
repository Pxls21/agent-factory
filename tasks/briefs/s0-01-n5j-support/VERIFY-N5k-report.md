# VERIFY-N5k — PC adversarial verification proposal

Arm A landed commit: `b9b6134`  
PIN: `3277373`  
Scope: S0-01 ACP probe round 14, plus arm B v3 comparison.

## VERDICT

**PC provisional grade: NOT-READY for promotion.** This is a verification proposal, not a final gate verdict: the sandbox adversarial-verifier lane must independently grade it.

**F1 — blocking hollow-green: arm A's committed suite does not kill a read-side `O_NOFOLLOW` regression.** On a fresh full PIN scratch tree, I removed `os.O_NOFOLLOW` only from the read-open flags at `probe:62`, then ran the entire targeted suite with venue exports: **`113 passed in 52.01 s`**. The mutated primitive follows a final symlink to a regular file and returns its content (`ACCEPTED=real content`), violating the property stated at `probe:58-60`. This is a real behavioral failure, not a static-rig artifact. Minimal fix: add a committed behavioral test that passes a final symlink to a regular file into `_read_regular` and requires the exact `ELOOP` refusal; port/adapt v3's source-mutant guard at `test_probe_read_primitive_mutants_die_at_the_open_level` as a second control.

**F2 — non-blocking observation gap: arm A has no real-emitter fd census.** The landed bytes remained safe in the exact matrix run: landed, CLOEXEC-dropped, and set-inheritable-only each gave `CENSUS=0`; `set_inheritable + close_fds=False` and the full triple gave `CENSUS=1`. The two changes needed for the leak are independently caught by arm A's structural pins, the `O_CLOEXEC` pin inside `_framedir_flags_from_probe_source` and the `popen_block` pin inside `test_probe_agent_launch_pins_the_close_fds_default_second_defence`. This is not the blocker, but it leaves the claimed child-fd property unobserved at the real `proc` launch (`probe:371-373`). Port v3's real-emitter census from `test_probe_census_agent_sees_no_framedir_fd_on_final_bytes` as defense in depth.

**F3 — v3-only port defect, not an arm-A byte defect.** v3's `close_fds=True` source pin (the file-wide presence assertion inside `test_probe_framedir_open_pins_oder_directory_and_ocloexec_and_popen_pins_close_fds`) searches the whole source for that string. A comment at `v3probe:382` contains it, so a mutant changing the actual `Popen` argument at `v3probe:388` to `close_fds=False` (`v3probe:390`) still passed that v3 pin (`1 passed in 0.04 s`). Do not port that pin as written; scope it to the Popen block or parse the AST.

No current-byte failure was found in the O_DIRECTORY, O_CLOEXEC, fd-first read, receiver-inventory, or exact-negative-reason properties. The blocker is the surviving F1 mutant: a gate that stays green over this real regression is hollow.

## FILE IDENTITY

- The probe file `proofs/S0-01/tools/acp_probe.py` (the `acp_probe` module): **677 lines**, SHA-256 `e71ec3cfc7db220424b08fb90070166983c35a69cdc6cd78270dc216db9d3726`.
- The test file `tests/test_s0_01_acp_probe.py`: **3592 lines**, SHA-256 prefix `ee29b9584fdc3908`.
- Both match the PIN/brief identity. The lane worktree was clean before scratch mutations; all mutations were under the lane-private scratch directory.
- Reconstructed v3 identity: the v3 probe `proofs/S0-01/tools/acp_probe.py` is **695 lines**, SHA-256 `d141648893366b9c7adf11dbc8c760b216f84de07c2ccd183c466d145af4adc8`; the v3 test `tests/test_s0_01_acp_probe.py` is **3681 lines**, SHA-256 `d7f033dc85169bfacaba7cb8a51493aae363b28c702aa635ee8bd59ce87fb3fe`.

## Item 0 — mechanical gates

- Fresh targeted run 1: **`113 passed in 50.97 s`**.
- Fresh targeted run 2: **`113 passed`**.
- `python3 -m pyflakes` on the two target files returned `0`.
- `python3 scripts/ap_screen.py proofs/S0-01/tools/acp_probe.py` and the `--tests` scan were clean; no AF-AP-70 row was introduced.
- No suite result was accepted from a zero-match filter. Every piped mutation run recorded the producer status separately.

## Item 1 — O_DIRECTORY load-bearing

The framedir is opened once with `O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC` at `probe:326-327`. The relevant mutation is behavioural:

- In the source-injected dir-to-file window rig `test_probe_refuses_a_file_swapped_into_the_framedir_at_the_odir_window`, LANDED names the framedir in the resulting error; O_DIRECTORY-dropped opens the swapped regular file and fails later on a leaf. The dropped-mutant control `test_probe_odir_dropped_mutant_names_the_leaf_not_the_framedir` reds because the failure names `frame/runtime-identity.json`, not the framedir.
- A file present at framedir creation time is non-discriminating: both landed and O_DIRECTORY-dropped exit 64 through the earlier `makedirs(..., exist_ok=True)` path. That shape never reaches the open.
- Therefore the window rig, not the file-from-start probe, proves the flag is load-bearing. The source-injection rig reaches the actual open; it is not the v3 agent-driven swap shape that misses the window.

**Held for current bytes.**

## Item 2 — O_CLOEXEC and the child-fd claim

The framedir flag is present at `probe:327-328`; the real agent launch is `proc` at `probe:371-373`. Arm A's isolated-census test `test_probe_cloexec_is_load_bearing_child_sees_no_framedir_fd` is a fork/exec census that sets F_SETFD itself, so it does not observe the probe's actual launcher. The `O_CLOEXEC` pin inside `_framedir_flags_from_probe_source` structurally evaluates the framedir flags, and the `popen_block` pin inside `test_probe_agent_launch_pins_the_close_fds_default_second_defence` structurally pins the absence of a `close_fds` override in the Popen block.

I re-ran the real-emitter matrix with v3's canonical census agent, which counts only fds that resolve to the framedir:

| scratch mutation | real Popen result |
|---|---|
| landed | `rc=0 CENSUS=0` |
| drop O_CLOEXEC only | `rc=0 CENSUS=0` |
| `set_inheritable(framedir_fd, True)` only | `rc=0 CENSUS=0` |
| drop O_CLOEXEC + set-inheritable | `rc=0 CENSUS=0` |
| set-inheritable + `close_fds=False` | `rc=0 CENSUS=1` |
| full triple: drop O_CLOEXEC + set-inheritable + `close_fds=False` | `rc=0 CENSUS=1` |

The previous broad fd-count experiment was discarded: it counted all child fds above 2 rather than only framedir fds. A direct child fd-table dump for set-inheritable-only showed `FRAMEDIR_HITS=[]`; it is safe. The real leak requires `close_fds=False` plus an inheritable fd. Arm A structurally catches the two required source changes. v3's real-emitter census catches the full triple: it reds with `CENSUS=1`.

**Held for current bytes; F2 is an observation-strength recommendation, not a current-byte failure.**

## Item 3 — fd-first read primitive

`_read_regular` at `probe:48-78` opens first, validates `fstat(fd)` with `S_ISREG`, closes on every refusal, and then returns the owned fd. Every file-content reader routes through it via `_sha256_file` at `probe:81-91` or the fixture read path.

Standalone timeout probes established the hostile-input mechanics:

- A historical stat-then-open shape hangs on a FIFO under `timeout` (`rc=124`).
- LANDED `_read_regular` refuses the same FIFO promptly; no caller hangs.
- A blocking `os.open` on a writer-less FIFO hangs (`rc=124`); an `O_NONBLOCK` open returns a live FIFO fd, then `S_ISREG` rejects it. The **flag at `probe:62` is load-bearing**.
- Dropping `S_ISREG` accepts `/dev/zero`; dropping the close-on-refusal path leaves `fd_delta=1`; dropping `O_NOFOLLOW` follows a final symlink.
- The fcntl **clear** at `probe:68-69` is a separate concern: removing only that clear still reads a 1 MiB regular file completely. It is belt-and-braces for regular-file reads; it is not the same as dropping the open flag.

F1 is the outcome of taking the O_NOFOLLOW mutant through the full committed suite. The current code is correct, but the suite does not guard this exact regression.

## Item 4 — receiver inventory

The inventory scanner (`test:2868-2960`, its `tracked` set names `attribute.read_bytes` and the like) keys receivers by `(function, callee, ordinal)`; the equality check `test_probe_every_file_receiver_is_guarded_or_committed` at `test:3030` enforces it. I planted eight independent bypass forms in fresh scratch copies:

- `Path.read_bytes`, `Path.read_text`, `io.open`, `os.open` plus `os.fdopen`, builtins `open`, and bound-local `Path` in new functions;
- `open` and `io.open` inside existing `_sha256_file`;
- replacement of the existing `_read_regular` call at the same ordinal.

All eight changed the scanner result and were caught. Collapsing the ordinal part of the identity key also red the equality comparison. The inventory is adequate for receiver-shape changes, but it cannot see flag changes inside an already-inventoried `os.open` call. F1 demonstrates that limit.

## Item 5 — serial and parallel evidence runs

- Serial pair 1 (`test_s0_01_acp_probe.py` plus `test_s0_01_negative_contract.py`): **`172 passed in 52.69 s`**.
- Four-file `xdist -n 4` run: **`600 passed, 9 xfailed in 202.87 s`**.
- The nine xfails are the known stale corpus `probe_sha256` mismatch.
- The second long serial pair was deliberately not re-run: its conformance component exceeds this lane's command ceiling. It was read as reported evidence only, not counted as reproduced.

## Item 6 — mutation audit

| mutation | observed killer or survivor |
|---|---|
| O_DIRECTORY drop, source-injected window | `test_probe_refuses_a_file_swapped_into_the_framedir_at_the_odir_window` red; leaf-vs-framedir discriminator `test_probe_odir_dropped_mutant_names_the_leaf_not_the_framedir` |
| O_DIRECTORY drop, file initially at framedir | both exit 64 earlier; non-discriminating shape |
| O_CLOEXEC drop | structural flag pin red inside `_framedir_flags_from_probe_source` |
| `close_fds=False` | `popen_block` pin red inside `test_probe_agent_launch_pins_the_close_fds_default_second_defence` |
| read O_NONBLOCK flag drop | **`3 failed, 110 passed`**; FIFO timeouts in `test_probe_refuses_a_non_regular_fixture`, `test_sha256_file_refuses_a_non_regular_file`, and `test_probe_unreadable_own_file_is_named_not_a_traceback` |
| read O_NOFOLLOW flag drop | **SURVIVED**: `113 passed in 52.01 s`; direct regular-symlink read accepted content (F1) |
| read S_ISREG drop | `/dev/zero` accepted / non-EOF read path reachable |
| no close on read refusal | `fd_delta=1` |
| S_ISREG changed to only reject directories | FIFO and `/dev/zero` accepted |
| close before fstat | `EBADF` |
| framedir O_NOFOLLOW drop | `realpath` guard at `probe:324-325` still rejects symlinked framedir; belt-and-braces |
| realpath guard drop | symlinked framedir reaches a later `NotADirectoryError` |
| swallow read fstat refusal | FIFO no longer gets the named refusal |
| delete inventory row | equality comparison `test_probe_every_file_receiver_is_guarded_or_committed` red |
| fcntl O_NONBLOCK clear drop only | regular-file 1 MiB control completes; lone suite red is self-hash structural control, not read behaviour |
| full fd-leak triple | real-emitter `CENSUS=1`; arm-A's two independent source pins red because both source protections were removed |

Nine independently added mutation rows plus the real-emitter triple meet the brief's minimum of eight. F1 is reported as a survivor, not rationalized away.

## Item 7 — exact negative reasons

The negative controls were reviewed for exact reason assertions. There are no `rc != N`-only acceptance checks. Refusal cases pair return code with exact stderr/stdout/probe-error state, including the read and framedir cases: `test:486` (`returncode`) pairs its return code with the exact stored `probe_error`; `test:588` (`returncode == 64`), `test:682` (`returncode == 64`), and `test:950` (`returncode == 64`) pair exit 64 with exact validation messages. No AF-AP-64 or AF-AP-65 pattern was found.

## Item 8 — arm B v3 comparative grade

v3 reconstructed from `c6c384a` plus `N5k-xhigh-v3.diff`; its own suite produced **`119 passed in 52.42 s`**. Its read primitive is mechanically the same fd-first shape, renamed `_open_regular_read` at `v3probe:48-78`. Its three design changes are: explicit `Popen` launch with `close_fds=True` at `v3probe:388-390`; named ENOTDIR refusal at `framedir_fd = os.open(` (`v3probe:330-331`); and a real-emitter census `test_probe_census_agent_sees_no_framedir_fd_on_final_bytes`.

| v3 new test | arm-A equivalent | comparative finding |
|---|---|---|
| `test_probe_framedir_oder_directory_makes_the_open_raise_not_return` (v3:3366) O_DIRECTORY direct open proof | `test_probe_refuses_a_file_swapped_into_the_framedir_at_the_odir_window`, `test_probe_odir_dropped_mutant_names_the_leaf_not_the_framedir` | DIFFERENT-PROPERTY: both kill; arm A's window rig reaches the open, v3's direct proof is simpler |
| `test_probe_framedir_open_pins_oder_directory_and_ocloexec_and_popen_pins_close_fds` (v3:3403) combined structural pin | `_framedir_flags_from_probe_source` pin + `popen_block` pin | ARM A STRONGER for close_fds: v3's file-wide presence assertion is comment-defeatable (F3) |
| v3:3424 regular read | no direct arm-A primitive success test | v3 stronger coverage, low risk |
| v3:3436 named non-regular refusals | no arm-A read-side exact-name test | v3 stronger |
| v3:3466 no fd leak on refusal | none | v3 stronger |
| `test_probe_read_primitive_mutants_die_at_the_open_level` (v3:3481) source-mutant read guard | inventory only | v3 stronger structural coverage; it catches its expected NOFOLLOW source mutation |
| `test_probe_census_agent_sees_no_framedir_fd_on_final_bytes` (v3:3603) real-emitter census | isolated census test only | v3 stronger observation of final bytes |
| `test_probe_census_isolated_fsetfd_negative_control` (v3:3623) isolated F_SETFD control | `test_probe_cloexec_is_load_bearing_child_sees_no_framedir_fd` | redundant |

Port, in priority order:

1. A behavioral final-symlink-to-regular test for `_read_regular` (new arm-A test) plus v3's source-mutant guard adapted to `_read_regular`. This closes F1.
2. The v3 named-refusal and no-fd-leak tests, adapted to arm A's helper name, for named refusals and fd closure.
3. The v3 real-emitter census, adapted to arm A's fixtures, for F2 observability.
4. Optionally make `close_fds=True` explicit, but first amend arm A's absence pin and do not copy v3's comment-defeatable presence pin.
5. The named ENOTDIR branch is optional UX/telemetry improvement; arm A already has a behavioural O_DIRECTORY gate.

## Item 9 — report discipline

Arm A's `N5k-report.md` lint was reproduced before this report: **`41 refs — OK 39, NEAR 0, MISS 0, UNCHECKABLE 2`**. v3's report had **`51 refs — OK 32, NEAR 3, MISS 16, UNCHECKABLE 0`** on its reconstructed tree; its misses are line-number drift and it did not paste a completed lint summary. This report's lint result is appended last after the bounded lint pass.

## Item 10 — design recommendations

- Keep the fd-first read shape at `probe:48-78`, the O_NONBLOCK **flag**, fstat classification, and close-on-refusal path.
- Retain the fcntl clear as cheap defense in depth, but document it separately from the load-bearing open flag.
- Add F1's direct behavioral symlink test. A source-inventory test cannot protect flag semantics.
- Add the real-emitter census but retain independent source pins. The census protects emitted state; the pins protect source intent.
- If `close_fds=True` becomes explicit, replace the current absence-only arm-A pin with a scoped assertion that permits the explicit safe value and rejects `False`.

## Item 11 — process and scope

All hostile FIFO experiments were standalone and timeout-bounded. Scratch trees were private full copies or deliberately minimal proof/test copies with the required `proofs/S0-01` layout. No production service, PC runner, real corpus content, credentials, bridge material, or other Stage-0 lane was touched. No commits, pushes, or outward-facing actions were performed.

## DISCREPANCIES

1. v3's agent-driven O_DIRECTORY swap cannot land because the `framedir_fd = os.open(` at `v3probe:330-331` precedes the `Popen` at `v3probe:388-390`; arm A's source-injected window rig does land. The differing results are shape-specific, not contradictory.
2. The premise that CLOEXEC-dropped alone causes a real-emitter census of one did not reproduce. With `close_fds=True`, the single drop gave `CENSUS=0`; the leak requires an inheritable fd and `close_fds=False`. v3's own isolated F_SETFD control `test_probe_census_isolated_fsetfd_negative_control` correctly isolates the flag bit.
3. The earlier broad child-fd count was not used as final evidence because it counted non-framedir fds. The canonical census matrix and direct fd-table dump supersede it.
4. O_NONBLOCK has two independently tested pieces: dropping the open flag causes FIFO hangs; removing the later fcntl clear does not break regular-file reads. They must not be conflated.

## NOT-DONE

- No live Buzz → ACP → Hermes → OmniRoute run was launched; this increment is a probe/test verification task and the brief prohibited launching those services.
- No sandbox-side independent adversarial grading has occurred. This PC report is evidence and a proposal only.
- The F1 fix was not implemented: the task is verification, not a builder increment.
- Pair 2 of the long serial item-5 run was not reproduced locally for the stated command-ceiling reason.

## LINT SUMMARY

Final bounded `report_lint.py` run (three rounds, four maps `probe`/`test`/`v3probe`/`v3test`, `--min-refs 25`):

`report_lint: 26 refs — OK 25, NEAR 0, MISS 0, UNCHECKABLE 1, UNRESOLVED 0 (worktree)`

The one UNCHECKABLE is `probe:68-69` on a line carrying no backticked claim token; no MISS or NEAR remains.
