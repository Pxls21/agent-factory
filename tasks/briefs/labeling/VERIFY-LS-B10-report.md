# VERIFY-LS-B10 report (task #364)

> **Coordinator note (2026-09-29 16:2xZ):** extracted by `scripts/stack.py harvest` (run s-20260929T162443Z-837e26; hand-back sha256 prefix de7d1104d199, 39,367 characters). Served model: claude-opus-5-5 on all 284 assistant records, 0 refusal stops, 1 compaction. `report_lint`: 2 OK and 2 MISS, both on the right lines (`scripts/ls_req.py:584` is `def known(c, idx, seen):`; `tests/test_session_hooks.py:4` is the eight-hooks text); no local ids. The gate recommendation is NOT-READY on F1, conditional on the reading that a byte-identical repeat of a request line is a request of its own. The coordinator's rulings: (1) F1 BLOCKS. The contract's item 4 gives every request line exactly one receipt, refusals included, and names `duplicate id` as a status; the refusal text itself says every request line takes a new id; so a repeated line is a request whose receipt is `refused: duplicate id`, and on the fallback path it gets none (in S2 the Stop exits 0 on the model's unanswered line). It contradicts a frozen criterion (D-034); LS-B10's one focused repair (D-031) goes to it. (2) F11 (D2): item 7's specific wording governs; the chain-end git report reports as the harness's own check would, once per chain, and item 10's never-block rule covers request handling only. (3) Round 2 also takes F4 (the same silent-drop class under the builder's own cap model; the fix is safe whatever the harness does), F6's never-run and window tests (standing rule 14: the never-run sources are the injection boundary) and F10 (a false status line); the other follow-ups are GitHub issue #84.

VERIFY-LS-B10 REPORT (task #364, D-108 item 6)
Lane: sandbox adversarial-verifier, Opus 5.5 (claude-opus-5-5). PIN: 757ca51 (origin `claude/soundbox-kit-migration-iz1jwf`). Last stamp from `date -u`: Tue Sep 29 16:19:25 UTC 2026.

TL;DR: NOT-READY, on one finding (F1). On the `last_assistant_message` fallback path, a byte-identical repeat of a request line gets no receipt, no ledger row and no reconciler report. In one shape the Stop also exits 0, so the turn ends on the unanswered line.
- Nothing reaches a shell.
- Nothing stale or foreign runs.
- No double run reproduced on a verified trigger.
- Everything else is FOLLOW-UP or INFO.

- [x] 1 Premise: every line identical (43 passed, set=35c6a92807a9).
- [x] 2 No shell: 45 hostile cases gave 45 receipts, 45 ledger rows and 16 runs. Every value reached `stack.py` as ONE argv element after `--`. No `touch` target appeared.
- [x] 3 Current turn only, once:
  - Every intact-nonce shape got exactly one receipt.
  - Stale lines never run or block.
  - REQ lines in tool_use inputs, tool results, sidechain records and agent_id payloads never run.
  - A second Stop never re-runs.
  - A mangled nonce is silent (disclosed; F9).
- [ ] 4 Nothing drops without a word: FAILS on the fallback path (F1).
  - P3a, P3b, P1, interrupt, API error, budget and cap-1 pass.
  - A SIGKILL mid-run leaves a false "it did not run" (F2, trigger unverified).
  - Stop cap+1 loses a refusal under the builder's own cap model (F4, harness side inferred).
- [x] 5 Transcript read:
  - Shrink, resume with SessionStart, compaction, a partial line, and 1.5 MB and 3 MB records all pass.
  - A new path with no SessionStart forgets the old file's request (F7, trigger unverified).
  - Timing matches the builder's.
- [x] 6 Ledger and pairing: the pairing holds on my fixture. 6 sessions x 60 concurrent receipts gave 360 rows and 0 bad lines.
- [x] 7 Other Stop hooks: the patched retro gate defers, then fires at the chain end and writes its sentinel then. The git report matches the harness check in 8 of 9 repo states.
- [x] 8 Off switch and failure: pass. The chain-end git report blocks a Stop that has no request (D2; F11 needs a ruling).
- [x] 9 Patch: applies at 757ca51 (identical at 1f30c40). With the patch: 184 passed and 328 passed. The manifest check FAILS with the patch (expected; F12).
- [x] 10 Mutation:
  - The builder's mutants: 70/70 and 14/14 killed after their controls.
  - Of my 14: 2 killed, 10 survived, 2 equivalent or near-equivalent (F6).

## GATE RECOMMENDATION

NOT-READY (F1). This depends on two things I did not reproduce live:
- (a) The transcript lag was SIMULATED on fixture transcripts through the real hook entry, the same way the builder's own fallback test simulates it. The fallback's live frequency is unmeasured.
- (b) It uses the brief's literal reading: a byte-identical repeat line is a request of its own ("exactly one per request, always"; "drops with no receipt and no reconciler report").

If the coordinator rules that a byte-identical repeat of an answered line is not a separate request, F1 becomes a FOLLOW-UP and the recommendation is MERGE-READY-WITH-FOLLOWUPS.

I considered CONTRACT-INVALID and rejected it:
- The premise matched.
- D2 is a tension that item 7's specific wording resolves, not a contradiction.

## FINDING INVENTORY (no severity filter)

Each finding carries these fields: class, evidence, contract, canonical path, effect, reproduction and fix.
- Scratch paths are relative to `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vlsb10/`.
- `harness.py` imports test_ls_req's `World` from `vlsb10/wt`. Before re-running any attack, re-create that worktree: `git -c core.hooksPath=/dev/null worktree add -q --detach <scratchpad>/vlsb10/wt 757ca51`.

**F1. BLOCKER. The fallback path absorbs a byte-identical repeat of a request line, with no receipt.**
- Evidence: VERIFIED, with a transcript-path control for each shape.
- Mechanism (primary source, `scripts/ls_req.py:584-595`, `known()`):
  ```python
  if row.get("sha") == c.sha and (row.get("uuid") is None or c.uuid is None):
      return "same"
  ```
  - A fallback candidate has no uuid, and neither does a fallback ledger row.
  - `cmd_stop` skips every "same" and writes no row and no receipt for it (`:1028-1030`).
  - `reconcile` uses the same `known()` (`:857-859`), so the next prompt is silent too.
  - `sha` covers the whole request: the head line plus every block body and end word (`:506`).
- Shapes (`attack4.out`, `attack4b.out`):
  - S1: the same line twice in the final message, through the fallback.
    - That Stop: rc 2, 1 receipt (`r1 ran`), 1 row.
    - When the record arrives, the next Stop: rc 0, 0 receipts, still 1 row.
    - The next prompt: no report.
  - S1 control, on the transcript path: rc 2, 2 receipts, 2 rows. The receipts are `r1 ran` and `r1 refused: duplicate id (r1 is taken for this nonce: every request line takes a new id)`.
  - S2: a fallback round runs r1, then a later message of the same turn re-issues the identical r1 line.
    - That Stop: rc 0, 0 receipts, 1 row. The turn ends.
    - The next prompt: no report.
  - S2 control: a transcript round, then the identical re-issue. rc 2, `r1 refused: duplicate id …`, 2 rows.
- Scope:
  - Tested: byte-identical repeats (same nonce, id, label, parameters and blocks).
  - A same-id line with other text gets `duplicate id` on both paths, because its sha differs.
  - Static, not run: two byte-identical malformed current-nonce lines (id `?`) are absorbed the same way.
  - Static, not run: the reverse order (a transcript row first, then a fallback candidate) absorbs the fallback candidate. The later transcript record then gets `duplicate id`, because the row carries a uuid.
- Contract:
  - LS-B10-brief item 4 and its TESTS line ("exactly one per request, refusals included"). `duplicate id` is one of the listed statuses.
  - VERIFY brief items 3 and 4, and the core-blocking clause.
  - It falsifies the builder's evidence line "A duplicate id is refused within a round and across rounds" on this path.
- Canonical path: the real entry (`main` → `cmd_stop` → `collect` → `known`) at the PIN. The lag is a fixture: the transcript lacks the final record while the payload carries `last_assistant_message`.
- Effect:
  - A request line gets no receipt, no ledger row and no reconciler report.
  - In S2 the exit code changes from 2 to 0, so the turn ends on the model's unanswered line.
  - Nothing runs twice, and nothing runs that should not.
- Reproduction: `attack4.py` (cases S1, S1b, S2 and their controls) and `attack4b.py` (the next-prompt checks).
- Fix: match by occurrence, not by text.
  - A fallback row absorbs at most ONE transcript line: the first one in transcript order, at or after the fallback round's `read`.
  - Bind that line, for example with a `bind` row carrying its uuid and line. A later identical line then reads as `dup`.
  - Within one fallback text, "same" needs the same `line`.
  - Keep scratch case 5d' green: the record that carried a fallback line must still read as "same", so nothing runs twice.
  - Add two tests: the identical line twice through the fallback, and the identical re-issue after a fallback round. Each must end with a `duplicate id` receipt and exit 2.

**F2. FOLLOW-UP (trigger UNVERIFIED). After a SIGKILL mid-run, the orphan runner finishes and the reconciler says "it did not run".**
- Evidence: the mechanism is VERIFIED (`attack4c.out`). The trigger is UNVERIFIED: I do not know whether the harness ever SIGKILLs a Stop hook, and the harness binary read was denied.
- "KILL during first request":
  - Hook rc -9, no ledger row, `read` not advanced.
  - The step finished, and runs.jsonl holds the run.
  - The next prompt said `unanswered: r1 medium (unknown: …)` under the header "(`unanswered`: it did not run; re-issue any still wanted, with a new id)" (`context_text`, `:874-891`). That claim is false.
- "KILL first, turn continued": the next Stop re-ran r1. runs.jsonl shows 2 runs, and the step ran again.
- SIGTERM is handled: the runner and its step end, the hook exits 143, and "unanswered" is then true.
- Contract: items 4 and 5 (a true receipt). The core-blocking "runs twice" shape appears only in the turn-continued variant. That variant needs another Stop hook to block at the same Stop, and the retro gate defers there, so it is unlikely.
- Canonical path: the real hook and a real runner. The SIGKILL comes from the fixture.
- Effect: a false "did not run" in the next prompt's context. The re-issue it advises runs the stack twice.
- Reproduction: `attack4c.py`.
- Fix: write a `started` ledger row (with the run dir or the runner pid) before `Popen`.
  - The reconciler can then say "started, outcome unknown: see `.jev/stacks/runs.jsonl`".
  - No Stop re-runs a started request.
  - The builder's line "Covered, not silent: a hook killed mid-round" should name this case.

**F3. FOLLOW-UP. When both the ledger row and the state save fail, the next Stop re-runs the request.**
- Evidence: VERIFIED (`attack_s6.py`, `chattr +i` on `sessions/` and a directory as `ledger.lock`): 2 runs. The output went to the console; `progress.txt` records the result.
- What happens:
  - The round still delivers its receipt, with "NOT WRITTEN: …", and exits 2.
  - The turn continues.
  - The next Stop finds the same line with no row and an unadvanced `read`, and runs it again.
- Contract: the core-blocking "runs twice" shape. But the trigger is a double write failure in the environment, and the hook announces it each time. The coordinator may promote it.
- Fix: no run without a durable record. Write F2's `started` row first. If that write fails, refuse with "not started: the ledger is not writable" and run nothing.

**F4. FOLLOW-UP (harness side INFERRED). At Stop cap+1 and later, the hook still blocks, marks its refusals delivered, and never carries them.**
- Evidence: the hook side is VERIFIED (`attack4.out`, S3).
  - With the env var unset, Stops 7, 8, 9 and 10 exit 2 with `refused: cap: …`.
  - At Stop 9 the row reads delivered `feedback` and undelivered is 0. The next prompt's context is the nonce line alone.
  - The harness drop above the cap is the builder's own model (PM P2). The hook's own text says "above 8 the harness ends the turn and drops this text". I did not reproduce the drop: the binary read was denied and there is no live registration.
- Code: `at_cap = n >= ctx.cap - 1` (`:1066`). Once written, the receipts leave `undelivered` whatever `n` is (`:1130-1131`).
- Contract: this is the core-blocking "drops with no receipt and no reconciler report" IF PM P2 holds. The builder's self-attack 3 covers a different case (the harness counting differently); this one follows from the builder's own model.
- Reach: the model writes REQ lines after two cap refusals, or blocks from other hooks raise the count.
- Effect: a refusal receipt that no one sees. Nothing ran.
- Fix: when `n > ctx.cap`, write the receipts as delivered `no`, keep them in `undelivered`, and exit 0. The next prompt reports them. This is safe whatever the harness does.

**F5. FOLLOW-UP (trigger UNVERIFIED). A prompt hook that runs during a Stop round loses its nonce.**
- Evidence: the mechanism is VERIFIED (`attack_race.py`; console output, recorded in `progress.txt`).
  - `cmd_stop` loads the state at its start and saves it after each request and at its end.
  - A `cmd_prompt` that saves a new nonce in between gets overwritten.
  - The next REQ line with the new nonce gets `refused: stale nonce (not this turn's)` with rc 0. The next prompt reports it as delivered late.
- Trigger: can UserPromptSubmit fire for a session while that session's Stop hooks run? Unmeasured.
- Effect: a wrong stale refusal. No run, no drop.
- Fix: a per-session state lock (flock on `sessions/<s>.lock` around load and save), or merge the nonce set at save.

**F6. FOLLOW-UP. Ten of my mutants survive the builder's suite, on the never-run and window clauses.**
- Evidence: VERIFIED. Each mutant ran against the whole `tests/test_ls_req.py`. Control: `CONTROL identity=True rc=0 43 passed in 28.40s` (`mut/my1.log`).
- SURVIVED (43 passed each):
  - V1: the subagent guard dropped (`agent_id`).
  - V2: sidechain records read.
  - V3: a tool_use input read as text.
  - V12: a tool_result read as text.
  - V5: the Stop ignores a new transcript path.
  - V6: the Stop ignores a shrink.
  - V7: `ended()` does not reset after activity.
  - V8: `how_ended` names an earlier marker.
  - V9: the git report at the cap.
  - V10: the prompt ignores a path change.
  - V11: the NUL check dropped (equivalent: the runner refuses NUL too).
  - V13: `MIN_START_S` dropped (near-equivalent).
- KILLED:
  - V4 (an identical line read as "same"), by `test_a_duplicate_id_is_refused_within_a_round_and_across_rounds`. That test covers the transcript path only.
  - V14 (an interrupt not read as an ending), by `test_a_signal_to_the_hook_ends_its_runner_and_the_request_is_reported[15]`.
- My attacks detect V1, V2, V3, V12 and V6 (`mutcheck.out`). At the PIN the behavior is correct for every one of them (items 3 and 5). Only the test lock is missing.
- Contract: standing rule 14 (tests for the security boundary) and VERIFY item 3's "must never run" sources. Not core-blocking under D-034, because the behavior is correct.
- Fix: at least, tests that kill V1, V2, V3 and V12 (the never-run sources) and V5 and V6 (window changes).

**F7. FOLLOW-UP (trigger UNVERIFIED). A Stop on a new transcript path with no SessionStart forgets the old file's unanswered request.**
- Evidence: VERIFIED (`attack5.out` 5b).
  - The Stop reanchors on the new file, says so, and runs r2.
  - The next prompt reports nothing about r1 in the old file.
  - When SessionStart(resume) runs first (5b'), r1 is reported.
- Trigger: a new path with no SessionStart run, for example when the SessionStart hook failed or timed out. Unverified.
- Fix: on a path change at the Stop, reconcile the old file's `[turn_start, EOF)` first. The prompt hook's `reconcile` already reads the state's old path.

**F8. FOLLOW-UP (low). The prompt hook resets silently when the transcript shrank below `turn_start`.**
- Evidence: VERIFIED (`attack4.out` S4 and S4b). The context is the nonce line alone, and there are 0 rows.
- The Stop path announces its reanchor; the prompt path does not.
- Trigger: a transcript that shrinks. Whether the harness ever truncates one is unknown.
- Fix: add one line to the context: "the transcript changed; the last turn's requests could not be checked".

**F9. FOLLOW-UP (disclosed, NOT-DONE 10). A mangled nonce is silent.**
- Evidence: VERIFIED (`attack3.out`). Three shapes gave no receipt, no row and no report:
  - a ZWSP inside the nonce;
  - a Cyrillic "а" inside it;
  - fullwidth digits.
- A lookalike or zero-width REQ keyword with an INTACT nonce is answered (`refused: malformed`).
- The frozen shapes keep the current nonce intact, so this case is outside them.
- Fix idea: apply NFKC and remove zero-width characters. A line that then carries a current nonce gets `refused: malformed (the nonce is mangled)`.

**F10. FOLLOW-UP. Stale hook-count text, locked by a test.**
- Evidence: VERIFIED by a static read of the PIN and the patch.
  - `scripts/install_session_hooks.py:2` says "register the eight project hooks".
  - `:176` (`:191` after the patch) prints `installed 8 in`.
  - `tests/test_session_hooks.py:4` repeats the text, and `:117-120` `test_fresh_install_registers_the_eight_hooks` asserts `"installed 8" in r.stdout`.
- The installer registers 10 hooks at the PIN and 13 with the patch. The patched test file asserts `len(cmds) == 13` beside the old assertion.
- The builder listed this under ADJACENT DEFECTS. The patch edits both files and leaves the text.
- Effect: after registration the installer's status line is false (a hollow green in prose).
- Fix, inside the patch: print the count from `our_hooks()` and rename the test.

**F11. FOLLOW-UP (ruling). D2: the chain-end git report blocks a Stop that has no current-nonce REQ line.**
- Evidence: VERIFIED by the builder's `test_the_chain_end_runs_the_git_checks_once_in_the_harness_checks_words` and by my item-7 git-state runs.
- Contract: frozen item 7 ("reports them as that check would", which blocks) against item 10 ("a Stop with no current-nonce REQ line never blocks"). Item 7 reads as the specific exception.
- The report fires at most once per chain, only when `stop_hook_active` is true and the count is under cap-1.
- Fix: a coordinator ruling that records the exception.

**F12. FOLLOW-UP (disclosed, NOT-DONE 2). The vendored manifest fails with the patch.**
- Evidence: VERIFIED.
  - `vendored_manifest.py --check`: FAIL with the patch (generated a8ff9032f3c3…, committed cc841d92833c…), PASS without it.
  - `test_committed_manifest_matches_fresh_generation`: 1 failed with the patch, 1 passed without it.
- Fix: regenerate at the registration HEAD, covering the two unrelated SKILL.md edits the builder named.

**F13. FOLLOW-UP (disclosed, NOT-DONE 9). There is no retention, and every hook run reads the whole ledger.**
- Evidence: static. `ledger_index` (`:540-562`) reads `ledger.jsonl` whole on every Stop and every reconcile, so the cost grows with the ledger. Not measured at scale.
- Fix: rotate by session age, or index by session.

**F14. FOLLOW-UP. The neutralizer changed after the PIN.**
- Evidence: VERIFIED.
  - I ran `git log 757ca51..origin/claude/soundbox-kit-migration-iz1jwf` over the files ls_req runs and the files the patch touches, at the local origin ref 15a326b (no fetch).
  - It shows one commit: 0de29b2 "handback_extract --local-ids: also list an id that resolves to a local commit origin does not hold (13:4xZ)".
  - `ls_req.py` loads `scripts/handback_extract.py` as its neutralizer (`HANDBACK`, `:109`).
- Fix: re-run `tests/test_ls_req.py` and the patch's tests at the registration HEAD.

**F15. FOLLOW-UP (minor). A cap that is set but invalid falls back to 8, which fails open.**
- Evidence: VERIFIED (`attack4.out`, the S3 cap cases).
  - `'4'` runs at Stop 2.
  - `'1'`, `'0'` and `' 3 '` refuse.
  - `'abc'`, `'-1'`, `'4.5'` and `'99999'` fall back to 8 (`Ctx`, `:217-221`, `[0-9]{1,4}`).
  - The note naming the bad value appears only in a cap refusal.
- Effect: the harness might parse such a value lower (for example `4.5` as 4). Rounds at Stops 5 and 6 would then run while the harness drops their feedback. Hypothetical: it needs an odd owner setting.
- Fix: when the cap is set but does not parse, refuse every request and say why, instead of assuming 8.

**F16. FOLLOW-UP (minor). Two quiet paths.**
- `save_print` returns None on OSError (`:752-762`). The receipt shows this only when a cut needs the file name ("not saved").
- `bad_ledger_rows` (ledger lines that do not parse) appear only in `hooks.jsonl`. A torn row would make its request look unanswered.
- Fix: one head line in the receipt when either happens.

**F17. INFO. The git report differs from the harness check for unpushed unsigned commits under `commit.gpgsign=true`.**
- Evidence: VERIFIED (`attack7.out`, 9 scratch repo states; I ran the harness check only on scratch repos).
  - In this state the harness reports "… GitHub will show as Unverified …" first.
  - ls_req reports "There are 1 unpushed commit(s) …".
  - The other 8 states match word for word.
- Contract: frozen item 7 asks for "the same dirty and unpushed checks", and `git_report`'s docstring (`:767-769`) leaves the signing check out on purpose. This is within the contract.

**F18. INFO. A Stop hook error is invisible to the model in that turn.**
- The one-line error goes to stderr with exit 0 (item 8, VERIFIED). The harness does not feed that to the model (INFERRED from the hooks docs).
- The request lines stay unanswered. The next prompt's reconciler reports them, because it reads from `turn_start`, not from `read`. `attack4c.out` shows this: r2 was reported although `read` had passed it.
- So it is not silent overall.

**F19. INFO. A budget stop carries the status `refused`.**
- Example: `refused: budget (stopped after 7 s …; the runner exited 143)` for a run that started and was killed. Its steps may have partly run.
- The text is accurate; the status word is not.
- Fix idea: a `stopped` status.

**F20. INFO. TN1 is refuted; P10 was not observed.**
- TN1 (an interrupted request runs at a notification query's Stop) came from my fixture, which left out the prompt hook.
- The live `.jev/system1.jsonl` (read for counts and timestamps only) shows the prompt hook runs for those queries and reconciles:
  - 252 of 296 UserPromptSubmit runs carry `why=harness-event`;
  - a UserPromptSubmit falls within 5 s of 15 of 15 task-notification records and 17 of 17 peer records.
- P10: 0 UserPromptSubmit runs fall within 5 s of the 60 Stop-feedback records. This fits the builder's model: a blocking Stop continues the same query.

**F21. INFO. No double registration (static).**
- HOME is /root.
- The installer writes absolute-path commands into `/home/user/.claude/settings.json`. That is the project settings file for sessions rooted at `/home/user`.
- The patch writes `$CLAUDE_PROJECT_DIR` commands into the repo's `.claude/settings.json`, which sessions rooted at the repo read.
- A session reads one of the two. hooks.md:414 also runs an identical handler only once.
- The unquoted `$CLAUDE_PROJECT_DIR` matches the spelling of the existing entries.

**F22. INFO. The hooks run in parallel (hooks.md:414).**
- "Last in its list" means list order, not run order.
- `defer-check` works from content and never reads the ledger, so the retro gate cannot race the Stop round (VERIFIED, `attack7.out`, 7 cases).

**F23. INFO. Control bytes reach the step as data.**
- SOH, ESC and DEL in a value, and VT, FS, U+2028 and NEL in a block body, reach the step verbatim as argv, never through a shell.
- A CRLF head runs with the CR stripped. A CRLF block keeps `body\r`, and the runner refuses it.
- A step that prints these bytes could carry them into the receipt; the neutralizer handles tags only.

**F24. INFO. One malformed current-nonce line after the requests refuses every request of that message.**
- This is by design: the request lines must close the message. It showed up in my first pairing fixture.

**F25. INFO. `defer-check` misses a final record over 2 MiB when `last_assistant_message` is absent.**
- `attack5.out` 5e: a 3.0 MB record gives rc 1 (no defer); a 1.5 MB record defers.
- When the payload carries `last_assistant_message` (the normal case), it defers.
- The effect is PM P6's retro beside the receipts, not a drop.

**F26. INFO. A partial last line over 64 KB puts `turn_start` mid-line.**
- `attack5.out` 5f. The next Stop ran r1. Harmless here.

**F27. INFO. The scan is slower on assistant text.**
- `attack8.out`, the prompt hook over a 100 MB window: 45.0 MB/s for assistant-text records and 136.3 MB/s for tool-result records.
- The builder's "about 90 MB/s" is an average. A 100 MB assistant-text window costs about 2.2 s, well under the 30 s timeout.

**F28. UNVERIFIED. Records that mix thinking and text are skipped whole.**
- This is the builder's self-attack 1; I did not re-test it.
- It would be silent if the harness ever wrote such a record. The builder found single-block records in 4,250 of 4,250 cases in the tail.

**F29. INFO (disclosed, NOT-DONE 4). Runner prints are not scrubbed.**
- The model sees the same text a tool call would show, so the exposure is not new.
- `out/<session>/` keeps the prints at mode 0600.

## PER-ITEM RESULTS

1. **Premise.** Re-run in a clean detached worktree at 757ca51. Every line is identical:
   - HEAD 757ca51; the log lines 757ca51 and 1f30c40.
   - The four sha256 values.
   - 1181/1058/391 lines (2630 total).
   - `patch-applies`; the stat of 4 files, 239 insertions and 12 deletions.
   - Every `grep -c` is 0, with `[rc=1]`; `ls` gives `[rc=2]`.
   - `1 files set=35c6a92807a9`; `pytest-summary: 43 passed` (raw: `pytest-summary: 43 passed in 50.80s`).

2. **No shell.** 45 hostile cases (`attack2.py`), each run twice: once with a shim that logs argv, once through the pristine entry. The receipts were identical ("differing: []"). Totals: 45 receipts, 45 ledger rows, 16 runs; no `touch` target appeared; each value was ONE argv element after `--`.
   - `q=` with backquotes, `$( )`, `;` and `|`: ran, and the value printed back verbatim.
   - A newline inside a block: the runner refused it with `a text holds no NUL and no newline`.
   - The end word as an exact line inside its own block: `malformed (text after the request lines)`.
   - An unclosed block: malformed.
   - `=` inside a value: kept.
   - A duplicate key: the runner refused it with `repeated key 'q'`.
   - A label with a path or shell characters: `? refused: malformed (the label '../stack' is not a stack label)`.
   - The labels `rate` and `explain`: `unknown label`.
   - A value with a leading `-`, and a path outside the tree: runner refusals.
   - NUL: `malformed (a value holds a NUL character)`.
   - VT, FF, FS, NEL, U+2028 and a tab in the head: malformed, with the code point named. Other control bytes: see F23.
   - A lone surrogate: `refused: the runner did not start: 'utf-8' codec can't encode …`.
   - 600 characters: the runner refused it (TEXT_MAX 500).
   - Globs, `~` and `$HOME`: passed verbatim.
   - A REQ line nested inside a block: stays text.

3. **Only the current turn's requests, each once** (`attack3.out`).
   - A stale quoted line never runs or blocks. The next prompt says `delivered late: RES <n1> r1 refused: stale nonce (not this turn's)`.
   - 28 intact-nonce shapes each got exactly one receipt or ran: a fence, bold, NBSP, a line over 200 characters, and lookalike and zero-width REQ keywords. An unclosed fence BEFORE the request ran, and so did a line over 200 characters.
   - A mangled nonce: silent (F9).
   - The same id twice, in one message or in a later block: one run plus `refused: duplicate id` on the transcript path. The fallback path is F1.
   - REQ lines in tool_use inputs, in tool_result content, in sidechain records and in an `agent_id` payload: never ran.
   - Two Stops in one turn: no re-run.

4. **Nothing drops without a word** (`attack4*.out`).
   - The fallback identical repeat fails (F1).
   - P3a (requests in an earlier text block of the final message): 2 ran.
   - P3b (a thinking-only final message): ran.
   - P1 (`stop_hook_active` true): ran.
   - Interrupt: `unanswered: r1 echoargs (an interrupt, transcript record i3)`, 0 runs.
   - API error: `unanswered: r3 echoargs (an API error, transcript record e6)`, 0 runs.
   - Budget of 7 s, 7.2 s in all; the sleeper did not outlive the hook:
     - r1: `refused: budget (stopped after 7 s, at the 7 s round budget; the runner exited 143)`;
     - r2 and r3: `(… not started)`.
   - Cap with the env var unset: Stop 6 ran; Stops 7 to 10 refused with exit 2. Stop 9 and later: F4. With the env var set: F15.
   - A hook crash mid-round:
     - SIGTERM (my run) and SIGINT (the builder's test, parametrized `[2]`) are handled. The runner and its step end. The next prompt reports what did not run, and `delivered late` for what did.
     - SIGKILL: F2.
   - Receipts per request: exactly one in every shape except F1.

5. **The transcript read** (`attack5.out`, `replay.out`).
   - A shrink at the Stop: reanchored with the note "(the transcript changed under this session's state: only its last 2097152 bytes were read)"; r2 ran.
   - A new path: F7. SessionStart(resume) on a new file reconciles r1.
   - A compaction boundary inside the window: r1 and r2 ran.
   - A partial last record with no fallback text: exit 0, and the next prompt reports r1 unanswered.
   - The same record with fallback text: r1 ran, and the completed record did not run it again (5d').
   - 1.5 MB and 3.0 MB records with the REQ at their end: ran. `defer-check` on them: F25.
   - Timing: a replay of the lane's 41,943,040-byte tail (14,003 lines; 47 prompt, 79 Stop and 7 SessionStart events). Each cell reads mine; the builder's:

   | Hook | Wall p50/p95/max ms | Own p50/p95/max ms |
   |---|---|---|
   | stop | 86.4/124.6/187.2; 92.1/132.3/176.0 | 2.1/26.8/100.1 (n=77); 3.0/24.5/58.5 |
   | prompt | 85.7/172.8/223.4; 104.0/169.5/261.4 | 3.5/82.4/104.3; 5.7/63.9/152.4 |
   | defer-check | 86.2/115.1/126.9; 102.7/134.2/155.0 | not logged |
   | session-start | 71.3/291.8/291.8; 91.7/145.8/145.8 | 1.7/192.0/192.0; 8.6/61.3/61.3 |

   Stop bytes read: p50 135,690, p95 3,172,450, max 4,763,656. The builder's: 138,189 / 3,133,618 / 4,775,366. Consistent.

6. **Ledger and pairing** (`attack6.out`, `attack6b.out`).
   - Receipts equal rows (3 and 3).
   - For each ran row:
     - its uuid finds the record, and line `row.line` of that record holds the request;
     - the chat before it holds the prompt;
     - `run` is in runs.jsonl and equals the receipt's;
     - `run_dir` exists, and `out` is saved.
   - 6 sessions x 60 concurrent receipts: 360 JSON rows, 60 per session, 0 bad lines, and the file ends with a newline.

7. **The other Stop hooks** (`attack7.out`, in the patched worktree).
   - The retro gate:
     - no state yet: fires;
     - a round whose final message closes on a current-nonce REQ: defers (rc 0, no sentinel), with or without `last_assistant_message`;
     - the chain's end: fires, and writes the sentinel then;
     - a stale line only, the off switch, or empty stdin: fires;
     - HEAD unchanged: exits 0 before the deferral.
   - The git report, compared with `/root/.claude/stop-hook-git-check.sh` (which I read, then ran only on scratch repos):
     - the same words in the clean, unstaged, staged, untracked, no-remote-branch, detached, no-remote and not-a-repo states;
     - it differs for unpushed unsigned commits (F17).
   - Order in the patched `.claude/settings.json` Stop list: the retro gate, then task_sync, then ls_req last. They run in parallel (F22).

8. **The off switch and failure** (`attack8.out` and the builder's tests).
   - `req-off` as a file, as a dangling link and as a directory: every subcommand is silent and exits 0.
   - Seven failure shapes each print one line and exit 0 (for the prompt, the line goes into additionalContext):
     - the state path is a file (prompt, and Stop);
     - a session id with a slash;
     - a relative transcript path;
     - stdin that is not UTF-8;
     - stdin that is a JSON list;
     - an unknown subcommand.
   - A prose-only Stop and a stale-only Stop: exit 0, no output. The one exception is the chain-end git report (F11).
   - Budgets: the Stop round stops at its budget plus a 10 s grace. The worst case (3 s catch-up + 240 s + 10 s) is under the 300 s timeout.
   - The runner's steps write to files with `close_fds`, so `communicate()` after a SIGKILL cannot wait on a step.

9. **The registration patch.**
   - It applies at 757ca51 and is byte-identical at 1f30c40. Nothing between the two touches the patched files. For later origin work, see F14.
   - With the patch, the brief's three files (set=9425e01745d1): `pytest-summary: 184 passed in 103.43s (0:01:43)`.
   - With the patch, the other tests that name a patched path, `tests/test_filepacks.py tests/test_hooks_worktree.py tests/test_jev_context.py tests/test_system1_context.py tests/test_strip_cbm_hooks.py` (set=6351e0d895cc): `pytest-summary: 328 passed in 160.80s (0:02:40)`.
   - The manifest: F12.
   - `python3 harness-ports/tests/test_hermes_hook_adapter.py`: 6/6, with and without the patch.
   - pyflakes is clean, `bash -n` passes on the retro gate, and the settings JSON parses.

10. **Mutation.**
   - The builder's `ls_req.py` mutants on the final bytes, re-pointed at my worktree:
     - control: identity True, 43 passed;
     - then `EXPECTED=70 ROWS=24 KILLED=24`, `ROWS=24 KILLED=24` and `ROWS=22 KILLED=22`, with 0 survived and 0 invalid: 70/70.
   - The patch mutants: `CONTROL identity=True rc=0 5 passed, 32 deselected in 1.61s`, then `EXPECTED=14 ROWS=14 KILLED=14 SURVIVED=0 INVALID=0`.
   - My own mutants: F6.

## THE COORDINATOR'S OBSERVATIONS

- `ls_req.py:242`: `hook_log` is the only fully silent swallow, and it loses only a diagnostics line.
  - The receipt, ledger and reconciler paths are loud: a failed append prints `NOT WRITTEN: …`, an unreadable ledger raises, and an unreadable transcript adds a line to the report.
  - Quieter paths: F16 (`save_print`, `bad_ledger_rows`).
  - The final `save_state` `pass` (`:1132-1135`) gives a double report, not a loss, unless the ledger write failed too (F3).
- AF-AP-175 (`tests/test_ls_req.py:991`): harmless in the fixture. No production path names a ref twice: `git_report` names `HEAD` once (`rev-list <upstream>..HEAD --count`, `:794-795`).
- Root: nothing needs it.
  - As `nobody` with Python 3.11.15: 43 passed in 30.22 s. This count is from my run notes at 15:55Z; that log was not kept, so it is not a paste.
  - Signals go only to the hook's own runner (`killpg` of the runner's own session).
  - The running user creates the state dir with mode 0700.
  - Only my S6 probe used `chattr`, as root.
  - Not run: Python 3.12 as non-root.
- The tail: I reused `scratchpad/tx/tail40m.jsonl` read-only, skipping thinking records by their bytes and printing only counts, bytes and ids. No copy of mine remains. The file itself stays for the coordinator to delete.

## BLOCKING PREDICATE

F1 meets all five conditions, so it blocks:
1. Contract: LS-B10 item 4, its TESTS line, and the core-blocking clause.
2. Reproduction: the real entry at the PIN, with the lag simulated the way the builder's own test simulates it.
3. Effect: a missing receipt, row and report; in S2, exit 0 instead of 2.
4. Discriminator: S1 and S2 against their transcript-path controls.
5. Ownership: the fix lives in `known()` and its tests.

The others do not block:
- F2 fails condition 2: the SIGKILL trigger is unverified.
- F3 fails condition 3 as a normal-path effect: it needs a double write failure in the environment, and the hook announces it each time. The coordinator may promote it.
- F4 fails condition 2: the harness drop is not reproduced (it is inferred from PM P2).
- F5 and F7 fail condition 2: their triggers are unverified.
- F6: the behavior is correct, so it is not core-blocking under D-034.
- F8 to F29: none meets conditions 1 and 3 together.

## WHAT MUST HOLD BEFORE REGISTRATION

1. F1 fixed, its two fallback tests added, and a short re-verify: S1, S2, and 5d' with no double run.
2. A ruling on D2 (F11).
3. F4: at Stop n > cap, carry the receipts and exit 0.
4. The never-run and window tests (F6): kill V1, V2, V3, V12, V5 and V6.
5. F2 and F3: a `started` ledger row before each run, and no run when that write fails. Or the owner explicitly accepts both.
6. F5: a per-session state lock, or a measurement showing UserPromptSubmit cannot fire while the session's Stop hooks run.
7. The manifest regenerated at the registration HEAD (F12).
8. The "eight hooks" text and its test fixed inside the patch (F10).
9. The P13 instruction text on when to use the form (the builder's NOT-DONE 6).
10. `tests/test_ls_req.py` and the patch's tests re-run at the registration HEAD (F14).
11. The first live run measures and logs:
    - that the Stop's exit-2 feedback reaches the model;
    - that the prompt and SessionStart additionalContext reach the model;
    - what happens when two Stop hooks block at once;
    - how often the fallback fires (count `"lam": true` in `.jev/req/hooks.jsonl`). This sets F1's real reach.

## REPRODUCED, STATIC, SKIPPED

- Reproduced through the real hook entry, with state dirs of my own under `/tmp/vlsb10` (now deleted):
  - items 1 to 10, as above;
  - the mechanisms of F1 to F10;
  - the timing replay;
  - the non-root run;
  - the harness git check, on scratch repos only.
- Static only:
  - The harness binary facts from two greps made before the denial: `stop_hook_summary.hookErrors` holds blocking errors only; a timed-out hook is skipped; an abort writes no summary.
  - hooks.md: hooks run in parallel; an identical handler runs once; UserPromptSubmit's default timeout is 30 s.
  - F4's harness drop (PM P2).
  - F18's "exit-0 stderr is not shown to the model".
  - F21.
  - The two scope notes in F1.
- Skipped, with reasons:
  - The full `tests/test_vendored_manifest.py`: it copies about 3.4 GB and the disk had 6.8 GB free. I ran `--check` and the freshness test instead.
  - Python 3.12 as non-root. The coordinator's 3.12.3 run covers 3.12 as root.
  - The harness's cap logic: the auto-mode classifier denied a third read of the harness binary, and I did not pursue it through another tool.
  - Any live registration: the brief forbids it.
  - F28, the mixed-record residual.

## STANDING-RULE DISCLOSURES

- Worktrees:
  - I made both of mine with `git -c core.hooksPath=/dev/null worktree add -q --detach`: `vlsb10/wt` at the PIN, and `vlsb10/wt2` at the PIN with the patch applied inside it.
  - I removed both with `git worktree remove --force` (rc 0). `git worktree list` shows neither, and their admin dirs are gone.
  - `/tmp/vlsb10` is deleted.
- No git write in the shared tree, and no fetch. Read-only git only: one `git status`, plus `git show`, `git log`, `git grep`, `git cat-file`, `git merge-base --is-ancestor` and `git worktree list` against the object store.
- Never registered:
  - No patch applied in the shared tree.
  - The installer ran only inside the test suite, against tmp targets.
  - `/home/user/.claude/settings.json` and the repo's `.claude/` were not touched; only the premise's `grep -c` read the settings.
  - The live `.jev/` was not written.
- Live data, read-only:
  - `.jev/system1.jsonl`, for counts and timestamps (F20);
  - the transcript tail, with thinking records skipped by their bytes, printing only counts, bytes and ids.
- No secret file read. No subagent, no PC bridge, no outward action.
- Rule slips, none of which changed a result:
  - a top-level `cd` in my first Bash call;
  - six read-only calls in the final pass: five `cd /tmp && git -C …`, and one `cd /home/user/agent-factory` to compute a set id;
  - a typed stamp in my scratch notes, corrected and marked there.
- S1-RATE lines, each written as a text of its own: `S1-RATE s1-9a9d8c9d rel=2 use=1`, `S1-RATE s1-9dd896ca rel=2 use=3`, `S1-RATE s1-e4827bd1 rel=1 use=0`.
- Processes: none of mine remain; a check at 16:19Z found 0 probe processes. At 16:14Z a pytest (pid 16881, `tests/test_hooks_worktree.py …`) and a `sleep 5` (the memory monitor) were running. Neither is mine, and I did not touch them.

## SCRATCH KEPT

Directory: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vlsb10/`
- `harness.py`.
- `attack2.py` to `attack8.py` with their `.out` files, including `attack2-real.out`, `attack2-shim.out`, `attack4b/c/d` and `attack6b.out`.
- `attack_race.py` and `attack_s6.py`: console output only; the results are in `progress.txt`.
- `replay.py` and `replay.out`; `mutcheck.py` and `mutcheck.out`.
- `item9a.log`, `item9b.log`, `premise_ts.log` and `progress.txt`.
- `mut/`: the builder's drivers and mutants re-pointed at my worktree, `my_driver.py`, `my_mutants.py`, and the logs `chunk1-3.log`, `patch.log` and `my1-3.log`.

Re-create `vlsb10/wt` at 757ca51 before re-running anything.