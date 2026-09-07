# VERIFY-CK10 — round-10 adversarial grade of checker lane A5h (S0-01 ACP conformance checker)

*(draft in progress — items completed so far are final; the verdict is at the end)*

## PREMISE

| item | observed |
|---|---|
| PIN | `9b2803c618a2bb42cb2b0b18258528d26c41e358` — `git cat-file -e` exits 0; `git log --oneline -1` = `9b2803c S0-01 WIP checkpoint 8p: checker refuses a non-positive cap, walks the tree before reading it, pins the FINAL arm exactly (lane A5h); world-aware scan tests (AF-AP-59) — REVIEW-PENDING, nothing minted` |
| PIN == local HEAD | yes (`git log --oneline -3` head = `9b2803c`) |
| PIN parent | `618749f` (`S0-01 backend round 12 brief (D5i) + the VERIFY-D5h verdict, before dispatch`) |
| shared-tree dirt at start | ` M proofs/S0-01/tools/frame_tee.py`, ` M proofs/S0-01/tools/scripted_backend.py`, ` M tests/red/test_s0_01_backend_credential_screen.py`, ` M tests/test_s0_01_frame_tee.py`, ` M tests/test_s0_01_scripted_backend.py`, `?? tasks/briefs/s0-01-b5f-support/B5f-report.md` — other lanes (B5f tee, D5i backend). **None of my scope files.** I graded from `git archive 9b2803c`, never the shared tree. |
| tee at the PIN | `proofs/S0-01/tools/frame_tee.py` 466 lines, sha256 `061dd10c129b75ee4e56a5eb8a289b43c9d8bf40b1704f7ee18b3951db9e6ba7` — matches the brief exactly. No `tee_sha256 mismatch` in any run. |
| scope-file hashes at the PIN | `3edd8a2023c7f3af8ac0947cb880cbeddb411219a404c0c594ba55f5f31ec859  check_acp_conformance.py` · `5b192f830a4e0c1249a9a80a979d2622932f7ed22b5d967489fafafac90a1dbb  test_s0_01_check_acp_conformance.py` — **both match the lane report's FINAL FILE HASHES block verbatim.** Line counts 1840 / 4426 also match. |
| lane report PIN | `A5h-report.md` says `PIN: d5b1b03e058a6f50438446fcf3df0e888d771d63`. **Verified: it exists** (`git cat-file -e` rc 0) and is `S0-01 checker round 10 brief (A5h) + the VERIFY-CK9 verdict, before dispatch` — the lane's dispatch PIN, an ancestor of my PIN (4 commits back). Its scope files are **byte-identical** to `618749f` (my PIN's parent), so the lane's red-before baseline and mine are the same tree. No drift. |
| interpreter | `/root/venv-agent-factory/bin/python` = CPython 3.11.15, pytest 9.1.1. `python3` = same 3.11.15. |
| disk / load at start | `df -h /` 252G/26G/13G/68%; `/proc/loadavg` 2.20 1.70 1.80; 4 cores. |

Working copies (all under the session scratchpad, none in the repo):
`ck10/pin` = `git archive 9b2803c`; `ck10/parentck` = pin tree with the PARENT checker swapped in;
`ck10/wk1` (fixture harness), `ck10/wk2` (end-to-end CLI harness, `PINNED_GOLDEN_SHA256` patched to the synthetic golden),
`ck10/wk3` (mutation tree, restored + sha-verified after every mutant); `ck10/mat` = a materialised PASS bundle
(evidence/ + fixtures/ + tools/) so the **CLI** can be driven end-to-end, not just `check_bundle` in-process.
`ck10/wk2` CLI on `mat`: `PASS: S0-01 acp-conformance - 63 checks executed over 5 legs; …` rc 0.

---

## ITEM 2 — the cap's domain (`F1`)

### CLI `--timeout-s`, executed (load average 0.72 1.29 1.63 at the batch)

`python3 proofs/S0-01/check_acp_conformance.py --timeout-s <V> /tmp/nonexistent-x` (rc 2 = accepted → `deferred:`; rc 64 = refused):

| value | rc | first line |
|---|---|---|
| `0` | 64 | `usage: --timeout-s must be a positive integer` |
| `-1` | 64 | same |
| `-0` | 64 | same |
| `abc` | 64 | same |
| `1.5` | 64 | same |
| `1e3` | 64 | same |
| `""` (empty) | 64 | same |
| `+5` | 2 | accepted (= 5) |
| `" 5"` (leading ws) | 2 | accepted |
| `"5 "` (trailing ws) | 2 | accepted |
| `5_0` (PEP-515 underscore) | 2 | accepted (= 50) |
| **`2**31` = 2147483648** | **1** | **`failure_reason: malformed evidence: OverflowError: Python int too large to convert to C int`** |
| **`2**32-1`, `2**40`** | **1** | same |
| `2**31 - 1` | 2 | accepted |
| `--timeout-s 5 --timeout-s 0` | 64 | generic `usage: check_acp_conformance.py [--fixtures-dir <dir>] [--timeout-s N] <evidence-root>` (fail-closed: the first is consumed, the second is leftover argv) |
| no flag | 2 | accepted (default) |

Every non-positive value refuses loudly with the exact reason. **The huge-value class does not** — see F-R10-04.

### In-process `check_bundle(root, timeout_s=…)`, executed

| value | outcome |
|---|---|
| `0` | `ValueError: timeout_s must be a positive integer` |
| `-1` | `ValueError: …` |
| `False` | `ValueError: …` |
| `-0.0` | `ValueError: …` |
| **`True`** | **ACCEPTED — instrumented `signal.alarm` call list = `[True, 0]`, i.e. a silent 1-second cap** (F-R10-03) |
| `1.0` | `TypeError: 'float' object cannot be interpreted as an integer` (loud, but from `signal.alarm`, not the guard) |
| **`float('nan')`, `float('inf')`** | `TypeError` **from `signal.alarm`, not from the guard** — `nan <= 0` is `False`, so NaN walks straight through the positivity floor (F-R10-05) |
| `"5"` | `TypeError: '<=' not supported between instances of 'str' and 'int'` (loud) |
| `2**31` | `OverflowError` |
| `None` | no cap (by design) |

**Can any CLI path reach `None`?** No — verified from primary source: `main()` initialises `timeout_s = 90` (C:1798) and the only
reassignment is `timeout_s = int(args[idx + 1])` (C:1812). There is no path that assigns `None`. ✅

### Is the 90 s default actually exercised?

- `test_ck9_default_timeout_is_90` (T:4422-4426) asserts **`inspect.signature(cc.check_bundle).parameters["timeout_s"].default == 90`** — a signature assertion, nothing fires.
- **No test makes the default alarm fire.** Reproduced that it *can*: with `main()`'s literal scratch-patched `90 → 2`, the CLI with
  **no flag** against a bundle whose clean runtime is ~9 s:
  ```
  failure_reason: checker timed out after 2s
  rc=70  elapsed=3s
  ```
  (this proves the **default path installs a live alarm that fires with the exact reason and rc 70**; it does not by itself isolate any
  particular slow read — the clean run alone exceeds 2 s. The FIFO isolation is done separately in item 3 with a 25 s cap and a 40 s
  external kill against a 9 s baseline.)
- **The default is TWO independent literals** (C:1633 signature `timeout_s: int = 90`, C:1798 `main()`'s `timeout_s = 90`) and
  only the CLI one governs `spec.json` (which passes no flag). Mutants, executed on `ck10/wk3` (`-k "cli or timeout or default or fifo or usage"`, 344 collected):
  | mutant | result |
  |---|---|
  | `SIG-DEFAULT-900` (signature `90 → 900`) | **KILLED** — `1 failed, 15 passed, 328 deselected in 13.52s` (`test_ck9_default_timeout_is_90`) |
  | **`MAIN-DEFAULT-900`** (`main()`'s `90 → 900`) | **SURVIVED** — `16 passed, 328 deselected in 13.62s` |
  | `MAIN-DEFAULT-3` (`main()`'s `90 → 3`) | killed only *incidentally* — `test_cli_pass_path_fails_on_golden_pin` runs >3 s, so it trips on runtime, not on the value |
  The documented invariant ("The default cap is 90 s so it always fires before the runner's `timeout_s: 120`", C:12-13) is
  **unpinned on the only path that uses it** (F-R10-06).

---

## ITEM 3 — walk-before-read + `S_ISREG` (F2 / F27)

### Every read in the checker, and what protects it (enumerated from primary source)

`grep -n "read_text()\|read_bytes()\|open(\|iterdir()\|glob("` over `check_acp_conformance.py` → 33 `_require_file(` call sites.
Classification:

| read path | protected by |
|---|---|
| everything under `golden/` (timeline, frames, rid, env, pid, argv, exit, log, manifests, summaries, scans, owned-pids, tee-status, mentions, upstream-records, agent-stderr, golden.jsonl, negative/) | the **walk** (C:1655-1669, `os.walk(golden, followlinks=False)`) **and**, for 33 of them, `_require_file` |
| everything under `_fixtures()` (identities.json, acp-schema-v1.json, upstream-token.fingerprint, neg-malformed-initialize.json) | the **walk** (second walk root) + `_require_file` for identities/fingerprint |
| reads with no `_require_file` but inside a walked tree: C:581 `<replies_to>.event.json`, C:608 `rec_dir.glob("*.json")`, C:938-939 `owner/user2.event.json`, C:988/992/1223/1299, C:1602 `r1m/r2m` | the walk only |
| **`HERE/"tools"/"frame_tee.py"` (C:416-420)** | **NOTHING** — bare `if not tee_file.exists()`, then `_sha256_file(tee_file)` → `open(path,"rb")`. Not a walk root, not `_require_file`d. |
| **`d/"manifest-post.summary"` at C:1697-1699** (the A1 pre-read, which runs BEFORE the per-leg allowlist loop) | **the walk only** — bare `.exists()` then `_parse_summary` → `read_text()`; no `_require_file` |

### Executed class sweep — the CLI, **default cap**, external cap 12 s (load 0.59-0.86)

Harness: a materialised PASS bundle (`ck10/mat`) + `ck10/wk2` (checker byte-identical to the PIN; only `pins.PINNED_GOLDEN_SHA256` patched to the synthetic golden). Control: pristine → `PASS: … 63 checks executed over 5 legs …` rc 0 in 8864 ms.

| vector | rc | elapsed | reason |
|---|---|---|---|
| **FIFO @ `fixtures/identities.json`** (the CK8 item-1d vector) | 1 | **153 ms** | `failure_reason: fixtures: non-regular entry in evidence tree: identities.json` ✅ |
| FIFO @ `golden/run-1/timeline.jsonl` | 1 | 163 ms | `golden: non-regular entry in evidence tree: run-1/timeline.jsonl` ✅ |
| **char device** (`mknod c 1 3`) @ `run-1/env.json` | 1 | 148 ms | `golden: non-regular entry in evidence tree: run-1/env.json` ✅ |
| **unix socket** @ `run-1/env.json` | 1 | 168 ms | `golden: non-regular entry in evidence tree: run-1/env.json` ✅ |
| symlink → FIFO @ `run-1/env.json` | 1 | 147 ms | `golden: symlink in evidence tree: run-1/env.json` ✅ |
| symlink → directory @ `run-1/env.json` | 1 | 145 ms | `golden: symlink in evidence tree: run-1/env.json` ✅ |
| symlink → `/dev/null` (char device) | 1 | 145 ms | `golden: symlink in evidence tree: run-1/env.json` ✅ |
| DIR named `fixtures/identities.json` | 1 | 152 ms | `golden: fixtures/identities.json is not a regular file` ✅ |
| **FIFO @ `proofs/S0-01/tools/frame_tee.py`** | **124** | **15 000 ms (external kill)** | **nothing — blocked; with `--timeout-s 3`: `failure_reason: checker timed out after 3s` rc 70** ❌ **F-R10-02** |

**F2's own vector is genuinely closed** — 153 ms and the exact reason under the *default* cap, versus CK9's reproduction of the same vector blocking past a 12 s kill on the parent. Reproduced red-before: `test_ck9_fifo_at_identities_json_is_named` FAILS on the parent checker (item 1 batch).

### A **directory** named exactly like each of the 20 allowlisted per-leg files (default cap)

19 of 20 give the exact `run-1: <name> is not a regular file`. Times range 160 ms → 9350 ms (a directory is *legal* to the walk, so each is caught only when its own `_require_file` is reached — the "≤ 1 s" property is a FIFO property, not a directory property).

**One exception — F-R10-07:**
```
manifest-post.summary   rc=1  160ms  failure_reason: malformed evidence: IsADirectoryError: [Errno 21] Is a directory: '.../run-1/manifest-post.summary'
```
This is *verbatim* the defect R9-CK-F27 named ("fails only as `failure_reason: malformed evidence: IsADirectoryError: …` — a generic reason, not `non-regular entry`"), still live at one path, while the lane report's F27 row claims "`_require_file` S_ISREG gate covers **every read path**".

---

## ITEM 4 — `_scan_direct_writes` (F3)

### The lane's two mutants (reproduced on `ck10/wk3`, restored + sha-verified after each)

| mutant | pytest summary (verbatim) | verdict |
|---|---|---|
| control (pristine, `-k f43_no_direct`) | `1 passed, 343 deselected in 0.51s` | green |
| `F43-ATTRS-OFF` (`_WRITE_ATTRS = set()`) | `1 failed, 343 deselected in 0.60s` — `assert 5 >= 6` | **KILLED** ✅ |
| `F43-SCAN-OFF` — superseded by `F43-MODEOPEN-OFF` below; the full short-circuit also dies (the real assertion then also returns `[]` but the self-test count drops to 0) | — | **KILLED** ✅ |
| `F43-MODEOPEN-OFF` (disable the builtin-`open()` mode branch) | `1 failed, 343 deselected in 0.62s` — `assert 5 >= 6` | **KILLED** ✅ |

### **Three more mutants I built — all SURVIVE (F-R10-08)**

The self-test asserts `len(self_violations) >= 6` over a 6-statement source, but that source yields **7** violations, because
`json.dump(obj, open(p, "w"))` is TWO `Call` nodes (`json.dump(…)` **and** the nested `open(…, "w")`). The threshold is therefore
slack by exactly one, and any single one-violation pattern family can be deleted with the self-test still green:

| mutant | pytest summary (verbatim) | verdict |
|---|---|---|
| `F43-SHUTIL-OFF` (`_SHUTIL_WRITERS = set()`) | `1 passed, 343 deselected in 0.52s` | **SURVIVED** ❌ |
| `F43-OSW-OFF` (`_OS_WRITERS = set()`) | `1 passed, 343 deselected in 0.52s` | **SURVIVED** ❌ |
| `F43-JSONDUMP-OFF` (`if False and … func.attr == "dump"`) | `1 passed, 343 deselected in 0.51s` | **SURVIVED** ❌ |

So the docstring's load-bearing claim — "Both the real test and the self-test call this function — **disabling the scan disables both**"
(T:3276-3278) — is false for three of the six families. R9-CK-F3 is **half** closed, not closed.

### The equivalence class of a direct write (19 vectors, each planted one at a time in a fresh non-exempt module-level test fn)

| # | vector | scan |
|---|---|---|
| a | `with open(bundle/"x","w")` | **CAUGHT** |
| b | **`os.open(...,O_WRONLY\|O_CREAT\|O_TRUNC)` + `os.write`** | **MISSED** |
| c | `Path(...).write_bytes(b"…")` | **CAUGHT** |
| d | `shutil.copy(src, bundle/"x")` | **CAUGHT** |
| e | `json.dump(obj, fh)` | **CAUGHT** |
| f | `(bundle/"x").touch()` | **MISSED** (mtime only — low harm) |
| g | `os.replace("/tmp/evil", bundle/"x")` | **CAUGHT** |
| h | `os.rename("/tmp/evil", bundle/"x")` | **CAUGHT** |
| i | write inside a module-level helper not in `_EXEMPT_FNS` | **CAUGHT** |
| j | **`(bundle/"x").rename(...)` (Path method form)** | **MISSED** |
| k | **`(bundle/"x").open(mode="w")` (keyword mode)** | **MISSED** — the builtin-`open` branch checks `keywords`, the `.open` branch checks only `args[0]`: an asymmetry in the same function |
| l | **`m="w"; open(bundle/"x", m)` (mode via a variable)** | **MISSED** |
| m | **`shutil.copytree(src, bundle/"x")`** | **MISSED** |
| n | **`shutil.move(src, bundle/"x")`** | **MISSED** |
| o | **`io.open(bundle/"x","w")`** | **MISSED** |
| p | **a write at module scope** (`fn_name is None` → `continue`, T:3300) | **MISSED** |
| q | `subprocess.run(["cp", …])` | **MISSED** (out of scope, named for completeness) |
| r | write inside a nested fn defined in a test | **CAUGHT** |
| s | write in a `class Test…` method | **CAUGHT** |

9 CAUGHT / 10 MISSED. Note `shutil.copytree` cannot be added to `_SHUTIL_WRITERS` without flagging the **`bundle` fixture itself**
(T:461-471 calls `shutil.copytree` three times and `bundle` is **not** in `_EXEMPT_FNS`) — i.e. the writer set is fitted to what the
file happens to contain, not to the threat.

---

## ITEM 1 — the R9-CK-F1…F29 closure table

**Method.** `ck10/parentck` = the PIN tree with `git show 618749f:proofs/S0-01/check_acp_conformance.py` swapped in.
`618749f` (the PIN's parent) and `d5b1b03` (the lane's dispatch PIN, which the lane report names and which **does exist**
— `git cat-file -e` rc 0) carry **byte-identical** scope files, so this is exactly the lane's own red-before baseline.
Run: `pytest tests/test_s0_01_check_acp_conformance.py -q -p no:randomly -k ck9 -rf` → **`13 failed, 17 passed, 314 deselected in 152.01s`** (load 1.40 at close).

**17 of the 30 new `ck9` tests are GREEN on the parent checker — they are CONTROLs, not red-before.**

| R9-CK id | closed by | red-before reproduced on the parent? |
|---|---|---|
| **F1** cap domain | `test_ck9_timeout_arg_zero_rejected`, `_negative_rejected`, `_inprocess_zero_raises` | **RED ✅** (3/3 fail on parent) |
| **F2** walk before read | `test_ck9_fifo_at_identities_json_is_named` | **RED ✅** |
| **F27** type before name | `test_ck9_require_file_rejects_fifo`, `_rejects_dir` | **RED ✅** (2/2) — but **not closed at the class**, see F-R10-07 / F-R10-02 |
| **F3** F43 scan one function | `test_f43_no_direct_writes_outside_rewrite` + `_scan_direct_writes` | test-side; ATTRS-OFF/MODEOPEN-OFF die — **half closed**, F-R10-08 |
| **F4** tee parented by buzz | `test_ck9_no_tee_parented_by_buzz` | **GREEN on parent = CONTROL**; report says "RED-BEFORE:" (F-R10-09) |
| **F5** FINAL arm pinned | `ck9_final_arm_forwarded_exact` ×2, `_recorded_exact` ×2, `_updated_seq_exact`, `_stdin_reader_done` | **GREEN on parent = CONTROL** ×6; report says "RED-BEFORE:" (F-R10-09). Mutants die — item 5 |
| **F18** both arms type-strict | `test_ck9_final_arm_float_rejected[3]` | **RED ✅** (3/3). 84/84 hostile type shapes reject — item 5 |
| **F29** RUNNING upper bounds | `ck9_running_seq_lag_2`, `_recorded_deficit_2` | **GREEN on parent = CONTROL** ×2; report says "RED-BEFORE:" (F-R10-09). Mutants die |
| **F17** dead seq-sum deleted | deletion + comment | **43 218 live-reachable shapes: 0 verdict differences** — item 7 ✅ |
| **F6** six dead branches | deletions + comments | deletions SAFE (10 hostile bundles, none reached a site) but **4 of 6 comments cite the wrong guard** — F-R10-10 |
| **F7/F8/F9/F10/F13/F23** exact reasons | 11 conversions + `_EXPECTED_STARTUP_KEYS` hoist | `test_ck9_expected_startup_keys_importable` **RED ✅**; `_startup_missing_keys_exact` CONTROL |
| **F11** owned_zombies consumed | `ck9_owned_zombies_exceeds_owned` **RED ✅**; `_negative`/`_abc` CONTROL | **half closed** — F-R10-11 |
| **F12** pins not literals | `test_ck9_env_respond_to_from_pin` | **RED ✅** — but only the non-two-users branch, F-R10-12 |
| **F20** role SEQUENCE | `ck9_post_roles_reordered`, `_duplicated` | **GREEN on parent = CONTROL** ×2; report says "RED-BEFORE:" (F-R10-09) |
| **F19** fixture hardlinks | `test_ck9_tools_not_hardlinked` | CONTROL — correctly labelled in the report ✅ |
| **F21** strict xfails | `_KNOWN_XFAIL_REASONS` + `pytest.xfail(strict=True)` | item 11 |
| **F24** version strings | `T:1` v2.2 | mechanical ✅ (verified: `T:1` reads "v2.2 test suite", `C:1` "v2.2") |
| **F25** A25 reorder | `test_ck9_a25_reorder_diagnostic` | **RED ✅** |
| **F28** `_check` default cap | `_check(..., timeout_s=60)`; `test_ck9_default_timeout_is_90` | CONTROL; **the CLI default is a second, unpinned literal** — F-R10-06 |
| **F13** startup parametrised | `test_ck9_startup_wrong_value_parametrised` | **GREEN on parent = CONTROL** |
| **F14/F15/F16/F22/F26** report discipline | prose | F14 ✅ (11 passed run here), F15 ✅ (line counts re-derived: checker 1790→1840 = +50 ✅, tests 3956→4426 = +470 ✅), F16 carried honestly ✅ |

**Every R9-CK id is addressed.** Five are only partly closed (F27, F3, F11, F12, F28) and one carries a false derivation (F6);
none is untouched.

---

## ITEM 5 — the FINAL arm, the RUNNING upper bounds, type strictness

### The 38-shape A21d table, re-executed at the PIN (`ck10/teerun/a21d_table.py`, adapted from CK9's harness)
```
TOTAL 38 cases, 0 MISMATCHED expectation
```
All 38 verdicts **and all 38 reason strings** are identical to CK9's table. 10 B5d-legal RUNNING shapes ACCEPT,
17 out-of-bound siblings REJECT, 2 FINAL shapes ACCEPT, 9 FINAL shapes REJECT.

### The float / bool / str / NaN matrix on BOTH arms (`ck10/teerun/types_table.py`) — 84 shapes, **BAD=0**
5 numeric fields × {`3.0`, `True`, `"3"`, `3.5`, `-0.0`, `1e0`} × {FINAL, RUNNING} = 60 → every one
`REJECT run-1: tee-status.json <field> is not int`. Plus raw-JSON `NaN` / `Infinity` / `-Infinity` / `1e400` on
`recorded_c2a`, `updated_seq`, `agent_returncode` × both arms = 24 → all REJECT with a named reason.
**R9-CK-F18 is fully closed; there is no NaN wormhole on either arm.**

### Mutants (`ck10/wk3`, one at a time, checker restored + sha-verified after each, 3 runs each)
Controls (pristine): `ck9_final_arm_forwarded_exact` `2 passed, 342 deselected in 18.05s` · `_recorded_exact` `2 passed … 19.52s` ·
`_updated_seq` `1 passed … 10.48s` · `_stdin_reader_done` `1 passed … 10.43s` · `ck9_running_seq_lag_2` `1 passed … 10.65s` ·
`ck9_running_recorded_deficit_2` `1 passed … 10.65s` · `ck9_final_arm_float_rejected` `3 passed, 341 deselected in 26.42s`.

*(mutant results table — see the MUTANT TABLE section below)*

---

## ITEM 6 — the six deleted dead branches

**The deletions are SAFE — 10 hostile bundles, not one reached a deleted site.** No traceback, no wrong reason, no silent pass.
**But 4 of the 6 derivation comments name the wrong guard.** The comment is the only record of why the branch was safe to delete;
a future editor who checks the named function will find it unchanged and reintroduce the crash.

Executed (`ck10/wk1`, hostile bundle per site; `_check(bundle)`):

| deleted site | what would crash | reason actually produced | guard the code comment CITES | guard that ACTUALLY fires |
|---|---|---|---|---|
| **C:952** `first_term_epoch = int(first_term.timestamp())` | `AttributeError` on `None` | `failure_reason: two-users: a user's turn did not reach end_turn` | "`check_initialize_frames` … requires `stopReason=="end_turn"` for every prompt response" — **FALSE**, `check_initialize_frames` (C:713-741) validates only the *initialize* req/resp pair | **C:922-925**, inside `check_two_users` itself, 27 lines earlier |
| **C:960** `new_seqs[1]`, `term_seqs[0]` | `IndexError` | `failure_reason: two-users: c2a request methods […] != expected […]` (direct call) | "`new_seqs >= 2` guaranteed by `check_initialize_frames` (exactly 2 session/new)" — **FALSE** | **C:894-895** and **C:906-907**, same function |
| **C:1547** `init_resp_idx >= session_new_idx` | `TypeError` on `None` | `failure_reason: run-1: initialize response protocol-violation: missing required initialize field` | `check_initialize_frames` + the `req_methods` check | **CORRECT** ✅ (`ci.classify_response`, C:729-730; `req_methods`, C:1533-1535) |
| **C:1563** `new_resp_idx >= prompt_idx` | `TypeError` on `None` | `failure_reason: run-1: session/new has no sessionId response` | "`check_initialize_frames` (session/new has sessionId response)" — **FALSE** | **`check_prompt_turn` C:747-749** |
| **C:1594** `sid1 == sid2` | (weakened, not deleted) | `failure_reason: run-1: session/new has no sessionId response` | "`check_initialize_frames` validates the session/new response" — **FALSE** | **`check_prompt_turn` C:747-749** |
| **C:1599** `r1m.read_text()` | `FileNotFoundError` | `failure_reason: run-1: mentions/owner.event.json absent` | `check_mentions` via `EXPECTED_MENTIONS` | **CORRECT** ✅ |

**The `init_resp_idx` derivation CK9 left UNSURE — completed here, from primary source.**
`check_initialize_frames` runs for **every** leg in the first loop of `EXPECTED_CHECK_SEQUENCE` (C:216-219), before `check_golden`
(C:246). For run-1 it requires (a) a successful response to the `initialize` request (C:719-720), (b) `ci.classify_response(resp["result"])
== "ok"` (C:723-725), and (c) `resp["result"].get("protocolVersion") == PINNED_AGENT_PROTOCOL_VERSION` — which is **`1`**, a non-None value
(`pins.py:54`). `normalize_timeline` (C:1461-1465) copies `res["protocolVersion"]` into the normalized record whenever `res` is a dict
containing the key. Therefore an a2c record with `kind == "resp"` and a non-None `protocolVersion` always exists in `n1`, and
`init_resp_idx` is never `None`. `session_new_idx` is guaranteed by the `req_methods` equality at C:1533-1535. **DEAD — derivation
complete, and the executed hostile bundle (F6c) confirms `check_initialize_frames` fires first.**

Note the **semantic tightening** at C:1594: the parent's `if sid1 is not None and sid2 is not None and sid1 == sid2` accepted a bundle
where BOTH runs lacked a sessionId; the PIN's `if sid1 == sid2` now rejects it (`None == None`). Stricter, fail-closed — not a defect,
but not documented as a behaviour change either.

---

## ITEM 7 — F17, the deleted seq-sum rule

Exhaustive differential (`ck10/teerun/f17.py`): the PIN's `check_tee_status` vs the PARENT's (which still has the rule),
over the same timeline, enumerating `recorded_c2a`, `recorded_a2c`, `forwarded_c2a`, `forwarded_a2c` ∈ 0..6 and `updated_seq` ∈ 0..8 on both arms.

- **Live-reachable timeline** (seq 1..6 contiguous — what `check_timeline` C:262-… enforces before `check_tee_status` runs for that leg):
  **43 218 status shapes, 0 verdict differences.** The deletion changes nothing reachable through `check_bundle`. ✅
- **Direct-call-only timeline** `seq=[1,2,3,4,5,7]` (rejected by `check_timeline`, so unreachable via `check_bundle`):
  **13 shapes differ** — the PIN ACCEPTs, the parent REJECTed. The differing family is exactly *timelines whose last seq exceeds
  c2a_count + a2c_count*, e.g.
  `FINAL recorded_c2a=3 recorded_a2c=3 updated_seq=7` → PIN ACCEPT, parent `run-1: tee-status.json updated_seq 7 != recorded_c2a + recorded_a2c (3 + 3)`.
  (That the parent module *does* reject these is the harness's built-in positive control.)

The cited derivation (C:1456-1457, "check_timeline (C:261-262) enforces seq 1..N") is **correct**: `check_timeline` is registered for
every leg in the first loop of `EXPECTED_CHECK_SEQUENCE`, `check_tee_status` in the fifth. ✅

---

## ITEM 8 — F11 `owned_zombies`

Executed through the CLI against a materialised PASS bundle whose `run-1` scan header has `owned=3 owned_present=3`:

| `owned_zombies=` | rc | reason |
|---|---|---|
| `0` | 0 | PASS |
| **`3` (== owned, and `owned_present` is also 3)** | **0** | **PASS — an impossible header ACCEPTED, F-R10-11** |
| `4` (owned+1) | 1 | `run-1: process-scan-after.txt owned_zombies=4 exceeds owned=3` |
| `99` | 1 | same shape |
| `2**64` | 1 | same shape (arbitrary-precision int; no overflow) |
| `-1` | 1 | `run-1: process-scan-after.txt has no enumeration header` (the `(\d+)` regex) |
| `abc` | 1 | same |
| field removed entirely | 1 | same |

Every garbage value is refused. **But the consistency rule is weaker than the producer's invariant.** From primary source
(`proofs/S0-01/tools/pc/pc_post.sh:40-44, 71-75`): a `Z`-state row is `continue`d **before** `rows.append`, so `table_pids` excludes
zombies; `owned_present = len(owned & table_pids)` and `owned_zombies = len(owned & zombies)` are therefore **disjoint** subsets of
`owned`. The true invariant is `owned_present + owned_zombies <= owned` — exactly what R9-CK-F11 proposed
(`int(hdr.group(8)) + int(hdr.group(6)) <= int(hdr.group(5))`). The landed check is only `group(8) > group(5)`.
Also: `owned_zombies` is consumed **only** for `process-scan-after.txt` (C:1259); the teardown scan's `td_hdr.group(8)` is
never read (`grep -n "group(8)"` → one hit).

---

## ITEM 9 — F12 pins

`PINNED_STARTUP_RESPOND_TO = "owner-only"`, `PINNED_STARTUP_RESPOND_TO_TWO_USERS = "allowlist(1)"` (`pins.py:135-136`).
Two surfaces: the **startup line** compares against the pin verbatim (C:1137-1140, `expected_rt`); the **env** compares against
`PINNED_STARTUP_RESPOND_TO_TWO_USERS.split("(")[0]` (C:490-492).

Probed through the CLI on the two-users leg — **the env value's exact form IS pinned, and `allowlist(2)` is NOT accepted**:

| `BUZZ_ACP_RESPOND_TO` | rc | reason |
|---|---|---|
| `allowlist` | 0 | PASS |
| `allowlist(1)` | 1 | `two-users: env BUZZ_ACP_RESPOND_TO should be 'allowlist' for two-users` |
| **`allowlist(2)`** | **1** | same — **rejected** ✅ |
| `owner-only` | 1 | same |
| `ALLOWLIST` | 1 | same (case-sensitive) |

**But the two-users branch has no pin-consumption test.** `test_ck9_env_respond_to_from_pin` monkeypatches only
`PINNED_STARTUP_RESPOND_TO` (the non-two-users pin) and asserts a **substring**, not the exact reason. Mutant
`LITERAL-PINS-2U` (C:490 → `_expected_rt_env = "allowlist"`, the literal F12 was raised to remove):
**`30 passed, 314 deselected in 38.10s` — SURVIVED** over `-k "env or pin or twousers or two_users"`. F-R10-12.

---

## ITEM 10 — F19 fixture copy

Executed inode/nlink audit over the WHOLE materialised bundle tree (`ck10/wk1`, `test_zz_fixture_link_audit`):
```
ITEM10 tracked-inode collisions in the bundle tree: []
ITEM10 nlink census: [('evidence', 2), ('fixtures', 2), ('tools', 1)]
```
**No inode of any tracked file under `proofs/S0-01/tools/` or `proofs/S0-01/fixtures/` appears anywhere in the bundle tree.**
`tools/` is `st_nlink == 1` (a real `shutil.copy2`), `evidence/` and `fixtures/` are `st_nlink == 2` — hardlinked to the
**session-scoped tmp** copies, never to tracked sources (`_session_bundle` itself uses `shutil.copy2` from `FIXTURES`, T:432-435).
**F19 is closed at the class, not just for the tee.** ✅
Residue: the killing test writes to the copy (`tee_copy.write_text`) and was added to `_EXEMPT_FNS` (T:3272) rather than routed
through `_rewrite`, so any future write inside `test_ck9_tools_not_hardlinked` is invisible to the F43 scan. The destructive step
is correctly *gated* behind the `st_nlink == 1` assert, so the tracked file cannot be written even if the fixture regresses.

---

## ITEM 11 — F21 strict xfails

Executed on a scratch copy of the real-leg corpus (`ck10/realleg`, copied from `scratchpad/realleg`; **the shared original was never written** —
re-verified afterwards: `probe_sha256 4e88997e2b74 agent_exit_code 0`), with `_REAL_LEG_DIR` re-pointed in a scratch test file:

| scenario | pytest outcome |
|---|---|
| **A** — stale reason repaired (`probe_sha256` set to the live `acp_probe.py` sha; `check_negative` then returns `observed: … Invalid params`) | **`1 passed, 343 deselected in 0.06s`** |
| **B** — an unrelated Failure (`agent_exit_code = 12345`) | **`1 failed`** — `AssertionError: unexpected failure: negative: negative: agent_exit_code is 12345, expected 0` ✅ the fail-open R9-CK-F21 named is closed |
| **C** — original stale sha restored | **`343 deselected, 1 xfailed in 0.18s`** — `XFAIL … real v2.2 sample: probe_sha256 mismatch (capture predates current probe)` ✅ matches the gate's "1 xfailed" |

**But two claims about the mechanism are false (F-R10-13).**
1. `grep -n "strict" tests/test_s0_01_check_acp_conformance.py` → **no `strict=True` anywhere.** The call is the *imperative*
   `pytest.xfail(reason)` (T:2793), which has no strict mode. The docstring at T:2780-2781 — "the strict=True ensures the test suite
   goes RED when the stale reason disappears" — describes a mechanism that does not exist, and behaviour A shows the opposite
   (it goes GREEN). The lane report's F21 row ("with `pytest.xfail(strict=True)`", "after re-capture these turn into failures by
   design") repeats it.
2. "on **exact** match of the three known-stale reasons": the code is `r == result or r in result` (T:2791) — still a **substring**
   match, and for the real reason (`negative: negative: probe_sha256 mismatch`) the `==` branch is **dead**; only the substring
   branch ever fires. Measured.

---

## ITEM 12 — F25 A25 reorder

Executed (`ck10/wk1`, `test_zz_a25_*`):
```
pure reorder  -> failure_reason: golden: check sequence mismatch - first out of order at #0: got check_initialize_frames:run-1, expected check_timeline:run-1
missing pair  -> failure_reason: golden: check sequence mismatch - first missing: check_env:run-2
```
Both messages are exactly right, and the reorder string is **character-for-character reproducible from `cc.EXPECTED_CHECK_SEQUENCE`**
inside the test (I computed it independently and diffed — identical). The old `first missing` message is preserved for a genuine omission. ✅

**But the new test asserts a fragment.** `test_ck9_a25_reorder_diagnostic` (T:4356) is
`assert "first out of order at #" in out` — a substring, in a test added by the very round that converted 11 other fragment
assertions to exact `==` (F7/F8/F9/F10/F13/F23). F-R10-14.

---

## THE COORDINATOR'S OWN HUNK — `_split_world` / AF-AP-59 (`tests/test_s0_01_pc_post_scan.py`)

**The diagnosis is right and reproducible from primary source.** `pc_post.sh:71` `keep = [r for r in rows if r[0] in owned or any(p in r[3] for p in PINNED)]` —
the body is world-scoped by construction, so four assertions that equated the body with the test's own spawn set were venue
assumptions, true only serially. The incident entry and registry row AF-AP-59 are accurate; the PC evidence
(run `20260907T161133Z` → `1 failed, 303 passed, 51 skipped`; run `20260907T161745Z-a60b933` → `304 passed, 51 skipped`) is a
genuine two-venue proof. `import pins` is placed after `_parse` with a `noqa: E402`; `sys` is already imported at the top; pyflakes is clean.

Three things I would still fix:

1. **The foreign branch is never executed in the sandbox, and has no committed negative control (F-R10-20).**
   `_split_world`'s `assert any(p in r[3] for p in _PINNED)` runs only when `foreign` is non-empty. In a serial sandbox the world
   is empty, so the loop body never runs — the whole point of the hunk is dead code in the venue that produces the
   `345 passed` gate of record. The commit message says "Negative control run: an unexplained `sleep 60` row rejected, a pinned
   foreign row accepted" — **run, not committed.** This repo's own AF-AP-36 ("a reviewer-reported mutation of a proof's evidence
   becomes a committed FAILING regression test") is the matching rule.
   **Red test to add** (deterministic, sandbox-runnable, no PC needed):
   ```python
   def test_split_world_rejects_an_unexplained_foreign_row():
       import pytest
       with pytest.raises(AssertionError, match="unexplained foreign row"):
           _split_world([(1, 0, 5, "/usr/bin/sleep 60")], owned=set())
   def test_split_world_admits_a_foreign_row_naming_a_pinned_path():
       own, foreign = _split_world([(1, 0, 5, f"python {pins.PINNED_TEE_PATH}")], owned=set())
       assert own == [] and len(foreign) == 1
   ```
2. **`pinned_present` lost its exactness for a one-sided bound.** `assert m.group(7) == "0"` → `assert int(m.group(7)) >= len(foreign)`
   (line 124). In the sandbox the true value is still `0`, so the bound is satisfied by `0 >= 0` and any *inflation* of
   `pinned_present` — the field the checker cross-checks against the body at `C:1252-1254` — is now unpinned in this test.
   Minimal tightening that survives a parallel venue:
   `assert int(m.group(7)) == len([r for r in rows if any(p in r[3] for p in _PINNED)]) + _dropped_helpers` is not derivable
   (the helper filter drops rows), so instead keep the world-empty case honest: `if not foreign: assert m.group(7) == "0"`.
3. **What the foreign assertion can and cannot catch — stated precisely.** `pc_post.sh:71` keeps a row only if
   `r[0] in owned or any(p in r[3] for p in PINNED)`, so *no foreign row the producer emits can fail the assertion by being
   unpinned*. The branch is therefore **not** a filter on the world; the one thing it can actually catch is a **divergence
   between the producer's owned closure and the test's own spawn set** — a row the producer counted as owned (via the
   buzz-descendant walk from `owned-pids.json`) that the test does not list, and that happens not to name a pinned path. That is
   a real and useful signal, but it is a *different* signal from the docstring's "every foreign row must be admissible under the
   producer's only other rule". Worth saying so in the docstring, and it is why the negative control had to be hand-constructed
   rather than produced by running `pc_post.sh`.
   Adjacent, unaddressed: `_split_world` keys on **PID**, and in `test_teardown_scan_after_a_clean_exit_is_empty_with_owned_present_zero`
   the owned PIDs are already dead — a recycled PID belonging to another xdist worker would be classified as *owned* and skip the
   foreign check entirely. Low probability, same AF-AP-59 family, not covered.

Reproduced statically from `pc_post.sh`; **not** reproduced by running `tests/test_s0_01_pc_post_scan.py` under a hostile world —
I deliberately did not spawn foreign `sleep` processes while my own gate runs were in flight, because those sleepers would have
appeared in the gate's own scan bodies and reddened my gate of record. Named as a deliberate skip.

---

## FINDINGS — everything found, no severity filtering

`C:` = `proofs/S0-01/check_acp_conformance.py`, `T:` = `tests/test_s0_01_check_acp_conformance.py`, `S:` = `tests/test_s0_01_pc_post_scan.py`, all at the PIN.

**F-R10-01 is retracted** — I first read the lane report's `PIN: d5b1b03e…` as a non-existent sha. It exists and is correct (the A5h
dispatch commit, an ancestor of my PIN, with byte-identical scope files). The id is left unused rather than renumbered so the
numbering in this document is stable. Two further self-corrections are recorded inline: the first `--timeout-s 3` datum for
F-R10-02 was not diagnostic (a clean run also exceeds 3 s) and was replaced with a 40 s kill against a measured 9 s baseline; and
my first fragment-assertion census compared the PIN against a tree carrying the PIN's own test file — re-measured from git, and the
lane's "11 converted" claim is **correct**.

### F-R10-02 — SOLID — the walk-before-read fix does not cover `tools/frame_tee.py`; a FIFO there still hangs to the cap
`C:416-420`:
```python
tee_file = HERE / "tools" / "frame_tee.py"
if not tee_file.exists():
    raise Failure(f"{leg}: tools/frame_tee.py absent (needed for tee_sha256)")
_chk("tee_sha256", _sha256_file(tee_file))
```
`.exists()` is TRUE for a FIFO — the exact idiom R9-CK-F2 was raised to remove — and `HERE/"tools"` is in **neither** walk root
(`C:1654` walks only `golden` and `_fixtures()`).
**Observed** (CLI, materialised PASS bundle, `mkfifo proofs/S0-01/tools/frame_tee.py`, load 3.9-4.6). Clean baseline first, so the
cap numbers are diagnostic: a clean run of the same bundle takes **9355 ms / 8819 ms, rc 0**. With the FIFO:
default cap (90 s) → **rc 124 at a 40 s external kill, no output**; `--timeout-s 25` (≈ 3× the clean runtime) →
`failure_reason: checker timed out after 25s`, **rc 70, 26 s**. Neither is explainable by normal runtime.
**Expected**: `failure_reason: run-1: tools/frame_tee.py is not a regular file` in < 1 s, the same treatment every other read path gets.
Also falsifies the comment at `C:1654`: "walk EVERY tree the checker reads — golden/ AND fixtures dir" — `tools/` is read and not walked.
**Minimal fix**: `tee_file = _require_file(HERE / "tools" / "frame_tee.py", leg, "tools/frame_tee.py")` (drop the bare `.exists()` branch;
`_require_file` already produces `<leg>: tools/frame_tee.py absent`), **or** add `(HERE / "tools", "tools")` to `walk_roots`.
**Exact red test**:
```python
def test_ck10_fifo_at_tools_frame_tee_is_named(bundle, tmp_path):
    import time
    tee = tmp_path / "tools" / "frame_tee.py"          # HERE is monkeypatched to tmp_path
    tee.unlink(); os.mkfifo(tee)
    t0 = time.monotonic(); rc, out = _check(bundle, timeout_s=10)
    assert time.monotonic() - t0 < 5
    assert (rc, out) == (1, "failure_reason: run-1: tools/frame_tee.py is not a regular file")
```
*Threat-model note*: `proofs/S0-01/tools/` is a tracked repo path, not attacker-controlled evidence, so this is a
robustness/consistency hole rather than an evidence-forgery hole. It is still the class the round declared closed.

### F-R10-07 — SOLID — a directory named `manifest-post.summary` still produces the generic `IsADirectoryError` reason
`C:1696-1699` (the A1 pre-read, which runs **before** the per-leg allowlist loop):
```python
post_sum_path = d / "manifest-post.summary"
if post_sum_path.exists():
    _, post_ts = _parse_summary(post_sum_path, leg, "manifest-post.summary")   # -> read_text() at C:1039
```
No `_require_file`. **Observed**: `failure_reason: malformed evidence: IsADirectoryError: [Errno 21] Is a directory: '…/run-1/manifest-post.summary'` (rc 1, 160 ms).
**Expected**: `failure_reason: run-1: manifest-post.summary is not a regular file` — what the other **19** of 20 allowlisted names produce.
This is verbatim the shape R9-CK-F27 named, and the lane report's F27 row claims "`_require_file` S_ISREG gate covers **every read path**".
**Minimal fix**: `if post_sum_path.exists(): _require_file(post_sum_path, leg, "manifest-post.summary")` before `_parse_summary`.
**Exact red test**:
```python
def test_ck10_dir_named_manifest_post_summary(bundle):
    p = bundle / "golden" / "run-1" / "manifest-post.summary"
    p.unlink(); p.mkdir()
    rc, out = _check(bundle)
    assert (rc, out) == (1, "failure_reason: run-1: manifest-post.summary is not a regular file")
```

### F-R10-08 — SOLID — the F43 self-test threshold is slack by one; three pattern families can be deleted and it stays green
`T:3363` `assert len(self_violations) >= 6`. The self-test source has six violating *statements* but yields **seven** violations,
because `json.dump(obj, open(p, "w"))` is two `Call` nodes. Measured:
| mutant | result |
|---|---|
| `_SHUTIL_WRITERS = set()` | `1 passed, 343 deselected in 0.52s` — **SURVIVES** |
| `_OS_WRITERS = set()` | `1 passed, 343 deselected in 0.52s` — **SURVIVES** |
| `if False and … func.attr == "dump"` | `1 passed, 343 deselected in 0.51s` — **SURVIVES** |
| `_WRITE_ATTRS = set()` | `1 failed … assert 5 >= 6` — killed |
| builtin-`open` mode branch off | `1 failed … assert 5 >= 6` — killed |
The docstring at `T:3276-3278` ("Both the real test and the self-test call this function — **disabling the scan disables both**") is
false for those three.
**Minimal fix** — assert the *categories*, not a count:
```python
cats = {v.split(": ", 1)[1].split("(")[0] for v in self_violations}
assert cats == {".write_text", ".write_bytes", "open", "json.dump", "shutil.copy", "os.replace"}, self_violations
```
**Exact red test**: the assertion above, run with `_SHUTIL_WRITERS = set()` — currently green, must go red.
Coverage gaps in the scan itself (each planted one at a time, measured): **MISSED** — `os.open`+`os.write`, `Path.touch`,
`Path.rename`/`Path.replace` (method form), `p.open(mode="w")` (keyword — the builtin-`open` branch checks `keywords`, the `.open`
branch checks only `args[0]`), `open(p, m)` with a variable mode, `shutil.copytree`, `shutil.move`, `io.open`, a module-level write
(`fn_name is None` → `continue`, T:3300), `subprocess.run(["cp", …])`. **CAUGHT** — `open(p,"w")`, `write_text`, `write_bytes`,
`shutil.copy`, `json.dump`, `os.replace`, `os.rename`, a non-exempt module-level helper, a nested fn, a class method.
Note `shutil.copytree` cannot be added to `_SHUTIL_WRITERS` without flagging the `bundle` fixture itself (`T:461-471`, three
`copytree` calls, and `bundle` is **not** in `_EXEMPT_FNS`) — the writer set is fitted to the file, not to the threat.

### F-R10-03 — SOLID — `check_bundle(timeout_s=True)` is accepted and installs a silent 1-second cap
`C:1636` `if timeout_s is not None and timeout_s <= 0:` — `True <= 0` is `False`. Instrumented `signal.alarm` call list: **`[True, 0]`**.
The checker's own convention elsewhere is that a bool is **not** an int (`_is_strict_int`, `C:210-212`, used on all five tee-status counters).
**Observed**: `check_bundle(root, timeout_s=True)` → runs with a 1 s cap. **Expected**: `ValueError: timeout_s must be a positive integer`.
**Minimal fix**: `if timeout_s is not None and not (_is_strict_int(timeout_s) and 0 < timeout_s <= 2**31 - 1): raise ValueError(...)`.
**Exact red test**: `with pytest.raises(ValueError, match="positive integer"): cc.check_bundle(Path(td), timeout_s=True)`.

### F-R10-05 — SOLID — the positivity floor does not reject NaN; only CPython's `alarm()` type check does
`float("nan") <= 0` is `False`, so `NaN` walks straight through `C:1636` and is stopped one frame later by
`signal.alarm` raising `TypeError`. Reproduced: `check_bundle(root, timeout_s=float('nan'))` → `TypeError: 'float' object cannot be
interpreted as an integer`. Fail-closed **today, by luck of the sink**: if the cap were ever re-implemented on a deadline
(`time.monotonic() + timeout_s`) instead of `signal.alarm`, NaN would silently disable it — the exact wormhole
`CLAUDE.md` tactic 1 names and `docs/INCIDENT-LOG.md` records as having bitten twice.
**Minimal fix**: the same strict-int guard as F-R10-03 (it subsumes NaN/inf/float/str).
**Exact red test**: `for bad in (float("nan"), float("inf"), 1.0, "5"): with pytest.raises(ValueError, match="positive integer"): cc.check_bundle(Path(td), timeout_s=bad)`.

### F-R10-04 — SOLID — an out-of-range `--timeout-s` is reported as *malformed evidence*, not as a usage error
`C:1812-1817` accepts any `int`; `C:1627` `_signal.alarm(timeout_s)` then raises `OverflowError` for anything ≥ 2**31, which
`main()`'s catch-all (`C:1833-1835`) turns into rc 1.
**Observed**: `--timeout-s 2147483648` (and 2**32-1, 2**40) → `failure_reason: malformed evidence: OverflowError: Python int too large to convert to C int`, **rc 1**.
**Expected**: rc **64** and `usage: --timeout-s must be a positive integer` — the module docstring itself defines 64 as
"fatal usage — missing/invalid arguments". A bad operator flag must not be recorded as bad evidence in a proof system.
**Minimal fix**: `if not (0 < timeout_s <= 2**31 - 1): print("usage: --timeout-s must be a positive integer", file=sys.stderr); return 64`.
**Exact red test**:
```python
def test_ck10_timeout_arg_out_of_range_is_a_usage_error():
    r = subprocess.run([sys.executable, str(CHECKER), "--timeout-s", str(2**31), "/tmp/x"],
                       capture_output=True, text=True, timeout=10)
    assert r.returncode == 64
    assert r.stderr.strip() == "usage: --timeout-s must be a positive integer"
```

### F-R10-15 — SOLID — `_check_with_timeout` leaks the SIGALRM handler when `alarm()` itself raises
`C:1624-1631`:
```python
old = _signal.signal(_signal.SIGALRM, _raise_timeout)
_signal.alarm(timeout_s)        # <-- OUTSIDE the try
try:
    return fn(*args)
finally:
    _signal.alarm(0)
    _signal.signal(_signal.SIGALRM, old)
```
**Observed** (executed): `signal.getsignal(SIGALRM)` before = `0` (SIG_DFL); `check_bundle(root, timeout_s=2**31)` → `OverflowError`;
after = `<function _check_with_timeout.<locals>._raise_timeout>` — **`LEAKED: True`**. Same for a float/NaN cap (`TypeError`).
**Expected**: the process's SIGALRM disposition unchanged after a failed call. The audience is exactly the in-process consumers the
cap was moved inside `check_bundle` for (`C:1633-1634`); the next SIGALRM from any source then prints
`failure_reason: checker timed out after 2147483648s` and raises `SystemExit(70)` inside unrelated code.
This is an **unexploded sibling of AF-AP-58** — and `docs/INCIDENT-LOG.md`'s echo sweep explicitly *cleared* this site
("its handler raises SystemExit(70) with the reason already printed … alarm granularity (≥ 1 s) makes the microsecond gap
unreachable: not an echo"). That clearance reasons about a signal arriving in the gap; the live defect is that `alarm()` **itself**
raises and skips the `finally`.
**Minimal fix**: move `_signal.alarm(timeout_s)` inside the `try:` (the `finally` already cancels and restores), or validate the
domain in `check_bundle` before installing anything (F-R10-03's guard does both).
**Exact red test**:
```python
def test_ck10_sigalrm_handler_restored_after_a_bad_cap():
    import signal
    before = signal.getsignal(signal.SIGALRM)
    with pytest.raises(Exception):
        cc.check_bundle(Path("/tmp"), timeout_s=2**31)
    assert signal.getsignal(signal.SIGALRM) is before
```

### F-R10-06 — SOLID — the CLI's default cap is an untested second literal; the documented "90 < the runner's 120" invariant is unpinned
`C:1633` `def check_bundle(root: Path, timeout_s: int = 90)` and `C:1798` `timeout_s = 90` in `main()` are independent constants,
and `spec.json` invokes the checker with **no** `--timeout-s`, so the one that governs the proof runner is `C:1798`.
Measured on `-k "cli or timeout or default or fifo or usage"` (16 selected):
| mutant | result |
|---|---|
| `SIG-DEFAULT-900` (`C:1633` 90→900) | `1 failed, 15 passed, 328 deselected in 13.52s` — killed by `test_ck9_default_timeout_is_90` |
| **`MAIN-DEFAULT-900`** (`C:1798` 90→900) | **`16 passed, 328 deselected in 13.62s` — SURVIVES** |
**Minimal fix**: delete the duplicate — `main()` should start from `inspect.signature(check_bundle)...default`, or simply
`timeout_s = None` and pass it through so `check_bundle`'s own default applies; then assert `< 120` in the test.
**Exact red test**:
```python
def test_ck10_cli_default_cap_is_below_the_runner_timeout():
    src = CHECKER.read_text()
    import ast, json
    spec = json.loads((P / "spec.json").read_text())
    tree = ast.parse(src)
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    lit = next(n.value.value for n in ast.walk(main)
               if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "timeout_s"
               and isinstance(n.value, ast.Constant))
    assert 0 < lit < spec["timeout_s"]
```
(and `MAIN-DEFAULT-900` must then die).

### F-R10-11 — SOLID — the `owned_zombies` rule is weaker than the producer's invariant, and covers only the after-scan
`C:1259` `if _owned_zombies > int(hdr.group(5)):`. From `proofs/S0-01/tools/pc/pc_post.sh:40-44, 71-75`, `zombies` are `continue`d
before `rows.append`, so `table_pids` (hence `owned_present`) and `owned_zombies` are **disjoint** subsets of `owned`.
**Observed**: a header with `owned=3 owned_present=3 owned_zombies=3` — arithmetically impossible for the producer — **PASSES (rc 0)**.
**Expected**: rejected. R9-CK-F11's own proposed fix was `group(8) + group(6) <= group(5)`; only the `> owned` half landed.
Second gap: `grep -n "group(8)" C` → one hit; the **teardown** scan's `td_hdr.group(8)` is never consumed (`C:1333-1353`).
**Minimal fix**:
```python
if _owned_zombies + int(hdr.group(6)) > int(hdr.group(5)):
    raise Failure(f"{leg}: process-scan-after.txt owned_present={hdr.group(6)}+owned_zombies={_owned_zombies} exceeds owned={hdr.group(5)}")
```
plus the same two lines against `td_hdr` in the teardown block.
**Exact red test**: rewrite `run-1/process-scan-after.txt`'s header with `owned_zombies=3` (owned=3, owned_present=3) and assert
`out == "failure_reason: run-1: process-scan-after.txt owned_present=3+owned_zombies=3 exceeds owned=3"` — today this returns rc 0 PASS.

### F-R10-12 — SOLID — `LITERAL-PINS-2U` survives: the two-users env pin has no consumption test
`C:490` `_expected_rt_env = PINNED_STARTUP_RESPOND_TO_TWO_USERS.split("(")[0]`. Mutant → `_expected_rt_env = "allowlist"` (the literal
F12 exists to remove): **`30 passed, 314 deselected in 38.10s` — SURVIVES** over `-k "env or pin or twousers or two_users"`.
`test_ck9_env_respond_to_from_pin` patches only `PINNED_STARTUP_RESPOND_TO`, and asserts a **substring** (`T:4288`) rather than the exact reason.
**Minimal fix / exact red test**:
```python
def test_ck10_env_respond_to_two_users_from_pin(bundle, monkeypatch):
    monkeypatch.setattr("check_acp_conformance.PINNED_STARTUP_RESPOND_TO_TWO_USERS", "PATCHED(9)")
    rc, out = _check(bundle)
    assert (rc, out) == (1, "failure_reason: two-users: env BUZZ_ACP_RESPOND_TO should be 'PATCHED' for two-users")
```
and make `T:4288` `assert out == "failure_reason: run-1: env BUZZ_ACP_RESPOND_TO should be 'PATCHED_RT'"`.

### F-R10-13 — SOLID — there is no `strict=True`; the docstring and the report describe a mechanism that does not exist
`grep -n "strict" tests/test_s0_01_check_acp_conformance.py` → **no `strict=True` anywhere**. `T:2793` is the imperative
`pytest.xfail(reason)`, which has no strict mode. `T:2780-2781` says "the strict=True ensures the test suite goes RED when the
stale reason disappears"; **measured**, when the stale reason disappears the test goes **`1 passed`**, not red.
Second: "on **exact** match" — `T:2791` is `r == result or r in result`; for the real reason
(`negative: negative: probe_sha256 mismatch`) the `==` branch is dead and only the substring branch fires.
**Minimal fix**: either (a) make it honestly a substring xfail and correct the docstring/report, or (b) implement what the design
asked: match on the trailing segment exactly — `result.rsplit(": ", 1)[-1] in _KNOWN_XFAIL_REASONS` — and, if the "goes RED at
re-capture" behaviour is really wanted, replace the imperative call with a computed `pytest.xfail`-marker via
`request.node.add_marker(pytest.mark.xfail(strict=True, reason=…))` **before** running the check.
**Exact red test**:
```python
def test_ck10_known_xfail_match_is_anchored():
    for r in ("probe_sha256 mismatch",):
        assert r not in "negative: negative: probe_sha256 mismatch and an injected payload"  # currently FALSE -> red
```
(state which semantics you want first; today the code and its prose disagree.)

### F-R10-10 — SOLID — 4 of the 6 dead-branch deletion comments cite a guard that does not enforce what they claim
`C:948-950`, `C:958-959`, `C:1561-1562`, `C:1590-1591` all name `check_initialize_frames` as the guarantor.
`check_initialize_frames` (`C:713-741`) validates **only** the `initialize` request/response pair — it never inspects
`stopReason`, never counts `session/new`, never touches the `session/new` response.
The real guarantors (executed, see item 6): `check_two_users`' own `C:894-895`/`C:906-907`/`C:922-925`, and `check_prompt_turn`'s
`C:747-749`. CK9's own table cited these correctly (`C:888`, `C:904-906`, `C:725-726`); the comments regressed them.
**Observed**: the code is correct; the *recorded reason it is correct* is wrong, and it is the only such record.
**Minimal fix**: replace `check_initialize_frames` with the true citation in each of the four comments.
**Exact red test** (a structural pin, cheap and durable):
```python
def test_ck10_dead_branch_comments_cite_a_real_guard():
    src = CHECKER.read_text().splitlines()
    for lineno, fn in ((949, "check_two_users"), (958, "check_two_users"),
                       (1561, "check_prompt_turn"), (1590, "check_prompt_turn")):
        block = "\n".join(src[lineno - 3:lineno + 1])
        assert fn in block, f"C:{lineno} cites the wrong guard: {block}"
```

### F-R10-16 — SOLID — the F13 parametrised test can silently drop keys
`T:4386-4388`:
```python
if new_startup == old:
    continue  # parenthesised values need special handling, skip
```
Nothing counts the keys that actually ran. **Measured today: 19 of 19 exercised, 0 skipped** (instrumented run) — so the coverage
claim is true *now*, and latent thereafter: any change to a pin's rendering silently removes that key from the suite with the test
still green.
**Minimal fix / exact red test**: collect `ran` and end the test with `assert len(ran) == len(checks), sorted(set(checks) - set(ran))`;
it goes red the moment a substitution stops matching.

### F-R10-14 — SOLID — the new A25 test asserts a fragment
`T:4356` `assert "first out of order at #" in out`, added by the round whose F7/F8/F9/F10 work converted 11 fragment assertions to
exact `==`. The full string is computable inside the test from `cc.EXPECTED_CHECK_SEQUENCE` — I computed it independently and it
matches character-for-character.
**Minimal fix / exact red test**:
```python
exp = cc.EXPECTED_CHECK_SEQUENCE
assert out == (f"failure_reason: golden: check sequence mismatch - first out of order at #0: "
               f"got {exp[1][0]}:{exp[1][1]}, expected {exp[0][0]}:{exp[0][1]}")
```

### F-R10-21 — SOLID (low) — the module docstring's NOTE reads as a statement of current behaviour
`C:2-3`: "``--timeout-s`` must be a positive integer (R9-CK-F1); zero or negative **silently cancels the SIGALRM cap**."
As of this commit zero/negative is refused with rc 64 before anything is installed. The clause is defensible as *rationale*
("…because alarm(0) would cancel it"), but as written a reader concludes the current binary silently uncaps.
**Minimal fix**: "…must be a positive integer (R9-CK-F1): `alarm(0)` and `alarm(-N)` would cancel the cap, so a non-positive value is refused with exit 64."

### F-R10-09 — SOLID — 11 CONTROL tests are labelled "RED-BEFORE" in the lane report
Measured against the parent checker: `test_ck9_no_tee_parented_by_buzz` (F4), the five FINAL-arm tests + `_stdin_reader_done` (F5, 6 params),
`test_ck9_startup_wrong_value_parametrised` (F13), `ck9_post_roles_reordered`/`_duplicated` (F20), `ck9_running_seq_lag_2`/`_recorded_deficit_2` (F29)
— **all GREEN on the parent**. The report's cells open with "RED-BEFORE:" and then state a *mutant survival*, which is the CONTROL+killer
form the report's own column header offers. The substance (the mutants did survive at the parent — CK9 reproduced that) is true; the
label is not. Only the F19 row is correctly marked "CONTROL+…".
**Minimal fix**: relabel those rows "CONTROL + killer (mutant X survived at the parent)".

### F-R10-17 — SOLID — the lane report's `file:line` refs are stale on the test-file side, and two checker refs are wrong
Spot-checked 26 refs. Checker side: 11 exact; **2 wrong** — `C:1808-1810` (claimed: the F1 CLI guard) is the *missing-argument*
usage branch, the guard is at **C:1815-1817**; `C:1618-1635` (claimed: the walk block) is the `check_bundle` region, the walk is at
**C:1650-1669**. Test side: 11 of 13 off by 1-23 lines (`_scan_direct_writes` claimed T:3252, actual **T:3275**; F4 claimed T:4051,
actual **T:4043**; F29 claimed T:4199, actual **T:4210**; F13 claimed T:4353, actual **T:4360**; `_check` claimed T:499, actual **T:498**),
and 4 of the 11 "exact-reason conversion" refs (T:2341, T:2426, T:3095, T:3110) point at non-assertion lines — the assertions are 1-5
lines further down and **do** exist (T:2342, T:2428, T:3098, T:3115). Likewise T:2284→**T:2289**, T:2350→**T:2359**, T:2402→**T:2403**.
Cause is visible in the report itself: the DONE table was written before `test_ck9_owned_zombies_exceeds_owned` (+10 lines at T:4259)
and the `_EXEMPT_FNS` fix, and was not re-derived. Nothing is fabricated; every claimed change exists.

### F-R10-18 — SOLID — the lane report's Collection-count section describes the pre-follow-up bytes
Report: "343 items collected from `test_s0_01_check_acp_conformance.py` … = 354 total. 344 passed + 9 skipped + 1 xfailed = 354."
Measured at the PIN: that file collects **344** (every `-k` run reports `N selected + (344-N) deselected`), and the committed bytes give
**355** collected / `345 passed, 9 skipped, 1 xfailed` (the commit message's gate of record, which I reproduce below). The report's own
FINAL FILE HASHES block *is* the committed bytes. So the hashes and the counts in one document describe two different trees.
**Minimal fix**: re-derive the collection block on the final bytes (the report already declares the clean full gate NOT_DONE, which is honest —
the count block should say the same).

### F-R10-19 — SOLID — the lane report mis-diagnoses its own red run, and the diagnosis was never reproduced
Report DISCREPANCIES §4 / SELF-ATTACK §1: "Run 2 (99 failures) was resource contention, not a code regression … 8 concurrent pytest
processes". The commit message says something different and far more plausible: "the lane's own second run hit 99 failures because lane
B5f was editing the tee under it — the `tee_sha256` moving-target artifact". A moving `tee_sha256` fails `check_runtime_identity` in
**every** bundle test deterministically; contention produces slowness, not 99 deterministic failures. The lane accepted a cause it did not
reproduce (`CLAUDE.md` build-loop 3: "an unexpected test failure indicts YOUR assumption first … reproduce before believing any recorded
diagnosis"), and the report was not corrected when the coordinator found the real cause.
**Minimal fix**: correct the report's two sections to the tee-moving-target cause and cite the commit message.

### F-R10-20 — SOLID — `_split_world`'s foreign branch has no committed negative control and is never executed in the sandbox
See the coordinator-hunk section. `S:90-91`. The two red tests are given there.

### F-R10-22 — UNSURE (low) — `_check(timeout_s=60)` makes ~340 tests load-sensitive
`T:498`. A single `check_bundle` costs ~0.15-9 s here (load 0.3-2.5); the new 60 s cap is ~6.6× the worst nominal. On a heavily
contended box a test asserting `rc == 1` would instead see `(70, "failure_reason: checker timed out")`. This is the right trade
(a walk regression now fails instead of wedging the suite) and I could not make it fire, but it is a new failure mode on a box that
has already produced a 99-failure run. Noted, not reproduced.

---

## MUTANT TABLE — every mutant I ran (scratchpad copies only; `sha256sum -c` on both scope files after each restore, all `OK`)

Harness: `ck10/wk3` (a `git archive` copy of the PIN). One mutation at a time; the file is restored from `ck10/pin` and its sha
re-verified before the next. `git status --porcelain` on `/home/user/agent-factory` was checked at open and close and was never
touched by me (other lanes' 5 dirty files + 1 untracked, unchanged).

### A. The lane's FINAL-arm / RUNNING-bound set — 3 runs each, killer subset (`ck10/mutants.log`)

| mutant | line | run 1 | run 2 | run 3 | verdict |
|---|---|---|---|---|---|
| control `ck9_final_arm_forwarded_exact` | — | `2 passed, 342 deselected in 18.05s` | | | green |
| control `ck9_final_arm_recorded_exact` | — | `2 passed, 342 deselected in 19.52s` | | | green |
| control `ck9_final_arm_updated_seq` | — | `1 passed, 343 deselected in 10.48s` | | | green |
| control `ck9_final_stdin_reader_done` | — | `1 passed, 343 deselected in 10.43s` | | | green |
| control `ck9_running_seq_lag_2` | — | `1 passed, 343 deselected in 10.65s` | | | green |
| control `ck9_running_recorded_deficit_2` | — | `1 passed, 343 deselected in 10.65s` | | | green |
| control `ck9_final_arm_float_rejected` | — | `3 passed, 341 deselected in 26.42s` | | | green |
| **FINAL-RELAXED-fwdc2a** | C:1414 `!=`→`==` | `2 failed, 342 deselected in 19.06s` | `… 18.93s` | `… 19.20s` | **KILLED ×3** |
| **FINAL-RELAXED-fwda2c** | C:1416 | `1 failed, 1 passed, 342 deselected in 18.53s` | `… 18.82s` | `… 18.67s` | **KILLED ×3** |
| **FINAL-RELAXED-recc2a** | C:1418 | `2 failed, 342 deselected in 18.40s` | `… 18.98s` | `… 20.60s` | **KILLED ×3** |
| **FINAL-RELAXED-reca2c** | C:1420 | `1 failed, 1 passed, 342 deselected in 18.62s` | `… 18.64s` | `… 18.49s` | **KILLED ×3** |
| **FINAL-RELAXED-seq** | C:1422 | `1 failed, 343 deselected in 10.84s` | `… 10.50s` | `… 10.95s` | **KILLED ×3** |
| **FINAL-RELAXED-stdin** | C:1465-1466 deleted | `1 failed, 343 deselected in 10.81s` | `… 10.81s` | `… 10.51s` | **KILLED ×3** |
| **RUN-DIFF2** | C:1440 `(0,1)`→`(0,1,2)` | `1 failed, 343 deselected in 10.89s` | `… 10.48s` | `… 10.79s` | **KILLED ×3** |
| **RUN-RECDEF2** | C:1446 `(0,1)`→`(0,1,2)` | `1 failed, 343 deselected in 11.98s` | `… 10.50s` | `… 10.79s` | **KILLED ×3** |
| **RUN-FWD2** | C:1435 `(0,1)`→`(0,1,2)` | `3 failed, 22 passed, 5 skipped, 314 deselected in 186.18s` | `… 191.51s` | `… 188.79s` | **KILLED ×3** |

All six FINAL-RELAXED mutants and both RUNNING upper-bound mutants **die on the named ck9 test**, deterministically over 3 runs.
R9-CK-F5 and R9-CK-F29 are closed.

### B. My own mutants

| mutant | file:line | result | verdict |
|---|---|---|---|
| `MAIN-DEFAULT-900` | C:1798 `90`→`900` | `16 passed, 328 deselected in 13.62s` | **SURVIVES** (F-R10-06) |
| `SIG-DEFAULT-900` | C:1633 `90`→`900` | `1 failed, 15 passed, 328 deselected in 13.52s` | killed |
| `MAIN-DEFAULT-3` | C:1798 `90`→`3` | `1 failed, 15 passed, 328 deselected in 7.56s` | killed **incidentally** (a >3 s CLI run trips the cap; the value is not pinned) |
| `F43-SHUTIL-OFF` | T:3264 `set()` | `1 passed, 343 deselected in 0.52s` | **SURVIVES** (F-R10-08) |
| `F43-OSW-OFF` | T:3265 `set()` | `1 passed, 343 deselected in 0.52s` | **SURVIVES** (F-R10-08) |
| `F43-JSONDUMP-OFF` | T:3326 `if False and …` | `1 passed, 343 deselected in 0.51s` | **SURVIVES** (F-R10-08) |
| `F43-ATTRS-OFF` (lane's) | T:3263 `set()` | `1 failed, 343 deselected in 0.60s` (`assert 5 >= 6`) | killed |
| `F43-MODEOPEN-OFF` | T:3311 `if False and …` | `1 failed, 343 deselected in 0.62s` | killed |
| `LITERAL-PINS-2U` | C:490 → literal `"allowlist"` | `30 passed, 314 deselected in 38.10s` | **SURVIVES** (F-R10-12) |
| `TYPEGATE-OFF` | C:1404-1407 deleted | *(see below)* | |

### C. The 24-guard combined mutant, re-derived at the PIN

A5e's 24-guard line list, re-mapped from the **parent** checker (`cc80f7b7…`, byte-identical to CK9's PIN) to the PIN by **exact
source-line text**: 24 of 27 map verbatim; three needed content-matching because the round changed their indentation or text —
`if not (owner_ev["created_at"] < …)` (parent 931 → **PIN 952**, dedented by the F6 deletion), `if new_seqs[1]["seq"] < …`
(parent 938 → **PIN 960**, dedented), and `if sid1 is not None and sid2 is not None and sid1 == sid2:`
(parent 1559 → **PIN 1594** as `if sid1 == sid2:`, the F6 weakening). Final PIN target set (27 `if` lines, each rewritten
`if <cond>:` → `if False and (<cond>):`, pyflakes rc 0 after patching, 27 occurrences of `if False and (` verified):

`338 340 356 362 952 960 1281 1285 1306 1314 1329 1334 1336 1338 1341 1412 1416 1418 1430 1435 1446 1453 1468 1476 1534 1594 1596`

*(full-suite result below in the gate section)*

### D. The lane's remaining MUTANT-table rows + my four survivors — **clean serial re-run in `ck10/wk6`**
Every row below comes from `ck10/redo.log`: a dedicated tree, one mutant at a time, a **pristine-sha pre-check before each
mutation**, a no-op check after it, and a restore + `sha256sum -c` at the end (`proofs/…: OK`, `tests/…: OK`). Load 3.4-4.2.

| mutant | mutation | pytest summary (verbatim) | verdict |
|---|---|---|---|
| control (roles subset) | none | `4 passed, 340 deselected in 2.52s` | green |
| `ROLES-SET` | C:657 `roles !=` → `set(roles) !=` | `2 failed, 2 passed, 340 deselected in 19.71s` | **KILLED** |
| `TEEPAR-OFF` | C:1295 `raise` → `pass` | `1 failed, 9 passed, 334 deselected in 55.39s` | **KILLED** — proves `test_ck9_no_tee_parented_by_buzz` reaches C:1295, closing R9-CK-F4 |
| `CAP-ZERO-ACCEPTED` | C:1636-1637 deleted | `1 failed, 2 passed, 341 deselected in 0.88s` | **KILLED** |
| `REQFILE-EXISTS` | C:198-199 deleted (the `S_ISREG` gate) | `2 failed, 1 passed, 341 deselected in 2.79s` | **KILLED** |
| `ZOMBIES-UNCHECKED` | C:1259-1260 deleted | `1 failed, 2 passed, 341 deselected in 26.33s` | **KILLED** |
| `LITERAL-PINS` | C:496 pin → literal `"owner-only"` | `1 failed, 343 deselected in 2.95s` | **KILLED** |
| **`LITERAL-PINS-2U`** | C:490 → literal `"allowlist"` | **`30 passed, 314 deselected in 39.64s`** | **SURVIVES** (F-R10-12) |
| `A25-MEMBERSHIP` | C:1779-1784 deleted (the reorder loop) | `1 failed, 2 passed, 341 deselected in 26.84s` | **KILLED** |
| `HARDLINK-FIXTURE` | T:470 `shutil.copy2` → `os.link` | `1 failed, 343 deselected in 2.77s` | **KILLED** |
| `TYPEGATE-OFF` (mine) | C:1404-1407 deleted (the pre-arm `_is_strict_int` loop) | `3 failed, 341 deselected in 29.42s` | **KILLED** |
| **`MAIN-DEFAULT-900`** | C:1798 `90` → `900` | **`16 passed, 328 deselected in 13.78s`** | **SURVIVES** (F-R10-06) |
| **`F43-SHUTIL-OFF`** | `_SHUTIL_WRITERS = set()` | **`1 passed, 343 deselected in 0.51s`** | **SURVIVES** (F-R10-08) |
| **`F43-OSW-OFF`** | `_OS_WRITERS = set()` | **`1 passed, 343 deselected in 0.51s`** | **SURVIVES** (F-R10-08) |

**14 mutants killed, 4 survive.** The four survivors are findings F-R10-06, F-R10-08 (×2 families, plus `F43-JSONDUMP-OFF` measured
separately) and F-R10-12.

**Discrepancy in the lane's own table:** `REQFILE-EXISTS` and `ALLOWLIST-NAME-ONLY` are listed as two mutants with the **same**
mutation ("C:195-199 deleted (S_ISREG gate)"). They are one mutant under two names. The lane brief's separate design item — "the
per-leg entry allowlist (`C:1674-1677`) checks the entry TYPE as well as the name" — was **not** implemented as an allowlist change:
`C:1716-1718` still tests only `item.name not in allowed`, and the type verdict comes from `_require_file` downstream. That works for
19 of the 20 allowlisted names and is exactly why `manifest-post.summary` leaks (F-R10-07), since its earliest consumer
(`C:1697-1699`) runs before the allowlist loop and never calls `_require_file`.

---

## WHAT I REPRODUCED · WHAT I REVIEWED STATICALLY · WHAT I DELIBERATELY SKIPPED

### Reproduced (executed this session, on `git archive` copies of the PIN)
- The premise: PIN existence, `git log`, `git status`, per-file sha of both scope files vs the lane report's FINAL FILE HASHES,
  the tee's 466 lines / `061dd10c…`, the lane report's PIN (`d5b1b03`) and its byte-identity with `618749f`.
- The full `--timeout-s` CLI domain (16 values) and the in-process `check_bundle` domain (13 values, incl. an instrumented
  `signal.alarm` call list for `True`), plus the SIGALRM-handler-restoration probe.
- The default cap firing end-to-end (rc 70, exact reason) with `main()`'s literal scratch-patched to 2 s.
- `MAIN-DEFAULT-900` / `SIG-DEFAULT-900` / `MAIN-DEFAULT-3`.
- The non-regular class at nine paths + a directory named after each of the 20 allowlisted per-leg files, all through the **CLI**
  against a materialised PASS bundle, under the **default** cap.
- The FIFO-at-`tools/frame_tee.py` hang (rc 124 at 15 s; rc 70 with `--timeout-s 3`).
- `_scan_direct_writes`: 5 pattern-family mutants, 19 planted write vectors, and a standalone re-execution of the scan on the
  self-test source proving the 7-vs-6 slack.
- The 38-shape A21d table (0 mismatches, reasons identical to CK9) and an 84-shape type/NaN matrix on both arms (BAD=0).
- 16 checker mutants (FINAL-RELAXED ×6, RUN-DIFF2/RECDEF2/FWD2, TYPEGATE-OFF, ROLES-SET, TEEPAR-OFF, CAP-ZERO-ACCEPTED,
  REQFILE-EXISTS, ZOMBIES-UNCHECKED, LITERAL-PINS, LITERAL-PINS-2U, A25-MEMBERSHIP) + 2 test-file mutants (HARDLINK-FIXTURE, F43 family).
- The PIN's tests against the PARENT checker (`13 failed, 17 passed, 314 deselected in 152.01s`) — the red-before/CONTROL split.
- 10 hostile bundles for the six deleted dead branches, plus 3 direct calls into `check_two_users`.
- The F17 differential: 43 218 live-reachable status shapes (0 differences) and 43 218 direct-call-only shapes (13 differences).
- `owned_zombies` over 8 header values; `BUZZ_ACP_RESPOND_TO` over 5 values; `--fixtures-dir` over 3 hostile shapes.
- The fixture inode/nlink audit over the whole bundle tree.
- The F21 xfail behaviour in all three states (repaired → `1 passed`; unrelated failure → `1 failed`; stale → `1 xfailed`).
- The A25 reorder and missing-pair messages, and an independent recomputation of the reorder string from `EXPECTED_CHECK_SEQUENCE`.
- The F13 parametrised test instrumented (19/19 keys exercised, 0 silently skipped).
- The REAL tee at the PIN under SIGTERM (rc 70) and clean exit (rc 0), both statuses ACCEPTED by the PIN's `check_tee_status`.
- A live `ps -eww` census showing **zero** processes in this sandbox can name any `_PINNED` path (they are PC-absolute `/home/rocco/…`).
- 26 of the lane report's `file:line` refs.

### Reviewed statically (traced from primary source, not executed)
- The dominance argument for each deleted branch (each is also backed by an executed hostile bundle; the *static* part is that no
  other caller reaches those functions — `EXPECTED_CHECK_SEQUENCE` is the sole dispatcher).
- `pc_post.sh`'s zombie/`table_pids`/`owned_present` partition (read, not run — the producer needs a PC-shaped tree).
- The threat-model reachability of `proofs/S0-01/tools/` (a tracked repo path, not evidence).

### Deliberately skipped, with reasons
- **The PC leg.** No bridge banner this session; `.pc-bridge.env` is not present. The PC gate of record (`304 passed, 51 skipped in
  129.81s`, run `20260907T161745Z-a60b933`) is **carried from the commit message, not reproduced by me** — see the verdict line.
- **`-n 8` / xdist.** Not installed in `/root/venv-agent-factory` (CK9 recorded the same); the parallel venue is PC-only.
- **Running `tests/test_s0_01_pc_post_scan.py` under a hostile world.** Spawning foreign `sleep` processes would have put rows in the
  scan bodies of my own gate runs of record. Skipped on purpose; the structural argument (no sandbox process can name a `_PINNED`
  path) is measured instead and is stronger.
- **Python other than 3.11.** Only 3.11.15 has pytest here; nothing version-specific was found.

### A defect in MY OWN harness, disclosed
Two of my scripts (`run_mutants.sh` and a follow-up `TYPEGATE-OFF` run) briefly shared the `ck10/wk3` tree, so a restore from one
clobbered the other's mutation. Symptom: a third `TYPEGATE-OFF` run reported `19 passed` (mutant absent). Affected rows —
`RUN-FWD2` run 3 (ran with an extra mutation present; its result is identical to runs 1 and 2) and the whole first pass of the
lane's remaining-mutant table. **Every affected row was re-run serially in a dedicated tree (`ck10/wk6`) with a pristine-sha
pre-check before each mutation**; only those clean results are reported in table D. The `FINAL-RELAXED-*`, `RUN-DIFF2`,
`RUN-RECDEF2` runs and the `mut.sh`/`plant.sh` batches were sole occupants of their tree and are unaffected.

---

## CROSS-LANE DRIFT OBSERVED DURING THIS REVIEW (read-only, reported for the coordinator)

At my open, `/home/user/agent-factory` HEAD was the PIN `9b2803c` and the dirty set was lane B5f's tee + lane D5i's backend.
At my close, HEAD is **`4b43284` "S0-01 WIP checkpoint 8q … (lane B5f)"** — my PIN is still an ancestor, and **all four graded files
are byte-identical at the PIN and at the new HEAD**. But the **tee moved**: the working tree's `proofs/S0-01/tools/frame_tee.py`
is now `ac82dba82e2f4cb69c5ac1344f9f6b730bfeb69ccccc456929201ab3a595361c`, not the PIN's `061dd10c…`.

That matters because the checker's 3-file suite **consumes the tee's bytes in three places**:
`T:160 tee_sha = _sha256_file(P / "tools" / "frame_tee.py")` (the session fixture stamps every synthetic
`runtime-identity.json` with it), `T:3479 test_ck7_f34_frame_tee_keys_match_pin_ast`, and
`T:3502 test_ck8_f34_frame_tee_subprocess_keys` (spawns the real tee). The commit message's sandbox gate of record was produced
"from a clean detached worktree of `a60b933` … the tee static at checkpoint 8n". **The 3-file gate has not been run against the
checkpoint-8q tee.** My gates run against a frozen `git archive` of the PIN (`ck10/pin`, tee `061dd10c…` verified), so they measure
the PIN's bytes exactly and are immune — which is also why the brief's "grade from a `git archive` copy" instruction was right.
**Action for the coordinator: re-run the 3-file gate at the new HEAD before treating the checkpoint-8p gate lines as current.**
This is also the mechanism behind F-R10-19: a tee moving under a running suite is what produced the lane's 99 failures.

### F-R10-23 — SOLID — a new test reintroduces "the weakest assertion" pattern
`T:4279` `assert "process-scan-after.txt" in out` in `test_ck9_owned_zombies_abc`. That substring matches every
`process-scan-after.txt` reason the checker can print (~10 of them), and the exact string is already asserted verbatim by its own
sibling four functions earlier (`T:4256`: `assert out == "failure_reason: run-1: process-scan-after.txt has no enumeration header"`)
— the `abc` and `-1` cases produce the **same** reason. This is the R9-CK-F8 anti-pattern, reintroduced by the round that removed
eleven instances of it.
**Minimal fix / exact red test**: `assert out == "failure_reason: run-1: process-scan-after.txt has no enumeration header"`.
Same for `T:4288` (`assert "BUZZ_ACP_RESPOND_TO should be 'PATCHED_RT'" in out`) — the exact string is
`failure_reason: run-1: env BUZZ_ACP_RESPOND_TO should be 'PATCHED_RT'`.

Fragment-assertion census, **re-measured from git** (`git show <rev>:tests/…` — my first attempt compared the PIN against a tree
that carried the PIN's own test file, and was wrong; retracted):

| | parent `618749f` | PIN `9b2803c` |
|---|---|---|
| `in out` | **20** | **9** (−11 — the report's "11 converted" is **correct**) |
| `in result` | 9 | 8 |
| `startswith(` | 14 | **15 (+1)** |
| `assert out ==` | 143 | **171 (+28)** |
| lines | 3956 | 4426 |

So the round genuinely removed eleven fragment assertions and added twenty-eight exact ones. It also **added three new fragments**
(T:4279, T:4288, T:4356) and **one new `startswith`** — see F-R10-24.

### F-R10-24 — SOLID — R9-CK-F23's hoist landed but the test it was raised for still asserts only a prefix
`T:4418` `assert out.startswith("failure_reason: run-1: startup-line missing keys:")` in `test_ck9_startup_missing_keys_exact`
(the name says "exact"). R9-CK-F23's entire rationale was: "`_EXPECTED_STARTUP_KEYS` is a **function-local** at C:1049, so the test
must hardcode the 21 keys; hoist it to module scope" — i.e. hoist it *so that the exact missing-keys list becomes computable*.
`C:129-135` now exports it (21 keys, verified) and `test_ck9_expected_startup_keys_importable` asserts the count, but the assertion
that motivated the hoist was never converted. It is the one net-new `startswith` in the diff.
**Minimal fix / exact red test**:
```python
present = {tok.split("=", 1)[0] for tok in log_tokens[0].split()[…]}   # the test already builds the surviving line
missing = sorted(cc._EXPECTED_STARTUP_KEYS - present)
assert out == f"failure_reason: run-1: startup-line missing keys: {missing}"
```

---

## GATES

### The combined 24-guard mutant (27 `if` lines disabled) — FULL 3-file suite, `scripts/test_summary.sh`
```
pytest-exit: 1
pytest-summary: 36 failed, 309 passed, 9 skipped, 1 xfailed in 1063.87s (0:17:43)
```
Collection reconciles: 36 + 309 + 9 + 1 = **355**. CK9's equivalent at its PIN was `32 failed, 283 passed, 10 skipped in 949.26s`
(325 collected). The guards still bite — **four more tests fail now than at CK9's PIN**, consistent with this round adding
killers for the FINAL arm and the RUNNING bounds. Load 2.4-4.6 throughout (another lane was running four CPU burners plus its own
suite for part of the window — see the drift section).

### ITEM 13 answered — **24/24 A5e guards still die at the PIN**
The lane's report says the combined mutant was "only partly re-derived at this tree (11 killers fail, the rest unmapped)". Fully
re-derived here. Same 27 `if` lines, run against CK9's named killer set (`-k` over the A5e names + the 11 siblings), load 2.5-2.8:
```
32 failed, 19 passed, 293 deselected in 297.00s (0:04:57)
```
The 32 failures are **exactly** CK9's list, name for name:
`test_ck7_f1_second_mention_after_first_terminal`, `f2_second_session_new_before_first_terminal`, `f3_duplicate_response_id`,
`f4a_a2c_agent_request`, `f4b_c2a_client_response`, `f5_invalid_response_envelope`, `f6a_tee_pid_wrong_ppid`,
`f6b_agent_pid_wrong_ppid`, `f7a_teardown_mode_mismatch`, `f7b_teardown_rows_zero`, `f7c_teardown_owned_mismatch`,
`f7d_teardown_owned_present_mismatch`, `f8a_tee_status_write_errors`, `f8b_tee_status_forwarded_a2c_mismatch`,
`f8c_tee_status_recorded_c2a_wrong`, `f8d_tee_status_updated_utc_bad_format`, `f8e_tee_status_final_returncode_not_int`,
`f8f_tee_status_not_final_exit_not_null`, `f9a_golden_request_kinds`, `f9b_golden_same_session_ids`, `f9c_golden_same_first_tutc`
(21 A5e names) + `test_proc_tee_parent`, `test_proc_agent_parent`, `test_proc_closure`, `test_orphan_pair`,
`test_pc_launch_exemption`, `test_tee_status_forwarded_lt_recorded`, `test_ck8_f4_no_tee_parented_by_buzz`,
`test_ck8_tee_status_hostile_bundle`, `test_ck8_running_sigkill_errors_rejected`, `test_ck8_running_sigterm_on_final_rejected`,
`test_ck8_running_forwarded_deficit_2_rejected` (11 siblings).
The full-suite figure (36 failed) is these 32 plus 4 more, consistent with this round's new FINAL-arm/RUNNING killers also tripping.

### F-R10-25 — SOLID — 16 real-producer test functions are pinned to a path containing **this session's UUID**
`T:2579`:
```python
_REAL_LEG_DIR = Path("/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/realleg/golden")
```
That directory is **untracked** (`git ls-files | grep realleg` → nothing) and lives in the *session* scratchpad, whose name carries
the container/session id. Sixteen test functions (`test_real_leg_timeline`, `_initialize_frames`, `_runtime_identity`, `_env`,
`_mentions`, `_route`, `_config_echo`, `_manifests`, `_process_evidence`, `_buzzacp_log`, `_prompt_turn`, `_cancel`, `_shutdown`,
`_two_users`, `_negative`, `_normalize_timeline`), several parametrised over four legs, gate on `if not _REAL_LEG_DIR.is_dir():
pytest.skip(...)`.
**Observed — exact, not inferred.** `pytest -k real_leg --collect-only` at the PIN: **`51/344 tests collected`**. The PC gate of
record reports **`304 passed, 51 skipped in 129.81s`**. The numbers match on the nose: on the PC **every one of the 51 real-producer
tests skips**, because `_REAL_LEG_DIR` names this container's scratchpad. In the sandbox only 9 of the 51 skip (for finer reasons)
and 1 xfails, so 41 actually run — and `345 − 304 = 41`. The venue the coordinator treats as the parallel/production gate therefore
runs **zero** real-producer coverage, and nothing asserts the skip count, so the day this container ends the sandbox suite also
reports green with 41 fewer tests executed.
Pre-existing (introduced at checkpoint 4, `b60f02a`) and **not** this round's doing — but it is the single largest hollow-green
surface in the file, and the F21 work this round (`R9-CK-F21`, the xfail) sits **entirely inside it**: the "1 xfailed" in the gate
line is a property of this container.
**Minimal fix**: resolve the corpus from an env var with a repo-relative default (`Path(os.environ.get("S0_01_REAL_LEG_DIR",
ROOT / "proofs" / "S0-01" / "evidence" / "real"))`), and add a gate assertion that the skip count is what the venue expects, e.g.
```python
def test_ck10_real_leg_corpus_presence_is_declared():
    want = os.environ.get("S0_01_REAL_LEG_EXPECTED", "absent")
    assert (_REAL_LEG_DIR.is_dir() and want == "present") or (not _REAL_LEG_DIR.is_dir() and want == "absent"), \
        f"real-leg corpus {_REAL_LEG_DIR} presence != declared {want!r}"
```
so a venue that silently loses the corpus goes RED instead of green-by-skip.

---

## PREMISE TABLE — every claim in the lane report and the commit message I could check

| claim | source | my measurement | verdict |
|---|---|---|---|
| PIN `d5b1b03e…` exists | report | `git cat-file -e` rc 0; = the A5h dispatch commit | ✅ |
| checker sha `3edd8a20…`, 1840 lines | report | identical | ✅ |
| tests sha `5b192f83…`, 4426 lines | report | identical | ✅ |
| `pc_post_scan` sha `73865faf…` | commit msg | identical | ✅ |
| checker 1790 → 1840 (+50) | report | `git show 618749f:` = 1790, `9b2803c:` = 1840 | ✅ |
| tests 3956 → 4426 (+470) | report | identical | ✅ (R9-CK-F15's class closed) |
| `pins.py` untouched | report | `e452e591…` at brief/parent/PIN | ✅ |
| "11 `in out` converted, 20 → 9" | report | parent 20 → PIN 9 | ✅ |
| `_EXPECTED_STARTUP_KEYS` = 21 | report | `len(...) == 21` | ✅ |
| `C:1` and `T:1` both v2.2 | report | both "v2.2" | ✅ |
| FIFO at `fixtures/identities.json` named in < 1 s under the default cap | report PROBE | 153 ms, exact reason | ✅ |
| `--timeout-s 0`/`-1` → rc 64 + exact stderr | report PROBE | identical | ✅ |
| `check_bundle(timeout_s=0)` → ValueError | report PROBE | identical | ✅ |
| `_require_file(<FIFO>)` / `(<dir>)` raise | report PROBE | identical | ✅ |
| real tee SIGTERM rc 70 / clean rc 0, both ACCEPTED | report PROBE | identical, on the PIN's tee `061dd10c…` | ✅ |
| 21/21 named mutants killed | commit msg | 14 of the 18 I ran are killed; **4 survive** (2 of them the lane never ran: `MAIN-DEFAULT-900`, `LITERAL-PINS-2U`; 2 are F43 families) | **partly** |
| `F43-ATTRS-OFF` and `F43-SCAN-OFF` now die | commit msg | both die | ✅ (but 3 sibling families survive — F-R10-08) |
| "the 24-guard combined mutant only partly re-derived… VERIFY-CK10 re-derives it" | commit msg | done: **32 named failures = CK9's list exactly; 24/24 die** | ✅ |
| `_require_file` "covers every read path" | report F27 row | **false** at `C:416` and `C:1697` | ❌ F-R10-02, F-R10-07 |
| `pytest.xfail(strict=True)` on exact match | report F21 row + `T:2780` | **no `strict=` in the file**; matching is `==` **or** substring | ❌ F-R10-13 |
| "disabling the scan disables both" | `T:3276-3278` | false for 3 of 6 families | ❌ F-R10-08 |
| "RED-BEFORE" on F4/F5/F13/F20/F29 rows | report | 11 of those tests are **green on the parent** = CONTROLs | ❌ F-R10-09 |
| Run 2's 99 failures were "resource contention" | report | commit msg says the tee moved under it; contention does not produce 99 deterministic failures | ❌ F-R10-19 |
| collection 343 + 3 + 8 = 354 | report | the checker file collects **344**; committed bytes give **355** | ❌ F-R10-18 |
| sandbox gate `345 passed, 9 skipped, 1 xfailed in 1045.35s` | commit msg | see the gate section below | *(reproduced)* |
| PC gate `304 passed, 51 skipped in 129.81s` | commit msg | **not reproduced** (no bridge). Cross-checked arithmetically: 304+51 = 355 = the sandbox collection, and `-k real_leg` collects exactly **51** — see F-R10-25 | consistent |

### Three full 3-file runs on a `git archive` copy of the PIN — `bash scripts/test_summary.sh tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_audit_cp5_controls.py tests/test_s0_01_pc_post_scan.py`

Pasted verbatim from `ck10/big.log`, not typed:
```
### GATE RUN 1  (load before: 2.42 3.55 3.11)
pytest-exit: 0
pytest-summary: 345 passed, 9 skipped, 1 xfailed in 1021.04s (0:17:01)

### GATE RUN 2  (load before: 1.33 1.70 2.19)
pytest-exit: 0
pytest-summary: 345 passed, 9 skipped, 1 xfailed in 1033.00s (0:17:12)

### GATE RUN 3  (load before: 1.31 1.53 1.72)
pytest-exit: 0
pytest-summary: 345 passed, 9 skipped, 1 xfailed in 1007.47s (0:16:47)
```
**Three identical outcomes — the determinism triple holds.** It reproduces the commit message's gate of record
(`345 passed, 9 skipped, 1 xfailed in 1045.35s`) exactly in outcome; my durations are 1007-1033 s at load 1.3-3.6.

Skip reasons, verbatim from run 1's `-rs` summary (9, exactly as the lane report states):
```
SKIPPED [4] tests/test_s0_01_check_acp_conformance.py:2705: real leg predates scan v2.3 (no enumeration header)
SKIPPED [1] tests/test_s0_01_check_acp_conformance.py:3865: tee-status.json absent in run-1 (corpus predates the tee status)
SKIPPED [1] …:3865: tee-status.json absent in run-2 …   SKIPPED [1] …: cancel …
SKIPPED [1] …: shutdown …                                SKIPPED [1] …: two-users …
```
Xfail (1): `real v2.2 sample: probe_sha256 mismatch (capture predates current probe)` — I exercised all three of its states (item 11).

### Collection — measured, and it does **not** match the lane report
```
355 tests collected in 0.14s
tests/test_s0_01_check_acp_conformance.py: 344 tests collected
tests/test_s0_01_audit_cp5_controls.py:      3 tests collected
tests/test_s0_01_pc_post_scan.py:            8 tests collected
```
`344 + 3 + 8 = 355 = 345 passed + 9 skipped + 1 xfailed` ✅. The lane report says "343 … = 354 total. 344 passed …" — that is the
pre-follow-up tree (F-R10-18). The commit message's "collection 355 = 345+9+1" is correct.

### Pyflakes
```
python3 -m pyflakes proofs/S0-01/check_acp_conformance.py tests/test_s0_01_check_acp_conformance.py \
                    tests/test_s0_01_pc_post_scan.py tests/test_s0_01_audit_cp5_controls.py proofs/S0-01/pins.py
pyflakes rc=0
```

### The real tee through the rewritten checker (`ck10/teerun/run_real_tee.py`, tee `061dd10c…`)
```
--- SIGTERM: tee rc=70
    status = {"agent_returncode": null, "drained": true, "exit_code": null, "final": false, "forwarded_a2c": 1,
              "forwarded_c2a": 1, "recorded_a2c": 1, "recorded_c2a": 1, "stdin_reader_done": false,
              "updated_seq": 2, "updated_utc": "2026-09-07T17:08:03.690924Z", "write_errors": ["terminated: SIGTERM"]}
    check_tee_status(SIGTERM) -> ACCEPTED
--- CLEAN-EXIT: tee rc=0
    status = {… "final": true, "stdin_reader_done": true, "write_errors": [], "exit_code": 0, "agent_returncode": 0 …}
    check_tee_status(CLEAN-EXIT) -> ACCEPTED
SUMMARY: {'SIGTERM': 'ACCEPTED', 'CLEAN': 'ACCEPTED'}
```
No stray processes: `pgrep -fc '[f]rame_tee.py'` = 4 before, 4 after (all other lanes'). I killed nothing I did not start.

### Hygiene at close
`/home/user/agent-factory` was **never** edited, staged, committed, stashed, checked out or reset by me — the only git commands run
there were `cat-file`, `rev-parse`, `log`, `show`, `status`, `diff`, `merge-base`, `ls-files`. `git status --porcelain` at close carries only
other lanes' work (` M proofs/S0-01/tools/frame_tee.py`, ` M tests/test_s0_01_frame_tee.py` — lane B5f, mid-round-11), none of it mine. All four graded files are byte-identical at the PIN and at the current HEAD
`fc35fbb`. Both scope files in every mutation tree restored and `sha256sum -c` verified `OK`. My `/tmp` scratch files removed
(`/tmp/ci.bak` was left alone — it predates this session and is not mine; note that copying it into a scratch tree by mistake is how
a foreign `check_invariants.py` briefly appeared in `ck10/wk2`, since removed and the tree diffed clean against `ck10/pin`).
The shared real-leg corpus at `scratchpad/realleg` is untouched (`probe_sha256 4e88997e2b74`, `agent_exit_code 0`).
`df -h /`: 252G / 26G used / 12G free / 70%.

---

## VERDICT

**NOT-READY.**

This round is a genuine, large improvement on checkpoint 8m, and I want that on the record before the blocking set: every one of
CK9's five blockers has had its *behaviour* fixed and I proved it — the FIFO-at-`identities.json` vector is named in **153 ms**
under the default cap where the parent burned past a 12 s kill; the six FINAL-RELAXED mutants and both RUNNING upper-bound
mutants now die on named tests, **three runs each, deterministically**; `TEEPAR-OFF` dies; the cap refuses its whole non-positive
domain from the CLI; **84 of 84** hostile type/NaN shapes are rejected on both arms with exact per-field reasons; the 38-shape
A21d table reproduces character-for-character; the deleted seq-sum rule is **provably** behaviour-neutral over 43 218
live-reachable shapes; the six dead-branch deletions are safe against ten hostile bundles; and the A5e 24-guard combined mutant
still kills all 24, name for name. I found **no** input the checker accepts that a bad bundle could exploit, save one
arithmetically impossible scan header.

It is NOT-READY because five things the artifact *asserts about itself* are measurably false, and because two guards this round
installed can be deleted with the suite green. Each fix below is one to five lines plus a named red test.

### BLOCKING SET

| # | id | one-line statement | fix size |
|---|---|---|---|
| B1 | **F-R10-13** | There is **no `strict=True`** anywhere in the file, yet `T:2780-2781` and the report's F21 row both assert it, on a gate (`_KNOWN_XFAIL_REASONS`) that was itself a named fail-open; and "exact match" is a substring match whose `==` branch is provably dead for the real reason. Measured all three states. | docstring + 1 line, or 3 lines for real strictness |
| B2 | **F-R10-08** | Three of the F43 scan's six pattern families (`_SHUTIL_WRITERS`, `_OS_WRITERS`, `json.dump`) can be **deleted with the self-test green** — the `>= 6` threshold is slack by one because `json.dump(obj, open(p,"w"))` yields two violations. `T:3276-3278` claims the opposite. This is the guard raised to close a CK9 **blocker**. | 2 lines (assert categories, not a count) |
| B3 | **F-R10-02 + F-R10-07** | The F27 DONE row claims `_require_file` "covers **every** read path". Two executed counterexamples: a FIFO at `C:416 HERE/tools/frame_tee.py` blocks past a **40 s** kill against a 9 s baseline (rc 70 at `--timeout-s 25`) — the exact CK9-F2 symptom at a different path; and a directory named `manifest-post.summary` yields `malformed evidence: IsADirectoryError` (`C:1697`), verbatim the shape R9-CK-F27 named, while the other 19 allowlisted names give the exact reason. | 2 × 1 line |
| B4 | **F-R10-06** | `MAIN-DEFAULT-900` **survives**: `main()`'s cap literal (`C:1798`) — the only one `spec.json` ever uses — is a second, unpinned copy. `test_ck9_default_timeout_is_90` pins the *other* copy. The module docstring asserts "90 s so it always fires before the runner's `timeout_s: 120`"; nothing holds it. | delete the duplicate + 1 test |
| B5 | **F-R10-12** | `LITERAL-PINS-2U` **survives**: C:490's derived two-users pin can be reverted to the literal `"allowlist"` — the very literal F12 exists to remove — with `30 passed, 314 deselected`. F12's only consumption test patches the other pin, and asserts a substring. | 1 test |
| B6 | **report corrections** (F-R10-09, F-R10-17, F-R10-18, F-R10-19) | 11 CONTROL tests labelled "RED-BEFORE"; 2 checker and 11 test `file:line` refs stale (4 pointing at non-assertion lines); a collection block computed on pre-final bytes while the hash block is final; and a mis-diagnosis of the lane's own 99-failure run ("resource contention") that the commit message silently corrects to the tee moving under it, and that the lane never reproduced. | report edit only |

### NON-BLOCKING, all real, all reported above
F-R10-03 (`timeout_s=True` → silent 1 s cap), F-R10-04 (a huge cap is reported as *malformed evidence*, rc 1, not usage rc 64),
F-R10-05 (NaN passes the positivity floor; only `alarm()`'s type check stops it), F-R10-10 (four dead-branch deletion comments
cite `check_initialize_frames`, which enforces none of what they claim), F-R10-11 (the `owned_zombies` rule is half the producer's
invariant, and covers only the after-scan; an impossible header PASSES), F-R10-14/F-R10-23 (three new fragment assertions,
including a fresh instance of "the weakest assertion in the file"), F-R10-15 (the SIGALRM handler leaks when `alarm()` itself
raises — an unexploded AF-AP-58 sibling the incident log explicitly, and wrongly, cleared for this site), F-R10-16 (the F13
parametrised test can silently drop keys; 19/19 run today), F-R10-20 (`_split_world`'s foreign branch has no committed negative
control and **structurally cannot fire in the sandbox** — no sandbox process can name a `_PINNED` path, measured: 0 of 89 live
rows), F-R10-21 (a docstring NOTE that reads as current behaviour), F-R10-22 (the new 60 s helper cap makes ~340 tests
load-sensitive), F-R10-24 (R9-CK-F23's hoist landed but `test_ck9_startup_missing_keys_exact` still asserts a prefix),
**F-R10-25** (16 real-producer test functions / **51 collected tests** are pinned to a path containing this container's UUID;
the PC gate skips **exactly 51**, i.e. the parallel venue runs zero real-producer coverage, and nothing asserts the skip count).

### WHAT THIS VERDICT DEPENDS ON THAT I DID NOT REPRODUCE
Exactly one thing: **the PC gate line `304 passed, 51 skipped in 129.81s`**. There is no bridge banner this session, so I could not
run it. I cross-checked it two ways and it is consistent (304 + 51 = 355 = the sandbox collection; `-k real_leg` collects exactly
51, which accounts for the skip delta) — but it is carried, not measured. **No blocking item depends on it.** Every blocking item
was executed here, twice or three times, on `git archive` copies of the PIN.

One further caveat that is not a dependency but the coordinator must act on: **the tee moved during this review** (checkpoint 8q,
`4b43284`, `ac82dba8…`). The checker suite consumes the tee's bytes in three places, so the sandbox gate below measures the PIN's
bytes and **not** current HEAD. Re-run the 3-file gate at HEAD before treating any of these lines as current.
