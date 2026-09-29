LS-B10 REPORT (task #364, D-108 item 6): the chat form. Lane: sandbox code-implementer, Opus 5.5. Last stamp from `date -u`: 2026-09-29 13:11:22Z.

## VERDICT
The chat form is built and gated: `scripts/ls_req.py` and `tests/test_ls_req.py`, plus the registration as `tasks/briefs/labeling/LS-B10-registration.patch`.
- It is NOT registered. Nothing runs `ls_req.py` in the shared tree until you apply the patch.
- All gates are green:
  - `tests/test_ls_req.py`: 43 passed, twice.
  - The clean clone at the PIN with the patch: the brief's 3 files 184 passed; set A 190 passed; set B 520 passed.
  - The Hermes adapter test: 6/6.
- Mutation: 70/70 named mutants killed for `ls_req.py`, and 14/14 for the patch.
- `vendored_manifest.py --check` FAILS on the `.claude/` row, as the brief expected. It is your landing step.

## NOT DONE (first-class)
1. **Nothing is registered or live-tested.** These are UNMEASURED in a live harness session:
   - the Stop exit-2 feedback reaching the model;
   - the UserPromptSubmit and SessionStart JSON `additionalContext` reaching the model;
   - two Stop hooks blocking at once (my receipts plus the harness git check).
   The first live run is yours, after `git apply tasks/briefs/labeling/LS-B10-registration.patch`.
2. **The vendored manifest is stale after the patch** (the `.claude/ (kit-adapted)` row). Regenerate it at landing.
   - The shared tree ALSO has two `.claude/` files modified that are NOT mine: `.claude/skills/build-loop/SKILL.md` and `.claude/skills/env-tool-quirks/SKILL.md`. The regeneration must cover those too.
3. **The export of item 6 is not built.** The pairing is proven on a fixture only.
4. **P12:** runner prints in RES bodies and in `out/` are not scrubbed for secrets.
5. **P11:** the nonce is a replay guard, not a secret. It sits in plain text in a 0600 state file and in the transcript.
6. **P13:** the coordinator's instruction text on when to use the form is not written; it is outside my boundary. The injected line carries the grammar.
7. **P7:** RES via `additionalContext` is not measured. The brief chose exit 2.
8. **Ratings are not accepted as REQ lines.** `rate` is a runner command, not a stack, so it is refused as an unknown label. Use T1 (a tool call).
9. **No retention.** `.jev/req/out/<session>/` is never pruned and `ledger.jsonl` grows without bound. `hooks.jsonl` rotates at 4 MB.
10. **A request line with no current nonce at all** (a missing or mangled nonce) is never answered. See the self-attack.

## PREMISE RE-RUN
`bash scripts/premise_block.sh` from the main tree at 11:07Z. The output is IDENTICAL to the brief's block: `diff premise_expected.txt premise_out.txt` is empty (39 lines).
- It includes 334 passed for set bc6d12c0785b, and the hashes `c69a8191…` stack.py through `3932dc63…` turn-retro-gate.sh.
- HEAD has since moved to 164bf49 [coordinator: the origin id; the lane cited its pre-push local id]. `git log bef1e9e..HEAD` over the four registration files is empty, so the patch applies at both commits (proven below).

## FILES (shared tree, untracked, created by this lane)

| File | Lines | sha256 |
|---|---|---|
| `scripts/ls_req.py` | 1181 | 7dfb0b9d91f8473287e1006ba34d8f54ab282aeefad095d65965af7b301c14aa |
| `tests/test_ls_req.py` | 1058 | cfa360f21aae083e94e3fe32e1835c7606e6191cb0524f0e6bcda7139115a83d |
| `tasks/briefs/labeling/LS-B10-registration.patch` | 391 | b7a5d6c0dbbeeffeaccc21be68f8e348e5491ee3c9e7f3cdd86797e870a47062 |

The patch diffstat (`git apply --stat`):
- `.claude/hooks/turn-retro-gate.sh` +9
- `.claude/settings.json` +27
- `scripts/install_session_hooks.py` +20 −5
- `tests/test_session_hooks.py` +183 −7
- In all: 239 insertions, 12 deletions.

pyflakes is clean on all four Python files. The U+2028/U+2029 separator count is 0 in both of my files.

## CONTRACT ITEMS: EVIDENCE (all VERIFIED by the tests named; each test's docstring names its mutants)

**1. The grammar.**
- The form is `REQ <nonce> <id> <label> key=value ...`. Blocks are `key=<<WORD` … a line that is exactly `WORD`; bodies are verbatim.
- The request lines close their message's text: prose after them refuses every request of that message.
- Tests: `test_a_well_formed_line…`, `test_a_block_carries_backquotes_fences_and_request_shaped_lines_verbatim`, `test_an_unclosed_block…`, `test_a_non_breaking_space_bold_markup_and_a_fence_are_malformed_never_silent`, `test_a_line_over_200_characters_parses`, `test_request_lines_followed_by_more_text_are_all_refused_as_malformed`.
- Never a shell: `test_the_argument_vector_carries_a_block_verbatim_and_no_shell_runs_it`. A step echoes its argv: the value with backquotes, `$(touch pwned)`, `;` and `|` arrives as ONE element, and `pwned` is not created.
- A multi-line block reaches the runner, which refuses it: `refused: q=line one line two refused: a text holds no NUL and no newline`.

**2. The nonce.**
- A fresh 12-hex nonce on every UserPromptSubmit. The injected line is ONE line of 454 characters, with the nonce three times.
- Stale: `refused: stale nonce (not this turn's)`, never run. A stale line alone never blocks; its receipt reaches the next prompt as `delivered late: …`.
- A duplicate id is refused within a round and across rounds.
- No state (no prompt ran): nothing runs and nothing is written.
- The current nonce anywhere else (bold, a list mark, U+00A0, upper case, a quoted RES line, prose) gives ONE `refused: malformed (<why>)` with id `?`.
- The valid set keeps the last 4 nonces while the query runs, and resets on an ended query.
- Tests: `test_no_nonce…`, `test_a_stale_nonce…`, `test_a_duplicate_id…`, `test_the_valid_set…`, `test_the_prompt_hook_injects_one_line…`.

**3. The Stop hook.**
- It collects from EVERY assistant text block since its stored byte offset: `test_a_request_in_an_earlier_text_block_of_the_final_message_runs`, `test_a_request_before_a_thinking_only_final_block_runs`.
- `stop_hook_active` true still runs.
- Thinking blocks are never read. A counted `json.loads` shows 0 decodes for a thinking record and 1 for the text control, and a thinking block in an evading spelling is decoded but never read as text.
- Spaced JSON is read too.
- The offset: `test_the_stop_reads_from_its_stored_offset_never_the_whole_file` (the bytes read equal the window); `test_the_stop_hook_time_on_a_large_transcript_is_bounded` (40 MB filler: prompt bytes 0, stop bytes < 2000, under 10 s including a real run).
- The cap: blocking Stop 3 with `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=4` refuses with the exact line `RES <n> r1 refused: cap: nothing ran; continue with tool calls (python3 scripts/stack.py premise ...): this is blocking Stop 3 in a row with no tool call, and above 4 the harness ends the turn`. A `REFUSED AT THE CAP` head line appears and nothing runs.
  - A tool call resets the count. A compaction summary does not.
  - Default 8: Stop 7 refuses. The hook's own count holds with no summaries.
- The budget (a 7-second test budget): the running request gets `refused: budget (stopped after …)` (SIGTERM to the runner, which kills its step) and the next one gets `refused: budget (… not started)`. The hook returns in 6 to 20 s and the sleeping step is gone.
- The real run: `RES <n> r1 ran rc=0 run=s-…` with the runner's print, exit 2, the runs.jsonl record and `sha.out`.
- A signal (SIGTERM or SIGINT) to the hook mid-run: exit 128+N, the runner and its step end, and the next prompt reports `unanswered: r1 slow (an interrupt, transcript record <uuid>)`.

**4. Receipts.** `test_exactly_one_receipt_per_request_line_refusals_included_and_one_ledger_row_each` covers malformed, ran, unknown label, a runner refusal (`files= refused: an empty…`), stale and dup:
- 6 RES lines and 6 ledger rows.
- Re-running the Stop from the rolled-back offset adds nothing: exit 0, 6 rows, 1 run.

The feedback cap (9,500 UTF-16 units) is `test_the_feedback_is_capped…`:
- 29 requests.
- The prints are cut largest first. Each cut names its saved file (`… N characters cut; in full: <nonce>-<id>.txt`) and the note names the directory once.
- The short refused print stays whole and neutralized: `<\system-reminder>`, with no raw tag.

Past the cap even for RES lines, `test_receipts_past_the_cap_are_carried_to_the_next_prompt`: 100 malformed lines, of which 50 to 99 are shown, with `… N more receipts: the next prompt's context carries them`. The rest arrive at the next prompt as `delivered late`.

A failed ledger write still delivers: `NOT WRITTEN: the ledger row of r1 ([Errno 21] Is a directory…`.

Ledger fields: `v, ts, session, nonce, id, label, kind, status, reason, uuid, line, sha, source, transcript, delivered, rc, run, run_dir, out, receipt`.

**5. The reconciler.**
- An interrupt: `unanswered: r1 premise (an interrupt, transcript record <uuid>)`, and a malformed line there too (neutralized). Nothing runs; the ledger row reads delivered `context`.
- An API error: the error record is named. An unknown ending: `unknown: no interrupt or error after it…`.
- An answered request is not reported: the context is the nonce line alone.
- SessionStart: `test_session_start_keeps_a_running_query_and_reconciles_an_ended_one`. A compaction inside a running query re-injects the nonce, and the next Stop runs r1. A resume reconciles: `unanswered: r2 premise (unknown: the session restarted (SessionStart, source resume) before a Stop answered it)`. No nonce is injected, the form stays off until the next prompt, and the old nonce is stale after it.

**6. The labels are data.** `test_a_ledger_row_pairs_the_chat_before_a_request_with_its_label_and_its_result`: from a row, the transcript record found by uuid holds the request line at `row.line`. The user record before it is in the chat, and `run` / `run_dir` point at the runs.jsonl record and the step outputs.

**7. The other Stop hooks.**
- `defer-check` (`test_defer_check_says_defer_only_when_this_stop_answers_a_current_nonce`): it prints `defer` only when a text since the last Stop summary, or `last_assistant_message`, carries a current nonce.
  - It says no for an answered earlier round, a stale nonce, a thinking-only final message, and a payload that is not JSON (exit 1).
  - It is content-based, never the ledger, so it cannot race the Stop hook.
- The chain-end git report (`test_the_chain_end_runs_the_git_checks_once_in_the_harness_checks_words`): after a receipt round, the first Stop with no current request, with `stop_hook_active` true, reports once per chain. It uses the harness check's words and order (uncommitted, then untracked, then unpushed), with exit 2. It stays silent when `stop_hook_active` is false. `test_the_git_report_mirrors_the_harness_check` covers the order.
- The retro gate's deferral is in the patch: `test_the_retro_gate_defers_while_this_stop_answers_chat_form_requests`.

**8. The registration patch:** see its proof below.

**9. The off switch.** `test_the_off_switch_silences_every_subcommand_and_writes_nothing` runs twice: `req-off` as a file, and as a dangling link (`lexists`).
- With a live state and a pending current request, nothing runs or blocks, `defer-check` says no, and neither SessionStart nor the prompt hook injects anything.
- No state byte changes. After the switch is removed, the same Stop runs r1.
- `test_the_default_state_is_the_main_trees_even_from_a_worktree`: from a linked worktree the state goes to the MAIN tree's `.jev/req`, and its `req-off` silences.

**10. Fail loud, never stall.** `test_a_hook_error_is_one_line_and_never_blocks`: a broken payload, a missing transcript and a corrupt state each give one line, exit 0.
- The prompt hook reports a corrupt state in the context and starts a fresh state.
- An unreadable ledger: `ls_req stop: the ledger <path> is unreadable (IsADirectoryError) (the chat form did not act; use tool calls)`, and nothing runs.
- `defer-check` exits 1 on any failure.

## GATES (pasted from `scripts/test_summary.sh`; set ids from `bash scripts/pc_suite.sh set-id`)
- **Shared tree, `tests/test_ls_req.py`** (set=35c6a92807a9), run twice: `pytest-summary: 43 passed in 40.39s` then `pytest-summary: 43 passed in 39.87s`.
- **Clean clone at bef1e9e + the patch + my two files** (`git clone --shared`; a fresh checkout; no git write in the shared tree):
  - The brief's three files (set=9425e01745d1): `pytest-summary: 184 passed in 147.15s (0:02:27)`.
  - Set A, `test_session_hooks` + `test_search_intercept` + `test_ls_req` + `test_hooks_worktree` (set=52c6d7dd76f7): `pytest-summary: 190 passed in 115.01s (0:01:55)`.
  - Set B: the tests that name a changed file, `test_stack` + `test_system1_context` + `test_filepacks` + `test_jev_context` + `test_strip_cbm_hooks` (set=cd3b84378b0c): `pytest-summary: 520 passed in 239.71s (0:03:59)`.
  - `python3 harness-ports/tests/test_hermes_hook_adapter.py`: `6/6 passed`, exit 0. It runs the real retro gate, whose `defer-check` exits 1 on the adapter's payload (no `transcript_path`); no `.jev` appeared in the clone.
- **An environmental failure, disclosed.** The first nine-file run in the clone read `1 failed, 709 passed`: `test_search_intercept.py::test_semantic_grep_is_answered_once_then_the_identical_repeat_passes`.
  - Cause: the clone had `graft/INDEX.md` but no graft graph, so the intercept fell back to rg.
  - CONTROL: the same test in a pristine PIN clone WITHOUT the patch failed the same way (`1 failed, 103 deselected`).
  - With the shared tree's `graft/` copied in (read only), `test_search_intercept.py` passed 104 of 104, and the sets above include it.
- **`python3 scripts/vendored_manifest.py --check` in the patched clone: EXPECTED FAIL.**
  - `FAIL: vendored manifest drift: line 20: committed='| .claude/ (kit-adapted) | … | 17 | 0 | 214664b31ef9271d6ccac9664d6e3a59cfa17a0221861d11b34e20ef84bb9098 |'; generated='… | dd937a03f7818058146731a6b907adf83978eed410f6b81b3bca4276801656a4 |'`, exit 1.
  - `tests/test_vendored_manifest.py` read `5 failed, 52 passed` before regeneration: `test_committed_manifest_matches_fresh_generation`, `…passes_check_at_a_later_head`, `test_changed_vendored_byte_names_root_and_returns_one`, `test_docs_byte_change_names_docs_row`, `test_declared_root_symlink_is_refused_by_name`.
  - Proof the stale row is the only cause: `--write` in the CLONE only (`WROTE sandbox-kit/VENDORED-MANIFEST.md (10 roots)`) gave `PASS: … matches 10 vendored roots`, and the five tests then passed one at a time.
  - The regenerated manifest was reverted in the clone, so the patch does not carry it. The regeneration is your landing step. The digest `dd937a03…` is PIN+patch only; your landing tree also carries the two SKILL.md edits.

## MUTANTS (drivers in scratch: control first, a tmp tree copy per mutant, a module-identity check, compile then collect-only, `PYTHONDONTWRITEBYTECODE=1`, a literal EXPECTED, a kill = a pasted FAILED line)

**`ls_req.py`: `$SP/mut/driver.py` with `mutants.py`, final code (sha 7dfb0b9d…).**
- `CONTROL identity=True rc=0 43 passed`, then `EXPECTED=70 ROWS=70 KILLED=70 SURVIVED=0 INVALID=0`, driver exit 0.
- Self-test: a table with one row deleted gives `ROWS=69`, exit 1.
- The rows by area:
  - grammar G1–G6: the terminator by startswith, the unclosed block accepted, a case-sensitive nonce, the closing rule dropped, a 200-char cap, a stripped body;
  - transport T1–T7: the last message only, empty lam means no request, `stop_hook_active` exits, the thinking byte skip dropped, thinking read as text, compact JSON only, a shell-joined argv;
  - nonce N1–N6;
  - cap C1–C7, including the compaction read as a prompt;
  - budget and signals B1–B5: no run timeout, SIGKILL first, no handler, the handler leaves the runner, SIGTERM only;
  - receipts R1–R13;
  - reconciler Q1, Q3–Q9;
  - deferral D1–D4;
  - git K1–K5;
  - off and fail-loud O1–O6;
  - offsets S1–S3.
- Two survivors on the way, both fixed by strengthening the tests, never the gate:
  - T5 was equivalent as first written: a post-decode thinking check made the texts line unreachable. That check only dropped text blocks of mixed records, so I removed it; T5 is now killed by a mixed record with an evading spelling.
  - O1: the off-switch test had no live state, so every hook exited early anyway. It now builds a live state first.

**Patch: `$SP/mut/patch_driver.py` with `patch_mutants.py`, on copies of the gated clone's files.**
- `CONTROL identity=True rc=0 5 passed`, then `EXPECTED=14 ROWS=14 KILLED=14 SURVIVED=0 INVALID=0`, exit 0. Self-test with 13 rows: exit 1.
- The rows:
  - P1 no timeout;
  - P2 the Stop timeout at 60;
  - P3 the Stop group first;
  - P4 the ls_req marker dropped from the merge;
  - P5 a matcher on SessionStart;
  - P6 the events swapped;
  - P7 routed through `hook_context.py`;
  - P8 the deferral writes the sentinel;
  - P9 the defer test inverted;
  - P10 defer on any payload;
  - P11 defer when `ls_req.py` is absent;
  - P12 the deferral after the sentinel write;
  - P13 the settings Stop timeout dropped;
  - P14 a settings entry not last.
- I corrected one test docstring claim. "The deferral without its guard" is equivalent: python cannot open the missing file, prints nothing, and the gate fires.

## REGISTRATION PATCH PROOF
The patch is `git diff` output at the PIN, holding the four files the brief names.
- `git apply --check` passes in fresh clones at bef1e9e AND at 164bf49 [coordinator: the origin id; the lane cited its pre-push local id] (the current HEAD). After applying, each of the four files is byte-identical (`cmp`) to the gated clone's.
- `.claude/settings.json` gains three entries, each LAST in its list, each with `timeout`, no matcher, in the `$CLAUDE_PROJECT_DIR` spelling:
  - UserPromptSubmit: `… ls_req.py prompt`, 30;
  - Stop: `… ls_req.py stop`, 300;
  - SessionStart: `… ls_req.py session-start`, 30.
  The file round-trips byte for byte through `json.dumps(indent=2)`, so the diff holds only the three entries.
- `scripts/install_session_hooks.py`: a `req(event, timeout)` group through `guarded()`, appended last on SessionStart, UserPromptSubmit and Stop. `req_marker` (`<repo>/scripts/ls_req.py`) joins the merge rule, and a docstring paragraph describes both.
- `.claude/hooks/turn-retro-gate.sh`, just before `echo "$HEAD_SHA" > "$SENT"`:
  ```
  if [ -f "$REPO_ROOT/scripts/ls_req.py" ] && [ ! -t 0 ]; then
    if [ "$(timeout 20 python3 "$REPO_ROOT/scripts/ls_req.py" defer-check 2>/dev/null)" = "defer" ]; then
      exit 0
  ```
  Exempt commits keep their existing path.
- `tests/test_session_hooks.py` gets the counts: SessionStart 4, Stop 3, UserPromptSubmit 3; 13 commands; 14 groups in the quoting test; the `others` filter excludes `ls_req.py`. Five new LS-B10 tests:
  - installed last with the timeouts (and the relation budget + grace + catch-up + 30 ≤ 300, read from `ls_req.py`);
  - an older spelling replaced;
  - the repo settings last;
  - the installed commands run through `sh` against a temp git repo (nonce line; silent Stop; a real `premise` run giving `RES … ran rc=0`; compaction re-inject; off switch);
  - the retro gate defers without writing its sentinel, fires with no request, a payload that is not JSON never defers, and it is unchanged without `ls_req.py`.
- The installer ran only inside the test suite, against tmp targets in the scratch clone. It never ran against a real settings file.

## TIMING (VERIFIED; `$SP/timing/replay.py`)
The replay grows a copy of a real 41,943,040-byte transcript tail (14,004 lines) and runs each hook at its real boundaries: 21 prompt-hook batches, 76 Stop summaries (with `defer-check`), and 9 SessionStart groups. The hooks run from a scratch git repo with no `AF_REQ_STATE`, so the state goes to that repo's `.jev`, as in production.
- Exit codes: all as expected, and no stderr.

| Hook | Wall ms p50 / p95 / max | Own ms p50 / p95 / max | Bytes read p50 / p95 / max |
|---|---|---|---|
| prompt | 104.0 / 169.5 / 261.4 | 5.7 / 63.9 / 152.4 | 366,964 / 7,991,004 / 13,996,318 |
| stop | 92.1 / 132.3 / 176.0 | 3.0 / 24.5 / 58.5 | 138,189 / 3,133,618 / 4,775,366 |
| defer-check | 102.7 / 134.2 / 155.0 | not logged | not logged |
| session-start | 91.7 / 145.8 / 145.8 | 8.6 / 61.3 / 61.3 | 400,734 / 7,969,595 / 7,969,595 |

Wall time is mostly Python startup. The scan runs at about 90 MB/s, so a 100 MB turn window costs about 1 s against the 30-second timeout. The test's bound: under 10 s with 40 MB of filler and a real run.

## DISCREPANCIES (deviations from the brief)
- **D1. SessionStart registration added.** Item 5 needs it; item 8 names only the UserPromptSubmit and Stop entries. It covers every source (no matcher), timeout 30, last in its list.
- **D2. The chain-end git report blocks (exit 2) at a Stop with no current-nonce REQ.** Item 7 asks for the check "as that check would" (exit 2); item 10 says such a Stop "never blocks". It never blocks FOR A REQUEST, and the git report fires at most once per chain, only when `stop_hook_active` is true and the count is under cap−1.
- **D3. `defer-check` reads every text since the last Stop summary, not only "the final message".**
  - The hook answers requests from all of those texts, so a receipt lands beside the retro in exactly that case.
  - Reading the final message only deferred wrongly after a thinking-only final message.
- **D4. Stale-only Stops never block.** Their receipts are ledgered with delivered `no` and reported at the next prompt as `delivered late`.
- **D5. The hooks are registered directly, not through `scripts/hook_context.py`** as the other prompt hooks are.
  - They print their own JSON.
  - A Stop round outlasts the wrapper's 55-second cap.
  - The S1 stamp would ask for a rating of every nonce line.
- **D6. Nonce semantics.** A fresh nonce per UserPromptSubmit; the valid set is the last 4 while the query runs; it resets when the transcript shows an end (a non-blocking Stop, an interrupt, an error) or at a SessionStart that ends the query.
  - Measured on the real tail: the prompt hook fired for 6 messages absorbed mid-turn.
  - PM P10's "prompt hook after Stop feedback" did not appear: 0 of 60 Stop-feedback records.
- **D7. Ledger rows of receipts past the feedback cap read delivered `feedback`**, though the receipts themselves are carried to the next prompt.
- **D8. A compaction's SessionStart reconciles only when the query ended.** Inside a running query it re-injects the nonce and leaves the pending requests to the next Stop. Item 5 says "the ended turn".
- **D9. A compaction's summary record resets neither the block count nor the query.** It carries `turnOrigin` and `isCompactSummary`; measured on 7 of 7 compactions. This is conservative. ASSUMED: the harness's own counter does not reset at a compaction.
- **D10. A malformed line with no parsable id is answered with the id `?`.**
- **D11. Beyond the brief:** the patch's own mutation run, and SIGINT/SIGHUP handling.

## SELF-ATTACK: how could a request still drop without a word?
1. **A mixed assistant record** (a thinking block beside a text block, byte-matched) is skipped whole.
   - Measured: all 4,250 assistant records in the 40 MB tail hold one block each.
   - Partial cover: a final block reaches the hook as `last_assistant_message`, which triggers the fallback.
   - A REQ in an earlier block of such a record would be SILENT. This is a residual that depends on the harness format.
2. **A request line with no current nonce at all** (the nonce forgotten, or under 12 hex digits) is SILENT. It cannot be told apart from prose about REQ lines. A one-digit typo, by contrast, reads as a stale nonce and gets a receipt.
3. **The harness counts blocking Stops differently from my model of P2.** Then a round could run at the real cap, the harness would drop the feedback, and the ledger would say delivered `feedback`: results lost silently.
   - Mitigated: my count is the max of the transcript count and my own, and the compaction choice is conservative.
   - Not verified against the harness source.
4. **A session that never resumes** (a new session id after a crash): the old state's unanswered requests are never reported to anyone. The ledger simply lacks their rows. An export could find them; it is not built.
5. **The off switch mid-turn** silences pending requests. That is by design (item 9).

**Covered, not silent:** a hook killed mid-round (the receipts made so far stay undelivered and reach the next prompt; the rest are reconciled); a transcript lag longer than 3 s (the fallback, or the next prompt reconciles); an interrupt or an API error (the reconciler, naming the record); a restart (SessionStart reconciles, naming the restart); receipts past the cap (carried).

## THREE MOST LIKELY WAYS THIS IS WRONG, AND HOW EACH WAS RULED OUT
- **(a) The P2 counting model is wrong.** Tier: ASSUMED from the premortem. Partial evidence: 60 blocking summaries match 60 Stop-feedback records in the tail. The tests pin my model; they cannot pin the harness's.
- **(b) The transcript-structure assumptions are wrong:** one block per record; `turnOrigin` means a new query; `isCompactSummary`; a Stop summary per Stop; `[Request interrupted`. Tier: VERIFIED on this session's 14,003-record tail. The replay read 13 of 13 new queries as ended, 6 of 6 absorbed messages as running, and handled the resume. A harness update could change any of them.
- **(c) The exit-2 feedback and JSON context channels behave differently when live**, especially two blocking Stop hooks at once. Tier: INFERRED from the retro gate's proven channel and task #214's measurement of the JSON form. UNMEASURED live: this is NOT-done item 1.

## ADJACENT DEFECTS (reported, not fixed)
- `scripts/install_session_hooks.py` says "installed 8 in" and "the eight project hooks", and `test_fresh_install_registers_the_eight_hooks` repeats it. It installs 10 at the PIN and 13 with the patch.
- `scripts/hook_context.py`: the comment on `TIMEOUT_S=55` says "under Claude Code's 60 s default", but the harness docs copy says 600 s.
- The two shared-tree SKILL.md modifications (not mine) will move the manifest's `.claude/` row.

## STANDING-RULE NOTES
- No subagents, no outward action, no PC bridge, no git write in the shared tree. I used read-only git and clones only.
- `.claude/`, `/home/user/.claude/settings.json` and the live `.jev/` were never touched. `.jev/req` does not exist.
- No secret file was read. The `--basetemp` directories were all under the scratchpad and are deleted. Every gate ran in the foreground.
- **Disclosed:** two probes written before this conversation was compacted (`$SP/tx/probe_ups.py`, `probe_prompts.py`) ran `json.loads` on every line, thinking records included. They read only record and block types and enum fields, and printed only counts. Every later probe and the replay skip thinking records by their bytes before decoding.
- No process of mine is left: no sleeper, runner or pytest. The live pytest processes belong to other lanes (a `test_stack`/`test_lane_gate` set and the scrubber's `test_transcript_export.py`).

## SCRATCH KEPT (for a verifier; `$SP=/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad`)
- `$SP/mut/driver.py`, `mutants.py`, `patch_driver.py`, `patch_mutants.py`, and `run1.log`–`run3.log`.
- `$SP/timing/replay.py`.
- `$SP/tx/probe_*.py`, and `$SP/tx/tail40m.jsonl`: a 0600 copy of this session's transcript tail, kept so the timing can be re-measured on the same bytes. Delete it when no longer needed.
- `$SP/premise_*.txt` and `$SP/LS-B10-registration.patch` (identical to the one in the shared tree).
