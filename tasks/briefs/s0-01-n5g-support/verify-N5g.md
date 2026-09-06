# VERIFY-N5g (round 10) — adversarial grade of lane N5g (every interpreter-sample site pinned)

## 0. Premise · venue · disk

```
PIN at dispatch      56e9a7d6d988dcc66e74553f1e0d7ef223731984   "S0-01 WIP checkpoint 8k: …" -- HELD
graded commit        5885228  (coordinator mid-task amendment: the F8 fixture)
git diff --stat 56e9a7d 5885228 -> docs/INCIDENT-LOG.md | tests/test_s0_01_acp_probe.py (12 ±) | todo/BUILD-TASKLIST.md
                     => the ONLY scope file that moved is tests/test_s0_01_acp_probe.py; all others byte-identical.
df -h /  (before first batch)  /dev/vda 252G 23G 15G 62%      (64% at the end; never below 14 G; no ENOSPC)
interpreter          python3 -> /usr/local/bin/python3, realpath /usr/bin/python3.11, 3.11.15; pytest 9.1.1; jsonschema 4.25.1
```
All work on `scratchpad/vn11/repo` (`git archive 5885228 | tar -x`, `git init` + base commit). Every mutant restored from
`scratchpad/vn11/pristine/`, never git-restore/stash/checkout of a shared tree. `--basetemp` per pytest run, deleted after. No xdist.
**Final state: 13/13 in-scope + read-only-context files PRISTINE vs the `5885228` blobs; my copy `git status` empty.
The shared tree was never written to** (read-only git only; it still carries only the other lanes' 3 modified files).

Lane report graded: `tasks/briefs/s0-01-n5g-support/N5g-report.md`. Report shas reproduced exactly:
`671e35785d9fb759826b579f14e6573f59af1d6927d94cc8f9f4d8d6e1e565c1  proofs/S0-01/tools/acp_probe.py`
`30a2806e7825b0f0e99e1d4918264b8e19f026a570096243018ca1ed72c7c305  proofs/schemas/spec.schema.json`

## 1. Gate lines (mine, pasted verbatim, at 5885228)

```
pytest-summary: 256 passed in 56.06s      (five-file suite, run 1)
pytest-summary: 256 passed in 56.14s      (five-file suite, run 2)
pytest-summary: 33 passed in 6.05s        (tests/test_spec_probe_schemas.py tests/test_proof_runner.py, run 1)
pytest-summary: 33 passed in 6.12s        (tests/test_spec_probe_schemas.py tests/test_proof_runner.py, run 2)
pyflakes rc=0   (acp_probe.py, test_s0_01_acp_probe.py, test_s0_01_spec_runner.py, test_spec_probe_schemas.py)
closing re-run: 256 passed in 55.40s · 33 passed in 5.99s · pyflakes rc=0
```
One earlier five-file run was SIGTERM-killed by the shared box (`pytest-exit: 143`, 233 dots) — re-ran clean; not a suite defect.

**Denominator verified, not assumed:** parent `a5b9e9b` → HEAD adds exactly 4 test defs, none deleted or renamed
(`late_readlink_failure_keeps_the_early_reading`, `interpreter_is_child_not_self_for_a_silent_agent`,
`interpreter_is_sampled_once_at_the_first_a2c_byte`, `interpreter_deleted_after_start_is_a_loud_probe_error`);
252 + 4 = **256 collected**. Schema suite 31 → 33 = the two new parametrize ids (`multiline`, `trailing-newline`).

**`acp_probe.py` is comments-only, verified not assumed:** stripping comments/blank lines from `a5b9e9b` and `5885228`
gives **0 code-line differences**. (Consequence: item 1's "paired control on the parent commit" is VACUOUS at this PIN —
the behavioural control is `736bb94`, run below.)

## 2. Agent-shape table + block attribution (real probe, 3-site instrument, HEAD)

Instrument = a marker-only copy of the probe (`acp_probe_instr.py`, diff vs pristine = the marker lines alone):
`EARLY`=`:235` · `EARLY_SHA_ERR`=`:239` · `LATE`=`:301` · `LATE_SHA_ERR`=`:306` · `LATE_CLEAR`=`:314` ·
`LATE_EXC`=`:316` · `POST_BLOCK`=`:374` · `POST_RL_OK`=`:379` · `POST_RL_ERR`=`:381` · `POST_SHA_OK`=`:385`.

| shape | rc | interp realpath | sha8 | agent_exit | probe_error | sites fired |
|---|---|---|---|---|---|---|
| A `sys.exit(0)`, no stdout | 1 | /usr/bin/python3.11 | f56a5885 | 0 | BrokenPipeError: agent process exited before c2a write landed | EARLY |
| B `sys.exit(1)`, no stdout | 1 | /usr/bin/python3.11 | f56a5885 | 1 | same | EARLY |
| C `os.close(1)` + sleep | 0 | /usr/bin/python3.11 | f56a5885 | 0 | null | EARLY,POST_BLOCK |
| D 1 byte then `os._exit(0)` | 1 | /usr/bin/python3.11 | f56a5885 | 0 | BrokenPipe… | EARLY |
| E full answer + `stdin.read()` | 0 | /usr/bin/python3.11 | f56a5885 | 0 | null | EARLY,LATE |
| F answer, exit at once | 0 | /usr/bin/python3.11 | f56a5885 | 0 | null | **EARLY,LATE_EXC** |
| G first byte after 2 s | 0 | /usr/bin/python3.11 | f56a5885 | 0 | null | EARLY,LATE |
| H 1 byte, sleep .05, `_exit` | 0 | /usr/bin/python3.11 | f56a5885 | 0 | null | EARLY,LATE |
| I answer, no trailing NL | 0 | /usr/bin/python3.11 | f56a5885 | 0 | null | EARLY,LATE |
| J never answers, hangs | 0 | /usr/bin/python3.11 | f56a5885 | −9 | null | EARLY,POST_BLOCK |
| K closes stdout, sleeps | 0 | /usr/bin/python3.11 | f56a5885 | −9 | null | EARLY,POST_BLOCK |
| L partial line then hang | 0 | /usr/bin/python3.11 | f56a5885 | −9 | null | EARLY,LATE |
| M self-SIGTERM, no stdout | 0 | /usr/bin/python3.11 | f56a5885 | −15 | null | EARLY,POST_BLOCK |
| N interpreter unlinked at start | 1 | `…/myshell (deleted)` | null | −9 | interpreter sample failed: [Errno 2] … '…/myshell (deleted)' | EARLY,EARLY_SHA_ERR,POST_BLOCK |
| W `#!/bin/sh` sleep + exec py | 0 | /usr/bin/python3.11 | f56a5885 | 0 | null | EARLY,LATE |
| EV `#!/usr/bin/env python3` | 0 | /usr/bin/python3.11 | f56a5885 | 0 | null | EARLY,LATE |
| DASH `#!/bin/dash` single exec | 0 | /usr/bin/dash | 86d31f6f | 0 | null | EARLY,LATE |
| BP1 (A + readlink always fails) | 1 | null | null | 0 | BrokenPipe… | — |
| BP2 (D + readlink always fails) | 1 | null | null | 0 | BrokenPipe… | — |

Value columns match the round-9 table for all 19 shapes. Two attribution deltas, both explained:
* **Shape F now shows `LATE_EXC`, not `LATE`** — the child is already a zombie when the probe readlinks after the first chunk,
  so the late `except` arm fires and *keeps the early reading*. **The N5g-F1 arm is reachable by a REAL agent shape**, not only
  under injection — that strengthens the lane's F1 beyond what the ruling assumed.
* **Shape N** differs from round-9 because the fixture differs (the lane's amended one). rc/realpath/sha/reason all as specified.
* **`POST_RL_OK` / `POST_RL_ERR` / `POST_SHA_OK` fired in 0 of 19 shapes.** `POST_BLOCK` is entered by C/J/K/M/N but both
  inner guards are false (the early loop already filled the pair). Confirms round-9 F10 and the lane's F10 comment.

**Repeat measurements (HEAD unloaded / HEAD under 4 CPU hogs / the pre-fix parent probe `736bb94`, 12× each):**

| agent | HEAD unloaded | HEAD 4-hogs | PARENT 736bb94 |
|---|---|---|---|
| W (sh wrapper) | python3.11 **12/12**, sha f56a5885 12/12, rc 0 ×12 | python **12/12** | **/usr/bin/dash 12/12**, sha 86d31f6f |
| EV (env shebang) | python3.11 **12/12**, rc 0 ×12 | python **12/12** | **/usr/bin/env 12/12**, sha 595f3912 |

The later-reading-wins fix is real and the paired control reproduces the defect on the pre-fix probe. (Round-9 measured the parent
EV at 10/12 env + 2/12 python; mine is 12/12 env — same direction, different ratio, consistent with round-9's own F11 note.)

**Shapes A and D, 20× each:** rc `{1: 20}` both; **1 interpreter triple each** (`/usr/bin/python3.11`, f56a5885);
`probe_error == "BrokenPipeError: agent process exited before c2a write landed"` **20/20**;
`stderr == "acp_probe: BrokenPipeError: agent process exited before c2a write landed"` **20/20**; **0 wrong arms**.

**Docstring-mechanism measurement** (`/proc/*/exe` readlinks per probe run, 6 runs each): shape A → **1**, shape M → **1**,
shape K → **1**, shape E → **2** (early + late). The renamed test's "loop breaks on iteration 1" claim holds; the 101-iteration
figure holds only under an always-failing readlink.

## 3. Mutant table — every row below is the FULL five-file suite (256 tests) unless the row says otherwise

| id | mutation | result | killer(s) I observed |
|---|---|---|---|
| NOOP | — | `256 passed in 54.97s` | — |
| **LATE-NULL** | late readlink failure nulls the early reading | **KILLED `1 failed, 255 passed`** | late_readlink_failure_keeps_the_early_reading |
| **LG2-EARLY** | early loop reads `/proc/self/exe` | **KILLED `2 failed, 254 passed`** | interpreter_is_child_not_self_for_a_silent_agent, interpreter_deleted_after_start_is_a_loud_probe_error |
| **DL_SCALE** | deadline 0.2→0.4 AND step 0.002→0.004 | **KILLED `1 failed, 255 passed`** | early_sample_loop_bound_is_pinned (on the new absolute-value assert) |
| **LATE-EVERY** | re-sample on every chunk | **KILLED `1 failed, 255 passed`** | interpreter_is_sampled_once_at_the_first_a2c_byte |
| **PINS-12KEY** | 12th key in `pins.NEGATIVE_IDENTITY_KEYS` | **KILLED `36 failed, 220 passed`** | 29 named tests incl. self_deleting…, m3_handler… |
| EARLY-DEL | delete the post-Popen loop | KILLED `8 failed, 248 passed` | early_retry_recovers, early_sample_loop_bound, fast_exit_deterministic, agent_exits_without_output_keeps, broken_pipe_deterministic, sampled_once_at_first_a2c_byte, +2 |
| LATE-DEL | delete the a2c-triggered sample | KILLED `6 failed, 250 passed` | env_shebang_constant, sampled_once…, final_exec_not_a_wrapper, interpreter_sample_failure(+after_child_exit), late_sample_clears |
| LATE-GATE | re-gate on `interp_realpath is None` | KILLED `4 failed, 252 passed` | env_shebang_constant, sampled_once…, final_exec_not_a_wrapper, late_sample_clears |
| LATE-NOCLEAR | drop the error-clearing arm | KILLED `1 failed, 255 passed` | late_sample_clears_early_interpreter_error |
| APF1A | one readlink at Popen, no retry | KILLED `2 failed, 254 passed` | early_retry_recovers, early_sample_loop_bound |
| POST-DEL | delete the post-loop block | KILLED `1 failed, 255 passed` | post_loop_sha256_failure_truthful_error |
| F3PREFIX | drop the `interpreter sample failed: ` prefix (4 sites + the fixed wording) | KILLED `5 failed, 251 passed` | interpreter_deleted_after_start…, interpreter_sample_failure(+after_child_exit), late_sample_clears, post_loop_sha256… |
| DL_DOUBLE | deadline 0.2→0.4 | KILLED `1 failed, 255 passed` (observed count **201**) | early_sample_loop_bound_is_pinned |
| EV_OUTSIDE | `_write_evidence` moved out of the `try` | KILLED `1 failed, 255 passed` | m3_handler_writes_complete_evidence |
| EV_SWALLOW | handler returns without writing/exiting | KILLED `3 failed, 253 passed` | bad_agent_path, error_surfaces_on_exception, m3_handler… |
| M3-NOENV | handler skips `env.json` | KILLED `1 failed, 255 passed` | m3_handler_writes_complete_evidence |
| M3-1KEY | handler writes `{"probe_error": …}` only | KILLED `1 failed, 255 passed` | m3_handler_writes_complete_evidence |
| M3-NOTIMELINE | handler skips `timeline.jsonl` | KILLED `2 failed, 254 passed` | bad_agent_path, m3_handler… |
| FC-BIND | `from time import monotonic, sleep` in the loop | KILLED `1 failed, 255 passed` | early_sample_loop_bound_is_pinned |
| LG2-LATE | late sample reads `/proc/self/exe` | KILLED `1 failed, 255 passed` | interpreter_is_child_not_self |
| **LG2-POST** | **post-loop reads `/proc/self/exe`** | **SURVIVED `256 passed in 55.70s`** | **NONE — finding R10-N5g-F1** |
| LATE-DISCARD-DIFF (new) | late reading discarded when ≠ early | KILLED `2 failed, 254 passed` | final_exec_not_a_wrapper, env_shebang_constant |
| LATE-CLEARALL (new/rerun) | late success clears **any** `probe_error` | SURVIVED `256 passed` | **equivalent-by-reachability — proven, see instruments** |
| SCHEMA-NOPAT | pattern removed | KILLED `4 failed, 29 passed` (schema suite) | spec_failure_reason_rejects_edge_whitespace_and_newlines ×4 |
| SCHEMA-TRAILNL | old `$`-anchored pattern | KILLED `1 failed, 32 passed` (schema suite) | …_and_newlines[trailing-newline] |
| **SILENT-KEEP-RAISE** (instrument) | raise when the late `except` arm keeps a non-null early reading | **FIRED — `1 failed, 255 passed`** | **exactly `test_probe_late_readlink_failure_keeps_the_early_reading`, and nowhere else** |
| **CLEAR-GUARD-RAISE** (instrument) | raise if a non-`interpreter sample failed:` error reaches the clear guard | **NEVER FIRED** (256 tests) | reachability proof for LATE-CLEARALL |
| **POST-RL-RAISE** (instrument) | raise on entry to the post-loop readlink | FIRED — `1 failed, 255 passed` | **only `test_probe_post_loop_sha256_failure_truthful_error`** |
| SR-03 (runner) | per-line rule dropped (match whole text) | KILLED `7 failed, 17 passed` | per_line_rule_holds_for_a_multiline_expected_reason **+6 others** |
| SR-05 | `in` → `==` | KILLED `3 failed, 21 passed` | records_the_first_matching_line, observed_line_not_expected, raw_line_not_stripped |
| SR-06 | match `line.strip()` | SURVIVED `24 passed` | **equivalent by proof, premise re-verified** |
| SR-07 | case-folded | KILLED `1 failed, 23 passed` | reason_match_is_case_sensitive |
| SR-08 | record the LAST match | KILLED `1 failed, 23 passed` | records_the_first_matching_line |
| SR-09 | record `line.strip()` | KILLED `1 failed, 23 passed` | records_the_raw_line_not_the_stripped_line |
| SR-10 | `in` → `startswith` | KILLED `3 failed, 21 passed` | as SR-05 |
| SR NOOP | — | `24 passed in 8.49s` (spec_runner + proof_runner) | — |

**Totals: 36 mutants + 3 raise instruments run. 33 killed by a NAMED test · 1 survivor (LG2-POST) ·
2 equivalent (LATE-CLEARALL by reachability, proven with CLEAR-GUARD-RAISE; SR-06 by proof).**
All five round-9 survivors (LATE-NULL, LG2-EARLY, DL_SCALE, LATE-EVERY, PINS-12KEY) now die by named tests.
`_last_good` / `_interp_sampled`: **0 hits** in `proofs tests scripts` (present only in my extracted `736bb94` copy).

## 4. Round-10 B — the schema pattern

`proofs/schemas/spec.schema.json:36` → `"failure_reason": {"type":"string","minLength":1,"pattern":"^\\S(.*\\S)?(?![\\s\\S])"}`
(the only `failure_reason` subschema in the file: `/$defs/leg/properties/expect/properties/failure_reason`).

```
trailing-newline 'foo\n'    schema_rejected=True      leading-space   ' foo'     schema_rejected=True
multiline        'a\nb'     schema_rejected=True      trailing-cr     'foo\r'    schema_rejected=True
leading-newline  '\nfoo'    schema_rejected=True      trailing-nbsp   'foo\xa0'  schema_rejected=True
trailing-tab     'foo\t'    schema_rejected=True      trailing-2nl    'foo\n\n'  schema_rejected=True
trailing-space   'foo '     schema_rejected=True
7 committed spec-leg failure_reason values (S0-01, S0-07, S0-09, S0-10, S0-11 ×2, S0-12): accepted=True ×7
```
**ECMA-262 question, answered from primary source.** `jsonschema` 4.25.1 compiles the pattern with **Python `re`** —
`/usr/local/lib/python3.11/dist-packages/jsonschema/_keywords.py`, `def pattern(...)`: `re.search(patrn, instance)`
(`re.search`, no MULTILINE, so `^` is start-of-string and the end anchor must be explicit). Under ECMA-262 `[\s\S]` is
also "any character", so `(?![\s\S])` is likewise a true end-of-input assertion; and ECMA's `$` (no `m`) already matches
only at end of input, so ECMA rejected `"foo\n"` under the OLD pattern too. **The new pattern has identical semantics in
both engines; the change is a Python-side repair with no ECMA regression.** SOLID.

## 5. Round-10 C — the attestation chain

```
python3 scripts/validate-ledger integrity --root .   ->  S0-09 PRESENT  S0-10 PRESENT  S0-11 PRESENT  S0-12 PRESENT
                                                        conformance_checked_decision 3/3 · execution_proof 1/7
                                                        blocked_credential 1/1 · blocked_host 0/1 · rc=0
python3 scripts/ledger-gen --root .  x2  -> f13bc801e553a01e5381f6f35b1d1bd8d73454a9982047a9989a5dddcb1507b6 (both), and
                                            `git status --porcelain proofs/ledger.json` EMPTY -> byte-identical to the commit.
```
**The four `result.json` diffs vs the parent are `recorded_at` + per-leg `started_at`/`finished_at` + the
`proofs/schemas/spec.schema.json` attestation hash (`5f50497a…` → `30a2806e…`) + the top-level `digest`. Nothing else.**
**`proofs/ledger.json`'s whole diff is four `normalized_digest` moves** — the new values:
S0-09 `c5e549fde7d2bffc5d7a07af32c2c06b4dca9a7b5f079e3679b7260a09d788cc` ·
S0-10 `32a3cf0ae8bac1d69417531e6e6c8160629eef9531561ad0f1ace8e64c5b2fe5` ·
S0-11 `82cb3770943a9faa39152790405e5cf1a2d9c2df5be679ccf85e1678b7f6b871` ·
S0-12 `3ef400bb76971f7a14228c0adece5bcce31f62d0b0fe3638800b23e71e117e0e`.
**Nothing hand-edited:** a fresh `proof-runner run` of S0-09/S0-10/S0-12 on my copy reproduced files whose only differences
from the lane's committed artifacts are `recorded_at`/`started_at`/`finished_at`/`digest`; `ledger-gen` after that regeneration
changed **no** `normalized_digest`. S0-11 could not be re-run here — see R10-N5g-F8 (my venue, not the repo).

## 6. Round-10 D/E — the once-only sample, shape N, hygiene items

* **F6 once-gate present and pinned:** `acp_probe.py:298-299`, comment `:294-297`; LATE-EVERY dies (above).
* **The stated rule is NOT what the code delivers — see R10-N5g-F2.** Agent that flushes its first protocol byte and then
  `os.execl("/bin/dash", …)`: recorded interpreter over **48 runs** = `/usr/bin/python3.11` **41**, `/usr/bin/dash` **7**
  (12 unloaded: 10/2 · 24 unloaded: 21/3 · 12 under 4 hogs: 10/2). rc 0 ×48. **Not stable 12/12.**
* **Shape N test present and exact** (`tests/test_s0_01_acp_probe.py:1927`): rc 1 · realpath ends `" (deleted)"` ·
  sha256 `None` · `probe_error == "interpreter sample failed: [Errno 2] No such file or directory: '<path> (deleted)'"`.
  **Coordinator's item — the amended fixture, measured 6× per interpreter source:** all four assertions hold
  **6/6 with a `/bin/bash` copy** (the Fedora shape), **6/6 with `os.path.realpath("/bin/sh")`** (dash here) and
  **6/6 with the pre-amendment `/bin/dash`**. The agent script (`exec 1>&-` then `sleep 5`) is POSIX and behaves
  identically under both shells. LG2-EARLY still dies on this test at 5885228. The amendment is behaviour-preserving.
* **F13 env-shebang test:** minimal env (`S0_01_AGENT`, `S0_01_FRAMEDIR`, `PYTHONDONTWRITEBYTECODE`, `ACP_PROBE_TIMEOUT`,
  `PATH`, `HOME`), `assert r.returncode == 0, r.stderr` at `:1522` and `assert "probe_error" not in rid` at `:1524`, per run. ✔
* **F14 time conjunct gone:** the gate at `:1654` is `if _sha_call[0] == 1:` alone; docstring says so. ✔
* **F4 rename + sibling:** `test_runner_per_line_rule_holds_for_a_multiline_expected_reason`
  (`tests/test_s0_01_spec_runner.py:437`) with the corrected docstring; schema sibling
  `test_spec_failure_reason_rejects_edge_whitespace_and_newlines` (`tests/test_spec_probe_schemas.py:101`) with
  `multiline` + `trailing-newline` ids. ✔
* **F7 comment states unreachability** at `acp_probe.py:309-311`, and CLEAR-GUARD-RAISE proves it. ✔
* **F9 key set from pins:** `set(rid) - {"probe_error"} == set(pins.NEGATIVE_IDENTITY_KEYS)` at `:1287` and `:1728`;
  the identity key COVERS the changing attribute (PINS-12KEY dies). ✔
* **Exact-reason census over the probe tests:** `rid["probe_error"] ==` equality asserts **14**; `in rid[` substring asserts
  **0**; `.startswith(` **2** (both harness stdout parsing, `:1605`/`:1915`, not reason assertions); `assert … or `
  **1** (`:435`, inside a literal error string). **0 inexact reason assertions survive.**
* **`realpath(sys.executable)` assertion sites (F12): 5** — `:457, :659, :895, :1464, :1784` (+ a docstring mention `:652`);
  every one of those fixtures is a `#!{sys.executable}` agent, so none of them alone can catch a self-sampling read;
  the self-sampling killers are the bash-agent tests (`:769`, `:1793`) and the deleted-interpreter test (`:1927`).
* **No wall-clock assertions added:** `time.time`/`perf_counter` → **0** hits in the probe tests; the only elapsed bounds are
  pre-existing (`:327 < 10`, `:380 < 15`) plus the pre-existing 0.3 s gate at `:1211` (see R10-N5g-F6).
* **`tmp_path` hygiene:** every write in the four new tests goes to a `tmp_path`-derived path; the only absolute literals are
  `/proc/…`, `/bin/sh`, `/bin/bash` and the two sentinels (`/SENTINEL/should-never-be-recorded`, `/tmp/fake_interp (deleted)`),
  none of which is ever written.
* **"14 committed reasons" appears in nothing new** — only in the round-9 verdict (quoting it as wrong), the round-9 brief and
  the tasklist line quoting that verdict. ✔

## 7. Item 4 — the fake-clock bound

`test_probe_early_sample_loop_bound_is_pinned` (`:1543`): HEAD **passes with exactly 101 attempts**; DL_DOUBLE →
`AssertionError: early sample loop attempted 201 readlinks, expected 101 (ceil(0.2/0.002) + 1)`; DL_SCALE → dies on the NEW
`assert _ap._EARLY_SAMPLE_DEADLINE_S == 0.2` at `:1617` (the 101-count assert still passes under DL_SCALE — exactly the ratio
gap the new asserts close). **The fake clock covers the real call path:** the loop uses the module attribute the test patches,
and FC-BIND (`from time import monotonic, sleep`) is KILLED. SOLID.

## 8. Item 3 — the crash path, live (real probe, real checker, real validator)

```
probe rc= 1 ; stderr = "acp_probe: FileNotFoundError: [Errno 2] No such file or directory: '…/livecap/agent_self_delete.py'"
Traceback in stderr: False
files: ['agent-stderr.txt(0B)', 'env.json(611B)', 'runtime-identity.json(1017B)', 'timeline.jsonl(491B)']
rid key count: 12   (set(rid) - {"probe_error"} == set(pins.NEGATIVE_IDENTITY_KEYS) -> True)
probe_error == "FileNotFoundError: [Errno 2] No such file or directory: '<agent_realpath>'"   -> MATCH
agent_entrypoint_sha256: None

check_initialize.py request  <cap> -> rc=1
    failure_reason: negative: probe reported an error: FileNotFoundError: [Errno 2] No such file or directory: '…/agent_self_delete.py'
check_initialize.py response <cap> -> rc=1
    error code=-32602 message=Invalid params
negative_contract.validate_negative_dir(cap) -> NegativeFailure: probe reported an error: FileNotFoundError: [Errno 2] …
```
The producer error is named at every layer; `env.json absent` never appears. **M3 path** (`_write_evidence` patched to raise):
rc 1, stderr `acp_probe: RuntimeError: boom`, all four files, key set == pins (12 keys), `probe_error == "RuntimeError: boom"`,
timeline 2 lines. SOLID.

**Item 6 — the coordinator's F7 hunk** (`proofs/S0-01/negative_contract.py:165-173`), current validator:
`0 → "probe reported an error: 0"` · `False → …False` · `[] → …[]` · `{} → …{}` · `"" → …(empty reason)` · `"x" → …x`.
Red on the previous validator (`f"…{rid['probe_error'] or '(empty reason)'}"`), pasted verbatim:
`4 failed, 1 passed, 50 deselected in 0.09s` — exactly the claimed shape.

## 9. Findings

### R10-N5g-F1 — BLOCKING · SOLID · mutant LG2-POST survives the FULL 256-test suite: the post-loop site's identity SOURCE is the one interpreter-sample site still unpinned, and "equivalent by test design" is not equivalence
`vn11/repo/proofs/S0-01/tools/acp_probe.py:379` (`interp_realpath = os.readlink("/proc/%d/exe" % proc.pid)` inside
`if interp_realpath is None:` at `:377`).
**Concrete failing input / measurement.** Mutating `:379` to `/proc/self/exe` → **`256 passed in 55.70s`** (the lane's
`53 passed` was the probe file alone; it survives the real five-file gate too). Instrument **POST-RL-RAISE** shows the site is
reached by exactly **one** test, `test_probe_post_loop_sha256_failure_truthful_error` (`:1172`), whose `_gated_readlink`
(`:1208-1213`) returns `_fake_path` for **any** `/proc/*/exe` string — so the correct and the self-sampling implementation are
indistinguishable to it. POST-DEL and F3PREFIX pin the WORDING at that site; nothing pins WHOSE exe it reads.
Observed vs expected: the brief's title and acceptance bar are "every interpreter-sample site is pinned" / "every
non-equivalent one killed by a NAMED test", granting equivalence only to LATE-CLEARALL. LG2-POST is **not** equivalent —
I built its killer and measured it (below). The lane's own row reads `SURVIVED 53 passed | equivalent-by-test-design`;
that phrase describes a hollow green, not an equivalent mutant, and the report's `not_done: None` claims the bar is met.
**Reachability, measured (this is why it is not also a live defect):** `POST_RL_*` fired in **0 of 19** real shapes; a zombie's
`/proc/<pid>/exe` readlink fails ENOENT (measured) but a dead child also means the c2a write raises BrokenPipe, which sets
`c2a_delivered = False` and skips the entire block at `:275`; and the first readlink after `Popen` **never** failed in
**200/200** trials against an instantly-exiting child, nor did the whole 0.2 s loop in **60/60**. So today the site is
unreachable for a same-uid, non-setuid child on a normal `/proc`. The residual matters because the failure DIRECTION flips:
today an unreachable-child post-loop read is fail-CLOSED (`probe_error: agent exited before its first a2c byte`, rc 1);
under LG2-POST it is fail-OPEN — the probe's own python + its sha recorded as the agent's interpreter, rc 0, and
`validate_negative_dir` ACCEPTS it into an attested artifact.
**Exact red test I would add (built and measured on my copy, 2 lines):** in `test_probe_post_loop_sha256_failure_truthful_error`,
make `_gated_readlink` path-aware —
```python
            if "/proc/self/exe" in str(path):
                return "/SELF/should-never-be-sampled"   # the site must read the CHILD's exe
```
Measured: `HEAD + path-aware killer -> 1 passed` · `LG2-POST + path-aware killer -> 1 failed` ·
`LG2-POST + current test -> 1 passed` (the blind control) · `HEAD + current test -> 1 passed`.
**Minimal fix:** that patch, plus correct the LG2-POST row to "KILLED by …post_loop_sha256_failure_truthful_error" and drop
the "equivalent-by-test-design" category from the report, commit body and ledger.

### R10-N5g-F2 — BLOCKING · SOLID · the once-gate comment states a determinism the code does not have (a hollow green in prose, at the exact rule this round was told to state)
`acp_probe.py:294-297`: "sampled once, at the first a2c byte: the stage that wrote the first protocol byte is the interpreter
of record; an agent that execs later is recorded as the stage that spoke first".
**Concrete failing input.** An agent that reads the request, writes+flushes a notification, then `os.execl("/bin/dash", …)`:
recorded interpreter over **48 runs** = python **41**, **dash 7** (12 unloaded 10/2 · 24 unloaded 21/3 · 12 under 4 hogs 10/2),
rc 0 ×48. **7/48 ≈ 15 % of runs record the stage that did NOT speak first.** Mechanism, re-derived from the code: the once-gate
at `:298-299` fixes HOW MANY samples are taken; the sample itself is taken at `:301`, after `os.read` returns the chunk, and
that instant races the child's subsequent `execve`. The gate does not, and cannot, make the observation coincide with the
first-byte instant. (Round-9 F6 measured the same agent at dash 12/12 on the pre-gate code; the once-gate improved the ratio
and left the rule false.)
Observed vs expected: the comment asserts a rule; the code delivers a race with a strong bias. The ruling handed the lane this
exact wording and the lane shipped it verbatim without measuring it.
**Exact red test I would add:** `test_probe_interpreter_of_an_agent_that_execs_after_its_first_byte_is_the_first_byte_stage` —
the agent above, but with the exec made deterministic relative to the probe's readlink by patching `os.readlink` to block on a
file-based barrier the agent drops after `execve` (or, if determinism is not wanted, delete the second clause). **Minimal fix
(cheapest, and what I recommend):** replace the second clause with what is true — "the reading is taken once, at the moment the
probe consumes the first a2c chunk; an agent that execs after its first byte may be recorded as either stage (measured
41/48 first-stage, 7/48 second-stage) — a multi-stage agent must not exec after speaking".

### R10-N5g-F3 — SOLID · two mutant rows were graded on a 53-test subset, not the five-file suite the lane's own bar demands, and two more rows are not reproducible
`tasks/briefs/s0-01-n5g-support/N5g-report.md`, Mutant table.
| row | lane's pasted denominator | mine (full five-file suite) |
|---|---|---|
| PINS-12KEY | `2 failed, 51 passed` = **53** (the probe file alone) | `36 failed, 220 passed` = 256 — still KILLED |
| LG2-POST | `SURVIVED 53 passed` | `SURVIVED 256 passed` — survival confirmed, on a 5× larger gate |
| EARLY-DEL | `KILLED 55 failed` | `8 failed, 248 passed` |
| EV_OUTSIDE | `KILLED 35 failed` | `1 failed, 255 passed` |
| LATE-EVERY | `KILLED 1 failed` (no denominator) | `1 failed, 255 passed` |
The brief says "Mutants: … run the suite" with the acceptance bar "The five-file suite TWICE"; round-9's table header was
"every run is the FULL five-file suite". Two rows were not. The EARLY-DEL/EV_OUTSIDE counts are not reproducible with the
natural mutation (delete the loop / move the call out of the `try`) — both still KILL, so no green is at risk, but the
numbers are unverifiable as written. **Minimal fix:** re-run those rows on the five-file suite and paste the real denominators,
or state the subset explicitly per row.

### R10-N5g-F4 — SOLID · F11 (hygiene: "every `file:line` in your report re-derived at your final tree") is unmet while `not_done` says "None"
Re-derived on my copy of `5885228` (the probe file is byte-identical at `56e9a7d`, so no excuse from the amendment):
| claim in the report | report says | actual |
|---|---|---|
| F6 once-gate comment | `acp_probe.py:296-299` | **`:294-297`** (`:298-299` is the `if not _late_sampled:` code) |
| F7 clear-guard comment | `acp_probe.py:310-313` | **`:309-311`** |
| F10 post-loop comment | `acp_probe.py:371-375` | **`:369-372`** |
| F3 pinned absolute values | `tests/…acp_probe.py:1612-1614` | comment `:1612`, asserts **`:1617-1618`** |
| F9 second pins assertion | `tests/…acp_probe.py:1718-1721` | **`:1727-1731`** |
Correct as written: F1 comment `:317-319`; F1 test `:1737`; F2 `:1793`; F6 test `:1820`; F8 `:1927`; F14 `:1624`/gate `:1654`;
F9 first site `:1286-1290`; F13 `:1508-1528`; spec_runner `:437`; schemas `:101`. The brief's bar: "an empty not_done beside an
unmet item reopens the lane". **Minimal fix:** correct the five refs, or move F11 to `not_done` with the reason.

### R10-N5g-F5 — SOLID · the amended F8 docstring still calls the fixture a hardlink, which is what the amendment set out to remove
`tests/test_s0_01_acp_probe.py:1933`: "Uses an in-process wrapper to delete the **hardlink** before the first readlink —
deterministic, no race." The amendment's own commit body says the docstring "called the copy a hardlink (it never was)" and
claims it corrected; the first paragraph and the inline comment at `:1936-1937` were corrected, this sentence was not.
**Minimal fix:** "delete the copied interpreter".

### R10-N5g-F6 — UNSURE (measured low risk) · the post-loop killer itself carries the 0.3 s wall-clock gate F14 removed elsewhere, and its failure mode is silent vacuity
`tests/test_s0_01_acp_probe.py:1211` — `if time.monotonic() - _start < 0.3: raise OSError("No such process")`.
The gate must outlast the early loop's 0.2 s deadline, so some time coupling is inherent — but if the early loop's 101
iterations ever exceed 0.3 s wall, the early loop succeeds with `_fake_path`, the early sha fails with the SAME message, all
four assertions still pass, and the test silently stops covering the post-loop block (POST-DEL would then survive). Measured
margin here: the early loop completes 101 iterations in ≈0.2 s and POST-RL-RAISE fired in this test on every run I made.
**Minimal fix:** gate on a readlink call counter (fail calls 1..101, succeed after) instead of the clock, exactly as F14 did.

### R10-N5g-F7 — SOLID (informational) · round-9 F4's "sole killer of SR-03" is not reproducible
`tests/test_s0_01_spec_runner.py:437`. With a faithful SR-03 (per-line rule dropped, a line still recorded) the kill set is
**7 tests**: `per_line_rule_holds_for_a_multiline_expected_reason`, `matches_reason_on_non_first_line`,
`valid_result_matches_schema_validator_digest_and_integrity`, `indent_two_digest_mutant_is_rejected`,
`parent_environment_is_not_inherited_by_legs`, `spec_classification_is_rejected…`, `timeout_kills_the_leg_process_group…`.
Keeping the test is still right (it is the only one that names the per-line rule) but the round-9 rationale overstates it.
No action for the lane.

### R10-N5g-F8 — SOLID (my venue, NOT a repo defect) · S0-11's regeneration cannot run from a scratch copy under `/tmp/claude-0`, and a failed `proof-runner run` deletes the minted artifact
`proofs/S0-11/check_eval_hardening.py:268` returns `["observation-failed"]` when the isolated child never signals ready.
Reproduced 3/3 on my copy (`rubric-isolation-failure: observation-failed`, `leg-exit-mismatch: S0-11 positive expected 0 got 1`).
**Root cause found and it is mine:** the check drops privileges to `nobody` (`:79-82`, `unshare --net` + `setpriv --reuid 65534`),
and `/tmp/claude-0` is `drwx------ root`, so the dropped child cannot traverse to `proofs/S0-11/fixtures/rubric_probe.py`.
Proven: `su -s /bin/sh nobody -c "cat <scratch>/proofs/S0-11/fixtures/rubric_probe.py"` → **Permission denied**; the same file
in `/home/user/agent-factory` → **readable**. So this is a verification-location artefact; nothing is wrong with S0-11 or with
the lane's regeneration, and the ledger check that matters (`ledger-gen` reproducing the committed `proofs/ledger.json`
byte-identically) passed. Recorded because I hit it: `scripts/proof-runner:126` `_remove(result_path)` on a real failure
**deletes** the existing artifact (flipping S0-11 PRESENT → ABSENT, `execution_proof` 1/7 → 0/7) — this is DELIBERATE and
documented in `run_proof` ("a real capable-run FAILURE invalidates the stale artifact"), so it is behaviour, not a bug; but any
future verifier re-running `proof-runner` on a copy where a proof cannot run will destroy a minted artifact. Suggest verifiers
run the regeneration only where every proof's venue prerequisites hold, or use a world-traversable scratch path.

### R10-N5g-F9 — SOLID (informational) · a clean live negative capture is rejected on the agent identity pin, as designed
An ad-hoc `-32602` agent produced a clean capture (rc 0, no `probe_error`, four files, interp `/usr/bin/python3.11`), and both
`check_initialize.py request` and `validate_negative_dir` reject it with **`agent_argv mismatch`** — the pinned agent identity
is enforced. A fully green negative capture needs the pinned `hermes-acp`, i.e. a PC-side artefact. No action; recorded so the
absence of a green live negative in this report is not read as a gap in the lane.

## 10. What I reproduced vs reviewed statically vs deliberately skipped

**Reproduced (ran it myself):** the premise and 13-file byte-identity at `5885228`; the `56e9a7d`→`5885228` diff; both five-file
runs and both schema/runner runs plus a closing pair; pyflakes; the 252→256 denominator and the exact set of 4 new tests; the
comments-only proof for `acp_probe.py` (0 code-line diffs); the 19-shape table with a 3-site block-attribution instrument;
W/EV 12× on HEAD unloaded, 12× under 4 CPU hogs, and 12× on the pre-fix `736bb94` probe; A/D 20× each with per-arm exact reason
and stderr; readlink-count-per-run for shapes A/E/K/M; the exec-after-first-byte race 48×; **36 mutants + 3 raise instruments**,
each over the full five-file suite (schema mutants over the schema suite, SR mutants over spec_runner+proof_runner); the
path-aware LG2-POST killer red/green; the fake-clock 101/201 measurement; the 9 hostile schema strings and the 7 committed
spec-leg values; the `jsonschema` `pattern` implementation read from its installed source; `validate-ledger integrity`,
`ledger-gen` ×2 byte-identity, the four `result.json` diffs, the ledger `normalized_digest` diff and a fresh regeneration of
S0-09/S0-10/S0-12; the live self-deleting capture through the real `check_initialize.py request|response` and
`validate_negative_dir`; the M3 `_write_evidence`-raises path; the F7 six messages and the `4 failed, 1 passed` red; the F8
fixture under bash/dash/`realpath(/bin/sh)` copies 6× each; the zombie-`/proc/exe` and 200+60 Popen-race reachability trials;
the `nobody`-traversal proof for R10-N5g-F8; the exact-reason grep census and the `_last_good`/`_interp_sampled` absence.
**Reviewed statically (no execution):** the SR-06 equivalence argument (its premise — `_validate` before the leg loop at
`scripts/proof-runner:154`, matcher at `:193-198` — was reproduced, and SR-06 survives as predicted; I found no
counter-example and the proof holds for any `expected` the pattern admits, single-character included); the ECMA-262 half of
the pattern argument (reasoned from the grammar, not executed on an ECMA engine); `tmp_path` hygiene by inspection of every
write in the four new tests.
**Deliberately skipped:** the **PC leg** — Python 3.13 and the real `hermes-acp` multi-stage exec shape are **NOT run here**
(no bridge banner this session). The coordinator reports the PC gate at `5885228` as `289 passed in 15.18s` (seven files,
8 workers) and a 3.13 leg `1 passed`; **I did not reproduce either**, and neither covers a real multi-stage-exec agent — which
is exactly the class R10-N5g-F2 leaves mis-described. I also did not re-run the tree-wide suite (out of scope) and did not
re-run S0-11's proof (R10-N5g-F8).

## Verdict

**NOT-READY** — blocking: **R10-N5g-F1** (mutant LG2-POST survives the full `256 passed` gate; the post-loop site is the one
interpreter-sample site whose identity SOURCE no test pins — proven twice, by the surviving mutant and by the POST-RL-RAISE
instrument showing the single covering test is path-blind — while the report/commit/ledger record it as
"equivalent-by-test-design" beside `not_done: None`; a 2-line killer is measured red-on-mutant / green-on-HEAD) and
**R10-N5g-F2** (the once-gate comment the ruling required states a rule the code does not deliver: an agent that execs after
its first protocol byte is recorded as the LATER stage in 7 of 48 measured runs).

Both are closable with the two changes specified above (each measured on my copy) plus the F3/F4/F5 hygiene corrections.
Everything else in the lane is **verified real**: all five round-9 survivors now die by named tests, the SILENT-KEEP arm is
executed by exactly the new F1 test and by real shape F, LATE-CLEARALL is proven equivalent-by-reachability with a
never-firing instrument, the schema pattern is a true end anchor in Python `re` and ECMA-262 with the four attestations
regenerated and `ledger-gen` reproducing the committed ledger byte-identically, the crash path writes complete, correctly
attributed evidence through the real checker, 0 inexact reason assertions survive, and the coordinator's amended F8 fixture
holds identically under a bash copy, a dash copy and the resolved system shell.
Nothing in this verdict depends on the PC leg, which I did not run.
