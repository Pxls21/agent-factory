Outcome: FINDINGS ONLY. Single-model rule: no merge verdict.

VERIFY-N5m — S0-01 probe round 16 adversarial findings

Scope and method

Verified on PC against PIN `f911bd0`, using scratch copies only. The landed test set ran clean: `126 passed in 51.07s`; one-file set `a5097bab1417`. The production probe is unchanged: `git diff --quiet f911bd0 -- proofs/S0-01/tools/acp_probe.py` returned `0`.

Reproduced dynamically: census generality; AST scanner attacks; driver row/denominator attacks; socket cleanup on normal, early-return, and `KeyboardInterrupt` paths; the 11-row driver; and the driver self-test. Reviewed statically: the scoped AST walker and both socket-fixture callers.

Findings

1. BLOCKER — the close-fds AST gate permits extra real launches.

`test:_agent_popen_close_fds_value` only recognizes assignments whose target is exactly `proc` and whose callee is exactly `subprocess.Popen` (`test:3606-3615`). Its `ast.iter_child_nodes` traversal prunes nested `FunctionDef`, `AsyncFunctionDef`, and `Lambda` bodies at `test:3601-3605`. The exact-one assertion sits at `test:3617-3618`; `close_fds` is accepted as the literal `True` only at `test:3623-3630`.

A scratch production mutation adding `sidecar = subprocess.Popen([agent], close_fds=False)` before the guarded agent launch returned `True`; the committed static gate also stayed green when run against the mutant: `1 passed, 125 deselected`. A loop around the guarded `proc = subprocess.Popen(... close_fds=True)` likewise returned `True` and the committed gate stayed green, although it launches the agent twice at runtime.

Minimal fix: enumerate all reachable `subprocess.Popen` call expressions in top-level `main` regardless of assignment target; reject loop-contained launches and every extra call. If the contract protects all child processes, follow aliases/partials or add runtime fd-census coverage for each child.

Reproduced controls

- V1: `test:_CENSUS_AGENT` enumerates `/proc/self/fd` at `test:3879-3888`; `test:test_probe_census_agent_sees_only_stdio_and_its_output_fd` requires exact inventory `{0,1,2,3}` at `test:3920-3931`. A scratch copy inherited pipe read/write, high fd `97`, directory fd, `O_PATH` fd, and eventfd with `close_fds=False`; the real census agent reported `CENSUS=5`, extras `FD=4,5,6,7,97`. This supports census generality.

- V2: `test:test_probe_agent_launch_pin_ignores_a_nested_helper_but_rejects_two_main_launches` checks the nested-helper and two-main-launch shapes at `test:3657-3678`. Direct extra `proc` launches in `if`, `try`, and `with` were rejected. The scanner intentionally prunes nested helpers; a called helper with an unguarded sidecar is invisible. Aliased/partial launches are rejected as no recognized guarded launch, not classified as their own launch forms.

- V3: `driver:7` is literal `EXPECTED=11`; `driver:18-52` copies then deletes the `FD_LEAK_PIPE` row. Lowering literal `EXPECTED` to 10 caused the self-test driver to produce `rc=0 EXPECTED=10 KILLED=10 ...`; its outer self-test returned `1`, so the weakened-denominator control is effective. Adding an undeclared extra control row gave `SURVIVED=1` and driver rc `1`.

- V4: `test:_short_unix_socket_path` cleans children and directory in its `finally` at `test:259-266`; `test:test_probe_socket_fixture_cleans_up_after_failure` guards an exception at `test:3777-3786`. It left no `/tmp/n5l-sock-*` directory on normal, early-return, or `KeyboardInterrupt`; both production callers are inside `with` bodies (`test:3773-3774`, `test:3807-3817`).

- V5: `driver:121-139` makes compile or collect failure `INVALID`; `driver:177-179` requires no survivor or invalid row. With an absolute scratch output directory, driver output was `EXPECTED=11 KILLED=11 SURVIVED=0 INVALID=0 CONTROL=1` and rc `0`.

- V6: P sha256 `f42a9025ba5436c0109ad601709a1730c9a78880d4647e74fc7734ca135ec6b2`, 678 lines; T sha256 `904788d60e8c291c9134a1f75ab0467c9165a4cb9a4f2bfbdd9a0d2023691113`, 3931 lines; D sha256 `bbaa5b08fa2e5c9ac51ad515ff59343e2b7d8da3b9fd34640b6d5c528300bebd`, 179 lines.

- V7: probe-file suite repeated by `scripts/test_summary.sh`: `126 passed in 51.07s`, set `a5097bab1417`. The attempted 13-file list from the brief does not exist at this PIN: seven named paths are absent, so pytest exits `5` before collection. A corrected broad run was attempted but exceeded the 420 s terminal cap; no result is claimed.

- V8: AP screen ran. The test-file classifications are AF-AP-80 four pre-existing substring/assertion checks, AP-66 one pre-existing timer daemon, AF-AP-57 one pre-existing bounded retry. No round-16-specific new hit was identified.

Discrepancies

- The brief describes the self-test as having a nonzero inner driver rc. Measured behavior is intentional and correct: the copied driver exits `1` (`SELF_TEST rc=1 ...`) and the outer `--self-test` wrapper exits `0` after verifying that exact failure. No product finding.

- The brief’s 13-file V7 list names seven absent files at `f911bd0`; `pytest -n 8` returned `no tests ran`, rc 5. The actual repository has 13 `tests/test_s0_01_*.py` files, but they are a different list.

- Driver runs with relative `N5L_MUTANT_DIR=../scratch/...` fail spuriously because each archive tree resolves `--basetemp` under its own cwd. Absolute output paths work. This is a verification harness invocation constraint, not a product finding.

- GitNexus `impact` did not index the round-16 test symbols and returned `risk UNKNOWN`; ripwire supplied caller results. No code edits were made.

- `report_lint` final: `15 refs — OK 15, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.

Not done

- No full corrected 13-file run is claimed: the brief list is invalid and the corrected broad run exceeded this terminal’s 420 s cap.

- No live model, relay, capture, or production service was touched.

- No independent merge verdict: findings require coordinator disposition and a subsequent independent verifier after repair.

Hygiene and retro

- Process census after timed gates found no `pytest` or `xdist` worker from this lane. An unrelated VERIFY-GOV1 Hermes lane was live and untouched.

- Worktree hygiene: `git diff --check` passed. The only lane changes are the two staged dispatcher brief files and the untracked report; no product source was changed.

- Retro: coordinator should run `/bug-echo` for this narrow-AST-recognizer class before closing the repair increment.

Gate evidence

- `python3 -m pyflakes tests/test_s0_01_acp_probe.py`: rc 0.

- `git diff --check f911bd0 -- <P,T,D>`: rc 0.

- `python3 scripts/ap_screen.py --s0-01 tests/test_s0_01_acp_probe.py`: rc 0; classifications above.

- `node ... gitnexus ... detect-changes --scope all`: `No changes detected.`

File identity

P `proofs/S0-01/tools/acp_probe.py`: `f42a9025ba5436c0109ad601709a1730c9a78880d4647e74fc7734ca135ec6b2`, 678 lines, unchanged from `f911bd0`.

T `tests/test_s0_01_acp_probe.py`: `904788d60e8c291c9134a1f75ab0467c9165a4cb9a4f2bfbdd9a0d2023691113`, 3931 lines.

D `tasks/briefs/s0-01-n5l-support/mutants.sh`: `bbaa5b08fa2e5c9ac51ad515ff59343e2b7d8da3b9fd34640b6d5c528300bebd`, 179 lines.

Saved: `tasks/briefs/s0-01-n5l-support/VERIFY-N5m-report.md`

🌱 graft saved ~46,744 tokens this turn
