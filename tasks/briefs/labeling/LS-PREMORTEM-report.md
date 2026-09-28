> **COORDINATOR NOTE (2026-09-28 14:5xZ):** the LS-PREMORTEM lane (sandbox adversarial-verifier, served claude-opus-5-5 on all 215 assistant records, 0 refusal stops, per `scripts/hiccup_scan.py`) returned this report as its final message. This copy is extracted from its hand-back in the subagent transcript, never retyped; control tags are neutralized (`<` became `<\`), as the harness relay did. Two commit ids that a push rewrote are replaced by their ids on origin (in the Lane paragraph). Disposition: `docs/research/findings/labeling/LS-DESIGN-v2-2026-09-28.md`.

# LS-PREMORTEM (task #339): the labeling output style design, attacked before it is built

**Lane.** Sandbox adversarial-verifier in premortem mode, claude-opus-5-5 (per the session environment line). Read-only: no git writes, no bridge, no subagents, no outward action, and no hook, setting or repo file touched.

- **Brief:** `tasks/briefs/labeling/LS-PREMORTEM-brief.md`.
- **Design attacked:** `docs/research/findings/labeling/LS-DESIGN-2026-09-28.md` at 370fead. Both trees were at 370fead when I started. The main tree moved to 40dd47d during the lane. `/home/user/i59-landing` still shows only the other lane's 7 modified files.
- **Assembled:** 2026-09-28T14:44:21Z (`date -u`).
- **Scratch:** 8 KB (one probe script).
- **S1-RATE:** no `[S1 …]` injection reached this lane, so no S1-RATE lines are owed.

## TL;DR

Two weeks on, LS has failed mainly through its transport.

- **Silent stalls.** The Stop-hook request loop drops requests without a word in common cases. The turn then just ends, and an autonomous coordinator sits idle until the owner comes back.
- **Wrong control semantics.** `stop_hook_active` and the continuation guard are specified against behaviour the 2.1.283 binary does not have.
- **`book` cannot carry real entries.** Under the 200-character line cap it cannot hold a real ledger, incident or decision entry. Measured: 81–100% of real entries are longer.
- **No real saving.** Each request round costs one model request, the same as the tool call it replaces. The promised saving would appear only in a metric that counts tool calls.
- **Labels that cannot train.** Label records keep a digest of the state, not the state. The SYNTH1 result predicts that labels taken "where the context is" will not be learnable from the input a Jev instance sees.

**GATE RECOMMENDATION: REDESIGN the request transport (§4.2, §5, and the execution path of `book` in §6).** The labels (§4.1), the registry (LS-B8), the action log (LS-B4), the collector (LS-B3) and the Read hook (LS-B5, shadow mode first) can go to the seed with the changes listed at the end. This rests partly on harness behaviour I read statically from the binary; none of it was exercised (no hook was registered).

## Method: reproduced vs reviewed

**Reproduced (commands run, output read):**
- **Harness binary** `/opt/claude-code/bin/claude` 2.1.283, read with grep and mmap. Covered: the Stop continuation guards, the cap, how streamed content blocks become messages, how `last_assistant_message` is built, the thinking-only nudge, and the per-event timeout table. This is a static reading of minified code; nothing was exercised.
- **Harness docs copy** (the LS-AUDIT fetch), quoted by line.
- **Probes on live files:**
  - entry lengths in the four `book` targets;
  - the mirror caps;
  - a census of narrowable files and their window sizes;
  - `.jev/injections.jsonl` counts by event and thread (ids and counts only);
  - `git check-ignore`;
  - `.lanes-live` and the main tree's dirty set.
- **The production S1-RATE collector** (`scripts/s1_scores.py`, imported with bytecode off), run on sample text.
- **A draft REQ parser** that follows §4 word for word. This is a surrogate: nothing is built yet.

**Reviewed statically:**
- The design, the audit, and D-077, D-078, D-082, D-099, D-100, D-101, X-010 and X-011.
- The two Stop hooks and the installer.
- `hook_context.py`, `s1_scores.py`, `anchor_edit.py`, `push_clean.sh`, `test_context_mirrors.sh`.
- The ledger's structure and jev's `hook.go`.

**Not done:**
- **No transcript read.** Every "coordinator session" count stays the design's own.
- **No test run.** The timing of the `book` test map is UNVERIFIED.
- **No hook registered.** There was no live experiment on Stop, UserPromptSubmit or the Write precondition.

## Finding inventory

**Classes:**
- **BLOCKER:** must change before the seed. It maps to D-101, X-010, a repo invariant, or the design's own stated requirement. It has a concrete discriminator (binary code, a live file, or a probe). It changes the outcome, and it belongs to this design.
- **FOLLOW-UP, INFO, UNVERIFIED:** as usual.
- **L/I:** likelihood / impact, each H, M or L.

### A. The request loop

**P1. BLOCKER — `stop_hook_active` stays true for the rest of the turn, and the design only says it "is read" (design :83). L H, I H.**
- **Mechanism.**
  - After any Stop hook blocks, every later Stop in the same user turn arrives with `stop_hook_active: true`, even after many tool calls.
  - Suppose `ls-exec` honours the flag the way the git check does (`stop-hook-git-check.sh:7-9`). That is also what the harness itself advises in its cap message: "For Stop/SubagentStop hooks, check stop_hook_active in the input and return success while it's true". Then LS serves only one request round per user turn, and the next REQ message ends the turn with nothing run.
  - If it ignores the flag, P2 decides what happens.
- **Evidence (binary, static).**
  - The initial guards are `Kr={...Vn,thinkingOnlyNudged:!1,malformedToolUseRetried:!1,stopHookBlockingCount:0}`.
  - The continuation after tool calls is `guards:{...Me,...Kr,turnCount:Pn}` (`next_turn`). It keeps `stopHookActive` from `Me`.
  - The Stop-block continuation sets `stopHookActive:!0`.
  - The string `stopHookActive:!1` occurs 0 times in the binary.
- **Change.** State that `ls-exec` does not use `stop_hook_active` to decide whether to execute. Key execution on the nonce and on P2's counter.

**P2. BLOCKER — the design's continuation guard cannot see what the harness counts, and its refusal is silent (design :81-82, :85). L H, I H.**
- **What the harness counts.** Consecutive blocking Stops with no tool call between them.
  - `stopHookBlockingCount` resets at every `next_turn`, because it is part of `Kr`.
  - It rises by one per Stop event that has any blocking hook (`de=Xn+1`).
  - The turn is ended when `de > (CLAUDE_CODE_STOP_HOOK_BLOCK_CAP ?? 8)`.
- **Why the design's counter cannot match it.** The Stop payload says nothing about tool calls, and `stop_hook_active` never resets (P1). A state-file counter therefore either never resets within a user turn, so it refuses after 6 rounds however much work sat between them, or it resets on the wrong signal.
- **The refusal is invisible.** The design refuses by exiting 0. Stop stdout goes to the debug log (hooks.md:792). So the model never sees `refused: continuation budget`, and the turn ends. That contradicts the design's own rule: "Fail loud … nothing fails silently" (:85).
- **Results can be lost after the work is done.** When the harness cap fires, the pending blocking messages are not appended (`return yield*wt(f,[...A,...L],…)`, reason `completed`). Verbs that already ran lose their RES.
- **Change.**
  - Reset the counter from the LS-B4 action log: any tool call since the last block sets it to 0.
  - Read `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`.
  - At cap−1, refuse loudly (exit 2, "continue with tool calls").
  - Run no side-effecting verb at or above cap−1.

**P3. BLOCKER — several drop paths end the turn while the coordinator waits (contradicts :85 and D-101 (3) "write the request … end, wait for a response"). L H, I H.** In each case there is no RES and an ordinary turn end, so the session idles until the next prompt.
- **(a) Only the last block is seen.**
  - At each `content_block_stop`, the harness yields a new assistant message that holds that one block (`Qrt([ci],…)` then `yield Hc`; binary offset about 205,375,653).
  - The Stop input takes `ey(S)=S.findLast(n=>n.type==="assistant")` and joins that message's text blocks (`eo`).
  - So REQ lines in any earlier text block of the final response are invisible.
- **(b) Thinking-only final messages.** The harness has a `thinking_only_retry` path. Its nudge reads: "[Your previous response had no visible output. Please continue and produce a user-visible response.]". The VERIFY-S1-RATE F1 shape (50 of 50 `missing` rows) can therefore hit a final message, and the nudged reply need not repeat the REQ lines.
- **(c) Parser misses (probe with the draft parser):** each of these returns `[]`:
  - a REQ line over 200 characters;
  - a non-breaking space after `REQ`;
  - `**REQ …**`;
  - REQ lines after an unclosed code fence.
- **(d) Interrupts and API errors.** "Does not run if the stoppage occurred due to a user interrupt. API errors fire StopFailure instead" (hooks.md:2527).
- **(e) Hooks not installed** (P13).
- **Change.**
  - Treat the current nonce, anywhere in the text (fences, bold, long lines), as intent: parse it, or answer `refused: malformed` loudly.
  - Require REQ lines to close the final text.
  - Add a watchdog on the next UserPromptSubmit or SessionStart that says "your last message held REQ lines and got no RES".
  - Add the rule "no nonce injected this turn ⇒ LS is off ⇒ use tool calls".
  - Cases (a), (b) and (d) stay possible even after these changes; see the gate recommendation.

**P4. FOLLOW-UP — LS silences the harness git check for the rest of most turns. L H, I M.**
- The git check exits 0 whenever `stop_hook_active` is true (`stop-hook-git-check.sh:7-9`). By P1, that is every Stop after the first request round.
- So at the end of such turns, uncommitted `book` writes and unpushed commits go unchecked, in an ephemeral container.
- **Change.** When a message ends a chain (no REQ), `ls-exec` runs the same dirty and unpushed checks. `book` RES lines say "uncommitted".

**P5. FOLLOW-UP — "ls-exec runs first" (:83-84) is not how the harness works. L H, I L.**
- "All matching hooks run in parallel" (hooks.md:414).
- Each blocking hook yields its own message, and all of one Stop's messages go back together (`messages:[...A,...L,...lt.blockingErrors]`) in completion order.
- The git check's `git diff --quiet` races a `book` write.
- **Change.** Drop the claim. Either accept parallel runs, or run all Stop hooks from one dispatcher command.

**P6. FOLLOW-UP — the retro gate would fire in the middle of a chain. L M-H, I M.**
- `turn-retro-gate.sh` reads no stdin and fires on the first Stop after a new HEAD (lines 12-17, 58, 66-74).
- With LS, the first Stop after a commit is usually a request round. The five-item retro then lands beside a RES block and a rating request, not at the end of the batch.
- **Change.** The gate reads stdin. When `last_assistant_message` carries a REQ with the current nonce, it defers: exit 0, sentinel not written.

**P7. FOLLOW-UP — every request round shows the owner a hook error. L H, I L-M.**
- Exit 2 and `decision: block` show as errors. Only `additionalContext` "is shown in the transcript as hook feedback … no hook error notification is shown" (hooks.md:2615). The binary labels the error `Stop hook blocking error from command "…"`.
- **Change.** Return RES through `hookSpecificOutput.additionalContext`. First measure whether that path comes back as a UserPromptSubmit prompt. `wiki-context.py:34` lists "Stop hook feedback" among the prompt prefixes seen through UserPromptSubmit, and that would interact with P10.

**P8. FOLLOW-UP — timeouts: the 60 s budget is fine, the `ask` verb is not. L H, I M.**
- **The timeout contradiction (AUDIT §6.3).**
  - The binary's `{PreToolUse:15,…,UserPromptSubmit:30,…,Stop:120}` table sits in the code that forwards hooks from an attached machine (`registry`, `leaseExpiresAt`, "the attached machine").
  - The docs give 600 s for local command hooks: UserPromptSubmit's 30 s is "shorter than the 600-second default … on most other events" (hooks.md:1329).
  - The repo still believes 60 s (`hook_context.py:42`).
  - A 60 s wall budget fits every reading.
- **The `ask` verb.** It runs graft first and Jev locate second, and D-077 measured "a Jev pack costs 36-165 s against 5-28 s" (DL:88). That cannot fit a shared 60 s budget.
- **Change.** Set an explicit `timeout` on the registration. Keep Jev out of synchronous `ask`, or return a result file later. Kill child processes at the budget.

### B. Safety

**P9. FOLLOW-UP — a stale nonce stops execution but still continues the turn, and invites a re-issue. L M, I M.**
- Probe: the unfenced pasted line `REQ 00ff00ff r1 book decision D-102 remove the git check` parses as a request.
- §5.2 says such a line is reported as "ignored: stale nonce". Reporting needs exit 2, and exit 2 continues the turn.
- The RES carries the fresh nonce, and a helpful model may re-issue a line it only quoted.
- So "a quoted report … cannot trigger a request" holds for execution only.
- **Change.** Log stale lines and drop them silently. Never echo them. Only the current nonce signals intent.

**P10. FOLLOW-UP — a single nonce slot races harness events and compaction. L M-H, I M.**
- 122 of 147 UserPromptSubmit records were harness events (AUDIT §1.3 S2). `wiki-context.py:30-35` lists task notifications, agent messages and "Stop hook feedback" among them.
- If each of these rotates the one valid nonce, a notification or an owner's mid-turn message between a RES and the next REQ makes that REQ stale. Each retry spends a continuation (P2).
- Compaction can summarize the nonce away.
- **Change.** Keep a turn-scoped set of valid nonces. Rotate only on human prompts (reuse `HARNESS_EVENT_PREFIXES`). Re-inject the nonce on SessionStart(compact).

**P11. FOLLOW-UP — the nonce is readable by every process in the container. L L, I M.**
- UserPromptSubmit output and Stop blocking text are stored in the transcript (`s1_scores.py:11-19`). A plaintext state file under `.jev/ls/` would hold the current value. Subagents run as the same user.
- A lane that reads either one (the LS-B2 verify lane, for example) can put a live REQ into a report the coordinator quotes.
- **Change.** Store on disk only an HMAC of the nonce, bound to `session_id`.

**P12. FOLLOW-UP — the verbs run outside the permission system and return raw content. L M, I M-H.**
- **Outside the permission layer.** A hook runs with the container's full privileges, while permission rules and the auto-mode classifier see only tool calls.
- **Secret sources are reachable.** The `read` and `find` paths are "checked against an allowlist" that the design never defines. A plain Python `open` can reach `.pc-bridge.env` in the repo root, `/root/.claude/projects/` and `/root/.codiv/`, all on this project's no-read list. `status` must read the bridge env to reach a lane.
- **Content is not neutralized.** RES text reaches the model as hook feedback. The harness's control-tag neutralizer is framed for subagent output (binary text: "[harness: subagent output matched instruction-shaped pattern(s)…"). Whether it touches hook stderr is UNVERIFIED. If it does not, a `<\system-reminder>` literal in a file (for example jev's `hook.go` cut list, or the hooks.md copy) arrives raw.
- **Change.**
  - Allowlist = git-tracked files, plus an explicit deny list.
  - Run `transcript_export.scrub` on every RES.
  - Neutralize control tags the way the harness does.
  - State how the bridge token is handled.

**P13. BLOCKER — no registration path: this is the AF-AP-172 class. L H if missed, I H.**
- The session is rooted at `/home/user`, which is not a git repo. Project hooks reach it only through `scripts/install_session_hooks.py`. Its docstring (:4-8) records the failure: "the turn-end retro ran 0 times in 834 Stop runs".
- `our_hooks()` is a fixed set of six (:41-70), run by `setup.sh:438` and `resume-heal.sh:14`.
- The design registers nothing: `install_session_hooks` appears 0 times in it.
- A hook added only to `.claude/settings.json` never fires in this session. Every REQ message would then end the turn (P3e).
- **Change.** LS-B2, B4 and B5 extend `our_hooks()` and its tests, with a `--check` smoke test, plus the rule "no nonce ⇒ no REQ".

**P14. FOLLOW-UP — `book` races the lanes and writes a fixed tree. L M, I M.**
- **The lock covers only `ls-exec`.** Edit, `anchor_edit.py` and the lanes never take it.
- **Lane-held files.** `.lanes-live` lists the files lanes hold (`push_clean.sh:50-56`).
  - At 14:3xZ the main tree had `docs/08_DECISION_LOG.md` dirty and not in `.lanes-live`. That is exactly the state an uncommitted `book decision` leaves, and it is the state `push_clean --lanes-live` refuses.
  - `safe_commit` stages whole paths. A `book` hunk inside a lane-held file would ship under the lane's commit, or be lost when the lane reverts.
- **Fixed target tree.** The hooks `cd` into `/home/user/agent-factory` (`install_session_hooks.py:49`). So `book` always writes the main tree, even while a batch lands in a worktree (there are two worktrees today).
- **Change.** Refuse a target listed in `.lanes-live` or dirty with foreign hunks. Name the target tree. Reuse `anchor_edit`'s all-or-nothing edit (P24).

**P15. FOLLOW-UP — no idempotency. L M, I M.**
- Verbs act before the harness decides whether to deliver the result:
  - the cap drops the RES (P2);
  - a timed-out hook does not block;
  - the container can die between the write and the delivery.
- A re-issue under a new nonce then writes the entry twice and allocates a second AF-AP id.
- **Change.** Add a request key (a content hash) with a dedupe window. The RES for a duplicate says "done at <stamp>".

**P16. INFO — the stamp rule.**
- `book` takes the leading stamp from the clock, but a stamp typed inside `<text>` still gets through.
- `stamp_check.py --staged` catches future stamps at commit time (pre-commit:136-141; its target list at :42-45 names all four `book` files).
- So "ends by construction" (:96) overclaims.

### C. The labels

**P17. BLOCKER — the records keep a digest of the state, and the SYNTH1 result predicts the labels will not train (:125, :128; D-101 (3) "all the systems can get the training data they need"). L H, I H.**
- **The missing field (certain).** Records hold "state digest, answer, rating, outcome", and the action log keeps "a digest of the input". Nothing can be trained on a digest.
- **The learnability risk (a prediction).**
  - On the one measured case, two labelers from different model families were given the recorded input. They did not reproduce the coordinator's scores. Qwen reached rel exact 0.3846 and OpenJev 0.2692 on 52 sections, against a bar of 0.75 (`todo/BUILD-TASKLIST.md:1651`).
  - The ledger reads this as "points at the input". The same fact says a Jev instance that sees only that input will miss too, however many labels are collected "where the context is".
- **Change.**
  - For each family, the registry defines the state the Jev instance will see at inference time, built by the code the future hook will call.
  - The collector stores that state verbatim (scrubbed), cut strictly before the decision.
  - It strips LBL, REQ and RATE lines and the coordinator's own prose about the choice, so the answer does not leak into the state.
  - Before collecting at scale, run a learnability probe per family: a strong labeler given exactly that state must reach a pre-registered agreement on about 50 items.

**P18. FOLLOW-UP — few labels, and skewed ones. L H, I H.**
- **S1-RATE's record.** S1-RATE prompts once per injection, yet it stood at 28 scored, 39 missing and 1 open (SYNTH1-report:139; the audit cites :136). VERIFY-S1-RATE F1 shows the scored ones are selected by reply length.
- **LBL has no prompt at all.** The coordinator must notice each D4 decision and recall an id from a 46-family registry, so only noticed, deliberate decisions get labels.
- **No reliability check.** Nothing measures the coordinator's own label reliability. SYNTH1's miss has a second reading: the gold labels may be noisy.
- **Change.**
  - Derive labels from the action wherever the action carries the answer (Agent dispatch fields → `f23.route`; a repair dispatch → `f26`).
  - Count compliance daily, with an alarm.
  - Have the coordinator blind re-rate about 5% of labels, with a floor, before any label trains a model.

**P19. FOLLOW-UP — the D4-only rule (:53) contradicts the design's own examples (:50-51). L H, I M.**
- The design lists `f36.read_next`, `f37.changes_gate`, `f38.wake_now`, `f39.dup_of` and `f40.claim_holds` as LBL examples.
- AUDIT §1.4 gives other sources for these: F36 comes from "the next reads" (behaviour); F37 is "as F25" (verifier words); F38 would need one label per Monitor event.
- **Change.** The registry states each family's label source, and the collector refuses LBL lines for D1 and D2 families.

**P20. FOLLOW-UP — rating ids collide; RATE-first breaks S1-RATE; rating bookkeeping is noise. L H, I M.**
- **Id collisions.** `RATE r1` restarts every turn. S1-RATE uses random ids (`hook_context.py:51, :62-63`). A late rating would pair with the wrong result.
- **RATE-first breaks S1-RATE (probe with the production module).** `s1_scores.attempts()` on the text `RATE r1 rel=2 use=3` followed by `S1-RATE s1-0123abcd rel=2 use=2` classifies the S1-RATE line `below-text` (malformed). With S1-RATE first, it is well formed.
- **Meaningless ratings.** A relevance/use rating of `book: ok, 29 passed` means nothing.
- **Change.** Make RES ids `<nonce>.rN`. Put S1-RATE lines before RATE lines. Rate only `ask`, `find` and `read`.

**P21. FOLLOW-UP — coverage of the owner's "about 20" is not shown, and lanes are unlabeled. L H, I M.**
- The referent of "about 20" is UNVERIFIED (AUDIT §1.1: RF2 says "~20" and enumerates 33).
- The design gives 10 example questions and no table per instance.
- Families with no D1, D2 or D4 source stay at zero labels: F30 ("29,211 PC tool results carry no outcome"), F32, F34, F35, F38, F46.
- PC Hermes lanes, the default BUILD and VERIFY venue, run no Claude Code hooks. Sandbox subagents never receive a nonce (P25).
- **Change.** Build a coverage table: each instance → family → label source → expected labels per day, with NONE flagged. Confirm it with the owner.

**P22. FOLLOW-UP — records omit the model, and the data has no durable home. L M, I H.**
- There is no served-model field, although AF-AP-154 documents silent model switches in the middle of a run.
- `.jev/` is gitignored (`.gitignore:68`) and is lost on a container reset (AUDIT §7). The design names no durable store for the action log or the records.
- **Change.** Record the served model and the harness version. Export the scrubbed records on a schedule (committed, or synced to the PC).

### D. The offload

**P23. BLOCKER — `book` cannot carry a real entry (:45 cap; D-101 (6)). L H, I H.**
- Entry lengths measured at 370fead:

| Target | Entries | Median length (chars) | Over 200 chars |
|---|---|---|---|
| Incident-log dated entries | 198 | 1,270 | 100% |
| Registry rows | 235 | 1,114 | 100% |
| Ledger stamped lines | 523 | 1,433 | 87% |
| Decision-log D-rows | 101 | 1,218 | 81% |

- A longer REQ line does not parse (P3c), so it is dropped without a word.
- **Change.** Allow block bodies or file-backed values (`anchor_edit`'s `@path`), or structured fields that the verb composes.

**P24. FOLLOW-UP — `book` duplicates `anchor_edit.py`. L H, I M.**
- `scripts/anchor_edit.py:1-20` already does all-or-nothing anchored edits, fills `{STAMP}` from the clock, takes long values via `@path`, and never commits. It ran 348 times in eight days; the design mentions it only as that count.
- Two owners of the same write path will drift.
- **Change.** Build `book` on `anchor_edit`'s plan-and-validate step, and add only next-id allocation and placement.

**P25. BLOCKER — LS-B6 cannot land as designed, and literal mirrors would stop the lanes (repo invariant: the mirror gate). L H, I H.**
- **Byte budget.**
  - AGENTS.md is 32,641 bytes against the gate's 32,768 (`test_context_mirrors.sh:29, :104`), so it has 127 bytes of headroom.
  - `.hermes.md` has 3,416 characters of headroom.
  - Section parity (:9-11) forces any new `## ` section in CLAUDE.md into both mirrors.
- **Lanes would follow the rule with no executor.**
  - Every sandbox subagent loads CLAUDE.md (this lane did).
  - UserPromptSubmit reaches the main thread only: `.jev/injections.jsonl` shows UserPromptSubmit main 18, subagent 0.
  - SubagentStop has no executor, and Hermes lanes have no executor at all.
  - A lane told "end with REQ lines and wait" would end its run with a request list as its report.
- **Change.** Put the LS text where only the coordinator reads it: a skill the main loop loads, or a CLAUDE.md line scoped to "main session, only when a nonce was injected". The mirrors get one line saying lanes do not use REQ. Keep a byte budget.

**P26. FOLLOW-UP — the owner said to keep the styles, and LS-B6 edits them (:151). L H, I L-M.**
- D-101 (3): "keep the current output styles ('I like it')".
- The style files are byte copies of `sandbox-kit/output-styles/` (`VENDORED-CLAUDE-CLASSES.tsv:49-52`; `tests/test_vendored_manifest.py:465` expects four such copies), licensed AGPL-3.0.
- The only `outputStyle` setting sits in a file this session does not load (AUDIT §3.2).
- **Change.** Leave the style files untouched. Put the grammar in CLAUDE.md or a skill.

**P27. BLOCKER — no saving by construction, and the measures would show one anyway (:156; X-010). L H, I M.**
- **Same cost per round.** A request round is one new model request carrying the whole context: the `stop_hook_blocking` continuation re-enters the same query loop. That is the same cost as one tool-call round.
- **Tool calls remain.**
  - `book` never commits, so `safe_commit` stays (567 calls in eight days).
  - A RES over 9,500 characters becomes a file the coordinator must Read. Probe: a `read` window (max(lines/5, 150)) exceeds 9,500 characters for 203 of 309 narrowable files, including 128 of 137 Markdown files.
- **The measures would mislead.**
  - "Tool calls per task" falls even with zero saving, because REQs are not tool calls.
  - "Cache-read tokens per turn" is measured per request, and LS does not shrink requests.
  - X-010's criterion is per task, "with no gate bypass". The design has no pilot, baseline, threshold or kill criterion (each term: 0 occurrences).
- **Change.**
  - Pre-register, per task (a task = the span of one ledger id): model requests, total cache-read plus output tokens, and wall time.
  - Use 09-20..09-28 as the baseline, and set a threshold and a kill criterion.
  - Count the follow-up Reads caused by RES-to-file overflow.

**P28. FOLLOW-UP — placement and ids. L M, I M.**
- **Placement.** The ledger's §2 header says "append-only sync blocks; newest first" (`BUILD-TASKLIST.md:420`), but the newest blocks sit at the end: lines 1641-1652 are dated 09-26 to 09-28, while lines 422 and 433 are dated 09-17. So "after the ledger's newest block" has two readings.
- **Ids.** The next AF-AP and D ids are computed per tree and are unknown until the RES arrives. An incident entry and its ledger line written in one REQ message therefore cannot cite the new id.
- **Change.** Use explicit anchors that the verb's tests pin. Return the id in the RES. Add a `{NEXT_AP}` token filled across one write set.

**P29. UNVERIFIED — the test map may not fit the budget.**
- Tests that name `docs/INCIDENT-LOG.md`: 13 files and about 730 test functions. `test_s0_01_check_acp_conformance.py` alone has 365 tests, 6,641 lines and 23 subprocess sites.
- Tests that name the ledger: 7 files.
- Not timed; no test was run in this lane.
- **Change.** Use a curated fast map per target, or report the tests on the next Stop.

**P30. FOLLOW-UP — the task-list view has no data source and conflicts with two owner rulings (:103-106). L H, I M.**
- **No source.** The design says "the D-rows' open tasks", but D-rows are decisions. The §1 Tasks table (`BUILD-TASKLIST.md:372-418`) has free-text status and stops around task #63. Tasks #339-#341 exist only in prose blocks.
- **Ruling conflict.** CLAUDE.md's TASK-SURFACE SYNC (owner, 2026-08-31: "keep them where they are now, but update them more often") and D-101 (6) ("update the task list, update the DB") both ask for updating, not replacing.
- **Owner-visible loss.** The owner's UI task list would go stale.
- **Repeat cost.** UserPromptSubmit fires on harness events (P10), so an unfiltered view would repeat on every notification.
- **Change.** When asking the owner, cite both rulings and name the loss. Build a machine-readable active-task file as the source. Skip harness events.

### E. The Read hook

**P31. UNVERIFIED mechanism, high impact — a narrowed Read followed by a Write can destroy content. L L-M per event, I H.**
- The hook turns a whole-file Read into a window.
- If the harness's Write precondition (a prior Read) accepts a partial Read (not tested on 2.1.283), a model that thinks it read the whole file rewrites it and loses every line outside the window.
- `edit-snapshot.py` runs only after the write.
- **Change.** Add a PreToolUse Write guard: refuse a Write to a file whose last Read in this session was narrowed. The F42 log already holds that fact.

**P32. FOLLOW-UP — lanes, verifiers and patch diffs would be narrowed. L H, I H.**
- Session hooks fire inside subagents: `.jev/injections.jsonl` shows PreToolUse subagent 117 and PostToolUse subagent 126.
- Census of files with at least 400 lines and at most 80 KB: 309 files. That is 137 `.md` (reports and briefs), 82 `.py`, 42 lane-patch `.diff` and 30 `.json`.
- The coordinator grades lane patches, and a narrowed diff hides hunks.
- The design counts its 301 large Reads "across 322 transcripts", which includes subagents; the subagent share is UNVERIFIED.
- **Change.** Narrow in the main thread only (no `agent_id`). Never narrow `.diff`, `.patch` or report files. Make it opt-in first.

**P33. FOLLOW-UP — the goal source does not exist at PreToolUse, and the port scans the whole transcript per Read. L H, I M.**
- **No goal available.**
  - PreToolUse receives `tool_name`, `tool_input` and `tool_use_id` (hooks.md:1585), with no assistant text.
  - The transcript "may lag" (hooks.md:738).
  - An LBL line written before a tool call can end up as a thinking block (F1).
- **Scan cost.** jev's `lastUserMessage` (`hook.go:186`) unmarshals every transcript line on each call. The main transcript was 705,586,594 bytes on 09-25 (MAP:44-48). A line over 8 MB ends the scan early, leaving an older goal.
- **Wrong goal for lanes.** Only SubagentStop carries `agent_transcript_path`, so a lane's Read likely gets the coordinator's goal (UNVERIFIED).
- **Wrong goal type.** An LBL line such as `f23.route opus` is not a goal for reading a file.
- **Change.** Narrow only when the `read` verb supplies an explicit goal. Otherwise pass the Read through.

**P34. FOLLOW-UP — the recall plan cannot measure the designed hook, and F42 labels misses as hits. L H, I M.**
- Historical Reads predate LBL and REQ, so the goal ladder cannot be replayed on them.
- "The lines the session went on to use" is observable for code edits, not for reading documents.
- F42's outcome ("read outside the window within 5 calls") records a hit for every miss nobody noticed.
- jev's own bench says "23 narrowed windows with no loss is 'no failure observed', not a rate" (RESULTS_HOOK.md:132), and its confidence scores overlap for hits and misses. X-011's bar is "no lost answers".
- **Change.** Run a shadow mode first: compute the window, do not narrow, log it. Check it with an independent scripted oracle, then decide on default-on.

**P35. FOLLOW-UP — the backend and venue are unnamed. L H, I M.**
- **TypeSafe.** jev posts the whole file (up to 80 KB) to api.typesafe.ai in one request. X-011 allows "TypeSafe only after D-078's scrub", and D-078 approves external egress (codiv) only for generating training data.
- **Laya.** Laya scores one chunk at a time in a `max_len` window that defaults to 512 (`laya_systemone_server.py:157-160`; 1,024 in its config). That is a different algorithm, with no recall data.
- **PC venue.** The PC's laya-systemone shares the GPU host with vLLM. D-099 records 63 MiB of slack and an out-of-memory crash of the vLLM engine.
- **Change.** Name the backend, venue, scrub and latency budget before the recall work starts.

### F. Omissions against D-101 and X-010

**P36. BLOCKER — X-010's registered acceptance items are missing. L H, I M.**
- X-010 (DL:129) requires "an off switch" and "a one-week pilot shows fewer turns or fewer cache-read tokens per task with no gate bypass".
- The design has neither: "off switch" and "-off" occur 0 times, while the repo's pattern is `.jev/<name>-off`; there is no pilot (P27).
- **Change.** Add a tested, fail-safe off switch per part (ls-exec, the action log, the Read hook). Add the pilot described in P27.

**P37. FOLLOW-UP — D-101 (4) asked to "build the retrimming hooks build all the hooks everything".** The design has one hook (Read). It does not address the output pruner (B7 runs at a 10k floor; the P1 variant failed at the 2k floor), and it draws up no list of "all the hooks".

**P38. FOLLOW-UP — D-101 (6): "if it's something a Jev model can do, it should do it itself".** `book` is a script with no Jev part, and "update the DB" is not mapped to anything.

**P39. INFO — D-100 (1) asked for scripts that "run in the background … work in parallel".** `ls-exec` runs synchronously while the coordinator waits, and parallel runs across verbs are unspecified.

**P40. FOLLOW-UP — a proven free label source is not reused.** hermes-jev-skills flips a shown suggestion to 1 when the skill is loaded within the window (AUDIT §5.2: 34% of 1,188 on a fleet; 51% on replay). That gives a behavioural outcome label for S1 injections (F13, F14) with no rating needed.

**P41. FOLLOW-UP — the owner's view.** Every message would open with S1-RATE and RATE lines and close with REQ lines. That goes against Attention-kind's "answer first" and the owner's "keep the current output styles". No rule separates the owner-facing answer from the machine lines.

### G. Other notes

- **P42 INFO.** The claim "the harness caps hook text at 10,000" is documented for `additionalContext`, `systemMessage`, `initialUserMessage` and plain stdout (hooks.md:923-928), not for exit-2 stderr. The 9,500-character cap is safe either way.
- **P43 INFO.** The audit's timeout contradiction (§6.3) resolves toward the docs for local command hooks (see P8). The 600 s figure comes from the docs; it was not exercised.
- **P44 INFO.** The action log cannot find "the nearest preceding LBL or REQ id" at write time, because PostToolUse carries no assistant text. Do that join in the collector, keyed by (session, agent_id).
- **P45 INFO.** An LBL line with an unknown family should go to a quarantine file, not be dropped.
- **P46 INFO.** LS-B5 needs LS-B2 only for the `read` verb. The owner-approved Read hook need not wait for the executor.
- **P47 INFO.** `book wiki` skips the only System-1 situation row keyed on `live-state.md` (`system1-situations.json`, id `live-state`).
- **P48 UNVERIFIED, for the owner's awareness only.** Whether Claude-written labels may train the owner's Jev models is not recorded in D-078 or D-101. The practice already exists: D-083 and D-085 use recorded answers.

## Ranking (likelihood × impact)

1. P3: silent drops lead to stalls.
2. P1 and P2: continuation semantics, and the silent refusal.
3. P23: the 200-character cap on `book`.
4. P17: no trainable state, and the learnability risk.
5. P25: the mirrors and the lanes.
6. P13: the missing registration path.
7. P18: label volume and bias.
8. P27 and P36: no saving, misleading measures, and the missing X-010 items.
9. P12: the permission bypass, secret paths and raw RES content.
10. P31 and P32: Read-hook data loss, and narrowing inside lanes.
11. P33–P35: the Read hook's goal, measurement and backend.
12. P4, P6, P9, P10, P14, P15: side effects of the request loop.
13. P19–P22: label hygiene.
14. P24, P28–P30: offload details.
15. P5, P7, P8, P26, P37–P41.
16. The INFO items.

## GATE RECOMMENDATION: REDESIGN the request transport; the other parts PROCEED-WITH-CHANGES

**Why REDESIGN rather than a change list.** Three failure classes belong to the Stop-hook channel itself, not to this spec:
- **It cannot fail loud when it never runs or never sees the lines.** The hook does not run on an interrupt, an API error, or when it is not installed. It does not see REQ lines outside the last content block, or in a thinking-only final message.
- **The binary fixes the harness's continuation semantics.** The design must work within them.
- **A request round is a model request.** The promised saving has to come from what each verb does, and a tool call delivers that equally well.

The redesign should put two transports side by side for the owner, because his literal words ("write it in the chat … end, wait") pick one, while his stated reasons (fewer calls, fewer tokens, labels for every Jev use) do not.
- **A. The Stop hook, fully specified.**
  - a turn-scoped set of valid nonces;
  - the current nonce treated as intent;
  - loud refusals;
  - a counter reset from the action log;
  - RES through `additionalContext`, measured first;
  - a stall watchdog on the next prompt;
  - REQ lines last in the message;
  - block bodies for long values;
  - rules that apply to the main thread only.
- **B. One closed-verb command line called as a tool,** for example `python3 scripts/ls.py <verb> …`, with the same verbs and schemas.
  - The request and result stay visible in the transcript.
  - The call waits by construction.
  - It passes through the permission system.
  - It works in subagents and PC lanes.
  - It has no continuation cap and no silent drop.
  - Ratings can ride as arguments on the next call (`--rate <id>=<rel>/<use>`). They are then stored in the tool input and never lost to a thinking block, which would also close S1-RATE's F1 gap.

**Changes that apply to either transport** (the PROCEED-WITH-CHANGES list for the other parts):
1. The registry defines each family's inference-time state and label source. Records store the scrubbed state (not a digest), the served model and the harness version. Run a learnability probe per family before scale (P17, P19, P22).
2. Derive D4 labels from actions where the action carries the answer. Count compliance daily. Blind re-rate a sample, with a floor (P18).
3. Use globally unique result ids. Put S1-RATE before RATE. Rate content verbs only (P20).
4. Build a coverage table for the owner's "about 20", stating what PC lanes and subagents produce (P21).
5. Register through `install_session_hooks.our_hooks()`, with tests and a smoke check. Adopt "no nonce ⇒ no REQ" (P13).
6. Keep LS text coordinator-only. Put a one-line lane rule in the mirrors, inside the byte budget. Leave the style files untouched (P25, P26).
7. Add off switches per part, and a pre-registered pilot with per-task metrics, a baseline, a threshold and a kill criterion (P27, P36).
8. Build `book` on `anchor_edit.py`: long values by file or block, explicit anchors, refusal of `.lanes-live` paths, a named target tree, an idempotency key, and the new id returned in the RES (P14, P15, P23, P24, P28).
9. Read hook:
   - shadow mode first;
   - main thread only;
   - never narrow `.diff`, `.patch` or report files;
   - a Write guard after a narrowed Read;
   - an explicit goal, or no narrowing;
   - a named backend with its scrub and latency budget;
   - an independent oracle (P31–P35).
10. A secret deny list, an allowlist of git-tracked files, and scrubbed, neutralized RES content (P12).
11. Make the retro gate and the git check aware of request chains (P4, P6).
12. When asking the owner about the task-list view, cite TASK-SURFACE SYNC and D-101 (6), and name the loss of the UI list (P30).
13. Export the action log and the records durably (P22).

**Caveat.** This recommendation depends on binary behaviour read statically (P1, P2, P3a-b, P7) and on one probe through a surrogate parser (P3c). None of it was exercised live.

## Paths
- Design: `/home/user/i59-landing/docs/research/findings/labeling/LS-DESIGN-2026-09-28.md`
- Evidence:
  - `/home/user/i59-landing/tasks/briefs/labeling/LS-AUDIT-report.md`
  - `/home/user/i59-landing/docs/08_DECISION_LOG.md` (D-077, D-078, D-100, D-101, X-010, X-011)
  - `/home/user/i59-landing/todo/BUILD-TASKLIST.md`
  - `/home/user/i59-landing/tasks/briefs/system1/SYNTH1-report.md`
  - `/home/user/i59-landing/tasks/briefs/system1/VERIFY-S1-RATE-report.md`
- Harness:
  - `/opt/claude-code/bin/claude` (2.1.283)
  - docs copy `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ls-audit/hooks.md`
- Live code read:
  - `/home/user/i59-landing/.claude/hooks/turn-retro-gate.sh`
  - `/root/.claude/stop-hook-git-check.sh`
  - `/home/user/i59-landing/scripts/install_session_hooks.py`
  - `/home/user/i59-landing/scripts/s1_scores.py`
  - `/home/user/i59-landing/scripts/hook_context.py`
  - `/home/user/i59-landing/scripts/anchor_edit.py`
  - `/home/user/i59-landing/scripts/push_clean.sh`
  - `/home/user/i59-landing/harness-ports/tests/test_context_mirrors.sh`
  - `/home/user/i59-landing/.claude/hooks/wiki-context.py`
  - `/home/user/i59-landing/scripts/laya_systemone_server.py`
  - `/home/user/borislemeec/jev/internal/run/hook.go`
- Live state read (counts only):
  - `/home/user/agent-factory/.jev/injections.jsonl`
  - `/home/user/agent-factory/.jev/system1.jsonl`
  - `/home/user/agent-factory/.lanes-live`
  - `/home/user/.claude/settings.json`
- Probe script: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ls-premortem/probe_parse.py`