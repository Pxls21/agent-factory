> **Coordinator note (2026-09-29 23:0xZ, at harvest).** The builder's hand-back, saved as the transcript holds it
> (agent a27e2620eaee3eb6d; served wholly by claude-opus-5-5, 0 refusal stops). Landed GATED-PENDING-VERIFY: the
> landing gate `3 files set=c3270831ad89` read `pytest-summary: 326 passed in 110.14s (0:01:50)`. Its D4 (a body
> of one line only) is the first item for its verify and repair.

# LS-B11 report: the box (task #380; D-111, D-113). Lane: sandbox code-implementer, Opus 5.5. PIN b2e1ed8.

VERDICT: I built the box. The deliverable is written and applies at the PIN. Both gates passed twice. All 51 mutants were KILLED. The registration patch needs NO change. Nothing is registered, and nothing was committed or pushed.

Read these first: the NOT DONE list, then the DISCREPANCIES list. D1 and D2 are my readings of two points where the brief contradicts itself. D4 is a real limit: a body of more than one line cannot run.

## 1. Premise re-run (CONTRACT item 1)
- I ran `bash scripts/premise_block.sh` from /home/user/agent-factory at 21:38:16Z. It printed 32 lines. `diff` against the brief's block was empty: IDENTICAL.
- The main tree's HEAD moved to 3f18bc0 during the lane (the coordinator's commits). `git diff --stat b2e1ed8 HEAD` over my six files is empty, so the patch should also apply at HEAD. That is inferred from identical files; I did not check it there.

## 2. Deliverable
- File: /home/user/agent-factory/tasks/briefs/labeling/LS-B11.patch (untracked, 944 lines). It is the only file I wrote in the shared tree.
- sha256: 3186217e39e1a2042f1d3bf405a9c6511f5cff41bb0acf5d64250d6874c1b62f. It equals `git -C <wt> diff b2e1ed8`.
- Scope: 6 files changed, 634 insertions(+), 32 deletions(-). No new files.
- `git apply --check` on a clean PIN checkout: rc 0.
- I applied it in a fresh PIN worktree. `sha256sum -c` passed for all 6 files against the final copies.
- A U+2028/U+2029 check gave 0 hits in the patch and in each file.

## 3. Files: line counts at the PIN and now, sha256 now, numstat

| File | Lines (PIN / now) | sha256 now | numstat |
|---|---|---|---|
| scripts/ls_req.py | 1267 / 1412 | 3f65b05429d6ae56cf2ed2fb2b24021bb7f3fb09aadfb959a814a29eed4d5df8 (PIN cb4943a96f6578e5) | +167 -22 |
| tests/test_ls_req.py | 1397 / 1785 | 4154a754e8634f6a7fe22804ef890dd492573370c434b0d1cd805dbd2db7c40e (PIN 64faf22cf543bc56) | +391 -3 |
| scripts/stack.py | 1434 / 1442 | ef819f69430d7459991c68dc0b08cdb8f1de06c6e59a5c921ba42d3d4a9ce506 (PIN c69a819138d21471) | +12 -4 |
| scripts/stacks.toml | 529 / 532 | 05ba1573b6212e7b02c1d83934c74f6f001bf1dc0209ae22dac10fd50ecc5281 (PIN 6393305a0bf1a585) | +3 -0 |
| tests/test_stack.py | 2424 / 2473 | 749d679db3b2d4eb2d1047c37d336f6a91ff377930c06ac0a8119b9c80f97600 (PIN 384253ec06482aa8) | +52 -3 |
| docs/research/findings/labeling/LS-DESIGN-v2-2026-09-28.md | 140 / 149 | 1726d3a57d9f0a6458a242e76df352537945ee7ce979926e3160cc77baa70a82 | +9 -0 |

- pyflakes: 0 hits at the PIN and 0 now, on each .py file.
- Added lines: 634. The longest is 120 characters, and none is over 120.
- Copies of the six final files and a SHA256SUMS file: /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/lsb11-lane/final/

## 4. Evidence per CONTRACT item (line numbers are the final files')

**Item 2: the box is a second request head in parse_message.**
- ls_req.py:183-191 has the constants: TOP_RE, BOTTOM_RE, DIVIDER_RE, NAME_RE, FENCE_RE, BAR, BOX_LINE and LEDGER_TEXT_MAX=4000. They are real `\u` escapes.
- Cand gets `form` ("req" or "box") and `body` (:476-487).
- why_malformed sends a line that starts with ┌ to the new why_top (:499-502, :521-535).
- New parse_box (:538-587).
- The box head in parse_message is at :598-605. A box is appended as a request only when its nonce is current or it is well formed on its own grammar. Otherwise its lines are text.
- Closing rule (:657-662): a fence line is exempt only in a message that holds a box.
- lam_missing also looks for a top edge (:674).
- The ledger row adds `form` and `text` (:771). `text` is cut at 4000 characters; `sha` is always the whole text's.
- stack_labels returns {label: body} (:804). run_request adds `[body_key, c.body]` (:837).
- cmd_stop judges the two registry body cases (:1307, :1310) after the unknown-label check.
- Everything else (the Stop hook, duplicate id, stale nonce, cap, budget, receipts, bind rows, reconciler) is unchanged, and boxes pass through it.

**Item 3: NONCE_LINE (ls_req.py:216).**
- Length with a 12-character nonce: 454 characters before; 555 characters (577 UTF-8 bytes) now.
- Still one line. The nonce appears 3 times before and 4 times now.
- New text (nonce shown as `<nonce>`): "Chat form (LS-B10) nonce <nonce>: to run a stack without a tool call, end your message with one box per request, such as the three lines `┌─ find · r1 · <nonce>`, `│ q: who calls parse_message`, `└─` (a label of scripts/stacks.toml, a new id per box, a `│ key: value` line per parameter; below a `│ ┄┄┄` line, the stack's body, verbatim), nothing after them and the nonce nowhere else; fallback, one line: `REQ <nonce> <id> <label> key=value ...`. A Stop hook runs each through scripts/stack.py and answers `RES <nonce> <id> <status>`."

**Item 4: a stack names its body.**
- stacks.toml gets three `body` lines:
  - ctx: `body = "q"` (:256). The question for graft ask, in prose; `files` and `sym` stay key: value lines.
  - find: `body = "q"` (:322). The question, the stack's one text parameter.
  - echo: `body = "pattern"` (:411). A search pattern, written as is.
- No body for: harvest (agent id, path), gate (paths and switches), impact (a symbol), premise (paths), review (paths, mode), ci (a branch name, not prose).
- stack.py: STACK_KEYS gets "body" (:93).
- Validation (:377): the body must name a parameter a request sets, else registry exit 3: `stacks.<label>.body: must name a parameter of this stack that a request sets (found %r; those parameters: ...)`.
- `explain` prints `body: <param> (a chat-form box's lines below its ┄┄┄ divider fill it)` only when a body is set (:1235).

**Item 5: the REQ form is unchanged.**
- Differential probe: 30,000 random box-free messages, 65,986 candidates. The PIN and new versions of parse_message, lam_missing and why_malformed were compared on 12 fields: `diffs=0`. The control mutant (fence always exempt) gives `diffs=281`, rc 1.
- 286 unchanged tests of the gate-1 set pass.
- The tests that name VERIFY-LS-B10 F1 (5 LS-B10 tests), F4 (2) and F6 (6: V1, V2, V3, V5, V12, cap) all pass.
- F10 (the registration patch: "registers 13 hooks") passes in gate 2 through `test_fresh_install_registers_and_prints_13_hooks`.
- Ledger rows stay one per receipt. Bind rows are unchanged and carry `form`.

**Item 6: the design record.**
- The THE BOX docstring section is at ls_req.py:41-76, between THE GRAMMAR and RECEIPTS.
- The STATE docstring names `form` and `text`.
- LS-DESIGN-v2 §3 gets a paragraph dated 2026-09-29 (:47-55). It states the known limit.

## 5. Tests (tests/test_ls_req.py:1416-1785; tests/test_stack.py). Each names its mutants.

tests/test_ls_req.py (fixture registry BOX_REGISTRY adds stack `echobody` with `body = "q"`):
- :1451 a box's parameters (V01-V05, V37).
- :1467 the body keeps backquotes, a fence line, a leading space and an empty line (V06-V08).
- :1479 a box in a fence, two boxes, a box beside a REQ line, and prose after them (V09-V11).
- :1496/:1531 the 15 malformed cases, each with its exact reason (V11-V24).
- :1540 illustration against stale (V25-V27).
- :1559 premise through the real hook: row form, text, sha and line (V04, V05, V09, V28, V29).
- :1581 the fallback answers a box once and binds its record (V04, V28, V37).
- :1605 a stale box only in the fallback (V28, V30).
- :1623 duplicate id across the two forms (V35).
- :1639 a stale box never runs or blocks; a box with no nonce gets nothing (V26, V28).
- :1655 one receipt under the id or under `?` (V12, V28, V36).
- :1672 the body goes in as ONE argument. `$(touch pwned) ; echo hi | cat && x` arrives intact and no file is created. The two body cases are refused. A body of two lines is refused by the runner (V02, V31-V33, S05).
- :1696 reconciler (V41).
- :1708 NEW this stretch: defer-check defers the retro for a box (V44).
- :1730 cap (V42).
- :1745 budget (V43).
- :1762 time bound (V38).
- Moved: :545 the NONCE_LINE pin (V34, V39, V40).

tests/test_stack.py:
- Three new bad-registry cases at :905-906 (body-undeclared, body-derived, body-not-a-string), each with its exact message (S01, S02).
- :1259 explain shows the body line only when a body is set (S03, S04).
- :1277 the exact body map (S05, T01, T02).
- Moved: explain pins ctx, echo and find (:1235; S03, T01).

## 6. Gates (in my worktree; --basetemp under the scratch directory, outside every work tree; counts pasted from scripts/test_summary.sh)

- PIN baseline, `3 files set=c3270831ad89` (tests/test_ls_req.py tests/test_session_hooks.py tests/test_stack.py): `pytest-summary: 290 passed in 108.17s (0:01:48)`.
- **Gate 1** (every test file that names a changed file, from `stack.py gate ... mode=plan graph=no`: the same 3 files), `3 files set=c3270831ad89`:
  - `pytest-summary: 326 passed in 108.99s (0:01:48)`
  - `pytest-summary: 326 passed in 107.20s (0:01:47)`
  - pytest-exit 0 both times.
- **Gate 2** (a second worktree = PIN + LS-B11.patch + LS-B10-registration.patch; both applied with rc 0, in either order), `3 files set=9425e01745d1` (tests/test_ls_req.py tests/test_search_intercept.py tests/test_session_hooks.py):
  - `pytest-summary: 230 passed in 122.64s (0:02:02)`
  - `pytest-summary: 230 passed in 119.27s (0:01:59)`
  - pytest-exit 0 both times. 230 = the verifier's 199 at 03ad1b6 + my 31 new ls_req tests.
- No SKIPPED, XFAIL or XPASS in any gate log.
- Earlier runs, before I added the defer test, are superseded: gate 1 `325 passed` twice, gate 2 `229 passed` twice.
- I found no pattern reader (glob, rglob, os.walk, ls-files) that reaches the six files. test_shell_syntax.py selects .sh files and sh shebangs only.
- **Red at the PIN** (PIN + my final test files, before the defer test existed): `pytest-summary: 39 failed, 286 passed in 107.47s (0:01:47)`. The 39 failure headers equal the 35 new + 4 moved tests exactly. The defer test PASSES at the PIN (`1 passed in 0.76s`): it pins behaviour that already existed, so it is not a red-green test.

## 7. Mutants (the AF-AP-223 driver: control first; KILLED only when rc is 1 with failures and no errors)
- Driver controls: C1 no-op `SURVIVED`, C2 syntax break `INVALID` (1 error). `ROWS=2 KILLED=0 SURVIVED=1 INVALID=1`: the scoring works.
- Unmutated control: `CONTROL identity=True rc=0 tests=41 41 passed in 15.09s`.
- `ROWS=51 KILLED=51 SURVIVED=0 INVALID=0`: V01-V44 in ls_req.py, S01-S05 in stack.py, T01-T02 in stacks.toml. After the run, each file matched its sha256.
- V44 (defer only on `REQ <nonce>`) SURVIVES the old defer test and is killed only by the new one.
- Logs: mut-final2-all.log, mut-final2-control.log, mut-v44-old.log.

## 8. Hook time (the measured numbers; the test bound is `took < 10` s, and a whole-file-scan mutant fails the byte bound)
- Setup: a 42,269,422-byte transcript, a turn of 200 prose records, and one message with five boxes that run `premise`. 30 rounds.
- Hook's own time: p50 622.2 ms, p95 697.0 ms, max 717.0 ms. Wall: 0.692 / 0.773 / 0.788 s. Bytes read: 329,635.
- The next Stop: p50 7.1 ms, p95 10.3 ms, max 10.9 ms. Bytes read: 129.
- Control, five REQ lines: PIN hook 620.8 / 675.9 / 676.6 ms; new hook 626.0 / 690.5 / 691.1 ms. The box adds no measurable cost.

## 9. The registration patch: NO change needed
- It applies at the PIN and on top of LS-B11 (rc 0), and gate 2 passed twice.
- Its test fullmatches `Chat form \(LS-B10\) nonce ([0-9a-f]{12}): [^\n]*`. I kept that prefix, and kept the line to one line.
- turn-retro-gate.sh calls `ls_req.py defer-check`, which reads content only: a current nonce in the texts. A box's top edge carries the nonce. The new test at :1708 proves a box defers the retro.

## 10. NOT DONE
1. The hooks are not registered (by rule). The box is not live.
2. No run in the real harness. All hook evidence uses the real hook entry on synthetic transcripts.
   - The committed fixtures write ASCII-escaped JSON, but the harness writes raw UTF-8.
   - A scratch probe re-ran 10 hook-level box tests with raw UTF-8 in the transcript and the payload: `12 passed in 6.13s` (10 tests, 1 payload-bytes check, 1 escaped-fixture control).
   - The probe is not committed. A committed raw-UTF-8 fixture variant is a follow-up.
3. A body of more than one line cannot run (see D4).
4. Only `explain` shows `body`. `list` and the SessionStart catalog do not (the brief asked for explain only).
5. Wording not updated, to keep LS-B10's pinned strings: the feedback head says "one per request line", and the duplicate-id reason says "every request line takes a new id".
6. A box split across two text blocks of one message, while the transcript lags, could be refused as unclosed. LS-B10's `<<WORD` blocks have the same shape. Not tested.
7. GitNexus detect_changes was not run: no commit, and the worktree is not indexed. I ran impact before editing: parse_message is **HIGH** risk (1 direct caller; flows cmd_prompt, cmd_session_start, cmd_stop). The probe and the gates above are how I addressed it. stack_labels, lam_missing and cmd_explain are LOW. Stack is UNKNOWN; a text sweep found its only consumers are stack.py, ls_req.py and the tests.
8. LS-B10's 1-file set `35c6a92807a9` was not run on its own. It is a subset of both gate sets.

## 11. DISCREPANCIES
- **D1 (the brief contradicts itself).** Item 2 calls its mock-up "an illustration", but the mock-up is a well-formed box with a 12-hex nonce, and the same item says such a box is `refused: stale nonce`. I followed the specific rule.
  - If the mock-up is written in chat, it is a stale request: `refused: stale nonce`, held until the next prompt, never blocking.
  - Only a box broken on its own grammar is a silent illustration. The closing rule and the two body cases do not count here, so the check is not circular.
  - The test at :1540 pins this.
- **D2 (fences).** Item 2 says fence lines never break the closing rule. Item 5 says REQ stays exactly as it was, and an LS-B10 test pins a fenced REQ-only line as malformed. So the fence exemption applies only in a message that holds a box (probe: 0 differences).
- **D3.** NONCE_LINE keeps "(LS-B10)" and stays one line, because of the registration test (section 9).
- **D4 (real limit).** stack.py's text type refuses newlines and takes at most 500 characters. So "everything below ┄┄┄ verbatim" works only for a body of one line. A longer body reaches the runner and gets its refusal, for example `refused: q=line one line two refused: a text holds no NUL and no newline`. That is never silent, but it cannot run. A fix needs a stack.py type change, which is outside my boundary (the body key only). The coordinator must decide.
- **D5.** `body` must name a parameter a request SETS, which is stricter than "declared". A declared parameter that a request cannot set (the body-derived case) is refused.
- **D6.** REQ rows also carry `text`, so both forms share one schema. `text` is cut at 4000 characters with "…"; `sha` is the whole text's.
- **D7.** An empty `│` among the parameters is skipped. `│x` (no space) is malformed.
- **D8 (tool quirk; a candidate for env-tool-quirks).** A `\uXXXX` typed in ANY tool-call text (Edit, Write, Bash heredoc) lands in the file as the literal character; `\n` and `\x00` stay escapes. I rebuilt the escapes by script at run time. Also, a timing variant's REQ substitution failed silently for that reason (count 0). I fixed it with `chr()`.
- **D9 (rule slip).** At 21:42Z one read-only Bash call began with a top-level `cd /tmp && grep` (AF-AP-249). There was no other cd.
- **D10.** Fences: only lines of exactly three backquotes, optionally with a language word, as the brief pinned. In a box message, a `~~~` line, a four-backquote line or an indented fence is text and refuses all requests.

## 12. Self-attack
- **Could a box run twice?**
  - The fallback binds by sha (:1581: one run, one receipt, one bind row; V37 KILLED).
  - Duplicate ids are refused across the two forms (:1623; V35).
  - A later Stop reads only new bytes: 129 bytes, no new run (:1762; V38).
  - A stale box's row stays single (:1639).
  - A box's lines are consumed, so a REQ-shaped line in its body is never a second request (:1467).
- **Could it run something it should not (D-111)?**
  - Values and the body are argv elements handed to stack.py, never a shell (:1672: no file created).
  - The label comes from the registry. Unknown keys are refused by the runner.
  - Stale boxes and illustrations never run (:1639, :1540).
  - The body fills only the stack's named body. A line that also sets it is refused, and so is a body for a stack with no body.
  - The hook reads assistant text only. The unchanged LS-B10 tests (V2, V3, V12, agent id) pin that sidechain, tool_use and tool_result records are skipped.
- **Could it go unanswered?**
  - Every current-nonce box gets exactly one receipt: the 15 malformed cases, plus `?` for a broken top edge (:1655).
  - The reconciler, cap, budget and fallback paths cover boxes (:1696, :1730, :1745, :1581, :1605).
  - Silent by design (the brief's rule): a box with no nonce, and a non-current box broken on its own grammar.
  - Untested: the split-block case (NOT DONE 6).
- **Top three risks and how I ruled each out:**
  - (1) A REQ regression through the HIGH-risk parse_message: ruled out by the differential probe (0 differences) and 286 unchanged tests.
  - (2) Fixtures that cannot carry production bytes: addressed by the raw-UTF-8 probe.
  - (3) Mirror tests: every new test kills a named mutant, and the red run at the PIN matched exactly.

## 13. Evidence tiers
- **VERIFIED:** premise; the gates; red at the PIN; the mutants; the probes; the timing; the apply checks; the hashes; the U+2028/9 check; pyflakes; line lengths.
- **INFERRED:** the patch applies at HEAD 3f18bc0 (the files are identical); the registration patch needs no change beyond what gate 2 exercises.
- **ASSUMED:** the real harness's record layout for an assistant message that holds a box matches the fixture's.

## 14. Housekeeping
- I removed all my worktrees (wt, wtred, wtmut, wtreg, wtp); `git worktree list` shows none. No process of mine is running.
- Shared tree: only `?? tasks/briefs/labeling/LS-B11.patch` is mine. The two SCRUB2 files beside it belong to another lane.
- No commits, pushes, PC bridge use or `.claude/` edits. I never touched the live `.jev/`. I read no secret file.
- S1-RATE given this stretch: s1-b2be160d rel=1 use=1, and s1-537b6a4a rel=1 use=1.
- Evidence (logs, probes, drivers): /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/lsb11-lane/ (PROGRESS.md, gate1c/gate1d/gate2c/gate2d.log, red2.log, red2-check.txt, mut-final2-*.log, diff_probe_final.out, probe_utf8b.log, timing*.out, final/).