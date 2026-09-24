# K150 report — lane k150 (task #150), sandbox `code-implementer`, shared tree

STATUS: DONE 2026-09-24T02:5xZ — every item (a)-(n) done in the tree, uncommitted; all gates green (below). Deviation by
addition D-5 (AF-AP-139 also in TEST_SCREEN) and fix D-10 (a hollow mutant row the new control caught) flagged for review.

## Premise re-measure (2026-09-24T01:45Z)

- HEAD at dispatch `8ea2932`; HEAD moved to `48e81f0` during the re-measure (coordinator commit
  2026-09-24T01:45:25+00:00, touches only `todo/BUILD-TASKLIST.md` and `wiki/topics/live-state.md`).
- Every boundary file: blob at HEAD == blob at PIN `033a9b0` == working-tree blob (git hash-object):
  build-loop b33bb80b73ee/db4f9e65a4f5, anti-hollow-green e6438ca6442c/58a351bc0f33, orchestration
  2315dc9f5723/ed3c231ce795, `.claude/hooks/edit-snapshot.py` b52a0d8ab536, `tests/test_edit_snapshot_ap_screen.py`
  d7448f51bb89, `tests/test_vendored_manifest.py` 74b02f869df5; lane-skills twins db4f9e65a4f5/58a351bc0f33/ed3c231ce795;
  `harness-ports/hand-ported.sha256` 2b4ccfab228e; `sandbox-kit/VENDORED-MANIFEST.md` 910d0a9c6bd5;
  `sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv` 2310ac61fbd5; `scripts/vendored_manifest.py` 4a4ed0fece0b.
- Twins identical x3, hand-ported x3, in lane-skills.txt x3; `sync-skills --check rc=0`; `sync-lane-skills --check rc=0`;
  `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots`; classes lines 41/350/501/1827 all `kit-adapted`.
- Anchors: build-loop `:78`; orchestration 0d′ `:50`, 0d″ `:59`, 0f `:84`, `## Parallel agents` `:241`, RESTART `:429`;
  `.agents` orchestration `RESTART is the same` count 0 (rc=1); `AP_SCREEN = [` `:63`, `_pyflakes_msgs` `:284`,
  `pyflakes_delta` `:297`.
- Registry rows: one each for AF-AP-25/44/89/138/139/140/153/155/159/162/164/170; hook lines naming AF-AP-44: 3, AF-AP-159: 3, rest 0.
- Baseline gate: `152 passed`; `2 files set=2a60fb528bf2`.
- Verdict: premise MATCHES on every line. No STOP.

## Resume after the container restart (2026-09-24T02:02:50Z)

- HEAD `48e81f0`; origin `8ea2932`. `git status --porcelain`: only `?? tasks/briefs/kit-k1-support/K150-report.md` and
  `?? tasks/briefs/laya/J1-3-R1-report.md` (the other lane's report); no boundary file modified.
- `git diff --stat 033a9b0 HEAD -- <16 boundary files incl. scripts/vendored_manifest.py>`: printed nothing (rc=0).
- Commits since the PIN: 257394b, de4e749 (brief), d091312 (S0-05 anchor), 8ea2932 (transcripts), 48e81f0 (ledger + wiki).
- Verdict: premise still MATCHES. Continuing from item (a).

## Resume after the owner's stop (2026-09-24T02:17:43Z)

- HEAD `a10a012`; origin `499cb55`. `git diff --stat 033a9b0 HEAD -- <the 16 boundary files>`: printed nothing (diff-rc=0);
  commits since 48e81f0: 247a39a, a10a012 (ledger, wiki, D-065; no boundary file).
- Tree: `.claude` + `.agents` build-loop and anti-hollow-green modified (6 insertions, 2 deletions); no other boundary file.
- Review of the three DONE items against their rows and the tree: (a) build-loop `:78` / twin `:86` identical (`diff` of the
  two lines: empty); every claim matches `scripts/ci_gate.py:1-45` (exit table: 1 red, 75 unknown, `--wait SECONDS`, default
  hint `--wait 1800` at `:299`) and the call site `scripts/push_clean.sh:88` (`ci_gate.py`). (d1) `:129` and (l′) `:130` identical in both
  twins (`diff`: empty); each matches its registry row (`AF-AP-139` `docs/INCIDENT-LOG.md@2b13ced:574`, AF-AP-162 `:597`; the draft's
  `:559`/`:572`/`:595` were the row numbers at 48e81f0; commit 2b13ced, 2026-09-24T02:04:05Z, added 2 lines to the log). No half-done edit. `.agents/lane-skills`
  twins still carry the PIN text (the sync step comes later, per the brief's order).

## Items

(filled below as each lands)

### (a) build-loop: the CI-read paragraph names its instrument — DONE
- `.claude/skills/build-loop/SKILL.md:78` and twin `.agents/skills/build-loop/SKILL.md:86`: one sentence appended to the
  paragraph "A pushed head is green only when ITS CI run has been read" — `scripts/ci_gate.py`, run by `scripts/push_clean.sh`
  after its fetch; exit 1 refuses while the newest stage0-ci run in origin's history is red, exit 75 while the verdict is
  unknown; `python3 scripts/ci_gate.py --branch <branch> --wait 1800` waits.
- Source: registry row `AF-AP-126` (`docs/INCIDENT-LOG.md@2b13ced:561`), and the exit table in the `scripts/ci_gate.py` docstring (lines
  1-46); the call site is `scripts/push_clean.sh:88`. The twin paragraph was byte-identical at the PIN (no Claude-only
  mechanism in it), so the port is the same sentence, written by hand.

### (d1) anti-hollow-green: AF-AP-139's rule — DONE
- `.claude/skills/anti-hollow-green/SKILL.md:129` and twin `.agents/skills/anti-hollow-green/SKILL.md:129`: "Stand-in corollary"
  under tactic 7 (a green without the claimed part running). Rule: a stand-in for a named real service answers the probe's exact
  request as that service does, measured on the real service before the design freezes; never one 2xx for every path.
- Source: registry row `AF-AP-139` (`docs/INCIDENT-LOG.md@2b13ced:574`): C0's `GET /v1/models`; the real OmniRoute 401, the real relay
  404; the fix keys the stand-in's status on the path and adds a 401 negative control on the probe path.

### (l′) anti-hollow-green: AF-AP-162's rule — DONE
- `.claude/skills/anti-hollow-green/SKILL.md:130` and twin `.agents/skills/anti-hollow-green/SKILL.md:130`: "Remote-program
  corollary". Rule: a double for a remote command RUNS it (`bash -c`) against a fake remote root no local path matches, never
  answers from the command's text; a lane's own new case arm writes the test's answer; one executed case per remote-state
  branch, and each mutant runs as the lane's user and as root.
- Source: registry row `AF-AP-162` (`docs/INCIDENT-LOG.md@2b13ced:597`), both instances (the T94 landing's 42/42 through a canned arm; the
  second instance, VERIFY-T94 F-1). Twin wording: no Claude-only mechanism in either corollary, so the text is the same.

### (e) orchestration, `## Parallel agents, liveness, coordinator economy`: AF-AP-140's rule — DONE
- `.claude/skills/orchestration/SKILL.md:301`, twin `.agents/skills/orchestration/SKILL.md:314`: new bullet "A terminal marker
  belongs to ONE attempt". Rule: a poller reads a FAILED / exit / ready marker only when it is bound to the current attempt (pid
  alive or dead, an attempt counter, or an mtime after this launch). Source: row `AF-AP-140` (`docs/INCIDENT-LOG.md@2b13ced:575`), its
  incident (2026-09-23 07:14Z, VERIFY-T92's relaunch, `LANE FAILED` from the 04:03Z loop's marker, a false capacity claim).

### (h) orchestration: AF-AP-155's brief-time grep — DONE
- `.claude/skills/orchestration/SKILL.md:92`, twin `:100`: new `0e′` under 0e. Rule: at authoring, grep the ledger and every
  PROVENANCE file for the lane's name with the row's phrasings, and carry each hit into the brief or say why it is out of scope.
  Source: row `AF-AP-155` (`docs/INCIDENT-LOG.md@2b13ced:590`) and the quoted planning note (`todo/BUILD-TASKLIST.md:120`, "B9's inputs", `revoked.json`).
- The grep in the bake, run on the real tree (0d‴): `grep -n "B9's inputs\|in B9\b\|B9 option\|takes this value in B9"
  todo/BUILD-TASKLIST.md $(git ls-files 'proofs/*PROVENANCE.md')` → `todo/BUILD-TASKLIST.md:120:…` rc=0; control lane `B99` →
  no output, rc=1. The file set is `git ls-files 'proofs/*PROVENANCE.md'` (15 files), not the row's glob (see DISCREPANCIES D-2).

### (i) orchestration 0d″: a verifier's PROPOSED FIX is a hypothesis too — DONE
- `.claude/skills/orchestration/SKILL.md:69-73`, twin `:77-81`: corollary appended to 0d″. Rule: before a brief adopts a
  verifier's fix, run it against a control with a real value for each condition under which it SKIPS a redaction or a refusal.
- Source: VERIFY-J1-1-R1's option B (`tasks/briefs/laya/VERIFY-J1-1-R1-report.md:538-547`, the bearer lookahead
  `(?![\"']?\s?[:=])`), `D-057`'s rejection (`docs/08_DECISION_LOG.md:68`: "measured at authoring on a scratch copy, it opens a NEW
  leak (`Authorization: Bearer <token>: rejected` keeps the token)"), ledger `todo/BUILD-TASKLIST.md:1348`; class `AF-AP-153`
  (`docs/INCIDENT-LOG.md@2b13ced:588`).

### (l) orchestration 0d′: no volatile field in a premise line — DONE
- `.claude/skills/orchestration/SKILL.md:58-63`, twin `:66-71`: corollary appended to 0d′. Rule: strip pytest's ` in N.NNs` (and
  any clock or pid) with `sed` inside the echoed command, never by hand; the lane re-runs the echoed line.
- Source: row `AF-AP-164` (`docs/INCIDENT-LOG.md@2b13ced:599`) and its narrative (`:22`); the first VERIFY-J1-3 brief's block
  (`git show 3184014:tasks/briefs/pc/pc-verify-j1-3.md`, lines 77-78: `… | tail -1   (set 87e28761f102)` / `33 passed in 12.09s`);
  the re-measured block strips it inside the command (`tasks/briefs/pc/pc-verify-j1-3.md:79`, commit 1cfc8f1). See D-1.

### (k) orchestration 0f: two partial-verify rules — DONE
- `.claude/skills/orchestration/SKILL.md:106-112`, twin `:114-120`: "A partial verify is never a verification", rules (1) and (2).
- Sources: (1) VERIFY-C2 (`todo/BUILD-TASKLIST.md:1375`: "served ENTIRELY by antigravity/gemini-3.1-pro-low, 29 calls … its §6
  mutants were reasoned, not executed, so C2 STAYS GATED-PENDING-VERIFY … All of this is in issue #56"); (2) VERIFY-J1-3's first
  pass (`todo/BUILD-TASKLIST.md:1384`, the coordinator's PARTIAL ruling) refuted by VERIFY-J1-3-R2 (`:1387`, NOT-READY, four
  blockers), row `AF-AP-170` (`docs/INCIDENT-LOG.md@2b13ced:605`).

### (j) orchestration recovery paragraph: the QUOTA STOP form — DONE
- `.claude/skills/orchestration/SKILL.md:452-458`: the QUOTA STOP form appended to the (d) paragraph, right after "A container
  RESTART is the same shape" (`:448-451`). Route worded neutrally: "on the route the current routing ruling allows" (D-061).
- Twin `.agents/skills/orchestration/SKILL.md:446-467`: the whole missing recovery text (user-STOPPED, COMMIT-EARLY, Recovery =,
  container RESTART; dropped from the twin by port commit 06b1d24, 2026-09-03) plus the QUOTA STOP form. The one reword, in the
  twin's words: `(the harness refuses SendMessage: "won't be resumed")` → `(the sandbox harness refuses to resume it: "won't be
  resumed")`; `TaskStop'd` and "compaction summary" stay, as elsewhere in the twins.
- Sources: the owner ruling of 2026-09-08 (`docs/INCIDENT-LOG.md@2b13ced:357`, `LANE_PATCH`), the fourth stop and its recovery (`:37-41`), S198A's landing
  (`todo/BUILD-TASKLIST.md:1361`: "the coordinator proved its final blob 37d94bd AST-identical to 515d78b … re-ran the gates", `37d94bd`), D-061
  (`docs/08_DECISION_LOG.md:72`), D-062 (`:73`).
- Twin check: every line added to the `.claude` file is among the twin's added lines (grep -x -F: 0 missing); the twin's 15 extra
  lines are exactly the ported recovery text.

### Screen rows — design measurements (before writing each row)
- Instrument `/tmp/k150/flood.py`: whole-text `finditer` over `git ls-files` of the named dirs (the hook's and
  `scripts/ap_screen.py`'s semantics; `ap_screen.py`'s own directory walk is non-recursive, so it is not the counter).
- Consumers read before editing (literal sweep; GitNexus `impact pyflakes_delta` → `Target 'pyflakes_delta' not found`,
  risk UNKNOWN, the hook is outside its index): `scripts/lint_delta.py:103-114,144-152` (AP_SCREEN advisory, blocks only on
  pyflakes), `scripts/ap_screen.py:25-29`, `tests/test_s0_01_frame_tee.py:43,3058` (reads AF-AP-59 only), `tests/test_ap_screen.py:58-59`
  (reads AF-AP-57 only). No consumer keys on the row count.
- Self-screen baseline, unedited hook (`python3 scripts/ap_screen.py .claude/hooks/edit-snapshot.py`):
  `--- AP_SCREEN over 1 path(s): 19 hits over 1 files ---`.

### (d2) AF-AP-139's signature — DONE (with deviation D-5)
- `.claude/hooks/edit-snapshot.py:60-72` (`_AF_AP_139`, one tuple), in `AP_SCREEN` at `:210` and `TEST_SCREEN` at `:297`.
  Regex: a `do_<METHOD>(self)` handler that reaches `send_response(<literal 2xx>)` with no `if … self.path` line and no
  other `def` before it (within 1000 chars). Source: row `AF-AP-139` (`docs/INCIDENT-LOG.md@2b13ced:574`), signature column "a test HTTP
  handler that sends the same 2xx for every path and method (no branch on `self.path`)".
- Why not "no `self.path` at all": the registry's own instance logs `self.path` and never branches on it (pre-fix
  `tests/test_s0_05_egress.py` at `76f439f^:1579-1583`); mutant M139-any-self-path-stops misses it (below).
- Measured: over the pre-fix S0-05 test, hits at lines 782, 926, 1580 (1580 = the motivating `_listener`; 782/926 the
  DEVICE handlers the registry reviewed as intended). Literal-only alternative `send_response\(\s*2\d\d\s*\)`: 3 lines over
  the four dirs, incl. two handlers that branch on the path or sit in a helper (`harness-ports/tests/test_qwen_matrix.py:94`,
  `proofs/S0-01/tools/scripted_backend.py:795`); the tempered form: 1 (below).
- Tests `tests/test_edit_snapshot_ap_screen.py:500-535` (`TestAFAP139`): identity of the two list entries; positives = the
  pre-fix listener (fixture byte-identical to `76f439f^:1579-1583`, checked: `True`) and an always-200 `do_POST`; negatives = the
  E3-b fix (`STATUS.get(self.path, 200)`), a handler that branches on the path, a literal 200 in a non-handler method.

### (g) AF-AP-25's line-parser signature — DONE
- `.claude/hooks/edit-snapshot.py:211-216`: a `for … in …splitlines()/readlines()/open(…):` loop whose body, within 400
  chars, calls `re.match(` / `re.fullmatch(`. Source: row `AF-AP-25` (`docs/INCIDENT-LOG.md@2b13ced:460`, the 2026-09-23 line-parser
  twist) and its bug-echo (`docs/research/bug-echo/2026-09-23-bug-echo-fail-open-line-parser.md:14-20`).
- Flood measurement (four dirs): the bug-echo's own loop-header regex alone fires on 56 lines (45 in .py) — a flood; with the
  `re.(full)?match(` conjunct, 4 lines (both BUG sites `scripts/vendored_manifest.py:759`, `:798` + 2; both `enumerate` over `splitlines`). A compiled-pattern
  extension (`NAME.match(`) was measured at 8 lines, the 4 extra being key-line lookups and scans that fail closed
  (`proofs/S0-03/tools/pc/direct_responses_probe.py:88`, `proofs/S0-04/tools/pc/capture_leg.py:70`, `scripts/check-proof-status.py:238`,
  `harness-ports/bin/codex-hook-adapter.py:82`): rejected; documented limit in the row's comment.
- Tests `tests/test_edit_snapshot_ap_screen.py:538-565` (`TestAFAP25`): positives = the `parse_sbom` loop and `parse_lock`'s
  seven-line skip prefix; negatives = a JSONL loop (`json.loads` raises), a single-value `re.fullmatch` outside a loop.

### (k′) AF-AP-162 / AF-AP-89's doubled escape — DONE (one reviewed-safe hit, D-6)
- `.claude/hooks/edit-snapshot.py:217-222`, row id `AF-AP-89` (the signature is in AF-AP-89's column; AF-AP-162's column says
  "no mechanical code signature"; both cited). Regex: `bridge` / `pc.sh`, whitespace, `"`, then a shell double-quoted body
  scanned as escape PAIRS (`(?:[^"\\]|\\[\s\S])*?`), then a literal `\\` followed by `$(` or `\"`. Pair scanning stops at the
  argument's closing quote and aligns backslashes, so a single escape `\$(` never matches.
- Source: rows `AF-AP-89` (`docs/INCIDENT-LOG.md@2b13ced:524`) and AF-AP-162 (`:597`); the instance: T94's patch
  (`tasks/briefs/pc/patch-pc-t94.md--feb26d7.diff:262`, `lane.pid`, `! kill -0 \\$(cat …/lane.pid …)`, `[ -n \\\"\\$(find …)\\\" ]`).
- Tests `tests/test_edit_snapshot_ap_screen.py:568-588` (`TestAFAP89`): positives = the T94 `\\$(` probe, a `\\\"` through
  `scripts/pc.sh`; negatives = the single escape `\$(`, a doubled escape in a local `echo "…"`, a doubled escape after the
  bridge argument has closed.

### (m) issue #57 F-2: AF-AP-159's right-operand fixture — DONE (row WIDENED)
- The row did NOT fire on `2 + node.start_mark.line` (mutant M159-old-left-only = the PIN's regex: the new fixture fails).
  Scope: the registry row's class is "a line map built as `node.start_mark.line + k`" (`docs/INCIDENT-LOG.md@2b13ced:594`); the sum is
  commutative, so `k + node.start_mark.line` is the same line map, in scope. Widened at `.claude/hooks/edit-snapshot.py:205-206`
  to `\.start_mark\.line\s*\+|\+\s*[\w.\[\]]*\bstart_mark\.line\b`; comment line added.
- Tests `tests/test_edit_snapshot_ap_screen.py:491-497`: `test_fires_on_the_right_operand_form` (RED on the PIN regex, GREEN
  widened), `test_no_fire_on_a_right_operand_column` (`2 + node.start_mark.column`).

### Row fixtures, RED side: 8 regex mutants in the scratch copy, each killed by a named fixture
`/tmp/k150/row_mutants.py`, run in `/tmp/k150/work` (HEAD archive + the lane's hook and test file), 2026-09-24T02:39:43Z:
```
M139-literal-only: rc=1 2 failed, 4 passed, 114 deselected in 0.08s killed-by=['test_no_fire_when_the_handler_branches_on_the_path', 'test_no_fire_on_a_literal_200_outside_a_handler']
M139-no-path-branch-stop: rc=1 1 failed, 5 passed, 114 deselected in 0.10s killed-by=['test_no_fire_when_the_handler_branches_on_the_path']
M139-any-self-path-stops: rc=1 1 failed, 5 passed, 114 deselected in 0.06s killed-by=['test_fires_on_the_pre_fix_s0_05_listener']
M25-match-only: rc=1 2 failed, 2 passed, 116 deselected in 0.07s killed-by=['test_fires_on_the_parse_sbom_loop', 'test_fires_past_the_skip_prefix_of_parse_lock']
M25-no-regex-conjunct: rc=1 1 failed, 3 passed, 116 deselected in 0.09s killed-by=['test_no_fire_on_a_jsonl_loop']
M89-single-backslash: rc=1 3 failed, 2 passed, 115 deselected in 0.08s killed-by=['test_fires_on_the_t94_doubled_command_substitution', 'test_fires_on_a_doubled_escaped_quote_through_pc_sh', 'test_no_fire_on_the_single_escape']
M89-scan-crosses-quote: rc=1 1 failed, 4 passed, 115 deselected in 0.06s killed-by=['test_no_fire_after_the_argument_closes']
M159-old-left-only: rc=1 1 failed, 5 passed, 114 deselected in 0.08s killed-by=['test_fires_on_the_right_operand_form']
scratch hook restored == shared: True
```

### (f) AF-AP-44, the hook instance: `pyflakes_delta` — DONE
- Probes of the venv path in the hook (the complete set): `_VENV_PY` built at `:311` (no probe); `Path(_VENV_PY).exists()`
  (PIN `:300`, OUTSIDE the try — the crash); `_pyflakes_msgs(_VENV_PY, …)` twice (running the venv interpreter, already
  inside the try). Fix `.claude/hooks/edit-snapshot.py:327-336`: the `exists()` probe moved inside the `try`, so every venv-path
  probe is in it; the docstring says so. Source: row `AF-AP-44` (`docs/INCIDENT-LOG.md@2b13ced:479`, the 2026-09-23 hook instance).
- Tests `tests/test_edit_snapshot_ap_screen.py:591-625`: `test_pyflakes_delta_is_empty_when_the_venv_probe_raises` (the
  `exists()` probe raises `PermissionError(13)`) and `…_when_running_the_venv_python_raises` (the interpreter run raises).
- RED before the fix (scratch, the lane's hook without the fix, 2026-09-24T02:38:41Z):
  `.claude/hooks/edit-snapshot.py:330: in pyflakes_delta` / `if not Path(_VENV_PY).exists():` /
  `E           PermissionError: [Errno 13] Permission denied: '/root/venv-agent-factory/bin/python'` /
  `FAILED tests/test_edit_snapshot_ap_screen.py::test_pyflakes_delta_is_empty_when_the_venv_probe_raises` /
  `1 failed, 1 passed, 118 deselected in 0.14s`. GREEN after (02:38:53Z): `2 passed, 118 deselected in 0.06s`.
- The second test was GREEN before the fix (that probe was already inside the try); de-vacuoused by mutant
  M-run-outside-try (scratch): `FAILED …::test_pyflakes_delta_is_empty_when_running_the_venv_python_raises` /
  `1 failed, 1 passed, 118 deselected in 0.08s`.
- Outermost boundary, a REAL kernel refusal (sandbox `/root` is `700 root`): the hook run as uid 65534 via `setpriv`,
  `AF_VENV` unset, on an Edit payload: HEAD's hook → `PermissionError: [Errno 13] Permission denied:
  '/root/venv-agent-factory/bin/python'`, rc=1; the fixed hook → `EDIT SNAPSHOT · mod.py` … `registry screen: no mechanical
  anti-pattern tells in this hunk`, rc=0.

### (b) AF-AP-138's baseline control in `tests/test_vendored_manifest.py` — DONE (+ one hollow row found and fixed, D-10)
- `tests/test_vendored_manifest.py:1129-1266` `run_killer` (`run_killer(killer, module, work, label)`): the killer bodies moved out of the
  test unchanged except `mutant.`→`module.`, `tmp_path`→`work`, `mutant_name`→`label` (generated by script, a guard asserted no
  other `mutant` identifier remained). `:1270-1299` `test_required_mutants_are_killed`: the killer runs on the UNMUTATED module
  first in `tmp_path/baseline` and must pass (else `pytest.fail("AF-AP-138: … fails on the UNMUTATED module …")`), then on the
  mutant in `tmp_path/mutant` inside `pytest.raises(AssertionError, match=mutant_name)`. Source: row `AF-AP-138`
  (`docs/INCIDENT-LOG.md@2b13ced:573`: "each killer run once on the unmutated module and required to pass, then on the mutant").
- RED→GREEN in the scratch copy (HEAD + test file), the registry's own shape (a killer pin gone stale), `2957`→`2958` in the
  `test_real_claude_split_counts_and_class_file` killer, 2026-09-24T02:44:43Z:
  A, OLD harness: `1 passed, 50 deselected in 1.61s` (the hollow kill, reproduced).
  B, NEW harness: `E           Failed: AF-AP-138: test_real_claude_split_counts_and_class_file fails on the UNMUTATED module, so
  a kill of blob-sha-without-git-header is not attributable to the mutation: AssertionError('blob-sha-without-git-header\nassert
  2957 == 2958')` / `1 failed, 50 deselected in 1.86s`.
- The control's first real catch (02:44:54Z, NEW harness, no injected pin): `FAILED …[unsorted-tree-digest-<lambda>-
  test_walk_is_sorted_before_digest]` / `1 failed, 10 passed, 40 deselected in 35.56s` — `Failed: AF-AP-138:
  test_walk_is_sorted_before_digest fails on the UNMUTATED module … assert ['', 'aaa/c.t..., 'zzz/d.txt'] == ['aaa/c.txt',...`.
  Proven at HEAD's own bytes (`/tmp/k150/head_check`): `HEAD module (unmutated): walk_tree -> ['', 'aaa/c.txt', 'b.txt',
  'zzz/d.txt']; HEAD killer's expectation holds: False` and `unsorted-tree-digest mutant: walk_tree -> ['', 'b.txt', 'aaa/c.txt',
  'zzz/d.txt']; HEAD killer's expectation holds: False`. fe2284d (2026-09-22T15:58:16Z, K1-g harvest) added the root record
  `("", b"dir")` to `walk_tree` and updated the direct test (`tests/test_vendored_manifest.py:918-920`), not the harness's copy.
  Fixed at `:1139-1146` by aligning the killer's list with the direct test's (`""` first).
- After: 02:46:27Z, `11 passed, 40 deselected in 43.51s` (every killer passes on the unmutated module, and every mutant is
  killed by its named assertion; the `unsorted-tree-digest` kill is now attributable: `''` then the mutant's `b.txt` first).

### (n) issue #60 finding 1: a committed test for `parse_classes`' malformed-row refusal — DONE
- `tests/test_vendored_manifest.py:651-679` `test_malformed_claude_class_row_is_refused_by_line`, two shapes: `unknown-class`
  (line 2's class cell → `BROKEN-CLASS`, VERIFY-K1-h's probe) and `no-tab` (a row with no tab appended, the brief's premise
  probe). A clean fixture passes `--check` first (`EXPECTED_PASS`), then the malformed file must give rc 1 and
  `FAIL: .claude class file parse failure at line <n>\n` in stderr (the `\n` pins the exact number). `scripts/vendored_manifest.py`
  untouched. Source: `tasks/briefs/kit-k1-support/VERIFY-K1-h-report.md:146-160,181` (v-D, v4, the live-guard probe).
- v-D and v4 rebuilt on the scratch copy (`/tmp/k150/n_mutants.py`, 2026-09-24T02:47:53Z), the unmutated script first:
```
unmutated: rc=0 2 passed, 51 deselected in 11.06s
v-D (the row refusal swallowed: klass = first-party): rc=1 2 failed, 51 deselected in 9.97s
    E       AssertionError: ('unknown-class', 'FAIL: .claude class drift: agents/adversarial-verifier.md: committed=first-party generated=kit-adapted
    E       assert 'FAIL: .claude class file parse failure at line 2\n' in 'FAIL: .claude class drift: agents/adversarial-verifier.md: committed=first-party generated=kit-adapted\n'
v4 (parse_classes a no-op returning {}): rc=1 2 failed, 51 deselected in 6.82s
    E       AssertionError: ('unknown-class', 'FAIL: .claude class drift: byte length differs
    E       assert 'FAIL: .claude class file parse failure at line 2\n' in 'FAIL: .claude class drift: byte length differs\n'
scratch script restored to HEAD: True
```

## Twin and manifest steps (the brief's order, steps 3-5; 2026-09-24T02:49Z)

- Step 3. `bash harness-ports/bin/sync-skills.sh --check` before `--record`: `STALE-BASE: anti-hollow-green`,
  `STALE-BASE: build-loop`, `STALE-BASE: orchestration`, rc=1 (exactly the three edited skills). `--record`:
  `sync-skills: recorded base hashes for 15 hand-ported skills in …/harness-ports/hand-ported.sha256`, rc=0. `--check`: rc=0,
  `sync-skills: .agents/skills is in sync with .claude/skills (410 skills)`. `git diff --stat -- harness-ports/hand-ported.sha256`:
  `1 file changed, 3 insertions(+), 3 deletions(-)` (anti-hollow-green 8b248b65…→58db02c1…, build-loop caf3471d…→f0508156…,
  orchestration a0153e8a…→079fa230…).
- Step 4. `bash harness-ports/bin/sync-lane-skills.sh --check` before: `DRIFT: build-loop`, `DRIFT: orchestration`,
  `DRIFT: anti-hollow-green`, rc=1. Run: `sync-lane-skills: synced 25 skills into .agents/lane-skills (3 changed)`, rc=0.
  `--check`: `sync-lane-skills: in sync (25 skills)`, rc=0. `cmp` of each `.agents/skills` twin with its `.agents/lane-skills` twin:
  identical ×3.
- Step 5. `python3 scripts/vendored_manifest.py --check` before `--write`: `FAIL: vendored manifest drift: line 20:` (the
  `.claude/ (kit-adapted)` row only, tree `bc6af574…` → `0516bdc2…`), rc=1. `--write`: `WROTE sandbox-kit/VENDORED-MANIFEST.md (9
  roots)`, `WROTE sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv (3101 paths)`, rc=0. `--check`: `PASS: sandbox-kit/VENDORED-MANIFEST.md
  matches 9 vendored roots`, rc=0.
- The diff: `sandbox-kit/VENDORED-MANIFEST.md` changes three lines only: `Generated from commit` (d116e3d… → b74b63b…, HEAD at
  the write; informational, the drift comparison ignores it), `Generated at (UTC)` (→ 2026-09-24T02:49:41.625109Z), and the
  `.claude/ (kit-adapted)` row's tree SHA-256 (`bc6af5743d45…` → `0516bdc2c093…`; files 15, symlinks 0, unchanged).
  `sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv`: NO diff. No class changed: all four `.claude` files stay `kit-adapted`.
- HEAD moved during the lane to b74b63b (coordinator commits 7ddcd2e … b74b63b, ledger/wiki/STATUS/incident);
  `git diff --stat a10a012 HEAD -- <the boundary>`: empty, rc=0.

## Gates (every command with its output; final tree)

```
$ /root/venv-agent-factory/bin/python -m pytest tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py -q -p no:cacheprovider
173 passed in 129.67s (0:02:09)          (run 1, 2026-09-24T02:50:21Z, rc=0)
173 passed in 160.85s (0:02:40)          (run 2, 2026-09-24T02:52:35Z, rc=0)
$ bash scripts/pc_suite.sh set-id -- tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py
2 files set=2a60fb528bf2
```
The two runs agree; PIN `152 passed` on the same set; +21 = 19 in the hook file (2 for (m), 6 for (d2), 4 for (g), 5 for
(k′), 2 for (f)) + 2 in the manifest file ((n), two shapes). (b) adds no item: 11 mutant rows before and after.
```
$ /root/venv-agent-factory/bin/python -m pytest tests/test_hooks_worktree.py -q -p no:cacheprovider
2 passed in 0.13s                        (2026-09-24T02:55:21Z, rc=0)
$ bash harness-ports/tests/run-all.sh    (2026-09-24T02:55:26Z → 02:56:51Z, rc=0; last lines)
test_codex_hook_adapter.py         7/7 passed
test_hermes_hook_adapter.py        6/6 passed
test_hermes_spool.py               9/9 passed
…
test_context_mirrors.sh            11 passed, 0 failed
test_sync_skills.sh                34 passed, 0 failed
build-roles --check                OK: 3 role config layers match their sources

ALL SUITES PASSED
$ /root/venv-agent-factory/bin/python -m pyflakes .claude/hooks/edit-snapshot.py tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py
(no output) rc=0
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 40 files scanned, clean
rc=0
$ python3 scripts/ap_screen.py .claude/hooks/edit-snapshot.py
--- AP_SCREEN over 1 path(s): 19 hits over 1 files ---     (rc=0)
```
The self-screen gives the same 19 hits, of the same classes and texts, as the unedited hook (`diff` of the hit lines with line numbers
normalized: empty, rc=0): the lane's rows cause NO new hit in the hook. Its one AF-AP-159 hit is the PIN comment
"`node.start_mark.line + k`".

Per new row, the lines it fires on across `scripts/ src/ proofs/ harness-ports/` (git ls-files, whole-text finditer, the hook's
own compiled rows; `/tmp/k150/final_counts.py`):
```
AF-AP-139: 1 lines over scripts/ src/ proofs/ harness-ports/ (1 in .py)
    harness-ports/tests/test_pc_bridge_exec.py:20
AF-AP-25: 4 lines over scripts/ src/ proofs/ harness-ports/ (4 in .py)
    proofs/S0-01/check_acp_conformance.py:1102
    proofs/S0-01/tools/archive/build_capture_record_v1.py:34
    scripts/vendored_manifest.py:759
    scripts/vendored_manifest.py:798
AF-AP-89: 1 lines over scripts/ src/ proofs/ harness-ports/ (0 in .py)
    scripts/pc_lane.sh:292
AF-AP-159: 0 lines over scripts/ src/ proofs/ harness-ports/ (0 in .py)
AF-AP-139 (TEST_SCREEN twin, context only): 5 lines over tests/
    tests/test_edit_snapshot_ap_screen.py:505
    tests/test_edit_snapshot_ap_screen.py:523
    tests/test_s0_05_egress.py:917
    tests/test_s0_05_egress.py:1061
    tests/test_s0_05_egress.py:3511
```
Classification: AF-AP-139 `test_pc_bridge_exec.py:20` is the bridge stand-in the registry's sweep reviewed (AF-AP-139 row). AF-AP-25
`vendored_manifest.py:759/:798` are the two OPEN BUG sites (task #170). `check_acp_conformance.py:1102` is a log scan whose window
reaches a post-loop single-value `re.match` (a tell, reviewed: it fails closed). The `archive/` file is retired tooling. AF-AP-89
`pc_lane.sh:292` is reviewed-safe (D-6). The `tests/` hits: 2 are this lane's own fixtures, `:917`/`:1061` the reviewed DEVICE
handlers, and `:3511` is unclassified (D-8). No row floods.
- GitNexus `node .gitnexus/run.cjs detect-changes --scope all --repo .`: `Changes: 16 files, 62 symbols` / `Affected processes: 0` /
  `Risk level: low`. This covers the whole shared tree, including J1-3-R1's files.
- `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/kit-k1-support/K150-report.md` (fix round 1 of at most 3: every
  incident-log ref pinned `@2b13ced`, the on-origin revision it was measured at, because 8383313 prepended an entry
  mid-lane; a claim token added per MISS line): `report_lint: 70 refs — OK 41, NEAR 0, MISS 0, UNCHECKABLE 29, UNRESOLVED 0
  (worktree)`, rc=0. Round 0 was `70 refs — OK 15, NEAR 1, MISS 21, UNCHECKABLE 33`.

## Self-attack (the three likeliest ways this change is wrong)
1. A screen row passes its fixtures but never fires where its class lives (a hollow row). Ruled out per row by measurement: each
   positive fixture is the registry's real instance (the S0-05 listener byte-identical to `76f439f^:1579-1583`, the `parse_sbom` /
   `parse_lock` loops, T94's probe line). Each regex fires on the real tree where the class is (AF-AP-25 on both BUG sites; AF-AP-89
   on the one bridge doubled-escape shape). The AF-AP-139 row is also in TEST_SCREEN, because the hook applies only that list to
   `/tests/` (D-5). All 8 regex mutants are killed by a named fixture.
2. The (b) harness change weakens the kills (a renamed variable no longer reaches its mutant, a shared tmp dir leaks state
   between the baseline and mutant runs). Ruled out: the move was generated with a guard (no stray `mutant` identifier), each run
   gets its own directory, the stale-pin negative control reds on the NEW harness and passes on the OLD one, and all 11 rows pass
   with every killer first green on the unmutated module.
3. The (f) fix only moves the crash (another venv probe raises, or `main` still dies). Ruled out: every `_VENV_PY` use is
   listed (`:311`, `:333`, and the `_pyflakes_msgs` calls at `:340-341`), each probe kind has a test (the second de-vacuoused by a
   mutant), and the real kernel refusal as uid 65534 gives rc=0 with the fixed hook against rc=1 with HEAD's.

## NOT-done
- NOT run here: `harness-ports/tests/run-all.sh` in a bare NON-ROOT PC shell without `AF_VENV` (the registry's original symptom
  for (f)). The brief forbids bridge use. The sandbox's uid-65534 hook run is the stand-in (real kernel refusal; rc 1 → 0).
- NOT done (out of boundary; for the coordinator): the registry updates D-2 (AF-AP-155's glob), D-3 (AF-AP-140's status) and D-10
  (AF-AP-138's second instance); the classification of D-8; the misplaced AF-AP-118 comment (D-7); the D-9 probe.
- NOT added: v-D and v4 as permanent `MUTANTS` rows (the brief asked for scratch rebuilds only; both are RED against the new test).
- The new screen rows' RED side is proven by regex mutants, not by a run with the row absent (a missing row is a `KeyError` at
  class creation, which proves nothing about the fixtures).
- No commit, no push, no outward action (the coordinator commits).

## DISCREPANCIES

- D-1 (brief item (l), attribution). The brief ties the timing-strip rule to "VERIFY-J1-3's first stop". The lane's stop report
  (`tasks/briefs/pc/report-pc-verify-j1-3.md--e8db82c.md:15-22`) names only the pre-push SHAs and the retyped grep. The timing
  instance is in the same block (first brief at 3184014, lines 77-78: `33 passed in 12.09s` under an unstripped command). It was
  fixed in the re-measured block (`tasks/briefs/pc/pc-verify-j1-3.md:79`, 1cfc8f1) but not named by the lane. The bake says exactly
  this; no contract line changes.
- D-2 (adjacent, registry row AF-AP-155, READ-ONLY here). The row's brief-time grep reads `proofs/*/fixtures/PROVENANCE.md`, a glob
  that matches 1 of the 15 proof PROVENANCE files (`git ls-files 'proofs/*PROVENANCE*' | wc -l` → 15, e.g.
  `proofs/S0-03/fixtures/evidence-stub-route/PROVENANCE.md`, `proofs/S0-06/evidence/PROVENANCE.md`). The bake uses
  `$(git ls-files 'proofs/*PROVENANCE.md')`, as the brief asks ("every PROVENANCE file"). The row is not edited.
- D-3 (adjacent, registry row AF-AP-140, READ-ONLY here). The row's status still reads "OPEN — task #167", while CLAUDE.md records
  the fix as landed and verified (T94 = tasks #167 + #200, VERIFY-T94-R1 MERGE-READY-WITH-FOLLOWUPS). The row is not edited.
- D-4 (brief citation, cosmetic). Item (j) cites the recovery paragraph as `.claude/…/SKILL.md:429-435`. At the PIN, the RESTART
  sentence spans `:429-432`, and `:434-435` are item (e) of the ORCHESTRATOR protocol. The QUOTA STOP form went into the paragraph.
- D-5 (DEVIATION BY ADDITION, item (d2); flagged loudly). The brief places the rows in `AP_SCREEN`. The AF-AP-139 row IS in
  `AP_SCREEN` (`.claude/hooks/edit-snapshot.py:210`), and the SAME tuple is also in `TEST_SCREEN` (`:297`). Reason, measured:
  the hook screens every `/tests/` path with `TEST_SCREEN` only (`main`, `:445-454`), and the class lives in tests. The
  registry's instance is `tests/test_s0_05_egress.py`, and the row's only hit over `scripts/ src/ proofs/ harness-ports/` is
  itself a `/tests/` path (`harness-ports/tests/test_pc_bridge_exec.py:20`, `do_POST`). An `AP_SCREEN`-only row would fire on 0 lines that
  the hook screens with `AP_SCREEN`: a row whose claimed part never runs (anti-hollow-green tactic 7). No contract line
  forbids the twin. The coordinator can drop it by deleting one line (`:297`) and the one identity test (`tests/test_edit_snapshot_ap_screen.py:515-517`, `test_the_same_row_screens_tests`); the
  `AP_SCREEN` row stays.
- D-6 (item (k′), one reviewed-safe hit). The brief's exact signature (`\\$(` or `\\\"`) fires on `scripts/pc_lane.sh:292` (`EFF_STATE`). The
  `\\\"` there sits inside a QUOTED heredoc (`<<'PY'`) within the bridge argument. The PC does not expand the heredoc body, so
  Python receives `lstrip('\" :=')` as intended: correct code. The row is kept as the brief specifies, the one legitimate form
  is named in its message, and the count below lists this hit.
- D-7 (adjacent, hook, not fixed). The AF-AP-118 comment (`.claude/hooks/edit-snapshot.py:195-197`) is separated from its row
  (`:208`) by the AF-AP-127 and AF-AP-159 rows (`:198-206`). This was present at the PIN, and the lane changed no line of it.
- D-8 (adjacent, unclassified hit of the new AF-AP-139 row). `tests/test_s0_05_egress.py:3506-3513`, `RELAY_LOG_SERVER` (A2'',
  commit a840943, 2026-09-23 23:20Z, after the registry's sweep), answers 200 on every path. The lane did not measure what
  that test's C0 asks. The coordinator or a verifier classifies it: the registry's other two S0-05 hits (`:917`, `:1061`) are
  the DEVICE handlers it reviewed.
- D-9 (adjacent, hook, outside (f)'s scope). `gitnexus_impact`'s `except` branch probes
  `Path("/tmp/gitnexus-analyze.lock").exists()` (`.claude/hooks/edit-snapshot.py:430`) outside any `try`, the self-screen's
  AF-AP-40 hit. It is not a venv-path probe; `/tmp` is world-traversable, so a raise there is unlikely but uncaught. Not changed.
- D-10 (item (b), a finding the new control made; FIXED in the boundary because the control's gate cannot pass without it). The
  `unsorted-tree-digest` mutant row has been a HOLLOW kill since fe2284d (2026-09-22): its killer expected `walk_tree`'s list
  without the root record `""`, so it failed on the unmutated module too (proven at HEAD's bytes, (b) above). Registry row
  `AF-AP-138` (`docs/INCIDENT-LOG.md@2b13ced:573`, READ-ONLY here) says its sweep "found no other instance". This is a second instance in
  the SAME harness: the shape is a killer's copied expectation left stale when the producer changed. The coordinator owns the
  registry update and any bug-echo of that shape beyond this file. The fix changes only the killer's expected list, to the direct
  test's (`tests/test_vendored_manifest.py:920`); the mutant stays killed (its unsorted order puts `b.txt` before `aaa/c.txt`).
