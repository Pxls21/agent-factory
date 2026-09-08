# P5b — S0-01 PC capture tools, round 2 (sandbox Opus 4.6 `code-implementer`)

PIN: `d3a39d18d3f29f315f1a26381574ec904ed410a9` (the commit carrying the brief; branch HEAD while the lane ran
was `68fb454cab50cc2b5ca0e0142abd53e919a605c5`, and `git diff d3a39d1 HEAD` over my whole scope is EMPTY — only
`tests/test_s0_04_compression.py` and `tests/test_s0_05_egress.py` moved, neither mine). Graded against the
DETACHED verifier pin `582ada4c` as the parent of P5a's bytes. Clock: `date -u` at the last measurement = `Tue Sep  8 04:15:57 UTC 2026`.

P5a's starting bytes verified BEFORE the first edit, exactly as the brief pins them:
`sha256sum proofs/S0-01/pins.py | cut -c1-16` = `974b86f2445d239f`, `…/pc_post.sh` = `8db8caeaf5e56f28`.
Corpus: `bash scripts/realleg_sync.sh check` -> `realleg_sync: /root/s0-01-realleg/golden intact (142 files)`.

## FILE IDENTITY (sha256[:16] / lines, FINAL bytes, `git diff --numstat d3a39d1`)

```
3a0627e8aba97798  proofs/S0-01/pins.py                       367 lines   +211  -0   (ADD-only + 3 status lines)
f57ebe22272b7308  proofs/S0-01/tools/build_capture_record.py  211 lines    +49  -1
1cc78bad5a99a0f8  proofs/S0-01/tools/pc/pc_launch.py          406 lines   +200 -67
326b620baa269e2b  proofs/S0-01/tools/pc/pc_negative.py         54 lines    +37 -17
92bf9609f54652d3  proofs/S0-01/tools/pc/pc_post.sh            155 lines    +33 -13
4017b53887573017  proofs/S0-01/tools/pc/collect_leg.sh         29 lines     +6  -2
4cd4f18b8f9e4411  tests/conftest.py                            61 lines     NEW
9620fa6923969c38  tests/test_s0_01_pc_tools.py                961 lines     (untracked at the PIN; P5a's file)
7bdaa3cb0ba6a1df  tests/test_s0_01_pc_post_scan.py            395 lines   +121 -47
04765ed8433aec8b  tests/test_s0_01_scripted_backend.py       2169 lines    +11 -19
c21fe3b969611492  tests/test_ap_screen.py                      82 lines    +32  -0   (coordinator's F11 item)
ad42f6fdd0ad36af  tests/test_edit_snapshot_ap_screen.py       361 lines    +15  -0
5129db9d3111dc2d  .claude/hooks/edit-snapshot.py              425 lines    +12  -2
```

The sha256 above are the FINAL bytes (recomputed after the last increment) and are the same 13 the
`lane_gate` RESULT below was taken from — verified 13/13 SAME afterwards.
`proofs/S0-01/check_acp_conformance.py`, `negative_contract.py`, `check_initialize.py`, `frame_tee.py`,
`acp_probe.py`, `scripted_backend.py` and everything under `proofs/S0-03/` were never opened for writing.
The numstat for the three `.py` files with large `-` counts is the diff against the PIN, i.e. it includes
P5a's own uncommitted delta, not just mine.

## PREMISE — the four blockers reproduced on the PIN+P5a bytes, before any edit

Run from `git archive d3a39d1` + P5a's six working-tree files, interpreter `/root/venv-agent-factory/bin/python`.

```
F2  the tool over a copy of /root/s0-01-realleg/golden/run-1:
      run-1: missing required leg files: tee-status.json          RC=1

F1  pytest tests/test_s0_01_scripted_backend.py::test_build_capture_record_roundtrip_check:
      E  AssertionError: build failed: test-leg: missing required leg files: argv.txt,
         backend-healthz-after.json, ... tee-status.json, upstream-records
      E  assert 1 == 0
      1 failed in 0.28s

F4  the REAL producer over a `ps` shim carrying one bystander row (/usr/bin/cat <tee>):
      # process-scan v2.4 mode=after rows=2 ... pinned_present=1 ... table_rows=2
      4242 1 7 /usr/bin/sleep 120
      5007 1 7 /usr/bin/cat /home/rocco/agent-factory/proofs/S0-01/tools/frame_tee.py
      -> the bystander is counted pinned AND written into the leg's evidence body

F6  a complete leg with timeline.jsonl truncated to 0 bytes:
      run-1: 9 raw files, 0 timeline entries                      RC=0

F7  a mention event with its receipt removed:
      run-1: 9 raw files, 1 timeline entries                      RC=0
      capture.json -> "mentions": {"owner": {"accepted": null, ...}}
```

Everything the verdict claims that this lane depends on is therefore reproduced, not adopted.

## DONE — one row per brief item, `file:line` by grep on the FINAL bytes

| brief item | where | what |
|---|---|---|
| **1. the list as FUNCTIONS** | `pins.py:265 required_files`, `:281 entry_allowlist`, `:291 corpus_version`, `:255 PINNED_SCAN_VERSIONS` | `required_files(version)` resolves `PINNED_LEG_FILES_SINCE` by version key and RAISES on a version it does not know; `entry_allowlist()` is `required \| optional \| PINNED_LEG_DIRS`; `corpus_version(leg_dir)` is the ONE detector, off `process-scan-after.txt`'s line 1. |
| 1. consumers of the functions | `build_capture_record.py:71,75`; `tests/test_s0_01_pc_tools.py:185` | the tool (build path) and the corpus tests call them. The test mirror `_required_for` at the old `:81-87` is **DELETED**; `_corpus_version()` (`tests/test_s0_01_pc_tools.py:58`) is now a fold of `pins.corpus_version` over the legs, not a second rule. |
| 1. red-before / green-after | pasted in PREMISE and GATES | `missing required leg files: tee-status.json` rc 1 -> `run-1: 9 raw files, 11 timeline entries` rc 0. |
| 1. the new corpus test | `tests/test_s0_01_pc_tools.py:435 test_build_capture_record_accepts_a_v2_2_corpus_leg` | copies `S0_01_REAL_LEG_DIR/run-1` to tmp_path, asserts `corpus_version == "v2.2"` and the exact stdout line. | — cited lines read: `def test_build_capture_record_accepts_a_v2_2_corpus_leg(tmp_path):`
| **2. the gate on the BUILD path only** | `build_capture_record.py:69 if not check_mode:` | `--check` keeps byte-identity as its only question; `:481 test_build_capture_record_check_mode_keeps_its_own_diagnosis` pins the diagnosis over a leg that is incomplete AND tampered. | — cited lines read: `if not check_mode:`
| 2. ONE shared fixture | `tests/conftest.py:25 synthetic_leg` | lifted from the old `tests/test_s0_01_pc_tools.py:285 _synthetic_leg`, reads `pins.required_files(pins.PINNED_SCAN_VERSIONS[-1])` and `PINNED_LEG_DIRS`; used by `tests/test_s0_01_pc_tools.py:386,398,418,451,463,481` and by `tests/test_s0_01_scripted_backend.py:894`. No hand list of names, no xfail, no copy. | — cited lines read: `"""Factory` / `if _PRODUCERS[rel] == "negative":` / `def test_build_capture_record_writes_the_record_for_a_complete_leg(tmp_path, synthetic_l` / `def test_build_capture_record_roundtrip_check(tmp_path, synthetic_leg):`
| **3. `is_pinned` narrowed** | `pins.py:317 is_pinned_argv` | `argv[0] == PINNED_BUZZ_ACP_EXE_REALPATH`, OR `basename(argv[0]).startswith("python")` AND `argv[1] in (PINNED_TEE_PATH, PINNED_AGENT_REALPATH)`. |
| 3. ONE function, three callers | `pc_post.sh:45` (the heredoc), `tests/test_s0_01_pc_post_scan.py:91 _is_pinned`, and A5k's checker | the producer's local `PINNED_BINARY`/`PINNED_SCRIPTS` copy is gone (`tests/test_s0_01_pc_tools.py:837` asserts `PINNED_SCRIPTS` no longer appears in `pc_post.sh`). | — cited lines read: `return pins.is_pinned_argv(cmd.split())` / `def _is_pinned(cmd: str) -> bool:` / `def test_the_scan_producer_and_its_test_shim_read_one_rule():`
| 3. still matches the real corpus | `tests/test_s0_01_pc_tools.py:826` | all 3 body rows of `golden/run-1/process-scan-after.txt` are `True`, asserted against the corpus. | — cited lines read: `def test_is_pinned_argv_matches_every_row_of_the_real_corpus_scan():`
| 3. red tests | `tests/test_s0_01_pc_tools.py:806` (9 rows) + the scan shim's new `/usr/bin/cat` row (pid 5007) | `/usr/bin/cat <tee>` NOT counted; `/usr/bin/python3 <tee>` counted; `<venv>/python3.13 <agent>` counted. | — cited lines read: `def test_is_pinned_argv_matches_the_entry_point_only(cmd, pinned, why):`
| 3. **F5 DECIDED: documented limit, not /proc** | `pins.py:334-343` (docstring) + `tests/test_s0_01_pc_tools.py:815` | see DECISIONS below. | — cited lines read: `it for the producer only: the checker computes this same predicate over a COLLECTED text` / `def test_is_pinned_argv_does_not_count_a_pinned_binary_reached_by_another_path():`
| **4. the producer parser** | tests/test_s0_01_pc_tools.py:100-106, `_PY_JOIN` / `_PY_PATH` / `_SH_FD` | `os.path.join(FD\|fd\|framedir, …)`, `Path(FD\|fd\|framedir, …)`, `d / "…"`, `f"{fd}/…"`, `$FD/…`, `"$FD"/…`, `"${FD}"/…`, `OUT=$FD/…`. |
| 4. the coverage pin | `tests/test_s0_01_pc_tools.py:270 _PRODUCER_NAME_FLOOR`, `:293 test_the_producer_parse_does_not_lose_coverage` | per-producer name count, as a FLOOR — see DISCREPANCIES D2 for why a floor and not an equality. | — cited lines read: `"proofs/S0-01/tools/pc/pc_launch.py": 17`
| 4. the parser's own vocabulary | `tests/test_s0_01_pc_tools.py:353 test_the_producer_parser_recognises_every_declared_idiom` | 11 rows, one per idiom — added after mutant P8 SURVIVED the floor (an idiom with no live producer site cannot be protected by a coverage floor). | — cited lines read: `def test_the_producer_parser_recognises_every_declared_idiom(tmp_path, source, expected)`
| **5. `transient` gone** | `pins.py:220,227` (both names now `excluded_on_collect`), `pins.py:170-176` (the vocabulary comment), `collect_leg.sh:19 --exclude='manifest-*.txt'` | `_STATUSES` (`tests/test_s0_01_pc_tools.py:42`) is three; `_EXCLUDE_DISPOSITION` (`:706`) gains `"manifest-*.txt": "dropped"`. |
| 5. the escape hatch removed | `tests/test_s0_01_pc_tools.py:797-802` | the old `\| transient` term at `:605` is gone; the real-tar test now asserts `got \| restored == pins.entry_allowlist()` and that `manifest-post.txt` / `manifest-pre.txt` are NOT unpacked. | — cited lines read: `(f"/home/rocco/s0-01-pinned/.venv-hermes/bin/python3.13 {pins.PINNED_AGENT_REALPATH}", T`
| **6. F6 empty timeline** | `build_capture_record.py:84`; test `tests/test_s0_01_pc_tools.py:451` | `stat().st_size == 0` -> rc 1 naming it. | — cited lines read: `def test_build_capture_record_fails_on_an_empty_timeline(tmp_path, synthetic_leg):`
| 6. F7 the receipt read | `build_capture_record.py:151,161`; test `tests/test_s0_01_pc_tools.py:463` | the FAILURE was picked, per the brief: `run-1: mention receipt absent: mentions/owner.receipt.json` rc 1, with the positive twin in the same test. | — cited lines read: `if rp.is_file():` / `def test_build_capture_record_fails_on_a_mention_with_no_receipt(tmp_path, synthetic_leg`
| 6. F7 the AP_SCREEN row | `.claude/hooks/edit-snapshot.py:123` (`else\b` added to AF-AP-40); tests `tests/test_edit_snapshot_ap_screen.py:177,182` | see DISCREPANCIES D1 for extend-vs-new-row. | — cited lines read: `def test_fires_on_exists_and_conjunct(self):`
| 6. F8 signal death | `pc_negative.py:42-49`; test `tests/test_s0_01_pc_tools.py:676` (4 rows incl. `os.kill(os.getpid(), 9)` -> `main() == 137`) | the branch prints its own reason rather than mapping silently. | — cited lines read: `# VERIFY-P5a F8: subprocess reports a signal death as -N, and` / `def test_pc_negative_propagates_the_probe_exit_code(tmp_path, monkeypatch, capsys, endin`
| 6. F9 shape ∈ {dir, fifo} | `tests/test_s0_01_pc_tools.py:418` | both shapes rejected by name; mutant V8 dies. |
| 6. F14 docstring | `pc_launch.py:93-97` | the empty-log case named as NOT the failure signature, with what the wait does instead. |
| **7. the S0-03 launcher seam** | `pins.py:348 hermes_home` (env `S0_01_HERMES_HOME`, exit 64 named); `pc_launch.py:36` resolves it ONCE; `:202 resolve_launch_profile`; `:267 --profile`; `:197 leg_framedir`; `:233 launch_env` | tests `tests/test_s0_01_pc_tools.py:850` (default path unchanged), `:887` (foreign leg + both refusals), `:905` (the launch env carries the profile home and the leg name), `:936` (override validated), `:950` (the override never moves the checker's pin). | — cited lines read: `def hermes_home():` / `HERMES_HOME = pins.hermes_home()` / `def test_the_s0_01_legs_keep_their_closed_set_without_a_profile():`
| 7. the CLI really reaches the validator | tests/test_s0_01_pc_tools.py `test_the_launcher_cli_really_reaches_the_leg_validator` (3 rows) | the closed sets used to be argparse `choices`; moving them into a helper is a fix only if argv still triggers them. Driven as a subprocess through the real entry point, asserting each refusal verbatim. Mutant P21 (the `choices` restored) dies. |
| **F11 (VERIFY-N5h)** — coordinator's added item | `.claude/hooks/edit-snapshot.py:186-190` | the AF-AP-57 alternation is now `(?:calls?\|call_count\|n_calls\|attempts?\|count)\s*(?:\[0\])?`; tests `tests/test_ap_screen.py:57` (end-to-end through `ap_screen.screen` on the hook's REAL row, red before the fix) and `tests/test_edit_snapshot_ap_screen.py:310`. | — cited lines read: `def test_fires_on_a_bracketed_call_count(self):`

## DECISIONS (the two the brief asked me to make and state)

**F5 — a pinned BINARY reached by another path: DOCUMENTED LIMIT, not a `/proc/<pid>/exe` resolution.**
`pins.py:334-343` carries the reason and `tests/test_s0_01_pc_tools.py:815` pins the behaviour so it is a
decision and not an accident. The reason is not cost, it is CORRECTNESS OF ONE PREDICATE ACROSS TWO VENUES:
`is_pinned_argv` is computed by the producer over a LIVE `ps` table and by the checker (A5k, `:1249-1253` and
the five substring siblings the verifier lists) over a COLLECTED text file, where no `/proc` exists. Resolving
argv[0] through `/proc/<pid>/exe` on the producer side only would give the two sides two different predicates
over one body — the exact drift this function was extracted to remove, and the shape that produced F17/F4 in
the first place. The escape is bounded elsewhere and that bound is real, not asserted: `pc_launch.py:72`
`alive_pinned_buzz` reads `/proc/<pid>/exe` (which resolves the realpath whatever the invocation) and refuses
to launch over a live pinned buzz-acp, so the escape also needs the pidfile gone. The residual — a foreign
buzz-acp started through a symlink while no pidfile exists is invisible to the evidence — is stated here and
in the docstring, NOT closed.

**The `S0_01_HERMES_HOME` override does NOT move `pins.PINNED_HERMES_HOME`.** O1's proposal
(`run_s0_03_legs.sh:123`) was literally `PINNED_HERMES_HOME = os.environ.get(...)`. Building that would have
opened a fail-open in the gate spine: `check_acp_conformance.py:468` and `negative_contract.py:210` compare a
CAPTURED leg's `env.json` against that constant, so anyone running the checker with the variable set would
make a leg captured under a foreign Hermes home pass its own oracle. The seam is therefore
`pins.hermes_home()` (`pins.py:348`), read ONCE by the launcher at `pc_launch.py:36` and threaded explicitly; — cited lines read: `def hermes_home():`
the constant is untouched. `tests/test_s0_01_pc_tools.py:950` is the negative control, and mutant P12 (O1's
literal line) is killed by it. `pc_negative.py:30` deliberately keeps `pins.PINNED_HERMES_HOME`: the negative
leg's env is graded against the constant by `negative_contract.py:210`.

## MUTANT TABLE (31 applied, 31 killed on the final bytes; killer line pasted from the run)

Applied to a `git archive d3a39d1` + final-bytes copy under the session scratchpad, restored BY COPY from a
pristine twin after each run. V1-V10 are the verifier's own, re-run against the final bytes — **all six of
her survivors now die**.

| # | mutant | file | verdict — killer line |
|---|---|---|---|
| V1 | PRODUCER-UNLISTED via lowercase `fd` | pc_launch.py | KILLED — `AssertionError: proofs/S0-01/tools/pc/pc_launch.py: writes names outside pins.PINNED_LEG_FILES: ['leak-report-v1.json']` |
| V2 | write via `"$FD"/name` | pc_post.sh | KILLED — `AssertionError: proofs/S0-01/tools/pc/pc_post.sh: writes names outside pins.PINNED_LEG_FILES: ['leak-report-v2.json']` |
| V3 | write via `Path(framedir, …)` | frame_tee.py | KILLED — `AssertionError: proofs/S0-01/tools/frame_tee.py: writes names outside pins.PINNED_LEG_FILES: ['tee-heartbeat-v3.json']` |
| V4 | write via `"${FD}"/name` | pc_mention.sh | KILLED — `AssertionError: proofs/S0-01/tools/pc/pc_mention.sh: writes names outside pins.PINNED_LEG_FILES: ['mention-audit-v4.json']` |
| V5 | TABLE-ROWS-LITERAL `table_rows=99` | pc_post.sh | KILLED — `AssertionError: assert '99' == '8'` |
| V6 | COUNTERS-SWAPPED (`rows`↔`table_rows`) | pc_post.sh | KILLED — `AssertionError: header rows=103 but the body carries 3 rows` |
| V7 | NEG-RC-CLAMPED (the signal branch off) | pc_negative.py | KILLED — `assert -9 == 137` |
| V8 | EXISTS-NOT-ISFILE | build_capture_record.py | KILLED — `AssertionError: (0, 'run-1: 9 raw files, 1 timeline entries` |
| V9 | ARGV1-ARM-DROPPED | pins.py | KILLED — `AssertionError: an interpreter running the pinned tee` |
| V10 | SINCE-EMPTIED | pins.py | KILLED — `AssertionError: corpus version v2.2: required names absent: {'run-1': ['tee-status.json'], …}` |
| P1 | SINCE-IGNORED-IN-TOOL (the F2 defect restored) | build_capture_record.py | KILLED — `AssertionError: (1, '', 'run-1: missing required leg files: tee-status.json` |
| P2 | CHECK-MODE-GATED (the F1/F16 defect restored) | build_capture_record.py | KILLED — `AssertionError: assert 'run-1: missi...ned-pids.json' == 'run-1: captu...ent (--check)'` |
| P3 | EMPTY-TIMELINE-OK | build_capture_record.py | KILLED — `AssertionError: (0, 'run-1: 9 raw files, 0 timeline entries` |
| P4 | RECEIPT-SILENT (the F7 ternary restored) | build_capture_record.py | KILLED — `AssertionError: (0, 'run-1: 9 raw files, 1 timeline entries` |
| P5 | PYTHON-ARM-WIDE (the F4 defect restored) | pins.py | KILLED — `AssertionError: F4: a bystander whose FIRST OPERAND is a pinned script` |
| P6 | BINARY-ARM-BY-BASENAME (widening past the F5 limit) | pins.py | KILLED — `AssertionError: assert True is False` |
| P7 | COVERAGE-BLIND-`fd` (the F3 idiom removed again) | test_s0_01_pc_tools.py | KILLED — `AssertionError: proofs/S0-01/tools/pc/pc_launch.py: the parse resolves 16 framedir names, below the pinned floor 17 — a write is hidden from the subset gate` |
| P8 | PATH-IDIOM-DROPPED | test_s0_01_pc_tools.py | **SURVIVED first (84 passed)**, then KILLED — `AssertionError: assert set() == {'d.json'}` (see below) |
| P9 | EXCLUDE-DROPPED (`manifest-*.txt`) | collect_leg.sh | KILLED — `AssertionError: ['manifest-*.txt']` |
| P10 | TRANSIENT-BACK | pins.py | KILLED — `AssertionError: ['excluded_on_collect', 'optional', 'required', 'transient']` |
| P11 | CORPUS-VERSION-DEFAULTS (raise -> v2.2) | pins.py | KILLED — `Failed: DID NOT RAISE ValueError` |
| P12 | OVERRIDE-MOVES-THE-PIN (O1's literal proposal) | pins.py | KILLED — `AssertionError: assert '/tmp/claude-...never_moves_0' == '/home/rocco/.../.hermes-home'` |
| P13 | OVERRIDE-UNVALIDATED | pins.py | KILLED — `AssertionError: ('/tmp/.../does-not-exist', …)` (rc 0 where 64 is required) |
| P14 | FOREIGN-LEG-WITHOUT-PROFILE | pc_launch.py | KILLED — `KeyError: 's0-03-hermes'` |
| P15 | S0-01-LEG-TAKES-A-FOREIGN-PROFILE | pc_launch.py | KILLED — `Failed: DID NOT RAISE SystemExit` |
| P16 | FIXTURE-INCOMPLETE (the shared leg drops one required name) | tests/conftest.py | KILLED — `AssertionError: build failed: test-leg: missing required leg files: owned-pids.json` (in `test_s0_01_scripted_backend.py`, i.e. the fixture really is load-bearing for the OTHER file) |
| P17 | ALLOWLIST-ADMITS-EXCLUDED | pins.py | KILLED — `AssertionError: assert frozenset({'a...cp.log', …}) == {'argv.txt', …}` |
| P18 | AP57-NARROW-AGAIN (VERIFY-N5h F11 regressed) | edit-snapshot.py | KILLED — `AssertionError: assert 0 == 1` |
| P19 | AP40-TERNARY-BLIND-AGAIN (VERIFY-P5a F7 screen regressed) | edit-snapshot.py | KILLED — `AssertionError: assert None` |
| P21 | CLI-CHOICES-BACK (argparse `choices` restored on `--leg`) | pc_launch.py | KILLED — `AssertionError: (2, '', "usage: pc_launch.py [-h] --leg {run-1,run-2,cancel,shutdown,two-users} --model` |
| P20 | QUOTED-SHELL-IDIOM-DROPPED (`"$FD"/`) | test_s0_01_pc_tools.py | KILLED — `AssertionError: assert set() == {'i.json'}` |

**P8 is the one that found a hole in my own work, and it is worth the paragraph.** Removing the
`Path(FD|fd|framedir, …)` row from the parser left all 84 tests green: the coverage FLOOR can only protect an
idiom that a producer uses TODAY, and no current producer uses that one — so the idiom was an
emitted-but-unreachable check, the exact shape the build loop forbids. The repair is
`test_the_producer_parser_recognises_every_declared_idiom` (`tests/test_s0_01_pc_tools.py:353`), 11 rows, one
per idiom, each asserting the EXACT resolved set. P8 and P20 are the re-runs after it landed.

## ANTI-PATTERN SCREEN — every hit classified BY RUNNING it

`scripts/ap_screen.py --tests tests/test_s0_01_pc_tools.py tests/test_s0_01_pc_post_scan.py tests/conftest.py`
-> `TEST_SCREEN over 3 path(s): 0 hits over 3 files`.

`scripts/ap_screen.py proofs/S0-01/tools/pc proofs/S0-01/tools/build_capture_record.py proofs/S0-01/pins.py`
-> `AP_SCREEN over 3 path(s): 24 hits over 4 files` (P5a's line was 21; the three new ones are mine and are the
first three rows below).

| class | hits | classification |
|---|---|---|
| **AP-1** | 1 — `pins.py:361` `override = os.environ.get("S0_01_HERMES_HOME")` | **Reviewed-safe, and the remedy the row names is what the code does.** The value is resolved ONCE, at `pc_launch.py:36`, into a module constant threaded explicitly into `resolve_launch_profile` / `launch_env`; nothing deeper re-reads the environment. The dangerous half — an env var moving a value the CHECKER compares against — is structurally excluded and pinned by `tests/test_s0_01_pc_tools.py:950`, and mutant P12 (the version that does move it) is killed by that test. | — cited lines read: `HERMES_HOME = pins.hermes_home()` / `def test_the_override_never_moves_the_pin_the_checker_compares_against(tmp_path):`
| **AF-AP-40** | 12 (was 10) — `build_capture_record.py:92,116,121,127,134,138,145,151,168,174,179,188` | **Ten dominated, one is my own comment, one is the F7 repair.** `:138` is the comment quoting the defective ternary (the screen cannot tell code from prose). `:151` `if rp.is_file():` is the repair: its `else` arm appends to `no_receipt`, and `:161` fails the build naming the file — proven by running (`run-1: mention receipt absent: mentions/owner.receipt.json` rc 1, and mutant P4 dies). The other ten are dominated **on the build path** by the required gate (the verifier re-derived that 13/13 by dropping each name) and **on the `--check` path** by byte identity, which I verified by running rather than assuming — dropping each of the six files the record reads, over a real corpus leg with a committed record: 6/6 `run-1: capture.json differs from re-derived content (--check)` rc 1. Moving the completeness gate off `--check` therefore did NOT un-dominate them. | — cited lines read: `if tl_path.exists():`
| **AP-32** | 6 (unchanged) — `pc_launch.py:50,191`; `build_capture_record.py:23,24,28,45` | Unchanged from P5a's classification; my edits moved `:181->:191` without changing the hashed form. | — cited lines read: `h = hashlib.sha256()` / `def _sha256(data: bytes) -> str:`
| AF-AP-45 | 2 — `pc_launch.py:153,156` | P5a's classification stands (a MEMBERSHIP set, with the STATE column classified in the consumer at `pc_post.sh:58-61`). Not touched by this lane. | — cited lines read: `detach shares that session. Walking the FULL` / `if parts[3].startswith("Z"):`
| AF-AP-55 | 2 — `pc_launch.py:73,144` | P5a's classification stands (single-stage native binary, exe sha pinned). Not touched. |
| AF-AP-41 | 1 — `build_capture_record.py:129` | Pre-existing, untouched, non-load-bearing (the checker pins the startup line itself). |

Other mechanical gates: `pyflakes` over the eleven `.py` files touched -> rc 0, no output. `bash -n` ->
`OK proofs/S0-01/tools/pc/pc_post.sh`, `OK proofs/S0-01/tools/pc/collect_leg.sh`.
`python scripts/lint_delta.py --base d3a39d1` ->
`lint_delta (worktree vs d3a39d18d3f29f315f1a26381574ec904ed410a9): 24 .py changed, 0 NEW pyflakes hit(s), 0 removed`
(the 24 counts other live lanes' untracked S0-02/S0-06 files in the same worktree; the four advisory TELLs on
MY added lines are AP-1, AF-AP-40, AP-32, AF-AP-45 — all four classified in the table above).

## 18-CLASS SELF-SWEEP over the final bytes

Static scan over the nine scope files (`pins.py`, `build_capture_record.py`, `pc_launch.py`, `pc_negative.py`,
`pc_post.sh`, `collect_leg.sh`, `conftest.py`, the two test files). "The run" is the run that decided the
verdict, not a citation.

| class | sample on the final bytes | verdict | the run |
|---|---|---|---|
| C1 presence-gated checks | `build_capture_record.py:92,116,121,127,134,145,151,168,174,179,188` | SAFE — dominated on the build path by `:75-80` and on `--check` by byte identity, both measured | 13/13 drop -> `rc 1` naming the entry (verifier, re-derived); 6/6 drop under `--check` -> `differs from re-derived content` (this lane) | — cited lines read: `if tl_path.exists():`
| C2 reads outside walk / no S_ISREG | `build_capture_record.py:75 is_file()`, `:147,169 glob()`; `tests/…pc_tools.py:428 os.mkfifo` | SAFE — the gate is `is_file()`/`is_dir()`, and BOTH non-regular shapes are now planted controls | `test_build_capture_record_requires_a_regular_file_not_just_an_entry[dir/fifo]`; mutant V8 dies |
| C3 stale `[-1]` over produced records | `pc_launch.py:118 lines[-1] if lines else`, `:351 argv[-1]`; `conftest.py:54 PINNED_SCAN_VERSIONS[-1]` | SAFE — `:118` is #48's guarded form; `:351` is the trailing-empty strip; `conftest.py:54` indexes a 2-tuple pin, not a produced record | `test_pc_launch_survives_an_empty_pre_manifest_summary`; full gate |
| C4 negative acceptance assertions | 14 in `test_s0_01_pc_tools.py`, 5 in `test_s0_01_pc_post_scan.py` | SAFE — every `assert not` / `is False` is a NAMED negative twin of a positive in the same test (`is_pinned_argv` rows carry a `why` string that appears in the failure) | mutants P5, P6, P15 die naming the exact row |
| C5 substring/tail anchors classifying an outcome | `pins.py:309 first.startswith("#")`, `:345 basename().startswith("python")` | SAFE — `:309` is deliberate (a `#` line CLAIMS to be a header and must then parse or raise); `:345` is the interpreter test, and the whole point is that the PATH comparison stays exact equality | `test_the_one_corpus_version_detector_refuses_to_default` (4 rows); `test_is_pinned_argv_matches_the_entry_point_only` (9 rows) | — cited lines read: `if not first.startswith("#"):` / `if not first.startswith("#")`
| C6 env-domain fail-opens | `pins.py:361` (the only production env read added) | SAFE — validated, exit 64 on a non-directory, and structurally unable to move the checker's pin | `test_the_hermes_home_override_is_validated`; `test_the_override_never_moves_the_pin_the_checker_compares_against`; mutants P12, P13 die | — cited lines read: `override = os.environ.get("S0_01_HERMES_HOME")`
| C7 lossy decodes on a decision path | `pins.py:307 errors="replace"` (new); `pc_launch.py:80,104,117,188,193` (pre-existing) | SAFE — `pins.py:307` reads only line 1 of the scan and the decision is `startswith("#")` plus a `v\d+\.\d+` match, neither reachable through a replacement char; the `pc_launch` ones are P5a's, unchanged, and `:188-193` is the #25 fix whose fingerprints are taken on RAW bytes | `test_env_redaction_fingerprints_the_raw_bytes`; full gate |
| C8 broad catches | build_capture_record.py:72 `except ValueError as exc:`, `pc_launch.py:70,74,145`, `:309 except Exception` | SAFE — `:72` catches only `corpus_version`'s own ValueError and re-prints it as a named failure; `:309` is P5a's pre-existing backend probe, unchanged | `test_the_one_corpus_version_detector_refuses_to_default` reaches `:72` through the tool (rc 1, message preserved) | — cited lines read: `except ValueError as exc:` / `except (OSError, ValueError):`
| C9 waits/polls + ORDINAL gates | `pc_launch.py:100,107,129,132` (`range(tries)` + `time.sleep`) | SAFE — bounded, failure-aware (`:101-106` is the #32 signature), and NO fake in this lane selects behaviour by call ordinal | `test_pre_manifest_wait_breaks_on_a_manifest_error` (`_NoSleep.slept < 1.0`); `ap_screen --tests` AF-AP-57 = 0 hits over my three test files, with the row WIDENED by this lane |
| C10 skips/xfails that cannot fire | `tests/test_s0_01_pc_tools.py:52` — the corpus skip | SAFE and DECLARED — venue-gated by design (`S0_01_REAL_LEG_DIR` unset in CI); absent-when-declared is `pytest.fail`, not skip (`:53-54`). No xfail anywhere; the brief forbade one and none was added | the whole corpus set runs green under `S0_01_VENUE=sandbox` (447 passed) |
| C11 world-scoped enumerations | `pc_post.sh:51` (`ps -eww`, the producer, by design) | SAFE — the producer is world-scoped on purpose and `_split_world` characterises every foreign row; the F4 narrowing REDUCES what the world can put in the body, which is the direction that helps | `test_pinned_present_is_exact_over_a_synthetic_table` (8-row shim, exact counters); `test_split_world_rejects_an_unexplained_foreign_row` | — cited lines read: `for line in subprocess.run(["ps", "-eww", "-o", "pid,ppid,etimes,stat,args", "--no-heade`
| C12 signal installs before try | EMPTY — no `signal.signal` / `SIGALRM` / `alarm(` in any scope file | EMPTY | static scan 0 |
| C13 `/proc/<pid>/exe` races | `pc_launch.py:73,144` (pre-existing) | SAFE — P5a's classification, untouched; and this lane's F5 DECISION is precisely not to add a new `/proc` read (see DECISIONS) | `test_pc_launch_names_a_buzz_exit_during_identity_capture`; `test_pc_launch_captures_the_identity_of_a_live_process` |
| C14 mirrors of code under test | `tests/test_s0_01_pc_post_scan.py:92 _is_pinned`; `tests/test_s0_01_pc_tools.py:58 _corpus_version` | **FIXED this lane** — both were mirrors and both now CALL the production function (`pins.is_pinned_argv`, `pins.corpus_version`); `test_the_scan_producer_and_its_test_shim_read_one_rule` asserts no copy has come back | mutants V9, P5, P11 die; `assert "PINNED_SCRIPTS" not in post` | — cited lines read: `def _corpus_version():`
| C15 two counters over different populations | `pc_post.sh:91,94` (`rows` vs `table_rows`) | SAFE — P5a's #5 fix, unchanged by this lane except that the shim table grew a row; `_parse` still checks the header's own counter against its own body on EVERY caller | mutants V5, V6 die (`assert '99' == '8'`, `header rows=103 but the body carries 3 rows`) |
| C16 redundant/dead guards | `pyflakes` over the eleven `.py` files | SAFE — rc 0, no output; the one alias I introduced mid-build (`cfg = cfg_path`) was removed in the same increment | pyflakes rc 0; `lint_delta … 0 NEW pyflakes hit(s)` |
| C17 hardlink-clobbering writes | `build_capture_record.py:205 out.write_text`; `pc_launch.py:301,302,336…` | SAFE — every write is into a framedir the launcher itself created with `os.makedirs` after `shutil.rmtree`; no `os.link`/`os.symlink` anywhere in scope | static scan 0 link calls; full gate | — cited lines read: `out.write_text(new_text)` / `open(os.path.join(FD, "hermes-model.txt"), "w").write(default_lines[0] + "\n")`
| C18 other families | subprocess timeouts: 6 in `test_s0_01_pc_tools.py`, 8 in `test_s0_01_pc_post_scan.py` | SAFE — every subprocess in this lane's tests carries an explicit `timeout=`; the FIFO control at `:428` is the one that would hang without the `is_file()` gate, and it returns rc 1 in <1 s | `test_build_capture_record_requires_a_regular_file_not_just_an_entry[fifo]` |

## GATES (pasted verbatim)

`report_lint` summary on this report, run last, against the FINAL frozen bytes:
`report_lint: 98 refs — OK 81, NEAR 0, MISS 0, UNCHECKABLE 17, UNRESOLVED 0`.


All from a `git archive d3a39d1` copy + exactly the thirteen working-tree files, under
`…/scratchpad/p5b/`. The 13 sha256 in the gate's own identity table equal the FILE IDENTITY table above, and
the frozen copy was re-verified byte-for-byte against the working tree after the run (13/13 SAME).

**The four-file set the brief names, twice (`scripts/lane_gate.sh -n 2`):**

```
RESULT: rev=d3a39d18d3f2 files=13 runs=2 identical=yes rc=1 summary="2 failed, 451 passed in 104.45s (0:01:44) 2 failed, 451 passed in 104.05s (0:01:44)"
```

The two failures are `tests/test_s0_01_audit_cp5_controls.py` and nothing else, both times: they are A5k's
sequencing dependency (see NOT_DONE 2) and they were already the state of the tree before this lane. The
three files that are mine are green:

```
=== THREE-FILE GREEN SET, run 1 ===
447 passed in 102.73s (0:01:42)
pytest-exit: 0
=== THREE-FILE GREEN SET, run 2 ===
447 passed in 102.61s (0:01:42)
pytest-exit: 0
```
(This three-file pair was measured on the bytes BEFORE the last increment — the three
`test_the_launcher_cli_really_reaches_the_leg_validator` rows — landed, so its `447` is one increment behind.
The four-file RESULT line above is the run on the FINAL bytes and reconciles exactly: 447 (my three files) + 1
(the audit file's one passing test, its other two being the A5k reds) + 3 (the new CLI rows) = **451 passed,
2 failed**. The frozen copy that RESULT was taken from was re-verified against the working tree afterwards:
**13/13 SAME**.)

**The six-file adjacent set VERIFY-P5a ran, once, same static copy:**

```
=== SIX-FILE ADJACENT SET ===
2 failed, 642 passed in 318.63s (0:05:18)
pytest-exit: 1
   (files: frame_tee, acp_probe, negative_contract, check_initialize, audit_cp5, scripted_backend)
```

VERIFY-P5a measured `3 failed, 599 passed` on P5a's bytes against `602 passed` on the parent. The third red —
`test_s0_01_scripted_backend.py::test_build_capture_record_roundtrip_check`, F1 — is gone; the two that remain
are the A5k pair. Wall times are not comparable between these runs: another verify lane was running its own
pytest set on the same box throughout (`…/scratchpad/vb14/`), so the box was contended.

**Mechanical gates:** `pyflakes` over the eleven `.py` files -> rc 0, no output. `bash -n` ->
`OK proofs/S0-01/tools/pc/pc_post.sh`, `OK proofs/S0-01/tools/pc/collect_leg.sh`.
`scripts/lint_delta.py --base d3a39d1` -> `24 .py changed, 0 NEW pyflakes hit(s), 0 removed`.

**`report_lint.py` on THIS report:**

```
report_lint: 98 refs — OK 81, NEAR 0, MISS 0, UNCHECKABLE 17, UNRESOLVED 0 (worktree)
```

**MISS 0, NEAR 0** — the brief's bar. On the mode, because VERIFY-P5a F13 was exactly this: the run is
`--root <the frozen gate copy>` and NOT `--rev d3a39d1`, because at that rev my symbols do not exist (the
lane's bytes are uncommitted and I may not commit in a shared tree). `--root` gives the same property `--rev`
gives — a fixed tree that cannot move under the linter — and the copy is proven byte-identical to the working
tree for all 13 files. Running `--rev d3a39d1` instead would resolve every reference against P5a's bytes and
report a MISS for every symbol this lane added; that number would say nothing about this report. The 17
UNCHECKABLE rows are report lines whose reference carries no backticked claim token for the linter to test
(each is named in full elsewhere in the report).

**Process census.** `ps -eww -o pid,ppid,etimes,args` filtered on this lane's own spawn signatures
(`scratchpad/p5b`, `bt-m`, `leak-report`, `time.sleep(120)`): **0 rows**, with 101 processes on the box.
Every process this lane started ended in its own `finally`/`kill`, by pid; no `pkill`/`pgrep -f` was used.

**SHARED-TREE HYGIENE.** No `git stash/checkout/restore/reset/add/commit/push` was run, and nothing outside
the scope was written. `git status --porcelain` at the end carries my 13 files plus other live lanes' work
that appeared DURING this lane and is not mine: `proofs/S0-01/tools/acp_probe.py` (M),
`proofs/S0-08/{canaries/P1.sh,canaries/P2.sh,canaries/P4.sh,check_containment.py,spec.json,tools/pc/run_containment.sh}`
(M), and an untracked `userpid.txt` at the repo root (created 04:08, contains a bare pid — not written by this
lane; left alone). Because `acp_probe.py` moved under me I re-ran the producer/parser tests against the LIVE
working tree, not only against my frozen copy: `28 passed, 70 deselected in 0.09s` — the floor for that file
is a floor precisely so another lane's landing does not turn red in my file. Every mutant and every
reproduction ran on copies under `…/scratchpad/p5b/`; every pytest run I invoked directly carried an explicit
`--basetemp` there (see DISCREPANCIES D7 for `test_summary.sh`). No worktree was created, no PC bridge call
was made, no outward-facing action was taken, and no credential was read or printed (the two `…=fixture-value-not-a-key`
strings in `test_the_launch_env_carries_the_profile_home_and_the_leg_name` are test fixtures written by the
test itself).

## THE EXACT ARGV FOR THE S0-03 RUNNER (O1's blocker; I did NOT edit `proofs/S0-03/*`)

`run_s0_03_legs.sh` currently refuses at `:125-134` (exit 5) unless `S0_03_HERMES_CONFIG` names a launcher
that accepts a profile path. With this lane's seam it can invoke S0-01's launcher directly. The invocation:

```sh
S0_01_HERMES_HOME=/home/rocco/s0-03-pinned/.hermes-home \
setsid /usr/bin/python3 /home/rocco/agent-factory/proofs/S0-01/tools/pc/pc_launch.py \
    --leg s0-03-hermes \
    --model agentfactory-build \
    --profile /home/rocco/agent-factory/proofs/S0-03/hermes/config.yaml \
    </dev/null > /home/rocco/s0-03-pinned/.markers/v2-s0-03-hermes.launch.log 2>&1 &
```

What each part is doing, and what the S0-03 lane must know:

1. **`S0_01_HERMES_HOME` moves the TREE, `--profile` names the CONFIG.** `pc_launch.py:37` — cited lines read: `BASE = os.path.dirname(HERMES_HOME)                      # /home/rocco/s0-01-pinned`
   `BASE = os.path.dirname(HERMES_HOME)`, so the override also moves `.markers` (the framedir, the pidfile,
   `current-framedir`) and `.secrets` (from which `launch_env` reads `agent.env` and `owner.pub`). The S0-03
   tree must therefore provide `<S0_01_HERMES_HOME>/../.secrets/agent.env` (a `BUZZ_PRIVATE_KEY=` line) and
   `owner.pub`, or `read_kv` exits with `pc_launch: BUZZ_PRIVATE_KEY not found in <path>`. Without the
   override the launch would write into S0-01's pinned markers dir — the thing O1 rightly refused to do.
2. **`--leg` may be any name that is NOT one of `pins.LEGS`**, and only with `--profile`; the framedir is
   `<markers>/v2-<leg>` (`pc_launch.py:197`). `--model` is unconstrained for a foreign leg (no — cited lines read: `def leg_framedir(markers, leg):`
   `EXPECTED_MODEL` pin exists for it) and lands in the launch's `hermes-model.txt`.
3. **The config is NOT rewritten** for a foreign profile: the model-route substitution at
   `pc_launch.py:293-294` is anchored on `s0-01-scripted/s0-01-\w+`, so `s2 == s` and the guarded write at
   `:295-296` does not fire. The S0-03 profile's own `default:` line must therefore already name the route it
   wants; `pc_launch.py:298-300` still requires a `default:` line and exits named if there is none.
4. **`S0_01_FRAMEDIR` and `S0_01_AGENT` are still set in the launch env** (`pins.PINNED_ENV_KEYS` is the pinned
   key set and the seam does not change it) — `S0_01_AGENT` is `pins.PINNED_AGENT_REALPATH`, i.e. S0-01's
   pinned hermes-acp. If S0-03's leg B needs a different agent binary, that is a SECOND seam this lane did not
   build; say so rather than pointing `--profile` at it and hoping.
5. `run_s0_03_legs.sh`'s own `capture_hermes_leg` invokes `python3 "$S0_03_HERMES_CONFIG" --config … --prompt …`
   — a different CLI shape (`--config`/`--prompt`). Adapting that call site is O1's edit, not mine.

## DISCREPANCIES — where I departed from the brief or the verdict, and why

**D1 — the AF-AP-40 signature was EXTENDED by one alternative, not added as a second row.** The brief says
"ONE new AP_SCREEN row for the AF-AP-40 ternary form". `tests/test_edit_snapshot_ap_screen.py:19` builds
`_AP_BY_ID = {row[0]: row[1] for row in AP_SCREEN}` — a dict keyed by class id — so two rows both called
"AF-AP-40" would leave one of them with no test at all, which is the opposite of what the item is for. The
class is the same (a presence gate that makes a required artifact optional), only the syntax differs, so the
change is `\s*(?::|and\b)` -> `\s*(?::|and\b|else\b)`: one token, one row, one id, tested both ways
(`:177` fires on the ternary, `:182` does not fire on an unrelated `if … else`). Mutant P19 restores the old
alternation and dies.

**D2 — the per-producer NAME COUNT is pinned as a FLOOR (`>=`), not an equality.** The brief's parenthetical
states the intent — "a refactor that hides a write fails loudly" — and shrinkage is the defect direction that
actually happened (18 -> 16 in F3, silently). A floor fails on exactly that. Equality adds no detection power
(a name a producer STARTS writing is already caught by the subset direction and the orphan direction) and adds
a false-red surface: another lane's legitimate new write would go red in MY file instead of theirs.
`tests/test_s0_01_pc_tools.py:263-269` carries this reasoning in the code.

**D3 — the env override does not move `pins.PINNED_HERMES_HOME`.** The brief says "the PIN's `pins.py` line 18 (`PINNED_HERMES_HOME`)
gets an env override"; O1's proposal was the literal `PINNED_HERMES_HOME = os.environ.get(...)` at that line. Built as
written, that adds a fail-open to the checker spine (`check_acp_conformance.py:468`,
`negative_contract.py:210` compare a captured leg's `env.json` against that constant). The seam is delivered — — cited lines read: `for key, pin in (("HERMES_HOME", pins.PINNED_HERMES_HOME), ("PYTHONDONTWRITEBYTECODE", "`
`pc_launch` runs against any declared Hermes home — with the constant left immutable. Full reasoning in
DECISIONS; the negative control is `tests/test_s0_01_pc_tools.py:950` and mutant P12. — cited lines read: `def test_the_override_never_moves_the_pin_the_checker_compares_against(tmp_path):`

**D4 — `--model` had to open for a foreign leg too; the brief pinned only `--leg`.** Not a widening for its
own sake: `pc_launch.py:199` (old numbering) indexes `pins.EXPECTED_MODEL[args.leg]`, which raises a bare — cited lines read: `return os.path.join(markers, f"v2-{leg}")`
`KeyError` for a foreign leg, and argparse `choices` on `--model` rejected every non-S0-01 route before
`main()` ran. Leaving either in place would have made the `--profile` seam an emitted-but-unreachable check.
S0-01's own legs keep BOTH constraints (`resolve_launch_profile:220-224`), pinned by
`test_the_s0_01_legs_keep_their_closed_set_without_a_profile`.

**D5 — my per-producer count for `pc_launch.py` is 17, not the verdict's 18.** VERIFY-P5a F3 measured the
PIN's parser at 16 names over the PIN's `pc_launch.py` and 18 over the PARENT's. Neither number is what the
final bytes give: the parser's idiom set is wider now and the file has been refactored again (the env dict
moved into `launch_env`). The floor is pinned at the MEASURED 17, not at the verdict's 18 — a floor copied
from a report rather than from a run would have been red on arrival.

**D6 — `_corpus_version()` no longer folds a `tee-status.json` presence check into the version answer, and
that is a deliberate behaviour change the checker suite has not made.** The old mirror
(`tests/test_s0_01_pc_tools.py:58-77` at the PIN, itself copied from
`tests/test_s0_01_check_acp_conformance.py`'s `_corpus_version`) answered "v2.2" for a leg that carried a v2.4
header but no `tee-status.json` — i.e. a leg missing a name its own contract requires was silently graded by
the older, weaker set and PASSED. `pins.corpus_version` reads the header and only the header, so such a leg is
graded v2.4 and fails on the missing name. **This is louder, and A5k's suite still has the old fold** — when
the checker adopts `pins.corpus_version` (A5k list item 7) it inherits the stricter answer. Flagged, not
changed: `tests/test_s0_01_check_acp_conformance.py` is not mine.

**D7 — the `--basetemp` rule and `scripts/test_summary.sh`.** Every pytest run I invoked directly carries
`--basetemp` under `…/scratchpad/p5b/`. `scripts/test_summary.sh:19` hard-codes — cited lines read: `output=$(python3 -m pytest "${paths[@]}" -q -rs -p no:cacheprovider 2>&1)`
`python3 -m pytest "${paths[@]}" -q -rs -p no:cacheprovider` and accepts no basetemp, so the gate runs (which
the brief requires to be `test_summary.sh` invocations) land in pytest's own `/tmp/pytest-of-root/pytest-N`
(268 MB at the end of this lane, self-rotating at 3 runs). Stating the deviation rather than editing a script
outside my scope or paraphrasing the brief's gate command.

**D8 — the widened AF-AP-57 row surfaces one previously-invisible ordinal gate OUTSIDE my scope.**
Measured over `tests/test_s0_01_*.py` + `tests/red/test_s0_01_*.py`: old pattern **1** hit, widened pattern
**2** — the new one is `tests/test_s0_01_check_acp_conformance.py:4493: if call_count[0] == 2:`. Reported,
not touched (another lane owns that file). The coordinator's own figure (1 reported vs 5 by grep across four
fakes) was measured on the probe test's parent, a different file set; both numbers are true of their own set.

**D9 — I did not take VERIFY-P5a F5's suggested `/proc/<pid>/exe` option**, and the verdict did not weigh the
reason: the checker computes this same predicate over a COLLECTED text file, where `/proc` does not exist. See
DECISIONS. The verdict's other suggested minimal fixes (F1/F2/F3/F4/F6/F7/F8/F9/F10/F16) were all taken.

## NOT_DONE (first-class)

1. **NOT run on the PC — no bridge use in this lane, by the brief.** Every PC-only path is still driven only
   through a monkeypatched primitive or a `ps` shim and has NEVER executed end to end on the PC. That now
   includes the whole S0-03 seam: `resolve_launch_profile`, `launch_env` and the `S0_01_HERMES_HOME` override
   are unit-proven in the sandbox, and `pc_launch.main()` has never run against a real Hermes home of any kind.
   The argv in the section above is derived from the code, not from a launch.
2. **`tests/test_s0_01_audit_cp5_controls.py` is still 2-of-3 RED, and that is A5k's sequencing, not a
   regression I introduced.** Final gate run: `2 failed, 451 passed` twice, identical; the two are
   `test_clean_shutdown_empty_after_scan_passes` (the test FILE's own `# process-scan v2.3 mode=after `
   literal at `:110` — VERIFY-P5a F11) and `test_shutdown_owned_survivor_is_named_whatever_its_command` (the
   checker's `_parse_scan_v23` rejecting a v2.4 header). Neither is touchable from my boundary. With that file
   excluded the same static copy is green: `447 passed` twice on the previous increment's bytes, and the 451
   of the final run minus the audit file's one passing test = 450 of my own, all green.
3. **The checker's consumer side is untouched, by the brief.** `pins.required_files` / `entry_allowlist` /
   `corpus_version` / `is_pinned_argv` exist and are tested, but `check_acp_conformance.py` does not call them
   yet — that is A5k/A5l (verifier list items 1-11). Until it does, the ONE list has one consumer, not two,
   and the drift the list exists to end is only half closed.
4. **`docs/INCIDENT-LOG.md` was NOT edited — a registry row is owed and I could not write it.** The build
   loop requires the anti-pattern registry to learn any real defect an increment FOUND. This lane found one in
   its own work: **mutant P8 — an idiom listed in a producer-parser with no live producer site is protected by
   nothing, because a per-producer coverage FLOOR only covers idioms in current use, and a SUBSET gate gets
   greener the less the parser resolves.** The repair pattern (one committed row per declared idiom, asserting
   the exact resolved set) is at `tests/test_s0_01_pc_tools.py:353`. The log is outside my scope; the
   coordinator should register the class and, if it gets a mechanical signature, extend AP_SCREEN in the same
   increment.
5. **Not attempted:** `tests/test_s0_01_check_acp_conformance.py` (~17 min, and it is A5k's file), the full
   `tests/` tree in one run, the PC `-n 8` gate, and any real capture. The six-file adjacent set and the
   four-file static gate, pasted verbatim in GATES above, are what stands in their place.
6. **`--check` mode's behaviour on a leg whose receipt is absent is deliberately unchanged** — it still
   derives `"accepted": null` and compares bytes. A leg like that cannot be produced by the build path any
   more, so the case is unreachable through the pipeline; if a hand-built record ever carries it, `--check`
   answers "differs", not "receipt absent". Stated because it is a real asymmetry between the two modes.

## SELF-ATTACK — the three likeliest ways this is wrong

**A1 — "moving the completeness gate off `--check` un-dominates eleven AF-AP-40 presence gates in that mode."**
This is the sharpest objection, because the domination argument P5a's report made is what justifies all ten
pre-existing hits, and I narrowed the dominator. I did not answer it by reasoning: I ran it. Over a real
corpus leg with a committed `capture.json`, deleting each of the six files the record actually reads gives
`run-1: capture.json differs from re-derived content (--check)` rc 1, 6/6 — the check-mode dominator is
byte-identity of the whole record, which is strictly stronger than presence, because the committed record can
only have been produced by the build path, which does require presence. The residual: a record hand-written to
match an incomplete leg would round-trip. That needs someone to forge the record the checker already does not
trust (`build_capture_record.py:2`).

**A2 — "`is_pinned_argv`'s interpreter arm is a `startswith`, i.e. the substring rule came back."** It is a
`startswith` on `os.path.basename(argv[0])`, not on the command line, and it is an AND with an exact path
equality on `argv[1]`. So the widest thing it admits is a process whose executable is named `python*` running
one of two absolute pinned paths. The rows that made F4 a real defect (`cat`, `vim`, `sha256sum`, `less`) all
fail it, tested; the decoy that only MENTIONS a path fails it, tested; all three real corpus rows pass it,
tested against the corpus. The honest cost is the other direction (F5), and it is documented and pinned rather
than argued away. What I did NOT do is prove the interpreter test is necessary on the PC — no capture has run
with these bytes.

**A3 — "the coverage floor is a number I typed."** It is a number I measured on the final bytes and then
attacked: P7 (revert the `fd` idiom) drops `pc_launch.py` to 16 and the floor fails naming the file, the
count and the floor. But the floor is also the weakest gate in this lane, and P8 proved it: it cannot protect
an idiom no producer currently uses, and it would not notice a producer that stops writing a name entirely as
long as the count holds (a rename inside the mapping keeps the count). The idiom control at `:353` closes the
first hole; the second is closed by the subset and orphan directions, not by the floor. I have not built a
gate that catches "a producer silently stops writing a required name" — the corpus direction (b) catches it
only once a capture has run.

Two smaller ones I checked and could not break. First, `tests/conftest.py` is global to a ~30-file directory:
it imports nothing and touches no `sys.path` at collection time (the S0-01 pin module is imported inside the
fixture body), and `proofs/S0-01/pins.py` is the only `pins.py` in the tree
(`ls proofs/*/pins.py`), so there is no module to shadow. Second, `pins.py` now has module-level `import os`
and a function that can `SystemExit(64)` at import time — but only when `S0_01_HERMES_HOME` is SET, so every
existing consumer (the checker, `negative_contract`, three other test files) imports it exactly as before;
proven by the six-file adjacent run below.
