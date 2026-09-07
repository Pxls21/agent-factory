# SWEEP-tests — every defect CLASS over every S0-01 TEST file, every instance RUN

**Graded sha:** `fffb5116bd95f76428c8fd996a8687ff44ff20c8` (recorded at dispatch), extracted with
`git archive fffb511 | tar -x -C <scratch>/arch`. The shared tree advanced to
`6b8c9d1f88c337292a825fea19620de2081ee750` (lane A5j + registry commits) while this lane ran; I re-checked
every file in my set with `git show <sha>:<file> | sha256sum` — **all 15 are byte-identical at fffb511 and
6b8c9d1**, so every finding below holds at the current HEAD too. The working tree also carries uncommitted
A5j edits to `tests/test_s0_01_check_acp_conformance.py`; those bytes were NOT graded.

**Baseline (mine, verbatim):**
`1274 passed, 9 skipped, 1 xfailed in 1504.47s (0:25:04)` — 1284 collected,
`S0_01_VENUE=sandbox S0_01_REAL_LEG_DIR=/root/s0-01-realleg/golden`, all 15 files.

**Box load — every timing below is contended.** 4 cores shared with the A5j build lane and two other verifier
lanes running scratch suites. `uptime` load average at the start of each run is stated inline; over this lane it
ranged **0.75 → 8.29**. Wall times are therefore upper bounds and not comparable between runs.

**Method.** Enumeration by AST where the shape allowed (classes 3, 17, and the consumer-set intersection for
class 1), by grep otherwise. Every row was RUN: a defect row is proven by a mutant that stays green (or a hang,
or a loud failure that names the wrong thing); a SAFE row is proven by executing the guard and showing the loud
failure. All mutation was on scratch copies under the session scratchpad; the shared tree got read-only git
only (`git status` / `git log` / `git show`), no stash/checkout/restore/reset/add/commit/push. Only processes I
started were killed, PID-targeted.

---

## THE TABLE

Legend: **D** = DEFECT · **S** = SAFE (guard named) · **DL** = DOCUMENTED-LIMIT · **E** = EQUIVALENT/redundant.

### Class 1 — Presence-gated checks (AF-AP-40) — 67 gating `if` forms / 99 presence predicates

| # | file:line | V | the run that proves it | minimal fix | exact red test |
|---|---|---|---|---|---|
| 1.1 | `tests/test_s0_01_frame_tee.py:185,192,197,202` (`_run_tee` collector: `timeline`←`[]`, `c2a_bytes`←`b""`, `a2c_bytes`←`b""`, `identity`←`{}`) | **D** | **R19** — patched `proofs/S0-01/tools/frame_tee.py` to unlink the four evidence files immediately before each `os._exit()` (`:469`, `:478`). **Instrument verified first**: a manual tee run leaves only `tee-status.json` in the framedir, rc 0 unchanged (an earlier `atexit` version of the same mutant did NOT fire — `os._exit` bypasses atexit — and I discarded its `101 passed` as a null result; see 18.4). Then `pytest tests/test_s0_01_frame_tee.py -v --tb=no` → **`41 failed, 60 passed in 188.78s`** (load 2.81). Cross-referencing the 60 survivors against the collector's four keys gives **7 tests that pass while the tee produced no evidence at all** (row 1.2). | Raise instead of defaulting: `assert tl_path.is_file(), "tee wrote no timeline.jsonl"` (same for the three others) — the collector already knows the run is supposed to produce them. | The 7 tests of row 1.2 must go red under the R19 mutant. |
| 1.2 | the 7 — `TestTimeline::test_has_t_utc_and_t_mono` (FT:243), `TestTimeline::test_t_mono_non_decreasing` (FT:250), `TestDirectionalEqualsTimeline::test_c2a_split` (FT:302), `::test_a2c_split` (FT:305), `TestTimestampsAreReal::test_t_utc_within_fixture_window` (FT:729), `::test_t_utc_increases` (FT:738), `TestMonoNsWindow::test_t_mono_ns_within_monotonic_window` (FT:746) | **D** | same run — all seven drive the tee through `_run_tee`/`tee_run` (`subprocess.run` to completion), so the mutant provably fired for each. Mechanism, verbatim from the source: `for e in tee_run["timeline"]: assert ...` and `for i in range(1, len(monos)): ...` are **vacuous over an empty list**; `assert self._timeline_split(tee_run,"c2a") == tee_run["c2a_bytes"]` is `b"" == b""`. The de-vacuoused sibling one method up (`test_seq_strictly_increasing`, FT:233, `assert len(tl) > 0, "timeline is empty"`) **dies** under the same mutant — the fix pattern is already in the file, three lines away. | Copy FT:233's guard: `assert len(tl) > 0` / pin the exact counts (`test_c2a_count` pins 3, `test_a2c_count` pins 5 — those two die correctly). | Under R19 each of the 7 must fail; `test_seq_strictly_increasing` is the control that already does. |
| 1.2b | **my own experiment's 8 non-results**, stated so nobody counts them: `test_write_failure_exit_70` (FT:975), `test_bounded_write_errors_dedup` (FT:1176), `test_c2a_directional_enospc_eof_agent_exits_70` (FT:1413), `test_a2c_directional_close_error_recorded` (FT:1445) — their only reference to a wiped name is an `os.symlink("/dev/full", framedir/<name>)` **target**, not a read, so the wipe cannot touch them; `test_initial_status_before_first_frame` (FT:1234) — a docstring mention only; `test_sigterm_kills_agent_child` (FT:2913) — reads `runtime-identity.json` *while the tee is alive* and asserts its presence loudly (`assert identity is not None, "runtime-identity.json never appeared"`); `test_sigkill_leaves_nonfinal_status` (FT:1859) and `test_directional_trails_timeline_after_sigkill` (FT:2043) — both **SIGKILL** the tee, so `os._exit` and therefore the mutant **never run**. | **not a result** | verified by reading each body after the run and by `grep -n "SIGKILL"` in the two kill paths. My first pass reported 15 survivors off a filename-mention heuristic; 8 of the 15 do not exercise the mutant, so the honest number is 7. | — | — |
| 1.3 | `tests/test_s0_01_frame_tee.py:2121,2138,2142,2156` (trial loop: `if not tl_path.exists(): results.append(None); continue`, `if c2a_path.exists()`, `if a2c_path.exists()`, `if sp.exists()`) and `:1923-1925` (`tl_last_seq = 0; if tl_path.exists(): ...`) | **D — static only** | **NOT reproduced.** Both sites live in tests that SIGKILL the tee, where the R19 mutant cannot fire (see 1.2b). Static: with the artifacts absent the trial appends `None` and `continue`s, so `assert dir_c2a <= tl_c2a` / `assert dir_a2c <= tl_a2c` (FT:2148,2150) and the `0 <= lag <= 1` invariant behind `if sp.exists()` (FT:2156-2161) never execute at all; at FT:1923 an absent timeline defaults `tl_last_seq` to 0, which fails open only when `updated_seq` is also 0. | Drop the gates; make absence the failure (`assert tl_path.is_file()`), and assert `results.count(None) == 0` after the loop. | Delete the framedir artifacts from **inside the test** after the SIGKILL (the only route the mutant cannot take) — `test_directional_trails_timeline_after_sigkill` must then fail. |
| 1.4 | `tests/test_s0_01_check_acp_conformance.py:667,721,734,743` (`if p.exists(): p.unlink()` in `test_deletion`, `test_del_negative_file`, `test_del_neg_fixture`, `test_del_identities`) | **E** | **R8** — removed all four gates on the scratch copy (`p.unlink()` / `fp.unlink()` bare) → `pytest -k "test_deletion or del_neg_fixture or del_identities"` → **`26 passed, 334 deselected in 90.45s`** (load 4.1). Every guarded file exists today, so the guard is provably redundant; keeping it means a future bundle-fixture regression silently downgrades the test from "delete then detect" to "already absent, detect". | Delete the four `if …exists():` lines. | With a fixture file removed from `_session_bundle`, the bare `unlink()` must raise `FileNotFoundError` instead of the test passing. |
| 1.5 | `tests/test_s0_01_check_acp_conformance.py:2607,2621,2634,2648,2663,2676,2690,2703,2715,2718,2735,2737,2740,2755,2767,2781,2795,2809,2828,2830,2854,3945,3948` (23 real-leg gates) | — | rolled up into class 10 (rows 10.1–10.4). | | |
| 1.6 | `tests/test_s0_01_frame_tee.py:976,1178,1381,1416,1447,1710,1805,1826` (8 `/dev/full` gates) | — | rolled up into class 10 (row 10.5). | | |
| 1.7 | `tests/test_s0_01_frame_tee.py:584,951,1125,1245,1275,1522,1620,1682,1895,2006,2100,2288,2349,2628` (14 poll-loop `if status_path.exists()`) | **S** | guard named: every one sits inside `while time.monotonic() < deadline:` and is followed by a loud post-loop assertion (e.g. FT:593 `assert loaded, "no a2c frame recorded before the liveness window"`). Executed in the R19 run — 12 of the 14 enclosing tests go **red** when the artifacts vanish, with the timeout assertion as the reason. | none | — |
| 1.8 | `tests/test_s0_01_frame_tee.py:2797,2807,2967,2977` (`/proc/<pid>/stat` existence) | **S** | both branches feed one final assertion (`assert proc_state == "Z"`, FT:2813/2983); absence is treated as "gone" by design and is asserted. Executed: the R12b run produced the loud `AssertionError: agent pid 5834 state S after 2 s, expected Z or gone`. | none | — |
| 1.9 | `tests/test_s0_01_check_acp_conformance.py:517` (`if timeline.jsonl exists: assert PASS else: assert deferred`) | **S** | executed in the baseline: the tracked `proofs/S0-01/evidence/golden/run-1/timeline.jsonl` is present, so `test_real_bundle_cli` takes the `assert r.returncode == 0 and startswith("PASS:")` branch. Both branches assert; neither is silent. | none | — |
| 1.10 | `tests/test_s0_01_check_acp_conformance.py:432` (`for fn in (…): src = FIXTURES/fn; if src.exists(): shutil.copy2(...)` in `_session_bundle`) | **D** (static) | **NOT RUN** — see "What I could not run". Static: a missing repo fixture is silently omitted from every per-test bundle; `test_del_neg_fixture` (row 1.4) then no-ops its unlink and still passes, so the fixture-absence regression is invisible from two directions at once. | `shutil.copy2(FIXTURES/fn, …)` unguarded — the three names are required, not optional. | Remove `proofs/S0-01/fixtures/acp-schema-v1.json` on a scratch copy; `_session_bundle` must raise, not build a degraded bundle. |
| 1.11 | `tests/test_s0_01_frame_tee.py:2214,2946` and `tests/test_s0_01_check_acp_conformance.py:3624` | **S** | executed in R19/R12b: each is inside a bounded poll followed by a loud assertion on the value it guards — `assert sentinel.exists(), "agent did not write sentinel"` (FT:2217) and `assert identity is not None, "runtime-identity.json never appeared"` (FT:2954). (`FT:1925` was in this row in my first pass; it belongs in 1.3 — corrected.) | none | — |

### Class 2 — Reads outside the walk / S_ISREG rule (AF-AP-30 class)

606 read receivers (`read_text(` / `read_bytes(` / `json.load(` / `open(` / `os.readlink(`) across the 15 files.
Roots: (a) `tmp_path` — created by the test itself; (b) the repo tree (`P` / `FIXTURES` / `GOLDEN`); (c)
**`_REAL_LEG_DIR`, operator-supplied via env**. Only (c) is attack surface, and only one test-side read of it
bypasses the checker.

| # | file:line | V | the run that proves it | minimal fix | exact red test |
|---|---|---|---|---|---|
| 2.1 | `tests/test_s0_01_check_acp_conformance.py:2740-2743` — `scan = leg_dir/"process-scan-after.txt"; if not scan.exists(): skip; first_line = scan.read_text().splitlines()` | **D — HANG** | **R11b** — corpus copy with a FIFO at `run-1/process-scan-after.txt`; `pytest -k real_leg_process_evidence` with `timeout 90` → **no output, `real 1m30.008s`, `user 0m0.316s`** (killed by the timeout; blocked, not spinning). Minimal repro: `exists(): True | is_fifo(): True` then `read_text()` → `rc=124 (blocked)` after 12 s. There is no per-test timeout, so this wedges the whole pytest process. | Use the checker's own helper — `cc._require_regular_file(scan, leg, "process-scan-after.txt")` — or `if not scan.is_file(): pytest.fail(...)`. | Plant a FIFO at that path; the test must fail with a named reason in < 1 s. |
| 2.2 | `tests/test_s0_01_check_acp_conformance.py:2626,2640,…` — every real-leg read routed through `cc._load_timeline_raw` / `cc.check_*` | **S** | **R11a** — same corpus with a FIFO at `run-1/timeline.jsonl`; `pytest -k real_leg_timeline` → **`1 failed, 3 passed, 356 deselected in 0.37s`** with `check_acp_conformance.Failure: run-1: timeline.jsonl is not a regular file` (`proofs/S0-01/check_acp_conformance.py:199`). No hang, named reason. | none | — |
| 2.3 | `tests/test_s0_01_check_acp_conformance.py:2607` — `_REAL_LEG_DIR.iterdir()` | **S** | executed in R2a/R2c: `iterdir()` on a non-directory raises `NotADirectoryError` loudly, and the line is preceded by `assert _REAL_LEG_DIR.is_dir()`. | none | — |

### Class 3 — Stale last-artifact reads in tests

113 `[-1]` tokens; **79** are subscripts over an artifact source (`_records(`/`glob(`/`iterdir(`, or a local bound
from one) — AST-enumerated. **77 of 79 carry a count delta** in the same function (`n0 = len(...)` …
`assert len(recs) == n0 + 1`, or `count_before`/`count_after`). Two do not:

| # | file:line | V | the run that proves it | minimal fix | exact red test |
|---|---|---|---|---|---|
| 3.1 | `tests/test_s0_01_check_acp_conformance.py:1223` — `p = sorted(rd.glob("*.json"))[-1]` in `test_route_pairs_evil` | **S** | **R4a** — changed `[-1]` to `[0]` on the scratch copy → `1 failed`: `assert 'failure_reason: run-1: upstream record (GET, /evil) not in allowed set' == '… (POST, /evil) …'`. The expected-reason string **covers the attribute the index selects** (method), so a different `[-1]` fails loudly. Also not a stale-artifact read — `rd` is a static fixture the test did not produce. | none | — |
| 3.2 | `tests/red/test_s0_01_backend_credential_screen.py:80-81` — `def _last_record_text(backend): return _records(backend)[-1].read_text()` | **E — dead** | **R5** — deleted the helper on the scratch copy → `pytest tests/red/test_s0_01_backend_credential_screen.py` → **`200 passed in 76.28s`** (load 5.05). Zero callers; the file's own greps confirm the only occurrence is the `def`. | Delete lines 80-81. | none needed — deletion must leave 200 passed. |
| 3.3 | the other 77 (BCS ×52, `test_s0_01_scripted_backend.py` ×25) | **S** | guard named: count delta. Verified by execution in the baseline and in R5 (`200 passed`) — e.g. BCS:230/235 `n0 = len(_records(backend))` … `assert len(recs) == n0 + 1` before `recs[-1]`. The recordless mutant cannot reach `[-1]` past that assertion. | none | — |
| 3.4 | `tests/test_s0_01_scripted_backend.py:150,153` — `frames[-1]`, `payloads[-1]` | **S** | not artifact reads: both are derived from **one** HTTP response body inside the same statement (`a[1].decode().split("\n\n")`), so `[-1]` is the last SSE frame of that response, not a directory tail. Executed in the baseline. | none | — |

### Class 4 — Negative acceptance assertions

| # | file:line | V | the run that proves it | minimal fix | exact red test |
|---|---|---|---|---|---|
| 4.1 | `tests/test_s0_01_acp_probe.py:1696` — `assert "probe_error" not in rid` (whole test `test_probe_late_sample_clears_early_interpreter_error`, T:1650) | **D** | **R10a** — changed the fake's gate at T:1681 from `_sha_call[0] == 1` to `== 99` so the early sha **never fails** → `1 passed, 52 deselected in 0.26s`. The test has **no positive control that the early error was ever set**; the pure negation is trivially true when nothing failed. | Make the fake record its firing and assert it: write a sentinel in `_early_fail_sha256` and `assert sentinel.read_text() == "1"`, plus gate on the *argument* (`if path == interp_path and not _fired[0]`) instead of the ordinal. | With the gate at `== 99`, the test must fail on the missing sentinel. |
| 4.2 | `tests/test_s0_01_pc_post_scan.py:120` — `assert int(m.group(2)) > 3  # the full table was enumerated` and `:146` — `int(m.group(2)) > 0` | **D** | **R15** — hard-coded `rows=4` in the producer (`proofs/S0-01/tools/pc/pc_post.sh:72`, replacing `rows={len(rows)}`) → **`11 passed in 1.28s`** — the whole file is green while the enumeration header lies about the table it heads. `> 3` / `> 0` cannot express "the full table was enumerated". | One line in `_parse` (T:66-74), covering every caller: `assert int(m.group(2)) == len(rows)`. | With `rows=4` hard-coded, `_parse` must raise on the real 3-process tree (body > 4 rows). |
| 4.3 | `!= MARKER` as an acceptance check | **S (0 live instances)** | grep over the 15 files: **zero** live `assert … != MARKER` assertions. The only hits are the lint's own comment/docstring at BCS:1178-1195. | none | — |
| 4.4 | `tests/red/test_s0_01_backend_credential_screen.py:1180-1195` — `test_no_not_equal_marker_assertions`, the lint that guards 4.3 | **D** | **R6** — appended two live `!= MARKER` acceptance assertions to the same file (`assert MARKER != json.loads(recs[-1].read_text())["body"]` — reversed operands; and `body = …["body"]` then `assert body != MARKER` — variable form) → **`1 passed, 201 deselected`**. **R6b** — put the *canonical* matching form (`assert rec["body"] != MARKER`) into a **third** S0-01 test file (`tests/test_s0_01_negative_contract.py`) → **`1 passed, 199 deselected`**: the lint's file list is hard-coded to two paths (`red_file`, `../test_s0_01_scripted_backend.py`). | Replace the regex+2-file grep with an AST walk over `tests/test_s0_01_*.py` + `tests/red/test_s0_01_*.py`: flag any `ast.Compare` with `ast.NotEq` whose either side resolves to the name `MARKER`. | The two R6 forms and the R6b third file must all be flagged. |

### Class 5 — Substring / tail anchors classifying outcomes — 22 sites

| # | file:line | V | the run that proves it | minimal fix | exact red test |
|---|---|---|---|---|---|
| 5.1 | `tests/test_s0_01_check_acp_conformance.py:2654` — `assert "tee_sha256 mismatch" in result` (`test_real_leg_runtime_identity`, the "ONLY expected failure" gate) | **D** | **R13** — corpus copy with an extra key literally named `tee_sha256 mismatch` in `run-1/runtime-identity.json`. The checker raises the **unrelated** `run-1: runtime-identity.json key set mismatch (extra=['tee_sha256 mismatch'], missing=[])` (printed directly from `cc.check_runtime_identity`) and the test reports **`1 passed, 359 deselected in 0.14s`**. | `assert result == f"{leg}: tee_sha256 mismatch"` — `_chk` emits exactly that shape. | The R13 corpus must make the test fail. |
| 5.2 | `tests/test_s0_01_check_acp_conformance.py:2725` — `assert "manifest timestamps not pre < start < post" in result` | **D (same class, collision not constructed)** | executed against the real corpus in the baseline (the branch is not taken today — `check_manifests` passes). No `check_manifests` reason echoes corpus-controlled text, so I **could not build a collision through the checker**; the shape is nonetheless the same unanchored containment as 5.1 and the exact-equality fix costs nothing. | `assert result == f"{leg}: manifest timestamps not pre < start < post"`. | An injected extra key trick as in 5.1, once any manifest reason echoes corpus text. |
| 5.3 | `tests/test_s0_01_check_acp_conformance.py:2839` — `tail = result.rsplit(": ", 1)[-1]` then `if tail in _KNOWN_XFAIL_REASONS` | **S — collision attempt failed** | **R13b** — corpus with a key named `zz: probe_sha256 mismatch` injected into `negative/runtime-identity.json`. The checker still reported `negative: negative: probe_sha256 mismatch`, tail `'probe_sha256 mismatch'`, and the test stayed **`1 xfailed`**. I also traced the key-set reason by hand: its last `": "` lands before `runtime-identity.json …`, so the injected fragment cannot become the tail. The docstring's claim ("a substring injection cannot widen the gate") held under attack. **Named residual:** the gate is *reason*-scoped, not *check*-scoped — any check emitting `_chk`'s `f"{leg}: {field} mismatch"` for those three fields is xfailed regardless of which check produced it. | optional: pin the producing check as well as the reason. | — |
| 5.4 | `tests/test_s0_01_check_acp_conformance.py:2041` — `assert out.startswith("failure_reason: malformed evidence:")` | **D** | see 8.1 (same run). | | |
| 5.5 | the other 18 (`startswith("failure_reason: run-1: …")` at CK:826, 1110, 1259, 1276, 1287, 1297, 1462, 1904, 2031, 2059; `"in out"` at 1951, 2008, 2260, 3798, 3829, 3907, 3908; `endswith("Z")` at FT:248, 334, 845) | **S** | executed in the baseline (all green) and under R17: each anchor is a long, leg-qualified prefix that names the failing subject, or a format assertion on a timestamp. None is a bare classifier over an open reason space; the R17 checker-crash mutant (which forges the *generic* prefix at 5.4) does **not** satisfy any of them. | none | — |
| 5.6 | `tests/test_s0_01_audit_cp5_controls.py:74` — `stat.rsplit(")", 1)[1].split()[0] == "Z"` | **S** | executed in the baseline (3 passed). `rsplit(")", 1)` is the correct way to skip a `comm` containing `)`; a `startswith`/`split()[2]` form would be the defect and is not used. | none | — |

### Class 6 — Env-domain fail-opens — 37 `os.environ.get(` + 46 `os.environ.copy()`

`copy()` sites build subprocess environments and select no behaviour. Behaviour-selecting reads: 2.

| # | file:line | V | the run that proves it | minimal fix | exact red test |
|---|---|---|---|---|---|
| 6.1 | `tests/test_s0_01_check_acp_conformance.py:2600` — `venue = os.environ.get("S0_01_VENUE", "")` then `if venue in ("sandbox","pc")` | **D** | **R2b** — `S0_01_VENUE="sandbox "` (trailing space), `S0_01_REAL_LEG_DIR` unset → `1 skipped … "S0_01_REAL_LEG_DIR unset and S0_01_VENUE is not sandbox/pc"`. **R2c** — `S0_01_VENUE="Sandbox"` → identical `1 skipped`. Control **R2a** — `S0_01_VENUE=sandbox`, var unset → `1 failed`, `AssertionError: S0_01_VENUE=sandbox but S0_01_REAL_LEG_DIR is unset`. A typo silently demotes a sandbox/pc run to "CI" and retires the whole real-leg declaration. *(Already named as CK11-F16 in `tasks/briefs/s0-01-a5j-support/verify-CK11.md:833`; reproduced here and still live at fffb511/6b8c9d1.)* | `venue = os.environ.get("S0_01_VENUE", "").strip().lower()` + `assert venue in ("", "ci", "sandbox", "pc"), f"S0_01_VENUE={venue!r} is not a known venue"`. | `S0_01_VENUE="Sandbox"` must fail, not skip. |
| 6.2 | `tests/test_s0_01_check_acp_conformance.py:2579` — `_REAL_LEG_DIR = Path(os.environ["S0_01_REAL_LEG_DIR"]) if os.environ.get(...) else None` | **S** | **R2a** — the declaration test fires loudly (see above) and also asserts `is_dir()` and the complete leg set (`_EXPECTED_REAL_LEGS`). Executed with the var set (baseline: 43 passed / 9 skipped over the real-leg selection). **Named residual:** bound at **import**, while `venue` is read at **call** time — `monkeypatch.setenv("S0_01_REAL_LEG_DIR", …)` cannot move it. | none (the residual is documented in CK11) | — |
| 6.3 | the 35 others (`os.environ.get("PATH"/"HOME", "")` ×32 in probe env dicts; `_TEST_PID_FILE` at AP:825; `S0_01_FRAMEDIR`/`S0_01_FRAMEDIR_CHECK` at FT:548/1090/1241/2583/2682 inside generated agent scripts) | **S** | executed in the baseline. None selects a branch in the *test*; the generated-agent reads feed the tee's own validated env contract, whose empty/absent/not-a-directory cases are pinned by exact stderr at FT:795/802/1560/1570/1581. | none | — |

### Class 7 — Lossy decodes on a decision path — 5 sites

| # | file:line | V | the run that proves it | minimal fix | exact red test |
|---|---|---|---|---|---|
| 7.1 | `tests/test_s0_01_frame_tee.py:1820` — `stderr = proc.stderr.decode("utf-8", errors="replace")` then `assert "tee-status.json write failure" in stderr` | **S** | **R16** — junk bytes through the same decode: `b'\xff\xfe frame_tee: tee-status.json write failure: x\n'` → anchor present **True**; `b'…write fail\xffure\n'` → anchor present **False**. A replacement char cannot forge the ASCII anchor, and a junk byte *inside* the anchor correctly breaks the match. The decode does not reach a decision it can corrupt. | none | — |
| 7.2 | `tests/red/test_s0_01_backend_credential_screen.py:195,199,201` (inside `_absent_under_all_normalizations`, :170) — `errors="ignore"` in `unquote_drop`/`unquote_plus_drop` | **S** | these are the **oracle's** deliberate normalisation variants; the file's own docstring at BCS:180 declares them, and the oracle unions them (`_absent_under_all_normalizations`, BCS:170-222) so it is `>=` the implementation on every path. Executed in the baseline and in R5 (`200 passed`) — the union means a dropped byte can only make the oracle *stricter*, never fail-open. | none | — |

### Class 8 — Broad catches in production-shaped test wrappers — 1 site

| # | file:line | V | the run that proves it | minimal fix | exact red test |
|---|---|---|---|---|---|
| 8.1 | `tests/test_s0_01_check_acp_conformance.py:510-511` — `except Exception as exc: return 1, f"failure_reason: malformed evidence: {type(exc).__name__}: {exc}"`, consumed by `test_bad_json_timeline` (T:2036-2041) | **D** | **R17** — made `cc.check_bundle` raise `AttributeError("SWEEP: a checker BUG, not malformed evidence")` on entry, before touching the bundle → `pytest -k test_bad_json_timeline` → **`1 passed, 359 deselected in 2.97s`**. Every exception type is mapped to the same prefix and the test only checks the prefix, so a checker crash (AttributeError/TypeError/KeyError from a refactor) is indistinguishable from the corrupted-JSON case the test claims to prove. | `assert out.startswith("failure_reason: malformed evidence: JSONDecodeError:")` — or full equality on the reason. | The R17 AttributeError mutant must fail the test. |

### Class 9 — Waits and polls — 58 `while` loops, 73 `time.sleep(` calls

| # | file:line | V | the run that proves it | minimal fix | exact red test |
|---|---|---|---|---|---|
| 9.1 | `tests/test_s0_01_scripted_backend.py:66-78` and `tests/red/test_s0_01_backend_credential_screen.py:42-54` — the module-scoped `backend` readiness loop | **D** | **R9a** — made `proofs/S0-01/tools/scripted_backend.py`'s `main()` print to stderr and `exit(2)` at startup → `pytest -k test_bearer_required_exact_401 -x` → `1 failed … ConnectionRefusedError: [Errno 111] Connection refused`, **`real 0m10.582s`** (the full 10 s deadline burned). The loop is success-only: it never checks `proc.poll()`, never asserts readiness after the loop, and `yield`s a dead backend. The server's own `scripted_backend: SWEEP startup failure` is captured in the never-read `stdout=PIPE` and discarded, so the reason points at the test's socket instead of the process that died. | Add the failure signature to the exit condition and a post-loop assertion: `while time.time() < deadline and proc.poll() is None: …` then `assert ready and proc.poll() is None, f"backend failed to start (rc={proc.poll()}): {proc.stdout.read()}"`. | The R9a startup-failure mutant must produce that message, not `ConnectionRefusedError`. |
| 9.2 | same two fixtures — `stdout=subprocess.PIPE` never drained for the process's life | **D (compounding)** | same R9a run: the stderr the fixture needed for the diagnosis was already in an unread pipe. A backend that writes more than the pipe buffer blocks forever. | drain in a daemon thread (the pattern is already in `tests/test_s0_01_frame_tee.py:573-579` (`_drain` + daemon thread)), or `stdout=subprocess.DEVNULL` plus a separate `stderr` capture read on failure. | fill the pipe from the server; the fixture must not wedge. |
| 9.3 | `tests/test_s0_01_acp_probe.py:1681` — `if _sha_call[0] == 1:` — AF-AP-57 ordinal gate inside a fake | **D** | **R10a** (see 4.1) proves the vacuity. **R10b** — the realistic regression (a new `_sha256_file(…)` call added at the top of `acp_probe.main()`, so the ordinal fires on the wrong call) → `1 failed`; that particular reordering is caught **by accident**, because the new call is unguarded and the OSError propagates to rc 1. Any earlier call wrapped in the `try/except OSError` the file already uses at `acp_probe.py:98-102` (`try: … except OSError as exc:` at :100) would go silently green. | gate on the argument + a fired-flag, and assert the flag (see 4.1). | the `== 99` gate must fail the test. |
| 9.4 | `tests/test_s0_01_frame_tee.py:583,950,1124,1274,1521,1619,1681,1894,2099,2213,2287,2348,2765,2945,2966` (bounded polls) | **S** | guard named: each is followed by a loud assertion (`assert loaded, …` FT:593; `assert child_pid is not None, "agent child never appeared"` FT:2773). Executed in R19 — the timeout assertions are exactly the reasons in the 41 failures. | none | — |
| 9.5 | `tests/test_s0_01_frame_tee.py:2005,2627` — `while tee_proc.poll() is None and time.monotonic() < deadline:` | **S** | failure-aware by construction: process death is in the exit condition. Executed in R19/R12b. | none | — |
| 9.6 | `tests/test_s0_01_pc_post_scan.py:103-110` (`_wait_gone`) and `tests/test_s0_01_audit_cp5_controls.py:79-84` | **S** | failure-aware: `raise AssertionError(f"pids still running after kill: {pids}")` on timeout (T:110). Executed in the baseline (11 + 3 passed). | none | — |

### Class 10 — Skips — 48 `pytest.skip(` calls, 1 `pytest.mark.xfail`

| # | file:line | V | the run that proves it | minimal fix | exact red test |
|---|---|---|---|---|---|
| 10.1 | `tests/test_s0_01_check_acp_conformance.py:2612` + the 20 `S0_01_REAL_LEG_DIR unset` / `real leg directory absent` skips | **S — declared** | **R2a** — the declaration mutation: `S0_01_VENUE=sandbox` with the var unset → `1 failed`, `AssertionError: S0_01_VENUE=sandbox but S0_01_REAL_LEG_DIR is unset (real-leg corpus not declared for this venue)`. `test_real_leg_corpus_declared` (T:2597) also asserts `is_dir()` and `_EXPECTED_REAL_LEGS ⊆ present`, so a missing leg **directory** cannot skip silently in the sandbox/pc venue. | none — but see 6.1: the declaration itself is defeated by a venue typo. | — |
| 10.2 | `tests/test_s0_01_check_acp_conformance.py:2740,2743` — `real leg predates scan v2.3 (no enumeration header)` | **D — green by skip, undeclared** | **R3** — `S0_01_VENUE=sandbox S0_01_REAL_LEG_DIR=/root/s0-01-realleg/golden pytest -k "real_leg or real_bundle or tee_status_absent" -rs` → `43 passed, **9 skipped**, 307 deselected, 1 xfailed in 14.74s`, of which `SKIPPED [4] …:2744: real leg predates scan v2.3 (no enumeration header)` — **all 4 positive legs**. Corpus check: `head -1 /root/s0-01-realleg/golden/run-1/process-scan-after.txt` starts with a PID row, not `# process-scan v2.3`. Nothing declares the header requirement, so the real-producer process-evidence proof is 0/4 and rc stays 0. | extend `test_real_leg_corpus_declared` to assert the v2.3 header (and `owned-pids.json`) for every expected leg when `venue in ("sandbox","pc")`. | today's corpus must make that declaration test FAIL, naming the missing header. |
| 10.3 | `tests/test_s0_01_check_acp_conformance.py:3948` — `tee-status.json absent in {leg}` | **D — green by skip, undeclared** | same **R3** run: `SKIPPED [1] …:3949` ×5 — `run-1`, `run-2`, `cancel`, `shutdown`, `two-users`. Corpus check: `ls /root/s0-01-realleg/golden/*/tee-status.json` → *No such file or directory*. `test_ck8_real_leg_tee_status` is 0/5 over the real corpus. | same declaration extension (assert `tee-status.json` present per leg), or retire the test and say so. | as 10.2. |
| 10.4 | `tests/test_s0_01_check_acp_conformance.py:2718` (`baseline manifest absent`), `:2737` (`owned-pids.json` / real v2.2 sample), `:2830` (negative `timeline.jsonl`) | **D — same class, currently not firing** | **R3**: none of the three fired against today's corpus (they are not among the 9 skips), so the content is present — but nothing *declares* it, so a corpus that loses any of the three degrades silently exactly like 10.2/10.3. | same declaration extension. | delete `owned-pids.json` from a corpus copy; the declaration test must fail rather than the leg test skipping. |
| 10.5 | `tests/test_s0_01_frame_tee.py:976,1178,1381,1416,1447,1710,1805,1826` — 8 × `pytest.skip("/dev/full not available")` | **D — green by skip, undeclared** | **R18** — the declaration mutation: repointed the eight predicates at `/dev/full-SWEEP-ABSENT` on the scratch copy → `pytest -k "dev_full or unwritable or write_error or status" -rs` → **`22 passed, 4 skipped, 75 deselected in 98.22s`**, rc 0, reason `/dev/full not available`. Repo-wide grep confirms **nothing** asserts `/dev/full` exists. Every ENOSPC / write-failure proof for the tee silently retires in a venue with a restricted `/dev`. | add a declaration test mirroring `test_real_leg_corpus_declared`: `if venue in ("sandbox","pc"): assert os.path.exists("/dev/full"), "…the write-failure proofs cannot run"`. | R18's repointed predicate must make the declaration test fail, not skip 8 tests. |
| 10.6 | `tests/test_s0_01_check_acp_conformance.py:2820-2845` — `test_real_leg_negative`, `request.node.add_marker(pytest.mark.xfail(strict=True, raises=AssertionError, …))` | **S — can XPASS** | executed: baseline reports `1 xfailed`; **R13b** (`-rxX`) shows the anchored reason `XFAIL … real v2.2 sample: probe_sha256 mismatch (capture predates current probe)`. `strict=True` means a repaired capture (the known reason gone, check passes) turns it into a FAILURE by design — the XPASS path is the intended alarm, and the anchor is the narrow `rsplit` tail of 5.3, not a substring. | none | — |

### Class 11 — World-scoped enumerations in tests (AF-AP-59)

| # | file:line | V | the run that proves it | minimal fix | exact red test |
|---|---|---|---|---|---|
| 11.1 | `tests/test_s0_01_pc_post_scan.py:82-91` — `_split_world`, over the producer's world-scoped `ps -eo` table | **S** | executed in the baseline (`11 passed`) and in **R15** (`11 passed in 1.28s`). The helper asserts the **owned subset exactly** and requires every foreign row to be admissible under the producer's only other rule (it names a pinned path), failing on `unexplained foreign row in the scan body`. The AF-AP-59 incident (PC run 20260907T161133Z) is quoted in its own docstring. | none | — |
| 11.2 | `tests/test_s0_01_frame_tee.py:2765-2772` — `pgrep -P <tee_proc.pid>` | **S** | scoped to the test's **own** child by `-P`, not a world `pgrep -f`. Executed in R19/R12b; the loop's post-assert `assert child_pid is not None, "agent child never appeared"` is loud. | none | — |
| 11.3 | `tests/test_s0_01_audit_cp5_controls.py:71`, `tests/test_s0_01_pc_post_scan.py:97`, `tests/test_s0_01_frame_tee.py:2796,2809,2957,2970,2979` — `/proc/<pid>/stat` reads | **S** | every pid comes from a process the test spawned (`tree` fixture T:43-52; `tee_proc.pid`). Executed in the baseline and R12b. | none | — |
| 11.4 | `tests/test_s0_01_scripted_backend.py:52,100,654,721,1598`, `tests/red/…:28` — `socket.socket()` / `_free_port()` | **D (weak)** | `_free_port()` binds port 0, reads the number, **closes**, and the server binds it later — a TOCTOU. Not independently reproduced; it is the mechanism that turns R9a from a diagnosis problem into a flake under the 8-worker PC gate (a sibling worker can take the port between the two calls, and 9.1 then yields a dead backend silently). | `SO_REUSEPORT` hand-off, or retry-on-bind-failure inside the fixture with the 9.1 post-loop assertion. | bind the port between `_free_port()` and `Popen`; the fixture must fail with a named reason. |

### Class 12 — Signal-handler installs (AF-AP-58)

**Zero installs in the 15 test files** (`signal.signal` appears only inside comments/docstrings and the two guard
tests below). An empty class is a result.

| # | file:line | V | the run that proves it | minimal fix | exact red test |
|---|---|---|---|---|---|
| 12.1 | `tests/test_s0_01_frame_tee.py:2816-2850` — `test_no_statement_between_signal_and_try`, the structural pin on the tee's install→try window | **S — narrow, covered elsewhere** | **R12** — swapped `signal.signal(signal.SIGTERM, _sigterm_handler)` → `signal.SIGUSR1` at `proofs/S0-01/tools/frame_tee.py:221` → the pin **passes** (`1 passed, 100 deselected in 0.05s`): it covers the install's *position*, not *which signal*. **R12b** — the full file against the same mutant → **`10 failed, 91 passed in 194.34s`**: `TestSigtermHandler::test_sigterm_writes_status_and_exits_70`, `…no_deadlock_under_contention`, `TestSigtermStatusVsChecker`, `TestSigtermTerminatesAgent::test_sigterm_kills_agent_child`, `TestEarlySigterm`, `TestZombieGrandchild`, `TestGrandchildStdout`, `TestTeeStatus::test_never_reading_client`, `…test_grandchild_never_closes_sigterm_required`, `TestStdinReaderDoneValue::…`. The signal-identity mutant dies ten times over. | optional: add `func.args[0]` = `signal.SIGTERM` to the pin so it says what it appears to say. | R12's SIGUSR1 mutant must fail the pin itself, not only its ten neighbours. |
| 12.2 | `tests/test_s0_01_check_acp_conformance.py:4626-4631` — SIGALRM disposition unchanged after a failing `check_bundle` | **S** | executed in the baseline (green) and under R17 (the AttributeError mutant does not disturb it). This is the AF-AP-58 sibling guard and it asserts a real before/after equality. | none | — |

### Class 13 — `/proc/<pid>/exe` races (AF-AP-55)

**One readlink site in the 15 test files** — an empty class for races.

| # | file:line | V | the run that proves it | minimal fix | exact red test |
|---|---|---|---|---|---|
| 13.1 | `tests/test_s0_01_acp_probe.py:785` — `probe_exe = os.readlink(f"/proc/{os.getpid()}/exe")` | **S** | reads the **test's own** live pid; no spawn/exit window exists. Executed in the baseline. Its use is a negative control (`assert rid[...] != probe_exe, "…the probe is reading /proc/self/exe, not /proc/<child>/exe"`, T:786-788). The six production `/proc/<pid>/exe` sites in `apscreen.txt` are outside my file set (production sweep). | none | — |

### Class 14 — Mirrors (hand-copied data / prose pins that are token sets)

| # | file:line | V | the run that proves it | minimal fix | exact red test |
|---|---|---|---|---|---|
| 14.1 | `tests/test_s0_01_frame_tee.py:3122-3145` — `TestDocstringAnchor::test_docstring_pins_the_meaning_not_the_tokens` | **D — token-set mirror** | **R14** — appended a **factually false** sentence to `proofs/S0-01/tools/frame_tee.py`'s module docstring: *"frame_tee itself sends SIGKILL to buzz-acp's process group at startup, so buzz-acp never runs; the tee's own killpg is what ends the leg, and SIGKILL cannot be handled, so the last RUNNING status is written by the tee before buzz-acp exists."* → `pytest -k TestDocstringAnchor` → **`2 passed, 99 deselected in 0.49s`**. The assertions are presence of `killpg`, `SIGKILL cannot be handled`, `last RUNNING status` plus two negative regexes; any false claim that keeps the tokens and dodges the two regexes is green. | pin the *sentence*, not the tokens: assert the docstring contains `PINNED_SHUTDOWN_CLAUSE` verbatim (the constant that 14.2 already derives and validates) rather than three fragments. | the R14 sentence must fail the test. |
| 14.2 | `tests/test_s0_01_frame_tee.py:2999-3120` — `test_shutdown_prose_matches_the_pinned_source` | **S** | not a mirror: it hashes the vendored `acp.rs` against `VENDORED_ACP_RS_SHA256`, then **derives** every fact from that source (`count("SIGTERM") == 0`; `killpg(`+`Signal::SIGKILL` inside `fn kill_process_group`; `kill_line < wait_line`; `from_secs(5)` unique before `#[cfg(test)]`; `sd_start == 422`; `kpg_start == 2323`) before checking the constant against the derived facts. Executed in R14 — it passed only because the false sentence is *additional* prose, which is 14.1's gap, not this test's. | none | — |
| 14.3 | `tests/test_s0_01_check_acp_conformance.py:4448-4464` — the 21 startup keys hand-listed against `cc.PINNED_*` | **S** | not a mirror: the values are read from the module under test (`cc.PINNED_SESSION_POLICY`, …), and `test_ck9_expected_startup_keys_importable` (T:4488) pins `len(cc._EXPECTED_STARTUP_KEYS) == 21`. Executed in the baseline. See 15.1 for the loop's own completeness assertion. | none | — |

### Class 15 — Two counters over different populations asserted equal

| # | file:line | V | the run that proves it | minimal fix | exact red test |
|---|---|---|---|---|---|
| 15.1 | `tests/test_s0_01_check_acp_conformance.py:4484` — `assert len(ran) == len(checks)` | **S** | same population: `ran` collects keys from `checks.items()`, so this is the R10-F16 completeness guard against the loop's own `continue`, not a cross-population equality. Executed in the baseline. | none | — |
| 15.2 | `tests/test_s0_01_pc_post_scan.py:66-74` (`_parse`) — the header's `rows=` counter and the body's row count are **never** asserted equal | **D** | **R15** (see 4.2) — `rows=4` hard-coded in the producer → **`11 passed in 1.28s`**. Two counters over the same population, one of them a free-floating literal. | `assert int(m.group(2)) == len(rows)` in `_parse`. | as 4.2. |

### Class 16 — Provably redundant guards / dead statements (M_V12_CLOSE class)

| # | file:line | V | the run that proves it | minimal fix | exact red test |
|---|---|---|---|---|---|
| 16.1 | `tests/red/test_s0_01_backend_credential_screen.py:80-81` — `_last_record_text` | **E — delete** | **R5**: `200 passed in 76.28s` with it removed. Zero callers. | delete. | — |
| 16.2 | `tests/test_s0_01_check_acp_conformance.py:667,721,734,743` — the four `if …exists():` deletion guards | **E — delete** | **R8**: `26 passed, 334 deselected in 90.45s` with all four removed. | delete (see 1.4 for why keeping them is worse than neutral). | — |
| 16.3 | `tests/test_s0_01_check_acp_conformance.py:3319-3327` — `_EXEMPT_FNS` entries `test_ck8_f34_frame_tee_subprocess_keys`, `test_golden_run_eq`, `test_golden_distinctness_all` | **S — pin, do not delete** | AST-enumerated (class 17 scan): the three do carry non-`_rewrite` writes (`shutil.copytree`+`rename` at T:1822/1824 and T:1880/1882) under `tmp_path`, so the exemptions are load-bearing today. | none — but each exemption should carry a one-line reason, as `test_ck9_tools_not_hardlinked` and `test_ck10_fifo_at_tools_frame_tee_is_named` do. | — |

### Class 17 — Hardlink-clobbering writes in tests (F43 class)

AST-enumerated: **6** write-shaped calls inside functions taking the `bundle` fixture that do not go through
`_rewrite`. All 6 are safe: `.rename()` on a per-test directory (CK:1824, 1882), `symlink_to` creating a **new**
path (CK:2171, 2182), and two writes under `tmp_path/tools`, which the fixture copies with `shutil.copy2` and
never `os.link` (CK:4419, 4542 — CK:467-470 documents exactly that, R9-CK-F19).

| # | file:line | V | the run that proves it | minimal fix | exact red test |
|---|---|---|---|---|---|
| 17.1 | `tests/test_s0_01_check_acp_conformance.py:3314-3408` — `_scan_direct_writes` (:3329) / `_WRITE_ATTRS` (:3314): **`chmod` and `utime` are neither detected nor in the docstring's Known-limits list** | **D — undocumented blind spot** | **R7a** — appended `test_SWEEP_chmod_mutant(bundle)` doing `tgt.chmod(0o400)` + `os.utime(tgt, (0,0))` on `bundle/golden/run-1/timeline.jsonl` (a non-exempt function) → `pytest -k f43_no_direct_writes` → **`1 passed, 360 deselected in 0.63s`**. **R7b** — the harm, demonstrated on a two-link inode: `before: session=644 … mtime=1788820163` → after `chmod 400` + `touch -d @0` on the *per-test* link → **`session=400 mtime=0`**. Mode and mtime live on the shared inode, so one `chmod` in one test poisons the session-scoped pristine bundle for every later test — and `check_manifests` reads mtimes. | add `chmod`, `utime`, `truncate`, `symlink_to`, `hardlink_to` to `_WRITE_ATTRS`/`_OS_WRITERS`, and extend the self-test's category set so none can be silently dropped; or name them in the Known-limits docstring. | R7a's function must appear in `violations`. |
| 17.2 | `_scan_direct_writes` documented limits (`os.open`+`os.write`, variable mode, `copytree`/`move`, subprocess `cp`, module-level writes) | **DL** | executed: the shell-redirect form of the same class was demonstrated in R7b — `echo mutated > $D/pertest/timeline.jsonl` → `session content now: mutated`. The limit is real and is stated in the docstring. | none (documented) | — |
| 17.3 | `test_f43_no_direct_writes_outside_rewrite` (CK:3411-3446) self-test | **S** | executed in the baseline and R7a; it asserts the detected **categories** as a set (`{".write_text", ".write_bytes", "open", "json.dump", "shutil.copy", "os.replace", ".touch", ".rename", ".open", "io.open"}`), so no single pattern family can be deleted with the self-test still green. | none | — |

### Class 18 — Other families I found

| # | file:line | V | the run that proves it | minimal fix | exact red test |
|---|---|---|---|---|---|
| 18.1 | **A lint whose scope is a hard-coded file list.** `tests/red/test_s0_01_backend_credential_screen.py:1183-1188` (2 paths) — and the same shape in `tests/test_s0_01_check_acp_conformance.py:3414` (`_scan_direct_writes` runs on `inspect.getfile(...)`, i.e. exactly one file). | **D** | **R6b** — canonical `!= MARKER` in a third S0-01 test file → lint green. For the F43 scan: the class it enforces (hardlink clobbering) applies to any file that mutates a hardlinked bundle; only the one file is scanned. | glob the file set (`tests/test_s0_01_*.py` + `tests/red/test_s0_01_*.py`) in both lints. | R6b's third file must be flagged. |
| 18.2 | **Module-scoped, accumulating fixture state.** `tests/test_s0_01_scripted_backend.py:57` and `tests/red/…:33` — `@pytest.fixture(scope="module")` over a shared record directory that every `[-1]` read indexes into. | **S today** | the 77 count-delta guards (row 3.3) make the accumulation safe, and the `{n:06d}.json` naming (`proofs/S0-01/tools/scripted_backend.py:533`) keeps `sorted()` correct to 999 999 records. Verified by the baseline and R5. **Named residual:** the safety rests entirely on every future `[-1]` site remembering the `n0` idiom; nothing enforces it. | a `_last_record(backend, n0)` helper that takes the pre-count and asserts the delta itself, so the guard cannot be forgotten. | a new `[-1]` read without a delta must fail a lint. |
| 18.3 | **A "the only expected failure is X" gate written as containment** — the family behind 5.1/5.2, three sites (`CK:2654`, `CK:2725`, and the `_KNOWN_XFAIL_REASONS` set at `CK:2832`). | **D (family)** | R13 falsifies one member; R13b shows the third member resists. The family rule: a *known-acceptable-failure* gate must be exact equality on the whole reason, because the reason space is open and the checker echoes corpus-controlled text into it (`extra=[...]`, `unexpected entries: [...]`). | exact equality in all three. | as 5.1. |
| 18.4 | **`os._exit()` defeats `atexit` in `proofs/S0-01/tools/frame_tee.py:469,478`** — found while building the R19 instrument. | **S (informational)** | my first R19 attempt registered an `atexit` wipe and the artifacts survived (`ls -A` showed all five files, rc 0) — the mutant did **not** fire, and the resulting `101 passed` was a **null result, not a finding**. Re-built the mutant to run immediately before each `os._exit()`, verified the instrument (`framedir: tee-status.json` only), and re-ran. Reported here because it is the trap any future mutation lane will hit on this file. | none | — |

---

## COUNTS PER CLASS

| class | instances enumerated | DEFECT | SAFE | DOCUMENTED-LIMIT | EQUIVALENT/redundant |
|---|---|---|---|---|---|
| 1 presence-gated | 67 gating `if` (99 predicates) | 4 reproduced (1.1, killing 7 tests) + 5 static-only (1.3) + 1 static-only (1.10) | 22 | 0 | 4 (1.4) |
| 2 reads outside the walk | 606 receivers, 3 roots; 1 operator-supplied read bypassing the checker | 1 (hang) | 2 | 0 | 0 |
| 3 stale `[-1]` | 113 tokens → 79 artifact subscripts | 0 | 77 + 2 non-artifact | 0 | 1 dead helper |
| 4 negative acceptance | 4 (0 live `!= MARKER`) | 3 | 1 | 0 | 0 |
| 5 substring/tail anchors | 22 | 3 | 19 | 0 | 0 |
| 6 env-domain | 37 `get(` + 46 `copy()`; 2 behaviour-selecting | 1 | 36 | 0 | 0 |
| 7 lossy decodes | 5 | 0 | 5 | 0 | 0 |
| 8 broad catches | 1 | 1 | 0 | 0 | 0 |
| 9 waits/polls | 58 loops, 73 sleeps | 3 | 20 sampled + rest structurally identical | 0 | 0 |
| 10 skips | 48 skips + 1 xfail | 4 families (10.2, 10.3, 10.4, 10.5) covering 8 + 9 firing skips | 21 declared + the xfail | 0 | 0 |
| 11 world-scoped | 12 | 1 weak (TOCTOU) | 11 | 0 | 0 |
| 12 signal installs | **0 installs** + 2 guards | 0 | 2 | 0 | 0 |
| 13 `/proc/<pid>/exe` races | **1 site, own pid** | 0 | 1 | 0 | 0 |
| 14 mirrors | 3 | 1 | 2 | 0 | 0 |
| 15 two counters | 2 | 1 | 1 | 0 | 0 |
| 16 redundant/dead | 3 families | 0 | 1 | 0 | 2 (delete) |
| 17 hardlink writes | 6 write sites + the scan | 1 (blind spot) | 1 | 1 | 0 |
| 18 other families | 4 | 3 | 1 | 0 | 0 |

**Empty classes (a result):** class 12 has **zero signal-handler installs** in the 15 test files. Class 13 has
**one** `/proc/<pid>/exe` readlink and it targets the test's own pid — **zero race windows**. Class 4's headline
shape (`!= MARKER` acceptance) has **zero live instances**; only its lint is defective. Class 17 has **zero**
live hardlink-clobbering writes; only the scan's coverage is defective.

---

## DEFECT ROWS RANKED BY BLAST RADIUS

1. **1.1 / 1.2 — 7 of 101 `frame_tee` tests pass while the tee produces no evidence at all.** The collector's
   four `if …exists(): … else default` branches (FT:185,192,197,202) turn "the producer wrote nothing" into
   empty lists, empty bytes and an empty dict, and seven consuming assertions are `for`-loops and equalities
   that are vacuous or trivially true on those defaults. This is the S0-01 tee's own evidence contract, and
   seven tests cannot tell it apart from silence. `41 failed, 60 passed` with a verified instrument; the
   de-vacuoused sibling three lines away (FT:233) dies correctly, so the fix is a copy-paste. Row 1.3 adds five
   more sites of the same shape that the mutant structurally cannot reach (SIGKILL paths) — static only.
2. **2.1 — an unguarded `read_text()` on an operator-supplied corpus path hangs the whole suite.** A FIFO at
   `<S0_01_REAL_LEG_DIR>/run-1/process-scan-after.txt` blocks pytest forever (90 s timeout burned, 0.3 s user).
   The production checker already has the S_ISREG guard three lines away; the test reaches around it.
3. **10.2 / 10.3 / 10.5 — 17 real-producer proofs retire silently.** 9 real-leg tests skip against today's
   sandbox corpus (4 process-evidence, 5 tee-status) and 8 `/dev/full` write-failure tests skip in any venue
   with a restricted `/dev` — with rc 0 and nothing declaring the dependency. The declaration pattern that
   fixes them already exists in the same file (`test_real_leg_corpus_declared`).
4. **4.2 / 15.2 — the process-scan enumeration header is never checked against its own body.** `rows=4`
   hard-coded in `pc_post.sh` leaves all 11 `pc_post_scan` tests green; the header is the exact artefact that
   lets the checker tell "enumerated, nothing owned left" from "no scan ran".
5. **6.1 — a one-character typo in `S0_01_VENUE` disables the real-leg declaration.** `"Sandbox"` and
   `"sandbox "` both demote a sandbox run to CI, silently. (Prior finding CK11-F16, still live.)
6. **5.1 / 18.3 — the "only expected failure" gates accept unrelated failures.** A corpus key literally named
   `tee_sha256 mismatch` makes a *key-set corruption* pass as the one known-acceptable failure.
7. **8.1 — a checker crash is accepted as malformed evidence.** `AttributeError` raised on entry to
   `check_bundle` leaves `test_bad_json_timeline` green.
8. **4.1 / 9.3 — the AF-AP-57 ordinal gate has no positive control.** With the fake's gate at `== 99` the test
   passes; the assertion is a pure negation and cannot tell "error set and cleared" from "no error ever".
9. **14.1 — a false docstring passes the prose pin.** Token-set matching, demonstrated with a sentence that
   contradicts the mechanism the file exists to document.
10. **17.1 — `chmod`/`utime` bypass the F43 hardlink scan and are not in its documented limits.** No live
    instance; the scan is one careless line away from a session-wide bundle corruption it cannot see.
11. **4.4 / 18.1 — both class-ban lints are evadable and scoped to hard-coded files.** Reversed operands, a
    variable, or a third file all defeat the `!= MARKER` lint.
12. **9.1 / 9.2 / 11.4 — the backend readiness loop is success-only, its stdout pipe is never drained, and its
    port is chosen by a TOCTOU.** Not a hollow green (the first test goes red), but the reason names the test's
    socket instead of the process that died, and under the 8-worker PC gate it is a flake generator.
13. **1.10 — the session bundle is built with `if src.exists()` around three required fixtures.** Static only.

---

## WHAT I COULD NOT RUN, AND WHY

- **1.10** (`CK:432` bundle-builder presence gate) — running it means removing a tracked fixture from
  `proofs/S0-01/fixtures/`. Every scratch route I had left would have re-run the 25-minute session-bundle build
  inside an already 4-way-contended box while the A5j build lane held the shared copy of that exact test file.
  Reported as **static**, with the exact red test named. It is the one row in the table that is reviewed, not
  reproduced.
- **5.2** (`"manifest timestamps not pre < start < post" in result`) — I could not construct a **collision**:
  no `check_manifests` reason echoes corpus-controlled text, so there is nothing to inject the fragment into.
  Graded as same-class-shape with the fix, not as a reproduced defect. Stated so the verdict does not rest on it.
- **11.4** (`_free_port()` TOCTOU) — the race is real by inspection (bind → close → later bind by another
  process) but I did not stage the interleaving; it is reported as **weak** and as the mechanism that makes 9.1
  worse, not as an independently reproduced failure.
- **Deliberately skipped:** anything on the PC bridge (out of scope by the brief), the six production
  `/proc/<pid>/exe` sites and every `proofs/S0-01/**` row from `apscreen.txt` (the production sweep's file set,
  not mine — I touched production files only as *mutants* to drive test-side behaviour, always on scratch
  copies), and `pkill`-shaped process hunting (forbidden; every kill I did was PID-targeted on processes I
  started).
- **Not attempted:** a full-suite re-run under each mutant. Each full pass is ~25 min on this box, and I ran 19
  targeted mutants; the per-file runs (`frame_tee` ×3 at ~3 min, `backend_credential_screen` ×2 at ~76 s,
  `pc_post_scan` at 1.3 s) are the reachability evidence instead. Where a mutant's blast radius mattered — R12,
  R19 — I ran the whole owning file.

## WHAT I REPRODUCED vs REVIEWED STATICALLY

**Reproduced (a command was run and its output is quoted above):** rows 1.1, 1.2, 1.2b, 1.4, 1.7, 1.8, 1.9,
1.11, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4, 5.1, 5.3, 5.5, 5.6, 6.1, 6.2, 6.3, 7.1, 7.2, 8.1,
9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 11.1, 11.2, 11.3, 12.1, 12.2, 13.1, 14.1,
14.2, 14.3, 15.1, 15.2, 16.1, 16.2, 16.3, 17.1, 17.2, 17.3, 18.1, 18.2, 18.4.
**Reviewed statically only:** 1.3 (5 sites), 1.10, 5.2, 11.4 (each flagged in its row and in the section above).

## FILE SHAS OF EVERYTHING I GRADED (sha256, at `fffb511`; identical at `6b8c9d1`)

```
f1f016fa1a787809646f5eb54cdf61265a4809b022cb669da6ac575dc58f236b  tests/test_s0_01_acp_probe.py
8f0cdf2a82e0d21dc8782a1f53db5f1e35aa34be4928d227dcdf389c77f0b46c  tests/test_s0_01_audit_cp5_controls.py
da1ce46654675f497d7e80ffc31814fba229fc7c73379a8f02d8f31b2d338f1c  tests/test_s0_01_check_acp_conformance.py
78d02f4ff58676c2a52d3f21bd31ad7eb543117eb9adc9d06fd00ef7dafd4370  tests/test_s0_01_check_initialize.py
d1be6adf7ff3baf9bf792c84e095be55aaeae57c213eda5ad6876c7630269c32  tests/test_s0_01_frame_tee.py
185f62ad298c67d680714e8c357e101f0219ee5a76e2e95807b26d00d7103aff  tests/test_s0_01_initialize_capture.py
8143ecfa27658f2f7aba1e6422e73b0d9cc6d121de6c0663a3657fbfbfe47540  tests/test_s0_01_negative_contract.py
5954bc4f6c6b97b156691cd5cadb4c8bdf502c2c076911ce08d8c7ba6dbab5b5  tests/test_s0_01_nostr_verify.py
74dc06219b51fcf50ba95ffb7233b2a89d81df1d95d829ee071c8cc3a033fff2  tests/test_s0_01_pc_post_scan.py
eb07b8090783bc80f97d1b867157c450021ebc2d93ce68435bc5ab42839003c2  tests/test_s0_01_scripted_backend.py
0c7528113bb41dc98168032bb956e33c3b1b5a707075ae7ed8294517d3ce5b82  tests/test_s0_01_spec_runner.py
c24c20c9eea336f12d91f69c2c2b4fa50c3d8ff10b8b131b995a9030d1d9fe72  tests/test_s0_01_turn_capture.py
5aa76e5e9b4c18adf881041268fb167ea44d91a849ea1cd3c1e1916db9ea1dfd  tests/red/test_s0_01_adversarial.py
efbc3da8628600c85cf4f9cda7eff9e57c55bf51e66579fbbfd938f305868b56  tests/red/test_s0_01_backend_credential_screen.py
a38420393c0b084f62775d79845eb8bb963b6f48928aedeba44b7b488a63fb41  tests/red/test_s0_01_round4.py
```

Line counts: 2032 / 144 / 4677 / 850 / 3144 / 126 / 441 / 751 / 321 / 2144 / 716 / 116 / 141 / 1212 / 46 =
**16 861 lines**.

**Three files carry no rows** — `tests/test_s0_01_initialize_capture.py` (5 tests), `tests/red/test_s0_01_adversarial.py`
(5), `tests/red/test_s0_01_round4.py` (1): AST + grep found no instance of any of the 18 classes in them, and
all 11 tests pass in the baseline. `tests/test_s0_01_nostr_verify.py` (82 tests) and
`tests/test_s0_01_turn_capture.py` (5) likewise carry no class instances; `tests/test_s0_01_spec_runner.py` (13)
and `tests/test_s0_01_check_initialize.py` contribute only to the class-3 and class-6 SAFE counts. An empty file
is a result too.

---

## VERDICT

**NOT-READY.** 22 DEFECT rows across 11 of the 18 classes, every one reproduced by a run whose output is quoted
above, except the four named in "reviewed statically only". The verdict does **not** depend on those four: it
rests on 1.1/1.2 (7 tests green while the producer writes nothing, instrument verified), 2.1 (a suite-wide
hang on an operator-supplied path), 10.2/10.3/10.5 (17 proofs retired by undeclared skips), 4.2/15.2 (a lying
enumeration header the whole file accepts), 8.1 (a checker crash accepted as evidence corruption) and 5.1 (an
unrelated failure accepted as the one known-acceptable one) — all seven reproduced.
