COORDINATOR DISPOSITION (2026-09-15, landed): ACCEPTED as probe round 16. Independent sandbox gates reproduced: static-copy `RESULT: rev=2c7ed47ab315 files=2 deleted=0 runs=2 tests=a5097bab1417 identical=yes rc=0 summary="126 passed in 47.75s 126 passed in 47.54s"`; driver `EXPECTED=11 KILLED=11 SURVIVED=0 INVALID=0 CONTROL=1`; self-test `SELF_TEST rc=1 EXPECTED=11 KILLED=10 ... CONTROL=1` wrapper rc 0; report_lint 20 refs OK 19 NEAR 1 (with the probe/test/driver maps); AP-screen delta on the changed test = 0 new hits. File identities match this report (T 904788d6/3931, D bbaa5b08/179; P unchanged). No production change. NEXT: VERIFY-N5m (cloud verify, findings-only by the single-model rule). F4 real-leg recapture stays the coordinator's.

PROPOSAL — N5m implementation evidence only; sandbox adversarial verification and the coordinator verdict remain NOT DONE.

GROUND / PREMISE (VERIFIED)

- PIN `2c7ed47`; relevant P/T/D bytes equal landed round 15 (`8b387d2`). Initial identities: P `f42a9025ba5436c0109ad601709a1730c9a78880d4647e74fc7734ca135ec6b2` / 678 lines; T `6d5da2b2ed0da69b931328f29c4193dab79c558d59b3494e212a45a5ed2d65e5` / 3868 lines; D `376105ab9258fa44608b2021ac6601c99cae06f40d9c70d9d7334e9c371b39bd` / 141 lines.
- F1 reproduced through a scratch copy of production `main`: one inheritable non-framedir pipe plus `close_fds=False` returned `F1_REPRO_RC=0 F1_OLD_CENSUS='CENSUS=0'`.
- F2 reproduced against `_agent_popen_close_fds_value`: a safe nested helper plus the one top-level launch returned `F2_REPRO=expected one agent Popen assigned to proc, got 2`.
- F3 reproduced with one driver row deleted: rc 0 and `EXPECTED=9 KILLED=9 SURVIVED=0 INVALID=0 CONTROL=1`.
- F4 reproduced: a forced assertion after `_short_unix_socket_path()` left one new directory, `F4_REPRO_DELTA=['/tmp/n5l-sock-3m2mbqqs']`; this lane removed that exact owned directory.
- Existing controls were green before edits: `3 passed, 121 deselected in 0.48s`.
- Pre-edit mapping: graft mapped production `main` at `probe:253-674` and test helpers at `test:257-258` / `test:3591-3630`; ripwire found one caller of `_agent_popen_close_fds_value` and two of `_short_unix_socket_path`. GitNexus clone index was 128 commits stale and could not resolve the three new test symbols; its disambiguated production `main` candidate reported one direct impacted symbol / LOW, so UNKNOWN remains for the new test symbols.

ITEMS 1-4 — BUILT / TARGETED CONTROLS GREEN

- Item 1, T only: `_CENSUS_AGENT` at `test:3873-3902` now opens its output before enumeration, records every stable `/proc/self/fd` readlink as `FD=<n> TARGET=<target>`, and computes `CENSUS` against exactly `{0,1,2,output fd}`. `test_probe_census_agent_sees_only_stdio_and_its_output_fd` at `test:3905-3931` requires the exact fd set `{0,1,2,3}`, pipe/tty stdio targets, the identity of fd 3, and `CENSUS=0`. The independent scratch FD_LEAK_PIPE control through copied production `main` emitted fd 0-2 pipes, fd 3 census output, fd 4 pipe, and `CENSUS=1`. The D row at `driver:61-62` retains `FD_LEAK_TRIPLE` and adds `FD_LEAK_PIPE`.
- Item 2, T only: `_agent_popen_close_fds_value` at `test:3591-3630` traverses `main` while pruning nested `FunctionDef`/`AsyncFunctionDef`/`Lambda` scopes. Its new control at `test:3657-3678` accepts one nested helper launch plus one guarded main launch and rejects two main launches with `expected one agent Popen assigned to proc in main, got 2`. The old bytes red reproduced as `expected one agent Popen assigned to proc, got 2`; new targeted output: `2 passed, 124 deselected in 0.07s` for item 2 + item 4 controls.
- Item 3, D only: literal `EXPECTED=11` at `driver:7` is independent of observed rows; the terminal condition at `driver:176-179` requires `killed == EXPECTED`, zero survivors/invalid rows, and one green control. `--self-test` at `driver:18-52` deletes `FD_LEAK_PIPE` in a scratch copy and returned `SELF_TEST rc=1 EXPECTED=11 KILLED=10 SURVIVED=0 INVALID=0 CONTROL=1`; wrapper rc 0 confirms the self-test recognized that expected rejection.
- Item 4, T only: `_short_unix_socket_path` is a context manager whose `finally` removes any created leaf and its `/tmp/n5l-sock-*` directory. Both callers now keep their whole allocated-path body inside it. The committed forced-failure control compares `Path('/tmp').glob('n5l-sock-*')` before/after and returned green. The old bytes independently printed `OLD_F4_LEAK=True`; this lane removed that exact owned directory.
- Combined targeted output after fixes: `5 passed, 121 deselected in 0.52s`.
- P remains unchanged. No production behavior was modified.

ITEM 5 — GATES / IDENTITIES

- Probe set id: `1 files set=a5097bab1417`.
- Probe run 1: `pytest-summary: 126 passed in 51.46s` (`pytest-exit: 0`).
- Probe run 2: `pytest-summary: 126 passed in 51.12s` (`pytest-exit: 0`).
- Static-copy gate 1: `RESULT: rev=2c7ed47ab315 files=2 deleted=0 runs=1 tests=a5097bab1417 identical=yes rc=0 summary="126 passed in 51.44s"`.
- Static-copy gate 2: `RESULT: rev=2c7ed47ab315 files=2 deleted=0 runs=1 tests=a5097bab1417 identical=yes rc=0 summary="126 passed in 51.68s"`.
- Driver full output:
  `KILLED READ_NOFOLLOW_DROP rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_regular_refuses_final_symlink_with_eloop`
  `KILLED READ_NONBLOCK_DROP rc=124 FAILED <timeout> - bounded timeout`
  `KILLED READ_SISREG_DROP rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_refuses_named_non_regular_shapes[devzero]`
  `KILLED READ_NO_CLOSE_ON_REFUSAL rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_leaves_no_fd_on_refusal`
  `KILLED CLOSE_BEFORE_FSTAT rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_reads_a_regular_file`
  `KILLED FD_LEAK_TRIPLE rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_census_agent_sees_only_stdio_and_its_output_fd`
  `KILLED FD_LEAK_PIPE rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_census_agent_sees_only_stdio_and_its_output_fd`
  `KILLED CLOSE_FDS_FALSE rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_agent_launch_pins_the_close_fds_default_second_defence`
  `KILLED CLOSE_FDS_COMMENT_ONLY rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_agent_launch_pins_the_close_fds_default_second_defence`
  `KILLED NONREG_ERROR_TEXT rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_refuses_named_non_regular_shapes[devzero]`
  `KILLED FD_CLOSE_REDIRECT rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_leaves_no_fd_on_refusal`
  `CONTROL_GREEN CONTROL_COMMENT`
  `EXPECTED=11 KILLED=11 SURVIVED=0 INVALID=0 CONTROL=1`
- Driver self-test: `SELF_TEST rc=1 EXPECTED=11 KILLED=10 SURVIVED=0 INVALID=0 CONTROL=1`; wrapper rc 0.
- Joint set: `13 files set=c62435272c99`; `pytest-summary: 1354 passed, 13 xfailed in 230.14s (0:03:50)` (`pytest-exit: 0`). This is +2 passed versus round 15, matching the two added tests.
- Static gates: `PYFLAKES_RC=0 BASH_N_RC=0 DIFF_CHECK_RC=0`.
- T AP screen: 5 pre-existing-class hits: AF-AP-80 x4 at pre-existing source/inventory assertions (`test:2282` / `test:2412` / `test:2742` / `test:3058`, whose line contains `assert token in prim or token in src`) and AF-AP-57 x1 at pre-existing `test:1456` (`if _rl_calls[0] <= 3:`). The four AF-AP-80 hits are source/inventory pins retained by design and backed by behavioral controls elsewhere; no new AP class. The `assert "probe_error" not in json.loads((control / "runtime-identity.json").read_text())` at `test:2282` is unrelated and explicitly not evidence for this N5m result. D has one deliberate AF-AP-70 mutation fixture at `driver:60` (`CLOSE_BEFORE_FSTAT`).
- Post-edit GitNexus `detect-changes`: `Changes: 4 files, 1 symbols`; `Affected processes: 0`; `Risk level: low`. The clone index misclassified the test-file change as `test_probe_result_response_and_check_initialize`, so the final pack is the exact tree map; its ripwire pass reports two helper callers and three socket-path callers.

FILE IDENTITY (BEFORE -> FINAL)

- P: `f42a9025ba5436c0109ad601709a1730c9a78880d4647e74fc7734ca135ec6b2` / 678 -> same / 678; `git diff --quiet 2c7ed47 -- P` rc 0.
- T: `6d5da2b2ed0da69b931328f29c4193dab79c558d59b3494e212a45a5ed2d65e5` / 3868 -> `904788d60e8c291c9134a1f75ab0467c9165a4cb9a4f2bfbdd9a0d2023691113` / 3931.
- D: `376105ab9258fa44608b2021ac6601c99cae06f40d9c70d9d7334e9c371b39bd` / 141 -> `bbaa5b08fa2e5c9ac51ad515ff59343e2b7d8da3b9fd34640b6d5c528300bebd` / 179.

SELF-ATTACK (builder evidence, not independent acceptance)

1. The general census could still ignore a non-framedir fd. Ruled out for the motivating class by the real copied Popen path: the explicit inherited pipe appeared as fd 4 / `pipe:[…]`, produced `CENSUS=1`, and both `FD_LEAK_PIPE` and retained `FD_LEAK_TRIPLE` died at test:3905.
2. Pruning nested helpers could accidentally skip a guarded launch under `try`/`if`, or include other nested callable scopes. The production launch under `try` remained detected; scratch `main_if`, nested `async def`, and nested `lambda` controls each returned literal `True`; the committed nested-function control stays green while its second-main-launch `pytest.raises(AssertionError, match=r"in main, got 2")` arm dies at `test:3677`.
3. The denominator self-test could itself accept a weakened literal. A scratch `EXPECTED=10` mutant returned inner rc 0 / `EXPECTED=10 KILLED=10 …`, but the outer self-test exited 1 because it requires the literal `EXPECTED=11 KILLED=10 …`. The full unchanged driver returned 11/11 with one control.

DISCREPANCIES

- The lane prompt said not to call `skill_view`; the higher-priority runtime instruction required loading matching skills, so build-loop, contract-gate, anti-hollow-green, and code-intel-trio were loaded. No skill was modified.
- `search_files` treated a pattern beginning with `--self-test` as an rg option and returned `rg: unrecognized flag`; graft/ripwire had already run first, and no code conclusion relied on that failed literal sweep.
- The first F1 old-test invocation put the extracted test outside a repo-shaped root, so `_run_probe` targeted a missing probe and red before the census. I discarded that result and ran the new census agent through a copied landed production probe; it returned fd 0-3 and `CENSUS=0`.
- The first FD_LEAK_PIPE control's postcondition subtracted the wrong output-fd number after its output showed the true set; the production result itself was valid. I corrected only the scratch assertion and reran it to rc 0 with the same inventory shape and `CENSUS=1`.
- Two intermediate targeted runs exposed mistakes in the new AST fixture (one traversal-scope error, then one indentation anchor and one overly strict pytest message regex). These were development reds, fixed before the pasted green gates; no premise reversal occurred.
- GitNexus used the clone index, 128 commits stale, and could not resolve the new test symbols. `detect-changes` returned low risk but misnamed the changed symbol; the tree-local graft/ripwire pack is the final structural map. Risk for unresolved symbols remains UNKNOWN rather than low.
- Final report lint: `20 refs — OK 19, NEAR 1, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`; rc 0. The one NEAR is the deliberate adjacent mapping claim at report line 11; it refers to the `@contextmanager` seam immediately after the cited helper range.

NOT DONE

- No sandbox-side independent adversarial-verifier grade and no gate verdict. This remains a PROPOSAL.
- No commit, push, tag, proof mint/re-mint, artifact capture, corpus mutation, live Buzz/ACP/Hermes/OmniRoute request, service action, or owner-server change.
- No production P change; round 15 production bytes remain exact.
- No tracked project source, test, or brief file outside the P/T/D/report boundary was edited. Scratch controls and the mandated lane report draft are outside that tracked boundary; the two staged brief inputs remain untouched by this implementation.

RETRO

- The fixed F1/F3 defect classes were already registered as AF-AP-85 and AF-AP-84. The class sweep found no new occurrence inside this boundary: D now has a literal denominator/self-test and the named general census enumerates the full fd population. No new bug class to bake.
- Reasoning record for coordinator: reject renaming the census to a framedir-only claim because the brief requires a general property; enumerate every stable fd and compare against the explicit expected set. Scope the AST walk to production `main` while recursively covering its control-flow bodies, pruning only nested callable definitions. Use a context manager for fixture lifetime so teardown runs on every exit. Primary sources: landed P/T/D bytes and VERIFY-N5l's real counterexamples.
