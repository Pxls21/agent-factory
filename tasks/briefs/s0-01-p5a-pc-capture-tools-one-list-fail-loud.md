# Lane P5a — S0-01 PC capture tools, round 1: ONE producer/consumer file list, a scan header that cannot lie, every tool fail-loud (sandbox Opus 4.6 `code-implementer`)

PIN: (HEAD at dispatch — the commit carrying this brief. Your work lands in the CHILD commit; the report header says "PIN: `<sha>`".)

**Why (the largest open S0-01 defect):** SWEEP-prod row #1 — the checker's `_LEG_REQUIRED_FILES` (20 names) does not match what
the PC capture pipeline writes: the real corpus leg `run-1` (/root/s0-01-realleg/golden/run-1) carries 8 names the F21 allowlist
REJECTS (`backend-healthz-before.json`, `backend-healthz-after.json`, `hermes-config.sha256`, `launch.exited`, `launch.ready`,
`manifest-pre.done`, `manifest-post.done`, `teardown.txt`) and lacks 2 it REQUIRES (`tee-status.json`, `agent-stderr.txt`). No test
ever ran `check_bundle` over a real collected leg. The checker cannot pass the proof's own capture end to end; the PC tools were
never verified as a component. This lane owns the PRODUCER side and the shared list; the checker's consumer side (importing the
list) is the checker's next round — do NOT edit the checker.
**Inputs:** `tasks/briefs/s0-01-sweep-support/SWEEP-prod.md` rows #1, #5, #6, #12, #25, #27, #28, #31, #32, #33, #48, #52 (each with
its run, fix, red test) · `SWEEP-tests.md` rows 4.2 / 15.2 (the scan header's `rows=` never checked against the body: `rows=4`
hard-coded → 11 passed) and 11.1 (SAFE) · `tasks/briefs/s0-01-sweep-support/pack-probe-pctools.md` · the real corpus (declared:
`bash scripts/realleg_sync.sh check`; `/root/s0-01-realleg/golden/<leg>/` = what the pipeline actually writes) · `proofs/S0-01/pins.py`
(the pins the PC tools already import) · `docs/INCIDENT-LOG.md` (AF-AP-45, AF-AP-55, AF-AP-59 + addendum).
**Scope (+ your report):** `proofs/S0-01/pins.py` (ADD the list; change nothing else) · `proofs/S0-01/tools/pc/pc_launch.py` ·
`proofs/S0-01/tools/pc/pc_post.sh` · `proofs/S0-01/tools/pc/pc_negative.py` · `proofs/S0-01/tools/pc/run_leg.sh` ·
`proofs/S0-01/tools/pc/collect_leg.sh` · `proofs/S0-01/tools/build_capture_record.py` · `tests/test_s0_01_pc_post_scan.py` · a NEW
`tests/test_s0_01_pc_tools.py` · report `tasks/briefs/s0-01-p5a-support/P5a-report.md`. Everything else READ-ONLY — in particular
`proofs/S0-01/check_acp_conformance.py` and its test (another lane's checkpoint). Shared-tree rules: never `git
stash/checkout/restore/reset/add/commit/push`; gates from a `git archive <PIN>` copy under the session scratchpad
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/p5a/ + your files; mutants on scratch copies; explicit
`--basetemp`; kill only your own processes by pid; NEVER background a run and stop; no outward actions; NO PC bridge — the PC-only
paths (rows #12, #32, #48) are built with unit tests that monkeypatch the primitive and are marked `NOT run on the PC` in the report.

## Design (pinned — build it, do not redesign it)
1. **ONE list, in `pins.py`.** `PINNED_LEG_FILES` = a mapping name → {"required" | "optional"} covering EVERY name the pipeline writes
   into a leg (derive it by reading the producers: `pc_launch.py` writes, `pc_post.sh` writes, `frame_tee.py` writes (tee-status.json,
   timeline, frames, runtime-identity), `acp_probe.py` (negative leg), `pc_manifest.sh`, `collect_leg.sh` exclusions,
   `build_capture_record.py`'s `capture.json`) and CROSS-CHECKED against the real corpus (`ls /root/s0-01-realleg/golden/run-1`) —
   every real name is in the mapping, every mapping name has a producer named in a comment. `PINNED_LEG_DIRS` likewise (`mentions`,
   `upstream-records`). A test in the new file asserts (a) the corpus legs ⊆ the mapping's keys, (b) every "required" name is present
   in every corpus positive leg (or the test states the corpus-version rule: `tee-status.json` required only for a v2.3 corpus — read
   the checker's `_CORPUS_VERSION` idea from tests/test_s0_01_check_acp_conformance.py and MIRROR the rule, do not import that file),
   (c) the producers' write set (parsed from the scripts by grep for the literal names) ⊆ the mapping. Rejected: extending the
   checker's private set (two lists drift again).
2. **`capture.json` (rows #27/#28).** `build_capture_record.py` exits non-zero when `timeline.jsonl` is absent and takes its
   required-name list FROM `pins.PINNED_LEG_FILES`; its output name is in the mapping as optional (the checker admits it once it
   imports the list). Red-before: an empty leg dir → rc 0 (the sweep's run); after: rc ≠ 0 named.
3. **The scan header cannot lie (rows #5/#6; tests 4.2/15.2; the AF-AP-59 addendum).** `pc_post.sh`: `pinned_present` is counted over
   the SAME `keep` list the body is written from (header after the filter), and a row counts as pinned by its EXECUTABLE — for
   buzz-acp and the agent compare `/proc/<pid>/exe` realpath to the pinned realpaths; for the tee compare argv[1] to
   `PINNED_TEE_PATH` — never a substring of the command line. Header `rows=` = the count of rows the body carries after the filter
   PLUS a new `table_rows=` for the full table (two counters, two names, never asserted equal). Bump the header to `v2.4` and update
   `tests/test_s0_01_pc_post_scan.py`'s `_parse` to assert `rows= == len(body)` (the sweep's one-line fix) and the synthetic-table
   test to the new semantics (the coordinator's `test_pinned_present_is_exact_over_a_synthetic_table` — keep its shape, change its
   expectations, and say why in the docstring). Red-before: `rows=4` hard-coded → 11 passed (the sweep's R15); a `sleep` whose argv
   mentions the tee path counted as pinned (#6). NOTE: the checker's F17 consumer still expects v2.3 — state in the report that the
   checker's next round adopts v2.4 (the coordinator sequences it); do not touch the checker.
4. **`pc_launch.py` fail-loud (rows #12, #31, #32, #48, #52, #25).** `readlink`/`sha256_file` on `/proc/<pid>/exe` inside `try/except
   OSError` → `SystemExit("pc_launch: buzz-acp exited during identity capture (rc=…)")`; the tee-identity wait raises a named
   SystemExit instead of the `_note` default; the pre-manifest wait breaks on the manifest's failure signature (its log non-empty
   with no `.done`) and surfaces the tail; the summary `[-1]` guarded; the descendant walk scoped to the session (`ps -s`); redaction
   fingerprints (`len`, `sha256_12`) computed on the RAW bytes before decoding. Each with a unit test that monkeypatches the primitive
   (`os.readlink` raising, a fake `ps` table, a truncated summary) — PC-only paths are `NOT run on the PC` in the report.
5. **`pc_negative.py` propagates the probe's exit code (row #33)** — `raise SystemExit(rc)`; test: a probe returning 3 → rc 3.
6. **`run_leg.sh` / `collect_leg.sh`:** `set -euo pipefail` already; `collect_leg.sh`'s exclusion list and the mapping agree (a test
   parses the `--exclude=` literals and checks each is either excluded on purpose (named in the mapping as `excluded_on_collect`) or
   absent from the mapping with a reason).
7. **Report discipline:** `report_lint.py` on your report (map every scope file), MISS 0; `ap_screen.py` over your production files
   (`proofs/S0-01/tools/pc`, `build_capture_record.py`, `pins.py`) and `--tests` over your two test files — every hit classified by
   running it; every file:line by `grep -n` on the FINAL bytes; counts pasted.

## Mutants (scratch copies; ≥ 12 rows; killer line pasted)
LIST-DRIFT (drop one real name from the mapping → test 1a red) · PRODUCER-UNLISTED (a producer writes a name outside the mapping →
1c red) · PINNED-OVER-TABLE (header counted over the full table again) · SUBSTRING-PINNED (argv substring match restored) ·
ROWS-LITERAL (`rows=4`) · CAPTURE-GREEN-ON-NOTHING · READLINK-UNGUARDED · NOTE-DEFAULT · WAIT-SUCCESS-ONLY · SUMMARY-INDEX ·
NEGATIVE-RC-DROPPED · FINGERPRINT-ON-REPLACED.

## Gates (paste verbatim)
`bash scripts/test_summary.sh tests/test_s0_01_pc_post_scan.py tests/test_s0_01_pc_tools.py` twice from the archive copy + your
files · `pyflakes` on every Python file you touched · `bash -n` on every shell script · `python3 scripts/lint_delta.py --base <PIN>`
· report_lint + ap_screen (item 7) · the process census. NOT run here: the PC `-n 8` gate and any real capture (coordinator's; the
re-capture with the final tools validates end to end). Report shape: FILE IDENTITY, DONE, MUTANT table, NOT_DONE (the PC-only rows
by name), DISCREPANCIES (anything the sweep got wrong — e.g. a name it called "written by the pipeline" that no producer writes),
SELF-ATTACK.
