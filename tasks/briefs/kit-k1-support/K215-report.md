# K215 — report (task #215; lane k215, sandbox, shared tree)

STATUS: DONE, with the discrepancies below. Every item is DONE except that AF-AP-153 has no screen row, as the brief directs. Brief:
`tasks/briefs/kit-k1-support/K215-brief.md` (7aa7f35, rewritten on origin as b26f9f9), PIN 942ad5e. Nothing was committed (a lane never commits).
Evidence tiers: V = verified by a command or read this session; I = inferred from code; A = assumed.

## 1. Premise re-measure (2026-09-24 05:11Z, before any edit) — V

Every line of the brief's premise block reproduced unchanged at HEAD 7aa7f35. `git log 942ad5e..HEAD` listed only the brief's commit.
```
$ git rev-parse --short '942ad5e^{commit}'                                   -> 942ad5e
$ git merge-base --is-ancestor 942ad5e origin/claude/soundbox-kit-migration-iz1jwf && echo pin-is-on-origin   -> pin-is-on-origin
blobs at PIN == at HEAD == working tree: 2f968c6f5bb3 hook · 86a2d657e65d anti-hollow-green · ad8f20500fae build-loop ·
3c4987a07e64 deep-work · eb20dde7e198 ap_screen.py · 4a4ed0fece0b vendored_manifest.py · c33aa104023a / 9737b4919c95 the two tests
$ pytest tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py -q -p no:cacheprovider | tail -1   -> 173 passed
$ bash scripts/pc_suite.sh set-id -- tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py       -> 2 files set=2a60fb528bf2
$ python3 scripts/vendored_manifest.py --check | tail -1        -> PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots
sync-skills-check rc=0 · sync-lane-skills-check rc=0 · registry-rows=1 hook-mentions=0 for AF-AP-132/141/144/145/149/150/151/152/153/175/177
anchors as listed (hook 65/78/232/327/435; parse_classes 574; run_killer 1132; the control comment 1285; deep-work 195; build-loop 81)
```
Clock, V (05:43Z): during the lane the coordinator pushed. 7aa7f35 is now b26f9f9, and HEAD is 67cb0fa (origin 780f25a).
`git diff --name-only 7aa7f35 HEAD` names five files, none of them in this boundary. Every boundary blob at HEAD still equals the PIN's.
`git merge-base --is-ancestor 942ad5e HEAD` returned rc 0 with an empty stderr. At 06:14:39Z the coordinator committed ef21f88
(67cb0fa was rewritten to 9076164 by that push). Since b26f9f9 eight files changed, and none is in this boundary
(`git diff --name-only b26f9f9 HEAD`). `vendored_manifest.py --check` still passes at ef21f88.

## 2. Registry rows read (in full, before each pattern or bake) — V

I read them at lines 580-625 (05:1xZ). The coordinator's commit ef21f88 (06:14:39Z) moved them down 3 lines. Each row's text is
unchanged: its sha256 is equal at b26f9f9 and in the working tree for all eleven. Current lines:
- `docs/INCIDENT-LOG.md:583` `AF-AP-132`
- `docs/INCIDENT-LOG.md:592` `AF-AP-141`
- `docs/INCIDENT-LOG.md:595` `AF-AP-144`
- `docs/INCIDENT-LOG.md:596` `AF-AP-145`
- `docs/INCIDENT-LOG.md:600` `AF-AP-149`
- `docs/INCIDENT-LOG.md:601` `AF-AP-150`
- `docs/INCIDENT-LOG.md:602` `AF-AP-151`
- `docs/INCIDENT-LOG.md:603` `AF-AP-152`
- `docs/INCIDENT-LOG.md:604` `AF-AP-153`
- `docs/INCIDENT-LOG.md:626` `AF-AP-175`
- `docs/INCIDENT-LOG.md:628` `AF-AP-177`
- and the AF-AP-87, -89, -138 and -139 rows
- VERIFY-K150's inventory: `tasks/briefs/kit-k1-support/VERIFY-K150-report.md:556` (`FINDING INVENTORY`), plus its items 3, 7, 8 and 9
- Registry instances extracted from history into `/tmp/k215/inst/` (scratch). run_s0_05_units.sh at 97b589a^ and 97b589a. qwen-matrix.sh at 0c05970^ and 0c05970.
  transcript_export.py at 9932f34^ and 9932f34. The J1-1 redactor at 01ca7d5 and at HEAD (read only). J1-3's harvester at 0d62801^ and 0d62801.

## 3. Items — per item, the change and where it is (final tree)

`.claude/...` and `.agents/...` paths are not graded by report_lint (its reference pattern cannot start with a dot), so the hook's
lines are given here in words and numbers. The hook is `.claude/hooks/edit-snapshot.py`.

- s132 DONE — AF-AP-132. Hook row at line 273 (comment 268-272), AP_SCREEN only. It has three tells: enumerate over a `.splitlines()` call; a
  list bound from `.splitlines()` and enumerated with a start within 15 lines; a literal U+2028/U+2029/U+0085 on a line that decoded
  (U+FFFD on the line excludes it). Tests: `tests/test_edit_snapshot_ap_screen.py:610` (`TestAFAP132`): 4 positives, 4 negatives.
- s141 DONE — AF-AP-141. Hook row at 280. The comment (275-279) carries the AF-AP-87-style shell-reach line at 279. It fires on an argv
  holding `"--is-ancestor"` or `"cat-file", "-e"`, unless the line binds the error text, and on the shell form.
  Tests: `tests/test_edit_snapshot_ap_screen.py:655` (`TestAFAP141`): 3 positives, 2 negatives.
- s144 DONE (path-scoped; see D-3) — AF-AP-144. Hook row at 289 (comment 285-288). New class `_PathScoped` at hook lines 76-92.
  The hook's `main` applies the scope at lines 617-618 (`isinstance(rx, _PathScoped)`).
  Tests: `tests/test_edit_snapshot_ap_screen.py:681` (`TestAFAP144`): 2 positives, 3 negatives.
  Also `tests/test_edit_snapshot_ap_screen.py:718` (`test_af_ap_144_the_hook_applies_the_path_scope`): the REAL `main` on an Edit payload.
  Its runner is at `tests/test_edit_snapshot_ap_screen.py:708` (`capsys, path, hunk`).
- s145 DONE — AF-AP-145. Hook row at 301 (comment 295-300, shell-reach line 300). New class `_ExitTrapCleanup` at hook lines 95-116.
  It makes the row linear: a regex lookahead version took 0.68 s on 2,000 definitions (AF-AP-152's class, found by my timing probe).
  It also sees a trap line placed above its function. Tests: `tests/test_edit_snapshot_ap_screen.py:753` (`TestAFAP145`): 3 positives, 3 negatives.
- s149 DONE — AF-AP-149. Hook row at 308 (comment 303-307). Tests: `tests/test_edit_snapshot_ap_screen.py:781` (`TestAFAP149`): 3 positives, 2 negatives.
- s152 DONE — AF-AP-152. Hook row at 316 (comment 310-315). Tests: `tests/test_edit_snapshot_ap_screen.py:807` (`TestAFAP152`): 2 positives, 3 negatives.
- s175 DONE (line form; see D-2) — AF-AP-175. Hook row at 327 (comment 322-326).
  Tests: `tests/test_edit_snapshot_ap_screen.py:832` (`TestAFAP175`): 2 positives, 2 negatives.
- s177 DONE — AF-AP-177. Hook row at 337 (comment 332-336), with the direct form and the variable-held form. Tests:
  `tests/test_edit_snapshot_ap_screen.py:864` (`TestAFAP177`): 3 positives, 2 negatives. The fixture is `J1_3_R1_DISPATCH_SCAN` at `tests/test_edit_snapshot_ap_screen.py:854`.
- AF-AP-153 has NO screen row. Its class, a rewrite that drops an old refusal, has no line signature: the registry's signature column
  describes a missing differential step, not a line of code. It is bake b153 (D-5).
- No new row is in TEST_SCREEN. No class lives in tests. The only test-tree hits are three AF-AP-145 hits on harness-ports/tests fixture
  cleanups, and those are false hits.
- b150 DONE — AF-AP-150. `.claude/skills/deep-work/SKILL.md` lines 205-210 (inside the bug-echo paragraph). Twin: `.agents/skills/deep-work/SKILL.md`
  213-218, in its own words. Lane copy: `.agents/lane-skills/deep-work/SKILL.md` 213-218.
- b151 DONE — AF-AP-151. `.claude/skills/build-loop/SKILL.md` lines 85-92 (step 2, right after the pre-commit sentence). Twin:
  `.agents/skills/build-loop/SKILL.md` 88-95. The twin's step 2 has no pre-commit sentence, so there the bake opens step 2. Lane copy:
  the same lines.
- b153 DONE — AF-AP-153. `.claude/skills/anti-hollow-green/SKILL.md` lines 96-102: a new 3e in tactic 3. It points to
  orchestration 0d″ and does not repeat it. Twin: `.agents/skills/anti-hollow-green/SKILL.md` 104-111. Lane copy: the same lines.
- f03 DONE — F-03 / AF-AP-138. The harness body moved unchanged into `assert_mutant_killed` at `tests/test_vendored_manifest.py:1276`,
  with `run=run_killer`; only `run_killer(` became `run(`. `test_required_mutants_are_killed` (`tests/test_vendored_manifest.py:1305`) now calls it.
  New row: `test_af_ap_138_control_refuses_a_killer_that_fails_on_the_unmutated_module` at `tests/test_vendored_manifest.py:1314`.
- f04 DONE — F-04 / AF-AP-89: the reach comment at hook line 265, above the AF-AP-89 row.
- f06 DONE, WIDENED — F-06 / AF-AP-139. Hook lines 65-68 now accept an optional `-> None` and the ten 2xx `HTTPStatus` members. The registry
  row's scope ("the same 2xx for every path and method") includes both. The PIN row missed both positives (red run in section 4).
  Tests: `tests/test_edit_snapshot_ap_screen.py:541` (`test_fires_on_a_handler_annotated_to_return_none`),
  `tests/test_edit_snapshot_ap_screen.py:545` (`test_fires_on_an_http_status_member`), and
  `tests/test_edit_snapshot_ap_screen.py:549` (`test_no_fire_on_a_handler_that_always_refuses`).
- f07 DONE (see D-1) — F-07. `tests/test_edit_snapshot_ap_screen.py:933` (`test_pyflakes_delta_is_empty_when_the_venv_path_is_too_long`),
  `tests/test_edit_snapshot_ap_screen.py:949` (`test_pyflakes_delta_is_empty_when_the_venv_python_times_out`),
  `tests/test_edit_snapshot_ap_screen.py:966` (`test_pyflakes_delta_is_empty_when_the_venv_is_absent`).
- f08 DONE — F-08. `tests/test_vendored_manifest.py:662` (`bad-header`, refused at line 1), `tests/test_vendored_manifest.py:664` (`extra-cell`,
  refused at line 2). `scripts/vendored_manifest.py` was not modified.

## 4. RED → GREEN per new test — V (scratch only)

Scratch tree: `/tmp/k215/work` = `git archive HEAD` plus this lane's working files. Driver: `/tmp/k215/red.py`. Each mutant is one
exact-once replacement, compiled, run, then restored. GREEN side: the unmutated scratch runs (`168 passed`, `169 passed`, `170 passed`
as tests were added) and the gates in section 6. Runs from 05:44:37Z to 06:09:16Z.
```
RED   AF-AP-132 NEVER | 4 failed (the 4 positives)            RED   AF-AP-132 ALWAYS | 3 failed (the 3 negatives then present)
RED   AF-AP-141 NEVER | 3 failed                              RED   AF-AP-141 ALWAYS | 2 failed
RED   AF-AP-149 NEVER | 3 failed                              RED   AF-AP-149 ALWAYS | 2 failed
RED   AF-AP-152 NEVER | 2 failed                              RED   AF-AP-152 ALWAYS | 3 failed
RED   AF-AP-175 NEVER | 2 failed                              RED   AF-AP-175 ALWAYS | 2 failed
RED   AF-AP-177 NEVER | 3 failed                              RED   AF-AP-177 ALWAYS | 2 failed
RED   AF-AP-144 NEVER (inner pattern) | 3 failed: 2 TestAFAP144 positives + test_af_ap_144_the_hook_applies_the_path_scope
RED   AF-AP-144 ALWAYS (inner pattern) | 1 failed: test_no_fire_on_a_read_that_names_its_encoding
RED   AF-AP-144 path scope matches every path | 2 failed: test_no_fire_outside_the_checker_paths, …the_path_scope
RED   AF-AP-144 path-less search unscoped | 3 failed: …outside_the_checker_paths, test_the_path_less_callers_see_nothing, …the_path_scope
RED   main does not apply the scope | 1 failed: test_af_ap_144_the_hook_applies_the_path_scope
    E   AssertionError: assert 'AF-AP-144' in 'EDIT SNAPSHOT · check_pins.py\n  impact  module-level edit (no enclosing symbol resolved)\n  registry screen: no mechanical anti-pattern tells in this hunk\n'
RED   AF-AP-132 without branches B and C | 2 failed      RED   AF-AP-132 without branch C | 1 failed: test_fires_on_a_literal_separator
RED   AF-AP-132 separator branch without the U+FFFD exclusion | 1 failed: test_no_fire_on_a_line_that_did_not_decode
RED   AF-AP-141 without the shell branch | 1 failed      RED   AF-AP-141 without the bound-error exclusion | 1 failed
RED   AF-AP-149 without the missing-END branch | 1 failed RED  AF-AP-149 without the is-a-regex lookahead | 1 failed
RED   AF-AP-152 without form 2 | 1 failed               RED   AF-AP-152 negated classes admitted | 1 failed
RED   AF-AP-177 without the variable-held branch | 1 failed    RED   AF-AP-177 branch 1 without the str exclusion | 1 failed
RED   AF-AP-145 finds nothing | 3 failed (incl. test_fires_when_the_trap_line_comes_first)
RED   AF-AP-145 body check without the ignore test | 2 failed   RED   AF-AP-145 without the $? preamble allowance | 1 failed
RED   AF-AP-145 handler check without the ignore test | 1 failed RED  AF-AP-145 every function counts, trapped or not | 1 failed
RED   AF-AP-145 without the handler tell | 1 failed      RED   AF-AP-145 the old order (only a trap AFTER the function) | 1 failed
RED   AF-AP-139 at the PIN (no widening) | 2 failed: …annotated_to_return_none, …http_status_member
RED   AF-AP-139 K3 (any status) | 1 failed: test_no_fire_on_a_handler_that_always_refuses
RED   pyflakes_delta catch narrowed to PermissionError | 2 failed: …venv_path_is_too_long, …venv_python_times_out
    E   OSError: [Errno 36] File name too long: '/root/venv-agent-factory/bin/python'
    E   subprocess.TimeoutExpired: Command '['/root/venv-agent-factory/bin/python', '-m', 'pyflakes']' timed out after 8 seconds
RED   pyflakes_delta catch narrowed to OSError (K15) | 1 failed: …venv_python_times_out
RED   pyflakes_delta absent venv answers a line (K16) | 1 failed: test_pyflakes_delta_is_empty_when_the_venv_is_absent
    E   AssertionError: assert ['  LINT   venv absent'] == []
== unmutated scratch (138 set): 12 passed, 44 deselected          == unmutated scratch (F-08 set): 4 passed, 52 deselected
RED   F-03: the baseline control deleted | 1 failed, 11 passed: test_af_ap_138_control_refuses_…
    E   Failed: DID NOT RAISE Failed
RED   F-03: the control's pytest.fail swallowed (K20) | 1 failed, 11 passed
RED   F-08: M8d, the header refusal removed | 1 failed, 3 passed: [bad-header-<lambda>]
    E   AssertionError: ('bad-header', 'FAIL: .claude class drift: byte length differs
RED   F-08: M8e, a row with extra cells accepted | 1 failed, 3 passed: [extra-cell-<lambda>]
    E   AssertionError: ('extra-cell', 'FAIL: .claude class drift: byte length differs
```
Each NEVER run listed the row's positives by name, and each ALWAYS run its negatives. No mutant was INVALID. The F-03 RED is the
one the brief demands: with the control deleted on a scratch copy, the new row goes red (`DID NOT RAISE`), because the harness then
scores the stale killer as a kill. The F-07 GREEN side is the PIN's own code: `pyflakes_delta`, `_pyflakes_msgs`, `file_aware_screen` and
`enclosing_symbols` are identical to 942ad5e by an AST compare, and `main` differs only by the two scope lines.

## 5. Twins and generated files — V (the final pass, 06:09:26Z)
```
$ bash harness-ports/bin/sync-skills.sh --record  -> recorded base hashes for 15 hand-ported skills   rc=0
$ bash harness-ports/bin/sync-skills.sh --check   -> INTENTIONAL x15 … .agents/skills is in sync with .claude/skills (410 skills)   rc=0
$ git diff --stat harness-ports/hand-ported.sha256 -> 3 lines changed: anti-hollow-green 68916b02…, build-loop 635a2c3c…, deep-work ad2dd41c…
$ bash harness-ports/bin/sync-lane-skills.sh      -> first pass: DRIFT build-loop, deep-work, anti-hollow-green; synced 25 skills (3 changed); final pass: 0 changed   rc=0
$ bash harness-ports/bin/sync-lane-skills.sh --check -> sync-lane-skills: in sync (25 skills)   rc=0
$ python3 scripts/vendored_manifest.py --write    -> WROTE sandbox-kit/VENDORED-MANIFEST.md (9 roots) / WROTE …VENDORED-CLAUDE-CLASSES.tsv (3101 paths)   rc=0
$ python3 scripts/vendored_manifest.py --check    -> PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots   rc=0
$ git diff sandbox-kit/VENDORED-MANIFEST.md sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv
-Generated from commit: `9e5a171811355595591714e6403e84805633b7ff`
-Generated at (UTC): 2026-09-24T04:30:19.661392Z
+Generated from commit: `67cb0fa4d61e5c0ed294270eeabc6658bb49e270`
+Generated at (UTC): 2026-09-24T06:09:29.943489Z
-| `.claude/ (kit-adapted)` | … | 16 | 0 | `db403ca7d6e836c9d9b3c54ad179f0f9b68c70946f923b91aca61c70305bef5a` |
+| `.claude/ (kit-adapted)` | … | 16 | 0 | `52fd272761708c3b100515c12b2ab689bb1ee53b2604b342dcda7af3e11fa30d` |
(VENDORED-CLAUDE-CLASSES.tsv: no diff)
```
No class changed: the three skills and the hook stay `kit-adapted` (16 files), and the kit-verbatim count is 2956. The twins are in their own words:
`diff` of each `.claude` hunk against its `.agents` hunk shows different sentences for the same rule and incident.

## 6. Gates at the final tree — V
```
06:09:38Z $ /root/venv-agent-factory/bin/python -m pytest tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py -q -p no:cacheprovider
226 passed in 160.76s (0:02:40)        run 1 rc=0
06:12:19Z (same command)
226 passed in 174.14s (0:02:54)        run 2 rc=0
$ bash scripts/pc_suite.sh set-id -- tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py   -> 2 files set=2a60fb528bf2
06:15:22Z $ … -m pytest tests/test_hooks_worktree.py -q -p no:cacheprovider      -> 2 passed in 0.21s   rc=0
$ … -m pyflakes .claude/hooks/edit-snapshot.py tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py   -> (no output) rc=0
$ python3 scripts/no_laya_in_gates.py            -> no_laya_in_gates: 40 files scanned, clean   rc=0
$ python3 scripts/ap_screen.py .claude/hooks/edit-snapshot.py   -> --- AP_SCREEN over 1 path(s): 20 hits over 1 files ---   rc=0
06:15:28Z-06:16:59Z $ bash harness-ports/tests/run-all.sh   rc=0; last lines:
test_lane_context.sh               5 passed, 0 failed
test_context_mirrors.sh            11 passed, 0 failed
test_sync_skills.sh                34 passed, 0 failed
build-roles --check                OK: 3 role config layers match their sources

ALL SUITES PASSED
```
The count is 226 against the PIN's 173 (+53). The screen file went from 120 to 170 (+50), and the manifest file from 53 to 56 (+3). Same set id.
Hook self-screen: 20 hits. The PIN's hook text, screened by the same final rows, also gives 20, and the two hit lists are identical after
stripping line numbers (`diff` rc 0). My rows add exactly ONE hit to the hook's own text: AF-AP-175 at hook line 457. That is
`pyflakes_delta`'s single `git show HEAD:{rel}` per hook run, a known site. No new row fires on its own pattern, comment or message.
Regex cost on hostile input (`/tmp/k215/timing.py`; texts of up to 160,000 characters): the worst row is 0.0271 s (AF-AP-177).

## 7. Fire counts and hit classification (final tree) — `python3 scripts/ap_screen.py --limit 100000 $(git ls-files scripts src proofs harness-ports .claude/hooks)`

Output: `--- AP_SCREEN over 960 path(s): 385 hits over 960 files ---`, rc 0, 06:17:11Z. One line per hit follows. Classes: REAL (an
instance of the class), KNOWN (a site the registry already reviewed or that the class names), FALSE (not the class).

AF-AP-132 — 13 hits on 13 lines, all REAL (V: each line numbers a file line from a splitlines list; whether its input can ever hold a separator was not traced):
- `scripts/no_laya_in_gates.py:1443` `enumerate(content.splitlines(), 1)` — KNOWN, the registry's open site (its :639)
- `scripts/vendored_manifest.py:759` `splitlines` — KNOWN, the registry's :598 (parse_lock)
- `scripts/vendored_manifest.py:798` `splitlines` — KNOWN, the registry's :637 (parse_sbom)
- `scripts/vendored_manifest.py:477` `splitlines` — REAL, not in the registry (the pin line number written into the manifest)
- `scripts/vendored_manifest.py:402` `splitlines` — REAL, not in the registry (kit index parse; its refusal names the line)
- `scripts/vendored_manifest.py:575` `splitlines` — REAL, not in the registry (`parse_classes`)
- `scripts/vendored_manifest.py:653` `splitlines` — REAL, not in the registry (its line numbers are made at `scripts/vendored_manifest.py:666`, `start=header + 3`)
- `proofs/S0-01/check_acp_conformance.py:1200` `splitlines` — REAL, not in the registry (an attested input of the accepted S0-01)
- `proofs/S0-01/check_acp_conformance.py:1572` `splitlines` — REAL, not in the registry
- `proofs/S0-01/pins.py:553` `splitlines` — REAL, not in the registry
- `proofs/S0-01/pins.py:574` `splitlines` — REAL, not in the registry
- `proofs/S0-05/check_egress.py:253` `splitlines` — REAL, not in the registry
- `proofs/S0-08/check_containment.py:133` `splitlines` — REAL, and worse: the list drops blank lines, so its `line {index}` is not a file line at all
Before the U+FFFD exclusion the row also fired 275 times on 11 binary `.gz` evidence files (FALSE; D-4). It now fires 0 times on them.

AF-AP-141 — 5 hits on 4 lines:
- `scripts/check-proof-status.py:164` `--is-ancestor` — KNOWN (the registry's WATCH: fails closed, only its message can mislead)
- `scripts/ci_gate.py:213` `cat-file` — KNOWN (the registry's OPEN sibling, issue #40)
- `scripts/no_laya_in_gates.py:1311` `cat-file` — REAL, not in the registry (`_exists_staged` reads rc 0 as "staged" and never reads the captured stderr; consequence not traced)
- `scripts/pc_suite.sh:67` `cat-file -e` (2 hits on one line) — REAL in the shell form; the stderr is discarded. It fails safe (I): a false "absent" leads to a fetch and a second check.
- The fixed form stays quiet: `scripts/ci_gate.py:207` (`rc, _, err`).

AF-AP-144 — `ap_screen` count 0 by design (D-3). The row's own scope, applied per tracked file (`for_path(path)` over each whole file):
13 in-scope files of 960, 105 matches on 84 lines. Classification by the registry's own sweep and the `main`-handler table (V: an AST
walk of each `main`):
- S0-01 `check_acp_conformance.py`: 63 matches — FALSE: `main` catches `Exception`, and the registry says S0-01 converts at its readers
- S0-01 `check_initialize.py`: 7 — FALSE: `main` catches `Exception` (the malformed-evidence line)
- `proofs/S0-02/check_buzz_authz.py:186` `json.loads` — REAL in part: JSON errors are converted by the handler below it, but a non-UTF-8 read is not
- S0-02 lines 407, 543, 549 (`.read_text()` of `buzzacp.log`) — KNOWN: the registry's open sibling (non-UTF-8 `buzzacp.log`, issue #38)
- `proofs/S0-02/check_buzz_authz.py:835` `identities` — REAL, not in the registry: `json.loads` of `identities.json` with no handler; `main` catches `Deferred`/`Failure` only
- S0-03: 2 — FALSE (converted at the readers); S0-04: 3 — FALSE (`main` catch-all); S0-05: 6 — FALSE (catch-alls in the readers, per the registry)
- S0-06: 4 — FALSE (converted at the readers, per the registry); S0-08: 2 — FALSE (catch-alls in the readers, per the registry)
- S0-07: 4 (lines 43, 44, 45, 185) — KNOWN: the registry's WATCH (default-encoding reads, no handler)
- `proofs/S0-12/check_pin_diff.py:33` `yaml.safe_load` — KNOWN: the registry's WATCH (plus lines 28 and 34, the same WATCH)
- `proofs/S0-11/check_eval_hardening.py:146` `decode` — FALSE: `"replace"` cannot raise
- `proofs/S0-11/check_eval_hardening.py:357` `yaml.safe_load` — FALSE: inside `try … except Exception`
- `proofs/S0-11/check_eval_hardening.py:341` `design.read_text()` — REAL, not in the registry: a committed file read with the default encoding, no handler (the S0-12 shape)
- Not seen: S0-09 and S0-10 read with `open()`, which is not one of the signature's four calls (the registry lists them as WATCH).

AF-AP-145 — 7 hits:
- `proofs/S0-03/tools/pc/run_s0_03_legs.sh:83` `stop_all()` — KNOWN (the registry's WATCH)
- `proofs/S0-06/tools/pc/run_s0_06_legs.sh:59` `cleanup()` — KNOWN (the registry's WATCH)
- `proofs/S0-08/tools/pc/run_containment.sh:91` `cleanup()` — KNOWN (the registry's WATCH)
- `harness-ports/bin/pc-lane.sh:127` `stop_session` — KNOWN, FALSE for the class: the registry's OK (the handler re-enters and runs cleanup to its end)
- `harness-ports/tests/test_pc_lane_dispatcher.sh:11` `cleanup()` — FALSE (a test fixture: kills its own children, removes its temp dir)
- `harness-ports/tests/test_qwen_matrix_sh.sh:9` `cleanup()` — FALSE (the same)
- `harness-ports/tests/test_qwen_server.sh:29` `cleanup()` — FALSE (the same)
- Outside the five roots: the registry's WATCH `spikes/selective-egress/probe.sh:32` (`trap cleanup EXIT`) was not counted.

AF-AP-149 — 0 hits. Both registry instances are fixed. The row fires on both pre-fix texts from history (the transcript exporter at
9932f34^ line 27; the J1-1 redactor at 01ca7d5 line 57) and stays quiet on the fix (9932f34).

AF-AP-152 — 1 hit:
- `src/agent_factory/decisions/volatile.py:137` `backtracked exponentially` — FALSE: a comment quoting the fixed pattern. The row fires on the pre-fix `_ENVVAL` (01ca7d5 line 53).

AF-AP-175 — 12 hits, and none is a live mixed-snapshot run. This matches the registry's sweep ("none mixed"):
- `scripts/decide-harvest:145` `HEAD^{commit}` — KNOWN: the fix, the one resolve (J1-3-R1's `_resolve_commit`)
- `scripts/check-proof-status.py:164` `"HEAD"` — KNOWN: one read per accepted-proof check (I)
- `scripts/lint_delta.py:88` `_git_show` — KNOWN: one read per changed file inside the pre-commit hook
- `scripts/stamp_check.py:87` `_blob` — KNOWN: one read per file inside the pre-commit hook
- `scripts/stamp_check.py:43` `HEAD:path` — FALSE: a docstring
- `scripts/push_clean.sh:98` `TREE_BEFORE` — KNOWN: a deliberate before/after pair that proves tree identity across the rewrite
- `scripts/push_clean.sh:103` `TREE_AFTER` — KNOWN: the same pair
- `scripts/fubuki_pin_sync.sh:36` `HEAD^{tree}` — KNOWN: `tree_of` of a named repo (I)
- `scripts/fubuki_pin_sync.sh:66` `rev-parse` — KNOWN: the parent of ANOTHER repo's HEAD
- `scripts/vendored_manifest.py:844` `rev-parse` — KNOWN: one read, for the manifest header
- `src/agent_factory/governance/pin.py:75` `rev-parse` — KNOWN: one read per pin check (I)
- The hook itself at line 457 — KNOWN (section 6)
- The registry's instance (J1-3 before R1: `ls-tree … HEAD`, then `cat-file blob HEAD:{path}`) fires twice at 0d62801^ lines 141 and 152.

AF-AP-177 — 4 hits:
- `scripts/decide-harvest:686` `block.get("name")` — KNOWN (the registry's instance)
- `scripts/decide-harvest:689` `subagent_type` — KNOWN (the registry's variable-held instance at :691; the hit names the binding line)
- `harness-ports/bin/qwen_matrix.py:263` `message.get("role")` — KNOWN (the registry's sibling)
- `harness-ports/bin/lane-done-gate.py:148` `tool_name` — REAL, not in the registry: it is tested with `in {` two lines below
  (`write_file`, `harness-ports/bin/lane-done-gate.py:150`). A list there raises TypeError. That is contained by the catch-all at
  `harness-ports/bin/lane-done-gate.py:308` (`except Exception`): a warning, rc 0, and the record is skipped.

AF-AP-139 (widened) — production 1 hit, the same as at the PIN: `harness-ports/tests/test_pc_bridge_exec.py:20` `do_POST`, KNOWN (the bridge
stand-in the registry reviewed). TEST_SCREEN over `git ls-files tests harness-ports/tests` gives 8. VERIFY-K150 measured 6 at the PIN;
the two extra hits are this lane's own new positives (`tests/test_edit_snapshot_ap_screen.py:543` `-> None`, `tests/test_edit_snapshot_ap_screen.py:547` `HTTPStatus.OK`).

## 8. Registry rows this change settles (the coordinator owns docs/INCIDENT-LOG.md)
- The screen line now exists (task #215) for AF-AP-132, -141 (with `cat-file -e`), -144 (path-scoped), -145, -149, -152, -175 (line form) and -177 (with the variable-held form).
- AF-AP-150 is baked in deep-work and AF-AP-151 in build-loop. AF-AP-153 is baked in anti-hollow-green 3e; it gets no screen line, although its status column says one waits for #215.
- The AF-AP-138 follow-up (VERIFY-K150 F-03) is closed. The AF-AP-139 widening (F-06) and the AF-AP-89 reach comment (F-04) are in. F-07 and F-08 are closed.
- The registry's cited lines drifted. AF-AP-132 cites `no_laya_in_gates.py:639` and `vendored_manifest.py:598/:637`; at the PIN these are
  `scripts/no_laya_in_gates.py:1443` (`enumerate`), `scripts/vendored_manifest.py:759` and `scripts/vendored_manifest.py:798` (both `splitlines`).

## 9. Adjacent defects found (reported, NOT fixed: each is outside this boundary)
1. AF-AP-132, ten siblings the registry does not list (section 7). `proofs/S0-08/check_containment.py:133` (`splitlines`) is a second
   defect as well: its index counts non-blank lines only.
2. AF-AP-132 inside the commit-time screen: `scripts/lint_delta.py:99` (`splitlines`) splits the diff with `splitlines()`. A literal
   separator in an added line cuts that line, and the rest of the line is dropped from every AP_SCREEN row at commit time.
   V (the same expression, run on a diff line holding U+2028: `['a = 1']`).
3. AF-AP-141 sibling: `scripts/no_laya_in_gates.py:1311` (`cat-file`).
4. AF-AP-177 sibling: `harness-ports/bin/lane-done-gate.py:148` (`tool_name`); contained by `main`'s catch-all.
5. AF-AP-144 siblings: `proofs/S0-02/check_buzz_authz.py:835` (`identities`, no handler); `proofs/S0-11/check_eval_hardening.py:341` (`design.read_text()`).
6. Tooling (V, 05:37Z): my Edit call's parameter transport turned the typed escapes for U+2028 and U+2029 into LITERAL characters in
   the hook source; the U+0085 escape survived as text. That is AF-AP-132's second shape, written by the tool. My own separator check
   caught it before any gate ran, and the escapes were restored through a Python rewrite. Any lane that types those two escapes through
   the Edit or Write tool can hit this (a candidate CLAUDE.md quirk line).
7. Pre-existing VERIFY-K150 F-18, not fixed: `{ap_id:6s}` runs a 9-character id into its message. All my rows are 9 characters.

## DISCREPANCIES
- D-1 (f07). The brief asks for each of the three controls to go RED on a scratch copy with the catch narrowed to `PermissionError`.
  The absent-venv control never raises, so that mutant cannot red it; that run lists only the two other controls. The control goes RED
  under VERIFY-K150's K16 mutant instead (the absent branch answers a line: `assert ['  LINT   venv absent'] == []`). Both runs are pasted.
- D-2 (s175). The registry asks for a per-file COUNT screen. A row sees one hunk (the hook), the added lines (`lint_delta`) or one
  file's text (`ap_screen`). A hunk-level count would miss the commonest way this defect arrives: a hunk that adds a second read to a
  file that already has one. So this is the brief's fallback, the LINE form (every quoted `HEAD` literal), with the count condition in
  the message and in the comment. `ap_screen` prints hits per file, so the count is visible there.
- D-3 (s144). This is only a path-scoped line pattern. (a) The `main` condition and the reader-conversion condition are NOT checked,
  so a checker that fails closed through a catch-all gives false hits: 73 of the 105 matches are in the three catch-all mains.
  (b) The scope is applied in the hook's `main` only. `scripts/ap_screen.py` and `scripts/lint_delta.py` pass no path, so the row is
  quiet there by design (a test pins that). It needed a new class (`_PathScoped`) and two lines in `main`.
- D-4 (s132). The registry's third shape, a `.splitlines()` list indexed by a `\n`-counted number, has no line signature; it is not
  screened. The literal-separator shape skips lines that hold U+FFFD. Unnarrowed, it gave 275 FALSE hits in 11 binary `.gz` files when
  every tracked file was named. The narrowing was added after that measurement, with its own negative test and RED run.
- D-5 (AF-AP-153). There is no screen row, as the brief directs. The registry's status column still says "the screen line waits for task #215".
- D-6 (my sequencing). I edited the hook twice after the first pass of steps 3-5: the `_ExitTrapCleanup` fix after the timing probe,
  and the AF-AP-132 narrowing after the count. The first gate pair failed `5 failed, 220 passed` on both runs, on manifest drift
  (the committed `.claude/ (kit-adapted)` digest). I re-ran steps 3-5 in order after the last hook edit, and re-ran every gate at the
  final tree. Section 6 holds only final-tree results.
- D-7. The manifest header names `67cb0fa`, HEAD at write time. The coordinator's next push already rewrote that commit to 9076164
  (HEAD is now ef21f88), so the header names a commit that is not on the branch. It is informational (VERIFY-K150 F-19's class);
  `--check` ignores it and still passes.
- D-8 (f06). The widening goes beyond the literal-2xx form, and the registry's scope includes it. The other VERIFY-K150 near misses
  (the message argument, delegation, alias, `send_response_only`, bodies over 1,000 characters) were not in F-06 and were not addressed.
- D-9 (s177). The brief cites `scripts/decide-harvest:691` (`if role in`) for the variable-held form.
  The row reports its binding line instead: `scripts/decide-harvest:689` (`subagent_type`).
- D-10 (s145). The handler tell fires on `harness-ports/bin/pc-lane.sh:127` (`stop_session`), which the registry reviewed as OK.

## NOT-done
- No screen row for AF-AP-153 (D-5). The count form of AF-AP-175 (D-2). The `main` and reader conditions of AF-AP-144 (D-3). The indexed-list shape of AF-AP-132 (D-4).
- Not seen by the rows (documented in the hook comments): AF-AP-145 one-line function bodies; AF-AP-152 shorthand classes in form 2 and
  hand-written scanners (the `arith()` instance); AF-AP-177 a set held in a name and subscript reads; AF-AP-144 `open()` reads.
- No PC or bridge use. No commit. The registry was not edited (read-only). GitNexus `detect_changes` was not run (no commit is made
  here). `impact` was run before editing: `main` and `pyflakes_delta` in the hook returned risk UNKNOWN with 0 callers. A text search
  confirmed the real consumers: the hook runs as a process (`.claude/settings.json:46` and the codex/hermes adapters), and
  `scripts/ap_screen.py`, `scripts/lint_delta.py` and the test file load it in-process. All of them are covered by the gates in section 6.
- Scratch left for the coordinator: `/tmp/k215/` (driver, plans, instance copies, counts). The work tree was rebuilt per driver run.

## Self-attack (the three most likely ways this change is wrong, and how each was ruled out)
1. A row misses its registry instance, or fires on the fix. Ruled out: every instance was extracted from history and run through the
   real consumer (`scripts/ap_screen.py`). Each fires on every named pre-fix instance and stays quiet on every fix. Per-row NEVER,
   ALWAYS and per-branch mutants all went RED, and the fire counts are classified line by line (section 7).
2. The scope change in `main` breaks the hook, or a path-less caller. Ruled out: `main` changed only for `_PathScoped` rows (AST compare).
   `harness-ports/tests/run-all.sh` ran the real hook through the codex and hermes adapters and the spool: ALL SUITES PASSED.
   The path-less callers get `None` or nothing (a test pins this), and the main-level test goes RED when the scope is removed.
3. A new row is itself super-linear (AF-AP-152's class) and stalls a commit. This was found, not only ruled out: my first AF-AP-145
   regex took 0.68 s on 2,000 function definitions. It became the linear `_ExitTrapCleanup` class (0.0042 s), with two new tests
   (the trap-first order, and every function counting). Every final row's worst case on hostile input is at most 0.0271 s.
Also checked: `scripts/no_laya_in_gates.py` is clean (the hook is a gate file, so it names J1-3's harvester in words); no edited
file holds a literal separator or U+FFFD (a Python count gave 0 for each of the nine files); and the twins are rewritten, not copied.

## Report lint (two rounds, within the three-round bound)
```
$ python3 scripts/report_lint.py --min-refs 15 tasks/briefs/kit-k1-support/K215-report.md
round 1 (06:24:18Z): report_lint: 100 refs — OK 83, NEAR 5, MISS 12, UNCHECKABLE 0, UNRESOLVED 0 (worktree)   rc=1
round 2 (06:25:34Z): report_lint: 100 refs — OK 100, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)   rc=0
```
Round 1's MISSes had two causes. The registry rows had moved down 3 lines under the coordinator's ef21f88, so they are now cited at
their current lines, with the sha check in section 2. And several refs sat on a different physical line from their token; each ref now
shares a line with a token copied from the cited line. No cited line was wrong for its claim.
