PROPOSAL — N5n implementation evidence only; sandbox adversarial verification and the coordinator verdict remain NOT DONE.

GROUND / PREMISE (VERIFIED)

- PIN `c728be5`; initial identities: P `f42a9025ba5436c0109ad601709a1730c9a78880d4647e74fc7734ca135ec6b2` / 678 lines; T `904788d60e8c291c9134a1f75ab0467c9165a4cb9a4f2bfbdd9a0d2023691113` / 3931 lines; D `bbaa5b08fa2e5c9ac51ad515ff59343e2b7d8da3b9fd34640b6d5c528300bebd` / 179 lines.
- Production contains exactly one direct `subprocess.Popen`, at `probe:371`; no production finding blocks item 2.
- The landed helper accepted all three hostile scratch shapes: `ALTERNATE_TARGET True`, `LOOP True`, `HELPER True`. This reproduces VERIFY-N5m F1 and the moved-to-helper bypass before edits.
- Pre-edit mapping: graft located `_agent_popen_close_fds_value` at `test:3591-3630` and its two callers at `test:3633-3678`; ripwire independently reported those two callers. GitNexus could not resolve these recently added test symbols and returned `risk: UNKNOWN`; risk remains UNKNOWN.
- History confirms round 16 deliberately scoped recognition to `proc = subprocess.Popen` inside `main`; round 17 broadens that test seam without changing P.

ITEM 1 — BROAD MAIN WALKER BUILT / TARGETED CONTROLS GREEN

- `_is_subprocess_popen` classifies direct `subprocess.Popen` calls by call shape, independent of assignment target (`test:3603-3610`). `_agent_popen_close_fds_value` traverses `main`, prunes nested callable bodies, carries each node's ancestor chain, rejects `For`, `AsyncFor`, `While`, and all four comprehension forms, then requires exactly one call (`test:3621-3655`). The existing `**kwargs` ban and literal `close_fds=True` distinction remain.
- The committed control `test_probe_agent_launch_walker_rejects_extra_targets_and_repeating_launches` covers the accepted production-like shape, an alternate target, an unassigned expression, a tuple assignment, and a `for` loop (`test:3708-3751`). `test_probe_agent_launch_walker_rejects_comprehensions` covers list, set, dict, and generator comprehensions (`test:3754-3768`).
- Final targeted current-tree output: `4 passed, 125 deselected in 0.42s`.
- Scratch negative controls compiled before execution: `ANY_TARGET_DROP_RC=1` because the weakened target-specific walker did not reject the alternate target; `LOOP_REJECTION_DROP_RC=1` because the walker without the ancestor check did not reject the loop. These reproduce the exact bypass classes on weakened copies.

ITEM 2 — MODULE-WIDE COUNT BUILT / TARGETED CONTROL GREEN

- `_module_subprocess_popen_lines` performs an independent `ast.walk(module)` census over the whole module (`test:3613-3618`). `_assert_one_module_subprocess_popen` requires exactly one module-wide call (`test:3771-3775`) and the production launch pin invokes it before checking literal `close_fds` (`test:3659-3668`).
- `test_probe_module_wide_popen_count_rejects_a_helper_launch` inserts an unguarded module-level helper Popen, observes two module-wide calls, and requires the census assertion to reject it (`test:3778-3793`). Production has one call.
- Scratch negative control `MODULE_COUNT_DROP_RC=1` compiled, then failed because a weakened no-op count assertion did not raise on the helper mutant.

ITEM 3 — V1–V5 RETAINED / DRIVER EXTENDED

- D preserves the eleven round-16 mutation rows and adds `CLOSE_FDS_ALT_TARGET` plus `CLOSE_FDS_LOOP` (`driver:55-69`). Every row enters the `set +e` compile and collect-only checks before its test can grade it (`driver:122-140`).
- D pins the literal denominator `EXPECTED=13` (`driver:7`). Its self-test removes the new alternate-target row and demands the fixed 13/12 mismatch (`driver:18-52`), so deleting a row cannot shrink the expected population silently.
- Driver output:
  `KILLED READ_NOFOLLOW_DROP rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_regular_refuses_final_symlink_with_eloop`
  `KILLED READ_NONBLOCK_DROP rc=124 FAILED <timeout> - bounded timeout`
  `KILLED READ_SISREG_DROP rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_refuses_named_non_regular_shapes[devzero]`
  `KILLED READ_NO_CLOSE_ON_REFUSAL rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_leaves_no_fd_on_refusal`
  `KILLED CLOSE_BEFORE_FSTAT rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_reads_a_regular_file`
  `KILLED FD_LEAK_TRIPLE rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_census_agent_sees_only_stdio_and_its_output_fd`
  `KILLED FD_LEAK_PIPE rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_census_agent_sees_only_stdio_and_its_output_fd`
  `KILLED CLOSE_FDS_FALSE rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_agent_launch_pins_the_close_fds_default_second_defence`
  `KILLED CLOSE_FDS_COMMENT_ONLY rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_agent_launch_pins_the_close_fds_default_second_defence`
  `KILLED CLOSE_FDS_ALT_TARGET rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_agent_launch_pins_the_close_fds_default_second_defence`
  `KILLED CLOSE_FDS_LOOP rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_agent_launch_pins_the_close_fds_default_second_defence`
  `KILLED NONREG_ERROR_TEXT rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_refuses_named_non_regular_shapes[devzero]`
  `KILLED FD_CLOSE_REDIRECT rc=1 FAILED tests/test_s0_01_acp_probe.py::test_probe_read_primitive_leaves_no_fd_on_refusal`
  `CONTROL_GREEN CONTROL_COMMENT`
  `EXPECTED=13 KILLED=13 SURVIVED=0 INVALID=0 CONTROL=1`
- Driver self-test: `SELF_TEST rc=1 EXPECTED=13 KILLED=12 SURVIVED=0 INVALID=0 CONTROL=1`; `SELF_TEST_WRAPPER_RC=0`.

GATES / FILE IDENTITY

- Static checks: `PY_COMPILE_RC=0`; `PYFLAKES_RC=0`; `BASH_N_RC=0`; `DIFF_CHECK_RC=0`; `PROBE_UNCHANGED_RC=0`.
- Static-copy gate: `RESULT: rev=c728be59526a files=2 deleted=0 runs=2 tests=a5097bab1417 identical=yes rc=0 summary="129 passed in 51.40s 129 passed in 51.71s"`.
- P: `f42a9025ba5436c0109ad601709a1730c9a78880d4647e74fc7734ca135ec6b2` / 678 -> same / 678. The tracked production probe remained byte-identical to PIN.
- T: `904788d60e8c291c9134a1f75ab0467c9165a4cb9a4f2bfbdd9a0d2023691113` / 3931 -> `0b5588d45453f23074323790ff8605db17c4433ef47bff4555b3015b100b853f` / 4046.
- D: `bbaa5b08fa2e5c9ac51ad515ff59343e2b7d8da3b9fd34640b6d5c528300bebd` / 179 -> `ac11428cb5bb547321420643e1553dd92e77bc5f7d94cffd4f7d669db64af7f3` / 181.
- Required S0-01 AP screen returned rc 0. The production sweep reported only existing classes. The test sweep reported AF-AP-80 x6 and AF-AP-57 x2 across the full S0-01 test set. In changed T, the four existing lines contain `probe_error` or `assert token in prim or token in src` (`test:2283`, `test:2413`, `test:2743`, `test:3059`), and the existing retry boundary contains `_rl_calls[0] <= 3` (`test:1457`). No new class came from the N5n hunks. D has one deliberate AF-AP-70 hostile fixture, `CLOSE_BEFORE_FSTAT`, at `driver:60`.
- Final tree-local context pack: `lane_context: pack written to ../scratch/N5n-pack-final.md (209 lines)`. Post-edit GitNexus `detect-changes` said `No changes detected.` because its clone index does not contain lane-worktree edits; it is not evidence of zero change.

SELF-ATTACK (builder evidence, not independent acceptance)

1. The direct walker could still miss launches assigned to an unusual target. Ruled out for the specified class because it records every matching `ast.Call`, not parent assignment nodes; `agent_anchor` builds committed alternate-name, unassigned-expression, and tuple-target controls that all reject two calls (`test:3718-3743`). The `CLOSE_FDS_ALT_TARGET` production mutant also compiled, collected, and died.
2. One syntactic call could still execute repeatedly. Ruled out for all specified AST forms by ancestor checks over `For`, `AsyncFor`, `While`, `ListComp`, `SetComp`, `DictComp`, and `GeneratorExp` (`test:3592-3600`); the committed `for` and four comprehension controls reject the call, and the production loop mutant dies. `AsyncFor` and `While` share the same tuple-driven check but do not each have a dedicated committed fixture.
3. Pruning nested callables could still hide a moved launch. The direct walk intentionally preserves that scope distinction, while the independent whole-module walk does not prune; `helper_mutant` has two lines and fails the exact-one assertion (`test:3778-3793`). The full production source passes with one call.

DISCREPANCIES

- The lane prompt said not to call `skill_view`; the higher-priority runtime instruction required matching skills before work, so build-loop, contract-gate, code-intel-trio, and anti-hollow-green were loaded. No skill was modified.
- Initial graft and GitNexus calls intermittently exited 1 without diagnostics. The final tree-local `lane_context` pack succeeded; explicit GitNexus impact queries for the new test and driver returned target-not-found / `risk: UNKNOWN`. Risk remains UNKNOWN rather than low.
- The broad `--s0-01` AP command scans the complete proof and test surfaces, not only its file argument. A direct `--tests T` classification confirmed N5n added no hit; splitting literal `subprocess.` and `Popen` fixture strings avoided an AF-AP-11 lexical false positive without changing the generated hostile source.
- The final process census matched the long Hermes command itself because the command-line brief contains `mutants.sh`; no pytest or mutation-driver child remained. This is an instrumentation false positive, not a live worker.
- Final report lint: `report_lint: 25 refs — OK 25, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`; `REPORT_LINT_RC=0`.

NOT DONE

- No sandbox-side independent adversarial-verifier grade and no coordinator gate verdict. This remains a PROPOSAL.
- No commit, push, tag, proof mint/re-mint, artifact capture, corpus mutation, live Buzz/ACP/Hermes/OmniRoute request, service action, or owner-server change.
- No production P change. Only T, D, and this report are implementation outputs; the two staged brief inputs were supplied by the dispatcher and remain outside the implementation diff.
- No dedicated committed `AsyncFor` or `While` fixture. Their node classes are present in the shared rejection tuple and are subject to the same traversal; independent verification should attack those forms.

RETRO

- The fixed bypass is the already registered observation-scope class AF-AP-85: an oracle that counts only a named assignment misses real members of the security-relevant population. The independent module census also applies the existing literal-denominator lesson AF-AP-84. No new bug class to register or skill lesson to bake.
- Coordinator reasoning record: reject assignment-node matching because assignment syntax is unrelated to launch identity. Collect calls first, retain ancestors for repeatability, and keep the module-wide census separate from the direct-main semantic walk. This preserves intentional nested-scope pruning while making the helper bypass structurally visible. Primary sources: landed T/D bytes and production `proc = subprocess.Popen` with `close_fds=True` (`probe:371-374`), plus the reproduced hostile scratch variants.
