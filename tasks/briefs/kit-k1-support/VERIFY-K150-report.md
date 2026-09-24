# VERIFY-K150 report — independent verify of the K150 kit edits (task #213 verifies task #150)

PIN: 656ddf6. Venue: sandbox, uid 0 (plus uid 65534 runs for item 6), shared tree read-only, scratch `/tmp/vk150/`.
Model: Opus 5.5 (claude-opus-5-5). Honey `full`. Started 2026-09-24 03:27:33 UTC (pasted from `date -u`).

STATUS: DONE — all eleven items run fully (item 5 by the brief's read-from-code method). Recommendation (the one line is below the predicate table): MERGE-READY-WITH-FOLLOWUPS (no finding meets the whole blocking predicate; follow-ups F-01..F-08; the coordinator owns the gate).

## Item 1 — PREMISE (RUN FULLY)

- Shared tree at run time: HEAD `5bfc8f6`, origin `a923be5`; `git status --short` showed only `?? tasks/briefs/laya/VERIFY-J1-3-R1-report.md`
  (another lane's report), so every tracked boundary file in the working tree equals HEAD.
- The brief's 13 commands, copied verbatim into `/tmp/vk150/premise_cmds.txt`, run as
  `bash scripts/premise_block.sh < /tmp/vk150/premise_cmds.txt` (2026-09-24T03:28:18Z to 03:31:02Z, `premise_block rc=0`,
  `PYTHONDONTWRITEBYTECODE=1` exported so the run left no `.pyc` in the tree).
- Comparison: the brief's fenced block extracted with `awk` into `/tmp/vk150/premise_brief.txt`, then
  `diff /tmp/vk150/premise_brief.txt /tmp/vk150/premise_out.txt` → no output, `diff rc=0` (59 lines each).
  Key lines reproduced: `pin-is-on-origin`, `boundary-identical-to-pin`, `173 passed`, `2 files set=2a60fb528bf2`,
  `PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots`, both sync checks `rc=0`,
  `--- AP_SCREEN over 1 path(s): 19 hits over 1 files ---`.
- Verdict: the premise MATCHES on every line. No CONTRACT-INVALID stop.
- During the run HEAD moved to `f7a393f` (coordinator commits 2aab702, cf1da87, f7a393f: registry and ledger only).
  Re-checked: `git diff --quiet 656ddf6 HEAD -- <the 15 boundary paths>` → `boundary-identical-to-pin`. Registry rows below are
  read at the PIN (`git show 656ddf6:docs/INCIDENT-LOG.md > /tmp/vk150/incident_pin.md`), as the brief says.
- Private clone: `git clone -q --shared /home/user/agent-factory /tmp/vk150/clone && git -C /tmp/vk150/clone checkout -q --detach 656ddf6`
  → `656ddf6`, clean, 201M.
- Code intel: `scripts/lane_context.sh … -o /tmp/vk150/pack.md` rc=0 (275 lines). graft has NO index for `.claude/hooks/`
  (`graft skeleton` → `no definitions indexed for this file`; `graft ask` → `✗ nothing indexed under ".claude/hooks/"`), so the
  hook was read whole (fallback named). crg `callers_of pyflakes_delta` → `main` + the two new tests.

## Item 2 — SKILL BAKES (RUN FULLY)

Method: `git show 656ddf6 --format= -- <file>` for each of the six skill files; each cited fact checked against its primary
source at the PIN.

| Bake | Location at PIN (.claude / .agents) | Cited facts checked against | Result |
|---|---|---|---|
| (a) build-loop | `.claude/skills/build-loop/SKILL.md:78` / `.agents/skills/build-loop/SKILL.md:86` | `scripts/ci_gate.py:1-45` (exit table: `1 refused, the verdict run is red`, `75 wait`, `--wait SECONDS`), `scripts/push_clean.sh:64` (`git fetch origin "$BRANCH"`) then `:88` (`python3 … ci_gate.py`), `:299` (`--wait 1800` hint); row AF-AP-126 (`incident_pin.md:563`: "eleven red runs unread"; ci_gate docstring: "twice the coordinator forgot it") | TRUE |
| (d1) anti-hollow-green | `:129` in both | row AF-AP-139 (`incident_pin.md:576`): C0 `GET /v1/models`, real OmniRoute 401, relay 404, per-path status + 401 negative control | TRUE |
| (l′) anti-hollow-green | `:130` in both | row AF-AP-162 (`:599`), narrative `incident_pin.md:30-31` (T2 `pc_lane dispatcher: 42 passed, 0 failed`) | TRUE, one imprecision (F-12) |
| (e) orchestration | `.claude :301` / `.agents :314`, both inside `## Parallel agents, liveness, coordinator economy` (`:258` / `:271`, next heading `:303` / `:316`) | row AF-AP-140 (`:577`): 07:14Z, `LANE FAILED` from the 04:03Z loop, false capacity claim corrected before push | TRUE |
| (h) orchestration 0e′ | `.claude :92` / `.agents :100` | ledger `todo/BUILD-TASKLIST.md:120` ("B9's inputs: `revoked.json` signer → `owner2` (`expected_pubkey` = its pub), `neg-unauthorized.json` `expected_pubkey` → the nonmember pub"; the bake's `…` elides the parenthesis); row AF-AP-155 (`:592`). The bake's grep run at the PIN: `todo/BUILD-TASKLIST.md:120:…` rc=0; `git ls-files 'proofs/*PROVENANCE.md' \| wc -l` → `15` (the row's `proofs/*/fixtures/PROVENANCE.md` → `1`) | TRUE; the grep omits two of the row's phrasings (F-13) |
| (i) orchestration 0d″ | `.claude :69-73` / `.agents :77-81` | `tasks/briefs/laya/VERIFY-J1-1-R1-report.md:538-539` (option B, lookahead `(?![\"']?\s?[:=])`); D-057 (`docs/08_DECISION_LOG.md:68`: "it opens a NEW leak (`Authorization: Bearer <token>: rejected` keeps the token)") | TRUE |
| (l) orchestration 0d′ | `.claude :58-63` / `.agents :66-71` | `git show 3184014:tasks/briefs/pc/pc-verify-j1-3.md` (`… \| tail -1   (set 87e28761f102)` / `33 passed in 12.09s`); stop report `tasks/briefs/pc/report-pc-verify-j1-3.md--e8db82c.md:15-22` (names the commits `e8db82c2`, `3a455682` and the grep only); `git show 1cfc8f1:tasks/briefs/pc/pc-verify-j1-3.md:79` (`… \| sed -E 's/ in [0-9.]+s.*//'` / `33 passed`) | TRUE |
| (k) orchestration 0f | `.claude :106-112` / `.agents :114-120` | ledger `:1375` (VERIFY-C2: "served ENTIRELY by antigravity/gemini-3.1-pro-low, 29 calls … MERGE-READY-WITH-FOLLOWUPS, but its §6 mutants were reasoned … issue #56"); ledger `:1384` ("The 4.7 KB report skipped item 2's races … pasted no harvest lines"); `:1387` (R2 NOT-READY, four blockers); row AF-AP-170 (`:607`) | TRUE |
| (j) orchestration recovery | `.claude :452-458` / `.agents :446-467` | incident `incident_pin.md:40` (HTTP 429 weekly limit, S198A "final gates run at 16:28Z"), `:359` (third stop, HTTP 429); ledger `:1361` ("proved its final blob 37d94bd AST-identical to 515d78b … comments only"), `:1362` (VERIFY-S198A on the PC) | TRUE |

Twins (measured):
- Added-line overlap per skill (`git show 656ddf6 -- <file> \| grep '^+'`, then `grep -v -x -F -f`):
  `build-loop: claude_added=1 agents_added=1 claude_lines_not_in_twin=0 twin_lines_not_in_claude=0`;
  `anti-hollow-green: claude_added=2 agents_added=2 claude_lines_not_in_twin=0 twin_lines_not_in_claude=0`;
  `orchestration: claude_added=28 agents_added=43 claude_lines_not_in_twin=0 twin_lines_not_in_claude=15`.
  So every twin hunk is a BYTE COPY of its `.claude` hunk; the 15 extra twin lines are (j)'s ported recovery text (F-11).
- `.agents/lane-skills/` = twin at the PIN (blob ids): build-loop `31664195a989 31664195a989`, anti-hollow-green
  `172709f592e7 172709f592e7`, orchestration `934a156679f6 934a156679f6`; and the premise's `sync-lane-skills-check rc=0`.
- (j) whole paragraph in the twin: before K150 the twin's (d) paragraph ended at `re-running from scratch.`
  (`git show 656ddf6^:.agents/skills/orchestration/SKILL.md` line 427, then the blank line and `(e)`), while `.claude` continued
  with `**A user-STOPPED agent cannot be resumed at all**` (line 418). At the PIN a word diff of the paragraph from
  `**A user-STOPPED` to `AST-identical to 515d78b).` differs only in `sandbox` (twice) and `SendMessage:` → `to resume it:`
  (337 vs 341 words). The whole paragraph is there. The report's cause is true: `06b1d24` (2026-09-03) took the twin's
  `user-STOPPED` count from 1 to 0 while `.claude` kept 1.
- D-1 (graded ACCURATE): the stop report names only the SHAs and the retyped grep; the timing is in the first block at 3184014.
- D-4 (graded ACCURATE): `git show 033a9b0:.claude/skills/orchestration/SKILL.md` lines 429-432 hold the RESTART sentence,
  433 is blank and 434-435 are `(e) **Commit at every boundary…`.

## Item 3 — SCREEN ROWS (RUN FULLY)

Instrument: the REAL consumer, `scripts/ap_screen.py` at the PIN (it loads the clone's `.claude/hooks/edit-snapshot.py`), over every
tracked file of the four directories and, for TEST_SCREEN, over `tests/` and `harness-ports/tests/`:
```
$ python3 scripts/ap_screen.py --limit 100000 $(git ls-files scripts src proofs harness-ports)      (in /tmp/vk150/clone, rc=0)
--- AP_SCREEN over 955 path(s): 322 hits over 955 files ---
AF-AP-25: 4        AF-AP-139: 1        AF-AP-89: 1        (AF-AP-159: no line — 0 hits)
$ python3 scripts/ap_screen.py --tests --limit 100000 $(git ls-files tests harness-ports/tests)    (rc=0)
--- TEST_SCREEN over 114 path(s): 154 hits over 114 files ---
AF-AP-139: 6
```
The builder's counts (`AF-AP-139: 1`, `AF-AP-25: 4`, `AF-AP-89: 1`, `AF-AP-159: 0`, TEST_SCREEN twin 5 over `tests/`) REPRODUCE.

### (i) Each row on the registry's own instances (the consumer, on files extracted from history into `/tmp/vk150/inst/`)
```
== --tests test_s0_05_egress_prefix.py      (git show 76f439f^:tests/test_s0_05_egress.py — before E3-b)
AF-AP-139: 3   …prefix.py:782: def do_GET(self):   …:926: "    def do_GET(self):\n"   …:1580: "    def do_GET(self):\n"
== --tests test_s0_05_egress_fix.py         (git show 76f439f:… — E3-b's fix)
AF-AP-139: 2   …fix.py:789   …fix.py:933          (the two DEVICE handlers the registry reviewed; the fixed _listener is quiet)
== no_laya_r5.py                            (git show d116e3d^:scripts/no_laya_in_gates.py)
AF-AP-159: 1   …no_laya_r5.py:521: runs.append((value.start_mark.line + (2 if value.style in ("|", ">") else 1), value.value,
== no_laya_r6.py                            (git show d116e3d:… — the fix): no AF-AP-159 line
== t94.diff                                 (tasks/briefs/pc/patch-pc-t94.md--feb26d7.diff)
AF-AP-89: 1    t94.diff:262: +  probe="$(bridge "(! test -f $PC_AF_REPO/.lanes/$LANE_ID/FAILED …
```
Line 262 holds all four doubled `\\$(` and the `\\\"` of T94's probe in ONE bridge argument (`grep -o -F '\\$(' | wc -l` → `4`), so
one hit covers the instance. AF-AP-25's two named instances are the two hits at `scripts/vendored_manifest.py:759` (`parse_lock`, `for line_number, line in enumerate`)
and `:798` (`parse_sbom`), still OPEN (task #170). Every row fires on every instance its registry row names, and not on the fixes.

### (iii) Every hit classified
| Row | Hit | Class |
|---|---|---|
| AF-AP-139 | `harness-ports/tests/test_pc_bridge_exec.py:20` (`do_POST`) | signature TRUE (always 200); class reviewed-safe by the registry's sweep (the bridge stand-in, `incident_pin.md:576`) |
| AF-AP-139 (TEST) | `tests/test_edit_snapshot_ap_screen.py:505`, `:523` | the row's own positive fixtures (`do_GET`, `do_POST`) |
| AF-AP-139 (TEST) | `tests/test_s0_05_egress.py:917`, `:1061` | signature TRUE (`do_GET`); the DEVICE handlers the registry reviewed (`:790`/`:934` at its sweep) |
| AF-AP-139 (TEST) | `tests/test_s0_05_egress.py:3511` | signature TRUE (`do_GET`); class: see item 5 (D-8) |
| AF-AP-25 | `scripts/vendored_manifest.py:759`, `:798` | TRUE: the two OPEN bug sites (`line_number`) |
| AF-AP-25 | `proofs/S0-01/tools/archive/build_capture_record_v1.py:34` | TRUE for the class (`p.read_text().splitlines()`, `manifest_summary` keeps a BASELINE key or a timestamp line and skips any other line), in retired archive code the bug-echo excluded |
| AF-AP-25 | `proofs/S0-01/check_acp_conformance.py:1102` | FALSE POSITIVE: the loop (`for log_line in log_text.splitlines()`) body is a substring test (`if "buzz-acp starting:" in log_line`); the `re.match` at `:1110` runs AFTER the loop on one value and fails closed (`raise Failure`). The 400-char window crosses the dedent |
| AF-AP-89 | `scripts/pc_lane.sh:292` (the `\\\"` at `:305`) | FALSE POSITIVE on correct code (`EFF_STATE`), proven by execution (item 4, D-6) |

No row floods: 6 production hits and 6 test hits in total. The builder's classifications all REPRODUCE.

### (ii) Near misses — `/tmp/vk150/nearmiss.py` (41 shapes the builder's fixtures do not hold, against the PIN's compiled rows)
```
$ /root/venv-agent-factory/bin/python /tmp/vk150/nearmiss.py /tmp/vk150/clone
AF-AP-139  A1 return annotation `-> None`                        expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-139  A2 HTTPStatus.OK                                      expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-139  A3 message argument                                   expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-139  A4 delegation to a helper                             expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-139  A5 alias do_GET = handler                             expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-139  A6 send_response_only                                 expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-139  A7 body longer than 1000 chars                        expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-139  A8 if on the METHOD only (answers 200 on every path)  expected=FIRE  got=FIRE  agree
AF-AP-139  A9 unrelated if on the path, then 200 for all         expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-139  A10 a COMMENT naming if/self.path                     expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-139  A11 CLEAN: branch on a path variable                  expected=QUIET got=FIRE  FALSE-POSITIVE
AF-AP-139  A12 CLEAN: match statement on the path                expected=QUIET got=FIRE  FALSE-POSITIVE
AF-AP-139  A13 CLEAN: route table lookup then if                 expected=QUIET got=FIRE  FALSE-POSITIVE
AF-AP-139  A14 CLEAN: guard clause on the path                   expected=QUIET got=QUIET agree
AF-AP-25   B1 split('\n') loop                                   expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-25   B2 for line in fh (open on the with line)             expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-25   B3 for line in lines (split earlier)                  expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-25   B4 re.search in the loop                              expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-25   B5 black-wrapped loop header                          expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-25   B6 compiled pattern (documented limit)                expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-25   B7 the REFUSING form (task #170's fix shape)          expected=QUIET got=FIRE  FALSE-POSITIVE
AF-AP-25   B8 re.match AFTER the loop ends (window crosses the dedent) expected=QUIET got=FIRE FALSE-POSITIVE
AF-AP-89   C1 doubled backtick                                   expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-89   C2 doubled escape before a variable                   expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-89   C3 doubled escape after a nested quote in $( )        expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-89   C4 through the pc() helper (realleg_sync.sh)          expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-89   C5 through pc_bridge_exec.py                          expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-89   C6 bridge argument opens after a flag                 expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-89   C7 CLEAN: triple escape for a nested remote bash -c   expected=QUIET got=QUIET agree
AF-AP-89   C8 CLEAN: single escape                               expected=QUIET got=QUIET agree
AF-AP-89   C9 CLEAN: a doubled escape in a SINGLE-quoted bridge argument expected=QUIET got=QUIET agree
AF-AP-89   C10 CLEAN: a comment line naming the bad form         expected=QUIET got=FIRE  FALSE-POSITIVE
AF-AP-159  D1 CLEAN: + inside a subscript                        expected=QUIET got=FIRE  FALSE-POSITIVE
AF-AP-159  D2 minus                                              expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-159  D3 two-line alias                                     expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-159  D4 parenthesized right operand                        expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-159  D5 augmented assignment                               expected=FIRE  got=QUIET FALSE-NEGATIVE
AF-AP-159  D6 CLEAN: lineno of an ast node                       expected=QUIET got=QUIET agree
AF-AP-159  D7 CLEAN: start_mark.column                           expected=QUIET got=QUIET agree
AF-AP-159  D8 f-string display line                              expected=FIRE  got=FIRE  agree
AF-AP-159  D9 CLEAN: string concat of a label                    expected=QUIET got=QUIET agree
cases=41 agree=9 disagree=32
```
("expected" is my reading of each registry row's scope. The cases are synthetic; what matters is whether they occur in the tree.)

Real-tree check of the misses (does any in-scope spelling exist in the tree that the row does not fire on?):
- AF-AP-139: every `def do_[A-Z]+(` / `do_X =` definition outside the vendored trees (`git grep`, 14 in code) was read. The
  unfired ones branch on the path (`harness-ports/tests/test_qwen_matrix.py:82,109`, `scripts/laya_systemone_server.py:161,170`,
  `proofs/S0-01/tools/scripted_backend.py:720,745`, `tests/test_s0_06_four_scope.py:98,117`, `tests/test_s0_05_egress.py:1729`), send
  a 401 always (`tests/test_proof_runner.py:320`, `tests/test_s0_03_omniroute.py:1541`), or hold the status in a variable:
  `tests/test_s0_03_omniroute.py:856-866` (`status = 200`, `self.send_response(self.status)` on every path). That one is set per
  test (`_serve(200/401/403/500)`, `:896-906`) to exercise the probe's HTTP-status taxonomy, so it is class-safe. It shows the
  literal-only row, like the registry's own `send_response(200)` sweep, cannot see a status held in a variable (F-06).
- AF-AP-25: the bug-echo's candidates (`docs/research/bug-echo/2026-09-23-bug-echo-fail-open-line-parser.md`): both BUG sites
  fire; the WATCH site (`scripts/vendored_manifest.py:667` at the PIN, `if not line.startswith("|")`; the bug-echo's `:506` is an older revision's line) and the REVIEW site
  (`proofs/S0-01/tools/build_capture_record.py:39`, `for line in text.splitlines()` then `startswith("## ")`) use no regex, so quiet is right. The row is Python-only;
  the bug-echo's shell form (`while … read`) is not screened (the hook never screens `.sh`). No in-class site is missed at the PIN.
- AF-AP-89: every doubled escape in tracked `.sh` files (`git grep -F '\\$'` → 2 lines, `'\\\"'` → 4 lines): both `\\$` lines are
  comments (`harness-ports/tests/test_pc_lane_dispatcher.sh:417` `ever EXECUTED the probe`, `scripts/pc_lane.sh:388` `ON THE PC`); the `\\\"` lines are systemd quoting
  (`harness-ports/bin/qwen-server.sh:130`), test strings (`harness-ports/tests/test_qwen_server.sh:187,195`) and D-6
  (`scripts/pc_lane.sh:305`, the `reasoning_effort` read). The other bridge helpers (`pc_quiet`, `proofs/S0-01/tools/pc/run_leg.sh:12`; `pc`,
  `scripts/realleg_sync.sh:25`, `pc() { bash scripts/pc.sh`; `scripts/pc_bridge_exec.py`) carry no `\$(` at all (`git grep … | grep -c -F '\$('` → `0`); the one
  `pc "…"` call with a remote escape (`scripts/realleg_sync.sh:30`, `\$leg`) is single-escaped. No in-class site is missed at the PIN.
- AF-AP-159: 0 hits over the four directories; the registry's own sweep found no other YAML node-position line map.
- REACHABILITY of AF-AP-89 (measured): the hook's `main` returns at `.claude/hooks/edit-snapshot.py:443` for any path not ending in
  `.py`, `scripts/lint_delta.py:_changed` keeps only `.py`, and `scripts/ap_screen.py:_files` walks directories for `*.py` only.
  The row's class lives in `.sh` files, so it runs ONLY when a `.sh` path is named explicitly to `ap_screen.py` or to
  `scripts/lane_context.sh` (`:63`). The AF-AP-87 row documents this limit in its comment (`:293-294`); the AF-AP-89 row does not
  (F-04).

## Item 4 — D-5 and D-6 (RUN FULLY)

### D-5: the AF-AP-139 row also in TEST_SCREEN
- `main` routes by path: `if "/tests/" in fp:` → `TEST_SCREEN` only (`.claude/hooks/edit-snapshot.py:445-454`); production paths →
  `AP_SCREEN` (`:496-499`). Measured through the REAL `main` (`/tmp/vk150/d5/`): an Edit payload whose `new_string` is the pre-fix
  S0-05 listener, on `…/tests/test_standin.py` and on `…/harness-ports/tests/test_standin.py`, run with the PIN hook and with a copy
  whose only change is the deleted twin line (`diff` → `297d296 <     _AF_AP_139,  # the same row as in AP_SCREEN…`):
  ```
  pin_hook.py tests rc=0: 1 AF-AP-139 line(s); first: EDIT SNAPSHOT · test_standin.py
  pin_hook.py htests rc=0: 1 AF-AP-139 line(s); first: EDIT SNAPSHOT · test_standin.py
  no_twin_hook.py tests rc=0: 0 AF-AP-139 line(s); first:
  no_twin_hook.py htests rc=0: 0 AF-AP-139 line(s); first:
  ```
- But the commit-time path applies AP_SCREEN to TEST files: `scripts/lint_delta.py:_changed` keeps every changed `.py` outside
  the vendored trees (tests included) and screens its added lines with `AP_SCREEN` (`scripts/hooks/pre-commit:16` runs it `--staged`). In the
  private clone, a staged `tests/test_vk150_standin.py` with an always-200 `do_GET`:
  ```
  lint_delta (index vs HEAD): 1 .py changed, 0 NEW pyflakes hit(s), 0 removed
  anti-pattern screen (TELLS on added lines — verify each, advisory):
    AF-AP-139tests/test_vk150_standin.py: an HTTP stand-in that sends a literal 2xx with no branch on `self.path` — …
  lint_delta rc=0
  ```
  (then `git reset` + `rm` in the private clone; `git status --short` empty.) `scripts/lane_context.sh:63` (`ap_screen.py --tests` only for `tests/*`) also sends
  `harness-ports/tests/*` (not `tests/*`) through AP_SCREEN.
- Hits under the test trees at the PIN: 6 (item 3 table): 2 the row's own fixtures, 3 S0-05 handlers, 1 the bridge stand-in.
  The twin does not flood.
- GRADE: the deviation is NEEDED and sound: without it the edit-time hook and `ap_screen.py --tests` never apply the row to a test
  file, where the registry's instance lived. The builder's stated reason overreaches a little: "An `AP_SCREEN`-only row would fire
  on 0 lines that the hook screens" is true of the hook, but the row would still have run on test files at commit time through
  `lint_delta.py` (F-05, INFO).

### D-6: the AF-AP-89 hit at `scripts/pc_lane.sh:292`
- The bridge argument (`:292-308`) carries the `\\\"` at `:305` inside `python3 - "\$MP" <<'PY' … PY` (a quoted heredoc).
- RENDERED, not read: `/tmp/vk150/d6/render.sh` defines an ECHOING `bridge() { printf '%s' "$1"; }` and sources the PIN's
  `:292-308` (no bridge call). The rendered program holds `wanted = 'xhigh'`, `.split(b'\0')` and
  `.lstrip('\" :=').split('\"', 1)`; `bash -n` → `rc=0`.
- EXECUTED: the rendered program run with `bash`, a `systemctl` stand-in on PATH that prints the pid of a live
  `python3 … --chat-template-kwargs {"reasoning_effort": "xhigh"}`:
  ```
  argv of pid 18599: python3 -c import time,sys; time.sleep(60) --chat-template-kwargs {"reasoning_effort": "xhigh"}
  wanted=xhigh -> match
  wanted=medium -> mismatch:xhigh
  ```
- CONFIRMED: the PC receives the heredoc body verbatim and Python reads `'\" :='` as `" :=`, so the code is correct and the hit is
  the one legitimate form the row's message names.

## Item 5 — D-8, the unreviewed AF-AP-139 hit `tests/test_s0_05_egress.py:3506-3513`, `RELAY_LOG_SERVER` (RUN FULLY, from code; no bridge, no netns run)
- `RELAY_LOG_SERVER` (`:3506-3517`) logs each request through a descriptor it holds on `relay.log` and answers 200 on every path.
  Its one user is `_relay_log_server` (`:3565-3580`), called by `test_a2pp_a_log_its_holder_appends_during_the_leg_passes`
  (`:3614-3640`) through `_census_leg(e3dir, port, unit, serve=serve)`, which runs the `hermes-acp` unit's leg
  (`_run_runner(env, evidence, "hermes-acp", …)`).
- What C0 asks on that leg: `proofs/S0-05/tools/pc/run_s0_05_units.sh:547` sets `allowed=("$host_ip:$OMNI_PORT");
  probe_paths=("$OMNI_PROBE_PATH")` for every unit but `buzz-acp`, and `:96` sets `OMNI_PROBE_PATH=/api/health`. The preflight
  (`:580`, `_c0_preflight … "${probe_paths[$i]}"`) and the canaries (`:668-669` → `proofs/S0-05/run_canaries.sh:41-50` (`PROBE_PATHS`) →
  `proofs/S0-05/canaries/c0_allowed_target.sh:9-12`, `curl … "http://$target$path"`) both send `GET /api/health`.
- Would the real service refuse it? No. `/api/health` is the path E3-b measured the real OmniRoute answering 2xx on
  (`run_s0_05_units.sh:50-52`: "facts about the services on the PC today"; registry row AF-AP-139's fix note). The unit's own
  request (`UNIT_RELAY`, `:3603-3611`, `GET /unit-was-here` at `:3607`) has no graded status (`conn.recv(64)`, then the unit appends to `relay.log` itself).
  The test grades the census of the held log, and the real relay logs a request whatever its status.
- CLASSIFICATION: signature TRUE, class SAFE (not an AF-AP-139 instance). No graded request gets a 2xx the real service would
  refuse. D-8 can be closed as reviewed-safe, the same disposition as the registry's `:790`/`:934`.

## Item 6 — THE HOOK FIX (f), AF-AP-44 (RUN FULLY)

Every probe of the venv path in the PIN hook (`grep -n -E '_VENV_PY|AF_VENV|venv' .claude/hooks/edit-snapshot.py`):
- `:311` `_VENV_PY = os.environ.get("AF_VENV", "/root/venv-agent-factory") + "/bin/python"`: builds a string at import, no probe.
  The hook's in-process loaders (`scripts/ap_screen.py:25-29` `_load_screens`, `scripts/lint_delta.py:_ap_screen`, the tests) run only this.
- `:333` `Path(_VENV_PY).exists()`: inside the `try` (`:332-343`, `except Exception: return []`). Before K150 it was at `:300`,
  outside it.
- `:340` and `:341` `_pyflakes_msgs(_VENV_PY, …)` → `subprocess.run([py, "-m", "pyflakes"], …, timeout=PROBE_TIMEOUT)` (`:317-318`):
  inside the same `try`.
All three sit in the `try` that returns `[]`. The hook runs under `python3` from PATH (`.claude/settings.json:46`; here Python
3.11.15).

The builder's outermost-boundary pair, REPRODUCED through the real `main` on a real Edit payload as uid 65534 with `AF_VENV` unset
(`/tmp/vk150/f6/`: a scratch git repo with `mod.py`, the pre-fix hook from `git show 656ddf6^:…`, the PIN hook; `/root` is
`drwx------`):
```
== hook_prefix.py as uid 65534, AF_VENV unset
rc=1
  File "/tmp/vk150/f6/hook_prefix.py", line 300, in pyflakes_delta
    if not Path(_VENV_PY).exists():
PermissionError: [Errno 13] Permission denied: '/root/venv-agent-factory/bin/python'
== hook_pin.py as uid 65534, AF_VENV unset
rc=0
EDIT SNAPSHOT · mod.py
  impact  module-level edit (no enclosing symbol resolved)
  registry screen: no mechanical anti-pattern tells in this hunk
```

Probe failures the builder's tests do not raise, through the real `main` (root, `AF_VENV` → a crafted venv under
`/tmp/vk150/f6/v/`, each run bounded by `timeout 120` and timed):
```
dangling        hook_prefix rc=0     0.1s    registry screen: no mechanical anti-pattern tells in this hunk
dangling        hook_pin   rc=0     0.1s    registry screen: no mechanical anti-pattern tells in this hunk
loop            hook_prefix rc=0     0.1s    (ELOOP symlink)                     hook_pin rc=0 0.1s
dirinterp       hook_prefix rc=0     0.1s    (bin/python is a directory)         hook_pin rc=0 0.1s
noexec          hook_prefix rc=0     0.1s    (mode 0644 interpreter)             hook_pin rc=0 0.1s
enoexec         hook_prefix rc=0     0.1s    (garbage bytes, no shebang)         hook_pin rc=0 0.1s
exit1           hook_prefix rc=0     0.1s    (exit 1 with a stdout line)         hook_pin rc=0 0.1s
hang_exec       hook_prefix rc=0     8.1s    (exec sleep 30)                     hook_pin rc=0 8.1s
hang_child      hook_prefix rc=0     8.1s    (sh + a child sleep holding the pipes)  hook_pin rc=0 8.1s
enametoolong    hook_prefix rc=1     0.1s  OSError: [Errno 36] File name too long: '/tmp/aaaa…
enametoolong    hook_pin   rc=0     0.1s    registry screen: no mechanical anti-pattern tells in this hunk
```
(Rows after the first pair are abbreviated here; each printed the same `registry screen: …` last line and the rc shown.)
- Every case returns `[]` through the fix (`rc=0`, a normal snapshot). An overlong `AF_VENV` is a SECOND crash class at the same
  probe (ENAMETOOLONG is not one of pathlib's ignored errnos). The pre-fix hook crashes on it and the fix covers it: the move covers
  the whole `OSError` family, not only EACCES.
- The hangs are bounded at `PROBE_TIMEOUT` (8 s). With a grandchild holding the pipes, `subprocess.run` still returns at the
  timeout: on POSIX it kills the child and only `wait()`s. The orphaned `sleep` outlives the hook, harmlessly.
- D-9 (adjacent, NOT fixed, reported): `gitnexus_impact`'s `except` branch calls `Path("/tmp/gitnexus-analyze.lock").exists()`
  (`:430`) outside any `try`, so a raise there would escape `main`. It needs `/tmp` to be unsearchable by the hook's user, which no
  venue in this repo has. Static only; not reproduced (INFO, F-09).
- Adjacent (INFO, F-10): `main`'s `p.is_file()` (`:456`) on the EDITED file is also outside a `try`. It raises only for a path the
  editing user cannot stat, and PostToolUse runs after that user's successful edit, so it is not reachable in practice.

## Item 7 — THE BASELINE CONTROL (b), AF-AP-138 (RUN FULLY)

- Structure (read at the PIN): every one of the 11 `MUTANTS` rows (`tests/test_vendored_manifest.py:1014-1126`) goes through the
  single parametrized `test_required_mutants_are_killed` (`:1269-1299`). Each run calls `run_killer(killer, load_module(), baseline,
  mutant_name)` on the UNMUTATED module in its own `tmp_path/baseline` and turns an `AssertionError` there into
  `pytest.fail("AF-AP-138: … fails on the UNMUTATED module …")`. Only then does it load the mutant and require
  `pytest.raises(AssertionError, match=mutant_name)` in `tmp_path/mutant`. Any other exception in the baseline propagates and fails
  the row loudly. The 11 rows pass at the PIN (item 10), so every killer passes on the unmutated module there.
- Discriminator, one hollow killer of my own (a STALE PIN: the exclusions killer demands a record that never exists, so it is false
  on the unmutated module AND on the mutant, the registry's shape), in variant copies inside the private clone's `tests/`:
  ```
  == [10] tests/test_vk150_tvm_hollowold.py -k empty-exclusions        (the 656ddf6^ harness + the stale pin)
  1 passed, 50 deselected in 0.16s                                      ← the OLD harness accepts the hollow kill
  == [9] tests/test_vk150_tvm_hollowpin.py -k empty-exclusions         (the PIN harness + the same stale pin)
  E           Failed: AF-AP-138: test_exclusions_do_not_affect_tree_record fails on the UNMUTATED module, so a kill of empty-exclusions is not attributable to the mutation: AssertionError("empty-exclusions\nassert [('', b'dir')...dfc24ca8c96')] == [('', b'dir')...e-pin', b'x')]\n …")
  1 failed, 52 deselected in 0.16s                                      ← the PIN harness refuses it
  == [7] tests/test_vendored_manifest.py -k empty-exclusions           (the PIN, unedited)
  1 passed, 52 deselected in 0.13s
  ```
  (A first attempt inverted the oracle (`!=`). That killer PASSES on the mutant, so the old harness reported `DID NOT RAISE`, a
  survivor, not a hollow kill. It was the wrong shape for the demonstration and was replaced by the stale pin above.)
- D-10 at `656ddf6^`'s bytes, and the fix at the PIN:
  ```
  == [1] tests/test_vk150_tvm_old.py -k unsorted                       (656ddf6^'s test file, byte copy)
  1 passed, 50 deselected in 0.12s                                      ← the hollow kill passes the old harness
  == [8] tests/test_vk150_tvm_d10stale.py -k unsorted                  (the PIN harness with the 656ddf6^ killer list)
  E           Failed: AF-AP-138: test_walk_is_sorted_before_digest fails on the UNMUTATED module, so a kill of unsorted-tree-digest is not attributable to the mutation: AssertionError("unsorted-tree-digest\nassert ['', 'aaa/c.t..., 'zzz/d.txt'] == ['aaa/c.txt',..., 'zzz/d.txt']\n …")
  == [4] tests/test_vendored_manifest.py -k unsorted                   (the PIN)
  1 passed, 52 deselected in 0.12s
  ```
  The mechanism, measured on `656ddf6^:scripts/vendored_manifest.py` (identical to the PIN's, `git diff --quiet` rc 0):
  ```
  unmutated: walk_tree -> ['', 'aaa/c.txt', 'b.txt', 'zzz/d.txt']; 656ddf6^ killer holds: False; PIN killer holds: True
  unsorted-tree-digest mutant: walk_tree -> ['', 'b.txt', 'aaa/c.txt', 'zzz/d.txt']; 656ddf6^ killer holds: False; PIN killer holds: False
  ```
  The root record `("", b"dir")` came from `fe2284d` (2026-09-22T15:58:16+00:00, `+    records: list[tuple[str, bytes]] = [("", b"dir")]`).
  D-10 REPRODUCED; the fix makes the kill attributable. `walk_tree` sorts per directory, so the mutant's order is deterministic,
  not filesystem-dependent.
- Variant files removed; `git -C /tmp/vk150/clone status --short` → empty.

## Item 8 — PARSE_CLASSES (n) (RUN FULLY)

`/tmp/vk150/n_mutants.py`: each mutant is one exact-once replacement in the PRIVATE clone's `scripts/vendored_manifest.py`, checked
to compile, run against `tests/test_vendored_manifest.py -k test_malformed_claude_class_row_is_refused_by_line`, then restored from
the saved PIN bytes (2026-09-24T03:52:21Z to 03:53:21Z):
```
unmutated: rc=0 2 passed, 51 deselected in 8.44s
v-D (the row refusal swallowed: klass = first-party): rc=1 2 failed, 51 deselected in 9.33s
    E       assert 'FAIL: .claude class file parse failure at line 2\n' in 'FAIL: .claude class drift: agents/adversarial-verifier.md: committed=first-party generated=kit-adapted\n'
v4 (parse_classes a no-op returning {}): rc=1 2 failed, 51 deselected in 5.52s
    E       assert 'FAIL: .claude class file parse failure at line 2\n' in 'FAIL: .claude class drift: byte length differs\n'
M8a (a wrong line number in the refusal: line_number - 1): rc=1 2 failed, 51 deselected in 7.71s
    E       assert 'FAIL: .claude class file parse failure at line 2\n' in 'FAIL: .claude class file parse failure at line 1\n'
M8b (a wrong rc: --check prints FAIL and exits 0): rc=1 2 failed, 51 deselected in 5.47s
    E       assert 0 == 1
M8c (the refusal only on the first data row, line 2): rc=1 1 failed, 1 passed, 51 deselected in 6.18s
    E       assert 'FAIL: .claude class file parse failure at line 3103\n' in 'FAIL: .claude class drift: this row has no tab: committed= generated=<missing>\n'
M8d (the header refusal removed): rc=0 2 passed, 51 deselected in 6.75s
M8e (a row with EXTRA cells accepted: cells[1] whatever the cell count): rc=0 2 passed, 51 deselected in 8.32s
scratch script restored to the PIN blob: True
```
- The builder's v-D and v4 REPRODUCE RED. My three contract-shaped mutants (wrong line number, wrong rc, a refusal on the first
  malformed row only) are RED. M8c is killed only by the `no-tab` shape (line 3103), so the test's two shapes both earn their place.
- Two SURVIVORS of the new test (`/tmp/vk150/n_survivors.py`, 03:53:56Z to 03:59:04Z), then the WHOLE file against each and
  `--check` on the shape each misses (a fixture built by the test's own `copy_fixture` + `rewrite_manifest_and_classes`):
  ```
    PIN / three-cell row: rc=1 stderr='FAIL: .claude class file parse failure at line 2'
    PIN / bad header: rc=1 stderr='FAIL: .claude class file parse failure at line 1'
    M8d / bad header: rc=1 stderr='FAIL: .claude class drift: byte length differs'
    M8d whole tests/test_vendored_manifest.py: rc=0 53 passed in 134.98s (0:02:14)
    M8e / three-cell row: rc=1 stderr='FAIL: .claude class drift: byte length differs'
    M8e whole tests/test_vendored_manifest.py: rc=0 53 passed in 155.00s (0:02:34)
  restored to the PIN blob: True
  ```
  No test in the file names the header refusal (`at line 1`) or a row with an extra cell (`grep` of the test file: only `:679`
  asserts the refusal text). Under either mutant `--check` still FAILS (rc 1), with a drift message in place of the named
  refusal. So these are refusal-precision survivors, not gate fail-opens (F-08, FOLLOW-UP).
- Disk note: the fixture copies under `/tmp/vk150/bt*` and `tmp*` reached ~1.4 GB; removed (`df`: 1.8G → 2.8G free).
  `/tmp/pytest-of-root` (287M) was left alone because the other live lanes may be using it.

## Item 9 — MY MUTANTS (RUN FULLY: 23 valid, 11 KILLED, 12 SURVIVORS)

`/tmp/vk150/my_mutants.py` (2026-09-24T04:01:20Z to 04:03:17Z): one exact-once replacement per mutant in the PRIVATE clone. Each
mutated file compiles, the mutated hook imports (every regex compiles), and the run must collect the full count (120 for
`tests/test_edit_snapshot_ap_screen.py`, 11 for `tests/test_vendored_manifest.py -k test_required_mutants_are_killed`) with no
error (AF-AP-78). Restored from the PIN blobs after each run (`restored to the PIN blobs: True`). None repeats the builder's eight
regex mutants or its `M-run-outside-try`.
```
K1 M139-window-10: KILLED | 2 failed, 118 passed | killed-by=['TestAFAP139::test_fires_on_a_class_handler_that_always_answers_200', 'TestAFAP139::test_fires_on_the_pre_fix_s0_05_listener']
K2 M139-no-def-stop: SURVIVOR | 120 passed
K3 M139-any-status: SURVIVOR | 120 passed
K4 M139-any-method: KILLED | 1 failed, 119 passed | killed-by=['TestAFAP139::test_no_fire_on_a_literal_200_outside_a_handler']
K5 M25-window-40: KILLED | 1 failed, 119 passed | killed-by=['TestAFAP25::test_fires_past_the_skip_prefix_of_parse_lock']
K6 M25-splitlines-only: SURVIVOR | 120 passed
K7 M25-no-comment-allowance: SURVIVOR | 120 passed
K8 M25-fullmatch-only: SURVIVOR | 120 passed
K9 M89-bridge-only: KILLED | 1 failed, 119 passed | killed-by=['TestAFAP89::test_fires_on_a_doubled_escaped_quote_through_pc_sh']
K10 M89-cmdsub-only: KILLED | 1 failed, 119 passed | killed-by=['TestAFAP89::test_fires_on_a_doubled_escaped_quote_through_pc_sh']
K11 M89-any-whitespace-before-quote: SURVIVOR | 120 passed
K12 M159-right-no-dots: KILLED | 1 failed, 119 passed | killed-by=['TestAFAP159::test_fires_on_the_right_operand_form']
K13 M159-right-no-final-boundary: SURVIVOR | 120 passed
K14 Mpf-catch-PermissionError-only: SURVIVOR | 120 passed
K15 Mpf-catch-OSError-only: SURVIVOR | 120 passed
K16 Mpf-absent-venv-not-empty: SURVIVOR | 120 passed
K17 Mpf-exists-back-outside-try: KILLED | 1 failed, 119 passed | killed-by=['test_pyflakes_delta_is_empty_when_the_venv_probe_raises']
K18 Mtwin-removed: KILLED | 1 failed, 119 passed | killed-by=['TestAFAP139::test_the_same_row_screens_tests']
K19 Mbl-control-deleted: SURVIVOR | 11 passed, 42 deselected in 9.00s
K20 Mbl-fail-swallowed: SURVIVOR | 11 passed, 42 deselected in 37.29s
K21 Mbl-baseline-runs-the-mutant: KILLED | 11 failed, 42 deselected in 13.38s | killed-by= all 11 rows
K22 Mbl-one-shared-directory: KILLED | 11 failed, 42 deselected in 16.55s | killed-by= all 11 rows
K23 Mbl-label-dropped: KILLED | 11 failed, 42 deselected in 29.39s | killed-by= all 11 rows
valid mutants: 23 killed: 11
```
(Timings dropped from the hook rows for width; each ran in 0.15-0.20 s.)

What each survivor changes on the real tree at the PIN (`/tmp/vk150/survivor_tree.py`, the same whole-text finditer over
`git ls-files scripts src proofs harness-ports tests`, 1050 files):
```
K2 M139-no-def-stop: 6 hits (PIN 6); added=[] lost=[]
K3 M139-any-status: 8 hits (PIN 6); added=['tests/test_proof_runner.py:320', 'tests/test_s0_03_omniroute.py:1541'] lost=[]
K6 M25-splitlines-only: 4 hits (PIN 4); added=[] lost=[]
K7 M25-no-comment-allowance: 4 hits (PIN 4); added=[] lost=[]
K8 M25-fullmatch-only: 3 hits (PIN 4); added=[] lost=['proofs/S0-01/check_acp_conformance.py:1102']
K11 M89-any-whitespace-before-quote: 3 hits (PIN 3); added=[] lost=[]
K13 M159-right-no-final-boundary: 3 hits (PIN 3); added=[] lost=[]
```
- K3 would add two false hits on always-401 REJECTING stand-ins, which are not the class, and no fixture pins the 2xx restriction.
  K8 would lose the `re.match` arm; its one real hit is itself a false positive (item 3). The rest are equivalent on today's tree.
- What the `pyflakes_delta` survivors break, through the real `main` with item 6's crafted venvs (`/tmp/vk150/f6/hook_k1{4,5,6}.py`):
  ```
  enametoolong  hook_pin     rc=0    registry screen: no mechanical anti-pattern tells in this hunk
  hang_exec     hook_pin     rc=0    registry screen: no mechanical anti-pattern tells in this hunk
  enametoolong  hook_k14     rc=1  OSError: [Errno 36] File name too long: '/tmp/aaaa…
  hang_exec     hook_k14     rc=1  subprocess.TimeoutExpired: Command '['/tmp/vk150/f6/v/hang_exec/bin/python', '-m', 'pyflakes']' timed out after 8 second
  enametoolong  hook_k15     rc=0    registry screen: no mechanical anti-pattern tells in this hunk
  hang_exec     hook_k15     rc=1  subprocess.TimeoutExpired: Command '['/tmp/vk150/f6/v/hang_exec/bin/python', '-m', 'pyflakes']' timed out after 8 second
  dangling      hook_pin     rc=0    registry screen: no mechanical anti-pattern tells in this hunk
  dangling      hook_k16     rc=0    LINT   venv absent
  ```
  The PIN code is right. The committed tests pin only the `PermissionError` shape the contract named, so narrowing the `except`
  would re-open a hook crash unseen (F-07).
- K19/K20: the AF-AP-138 control itself has no committed negative control. Deleting it, or swallowing its `pytest.fail`, leaves the
  11 rows green at the PIN, because every killer passes on the unmutated module today. Its only RED proof is scratch (the builder's
  2957→2958 run and my item 7 runs), not a committed test (F-03).

## Item 10 — GATES at the PIN, in the private clone (RUN FULLY)

`/tmp/vk150/clone` at `656ddf6` (`git status --short | wc -l` → `0`), `PYTHONDONTWRITEBYTECODE=1`:
```
$ /root/venv-agent-factory/bin/python -m pytest tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py -q -p no:cacheprovider --basetemp=/tmp/vk150/btg1
173 passed in 139.83s (0:02:19)          run 1, 2026-09-24T04:05:21Z, rc=0
173 passed in 159.58s (0:02:39)          run 2, 2026-09-24T04:07:42Z, rc=0
$ bash scripts/pc_suite.sh set-id -- tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py
2 files set=2a60fb528bf2
$ … -m pytest tests/test_hooks_worktree.py -q -p no:cacheprovider --basetemp=/tmp/vk150/btw
2 passed in 0.14s                        rc=0
$ bash harness-ports/tests/run-all.sh    rc=0 (2026-09-24T04:10:30Z to 04:11:58Z window); last lines:
test_pc_lane.sh                    67 passed, 0 failed
test_pc_lane_dispatcher.sh         pc_lane dispatcher: 51 passed, 0 failed
test_pc_lane_admission.sh          22 passed, 0 failed
test_qwen_server.sh                qwen-server: 101 passed, 0 failed
test_qwen_matrix.py                test_qwen_matrix: 4 tests passed
test_qwen_matrix_sh.sh             qwen-matrix-sh: 19 passed, 0 failed
test_lane_context.sh               5 passed, 0 failed
test_context_mirrors.sh            11 passed, 0 failed
test_sync_skills.sh                34 passed, 0 failed
build-roles --check                OK: 3 role config layers match their sources

ALL SUITES PASSED
$ … -m pyflakes .claude/hooks/edit-snapshot.py tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py
(no output) pyflakes rc=0
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 40 files scanned, clean      rc=0
$ python3 scripts/ap_screen.py .claude/hooks/edit-snapshot.py
--- AP_SCREEN over 1 path(s): 19 hits over 1 files ---      rc=0
AF-AP-159: 1   .claude/hooks/edit-snapshot.py:204: # !!tag), which can sit on the line above the value, so `node.start_mark.line + k` named a line outs…
```
The two runs agree (`173 passed`, set `2a60fb528bf2`), matching the builder's and the premise's counts. The self-screen hit set is
IDENTICAL before and after K150: the `656ddf6^` hook text screened by the same PIN rows gives `19 hits`, and the diff of the two
hit lists with the `path:line:` prefix stripped is empty (`normalized diff rc=0`). No new row fires on the hook itself; the one
AF-AP-159 hit is the pre-existing comment.

## Item 11 — ADJACENT CONSUMERS (RUN FULLY)

- `scripts/ap_screen.py` (loads the hook in-process, `:25-29`), on a real file at the PIN (private clone):
  `python3 scripts/ap_screen.py scripts/pc_lane.sh` → rc=0, `--- AP_SCREEN over 1 path(s): 1 hits over 1 files ---`,
  `AF-AP-89: 1` / `scripts/pc_lane.sh:292: EFF_STATE="$(bridge "export XDG_RUNTIME_DIR=…`. Over the four directories (955
  paths) and the test trees (114 paths) it ran rc=0 (item 3).
- `scripts/lint_delta.py` (loads the hook in-process, `_ap_screen`), in the private clone:
  `/root/venv-agent-factory/bin/python scripts/lint_delta.py --base 656ddf6^` → rc=0,
  `lint_delta (worktree vs 656ddf6^): 2 .py changed, 0 NEW pyflakes hit(s), 0 removed`, then the advisory tells
  (`AF-AP-159`, `AF-AP-139`, `AF-AP-89` on `tests/test_edit_snapshot_ap_screen.py`'s own fixtures). The `--staged` run is in item 4.
- `scripts/lane_context.sh`'s screen section (`:63`), in the shared tree, read-only (`git diff --quiet 656ddf6 HEAD -- <the
  consumer paths>` → identical): `bash scripts/lane_context.sh -o /tmp/vk150/pack_consumers.md scripts/pc_lane.sh
  tests/test_s0_05_egress.py` → rc=0, `pack written … (122 lines)`; its screen sections read `AF-AP-89: 1` (`scripts/pc_lane.sh:292`, `EFF_STATE`)
  and, under `--- TEST_SCREEN over 1 path(s): 30 hits over 1 files ---`, `AF-AP-139: 3` (`:917`, `:1061`, `:3511`).
- Regex safety (`/tmp/vk150/regex_timing.py`: whole-text finditer over `git ls-files scripts src proofs harness-ports tests` =
  1050 files, 38,569,181 bytes, every exception recorded):
  ```
  AF-AP-139: total 0.049s over 1050 files; slowest 2.6 ms proofs/S0-01/evidence/golden/shutdown/manifest-post.txt.gz; raised=[]
  AF-AP-25: total 0.652s over 1050 files; slowest 46.0 ms proofs/S0-01/evidence/golden/cancel/manifest-post.txt.gz; raised=[]
  AF-AP-89: total 0.710s over 1050 files; slowest 44.7 ms proofs/S0-01/evidence/golden/two-users/manifest-pre.txt.gz; raised=[]
  AF-AP-159: total 0.336s over 1050 files; slowest 19.1 ms proofs/S0-01/evidence/golden/run-1/manifest-post.txt.gz; raised=[]
  AF-AP-89 on tests/test_s0_01_check_acp_conformance.py (315851 bytes): 0 hits in 6.0 ms      (the five largest .sh/.py files: 3.1-6.0 ms)
  synthetic: AF-AP-89 2000 bridge args (108000 bytes) 0.005s · AF-AP-25 5 colon-less for-lines of 8005 chars 0.013s
             (2005 → 8005 chars: 0.001s → 0.013s, about quadratic) · AF-AP-139 4000 handlers with no send_response 0.005s
  ```
  No row raises on any file; nothing backtracks catastrophically on the tree. AF-AP-89's scan from each `bridge "` ends at the
  next unescaped quote, and every start holds one, so it stays linear. AF-AP-25's two `[^\n]*` around the alternation are quadratic
  in the length of ONE colon-less `for` line; that is harmless at real line lengths (F-14, INFO).

## Red-green over every NEW test (technique 3; `/tmp/vk150/red_each.py`, targeted mutants in the private clone)
```
RED  TestAFAP139::test_no_fire_on_a_status_keyed_on_the_path | 1 failed, 119 passed in 0.18s
RED  TestAFAP139::test_no_fire_when_the_handler_branches_on_the_path | 1 failed, 119 passed in 0.18s
RED  TestAFAP25::test_fires_on_the_parse_sbom_loop | 2 failed, 118 passed in 0.18s
RED  TestAFAP25::test_no_fire_on_a_jsonl_loop | 1 failed, 119 passed in 0.18s
RED  TestAFAP25::test_no_fire_on_a_single_value_match | 1 failed, 119 passed in 0.18s
RED  TestAFAP89::test_fires_on_the_t94_doubled_command_substitution | 2 failed, 118 passed in 0.20s
RED  TestAFAP89::test_no_fire_on_the_single_escape | 3 failed, 117 passed in 0.20s
RED  TestAFAP89::test_no_fire_outside_a_bridge_argument | 2 failed, 118 passed in 0.18s
RED  TestAFAP89::test_no_fire_after_the_argument_closes | 1 failed, 119 passed in 0.19s
RED  TestAFAP159::test_no_fire_on_a_right_operand_column | 1 failed, 119 passed in 0.18s
RED  test_pyflakes_delta_is_empty_when_running_the_venv_python_raises | 1 failed, 119 passed in 0.20s
restored: True
```
With item 9 (K1, K4, K5, K9/K10, K12, K17, K18, K21-K23) and item 8 (v-D, v4, M8a-c), every one of the 21 new tests
(`tests/test_edit_snapshot_ap_screen.py:491-625`, `tests/test_vendored_manifest.py:651-679`) and all 11 rows of the reworked
`test_required_mutants_are_killed` have been seen RED at least once. No new test is a tautology.

## Item 6 addendum — the registry's ORIGINAL symptom, reproduced at the suite level (beyond the builder's NOT-done)
AF-AP-44's row (`incident_pin.md:481`) records `harness-ports/tests/run-all.sh` in a bare non-root PC shell without `AF_VENV`:
"codex adapter 6/7, hermes adapter 4/6, spool 4/9". The sandbox's `/root` is `drwx------`, so uid 65534 meets the same refusal.
I ran the three hook-driven suites in the private clone as uid 65534 (`env -u AF_VENV HOME=/tmp setpriv --reuid=65534 --regid=65534
--clear-groups python3 harness-ports/tests/<suite>`), with the hook swapped between the `656ddf6^` blob and the PIN blob:
```
== hook=prefix (blob b52a0d8ab536), uid 65534, AF_VENV unset
  test_codex_hook_adapter.py     rc=1  6/7 passed
  test_hermes_hook_adapter.py    rc=1  4/6 passed
  test_hermes_spool.py           rc=1  4/9 passed          ← the registry's numbers, exactly
== hook=pin (blob 2f968c6f5bb3), uid 65534, AF_VENV unset
  test_codex_hook_adapter.py     rc=0  7/7 passed
  test_hermes_hook_adapter.py    rc=1  5/6 passed
  test_hermes_spool.py           rc=0  9/9 passed
```
The PIN's remaining 5/6 is the retro-gate check (`[FAIL] pre_verify POSITIVE: retro gate's exit-2+stderr becomes a Hermes block`,
`stdout=''`), not the hook. uid 65534 in a root-owned clone gets `fatal: detected dubious ownership in repository at
'/tmp/vk150/clone'`, so the gate is silent: a venue artifact of the reproduction (the registry notes the same for a `.git`-less
copy). With git allowed the directory through its environment (`GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=safe.directory
GIT_CONFIG_VALUE_0='*'`), the hook is the only variable:
```
== hook=prefix (blob b52a0d8ab536) …, safe.directory=*   codex 6/7 rc=1 · hermes adapter 5/6 rc=1 · spool 4/9 rc=1
== hook=pin (blob 2f968c6f5bb3) …, safe.directory=*      codex 7/7 rc=0 · hermes adapter 6/6 rc=0 · spool 9/9 rc=0
```
The fix closes the recorded symptom at the harness level. The clone was restored to the PIN blob (`2f968c6f5bb3`, `git status`
empty).

## FINDING INVENTORY (no severity filter)

Evidence levels: VERIFIED = reproduced this session by the command quoted in the item section; STATIC = read from primary source only.

| ID | Class | Evidence | Contract mapping | Canonical path | Material effect | Reproduction | Suggested fix |
|---|---|---|---|---|---|---|---|
| F-01 | FOLLOW-UP (escalation to the coordinator; the AF-AP-155 class at brief authoring) | VERIFIED (grep) | none: outside the frozen K150 contract | n/a (planning) | Nine registry rows defer their screen line or skill bake to task #150: screen lines for AF-AP-132, -141, -144, -145, -149, -152, -153 and skill bakes for AF-AP-150 (deep-work) and AF-AP-151 (build-loop) (`incident_pin.md:569,578,581,582,586-590`). None is in the K150 contract or in the ledger's #150 item list (`todo/BUILD-TASKLIST.md:1367`, `TASK #150 GAINS TWO ITEMS`; `grep '#150'` per id → 0, one incidental AF-AP-149 mention). Closing #150 as complete would leave nine registry promises unowned | the grep in "Stale context" below | before #150 closes, give each deferral a named task, or mark it not mechanizable (AF-AP-153 has no line signature) |
| F-02 | FOLLOW-UP (coordinator, registry) | VERIFIED (grep at the PIN and at HEAD `cbd05fa`) | technique 7 (stale context); the registry is READ-ONLY for K150 (brief §Boundary) | n/a | Registry text K150 made false: AF-AP-25/-44/-139/-162 still say the screen line or fix "waits for task #150"; AF-AP-89 still says "A shell/bridge signature, not an edit-snapshot AP_SCREEN row"; AF-AP-138 still says "OPEN — … goes in at K1-h's harvest" and "found no other instance" (D-10 is a second); AF-AP-159's signature column quotes only the left form | `grep '^\| AF-AP-138 \|' docs/INCIDENT-LOG.md` etc. at HEAD | one registry pass at the landing |
| F-03 | FOLLOW-UP | VERIFIED (K19, K20) | (b) is met; nothing demands a meta-test | `tests/test_vendored_manifest.py:1269-1299` | The AF-AP-138 control has no committed negative control: deleting it or swallowing its `pytest.fail` leaves 11 rows green. Its RED proof is scratch only | item 9 K19/K20 | a committed meta-row that feeds the harness a stale killer and asserts the `AF-AP-138:` failure |
| F-04 | FOLLOW-UP | VERIFIED (item 3 reachability, item 11) | (k′) placed the row in AP_SCREEN, and it fires there through `ap_screen.py`/`lane_context.sh` | `.claude/hooks/edit-snapshot.py:221`; `main` `:443`; `scripts/lint_delta.py:_changed`; `scripts/ap_screen.py:_files` | The AF-AP-89 row reaches its class (`.sh`) only when a `.sh` path is named explicitly; the edit-time hook and the pre-commit lint never apply it. The AF-AP-87 comment (`:293-294`) documents the same limit; the AF-AP-89 comment does not | item 11 (`ap_screen.py scripts/pc_lane.sh` → `AF-AP-89: 1`; the hook returns 0 on `.sh`) | add the AF-AP-87-style comment line; optionally screen staged `.sh` files with the shell rows in pre-commit |
| F-05 | INFO | VERIFIED | D-5 | `lint_delta.py` via `scripts/hooks/pre-commit:16` | D-5's stated reason overreaches: an AP_SCREEN-only row would still run on test files at commit time. The twin is still needed for the edit-time hook and `ap_screen.py --tests`, and it does not flood (6 hits) | item 4 | reword the D-5 note; keep the twin |
| F-06 | FOLLOW-UP | VERIFIED (nearmiss A1-A14, K2, K3, survivor_tree) | (d2): positive + negative fixtures exist | the row at `:67` | Literal-2xx only: misses `HTTPStatus.OK`, `send_response(200, msg)`, a status held in a variable (the real, class-safe `_Handler` at `tests/test_s0_03_omniroute.py:856-866`), `-> None`, delegation, aliasing, `send_response_only`, >1000-char bodies, and an unrelated `if … self.path` or a comment naming it. False hits on a path variable, a `match` statement, a route table. K3 (any status) survives and would add 2 false hits on always-401 rejecting stand-ins. No in-class miss in the tree | item 3 (ii), item 9 | negative fixture: an always-401 handler; positives: `-> None` and `HTTPStatus.OK` |
| F-07 | FOLLOW-UP | VERIFIED (K14-K16 through the real `main`) | (f): the demanded `PermissionError` test exists | `pyflakes_delta` `:332-343` | The committed tests pin only `PermissionError`. `except PermissionError`/`except OSError` would re-open a hook crash (`rc=1` on ENAMETOOLONG, `subprocess.TimeoutExpired`), and a non-empty absent-venv return would print a false tell; all three survive. The PIN code is correct | item 9 | controls raising `OSError(ENAMETOOLONG)` from the probe and `TimeoutExpired` from the run; an absent-venv case asserting `[]` |
| F-08 | FOLLOW-UP | VERIFIED (M8d, M8e: whole file `53 passed`) | (n) is met: v-D and v4 RED, the named refusal asserted | `parse_classes` `scripts/vendored_manifest.py:574-587` | The header refusal (`line 1`) and the cell-count refusal for a 3-cell row are untested. `--check` still fails closed (rc 1), with a drift message in place of the named refusal | item 8 | add `bad-header` and `extra-cell` shapes to the parametrize |
| F-09 | INFO (D-9) | STATIC | none | `gitnexus_impact` `:430` | `/tmp/gitnexus-analyze.lock` probe outside a `try`; unreachable where `/tmp` is searchable | none | wrap it when next touched |
| F-10 | INFO | STATIC | none | `main` `:456` | `p.is_file()` on the edited path outside a `try`; unreachable after a successful edit by the same user | none | wrap it when next touched |
| F-11 | INFO (brief-named finding) | VERIFIED (added-line overlap; term scan) | K150 §Items "in the twin's own words" | `.agents/skills/*/SKILL.md` | Every twin hunk of the nine bakes is a byte copy of the `.claude` hunk. Harmless: the copied text names no Claude-only mechanism (the scan's only harness terms are in the ported paragraph's reworded lines), and those regions were already byte-identical between the twins | item 2 | none required |
| F-12 | INFO | VERIFIED (`incident_pin.md:30-31`) | (l′) | `.claude/skills/anti-hollow-green/SKILL.md:130`; hook comment `:217-220` | "made every poll a syntax error on the PC" / "the PC received a syntax error" state as an event what the narrative calls a counterfactual ("would have", caught at the coordinator's pre-commit read). The bake mirrors AF-AP-162's own row wording; the rule stands | item 2 | "would have made" |
| F-13 | INFO | VERIFIED | (h) ("the ledger and every PROVENANCE file", followed) | `.claude/skills/orchestration/SKILL.md:92` | The grep omits AF-AP-155's `before the next capture (<LANE>)` phrasing and the row's "findings" files | item 2 | add the phrase |
| F-14 | INFO | VERIFIED | none | AF-AP-25 row `:215` | About quadratic in the length of one colon-less `for` line (2005 → 8005 chars: 0.001 s → 0.013 s); harmless at real lengths | item 11 | none |
| F-15 | INFO | VERIFIED | (g) | AF-AP-25 row | Misses `.split("\n")`, `for line in fh`, a list split earlier, `re.search`, a wrapped header, compiled patterns (documented). One real false hit: `proofs/S0-01/check_acp_conformance.py:1102` (`log_line`) (the window crosses the loop's dedent). It will keep firing on `parse_lock`/`parse_sbom` if task #170 keeps the regex loop and adds a refusal (B7). K6/K7/K8 survive. No in-class miss in the tree | items 3, 9 | fixtures for `re.match` and `readlines`/`open(` headers; a negative for a post-loop match |
| F-16 | INFO | VERIFIED | (k′) | AF-AP-89 row | Misses a doubled backtick, `\\$VAR`, a nested quote in `$( )` before the escape, the `pc()`/`pc_quiet`/`pc_bridge_exec.py` helpers, and a flag before the argument; fires on a comment. K11 survives. No in-class miss in the tree | items 3, 9 | key on the tree's other helper names if they ever carry a remote `\$(` |
| F-17 | INFO | VERIFIED | (m) | AF-AP-159 row `:206` | Misses `start_mark.line - 1`, the two-line alias, `k + (node.start_mark.line)`; fires on `nodes[i + 1].start_mark.line`. K13 survives. 0 hits in the tree | items 3, 9 | none now |
| F-18 | INFO (pre-existing) | VERIFIED | none | hook `:450`, `:499`; `lint_delta.py` | `{ap_id:6s}` runs a 9-char id into the text (`AF-AP-139an HTTP…`, `AF-AP-139tests/…`) | items 4, 11 | a space after the id |
| F-19 | INFO (pre-existing) | VERIFIED | none | `sandbox-kit/VENDORED-MANIFEST.md` header | `Generated from commit` names a pre-push SHA unreachable from origin (`b74b63b`; `d116e3d` before; `git merge-base --is-ancestor` rc 1 for both). Informational by design (the drift check ignores it) | above | write the manifest after the push, or drop the SHA |
| F-20 | INFO (my conduct, disclosed) | VERIFIED | brief boundary ("CREATE only …") | the shared tree root | A failed D-6 command (a trailing `&` backgrounded its `cd`) created three EMPTY untracked files in the shared tree root at 03:44:11Z (`r_medium.txt`, `r_unq.txt`, `r_xhigh.txt`); found by `git status` at about 04:14Z and removed; no other file in that window (`find -newer`), no tracked file touched | above | none left |

### Stale context (technique 7), the grep behind F-01/F-02
`git show <rev>:docs/INCIDENT-LOG.md | grep -n -o -E '^\| AF-AP-[0-9]+ \||task #150…'` at `656ddf6` and at HEAD: rows naming
task #150 for pending work = AF-AP-25, -44, -132, -139, -141, -144, -145, -149, -150, -151, -152, -153, -155, -162 (identical sets
at both revisions). K150 delivered the work of -25, -44, -139, -155 and -162; the other nine are F-01.

## BLOCKING PREDICATE (every condition must hold)

| Finding | 1 contract | 2 canonical repro | 3 material | 4 discriminator | 5 in boundary | Blocks? |
|---|---|---|---|---|---|---|
| F-01 | NO (not in the frozen contract) | n/a | yes, for the ledger | grep | NO (coordinator) | no: escalation |
| F-02 | technique 7 only | yes | registry prose | grep | NO (registry READ-ONLY) | no |
| F-03 | NO (not demanded) | yes | no (all kills attributable today) | K19/K20 | yes | no |
| F-04 | NO (contract put it in AP_SCREEN; it fires via ap_screen) | yes | no (it fires where the class lives) | yes | yes | no |
| F-06/-15/-16/-17 | fixtures exist as demanded | yes | no (no in-class miss, no flood in the tree) | yes | yes | no |
| F-07 | NO (the PermissionError test exists) | yes | no (the PIN code is correct) | K14/K15 | yes | no |
| F-08 | NO (v-D/v4 RED as demanded) | yes | no (fails closed) | M8d/M8e | yes | no |
| F-11/-12/-13 | partly | yes | no false fact | text | yes | no |
| F-05, F-09, F-10, F-14, F-18, F-19, F-20 | no | — | no | — | — | no |

No finding satisfies all five conditions. None is a CONTRACT-DEFECT: nothing falsifies evidence, corrupts state or loses data on
the production path. The one silent-green class this change targets (AF-AP-138) was checked in both directions (items 7, 9).

GATE RECOMMENDATION: MERGE-READY-WITH-FOLLOWUPS — every load-bearing claim reproduced this session; follow-ups F-01 (the coordinator's #150 scope gap, before #150 closes), F-02, F-03, F-04, F-06, F-07, F-08.

## Report lint (two rounds; stopped per the brief's three-round bound)
```
$ python3 scripts/report_lint.py --min-refs 15 tasks/briefs/kit-k1-support/VERIFY-K150-report.md --root .
round 1: report_lint: 57 refs — OK 18, NEAR 2, MISS 24, UNCHECKABLE 13, UNRESOLVED 0 (worktree)
round 2: report_lint: 60 refs — OK 44, NEAR 0, MISS 2, UNCHECKABLE 14, UNRESOLVED 0 (worktree)   (rc=1: the two MISSes below)
```
Round 1's `fix:` hints were applied: a backticked token from each cited line, and one wrong number corrected (the bug-echo's
line 506 of the manifest script, an older revision's number; the table walk is `scripts/vendored_manifest.py:667` at the PIN,
`if not line.startswith("|")`). The two MISSes left are both on one line of VERBATIM tool output inside a fence (the
`survivor_tree.py` K3 line). Its cited lines are right: `def do_GET(self):` is `tests/test_proof_runner.py:320`, and
`def do_POST(self):` is `tests/test_s0_03_omniroute.py:1541`. Editing pasted output would falsify it, so they stay.

## DISCREPANCIES
- The builder's ten, graded: D-1 ACCURATE (item 2). D-2 ACCURATE; the coordinator corrected the glob at `2aab702` (HEAD's
  AF-AP-155 row reads `proofs/*PROVENANCE.md`). D-3 ACCURATE; AF-AP-140 reads `FIXED(2026-09-23)` at HEAD. D-4 ACCURATE (item 2).
  D-5 NEEDED and sound, rationale overreaches (F-05). D-6 CONFIRMED by execution (item 4). D-7 CONFIRMED pre-existing: at
  `656ddf6^` the AF-AP-118 comment is `:180` and its row `:192`, with AF-AP-127 and AF-AP-159 between. D-8 CLASSIFIED class-safe
  (item 5). D-9 CONFIRMED statically (F-09). D-10 REPRODUCED, and the fix verified (item 7).
- Mine: (1) F-20, the three stray files, now removed. (2) The premise block's pytest ran in the shared tree (the brief's own
  command), with `PYTHONDONTWRITEBYTECODE=1`; pytest used its default basetemp under `/tmp/pytest-of-root`, which I did not delete
  because other lanes may use it. (3) `scripts/lane_context.sh` ran twice in the shared tree (the brief's pack, and the item-11
  consumer check); it wrote only `/tmp/vk150/*.md` plus gitignored index directories. (4) My first hollow killer in item 7
  inverted the oracle, the wrong shape; it was replaced by a stale pin, and both runs are pasted. (5) At the end the shared tree
  shows ` M docs/INCIDENT-LOG.md`. That is not mine: the coordinator is editing it; I never opened it for writing.
- The builder's report cites `docs/INCIDENT-LOG.md@2b13ced:<n>` row numbers; at the PIN the same rows sit about 2 lines lower
  (for example AF-AP-139 is `incident_pin.md:576` against the report's `:574`), because entries were prepended after `2b13ced`. The
  contents match.

## NOT-done (and how each item ran)
- Items RUN FULLY: 1, 2, 3, 4, 5, 6 (with the suite-level addendum), 7, 8, 9, 10, 11. Item 5 ran by the brief's own method (the
  test, the runner, the canary and the checker, read at the PIN). The `NEEDS_NETNS` test itself was NOT executed: it builds
  namespaces and firewall rules in the sandbox's root namespace, which two live lanes and the agent proxy share.
- NOT re-run as named: the builder's eight regex mutants and `M-run-outside-try`. My 23 item-9 mutants and 11 targeted mutants
  cover the same rows, and K17 is the builder's pre-fix placement.
- NOT re-measured (not load-bearing): the builder's flood counts for the bug-echo's loop-header regex (`56 lines`) and the
  compiled-pattern extension (`8 lines`); the GitNexus `detect-changes` line; the coordinator's served-model count
  (`448 assistant records`).
- NOT run here (brief: no PC, no bridge): the AF-AP-44 symptom on the PC. It was reproduced in the sandbox as uid 65534
  instead (item 6 addendum).
- Scratch cleanup at the end: the private clone and `/tmp/vk150` fixture copies are removed (see the last line).
- Cleanup done 2026-09-24T04:23:04Z: `rm -rf /tmp/vk150/clone` and the fixture dirs → `ls -d /tmp/vk150/clone` → `No such file or directory`; `/tmp/vk150` is 916K (the driver scripts and text outputs cited above, kept for the coordinator); `df` 3.3G free. No process of mine is left; the only `sleep 30` alive (pid 8125) belongs to another session's PC poll loop (pid 6289) and was left alone. The shared tree shows only this report (`??`) and the coordinator's ` M docs/INCIDENT-LOG.md`.
