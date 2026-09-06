All grading runs are complete. Final report:

---

# VERIFY-N5d (round 8, Opus 5) — VERDICT: **NOT-READY** (3 mechanical blockers; all four round-7 blockers CLOSED and reproduced)

## Premise + disk

```
b84c1ac S0-01 WIP checkpoint 8b: the ACP probe never exits 0 with an unsampled interpreter identity, SR-03 has a real killer, fixture agents run under the runner's interpreter by construction (lane N5d) — REVIEW-PENDING, nothing minted
1e67982 transcripts: scrubbed sandbox chat digests (2026-09-06)
```
`git log origin/claude/soundbox-kit-migration-iz1jwf..HEAD` → `b84c1ac` only (local, unpushed — as the brief states). Premise HOLDS.

```
df -h /tmp/claude-0 | tail -1  (before the first mutant batch)
/dev/vda        252G   22G   16G  58% /
```
Unchanged at 58% throughout. One materialised tree (`scratchpad/vn8/repo`, 132 M, `git archive HEAD | tar -x`, then `git init`+commit for hygiene); every pytest run got `--basetemp` under `vn8/tmproot`, deleted after. No ENOSPC. All 8 scope files in my copy are sha256-identical to the `b84c1ac` blobs (verified). Shared tree: read-only git commands only (it carries two other lanes' live edits: `proofs/S0-01/tools/frame_tee.py`, `tests/test_s0_01_frame_tee.py`, `tasks/briefs/s0-01-b5c-support/B5c-report.md`).

## 1. Agent-shape table — the REAL probe, real agents (`ACP_PROBE_TIMEOUT` 2–5 s)

| # | agent shape | probe rc | `agent_interpreter_realpath` / `_sha256` | `agent_exit_code` | `probe_error` |
|---|---|---|---|---|---|
| A | `import sys; sys.exit(0)`, no stdout | **1** | null / null | 0 | `interpreter sample failed: agent exited before its first a2c byte` |
| B | `sys.exit(1)`, no stdout | **1** | null / null | 1 | same |
| C | `os.close(1)` then sleep 3 | 0 | `/usr/bin/python3.11` / `f56a588548dd…` | 0 | null |
| D | write 1 byte then `os._exit(0)` | **RACY 0/1** | null/null when rc=1 | 0 | `interpreter sample failed: [Errno 2] No such file or directory: '/proc/20431/exe'` |
| E | full answer + `sys.stdin.read()` (the lane's new fixture shape) | 0 | set / set | 0 | null |
| F | full answer then exit **immediately, no stdin read** (production CPython shape) | 0 (**90/90**) | set / set | 0 | null |
| G | slow: first byte after 2 s, then answer | 0 | set / set | 0 | null |
| H | 1 byte, sleep 0.05, `os._exit` | 0 | set / set | 0 | null |
| I | full answer with **no trailing newline**, then exit | 0 | set / set | 0 | null |
| J | never answers, hangs (deadline path) | 0 | set / set | −9 | null |
| K | closes stdout, sleeps 60 (probe kills it) | 0 | set / set | −9 | null |
| L | partial line then hang | 0 | set / set | −9 | null |
| M | `agent_sigterm` fixture (self-SIGTERM after stdin, no stdout) | **1 (20/20)** | null / null | −15 | `interpreter sample failed: agent exited before its first a2c byte` |
| N | interpreter unlinked at start, closes stdout, stays alive | **1** | `…/myshell (deleted)` / **null** | 0 | `interpreter sample failed: agent exited before its first a2c byte` ← **FALSE** |
| BP1 | BrokenPipe, child alive | 1 | null / null | 0 | `BrokenPipeError: agent process exited before c2a write landed` |
| BP2 | BrokenPipe, child dead | 1 | null / null | 0 | same |

**Race window, measured** (`race.py`, 30 runs each; then 60/30/30 with 4 CPU hogs):

| agent | unloaded | loaded (4 hogs) | `taskset -c 0` |
|---|---|---|---|
| D `os._exit` right after the byte | **21/30 rc=1** (70 %) | **13/30 rc=1** (43 %) | 0/30 |
| F CPython answer-then-exit | 0/30 | 0/60 | 0/30 |
| E stdin-blocking | — | 0/30 | 0/30 |

**Ordering (read + corroborated):** both samples (`acp_probe.py:205-211` in-loop, `:259-265` post-loop) precede `proc.stdin.close()` at `:269`, so the sample never depends on the agent surviving the probe's stdin close. The real PC negative capture sampled successfully (`agent_interpreter_realpath=/usr/bin/python3.13`, sha `8be0f8e5…`, `agent_exit_code 0`, a2c at +635.4 ms), so at first-byte time the pinned child was alive with a live `mm`. The capture carries **no** exit timestamp, so it does not settle whether `hermes-acp` waits for stdin EOF — and it does not need to, given the ordering. `agent-stderr.txt` ends with the ACP supervisor's `RequestError` traceback and no shutdown line.

**Exit 0 with a null interpreter field: NO path found.** 16 shapes; every arm either populates the field or sets `probe_error`, and `probe_error` forces exit 1 (mutant N4 proves the exit is test-gated). No pid-reuse hazard: the child is reaped only at `:275`, after both samples.
**Exit 1 on a healthy agent: YES, for shape D only** — an agent that exits without interpreter teardown between its first stdout byte and the readlink. **The pinned agent is not in that class** (CPython, shape F, 90/90 clean + the live capture), so the PC re-capture is not expected to break; the risk is unpinned by any test and would become live if the pinned agent were ever a compiled binary.

## 2. The not-delivered (BrokenPipe) path — downstream reasons (`validate_negative_dir`, run live)

| bundle | validator verdict |
|---|---|
| control (`build_valid`) | `OK: observed: error code=-32602 message=Invalid params` |
| valid + `probe_error`(BrokenPipe) | `FAILURE: probe reported an error: BrokenPipeError: agent process exited before c2a write landed` |
| interp NULL + `probe_error`(sample) | `FAILURE: probe reported an error: interpreter sample failed: agent exited before its first a2c byte` |
| interp NULL, **no** probe_error (the pre-N5d shape) | `FAILURE: agent_interpreter_realpath mismatch` ← R7-N5c-F1's misattribution, now unreachable |
| **real BrokenPipe capture** (1 entry, `delivered:false`, interp NULL) | `FAILURE: initialize request was not delivered to the agent` |
| `probe_error=""` | `OK: observed: …` (see F9) |

Answer: on the BrokenPipe path the interpreter identity **is** null, `probe_error` **does** name the delivery, and downstream rejects with the **delivery** reason (`negative_contract.py:120`, reached before the rid `probe_error` check at `:162`). The interpreter reason cannot win — **but only because the post-loop block sits inside `if c2a_delivered:`, and nothing pins that** (finding F2).

## 3. Mutant table — 83 mutants run

**58-set (round-6/7 spec, anchors dry-run first: 58/58 matched, ZERO moved).**

| group | ids | result |
|---|---|---|
| CI-06 … CI-14 (9) | classifier schema/text/cardinality/NaN | **KILLED** (same first-killers as round 7) |
| **CI-10 last-wins** | — | **SURVIVED** (equivalent, gate-shadowed; re-run vs full 5-file suite: `234 passed`) |
| AP-F1a/b/c, AP-17, AP-12/12b/12c, AP-11, AP-19/19b, AP-F4a/F4b, AP-F16, AP-F15, AP-interp-fail-open (16) | probe identity | **KILLED** (AP-F1a now killed by 3 tests incl. both new ones; AP-interp-fail-open `17 failed`) |
| **SR-02 / SR-03 / SR-04** | runner reason rule | **ALL KILLED** — SR-03 by `test_runner_records_the_observed_line_not_the_expected_reason` **+** `test_runner_unmet_when_expected_reason_is_multiline` |
| NC-08/12/22/27 (4) | validator | **KILLED** |
| CI-15 … CI-23 (9) | classifier CLI/text | **KILLED** |
| AP-20 … AP-29, AP-02, AP-16, AP-33/34/35 (13) | probe fields / M3 | **KILLED** |
| **AP-32 probe-path-wrong** | — | **SURVIVED under the round-7 subset** (probe+classifier); **KILLED** vs the full 5-file suite by `negative_contract::test_build_valid_matches_the_live_producer_shape` (`1 failed, 233 passed`) |

**TOTAL 58 · KILLED 57 · SURVIVED 1 (CI-10, the proven equivalent).** The lane's 57/58 reproduces — with the caveat in F12.

**Guard mutants — G1-G5 (verify-N5c, re-aimed at the new code) + N1-N8 (the new code), all vs the full 5-file suite:**

| id | mutation | result | killing test |
|---|---|---|---|
| G1 | in-loop except → `pass` | KILLED | `test_probe_interpreter_sample_failure` (+1) |
| **G2** | **re-introduce `if proc.poll() is None:`** (the R7-N5c-F1 regression) | **KILLED** | `test_probe_interpreter_sample_failure_after_child_exit` — **sole killer** |
| G3 | sha step always raises | KILLED | 16 tests |
| G4 | in-loop `if False:` | KILLED | 2 tests |
| G5 | in-loop probe_error → dead local | KILLED | 2 tests |
| N1 | delete the post-loop block | KILLED | `test_probe_agent_exits_without_output_is_fail_loud` |
| N2 | post-loop except → `pass` | KILLED | same |
| N3 | post-loop samples `/proc/self/exe` | KILLED | same |
| N4 | drop the final `exit 1` | KILLED | 5 tests |
| N5 | post-loop `if False:` | KILLED | same |
| N6 | post-loop probe_error → dead local | KILLED | same |
| N7 | post-loop reason text swapped | KILLED | same |
| **N8** | **post-loop block dedented out of `if c2a_delivered:`** | **SURVIVED `234 passed`** | — (finding F2) |

**Runner siblings (item 4's "what else does the new test miss"):**

| id | mutation | result |
|---|---|---|
| SR-05 | per-line `in` → per-line `==` | **KILLED** by the new observed-line test |
| SR-10 | `in line` → `line.startswith(...)` | **KILLED** by the new observed-line test |
| SR-06 | match against `line.strip()` | **SURVIVED** |
| SR-07 | case-folded match | **SURVIVED** |
| SR-08 | record the LAST matching line | **SURVIVED** |
| SR-09 | record the stripped line | **SURVIVED** |

**F10-deletion audit (X-series, full 5-file suite):** X1 `AP-20 + delete tests/test_s0_01_acp_probe.py:287` → **SURVIVED 234 passed** ⇒ `:287 agent_argv` confirmed the **sole** killer of AP-20 (lane kept the right line). X2 drop `probe_path` key → KILLED (3 tests, two in other files). X3 `agent_exit_code` → 99 → KILLED (incl. `test_probe_error_response`, the report's named cover). X4 interpreter fields → None → KILLED (3). X5 drop `spawned_at_utc` → KILLED (4). X6 drop `probe_sha256` → KILLED (3). **All five deleted assertions are genuinely covered.**

**Red-green (F1):** pre-N5d probe (`git show 1e67982:proofs/S0-01/tools/acp_probe.py`) + the new tests → **`2 failed, 232 passed`**, exactly `test_probe_agent_exits_without_output_is_fail_loud` and `test_probe_interpreter_sample_failure_after_child_exit`. Green on HEAD. Reproduced.

**PATH shim (F4/F8), de-vacuoused:**
```
RUN A  no shim                                    5 passed, 34 deselected in 6.59s
RUN B  shim python3 -> 3.13, runner 3.11          5 passed, 34 deselected in 6.56s
RUN C  shim + the two other real-probe producers  2 passed in 0.22s
RUN B' shim + shebangs reverted to env python3    2 failed, 3 passed   <-- the recipe DOES discriminate
         test_probe_interpreter_fields_pinned / test_probe_identity_fields_all_pinned
         assert 'd8f6c91b455a…' == 'f56a588548dd…'   (N5c §7b's exact PC reds)
RUN A' no shim + shebangs reverted                5 passed  (the sandbox coincidence)
```
No remaining `os.path.realpath(sys.executable)` expectation whose producer samples something else: only `:652` and `:872`, both now matched **by construction** (`#!{sys.executable}` → `/proc/<pid>/exe`). Verified.

**Exact-reason grep (item 6):** `in r.stdout|in r.stderr` → **3** hits, all `"Traceback" not in r.stderr` (legitimate negative controls). `assert … >=` → **2** hits (`:344`, `:888` — see F11). `in {…}` reason sets → **0** (R7-N5c-F5 closed: `tests/test_s0_01_negative_contract.py:426 assert str(ei.value) == "agent_argv mismatch"`). The report's `ci:393/403/837/850` and `probe:287/288/565/1000/1018`, `runner`-side `spec_runner:363/437`, and `acp_probe.py:151/209-210/258-265` all check out verbatim on HEAD.

## Findings

**R8-N5d-F1 — SOLID — the new fail-loud is race-decided for an agent that exits between its first a2c byte and the sample.**
`vn8/repo/proofs/S0-01/tools/acp_probe.py:205-211`. Input: agent writes one byte then `os._exit(0)`. Observed: `probe rc` flips run to run — 21/30 rc=1 unloaded, 13/30 loaded, 0/30 pinned to one CPU; on the rc=1 arm `probe_error = "interpreter sample failed: [Errno 2] No such file or directory: '/proc/20431/exe'"`, interpreter fields null. Expected: one deterministic outcome for one agent shape. **Not a PC blocker** — the pinned `hermes-acp` is CPython (shape F: 90/90 sampled, and the live capture sampled `/usr/bin/python3.13`) — but nothing in the suite pins either direction, so a compiled ACP agent would make the negative leg non-reproducible. **Red test I would add:** `test_probe_fast_exit_agent_is_deterministic` — agent `sys.stdout.write('x'); os._exit(0)`, run the probe 20× in-test, assert the (rc, interpreter-is-null) pair is constant. **Minimal fix:** start sampling right after `Popen` in a bounded retry loop (retry while the link still resolves to the probe's own exe, ≤200 ms), keep the first success authoritative, and keep the never-sampled fail-loud — this does not resurrect AP-F1a (which samples once, too early).

**R8-N5d-F2 — SOLID — BLOCKING — the post-loop sample's placement is unpinned; mutant N8 survives the whole gate.**
`acp_probe.py:258-265` inside `if c2a_delivered:` (`:187`). Dedenting the block one level survives `234 passed` while changing the evidence: on a not-delivered capture the interpreter fields become non-null (`/usr/bin/python3.11`) where pristine writes null — reproduced live on both BrokenPipe arms — and a readlink failure on that path would overwrite the `BrokenPipeError` reason with the interpreter reason. Item 2's correct answer (delivery reason wins) is load-bearing on this placement and no test asserts it. **Red test:** in `test_probe_broken_pipe_deterministic` (`:511`) add `assert rid["agent_interpreter_realpath"] is None and rid["agent_interpreter_sha256"] is None`. **Fix:** that assertion; no production change needed.

**R8-N5d-F3 — SOLID — BLOCKING — the post-loop reason is a fixed string that lies when the failure is the sha step, not the readlink.**
`acp_probe.py:263-264` catches `(OSError, IOError)` around **both** `os.readlink` and `_sha256_file` but always writes `"interpreter sample failed: agent exited before its first a2c byte"`. Live repro (`misattr.py`, agent = `#!<hardlinked dash>` that unlinks its own interpreter, closes stdout, sleeps 3): probe rc 1, `agent_exit_code 0` (the agent was **alive** and exited normally), `agent_interpreter_realpath = "…/myshell (deleted)"`, `agent_interpreter_sha256 = null`, `probe_error = "interpreter sample failed: agent exited before its first a2c byte"`. Observed vs expected: the recorded cause is false and contradicts two other fields in the same object; the in-loop arm at `:210` gets this right with `f"…: {exc}"`. **Red test:** the agent above; assert `rid["probe_error"] == "interpreter sample failed: [Errno 2] No such file or directory: '…/myshell'"`. **Fix:** `except (OSError, IOError) as exc:` and set the "agent exited before its first a2c byte" wording only when `interp_realpath is None`, else `f"interpreter sample failed: {exc}"`.

**R8-N5d-F4 — SOLID — the report's F9-closure claim over-generalizes: two other tests run the REAL probe with a non-stdin-blocking agent and assert `rc == 0`.**
`vn8/repo/tests/test_s0_01_check_initialize.py:689` (`test_make_capture_dir_keys_match_live_producer`, still `#!/usr/bin/env python3`, `assert r.returncode == 0` at `:719`) and `vn8/repo/tests/test_s0_01_negative_contract.py:364/381` (`_FAKE_AGENT` → `_run_real_probe`, `assert r.returncode == 0` at `:388`). Both are shape F, measured 0/90 flake, so latent not active — but the lane made the probe *stricter* (exit 1) without covering them, which is the same F9 mechanism. **Fix:** append `sys.stdin.read()` to both agents (and `#!{sys.executable}` at ci:689 for consistency with the other nine).

**R8-N5d-F5 — SOLID — BLOCKING — stale comments the same diff falsifies (stale-context sweep).**
`tests/test_s0_01_acp_probe.py:259` — docstring still says *"V2: interpreter fields must NOT be null (sampled before proc.wait)"* and `:285` — *"# V2: Runtime identity has interpreter fields NOT null (sampled before wait)"*, but F10 **deleted** exactly those two assertions from that test. `:645-647` — docstring still says *"with an env-shebang agent … The agent_result fixture uses `#!/usr/bin/env python3`"*, falsified by F4/F8 in the same commit. **Fix:** three comment edits in the same change (repo rule: a doc the diff falsifies is a hollow green in words).

**R8-N5d-F6 — SOLID — the report's F4/F8 line list is stale for 7 of 9 entries (recurrence of R7-N5c-F12).**
Report says `agent_result :40, agent_error :68, agent_silent :88, agent_stderr_heavy :100, agent_partial_line :126, agent_notification_then_response :140, agent_non_json :193, agent_sigterm :225, inline :824`. On HEAD the `#!{sys.executable}` write lines are `40, 70, 95, 110, 142, 159, 193, 226, 816` (fixture `def` lines `37, 67, 92, 107, 139, 156, 190, 223`; the inline agent's test def is `:807`). Only `:40` and `:193` match either reading. Every **other** ref in the report is correct on HEAD.

**R8-N5d-F7 — SOLID — four runner mutants the new SR-03 killers miss; one of them loosens the gate.**
`vn8/repo/scripts/proof-runner:192-199`. SR-07 (case-folded match) SURVIVES: a checker printing `PROTOCOL-VIOLATION: …` would satisfy a lowercase `failure_reason` — a fail-open in the matching direction. SR-08 (last-match-wins) and SR-09 (record the stripped line) SURVIVE and change the recorded observation; SR-06 (strip before matching) SURVIVES. The multi-line expectation **is** right under the rule as written (`splitlines()` can never yield a line containing `\n`, so an embedded newline is unmatchable ⇒ `negative-control-unmet`), and the test is de-vacuoused by pinning `r.stderr.strip() == "negative-control-unmet: S0-95"` (a schema rejection could not produce that string). **Red tests:** (i) checker prints the reason upper-cased, expected reason lower-case → assert rc != 0 and the exact `negative-control-unmet: S0-9x`; (ii) checker prints two lines that both contain the reason → assert `observed_failure_reason` equals the **first**.

**R8-N5d-F8 — SOLID — pre-existing hole in the M3 contract inside the graded file: the evidence writes sit outside the wrapped body, and a crash there is classified as DEFERRED.**
`acp_probe.py:303-333` is after the `except Exception` at `:287`. Live repro: an agent that `os.unlink(__file__)` at start, then answers → `_sha256_file(agent_realpath)` at `:309` raises `FileNotFoundError` → **uncaught traceback**, exit 1, capture dir contains only `agent-stderr.txt`, no `runtime-identity.json`/`env.json`/`timeline.jsonl`. `check_initialize.py request <dir>` → `deferred: negative probe not captured`, **rc 2** — and `scripts/proof-runner:181-185` turns exit 2 into `Deferred(… capability-unavailable …)` with the previous artifact **preserved** (read, not run). A producer crash therefore reads as "this venue can't run the leg" and lets a stale `result.json` stand. Same class for ENOSPC/read-only `S0_01_FRAMEDIR`. **Red test:** the self-deleting agent; assert rc 1, `"Traceback" not in r.stderr`, `rid["probe_error"].startswith("FileNotFoundError")`. **Fix:** move the identity/env/timeline writes inside the wrapped body (or wrap them in the same M3 handler).

**R8-N5d-F9 — SOLID (informational) — `probe_error == ""` validates.**
`proofs/S0-01/negative_contract.py:162` (`not in (None, "")`). Unreachable from this producer (the key is written only when non-None), but any producer writing an empty reason passes the check. **Fix:** drop `""` from the carve-out, or assert the key's absence.

**R8-N5d-F10 — SOLID (informational) — `test_probe_sigterm_killed_agent_exit_code` (`tests/test_s0_01_acp_probe.py:451`) now drives an exit-1 probe run and never asserts rc.**
Measured 20/20: rc 1, `probe_error = "interpreter sample failed: agent exited before its first a2c byte"`, `agent_exit_code -15`. The M7 assertion is made on a capture the probe itself declares broken. (Downstream would still reject that bundle for the better reason — `no agent response captured`, `negative_contract.py:141-142`, which precedes the probe_error check.) **Fix:** add `assert r.returncode == 1` and the exact `probe_error`, making the shape's contract explicit.

**R8-N5d-F11 — SOLID (informational) — two loose comparisons remain after the F7 sweep.**
`tests/test_s0_01_acp_probe.py:344` `st_size >= 200000` where the fixture writes exactly `204800`; `:888` `redacted_seen >= 1` where the exact count is derivable from the env dict. Same class as the `>= 1` → `== 1` the lane fixed at `:565`.

**R8-N5d-F12 — SOLID (methodology) — AP-32's kill depends on the run's file scope.**
Under the round-6/7 per-mutant subset (`probe` + `classifier`) AP-32 still **SURVIVES `92 passed`**; it is killed only when `tests/test_s0_01_negative_contract.py` is in the run. The lane's "57/58 killed" is correct against the 5-file coordinator gate and its table names the right killer — but the inherited mutant spec's subsets under-run their own mutants, so any future "killed" claim taken from that spec must state the file scope.

**Verified-good (claims I reproduced rather than accepted):** F1 red-green (`2 failed, 232 passed` on the reverted probe); the two new tests are non-tautological and `test_probe_interpreter_sample_failure_after_child_exit` is the **sole** killer of the guard's re-introduction (G2); SR-03 killed by both new tests and green on pristine; the shim recipe discriminates (RUN B′); all five F10 deletions covered by mutation; `:287` sole killer of AP-20; the exact-reason sweep is clean; the coordinator's new `probe_path` tail check passes on the **real** capture (`endswith` True) so it does not break the PC path.

## Item 8 — the real negative capture (`scratchpad/realleg/golden/negative`)

```
$ python3 proofs/S0-01/check_initialize.py request  <dir>   ->  failure_reason: negative: probe_sha256 mismatch      rc=1
$ python3 proofs/S0-01/check_initialize.py response <dir>   ->  error code=-32602 message=Invalid params            rc=1

capture probe_sha256: 4e88997e2b74db0f53d4f505c33ec3ddeab5037fa0c6fd38bbda39e2430b5999
current probe_sha256: ccf79194736e87276e97f61879ac58cd0687b1d0a988369294041f0e2705ec51   (round 7 saw a5f9115…; it moved again)
```
With **only** `negative_contract.py:174-175` (the `probe_sha256` check) peeled, the same capture passes the entire validator — `protocol-violation: missing required initialize field` / `observed: error code=-32602 message=Invalid params` — and reverts to `probe_sha256 mismatch` on restore. **The expected-sha drift is the SOLE failure ground** (as in round 7); no fixture-vs-producer divergence. The PC negative must be re-captured with this probe.

## Gates (my copy, HEAD, pasted verbatim)

```
pytest-exit: 0
pytest-summary: 234 passed in 39.04s
pytest-exit: 0
pytest-summary: 234 passed in 39.24s
```
```
python3 -m pyflakes proofs/S0-01/{tools/acp_probe.py,check_initialize.py,negative_contract.py,pins.py} \
  tests/test_s0_01_{acp_probe,check_initialize,negative_contract,spec_runner,nostr_verify}.py scripts/proof-runner
pyflakes rc=0
```
`git status --porcelain` on my copy: **0 lines before, 0 after** two suite runs + ~95 mutant runs + ~250 probe launches. All eight mutated files `cmp`-identical to pristine at the end.

## What I reproduced vs reviewed statically vs skipped

**Reproduced (ran it):** all 58 spec mutants (anchor dry-run first, 0 misses) + both survivors vs the full suite; 13 guard mutants; 6 runner siblings; 6 F10-deletion probes; 16 agent shapes against the real probe; the race measurement (unloaded / 4-hog loaded / single-CPU); the N8 and misattribution live differentials; the BrokenPipe and null-identity downstream table; the F1 red-green revert; the PATH shim in four configurations including the de-vacuousing control; the real capture through both checker modes plus the peeled-check diagnostic; two suite runs, pyflakes, hygiene, blob-identity.

**Reviewed statically (not executed):** `scripts/proof-runner:177-185` exit-2 → `Deferred` + artifact-preserved (read; I observed the classifier's rc 2 but did not drive the runner on a crashed-probe leg); the claim that `hermes-acp` blocks on stdin (settled as irrelevant by the probe's ordering, which I read and corroborated with the capture).

**Deliberately skipped:** (1) anything on the PC — no bridge banner this session; the PC re-capture and a PC-venue run of the shim are `NOT run here`. (2) The tree-wide suite — the brief scoped the gate to five files. (3) The other lanes' live files (`frame_tee.py`, `test_s0_01_frame_tee.py`, `check_acp_conformance`) — different lanes, and the shared tree is being edited. (4) `tests/test_s0_01_nostr_verify.py` content — in the suite scope only.

## Verdict

**NOT-READY.** Blocking: **R8-N5d-F2** (a non-equivalent mutant of the code this lane added survives the whole gate; the delivery-vs-interpreter reason ordering item 2 asks about is correct-but-unpinned), **R8-N5d-F3** (the new post-loop block emits a demonstrably false cause on a reachable path — the misattributed-reason class round 7 blocked on), **R8-N5d-F5** (three comments inside the lane's own hunks that the same diff falsifies). All three are ≤10-line fixes and none of them re-opens a round-7 blocker.

Non-blocking, land before minting: **F1** (race-decided fail-loud for fast-exiting agents), **F4** (two other real-probe producers still un-hardened), **F6** (stale line refs in the report), **F7** (four surviving runner mutants, SR-07 fail-open), **F8** (pre-existing M3 hole → crash reads as DEFERRED with the artifact preserved), **F9**, **F10**, **F11**, **F12**.

All four round-7 blockers are **CLOSED and reproduced**: R7-N5c-F1 (no exit-0-with-null path in 16 shapes; the guard's re-introduction is killed by a unique test), R7-N5c-F2 (SR-03 killed by two non-tautological tests, which also kill SR-05 and SR-10), R7-N5c-F4/F8 (fixed at the root, shim recipe proven to still discriminate), R7-N5c-F5 (exact reason assertion in place). This verdict does **not** depend on anything I failed to reproduce, with one bounded exception: the *PC* behaviour of the pinned agent is inferred from the single real capture plus 90 local runs of the same agent class — I did not execute on the PC.