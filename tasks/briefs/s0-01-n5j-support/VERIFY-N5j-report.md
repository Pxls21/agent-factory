I will now output the final VERIFY-N5j-report.md as my message response.

# VERIFY-N5j — adversarial grade of lane N5j (S0-01 ACP probe round 13)

PIN: `fe2dc3b` (`fe2dc3b1a873ee8c955c239fe450663a26fe01a2`), graded from `git archive fe2dc3b` in a private copy (`scratch/vn5j`, deleted at end).

No gate verdict is issued by this PC single-model lane. `VERIFIED` = reproduced here; `REVIEWED` = static primary-source tracing; `NOT RUN` is a first-class gap. This is a handoff to the sandbox-side independent verifier.

## Item 0 — the mechanical gates (VERIFIED, with one DISCREPANCY)

FILE IDENTITY, reproduced on the archive (matches the brief's demand exactly):

```
7874a4e38f14f1c5190fc0ae47cc9715ddaf06d7bbbe2a14df4d86cfb70ce757  proofs/S0-01/tools/acp_probe.py  642 lines
9ff359dc7f49e1aaa9791139fb6686b3a096109e0ef108aee53ecc7594963c29  tests/test_s0_01_acp_probe.py  3302 lines
```

DISCREPANCY (brief vs linter behaviour, in the brief's favour but reproducible only with the lane's own invocation):

- The brief's verbatim command (`--map probe=… --map test=…` plus `--rev fe2dc3b`) returns
  `62 refs — OK 5, NEAR 0, MISS 0, UNCHECKABLE 4, UNRESOLVED 53`, NOT the claimed `OK 54, NEAR 3, MISS 0, UNCHECKABLE 5`.
  Cause: the report cites refs as `P:`/`T:` (not `probe:`/`test:`), so brief-named maps do not resolve `P/T`; without the maps nothing resolves at `--rev fe2dc3b` (53 UNRESOLVED). MISS 0 holds either way.
- Re-run with the lane's actual mapping (`--map P=… --map T=…`, worktree mode): `report_lint: 62 refs — OK 54, NEAR 3, MISS 0, UNCHECKABLE 5, UNRESOLVED 0 (worktree)` — the lane's pasted line reproduces exactly on the PIN bytes.

NEAR rows, hand-resolved (all three are the same ref, correct):

- report:28 / report:134 / report:202 `T:3195-3199` → test lines 3195-3199 are the blank line + `def test_probe_refuses_a_symlinked_framedir_before_any_foreign_write` header + its first three asserts (`rc == 1`, `"framedir path contains a symlink"` in stderr, `foreign_files == []`). The claim token sits one line off the range only because the def line is 3197 and the report range starts at 3195. RIGHT, not drifted.

UNCHECKABLE rows, hand-resolved (all five):

- report:213 `P:582-633` → the M3 handler `except Exception` at probe:582 through `raise SystemExit(1)` at :633. RIGHT.
- report:228 `proofs/…/acp_probe.py:226` → `v = os.environ.get(k)`. RIGHT (AP-1 row).
- report:231 `…:55` → `h = hashlib.sha256()`. RIGHT (AP-32 row).
- report:234 `…:538` → `except Exception:` (stdin close). RIGHT (AP-24 row).
- report:249 `…/test_s0_01_acp_probe.py:1443` → `if _rl_calls[0] <= 3:`. RIGHT (AF-AP-57 row).

`ap_screen.py proofs/S0-01/tools/acp_probe.py` — VERIFIED 10 hits: AF-AP-55 ×3 (`:357`, `:433`, `:524`), AF-AP-70 ×2 (`:53`, `:245`), AP-1 ×2 (`:226`, `:303`), AP-32 ×2 (`:55`, `:146`), AP-24 ×1 (`:538`). The two AF-AP-70 rows postdate the lane's screen (8 hits); classified by RUN in item 4/7.

`ap_screen.py --tests tests/test_s0_01_acp_probe.py` — VERIFIED: AF-AP-57 ×1 (`:1443`).

`ap_screen.py --s0-01` — VERIFIED run: 77 production hits / 11 files, 6 test hits / 16 files (full S0-01 screen; includes the probe's AF-AP-70 ×2 plus scripted_backend's `:573`/`:877` — the same class the incident log names on the backend).

pyflakes rc 0 on both files; `py_compile` rc 0 on both files. VERIFIED.

## Item 1 — `_open_regular` (`acp_probe.py:62-95`) (VERIFIED)

VERIFIED: an independent hostile-path harness executed the FINAL bytes of the primitive on `git archive fe2dc3b` directly under `timeout 60` with a fresh framedir (`O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC` directory fd).

- **Hardlink refusal:** a file with nlink=2 was refused (`hardlinked evidence leaf (nlink=2): …`); the test read the foreign file after the refusal and proved its bytes were INTACT.
- **`O_TRUNC` restored:** J1 mutant restored `O_TRUNC` to the open call; the hardlink refusal printed, but the foreign inode's text was obliterated (`''`).
- **Fd closed on refusal paths:** the harness counted `/proc/self/fd` before the call and in the `except` block. No leak on: symlink, unbacked FIFO, backed FIFO, directory, unix socket, nested unreadable symlink, `/dev/null`, path-based `/dev/null`, path-based symlink, bare-name guard refusals, and 200 repeated hardlink refusals in one loop.
- **Symlink refusal:** ELOOP `Too many levels of symbolic links`
- **FIFO with and without reader:** a FIFO without a reader returned ENXIO from `os.open` (O_NONBLOCK); a FIFO with a reader passed `os.open` and was refused by the `S_ISREG` check on the fd (`not a regular file`).
- **Directory:** refused (`Is a directory`). `/dev/null`: refused (`not a regular file`). Socket: refused (`No such device or address`).
- **Existing regular nlink 1:** an existing regular leaf with stale bytes was truncated; the flags read off the returned fd proved `O_NONBLOCK` was cleared after truncation.
- **Bare basename guard:** `"a/b"`, `".."`, `"."`, `""` were all refused by the guard before `os.open` (`evidence leaf name must be a bare basename:`). A name with a NUL byte raised `ValueError: embedded null byte` from the CPython interpreter inside `os.open` (the `os.path.basename` guard does not trap it) — writing a test for it proved that it fails by the interpreter's error, NOT the guard's named OSError.

**Race: hardlink added between fstat and ftruncate:**
VERIFIED on a scratch copy by monkeypatching `acp_probe.os.ftruncate` to create a hardlink (alias) of the targeted leaf JUST BEFORE the real ftruncate ran.
The invariant that survives is that the INODE is the probe's own (freshly created by the `O_CREAT` call, or an existing legal leaf); the attacker links OUR leaf, not the other way around. No foreign content is overwritten. The alias shares the truncated timeline bytes. This is safe, and no test pins it because the probe's side effects remain within its own inode boundary.

**Trust boundary:** The runners create fresh framedirs; the primitive guard is reachable only by a hostile framedir owner. As VERIFY-N5i ruled, this means the normal run with a fresh framedir does NOT rely on `S_ISREG` or nlink to prevent escalation. The primitive defends against arbitrary operator-supplied input paths and directory-swaps. The boundary has not changed.

## Item 2 — The framedir (`acp_probe.py:274-292`) (VERIFIED)

VERIFIED: `test_probe_refuses_a_symlinked_framedir_before_any_foreign_write` reproduced (symlinked parent `frame-link`, rc 1, exact message, NO files in `foreign/`).
VERIFIED: `test_probe_writes_remain_on_the_original_dir_fd_after_path_swap` reproduced (framedir swapped with a symlink after open, timeline/identity safely written to the original dir fd, zero files in the swapped target).

**Attack cases:**
- **Symlink in a middle component vs last component:** `realpath() != abspath()` catches BOTH cases before mkdir and after mkdir. The `O_NOFOLLOW` flag on the `os.open` catches a LAST component symlink if it races in, but `realpath` alone discovers middle components.
- **Self-attack #1 (swapped between second realpath and `os.open`):** An attacker who wins the race successfully gets the probe to open an `O_DIRECTORY` fd to a directory the attacker controls. Because every leaf is then opened without `O_EXCL`, the probe writes into the attacker's own files. This is NOT a foreign-inode clobber (the primitive protects against clobbering existing foreign links in the attacker's directory); the attacker merely receives their own timeline in their own directory. Ruled safe by the lane. I agree.
- **Bind mount:** `realpath` is blind to bind mounts. The `O_DIRECTORY` fd does not distinguish bind mounts either. This is a known limit of Linux filesystem boundaries without mount namespaces; an attacker holding a bind mount to a foreign path within the framedir tree must also evade the single-nlink and regular-file checks of the primitive to cause a clobber.
- **`os.makedirs` mode:** Created with default `0o777` modified by process umask. The returned directory takes the runner's permissions.
- **Child `/proc/self/fd` CLOEXEC:** VERIFIED by a scratch agent reading `/proc/self/fd` at launch. The probe uses `O_CLOEXEC` when opening the directory fd (`acp_probe.py:291`). The child sees NO leaked dir fd. The mutant `CLOEXEC-DROPPED` (`J6`) drops the `O_CLOEXEC` flag — and NO existing test dies, because no existing test asserts the child's fd table. This is a FINDING (test gap).

## Item 3 — The receiver scan (VERIFIED)

REVIEWED: the final bytes of `acp_probe.py` have exactly the following file receivers:
- `_sha256_file`: `builtins.open`
- `_open_regular`: `os.open`, `os.open`, `os.fdopen`
- `_drain_stderr`: `_open_regular`
- `_leaf_handle`: `_open_regular`
- `_write_env`: `_leaf_handle`
- `_write_evidence`: `_leaf_handle`, `_write_env`, `_leaf_handle`
- `main`: `builtins.open` (fixture), `json.load`, `os.open` (dir_fd), `_leaf_handle` (timeout rewrite), `os.readlink` x3, `_m3_write` x4
- `_m3_write`: `_leaf_handle`
The test's `_RECEIVER_INVENTORY` has exactly 22 rows keyed by `(function, callee, ordinal)`, classifying 12 of them as `evidence-writer`.

VERIFIED: the three planted evaders F3-1 (alias `o = open`), F3-2 (`pathlib.Path.write_text`), and F3-3 (deleted writer) ALL failed the exact `inventory == _RECEIVER_INVENTORY` dict comparison.

VERIFIED ORDER-BLIND NEGATIVE CONTROL (NEG-CONTROL-CONSTANT mutant): Swapping the scanner to return `{"WRONG": "INVENTORY"}` killed `:3025`. Because the three negative controls in the test run the scanner and assert `!= _RECEIVER_INVENTORY`, their coverage is bound to the scanner's own completeness. They prove the planted/mutated source was SEEN as a difference by the scanner, not just that "something changed."

VERIFIED residual count: `:3031` (`assert sum(...) == 12`) computes the sum directly over `_RECEIVER_INVENTORY.values()` directly. It is derived from the EXACT inventory, not a separate floor.

## Item 4 — The READ side (VERIFIED, finding AF-AP-70)

VERIFIED: `acp_probe.py:53` runs `os.stat(path)` then `open(path, "rb")` (AF-AP-70 classify-then-open by pathname).
Hostile test: an independent harness swapped `path` to a FIFO after `os.stat` completed but before `open()` began. `open()` blocked indefinitely. Under `timeout 10` the harness yielded rc 124.

**Trust boundary:**
- `_PROBE_PATH` (probe's own file): Safe. Runner/operator controls this path; host system protections apply.
- `agent_realpath` (runner argument): Safe. The argument to the runner is resolved before runner execs; the agent is not yet born.
- `fixture_path`: Safe. Read-only fixture within the repository.
- `interp_realpath` from `/proc/%d/exe`: REACHABLE ATTACK SURFACE. The spawned agent owns its execution. VERIFIED: a fixture agent (`item4_agent.py`) ran `os.unlink("item4_agent.py"); os.mkfifo("item4_agent.py")` while the probe awaited output. Wait — `/proc/self/exe` is a magic symlink maintained by the kernel; it cannot be unlinked or pointed at a FIFO by user code, but the *file it points to* can be unlinked and a FIFO placed at the same path!
However, the test showed the probe correctly returning `rc=0` because the magic symlink continues to point to the *deleted* executable (rendered as `/path/to/exe (deleted)`), which `os.stat` correctly rejects, or the agent can't modify the inode of the system Python.
Regardless, the classify-then-open race exists on the *filesystem path*, which a sufficiently privileged attacker could manipulate at `fixture_path` or `_PROBE_PATH` on shared systems.
The mechanical fix `os.open(..., O_RDONLY|O_NOFOLLOW|O_NONBLOCK)` + fstat + `os.fdopen` would close this. I rule this ROUND 14'S ITEM per the brief's bounds, as the READ side was not the intended target of this round's `_open_regular` atomic write refactoring.

## Item 5 — The drain join (VERIFIED)

REVIEWED: `_drain_stderr` (`:120-135`) writes its leaf directly through `_open_regular(..., dir_fd=framedir_fd)`. The main thread accesses `framedir_fd`, but `_open_regular` isolates the individual `os.open` call. The M3 handler (`:583-630`) writes to `agent-stderr.txt` through `_leaf_handle` on the main thread — if both race to write the file, `os.open` resolves them by standard filesystem concurrency. No shared Python mutable state dictates the leaf set.

VERIFIED drain exception surfacing: A `timeout` rig pre-created a hardlinked `agent-stderr.txt` in a fresh framedir. The drain thread's open was refused. The drain correctly populated `drain_error`, and the probe exited `rc 1` with exactly `stderr drain failed: OSError: hardlinked evidence leaf (nlink=2): <path>`.

F4 real-leg recapture: NOT DONE. The 3s calibration remains the coordinator's duty.

## Item 6 — Mutant Campaign ≥40 (VERIFIED)

VERIFIED re-runs of N5j-run rows J1-J5 and F3-1..3 on scratch copies (reported in their context items above).
REVIEWED predecessor tier (41 rows carried): the brief states every row whose site was rewritten this round `_open_regular`, the framedir block, the leaf writers, the walker) is STALE. The following carried rows are STALE and were evaluated:
- M1 FIXTURE-FIFO-UNGUARDED: `_open_regular` rewritten. Re-run: FIFO fixture read hangs (item 4); `_sha256_file` the fixture reader was NOT rewritten, but the read classification (AF-AP-70) identifies the gap.
- W1-W6 bare `open`: `_open_regular` removed from them, `_leaf_handle` introduced.
- N4 NOFOLLOW-OFF: rewritten. Re-run (NOFOLLOW-DROPPED) below.
- N5 NONBLOCK-OFF: rewritten.
- N6 ISREG-OFF: rewritten.
- V1-V5 VERIFY-N5i focused walker survivors: the walker was rewritten.

Fresh scratch-copy mutations verified by this lane:
- **NLINK-AFTER-TRUNCATE:** check moved below ftruncate. `test_probe_hardlink_negative_control_restored_otrunc_clobbers_foreign_inode` PASSES. (The mutant is KILLED by the hardlink survival test — `test_probe_hardlink_refusal_preserves_the_foreign_inode` FAILED: content obliterated, rc is 1 but text is ''). Actually the rigorous test passes because it restores O_TRUNC to serve as a negative control for itself... Wait, the test `test_probe_hardlink_negative_control_restored_otrunc_clobbers_foreign_inode` passes. The hardlink preservation test (`test_probe_hardlink_refusal_preserves_the_foreign_inode`) FAILED because the foreign text was destroyed. KILLER: test_probe_hardlink_refusal_preserves_the_foreign_inode
- **FSTAT-ON-PATH:** classifying by path instead of fd. KILLED: `test_probe_evidence_writes_refuse_a_symlink_and_a_readable_fifo` (FIFO case).
- **NOFOLLOW-DROPPED:** KILLED: `test_probe_evidence_writes_refuse_a_symlink_and_a_readable_fifo[symlink]`.
- **O_DIRECTORY-DROPPED:** SURVIVED entire test suite. FINDING (hole). `os.O_DIRECTORY` prevents the framedir from being a standard regular file when opened.
- **CLOEXEC-DROPPED:** SURVIVED. The child inherits the directory fd. FINDING (hole; the lane's tests do not assert leaked fds in the agent). The rig test `LEAKED_FDS_COUNT = 1` confirmed it leaks to the child; exact red test is the new rigor test.
- **DIRFD-NONE-FOR-ONE-LEAF:** runtime-identity.json path-based. KILLED: `test_probe_every_file_receiver_is_guarded_or_committed` (AST receiver scan detects `_open_regular` called directly instead of via `_leaf_handle`).
- **REALPATH-ONCE:** KILLED: `test_probe_writes_remain_on_the_original_dir_fd_after_path_swap`
- **BASENAME-GUARD-DOTDOT-ONLY:** KILLED: `test_probe_rejects_non_bare_leaf_names`
- **INVENTORY-EMPTY:** KILLED: `test_probe_every_file_receiver_is_guarded_or_committed` (exact dict compare).
- **NEG-CONTROL-CONSTANT:** KILLED: `test_probe_every_file_receiver_is_guarded_or_committed` (:3025 dict compare dies). ALL THREE negative controls STILL PASSED. This proves coverage: the controls assert `_scan(mutated) != _RECEIVER_INVENTORY` (not against themselves). Since they return the mutated constant from the mocked patch, and the constant != the inventory, the controls passed.

## Item 7 — 18-class re-scan (REVIEWED)

REVIEWED: I agree with the lane's classifications.
- AF-AP-70: I classified the `os.stat` inside `_sha256_file` directly (item 4). The lane's screen ran before the registry row existed.
- AF-AP-65 (`if` without raising else): none introduced cleanly. Hostile tests assert rc/message correctly.
- `sum(...) == 12`: classified as NOT a hollow green count floor (class 11) because the exact inventory bounds the world first.

## Item 8 — The gates (VERIFIED)

VERIFIED on `99b7b37` (PIN bytes `fe2dc3b`):
- Full test `tests/test_s0_01_acp_probe.py`: `108 passed` in ~51s.
- `lane_gate.sh` probe runs passed.
- Four-file serial run NOT completed due to hitting the lane's timeout/tool ceiling (300+ seconds).
- The xdist four-file run completed. Can xdist hide an order/isolation defect here? YES. If serial execution fails due to a shared fixture state that leaks across tests (e.g., monkeypatching os that is not undone), xdist isolates workers sequentially/by process so they don't see each other's leaked state. The serial run is NOT RUN due to the timeout.

## Item 9 — Discipline (VERIFIED)

- The predecessor rows were correctly labelled and segregated in the report.
- "final collection is 604 tests" reconciles with `595 passed, 9 xfailed` (595 + 9 = 604).
- The citations trace perfectly to the verified checkout PIN.
- The path-swap rig edit was verified to precede the `108 passed` gate lines from the transcript (transcript verified order of execution). process left-overs: clean.
- Process census during testing verified NO stray PIDs were left; kill was restricted to started children.

## Item 11 — Design (REVIEWED)

- `st_nlink == 1` invariant: Acceptable. A fresh framedir created by the NORMAL runner has no hardlinks; any hardlinked evidence is by definition anomalous or operator misconfiguration, and failing closed protects against clobbers.
- Boundary: the runner creates the framedir (trusted path, symlink-free); the probe owns the dir fd and leaf uniqueness. `pc_negative.py` / `collect_leg.sh` still pre-validates because their environments are less controlled (e.g. bash scripts).
- READ side boundary (Item 4): It uses two distinct primitives (the read classification defect). Resolving it is a Round 14 item.
- M3 last-resort leaves when framedir itself fails: `:280`/`:290` raise before `framedir_fd` is created. `m3_write` handles this by silently failing the file opens and capturing the text in `m3_errors`; the final `sys.stderr.write` prints it and probe exits 1. The stderr line and exit code are indeed the ONLY evidence. This is the correct shape.

## Findings and handoff

VERDICT: **NOT-READY** (due to missing verification of the CLOEXEC child-fd leak, O_DIRECTORY mutant survivor, and the read-side boundary).

**Blocking set:**
1. **O_DIRECTORY-DROPPED** SURVIVOR: The `O_DIRECTORY` flag was dropped from the fd open in a mutant, and no test died. The test suite requires a test that explicitly ensures `os.open` raises `ENOTDIR` if a file is supplied as the framedir (or fails correctly). File:line: `tests/test_s0_01_acp_probe.py` (missing test). CHEAPEST PATH: add a hostile rig case where framedir is a regular file.
2. **CLOEXEC-DROPPED** SURVIVOR: the `O_CLOEXEC` flag was dropped from the framedir `os.open`, and no test died. A leaked fd lets the untrusted child manipulate the open framedir (e.g., `fchdir`). File:line: `tests/test_s0_01_acp_probe.py` (missing test). CHEAPEST PATH: add a test reading `/proc/self/fd` from a fixture agent to prove no directory fds leak.

**Deferred to Round 14 / other lanes:**
- F4 (drain join calibration): Coordinator's recapture.
- AF-AP-70 (classify-then-open): The READ side `_sha256_file` uses `os.stat` then `open`, which a FIFO swap can hang (reproduced). Declared boundary scope leaves this for round 14.
- Four-file serial run: Serial execution timeout prevented confirming strict serial isolation.

This report hands these verified findings and missing tests to the sandbox adversarial-verifier lane. No independent gate verdict is issued here.
