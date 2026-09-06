Verification complete. All artifacts under `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vn7/`.

---

# VERIFY-N5c (round 7, Opus 5) — VERDICT: **NOT-READY**

## F0 — brief-guard contradiction (procedural, read first)

My task text says to STOP and report "brief missing" if the brief's last line ends with `(tee lane, not yours).` — but the same paragraph calls the PREMISE UPDATE the brief's **final** paragraph, and that paragraph is exactly the one ending in those words. The brief at `/tmp/.../scratchpad/brief-verify-r7-N5c.md` is 60 lines, carries all 8 grading items, the authorization paragraph, and the PREMISE UPDATE. It is neither missing nor truncated, so I graded the antecedent false and proceeded. If the guard was meant to fire on a different truncation point, re-issue it.

## Premise check + disk

```
cc03846 transcripts: scrubbed sandbox chat digests (2026-09-06)
4b173b7 S0-01 producer: process scans use ps -eww ...
9d40b18 transcripts: scrubbed sandbox chat digests (2026-09-06)
73d025d S0-01 WIP checkpoint 7: ... REVIEW-PENDING, nothing minted
```
`git diff --stat 73d025d..HEAD -- <the 6 scope paths>` → **empty**. I also checked `tests/test_s0_01_nostr_verify.py`, `proofs/S0-01/negative_contract.py`, `scripts/proof-runner`, `proofs/S0-01/pins.py` 73d025d..HEAD → **empty**. Premise HOLDS; graded HEAD.

`df -h /tmp/claude-0 | tail -1` (before the first mutant batch):
```
/dev/vda        252G   16G   22G  42% /
```
Unchanged at 42–43% throughout. One materialised tree (`vn7/repo`, 131 M); every pytest run got `--basetemp` under `vn7/tmproot`, deleted at the end. No ENOSPC.

Scratch copy: `git archive HEAD | tar -x` into `vn7/repo`, then `git init`+commit for hygiene checking. `vn5b/` survived the restart — I used **its** `mut.py` and `spec1–5.json` (58 unique ids; `spec6`/`spec8-substantive` are re-runs of survivors). Only change to the round-6 runner: added `--basetemp` (disk budget); nothing about what is tested changed.

## 1. The 58-mutant set, re-run — **55 killed / 3 survived**

**Anchors moved: ZERO.** All 59 edits across 58 mutants matched at the expected count on HEAD (dry-run before any application).

| # | id | result | first killing test |
|---|---|---|---|
|1|CI-06 reqdir-schema|KILLED|`check_initialize::test_request_dir_uses_fixtures_dir_schema`|
|2|CI-06b respdir-schema|KILLED|`check_initialize::test_response_dir_uses_fixtures_dir_schema`|
|3|CI-06c filemode-schema|KILLED|`check_initialize::test_request_file_mode_uses_fixtures_dir_schema`|
|4|CI-08 malformed-ret0|KILLED|`check_initialize::test_malformed_rid_json_exits_1` (+1)|
|5|CI-09 retext-noc2a|KILLED|`check_initialize::test_response_dir_no_c2a_frames_exits_1`|
|6|CI-09b retext-noid|KILLED|`check_initialize::test_response_dir_rejects_unparseable_c2a` (+1)|
|7|**CI-10 last-wins**|**SURVIVED**|— (equivalent, see §2)|
|8|CI-11 del-cardinality|KILLED|`check_initialize::test_response_dir_rejects_duplicate_id_responses`|
|9|CI-12 id-fail-open|KILLED|`check_initialize::test_response_dir_foreign_id_a2c_response_first`|
|10|CI-13 del-noid-guard|KILLED|`check_initialize::test_response_dir_rejects_unparseable_c2a` (+1)|
|11|CI-14 nan-parse-off|KILLED|`check_initialize::test_response_dir_nan_in_a2c_frame`|
|12|AP-F1a interp-at-Popen|KILLED|`acp_probe::test_probe_interpreter_fields_pinned` (+2)|
|13|AP-F1b interp-self-exe|KILLED|`acp_probe::test_probe_interpreter_is_child_not_self`|
|14|AP-F1c interp-hardcoded|KILLED|`acp_probe::test_probe_interpreter_is_child_not_self` (+1)|
|15|AP-17 probe-sha-zeros|KILLED|`acp_probe::test_probe_identity_fields_all_pinned`|
|16|AP-12 pid-neg1|KILLED|`acp_probe::test_probe_identity_fields_all_pinned`|
|17|AP-12b pid-is-self|KILLED|`acp_probe::test_probe_identity_fields_all_pinned`|
|18|AP-12c pid-plus-one|KILLED|`acp_probe::test_probe_identity_fields_all_pinned`|
|19|AP-11 interp-sha-zeros|KILLED|`acp_probe::test_probe_interpreter_fields_pinned` (+1)|
|20|AP-19 sha12-hardcoded|KILLED|`acp_probe::test_probe_identity_fields_all_pinned` (+1)|
|21|AP-19b redlen-hardcoded|KILLED|`acp_probe::test_probe_env_json_redaction`|
|22|AP-F4a del-empty-check|KILLED|`acp_probe::test_probe_empty_framedir_exits_64_no_probe_error` (+1)|
|23|AP-F4b swap-empty-msg|KILLED|`acp_probe::test_probe_empty_framedir_exits_64_no_probe_error` (+1)|
|24|AP-F16 del-makedirs|KILLED|`acp_probe::test_probe_framedir_is_file_exits_64` (+1)|
|25|AP-F15 spawned-late|KILLED|`acp_probe::test_probe_spawned_at_precedes_first_frame` (+1)|
|26|AP-interp-fail-open|KILLED|`acp_probe::test_probe_result_response_and_check_initialize` (16 failed)|
|27|SR-02 first-line-exact|KILLED|`spec_runner::test_runner_matches_reason_on_non_first_line`|
|28|**SR-03 whole-output-substr**|**SURVIVED**|— (NOT equivalent, see §2)|
|29|SR-04 concat-no-newline|KILLED|`spec_runner::test_runner_unmet_when_reason_split_across_streams`|
|30|NC-08 isint-bool|KILLED|`negative_contract::test_agent_child_pid_bool_is_not_an_int`|
|31|NC-12 mono-off|KILLED|`negative_contract::test_t_mono_ns_must_not_decrease`|
|32|NC-22 keys-open|KILLED|`negative_contract::test_timeline_entry_with_an_unexpected_key_is_rejected`|
|33|NC-27 tutc-unchecked|KILLED|`negative_contract::test_t_utc_without_microseconds_is_rejected`|
|34|CI-15 respdir-defer-text|KILLED|`check_initialize::test_response_dir_defers_when_absent`|
|35|CI-16 respdir-ok-always0|KILLED|`check_initialize::test_response_dir_invalid_result_exits_1`|
|36|CI-17 fixdir-arg-ignored|KILLED|`check_initialize::test_request_dir_fails_fixture_absent` (4 failed)|
|37|CI-18 fixdir-missing-val|KILLED|`check_initialize::test_fixtures_dir_no_value_exits_64`|
|38|CI-19 error-line-format|KILLED|`check_initialize::test_response_dir_foreign_id_a2c_response_first` (3)|
|39|CI-20 dirmode-suffix|KILLED|`check_initialize::test_request_dir_defers_when_absent` (+1)|
|40|AP-20 argv-empty|KILLED|`acp_probe::test_probe_result_response_and_check_initialize` (**sole killer**)|
|41|AP-21 realpath-wrong|KILLED|`acp_probe::test_probe_identity_fields_all_pinned`|
|42|AP-22 entrypoint-sha-zeros|KILLED|`acp_probe::test_probe_identity_fields_all_pinned`|
|43|AP-23 bytecode-hardcoded|KILLED|`acp_probe::test_probe_bytecode_false_when_unset`|
|44|AP-24 exitcode-hardcoded|KILLED|`acp_probe::test_probe_sigterm_killed_agent_exit_code`|
|45|AP-25 redact-regex-narrow|KILLED|`acp_probe::test_probe_identity_fields_all_pinned` (+1)|
|46|AP-26 probe-error-exit0|KILLED|`acp_probe::test_probe_broken_pipe_deterministic` (+1)|
|47|AP-27 delivered-flag-drop|KILLED|`acp_probe::test_probe_broken_pipe_deterministic`|
|48|AP-28 fixture-path-swap|KILLED|`acp_probe::test_probe_result_response_and_check_initialize` (+1)|
|49|AP-29 empty-agent-ungated|KILLED|`acp_probe::test_probe_empty_agent_exits_64`|
|50|AP-02 producer-extra-key|KILLED|`check_initialize::test_make_capture_dir_keys_match_live_producer`|
|51|AP-16 producer-key-order|KILLED|`check_initialize::test_make_capture_dir_keys_match_live_producer`|
|52|**AP-32 probe-path-wrong**|**SURVIVED**|— (NOT equivalent, see §2)|
|53|CI-21 observed-line-drop|KILLED|`check_initialize::test_request_dir_valid_capture_exits_1_with_classification_and_observed` (+1)|
|54|CI-22 negprefix-drop|KILLED|`check_initialize::test_request_dir_fails_no_c2a_frames` (26 failed)|
|55|CI-23 deferred-exit2to1|KILLED|`check_initialize::test_request_dir_defers_when_absent` (3)|
|56|AP-33 m3-exit0|KILLED|`acp_probe::test_probe_bad_agent_path_writes_probe_error` (+1)|
|57|AP-34 m3-drop-probe-error|KILLED|`acp_probe::test_probe_bad_agent_path_writes_probe_error` (+1)|
|58|AP-35 m3-swallow-timeline|KILLED|`acp_probe::test_probe_bad_agent_path_writes_probe_error`|

**TOTAL 58 · KILLED 55 · SURVIVED 3.** The lane's "55/55 non-equivalent killed" reproduces. I also re-ran the 3 survivors against the **full 5-file suite** (round-6 used narrower per-mutant subsets, none of which included `test_s0_01_negative_contract.py` for the AP-* set): all three still `SURVIVED 228 passed`, so the coordinator's new producer-pin test does not kill them either.

## 2. The three "equivalents" — live differentials

### CI-10 (`check_initialize.py:157` `matching[0]` → `matching[-1]`) — **TRUE equivalent, gate-shadowed**
Bundle with two a2c frames both carrying `id 0`, one a `-32602` error and one a `protocolVersion:1` result (so `[0]` and `[-1]` genuinely differ):

```
[1] PRISTINE                response<dir>: rc=1 stdout='Failure: 2 a2c responses carry request id 0'
[2] MUTANT matching[-1]     response<dir>: rc=1 stdout='Failure: 2 a2c responses carry request id 0'
[3] gate REMOVED, pristine  response<dir>: rc=1 stdout='error code=-32602 message=Invalid params'
[4] gate REMOVED + mutant   response<dir>: rc=0 stdout='ok'
[5] sanity, single frame    response<dir>: rc=1 stdout='error code=-32602 message=Invalid params'
```
`:151` (`not matching` → 1) and `:153` (`len>1` → 1) leave exactly one element at `:157`, so no path reaches the difference. Equivalent — but note [4]: the difference is real and **fail-open** (`ok`, exit 0) if the cardinality gate is ever weakened. CI-11 kills the gate mutant, so the pair is currently sound.

### SR-03 (`scripts/proof-runner:194-197`) — **NOT equivalent. Two live differences.**
```
CASE A — expected reason CONTAINS a newline, checker prints the two halves as two lines
  PRISTINE {"rc":1,"stderr":"negative-control-unmet: S0-95","result_exists":false}
  MUTANT   {"rc":0,"stderr":"","result_exists":true,
            "observed_failure_reason":"alpha-violation: part-one\npart-two tail"}   <-- FORGED MET

CASE B — single-line reason, observed line is a SUPERSET
  PRISTINE observed_failure_reason = "failure_reason: negative: protocol-violation: missing required initialize field (seq 2, id 0)"
  MUTANT   observed_failure_reason = "protocol-violation: missing required initialize field"   <-- records the EXPECTATION, not the observation

CASE C (control, the repo's own S0-01 shape) — identical both builds
```
The per-line rule **does** admit a multi-line reason from `spec.json` (nothing forbids `\n` in `failure_reason`); CASE A shows the mutant mints a `result.json` the pristine runner refuses. And CASE B is the observation-collapses-into-expectation pattern the whole negative-control discipline exists to prevent — the recorded evidence becomes a copy of the assertion. On the **current** corpus (all 7 repo `failure_reason` values are single-line and, for S0-01, equal to the whole printed line — `check_initialize.py:113` `print(verdict)`) the two builds agree, which is why the mutant survives.

The test that is supposed to kill it does not: `tests/test_s0_01_spec_runner.py:363` `test_runner_unmet_when_reason_split_across_lines` uses expected `"protocol-violation: missing required initialize field"` (a **space**) against output split at that space (a **newline**), so `expected in whole_text` is *also* False — the mutant passes it. Its docstring "Kills the 'whole-output substring' mutant" is FALSE. Round-6 F12's "docstrings claim kills that do not happen" recurs.

### AP-32 (`acp_probe.py:300` `probe_path`) — **NOT equivalent; an unread identity field**
```
value correct (control)   request<dir>: rc=1 'protocol-violation: missing required initialize field'  (VALID)
value = '/x'              request<dir>: rc=1 'protocol-violation: missing required initialize field'  (VALID)
value = null              request<dir>: rc=1 'protocol-violation: missing required initialize field'  (VALID)
value = 12345 (int)       request<dir>: rc=1 'protocol-violation: missing required initialize field'  (VALID)
KEY ABSENT                request<dir>: rc=1 'failure_reason: negative: runtime identity key probe_path absent'
```
Every consumer, traced: `pins.py:105` puts `probe_path` in `NEGATIVE_IDENTITY_KEYS`, which `negative_contract.py:164` uses for **key presence only**; `negative_contract.py:170` explicitly declines to pin the value; `check_acp_conformance` reuses the same validator; the only test mention is `tests/test_s0_01_acp_probe.py:291` `assert "probe_path" in rid` — presence. Nobody reads the value. That is fail-soft by omission, not equivalence: a field is written into the evidence bundle, required to exist, and carries zero evidentiary weight.

## 3. Sampling-guard attack — `proc.poll() is None` (`acp_probe.py:205-215`)

### 3A — probe behaviour per agent shape (real probe, real agents)

| agent shape | probe rc | `agent_child_pid` | `agent_realpath` | `agent_entrypoint_sha256` | `agent_interpreter_realpath` / `_sha256` | `probe_error` |
|---|---|---|---|---|---|---|
| A `sys.exit(0)`, no stdout | **0** | 20556 | (real path) | `1b76d41e80e0…` | **null / null** | **null** |
| B `sys.exit(1)`, no stdout | **0** | 20559 | (real path) | `5fac48ef950a…` | **null / null** | **null** |
| C `os.close(1)` then sleep 3 s | **0** | 20562 | (real path) | `f9ea852eb113…` | **null / null** | **null** |
| D write 1 byte then `os._exit(0)` | 1 | 20584 | (real path) | `7db683750177…` | null / null | `interpreter sample failed: [Errno 2] No such file or directory: '/proc/20584/exe'` |
| E full answer then exit (control) | 0 | 20587 | (real path) | `c9e6bc3c9f97…` | `/usr/bin/python3.11` / `f56a588548dd…` | null |

**Mechanism (reproduced, not read):** the sampling block at `:205` sits *after* `if not chunk: break` at `:202-203`. An agent that never writes to stdout hits EOF and leaves the read loop **before sampling is attempted** — `_interp_sampled` stays False, the `try/except` never runs, so the `proc.poll()` guard is never consulted. Result: exit 0, complete-looking capture, null interpreter identity, no `probe_error`.

I also built the **guarded silent arm** deterministically (patched `os.readlink` to `sleep(d)` then raise, so the child is reaped before `poll()` runs):
```
readlink raises after 0.0s -> probe_rc=1  probe_error='interpreter sample failed: [Errno 2] ...'  (fail-loud, as designed)
readlink raises after 1.0s -> probe_rc=0  probe_error=None  interp_realpath=None  interp_sha=None  (SILENT)
      capture files both cases: ['agent-stderr.txt','env.json','runtime-identity.json','timeline.jsonl']
```
So the guard turned "always silent" into "silent whenever the child is already dead" — and *the child being already dead is the pinned agent's required shape*: `negative_contract.py:185` REQUIRES `agent_exit_code == 0`. The lane's report calls the suppressed case "a false positive from fast-exiting children"; it is not a false positive — the sample genuinely failed and the interpreter identity is genuinely unknown.

### 3B — downstream verdict on null / missing identity

| bundle | `check_initialize.py request <dir>` |
|---|---|
| control (all pinned) | rc=1 `protocol-violation: missing required initialize field` (VALID) |
| interpreter fields NULL (= shapes A/B/C) | rc=1 `failure_reason: negative: agent_interpreter_realpath mismatch` |
| interpreter realpath NULL only | rc=1 `failure_reason: negative: agent_interpreter_realpath mismatch` |
| interpreter sha NULL only | rc=1 `failure_reason: negative: agent_interpreter_sha256 mismatch` |
| interpreter keys ABSENT | rc=1 `failure_reason: negative: runtime identity key agent_interpreter_realpath absent` |
| `agent_child_pid` NULL | rc=1 `failure_reason: negative: agent_child_pid is not a positive int` |
| `agent_realpath` NULL | rc=1 `failure_reason: negative: agent_realpath mismatch` |
| `agent_entrypoint_sha256` NULL | rc=1 `failure_reason: negative: agent_entrypoint_sha256 mismatch` |
| `agent_exit_code` NULL | rc=1 `failure_reason: negative: agent_exit_code is None, expected 0` |

**No null-identity bundle validates.** The brief's HIGH bar ("a bundle with null identity that validates") is NOT met — I state that explicitly. What remains is (a) a probe that exits **0** on a capture it knows is incomplete, and (b) a **misattributed** downstream reason: a dead-before-sample run is reported as `agent_interpreter_realpath mismatch`, indistinguishable from a genuine wrong-interpreter pin violation. That is verbatim the defect R6-N5b-F5 raised.

### Guard mutants (all against the full 5-file suite)

| mutant | result | killing test |
|---|---|---|
| G1 delete the guard body (`pass`) | KILLED | `test_probe_interpreter_sample_failure` |
| G2 invert (`poll() is not None`) | KILLED | `test_probe_interpreter_sample_failure` |
| G3 sha step raises inside the guarded region | KILLED | 16 tests |
| G4 never sample (`if False:`) | KILLED | 5 tests incl. `test_probe_interpreter_fields_pinned` |
| G5 assign `probe_error` to a dead local | KILLED | `test_probe_interpreter_sample_failure` |

The guard's *exception* arm is well covered. The **never-sampled** arm needs no mutant — the pristine code already exhibits it (shapes A/B/C), and no test drives an agent that produces no stdout while asserting on identity or `probe_error` (`test_probe_never_answers:332` uses a hanging agent and asserts only `rc==0` and one timeline entry).

## 4. The coordinator's producer-pin test

`tests/test_s0_01_negative_contract.py:385 test_build_valid_matches_the_live_producer_shape`

- **Runs the REAL probe?** YES — `:381` `subprocess.run([sys.executable, str(P / "tools" / "acp_probe.py")], env=env, …)`. Not an import, not a re-implementation. Its fake agent's shebang is `#!%s % sys.executable` (`:379`), so it is deliberately venue-independent — unlike the older probe tests (§7b).

| mutant | result |
|---|---|
| PP-1 `build_valid` ADD a rid key | KILLED (this test only) |
| PP-2 `build_valid` DROP `probe_path` | KILLED (20 failed) |
| PP-3 `build_valid` DROP `agent_child_pid` | KILLED (18 failed) |
| PP-4 rename `sha256_12` → `sha12` in `build_valid` | KILLED (this test only) |
| PP-5 `build_valid` env DROP `S0_01_FRAMEDIR` | KILLED (this test only) |
| PP-6 fake agent code `-32602`→`-32600` | KILLED |
| PP-7 fake agent message → `"Bad params"` | KILLED |
| PP-8 fake agent DROP `error.data` | KILLED |
| PP-9b fake agent ADD `error.extra` | KILLED |
| PP-10 fake agent shebang → `/usr/bin/env python3` | SURVIVED — **by design**, the test asserts shapes only |
| PP-11 **probe** DROPS a rid key | KILLED (this test only) |
| PP-12 **probe** ADDS a rid key | KILLED (this test only) |
| PP-13 **probe** redaction key `sha256_12`→`sha12` | KILLED (this test only) |

Every key-set mutation on **both** sides reds. Good.

- **Is the venue-pin assertion exact?** NO — `:417-419` is `assert str(ei.value) in {7 reasons}`. Proved 7× looser than needed:
```
PP-14 narrow to exactly "agent_argv mismatch"   -> SURVIVED (i.e. still PASSES)
PP-15 narrow to a WRONG single reason           -> KILLED
PP-16 delete the assertion entirely             -> SURVIVED
PP-17 narrow to a 2-element set                 -> SURVIVED
direct run of the live capture through nc:       'agent_argv mismatch'   (deterministic, single-valued)
```
The reason is deterministically `agent_argv mismatch`; the set admits six reasons that never fire, so a reordering of the validator's checks (or a regression that makes a *different* pin fail first) passes unnoticed.

- **Is the fake agent's `-32602` envelope the pinned shape byte-for-byte?** It is *equivalent* but **duplicated as literals** (`tests/test_s0_01_negative_contract.py:359-361`: `"code": -32602, "message": "Invalid params"`), not referenced from `pins.PINNED_NEGATIVE_ERROR_CODE` / `_MESSAGE`. It is transitively exercised (PP-6/PP-7 red, because `negative_contract.py:154` checks code+message before the identity block), so it is not hollow — but it is a local copy of a pin, the AF-AP-42 signature.

## 5. The real negative capture (`scratchpad/realleg/golden/negative`)

```
$ python3 proofs/S0-01/check_initialize.py request  <dir>
failure_reason: negative: probe_sha256 mismatch
rc=1

$ python3 proofs/S0-01/check_initialize.py response <dir>
error code=-32602 message=Invalid params
rc=1

capture  probe_sha256: 4e88997e2b74db0f53d4f505c33ec3ddeab5037fa0c6fd38bbda39e2430b5999
current  probe_sha256: a5f91153a1c9aa25370a3663781d4a543137ad596f765498d30c658b19423676
```
With **only** the `probe_sha256` check peeled (`negative_contract.py:171-172`), the same capture passes the entire validator:
```
protocol-violation: missing required initialize field
observed: error code=-32602 message=Invalid params
rc=1
```
and reverts to `probe_sha256 mismatch` on restore. So the expected sha drift is the **sole** failure ground — no fixture-vs-producer divergence (no AF-AP-42 here). Note the current probe sha `a5f9…` differs from round-6's `3decc…` too: the PC negative must be re-captured after this lane's probe edit, as the checkpoint message already says.

## 6. Discipline, hygiene, lint tells

**Exact-reason violations** (only reason/message assertions; structural `in`/`>=` checks excluded):
- `tests/test_s0_01_negative_contract.py:417` — `in {7 reasons}` (see §4). **Blocking.**
- `tests/test_s0_01_check_initialize.py:835` — `assert "NaN/Infinity not allowed in timeline" in r.stdout.strip()`. Exact value available: `"failure_reason: malformed evidence: ValueError: NaN/Infinity not allowed in timeline: 'NaN'"`.
- `tests/test_s0_01_check_initialize.py:848` — `assert "usage:" in r.stderr`. Exact: `"usage: check_initialize.py request|response <file|dir> [--fixtures-dir <dir>]"`.
- `tests/test_s0_01_check_initialize.py:386,395` — usage tests assert the exit code only, no stderr line at all (a usage-text mutant survives them; CI-18 is killed elsewhere).
- `tests/test_s0_01_acp_probe.py:576` — `assert len(entries) >= 1` where the producer writes exactly 1.
- `tests/test_s0_01_spec_runner.py:283,424,494` — `assert r.returncode != 0` are each **paired** with an exact `r.stderr.strip() == …`. Not violations.

**tmp_path hygiene: PASS.** `git status --porcelain` on my copy is empty before and after two full suite runs plus ~80 mutant runs. Round-6's F16 residue is fixed: `test_probe_empty_framedir_exits_64_no_probe_error:736` now uses `tmp_path` as `cwd` and asserts `not (tmp_path / "runtime-identity.json").exists()`; the `spec_runner` blank-line residue is gone.

**Lint tells.**
- **AP-1** (`os.environ.get|getenv(`) — `tests/test_s0_01_acp_probe.py:533,534,830,978,979` and `tests/test_s0_01_negative_contract.py:377`. All are subprocess-env plumbing (building a child's env / the fixture agent reading `_TEST_PID_FILE`), not a config channel into production code. **Benign.** One caveat: `:978-979` and `:377` propagate the caller's `PATH` into the child, which is the vector for §7b.
- **AP-32** (`(sha256|md5|hash)\(`) — `tests/test_s0_01_acp_probe.py:668,862,876,884,892,959`. `:862/:876/:892/:959` hash exactly what the producer hashes: **benign**. **`:668` and `:884` are NOT benign** — they hash `Path(os.path.realpath(sys.executable)).read_bytes()` while the producer hashes the file at `os.readlink("/proc/<child>/exe")`. The AP-32 screen's own question ("is the hashed form EXACTLY what the store holds?") answers *no* off-sandbox. This screen flag is the mechanical signature of the §7b defect and should not have been waved through.

## 7. Is `test_probe_result_response_and_check_initialize` redundant? — quantified by mutation

| probe | result | reading |
|---|---|---|
| R1 delete `:291-298` (presence-only + not-null block) | suite GREEN 3/3 on re-run | **redundant** (the one red in the first run was the §F11 flake, not coupling) |
| R2 delete `:290` `assert rid["agent_argv"] == [agent_result]` | suite GREEN | no other test asserts it |
| R2b R2 **+ AP-20 source mutant** | **SURVIVED 228 passed** | `:290` is the **SOLE killer** of AP-20 |
| R4 AP-20 with the test intact (control) | KILLED by this test | confirms R2b |
| R3 delete the `check_initialize` round trip `:300-306` | suite GREEN | kills no mutant uniquely |
| R3b R3 **+ nc reason mutant** | KILLED by `test_request_dir_result_response_rejected_by_validator` and `test_agent_accepted_malformed_initialize` | round trip is redundant for the reason |

**Answer:** the lane's "subsumed by `test_probe_identity_fields_all_pinned`" is only partly right. Line **:290** (`agent_argv`) is load-bearing and unique — `test_probe_identity_fields_all_pinned` never asserts `agent_argv`, `agent_interpreter_realpath`, or `spawned_at_utc`. Line **:291** (`"probe_path" in rid`) is the **only** `probe_path` assertion anywhere in the suite. Lines **:292, :293, :294, :296, :298** are genuinely redundant (with `:862`, `:329`, `test_probe_spawned_at_two_sided`, and `test_probe_interpreter_fields_pinned` respectively). The `check_initialize` round trip is the only end-to-end probe→CLI path but kills nothing uniquely; keep it as the integration path, not as a mutant gate.

## 7b. The two PC reds — **venue coincidence, CONFIRMED**

Reproduced locally by decoupling `env python3` from `sys.executable` with a PATH shim (`shim/python3 → /usr/bin/python3.13`; `sys.executable` stays 3.11), the exact PC shape:

```
RUN A (sandbox PATH, runner python == shebang python):   4 passed
RUN B (shim: 'env python3' = 3.13, sys.executable = 3.11): 2 failed, 2 passed
  FAILED test_probe_interpreter_fields_pinned
    E  AssertionError: interpreter realpath '/usr/bin/python3.13' != '/usr/bin/python3.11'
    tests/test_s0_01_acp_probe.py:664
  FAILED test_probe_identity_fields_all_pinned
    E  assert 'd8f6c91b455a…2df6a225d1aab' == 'f56a588548dd…0d9643e78ff9e'
    tests/test_s0_01_acp_probe.py:885
```

**Exact expected-value derivation on each side:**

| side | derivation | value in RUN B |
|---|---|---|
| **producer** (`acp_probe.py:207-208`) | `interp_realpath = os.readlink("/proc/%d/exe" % proc.pid)` — the **agent child's** interpreter, i.e. whatever the fixture's shebang `#!/usr/bin/env python3` (`tests/test_s0_01_acp_probe.py:40`) resolved from the inherited `PATH`; `interp_sha256 = _sha256_file(interp_realpath)` | `/usr/bin/python3.13`, `d8f6c91b455a…` |
| **test** (`:663-664`, `:668`) | `expected_interp = os.path.realpath(sys.executable)` — the **pytest runner's** interpreter; `expected_sha = sha256(Path(expected_interp).read_bytes())` | `/usr/bin/python3.11`, `f56a588548dd…` |
| **test** (`:883-885`) | same `os.path.realpath(sys.executable)` derivation, compared to `rid["agent_interpreter_sha256"]` | same mismatch |

Both expectations come from `sys.executable`; the probe samples the agent's `/proc/<pid>/exe`. In the sandbox `/usr/local/bin/python3` and `/usr/bin/python3` both realpath to `/usr/bin/python3.11`, so runner == shebang and the tests pass by **coincidence**. On the PC (project venv 3.11, `/usr/bin/python3` → 3.13) they diverge. AF-AP-42 venue class, confirmed.

**One correction to the brief:** the second red is `agent_interpreter_sha256`, not `agent_entrypoint_sha256`. The failing line is `:885` (`assert rid["agent_interpreter_sha256"] == expected_interp_sha`, no custom message); the `agent_entrypoint_sha256` block sits immediately above it in the traceback, which is how the misread arises. `agent_entrypoint_sha256` (`:876`) hashes the agent script's own bytes and is venue-independent — it cannot fail this way.

**Fix (state which):** derive the expectation from the **fixture agent's actual shebang**, e.g. `expected_interp = os.path.realpath(shutil.which("python3"))` for a `#!/usr/bin/env python3` agent — or, preferably, write the fixture agents with `#!{sys.executable}` (the pattern the coordinator's `_FAKE_AGENT` at `:357` already uses), making runner and agent interpreter identical **by construction** rather than by venue. The second is the smaller, more honest change and matches the shape the newer test already ships.

## Findings

**R7-N5c-F1 — SOLID — HIGH-severity fail-soft on the pinned agent's expected shape.**
`vn7/repo/proofs/S0-01/tools/acp_probe.py:202-215`. Two reachable paths leave `agent_interpreter_realpath`/`_sha256` **null with `probe_error` null and exit 0**: (a) the agent writes nothing to stdout — control breaks at `:202-203` before the sampling block at `:205`, so the guard is never consulted; (b) `os.readlink` fails after the child has been reaped — `proc.poll() is None` is False at `:213`, suppressing `probe_error`. Observed vs expected: observed `probe_rc=0, probe_error=None, interp fields null, four-file capture written`; expected `probe_rc=1` with a named `probe_error`. Path (b) is the *normal* negative-leg shape (agent answers and exits; `negative_contract.py:185` REQUIRES `agent_exit_code == 0`). Downstream does reject (`agent_interpreter_realpath mismatch`) so this is not a validating null, but the reason is misattributed — a race is reported as a pin violation. **Red test:** `test_probe_agent_exits_without_output_is_fail_loud` — agent body `import sys; sys.exit(0)`; assert `r.returncode == 1` and `rid["probe_error"] == "interpreter sample failed: agent exited before its first a2c byte"`; plus `test_probe_interpreter_sample_failure_after_child_exit` using the `sleep(1)`-then-raise `os.readlink` wrapper, asserting `r.returncode == 1` and the exact `probe_error`. **Minimal fix:** sample once unconditionally before leaving the read loop (or at EOF), and make "never sampled" itself a `probe_error` rather than keying loudness on `poll()`.

**R7-N5c-F2 — SOLID — SR-03 is not equivalent; the test that claims to kill it is a tautology.**
`vn7/repo/scripts/proof-runner:194-197`; `vn7/repo/tests/test_s0_01_spec_runner.py:363-429`. CASE A (multi-line `failure_reason`): pristine `rc=1 negative-control-unmet`, mutant `rc=0` with `result.json` minted. CASE B (observed line a superset): pristine records the observed line, mutant records the expected reason verbatim. The existing test's needle contains a space where the output has a newline, so both builds fail it. **Red tests:** (i) `test_runner_records_the_observed_line_not_the_expected_reason` — checker prints `failure_reason: negative: <R> (seq 2, id 0)` with `expect.failure_reason = "<R>"`; assert `result["negative_control"]["observed_failure_reason"] == "failure_reason: negative: <R> (seq 2, id 0)"`. (ii) `test_runner_unmet_when_expected_reason_is_multiline` — `failure_reason = "alpha\nbeta"`, checker prints `alpha` then `beta`; assert `rc != 0` and `r.stderr.strip() == "negative-control-unmet: S0-95"`. Also fix the false docstring at `:364`.

**R7-N5c-F3 — SOLID — `probe_path` is an unread identity field (AP-32).**
`acp_probe.py:300`, `pins.py:105`, `negative_contract.py:164,170`, `tests/test_s0_01_acp_probe.py:291`. `/x`, `null` and `12345` all validate; only key absence is caught. **Red test:** in `tests/test_s0_01_negative_contract.py`, `_set_rid(neg, probe_path="/x")` → `_expect(neg, "probe_path is not the probe's path")`, backed by a venue-independent suffix check in `negative_contract.py` (`str(rid["probe_path"]).endswith("proofs/S0-01/tools/acp_probe.py")`). **Alternative minimal fix (preferred under anti-hollow-green tactic 4):** drop `probe_path` from `NEGATIVE_IDENTITY_KEYS` and stop writing it — an assertion that cannot be made should be dropped, not carried as decoration.

**R7-N5c-F4 — SOLID — two tests encode the sandbox coincidence `runner interpreter == shebang interpreter`.**
`tests/test_s0_01_acp_probe.py:663-671` and `:883-885`. Derivations and reproduced messages in §7b. **Red test:** run the current file under `PATH=<dir with python3 → a different minor version>:$PATH`; both tests must stay green. **Minimal fix:** give the fixture agents `#!{sys.executable}` (as `tests/test_s0_01_negative_contract.py:357` already does) so producer and expectation share one interpreter by construction.

**R7-N5c-F5 — SOLID — the producer-pin test's venue-pin assertion is a 7-way set.**
`tests/test_s0_01_negative_contract.py:417-419`. Observed reason is deterministically `agent_argv mismatch`; PP-14 shows the exact assertion passes, PP-17 shows a 2-element set also passes. **Red test / fix:** `assert str(ei.value) == "agent_argv mismatch"`.

**R7-N5c-F6 — SOLID — the fake agent duplicates the negative pins as literals.**
`tests/test_s0_01_negative_contract.py:359-361` hardcodes `-32602` / `"Invalid params"` instead of `pins.PINNED_NEGATIVE_ERROR_CODE` / `_MESSAGE`. Transitively exercised (PP-6/PP-7 red), so not hollow — but a pin change silently desynchronises the producer fixture. **Fix:** interpolate the pins into `_FAKE_AGENT`.

**R7-N5c-F7 — SOLID — exact-reason violations.** `tests/test_s0_01_check_initialize.py:835` (substring; exact string available), `:848` (substring; exact string available), `:386`/`:395` (exit code only), `tests/test_s0_01_acp_probe.py:576` (`>= 1` where the producer writes exactly 1). Each fix is the `==` form of the value I printed in §6.

**R7-N5c-F8 — SOLID — AP-32 lint tell waved through incorrectly.** `tests/test_s0_01_acp_probe.py:668` and `:884` hash `realpath(sys.executable)` while the producer hashes the child's `/proc/<pid>/exe`. This is the screen's exact question and it answers *no*. Same fix as F4.

**R7-N5c-F9 — SOLID — `test_probe_interpreter_fields_pinned` is flaky (consequence of F1).** Observed 1 red across my ~20 full-file runs of `tests/test_s0_01_acp_probe.py` (in the R1 mutant run: `1 failed, 227 passed`, `FAILED …::test_probe_interpreter_fields_pinned`); the same three-run repeat then went 3/3 green, and a 6× focused repeat went 6/6 green. Round-6 independently saw 2/~46. Closing F1 closes this.

**R7-N5c-F10 — SOLID — the lane's "adjacent defect" claim is partly wrong.** `wf-results-r5/N5c.md` says `:291-294` is "subsumed by `test_probe_identity_fields_all_pinned`". `:290` (`agent_argv`) is the **sole** killer of AP-20 (R2b survived without it); `:291` is the only `probe_path` assertion in the suite. Only `:292,:293,:294,:296,:298` are redundant. Deleting the block as reported would open an untested hole.

**R7-N5c-F11 — SOLID — recorded test counts understate the committed tree (AF-AP-37 class).** Commit `73d025d` and `docs/INCIDENT-LOG.md` record `227 passed in 38.84s` / `227 passed in 37.47s` for the five-file set, but the tree **at that commit** yields **228** — all six scope files are byte-identical `73d025d..HEAD`, and my two runs on HEAD give 228. The lane's 227 predates the coordinator's `test_build_valid_matches_the_live_producer_shape` (which the same commit also carries, and whose file the commit separately records as `47 passed in 0.38s`; 227+1 = 228). Paste the post-integration summary, not the lane's.

**R7-N5c-F12 — SOLID — the lane report's `probe:` line refs are stale by 4.** `wf-results-r5/N5c.md` cites `probe:296/299/300/301` for `probe_path`/`agent_realpath`/`agent_entrypoint_sha256`/`agent_child_pid`; actual on HEAD are `300/303/304/305` (the lane's own 4-line guard shifted them). `ci:` and `runner:` refs check out.

**R7-N5c-F13 — SOLID (informational) — CI-10 is equivalent only while the cardinality gate holds.** With `check_initialize.py:153-155` removed, `matching[-1]` returns `ok` / exit **0** on a duplicate-id bundle that pristine rejects. CI-11 currently kills the gate mutant, so no action is required — but the pair should be noted as coupled if that gate is ever refactored.

## Gates (pasted verbatim, my copy, HEAD)

```
pytest-summary: 228 passed in 38.08s
pytest-summary: 228 passed in 37.88s
```
(baseline before the mutation work: `228 passed in 39.02s`)

```
$ python3 -m pyflakes proofs/S0-01/tools/acp_probe.py proofs/S0-01/check_initialize.py \
    proofs/S0-01/negative_contract.py tests/test_s0_01_acp_probe.py tests/test_s0_01_check_initialize.py \
    tests/test_s0_01_negative_contract.py tests/test_s0_01_spec_runner.py tests/test_s0_01_nostr_verify.py \
    scripts/proof-runner
pyflakes rc=0
```

Integrity after all mutation work: all seven mutated files `cmp`-identical to their pristine copies; `git status --porcelain` empty.

## What I reproduced vs. reviewed statically vs. skipped

**Reproduced (ran it):** all 58 mutants + 3 full-suite re-runs of the survivors + 5 guard mutants + 13 producer-pin mutants + 5 test-deletion probes; the CI-10 / SR-03 / AP-32 live differentials; the five agent-shape attacks and the nine downstream null-identity bundles; the deterministic silent-arm construction; the PATH-shim reproduction of both PC reds; the real negative capture through both checker modes plus the peeled-check diagnostic; two suite runs, pyflakes, `git status`.

**Reviewed statically (not executed):** the `probe_path` consumer trace (grep across `proofs/`, `tests/`, `scripts/` plus reading `pins.py:104-107` and `negative_contract.py:159-172`) — the live differential then confirmed it behaviourally; the AP-screen regexes in `.claude/hooks/edit-snapshot.py:63-76`.

**Deliberately skipped, with reason:** (1) anything on the PC — no bridge banner this session, so §7b is reproduced by a local PATH shim that recreates the same runner≠shebang decoupling, **not** on the PC itself; the PC re-capture of the negative is likewise not run here. (2) The full repo suite — the brief scoped item 8 to the five files. (3) `tests/test_s0_01_nostr_verify.py` content — in the suite scope only, not in the grading scope. (4) `check_acp_conformance.py`'s own gate — a different lane's verifier owns it; I only traced its use of the shared validator.

## Verdict

**NOT-READY.** Blocking: **R7-N5c-F1** (probe exits 0 with null interpreter identity on the pinned agent's normal answer-then-exit shape; the `poll()` guard closes only the still-alive arm), **R7-N5c-F2** (SR-03 survives a real behavioural difference and its designated killer test is a tautology in both builds), **R7-N5c-F4** (two tests will red on the PC as a matter of venue, not correctness — the same reds the first PC run already produced), **R7-N5c-F5** (the producer-pin test's terminal reason assertion is 7-way loose where an exact one passes).

Non-blocking but must land before minting: F3, F6, F7, F8, F9, F10, F11, F12.

This verdict does **not** depend on anything I failed to reproduce, with one bounded exception: F4's *PC* manifestation is inferred from a faithful local reproduction of the interpreter decoupling plus the brief's report of the PC run — I did not execute on the PC. The defect itself (both expectations derived from `sys.executable` while the producer samples the child's `/proc/<pid>/exe`) is read directly from the source and confirmed by live differential here.