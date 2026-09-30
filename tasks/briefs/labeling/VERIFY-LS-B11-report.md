# VERIFY-LS-B11 report (task #380)

> **Coordinator note (2026-09-30 02:0xZ).** The report of record for VERIFY-LS-B11 (task #380, the box), extracted by
> `scripts/stack.py harvest` (run s-20260930T015558Z-c8f83d; hand-back sha256 prefix 5fb9908229a6, 19,605 characters,
> lint OK). Served model: claude-opus-5-5 on all 331 assistant records; 0 refusal stops (`scripts/hiccup_scan.py`).
> Its MERGE-READY-WITH-FOLLOWUPS is accepted: the gates match the landing's set (`3 files set=c3270831ad89`, 326
> passed twice), the PIN plus `LS-B10-registration.patch` passes (`3 files set=9425e01745d1`, 230 passed twice), the
> REQ form reads `diffs=0` on two differential probes, and no finding meets D-034's five conditions. The box is
> verified; LS-B11 is no longer GATED-PENDING-VERIFY. Applied now: F-3 (a Rules line in skill `box-and-labels`: draw
> an example box with `<nonce>`, never 12 hex); F-1 logged as an AF-AP-192 recurrence. F-1 to F-14 are issue #87.
> The registration follows D-113 ("the hooks are registered once the box is verified, with issue #84's follow-ups
> fixed or accepted then"). Its preconditions: (1) F-14, the K2 patch conflict: K2 is not registering now, so
> LS-B10's patch applies alone, and K2's patch is rebased when K2 registers; (2) the owner's word: D-113; (3) the
> first live-run counters (R2-F1, F-4, F-5) are measured after the registration; (4) F-3: applied.

## VERIFY-LS-B11
Written 2026-09-30 01:54:22Z

Lane: sandbox adversarial-verifier, Opus 5.5 (claude-opus-5-5). Brief: `tasks/briefs/labeling/VERIFY-LS-B11-brief.md` (committed as of ee86eab). PIN 69e7999. Started 00:49:36Z. No subagents, no outward action, no PC bridge, no commits. I never registered the hooks. I read no secret file.

**Recommendation: MERGE-READY-WITH-FOLLOWUPS.** No finding meets all five D-034 conditions. Everything below was reproduced through the real hook entry (`python3 scripts/ls_req.py stop|prompt|defer-check`) and the real `scripts/stack.py`, on fixture transcripts. One point is not reproduced: the real harness has never carried a box, because the hooks are not registered. So "no blocker" rests on fixture transcripts plus measured counts from the real 835 MB transcript.

## Checklist (the brief's 12 items)
- [x] 1. **Premise:** IDENTICAL. `diff` of the brief's block against a fresh `bash scripts/premise_block.sh` run is empty. No boundary file changed from the PIN to HEAD.
- [x] 2. **Grammar:** 173 cases through `parse_message`. Every current-nonce case gets exactly one candidate with a reason; none is silent. On D1 and D2, I **agree** with the builder (reasons in item 2 evidence below). New: an example box poisons a later real box in the same message (F-3).
- [x] 3. **D-111:** holds. 28 cases through the hook; each value is exactly one argv element; nothing reached a shell.
- [x] 4. **Run twice / go unanswered:** no double run anywhere. A box split across two text blocks gets refused (F-4), but 8,202 of 8,202 real messages have one text block.
- [x] 5. **REQ form unchanged:** the builder's probe reproduces `diffs=0` (its control 281). My wider probe also reads `diffs=0` (controls 360 and 206). F1, F4, F6 and F10 hold on the new bytes.
- [x] 6. **Raw UTF-8:** the whole `tests/test_ls_req.py` (89 tests, not only the box tests) passes on raw-UTF-8 transcripts and payloads. The ASCII control also passes.
- [x] 7. **D4:** measured; smallest stack.py change proposed below.
- [x] 8. **Registration:** 230 passed, twice. The K2 conflict is reproduced (report only; not rebased).
- [x] 9. **Mutation:** the builder's table reproduces 51 of 51 KILLED only when bytecode caching is off. Its driver repeats AF-AP-192 (F-1). My 19 added mutants: 4 KILLED, 15 SURVIVED, all test gaps (F-2).
- [x] 10. **Screen advisories:** AP-32 is real but by documented design, and the only comparison is sound. The AF-AP-175 line is not new to the landing (a moved line); it can cause a test-only false red.
- [x] 11. **Gates:** set `c3270831ad89`, 326 passed, twice.
- [x] 12. **Preconditions and recommendation:** below.

## FINDING INVENTORY (no severity filter)

**F-1: FOLLOW-UP. The builder's mutation driver repeats AF-AP-192 (stale bytecode).**
- Evidence: reproduced.
- Mechanism: `mutdriver.py` rewrites `scripts/ls_req.py` in place with bytecode caching on. The test module imports it through `spec_from_file_location`, so CPython reuses a `.pyc` whose recorded mtime (whole seconds) and size match. V12 and V13 each add exactly 10 bytes; V42 and V43 each add 20.
- My first full re-run read `ROWS=51 KILLED=50 SURVIVED=1` (V13).
- V13 alone: KILLED. V12 then V13, twice with nothing changed: SURVIVED, then KILLED.
- With `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared: KILLED. The full table on that setting reads `ROWS=51 KILLED=51 SURVIVED=0 INVALID=0`.
- In this table a collision can only produce a false SURVIVED: V12's code keeps V13's reason, and V42's code passes V43's budget test. So the builder's 51/51 claim stands; its driver just cannot reproduce it deterministically.
- Contract: TESTS (named mutants). Canonical path: yes. Material: no (the evidence is not falsified).
- Fix: log the recurrence under AF-AP-192. Future drivers should set `PYTHONDONTWRITEBYTECODE=1` and clear `__pycache__` before each mutant, or copy a fresh tree per mutant.
- Repro: `S/mut/clean-all.log`, `S/mut/afap223-main.log`, and the V12,V13 runs.

**F-2: FOLLOW-UP. Contract grammar clauses no test pins.** I ran 19 added mutants against whole test files (`S/mut/mydriver.py`: bytecode off, control first). Controls: no-op SURVIVED, syntax break INVALID, known kill KILLED.
- These survive `89 passed`:
  - M01: a bare `└` accepted as a bottom edge.
  - M02: `└─ <text>` accepted.
  - M03: a two-character divider `┄┄` accepted.
  - M04: a divider with trailing text accepted.
  - M05: four backquotes accepted as a fence.
  - M06: an indented fence accepted.
  - M07: a `~~~` fence accepted.
  - M09: the ledger text cap removed.
  - **M10: the body always sent to `q`.** Every hook-level body test uses a stack whose body is `q`; this clause is in contract item 2/4.
  - M11: the body's NUL check removed.
  - M14: decoration with no space accepted (`<nonce>───`).
  - M15: CR kept on inside lines.
  - M16: the fence exemption also triggered by a malformed box line.
  - M18: a one-letter label accepted in the top edge.
  - M19: an id of 17 to 32 characters accepted in the top edge.
- KILLED: M08, M12, M13, M17.
- The landed code is correct on every surviving case. My grammar probe and a direct check show B02, B04, I01, I04, F02 to F04, T17b, a one-letter label, a 17-character id and CRLF all handled as the contract says. My D4 probe shows `echo`'s body reaching `pattern`.
- Contract: item 2's clauses; the contract's "each malformed case" is met at the category level. Canonical path: yes. Material: none today; these are regression gaps.
- Fix: add grammar cases for M01 to M07, M14, M18 and M19, and one hook test whose body parameter is not named `q` (for example `echo`'s `pattern`).
- Repro: `S/mut/my-b1.log`, `S/mut/my-b2.log`, `S/mut/my-b3.log`.

**F-3: FOLLOW-UP. D1's cost: an example box poisons a real request later in the same message.**
- A well-formed box with a 12-hex nonce that is not current is a stale request (D1), so it counts as "the first request". Prose after it then refuses every request in the message.
- Probe case C08: a stale box, prose, then a current box. Both are refused with "text after the request lines". The real box's refusal blocks the turn.
- The REQ form has the same property. But boxes are likelier to be drawn as examples: the D-113 conversation drew one.
- The `box-and-labels` skill's example uses the `<nonce>` placeholder, which parses as a silent illustration. The skill does not warn against a real-looking nonce.
- Contract: follows item 2 literally. Canonical path: yes. Material: a false refusal, never silence and never a run.
- Fix: one skill line ("draw an example box with `<nonce>`, never 12 hex"). Or, as an LS-B10-level change covering both forms, apply the closing rule only after the first current-nonce request.

**F-4: FOLLOW-UP (trigger never observed). A box split across two text blocks of one message is refused.** Three shapes, all through the hook:
- P5b: block 1 ends with a newline. Each block is split separately, which inserts an empty line, so the box is refused ("inside line … found ''") even with the transcript caught up.
- P5c and P5d: the transcript lags on block 2. `lam_missing` keys only on the top edge, so it does not wait, and the box is refused as unclosed. This happens whether `last_assistant_message` holds block 2 only or the whole message.
- Never a double run, never silent. P5a (block 1 ends without a newline) runs.
- Real transcript, counts only: `text_blocks 8202, messages_with_2plus_text_blocks 0` over 835 MB.
- D-034 condition 2 fails: no production trigger.
- Fix: when a transcript box is unclosed and `last_assistant_message` holds a closed box under the same top edge, wait or take the fallback. Add a counter at the first live run.

**F-5: INFO (inherited from LS-B10). A trailing-blank difference between `last_assistant_message` and the record breaks the bind.**
- P3b: the box runs via the fallback. Its record then lands with trailing blanks, so the sha differs and the record gets a spurious blocking `refused: duplicate id`. There is no second run.
- The REQ control P3c behaves the same.
- Trigger unverified (it needs the harness to trim `last_assistant_message`).

**F-6: INFO. Look-alike corners and indented or marked-up top edges are labeled `form: "req"`.** Cases T09 and T18. `c.form` keys on a line's first character, so the export would count those box attempts as REQ attempts. The receipt still exists. Fix: label any malformed line holding `┌`, `│` or `└` as `box`.

**F-7: INFO. Some malformed-box reasons are imprecise.**
- T06 (two spaces before the nonce) says "the nonce is written ''".
- T01, T03 and T04 blame the label or id for a spacing fault.
- T09 (a look-alike corner) says "the nonce outside a request line".
- Every case still has a receipt and blocks.

**F-8: INFO (AP-32). The ledger's `sha` is the full text's; its `text` is cut at 4,000 characters.**
- A 4,810-character box: `row_text_chars 4000`, ending in "…"; `row_sha_is_sha_of_full_text true`; `row_sha_is_sha_of_row_text false`.
- The only comparison, the fallback bind in `known()`, compares sha to sha, both from the full parse. That record bound with rc 0.
- This is documented in the docstring's STATE section. A future export that checks `sha256(text) == sha` must know the cut rule.
- The test-side `sha()` (`tests/test_ls_req.py`) hashes exactly what the code hashes for the tested inputs.

**F-9: INFO (AF-AF-175). `tests/test_stack.py:1247` reads `HEAD` in the test while `stack.py explain` reads it in its own process.**
- Two reads per test run. The line is not new: the landing re-flowed the tuple (the parent commit has it at line 1233).
- A commit landing in the tested tree mid-test can cause only a false red, never a mixed record. At a detached PIN, `HEAD` cannot move.

**F-10: INFO. Request text now persists in the ledger.** REQ rows gain `form` (required by the contract) and `text` (the builder's D6). `.jev/` is git-ignored (`.gitignore:68`), and no export exists yet. A future export must scrub `text` the way transcripts are scrubbed.

**F-11: INFO (D2's consequence).** In a message that holds any box, a stale one included, a fenced REQ line runs (F09b). A REQ-only message keeps LS-B10's rule (F09 is refused). This follows the extended closing rule as written.

**F-12: INFO.** Behaviours that are correct and never silent:
- A value with U+2028, NEL or VT reaches the runner as one element (A19).
- A 150,000-character value gets `refused: the runner did not start: [Errno 7] Argument list too long` (A17).
- A body of only a divider, or a body ending in a bare `│`, is refused by the runner.

**F-13: INFO (stack.py, out of the box's boundary).** Labels are not reserved. A future stack named `list`, `catalog`, `explain` or `rate` would reach the runner's subcommand of that name. Today all four get `unknown label` (L02 to L05).

**F-14: INFO (precondition).** `tasks/briefs/jev-trim/K2-registration.patch` (sha prefix 3e8b979120d0638a, the same at PIN and HEAD) applies alone at the PIN. On top of `LS-B10-registration.patch` it fails in `scripts/install_session_hooks.py` and `tests/test_session_hooks.py`.

## Per-item evidence
- **Gate 1** (item 11), in my worktree at the PIN, `3 files set=c3270831ad89`:
  - `pytest-summary: 326 passed in 85.65s (0:01:25)`
  - `pytest-summary: 326 passed in 80.96s (0:01:20)`
  - No FAILED, ERROR, SKIPPED, XFAIL or XPASS.
- **Gate 2** (item 8), PIN plus `LS-B10-registration.patch` (sha prefix ded5c249f249c372, rc 0), `3 files set=9425e01745d1`:
  - `pytest-summary: 230 passed in 91.28s (0:01:31)`
  - `pytest-summary: 230 passed in 85.41s (0:01:25)`
  - The real settings files hash the same before and after.
- **F10:** dropping `req("session-start", 30)` makes the count test red on `installed 12`; restored, it passes.
- **Red-green:** the landed tests on the pre-landing code (hash-identical to b2e1ed8's) read `39 failed, 287 passed in 75.67s`.
  - 32 of the 33 new test ids are red.
  - The one never red is `test_defer_check_defers_the_retro_for_a_box_as_for_a_req_line`, a regression pin the builder disclosed; V44 kills it.
  - The other 7 reds: 3 new bad-registry cases, 3 moved explain pins, and the injected-line pin.
- **REQ unchanged** (item 5):
  - The builder's probe, re-run: `messages=30000 candidates=65986 diffs=0`; its control reads `diffs=281`.
  - My probe mixes REQ lines with box-like lines that are not boxes: `messages=39803 … expected_reason_changes=12817 diffs=0`. Controls: `diffs=360` (fence) and `diffs=206` (illustration lines skipped). The 12,817 accepted changes are all reason text on lines holding `┌`.
  - Round 2's scripts give identical output after masking: attack4b, attack5, attack_cap_r2, attack_r2 (27 lines), and attack2-real (`LEDGER rows=45 runs=16 argv_calls=0`, no marker file created).
  - attack4 differs only in the injected line, which contract item 3 changes on purpose. attack3 differs only in unmasked nonce fragments.
  - F6, re-run: `CONTROL identity=True rc=0 89 passed`, then `ROWS=6 KILLED=6`, killed by the same tests as round 2.
- **Raw UTF-8** (item 6):
  - The builder's probe: `12 passed in 4.36s`.
  - My plugin over the whole file: `89 passed in 40.76s`, with `raw_records 13 of 399` and `raw_payloads 4 of 210`.
  - The ASCII control: `89 passed`, with `raw_records 0`.
- **D-111** (item 3), selected cases:
  - A body or parameter holding metacharacters arrives as exactly one argv element: `["\`id\`; $(id) && echo $HOME > /tmp/vlsb11-pwned | cat * ~ …"]`, and no file was created.
  - A leading `-` is refused (option injection).
  - Keys named after runner options (`registry`, `tree`, `log_dir`, `rate`) and undeclared keys get "unknown key".
  - A derived key gets "never set". Two `q:` lines get "repeated key". A parameter line plus a body, or a body for a stack with no body, is malformed. NUL is malformed.
  - A `tag: evil` line below the divider stays body text.
- **Item 2:** 173 cases in `S/probes/grammar.out`. All forms the brief lists behave as the contract says, including:
  - look-alikes for `·` (11 code points), `─` (12) and `┌` (11);
  - tabs, NBSP, U+3000, CRLF;
  - the nonce twice or in another slot (in the id slot it runs, as a REQ line does);
  - two, six or mixed dividers; four backquotes, tildes and indented fences;
  - mixed closing-rule cases.
- **Item 4:** P1 and P2 (box then REQ, and two boxes, with one id) give one run and one `duplicate id`. P3a: two boxes via the fallback run, then both bind, and the next prompt reports nothing. P4: a second Stop and a reanchor to a copied path rerun nothing. P6: over the cap, rc 0 and nothing written; the next prompt says "delivered late … refused: cap". P7: the reconciler answers boxes. P8: `defer-check` defers on a look-alike corner line.
- **Item 3 (contract):** the injected line went from 454 to 555 characters (577 UTF-8 bytes), still one line, the nonce 3 then 4 times. **Item 6:** `LS-DESIGN-v2` §3, lines 47 to 55, dated 2026-09-29, points to THE BOX docstring section.
- **stack.py:** hostile `body` values (`""`, `true`, `5`, `["q"]`, `"words"`, `"nosuch"`, `"q "`, `"Q"`) are all refused with exit 3 and a named reason; `"files"` is accepted (a settable parameter). `explain` prints the body line for find, echo and ctx, none for premise, and writes no log.

## D1 and D2
- **D1 (a well-formed box with an old nonce is a stale request): agree.**
  - The rule "as a REQ line is" is item 2's governing principle.
  - The owner's "never silence" rules out dropping it: a re-issued old box must be told it did not run.
  - A stale receipt never blocks.
  - Cost: F-3, fixable by a skill line.
- **D2 (the fence exemption only in a message that holds a box): agree.**
  - Item 5 says the REQ form stays "exactly" as it was, and LS-B10's test pins a fenced REQ-only line as refused.
  - The fence bullet exists so the chat renders the box.
  - Both differential probes show REQ-only messages unchanged. Consequence: F-11.

## D4: the receipt and the smallest fix
- Measured on the committed registry.
- `find`, two-line body: `RES <n> r1 refused: q=where does the scrubber hide bearer tokens refused: a text holds no NUL and no newline`. The feedback's print shows the raw newline; `short()` joins the lines in the RES line.
- `echo`: `refused: pattern=foo( bar refused: …`.
- A body ending in a bare `│` is refused too: `q=one line refused: …`.
- A 501-character body: `refused: … a text is 1 to 500 characters (found 501)`.
- The `box-and-labels` skill already states the one-line, 500-character limit.

Proposal (not built):
1. `check_scalar(kind, raw, tree, what, choices=None, lines=False)`: for text, allow `\n` when `lines` is true. Still refuse NUL and CR and a leading `-`, and cap at a separate `BODY_MAX` (for example 4,000).
2. `validate(p, raw, tree, lines=False)` passes it through.
3. `parse_tokens` sets `lines=(name == stack.body and p.type == "text")`.
4. Escape newlines when printing the body value in the `params:` header, so the header stays one line.
5. Caveat from measurement: `rg -e $'a\nb'` exits 2 ("the literal "\n" is not allowed"), while `git grep -e` splits the value into OR'ed patterns. So `echo` should drop its `body`, or bodies need a per-stack opt-in.
6. Tests: a two-line body reaches `graft ask` as one element. A two-line value for a non-body text parameter is still refused (the negative control).

## What must hold before the registration
1. Rebase one registration patch on the other: they conflict (F-14). Re-run the combined gate on the resulting set, including the hook-count test (13 for LS-B10 alone).
2. The owner's word, per the round-2 coordinator note (D-111 item 3). The kill switch `<main>/.jev/req-off` is known before registering.
3. First live-run counters: R2-F1's stale `last_assistant_message`; messages with two or more text blocks that hold a box (F-4); binds missed because of text drift (F-5).
4. Recommended, not blocking: the F-3 skill line.

## Blocking predicate (D-034)
- F-1: conditions 1, 2, 4 and 5 hold; 3 fails (the claim holds on a clean run).
- F-2: 3 fails (no present defect).
- F-3: 1 fails (it follows the contract literally).
- F-4: 2 fails (no production trigger).
- F-5 to F-13: 3 fails.
- No CONTRACT-DEFECT.

## Reproduced / static / skipped
- **Reproduced:** everything above.
- **Static only:** the harness's real record layout for a box message, and how it fills `last_assistant_message` for a message with several text blocks.
- **Skipped:** the default 240 s budget in real time (the builder's 7 s budget test passed in both gates); any PC run (out of scope).

## Standing-rule disclosures
- S1 rates given: s1-a9df6f7b (2/1), s1-2d9b9dc6 (1/0), s1-f4a42268 (2/2), s1-c4a3ea5b (2/1).
- Worktrees `S/wt`, `S/wtreg` and `S/mut/wtmut` (all hooks off) were removed. `wtreg` was removed with `--force` because it held my scratch copy of the registration patch. The shared tree is clean.
- No process of mine is running; 0 sleepers.
- Every script I wrote has 0 non-ASCII bytes; box characters are built with `chr()`.

## Evidence
Everything is under `S = /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vlsb11`:
- Gates: `gate1.log`, `gate1b.log`, `gate2.log`, `gate2b.log`, `red.log`
- Probes: `probes/grammar.out`, `d111.out`, `twice.out`, `d4.out`, `blocks_count.py`, `ap32_probe.py`
- Differential probes: `dp/diff_probe.out`, `dp/diff_probe2*.out`
- Round-2 re-runs: `r10/*.out`, `f6/f6.log`
- Raw UTF-8: `utf8/raw_all.log`, `utf8/ascii_all.log`
- Mutation: `mut/clean-all.log`, `mut/my-b1.log`, `mut/my-b2.log`, `mut/my-b3.log`
- F10: `f10-mutant.log`
- Settings hashes: `settings-*.txt`